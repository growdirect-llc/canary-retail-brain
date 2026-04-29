---
card-type: platform-thesis
card-id: platform-performance-nfrs
card-version: 1
domain: platform
layer: cross-cutting
status: approved
tags: [NFR, SLA, performance, scalability, throughput, latency, batch, restart-recovery, event-log, valkey, pgvector, MCP, hash-chain]
last-compiled: 2026-04-29
---

## What this is

The platform's non-functional requirements and service level terms — translated from Retek-era benchmark principles into the modern stack's terms. The Retek benchmarks (Carrefour: 16M transactions / 148 minutes; Best Buy: 80K sales / 20 minutes; USPS: 30M line items / 444 minutes; user response: <3 seconds at 1,492 concurrent users; mix processing: <0.7 seconds average) were achieved on 2001-era hardware with on-premise Oracle and batch file pipelines. The modern stack eliminates the constraints that drove those numbers while inheriting the design principles that made them achievable.

## The governing translation

Retek solved the throughput problem by committing in bulk (LUW: every 10,000 SKU/store combinations), using array processing to reduce round trips, and partitioning batch workloads across threads by department or store segment. These are solutions to the limitations of serial RDBMS batch processing against mutable tables.

The append-only event log eliminates most of these constraints: a new event is a write, not a read-modify-write cycle; there is no lock contention on historical records; each merchant namespace is an independent partition. The principles that remain are: commit granularity, parallel processing by partition, and LUW-level restart from a known-good position. In the modern stack, those translate to event batching, namespace-level parallelism, and idempotent event replay.

## Event log throughput

**Principle inherited from Retek:** sustained batch throughput of 100K–1M events per hour per processing unit, with degradation-free concurrent OLTP at transaction volumes well below the batch ceiling.

**Our target:** PostgreSQL append-only event log, partitioned by `merchant_id`, sustained write throughput of 500K events per hour per merchant namespace under nominal load. This is conservative relative to what modern PostgreSQL on GCP achieves — the constraint is network ingress and hash computation, not the database write path.

**Invariant:** no event acknowledged to the MCP caller until it is durably written to the event log and its sequence position is assigned. Acknowledged = durable. No eventual consistency on writes.

**Hash computation:** SHA-256 of the canonical JSON payload including prior event hash. On current hardware: <1ms per event. Not a throughput bottleneck.

## MCP response SLA

The MCP surface is the primary interface contract. Every tool call has a latency target. These are P99 targets under nominal load (single merchant, no batch interference).

| Tool class | P99 target | Notes |
|---|---|---|
| Namespace read (Valkey hot) | <10ms | Cache hit; key already resolved |
| Event log query (recent, indexed) | <100ms | Last N events for a namespace |
| Event log query (range, unindexed) | <500ms | Arbitrary date range without pre-agg |
| Event write + hash + chain entry | <2s | Includes SHA-256, sequence assignment, Valkey cache update |
| Template match (pgvector semantic) | <200ms | Field capture event type matching |
| verify_chain() call | <1s | Sequence verification for external party; range-bounded |
| Smart contract evaluation (three-way match) | <500ms | PO + ASN + Invoice hash comparison |

**Field capture invariant:** chain entry must be written and receipt hash returned to the operative's phone within 5 seconds of operative confirmation tap. This is the hard latency bound for field capture — it governs network tolerance and mobile UX requirements.

## Cache and pre-aggregation

**Principle inherited from Retek:** mix processing achieved <0.7 second average response during concurrent batch by using pre-computed summaries. Retek could not serve OLTP queries from the raw transaction log at acceptable latency — it required nightly aggregation into summary tables.

**Our approach:** Valkey serves the hot path. The event log is append-only truth; Valkey holds the derived, queryable state for active namespaces. Every chain entry that affects a queryable metric (inventory position, OTB balance, shrink rate by store) triggers a Valkey cache update as part of the write pipeline. No dashboard query touches the raw event log under normal operation.

**Pre-aggregation targets:**
- Store-level inventory position: maintained in Valkey, updated on every inventory event, read latency <10ms
- OTB balance: updated on every L402-gated commit call, consistent with the settled payment
- Shrink rate by store (rolling 30-day): pre-computed, refreshed on every Fox case write, read from Valkey
- Receiving discrepancy rate by vendor: refreshed on every ASN variance event

**Valkey eviction policy:** LRU, keyed by `{merchant_id}:{domain}:{entity_id}:{metric}`. Inactive merchant namespaces are evicted; their state is reconstructible from the event log on demand (point-in-time reconstruction is the rebuild path, not a backup restore).

## Batch throughput and namespace partitioning

**Principle inherited from Retek:** partition batch workloads by segment (department, store) to achieve parallel throughput. Retek's threading model used stored procedures to divide driving cursors into discrete segments.

**Our model:** each merchant is an independent namespace. There is no cross-namespace state. Batch processing — end-of-day aggregation, inventory reconciliation, vendor chargeback calculation — runs per merchant in parallel. The partition key is always `merchant_id`. Retek's threading model becomes horizontal scale across namespaces.

**Within a merchant namespace:** large-batch event ingestion (e.g., full inventory position import at onboarding) uses buffered writes of 1,000 events per transaction commit, equivalent to Retek's LUW commit counter. This balances write throughput against recovery granularity.

## Restart and recovery

**Retek model:** LUW-based restart. Commit every 10,000 records. Bookmark stored before commit. On failure, resume from last bookmark position.

**Our model:** restart without bookmarks. The append-only event log is the bookmark. Every committed event has a sequence number. A failed batch process re-runs its driving query with a WHERE clause on sequence numbers not yet processed — equivalent to Retek's bookmark-based query restriction, without requiring a separate restart table. Idempotency is enforced at the event level: duplicate event submission is detected by payload hash before chain entry.

**Recovery guarantee:** any interrupted batch operation is recoverable from the event log alone. No separate restart state table required. The sequence number is the bookmark.

**Gap detection:** the Operations Agent monitors sequence continuity per merchant namespace. A gap in sequence numbers is an alert — not a normal condition. Retek's restart model tolerated gaps as artifacts of threading; this model treats them as evidence of data integrity failure.

## User-facing response time

**Retek benchmark:** <3 seconds at 1,492 concurrent users across the full application.

**Our SLA (retailer-facing UI and agent surfaces):**

| Surface | P95 target |
|---|---|
| Store-level dashboard load (metrics from Valkey) | <2s |
| Inventory position lookup (single item, single store) | <500ms |
| Fox case list (open cases, filtered by store) | <1s |
| LP case detail (event timeline, hash-verified) | <2s |
| Field capture receipt confirmation (chain entry → phone) | <5s |
| verify_chain() external call | <1s |

## Durability and availability

**Inventory fill rate reference (Katz 2003, drug chain):** Rx category ~99.5%, total product line ~97–99%. These are inventory availability terms, not system uptime terms. The principle is that the platform's service availability needs to exceed the inventory fill rate it is measuring — a platform that goes down during receiving or POS peak is less reliable than the manual process it replaces.

**Event durability:** 99.9% — no event lost once acknowledged. PostgreSQL on GCP with synchronous replication. This is the floor, not the aspiration.

**Platform availability target:** 99.5% monthly uptime, excluding planned maintenance windows communicated 48 hours in advance. The POS integration path (transaction event write) is the most availability-sensitive surface — a 4.4 hour/month outage window is the contractual maximum.

**POS write path failover:** if the platform event endpoint is unreachable, the local POS adapter queues events locally (SQLite, capped at 24 hours of nominal transaction volume) and replays on reconnect. The chain entry timestamp reflects the moment of original capture, not the moment of replay. This is the field capture invariant extended to POS: the timestamp is when it happened, not when the network recovered.

## Sizing inputs (modern equivalents)

Retek sizing required upfront estimates of: annual transaction count, concurrent user count, batch window length, hardware CPU and RAM configuration. These determined whether the on-premise deployment could sustain the projected load.

**Our sizing model:** no upfront hardware sizing. The platform scales horizontally on GCP. The relevant inputs for SLA negotiation are:

- **Peak daily transaction volume** — drives Valkey cache sizing and event log partition planning
- **Concurrent MCP client count** — drives connection pool sizing; target <100 concurrent clients per merchant namespace without additional provisioning
- **Batch window requirement** — if the merchant requires end-of-day processing to complete before store open, that sets the throughput floor for their namespace; relevant only for large merchants
- **Data retention period** — the event log is append-only and never purged without explicit export + archive; retention drives storage cost, not performance
- **Number of merchant namespaces** — the platform is multi-tenant; each namespace is independent; adding merchants does not degrade existing merchant SLAs

## Related

- [[raas-receipt-as-a-service]] — the primary event log service these NFRs govern
- [[platform-enterprise-document-services]] — the full EDS surface; all services share these latency targets
- [[platform-field-capture]] — field capture chain entry latency is the hard 5-second invariant
- [[platform-thesis]] — the accountability model these NFRs must sustain
- [[infra-blockchain-evidence-anchor]] — the L1/L2 anchoring layer; anchoring latency is asynchronous and not included in the MCP response SLA

---
classification: confidential
owner: GrowDirect LLC
type: module-article
prefix: T
status: v1 (shipping)
sibling-modules: [R, N, A, Q]
---

# T — Transaction Pipeline

The transaction pipeline is the inbound edge of Canary Retail. Every
operational signal in the platform — every detection, every case, every
metric, every ARTS-shaped projection — eventually traces back to a row
that landed through T. T is therefore the module the rest of the spine
sits on top of: if T is wrong, every downstream answer is wrong.

T is one of the [[spine-13-prefix#v1-differentiated-five-t-r-n-a-q|
Differentiated-Five]] modules that ship at v1. It is also the most
classical of the five — POS-agnostic transaction ingestion is what
every loss-prevention vendor sells. Canary's edge in T is not the
existence of the pipeline; it is what's done with the bytes between
the wire and the database. Specifically: the bytes are hashed before
they are parsed, and that hash anchors a chain that survives every
downstream operation.

## Purpose

T owns three jobs:

1. **Receive** retail-operational events from external sources
   (today: Square webhooks; tomorrow: any POS, any e-commerce platform,
   any inventory adjustment feed). Translate vendor payloads into the
   canonical model with no loss of fidelity.
2. **Seal** every received event into an append-only, hash-chained
   evidence record before any business logic runs. The hash is taken
   over the raw bytes as they arrived, not over a parsed shape — so
   later parser changes can't invalidate prior evidence.
3. **Stream** sealed events to downstream subscribers (Q for detection,
   R for customer enrichment, N for device telemetry, A for asset
   anomaly scoring, future modules for everything else). T does not
   decide what an event means; it just guarantees the event was real
   and gets it to the modules that decide.

T does **not** own merchant configuration, tenant onboarding, or
detection rule definitions. Those live in adjacent surfaces (`app`
schema, onboarding service, Q/Chirp rule catalog). T owns the
pipeline; everything else owns the policy.

## BST cells T populates

T is the upstream feeder for many BSTs but the primary owner of only
a few. Mapping below uses the [[../platform/overview|RBIS-derived
spine]]; primary ownership in **bold**, contributing-feed in plain.

| Domain | BST | T's role |
|---|---|---|
| Store Operations | **Loss Prevention Analysis** | Primary feeder — every Q rule fires off T's stream |
| Store Operations | **Transaction Profitability Analysis** | Primary feeder — `transactions.amount_cents` × `tenders` × `processing_fee_cents` is the source data |
| Store Operations | Suspicious Activity Analysis | Feeder — out-of-band events (NO_SALE, PAID_OUT, POST_VOID) surface here |
| Store Operations | Cashier-side Performance Measurement | Feeder via `employee_id` on every row |
| Customer Management | Purchase Profiles | Feeder — line-item × customer joins |
| Customer Management | Market Basket Analysis | Feeder — line-item composition per `order_id` |
| Customer Management | Product Purchasing RFQ | Feeder — recency/frequency derived from `transaction_date` |
| Products & Services | Product Analysis | Feeder — sales-by-product joins through `transaction_line_items.catalog_object_id` |
| Multi-Channel | eCommerce Analysis | Feeder — for merchants whose Square traffic is online |
| Corporate Finance | Financial Mgmt Accounting | Feeder — gross sales, refunds, tender mix |
| Corporate Finance | Income Analysis | Feeder — daily/weekly reconciliation |

T populates these by writing rows. It does not compute the BSTs
themselves — those are projections owned by Q (LP), and by future
metrics services for everything else.

## CRDM entities touched

Per [[../platform/crdm|CRDM]], every module reads/writes the
five-entity frame.

| CRDM entity | T's relationship | How |
|---|---|---|
| **Events** | **Owns** the transaction subset | Every row in `transactions` is a CRDM Event |
| **Things** | Reads | Foreign-keys `device_id`, `catalog_object_id` to the Thing registry; doesn't curate |
| **People** | Reads | Foreign-keys `customer_id` (R-owned), `employee_id` (L-owned in v3); doesn't curate |
| **Places** | Reads | Foreign-keys `location_id` to the Place registry; doesn't curate |
| **Workflows** | Emits triggers | Q creates Cases (Workflows) downstream; T just hands the Event over |

The cleanest way to read T's CRDM posture: **T is an Event factory
with foreign keys into everyone else's registries.** It depends on
R/N/A having already curated the People/Things/Places it points at.
That dependency is enforced at read time, not write time — T will
write a row pointing at an unknown `customer_id` and let R catch up
asynchronously.

## ARTS mapping

T is the home of [[../platform/crdm#relationship-to-arts|POSLog]]
adoption. Square's webhook payloads are translated into POSLog-shaped
internal records:

| ARTS POSLog construct | Canary table / column |
|---|---|
| RetailTransaction | `transactions` |
| RetailTransaction.SequenceNumber | `transactions.external_id` (Square payment/refund ID) |
| RetailTransaction.LineItem | `transaction_line_items` |
| Tender | `transaction_tenders` |
| RetailTransaction.OperatorID | `transactions.employee_id` |
| RetailTransaction.WorkstationID | `transactions.device_id` |
| BeginDateTime | `transactions.transaction_date` |
| ControlTransaction (NO_SALE, PAID_IN/OUT) | `transactions.transaction_type` enum values |

POSLog field names are preserved at the API boundary where Canary
publishes back out to integrators, even where internal column names
diverge. This is the "ARTS-native, not ARTS-veneer" commitment from
[[../platform/overview#what-makes-it-different|Overview §What makes
it different]].

## Pipeline architecture

T is implemented as a four-stage Valkey-streamed pipeline:

```
webhook  →  seal  →  parse  →  merkle  →  detect
  (1)       (2)      (3)       (4)        (5)
```

| Stage | Responsibility | Where it runs |
|---|---|---|
| **1. Webhook** | HMAC-validate, hash raw bytes, idempotency-check, publish to `canary:events` | Flask webhook endpoint, in-process |
| **2. Seal** | Verify event hash, compute chain hash, write `evidence_records` under per-merchant advisory lock | `sub1-seal` consumer (Docker service) |
| **3. Parse** | Route by event_type to vendor-specific parser, write canonical rows to the `sales` schema, publish to `canary:detection` | `sub2-parse` consumer (Docker service) |
| **4. Merkle** | Batch sealed event hashes, build deterministic Merkle tree, anchor (mock today, Bitcoin ordinal in v2) | `sub3-merkle` consumer (Docker service) |
| **5. Detect** | Hand off to Q (Chirp rule engine) | `sub4-detection` consumer — *T's responsibility ends at handoff* |

Stage ordering is patent-critical: the raw-bytes hash is taken
**before** JSON parsing. Parsing is fallible; hashing is not. Every
later integrity claim depends on this ordering.

## Source-of-truth ingest paths

T currently accepts events from these sources, in priority order:

1. **Webhooks** — push, near-real-time, signed. The default and only
   v1 production path. Source: Square Webhooks API.
2. **Polling** — pull, periodic, used for backfill and reconciliation.
   Same parser surface; `source_type=POLLING` marker on resulting rows.
3. **Batch** — file or admin-initiated import; `source_type=BATCH`.
   Reserved for migration scenarios; no scheduled use today.

All three paths funnel into the same seal → parse → merkle → detect
pipeline. The vendor adapter chooses which path to use; downstream
modules cannot tell them apart except by inspecting `source_type`.

## Vendor adapters

Each adapter owns: webhook endpoint registration, signature
verification, payload-shape contract, and the parsers that translate
that vendor's shape into the canonical model.

| Vendor | Status | Adapter location |
|---|---|---|
| **Square** | v1 (shipping) | OAuth + webhook + 6 parser modules (payment, order, loyalty, payout, dispute, auxiliary) |
| Shopify | v2 roadmap | not yet implemented |
| Clover | v2 roadmap | not yet implemented |
| Generic POSLog import | v2 roadmap | adapter for direct POSLog feeds |

The promise to retailers is "POS-agnostic by architecture." That
promise is currently true at the canonical-model layer (every
downstream module reads canonical rows, not Square rows) but
unproven at the adapter layer until adapter #2 ships.

## Schema crosswalk

T writes to the `sales` schema. The relevant tables:

| Table | Owner | Purpose |
|---|---|---|
| `evidence_records` | T (write-once) | Hash-chained sealed event records |
| `ingestion_log` | T | Per-event lifecycle (received → parsed → completed/failed) |
| `transactions` | T | Append-only ledger of every Square payment/refund/void/no-sale/paid-in/out/exchange |
| `transaction_line_items` | T | Per-transaction line detail (FK to `transactions.id`) |
| `transaction_tenders` | T | Tender mix per transaction |
| `refund_links` | T | Junction table linking refunds back to original payments |
| `cash_drawer_shifts` | T | Cash drawer session boundaries |
| `cash_drawer_events` | T | Drawer open/close/skim events |
| `inscription_pool` | T (Merkle stage) | Batched event hashes awaiting anchor |
| `event_inscriptions` | T (Merkle stage) | Per-event inclusion proofs into Merkle batches |

T reads (but does not write) from:

| Table | Owner | Why T reads |
|---|---|---|
| `app.merchants` | platform | Tenant resolution from webhook signature |
| `app.square_oauth_tokens` | platform | Token retrieval for backfill/polling |
| `app.merchant_locations` | platform / Places registry | Validate `location_id` references |
| `app.merchant_devices` | N | Validate `device_id` references |
| `app.merchant_employees` | future L | Validate `employee_id` references |

## Service-name markers (v0.7 microservice index)

For the future microservice extraction, T's surface decomposes into
these service slots. Names are placeholders to seed the v0.7 index;
they are not committed deployment names.

| Service slot | Responsibility | Currently lives in |
|---|---|---|
| `tsp-ingress` | Webhook receipt, HMAC validation, raw-byte hashing, idempotency | `canary/blueprints/webhooks_tsp.py` |
| `tsp-seal` | Chain-hash compute, evidence record write | `canary/services/tsp/consumers/sub1_seal.py` |
| `tsp-parse-square` | Square-specific parsers (one per event family) | `canary/services/parsers/square_*.py` |
| `tsp-merkle` | Batch accumulation, Merkle tree construction, anchor handoff | `canary/services/tsp/consumers/sub3_merkle.py` |
| `tsp-route` | Event-type → parser routing | `canary/services/webhook_dispatch.py` |
| `tsp-oauth-square` | Square OAuth token lifecycle | `canary/services/square_oauth.py` |
| `tsp-onboard` | Merchant onboarding orchestration | `canary/services/onboarding/coordinator.py` |

**Perpetual-vs-period boundary.** Canary owns the entire stack — sealed transaction stream is ledger-grade and has no merchant-side equivalent. Implementation route: `legacy-native`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (event producers):

- Square Webhooks API (push)
- Square Payments / Orders / Refunds APIs (pull, for backfill)
- Future: Shopify, Clover, BigCommerce, generic POSLog feeds

**Downstream consumers** (event subscribers):

- **Q (Loss Prevention)** — Chirp rule engine, primary consumer; reads
  every parsed transaction off `canary:detection`
- **R (Customer)** — reads `customer_id` references for unified
  customer projection
- **N (Device)** — reads `device_id` for telemetry correlation
- **A (Asset Management)** — anomaly detection over device-bound
  transaction patterns
- **Future C/D/F/J** — line-item composition feeds Commercial,
  movement velocity feeds Distribution, payout reconciliation feeds
  Finance, demand signal feeds Forecast & Order

## Agent surface

T exposes one MCP tool family today, scoped to debugging and
operations rather than retailer-facing workflows:

- Pipeline-health introspection (queue depths, parse-failure rate,
  per-stage lag) — owned by the operations agent population
- Replay tooling — re-process a sealed event without re-sealing it
  (parse-only path) for parser bugfix recovery

Retailer-facing transaction-search agents are owned by Q (case
investigation context) and R (customer history), not T directly.

## Security posture

- **Auth.** Webhook signatures verified per-vendor. Square: HMAC-SHA256
  with timing-safe comparison; signature key rotated per merchant
  during onboarding.
- **Tenant scoping.** Every write carries `merchant_id`; every read
  is row-level-secured to the requesting tenant. T enforces this at
  the consumer-service boundary, not at the webhook boundary —
  webhook-time tenant resolution happens via signing-key lookup.
- **PII handling.** Customer phone numbers from Square loyalty
  webhooks are hashed before persistence (parser-side, not
  consumer-side, so PII never enters the seal layer in clear). Card
  PANs are never received; `card_fingerprint` is Square's tokenized
  fingerprint and is treated as opaque.
- **Evidence integrity.** Per-merchant `pg_advisory_xact_lock` during
  seal serializes chain-hash computation per tenant. The chain is
  `SHA-256(previous_chain_hash || event_hash)`; breaking it requires
  rewriting every subsequent row, which the lock prevents.
- **Idempotency.** Valkey DB 3 deduplicates by `(merchant_id,
  source_event_id)` with a 24h TTL. Resends within 24h are silently
  acknowledged.

## Open questions

These are the gaps the next pass over T should close.

1. **Adapter #2 selection.** Shopify vs Clover vs generic POSLog as
   the second adapter is undecided. The choice affects how thin the
   "POS-agnostic by architecture" claim actually is at v2.
2. **Polling SLA.** Polling is implemented but has no published SLA
   for backfill latency or completeness. Needed before the polling
   path is offered to retailers in production.
3. **Merkle anchor cadence.** Sprint-6 anchor is a mock; real
   Bitcoin ordinal inscription needs a confirmed cadence (per-batch?
   per-day? per-100k-events?) and a cost model.
4. **Cross-vendor event reconciliation.** A retailer who runs Square
   in-store and Shopify online will have two transaction streams for
   the same business. T does not yet have a model for unified
   transaction identity across vendors. Likely belongs in R/N
   conjointly, not T alone — but T owns the foreign-key shape that
   would carry it.
5. **Replay safety.** Replay tooling exists for parse-only re-runs.
   What happens when a parser change retroactively reclassifies a
   transaction (e.g., a `PAID_OUT` becomes a `POST_VOID`) is not
   formally specified; downstream Q rules may double-fire.

## Roadmap status

- **v1 (shipping)** — Square adapter end-to-end. Pipeline complete
  through detect handoff. Append-only ledger live. Mock Merkle anchor.
- **v2** — Adapter #2 (vendor TBD). Real Merkle anchor. Published
  polling SLA. Cross-vendor identity model.
- **v3+** — Generic POSLog ingest. Multi-region pipeline. Adapter
  marketplace pattern.

## Related

- [[../platform/spine-13-prefix|13-prefix spine]]
- [[../platform/crdm|Canonical Retail Data Model]]
- [[../platform/overview|Platform overview]]
- [[../platform/worked-example-solex|Solex worked example]] —
  T's stream, observed end-to-end
- [[R-customer]] — sibling Differentiated-Five module (planned)
- [[N-device]] — sibling Differentiated-Five module (planned)
- [[A-asset-management]] — sibling Differentiated-Five module (planned)
- [[Q-loss-prevention]] — primary downstream consumer (planned)

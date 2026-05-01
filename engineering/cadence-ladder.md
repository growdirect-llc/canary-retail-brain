---
tags: [canary, go, architecture, cadence, endpoint-strategy]
last-compiled: 2026-04-30
related: [canary-go-endpoint-library, canary-go-vs-gk-pos-gap-analysis, canary-go-portal, agent-card-format]
---

# Canary Go — Cadence Ladder

> **Governing thesis.** The cadence ladder is the **how-and-why** of Canary Go's endpoint strategy. The three-axis model in the [[canary-go-endpoint-library|Endpoint Library]] (Adapter / Resource / Agent) answers *who* the endpoint serves and *where* it sits. The cadence ladder adds the orthogonal dimension: *what cadence* it runs at. Every endpoint occupies one cell of a 3×5 grid. The tier dictates protocol, SLA, alerting, recovery, and agent contract — and gets baked in at four layers (config, agent contract, runtime behavior, surface). Without the tier dimension, "endpoint" is too coarse a unit; freshness budgets, replay-vs-resync, alert routing, and agent-readiness all collapse into binary green/red instead of the five-tier health model that real multi-store operators actually need.

## Provenance

The cadence ladder is synthesized from a national specialty retailer's ~2011 multi-tier RTI (Real-Time Integration) architecture for store↔hub data flow — an enterprise-scale precedent the founder authored and still finds operationally correct fifteen years later. Key extractions: the **Service Pulse heartbeat** as canonical stream-tier liveness proof, the **DDS message-queue polling** pattern as change-feed, the **Windows-Event-Log + CA-UNICENTER integration** as tier-aware alert routing, and the **Interface Groups taxonomy** (5 groups by cadence) as the prior-art classification of feeds. Raw intakes preserved in `Brain/raw/inbox/technical_design_*` — never the named source in synthesis.

## The five-tier ladder

| Tier | Cadence | Payload | Failure mode | Recovery primitive |
|---|---|---|---|---|
| **Stream** | ms–sec | bytes–KB | "no heartbeat in N seconds" | replay from queue |
| **Change-feed** | min–hour | KB–MB | "lag exceeded" / "queue depth above threshold" | catch up from watermark |
| **Daily batch** | daily | MB | "schedule missed" / "checksum diff" | rerun the job |
| **Bulk window** | weekly | MB–GB | "didn't land in window" / "row count off" | reschedule + investigate |
| **Reference** | monthly+ | varies | "version drift" | force resync, notify consumers |

Each tier has a different protocol fit (stream → WebSocket/SSE/MSMQ; change-feed → REST polling or webhooks; daily batch → cron-driven export; bulk window → scheduled file drop or large GraphQL/REST page; reference → cached lookup with TTL), a different failure metric, and a different recovery operation. **Mixing tiers in one endpoint is the fastest way to make health unmonitorable** — you can't write a single alert that catches both "stream stalled for 10 seconds" and "weekly file didn't land."

## The 3×5 grid (axis × tier)

The endpoint library's three axes (Adapter Substrate / Resource APIs / Agent Surface) cross with the five tiers to produce 15 endpoint archetypes. Every endpoint Canary exposes occupies exactly one cell.

|  | **Stream** | **Change-feed** | **Daily batch** | **Bulk window** | **Reference** |
|---|---|---|---|---|---|
| **A — Adapter** | Webhook receivers, edge-agent push | Polling `/sync/pull` | EOD reconciliation pulls | Weekly assortment imports, catalog drops | Tax tables, fiscal calendar, jurisdiction masters |
| **B — Resource** | SSE feeds, real-time dashboards | `/alerts` tail, `/transactions` tail | `/reports` daily rollups | `/export` bulk dumps | `/risk-dictionary`, `/compliance` lookups, item master |
| **C — Agent** | MCP tool calls (synchronous), SSE | Webhook publishers | Scheduled agent runs (digest, sweeps) | Bulk evidence anchoring, end-of-period attestation | Reference MCP tools (compliance lookups, risk dictionary) |

### Worked examples

**Inventory across the grid:**

| Need | Tier | Endpoint shape |
|---|---|---|
| "What's the current stock at store 12 for SKU 4567?" | Reference (with short TTL) | `GET /inventory/positions?item_id=&location_id=` cached 60s |
| "Stream me every adjustment as it happens." | Stream | SSE `/inventory/sse?merchant_id=&since=` |
| "Pull all adjustments since I last asked, every 15 minutes." | Change-feed | `GET /inventory/adjustments?cursor=&limit=500` |
| "Export every position snapshot for last quarter." | Bulk window | `POST /exports/inventory-positions { from, to }` returns job ID |
| "End-of-day reconciliation against POS counts." | Daily batch | scheduled `POST /reconciliation/run` cron job |

**Alerts across the grid:**

| Need | Tier | Endpoint shape |
|---|---|---|
| Live ops dashboard | Stream | SSE `/alerts/sse` |
| Hourly catch-up tail | Change-feed | `GET /alerts?cursor=&since=` |
| Daily severity rollup for management | Daily batch | scheduled report generation |
| Compliance archive (90-day rolling) | Bulk window | scheduled `/exports/alerts` |
| Alert rule lookup (definition cache) | Reference | `GET /rules/:id` with long TTL |

The same domain (inventory, alerts) shows up in *every* tier. That's the point. Tier completeness is the right unit of capability, not endpoint count.

## The four-layer baking model

Tier metadata isn't a comment in the docs — it's load-bearing in four places.

### Layer 1 — Config schema

Every feed declaration carries `tier:` as a required field. Tier drives required companions:

```yaml
feed: counterpoint.transactions
tier: change-feed              # required
sla:
  freshness_budget: 15m        # required for change-feed
  max_lag: 30m                 # required for change-feed
recovery:
  mode: catch-up-from-watermark  # tier-determined
retention: 90d
alert_pattern: lag-exceeded     # tier-determined
```

Config validation rejects `tier: stream` without a `freshness_budget` in seconds. It rejects `tier: bulk-window` without a schedule. The schema is the first checkpoint where tier mismatches die loudly instead of degrading silently.

### Layer 2 — Agent contract

Every Canary agent declares which tiers it consumes and what freshness it needs. From `agent-card-format`:

```yaml
consumes:
  - feed: alerts.events
    tier: stream
    freshness_budget: 5s
  - feed: items.master
    tier: reference
    freshness_budget: 1d
```

At agent-boot time, the runtime cross-references each declared dependency against the feed config. **Tier mismatch is a hard error, not a runtime warning** — an agent that wants stream-tier alerts but the feed is configured as daily-batch fails to boot. This is the contract the Ross RTI architecture got right: agents that misjudge cadence cause the silent 2 a.m. drift that forensic teams find weeks later.

### Layer 3 — Runtime behavior

Tier parameterizes everything operational:

| Behavior | Stream | Change-feed | Daily batch | Bulk window | Reference |
|---|---|---|---|---|---|
| Health check | heartbeat-every-N-seconds | last-watermark-age | schedule-met | window-landed | version-current |
| Retry policy | exponential backoff to circuit break | lag-bounded retry | rerun on next slot | manual reschedule | ETag-based revalidation |
| Replay vs. resync | replay from queue head | catch up from cursor | rerun specific date | rerun specific window | force resync |
| Alert routing | pager / on-call | ops queue | morning email | weekly review | monthly drift report |
| Cache strategy | none (real-time) | short TTL (mins) | invalidate at cron | invalidate at window close | long TTL with versioning |

The runtime doesn't carry tier-specific code paths for each feed — it carries five tier-specific code paths, parameterized by feed config. Adding a new feed means writing config, not code.

### Layer 4 — Surface (Bases / dashboards / docs)

The Brain wiki has a Bases view that **groups feeds by tier**, not by domain. There are five separate per-tier health rollups, not one binary "all green." The CRB Endpoint Library renders the Tier column on every endpoint table. The Ops Dashboard SSE channel surfaces five health indicators, not one.

This sounds cosmetic. It is not. **Tiering the surface forces tiering everywhere upstream.** A flat "all systems green" rollup tolerates silent change-feed lag because it's not visible. A five-tier rollup makes change-feed lag a visible amber light next to a green stream.

## Adapter substrate as tier expression

The current [[canary-go-endpoint-library|Endpoint Library]] lists three adapter patterns (webhook / polling / edge-agent) without naming them as tier expressions. Naming clarifies and surfaces a missing pattern:

| Adapter pattern | Tier | Example |
|---|---|---|
| Webhook receiver | Stream | Square webhook → `tsp` |
| Polling client | Change-feed | Counterpoint REST polled by `bull` |
| Edge-agent push | Stream-out (push side of stream tier) | `cmd/edge` → `tsp` cloud webhook |
| **Bulk-import** | **Bulk window** | **Weekly catalog drop, vendor master refresh — currently absent from Axis A** |

The bulk-import pattern is required and the current library does not list it. Catalog refreshes, store-list updates, weekly assortment imports, and reference-master synchronization all need a bulk-window-tier inbound channel. The shape: scheduled file drop → SFTP or signed S3 URL → `POST /imports` returns a job ID → status polling endpoint → completion event. The Ross RTI architecture handled this as DDS-staged file transfers over HTTPS streams with explicit landing-window monitoring; Canary's variant is a cloud-native SFTP-or-bucket landing zone with the same lifecycle semantics.

**Action item:** Axis A in the Endpoint Library now lists four patterns, not three.

## Moat-service tier mapping

The accountability rails — Canary's patent-protected differentiators — must be tiered explicitly because they are exactly the services where tier mismatches would be catastrophic.

| Service | Tier | Why |
|---|---|---|
| `blockchain-anchor` | **Bulk window** | Batch hash commits to Bitcoin L2. Per-event stream is cost-prohibitive on L2 settlement. Anchoring is hourly or daily aggregation, not real-time. |
| `l402-otb` | **Change-feed** | Periodic OTB reconciliation against actuals. Stream is overkill (decisions don't shift by the second); daily batch is too slow for in-day budget enforcement. Change-feed at 15-min cadence is the sweet spot. |
| `ildwac` | **Reference + Change-feed** | Cost-model state is reference (slow-moving, cached, versioned). Recomputes on receiving events are change-feed (recompute-on-write, not stream). Two tiers, two endpoint families. |
| `compliance` | **Reference** | Item × regulatory zone × ops blocks are slow-moving lookups. Long-TTL caching with explicit invalidation events. Stream-tier compliance lookups would burn the cache. |

**Do not break this mapping.** A future engineer arguing `blockchain-anchor` should be stream-tier is making an architectural mistake — L2 settlement economics enforce the tier, not preference. Same for the others.

## How this composes with the three-axis model

Axes answer **who consumes the endpoint** (Adapter for POSes inbound, Resource for external systems, Agent for AI). Tiers answer **what cadence it runs at**. Both compose. An endpoint is fully specified only when both are declared:

```
GET /alerts/sse        → Axis B (Resource), Tier: Stream
POST /webhooks/square  → Axis A (Adapter), Tier: Stream
canary-compliance.lookup_zone()  → Axis C (Agent), Tier: Reference
POST /exports/inventory-positions  → Axis B (Resource), Tier: Bulk window
```

This is what gets stamped on every row in the [[canary-go-endpoint-library|Endpoint Library]]: axis + tier. A coverage matrix that looks like (axes × tiers × domains) is the actual measure of "is this API surface complete."

## What this changes in the existing wiki

Three downstream edits land in the same commit set as this card:

1. [[canary-go-endpoint-library]] — add Tier column to every endpoint table; audit all 11 documented services and assign tiers; for each of the 21 undocumented services, propose a tier-shaped endpoint family (not a single generic endpoint); add the bulk-import pattern to Axis A; add a Tier classification section linking back here.
2. [[canary-go-vs-gk-pos-gap-analysis]] — add a "Gap as tier coverage, not endpoint count" section; reframe the 9-namespace GK comparison with the tier lens (GK's Pos namespace is stream + reference; their Service API spans daily batch + bulk window; the gap analysis is now multi-dimensional).
3. The dispatch GRO-717 closes on the commit landing.

## What this is *not*

- **Not a replacement for the three-axis model.** The Adapter / Resource / Agent split stays. This adds a column.
- **Not a code change.** Wiki + spec only. Config schema, agent contract, runtime parameterization all follow in a feed-tier-contract SDD (separate dispatch).
- **Not volatile data.** Specific freshness budgets, queue depth thresholds, current feed counts, SLA numbers — those live in code/config, not in this card. The card defines the structure; numbers live in `deploy/` and `internal/config/`.

## References

- Source intakes (provenance, abstract in synthesis): `Brain/raw/inbox/technical_design_ross_*` (7 files, 2011 RTI architecture)
- [[canary-go-endpoint-library]] — where tiers stamp every endpoint
- [[canary-go-vs-gk-pos-gap-analysis]] — where tier coverage replaces endpoint count as the unit
- [[canary-go-portal]] — project portal
- [[agent-card-format]] — where agent tier consumption gets declared
- Memory: `project_canary_canonical_positioning`, `project_engine_map_and_main_street_archetype`, `feedback_no_volatile_data_in_wiki`, `feedback_extract_working_solution`, `feedback_no_hand_rolling_outside_core_ip`

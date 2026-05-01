---
tags: [canary, go, architecture, endpoint-library, api-contracts, crb-source]
last-compiled: 2026-04-30
related: [canary-go-cadence-ladder, canary-go-portal, canary-go-vs-gk-pos-gap-analysis, canary-architecture, microservice-architecture]
---

# Canary Go Endpoint Library

> **Governing thesis.** Canary Go's API surface organizes along **three axes** crossed with **five cadence tiers** — the axes (Adapter / Resource / Agent) answer *who* the endpoint serves; the tiers (Stream / Change-feed / Daily batch / Bulk window / Reference) answer *what cadence* it runs at. Every endpoint occupies one cell in the 3×5 grid. The library is the partner-facing canonical reference for all three axes; tier metadata is load-bearing for SLAs, alerting, and recovery. It lives here in Brain as the source of truth and is curated to [crb.growdirect.io](https://crb.growdirect.io) as the public partner surface.

The reframe and benchmark behind this structure is in [[canary-go-vs-gk-pos-gap-analysis|Canary Go vs GK-POS — Gap Analysis]]. The cadence-tier model is in [[canary-go-cadence-ladder|Cadence Ladder]] — read it before authoring or auditing entries here.

## The three axes

| Axis | Surface | Direction | Consumers |
|---|---|---|---|
| **A — Adapter Substrate** | Webhook receivers, polling clients, edge agents, **bulk-import landing zones** | POS → Canary | POS vendors, integration partners, merchant IT |
| **B — Resource APIs** | 32-service REST surface | Canary → external | Merchant tools, BI/dashboards, partner platforms, ops engineers |
| **C — Agent Surface** | MCP tools, SSE streams, webhook publishers | Canary → AI agents | Claude Code / Cowork / agent platforms, in-store AI assistants, third-party AI tooling |

## Tier classification

Five tiers, summary form. Full definitions, recovery primitives, and worked examples live in [[canary-go-cadence-ladder|Cadence Ladder]].

| Tier | Cadence | Failure mode | Typical protocol |
|---|---|---|---|
| **Stream** | ms–sec | "no heartbeat in N seconds" | SSE, WebSocket, push webhook |
| **Change-feed** | min–hour | "lag exceeded" | REST polling, webhook subscription |
| **Daily batch** | daily | "schedule missed" | cron-driven export |
| **Bulk window** | weekly | "didn't land in window" | scheduled file drop, paged export |
| **Reference** | monthly+ | "version drift" | cached lookup with TTL |

Every endpoint row below carries a Tier column. Tier mismatches are caught at config-schema time, not at runtime — see Cadence Ladder, four-layer baking model.

---

## Axis A — Adapter Substrate (POS → Canary)

How Canary acquires data from external POSes. The contract every POS adapter must implement is the [[pos-adapter-substrate|POS Adapter Substrate]]. Each adapter is one Go binary in `cmd/`.

**Four adapter patterns, each a tier expression:**

| Pattern | Tier | Implemented by |
|---|---|---|
| Webhook receiver (POS pushes events to Canary) | Stream | `tsp` (:8080) |
| Polling client (Canary pulls from POS REST) | Change-feed | `bull` (Counterpoint), `hawk` (Square) |
| Edge-agent push (on-prem agent emits to cloud) | Stream-out | `cmd/edge` → `tsp` |
| **Bulk-import landing zone (scheduled file drops, vendor masters)** | **Bulk window** | TBD per source |

### Webhook receivers (Stream tier)

| Endpoint | Tier | Status | Notes |
|---|---|---|---|
| `POST /webhooks/square` | Stream | ✅ | Square webhook receiver |
| `POST /webhooks/counterpoint` | Stream | ✅ | Counterpoint event receiver (polling adapter pushes here) |
| `POST /webhooks/inbound` | Stream | ✅ | Square OAuth webhook |
| `POST /webhooks/{source}` | Stream | ⚪ | Generic pattern for future POS adapters |

### Polling adapter contracts (Change-feed tier)

| Endpoint | Tier | Status | Notes |
|---|---|---|---|
| `POST /sync/pull` | Change-feed | ✅ | Trigger manual pull sync (ops use) |
| `GET /sync/status` | Reference | ✅ | Last sync watermarks |
| `POST /merchants/:id/sync/pull` | Change-feed | ✅ | Force immediate poll |
| `GET /merchants/:id/sync/status` | Reference | ✅ | Per-merchant poll watermarks and lag |
| `POST /merchants/:id/connect` | Reference | ✅ | Register API credentials |
| `DELETE /merchants/:id/connect` | Reference | ✅ | Remove credentials |

### Edge agent protocol (Stream-out tier)

The edge agent (`cmd/edge`) runs on-prem (Windows Service) at the merchant's back-office server. **Outbound only** — no inbound endpoints. It pushes derived intelligence packets to the cloud `tsp` webhook receiver. See [[bull|Bull SDD]].

### Bulk-import landing zone (Bulk window tier) — *new pattern*

Scheduled file drops for catalog refreshes, store-list updates, weekly assortment imports, and reference-master synchronization. The shape:

| Endpoint | Tier | Status | Notes |
|---|---|---|---|
| `POST /imports/{kind}` | Bulk window | ⚪ | Returns job ID; `kind ∈ {catalog, stores, vendors, calendar, tax-zones, ...}` |
| `GET /imports/jobs/:id` | Reference | ⚪ | Job status, row count, error log |
| `POST /imports/jobs/:id/finalize` | Bulk window | ⚪ | Commit the imported batch |
| `POST /imports/jobs/:id/cancel` | Bulk window | ⚪ | Abandon an in-progress import |

Bulk-import is required and the original library did not list it. Adding it now closes the Axis A coverage gap.

### POS Adapter Substrate Interface

The Go interface every adapter implements lives in `internal/pos-adapter/`. It defines:

- `Connect(merchantID, credentials) (Session, error)`
- `Pull(session, since time.Time) ([]ARTSEvent, watermark, error)` — Change-feed
- `Subscribe(session, eventTypes) (<-chan ARTSEvent, error)` — Stream
- `Import(session, kind, source) (JobID, error)` — Bulk window
- `Disconnect(session) error`

All output normalizes to **ARTS POSLog** before entering Canary's pipeline.

---

## Axis B — Resource APIs (Canary → external)

The 32-service REST surface. Tier column on every table. ⚪ rows are tier-shaped families — proposed endpoint sets, not placeholders.

### Sales & Transactions

| Pattern | Tier | Service | Status |
|---|---|---|---|
| `GET /transactions/sse` | Stream | `tsp` (:8080) | ⚪ |
| `GET /transactions?cursor=&since=` | Change-feed | `tsp` (:8080) | ✅ partial |
| `GET /transactions/:id` | Reference | `tsp` (:8080) | ✅ |
| `POST /exports/transactions` | Bulk window | `analytics` (:8088) | ⚪ |
| `GET /returns/:id` | Reference | `returns` (:8097) | ⚪ |
| `GET /returns?cursor=&since=` | Change-feed | `returns` (:8097) | ⚪ |
| `POST /returns/:id/authorize` | Stream | `returns` (:8097) | ⚪ |

### Detection & Cases

| Pattern | Tier | Service | Status |
|---|---|---|---|
| `GET /alerts/sse` | Stream | `alert` (:8087) | ⚪ |
| `GET /alerts?cursor=&since=` | Change-feed | `alert` (:8087) | ✅ |
| `GET /alerts/:id` | Reference | `alert` (:8087) | ✅ |
| `PATCH /alerts/:id/{acknowledge,investigate,dismiss,escalate}` | Stream | `alert` (:8087) | ✅ |
| `GET /cases/:id` | Reference | `fox` (:8083) | ✅ |
| `POST /cases/:id/evidence` | Stream | `fox` (:8083) | ✅ |
| `GET /cases/:id/chain` | Reference | `fox` (:8083) | ✅ |
| `GET /rules` | Reference | `chirp` (:8081) | ✅ |
| `GET /rules/:id` | Reference | `chirp` (:8081) | ✅ |
| `POST /rules/:id/evaluate` | Change-feed | `chirp` (:8081) | ✅ |
| `POST /rollup/{daily,hourly}` | Daily batch / Change-feed | `analytics` (:8088) | ✅ |
| `POST /score/:merchant_id` | Change-feed | `analytics` (:8088) | ✅ |

### Master Data

| Pattern | Tier | Service | Status |
|---|---|---|---|
| `GET /items/:id` | Reference | `item` (:8090) | ⚪ |
| `GET /items?cursor=&since=` | Change-feed | `item` (:8090) | ⚪ |
| `POST /imports/items` | Bulk window | `item` (:8090) | ⚪ |
| `GET /items/by-upc/:upc` | Reference | `item` (:8090) | ⚪ |
| `GET /customers/:id` | Reference | `customer` (:8096) | ⚪ |
| `GET /customers?cursor=&since=` | Change-feed | `customer` (:8096) | ⚪ |
| `POST /imports/customers` | Bulk window | `customer` (:8096) | ⚪ |
| `GET /employees/:id` | Reference | `employee` (:8095) | ⚪ |
| `GET /employees?cursor=&since=` | Change-feed | `employee` (:8095) | ⚪ |
| `POST /imports/employees` | Bulk window | `employee` (:8095) | ⚪ |
| `GET /vendors/:id` | Reference | `receiving` (:8092) | ⚪ |
| `GET /vendors?cursor=&since=` | Change-feed | `receiving` (:8092) | ⚪ |

### Operations

| Pattern | Tier | Service | Status |
|---|---|---|---|
| `GET /assets/:id` | Reference | `asset` (:8089) | ⚪ |
| `GET /assets?cursor=&since=` | Change-feed | `asset` (:8089) | ⚪ |
| `POST /assets/:id/state` | Stream | `asset` (:8089) | ⚪ |
| `GET /inventory/positions?item_id=&location_id=&as_of=` | Reference | `inventory` (:8091) | ⚪ |
| `GET /inventory/sse` | Stream | `inventory-as-a-service` (:9081) | ⚪ |
| `GET /inventory/adjustments?cursor=&since=` | Change-feed | `inventory` (:8091) | ⚪ |
| `POST /reconciliation/run` | Daily batch | `inventory` (:8091) | ⚪ |
| `POST /exports/inventory-positions` | Bulk window | `inventory` (:8091) | ⚪ |
| `GET /purchase-orders/:id` | Reference | `receiving` (:8092) | ⚪ |
| `GET /purchase-orders?cursor=&since=` | Change-feed | `receiving` (:8092) | ⚪ |
| `POST /receipts` | Stream | `receiving` (:8092) | ⚪ |
| `GET /transfers/:id` | Reference | `transfer` (:8093) | ⚪ |
| `GET /transfers?cursor=&since=` | Change-feed | `transfer` (:8093) | ⚪ |
| `POST /transfers/:id/{ship,receive}` | Stream | `transfer` (:8093) | ⚪ |
| `GET /pricing/effective?item_id=&location_id=&as_of=` | Reference | `pricing` (:8094) | ⚪ |
| `GET /price-rules?cursor=&since=` | Change-feed | `pricing` (:8094) | ⚪ |
| `POST /imports/price-rules` | Bulk window | `pricing` (:8094) | ⚪ |
| `GET /promotions?status=&cursor=` | Change-feed | `pricing` (:8094) | ⚪ |

### Intelligence

| Pattern | Tier | Service | Status |
|---|---|---|---|
| `POST /search` (semantic) | Reference | `owl` (:8084) | ✅ |
| `GET /risk-dictionary/:entity_id` | Reference | `owl` (:8084) | ✅ |
| `GET /ej-spine/:employee_id` | Reference | `owl` (:8084) | ✅ |
| `POST /embed` | Reference | `owl` (:8084) | ✅ |
| `GET /analytics/sse` | Stream | `analytics` (:8088) | ⚪ |
| `GET /analytics/rollups?cursor=&since=` | Change-feed | `analytics` (:8088) | ✅ partial |

### Identity & Tenancy

| Pattern | Tier | Service | Status |
|---|---|---|---|
| `POST /merchants` | Stream | `identity` (:8086) | ✅ |
| `GET /merchants/:id` | Reference | `identity` (:8086) | ✅ |
| `PATCH /merchants/:id` | Stream | `identity` (:8086) | ✅ |
| `POST /users` | Stream | `identity` (:8086) | ✅ partial |
| `GET /users/:id` | Reference | `identity` (:8086) | ✅ |
| `POST /sessions` | Stream | `identity` (:8086) | ✅ |
| `DELETE /sessions/:token` | Stream | `identity` (:8086) | ✅ |
| `POST /oauth/{authorize,refresh}` | Stream | `identity` (:8086) | ✅ |
| `GET /oauth/callback` | Stream | `identity` (:8086) | ✅ |

### Reports

| Pattern | Tier | Service | Status |
|---|---|---|---|
| `POST /reports/:report_id/generate` | Daily batch | `report` (:8098) | ⚪ |
| `GET /reports/:report_id/runs/:run_id` | Reference | `report` (:8098) | ⚪ |
| `POST /reports/schedules` | Reference | `report` (:8098) | ⚪ |
| `POST /exports/{kind}` | Bulk window | `report` (:8098) | ⚪ |

### Cost & Settlement (satoshi rollup — Canary-unique moat)

The cost-rollup surface composes three patent-protected primitives (ILDWAC + L402-OTB + blockchain-anchor) into a satoshi-denominated billing model. See [[canary-go-satoshi-cost-model|Satoshi Cost Model]] and SDD `satoshi-cost-rollup.md` for full detail.

| Pattern | Tier | Service | Status |
|---|---|---|---|
| `POST /usage/forecast` (5-input diagnostic) | Reference | `report` (or new `forecast`) | ⚪ |
| `GET /usage/statements?merchant_id=&since=` | Change-feed | `report` | ⚪ |
| `GET /usage/statements/:id` | Reference | `report` | ⚪ |
| `GET /usage/statements/:id/proof?event_id=` | Reference | `report` | ⚪ |
| `GET /usage/sse?merchant_id=` | Stream | `ops-dashboard` | ⚪ |
| `GET /usage/current?merchant_id=` | Reference | `ops-dashboard` | ⚪ |
| `POST /usage/statements/:id/pay` | Stream | `l402-otb` | ⚪ |
| `GET /revshare/channels?period=` | Reference | `commercial` | ⚪ |

### Accountability Rails (Canary-unique — no GK equivalent)

These are the moats. Tier mapping is patent-protected territory; do not break it.

| Pattern | Tier | Service | Status |
|---|---|---|---|
| `GET /ildwac/cost-model/:item_id` | Reference | `ildwac` (:9082) | ⚪ |
| `POST /ildwac/recompute` | Change-feed | `ildwac` (:9082) | ⚪ |
| `GET /ildwac/lineage?item_id=&from=&to=` | Reference | `ildwac` (:9082) | ⚪ |
| `GET /l402-otb/budget?merchant_id=` | Change-feed | `l402-otb` (:9090) | ⚪ |
| `POST /l402-otb/reconcile` | Change-feed | `l402-otb` (:9090) | ⚪ |
| `POST /l402-otb/gate` | Stream | `l402-otb` (:9090) | ⚪ |
| `POST /blockchain-anchor/commit` | Bulk window | `blockchain-anchor` (:9086) | ⚪ |
| `GET /blockchain-anchor/proofs/:hash` | Reference | `blockchain-anchor` (:9086) | ⚪ |
| `GET /compliance/lookup?item_id=&zone_id=` | Reference | `compliance` (:9091) | ⚪ |
| `GET /compliance/zones/:id` | Reference | `compliance` (:9091) | ⚪ |
| `POST /compliance/blocks` | Reference | `compliance` (:9091) | ⚪ |
| `GET /device-contracts/:device_id` | Reference | `device-contracts` (:9083) | ⚪ |
| `POST /device-contracts/:device_id/breach` | Stream | `device-contracts` (:9083) | ⚪ |
| `GET /store-network-integrity/anomalies?cursor=` | Change-feed | `store-network-integrity` (:9088) | ⚪ |
| `GET /store-network-integrity/cross-location/:case_id` | Reference | `store-network-integrity` (:9088) | ⚪ |
| `POST /field-capture/register` | Reference | `field-capture` (:9087) | ⚪ |
| `GET /field-capture/lookup?source=&field=` | Reference | `field-capture` (:9087) | ⚪ |
| `GET /commercial/rebates?vendor_id=` | Reference | `commercial` (:9089) | ⚪ |
| `POST /commercial/chargebacks` | Stream | `commercial` (:9089) | ⚪ |
| `GET /commercial/invoices?cursor=&since=` | Change-feed | `commercial` (:9089) | ⚪ |
| `GET /raas/resolve/:merchant_id` | Reference | `raas` (:8099) | ⚪ |
| `POST /raas/build-key` | Reference | `raas` (:8099) | ⚪ |
| `POST /webhooks/{source}` | Stream | `ecom-channel` (:9080) | ⚪ |
| `GET /ecom-channel/sync/status` | Reference | `ecom-channel` (:9080) | ⚪ |

### Ops & Health

| Pattern | Tier | Service | Status |
|---|---|---|---|
| `GET /health` | Reference | every service | ✅ |
| `GET /status` | Reference | most services | ✅ partial |
| `GET /ops-dashboard/sse` | Stream | `ops-dashboard` (:9084) | ⚪ |
| `GET /ops-dashboard/devices` | Reference | `ops-dashboard` (:9084) | ⚪ |
| `GET /store-brain/sse` | Stream | `store-brain` (:9085) | ⚪ |
| `GET /store-brain/presence/:location_id` | Reference | `store-brain` (:9085) | ⚪ |

---

## Axis C — Agent Surface (Canary → AI agents)

The MCP tool registry, SSE streams, and webhook publishers that make Canary AI-native. Every tool carries a tier.

### MCP tool registry

Each agent-facing service exposes an MCP server with named tools. JWT-gated. REST internally; MCP at the edge.

| MCP Server | Tier | Service | Tools | Status |
|---|---|---|---|---|
| `canary-compliance` | Reference | `compliance` (:9091) | 7 tools (item × zone × ops blocks) | ✅ |
| `canary-raas` | Reference | `raas` (:8099) | 7 tools (namespace resolution, key construction) | ✅ |
| `canary-fox` | Mixed (Reference for query, Stream for evidence-add) | `fox` (:8083) | TBD | ⚪ |
| `canary-chirp` | Reference + Change-feed | `chirp` (:8081) | TBD (rule introspection, force-evaluate) | ⚪ |
| `canary-owl` | Reference | `owl` (:8084) | TBD (search, risk lookup, EJ spine query) | ⚪ |
| `canary-store-brain` | Stream + Reference | `store-brain` (:9085) | TBD (presence resolution, session governance) | ⚪ |
| `canary-ops` | Stream + Reference | `ops-dashboard` (:9084) | TBD (device health queries, alert gates) | ⚪ |
| `canary-cost` | Reference | `report` or new `forecast` | 4 tools: `cost.preview_call`, `cost.merchant_summary`, `cost.statement_proof`, `cost.forecast` (verifiable billing surface — Canary moat) | ⚪ |

### SSE streams (Stream tier)

| Stream | Service | Purpose |
|---|---|---|
| `GET /ops-dashboard/sse` | `ops-dashboard` (:9084) | Real-time device health, MCP observability |
| `GET /store-brain/sse` | `store-brain` (:9085) | Presence events, session state changes |
| `GET /alerts/sse` | `alert` (:8087) | Live alert feed |
| `GET /transactions/sse` | `tsp` (:8080) | Live transaction tail |
| `GET /inventory/sse` | `inventory-as-a-service` (:9081) | Live stock-position changes |
| `GET /analytics/sse` | `analytics` (:8088) | Live metric updates |

### Webhook publishers (Stream / Change-feed tier)

Outbound from Canary to merchant-configured destinations:

| Pattern | Tier | Trigger |
|---|---|---|
| `POST {merchant-configured-url}` | Stream | Alert created · Case escalated · Detection rule fired |
| `POST {merchant-configured-url}` | Change-feed | Daily digest · Reconciliation summary · Risk-score delta |

Each merchant configures outbound webhook destinations through `/merchants/:id/webhooks` (TBD).

---

## Coverage status

Two dimensions: per-service status, and per-tier completeness.

### Per-service status (as of 2026-04-30, post-Phase-2 contracts)

| Status | Services | Endpoints |
|---|---|---|
| ✅ Documented | 32 | ~250 patterns across 5 tiers |
| ⚪ Undocumented | 0 | — |

All 32 services in the spine + extended block now have published endpoint contracts in `docs/sdds/go-handoff/microservice-architecture.md`. The library tables here are the partner-facing summary; full request/response/error contracts and state machines live in the SDD.

### Per-tier coverage (Canary as of 2026-04-30)

| Tier | Coverage | Notes |
|---|---|---|
| Stream | Substantial | Webhook receivers ✅, SSE streams ✅ (`alerts`, `transactions`, `inventory`, `analytics`, `ops-dashboard`, `store-brain`), state-transition mutations ✅ |
| Change-feed | Substantial | Adapter polling ✅, resource tail-feeds ✅ (cursor-paginated lists across all 32 services) |
| Daily batch | Substantial | `analytics` rollups ✅, `inventory` reconciliation ✅, `commercial` reconciliation ✅, `store-network-integrity` correlations ✅, `report` schedule runs ✅ |
| Bulk window | Substantial | Bulk-import landing zone ✅ (Axis A — `/imports/{kind}` for items, customers, employees, vendors, invoices, regulatory-zones); `/exports/{kind}` ✅ (Axis B — transactions, inventory positions, returns, compliance attestations) |
| Reference | Substantial | Identity ✅, Owl ✅, Compliance ✅, all masters ✅, accountability rails ✅ |

**Status: tier-balanced.** The original bulk-window gap is closed. The library's structural completeness shifts from "21 undocumented services" to "32 services contracted across all 5 tiers." Next phase of work is partner-facing CRB curation — selecting which subset of these 250 patterns is appropriate for the public partner site versus internal-only.

## Conventions

- **URL shape:** `/{resource}` for collections, `/{resource}/{id}` for single items, `/{resource}/{id}/{subresource}` for related records. Verbs on the action: `/alerts/:id/acknowledge`, not `/alerts/:id/status`.
- **Tenant isolation:** Every endpoint scopes by `merchant_id` — path parameter, query parameter, or implicit via JWT claim.
- **Response shape:** JSON. Errors as `{"error": {"code": "...", "message": "..."}}`. Pagination cursor-based via `?cursor=...&limit=...`.
- **Auth:** JWT Bearer for all non-`/health` endpoints. MCP tools authenticated via the MCP protocol's session header plus tenant-scoped JWT.
- **Versioning:** No URL versioning. Breaking changes go through the Hardening phase per the [[canary-go-portal#agent-lifecycle|agent PMO lifecycle]].
- **Schema-qualified DB writes:** `app.`, `sales.`, `metrics.` always; never unqualified.
- **Tier declaration:** Every endpoint config carries `tier:` as a required field. Tier mismatches between feed config and agent contract are hard errors at boot — see [[canary-go-cadence-ladder|Cadence Ladder]] §4-layer baking model.
- **Idempotency:** Stream and change-feed tiers require idempotency keys on all `POST` and `PATCH` operations. Bulk-window tier uses job IDs as natural idempotency.

## Where this lives

- **Source of truth:** this article + per-service SDDs in `docs/sdds/go-handoff/` + per-endpoint tables in `microservice-architecture.md`
- **Partner-facing publication:** [crb.growdirect.io](https://crb.growdirect.io) — curated subset, no internal-only details
- **Internal cross-references:** [[canary-go-cadence-ladder]] · [[canary-go-portal]] · [[microservice-architecture]] · [[canary-go-vs-gk-pos-gap-analysis]]
- **Curation flow:** Brain wiki → Brain/dispatches → CRB push (per [[canary-go-portal|three-vault architecture]])

## Sources

- [[canary-go-cadence-ladder]] — the tier model
- [[canary-go-vs-gk-pos-gap-analysis]] — the analysis behind this structure
- [[microservice-architecture]] — current per-service endpoint detail
- [[canary-go-portal]] — project portal and SDD index

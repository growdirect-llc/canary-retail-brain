---
tags: [canary, go, rapidpos, counterpoint, vendor-crosswalk, adapter, cadence, cost-model, bull, edge, var, channel-partner, revshare]
last-compiled: 2026-05-01
related: [canary-go-cadence-ladder, canary-go-endpoint-library, canary-go-satoshi-cost-model, canary-bull, channel-revshare-architecture]
---

# Canary Go ↔ RapidPOS — Vendor Crosswalk

> **Governing thesis.** RapidPOS is Canary's first VAR channel partner, distributing NCR Counterpoint to a hundreds-of-merchants installed base. The cadence ladder maps Counterpoint's poll-based REST API into the **Change-feed** tier with edge-agent stream-out from the merchant's on-prem `cmd/edge` to the cloud `tsp` webhook. The cost model attributes Counterpoint-sourced traffic to RapidPOS's channel partner identifier; period-end Lightning settlement to RapidPOS's address is proportional to data flow through their adapter — **architecture, not contract**. The article is structured for the RapidPOS technical and commercial leadership.

This crosswalk pairs with [[crb-rapidpos-alignment-notes]] and [[catz-rapidpos-alignment-notes]] for the broader relationship context. The focus here is the cadence-ladder and cost-model lens.

## Adapter substrate

| Property | Value |
|---|---|
| Canary binaries | `canary-bull` (cloud, port `:8085`) + `canary-edge` (on-prem Windows Service) |
| Inbound pattern | Polling client (cloud) + edge-agent push |
| Authentication | API key per merchant (Counterpoint-issued) |
| Wire format | Counterpoint REST JSON → CRDM (ARTS POSLog) normalization |
| `SourceCode` value | `counterpoint` |
| Channel partner | **RapidPOS** (configured per-merchant via `canary-identity.merchant.var_of_record`) |
| Edge agent required | **Yes** — runs on merchant's back-office Windows Server alongside SQL Server + Counterpoint |
| Bulk-import lifecycle | `POST /imports/items` for catalog drops (Counterpoint catalog export) |

Counterpoint is a closed-source on-prem POS with a thin REST veneer (~50 endpoints). `canary-bull` polls those endpoints from cloud at configurable intervals; `canary-edge` runs on-prem to handle latency-sensitive operations and pre-screens detection-rule signals before emitting derived intelligence packets to cloud (never raw transaction data). The edge-agent path is the **stream-out** tier expression.

## Tier mix for Counterpoint-via-RapidPOS merchants

| Tier | Counterpoint traffic shape | Examples |
|---|---|---|
| **Stream** | Edge-agent push to cloud `tsp` | Detection-rule pre-screened signal packets, real-time alerts from on-prem |
| **Change-feed** | Cloud-side polling at configurable cadence | `bull` polling Counterpoint REST every 60-300s for transaction tail |
| **Daily batch** | EOD reconciliation runs | Counterpoint stock count vs Canary derived position |
| **Bulk window** | Initial migration + weekly catalog refresh | Counterpoint Item File → Canary `item` master via `/imports/items` |
| **Reference** | Lookups + masters | Customer reads, vendor master, employee roster |

The dominant tier is **Change-feed** — Counterpoint's polling cadence is the heartbeat. Edge-agent push is a stream-out adjunct that handles the latency-sensitive subset (detection signals).

## Cost-model worked example

Typical Counterpoint-via-RapidPOS merchant — multi-store specialty retail (3 locations) on on-prem Counterpoint:

| Input | Value |
|---|---|
| Transactions / month | 25,000 |
| Active locations | 3 |
| POS sources | 1 (Counterpoint) |
| Agent decisions / day | 5,000 |
| Retention preference | 1 year |
| Compliance complexity | 1 |

Forecast (illustrative):

```
Ingestion (Change-feed): 25K × 5 × 4   = 500K sats     ← change-feed tier weight 4
Detection + cases:        25K × 720    = 18M sats
Storage:                  25K × 365 × 0.05 = 456K sats
Agent decisions:          5K × 7,500   = 37.5M sats
Multi-location:           3 × 50K      = 150K sats
Adapter overhead:         1 × 100K     = 100K sats
Edge-agent overhead:      additional 200K (stream-out)
Anchor amortized:         20K
Platform floor:           200K
────────────────────────────────────────────────────
TOTAL:                    ~57M sats / month
                          ≈ $34 / month at $60K BTC
                          ≈ $23 / month at $40K BTC
```

## Channel rev-share — the architectural commitment

This is where RapidPOS earns. **Architecture, not contract.**

```yaml
# excerpt from deploy/cost-calibration.yaml
revshare:
  channels:
    counterpoint:
      partner_id: "rapidpos-uuid"
      share: 0.20
      lightning_address: "rapidpos@payments.example"
```

For the worked example merchant above (~57M sats/month flowing through the `counterpoint` SourceCode):

```
RapidPOS rev-share = 57M × 0.20 = 11.4M sats / merchant / month
                   ≈ $7 / merchant / month at $60K BTC
```

**At 100 RapidPOS-deployed Counterpoint merchants on Canary**: ~1.14B sats/month = ~$700/month direct to RapidPOS. **At 1,000 merchants** (full installed-base reach): ~$7,000/month. **All settled via Lightning at period close.** No quota negotiation, no annual reconciliation, no "we'll true-up in Q3" lag — proportional to actual data flow, anchored to the same Bitcoin L2 commit that anchors the merchant's verifiable usage statement.

### Channel attribution clarification (architecture refinement)

The cost-calibration YAML keys channel rev-share by `source_code` ("counterpoint"). In the multi-VAR reality (RapidPOS, NCR-direct, future VARs), this needs refinement: a single source code maps to multiple channels.

The cleaner model — captured here as the architectural direction — keys channel attribution by **`var_of_record`** stored at merchant onboarding in `canary-identity`:

```sql
-- Refinement: aggregate rev-share by VAR-of-record, not just by source_code
WITH events AS (
    SELECT 
        e.merchant_id,
        m.var_of_record AS channel_partner_id,
        e.source_code,
        SUM(e.sat_cost) AS sats
    FROM metrics.cost_events e
    JOIN app.merchants m ON e.merchant_id = m.id
    WHERE e.occurred_at BETWEEN $1 AND $2
    GROUP BY e.merchant_id, m.var_of_record, e.source_code
)
```

Calibration becomes:

```yaml
revshare:
  channel_partners:                    # keyed by partner_id, not source
    rapidpos:
      partner_id: "rapidpos-uuid"
      share: 0.20
      lightning_address: "rapidpos@payments.example"
      sources: ["counterpoint"]        # which source codes this partner channels
    ncr-direct:
      partner_id: "ncr-direct-uuid"
      share: 0.15
      lightning_address: "ncr@..."
      sources: ["counterpoint"]
```

This refinement is captured in the [[canary-go-ncr-counterpoint-crosswalk]] companion article and slated for incorporation in the next satoshi-cost-rollup SDD revision.

## RapidPOS-specific adapter behavior

Three operational nuances:

1. **Edge-agent install runs alongside Counterpoint.** `canary-edge` deploys as a Windows Service on the merchant's back-office server. RapidPOS already has a relationship with that server (they support Counterpoint there). Canary's deploy can ride RapidPOS's existing software-delivery pipeline — `canary-edge` is one more package in their installer.
2. **API-key custody is RapidPOS's lever.** Counterpoint API keys are issued at the customer level. RapidPOS holds the relationship; Canary's adapter onboarding flow goes through RapidPOS to issue the key. This is the channel partner's commercial leverage point — RapidPOS sees every merchant onboarding in real time.
3. **Detection-rule pre-screening at edge reduces cloud cost.** `canary-edge` runs the cheap detection rules locally and emits only derived signals. Canary's cloud-side cost-to-serve is materially lower than a polling-only adapter. The savings flow back to RapidPOS's rev-share — better edge architecture = more profit per merchant.

## What's documented

| Concern | Where |
|---|---|
| Adapter implementation | `docs/sdds/go-handoff/bull.md` |
| Edge-agent design | go-module-layout.md `cmd/edge` |
| Counterpoint API reference | [[ncr-counterpoint-api-reference]] |
| Connection runbook | [[ncr-counterpoint-connection-runbook]] |
| Counterpoint document model | [[ncr-counterpoint-document-model]] |
| Endpoint spine map | [[ncr-counterpoint-endpoint-spine-map]] |
| Modernization narrative | [[ncr-counterpoint-modernization-path]] |
| RapidPOS relationship | [[ncr-counterpoint-rapid-pos-relationship]] |
| RapidPOS alignment (CRB lens) | [[crb-rapidpos-alignment-notes]] |
| RapidPOS alignment (CATz lens) | [[catz-rapidpos-alignment-notes]] |
| Cost model implications | This article + [[canary-go-satoshi-cost-model]] |

## Partner integration touchpoints

For RapidPOS technical + commercial leadership:

- **Joint kickoff / first 10 merchants** — pilot phase, calibration period; Canary observes actual workload to refine per-merchant unit costs.
- **Channel onboarding API** — RapidPOS issues Counterpoint API keys per merchant; `POST /merchants/:id/connect` registers the credentials and tags `var_of_record = rapidpos`.
- **Period-end settlement dashboard** — RapidPOS sees per-merchant rev-share accruals in real time via `GET /revshare/channels?period=current`.
- **Lightning settlement** — RapidPOS provides Lightning address; period close auto-pays. Verifiable against same Bitcoin L2 commit that anchors merchant statements.
- **Detection-rule pre-screening calibration** — RapidPOS sees the edge-agent's detection performance metrics; can request rule profile updates per-merchant or per-region.

## See also

- [[canary-go-cadence-ladder]] — tier model
- [[canary-go-satoshi-cost-model]] — pricing mechanism
- [[channel-revshare-architecture]] — rev-share architectural primitive
- [[canary-go-ncr-counterpoint-crosswalk]] — NCR-direct VAR channel (different partner, same source code)
- [[crb-rapidpos-alignment-notes]] · [[catz-rapidpos-alignment-notes]] — broader relationship context
- SDD: `docs/sdds/go-handoff/bull.md` · `docs/sdds/go-handoff/satoshi-cost-rollup.md`

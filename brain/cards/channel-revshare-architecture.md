---
card-type: infra-capability
card-id: channel-revshare-architecture
card-version: 1
domain: platform
layer: cross-cutting
feeds:
  - infra-satoshi-cost-rollup
receives:
  - infra-satoshi-cost-rollup
  - infra-l402-otb-settlement
tags: [channel, revshare, var, partner, attribution, lightning, source-code, micropayment, rapidpos, ncr]
status: approved
last-compiled: 2026-05-01
---

# Channel Rev-Share — Architecture, Not Contract

## What this is

The mechanism by which channel partners (RapidPOS, NCR Counterpoint VARs, future ecosystem partners) earn revenue proportional to data flow through their adapter, settled via Lightning at period close. **Not a contract clause negotiated annually** — a SQL aggregation by `SourceCode` plus a Lightning route, anchored to the same Bitcoin L2 commit that anchors the merchant's usage statement.

## Purpose

Aligns channel incentive with platform value-flow rather than seat-quota. RapidPOS earns when Counterpoint-tagged events flow through Canary; the more value Canary surfaces in those events, the more both parties earn. No quota negotiation, no annual true-up — the rev-share is per-period, per-event, settled via Lightning.

## Structure

### Three rev-share classes

| Class | Source | How it settles |
|---|---|---|
| First-party services | All 32 Canary services | Full revenue retained by GrowDirect |
| Partner-contributed services | Future ecosystem services that join the agent surface | Per-microservice share declared at registration; gate enforces split |
| Channel rev-share | Adapter-attributed traffic by `SourceCode` | Period-end aggregation × channel share, settled to partner Lightning address |

### Channel attribution (existing primitives)

| Primitive | Role |
|---|---|
| CRDM `SourceCode` field | Every event tagged with originating adapter source |
| `app.feed_registry` | Adapter feed declares producer (channel partner mapping) |
| `metrics.cost_events.source_code` | Indexed for efficient per-source aggregation |
| `app.cost_calibration.revshare.channels` | Per-channel share configuration |
| Lightning channel to partner address | Settlement instrument |

**Every component already exists.** Rev-share is a SQL group-by + Lightning send.

### Settlement choreography

```
Period-end cron fires
  → Aggregate sat_cost grouped by source_code over period
  → For each channel with revshare.channels[source].share > 0:
       channel_payout_sats = sum(sat_cost_for_source) × share
  → Generate Lightning payment to channel.lightning_address
  → Anchor channel rev-share record in same blockchain-anchor batch
       as the merchant statement
  → Statement reaches SETTLED status only after all rev-share payments confirm
```

### Configuration

```yaml
# excerpt from deploy/cost-calibration.yaml
revshare:
  channels:
    counterpoint:
      partner_id: "rapidpos-uuid"
      share: 0.20                              # 20% of satoshis flowing through Counterpoint events
      lightning_address: "rapidpos@payments.example"
    square:
      share: 0.0                               # no channel partner
    shopify:
      share: 0.0
```

Share rates are calibration parameters — quarterly recalibration per published changelog. Partner can update `lightning_address` via signed config update; share changes go through joint review (commercial decision, not platform-side adjustment).

## Why architecture, not contract

Three structural advantages over traditional VAR rev-share contracts:

1. **Per-period, per-event proportional**. RapidPOS earns exactly proportional to actual data flow through their adapter — no minimum, no cap, no quota. A merchant that uses Counterpoint heavily generates more rev-share to RapidPOS than a low-volume merchant. Aligned by data flow, not by negotiation.
2. **Cryptographically anchored**. Rev-share record commits to Bitcoin L2 alongside the merchant's usage statement. RapidPOS can verify their rev-share against an immutable timestamp — no quarterly reconciliation drama, no "we'll true-up in Q3" lag.
3. **Composable with partner-contributed microservices**. Future: a partner builds a microservice that joins Canary's agent surface (e.g., a specialized fraud-detection model). The microservice declares its rev-share at registration; the gate enforces. Same architecture; different revenue source.

## Consumers

- canary-commercial (`/revshare/channels?period=` endpoint)
- Channel partners (settlement reports + Merkle proofs)
- Sales / commercial team (forecasting partner take-rate)
- Auditors / regulators (rev-share verification)

## Sources

- Wiki: [[canary-go-satoshi-cost-model]] §rev-share
- SDD: `docs/sdds/go-handoff/satoshi-cost-rollup.md` §settlement choreography
- Card: [[infra-satoshi-cost-rollup]]
- Card: [[canary-commercial]]

## Routing

```
event landed via canary-bull (Counterpoint adapter)
  → CRDM record tagged source_code = "counterpoint"
  → cost_event written with source_code populated
  → period-end aggregation by source_code
  → rev-share split per calibration share
  → Lightning payment to RapidPOS address
  → settlement record committed to L2
```

## Anti-pattern

- Don't conflate channel rev-share with referral commission. Channel rev-share continues for the life of the merchant relationship, proportional to flow. Referral commission is one-time. Use the right primitive.
- Don't allow `share` > 0.5 for any channel without explicit founder + commercial review. The 50% cap is a guardrail; exceeding it shifts platform economics fundamentally.
- Don't expose channel partner identifiers (Lightning addresses) to merchants. Merchants see their bill, not the rev-share split.
- Don't promise immediate channel rev-share payouts. Payouts settle at period-end alongside the merchant statement — same anchor commit, same Lightning batch.

## See also

- Card: [[infra-satoshi-cost-rollup]]
- Card: [[canary-commercial]]
- Card: [[infra-l402-otb-settlement]]
- Memory: `project_bart_var_partnership`, `project_rapidpos_stakeholders`, `project_canary_rapidpos_primary_shift`

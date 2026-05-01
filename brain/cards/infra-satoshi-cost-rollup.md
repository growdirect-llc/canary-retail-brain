---
card-type: infra-capability
card-id: infra-satoshi-cost-rollup
card-version: 1
domain: platform
layer: infra
feeds:
  - infra-cadence-ladder
  - infra-l402-otb-settlement
  - infra-blockchain-evidence-anchor
  - ilwac-extended-bitcoin-standard
receives:
  - infra-cadence-ladder
tags: [satoshi, cost-rollup, pricing, bitcoin-standard, lightning, l402, micropayment, rev-share, diagnostic, moat, verifiable-billing]
status: approved
last-compiled: 2026-05-01
---

# Satoshi Cost Rollup

## What this is

The platform-wide instrument that measures, accumulates, and settles cost-to-serve in satoshis instead of seat-based fiat. Every event, agent decision, byte-day, and external passthrough is metered and rolled up to the merchant level; period-end statements are committed to a Bitcoin L2 via canary-blockchain-anchor and settled via Lightning. The natural extension of three patent-protected primitives already in the stack — ILDWAC, L402-OTB, and blockchain-anchor — composed into a single commercial mechanism.

## Purpose

Replaces seat-based pricing with usage-anchored pricing. Aligns Canary's incentive with merchant efficiency (fewer wasteful events → lower bill). Exposes channel rev-share as architecture (data-flow attribution) rather than contract clause. Makes the moat — verifiable billing against Bitcoin L2 — a sales conversation in the first thirty seconds of the diagnostic.

## Structure

### Cost components

```
sat_cost(merchant, period) =
  Σ events × tier_weight × service_unit_cost      ← ingestion + processing
+ Σ storage_GB × tier × days                      ← retention
+ Σ agent_decisions × decision_cost               ← MCP / API
+ Σ external_passthroughs                         ← upstream API costs
+ Σ blockchain_anchor_share                       ← amortized L2 commit
+ base_platform_floor                             ← merchant-tier minimum
```

### Settlement modes

| Mode | When | Primitive |
|---|---|---|
| Pre-funded OTB | Steady-state | L402-OTB Lightning wallet |
| Per-call gate | High-value or external-passthrough calls | L402 invoice on insufficient budget |
| Period-end with L2 anchor | Trusted merchants, monthly close | Merkle root → blockchain-anchor → Lightning |

### Key tables (per `satoshi-cost-rollup.md` SDD)

- `app.cost_calibration` — versioned tier weights, service unit costs, decision costs, rev-share config
- `metrics.cost_events` — append-only metering log, partitioned monthly
- `app.usage_statements` — period-end statements with Merkle root + anchor commit
- `app.usage_statement_line_items` — per-component breakdown
- `app.usage_statement_proofs` — Merkle paths for verification

## Consumers

- Every Canary service emits cost events on its lifecycle hooks (ingest, decide, store, passthrough)
- canary-l402-otb consumes the cost stream for budget gating
- canary-blockchain-anchor receives period-end Merkle roots for L2 commit
- canary-ops-dashboard surfaces real-time consumption via SSE
- canary-cost MCP server exposes preview/summary/proof tools to agents
- Sales-side diagnostic (POST /usage/forecast) translates 5 simple inputs into a forecast + competitor side-by-side
- Merchants verify any line item against the L2-committed Merkle root via `cost.statement_proof`

## Sources

- [[canary-go-satoshi-cost-model]] — narrative spine
- SDD: `docs/sdds/go-handoff/satoshi-cost-rollup.md` — buildable spec
- [[infra-cadence-ladder]] — tier weights live there
- [[infra-l402-otb-settlement]] — settlement primitive
- [[infra-blockchain-evidence-anchor]] — anchoring primitive
- [[ilwac-extended-bitcoin-standard]] — founder intent on Bitcoin-standard cost accounting

## Routing

```
service emits cost_event
  → metrics.cost_events (Postgres, partitioned by month)
  → Valkey accumulator updates (per-merchant, per-period)
  → l402-otb gate consults accumulator
  → period-end reconciliation cron
  → rollup query produces line items
  → Merkle root computed
  → canary-blockchain-anchor batch commit
  → Lightning invoice generated
  → merchant pays
  → channel rev-share settles to partner Lightning addresses
  → cost_events.settlement_id set
```

## Why this is the moat

Three claims competitors can't make:

1. **Verifiable billing against Bitcoin L2.** Patent-protected primitive (canary-blockchain-anchor). No POS competitor has this; none can build it without rebuilding the evidentiary rail.
2. **Microservice-level cost transparency.** Canary's bill is itemized by service consumed. Square / Lightspeed / Toast charge flat fees that hide cost-to-serve. Canary's structure is transparent by construction.
3. **Channel rev-share as data-flow architecture.** Channel partners earn a share of every satoshi flowing through their adapter — settled per period, anchored per L2 commit. No quota negotiation; no annual contract.

## Anti-pattern

- Don't expose the calibration matrix to merchants (commercially sensitive)
- Don't conflate satoshi-denominated with crypto-volatile billing (Canary takes the BTC volatility, merchant gets predictable fiat-equivalent at quote time)
- Don't try to keep Lightning channel state in lockstep with cost_events (they reconcile at period-end; mid-period drift is allowed)
- Don't build the diagnostic as a calculator; it's a discovery instrument that drives a conversation

## See also

- Wiki: [[canary-go-satoshi-cost-model]]
- SDD: `docs/sdds/go-handoff/satoshi-cost-rollup.md`
- Cards: [[infra-cadence-ladder]], [[infra-l402-otb-settlement]], [[infra-blockchain-evidence-anchor]], [[ilwac-extended-bitcoin-standard]]

---
card-type: runbook
card-id: diagnostic-five-input-forecast
card-version: 1
domain: platform
layer: cross-cutting
feeds:
  - infra-satoshi-cost-rollup
receives:
  - infra-satoshi-cost-rollup
tags: [diagnostic, sales, discovery, forecast, five-inputs, side-by-side, comparison, moat-conversation]
status: approved
last-compiled: 2026-05-01
---

# Diagnostic — Five-Input Cost Forecast

## What this is

The discovery instrument used at the opening of every Canary sales conversation. Five simple inputs the buyer answers in under a minute; the platform produces a satoshi cost forecast and a side-by-side comparison against any seat-based competitor (Square / Lightspeed / Toast / Counterpoint license). The diagnostic anchors the conversation in the buyer's operating reality, not the competitor's pricing rubric.

## Purpose

Three moves the diagnostic enables in a sales conversation:

1. **Reframes the conversation.** "Your headcount" → "your operating reality." Buyers stop comparing seat counts and start comparing what they actually run.
2. **Surfaces the value layer.** A merchant pays Canary based on what flows through. Platform incentive aligns with merchant efficiency.
3. **Anchors the moat.** The diagnostic ends with: "Want to see your bill verified against a Bitcoin L2 timestamp?" No competitor can answer that. Conversation lands in moat territory by minute three.

## Inputs

| Symbol | Input | Typical SMB range | What it captures |
|---|---|---|---|
| **T** | Transactions / month | 1K – 100K | Ingestion + detection volume |
| **L** | Active locations | 1 – 20 | Tenant scaling, multi-store correlation |
| **P** | POS sources | 1 – 3 | Adapter mix (Square + Counterpoint + ecom) |
| **A** | Agent decisions / day | 100 – 10,000 | MCP tool call volume |
| **R** | Retention preference | 90d / 1y / 7y | Storage cost driver |

Optional sixth: **C** — compliance complexity (regulated items × regulatory zones). Defaults to 1.

## Outputs

```
Estimated monthly cost: f(T, L, P, A, R, C) sats
Fiat equivalent at <quoted BTC/USD rate>: $XX.XX

Breakdown:
  Ingestion + processing:   X sats
  Detection + cases:        X sats
  Storage:                  X sats
  Agent decisions:          X sats  (typically the largest variable)
  Multi-location overhead:  X sats
  Adapter overhead:         X sats
  Anchor amortized:         X sats
  Platform floor:           X sats
  ─────────────────────────────────
  TOTAL:                    X,XXX,XXX sats / month
                            ≈ $XX.XX / month at $YY,YYY BTC

Comparison vs seat-based <Square|Lightspeed|Toast|Counterpoint>:
  Seat baseline:           $XXX.XX / month
  Canary delta:            ~XX% cheaper / more expensive
  Calculation:             <transparent math>
  Value-capture note:      <e.g., "Square also takes 2.6% of transaction value">

Verifiable path:
  "On Canary, your monthly bill is independently verifiable against an
   immutable Bitcoin L2 timestamp. No competitor offers this."
```

## Structure (REST contract)

```
POST /usage/forecast
Auth: optional JWT (anon allowed for marketing-site embeds)

Body:
  {
    "transactions_per_month": 20000,
    "active_locations": 3,
    "pos_sources": ["counterpoint", "shopify"],
    "agent_decisions_per_day": 5000,
    "retention_days": 365,
    "compliance_complexity": 1,
    "comparison_baseline": "square"
  }

Response:
  Forecast object with breakdown, fiat quote, and comparison side-by-side.
```

## Worked example

Typical SMB specialty retailer:
- T = 20,000 transactions/month
- L = 3 locations
- P = 2 sources (Counterpoint + Shopify)
- A = 5,000 agent decisions/day
- R = 1 year retention
- C = 1 (no regulated items)

Forecast: ~60M sats/month → ~$36/month at $60K BTC.

Square baseline for same merchant: ~$240/month (3 locations × $80) plus ~2.6% of transaction value.

Canary lands ~85% cheaper *and* doesn't take a percentage of transaction value. The 30-second answer becomes a 3-minute conversation about what they're actually paying for.

## Sources

- Wiki: [[canary-go-satoshi-cost-model]]
- SDD: `docs/sdds/go-handoff/satoshi-cost-rollup.md` Layer 5

## Sales-side usage

The diagnostic embeds three places:

1. **Public marketing site** — anonymous forecast with no JWT; lead-capture follows
2. **Discovery call** — sales rep walks the buyer through the form on a screenshare; answer lands in the conversation
3. **Buyer self-service** — once they're a prospect, their account dashboard shows live forecast updates as they connect adapters

The buyer never sees the calibration matrix. They see line items, fiat equivalent, comparison, verification path. Calibration is platform-internal.

## Anti-pattern

- Don't pitch the diagnostic as a calculator. It's a discovery instrument; the conversation matters more than the number.
- Don't lead with the moat claim before the buyer has felt the pricing reframe. The order is: reframe → surface → anchor.
- Don't show a single point estimate. Show low/mid/high band — calibration variance is real, and bands inoculate against "the bill came in higher than the quote" complaints.
- Don't expose internal cost-component math (per-tool decision cost, tier weights). The buyer sees outputs; the calibration is commercial sensitivity.

## See also

- Card: [[infra-satoshi-cost-rollup]]
- Card: [[infra-cadence-ladder]] (where tier weights live)
- Card: [[platform-thesis]] (every entity has a meter)

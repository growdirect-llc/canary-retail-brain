---
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-a, bubble, asset-management, anomaly-detection]
sources:
  - Canary-Retail-Brain/modules/A-asset-management.md
  - Canary/canary/services/onboarding/baseline_calculator.py
  - Canary/canary/models/metrics/risk.py
last-compiled: 2026-04-24
----

# Canary Module — A (Asset Management / "Bubble")

## Summary

A — codenamed **Bubble** — is multivariate anomaly detection over
[[canary-module-n-device|N's]] device registry. Where
[[canary-module-q-loss-prevention|Q (Chirp)]] runs largely-univariate
rules over single transactions, A would maintain a per-device
behavioral "bubble" (multi-dimensional expected range) and signal
when a device departs from it.

**Status — read carefully.** The
[[../projects/RetailSpine|Retail Spine]] documents A as v1
(shipping) because the architectural commitment is real and the
foundation infrastructure is in place. The dedicated A-as-a-module
surface — per-device baselines, multivariate scoring, cross-device
correlation, signal emission — **is not yet implemented as code.**
This is brain-vs-code drift in the spine doc itself; flagged as
open question #1 in the canonical brain article and again below.

This wiki article documents what exists today, what doesn't, and
where the existing scaffold lives.

## What exists today (foundation)

| Component | Status | File path | A's intended use |
|---|---|---|---|
| Baseline calculator (transaction-level) | shipping | `Canary/canary/services/onboarding/baseline_calculator.py` | Seed for per-device baseline computation |
| Metrics risk schema | shipping | `Canary/canary/models/metrics/risk.py` | Substrate for multivariate feature storage (TransactionFeature, FeatureDefinition) |
| N's device registry | shipping (opportunistic populate) | `Canary/canary/models/sales/devices.py` | Device-side input |
| T's transaction stream | shipping | `Canary/canary/models/sales/transactions.py` | Event-side input |
| Q's alert pipeline | shipping | `Canary/canary/models/app/alerts.py` (and detection.py) | Signal output channel |

## What doesn't exist (the A-specific layer)

| Intended component | Status |
|---|---|
| Per-device baseline tables (`device_baselines`, `device_baseline_history`) | not implemented |
| Streaming device-state observer | not implemented |
| Multivariate anomaly scorer | not implemented |
| Cross-device correlation engine | not implemented |
| `device_anomalies` table in `app` schema | not implemented |
| `canary-bubble` MCP server | not implemented |
| A-specific SDD in `Canary/docs/sdds/v2/` | not present |

## SDD crosswalk

| SDD | Path | A's relationship |
|---|---|---|
| analytics | `Canary/docs/sdds/v2/analytics.md` | Referenced as analytics surface; no A-specific spec |
| data-model | `Canary/docs/sdds/v2/data-model.md` | Defines `metrics` schema (where A's baselines would live) |

A does not yet have a dedicated SDD. Writing one would be the first
implementation deliverable.

## Where A fits on the spine

A is one of the [[../projects/RetailSpine|Retail Spine]]
Differentiated-Five modules. Per
[[../projects/RetailSpine#4-store-operations-management|Store
Operations § BST inventory]], A is the intended primary owner of:

- **Suspicious Activity Analysis** (multivariate device-level
  anomalies, distinct from Q's transaction-level rules)

A is also the intended cross-device pattern detector for **Store
Optimization Analysis** and a long-tail feeder for **Performance
Measurement**.

## Open Canary-specific questions

1. **No SDD yet.** A's first implementation deliverable is probably
   an SDD at `Canary/docs/sdds/v2/bubble.md` or similar. Spine doc
   now reflects A as "v1 (design — implementation pending)" so the
   Brain-vs-code drift on status itself is cleared.
2. **Bubble dimensions.** Empirical decision; needs to be tuned
   against Solex's transaction stream as a starting fixture.
3. **Scoring method choice.** Mahalanobis distance, isolation
   forest, or per-dimension threshold-count. Affects explainability.
4. **Baseline cadence and cold-start.** Both unspecified.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-data-model|Canary Data Model]]
- [[canary-architecture|Canary Architecture]]
- [[canary-module-t-transactions|Canary Module — T (Transaction Pipeline)]]
- [[canary-module-n-device|Canary Module — N (Device)]]
- [[canary-module-q-loss-prevention|Canary Module — Q (Loss Prevention)]]

## Sources

- `Canary-Retail-Brain/modules/A-asset-management.md` — canonical vendor-neutral spec (design intent)
- `Canary/canary/services/onboarding/baseline_calculator.py` — Stage 2 seed
- `Canary/canary/models/metrics/risk.py` — TransactionFeature / FeatureDefinition substrate
- `Canary/canary/models/sales/devices.py` — N's registry (A's input)
- `Canary/canary/models/sales/transactions.py` — T's stream (A's input)
- `Canary/canary/models/app/alerts.py` — Q's alert pipeline (A's output channel)

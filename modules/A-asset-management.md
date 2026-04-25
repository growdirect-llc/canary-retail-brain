---
classification: confidential
owner: GrowDirect LLC
type: module-article
prefix: A
codename: Bubble
status: v1 (design — implementation pending)
sibling-modules: [T, R, N, Q]
---

# A — Asset Management

A — codenamed **Bubble** — is anomaly detection over the asset
registry. Where Q (Loss Prevention) detects anomalies in the
*transaction stream*, A detects anomalies in the *device estate*:
sudden drift in transaction velocity per device, unexpected device
behavior versus a per-device baseline, cross-device pattern shifts
within a store. Q says "this transaction looks wrong"; A says "this
device is acting wrong."

A is one of the [[../platform/spine-13-prefix#v1-differentiated-five-t-r-n-a-q|
Differentiated-Five]] modules. **Status reality check:** the spine
ships A as v1 because the architectural commitment is real and the
infrastructure to support it (baseline_calculator, metrics risk
tables, [[N-device|N's]] registry) is in place. The dedicated
A-as-a-module surface — anomaly rules, per-device baselines, the
"Bubble" detection layer — is not yet implemented as code. This
article describes A's design intent and existing scaffold; the open
questions section names the work needed to close the gap between
intent and implementation.

## Purpose

A owns three jobs:

1. **Maintain per-device baselines.** A "baseline" is the expected
   range of behavior for a specific device in a specific store at a
   specific time-of-day-of-week — derived from observed history.
   Baselines update continuously; A holds the projection.
2. **Detect anomalies against baselines.** When a device's observed
   behavior departs from its baseline by more than a configured
   tolerance, A fires a signal. The signal becomes a Q alert (or, in
   v3, a W work item) for human review.
3. **Provide cross-device pattern detection.** When multiple devices
   in one store, or one device across stores, drift in correlated
   ways, A surfaces the pattern. This is the "the whole store is
   acting weird" detection that single-device baselines miss.

A does **not** own:

- Single-transaction anomaly detection. That's Q's surface.
- Device curation. That's [[N-device|N's]] surface.
- Case management for A's signals. Cases are Fox's surface (under Q).

## Why "Bubble"

The codename. A device's expected behavior is a "bubble" of
acceptable values across many dimensions (transaction count per
hour, average transaction value, void rate, refund rate, network
posture, time-between-transactions, employee-mix). A device staying
inside its bubble is healthy. A device leaving its bubble is the
signal A fires on.

The bubble metaphor matters operationally because it implies:

- The bubble is **multivariate**, not a single threshold per metric
- The bubble is **per-device**, not a global expectation
- The bubble is **adaptive** — it updates as the device's normal
  behavior shifts (a register that becomes the busy register at a
  store legitimately changes its bubble)
- Departing the bubble produces a *single* signal, not one per
  metric — the signal is "this device is outside expected behavior,"
  with the dimensions that contributed surfaced as evidence

## BST cells A populates

| Domain | BST | A's role |
|---|---|---|
| Store Operations | **Suspicious Activity Analysis** | Primary owner — A's signals *are* this BST |
| Store Operations | **Loss Prevention Analysis** | Feeder via signal-to-Q-alert handoff |
| Store Operations | Performance Measurement | Feeder — device-bubble compliance metrics |
| Store Operations | Store Optimization Analysis | Feeder — cross-device store-level pattern detection |
| Products & Services | Business Performance Analysis | Long-tail feeder via product-velocity-by-device patterns |

A is the only module on the v1 spine that owns a multivariate
anomaly-detection workload. Q's rules are largely univariate
threshold checks; A's bubble model is a different shape of detection.

## CRDM entities touched

| CRDM entity | A's relationship | How |
|---|---|---|
| **Things** (devices) | Reads | A's baselines and signals key on N's `device_id` |
| **Events** | Reads | T's transactions are A's input data |
| **Workflows** | Triggers | A's signals create Q alerts → potential Fox cases |
| Places | Reads | Per-store baselines join through `location_id` |
| People | Reads | Cashier-on-device patterns join through `employee_id` |

A's posture: **A is a projection-and-detection layer over T's events
and N's registry. It owns no entities of its own — only baselines and
signals.** This is what keeps A clean architecturally; it's a
read-mostly layer that produces signals consumable by Q.

## Architecture (intended)

A is a four-stage projection-and-detection pipeline:

```
N + T  →  baseline build  →  observation  →  anomaly score  →  signal
 (1)         (2)                 (3)             (4)             (5)
```

| Stage | Responsibility | Where it would live |
|---|---|---|
| **1. Inputs** | N's device registry + T's transaction stream | already in place |
| **2. Baseline build** | Periodic batch job: compute per-device per-time-bucket expected ranges across the bubble dimensions | `metrics` schema; baseline_calculator scaffold exists |
| **3. Observation** | Streaming projection of current device state vs. baseline | not yet implemented |
| **4. Anomaly score** | Multivariate distance from baseline; cross-device correlation | not yet implemented |
| **5. Signal** | Score above threshold → Q alert via shared alert channel | uses Q's alert pipeline |

The seed of stage 2 already exists — the baseline_calculator
computes transaction-level patterns (amount, refund rate, velocity)
for Chirp's threshold reference. Extending it to per-device-keyed
baselines and additional bubble dimensions is the v1 implementation
work.

## Existing scaffold

While A as a module is not yet code-complete, the supporting
infrastructure is in place:

| Component | Status | Used by A how |
|---|---|---|
| Baseline calculator | shipping (transaction-level) | Stage 2 base; needs per-device extension |
| Metrics schema risk tables (TransactionFeature, FeatureDefinition) | shipping | Stage 4 substrate — multivariate feature storage |
| N's device registry | shipping (model + opportunistic populate) | Stage 1 device-side input |
| T's transaction stream | shipping | Stage 1 event-side input |
| Q's alert pipeline | shipping | Stage 5 output channel |

Reading this list: **the foundation is built; the A-specific
projection and detection layer is what's missing.**

## Schema crosswalk (intended)

A would write to the `metrics` schema (analytics-flavored) for
baselines and to the `app` schema for signals (alongside Q's
alerts). Concrete table inventory pending implementation.

| Table (intended) | Schema | Purpose |
|---|---|---|
| `device_baselines` | `metrics` | Per-device per-time-bucket expected ranges (dimensions × statistics) |
| `device_baseline_history` | `metrics` | Append-only baseline-revision log |
| `device_anomalies` | `app` | Per-device current anomaly scores; signal threshold breaches |
| `device_pattern_correlations` | `metrics` | Cross-device correlation matrices (per store, per region) |

A would read from N's `sales.devices`, T's `sales.transactions`, and
T's `sales.transaction_line_items`.

## Service-name markers (v0.7 microservice index)

| Service slot | Responsibility | Currently lives in |
|---|---|---|
| `a-baseline-builder` | Periodic per-device baseline computation | extends `canary/services/onboarding/baseline_calculator.py` |
| `a-observer` | Streaming device-state projection | not yet implemented |
| `a-scorer` | Multivariate anomaly scoring | not yet implemented |
| `a-correlator` | Cross-device pattern detection | not yet implemented |
| `a-signal-emitter` | Score-to-alert handoff | reuses Q's alert pipeline |
| `a-mcp` | Read-only A-state MCP surface | not yet implemented |

**Perpetual-vs-period boundary.** Canary owns the entire stack — per-device anomaly detection has no merchant-side equivalent at SMB tier. Implementation route: `legacy-native`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (A's inputs):

- N's device registry — Stage 1 device side
- T's transaction stream — Stage 1 event side
- Q's existing baseline_calculator output — Stage 2 seed

**Downstream consumers** (what reads A's signals):

- **Q (Loss Prevention)** — A's signals become Q alerts
- **Fox (case management, under Q)** — A-originated alerts can
  promote to cases
- **Future W (Work Execution)** — generalized detection-and-case
  pattern; A is one of many signal sources W will consume

## Agent surface (intended)

`canary-bubble` MCP server, read-only:

- Device-baseline lookup (current bubble for a device)
- Device-anomaly query (current/historical scores for a device)
- Store-pattern query (cross-device correlations for a store)
- Baseline-history audit (how a device's bubble has evolved)

None of these tools exist yet.

## Security posture

Inherited from N (registry side) and T (event side). Tenant scoping
on every baseline / signal table via `merchant_id`. RLS on the
metrics schema follows the same pattern as the rest of Canary.

A's specific security concern: a misconfigured baseline produces
either too many alerts (false positives erode trust) or too few
(misses theft). Baseline tuning is therefore an explicit per-merchant
configuration surface — never a global default at the platform.

## Open questions

These are the work items needed to close the design-intent vs.
implementation gap.

1. **Implementation gap.** Spine doc has been reframed to
   "v1 (design — implementation pending)" so the documentation no
   longer overclaims; the work item now is to ship the code. A is
   the most differentiating of the Differentiated-Five and is the
   strongest case for prioritizing v1.x implementation.
2. **Bubble dimension selection.** Which dimensions belong in the
   per-device bubble? Transaction count, value, void rate, refund
   rate, network state, employee mix, time-between are obvious
   candidates. Adding too many dimensions makes the bubble noisy;
   too few makes it miss. Empirical tuning from Solex's stream is
   the proposed path.
3. **Multivariate scoring choice.** Mahalanobis distance? Isolation
   forest? Per-dimension threshold count? The choice affects
   explainability (why did this device trip?) — pick the most
   explainable model that meets accuracy needs.
4. **Baseline cadence.** Daily rebuild? Weekly? Streaming update?
   Affects compute cost and adaptation speed.
5. **Cross-device correlation scope.** Per-store? Per-region? Per-
   merchant? Larger scopes catch coordinated patterns; smaller
   scopes are computationally cheaper.
6. **Cold-start.** A new device has no baseline. What does A do
   for the first N days? Likely: borrow from a similar-class device
   in the same store or fall through to Q's univariate rules.

## Roadmap status

- **v1 (design — code pending)** — Foundation infrastructure in
  place. The A-specific projection / detection / signal layer is
  unbuilt.
- **v1 (implementation)** — Build out the A surface above. This is
  the largest engineering chunk on the Differentiated-Five.
- **v2** — Cross-store pattern detection. Baseline-tuning UX for
  retailers.
- **v3+** — Generalized into [[../platform/spine-13-prefix#v3-full-spine-s-p-l-w|
  W (Work Execution)]] — A's pattern is the seed for W's domain-
  agnostic anomaly model.

## Related

- [[../platform/spine-13-prefix|13-prefix spine]]
- [[../platform/crdm|Canonical Retail Data Model]]
- [[../platform/overview|Platform overview]]
- [[N-device]] — registry A runs against
- [[T-transaction-pipeline]] — event source for A's projections
- [[Q-loss-prevention]] — primary downstream consumer of A's signals
- [[R-customer]] — sibling Differentiated-Five module

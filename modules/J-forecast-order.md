---
classification: confidential
owner: GrowDirect LLC
type: module-spec
prefix: J
status: v2 (design)
sibling-modules: [C, D, F]
---

# J — Forecast & Order

The forecast and order module owns demand forecasting, replenishment-point calculation, and automated purchase-order recommendation. J reads the historical movement ledger to derive demand patterns, reads current stock-on-hand to validate replenishment needs, and subscribes to OTB headroom constraints before recommending a purchase order.

J is one of the [[spine-13-prefix#v2-crdm-expansion-c-d-f-j|v2 CRDM expansion]] modules. It closes the forecast-and-ordering gap: moving from manual buyer-driven replenishment (guesses based on intuition) to demand-driven automated ordering (recommendations based on ledger signals and OTB constraints).

## Purpose

J owns three jobs:

1. **Forecast demand.** Read the stock-ledger movement history (receipts, sales via T, RTVs, markdowns) to derive demand patterns. Calculate demand velocity (units per day, per week) per item per location. Produce a rolling 13-week demand forecast per item per location.
2. **Calculate replenishment parameters.** For each item at each location, calculate: Reorder Point (ROP) — the on-hand level at which replenishment should trigger; Economic Order Quantity (EOQ) — the order size that minimizes total cost; and Safety Stock — buffer inventory to protect against demand variance. These are the inputs to the PO-recommendation algorithm.
3. **Generate PO recommendations.** When current on-hand falls below ROP, recommend a purchase order. The recommendation specifies: quantity (EOQ or multiple thereof), supplier (from C item master), requested receipt date (based on supplier lead time), and OTB headroom check (validate that C approves the recommended PO amount).

J does **not** own:

- Cost-method choice or landed-cost updates. That belongs to [[F-finance|F (Finance)]].
- Buyer approval or PO commitment. That belongs to F.
- Item-master or supplier curation. That belongs to [[C-commercial|C (Commercial)]].
- Markdown or pricing-driven demand shifts. That belongs to [[P-pricing-promotion|P (Pricing & Promotion)]] in v3.

## CRDM entities touched

| CRDM entity | J's relationship | How |
|---|---|---|
| **Events** | Reads | Stock-ledger movements (receipts, sales, RTVs, adjustments) are J's input data for demand derivation |
| **Things** | Reads | Item master (supplier, lead time, EOQ parameters) via C; doesn't curate |
| **Places** | Reads | Location on-hand and movement history; doesn't curate Places itself |
| **Workflows** | Emits events | J publishes PO recommendations (implicit workflow: awaiting buyer approval) |
| **People** | Reads | Identifies buyer owner of a department/category |

J's posture: **J is a Subscriber that reads ledger history and current SOH, calculates replenishment parameters, and publishes PO recommendations.** J does not post to the ledger; instead, J generates recommendations that F converts to formal POs.

## Ledger relationship

**J is SUBSCRIBER and PUBLISHER of replenishment recommendations.**

Ledger reads J consumes:

- **Movement history per item per location** — receipts, sales (via T), RTVs, adjustments over the trailing 12–26 weeks. Used to calculate demand velocity and variance.
- **Current stock-on-hand (SOH)** — snapshot of on-hand quantity and value per item per location. Used to validate that current position is below ROP.
- **On-order quantity** — sum of quantities in POs that have been committed but not yet received. Used to calculate projected on-hand (SOH + on-order).

Movements J publishes (indirectly via F):

| Recommendation | Trigger | Ledger impact (upon PO commitment) |
|---|---|---|
| **PO recommendation** | Current SOH + on-order falls below ROP | F converts to a formal PO; D posts the receipt when it arrives |

Example flow: J calculates that Widget A at Store #5 has ROP=50, SOH=30, on-order=0. J publishes recommendation: "Order 100 units of Widget A from Supplier X, receipt date 7 days." F routes to buyer for approval. Buyer approves. F posts a formal PO. D receives the shipment and posts a receipt movement 7 days later.

**Perpetual-vs-period boundary.** Canary owns: demand signal + forecast + reorder-point calculation. Merchant tool owns: long-range merchandise planning (merchant tool if any). Default implementation route: `integrated-hybrid`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (data producers):

- Stock-ledger movement history (from T, D, C)
- Current SOH (from ledger snapshot, via C/D)
- Item master and supplier lead times (from C)
- OTB headroom (from C)

**Downstream consumers** (data subscribers):

- **F (Finance)** — F subscribes to PO recommendations and converts approved recommendations to formal POs.
- **C (Commercial)** — C provides item master, supplier, and lead-time data; C validates OTB headroom for each recommendation.
- **D (Distribution)** — D receives formal POs from F and posts receipts when stock arrives.
- **Merchant buyer** — J's recommendations are visibility for the buyer to accept, modify, or override.

## Agent surface

J exposes MCP tool families for planner and buyer workflows:

- **Demand forecast** — query 13-week demand forecast per item per location with variance bounds (low/mid/high scenarios)
- **Replenishment parameters** — inspect ROP, EOQ, safety stock per item per location with calculation breakdown (lead time, demand velocity, variance)
- **PO recommendations** — view pending PO recommendations, sorted by priority (below-ROP threshold first); see recommendation details (quantity, supplier, requested receipt date)
- **Recommendation approval** — (buyer/planner role) accept, modify, or reject a recommendation; if approved, route to F for PO creation
- **Replenishment dashboard** — at-a-glance view per location or per category: items below ROP, items at risk (falling below ROP within lead time), items over-stocked
- **Forecast accuracy audit** — compare forecast (from prior periods) to actual sales; calculate Mean Absolute Percentage Error (MAPE); identify forecast bias
- **What-if simulation** — (planner role) simulate demand scenarios (e.g., "if sales increase 10%") and see impact on ROP and recommended order quantities

## Security posture

- **Auth.** PO recommendations are read-only to merchants. Buyer-side approval/override requires `buyer` or `planner` role. Modification of replenishment parameters (ROP, EOQ, safety stock) requires `merchandiser` or `planner` role.
- **Tenant scoping.** Every recommendation and forecast carries `merchant_id`; every read is row-level-secured. J cannot recommend orders for another merchant.
- **Auditability.** Every recommendation is timestamped with the forecast version and parameters used. If parameters change, prior recommendations are invalidated and new ones are generated.
- **Forecast refresh cadence.** Forecast is recalculated on a merchant-configurable schedule (daily recommended; weekly minimum). Buyers can request manual recalculation but cannot override forecast data directly.

## Roadmap status

- **v2 (design)** — Demand forecasting (velocity + variance), ROP/EOQ calculation, PO recommendation generation. MCP tools for planner/buyer workflows. Integration with C for item master and OTB validation. Integration with D for receipt matching (used to validate forecast accuracy). No advanced features like multi-location allocation optimization, seasonal decomposition, or machine-learning demand modeling.
- **v2.1** — Seasonal demand modeling (detect and forecast seasonal patterns). Lead-time variance modeling (supplier consistency tracking).
- **v3** — Integration with P (Pricing & Promotion) to account for markdown-driven demand shifts. Integration with S (Space, Range, Display) for assortment-eligibility gating (item cannot be ordered for a location where it is not authorized to sell). Integration with W (Work Execution) for exception handling (e.g., "demand forecast is stale because sales data is late").

## Lawn-and-garden specifics

J is disproportionately load-bearing for L&G chains relative to other retail verticals. Three reasons:

1. **Five-month plant-supply lead time.** Live-plant nurseries set the upcoming season's variety and quantity in Q4, propagate cuttings or seedlings through Q1, and ship live stock starting in Q2. The retailer who didn't commit by January doesn't get the inventory in April. J's forecast horizon must reach at least 26 weeks for live-plant categories — much longer than the 13-week default for hard goods. Manifest field `vendors.lead_time_days` defaults to ~120 days for `vendor_type=live_plant_nursery` to drive this correctly.
2. **Regional drive-radius constraints.** Live perennials don't survive 3-day cross-country shipping. Vendors are graded by `drive_radius_miles` from the merchant's distribution point, and J's recommender excludes out-of-radius vendors for live-plant categories. The buyer's working set of vendors is therefore much smaller than for hard-goods retail, which makes vendor performance tracking proportionally more important.
3. **Seasonal pre-book carry-forward.** Garden centers pre-book hot-selling SKUs (e.g., specific tomato cultivars, region-specific perennials) months in advance via `D.backorder_records` with `source='seasonal_pre_book'`. J's recommendation engine reads those committed quantities and excludes them from the open-headroom calculation. This is a different shape from generic SMB retail where pre-booking is rare.

J's manifest also captures **substitution-aware forecasting** (`purchase_order_lines.substitution_item_id` — vendor sent a different cultivar; future demand model learns the substitution pattern) and **damage-on-arrival rate tracking** (`vendor_performance_records.damage_returns_count` — a live-plant-specific quality signal). Both are unusual outside the vertical and central within it. See `Canary-Retail-Brain/case-studies/lawn-and-garden-catz-phase1-diagnostic.md` §3.3 for the as-is buyer pain points pre-Canary (typically: spreadsheet-driven seasonal commits, no formal vendor scorecard, overstock at Sep clearance because forecasts didn't account for soft seasons).

## Counterpoint upstream coverage

Per the [[../../docs/sdds/canary/ncr-counterpoint-retail-spine-integration|NCR Counterpoint Retail Spine Integration SDD]] §6.9, Counterpoint exposes a **partial** J surface: Vendor master is reachable, and Document with `DOC_TYP=PO` carries the PO header + lines for ingest. The `ReplenishmentOrder` endpoint family is documented but availability is flagged as pending verification — the live Counterpoint REST scan is incomplete on that path. Until verified, J's Counterpoint adapter populates `vendors` and `purchase_orders` from the verified surface, and the demand-forecast + replenishment-recommendation logic stays Canary-native (no upstream replenishment engine to delegate to). If Counterpoint's replenishment engine turns out to be REST-exposed at the merchant we cross-reference but don't replace — Canary's ML-driven model is the differentiator and should not be supplanted by a vendor-internal heuristic engine.

## Open questions

1. **Demand-forecast scope.** Should J forecast at SKU level, at SKU+location level, or both? Current assumption: both, with location-level overrides available to account for store-level demand differences.
2. **Lead-time variance.** If supplier lead time is variable (5–10 days), should J use the worst-case (10d) for safety-stock calculation, or use a probabilistic model?
3. **Seasonal reset.** At the start of a new season (e.g., back-to-school, holiday), should J ignore prior-year demand history and forecast based on recent demand only? Or blend the two?
4. **Recommendation auto-commit.** Should J auto-commit PO recommendations that are below a certain threshold (e.g., auto-commit orders <$100), or do all recommendations require explicit buyer approval?

## Related

- [[../platform/stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]]
- [[../platform/retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]]
- [[../platform/crdm|Canonical Retail Data Model (CRDM)]]
- [[../platform/spine-13-prefix|The Canary Retail Spine — 13 Modules]]
- [[C-commercial|C (Commercial)]]
- [[D-distribution|D (Distribution)]]
- [[F-finance|F (Finance)]]
- [[P-pricing-promotion|P (Pricing & Promotion)]] (v3, future integration)
- [[S-space-range-display|S (Space, Range, Display)]] (v3, future integration)

## Sources

- [[../../GrowDirect/Brain/wiki/katz-scm-2003-archetype|Katz SCM 2003 Archetype]] — demand forecasting and replenishment optimization patterns
- [[../../GrowDirect/Brain/wiki/retek-rms-perpetual-inventory|Retek RMS — Perpetual-Inventory Movement Ledger]] — RDF/RRO/AIP forecasting and replenishment modules; demand-velocity signals
- [[../../GrowDirect/Brain/wiki/secure-retail-operating-model-2006|Secure Retail Operating Model (2006)]] — replenishment and inventory-position planning workflows

---

*Classification: confidential. Owner: GrowDirect LLC. Created 2026-04-24. J (Forecast & Order) is a v2 module spec within the Canary Retail Spine. It is design-stage; implementation is pending.*

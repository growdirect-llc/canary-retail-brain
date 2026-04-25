---
classification: confidential
owner: GrowDirect LLC
type: module-spec
prefix: P
status: v3 (design)
sibling-modules: [C, S, L, W]
---

# P — Pricing & Promotion

P owns the promotion engine, markdown management, pricing-elasticity tracking, and multi-channel price reconciliation. P publishes price-change events to the stock ledger that revalue on-hand inventory and drive GL cost-of-goods accounting.

P is one of the [[spine-13-prefix#v3-full-spine-s-p-l-w|v3 full-spine expansion]] modules. It extends the promo-code dimension that v1 T (Transaction Pipeline) inherits from Square into a full promotion engine: bundle rules, threshold promotions, conditional offers, markdown cadence, and elasticity feedback loops.

## Purpose

P owns four jobs:

1. **Promotion engine.** Design and execute promotion rules: bundle offers (buy 2 get 1), threshold promotions (spend $50 save $10), conditional offers (discount on category A if you buy category B), BOGO patterns. Rules are merchant-configurable and time-bounded.
2. **Markdown management.** Lifecycle management for markdowns: proposal → approval → execution → analytics. Track markdown timing, velocity, and margin impact. Post markdown events to the stock ledger as cost-complement adjustments (under RIM) or as GL revaluation entries.
3. **Pricing-elasticity tracking.** Measure demand elasticity per item: when price changes by X%, does demand change by Y%? Use elasticity signals to guide future markdown timing and promotion strategy.
4. **Multi-channel price reconciliation.** Maintain price parity across channels (in-store, online, marketplace). Flag discrepancies and route to buyer for resolution.

P does **not** own:

- The item master or cost basis. That belongs to [[C-commercial|C (Commercial)]].
- Physical space and location assignments. That belongs to [[S-space-range-display|S (Space, Range, Display)]].
- Demand forecasting. That belongs to [[J-forecast-order|J (Forecast & Order)]].
- Workforce scheduling or labor cost attribution. That belongs to [[L-labor-workforce|L (Labor & Workforce)]].

## CRDM entities touched

| CRDM entity | P's relationship | How |
|---|---|---|
| **Things** | Owns the Promotion subset | Promotion rules linked to items/categories with conditions and timing |
| **Events** | Publishes | Price-change events and markdown events to the stock ledger |
| **Workflows** | Reads | Reads ledger movements to calculate markdown impact on cost/margin |
| **Places** | Reads | Location-level price overrides (regional pricing, local markdowns) |
| **People** | Reads | Buyer approval workflow for markdown proposals; analytics recipients |

P's posture: **P is a Promotion factory that publishes price-change events to the stock ledger and tracks elasticity signals.** P does not modify the ledger directly; it contracts with D (Distribution) and F (Finance) to post events.

## ARTS mappings

ARTS includes a rudimentary `promo_code` dimension on transactions but no promotion-engine specification. Canary defines Promotion and Markdown mechanics internally:

| Canary construct | Definition | Reference |
|---|---|---|
| **Promotion rule** | Time-bounded, condition-based offer with discount/bundle mechanics | Square promotions API (v1 baseline); extend to bundle, threshold, conditional |
| **Bundle offer** | N items at discounted total price (e.g., buy 2 get 1 at 50% off) | Retail standard; T records multi-line bundle transactions |
| **Threshold promotion** | Discount triggered at transaction level (spend $50, save $10) | Square promotions API family |
| **Conditional offer** | Discount on item A only if item B is purchased | Retek-era rule engines; not standard in Square |
| **Markdown** | Permanent or time-bounded retail-price reduction (e.g., seasonal clearance) | Inherited from RIM cost-method; markdown event triggers cost-complement recalc |
| **Elasticity signal** | Demand change per unit price change; tracked per item per period | Retek RMS analytics; input to future markdown forecasting |

Cross-reference to ARTS:

- ARTS POSLog carries `promo_code` (P can trace promos to sales)
- ARTS Customer Model has no promotion or elasticity construct

## Ledger relationship

**P is PUBLISHER for markdown and price-change events.**

Movements P publishes to the stock ledger:

| Movement | Trigger | Effect on ledger | Cost-method handling |
|---|---|---|---|
| **Price-change event** | Markdown execution, promo activation, list-price update | Revalues on-hand at new retail price; posts GL cost-complement adjustment (RIM) or cost-variance entry (Cost Method) | **RIM:** cost complement is recalculated; on-hand cost value changes. **Cost Method:** retail price changes; cost basis is unchanged (only on-hand value for margin tracking changes) |
| **Markdown event** | Seasonal markdown, clearance, loss-leader | Posts retail-price decrease; triggers GL markdown variance entry; may post shrink/loss reserve if needed | RIM: cost complement may increase (if markdown is taken late in period). Cost Method: GL tracks markdown variance separately from cost variance |
| **Promotion event** | Bundle, threshold, or conditional promo activation | Posts promotional discount to on-hand value (if promo is permanent; if time-bounded, no ledger posting until expiration) | Both methods: promo discounts are tracked separately from list-price changes; margin impact is visible via ledger discount fields |

Ledger reads P consumes:

- **Stock-on-hand (SOH) per item** — to calculate on-hand value impact of markdown
- **Movement history and sales velocity** — to calculate elasticity signals and inform future markdown timing
- **Cost-complement and cost-basis data** — to understand margin impact of markdown events

**Co-ownership of markdown governance** — P initiates markdown events; C (Commercial) approves (OTB impact check); F (Finance) posts GL entries and calculates markdown impact on GL gross margin.

**Perpetual-vs-period boundary.** Canary owns: markdown + price-change events that revalue ledger SOH. Merchant tool owns: price display at POS; long-term pricing strategy (merchant's commercial team). Default implementation route: `integrated-hybrid`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (data producers):

- Buyer input (markdown proposals, promotion rule authoring)
- C (Commercial) — item master, cost basis, department hierarchy for price rules
- S (Space, Range, Display) — planogram assignments to flag SEL re-compile needs
- Stock ledger — SOH and movement history for elasticity tracking and on-hand revaluation

**Downstream consumers** (data subscribers):

- **T (Transaction Pipeline)** — P rules are evaluated during POS receipt; promotion codes flow through T's transaction stream
- **C (Commercial)** — P publishes markdown events; C evaluates OTB impact (markdown reduces on-hand value, may free up OTB headroom)
- **F (Finance)** — P publishes price-change and markdown events; F posts GL entries for markdown variance and cost-complement adjustment
- **J (Forecast & Order)** — P's elasticity signals feed demand forecasting; elastic items should be replenished more frequently
- **S (Space, Range, Display)** — markdown events trigger S's SEL re-compile (new price on shelf-edge label)
- **Reporting/analytics dashboard** — margin analysis, elasticity trending, promotion ROI

## Agent surface

P exposes MCP tool families for buying and promotional workflows:

- **Promotion-rule authoring** — create/edit bundle, threshold, and conditional promotion rules; set timing and target audience
- **Markdown proposal workflow** — propose markdown with before/after pricing, estimated on-hand impact, margin impact; track approval status
- **Elasticity analysis** — query elasticity signals per item; identify candidates for future promotional optimization
- **Price-reconciliation auditing** — compare in-store vs. online vs. marketplace prices; flag discrepancies; route to buyer
- **Markdown calendar** — view and manage markdown schedule per department; plan seasonal clearance cadence
- **Promotion ROI tracking** — measure promo impact on sales, margin, and inventory turns; inform future promo strategy

## Security posture

- **Auth.** Promotion rule creation and markdown approval require `buyer`, `merchandiser`, or `promotions_manager` role. MCP tool-level role checking enforced.
- **Tenant scoping.** Every promotion rule and markdown record carries `merchant_id`; every read is row-level-secured.
- **Approval governance.** Markdown proposals require explicit approval from C (Commercial) before execution. Strict mode: rejected if over-budget; soft mode: flagged for manual override.
- **Price-change auditability.** Every price change is logged with `changed_by`, `changed_at`, `reason_code` (markdown / promo / list-price update), `before_price`, `after_price`. GL impact is traceable.
- **Channel-price consistency.** Price discrepancies across channels are flagged automatically; buyer is required to acknowledge or correct.

## Roadmap status

- **v3 (design)** — Promotion engine (bundle, threshold, conditional rules). Markdown lifecycle (proposal → approval → execution). Elasticity tracking. Price-reconciliation auditing. Read-only and restricted-write MCP tools for buyer workflows. GL cost-complement integration with F (Finance).
- **v3.1** — Advanced elasticity models (cross-item elasticity, category-level elasticity). Seasonal promotion planning calendars. Promotion ROI attribution (per-promo margin impact).
- **v3.2** — Autonomous markdown optimization (AI-driven markdown timing recommendations based on elasticity and inventory position).
- **v3.3** — Dynamic pricing support (minute-by-minute price updates based on demand signals and inventory age).

## Open questions

1. **Promotion scope and channel** — Are promotions applied at the item level, category level, or customer level? Do promotions apply in-store only, or across all channels (online, marketplace, app)?
2. **Time-bounded vs. permanent markdown** — Should a markdown be treated as a temporary promotion (expires at end date, price reverts) or permanent (executed once, does not revert)? RIM cost-complement handling differs.
3. **GL markdown-variance account structure** — Should markdown variance be one account or split by reason (seasonal vs. loss-leader vs. clearance)? Who owns account allocation — P or F?
4. **Price override per location** — Can individual stores override regional prices (e.g., local markdown for specific location), or is pricing uniform across all locations? Per-merchant policy?
5. **Elasticity feedback loop to J (Forecast).** Should J (Forecast & Order) automatically adjust replenishment based on elasticity signals, or should elasticity be informational only? How granular (per-item vs. per-category)?

## Related

- [[../platform/stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]]
- [[../platform/retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]]
- [[../platform/spine-13-prefix|The Canary Retail Spine — 13 Modules]]
- [[C-commercial|C (Commercial)]]
- [[D-distribution|D (Distribution)]]
- [[F-finance|F (Finance)]]
- [[J-forecast-order|J (Forecast & Order)]]
- [[S-space-range-display|S (Space, Range, Display)]]
- [[L-labor-workforce|L (Labor & Workforce)]]
- [[W-work-execution|W (Work Execution)]]

## Sources

- [[../../GrowDirect/Brain/wiki/retek-rms-perpetual-inventory|Retek RMS — Perpetual-Inventory Movement Ledger (markdown and cost-complement handling)]]
- [[../../GrowDirect/Brain/wiki/secure-merchandising-rfp-evant-response-2003|Merchandising System RFP — Evant Response (promotion engine reference)]]
- [[../platform/retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy (markdown impact on cost complement)]]

---

*Classification: confidential. Owner: GrowDirect LLC. Created 2026-04-24. P (Pricing & Promotion) is a v3 module spec within the Canary Retail Spine. It is design-stage; implementation is deferred pending v2 ring (C/D/F/J) stabilization.*

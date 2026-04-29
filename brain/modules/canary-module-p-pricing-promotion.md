---
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-p, pricing, promotion, markdown, elasticity, v3]
sources:
  - Canary-Retail-Brain/modules/P-pricing-promotion.md
  - Canary-Retail-Brain/platform/stock-ledger.md
  - Canary-Retail-Brain/platform/retail-accounting-method.md
last-compiled: 2026-04-24
----

# Canary Module — P (Pricing & Promotion)

## Summary

P (Pricing & Promotion) owns the promotion engine, markdown management, elasticity tracking, and multi-channel price reconciliation. **v3 design — implementation deferred.** This wiki article is the Canary-specific crosswalk for the v3 P module. The canonical, vendor-neutral module spec lives at `Canary-Retail-Brain/modules/P-pricing-promotion.md`.

P extends the promo-code dimension that v1 T (Transaction Pipeline) inherits from Square into a full promotion engine. Every markdown posted to the ledger revalues on-hand inventory and drives GL accounting. Elasticity signals inform future markdown timing and category optimization.

## Code surface

| Concern | File | Status | Notes |
|---|---|---|---|
| Promotion rule schema | `Canary/canary/models/app/promotions.py` (projected) | no code yet | Promotion rule types: bundle, threshold, conditional; timing and target scope |
| Markdown lifecycle | `Canary/canary/models/app/markdowns.py` (projected) | no code yet | Markdown proposals, approval workflow, execution, GL impact tracking |
| Elasticity tracking | `Canary/canary/services/pricing/elasticity_calculator.py` (projected) | no code yet | Measures demand elasticity per item per period; inputs to forecasting |
| Price-reconciliation auditor | `Canary/canary/services/pricing/price_auditor.py` (projected) | no code yet | Compares in-store, online, marketplace prices; flags discrepancies |
| GL integration | `Canary/canary/services/pricing/gl_poster.py` (projected) | no code yet | Posts markdown variance and cost-complement adjustments to GL (with F module) |
| MCP tools | `Canary/canary/blueprints/pricing_mcp.py` (projected) | no code yet | Tools: promo-authoring, markdown-proposal, elasticity-analysis, price-reconciliation, markdown-calendar, promo-roi |
| Configuration | `Canary/config.py` extensions (projected) | no code yet | Would add `PROMOTION_ENGINE_MODE` (basic/advanced), `MARKDOWN_APPROVAL_REQUIRED` (yes/no), `PRICE_RECONCILIATION_TOLERANCE_PCT` |

## Schema crosswalk

P would write to the `app` schema (configuration and master data). Anticipated tables:

| Table | Owner | Purpose |
|---|---|---|
| `promotions` | P | Promotion rules: id, merchant_id, rule_type (bundle/threshold/conditional), condition_def, discount_def, start_date, end_date, status |
| `promotion_items` | P | Items included in promotion: id, promotion_id, item_id, discount_amount or bundle_config |
| `markdowns` | P | Markdown records: id, item_id, location_id, old_price_cents, new_price_cents, markdown_date, reason_code, proposal_date, approved_date, approved_by |
| `markdown_approvals` | P | Approval workflow: id, markdown_id, approver_id, approval_date, status (proposed/approved/rejected), margin_impact_cents, otb_impact_cents |
| `elasticity_signals` | P | Elasticity tracking: id, item_id, period, price_change_pct, demand_change_pct, elasticity_coefficient |
| `price_discrepancies` | P | Multi-channel price auditing: id, item_id, in_store_price_cents, online_price_cents, marketplace_price_cents, discrepancy_amount, flag_date, status |
| `markdown_gl_posting` | P | GL ledger bridge: id, markdown_id, gl_account, amount_cents, posting_date, cost_complement_adjustment_flag |

P reads from (no write):

| Table | Owner | Why |
|---|---|---|
| `stock_ledger.movements` (projected) | D | P calculates on-hand revaluation for markdown impact |
| `sales.transactions` | T | P calculates elasticity (price change vs. sales impact) |
| `items` | C | P looks up item attributes when authoring promotions |

## SDD crosswalk

No v3 SDDs exist yet for P. Canary's current SDDs only cover v1 modules (T, Q, architecture, data-model) and projected v2 modules (C, D, F, J).

Projected SDD structure (future):
- `Canary/docs/sdds/v3/pricing-promotion.md` — promotion rule types and mechanics, markdown lifecycle, elasticity calculation, GL posting integration
- Section: Ledger relationship (publisher role, markdown events, cost-complement adjustment logic)
- Section: Integration with C (item master), F (GL posting), J (elasticity signals to forecast), S (SEL re-compile on price change)

## Where this module fits on the spine

| Axis | Cell | Notes |
|---|---|---|
| [[../projects/RetailSpine\|Retail Spine]] | v3 Commercial + Financial | P is part of the v3 full-spine ring alongside S, L, W |
| [[../projects/RetailSpine\|Retail Spine]] Ledger roles | Publisher (markdown/price-change events) | P publishes events; F/D co-post GL entries and ledger movements |
| Cost-method impact | RIM: markdown → recalc cost complement → revalue on-hand; Cost Method: markdown → GL variance, no cost-basis change | |
| Upstream feeder | P reads C's item master + ledger movements to understand on-hand impact | |
| Downstream consumer | F reads P's markdown events for GL posting; J reads P's elasticity signals for forecast; S reads P's price changes for SEL re-compile | |

## Open Canary-specific questions

1. **Promotion scope.** Should promotions be defined at the item level, category level, or customer level? Hybrid? Current assumption: item-level at v3; customer-level at v3.2.
2. **Multi-channel price parity.** Does Canary need to enforce price parity across in-store, online, and third-party marketplace (if merchant uses one)? Or is it informational only? Current assumption: informational with flagging at v3; enforcement deferred.
3. **Markdown proposal approval.** Should markdown require explicit buyer approval before execution, or is proposal-to-execution automatic? Current assumption: approval required (soft mode: C checks OTB; hard mode: automatic rejection if over-budget).
4. **Elasticity feedback to J (Forecast).** Should J automatically adjust replenishment based on elasticity, or is elasticity informational? Current assumption: informational at v3; automated feedback at v3.2.
5. **Time-bounded vs. permanent markdown.** Should markdown reversal be supported (price goes back up after end date), or are markdowns one-way (permanent)? RIM cost-complement handling differs. Current assumption: permanent at v3; time-bounded at v3.1.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-module-c-commercial|C (Commercial)]]
- [[canary-module-d-distribution|D (Distribution)]]
- [[canary-module-f-finance|F (Finance)]]
- [[canary-module-j-forecast-order|J (Forecast & Order)]]
- [[canary-module-s-space-range-display|S (Space, Range, Display)]]
- [[canary-module-l-labor-workforce|L (Labor & Workforce)]]
- [[canary-module-w-work-execution|W (Work Execution)]]
- [[../platform/RetailSpine|Retail Spine — Ledger relationships]]
- [[../platform/stock-ledger|Stock Ledger — Perpetual-Inventory Movement Ledger]]
- [[../platform/retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]]

## Sources

- `Canary-Retail-Brain/modules/P-pricing-promotion.md` — canonical module spec
- `Canary-Retail-Brain/platform/stock-ledger.md` — ledger movement patterns
- `Canary-Retail-Brain/platform/retail-accounting-method.md` — RIM cost-complement logic

---

**Status:** Canary module P is design-phase. No code yet. Ready for SDD drafting and schema design when v3 development cycle begins. Expected integration points: C (item master), F (GL posting), J (elasticity signals), S (SEL re-compile).

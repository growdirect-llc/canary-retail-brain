---
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-j, forecast, replenishment, ordering, v2]
sources:
  - Canary-Retail-Brain/modules/J-forecast-order.md
  - Canary-Retail-Brain/platform/stock-ledger.md
  - Canary-Retail-Brain/platform/retail-accounting-method.md
last-compiled: 2026-04-24
----

# Canary Module — J (Forecast & Order)

## Summary

J (Forecast & Order) owns demand forecasting, replenishment-point calculation, and automated purchase-order recommendation. **Design-only at this point — no Canary code yet.** This wiki article is the Canary-specific crosswalk for the v2 J module. The canonical spec lives at `Canary-Retail-Brain/modules/J-forecast-order.md`.

J completes the buying triangle: C owns the catalog and OTB budget; F owns the financial close and cost method; J owns the demand signal and replenishment trigger. Together, C+F+J implement automated, demand-driven ordering constrained by budget.

## Code surface

| Concern | File | Status | Notes |
|---|---|---|---|
| Demand forecaster | `Canary/canary/services/forecast/demand_forecaster.py` (projected) | no code yet | Would read movement history (sales, receipts, RTVs, adjustments); calculate demand velocity + variance; produce 13-week rolling forecast |
| Replenishment calculator | `Canary/canary/services/forecast/replenishment_params.py` (projected) | no code yet | Would calculate ROP (reorder point), EOQ (economic order qty), safety stock per item per location based on demand variance and supplier lead time |
| PO recommender | `Canary/canary/services/forecast/po_recommender.py` (projected) | no code yet | Would check if SOH + on-order < ROP; generate PO recommendation with qty (EOQ-based), supplier, requested receipt date |
| OTB validator | `Canary/canary/services/forecast/otb_validator.py` (projected) | no code yet | Would query C for available OTB headroom before recommending PO; include headroom check result in recommendation |
| Forecast analyzer | `Canary/canary/services/forecast/accuracy.py` (projected) | no code yet | Would compare prior forecasts to actual results; calculate MAPE (mean absolute percentage error); identify bias |
| MCP tools | `Canary/canary/blueprints/forecast_mcp.py` (projected) | no code yet | Tools: view-forecast, view-replenishment-params, view-po-recommendations, approve-recommendation, replan-scenario, forecast-accuracy-audit, replenishment-dashboard |
| Configuration | `Canary/config.py` extensions (projected) | no code yet | Would add per-item lead-time, per-category EOQ/ROP overrides, forecast-refresh cadence, recommendation-approval threshold |

## Schema crosswalk

J would write to the `metrics` schema (forecasts and parameters are reporting, not operational master data). Anticipated tables:

| Table | Owner | Purpose |
|---|---|---|
| `demand_forecasts` | J | id, merchant_id, item_id, location_id, forecast_date (snapshot of when forecast was calculated), week_ending_date, forecast_qty_units, low_scenario_qty, high_scenario_qty, velocity_units_per_day, variance_pct |
| `replenishment_params` | J | id, merchant_id, item_id, location_id, rop_units (reorder point), eoq_units (economic order qty), safety_stock_units, lead_time_days, demand_variability_flag (stable/variable/volatile), last_calc_date |
| `po_recommendations` | J | id, merchant_id, item_id, location_id, recommended_qty_units, supplier_id, requested_receipt_date, priority (by how-far-below-ROP), otb_headroom_validated (bool), otb_headroom_available_cents (if RIM) or _cost (if Cost Method), status (pending/approved/rejected/converted-to-po), created_at, approved_at |
| `forecast_results` | J | id, merchant_id, item_id, location_id, period_start, forecast_qty_units (from prior period), actual_qty_units, mape_pct (mean absolute percentage error), bias_pct (consistent over/under forecast?) |

J reads from (no write):

| Table | Owner | Why |
|---|---|---|
| `sales.stock_movements` (from D) | D | J reads all movements to derive demand and validate forecast assumptions |
| `sales.transactions` (from T) | T | J reads sales transactions to extract velocity and seasonal patterns |
| `app.items` (via C) | C | J reads supplier, lead_time_days, item hierarchy |
| `app.otb_budgets` (via C) | C | J queries available OTB headroom before recommending PO |
| `app.purchase_orders` (via F) | F | J reads on-order quantities to calculate projected on-hand (SOH + on-order) |

## SDD crosswalk

No v2 SDDs exist yet for J. Projected SDD structure:
- `Canary/docs/sdds/v2/forecast.md` — demand forecasting algorithm (velocity + variance), ROP/EOQ/safety-stock calculation, PO-recommendation workflow, OTB headroom check, forecast-accuracy metrics
- Section: Ledger relationship (J reads movement history; J doesn't publish to ledger directly, but recommendations become D/F movements)
- Section: Integration with C (item master, OTB), F (on-order visibility, cost-method for ROP calculation), D (receipt matching for forecast validation)

## Where this module fits on the spine

| Axis | Cell | Notes |
|---|---|---|
| [[../projects/RetailSpine\|Retail Spine]] | v2 Forecast & Order | J is part of CRDM expansion ring alongside C, D, F |
| [[../projects/RetailSpine\|Retail Spine]] Ledger roles | Subscriber + Publisher (indirectly) | J reads ledger history; recommendations become F POs → D receipts |
| Replenishment workflow | Read history → forecast → calc params → recommend PO → await approval | J orchestrates automated ordering pipeline |
| Upstream deps | D (movement history), C (item master, OTB), F (on-order) | J cannot forecast without these |
| Downstream consumers | F (PO approval), D (receipt matching), C (OTB consumption tracking) | J's recommendations feed the buying triangle |

## Open Canary-specific questions

1. **Forecast granularity.** Should forecast be at SKU level, SKU+location level, or both? Current assumption: both, with location-level overrides possible (e.g., a slow-moving item can be ordered less frequently at a small store).
2. **Seasonal decomposition.** Should J detect and forecast seasonal patterns (e.g., higher demand in Q4), or is demand assumed to be stationary? Current assumption: stationary at v2; seasonal modeling deferred to v2.1.
3. **Lead-time variability.** If supplier lead time is 5–10 days (variable), should J use worst-case (10d) for safety-stock calculation? Current assumption: use average; document that suppliers with high variability may need higher safety stock.
4. **Auto-commit threshold.** Should J auto-commit PO recommendations below a certain amount (e.g., auto-commit orders <$50 without buyer approval), or require explicit approval for all? Current assumption: all recommendations require explicit approval; merchant can configure override threshold.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-module-c-commercial|C (Commercial)]]
- [[canary-module-d-distribution|D (Distribution)]]
- [[canary-module-f-finance|F (Finance)]]
- [[../platform/RetailSpine|Retail Spine — Ledger relationships]]
- [[../platform/stock-ledger|Stock Ledger — Perpetual-Inventory Movement Ledger]]
- [[../platform/retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]]
- [[katz-scm-2003-archetype|Katz SCM 2003 Archetype]] — demand forecasting patterns reference

## Sources

- `Canary-Retail-Brain/modules/J-forecast-order.md` — canonical module spec
- `Canary-Retail-Brain/platform/stock-ledger.md` — ledger movement history patterns
- `Canary/docs/sdds/v2/data-model.md` — projected schema overview (not yet written)

---

**Status:** Canary module J is design-phase. No code yet. Ready for SDD drafting and schema design when v2 dev cycle begins. J is the final piece of the C+D+F+J buying triangle.

---
card-type: domain-module
card-id: retail-replenishment-model
card-version: 2
domain: merchandising
layer: domain
status: approved
feeds: [retail-purchase-order-model]
receives: [retail-demand-forecasting, retail-merchandise-financial-planning, retail-site-management]
tags: [replenishment, SOQ, suggested-order-quantity, safety-stock, DC, store-replenishment, order-type]
last-compiled: 2026-04-29
---

## What this is

The retail replenishment model: how suggested order quantities (SOQs) are calculated, the replenishment methods available, the parameter structure that governs item-site replenishment behavior, and the split between DC replenishment and direct-to-store replenishment.

## Purpose

Replenishment exists to maintain a continuous flow of product through the supply chain — the right product in the right amount at the right place at the right time. Without a disciplined replenishment model, buyers order manually based on instinct, resulting in both excess inventory on some items and stockouts on others. The replenishment model converts demand forecasts into purchase recommendations that optimize inventory investment against service level targets.

## Structure

**Replenishment parameters** — Parameters are maintained at the item × site level. Key parameters:

| Parameter | What it governs |
|-----------|----------------|
| Replenishment method | Demand-based, inventory-based, or order-up-to |
| Order cycle | How frequently orders are generated (daily, weekly) |
| Review period | Days between replenishment reviews |
| Safety stock | Buffer inventory maintained to protect against demand variability and lead time variability |
| Minimum order quantity | Vendor-specified minimum per order line, in eaches |
| Rounding requirements | Order quantities rounded to inner pack, case, or layer |
| Lead time | Days from PO creation to expected receipt |
| Seasons and phases | Active date ranges within which replenishment parameters are valid |
| Source | Primary source (vendor or DC), with secondary source fallback |

**Replenishment methods:**

- **Demand-based** — SOQ is calculated to cover forecasted demand over the review period plus safety stock, minus current on-hand and on-order. Requires an accurate demand forecast as the primary input.
- **Inventory-based** — SOQ is triggered when on-hand falls below a defined reorder point. Reorder point = safety stock + expected demand during lead time. Simpler than demand-based but less accurate in volatile demand environments.
- **Order-up-to** — SOQ brings on-hand quantity (including on-order) up to a maximum target level. Target = demand over review period + lead time + safety stock. Best for items with very stable demand and fixed order cycles.

**SOQ calculation flow** — For demand-based replenishment: (1) read current on-hand per item-site; (2) read open purchase orders not yet received; (3) read approved demand forecast for the order horizon; (4) calculate net need = forecast demand − (on-hand + on-order − safety stock); (5) apply rounding to inner pack or case; (6) apply minimum order quantity; (7) present as suggested order quantity for buyer review.

**DC vs. direct-store replenishment** — Store replenishment is based on the store-level sales forecast. DC replenishment is based on an aggregated sales forecast across all stores the DC services, plus presentation quantity minimums per item per location. A single PO may cover multiple store delivery locations, enabling truck building across stores served by the same vendor. Direct store delivery (DSD) bypasses the DC: vendor trucks deliver directly to stores on a defined route schedule.

**Exception management** — Not every SOQ requires buyer review. Exception-based workflows surface only: items where the SOQ deviates significantly from the prior order, items approaching a stockout faster than expected, items with open orders past their ship-not-after date, and items whose calculated SOQ would exceed OTB. The buyer reviews exceptions; the rest auto-convert to purchase orders or requisitions.

**Simulation** — Replenishment simulation generates SOQs without creating actual orders. Used for testing parameter changes, modeling the impact of promotional events on order requirements, and validating replenishment schedules before go-live.

## Consumers

The Replenishment module generates the SOQ list and presents it for buyer review or auto-approval based on exception rules. The PO Management module converts approved SOQs into purchase orders. The Merchandise Financial Planning process reads expected order volumes to validate OTB utilization. The Operations Agent monitors replenishment fill rate (% of SOQs that resulted in on-time delivery) and safety stock sufficiency (% of stockout events that occurred despite safety stock being in place).

## Invariants

- DC replenishment is driven by aggregated store forecasts — not by DC consumption history alone. Using DC consumption history without store-level visibility misses demand signal and creates artificial demand smoothing.
- Minimum order quantities and rounding rules must be applied after the net need calculation, not before. Applying them before distorts the underlying demand signal.
- Replenishment simulation must not affect production on-hand or on-order balances. Simulations are planning tools only.

## Platform (2030)

**Agent mandate:** Operations Agent owns replenishment execution for non-exception items — SOQ generation, auto-approval within OTB, and exception surfacing. Business Agent reviews replenishment exceptions and adjusts parameters. The goal is to reduce the human decision surface to only the cases that genuinely require judgment; everything within parameters runs automatically.

**Auto-replenishment within L402 OTB.** Traditional replenishment requires buyer review of every SOQ. In Canary Go, SOQs that are within OTB (L402 wallet balance check) and within configured exception bounds auto-convert to purchase orders without buyer review. The buyer's attention is reserved for exceptions: SOQs that exceed OTB, items where the SOQ deviates significantly from prior orders, items approaching stockout faster than the model anticipated, and new items without established parameters. The goal is to remove human review from the 80% of replenishment decisions that are routine.

**Real-time OTB feedback loop.** As SOQs auto-convert to POs, the L402 OTB wallet balance decrements in real time. Business Agent monitoring OTB balance can see the replenishment pipeline consuming OTB as it runs — not at end of day. If auto-replenishment is consuming OTB faster than expected (demand running above forecast), Business Agent surfaces this before the wallet is exhausted and replenishment is blocked, rather than discovering the blockage after the fact.

**MCP surface.** `replenishment_exceptions(buyer_id)` returns SOQs requiring human review with reason code. `soq(sku, site)` returns the current suggested order quantity and calculation basis. `replenishment_pipeline(dept, period)` returns all auto-approved orders in flight with OTB impact. `safety_stock_health(dept)` returns items where safety stock is below minimum — stockout risk signal.

**RaaS.** Replenishment order creation is a sequenced event that must follow OTB wallet confirmation — a PO generated before the OTB decrement is confirmed creates a double-spend risk. `soq(sku, site)` is the highest-volume MCP call in the platform: at 10K active SKUs × 100 sites, the replenishment cycle generates ~1M calls; must resolve from Valkey hot cache in sub-50ms. `replenishment_exceptions(buyer_id)` from SQL indexed on (buyer_id, exception_type, created_at) — the buyer dashboard must not trigger a full-scan. Replenishment order records append-only. Replenishment pipeline data exportable for vendor collaboration and supply chain audit.

## Related

- [[retail-demand-forecasting]] — the forecast input that drives demand-based SOQ calculation
- [[retail-purchase-order-model]] — the downstream process that converts approved SOQs into purchase commitments
- [[retail-merchandise-financial-planning]] — OTB constrains replenishment order volume
- [[retail-site-management]] — site configuration (DC assignments, delivery schedules) governs replenishment routing

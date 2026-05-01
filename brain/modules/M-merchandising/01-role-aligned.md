---
title: C — Role Alignment
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-m, commercial, items, otb, suppliers, v2]
sources:
  - Canary-Retail-Brain/modules/M-merchandising.md
  - Canary-Retail-Brain/platform/retail-accounting-method.md
  - Canary-Retail-Brain/platform/stock-ledger.md
last-compiled: 2026-04-24
----

# Canary Module — C (Commercial)

## Summary

C (Commercial) owns the item catalog, merchandising hierarchy, supplier relationships, and Open-to-Buy allocation. **Design-only at this point — no Canary code yet.** This wiki article is the Canary-specific crosswalk for the v2 C module. The canonical, vendor-neutral module spec lives at `Canary-Retail-Brain/modules/M-merchandising.md`.

C is a v2 module that closes the merchandising gap left by v1. Once T (Transaction Pipeline) is shipping, the next retailer ask is almost always "can you handle our buying and inventory?" C answers that by owning the item master, department hierarchy, supplier catalog, and OTB enforcement at the buyer level.

## Code surface

| Concern | File | Status | Notes |
|---|---|---|---|
| Item master schema | `Canary/canary/models/app/items.py` (projected) | no code yet | Would inherit from `AppBase`; fields: sku, upc, description, cost_method, cost_basis, retail_price, supplier_id, hierarchy |
| Department hierarchy | `Canary/canary/models/app/departments.py` (projected) | no code yet | Would carry division → department → class → subclass tree with cost-method designation per node |
| Supplier master | `Canary/canary/models/app/suppliers.py` (projected) | no code yet | Would carry vendor_name, payment_terms, invoice_tolerance_pct, lead_time_days, performance_sla |
| OTB calculation | `Canary/canary/services/commercial/otb.py` (projected) | no code yet | Would implement formula: OTB = Planned EOH + Planned Receipts + Planned Markdowns − Planned Sales − Current SOH |
| Cost-update events | `Canary/canary/services/commercial/cost_updates.py` (projected) | no code yet | Would publish cost-variance movements to stock ledger when landed cost changes |
| MCP tools | `Canary/canary/blueprints/commercial_mcp.py` (projected) | no code yet | Tools: item-lookup, otb-headroom, cost-audit, supplier-perf, assortment-check, otb-replan |
| Configuration | `Canary/config.py` extensions (projected) | no code yet | Would add `COST_METHOD_BY_DEPARTMENT` mapping, `OTB_ENFORCEMENT_MODE` (strict/soft), `OTB_CURRENCY` (retail/cost) |

## Schema crosswalk

C would write to the `app` schema (configuration and master data, not transactional). Anticipated tables:

| Table | Owner | Purpose |
|---|---|---|
| `items` | C | One row per SKU per merchant; fields: sku, upc, item_name, cost_method, cost_basis_cents, retail_price_cents, supplier_id, hierarchy_path, active_flag |
| `departments` | C | Hierarchy tree: id, parent_id, dept_name, level (division/dept/class/subclass), cost_method |
| `suppliers` | C | Vendor master: id, supplier_name, payment_terms, invoice_tolerance_pct, lead_time_days |
| `item_suppliers` | C | Junction: item_id, supplier_id, supplier_sku, supplier_cost_cents, min_order_qty |
| `otb_budgets` | C | Buyer level: id, merchant_id, buyer_id, department_id, period, otb_retail_cents (if RIM) or otb_cost_cents (if Cost Method), consumed_amount, remaining_headroom |
| `cost_update_events` | C | Audit trail: id, item_id, reason (supplier-price-change / variance-resolution / tariff), old_cost_cents, new_cost_cents, effective_date, posted_by |

C reads from (no write):

| Table | Owner | Why |
|---|---|---|
| `sales.transactions` (via D stream) | T | C tracks sales velocity per item per location to validate OTB forecast assumptions |
| `sales.inventory_movements` (projected) | D | C reads receipt velocity to validate OTB consumption and replenishment headroom |

## SDD crosswalk

No v2 SDDs exist yet for C. Canary's current SDDs only cover v1 modules (T, Q, architecture, data-model). C's SDD would be drafted after this wiki article is validated.

Projected SDD structure (future):
- `Canary/docs/sdds/v2/commercial.md` — item master schema, department hierarchy design, supplier catalog, OTB calculation and enforcement, cost-method designation
- Section: Ledger relationship (cost-update events, OTB co-ownership with F/J)
- Section: OTB integration with D/F/J (D checks C before posting receipts; F validates cost-method; J reads OTB headroom)

## Where this module fits on the spine

| Axis | Cell | Notes |
|---|---|---|
| [[../projects/RetailSpine\|Retail Spine]] | v2 Commercial-Financial | C is part of the CRDM expansion ring alongside D, F, J |
| [[../projects/RetailSpine\|Retail Spine]] Ledger roles | Publisher (cost-update) + Co-analyst (OTB) | C publishes cost-update events; C and F and J collaborate on OTB |
| Upstream feeder | C reads sales history (T) and receipt history (D) to validate forecasts | |
| Downstream consumer | D reads C's item master before posting receipts; F reads C's cost-method designation for period close; J reads C's supplier/lead-time data to generate PO recommendations | |

## Open Canary-specific questions

1. **Item-master multitenancy.** Should item records be merchant-specific (isolated per merchant), or could GrowDirect support a "shared item catalog" model where multiple merchants reference the same SKU master (with merchant-specific pricing/supplier overlays)? Current assumption: merchant-specific at v2.
2. **Supplier master scope.** Does the supplier master include only transactional vendors (suppliers of inventory), or also service vendors (freight, 3PL, consulting)? Current assumption: transactional vendors only at v2.
3. **Cost-method schema implications.** Do RIM-method items and Cost-Method items live in the same `items` table, or separate tables? Current assumption: same table, with cost_method column, and cost_basis is null for RIM items (cost is derived at period close).
4. **OTB currency flexibility.** Should a merchant be able to set OTB per department (RIM depts in retail dollars, Cost-Method depts in cost dollars), or must OTB currency be uniform across the merchant? Current assumption: uniform per merchant, configurable at merchant setup.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-module-d-distribution|D (Distribution)]]
- [[canary-module-f-finance|F (Finance)]]
- [[canary-module-o-orders|J (Orders)]]
- [[../platform/RetailSpine|Retail Spine — Ledger relationships]]
- [[../platform/stock-ledger|Stock Ledger — Perpetual-Inventory Movement Ledger]]
- [[../platform/retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]]

## Sources

- `Canary-Retail-Brain/modules/M-merchandising.md` — canonical module spec
- `Canary/docs/sdds/v2/data-model.md` — projected schema overview (placeholder; not yet written)

---

**Status:** Canary module M is design-phase. No code yet. Ready for SDD drafting and schema design when v2 development cycle begins. Expected integration points: D (receipt validation), F (cost-method), J (OTB headroom).

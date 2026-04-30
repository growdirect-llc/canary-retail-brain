---
title: F — Role Alignment
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-f, finance, invoices, period-close, accounting, v2]
sources:
  - Canary-Retail-Brain/modules/F-finance.md
  - Canary-Retail-Brain/platform/retail-accounting-method.md
  - Canary-Retail-Brain/platform/stock-ledger.md
last-compiled: 2026-04-24
----

# Canary Module — F (Finance)

## Summary

F (Finance) owns purchase orders, supplier invoices, invoice-to-receipt reconciliation (three-way match), period-close GL posting, and the cost-method choice (RIM vs Cost Method) that cascades through the entire retail platform. **Design-only at this point — no Canary code yet.** This wiki article is the Canary-specific crosswalk for the v2 F module. The canonical spec lives at `Canary-Retail-Brain/modules/F-finance.md`.

F is the reconciler that ensures ledger state agrees with supplier truth and that period-close financial statements are accurate. It is also a co-owner (with C and J) of Open-to-Buy calculation.

## Code surface

| Concern | File | Status | Notes |
|---|---|---|---|
| PO lifecycle | `Canary/canary/services/finance/purchase_orders.py` (projected) | no code yet | Would manage PO creation, approval, commitment, release stages |
| Invoice service | `Canary/canary/services/finance/invoices.py` (projected) | no code yet | Would ingest supplier invoices, perform 3-way match (PO↔receipt↔invoice) |
| Three-way matcher | `Canary/canary/services/finance/three_way_match.py` (projected) | no code yet | Would compare PO cost vs receipt cost vs invoice cost; flag variances; auto-resolve within tolerance |
| Cost-variance handler | `Canary/canary/services/finance/cost_variances.py` (projected) | no code yet | Would publish cost-variance movements to ledger when invoice doesn't match receipt |
| Period-close engine | `Canary/canary/services/finance/period_close.py` (projected) | no code yet | Would aggregate all movements for period, apply cost-method (RIM or Cost), calculate COGS, post GL entries |
| GL posting | `Canary/canary/services/finance/gl_posting.py` (projected) | no code yet | Would generate GL entry payloads (debit/credit tuples) and publish to general-ledger sink |
| MCP tools | `Canary/canary/blueprints/finance_mcp.py` (projected) | no code yet | Tools: create-po, commit-po, ingest-invoice, view-match-status, approve-variance, period-close-dashboard, margin-reporting |
| Configuration | `Canary/config.py` extensions (projected) | no code yet | Would add per-department cost-method designation, invoice-variance tolerance thresholds, GL account mapping, period-close cadence |

## Schema crosswalk

F would write to the `app` and `metrics` schemas. Anticipated tables:

**app schema (configuration and master):**

| Table | Owner | Purpose |
|---|---|---|
| `purchase_orders` | F | id, merchant_id, buyer_id, item_id, supplier_id, qty_units, cost_cents_per_unit, total_cost_cents, requested_receipt_date, status (drafted/approved/committed/received/closed), created_at, approved_at |
| `invoices` | F | id, merchant_id, supplier_id, invoice_number, invoice_date, total_amount_cents, match_status (unmatched/matched/variance/disputed), received_at |
| `invoice_line_items` | F | id, invoice_id, item_id, qty_units, unit_cost_cents, total_cost_cents |
| `cost_variances` | F | id, merchant_id, po_id, receipt_id, invoice_id, variance_type (qty/cost/both), variance_amount_cents, tolerance_exceeded (bool), resolved (bool), resolution_note, posted_at |
| `department_cost_methods` | F | id, merchant_id, dept_id, cost_method (RIM/Cost), effective_date |
| `gl_posting_templates` | F | id, merchant_id, movement_type, dr_account, cr_account, narrative_template (for audit trail) |

**metrics schema (reporting):**

| Table | Owner | Purpose |
|---|---|---|
| `period_close_results` | F | id, merchant_id, period_end_date, cogs_cents, inventory_value_cents, margin_cents, margin_pct, shrink_attributed_cents, gl_posted (bool), posted_at |
| `margin_by_dept` | F | id, merchant_id, period_end_date, dept_id, sales_cents, cogs_cents, margin_cents, margin_pct |
| `margin_by_item` | F | id, merchant_id, period_end_date, item_id, qty_sold, sales_cents, cogs_cents, margin_cents, margin_pct |

F reads from (no write):

| Table | Owner | Why |
|---|---|---|
| `app.items` (via C) | C | F reads cost-method designation per item |
| `app.departments` (via C) | C | F reads cost-method per department to apply correct period-close calculation |
| `sales.stock_movements` (projected, from D) | D | F reads all movements for the period to calculate COGS and period-close GL entries |
| `app.suppliers` (via C) | C | F resolves supplier info for invoice matching |

## SDD crosswalk

No v2 SDDs exist yet for F. Projected SDD structure:
- `Canary/docs/sdds/v2/finance.md` — PO/invoice lifecycle, three-way-match algorithm, cost-variance tolerance policy, RIM cost-complement calculation, Cost-Method cost-flow assumption, period-close workflow, GL posting contract
- Section: Ledger relationship (F as reconciler; cost-variance events; GL posting at period close)
- Section: Integration with C (cost-method designation), D (receipt validation), J (OTB co-ownership)

## Where this module fits on the spine

| Axis | Cell | Notes |
|---|---|---|
| [[../projects/RetailSpine\|Retail Spine]] | v2 Finance | F is part of CRDM expansion ring alongside C, D, J |
| [[../projects/RetailSpine\|Retail Spine]] Ledger roles | Reconciler + Publisher | F reconciles against external truth (invoices); publishes cost-variance and GL-posting movements |
| Financial close workflow | Aggregates ledger → calculates COGS → applies cost-method → posts GL | F orchestrates month-end accounting |
| Upstream deps | D (receipts), C (cost-method), T (sales via Q) | F cannot close without these |
| Downstream consumers | Merchant accounting/finance system (GL entries) | F's GL posting feeds financial statements |

## Open Canary-specific questions

1. **Cost-method change policy.** If a department switches cost method mid-period, how are COGS and margin calculated? Blended? Split per sub-period? Current assumption: not supported at v2; cost-method is locked per period.
2. **Invoice variance escalation.** If variance exceeds tolerance, what's the escalation path? F flags for finance-manager approval before GL posting? Or post tentatively and reverse if supplier disputes? Current assumption: flag and hold pending approval.
3. **Multi-currency invoicing.** If supplier invoices in EUR but merchant GL is USD, does F convert at invoice-date rate or posting-date rate? Who handles FX variance? Current assumption: F assumes all invoices are in merchant's reporting currency; FX conversion is pre-invoice (supplier or payment processor).
4. **Satoshi cost extension.** Should F extend cost ledger to [[../platform/satoshi-cost-accounting|satoshi-level cost accounting]] for sub-cent metered costs (agent tooling, shipping micropayments)? Phase 2 or defer? Current assumption: Phase 2, after v2 ships.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-module-c-commercial|C (Commercial)]]
- [[canary-module-d-distribution|D (Distribution)]]
- [[canary-module-j-forecast-order|J (Forecast & Order)]]
- [[../platform/RetailSpine|Retail Spine — Ledger relationships]]
- [[../platform/stock-ledger|Stock Ledger — Perpetual-Inventory Movement Ledger]]
- [[../platform/retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]]
- [[../platform/satoshi-cost-accounting|Satoshi-Level Cost Accounting]] — future cost-extension reference

## Sources

- `Canary-Retail-Brain/modules/F-finance.md` — canonical module spec
- `Canary-Retail-Brain/platform/retail-accounting-method.md` — RIM vs Cost Method decision matrix
- `Canary/docs/sdds/v2/data-model.md` — projected schema overview (not yet written)

---

**Status:** Canary module F is design-phase. No code yet. Ready for SDD drafting and schema design when v2 dev cycle begins. F is a critical path item because it owns cost-method designation and period-close.

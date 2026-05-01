---
title: D — Role Alignment
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-d, distribution, inventory-movement, receipts, transfers, v2]
sources:
  - Canary-Retail-Brain/modules/D-distribution.md
  - Canary-Retail-Brain/platform/stock-ledger.md
  - Canary-Retail-Brain/platform/crdm.md
last-compiled: 2026-04-24
----

# Canary Module — D (Distribution)

## Summary

D (Distribution) owns inventory movement across the retail organization: receipts from suppliers, transfers between locations, returns to vendors, and inventory adjustments/cycle counts. **Design-only at this point — no Canary code yet.** This wiki article is the Canary-specific crosswalk for the v2 D module. The canonical spec lives at `Canary-Retail-Brain/modules/D-distribution.md`.

D is the most ledger-centric v2 module. It publishes more of the stock-ledger's canonical movement verbs (receipt, transfer, RTV, adjustment, cycle-count) than any other module. If the ledger is the substrate, D is the principal author writing to it.

## Code surface

| Concern | File | Status | Notes |
|---|---|---|---|
| Receipt service | `Canary/canary/services/distribution/receipt.py` (projected) | no code yet | Would validate PO, accept received qty, validate cost method, publish receipt movement to ledger |
| Transfer service | `Canary/canary/services/distribution/transfer.py` (projected) | no code yet | Would validate locations, apply up-charges, publish transfer movement |
| RTV service | `Canary/canary/services/distribution/rtv.py` (projected) | no code yet | Would validate RTV auth, reverse cost, publish RTV movement |
| Adjustment service | `Canary/canary/services/distribution/adjustment.py` (projected) | no code yet | Would accept reason code, validate against policy threshold, publish adjustment movement |
| Cycle-count service | `Canary/canary/services/distribution/cycle_count.py` (projected) | no code yet | Would snapshot ledger, accept count sheet, post variance movements |
| Movement publisher | `Canary/canary/services/distribution/ledger_publisher.py` (projected) | no code yet | Would accept movement payloads (qty, cost, reason) and publish to stock-ledger Valkey stream |
| MCP tools | `Canary/canary/blueprints/distribution_mcp.py` (projected) | no code yet | Tools: post-receipt, post-transfer, post-rtv, post-adjustment, init-cycle-count, post-count-result, query-soh, query-intransit |
| Schema | `Canary/canary/models/sales/movements.py` (projected) | no code yet | Would inherit from `SalesBase`; tables: stock_movements, movement_audit_log (append-only, hash-chained) |

## Schema crosswalk

D would write to the `sales` schema (operational/event data). Anticipated tables:

| Table | Owner | Purpose |
|---|---|---|
| `stock_movements` (or `inventory_movements`) | D | Append-only ledger of all inventory movements: receipt, transfer, rtv, adjustment, cycle-count; fields: id, item_id, from_location_id, to_location_id, movement_type, qty_units, cost_cents, reason_code, posted_by, posted_at, merchant_id |
| `movement_audit_log` | D | Hash-chained audit trail; one row per movement; fields: movement_id, prior_chain_hash, chain_hash (SHA-256), posted_at |
| `intransit_inventory` | D | In-transit holds; cleared when receipt completes; fields: transfer_id, item_id, qty, from_location, to_location, expected_arrival_date |
| `cycle_count_sessions` | D | Cycle count instances; fields: id, location_id, snapshot_at (timestamp), count_date, count_type (unit-only, unit-and-dollar) |
| `cycle_count_results` | D | Line items from physical counts; fields: session_id, item_id, counted_qty, ledger_snapshot_qty, variance, reason_code |

D reads from (no write):

| Table | Owner | Why |
|---|---|---|
| `app.items` (via C) | C | D validates item exists and has a cost method before posting receipt |
| `app.purchase_orders` (via F, projected) | F | D matches receipts to POs |
| `sales.transactions` (query only) | T | D may read to correlate inventory position with sales for anomaly detection |

## SDD crosswalk

No v2 SDDs exist yet for D. Projected SDD structure:
- `Canary/docs/sdds/v2/distribution.md` — movement verb definitions, receipt/transfer/RTV/adjustment/cycle-count workflows, ledger-publishing contract, validation rules (reason codes, policy thresholds)
- Section: Ledger relationship (D as primary publisher; which verbs D writes; hash-chain integrity)
- Section: Integration with C (item-master + cost-method validation), F (invoice matching), Q (anomaly detection)

## Where this module fits on the spine

| Axis | Cell | Notes |
|---|---|---|
| [[../projects/RetailSpine\|Retail Spine]] | v2 Distribution | D is part of CRDM expansion ring alongside C, F, J |
| [[../projects/RetailSpine\|Retail Spine]] Ledger roles | Primary Publisher | D publishes 6 of 13 movement verbs: receipt, transfer, RTV, adjustment, cycle-count, reclassification (future) |
| Stock-ledger workflow | Receives → seals → publishes movements | D receives movement data from WMS/manual entry, validates, publishes to `canary:ledger` stream |
| Upstream deps | F (cost-method validation), C (item master) | D cannot post receipt without these |
| Downstream consumers | F (invoice match), Q (anomaly detection), J (demand history) | D's movements feed their analyses |

## Open Canary-specific questions

1. **In-transit inventory tracking.** Should D maintain a separate in-transit table, or resolve ASN/in-transit through the main ledger with a status flag? Current assumption: separate table for efficiency; cleared on receipt.
2. **Receiving discrepancy handling.** If received qty ≠ PO qty, is this posted as one receipt movement (with qty=received) plus one adjustment movement (variance qty), or as a single "receiving variance" movement type? Current assumption: receipt at received qty; if over/under, adjustment follows as separate movement.
3. **Location hierarchy for transfers.** Can D post transfers between any two locations (store↔store, warehouse↔store, warehouse↔warehouse), or are there restricted routes (e.g., only WH→store, no store↔store)? Current assumption: any-to-any at v2, with optional route policy per merchant.
4. **Cycle-count manual override.** If a physical count finds a variance, can the warehouse manager post it directly (D receives and posts), or must Finance (F) approve before D posts? Current assumption: D posts directly; F may audit/escalate.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-module-m-merchandising|C (Commercial)]]
- [[canary-module-f-finance|F (Finance)]]
- [[canary-module-o-orders|J (Orders)]]
- [[canary-module-q-loss-prevention|Q (Loss Prevention)]] — Q reads D's movements for anomaly correlation
- [[../platform/RetailSpine|Retail Spine — Ledger relationships]]
- [[../platform/stock-ledger|Stock Ledger — Perpetual-Inventory Movement Ledger]]
- [[secure-5-inventory|Secure 5 Inventory]] — BOH/RTN/RCT/ADJ/EOH ledger pattern reference

## Sources

- `Canary-Retail-Brain/modules/D-distribution.md` — canonical module spec
- `Canary-Retail-Brain/platform/stock-ledger.md` — ledger verb definitions
- `Canary/docs/sdds/v2/data-model.md` — projected schema overview (not yet written)

---

**Status:** Canary module D is design-phase. No code yet. Ready for SDD drafting and schema design when v2 dev cycle begins. D is the highest-priority v2 module after substrate, as it is the primary publisher to the ledger.

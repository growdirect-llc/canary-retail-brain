---
title: S — Role Alignment
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-s, space-range-display, planogram, fixture, shelf-edge-label, ordering-gate, v3]
sources:
  - Canary-Retail-Brain/modules/S-space.md
  - Canary-Retail-Brain/platform/stock-ledger.md
  - GrowDirect/Brain/wiki/intactix-canonical-validation.md
  - GrowDirect/Brain/wiki/tesco-technical-library.md
  - GrowDirect/Brain/wiki/third-branch.md
last-compiled: 2026-04-24
----

# Canary Module — S (Space)

## Summary

S (Space) owns planograms, fixture inventory, shelf-edge label compilation, and the ordering gate that prevents items from being purchased until they have a physical place on the shelf. **v3 design — implementation deferred.** This wiki article is the Canary-specific crosswalk for the v3 S module. The canonical, vendor-neutral module spec lives at `Canary-Retail-Brain/modules/S-space.md`.

S closes the merchandising-to-operations gap that every SMB retailer faces: the buyer commits to a PO, the store receives the goods, and then nobody knows where to put them. S inverts this by requiring planogram assignment *before* order entry. The ordering gate is the operational discipline that closes the supply chain at the shelf.

## Code surface

| Concern | File | Status | Notes |
|---|---|---|---|
| Planogram schema | `Canary/canary/models/app/planograms.py` (projected) | no code yet | Store-level and zone-level planogram objects with item assignments, facings, pack configurations |
| Fixture master schema | `Canary/canary/models/app/fixtures.py` (projected) | no code yet | Shelf inventory: shelf_id, store_id, dimensions, capacity_units, zone_assignment |
| Capacity validation | `Canary/canary/services/space/capacity_validator.py` (projected) | no code yet | Compares current SOH to planogram capacity; alerts on overstocking |
| Ordering gate | `Canary/canary/services/space/ordering_gate.py` (projected) | no code yet | Queries planogram assignments; blocks PO/receipt if item not assigned at location |
| SEL compilation driver | `Canary/canary/services/space/sel_compiler.py` (projected) | no code yet | Contracts with external SEL system; daily batch + emergency updates |
| MCP tools | `Canary/canary/blueprints/space_mcp.py` (projected) | no code yet | Tools: planogram-authoring, capacity-check, fixture-query, orderability-check, sel-monitor |
| Configuration | `Canary/config.py` extensions (projected) | no code yet | Would add `SEL_SYSTEM_ENDPOINT`, `PLANOGRAM_AUTH_MODE` (strict/permissive), `FIXTURE_REMODEL_NOTIFICATION` |

## Schema crosswalk

S would write to the `app` schema (configuration and master data). Anticipated tables:

| Table | Owner | Purpose |
|---|---|---|
| `planograms` | S | Store-level planogram definition: id, store_id, planogram_version, effective_date, status (draft/active/archived) |
| `planogram_items` | S | Items assigned to planogram: id, planogram_id, item_id, shelf_id, position, facings, pack_config_id, capacity_units, assigned_date |
| `fixtures` | S | Shelf inventory: id, store_id, fixture_name, shelf_id, height_cm, width_cm, depth_cm, linear_ft, capacity_units, zone_id |
| `zones` | S | Store zones: id, store_id, zone_name, fixture_count, total_linear_ft, purpose (produce, dairy, etc.) |
| `planogram_capacity_alerts` | S | Audit trail: id, planogram_id, item_id, alert_type (overstocked, understocked, capacity_exceeded), current_soh, capacity_limit, alert_date |
| `sel_batch_status` | S | SEL compilation tracking: id, batch_date, item_count, compile_status (pending/completed/failed), error_message |

S reads from (no write):

| Table | Owner | Why |
|---|---|---|
| `stock_ledger.movements` (projected) | D | S validates on-hand against planogram capacity |
| `items` | C | S looks up item attributes when assigning to planogram |
| `merchants` | Platform | Store/location list for planogram scoping |

## SDD crosswalk

No v3 SDDs exist yet for S. Canary's current SDDs only cover v1 modules (T, Q, architecture, data-model) and projected v2 modules (C, D, F, J).

Projected SDD structure (future):
- `Canary/docs/sdds/v3/space-range-display.md` — planogram schema, fixture master design, ordering gate implementation, SEL compilation driver interface contract
- Section: Ledger relationship (subscriber role, capacity validation logic, ordering-gate query shape)
- Section: Integration with C (item master lookup), J (replenishment constraints), D (receipt validation), P (price-change SEL re-compile)

## Where this module fits on the spine

| Axis | Cell | Notes |
|---|---|---|
| [[../projects/RetailSpine\|Retail Spine]] | v3 Operations | S is part of the v3 full-spine ring alongside P, L, W |
| [[../projects/RetailSpine\|Retail Spine]] Ledger roles | Subscriber + Gatekeeper | S reads ledger for capacity validation; enforces ordering gate |
| Three-canonical model | WHERE (location/planogram) | Completes the three-canonical model: C (WHO — merchandising), TTL (WHAT — specification), S (WHERE — planogram/display) |
| Upstream feeder | S reads C's item master + D's movement stream (ledger) to validate | |
| Downstream consumer | C reads S's planogram assignments; J reads S's capacity constraints; D reads S's assignments on receipt; P triggers S's SEL re-compile on markdown | |

## Open Canary-specific questions

1. **Planogram-authorization workflow.** Should every store manager be able to edit planograms in real time (permissive), or should planogram changes require central approval (strict)? Current assumption: per-merchant policy; default strict.
2. **Capacity units flexibility.** Should capacity be always in "item units," or support weight/volume for bulk departments (produce, deli)? Current assumption: item units at v3; weight/volume at v3.1.
3. **Multi-location assortment.** Does every store carry every item (uniform assortment), or is there a per-store assortment matrix (store A carries item X, store B doesn't)? Current assumption: uniform at v3; matrix support deferred to v3.1.
4. **SEL external integration.** Is the SEL compiler a Canary-owned service, or does Canary integrate with a third-party label system (Sysrepublic, competitor)? API contract shape? Current assumption: external integration (TBD vendor).
5. **Fixture remodel process.** When a store wants to update fixtures (new shelf, remodel), how does S handle conflict if new capacity is insufficient for existing planogram? Escalation workflow? Current assumption: manual negotiation; automated conflict detection deferred to v3.2.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-module-m-merchandising|C (Commercial)]]
- [[canary-module-d-distribution|D (Distribution)]]
- [[canary-module-o-orders|J (Orders)]]
- [[canary-module-p-pricing-promotion|P (Pricing & Promotion)]]
- [[canary-module-e-execution|W (Execution)]]
- [[../platform/RetailSpine|Retail Spine — Ledger relationships]]
- [[../platform/stock-ledger|Stock Ledger — Perpetual-Inventory Movement Ledger]]
- [[intactix-canonical-validation|Intactix 2006 — Canonical Validation]]
- [[tesco-technical-library|Tesco Technical Library — The Third Canonical Layer]]
- [[srd-shelf-edge-label|Shelf-Edge Label Compilation and Delivery]]
- [[third-branch|The Third Branch]]

## Sources

- `Canary-Retail-Brain/modules/S-space.md` — canonical module spec
- `GrowDirect/Brain/wiki/intactix-canonical-validation.md` — IKB and Space Planning reference
- `GrowDirect/Brain/wiki/tesco-technical-library.md` — TTL and SRD reference
- `GrowDirect/Brain/wiki/srd-shelf-edge-label.md` — SEL compilation context

---

**Status:** Canary module S is design-phase. No code yet. Ready for SDD drafting and schema design when v3 development cycle begins. Expected integration points: C (item master), J (capacity constraints), D (receipt validation), P (SEL re-compile on markdown).

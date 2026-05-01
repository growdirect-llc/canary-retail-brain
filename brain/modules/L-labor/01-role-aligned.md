---
title: L — Role Alignment
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-l, labor, workforce, scheduling, time-tracking, productivity, v3]
sources:
  - Canary-Retail-Brain/modules/L-labor.md
  - Canary-Retail-Brain/platform/stock-ledger.md
  - GrowDirect/Brain/wiki/secure-retail-operating-model-2006.md
  - GrowDirect/Brain/wiki/secure-property-services-operating-model-2002.md
last-compiled: 2026-04-24
----

# Canary Module — L (Labor)

## Summary

L (Labor) owns scheduling, time tracking, payroll integration touchpoints, and labor productivity analytics. **v3 design — implementation deferred.** This wiki article is the Canary-specific crosswalk for the v3 L module. The canonical, vendor-neutral module spec lives at `Canary-Retail-Brain/modules/L-labor.md`.

L is the people-side dimension of the retail operating system. Unlike C (Customer), which tracks customers, L tracks employees — their schedules, time entries, productivity, and payroll integration. L closes the workforce gap that every SMB retailer needs: staffing aligned to traffic, time tracking for labor cost validation, and productivity insights.

## Code surface

| Concern | File | Status | Notes |
|---|---|---|---|
| Employee schema | `Canary/canary/models/app/employees.py` (projected) | no code yet | Employee entity: id, merchant_id, name, contract_type, hourly_rate, location_id, role, active_flag |
| Shift schema | `Canary/canary/models/app/shifts.py` (projected) | no code yet | Shift: id, store_id, employee_id, start_time, end_time, role_assignment, scheduled_hours, traffic_tier |
| Time-entry schema | `Canary/canary/models/app/time_entries.py` (projected) | no code yet | Clock in/out: id, employee_id, location_id, punch_type (in/out/break_start/break_end), timestamp, device_origin, status (on_time/early/late) |
| Schedule management | `Canary/canary/services/labor/schedule_manager.py` (projected) | no code yet | Create/edit/publish shifts; validate traffic alignment and labor budget |
| Productivity calculation | `Canary/canary/services/labor/productivity_calculator.py` (projected) | no code yet | Aggregates transactions per employee per shift; calculates items/hour, txns/hour metrics |
| Payroll export | `Canary/canary/services/labor/payroll_exporter.py` (projected) | no code yet | Exports time entries to payroll system (CSV, generic format; system-specific integrations deferred) |
| MCP tools | `Canary/canary/blueprints/labor_mcp.py` (projected) | no code yet | Tools: schedule-management, time-entry-audit, productivity-analysis, payroll-export-audit, schedule-optimization, absence-management |
| Configuration | `Canary/config.py` extensions (projected) | no code yet | Would add `PAYROLL_SYSTEM_TYPE`, `BREAK_ENFORCEMENT_MODE`, `PRODUCTIVITY_METRICS_VISIBILITY` |

## Schema crosswalk

L would write to the `app` schema (configuration and master data). Anticipated tables:

| Table | Owner | Purpose |
|---|---|---|
| `employees` | L | Employee master: id, merchant_id, location_id, name, contract_type (FT/PT), hourly_rate_cents, role (cashier/stocker/supervisor/manager), active_flag |
| `shifts` | L | Schedule: id, location_id, employee_id, scheduled_start, scheduled_end, role_assignment, traffic_tier (low/medium/high), status (draft/published/completed) |
| `time_entries` | L | Time tracking: id, employee_id, location_id, punch_type (in/out/break_start/break_end), timestamp, device_origin (pos/time_clock/mobile), status (on_time/early/late/no_show) |
| `breaks` | L | Break tracking: id, time_entry_id_start, time_entry_id_end, break_type (paid/unpaid), duration_minutes |
| `absences` | L | Absence tracking: id, employee_id, absence_date, absence_type (sick/pto/unscheduled), approved_flag, approver_id |
| `productivity_metrics` | L | Daily aggregates: id, employee_id, location_id, shift_date, transactions_count, items_handled, labor_hours, txns_per_hour, items_per_hour |
| `payroll_exports` | L | Audit trail: id, export_date, employee_count, total_hours, status (pending/exported/acknowledged_by_payroll), payroll_system_ack_date |

L reads from (no write):

| Table | Owner | Why |
|---|---|---|
| `sales.transactions` | T | L aggregates by employee to calculate productivity (txns per shift) |
| `stock_ledger.movements` (projected) | D | L aggregates by handler to calculate items-handled productivity |
| `fox_cases` | Q | L reads case subjects to see if employees are named in shrink cases |

## SDD crosswalk

No v3 SDDs exist yet for L. Canary's current SDDs only cover v1 modules (T, Q, architecture, data-model) and projected v2 modules (C, D, F, J).

Projected SDD structure (future):
- `Canary/docs/sdds/v3/labor-workforce.md` — employee profile schema, shift management, time-entry capture, payroll export integration, productivity metrics
- Section: Ledger relationship (time-entry events, payroll co-ownership)
- Section: Integration with T (transaction attribution to employee), Q (shrink attribution), J (staffing optimization signals)

## Where this module fits on the spine

| Axis | Cell | Notes |
|---|---|---|
| [[../projects/RetailSpine\|Retail Spine]] | v3 Operations + People | L is part of the v3 full-spine ring alongside S, P, W |
| [[../projects/RetailSpine\|Retail Spine]] Ledger roles | Publisher (time-entry events) + Subscriber (productivity signals) | L publishes time entries to payroll stream; L reads T transactions for productivity |
| People dimension | Employees (distinct from R's Customers) | L owns employee entity with scheduling and time-tracking; R owns customer entity |
| Upstream feeder | L reads T's transaction stream to calculate productivity metrics | |
| Downstream consumer | Payroll system reads L's time entries; J reads L's productivity for staffing optimization; Q uses L's employee data for case context | |

## Open Canary-specific questions

1. **Payroll system integration.** Should Canary support direct API integration to specific payroll systems (ADP, Gusto, Workday), or export generic CSV for merchant to import? Current assumption: generic CSV export at v3; direct API integrations deferred to v3.1.
2. **Time-clock hardware integration.** Should L integrate with physical time-clock devices (Kronos, ADP Timesheets, etc.), or accept time entries only via POS and manual entry? Current assumption: POS + manual entry at v3; hardware integration deferred.
3. **Break-time enforcement.** Should L enforce regulatory breaks (minimum rest periods, max shift length), or is this a merchant-configurable policy layer? Current assumption: policy-configurable at v3; regulatory alerts at v3.1.
4. **Productivity metrics visibility.** Should productivity metrics be visible to the employee (motivational transparency) or only to management? Current assumption: management-only at v3; employee visibility deferred.
5. **Shrink attribution to employees.** When Q identifies shrink with an employee as subject, should L's productivity metrics be "shrink-adjusted"? Current assumption: case context only at v3; metrics adjustment deferred to v3.2.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-model-r-customer|C (Customer)]]
- [[canary-module-t-transaction-pipeline|T (Transaction Pipeline)]]
- [[canary-module-q-loss-prevention|Q (Loss Prevention)]]
- [[canary-module-o-orders|J (Orders)]]
- [[canary-module-s-space|S (Space)]]
- [[canary-module-e-execution|W (Execution)]]
- [[../platform/RetailSpine|Retail Spine — Ledger relationships]]
- [[secure-retail-operating-model-2006|Secure Retail Operating Model 2006]]
- [[secure-property-services-operating-model-2002|Secure Property Services Operating Model 2002]]

## Sources

- `Canary-Retail-Brain/modules/L-labor.md` — canonical module spec
- `GrowDirect/Brain/wiki/secure-retail-operating-model-2006.md` — people-side operating model context
- `GrowDirect/Brain/wiki/secure-property-services-operating-model-2002.md` — workforce planning reference

---

**Status:** Canary module L is design-phase. No code yet. Ready for SDD drafting and schema design when v3 development cycle begins. Expected integration points: T (transaction attribution), Q (shrink attribution), J (staffing optimization).

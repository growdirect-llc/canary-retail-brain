---
classification: confidential
owner: GrowDirect LLC
type: module-spec
prefix: L
status: v3 (design)
sibling-modules: [S, P, W]
---

# L — Labor & Workforce

L owns scheduling, time tracking, payroll integration touchpoints, labor productivity analytics, and employee profile management. L is the people-side dimension that complements R (Customer) on the customer-facing side — the employee as a first-class entity in the retail operating system.

L is one of the [[spine-13-prefix#v3-full-spine-s-p-l-w|v3 full-spine expansion]] modules. It closes the workforce gap that every SMB retailer needs: scheduling staff to match traffic, time tracking to validate labor costs, and productivity signals that feed into store operations analytics.

## Purpose

L owns four jobs:

1. **Scheduling and shift management.** Create and manage employee schedules aligned to store traffic patterns, labor budget constraints, and regulatory requirements (rest periods, max-hours-per-week, etc.). Publish schedules to employees; track adherence.
2. **Time tracking and attendance.** Clock in/out records, break tracking, absence tracking. Validate that actual hours match scheduled hours. Flag exceptions (early/late, missed punches, unauthorized breaks).
3. **Payroll integration touchpoints.** Export time-tracking data to payroll system (do not own payroll itself). Validate wage calculations against contracted rates. Provide audit trail for wage variance investigation.
4. **Labor productivity analytics.** Measure productivity per employee per shift (transactions per labor-hour, items handled per labor-hour, etc.). Use productivity signals to identify training needs, staffing optimization opportunities, and schedule improvements.

L does **not** own:

- Payment processing or payroll execution. Payroll is external.
- Store traffic forecasting. That belongs to [[J-forecast-order|J (Forecast & Order)]].
- Workforce planning or headcount forecasting. That is a merchant-level strategic function.
- Compensation strategy or benefit administration. That is HR/payroll system.

## CRDM entities touched

| CRDM entity | L's relationship | How |
|---|---|---|
| **People** | Owns the Employee subset | Employee entity with scheduling, time-tracking, and productivity attributes (distinct from R's Customer) |
| **Events** | Publishes | Time-entry events (clock in/out, break, absence) that feed into payroll export |
| **Workflows** | Reads | Reads ledger movements and transaction data to calculate productivity metrics |
| **Places** | Reads | Location and zone assignments for schedule planning |
| **Things** | Reads | Device and POS assignment for time-entry origin validation |

L's posture: **L is an Employee registry and time-tracking system that publishes time-entry events and tracks productivity signals.** L does not modify the stock ledger directly; it subscribes to T's transaction stream for productivity calculation.

## ARTS mappings

ARTS does not define Employee, Scheduling, or Time Tracking specifications. Canary defines these internally:

| Canary construct | Definition | Reference |
|---|---|---|
| **Employee** | Individual worker with contract type (full-time, part-time, contractor), hourly rate, location assignment, role (cashier, stocker, supervisor, manager) | Square has basic employee record; extend with scheduling/time-tracking attributes |
| **Shift** | Scheduled work block: employee, location, start time, end time, role assignment, expected traffic tier | Retail standard scheduling model |
| **Time Entry** | Clock in/out record with timestamp, employee, location, device, actual hours, break time, status (on-time, early, late, no-show) | Square integrates with time-clock systems; model extends to time-tracking dimension |
| **Productivity metric** | Transactions per labor-hour, items handled per labor-hour, shrink attribution to employee (via Q case subjects), schedule adherence rate | Retek-era analytics; feed from T transaction stream + Q case subject tracking |

Cross-reference to ARTS:

- ARTS has no Employee or Scheduling specification (customer-facing; does not include workforce dimension)
- Square has basic employee records; integration path exists for time-tracking import

## Ledger relationship

**L is PUBLISHER of time-entry events and SUBSCRIBER for productivity signals.**

Movements L publishes:

| Movement | Trigger | Effect | Note |
|---|---|---|---|
| **Time-entry event** | Clock in/out, break start/end, absence/illness | Appends to time-tracking ledger; feeds payroll export; no ledger movement itself | L publishes to payroll stream; ledger records employee attribution for loss-prevention case context |
| **Productivity signal** | End of shift / daily aggregation | Calculates metrics (txns per hour, items per hour); stored in employee performance table | Informational; feeds J (Forecast) for staffing optimization |

L reads from (no write):

- **Sales.transactions (via T)** — to calculate productivity (txns per employee per shift)
- **Stock.movements (via D)** — to calculate item-handling productivity
- **Loss-prevention case subjects (via Q)** — to attribute shrink/exceptions to employees for investigative context
- **Schedule and time-entry data** — L's own tables; reads to validate schedule adherence

**Payroll co-ownership** — L exports time entries to payroll; payroll system applies wage rates and calculates gross pay. L validates wage output against contracted rates. Wage variance is escalated to HR/payroll.

**Perpetual-vs-period boundary.** Canary owns: time-clock entries + scheduled-shift movements. Merchant tool owns: payroll calculation + tax filing (Gusto, Paychex, ADP, etc.). Default implementation route: `integrated-hybrid`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (data producers):

- Employee input (schedule requests, manual time edits for payroll corrections)
- Time-clock hardware or manual clock-in (POS, dedicated time terminal, mobile app)
- Scheduling rules (labor budget, traffic patterns, regulatory constraints)
- HR system or employee master (contract rate, role, location)

**Downstream consumers** (data subscribers):

- **Payroll system (external)** — L exports time entries; payroll calculates pay and deductions
- **T (Transaction Pipeline)** — T records employee (cashier) on every transaction for productivity calculation and LP context
- **Q (Loss Prevention)** — Q uses L's employee records to identify subjects of interest; shrink may be attributed to specific employees in case investigation
- **J (Forecast & Order)** — J reads L's productivity metrics to optimize staffing schedules and replenishment timing
- **S (Space, Range, Display)** — S reads L's schedule to validate that labor is available for planogram changes or restocking
- **Store operations dashboard** — displays schedule adherence, productivity trends, staffing alerts (over/under budget)

## Agent surface

L exposes MCP tool families for store-management and scheduling workflows:

- **Schedule management** — create/edit shifts, assign employees, set traffic tiers, publish schedules to staff, track adherence
- **Time-entry audit** — review clock in/out records, identify anomalies (missed punches, long shifts, excessive breaks), approve manual corrections
- **Productivity analysis** — query productivity metrics per employee per shift; identify top performers and training candidates
- **Payroll export auditing** — review time entries ready for payroll export, validate against contracted rates, flag wage variance
- **Schedule optimization** — view historical productivity and traffic patterns; request algorithm-assisted schedule suggestions
- **Absence management** — log and track employee absences (illness, PTO, scheduled leave); validate coverage

## Security posture

- **Auth.** Scheduling and time-entry management require `store_manager` or `supervisor` role. Payroll export requires `payroll_administrator` or `finance` role. MCP tool-level role checking enforced.
- **Tenant scoping.** Every employee, shift, and time entry carries `merchant_id` and (usually) `location_id`; every read is row-level-secured.
- **PII handling.** Employee names, phone numbers, social security numbers (if captured for payroll) are stored securely and encrypted. Access is logged.
- **Time-entry integrity.** Clock in/out times are recorded with device origin, cannot be edited retroactively (audit trail only; corrections must go through manual-edit workflow with approval).
- **Payroll data protection.** Time entries exported to payroll are marked immutable once exported; any correction requires payroll system acknowledgment.
- **Productivity reporting privacy.** Productivity metrics are reported per employee (visible to management) but not visible to other employees. Compensation impact is not disclosed in Canary (payroll system decision).

## Roadmap status

- **v3 (design)** — Employee profile management. Schedule creation and adherence tracking. Time entry capture (clock in/out, breaks, absences). Payroll export integration touchpoint. Productivity metrics calculation. Read-only and restricted-write MCP tools for scheduling workflows.
- **v3.1** — Schedule optimization engine (algorithm-assisted shift suggestions based on traffic and productivity). Absence forecasting (predict staffing gaps).
- **v3.2** — Wage variance analysis and escalation. Training-need identification based on error rates and productivity.
- **v3.3** — Cross-location labor pool management (flexible staffing to cover peaks at multiple locations).

## Open questions

1. **Payroll system integration scope.** Should L export to a specific payroll system (ADP, Gusto, Workday, etc.), or provide a generic CSV export that any payroll system can ingest? Current assumption: generic export at v3; direct API integrations at v3.1+.
2. **Scheduling authority.** Can any manager create schedules, or must schedules be approved by a higher authority (district manager)? Per-merchant policy?
3. **Time-clock hardware support.** Does L integrate with specific time-clock vendors (e.g., Kronos, ADP), or accept time entries only via manual entry and POS? Current assumption: manual entry and POS at v3; hardware integration deferred.
4. **Productivity attribution to shrink.** When Q identifies shrink associated with an employee (via case subject), should L's productivity metrics reflect this (e.g., shrink-adjusted productivity), or is shrink purely a case context? Current assumption: case context only at v3; metrics adjustment deferred.
5. **Break-time enforcement.** Should L enforce regulatory breaks (minimum rest period, maximum shift length), or is break enforcement a store-policy layer? Current assumption: policy-configurable at v3; regulatory compliance alerts at v3.1.

## Related

- [[../platform/stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]]
- [[../platform/spine-13-prefix|The Canary Retail Spine — 13 Modules]]
- [[../../GrowDirect/Brain/wiki/secure-retail-operating-model-2006|Secure Retail Operating Model — People-side context]]
- [[../../GrowDirect/Brain/wiki/secure-property-services-operating-model-2002|Secure Property Services Operating Model — Workforce planning reference]]
- [[T-transaction-pipeline|T (Transaction Pipeline)]]
- [[Q-loss-prevention|Q (Loss Prevention)]]
- [[J-forecast-order|J (Forecast & Order)]]
- [[S-space-range-display|S (Space, Range, Display)]]
- [[W-work-execution|W (Work Execution)]]

## Sources

- [[../../GrowDirect/Brain/wiki/secure-retail-operating-model-2006|Secure Retail Operating Model 2006 — Operating framework including people-side dimension]]
- [[../../GrowDirect/Brain/wiki/secure-property-services-operating-model-2002|Property Services Operating Model 2002 — Workforce scheduling and time-tracking reference]]

---

*Classification: confidential. Owner: GrowDirect LLC. Created 2026-04-24. L (Labor & Workforce) is a v3 module spec within the Canary Retail Spine. It is design-stage; implementation is deferred pending v2 ring (C/D/F/J) stabilization.*

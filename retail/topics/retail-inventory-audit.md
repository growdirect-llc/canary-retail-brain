---
card-type: domain-module
card-id: retail-inventory-audit
card-version: 2
domain: lp
layer: domain
status: approved
agent: ALX
feeds: [retail-inventory-valuation-mac, retail-operations-kpis]
receives: [retail-site-management, retail-merchandise-hierarchy]
tags: [inventory-audit, physical-inventory, cycle-count, shrink, stock-count, physical-book-reconciliation, loss-prevention]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

The retail inventory audit model: cycle-count scheduling, physical inventory procedures, physical-book inventory reconciliation, and shrink management at the site and department level.

## Purpose

Perpetual inventory accuracy is the foundation of replenishment, financial reporting, and loss prevention. If the system believes a store has 12 units of an item and the store actually has 3, replenishment will not reorder until the phantom inventory is consumed — causing preventable stockouts. Physical inventory audits reconcile the book record against physical reality, surface shrinkage, and satisfy accounting requirements. Without a disciplined audit schedule, perpetual inventory accuracy degrades over time and every downstream process that depends on on-hand data becomes unreliable.

## Structure

**Audit schedule management** — Physical inventory audits are scheduled in advance, not conducted ad hoc. The schedule specifies: which sites are counted, which departments or item categories are in scope for a given count, the count date and time (typically before store opening to avoid transaction interference), and whether the count is a full store count or a targeted cycle count. High-shrink departments receive higher audit frequency.

**Audit types:**

| Type | Scope | Frequency |
|------|-------|-----------|
| Full store count | All items in the store | Annual or semi-annual |
| Cycle count | Defined subset of items (by department, category, or ABC velocity) | Continuous, rotating |
| Empty shelf audit | Items with zero on-hand per system but absent from shelf | Weekly or as-needed |
| Targeted count | High-shrink items, recently received items, or items flagged by loss prevention | As triggered |

**Count execution** — Before the count begins, the system freezes the article snapshot: a point-in-time on-hand record that count variances are calculated against. During the count, associates count physical units using RF scanners or manual count sheets. No receiving transactions or sales should occur in the counted area during the count. After the count, the system compares physical counts to the snapshot.

**Physical-book reconciliation** — Variances between the physical count and the book record are classified:

- **Shrink** — On-hand per book is higher than physical count. Causes: theft, vendor short-shipment, administrative error, spoilage. Shrink is posted as an inventory adjustment and charged to the shrink account by department.
- **Overage** — Physical count is higher than book. Causes: receiving error (received more than booked), returned merchandise processed incorrectly, counting error. Overages are investigated before posting — unexplained overages may indicate receiving fraud.
- **Tolerance** — Minor variances within a defined count tolerance (% or unit) are accepted without investigation. Variances outside tolerance require sign-off before posting.

**Shrink management** — Shrink rate (shrink $ ÷ sales $) is the primary performance measure, tracked at store and department level. High-shrink departments receive targeted audits and LP attention. Shrink reporting is maintained historically so trends are visible — a store with deteriorating shrink rates over consecutive periods is a loss prevention signal. Accrual-based shrink accounting applies an estimated shrink rate between physical counts, true-up at each count.

**Empty shelf audit** — A specialized count type that identifies items where the system shows positive on-hand but the physical shelf is empty. These are phantom inventory units — they exist in the book but not in reality. Empty shelf audits are the fastest way to find perpetual inventory errors without conducting a full count.

## Consumers

The Inventory module applies adjustment transactions from reconciled counts and updates the perpetual on-hand. The Finance module uses count results to true up shrink accruals on the P&L. The Loss Prevention function uses shrink rate trends by department and store to prioritize investigation resources. The Replenishment module reads corrected on-hand data immediately after count posting. The Operations Agent monitors shrink rate trends and empty-shelf audit results as indicators of inventory data health.

## Invariants

- The article snapshot must be frozen before counting begins. Counting against a live on-hand record produces reconciliation errors as transactions post during the count.
- Physical inventory adjustments require documented authorization above a defined threshold — they are not a mechanism for fixing purchasing or receiving errors without an audit trail.
- Shrink accrual and physical count results must use consistent accounting treatment. Mixing accrual methods between count cycles produces meaningless variance analysis.

## Platform (2030)

**Agent mandate:** Operations Agent owns perpetual inventory health monitoring — it is not waiting for the next physical count. It monitors POS exception patterns, empty-shelf audit results, and receiving discrepancy rates continuously to detect inventory accuracy degradation between physical counts. Physical counts are an accounting compliance requirement; they are not the primary inventory accuracy mechanism.

**Continuous shrink detection vs. periodic reconciliation.** Traditional shrink management is a count exercise: count twice a year, reconcile to book, post the adjustment. Operations Agent monitors three leading shrink indicators in real time: (1) items with positive book inventory but zero recent sales velocity — phantom stock candidates; (2) receiving discrepancy patterns at specific sites — over-receiving or under-recording signals; (3) POS exception patterns (frequent voids, high return rates at specific terminals, no-sale transactions) — potential employee theft signals. These surface before the annual count, when intervention is still possible.

**Physical counts for accounting, not operations.** Physical inventory remains required for GAAP compliance and shrink true-up. But in a well-instrumented Canary Go store, the physical count result should not be a surprise — Operations Agent has been tracking the expected shrink trajectory and the count should confirm the accrual estimate within a tight range. A large count variance is a signal that continuous monitoring missed something — an investigation trigger, not just an accounting entry.

**MCP surface.** `shrink_rate(site_id, dept, period)` returns shrink rate trend by site and department. `phantom_inventory_alerts(site_id)` returns items flagged as probable phantom stock. `audit_schedule(site_id)` returns upcoming counts and last-count dates. `inventory_accuracy(site_id)` returns perpetual accuracy score from the most recent cycle count. Low-token, agent-consumable.

**RaaS.** Physical count events and inventory adjustment records are receipt-class data — timestamped, immutable after posting. Adjustment events are new records referencing the count event that generated them; retroactive modification of a count record is a control failure. `shrink_rate(site_id, dept, period)` is a range aggregate indexed on (site_id, dept, count_date) — rolling 52-week queries are common and must not full-scan. `phantom_inventory_alerts(site_id)` requires near-real-time comparison of book on-hand (SQL) against sales and receipt signals (Valkey). Count history exportable for insurance claims, financial audit, and LP investigation.

## Related

- [[retail-inventory-valuation-mac]] — physical count adjustments update MAC and on-hand book value
- [[retail-site-management]] — site configuration determines count scope and RF infrastructure availability
- [[retail-operations-kpis]] — shrink rate is a primary operations KPI
- [[retail-receiving-disposition]] — receiving errors are a leading cause of perpetual inventory inaccuracy

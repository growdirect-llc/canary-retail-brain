---
classification: confidential
owner: GrowDirect LLC
type: module-spec
prefix: F
status: v2 (design)
sibling-modules: [C, D, J]
---

# F — Finance

The finance module owns purchase orders, supplier invoices, invoice-to-receipt reconciliation (three-way match), period-close financial reporting, general-ledger posting, and the merchant's choice of cost accounting method (Retail Inventory Method vs Cost Method). F is the reconciler that ensures ledger state agrees with supplier truth and that margin calculations are accurate.

F is one of the [[spine-13-prefix#v2-crdm-expansion-c-d-f-j|v2 CRDM expansion]] modules. It closes the financial-flow and cost-accounting gap: from purchase-order commitment through invoice receipt and cost reconciliation through period-close GL posting and margin reporting.

## Purpose

F owns four jobs:

1. **Own the cost-method decision.** Per-department designation of Retail Inventory Method (RIM) or Cost Method. This choice cascades through the entire organization: how on-hand is valued, how margin is calculated, how period close runs, and how Open-to-Buy is expressed. F is the authoritative source of this decision for the entire retail platform.
2. **Manage the purchase-order and invoice lifecycle.** A PO is a commitment; an invoice is a claim for payment. F tracks both, validates that each invoice matches a corresponding PO, and flags variances (price, quantity, freight, duty) for resolution.
3. **Reconcile invoices to receipts.** When a supplier invoice arrives, F performs a three-way match: PO ↔ receipt (from D) ↔ invoice. If amounts don't match within tolerance, F posts a cost-variance adjustment to the stock ledger and flags the discrepancy for resolution.
4. **Run period close and GL posting.** At month-end (or other period boundary), F aggregates all ledger movements, calculates cost-of-goods-sold, applies the chosen cost-method (RIM cost-complement calculation or Cost-Method cost-flow assumption), and posts entries to the general ledger. Period-close run produces the month-end financial statements.

F does **not** own:

- Purchase-order recommendation generation. That belongs to [[J-forecast-order|J (Forecast & Order)]].
- Item-cost updates due to supplier price changes. That belongs to [[C-commercial|C (Commercial)]].
- Period-close accounting policy (e.g., should shrink be written off or capitalized?). That is a merchant-side policy decision; F implements it.

## CRDM entities touched

| CRDM entity | F's relationship | How |
|---|---|---|
| **Events** | Reads and publishes | F reads all stock-ledger movements (from D, C, T); F publishes GL-posting movements at period close |
| **Things** | Reads | Joins to item master (via C) for cost-method validation |
| **Places** | Reads | Joins to location for period-close location-level rollup |
| **Workflows** | Emits events | F publishes variance cases and period-close workflows; W and Q may subscribe |
| **People** | Reads | Identifies finance manager, approver of invoice variance resolutions |

F's posture: **F is a Reconciler and GL Publisher that reads all ledger movements, validates them against external sources (supplier invoices, POs), and posts period-close entries.** F does not directly modify the stock ledger; instead, F publishes cost-variance movements (when invoices don't match receipts) and GL-posting movements (at period close) that the ledger ingests.

## Ledger relationship

**F is RECONCILER and CO-ANALYST for Open-to-Buy calculation.**

Movements F publishes to the stock ledger:

| Movement | Trigger | Effect on ledger |
|---|---|---|
| **Cost-variance adjustment** | Invoice amount doesn't match receipt cost within tolerance (ReIM / three-way-match failure) | Posts `+/-` cost adjustment to on-hand; posts GL variance entry (COGS adjustment) |
| **GL posting at period close** | Month-end close process | Aggregates all movements for the period, applies cost-method (RIM cost-complement or Cost-Method cost flow), posts GL entries (COGS, inventory, margin) |
| **Shrink write-off (optional)** | Merchant policy: shrink is a period-end GL entry rather than a ledger adjustment | Posts shrink reserve / shrink expense GL entry if policy requires it |

Ledger reads F consumes:

- **Stock-on-hand and cost basis** — current quantity and value per item per location per cost method. Used to calculate inventory valuation at period close.
- **Movement history for the period** — all receipts, sales (via T), RTVs, adjustments, markdowns. Used to calculate COGS and margin per item, per department, per location.
- **Cost-method designation per item** — from C, to determine whether to apply RIM cost-complement calculation or Cost-Method cost-flow assumption during period close.

**Co-owner of OTB calculation** — F owns the RIM/Cost-Method choice; C owns the OTB calculation; J owns the demand forecast that feeds into OTB.

**Perpetual-vs-period boundary.** Canary owns: 3-way invoice match + COGS posting events. Merchant tool owns: GL, A/P, A/R, P&L (QuickBooks Online, Xero, Wave, etc.). Default implementation route: `integrated-hybrid` — established by [[../case-studies/canary-finance-architecture-options|v2.F ADR]]. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (event producers):

- Purchase-order system (POs authorized by buyer or automated by J)
- Supplier invoice system (invoices received, matched to POs)
- Accounting system (GL chart of accounts, GL posting templates)
- Bank / payment processor (payment confirmation, payout reconciliation)

**Downstream consumers** (data subscribers):

- **C (Commercial)** — C reads cost-method designation to understand how to price cost-update events; C receives cost-variance notifications from F for audit trails.
- **D (Distribution)** — D reads cost-method validation before posting a receipt (can only receive items with a defined cost method).
- **J (Forecast & Order)** — J reads period-close margin data to validate forecast accuracy and optimize replenishment.
- **Q (Loss Prevention)** — Q reads cost-variance data to correlate with shrink and exception cases.
- **Merchant financial reporting** — F publishes GL entries that feed the merchant's financial statements (P&L, balance sheet).

## Agent surface

F exposes MCP tool families for finance and accounting workflows:

- **PO lifecycle** — create, approve, and commit POs with OTB check (C provides headroom validation); release POs for receipt
- **Invoice matching** — query PO ↔ receipt ↔ invoice status; flag variances; approve or dispute
- **Cost-variance audit trail** — inspect all cost-variance adjustments posted over a period; see GL impact and resolution status
- **Period-close dashboard** — initiate close, see per-location close status, post GL entries, view close results (COGS, margin, inventory valuation)
- **Cost-method configuration** — read-only view of department cost-method assignments; (restricted) update per-department cost method (gated to CFO role)
- **GL reconciliation** — query GL balances, compare to ledger-derived balances, identify reconciling items
- **Margin reporting** — per-item, per-department, per-location margin analysis with shrink attribution

## Security posture

- **Auth.** PO creation requires `buyer` role; PO commitment requires `approver` role (gated by OTB headroom). Invoice variance approval requires `finance-manager` or `controller` role. Period-close posting requires `controller` or `cfo` role.
- **Tenant scoping.** Every row carries `merchant_id`; every read is row-level-secured. F cannot post GL entries for another merchant.
- **Cost-method lock.** Cost-method designation per department cannot be changed retroactively without triggering a full inventory revaluation (not automated; requires manual accounting action). Cost-method changes are logged with approval trail.
- **Invoice variance tolerance.** Per-merchant policy threshold (e.g., ±2% on landed cost). Variances exceeding tolerance are escalated to F manager for review before GL posting.
- **Auditability.** Every PO, invoice, variance, and GL posting is immutable once posted. GL posting is tied to an audit-signed period-close event.
- **Segregation of duties.** PO creation is separate from invoice approval; invoice approval is separate from GL posting. Same person cannot do all three steps.

## Roadmap status

- **v2 (design)** — PO lifecycle, invoice matching (three-way match), cost-variance posting to ledger, cost-method designation per department, period-close GL posting (monthly). MCP tools for finance workflows. Integration with C for OTB validation and cost-update subscriptions. Integration with D for receipt matching. No multi-currency or multi-fiscal-calendar support at v2.
- **v2.1** — Extended cost-variance tolerance rules (tiered by vendor, by category, etc.). Rebate and chargeback tracking.
- **v3** — Integration with P (Pricing & Promotion) for markdown-driven cost revaluation. Integration with L (Labor & Workforce) for payroll GL posting.

## Open questions

1. **Cost-method change mid-period.** If a department switches from RIM to Cost Method mid-month, how are the period-close calculations handled? Blended? Or split by cost method per sub-period?
2. **Invoice variance resolution.** If an invoice variance is disputed (e.g., retailer says supplier overcharged), who has authority to adjust the posted cost-variance — the supplier (vendor credit memo) or the retailer (debit memo)?
3. **Multi-currency transactions.** If a supplier bills in EUR but the merchant's GL is in USD, who handles FX conversion — the supplier (invoice in USD) or F (FX variance on posting)?
4. **Satoshi-level cost accounting.** Should F extend the cost ledger to [[../platform/satoshi-cost-accounting|satoshi-level cost accounting]] for metered sub-cent costs (shipping fees, agent tool fees)? Phase 2 or later?

## Related

- [[../platform/stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]]
- [[../platform/retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]]
- [[../platform/satoshi-cost-accounting|Satoshi-Level Cost Accounting — Sub-Cent Unit Cost on the Stock Ledger]]
- [[../platform/crdm|Canonical Retail Data Model (CRDM)]]
- [[../platform/spine-13-prefix|The Canary Retail Spine — 13 Modules]]
- [[C-commercial|C (Commercial)]]
- [[D-distribution|D (Distribution)]]
- [[J-forecast-order|J (Forecast & Order)]]

## Sources

- [[../../GrowDirect/Brain/wiki/retek-rms-perpetual-inventory|Retek RMS — Perpetual-Inventory Movement Ledger]] — cost-method treatment (RIM, Cost Method, consignment), three-way-match pattern, ReIM invoice-matching module
- [[../../GrowDirect/Brain/wiki/retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]] — financial foundation for cost-method choice

---

*Classification: confidential. Owner: GrowDirect LLC. Created 2026-04-24. F (Finance) is a v2 module spec within the Canary Retail Spine. It is design-stage; implementation is pending.*

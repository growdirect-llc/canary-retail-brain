---
card-type: domain-module
card-id: retail-three-way-match
card-version: 2
domain: finance
layer: domain
status: approved
agent: ALX
feeds: [retail-chargeback-matrix, retail-inventory-valuation-mac, retail-ap-vendor-terms]
receives: [retail-purchase-order-model, retail-receiving-disposition]
tags: [three-way-match, receiving, invoice, PO, ASN, discrepancy, finance, AP, inventory]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

The three-way match: the reconciliation of Purchase Order, Advance Ship Notice, and physical Receipt that gates invoice approval and triggers chargeback events when discrepancies are found.

## Purpose

The three-way match is the financial control point at the intersection of purchasing, receiving, and accounts payable. It verifies that what was ordered (PO), what the vendor said they shipped (ASN), and what the retailer physically received (Receipt) all agree before an invoice is approved for payment. Discrepancies between any two of the three documents trigger specific financial consequences — chargebacks, deductions, or credits — rather than being resolved informally.

## Structure

**The three documents:**

| Document | Source | Key data |
|----------|--------|----------|
| Purchase Order (PO) | Buyer/replenishment system | Item, ordered qty, PO cost, delivery location, delivery window |
| Advance Ship Notice (ASN) | Vendor via EDI 856 | Item, shipped qty, carton configuration, ship date, carrier |
| Receipt | Receiving system at DC or store | Item, received qty, condition, receipt date, receiving method |

**Match logic** — A complete three-way match requires all three documents to agree within defined tolerances on item identity, quantity, and timing. The sequence of comparisons:

1. **PO vs. ASN** — Vendor shipped what was ordered? Item substitutions, quantity overages/underages, and missing items are flagged. An ASN that does not reference a valid open PO is rejected.

2. **ASN vs. Receipt** — Physical receipt matches what vendor said was shipped? Carton count variance, inner pack discrepancies, and missing shipments are flagged. This comparison also validates ASN accuracy for the vendor scorecard.

3. **PO vs. Receipt** — Combined: did the retailer receive what it ordered, at the ordered cost? Quantity variance drives short-shipment chargebacks. Cost variance drives invoice deductions.

**Receiving methods and confidence levels** — Three receiving methods produce the Receipt document, each with different accuracy confidence:

- **Assumed receiving** — Receipt accepted as equal to the ASN without physical count. High throughput, low accuracy. Used for trusted high-compliance vendors with strong ASN track records. Retrospective audits validate assumption accuracy.
- **Outer-case scan** — Carton barcodes scanned; inner pack counts are assumed from item master. Medium confidence. Efficient for high-volume standard-pack items.
- **Manual count** — Full unit-level count of all received items. Highest accuracy, highest cost. Required for high-value items, first shipments from new vendors, or vendors with poor ASN compliance history.

**Discrepancy handling** — Discrepancies between PO, ASN, and Receipt fall into categories: shortage (received less than invoiced), overage (received more), substitution (different item), damage (units received in unacceptable condition), and timing violation (received outside the delivery window). Each category maps to a defined chargeback type in the chargeback matrix.

**Invoice approval gate** — An invoice is approved for payment only when the three-way match is complete within tolerance. Invoices with open discrepancies are held. The AP module generates debit memos for deductions before releasing payment. Invoice hold aging is monitored to avoid vendor relationship damage from unexplained holds.

## Consumers

The Finance/AP module executes the match and holds invoices on discrepancy. The Vendor Agent records match results as compliance events in the vendor scorecard. The Inventory module updates on-hand quantities based on confirmed receipt. The Operations Agent monitors match failure rates by vendor and surfaces vendors where match failure is systematic rather than episodic.

## Invariants

- Every invoice payment must be gated on a completed three-way match. Paying on invoice alone removes all chargeback leverage.
- Discrepancy tolerance thresholds (acceptable quantity variance %) are maintained in vendor management, not set ad hoc by the receiving team.
- All three documents must reference the same PO number as the common key. Orphaned receipts (no PO) and phantom invoices (no receipt) are exception alerts, not normal process outcomes.

## Platform (2030)

**Agent mandate:** Operations Agent executes three-way match automatically in real time when receipt events arrive. Finance Agent triggers automatic payment release for matched invoices and holds for exceptions. Neither agent makes discretionary payment decisions — the contract and match logic execute; agents surface exceptions and initiate authorized flows.

**Match as contract state machine.** In the traditional model, three-way match is a batch job: AP runs a match program at invoice processing time, exceptions go to a work queue. In the Canary Go model, the vendor's smart contract is the match engine. PO issuance writes PO state. ASN arrival updates ASN state. Receipt confirmation triggers match evaluation automatically. For smart-contract-native vendors, the contract produces one of three outcomes: (1) matched within tolerance → automatic payment release signal; (2) short shipment → automatic chargeback event computed against the chargeback matrix; (3) no-ASN receipt → automatic ASN non-compliance event. No manual match steps. No AP work queue for compliant vendors.

**Real-time discrepancy surfacing.** Operations Agent monitors the match stream in real time. Systematic match failures by vendor — high invoice exception rate, repeated short shipments, recurring ASN inaccuracies — surface as vendor performance signals before the scorecard period closes. An exception that takes 30 days to resolve in the traditional model often costs more in AP handling time than the chargeback value; Operations Agent identifies these patterns and flags vendors for smart contract enrollment or compliance remediation.

**MCP surface.** `match_status(po_id)` returns PO/ASN/receipt reconciliation state and any pending exceptions. `match_exceptions(vendor_id, period)` returns unresolved discrepancies with age and financial exposure. `match_rate(vendor_id)` returns first-pass match rate — the primary AP efficiency KPI. Single-call, low-token.

**RaaS.** The three-way match event — PO, receipt, and invoice aligned — is the most critical receipt event in the financial chain; it authorises payment. Match events must be sequenced strictly after their constituent events: receipt event must precede the match event, match event must precede the payment event. An out-of-sequence match (payment before confirmed receipt) is a financial control failure. `match_status(po_id)` indexed on po_id; must resolve in <200ms to support same-day payment processing. Match records are append-only; exceptions are new events against the match record. Match history exportable for AP audit; exception records must support ad hoc query by vendor, period, and exception type without full-scan.

## Related

- [[retail-purchase-order-model]] — the PO that anchors the match
- [[retail-receiving-disposition]] — the operational response to quality discrepancies at receipt
- [[retail-chargeback-matrix]] — the financial consequences of match failures
- [[retail-ap-vendor-terms]] — the invoice approval and payment process that the match gates
- [[retail-inventory-valuation-mac]] — MAC update triggered by confirmed receipts

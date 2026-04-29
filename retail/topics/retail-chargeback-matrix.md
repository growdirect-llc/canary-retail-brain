---
card-type: domain-module
card-id: retail-chargeback-matrix
card-version: 2
domain: finance
layer: domain
status: approved
agent: ALX
feeds: [retail-ap-vendor-terms]
receives: [retail-vendor-scorecard, retail-vendor-compliance-standards, retail-receiving-disposition, retail-three-way-match]
tags: [chargeback, vendor, allowances, deductions, compliance-fee, smart-contract, AP, finance]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

The chargeback matrix: the taxonomy of chargeback types, the occurrence-based administrative fee schedule, and the deduction and allowance structures that govern financial enforcement of vendor compliance obligations.

## Purpose

Chargebacks are the financial teeth of vendor compliance. A compliance standard without an associated chargeback is a suggestion. The chargeback matrix defines exactly what a vendor owes the retailer when they fall below a documented standard — by type of violation, by number of occurrences, and by severity. This matrix is also the primary data model for smart contract encoding: each row is a clause that can be automated, monitored, and settled programmatically.

## Structure

**Chargeback types:**

| Type | Trigger | Enforcement mechanism |
|------|---------|----------------------|
| Short shipment | Units received < units invoiced | Deduct from invoice payment |
| Late delivery | Delivery outside agreed window | Administrative fee per occurrence |
| ASN non-compliance | ASN missing, inaccurate, or late | Administrative fee per occurrence |
| EDI non-compliance | Missing or malformed EDI transaction | Administrative fee per occurrence |
| Carton/marking violation | Carton fails packing or marking standard | Administrative fee per carton |
| Product quality rejection | Lot fails acceptance inspection | Return at vendor cost, or defective allowance |
| Invoice discrepancy | Invoice price ≠ PO cost | Automatic deduction at payment |
| RTV credit delay | Credit not issued within agreed timeline | Interest accrual or deduction |
| Co-op non-compliance | Co-op funds not earned or not claimed correctly | Debit memo adjustment |

**Occurrence-based fee escalation** — Administrative fees for repeated violations escalate by occurrence count within a measurement period. A typical structure:

- 1st occurrence: base administrative fee (e.g., flat $25–$100 per event)
- 2nd–3rd occurrence: 150% of base fee
- 4th+ occurrence: 200% of base fee, plus scorecard flag for rationalization review

The matrix must be agreed with the vendor at setup. Escalation tiers and base fees are vendor-negotiable within a defined range.

**Allowance types:**

| Allowance type | Structure | Settlement timing |
|----------------|-----------|------------------|
| Off-invoice allowance | Deducted from invoice at time of payment | At invoice |
| Billback allowance | Earned over time, claimed via debit memo | Periodic (monthly/quarterly) |
| Volume rebate | Earned at annual purchase threshold | Annual settlement |
| Promotional allowance | Tied to specific promotional event | Post-event |
| Markdown allowance | Compensates retailer for markdown taken on vendor product | At markdown event |

**Deduction process** — All deductions must reference a specific PO, receipt, and compliance clause. Chargebacks without a traceable basis are commercially indefensible and create vendor disputes that cost more to resolve than the chargeback is worth.

## Consumers

The AP module generates debit memos from chargeback events and applies them at invoice settlement. The Vendor Agent records chargeback events in the vendor scorecard for trend analysis. The Operations Agent monitors chargeback volume by vendor and flags vendors where chargeback costs exceed a threshold of total purchase value (indicating a structurally unprofitable vendor relationship). The smart contract layer, for smart-contract-native vendors, encodes each chargeback type as a Solidity clause: threshold breach triggers automatic financial consequence with on-chain auditability.

## Invariants

- Every chargeback must trace to a documented compliance clause agreed at vendor setup. The matrix is enforced, not invented post-hoc.
- Occurrence escalation applies within a defined measurement period (typically 12 months rolling). Occurrence counts reset at period close.
- Chargeback rights survive vendor termination for events that occurred during the active relationship.

## Platform (2030)

**Agent mandate:** Operations Agent owns chargeback monitoring — it detects compliance failures in real time and generates chargeback events automatically. Business Agent reviews chargeback trends in negotiation preparation. Neither agent makes discretionary chargeback decisions; they enforce the matrix as defined.

**Smart contract as the chargeback engine.** The traditional chargeback process is: compliance failure occurs → someone notices → debit memo is generated → vendor disputes → finance resolves → net settlement weeks later. In the Canary Go smart contract model, the AVAX vendor subnet contract is the chargeback engine. Each chargeback type in the matrix is encoded as a Solidity clause with its trigger condition, fee schedule, and occurrence escalation logic. When a compliance event is submitted to the contract — a short shipment receipt, a late ASN, a failed carton scan — the contract evaluates it against the clause, computes the financial consequence, and records it as an immutable ledger entry. The retailer doesn't generate a debit memo. The vendor doesn't dispute whether the event happened. It's on-chain. The deduction is applied to the vendor's L402 wallet balance automatically at settlement.

**L402 wallet deductions.** Chargeback amounts are held as pending debits against the vendor's L402 wallet. At invoice settlement, the wallet balance (invoice amount minus pending debits) determines the net payment. For lightning-settled vendors, the net payment is a Lightning transaction for the balance amount. No AP human intervention required for matched, contract-covered chargebacks. Human review is only for disputes about whether the compliance clause itself was correctly configured.

**Occurrence escalation in real time.** The contract tracks occurrence count within the rolling measurement period. The escalation tier changes automatically when occurrence thresholds are crossed — no manual tracking, no end-of-period calculation that surprises the vendor. The vendor can query their own contract state at any time to see their current occurrence count and pending deductions.

**Exception surfacing.** Operations Agent surfaces: (1) vendors where chargeback rate as % of purchases is rising quarter-over-quarter — rationalization signal; (2) chargeback types where the deduction is being disputed at high frequency — contract clause ambiguity signal; (3) vendors where chargeback deductions have exceeded invoice value — operational breakdown signal requiring immediate escalation.

**MCP surface.** `chargeback_balance(vendor_id)` returns pending deductions by type. `chargeback_history(vendor_id, period)` returns occurrence counts by clause. `chargeback_rate(vendor_id)` returns deduction as % of purchase value — the primary rationalization input. Single-call, low-token, agent-readable.

**RaaS.** Each chargeback event — issuance, vendor response, dispute, resolution, credit — is a sequenced receipt-class financial event. The chargeback chain must be traceable from the originating receipt event (the delivery or invoice that triggered the violation) through to final credit. Resolution credits are new events against the chargeback record, not overwrites. `chargeback_status(vendor_id)` indexed on (vendor_id, status, created_at); dispute timeline queries must resolve without full-scan. Chargeback history exportable for AP audit and vendor negotiation; the event log is the evidentiary record in any vendor dispute.

## Related

- [[retail-vendor-compliance-standards]] — the clause definitions that chargebacks enforce
- [[retail-vendor-scorecard]] — the performance data that triggers occurrence thresholds
- [[retail-three-way-match]] — the receipt-side data source for short shipment and ASN chargebacks
- [[retail-ap-vendor-terms]] — the AP settlement process that executes chargeback deductions

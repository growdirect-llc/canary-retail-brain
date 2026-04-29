---
card-type: domain-module
card-id: retail-receiving-disposition
card-version: 2
domain: merchandising
layer: domain
status: approved
feeds: [retail-three-way-match, retail-chargeback-matrix, retail-inventory-valuation-mac]
receives: [retail-vendor-compliance-standards, retail-purchase-order-model]
tags: [receiving, disposition, RTV, defective, return-to-vendor, damage, reason-codes, smart-contract]
last-compiled: 2026-04-29
---

## What this is

The receiving disposition model: the reason-code taxonomy, disposition matrix, and automatic transaction triggers that govern what happens to product when it arrives in unacceptable condition or fails the three-way match.

## Purpose

When received product is damaged, defective, recalled, mis-packaged, or otherwise unacceptable, the retailer must make an immediate disposition decision that affects inventory, vendor liability, and financial accounting simultaneously. The disposition model pre-defines that decision by vendor, item, reason code, and date range — removing discretion from the receiving dock and ensuring consistent, audit-trailed handling. This model is a prerequisite for smart contract encoding of vendor liability at receipt.

## Structure

**Reason codes** — Every product removal or receiving exception requires a reason code that classifies the problem. Standard reason codes include:

- Customer return — damaged
- Customer return — dissatisfied
- DC damage (occurred in distribution center)
- Vendor damage (arrived damaged)
- Store damage
- Known theft
- Mis-packaged (wrong item in carton)
- Discontinued (item no longer carried)
- Hazardous recall (do not sell under any circumstances)
- Voluntary recall
- Outdated / expired
- Short shipment (physical count below ASN)

**Disposition types** — Each reason code maps to an allowed set of dispositions. A disposition dictates the financial transaction, the physical handling instruction, and the vendor notification:

| Disposition | Financial effect | Physical instruction |
|-------------|-----------------|---------------------|
| RTV — direct to vendor | Creates vendor return order; credit expected | Ship product to vendor |
| RTV — through DC | Creates stock transport to DC; DC initiates return | Transfer to DC for consolidation |
| RTV — through consolidator | Creates order to consolidator | Transfer to third-party consolidator |
| Defective allowance — markdown | Markdown applied; vendor provides credit | Sell at reduced price |
| Defective allowance — destroy/donate | Allowance claimed; product disposed | Destroy or donate product |
| Transfer to scrap | No vendor credit; internal loss | Destroy product |
| Not allowed | Blocks removal attempt | Escalate to buyer |

**Disposition matrix** — The allowed dispositions for a given combination of vendor × item × reason code × date range are maintained in vendor management. When a receiving exception is posted, the system reads the matrix and issues the correct disposition automatically. The receiving associate sees only the disposition instruction — they do not make the decision.

**Automatic transaction triggers** — Each disposition generates one or more downstream transactions automatically at posting:

- RTV Direct: standard return order with item, vendor, quantity, and agreed credit price populated
- RTV through DC: stock transport document to DC, RTV claim document to vendor
- Defective allowance: markdown or expense transaction to the appropriate G/L account
- Transfer to scrap: inventory adjustment to loss account with reason code preserved for shrink reporting

**Handling charge treatment** — Handling fees or administrative charges may be added to any removal transaction and allocated to a specific G/L account by reason code. These are defined in the chargeback matrix for vendor-caused dispositions.

## Consumers

The Receiving module posts the exception and reads the disposition matrix to issue the handling instruction. The Inventory module processes the adjustment or transfer transaction. The AP/Finance module processes the credit or deduction against the vendor account. The Vendor Agent records the disposition event in the vendor compliance history for scorecard inclusion. The smart contract layer, for smart-contract-native vendors, encodes disposition rights as on-chain obligations: a documented receiving failure triggers an automatic credit claim without manual dispute.

## Invariants

- Dispositions are determined by the matrix — not by the receiving associate or store manager. Manual disposition overrides require buyer authorization and audit log.
- Destruction of recalled product must be documented with a disposal record. Recalls require a hazardous recall flag on the item master that blocks any sale attempt at POS.
- The disposition matrix must be maintained in vendor management, not in a spreadsheet. Spreadsheet-driven disposition creates untraceable manual decisions.

## Platform (2030)

**Agent mandate:** Operations Agent monitors receiving exceptions in real time and validates that disposition decisions match the configured matrix. Technical Agent provisions the disposition matrix in the vendor smart contract at setup. Neither agent makes disposition decisions — the matrix decides; agents confirm and alert on overrides.

**Disposition matrix as smart contract logic.** In traditional systems, the disposition matrix is a database lookup: receiving system queries, displays the instruction. In the Canary Go model, the disposition matrix for smart-contract-native vendors is encoded as Solidity. When a receiving exception event is submitted with reason code and item attributes, the contract evaluates the matrix and returns the disposition instruction with an on-chain record. The retailer's claim to a vendor credit does not depend on an AP staff member generating a debit memo weeks later — the contract record IS the credit claim, with a verifiable timestamp and immutable audit trail.

**Automatic credit accrual.** When a disposition triggers a vendor credit claim (RTV, defective allowance), the contract records the pending credit against the vendor's L402 wallet as a receivable. At settlement, the credit offsets the vendor's payment — the retailer does not chase credits through a separate AP workflow. For destroy/donate dispositions, the contract records the allowance claim and computes the applicable chargeback rate automatically. The entire credit cycle from receiving exception to settlement becomes a chain of contract events with no manual handoffs.

**MCP surface.** `disposition_matrix(vendor_id, reason_code, item_id)` returns the applicable disposition for a given exception. `pending_credits(vendor_id)` returns open vendor credit claims with contract reference and aging. `disposition_exceptions(site_id, period)` returns receiving exceptions where human override was required — a compliance audit tool.

**RaaS.** Every DC receipt is a receipt event — quantity received, quality disposition, and vendor attribution captured exactly as they occurred. This is the chain-of-custody anchor for inventory and financial records; a receipt event that is wrong or out of sequence corrupts MAC, replenishment, and the three-way match simultaneously. Receipt events must be sequenced before MAC updates, before replenishment adjustments, and before match events. `disposition_matrix(vendor_id, reason_code, item_id)` resolves from Valkey hot cache or indexed SQL in sub-50ms to support DC throughput. Receipt records are append-only; ASN data feeds from vendor as pre-receipt events. Receipt history exportable for customs (import), AP audit, and inventory reconciliation.

## Related

- [[retail-three-way-match]] — the match failure that triggers a receiving disposition event
- [[retail-vendor-compliance-standards]] — the vendor-specific agreements that define what's expected
- [[retail-chargeback-matrix]] — the fee structure applied when vendor damage causes a disposition
- [[retail-inventory-valuation-mac]] — MAC adjustments triggered by disposal and defective allowance transactions

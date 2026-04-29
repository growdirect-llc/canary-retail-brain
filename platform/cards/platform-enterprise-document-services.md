---
card-type: platform-thesis
card-id: platform-enterprise-document-services
card-version: 1
domain: platform
layer: cross-cutting
status: approved
agent: ALX
tags: [EDS, enterprise-document-services, RaaS, SKUaaS, POaaS, ASNaaS, IaaS, InvaaS, MDM, as-a-service, data-integrity, hash-chain, smart-contract, MCP, namespace, retail-spine]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

The Enterprise Document Services (EDS) architecture: the principle that every key retail enterprise document and MDM record is treated as a first-class, hash-chained, MCP-queryable service — not a mutable database row. Receipt as a Service (RaaS) is the first and foundational instance. The same pattern applies uniformly across the retail spine: SKU, Vendor, Site, PO, ASN, Invoice, Inventory, Hierarchy — each is a service that any party can call to retrieve the canonical, verifiable state of that document.

## Purpose

Retail enterprise systems have always treated their core documents — the purchase order, the invoice, the receipt, the inventory position — as internal database records. The retailer asserts what these records say; counterparties (vendors, lenders, insurers, auditors, regulators) have to take their word for it or perform expensive independent verification. This creates friction, dispute, and information asymmetry at every boundary in the retail ecosystem.

The EDS architecture eliminates the assertion. Every core retail document is a verified service call. The PO is not a number on a spreadsheet — it is a hash-chained record that any authorised party can call and receive back with a cryptographic proof of its state. The inventory position is not a number in a WMS — it is a live, hash-verified service call derived from the sequence of receipt events that produced it. The invoice match is not an approval in an AP queue — it is a verified event that a smart contract can consume to release payment without human intermediation.

This is what makes the platform a genuine infrastructure play rather than another SaaS application. SaaS sells access to a database. EDS sells trust in a document. Those are different businesses with different moats.

## The service family

Each service in the family shares the same structural properties: it is namespace-resolved under `raas:{merchant_id}`, it returns a canonical document with its hash and sequence position, it is backed by an append-only event log, and it exposes a smart-contract-consumable interface. The specific content of each service is determined by its document type.

**Receipt as a Service (RaaS)** — The foundational service. Every POS transaction, DC receipt, and financial settlement event is a receipt. The receipt hash is the unit of trust — the proof that a specific transaction occurred at a specific time with a specific receiver. Return policy enforcement, chargeback authorisation, and payment gating all consume receipt hashes. See [[raas-receipt-as-a-service]].

**SKU as a Service (SKUaaS)** — The item master as a verified service. Any party — vendor, buyer, space planner, POS system, replenishment agent — calls `sku(item_id)` and receives back the canonical item record: UPC, hierarchy placement, all units of measure with dimensions and weights, country of origin, status, and the hash of the current record state. Item master changes are sequenced events; the SKU's state at any prior date is reconstructible. Vendors can verify that the item they are shipping against matches the item the retailer has on file — without a phone call. Planogram systems can verify item dimensions before building a shelf layout. Smart contracts can verify item eligibility before a PO is generated.

**Vendor as a Service (VaaS)** — The vendor master as a verified service. `vendor(vendor_id)` returns the canonical vendor record: legal entity name, remittance address, payment terms, compliance status, and current scorecard — all with hash-verified state. Vendor status changes are sequenced events. A payment contract that needs to verify vendor bank details before releasing funds calls VaaS — not a human-maintained spreadsheet. A chargeback contract that needs to verify compliance clause applicability calls VaaS. Counterparty verification without manual lookup.

**Site as a Service (SiteaaS)** — The store master as a verified service. `site(site_id)` returns the canonical site record: format, cluster, regulatory zone, fixture configuration, and operational status. Site configuration changes are sequenced events. A regulatory compliance check calls SiteaaS to determine which restrictions apply at a given location — it does not read a spreadsheet. A planogram system calls SiteaaS to get fixture dimensions before building a shelf layout. A lender assessing store-level performance calls SiteaaS to verify the site count and format mix they are underwriting against.

**PO as a Service (POaaS)** — The purchase order as a verified service. `po(po_id)` returns the canonical PO record: line items, quantities, agreed costs, vendor, ship window, and current status — with the hash of the PO at the time it was transmitted to the vendor. PO amendments are sequenced events; the PO's state at any prior point is reconstructible. A three-way match contract calls POaaS to get the authorised PO state before verifying the invoice. A vendor calls POaaS to confirm the order they received matches the system of record — before manufacturing. An auditor calls POaaS to verify that the cost on the invoice matches the cost the buyer agreed to.

**ASN as a Service (ASNaaS)** — The advance ship notice as a verified service. `asn(asn_id)` returns the canonical ASN: items shipped, quantities, packing configuration, carrier details, and expected arrival. The ASN is the vendor's assertion of what they shipped; ASNaaS makes that assertion hash-verified. When goods arrive at the DC, the receiving event is compared against the ASN hash — discrepancies are receipt events in their own right. A three-way match contract consumes the ASN hash alongside the PO hash and the invoice hash. An import customs entry references the ASN hash as the bill of lading surrogate in the RaaS model.

**Invoice as a Service (IaaS)** — The vendor invoice as a verified service. `invoice(invoice_id)` returns the canonical invoice: line items, amounts, payment terms, and the hash of the invoice as submitted. The invoice cannot be altered after submission — amendments are new invoices referencing the original. The three-way match contract consumes the invoice hash. Early payment discount eligibility is verified against the invoice receipt timestamp — a field that is hash-anchored and cannot be retroactively adjusted to claim a discount window that has passed.

**Inventory as a Service (InvaaS)** — The inventory position as a verified service. `inventory(item_id, site_id)` returns the current on-hand position with the hash of the last receipt event that produced it. The inventory position is not stored as a number — it is derived from the sequence of receipt events (purchases received, sales sold, adjustments made) that produced it. This means the inventory position is auditable: any party can verify that the stated position is consistent with the receipt event history. A lender assessing inventory as collateral calls InvaaS — they receive a position backed by a hash-verified event sequence, not a self-reported number. An insurer assessing a loss claim calls InvaaS to verify the inventory that was present at the time of the loss event.

**Hierarchy as a Service (HaaS)** — The merchandise hierarchy as a versioned, verified service. `hierarchy(item_id, as_of_date)` returns the hierarchy placement of an item at a specific point in time. Hierarchy changes are sequenced events; the hierarchy version in effect at any prior date is reconstructible. This is required for historical reporting across hierarchy restructurings: a category that was split six months ago must be reportable in its prior unified form for year-over-year comparison.

## The convergence: three-way match as smart contract

The three-way match is where POaaS, ASNaaS, and IaaS converge. The match contract takes three inputs: the PO hash, the ASN hash, and the invoice hash. It verifies that all three exist in the hash chain, reference the same PO number, and that the quantities and costs align within tolerance. If all three verify, the contract releases payment. No human approval. No dispute about whether the goods were received — the ASN hash proves it. No dispute about whether the cost matches — the PO hash proves it. No dispute about whether the invoice was received — the IaaS timestamp proves it.

This eliminates the largest source of AP friction in retail: the invoice exception. Invoice exceptions exist because PO cost, received quantity, and invoice amount don't match — and resolving them requires human investigation across three systems. When all three documents are hash-verified services, the contract resolves the match mechanically and surfaces only genuine exceptions (where the documents genuinely disagree) rather than data entry discrepancies.

## Shared architectural principles

Every service in the EDS family implements the same data integrity principles:

- **Append-only event log.** Documents are never overwritten. Amendments are new events referencing the original. The original is permanent.
- **Hash-chained sequence.** Each event's hash includes the prior event's hash within the document's lifecycle. The chain is tamper-evident.
- **Receiver attribution.** Every event carries the identity of the party that created or accepted it. Attribution is not optional.
- **Namespace-resolved.** Every document is addressable under `raas:{merchant_id}:{service}:{document_id}`. The namespace persists across POS changes and system migrations.
- **Point-in-time reconstructible.** The state of any document at any prior date is derivable from the event sequence. No state is stored only as current value.
- **Smart-contract consumable.** Every service returns a hash that a smart contract can verify. The contract does not need to trust the service — it verifies the hash independently.
- **Portable.** Every document's event log is exportable in a format that any party can independently verify. The hash chain is the portability standard.

## Competitive position

SaaS: sells access to a database. The merchant asserts what the database says.

EDS: sells trust in a document. Any authorised counterparty can verify the document's state without trusting the merchant or the platform.

No enterprise retail software vendor currently offers hash-verified, smart-contract-consumable retail document services as a unified platform primitive. The incumbents (SAP, Oracle Retail, Blue Yonder) are database-of-record vendors. They assert. They do not verify. The EDS architecture makes verification a platform capability, not an audit engagement.

## MCP surface

Each service exposes a consistent MCP interface:
- `{service}(id)` — returns current canonical document state with hash and sequence position
- `{service}_history(id, from_ts, to_ts)` — returns the ordered event sequence over a time range
- `{service}_verify(hash)` — verifies that a hash exists in the chain and returns its position
- `{service}_as_of(id, date)` — returns the document state as of a specific date (point-in-time reconstruction)

## Related

- [[raas-receipt-as-a-service]] — the foundational EDS service; the pattern all others follow
- [[infra-l402-otb-settlement]] — OTB as an L402 wallet is itself an EDS service (OTB as a Service)
- [[infra-blockchain-evidence-anchor]] — the L1/L2 anchoring layer that makes EDS hashes externally verifiable
- [[retail-three-way-match]] — the convergence point where POaaS, ASNaaS, and IaaS meet
- [[retail-inventory-valuation-mac]] — InvaaS derives its position from the MAC event sequence
- [[retail-vendor-lifecycle]] — VaaS draws from the vendor lifecycle event log

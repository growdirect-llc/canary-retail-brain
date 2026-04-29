---
card-type: domain-module
card-id: retail-purchase-order-model
card-version: 2
domain: merchandising
layer: domain
status: approved
feeds: [retail-three-way-match, retail-receiving-disposition, retail-vendor-scorecard]
receives: [retail-merchandise-financial-planning, retail-replenishment-model, retail-vendor-lifecycle]
tags: [purchase-order, PO, ASN, advance-ship-notice, OTB, vendor-acknowledgment, EDI, receiving]
last-compiled: 2026-04-29
---

## What this is

The purchase order management model: PO creation, vendor communication, ASN receipt, open-order tracking, and the lifecycle of a purchase commitment from initiation through receipt.

## Purpose

Purchase order management ensures continuous product supply by tracking commitments from order placement through delivery. The PO is the legal commitment that triggers vendor performance obligations, opens the chargeback window, and initiates the three-way match at receipt. Without rigorous PO management, inventory accuracy, vendor accountability, and financial reconciliation all degrade.

## Structure

**PO creation** — Purchase orders are created from three sources: replenishment-generated suggested orders, buyer-initiated direct orders, and allocation-driven store distribution orders. Key PO data elements: vendor, items (with UPC), ordered quantities in eaches, cost per unit (including all applicable allowances), delivery-to location(s), requested delivery date, and ship-not-before/ship-not-after window.

OTB (Open-to-Buy) gates PO creation at the buyer level. A PO that would exceed planned OTB requires authorization override. The OTB check is a hard gate, not a soft warning, for planned purchases; buyers may set soft or hard warnings depending on business rules.

A single PO may have multiple ship-to locations (e.g., direct store delivery to five stores on one truck), enabling vendor consolidation at the purchase commitment level.

**Vendor acknowledgment** — For EDI-capable vendors, the 855 PO acknowledgment confirms vendor acceptance, any item substitutions, and confirmed ship dates. Non-EDI vendors are not required to provide formal acknowledgment. Discrepancy standards for acknowledgment (acceptable date variance, quantity variance) are maintained in vendor management.

**ASN management** — The 856 Advance Ship Notice is the vendor's electronic declaration of what was shipped, in what carton configuration, and when it left the facility. ASN data drives receiving efficiency: the system can pre-stage expected receipts, validate carton contents against the ASN at scan, and detect discrepancies before the physical count is complete. ASN accuracy is a scored vendor compliance dimension.

**Open order tracking** — All open POs are monitored against planned receipt dates. An exception-based view surfaces: orders past their ship-not-after date without an ASN, orders with confirmed ASNs not yet received, and orders with quantities diverging from acknowledgment by more than the defined tolerance.

**PO maintenance** — Quantity, cost, and date changes to open POs require buyer authorization. Changes initiated by the vendor enter through vendor management, not directly into the PO. All changes are version-controlled and audit-trailed.

**PO communication** — POs are transmitted to vendors via EDI 850. Non-EDI vendors receive POs via email or portal. Partners (freight brokers, mixing centers, shipping lines) may also receive PO data when relevant to logistics coordination.

## Consumers

The Replenishment module generates suggested orders that become POs. The Receiving module reads open PO data to validate inbound shipments. The Finance module reads PO cost data for three-way match at invoice. The Vendor Agent updates open PO status when ASNs arrive. The Operations Agent monitors open PO age and surfaces exception reports.

## Invariants

- All external interface feeds (UPC database, vendor pricing) must be validated before a PO is created. A PO with bad item or cost data corrupts the entire downstream chain.
- Base order quantities are in eaches/units. Mixed units of measure are not permitted on a single PO line.
- Vendor PO changes are routed through vendor management — buyers do not accept verbal change requests directly into the PO system.

## Platform (2030)

**Agent mandate:** Operations Agent monitors open PO exceptions — past-window orders, unmatched ASNs, OTB overruns — continuously and surfaces them to the merchant. Business Agent uses open PO data for vendor conversation preparation. Technical Agent provisions EDI endpoints and vendor MCP credentials at onboarding. No agent auto-creates POs above OTB without merchant authorization.

**OTB gate as L402 wallet check.** Traditional OTB gating compares a planned field in the merchandise system. In the Canary Go model, the OTB gate is a cryptographic wallet check: before a PO is committed, the system calls `otb_balance(dept, period)` and compares PO cost to available L402 wallet balance. If insufficient, the PO is blocked — no override without a signed wallet increment authorization. This creates an unbreakable audit trail: every PO was either within OTB at creation or has an attached authorization record explaining the exception.

**PO as smart contract event.** When a PO is issued to a smart-contract-native vendor, the PO emission is also a contract event on the AVAX vendor subnet. The contract records the PO, its terms, and the compliance obligations that apply to this order. When the ASN arrives, the contract validates it against the PO. When the receipt is posted, the contract computes the match. The traditional cycle — PO → email → ship → receive → match → settle — compresses to: PO event → ASN event → receipt event → automatic settlement signal. No disputes about what was ordered, because it's on-chain.

**MCP surface.** `open_orders(vendor_id)` returns open POs with age, ASN status, and expected receipt date. `otb_balance(dept, period)` returns available OTB before PO creation. `po_exceptions()` returns POs past ship-not-after date, ASN-less, or OTB-breached. Agent-readable, single-call.

**RaaS.** PO creation, amendment, and receipt confirmation are sequenced receipt-class commitment events. OTB is the L402 wallet balance; the OTB decrement on PO creation must be sequenced before any subsequent OTB query sees the updated balance — a race condition here produces double-spend on the OTB bucket. `open_orders(vendor_id)` resolves from indexed SQL on (vendor_id, status); `otb_balance(dept, period)` from Valkey hot cache (sub-100ms, called before every PO creation). PO records are append-only; amendments are new events referencing the original PO. PO history exportable for AP reconciliation, receiving, and customs (import POs).

## Related

- [[retail-merchandise-financial-planning]] — OTB that gates PO creation
- [[retail-replenishment-model]] — the demand-driven source of suggested orders
- [[retail-three-way-match]] — what happens when the ordered goods arrive
- [[retail-vendor-compliance-standards]] — the compliance obligations this PO activates

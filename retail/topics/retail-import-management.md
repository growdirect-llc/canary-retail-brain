---
card-type: domain-module
card-id: retail-import-management
card-version: 1
domain: merchandising
layer: domain
status: approved
agent: ALX
feeds: [retail-purchase-order-model, retail-inventory-valuation-mac, retail-three-way-match]
receives: [retail-vendor-lifecycle, retail-merchandise-hierarchy]
tags: [import, international-sourcing, letter-of-credit, customs, landed-cost, HTS, trade-management, RTM, obligations]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

The import management model: the end-to-end process for internationally sourced merchandise, from purchase order through customs clearance to actual landed cost calculation — including letter of credit management, harmonized tariff schedule compliance, transportation tracking, and obligations management.

## Purpose

Import purchasing introduces a layer of complexity that domestic PO management does not address: currency risk, letter of credit obligations, customs classification, customs entry, port handling, and a landed cost that is only fully known after the goods clear customs. A retailer that sources 20% of its product internationally but manages import orders through the same process as domestic orders will systematically misstate its cost basis, miss customs obligations, and lose financial visibility between PO issuance and DC receipt. Import management exists as a distinct process because the data model, the parties, and the financial obligations are fundamentally different.

## Structure

**Harmonized Tariff Schedule (HTS)** — Every imported item must be classified under the Harmonized Tariff Schedule, which determines the duty rate assessed at customs. HTS codes are maintained at the item level. Classification errors — wrong HTS code on an import PO — result in either overpayment of duties (cost impact) or underpayment (compliance risk). HTS maintenance must be current: tariff schedules change, and country-specific duty rates are subject to trade agreements and trade actions.

**Letter of credit (LC)** — For import vendors requiring payment security, the retailer's bank issues a letter of credit in favor of the vendor's bank. The LC specifies: the purchase order amount, required shipping documents (commercial invoice, packing list, bill of lading, certificate of origin), the shipment window (ship-not-before/ship-not-after at the port of origin), and the expiry date. The vendor presents compliant documents to their bank to draw on the LC. LC management tracks: open LCs by vendor and PO, document presentation deadlines, amendment history, and LC expiry. An expired LC on an open order is a procurement failure.

**Transportation** — Import transportation involves multiple legs and parties: inland transportation at origin (factory to port), ocean or air freight (origin port to destination port), port handling and customs at destination, and inland transportation (port to DC). Transportation tracking maintains: booking confirmations, vessel/flight details, estimated and actual arrival dates, and bill of lading data. Transportation data feeds the expected receipt timeline for open order tracking and the freight cost allocation that becomes part of MAC.

**Customs entry** — When goods arrive at the destination port, a customs entry must be filed with the relevant customs authority (CBP in the US). The entry specifies: importer of record, HTS classification per line item, country of origin, dutiable value (typically the transaction value on the commercial invoice), and applicable duty rates. Customs entry management tracks: entry numbers, entry status (filed, liquidated, protest filed), duty amounts assessed, and any custom holds or examination orders. The entry must be filed within the required timeframe from vessel arrival — late filing incurs penalties.

**Obligations** — Import obligations are the financial commitments outstanding at any point in the import lifecycle: LC obligations (open letter of credit amounts not yet drawn), duty obligations (estimated duties on goods in transit not yet entered), and freight obligations (committed freight costs for shipments in transit). Obligations provide the financial visibility into import inventory cost that has not yet landed — the "in-transit inventory value" that accrues between shipment and DC receipt.

**Actual landed cost** — Landed cost is the total cost to get an imported unit to the DC: vendor invoice cost + duties + freight + port handling + insurance + origin inland freight. Landed cost is only fully calculable after customs entry is liquidated. The process maintains an estimated landed cost (used to initialize MAC at receipt) and reconciles to actual landed cost when all cost components are confirmed. The MAC update process treats freight variance settlement the same whether the freight is domestic or international.

## Consumers

The AP/Finance module uses LC data to manage bank obligations and duty payment. The Inventory module uses estimated landed cost to initialize MAC at DC receipt. The Vendor Agent tracks open LC status as part of the vendor relationship record. The Operations Agent monitors import pipeline health: LCs approaching expiry on open POs, shipments overdue at port, customs entries with open examination holds, and obligations balance as a working capital indicator.

## Invariants

- Every import PO line must have an HTS code before the PO is transmitted to the vendor. An import PO without HTS codes cannot be entered at customs.
- LC expiry dates must be monitored against the ship-not-after date on the PO. An LC that expires before the vendor ships is a procurement failure that requires bank amendment or new LC issuance.
- Estimated landed cost must be updated when actual freight and duty are known. Using the original estimate indefinitely produces a permanently incorrect MAC for imported items.

## Platform (2030)

**Agent mandate:** Business Agent owns import sourcing decisions — vendor selection, LC terms negotiation, and country-of-origin strategy. Technical Agent manages the import data pipeline: HTS code maintenance, LC data synchronization with the bank's trade finance system, and customs entry status feeds from the broker. Operations Agent monitors import pipeline exceptions continuously: LCs expiring within 14 days on open POs, shipments overdue against vessel ETA, customs entries with holds, and obligations balance trending as a working capital signal.

**Smart contract for LC obligations.** A letter of credit is already a structured financial instrument with defined trigger conditions — it is the closest analog to a smart contract in traditional trade finance. The Canary Go model maps LC mechanics to AVAX vendor subnet contract events: PO issuance creates an obligation event with the LC amount, required document set, and expiry date. When the vendor submits shipping documents (as a contract event with document hash references), the contract validates the document set against the LC terms. Compliant presentation triggers the payment signal. The vendor does not wait for a bank to process paper — the contract state machine evaluates compliance and releases payment. For vendors in jurisdictions where blockchain-native LC settlement has regulatory recognition, this eliminates the traditional 5–7 day document processing window.

**Actual landed cost via smart contract settlement.** Freight carriers and customs brokers enrolled in the Canary Go network submit actual cost components as contract events: the freight invoice as an event referencing the bill of lading, the duty assessment as an event referencing the customs entry number. When all components are posted, the contract computes actual landed cost and emits a MAC adjustment event. The MAC update workflow receives a verifiable, on-chain cost basis — not a spreadsheet from the logistics team.

**MCP surface.** `lc_status(vendor_id)` returns open LCs with expiry dates, document status, and PO references. `import_pipeline(period)` returns shipments in transit with ETA, customs entry status, and estimated landed cost. `obligations_balance(period)` returns total in-transit financial obligations by category (LC, duty, freight). `landed_cost(po_id)` returns estimated vs. actual landed cost and reconciliation status. Single-call, agent-readable.

**RaaS.** Import lifecycle events — PO issuance, LC issuance, shipment booking, customs entry filing, customs liquidation, landed cost settlement — are sequenced receipt-class records. The chain from purchase order to actual landed cost must be traceable event by event; an estimated cost that is not reconciled to actual after customs liquidation is a permanent error in MAC. Landed cost settlement events must be sequenced after customs liquidation — out-of-order settlement produces incorrect cost basis. `import_pipeline(period)` from SQL indexed on (vessel_eta, customs_status); `landed_cost(po_id)` from SQL with joined cost components. Import lifecycle records append-only; obligations balance computable from open events without full-scan. Import data exportable for customs broker, bank (LC reconciliation), AP, and financial audit.

## Related

- [[retail-purchase-order-model]] — import POs are a specialized PO type with additional data requirements
- [[retail-inventory-valuation-mac]] — actual landed cost is the cost basis that updates MAC at import receipt
- [[retail-three-way-match]] — import receipts flow through the same match process; ASN is the customs entry data
- [[retail-vendor-lifecycle]] — import vendor setup includes HTS registration and LC term negotiation
- [[retail-ap-vendor-terms]] — duty payment and freight settlement are subsequent cost adjustments that flow through AP

---
card-type: infra-capability
card-id: raas-receipt-as-a-service
card-version: 1
domain: platform
layer: infra
status: approved
feeds: [retail-sales-audit, retail-inventory-valuation-mac, retail-three-way-match, retail-operations-kpis, retail-chargeback-matrix]
receives: [retail-sales-audit]
tags: [RaaS, receipt-as-a-service, TSP, namespace, data-integrity, hashing, sequence-preservation, smart-contract, return-policy, blockchain, POS, receipt-hash, chain-of-custody]
last-compiled: 2026-04-29
---

## What this is

Receipt as a Service (RaaS): the platform layer that captures, sequences, hashes, and makes verifiable every receipt event that moves through the system — from POS transaction through DC receipt through invoice match through payment settlement. Any POS hits the service; the service returns the receipt. The receipt is not a PDF. It is a cryptographically hashed, sequenced record of what happened, who was involved, and when — anchored such that neither the merchant nor the platform can alter it after the fact.

## Purpose

The receipt is the most important document in retail. It is simultaneously the sales record, the inventory trigger, the payment authorisation, the return eligibility determination, the tax event, and the chain-of-custody anchor for every downstream analytical and financial process. Yet in traditional retail systems the receipt is a mutable row in a POS database, a printed slip that gets lost, and a parameter file that a store manager can override.

RaaS exists because the receipt should be a first-class data primitive — immutable, sequenced, hashed, and queryable — not a printed artifact. Every problem in retail operations that traces back to "we don't know exactly what happened at that register at that time" is a receipt integrity failure. RaaS is the technical answer to that class of failure.

This is also a genuine blockchain application with real-world commercial value — not speculation. The hash anchoring of receipt events provides cryptographic proof of what occurred at a POS, when, and to whom. This proof is commercially valuable to insurers, lenders, auditors, regulators, vendors processing returns, and any counterparty that needs to verify a claim about a transaction without taking the merchant's word for it.

## Structure

**The receipt event model.** Every meaningful event in the retail data flow is a receipt event: a POS sale, a return, a void, a DC receiving confirmation, a three-way match, a vendor payment, a planogram change, an inventory adjustment. Each event carries: a timestamp (UTC, millisecond precision), a sequence number within the merchant's event stream, a payload hash (SHA-256 of the canonical JSON representation of the event), a receiver identifier (who or what processed the event — cashier ID, DC dock door, agent ID), and a reference to the prior event hash (forming a hash chain within the stream).

**Sequence preservation.** Events must be processed in the order they occurred. An out-of-sequence event — a payment before a receipt, a receipt before a PO, a return before a sale — is not just a data quality problem; it is a financial control failure. The RaaS pipeline enforces event ordering within each merchant's namespace. The TSP (Transaction Sub-Pipeline) is the ingestion layer; `normalize_payload()` canonicalises source-specific identifiers to internal UUIDs before the event enters the hash chain, preserving the original source identifier as `_source_merchant_id` for audit.

**Payload hashing and the hash chain.** Each event is hashed after normalisation. The hash includes the payload, the timestamp, the sequence number, and the hash of the immediately preceding event — creating a chain where any alteration of a past event invalidates every subsequent hash. The chain cannot be silently corrupted; tampering is detectable by any party that holds a copy of any hash in the chain. The receipt hash is the unit of trust in the RaaS model.

**Receiver details.** The receiver — the party that processed or accepted the event — is a first-class field on every receipt event. For a POS transaction: the cashier ID, register ID, and site ID. For a DC receipt: the dock door, receiver employee ID, and PO reference. For an invoice match: the agent or user that approved the match. Receiver details make the event attributable — not just "this happened" but "this person or agent made this happen at this location at this time." Attribution is the foundation of accountability, loss prevention investigation, and vendor dispute resolution.

**Namespace resolution and MCP key construction.** The `raas:{merchant_id}` namespace is the token that ties all receipt events for a merchant across POS systems, store locations, and time. A merchant that switches POS systems does not lose their receipt history — the namespace persists; only the source connection changes. Multi-location chains have one namespace GUID with multiple site aliases. The namespace is the merchant's permanent identity in the receipt chain.

The namespace is also the mechanical foundation of the MCP surface. Every cache key, every event log entry, and every smart contract call is namespaced. The TSP's `normalize_payload()` function canonicalises all source-system identifiers (POS terminal IDs, vendor-assigned item codes, legacy site numbers) to internal UUIDs before the event enters the hash chain — but preserves the original source identifier as `_source_merchant_id` for audit and portability. The `build_key()` function constructs the Valkey cache key in the form `raas:{merchant_id}:{domain}:{entity_id}` — the same structure across every EDS service (RaaS, SKUaaS, POaaS, InvaaS, and the rest of the document service family). Any MCP call resolves through this namespace first: `resolve_namespace(merchant_id)` returns the canonical GUID and the list of active site aliases before any domain query proceeds. This means the MCP surface is portable — a lender, auditor, or vendor calling `receipt_hash(transaction_id)` against the API does not need to know which POS system generated the original transaction; the namespace layer handles the mapping. The receipt hash they receive back is verifiable against the chain regardless of the source system that produced it.

**The return policy smart contract.** A receipt hash is the eligibility proof for a return. In the traditional model, return policy enforcement depends on the cashier trusting the printed receipt and manually checking the date. In the RaaS model, the return policy is a smart contract. When a customer presents a receipt (or a receipt hash, or a merchant pulls the receipt by transaction ID), the contract evaluates: is this receipt in the verified hash chain? Is the return window still open? Is the item in a returnable category? Does the receiver (the store processing the return) have authority to accept this return type? The contract returns authorised or denied with a reason code — no cashier discretion, no receipt forgery, no return fraud on altered paper receipts. The return authorisation is itself a receipt event, sequenced and hashed into the chain. This is a direct commercial application: return fraud is a multi-billion dollar loss category in retail, and cryptographic receipt verification eliminates the paper-receipt forgery vector entirely.

**KPI integrity through receipt hashing.** Every KPI in the retail operations framework — gross margin, in-stock rate, shrink, fill rate, forecast accuracy — is computed from receipt events. The integrity of those KPIs is a direct function of receipt event integrity. A KPI computed from a tampered or incomplete receipt chain is wrong. A KPI computed from a verified hash chain is auditable: any counterparty (investor, lender, insurer, auditor) can verify that the KPI is derived from an unaltered event sequence. This converts merchant KPIs from self-reported numbers into cryptographically verifiable claims — a meaningful upgrade in trust for any merchant seeking financing, insurance, or partnership terms based on operating performance.

**Smart contract integration.** The smart contract layer (AVAX vendor subnet) consumes receipt hashes as contract inputs. A three-way match that triggers vendor payment does so by presenting the receipt hash of the DC receiving event, the PO event, and the invoice event to the payment contract — the contract verifies that all three hashes exist in the chain, in sequence, and that they reference the same PO. If the verification passes, payment is authorised. No human approval required. No invoice dispute about whether the goods were received — the receipt hash proves it. Chargeback deductions follow the same model: the chargeback contract takes the receipt hash of the violation event as its input; the vendor cannot dispute a chargeback that references a verified receipt hash they cannot alter.

## Data integrity principles

These principles apply uniformly across every module that generates or consumes receipt events:

- **Append-only.** Receipt events are never overwritten. Corrections are new events that reference the original. The original remains in the chain.
- **Sequence-enforced.** Events are processed in occurrence order. Out-of-sequence events are rejected or held for ordering before they enter the chain.
- **Hash-chained.** Each event's hash includes the prior event's hash. The chain is tamper-evident end-to-end.
- **Receiver-attributed.** Every event carries the identity of the party that processed it. Attribution is not optional.
- **Point-in-time reconstructible.** The state of any record (inventory position, vendor status, item authorization, OTB balance) at any prior point must be derivable from the event sequence. No state is stored only as current value.

## Performance and storage NFRs

The receipt chain imposes real requirements on storage architecture, query design, and caching strategy. These are not aspirational — they are constraints that flow from the volume and latency requirements of retail-scale event processing.

**Valkey hot cache.** Current state for high-frequency reads (MAC, OTB balance, item authorization, site config, SOQ parameters) lives in Valkey. Cache keys follow `raas:{merchant_id}:{domain}:{key}`. Cache is updated on receipt event processing; stale cache is a data integrity failure, not a performance issue.

**SQL append-only event log.** All receipt events land in SQL (PostgreSQL). The event log is the source of truth for point-in-time reconstruction, audit, and export. Indexes are on the access patterns that matter: (merchant_id, event_type, event_timestamp) for time-range queries; (entity_id, event_type) for entity history; (site_id, business_date) for store-level reporting. Ad hoc queries over historical event data must be scoped — unbounded full-table scans on a multi-year event log are not acceptable.

**Pre-aggregation.** KPIs, scorecards, event performance, space productivity, and forecast accuracy are all pre-aggregated views over the event log — they are not computed real-time from raw events. The pre-aggregation job runs on the verified event stream, not on raw POS data. This is what makes KPI latency (sub-200ms dashboard load) compatible with KPI accuracy (derived from the full audited event sequence).

**Portability.** The receipt event log must be exportable in a portable format. Merchants must be able to take their receipt history with them. The hash chain must be independently verifiable — an exported event log that cannot be verified against its own hashes is not portable, it is just a data dump.

## MCP surface

`receipt_hash(transaction_id)` returns the receipt hash, sequence number, and chain position for a specific transaction. `verify_chain(merchant_id, from_seq, to_seq)` verifies hash chain integrity over a sequence range — returns valid or the first broken link. `return_eligible(receipt_hash, item_id, return_date)` evaluates the return policy smart contract against a receipt hash — returns authorised/denied with reason code. `event_stream(merchant_id, event_type, from_ts, to_ts)` returns the ordered event sequence for a merchant over a time range — the portable export surface. `receiver_attribution(event_hash)` returns the receiver details attached to a specific event hash.

## Related

- [[retail-sales-audit]] — primary RaaS input: validated POS transactions enter the receipt chain at audit close
- [[retail-inventory-valuation-mac]] — MAC updates are triggered by receipt events; cost basis integrity depends on event sequence
- [[retail-three-way-match]] — the match event is the receipt hash gate for payment authorisation
- [[retail-chargeback-matrix]] — chargeback contracts consume receipt hashes as their evidentiary input
- [[retail-operations-kpis]] — all KPIs derive from the verified receipt event stream
- [[retail-item-authorization]] — authorization state changes are receipt-class events; the authorization at transaction time is reconstructible from the chain
- [[infra-blockchain-evidence-anchor]] — the L1/L2 anchoring layer that makes the hash chain externally verifiable

---
card-type: domain-module
card-id: retail-vendor-lifecycle
card-version: 2
domain: merchandising
layer: domain
status: approved
feeds: [retail-vendor-scorecard, retail-vendor-compliance-standards, retail-purchase-order-model, retail-chargeback-matrix]
tags: [vendor, supplier, lifecycle, onboarding, rationalization, discontinuation, retail-ops]
last-compiled: 2026-04-29
---

## What this is

The end-to-end lifecycle for a retail vendor relationship: from initial selection and setup through active partnership management to rationalization or discontinuation.

## Purpose

Vendor lifecycle management exists to maximize profit and sales through disciplined supplier relationships. The lifecycle governs which vendors the retailer commits to, what standards they must meet, how performance is measured, and under what conditions the relationship ends. Without a defined lifecycle, vendor sprawl accumulates, compliance gaps go unmeasured, and chargeback rights erode.

## Structure

The vendor lifecycle has seven stages:

**1. Select Vendor** — Evaluate candidates against a defined matrix: product quality, pricing, availability, RTV policy, carton and packing standards, routing and transportation compliance, EDI capability, co-op and rebate terms, and marketing support. Assign relative importance weights before any evaluation begins.

**2. Set Up Vendor** — Establish vendor master record with all terms, compliance standards, payment terms, and EDI parameters. Record agreed-upon compliance standards in vendor management, not informally. Vendor guidelines must cover accounting, traffic, store, and warehouse compliance.

**3. Define Vendor Guidelines** — Document the compliance standards that govern the ongoing relationship. These include: product quality acceptance criteria, availability commitments, net pricing terms, RTV policy, carton quality and marking standards, unit load specifications, transportation and routing requirements, discount and rebate schedules, co-op and marketing support, and shared forecast obligations. These are the clauses that chargebacks enforce.

**4. Evaluate Performance (Scorecard)** — Run the vendor scorecard by period (month, season, year). Dimensions cover all facets of the supply chain: fill rate, on-time delivery, ASN accuracy, EDI compliance, product quality, invoice accuracy, and RTV compliance. Performance feeds chargeback calculations and purchase allocation decisions.

**5. Negotiate** — Use scorecard data as the basis for commercial renegotiation. Buyers engage vendors with quantitative performance history. Terms, pricing, and compliance requirements are renegotiated on evidence, not relationship.

**6. Rationalize Vendors** — Periodically reduce the vendor base. Concentrate purchasing on a smaller set of high-performing strategic partners. Track vendor profitability — not just vendor revenue — as the rationalization criterion. Strategic partners receive forecast-sharing and preferred terms; commodity vendors are reduced or exited.

**7. Discontinue Vendor** — Execute a formal discontinuation process: close open POs, resolve outstanding chargebacks and credits, settle allowances, and archive the vendor record. Discontinuation criteria are defined in advance, not decided ad hoc.

## Consumers

The Vendor Agent uses lifecycle state to gate PO creation — a vendor in discontinuation cannot receive new orders. The Receiving module reads compliance standards to trigger chargebacks at receipt. The Finance module reads payment terms for AP settlement. The Operations Agent monitors scorecard health and flags vendors approaching rationalization thresholds.

## Invariants

- Vendor compliance standards must be recorded in vendor master, not in email or informal agreements. Chargebacks are only defensible if terms were documented at setup.
- Rationalization decisions must be driven by vendor profitability, not vendor revenue. A high-volume vendor with poor margins is a rationalization candidate.
- Scorecard dimensions and weighting factors must be established before evaluation begins — not reverse-engineered from a desired outcome.

## Platform (2030)

**Agent mandate:** Business Agent owns the vendor relationship layer — qualification scoring, scorecard review, negotiation preparation, rationalization recommendations. Operations Agent monitors lifecycle state and alerts on vendors approaching rationalization thresholds or with open compliance failures that have not been resolved. Technical Agent handles system-side vendor onboarding: provisioning vendor MCP credentials, configuring EDI endpoints, deploying the vendor's smart contract on the AVAX vendor subnet.

**Smart contract provisioning at setup.** In the traditional model, compliance standards are recorded in a database and enforced manually. In the Canary Go model, when a vendor's compliance standards are finalized, a smart contract is deployed on the AVAX vendor private subnet encoding those terms. The contract is the vendor agreement — not a PDF filed in a shared drive. Compliance events (receipt failures, ASN mismatches, late deliveries) are submitted to the contract as transactions. The contract computes the financial consequence automatically. The vendor sees the same contract state the retailer sees — no dispute about what was agreed.

**L402 wallet provisioned at activation.** Each active vendor relationship has an associated L402 wallet in the vendor wallet tier of the hierarchy. Vendor payments flow through this wallet. Chargeback deductions are applied to the wallet balance before settlement. The wallet balance at any point is the net amount owed to the vendor after all deductions — real-time, not at invoice date.

**Exception-based rationalization.** The Operations Agent does not wait for a periodic vendor review. It monitors vendor scorecard health continuously and surfaces rationalization candidates when: scorecard composite falls below threshold for two consecutive measurement periods, chargeback rate as a percentage of purchase value exceeds the defined ceiling, or vendor fill rate drops below the critical threshold for more than three consecutive weeks. The recommendation is queued to the merchant as an exception, not buried in a periodic report.

**MCP surface.** `vendor_status(vendor_id)` returns lifecycle stage, current scorecard composite, open compliance failures, and wallet balance in a single low-token call. `vendor_rationalization_queue()` returns the current list of vendors flagged for review with reason codes. Agents use these for planning without reading the full vendor record.

**RaaS.** Vendor lifecycle events — onboarding, status transitions, contract amendments — are sequenced receipt-class records. The vendor's status at the time of any PO, receipt, or payment must be reconstructible from the event log; a vendor that was suspended at the time of a shipment cannot be retroactively cleared. `vendor_status(vendor_id)` resolves from Valkey hot cache (sub-100ms); the underlying event log is SQL, append-only, indexed on (vendor_id, effective_date). Ad hoc queries over vendor history (all status changes for a vendor over 3 years for audit) must not full-scan — partial index on active vendors covers the common path. Vendor lifecycle history is exportable for AP audit, compliance review, and onboarding reconciliation.

## Related

- [[retail-vendor-compliance-standards]] — the compliance clause matrix this lifecycle enforces
- [[retail-vendor-scorecard]] — the performance measurement model used in stage 4
- [[retail-chargeback-matrix]] — the financial enforcement layer triggered by non-compliance
- [[retail-purchase-order-model]] — gated by vendor lifecycle state

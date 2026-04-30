---
title: The Vendor
classification: confidential
nav_order: 5

---

# The vendor

## Your view

You are a counterparty — to a buyer, to a receipt event, to an invoice match, to a payment.

The merchant you supply has Canary running their backoffice. The terms you negotiated with them are now machine-readable. The receipt events from the dock are hash-anchored. The invoices you submit clear or hold based on a contract evaluation, not a manual queue.

This page describes what changes for you and how to operate effectively against a Canary-running merchant.

## What changes

| Operation | Before Canary | With Canary |
|---|---|---|
| Receipt confirmation | Email exchange or portal upload | Receipt event posted to the chain at the dock; visible to you in real time |
| Three-way match | Manual reconciliation in the merchant's AP queue | Automatic match against PO + ASN + receipt hashes; payment releases on contract evaluation |
| Chargeback dispute | Email thread, attached PDFs, eventual resolution | Verifiable chain reference for the originating event; dispute on contract clause interpretation, not on whether the event happened |
| Scorecard | Periodic, opaque, surprise at quarter-end | Continuous, queryable by you in real time; you see your own performance the same way the merchant does |
| Co-op claim filing | Manual submission, paper trail | Automated based on attributable promotional events; settlement against your wallet |
| Forecast collaboration | Quarterly meeting | Real-time data exchange via the platform's collaborative forecast endpoint |

## What stays the same

Your product. Your delivery. Your relationship with the buyer. Your domain expertise.

The platform does not insert itself between you and the buyer. It mechanizes the event substrate that both parties have always agreed should be the source of truth — the actual receipt at the actual dock at the actual time, hash-anchored so neither party can dispute it after the fact.

## Where you have visibility

The platform exposes vendor-facing tools for the merchants you supply. With your authentication scope, you can call:

| Tool | Returns |
|---|---|
| `vendor_status(your_id)` | Your scorecard composite; active commitments; lifecycle stage |
| `pending_credits(your_id)` | Open chargebacks with originating event reference; dispute window status |
| `compliance_status(your_id)` | Your compliance rate per dimension (fill rate, on-time, ASN accuracy, etc.) |
| `coop_pipeline(your_id)` | Co-op accruals, claims filed, claims pending, deadlines approaching |
| `forecast_share(your_id)` | Forward demand forecast from the merchant (when collaborative forecasting is enabled by the merchant) |

These are read-only from your side. You do not write into the merchant's system; the merchant's events flow into your scorecard automatically.

## What disputes look like

Disputes about whether something happened do not exist when the receipt is hash-anchored. Disputes about how a contract clause is interpreted — what counts as on-time delivery, what counts as ASN accuracy, what triggers the volume rebate threshold — still happen.

The dispute mechanism is documented and bilateral. The merchant submits a dispute; you respond; if unresolved, the L&C agent (on the merchant side) escalates per the contract terms. The chain provides the evidence; the contract terms provide the interpretation.

## What this means for your business

For vendors who run a clean operation, Canary is a margin improvement: faster three-way clearance means you get paid sooner, fewer disputed deductions, lower chargeback exposure.

For vendors who rely on opaque deductions, missed dispute windows, or delayed three-way matching, Canary closes those windows. The merchant's AP cycle compresses; the dispute timer starts at the moment of the receipt event, not at invoice time.

The platform does not target vendors. It mechanizes the substrate. Vendors who deliver as agreed benefit; vendors who don't have less room to operate informally.

## Related

- [The merchant](merchant) — your counterparty
- [Why Canary](../why/why) — the platform's accountability framework that produces this vendor experience
- [The external party](external-party) — auditors and lenders who consume the same chain you transact against

---
card-type: domain-module
card-id: canary-commercial
card-version: 1
domain: finance
layer: domain
feeds:
  - canary-l402-otb
receives:
  - canary-identity
  - canary-receiving
  - canary-fox
tags: [commercial, vendor-finance, invoice, chargeback, rebate, edi-810, reconciliation]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: commercial

## What this is

Vendor relationship layer — invoice reconciliation, rebate accruals, chargebacks, and vendor-side deductions. Cross-references canary-receiving for the receipt side; closes the loop between physical goods received and financial obligations to vendors. Every chargeback records the underlying receipt or transfer variance as evidence.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9089` |
| Axis | B — Resource APIs |
| Tier mix | Reference (single invoice/rebate/chargeback reads) · Change-feed (filtered tails) · Stream (mutations, reconciliation triggers) · Daily batch (merchant-wide reconciliation runs) · Bulk window (EDI 810 batch import, reconciliation export) |
| Owned tables | `app.vendor_invoices`, `app.invoice_lines`, `app.chargebacks`, `app.rebate_accruals`, `app.reconciliation_runs` |
| Invoice match lifecycle | `SUBMITTED → MATCHING → MATCHED → APPROVED → PAID` with `DISPUTED → CHARGEBACK_ISSUED → RESOLVED` branch |

## Purpose

Variance-driven chargebacks: when invoice match finds a price/quantity/undelivered-line variance, `POST /commercial/chargebacks` records the disposition with link to the receipt evidence (`receipt_id`, `transfer_id`) and updates canary-receiving's PO state to RECONCILED with chargeback note.

## Dependencies

- canary-identity, canary-receiving (PO + receipt linkage)
- canary-fox (evidence on disputed invoices)
- canary-l402-otb (chargeback impact on OTB budget)

## Consumers

- canary-receiving (RECONCILED transition)
- canary-l402-otb (chargeback recovers OTB budget)
- Finance / AP teams (invoice processing)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-commercial
- Card: [[retail-chargeback-matrix]]
- Card: [[retail-ap-vendor-terms]]
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]], [[tier-daily-batch]], [[tier-bulk-window]]

---
card-type: domain-module
card-id: canary-receiving
card-version: 1
domain: merchandising
layer: domain
feeds:
  - canary-inventory
  - canary-commercial
  - canary-ildwac
receives:
  - canary-identity
  - canary-item
tags: [receiving, purchase-order, dsd, vendor-master, edi, po-lifecycle]
milestone: M4
status: approved
last-compiled: 2026-04-30
---

# Canary Service: receiving

## What this is

Owns purchase-order lifecycle and receiving events including direct-store-delivery (DSD) without prior PO, plus vendor master data. Cross-references canary-commercial for vendor-invoice reconciliation; cross-references canary-inventory for receipt-driven position increments.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:8092` |
| Axis | B — Resource APIs |
| Tier mix | Reference (PO/receipt/vendor lookups) · Change-feed (filtered lists) · Stream (lifecycle mutations) · Bulk window (EDI 810, PO bulk imports) |
| Owned tables | `app.purchase_orders`, `app.po_lines`, `app.receipts`, `app.receipt_lines`, `app.receipt_variances`, `app.vendors` |
| PO state machine | `DRAFT → SUBMITTED → IN_TRANSIT → RECEIVED → RECONCILED → CLOSED` (with CANCELED branches) |
| Receipt idempotency | `(vendor_id, vendor_invoice_number, location_id)` natural key |

## Purpose

Receipt-side authoritative. Invoice-side reconciliation explicitly delegated to canary-commercial — RECONCILED transition is set by canary-commercial when invoice match completes. EDI 810 bulk import supports vendor-systems-of-record sync.

## Dependencies

- canary-identity, canary-item
- canary-inventory (receipt → position increment)
- canary-commercial (RECONCILED transition, invoice match)

## Consumers

- canary-inventory (position increment events)
- canary-commercial (PO + receipt linkage for reconciliation)
- canary-ildwac (receiving events trigger cost-model recompute)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-receiving
- Card: [[canary-commercial]]
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]], [[tier-bulk-window]]

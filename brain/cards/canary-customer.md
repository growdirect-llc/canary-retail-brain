---
card-type: domain-module
card-id: canary-customer
card-version: 1
domain: merchandising
layer: domain
feeds:
  - canary-owl
receives:
  - canary-identity
  - canary-tsp
tags: [customer, master, loyalty, gdpr, ccpa, right-to-erasure, pii, consent]
milestone: M4
status: approved
last-compiled: 2026-04-30
---

# Canary Service: customer

## What this is

Customer master records, loyalty program membership, purchase history references, and consent state for marketing/data-handling. Customers are merchant-scoped by design (same person across two merchants is two records); cross-merchant linkage is a separate concern handled by canary-owl.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:8096` |
| Axis | B — Resource APIs |
| Tier mix | Reference (PII-gated lookups) · Change-feed (filtered list) · Stream (master CRUD, loyalty adjust, consent updates, anonymization) · Bulk window (master refresh, GDPR exports) |
| Owned tables | `app.customers`, `app.customer_consents`, `app.customer_loyalty`, `app.customer_erasure_log` |

## Purpose

Master + loyalty + GDPR/CCPA right-to-erasure. **Anonymization scrubs PII fields, retains transaction-link tokens, and writes an erasure receipt — does not delete rows.** Hard delete is operationally prohibited because of Fox's append-only evidence chain — historical transactions remain hash-chained even when customer PII is scrubbed.

## Dependencies

- canary-identity (JWT, merchant scope, PII RBAC)
- canary-tsp (transaction-history pointers)

## Consumers

- canary-tsp (customer attribution on transactions)
- canary-pricing (customer-segment-aware pricing)
- canary-returns (return history aggregation)
- canary-owl (cross-merchant linkage as separate concern)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-customer
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]], [[tier-bulk-window]]
- Card: [[platform-pii-hashing]]

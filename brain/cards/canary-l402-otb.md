---
card-type: domain-module
card-id: canary-l402-otb
card-version: 1
domain: finance
layer: domain
feeds: []
receives:
  - canary-identity
  - canary-receiving
  - canary-transfer
  - canary-commercial
tags: [l402, lightning, otb, open-to-buy, gate, micropayment, accountability, patent-protected]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: l402-otb

## What this is

**Patent-protected (#63/991,596)** Lightning-gated open-to-buy budget enforcement. Allocates merchant-wide and category-level OTB budgets; reconciles against actuals on a change-feed cadence (15-minute default). The `gate` endpoint enforces budget compliance for any procurement action that touches OTB — POs, transfers, restocks, vendor commitments.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9090` |
| Axis | B — Resource APIs |
| Tier mix | Reference (budget reads, allocation, policy) · Change-feed (reconciliation history, periodic reconcile) · Stream (gate decisions, allocation/policy mutations) · Bulk window (period-end exports) |
| Owned tables | `app.otb_budgets`, `app.otb_allocations`, `app.otb_policies`, `app.otb_gate_decisions`, `app.otb_reconciliations`, `app.otb_l402_invoices` |
| Tier mapping rule | **Change-feed for reconciliation, stream only for the gate decision. Periodic reconciliation prevents over-fitting; per-event reconciliation would burn the model.** |

## Gate decision contract

`POST /l402-otb/gate` returns `200 {allowed:true}` or `402 {allowed:false, l402_invoice:<lightning-invoice>}`. **The 402 response carries an L402 Lightning invoice** — clients that pay the invoice can continue the action, providing a built-in escalation path for legitimate over-budget operations. This is the patent-protected mechanism.

## Purpose

OTB enforcement that's neither manual approval flow nor blind authorization. Lightning micropayment gates create cryptographic, timestamped, non-repudiable spend records. Empty wallet → tool call fails. Settled payment IS the authorization.

## Dependencies

- canary-identity, canary-receiving (PO submit gates here)
- canary-transfer (transfer-cost gates here)
- canary-commercial (chargeback impact on budget)
- Lightning node (L402 invoice issuance)

## Consumers

- canary-receiving (PO submit calls /gate)
- canary-transfer (transfer-cost calls /gate)
- canary-commercial (reconciliation feedback)
- Finance / treasury teams (budget reads)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-l402-otb
- Card: [[infra-l402-otb-settlement]] (concept-level capability card)
- Card: [[platform-l402-ildwac-moat]]
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]], [[tier-bulk-window]]

---
card-type: domain-module
card-id: canary-returns
card-version: 1
domain: lp
layer: domain
feeds:
  - canary-inventory
  - canary-fox
  - canary-customer
receives:
  - canary-identity
  - canary-tsp
tags: [returns, refund, escalation, fraud, fox-case, return-history]
milestone: M4
status: approved
last-compiled: 2026-04-30
---

# Canary Service: returns

## What this is

Return-to-merchant workflow — return authorization, reason classification, refund flow, and exchange handling. Owns the return record from initiation through resolution; cross-references canary-tsp for the original transaction, canary-inventory for restocking, canary-fox for fraud-flagged returns, canary-customer for return history.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:8097` |
| Axis | B — Resource APIs |
| Tier mix | Reference (return + timeline + reason catalog) · Change-feed (filtered list) · Stream (state transitions, escalation, restock, refund record) · Bulk window (reporting export) |
| Owned tables | `app.returns`, `app.return_lines`, `app.return_events`, `app.return_reasons` |
| State machine | `REQUESTED → AUTHORIZED → RESTOCKED → REFUNDED → CLOSED` with `DECLINED` and `ESCALATED → Fox case` branches |
| Auto-authorization | within N days, original receipt, new condition, below merchant-configured threshold |

## Purpose

Records return disposition; does **not** execute payment refund (that's the POS or payment processor). ESCALATED branch creates Fox case via canary-alert and blocks CLOSED until Fox resolves — the canonical return-fraud escalation primitive.

## Dependencies

- canary-identity, canary-tsp (original transaction)
- canary-inventory (restock event)
- canary-customer (return history aggregation)
- canary-fox (case creation on escalation)
- canary-alert (alerts on auto-decline patterns)

## Consumers

- canary-fox (case subjects on escalation)
- canary-chirp (return-fraud detection rules)
- canary-customer (return history)
- BI/reporting

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-returns
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]], [[tier-bulk-window]]

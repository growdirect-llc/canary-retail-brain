---
card-type: domain-module
card-id: canary-transfer
card-version: 1
domain: merchandising
layer: domain
feeds:
  - canary-inventory
  - canary-bull
receives:
  - canary-identity
  - canary-item
tags: [transfer, inter-location, distribution, variance, fox-escalation, transfer-loss]
milestone: M4
status: approved
last-compiled: 2026-04-30
---

# Canary Service: transfer

## What this is

Operational record for inter-location transfer requests, in-transit tracking, and variance reporting on short-shipments, over-receipts, damages, and missing items. Loss detection and pattern analysis on transfer-loss events live in canary-bull.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:8093` |
| Axis | B — Resource APIs |
| Tier mix | Reference (transfer, lines, events lookup) · Change-feed (filtered lists) · Stream (lifecycle, variance, line corrections) |
| Owned tables | `app.transfers`, `app.transfer_lines`, `app.transfer_events`, `app.transfer_variances` |
| State machine | `CREATED → IN_TRANSIT → RECEIVED → RECONCILED` with `CANCELED` and `DISPUTED → ESCALATED-TO-FOX` branches |
| Variance taxonomy | `SHORT \| OVER \| DAMAGED \| MISSING` |

## Purpose

Operational record only. Loss intelligence delegated to canary-bull. Material variances trigger Fox case creation via canary-alert, blocking transfer CLOSED until Fox resolves. No bulk-window endpoints by design.

## Dependencies

- canary-identity, canary-item
- canary-inventory (transfer events drive position decrement at source / increment at destination)
- canary-bull (subscribes to variance events for cross-location loss correlation)

## Consumers

- canary-bull (transfer-loss intelligence)
- canary-alert (escalation → Fox case)
- canary-fox (forensic record on disputed transfers)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-transfer
- SDD: `docs/sdds/go-handoff/bull.md` (loss intelligence)
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]]

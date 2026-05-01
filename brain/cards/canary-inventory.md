---
card-type: domain-module
card-id: canary-inventory
card-version: 1
domain: merchandising
layer: domain
feeds:
  - canary-inventory-as-a-service
  - canary-fox
receives:
  - canary-identity
  - canary-item
  - canary-receiving
  - canary-tsp
tags: [inventory, stock, adjustments, cycle-counts, time-travel, reconciliation, audit]
milestone: M4
status: approved
last-compiled: 2026-04-30
---

# Canary Service: inventory

## What this is

Historical and eventual-consistency stock-position store. Answers "what is the stock level of item X at location Y as of time T" with append-only adjustment records. The audit-ready store; canary-inventory-as-a-service is the real-time engine.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:8091` |
| Axis | B — Resource APIs |
| Tier mix | Reference (positions, time-travel) · Change-feed (adjustments tail) · Stream (adjustment writes, cycle counts) · Daily batch (reconciliation) · Bulk window (snapshot exports) |
| Owned tables | `app.inventory_positions`, `app.inventory_adjustments`, `app.cycle_counts`, `app.cycle_count_lines`, `app.reconciliation_runs` |
| Time-travel semantics | `as_of` UTC; client renders to merchant-local |

## Purpose

The historical/audit-ready inventory store. Adjustment events are append-only with `chain_hash` linkage and optional `evidence_record_id` for Fox-chain forensic linkage on shrink/theft adjustments. Daily-batch reconciliation pass against POS counts.

## Dependencies

- canary-identity, canary-item
- canary-receiving (receipt-driven position increments)
- canary-tsp (transaction-driven decrements)

## Consumers

- canary-inventory-as-a-service (real-time position derived from this)
- canary-fox (evidence on shrink/theft adjustments)
- canary-pricing (low-velocity markdown triggers)
- BI/reporting tools

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-inventory
- Card: [[canary-inventory-as-a-service]]
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]], [[tier-daily-batch]], [[tier-bulk-window]]

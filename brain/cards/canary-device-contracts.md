---
card-type: domain-module
card-id: canary-device-contracts
card-version: 1
domain: platform
layer: domain
feeds:
  - canary-alert
  - canary-fox
  - canary-ildwac
receives:
  - canary-identity
  - canary-asset
tags: [device-contracts, sla, smart-contract, breach, uptime, throughput, error-budget]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: device-contracts

## What this is

Smart-contract-style enforcement of cost/profit-center device SLAs. A device-contract declares the expected behavior of an asset (uptime, throughput, error budget) and surfaces breach events when actual behavior drifts. Pairs with canary-asset for the device record and with canary-ildwac for cost attribution at breach time.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9083` |
| Axis | B — Resource APIs |
| Tier mix | Reference (single-contract reads, templates) · Change-feed (contract list, breach event tail) · Stream (mutations, breach recording) |
| Owned tables | `app.device_contracts`, `app.device_contract_versions`, `app.device_contract_breaches` |
| Evaluator | continuous worker (not REST-driven); reads device telemetry, computes against active contracts |
| Breach actions | `alert`, `case`, `escalate-to-vendor` |

## Purpose

Bridge from "this asset exists" (canary-asset) to "this asset is meeting its SLA" (canary-device-contracts). Breach events fan out to canary-alert for noisy issues, canary-fox for severe ones, and canary-ildwac for cost attribution at breach time.

## Dependencies

- canary-identity, canary-asset (device record)
- canary-alert (breach → alert)
- canary-fox (breach → case for severe)
- canary-ildwac (cost attribution at breach time)

## Consumers

- canary-alert (alert creation on breach)
- canary-fox (case opening on severe breach)
- Vendor escalation systems (via webhook)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-device-contracts
- Card: [[canary-asset]]
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]]

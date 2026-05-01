---
card-type: domain-module
card-id: canary-asset
card-version: 1
domain: platform
layer: domain
feeds:
  - canary-device-contracts
  - canary-store-network-integrity
receives:
  - canary-identity
tags: [asset, registry, lifecycle, location-binding, devices, hardware, operations]
milestone: M4
status: approved
last-compiled: 2026-04-30
---

# Canary Service: asset

## What this is

The authoritative registry for every physical or digital resource the merchant tracks at the per-location level — registers, scanners, scales, tablets, signage devices, edge compute, network appliances. Owns asset lifecycle, location binding, and audit history.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:8089` |
| Axis | B — Resource APIs |
| Tier mix | Reference (lookups, history) · Change-feed (filtered list) · Stream (lifecycle mutations) |
| Owned tables | `app.assets`, `app.asset_lifecycle_events`, `app.asset_types` |
| State machine | `ACTIVE ⇄ IDLE → RETIRED` (RETIRED terminal) |

## Purpose

Asset records are the canonical reference for any hardware or digital resource the merchant tracks. Cross-references canary-device-contracts for SLA enforcement and canary-store-network-integrity for cross-location anomaly detection on hardware fingerprints.

## Dependencies

- canary-identity (JWT validation, merchant scope)
- canary-device-contracts (publishes lifecycle events for SLA cross-reference)

## Consumers

- canary-device-contracts (SLA enforcement)
- canary-store-network-integrity (hardware-fingerprint cross-location correlation)
- Merchant ops dashboards (asset health grid)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-asset
- Card: [[axis-resource]]
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]]
- Card: [[infra-cadence-ladder]]

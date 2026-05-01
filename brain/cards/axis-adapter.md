---
card-type: infra-capability
card-id: axis-adapter
card-version: 1
domain: platform
layer: infra
feeds:
  - infra-cadence-ladder
receives: []
tags: [axis, adapter, pos-substrate, webhook, polling, edge-agent, bulk-import]
status: approved
last-compiled: 2026-04-30
---

# Axis: Adapter Substrate

## What this is

Axis A in the three-axis API model. The inbound integration surface — how Canary acquires data from external POSes and merchant systems. Inverse of GK Software's App Enablement (which runs plug-ins inside an external POS UI); Canary runs adapters that pull from or receive from external POSes.

## Purpose

Canary is POS-agnostic by design. Every supported POS (Square, NCR Counterpoint via RapidPOS, Shopify, WooCommerce, future) implements the same `POSAdapterSubstrate` interface and emits ARTS POSLog as the canonical wire format. The adapter axis is what makes Canary's "intelligence layer over any POS" lane viable.

## Structure

Four adapter patterns, each a tier expression:

| Pattern | Tier | Example |
|---|---|---|
| Webhook receiver | Stream | Square webhook → `tsp` |
| Polling client | Change-feed | Counterpoint REST polled by `bull` |
| Edge-agent push | Stream-out | `cmd/edge` → `tsp` cloud webhook |
| Bulk-import landing zone | Bulk window | Weekly catalog drop, vendor master refresh |

The bulk-import pattern was the missing fourth — added with the cadence-ladder pass.

## Adapter interface

```go
Connect(merchantID, credentials) (Session, error)
Pull(session, since time.Time) ([]ARTSEvent, watermark, error)        // change-feed
Subscribe(session, eventTypes) (<-chan ARTSEvent, error)               // stream
Import(session, kind, source) (JobID, error)                           // bulk-window
Disconnect(session) error
```

All output normalizes to ARTS POSLog before entering Canary's pipeline.

## Direction

Inbound — from external POS to Canary.

## Consumers

- `cmd/tsp` (Transaction Stream Processor) — receives webhooks
- `cmd/hawk` (Square adapter) — webhook + polling
- `cmd/bull` (Counterpoint adapter) — polling
- `cmd/edge` (edge agent) — outbound to cloud webhook
- `cmd/ecom-channel` (ecom adapter) — webhook + polling per channel

## Sources

POS Adapter Substrate SDD (`docs/sdds/go-handoff/pos-adapter-substrate.md`) defines the contract; Hawk and Bull SDDs document specific adapter implementations.

## Anti-pattern

Don't build a per-POS adapter that bypasses the substrate. Every new POS implements the four patterns or it doesn't ship. Adapter-specific extensions go in adapter-specific code; the substrate contract is universal.

## See also

- Card: [[infra-cadence-ladder]]
- Card: [[axis-resource]]
- Card: [[axis-agent]]
- SDD: `docs/sdds/go-handoff/pos-adapter-substrate.md`
- Wiki: [[Brain/wiki/canary-go-endpoint-library]] §Axis A

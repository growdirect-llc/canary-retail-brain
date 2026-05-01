---
card-type: domain-module
card-id: canary-inventory-as-a-service
card-version: 1
domain: merchandising
layer: domain
feeds:
  - canary-ecom-channel
receives:
  - canary-identity
  - canary-inventory
  - canary-tsp
  - canary-item
  - canary-owl
tags: [iaas, real-time, inventory, sse, reservations, pgvector, similarity, cart-hold]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: inventory-as-a-service (IaaS)

## What this is

Real-time inventory position engine. Answers "right now, what is the stock at location X for item Y?" — superset of canary-inventory (which is the historical store). Holds in-memory live positions per (merchant, location, item) backed by Postgres + pgvector for similarity-based substitute lookups. SSE stream emits position changes for ops dashboards and ecom cart reservations.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9081` |
| Axis | B — Resource APIs · C — Agent Surface (SSE) |
| Tier mix | Stream (SSE, reservation engine) · Reference (live snapshot, similarity search) · Change-feed (velocity windows) |
| Owned tables | `app.iaas_reservations`, `metrics.inventory_velocity` (write-back) |
| Reservation lifecycle | `ACTIVE (TTL countdown) → COMMITTED \| EXPIRED \| RELEASED` |

## Purpose

The line between historical/audit (canary-inventory) and real-time/decision (canary-inventory-as-a-service). IaaS holds live state in Valkey, rebuilds on startup from canary-inventory snapshot + post-snapshot adjustments. SSE merchant-scoped at subscribe time.

## Dependencies

- canary-identity, canary-inventory (durable adjustments)
- canary-tsp (transaction-driven decrement)
- canary-item (item metadata for similarity)
- canary-owl (pgvector embeddings)
- Valkey (live state)

## Consumers

- canary-ecom-channel (cart reservations during checkout flow)
- Ops dashboards (real-time stock visualization)
- AI agents (live position queries for decision-support)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-inventory-as-a-service
- Card: [[canary-inventory]] (the historical/audit counterpart)
- Cards: [[tier-stream]], [[tier-reference]], [[tier-change-feed]]

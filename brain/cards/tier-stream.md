---
card-type: infra-capability
card-id: tier-stream
card-version: 1
domain: platform
layer: infra
feeds:
  - infra-cadence-ladder
receives: []
tags: [tier, stream, real-time, sse, websocket, freshness-budget, heartbeat]
status: approved
last-compiled: 2026-04-30
---

# Tier: Stream

## What this is

The fastest tier in the cadence ladder. Cadence: milliseconds to seconds. Payload: bytes to KB. Used for in-flight transactional events, real-time alerts, SSE feeds, hardware-event subscriptions, and webhook receivers from external POSes.

## Purpose

When a downstream consumer needs to react inside the user's perception window — cashier sees alert in under a second, ops dashboard updates in real time, AI agent makes a decision before the cart finalizes — the cadence is stream. Anything slower fails the use case.

## Structure

| Property | Value |
|---|---|
| Cadence | ms–sec |
| Payload size | bytes–KB |
| Protocol fit | SSE, WebSocket, push webhook, MSMQ-style queue |
| Failure metric | "no heartbeat in N seconds" |
| Health input | last-heartbeat timestamp |
| Recovery primitive | replay from queue (idempotency key required) |
| Alert pattern | heartbeat-lost |
| Cache strategy | none — real-time |
| Required SLA fields | `freshness_budget` (seconds) |
| Forbidden SLA fields | `schedule`, `window_*`, `ttl` |
| Required recovery | `mode: replay-from-queue`, `idempotency_key` |
| Watcher check interval | 1 second |

## Health states

```
green:  now − last_heartbeat < freshness_budget
amber:  freshness_budget ≤ now − last_heartbeat < 2× freshness_budget
red:    now − last_heartbeat ≥ 2× freshness_budget
```

## Examples

- `POST /webhooks/square` — Square webhook receiver (Adapter axis)
- `GET /alerts/sse` — live alert feed (Resource axis)
- `GET /inventory/sse` — real-time stock-position changes (Resource axis)
- MCP tool synchronous calls like `compliance.create_block` (Agent axis)
- Hardware events from in-store devices (cash drawer open, scanner errors)

## Consumers

- Cashier UI (alerts must surface within human perception)
- In-store AI assistants (agents that gate transactions)
- Ops dashboards (live device-health grid)
- Anomaly detection (Chirp consumes streams of detection-ready events)

## Anti-pattern

Don't use stream tier for slow-moving data — burns cache, generates noise, no benefit. Reference tier with short TTL is almost always better for "current value" lookups.

## See also

- Card: [[infra-cadence-ladder]]
- Card: [[infra-feed-tier-contract]] (config schema + runtime)
- SDD: `docs/sdds/go-handoff/feed-tier-contract.md` Layer 3 — `StreamTier` handler

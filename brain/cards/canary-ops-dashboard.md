---
card-type: domain-module
card-id: canary-ops-dashboard
card-version: 1
domain: platform
layer: domain
feeds: []
receives:
  - canary-identity
  - canary-store-brain
tags: [ops-dashboard, store-noc, sse, mcp, device-health, observability, health-rollup]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: ops-dashboard

## What this is

The store-network operations console. Live device-health grid, MCP-server observability, alert state distribution, and adapter-sync watermarks. Two surfaces: REST API for state queries and SSE channel for live updates. Also exposes an MCP server (`canary-ops`) so AI assistants query operational state on demand.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9084` |
| Axis | B — Resource APIs · C — Agent Surface (SSE + MCP) |
| Tier mix | Stream (SSE channel for live ops) · Reference (snapshot state, device telemetry, MCP grid) · Change-feed (operational event log) · Stream (silence/unsilence actions) |
| Owned tables | `app.device_telemetry`, `app.adapter_watermarks`, `app.ops_event_log`, `app.device_silences` |
| MCP server | `canary-ops` — 6 tools |
| SSE event taxonomy | device.online · device.offline · device.degraded · adapter.lag · mcp.unhealthy · alert.created |

## MCP surface (Axis C)

| Tool | Tier | Purpose |
|---|---|---|
| `ops.device_status` | Reference | Get device health |
| `ops.adapter_lag` | Reference | Adapter sync lag |
| `ops.alert_distribution` | Reference | Alert counts by severity/status |
| `ops.mcp_health` | Reference | MCP server observability |
| `ops.health_rollup` | Reference | Per-tier health summary (5 tiers) |
| `ops.silence_device` | Stream | Silence noisy device |

## Purpose

Surfaces tier-rollup data (5 indicators, not binary green/red) per the cadence-ladder Layer 4 surface commitment. Bases query on Brain wiki consumes from same data.

## Dependencies

- canary-identity (JWT, super-admin scoping)
- Every other Canary service (consumes their `/health` and `/status`)
- canary-store-brain (presence data for in-store device attribution)

## Consumers

- Operators / on-call engineers
- AI assistants (founder ALX, Cowork, in-store agents)
- Brain wiki Bases queries (5-tier rollup)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-ops-dashboard
- Card: [[axis-agent]]
- Card: [[infra-feed-tier-contract]] (Layer 4 surface)
- Cards: [[tier-stream]], [[tier-reference]], [[tier-change-feed]]

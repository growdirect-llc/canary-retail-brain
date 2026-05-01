---
card-type: domain-module
card-id: canary-store-brain
card-version: 1
domain: platform
layer: domain
feeds:
  - canary-ops-dashboard
receives:
  - canary-identity
  - canary-raas
tags: [store-brain, presence, session, permission-gating, mcp, sse, ai-context-manager, in-store]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: store-brain

## What this is

The in-store AI context manager. Resolves which assistant agents are present in a location, which user sessions are active, and which MCP tools each agent has permission to call. **Acts as the policy-decision-point for in-store agent activity** — every in-store MCP tool call traverses store-brain for permission gating.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9085` |
| Axis | B — Resource APIs · C — Agent Surface (SSE + MCP) |
| Tier mix | Stream (SSE, session lifecycle, heartbeats, policy-grant mutations) · Reference (presence snapshot, permission resolution, policy lookup) · Change-feed (session history tail) |
| Owned tables | `app.store_brain_sessions`, `app.store_brain_session_events`, `app.store_brain_policies`, `app.store_brain_permission_grants` |
| MCP server | `canary-store-brain` — 5 tools |
| Permission resolution | merchant policy → location overrides → session grants/revokes (deny-overrides) |

## MCP surface (Axis C)

| Tool | Tier | Purpose |
|---|---|---|
| `store_brain.who_is_here` | Reference | Active agents at location |
| `store_brain.start_session` | Stream | Begin agent session |
| `store_brain.check_permission` | Reference | Verify tool permission |
| `store_brain.heartbeat` | Stream | Session keep-alive |
| `store_brain.end_session` | Stream | End session |

## Purpose

**Without permission gating, the MCP surface is too dangerous to expose.** Every session is bound to a single (merchant_id, location_id) tuple. SSE channel is merchant + location scoped at subscribe time. Policy decision happens server-side; clients receive allow/deny answers, not raw policy data.

## Dependencies

- canary-identity (JWT, tenant context)
- canary-raas (session-key construction)
- Every MCP-bearing service (consults store-brain for permission gating)

## Consumers

- Every MCP-bearing service in Canary (permission resolution before tool execution)
- canary-ops-dashboard (presence data)
- In-store AI assistants (session lifecycle)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-store-brain
- Card: [[axis-agent]]
- Cards: [[tier-stream]], [[tier-reference]], [[tier-change-feed]]

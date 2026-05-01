---
card-type: infra-capability
card-id: axis-agent
card-version: 1
domain: platform
layer: infra
feeds:
  - infra-cadence-ladder
receives: []
tags: [axis, agent, mcp, sse, webhook-publisher, ai-native, differentiation]
status: approved
last-compiled: 2026-04-30
---

# Axis: Agent Surface

## What this is

Axis C in the three-axis API model. **Canary's most novel axis — and the one with no GK Software equivalent.** The AI-native surface where AI agents (Claude Code, Cowork, in-store AI assistants, third-party agentic tooling) are first-class consumers. Three sub-surfaces: MCP tool registry, SSE event streams, outbound webhook publishers.

## Purpose

When the consumer is an AI agent rather than a human or a traditional integration, the contract shape changes. Tools have to be machine-described (MCP). Events have to stream so agents can react in real time (SSE). Outbound notifications need typed schemas so agents can subscribe without scraping (webhook publishers). Axis C is what makes Canary AI-native rather than retrofitted-for-AI.

## Structure

### MCP tool registry

Each agent-facing service exposes an MCP server with named tools, JWT-gated, tenant-scoped:

| MCP Server | Tools | Tier mix |
|---|---|---|
| `canary-compliance` | 7 | Reference + Stream |
| `canary-raas` | 7 | Reference + Stream |
| `canary-fox` | TBD | Reference + Stream |
| `canary-chirp` | TBD | Reference + Change-feed |
| `canary-owl` | TBD | Reference |
| `canary-store-brain` | 5 | Reference + Stream |
| `canary-ops` | 6 | Reference + Stream |

### SSE streams

Server-Sent Events for live event consumption by AI agents:

| Stream | Service |
|---|---|
| `/alerts/sse` | alert |
| `/transactions/sse` | tsp |
| `/inventory/sse` | inventory-as-a-service |
| `/analytics/sse` | analytics |
| `/ops-dashboard/sse` | ops-dashboard |
| `/store-brain/sse` | store-brain |

### Webhook publishers

Outbound notifications from Canary to merchant-configured destinations on alert creation, case escalation, detection rule firing, daily digests, reconciliation summaries.

## Direction

Outbound — Canary serves AI consumers.

## Why no GK equivalent

GK's Function namespace dispatches generic functions for in-POS plug-ins; that's RPC-flavored, not AI-native. MCP tool surfaces with typed input/output schemas, capability gates via canary-store-brain permission resolution, and AI-readable descriptions are a different model entirely. **This is Canary's AI-native differentiator** — the surface that makes the platform leapfrog the enterprise POS playbook rather than catch up to it.

## Consumers

- Claude Code in development sessions
- Cowork in operator-facing workflows
- In-store AI assistants
- Third-party agentic tooling
- Founder ALX/ALXjr instances

## Permission gating

Every MCP tool call passes through canary-store-brain for permission resolution. The session-scoped policy decides which tools are allowed for which agent at which location. **Without permission gating, the MCP surface is too dangerous to expose.**

## Sources

- canary-store-brain SDD (session governance + permission resolution)
- canary-compliance SDD (7-tool MCP reference)
- canary-raas SDD (7-tool MCP reference)
- microservice-architecture.md MCP surface tables

## Anti-pattern

Don't expose MCP tools without store-brain permission gating. Don't publish events on SSE streams without tenant scoping at subscribe time. Don't push outbound webhooks to user-supplied URLs without HMAC signing and replay protection.

## See also

- Card: [[axis-adapter]]
- Card: [[axis-resource]]
- Card: [[platform-stack-commitment]]
- Wiki: [[Brain/wiki/canary-mcp-stack-architecture]]
- Wiki: [[Brain/wiki/canary-go-endpoint-library]] §Axis C

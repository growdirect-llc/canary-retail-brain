---
card-type: domain-module
card-id: canary-raas
card-version: 1
domain: platform
layer: infra
feeds: []
receives:
  - canary-identity
tags: [raas, namespace, key-construction, chain-hash, mcp, tenant-isolation, primitive]
milestone: M4
status: approved
last-compiled: 2026-04-30
---

# Canary Service: raas

## What this is

Resolution as a Service — namespace resolution and chain-hash backbone. Every Canary service that constructs a Valkey key, resolves a tenant namespace, or anchors a hash to the chain calls canary-raas. **Load-bearing primitive that prevents key-construction divergence across 32 services and prevents tenant-isolation bugs at the cache layer.**

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:8099` |
| Axis | B — Resource APIs · C — Agent Surface (MCP) |
| Tier mix | Reference (deterministic computations: namespace resolve, key build, chain verify) · Stream (chain anchoring is per-event) |
| Owned tables | `app.raas_namespaces`, `app.raas_anchors`, `app.raas_active_sources` |
| MCP server | `canary-raas` — 7 tools |
| Inverse dependency | every other service depends on canary-raas for key construction |

## MCP surface (Axis C)

| Tool | Tier | Purpose |
|---|---|---|
| `raas.resolve_namespace` | Reference | Full namespace state for merchant |
| `raas.build_key` | Reference | Deterministic Valkey key construction |
| `raas.ensure_namespace` | Reference | Pure-string namespace construction |
| `raas.verify_chain` | Reference | Chain integrity check |
| `raas.list_active_sources` | Reference | Enumerate active POS sources |
| `raas.anchor_hash` | Stream | Submit hash for chain anchoring |
| `raas.get_chain_head` | Reference | Latest chain position for merchant + class |

## Purpose

Key construction rule: **No service constructs Valkey keys directly.** Every key goes through `raas.build_key` or `raas.ensure_namespace`. Pattern: `raas:{merchant_id}:{domain}:{key}`. Violations would silently break tenant isolation at the cache layer.

## Dependencies

- canary-identity (JWT, merchant context)
- PostgreSQL (chain anchor persistence)

## Consumers

- Every other Canary service (key construction)
- canary-fox (evidence-chain anchoring)
- canary-blockchain-anchor (consumes raas anchors for L2 batching)
- AI agents (MCP tool surface)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-raas
- Card: [[axis-resource]] · [[axis-agent]]
- Card: [[raas-receipt-as-a-service]] (related concept)

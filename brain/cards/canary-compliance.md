---
card-type: domain-module
card-id: canary-compliance
card-version: 1
domain: lp
layer: domain
feeds:
  - canary-fox
receives:
  - canary-identity
  - canary-item
  - canary-employee
  - canary-customer
  - canary-raas
tags: [compliance, item-authorization, regulatory-zone, ops-blocks, mcp, attestation, age-verification]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: compliance

## What this is

Cross-cutting compliance enforcement — item authorization (which items can be sold at which locations), regulatory zone management (state/county tax, age-verification, license requirements), and operational blocks (item × time-of-day restrictions, employee-role restrictions). Reference-tier service: lookups are slow-moving and heavily cached. The 7-tool MCP surface is where AI assistants consult compliance state at decision time.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9091` |
| Axis | B — Resource APIs · C — Agent Surface (MCP) |
| Tier mix | Reference (lookups, zones, authorization, policies, blocks — heavy caching) · Change-feed (audit log) · Stream (block / zone / authorization mutations) · Bulk window (regulatory updates, catalog-wide authorization sweep, period attestation) |
| Owned tables | `app.compliance_zones`, `app.compliance_zone_rules`, `app.compliance_item_authorizations`, `app.compliance_blocks`, `app.compliance_audit_log`, `app.compliance_attestations` |
| MCP server | `canary-compliance` — 7 tools |
| Lookup precedence | Operational block (most specific wins) → Item authorization at location → Regulatory zone rules → default allowed |

## MCP surface (Axis C)

| Tool | Tier | Purpose |
|---|---|---|
| `compliance.lookup` | Reference | Full compliance check (item × location × customer × time) |
| `compliance.list_zones` | Reference | Zones for a merchant |
| `compliance.zone_detail` | Reference | Single zone detail |
| `compliance.item_authorization` | Reference | Item authorization across locations |
| `compliance.create_block` | Stream | Add operational block |
| `compliance.audit_log` | Reference | Recent compliance decisions |
| `compliance.attest` | Stream | Generate attestation for period |

## Purpose

The "can this happen at all" gate. Tier mapping is intentional: stream-tier compliance would burn the cache. Compliance policies are merchant-scoped; regulatory zones may be shared across merchants but applicability is merchant-scoped.

## Dependencies

- canary-identity (JWT, merchant scope)
- canary-item, canary-employee (role checks), canary-customer (age/verification claims)
- canary-fox (evidence on attestation)
- canary-raas (key construction for cache)

## Consumers

- POS adapters (compliance.lookup at decision time)
- AI agents (in-store, founder-side) consulting compliance state
- canary-returns (compliance check before authorizing return)
- Audit/regulatory review

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-compliance
- SDD: `docs/sdds/go-handoff/compliance.md`
- Card: [[axis-agent]]
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]], [[tier-bulk-window]]

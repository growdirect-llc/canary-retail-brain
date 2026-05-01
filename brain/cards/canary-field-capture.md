---
card-type: domain-module
card-id: canary-field-capture
card-version: 1
domain: platform
layer: domain
feeds: []
receives:
  - canary-identity
  - canary-owl
tags: [field-capture, semantic-mapping, pgvector, schema-registry, adapter-aid]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: field-capture

## What this is

pgvector-backed registry of semantic field mappings. When a POS adapter or import job encounters a non-standard field name (`cust_no` vs `customer_id` vs `acctNum`), canary-field-capture resolves it to the canonical Canary field via embedding similarity plus learned per-source mappings.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9087` |
| Axis | B — Resource APIs |
| Tier mix | Reference (lookup, canonical reads, per-source mappings) · Stream (mapping mutations) · Bulk window (per-merchant migration of learned mappings) |
| Owned tables | `app.field_canonical`, `app.field_mappings`, `app.field_mapping_audits` |
| Resolution flow | adapter sees raw field → POST /lookup → embedding kNN against canonical → cached resolution returned with confidence |

## Purpose

Canonical fields are merchant-agnostic (shared catalog). Learned mappings are merchant + source scoped to prevent cross-merchant pollution of the learning signal. **Reduces adapter integration cost** — new POS adapters lean on field-capture to resolve idiosyncratic field naming without writing per-source mapping tables.

## Dependencies

- canary-identity (JWT, scope)
- canary-owl (embedding generation)
- PostgreSQL with pgvector

## Consumers

- All POS adapters (canary-hawk, canary-bull, canary-ecom-channel, future)
- Bulk import jobs across services
- Future: agent-driven migration tooling

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-field-capture
- Card: [[platform-field-capture]] (concept-level field capture for evidence chain)
- Cards: [[tier-reference]], [[tier-stream]], [[tier-bulk-window]]

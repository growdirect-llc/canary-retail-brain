---
card-type: infra-capability
card-id: tier-reference
card-version: 1
domain: platform
layer: infra
feeds:
  - infra-cadence-ladder
receives: []
tags: [tier, reference, ttl, cached-lookup, slow-moving, master-data, version-drift]
status: approved
last-compiled: 2026-04-30
---

# Tier: Reference

## What this is

The slowest tier — slow-moving lookup data with long TTL caching. Cadence: monthly or longer. Payload: variable (small for individual lookups, larger for bulk masters). Used for master data that changes rarely — tax tables, fiscal calendars, jurisdiction masters, item authorization, regulatory zones, employee roles, vendor contracts.

## Purpose

Most lookups in any retail system are reference. Tax rates don't change every second. Item-authorization mappings don't churn. Employee role definitions are stable. Treating these as faster tiers wastes cache, generates spurious alerts, and obscures actual stream/change-feed health. Reference tier is the mathematical default — anything not justified to a faster tier belongs here.

## Structure

| Property | Value |
|---|---|
| Cadence | monthly+ (TTL-based revalidation) |
| Payload size | varies — small per-record, large per-master |
| Protocol fit | REST GET with long Cache-Control / ETag, MCP tool sync call |
| Failure metric | "version drift" — current version older than cohort or stale beyond TTL |
| Health input | last revalidation timestamp |
| Recovery primitive | force resync (full pull) |
| Alert pattern | version-drift |
| Cache strategy | long TTL with versioning, ETag-based revalidation |
| Required SLA fields | `ttl` (duration) |
| Forbidden SLA fields | `freshness_budget`, `max_lag`, `schedule`, `window_*` |
| Required recovery | `mode: force-resync` |
| Watcher check interval | 1 hour |

## Health states

```
green:  now − last_revalidated < ttl
amber:  ttl ≤ now − last_revalidated < 2× ttl
red:    now − last_revalidated ≥ 2× ttl
```

## Examples

- `GET /items/:id` — item lookup (24h cache)
- `GET /compliance/lookup?item_id=&zone_id=` — compliance state (24h cache, invalidated on policy change)
- `GET /raas/build-key` — deterministic key construction (long cache)
- `GET /pricing/effective?...` — effective price resolution (60s TTL — short for reference, but still reference-tier semantics)
- `GET /merchants/:id` — merchant config
- `GET /risk-dictionary/:entity_id` — Owl risk profile lookup
- All MCP tools that don't mutate state (compliance.lookup, raas.resolve_namespace, owl.search)

## Consumers

- Every other tier reads reference data (it's foundational)
- Cashier UI for tax rate, regulatory check, age verification rules
- AI agents at decision time (compliance lookup before allowing item sale)
- Reporting and analytics jobs (master-data join keys)

## Anti-pattern

Don't promote a reference feed to stream tier just because the cache invalidates on write — that's correct behavior for cached references, not justification for changing tier. Reference + invalidation event is fine; "reference, but real-time" is a contradiction.

## See also

- Card: [[infra-cadence-ladder]]
- Card: [[infra-feed-tier-contract]]
- SDD: `docs/sdds/go-handoff/feed-tier-contract.md` Layer 3 — `ReferenceTier` handler

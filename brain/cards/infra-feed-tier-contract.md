---
card-type: infra-capability
card-id: infra-feed-tier-contract
card-version: 1
domain: platform
layer: infra
feeds: []
receives:
  - infra-cadence-ladder
  - tier-stream
  - tier-change-feed
  - tier-daily-batch
  - tier-bulk-window
  - tier-reference
tags: [feed-registry, tier-validation, agent-contract, runtime, boot-validation, sla, alert-pattern]
status: approved
last-compiled: 2026-04-30
---

# Feed-Tier Contract

## What this is

The four-layer baking model that turns the [[infra-cadence-ladder|Cadence Ladder]] from descriptive wiki into buildable spec. Every feed declaration carries a tier; the tier is enforced at four layers — config schema, agent contract, runtime behavior, and surface — making tier mismatches fail loudly at boot rather than silently at 2 a.m.

## Purpose

Without baking, tier is a comment. With baking, tier is load-bearing — feed configs reject invalid `sla.*` field combinations per tier, agents fail boot if their `expected_tier` doesn't match the registry, runtime parameterizes per-tier code paths, and surface (Bases queries, Ops Dashboard SSE) renders five-tier health rollup. This card is the contract every implementing service honors.

## Structure

### Layer 1 — Config Schema

Feed declaration in YAML with `tier:` as required field. Per-tier validation rules govern which `sla.*` fields are required vs forbidden:

| Tier | Required | Forbidden | Recovery mode |
|---|---|---|---|
| stream | freshness_budget | schedule, window_*, ttl | replay-from-queue + idempotency_key |
| change-feed | freshness_budget, max_lag | schedule, window_*, ttl | catch-up-from-watermark + watermark_field + idempotency_key |
| daily-batch | schedule (cron) | freshness_budget, window_* | rerun-job |
| bulk-window | window_start, window_end (cron) | freshness_budget, max_lag, schedule, ttl | reschedule-window |
| reference | ttl | freshness_budget, max_lag, schedule, window_* | force-resync |

Persisted to `app.feed_registry` at deploy time. YAML SHA tracked to detect repo↔registry drift.

### Layer 2 — Agent Contract

Each agent declares `consumes:` and `produces:` with expected tier per feed. At boot, runtime cross-references against registry. **Tier mismatch = fatal exit code 78 (EX_CONFIG)**, not a warning.

### Layer 3 — Runtime Behavior

`TierRuntime` interface implemented per tier in `internal/runtime/<tier>.go` (5 files). Watcher loop runs per-feed health checks at tier-determined intervals (1s for stream, 1m for change-feed, 5m for daily-batch, 1h for bulk-window and reference).

### Layer 4 — Surface

- Brain wiki `canary-go-feed-health.base` Bases query — five-tier health rollup, not one binary
- Auto-generated feed cards under `Brain/wiki/cards/` (one per registered feed) — regenerated on deploy
- Ops Dashboard SSE channel `/ops-dashboard/sse?scope=tier-rollup` — per-tier state events

## Consumers

- Every Canary service binary at boot validates its agent contract
- `feed-registry-load` at deploy time validates and upserts feed YAMLs
- Ops Dashboard renders per-tier health
- All in-store agents query feed registry for tier metadata when reasoning about freshness

## Sources

- SDD: `docs/sdds/go-handoff/feed-tier-contract.md` (full spec including Go types, validation algorithm, DB schema, watcher loop)
- Spine card: [[infra-cadence-ladder]]

## Routing

feed YAMLs in `deploy/feeds/*.yaml`
  → `feed-registry-load` deploy job
  → `app.feed_registry` (Postgres)
  → service boot reads contract YAML, validates against registry
  → `internal/runtime/<tier>.go` parameterizes behavior
  → `app.feed_observations` writes per-feed health
  → Bases + SSE surface

## Pitfalls

- Don't bypass tier validation in dev (silent drift returns)
- Don't reinvent recovery modes (five cover the five tiers)
- Don't write feed cards by hand (generated from registry)
- Don't make watcher check interval shorter than tier's natural cadence

## See also

- SDD: `docs/sdds/go-handoff/feed-tier-contract.md`
- Wiki: [[Brain/wiki/canary-go-cadence-ladder]]
- Card: [[infra-cadence-ladder]]
- Card: [[agent-card-format]] (feed-card generator emits cards in this format)

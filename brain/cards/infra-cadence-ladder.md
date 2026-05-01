---
card-type: infra-capability
card-id: infra-cadence-ladder
card-version: 1
domain: platform
layer: infra
feeds:
  - infra-feed-tier-contract
  - tier-stream
  - tier-change-feed
  - tier-daily-batch
  - tier-bulk-window
  - tier-reference
  - axis-adapter
  - axis-resource
  - axis-agent
receives: []
tags: [cadence, tier, endpoint-strategy, freshness, sla, architecture, ross-rti-precedent]
status: approved
last-compiled: 2026-04-30
---

# Cadence Ladder

## What this is

The orthogonal dimension to the three-axis API model. Where axes (Adapter / Resource / Agent) answer *who* an endpoint serves and *where* it sits, the cadence ladder answers *what cadence* it runs at. Five tiers — Stream, Change-feed, Daily batch, Bulk window, Reference — cross with three axes to produce a 3×5 grid where every endpoint occupies exactly one cell.

## Purpose

Tier metadata is load-bearing for SLAs, alerting, and recovery. Without it, "endpoint" is too coarse a unit — freshness budgets, replay-vs-resync, alert routing, and agent readiness all collapse into binary green/red instead of the five-tier health model real multi-store operators need. The ladder makes tier mismatches die loudly at boot rather than silently at 2 a.m.

## Structure

Five tiers, ordered by cadence:

| Tier | Cadence | Payload | Failure mode |
|---|---|---|---|
| Stream | ms–sec | bytes–KB | "no heartbeat in N seconds" |
| Change-feed | min–hour | KB–MB | "lag exceeded" / "queue depth" |
| Daily batch | daily | MB | "schedule missed" / "checksum diff" |
| Bulk window | weekly | MB–GB | "didn't land in window" / "row count off" |
| Reference | monthly+ | varies | "version drift" |

Each tier has a different protocol fit, failure metric, recovery primitive, alert pattern, and cache strategy. Mixing tiers in one endpoint makes health unmonitorable — a single alert cannot catch both "stream stalled for 10 seconds" and "weekly file didn't land."

## Consumers

- All 32 services declare a tier per feed via [[infra-feed-tier-contract]] config schema
- All agents declare consumes/produces with `expected_tier` matching the registry — boot-time mismatch is fatal
- Brain wiki Bases query renders five-tier health rollup, not one binary
- Ops Dashboard SSE channel emits per-tier state-change events

## Sources

Synthesized from a national specialty retailer's ~2011 multi-tier RTI architecture for store↔hub data flow — Service Pulse heartbeat (stream), DDS message-queue polling (change-feed), Windows Event Log + CA UNICENTER alert routing (tier-aware), and Interface Groups taxonomy (5 cadence-suggesting groups). Raw intakes preserved unredacted; this card and downstream artifacts abstract the source.

## Routing

cadence-ladder spec ([[infra-cadence-ladder]])
  → feed-tier-contract SDD ([[infra-feed-tier-contract]])
  → per-tier cards ([[tier-stream]], [[tier-change-feed]], [[tier-daily-batch]], [[tier-bulk-window]], [[tier-reference]])
  → per-axis cards ([[axis-adapter]], [[axis-resource]], [[axis-agent]])
  → endpoint library ([[Brain/wiki/canary-go-endpoint-library]])
  → microservice contracts (`docs/sdds/go-handoff/microservice-architecture.md`)

## See also

- Wiki: [[Brain/wiki/canary-go-cadence-ladder]] (narrative)
- Wiki: [[Brain/wiki/canary-go-endpoint-library]] (3×5 grid in practice)
- SDD: `docs/sdds/go-handoff/feed-tier-contract.md` (buildable spec)
- Memory: `feedback_no_volatile_data_in_wiki`, `feedback_extract_working_solution`

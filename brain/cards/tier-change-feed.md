---
card-type: infra-capability
card-id: tier-change-feed
card-version: 1
domain: platform
layer: infra
feeds:
  - infra-cadence-ladder
receives: []
tags: [tier, change-feed, polling, watermark, lag, cursor-pagination]
status: approved
last-compiled: 2026-04-30
---

# Tier: Change-Feed

## What this is

The minute-to-hour cadence tier. Used for periodic catch-up reads, polling adapters, cursor-paginated tail-feeds, and recompute-on-event flows. Sits between stream (real-time) and daily-batch (scheduled) — appropriate when consumers can tolerate lag bounded in minutes, not seconds, and not days.

## Purpose

The bulk of enterprise integration is change-feed by nature. POS adapters that poll vendor REST APIs, BI tools that ingest periodic snapshots, agent runs that reconcile against actuals every 15 minutes — all change-feed. Stream is wasteful here; daily batch is too slow.

## Structure

| Property | Value |
|---|---|
| Cadence | min–hour |
| Payload size | KB–MB |
| Protocol fit | REST polling, webhook subscription, paginated cursor |
| Failure metric | "lag exceeded" / "queue depth above threshold" |
| Health input | last watermark advance |
| Recovery primitive | catch up from watermark (idempotency key required) |
| Alert pattern | lag-exceeded |
| Cache strategy | short TTL (mins), invalidate on next pull |
| Required SLA fields | `freshness_budget`, `max_lag` |
| Forbidden SLA fields | `schedule`, `window_*`, `ttl` |
| Required recovery | `mode: catch-up-from-watermark`, `watermark_field`, `idempotency_key` |
| Watcher check interval | 1 minute |

## Health states

```
green:  now − last_watermark < max_lag
amber:  max_lag ≤ now − last_watermark < 2× max_lag
red:    now − last_watermark ≥ 2× max_lag
```

## Examples

- `POST /sync/pull` (`bull` polling Counterpoint REST every 60s)
- `GET /alerts?cursor=&since=` — alert tail (Resource axis)
- `GET /inventory/adjustments?cursor=&since=` — adjustment events
- `POST /l402-otb/reconcile` — 15-min OTB reconciliation
- ILDWAC recompute jobs triggered by receiving events

## Consumers

- BI tools and dashboards (polling tail feeds)
- Recompute engines (ILDWAC, analytics rollups)
- Reconciliation services (l402-otb actuals match)
- AI agents that need fresh-but-not-instant context

## Anti-pattern

Don't drop a change-feed feed into daily-batch slot to "save infrastructure." If consumers need 15-min freshness, batching daily silently breaks the contract. Either accept change-feed cadence or move to a stream tier — never split the difference.

## See also

- Card: [[infra-cadence-ladder]]
- Card: [[infra-feed-tier-contract]]
- SDD: `docs/sdds/go-handoff/feed-tier-contract.md` Layer 3 — `ChangeFeedTier` handler

---
card-type: infra-capability
card-id: tier-daily-batch
card-version: 1
domain: platform
layer: infra
feeds:
  - infra-cadence-ladder
receives: []
tags: [tier, daily-batch, cron, eod, reconciliation, scheduled-job]
status: approved
last-compiled: 2026-04-30
---

# Tier: Daily Batch

## What this is

The day-cadence tier. Cron-driven scheduled jobs that run at fixed times — end-of-day reconciliation, daily rollups, morning reports. Cadence is "once per day" but the slot itself is precise (e.g., `0 2 * * *` = 2 a.m. daily). Failure mode is missing the slot or producing a checksum mismatch against the expected output.

## Purpose

Some operations only make sense at day boundaries. Sales day-close, shrink reports, employee scorecards, vendor daily-reconciliation runs, payroll exports — all demand the discipline of "exactly once, at this time." Stream and change-feed are inappropriate; bulk-window is too slow.

## Structure

| Property | Value |
|---|---|
| Cadence | daily (or sub-daily on cron schedule) |
| Payload size | MB |
| Protocol fit | cron-driven export, scheduled REST job, scheduled file write |
| Failure metric | "schedule missed" or "checksum diff vs expected" |
| Health input | last successful run timestamp |
| Recovery primitive | rerun the job for the slot |
| Alert pattern | schedule-missed |
| Cache strategy | invalidate at cron tick |
| Required SLA fields | `schedule` (cron string) |
| Forbidden SLA fields | `freshness_budget`, `max_lag`, `window_*` |
| Required recovery | `mode: rerun-job` |
| Watcher check interval | 5 minutes |

## Health states

```
green:  last successful run within current cron slot
amber:  current run started but not completed
red:    scheduled slot missed entirely (no run in current window)
```

## Examples

- `POST /reconciliation/run` — daily inventory reconciliation against POS counts
- `POST /rollup/daily` — analytics daily rollup
- `POST /commercial/reconciliation/run` — vendor invoice reconciliation
- `POST /correlations/run` — store-network-integrity daily correlation pass
- `POST /reports/:id/runs` — scheduled report generation

## Consumers

- Operators reviewing morning summaries
- Finance running monthly close (consumes daily-batch outputs as building blocks)
- Compliance attestations
- BI tools ingesting daily aggregates

## Anti-pattern

Don't use daily-batch for things that need fresher data — "we'll just rerun it more often" is the road to a fake change-feed. If you need 15-min freshness, declare it as change-feed; if you need real-time, stream.

## See also

- Card: [[infra-cadence-ladder]]
- Card: [[infra-feed-tier-contract]]
- SDD: `docs/sdds/go-handoff/feed-tier-contract.md` Layer 3 — `DailyBatchTier` handler

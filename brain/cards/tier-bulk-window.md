---
card-type: infra-capability
card-id: tier-bulk-window
card-version: 1
domain: platform
layer: infra
feeds:
  - infra-cadence-ladder
receives: []
tags: [tier, bulk-window, weekly-import, catalog-refresh, edi, sftp, large-payload]
status: approved
last-compiled: 2026-04-30
---

# Tier: Bulk Window

## What this is

The weekly-cadence tier for large payloads. Cadence: weekly (or monthly close cycles, period-end attestations). Payload: MB to GB. Used for catalog refreshes, vendor master sync, weekly assortment imports, EDI 810 invoice batches, period-end exports, and Bitcoin L2 hash anchoring. **Distinct from daily-batch by payload size and schedule cadence — bulk-window is the missing fourth adapter pattern in the original Endpoint Library.**

## Purpose

Some operations are inherently periodic and inherently large. A retailer's weekly Item File. A vendor's EDI 810 invoice batch. An hourly Bitcoin L2 commit. Daily-batch is too frequent; reference is too slow. Bulk-window is the right slot — "scheduled, large, takes time to process."

## Structure

| Property | Value |
|---|---|
| Cadence | weekly, monthly close, period-end |
| Payload size | MB–GB |
| Protocol fit | scheduled SFTP drop, signed S3 URL, paged REST/GraphQL export, EDI |
| Failure metric | "didn't land in window" / "row count off vs manifest" |
| Health input | last window completion timestamp |
| Recovery primitive | reschedule the window (or run partial with manual oversight) |
| Alert pattern | window-missed |
| Cache strategy | invalidate at window close |
| Required SLA fields | `window_start`, `window_end` (cron strings) |
| Forbidden SLA fields | `freshness_budget`, `max_lag`, `schedule`, `ttl` |
| Required recovery | `mode: reschedule-window` |
| Watcher check interval | 1 hour |

## Health states

```
green:  window completed within window range
amber:  window started but not completed within range
red:    window slot missed entirely
```

## Examples

- `POST /imports/items` — weekly catalog drop (Adapter axis)
- `POST /imports/customers` — customer master refresh
- `POST /imports/employees` — HRIS roster sync
- `POST /imports/regulatory-zones` — quarterly compliance sweep
- `POST /exports/transactions` — period transaction export
- `POST /blockchain-anchor/commit` — hourly/daily Bitcoin L2 batch hash commit
- EDI 810 invoice batches via canary-commercial

## Consumers

- POS adapters refreshing catalog from merchant ERP
- BI tools running monthly close
- Compliance attestations
- Vendor accounting systems
- Bitcoin L2 anchoring (cost economics enforce bulk window — per-event L2 is cost-prohibitive)

## Why this tier was missing

The original Endpoint Library listed three adapter patterns (webhook receiver / polling client / edge-agent push) without naming them as tier expressions. The fourth pattern — bulk-window inbound — was structurally absent. Catalog refreshes, weekly imports, and reference-master sync had no canonical home. The Ross 2011 RTI architecture had it (DDS-staged file transfers over HTTPS streams with explicit landing-window monitoring); Canary's variant is cloud-native SFTP/bucket landing zones with the same lifecycle semantics. Adding bulk-window closes the largest tier gap.

## Anti-pattern

Don't degrade bulk-window to daily-batch for "simplicity." Catalog refresh that takes hours to process becomes a daily-batch slot that runs over its window; that breaks the schedule contract for everything else in the daily slot.

## See also

- Card: [[infra-cadence-ladder]]
- Card: [[infra-feed-tier-contract]]
- SDD: `docs/sdds/go-handoff/feed-tier-contract.md` Layer 3 — `BulkWindowTier` handler
- Card: [[infra-blockchain-evidence-anchor]] (uses this tier by patent-protected design)

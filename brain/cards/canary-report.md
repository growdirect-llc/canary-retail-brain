---
card-type: domain-module
card-id: canary-report
card-version: 1
domain: platform
layer: domain
feeds: []
receives:
  - canary-identity
  - canary-tsp
  - canary-alert
  - canary-fox
  - canary-analytics
tags: [reports, scheduled-exports, daily-batch, bulk-window, presigned-url, attestation]
milestone: M4
status: approved
last-compiled: 2026-04-30
---

# Canary Service: report

## What this is

Generates and serves merchant-facing reports — sales summaries, shrink reports, employee scorecards, vendor reconciliation, compliance attestations. Pre-defined templates (not ad-hoc query — that's canary-owl). Schedule management for recurring runs; each run produces a PDF/CSV/JSON/XLSX artifact in tenant-isolated object storage.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:8098` |
| Axis | B — Resource APIs |
| Tier mix | Reference (catalog, run lookups, schedule detail) · Change-feed (cross-template run tail) · Stream (immediate runs) · Daily batch (cron-driven schedule evaluator) · Bulk window (`/exports/{kind}` for transactions, items, customers, alerts, cases) |
| Owned tables | `app.report_templates`, `app.report_runs`, `app.report_schedules`, `app.export_jobs` |
| Run lifecycle | `QUEUED → RUNNING → COMPLETED → DELIVERED` (with FAILED → NOTIFIED) |
| Storage | `s3://canary-reports-prod/<merchant_id>/...` with 24h presigned URLs |

## Purpose

Templated reports + scheduled subscriptions + generic data exports. Daily-batch tier covers schedule cron evaluation; bulk-window tier covers async export jobs with presigned URL delivery.

## Dependencies

- canary-identity (JWT, tenant isolation in storage paths)
- canary-tsp / canary-alert / canary-fox (data sources)
- canary-analytics (precomputed aggregates)
- Object storage (S3-compatible)

## Consumers

- Merchant operators (report subscriptions)
- BI tools (scheduled exports)
- Compliance teams (attestation runs)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-report
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]], [[tier-daily-batch]], [[tier-bulk-window]]

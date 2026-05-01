---
card-type: infra-capability
card-id: axis-resource
card-version: 1
domain: platform
layer: infra
feeds:
  - infra-cadence-ladder
receives: []
tags: [axis, resource-api, rest, partner-facing, crb, microservice]
status: approved
last-compiled: 2026-04-30
---

# Axis: Resource APIs

## What this is

Axis B in the three-axis API model. Canary's outbound REST surface — the 32-service endpoint catalog that external systems (merchant tools, BI/dashboards, partner platforms, ops engineers) consume. Direct analogue of GK Software's Service API. The partner-facing canonical reference at [crb.growdirect.io](https://crb.growdirect.io) is curated from this axis.

## Purpose

When a third party (merchant IT, BI tool, integration partner) needs to read or mutate Canary state, they hit the Resource API. Tenant-isolated, JWT-gated, REST-only, organized by domain (sales/transactions, detection/cases, master data, operations, intelligence, identity, reports, accountability rails).

## Structure

Resource API endpoints organized by domain, each domain spans multiple cadence tiers:

| Domain | Services |
|---|---|
| Sales & Transactions | tsp, returns, analytics |
| Detection & Cases | alert, fox, chirp |
| Master Data | item, customer, employee, receiving (vendors) |
| Operations | asset, inventory, inventory-as-a-service, receiving, transfer, pricing |
| Intelligence | owl, analytics |
| Identity & Tenancy | identity |
| Reports | report |
| Accountability Rails | ildwac, l402-otb, blockchain-anchor, compliance, device-contracts, store-network-integrity, field-capture, commercial, raas, ecom-channel |
| Ops & Health | ops-dashboard, store-brain |

Total: 32 services with ~250 endpoint patterns documented as of 2026-04-30.

## Direction

Outbound — Canary serves data to external consumers.

## Conventions

- URL shape: `/{resource}` for collections, `/{resource}/{id}` for items, `/{resource}/{id}/{verb}` for actions
- Tenant isolation: `merchant_id` mandatory (path / query / JWT-implicit)
- Auth: JWT Bearer for all non-`/health` endpoints
- Pagination: cursor-based via `?cursor=&limit=`
- Errors: `{"error": {"code": "...", "message": "..."}}`
- Versioning: no URL versioning; breaking changes go through Hardening phase
- Tier declaration: every endpoint config carries `tier:` as required field

## Consumers

- Merchant IT building integrations
- BI/dashboard partners
- Ops engineers
- Other Canary services (inter-service REST)
- Curated subset published to crb.growdirect.io

## Sources

- `docs/sdds/go-handoff/microservice-architecture.md` — full per-service contracts (canonical source)
- [[Brain/wiki/canary-go-endpoint-library]] — partner-facing index with Tier column
- Per-service SDDs in `docs/sdds/go-handoff/<service>.md`

## Anti-pattern

Don't expose internal-only data on Axis B without explicit CRB curation review. Anything in the library is curation-eligible by default; anything that should NOT be partner-facing requires an explicit `crb_visible: false` flag.

## See also

- Card: [[axis-adapter]]
- Card: [[axis-agent]]
- Wiki: [[Brain/wiki/canary-go-endpoint-library]]
- SDD: `docs/sdds/go-handoff/microservice-architecture.md`

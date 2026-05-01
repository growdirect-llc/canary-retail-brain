---
card-type: domain-module
card-id: canary-item
card-version: 1
domain: merchandising
layer: domain
feeds:
  - canary-pricing
  - canary-inventory
  - canary-owl
receives:
  - canary-identity
tags: [item, master, catalog, upc, sku, hierarchy, attributes, bulk-import]
milestone: M4
status: approved
last-compiled: 2026-04-30
---

# Canary Service: item

## What this is

Read-side canonical for the merchandise catalog — item master records, hierarchical categories, alternate identifiers (UPC/EAN/SKU), per-item attributes, multi-location item authorization, and pricing-tier linkage.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:8090` |
| Axis | B — Resource APIs |
| Tier mix | Reference (lookups) · Change-feed (catalog tail) · Stream (mutations) · Bulk window (catalog imports) |
| Owned tables | `app.items`, `app.item_categories`, `app.item_attributes`, `app.barcodes`, `app.import_jobs` (item subset) |
| Bulk-import lifecycle | `QUEUED → VALIDATING → READY → FINALIZED` |

## Purpose

The canonical item catalog. **Not** authoritative for inventory positions (canary-inventory / canary-inventory-as-a-service) or pricing rules (canary-pricing) — strictly catalog. Bulk catalog refresh from POS adapters lands via `/imports/items` bulk-window pattern, closing one of the largest tier gaps in Axis A.

## Dependencies

- canary-identity (JWT, merchant scope)
- canary-pricing (read-only: tier linkage)
- canary-owl (publishes item updates for embedding refresh)

## Consumers

- All POS adapters (catalog reads for transaction enrichment)
- canary-pricing (item base price lookup)
- canary-inventory (item context)
- canary-compliance (item authorization checks)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-item
- Card: [[axis-resource]]
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]], [[tier-bulk-window]]
- Card: [[infra-cadence-ladder]]

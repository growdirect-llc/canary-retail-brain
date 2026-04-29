---
card-type: domain-module
card-id: retail-site-management
card-version: 2
domain: merchandising
layer: domain
status: approved
agent: ALX
feeds: [retail-merchandise-hierarchy, retail-replenishment-model, retail-demand-forecasting]
tags: [site-management, store-setup, location, site-hierarchy, store-lifecycle, DC, site-master]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

The site management model: how retail locations (stores, DCs, mixing centers) are defined, configured, opened, maintained, and closed — and how site master data governs all downstream operations that are location-dependent.

## Purpose

Every operational process in retail is site-specific. Replenishment runs per item per site. Pricing may vary by site. Assortment is defined per store. Inventory is tracked per location. The site master record is the anchor for all of this — if a site is misconfigured at setup, every process that depends on it inherits the error. Site management is infrastructure, not an afterthought.

## Structure

**Site types** — A site is any operational location that transacts merchandise or money:

| Site type | Purpose |
|-----------|---------|
| Store | Customer-facing retail location |
| Distribution Center (DC) | Receives bulk from vendors, picks and ships to stores |
| Mixing center | Cross-dock facility; receives and re-routes by store without put-away |
| Direct delivery vendor | Vendor location for DSD-sourced product |
| Wholesale customer | External customer (for wholesale/diverting operations) |

**Site master data** — A new site inherits configuration from a model site to reduce setup effort, then overrides where the new site differs. Key site master fields include:

- Formal hierarchy position (region, market, district)
- Site group memberships (climate zone, pricing zone, advertising zone, competition cluster)
- DC assignments (which DC services this store; fallback DC if primary is out of stock)
- Delivery schedule (days of week, appointment windows by carrier)
- RF and POS system configuration
- Replenishment parameters inherited from site group or overridden at site level
- Space and planogram configuration
- Linked personnel (market manager, district manager — for performance reporting)
- Store format and size characteristics

**Site setup process** — Opening a new site requires: assigning formal hierarchy position, defining site group memberships, configuring DC assignments and delivery schedule, loading replenishment parameters (from model site or site group defaults), loading assortment (from assortment module), loading opening inventory, and activating the site in the POS system. Each step is a dependency of the next.

**Site maps (planograms)** — The site map defines physical layout: which items are shelved in which locations, how much space each category receives, and the planogram ID that governs the visual presentation standard. Site maps are maintained in a planogram management system and linked to the site master. Changes to site maps (remodels, seasonal resets) require authorized updates to the space planning record.

**Site maintenance** — Ongoing maintenance covers: updating site group memberships as competitive or demographic characteristics change, adjusting DC assignments when logistics networks change, updating delivery schedules seasonally, and maintaining the personnel linkage as management roles change.

**Site close** — Closing a site requires: liquidating remaining inventory (transfers, markdowns, or write-offs), closing open purchase orders (cancel or redirect), settling outstanding AP, deactivating the site in all operational systems, and archiving the site's performance history. Site closure is a structured workflow, not a database delete.

## Consumers

The Replenishment module reads DC assignments and delivery schedules to route suggested orders. The Assortment module reads site group memberships to determine which items are listed at each store. The Pricing module reads pricing zone assignments to apply the correct price at each location. The Forecasting module uses site characteristics to assign seasonal profiles and demand parameters. The Operations Agent monitors site operational health — new sites with unusual demand patterns, sites approaching maximum replenishment capacity, and closed sites with residual inventory exposure.

## Invariants

- Every store must be assigned to exactly one primary DC and one pricing zone. Missing or duplicate assignments corrupt replenishment routing and pricing.
- Site group memberships must be maintained when business conditions change. A store still assigned to a "mild climate" group after moving to a "cold climate" market receives wrong replenishment parameters for seasonal items.
- Model-site inheritance is a starting point, not a permanent configuration. New sites must be reviewed and overridden where the model site's characteristics differ from the new site's reality.

## Platform (2030)

**Agent mandate:** Technical Agent owns site master provisioning — it configures site parameters, DC assignments, replenishment defaults, and POS integration at site setup. Operations Agent monitors site operational health continuously: new-site demand patterns, sites with unusual KPI behavior, and sites approaching capacity constraints. Business Agent reads site configuration for assortment and pricing decisions.

**Site master as agent configuration.** In traditional retail systems, site master data is a database table queried by humans. In Canary Go, site master data is the configuration layer that governs agent behavior per location. Operations Agent behavior at a given store is parameterized by: site group memberships (which determine which seasonality signals and competitive signals apply), DC assignments (which determine replenishment routing), pricing zone (which determines which price rule applies), and competition cluster (which determines relevant market benchmarks). The site master is not just a record — it is the configuration that makes per-location agent intelligence possible without embedding location-specific logic in the agent itself.

**Site setup as Technical Agent workflow.** Opening a new site is a Technical Agent-orchestrated workflow: provision site master record → assign hierarchy position and group memberships → configure DC assignment and delivery schedule → load replenishment parameters from model site → provision POS integration credentials → activate site in the platform → notify Operations Agent to begin monitoring. Technical Agent confirms prerequisites before advancing each step. A site is not live until the workflow is complete — not when a single table row is inserted.

**MCP surface.** `site_config(site_id)` returns site master data including hierarchy position, group memberships, DC assignment, and delivery schedule — the full agent configuration for a location. `site_health(site_id)` returns Operations Agent's current assessment: KPI status, open exceptions, and replenishment pipeline. `site_group_members(group_id)` returns all sites in a given pricing zone, climate zone, or competition cluster — the scoping filter for zone-level operations.

**RaaS.** Site configuration changes — format, cluster, regulatory zone, fixture data — are sequenced events. The configuration of a site at the time of any transaction must be reconstructible: a planogram reset must be timestamped against the reset date; a regulatory zone update must be effective from a specific date, not retroactively applied. `site_config(site_id)` from Valkey hot cache (sub-10ms; called on every agent operation for context). `site_group_members(group_id)` from SQL indexed on group_id. Site configuration change log append-only. Site master exportable for space planning system sync and regulatory zone mapping.

## Related

- [[retail-merchandise-hierarchy]] — site hierarchy is the location axis of the full hierarchy model
- [[retail-replenishment-model]] — site master drives DC assignment, delivery schedule, and replenishment parameters
- [[retail-demand-forecasting]] — site characteristics (format, climate zone, competition cluster) inform forecast parameters

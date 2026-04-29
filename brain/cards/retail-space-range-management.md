---
card-type: domain-module
card-id: retail-space-range-management
card-version: 1
domain: merchandising
layer: domain
status: approved
feeds: [retail-assortment-management, retail-site-management, retail-demand-forecasting]
receives: [retail-merchandise-hierarchy, retail-event-management]
tags: [space-management, planogram, range, SRD, fixture, display-hierarchy, space-allocation, reset, category-review]
last-compiled: 2026-04-29
---

## What this is

The space, range, and display (SRD) model: how retail floor space is allocated to categories, how item ranges are built into planograms for each store format, how changes are implemented in stores, and how the display hierarchy that governs all of this is maintained.

## Purpose

Space is the retailer's most constrained resource. Every category competes for it, every item requires it, and the wrong allocation — too much space to a slow-moving category, not enough to a high-velocity one — directly destroys margin through excess inventory and stockouts. Space management exists to make space allocation an analytically driven decision rather than a function of whoever last reset the aisle. The planogram is the executable output: it specifies exactly what goes where, in what quantity, for every fixture in every store. Without a planogram, replenishment is guessing, and the "right product in the right place" principle is aspirational rather than operational.

## Structure

**Display hierarchy** — A product-display group hierarchy that organizes items for shelving purposes, independent of but linked to the merchandise hierarchy. Display groups reflect how customers shop (e.g., "dog flea & tick" as a display group regardless of how it sits in the merchandise hierarchy). The display hierarchy is the currency in which space allocations, ranges, and planograms are defined. All store formats must have a display hierarchy that covers all product areas.

**Space and equipment data** — Accurate space management requires knowing precisely what physical space and fixture equipment each store has: fixture types, fixture dimensions, bay counts, aisle configurations, and any store-specific constraints (support columns, HVAC drops, door swing clearances). Space and equipment data must be maintained centrally and kept current through a store maintenance process — a planogram built against wrong fixture data will not fit on the actual shelf.

**Space allocation** — Top-down process: corporate sets category-level space allocations by store format and cluster. Allocation is driven by: category sales-to-space ratios (space productivity), category role (destination categories get more space), supply chain efficiency (adequate facings to support replenishment without excessive backstock), and customer shopping logic (adjacency of complementary categories). Store clusters receive different space allocations where customer demographics, store size, or competitive context differs materially.

**Range planning** — Within the allocated space, the category team defines the range: which items are in-range for each store format or cluster, at what Good/Better/Best tier balance, and with what import/corporate brand/branded mix. A range is store-cluster specific — a small-format urban store and a large-format suburban store have different ranges even within the same category. Range planning outputs feed the listing process in assortment management.

**Planogram building** — Planograms translate the range and space allocation into a specific shelf layout: item placement by fixture position, facings per item, shelf height and depth settings, and signage locations. Planograms are built in specialist space management software (JDA Space Planning, Intactix, Blue Yonder) and stored as data files that are synchronized to the merchandising system for listing purposes. A planogram is correct when: every item fits on the fixture, the allocated space is fully used, the range is represented without overstock, and replenishment can be executed efficiently.

**Category review and reset schedule** — Planogram changes are executed through a scheduled category review and reset process. The reset calendar specifies: which categories reset in which weeks, which stores are in scope, how many labor hours the reset requires, and which team executes it (store team, third-party reset crew, or a combination). The calendar must be coordinated with the category review cycle and the supply chain — reset items need to be on hand at the store before the reset, which means replenishment timing must account for the reset date.

**Store implementation** — Stores receive a reset brief: the new planogram, a shelf label set, a before/after photo guide, and a set of instructions for discontinued items (where to move them, when to discontinue ordering). Implementation accuracy is measured: the planogram-in-store compliance rate is a KPI. A planogram that is not correctly implemented is not delivering its designed sales and replenishment efficiency.

## Consumers

The Assortment Management module reads planogram outputs to set item listing by store — the planogram is the authoritative source of which items are listed at each location. The Replenishment module reads planogram capacity data (facings, shelf depth) to calibrate minimum on-shelf quantity targets. The Site Management module feeds store space and equipment data to the space planning system. The Operations Agent monitors planogram compliance (shelf audit results vs. planogram) and space productivity (sales per linear foot by category).

## Invariants

- Space allocations must be defined before planograms are built. A planogram built without a space allocation target will either under-use or exceed the available fixture space.
- The display hierarchy must be aligned with the merchandise hierarchy at the category level. A display group that spans multiple merchandise categories creates unresolvable reporting conflicts.
- Planogram changes must be synchronized to the listing system before the reset is executed. Resetting a shelf to a new planogram before the listing is updated creates a replenishment gap: the new items are not listed, so they will not be ordered.

## Platform (2030)

**Agent mandate:** Business Agent owns range decisions — item selection for each store cluster and format. Technical Agent manages planogram data synchronization to the listing and replenishment systems. Operations Agent monitors planogram compliance (shelf accuracy vs. planogram spec) and space productivity (sales per linear foot) continuously.

**Planogram as listing instruction.** In the Canary Go model, publishing a planogram is an event, not a file export. When a planogram is finalized in the space planning system, Technical Agent receives the planogram event, extracts the item-site listing instructions, and updates the assortment listing records automatically. Items added to the planogram become listed at the affected stores; items removed are de-listed. The replenishment wallet scope updates in the same transaction. The traditional failure mode — planogram changed, listing not updated, replenishment continues for discontinued items for three weeks — is eliminated by treating planogram publication as a system event that cascades to listing state.

**Space productivity as a continuous Operations Agent signal.** Traditional space management measures space productivity at category review time — typically twice a year. Operations Agent monitors sales-per-linear-foot by display group continuously, using validated sales data from the sales audit module. A display group whose space productivity drops below the category average for N consecutive weeks surfaces as a reset candidate without waiting for the scheduled review cycle.

**MCP surface.** `planogram(site_id, display_group)` returns the current active planogram with item placements and facing counts. `space_productivity(dept_or_group, site_id, period)` returns sales per linear foot vs. category average. `reset_schedule(site_id)` returns upcoming planned resets with date, labor estimate, and category scope. `listing_from_planogram(planogram_id)` returns the item-site listing set that a planogram drives — the bridge between space and replenishment.

**RaaS.** Planogram publication events are sequenced records that cascade to listing state changes. The planogram in effect at any store at any time must be reconstructible from the event sequence — this is required for reset compliance audits and for attributing replenishment behaviour to the correct shelf layout. The planogram publication event must be sequenced before the listing change event it triggers; a listing change without an attributed planogram event is a process failure. `planogram(site_id, display_group)` from SQL indexed on (site_id, display_group, effective_date). `space_productivity(dept_or_group, site_id, period)` must be pre-aggregated — not a real-time join over raw receipt events (all transactions × all display groups × all sites × rolling 52 weeks is prohibitive). Planogram data exportable to store reset teams and space planning systems; space productivity data exportable for category review.

## Related

- [[retail-assortment-management]] — planogram outputs drive item listing; range decisions feed planogram building
- [[retail-site-management]] — site space and equipment data is the physical constraint that planograms must respect
- [[retail-merchandise-hierarchy]] — display hierarchy is linked to merchandise hierarchy at category level
- [[retail-demand-forecasting]] — space capacity (facings, shelf depth) feeds replenishment safety stock parameters

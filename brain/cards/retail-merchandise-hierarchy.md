---
card-type: domain-module
card-id: retail-merchandise-hierarchy
card-version: 2
domain: merchandising
layer: domain
status: approved
feeds: [retail-demand-forecasting, retail-replenishment-model, retail-event-management, retail-operations-kpis]
receives: [retail-site-management]
tags: [merchandise-hierarchy, category, department, class, item-grouping, site-hierarchy, characteristics, mass-maintenance]
last-compiled: 2026-04-29
---

## What this is

The merchandise and site hierarchy model: the formal and informal grouping structures that organize items and locations for reporting, mass maintenance, pricing, replenishment, assortment management, and promotional planning.

## Purpose

Hierarchies are the organizational spine of retail operations. Without a well-designed hierarchy, mass maintenance (changing prices, replenishment parameters, or promotional terms across thousands of items) requires item-by-item edits. Reports become unreadable because there's no consistent aggregation structure. Planning is done at the wrong level of detail. The hierarchy determines what can be done at scale vs. what requires individual attention — and in retail, everything that can't be done at scale doesn't get done well.

## Structure

**Merchandise hierarchy — formal levels:**

| Level | Description |
|-------|-------------|
| Company | Top of hierarchy; global financial roll-up |
| Division | Major business segment or channel |
| Department | Primary buying and planning unit; buyer ownership assigned here |
| Class | Subcategory within department |
| Merchandise category | The category management unit — the level at which assortment decisions are made |
| Generic article | Style/product without specific size/color variation |
| Article (SKU) | The sellable unit with all attributes (size, color, UPC) |

**Merchandise hierarchy — informal groupings** — Items can belong to multiple informal groups simultaneously, independent of the formal hierarchy. Examples: "flea & tick" (cross-category product group), "clearance" (clearance-eligible items), "seasonal" (climate-dependent items). Informal groups support assortment management, promotional planning, and mass maintenance without requiring a formal hierarchy restructure.

**Characteristics** — Characteristics are attributes applied at any level of the merchandise hierarchy: buyer, climate zone, target customer, flavor, color family, brand tier. Characteristics can hold multiple values per item (a brush can target both dogs and cats). Reporting, mass maintenance, and assortment decisions can be driven by characteristics independently of the formal hierarchy. Characteristics that apply company-wide (e.g., "brand") are defined at the company level and inherited; characteristics that vary by category are defined at the category level.

**Site hierarchy — formal levels:**

| Level | Description |
|-------|-------------|
| Company | All locations |
| Region | Geographic grouping (for buying, pricing, and reporting zones) |
| Market | Sub-region or trading area |
| Site | Individual location: store, DC, mixing center, wholesale customer |

**Site groupings** — Like merchandise, sites can belong to multiple informal groups simultaneously: climate zone, pricing zone, advertising zone, competition cluster. A store can be in both the "cold climate" group and the "high-competition" group. Site groupings drive: stock allocation, promotional management, listing procedures, replenishment parameter mass maintenance, and sales performance benchmarking against similar stores.

**Mass maintenance** — The primary operational value of hierarchies is mass maintenance: the ability to change a pricing parameter, replenishment rule, or promotional assignment for an entire department or site group in a single operation. Mass maintenance requires authorization controls — ownership of each hierarchy level should be assigned, and changes above that level require elevated authorization.

**Personnel hierarchy** — A parallel hierarchy links people to merchandise categories or site groups for performance reporting. A buyer's performance is reported against the categories they own; a market manager's performance is reported against the stores they manage. The personnel hierarchy is independent of the formal merchandise and site hierarchies but can be linked to them for reporting.

## Consumers

The Replenishment module uses site groupings and merchandise categories to apply replenishment parameters via mass maintenance. The Pricing module applies pricing rules at hierarchy levels. The Forecasting module aggregates demand forecasts up the merchandise hierarchy for financial planning. The Assortment Management module uses merchandise categories and site groups to define store-specific assortments. The Operations Agent uses hierarchy-level aggregates for performance reporting and exception surfacing.

## Invariants

- An item belongs to exactly one path in the formal merchandise hierarchy (one department, one class, one category). Formal hierarchy membership is exclusive.
- Informal groupings are additive — an item can belong to any number of informal groups simultaneously without hierarchy conflict.
- Hierarchy restructuring (e.g., redefining class boundaries) must carry historical sales and inventory data into the new structure. A hierarchy change that breaks historical reporting is a business continuity event.

## Platform (2030)

**Agent mandate:** Hierarchy is infrastructure — it is not owned by one agent; it is consumed by all of them. Business Agent uses hierarchy for assortment planning and buyer performance reporting. Operations Agent uses hierarchy for KPI aggregation and exception scoping. Technical Agent maintains hierarchy configuration as system-of-record data and processes hierarchy changes as controlled events.

**Hierarchy as MCP filter context.** Every agent query in the Canary Go platform is hierarchy-scoped. When Operations Agent asks for shrink rate, the query specifies department and site group. When Business Agent asks for OTB balance, it specifies department and period. When a vendor receives a forecast, it is scoped to the relevant buyer and category. The hierarchy is the universal filter — not fetched once and cached in an agent's context, but passed as query parameters on every tool call. This keeps context windows narrow and enables precise agent scoping without loading the full merchant data model into memory on every query.

**Hierarchy changes as controlled events.** Traditional hierarchy restructuring is a DBA operation with unpredictable downstream effects. In Canary Go, hierarchy changes (moving a class to a new department, splitting a category) are controlled events: they carry historical data into the new structure, update active replenishment parameters and OTB wallets, and emit a hierarchy-change event that Business Agent uses to flag any downstream items needing buyer review. Technical Agent handles the structural change; Business Agent handles the business consequence.

**MCP surface.** `hierarchy_path(item_id)` returns the full formal hierarchy for an item. `site_groups(site_id)` returns all informal group memberships for a location. `hierarchy_members(level, id)` returns all items or sites belonging to a hierarchy node — the filter list for mass maintenance or query scoping. These are context assembly calls made before domain queries to keep those queries narrow and low-token.

**RaaS.** Hierarchy changes — reclassification, new nodes, restructuring — are sequenced events. The hierarchy version in effect at the time of any transaction must be reconstructible: a sale must be attributable to the node in effect when it occurred, not the current hierarchy. Historical reporting breaks when hierarchy changes are not versioned. `hierarchy_path(item_id)` from Valkey hot cache (sub-10ms; called on every transaction for classification). `hierarchy_members(level, id)` from SQL indexed on (level, parent_id). Hierarchy change log append-only. Full hierarchy exportable for external reporting and period-over-period comparison when structure has changed.

## Related

- [[retail-site-management]] — site master data that populates the site hierarchy
- [[retail-demand-forecasting]] — hierarchy levels determine how forecasts are aggregated and parameters are mass-maintained
- [[retail-event-management]] — promotional events target items and sites via hierarchy and grouping references
- [[retail-operations-kpis]] — KPI roll-ups follow hierarchy structure

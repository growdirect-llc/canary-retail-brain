---
card-type: domain-module
card-id: retail-assortment-management
card-version: 1
domain: merchandising
layer: domain
status: approved
feeds: [retail-demand-forecasting, retail-replenishment-model, retail-site-management]
receives: [retail-merchandise-hierarchy, retail-event-management, retail-vendor-lifecycle]
tags: [assortment, item-master, listing, planogram, category-management, item-setup, discontinue, new-item, SKU]
last-compiled: 2026-04-29
---

## What this is

The assortment management model: how items are selected, set up, listed at stores, maintained through their lifecycle, and discontinued — and how category strategy governs assortment decisions from annual planning through individual item execution.

## Purpose

Assortment management determines what the retailer sells and where. It translates category strategy into a specific item set listed at specific stores, with accurate item master data that every downstream process depends on. Without disciplined assortment management, replenishment orders the wrong things, planograms break, and the financial cost of carrying underperforming items accumulates invisibly. The item master record — created in this process — is the anchor for pricing, purchasing, receiving, forecasting, and financial reporting. If it is wrong at setup, everything downstream inherits the error.

## Structure

**Assortment planning** — The process of determining an optimal product offering within a category that achieves consumer fulfillment and financial results. It operates at two levels simultaneously: the corporate category plan (what the chain carries) and the local assortment (which stores carry which items). A single corporate listing does not mean uniform assortment across all stores — micro-market assortment variation is a design requirement, not an exception.

**Category strategy** — Annual category strategy defines the role and objectives of each merchandise category. Four category roles are standard:

| Role | Strategic purpose |
|------|-----------------|
| Traffic builder | High-frequency purchase, drives store visits |
| Destination | Specialty depth, differentiates the retailer |
| Profit contributor | Margin-optimized, less traffic-sensitive |
| Convenience | Impulse / add-on, not core assortment driver |

Category strategy must be established at the right hierarchy level (department, class, or merchandise category) before item selection begins. Strategy drives the assortment criteria: Good/Better/Best tiering, import penetration target, corporate brand penetration, and acceptable new item percentage.

**Category review and planogram calendar** — Assortment changes are scheduled, not ad hoc. The category review calendar specifies: which categories are reviewed each period, the review type (full reset vs. targeted edit), labor constraints, and store execution timing. The planogram calendar is a dependent artifact — planogram changes must be coordinated with store labor capacity and category review cycles.

**Item lifecycle** — Every item moves through a defined set of status states:

| Status | Operational meaning |
|--------|-------------------|
| New | Item created, not yet active |
| Active | Replenishment and sales enabled |
| Discontinued sale | Sale blocked; existing stock may be cleared |
| Discontinued shipment | No new receipts; existing orders complete |
| Discontinued order | No new POs; existing shipments complete |
| Hold | Temporary block; investigation or recall |
| Purge | Record archived; removed from active system |

Status transitions are controlled — each transition has specific blocking logic in purchasing, receiving, and POS. A hazardous recall item must be blocked at POS, not just in purchasing.

**New item setup** — Item master creation is a structured data entry process, not a free-form record. Required data at setup includes: UPC/EAN/JAN, merchandise hierarchy assignment (division → department → class → category), vendor and vendor style number, all units of measure (selling, purchasing, inner pack, warehouse transfer) with dimensions and weights, item status, country of origin, replenishment source, and allowance/rebate structure. Item master data feeds WMS, POS, replenishment, pricing, and financial reporting — missing or inaccurate data at setup creates downstream failures that are expensive to trace.

**Listing** — An item is "listed" at a store when it is authorized for sale and replenishment at that location. Listing is controlled by planogram assignment: when a planogram is applied to a store, the items on that planogram are listed at that store. De-listing is the mechanism for removing an item from a store's active assortment without discontinuing it chain-wide.

**Discontinuation** — Discontinuing an item requires staged execution: stop purchasing (block new POs), sell through existing stock, apply clearance pricing if needed, remove from planograms and de-list at affected stores, then purge the item record. Rushed discontinuation without clearing inventory creates phantom stock and residual liability.

**Planogram management** — Planograms define physical shelf layout: which items occupy which fixture positions, how much space each item receives, and the visual presentation standard for each category. Planograms are maintained in a space management system (e.g., Intactix/JDA) and the resulting listing assignments are synchronized to the item master. Planogram-driven listing is the control mechanism that ensures replenishment only runs for items that are physically on the shelf at a given store.

## Consumers

The Replenishment module reads active listings to determine which items to order at each store — only listed items at a given site generate replenishment orders. The Pricing module reads item master data for price rule application. The Receiving module reads item status to block receipt of discontinued-order items. The Vendor Agent reads new item data to confirm vendor-side setup (UPC registration, pack configuration). The Operations Agent monitors assortment health: new item adoption rate, underperforming item age in assortment, and listing-replenishment discrepancies (items listed but never ordered, items ordered but not listed).

## Invariants

- An item must be fully set up in the item master before a PO can be created against it. POs with item data errors corrupt the receiving and financial chain.
- Listing is controlled by planogram, not by manual data entry. Items replenished at a store that is not on an applicable planogram indicates a process failure.
- Item status transitions must follow the defined sequence. Jumping from Active to Purged without a Discontinue step leaves open purchase orders and price rules orphaned.

## Platform (2030)

**Agent mandate:** Business Agent owns assortment strategy — category role assignment, item selection decisions, and new item introduction planning. Technical Agent owns item master provisioning — it executes the new item setup workflow, validates all required data elements before activation, and pushes item data to downstream systems (POS, WMS, vendor MCP endpoint). Operations Agent monitors assortment health continuously: adoption rates on new items, age of underperforming items in the active assortment, and listing-replenishment discrepancy signals.

**Item master as smart contract initialization.** When a new item is set up and a vendor is smart-contract-native, item activation is also a contract event on the AVAX vendor subnet: the item's agreed cost, allowance structure, and packing specifications are written to the contract. Subsequent POs for that item reference the contract state, not a manually maintained price file. Cost changes require a signed contract amendment — not a buyer verbal approval that doesn't make it into the system. This eliminates the "the cost on the PO doesn't match what we agreed" category of invoice discrepancy.

**Listing as L402 gate.** In the Canary Go model, listing state is the gate on replenishment wallet calls. `otb_balance(dept, period)` only considers OTB for listed items at each site. An item de-listed from a store immediately removes it from that store's replenishment pipeline — no manual replenishment parameter update required. Planogram-driven listing changes propagate to the OTB wallet scope automatically.

**Operations Agent assortment monitoring.** Business Agent does not review every item's performance manually. Operations Agent monitors: (1) new items with no sales in the first N weeks post-listing — adoption failure signal; (2) active items with declining velocity below a threshold for M consecutive weeks — rationalization candidate; (3) items listed at stores not on any active planogram — phantom listing that will cause phantom replenishment. These surface as exceptions to the merchant dashboard, not as periodic category review reports.

**MCP surface.** `item_status(item_id)` returns current lifecycle status and listing count by site. `assortment(site_id, dept)` returns active listings for a location and department. `new_item_pipeline(buyer_id)` returns items in setup workflow with missing data fields flagged. `underperforming_items(dept, threshold_weeks)` returns active items below velocity threshold — the assortment rationalization queue. Single-call, agent-readable.

**RaaS.** Item lifecycle transitions — new, active, discontinued — are sequenced events. Listing changes triggered by planogram publication must be sequenced after the planogram event that caused them; a listing change that cannot be attributed to a planogram event is a process failure. `item_status(item_id)` from Valkey hot cache (sub-10ms; called on every replenishment check). `assortment(site_id, dept)` from SQL indexed on (site_id, dept, status). Item master in SQL (relational — items link to hierarchy, vendors, sites); listing event log append-only. Item master exportable for vendor collaboration, POS configuration, and space planning system synchronisation.

## Related

- [[retail-merchandise-hierarchy]] — the hierarchy structure that items are assigned to at setup
- [[retail-site-management]] — site groups determine which stores receive which planograms
- [[retail-demand-forecasting]] — new item like-item forecasting depends on item master data
- [[retail-replenishment-model]] — listing state gates replenishment order generation
- [[retail-vendor-lifecycle]] — vendor setup is a prerequisite for item setup

---
card-type: domain-module
card-id: retail-backroom-cost-transfer
card-version: 1
domain: merchandising
layer: domain
feeds:
  - platform-closed-loop-attribution
  - retail-inventory-audit
  - retail-chargeback-matrix
receives:
  - retail-purchase-order-model
  - retail-receiving-disposition
  - retail-vendor-lifecycle
  - retail-assortment-management
tags: [backroom, carrying-cost, margin, cost-transfer, inventory, shrink, attribution, upstream, accountability, open-to-buy]
status: approved
last-compiled: 2026-04-29
---

# Retail: Backroom Cost Transfer

## What this is

The pattern by which upstream decision-makers — buyers, planners, vendors, distribution — discharge the consequences of bad commercial decisions into the store's back room, where the cost is absorbed by store operations rather than attributed to its source.

## Purpose

Names and closes the most common accountability escape route in retail. In an open-loop system, excess inventory pushed to the back room becomes the store's problem: it consumes labor bandwidth, occupies space, ties up working capital, and ages into shrink. The upstream decision-maker who created the inventory position bears none of it. This card defines the pattern, the attribution path, and the invariants that prevent cost transfer in a closed-loop system.

## Structure

**How the transfer happens:**

1. A buying decision produces excess inventory — wrong product, wrong quantity, wrong timing, vendor overshipment, failed promotion clearance
2. The inventory cannot sell through on the floor at planned velocity
3. Rather than resolving the position (markdown, return, vendor credit), it is moved to the back room
4. In an open-loop system, the carrying cost now accrues to the store's P&L — labor to manage it, space it consumes, working capital it ties up, eventual markdown or damage it produces
5. The upstream offender's performance metric is unaffected

**Why carrying cost is a margin cost, not an ops cost:**

Every day an inventory position ages in the back room, it is:
- Earning zero revenue (it is not on the selling floor)
- Consuming space that could hold sellable product
- Consuming labor bandwidth (receiving, sorting, relocating, counting)
- Tying up working capital that could fund open-to-buy on productive SKUs
- Accumulating the risk of damage, expiry, and obsolescence

None of these are store costs if the store did not make the upstream decision. They are deferred consequences of the buying, planning, or vendor decision — relocated to a room with less visibility, not resolved.

**Attribution path by source:**

| Source of excess | Attribution node | Resolution mechanism |
|-----------------|-----------------|---------------------|
| Buyer over-buy | Module C / Buyer | Buyer performance metric; OTB impact on next cycle |
| Vendor overshipment | Vendor / Module D | Vendor chargeback; return-to-vendor claim |
| Failed promotion clearance | Module P / Commercial | Promotional ROI metric; markdown cost charged to campaign |
| Late delivery (demand window missed) | Module D / Vendor | Vendor SLA breach; refused receipt or negotiated credit |
| Allocation misfire (wrong store) | Module S / Planner | Reallocation cost charged to planning decision |

## Invariants

- **Backroom location does not change attribution.** A unit in the back room carries the same cost ownership as when it was on the receiving dock. Moving it does not transfer the accountability.
- **Carrying cost accrues to the source, not the store.** The aging clock starts at the upstream decision event — the PO date, the allocation date, the promotional plan date — not at the date the inventory was moved to the back room.
- **Back-room inventory must have a source PO and a buyer on record.** Inventory without a traceable upstream record is itself an attribution failure and must be surfaced, not counted as store shrink.
- **Resolution is not deferral.** A position is resolved when it is sold through, returned, credited, or officially written down with the cost attributed. Moving it to a different location, a different store, or a different period is deferral.

## Signal

Back-room inventory aging report by source PO, buyer, and days-on-hand is the primary signal. Secondary signals:
- Markdown rate above plan by category and buyer
- Open-to-buy utilization below plan (capital tied up in back room cannot fund new buys)
- Labor hours above plan for back-room management tasks
- Cycle count variance from back room vs. selling floor (back room has lower visibility and higher shrink risk)

## Consumers

- **Module C (Commercial)** — buyer accountability; back-room aging by buyer feeds performance metric
- **Module D (Distribution)** — vendor overshipment attribution; return-to-vendor and chargeback triggers
- **Module Q (Loss Prevention)** — back-room shrink monitoring; elevated risk surface vs. selling floor
- **Controller agent** — cross-module escalation when back-room aging indicates a commercial accountability gap that has not been resolved

## Related

- [[Brain/wiki/cards/platform-closed-loop-attribution|Platform: Closed-Loop Attribution]] — the governance model this pattern violates and that Canary enforces
- [[Brain/wiki/canary-closed-loop-cost-attribution|Closed Loop — Full Wiki Article]] — complete context including all five layers and the full offender taxonomy
- [[Brain/wiki/cards/retail-chargeback-matrix|Retail: Chargeback Matrix]] — vendor chargeback execution for overshipment and SLA breach
- [[Brain/wiki/cards/retail-receiving-disposition|Retail: Receiving Disposition]] — what happens at the receiving dock; where the upstream accountability event is first recorded
- [[Brain/wiki/cards/retail-inventory-audit|Retail: Inventory Audit]] — physical sweep mechanics; back room is a distinct location with its own audit cadence
- [[Brain/wiki/cards/retail-vendor-scorecard|Retail: Vendor Scorecard]] — overshipment and late delivery pattern tracking at the vendor level

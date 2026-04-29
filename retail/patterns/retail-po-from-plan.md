---
type: wiki
status: active
date: 2026-04-26
owner: GrowDirect LLC
tags: [retail, purchase-orders, allocation, replenishment, forecasting, canary]
related:
  - Brain/wiki/retail-merchandise-planning-otb.md
  - Brain/wiki/retail-promotion-workflow.md
  - Canary-Retail-Brain/modules/J-forecast-order.manifest.yaml
  - Canary-Retail-Brain/modules/D-distribution.manifest.yaml
  - Brain/wiki/ncr-counterpoint-endpoint-spine-map.md
source-intakes:
  - Brain/raw/inbox/sap-fashion-workshop-1998.md
  - Brain/raw/inbox/sap-apparel-workshop-promotions-pricing-po.md
last-compiled: 2026-04-26
needs-review: 2026-05-10
---

# Retail Purchase Order Generation from Plan

## Governing Thesis

In specialty retail, purchase orders are not discrete buying decisions — they are the downstream output of a planning process that has already committed to a sales plan, an allocation, and an OTB budget. The PO is the last step, not the first. Any system that treats PO entry as a standalone transaction disconnects the buying decision from the financial plan, breaking the feedback loop that controls inventory investment.

Canary module J (Forecast/Order) owns this chain. Its design requirement is tight, bidirectional integration with the merchandise plan in P, the allocation logic in D, and the receiving and cost flows in F.

---

## The PO Generation Chain

```
Seasonal Plan (P)
  ↓ creates
Unit Plan / Allocation (P → J)
  ↓ generates
Purchase Order (J)
  ↓ sent to
Vendor (via EDI or manual)
  ↓ received at
DC / Store (D)
  ↓ updates
OTB remaining (P)
```

Each arrow is a live link. A change upstream must propagate downstream automatically, and actual receipts must flow back upstream to close the OTB loop.

---

## Purchase Order Contents

A retail PO must contain more than a standard procurement PO. Required fields:

**Header:**
- Total cost (all lines)
- Total retail (all lines)
- Markup % at header
- Distribution Center identifier (for cross-dock / pre-distributed POs)
- Terms (payment, FOB, cancellation date)
- Spend-to-date with this vendor by category for the month and season

**Line level:**
- Cost per unit
- Retail per unit
- Markup % per line
- Gross margin per line
- Cancellation date per line (auto-cancel remaining quantity after date)
- Allocation summary: units per store or per DC
- Ability to drill down to full store-level allocation from the line

**Views required on the PO:**
1. Item summary (all lines, totals)
2. Single line with full allocation detail
3. Total units across all lines
4. Total cost / total retail across all lines
5. Allocation of all styles to a single store (the "what is Store 03 getting?" view)
6. Allocation matrix by color × size for a style (the "show me the size run" view)

---

## Pre-distributed vs. Bulk POs

### Pre-distributed (Cross-dock)

Allocation is set before the PO is sent to the vendor. The vendor packs merchandise by store, ships to DC, DC scans each carton directly to the outbound store truck. No put-away at DC.

Requirements:
- Allocation must be attached to the PO before it is released to vendor
- PO must carry store-level allocation at the line level for EDI transmission
- DC address and store number must appear on vendor carton label
- Any allocation change after PO transmission must generate a PO change EDI message to the vendor

### Bulk (Post-distribution)

PO placed in total; allocation determined at DC receiving or just before shipment. Normal DC put-away, followed by store-pick or automated sortation.

Requirements:
- PO commitment is visible as on-order at the store from the moment it is created, even before allocation is finalized
- Allocation must be executable from inside the PO view — buyer should not have to navigate to a separate allocation module

---

## Allocation-to-PO Integration Requirements

### Allocation created from PO (new season order)

Process: plan → unit plan → allocation table → PO generated from allocation.

The allocation table drives the total PO quantity: the sum of store allocations becomes the order quantity. If the allocation changes (a store is dropped, quantities revised), the PO must update automatically.

### Allocation attached to existing PO (re-order)

Process: PO exists at total quantity → allocation added afterward (e.g., a re-order placed before the selling pattern is known).

The allocation must be attachable to the existing PO. Once attached, it follows the pre-distribution requirements above.

### Short-ship reconciliation

When the vendor delivers less than the PO quantity, the allocation must be revised at goods receipt. The system must decide which stores' allocations to reduce. Simple proportional reduction (apply the shortage ratio to all stores equally) is the default — but it systematically underserves small-volume stores. The correct logic:

1. First, protect minimum viable quantities for top-tier stores
2. Distribute the remaining available quantity proportionally among remaining stores
3. Bottom-tier stores may receive zero if the shortage is severe

Short-ship must also trigger a PO change at the line level — cancelling or back-ordering the remaining quantity per buyer instruction.

---

## Replenishment (Basic / NOS Items)

Replenishment is the continuous reorder engine for never-out-of-stock items. It runs separately from the seasonal allocation cycle.

### Replenishment Logic

1. **Reorder point:** set initially by the buyer (based on anticipated lead time × weekly sales); updated automatically after N months based on actual sales trend
2. **Reorder quantity:** typically minimum vendor pack or minimum order value; ensures the system never orders a quantity below vendor minimums
3. **Safety stock:** a buffer above the reorder point to absorb forecast error and lead time variation
4. **Weeks of supply target:** the buyer's forward coverage goal; drives reorder point and safety stock jointly

When an item's projected on-hand (current SOH + on-order − expected sales) falls below the reorder point at any store-article combination, the system generates a purchase requisition for review or auto-converts to a PO per configuration.

### Promotional Demand and Replenishment

A known replenishment hazard: if an upcoming promotion is not visible to the replenishment engine, the system may generate a normal replenishment order for the item at the same time a promotional order is being planned — resulting in double-ordering.

The fix: replenishment must read the promotion module for any active or planned promotions on the item. Planned promotional demand is added to the forecast horizon, and the replenishment engine will not generate a competing order for the same period.

Post-event: promotional lift is tagged separately so it does not inflate the base forecast used for future reorder point calculations.

### Counter Stock

Some categories (display items, tester fixtures, seasonal displays) need a reserved quantity that is never available for sale. This "counter stock" is functionally blocked stock, but it must be managed at a more granular level than a safety stock flag — the buyer needs to specify the counter stock quantity per store, and the replenishment system must exclude it from available SOH.

---

## New Article Creation at PO Entry

In fashion retail, buyers encounter new styles at trade shows or vendor visits and need to create a PO on the spot — before the item master exists in the system. The process:

1. Buyer enters vendor number, style, color, size range, cost, retail, season code
2. System auto-creates the article master from the merchandise reference article (a template for the category) + the data entered at PO
3. PO is created simultaneously with the article master
4. When buyer returns from the market / trade show, the PO and article master are uploaded or synchronized to the main system

Article creation structures by type:

| Article Type | Variant Structure |
|---|---|
| **Fashion** | Generic article → ident number (color/style grouping); UPC at style level, not size level |
| **High Fashion** | Individual serial number per unit (mink coat, jewelry) — tracked for provenance |
| **NOS / Basic** | Generic article → color variant → size variant; UPC at color+size level |
| **Pre-pack (branded)** | Pre-pack = vendor assortment of sizes; tracked at pack level, not variant level |
| **Pre-pack (private label)** | Broken at DC; tracked at individual color+size level |

---

## PO Visibility and OTB Impact

Buyers need to see the OTB impact of a potential PO *before* committing it. The standard failure mode: as soon as a PO is saved, OTB is consumed — there is no preview step.

Required behavior:
1. Buyer builds a draft PO (or a set of purchase requisitions)
2. System shows: if these are committed, here is your remaining OTB for this month by category and buyer
3. Buyer approves, PO is committed, OTB updates

This preview must operate against the live OTB budget, not a static snapshot.

---

## Early Warning and PO Lifecycle Monitoring

Standard PO lifecycle events that require alerts:

| Event | Alert |
|---|---|
| PO transmitted to vendor | Confirm transmission |
| Line cancellation date approaching | Alert buyer N days before; prompt to extend or cancel |
| Vendor has not acknowledged PO | Alert after X days |
| Vendor ships PO | Receipt confirmation; partial ship flag if quantity short |
| PO being received at DC | Progress update; flag early if % complete is low at midpoint |
| Back-order decision required | Present accept-back-order vs. cancel-balance choice |

---

## Canary Module J Implications

| Retail Requirement | Canary J Behavior |
|---|---|
| PO generated from allocation | J consumes allocation output from P; creates PO at the store-level detail |
| Pre-distributed PO with EDI | J stores store-allocation at line level; EDI mapping in module C (Commercial) |
| Short-ship reconciliation | J invokes re-allocation logic at goods receipt; updates store commitments in D |
| Replenishment engine | J runs the demand-driven reorder cycle for basic/NOS items |
| Promotional demand visibility | J reads P's promotion calendar before generating replenishment suggestions |
| New article creation | J calls article master creation as part of PO entry workflow |
| OTB preview before commit | J presents OTB impact in a confirmation step before PO status goes to "open" |
| PO lifecycle alerts | J emits events into Canary's alert infrastructure (Q-module detection surface) |

---

## Related

- **Merchandise planning and OTB:** [[Brain/wiki/retail-merchandise-planning-otb]]
- **Promotion workflow:** [[Brain/wiki/retail-promotion-workflow]]
- **Canary module J:** [[Canary-Retail-Brain/modules/J-forecast-order.manifest.yaml]]
- **Canary module D:** [[Canary-Retail-Brain/modules/D-distribution.manifest.yaml]]
- **NCR Counterpoint endpoint map:** [[Brain/wiki/ncr-counterpoint-endpoint-spine-map]]
- **Source intakes:** [[Brain/raw/inbox/sap-fashion-workshop-1998]] · [[Brain/raw/inbox/sap-apparel-workshop-promotions-pricing-po]]

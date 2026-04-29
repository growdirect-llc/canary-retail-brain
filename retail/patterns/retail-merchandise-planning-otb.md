---
type: wiki
status: active
date: 2026-04-26
owner: GrowDirect LLC
tags: [retail, merchandise-planning, otb, allocation, apparel, canary]
related:
  - Brain/wiki/canary-location-item-data-model.md
  - Brain/wiki/canary-module-p-pricing-promotion.md
  - Canary-Retail-Brain/modules/P-pricing-promotion.manifest.yaml
  - Canary-Retail-Brain/modules/J-forecast-order.manifest.yaml
  - Canary-Retail-Brain/modules/D-distribution.manifest.yaml
source-intakes:
  - Brain/raw/inbox/sap-fashion-workshop-1998.md
last-compiled: 2026-04-26
needs-review: 2026-05-10
---

# Retail Merchandise Planning and Open-to-Buy

## Governing Thesis

Specialty retail buying operates on a planning pyramid: financial plan feeds assortment plan feeds unit plan feeds allocation and purchasing. Every level is linked in both directions — top-down targets constrain bottom-up builds, and actual results flow back up to revise forward commitments. Open-to-Buy (OTB) is the live view of that pyramid: purchasing authority remaining after committed receipts are subtracted from the plan.

Canary modules P (Pricing/Promotion) and J (Forecast/Order) own the operating layer of this pyramid. The planning methodology documented here is the industry standard that those modules must serve.

---

## The Planning Pyramid

### Level 1: Seasonal Merchandise Plan (Department / Category)

The top-level financial plan. Built before season opens; updated throughout. Key figures:

| Key Figure | Definition |
|---|---|
| Sales | Net sales in currency |
| Average Stock | Total period stock ÷ number of periods |
| Receipts | Planned merchandise received |
| Markdowns | Original retail − revised retail |
| Markup % | (Retail − Cost) ÷ Retail |
| Gross Margin | Sales − gross COGS |
| Turnover | Sales ÷ Average Stock |
| Shrinkage | Estimated inventory loss |
| GMROI | Gross Margin ÷ Average Inventory Cost |

Plan is created at department level, spread by month, and built simultaneously top-down (corporate) and bottom-up (store) — the two are reconciled before final approval.

### Level 2: Store / Location Plan

Location plans are spread from the corporate seasonal plan, adjusted for regional selling patterns, new store openings, and store groups (comp vs. non-comp). Never a flat per-store fraction of corporate — each location has its own seasonal index.

### Level 3: Class / Vendor / Article Category Plan

Below the department, plans are created by classification or vendor within a category. Article categories at this level:

- **Fashion** — seasonal; not perpetually in stock; planned by style and receipt window
- **Basic / NOS** — never-out-of-stock; planned by weeks-of-supply and reorder point
- **Promotional** — specifically purchased for a defined promotion; demand treated separately from base

### Level 4: Assortment Plan

At the style level, once articles are known. Maps specific items to specific stores or store groups for a season. Feeds allocation.

### Level 5: Unit Plan

Dollar plan converted to units using the category's average retail price. Drives allocation quantities and purchase order sizing.

---

## Open-to-Buy (OTB)

**Definition:** OTB = Total Receipt Plan − Committed Receipts already on order for the period.

OTB is not a one-time calculation — it is a rolling operating forecast (ROF) that updates as:

- Planned sales change
- Markdowns execute
- Stock levels deviate
- New purchase orders are committed

### OTB State Changes

| Event | OTB Effect |
|---|---|
| PO created / committed | Reduces OTB for the PO's receipt month |
| PO cancelled | Restores OTB for that month |
| Sales exceed plan | May reduce required future receipts; loosens OTB |
| Sales miss plan | Excess stock builds; tightens future OTB |
| Markdown executed | Reduces retail value; adjusts margin/markup key figures |

### OTB Approval Gates

Multi-tier approval workflow is standard. A buyer can commit up to a dollar threshold autonomously; above that, workflow routes to department head, then VP Merchandising. Once a plan period is locked, changes require an override approval.

---

## Allocation

Allocation is the distribution of a planned receipt across stores before or at the time of the purchase order. It is the operational bridge between the merchandise plan and the PO.

### Allocation Methods (standard)

| Method | When Used |
|---|---|
| **Actual selling** | Fill-in of existing item; stores ranked by sales history |
| **Plan need** | New item or new season; each store brought to stock plan |
| **Plan need + actual** | Hybrid; ensures minimum in-stock while respecting historical performance |
| **Weeks of supply** | Target weeks-on-hand at all stores; system calculates units needed given current SOH + on-order + sales trend |

### Allocation Inputs Required

For any allocation method, the system must have access to:
- Store-level on-hand
- On-order by store (committed receipts already allocated)
- Sales trend (last N weeks) for the item or a like item
- Like-item history for new articles with no own history
- Store group membership (for regional allocation targeting)

### Pre-pack Allocations

Fashion and branded vendors often ship in pre-packs — a vendor-defined assortment of sizes and/or colors. Allocation rules must operate at the pre-pack level, not the individual variant level. When a partial shipment occurs, the allocation system must determine which stores receive partial pre-packs and handle the size/color remainder rather than defaulting to proportional distribution (which systematically underserves small-volume stores).

### Allocation and the PO

Allocation can attach to a PO in two directions:
1. **Pre-distributed PO** — allocation is set before the PO is sent to the vendor; vendor packs by store, merchandise cross-docks at DC
2. **Post-distribution** — PO committed in bulk; allocation assigned before or at DC receiving

In both cases, the allocation rule must be visible from the PO, and any change to the allocation must propagate back to the PO (and if EDI is in play, trigger a PO change message to the vendor).

---

## Layout Planning

Layout planning links merchandise assortment to physical store capacity. The plan is built against actual square footage and fixture counts per location, ensuring that the planned assortment physically fits the store.

Use cases:
- Seasonal floor moves: merchandising calendar drives fixture rotation
- New store setup: assortment sized against actual square footage
- Capacity gate on ordering: items cannot be received beyond fixture capacity

Canary module S (Space, Range, Display) owns this gate in the spine.

---

## Merchandise Hierarchy and Plan Synchronization

A recurring failure mode in planning systems: hierarchy reorganizations break historical comparability. When a style is moved to a new category mid-season, historical sales in the old category must be restated to the new one — otherwise plan vs. actual comparisons are invalid, and allocations generated from the old hierarchy produce wrong distributions.

**Canary implication:** Module P and J must maintain a history of hierarchy assignments with effective dates so that any plan comparison crosses the same product structure.

---

## Canary Module Mapping

| Planning Concept | Canary Module | Notes |
|---|---|---|
| Seasonal plan, OTB | P — Pricing/Promotion | OTB is a forward-looking pricing constraint |
| Unit plan, allocation | J — Forecast/Order | Allocation output drives PO creation in J |
| Store allocation distribution | D — Distribution | Stock transport orders and DC-to-store flow |
| Assortment plan, listing grade | S — Space, Range, Display | Ordering gate: item must have planogram assignment |
| Historical sales for allocation | T — Transactions | Source of actual sales by store by item |
| Location hierarchy | N — Device / Places | Store master and store group membership |

---

## Key Retail Planning Principles (Practitioner View)

These are standing invariants, not vendor-specific:

1. **Plan in dollars, execute in units.** Financial plan sets the dollars; unit plan derives quantities using average retail. The conversion must use actual price records, not a static average stored in configuration.
2. **Multi-level linkage is non-negotiable.** A change at any level must propagate up and down the hierarchy automatically. Manual reconciliation at scale is operationally impossible.
3. **What-if modeling before commitment.** Buyers require the ability to simulate the effect of a price change, markdown, or OTB adjustment before executing the transaction.
4. **Comp vs. non-comp store separation.** New stores need like-store modeling; they cannot be planned from scratch. Comp store analysis is the primary performance benchmark.
5. **Promotional demand is separate from base demand.** When an item is promoted, the lift must be quarantined from the base forecast to avoid inflating future replenishment projections.

---

## Related

- **Canary module P:** [[Canary-Retail-Brain/modules/P-pricing-promotion.manifest.yaml]]
- **Canary module J:** [[Canary-Retail-Brain/modules/J-forecast-order.manifest.yaml]]
- **Canary module D:** [[Canary-Retail-Brain/modules/D-distribution.manifest.yaml]]
- **Promotion workflow:** [[Brain/wiki/retail-promotion-workflow]]
- **PO from plan:** [[Brain/wiki/retail-po-from-plan]]
- **Source intake:** [[Brain/raw/inbox/sap-fashion-workshop-1998]]

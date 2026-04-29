---
type: wiki
status: active
date: 2026-04-26
owner: GrowDirect LLC
tags: [retail, promotions, pricing, markdown, workflow, canary]
related:
  - Brain/wiki/retail-merchandise-planning-otb.md
  - Brain/wiki/retail-po-from-plan.md
  - Canary-Retail-Brain/modules/P-pricing-promotion.manifest.yaml
source-intakes:
  - Brain/raw/inbox/sap-apparel-workshop-promotions-pricing-po.md
last-compiled: 2026-04-26
needs-review: 2026-05-10
---

# Retail Promotion and Pricing Workflow

## Governing Thesis

Promotions and pricing changes in specialty retail are not simple price edits — they are planned events with approval gates, stock consequence, and post-event analysis requirements. The same workflow structure governs both: plan → model → approve → execute → monitor → recap. Canary module P owns this workflow in the spine; its implementation must support the full lifecycle, not just the price record.

---

## Promotion Lifecycle

### Phase 1: Planning

Before a promotion is created, buyers and planners need access to:

| Information Required | Where It Comes From |
|---|---|
| Current on-hand stock | Module D (inventory_by_location) |
| Sales history of past promotions for same article/category | Module T (transaction history) |
| Prior promotion purchase quantities | Module J (historical POs) |
| Current regular cost, retail, and gross margin | Module P (current conditions) |
| Promotional cost, retail, and gross margin at plan retail | Module P (modeled) |

The system must show the current retail, cost, and margin *before* the buyer enters a promotional price — not after saving. Planning against an unknown margin is a known design failure in enterprise retail systems.

### Phase 2: Modeling

Promotion modeling requires what-if capability:

- Set a promotional retail (% off, $ off, or new price) and see projected gross margin, sell-through, and lift over base rate of sale
- Copy a comparable past promotion and mass-apply percentage or absolute changes across characteristics (size, color, store group, category)
- Simulate sell-through: given promotional rate of sale, how many weeks does it take to clear?
- Simulate margin: given cost and new retail, what is GM% and GMROI?

For clearance markdowns specifically: starting from current SOH and current rate of sale, the system should calculate the estimated weeks-to-clearance at each candidate retail price.

### Phase 3: Approval Workflow

All promotions go through a tiered approval process:

1. Buyer proposes promotion (price, dates, affected articles/categories, stores)
2. Department head approves (checks OTB impact, margin floor)
3. VP Merchandising approves if the promotion exceeds a dollar threshold or margin deviation threshold
4. Finance sign-off if it involves advertising allowances or co-op funds from vendors

Approval tolerance by role: each user has a maximum % markdown or dollar impact they can approve without escalation. Exceeding the tolerance triggers the next tier automatically.

Once approved, the promotion is locked — changes require a re-approval.

### Phase 4: Execution

On the promotion start date:
- Price conditions activate at POS (all affected stores/channels)
- Allocation tables for promotional stock are executed: merchandise routed from DC or transferred between stores
- If an Open-to-Ship is required (high-sell-through promotion), the system generates daily or weekly replenishment recommendations based on previous day's actuals vs. plan

### Phase 5: Monitoring

Early warning system tracks throughout the event:
- **High sell-through** — risk of stockout; trigger reorder or inter-store transfer
- **Low sell-through** — excess stock; consider deepening markdown or extending event
- **Actual sales vs. plan** — daily variance; alert if deviation exceeds threshold

When a high-sell-through alert fires, the system should check whether:
1. Stock is available at DC → create stock transport to affected stores
2. Stock is available at other stores → recommend inter-store transfer
3. Vendor can provide additional supply → flag for emergency PO (per buyer discretion)

### Phase 6: Recap

After the event, the system captures:
- Sales in units and currency by store, category, style
- Gross margin realized vs. planned
- Stock levels at event close
- Sell-through % by style/size/color

Recap data feeds the next planning cycle: "we promoted this item at $X two Octobers ago; here is what sold."

---

## Pricing Management

### Price Change Types

| Type | Description | Approval Required |
|---|---|---|
| **Promotional markdown** | Temporary price reduction for a defined event | Standard promotion workflow |
| **Clearance markdown** | Permanent reduction to clear aged inventory | Approval by markdown %threshold |
| **Competitive price match** | Price adjusted based on competitor survey | Buyer + department head |
| **Mass price change** | Applied across a category, size, color, or store group | Approval by impact magnitude |
| **Cost update** | Vendor cost change requires retail retail adjustment | Buyer + finance |

### Price Hierarchy

Price changes are applied at a hierarchy level and cascade down:
1. **Department** — broadest; applies to all items in department
2. **Category / Class** — mid-level
3. **Vendor** — all items from a specific vendor
4. **Style / Article** — individual item
5. **Characteristic** (color, size) — variants within a style

Mass price changes must be executable across *cross-cutting characteristics* — e.g., "mark down all large sizes by 15% across all women's outerwear vendors in the Northeast region." This requires the pricing engine to filter across multiple dimensions simultaneously.

### Linked Items

Related articles across categories must be flagged for coordinated markdown. The standard example: a jacket, blouse, and skirt from the same outfit must be marked down together. When a buyer initiates a markdown on any one of the linked items, the system alerts them to the other linked articles and prompts for a decision.

### Price History and Analysis

The system must retain the full history of price changes per article, including:
- Effective dates for each price tier
- Units sold at each price point
- Margin realized at each price point

This enables the comparison: "what was the sell-through rate on this jacket at $89.99 vs. $79.99?" — the primary analytical question a buyer asks when setting a promotional price.

### Competitor Price Tracking

Specialty retailers run regular competitive price surveys: a shopper visits competitor stores on a defined schedule and records prices for a target basket of items. Those prices are uploaded (handheld or flat file) and stored against the article. The pricing module can then flag items where the chain's price is above the competitor's by more than a configured tolerance.

---

## Promotion and Replenishment Integration

Promotions run on top of the base replenishment plan. The demand lift from a promotion must be treated as promotional demand, not base demand, so that:

1. Post-event forecasts are not inflated by the one-time lift
2. Future replenishment runs do not build excess safety stock based on promoted sales

Two options, configurable per item or category:
- **Include in base demand:** for recurring promotions (same week every year) — the lift is part of the regular selling pattern
- **Smooth out of base demand:** for one-time or irregular promotions — the lift is quarantined from the forecast

If the promotion is still active but not yet converted to a PO or stock transport, the replenishment system must be aware of the planned promotional demand and account for it in current reorder point calculations.

---

## Canary Module P Implications

| Requirement | Canary P Behavior |
|---|---|
| Pre-approval price modeling | P must compute projected margin before saving a promotion |
| Tiered approval workflow | P owns the approval state machine; escalation rules are configurable |
| Mass maintenance across characteristics | P applies changes by filtering the item catalog by size/color/vendor/store-group |
| Linked item alerts | P maintains article linkage table; markdown on one triggers alert on linked items |
| Promotional demand isolation | P tags transactions with promotion ID; J and T use the tag to separate base vs. lift |
| Post-event recap | P aggregates actual vs. plan at event close; feeds historical promotion library |

---

## Related

- **Merchandise planning and OTB:** [[Brain/wiki/retail-merchandise-planning-otb]]
- **PO from plan:** [[Brain/wiki/retail-po-from-plan]]
- **Canary module P:** [[Canary-Retail-Brain/modules/P-pricing-promotion.manifest.yaml]]
- **Source intake:** [[Brain/raw/inbox/sap-apparel-workshop-promotions-pricing-po]]

---
title: Retail Accounting Method — RIM, Cost Method, Open To Buy
date: 2026-04-24
type: platform-substrate
owner: GrowDirect LLC
classification: confidential
tags: [rim, retail-inventory-method, cost-method, otb, open-to-buy, merchandise-planning, accounting]
nav_order: 8

---

# Retail Accounting Method — RIM, Cost Method, Open To Buy

**Governing thesis.** The stock ledger carries both quantity and value. The **value method** — the choice between Retail Inventory Method (RIM) and Cost Method — is a real decision with load-bearing downstream consequences. It affects how on-hand value is calculated, how period close works, how margin is measured, and how merchandise planning budgets are enforced. **Open To Buy (OTB)** is the planning constraint that sits on top of the ledger and the value method: it is the dollar budget in retail inflows that a buyer cannot exceed without re-plan approval. Every SMB retailer defaults to whatever their POS picked (usually neither), which is why margin erosion is the second-largest source of shrink-adjusted loss after cash/card theft. Choosing the right value method and enforcing OTB discipline closes that leak.

---

## Why This Article Exists

The perpetual stock ledger records quantity and value together. This is not incidental; it is required for financial accounting and merchandise planning. But the **value method** — how the value is calculated and carried forward in on-hand inventory — is a choice with real consequences. Retail has inherited two distinct methods from the 1900s, and both are load-bearing today:

1. **RIM (Retail Inventory Method)** — on-hand is carried at retail; cost is derived via the cost complement.
2. **Cost Method** — on-hand is carried at landed unit cost; cost flows directly.

The choice affects:
- How quickly the period close runs
- How accurately shrink is attributed
- How margin is calculated per item
- Whether the buyer can see cost basis per unit (Cost Method) or must estimate it via reverse markup (RIM)
- How markdown timing affects on-hand valuation (critical for RIM)

Most SMB retailers don't make this choice consciously. Their POS came with a default. This article names the choice and the consequences, so Canary customers can pick the method that fits their operation.

---

## RIM (Retail Inventory Method)

### Origin and Adoption

The Retail Inventory Method is the invention of early department stores in the 1900s. Before computerized inventory systems, department stores tracked thousands of items across dozens of locations and needed a way to close the books monthly without taking a physical count. The solution: carry on-hand value at the retail price the customer paid, not the cost price the merchant paid.

RIM remains standard in soft-line retail (apparel, home goods, accessories), general merchandise (drugstores, dollar stores), and any vertical where markdown management is frequent and unit costs vary widely.

### How It Works

Under RIM:

1. **On-hand value is recorded at retail** — the price tag, not the cost basis.
2. **Cost is derived via the cost complement** — calculated at period close for a department or class, using the formula:
   ```
   Cost Complement = Cost / Retail (averaged across all items in the pool)
   Cost of On-Hand = On-Hand Retail Value × Cost Complement
   ```
3. **VAT and other taxes are reflected in the retail value** where applicable (e.g., in EU jurisdictions).

### Example

A department carries soft-line apparel at a 50% gross margin. On-hand at retail is $50,000. The cost complement (cost ÷ retail) is 0.50. Therefore, the on-hand at cost is $50,000 × 0.50 = $25,000.

If the department marks down $5,000 in retail value (e.g., end-of-season clearance), the on-hand at retail drops to $45,000. The cost complement remains 0.50 (assuming the markdown is proportional). The on-hand at cost drops to $22,500.

### Strengths

- **Fast period close.** The cost complement is calculated once per department per period. All on-hand revaluation rolls into one formula.
- **Hides unit cost from store labor.** Sales associates and stockers never see the cost basis of an item; they see only the retail price. This prevents intentional or accidental margin leakage through informal discounting.
- **Markdown management is clean.** Markdowns are recorded at the retail level. The system automatically carries the impact down to cost via the cost complement. The buyer sees margin impact immediately.
- **Works well with frequent assortment changes.** Department stores refresh assortment seasonally or quarterly; RIM doesn't require itemization of cost per SKU.

### Weaknesses

- **Less precise per-unit.** Unit cost is estimated via the cost complement, not tracked. If one item has a 60% margin and another has a 40% margin within the same department, the cost complement (50% average) is inaccurate for both.
- **Sensitive to markdown timing.** If markdowns are taken late in the period, the cost complement for the period is different than if they had been taken early. This can cause reconciliation friction.
- **Requires accurate retail prices.** If retail prices are wrong in the system, the cost complement is wrong, and on-hand value is wrong. RIM is less forgiving of data quality issues than Cost Method.
- **Cannot support consignment or concession pricing.** If a supplier retains ownership and the retailer is only selling on consignment, RIM breaks down because the cost basis is different from the retail price the customer sees.

### When to Use RIM

- Soft-line apparel and accessories
- General merchandise with seasonal assortment
- Dollar stores and off-price retailers
- Any vertical where unit margins vary widely and markdowns are frequent
- Retailers with slow inventory turn who can afford a monthly close cycle

---

## Cost Method

### How It Works

Under Cost Method:

1. **On-hand value is recorded at landed unit cost** — the actual cost the retailer paid for the item, including freight, tariffs, and other inbound costs.
2. **Cost flows to COGS (Cost of Goods Sold) using the selected cost flow assumption:**
   - **FIFO** — First In, First Out. Oldest cost is assumed to flow first.
   - **Weighted-average** — Average cost of all units in inventory.
   - **Standard cost** — Predetermined cost; actual cost flows at period end via variance posting.
3. **VAT and other taxes are part of the landed cost** (or excluded, depending on the jurisdiction).

### Example

A hard-line retailer buys widgets at $10 landed cost and sells them at $25 retail (60% gross margin). On-hand of 1,000 units is valued at $10,000 at cost.

When 100 units sell:
- COGS is charged $1,000 (100 × $10).
- Revenue is $2,500 (100 × $25).
- On-hand at cost drops to $9,000.

When a supplier invoice shows the items cost $11 (due to currency fluctuation or tariff increase), the next purchase is recorded at $11. Previous on-hand remains at $10 per unit (unless standard cost accounting is used, which adjusts all units to the new standard).

### Strengths

- **Precise per-unit.** Cost is tracked at the individual item or batch level. Shrink attribution is exact.
- **Works with consignment and concession.** The retailer can track owned inventory at cost, consignment inventory separately (on-balance-sheet but not owned), and concession inventory off-balance-sheet.
- **Regulatory alignment.** Food and beverage retailing, pharmaceuticals, and other regulated verticals often require Cost Method for compliance and traceability.
- **Margin per item is visible.** The buyer sees retail price and unit cost side by side. Gross margin per item is exact, not estimated.

### Weaknesses

- **More compute at period close.** Every item's cost flow assumption must be calculated. For large inventories, this is expensive.
- **Requires landed-cost detail at receipt.** The system must capture cost including freight and duties. Missing data means cost is inaccurate.
- **Store labor exposure.** If cost is visible in the system (necessary for many use cases), unauthorized discounting risk increases.

### When to Use Cost Method

- Hard-line merchandise with stable margins
- Food and beverage with shrinkage tracking
- Pharmacy and health/beauty
- Consignment and concession programs
- Any vertical with regulatory traceability requirements (food safety, medication tracking)
- Direct-to-consumer brands where per-item cost and margin are business KPIs

---

## Choosing Between Them — Decision Matrix

Use this matrix to pick the method for each department or business unit:

| Vertical | Primary driver | Recommended | Rationale |
|---|---|---|---|
| **Apparel & Accessories** | Seasonal assortment, frequent markdowns, hidden cost | RIM | Markdown velocity and labor protection favor RIM |
| **General Merchandise** | Multi-category, varied margins, frequent turns | RIM | Operational simplicity, fast close |
| **Grocery & Deli** | Shrink tracking, item-level margin, expiration dates | Cost | Regulatory + shrink attribution requires precision |
| **Pharmacy** | Regulatory traceability, expiration dates, theft risk | Cost | Compliance + loss prevention require item-level detail |
| **Specialty Hard-line (Tools, Electronics)** | Item-level margin, stable pricing, low turnover | Cost | Per-unit visibility is a sales tool; turnover is low enough to support Cost Method |
| **Consignment / Concession** | Vendor ownership, variable vendor terms | Cost + Special treatment | Consignment items must be tracked separately |
| **Online / Direct-to-Consumer** | Per-item profitability analysis, transparency | Cost | Transparency to customers (and investors) requires per-unit precision |
| **High-end Soft-line (Luxury, Designer)** | Item-level margin, exclusive assortment, high ASP | Cost | Per-item margin is a competitive tool |

**Default for SMB specialty retail:** RIM for soft-line; Cost Method for hard-line and perishable. Mixed approach is common (RIM for soft, Cost for deli/grocery/wine).

---

## Open To Buy (OTB) — The Planning Constraint

### Definition

Open To Buy is the amount of new merchandise (in retail dollars) a buyer is authorized to commit to purchase over a specified planning period (usually a month or quarter), without exceeding a planned on-hand ceiling.

The formula:

```
OTB = Planned End-of-Period On-Hand + Planned Receipts 
      + Planned Markdowns − Planned Sales
```

Working backward:

```
Planned Receipts = Planned Sales + Planned Markdowns − Planned EOH + Planned BOH
```

In plain English: 

- Start the period with some stock (BOH, Beginning On-Hand)
- Expect to sell some amount (Planned Sales)
- Plan some markdowns (Planned Markdowns)
- Want to end the period with some stock (Planned EOH)
- The receipts you need are what fills that gap
- The receipts you're *allowed* to buy is your OTB budget

### Why OTB Matters

Exceeding OTB silently is the single biggest source of inventory-driven margin erosion in mid-market retail. Here's how it happens:

1. The buyer commits $50,000 of POs against a $100,000 OTB.
2. The buyer identifies a deal (overstock clearance from a vendor, unplanned opportunity buy) and commits another $60,000 without re-plan.
3. The buyer is now $10,000 over OTB.
4. The buyer does not re-plan; instead, they expect sales to catch up or markdowns to bring on-hand down.
5. Sales miss or markdowns are late.
6. End of period: on-hand is $20,000 over plan.
7. The next period is starved of buying budget to bring on-hand back down.
8. The retailer misses sales that next period because it's out of stock on fast-movers.
9. The margin erosion compounds: overstock in period 1 → forced markdowns in periods 2–3 → stockout in period 4 → lost margin on the stockout period.

OTB enforcement prevents this cascade. When the buyer tries to commit a PO that would exceed OTB, the system either rejects it or forces a re-plan conversation with the planner.

### The Trinity of OTB

OTB lives at the intersection of three systems:

1. **The ledger** (truth): What is actually on-hand right now?
2. **The RIM/Cost choice** (valuation): In which currency is OTB expressed? Retail dollars (RIM) or cost dollars (Cost Method)?
3. **The forecast** (planning): What does demand look like for next period?

The OTB calculation requires all three:
- Ledger: current on-hand
- Forecast: expected sales + markdowns for the period
- RIM/Cost: the currency for expressing the budget (retail dollars make sense for RIM departments; cost dollars for Cost Method)

### OTB Implementation

The v2.F (Finance) module owns the value-method choice and period close.

The v2.J (Orders) module owns the forecast and the replenishment recommendation.

The v2.C (Commercial) module owns OTB calculation and the PO commitment gate.

Together, they form the merchandise-planning trinity:

```
Ledger (F) ← Current On-Hand (truth)
    ↓
Commercial (C) ← OTB Calculation
    ↓
    ├─→ Forecast (J) ← Demand Forecast + Replenishment ROP
    ├─→ Finance (F) ← Period Close + GL Posting
    └─→ Distribution (D) ← PO Commitment ← Allowed headroom check
```

If OTB is exceeded, the system should either:
- Reject the PO and require re-plan (strict mode)
- Accept the PO but flag it as over-OTB and route to a planner for approval (soft mode)

Most retailers use soft mode: over-OTB buys are allowed but tracked. At month-end, the planner reviews any over-OTB commitments and either approves them (re-planning the quarter) or directs the buyer to cancel.

### Open Questions

- **Per-merchant default policy.** Does the merchant want strict OTB enforcement (reject over-budget POs) or soft enforcement (flag, require approval)?
- **OTB rollup across departments.** Is OTB a department-level constraint, a class-level constraint, or both? At what level does a buyer have flexibility to move budget between sub-categories?
- **Period-close timing.** OTB is usually monthly, but forecasts may be rolling 13-week. How are the two timelines reconciled?
- **Interdepartment allocation.** Does the buyer have global OTB headroom that they allocate across departments, or does each department have a separate OTB budget?

---

## How Canary Maps Onto This

**v2.F (Finance)** — Owns the value-method decision (RIM or Cost per department). Implements period close with the correct cost-complement or cost-flow calculation. Publishes cost-update events when landed cost changes or markdown events change the retail price.

**v2.J (Orders)** — Reads the ledger's movement history to derive demand forecast. Calculates replenishment points and order quantities. Consumes OTB headroom from v2.C and checks it before recommending POs.

**v2.C (Commercial)** — Maintains the item master, department hierarchy, supplier master. Calculates OTB per department and buyer. Enforces the OTB gate on PO commitment (accepts or rejects POs based on available headroom).

**v2.D (Distribution)** — Publishes receipts (which consume OTB headroom) and tracks receipts against POs.

Together, these four modules implement the accounting substrate that makes RIM, Cost Method, and OTB discipline work for SMB retailers.

---

## Related

- [[stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]]
- [[satoshi-cost-accounting|Satoshi-Level Cost Accounting — Sub-Cent Unit Cost on the Stock Ledger]]
- [[../../GrowDirect/Brain/wiki/third-branch|The Third Branch]]
- [[spine-13-prefix|The Canary Retail Spine — 13 Modules]]
- [[crdm|Canonical Retail Data Model (CRDM)]]

---

*Classification: confidential. Owner: GrowDirect LLC. Created 2026-04-24. This is a platform substrate document. Merchant-facing documentation should present RIM/Cost Method choice as a straightforward decision, with OTB as the enforcement mechanism that closes the margin-erosion loop.*

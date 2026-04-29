---
card-type: field-hierarchy
card-id: category-hierarchy
card-version: 1
domain: merchandising
layer: domain
feeds:
  - role-binding-model
  - module-p
  - module-s
  - module-j
  - module-c
receives:
  - merchant-org-hierarchy
tags: [hierarchy, category, merchandising, division, department, sku, range, otb]
status: approved
last-compiled: 2026-04-28
---

# Category Hierarchy

The category hierarchy is the merchandising axis used by buying, range planning, pricing, and forecast. It organizes product nodes from division down to SKU.

## Purpose

OTB allocation, range decisions, promotional authority, and forecast buckets all operate on category nodes. A buyer owns a Department node. A Category Manager owns a Category node. The same store that appears in the geography hierarchy as a GEO_STORE node also appears here as the measurement point where category performance is tracked at location.

## Structure

```
Division
  └─ Department
       └─ Category
            └─ Sub-category
                 └─ SKU
```

| Node | Code | Scope |
|------|------|-------|
| **Division** | `CAT_DIVISION` | Broadest merchandising grouping — apparel, hardlines, food |
| **Department** | `CAT_DEPT` | Buyer ownership unit — Women's, Electronics, Grocery |
| **Category** | `CAT_CATEGORY` | Range planning and OTB unit |
| **Sub-category** | `CAT_SUBCATEGORY` | Planogram and promotion unit |
| **SKU** | `CAT_SKU` | Individual item — inventory, price, forecast atom |

The GEO_STORE node in the [[geography-hierarchy]] is the anchor where category performance is measured at location. Category hierarchy nodes do not carry geography — that join happens at query time via the store linkage.

## Invariants

- SKU belongs to exactly one Sub-category → Category → Department → Division chain.
- OTB authority lives at `CAT_DEPT` level. Category Managers can allocate within a Department OTB; they cannot exceed it without Head Office sign-off.
- Promotional authority: Category and Sub-category nodes can carry promotions. SKU-level override requires Category Manager approval.
- The CRDM agent owns `cat_nodes` and the hierarchy table. Schema changes require CRDM sign-off and SI cycle for affected modules (P, S, J, C).
- Category hierarchy does not carry location. Performance at location is a join: `(CAT_SKU, GEO_STORE)`. Aggregation rolls up both axes independently.

## Consumers

| Consumer | Uses |
|----------|------|
| **Module P (Pricing & Promotion)** | Promotional rules attach to Category or Sub-category nodes |
| **Module S (Space, Range & Display)** | Range decisions at Category level, planograms at Sub-category |
| **Module J (Forecast & Order)** | Forecast buckets at Category or SKU level by store |
| **Module C (Commercial)** | Commercial strategy operates on Division and Department nodes |
| **Signal: Seasonality** | Demand curves are modeled per Category node |

## Related

- [[geography-hierarchy]] — the other field hierarchy axis; store is the shared anchor
- [[role-binding-model]] — Buyer and Category Manager roles bind to CAT_DEPT and CAT_CATEGORY nodes
- [[merchant-org-hierarchy]] — Merchants layer principals operate on category hierarchy nodes

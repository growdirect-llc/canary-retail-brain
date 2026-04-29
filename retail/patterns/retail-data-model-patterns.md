---
tags: [retail, data-model, schema, wiki]
project: retail
type: wiki
last-compiled: 2026-04-28
needs-review: 2026-05-12
---

# Retail Data Model Patterns

Canonical data model patterns for enterprise retail management systems. These structures are consistent across major platforms regardless of vendor; derived from interface mappings between merchandise and distribution systems.

## Canonical Data Domains

| Domain | Purpose | Key Entities |
|--------|---------|-------------|
| Item | Product master | Item_Master, Item_Loc, Item_Zone_Price |
| Organisation | Location hierarchy | Store, Warehouse, District, Country |
| Merchandise | Product hierarchy | Division, Group, Dept, Class, Subclass |
| Supplier | Vendor relationships | Supplier, Item_Supplier, Freight |
| Purchase Order | Procurement | Orderhead, Ordersku, Orderloc, Alloc_Header |
| Promotions | Marketing events | PromHeader, PromSku, PromEvent, PromStore |
| Inventory | Stock positions | Item_SOH, Item_Loc_Hist, Transfer headers |
| Finance | Pricing and transactions | Item_Zone_Price, FIF_Invoice_Header, Stock Ledger |
| Reference | Rates and codes | Currency_Rates, VAT_Codes, Ticket_Type |

## Item Master Pattern

The item master is the central entity. Key design invariants:

| Attribute | Pattern |
|-----------|---------|
| Item identifier | Supports multiple ID types simultaneously: UPC, PLU, item number, DIN, pack size |
| Unit of measure | Multi-UOM: units, weight, volume — all active simultaneously |
| Location binding | `Item_Loc` maps item to each store/warehouse it's active in |
| Price binding | `Item_Zone_Price` maps item to price zone (not directly to store) |
| Demand signal | `Item_Forecast` stores forward-looking demand; `Item_SOH` stores current stock position |
| History | `Item_Parents_Loc_Hist` (weekly parent-level), `Item_Diff_Loc_Hist` (diff-level), `Item_Loc_Hist` (transfer-level) |
| Ticketing | `Item_Ticket`, `Ticket_Request`, `Ticket_Type` — store-level label management |

### Item Identifier Types

| Type | Use Case |
|------|---------|
| UPC | Consumer packaged goods; scan at POS |
| PLU | Produce, bulk items; price lookup by code |
| Item number | Internal vendor/buyer reference |
| DIN (Drug Identification Number) | Pharmaceutical regulatory identifier |
| Pack size | Receiving unit vs. selling unit variant |

A single retail item may have all of these simultaneously. The item master must support parallel identifier types with clean resolution to a single canonical SKU.

## Organisation Hierarchy

```
Company
  └─ Region / Area
       └─ District
            └─ Store / Warehouse
                  └─ Store_Attributes (format, size, cluster)
                  └─ WH_Store_Assignment (stores served by this WH)
```

| Entity | Key Fields |
|--------|-----------|
| Store | Store number, name, district, currency, promo zone, warehouse assignment |
| Warehouse | WH number, network position, DC type |
| WH_Store_Assignment | Many-to-many: stores served by each warehouse |
| Promo_Zone | Store groupings for promotional pricing |

## Merchandise Hierarchy

```
Division
  └─ Group
       └─ Department
            └─ Class
                 └─ Subclass
```

Each level carries:
- Buyer / merchant assignment
- Forecasting aggregates: dept-level forecast, class-level forecast
- Historical aggregates: dept history, class history

Replenishment and financial planning operate at department level by default; can be driven to class or item level. Open-to-buy is calculated at department level.

## Supplier / Vendor Model

| Entity | Purpose |
|--------|---------|
| Sups (Supplier master) | Vendor name, terms, lead times |
| Item_Supplier | Item-to-supplier mapping with cost and origin |
| Item_Supplier_Country | Country of origin for import tracking and landed cost |
| Freight | Freight terms and rates per supplier |

A single item can have multiple suppliers. `Item_Supplier_Country` supports landed cost calculation and import compliance tracking.

## Purchase Order Model

```
Orderhead (PO header: supplier, terms, DC, ship dates)
  └─ Ordersku (line item: item, quantity, cost)
       └─ Orderloc (distribution: quantity to each location)

Alloc_Header (allocation event)
  └─ Alloc_Detail (item/location quantities)
```

Allocations are separate from purchase orders — a PO brings goods in; an allocation distributes them to stores. They share a lifecycle but have different control points and business owners (buyer vs. allocator).

## Promotions Model

```
PromHeader (event: dates, type, zone)
  └─ PromEvent (specific event details)
  └─ PromStore (store/zone applicability)
  └─ PromSku (item-level specifics: price, quantity thresholds)
```

Promotions are zone-based (`Promo_Zone` → stores), not store-by-store. A single promotion covers thousands of stores without per-store records. This is a key normalization choice that keeps promotions manageable at scale.

## Invoice Model (3-Way Match)

```
FIF_Invoice_Header (supplier invoice)
  └─ FIF_Invoice_Detail (line items)
       ↔ Receipt (actual goods received)
       ↔─ Ordersku (expected cost from PO)
```

3-way matching links: invoice line ↔ receipt quantity ↔ PO cost. Exceptions (cost variance, quantity discrepancy) surface as matching failures for manual resolution. The 3-way match is the AP control point.

## Price Model

| Entity | Purpose |
|--------|---------|
| Item_Zone_Price | Current retail price by item and price zone |
| Currencies_PP_Rules | Price point rounding rules by currency |
| Currency_Rates | Exchange rates for multi-currency operations |

Price zones decouple pricing from org hierarchy. A pharmacy chain may have 5 price zones across 300 stores, allowing regional pricing without per-store price records. Zone membership is in `Store` (via promo_zone FK).

## VAT / Tax Model

| Entity | Purpose |
|--------|---------|
| VAT_Codes | Tax code definitions |
| VAT_Rates | Rate by code (may vary by period or jurisdiction) |
| VAT_Item | Item-to-tax-code mapping |
| VAT_History | Historical rates for audit compliance |
| VAT_Deps | Department-level VAT defaults |
| VAT_Regions | Regional VAT applicability |

VAT model is separate from the price model — allows different tax treatment by item category and region without denormalizing the price table. Required for UK, EU, Canadian (GST/PST), and other VAT jurisdictions.

## Currency Model

| Entity | Purpose |
|--------|---------|
| Currency_Rates | Exchange rates (typically daily) |
| Currencies | Currency code definitions |
| Currencies_PP_Rules | Price point rounding rules per currency |

Multi-currency retail systems carry costs in supplier currency, report in reporting currency, and sell in local currency. The three are reconciled via Currency_Rates at period end.

## Related Cards

- [[retail-integration-patterns]] — how these entities flow across the integration bus
- [[retail-module-decomposition]] — which modules own which entities
- [[retail-vendor-evaluation-criteria]] — how data model coverage is evaluated in selection

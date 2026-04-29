---
tags: [retail, foundation-data, master-data, wiki]
project: retail
type: wiki
last-compiled: 2026-04-28
needs-review: 2026-05-12
---

# Retail Foundation Data

Foundation Data is the master data prerequisite for all transactional retail system operations. Without it, item updates don't propagate, purchase orders can't be created, and the integration bus fails. It is the critical path in every implementation.

## What Foundation Data Is

Foundation Data is the set of master records that transactional messages depend on. In a pub/sub integration bus, transactional message publishers assume Foundation Data has been synchronized to all subscribers before any event messages flow.

| Domain | Entities |
|--------|---------|
| Merchandise hierarchy | Division, Group, Department, Class, Subclass |
| Organizational hierarchy | Company, Region, District, Store, Warehouse, Country |
| Item master | Item_Master, Item_Loc, Item_Zone_Price, Item_Supplier |
| Vendor/supplier master | Sups, Item_Supplier, Item_Supplier_Country, Freight |
| Reference data | Currencies, Currency_Rates, VAT_Codes, VAT_Rates, Freight Terms |
| Buyers & merchants | Buyer, Merchant (linked to merchandise hierarchy) |
| Location attributes | Store_Attributes, WH_Store_Assignment, Promo_Zone |

## Why It's the Critical Path

Every other data domain has a dependency on Foundation Data:

```
Foundation Data
  ↓
Purchase Orders (need: items, locations, suppliers, hierarchy)
  ↓
Replenishment (need: item/loc, forecast, stock levels)
  ↓
Sales Audit (need: item/loc, price zones)
  ↓
Invoice Matching (need: POs, receipts, supplier)
  ↓
Planning (need: 6–12 months of clean transactional history)
```

A Foundation Data error discovered in Phase 3 can require retroactive re-processing of all downstream transactions. Catching errors in Phase 1 is dramatically cheaper.

## Integration Bus Dependency

In a message bus architecture:

- **Transactional messages** (PO creation, inventory adjustments, receipts) assume Foundation Data is pre-loaded at all subscribers
- If Foundation Data is missing or inconsistent, messages that reference unknown item or location codes fail at the subscriber
- Failed messages accumulate in the Error Hospital subsystem
- Non-dependent messages continue, but the backlog can grow faster than it can be cleared

**Rule**: Foundation Data sync must complete and be validated at all subscribers before transactional message flow begins.

## Foundation Data Quality Issues

Common problems surfaced during the extraction-cleanse-load process:

| Issue | Impact |
|-------|--------|
| Duplicate items (same product, multiple codes) | Inventory split across duplicate records; incorrect stock positions |
| Inconsistent merchandise hierarchy assignments | Planning and reporting roll-ups are wrong |
| Missing item/location relationships | Replenishment can't see that an item is active at a store |
| Stale supplier costs | POs created with wrong costs; invoice matching fails |
| Inconsistent UOM definitions | Receiving quantities don't match ordering quantities |
| Legacy code ≠ new system code | Integration bus messages fail; cross-reference layer required |

## Foundation Data Load Sequence

Order matters. Referential integrity constraints require this sequence:

1. Org hierarchy (Company → Region → District → Store/Warehouse)
2. Merchandise hierarchy (Division → Group → Dept → Class → Subclass)
3. Supplier/vendor master
4. Item master (depends on merch hierarchy)
5. Item/location relationships (depends on item master + org hierarchy)
6. Item/supplier relationships (depends on item master + supplier)
7. Price data (depends on item/location + price zones)
8. Reference data (currencies, VAT, freight terms — can load anytime)

## Foundation Data Governance After Go-Live

Foundation Data is not a one-time load — it must be continuously governed:

| Event | Foundation Data Impact |
|-------|----------------------|
| New item introduction | Item_Master + Item_Loc + Item_Zone_Price + Item_Supplier |
| New store opening | Store + Store_Attributes + WH_Store_Assignment + Item_Loc for all active items |
| Supplier change | Sups + Item_Supplier (new cost, new origin) |
| Merchandise hierarchy restructure | Reclassification across items; planning history may need restatement |
| Price zone restructure | Zone reassignments; Item_Zone_Price reload |

Hierarchy restructures mid-season are the highest-risk Foundation Data events — they can invalidate months of planning history.

## Related Cards

- [[retail-integration-patterns]] — Foundation Data as a prerequisite to message bus operation
- [[retail-data-model-patterns]] — canonical table structures for Foundation Data entities
- [[retail-implementation-methodology]] — Phase 1 is dedicated to Foundation Data
- [[retail-module-decomposition]] — Foundation Data module within merchandise operations management

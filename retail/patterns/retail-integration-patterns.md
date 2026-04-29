---
tags: [retail, integration, messaging, architecture, wiki]
project: retail
type: wiki
last-compiled: 2026-04-28
needs-review: 2026-05-12
---

# Retail Integration Patterns

Enterprise retail management systems integrate dozens of subsystems across merchandise, distribution, store operations, finance, and external partners. This card documents the canonical integration architecture, message patterns, and interface catalog.

## Integration Tiers

| Tier | Pattern | Use Case |
|------|---------|---------|
| Real-time / near-real-time | Message bus (pub/sub, JMS) | Item updates, PO events, inventory adjustments, store receipts |
| Scheduled batch | ETL (parallel multi-threaded) | Sales audit, replenishment quantities, bulk data loads |
| Point-to-point | Legacy harnesses, flat file adapters | Older POS systems, financial packages, WMS |

## Message Bus Architecture

The canonical retail integration bus uses a JMS-based publish/subscribe model:

```
Publisher → [JMS Queue] → Subscriber(s)
                ↑
          Error Hospital
          (dead-letter + retry)
```

### Key Properties

| Property | Description |
|----------|-------------|
| Single message schema | All publishers and subscribers share a common schema — no pairwise contracts |
| Foundation Data prerequisite | Transactional messages assume master data (items, locations, hierarchies) has been synced to all subscribers before event messages flow |
| Error Hospital | Messages that fail subscriber processing are isolated; non-dependent messages continue; failed messages can be retried without blocking |
| XML message format | Hierarchical XML; subscribers consume only needed elements |
| Registry-based configuration | EAI environment controlled by a Registry with replicating Secondary Registries; automatic failover on primary failure |

## Message Family Catalog

30+ message families in a standard retail integration bus:

| Domain | Message Families |
|--------|-----------------|
| Merchandising | Items, Locations, Hierarchies, Purchase Orders, Vendors, Allocations, Transfers, User Defined Attributes |
| Distribution Management | ASN, Appointments, Return to Vendor, Space Locations, Receipts (Bill of Lading), Stock Order Status, Order Release, Inventory Adjustments, Inventory Balances |
| Customer Order Management | Order Reserve, Sale, Return |
| Financial / Reference | Chart of Accounts, Freight Terms, Currency Rates, Vendors, Payment Terms |

## RMS → Distribution Management Interface Channels

The 9 canonical data channels between the merchandise system and distribution management:

| Channel | Key Tables | Data |
|---------|-----------|------|
| Item | Item_Zone_Price, Item_Master, Item_Loc, Item_Forecast, Item_SOH, Item_Loc_Hist, Item_Ticket, TSF_Head | Price, Item Master, Demand, Stock Level, Sales History, Tickets, WH Transfers |
| Purchase Order | Orderhead, Ordersku, Orderloc, Alloc_Header, Alloc_Detail | Orders, Allocations |
| Merchandise | Division, Groups, Deps, Class, Subclass, Buyer, Dept Forecast, Class History | Merchandise hierarchy, forecasts |
| Organisation | Store, Districts, Warehouse, Country, Promo_Zone, Store_Attributes, WH_Store_Assignment | Org hierarchy |
| Promotions | PromHeader, PromSku, PromEvent, PromStore | Promotion events |
| Supplier | Sups, Item_Supplier, Item_Supplier_Country, Freight | Supplier data |
| Invoice | FIF_Invoice_Header, FIF_Invoice_Detail | Invoice data |
| VAT | VAT_Codes, VAT_Rates, VAT_Item, VAT_History, VAT_Deps, VAT_Regions | Tax data |
| Currency | Currency_Rates, Currencies, Currencies_PP_Rules | FX + price point rules |

## ETL Layer

The parallel ETL engine handles bulk data movement:

| Operator | Function |
|----------|----------|
| Oraread | Extract data from Oracle database |
| Orawrite | Load transformed dataset into Oracle |

ETL code is written in XML. Fully utilizes all available processors — scales by adding CPUs.

**Primary ETL use cases:**
- Batch sales audit → stock ledger posting
- Pre-aggregating data for reporting workbenches
- Calculating replenishment quantities
- Bulk data loads during initial implementation

## External Integration Approaches

| Approach | Description | Tradeoffs |
|----------|-------------|-----------|
| Native EAI bridge | JMS bridge between retail message bus and a separate EAI platform (IBM MQ, webMethods, BEA) | Requires format/semantic translation; clear support boundary |
| Vendor-native adapters | Pre-built adapters for Oracle Financials, IBM WebSphere MQ | Faster to implement; requires additional licenses |
| Legacy harnesses | RIB XML → flat file format converters | Lowest friction for legacy POS and WMS; enables phased migration |
| Cross-reference/translation layers | ID translation between legacy and merchandise system codes | Required when systems use different item/location codes |
| Financial system integration | Custom integration to SAP, PeopleSoft, Oracle Financials, Lawson | Needed beyond standard two-connection-point option |
| EAI replacement | Full swap of the integration bus for an alternate platform | High cost; breaks upgrade path; not recommended |

## Foundation Data Pattern

All integration depends on Foundation Data being synchronized first:

```
Phase 1: Foundation Data sync
         (items, locations, hierarchies, suppliers, org)
         ↓
Phase 2: Transactional message flow
         (POs, receipts, inventory events, sales)
```

If Foundation Data is out of sync, transactional messages fail at subscribers. The Error Hospital fills up. This is the most common root cause of integration failures during go-live.

Foundation Data entities: items, locations, merchandise hierarchy, organizational hierarchy, suppliers, currency rates, VAT codes.

## Integration Anti-Patterns

| Anti-Pattern | Problem |
|--------------|---------|
| Point-to-point integrations between all apps | O(n²) complexity; any change requires modifying every connection |
| Skipping Foundation Data phase | Transactional messages fail; Error Hospital fills up |
| EAI replacement during implementation | High cost, upgrade path broken, split support responsibility |
| Non-standard message payloads | Cannot upgrade cleanly; custom payloads require renegotiation at each release |
| Co-locating integration bus with OLTP DB | JMS broker competes for memory and I/O; both degrade |

## Related Cards

- [[retail-data-model-patterns]] — canonical table structures in each channel
- [[retail-architecture-patterns]] — server topology for integration bus deployment
- [[retail-module-decomposition]] — which modules publish and subscribe to which families

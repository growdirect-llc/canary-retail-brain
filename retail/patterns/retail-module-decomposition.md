---
tags: [retail, modules, functional-decomposition, wiki]
project: retail
type: wiki
last-compiled: 2026-04-28
needs-review: 2026-05-12
---

# Retail Platform Module Decomposition

L3/L4 functional decomposition of a complete enterprise retail management platform. Six solution areas cover the full retail cycle from merchandise planning through store operations and financial settlement.

## Module Map

### 1. Merchandise Operations Management (Core)

The original core merchandising layer. Highest installed-base penetration; most mature module group.

| Module | L4 Capabilities |
|--------|----------------|
| Foundation Data | Organizational hierarchy, merchandise hierarchy, vendor management, buyers & merchandisers, partners & locations |
| Item Maintenance | Item setup, item reclassification, color/size dimensions, UPC/PLU/DIN support, multi-UOM |
| Purchasing | Purchase orders, contracts, deals management, allocations, scaling, minimum order requirements |
| Replenishment | Due order processing, scaling, seasons & phases, DC-to-store and vendor-to-store replenishment |
| Price Management | Retail and cost pricing, promotion management, clearance, competitive pricing, markdowns |
| Inventory Management | Receiving, return to vendor (RTV), ticketing & labeling, inventory adjustments, stock counts, BOL, layaway, transfers |
| Finance | Stock ledger, budgets, open to buy, invoicing, VAT maintenance, sales tax |
| Systems Administration | Supplier maintenance, timelines, seasons/phases, audit trail, landed costs, calendar, system variables, security |
| User & Grouping Tools | Item lists, location lists, attributes, UDAs, traits, masks, document maintenance |

### 2. Merchandise Optimization & Planning

Built on a dimensional array planning engine. CPU-intensive; runs against the shared demand signal.

| Module | L4 Capabilities |
|--------|----------------|
| Merchandise & Channel Planning | Top-down financial planning, channel-level plans |
| Assortment Planning | Product selection by store cluster, adjacency planning |
| Assortment to Space Optimization | Macro-level category selection, optimal space allocation |
| Item Planning | SKU-level open-to-buy, sell-through management |
| Markdown Optimization | Algorithmically timed markdowns to clear seasonal inventory |
| Visual Space Planning | Graphic planogram generation, space ROI |
| Collaborative Design & Source | Joint vendor planning |
| Promotional Planning | Promotion event planning, uplift modeling |

### 3. Inventory Optimization & Planning

| Module | L4 Capabilities |
|--------|----------------|
| Demand Forecasting | SKU/store-level statistical forecasting; causal models; promotion uplift |
| Replenishment Planning | Automatic order quantity calculation; multi-echelon |
| Allocation Planning | Inventory distribution to stores by need and store personality |
| Inventory Optimization | Service-level-driven safety stock |
| CPFR | Collaborative planning, forecasting, and replenishment with suppliers |
| VMI | Vendor-managed inventory; supplier self-replenishment |

### 4. Supply Chain Execution

| Module | L4 Capabilities |
|--------|----------------|
| Distribution Management | Warehouse operations, network distribution, ASN, appointment scheduling, receiving (BOL), stock order status, RTV, space locations, inventory adjustments, inventory balances |
| Trade Management | International procurement process, partner collaboration, estimated vs. landed cost compliance |

### 5. Integrated Store Operations

| Module | L4 Capabilities |
|--------|----------------|
| Point of Sale | Store transaction processing |
| Store Back Office | End-of-day settlement, store inventory, direct store delivery |
| Store Inventory Management | Wireless/browser access to replenishment data, store receiving, inventory adjustments, in-aisle applications |
| Order Management | Customer order reserve, fulfillment, returns |
| Time & Attendance | Labor scheduling, DC labor scheduling |

### 6. Enterprise Infrastructure

| Module | L4 Capabilities |
|--------|----------------|
| Sales Audit | POS data validation, automated totaling, automated audit, interactive audit, audit trail, import/export |
| Invoice Matching | 3-way match: receipts × invoices × expected costs |
| Active Retail Intelligence | Workflow, exception management, rule-driven monitoring, business process modification |
| Data Warehouse | Retail-specific data model, category mgmt workbench, marketing workbench, merchandising workbench, store ops workbench |
| Integration Bus | Pub/sub message bus, 30+ message families, error hospital |
| Price Management | Rules-based pricing, price change expert subsystem, markdown management |

## Module Maturity Reference

| Module Group | Maturity | Notes |
|-------------|---------|-------|
| Merchandise Operations | High | 10+ years production use at Tier 1 retailers |
| Sales Audit | High | Co-deployed with merchandise ops |
| Invoice Matching | High | Broadly adopted |
| Demand Forecasting | Medium–High | Production at drug/grocery |
| Replenishment Planning | Medium–High | Proven at volume |
| Distribution Management | Medium | Broad use; complex configurations |
| Markdown / Price Optimization | Medium | Fewer live customers; newer capability |
| Store Operations | Low–Medium | Latest additions; requires more configuration |
| Assortment / Space Optimization | Low–Medium | Requires modeling expertise |

*Maturity assessment is independent of any vendor — applies to the industry function category.*

## Implementation Sequencing Convention

| Phase | Modules | Rationale |
|-------|---------|-----------|
| Phase 1 | Foundation Data + Item Maintenance | Everything else depends on this |
| Phase 2 | Core Purchasing + Replenishment | Primary value driver for most retailers |
| Phase 3 | Sales Audit + Stock Ledger | Closes the inventory loop |
| Phase 4 | Invoice Matching + Finance | AP/GL integration |
| Phase 5 | Planning + Optimization | Requires 6–12 months of clean historical data |
| Phase 6+ | Store Operations + Advanced Analytics | Most complex; depends on stable core |

## Module-to-Integration-Bus Relationship

| Module | Integration Role |
|--------|----------------|
| Merchandise Operations (RMS) | Master publisher: items, locations, hierarchies, POs, vendors, allocations, transfers |
| Distribution Management | Publisher: ASN, appointments, receipts, inventory adjustments, inventory balances |
| Store Inventory Management | Publisher: store receipts, inventory adjustments |
| Customer Order Management | Publisher: order reserve, sale, return |
| Sales Audit | Consumer: validated sales data flows to stock ledger |
| Demand Forecasting | Consumer: item and location data; producer: forecast data |

## Related Cards

- [[retail-integration-patterns]] — message families and integration architecture
- [[retail-data-model-patterns]] — canonical table structures per module
- [[retail-vendor-evaluation-criteria]] — how module coverage is assessed in selection processes
- [[retail-implementation-methodology]] — phased sequencing in practice

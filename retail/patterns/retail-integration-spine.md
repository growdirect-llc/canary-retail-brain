---
date: 2026-04-23
type: wiki
tags: [retail-spine, retail-integration, canonical, oracle-retail, interface-catalog, crosswalk]
sources:
  - Brain/raw/inbox/Interface Design Documents/
  - Brain/projects/RetailSpine.md
  - Brain/raw/inbox/retail-business-intelligence-solution-v7.md
last-compiled: 2026-04-23
needs-review: 2026-05-23
status: v0.2
---

# Retail Integration Spine — Canonical Interface Catalog

## Summary

A canonical, vendor-agnostic catalog of the integration interfaces that
move data between the systems of an enterprise retailer. Five active
interface domains (Commercial, Distribution, Finance, Forecasting &
Ordering, Space-Range-Display) and ~76 named interfaces, each mapped to
the RBIS Business Solution Templates ([[Brain/projects/RetailSpine|RetailSpine MOC]])
they ultimately feed.

This article is the **integration-surface counterpart** to the
capability-surface decomposition in the RetailSpine MOC. Together they
answer: *what does an enterprise retailer actually need to compute,
and what data has to move between systems for the answer to be possible?*

## What this is — and what it isn't

**This is** an articulation of the canonical retail integration patterns
that emerged from a generation of Oracle-Retail-era enterprise
implementations. The interface IDs and shapes (C001 product details
flowing from a Merchandising System to an Operational Data Hub, F004
supplier invoices flowing from an Invoice-Matching System to an Invoice
Reconciliation engine, J004 sales facts flowing from a Till Data Store
to a Reporting Data Domain, etc.) are stable patterns — they recur
across retailers because the underlying business shapes recur.

**This isn't** a specific retailer's integration architecture. The
source corpus that seeded this catalog was assembled at one Tier-1
grocer's Oracle Retail rollout, but the systems referenced are
commercially available products (Oracle Retail Merchandising System,
Oracle Retail Warehouse Management System, Oracle Retail Predictive
Application Server, Oracle Retail Invoice Matching) and the interface
shapes are vendor-published patterns. We catalog the patterns, not the
deployment.

**This isn't** Canary's integration architecture either. Canary maps a
Square-merchant SMB onto this canonical surface; the mapping work is
deferred to v0.6. Here we describe what *enterprise retail integration
actually looks like*, agnostic to who is consuming the catalog.

## System glossary

The systems referenced by these interfaces, with their canonical role
and vendor-product origin where applicable.

| Acronym | Canonical role | Vendor-product origin |
|---|---|---|
| **RMS** / **ORMS** | Merchandising System — master of products, hierarchies, suppliers, prices, promotions, purchase orders | Oracle Retail Merchandising System |
| **IDS** | Operational Data Hub — landing zone + integration data store between transaction systems and downstream consumers | Oracle Retail integration tier |
| **IKB** | Item Knowledge Base — product master / item information management hub | (canonical role; vendor-neutral) |
| **IL** | Item Library — item master upstream | (canonical role) |
| **TIMS** | Invoice Matching System — three-way match of PO + receipt + invoice | (third-party AP matching) |
| **ReIM** | Invoice Reconciliation Engine — invoice exception handling and reconciliation | Oracle Retail Invoice Matching (Re-Invoice Match) |
| **OFi** | Financials — general ledger, supplier master | Oracle Financials |
| **GFO** | Demand Forecasting + Allocation + Ordering — the planning nervous system | (canonical role; "Group Forecasting & Ordering" in source) |
| **UDD** | Reporting Data Domain — subject-area data marts for analytics | (canonical role) |
| **SAE** | Sales Aggregation Engine — POS sales fact aggregation | (canonical role) |
| **TDS** | Till Data Store — raw POS event store | (canonical role) |
| **RPAS** | Predictive Application Server — forecasting + planning analytics | Oracle Retail Predictive Application Server |
| **CRDB** | Catalog / Range Database — assortment master | (canonical role) |
| **GPM** | Planogram Management — space planning + shelf layout | (canonical role; "Generic Planogram Management" in source) |
| **SR** | Store Range — per-store assortment execution | (canonical role) |
| **RWMS** / **ORWMS** | Warehouse Management System — DC operations | Oracle Retail Warehouse Management System |
| **Storeline** | Store System — POS + back-office at the store | (third-party in-store stack) |

For the SMB collapse (Canary's substrate) most of these systems compress
into one or two operational schemas; that mapping is RetailSpine v0.6.

## The five active interface domains

The source corpus is organized by single-letter prefix. P (People) and
R (Retail/Store) are present in the taxonomy but empty in the source —
documented below as canonical placeholders.

### C — Commercial

**Purpose.** Master-data flow from the Merchandising System into the
operational data hub and downstream consumers. Establishes the product,
supplier, hierarchy, price, and promotion foundation everything else
depends on.

**Dominant flow direction.** RMS → IDS (master data publication).

| Interface | Direction | Payload | Feeds RBIS BSTs |
|---|---|---|---|
| C001 | RMS → IDS | Product details (master record) | Products & Services Mgmt: all BSTs (foundational) · Merchandising: all BSTs (foundational) |
| C002 | RMS → IDS | Item Section / Department | Hierarchy backbone — every BST that rolls up by department |
| C003 | RMS → IDS | Item Sub-Department | Same as C002 at one level down |
| C008 | RMS → IDS | Supplier reference data | Products & Services: Business Performance (Vendor Performance, Compliance, Fulfillment, Rebate, In-Stock) |
| C010 | RMS → IDS | Price details | Merchandising: Pricing Analysis (Set vs Actual Price, Family Pricing, Multi-Channel Price, Markdown Trend, Price Elasticity, Price Competitive Exception) · Multi-Channel: Catalog price comparisons |
| C010 (TR variant) | RMS → GFO | Promotions | Merchandising: Promotion Analysis (all 9 reports) · Customer: Campaign & Promotion Analysis (all 5 reports) |
| C012 | RMS → IDS | Store attributes + hierarchy | Store Ops: Store Location Analysis (Performance by Format, Geo-Demographic, Segmentation) · all BSTs that dimension by store |
| C013 | RMS → IDS | Warehouse attributes + hierarchy | Store Ops: Location Profitability · Distribution interfaces depend on this |
| C023 / C027 / C045 / C054 | (master) | PLU requirements | Universal product identifier — foundational |
| C024 / C025 | RMS → Storeline | Department / Sub-Department for store system | POS configuration foundation |

### D — Distribution

**Purpose.** Movement events between store, warehouse, and HQ. Every
unit of stock that arrives, leaves, is counted, is adjusted, or is
returned generates a D-prefix message.

**Dominant flow direction.** Bidirectional — Storeline ↔ RMS, Storeline ↔ GFO,
RWMS → TIMS, IL → RMS/GFO.

| Interface | Direction | Payload | Feeds RBIS BSTs |
|---|---|---|---|
| D016 | RMS → Storeline | PO Download for Direct-to-Store deliveries | Merchandising: Inventory (On Order) · Store Ops: receiving |
| D019 / D020 / D033 | Storeline → RMS / GFO | Inventory Adjustment (write-down, write-up, found, lost) | **Store Ops: Loss Prevention (Inventory Discrepancy)** · Merchandising: Inventory (Damages, Stressed, Aged) |
| D021 / D022 / D029 | Storeline → RMS / GFO | Stock Take Result (cycle count + full count outcomes) | **Store Ops: Loss Prevention (Inventory Discrepancy — baseline)** · Merchandising: Inventory (Slow Moving, Safety Stock) |
| D028 | RWMS → TIMS | GRN (Goods Received Note) — what actually arrived at the DC | Finance: PO match (three-way) · Merchandising: Inventory (On Hand reconciliation) |
| D029 | RMS → TIMS | Inventory Report | Finance: Inventory valuation · Merchandising: Inventory (COGS on Hand by Location) |
| D030 / D032 / D035 | Storeline → RMS / GFO | Dispatch RTV (Return to Vendor) | Products & Services: Vendor Performance (Compliance, Quality) · Merchandising: Inventory (Damages) |
| D031 / D034 | IL → RMS / GFO | Direct PO Receipt | Merchandising: Inventory (On Hand) · Finance: PO match |
| D036 / D037 / D038 | Storeline → RMS / GFO | Stock Transfer Receipts (DC↔store, store↔store) | Merchandising: Inventory (Transfer Report and Management) |

### F — Finance

**Purpose.** The procure-to-pay backbone — purchase orders, supplier
masters, invoices, and three-way matching.

**Dominant flow direction.** RMS ↔ TIMS ↔ ReIM ↔ OFi.

| Interface | Direction | Payload | Feeds RBIS BSTs |
|---|---|---|---|
| F001 | RMS → TIMS | Purchase Order (header + lines + cost) | Corporate Finance: Financial Mgmt Accounting · Products & Services: Vendor Performance (timeliness baseline) · Merchandising: Inventory (On Order) |
| F004 | TIMS → ReIM | Supplier Invoice | Corporate Finance: Financial Mgmt Accounting · Products & Services: Vendor Performance (Vendor Compliance — billing) |
| F012 | OFi → RMS | Supplier Information (master) | Products & Services: Vendor master — backs every Vendor BST report |
| F013 | TIMS → RMS | PO Acknowledgement | Products & Services: Vendor Performance (Vendor Compliance — delivery confirmation) |
| F014 | ReIM → TIMS | Reconciled invoice | Corporate Finance: Financial Mgmt Accounting (close-the-loop on three-way match) |

### J — Forecasting + Ordering (GFO domain)

**Purpose.** The planning + analytics + replenishment nervous system.
Aggregates sales facts, computes forecasts, generates allocations,
issues replenishment orders, and feeds the reporting data domain. The
single largest interface family — and the one that most directly drives
operational decision-making.

**Dominant flow directions.** GFO → RMS (orders, allocations) · IDS / IL → GFO
(masters) · TDS → GFO (actual sales) · GFO → UDD (analytics feed) · ORWMS → GFO
(DC telemetry).

| Interface | Direction | Payload | Feeds RBIS BSTs |
|---|---|---|---|
| J001 | RMS → GFO | Allocations | Merchandising: Assortment & Allocation (Traited vs Value, Base Profit Contribution, Product Sales by Store Format) · Store Ops: Store Optimization |
| J002 | IDS → UDD | Location Hierarchy | Foundational location dim — every BST |
| J003 | GFO → UDD | Supplier Authority Data | Vendor master in the reporting domain |
| J004 | TDS → UDD | **Sales from Till** | **The single most important fact feed.** Customer: Purchase Profiles, RFQ, Market Basket, Customer Movement Dynamic (all reports) · Products & Services: Sales by Products (all variants), Cannibalization, New Item Launch · Merchandising: Promo Performance, Markdown Trend · Store Ops: Transaction Profitability, Sales Person Productivity · Multi-Channel: cross-channel sales |
| J006 | IDS → UDD | Commercial Hierarchy | Foundational product/department dim |
| J009 | GFO → UDD | Authorised Range + Shelf Capacities | Merchandising: Assortment & Allocation · Physical Merchandising / Space Mgmt (Capacity, Linear Footage Optimization) |
| J010 | GFO → UDD | Current SOH (Stock On Hand) | Merchandising: Inventory (On Hand, COGS on Hand) · Store Ops: Loss Prevention (discrepancy baseline) · Store Optimization |
| J015 | GFO → ORMS | Sales Forecast Data | Merchandising: Inventory (Days of Supply needs forecast) · Store Ops: Store Optimization (Projected Inventory vs Sales Projections) |
| J017 | GFO → RMS | PBS Stock Order (auto-replen) | Merchandising: Inventory (replenishment) |
| J019 | GFO → RMS | Direct Store Order | Merchandising: Inventory · Store Ops: receiving |
| J020 | GFO → RMS | PBL Procurement Order | Merchandising: Inventory · Finance: PO origination |
| J023 | TIMS → RMS | PO ASN IN (Advance Ship Notice) | Merchandising: Inventory (On Order accuracy) · Finance: PO match prep |
| J024 | GFO → RMS | PBL Final Order | Same as J020 at the commit step |
| J032 / J0110 / J0111 / J0112 | RMS → GFO | RMS document numbers placement | Plumbing — referential integrity across the planning loop |
| J035 | TDS → GFO | Actual Sales (forecast feedback) | Forecast accuracy loop · Customer: actual-vs-forecast at segment |
| J052 / J054 / J057 / J087 / J088 | IL → GFO | Base Product / Item Traded Unit / Product Hierarchy / Store Info / Stock Centres | Master-data foundations of the planning model |
| J076 | IDS → GFO | Supply Authority | Supplier master in planning |
| J097 | ORWMS → GFO | BOL (Bill of Lading) — Picking Details | Distribution telemetry · Products & Services: Vendor Fulfillment |
| J097.5 | ORWMS → GFO | BOL Load + Left-Off | Same — exception leg |
| J100 | IDS → GFO | Item-Warehouse-Supplier Data | Inventory-by-source dim · Vendor performance |
| J113 | (?) → IDS | Allocation Details | Allocation analytics in the reporting domain |
| J114 | (?) → GFO | Promotions Interface | Merchandising: Promotion Analysis (forecast inputs) · Customer: Campaign & Promotion |
| J115 | (?) → IDS | Transfer Details | Merchandising: Inventory (Transfer Report) |

### S — Space, Range & Display (SRD)

**Purpose.** The shelf-level view of the store — what products are
ranged where, in what quantity, on what planogram, with what observed
sales velocity. Drives assortment planning, space optimization, and
range execution.

**Dominant flow directions.** IDS / IKB → CRDB / GPM / SR · SAE → RPAS / IKB · GFO → SR · SR / GPM ↔ Store Range execution.

| Interface | Direction | Payload | Feeds RBIS BSTs |
|---|---|---|---|
| S003 / S082 | SAE → RPAS | Historical Sales, Margin, Waste | Merchandising: Pricing (Markdown Trend, Price Elasticity), Promo Analysis · Products & Services: Product Profitability · forecasting backbone |
| S004 | ORMS → Sales Engine | Sales Information Update | Sales aggregation pipeline foundation |
| S008 | IDS → CRDB | Store Detail Update | Catalog/Range master — store-side of the range matrix |
| S009 | IDS → CRDB | Base Products (approved) | Catalog/Range master — product-side |
| S032 | SAE → IKB | Sales Aggregation Data | Item-level sales facts · Merchandising: Product Sales by Store Format · Customer: Sales Quantity by Products vs Customers |
| S033 | IDS → IKB | Department | Hierarchy maintenance |
| S035 | IDS → IKB | Store's Update | Store master |
| S036 | IDS → IKB | Base Product Update | Product master |
| S047 | SR → GFO | Store range, capacity | Merchandising: Assortment & Allocation · Physical Merchandising / Space Mgmt |
| S057 | IKB → SR | Store Range Data | Range execution |
| S058 | IDS → GPM | Product Information | Planogram inputs |
| S059 | (master) | Valid Mod (Modular) Number Range | Planogram identifier integrity |
| S074 | IDS → GPM | Store Details | Planogram inputs (per-store) |
| S075 | GPM → SR | Capacity Information | Physical Merchandising / Space Mgmt: Optimization of Linear Footage, Section Elasticity |
| S077 | GFO → SR | Actual Range in Store | Range execution feedback loop |
| S078 | IKB → GPM and SR | Product Map | Master-data fan-out |

### P — People (canonical placeholder, source folder empty)

**Purpose if populated.** Workforce master and movement — employee
hierarchy, role/skill master, schedule, time and attendance, training
completion, payroll connectors. Would feed Store Ops: Staffing BST
(all 7 reports — Schedule Compliance, Cashier Performance, Cross
Training, Productivity, Skills vs Employees, Years of Service,
Employee Details).

### R — Retail / Store (canonical placeholder, source folder empty)

**Purpose if populated.** Store-system events that aren't covered by
the C/D/J/S families — typically opening/closing, cash drawer
operations, customer-facing terminal status, in-store device telemetry,
and store-event audit trail. Would feed Store Ops: Loss Prevention
(Cashier Exceptions, Receiver Exception, Schedule Compliance with
Loss), Store Location Analysis, Service Delivery.

## Reverse crosswalk — RBIS BSTs → feeding interfaces

Reading the same map the other way. For each RBIS BST in the
[[Brain/projects/RetailSpine|RetailSpine MOC]], which canonical
interfaces feed it.

### Customer Management

| BST | Feeding interfaces |
|---|---|
| Purchase Profiles · Customer Profiles · Product Purchasing RFQ · Cross Purchase Behavior · Target Product Analysis · Customer Movement Dynamic · Market Basket Analysis | **J004** (sales from till) primary · **J035** (forecast feedback) secondary · C001/C010 (product + price master) · C012 (store dim) |
| Campaign & Promotion Analysis | **C010-TR** (promotions) · **J114** (promotions to GFO) · J004 (campaign-attributed sales) |
| Customer Attrition · Loyalty · Lifetime Value · Profitability · Profile · Movement Dynamics | (canonical interfaces; source corpus thin in customer-master domain) |

### Products & Services Management

| BST | Feeding interfaces |
|---|---|
| Business Performance Analysis | **J004** (sales) · **C001** (product master) · **C008** + **F012** (vendor master) · D028/D031/D034 (receipt) · D030/D032/D035 (RTV) · F004/F013 (invoice + ack — vendor compliance) · J097/J097.5 (vendor fulfillment) |
| Product Analysis | C001/C002/C003 (product + hierarchy) · J004 (sales) · S032 (sales aggregation) · S036 (product master to IKB) |
| Product Profitability | C001/C010 (cost + price) · J004 (sales) · S003/S082 (margin + waste) |
| Planning and Forecasting | J015 (forecast) · J035 (actual vs forecast) · S003/S082 (history) |

### Merchandising Management

| BST | Feeding interfaces |
|---|---|
| Inventory Analysis | **J010** (SOH) · **D019/D020/D033** (adjustments) · D021/D022/D029 (stock take) · D028/D031/D034 (receipts) · D036/D037/D038 (transfers) · J023 (ASN — On Order) · F001 (PO — On Order) |
| Assortment / Allocation | **J001** (allocations) · **J009** (range + capacity) · S047 (store range/capacity) · S057 (range data) · S077 (actual range) |
| Promotion Analysis | **C010-TR** (promotions master) · **J114** (promotions to GFO) · J004 (sales attribution) · S003/S082 (margin) |
| Physical Merchandising / Space Mgmt | **S058** (planogram product info) · **S074** (planogram store info) · **S075** (capacity) · S078 (product map) · J009 (shelf capacity) · S059 (mod number) |
| Pricing Analysis | **C010** (price details) · J004 (price-realization on sales) · S003/S082 (margin trend) |

### Store Operations Management

| BST | Feeding interfaces |
|---|---|
| **Loss Prevention** | **D019/D020/D033** (inventory adjustments) · **D021/D022/D029** (stock take results) · **J010** (SOH baseline) · J004 (cashier-level transactions) · *(R-prefix would carry cashier exceptions, receiver exception, schedule-vs-loss when populated)* |
| Staffing | *(P-prefix; not present in source corpus)* · J004 (sales person productivity) |
| Store Location Analysis | **C012** (store attributes + hierarchy) · J004 (per-store sales) · S008/S035 (store master maintenance) |
| Store Optimization | **J010** (SOH) · **J015** (forecast) · J001 (allocations) · J023 (ASN) · F001 (PO — On Order) |
| Transaction Profitability | J004 (transaction-level sales) · C010 (cost reference) · S003/S082 (margin) |
| Vendor Performance | C008 + F012 (vendor master) · F004/F013 (invoice + ack) · D028 (GRN) · D030/D032/D035 (RTV) · J097/J097.5 (BOL) |

### Multi-Channel Management

| BST | Feeding interfaces |
|---|---|
| eCommerce Analysis · Catalog Analysis · Call Center Analysis | (source corpus is brick-and-mortar; multi-channel cells are populated by Solex commerce mockup in v0.3) · J004 covers cross-channel sales facts where channel attribute is present |

### Corporate Finance Management

| BST | Feeding interfaces |
|---|---|
| Financial Management Accounting | **F001** (PO) · **F004** (supplier invoice) · **F014** (reconciled invoice) · D028 (GRN — three-way match leg) · D029 (inventory valuation) |
| Income Analysis | J004 (revenue) · C010 (price) · F001/F004 (cost) · S003/S082 (margin/waste) |
| Capital Allocation · Credit Risk | (canonical; source corpus thin in CFO-facing domain) |

## Patterns visible in the corpus

A few structural observations from the catalog itself:

1. **Master data flows once, dimensions reach everywhere.** C-prefix
   masters (product, supplier, store, warehouse, hierarchy) plus J002
   / J006 / S033 / S035 / S036 (the master-data feeds into the reporting
   domain) appear in the "feeding interfaces" column of nearly every
   BST. The dimensional spine is fewer than 20 interfaces; everything
   else is fact.
2. **One fact source dominates.** **J004 (Sales from Till)** is the
   single most-cited interface across all BSTs. The whole capability
   surface in Customer / Products & Services / Merchandising / Store
   Ops / Multi-Channel funnels back to this one feed. SMB consequence:
   if you can ingest POS sales cleanly, you can compute most of the
   capability surface.
3. **Loss Prevention is fed entirely by movement events.** D-prefix
   inventory adjustments + stock takes + the SOH baseline (J010) plus
   J004 cashier-attributed transactions. No special "fraud detection
   feed" exists — fraud is *derived* from the same operational data
   that feeds inventory and finance.
4. **The Forecasting/Ordering domain is the busiest.** J-prefix
   carries 27 interfaces — more than any other domain. This reflects
   that planning is where analytics, transactions, and master data
   converge in real time.
5. **Two empty domains are not noise.** P (People) and R (Retail/Store)
   being empty in this source corpus reflects organizational scope, not
   a structural absence. Both are first-class domains in the canonical
   spine; they need to be populated from elsewhere.

## What this enables

Anything that has to claim "we cover retail capability X" can now be
checked against:

- *Which interfaces in this catalog feed X?*
- *Which of those does the system being claimed for have an analog of?*
- *What's the gap?*

That's the core utility. It also means new sources entering the vault
(Solex commerce mockup, Heartbeat / Fireball OOS prior art, Canary
modules, Secure wiki cards) can each be mapped against the same
substrate without inventing new taxonomy.

## Related

- [[Brain/projects/RetailSpine|RetailSpine MOC]] — capability-surface
  decomposition this catalog cross-references
- [[Brain/raw/inbox/retail-business-intelligence-solution-v7|RBIS V7
  full transcription]] — the BST decomposition source
- [[Brain/projects/Secure|Secure MOC]] — prior-art retail engagements
  whose patterns inform this catalog
- [[Brain/projects/Canary|Canary MOC]] — current implementation that
  the canonical surface will eventually be mapped onto (RetailSpine v0.6)

## Sources

- `Brain/raw/inbox/Interface Design Documents/` — 378 source files across
  5 active prefix folders (C / D / F / J / S) and 2 empty placeholders
  (P / R), assembled at one Tier-1 grocer's Oracle Retail rollout but
  representing canonical industry patterns
- `Brain/projects/RetailSpine.md` — the capability spine each interface
  is mapped against
- `Brain/raw/inbox/retail-business-intelligence-solution-v7.md` — the
  BST decomposition the mapping targets

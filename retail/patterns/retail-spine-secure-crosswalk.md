---
date: 2026-04-23
type: wiki
tags: [retail-spine, secure, prior-art, loss-prevention, crosswalk]
sources:
  - Brain/wiki/secure-*.md
  - Brain/projects/Secure.md
  - Brain/projects/RetailSpine.md
last-compiled: 2026-04-23
needs-review: 2026-05-23
status: v0.4
---

# Retail Spine — Prior-Art Cards Crosswalk

## Summary

Maps the 18 Secure prior-art wiki cards to the
[[Brain/projects/RetailSpine|RetailSpine MOC]] BST decomposition.
Most of the cards land on Store Operations (Loss Prevention is the
density centre) and Merchandising; several inform Multi-Channel,
Products & Services (Vendor), and the cross-cutting operating-model
view.

This crosswalk is *contextual*, not data-flow. Where the integration
spine and Solex crosswalk show *data flowing into BSTs*, the Secure
cards describe **how the BSTs were actually instantiated in production**
across years of enterprise retail engagements — what the platform
looked like, what the case workflow was, what the operating model
demanded, what the requirements documents specified. They are the
*lived-prior-art* layer of the spine.

## What this source contributes

A two-decade record of how a generation of enterprise retailers
actually operated the BSTs catalogued in RBIS. Each card is one of
three flavors:

1. **Product / platform cards** (Secure Platform Overview, Secure 5
   Inventory, Secure Lite, Secure Architecture, Secure Omnichannel) —
   describe a real LP / inventory product family and how it instantiated
   the relevant BSTs.
2. **Deployment / engagement cards** (Top-5 Grocery Chain, LPMS
   Sporting-Goods, Sysrepublic xBR Athleisure, DSD iRED, Customer Order
   Mgmt 2017, Eagle Eye 2018) — describe a specific production deployment
   or requirements engagement and the BST coverage it actually shipped.
3. **Operating-model / consulting-era cards** (Retail Operating Model
   2006, Property & Building Services 2002, US Property IT, Private
   Label 2006, Integrated Maps 2003, Merchandising RFP / Evant 2003,
   Pre-Secure Career Archive) — describe how retailers organised
   themselves around the BSTs at the operating-model level.

Together these cards turn the BST decomposition from *capability
inventory* into *capability-in-the-wild evidence* — what the work
actually looked like when retailers ran it.

## Card → BST mapping

Cards listed in approximate density-of-mapping order: heaviest LP
density first, then Merchandising/Distribution, then Multi-Channel,
then operating-model breadth.

| Card | Domains touched | Specific BSTs informed |
|---|---|---|
| [[secure-platform-overview]] | Store Ops · Multi-Channel | Loss Prevention (product identity, exception-based reporting paradigm) · Vendor Performance (case-supported vendor exceptions) — sets the paradigm against which all other LP-product cards describe variants |
| [[secure-architecture]] | Cross-cutting | (architectural — SSO/SAML/OIDC, factory delivery process; informs *how* BST-bearing systems are deployed and integrated, not which BSTs they instantiate) |
| [[secure-lite]] | Store Ops | Loss Prevention (SMB-variant evidence — what the product looks like collapsed for smaller deployments). Direct prior art for the SMB collapse principle in [[Brain/projects/RetailSpine\|RetailSpine MOC]] |
| [[secure-omnichannel]] | **Multi-Channel** · Store Ops | eCommerce Analysis · Catalog Analysis (BOPIS / BORIS surface) · Loss Prevention (omnichannel fraud detection — order-vs-fulfilment exception paradigm). One of the only enterprise-prior-art cards that lands *directly* on Multi-Channel BSTs |
| [[secure-eagle-eye-fnr-2018]] | Store Ops | Loss Prevention (functional + non-functional requirements for an LP product family — provides the requirement-level granularity that informs how a BST cell becomes a shipped product feature) |
| [[secure-lpms-case-management-2015]] | Store Ops | Loss Prevention (case management deployment for sporting-goods chain; firearms-regulated taxonomy + reference-data design) · Service Delivery Analysis (case workflow as a service) |
| [[secure-sysrepublic-xbr-2016]] | Store Ops · Merchandising | Loss Prevention (xBR = exception-based reporting; 10 requirement categories spanning cashier exceptions, inventory exceptions, audit) · Inventory Analysis (exception detection on inventory movements) |
| [[secure-5-inventory]] | Merchandising · Store Ops | Inventory Analysis (Out of Stock by Product, Days of Supply, Damages/Stressed/Aged, Slow Moving, Total COGS on Hand by Location) · Loss Prevention (Inventory Discrepancy — `s5-1` and `ebr` tags signal exception-based reporting on the inventory side, the same paradigm as xBR for transactions) |
| [[secure-dsd-ired-analytics]] | Distribution / Products & Services · Store Ops | **Vendor Performance** (DSD = Direct Store Delivery; iRED = invoice/receipt/exception/delivery analytics — Vendor Compliance for billing, delivery, fulfillment, rebate) · Loss Prevention (credit-invoice / variance detection on supplier-direct deliveries — vendor-fraud surface) |
| [[secure-customer-order-management-flow-2017]] | **Multi-Channel** · Store Ops | eCommerce Analysis (cross-channel order flow) · Catalog Analysis (catalog-to-fulfilment routing) · Loss Prevention (BOPIS / ship-from-store fraud surface) · Service Delivery Analysis (order-to-fulfillment SLA) |
| [[secure-merchandising-rfp-evant-response-2003]] | **Merchandising** · Products & Services · Multi-Channel | Pricing Analysis · Promotion Analysis · Assortment & Allocation · Inventory Analysis · Product Analysis (RFP-level requirements for a full merchandising suite — informs what enterprise expected from each Merchandising BST in the early-2000s catalog-retailer context) |
| [[secure-dv-private-label-2006]] | Products & Services · Merchandising | Vendor Performance (private-label setup workflow) · Pricing Analysis (private-label pricing tier) · Product Analysis (private-label SKU lifecycle) — design-validation level evidence for how Vendor / Pricing / Product BSTs interlock |
| [[secure-retail-operating-model-2006]] | Cross-cutting (all 6 RBIS domains) | (operating-model card — describes how an enterprise retailer organised people, process, and systems against the full BST surface; the closest 1:1 to the RetailSpine MOC structure itself, written 19 years earlier) |
| [[secure-property-services-operating-model-2002]] | Store Ops · Corporate Finance | Location Profitability · Location Exposure · ABC (Activity Based Costing) Analysis · Org Unit Profitability · Capital Allocation Analysis (RACI-level operating-model evidence for the property/estate side of Store Ops) |
| [[secure-us-property-it-scoping]] | Store Ops | Location Profitability · Location Exposure (US estate-side scoping evidence) |
| [[secure-integrated-maps-2003]] | Cross-cutting | (solution-landscape card naming the SAP and other systems in a hardlines retailer's stack circa 2003 — informs the *system-side* of which interfaces from the integration spine appear at which BST cells) |
| [[secure-client-top5-grocery-chain]] | Cross-cutting | (client-implementation card describing how a top-5 grocery chain deployed Secure + Retek + EBR + DSD; spans Store Ops LP densely, Merchandising Inventory, Distribution Vendor Performance, Customer (loyalty)) |
| [[secure-retail-career-archive]] | (index) | (archive-stub card — pointer to pre-Secure career history; not directly BST-mapping but provides chronological context for the operating-model cards above) |

## Domain density — where Secure cards cluster

How many cards inform each RBIS domain:

| Domain | Density | Cards |
|---|---|---|
| Store Operations Management | **High** (12 cards) | Platform Overview, Lite, Omnichannel, Eagle Eye, LPMS, Sysrepublic xBR, 5-Inventory, DSD iRED, Customer Order Mgmt, Property Services Op Model, US Property IT, Top-5 Grocery |
| Merchandising Management | **Medium** (7 cards) | 5-Inventory, Sysrepublic xBR, Merchandising RFP / Evant, DV Private Label, Top-5 Grocery, Operating Model 2006, Integrated Maps |
| Multi-Channel Management | **Medium** (3 cards) | Omnichannel, Customer Order Mgmt 2017, Merchandising RFP / Evant |
| Products & Services Management | **Medium** (4 cards) | DSD iRED, DV Private Label, Merchandising RFP, Top-5 Grocery |
| Customer Management | **Low** (2 cards via reference) | Top-5 Grocery (loyalty), Customer Order Mgmt 2017 (identified-shopper) |
| Corporate Finance Management | **Low** (2 cards) | Property Services Op Model, DSD iRED (variance to GL) |
| Cross-cutting (architecture / op-model) | (not BST-mapped per se) | Architecture, Retail Operating Model 2006, Integrated Maps, Career Archive |

## What Secure prior art tells us about each cell

Reading the same map cell-wise, by RBIS domain:

### Store Operations Management

The **Loss Prevention BST is the densest cell in the entire spine**.
Twelve Secure cards inform it from different angles:

- *Product evolution* — Platform Overview and Lite establish the
  enterprise-vs-SMB axis. Sysrepublic xBR (2016), Eagle Eye (2018), and
  5-Inventory (2018–2021) show how the LP product family expanded from
  cashier-exception detection into inventory-shrink + omnichannel-fraud.
- *Deployment specifics* — LPMS Sporting-Goods (firearms-regulated
  taxonomy), Top-5 Grocery (Retek + EBR + DSD), and Customer Order Mgmt
  2017 (BOPIS fraud surface) show what the BST looked like in three
  very different production contexts.
- *Engagement framing* — Omnichannel (paradigm), Eagle Eye (FNR
  document), Architecture (SSO/SAML/factory delivery) show how the
  product was sold, requirement-engineered, and integrated.

### Merchandising Management

Heaviest in **Inventory Analysis** (5-Inventory + Sysrepublic xBR
inventory-side) and **Pricing / Promotion / Assortment** (Merchandising
RFP / Evant 2003 + DV Private Label 2006). The 2003 Evant RFP is
particularly useful as a complete enterprise requirements document for
the full Merchandising suite — what Pricing, Promotion, Assortment,
Inventory, and Product Analysis BSTs were expected to ship in a
Tier-1 catalog retailer 22 years ago.

### Multi-Channel Management

Three cards — Omnichannel (BOPIS/BORIS paradigm), Customer Order Mgmt
2017 (cross-channel data flow), Merchandising RFP / Evant 2003
(multi-channel merchandising) — are the only direct prior-art cards in
this domain. Together with the Solex crosswalk
([[Brain/wiki/retail-spine-solex-crosswalk|v0.3]]), Multi-Channel cells
are now well-populated: prior-art for the *enterprise* shape of the
domain, worked example for the *SMB* shape.

### Products & Services Management

**Vendor Performance** is the strongest cell here, fed by DSD iRED
(invoice/receipt exception analytics), DV Private Label (vendor
relationship workflow), and Top-5 Grocery (Retek vendor integration).
Product Analysis and Business Performance Analysis get partial coverage
from Merchandising RFP and Top-5 Grocery.

### Customer Management

Thin on direct prior art (most enterprise LP and Merchandising
engagements treat Customer as a downstream beneficiary, not a primary
focus). Top-5 Grocery references loyalty; Customer Order Mgmt 2017
references identified-shopper segmentation. The Customer domain is
better served by the Solex crosswalk for now.

### Corporate Finance Management

Property Services Op Model (2002) and US Property IT cards inform the
**Location Profitability**, **Location Exposure**, and **Capital
Allocation** cells from the estate-management side. DSD iRED touches
**Financial Mgmt Accounting** via variance-to-GL reconciliation.

## What's not covered by the Secure cards

- **Customer demographics, lifetime value, attrition modelling at
  depth** — enterprise LP engagements treat customer largely as a
  downstream attribute, not a primary entity. Solex crosswalk does
  better here.
- **Forecasting & Planning at the BST report level** — the Secure
  cards capture operating-model and exception-based work, not
  forward-looking statistical forecasting. The Heartbeat / Fireball
  extraction (RetailSpine v0.5) will fill some of this from the
  out-of-stock detection angle.
- **Capital allocation, credit risk, advanced corporate-finance** —
  out of scope for LP-focused engagements.

## Patterns visible across the Secure corpus

1. **Loss Prevention is what enterprise retail kept investing in.**
   Twelve cards over two decades all tracing back to the LP cell. The
   capability is durable; the *technology* generation re-invents
   regularly (Retek → Sysrepublic → Eagle Eye → Secure 5).
2. **The inventory-side of LP and the inventory-side of Merchandising
   are the same data, viewed two ways.** 5-Inventory and Sysrepublic
   xBR both treat inventory as an exception-based reporting surface
   for LP, while Merchandising RFP / Evant treats it as an operational
   planning surface. Same source data, different BSTs computed.
3. **Operating-model artefacts predate the systems by years.** The
   2002 Property Services and 2003 Integrated Maps work captured the
   org structure and system landscape that 2006-2018 LP product
   evolution slotted into. The capability decomposition is more stable
   than any specific implementation.
4. **The omnichannel pivot is well-marked in 2017.** The Customer
   Order Management Flow 2017 card is the clear hinge between
   pre-omnichannel LP (cashier-and-back-room focus) and omnichannel LP
   (cross-channel order-vs-fulfilment focus). It's the moment the LP
   product family had to expand to cover Multi-Channel cells.

## Related

- [[Brain/projects/RetailSpine|RetailSpine MOC]] — the spine this
  crosswalk populates
- [[Brain/projects/Secure|Secure MOC]] — the Secure project that holds
  these cards
- [[Brain/wiki/retail-integration-spine|Retail Integration Spine]] —
  enterprise-integration counterpart (v0.2)
- [[Brain/wiki/retail-spine-solex-crosswalk|Solex Crosswalk]] — SMB
  e-commerce worked-example counterpart (v0.3)

## Sources

- 18 cards under `Brain/wiki/secure-*.md` (collected via
  `Brain/projects/Secure.md` MOC)
- `Brain/projects/Secure.md` — Secure project MOC
- `Brain/projects/RetailSpine.md` — the BST decomposition this maps
  against

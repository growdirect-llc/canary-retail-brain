---
date: 2026-04-23
type: wiki
tags: [retail-spine, solex, e-commerce, multi-channel, crosswalk]
sources:
  - docs/superpowers/specs/2026-04-23-solex-commerce-mockup-design.md
  - Brain/projects/RetailSpine.md
  - Brain/wiki/retail-integration-spine.md
last-compiled: 2026-04-23
needs-review: 2026-05-23
status: v0.3
---

# Retail Spine — E-commerce Worked Example Crosswalk

## Summary

Maps the components, data flows, and entities of a single-channel SMB
e-commerce site (the Solex commerce mockup spec) onto the
[[Brain/projects/RetailSpine|RetailSpine MOC]] BST decomposition.
Populates the previously-empty Multi-Channel cells and surfaces the
adjacent reach into Customer, Products & Services, Merchandising, and
Store Operations that any real e-commerce surface produces by virtue of
being operated.

This is the *worked example* counterpart to the integration spine in
[[Brain/wiki/retail-integration-spine|Retail Integration Spine]]: the
integration spine catalogs *what flows* in an enterprise stack, this
crosswalk shows *what populates* when a minimal-viable single-channel
e-commerce app actually runs.

## What this source contributes

A complete, runnable, single-merchant, single-channel SMB e-commerce
fixture. Its presence in the spine matters because:

1. **It instantiates the Multi-Channel domain.** Multi-Channel was
   the only RBIS domain with no source-of-truth feeding it from the
   integration spine (the source corpus was brick-and-mortar). The
   e-commerce fixture fills eCommerce Analysis BST and Catalog Analysis
   BST from a real production-shaped surface.
2. **It demonstrates the SMB collapse principle in code.** The spec
   collapses what would be a 5-system enterprise stack (catalog hub +
   pricing engine + cart + checkout + subs + inventory + tax + shipping
   + fulfillment) into a single Flask service with named modules. Same
   capabilities, dramatically fewer moving parts. This is the ODS-as-EDW
   principle (RetailSpine design principle 1) applied to the operational
   tier rather than the analytics tier.
3. **It produces fact data.** As an operating merchant against the
   Square sandbox, it generates real transactions, refunds, inventory
   adjustments, subscription charges, and webhook events — the same
   shape of data the J004 (sales from till) feed in the integration
   spine carries, but in commodity form.

## Component → BST mapping

Each Solex service module (spec §4) mapped to the BSTs whose data it
produces, populates, or makes computable.

| Solex component | RBIS BSTs it populates |
|---|---|
| `services/catalog.py` (browse, search, catalog mgmt) | **Multi-Channel: Catalog Analysis** (cross catalog purchase profiles, product placement to purchase propensity) · Products & Services: Product Analysis (catalog inventory, product detail) |
| `services/cart.py` (lifecycle, totals, promo apply) | **Multi-Channel: eCommerce Analysis** (session cycle, cart events) · Customer: Market Basket Analysis (cart composition) · *abandoned-cart* feeds eCommerce Analysis funnel reports |
| `services/checkout.py` (place_order orchestration) | **Multi-Channel: eCommerce Analysis** (purchase events, method of payment to actual sales) · Customer: Purchase Profiles (customer × product) · Store Ops: Transaction Profitability · Corporate Finance: Financial Mgmt Accounting (revenue capture) |
| `services/inventory.py` (on-hand, decrement, increment, adjust_to) | Merchandising: Inventory Analysis (On Hand) · **Store Ops: Loss Prevention (Inventory Discrepancy — `reason='shrink'` adjustments are the SMB analog of D019/D020)** · Merchandising: Inventory (Slow Moving — derivable from low decrement velocity) |
| `services/subscriptions.py` (autoship engine) | **Customer: Customer Loyalty** (subscription = highest-loyalty signal) · Customer: Customer Lifetime Value · Customer: Customer Movement Dynamic (subscription pause/resume/cancel = direct attrition signal) · **Multi-Channel: eCommerce Analysis** (subscription cohort = identified-shopper segmentation) |
| `services/refunds.py` (issue_refund, restore inventory) | Store Ops: Loss Prevention (refund-pattern detection) · Customer: Customer Complaints Analysis (return reasons) · Multi-Channel: Catalog Analysis (return rate per product) · Corporate Finance: Income Analysis (refund offsets) |
| `services/email.py` (transactional templates) | Customer: Campaign & Promotion Analysis (cart abandonment, win-back) · Customer: Customer Interaction Analysis |
| `services/scenarios/` (admin-triggered transaction batches) | (cross-cutting test-data generator — produces signal across most BSTs above; specific scenarios listed below) |
| `services/webhooks.py` (Square reconciliation) | Store Ops: Loss Prevention (orphan-payment recovery → reverse-payment audit trail) · Corporate Finance: Financial Mgmt Accounting (reconciled state) |
| `services/auth.py` (magic-link + password) | Customer: Customer Profile Analysis (identified vs guest) |
| `services/tax.py` / `shipping.py` / `addresses.py` / `fulfillment.py` | Multi-Channel: eCommerce Analysis (geographic distribution of orders) · Corporate Finance: Income Analysis (gross-to-net) |
| `services/analytics.py` (page views, add-to-cart, checkout-started, purchase events) | **Multi-Channel: eCommerce Analysis (clickstream patterns with sales results, session cycle count)** · Customer: Customer Movement Dynamic |
| `services/abandonment.py` (recovery email sweep) | Customer: Campaign & Promotion Analysis (recovery email response) · Multi-Channel: eCommerce Analysis (funnel) |

## Data flow → BST event mapping

Spec §6 describes 5 named flows. Each generates a specific event shape
that populates BST report computations.

| Solex flow | Event shape | RBIS BSTs computable from it |
|---|---|---|
| **6.1 Guest checkout (happy path)** | cart_created → cart_lines_added → checkout_started → square_order_created → square_payment_succeeded → order_persisted → inventory_decremented → email_enqueued → analytics_purchase | Multi-Channel: eCommerce Analysis (session cycle, method of payment to sales) · Customer: Purchase Profiles, Market Basket · Products & Services: Sales by Product · Merchandising: Inventory (decrement event) · Store Ops: Transaction Profitability |
| **6.2 Autoship charge** | scheduled_check → due_subscriptions_found → for-each: charge_saved_card → place_order(autoship_source=...) | Customer: Customer Loyalty (subscription tenure), Customer Lifetime Value, Customer Movement Dynamic · Multi-Channel: eCommerce Analysis (identified-shopper segment by period) |
| **6.3 Scenario run** | admin_triggered → scenario_emit → place_order × N (with scenario_tag) | Cross-cutting — populates whichever BSTs the scenario targets (see scenario table below) |
| **6.4 Refund** | refund_requested → square_refund_created → refund_persisted → order.status updated → inventory_incremented → email_enqueued | Store Ops: Loss Prevention (refund pattern, value-of-refund-to-prior-sales ratio) · Customer: Customer Complaints · Corporate Finance: Income Analysis |
| **6.5 Catalog import** | yaml_loaded → for-each: upsert_product → image_copy → search_index_rebuilt | Products & Services: Product Analysis (catalog inventory baseline) · Multi-Channel: Catalog Analysis (catalog mix baseline) |

## Scenario → BST coverage matrix

Spec §4.9 enumerates 9 named scenarios. Each is a deliberate fact pattern
designed to populate specific BST cells.

| Scenario | RBIS BSTs exercised |
|---|---|
| `normal_retail_day` | Baseline for every BST — no anomaly population |
| `after_hours_burst` | Store Ops: Loss Prevention (after-hours cashier exception analog), Multi-Channel: eCommerce Analysis (session cycle by period) |
| `round_amount_cluster` | Store Ops: Loss Prevention (suspicious activity — round-amount pattern) |
| `high_value_sale` | Store Ops: Transaction Profitability, Customer: Customer Lifetime Value (high-value customer detection) |
| `autoship_cohort` | Customer: Customer Loyalty, Customer Lifetime Value, Customer Movement Dynamic (recurring-purchase pattern) |
| `bulk_reseller_order` | Customer: Market Basket Analysis (large basket), Customer: Customer Profitability (bulk-buyer segment), Products & Services: Sales Quantity by Products |
| `refund_wave` | Store Ops: Loss Prevention (refund-pattern detection across cohort), Customer: Customer Complaints Analysis |
| `shrink_event` | **Store Ops: Loss Prevention (Inventory Discrepancy — direct shrink signal)**, Merchandising: Inventory Analysis (Damages / Stressed / Aged equivalent) |
| `cart_abandonment_cohort` | Multi-Channel: eCommerce Analysis (funnel patterns), Customer: Customer Interaction Analysis |

## Data model → BST dimension/measure mapping

Spec §5 lists 9 model groupings. Each contributes specific dimensions
and measures to the BSTs above.

| Solex model group | Dimensions contributed | Measures contributed |
|---|---|---|
| 5.1 Catalog (Product, Category, ProductImage) | Product, Category, Brand | (master, no facts) |
| 5.2 Inventory (Inventory, InventoryAdjustment) | Reason (sale, refund, shrink, restock, manual) | Quantity-on-hand, Adjustment-quantity, Adjustment-velocity |
| 5.3 Customers + auth (Customer, AdminUser) | Customer, Customer-segment (autoship vs one-off vs guest), Geo (via address), Acquisition channel | Customer-count, New-customer-count |
| 5.4 Cart (Cart, CartLine) | Cart-stage, Funnel-position | Cart-value, Add-to-cart-count, Abandon-rate |
| 5.5 Order (Order, OrderItem, Tender) | Order-status, Channel, Payment-method, Tax-jurisdiction, Shipping-region, Promo-code-applied | Order-count, Order-value, Tax-collected, Shipping-collected, AOV (avg order value) |
| 5.6 Subscriptions (Subscription) | Subscription-status, Cadence, Tenure-bucket | Subscription-count, MRR, Subscription-pause-rate, Subscription-cancel-rate |
| 5.7 Refunds + returns (Refund, ReturnRequest) | Refund-reason, Return-status | Refund-count, Refund-value, Refund-rate, Return-to-sale-ratio |
| 5.8 Ops / observability (SquareWebhookEvent, ScenarioRun, AnalyticsEvent) | Webhook-type, Scenario-tag, Event-type | Event-count, Reconciliation-lag, Funnel-step-rate |
| 5.9 Migrations | (operational only) | (operational only) |

## Coverage assessment per BST cell

How completely Solex populates each BST cell it touches.

### Multi-Channel Management

| BST | Coverage | Note |
|---|---|---|
| eCommerce Analysis | **Full** | All 9 sample reports computable from Solex order + cart + analytics + customer data |
| Catalog Analysis | **Full** | All 3 sample reports computable from Solex catalog + order data; demographic-response is thin (only what the customer profile carries) |
| Call Center Analysis | **None** | No call center surface in spec |

### Customer Management

| BST | Coverage | Note |
|---|---|---|
| Purchase Profiles | **Full** | Order × catalog × customer is the full join |
| Customer Profiles | **Partial** | Limited by what the customer record carries (no demographics beyond geo from address) |
| Product Purchasing RFQ | **Full** | Repeat-purchase patterns from autoship + repeat one-off orders |
| Campaign & Promotion Analysis | **Partial** | Cart abandonment campaigns yes; broader campaign attribution limited |
| Cross Purchase Behavior | **Full** | Order × catalog cross-product patterns |
| Target Product Analysis | **Full** | Per-product order metrics |
| Customer Movement Dynamic | **Full** | Subscription pause/resume/cancel + acquisition timestamps = direct dynamic |
| Market Basket Analysis | **Full** | OrderItem composition |
| Customer Loyalty | **Full** | Subscription tenure + repeat-order behavior |
| Customer Lifetime Value | **Full** | Cumulative-order-value per customer |
| Customer Profitability | **Partial** | Needs cost data (currently catalog price only); profitability derivable post-hoc |
| Customer Attrition | **Partial** | Subscription cancel = strong signal; one-off-customer attrition needs definition |
| Customer Complaints | **Partial** | Refund reasons + return requests; no separate complaints surface |
| Customer Credit Risk · Delinquency | **None** | Square handles payment risk; not surfaced into Solex |
| Customer Interaction Analysis | **Partial** | Email send/open thin in spec; analytics events present |
| Lead Analysis · Market Analysis | **None** | Solex doesn't track pre-sale leads or external market data |

### Products & Services Management

| BST | Coverage | Note |
|---|---|---|
| Product Analysis | **Full** | Sales × catalog at product / category granularity |
| Business Performance Analysis | **Partial** | Most sub-reports (sales by product, new item, discontinue) computable; vendor-side reports (compliance, fulfillment, rebate, in-stock) not present — Solex has no supplier-management surface |
| Product Profitability | **Partial** | Needs cost-of-goods (catalog has price only); structurally derivable |
| Planning and Forecasting | **Partial** | Forward-looking forecast outside spec; backward-looking velocity yes |

### Merchandising Management

| BST | Coverage | Note |
|---|---|---|
| Inventory Analysis | **Partial** | On-hand + adjustments yes; no warehouse/multi-location dimension; no on-order (Solex has no PO/replenishment) |
| Pricing Analysis | **Partial** | Set vs Actual Price yes (catalog vs OrderItem.unit_price); markdown trend yes; competitive/multi-channel pricing not present |
| Promotion Analysis | **Partial** | Promo-code-applied dimension yes; promotion engine itself stubbed in v1 |
| Assortment / Allocation | **Partial** | Single-store, single-channel — assortment is the catalog itself; no multi-store allocation |
| Physical Merchandising / Space Mgmt | **None** | No physical store, no planogram |

### Store Operations Management

| BST | Coverage | Note |
|---|---|---|
| **Loss Prevention** | **Full** | `shrink_event` scenario produces direct shrink signal; refund-wave produces refund pattern; round-amount + after-hours scenarios produce suspicious-activity patterns. Solex is a **production source** for LP detection, not just a fixture |
| Transaction Profitability | **Full** | Per-order revenue + per-order line-item composition |
| Service Delivery Analysis | **Partial** | Webhook-reconciliation lag = service-delivery proxy; no traditional CS surface |
| Vendor Performance | **None** | No vendor surface |
| Staffing | **None** | No employee surface (Solex is GrowDirect-operated, not multi-employee retail) |
| Store Location Analysis | **None** | Single-location |
| Store Optimization | **Partial** | Inventory-projection logic absent in v1 |

### Corporate Finance Management

| BST | Coverage | Note |
|---|---|---|
| Financial Mgmt Accounting | **Full** | Order revenue + refund offsets + Square payouts (post-MVP integration) = complete revenue/refund surface |
| Income Analysis | **Full** | Order × Refund × Subscription = revenue analysis surface |
| Capital Allocation · Credit Risk | **None** | Out of scope for an SMB e-commerce |

## What Solex's coverage tells us about the SMB collapse

Reading the coverage table column-wise produces three observations:

1. **Multi-Channel and Corporate Finance compress cleanly.** A single
   well-built e-commerce app gives you nearly the full RBIS report set
   for both. The enterprise reference assumed call-center + catalog
   division-of-labor; in SMB, the e-commerce app *is* the channel and
   the order *is* the financial transaction.
2. **Customer compresses well.** Authenticated customers + order
   history + subscription state covers most Customer BSTs. The gaps
   (credit risk, delinquency, lead, market) are gaps Square handles or
   that don't apply at SMB scale.
3. **Merchandising and Store Ops are where the missing operational
   schemas surface.** The gaps in Merchandising (multi-location
   inventory, on-order, planogram, assortment-allocation) and Store
   Ops (vendor, staffing, multi-store) are exactly the gaps that
   RetailSpine v0.6 will need to close — and they're the gaps that
   motivate the candidate new operational schemas (`vendor`, `merch`,
   `channel`) noted in the MOC.

A useful corollary: an SMB doesn't need a new system for each gap.
Solex shows that **a single well-modeled operational app can populate
~70% of the canonical capability surface**. The remaining 30% is
either out-of-scope for SMB scale (capital allocation), Square-handled
(credit risk), or addressable by extending the same operational schema
rather than building a separate system.

## What's not covered (gaps for downstream work)

- **Vendor surface** — Solex has no supplier management. Fills only
  via Square payouts (which collapses vendor into "Square fees + bank
  receipts"). Future operational schema candidate: `vendor`.
- **Multi-location inventory** — Solex is single-warehouse. The
  enterprise integration spine assumes warehouse + store + transit
  inventory tiers. Future operational schema candidate: extend
  inventory or add `merch.locations`.
- **Planogram / space management** — out of scope for online-only.
- **Call center** — out of scope.
- **Vendor performance / compliance** — needs supplier data.
- **Customer demographics beyond geo** — Solex doesn't capture; would
  enrich Customer Profiles, Customer Lifetime Value, Demographic
  Response BSTs significantly.

## Related

- [[Brain/projects/RetailSpine|RetailSpine MOC]] — the spine this
  crosswalk populates
- [[Brain/wiki/retail-integration-spine|Retail Integration Spine]] —
  enterprise interface counterpart this single-app worked example
  collapses
- [docs/superpowers/specs/2026-04-23-solex-commerce-mockup-design.md](../../docs/superpowers/specs/2026-04-23-solex-commerce-mockup-design.md) —
  the source spec
- [[Brain/projects/Canary|Canary MOC]] — the LP system that observes
  Solex's transaction stream

## Sources

- `docs/superpowers/specs/2026-04-23-solex-commerce-mockup-design.md` —
  full e-commerce mockup spec (Section 4 components, Section 5 data
  model, Section 6 data flows)
- `Brain/projects/RetailSpine.md` — the BST decomposition this maps
  against
- `Brain/wiki/retail-integration-spine.md` — the enterprise integration
  counterpart

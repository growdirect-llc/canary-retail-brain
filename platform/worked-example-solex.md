---
classification: confidential
owner: GrowDirect LLC
type: worked-example
status: v0.3
nav_order: 15

---

# Worked Example — Solex E-commerce Reference

A minimal, single-merchant, single-channel SMB e-commerce
implementation — GrowDirect's reference e-commerce front-end — used
as the production transaction source for Canary Retail. As an
operating merchant against the Square sandbox, it produces real
transactions, refunds, inventory adjustments, subscriptions, and
webhook events; Chirp/Fox (the Q-prefix loss-prevention module)
observes that stream.

This article reads column-wise across the Canary Retail module
spine and shows concretely how much of the canonical retail
capability surface a single well-modeled operational app can
populate. The answer, by coverage assessment: **~70%**.

That number is load-bearing. It is the evidence behind Canary
Retail's "SMB collapse" thesis — that the classical enterprise
retail decomposition (distinct catalog hub, pricing engine, cart,
checkout, subscription, inventory, tax, shipping, fulfillment,
and POS systems) compresses into one operational app for SMB
specialty retailers, without losing capability.

## Why this article exists

Canary Retail is a platform. Platform claims require evidence.
Solex is the evidence:

1. **It instantiates the Multi-Channel domain.** The enterprise
   reference model's Multi-Channel domain assumed call-center +
   catalog division-of-labor. In SMB specialty, the e-commerce
   app is the channel.
2. **It demonstrates the SMB collapse principle in code.** The
   same capability set that an enterprise stack splits across 5+
   systems collapses into one Flask service with named modules.
3. **It produces fact data.** Real transactions, refunds,
   inventory adjustments, subscription charges, and webhook
   events — the same shape of data an enterprise POS feed
   carries, in commodity form.

## Component → capability mapping

Each Solex service module mapped to the canonical retail
capability tables it populates.

| Solex component | Capability tables it populates |
|---|---|
| `services/catalog.py` | Multi-Channel: Catalog Analysis · Products & Services: Product Analysis |
| `services/cart.py` | Multi-Channel: eCommerce Analysis · Customer: Market Basket Analysis · abandoned-cart feeds funnel reports |
| `services/checkout.py` | Multi-Channel: eCommerce Analysis · Customer: Purchase Profiles · Store Ops: Transaction Profitability · Corporate Finance: Financial Mgmt Accounting |
| `services/inventory.py` | Merchandising: Inventory Analysis (On Hand) · **Store Ops: Loss Prevention (Inventory Discrepancy — `reason='shrink'` adjustments)** · Merchandising: Slow Moving (derivable from decrement velocity) |
| `services/subscriptions.py` | **Customer: Customer Loyalty** · Customer Lifetime Value · Customer Movement Dynamic (pause/resume/cancel) · **Multi-Channel: identified-shopper segmentation** |
| `services/refunds.py` | Store Ops: Loss Prevention (refund-pattern detection) · Customer: Customer Complaints · Multi-Channel: return rate per product · Corporate Finance: Income Analysis |
| `services/email.py` | Customer: Campaign & Promotion Analysis · Customer Interaction Analysis |
| `services/scenarios/` | Cross-cutting test-data generator |
| `services/webhooks.py` | Store Ops: Loss Prevention (orphan-payment recovery) · Corporate Finance: reconciled state |
| `services/auth.py` | Customer: Customer Profile Analysis (identified vs guest) |
| `services/tax.py` / `shipping.py` / `addresses.py` / `fulfillment.py` | Multi-Channel: geographic distribution · Corporate Finance: gross-to-net |
| `services/analytics.py` | **Multi-Channel: eCommerce Analysis (clickstream × sales, session cycle)** · Customer: Customer Movement Dynamic |
| `services/abandonment.py` | Customer: Campaign & Promotion Analysis (recovery) · Multi-Channel: funnel |

## Data flow → event mapping

Each named flow generates a specific event shape that populates
report computations.

| Flow | Event shape | Capabilities computable |
|---|---|---|
| **Guest checkout (happy path)** | cart_created → cart_lines_added → checkout_started → square_order_created → square_payment_succeeded → order_persisted → inventory_decremented → email_enqueued → analytics_purchase | Multi-Channel: eCommerce Analysis · Customer: Purchase Profiles, Market Basket · Products & Services: Sales by Product · Merchandising: Inventory (decrement) · Store Ops: Transaction Profitability |
| **Autoship charge** | scheduled_check → due_subscriptions_found → charge_saved_card → place_order(autoship_source) | Customer: Customer Loyalty (tenure), Customer Lifetime Value, Customer Movement Dynamic · Multi-Channel: identified-shopper segment |
| **Scenario run** | admin_triggered → scenario_emit → place_order × N (with scenario_tag) | Cross-cutting — targets specific tables |
| **Refund** | refund_requested → square_refund_created → refund_persisted → order.status updated → inventory_incremented → email_enqueued | Store Ops: Loss Prevention (refund pattern, value ratio) · Customer: Customer Complaints · Corporate Finance: Income Analysis |
| **Catalog import** | yaml_loaded → upsert_product → image_copy → search_index_rebuilt | Products & Services: Product Analysis · Multi-Channel: Catalog Analysis |

## Scenario → capability coverage

Named scenarios are deliberate fact patterns designed to populate
specific cells.

| Scenario | Capabilities exercised |
|---|---|
| `normal_retail_day` | Baseline for every table — no anomaly population |
| `after_hours_burst` | Store Ops: Loss Prevention (after-hours analog) · Multi-Channel: session cycle by period |
| `round_amount_cluster` | Store Ops: Loss Prevention (round-amount pattern) |
| `high_value_sale` | Store Ops: Transaction Profitability · Customer: Customer Lifetime Value (high-value detection) |
| `autoship_cohort` | Customer: Customer Loyalty, Customer Lifetime Value, Customer Movement Dynamic |
| `bulk_reseller_order` | Customer: Market Basket (large basket), Customer Profitability (bulk-buyer segment), Products & Services: Sales Quantity |
| `refund_wave` | Store Ops: Loss Prevention (refund pattern across cohort) · Customer: Customer Complaints |
| `shrink_event` | **Store Ops: Loss Prevention (Inventory Discrepancy — direct shrink signal)** · Merchandising: Inventory Analysis |
| `cart_abandonment_cohort` | Multi-Channel: funnel patterns · Customer: Customer Interaction Analysis |

## Data model → dimensions / measures

| Solex model group | Dimensions | Measures |
|---|---|---|
| Catalog (Product, Category, Image) | Product, Category, Brand | (master — no facts) |
| Inventory (Inventory, InventoryAdjustment) | Reason (sale, refund, shrink, restock, manual) | On-hand, adjustment-quantity, adjustment-velocity |
| Customers + auth | Customer, segment (autoship / one-off / guest), geo, acquisition channel | Customer-count, new-customer-count |
| Cart (Cart, CartLine) | Cart-stage, funnel-position | Cart-value, add-to-cart, abandon-rate |
| Order (Order, OrderItem, Tender) | Order-status, channel, payment-method, tax-jurisdiction, shipping-region, promo-code | Order-count, order-value, tax-collected, shipping-collected, AOV |
| Subscriptions | Subscription-status, cadence, tenure-bucket | Subscription-count, MRR, pause-rate, cancel-rate |
| Refunds + returns | Refund-reason, return-status | Refund-count, refund-value, refund-rate, return-to-sale ratio |
| Ops / observability (Webhook, Scenario, Analytics) | Webhook-type, scenario-tag, event-type | Event-count, reconciliation-lag, funnel-step-rate |

## Coverage assessment per capability domain

### Multi-Channel Management

| Capability | Coverage | Note |
|---|---|---|
| eCommerce Analysis | **Full** | All sample reports computable |
| Catalog Analysis | **Full** | Demographic-response thin |
| Call Center Analysis | **None** | No call-center surface |

### Customer Management

| Capability | Coverage | Note |
|---|---|---|
| Purchase Profiles | **Full** | Order × catalog × customer |
| Customer Profiles | **Partial** | Limited to geo + acquisition |
| Product Purchasing RFQ | **Full** | Repeat-purchase from autoship + one-off |
| Campaign & Promotion | **Partial** | Abandonment yes; broader attribution limited |
| Cross Purchase Behavior | **Full** | Order × catalog patterns |
| Target Product Analysis | **Full** | Per-product order metrics |
| Customer Movement Dynamic | **Full** | Subscription + acquisition timestamps |
| Market Basket | **Full** | OrderItem composition |
| Customer Loyalty | **Full** | Subscription tenure + repeat behavior |
| Customer Lifetime Value | **Full** | Cumulative order value |
| Customer Profitability | **Partial** | Needs cost-of-goods |
| Customer Attrition | **Partial** | Subscription cancel yes; one-off needs definition |
| Customer Complaints | **Partial** | Refund reasons + returns |
| Customer Credit Risk | **None** | Square handles |
| Customer Interaction | **Partial** | Email thin; analytics present |
| Lead / Market Analysis | **None** | No pre-sale or external market tracking |

### Products & Services Management

| Capability | Coverage | Note |
|---|---|---|
| Product Analysis | **Full** | Sales × catalog at product/category |
| Business Performance | **Partial** | Vendor-side reports absent |
| Product Profitability | **Partial** | Needs cost-of-goods |
| Planning and Forecasting | **Partial** | Backward velocity yes; forward forecast outside scope |

### Merchandising Management

| Capability | Coverage | Note |
|---|---|---|
| Inventory Analysis | **Partial** | On-hand + adjustments yes; no multi-location, no on-order |
| Pricing Analysis | **Partial** | Set vs Actual yes; markdown yes; competitive / multi-channel absent |
| Promotion Analysis | **Partial** | Promo-code dimension yes; engine stubbed |
| Assortment / Allocation | **Partial** | Single-channel; no multi-store allocation |
| Physical Merchandising / Space | **None** | No physical store |

### Store Operations Management

| Capability | Coverage | Note |
|---|---|---|
| **Loss Prevention** | **Full** | Shrink scenario + refund wave + round-amount + after-hours scenarios — Solex is a production source for LP, not just a fixture |
| Transaction Profitability | **Full** | Per-order revenue + line-item composition |
| Service Delivery Analysis | **Partial** | Webhook-reconciliation lag as proxy |
| Vendor Performance | **None** | No vendor surface |
| Staffing | **None** | No employee surface |
| Store Location Analysis | **None** | Single-location |
| Store Optimization | **Partial** | Inventory-projection absent |

### Corporate Finance Management

| Capability | Coverage | Note |
|---|---|---|
| Financial Mgmt Accounting | **Full** | Order revenue + refund offsets + Square payouts |
| Income Analysis | **Full** | Order × Refund × Subscription |
| Capital Allocation / Credit Risk | **None** | Out of scope for SMB e-commerce |

## What this coverage tells us — the SMB collapse

Reading the coverage column-wise produces three observations that
underpin the Canary Retail platform thesis.

1. **Multi-Channel and Corporate Finance compress cleanly.** A
   single well-built e-commerce app gives you nearly the full
   canonical report set for both. The enterprise reference assumed
   call-center + catalog division-of-labor; in SMB, the e-commerce
   app *is* the channel and the order *is* the financial
   transaction.
2. **Customer compresses well.** Authenticated customers + order
   history + subscription state covers most Customer capabilities.
   The gaps (credit risk, delinquency, lead, market) are gaps the
   payment processor handles or that don't apply at SMB scale.
3. **Merchandising and Store Ops are where the missing
   operational schemas surface.** The gaps in Merchandising
   (multi-location inventory, on-order, planogram,
   assortment-allocation) and Store Ops (vendor, staffing,
   multi-store) are exactly the gaps Canary Retail's module spine
   closes — and they motivate the non-Differentiated-Five prefixes
   (C / D / F / J / S / P / L / W) in [[spine-13-prefix]].

**A useful corollary:** an SMB doesn't need a separate system for
each gap. The Solex coverage shows that a single well-modeled
operational app populates ~70% of the capability surface. The
remaining 30% is either out-of-scope for SMB scale, processor-
handled, or addressable by extending the same operational schema
rather than building a separate system.

## What Solex does NOT cover (gaps for Canary Retail modules)

Each gap maps to a Canary Retail module on the spine:

- **Vendor surface** → **F** (Finance) module: vendor management,
  invoice and PO flow, supplier compliance.
- **Multi-location inventory** → **D** (Distribution) module:
  warehouse + store + transit tiers, store-to-store transfers.
- **On-order inventory** → **J** (Forecast & Order) module: PO /
  replenishment surface closes the open-order dimension.
- **Planogram / space management** → **S** (Space, Range, Display)
  module: for physical-store customers Canary Retail also serves.
- **Vendor performance / compliance** → **F** (Finance) + vendor-
  side of Merchandising.
- **Promotion engine** → **P** (Pricing & Promotion) module:
  extends Solex's promo-code stub into full promotion engine.
- **Staffing** → **L** (Labor & Workforce) module: employee
  surface, scheduling, time tracking.
- **Customer demographics beyond geo** → **R** (Customer) module
  extension when customer-data-platform integrations land.
- **Multi-domain work execution** → **W** (Work Execution) module:
  generalizes Chirp+Fox beyond LP to every domain in the spine.

## Related

- [[overview]] — platform positioning
- [[spine-13-prefix]] — the module catalog the gaps above populate
- [[crdm]] — the canonical data model the coverage is tested against
- [[../architecture/service-mesh]]

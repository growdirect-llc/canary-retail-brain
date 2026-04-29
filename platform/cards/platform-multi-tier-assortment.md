---
card-type: platform-thesis
card-id: platform-multi-tier-assortment
card-version: 1
domain: platform
layer: cross-cutting
status: approved
agent: ALX
tags: [assortment, ecom, inventory, fulfillment, bopis, store, warehouse, special-order, ecom-channel, iaas, item-master]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

The three-tier assortment model that lets an ecommerce store offer a wider catalog than the physical store actually carries, without breaking BOPIS trust. Each item has a per-store assortment tier — store, warehouse, or expanded — that governs how the storefront surfaces availability and how IaaS routes fulfillment at order time.

## Purpose

The merchant wants to sell what the customer wants. The customer wants reliable answers about when they can have it. These two goals collide if the storefront treats every item the same: a customer who picks BOPIS for an item the store doesn't actually carry has just been lied to. A customer who can't find an item online that the merchant could special-order has just been turned away.

The naive ecommerce model — one inventory pool, one availability number, one fulfillment path — solves neither problem. The merchant either loses the broader catalog (only what's on-shelf is online) or breaks the BOPIS guarantee (everything is online, but pickup is a coin flip). Neither is the right tradeoff for a small-footprint specialty merchant whose physical store is one node in a small distribution network.

The three-tier model resolves the conflict. The storefront surface is wider than the store. Each tier surfaces honestly: store-tier items show "pickup in an hour"; warehouse-tier items show "ships in 3 days"; expanded-tier items show "special order, 5–10 days." The customer makes an informed choice. The merchant captures the order they would otherwise lose.

## The three tiers

| Tier | Stock pool | Fulfillment paths | Availability source |
|---|---|---|---|
| **Store** | This store's on-hand (`shelf` + `backroom`) | BOPIS pickup, ship-from-store, in-store walk-in | `inventory_positions` for this `(store_id, item_id)` |
| **Warehouse** | Centralized warehouse on-hand (separate `location_id` of type `warehouse`) | Ship-to-customer from warehouse, store-replenishment transfer | `inventory_positions` for the warehouse location |
| **Expanded** | Not stocked anywhere — available via vendor drop-ship or special order | Vendor-direct ship, special order at the counter, in-store ring-up with vendor PO | Vendor capability registry — not a stock pool, a drop-ship promise |

The same item can sit in different tiers at different stores. A bottle of supplement carried locally is store-tier at store A and warehouse-tier at store B (because store B does not carry it but the chain warehouse does) and expanded-tier at store C (because the chain has stopped carrying it but the vendor will still drop-ship). The tier is a `(store_id, item_id)` mapping, not an item attribute.

## Routing decision at checkout

When an ecom order is placed against a specific store, IaaS evaluates options in tier order — store first, then warehouse, then expanded. The first tier that has the item in sufficient quantity wins. Ties (e.g., warehouse and store both have it; warehouse is closer to the customer's ship-to address) are broken by `fulfillment_routes` heuristics.

The order of evaluation is not "cheapest fulfillment first" — it is "fastest customer experience first." BOPIS in an hour beats warehouse-ship in three days even if the warehouse pick-and-pack cost is lower, because the merchant is competing on customer experience, not on margin per order.

## Ownership across modules

The tier model is data that lives in three different services:

- **`cmd/item`** owns the per-store assortment metadata: `(store_id, item_id, tier, active)`. The item master is the only writer. Other modules read but do not write.
- **`cmd/inventory-as-a-service`** owns availability across tiers — reading the tier metadata from item, and the stock pools from its own ledger.
- **`cmd/commercial`** owns the vendor-can-drop-ship registry that backs the expanded tier. Special-order availability is a vendor capability promise, not a stock count, so the data shape is different from the inventory ledger.
- **`cmd/ecom-channel`** consumes IaaS routing — surfaces tier-aware availability at cart, calls IaaS for the routing decision at checkout, emits the routed fulfillment plan in the `ecom.order.placed` event written to the RaaS chain.

The split exists because each module has a different rate of change. Item assortment metadata changes when the merchant decides to start or stop carrying an item locally — slow. Stock counts change every transaction — fast. Vendor drop-ship capability changes when a vendor contract is signed or terminated — slowest of the three. Co-locating them all in one module would force the slow data to ride the change cycle of the fastest.

## Storefront surface — tier-aware availability

The storefront does not show a single "in stock" boolean. It shows a tier-qualified availability:

| Tier | Storefront language |
|---|---|
| Store, on-hand | "Available for pickup in an hour at [store name]" |
| Warehouse, in-stock | "Ships in 3 days from our distribution center" |
| Expanded, vendor-orderable | "Special order — typically 5–10 days from the vendor" |
| All tiers out | "Backorder — notify me when available" or substitute suggestion |

The customer is choosing not just an item but a fulfillment promise. The merchant has surfaced an honest expectation. The platform has captured the order it would otherwise have lost to a less informative storefront.

## In-store ordering uses the same primitives

The same catalog and the same routing primitives power in-store ordering. An associate ringing up a special order at the counter is making the same routing decision as the ecom checkout flow — store-tier (already in the customer's hand), warehouse-tier (transfer in for pickup or ship to home), or expanded-tier (special order at vendor lead time). Only the UX surface and the channel attribution differ.

This is why `cmd/store-brain` (in-store agent) and `cmd/ecom-channel` (online ordering) both depend on `cmd/inventory-as-a-service` and `cmd/item`. The cart, the checkout invariant, and the routing decision are platform primitives, not channel-specific implementations.

## Source attribution

Solex (`/Users/gclyle/GrowDirect/Solex/`) is single-store and treats inventory as a single pool keyed only by item. The multi-tier assortment model is a Canary-Go addition, not a port-forward. Solex illustrates the cart-and-checkout invariants — those carry over. The tier overlay is new platform work.

## Invariants

- The tier mapping is `(store_id, item_id, tier)` — never a global per-item attribute. The same item can be store-tier at one location and expanded-tier at another, and that is correct.
- BOPIS is reserved for store-tier items only. A storefront that shows BOPIS on warehouse-tier items has broken the trust contract.
- The expanded tier is a vendor promise, not a stock pool. Calling `inventory_positions` for an expanded-tier item returns zero — that is the correct answer. Vendor capability is queried separately.
- Routing evaluates tiers in customer-experience order (store → warehouse → expanded), not cost order. Margin optimization is a secondary heuristic within a tier, not a tier-overriding rule.

## Sources

- `docs/sdds/go-handoff/inventory-as-a-service.md` → "Multi-Tier Assortment Model" section — the canonical contract
- `docs/sdds/go-handoff/item.md` — per-store assortment metadata ownership
- `docs/sdds/go-handoff/ecom-channel.md` → "Multi-tier fulfillment routing" — the consumer side
- `docs/sdds/go-handoff/commercial.md` — vendor drop-ship registry (expanded tier backing)

## Related

- [[retail-assortment-management]] — the operational practice of deciding which SKUs are in a store's regular assortment
- [[retail-replenishment-model]] — how store-tier replenishes from warehouse-tier
- [[platform-thesis]] — the broader platform context this pattern serves

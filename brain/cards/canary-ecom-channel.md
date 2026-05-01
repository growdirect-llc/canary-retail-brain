---
card-type: domain-module
card-id: canary-ecom-channel
card-version: 1
domain: merchandising
layer: domain
feeds:
  - canary-tsp
  - canary-inventory-as-a-service
receives:
  - canary-identity
tags: [ecom, channel, square-online, shopify, woocommerce, omnichannel, reservations, oauth]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: ecom-channel

## What this is

Adapter for ecommerce channels — Square Online (V1), Shopify and WooCommerce (V2+). Treats ecom orders as transactions on a parallel channel — same ARTS POSLog normalization, separate channel attribution.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9080` |
| Axis | A — Adapter Substrate · B — Resource APIs |
| Tier mix | Stream (webhook receivers, OAuth, connection mutations, reservations) · Change-feed (sync ops) · Reference (status reads) · Bulk window (historical order backfill) |
| Owned tables | `app.ecom_connections`, `app.ecom_oauth_state`, `app.ecom_sync_watermarks`, `app.ecom_reservations` |

## Purpose

Channel-to-ARTS mapping with explicit attribution (`transaction_metadata.channel`). Inventory reservation flow: cart-add → reserve stock with 15-min TTL → commit on checkout / release on abandonment. Omnichannel-attribution case ("did this customer buy in-store after browsing online") handled in canary-owl.

## Dependencies

- canary-identity, canary-tsp (transaction landing)
- canary-inventory-as-a-service (reservation engine)
- External ecom platforms (Square Online, Shopify, WooCommerce)

## Consumers

- canary-tsp (normalized transactions)
- canary-inventory-as-a-service (reservation events)
- canary-owl (omnichannel attribution joins)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-ecom-channel
- Card: [[axis-adapter]]
- Cards: [[tier-stream]], [[tier-change-feed]], [[tier-reference]], [[tier-bulk-window]]

---
classification: confidential
owner: GrowDirect LLC
type: platform-doc
date: 2026-04-24
tags: [arts, poslog, customer-model, device-model, site-model, standards-alignment]
---

# ARTS Adoption — POSLog · Customer · Device · Site

Canary Retail's module spine adopts the Association for Retail Technology Standards (ARTS), a vendor-neutral catalog of four interoperability specifications for retail systems. ARTS originated as an NRF working group and now serves as the reference frame for retail data interchange. Canary implements three of the four ARTS standards at v1 — POSLog, Customer Model, and Device Model — treating them not as an integration veneer but as the runtime schema.

## What ARTS is

ARTS is a family of four specifications published to close the semantic gap between retail vendors who build POS systems, payment processors, inventory platforms, and workforce tools. A retailer running Square for payments, Shopify for ecommerce, and Canary for loss prevention needs a common language for things like "transaction," "customer," and "device." ARTS provides that language: POSLog defines retail transactions; the Customer Model defines customers; the Device Model defines retail devices; the Site Model defines physical locations. The standards are technology-agnostic and focused on data shape and interchange, not on API protocol or storage.

## The four standards Canary adopts

### POSLog — Transaction interoperability

POSLog, developed and maintained by T (the Transaction module team), defines the canonical shape of a retail transaction and its constituent elements. Canary's [[T-transaction-pipeline|Transaction Pipeline]] module is the home of POSLog adoption.

At v1, Canary maps every Square webhook payload into POSLog constructs:

| ARTS POSLog construct | Canary table / column |
|---|---|
| RetailTransaction | `sales.transactions` |
| RetailTransaction.SequenceNumber | `transactions.external_id` (Square payment/refund ID) |
| RetailTransaction.LineItem | `sales.transaction_line_items` |
| Tender | `sales.transaction_tenders` |
| RetailTransaction.OperatorID | `transactions.employee_id` |
| RetailTransaction.WorkstationID | `transactions.device_id` |
| BeginDateTime | `transactions.transaction_date` |
| ControlTransaction (NO_SALE, PAID_IN/OUT) | `transactions.transaction_type` enum values |

POSLog field names are preserved at the API boundary where Canary publishes back out to integrators, even where internal column names diverge. This is the "ARTS-native, not ARTS-veneer" commitment: every ARTS field is answerable from the runtime schema, and the retailer experiences ARTS conformance, not a translation layer.

### Customer Model — Identity and lifecycle

The ARTS Customer Model, developed and maintained by R (the Customer module team), defines a customer entity with identity, lifetime metrics, and optional demographic and loyalty dimensions. Canary's [[R-customer|Customer]] module implements the v1 subset of the Customer Model.

The v1 implementation is deliberately minimal: R stores only the vendor-namespaced customer identifier and derived aggregates, with no PII at rest.

| ARTS Customer Model construct | Canary's v1 posture |
|---|---|
| CustomerID | `app.customers.square_customer_id` (vendor-namespaced) |
| Customer.LifetimeValue | `customers.lifetime_value_cents` (derived from transaction ledger) |
| Customer.FirstTransactionDate | `customers.first_seen_at` |
| Customer.LastTransactionDate | `customers.last_seen_at` |
| Customer.TransactionCount | `customers.transaction_count` |
| Customer.Name / ContactInfo / Demographics | Not stored; reads through to vendor at query time when workflow requires |
| Customer.LoyaltyAccount | Linked at FK; loyalty rows live in T's transaction surface |

The promise is **answerability**, not storage: every ARTS Customer Model field is answerable from Canary's schema. Some answers come from R's tables (LifetimeValue, FirstTransactionDate); others are answered by reaching back to the vendor's API (Name, ContactInfo) when a workflow demands them. The retailer experiences a unified customer entity without the privacy and GDPR burden of storing personal data.

A future cross-vendor identity layer — the `external_identities` scaffold — will extend this to customers who appear in multiple vendor namespaces (e.g., a customer who appears in both Square in-store and Shopify online).

### Device Model — Asset registry

The ARTS Device Model, developed and maintained by N (the Device module team), elevates devices from transaction attributes to first-class entities. This is a deliberate architectural departure from SMB-tier retail tools, where a register is typically a string field, not an entity with telemetry, version history, and status tracking.

| ARTS Device Model construct | Canary's column |
|---|---|
| Device.DeviceID | `sales.devices.square_device_id` (vendor-namespaced) |
| Device.SerialNumber | `devices.serial_number` |
| Device.DeviceName | `devices.device_name` |
| Device.OSVersion | `devices.os_version` |
| Device.ApplicationVersion | `devices.app_version` |
| Device.NetworkAddress | `devices.ip_address` |
| Device.NetworkConnection | `devices.network_connection_type`, `wifi_network_name`, `wifi_network_strength` |
| Device.PowerState | `devices.battery_percentage`, `charging_state` |
| Device.LocationID | `devices.location_id` (FK to Place registry) |
| Device.Manufacturer / Model | `raw_square_object` JSONB carries full vendor object |
| Device.Status | Derived from `db_status` + telemetry decay |

Device records live in the `sales` schema (alongside transactions) rather than `app` because they are ingested operational facts from a vendor, not configuration state owned by Canary. A JSONB safety-net column (`raw_square_object`) carries the complete vendor API response, ensuring no ARTS field is lost when the vendor adds fields Canary hasn't yet typed.

The Device Model is foundational to [[A-asset-management|A (Asset Management)]], which runs multivariate anomaly detection over the device registry to detect "this device is acting wrong" signals complementary to Q's transaction-level detection.

### Site Model — Locations (v2 ownership question)

The ARTS Site Model defines a physical location. At v1, Canary has not yet formally claimed Site Model adoption because no v1 module owns the mapping. The necessary site data exists in `app.merchant_locations` (location_id, address, timezone), but there is no dedicated Site Model documentation or mapped ARTS field catalog.

**Open positioning question:** When should Canary claim Site Model conformance? The model could be owned by:
- A future Places-registry module
- R (Customer) as part of a geo-attribution extension
- Q (Loss Prevention) as part of per-location alert routing

This is documented as a v2 decision point; for now, Site Model adoption is deferred pending module-ownership clarification.

## Where Canary deviates

Canary's relationship to ARTS is structural, not ceremonial. Three deviations are intentional and worth naming:

1. **POS-agnostic adapter layer.** ARTS POSLog is vendor-agnostic by design, but most implementations are written by a single POS vendor (Square, Shopify, etc.). Canary inverts this: POSLog is the canonical runtime schema, and Square is an adapter. When Shopify ships as the second adapter, this posture proves itself; until then, it's an architectural commitment, not a proven fact.

2. **External-identities for cross-vendor resolution.** ARTS Customer Model assumes one vendor = one customer namespace. Canary's `external_identities` table allows a customer to exist in multiple vendor namespaces and be linked at the platform level. This extends rather than contradicts the standard; it is where v2 customer identity lands.

3. **Privacy-first read-through pattern.** ARTS assumes customer demographic and contact data is stored and queried locally. Canary stores none of it, instead reading at query time when a workflow demands it. This is a conformance choice, not a non-conformance: every ARTS field is still answerable; the data residency is different.

## ARTS-native, not ARTS-veneer

The canonical commitment: **Every ARTS field that appears in Canary's runtime schema is answerable, even if some answers come from vendor passthrough rather than local storage.** This is the defining property that separates ARTS-native conformance from integration-layer translation.

A retailer using Canary should experience ARTS conformance transparently: querying a customer returns ARTS-shaped data; looking at a transaction sees POSLog structure; examining a device gets Device Model fields. The fact that some of those answers resolve to vendor APIs rather than Canary tables is an implementation detail, not a semantics gap.

## Open positioning question

How strict should the "ARTS-compliant" claim be at v1? Three possible stances:

1. **Conservative:** Claim only POSLog conformance (T shipping, fully tested). Defer Customer and Device claims until v1.x adds sync completeness.
2. **Balanced:** Claim POSLog + Customer + Device conformance, with transparent notes on v1 minimality (R's no-PII posture, N's gated sync scope). Be explicit about deferred Site Model.
3. **Aspirational:** Claim full four-standard adoption, framing minimality as architectural advantage (privacy, performance, simplicity).

The choice affects positioning, compliance claims in customer contracts, and certification pursuit (if ARTS ever formalizes certification). Currently leaning toward Balanced: ship the three modules with clear status notes, set Site Model ownership as a v2 decision gate.

## Related

- [[spine-13-prefix|13-prefix spine]] — module catalog and ownership assignments
- [[crdm|Canonical Retail Data Model]] — People × Places × Things × Events × Workflows framework
- [[T-transaction-pipeline|T (Transaction Pipeline)]] — POSLog source of truth
- [[R-customer|R (Customer)]] — Customer Model source of truth
- [[N-device|N (Device)]] — Device Model source of truth
- [[overview|Platform overview]]

## Sources

- [[T-transaction-pipeline|T — Transaction Pipeline]] — POSLog mapping (§ARTS mapping)
- [[R-customer|R — Customer]] — Customer Model mapping (§ARTS mapping)
- [[N-device|N — Device]] — Device Model mapping (§ARTS mapping)
- [[spine-13-prefix|13-prefix spine]] — module ownership and v2 positioning

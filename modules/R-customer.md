---
classification: confidential
owner: GrowDirect LLC
type: module-article
prefix: R
status: v1 (shipping, minimal)
sibling-modules: [T, N, A, Q]
---

# R — Customer

R owns the People entity in the [[../platform/crdm|CRDM]] frame, and
specifically the customer subset of People. It is the module retailers
ask about second (after the loss-prevention pitch) and the module that
positions Canary as more than a point solution: every customer
identifier on every transaction routes through R, every channel that
ever talks to a customer routes through R, and every downstream
projection that wants to answer "who is this person across our
business" reads R.

R is one of the [[../platform/spine-13-prefix#v1-differentiated-five-t-r-n-a-q|
Differentiated-Five]] modules at v1. It is the most architecturally
opinionated of the five: the v1 implementation is **deliberately
minimal** — no PII at rest, no stored profile beyond aggregate
metrics, only the vendor identifier and the things you can compute
from the transaction stream. This is a posture decision, not a
roadmap gap. Richer customer profiles are an opt-in extension, not a
default.

## Purpose

R owns three jobs:

1. **Curate the customer entity.** One row per customer per merchant,
   keyed by the upstream vendor's identifier (today: Square's
   `customer_id`). T writes transactions pointing at customers; R is
   the FK target.
2. **Compute derived customer state.** Lifetime value, transaction
   count, first-seen, last-seen — facts you can derive from the
   transaction ledger without storing anything the customer didn't
   already give the merchant's POS. R is the projection service for
   the customer side of the ledger.
3. **Provide the agent and analyst surface for customer questions.**
   "Who is this person?" "What have they bought?" "Are they a regular
   or a one-off?" — read-only MCP tools answer these without exposing
   the underlying schema.

R does **not** own:

- PII storage. Names, emails, phone numbers, addresses are
  intentionally not stored in R's tables. Square holds them; Canary
  reads at query time when the workflow demands it.
- Cross-channel identity resolution. A v2 ask. Today, one Square
  merchant = one customer namespace.
- Customer outreach (email, SMS, push). Adjacent to R's surface;
  out of scope for v1.

## BST cells R populates

R is the curator for People-side data. It is the primary owner of
some BSTs and the foreign-key provider for many more.

| Domain | BST | R's role |
|---|---|---|
| Customer Management | **Customer Profile Analysis** | Primary owner — R *is* the profile (minimal at v1) |
| Customer Management | **Customer Lifetime Value Analysis** | Primary owner — `lifetime_value_cents` is R's projection |
| Customer Management | **Customer Movement Dynamics** | Primary owner — `first_seen_at`, `last_seen_at` |
| Customer Management | Purchase Profiles | Feeder via FK — joined from T's transactions |
| Customer Management | Customer Loyalty | Feeder via repeat-purchase derivation |
| Customer Management | Customer Attrition Analysis | Feeder — derivable from `last_seen_at` decay |
| Customer Management | Customer Profitability | Partial — needs cost-of-goods (out of scope) |
| Customer Management | Customer Complaints Analysis | Not yet — needs refund-reason linkage |
| Customer Management | Cross Purchase Behavior | Feeder via T |
| Multi-Channel | Identified-shopper segmentation | Feeder via FK |

Customer-side BSTs not addressed at v1: Customer Credit Risk
(processor-handled), Customer Delinquency (processor-handled), Lead
Analysis (no pre-sale surface), Market Analysis (out of scope).

## CRDM entities touched

| CRDM entity | R's relationship | How |
|---|---|---|
| **People** | **Owns** the customer subset | One row in `customers` per merchant per Square customer |
| Events | Reads | Reads `transactions` to compute LTV, count, temporal bounds |
| Things | Reads | Joins through `transaction_line_items` for purchase-history queries |
| Places | Reads | Joins through `transactions.location_id` for geo-attribution |
| Workflows | Triggers | Q creates Cases pointing at customers as subjects of interest |

R's posture: **R is a People registry that derives projections from
T's Event stream.** R holds no facts that aren't computable from T.
This is what makes the privacy-first design work — there's nothing
to leak that wasn't already in T.

## ARTS mapping

R is the home of [[../platform/crdm#relationship-to-arts|ARTS Customer
Model]] adoption. The v1 implementation adopts the Customer Model's
identity layer and defers the demographic and contact layers.

| ARTS Customer Model construct | R's posture at v1 |
|---|---|
| CustomerID | `customers.square_customer_id` (vendor-namespaced) |
| Customer.LifetimeValue | `customers.lifetime_value_cents` (derived) |
| Customer.FirstTransactionDate | `customers.first_seen_at` |
| Customer.LastTransactionDate | `customers.last_seen_at` |
| Customer.TransactionCount | `customers.transaction_count` |
| Customer.Name / ContactInfo / Demographics | **Not stored.** Reads through to vendor at query time when workflow requires |
| Customer.LoyaltyAccount | Linked at FK; loyalty rows live in T's surface |
| Customer.Segment | Computed at projection time, not stored |

The promise: every ARTS Customer Model field is *answerable*. Some
are answered from R's tables; some are answered by reaching back to
the vendor's API. The retailer doesn't see the difference.

## Privacy posture

This is R's load-bearing design decision and deserves its own section.

R stores: vendor customer ID, derived aggregates, soft-delete state,
audit timestamps. **That's it.** No name, no email, no phone, no
address, no card data, no behavioral profile beyond integer counts.

This is enforced at the schema, not at the application layer:

- The `customers` table has no string columns for personal data
- The `card_profiles` table holds opaque tokenized fingerprints
  (Square's, never reversible to PAN), no card data of any kind
- PII that arrives in webhook payloads (loyalty enrollment phone
  numbers, etc.) is hashed at the parser layer in T before it ever
  reaches R

Consequences:

- **Breach scope is bounded.** A full database exfiltration of R
  yields vendor customer IDs and integer aggregates. Re-identification
  requires also breaching Square.
- **GDPR/CCPA compliance is structural, not procedural.** Right-to-be-
  forgotten is a single soft-delete on R + a vendor-side deletion
  request; there are no profile fields to scrub.
- **Cross-channel enrichment requires explicit opt-in.** A future
  retailer who wants Canary to store names/emails for first-party
  agent workflows turns it on per-merchant; the schema supports
  extension tables, the default is off.

The posture is a deliberate inversion of the dominant industry
default ("collect everything, decide later"). It is a marketable
property of the platform, not just a technical choice.

## Schema crosswalk

R writes to the `app` schema.

| Table | Owner | Pattern | Purpose |
|---|---|---|---|
| `customers` | R | mutable + soft-delete | Customer registry; one row per merchant per Square customer |
| `card_profiles` | R | mutable | Opaque tokenized card-fingerprint profiles for velocity checks |
| `external_identities` | R (extension) | mutable | Cross-database identity links (multi-merchant operators, future cross-vendor) |

R reads (no write):

| Table | Owner | Why R reads |
|---|---|---|
| `sales.transactions` | T | LTV / count / temporal bounds projection |
| `sales.transaction_line_items` | T | Purchase-history queries |
| `sales.refund_links` | T | Net LTV (refund-adjusted) |
| `sales.transaction_tenders` | T | Tender-mix analysis |

## Service-name markers (v0.7 microservice index)

| Service slot | Responsibility | Currently lives in |
|---|---|---|
| `r-registry` | Customer entity CRUD, soft-delete, FK target | `canary/models/app/customers.py` |
| `r-projection` | LTV / count / temporal computation | embedded in MCP tool implementations + chirp evaluator paths |
| `r-identity-mcp` | Read-only customer-query MCP surface | `canary/services/identity/` |
| `r-card-profile` | Opaque card-fingerprint registry | `canary/models/app/card_profiles.py` |
| `r-cross-vendor` | Multi-database / multi-vendor customer linking | `canary/models/app/external_identities.py` (scaffold; v2) |

**Perpetual-vs-period boundary.** Canary owns: unified customer identity + behavioral signals. Merchant tool owns: CRM/loyalty campaigns (Klaviyo, Mailchimp, etc.). Default implementation route: `integrated-hybrid`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (where customer data lands in R):

- T's parsed transaction stream — every new `customer_id` causes an
  upsert into R
- Square Customers API (during onboarding sync; enrichment of
  pre-existing Square customers)
- Square Loyalty webhooks — loyalty events surface customer IDs at
  enrollment

**Downstream consumers** (who reads R):

- **Q (Loss Prevention)** — chirp rules that depend on customer
  velocity (`C-005 CARD_VELOCITY` and similar) read R
- **Future P (Pricing & Promotion)** — promotion-engine targeting
- **Future C (Commercial)** — assortment-by-customer-segment
- **Agent surface** — investigator agents querying customer history
  via `canary-identity` MCP tools

## Agent surface

R exposes the `canary-identity` MCP server (read-only):

- Customer lookup by Square ID
- Customer lookup by card fingerprint
- Customer transaction history projection
- Customer LTV / count / temporal bounds query

There are no write-side MCP tools at v1 — agents cannot create or
mutate customer records. Customer creation happens automatically as a
side effect of T processing transactions.

## Security posture

- **Auth.** All R MCP tools require authenticated, tenant-scoped
  sessions. Row-level security on `customers.merchant_id` enforces
  cross-tenant isolation at the database layer.
- **Tenant scoping.** Every read is filtered by current_merchant_id
  via PostgreSQL RLS (`canary.current_merchant_id` session GUC).
- **PII handling.** As above — no PII at rest. Reads through to
  vendor when workflow requires.
- **Soft delete.** Customers go to `db_status = 'archived'` rather
  than DELETE. Preserves audit trail; a customer who comes back is
  re-activated, not duplicated.
- **External identities.** When the cross-DB linking surface is used
  (multi-merchant operators), the link table itself is also tenant-
  scoped and soft-deletable.

## Open questions

1. **Cross-vendor customer identity.** Today one Square merchant =
   one customer namespace. A retailer who runs Square in-store and
   Shopify online has two namespaces and no platform-level identity
   resolution. The `external_identities` scaffold is the planned
   home; the matching policy (deterministic? probabilistic? customer-
   confirmed?) is undecided.
2. **Profile-extension opt-in.** The privacy-first default is
   correct. The mechanism for retailers who want first-party PII
   storage (e.g., for first-party agent workflows or marketing) is
   not yet specified. Likely a per-merchant feature flag plus an
   extension table; needs a clear data-handling agreement.
3. **Customer Complaints linkage.** Refund reasons live in T and
   should populate Customer Complaints Analysis. R doesn't yet
   surface them. Small projection, currently missing.
4. **Customer-side anomaly detection.** Q has rules over customer
   velocity but no rule that fires on customer-profile drift
   (sudden change in geography, sudden activation after dormancy).
   Likely belongs in Q with R as the FK source.

## Roadmap status

- **v1 (shipping)** — Minimal customer registry. Privacy-first.
  Read-only MCP. Aggregate projections derived from T.
- **v2** — Cross-vendor identity resolution (with N's adapter
  expansion). Profile-extension opt-in. Customer Complaints
  projection.
- **v3+** — First-party CDP integrations. Demographic enrichment
  (opt-in). Customer-side anomaly detection rules.

## Related

- [[../platform/spine-13-prefix|13-prefix spine]]
- [[../platform/crdm|Canonical Retail Data Model]]
- [[../platform/overview|Platform overview]]
- [[T-transaction-pipeline]] — primary upstream source
- [[N-device]] — sibling Differentiated-Five module
- [[A-asset-management]] — sibling Differentiated-Five module
- [[Q-loss-prevention]] — primary downstream consumer

---
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-r, customer, identity, arts]
sources:
  - Canary-Retail-Brain/modules/R-customer.md
  - Canary/canary/models/app/customers.py
  - Canary/canary/services/identity/
  - Canary/docs/sdds/v2/identity.md
last-compiled: 2026-04-24
----

# Canary Module — R (Customer)

## Summary

R is Canary's customer registry — the People-side curation module on
the [[../projects/RetailSpine|Retail Spine]]. The v1 implementation
is deliberately minimal: vendor customer ID + derived aggregates +
soft-delete state. **No PII at rest.** Names, emails, phones, and
addresses live in Square; Canary reads through at query time when a
workflow demands it.

This wiki article is the Canary-specific crosswalk for R. The
canonical, vendor-neutral spec lives at
`Canary-Retail-Brain/modules/R-customer.md`.

## Code surface

| Concern | File | Notes |
|---|---|---|
| Customer model | `Canary/canary/models/app/customers.py` | `customers` table, `app` schema |
| Card profiles | `Canary/canary/models/app/card_profiles.py` | Opaque tokenized fingerprints, velocity checks |
| External identities | `Canary/canary/models/app/external_identities.py` | Cross-DB linking scaffold; v2 |
| Identity MCP server | `Canary/canary/services/identity/__init__.py` | Read-only, 6 tools |
| Identity MCP blueprint | `Canary/canary/blueprints/identity_mcp.py` | Route registration |
| Square OAuth (token side) | `Canary/canary/services/square_oauth.py` | Used for vendor read-through queries |

## Schema crosswalk

R writes to the `app` schema.

**Owns (write):**

| Table | Pattern | Purpose |
|---|---|---|
| `customers` | mutable + soft-delete | Customer registry (one row per merchant per Square customer) |
| `card_profiles` | mutable | Opaque tokenized card-fingerprint profiles |
| `external_identities` | mutable | Cross-DB identity links (scaffold; v2) |

**Reads (no write):**

| Table | Owner | Why |
|---|---|---|
| `sales.transactions` | T | LTV, count, temporal projection |
| `sales.transaction_line_items` | T | Purchase-history queries |
| `sales.refund_links` | T | Refund-adjusted LTV |
| `sales.transaction_tenders` | T | Tender-mix analysis |

## Customers table — column inventory

(All in `app.customers`, per `Canary/canary/models/app/customers.py`.)

| Column | Type | Notes |
|---|---|---|
| `id` | String(36) UUID | PK |
| `merchant_id` | String(36) | TenantMixin FK to `merchants.id` |
| `square_customer_id` | String(36) | UNIQUE per merchant; indexed |
| `lifetime_value_cents` | Integer | Derived projection; default 0 |
| `transaction_count` | Integer | Derived projection; default 0 |
| `first_seen_at` | DateTime | First transaction observed |
| `last_seen_at` | DateTime | Most recent transaction observed |
| `created_at`, `updated_at`, `created_by`, `modified_by` | AuditMixin | Standard |
| `db_status` | String(20) | SoftDeleteMixin (`active` / `archived`) |
| `db_effective_from`, `db_effective_to` | DateTime | Effective dating |

Notable absences (intentional): no `name`, no `email`, no `phone`, no
`address`, no `birthdate`, no `gender`, no `segment`. This is the
privacy-first posture, not a missing feature.

## SDD crosswalk

| SDD | Path | R's relationship |
|---|---|---|
| identity | `Canary/docs/sdds/v2/identity.md` | Primary spec — merchant registration, user auth, RBAC, OAuth |
| external-identities | `Canary/docs/sdds/v2/external-identities.md` | Cross-DB customer identity linking (v2 design) |
| data-model | `Canary/docs/sdds/v2/data-model.md` | App schema customer table definition |

## Where R fits on the spine

R is one of the [[../projects/RetailSpine|Retail Spine]] Differentiated-Five
modules. Per the [[../projects/RetailSpine#1-customer-management|Customer
Management § BST inventory]], R is the primary owner of:

- **Customer Profile Analysis** (R *is* the profile)
- **Customer Lifetime Value Analysis** (`lifetime_value_cents`)
- **Customer Movement Dynamics** (`first_seen_at`, `last_seen_at`)

R is the FK provider for many other Customer-Management BSTs (Purchase
Profiles, Customer Loyalty, Cross Purchase Behavior, etc.) — those
projections compute from T's tables joined through R's identity.

## MCP tool surface

`canary-identity` server is read-only at v1:

- Customer lookup by Square ID
- Customer lookup by card fingerprint
- Customer transaction history (projection from T)
- Customer LTV / count / temporal bounds query

No write tools — customer creation happens as a side effect of T
processing transactions.

## Open Canary-specific questions

1. **`external_identities` activation.** The scaffold exists; no
   merchant uses it yet. Cross-vendor identity resolution policy
   (deterministic / probabilistic / customer-confirmed) is undecided.
   Blocks the "POS-agnostic" claim from being end-to-end true at the
   customer layer.
2. **Profile-extension opt-in mechanism.** The privacy-first default
   is right; the per-merchant override path for retailers who want
   first-party PII storage is unspecified. Probably a feature flag +
   a `customer_profile_extensions` table; needs a data-handling
   agreement template.
3. **Customer Complaints projection.** Refund reasons live in T
   (`refund_links.reason`) and should populate Customer Complaints
   Analysis. R has no projection for this yet — small gap.
4. **No customer-side anomaly rule.** Q has card-velocity rules but
   no rule that fires on customer-profile drift (geographic shift,
   dormancy reactivation). Belongs in Q with R as the FK source.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-data-model|Canary Data Model]]
- [[canary-architecture|Canary Architecture]]
- [[canary-module-t-transactions|Canary Module — T (Transaction Pipeline)]]
- [[retail-integration-spine|Retail Integration Spine]]

## Sources

- `Canary-Retail-Brain/modules/R-customer.md` — canonical vendor-neutral spec
- `Canary/canary/models/app/customers.py` — Customer model
- `Canary/canary/models/app/card_profiles.py` — opaque card-fingerprint store
- `Canary/canary/models/app/external_identities.py` — cross-DB link scaffold
- `Canary/canary/services/identity/__init__.py` — identity MCP implementation
- `Canary/canary/blueprints/identity_mcp.py` — MCP route registration
- `Canary/docs/sdds/v2/identity.md` — primary SDD
- `Canary/docs/sdds/v2/external-identities.md` — cross-DB linking SDD

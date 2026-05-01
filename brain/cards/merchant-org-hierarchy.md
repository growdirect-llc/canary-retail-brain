---
card-type: org-layer
card-id: merchant-org-hierarchy
card-version: 1
domain: cross-cutting
layer: domain
feeds:
  - role-binding-model
  - module-q
  - module-l
  - module-e
  - module-f
receives: []
tags: [org, hierarchy, merchant, retailer, smb, roles, access-control]
status: approved
last-compiled: 2026-04-28
---

# Merchant Org Hierarchy

The retailer's internal org structure maps to seven operational layers. Every agent that reasons about users, access, data scope, or operational authority must understand which layer a principal occupies.

## Purpose

The hierarchy determines who can see what, who owns which decisions, and how escalation flows. It is not a static lookup — it is the frame through which every module-level permission, notification, and report makes sense. The CRDM agent owns the canonical layer definitions and the tables that back them.

## Structure

Seven operational layers, ordered from store floor to corporate top:

| Layer | Code | Owns | Typical Roles |
|-------|------|------|---------------|
| **Sales Floor** | `SALES_FLOOR` | Customer-facing ops, scanning, receiving handoff | Associate, Cashier |
| **Backroom** | `BACKROOM` | Stock management, receiving, shrink reconciliation | Receiver, Stock Lead |
| **Store** | `STORE` | Single-location P&L, scheduling, LP authority | Store Manager, ASM |
| **Head Office** | `HEAD_OFFICE` | Buying, merchandising, finance, HR, LP coordination | Director, VP |
| **Merchants** | `MERCHANTS` | Category/brand authority, range, promotion, OTB | Buyer, Category Manager |
| **Supply Chain** | `SUPPLY_CHAIN` | Distribution, forecasting, replenishment | DC Manager, Planner |
| **Org** | `ORG` | Legal entity top — multi-banner, holding, franchise parent | CEO, CFO, COO |

Two platform participants sit above the retailer and are not part of the merchant hierarchy:

| Tier | Code | Scope |
|------|------|-------|
| **VAR** | `VAR` | Multi-tenant operational scope — onboarding, channel delivery, support triage |
| **GrowDirect** | `PLATFORM` | PMO and domain authority only — no access to retailer operational data |

## Invariants

- Every user principal in the system binds to exactly one layer via the [[role-binding-model]].
- A principal at `STORE` layer cannot access sibling-store data — cross-store visibility requires `HEAD_OFFICE` or above.
- `VAR` and `PLATFORM` tiers are never mixed with retailer hierarchy nodes in role assignment.
- The CRDM agent is the schema authority for `org_layers`. Cross-module changes to layer definitions require CRDM sign-off and an SI cycle for affected modules.

## Consumers

| Consumer | Uses |
|----------|------|
| **Module Q (Loss Prevention)** | Escalation routing — incident alerts go up the hierarchy to the correct LP authority |
| **Module L (Labor)** | Scheduling scope — a Store manager sees their store, Head Office sees all stores |
| **Module E (Execution)** | Dispatch routing — work orders assigned by layer authority |
| **Module F (Finance)** | P&L scoping — Store layer gets single-location view, Org gets consolidated |
| **Identity & Auth** | RBAC enforcement — JWT claims carry layer code, enforced on every request |

## Related

- [[role-binding-model]] — how a principal is assigned to a layer and hierarchy node
- [[geography-hierarchy]] — the geography axis that Store nodes live within
- [[category-hierarchy]] — the category axis that Merchant nodes operate across

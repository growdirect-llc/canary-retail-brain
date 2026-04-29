---
card-type: field-hierarchy
card-id: geography-hierarchy
card-version: 1
domain: lp
layer: domain
feeds:
  - role-binding-model
  - module-q
  - signal-civil-services
  - local-market-agent
receives:
  - merchant-org-hierarchy
tags: [hierarchy, geography, lp, region, district, store, location, spatial]
status: approved
last-compiled: 2026-04-28
---

# Geography Hierarchy

The geography hierarchy is the spatial axis used by Loss Prevention, store operations, and local market intelligence. It organizes store nodes from continental region down to physical department zone.

## Purpose

LP alerting, civil services routing, shrink benchmarking, and local market agent assignment all operate on geography nodes — not category or legal entity relationships. A district manager sees all stores in their district. An LP alert escalates through the geography chain to the correct regional LP authority. Local market agents are instantiated at Region or District level depending on signal density.

## Structure

```
Region
  └─ District
       └─ Store
            └─ Department (physical zone)
```

| Node | Code | Scope |
|------|------|-------|
| **Region** | `GEO_REGION` | Multi-district geography — LP reporting unit, local market agent anchor |
| **District** | `GEO_DISTRICT` | Cluster of stores — district manager scope, civil services liaison zone |
| **Store** | `GEO_STORE` | Single retail location — primary operational unit |
| **Department** | `GEO_DEPT` | Physical zone within a store — shrink zone, planogram section |

The same `GEO_STORE` node also exists in the [[category-hierarchy]] as the point where category performance is measured at location. A store is simultaneously a geography node and a category performance node. The role binding model resolves which axis a given principal operates on.

## Invariants

- Every store has exactly one geography chain: Department → Store → District → Region.
- Geography nodes do not cross-reference category nodes. The axes are independent; the store node is the shared anchor.
- Civil services routing operates at `GEO_DISTRICT` level — never at Region or Dept. See [[signal-civil-services]].
- Local market agents are assigned to `GEO_REGION` or `GEO_DISTRICT` nodes. Never per-store — that would create too many agents for SMB scale.
- LP incident escalation follows the geography chain upward: Store → District → Region → Head Office (LP).

## Consumers

| Consumer | Uses |
|----------|------|
| **Module Q (Loss Prevention)** | Alert routing, shrink benchmarking by district, incident escalation path |
| **Local Market Agent** | Agent instantiated at GEO_REGION or GEO_DISTRICT — monitors all signal feeds for that geography |
| **Signal: Civil Services** | Liaison routing scoped to GEO_DISTRICT |
| **Signal: Weather + Zone SEO** | Weather zones map to GEO_DISTRICT or GEO_REGION |
| **Module J (Forecast)** | Regional demand curves inform replenishment planning |

## Related

- [[category-hierarchy]] — the other field hierarchy axis; store is the shared node
- [[role-binding-model]] — how principals are assigned to geography nodes
- [[local-market-agent]] — agent profile anchored to geography nodes
- [[signal-civil-services]] — routing uses GEO_DISTRICT as the liaison zone

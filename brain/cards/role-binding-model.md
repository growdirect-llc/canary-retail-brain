---
card-type: role-binding
card-id: role-binding-model
card-version: 1
domain: cross-cutting
layer: domain
feeds:
  - module-q
  - module-l
  - module-f
  - module-w
receives:
  - merchant-org-hierarchy
  - geography-hierarchy
  - category-hierarchy
tags: [rbac, roles, access-control, hierarchy, binding, identity, auth, permissions]
status: approved
last-compiled: 2026-04-28
---

# Role Binding Model

A role binding is the triple `(principal_id, hierarchy_type, hierarchy_node_id)` that assigns a principal to an authority scope. A single user can hold multiple bindings across different hierarchy axes simultaneously.

## Purpose

Traditional RBAC assigns a user to a role and a location. In a multi-dimensional retail platform, location is only one possible axis. A buyer operates on category nodes, not geography nodes. An LP analyst operates on geography nodes. A store manager operates on both — geography for operations, category for their local range decisions. The binding model resolves this without flattening the hierarchy or duplicating the permission logic.

## Structure

```
user_role(
  principal_id      UUID,        -- references users.id
  hierarchy_type    ENUM,        -- see types below
  hierarchy_node_id UUID,        -- references the node in the named hierarchy
  role              TEXT,        -- role code within this hierarchy type
  granted_at        TIMESTAMPTZ,
  granted_by        UUID         -- references users.id
)
```

**`hierarchy_type` values:**

| Type | Hierarchy | Node examples |
|------|-----------|---------------|
| `GEOGRAPHY` | [[geography-hierarchy]] | GEO_REGION, GEO_DISTRICT, GEO_STORE, GEO_DEPT |
| `CATEGORY` | [[category-hierarchy]] | CAT_DIVISION, CAT_DEPT, CAT_CATEGORY, CAT_SKU |
| `LEGAL_ENTITY` | [[merchant-org-hierarchy]] | ORG, HEAD_OFFICE, VAR, PLATFORM |

**Example bindings for common retail principals:**

| Principal | hierarchy_type | Node | Role |
|-----------|---------------|------|------|
| Store Manager | GEOGRAPHY | GEO_STORE (store-123) | `store_manager` |
| District LP | GEOGRAPHY | GEO_DISTRICT (dist-west) | `lp_district` |
| Buyer (Women's) | CATEGORY | CAT_DEPT (dept-womens) | `buyer` |
| Category Mgr | CATEGORY | CAT_CATEGORY (cat-denim) | `category_manager` |
| VAR Onboarding | LEGAL_ENTITY | VAR (var-rapidpos) | `var_admin` |

## Invariants

- A principal must have at least one binding to access the platform.
- Bindings are scoped downward — a binding at GEO_DISTRICT grants access to all GEO_STORE nodes beneath it. A binding at GEO_STORE does not grant sibling stores.
- Cross-axis bindings do not inherit. A GEOGRAPHY binding at GEO_STORE does not grant CATEGORY access to the SKUs sold in that store.
- `VAR` and `PLATFORM` bindings use `LEGAL_ENTITY` type with their own node. They are never granted GEOGRAPHY or CATEGORY bindings against retailer nodes.
- The Identity & Auth agent owns the `user_role` table and enforces binding validation at JWT issuance. Downstream modules receive the binding claims in the JWT and do not re-query the auth store.

## Consumers

| Consumer | Uses |
|----------|------|
| **Identity & Auth** | Owns the model, issues JWT claims from active bindings |
| **Module Q (LP)** | Checks GEOGRAPHY binding at GEO_DISTRICT or above for LP authority |
| **Module F (Finance)** | Scopes P&L reports to the deepest GEOGRAPHY or LEGAL_ENTITY binding |
| **Module L (Labor)** | Scheduling scope derived from GEOGRAPHY binding at GEO_STORE or GEO_DISTRICT |

## Related

- [[merchant-org-hierarchy]] — defines the LEGAL_ENTITY binding tier
- [[geography-hierarchy]] — defines the GEOGRAPHY binding axis
- [[category-hierarchy]] — defines the CATEGORY binding axis

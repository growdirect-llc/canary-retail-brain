---
tags: [retail, security, access-control, wiki]
project: retail
type: wiki
last-compiled: 2026-04-28
needs-review: 2026-05-12
---

# Retail System Security Controls

Enterprise retail management systems require layered security spanning database access, application-level controls, and organizational hierarchy. This card documents the canonical security model.

## Security Layers

| Layer | Controls |
|-------|---------|
| Database | User roles, table-level privileges (SELECT, INSERT, UPDATE, DELETE) |
| Application | Menu visibility, form controls, action buttons (new/edit/view/approve) |
| Organizational | User Group Hierarchy mapping roles to business structure |

Both database and application layers must be configured. Application security can be bypassed by direct database access (SQL, reporting tools); database-level restrictions close that gap.

## Role-Based Access Control (Database Layer)

### Design Process

1. Enumerate all user types and the tasks they perform (buyer, planner, store manager, auditor, developer, etc.)
2. Define roles corresponding to task clusters, not individuals
3. Assign table-level privileges per role — explicit INSERT/UPDATE/SELECT/DELETE grants per table
4. Assign roles to users — a user can hold multiple roles
5. Grant no more access than necessary to complete the role's tasks

### Example Role Privilege Pattern

| Role | Order Header | Stock Ledger | Item Master | User Admin |
|------|-------------|-------------|------------|-----------|
| Account Clerk | INSERT, UPDATE, SELECT | SELECT | SELECT | — |
| Account Supervisor | INSERT, UPDATE, DELETE, SELECT | SELECT, UPDATE | SELECT | — |
| Buyer | SELECT | SELECT | INSERT, UPDATE, SELECT | — |
| Developer (dev only) | All | All | All | SELECT |
| Security Admin | SELECT | SELECT | SELECT | All |

**Principle**: Roles should bundle all privileges needed for a task. Adding a new user = grant one role, not N individual table grants. Multiple roles can be assigned to a single user.

## Application-Level Security

Controls at the UI/form layer:

| Control Type | Mechanism |
|-------------|-----------|
| Menu items | Added or removed from navigation based on role assignment |
| Form action buttons (New, Edit, View, Delete, Approve) | Enabled/disabled by security program unit at each screen load |
| Search form list values | Drop-down options filtered by role |
| Hierarchy forms | Security program unit called on every action button event |

## User Group Hierarchy

Beyond individual roles, retail systems support an organizational security hierarchy:

| Hierarchy Type | Description | Example |
|----------------|-------------|---------|
| Supervision Hierarchy | Org reporting structure | GMM → DMM → Buyer → Assistant Buyer |
| Functional Hierarchy | Cross-departmental roles | Planner, Analyst, Admin |
| Parameter-Driven Groups | Aggregation by data attributes | Store group by region; Department group by buyer |

### User Group Hierarchy Capabilities

- **Language preference assignment** — per-user locale without separate user accounts
- **Advanced data-level security** — buyer sees only their department's items and POs; store manager sees only their store's inventory
- **Dynamic workflow routing** — exceptions routed to correct supervisor based on org hierarchy at time of event
- **Oracle role enhancement** — extends Oracle's native role model with retail-specific business structure

## Separation of Duties — Key Controls

| Function | Typical Separation |
|----------|-------------------|
| Order creation vs. order approval | Separate roles; supervisor role required for approval |
| Item setup vs. item activation | Different user groups |
| Price change creation vs. authorization | Workflow-controlled approval step |
| Receiving vs. invoice matching | Separate functional roles |
| User administration vs. operational access | Security Admin role isolated |

## Direct Database Access Restriction

Optional but recommended: restrict users from accessing the merchandise database through any path other than the retail application. Prevents direct SQL modification of item, pricing, and transaction tables outside business rules enforcement.

Common bypass risk: standard Oracle SQL*Plus, reporting tools (Business Objects, Crystal), or ETL tools with direct DB connections.

## Audit Trail

Audit trail is a core system administration function. All data changes in key tables (items, prices, purchase orders) tracked with:

| Field | Purpose |
|-------|---------|
| Operator ID | Who made the change |
| Timestamp | When |
| Change type | Insert / update / delete |
| Previous value | What changed from |

Audit trail data is required for financial audits, shrink investigations, and compliance reviews.

## Related Cards

- [[retail-module-decomposition]] — security module sits within Systems Administration of the merchandise management core
- [[retail-data-model-patterns]] — table structures that require security configuration

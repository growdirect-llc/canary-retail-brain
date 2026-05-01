---
card-type: domain-module
card-id: canary-employee
card-version: 1
domain: labor
layer: domain
feeds:
  - canary-owl
  - canary-fox
receives:
  - canary-identity
tags: [employee, master, roles, ej-spine, labor, hris-sync]
milestone: M4
status: approved
last-compiled: 2026-04-30
---

# Canary Service: employee

## What this is

Employee master records, role assignments, position bindings, and schedule references. The canonical record for who works for the merchant; roster data used by canary-fox (case subjects), canary-owl (EJ Spine attribution), and canary-chirp (employee-scoped detection rules).

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:8095` |
| Axis | B — Resource APIs |
| Tier mix | Reference (lookups, role catalog) · Change-feed (filtered list) · Stream (master CRUD, role changes) · Bulk window (HRIS roster import) |
| Owned tables | `app.employees`, `app.employee_roles`, `app.employee_locations`, `app.roles` |
| State machine | `ACTIVE → INACTIVE → TERMINATED` (TERMINATED triggers EJ Spine archival) |

## Purpose

Master record. Does **not** execute payroll or time-and-attendance — those are downstream merchant systems. Employee-Journey Spine querying is canary-owl's concern; this service owns the master record only. PII handling: email/phone require `employee:read-pii` JWT scope.

## Dependencies

- canary-identity (JWT, merchant scope)
- canary-owl (publishes employee status changes for EJ Spine)
- canary-fox (subject lookup on case open)

## Consumers

- canary-fox (case subjects)
- canary-owl (EJ Spine attribution)
- canary-chirp (employee-scoped detection rules)
- canary-store-brain (operator-presence lookup)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-employee
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]], [[tier-bulk-window]]

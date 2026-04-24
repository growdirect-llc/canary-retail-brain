---
classification: confidential
owner: GrowDirect LLC
type: data-model
---

# Canonical Retail Data Model (CRDM)

The CRDM is the canonical data model underlying every module in
Canary Retail. It is a five-entity frame that covers the full
operating surface of a retailer: People, Places, Things, Events,
Workflows. Every module reads and writes against this frame. Every
integration translates source data into this frame. The frame is
domain-agnostic enough that it also models non-commercial
entity shapes (e.g., a governed residential property), which makes
it a platform model, not a retail-only model.

## The five entities

### People

Customers, employees, vendors, investigators, tenants, members,
residents. Any human actor with a relationship to a Place, Thing,
Event, or Workflow. People have identifiers that may cross
channels (email, phone, loyalty number, employee ID, ARTS Customer
identity).

### Places

Stores, distribution centers, fulfillment points, residences,
properties, common areas. Physical or logical locations that things
live in, people work at or occupy, and events happen around. Places
are hierarchical (a store has departments; a property has parcels;
a DC has zones).

### Things

Items, SKUs, devices, fixtures, assets, vehicles, equipment. Any
tracked object. Things have identifiers that span systems (SKU,
UPC, serial number, ARTS Device identity, asset tag). Things are
bound to Places and handled by People.

### Events

Transactions, scans, alarms, inspections, deliveries, governance
actions, exceptions. Time-stamped things-that-happened. Every event
is hash-chainable and carries evidence. Events bind People, Places,
and Things to a moment.

### Workflows

Cases, orders, investigations, maintenance schedules, compliance
reviews, approval chains. Long-running stateful processes over the
other four entities. Workflows are how the system expresses
"something is in progress" and is what operational teams monitor.

## Why the five entities

This frame survives because every retail (and retail-adjacent)
operational question can be decomposed into combinations of the
five. Examples:

- "Which items are out of stock at this store?" → Things × Places
  × current-state projection.
- "Which employees handled this refund?" → People × Event (refund)
  × Workflow (audit).
- "Which devices are showing anomalies in this asset class?" →
  Things × Events × time-window.
- "Which cases have stalled in investigation?" → Workflow state ×
  time-since-last-event.

The model isn't retail-only. A residential property governance
platform (Places × People × Things × Events × Workflows, different
vocabulary) runs on the same frame. That cross-domain viability is
why GrowDirect's CRDM is a platform asset, not just a Canary Retail
schema.

## Relationship to ARTS

ARTS (Association for Retail Technology Standards) publishes retail
entity models that Canary Retail adopts:

- **ARTS Customer Model** → CRDM People (retail context).
- **ARTS Device Model** → CRDM Things (device subset).
- **ARTS Site Model** → CRDM Places (store subset).
- **POSLog** → CRDM Events (transaction subset).

ARTS provides validated entity structure for the retail use case.
The CRDM generalizes beyond retail while staying compatible with
ARTS.

## Module mapping

Every module in the 13-prefix spine reads and writes against CRDM
entities. Examples:

- **T (Transaction Pipeline)** — produces Events (POS transactions),
  binds them to People (customer, cashier), Places (location), and
  Things (items sold).
- **R (Customer)** — owns People entity curation.
- **N (Device)** — owns the device subset of Things.
- **A (Asset Management)** — detects anomalies in Events against
  Things and Places.
- **Q (Loss Prevention)** — evaluates Events against rules,
  produces Workflows (cases).

The same pattern generalizes across all v2 and v3 modules.

## Persistence and technology

- PostgreSQL 17 with pgvector. Multi-tenant via schema + row-level
  security.
- ARTS entities land as first-class tables with ARTS field names
  preserved for portability.
- Events are append-only. Workflows have append-only timelines.
- Hash-chained where compliance posture requires it.
- See [[../architecture/service-mesh]] for the full runtime
  architecture.

## Related

- [[overview]]
- [[spine-13-prefix]]
- [[arts-adoption]]
- [[../architecture/service-mesh]]
- [[../architecture/evidence-chain]]

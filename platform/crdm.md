---
classification: confidential
owner: GrowDirect LLC
type: data-model
---

# Canonical Retail Data Model (CRDM) — the ODS at the center

> **Governing rule.** **CRDM is the Operational Data Store. It sits in
> the middle of everything Canary builds and is the single source of
> truth.** Every module models against the CRDM schema, always. Every
> integration translates source data into the CRDM frame at the boundary.
> Every projection (perpetual movement layer, period-summary layer,
> agent-readable surface) is derived from CRDM. **Modules do not invent
> ad-hoc schemas; they read and write CRDM entities.** This is a hard
> architectural rule, not guidance.

## Why ODS, not EDW

The 2005-vintage enterprise reference architecture for retail BI assumes
a five-tier stack: Operational systems → ODS (operational data store) →
EDW (enterprise data warehouse) → marts → reports. That stack costs $5–$50M
to stand up and is the reason SMB retailers run on POS reports + Excel.

For SMB tier, **the ODS is the EDW** — three tiers, sometimes two. The
BST capabilities stay; the warehouse goes. CRDM is the ODS that
collapses the middle of that stack: real-time operational write surface
+ analytical read surface in one schema. Same answers as the enterprise
stack at ~1/100th the infrastructure.

This is what "Canary is the perpetual operational substrate behind the
merchant's existing tools" means in schema terms. The substrate is CRDM.

## The source-of-truth contract

What "CRDM is source of truth" means in practice:

1. **Every module's manifest declares its CRDM entity touchpoints.**
   The `entities` field in `<prefix>-<name>.manifest.yaml` lists which
   CRDM categories (People / Places / Things / Events / Workflows) the
   module reads and writes, and which specific tables under each.
2. **No module owns a private entity.** If a module needs an entity
   shape that does not exist in CRDM, the module's first work is
   extending the CRDM schema (with review) — not creating a parallel
   schema in the module's own namespace.
3. **Every projection is derivable from CRDM.** The EJ Spine, the
   Sales Audit scrubbed-and-aggregated output, every period-summary
   feed to a merchant tool, every agent answer — all derived from
   CRDM state. There is no "shadow" data anywhere that contradicts
   CRDM.
4. **Cross-vendor identity resolves through CRDM.** The
   `external_identities` table (Module R's responsibility) is a CRDM
   structure that maps source-system identifiers (Square customer ID,
   Shopify customer ID, etc.) to the canonical CRDM People row. The
   merchant has one CRDM customer; many vendor identities may resolve
   to it.
5. **Schema migrations go through CRDM review.** Adding a column,
   adding a table, changing a constraint — every database migration
   touches CRDM and so must be reviewed against the source-of-truth
   contract.

## The five entities

### People

Customers, employees, vendors, investigators, tenants, members,
residents. Any human actor with a relationship to a Place, Thing,
Event, or Workflow. People have identifiers that may cross
channels (email, phone, loyalty number, employee ID, ARTS Customer
identity).

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

## Where CRDM sits relative to the substrate primitives

CRDM is the **deepest** substrate primitive. The other substrate articles
describe how CRDM-aware modules behave:

- [[stock-ledger|Stock Ledger]] — the perpetual-movement projection of CRDM Events with conservation invariants
- [[retail-accounting-method|Retail Accounting Method]] — the value-method choices that read CRDM Things' cost basis
- [[satoshi-cost-accounting|Satoshi-Level Cost Accounting]] — the precision representation CRDM uses for unit cost
- [[satoshi-precision-operating-model|Satoshi-Precision Operating Model]] — the end-to-end precision commitment that decomposes every cost element to its originating CRDM Event
- [[perpetual-vs-period-boundary|Perpetual-vs-Period Boundary]] — the seam between CRDM-perpetual write and CRDM-period projection; both sides resolve through CRDM as source of truth

In Canary code, the EJ Spine and Sales Audit (see [[../../GrowDirect/Brain/wiki/canary-ej-spine-and-sales-audit|EJ Spine + Sales Audit anchor]]) are the named runtime instantiations of the perpetual write side and the period projection side. Both are CRDM-aware: EJ Spine writes CRDM Events; Sales Audit projects CRDM state.

## Related

- [[overview]]
- [[spine-13-prefix]]
- [[arts-adoption]]
- [[stock-ledger]]
- [[perpetual-vs-period-boundary]]
- [[satoshi-precision-operating-model]]
- [[module-manifest-schema]]
- [[../architecture/service-mesh]]
- [[../architecture/evidence-chain]]

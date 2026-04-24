---
classification: confidential
owner: GrowDirect LLC
type: platform-overview
---

# Canary Retail — Platform Overview

Canary Retail is a retail operating system for small and mid-sized
specialty retailers with online footprint. POS-agnostic by
architecture. ARTS-standards native. Multi-tenant SaaS. It is
deployed against a canonical retail data model and extended through
a module spine that covers the full retail operating surface.

## Who it's for

Specialty retailers from ~3 to ~300 stores, with an ecommerce or
direct-to-consumer channel, operating on a POS they didn't build
and probably can't replace this year. The segment that:

- Needs more than a POS but less than a full enterprise retail
  suite.
- Has real operational complexity (multi-channel, multi-location,
  inventory decisions, labor scheduling) and no central operational
  platform beneath it.
- Can't run a 12-month transformation engagement with a Big 4; can
  run a compressed version with GrowDirect.

Concrete vertical patterns: multi-store apparel, food & beverage
specialty, sporting goods, direct-selling / MLM channels with a
storefront presence.

## What it ships

Canary Retail is not a point solution. It is a platform with a
module catalog. The module spine has thirteen positions
(C/D/F/J/S/P/T/R/N/L/Q/W/A). At v1, Canary ships the
**Differentiated-Five** (T+R+N+A+Q) — the modules nobody else
productizes or productizes poorly:

- **T — Transaction Pipeline.** POS-agnostic ingestion (webhook-
  first), seal → parse → merkle → detect. Hash-chained evidence
  from intake onward.
- **R — Customer.** ARTS Customer Model. Unified customer entity
  across POS, ecommerce, and service channels.
- **N — Device.** ARTS Device Model. Every POS terminal, scanner,
  camera, and IoT device as a first-class tracked asset.
- **A — Asset Management.** Bubble — threat detection over the
  asset registry, per-store anomaly detection.
- **Q — Loss Prevention.** Detection engine + case management.
  Real-time rule evaluation against the transaction stream; cases
  with append-only evidence timelines.

Other modules ship on the v2 and v3 roadmaps (see
[[../roadmap/v2-crdm-expansion]] and [[../roadmap/v3-full-spine]]).

## What makes it different

1. **ARTS-standards native.** POSLog, Customer, Device, Site
   models adopted as the runtime schema — not an integration veneer.
2. **POS-agnostic by architecture.** Square is the first connector,
   not the core dependency. Canonical model is the source of truth;
   POS adapters are translation layers.
3. **CRDM abstraction.** People × Places × Things × Events ×
   Workflows. One model underlies every module. A retail store and
   an HOA parcel are architecturally the same entity — physical
   location + assets + people + governance + exceptions. The same
   CRDM supports both commercial and non-commercial expressions.
4. **Multi-tenant from v1.** No single-tenant fork. Multi-tenancy is
   a property of the schema and session, not a deployment toggle.
5. **Agent-native.** Every module has an agent mesh backing its
   tooling. Memory-bus-backed recall. Chirp+Fox generalizable to
   W (Work Execution) for any domain.
6. **Evidence-first.** Hash-chained from webhook intake through
   case timeline. Compliance posture is designed in, not added.

## Positioning against alternatives

- **Against a POS** — Canary Retail sits above the POS, not instead
  of it. A retailer keeps Square (or whatever they're on); Canary
  adds the operating tier on top.
- **Against an enterprise retail suite** — Canary Retail is sized
  for SMB specialty. It ships only what SMBs need. It doesn't ship
  an ERP, a WMS, or a dedicated merchandising tool — it provides
  the canonical model those categories plug into if the retailer
  needs them.
- **Against a point solution (just LP, just analytics, etc.)** —
  Canary Retail is a platform. A retailer adopting it starts with
  the Differentiated-Five and grows into the rest of the spine.

## Related

- [[spine-13-prefix]]
- [[crdm]]
- [[arts-adoption]]
- [[differentiated-five-add-on]]
- [[../architecture/service-mesh]]

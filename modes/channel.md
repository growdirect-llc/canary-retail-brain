---
title: Channel — Build on Top
classification: confidential
---

# Channel — Build on top

## What this is

A platform for VARs, integrators, and developers to build vertical extensions on. The architecture is the spine; specialized verticals — firearms compliance, regulated goods, hospitality, agricultural retail, regional grocery — extend it.

## Who it's for

- **Value-Added Resellers (VARs)** running their own retailer book — Counterpoint VARs, Lightspeed VARs, vertical specialists.
- **Consultancies** productizing repeatable engagement methodologies — diagnostic firms, transformation specialists, compliance practices.
- **Developers** building category-specific applications that need a verified retail data substrate — loss prevention specialists, vertical analytics builders, compliance reporting tools.

## What changes

You build on a platform whose accountability rails are already enforced. Your vertical extension inherits:

- The audit chain (every event hash-anchored)
- The Lightning settlement substrate (when enabled by the merchant)
- The agent topology (Operations / Business / Finance / Technical agents you can extend, not rewrite)
- The multi-POS adapter substrate (Square, Counterpoint, future POS platforms — adapters extend, not replace)
- The Canonical Retail Data Model (write your vertical extension against the same data model every other partner builds against)

You do not rebuild the integrity layer.

## What stays the same

Your relationships with your retailers. Your domain expertise. Your delivery model. Your commercial agreements with the merchants you serve.

## Starting move

The Apache 2.0 protocol layer is open. Start with a working integration on a non-production merchant. Reference the EDS (Enterprise Document Services) specifications and the multi-POS adapter substrate. A Contributor License Agreement is required before any external code touches the production platform.

## Integration patterns

| Pattern | Use case | What you implement |
|---|---|---|
| **POS adapter** | New POS platform integration | Adapter satisfying the substrate contract; events normalized to the canonical event schema |
| **Vertical agent** | Domain-specific intelligence (firearms compliance, OTC pharma, etc.) | Agent that subscribes to platform events; emits domain alerts and case candidates |
| **Channel adapter** | New ecommerce / marketplace integration | Adapter satisfying the ecom-channel contract; orders flow into the same RaaS event chain as POS transactions |
| **Reporting extension** | Industry-specific reporting (regulator filings, trade association benchmarks) | Read-only extension over the analytics schema |

## What you do NOT have to build

- The multi-tenant isolation model (schema-per-tenant, platform-managed)
- The receipt chain (RaaS service, platform-managed)
- The identity service (platform-managed; merchant federation handled by the platform)
- The encryption / cryptographic erasure pattern (platform-managed)
- The KPI rollup engine (analytics service, platform-managed)
- The agent runtime (orchestration platform-managed; you write agents, not infrastructure)

## Commercial structure (placeholder — under negotiation)

The channel commercial structure is under development. The intent: platform takes a metered cut of transactions or revenue running through the channel partner's extension; partner retains the relationship and direct revenue from their merchant. Specifics are negotiated per partner.

## Related

- [Operating system mode](operating-system) — the platform deployment your extension runs on
- [Modules](../modules/modules) — the 13-module spine your extension integrates with
- [Engineering](../engineering/nfrs) — the technical posture of the platform

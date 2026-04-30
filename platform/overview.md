---
classification: confidential
owner: GrowDirect LLC
type: platform-overview
nav_order: 1

---

# Platform overview

Canary is a retail operating system for private SMB and mid-market specialty retailers — typically $5M to $50M annual sales, multi-store but not enterprise — that don't have the budget or the staff for an enterprise stack but need the operational discipline that's been available to enterprise retailers for thirty years.

The platform is POS-agnostic: Square in V1, NCR Counterpoint as the primary commercial channel, additional POS platforms via the multi-POS adapter substrate.

## Architecture in one paragraph

Every retail event flows through a hash-anchored receipt chain. The chain is the source of truth — not the POS database, not the merchant's spreadsheet, not the buyer's memory. Every other system in the platform is a consumer of, or a contributor to, this chain. The chain is required core; everything else is extension.

## The platform articles

Each page below covers an architectural primitive or commitment that defines the platform. They read as peers — none is more important than the others.

### Architecture primitives

| Article | What it covers |
|---|---|
| [Architectural Continuity](platform-architectural-continuity) | The six properties — statelessness, federation, idempotency, content addressability, layered abstraction, cryptographic verification — that compose Canary's architecture. The continuity table from TCP/IP through SMTP / HTTP / Bitcoin to MCP shows the same primitives at every protocol scale. The novelty is composition for retail evidence, not new primitives. |
| [Stock Ledger](stock-ledger) | The perpetual-inventory movement ledger that every module communicates across. The integrity surface. |
| [CRDM — Canonical Retail Data Model](crdm) | The platform's POS-agnostic data model. People × Places × Things × Events × Workflows. ARTS-aligned. |
| [ARTS Adoption](arts-adoption) | POSLog, Customer, Device, Site standards alignment. The interop discipline that makes new POS connectors a normal weekly task instead of a quarter-long integration project. |
| [Differentiated-Five](differentiated-five-add-on) | T+R+N+A+Q — the V1 module set that distinguishes Canary on top of the retail baseline. |
| [Spine — 13-Module Prefix](spine-13-prefix) | The full module spine: C/D/F/J/S/P/T/R/N/L/Q/W/A. Module dependency graph and build order. |

### Accounting and financial substrate

| Article | What it covers |
|---|---|
| [Retail Accounting Method](retail-accounting-method) | RIM vs Cost Method. Open-To-Buy as the planning constraint. Integrated-hybrid as the default route for v2.F. |
| [Perpetual vs Period Boundary](perpetual-vs-period-boundary) | The staged migration story — Phase 1 parallel observer mode (zero adoption friction), Phase 2 module-by-module cutover at merchant pace, Phase 3 Canary as system of record. Every cutover reversible until Phase 3. |
| [Satoshi Cost Accounting](satoshi-cost-accounting) | Sub-cent unit cost as Canary's substrate primitive. Closes the 2002-vintage two-decimal precision gap that fiat-rounded WAC has carried for two decades. |
| [Satoshi Precision Operating Model](satoshi-precision-operating-model) | The top-down precision commitment — extends satoshi precision from COGS to Customer Acquisition Cost, SG&A, and IoT-tracked movement events. Every cost decomposed to its originating event with audit trail. Unifies the 13-module spine as instruments of cost decomposition. |

### Platform commitments

| Article | What it covers |
|---|---|
| [Stack Commitment](platform-stack-commitment) | GCP-native end to end. Single primary cloud. Eight specialist SaaS for plumbing. The discipline: anything not core IP or pure retail-domain logic gets bought, not built. |
| [Cryptographic Erasure](platform-cryptographic-erasure) | Per-subject DEK pattern. GDPR Article 17 erasure on append-only tables — the hash chain stays intact; the personal data becomes unreadable. Canonical answer for any system that combines integrity guarantees with privacy obligations. |
| [Module Manifest Schema](module-manifest-schema) | Machine-readable companion to module specs. Defines what a module manifest carries: ports, dependencies, data ownership, MCP tool surface, SLA commitments. |
| [Worked Example — Solex](worked-example-solex) | A working single-store retail implementation that exercises the platform's cart-and-checkout invariants, inventory model, and event flow. Solex is illustrative — it shows what the operational primitives look like in a working system. The platform generalizes those primitives to multi-channel, multi-location, multi-POS scale. |

## How to read this section

For an overview-first read: this page → [Architectural Continuity](platform-architectural-continuity) → [Stock Ledger](stock-ledger) → [CRDM](crdm).

For an accounting-first read: [Retail Accounting Method](retail-accounting-method) → [Perpetual vs Period Boundary](perpetual-vs-period-boundary) → [Satoshi Cost Accounting](satoshi-cost-accounting) → [Satoshi Precision Operating Model](satoshi-precision-operating-model).

For a worked-example-first read: [Worked Example — Solex](worked-example-solex) → [Stock Ledger](stock-ledger) → [Differentiated-Five](differentiated-five-add-on).

## Related

- [Why Canary](../why/why) — the why the architecture serves
- [Modules](../modules/modules) — the operational module library running on this architecture
- [Engineering posture](../engineering/nfrs) — NFRs, security, compliance
- [References](../references/references) — illustrative reference implementations and benchmarks

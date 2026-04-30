---
classification: confidential
owner: GrowDirect LLC
type: platform-overview
---

# Platform overview

Canary is a retail operating system for private SMB and mid-market specialty retailers — typically $5M to $50M annual sales, multi-store but not enterprise — that don't have the budget or the staff for an enterprise stack but need the operational discipline that's been available to enterprise retailers for thirty years.

The platform is POS-agnostic: Square in V1, NCR Counterpoint as the primary commercial channel, additional POS platforms via the multi-POS adapter substrate.

## Architecture in one paragraph

Every retail event flows through a hash-anchored receipt chain. The chain is the source of truth — not the POS database, not the merchant's spreadsheet, not the buyer's memory. Every other system in the platform is a consumer of, or a contributor to, this chain. The chain is required core; everything else is extension.

## The architectural primitives

### Receipt as a Service (RaaS) — the chain backbone

Every meaningful retail event becomes a receipt: a POS sale, a return, a void, a DC receiving confirmation, a three-way match, a vendor payment, a planogram change, an inventory adjustment. Each receipt is hashed (SHA-256 of canonical JSON), sequenced within the merchant's namespace, and chained — each event's hash includes the prior event's hash, making the chain tamper-evident.

The chain is the platform's evidentiary backbone. Every KPI, every audit, every dispute traces to it.

→ [Stock Ledger](stock-ledger) — the perpetual-inventory movement ledger that everything else cross-references

### Canonical Retail Data Model (CRDM) — the data substrate

The CRDM is the platform's POS-agnostic data model. It maps every supported POS's native data into a canonical shape that every downstream service operates on. A Square Payment, a Counterpoint document, and a Shopify order all become the same canonical event after the adapter normalizes them.

The CRDM is ARTS-aligned (Association for Retail Technology Standards) — POSLog, Customer, Device, Site standards — making interop with vendor-published schemas predictable.

→ [CRDM](crdm) — the canonical model in detail
→ [ARTS adoption](arts-adoption) — standards alignment

### Multi-POS adapter substrate — the integration seam

Every POS integration — current (Square, Counterpoint) and future — is implemented as an adapter that satisfies a contract: receive events from the source, normalize to the canonical schema, emit into the receipt chain. Downstream services never know which POS produced an event.

Adding a new POS does not require platform changes. It requires adapter code.

### Architectural continuity — the six properties

Canary's architecture is a composition of proven distributed-systems primitives applied to the retail evidence problem. Statelessness, idempotency, federation, content addressability, layered abstraction, and cryptographic verification — the same primitives that make TCP/IP, SMTP, HTTP, and Bitcoin scale.

We are not inventing new concepts at the protocol layer; we are composing old ones for a new use case. The novelty is in the composition and the application, not the underlying ideas.

→ [Architectural Continuity](platform-architectural-continuity) — the six properties and the continuity table

### Stack commitment — vendor posture

GCP-native end to end. Single primary cloud. Eight specialist SaaS for plumbing (Stripe, SendGrid, Twilio, Retool, Metabase, Sentry, Mintlify, OrdinalsBot). The discipline: anything not core IP or pure retail-domain logic gets bought, not built.

→ [Stack Commitment](platform-stack-commitment) — vendor commitment, why GCP, why not AWS

### Cryptographic erasure — privacy + integrity

Per-subject encryption keys for PII fields in append-only tables. To erase a customer's data under GDPR Article 17, the platform destroys their key. The ciphertext remains in the immutable table — but it is now unreadable. The chain integrity is intact; the personal data is gone.

This is the canonical answer for any system that combines integrity guarantees with privacy obligations.

→ [Cryptographic Erasure](platform-cryptographic-erasure) — the per-subject DEK pattern

### Worked example — Solex

A working single-store retail implementation that exercises the platform's cart-and-checkout invariants, inventory model, and event flow. Solex is illustrative — it shows what the operational primitives look like in a working system. The platform generalizes those primitives to multi-channel, multi-location, multi-POS scale.

→ [Worked Example — Solex](worked-example-solex)

## What lives in `deep/`

Deeper technical content — for engineers, architects, and partners doing detailed integration design. Not required for a CIO read.

| Topic | Pointer |
|---|---|
| The 13-letter spine and module dependency graph | [spine-13-prefix](deep/spine-13-prefix) |
| Differentiated Five — the V1 module set | [differentiated-five-add-on](deep/differentiated-five-add-on) |
| Phase migration from legacy POS to Canary as system of record | [perpetual-vs-period-boundary](deep/perpetual-vs-period-boundary) |
| Retail accounting method — RIM vs Cost, OTB as planning constraint | [retail-accounting-method](deep/retail-accounting-method) |
| Module manifest schema — machine-readable module descriptors | [deep/module-manifest-schema](deep/module-manifest-schema) |
| Satoshi cost accounting — sub-cent unit cost, optional Bitcoin standard | [deep/satoshi-cost-accounting](deep/satoshi-cost-accounting) |
| Satoshi precision operating model — full-stack Bitcoin standard, architectural direction | [deep/satoshi-precision-operating-model](deep/satoshi-precision-operating-model) |

## What's NOT here

This site does not document the platform's IP-sensitive details — the multi-tier assortment routing model, the ILDWAC five-dimension cost model, the L402 + Lightning settlement protocol, the keyed-PII-hashing standard, the data classification inventory. Those are protected, internal-only, and disclosed under specific commercial agreements with audited partners. This site documents the architecture a CIO needs to evaluate the platform for engagement; the deeper IP is available under NDA.

## Related

- [Why Canary](../why/why) — the why the architecture serves
- [Modules](../modules/modules) — the operational module library running on this architecture
- [Engineering posture](../engineering/nfrs) — NFRs, security, compliance

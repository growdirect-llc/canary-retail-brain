---
date: 2026-04-28
type: founder-intent
status: active
classification: confidential
tags: [raas, portable-store, data-sovereignty, positioning, founder-intent, main-street, l402, sha-256]
last-compiled: 2026-04-28
---

**Wiki:** [[Brain/Home|Home]] · [[Brain/wiki/cards/platform-thesis|Platform Thesis]]

# The Portable Store — Founder Intent

> **Scope.** This is a founder intent document. It records the vision that governs architecture decisions. It is not a sales claim, not a CATz article, not a merchant-facing document. The commercial expression of this vision is subject to the RaaS guardrail at [[Brain/wiki/canary-raas-positioning|Canary RaaS — Positioning Guardrail]] until audit clears.

---

## The Vision

Every other player in the retail technology stack uses data lock-in as retention. POS vendors, ERPs, franchise systems — your data lives in their system, in their format, on their terms. When you leave, you leave without it. The $15M specialty retailer on Main Street has never owned their operational record. It lives in the POS vendor's cloud, the franchisor's reporting system, the accountant's spreadsheet. They are tenants in other people's data structures.

The enterprise has always had this differently. Their IT teams extract, transform, and warehouse their own data independent of any vendor. They own their operational record. Main Street has never had that option.

**Canary ends that.**

The three accountability rails — operational, financial, evidentiary — are the retailer's. They travel with the business:

- **Jump providers.** Switch from Square to Counterpoint, Counterpoint to Lightspeed, whatever the next system is. The accountability record comes with you. LP history doesn't reset. OTB baseline doesn't disappear. The evidentiary trail is intact.
- **Jump locations.** Open a second store, a third, move across town, expand into a new market. The intelligence layer scales with the business, not with the lease.
- **Jump systems.** Migrate from Epicor to SAP, QuickBooks to Business Central. Canary's rails are the continuity layer that survives the migration. The before-state is documented and owned by the retailer, not the SI.
- **Jump networks.** Leave a franchise system, join a co-op, go independent. The operational history is not the franchisor's asset. It belongs to the operator who built it.

**Data sovereignty for Main Street.**

---

## The Closed Loop Economy

Three loops. Three rails. One closed system.

```
SHA-256 seals it  →  L402 authorizes it  →  Receipt records it  →  RaaS owns it
```

**SHA-256 wraps it in a bow.** Without it you have data — logs, entries, timestamps that can be edited, contested, explained away. SHA-256 seals every event into a chain: `event_hash` seals each transaction, `chain_hash` links each to the one before it, Merkle tree batches them into a root, that root goes to L1. The result is a mathematical fact. The record either matches the hash or it doesn't. There is no middle ground. No "the system was down." No "someone must have made a mistake."

**L402 closes the payment loop.** The agent cannot call the spend tool without settling the Lightning invoice first. The payment is the authorization. The receipt from L402 is the proof in both directions: the buyer authorized it because they paid it, the wallet enforced it because there was nothing left to overspend. You cannot say you authorized a budget you didn't fund — the Lightning receipt is the record.

**The receipt closes the cost loop.** Every receiving event recalculates ILWAC in Module V. Cost truth updates. The inventory record is current. The receipt is the atomic event that keeps the cost loop honest.

**RaaS ties all three loops to one portable identity.** The merchant moves. The loops travel with them.

| Loop | Mechanism | Rail | Guarantee |
|---|---|---|---|
| Cost | Receipt → ILWAC recalculate | Operational | No unknown inventory value |
| Payment | L402 → Lightning invoice settlement | Financial | No unauthorized spend |
| Evidentiary | SHA-256 → chain_hash → Merkle → L1 | Evidentiary | No unanchored record |
| Identity | RaaS namespace → portable across all POS | All three | No vendor lock-in |

Every commercial act in the closed loop economy is: **hashed, paid, receipted, and portable.** That is the platform.

---

## What RaaS Enables

This vision has a technical expression. It is RaaS — Resolution as a Service — the namespace layer that makes portability real.

The `raas:{merchant_id}` namespace is the portable identity token. It does not belong to Square, to Counterpoint, to any POS vendor. It belongs to the merchant. When a merchant switches POS, the underlying `merchant_source` connection changes — the namespace does not. Every domain in the spine (Chirp, Fox, Owl, V, M, T) addresses the merchant through this namespace. The intelligence is tied to the operator, not the tool.

The `.jeffe` identity layer (Bitcoin L1 inscription) is the permanent, cryptographically anchored expression of this: a merchant identity that no vendor can revoke, no POS migration can erase, no franchise exit can confiscate.

**ILWAC (Item-Location Weighted Average Cost)** is the cost truth that travels with the namespace. Every receipt event recalculates WAC in Module V. That recalculated cost is anchored to the merchant's namespace, not to any POS vendor's SKU mapping. The cost history is portable because the namespace is portable.

The receipt is the atomic event. RaaS is the layer that makes the receipt's meaning persist across every system the merchant will ever touch. Receipt as a Service — the closed loop where every commercial act produces a record the merchant owns.

---

## The Sentence

> *Your store. Your data. Wherever you go.*

The portable store. For Main Street.

---

## What This Is Not

- Not a sales claim today. The RaaS attestation layer is unaudited. The namespace portability is real and claimable; the cryptographic attestation narrative is not until SOC 2 Type 2 clears.
- Not a feature list. This is the governing intent — the reason architecture decisions get made the way they do. Tenant isolation is non-negotiable because of this. The API stays open because of this. The namespace is source-agnostic because of this.
- Not a marketing document. Commercial expression of this vision belongs in CATz, scoped to what is audited and deliverable. This document is the compass, not the brochure.

---

## Architecture Decisions This Governs

Any decision that would compromise data portability or impose vendor lock-in on the merchant's operational record is a violation of this intent. Specifically:

1. The `raas:{merchant_id}` namespace must remain source-agnostic — no POS-specific logic in the namespace key
2. The API surface must remain open — no forcing merchants to consume intelligence only through Canary's own UI
3. Fox case evidence must reference Canary UUIDs, not POS-vendor IDs — portable evidence survives POS migration
4. The evidentiary trail (Sub 1 hash chain, Merkle batch) must produce output the merchant can export and own independently of Canary's continued operation
5. Tenant isolation enforces data sovereignty in both directions — no franchisor sees franchisee data without explicit grant
6. SHA-256 is the cryptographic primitive — no substitution, no weakening, no optional hashing
7. L402 is the authorization mechanism for OTB-gated spend — the payment is the authorization, not a flag in a database

---

## Related

- [[Brain/wiki/canary-raas-positioning|Canary RaaS — Positioning Guardrail]] — what is and is not claimable today
- [[Brain/wiki/cards/platform-thesis|Platform Thesis — Every Entity Has a Meter]] — the governing accountability model
- [[Brain/wiki/canary-market-positioning|Canary Market Positioning — Competitive Landscape and Platform Motions]] — the four GTM motions this vision enables
- [[Brain/wiki/canary-franchise-play|Canary Franchise Play]] — data sovereignty as the franchisee association pitch
- `docs/sdds/canary/raas.md` — the technical implementation of namespace resolution
- `Canary/docs/sdds/v2/module-v.md` — ILWAC as the cost anchor that portability preserves
- `Canary/docs/sdds/v2/raas.md` — the RaaS SDD (Resolution as a Service)
- `docs/sdds/canary/goose.md` — L402 payment middleware implementation

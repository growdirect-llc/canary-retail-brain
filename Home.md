---
classification: confidential
owner: GrowDirect LLC
---

# Canary runs the loops. The merchant runs the store.

Canary is the retail operating system where agents run the operational machinery — receiving, replenishment, three-way match, inventory, sales audit, loss prevention, KPI surfacing — continuously. Merchants step in for three things only: strategic decisions, signing authority on financial deviations, and customer-facing work. Everything else closes itself.

## The bar

Three accountability rails. Every entity has a meter. The graph is closed.

- **Operational — no unknown loss.** Shrink stops being a black box. Every event that contributes to it is captured, classified, and traceable to a specific store, employee, vendor, or device. The shrink number becomes the sum of explained events instead of an unexplained line item at year-end.
- **Financial — no unauthorized spend.** Open-to-buy is a funded wallet, not a number in a spreadsheet. Commitments draw against the wallet at the moment of action; overspend is mathematically prevented, not policy-prohibited. Every dollar a merchant spends has a receipt the merchant owns.
- **Evidentiary — no unanchored record.** Every receipt, every case, every chargeback claim is hash-anchored. An auditor, an insurer, a lender, or a court can verify the chain without trusting the merchant — or trusting Canary.

## What the merchant gets back

> *Run the store again.*

Walk the floor. Talk to customers. Make the strategic calls — what to carry, what to cut, what to invest in for the season. Sign on the financial decisions that matter. The platform handles the operational load that used to consume the day.

This is what the four-beat outcome describes:

1. **Stays on track** — accountability without overhead. Plans are wallets the agents respect; variance surfaces before quarter-close, not after.
2. **Meets customers where they're going** — local market intelligence at the geography of the store, in real time.
3. **Operates above weight class** — agent network carries the analytical and operational work that would otherwise need a department.
4. **Gets back to running the store** — the merchant becomes a merchant again, not the operator of operational machinery.

## Where to go from here

| Section | Read this if you want to know |
|---|---|
| [Why](why/why) | Why the platform exists, the three rails, the meter model |
| [How to engage](modes/modes) | The five engagement modes — operating system, transformation, audit, channel, internal — and which one fits |
| [Experience](experience/experience) | What it looks like in your role: merchant, store manager, LP investigator, vendor, auditor |
| [Modules](modules/modules) | The 13-module spine that runs the operational loops |
| [Platform](platform/overview) | The architecture: Canonical Retail Data Model, Receipt as a Service, agent topology, Bitcoin standard substrate |
| [Engineering](engineering/nfrs) | NFRs, scale, security, compliance posture for the IT partner |
| [Proof](proof/proof) | Worked examples, benchmarks, dogfooding posture |

## What this is not

This is not a marketing site for a product that doesn't exist yet. It is the working surface of the platform we are building, in production, in public, with verifiable receipts. Some sections describe architectural direction (clearly marked); most describe what runs today.

This is not a comprehensive replacement for SAP or Oracle Retail. It is the platform a $5M to $50M private retailer can run on without an enterprise IT department, an enterprise consulting engagement, or an enterprise budget — and that scales when they grow.

This is not a Bitcoin retail product. The platform uses cryptographic primitives (SHA-256 chain anchoring, optionally Lightning settlement and Bitcoin L2 evidence anchoring) where they earn their place — not for ideology. Every Bitcoin / Lightning feature is opt-in. The platform operates correctly with all of them disabled.

---

*The platform is GCP-native, Go-implemented, multi-tenant by design, SOC 2 / ISO 27001 day-one architecture. See [Engineering](engineering/nfrs) for the technical posture.*

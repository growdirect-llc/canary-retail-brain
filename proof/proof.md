---
title: Proof
classification: confidential
---

# Proof

## The governing principle

Working code in production is the proof. Everything else is preparation. Academic framing, research papers, architectural documentation, and competitive analysis are useful — but none of it substitutes for a receipt that actually gets hashed, a return policy that actually gets enforced by a contract, and a namespace that actually resolves across a POS switchover.

Credibility follows code. Not the other way around.

## Three proof arguments

### 1. Structural — the cost of the alternative

The alternative to hash-verified document services is the status quo: each party in a retail transaction (retailer, vendor, lender, auditor, insurer) maintains their own copy of the PO, the ASN, the invoice, and the receipt, and reconciles them manually at settlement.

The cost of that reconciliation is measurable and benchmarked: AP headcount, invoice exception rate, chargeback dispute cycle time, audit engagement fees, return fraud losses.

Canary's Enterprise Document Services architecture eliminates these costs by making the documents themselves the source of truth rather than each party's local assertion. The structural argument does not require proof of a new technology — it requires proof that the reconciliation cost drops to near-zero when the three-way match is a contract verification rather than a human process.

That is a direct ROI argument with line items.

### 2. Mechanism — independent verification

The hash chain is not a proprietary claim. It is the same mathematical structure as git commits and Bitcoin blocks. Any party that holds a copy of any hash in the chain can verify independently — without trusting the platform, without trusting the merchant, without calling a support team.

The proof is delivered by shipping `verify_chain(merchant_id, from_seq, to_seq)` as a public MCP endpoint and letting counterparties call it. The claim is not "trust us, it's verified." The claim is "here is the tool, run it yourself."

That is what distinguishes Canary from SaaS: SaaS requires the counterparty to trust the vendor's assertion. Canary requires the counterparty to run a function.

### 3. Competitive — incumbents cannot follow

SAP, Oracle Retail, and Blue Yonder are database-of-record vendors. Making their records immutable would break every one of their existing integrations and eliminate the consulting revenue that depends on manual reconciliation workflows.

They cannot adopt this architecture without destroying the business model built on top of the legacy architecture. Canary can offer hash-verified document services precisely because it is building from scratch. The competitive moat is not "we got there first." It is "the architecture they would need to compete is structurally incompatible with their existing business."

---

## PwC Best Practices benchmarks (1997–1999)

The PwC Finance Best Practices research from a 1997–1999 retail engagement (PetSmart / Marks & Spencer era) is the evidentiary foundation for the platform's financial automation thesis. These are not theoretical targets — they are documented best practices from real Fortune 500 implementations. Canary doesn't aspire to these benchmarks. It makes them irrelevant by replacing the processes that generated them.

| AP metric | PwC best practice | Canary delivery |
|---|---|---|
| Total cost of A/P per $1,000 revenue | $1.43 | Approaches $0 — three-way match smart contract replaces human AP review |
| Invoices per A/P FTE | 30,000 | Irrelevant — no A/P FTE required for matched vendors |
| Average personnel cost per invoice | $2.22 | $0 for smart-contract-cleared invoices |
| % invoices auto-matched | 57% (best practice) | 100% target for enrolled vendors |
| % electronic payments | 71% | 100% — Lightning when enabled, ACH otherwise |
| % transactions error-free | 99% | Hash-verified match: clears or doesn't |
| Cycle time to schedule payment | 3 days | Immediate on smart contract clearance |
| % invoices via EDI | 80% (target) | 100% — every event is structured at intake |

The PwC observation that grounds this: *"The new A/P process begins when receiving personnel enter into the system the quantity received at the dock. The system then matches the receipt to a line item on a purchase order, retrieves the unit price, and generates a voucher."*

That is the three-way match smart contract, described in 1998. Canary enforces it by design.

A Fortune 500 automotive manufacturer achieved 70% AP headcount reduction implementing this model manually. Canary implements it as a smart contract. The headcount argument is structural.

## Buyerless buying

A large U.S. electronics manufacturer ran 60% of requisitions as "buyerless buying" — buyers intervene only for exceptions. The PwC benchmark for that manufacturer:

- Order cycle including confirmation: down to 5 minutes (was 20 days)
- Average processing time: from 20 days to 4 days
- On-time deliveries: from 21% (within 14 days) to 65% (within 5 days)
- Supplier count: from 30,000 to 20,000

Canary's commercial agent model is the buyerless buying pattern at SMB scale: agents commit POs within OTB and contracted vendor terms; buyers handle exceptions, not the standard flow.

These are process improvements from the 1990s. They are available today to any retailer with integrated PO, ASN, and invoice infrastructure. The SMB retailer has historically been excluded because the integration cost was enterprise-scale. Canary changes that.

---

## Worked example — Solex

[Worked Example — Solex](../platform/worked-example-solex) describes a single-store retail implementation that exercises the platform's cart-and-checkout invariants, inventory model, and event flow. Solex is illustrative — it shows what the operational primitives look like in a working system. The platform generalizes those primitives to multi-channel, multi-location, multi-POS scale.

## Internal reference — GrowDirect on Canary

GrowDirect runs on Canary. The platform's first customer is its own builder. Every architectural claim made on this site is testable against the running internal posture. See [Internal mode](../modes/internal) for the always-on reference.

---

## What the prototype must demonstrate to close the proof

The shortest verifiable proof is three things running end-to-end:

1. **A POS transaction that produces a receipt event with a SHA-256 hash, a sequence number, and a reference to the prior event hash** — demonstrating the hash chain mechanics.
2. **A return presented against that receipt hash, evaluated by the return policy smart contract** — demonstrating that the chain is not just stored but enforced.
3. **A `verify_chain` call from an external party (simulated vendor or auditor) that confirms the hash exists in the chain and returns its sequence position** — demonstrating independent verification without trusting the platform.

Those three demonstrations against a real merchant's transaction types constitute the minimum viable proof. Everything else follows.

## Related

- [Why Canary](../why/why) — the framework these proofs validate
- [PwC benchmarks (deep)](../platform/deep/pwc-benchmarks) — the underlying research
- [Worked example — Solex](../platform/worked-example-solex) — illustrative single-store implementation
- [Internal mode](../modes/internal) — always-on dogfooding reference

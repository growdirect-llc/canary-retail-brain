---
card-type: platform-thesis
card-id: platform-l402-ildwac-moat
card-version: 1
domain: platform
layer: cross-cutting
status: approved
tags: [l402, ildwac, lightning, bitcoin, satoshi, agent-billing, cost-attribution, moat, patent, defensibility, agent-pmo, micropayments]
last-compiled: 2026-04-29
---

## What this is

The composition of L402 (HTTP 402 + macaroons + Lightning Network) and ILDWAC (five-dimension provenance-weighted cost model in satoshis) creates a uniquely defensible billing-and-cost-attribution layer for agent-driven retail. Every cost-affecting agent action becomes a cryptographically-receipted event with five dimensions of provenance, denominated in satoshis, anchored to the hash chain, and verifiable on Bitcoin L2. No competitor can replicate the composition without rebuilding our chain primitive, securing equivalent patent coverage, and capturing five dimensions of attribution upstream of cost calculation. Each is a multi-year project; together they are a moat measured in years, not features.

## Purpose

The agent-driven retail platform creates a new category of operational question: when an LLM agent acts on the merchant's behalf, who paid for it, what did it cost, and what's the provable receipt? Conventional billing systems answer per-transaction or per-subscription, which collapses agent-call granularity into invoice-level summaries. Conventional cost accounting answers per-item-per-period, which collapses event-level provenance into trial-balance entries. Neither is granular enough for an agent network making thousands of decisions per day, each affecting cost and inventory.

L402 + ILDWAC is the composition that makes agent-driven economic action defensible. Every action is paid for at the moment of execution, in micropayments that reflect the actual cost of the action, with cryptographic proof of payment bound to the cost record. The merchant gets agent-driven operation with provable spending controls.

## L402 — protocol composition

L402 (Lightning Service Authentication Tokens) was invented by Lightning Labs ~2020. It composes three primitives that existed for decades but had never been combined for paid HTTP:

| Primitive | Origin | Role in L402 |
|---|---|---|
| HTTP 402 "Payment Required" | RFC 2068 (1996) — reserved, never standardized | The status code that signals "pay before you read" |
| Macaroons | Google Research (2014) | Delegated authentication tokens with caveats; the credential issued after payment |
| Lightning Network | Lightning whitepaper + LND (2018) | Sub-cent micropayments, settlement in seconds |

The flow:

```
1. Client GET /tool/expensive-thing
2. Server 402 + WWW-Authenticate: L402 macaroon="...", invoice="lnbc..."
3. Client pays Lightning invoice
4. Client GET /tool/expensive-thing with Authorization: L402 <macaroon>:<preimage>
5. Server verifies preimage matches invoice payment hash, returns the resource
```

Why this works for our architecture:

- **No account required.** Agent calls don't need merchant account overhead per call; the macaroon IS the credential.
- **Sub-cent micropayments.** A single MCP tool call can cost 50 satoshis — economically rational at agent-call granularity.
- **Macaroon caveats.** Time-bounded ("expires in 1 hour"), amount-bounded ("good for 1000 sats of API"), action-bounded ("only authorizes inventory reads") — third-party attenuation works without the issuer being involved.
- **Composable with REST.** Drops cleanly into our existing Chi/Cloud Run stack as middleware. No new transport.
- **Settlement is the receipt.** The Lightning preimage IS the cryptographic proof of payment — no separate billing reconciliation.

## ILDWAC — five-dimension cost model

ILDWAC = Item × Location × Device × MCP × Port × Weighted Average Cost. Five dimensions of provenance attached to every cost figure, denominated in satoshis, anchored to the hash chain.

| Dimension | Question it answers | Why it matters |
|---|---|---|
| **Item** | What SKU? | Standard. Every cost system has this. |
| **Location** | Which store / warehouse? | Standard for multi-store retailers. |
| **Device** | Which scanner / terminal / scale captured the event? | Lets you separate cost effects of a miscalibrated scale from the items it weighed. |
| **MCP** | Which agent tool call authorized the cost-affecting action? | Agent attribution. "What did the inventory agent's reorder decisions cost us this quarter?" |
| **Port** | Which POS source surfaced the event? (Square / Counterpoint / Shopify) | Source attribution. Cost differences across POS sources surface integration drift. |

The first two dimensions exist in every conventional retail ERP. The last three are new. Together they attach cryptographically-verifiable provenance to every cost figure.

Per-event WAC recalculation (packet-level, not period-end batch). RIB (Receipt-In-Batch) settlement layer ties to chain anchoring. Patent #63/991,596 covers the algorithm.

## The composition flow

Every cost-affecting agent action becomes a single chain of receipts:

```
1. Agent identifies need (e.g., "merchant should buy 50 more units of SKU-1234")
2. Agent calls MCP tool: cmd/receiving.create_purchase_order
3. The tool call is L402-gated — agent pays X satoshis via Lightning
4. The L402 receipt (preimage) is bound to the action via macaroon
5. The action writes an ILDWAC cost packet:
   - Item: SKU-1234
   - Location: Store 042
   - Device: (none — agent-initiated, no physical device)
   - MCP: receiving.create_purchase_order
   - Port: counterpoint
   - Cost: X satoshis (the L402 payment) + Y satoshis (the inventory cost at recalculated WAC)
   - L402 receipt hash: <preimage>
6. ILDWAC chain anchors the cost packet
7. RIB batch eventually inscribes the chain root to Bitcoin L2
```

What this enables:

**Provable agent accountability.** Every cost-affecting action has a cryptographic receipt. The merchant can audit the agent's spending in satoshis with proof that the action was authorized and what it cost.

**Cross-merchant cost benchmarks in satoshis.** ILDWAC industry benchmarks anonymize the merchant but preserve the cost dimension. "Average cost-of-goods drift in supplements category, satoshi-denominated, across merchants on the platform" is a network-effect data product. Network effects compound as the platform onboards more merchants — each new merchant strengthens the benchmarks for every existing merchant.

**Agent-driven capital allocation that doesn't require human approval.** L402 + ILDWAC means an agent can spend on the merchant's behalf within macaroon-bounded limits without escalating every transaction. The merchant sets the macaroon caveats; the agent operates within them. This is the operational unlock for agent-driven retail.

**The chain anchor turns cost data into an asset.** A merchant can take their ILDWAC chain to a lender or insurer and prove operational efficiency without revealing transaction-level data. The hash chain is the audit; the L402 receipts are the proof; the satoshi denomination is currency-neutral.

## Why this is defensible

A competitor would need all four of the following simultaneously:

1. **Chain primitive** — the hash chain + Merkle inscription patent. Years of engineering, plus patent clearance.
2. **L402 integration** — Lightning node operation, macaroon issuance, HTTP middleware. A few months for an experienced team. Not a moat alone, but a prerequisite.
3. **Five-dimension capture upstream of cost** — most architectures don't carry device + agent + source attribution into the cost calculation. Re-architecting an existing platform to capture it is a year-plus project.
4. **Satoshi denomination as the unit of account** — most platforms denominate in fiat currency, which drifts over time and complicates cross-time comparison. Switching denomination is a cost-model rewrite.

Individually, any of these is achievable. The combination is what's hard. The patent covers the algorithm that ties them together. The composition is the moat.

## Operating the moat — what makes it real

The architectural moat is theoretical until we have a working endpoint. Three concrete operations convert the moat from spec to demonstration:

**1. One L402-gated tool call on Lightning testnet.** Pick any cost-affecting MCP tool. Wire L402 middleware. Generate one paid call end-to-end. The first paid call is the proof case.

**2. One ILDWAC packet generated from that call.** Five dimensions populated, satoshi-denominated cost, L402 receipt hash bound. Written to the chain.

**3. One chain root anchored to Bitcoin L2.** Public verification URL where anyone can check the proof. The marketing artifact follows automatically — "anyone can verify our receipts on Bitcoin."

After these three operations, the moat narrative is grounded in working software. Before them, it's a patent application and three SDDs.

## Invariants

- Every L402 receipt is bound to an ILDWAC packet. A payment without a corresponding cost packet is a billing-only transaction (legal but architecturally incomplete).
- Every ILDWAC packet carries the L402 receipt hash. A cost packet without payment provenance is missing a dimension and is an architectural failure.
- The five dimensions are non-negotiable. Reducing to four (e.g., dropping MCP attribution) collapses agent accountability; reducing to three (dropping Port) collapses multi-POS attribution. The full composition is the IP.
- Satoshi is the unit of account at the chain layer. Fiat presentation in dashboards is a UI conversion, not the canonical record.
- The chain anchor is non-blocking. If Bitcoin L2 is unavailable, ILDWAC packets queue locally and are anchored asynchronously. The merchant store is never blocked by anchor unavailability.

## Sources

- L402 protocol specification (Lightning Labs)
- Macaroons paper — Birgisson, Politz, Erlingsson, Taly, Vrable, Lentczner (Google Research, 2014)
- Lightning Network whitepaper — Poon, Dryja (2016)
- Patent application #63/991,596
- `docs/sdds/go-handoff/l402-otb.md` — L402 wallet and OTB enforcement
- `docs/sdds/go-handoff/ildwac.md` — five-dimension cost model
- `docs/sdds/go-handoff/raas.md` — chain anchor for ILDWAC packets
- `docs/sdds/go-handoff/blockchain-anchor.md` — Bitcoin L2 inscription

## Related

- [[platform-architectural-continuity]] — the conceptual frame; L402 + ILDWAC is composition of proven primitives at the agent-billing layer
- [[platform-stack-commitment]] — Bitcoin L2 anchor via OrdinalsBot is the substrate; L402 + ILDWAC is the framework
- [[raas-receipt-as-a-service]] — the chain backbone
- [[infra-l402-otb-settlement]] — the operational settlement layer
- [[infra-blockchain-evidence-anchor]] — the on-chain anchor
- [[platform-cryptographic-erasure]] — per-subject erasure that preserves chain integrity

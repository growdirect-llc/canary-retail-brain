---
card-type: domain-module
card-id: canary-blockchain-anchor
card-version: 1
domain: lp
layer: domain
feeds: []
receives:
  - canary-identity
  - canary-fox
  - canary-raas
tags: [blockchain-anchor, bitcoin-l2, hash-anchoring, merkle-batch, evidence, patent-protected, court-admissible]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: blockchain-anchor

## What this is

External-verifiability layer for Canary's evidentiary rail. **Patent-protected (#63/991,596).** Batches event hashes from canary-fox (evidence chain) and canary-raas (chain anchors), commits Merkle roots to a Bitcoin L2, and serves verification proofs to partners and regulators on demand.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9086` |
| Axis | B — Resource APIs |
| Tier mix | Bulk window (batched commits — the canonical pattern) · Reference (proof verification, status) · Stream (rare — pending pool inspection) |
| Owned tables | `app.anchor_batches`, `app.anchor_pending_hashes`, `app.anchor_commits`, `app.anchor_l2_credentials` |
| Tier mapping rule | **Per-event L2 commits are cost-prohibitive. Batched hourly or daily commits are the canonical pattern. Do not change this tier mapping — it is enforced by the economics of L2 settlement.** |
| Commit lifecycle | `PENDING → READY → COMMITTING → CONFIRMED → ARCHIVED` |

## Purpose

Tamper-evident timestamped proof that a Canary record existed in a specific state at a specific time — non-repudiable by any party including GrowDirect. Hashes batched across all merchants for cost amortization; proofs are merchant-scoped (a merchant verifies only proofs for hashes their services emitted).

## Patent-protected behavior

The merkle-batching strategy and L2 selection economics are patent-protected. External docs cover the proof-verification contract; internal SDDs cover the batching algorithm.

## Dependencies

- canary-identity, canary-fox (evidence-chain hashes)
- canary-raas (chain-anchor hashes)
- Bitcoin L2 RPC (Liquid / RSK / Stacks / other)

## Consumers

- Legal-compliance reviewers (proof verification)
- Regulators / auditors
- canary-fox (proof URLs on case attestation)
- canary-ildwac (snapshot hash anchoring at period close)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-blockchain-anchor
- Card: [[infra-blockchain-evidence-anchor]] (concept-level capability card)
- Cards: [[tier-bulk-window]], [[tier-reference]]

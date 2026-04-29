---
card-type: infra-capability
card-id: infra-blockchain-evidence-anchor
card-version: 1
domain: lp
layer: infra
feeds:
  - fox-case-management
  - legal-compliance-agent
receives:
  - module-q
  - fox-case-management
tags: [blockchain, evidence, lp, compliance, hash-chain, audit-trail, l2, pci, gdpr, court-admissible]
status: approved
last-compiled: 2026-04-28
---

# Infra: Blockchain Evidence Anchor

The blockchain evidence anchor is a Legal & Compliance infrastructure capability that publishes cryptographic hashes of Fox case card generations to a public L2 blockchain. It produces tamper-evident, timestamped proof that a case record existed in a specific state at a specific time — non-repudiable by any party including GrowDirect.

## Purpose

Fox's INSERT-only hash-chain provides strong internal evidence integrity. But an internal chain, however disciplined, is controlled by the platform operator — a determined adversary could theoretically replace the whole chain. Anchoring hashes to a public blockchain removes that attack surface entirely. The chain of custody becomes mathematically provable to any third party: a court, an insurer, a regulatory auditor, or a retail enterprise buyer's legal team.

The economics are viable at SMB scale. Anchoring hashes (not data) at Fox case event frequency costs sub-cent per transaction on Base, Polygon, or Arbitrum. A high-volume SMB retailer generating 500 case events per month pays under $5/month in gas. This is not a scaling problem.

## What Gets Anchored

Only hashes are anchored — never case content, PII, or operational data.

| Event | Hash Input | Anchor Trigger |
|-------|-----------|----------------|
| **Card generation** | `SHA-256(card_body + frontmatter + generated_at)` | On every `hawk_cards` INSERT |
| **Case status transition** | `SHA-256(case_id + old_status + new_status + occurred_at)` | On every `hawk_timeline` status_change event |
| **Evidence chain close** | `SHA-256(fox_case_id + final_hash_chain_value + closed_at)` | On Fox case closure linked to Hawk |

The blockchain transaction stores: the hash, the `case_id` (not case content), the event type, and the platform-signed timestamp. That's it. No PII. No investigation detail. No SKU data.

## Chain Architecture

```
Fox Case Event (card generation, status change, closure)
  → Legal & Compliance Agent (hash computation + anchor decision)
    → L2 Blockchain Transaction (hash + case_id + event_type + timestamp)
      → Transaction receipt stored in hawk_timeline
        (event_type: 'evidence_anchored', event_data: {tx_hash, block_number, chain_id})
```

The transaction receipt written back to `hawk_timeline` closes the loop — the platform has proof of the anchor, and the blockchain has the hash. Both are independently verifiable.

## Network Selection

Preferred: **Base** (Coinbase L2) or **Polygon PoS**. Selection criteria:
- Sub-cent transaction cost at current gas prices
- EVM-compatible (standard tooling, no custom SDK)
- Sufficient decentralization to be credible as a neutral third party in litigation
- Long-term availability commitment appropriate for evidence retention periods

The Legal & Compliance agent holds the platform signing key used for anchor transactions. Key management follows the Security infrastructure agent's rotation and custody protocols.

## Use Cases

| Use Case | Beneficiary |
|----------|------------|
| **LP court proceedings** | Case evidence is timestamped and non-repudiable — stronger than internal logs for criminal prosecution support |
| **Insurance claims** | Anchored timeline proves the sequence of events for property/theft insurance claims without requiring the insurer to trust GrowDirect's internal records |
| **PCI DSS audit** | Demonstrates continuous, tamper-evident audit trail enforcement without manual attestation |
| **GDPR right-to-delete** | Anchor proves when data was deleted (or anonymized) — the hash of the deletion event is permanent even after the data is gone |
| **Enterprise buyer due diligence** | A blockchain-verifiable evidence chain is a material differentiator in enterprise retail procurement; procurement and legal teams recognize it without explanation |

## Invariants

- The anchor writes a hash only. It never reads or writes case content to the blockchain.
- The Legal & Compliance agent is the sole authority for anchor transaction submission. No other agent submits blockchain transactions.
- Anchor failures are non-blocking. If the L2 is congested or unavailable, the case event proceeds normally and the anchor is queued for retry. Case operations do not wait on blockchain confirmation.
- Anchor receipts (tx_hash, block_number) are stored in `hawk_timeline` as append-only events. They are never modified.
- The platform signing key is rotated per the Security agent's key management schedule. Old keys are retained for receipt verification; only the current key signs new anchors.

## Related

- [[signal-civil-services]] — court-admissible evidence chain is the downstream beneficiary of anchored LP cases
- [[local-market-agent]] — ORC and flash mob cases that reach civil services are the highest-value anchor targets

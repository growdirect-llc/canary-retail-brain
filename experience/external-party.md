---
title: The External Party — Auditor, Regulator, Lender, Insurer
classification: confidential
nav_order: 6

---

# The external party

Auditor. Regulator. Lender. Insurer. Court. Anyone with a verifiable interest in the merchant's records who needs to confirm what happened, when, and to whom.

## Your interest

Verifiable claims. Where the merchant says X happened, you need to confirm X happened — without taking the merchant's word, and without subpoenaing the platform's database.

## What changes

You don't have to take the merchant's word. The receipt chain is mathematically verifiable. Call `verify_chain(merchant_id, from_seq, to_seq)` and confirm the sequence is intact. Call `case_status(case_id)` and read the evidence chain timestamped on a public ledger (when the merchant has enabled blockchain anchoring).

| Verification need | What you do |
|---|---|
| Confirm a transaction occurred | `receipt_hash(transaction_id)` returns the hash; verify against the chain |
| Confirm a sequence is intact | `verify_chain(merchant_id, from_seq, to_seq)` returns the first broken link, if any |
| Confirm an LP case timeline | `case_status(case_id)` returns the timeline; each event hash is verifiable |
| Confirm the merchant's KPI claim | The KPI rollups derive from the same audited event log; verify by sampling events from the chain |
| Confirm a vendor chargeback's basis | The chargeback record references the originating receipt event; both are hash-anchored |
| Confirm cryptographic erasure under GDPR | Post-erasure ciphertext rows are present; decryption fails; chain integrity holds |

## What stays the same

Your standard. Your scrutiny. Your judgment.

The platform does not lower the bar for verification. It lowers the cost of verification. What used to require a forensic engagement, a subpoena, and weeks of reconciliation now requires a function call and the public chain.

## Why this is different

Conventional retail audit requires trusting the merchant's records. The merchant says they had this inventory at this date; the auditor takes that at face value (or imposes counts and reconciliations to verify). The merchant says this LP case happened in this sequence; the auditor reads the binder the merchant assembled.

The Canary chain doesn't ask for trust — it provides math. Insurance claims, regulatory inquiries, financing due diligence, court testimony — the same verification function applies. The merchant doesn't have to convince you; they hand you the verifier.

## What use cases this addresses

| Use case | Beneficiary |
|---|---|
| **Court proceedings** | Case evidence is timestamped and non-repudiable — stronger than internal logs for criminal prosecution support |
| **Insurance claims** | Anchored timeline proves the sequence of events for property/theft insurance claims without requiring the insurer to trust the merchant's internal records |
| **PCI DSS audit** | Demonstrates continuous, tamper-evident audit trail enforcement without manual attestation |
| **GDPR right-to-delete verification** | Post-erasure verification: ciphertext present, decryption fails, chain integrity holds — the platform proves erasure |
| **Lender due diligence** | KPIs (inventory turn, gross margin, comp sales) are derived from the audited event log; the lender can verify a claim by sampling events from the chain |
| **Enterprise buyer evaluation** | A blockchain-verifiable evidence chain is a material differentiator in enterprise retail procurement; procurement and legal teams recognize it without explanation |
| **Tax authority audit** | Disposal events, capex write-offs, depreciation timing — substantiated against the chain rather than the merchant's general ledger alone |

## How to access

External-party access is granted by the merchant via their identity service. The merchant issues a scoped token (read-only, time-bounded, sequence-range-bounded) for the verification engagement. You call the same MCP surface the merchant uses, scoped to your token. Your access is logged in the merchant's audit schema; the merchant has a complete record of what you queried, when, and what you saw.

For public-chain verification (no merchant cooperation required), the inscription IDs are published — anyone can verify the chain root against the public L2 without any platform-side authentication.

## What this enables

A category of verification that has not existed in retail before. Counterparties to the merchant — vendors, lenders, insurers, regulators, courts — operate against a verifiable substrate rather than trusting (or distrusting) the merchant's database. The merchant benefits because their claims become defensible; the counterparties benefit because their verification cost drops.

## Related

- [Why Canary](../why/why) — the evidentiary rail that produces this verification surface
- [Modules](../modules/modules) — RaaS, the chain backbone you verify against
- [Engineering](../engineering/nfrs) — the technical posture, including SOC 2 / ISO 27001 day-one design

---
title: GrowDirect on Canary — Internal Reference
classification: confidential
nav_order: 3

---

# GrowDirect on Canary — internal reference

The platform's first customer is its own builder. Canary's architecture works because we run on it.

## The posture

GrowDirect operates on Canary in production, in public, with verifiable receipts. Every architectural claim made elsewhere on this site is testable against the running internal posture. The chain we describe in [Platform overview](../platform/overview) exists at `verify_chain(growdirect)`. The KPI dashboard we ship to merchants is the dashboard we read every morning.

This is not a marketing assertion. It is a structural commitment.

## What's running

| Capability | Internal use |
|---|---|
| Multi-POS adapter substrate | Square as our POS connector for platform sales |
| Receipt chain (RaaS) | Every internal transaction hashes and sequences into the same chain merchants use |
| Multi-tier assortment routing substrate | Powers our vault publishing pipeline (CRB, CATz, NCR vaults) |
| OTB wallet model | Funds the platform's own operational spend |
| Loss prevention detection (where applicable) | Anomaly detection on our own transaction stream |
| Field capture pipeline | Internal team uses field capture for documentation and incident notes |
| Hash chain integrity | Our own audit log lives on the same chain primitive |
| Memory bus (pgvector) | Powers our internal context surfaces |
| Agent topology | Operations Agent, Business Agent, Finance Agent operate over our own data |

## Why this matters

A platform the builder won't run on is a platform that probably shouldn't ship. Canary's internal posture is the simplest, hardest test of the architecture — every claim made on this site is testable against the running system at GrowDirect. We hand the verifier to the reader.

For a CIO evaluating the platform, the question "does this actually work?" has a structural answer: it works because the people building it operate on it.

## What's not in this reference

We do not publish detailed operational metrics from our internal use as performance claims. Our own KPIs are not benchmarks for what merchants will achieve — they are validation that the architecture runs.

We do not claim our internal posture proves customer-facing outcomes. That comes as merchant engagements mature and the merchants sign off on attributable reference content.

What we do claim: every architectural primitive on this site has internal evidence. The receipt chain runs. The multi-tier assortment routing publishes content. The agent topology executes. The cryptographic primitives operate. None of this is theoretical from our side.

## The verifier

Anyone evaluating the platform can call:

- `verify_chain(growdirect, from_seq, to_seq)` — confirm GrowDirect's chain integrity
- `case_status(case_id)` (under appropriate scope) — read a case timeline against the chain
- Public chain inscriptions (when blockchain anchoring is enabled) — verify the chain root against a public L2

The platform is designed to make verification a function call, not a sales conversation. The internal posture is where that starts.

## Related

- [Why Canary](../why/why) — the architecture this internal posture validates
- [Internal mode](../modes/internal) — the always-on dogfooding posture
- [Proof](../proof/proof) — broader proof argument

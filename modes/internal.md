---
title: Internal — Our Own Shop
classification: confidential
---

# Internal — Our own shop

## What this is

GrowDirect runs on Canary. The platform's first customer is its own builder — in production, in public, with verifiable receipts.

This is reference, not a separate engagement. CIOs, partners, and investors evaluating the platform see what running on it actually looks like — because we're doing it ourselves, every day.

## Who it's for

This page is for everyone evaluating the platform. The internal-mode posture is structural — it does not require an engagement, a SOW, or a sales cycle. It is the always-on demonstration that the architecture works because we run on it.

## What this proves

| Claim | Internal evidence |
|---|---|
| The platform handles real merchant operations | We process our own platform sales (Square as our POS) through the same TSP pipeline merchants use |
| The OTB wallet enforces spend constraints | Our platform spend (Lightning when enabled, internal ledger otherwise) runs against the same OTB model |
| The receipt chain is verifiable | The chain we describe in `architecture.md` exists at `verify_chain(growdirect)` — anyone can call it |
| The KPI dashboard is real | The dashboard we ship to merchants is the dashboard we read every morning |
| The agent topology runs in production | Our Operations Agent, Business Agent, and Finance Agent execute the platform's operational work — same agent code path merchants run |
| Multi-tier assortment routing works | Our vault publishing pipeline (CRB, CATz, NCR) uses the multi-tier routing substrate to push curated content to public surfaces |

## What this does NOT do

This is reference, not a marketing surface. We do not publish detailed operational metrics from our internal use as performance claims. The internal posture serves verification — *the architecture works because the builder operates on it* — not benchmarks.

## What stays the same

Our work. Our customers. Our discipline. The dogfooding doesn't replace the build; it validates it.

## Starting move

None. This is always-on.

The internal page maintains the live reference, refreshed continuously. New CIO / partner / investor reviews can verify any architectural claim in `platform/` or `modules/` against the internal posture before scheduling a deeper conversation.

## Why this matters

A platform that the builder won't run on is a platform that probably shouldn't ship. Canary's internal posture is the simplest, hardest test of the architecture — every claim made on this site is testable against the running system at GrowDirect. We hand the verifier to the reader.

## Related

- [Why Canary](../why/why) — the architecture the internal posture validates
- [Proof](../proof/proof) — the broader proof argument that internal-mode evidence supports
- [Engineering](../engineering/nfrs) — the technical posture being demonstrated

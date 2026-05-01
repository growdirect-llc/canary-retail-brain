---
card-type: infra-capability
card-id: infra-l402-otb-settlement
card-version: 1
domain: merchandising
layer: infra
feeds:
  - module-m
  - module-p
  - module-o
  - module-f
receives:
  - module-m
  - cpa-agent
tags: [l402, lightning, otb, open-to-buy, micropayment, accountability, mcp, spend-control]
status: draft
last-compiled: 2026-04-28
---

# Infra: L402 OTB Settlement

L402 OTB Settlement gates commercial spend commitments behind Lightning Network micropayments via the L402 protocol on MCP tool calls. The OTB allocation is a funded Lightning wallet. An agent commits spend by calling a gated MCP tool — the payment is the authorization. If the wallet is empty, the tool call fails. The spend record is a settled Lightning payment: cryptographic, timestamped, non-repudiable by either party.

## Purpose

OTB as a database field is a permission. OTB as a Lightning wallet is a constraint. The distinction matters because permissions can be overridden, reinterpreted, or explained away after the fact. A failed Lightning payment cannot. This closes the gap between approved budgets and actual spend accountability — in both directions. Management cannot claim it authorized a budget it failed to fund. An agent cannot claim it stayed within OTB if its payments show otherwise.

## Status

**Draft — full technical spec pending.** See [[platform-thesis]] for the accountability model this serves. The L402 standard for MCP tool monetization is still maturing; this card will be updated when the integration contract is fully specified.

## Scope

- OTB wallet funding: how Head Office allocates OTB to CAT_DEPT wallets
- L402 gate on commercial MCP tools: which tool calls require payment
- Payment failure handling: what happens when a buy commitment fails at payment
- Receipt storage: where Lightning payment receipts are recorded (hawk_timeline or equivalent append-only log)
- Module F reconciliation: how Lightning receipts feed the financial P&L
- CPA agent monitoring: cost-per-action tracking for OTB spend velocity

## Related

- [[platform-thesis]] — the accountability model this serves
- [[category-hierarchy]] — OTB wallets are funded at CAT_DEPT level
- [[infra-blockchain-evidence-anchor]] — the evidence rail; L402 is the financial rail

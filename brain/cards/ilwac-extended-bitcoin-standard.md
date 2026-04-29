---
date: 2026-04-28
type: founder-intent
status: active
classification: confidential
tags: [ilwac, bitcoin-standard, satoshi, rib, mcp, provenance, cost-accounting, founder-intent, canary]
last-compiled: 2026-04-28
---

**Wiki:** [[Brain/Home|Home]] · [[Brain/wiki/cards/platform-thesis|Platform Thesis]] · [[Brain/wiki/cards/portable-store-founder-intent|Portable Store — Founder Intent]]

# IL(Device/MCP/Port/)WAC — Extended Cost Model on a Bitcoin Standard

> **Scope.** Founder intent and architectural direction. Not a sales claim. Not yet implemented. Captures the design decision before it evaporates. No downstream code or SDD should declare a hard dependency on this until a formal design pass produces a GRO ticket.

---

## The Claim

No one has this.

Retail cost accounting has always been fiat-denominated, device-agnostic, and channel-blind. A unit cost is a number in dollars, attached to an item and a location, updated when a PO is received. That is ILWAC as the industry knows it.

This is not that.

---

## The Bitcoin Standard

**Canary retail is on a Bitcoin standard. Everything else is an abstraction.**

Satoshi is the native monetary denominator at the system level. Fiat prices — the dollar amounts on receipts, on purchase orders, on the OTB budget — are the display layer. The accounting layer runs in satoshis.

This is not cosmetic. It has structural consequences:

- L402 Lightning payments are already denominated in satoshis. The payment loop and the cost loop close in the same unit. No currency conversion at the system level. No exchange rate embedded in the cost model.
- OTB wallets are funded in satoshis. The constraint is a Lightning wallet balance, not a number in a database. Overspending is not a policy violation — it is a payment failure. Mathematically impossible, not merely prohibited.
- COGS postings to Module F run in satoshis. Fiat equivalents are computed at the presentation layer using the exchange rate at the time of the event — the same way Bitcoin-standard accounting works in every other domain that has adopted it.
- The cost loop (receipt → ILWAC recalculate) and the payment loop (L402 → Lightning settlement) are now denominated in the same unit. The closed loop economy is internally consistent at the monetary level.

The enterprise retail world runs on fiat with all the currency risk, conversion complexity, and accounting abstraction that implies. Canary runs on satoshis. Fiat is the abstraction.

---

## The RIB Extension

**RIB = Retail Inventory Batch.** The Retek/Oracle RMS concept: inventory adjustment events are not processed individually at the time they occur — they are batched, validated, and posted as structured messages to the stock ledger in domain-organized runs.

The extension: **batched JSON RIB messages, organized by domain, rolled up into the extended WAC calculation.**

Instead of individual events firing ILWAC recalculates in real time, each domain (T, V, M, D, and others in the spine) produces structured RIB messages — JSON batches of inventory adjustment events scoped to that domain. Those batches are the inputs to the WAC recalculation.

The domain organization matters. A receiving event from Module M (Merchandising) carries different provenance than a transfer adjustment from Module D (Distribution) or a sale event from Module T (Transaction). The RIB message carries its domain origin. The WAC calculation knows where the adjustment came from.

SHA-256 seals each batch. The batch is tamper-evident before it touches the cost model.

---

## IL(Device/MCP/Port/)WAC

Standard ILWAC: **Item × Location × Weighted Average Cost.**

Extended: **Item × Location × Device × MCP × Port × Weighted Average Cost.**

| Dimension | What it captures |
|---|---|
| **Item** | The SKU — unchanged from standard ILWAC |
| **Location** | The store or warehouse — unchanged from standard ILWAC |
| **Device** | The terminal, mobile device, or hardware that processed the originating event |
| **MCP** | The MCP tool call that authorized the action — which agent, which server, which tool |
| **Port** | The POS connector — Square, Counterpoint, Lightspeed, or any future source |
| **WAC** | Weighted average cost — recalculated on every RIB batch, denominated in satoshis |

This is **provenance-weighted cost.** The cost carries its own audit trail — not appended as metadata, but embedded as dimensions in the calculation itself. The WAC for an item at a location is not one number. It is a vector: one value per (Device, MCP, Port) combination that has contributed to the cost basis.

**Why this matters:**

- A receiving event processed through the Counterpoint connector on a fixed POS terminal authorized by the `register_source` MCP tool produces a different provenance signature than the same event processed through the Square connector on a mobile device authorized by a different tool. The cost model tracks both — and the difference is auditable.
- When a Fox case investigation needs to trace a cost anomaly, the provenance dimensions tell the investigator not just what the cost was, but how it was established, by which channel, through which agent action.
- SHA-256 seals the RIB batch that produced the WAC update. The cost is not just a number — it is a hashed, domain-attributed, provenance-stamped value anchored to the event that created it.

---

## The Full Stack

```
Event occurs (sale, receipt, transfer, adjustment)
  → Domain RIB batch assembled (JSON, domain-tagged)
  → SHA-256 seals the batch
  → IL(Device/MCP/Port/)WAC recalculates in satoshis
  → L402 gates any spend authorized by the new cost basis
  → RaaS namespace owns the updated cost record
  → Merchant takes the cost history with them when they leave
```

Every step is hashed. Every authorization is paid. Every cost is receipted. Every record is portable.

---

## Cost Center Cross-Charge — Immediate Settlement

Each endpoint dimension — Device, MCP tool call, Port/connector — carries a fee denominated in satoshis. When a cost center uses an endpoint, the L402 payment settles immediately. No invoice batch. No period-end cost allocation. The payment is the authorization; the authorization is the charge; the charge flows directly into that cost center's dimension on the WAC.

This is structurally different from every existing cost allocation system: cross-charges are not a separate accounting layer applied after the fact. They are embedded in the event at the moment it happens.

| Endpoint dimension | Fee mechanism | Settlement |
|---|---|---|
| Device | Per-call or per-transaction terminal fee | L402 → cost center wallet, immediate |
| MCP | Per-agent-action compute cost | L402 → cost center wallet, immediate |
| Port | Per-event connector license cost | L402 → cost center wallet, immediate |

**The cost center is an L402 wallet.** Balance is the real-time P&L position. No period close required for internal cross-charges.

**Endpoint fee = internal transfer pricing.** Want to model a department's true cost of shared infrastructure? Price the endpoint. Want to incentivize adoption? Price it low for the first 90 days. The fee schedule is the pricing policy.

**Franchisor application:** A franchisor mandating Canary sets the endpoint fee schedule as a brand standard. Franchisee associations control the schedule on behalf of members. Individual units pay per use. The power spectrum that determines who holds the mandate also determines who sets the price.

---

## IT Project Self-Funding — The ROI Problem Solved

The persistent failure of retail IT justification: project costs are estimated before the work, results are measured (if at all) six months after go-live in a separate system, and the ROI model is a spreadsheet built to justify the decision retroactively. Everyone knows it. No one has fixed it.

With L402 endpoint fees + IL(Device/MCP/Port/)WAC, project costs and project results are in the same unit, on the same system, sealed by the same hash chain.

**Project costs are in satoshis from day one.** Every MCP call, every agent action, every endpoint used during implementation debits the project wallet. No invoices. No time-tracking reconciliation. The wallet balance is the project cost — live, sealed, auditable.

**Results are in satoshis from the same system.** Recovered inventory value, prevented shrink, OTB savings — all measured through the ILWAC layer and the Fox case evidence chain. Same unit, same sealing, same source.

**Net position is real-time.** Project wallet outflows = endpoint fees (cost). Project wallet inflows = results credited (return). The ROI model is not a deck — it is a wallet balance with a hash chain behind every line.

This becomes the SI firm's differentiation: run a transformation project on Canary and the client sees real-time ROI, not a post-hoc justification. Cost and return in the same unit, sealed, not reconstructable after the fact.

---

## Token Plan and Budget — The Meter Model

Every account receives a token plan (a fixed allocation) and a budget ceiling (the L402 wallet). The base tier is predictable and plannable — the merchant knows their cost floor before a single endpoint is called.

**The meter — variable billing above the base plan — runs on one ratio: payroll to revenue.**

Not transactions processed. Not API calls. Not seats. The ratio that defines whether a retail operation is healthy or bleeding. When payroll/revenue improves — fewer labor hours per dollar of sales, tighter scheduling, better shrink recovery, tighter OTB — the meter earns. When the ratio does not move, the meter does not run hard.

**Why payroll-to-revenue:**

- It is the one ratio that touches every module. Labor scheduling (L), shrink recovery (Q), OTB efficiency (M), margin on receipts (V) — every module's work either improves or degrades the ratio.
- It aligns Canary's revenue with merchant operational efficiency. The platform only wins when the merchant wins.
- It is the metric the CIO and CFO can both read. The CIO controls the endpoint spend; the CFO tracks the ratio. They are now looking at the same ledger.

**The token budget enforces discipline.** Accounts cannot infinitely call agents and endpoints. The budget makes every MCP call a real economic decision. A cost center burning token budget on low-value queries surfaces as a signal — the same as unnecessary labor hours on the schedule.

**The franchise application:** Franchisors set the payroll/revenue target as a brand standard. The meter enforces it commercially. Units that hit the target pay the base plan. Units that beat it earn credits. Units that miss it pay the overage. The fee schedule is the brand standard.

---

## What Does Not Exist Yet

This is architectural direction, not current implementation. What exists today:

- ILWAC (Item × Location × WAC) in Module V — functional, documented in `Canary/docs/sdds/v2/module-v.md`
- Satoshi-cost-accounting as a CATz substrate primitive — documented
- RaaS namespace resolution — functional, documented in `docs/sdds/canary/raas.md`
- SHA-256 hash chain in Sub 1 — functional, documented in `Canary/docs/sdds/v2/webhook-pipeline.md`
- L402 middleware (Goose) — documented in `docs/sdds/canary/goose.md`

What does not exist yet:

- The Device, MCP, and Port dimensions added to the WAC calculation
- Batched JSON RIB message format by domain
- Satoshi denomination at the system accounting level (currently fiat, with satoshi as a parallel substrate)
- The unified IL(Device/MCP/Port/)WAC recalculation engine

The design pass that produces GRO tickets for these items has not happened. This note is the record that the vision exists and the direction is set. The implementation follows a formal architecture session.

---

## Why No One Has This

Standard retail cost accounting:
- Fiat-denominated (dollar risk embedded in the cost model)
- Device-agnostic (no record of which terminal processed the event)
- Channel-blind (Square events and Counterpoint events produce identical WAC inputs)
- Agent-invisible (no record of which system authorized the cost-affecting action)
- Batch-less (most modern systems process individual events, losing the domain-organization benefit of RIB)

IL(Device/MCP/Port/)WAC on a Bitcoin standard:
- Satoshi-denominated (fiat is the display layer)
- Device-aware (terminal is a cost dimension)
- Channel-aware (POS port is a cost dimension)
- Agent-aware (MCP tool authorization is a cost dimension)
- RIB-batched by domain (domain origin is preserved and hashed)

The combination does not exist in any retail cost model in production today.

---

## Related

- [[Brain/wiki/cards/portable-store-founder-intent|Portable Store — Founder Intent]] — the vision this cost model serves
- [[Brain/wiki/cards/platform-thesis|Platform Thesis — Every Entity Has a Meter]] — the accountability model
- [[Brain/wiki/canary-raas-positioning|Canary RaaS — Positioning Guardrail]] — audit constraints on cryptographic claims
- `Canary/docs/sdds/v2/module-v.md` — current ILWAC implementation (Item × Location)
- `Canary/docs/sdds/v2/module-i.md` — Item master; vendor cost as input to V (I.9.2)
- `docs/sdds/canary/raas.md` — namespace resolution that owns the portable cost record
- `docs/sdds/canary/goose.md` — L402 payment middleware
- Canary-Retail-Brain: `platform/satoshi-cost-accounting.md` — existing substrate primitive
- Canary-Retail-Brain: `platform/satoshi-precision-operating-model.md` — existing substrate primitive

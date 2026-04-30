---
title: Why Canary
classification: confidential
nav_order: 1

---

# Why Canary

The retailer has always had accountability in theory. In practice:

- Loss prevention couldn't prove what they knew because the evidence chain was manual and contestable.
- Buyers overspent open-to-buy because the constraint was a spreadsheet someone could edit.
- Cost centers bloated because "unknown" variance gave everyone cover.
- Profit centers missed plan because external factors were untestable.

Canary removes every one of those escape routes. Not punitively — structurally. The graph is closed. The meters run. Everyone is held to their contract, including the platform.

---

## The three accountability rails

Each rail closes a different class of accountability gap that retail has historically accepted as unavoidable.

### Rail 1 — Operational: No unknown loss

The 13-module spine is a closed graph. Every unit of inventory, labor, price, space, and transaction has a node with a measurement contract. Every gap between expected and actual is detectable and traceable to a specific module, a specific actor, a specific event in the timeline.

Shrink either has a Fox case (an investigated event), a forecast variance, or a receiving discrepancy. If none of those exist, the absence is itself a signal — a failure in the accountability chain, not a mystery. The local market intelligence layer eliminates the last alibi: external signals (weather, seasonality, community intel) either explain a variance or they don't.

The word "shrinkage" described the space where negligence, vendor fraud, and operational sloppiness hid. Canary makes that space measurable.

**Closing statement:** *If it happened in the store, it is in the model. If it is in the model, it is measured. If it is measured, someone is accountable for it.*

### Rail 2 — Financial: No unauthorized spend

Open-to-buy (OTB) is not a number in a database. It is a funded wallet. A commercial agent commits spend by calling a tool gated by the wallet — the spend draws against the balance, the authorization is the receipt. If the wallet is empty, the tool call fails. The agent cannot overspend because the constraint is the balance itself.

Management is accountable too. Approving a budget that is never funded is visible — the agent's planned buys fail at the point of commitment, not at quarter-end. You cannot say you authorized a budget you did not fund.

**Closing statement:** *Every spend is a settled payment. Every approval is a funded wallet. Every variance is a failed payment or an exceeded plan — both are measurable, both are owned.*

### Rail 3 — Evidentiary: No unanchored record

Every event that affects accountability — a Fox case generation, a status transition, a chargeback claim, a return decision — produces a cryptographic hash. The hash becomes part of an append-only chain. The chain is independently verifiable: a court, an insurer, a regulatory auditor, or a procurement team can check the chain of custody without trusting any party's word.

The chain is internally verifiable as required core. Public anchoring to a verifiable blockchain (when enabled) converts internal verifiability into externally verifiable evidence — the kind of evidence that holds up in court without the merchant having to assemble a binder.

**Closing statement:** *The evidence chain is verifiable. The timeline is immutable. What happened is provable to anyone.*

---

## The meter model — every entity has one

Every entity in the system operates under one of two performance contracts.

### Cost centers — efficiency plus budget

A cost center's meter has two dials: efficiency and budget adherence.

| Entity | Efficiency metric | Budget constraint |
|---|---|---|
| Labor | Labor cost per transaction, schedule adherence rate | Labor OTB wallet |
| Asset Management | Asset utilization rate, depreciation vs plan | Capex OTB wallet |
| Distribution | Fill rate, landed cost per unit | Distribution OTB wallet |

Being a cost center is not a penalty. It is a contract: operate efficiently, stay in budget, and the platform leaves you alone. Exceed budget without a corresponding plan change, and the variance surfaces to the merchant before the next planning cycle.

### Profit centers — exceed plan

A profit center's meter has one dial: performance against plan.

| Entity | Performance metric | Plan authority |
|---|---|---|
| Transaction | Revenue vs forecast, transaction volume vs plan | Forecast |
| Customer | Lifetime value, loyalty earn rate vs target | Commercial |
| Pricing & Promotion | Margin vs plan, promotional ROI | Commercial |
| Commercial | OTB utilization, sell-through %, gross margin vs plan | Head Office |
| Store | Comp sales, shrink rate vs benchmark, labor efficiency | District |

Meeting plan is not the goal. Exceeding plan is the contract.

### Agent accountability — agents have meters too

Agents are not exempt from the meter. They are participants in the accountability model.

| Agent type | Meter |
|---|---|
| Domain agents (Operations, Business, Finance, Technical) | Signal accuracy rate, false positive rate on escalations, SLA pass rate |
| Local Market Agent | Lead conversion rate, signal latency |
| Infrastructure agents | Uptime, cost per action vs SLA, error rate |
| Controller (network coordinator) | Network health score, cross-agent conflict resolution rate |

An agent that escalates everything to the merchant has a high escalation rate — that is a measurable failure. An agent that never escalates and misses a critical exception is equally measurable. Agents are held to their contracts the same way humans are.

---

## What this means for the merchant

Three rails. One closed system. The merchant operates above their weight class because the platform carries the operational machinery.

The four-beat outcome:

1. **Stays on track.** Plans are wallets the agents respect. Variance surfaces before quarter-close, not after. The merchant does not chase numbers; the numbers surface themselves.
2. **Meets customers where they're going.** The local market layer gives the retailer a forward signal tuned to their specific geography and category mix — seasonality curves, weather shifts, social trends, community events. Same signals Amazon has at scale, delivered at community scale, hyper-local, in real time.
3. **Operates above weight class.** The agent network carries analytical and operational work that would otherwise need a full team. LP monitoring, forecast adjustment, commercial signal surfacing, compliance tracking, evidence anchoring — agents handle these continuously. The merchant gets the output, not the overhead.
4. **Gets back to running the store.** This is why any of it gets built. The SMB retailer opened a store because they know their product, their community, and their customers. The operational weight took that away — the meters became the job, the customers became the interruption. Canary inverts that. The merchant walks the floor instead of running reports. Talks to the customer in front of them instead of auditing receiving. They are a merchant again.

---

## The sentence

> *This model keeps the merchant on track, meets their customers where they're going, and gives them back the power to actually serve them — instead of worrying about ops and tech.*

That is the why.

---

## Glossary — terms used on this page

| Term | Definition |
|---|---|
| **OTB (open-to-buy)** | The financial constraint on purchasing — historically a planned dollar number per buyer per period. In Canary, OTB is a funded wallet that gates purchase orders at commitment time. |
| **Fox case** | An investigation case in Canary's loss prevention module. Cases carry hash-chained evidence and an append-only timeline. |
| **Hash chain** | A sequence of records where each record contains the cryptographic hash of the previous record. Tampering with any record invalidates the chain from that point forward. |
| **Agent** | An autonomous component that performs operational work — Operations Agent monitors KPIs, Business Agent reviews exceptions, Finance Agent posts to the GL, etc. Every agent action is attributable in the audit trail. |
| **Meter** | A quantitative performance contract attached to an entity — a store, an agent, a cost center, a profit center. Every entity has one.

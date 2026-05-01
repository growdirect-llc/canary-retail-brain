---
date: 2026-04-24
type: platform-substrate
owner: GrowDirect LLC
classification: confidential
tags: [substrate, satoshi-precision, operating-model, cogs, cac, sga, iot, end-to-end-precision, top-down]
nav_order: 11

---

# Satoshi-Precision Operating Model

> **The unifying principle.** Every cost element in the merchant's operating
> model — Cost of Goods Sold, Customer Acquisition Cost, SG&A — and every
> physical and digital movement that drives those costs is tracked at
> satoshi precision (sub-cent, ledger-grade) end to end. IoT extends the
> movement-tracking surface beyond POS-only to every meaningful physical
> event in the store. The Virtual Store Manager surfaces this granular
> truth; merchants for the first time know what every cent of every cost
> actually was, where it went, and what it produced.

## Why this article exists

The [[satoshi-cost-accounting]] substrate article named sub-cent unit
cost on the perpetual ledger as a Canary innovation. That was the right
starting move but undersold the principle. Satoshi precision is not a
ledger feature — it is the **operating-model commitment** that makes the
entire 13-module spine internally consistent and externally credible.

If the perpetual ledger is satoshi-precise but COGS rolls up at penny
precision, the precision falls out the bottom. If COGS is satoshi-precise
but CAC and SG&A are guessed monthly from accounting summaries, the
merchant cannot answer the only question that actually matters:
**"Did this customer make me money, and how do you know?"**

The Virtual Store Manager's promise is that *every dollar in and every
dollar out of the merchant's business is decomposed to its originating
event with full audit trail*. That promise requires satoshi precision
through the entire stack, not just on inventory cost. This article names
that commitment and walks each cost dimension that has to honor it.

## The four cost dimensions

### 1. COGS at satoshi precision

Already grounded in [[satoshi-cost-accounting]]. Every unit's landed cost
is tracked in millisatoshis (`cost_msat BIGINT`) alongside fiat cents
(`cost_usd_cents INT`), with the FX rate captured at posting time. Every
movement on the [[stock-ledger|perpetual ledger]] carries both
representations. Variance, write-offs, shrink, and markdown all post
against the satoshi side as the authoritative cost basis; fiat is the
display projection.

What this enables: per-unit margin queryable in real time at full
precision, even for items where the per-unit margin is fractional cents
(e.g., bulk consumables, low-value inventory, fractional packaging).

### 2. CAC at satoshi precision

Customer Acquisition Cost is the most-faked number in SMB retail. Most
merchants compute it as `total marketing spend ÷ new customers this
month` — an aggregate metric that hides every actionable fact.

Satoshi-precision CAC decomposes:

- **Channel-level spend** posted at touch time. Every ad impression /
  click / placement charge, every SEO content piece's amortized cost,
  every email send's compute + delivery cost — each posted as a
  channel-specific event on the perpetual ledger at sub-cent precision.
- **Attribution** computed against the actual customer journey on the
  ledger (first touch, last touch, multi-touch with weights). The
  customer journey is itself a stream of perpetual events: page views,
  cart adds, abandonments, returns, eventual purchase.
- **Per-acquired-customer rollup** as a derived projection. CAC for
  customer X = sum of channel spend events attributed to X's journey.
  Reported in fiat for human consumption; backed by satoshi-precise
  underlying events.

What this enables: merchants can ask "what did Customer X cost to acquire
and what's their lifetime value so far?" and get a real answer with
audit trail back to the originating ad clicks. They can compare channels
at the level of *return on satoshi spent* rather than *return on dollar
spent rounded*.

### 3. SG&A at satoshi precision

Selling, General & Administrative is the catch-all that absorbs every
overhead element merchants do not bother to decompose. Satoshi-precision
SG&A decomposes:

- **Labor cost per shift per minute** — driven by [[../modules/L-labor-workforce|v3.L Labor]]
  module's time-clock event stream. Each minute on the clock posts a
  labor-cost event on the perpetual ledger at the employee's precise
  rate (with shift differentials, overtime, etc.) in millisatoshis.
- **Rent allocated per minute per square foot** — fixed monthly rent
  expense decomposed into minute-by-square-foot accruals; reportable
  per location, per department within a location, per fixture.
- **Utilities per device per minute** — electrical / network / cloud
  costs allocated to specific devices (POS, cameras, IoT sensors) by
  measured consumption (where IoT enables measurement) or attribution
  (where it does not).
- **Software costs per agent-tool-call** — every Canary tool call gas-
  metered through the [[../platform/satoshi-cost-accounting|satoshi-cost]]
  GasMeter (already shipping per Goose / GRO-117). External SaaS
  subscriptions (QuickBooks, Gusto, etc.) accrue per-active-user per-day
  against the merchant's wallet.
- **Cost-of-tool-not-Canary** — for every package the merchant integrates
  with under [[perpetual-vs-period-boundary|integrated-hybrid]], the
  monthly subscription cost is captured as a per-day SG&A accrual against
  the merchant's perpetual ledger.

What this enables: per-transaction true cost (COGS + allocated SG&A +
allocated CAC). Per-store true contribution margin. Per-product-per-store
true profitability. None of this is currently visible at SMB tier;
merchants run on guesses.

### 4. IoT-tracked movement (the new perpetual-event source)

The earlier generation of perpetual ledgers ingested only POS movements.
Modern retail has 100× the meaningful events available, gated only by
instrumentation. The Internet of Things is the instrumentation.

Movement sources that an IoT-enabled Canary install captures as
ledger events:

- **Foot traffic** — door counters, computer-vision people-counters
  posting customer-arrival and customer-departure events; conversion
  rate (visitors → transactions) computable in real time per minute per
  store.
- **Dwell-and-flow** — in-store positioning beacons posting dwell-time
  events per zone per visitor; "sections people walk past without
  stopping" becomes a measurable KPI.
- **Shelf state** — RFID tags or computer-vision shelf monitors posting
  out-of-stock detection events the moment a shelf empties, not at next
  cycle count.
- **Cold-chain** — temperature sensors on refrigerated units posting
  temperature-event streams; deviation events trigger automatic shrink
  reason codes on the perpetual ledger.
- **Door / safe / drawer events** — physical access events on cash
  drawers, back-room doors, safes; cross-referenced against employee
  clock-state for security and shrink attribution.
- **Equipment health** — meter readings, fault codes, maintenance events
  on every device in the store; preventive-maintenance events posted to
  the [[../modules/A-asset-management|A Asset Management]] module's
  bubble.
- **Customer device interactions** — receipt-printer events, POS terminal
  events, kiosk interactions — all already partially captured; IoT
  extends to peripherals not previously instrumented.

Every IoT event is a movement on the perpetual ledger with a typed
schema. The ledger's verb taxonomy ([[stock-ledger#the-canonical-movement-verbs]])
extends to accommodate the new verbs (`foot_traffic_arrival`,
`shelf_oos_detected`, `cold_chain_excursion`, `equipment_fault`, etc.).
Each event is satoshi-stamped with its capture cost (the marginal cost
of the IoT sensor reading) and contributes to the merchant's SG&A
allocation if the sensor is itself a metered service.

What this enables: a perpetual-ledger view of the store that includes
*everything happening in the physical space*, not just the cash-register
events. The Virtual Store Manager can answer questions like *"how many
people walked past the new endcap and how many converted?"* at the same
fidelity it answers *"what was today's shrink in dairy?"*.

## The end-to-end commitment

Read together, these four dimensions describe a merchant operating model
where:

1. **Every cost is decomposed to its originating event.** No more
   "marketing spend $4,200 / divided by 23 customers / $182 CAC."
   Instead: "Customer X cost $173.42 to acquire — here are the 17
   channel events that produced them, here's the conversion path,
   here's the attribution weighting we used."

2. **Every event is captured at satoshi precision in real time on the
   perpetual ledger.** Display rounds to fiat for humans, but the
   underlying truth is sub-cent and audit-traceable.

3. **Every roll-up is derivable from the events.** The merchant's
   monthly P&L, COGS schedule, marketing performance report, labor
   productivity scorecard, and contribution-margin-by-product report
   are all projections of the same perpetual-ledger event stream. There
   is no separate truth in a marketing dashboard or an HR system that
   conflicts with the ledger.

4. **Every cost has audit trail.** A merchant can drill from a P&L
   line down to the originating event in seconds. Auditors,
   investors, lenders all consume the same perpetual-ledger truth as
   the operator.

## What this means for the spine

This principle re-reads the existing 13 modules as instruments of cost
decomposition:

| Spine module | COGS contribution | CAC contribution | SG&A contribution | IoT contribution |
|---|---|---|---|---|
| **T** Transactions | Sale at fiat-display price | First/last touch capture for attribution | Payment-processor fees per transaction | Receipt-printer + terminal events |
| **R** Customer | Customer identity for attribution rollup | Per-customer journey reconstruction | n/a | Customer-device interactions |
| **N** Device | n/a | n/a | Equipment health → maintenance accrual | Device telemetry as canonical IoT source |
| **A** Asset Mgmt | n/a | n/a | Anomaly cost attribution | IoT bubble per device |
| **Q** Loss Prev | Shrink → COGS write-off | n/a | Investigation labor | Door/safe/drawer events as detection inputs |
| **C** Commercial | Cost-update events at landed unit cost | n/a | Buyer labor allocation | Cold-chain → reason-code shrink |
| **D** Distribution | Receipt + transfer + RTV at cost | n/a | DC labor allocation | Shelf-state events for OOS detection |
| **F** Finance | RIM cost-complement / Cost Method posting | Marketing-spend-event posting + attribution | All overhead accruals + GL roll-up | n/a |
| **J** Forecast | Demand signal for replenishment | Customer-frequency forecast feeds CAC payback | n/a | Foot-traffic forecast inputs |
| **S** Space/Range | Planogram cost basis at slot precision | Conversion attribution per zone | Fixture allocation | Dwell-and-flow per zone |
| **P** Pricing/Promo | Price/markdown events that revalue ledger | Promo-attributed acquisition | n/a | Dynamic price reaction to IoT signal |
| **L** Labor | n/a | n/a | Time-clock events at minute precision | Workforce IoT (badge, location) |
| **W** Work Exec | Cross-domain exception cost attribution | n/a | Investigation + remediation labor | Cross-IoT exception correlation |

Every cell in this matrix becomes a real product capability the VSM can
expose. None require new modules — they are projections of the existing
spine when read against the satoshi-precision principle.

## What this means for product, sales, and engineering

**Product.** Every new feature decision asks: does this preserve satoshi
precision end to end? If a roll-up is added that hides the underlying
event chain, it does not ship. The VSM must always be able to drill from
the answer back to the events.

**Sales.** The pitch becomes specific: *we are the only retail platform
that knows what every cent of every cost actually was, where it went,
and what it produced.* This is not "we have a dashboard" — it is "you
will know things about your business no SMB merchant has ever known." The
Clarks-style diagnostic ([[../case-studies/canary-retail-diagnostic-archetype]])
becomes the demo: prize-sized opportunities with sub-cent audit trail.

**Engineering.** The substrate for this is mostly already in place
(stock-ledger, satoshi-cost-accounting, perpetual-vs-period-boundary).
The remaining engineering work is: (a) extend the ledger verb taxonomy
to include CAC-attribution events and IoT events; (b) build the
projection layer that rolls perpetual events into the merchant-readable
P&L, CAC report, contribution-margin report; (c) integrate the first IoT
sources (door counters, shelf RFID, cold-chain sensors) as Phase-1
parallel observers under the [[perpetual-vs-period-boundary|staged-migration]]
pattern.

## Open questions

1. **Attribution model defaults.** What's the default attribution model
   for CAC at install? First-touch, last-touch, multi-touch with linear
   weighting, or merchant-configurable? Defaults matter — most merchants
   will never change them.

2. **IoT vendor strategy.** Which IoT verticals does Canary integrate
   with first? Foot traffic (Density, RetailNext), shelf RFID (Impinj,
   Avery Dennison), cold-chain (Verkada, monnit) — same `integrated-hybrid`
   route question as accounting tools. Pick a starter vendor per
   category for v3 work.

3. **SG&A allocation policy.** Per-merchant allocation rules for rent,
   utilities, software costs are not standardized. Default to the
   simplest defensible split (per-square-foot, per-device, per-day) and
   surface as merchant-overridable.

4. **Per-customer LTV computation cadence.** Real-time, daily, on-demand?
   Affects compute cost. Real-time is the goal but may be a v3+
   capability.

5. **Privacy posture for in-store positioning.** Foot-traffic and
   dwell-and-flow capture customer signals that have privacy implications
   in some jurisdictions. Posture: aggregate-only by default;
   per-individual tracking opt-in per merchant per jurisdiction.

## Related

- [[stock-ledger|Stock Ledger — the perpetual-inventory movement ledger]] — the substrate this principle is read against
- [[satoshi-cost-accounting|Satoshi-Level Cost Accounting]] — the COGS-side of the precision principle (this article generalizes it)
- [[retail-accounting-method|Retail Accounting Method — RIM, Cost Method, OTB]] — the period-summary side that satoshi-precision flows into
- [[perpetual-vs-period-boundary|Perpetual-vs-Period Boundary]] — the staged migration that makes parallel-then-cutover possible
- [[spine-13-prefix|The Canary Retail Spine — 13 Modules]] — every module is an instrument of cost decomposition under this principle
- [[../../GrowDirect/Brain/wiki/growdirect-viewpoint-virtual-store-manager|GrowDirect Viewpoint — VSM on a Perpetual Ledger]]
- [[../../GrowDirect/Brain/wiki/growdirect-the-goose|The Goose]] — Canary's GasMeter / L402 satoshi-metering implementation; the production proof point already shipping
- [[../case-studies/canary-retail-diagnostic-archetype|Canary Retail Diagnostic — Archetype]] — what the satoshi-precision rollup looks like for a real merchant
- [[module-manifest-schema|Module Manifest Schema]] — every module's contribution to the precision principle is declared in its manifest

## Sources

- Goose / GRO-117 — production GasMeter shipping satoshi-precision per-tool metering
- L402 protocol — Lightning auth + payment substrate for sub-cent metered access
- Satoshi-cost-accounting article — COGS-side foundation
- IoT instrumentation industry references — Density, RetailNext, Impinj, Verkada, monnit (vendor research deferred to v3 work)

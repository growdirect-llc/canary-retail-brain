---
tags: [canary, go, architecture, pricing, satoshi, bitcoin-standard, cost-model, l402, micropayment, rev-share, diagnostic]
last-compiled: 2026-05-01
related: [canary-go-cadence-ladder, canary-go-endpoint-library, canary-go-vs-gk-pos-gap-analysis, canary-go-portal]
---

# Canary Go — Satoshi Cost Model

> **Governing thesis.** Canary's commercial model is satoshi-denominated cost-to-serve, not seat-based subscription. Every event flowing through the platform, every agent decision made, every byte stored has a measured satoshi cost rolled up to the merchant level and settled via Lightning. This is the natural extension of three patent-protected primitives already in the stack — **ILDWAC** (provenance-weighted cost model), **L402-OTB** (Lightning settlement), and **canary-blockchain-anchor** (verifiable usage records). Seat pricing leaves the moat on the table; satoshi rollup exposes it directly to the buyer. Critically, the diagnostic process that opens every sales conversation can be reduced to **five simple inputs** and produce a side-by-side forecast against any seat-based competitor — a discovery instrument no other retail platform can offer.

This article is the spine for the cost model. The buildable spec lives in `docs/sdds/go-handoff/satoshi-cost-rollup.md`. The agent recall surface lives in `Brain/wiki/cards/infra-satoshi-cost-rollup.md` and supporting cards.

## Why satoshi-denominated

| Property | Why it matters here |
|---|---|
| **Sub-cent precision** | One satoshi = 10⁻⁸ BTC. At any reasonable BTC/USD rate, a satoshi resolves to < $0.01. Per-event metering, per-tool-call gating, per-byte storage — all expressible without rounding to penny floors. |
| **Settles natively** | Lightning Network is the settlement layer. L402-OTB already implements the gate. No traditional payment-rail integration needed for micro-amounts; no PCI implications because the value layer is Bitcoin, not card. |
| **Deflationary denominator** | Fiat-denominated cost-to-serve drifts with inflation; satoshi-denominated cost-to-serve drifts with BTC. Customer's monthly bill in sats is stable; in fiat, it tracks BTC's purchasing power — historically deflationary against goods + services. |
| **Anchored, verifiable** | Every period-end usage statement gets its Merkle root committed to a Bitcoin L2 via canary-blockchain-anchor. Merchant can verify any line item against an immutable timestamp. **No competitor offers this.** |
| **Channel-native rev-share** | Lightning routes value at micropayment scale. VAR rev-share isn't a contract clause negotiated annually; it's a Lightning route that settles per-event. |

## The cost model

### Unit decomposition

```
sat_cost(merchant, period) =
    Σ events × tier_weight(t) × service_unit_cost(s)         ← ingestion + processing
  + Σ storage_GB × storage_tier_weight(s) × days             ← retention
  + Σ agent_decisions × decision_cost(tool, t)               ← MCP / API tool calls
  + Σ external_passthroughs                                  ← upstream API costs
  + Σ blockchain_anchor_share(period)                        ← amortized L2 commit cost
  + base_platform_floor(merchant_tier)                       ← minimum + identity + RaaS
```

Six terms. Each is independently measurable from primitives already in the architecture.

### Tier weights (from cadence ladder)

The cadence ladder establishes the cost asymmetry between tiers. A stream-tier event carries ~50× the per-event compute, alert routing, and bandwidth cost of a reference-tier read.

| Tier | Weight (relative) | Driver |
|---|---|---|
| Stream | **10.0** | Per-event compute, SSE bandwidth, real-time alert routing, replay queue retention |
| Change-feed | **4.0** | Bounded polling, watermark cursoring, lag observation |
| Daily batch | **1.5** | Scheduled compute, amortizable across slot |
| Bulk window | **1.0** | Scheduled batch compute, fully amortized within window |
| Reference | **0.2** | Cached reads, TTL-amortized, mostly read-heavy |

These are calibration parameters, not constants — the production system measures actual per-tier resource consumption and recalibrates quarterly. The 10:4:1.5:1:0.2 ratio is the architectural invariant; the absolute satoshi values are deploy-time configuration.

### Per-service unit costs

Each of the 32 services in the spine + extended block has a calibrated `service_unit_cost`. The cost reflects real compute, storage, and per-event work the service does. **Patent-protected services charge a moat premium** — partners pay for differentiation that can't be built elsewhere.

| Service class | Unit cost (sats / event, illustrative) | Notes |
|---|---|---|
| Ingestion (`tsp`, `gateway`) | 2 | Minimal compute; pipeline steward |
| Master data reads (`item`, `customer`) | 1 | Cached reference-tier; cheap |
| Detection eval (`chirp`) | 30 | Per-rule evaluation against transaction; pgvector touch |
| Case ops (`fox`) | 50 | Hash chain compute, evidence write |
| Search / intelligence (`owl`) | 80 | pgvector search, embedding compute |
| Real-time inventory (`inventory-as-a-service`) | 15 | SSE bandwidth, position cache |
| Compliance lookup (`compliance`) | 5 | Heavily cached; reference-tier dominant |
| Identity (`identity`) | 1 | JWT validation, session lookup |
| RaaS key construction (`raas`) | 0.5 | Deterministic; cache-hit dominant |
| **ILDWAC recompute** (patent-protected) | **150** | Provenance-weighted recompute; multi-dim cost model |
| **L402-OTB gate** (patent-protected) | **20** | Lightning gate decision + budget update |
| **Blockchain anchor** (patent-protected) | **5,000** | Includes amortized L2 commit cost for batch slot |
| **Store-network-integrity correlation** | 200 | Cross-location pattern recognition; expensive |
| **Field-capture lookup** | 3 | Cached pgvector kNN |
| Reports / exports (`report`) | per-MB cost | Scheduled compute + object-storage write |

Numbers above are **illustrative for design**, not committed pricing. Calibration happens at deploy time per the buildable spec.

### Per-decision costs (MCP tool calls)

Agent decisions are the dominant variable cost driver in any AI-native deployment. Each MCP tool call decomposes:

```
sat_cost(tool_call) =
    base_cost(tool, service)
  × tier_multiplier(declared_tier)
  × output_size_factor                  ← search returning 100 vs 10 results
  × cache_state_factor                  ← cache-hit pays ~10% of cache-miss
  + external_api_passthrough            ← if the tool crossed a boundary
```

Illustrative tool costs at typical workloads:

| MCP tool | Tier | Base | Effective cost (sats / call) |
|---|---|---|---|
| `compliance.lookup` | Reference | 5 | ~5 (cache-hit) / ~50 (cache-miss) |
| `compliance.create_block` | Stream | 30 | ~300 (stream tier × 10) |
| `raas.build_key` | Reference | 0.5 | ~0.5 (deterministic) |
| `raas.anchor_hash` | Stream | 50 | ~5,000 (includes amortized L2 commit) |
| `owl.search` | Reference | 80 | ~80 (cache-hit) / ~800 (vector kNN) |
| `fox.add_evidence` | Stream | 50 | ~500 (stream tier × 10) |
| `chirp.evaluate_rule` | Change-feed | 30 | ~120 (change-feed × 4) |
| `store_brain.check_permission` | Reference | 2 | ~2 (cache-friendly) |
| `ops.health_rollup` | Reference | 10 | ~10 |

A merchant with 10,000 decisions/day in a typical mix lands ~150K-300K sats/day in decision cost — **at $60K BTC, ~$0.09-$0.18/day, ~$3-$6/month** just on agent decisions. The full bill (ingestion + storage + decisions + anchoring) lands somewhere meaningfully above that.

This is what the diagnostic surfaces.

## Settlement architecture

Three settlement patterns compose. Most merchants use all three.

### 1. Pre-funded OTB allocation (existing primitive)

Per [[canary-l402-otb|L402-OTB]]:

- Merchant funds a Lightning wallet at month-start
- Cost-to-serve auto-deducts as services consume
- Real-time balance visible via `GET /l402-otb/budget`
- Empty wallet → gate decisions return `402` with L402 invoice

This is the **primary settlement path** for steady-state operation.

### 2. Per-call gating (existing primitive)

For high-value or external-passthrough calls:
- `POST /l402-otb/gate` returns `200 {allowed:true}` or `402 {allowed:false, l402_invoice:<lightning-invoice>}`
- Pay-and-continue UX: client presents the invoice to the operator (if interactive) or pays automatically (if pre-authorized)
- Settled payment IS the authorization — cryptographic, timestamped, non-repudiable

### 3. Period-end settlement with L2 anchor (new — buildable from existing primitives)

For trusted, established merchants:
- Accrue cost-to-serve continuously into per-merchant Lightning channel state
- Period-end (weekly / monthly): compute Merkle root over all line items
- Submit Merkle root to canary-blockchain-anchor for L2 commit
- Lightning settle the period total
- Merchant retains line-item-level receipts; can verify any item against the Merkle root + L2 commit

**This is the killer instrument.** A merchant's monthly bill is independently verifiable against an immutable Bitcoin L2 timestamp. No competitor offers this. The same primitive that protects evidence (Fox + blockchain-anchor) protects the bill.

### Lightning integration topology

```
Merchant ←─ Lightning channel ─→ Canary L402-OTB Lightning node
                                        ↓
                                  Per-merchant accrual
                                        ↓
                                  Period-end Merkle root
                                        ↓
                            canary-blockchain-anchor
                                        ↓
                                  L2 commit (Liquid / RSK / Stacks)
                                        ↓
                            Verifiable usage statement URL
```

Each merchant has a dedicated Lightning channel. Channel capacity sized at typical monthly cost-to-serve × 2 (headroom). Channel rebalanced at period-end alongside L2 commit. This is canary-l402-otb's Phase 2 buildout.

## Rev-share

### Per-microservice attribution

Three rev-share classes:

**First-party services** — full revenue to GrowDirect.
- All current 32 services in the spine + extended block fall here.
- Calibration costs reflect actual compute + amortized infra.
- Margin is the gap between calibrated cost and metered price.

**Partner-contributed services** (future) — split per published cost model.
- Partner registers a microservice that joins the agent surface.
- The microservice declares its rev-share at registration via feed-tier-contract.yaml: `revshare: { partner_id: <uuid>, share: 0.30 }`.
- Gate enforces the split: every satoshi flowing to that service is fan-out at settlement time.
- Partner can join, leave, or update share without contract negotiation — it's a Lightning route configuration.

**Channel rev-share (VARs)** — share of adapter-attributed traffic.
- Every event flowing into Canary carries `SourceCode` per CRDM (`square` / `counterpoint` / `shopify` / etc.) — already required field in `TransactionHeader`.
- Adapter binary tags every event with the channel partner's identifier (e.g., RapidPOS for Counterpoint events).
- Period-end aggregation: total satoshis flowing through `source = counterpoint` events, multiplied by channel share, settled to the channel partner's Lightning address.
- **No quota negotiation. No annual contract.** RapidPOS earns directly proportional to traffic flowing through their adapter — aligned by data flow, not by sales target.

### How attribution works (existing primitives)

| Primitive | Role in rev-share |
|---|---|
| CRDM `SourceCode` field | Every event tagged with originating adapter |
| `app.feed_registry` | Each adapter feed declares `producers` (channel partner) |
| canary-raas chain anchor | Per-merchant chain segments enable per-channel aggregation queries |
| canary-blockchain-anchor | Period-end attribution Merkle root commit |
| canary-l402-otb Lightning channel | Settlement instrument (one channel per channel partner) |

**Every component already exists.** Rev-share is a SQL aggregation + a Lightning route — no new infrastructure.

## Diagnostic process — five simple inputs

The diagnostic is the **discovery instrument**. Five inputs the buyer answers in 30 seconds; the platform produces a side-by-side forecast.

### Input form

| Symbol | Input | Typical SMB range | What it captures |
|---|---|---|---|
| **T** | Transactions / month | 1K – 100K | Ingestion + detection volume |
| **L** | Active locations | 1 – 20 | Tenant scaling, multi-store correlation |
| **P** | POS sources | 1 – 3 | Adapter mix (Square + Counterpoint + ecom) |
| **A** | Agent decisions / day | 100 – 10,000 | MCP tool call volume |
| **R** | Retention preference | 90d / 1y / 7y | Storage cost driver |

Optional sixth input for fidelity: **C** — compliance complexity (regulated items × number of regulatory zones, defaults to 1).

### Output forecast

```
Estimated monthly cost (illustrative — replaced with calibrated values at deploy):

  Ingestion + processing:
    T × 5 sats × 30 days                    = 5T × 30 = 150T sats

  Detection + cases:
    T × 0.3 trigger × (30+50) sats × 30     = T × 720 sats          ← 30% trigger rate × eval+case cost
    if cases escalate × 0.05 × 5,000 anchor = T × 250 sats          ← 5% escalation × anchor cost

  Storage:
    T × R × 0.05 sats / record / day        = T × R × 0.05 sats

  Agent decisions:
    A × 30 days × ~250 avg sats / call      = 7,500 A sats          ← typical mix

  Multi-location overhead:
    L × baseline (50K sats / location)      = 50,000 L sats

  Adapter overhead:
    P × baseline (100K sats / source)       = 100,000 P sats

  Compliance (if C > 1):
    T × C × 1 sat                           = TC sats

  Blockchain anchor share:
    1 commit / week × ~5,000 sats × 4       = 20,000 sats           ← amortized

  Base platform floor:
    Minimum 200K sats / month                = 200,000 sats
  ────────────────────────────────────────────────────────────────────
  TOTAL: f(T, L, P, A, R, C) sats / month
         ≈ $X.XX / month at <quoted BTC/USD>
```

Worked example — typical SMB specialty retailer:
- T = 20,000 transactions/month
- L = 3 locations
- P = 2 sources (Counterpoint + Shopify)
- A = 5,000 agent decisions/day
- R = 1 year retention
- C = 1 (no regulated items)

```
Ingestion:        20K × 150 = 3M sats
Detection:        20K × 720 = 14.4M sats
Anchor (escal):   20K × 250 = 5M sats
Storage:          20K × 365 × 0.05 = 365K sats
Decisions:        5K × 7,500 = 37.5M sats
Locations:        3 × 50K = 150K sats
Adapters:         2 × 100K = 200K sats
Anchor amortized: 20K sats
Floor:            200K sats
─────────────────────────────────────────
TOTAL:            ~60.6M sats / month
                  ≈ $36 / month at $60K BTC
                  ≈ $24 / month at $40K BTC
```

### Side-by-side: per-seat baseline vs per-flow Canary

Same merchant on competitive seat-based platforms:

| Platform | Pricing model | Estimated monthly | Notes |
|---|---|---|---|
| Square | $60 + $20/location/mo | 3 × $80 = $240/mo | Add transaction fees ~2.6% on every $ — Canary doesn't take a cut of transaction value |
| Lightspeed Retail | $99-$199/location | 3 × $129 ≈ $387/mo | + employee seats |
| Counterpoint license | $X licensed per terminal | varies wildly | Plus VAR support contract |
| Toast (restaurant) | $69-$165/location/mo | 3 × $120 ≈ $360/mo | (non-applicable example, illustrative scale) |
| **Canary (satoshi-rollup)** | **Flow-based** | **~$24-$36/mo** | Plus optional moat services priced separately |

The same merchant lands at **5-10× cheaper** on Canary than on competing seat-based platforms — *because they're a moderate-volume merchant whose flow doesn't justify seat fees.*

For a high-volume merchant (T = 500K, A = 50K decisions/day, L = 15):
- Canary lands ~$200-400/mo
- Square lands ~$1,200/mo
- Lightspeed lands ~$2,000/mo

The crossover never happens — flow pricing always undercuts seat pricing for any merchant whose flow doesn't grow linearly with headcount, which is essentially every retailer with automation.

### What the diagnostic actually does in the sales conversation

Three moves the diagnostic enables:

1. **Reframes the conversation.** "Your headcount" → "your operating reality." Buyers stop comparing seat counts and start comparing what they actually run.
2. **Surfaces the value layer.** A merchant pays Canary based on what flows through. The platform's incentive aligns with the merchant's efficiency — fewer wasteful events, lower bill, same outcomes.
3. **Anchors the moat.** The diagnostic ends with: "Want to see your bill verified against a Bitcoin L2 timestamp?" No competitor can answer that question. The conversation lands in moat territory by minute three.

## Implementation map

What's already in the architecture vs what needs to be built:

| Component | Status | Source |
|---|---|---|
| Cadence ladder + tier weights | ✅ Today's ship | [[canary-go-cadence-ladder]] |
| Feed-tier-contract (per-feed cost basis) | ✅ Today's ship | `docs/sdds/go-handoff/feed-tier-contract.md` |
| ILDWAC 5-dim cost model (patent) | ✅ Architecture | [[canary-ildwac]] · [[ilwac-extended-bitcoin-standard]] |
| L402-OTB Lightning gate (patent) | ✅ Architecture | [[canary-l402-otb]] · [[infra-l402-otb-settlement]] |
| canary-blockchain-anchor L2 commit | ✅ Architecture | [[canary-blockchain-anchor]] |
| canary-raas chain anchor | ✅ Architecture | [[canary-raas]] |
| `SourceCode` on every CRDM record | ✅ Required field | `internal/crdm/transaction.go` |
| canary-ops-dashboard SSE for telemetry | ✅ Specced | [[canary-ops-dashboard]] |
| Per-tool MCP cost calibration | ⚪ TBD | Profiling pass per tool |
| Per-service unit cost calibration | ⚪ TBD | Profiling pass per service |
| Per-merchant Lightning channel mgmt | ⚪ TBD | L402-OTB Phase 2 |
| Period-end usage Merkle root commit | ⚪ TBD | Combine raas + blockchain-anchor |
| Diagnostic input form + forecast | ⚪ TBD | Sales-side UI / spreadsheet, then API |
| Channel rev-share aggregator | ⚪ TBD | SQL aggregation by SourceCode + Lightning route |

**Eight components exist, six need to be built.** None of the six requires new infrastructure — all compose from existing primitives. The buildable spec is in `docs/sdds/go-handoff/satoshi-cost-rollup.md`.

## Pitfalls

- **Don't price the calibration parameters as constants.** Tier weights, per-service unit costs, and per-tool decision costs all drift with infrastructure changes. Quarterly recalibration with merchant-visible changelog is the discipline.
- **Don't expose internal calibration to merchants.** The merchant sees their bill and the verification path. They don't see the per-tool unit-cost matrix — that's commercially sensitive and changes more often than is helpful for pricing predictability.
- **Don't conflate satoshi-denominated with crypto-volatile billing.** Merchants want predictable monthly bills. Canary publishes a fiat-equivalent forecast at quote time and locks the satoshi rate for the period — exposure to BTC volatility is Canary's, not the merchant's.
- **Don't break the Lightning UX with custodial complexity.** Merchant Lightning wallet management is opt-in. Default UX: merchant funds OTB allocation via traditional rail (ACH / card) once a month; Canary handles Lightning under the hood. Lightning-native is the *option*, not the *requirement*.
- **Don't build the diagnostic as a calculator.** The diagnostic is a discovery instrument that drives a conversation. Five inputs → a forecast → a verifiable usage path. Build it as a guided experience, not a Excel spreadsheet handed to the buyer.

## Why this is the moat (and why $25/seat leaves it on the table)

Three claims competitors can't make:

1. **"Your bill is independently verifiable against an immutable Bitcoin timestamp."** No POS competitor has this primitive. None can build it without rebuilding the evidentiary rail. Patent-protected.
2. **"You see the cost of every microservice you consume in real time."** Square, Lightspeed, Toast charge a flat fee that hides cost-to-serve. Canary's structure is transparent by construction. No competitor wants to be transparent because their pricing has nothing to do with their costs.
3. **"Your channel partner earns proportional to data flow, not quota."** RapidPOS, NCR Counterpoint VARs, and future ecosystem partners get a share of every satoshi flowing through their adapter — settled per period via Lightning, anchored per L2 commit. No quota negotiation. No annual contract.

Seat-based pricing assumes the value is in the software. **Canary's value is in the flow.** Pricing the flow is more accurate, more defensible, and exposes the moat directly to the buyer in the first thirty seconds of the diagnostic.

## Cross-references

- SDD: `docs/sdds/go-handoff/satoshi-cost-rollup.md` (buildable spec)
- Card: [[infra-satoshi-cost-rollup]] (agent recall surface)
- [[canary-go-cadence-ladder]] (tier weights live here)
- [[canary-go-endpoint-library]] (the new `/usage/*` endpoints + MCP tools)
- [[canary-ildwac]] (provenance-weighted cost lineage)
- [[canary-l402-otb]] (Lightning settlement primitive)
- [[canary-blockchain-anchor]] (L2 commit + verifiable usage statements)
- [[canary-raas]] (per-merchant chain anchor)
- [[ilwac-extended-bitcoin-standard]] (founder intent — IL(D/MCP/Port/)WAC)
- [[platform-thesis]] (every entity has a meter — this is the meter)
- Memory: `project_ilwac_bitcoin_standard`, `project_canary_canonical_positioning`, `feedback_no_volatile_data_in_wiki`

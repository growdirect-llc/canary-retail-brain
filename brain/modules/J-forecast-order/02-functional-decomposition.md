---
title: J — Functional Decomp
classification: internal
type: wiki
sub-type: module-functional-decomposition
date: 2026-04-26
last-compiled: 2026-04-26
status: draft v1 (archetype — no real customer engagement)
module: J
solution-map-cell: ◐ Partial — Document family carries POs/PREQ/RECVR/RTV; replenishment engine UI-only; no forecast endpoints
companion-modules: [T, R, S, F, D, C, P, Q]
companion-substrate: [ncr-counterpoint-document-model.md, ncr-counterpoint-api-reference.md, ncr-counterpoint-endpoint-spine-map.md]
companion-context: [retail-merchandise-planning-otb.md, retail-po-from-plan.md, retail-promotion-workflow.md, garden-center-operating-reality.md]
companion-canary-spec: Canary-Retail-Brain/modules/J-forecast-order.md
companion-canary-crosswalk: Brain/wiki/canary-module-j-forecast-order.md
companion-catz: CATz/proof-cases/specialty-smb-counterpoint-solution-map.md
methodology-note: "Sister card to canary-module-q/t/r-functional-decomposition.md. First card whose L1 cell is genuinely PARTIAL — stress-tests the format against gap-shaped modules. The OTB / promotion / PO retail process cards are the plan-side source; the Counterpoint Document family is the substrate-side source; the gap between them IS the Canary J opportunity surface."
---

# Module J (Forecast & Order) — Functional Decomposition

> **Artifact layer.** Third of three Canary module artifact layers:
> 1. **Canonical spec** (vendor-neutral) — `Canary-Retail-Brain/modules/J-forecast-order.md`
> 2. **Code/schema crosswalk** (Canary-specific) — `Brain/wiki/canary-module-j-forecast-order.md`
> 3. **Functional decomposition** (Counterpoint-substrate-aware, L2/L3 + user stories) — *this card*

## Governing thesis

J is the **first partial-coverage cell** we've decomposed — and the partial-ness is the point. Counterpoint exposes the *order* side cleanly (POs, PREQs, RECVRs, RTVs all flow through the Document omnibus via DOC_TYP) but exposes **no forecast surface, no replenishment engine, and no OTB management** at the API. Specialty retail buying as Canary defines it requires all three: an OTB pyramid that constrains commitment, a promotion-aware demand model, and a PO chain that ties planning to execution. **The gap between the two is the J opportunity — Canary fills the plan side natively while reading the order side as substrate.**

J is also **the first module that writes back to Counterpoint** in a non-trivial way. Q reads Counterpoint and produces detections inside Canary. T reads Counterpoint and publishes canonical events inside Canary. R reads Counterpoint and curates a privacy-bounded customer registry inside Canary. J's full lifecycle ends with a Counterpoint PO — meaning a Document with DOC_TYP=PO has to land in Counterpoint, either by buyer-entry-in-the-Counterpoint-UI (v2 default, low-coupling) or by Canary-`POST /Document`-back (v3+ option, higher-coupling, requires write-tier API key permissions).

For a Lawn & Garden tenant specifically, the J surface is shaped by three vertical realities: (1) **vendor data quality is heterogeneous** — large nurseries are EDI-capable, mid-tier growers are PDF/email, hobbyist suppliers are cash-and-paper; (2) **item lifecycle is short and seasonal** — replenishment forecasting on a stable SKU base is the wrong mental model; (3) **promotional demand isolation is non-trivial** — every spring-promotion lift must be quarantined from the next-year base forecast or replenishment double-orders.

## Executive summary

| Dimension | Count | Source |
|---|---|---|
| L2 process areas | 8 | This card |
| L3 functional processes | 47 | This card |
| Counterpoint endpoints in J's path | 5 (Document POST/GET, VendorItem, Inventory_ByLocation, Items_ByLocation) | API reference |
| Document types J type-routes | 4 (PO, PREQ, RECVR, RTV) | Document model + Workgroup numbering |
| Canary-native L2 areas (no Counterpoint coverage) | 3 (J.1 forecasting, J.2 replenishment params, J.3 OTB) | Solution Map gap |
| Counterpoint-substrate L2 areas | 3 (J.5 PO generation, J.6 receiving, J.7 RTV) | Document family |
| Cross-cutting L2 areas | 2 (J.4 recommendation+approval, J.8 contracts) | Bridges |
| Substrate contracts J owes downstream | 11 | This card §J.8 |
| Assumptions requiring real-customer validation | 14 | Tagged `ASSUMPTION-J-NN` |
| User stories enumerated | 68 | Observer + actor mix; cast in §Operating notes |

**Posture:** archetype-shaped against Counterpoint specifically, with explicit accommodation for the gap between canonical retail planning and Counterpoint's UI-only replenishment engine. The L2 split below makes the Canary-native vs Counterpoint-substrate distinction load-bearing — every L3 declares which side it's on.

## L1 → L2 → L3 framework

```
L1 (Solution Map cell)         J = ◐ Partial
                                 │  (Counterpoint covers PO/PREQ/RECVR/RTV via Document;
                                 │   forecasting + replenishment params + OTB are gaps)
                                 │
L2 (Process areas)               ├── J.1  Demand forecasting        ★ Canary-native (gap)
                                 ├── J.2  Replenishment parameters  ★ Canary-native (gap)
                                 ├── J.3  Open-to-Buy management    ★ Canary-native (gap; cross-cut with P)
                                 ├── J.4  PO recommendation + approval  bridge (Canary plan → Counterpoint PO)
                                 ├── J.5  PO generation + transmission  ◐ Counterpoint-substrate (Document POST or buyer-UI)
                                 ├── J.6  Receiving + three-way match   ◐ Counterpoint-substrate (DOC_TYP=RECVR)
                                 ├── J.7  Short-ship + RTV handling     ◐ Counterpoint-substrate (DOC_TYP=RTV)
                                 └── J.8  Promotional-demand isolation + cross-module contracts
                                 │
L3 (Functional processes)       (47 — enumerated per L2 below)
                                 │
L4 (Implementation detail)      Canary-Retail-Brain/modules/J-forecast-order.md
                                  + canary-module-j-forecast-order.md (schema)
                                  + future Canary/docs/sdds/v2/forecast.md
```

## J.1 — Demand forecasting

**Coverage posture.** ★ Canary-native (gap). Counterpoint exposes no forecast endpoint. Replenishment recommendations in Counterpoint are UI-only and rule-based, not statistically derived. Canary fills this end-to-end.

**Companion cards.** `retail-merchandise-planning-otb` (the planning pyramid Canary operates against), `Canary-Retail-Brain/modules/J-forecast-order.md` (canonical spec), `canary-module-j-forecast-order.md` (schema crosswalk).

### L3 processes

| ID | L3 process | Substrate read | Notes |
|---|---|---|---|
| J.1.1 | Read movement history per item per location | T's `Events.transactions` + `Events.transaction_lines` (sales) + D's `Events.transfers/receivers/RTVs` (movements) over trailing 12-26 weeks | Demand-derivation input data |
| J.1.2 | Calculate demand velocity (units/day, units/week) per item per location | Movement history aggregation | Per-`(item, location)` velocity |
| J.1.3 | Calculate demand variance (stable / variable / volatile classification) | Movement history variance | Drives safety-stock decision in J.2 |
| J.1.4 | Produce 13-week rolling forecast per item per location | Velocity + variance + (later) seasonal model | Stationary at v2; seasonal at v2.1 |
| J.1.5 | Hierarchy-volatility-aware forecasting | S's category hierarchy + history-of-hierarchy-assignments | Per retail-planning § "hierarchy reorganizations break historical comparability" — when a style moves categories mid-season, history must be restated |
| J.1.6 | Like-item forecasting for new SKUs | C's item attributes + S's category for like-item lookup | New garden-center items mid-season have no history; use category-average velocity scaled by attributes. → TBD: L4 — like-item lookup algorithm: weighted average of comparables by category + velocity band; comparables selection criteria TBD per L4 spec. |
| J.1.7 | Per-channel demand attribution | T's transaction `EC` flag + Document `EC` indicators | Online vs in-store demand split for omnichannel forecast |
| J.1.8 | Forecast accuracy tracking (MAPE, bias) | Prior forecasts vs actual sales | Per `forecast_results` schema; feeds parameter retuning |

### User stories

- *As the Forecast Engine, I want a 13-week demand forecast per `(item, location)` recalculated daily, with low/mid/high scenarios, so PO recommendations carry uncertainty bounds not just point estimates.*
- *As the Forecast Engine, I want to detect when an item's category assignment has changed and restate prior history to the new category, so plan-vs-actual comparisons aren't broken by hierarchy reorganizations.*
- *As a Garden-Center Buyer in Owl, I want to ask "what's my forecast for perennials at the Glendora store next 4 weeks" and get a per-week unit projection drillable to per-item.*
- *As an Operator, I want to see per-`(item, location)` MAPE for the last 90 days so I can identify forecasts that are systematically wrong and trigger parameter retuning.*
- *As a Buyer dealing with new mid-season SKUs (a hobbyist grower drops off 30 flats of an unusual perennial), I want like-item forecasting to give me a starting point so the new item has a forecast immediately, not after 4 weeks of history.*

## J.2 — Replenishment parameter calculation

**Coverage posture.** ★ Canary-native (gap). Counterpoint allows manual ROP entry per item but does not calculate or maintain it from demand signal.

**Companion cards.** `retail-po-from-plan` (replenishment for NOS items), `Canary-Retail-Brain/modules/J-forecast-order.md` (canonical spec), `canary-module-j-forecast-order.md` (`replenishment_params` schema).

### L3 processes

| ID | L3 process | Inputs | Notes |
|---|---|---|---|
| J.2.1 | Calculate Reorder Point (ROP) per `(item, location)` | velocity (J.1.2) × supplier lead time + safety stock (J.2.3) | Initial value buyer-set; auto-recalculated after N months actual data |
| J.2.2 | Calculate Economic Order Quantity (EOQ) per `(item, location)` | EOQ formula + vendor-pack minimum + minimum-order-value | Never below vendor pack minimum |
| J.2.3 | Calculate Safety Stock per `(item, location)` | Demand variance (J.1.3) + lead-time variance + service-level target | Higher for volatile-demand items + variable-lead-time vendors |
| J.2.4 | Maintain Weeks-of-Supply target per category | Buyer-set per category | Drives ROP and safety stock jointly per retail-planning §  |
| J.2.5 | Counter stock exclusion | Per-store buyer-specified counter stock quantity | Excluded from "available SOH" for replenishment calc — display fixtures, testers, seasonal displays |
| J.2.6 | Lead-time variance modeling | Supplier consistency tracking per vendor | → v2.1 deferred: L4 — lead-time variance model (exponential smoothing with seasonal adjustment); fallback: rolling 13-week average lead time per vendor. See ASSUMPTION-J-04. |
| J.2.7 | Pre-pack-aware EOQ | Vendor pre-pack assortment definition | Order quantities round to pre-pack multiples for branded-vendor items |

### User stories

- *As the ROP Calculator, I want every `(item, location)` to have ROP recalculated monthly based on trailing demand + current lead time + chosen safety stock, with the calculation breakdown visible to buyers.*
- *As the EOQ Calculator, I want to never recommend a quantity below the supplier's minimum vendor pack — order generation should round up to the next pack multiple.*
- *As a Garden-Center Buyer, I want counter-stock per store excludable from "available" so the display perennials at the storefront don't trigger spurious replenishment.*
- *As a Buyer working with a hobbyist grower who shows up randomly with whatever's in season, I want to flag the vendor as "high-variability lead time" so safety stock is wider for items sourced from them.*

## J.3 — Open-to-Buy management

**Coverage posture.** ★ Canary-native (gap). Counterpoint has no OTB endpoint or budget structure at the API. OTB is a planning concept Canary brings to the Counterpoint substrate.

**Companion cards.** `retail-merchandise-planning-otb` (OTB definition + state changes + approval gates), cross-cuts with P (Pricing/Promotion).

**Why J owns this and not P.** OTB is the budget side of order recommendation. P maintains the seasonal plan and the budget definition; J is the consumer that validates every PO recommendation against remaining OTB headroom. **This is the load-bearing cross-module contract between P and J.**

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| J.3.1 | Read OTB budget per `(department, period)` from P's seasonal plan | P-derived | Per retail-planning § "Seasonal Merchandise Plan (Department/Category)" |
| J.3.2 | Calculate committed receipts per `(department, period)` | Sum of PO line costs by receipt month | Subtracts from OTB to compute remaining headroom |
| J.3.3 | Compute remaining OTB headroom (rolling) | OTB − committed receipts ± actuals adjustments | The rolling operating forecast |
| J.3.4 | OTB preview before PO commit | J.4 — recommendation displays OTB impact before buyer commits | Known failure mode in legacy systems: OTB consumed at save without preview, forcing the buyer to discover overcommit after the fact |
| J.3.5 | OTB state-change events | PO commit / cancel / sales-vs-plan delta / markdown execute | All affect remaining OTB |
| J.3.6 | OTB approval gate routing | Buyer threshold → dept head → VP merch → finance | Multi-tier escalation; per-role dollar threshold; finance involvement when vendor co-op funds in play |
| J.3.7 | Locked-period override | Once a plan period is locked, changes require override approval | Audit-logged |

### User stories

- *As J's OTB Validator, I want to compute remaining OTB headroom per `(department, receipt-month)` updated in real-time as POs commit and cancel.*
- *As a Buyer drafting a PO, I want to see "if I commit this, your remaining May OTB for perennials is $X" before I click commit — not after.*
- *As a VP of Merchandising in Owl, I want to ask "show me OTB usage by department this season" and get the rolling burn-down with projected end-of-season position.*
- *As a Department Head, I want POs above my buyer's threshold to route to me automatically with the OTB-impact context, so approval isn't a separate workflow.*
- *As Canary's Product Owner, I want OTB to be explicitly cross-cut with P's seasonal plan — both modules must reference the same plan definition; drift between them silently breaks the budget loop.*

## J.4 — PO recommendation + approval workflow

**Coverage posture.** Bridge — Canary computes the recommendation (Canary-native), Counterpoint receives the resulting PO (substrate). The bridge is buyer-mediated at v2, optionally Canary-`POST /Document`-mediated at v3+.

**Companion cards.** `retail-po-from-plan` (PO generation chain), `Canary-Retail-Brain/modules/J-forecast-order.md` (PO-recommendation workflow), `canary-module-j-forecast-order.md` (`po_recommendations` schema).

### L3 processes

| ID | L3 process | Side | Notes |
|---|---|---|---|
| J.4.1 | Detect below-ROP items per scan | Canary-native (J.2.1 + ledger SOH) | Projected on-hand = SOH + on-order − expected sales over lead time |
| J.4.2 | Generate PO recommendation per `(supplier, receipt-week)` bundle | Canary-native | Bundles same-supplier same-week items into one recommendation; respects EOQ from J.2.2 |
| J.4.3 | OTB headroom validation per recommendation | J.3.4 | Recommendation marked `otb_validated=Y/N` with available headroom inline |
| J.4.4 | Recommendation prioritization | Canary-native | Below-ROP severity ordering (how-far-below-ROP, days-of-supply-remaining) |
| J.4.5 | Buyer review + accept/modify/reject | Canary-native UI / MCP / Owl | Buyer adjusts quantity, supplier, receipt date inline; rejection captures reason |
| J.4.6 | Multi-tier approval routing | Canary-native (mirrors J.3.6) | Buyer threshold → dept head → VP merch; approval state machine |
| J.4.7 | Auto-commit threshold (per-tenant configurable) | Canary-native | Recommendations below $threshold optionally auto-commit; default off |
| J.4.8 | What-if simulation | Canary-native (planner role) | Simulate "if I bump safety stock 20% on this category, what happens to next month's PO recs" |

### User stories

- *As the PO Recommender, I want to bundle below-ROP items by `(supplier, receipt-week)` so a single supplier doesn't get 20 separate POs in a week.*
- *As a Buyer in Owl, I want to ask "what should I order from supplier X this week?" and get a structured list with quantity-rationale, OTB-impact, lead-time, drillable to per-item velocity.*
- *As a Buyer reviewing a recommendation, I want to modify quantity inline (bump the perennials order from 20 flats to 30 because of the holiday weekend) and see OTB impact recompute live.*
- *As a Department Head, I want a daily digest of recommendations awaiting my approval, sorted by OTB-impact + below-ROP severity, with one-click approve/modify.*
- *As a Planner in Owl, I want what-if simulation: "if I increase safety stock 20% on the perennials category, what does next week's PO recommendation look like?" — without committing anything.*

## J.5 — PO generation + transmission

**Coverage posture.** ◐ Counterpoint-substrate. Once a recommendation is approved, it becomes a Counterpoint Document with DOC_TYP=PO. Two paths: **buyer enters in Counterpoint UI** (v2 default — Canary tracks the recommendation→entered transition by polling for new PO Documents) or **Canary `POST /Document`** (v3+ — requires write-tier API key + reconciliation between Canary recommendation_id and Counterpoint PO_NO).

**Companion cards.** `ncr-counterpoint-document-model` (POST /Document, Workgroup `NXT_PO_NO`), `retail-po-from-plan` (pre-distributed vs bulk PO patterns).

### L3 processes

| ID | L3 process | Path | Notes |
|---|---|---|---|
| J.5.1 | Buyer-entered-in-Counterpoint path (v2 default) | Buyer takes recommendation to Counterpoint UI; enters PO; Canary detects new PO via T's poll loop | Loose coupling; recommendation_id reconciled to PO_NO via heuristic match (supplier + items + window) |
| J.5.2 | Canary-POST-Document path (v3+) | Canary calls `POST /Document` with DOC_TYP=PO + lines + allocation; Counterpoint returns DOC_ID | Tight coupling; reconciliation deterministic; requires write-tier API key |
| J.5.3 | PO header generation | Total cost, total retail, markup %, DC identifier, terms, cancellation date | Per retail-planning § "Purchase Order Contents" — header section |
| J.5.4 | PO line generation | Cost/retail/margin per unit, cancellation date per line, allocation summary | Per retail-planning § "Purchase Order Contents" — line section |
| J.5.5 | Pre-distributed PO with allocation attached | Allocation table set before vendor transmission; vendor packs by store; cross-dock at DC | The pattern for branded vendors and cross-dock-capable suppliers |
| J.5.6 | Bulk PO with allocation deferred | PO total committed; allocation at DC receiving | The pattern for warehouse-and-pick distribution; default for SMB |
| J.5.7 | EDI transmission to vendor | (External — outside Counterpoint API) | Counterpoint API doesn't carry EDI; standalone EDI integration; out of v2 scope |
| J.5.8 | New article creation at PO entry | Buyer at trade show creates PO before article master exists | Counterpoint workflow; Canary surfaces this through C's article-creation contract |
| J.5.9 | PO change message on allocation revision | Allocation change after PO transmission | Triggers EDI PO-change to vendor when EDI in play |

### User stories

- *As a Buyer at v2, I want to take an approved Canary recommendation, copy the structured details (supplier, items, quantities, dates) into my Counterpoint PO entry screen, and have Canary recognize the resulting PO via the next poll cycle and link it back to my recommendation.*
- *As Canary's Product Owner at v3, I want optional `POST /Document`-back so high-volume tenants can skip the buyer-typing step entirely, with explicit per-tenant opt-in and write-tier credential capture.*
- *As an Operator, I want unmatched recommendations (recommendation approved 7 days ago, no Counterpoint PO appeared) flagged so the buyer-driven entry isn't silently lost.*
- *As a Buyer at a fashion-adjacent garden retailer, I want new-article-at-PO creation supported — when a hobbyist grower brings an unknown perennial cultivar, I can create the PO and the article master in one workflow.*

## J.6 — Receiving + three-way match

**Coverage posture.** ◐ Counterpoint-substrate. Receivers flow as Documents with DOC_TYP=RECVR, automatically polled by T. Three-way match (PO + receipt + invoice) reconciles cost flow into F.

**Companion cards.** `ncr-counterpoint-document-model` (DOC_TYP=RECVR, Workgroup `NXT_RECVR_NO`), `retail-po-from-plan` (allocation-to-PO + short-ship), `garden-center-operating-reality` (thin-metadata receivers as normal, not anomalous).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| J.6.1 | Detect new receiver Documents | T's poll loop (DOC_TYP=RECVR) | Routes to J's receiving subscriber per T.4.7 |
| J.6.2 | Match receiver to PO via `PS_DOC_HDR_ORIG_DOC` | T.7.2 (T's contract) | If link present, deterministic match; if absent, heuristic match by vendor + items + window |
| J.6.3 | Quantity reconciliation | Receiver line qty vs PO line qty | Discrepancy threshold flags Q-IS-01 (receiver-vs-PO discrepancy) |
| J.6.4 | Cost reconciliation | Receiver landed cost vs PO line cost | Variance posts to F's GL adjustment |
| J.6.5 | OTB closeout | Receiver completes the PO's OTB consumption (in-progress → realized) | Updates J.3.3 remaining headroom |
| J.6.6 | Forecast accuracy feedback | Actual receipt date vs requested date | Feeds J.1.8 forecast-accuracy tracking + supplier-lead-time-variance tracking (J.2.6) |
| J.6.7 | Thin-metadata receiver tolerance | Garden-center reality: hand-typed receivers may have missing/default fields | Flag-and-ingest, not reject — per garden-center wiki § "Receivers with thin metadata are normal" |
| J.6.8 | Cash-paid receiver classification | Receivers with PayCode=CASH | Routes to ad-hoc-vendor-payment review queue per Q-IS-02 — NOT fraud queue |

### User stories

- *As J's Receiver subscriber, I want every new Document with DOC_TYP=RECVR matched to its originating PO via `PS_DOC_HDR_ORIG_DOC` deterministically when present, with heuristic fallback when absent.*
- *As J, I want quantity discrepancies (received vs ordered) above threshold to fire a Q-IS-01 detection AND trigger a Canary-side allocation revision (J.7.x short-ship handling).*
- *As J, I want every receiver to complete the OTB closeout so the seasonal-plan vs realized-receipts loop closes cleanly.*
- *As a Garden-Center Buyer, I want hand-typed receivers from cash-paid specialty growers to be ingested even when fields are sparse — the recommendation is "flag and review," not "reject and silently lose the record."*
- *As an Operator, I want supplier-lead-time-variance auto-updated from receipt-vs-requested-date deltas, so safety-stock recommendations evolve as supplier consistency changes.*

## J.7 — Short-ship + RTV handling

**Coverage posture.** ◐ Counterpoint-substrate. Short-ship triggers re-allocation; RTV flows as DOC_TYP=RTV. Both feed back into J.3 (OTB headroom restoration) and J.1 (demand-forecast adjustment for items that didn't actually arrive).

**Companion cards.** `retail-po-from-plan` (short-ship + NOS replenishment), `ncr-counterpoint-document-model` (DOC_TYP=RTV, Workgroup `NXT_RTV_NO`).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| J.7.1 | Short-ship detection | J.6.3 quantity reconciliation flags shortfall | Triggers re-allocation flow |
| J.7.2 | Re-allocation logic on short-ship | Tier-aware: protect top-tier stores first; proportional remainder; bottom-tier may receive zero | Default proportional reduction is **wrong for SMB** — implement tier-aware logic |
| J.7.3 | PO change message for cancelled balance | Standard back-order vs cancel decision | Cancel remaining quantity per buyer instruction |
| J.7.4 | RTV recommendation generation | Damaged goods, vendor-quality issues, return-to-vendor | Buyer-initiated; substrate flows as DOC_TYP=RTV |
| J.7.5 | RTV impact on OTB | Restores OTB headroom for the affected receipt period | J.3.5 OTB state-change |
| J.7.6 | RTV reason-code tracking | Per RTV reason; aggregates to vendor-quality signal | Feeds Q-IS-* (vendor-quality patterns) and supplier scorecard |
| J.7.7 | Dead-count / live-goods write-off (garden-center-specific) | Likely DOC_TYP=RTV with reason code OR separate adjustment workflow (**ASSUMPTION-J-12**) | Counterpoint convention undocumented; tracked against seasonal baseline per Q-IS-04 |

### User stories

- *As J, I want short-ship re-allocation to default to tier-aware logic (top-tier stores protected, proportional reduction below) — naive proportional reduction systematically underserves small-volume stores, which is the wrong default for SMB.*
- *As J, I want every cancelled PO balance from short-ship to restore OTB headroom and trigger the next replenishment scan with the corrected on-order quantity.*
- *As a Garden-Center Buyer dealing with a delivery of perennials where 30% arrived dead, I want RTV creation with a "live-goods spoilage" reason code that the system tracks against seasonal baseline — not as a vendor-quality signal.*
- *As an LP Analyst (Q.6), I want vendor-quality patterns (high-RTV-rate per supplier per item) surfaced, with garden-center seasonal-spoilage allow-listed.*

## J.8 — Promotional-demand isolation + cross-module substrate contracts

**Purpose.** Two distinct concerns share this L2 because both are cross-module: (1) promotional demand isolation (cross-cut with P), and (2) the substrate contract registry to D/F/P/T.

### J.8a — Promotional-demand isolation (cross-cut with P)

**Companion cards.** `retail-promotion-workflow` (promotion + replenishment integration).

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| J.8.1 | Read promotion calendar from P | P's `promotions` table | Replenishment must know about active + planned promotions on each item |
| J.8.2 | Quarantine promotional lift from base demand | Tag transactions with promotion ID at parse; J reads tagged-vs-untagged separately | Promotional lift must never inflate the base forecast used for next-cycle replenishment |
| J.8.3 | Recurring-promotion blending | Per-item config: "include in base" vs "smooth out of base" | Same week every year → include; one-time → smooth |
| J.8.4 | Pre-promotion demand projection | Add planned promotional demand to forecast horizon | Avoids replenishment double-ordering during promo windows |

### J.8b — Substrate contract registry (symmetric to T.7, R.6, Q.1)

| ID | Contract | Owner downstream | What J promises |
|---|---|---|---|
| J.8.5 | PO recommendations as event substrate | F (formal PO commitment), Q (recommendation-vs-actual auditing) | Every recommendation persisted with snapshot inputs; not regenerated on parameter change |
| J.8.6 | Forecast snapshot per recommendation | Future audit / compliance | Forecast version + parameters used at recommendation time |
| J.8.7 | OTB validation outcome inline | F (commit gating), Buyer review | Recommendation carries `otb_validated` boolean + `available_headroom` inline |
| J.8.8 | Per-recommendation buyer modifications captured | Audit trail | Original recommendation + buyer modifications + final approved PO all linked |
| J.8.9 | Receiver→PO match status | F (three-way match), Q (Q-IS-01) | Match outcome (deterministic / heuristic / unmatched) preserved per receiver event |
| J.8.10 | Lead-time-variance per supplier | J.2.6 self-feedback + supplier scorecard | Aggregated across receivers; updated per receipt event |
| J.8.11 | Demand-forecast snapshot for accuracy tracking | J.1.8 self-feedback | Per `(item, location, period)` forecast-vs-actual preserved indefinitely |

**Cross-module dependency notes (load-bearing):**

- **F.5.2 dependency (load-bearing):** J replenishment costing reads PO cost-flow data from F.5.2. F must publish cost-flow records before J can produce cost-accurate replenishment recommendations.
- **P.6.3 dependency (load-bearing per J.8a):** J demand forecasting requires P.6.3 promotion calendar contract to hold. Promotional demand must be isolated before baseline forecast is computed. See Module P §P.6.3.

### User stories

- *As J's Forecast Engine, I want to read P's promotion calendar and quarantine promotional lift from the base demand series, so post-event forecasts aren't inflated by one-time promotions.*
- *As J's PO Recommender, I want to add planned promotional demand to the forecast horizon for any active or planned promotion, so I don't generate a normal replenishment order at the same time a promotional order is being planned.*
- *As Canary's Product Owner, I want every J↔P contract (J.8.1 + J.8.4 + R-from-P promotion calendar contract) tested in the contract suite so promotional-vs-base-demand integration doesn't silently break.*
- *As an Auditor, I want every PO recommendation to carry the forecast version + parameters used at recommendation time, so retroactive parameter changes don't invalidate the audit trail.*

## Assumptions requiring real-customer validation

| ID | Assumption | What it blocks | Resolution path |
|---|---|---|---|
| ASSUMPTION-J-01 | PO Document type code — likely `PO`; Workgroup numbering confirms `NXT_PO_NO` | J.5 entire substrate path; T-01 dependency | Sandbox or sample PO Document inspection |
| ASSUMPTION-J-02 | PREQ vs PO distinction — purchase request workflow | J.4 approval routing (does PREQ exist as a Counterpoint state, or is it Canary-internal-only) | Sandbox workflow test |
| ASSUMPTION-J-03 | RECVR Document linkage to PO via `PS_DOC_HDR_ORIG_DOC` — assumed but unconfirmed | J.6.2 deterministic match | Sandbox workflow test |
| ASSUMPTION-J-04 | RTV Document reason-code field — schema location | J.7.6 reason tracking; Q-IS feedback | Sandbox DB inspection |
| ASSUMPTION-J-05 | Vendor master via `VendorItem` — single endpoint; full vendor record may live in `AP_VEND` (not exposed?) | J vendor-data completeness; supplier-scorecard fidelity | API doc deep-read; possibly direct-DB fallback |
| ASSUMPTION-J-06 | OTB representation in Counterpoint — believed UI-only / spreadsheet-only | J.3 entire L2 (Canary-native confirmed) | Customer interview; if customer maintains OTB in Counterpoint custom tables, path differs |
| ASSUMPTION-J-07 | Per-customer category margin targets (`MIN_PFT_PCT`, `TRGT_PFT_PCT`) actually tuned, or default values | J.1 like-item forecasting needs realistic margin context | Tenant onboarding |
| ASSUMPTION-J-08 | Buyer-driven PO entry workflow at v2 — does buyer copy from Canary or rekey | J.5.1 v2 path UX assumption | Real customer workflow observation |
| ASSUMPTION-J-09 | Write-tier API key feasibility for v3 `POST /Document` path | J.5.2 entire path | NCR partner / customer permission negotiation |
| ASSUMPTION-J-10 | Pre-pack vendor coverage in L&G vertical — branded vendors common, but unclear if dominant | J.5.5 pre-distributed PO L3 priority | Customer interview |
| ASSUMPTION-J-11 | EDI transmission scope — most L&G customers do NOT have EDI; manual phone/email/fax | J.5.7 likely deferred indefinitely for SMB L&G | Customer interview |
| ASSUMPTION-J-12 | Dead-count / live-goods write-off Document type — RTV with reason, separate adjustment workflow, or other (same as ASSUMPTION-Q-05) | J.7.7 entire substrate path; Q-IS-04 | **Real garden-center customer DB** |
| ASSUMPTION-J-13 | Promotion calendar in Counterpoint vs Canary — Counterpoint has no promotion endpoint family per api-reference | J.8.1 read-from-P assumes P maintains the calendar Canary-side | Confirms Canary-native P; no Counterpoint conflict |
| ASSUMPTION-J-14 | Supplier lead time field on item or vendor — schema location | J.2.1 ROP calculation | Sandbox DB inspection |

**Highest-leverage gaps:** J-06 (OTB representation) and J-08 (buyer workflow at v2). J-06 is the load-bearing assumption for the entire J.3 L2; if a customer maintains OTB in Counterpoint custom tables (Rapid POS proprietary extension), Canary's J.3 path changes from "build OTB from scratch" to "ingest customer's existing OTB." J-08 is the load-bearing UX assumption for v2; if buyers won't tolerate copy-from-Canary-then-enter-in-Counterpoint, v3 `POST /Document` becomes urgent rather than optional.

## Customer-specific overrides

*Empty until a real customer engagement starts. Format reserved:*

```
Customer: <name>
PO entry path: <buyer-via-Counterpoint-UI | Canary POST_Document | hybrid>
Write-tier API key: <granted | denied | not-yet-requested>
OTB management: <Canary-native | Counterpoint custom tables | spreadsheet-side>
EDI in play: <yes — vendor list | no>
Pre-pack vendor coverage: <% of $ / % of vendors>
Per-tenant auto-commit threshold: <$X | disabled (default)>
Demand-forecast cadence: <daily | weekly | manual-only>
Promotional-isolation per category:
  <category>: <include in base | smooth out>
Disabled J.x processes (with reason):
  J.x.x: <reason>
ASSUMPTION resolutions:
  ASSUMPTION-J-NN: resolved as <answer>; source: <evidence>
  ...
```

## Operating notes

**Cast of actors** (J is more populated than Q/T/R):

| Actor | Role | Lives where |
|---|---|---|
| Forecast Engine | Demand projection service | Canary-internal (J.1) |
| ROP Calculator | Replenishment parameter service | Canary-internal (J.2) |
| OTB Validator | Headroom-check service | Canary-internal (J.3) |
| PO Recommender | Recommendation generator | Canary-internal (J.4) |
| Buyer / Merchandiser | Human-in-the-loop, approves recommendations | Customer org |
| Department Head / VP Merch | Multi-tier approval | Customer org |
| Receiver subscriber | Three-way-match service at goods-in | Canary-internal (J.6) |
| Owl / Fox | Analyst-facing surface | Canary-internal (J.4 + J.6 surfaces) |
| Counterpoint Document writer | Optional `POST /Document` writer at v3+ | Canary-internal (J.5.2) |

**The partial-coverage cell drives the L2 split.** J's L2 explicitly tags Canary-native vs Counterpoint-substrate vs bridge for each area. This pattern should generalize to any other ◐ Partial cells (P-derived, A-derived, C-derived) — the format earns its keep precisely because gap-shaped modules need this distinction load-bearing.

**The OTB / PO / promotion process trio gives plan-shaped modules a stable L2 backbone.** The pyramid, chain, and lifecycle aren't aspirational — they're the operating shape Canary commits to. Future module cards (P, S in particular) reference the same three companion cards because the patterns are shared, not because the source is.

**The buyer-mediated v2 path is the load-bearing UX assumption.** Until a real customer can confirm buyers will tolerate "review recommendation in Canary, then enter PO in Counterpoint," J's actual deployment shape is uncertain. If they won't, v3 `POST /Document` becomes the v2 default. This is the single highest-priority discovery question for any first L&G customer.

## Related

- `Canary-Retail-Brain/modules/J-forecast-order.md` — L1 canonical spec (CRDM, ledger relationship, agent surface, security posture)
- `canary-module-j-forecast-order.md` — L2 Canary code/schema crosswalk (projected tables, code surface, SDD crosswalks)
- `canary-module-q-functional-decomposition.md` — sister card; J.6.3, J.6.8, J.7.6 connect to Q-IS-* rules
- `canary-module-t-functional-decomposition.md` — sister card; T.7.6 (DOC_TYP routing) and T.7.2 (original-doc-ref) are J.5/J.6 prerequisites
- `canary-module-r-functional-decomposition.md` — sister card; R's vendor-as-People surface (limited in Counterpoint API) cross-cuts with C
- `retail-merchandise-planning-otb.md` — planning pyramid + OTB; companion to J.1/J.2/J.3
- `retail-po-from-plan.md` — PO chain; companion to J.4/J.5/J.6/J.7
- `retail-promotion-workflow.md` — promotion lifecycle; companion to J.8a (cross-cut with P)
- `ncr-counterpoint-document-model.md` — Document substrate detail; DOC_TYP=PO/PREQ/RECVR/RTV
- `ncr-counterpoint-api-reference.md` — Counterpoint J coverage (sparse: VendorItem + Document family); confirms no forecast endpoint
- `ncr-counterpoint-endpoint-spine-map.md` — VendorItem placement in C+J seam
- `garden-center-operating-reality.md` — vendor data quality, item-code drift, dead-count workflow context
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — J row = ◐ Partial; this card is the L2/L3 expansion of that cell
- (CATz, proposed) `method/artifacts/module-functional-decomposition.md` — the artifact template this card stress-tests against partial-coverage shape

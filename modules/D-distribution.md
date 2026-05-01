---
title: D — Distribution
nav_order: 3
classification: internal
type: wiki
sub-type: module-functional-decomposition
date: 2026-04-26
last-compiled: 2026-04-26
module: D
solution-map-cell: ◐ Partial — per-location inventory snapshots direct; transfer workflow via Document omnibus (DOC_TYP=XFER); transfer-loss detection and multi-store distribution recommendations are Canary-native
companion-modules: [T, F, O, Q, C]
companion-substrate: [ncr-counterpoint-document-model.md, ncr-counterpoint-api-reference.md, ncr-counterpoint-endpoint-spine-map.md]
companion-context: [retail-merchandise-planning-otb.md, retail-po-from-plan.md, garden-center-operating-reality.md]
companion-canary-spec: Canary-Retail-Brain/modules/D-distribution.md
companion-canary-crosswalk: Brain/wiki/canary-module-d-distribution.md
companion-catz: CATz/proof-cases/specialty-smb-counterpoint-solution-map.md
methodology-note: "Sister card to j, c, p, a functional-decomp cards. Most ledger-centric v2 module — D is the primary publisher of stock-ledger movements. Counterpoint's per-location inventory endpoint family supplies the snapshot substrate; transfer workflow flows through the Document omnibus (no dedicated endpoint); transfer-loss reconciliation and multi-store distribution recommendations are the Canary-native gap. The gap-shape IS the D opportunity surface."
---

# Module D (Distribution) — Functional Decomposition

> **Artifact layer.** Third of three Canary module artifact layers:
> 1. **Canonical spec** (vendor-neutral) — `Canary-Retail-Brain/modules/D-distribution.md`
> 2. **Code/schema crosswalk** (Canary-specific) — `Brain/wiki/canary-module-d-distribution.md`
> 3. **Functional decomposition** (Counterpoint-substrate-aware, L2/L3 + user stories) — *this card*

## Governing thesis

D is the **primary publisher of stock-ledger movements** across the Canary spine — every receipt, transfer, RTV, adjustment, and cycle count originates here. Against the Counterpoint substrate, D's coverage is partial in a revealing way: Counterpoint exposes a rich per-location inventory snapshot surface (`Inventory_ByLocation`, `Items_ByLocation`, `InventoryLocations`, `InventoryControl`, `InventoryCost`) that gives Canary a clear real-time view of *where stock is*, but it exposes **no dedicated transfer endpoint**. Transfers flow through the same Document omnibus that handles sales, returns, and receiving — distinguished only by DOC_TYP=XFER. The gap between "I can see inventory position" and "I can see stock in motion" is where Canary must do real work.

The consequence is a clean L2 split: D.1 and D.2 are high-confidence substrate reads; D.3 is substrate-via-Document-type-routing (reliable but indirect); D.4 and D.5 are Canary-native gaps — transfer-loss reconciliation and multi-store distribution recommendations have no Counterpoint analog and represent D's distinct contribution at specialty SMB scale. For a garden-center operator managing 3-8 locations, getting stock from the right location to the right store at the right time is the operational problem Counterpoint doesn't solve. D closes it.

## Executive summary

| Dimension | Count | Source |
|---|---|---|
| L2 process areas | 6 | This card |
| L3 functional processes | 35 | This card |
| Counterpoint endpoints in D's path | 7 (`Inventory_ByLocation`, `InventoryControl`, `InventoryCost`, `InventoryEC`, `InventoryLocations`, `Items_ByLocation`, `Item_Inventory`) | API reference |
| Document types D type-routes | 1 (XFER) via Document omnibus | Document model |
| Counterpoint-substrate L2 areas | 3 (D.1 snapshot ingestion, D.2 per-location attribution, D.3 transfer detection) | API reference |
| Canary-native L2 areas (no Counterpoint coverage) | 2 (D.4 transfer-loss reconciliation, D.5 multi-store distribution recommendations) | Solution Map gap |
| Cross-cutting L2 areas | 1 (D.6 substrate contracts) | Downstream consumers |
| Substrate contracts D owes downstream | 9 | This card §D.6 |
| Assumptions requiring real-customer validation | 9 | Tagged `ASSUMPTION-D-NN` |
| User stories enumerated | 38 | Observer + operator mix; cast in §Operating notes |

**Posture:** archetype-shaped against Counterpoint specifically. The snapshot surface is unusually rich for an SMB POS; the transfer surface is indirect-but-workable. Transfer-loss detection and distribution optimization are Canary-native and are the highest-ROI D deliverables for multi-location garden-center operators.

## Counterpoint Endpoint Substrate

| Counterpoint Endpoint | CRDM Entity | L2 Process Area |
|---|---|---|
| Inventory_ByLocation | SOH by location | D.1.1 (SOH ingestion) |
| Items_ByLocation | Item-location catalog | D.1.2 (Item-location mapping) |
| Item_Inventory | Item-level inventory | D.1.3 (Inventory position) |
| InventoryLocations | Location registry | D.2.1 (Location context) |
| InventoryControl | Reorder parameters | D.1.4 (Reorder context) |
| InventoryCost | Cost layer | D.1.5 (Cost-flow substrate to F) |
| InventoryEC | EC inventory | D.1.6 (eCommerce position) |
| PS_DOC (type=XFER) | Transfer documents | D.3.1–D.3.6 (Transfer lifecycle) |

## L1 → L2 → L3 framework

```
L1 (Solution Map cell)         D = ◐ Partial
                                 │  (Counterpoint per-location snapshot endpoints: direct;
                                 │   transfer workflow: indirect via Document XFER;
                                 │   transfer-loss detection + distribution recs: gap)
                                 │
L2 (Process areas)               ├── D.1  Inventory snapshot ingestion    ● Counterpoint-substrate
                                 ├── D.2  Per-location item attribution    ● Counterpoint-substrate
                                 ├── D.3  Transfer detection (XFER)       ◐ Counterpoint-substrate (Document omnibus)
                                 ├── D.4  Transfer-loss reconciliation     ★ Canary-native (gap)
                                 ├── D.5  Multi-store distribution recs   ★ Canary-native (gap)
                                 └── D.6  Cross-module substrate contracts
                                 │
L3 (Functional processes)       (35 — enumerated per L2 below)
                                 │
L4 (Implementation detail)      Canary-Retail-Brain/modules/D-distribution.md
                                  + canary-module-d-distribution.md (schema crosswalk)
                                  + future Canary/docs/sdds/v2/distribution.md
```

## D.1 — Inventory snapshot ingestion

**Coverage posture.** ● Counterpoint-substrate. Counterpoint exposes a richer per-location inventory surface than most SMB POS platforms. Seven endpoints carry per-location quantity, cost, and control data. Canary polls and seals these into the movement ledger as snapshot records.

**Companion cards.** `ncr-counterpoint-api-reference.md` (inventory endpoint group), `ncr-counterpoint-endpoint-spine-map.md` (D-column coverage), `Canary-Retail-Brain/modules/D-distribution.md` (canonical spec).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| D.1.1 | Poll `GET /Inventory_ByLocation` per location on configurable cadence | `Inventory_ByLocation` endpoint | Per-`(item, location)` qty-on-hand snapshot; primary SOH signal → TBD: L4 implementation detail pending |
| D.1.2 | Poll `GET /Items_ByLocation` to reconcile item-location attributions | `Items_ByLocation` endpoint | Confirms which items exist at which locations; catches new-location-item pairs → TBD: L4 implementation detail pending |
| D.1.3 | Poll `GET /Item_Inventory` for item-level aggregate inventory | `Item_Inventory` endpoint | Cross-location rollup; used to validate per-location sum vs. aggregate → TBD: L4 implementation detail pending |
| D.1.4 | Detect and seal SOH deltas into the Canary ledger | Diff between successive snapshots → D's movement ledger | Delta between T-1 and T snapshots that cannot be attributed to a known Document becomes an UNATTRIBUTED-MOVEMENT flag → TBD: L4 implementation detail pending |
| D.1.5 | Reconcile snapshot-vs-Document-derived position | D.1.4 snapshot delta vs. D.3 XFER + O.6 RECVR events | The residual after Document-attributed movements are stripped is the reconciliation surface for D.4 → TBD: L4 implementation detail pending |
| D.1.6 | Handle stale-location responses (Counterpoint location offline or unreachable) | Retry policy, staleness flag on snapshot record | Garden-center locations with poor connectivity produce stale snapshots; flag-and-hold, not reject → TBD: L4 implementation detail pending |

### User stories

- *As D's Snapshot Ingestor, I want per-`(item, location)` SOH polled at a configurable cadence (hourly default), with delta records persisted to the movement ledger, so downstream consumers always have a fresh position.*
- *As D's Reconciler, I want snapshot deltas that cannot be attributed to a known Document (XFER, RECVR, RTV) flagged as UNATTRIBUTED-MOVEMENT so they surface for investigation — shrink or receiving discrepancy, not silently absorbed.*
- *As an Operator, I want stale-location snapshots (location offline > 4 hours) flagged in the dashboard so inventory decisions aren't made against stale data.*

## D.2 — Per-location item attribution

**Coverage posture.** ● Counterpoint-substrate. `InventoryLocations`, `InventoryControl`, and `InventoryCost` give Canary the per-location control parameters (bin/zone, cost method, reorder config) that contextualize raw SOH numbers.

**Companion cards.** `ncr-counterpoint-api-reference.md`, `Canary-Retail-Brain/modules/D-distribution.md`.

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| D.2.1 | Poll `GET /InventoryLocations` to map item-to-location assignments | `InventoryLocations` endpoint | Establishes the set of valid `(item, location)` pairs; drives D.1.1 poll scope → TBD: L4 implementation detail pending |
| D.2.2 | Poll `GET /InventoryControl` for per-item reorder parameters | `InventoryControl` endpoint | Reorder-point and QOH thresholds; feeds O.2.1 (ROP calculation) with substrate baseline → TBD: L4 implementation detail pending |
| D.2.3 | Poll `GET /InventoryCost` for per-item cost basis per location | `InventoryCost` endpoint | Landed cost per location; required for transfer-cost posting and RTV cost reversal → TBD: L4 implementation detail pending |
| D.2.4 | Poll `GET /InventoryEC` for omnichannel inventory flags | `InventoryEC` endpoint | EC (e-commerce) overlay flags; required when merchant has an online channel co-existing with in-store → TBD: L4 implementation detail pending |
| D.2.5 | Detect new item-location pairs and trigger attribution pipeline | D.2.1 set-diff vs. prior poll | New location-item pair triggers S's assortment-validation check before Canary starts tracking → TBD: L4 implementation detail pending |

### User stories

- *As D's Attribution Pipeline, I want `InventoryLocations` polled on a slower cadence (daily default) than SOH, so item-location set changes are detected promptly without over-polling a low-change surface.*
- *As J's ROP Calculator, I want D to surface `InventoryControl.reorder_point` per `(item, location)` as a buyer-set baseline ROP, so O.2.1 can use the Counterpoint value as the starting point before Canary calculates a demand-derived override.*
- *As D, I want new `(item, location)` pairs detected and flagged for assortment validation before tracking begins — a new item arriving at a location it wasn't assigned to is operationally significant.*

## D.3 — Transfer detection (DOC_TYP=XFER)

**Coverage posture.** ◐ Counterpoint-substrate via Document omnibus. Transfers are not a dedicated endpoint family — they flow through the same `GET /Document` poll loop that handles sales tickets, receivers, and RTVs. DOC_TYP=XFER is the discriminator. This is workable but indirect: T's pipeline type-routes Documents; D subscribes to the XFER subscriber.

**Companion cards.** `ncr-counterpoint-document-model.md` (DOC_TYP=XFER, Workgroup `NXT_XFER_NO`), `canary-module-t-functional-decomposition.md` (T.4.7 — Document-type routing).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| D.3.1 | Subscribe to T's Document stream filtered to DOC_TYP=XFER | T.4.7 routing contract | T routes XFER Documents to D's transfer-subscriber; D does not poll Documents directly → TBD: L4 implementation detail pending |
| D.3.2 | Parse XFER Document header (from_location, to_location, transfer date, initiating employee) | `PS_DOC_HDR` fields for DOC_TYP=XFER | Establishes the source-destination pair and time context → TBD: L4 implementation detail pending |
| D.3.3 | Parse XFER Document lines (item, qty, cost) | `PS_DOC_LIN` fields for DOC_TYP=XFER | Per-item transfer units and per-unit cost at time of transfer → TBD: L4 implementation detail pending |
| D.3.4 | Post in-transit inventory hold on transfer initiation | D's `intransit_inventory` table | `-qty from source` ledger; in-transit hold at item + source + destination; clears on RECVR match → TBD: L4 implementation detail pending |
| D.3.5 | Detect transfer completion via paired RECVR Document (ASSUMPTION-D-03) | Cross-reference DOC_TYP=RECVR with originating XFER | Deterministic if `PS_DOC_HDR_ORIG_DOC` is present; heuristic (location + items + window) if absent → TBD: L4 implementation detail pending |
| D.3.6 | Handle transfer-in-transit timeout (no RECVR appears within threshold) | Policy-configurable; default 72 hours | Flag unconfirmed in-transit as TRANSFER-TIMEOUT; route to operations review → TBD: L4 implementation detail pending |

### User stories

- *As D's Transfer Subscriber, I want every XFER Document routed from T's pipeline to create an in-transit hold that debits the source location and creates a pending credit at the destination — not posting the destination receipt until a RECVR arrives to confirm.*
- *As an Operator, I want transfers that have been in-transit more than 72 hours without a confirming RECVR flagged automatically, so "transfers that disappeared between stores" don't just silently become shrink.*
- *As D, I want `PS_DOC_HDR_ORIG_DOC` used for deterministic RECVR-to-XFER matching when present, with heuristic fallback by location + items + date window when absent — and a flag on every heuristic match so auditors can see what was inferred vs. confirmed.*

## D.4 — Transfer-loss reconciliation

**Coverage posture.** ★ Canary-native (gap). Counterpoint records that a transfer was initiated and that stock arrived at the destination; it does not reconcile what was lost in transit or flag systematic loss patterns. That analysis is Canary-native and is the primary Q cross-cut from D.

**Companion cards.** `canary-module-q-functional-decomposition.md` (Q-IS-03 — transfer-loss pattern rule), `garden-center-operating-reality.md` (multi-store transfer reality for L&G operators).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| D.4.1 | Calculate transfer-variance per `(XFER, item)` | XFER qty (D.3.3) vs. RECVR qty (O.6.2) | Variance = initiated qty − received qty per line → TBD: L4 implementation detail pending |
| D.4.2 | Classify transfer variance by type | Threshold rules: minor (< tolerance), significant (> threshold), zero-receipt | Zero-receipt on confirmed in-transit is the most severe classification → TBD: L4 implementation detail pending |
| D.4.3 | Detect systematic transfer-loss patterns per route or item | Canary-native aggregation over D.4.1 | Pattern = recurring variance on same from_location → to_location pair; feeds Q-IS-03 → TBD: L4 implementation detail pending |
| D.4.4 | Reconcile unattributed SOH deltas (D.1.4 residual) against XFER candidates | Snapshot delta vs. Document accounting | Residuals after known XFER/RECVR/RTV accounting may indicate undocumented transfers → TBD: L4 implementation detail pending |
| D.4.5 | Route high-variance transfers to investigation queue | Canary-native alert → Q's alert pipeline | Variance above threshold fires Q alert with D.4.1 evidence → TBD: L4 implementation detail pending |
| D.4.6 | Allow-list seasonal-movement patterns | Per-tenant config (e.g., end-of-season store-consolidation transfers have expected high variance) | Garden-center seasonal close-outs: large transfers with partial live-goods that don't survive; allow-list vs. flag → TBD: L4 implementation detail pending |

### User stories

- *As D's Variance Calculator, I want every XFER-RECVR pair compared line-by-line for quantity discrepancy, with the variance posted as a TRANSFER-VARIANCE record that feeds Q-IS-03 accumulation.*
- *As an LP Analyst (Q.6), I want transfer-loss patterns aggregated by route: "transfers from Warehouse A to Store B have a 12% loss rate on live plants — is this spoilage or pilferage?" surfaced as a pattern detection, not a per-transaction alert.*
- *As an Operator, I want large end-of-season consolidation transfers allow-listed for the Q-IS-03 rule — moving all remaining stock from three seasonal stores back to the warehouse legitimately looks like transfer-loss if you don't account for live-goods spoilage.*

## D.5 — Multi-store distribution recommendations

**Coverage posture.** ★ Canary-native (gap). Counterpoint exposes inventory position; it provides no distribution-optimization or cross-location rebalancing recommendation. Canary builds these natively by combining D.1's snapshot surface with J's demand forecast.

**Companion cards.** `retail-merchandise-planning-otb.md` (allocation methods), `canary-module-o-functional-decomposition.md` (O.1 demand forecast as input), `garden-center-operating-reality.md` (multi-store transfer reality).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| D.5.1 | Calculate excess stock per `(item, location)` | D.1.1 SOH − O.2 (ROP + safety stock target) | Excess = SOH beyond the weeks-of-supply target for that item at that location → TBD: L4 implementation detail pending |
| D.5.2 | Calculate deficit stock per `(item, location)` | O.2.1 ROP − D.1.1 current SOH | Deficit = SOH below ROP at the location → TBD: L4 implementation detail pending |
| D.5.3 | Match excess at one location to deficit at another | Canary-native rebalancing logic | "Store A has 40 flats of perennials they don't need; Store C is 20 below ROP" → TBD: L4 implementation detail pending |
| D.5.4 | Score rebalancing candidates by transfer-cost vs. replenishment-cost tradeoff | Per-route transfer cost (configurable) vs. J's new-order cost | Transfer is preferred when it's cheaper than ordering new and time-to-destination is faster than lead time → TBD: L4 implementation detail pending |
| D.5.5 | Generate transfer recommendation with OTB-context | Canary-native; cross-cut with O.3 (OTB) | Transfer doesn't consume OTB; restoring from transfer headroom context differs from new-PO headroom → TBD: L4 implementation detail pending |
| D.5.6 | Buyer review + accept/modify/reject for distribution recommendation | Canary-native UI / MCP / Owl | Same review UX pattern as O.4; buyer can accept the rebalancing suggestion or override → TBD: L4 implementation detail pending |

### User stories

- *As D's Distribution Recommender, I want to identify excess stock at high-SOH locations and deficit situations at low-SOH locations for the same item, and surface a rebalancing recommendation ranked by transfer-cost vs. replenishment-cost savings.*
- *As a Garden-Center Buyer, I want to ask "where do I have too much stock I should move?" and get a list of excess-at-location situations with candidate destination stores, expected transfer cost, and days-to-ROP at the destination.*
- *As a Buyer managing end-of-season, I want to generate a "consolidation plan" — all seasonal items with excess at seasonal pop-up locations, recommended for transfer back to the main store — as a single distribution recommendation batch.*
- *As D, I want transfer recommendations clearly distinguished from PO recommendations in the buyer surface — both appear in the recommendation queue, but their OTB-impact and procurement logic are different.*
- *As a logistics coordinator, I need to track a multi-stop transfer (warehouse → regional hub → destination store) so that inventory in-transit status is accurate at each leg.*
- *As a store manager, I need to cancel a transfer before the destination store receives it so that inventory is correctly returned to the source location.*
- *As a replenishment analyst, I need Canary to recommend splitting excess inventory from one location across multiple understocked locations, weighted by transfer cost and velocity, so I can optimize distribution.*
- *As a loss prevention analyst, I need to distinguish transfers initiated by a warehouse manager vs. a store manager so that audit context reflects the appropriate authorization level.*

## D.6 — Cross-module substrate contracts

**Purpose.** D is the primary publisher of stock-ledger movements. Downstream consumers (J, Q, F, C, T) depend on D's contracts holding. This L2 makes those contracts explicit.

| ID | Contract | Owner downstream | What D promises |
|---|---|---|---|
| D.6.1 | Per-`(item, location)` SOH snapshot, polled hourly | J (demand input), C (OTB calculation), Q (anomaly correlation) | Fresh SOH with staleness flag; delta log maintained between polls. **Consumed by A.2.1** — Asset lifecycle tracking reads D.6.1 SOH snapshot to determine asset movement history. |
| D.6.2 | XFER Documents routed to D from T before any other subscriber | T (routing contract), D.3 | T.4.7 routes XFER first; D processes before downstream SOH consumers. **Upstream source: T.4.7** — Transaction pipeline type-routes XFER documents to D. D.6.2 is downstream of T.4.7 type-routing. |
| D.6.3 | TRANSFER-VARIANCE record per XFER-RECVR pair | Q (Q-IS-03 accumulation), F (cost reconciliation) | Variance preserved with match-confidence flag (deterministic vs. heuristic). **Consumed by A.2.1** — Asset lifecycle tracking reads D.6.3 TRANSFER-VARIANCE events as movement evidence. |
| D.6.4 | In-transit inventory held until RECVR confirmation | J (on-order accounting), C (OTB) | In-transit is NOT available-for-sale; excluded from J's available-SOH replenishment calc |
| D.6.5 | UNATTRIBUTED-MOVEMENT events per snapshot delta residual | Q (anomaly correlation), F (shrink attribution) | Every delta not attributed to a Document is named, not silently dropped |
| D.6.6 | Transfer-cost per route (per-tenant configurable) | D.5 self-use, J (cost comparison) | Default transfer cost surfaced as configurable per route; zero if merchant doesn't track freight |
| D.6.7 | `InventoryControl.reorder_point` surface to J | O.2.1 (ROP baseline input) | D surfaces Counterpoint's buyer-set ROP as the starting baseline for J's ROP calculation |
| D.6.8 | Item-location set changes (new/removed pairs) | S (assortment validation), J (forecast scope) | Set changes published as events so J's forecast scope stays current |
| D.6.9 | In-transit timeout alerts to operations queue | D.3.6 timeout → operations review | Timeout is 72 hours (configurable); alert carries XFER Document ID and from/to context |

### User stories

- *As J's Demand Forecaster, I want D to surface the Counterpoint buyer-set ROP as a starting baseline I can override with demand-derived calculation — not replace without surfacing what the buyer originally set.*
- *As Q's Detection Engine, I want D.6.3 TRANSFER-VARIANCE records delivered with match-confidence flags so Q-IS-03 can weight deterministically-matched variances higher than heuristically-matched ones.*
- *As F, I want every UNATTRIBUTED-MOVEMENT event from D.6.5 with the snapshot delta, timestamp, and item-location context so cost reconciliation has a named record, not a gap.*

## Assumptions requiring real-customer validation

| ID | Assumption | What it blocks | Resolution path |
|---|---|---|---|
| ASSUMPTION-D-01 | Hourly snapshot poll cadence is adequate for transfer-visibility — if operators initiate multiple XFER Documents per hour at peak, the snapshot may lag | D.1 staleness policy; D.3 in-transit hold timing | Customer workflow observation; if sub-hourly is needed, switch to event-driven where Counterpoint supports it |
| ASSUMPTION-D-02 | `Inventory_ByLocation` returns all locations in one call or paginates cleanly — multi-location merchants need per-location scope confirmed | D.1.1 poll implementation | Sandbox with a multi-location test tenant |
| ASSUMPTION-D-03 | Transfer completion is confirmed via a Document with DOC_TYP=RECVR at the destination, linked via `PS_DOC_HDR_ORIG_DOC` | D.3.5 deterministic match path | Sandbox workflow test — initiate XFER, receive at destination, inspect resulting Document |
| ASSUMPTION-D-04 | DOC_TYP=XFER is the correct Counterpoint Document type for store-to-store transfers — naming convention confirmed via Document model wiki but not yet sandbox-verified | D.3 entire L2 | Sandbox workflow test; inspect `PS_DOC_HDR.DOC_TYP` on a live transfer |
| ASSUMPTION-D-05 | `InventoryControl` carries reorder-point fields accessible via the API (some control fields may be UI-only in Counterpoint) | D.2.2 and D.6.7 ROP baseline surface | API doc deep-read + sandbox schema inspection |
| ASSUMPTION-D-06 | Transfer cost per route is not stored in Counterpoint — assumed to be a Canary-configurable value | D.5.4 and D.6.6 | Customer interview; if merchant tracks freight in Counterpoint custom tables, path changes |
| ASSUMPTION-D-07 | End-of-season consolidation transfers are operationally significant for L&G SMB customers — assumed based on seasonal model but not confirmed | D.4.6 allow-list design and D.5.6 consolidation-plan use case | Garden-center customer interview |
| ASSUMPTION-D-08 | `InventoryEC` is only relevant for merchants with an active e-commerce channel — assumed most L&G SMB Counterpoint users do not have EC active | D.2.4 scope | Customer interview at onboarding |
| ASSUMPTION-D-09 | Undocumented transfers (stock moved between locations without a Counterpoint XFER Document) are a known L&G operating practice at some merchants | D.4.4 unattributed-delta design priority | Customer interview; if common, D.4.4 becomes a primary use case rather than an edge case |

**Highest-leverage gaps:** ASSUMPTION-D-03 (RECVR confirmation of transfer completion) and ASSUMPTION-D-04 (DOC_TYP=XFER naming) are the load-bearing assumptions for the entire D.3 substrate path. Both are sandbox-resolvable — they're not engagement-knowable, they're platform-knowable. ASSUMPTION-D-09 (undocumented transfers as a garden-center practice) is the engagement-knowable gap that most affects D.4's design priority.

## Customer-specific overrides

*Empty until a real customer engagement starts. Format reserved:*

```
Customer: <name>
Snapshot poll cadence: <hourly (default) | sub-hourly | daily>
Transfer-cost tracking: <Canary-configured per route | not tracked (default zero)>
Transfer-loss variance threshold: <% | units>
In-transit timeout: <72h (default) | <N>h>
End-of-season consolidation: <allow-list Q-IS-03 for consolidation-type XFER | standard rules apply>
InventoryEC in scope: <yes — merchant has e-commerce | no (default)>
Distribution recommendations: <enabled | disabled>
Distribution recommendation review: <buyer-mediated | auto-commit below $threshold>
Undocumented-transfer operating practice: <known / allow-list UNATTRIBUTED-MOVEMENT below threshold | standard (alert on all)>
Disabled D.x processes (with reason):
  D.x.x: <reason>
ASSUMPTION resolutions:
  ASSUMPTION-D-NN: resolved as <answer>; source: <evidence>
  ...
```

## Operating notes

**Cast of actors:**

| Actor | Role | Lives where |
|---|---|---|
| Snapshot Ingestor | Periodic SOH polling service | Canary-internal (D.1) |
| Transfer Subscriber | XFER Document consumer from T's pipeline | Canary-internal (D.3) |
| Variance Calculator | XFER-RECVR reconciliation service | Canary-internal (D.4) |
| Distribution Recommender | Excess/deficit matching and recommendation generator | Canary-internal (D.5) |
| Buyer / Distribution Manager | Human-in-the-loop for transfer recommendations | Customer org |
| Operator | Monitors in-transit timeouts and staleness flags | Customer org |
| Owl / Fox | Distribution recommendation surface + investigation queue | Canary-internal |

**The partial-coverage cell drives the L2 split.** D.1/D.2 are high-confidence substrate reads — Counterpoint's per-location inventory surface is genuinely richer than most SMB POS platforms. D.3 is substrate-via-indirection — workable, but the Document omnibus routing contract with T is a dependency that must hold. D.4/D.5 are the Canary-native gap — and are the highest-ROI deliverables for multi-location garden-center operators who currently manage stock rebalancing via whiteboard or spreadsheet.

**Transfer detection depends on T's routing contract.** D does not poll Documents independently. T's type-routing (T.4.7) is a prerequisite. If T's XFER routing fails, D.3's entire L2 fails silently. This cross-module dependency must be surfaced as a contract test in Phase III.

**Garden-center operational reality shapes D significantly.** Multi-location L&G operators frequently move stock between stores for seasonal displays, end-of-season consolidation, and opportunistic rebalancing. The transfer surface is not an edge case — it's a primary operating workflow. The Canary-native D.4/D.5 L2s exist precisely because Counterpoint doesn't optimize this.

## Related

- `Canary-Retail-Brain/modules/D-distribution.md` — L1 canonical spec
- `canary-module-d-distribution.md` — L2 Canary code/schema crosswalk
- `canary-module-o-functional-decomposition.md` — sister card; O.6.2 RECVR matching is D.3.5's prerequisite; O.2.1 ROP calculation consumes D.6.7
- `canary-module-q-functional-decomposition.md` — sister card; Q-IS-03 (transfer-loss pattern) reads from D.4.3
- `canary-module-f-functional-decomposition.md` — sister card; F's cost reconciliation consumes D.6.3 and D.6.5
- `canary-module-m-functional-decomposition.md` — sister card; C reads D.6.1 SOH for OTB calculation
- `canary-module-t-functional-decomposition.md` — sister card; T.4.7 routing contract is a D.3 prerequisite
- `ncr-counterpoint-document-model.md` — DOC_TYP=XFER, `PS_DOC_HDR_ORIG_DOC` reference
- `ncr-counterpoint-api-reference.md` — D-column coverage summary (7 inventory endpoints)
- `ncr-counterpoint-endpoint-spine-map.md` — per-endpoint × CRDM × spine placement for D
- `retail-merchandise-planning-otb.md` — allocation methods; companion for D.5
- `retail-po-from-plan.md` — PO chain; companion for D.3/D.4 (RECVR/RTV intersection)
- `garden-center-operating-reality.md` — multi-store transfer reality; live-goods context for D.4.6
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — D row = ◐ Partial; this card is the L2/L3 expansion of that cell

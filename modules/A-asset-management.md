---
classification: internal
type: wiki
sub-type: module-functional-decomposition
date: 2026-04-26
last-compiled: 2026-04-26
module: A
solution-map-cell: ◐ Derived — asset-item identification from IM_ITEM.ITEM_TYP flags; no dedicated Counterpoint asset endpoint; view over S
companion-modules: [S, T, Q, N]
companion-substrate: [ncr-counterpoint-api-reference.md, ncr-counterpoint-endpoint-spine-map.md]
companion-canary-spec: Canary-Retail-Brain/modules/A-asset-management.md
companion-canary-crosswalk: Brain/wiki/canary-module-a-asset-management.md
companion-catz: CATz/proof-cases/specialty-smb-counterpoint-solution-map.md
methodology-note: "Sister card to d, c, p functional-decomp cards. Thinnest of the four remaining modules — the Solution Map proof case explicitly notes asset-tracking depth is not needed at SMB specialty scale. IMPORTANT: The canonical Canary Brain spec for Module A (Bubble) describes device-anomaly detection, not item-level asset tracking. This card covers the CATz solution-map interpretation of A (retail asset management, non-saleable item tracking) and flags the scope discrepancy in ASSUMPTION-A-01."
---

# Module A (Asset Management) — Functional Decomposition

> **Artifact layer.** Third of three Canary module artifact layers:
> 1. **Canonical spec** (vendor-neutral) — `Canary-Retail-Brain/modules/A-asset-management.md`
> 2. **Code/schema crosswalk** (Canary-specific) — `Brain/wiki/canary-module-a-asset-management.md`
> 3. **Functional decomposition** (Counterpoint-substrate-aware, L2/L3 + user stories) — *this card*

## Governing thesis

A is the **thinnest module in the spine** against the Counterpoint substrate — and intentionally so. In the CATz solution map for specialty SMB retail, asset management means one thing: distinguishing inventory items from non-inventory fixed assets (fixtures, equipment, display materials) so that Canary's loss-prevention and merchandising surfaces don't conflate merchandise on the sales floor with assets that never leave the store. Counterpoint carries this distinction in `IM_ITEM.ITEM_TYP` — `I` for inventory (saleable), `N` for non-inventory (non-saleable) — and that flag is A's entire Counterpoint substrate.

**Critical scope note before reading further.** The canonical Canary Brain spec for Module A (codenamed Bubble) describes a different capability: **multivariate device-anomaly detection** over N's device registry — per-device behavioral baselines, anomaly scoring, cross-device pattern detection. That is a detection module, not an asset-management module, and it has no relationship to `IM_ITEM.ITEM_TYP`. This card covers the CATz solution-map interpretation of the A cell (retail asset management, non-saleable item tracking from Counterpoint substrate). The scope conflict is documented in ASSUMPTION-A-01 and should be resolved before the A card is elevated beyond draft v1.

Against the CATz proof case for specialty SMB, the A cell is rated ◐ Derived deliberately. A garden-center operator at 3-8 locations doesn't need a deep asset-management module — they need Canary to know which items in their catalog are non-saleable so that detection rules, OTB calculations, and replenishment recommendations don't fire against fixtures and display materials. That is the entirety of A's near-term job. The Bubble detection capability (ASSUMPTION-A-01) is a separate, higher-value deliverable that belongs in a different card when the scope conflict is resolved.

## Executive summary

| Dimension | Count | Source |
|---|---|---|
| L2 process areas | 3 | This card |
| L3 functional processes | 12 | This card |
| Counterpoint endpoints in A's path | 0 dedicated; `IM_ITEM.ITEM_TYP` field via S's item master | API reference |
| Counterpoint-substrate L2 areas | 1 (A.1 asset-item identification, derived from S) | Item flags |
| Canary-native L2 areas | 1 (A.2 asset lifecycle tracking, derived from movement history) | Canary ledger |
| Cross-cutting L2 areas | 1 (A.3 substrate contracts) | Downstream consumers |
| Substrate contracts A owes downstream | 4 | This card §A.3 |
| Assumptions requiring real-customer validation | 4 (+ 1 scope-level) | Tagged `ASSUMPTION-A-NN` |
| User stories enumerated | 14 | Observer-module posture; cast in §Operating notes |

**Posture:** thin derived module. A contributes no own-data and has no own Counterpoint endpoints. Its value is the classification layer it provides to Q (loss prevention doesn't chase fixture markdowns), to J (replenishment doesn't order non-saleable items), and to C (OTB doesn't consume budget on non-inventory items). Keep scope honest — this card does not over-decompose.

## L1 → L2 → L3 framework

```
L1 (Solution Map cell)         A = ◐ Derived
                                 │  (no dedicated Counterpoint endpoint family;
                                 │   asset-item identification derived from S via IM_ITEM.ITEM_TYP;
                                 │   asset lifecycle derived from D's movement history)
                                 │
L2 (Process areas)               ├── A.1  Asset-item identification     ◐ Derived from S (IM_ITEM.ITEM_TYP)
                                 ├── A.2  Asset lifecycle tracking      ◐ Derived from D's movement history
                                 └── A.3  Cross-module substrate contracts
                                 │
L3 (Functional processes)       (12 — enumerated per L2 below)
                                 │
L4 (Implementation detail)      Canary-Retail-Brain/modules/A-asset-management.md
                                  + canary-module-a-asset-management.md (crosswalk — currently covers Bubble/device-anomaly scope)
                                  + future Canary/docs/sdds/v2/asset-management.md (pending scope resolution)
```

## A.1 — Asset-item identification

**Coverage posture.** ◐ Derived from S (item master). Counterpoint's `IM_ITEM.ITEM_TYP` flag distinguishes inventory (`I`) from non-inventory (`N`) items. A reads this flag from S's item master surface; A does not poll Counterpoint independently.

**Companion cards.** `canary-module-s-functional-decomposition.md` (S publishes item master including ITEM_TYP), `ncr-counterpoint-endpoint-spine-map.md` (IM_ITEM placement in S + A seam).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| A.1.1 | Read `IM_ITEM.ITEM_TYP` per item from S's item master | S's item-master publication | `I` = inventory (saleable), `N` = non-inventory (asset, non-saleable); A reads this classification from S → TBD: L4 implementation detail pending |
| A.1.2 | Read `IM_ITEM.STAT` (item status) alongside ITEM_TYP | S's item-master publication | Active vs. discontinued; A is only interested in active non-inventory items → TBD: L4 implementation detail pending |
| A.1.3 | Maintain Canary-side asset-item registry | A's own classification projection | Per-merchant list of items classified as non-saleable assets; updated when S detects ITEM_TYP changes → TBD: L4 implementation detail pending |
| A.1.4 | Detect ITEM_TYP reclassification events | S event stream — when an item changes from `I` to `N` or vice versa | Reclassification events propagate to downstream consumers (Q allow-list, J replenishment exclusion, C OTB exclusion) → TBD: L4 implementation detail pending |
| A.1.5 | Surface asset-item registry to downstream consumers | A's substrate contract (§A.3) | Q, J, and C each consume the asset-item list for their own filtering; A is the single source of classification truth → TBD: L4 implementation detail pending |

### User stories

- *As A's Classifier, I want every item with `ITEM_TYP=N` in Counterpoint added to the Canary asset-item registry automatically when S publishes it, so no configuration step is needed to exclude non-saleable items from Canary's saleable surfaces.*
- *As A's Classifier, I want ITEM_TYP reclassification events (e.g., a fixture that was sold off inventory is reclassified from `N` to `I`) to propagate immediately to Q, J, and C so their filtering stays current.*
- *As an Operator, I want to query "show me all items Canary classifies as non-saleable assets at this location" with confirmation of which Counterpoint ITEM_TYP drove the classification — no opaque Canary-internal flag without substrate traceability.*

## A.2 — Asset lifecycle tracking

**Coverage posture.** ◐ Derived from D's movement history. Non-inventory items can still move between locations (fixtures transferred to a new store layout, display materials relocated). D's transfer and adjustment pipeline is the substrate; A reads movement records filtered to its asset-item registry.

**Companion cards.** `canary-module-d-functional-decomposition.md` (D.6.1 SOH snapshot and D.6.3 TRANSFER-VARIANCE as inputs), `garden-center-operating-reality.md` (fixture and display-material context for L&G).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| A.2.1 | Read D's movement records filtered to asset-item registry | D.6.1 SOH + D.6.3 TRANSFER-VARIANCE | Movement history for non-inventory items; tells the story of where a fixture has been → TBD: L4 implementation detail pending |
| A.2.2 | Track per-asset location history | A's projection over D's movements | Where is each asset right now, and where has it been? Low-cost view — movement records already exist → TBD: L4 implementation detail pending |
| A.2.3 | Detect unexpected movement on asset items | Canary-native flag | An adjustment or variance on a non-inventory item is operationally unusual; may indicate misclassification or loss of a fixture → TBD: L4 implementation detail pending |
| A.2.4 | Flag high-value asset disposal via RTV-type movement | D.6.3 RTV records filtered to asset registry | If a high-value asset (display case, cooler) is disposed via an RTV-type movement, flag for finance review → TBD: L4 implementation detail pending |

### User stories

- *As A's Lifecycle Tracker, I want D's movement records for non-inventory items surfaced as an asset-location history, so an operator can ask "where is fixture X and how did it get there" without a separate asset-tracking system.*
- *As an Operator, I want unexpected adjustments on non-inventory asset items flagged — if a store fixture suddenly has a shrink-attributed adjustment, that's worth a look.*
- *As Finance, I want high-value asset disposal movements (items with `ITEM_TYP=N` and cost above threshold appearing in RTV-type records) flagged for review, so fixture write-offs aren't silently absorbed.*

## A.3 — Cross-module substrate contracts

**Purpose.** A's primary value to the spine is as a classification filter for downstream modules. These contracts must hold for Q, J, and C to function correctly on multi-assortment Counterpoint catalogs.

| ID | Contract | Owner downstream | What A promises |
|---|---|---|---|
| A.3.1 | Asset-item registry (list of non-saleable item IDs) | Q (allow-list for detection rules), J (replenishment exclusion), C (OTB exclusion) | Current list of items with `ITEM_TYP=N`; updated within one S-poll cycle of any reclassification |

> **Reciprocal dependency:** Q.2 detection rules consume A.3.1 asset-item registry as allow-list filtering input. Q must not flag items classified as non-inventory assets. See canary-module-q-functional-decomposition §Q.2.
| A.3.2 | ITEM_TYP reclassification events | Q, J, C (downstream filter updates) | Reclassification events published with item_id, old_type, new_type, effective_date |
| A.3.3 | Asset location history (per asset per location) | Finance (asset audit), Operator (fixture management) | Location history derived from D's movement records; does not require independent polling |
| A.3.4 | High-value asset disposal flags | Finance (write-off review) | RTV-type movements on items with cost > configurable threshold; configurable threshold defaults to $500 (ASSUMPTION-A-04) |

### User stories

- *As Q's Detection Engine, I want A's asset-item registry injected as an allow-list exclusion so Q-DM-01/02/03 (discount and markdown rules) don't fire on fixture markdowns or non-inventory item adjustments.*
- *As J's Replenishment Engine, I want non-inventory items excluded from replenishment calculation — Canary should never recommend ordering more display stands.*
- *As C's OTB Calculator, I want non-inventory items excluded from OTB budget consumption, so fixture purchases don't reduce the buyer's merchandise open-to-buy.*
- *As a store manager, I need to reassign an asset (fixture/equipment) from one zone to another within the same location so that the asset registry reflects current physical placement.*
- *As a loss prevention analyst, I need Canary to detect when an item flagged as a non-inventory asset (ITEM_TYP = N) is sold at retail price, so I can investigate unauthorized merchandise conversion.*

## Assumptions requiring real-customer validation

| ID | Assumption | What it blocks | Resolution path |
|---|---|---|---|
| ASSUMPTION-A-01 | **SCOPE CONFLICT: canonical Canary spec for Module A (Bubble) is device-anomaly detection, not item-asset-management.** This card covers the CATz solution-map interpretation (item-level, IM_ITEM.ITEM_TYP derived). The two interpretations need explicit reconciliation before A's scope is finalized. | A's entire card scope; downstream contract registry | Founder decision: is A (i) item-asset-management (this card), (ii) device-anomaly detection (Bubble), (iii) both under one module letter, or (iv) split into separate modules? |
| ASSUMPTION-A-02 | `IM_ITEM.ITEM_TYP=N` is the correct Counterpoint flag for non-saleable fixed assets — field confirmed in item schema but not verified as the operational convention at L&G Counterpoint customers | A.1.1 and A.3.1 registry population | Sandbox schema inspection; customer interview to confirm operators actually set ITEM_TYP=N for fixtures vs. leaving all items as `I` |
| ASSUMPTION-A-03 | Non-inventory items are meaningfully present in L&G Counterpoint catalogs — some SMB merchants may have all items flagged `I` (inventory) even for display materials | A.1 scope relevance | Customer catalog inspection at onboarding |
| ASSUMPTION-A-04 | High-value asset disposal threshold ($500 default for A.3.4) is appropriate for L&G SMB | A.3.4 default calibration | Customer interview at onboarding |

**Highest-leverage gap:** ASSUMPTION-A-01 is the scope-level conflict that supersedes all others. Until the Bubble vs. item-asset-management question is resolved, this card should be treated as a working draft of one interpretation, not a finalized decomposition. That said, the item-asset-management L2s in this card are low-risk regardless of the Bubble decision — they represent a thin, real capability needed to protect Q, J, and C from non-saleable catalog items.

## Customer-specific overrides

*Empty until a real customer engagement starts. Format reserved:*

```
Customer: <name>
ITEM_TYP=N items in use: <yes — N items present in catalog | no — all items are ITEM_TYP=I>
High-value asset threshold: <$500 (default) | $<N>>
Asset disposal flag: <enabled (default) | disabled>
Fixture-transfer lifecycle tracking: <enabled | disabled>
ASSUMPTION resolutions:
  ASSUMPTION-A-NN: resolved as <answer>; source: <evidence>
  ...
```

## Operating notes

**Cast of actors:**

| Actor | Role | Lives where |
|---|---|---|
| Classifier | Reads S's item master, populates asset-item registry | Canary-internal (A.1) |
| Lifecycle Tracker | Reads D's movement records for asset items | Canary-internal (A.2) |
| Operator | Queries fixture location history | Customer org |
| Finance | Reviews high-value asset disposal flags | Customer org |
| Owl | Asset-registry and location-history surface | Canary-internal |

**A is an observer module.** There are no A-specific write paths. A reads from S and D; it publishes its asset-item registry as a service to Q, J, and C. This is intentional — at SMB specialty scale, asset management is a classification concern, not an operational workflow. Over-decomposing A would be a mistake.

**The Bubble conflict matters.** The canonical Canary Module A (device anomaly detection) is architecturally committed and has existing scaffold. If the scope of the A spine letter is ever resolved to mean both item-asset-management AND device-anomaly detection, this card will need a D.6-style substrate contract to the Bubble detection pipeline.

## Related

- `Canary-Retail-Brain/modules/A-asset-management.md` — canonical spec (covers Bubble device-anomaly scope; scope conflict with this card documented in ASSUMPTION-A-01)
- `canary-module-a-asset-management.md` — L2 Canary code/schema crosswalk (covers Bubble scope)
- `canary-module-s-functional-decomposition.md` — sister card; A.1.1 reads from S's item master publication
- `canary-module-d-functional-decomposition.md` — sister card; A.2.1 reads from D.6.1/D.6.3 movement records
- `canary-module-q-functional-decomposition.md` — sister card; A.3.1 registry is Q's allow-list for detection rules
- `canary-module-j-functional-decomposition.md` — sister card; A.3.1 excludes non-saleable items from J's replenishment scope
- `ncr-counterpoint-api-reference.md` — IM_ITEM schema context (ITEM_TYP field location)
- `ncr-counterpoint-endpoint-spine-map.md` — A-column placement (derived, no dedicated endpoints)
- `garden-center-operating-reality.md` — fixture and display-material context for L&G
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — A row = ◐ Derived; this card is the L2/L3 expansion of that cell

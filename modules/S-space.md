---
title: S — Space
nav_order: 4
classification: internal
type: wiki
sub-type: module-functional-decomposition
date: 2026-04-26
last-compiled: 2026-04-26
module: S
solution-map-cell: ● Full direct (Counterpoint Item / Inventory / EC families — 17 endpoints; the largest catalog surface in the API)
companion-modules: [T, C, Q, P, O, D, A]
companion-substrate: [ncr-counterpoint-api-reference.md, ncr-counterpoint-endpoint-spine-map.md]
companion-context: [garden-center-operating-reality.md, ncr-counterpoint-rapid-pos-relationship.md]
companion-canary-spec: Canary-Retail-Brain/modules/S-space.md
companion-canary-crosswalk: Brain/wiki/canary-module-s-space.md
companion-catz: CATz/proof-cases/specialty-smb-counterpoint-solution-map.md
methodology-note: "Sister card to canary-module-q/t/r/j-functional-decomposition.md. Same template per CATz/method/artifacts/module-functional-decomposition.md. S is the most vertical-distinctive substrate module — garden-center mix-and-match, fractional units, and multi-name plants are first-class L2/L3 concerns, not afterthoughts."
---

# Module S (Space) — Functional Decomposition

> **Artifact layer.** Third of three Canary module artifact layers:
> 1. **Canonical spec** (vendor-neutral) — `Canary-Retail-Brain/modules/S-space.md`
> 2. **Code/schema crosswalk** (Canary-specific) — `Brain/wiki/canary-module-s-space.md`
> 3. **Functional decomposition** (Counterpoint-substrate-aware, L2/L3 + user stories) — *this card*

## Governing thesis

S is the **catalog substrate** for everything in the spine that touches a product. Q reads category margin targets from S. P-derived pricing observations join through S. J's like-item forecasting reaches into S for category-average velocity. T's transaction lines reference S for item identity. R's tier-aware allow-lists join through S to apply per-category exemptions. Every non-trivial detection or projection routes through S.

Counterpoint's catalog surface is **the richest of any spine module** — 17 endpoints covering item master, categories, serial numbers, images, per-location inventory, vendor-item linkage, and a parallel eCommerce catalog. For a Lawn & Garden tenant specifically, three vertical capabilities sit on top of this substrate and are load-bearing: **mix-and-match groups** (`MIX_MATCH_COD` on items + per-line on Documents), **fractional unit modeling** (`PREF_UNIT_NUMER/DENOM/NAM` for "sell flat OR sell individual plant from flat"), and **multi-name plant identity** (botanical / common / Spanish names — convention-dependent across the `ADDL_DESCR_*` and `ATTR_COD_*` slots).

S is **● Full direct** in every Counterpoint Solution Map cell, but the cell hides three real architectural concerns that don't show up in simpler retail verticals: (1) **item lifecycle is short and seasonal** — the catalog churns mid-season, item-code drift across intakes is normal not anomalous, (2) **the ecommerce catalog runs in parallel** with separate publish flags + state machine + control table, and (3) **per-customer naming conventions for multi-name fields** vary across Rapid POS deployments — there is no universal mapping for which `ADDL_DESCR_N` slot holds which language.

## Counterpoint Endpoint Substrate

| Counterpoint Endpoint | CRDM Entity | L2 Process Area |
|---|---|---|
| IM_ITEM (location flags) | Item-location assignment | S.1 (Range definition), S.2 (Display catalog) |
| Items_ByLocation | Location-item catalog | S.1 (Location range audit) |
| Inventory_ByLocation | SOH by location | S.3 (Space utilization: stock vs. allocated facing) |
| PS_DOC_LIN | Transaction line detail | S.4 (Sales velocity by display position) |
| IM_ITEM.ITEM_TYP | Item classification | S.1 (Asset-item exclusion from range, sourced from A) |

## Executive summary

| Dimension | Count | Source |
|---|---|---|
| L2 process areas | 7 | This card |
| L3 functional processes | 36 | This card |
| Counterpoint endpoints in S's path | 17 (Item / Items / Items_ByLocation / ItemCategories / ItemCategory / ItemSerial / ItemSerials / Item_Images / Item_ImageFilename / Item_Inventory / Inventory_ByLocation / InventoryControl / InventoryCost / InventoryEC / InventoryLocations / VendorItem / EC / ECCategories) | API reference |
| Garden-center distinctive L2 areas | 3 (S.3 mix-and-match, S.4 fractional units, S.5 lifecycle/drift) | garden-center-operating-reality |
| Cached entities (24h server-side) | 4 (Items metadata, ItemCategories, eCommerce Categories, eCommerce Control) | API reference cache discipline |
| Substrate contracts S owes downstream | 11 | This card §S.7 |
| Assumptions requiring real-customer validation | 11 | Tagged `ASSUMPTION-S-NN` |
| User stories enumerated | 52 | Observer + actor mix; cast in §Operating notes |

**Posture:** archetype-shaped against Counterpoint specifically. The garden-center vertical concerns (mix-and-match, fractional units, multi-name plants) are first-class L2/L3 areas because they're load-bearing for Q rules and P-derived pricing observations. Per-customer convention discovery for multi-name fields and category-margin targets happens at onboarding.

## L1 → L2 → L3 framework

```
L1 (Solution Map cell)         S = ● Full direct (Counterpoint Item / Inventory / EC families — 17 endpoints)
                                 │
L2 (Process areas)               ├── S.1  Item master ingestion + sync
                                 ├── S.2  Category hierarchy + margin targets
                                 ├── S.3  Mix-and-match group surfacing      (garden-center distinctive)
                                 ├── S.4  Fractional unit modeling           (garden-center distinctive)
                                 ├── S.5  Item lifecycle + drift handling    (garden-center reality)
                                 ├── S.6  eCommerce catalog surface
                                 └── S.7  Cross-module substrate contracts
                                 │
L3 (Functional processes)       (36 — enumerated per L2 below)
                                 │
L4 (Implementation detail)      Lives in SDDs + module specs
                                  (Canary-Retail-Brain/modules/S-space.md,
                                   docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md §6.4)
```

## S.1 — Item master ingestion + sync

**Purpose.** Pull the Counterpoint item catalog into CRDM. Counterpoint's Item endpoint is the single richest entity surface in the API — `IM_ITEM` carries dozens of fields covering identity, classification, pricing, costing, attributes, ecommerce flags, mix-and-match grouping, vendor linkage, and serial-number tracking. S surfaces all of it without normalization.

**Companion cards.** `ncr-counterpoint-api-reference` (Item endpoint family + cache discipline), `Canary-Retail-Brain/modules/S-space.md` (canonical spec), `canary-module-s-space.md` (schema crosswalk).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| S.1.1 | Full-row enrichment from `GET /Item/{ItemNo}` | `IM_ITEM` master | Called when single-item enrichment needed (price update, attribute change) → TBD: L4 implementation detail pending |
| S.1.2 | Incremental sync via `GET /Items` | Paginated, category/subcategory-filterable | Items metadata is **cached server-side 24h** — `ServerCache: no-cache` for first poll of each cycle → TBD: L4 implementation detail pending |
| S.1.3 | Per-location item enrichment via `GET /Items/{LocId}` | Per-`LocId` view | Cross-cuts D (per-location inventory); same item can have per-location flags → TBD: L4 implementation detail pending |
| S.1.4 | Item image references via `GET /Item/{ItemNo}/Images` | Filename list | Image binaries fetched on-demand via `GET /Item/Images/{Filename}` — never bulk-cached → TBD: L4 implementation detail pending |
| S.1.5 | Serial number tracking via `GET /Item/{ItemNo}/Serial/{SerialNo}` | `SN_SER` lookup | Per-serial metadata; substrate for high-fashion / asset-tracking patterns (less relevant for L&G) → TBD: L4 implementation detail pending |
| S.1.6 | Per-location serial enumeration | `GET /Item/{ItemNo}/Serials/Location/{LocId}` | Active serials at a location; cross-cuts D → TBD: L4 implementation detail pending |
| S.1.7 | Vendor-item linkage via `GET /VendorItem/{VendorNo}/Item/{ItemNo}` | `IM_VEND_ITEM` | Substrate for J's vendor-master + supplier-scorecard → TBD: L4 implementation detail pending |

### User stories

- *As S's catalog ingester, I want the daily item-metadata poll to respect the 24h server-cache by default and only force `ServerCache: no-cache` when an item-attribute change is suspected (price update, vendor change, attribute toggle).*
- *As S, I want every `IM_ITEM` field preserved verbatim through ingestion — downstream modules (P-derived pricing, Q margin rules) need the raw values, not a normalized subset.*
- *As Q, I want category and subcategory codes attached to every item reference at parse-time, so margin-erosion rules don't need a second join to resolve item context.*
- *As J, I want vendor-item linkage available without a separate Counterpoint call per recommendation — the supplier should be on the item record at recommendation generation time.*

## S.2 — Category hierarchy + margin targets

**Purpose.** Counterpoint exposes category and subcategory codes plus per-category margin targets (`MIN_PFT_PCT`, `TRGT_PFT_PCT`). These are **load-bearing for Q's margin-erosion rules** (Q-ME-01) and informational for P-derived pricing observations. The hierarchy is also the foundation for J's like-item forecasting and S's own assortment-and-range execution surface.

**Companion cards.** `ncr-counterpoint-api-reference` § "Category margin targets", `canary-module-q-counterpoint-rule-catalog.md` § Q-ME-01 (consumer of margin targets).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| S.2.1 | Category hierarchy ingestion | `GET /ItemCategories` | Hierarchical list; cached 24h → TBD: L4 implementation detail pending |
| S.2.2 | Per-category detail enrichment | `GET /ItemCategory/{CategoryCode}` | Includes `MIN_PFT_PCT` + `TRGT_PFT_PCT` per category → TBD: L4 implementation detail pending |
| S.2.3 | Category-margin-target surfacing to Q | Direct surface on every item join | Q-ME-01 substrate (below-category-target margin detection) → TBD: L4 implementation detail pending |
| S.2.4 | Category-history-of-assignment tracking | Effective-dated category assignments per item | Plan-vs-actual comparisons cross hierarchy reorganizations cleanly (per O.1.5) → TBD: L4 implementation detail pending |
| S.2.5 | Subcategory rollup | `IM_ITEM.SUBCAT_COD` to category | Hierarchy traversal for analytics + dashboard rollups → TBD: L4 implementation detail pending |
| S.2.6 | Per-category assortment plan substrate | Reads cross-cut with P (which categories carry seasonal plans) | Substrate for P; not authored by S → TBD: L4 implementation detail pending |

### User stories

- *As S, I want every item join to carry the category's `MIN_PFT_PCT` and `TRGT_PFT_PCT` inline, so Q-ME-01 can compute realized-vs-target margin per line without a second lookup.*
- *As S, I want category reassignment events captured with effective dates so historical sales attribute correctly to "the category at the time of the sale" — not "the category as of today" — for plan-vs-actual comparisons.*
- *As a Garden-Center GM in Owl, I want to ask "which categories are below margin target this month" and get a per-category rollup with the contributing items drillable.*
- *As J's like-item forecaster, I want category-average velocity available per `(category, location)` so new mid-season SKUs can use category context for their initial forecast.*

## S.3 — Mix-and-match group surfacing (garden-center distinctive)

**Purpose.** Mix-and-match flat pricing — buy 6 perennials for $30 regardless of which 6 — is a defining capability of garden-center retail. Counterpoint surfaces this through `MIX_MATCH_COD` on `IM_ITEM` (group identity) and on `PS_DOC_LIN` (per-line membership at sale time, plus `MIX_MATCH_CONTRIB` and `MIX_MATCH_PRC_BASED_ON` for the bundle math). S surfaces the group identity; T captures the per-line application; Q audits the bundle integrity.

**Companion cards.** `ncr-counterpoint-rapid-pos-relationship` § "Mix-and-match flats / bundle pricing", `canary-module-q-counterpoint-rule-catalog.md` § Q-MM-01 / Q-MM-02 (consumer of mix-and-match group identity).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| S.3.1 | Item-side mix-and-match group identification | `IM_ITEM.MIX_MATCH_COD` | Membership in a bundle group; same code across items in the group → TBD: L4 implementation detail pending |
| S.3.2 | Bundle pricing rule surfacing | Where the bundle price lives (likely separate config; **ASSUMPTION-S-04**) | Per-bundle target price and qualification rules → TBD: L4 implementation detail pending |
| S.3.3 | Per-line bundle attribution at sale time | Cross-cut with T — `PS_DOC_LIN.MIX_MATCH_COD` + `MIX_MATCH_CONTRIB` + `MIX_MATCH_PRC_BASED_ON` | T flattens these per line; S provides the group context for interpretation → TBD: L4 implementation detail pending |
| S.3.4 | Bundle integrity audit | Cross-cut with Q — Q-MM-02 detects mix-match code on a line whose item isn't in the group | S supplies the group-membership check → TBD: L4 implementation detail pending |
| S.3.5 | Bundle-margin computation | Per-bundle realized vs target | Substrate for Q-MM-01 (bundle producing below-cost line — flag at bundle level not line level) → TBD: L4 implementation detail pending |

### User stories

- *As S, I want to surface every item's `MIX_MATCH_COD` so Q can build a per-bundle membership table at boot and answer "is this line legitimately part of this bundle" deterministically.*
- *As Q, I want bundle-level margin computed — sum of bundle line `EXT_PRC` minus sum of bundle line `EXT_COST` — flagged only when the BUNDLE goes negative, not when individual lines do (intentional structure of mix-and-match flat pricing).*
- *As an LP Analyst investigating a Q-MM-01 case in Fox, I want to see the bundle definition snapshot at detection time + the lines actually rung + the resulting bundle margin, all on one screen.*
- *As a Garden-Center GM in Owl, I want to ask "which mix-and-match bundles are running below target this season" and get the per-bundle drilldown.*

## S.4 — Fractional unit modeling (garden-center distinctive)

**Purpose.** Garden centers sell the same physical item at multiple unit granularities — buy a flat of 18 perennials, or buy a single perennial from the same flat. Counterpoint models this through `IM_ITEM.PREF_UNIT_NUMER/DENOM/NAM` + `STK_UNIT` and per-line `PS_DOC_LIN.QTY_NUMER/QTY_DENOM/QTY_UNIT/SELL_UNIT`. The fractional model is also load-bearing for non-plant categories (bulk soil sold by cubic foot or yard, fertilizer sold by lb or bag).

**Companion cards.** `ncr-counterpoint-rapid-pos-relationship` § "Bulk-to-fractional sales".

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| S.4.1 | Preferred unit identification | `IM_ITEM.PREF_UNIT_NUMER/DENOM/NAM` | The buyer-set "default" unit for sale (e.g., "single plant" vs "flat of 18") → TBD: L4 implementation detail pending |
| S.4.2 | Stock unit identification | `IM_ITEM.STK_UNIT` | The unit inventory is counted in (typically the larger/parent unit) → TBD: L4 implementation detail pending |
| S.4.3 | Per-line fractional quantity surfacing | Cross-cut with T — `PS_DOC_LIN.QTY_NUMER/QTY_DENOM/QTY_UNIT/SELL_UNIT` | T flattens fractional quantities; S provides the unit-conversion context → TBD: L4 implementation detail pending |
| S.4.4 | Inventory deduction at fractional scale | Cross-cut with D — selling 1/18th of a flat decrements 1/18th of a stock unit | D handles the math; S provides the conversion factor → TBD: L4 implementation detail pending |
| S.4.5 | Fractional-unit-aware analytics | Aggregate sales + margin computed in stock-unit-equivalents | Owl queries return consistent units for cross-item rollups → TBD: L4 implementation detail pending |

### User stories

- *As S, I want every item's stock-unit and preferred-sell-unit available so D can decrement inventory correctly when a fractional quantity is sold.*
- *As Owl, I want to answer "how many flats of perennials sold this week" by aggregating fractional quantities back to flat-equivalents transparently — the user shouldn't need to know whether each sale was a flat or 18 individual plants.*
- *As Q, I want to recognize fractional-unit sales as legitimate — a single-plant sale shouldn't fire Q-DM-03 (below-cost) just because the per-unit cost lookup gave the flat cost not the plant cost.*

## S.5 — Item lifecycle + drift handling

**Purpose.** Garden-center catalogs are short-lifecycle and high-churn. New items appear mid-season as new shipments arrive; old items retire. Item-code drift is normal — the same plant cultivar may exist as multiple `ITEM_NO` records over time as different intakes get coded differently. Multi-name plant identity (botanical / common / Spanish) is convention-dependent across the `ADDL_DESCR_*` and `ATTR_COD_*` slots; per-customer convention discovery happens at onboarding.

**Companion cards.** `garden-center-operating-reality` § "What this means for the data flow" (item-code drift, mid-season ad-hoc additions, multi-name plants).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| S.5.1 | Item status surfacing | `IM_ITEM.STAT` (active / discontinued / etc.) | Substrate for end-of-life clearance recognition + retired-item filtering → TBD: L4 implementation detail pending |
| S.5.2 | Multi-name field surfacing | `IM_ITEM.ADDL_DESCR_1/2/3` + `ATTR_COD_1/2` | Convention-dependent (**ASSUMPTION-S-07**); per-customer mapping captured at onboarding → TBD: L4 implementation detail pending |
| S.5.3 | Item-code drift handling | Same plant under multiple `ITEM_NO`s across intakes | S surfaces drift-tolerance metadata; downstream rules apply tolerance bands (per garden-center allow-list framework) → TBD: L4 implementation detail pending |
| S.5.4 | Mid-season catalog addition | New `ITEM_NO` appears between full poll cycles | S's incremental poll picks up new items via `RS_UTC_DT` filter; like-item forecasting (O.1.6) bridges the no-history gap → TBD: L4 implementation detail pending |
| S.5.5 | Retired-item handling | `STAT='D'` discontinued | Soft-retire in CRDM; preserve historical references; exclude from future replenishment recommendations → TBD: L4 implementation detail pending |
| S.5.6 | Manual-entry-error tolerance | Hand-typed item creation by buyers at intake | Flag-and-ingest, not reject — per garden-center wiki posture → TBD: L4 implementation detail pending |

### User stories

- *As S, I want item-code drift recognized as normal — when two different `ITEM_NO`s have very similar descriptions and the same vendor, surface the linkage as a hint to investigators rather than treating each as fully independent.*
- *As S, I want per-customer multi-name field convention captured at onboarding — for Customer X, `ADDL_DESCR_1` is botanical name, `ADDL_DESCR_2` is Spanish — so plant lookups across languages work consistently.*
- *As a Garden-Center GM in Owl, I want to search "monstera" and find both the item with `DESCR='Monstera Deliciosa'` and the item with `ADDL_DESCR_2='Costilla de Adán'` (Spanish common name) — the multi-name discovery is the language layer over the catalog.*
- *As Q.6 vertical pack, I want item-code drift on the allow-list for Q-ME-01 (margin) and Q-CT-01 (tier-on-retail-pattern) so churning catalog doesn't fire spurious detections.*

## S.6 — eCommerce catalog surface

**Purpose.** Counterpoint runs a parallel eCommerce catalog with its own publish state machine, EC-specific flags on items, EC-specific category tree, and EC-specific inventory snapshots. Whether a tenant uses NCR Retail Online, a third-party connector (IceSync / Shopify integration / etc.), or DIY against the API, the EC fields surface through the same standard endpoints.

**Companion cards.** `ncr-counterpoint-api-reference` § "Ecommerce surface — Counterpoint as omnichannel hub", `garden-center-operating-reality` § "The omnichannel reality".

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| S.6.1 | eCommerce control read at tenant bootstrap | `GET /EC` | EC_CTL config; cached 24h → TBD: L4 implementation detail pending |
| S.6.2 | eCommerce category hierarchy ingestion | `GET /ECCategories` | EC_CATEG; parallel to Item categories (may share or diverge per tenant) → TBD: L4 implementation detail pending |
| S.6.3 | Per-item EC flag surfacing | `IM_ITEM.IS_ECOMM_ITEM`, `ECOMM_LST_PUB_STAT`, `ECOMM_TXBL_*`, `ECOMM_NEW`, `ECOMM_ON_SPECL`, `ECOMM_CHRG_FRT`, `ECOMM_DISC_ON_SAL`, `ECOMM_ITEM_IS_DISCNTBL` | The full EC field set per item → TBD: L4 implementation detail pending |
| S.6.4 | EC-inventory snapshot | `GET /Inventory/EC` | Separate from physical-store inventory state (held-for-fulfillment subset) → TBD: L4 implementation detail pending |
| S.6.5 | HTML description surfacing | `EC_ITEM_DESCR.HTML_DESCR` | Storefront display content; S surfaces, doesn't curate → TBD: L4 implementation detail pending |
| S.6.6 | EC publish-state-machine tracking | `ECOMM_NXT_PUB_UPDT` / `ECOMM_NXT_PUB_FULL` / `ECOMM_LST_IMP_TYP` | Substrate for monitoring sync failure (which Q.eCommerce-monitoring rules consume) → TBD: L4 implementation detail pending |

### User stories

- *As S, I want every item's EC publish state surfaced so Q can monitor for stuck-in-publishing items (which sometimes indicate a broken eCommerce sync — a known pain pattern in the user-pain-points wiki).*
- *As an Operator monitoring an omnichannel garden-center tenant, I want a per-tenant EC sync health dashboard showing items pending publish, items with publish failures, and items with EC-vs-physical inventory mismatches.*
- *As Owl, I want to answer "how is online performing vs in-store this season" by joining Document `EC` flags through to S's per-item EC attribution.*

## S.7 — Cross-module substrate contracts

**Purpose.** S supplies catalog substrate to nearly every other spine module. This L2 is the contract registry — what fields, what preservation rules, what freshness commitments. Symmetric to T.7 / C.6 / J.8b.

### L3 contracts (registry)

| ID | Contract | Owner downstream | What S promises |
|---|---|---|---|
| S.7.1 | `IM_ITEM` field-set preservation | T (item-ref join), Q (margin context), J (forecast context) | Every Item field surfaced verbatim; no normalization of attribute or descriptor fields → TBD: L4 implementation detail pending |
| S.7.2 | Category margin targets on every item join | Q (Q-ME-01) | `MIN_PFT_PCT` + `TRGT_PFT_PCT` joined to every transaction line at parse time → TBD: L4 implementation detail pending |
| S.7.3 | Mix-and-match group identity | Q (Q-MM-01, Q-MM-02), P (bundle pricing observations) | `MIX_MATCH_COD` exposed per item; bundle-membership table queryable → TBD: L4 implementation detail pending |
| S.7.4 | Fractional unit conversion factors | T (line surface), D (inventory deduction), Owl (analytics rollup) | `STK_UNIT`, `PREF_UNIT_NUMER/DENOM/NAM` available per item → TBD: L4 implementation detail pending |
| S.7.5 | Multi-name field convention per tenant | Owl (multi-language search), C (B2B catalog views) | Per-tenant convention captured at onboarding; surfaced via metadata table → TBD: L4 implementation detail pending |
| S.7.6 | Item lifecycle signals | J (replenishment exclusion for retired), Q (drift-tolerance in margin rules) | `STAT` + drift-suspicion flag → TBD: L4 implementation detail pending |
| S.7.7 | EC publish state | Q (sync-monitoring), Owl (omnichannel performance queries) | Per-item EC flag set + state-machine values surfaced → TBD: L4 implementation detail pending |
| S.7.8 | Vendor-item linkage | J (supplier scorecard) | `IM_VEND_ITEM` available without re-call to Counterpoint → TBD: L4 implementation detail pending |
| S.7.9 | Per-location item attribution | D (per-location inventory), J (per-location forecast) | `Items_ByLocation` materialized into CRDM, not re-fetched per query → TBD: L4 implementation detail pending |
| S.7.10 | Category-history-of-assignment | J (plan-vs-actual across hierarchy reorgs), P (seasonal-plan continuity) | Effective-dated category assignments per item → TBD: L4 implementation detail pending |
| S.7.11 | Cache-discipline metadata | All | `last_polled_at` per item-cache entity so consumers can suppress stale-substrate alerts (mirrors Q.1 freshness contract) → TBD: L4 implementation detail pending |

### User stories

- *As S, I want every contract in S.7 enforced via the contract test suite — adding a third POS adapter requires it to surface every S.7 field or it doesn't pass conformance.*
- *As Q, I want to assert at boot that S surfaces all contracted fields including `MIN_PFT_PCT` and mix-and-match group identity, so a silent S contract break shows up at startup not at first detection-miss.*
- *As J, I want vendor-item linkage on every item record so my recommendation generation never blocks waiting for a separate VendorItem call.*

## Canary Detection Hooks

| S Process | → Detection Surface | Signal Description |
|---|---|---|
| S.3 (Space utilization anomaly) | Q-IS rule family | Persistent out-of-stock in a planogram position (SKU allocated but zero SOH) is an accumulation signal for Q-IS shrink investigation |
| S.4 (Sales velocity by display) | Q-DM rule family | Unexpected velocity spikes in a specific display position (e.g., end-cap) not correlated with a promotion feed Q-DM-03 discount/manipulation detection |
| S.5.2 (Owl eCommerce integration) | Owl investigator surface | S.5.2 data surfaces in Owl's eCommerce investigation view. Explicitly: S feeds Owl's range-vs-online-availability display (investigator-surface L2), not a Chirp rule input |

## Additional User Stories

- *As a loss prevention analyst using Owl, I need to see which planogram positions are chronically out-of-stock relative to online availability so I can identify potential diversion at the display level.*

## Assumptions requiring real-customer validation

| ID | Assumption | What it blocks | Resolution path |
|---|---|---|---|
| ASSUMPTION-S-01 | Counterpoint Item endpoint full field-set — sample-derived schema may miss attribute/descriptor fields specific to L&G | S.1.1 completeness; downstream substrate contracts | Sandbox DB schema inspection |
| ASSUMPTION-S-02 | `IS_ECOMM_ITEM` semantic — does it gate the item from EC entirely or just the publish state | S.6.3 surface decisions | Sandbox EC test |
| ASSUMPTION-S-03 | Category margin targets actually tuned per customer or default values from API | S.2.3 (Q-ME-01 threshold realism) | Tenant onboarding observation |
| ASSUMPTION-S-04 | Mix-and-match bundle pricing rule storage — whether bundle target price lives on item, separate config, or computed at sale time | S.3.2 substrate path; Q-MM-01 bundle margin computation | Sandbox + sample Document with mix-match bundle |
| ASSUMPTION-S-05 | Fractional-unit conversion fields complete — `STK_UNIT`, `PREF_UNIT_*` cover all item types | S.4 entire L2 | Sandbox + variety of item types (plants, bulk, fertilizer, hard goods) |
| ASSUMPTION-S-06 | Serial-number tracking active for L&G vertical — likely rare except for high-value perennials | S.1.5/S.1.6 priority | Customer interview |
| ASSUMPTION-S-07 | Multi-name plant convention — which `ADDL_DESCR_N` or `ATTR_COD_N` slot holds botanical / Spanish / common (varies per customer / VAR) | S.5.2 entire L3; multi-language Owl search | **Per-customer at onboarding** — engagement-knowable, not platform-knowable |
| ASSUMPTION-S-08 | Item-status code list — `STAT='D'` for discontinued assumed; full enum unknown | S.5.5 retired-item handling | Sandbox DB inspection |
| ASSUMPTION-S-09 | Rapid POS proprietary item-side extensions — custom fields beyond stock 5×4 profile slots | S.1 + S.5 substrate completeness | Direct conversation with Rapid POS / customer |
| ASSUMPTION-S-10 | EC publish-state machine values — full enum of `ECOMM_NXT_PUB_*` | S.6.6 monitoring rules | Sandbox EC workflow test |
| ASSUMPTION-S-11 | Category hierarchy reorganization frequency — customer-specific operational decision | S.2.4 (effective-dated category assignments) priority | Customer onboarding observation |

**Highest-leverage gaps:** S-04 (mix-and-match bundle pricing storage) and S-07 (multi-name plant convention). S-04 is the load-bearing assumption for Q-MM-01 + the entire S.3 L2. S-07 is the load-bearing assumption for the multi-language Owl search experience and is engagement-knowable only — every customer is unique.

## Customer-specific overrides

*Empty until a real customer engagement starts. Format reserved:*

```
Customer: <name>
Multi-name field convention:
  ADDL_DESCR_1 → <botanical | Spanish | common | other>
  ADDL_DESCR_2 → <...>
  ADDL_DESCR_3 → <...>
  ATTR_COD_1 → <...>
  ATTR_COD_2 → <...>
Mix-and-match bundle pricing storage: <where bundles' target prices live>
Fractional-unit categories actively used: [perennials, bulk soil, fertilizer, ...]
Per-category margin targets (overrides to API defaults):
  <CATEG_COD>: MIN=<%>, TRGT=<%>
EC platform: <NCR Retail Online | Shopify connector | IceSync | DIY | none>
EC inventory model: <held-for-fulfillment | shared-with-physical | other>
Rapid POS proprietary extensions in scope: <field list | none>
Disabled S.x processes (with reason):
  S.x.x: <reason>
ASSUMPTION resolutions:
  ASSUMPTION-S-NN: resolved as <answer>; source: <evidence>
  ...
```

## Operating notes

**Cast of actors:**

| Actor | Role | Lives where |
|---|---|---|
| Catalog Ingester | S's poll-driven sync service | Canary-internal (S.1) |
| Category-Tree Maintainer | Hierarchy + margin-target sync | Canary-internal (S.2) |
| Mix-Match Group Resolver | Bundle-membership lookup service | Canary-internal (S.3) |
| Fractional-Unit Converter | Unit math service | Canary-internal (S.4) |
| EC Publish Monitor | Per-item EC state tracker | Canary-internal (S.6) |
| Operator | Catalog-config + onboarding | Canary side |
| Owl / Fox | Analyst-facing surface | Canary-internal |
| Garden-Center GM | Catalog and margin queries | Customer side |

**S is the most vertical-distinctive substrate module.** Three full L2 areas (S.3 mix-and-match, S.4 fractional units, S.5 lifecycle/drift) exist because L&G retail demands them. A non-garden vertical pack would re-shape these — a gun-store pack would emphasize serial-number tracking (S.1.5/S.1.6) and ATF-compliance category attributes; a wine pack would emphasize vintage and varietal attributes via the same `ADDL_DESCR_*` slots with different conventions.

**The category-margin-target contract (S.7.2) is the load-bearing producer-side bridge to Q.** Q.2.6 (margin-erosion) and Q-ME-01 specifically depend on category targets being inline on every item join. This is the highest-frequency contract S delivers — every transaction line carries it.

**The multi-name plant convention (S.5.2 + S.7.5) is engagement-knowable only.** Platform-level discovery cannot resolve which slot means what — every customer has unique conventions. Capture at onboarding, audit at customer review, never assume across customers.

## Related

- `Canary-Retail-Brain/modules/S-space.md` — L1 canonical spec
- `canary-module-s-space.md` — L2 Canary code/schema crosswalk
- `canary-module-q-functional-decomposition.md` — sister card; S.2.3 + S.7.2 (margin targets) + S.3 (mix-and-match) + S.5 (drift) drive Q rule families
- `canary-module-t-functional-decomposition.md` — sister card; T's transaction-line parse needs S's item context (T.7.8 contract)
- `canary-module-c-functional-decomposition.md` — sister card; R's tier-aware allow-lists join through S categories
- `canary-module-o-functional-decomposition.md` — sister card; J's like-item forecasting and vendor-scorecard depend on S.2 + S.7.8
- `ncr-counterpoint-api-reference.md` — full Item / Inventory / EC family detail
- `ncr-counterpoint-endpoint-spine-map.md` — per-endpoint × CRDM × spine map for Item family
- `ncr-counterpoint-rapid-pos-relationship.md` — feature-to-API mapping (mix-and-match, fractional, multi-name)
- `garden-center-operating-reality.md` — vertical reality (item-code drift, mid-season churn, multi-name conventions)
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — S row = ● Full direct
- (CATz) `method/artifacts/module-functional-decomposition.md` — the artifact template this card follows

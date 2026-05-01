---
title: P — Functional Decomp
classification: internal
type: wiki
sub-type: module-functional-decomposition
date: 2026-04-26
last-compiled: 2026-04-26
status: draft v1 (archetype — no real customer engagement)
module: P
solution-map-cell: ◐ Derived — no Counterpoint Pricing or Promotion endpoint family; derived from IM_ITEM price fields (PRC_1, REG_PRC, PREF_UNIT_PRC_1, LST_COST), CustomerControl multi-tier flags, and per-line PS_DOC_LIN_PRICE (the output of pricing rules as captured on sales tickets)
companion-modules: [O, Q, T, S, F, C]
companion-substrate: [ncr-counterpoint-api-reference.md, ncr-counterpoint-endpoint-spine-map.md]
companion-context: [retail-promotion-workflow.md, retail-merchandise-planning-otb.md, garden-center-operating-reality.md]
companion-canary-spec: Canary-Retail-Brain/modules/P-pricing-promotion.md
companion-canary-crosswalk: Brain/wiki/canary-module-p-pricing-promotion.md
companion-catz: CATz/proof-cases/specialty-smb-counterpoint-solution-map.md
methodology-note: "Sister card to d, a, c functional-decomp cards. Second fully-derived module in this batch. P observes pricing decisions — it reads the outcomes of Counterpoint's pricing rules from IM_ITEM price fields and per-line PS_DOC_LIN_PRICE, but Counterpoint exposes no promotion-rule API, no markdown endpoint, and no elasticity surface. Canary builds promotion lifecycle and markdown management Canary-native. Cross-cuts heavily with O.8 (promotional-demand isolation) and Q-DM family (discount/markdown rules)."
---

# Module P (Pricing & Promotion) — Functional Decomposition

> **Artifact layer.** Third of three Canary module artifact layers:
> 1. **Canonical spec** (vendor-neutral) — `Canary-Retail-Brain/modules/P-pricing-promotion.md`
> 2. **Code/schema crosswalk** (Canary-specific) — `Brain/wiki/canary-module-p-pricing-promotion.md`
> 3. **Functional decomposition** (Counterpoint-substrate-aware, L2/L3 + user stories) — *this card*

## Governing thesis

P is **the pricing observer** in the Canary spine — the module that turns Counterpoint's raw price data into actionable pricing intelligence. Against the Counterpoint substrate, P's coverage gap is total: Counterpoint has no Pricing endpoint family and no Promotion API. There is no endpoint for promotion rules, no endpoint for markdown workflows, and no endpoint for elasticity signals. What Counterpoint *does* expose is the **outcome** of its internal pricing engine: multi-tier retail price fields on each item (`IM_ITEM.PRC_1`, `REG_PRC`, `PREF_UNIT_PRC_1`) and — critically — the per-line actual-price-charged on every sales ticket (`PS_DOC_LIN_PRICE`). That's the substrate.

The gap between "I can see what price was charged" and "I can model promotion rules, markdown cadence, and elasticity" is where Canary does its work. P.1 (multi-tier price derivation) reads the static tier structure. P.2 (promotion lifecycle) builds the promotion calendar Canary-native from transaction evidence — Counterpoint doesn't surface promotion rules to the API, so Canary infers promotional periods from discount-vs-list-price variance on `PS_DOC_LIN_PRICE`. P.3 (markdown management) is a Canary-native lifecycle built on top of P.1's price snapshots. P.4 (elasticity tracking) is the analytical layer that O.8 depends on for promotional-demand isolation.

This architecture has an important implication for J: **J.8a's promotional-demand isolation requires that P's promotion calendar be populated.** If P doesn't have promotion windows identified, J cannot isolate promotional lift from base demand. The P→J cross-cut is load-bearing, not advisory.

## Executive summary

| Dimension | Count | Source |
|---|---|---|
| L2 process areas | 6 | This card |
| L3 functional processes | 33 | This card |
| Counterpoint endpoints in P's path | 0 dedicated; `IM_ITEM` price fields (PRC_1, REG_PRC, PREF_UNIT_PRC_1, LST_COST) via S; `PS_DOC_LIN_PRICE` via T | API reference |
| Counterpoint-substrate L2 areas | 1 (P.1 multi-tier price derivation, derived from S) | Item + price surface |
| Canary-native L2 areas | 3 (P.2 promotion lifecycle, P.3 markdown management, P.4 elasticity tracking) | Solution Map gap |
| Derived / cross-cut L2 areas | 2 (P.5 mass price maintenance cross-cut S, P.6 contracts) | Downstream consumers |
| Substrate contracts P owes downstream | 7 | This card §P.6 |
| Assumptions requiring real-customer validation | 9 | Tagged `ASSUMPTION-P-NN` |
| User stories enumerated | 44 | Observer + analyst + human-in-loop mix; cast in §Operating notes |

**Posture:** derived observer for the price-tier structure; Canary-native for promotion lifecycle, markdown management, and elasticity. The P.2 promotional-calendar build from transaction evidence (rather than from an explicit Counterpoint promotion API) is the most architecturally novel aspect of this module — it inverts the usual order of operations (normally you read rules and verify against transactions; here you infer rules from transaction evidence).

## Counterpoint Endpoint Substrate

| Counterpoint Endpoint | CRDM Entity | L2 Process Area |
|---|---|---|
| IM_ITEM (price fields) | Item price master | P.1 (Price catalog ingestion), P.4 (Elasticity baseline) |
| IM_ITEM (promo flags) | Promotional item flags | P.2 (Promotional window inference) |
| PS_DOC_LIN_PRICE | Transaction line price | P.2 (Price-realized vs. catalog), P.3 (Price-change detection) |
| PS_PRC_GRP | Price group / tier | P.1 (Tier-based pricing), P.5 (Linked-item deps) |
| IM_ITEM_ADD (vendor cost) | Vendor cost layer | P.4 (Margin-floor constraint on elasticity) |

## Canary Detection Hooks

P does not own detection rules — that is Q's surface. However, P is a first-class upstream signal supplier to several Q rule families and one J demand-isolation process. The hooks below document what P publishes and where it lands.

- **P.2.6 (Undeclared promotions) → Q-DM-03:** Undeclared promotional pricing events (price drop without a PS_PRC_GRP promotion record) are published as Q-DM-03 discount-manipulation signals to Chirp.
- **P.4.1 (Elasticity signal) → O.1.4:** P's elasticity coefficient for a SKU is published to O.1.4 as promotional-demand lift factor. This is a J dependency, not a Chirp signal — P does not directly write to Chirp.
- **P.3 (Price-change audit) → Q-IS rule family:** Bulk price changes (≥N items in a single session) are flagged as Q-IS accumulation signals, surfaced via Chirp's investigation queue.

## L1 → L2 → L3 framework

```
L1 (Solution Map cell)         P = ◐ Derived
                                 │  (no Counterpoint Pricing or Promotion endpoints;
                                 │   price-tier structure read from IM_ITEM via S;
                                 │   promotion periods inferred from PS_DOC_LIN_PRICE via T;
                                 │   markdown + elasticity are Canary-native)
                                 │
L2 (Process areas)               ├── P.1  Multi-tier price derivation          ◐ Derived (from S)
                                 ├── P.2  Promotion lifecycle                   ★ Canary-native (inferred from T)
                                 ├── P.3  Markdown management                   ★ Canary-native
                                 ├── P.4  Elasticity tracking                   ★ Canary-native
                                 ├── P.5  Mass price maintenance + linked items ◐ Derived (cross-cut S)
                                 └── P.6  Cross-module substrate contracts
                                 │
L3 (Functional processes)       (33 — enumerated per L2 below)
                                 │
L4 (Implementation detail)      Canary-Retail-Brain/modules/P-pricing-promotion.md
                                  + canary-module-p-pricing-promotion.md (schema crosswalk)
                                  + future Canary/docs/sdds/v3/pricing-promotion.md
```

## P.1 — Multi-tier price derivation

**Coverage posture.** ◐ Derived from S's item master. Counterpoint stores multiple retail price fields per item. Canary reads these from S's item publication and builds a price-tier model that maps each field to a tier name and customer eligibility.

**Companion cards.** `canary-module-s-functional-decomposition.md` (S publishes IM_ITEM including price fields), `canary-module-m-functional-decomposition.md` (M.5.5 price-tier assignment per commercial account — reads P.1's tier structure).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| P.1.1 | Read `IM_ITEM.PRC_1` (primary retail price) from S's item publication | S's item master | The standard retail price; the baseline from which all tier and discount derivation starts |
| P.1.2 | Read `IM_ITEM.REG_PRC` (regular price, pre-markdown) from S | S's item master | Distinct from PRC_1 when an active markdown is in effect; the gap between REG_PRC and PRC_1 is the markdown amount |
| P.1.3 | Read `IM_ITEM.PREF_UNIT_PRC_1` through `PREF_UNIT_PRC_N` (preferred-unit price tiers) from S | S's item master | Multi-tier pricing; tier 1 = standard retail, tier 2/3 = commercial / wholesale preferred pricing |
| P.1.4 | Read `IM_ITEM.LST_COST` (last cost) from S | S's item master | Cost basis per item; drives margin-at-price-tier calculation |
| P.1.5 | Derive price-tier-to-customer-tier mapping | P.1.3 tier fields + M.5.5 customer price-tier assignment | Maps Counterpoint's numeric price tiers (1/2/3) to Canary's semantic tier labels (retail / commercial / wholesale); merchant-configurable |
| P.1.6 | Calculate margin per price tier | P.1.1/P.1.3 price per tier − P.1.4 cost | Margin at each tier; drives P.3 markdown-impact and P.4 elasticity-adjusted-margin calculations |
| P.1.7 | Detect price-tier changes (price increases or decreases) | S event stream — IM_ITEM price field updates | PRC_1 or PREF_UNIT_PRC changes publish P.6.1 price-change events to downstream consumers |

### User stories

- *As P's Price Reader, I want every item's price-tier matrix (retail / commercial / wholesale at current and cost) maintained as a rolling snapshot, with the delta between REG_PRC and PRC_1 surfaced as an active-markdown indicator.*
- *As a Garden-Center Buyer in Owl, I want to ask "show me all items where our wholesale price is less than 30% margin" and get a ranked list with cost, tier price, and item category — so margin compression on commercial accounts is visible before it becomes a problem.*
- *As P, I want price-tier changes detected and published as events within one S-poll cycle — a supplier cost increase that erodes our margin at wholesale tier should trigger a P.4 elasticity re-evaluation, not wait for a monthly price audit.*
- *As C's Price-Tier Assigner, I want P.1.5's tier mapping so that M.5.5 can surface the correct preferred-unit price to T's transaction validator without duplicating the derivation.*

## P.2 — Promotion lifecycle

**Coverage posture.** ★ Canary-native. Counterpoint has no promotion-rule endpoint. Canary infers promotion windows from the evidence left in transaction data: when `PS_DOC_LIN_PRICE` diverges from `IM_ITEM.PRC_1` for a high proportion of transactions on a given item over a date window, Canary detects a likely promotional period. The buyer confirms or defines the promotion formally in Canary; the transaction evidence is the discovery surface, not the definition surface.

**Companion cards.** `retail-promotion-workflow.md` (promotion lifecycle — companion not lineage), `canary-module-o-functional-decomposition.md` (J.8a promotional-demand isolation reads P's promotion calendar — load-bearing contract), `canary-module-q-functional-decomposition.md` (Q-DM-01/02/03 read pricing decisions; Q-MM-01 reads bundle pricing).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| P.2.1 | Infer promotional windows from T's transaction price variance | `PS_DOC_LIN_PRICE` vs. P.1.1 PRC_1 | When actual-price-charged < list-price on >N% of transactions for an item in a date window, flag as LIKELY-PROMOTION. → TBD: L4 — promotional window inference algorithm: sliding-window price-change detection on IM_ITEM history; SDD crosswalk to canary-module-p-pricing-engine.md §P.2.1 (to be authored). |
| P.2.2 | Buyer confirms or creates promotion definition | Canary-native promotion builder (Owl/MCP) | Buyer converts LIKELY-PROMOTION flag into a formal promotion record: name, period, target items/categories, discount mechanism |
| P.2.3 | Support promotion types: fixed-price, percent-off, bundle, BOGO, threshold | Canary-native rule engine | All mechanics are Canary-internal; Counterpoint's POS executes the actual discount; Canary observes the outcome |
| P.2.4 | Publish promotion calendar to J and Q | P.6.3 promotion calendar contract | J.8a reads P's calendar for promotional-demand isolation; Q-DM family reads for discount-context validation |
| P.2.5 | Track promotion-period lift vs. pre-promotion baseline | T's transaction velocity before/during promotion | Per-item unit velocity comparison: pre-promotion baseline vs. in-promotion actual; feeds P.4 elasticity |
| P.2.6 | Detect undeclared promotions (high-discount-rate period with no promotion record) | P.2.1 LIKELY-PROMOTION + absence of P.2.2 confirmed record | Undeclared promotional periods are an LP signal (Q-DM family) and a O.8 contamination risk |
| P.2.7 | Post-promotion performance summary | P.2.5 lift data + P.1.6 margin impact | Per-promotion: units sold, revenue, margin impact, lift vs. baseline; available in Owl |

### User stories

- *As P's Promotion Detector, I want transaction-price variance patterns to surface LIKELY-PROMOTION flags automatically, so the buyer doesn't have to build a promotion record retroactively — the discovery comes from the data, the confirmation comes from the buyer.*
- *As a Garden-Center Buyer running a spring perennials promotion, I want to define the promotion in Canary (period, items, discount type) and have it propagate to J's promotion calendar immediately, so J.8a is isolating the promotional lift from the base forecast during the promotion window.*
- *As J's Demand Forecaster, I want P's promotion calendar as a first-class input — if P.2.4's contract fails (calendar not published, promotion record missing), J.8a should flag an isolation gap, not silently contaminate the base forecast.*
- *As an LP Analyst (Q.6), I want undeclared-promotion detection (P.2.6) surfaced as a Q-DM audit event — a period where 40% of perennial transactions went out at 30% off with no promotion record is either a pricing error or an undocumented discount.*
- *As a Buyer reviewing last season, I want per-promotion performance: units, revenue, margin impact, and demand lift vs. baseline — so I can decide whether to run it again and at what discount depth.*

## P.3 — Markdown management

**Coverage posture.** ★ Canary-native. Counterpoint executes markdown pricing internally (buyer edits PRC_1 or REG_PRC in the Counterpoint UI); it has no markdown-lifecycle endpoint. Canary observes markdown execution via P.1.2's REG_PRC vs. PRC_1 gap, and builds the proposal→approval→execution→analytics lifecycle on top.

**Companion cards.** `retail-merchandise-planning-otb.md` (markdown as OTB-event; markdown execution affects planned sales and remaining OTB), `canary-module-f-functional-decomposition.md` (F posts GL markdown-variance entries that P tracks for cost-complement impact).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| P.3.1 | Detect markdown events from P.1.2 REG_PRC vs. PRC_1 delta | S event stream — price field change | When REG_PRC is set and PRC_1 < REG_PRC, an active markdown is inferred; Canary names it and tracks it |
| P.3.2 | Markdown proposal workflow (Canary-native) | Buyer-initiated in Owl/MCP | Buyer proposes markdown: item(s), new price, period, reason; Canary records proposal with before/after pricing and margin impact |
| P.3.3 | Markdown approval gate | C's OTB co-ownership (markdown reduces on-hand value, affecting OTB) | Multi-tier approval mirrors O.3.6; markdown above dollar threshold requires buyer → dept head sign-off |
| P.3.4 | Markdown execution tracking | P.1.7 price-change event + P.3.1 detection | Markdown "executes" when S detects the price change in Counterpoint; Canary links the execution event to the proposal record |
| P.3.5 | Markdown performance tracking | T's velocity during markdown period vs. P.4 pre-markdown baseline | Did the markdown move units at the expected rate? Measures sell-through acceleration |
| P.3.6 | End-of-markdown / clearance management | Buyer-defined markdown end date or sell-through threshold | When a markdown has achieved its purpose (cleared EOL stock), Canary flags it for closure review |
| P.3.7 | Seasonal markdown calendar | Canary-native markdown plan per category by period | Garden-center seasonal cadence: spring-opening markdowns, end-of-season clearance, holiday-weekend discounts |

### User stories

- *As a Garden-Center Buyer preparing for end-of-season clearance, I want to submit a markdown proposal for all annuals above reorder-point at locations where the season ends in 3 weeks — Canary builds the proposed list, I review, approve, and execute in Counterpoint.*
- *As P's Markdown Tracker, I want markdown execution detected from the REG_PRC/PRC_1 delta within one S-poll cycle, linked to the pending proposal record — so markdown "executed in Counterpoint by the buyer" is captured automatically, not through manual Canary entry.*
- *As a Buyer, I want end-of-markdown performance: did the clearance move units faster than pre-markdown velocity, and at what margin? If the markdown didn't work, I need to know before committing to the same approach next season.*
- *As Finance, I want every markdown event linked to the Counterpoint price change and surfaced to F's GL posting pipeline — markdown execution is a GL event, not just a price change.*

## P.4 — Elasticity tracking

**Coverage posture.** ★ Canary-native. Counterpoint has no elasticity surface. Canary builds elasticity signals from the combination of P.3.5 (markdown performance vs. pre-markdown velocity) and P.2.5 (promotion lift vs. baseline). Elasticity is the analytical layer that connects P's pricing observations to J's demand forecast.

**Companion cards.** `canary-module-o-functional-decomposition.md` (O.1.4 demand forecast consumes P.4 elasticity; O.8.2 promotional-lift quarantine requires P.4 signals to attribute lift correctly).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| P.4.1 | Calculate price-elasticity coefficient per item | P.3.5 markdown velocity vs. P.1.6 pre-markdown baseline | Elasticity = % demand change / % price change; per-item-per-period; requires minimum markdown observations to be reliable |
| P.4.2 | Classify items by elasticity tier | P.4.1 coefficient | Elastic (coefficient > 1.0), inelastic (< 0.5), unit-elastic; classification drives markdown strategy guidance |
| P.4.3 | Surface elasticity signals to J's demand forecast | P.6.5 elasticity contract to J | O.1.4 consumes per-item elasticity tier to weight promotional-period demand appropriately |
| P.4.4 | Track category-level elasticity | P.4.1 aggregated to S's category hierarchy | Category-level elasticity is more stable than per-item; useful for new-item forecasting (O.1.6 like-item) |
| P.4.5 | Cold-start elasticity (insufficient markdown history) | Canary-native fallback | New items or items with < minimum markdown observations default to category-average elasticity. → TBD L4 — cold-start fallback: use category-median elasticity coefficient as prior; update with first 4 weeks of actuals via Bayesian update. See ASSUMPTION-P-07. |

### User stories

- *As P's Elasticity Engine, I want per-item price-elasticity coefficients calculated from markdown-period velocity vs. pre-markdown baseline, with a minimum-observations threshold before I call a coefficient reliable — no elasticity coefficient from a single markdown event.*
- *As a Buyer planning next spring's promotion strategy, I want to ask "which perennial categories are elastic enough that a 20% discount drives 40%+ volume increase?" — so I invest promotion budget in the elastic items, not the inelastic ones.*
- *As J's Demand Forecaster, I want P's elasticity signals to inform my promotional-demand projection — if perennials are elastic at 1.4x, O.8's pre-promotion demand projection should account for the expected lift, not just use the base forecast.*

## P.5 — Mass price maintenance + linked items

**Coverage posture.** ◐ Derived cross-cut with S. Mass price changes (supplier cost increase propagated across all items from that supplier, or category-level retail-price adjustment) are buyer-initiated in Counterpoint but affect P.1's price snapshots at scale. S's item-master pipeline is the substrate; P needs to handle bulk change events without treating them as individual markup alerts.

**Companion cards.** `canary-module-s-functional-decomposition.md` (S publishes bulk price-change events), `canary-module-o-functional-decomposition.md` (O.8.3 recurring-promotion blending benefits from P.5 linked-item awareness).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| P.5.1 | Detect bulk price-change events (N items changed in one S-poll cycle) | S event stream — multiple IM_ITEM price changes with shared CATEG_COD or supplier_id | Distinguishes individual price corrections from bulk supplier-cost-passthrough events |
| P.5.2 | Flag bulk changes for buyer review before margin-impact propagation | Canary-native bulk-change review queue | Bulk price increase on category may erode commercial-tier margins below threshold; surface before execution |
| P.5.3 | Track linked-item price dependencies | Canary-native — items sold as bundles or sets whose bundle price depends on individual pricing | When PRC_1 on a component item changes, Canary flags that the bundle price may be inconsistent (ASSUMPTION-P-08). → TBD: L4 — bundle price reconciliation schema: parent-item price drives child-item constraints; delta propagated via CRDM PriceEvent; conflict resolution: parent wins, child flagged for review. |

### User stories

- *As P's Bulk Change Detector, I want a single supplier cost passthrough that updates 200 items in Counterpoint recognized as a single bulk-change event — not 200 individual price-change events that flood the alert queue.*
- *As a Buyer, I want bulk price changes that erode commercial-tier margins below the configured floor (e.g., PRC_3 wholesale margin < 15%) flagged before they execute — so I can reprice the commercial tier before the next commercial-account transaction.*
- *As a buyer, I need Canary to detect when two active promotions apply to the same item and their combined discount exceeds the margin floor so that I can resolve the conflict before the transaction is processed.*
- *As a merchandising manager, I need to see when a buy-2-of-category-A-get-discount-on-category-B promotion produces unexpected cross-category margin erosion so I can adjust the promotion parameters.*
- *As a loss prevention analyst, I need Canary to detect when a buyer reverts a markdown in Counterpoint after it has already been applied to transactions so I can assess whether transactions occurred at the erroneous price.*

## P.6 — Cross-module substrate contracts

**Purpose.** P's most critical downstream contract is to J.8a — the promotional-demand isolation that prevents promotional lift from contaminating base forecasts. If P.6.3 fails, J's forecasts are wrong. The contracts below make this dependency explicit and testable.

**J.8a dependency (load-bearing, reciprocal):** P.6.3 promotion calendar contract is architecturally load-bearing to J demand forecasting (J.8a). P must publish promotion calendar records before J computes baseline demand. Failure of P.6.3 degrades J forecast accuracy.

| ID | Contract | Owner downstream | What P promises |
|---|---|---|---|
| P.6.1 | Price-change events per item (PRC_1, REG_PRC, tier prices) | T (validation of charged-vs-list price), S (SEL re-compile trigger), F (GL revaluation events) | Price-change event published within one S-poll cycle of any IM_ITEM price field update |
| P.6.2 | Active-markdown indicator per item (REG_PRC > PRC_1) | J.8a (promotional-demand isolation), Q-DM-01 (discount rule context) | Markdown active/inactive flag maintained per item; updated on every S-poll delta |
| P.6.3 | Promotion calendar per item per period | J.8a (LOAD-BEARING — isolation fails without this), Q-DM family | Calendar populated from P.2.2 confirmed records + P.2.1 LIKELY-PROMOTION flags; J.8a isolation gap flagged if calendar is empty during a P.2.6 undeclared-promotion period |
| P.6.4 | Markdown proposal + approval status | F (GL posting trigger on approval), C (OTB impact on markdown execution) | Proposal record linked to execution event; approval status propagated to F and C on change |
| P.6.5 | Elasticity coefficient per item per period | O.1.4 (demand forecast weighting), O.1.6 (like-item forecasting for new SKUs) | Coefficients published with confidence flag (reliable / cold-start-fallback); updated after each qualifying markdown event |
| P.6.6 | Price-tier-to-customer-tier mapping | M.5.5 (commercial account price tier) | Counterpoint's numeric tier (1/2/3) mapped to Canary's semantic tier label; updated when merchant reconfigures |
| P.6.7 | Undeclared-promotion detection events | Q-DM-03 (discount audit rule), J.8a (gap notification) | LIKELY-PROMOTION + no confirmed record → event published to Q and J with item, date-range, and discount-rate evidence |

### User stories

- *As J.8a's Demand Isolator, I want P.6.3 as a first-class dependency — if P's promotion calendar is empty for a period where Q-DM-03 (or P.2.6) detected an undeclared promotion, J.8a should halt isolation and surface a "calendar gap" warning rather than silently contaminating the base forecast.*
- *As Q's Detection Engine, I want P.6.2's active-markdown indicator as context for Q-DM-01 — a transaction where charged-price < list-price during an active markdown is expected; the same transaction outside a markdown window is a discount-audit event.*
- *As F's GL Engine, I want P.6.4 markdown-approval events to trigger the GL markdown-variance posting immediately on approval — not on the next price-change poll cycle.*

## Assumptions requiring real-customer validation

| ID | Assumption | What it blocks | Resolution path |
|---|---|---|---|
| ASSUMPTION-P-01 | `PS_DOC_LIN_PRICE` is populated on every transaction line in Counterpoint — assumed as the per-line actual-price-charged field | P.2.1 LIKELY-PROMOTION detection; P.4.1 elasticity calculation | Sandbox transaction inspection; confirm field is present and populated on a sample of transaction Documents |
| ASSUMPTION-P-02 | `IM_ITEM.REG_PRC` is consistently set by L&G Counterpoint operators when a markdown is active — some operators may edit PRC_1 directly without setting REG_PRC | P.3.1 markdown detection reliability | Customer interview at onboarding; if REG_PRC is not used, markdown detection falls back to PRC_1-vs-baseline comparison |
| ASSUMPTION-P-03 | Counterpoint stores price tier fields `PREF_UNIT_PRC_1` through `PREF_UNIT_PRC_N` on IM_ITEM — multi-tier pricing assumed present in the standard schema | P.1.3 tier structure and P.6.6 tier mapping | Sandbox schema inspection; confirm field count and naming |
| ASSUMPTION-P-04 | L&G garden-center operators actively use Counterpoint's multi-tier pricing for commercial accounts — some SMB operators may use flat pricing for all customers | P.1.5 tier derivation relevance; M.5.5 contract accuracy | Customer interview at onboarding; if flat pricing, P.1.5 is a no-op |
| ASSUMPTION-P-05 | Promotion-period inference from PS_DOC_LIN_PRICE variance is sufficiently reliable as a discovery signal — assumed N% discount rate threshold triggers the LIKELY-PROMOTION flag | P.2.1 false-positive rate and P.2.6 undeclared-promotion detection | Real customer transaction data; threshold calibration needed before promotion detection is production-reliable |
| ASSUMPTION-P-06 | Canary does not write price changes back to Counterpoint — P is read-only against the Counterpoint substrate | P design constraint (one-way read, consistent with NCR-as-competitor framing) | Confirmed by operating posture; Canary-native markdown proposals are executed by the buyer in Counterpoint UI at v2 (same pattern as O.5.1) |
| ASSUMPTION-P-07 | Category-average elasticity is an appropriate cold-start fallback for new items or items with insufficient markdown history | P.4.5 cold-start behavior | Calibration against real seasonal data from L&G merchant; category-level elasticity stability needs validation |
| ASSUMPTION-P-08 | Bundle or linked-item pricing is a meaningful operational pattern for L&G garden-center merchants | P.5.3 scope relevance | Customer interview; if bundles are not used, P.5.3 is deferred |
| ASSUMPTION-P-09 | Seasonal markdown cadence (spring opening, end-of-season clearance, holiday weekend) is sufficiently predictable for P.3.7 to build a calendar template | P.3.7 seasonal calendar design | Customer interview + prior-season markdown history inspection at onboarding |

**Highest-leverage gaps:** ASSUMPTION-P-01 (PS_DOC_LIN_PRICE population) is the single most critical platform-knowable assumption — if this field is not reliably populated, P.2.1's LIKELY-PROMOTION detection collapses and P.4.1's elasticity calculation has no substrate. Sandbox-resolvable before Phase 1 adapter work begins. ASSUMPTION-P-02 (REG_PRC usage) is engagement-knowable at onboarding and determines whether P.3.1 markdown detection works out of the box or requires a fallback path.

## Customer-specific overrides

*Empty until a real customer engagement starts. Format reserved:*

```
Customer: <name>
Multi-tier pricing in use: <yes (P.1.3 active) | no — flat pricing only>
REG_PRC usage: <consistent | inconsistent — P.3.1 fallback mode>
Promotion definition: <buyer-confirms LIKELY-PROMOTION (default) | buyer-creates-proactively | both>
Markdown approval required: <yes — buyer threshold $<N> | no — auto-execute>
Seasonal markdown template: <spring/end-of-season/holiday-weekend | custom per customer>
Bundle pricing in scope: <yes — P.5.3 active | no>
Elasticity minimum observations: <N markdowns before coefficient is reliable (default: 3)>
Undeclared-promotion detection: <enabled (default) | disabled>
Disabled P.x processes (with reason):
  P.x.x: <reason>
ASSUMPTION resolutions:
  ASSUMPTION-P-NN: resolved as <answer>; source: <evidence>
  ...
```

## Operating notes

**Cast of actors:**

| Actor | Role | Lives where |
|---|---|---|
| Price Reader | Reads S's item-master price fields, publishes price-change events | Canary-internal (P.1) |
| Promotion Detector | Infers LIKELY-PROMOTION from PS_DOC_LIN_PRICE variance | Canary-internal (P.2) |
| Markdown Tracker | Detects markdown events from REG_PRC/PRC_1 delta | Canary-internal (P.3) |
| Elasticity Engine | Calculates price-elasticity coefficients from markdown performance | Canary-internal (P.4) |
| Buyer / Merchandiser | Confirms promotion records, approves markdowns, reviews bulk changes | Customer org |
| Owl / Fox | Pricing intelligence surface + markdown calendar + promotion ROI | Canary-internal |
| J's Demand Forecaster | Consumes P.6.3 promotion calendar and P.6.5 elasticity (P is J.8a's dependency) | Canary-internal |

**P is an observer module with one bidirectional dependency.** Counterpoint executes pricing; Canary observes. The one exception is the markdown proposal workflow (P.3.2) — the buyer drafts a markdown in Canary, but execution happens in Counterpoint UI (buyer sets PRC_1), and Canary detects the execution via P.3.1. This mirrors J's v2 buyer-mediated pattern (O.5.1) and carries the same assumption: buyers will tolerate "plan in Canary, execute in Counterpoint."

**The J.8a dependency is load-bearing and must be surfaced as a Phase III contract test.** J.8a's promotional-demand isolation fails silently if P's promotion calendar is incomplete. The "J forecast contaminated by undeclared promotion" failure mode is one of the hardest bugs to diagnose in a production system because the data looks plausible — it's just wrong. P.6.3 and P.6.7 exist to make this failure mode detectable. The corresponding contract test must confirm that J.8a halts isolation and surfaces a warning when the calendar is empty during a suspected promotion period.

**Garden-center seasonal pricing reality is distinctive.** L&G operators run 2-4 major markdown events per year (spring opening, Mother's Day weekend, fall clearance, holiday-weekend discount days). These are predictable enough that P.3.7 can build a seasonal calendar template, but their depth and timing vary enough by location and year that the template is a starting point, not a fixed schedule. Elasticity on live goods is also seasonally dependent — a 20% off perennial in week 3 of spring moves very differently than the same item in week 10.

## Related

- `Canary-Retail-Brain/modules/P-pricing-promotion.md` — L1 canonical spec
- `canary-module-p-pricing-promotion.md` — L2 Canary code/schema crosswalk
- `canary-module-o-functional-decomposition.md` — sister card; J.8a (promotional-demand isolation) is P.6.3's primary consumer — load-bearing contract; O.1.4 and O.1.6 consume P.6.5 elasticity
- `canary-module-q-functional-decomposition.md` — sister card; Q-DM-01/02/03 consume P.6.2 (active markdown), P.6.3 (promotion calendar), P.6.7 (undeclared-promotion events); Q-MM-01 reads bundle pricing
- `canary-module-s-functional-decomposition.md` — sister card; P reads IM_ITEM price fields via S; P.5.1 bulk-change detection reads S event stream
- `canary-module-f-functional-decomposition.md` — sister card; F's GL posting pipeline receives P.6.4 markdown-approval events
- `canary-module-m-functional-decomposition.md` — sister card; M.5.5 price-tier assignment reads P.6.6 tier mapping; C's OTB co-ownership is invoked by P.3.3 markdown approval gate
- `canary-module-t-functional-decomposition.md` — sister card; T's transaction stream is P.2.1's LIKELY-PROMOTION substrate and P.4.1's elasticity calculation input
- `retail-promotion-workflow.md` — promotion lifecycle companion; companion not lineage
- `retail-merchandise-planning-otb.md` — OTB as markdown-event context for P.3.3 approval gate
- `ncr-counterpoint-api-reference.md` — IM_ITEM price field context; confirms no Pricing/Promotion endpoint family
- `ncr-counterpoint-endpoint-spine-map.md` — P-column placement (no dedicated endpoints; derived via S and T)
- `garden-center-operating-reality.md` — seasonal markdown cadence; live-goods elasticity; commercial-account pricing reality
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — P row = ◐ Derived; this card is the L2/L3 expansion of that cell

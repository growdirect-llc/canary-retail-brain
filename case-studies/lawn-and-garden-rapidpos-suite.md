---
type: case-study
classification: internal-decision-record
date: 2026-04-25
status: completed-design
related-linear: GRO-588
related-adr: case-studies/canary-ncr-product-line-decision.md
methodology: CATz Phase II — to-be workshop artifact + solution map
author: Geoffrey C. Lyle
---

# Case Study: Lawn-and-Garden RapidPOS Suite — Canary as the L&G Operating Platform

## 1. Executive Summary

Canary is not a loss-prevention point solution for lawn-and-garden specialty retail. It is the operating platform — the full 13-module Canary spine (T R N A Q C D F J S P L W) running on top of NCR Counterpoint, delivered through Bart Monahan's Rapid POS VAR channel. The "RapidPOS Suite" is the productization of that posture: a Counterpoint adapter plus an L&G domain layer that knows seasonality, three-tier customer pricing, mix-and-match flats, perishable shrink, and the cash-and-paper culture at the back door. Phase 1 (T R F L N) ships in Q3 2026 and produces operating value within sixty days of go-live; Phase 4 (A C Q) closes the suite in Q2 2027 with the loss-prevention rule catalog firing on top of a fully populated CRDM. The Boutique H&G chain is the anchor first deployment — multi-store, Counterpoint-running, Bart-channel-delivered. Once that proof point lands, the playbook scales across the ~1,200 US garden-center sites and the broader ~9,000 Counterpoint specialty SMB base without rewriting the suite.

---

## 2. Vertical Reality — the L&G Operator's Day

A garden-center operator does not run a generic SMB retail business. Seven operational facts shape every product decision Canary makes for this vertical, and the 13-module suite is structured around them.

**Seasonality compresses the year.** April 1 through September 30 produces 70-80% of annual revenue for a temperate-zone garden center. October through March is the trough — cash conservation, end-of-season clearance, holiday-décor compression in November and December. Analytics priorities follow the season: peak-season focus on labor scheduling, replenishment velocity, perishable shrink, and loss-prevention; off-season focus on planning, vendor reconciliation, and historical analysis. A platform that doesn't accommodate the seasonal tilt produces noise during the trough and misses signal during the peak.

**Perishables run on a clock.** Live plants have shelf life — annuals at four weeks, perennials at six to eight, tropicals temperature-dependent. Chemicals carry regulatory shelf-life (EPA-registered pesticides, fertilizers with degradation curves, California Prop 65 restricted items). Markdown cadence is a real workflow: weekly markdowns on perishables in active inventory, end-of-season liquidation on remaining stock, dead-count write-offs on what didn't move. The ledger has to track not just quantity but freshness state. Module S (catalog) carries the perishable flag; Module Q (loss prevention) tracks dead-count baselines as informational signal, not fraud; Module P (pricing) carries the markdown cadence.

**Customers come in three tiers.** Retail walk-ins are the highest-volume, lowest-ticket segment — weather-driven, frequency-high, average-ticket-low. Landscapers buy at volume on account, with multi-tier wholesale pricing, monthly invoicing, and AR balances. Commercial accounts (HOAs, property managers, municipalities) sit between — multi-PO, project-based, large ticket, slower-turn. The same plant has three prices. Counterpoint's `CATEG_COD` on the Customer record carries the tier; Module R (customer) and Module C (commercial) split the load between retail and B2B handling.

**Mix-and-match flats are the unit of sale.** "Any 10 4-inch perennials for $25" — mixed across SKUs, with the bundle margin positive even though individual line margins go negative. Counterpoint's `MIX_MATCH_COD` field on items + transaction lines exposes the grouping; Q rules built without awareness of mix-and-match will fire false positives on every bundle scan. Module S models the groups, Module P prices them, Module Q allow-lists the negative-line-margin pattern within bundles.

**Cash and paper are operational baseline.** POS isn't always live — power outages, network drops, peak-rush manual ringing, farmers-market events held off-site. Paper backup workflows exist and produce out-of-band tickets that get reconciled into Counterpoint after the fact. Vendor receipts at the back door are sometimes paid in cash to specialty growers who don't issue formal invoices. Q rules built for digital-first environments will misfire on these patterns. The garden-center allow-list framework in `canary-module-q-counterpoint-rule-catalog.md` is the answer.

**Alternative payment rails substitute for cash.** Zelle, Venmo, Cash App, and Bitcoin Lightning are operationally normal for landscaper invoicing and ad-hoc vendor payments. Counterpoint's `PayCode` taxonomy supports manual recording of these tenders. Native integration (auto-capture from the wallet API) is a Canary value-add — POS-agnostic, not gated by Counterpoint's surface. This is the Module F extension lane that opens up after Phase 1.

**Multi-store distribution is normal.** A 3-15 location L&G chain runs inter-store transfers — moving high-velocity inventory between stores during peak season, consolidating slow-movers at season end. Counterpoint's `InventoryLocations`, `Items_ByLocation`, and transfer Document types cover the substrate. Module D sits on top.

**Seasonal staff doubles the headcount.** April through June is mass hiring — part-time labor, seasonal cashiers, plant-care help. Turnover is high, training is shallow, and Q-rule false-positive sensitivity goes up because new employees produce different patterns than tenured staff. Module L (labor) carries the seasonal-staff flag; Q-rule allow-lists widen during peak hiring to keep the false-positive rate tractable.

These seven facts are the operating reality the L&G suite is built for. Every module below is read against them.

---

## 3. Suite Composition — the 13-Module Spine on Counterpoint

Canary's 13-module spine maps to Counterpoint endpoints with high fidelity for ten modules, derived coverage for one (P), and Canary-native coverage for two (L, W). The L&G-specific value layer sits on top.

| Module | Spine Letter | L&G Value Delivered | Counterpoint Upstream | Canary-Native Layer | Phase |
|---|---|---|---|---|---|
| **Transactions** | T | Sales, returns, voids, line items, payments, audit log per ticket — the operating substrate | `Document*` family (omnibus DOC_TYP coverage) | TSP Counterpoint adapter; CRDM event normalization; POSLog 2.2.1 alignment | 1 |
| **Customer** | R | Three-tier customer model (retail/landscaper/commercial); loyalty; AR for landscapers | `Customer*`, `CustomerControl`, `Customer_OpenItems`, `AR_CUST.CATEG_COD` for tier | Tier resolver; B2B vs retail behavior split; loyalty-points reconciliation | 1 |
| **Device** | N | Stores + stations + devices; multi-store hierarchy via Workgroup | `Store*`, `Store_Station`, `Device_Config`, `Workgroup` | Hierarchy projection; per-store config surfacing; device-health observability | 1 |
| **Asset Management** | A | Non-saleable equipment (greenhouses, tractors, fixtures, displays) tracked alongside inventory | `Items` filtered on non-saleable flag (`ITEM_TYP` + custom attributes) | Asset lifecycle layer; depreciation hooks; fixture-to-store binding | 4 |
| **Loss Prevention** | Q | Perishable shrink baselines, employee discount abuse, voided-tender patterns, mix-and-match abuse, seasonal-staff fraud, restricted-item compliance | Consumes T + R + L + N + S — no Counterpoint-specific endpoints | Canary-native rule engine; 24 rules across 11 categories; L&G allow-list framework | 4 |
| **Commercial** | C | B2B landscaper accounts, PO matching, AR balances, account-charge tenders, project billing | `Customer*` with B2B flag, `Customer_OpenItems`, `PayCode*` (account tenders), `Document*` with AR_DOC type | B2B workflow surface; landscaper-tier behavior; project-bundling | 4 |
| **Distribution** | D | Multi-store transfers, inter-store inventory, in-transit tracking, low-stock routing | `InventoryLocations`, `Items_ByLocation`, `Document*` with XFER type | Transfer-loss aggregation; per-route shrinkage; replenishment routing | 3 |
| **Finance** | F | Payments, tenders, gift-card-as-tender, day-end close, perpetual cost ledger | `PayCode*`, `GiftCard*`, `Document*` payment detail, `Tax*` | Per GRO-526 ADR Option C — Canary perpetual layer, merchant GL via OAuth (QBO/Xero); alt-payment-rail capture | 1 |
| **Forecast / Order** | J | Seasonal demand forecast, weather-adjusted replenishment, vendor PO, specialty-grower onboarding | `Vendor*`, `PO*`, `Document*` with PO/RECVR types, `VendorItem` (verify) | Seasonal forecast engine; weather-adjustment overlay; specialty-grower flag-and-ingest | 3 |
| **Space, Range, Display** | S | Item hierarchy with perishable flag, mix-and-match groups, planogram, plant attributes | `Item*`, `ItemCategor*`, `Item_Images`, `MIX_MATCH_COD`, attribute codes | Perishable lifecycle; M&M group resolver; plant-attribute taxonomy | 2 |
| **Pricing / Promotion** | P | Three-tier customer pricing, mix-and-match flat pricing, seasonal markdown cadence | **Derived** — no Counterpoint Pricing/Promotion endpoint family. `Item.REG_PRC` + `CustomerControl` + `Customer.CATEG_COD` | Pricing resolver materialized in CRDM; markdown-cadence scheduler; bundle-pricing engine | 2 |
| **Labor / Workforce** | L | Employee, timecard, schedule, seasonal-staff flag, labor cost per shift | **None** — Counterpoint REST has no Employee/Timeclock/Schedule endpoints | **Canary-native module** per SDD §6.12 option (d); POS-data-native scheduling from CRDM sales velocity | 1 (basic), 6+ (full) |
| **Work Execution** | W | Daily ops checklists, perishable rotation tasks, store-floor workflows, opening/closing routines | **None** — Counterpoint REST has no task/checklist/workflow endpoints | **Canary-native module** per SDD §6.13 option (d); parked or 4 if prioritized | 4 (parked) |

**Read of the table.** Counterpoint provides direct or substrate-level coverage for ten of the thirteen modules. Module P is derived (no promotion endpoint exists; pricing resolves at consume-time from Item + CustomerControl + Customer). Modules L and W are real coverage gaps in the Counterpoint API surface — neither has Employee/Timeclock/Schedule endpoints (L) nor task/workflow endpoints (W). Both gaps become Canary-native product wedges, escalated to the founder before scope commits per memory `project_canary_native_labor_module_opportunity.md`. The L&G suite ships with a basic L module (employee + manual timecard ingestion) in Phase 1 to keep Q rules functional, with the full Canary-native L surface as a Phase 6+ build.

---

## 4. Vertical-Specific Q-Rules — the L&G-Critical Subset

The Module Q rule catalog (`canary-module-q-counterpoint-rule-catalog.md`) carries 24 rules across 11 categories. Nine of those are L&G-critical — they exploit Counterpoint's substrate richness and require the garden-center allow-list framework to keep the false-positive rate tractable.

| Rule ID | Name | L&G Specifics |
|---|---|---|
| **Q-DM-01** | Discount-cap exceeded | Landscaper-tier customers (CATEG_COD = WHOLESALE) legitimately receive deeper discounts; allow-list per-tier override. False positives drop sharply when tier-aware. |
| **Q-DM-02** | Markdown-and-buy pattern | Peak-season clearance markdowns are normal; rule keys on employee-or-colleague purchase within 24h of the markdown. Allow-list documented end-of-season clearance (`STAT = D`). |
| **Q-VR-01** | Voided sale, no original | Paper-backup tickets reconciled into Counterpoint after the fact may surface as voids without origin links. Allow-list documented manager-corrected entries with reason code. |
| **Q-IS-02** | Cash-paid receiver classification (NOT fraud) | The garden-center allow-list rule. Cash payments to specialty growers at the back door are operationally normal. Routes to ad-hoc-vendor-payment review queue, not the fraud queue. |
| **Q-IS-04** | Dead-count / live-goods write-off (informational) | Plant write-offs are normal and seasonal. Rule tracks per-category baseline (perennials 8% spring, 15% summer) and only flags spike deviations. |
| **Q-MM-01** | Mix-and-match producing below-cost line | Individual line margins go negative inside legitimate bundles. Allow-list bundle-level margin (only flag when the BUNDLE goes negative, not the line). |
| **Q-MM-02** | Mix-and-match used outside grouping | M&M code applied to a line whose item isn't in the group — manual-override exploit pattern. No allow-list; this one fires clean. |
| **Q-CT-01** | Wholesale tier on retail-pattern customer | Landscaper-tier abuse — retail walk-in customer flagged WHOLESALE but transaction pattern is single-line, low-dollar, retail SKUs. Aggregates to per-customer review. |
| **Q-RESTRICTED-ITEM-SALE** | Restricted-item sale without override | Cataloged 2026-04-25 under the new Compliance category (P1, regulatory exposure). Garden centers carry many EPA-registered pesticides and herbicides; California stores carry heavy Prop 65 exposure on amendments and fertilizers. The `restricted_items_authorized` manager override IS the forensic record — its absence on a restricted-item line is the detection. Allow-list is store-level flag activation (a Tennessee store doesn't activate `prop_65`). |

One more rule deserves mention as L&G-relevant but not in the nine-rule core:

- **Seasonal-staff onboarding fraud** (extension of Q-VR-03 / Q-DS-03) — first-30-day employee tender patterns and void clusters; baseline shifts during April-June peak hiring.

The garden-center allow-list framework in §"Garden-center allow-list framework" of the rule catalog wiki is pre-loaded for any L&G deployment. The framework covers cash-vendor-payment, manual-entry noise, item-code drift, live-goods write-off, and mix-and-match expected overlap. Phase 4 deployment activates rules in dry-run for thirty days, then promotes to active alerting per the per-customer cutover behavior.

---

## 5. Onboarding Story — 90-Day Deployment

A new L&G chain comes online in twelve weeks. Calendar tracks the Counterpoint substrate phasing already drafted in `Brain/dispatches/2026-04-25-ncr-counterpoint-*.md`.

**Weeks 1-2 — Counterpoint API access stand-up.** Customer's Counterpoint license is verified for the API user option in `registration.ini` (paid add-on; gating precondition). NCR-issued APIKey installed on the customer's Counterpoint API server. TLS 1.2 verified per `InstallationAndConfiguration/TLS1.2.md`. Canary-side credentials stored encrypted in the standard secret-store with `<company>.<username>` Basic + APIKey header bootstrap. Connection runbook (`Brain/wiki/ncr-counterpoint-connection-runbook.md`) carries the 401/403/404 disambiguation flow. Bart's Rapid POS lab is the candidate sandbox if the customer's production isn't ready for adapter polling on day one.

**Weeks 3-4 — Data sync, first transactions in CRDM.** Counterpoint adapter polling worker stands up. Phase 0c work plugs into the now-source-aware downstream (Phase 0b registers `'counterpoint'` as a source, extends CHECK constraints, and routes via per-source dispatch tables per the audit). First Document* polls populate `Events.transactions` in CRDM; first Customer* polls populate `People.customers` with tier resolution; first Item* polls populate `Things.items` and `Things.item_categories`. Schema-drift fingerprint runs per-source (no spurious alerts on Counterpoint payload shape). Multi-company decision applied if the customer runs multiple Counterpoint companies.

**Weeks 5-8 — Phase 1 priority modules online.** Module T (transactions) at full coverage via `/Documents`. Module R (customer) with three-tier resolution. Module F (finance) with PayCode + GiftCard ingestion and day-end close reconciliation. Module N (devices) with store hierarchy via Workgroup. Module L at basic coverage (employee + manual timecard ingestion) so Q rules don't hit null employee references. First Q rules fire in **dry-run** mode against backfilled Counterpoint data. Operator reviews dry-run output; tunes thresholds and allow-lists. By end of week 8, Q rules promote to active alerting per-rule based on operator confidence.

**Weeks 9-12 — Phase 2 catalog modules.** Module S (item hierarchy with perishable flag, mix-and-match groups, plant attributes via `ATTR_COD_1/2`). Module P (pricing) materialized as a CRDM resolver — base price from Item, tier from CustomerControl + Customer.CATEG_COD, markdown cadence loaded into the seasonal scheduler. Three-tier customer pricing live for landscapers and commercial accounts. Mix-and-match flat tracking active. By end of week 12, the customer is running Phase 1 + Phase 2 in production.

**Weeks 13+ — Phases 3 and 4 phased per merchant pace.** Phase 3 (D distribution + J forecast) for chains with multi-store transfer activity. Phase 4 (A asset, C commercial, Q at full L&G allow-list) once the substrate is stable. Per-customer Phase 5 cutover playbook (`Brain/dispatches/2026-04-25-ncr-counterpoint-cutover.md`) drives the per-rule promotion cadence.

Operator surface throughout — MCP tools per the Q catalog (`query_detections`, `tune_rule_threshold`, `add_allow_list_entry`, `dry_run_rule`) keep the catalog tunable without redeploys.

---

## 6. Pricing & Packaging — Tier Sketch

The 13-module suite ladders into four packaging tiers. Concrete pricing math is out of scope for this playbook; the package shape is what's load-bearing.

```
┌─────────────────────────────────────────────────────────────────────┐
│ Tier 1 — LP-Only                                                    │
│   Modules: Q + Fox dashboards                                       │
│   Substrate: T + R + N (minimum to feed Q)                          │
│   Target: customers who already have analytics + just want LP       │
│   Pricing: matches current Canary LP pricing                        │
├─────────────────────────────────────────────────────────────────────┤
│ Tier 2 — Operating Suite                                            │
│   Modules: T + R + N + F + L(basic) + S + P + Q + Fox               │
│   Substrate: full Phase 1 + Phase 2 coverage                        │
│   Target: L&G full-stack — single-store and small chains            │
│   Pricing: LP tier + operating-suite uplift                         │
├─────────────────────────────────────────────────────────────────────┤
│ Tier 3 — Distribution Suite                                         │
│   Modules: Operating Suite + D + J                                  │
│   Substrate: Phase 3 coverage                                       │
│   Target: multi-store chains (3-15 locations) with transfers + PO   │
│   Pricing: Operating Suite + per-store add-on                       │
├─────────────────────────────────────────────────────────────────────┤
│ Tier 4 — Enterprise                                                 │
│   Modules: Distribution Suite + A + C + W                           │
│   Substrate: Phase 4 + parked Phase W if activated                  │
│   Target: chains with B2B-heavy mix, asset tracking, store-ops      │
│   Pricing: Distribution Suite + enterprise uplift                   │
└─────────────────────────────────────────────────────────────────────┘
```

**Channel posture.** Tier 1 ships direct-to-merchant via Bart's Rapid POS VAR channel. Tier 2 and above bundle with VAR-led implementation services — the CATz Phase II to-be workshop runs alongside the deployment, and Bart's team carries the on-site customer-relationship surface.

**Guardrail.** Per memory `project_raas_positioning_guardrail`, RaaS is unaudited at this stage and cannot be cited as a substrate primitive in pricing claims. Pricing copy stays grounded in the operational suite and the L&G domain layer; the substrate language stays internal.

---

## 7. Competitive Position

L&G chains running Counterpoint have five alternatives Canary has to displace. None of them deliver the full operating suite.

**NCR Voyix** is the structural friction. Voyix is Counterpoint's parent corporation and the direct competitor for SMB analytics — they're pushing their own analytics stack onto the Counterpoint installed base. Per memory `project_ncr_voyix_is_competitor.md`, partnership posture is unworkable; Canary's access strategy routes through the customer license-holder, not through NCR partnership programs. Voyix wins on parent-vendor relationship; Canary wins on customer-routed access plus a deeper L&G domain layer that Voyix's general-purpose analytics doesn't carry.

**Counterpoint native reporting** is operational, not analytical. Standard Counterpoint reports cover sales by category, inventory on hand, customer aging — the day-to-day operational surface. They don't carry detection rules, don't surface mix-and-match abuse patterns, don't track perishable shrink baselines, don't run weather-adjusted forecasts. Counterpoint reports answer "what happened"; Canary answers "what's wrong and what to do about it." These are not the same product.

**Excel and manual workflows** are the de facto state for most SMB L&G chains today. The owner exports Counterpoint data to Excel weekly, manually reconciles, and produces ad-hoc dashboards. The labor cost is real and invisible — a part-time bookkeeper or the owner's own time. Canary replaces that labor with a continuous platform; the value proposition is direct and quantifiable in hours-per-week saved.

**LP-only point solutions** — Agilence, Profitect, NEXCOM, similar — handle Module Q at varying depth but don't touch the rest of the spine. They sell into the same Counterpoint base. The competitive differentiation is the suite: a customer choosing Canary doesn't have to integrate Agilence for LP plus a separate forecasting tool plus a separate labor scheduler plus a separate B2B account handler. One platform, one Counterpoint adapter, one operational surface.

**POS-vendor-agnostic platforms** — Square's analytics, Shopify POS reporting, generic BI on top of any POS — are not optimized for specialty retail. They handle generic SMB retail well but don't know about mix-and-match flats, three-tier customer pricing, perishable shrink, restricted-items compliance, or seasonal-staff patterns. The L&G domain layer is what makes Canary tractable for this vertical specifically; without it, the customer is back to building their own logic on top of generic infrastructure.

**Why Canary wins.** Full suite, not point solution. L&G-specific Q rules with allow-lists tuned for the vertical. Customer-routed access strategy that doesn't depend on NCR-Voyix-corporate cooperation. Bart Monahan's Rapid POS as a friendly VAR channel — distribution, lab access, customer pipeline rolled into one. Canonical positioning already aligned ("multi-store merchandising and store ops for SMB on the Counterpoint API backbone"). The competitive moat compounds as the suite ships: Phase 1 wins on substrate, Phase 2 on catalog, Phase 4 on LP detection depth. By the time a competitor would build the equivalent, the installed base has already consolidated.

---

## 8. Phasing Map — Which Modules Light Up When

```
Q3 2026                Q4 2026                Q1 2027                Q2 2027
─────────────────────  ─────────────────────  ─────────────────────  ─────────────────────
Phase 0 (substrate)    Phase 2 (catalog)      Phase 3 (operations)   Phase 4 (tertiary)
TSP + CRDM             P (derived) + S        D + J                  A + C + Q
GRO-558 in flight      ─────────────────────  W parked               ─────────────────────
─────────────────────                                                Phase 5 (cutover)
Phase 1 (priority)                                                   per-customer runbook
T + R + F + L + N                                                    H&G first deployment
─────────────────────
```

| Phase | Module Coverage | Quarter | Status |
|---|---|---|---|
| **0** | TSP + CRDM substrate (source-aware ingress, dispatch, validators, resolvers) | Q3 2026 | Phase 0a complete; 0b in progress; 0c queued under GRO-558 |
| **1** | T (transactions), R (customer), F (finance/tender), L (labor, basic), N (devices) | Q3 2026 | Dispatch drafted: `2026-04-25-ncr-counterpoint-priority-modules.md` |
| **2** | P (pricing, derived), S (catalog) — H&G-critical for tier pricing + mix-and-match | Q4 2026 | Dispatch drafted: `2026-04-25-ncr-counterpoint-catalog-modules.md` |
| **3** | D (distribution), J (forecast/order) — multi-store chains; W parked per SDD §6.13 | Q1 2027 | Dispatch drafted: `2026-04-25-ncr-counterpoint-operations-modules.md` |
| **4** | A (asset), C (commercial/B2B), Q (loss prevention with full L&G allow-list) | Q2 2027 | Dispatch drafted: `2026-04-25-ncr-counterpoint-tertiary-modules.md` |
| **5** | Cutover + per-customer runbook + monitoring + Boutique H&G first deployment | Q2 2027 | Dispatch drafted: `2026-04-25-ncr-counterpoint-cutover.md` |

Phases 1, 2, and 3 can run in parallel after Phase 0 if multiple sessions or engineers are available. Phase 4 (especially Q) depends on Phases 1-3 outputs because Q consumes a populated CRDM. Phase 5 depends on all prior phases.

The L&G suite is structured so that a customer can land at Tier 2 (Operating Suite — Phase 1 + 2) without ever needing Phase 3 if they're a single-store operator, and ladder up to Tier 3 (Distribution Suite — adds Phase 3) only when they grow into multi-store distribution. The phasing is the packaging.

---

## 9. Decision Gates

Five gate criteria govern when the L&G playbook scales beyond the Boutique H&G chain anchor deployment.

1. **Boutique H&G chain Phase 0-4 completes successfully.** Adapter stable in production, Phase 1 priority modules producing parity-quality detections to the Square baseline within sixty days of go-live, Phase 2 catalog modules covering tier pricing and mix-and-match. Phase 4 Q rules active under the L&G allow-list framework. Customer is running stable end-to-end. Without this proof point, no second deployment.

2. **Q-rule portability proven at >=80%.** The catalog has 23 rules; eight are L&G-critical. Portability metric: the percentage of rules that fire correctly in the Boutique H&G chain deployment with parameter tuning only (no new rule logic). Below 80%, the catalog is too brittle to scale; at or above 80%, it travels to the next deployment with confidence.

3. **>=3 production deployments before sales scaling.** The first deployment is the proof point; the second and third validate the playbook against deployment variance. Bart's Rapid POS channel is the source of deployments two and three. Until three are in production and stable, marketing and sales scaling stays in pilot mode — direct founder involvement, no broad outbound, no public case studies that name customers (per memory `feedback_scrub_client_names`).

4. **VAR partnership terms with Bart formalized.** The Monday 2026-04-27 1pm PST call has the VAR-partnership dimension beyond technical sparring (per memory `project_bart_var_partnership.md`). Formalized terms — referral split, customer-handoff protocol, lab-access provisions, support escalation paths — gate the channel-led deployment cadence. Until terms are written, deployments stay founder-direct.

5. **L&G playbook validated against >=2 retailer types.** Garden centers are the anchor, but the suite is built for L&G specialty retail broadly — feed-and-tack, hardware-and-garden, pet-and-garden, equestrian-supply, farmers-market-adjacent. Validating against at least two distinct retailer-type deployments before broad sales scaling confirms the L&G domain layer generalizes beyond the original archetype.

A sixth gate — implicit, but worth stating — is the founder's escalation requirement on Modules L and W. Both are Canary-native product wedges with real category competitors and real compliance burden. Neither ships beyond basic coverage in the L&G suite without an explicit founder decision per memory `project_canary_native_labor_module_opportunity.md`.

---

## 10. Conclusion

The Lawn-and-Garden RapidPOS Suite is real this quarter. It is not a 2027 aspiration or a deck-only positioning move. The substrate is in flight under GRO-558. The Phase 0 audit ratified that the Square pipeline can stay untouched and Counterpoint plugs in alongside. The OpenAPI spec validates clean. The connection runbook exists. Five phase dispatches are drafted on disk. The Q rule catalog has 24 rules with an L&G-specific allow-list framework. The Boutique H&G chain is the anchor first deployment, multi-store, Counterpoint-running, ready.

Bart Monahan's Rapid POS is the channel. Counterpoint is the substrate. Canary is the operating platform. The 13-module spine — T R N A Q C D F J S P L W — runs the full year of the L&G operator's day, from peak-season replenishment in May through dead-count write-off in October to vendor reconciliation in February. Loss prevention is one of those thirteen modules, not the whole product. The competitive moat is the suite plus the L&G domain layer, not the rule engine in isolation.

The decision in front of us is not whether to ship LP-only or operating-suite — both ship, packaged into tiers. The decision is sequencing the customer engagement so the suite reveals itself the way the operator's year reveals itself: priority modules first because that's what runs the season, catalog second because that's what differentiates the vertical, distribution third because that's what scales the chain, and tertiary plus loss prevention fourth because that's what closes the loop. Phase 5 cutover lands the runbook. Three deployments later, the playbook is durable. By Q2 2027, the L&G specialty SMB market has a Canary-shaped operating platform on top of Counterpoint, delivered through Rapid POS, validated against the operating reality the operator already knows is true.

---

## Appendix: Glossary

| Term | Definition |
|---|---|
| **L&G** | Lawn-and-Garden specialty retail. Garden centers, feed-and-tack, hardware-and-garden, pet-and-garden, equestrian, farmers-market-adjacent. The vertical this playbook is built for. |
| **RapidPOS Suite** | Productized name for Canary's full 13-module spine running on top of NCR Counterpoint, delivered through Bart Monahan's Rapid POS VAR channel. |
| **CRDM** | Canary Retail Data Model. Five-class entity model (People × Places × Things × Events × Workflows) that the Counterpoint adapter populates. |
| **CATz Phase II** | GrowDirect's engagement methodology. To-Be Workshop + RFP Package + Solution Map + IT Architecture + Scorecard + Contract Negotiation. This playbook is a Phase II to-be workshop artifact + solution map composite. |
| **Mix-and-Match (M&M)** | Bundle pricing pattern — "any 10 4-inch perennials for $25" — common in L&G. Counterpoint exposes via `MIX_MATCH_COD` field on items + transaction lines. |
| **Three-Tier Customer Pricing** | Retail / landscaper / commercial pricing tiers for the same item. Counterpoint carries via `Customer.CATEG_COD`. |
| **Dead-Count** | Write-off of unsold perishable inventory at end of season. Tracked as informational signal (per-category seasonal baseline), not fraud, in Module Q. |
| **Specialty Grower** | Small or hobbyist plant supplier paid in cash at the back door. Operationally normal in L&G; allow-listed in Q-IS-02. |
| **Bart's Rapid POS** | Whitelabel Counterpoint reseller operated by Bart Monahan. Friendly VAR channel for Canary's L&G suite. |

---

## Related

- `Canary-Retail-Brain/case-studies/canary-ncr-product-line-decision.md` — the GRO-560 ADR establishing Counterpoint as Canary's first NCR product line
- `Canary-Retail-Brain/case-studies/canary-iot-vendor-strategy.md` — sibling ADR; tone + structure reference
- `Canary-Retail-Brain/case-studies/canary-finance-architecture-options.md` — sibling ADR; Option C OAuth-bridge pattern that Module F inherits
- `docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md` — the SDD; per-module mappings (§6), CRDM alignment (§4), phasing (§8)
- `Brain/wiki/garden-center-operating-reality.md` — vertical operating reality this playbook is read against
- `Brain/wiki/canary-module-q-counterpoint-rule-catalog.md` — 24 Q rules with garden-center allow-list framework
- `Brain/wiki/ncr-counterpoint-phase-0-context-brief.md` — strategic context + Phase 0 handoff
- `Brain/wiki/rapid-pos-counterpoint-market-research-tam.md` — TAM (~1,200 US garden centers; ~9,000 specialty SMB across all Counterpoint VAR verticals)
- `Brain/wiki/alternative-payment-rails-canary-native-opportunity.md` — Module F extension lane (Zelle/Venmo/Cash App/Lightning capture)
- `CATz/method/overview.md` — methodology this playbook is a Phase II artifact under
- `CATz/proof-cases/specialty-smb-counterpoint-solution-map.md` — sanitized worked example

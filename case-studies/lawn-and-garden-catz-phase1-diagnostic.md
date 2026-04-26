---
type: case-study
classification: internal-decision-record
date: 2026-04-25
status: completed-design
related-linear: GRO-596
related-companion: case-studies/lawn-and-garden-rapidpos-suite.md
methodology: CATz Phase I retail diagnostic
author: Geoffrey C. Lyle
---

# Case Study: Lawn-and-Garden Specialty Retail — CATz Phase I Diagnostic

## 1. Executive Diagnosis

A lawn-and-garden specialty chain runs a compressed year — April through September produces 70-80% of annual revenue, and the operating system has to absorb that tilt without losing fidelity in the trough. The dominant cost pressure is perishable shrink, which industry citation places at up to 78% of total shrinkage in garden retail and which existing tooling does not surface as a managed signal. The customer base splits into three structural tiers — retail walk-in, landscaper on account, commercial project — and each tier carries different pricing, AR behavior, and abuse patterns that NCR Counterpoint represents in `Customer.CATEG_COD` but does not analyze. Counterpoint reports answer "what happened" against 11 years of accumulated data; they do not answer "what's wrong" or "what's about to go wrong" because the platform was built as an operational ledger, not an analytical surface. The prize is the convergence of three buckets — perishable shrink reduction, multi-store visibility, landscaper-tier B2B AR control — that compounds to a defensible 2-4% of revenue per chain, addressable through the GRO-588 Canary L&G suite without displacing the Counterpoint substrate the operator is already locked into.

---

## 2. The Vertical Profile

The L&G chain Canary is built for is not a single-store hobby operator and is not an enterprise destination retailer. It is the middle band of the segment — between three and fifteen physical stores, $5M to $50M in annual revenue, family-owned in most cases with a second-generation operator now running the day-to-day. The market wiki sizes the addressable Counterpoint-running L&G universe at approximately 1,200 garden centers in the United States, with a defensible range of 700-1,800, sitting inside a broader specialty-SMB Counterpoint base of approximately 9,000 sites across garden, gun, food, wine, feed-and-tack, pet, sporting goods, hobby, and gift verticals. The chain in the middle band is the one with enough operational complexity to need the suite and enough revenue to fund it.

Geographic distribution skews toward suburban and rural markets in climate zones with an active growing season — the Pacific Northwest, the Mid-Atlantic, the Southeast, the upper Midwest, Northern California, the Texas Hill Country, the Front Range. Destination-retail concentrations cluster around metro fringes where landscape services, garden classes, and on-site cafe traffic supplement the core plant-and-hardgoods business. Multi-store chains in the middle band typically run a hub-and-spoke distribution pattern with one larger anchor store plus two-to-fourteen satellites; transfers between stores are normal during peak season and consolidate at season end.

Family ownership is the cultural baseline. The first-generation owner is operationally fluent and intuitively oriented — pricing decisions, inventory bets, and labor calls are made on instinct refined over decades of season cycles. The second-generation operator is more digitally fluent and more analytically oriented but has inherited the platform stack and the customization investment. NCR Counterpoint is the typical POS, deployed by a Counterpoint VAR (Rapid POS, AMS Retail, RCS, Mariner, POS Highway, C&K Systems) with vertical-specific configuration and dealer-built customization on top. Annual customization spend through the VAR runs in the $10K-$100K range per the public review record. Migration off Counterpoint is rare in the middle band because the customization investment is the lock-in.

The payment mix is heterogeneous — credit and debit dominate the retail tender stream, account-charge and check dominate landscaper invoicing, cash and Zelle/Venmo/Cash App handle ad-hoc vendor payments at the back door and increasingly some landscaper invoice settlements. Counterpoint's `PayCode` taxonomy supports manual recording of any of these tenders; native API capture for the alternative payment rails is not part of the standard Counterpoint surface and represents a Canary-native value-add lane (the Module F extension per the GRO-588 playbook §3 and the alternative-payment-rails wiki).

---

## 3. As-Is Operating Reality (CATz 10-Workstream Frame)

The diagnostic backbone for an L&G chain follows the ten Phase I workstreams from `CATz/method/overview.md`. The first three workstreams (Executive Interviews, Field Visits, As-Is Workshops) carry the bulk of the evidence weight; the remaining seven are treated more briefly because they consolidate into the same thesis.

### 3.1 Executive Interviews — Synthesized Perspectives

A CATz Phase I engagement with an L&G chain runs three interview tracks, generally with three-to-five hours per track over the course of the engagement.

**Owner perspective.** The first-generation or principal owner runs the season. The interview centers on the year-over-year story — what worked in last spring's peak, what didn't, what changed in the customer mix, what the landscaper tier is doing, what the weather-driven trough looked like in the off season. The owner perspective consolidates to a single sentence: *"We make our year between Mother's Day and Father's Day. If we shrink wrong or staff wrong, the year is gone."* The operating instinct is correct — the analytics do not yet validate it on a continuous basis. The owner trusts intuition because the alternative is a Crystal Reports export at month-end that arrives too late to act on.

**Operations / GM perspective.** The operations lead runs the floor. The interview centers on day-to-day signal — which categories are moving, which are dead, what the dead-count baseline looks like by week, where the labor schedule is tight, where the markdown cadence is off, which vendors are late on receivers. The operations perspective consolidates: *"Counterpoint reports are great if you know what question to ask. Most days I don't have time to ask."* The system carries the data; the surface to interrogate it requires Crystal Reports literacy plus an RDP session into a Windows workstation, which the operations lead has neither time nor patience for during peak.

**IT lead perspective.** The IT lead — which in middle-band L&G is often a part-time consultant, a Counterpoint VAR engineer, or the second-generation operator wearing the IT hat — runs the platform stack. The interview centers on the data trail — what's logged, what's queryable, what's broken in the current Counterpoint version, what the dealer relationship is delivering and what it isn't. The IT perspective consolidates: *"We have 11 years of data. Almost none of it is queryable in a useful way."* The data exists in SQL Server tables that can be reached via ODBC or via the paid REST API; what it cannot be reached by is a modern analytical workflow that doesn't require Crystal Reports expertise.

The three perspectives converge on the same diagnostic shape — Counterpoint is operationally sufficient and analytically inert. The operator works around the gap with intuition, spreadsheets, and ad-hoc reports. The cost of the workaround is invisible until something goes wrong (a shrink event, a tier-pricing abuse pattern, an inventory overbuy), at which point the postmortem reveals that the data was always there but the surface to read it wasn't.

### 3.2 Field Visits — Store-Floor Reality

Field visits to two-to-four stores in the chain carry the operational texture the interviews can't. The store layout reveals the structural complexity that the analytics has to accommodate.

**Indoor sales floor.** The indoor portion carries perennials, annuals, hardgoods (pots, tools, fertilizers, garden chemicals), seasonal décor (holiday-compressed in November-December, Easter-compressed in March-April), and statuary. POS placement is centralized at one or two main stations in the off-season and expands to three-to-five satellite stations during peak. Restricted-items zones (Prop 65 chemicals, EPA-registered pesticides, plant-care products with age-of-purchase restrictions in some jurisdictions) require employee override at the register; the override workflow is dealer-customized and varies by chain.

**Outdoor sales floor.** Trees, shrubs, bulk soil, mulch, large pottery, and outdoor statuary live outside under shadehouses, hoop houses, or open yard. Inventory counting is harder — bulk soil and mulch don't scan, large trees may not have a barcode tag if the tag was removed by weather, and the physical layout makes cycle counting an end-of-season activity rather than a continuous discipline. Cash-and-paper backup tickets are normal for outdoor sales rung off-network during peak.

**Mixed environments.** Greenhouses (heated, year-round), shadehouses (seasonal cover), and hoop houses (temporary peak-season expansion) carry the most-perishable inventory and the highest write-off rates. The dead-count workflow for live goods is per-bay or per-row — visual inspection by a plant-care lead, items pulled to a write-off station, dead-count adjustments entered into Counterpoint either same-day or in a weekly batch. The accuracy of the entry depends on the discipline of the plant-care lead and the patience of the operations team to reconcile.

**Back-of-house and receiving.** The receiving dock is where the cash-and-paper culture is most visible. Specialty growers (heirloom plant suppliers, native-species producers, hobbyist succulent growers, plant societies running annual events) deliver in person, often unscheduled, with paper invoices or handwritten receipts and a preference for cash payment. Garden-center receiving staff transcribe these intakes into Counterpoint after the fact, sometimes the same day, sometimes in an end-of-week batch. The data trail is thin by design — the supplier relationship is the value, and the supplier relationship is built on cash-and-handshake protocols that pre-date the POS.

**Landscaper account workflow.** Landscapers buy at volume, often without an in-person customer interaction at the register — they call ahead, the materials are pre-pulled, the landscaper crew arrives with a truck, the load is signed for, and the AR account is charged at the close of day. Multi-tier pricing is applied automatically through Counterpoint's tier resolver, but tier abuse (a retail walk-in customer claiming landscaper status to access wholesale pricing) is a known soft spot that the as-is system does not surface as an exception.

### 3.3 As-Is Workshops — Per-Module Pain Points

Each of the 13 spine letters (T R N A Q C D F J S P L W) gets a per-module as-is pain statement. The table below is the diagnostic backbone — every module of the suite is read against the operational reality the operator already knows is true. The right column maps each pain to the module of the GRO-588 playbook that addresses it.

| Spine Letter | Module | As-Is Pain Statement | Playbook Module that Addresses It |
|---|---|---|---|
| **T** | Transactions | Tickets are logged but not analyzed continuously. Refunds and voids cluster around shift changes and end-of-day; owner suspects but cannot prove because the audit log is in SQL Server tables not exposed to a modern query surface. | Module T — Counterpoint adapter to CRDM; POSLog 2.2.1 alignment; full audit log ingestion. |
| **R** | Customer | Customer tier assignment is manual and error-prone. Landscaper-tier abuse (retail customer flagged WHOLESALE to access wholesale pricing) is unmeasured. Loyalty-tier reconciliation runs on monthly batch in Counterpoint with no continuous signal. | Module R — three-tier resolver; tier-abuse detection routed through Q-CT-01; loyalty reconciliation continuous. |
| **N** | Device | Multi-store device inventory is tracked in Excel by the IT lead. Per-station configuration drift is invisible until a station fails at peak. Device health is unobservable across the chain. | Module N — store hierarchy via Counterpoint Workgroup; per-store config surfacing; device-health observability. |
| **A** | Asset Management | Greenhouses, irrigation equipment, tractors, trucks, and fixed displays are "owner knows" — no formal asset register, no depreciation schedule, no fixture-to-store binding. Asset write-offs surface only at year-end accounting. | Module A — non-saleable asset layer alongside inventory; depreciation hooks; fixture binding. |
| **Q** | Loss Prevention | Loss prevention is reactive — shrink is discovered at year-end physical count, not detected during the season. Eight L&G-critical patterns (perishable shrink, mix-and-match abuse, voided-tender clusters, employee discount abuse, seasonal-staff fraud, landscaper-tier abuse, dead-count vs fraud disambiguation, restricted-items compliance) are unmonitored. | Module Q — 23-rule catalog with L&G allow-list framework; dry-run-then-promote per-rule cutover. |
| **C** | Commercial / B2B | Landscaper AR aging is tracked manually, often in a spreadsheet alongside Counterpoint's Customer_OpenItems. Collection is ad hoc — owner or office manager calls late accounts at month-end. Commercial-account project bundling is invisible. | Module C — B2B workflow surface; landscaper-tier behavior; project bundling; AR aging continuous. |
| **D** | Distribution | Multi-store transfers are managed via phone calls between store managers plus paper picklists. Transfer in-transit visibility is zero. Per-route shrinkage during transfer is invisible. Replenishment routing across stores is ad hoc. | Module D — transfer-loss aggregation; per-route shrinkage; replenishment routing on top of Counterpoint XFER documents. |
| **F** | Finance | Day-end close is a manual exercise — gift-card-as-tender reconciliation eats hours, pay-out documentation is paper-trailed, alternative-payment-rail (Zelle, Venmo, Cash App) capture is manual or absent. Perpetual cost ledger does not reconcile cleanly to general ledger. | Module F — per GRO-526 ADR Option C, Canary perpetual layer with merchant GL via OAuth; alt-payment-rail capture as Canary-native extension. |
| **J** | Forecast / Order | Peak-season demand forecasting is owner intuition plus last-year data. Major over-buys (excess inventory at season-end) and under-buys (out-of-stock during peak) are common. Specialty-grower onboarding is informal — vendor doesn't exist in Counterpoint at intake; staff add ad-hoc. | Module J — seasonal forecast engine with weather-adjustment overlay; specialty-grower flag-and-ingest. |
| **S** | Space, Range, Display | Item hierarchy is flat; perishable flag is informal or absent. Mix-and-match flat groupings are tracked visually only — bundle pricing is defined in Counterpoint but allocation across SKUs in a bundle is invisible. Plant-attribute taxonomy (sun/shade, hardiness zone, water needs) is inconsistent. | Module S — perishable lifecycle modeling; M&M group resolver; plant-attribute taxonomy. |
| **P** | Pricing / Promotion | Promotion stacking and tier interaction is a known sore point — manager calls customer service when a landscaper-tier customer with a loyalty discount and an end-of-season clearance markdown produces a price the cashier doesn't believe. Markdown cadence is owner intuition; markdown velocity is invisible. | Module P — pricing resolver materialized in CRDM; markdown-cadence scheduler; bundle-pricing engine. |
| **L** | Labor / Workforce | Seasonal staff onboarding compresses fraud risk into a two-week window in April. Labor cost per shift is tracked in a third-party scheduling tool (TimeForge or similar) or in Excel — not joined to sales velocity in real time. Schedule-to-actual variance is reviewed monthly, not weekly. | Module L — Canary-native workforce module per SDD §6.12; basic in Phase 1, full surface in Phase 6+. |
| **W** | Work Execution | Daily ops checklists are paper. Perishable rotation tasks slip frequently because the rotation cadence is verbal — plant-care lead tells morning crew, morning crew may or may not execute, no audit trail. Opening and closing routines vary by store and by manager. | Module W — Canary-native work execution module per SDD §6.13; parked Phase 4 or activated when prioritized. |

The table is the diagnostic backbone because it forces every module of the suite to be justified against an operational pain that the operator already recognizes. There is no "build it and they will come" module — every module addresses an as-is friction documented in the field-visit and interview record.

### 3.4 Quantitative Analysis

Numbers worth citing for an L&G chain diagnostic. Each is sourced or estimated; estimates are flagged.

| Metric | Value | Source / Confidence |
|---|---|---|
| Peak / trough revenue concentration | 70-80% Apr-Sep / 20-30% Oct-Mar | Garden-center operating reality wiki; high confidence |
| Industry-average L&G total shrink | 3-5% of revenue | Estimate; confirm against AMS Retail / Lawn & Garden Retailer trade-pub citations during engagement |
| Perishable share of total shrink | up to 78% | AMS Retail trade-pub citation (per market research wiki, source-quality table); medium confidence |
| Tier-pricing lookups per peak day | thousands per store | Estimate; derivable from Counterpoint Document line count during peak week |
| Manual tier-override rate | 5-10% of tier-priced lines | Estimate; validate against Counterpoint audit log during engagement |
| Multi-store transfer volume during peak | 10-30 transfers per chain per week | Estimate; derivable from Counterpoint Document.XFER count |
| Landscaper AR aging > 60 days | typically 15-25% of outstanding balance | Estimate; confirm against Customer_OpenItems aging during engagement |
| Counterpoint customization annual spend | $10K-$100K per chain | Public review record (Capterra / G2 multi-source); medium confidence |
| Counterpoint Cloud license | ~$149/month per license | VAR pricing pages (CompuTant, POS Highway); medium confidence |
| Annual revenue per Counterpoint-running L&G chain | $1M-$15M (single-store to small chain); $5M-$50M (3-15 store band) | BizBuySell mean / extrapolation from market research wiki; medium confidence |

The quantitative section in a real engagement carries the financial baseline in the form of a trailing-twelve-month sales-by-category extract, a per-store sales-and-labor scorecard, an AR aging by customer-tier breakout, and an inventory-on-hand by category-and-perishability snapshot. These extracts are the source of the prize-sizing math in §4.

### 3.5 Executive Visioning

The visioning workstream is short for an L&G chain because the vision is not aspirational — it is recoverable. The operator already knows what the year is supposed to look like; the gap is between operational instinct and analytical confirmation. The vision consolidates to a one-page articulation: continuous visibility into the eight as-is frictions captured in §3.3, with the analytics surface accessible from a manager's phone or a back-office laptop without RDP into a Windows workstation. The to-be is operationally familiar; the path to it is the suite.

### 3.6 Benchmarking

Benchmarking for an L&G chain compares the operator against three reference points — peer chains in the same revenue band (where Garden Center Magazine SOI data is the public record), top-quartile L&G operators (where sales-per-square-foot reaches $200+ vs $100-$150 industry average), and adjacent specialty SMB verticals (where Counterpoint is also installed and analytics adoption is also nascent). The benchmarking output positions the operator inside a defensible band and identifies the top-quartile delta that the suite is built to close.

### 3.7 Balanced Scorecards

A balanced scorecard for an L&G chain carries four quadrants — Financial (revenue per square foot, gross margin, EBITDA), Customer (NPS or equivalent, tier mix, repeat rate), Operational (inventory turn, perishable shrink %, labor cost %), and Learning (staff retention, training completion, technology adoption). The scorecard frames the engagement's success metrics; per-quadrant baselines come from the financial-and-operational extract pulled in §3.4.

### 3.8 Business Case

The business case consolidates the quantified prize from §4 into the standard CATz Benefits / Costs / NPV triad with a traceability artifact mapping suite components back to value opportunities. Benefits roll up to the 2-4% of revenue total addressable value; costs are the suite license plus the Phase II implementation budget through the Rapid POS VAR channel; NPV is computed against a three-to-five-year horizon with sensitivity analysis on the perishable-shrink-reduction assumption (the largest variable). The business case is the SC-3 deliverable.

### 3.9 Presentations

Steering committee cadence runs four touchpoints over the Phase I engagement (see §7 for detail). Each SC is numbered, dated, and marked Final at delivery. Per-SC content is the consolidation of the relevant workstream outputs into a board-ready deck per the seven-section retail-diagnostic frame (Executive Summary / Background / Financial Analysis / Theme 1 / Theme 2 / Priorities & Roadmap / Case for Action). The themes for an L&G chain are typically Perishable Shrink Control and Multi-Store / Multi-Tier Operating Discipline.

### 3.10 Change Management

Change management for an L&G chain is the workstream most often underestimated and is treated in detail in §6.

---

## 4. The Prize — Value at Stake

The prize for an L&G chain that adopts the full Canary suite is the convergence of three buckets, each independently defensible and together additive without double-counting.

**Bucket 1 — Perishable Shrink Reduction.** Industry citation places perishable shrink at up to 78% of total L&G shrinkage, with industry-average total shrink in the 3-5% of revenue range. For a $20M chain, that puts the perishable-shrink loss at $470K-$780K per year as a defensible band. Canary's Module Q with L&G-specific allow-lists (Q-IS-04 dead-count baseline, Q-DM-02 markdown-and-buy, Q-MM-01 mix-and-match below-cost) does not eliminate perishable shrink — perishability is biological — but it surfaces the deviation from baseline that distinguishes shrink from spoilage and drives operator action on the manageable subset. A 25-50% reduction in the manageable subset captures back 1-2% of revenue. For the $20M chain, that's $200K-$400K per year. Conservative band: 1% of revenue. Aggressive band: 2% of revenue.

**Bucket 2 — Multi-Store Visibility.** Three sub-drivers sit inside this bucket. Labor cost optimization — when labor schedule and sales velocity are joined continuously instead of reviewed monthly, schedule-to-actual variance closes by 0.2-0.5% of revenue. Transfer rationalization — when transfer-loss is aggregated and per-route shrinkage is observable, in-transit shrink and re-transfer waste close by 0.1-0.3% of revenue. Replenishment timing — when seasonal forecast plus weather adjustment plus per-store velocity drive replenishment instead of last-year-data plus owner intuition, the over-buy / under-buy gap closes by 0.2-0.4% of revenue. Total bucket: 0.5-1.0% of revenue. For the $20M chain, $100K-$200K per year.

**Bucket 3 — Landscaper-Tier B2B AR Control.** Landscaper-tier abuse alone (retail customers flagged WHOLESALE) is documented at 5-10% of tier-priced transactions in the as-is, with margin loss in the 3-5% range on those transactions. Aggregated, the abuse leakage is 0.15-0.5% of revenue. Collection improvement on landscaper AR — moving 60+ day aging from 15-25% to 8-15% through continuous aging visibility and earlier intervention — captures back another 0.2-0.5% of revenue in working capital and bad-debt avoidance. Commercial-tier expansion (HOA, property management, municipal accounts) becomes tractable when the B2B workflow surface is operational instead of paper-and-spreadsheet, contributing 0.1-0.3% of revenue uplift through new tier capture. Total bucket: 0.5-1.0% of revenue. For the $20M chain, $100K-$200K per year.

**Total addressable value: 2-4% of revenue per chain.** For a $20M chain, $400K-$800K per year. For a $50M chain, $1M-$2M per year. The market-research wiki sizes the addressable Counterpoint-running L&G universe at ~1,200 stores (US, primary segment); aggregated at midpoint per-chain revenue and midpoint capture, the segment-level value at stake is in the high-eight to low-nine figures annually before platform fee — which establishes the upper bound on Canary's pricing posture for the vertical without re-deriving the TAM math (see market-research wiki for specifics).

The prize is sized conservatively. The bands above assume modest Counterpoint customization (single-store to small chain), middle-band perishable mix (50% of inventory live-goods), and conservative B2B share (15-25% of revenue from landscaper plus commercial tiers). Operators outside the middle band — destination retailers with on-site cafe and delivery, chains with heavy commercial/HOA contracts, operators with greenhouse-grown specialty inventory at high margin — sit higher in the band.

---

## 5. Target State — High-Level, Points at Playbook

The target state is the GRO-588 L&G RapidPOS Suite playbook. This diagnostic does not re-derive the suite composition; it bridges the as-is pain points captured in §3.3 to the playbook's solution composition in §3 of the playbook.

| As-Is Pain (per §3.3) | Playbook Module | Counterpoint Integration Phase that Delivers It |
|---|---|---|
| Tickets not analyzed continuously | Module T — full audit log + POSLog alignment | Phase 1 (Q3 2026) |
| Tier abuse unmeasured | Module R + Module Q rule Q-CT-01 | Phase 1 (R) + Phase 4 (Q) |
| Multi-store device drift | Module N | Phase 1 |
| Asset register absent | Module A | Phase 4 |
| Loss prevention reactive, eight unmonitored patterns | Module Q (23-rule catalog with L&G allow-list framework) | Phase 4 |
| Landscaper AR manual, ad hoc collection | Module C | Phase 4 |
| Multi-store transfers paper-and-phone | Module D | Phase 3 |
| Day-end close manual; alt-payment-rail capture absent | Module F (per GRO-526 Option C) + alt-rail extension | Phase 1 (F core) + post-Phase-4 (alt-rail) |
| Forecasting on intuition + last-year-data | Module J — seasonal forecast + weather adjustment | Phase 3 |
| Item hierarchy flat; M&M tracking visual-only | Module S | Phase 2 |
| Promotion stacking unmanaged | Module P (derived) | Phase 2 |
| Seasonal staff onboarding fraud window | Module L (basic Phase 1, full Phase 6+) | Phase 1 (basic) |
| Daily checklists paper | Module W (parked, activate if prioritized) | Phase 4 (parked) |

The phasing is read from the GRO-588 playbook §8 and is not re-derived here. The bridge is what matters: every as-is pain captured in §3.3 maps to a playbook module, and every module is delivered in a defined phase against the Counterpoint substrate. The diagnostic does not invent the target state; it confirms that the target state is constructed against the operational reality the operator already recognizes.

---

## 6. Change-Management Considerations

The change-management workstream is the single most underestimated dimension of an L&G chain engagement. Five practical realities shape the deployment.

**Training cadence.** Apr-onset training is wrong because peak season is starting and training time is the constraint. Mar pre-season is the only window — late February through mid-March, before the spring inventory arrives and before the seasonal staff are hired. Engagement timeline planning has to anchor on this window. A diagnostic completed in Q4 followed by a Phase II vendor selection in Q1 followed by Phase 1 deployment in late Q1 or early Q2 catches the pre-season training window cleanly. A diagnostic completed in Q1 followed by a Phase II in Q2 misses the window and pushes deployment to the following pre-season — a cost the engagement sponsor should budget into the change plan.

**Cash-and-paper culture.** The L&G operator is not anti-technology — the operator is pragmatic about what the technology has earned the right to replace. Cash-and-paper at the back door, paper backup tickets at the register, and handwritten plant-care logs in the greenhouse are not failures of digitization; they are operational adaptations to environments that the digital-first stack is not yet ready for. Forcing the digital-first transition is a known failure mode in this vertical. The CATz parallel-observer stage from the perpetual-vs-period boundary applies here directly — Canary observes alongside the existing tooling for 3-6 months before the merchant cuts over to Canary-as-system-of-record for the analytical layer. Counterpoint remains the operational system of record throughout; Canary is the analytical projection on top.

**Seasonal staff.** Part-time and seasonal labor is 30-60% of total headcount during peak. Training material for cashier-facing surfaces (tier override, mix-and-match override, restricted-items compliance) must be repeatable, lightweight (≤30 minutes for the cashier basics), and re-runnable without engineering involvement. The full-time staff carry the analytical surface; the seasonal staff carry the operational surface and need only enough Canary training to not break the audit trail. The training material is built once for a per-customer rollout and re-used across pre-season cycles in subsequent years.

**Multi-generation ownership.** The first-generation owner is operationally fluent and analytically intuition-driven; the second-generation operator is more digitally fluent but still respects the operational instinct that built the chain. Canary's value proposition for both generations must be framed as amplification, not replacement — the analytics confirm and extend the operator's intuition, they do not override it. Detection rules in Module Q with operator-tunable thresholds and per-rule allow-lists are the technical embodiment of this posture; the operator decides what fires and at what threshold, the platform surfaces the signal.

**Trade groups and peer-validation.** L&G has strong regional and national trade associations — state nursery and landscape associations (CalNGLA, OAN, FNGLA, MNLA, etc.), AmericanHort, the Independent Garden Center Show, regional cooperatives. Deployment narrative benefits from peer-validation reference cases — an operator who has seen a peer chain run Canary for a season is materially easier to convert than an operator approached cold. The first-deployment proof point (Boutique H&G chain per the GRO-588 playbook §9) becomes the seed of the peer-validation network. Trade-group conference circuit (IGC Show in August, regional state-association winter meetings) is the channel for surfacing the proof point at the cadence the segment trusts.

A sixth dimension — VAR-channel handoff. The Rapid POS VAR carries the existing customer relationship and the operational implementation services. Canary's deployment threads through the VAR rather than displacing it. The change-management plan has to formalize the customer-handoff protocol, the support escalation paths, and the joint-success metrics between the VAR and Canary so the operator never sees a finger-pointing exchange between the two.

---

## 7. Steering Committee Cadence

A CATz Phase I engagement for an L&G chain runs four steering committee touchpoints over a 12-16 week window. Each is numbered, dated, and marked Final at delivery per CATz versioning discipline.

**SC-1 — Diagnostic (week 4).** The first SC presents the as-is operating reality (§3 of this diagnostic), the prize sizing (§4), and the target state vision (§5). The deck follows the seven-section retail-diagnostic frame with the two themes set as Perishable Shrink Control and Multi-Store / Multi-Tier Operating Discipline. The deliverable is a 30-40 slide deck plus a 2-3 page executive memo. The decision asked of the steering committee at SC-1 is whether to proceed to SC-2 with the suite framing or pivot the engagement to a narrower scope (LP-only, finance-only, etc.).

**SC-2 — Module Deep-Dive (week 8).** The second SC walks the steering committee through the Module Q + Module T + Module R + Module L value drivers in detail, with the Module Q rule catalog as supporting material and the L&G allow-list framework explained. This is the SC where the operator's operational intuitions get reflected back to them in the platform's detection signals — the moment when the suite stops being abstract and starts being concrete. The deliverable is a deeper module-by-module deck plus annotated rule samples drawn from the operator's own Counterpoint data (subject to data-access and confidentiality terms). The decision asked is whether the rule set as configured matches the operator's risk model.

**SC-3 — Phasing and Investment (week 12).** The third SC presents the Phase 0-4 phasing map (per the GRO-588 playbook §8), the per-phase implementation investment, and the per-quarter ROI build. The business case from §3.8 of this diagnostic consolidates here into the Benefits / Costs / NPV triad with sensitivity analysis. The deliverable is a phasing-and-investment deck plus the financial model in spreadsheet form. The decision asked is the budget commitment for Phase II execution.

**SC-4 — Phase I Closeout (week 16).** The fourth SC closes Phase I. The deliverable is the consolidated Phase I final report — diagnostic, prize, target state, change plan, business case, phasing, investment — packaged as a board-ready deck plus the supporting workstream artifacts archived to the engagement vault. The decision asked is binary — proceed to Phase II (vendor selection through the Rapid POS VAR channel, contracting, implementation kickoff) or pause. A pause is a defensible decision; the diagnostic stands on its own as a strategic asset even if Phase II does not immediately follow.

The four-SC cadence assumes a 12-16 week Phase I. A compressed engagement (6-8 weeks) collapses SC-1 and SC-2 into a single midpoint touchpoint and keeps SC-3 and SC-4 distinct; a deeper engagement (20-24 weeks) adds an interim SC between SC-2 and SC-3 for the quantitative-analysis workstream output and field-visit consolidation. The cadence is the heartbeat of the engagement; everything else feeds into a specific SC.

---

## 8. Conclusion

The L&G specialty retail chain in the middle band — three-to-fifteen stores, $5M-$50M annual revenue, family-owned, Counterpoint-running — has a real and sizable problem. The problem is not the absence of data; the problem is the absence of an analytical surface to act on the data continuously. Counterpoint captures eleven years of operational ledger. The operator's intuition is correct about the shape of the year, the perishable shrink pressure, the tier-pricing complexity, and the seasonal-staff risk window. What is missing is the platform that converts the captured data into continuous operational signal at a cadence the operator can act on without requiring Crystal Reports literacy or RDP into a Windows workstation.

The full Canary suite per the GRO-588 playbook addresses the problem module-by-module. Phase 1 modules (T R F L N) ship in Q3 2026 against the Counterpoint substrate and produce operating value within sixty days of go-live. Phase 2 modules (P S) close the catalog and pricing discipline. Phase 3 (D J) handles the multi-store distribution surface. Phase 4 (A C Q) closes the suite with the Module Q rule catalog firing on top of a fully populated CRDM. The phasing matches the operator's year — priority modules first because that's what runs the season, catalog second because that's what differentiates the vertical, distribution third because that's what scales the chain, and tertiary plus loss prevention fourth because that's what closes the loop.

Phase I closes with a defensible business case. The prize is 2-4% of revenue per chain, conservatively sized, addressable through the suite, deliverable through the Rapid POS VAR channel, durable against the Counterpoint substrate the operator is locked into. Phase II — vendor selection, contracting, implementation — follows the Phase I closeout with the suite as the candidate. The Boutique H&G chain anchor deployment is the proof point that converts the diagnostic from a strategic posture into an operational asset. Three deployments later, the playbook is durable and the segment moves from one-at-a-time to repeatable.

---

## Appendix: Glossary

| Term | Definition |
|---|---|
| **L&G** | Lawn-and-Garden specialty retail. Garden centers, feed-and-tack, hardware-and-garden, pet-and-garden, equestrian, farmers-market-adjacent. |
| **CATz Phase I** | Assess-and-Design phase of GrowDirect's two-phase engagement model. Ten parallel workstreams. Ends with a signed decision: proceed, vision, quantified business case. |
| **CATz Phase II** | Select-and-Implement phase. Six workstreams. Ends with a signed vendor commitment and a funded implementation plan. |
| **CRDM** | Canary Retail Data Model. Five-class entity model (People × Places × Things × Events × Workflows). |
| **Three-Tier Customer Pricing** | Retail / landscaper / commercial pricing tiers for the same item. Counterpoint carries via `Customer.CATEG_COD`. |
| **Mix-and-Match (M&M)** | Bundle pricing pattern — "any 10 4-inch perennials for $25" — common in L&G. Counterpoint exposes via `MIX_MATCH_COD`. |
| **Dead-Count** | Write-off of unsold perishable inventory at end of season. Tracked as informational signal (per-category seasonal baseline), not fraud. |
| **Specialty Grower** | Small or hobbyist plant supplier paid in cash at the back door. Operationally normal in L&G; allow-listed in Q-IS-02. |
| **Boutique H&G chain** | The canonical placeholder for the first deployment per memory `feedback_scrub_client_names`. |
| **VAR** | Value-Added Reseller. The Counterpoint distribution channel; Rapid POS is the friendly VAR for the L&G suite. |

---

## Related

- `Canary-Retail-Brain/case-studies/lawn-and-garden-rapidpos-suite.md` — the GRO-588 demand-side companion (offer side / Phase II)
- `Canary-Retail-Brain/case-studies/canary-ncr-product-line-decision.md` — the GRO-560 ADR establishing Counterpoint as Canary's first NCR product line
- `Canary-Retail-Brain/case-studies/canary-retail-diagnostic-archetype.md` — the prior retail-diagnostic archetype (sibling diagnostic structure)
- `CATz/method/overview.md` — the two-phase methodology this diagnostic operates under
- `CATz/method/retail-diagnostic.md` — the seven-section retail-diagnostic frame applied here
- `CATz/proof-cases/canary-self-diagnostic.md` — worked example of the self-applied diagnostic
- `Brain/wiki/garden-center-operating-reality.md` — vertical operating reality this diagnostic is read against
- `Brain/wiki/rapid-pos-counterpoint-market-research-tam.md` — TAM (~1,200 US garden centers; ~9,000 specialty SMB)
- `Brain/wiki/rapid-pos-counterpoint-user-pain-points.md` — synthesized public-record pain points
- `Brain/wiki/canary-module-q-counterpoint-rule-catalog.md` — 23-rule Q catalog with garden-center allow-list framework
- `docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md` — the SDD; per-module mappings (§6), CRDM alignment (§4), phasing (§8)

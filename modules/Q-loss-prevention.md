---
title: Q — Loss Prevention
nav_order: 8
classification: internal
type: wiki
sub-type: module-functional-decomposition
date: 2026-04-25
last-compiled: 2026-04-25
module: Q
solution-map-cell: ★ Canary native (non-negotiable Canary core)
companion-modules: [T, C, N, S, F, D]
companion-substrate: [ncr-counterpoint-document-model.md, ncr-counterpoint-api-reference.md, ncr-counterpoint-endpoint-spine-map.md]
companion-context: [garden-center-operating-reality.md, rapid-pos-counterpoint-user-pain-points.md, ncr-counterpoint-rapid-pos-relationship.md]
companion-rule-catalog: canary-module-q-counterpoint-rule-catalog.md
companion-catz: CATz/proof-cases/specialty-smb-counterpoint-solution-map.md
methodology-note: "Worked-example proof for a CATz Phase II artifact (Module Functional Decomposition) that does not yet exist in the method. Sits between Solution Map (L1 cell coverage) and SDD (L4 implementation). Once stable, propose at CATz/method/artifacts/module-functional-decomposition.md."
---

# Module Q (Loss Prevention) — Functional Decomposition

> **Artifact layer.** Third of three Canary module artifact layers:
> 1. **Canonical spec** (vendor-neutral) — `Canary-Retail-Brain/modules/Q-loss-prevention.md`
> 2. **Code/schema crosswalk** (Canary-specific) — `Brain/wiki/canary-module-q-loss-prevention.md` *(planned for Q/T/R; exists for J/P/F/C)*
> 3. **Functional decomposition** (Counterpoint-substrate-aware, L2/L3 + user stories) — *this card*

## Governing thesis

Q is the only spine module that is **★ Canary native in every Counterpoint Solution Map**, because Counterpoint exposes the substrate (audit logs, drawer sessions, void-comp reasons, pricing decisions, category margin targets) but no detection layer. Q's functional surface is dominated by **detection rule execution** — 24 rules across 11 families — wrapped by five cross-cutting concerns (substrate ingestion, detection lifecycle, tuning, investigator surface, deployment phasing) and one vertical concern (garden-center allow-list framework).

The decomposition is observer-shaped end to end. Cashiers ring sales; Q watches the Documents arrive. Every L3 has actors drawn from `Chirp` (the rule engine), `Owl` (analyst-facing natural-language surface), `Fox` (case management), and the human store GM / LP analyst who consumes what those agents surface. There are no L3 processes whose actor is "the cashier" — that decomposition lives in Counterpoint's UI, not in Canary.

## Executive summary

| Dimension | Count | Source |
|---|---|---|
| L2 process areas | 7 | This card |
| L3 functional processes | 38 | This card |
| Detection rules referenced | 23 | `canary-module-q-counterpoint-rule-catalog.md` |
| Detection rule families (L3 grouping) | 10 | Rule catalog |
| Garden-center allow-lists (first-class) | 5 | Rule catalog + garden-center-operating-reality |
| Assumptions requiring real-customer validation | 12 | Tagged `ASSUMPTION-Q-NN` |
| User stories enumerated | 71 | Observer-perspective; actor ∈ {Chirp, Owl, Fox, Store GM, LP Analyst, Operator} |

**Posture:** archetype-shaped. No real customer engaged. Every assumption marker exists because the answer requires either a Rapid Garden POS sandbox database, a real customer's data, or both. The card is reusable across Counterpoint-shaped customers; per-customer overrides slot into the final section.

## L1 → L2 → L3 framework

```
L1 (Solution Map cell)         Q = ★ Canary native
                                 │
L2 (Process areas)               ├── Q.1  Substrate ingestion
                                 ├── Q.2  Detection rule execution
                                 ├── Q.3  Detection lifecycle
                                 ├── Q.4  Tuning & allow-list management
                                 ├── Q.5  Investigator & analyst surface
                                 ├── Q.6  Vertical configuration
                                 └── Q.7  Deployment phasing
                                 │
L3 (Functional processes)       (38 — enumerated per L2 below)
                                 │
L4 (Implementation detail)      Lives in SDDs + module specs
                                  (canary-module-q-loss-prevention.md,
                                   canary-module-q-counterpoint-rule-catalog.md,
                                   ncr-counterpoint-retail-spine-integration.md)
```

## Q.1 — Substrate ingestion

**Purpose.** Q reads CRDM only. T/R/N/S/F/D adapters populate CRDM from Counterpoint. Q never reaches into Counterpoint directly. This L2 enumerates which CRDM entities Q depends on, what fields it needs, and what cross-module contracts it asserts.

**Dependency posture.** Q is a **read-only consumer** of every other in-scope module. Any field Q needs must be exposed by the upstream module's adapter; Q does not write back into substrate.

**A.3.1 dependency (load-bearing):** Q.2 detection rules depend on A.3.1 asset-item registry as allow-list input. Items classified as non-inventory assets (ITEM_TYP = N or fixture class) must be excluded from Q detection rule evaluation. Q.2 must consume A.3.1 before firing inventory-discrepancy rules.

**N.5 upstream contract:** Q.1.4 store-config threshold context is sourced from N.5 (store-demographic config + LP threshold publication). N.5 must hold for Q.1.4 baseline expectations to be accurate. Changes to N.4 thresholds require Q rule re-evaluation.

### L3 processes

| ID | L3 process | Substrate read | Owning upstream module | Notes |
|---|---|---|---|---|
| Q.1.1 | Read transaction headers | `Events.transactions` ← `PS_DOC_HDR` | T | DOC_ID, STR_ID, STA_ID, DRW_ID, DRW_SESSION_ID, USR_ID, SLS_REP, CUST_NO, TKT_NO, RS_UTC_DT, IS_DOC_COMMITTED, IS_REL_TKT |
| Q.1.2 | Read transaction lines | `Events.transaction_lines` ← `PS_DOC_LIN[]` | T | LIN_TYP, ITEM_NO, QTY_SOLD, PRC, REG_PRC, EXT_COST, EXT_PRC, MIX_MATCH_COD, IS_DISCNTBL, HAS_PRC_OVRD |
| Q.1.3 | Read payments | `Events.payments` ← `PS_DOC_PMT[]` | F (with T) | PAY_COD, PAY_COD_TYP, AMT, CARD_IS_NEW, SWIPED, EDC_AUTH_FLG |
| Q.1.4 | Read multi-authority taxes | `Events.transaction_taxes` ← `PS_DOC_TAX[]` | F | AUTH_COD, RUL_COD, TAX_AMT, TXBL_LIN_AMT |
| Q.1.5 | Read audit log | `Events.audit_log_entries` ← `PS_DOC_AUDIT_LOG[]` | T | LOG_SEQ_NO, CURR_USR_ID, CURR_DT, CURR_STA_ID, CURR_DRW_ID, ACTIV, LOG_ENTRY |
| Q.1.6 | Read pricing decisions | `Events.pricing_decisions` ← `PS_DOC_LIN_PRICE[]` | T (with P-derived) | PRC_JUST_STR, PRC_GRP_TYP, PRC_RUL_SEQ_NO, UNIT_PRC, QTY_PRCD |
| Q.1.7 | Read original-doc references | `Events.original_doc_refs` ← `PS_DOC_HDR_ORIG_DOC[]` | T | Links return → original sale, void → original sale |
| Q.1.8 | Read store config thresholds | `Places.stores` ← `PS_STR_CFG_PS` | N | MAX_DISC_AMT, MAX_DISC_PCT, USE_VOID_COMP_REAS, RETAIN_CR_CARD_NO_HIST, ALLOW_DRW_REACTIV |
| Q.1.9 | Read item categories with margin targets | `Things.item_categories` ← `IM_CATEG_COD` | S | CATEG_COD, MIN_PFT_PCT, TRGT_PFT_PCT |
| Q.1.10 | Read customer tier + AR posture | `People.customers` ← `AR_CUST` | R | CUST_NO, CATEG_COD (tier), CR_RATE, NO_CR_LIM, BAL, IS_TAX_EXEMPT |
| Q.1.11 | Read transfers, receivers, RTVs | `Events.transfers / receivers / returns_to_vendor` ← Document with DOC_TYP=XFER/RECVR/RTV | D, J | Source/dest store, vendor, items, quantities, payment if any |

### User stories

- *As Chirp, I want every CRDM field listed in Q.1.x to be present and typed before any rule fires, so that no rule silently misses data due to upstream adapter gaps.*
- *As Chirp, I want substrate-staleness signals (`last_polled_at` per entity per tenant) so I can suppress alerts when the substrate is older than my freshness budget.*
- *As an LP Analyst in Owl, I want to ask "what data is Q seeing for this store today" and get a freshness + completeness scorecard, not just rule output.*

### Cross-module contracts asserted

- T must surface `PS_DOC_AUDIT_LOG` flattened with `ACTIV` and `LOG_ENTRY` preserved verbatim — Q rules pattern-match on these strings (**ASSUMPTION-Q-01**: full ACTIV code list)
- T must surface `PS_DOC_HDR_ORIG_DOC` even when empty — Q.2.2 distinguishes "no link" from "no array"
- N must surface `PS_STR_CFG_PS` thresholds at tenant-config time, not per-transaction (cached daily)
- S must surface category margin targets (`MIN_PFT_PCT`, `TRGT_PFT_PCT`) on every item join

## Q.2 — Detection rule execution

**Purpose.** Run the rule catalog. Each rule has substrate, logic, parameters, allow-lists, and severity. This L2 organizes the 24 rules into 11 families; the detailed rule definitions live in the rule catalog companion.

**MECE assertion.** Every detection in Canary against a Counterpoint substrate routes to exactly one rule family. New detection categories require a new family, not stuffing into an existing one.

### L3 processes (rule families)

| ID | Family | Rule IDs | What it detects | Garden-center wrinkle |
|---|---|---|---|---|
| Q.2.1 | Discount-and-markdown | Q-DM-01, Q-DM-02, Q-DM-03 | Price-override abuse, markdown-then-buy, below-cost sales | Wholesale tier customers may legitimately exceed store MAX_DISC_PCT — allow-list per CATEG_COD |
| Q.2.2 | Void-and-return | Q-VR-01, Q-VR-02, Q-VR-03 | Voids without original ticket, refunds without lookup, employee void clusters | None vertical-specific; rules apply uniformly |
| Q.2.3 | Tender-mix anomalies | Q-TM-01, Q-TM-02, Q-TM-03 | Cash-only register patterns, tender swaps, payment fragmentation | Farmers-market / event days legitimately cash-skewed — temporal allow-list |
| Q.2.4 | Drawer-and-session | Q-DS-01, Q-DS-02, Q-DS-03 | Drawer-count shrinkage, post-close activity, drawer reactivation | None vertical-specific |
| Q.2.5 | Audit-trail anomalies | Q-AT-01, Q-AT-02, Q-AT-03 | Document edits after payment, cross-station handling, manager-override frequency | Layaway / order-pickup workflows naturally cross-station — allow-list legitimate hold-and-recall flows |
| Q.2.6 | Margin-erosion | Q-ME-01, Q-ME-02 | Below-category-target margin sales, free-item patterns | Mix-and-match groups have intentionally low line margin (bundle margin is positive) — bundle-aware aggregation |
| Q.2.7 | Inventory-and-shrink | Q-IS-01, Q-IS-02, Q-IS-03, Q-IS-04 | Receiver-vs-PO discrepancy, **cash-paid receivers (informational)**, transfer loss, **dead-count tracking (informational)** | **First-class garden-center awareness:** Q-IS-02 is allow-list-as-rule (cash receivers are normal). Q-IS-04 is informational tracking against seasonal baseline, not fraud |
| Q.2.8 | Tax-and-compliance | Q-TC-01, Q-TC-02 | Multi-authority tax mismatches, tax-exempt customer abuse | Landscaper customers may carry resale exemption; pattern-detect retail use of exemption |
| Q.2.9 | Customer-tier abuse | Q-CT-01, Q-CT-02 | Wholesale tier on retail-pattern customer, pre-purchase tier upgrade | Garden-center customer tiers are particularly volatile (seasonal landscaper conversions) — wider time window for Q-CT-02 |
| Q.2.10 | Mix-and-match abuse (garden-center-specific) | Q-MM-01, Q-MM-02 | Mix-and-match producing below-cost line, mix-match code on non-grouped item | Entire family is garden-center-originated; will need re-shaping for non-garden verticals |

### User stories per family

#### Q.2.1 Discount-and-markdown

- *As Chirp, I want to flag any line where `HAS_PRC_OVRD = "Y"` and per-line discount exceeds the store's `MAX_DISC_AMT/PCT` threshold, with the customer's tier (`AR_CUST.CATEG_COD`) joined so wholesale-tier overrides are auto-suppressed.*
- *As Chirp, I want to detect markdown-then-buy patterns by joining `Things.items` price-change events to subsequent transactions involving the same `ITEM_NO` and same `USR_ID/SLS_REP` within 24h.*
- *As an LP Analyst in Owl, I want to ask "show me all below-cost sales by employee this month" and get a ranked list with each row drillable to the originating Document audit log.*

#### Q.2.2 Void-and-return

- *As Chirp, I want to flag any voided transaction whose `Events.original_doc_refs` is empty, distinguishing "no link present" (suspicious) from "training-mode transaction" (allow-listed).*
- *As Chirp, I want to flag refund transactions where no receipt-lookup audit-log entry preceded the refund — refund without ticket lookup is the high-confidence cash-refund-fraud signal.*
- *As Fox, I want same-employee void clusters within a single drawer session bundled into a single case rather than fired as N separate detections.*

#### Q.2.3 Tender-mix anomalies

- *As Chirp, I want to compare the cash-share at each `(STA_ID, DRW_SESSION_ID)` to that station's rolling baseline and flag sessions that deviate beyond threshold.*
- *As Chirp, I want to detect tender-swap patterns by replaying audit-log entries on a Document and flagging cases where original tender = card and a later edit changed it to cash.*
- *As an LP Analyst, I want a Friday-and-Saturday allow-list for stations designated as "event tents" so farmers-market-day cash patterns don't fire weekly false positives.*

#### Q.2.4 Drawer-and-session

- *As Chirp, I want every drawer-close event to compare reconciled cash count to expected and emit a Q-DS-01 detection if the gap exceeds `(dollar_threshold OR pct_threshold)`.*
- *As Chirp, I want any audit-log entry on a Document committed AFTER its drawer-close timestamp to fire Q-DS-02, with a configurable grace window.*
- *As Fox, I want recurring per-employee shrinkage across multiple sessions auto-promoted from low-severity individual detections to a single high-severity case.*

#### Q.2.5 Audit-trail anomalies

- *As Chirp, I want to flag any line modification on a Document where `IS_DOC_COMMITTED = "Y"` was set before the modification timestamp — committed Documents shouldn't be edited.*
- *As Chirp, I want to flag any single Document whose audit log shows `CURR_STA_ID` changing across 3+ stations, with layaway/order-pickup workflows allow-listed.*
- *As an LP Analyst, I want manager-override frequency reported as a trend not as alerts — it's a pattern signal, not a per-event signal.*

#### Q.2.6 Margin-erosion

- *As Chirp, I want every transaction line to compute `(EXT_PRC - EXT_COST) / EXT_PRC` and compare against the line's category `MIN_PFT_PCT`, aggregating below-target-margin volume per employee per week.*
- *As Chirp, I want any line with `EXT_PRC = 0` and `HAS_PRC_OVRD = "Y"` to count toward Q-ME-02 free-item-pattern detection per `(USR_ID, DRW_SESSION_ID)`.*
- *As Owl, I want to answer "which categories are running below margin target this month and why" with the per-line breakdown drillable to the contributing Documents.*

#### Q.2.7 Inventory-and-shrink

- *As Chirp, I want to flag any receiver Document whose total quantity differs from the originating PO by > 5% or > $100, allow-listing documented short-shipments.*
- *As Chirp, I want **cash-paid receiver classification (Q-IS-02) routed to an "ad-hoc-vendor-payment" review queue, NOT the fraud queue** — this is the load-bearing garden-center allow-list.*
- *As Chirp, I want every transfer Document compared source-quantity vs destination-received-quantity, aggregating shrinkage to a per-route trend.*
- *As a Garden-Center GM in Owl, I want dead-count write-offs tracked against seasonal baseline (per category, per season) so spikes surface but normal seasonal shrink doesn't.*

#### Q.2.8 Tax-and-compliance

- *As Chirp, I want every Document's tax stack compared to the store's expected jurisdiction stack and flag any mismatches (could indicate misconfiguration or tax-evasion).*
- *As Chirp, I want tax-exempt-customer transactions pattern-matched against retail-walk-in shape (single-line, low-dollar, retail SKUs) and flag suspected exemption abuse.*
- *As an LP Analyst, I want a per-customer history view showing tax-exempt usage across 90 days so a known landscaper's legitimate exempt purchases are obvious.*

#### Q.2.9 Customer-tier abuse

- *As Chirp, I want any customer whose `CATEG_COD = WHOLESALE/LANDSCAPER` but transaction history matches retail (avg ticket < $X, single-line walk-in) flagged for tier review.*
- *As Chirp, I want any tier change on a customer record within 72h of a large purchase flagged as Q-CT-02, distinguishing legitimate sales-rep promotions from same-day-upgrade-then-buy patterns.*
- *As Owl, I want to answer "which wholesale-tier customers actually shop like wholesale customers" and get the segmentation with explicit thresholds.*

#### Q.2.10 Mix-and-match abuse (garden-center-specific)

- *As Chirp, I want bundle-level margin computed for any transaction containing `MIX_MATCH_COD` lines — flag only when the BUNDLE margin is negative, not when individual line margins are.*
- *As Chirp, I want to flag any line carrying a `MIX_MATCH_COD` whose corresponding `IM_ITEM` is not part of that mix-match group — manual override pattern.*
- *As Fox, I want mix-and-match abuse cases tagged with the bundle definition snapshot at detection time so retroactive bundle changes don't invalidate the case.*

### Cross-cutting rule contracts

- Every rule has a `dry_run | observation | alerting` mode (per Q.7 phasing)
- Every rule produces a `Detection` row carrying the substrate snapshot, not just IDs (so retroactive substrate changes don't invalidate detections)
- Every rule has explicit allow-list hooks at the parameter layer (per Q.4)
- Every rule emits to Fox case-bundling per `(employee, session, time-window)` co-occurrence rules

## Q.3 — Detection lifecycle

**Purpose.** A detection isn't a one-shot fire-and-forget. Every Q.2 rule output flows through the same lifecycle stages: emit → suppress → bundle → escalate → case → close. This L2 owns the lifecycle.

### L3 processes

| ID | L3 process | Triggers | Output | Notes |
|---|---|---|---|---|
| Q.3.1 | Detection emission | Rule fires against substrate | `Detection` row | Carries substrate snapshot, not just FK references |
| Q.3.2 | Suppression evaluation | New detection arrives | suppress / pass-through | Allow-list match → suppressed-with-reason; threshold-below → suppressed-as-noise |
| Q.3.3 | Case bundling | Multiple detections within `(employee, session, time-window)` | `Case` row groups N detections | Fox owns the bundling policy |
| Q.3.4 | Severity escalation | Bundled case crosses severity threshold | severity bumped (low → medium → high) | E.g., 3+ low-sev shrinkage detections in 7d → medium case |
| Q.3.5 | Investigator notification | Case reaches alerting threshold | Slack / email / dashboard alert | Per-tenant notification config |
| Q.3.6 | Case investigation | Investigator opens case in Fox | Case state machine: open → in-progress → resolved/dismissed | Investigator notes, evidence attachment, audit trail |
| Q.3.7 | Case close + outcome capture | Investigator marks resolved | Outcome enum: confirmed-fraud / training-issue / false-positive / unactionable | Outcomes feed back into rule tuning |

### User stories

- *As Chirp, I want every detection emission to write the substrate snapshot inline so a parser change tomorrow doesn't retroactively invalidate yesterday's detection.*
- *As Fox, I want the bundling policy to be configurable per tenant (some merchants want per-employee-per-day, others per-employee-per-session).*
- *As an LP Analyst, I want every dismissed false-positive to feed into a per-rule false-positive-rate metric so rule tuning is grounded in real outcomes, not vibes.*
- *As a Store GM, I want one daily case digest instead of N individual alerts — Fox's bundling is the difference between Q being useful and Q being noise.*
- *As Owl, I want to answer "which cases are still open across our stores" with the case state machine queryable.*

## Q.4 — Tuning & allow-list management

**Purpose.** Every rule is tunable by parameter; every rule has an allow-list. This L2 owns the operator-facing controls and the audit discipline around them.

### L3 processes

| ID | L3 process | Surface | Audit |
|---|---|---|---|
| Q.4.1 | Threshold tuning per rule | `tune_rule_threshold(rule_id, parameter, value)` MCP tool | Audit-logged with operator + before/after + reason |
| Q.4.2 | Allow-list entry creation | `add_allow_list_entry(rule_id, scope, reason)` MCP tool | Audit-logged; entries carry expiration |
| Q.4.3 | Allow-list expiration / sunset | Automatic expiration job + manual revocation | Expired entries logged; renewal requires fresh reason |
| Q.4.4 | Vertical-pack application | Apply garden-center pack at tenant onboarding (Q.6) | Snapshot at apply time; per-customer overrides tracked |
| Q.4.5 | Rule promotion (dry-run → alerting) | `promote_rule(rule_id, mode)` MCP tool | Audit-logged with operator + readiness check |

### User stories

- *As an Operator in Owl, I want to tune `Q-DM-01.severity_threshold` from 1.0 to 1.5 with one MCP call and see the new value reflected in the next rule evaluation.*
- *As an Operator, I want to add an allow-list entry for "customer 12345 — wholesale exemption granted by GM, expires 2027-04-25" with one call, with the expiration enforced automatically.*
- *As an LP Analyst, I want to see the audit log of every threshold change and allow-list entry across the last 90 days, so audit-time reviews are clean.*
- *As Fox, I want every detection to carry the threshold-as-of-detection-time so retroactive threshold tuning doesn't invalidate past detections.*

## Q.5 — Investigator & analyst surface

**Purpose.** Q outputs are meant to be consumed. This L2 owns the surfaces — Owl natural-language queries, Fox case management, MCP tools for programmatic access.

### L3 processes

| ID | L3 process | Surface | Actor |
|---|---|---|---|
| Q.5.1 | Detection query | `query_detections(rule_id?, date_range, store_id?)` MCP tool | LP Analyst, Operator |
| Q.5.2 | Detection detail | `get_detection_detail(detection_id)` — full substrate snapshot + audit trail | LP Analyst |
| Q.5.3 | Owl natural-language Q&A over detections | Owl prompt → SQL/MCP synthesis → answer | Store GM, Exec |
| Q.5.4 | Fox case workflow | Case open/in-progress/resolved/dismissed state machine | LP Analyst, Investigator |
| Q.5.5 | Dry-run preview | `dry_run_rule(rule_id, date_range)` MCP tool — execute rule without writing detections | Operator (during tuning) |
| Q.5.6 | Per-store / per-employee dashboards | Pre-built tiles surfacing Q outputs | Store GM, LP Analyst |
| Q.5.7 | Case digest (daily/weekly) | Scheduled digest of open cases per recipient | Store GM, Exec |

### User stories

- *As a Store GM in Owl, I want to ask "what should I be paying attention to today?" and get the top 3 open Q cases for my store, ranked by severity and drillable to investigation context.*
- *As an LP Analyst in Fox, I want to open a case, see all bundled detections + substrate snapshots + audit trails on one screen, attach my notes, and resolve with an outcome — without ever running a SQL query.*
- *As an Operator, I want to dry-run a tuned rule against the last 30 days of data and see how many detections it would have produced, before I promote it to alerting.*
- *As an Exec, I want a weekly digest with: cases opened, cases closed, confirmed-fraud-rate, top 3 patterns by frequency. One scrollable email.*
- *As Owl, I want to answer "did our LP improve this month vs last" with a per-store comparison drawn from the case state machine.*

## Q.6 — Vertical configuration

**Purpose.** Q is the most vertical-aware module. Garden-center allow-lists are first-class, not bolt-on. This L2 owns the vertical-pack framework: what's in the garden-center pack today, how new vertical packs get added.

### L3 processes (the 5 garden-center allow-lists)

| ID | Allow-list | Rules affected | Behavior |
|---|---|---|---|
| Q.6.1 | Cash-vendor-payment (load-bearing) | Q-IS-02 (cash-paid receivers) | Classify as ad-hoc-vendor-payment, route to review queue, NOT fraud queue |
| Q.6.2 | Manual-entry noise | Q-IS-01, Q-IS-03 (receiver / transfer discrepancies) | Wider tolerance bands for receiver/transfer reconciliation |
| Q.6.3 | Item-code drift | Q-ME-01, Q-CT-01 (margin / tier-on-retail) | Items churning in/out of catalog mid-season treated as expected |
| Q.6.4 | Live-goods write-off | Q-IS-04 (dead-count tracking) | Seasonal baseline per category; only spikes above baseline flag |
| Q.6.5 | Mix-and-match expected overlap | Q-MM-01 (mix-match below-cost line) | Bundle-margin computed; flag only when BUNDLE goes negative |

### L3 processes (vertical-pack management)

| ID | L3 process | Notes |
|---|---|---|
| Q.6.6 | Apply vertical pack at tenant onboarding | Garden-center pack applied to any tenant flagged `vertical=garden-center` |
| Q.6.7 | Override vertical pack per-tenant | Customer-specific tightening or relaxation, audit-logged |
| Q.6.8 | Author new vertical pack | When second vertical (gun store, feed-and-tack, specialty food, wine) onboards |

### User stories

- *As an Operator onboarding a new garden-center tenant in Owl, I want to apply the garden-center vertical pack with one call and see all 5 allow-lists become active, with per-tenant override available.*
- *As an Operator, I want to see exactly which Q rules a vertical pack tunes and exactly what each tuning does, before I apply it.*
- *As a Garden-Center GM, I want cash-paid receivers from my specialty growers to land in a "review and confirm" queue, not in the same alert stream as suspected fraud — Canary should know specialty growers paid in cash are normal.*
- *As an LP Analyst at a non-garden-center customer, I want a clear UI signal that "this rule has a garden-center allow-list bypass that does NOT apply to this tenant" so I'm not confused about why a rule's behavior differs across tenants.*

## Q.7 — Deployment phasing

**Purpose.** Rules don't all fire on day-zero of a customer deployment. This L2 owns the per-tenant rollout discipline: backfill → observation → tuning → steady state. The phases come from the existing rule catalog; this card formalizes them as L3 processes.

### L3 processes (per-tenant cutover phases)

| ID | Phase | Window | Behavior |
|---|---|---|---|
| Q.7.1 | Day 0 — backfill + dry-run | Tenant install + initial 24-72h Document backfill | All rules in dry-run mode; historical analysis only; no detections written; produces sample case packs for tuning |
| Q.7.2 | Day 1-7 — observation | First operational week post-cutover | Low-FPR rules promoted to informational alerts; high-FPR rules stay dry-run; investigator pre-tuning baseline established |
| Q.7.3 | Day 8-30 — tuning | Operator reviews dry-run outputs, tunes thresholds + allow-lists | Rules promoted per-rule based on dry-run outcome quality; vertical pack applied + customer-specific overrides set |
| Q.7.4 | Day 30+ — steady state | All planned rules in alerting | Continuous tuning per investigator-feedback loop; quarterly rule-catalog audit |

### L3 processes (deployment ops)

| ID | L3 process | Notes |
|---|---|---|
| Q.7.5 | Tenant cutover playbook | Runbook for taking a tenant from Q.7.1 → Q.7.4 |
| Q.7.6 | Per-tenant rollback | If a rule fires badly, demote back to dry-run without blocking other rules |
| Q.7.7 | Rule-catalog version pinning per tenant | Tenants can stay on rule catalog v1.x while v2.x deploys to new tenants — controlled migration |

### User stories

- *As an Operator cutting over a new garden-center tenant, I want a runbook that takes me through Q.7.1 → Q.7.4 with explicit go/no-go gates, not a vague "tune as needed" instruction.*
- *As an Operator, I want to demote any individual rule from alerting back to dry-run with one MCP call when a tuning miss surfaces in production, without affecting other rules' state.*
- *As Canary's Product Owner, I want every customer's rule-catalog version pinned and visible, so a v2.x rollout doesn't silently change behavior for v1.x tenants.*
- *As an LP Analyst, I want the Day-30 tuning review to be backed by data — every rule promoted-or-demoted with explicit dry-run evidence, not gut feel.*

## Assumptions requiring real-customer validation

These markers exist because the answer requires either a Rapid Garden POS sandbox database, a real Counterpoint customer's data, or both. Until resolved, the corresponding rule logic is best-effort against public-source archetype information.

| ID | Assumption | What it blocks | Resolution path |
|---|---|---|---|
| ASSUMPTION-Q-01 | Counterpoint audit-log `ACTIV` codes — what each code means | Q.2.5 rules pattern-match on `LOG_ENTRY` strings; ACTIV is the intended discriminator | Sandbox DB inspection or NCR doc deep-read |
| ASSUMPTION-Q-02 | Drawer reconciliation event modeling — captured in `PS_DOC_AUDIT_LOG`, separate `KeyValueData`, or different endpoint | Q.2.4 (Q-DS-01 drawer-shrinkage) substrate path | Sandbox DB inspection |
| ASSUMPTION-Q-03 | Manager-override flag representation — explicit `USR_ID` role marker, or inferred from override-having + `Roles` membership | Q-DM-01 (discount-cap-exceeded confirmation), Q-AT-03 (manager-override frequency) | Sandbox DB or live customer Roles config |
| ASSUMPTION-Q-04 | Tax-exempt customer field name — likely `AR_CUST.IS_TAX_EXEMPT`, not directly visible in current sample | Q-TC-02 (tax-exempt abuse) substrate path | Sandbox DB schema inspection |
| ASSUMPTION-Q-05 | Dead-count / write-off Document type code — RTV with reason code, separate adjustment workflow, or other | Q-IS-04 (dead-count tracking) entire substrate path | **Real garden-center customer data** — this is the highest-leverage gap |
| ASSUMPTION-Q-06 | Document edit-after-commit — does Counterpoint allow this, or do edits require void+reissue | Q-AT-01 (edit-after-payment) — if void+reissue, rule needs reframing | Sandbox DB workflow test |
| ASSUMPTION-Q-07 | Multi-name plant convention — which fields hold botanical / Spanish / common names | Q.1.x substrate ingestion completeness for L&G item identity | Real Rapid Garden POS customer DB |
| ASSUMPTION-Q-08 | Rapid POS proprietary tables on top of standard Counterpoint schema | Whether Q rules need additional substrate joins | Direct conversation with Rapid POS / customer |
| ASSUMPTION-Q-09 | Real customer's category margin targets (defaults from API, but every customer tunes) | Q-ME-01 thresholds | Tenant onboarding — first 30 days observation |
| ASSUMPTION-Q-10 | Real customer's tier code conventions (`CATEG_COD` values vary per VAR / customer) | Q-CT-01 (wholesale-on-retail-pattern), Q.6 vertical pack tier-aware allow-lists | Tenant onboarding |
| ASSUMPTION-Q-11 | Day-0 backfill data volume and cleanliness — historical Documents may have schema drift, missing audit logs, etc. | Q.7.1 (backfill + dry-run) feasibility for tenants with long history | Customer-specific scoping at onboarding |
| ASSUMPTION-Q-12 | Mix-and-match grouping conventions per Rapid Garden POS — whether bundles are stored as `MIX_MATCH_COD` groups or via Rapid-proprietary extensions | Q.2.10 (mix-and-match abuse) entire substrate path | Real garden-center customer DB |

**Highest-leverage gaps:** ASSUMPTION-Q-05 (dead-count workflow) and ASSUMPTION-Q-12 (mix-and-match implementation) — both are garden-center-distinctive and both require a real customer database. These should be priority asks of any first Rapid Garden POS customer engagement.

## Customer-specific overrides

*Empty until a real customer engagement starts. Format reserved:*

```
Customer: <name>
Vertical pack: <garden-center | gun-store | feed-and-tack | ...>
Tier code conventions:
  WHOLESALE → ...
  LANDSCAPER → ...
  RETAIL → ...
Per-rule overrides:
  Q-XX-NN: <parameter> = <value> (reason; expires <date>)
  ...
Allow-list additions:
  <rule>: <scope>, <reason>, <expiration>
  ...
Disabled rules (with reason):
  <rule>: <reason>
  ...
ASSUMPTION resolutions:
  ASSUMPTION-Q-NN: resolved as <answer>; source: <evidence>
  ...
```

## Operating notes

- This card is the **L2/L3 functional decomposition for one module**. Sister cards (T, R, N, S, F, D) are next; format must remain consistent across them so the Solution Map cells can cross-reference cleanly.
- The methodology gap this card stands in is real: CATz Phase II has no named artifact at this layer. Once 2-3 module cards are stable, propose `CATz/method/artifacts/module-functional-decomposition.md` formally with this Q card as the worked-example proof.
- Every L3 process here either has a corresponding rule in `canary-module-q-counterpoint-rule-catalog.md` (for Q.2 detection), an MCP tool surface (for Q.4–Q.5), or a runbook (for Q.7). Nothing is purely speculative — but every L3 has assumption markers where the substrate-side answer requires real-customer ground-truthing.

## Related

- `canary-module-q-counterpoint-rule-catalog.md` — full rule definitions (substrate × logic × parameters × allow-lists × severity); referenced by Q.2
- `canary-module-q-loss-prevention.md` — Module Q general overview (architecture-level, not functional decomposition)
- `ncr-counterpoint-document-model.md` — Document substrate detail (audit log, original-doc refs, pricing rules, taxes); referenced by Q.1
- `ncr-counterpoint-api-reference.md` — full API surface + Store config thresholds + category margin targets; referenced by Q.1.8 / Q.1.9
- `ncr-counterpoint-endpoint-spine-map.md` — per-endpoint × CRDM × spine map; referenced by every Q.1 substrate row
- `garden-center-operating-reality.md` — vertical-specific allow-list logic; referenced by Q.6
- `rapid-pos-counterpoint-user-pain-points.md` — public-source pain themes informing rule prioritization
- `rapid-pos-counterpoint-market-research-tam.md` — engagement sizing context
- `ncr-counterpoint-rapid-pos-relationship.md` — VAR clarification + feature-to-API mapping
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — Q row = ★ Canary native; this card is the L2/L3 expansion of that cell
- (CATz) `method/artifacts/solution-map.md` — L1 artifact this card sits below
- (CATz, proposed) `method/artifacts/module-functional-decomposition.md` — the artifact template this card proves out; not yet authored

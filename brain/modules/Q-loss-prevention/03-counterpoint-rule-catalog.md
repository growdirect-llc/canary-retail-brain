---
classification: internal
type: wiki
status: active
date: 2026-04-25
last-compiled: 2026-04-25
companion-modules: Brain/wiki/canary-module-q-loss-prevention.md
companion-substrate: Brain/wiki/ncr-counterpoint-document-model.md
companion-context: Brain/wiki/garden-center-operating-reality.md
----

# Canary Module Q — Counterpoint Rule Catalog

Loss-prevention rule catalog for Canary's Module Q operating against NCR Counterpoint substrate. Counterpoint exposes a richer event surface than Square (audit logs per Document, multi-authority tax breakdown, drawer-session correlation, line-level pricing rules captured per ticket, store-level configurable thresholds, category margin targets). This catalog defines rules that exploit that richness AND vertical-aware allow-lists that keep the false-positive rate tractable for cash-heavy specialty retail (garden centers in particular).

## Substrate — what Q reads from

Q runs against CRDM. CRDM is populated by the Counterpoint TSP adapter (Phases 0-3). Specifically:

| CRDM entity | Source | Key fields Q uses |
|---|---|---|
| `Events.transactions` | `PS_DOC_HDR` (DOC_TYP T or sale equivalents) | DOC_ID, STR_ID, STA_ID, DRW_ID, DRW_SESSION_ID, USR_ID, SLS_REP, CUST_NO, TKT_NO, RS_UTC_DT |
| `Events.transaction_lines` | `PS_DOC_LIN[]` | LIN_TYP (S/R/etc.), ITEM_NO, QTY_SOLD, PRC, REG_PRC, EXT_COST, EXT_PRC, MIX_MATCH_COD, IS_DISCNTBL, HAS_PRC_OVRD |
| `Events.payments` | `PS_DOC_PMT[]` | PAY_COD, PAY_COD_TYP, AMT, CURNCY_COD, CARD_IS_NEW, SWIPED, EDC_AUTH_FLG |
| `Events.transaction_taxes` | `PS_DOC_TAX[]` | AUTH_COD, RUL_COD, TAX_AMT, TXBL_LIN_AMT, NORM_TAX_AMT |
| `Events.audit_log_entries` | `PS_DOC_AUDIT_LOG[]` | LOG_SEQ_NO, CURR_USR_ID, CURR_DT, CURR_STA_ID, CURR_DRW_ID, ACTIV, LOG_ENTRY |
| `Events.pricing_decisions` | `PS_DOC_LIN_PRICE[]` | PRC_JUST_STR, PRC_GRP_TYP, PRC_RUL_SEQ_NO, UNIT_PRC, QTY_PRCD |
| `Events.original_doc_refs` | `PS_DOC_HDR_ORIG_DOC[]` | links return → original sale, void → original sale |
| `Events.transfers` | DOC_TYP XFER | source/dest store, item, quantity (Module D) |
| `Events.receivers` | DOC_TYP RECVR | vendor, items, quantities, payment if any (Module J) |
| `Events.returns_to_vendor` | DOC_TYP RTV | vendor, items, reason |
| `Things.items` | `IM_ITEM` | ITEM_NO, CATEG_COD, SUBCAT_COD, ATTR_COD_1/2, MIX_MATCH_COD, REG_PRC, LST_COST, IS_DISCNTBL, STAT |
| `Things.item_categories` | `IM_CATEG_COD` | CATEG_COD, MIN_PFT_PCT, TRGT_PFT_PCT (margin thresholds) |
| `People.customers` | `AR_CUST` | CUST_NO, CATEG_COD (tier), CR_RATE, NO_CR_LIM, BAL |
| `Places.stores` | `PS_STR` + `PS_STR_CFG_PS` | STR_ID, MAX_DISC_AMT, MAX_DISC_PCT, USE_VOID_COMP_REAS, RETAIN_CR_CARD_NO_HIST |

## Rule taxonomy

Rules are grouped by what they detect:

1. **Discount-and-markdown** — abuse of price overrides, discount stacking, markdown-then-buy patterns
2. **Void-and-return** — suspicious void patterns, returns without original, refund abuse
3. **Tender-mix anomalies** — cash-only vs. card patterns, tender swaps, payment fragmentation
4. **Drawer-and-session** — drawer reconciliation gaps, session-shrinkage, post-close activity
5. **Audit-trail anomalies** — Document edits, reassignments, suspicious staff activity around problem tickets
6. **Margin-erosion** — sales below cost, below category-target margin, free-item patterns
7. **Inventory-and-shrink** — receiving discrepancies, transfer-loss, dead-count anomalies
8. **Tax-and-compliance** — multi-authority tax mismatches, exempt-customer abuse
9. **Customer-tier abuse** — wholesale tier on retail-buying customer, tier reassignments
10. **Mix-and-match abuse** — flat pricing exploited beyond intended bundle structure (garden-center-specific)
11. **Compliance** — regulatory exposure on restricted-item sales (Prop 65, EPA pesticides/herbicides, age-restricted, bulk-chemical state regs)
12. **Commercial / B2B** — credit-limit violations, AR aging anomalies, tier-price mismatches, after-hours commercial activity (sourced from Module C signals)

## Per-rule definitions

Format: rule ID, name, substrate, logic, parameters (operator-tunable), allow-list considerations, severity.

### Discount-and-markdown

**Q-DM-01 — Discount-cap exceeded**

Substrate: `Events.transaction_lines.HAS_PRC_OVRD = "Y"` joined to `Places.stores.MAX_DISC_AMT/MAX_DISC_PCT`.
Logic: per-line discount > store's MAX_DISC_AMT or MAX_DISC_PCT, executed without manager override flag.
Parameters: `severity_threshold` (multiplier of MAX_DISC; default 1.0 = any over-cap, 1.5 = 50% over).
Allow-list: per-customer-tier overrides where wholesale customers may legitimately receive deeper discounts (CATEG_COD = WHOLESALE et al.).
Severity: medium. Confirms via audit log: did manager USR_ID approve?

**Q-DM-02 — Markdown-and-buy pattern**

Substrate: `Things.items` price changes (RS_UTC_DT delta) followed by `Events.transaction_lines` purchases of same ITEM_NO by same USR_ID/SLS_REP within window.
Logic: identify employees who mark down items then buy them (or have a colleague buy them), within 24h.
Parameters: `time_window_hours` (default 24), `discount_threshold_pct` (default 30%).
Allow-list: legitimate clearance markdowns (`STAT = D` discontinued) where the markdown is part of approved end-of-life pricing.
Severity: high. Direct fraud signal.

**Q-DM-03 — Below-cost sale**

Substrate: `Events.transaction_lines` where EXT_PRC < EXT_COST and HAS_PRC_OVRD = "Y".
Logic: line sold below cost via manual override.
Parameters: `cost_basis_field` (LST_COST vs. moving avg), `loss_threshold_dollars` (default $50).
Allow-list: clearance items, damaged items (specific reason codes), training transactions.
Severity: medium-to-high depending on volume + repetition.

### Void-and-return

**Q-VR-01 — Voided sale, no original**

Substrate: `Events.transactions` where DOC_TYP indicates void AND `Events.original_doc_refs` is empty.
Logic: a void without a reference to the original ticket is structurally suspicious — Counterpoint normally links them.
Parameters: `tolerance_minutes` (default 0 — any unlinked void).
Allow-list: training-mode transactions, manager-corrected entries with explicit reason code.
Severity: high.

**Q-VR-02 — Refund-without-original-ticket**

Substrate: `Events.transactions` with return lines (LIN_TYP = R) where `Events.original_doc_refs` is empty AND no receipt-lookup log entry in audit trail.
Logic: refund issued without linking to original sale ticket.
Parameters: `customer_known_required` (default Y — refund to known customer is less suspicious than cash refund).
Allow-list: customers with documented disputes, store credit issuance to specific cohorts.
Severity: high.

**Q-VR-03 — Same-employee void cluster**

Substrate: `Events.transactions` (voids) grouped by USR_ID, time-windowed.
Logic: single employee responsible for an outsized share of voids during a session.
Parameters: `void_count_threshold` (default 5 in session), `dollar_threshold` (default $500).
Allow-list: known store managers, training shifts.
Severity: medium escalating to high.

### Tender-mix anomalies

**Q-TM-01 — Cash-only register pattern**

Substrate: `Events.payments` aggregated by STA_ID + DRW_SESSION_ID.
Logic: a single station/session with disproportionate cash share vs. baseline (compares against rolling baseline per store).
Parameters: `cash_share_threshold_pct` (default 80%), `min_session_total` (default $200 to avoid noise on slow shifts).
Allow-list: stations explicitly designated cash-only (configurable per-store), farmers-market / event days.
Severity: low signal, but compounds with other anomalies.

**Q-TM-02 — Tender-swap pattern**

Substrate: `Events.payments` + `Events.audit_log_entries`.
Logic: original ticket recorded as card-paid, later edit changed tender to cash. Detects "card paid, employee pockets cash, swaps records."
Parameters: `time_window_hours` (default 24).
Allow-list: legitimate corrections with reason code.
Severity: high.

**Q-TM-03 — Payment fragmentation**

Substrate: `Events.payments` per `Events.transactions`.
Logic: single transaction split into many small payments below structuring thresholds.
Parameters: `payment_count_threshold` (default 3), `each_below_dollars` (default $10).
Allow-list: gift-card combination scenarios, customer-requested split tenders.
Severity: low.

### Drawer-and-session

**Q-DS-01 — Drawer-session shrinkage**

Substrate: drawer reconciliation events (Counterpoint may model these as audit-log entries with specific ACTIV codes).
Logic: drawer count at session close differs from expected by more than threshold.
Parameters: `dollar_threshold` (default $5), `pct_threshold` (default 0.5%).
Allow-list: documented till-correction reasons.
Severity: low individually; escalates if recurring per-employee.

**Q-DS-02 — Post-close activity**

Substrate: `Events.transactions` + `Events.audit_log_entries` where activity occurs AFTER drawer close timestamp.
Logic: any modification to a Document after the drawer was closed.
Parameters: `grace_minutes` (default 5).
Allow-list: scheduled overnight reporting jobs.
Severity: medium-high.

**Q-DS-03 — Drawer reactivation pattern**

Substrate: `PS_STR_CFG_PS.ALLOW_DRW_REACTIV = "Y"` indicates the store allows it; track the events.
Logic: drawer reactivated > N times per session.
Parameters: `reactivation_count_threshold` (default 2).
Allow-list: training shifts.
Severity: medium.

### Audit-trail anomalies

**Q-AT-01 — Document-edit-after-payment**

Substrate: `Events.audit_log_entries` where LOG_ENTRY indicates line modification post `IS_DOC_COMMITTED = "Y"`.
Logic: Document edited after committed (payment recorded).
Parameters: `tolerance_minutes` (default 0 — any post-commit edit).
Allow-list: documented corrections.
Severity: medium.

**Q-AT-02 — Cross-station Document handling**

Substrate: `Events.audit_log_entries` showing CURR_STA_ID changes across the same DOC_ID's audit timeline.
Logic: same Document handled across multiple stations or workstations.
Parameters: `station_count_threshold` (default 3).
Allow-list: legitimate hold-and-recall flows for layaway / order-pickup.
Severity: medium.

**Q-AT-03 — Manager override frequency**

Substrate: `Events.audit_log_entries` where LOG_ENTRY indicates manager override + USR_ID = manager.
Logic: a single manager USR_ID overriding restrictions at a rate above team baseline.
Parameters: `override_pct_threshold` (default 200% of team baseline).
Allow-list: legitimate roles requiring frequent overrides.
Severity: low signal; useful for trend analysis.

### Margin-erosion

**Q-ME-01 — Below-category-target margin**

Substrate: `Events.transaction_lines` joined to `Things.item_categories.MIN_PFT_PCT/TRGT_PFT_PCT`.
Logic: transaction_lines whose realized margin (EXT_PRC - EXT_COST)/EXT_PRC < category MIN_PFT_PCT.
Parameters: `aggregation_window_days` (default 7), `volume_threshold` (default $1000 in below-target sales).
Allow-list: clearance, damaged-goods reasons, mix-and-match groups (where line margin is intentionally lower because the bundle margin is positive).
Severity: low; aggregates into trend.

**Q-ME-02 — Free-item pattern**

Substrate: `Events.transaction_lines` where EXT_PRC = 0 and HAS_PRC_OVRD = "Y".
Logic: items priced to zero via override.
Parameters: `count_threshold_per_employee_per_session` (default 3).
Allow-list: legitimate giveaway events, customer-loyalty redemptions, in-store sample items.
Severity: medium.

### Inventory-and-shrink

**Q-IS-01 — Receiver-vs-PO discrepancy**

Substrate: `Events.receivers` joined to `Workflows.purchase_orders` via `Events.original_doc_refs`.
Logic: receiver quantity differs from PO quantity by > threshold.
Parameters: `qty_pct_threshold` (default 5%), `dollar_threshold` (default $100).
Allow-list: documented short-shipments, vendor-overage tolerance.
Severity: low; aggregates to trend.

**Q-IS-02 — Cash-paid receiver classification (NOT fraud)**

Substrate: `Events.receivers` with PayCode = CASH.
Logic: this is the **garden-center-allow-list pattern** — cash-paid vendor receivers are LEGITIMATE in cash-heavy specialty verticals (specialty growers paid at the back door). This rule classifies them separately, NOT as fraud signals.
Parameters: `vertical_allow_list` (default: garden-center, farmers-market, specialty-food).
Allow-list: this rule IS the allow-list for the vertical.
Severity: informational only; routes to a separate "ad-hoc-vendor-payment" review queue, not the fraud queue.

**Q-IS-03 — Transfer-loss pattern**

Substrate: `Events.transfers` where source-store quantity differs from dest-store received quantity.
Logic: in-transit shrinkage.
Parameters: `qty_pct_threshold` (default 1%).
Allow-list: damage-in-transit reasons.
Severity: low; aggregates to per-route signal.

**Q-IS-04 — Dead-count / live-goods write-off (garden-center-specific)**

Substrate: write-off documents (DOC_TYP code TBD; likely RTV with reason code or adjustment workflow).
Logic: track plant write-offs vs. expected seasonal spoilage baseline (per category, per season).
Parameters: `seasonal_baseline_pct` (per-category; e.g., perennials 8% spring, 15% summer).
Allow-list: this is normal in garden centers — the rule TRACKS it for trend analysis, not flagging individual write-offs as fraud.
Severity: informational; spike-detection only.

### Tax-and-compliance

**Q-TC-01 — Multi-authority tax mismatch**

Substrate: `Events.transaction_taxes` (PS_DOC_TAX rows).
Logic: per-Document tax stack doesn't match expected jurisdiction stack for the store's tax code.
Parameters: `expected_authority_set` (per-store; e.g., MEMTN store should always have MEMPHIS + SHELBY + TN).
Allow-list: documented tax-exempt customers (`AR_CUST.IS_TAX_EXEMPT` or equivalent).
Severity: medium — could indicate misconfiguration OR tax-evasion attempt.

**Q-TC-02 — Tax-exempt customer abuse**

Substrate: `Events.transactions` with tax-exempt customer (Customer.TAX_COD = NOTAX or equivalent) repeatedly used by walk-in retail patterns.
Logic: tax-exempt status applied to a customer making cash retail purchases (rather than the institutional B2B purchases the exemption was granted for).
Parameters: `pattern_window_days` (default 90), `walk-in_signal` (single-line, low-dollar, retail SKUs).
Allow-list: legitimate exempt customer scenarios.
Severity: medium.

### Customer-tier abuse

**Q-CT-01 — Wholesale tier on retail-pattern customer**

Substrate: `People.customers.CATEG_COD` (tier) cross-referenced with their transaction history pattern.
Logic: customer flagged WHOLESALE / LANDSCAPER but transaction pattern matches retail (single-item small-dollar walk-in).
Parameters: `wholesale_signal_threshold` (e.g., avg ticket > $500 OR multi-pallet items).
Allow-list: known retail-tier customers explicitly upgraded for relationship reasons (manual flag).
Severity: low; aggregates to per-customer review.

**Q-CT-02 — Tier-reassignment pattern**

Substrate: customer.CATEG_COD changes over time (audit-log on Customer record edits).
Logic: customer tier upgraded immediately before a large purchase, downgraded after.
Parameters: `time_window_hours` (default 72).
Allow-list: documented sales-rep promotions, customer-requested upgrades.
Severity: high.

### Mix-and-match abuse (garden-center-specific)

**Q-MM-01 — Mix-and-match producing below-cost line**

Substrate: `Events.transaction_lines` with MIX_MATCH_COD set, where realized line margin is negative.
Logic: mix-and-match flat pricing exploited beyond intended bundle (e.g., customer + employee gaming the bundle to extract free items).
Parameters: `negative_margin_dollars_per_session` (default $50).
Allow-list: legitimate mix-and-match overlap, mid-rule transition periods.
Severity: medium.

**Q-MM-02 — Mix-and-match used outside grouping**

Substrate: `Events.transaction_lines` where MIX_MATCH_COD on the line doesn't match any item-side MIX_MATCH_COD assignment.
Logic: mix-match code applied to a line whose item isn't part of the group — manual override pattern.
Parameters: none (any mismatch).
Allow-list: documented merchandising decisions.
Severity: medium.

### Compliance

**Q-CP-01 — Restricted-item sale without override**

Substrate: `Events.transaction_lines` joined to `Things.items` (item-side restricted flags), cross-referenced against `Events.audit_log_entries` for transaction-level override.
Logic: on transaction commit, any line whose item carries a restricted-item flag (`prop_65`, `epa_pesticide`, `epa_herbicide`, `restricted_chemical`, `age_restricted`) sells without a `restricted_items_authorized` override on the transaction. The override IS the forensic record — its absence on a restricted-item line is the detection.

```
on transaction.commit:
  for line_item in transaction.line_items:
    if item.has_flag('restricted_item')
       and not transaction.has_override('restricted_items_authorized'):
      emit detection {
        rule_id: 'Q-CP-01',
        transaction_id: transaction.id,
        item_id: item.id,
        store_id: transaction.store_id,
        employee_id: transaction.employee_id,
        timestamp: transaction.created_at,
        severity: P1,
        evidence: {
          item_name: item.name,
          restricted_classifications: item.restricted_flags,
          required_override: 'restricted_items_authorized'
        }
      }
```

Restricted-item flag taxonomy:

| Flag | Meaning |
|---|---|
| `prop_65` | California Prop 65 — cancer / reproductive harm warning items |
| `epa_pesticide` | EPA-registered pesticide |
| `epa_herbicide` | EPA-registered herbicide |
| `restricted_chemical` | Bulk fertilizer / soil amendment subject to state regulations |
| `age_restricted` | Pyrotechnics, certain bulk chemicals (18+ states) |

Parameters: `flag_set_active` (per-store; e.g., California stores activate `prop_65`), `override_code` (default `restricted_items_authorized`), `evidence_retention_days` (default 2555 / 7 years for regulatory exposure).
Allow-list: store-level flag activation (a Tennessee store doesn't activate `prop_65`); documented training transactions.
Severity: P1 — regulatory exposure. Garden centers carry many EPA-registered pesticides and herbicides; in California, Prop 65 affects a wide swath of plant amendments and fertilizers. The manager-override workflow needs a paper trail because the override IS the forensic record demonstrating informed sale.


## Garden-center allow-list framework

For garden-center / farmers-market / specialty-food / wine / feed-tack vertical deployments, the following allow-lists are pre-loaded:

```
Allow-list: cash-vendor-payment
- Rule applies: Q-IS-02 (cash-paid receiver classification)
- Behavior: classify as ad-hoc-vendor-payment, route to review queue, not fraud queue
- Tunable: vertical-allow-list parameter

Allow-list: manual-entry noise
- Rules affected: Q-IS-01, Q-IS-03 (receiver/transfer discrepancies)
- Behavior: tolerance bands wider for receiver/transfer quantity reconciliation
- Tunable: qty_pct_threshold, dollar_threshold

Allow-list: item-code drift
- Rules affected: Q-ME-01 (below-category-margin), Q-CT-01 (tier-on-retail-pattern)
- Behavior: items churning in/out of catalog mid-season treated as expected, not anomaly
- Tunable: catalog-volatility-baseline

Allow-list: live-goods write-off
- Rules affected: Q-IS-04 (dead-count tracking)
- Behavior: seasonal baseline for plant write-off; only spikes above baseline flag
- Tunable: seasonal_baseline_pct (per category)

Allow-list: mix-and-match expected overlap
- Rules affected: Q-MM-01 (mix-match producing below-cost line)
- Behavior: bundle-level margin computed; only flag if BUNDLE goes negative
- Tunable: bundle-margin-threshold
```

## Operator surface

MCP tools expose Q to the agent layer:

- `query_detections(rule_id?, date_range, store_id?)` — paginated; rule_id null returns all
- `get_detection_detail(detection_id)` — full context of a single detection (event chain + substrate snapshot)
- `list_active_rules()` — current rule catalog with their parameter values
- `tune_rule_threshold(rule_id, parameter, value)` — adjust without re-deploying; audit-logged
- `get_allow_list(rule_id)` — view current allow-list entries
- `add_allow_list_entry(rule_id, customer_id?, item_id?, reason)` — operator-tunable (audit-logged)
- `dry_run_rule(rule_id, date_range)` — execute the rule without writing detection records (used during deployment + tuning)

### Commercial / B2B (sourced from Module C)

Rules in this family are triggered by Module C signals (credit posture, tier classification, AR pattern) rather than direct Counterpoint transaction substrate. C derives the inputs; Q fires the alert via Chirp. These are account-management alerts, not LP fraud alerts — severity intentionally lower, routed to account manager surface in Owl rather than LP queue.

**Q-C-01 — At-limit commercial account continues transacting** *(C.4.1 B2B-CREDIT-01)*

Substrate: `C.CREDIT_POSTURE = AT-LIMIT` signal joined to `Events.transactions` for the same `AR_CUST.CUST_NO` (live transaction stream from T).
Logic: a commercial account whose C.2.5 credit-posture is AT-LIMIT initiates a new purchase transaction. Alert fires at transaction open, before close.
Parameters: `credit_posture_threshold` (default AT-LIMIT; configurable to PAST-DUE as looser trigger), `min_transaction_amount` (default $0 — any new transaction).
Allow-list: accounts with an approved credit-hold override flag (manual operator flag per account).
Severity: medium — account-management alert, not fraud. Routes to account manager in Owl.

**Q-C-02 — Rapid credit consumption before going dark** *(C.4.2 B2B-CREDIT-02)*

Substrate: `C.CREDIT_UTILIZATION` time-series per `AR_CUST.CUST_NO` — utilization velocity derived by C.2.2.
Logic: account transitions from <20% utilization to >80% utilization within a rolling 14-day window, with no corresponding change in credit limit.
Parameters: `low_threshold_pct` (default 20%), `high_threshold_pct` (default 80%), `window_days` (default 14).
Allow-list: accounts with documented seasonal purchase patterns (e.g., landscaper spring ramp — configurable per-account flag).
Severity: high — collections-risk signal; fires before the account formally enters past-due.

**Q-C-03 — Past-due balance crosses threshold** *(C.4.3 B2B-AR-01)*

Substrate: `C.AR_AGING_BUCKET` signal from C.2.3 (aging bucket transitions) per `AR_CUST.CUST_NO`.
Logic: account transitions into the 60-day (or operator-configured) aging bucket — C.2.3 detects the transition and publishes the trigger event.
Parameters: `past_due_days_threshold` (default 60), `minimum_balance_dollars` (default $100 to suppress noise on small accounts).
Allow-list: accounts in documented payment-arrangement status (manual operator flag).
Severity: medium — account-management alert. Escalate to high if balance > $1,000 (configurable).

**Q-C-04 — Transaction price inconsistent with B2B tier** *(C.4.4 B2B-TIER-01)*

Substrate: `Events.transaction_lines.EXT_PRC` joined to `People.customers.CATEG_COD` (tier from C.1.2) and `Things.items` price groups (PS_PRC_GRP via P.1).
Logic: a wholesale-tier account is sold at retail price level, or a retail account receives wholesale pricing. Detected per line via realized price vs. expected tier-price range.
Parameters: `tier_mismatch_tolerance_pct` (default 0% — any mismatch; configurable to allow small overrides).
Allow-list: accounts with explicit per-item or per-category pricing exceptions (documented in Counterpoint price group overrides).
Severity: low — data-quality flag, not fraud. Most likely cause is account-setup error. Routes to store manager, not LP queue.

**Q-C-05 — Commercial account transacting outside business hours** *(C.4.5 B2B-PATTERN-01)*

Substrate: `Events.transactions.BUS_DTE` + `Events.transactions.CRTE_DTE` (timestamp) joined to `People.customers.CATEG_COD = COMMERCIAL` (or equivalent wholesale/landscaper tier from C.1.2).
Logic: a flagged-commercial account transacts outside defined business hours for that store. The concern is account-sharing — a commercial account used by non-commercial parties after hours.
Parameters: `business_hours_start` (per-store from N; default 07:00), `business_hours_end` (per-store; default 19:00), `days_of_week` (default Mon–Sat).
Allow-list: accounts with documented 24h access (wholesale-delivery accounts, approved contractor access). See ASSUMPTION-C-06 — expect false positives from landscapers who legitimately transact evenings; calibrate allow-list against first 30 days of data.
Severity: low signal on its own; escalates to medium when combined with Q-C-01 or Q-C-02 signals on the same account.

## Phasing of rule deployment

Rules don't all fire on day-zero of a customer deployment:

| Phase | Rules active |
|---|---|
| Day 0 — backfill | All rules in dry-run mode (compute but don't alert); historical analysis only |
| Day 1-7 — observation | Rules that have low false-positive risk fire as informational; high-FPR rules stay dry-run |
| Day 8-30 — tuning | Operator reviews dry-run output, tunes thresholds + allow-lists, promotes rules to active alerting per-rule |
| Day 30+ — steady state | All rules active; tuning is ongoing per-rule based on operator feedback |

This is the per-customer cutover behavior the Phase 5 dispatch encodes.

## Open questions

1. Counterpoint audit-log entry types — what ACTIV codes mean what? (Sample data shows "N" for new ticket; need full list from sandbox or doc.)
2. Drawer reconciliation event modeling — is the drawer-close-and-count flow captured in PS_DOC_AUDIT_LOG, or in a separate KeyValueData entry, or via a different endpoint entirely?
3. Manager-override flag — how is "manager override" represented? Is there a specific USR_ID role marker, or is it inferred from override-having + Roles table membership?
4. Tax-exempt customer field — confirm field name on Customer record (likely some flag in `AR_CUST` not visible in current sample).
5. Dead-count / write-off Document type code — Counterpoint may use RTV with specific reason or a separate adjustment endpoint. Confirm against real garden-center data.
6. Document edit-after-commit — does Counterpoint actually allow this, or do edits require a void+reissue? If void+reissue, Q-AT-01 needs reframing.

## Related

- [[canary-module-q-loss-prevention]] — Module Q general overview
- [[ncr-counterpoint-document-model]] — Document substrate detail (audit log, original-doc refs, pricing rules, taxes)
- [[ncr-counterpoint-api-reference]] — full API surface + Store config thresholds + category margin targets
- [[garden-center-operating-reality]] — vertical-specific allow-list logic
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — engagement-level positioning of Q

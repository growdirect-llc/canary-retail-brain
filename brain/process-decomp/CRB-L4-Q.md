---
type: process-decomp
artifact: l4-spec
module: Q — Loss Prevention
pass-date: 2026-04-28
source: GRO-670 / GRO-675
method: Track A — Python codebase translation
python-sources:
  - Canary/canary/services/chirp/rule_definitions.py
  - Canary/canary/services/chirp/stateless_engine.py
  - Canary/canary/services/chirp/rule_engine.py
  - Canary/canary/services/chirp/threshold_manager.py
  - Canary/canary/services/fox/case_service.py
  - Canary/canary/services/fox/tools.py
  - Canary/canary/services/alert_lifecycle.py
  - Canary/canary/services/alerts/tools.py
  - Canary/canary/services/notification_service.py
confidence: HIGH — all L4s derived from implemented production code
---

# CRB L4 Spec — Module Q: Loss Prevention

**Governing note:** All L4 activities in this file are derived from the Canary Python prototype. They are implementation-level specifications for the CanaryGO Go build. Go engineer reads this file; the Python code is the reference for behavior; the Go implementation is the deliverable.

---

## Q.1 — Substrate Ingestion (5 L3s)

The bridge from TSP canonical event stream → Chirp detection engine. Sub4 is the consumer; Chirp rule_engine receives the parsed payload.

**Source:** `tsp/consumers/sub4_detect.py`, `chirp/rule_engine.py`

| L4 ID | Activity | Function / Contract |
|-------|----------|-------------------|
| Q.1.1.1 | XREADGROUP sub4-detect | Consumer group = `sub4-detect`. BLOCK_MS configurable. BATCH_SIZE=1. |
| Q.1.1.2 | Extract stream message fields | Fields: event_id, merchant_id, source, event_type, event_hash, raw_payload, received_at, parse_failed |
| Q.1.2.1 | Route by event_type | LP-critical event types routed to detection dispatch; log-only types ACK'd without evaluation |
| Q.1.2.2 | Skip on parse_failed=true | If upstream sub2 flagged parse failure, no rule evaluation; XACK and continue |
| Q.1.3.1 | Load active merchant rules | `ThresholdManager.get_all_active_rules(merchant_id)` — Valkey `chirp:active_rules:{merchant_id}` (TTL=300s) → DB MerchantRuleConfig → RULE_CATALOG defaults |
| Q.1.4.1 | Load per-rule thresholds | `ThresholdManager.get_thresholds(merchant_id, rule_id)` — Valkey `chirp:thresholds:{merchant_id}:{rule_id}` (TTL=300s) → DB → rule.default_thresholds |
| Q.1.5.1 | Build detection payload | JSON-decode raw_payload → merchant-annotated parsed dict (amount_cents, transaction_type, transaction_date, employee_id, location_id, delay_action, approved_amount_cents, etc.) |

---

## Q.2 — Detection Rules (10 L3s → 37 rules, 3 tiers)

**Source:** `chirp/rule_definitions.py`, `chirp/stateless_engine.py`, `chirp/rule_engine.py`

### Rule Catalog — Complete (37 rules, 10 categories)

| Rule ID | Name | Category | Severity | Tier | Threshold Keys |
|---------|------|----------|----------|------|---------------|
| C-001 | RAPID_REFUND | payment | high | 3 | seconds=900 |
| C-002 | EXCESSIVE_REFUND_RATE | payment | high | 2 | percent=15, min_transactions=5 |
| C-003 | ROUND_AMOUNT_PATTERN | payment | medium | 2 | count=5, window_seconds=3600 |
| C-004 | AFTER_HOURS_TRANSACTION | payment | medium | **1** | open_hour=6, close_hour=22 |
| C-005 | CARD_VELOCITY | payment | high | 2 | count=5, window_seconds=3600 |
| C-006 | SPLIT_TENDER_PATTERN | payment | medium | 2 | count=3, window_seconds=3600 |
| C-007 | HIGH_VALUE_REFUND | payment | high | **1** | amount_cents=10000 |
| C-008 | MANUAL_ENTRY_SPIKE | payment | medium | 2 | count=5, window=shift |
| C-009 | SQUARE_DELAY_HOLD | payment | critical | **1** | (no threshold — fires on delay_action presence) |
| C-010 | PARTIAL_AUTHORIZATION | payment | high | **1** | variance_cents=0 |
| C-011 | NO_SALE_DETECTED | payment | high | **1** | (no threshold — fires on transaction_type=NO_SALE) |
| C-101 | NO_SALE_ABUSE | cash_drawer | high | 2 | count=5, window=shift |
| C-102 | CASH_VARIANCE | cash_drawer | high | 3 | amount_cents=2000 |
| C-103 | PAID_OUT_ANOMALY | cash_drawer | medium | 3 | amount_cents=5000 |
| C-104 | AFTER_HOURS_DRAWER | cash_drawer | critical | 3 | open_hour=6, close_hour=22 |
| C-201 | EXCESSIVE_DISCOUNT_RATE | order | high | 3 | percent=50 |
| C-202 | LINE_ITEM_VOID_RATE | order | high | 3 | percent=10, min_items=10 |
| C-203 | SWEETHEARTING | order | high | 3 | amount_cents=2000 |
| C-204 | UNTENDERED_ORDER | order | critical | 3 | stale_hours=24 |
| C-301 | OFF_CLOCK_TRANSACTION | timecard | critical | 3 | (no threshold) |
| C-302 | BREAK_TRANSACTION | timecard | high | 3 | (no threshold) |
| C-303 | WRONG_LOCATION | timecard | high | 3 | (no threshold) |
| C-501 | HIGH_VOID_RATE | void | high | 2 | count=5, window=shift |
| C-502 | POST_VOID_ALERT | void | critical | 2 | immediate_max_seconds=120 (no alert), watch_max_seconds=900 (high), suspicious_max_seconds=28800 (critical), self_refund_score_boost=10, off_clock_score_boost=15 |
| C-601 | GIFT_CARD_LOAD_VELOCITY | gift_card | high | 2 | count=3, window_seconds=3600 |
| C-602 | GIFT_CARD_DRAIN | gift_card | critical | 3 | seconds_after_load=1800 |
| C-801 | RAPID_POINT_ACCUMULATION | loyalty | medium | 2 | count=5, window_seconds=3600 |
| C-802 | BULK_REDEMPTION | loyalty | high | 3 | points=5000 |
| C-803 | CROSS_LOCATION_VELOCITY | loyalty | high | 2 | location_count=3, window_seconds=7200 |
| C-804 | ENROLLMENT_FRAUD | loyalty | medium | 2 | count=10, window_seconds=86400 |
| C-901 | SRA_THRESHOLD_BREACH | composite | high | 3 | sra_pct_sales_max=3.0 |
| C-D01 | DISPUTE_CREATED | dispute | high | **1** | (no threshold) |
| C-D02 | DISPUTE_LOST | dispute | critical | **1** | (no threshold) |
| C-D03 | DISPUTE_VELOCITY | dispute | high | 2 | count=3, window_days=30 |
| C-I01 | INVOICE_OVERDUE | invoice | medium | **1** | (no threshold) |
| C-I02 | INVOICE_CHARGE_FAILED | invoice | high | **1** | (no threshold) |
| C-I03 | HIGH_VALUE_INVOICE_UNPAID | invoice | high | **1** | amount_cents=50000 |

**Tier 1 rules (12 total):** C-004, C-007, C-009, C-010, C-011, C-D01, C-D02, C-I01, C-I02, C-I03 — stateless, pure function, no I/O  
**Tier 2 rules (12 total):** C-002, C-003, C-005, C-006, C-008, C-101, C-501, C-502, C-601, C-801, C-803, C-804, C-D03 — Valkey counters  
**Tier 3 rules (13 total):** C-001, C-102, C-103, C-104, C-201, C-202, C-203, C-204, C-301, C-302, C-303, C-602, C-802, C-901 — full DB

### Q.2.1 — Tier 1 Stateless Evaluation

**Source:** `chirp/stateless_engine.py` → `evaluate_stateless()`

`evaluate_stateless(parsed: Dict, thresholds: Optional[Dict], disabled_rules: Optional[set]) → List[Dict]`

| L4 ID | Activity | Implementation Detail |
|-------|----------|-----------------------|
| Q.2.1.1 | Guard: empty payload | Return [] if parsed is falsy |
| Q.2.1.2 | Check C-004 (AFTER_HOURS) | `_check_after_hours()`: parse transaction_date → extract hour → compare to [open_hour, close_hour) |
| Q.2.1.3 | Check C-007 (HIGH_VALUE_REFUND) | `_check_high_value_refund()`: guard transaction_type IN (RETURN, REFUND); abs(amount_cents) >= threshold |
| Q.2.1.4 | Check C-009 (DELAY_HOLD) | `_check_square_delay_hold()`: delay_action present AND txn_type NOT in (SALE, RETURN, VOID, POST_VOID) |
| Q.2.1.5 | Check C-010 (PARTIAL_AUTH) | `_check_partial_auth()`: approved_amount_cents < amount_cents AND gap > variance_cents |
| Q.2.1.6 | Check C-011 (NO_SALE) | `_check_no_sale()`: transaction_type == NO_SALE |
| Q.2.1.7 | Build alert dict | `_make_alert(rule_id, parsed, details)` → {id: uuid4, rule_id, name, severity, category, source="stateless", source_id, merchant_id, employee_id, location_id, amount_cents, details, fired_at: utcnow} |
| Q.2.1.8 | Disabled rule skip | Each checker guarded by `if "{rule_id}" not in disabled_rules` |

### Q.2.2–Q.2.3 — Tier 2 (Valkey) and Tier 3 (DB) Rules

Tier 2 L4 pattern (applies to all Tier 2 rules):
1. Increment Valkey counter key `chirp:{rule_id}:{merchant_id}:{employee_id|card_id|location_id}:{window}`
2. Set TTL = window_seconds on first write
3. Read counter value → compare to threshold count
4. If count >= threshold: fire alert via `_make_alert()`

Tier 3 L4 pattern (applies to all Tier 3 rules):
1. Query PostgreSQL for required aggregate (shift totals, order line items, timecard state, etc.)
2. Apply threshold comparison
3. If threshold breached: fire alert

**C-502 POST_VOID_ALERT tiering (GRO-289):**
- `immediate_max_seconds=120`: <2 min gap → NO alert (legit correction)
- `watch_max_seconds=900`: 2-15 min gap → WATCH tier (severity=high)
- `suspicious_max_seconds=28800`: 15 min - 8 hr gap → SUSPICIOUS tier (severity=critical)
- Same-employee self-refund: +10 score boost
- Off-clock refund employee: +15 score boost

### Q.2.4–Q.2.5 — Rule Catalog API and Threshold Lookup

| L4 ID | Function | Behavior |
|-------|----------|----------|
| Q.2.4.1 | `get_rule(rule_id)` | RULE_MAP dict lookup → ChirpRuleDefinition or None |
| Q.2.4.2 | `get_rules_by_category(category)` | Filter RULE_CATALOG by category |
| Q.2.4.3 | `get_rules_by_tier(tier)` | Filter RULE_CATALOG by tier int |
| Q.2.4.4 | `get_stateless_rules()` | Alias for get_rules_by_tier(1) |
| Q.2.5.1 | `ThresholdManager.get_thresholds(merchant_id, rule_id)` | Cache key `chirp:thresholds:{merchant_id}:{rule_id}` → DB MerchantRuleConfig.custom_threshold → rule.default_thresholds |
| Q.2.5.2 | `ThresholdManager.get_all_active_rules(merchant_id)` | Cache key `chirp:active_rules:{merchant_id}` (TTL=300s) → DB configs → RULE_CATALOG (rules with is_enabled=False skipped) |
| Q.2.5.3 | `ThresholdManager.set_merchant_threshold(merchant_id, rule_id, thresholds)` | Upsert MerchantRuleConfig; `db.flush()`; call `invalidate_cache(merchant_id, rule_id)` |
| Q.2.5.4 | `ThresholdManager.invalidate_cache(merchant_id, rule_id)` | Delete `chirp:thresholds:{m}:{r}` AND `chirp:active_rules:{m}` |

---

## Q.3 — Case Management / Fox (5 L3s)

**Source:** `fox/case_service.py`, `fox/tools.py`  
**Key invariant:** chain_hash computed by PostgreSQL trigger `compute_entry_hash()` BEFORE INSERT (P0-3, B-001). Application code MUST NOT set chain_hash or previous_chain_hash.

**⚠️ GO SCHEMA NOTE — unified model:** The Python prototype implemented separate `fox_cases`, `fox_subjects`, `fox_case_actions`, `fox_timeline`, and `fox_evidence` tables as a build-speed shortcut. **CanaryGO does not use these tables.** Fox (`cmd/fox`) is the LP-specific case creation pathway into the unified Hawk schema. All Fox tools write to `hawk_cases`, `hawk_subjects`, `hawk_actions`, `hawk_timeline`. The LP-to-Hawk link is the `chirp_alert_id` FK on `hawk_cases`. Fox case types are `incident_type` rows in `hawk_incident_types` (theft, return_abuse, cash_variance, etc.). The L4 function behaviors documented below are behaviorally accurate; only the table names change. See CRB-L4-W.md §"W Module vs Q Module" for the full Fox/Hawk ownership map.

### Data Model (Python prototype VALID_* frozensets → Go: Hawk schema equivalents)

```
Case statuses:    open → investigating → pending_review → escalated → closed
                                                                     → referred_to_le
Case types:       theft | fraud | policy_violation | cash_variance | return_abuse | transaction_review | other
                  (CanaryGO: rows in hawk_incident_types with incident_class=internal)
Case priorities:  low | medium | high | critical
Subject types:    employee | customer | vendor | unknown  (hawk_subjects.subject_type)
Action types:     investigate | interview | suspend | terminate | refer_to_le | refer_to_hr | coaching | no_action | status_change
                  (CanaryGO: INTERNAL_ACTION_CODES in HawkCaseService)
Timeline events:  created | status_change | note_added | evidence_added | assigned | escalated | closed | action_added
                  (hawk_timeline.event_type)
```

Timeline metadata schema:
- `status_change`: requires {old_status, new_status}
- `evidence_added`: requires {evidence_id}
- `assigned`: requires {assigned_to}
- All others: no required keys

### FoxCaseService Methods (L4 Activities)

> Python prototype uses FoxCase/FoxSubject models. CanaryGO equivalent operates on HawkCase/HawkSubject with chirp_alert_id set on LP-originating cases.

| L4 ID | Method | Inputs | Behavior |
|-------|--------|--------|----------|
| Q.3.1.1 | `get_cases(merchant_id, status, created_after, page, limit)` | merchant_id required; status/created_after optional filters | Query FoxCase (→ hawk_cases), desc by opened_at, paginated; returns (cases, pagination) |
| Q.3.1.2 | `get_case_by_id(case_id, merchant_id)` | case_id + merchant_id | `.one()` — raises NoResultFound if not found (Hawk equivalent uses `.first()` + caller handles None — see W.3.1.2) |
| Q.3.2.1 | `add_subject(case_id, subject_type, entity_id, name, role)` | subject_type in VALID_SUBJECT_TYPES | Validate subject_type; `resolve_entity()` for employee type (checks Employee table); INSERT FoxSubject (→ hawk_subjects); flush |
| Q.3.2.2 | `add_action(case_id, action_type, description, user_id)` | action_type in VALID_ACTION_TYPES | INSERT FoxCaseAction (→ hawk_actions); INSERT FoxCaseTimeline (→ hawk_timeline) event_type="action_added"; flush |
| Q.3.3.1 | `get_case_evidence(case_id)` | case_id | Query FoxEvidence ordered by uploaded_at ASC |
| Q.3.3.2 | `get_evidence_by_id(evidence_id, case_id)` | both IDs | `.one()` |
| Q.3.4.1 | `validate_timeline_metadata(event_type, metadata)` | event_type string; metadata dict or JSON string | Validate required keys per _TIMELINE_METADATA_REQUIRED; raises ValueError on violation |
| Q.3.5.1 | `resolve_entity(db_session, subject_type, entity_id)` | subject_type="employee" | Query Employee.id; raises ValueError if not found |

### Q.3 MCP Tool Surface (from fox/tools.py → CanaryGO cmd/fox)

> cmd/fox provides LP-specific case creation tools. All writes land in Hawk tables. cmd/hawk owns the full case management surface (CRUD, workflow, card generation). Fox tools are LP alert→case entry points.

| Tool | Handler | Purpose |
|------|---------|---------|
| create_case | `_handle_create_case` | Open new LP case (sets chirp_alert_id on hawk_cases if alert-linked) |
| get_case | `_handle_get_case` | Get case details by ID |
| list_cases | `_handle_list_cases` | List cases with status/date filters |
| update_case_status | `_handle_update_case_status` | Transition status (validates state machine) |
| add_subject | `_handle_add_subject` | Link employee/vendor/party to case |
| get_timeline | `_handle_get_timeline` | Get append-only hash-chained audit trail |
| verify_chain | `_handle_verify_chain` | Verify evidence hash chain integrity |
| link_alert | `_handle_link_alert` | Link alert to existing case (sets chirp_alert_id FK) |

---

## Q.4 — Alert Triggers (4 L3s)

**Source:** `alert_lifecycle.py`  
**Alert model:** APPEND-ONLY. Status transitions written to AlertHistory; alert record is immutable.

| L4 ID | Function | Behavior |
|-------|----------|----------|
| Q.4.1.1 | Alert creation on rule fire | Chirp evaluation returns alert dict → persist to alerts table with status="new" |
| Q.4.1.2 | `is_stale(alert_created_at, ttl_days=14)` | Returns bool: alert_created_at < (now - ttl_days) |
| Q.4.2.1 | `resolve_status(alert_id, history_by_alert)` | Walk AlertHistory entries sorted ASC; return latest status or "new" |
| Q.4.2.2 | `is_terminal(status)` | status in TERMINAL_STATUSES {resolved, dismissed, case_opened, archived} |
| Q.4.3.1 | `get_active_alerts(alerts, history_by_alert, ttl_days)` | Filter: not terminal AND not stale |
| Q.4.3.2 | `get_stale_alerts(alerts, history_by_alert, ttl_days)` | Filter: not terminal AND is_stale |
| Q.4.4.1 | `build_archive_entries(stale_alerts, ttl_days)` | Create ArchiveEntry(alert_id, status="archived", changed_by="system:ttl", notes="Auto-archived: unactioned for N+ days") |
| Q.4.4.2 | `age_decay_factor(alert_created_at, ttl_days)` | Linear decay: 1.0 at creation → 0.0 at TTL; used by Owl for priority scoring |
| Q.4.4.3 | `alert_age_label(alert_created_at)` | Human label: "just now" / "{m}m ago" / "{h}h ago" / "{d}d ago" breakpoints |
| Q.4.4.4 | `lifecycle_summary(alerts, history_by_alert)` | Returns {total, active, stale, archived, resolved, dismissed, case_opened} counts |

**Alert status model:**
```
Active statuses:    new | investigating | escalated
Terminal statuses:  resolved | dismissed | case_opened | archived
```

---

## Q.5 — Alert Delivery (4 L3s)

**Source:** `alerts/tools.py`, `notification_service.py`, `notification_dispatcher.py`, `notification_preferences.py`

| L4 ID | Tool / Function | Behavior |
|-------|----------------|----------|
| Q.5.1.1 | `lifecycle_summary` tool | Pure function — computes active/stale/archived/resolved/dismissed/case_opened counts from alert list + history dict |
| Q.5.1.2 | `resolve_alert` tool | Write AlertHistory(status="resolved") for alert_id; merchant_id from context |
| Q.5.1.3 | `dismiss_alert` tool | Write AlertHistory(status="dismissed") for alert_id; optional notes |
| Q.5.2.1 | Alert routing config | Route by severity/type/store to correct investigator (notification_preferences model) |
| Q.5.3.1 | Alert acknowledgment | Investigator calls resolve_alert or dismiss_alert via MCP tool |
| Q.5.4.1 | Escalation delivery | Unacknowledged alert beyond TTL threshold → build_archive_entries → escalate |

---

## Q.6 — Allow-List Management (5 L3s)

**Source:** `chirp/threshold_manager.py`, `alert_config.py`

The allow-list IS the threshold model. "Allow-listing" a cashier/discount/void reason = setting merchant-specific thresholds that prevent rule firing for known-good patterns.

| L4 ID | Activity | Implementation |
|-------|----------|----------------|
| Q.6.1.1 | Dead-count allow-list | Set MerchantRuleConfig for C-011 (NO_SALE_DETECTED) with allowed employee_ids list |
| Q.6.2.1 | Known-discount allow-list | Set MerchantRuleConfig for C-007/C-201/C-203 with elevated threshold or approved_patterns list |
| Q.6.3.1 | Admin-void allow-list | Set MerchantRuleConfig for C-501/C-502 with allowed void reason codes |
| Q.6.4.1 | Manager-comp allow-list | Set MerchantRuleConfig for C-203 (SWEETHEARTING) with approved comp reason codes |
| Q.6.5.1 | Training-mode flag | Set MerchantRuleConfig.is_enabled=False for ALL rules for duration; `invalidate_cache(merchant_id)` |
| Q.6.x.1 | `set_merchant_threshold(merchant_id, rule_id, thresholds)` | Upsert MerchantRuleConfig; flush; invalidate Valkey cache keys |
| Q.6.x.2 | `invalidate_cache(merchant_id, rule_id=None)` | Delete specific rule key AND active_rules list key |

---

## Q.7 — MCP Investigator Tools (6 L3s)

**Source:** `chirp/tools.py`, `fox/tools.py`, `alerts/tools.py`

Full MCP tool manifest for the Go `cmd/chirp` + `cmd/fox` + `cmd/alert` servers:

| Tool | Server | Handler | Purpose |
|------|--------|---------|---------|
| get_rules | chirp | `_handle_get_rules` | Filter RULE_CATALOG by category/tier; returns rule list |
| get_rule | chirp | `_handle_get_rule` | Single rule lookup by rule_id |
| evaluate_stateless | chirp | `_handle_evaluate_stateless` | Tier 1 eval: parsed payload → alert list |
| apply_sensitivity | chirp | `_handle_apply_sensitivity` | Apply sensitivity preset (strict/default/relaxed/minimal) to merchant thresholds |
| get_templates | chirp | `_handle_get_templates` | Return available templates (retail_standard/food_service/high_value/high_volume/new_merchant) |
| apply_template | chirp | `_handle_apply_template` | Apply a named template to merchant threshold config |
| validate_thresholds | chirp | `_handle_validate_thresholds` | Validate threshold dict against rule schema |
| get_config_summary | chirp | `_handle_get_config_summary` | Return merchant's current Chirp config summary |
| estimate_sensitivity | chirp | `_handle_estimate_sensitivity` | Given threshold set, estimate expected alert volume |
| get_merchant_thresholds | chirp | `_handle_get_merchant_thresholds` | ThresholdManager.get_all_active_rules(merchant_id) |
| create_case | fox | `_handle_create_case` | Open new LP case |
| get_case | fox | `_handle_get_case` | Case detail by ID |
| list_cases | fox | `_handle_list_cases` | Case list with filters |
| update_case_status | fox | `_handle_update_case_status` | Status transition (state machine validated) |
| add_subject | fox | `_handle_add_subject` | Link subject to case |
| get_timeline | fox | `_handle_get_timeline` | Append-only timeline |
| verify_chain | fox | `_handle_verify_chain` | Chain integrity check |
| link_alert | fox | `_handle_link_alert` | Link alert to case |
| lifecycle_summary | alert | `_handle_lifecycle_summary` | Alert count breakdown |
| resolve_alert | alert | `_handle_resolve_alert` | Write resolved status |
| dismiss_alert | alert | `_handle_dismiss_alert` | Write dismissed status |

---

## Notes for Go Implementation

1. **Alert model is append-only.** No UPDATE on alerts table. All status changes go to AlertHistory (or equivalent). Fox enforces the same: chain_hash computed by PostgreSQL trigger — application NEVER sets it.

2. **Threshold cache invalidation is mandatory on write.** `set_merchant_threshold()` must call `invalidate_cache()` before returning. Stale Valkey thresholds cause false negatives in rule evaluation.

3. **Tier 1 rules are a pure function.** `evaluate_stateless()` has no DB or Valkey calls. It must remain that way — it's on the hot path of every webhook event. Any rule that requires a lookup is Tier 2 or 3.

4. **C-502 self-refund boost is a scoring modifier, not a separate rule.** The +10 score boost for same-employee sale+refund is applied inside the C-502 handler, not as a separate alert.

5. **Rule catalog is a compile-time constant.** RULE_CATALOG is a frozen list of frozen dataclasses. It should NOT be DB-backed in Go — it's code, not config. Merchant-specific changes are all in the threshold layer on top.

6. **Fox writes to Hawk tables (no fox_cases in Go).** The Python prototype's separate fox_* tables are prototype debt. In CanaryGO, cmd/fox tools operate on hawk_cases, hawk_subjects, hawk_actions, hawk_timeline. The LP-specific field is chirp_alert_id FK on hawk_cases. LP incident types are rows in hawk_incident_types. Fox case vocabulary maps directly to HawkIncidentType.incident_class=internal rows.

---

*Pass: GRO-670 / GRO-675 | Q L4 spec complete | 37 rules, all L4s derived from production Python code*

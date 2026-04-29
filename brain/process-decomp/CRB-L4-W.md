---
type: process-decomp
artifact: l4-spec
module: W — Work Execution
pass-date: 2026-04-28
source: GRO-670 / GRO-675
method: Track A — Python codebase translation
python-sources:
  - Canary/canary/services/hawk/case_service.py
  - Canary/canary/services/hawk/card_service.py
  - Canary/canary/services/hawk/tools.py
  - Canary/canary/services/velocity_engine.py
confidence: HIGH — all L4s derived from implemented production code
key-discovery: hawk/ Python service = W (Work Execution) module. cmd/hawk in CanaryGO maps to W.
---

# CRB L4 Spec — Module W: Work Execution

**Governing note:** The W module's Python implementation is `hawk/`. The CanaryGO package is `cmd/hawk`. This was confirmed during the L4 fill pass — Hawk IS the cross-domain case management system that generalizes Fox (Q.3) across all investigable domains.

**W-over-Fox:** Hawk extends the Fox pattern with four additions:
1. Incident type catalog (`HawkIncidentType`) — structured case taxonomy, not free-form type string
2. `incident_class` determines resolution track (internal vs external)
3. `generate_card()` — structured narrative card generation (versioned, invalidatable)
4. `get_wizard_template()` — incident type wizard (guided case opening)

---

## W.1–W.2 — Exception Detection and Aggregation

**Source:** `velocity_engine.py`, `chirp/rule_engine.py` (cross-domain adaptation)  
**Architecture:** W.1–W.2 generalize the Chirp detection pattern across all domains (not just LP). The same velocity anomaly engine that detects LP exceptions is reused for inventory, labor, and financial anomalies.

### W.1 — Cross-Domain Exception Detection

| L4 ID | Function | Behavior |
|-------|----------|----------|
| W.1.1.1 | `compute_baseline(daily_values: list[float]) → BaselineStats` | Rolling window (default 30 days). Computes mean and stddev. Returns BaselineStats(mean, std_dev, sample_count). Requires ≥3 values; returns None baseline if insufficient data. |
| W.1.2.1 | `detect_anomaly(current_value, baseline, sigma_threshold=2.0) → AnomalyResult` | z_score = (current_value - baseline.mean) / baseline.std_dev. AnomalyType: spike (z > +threshold), drop (z < -threshold), zero (current_value == 0 AND baseline.mean > 0). Returns AnomalyResult(is_anomaly, anomaly_type, z_score, current_value, baseline). |
| W.1.3.1 | Day-of-week pattern learning | Baseline computed per (merchant_id, metric_key, day_of_week) — separate baselines for Mon/Tue/Wed etc. |
| W.1.4.1 | Hour-of-day pattern learning | Baseline computed per (merchant_id, metric_key, hour_of_day) — separate baselines for each hour slot |
| W.1.5.1 | Cross-domain exception alert | When detect_anomaly fires: publish cross-domain exception event with domain label (inventory, finance, labor, LP) |

**AnomalyResult fields:** is_anomaly: bool, anomaly_type: str ("spike" | "drop" | "zero" | None), z_score: float, current_value: float, baseline: BaselineStats

**Constants:**
- DEFAULT_SIGMA_THRESHOLD = 2.0
- DEFAULT_WINDOW_DAYS = 30

### W.2 — Exception Aggregation

| L4 ID | Activity | Behavior |
|-------|----------|----------|
| W.2.1.1 | Collect domain-scoped exceptions | Aggregate exceptions from Q (LP), D (inventory), F (finance), L (labor) into unified exception queue |
| W.2.2.1 | Dedup by subject | Group exceptions by subject (employee_id, vendor_id, customer_id) across domains |
| W.2.3.1 | Correlation scoring | Score subject risk across domains: LP alert + inventory variance + off-clock = elevated composite score |

---

## W.3 — Case CRUD (HawkCaseService)

**Source:** `hawk/case_service.py` → `HawkCaseService`

### Status FSM

```
open → investigating → pending_review → escalated → closed
                                      ↗            ↗
                       investigating ──────────────→ referred_to_le
```

**VALID_TRANSITIONS:**
```python
"open":           ["investigating"]
"investigating":  ["pending_review", "escalated"]
"pending_review": ["escalated", "closed", "referred_to_le"]
"escalated":      ["closed", "referred_to_le"]
"closed":         []          # terminal
"referred_to_le": []          # terminal
```

### Resolution Tracks

incident_class → action code vocabulary:
- `internal` → INTERNAL_ACTION_CODES: CLOSED_UNFOUNDED, CORRECTIVE_ACTION, INTERVIEWED_NO_CASE, QUIT_BEFORE_INTERVIEW, QUIT_DURING_INTERVIEW, REPORTED_TO_ATF, TERMINATED_PROSECUTED, TERMINATED_RELEASED, UNDER_INVESTIGATION
- `external` | `critical_smart_alert` | `incident` → EXTERNAL_ACTION_CODES: CLOSED_UNFOUNDED, PROSECUTED, RELEASED_ADULT, RELEASED_TO_GUARDIAN, RELEASED_TO_POLICE, UNDER_INVESTIGATION

### HawkCaseService Methods (L4 Activities)

| L4 ID | Method | Key Behavior |
|-------|--------|-------------|
| W.3.1.1 | `create_case(merchant_id, location_id, incident_type, opened_by, narrative, source_code, assigned_to, chirp_alert_id)` | Lookup HawkIncidentType by incident_type; raises ValueError if not found. Derive incident_class and de_pv_flag from HawkIncidentType. Lookup HawkSource by source_code if provided. INSERT HawkCase(status="open"). Auto-create timeline entry event_type="created". |
| W.3.1.2 | `get_case(case_id)` | Query HawkCase by id; returns None if not found (vs Fox which raises NoResultFound — important difference) |
| W.3.1.3 | `list_cases(merchant_id, status, incident_class, limit=50, offset=0)` | Filter by merchant + optional status + optional incident_class; ORDER BY opened_at DESC |
| W.3.2.1 | `advance_status(case_id, new_status, actor_id)` | Lookup case; get current status; validate VALID_TRANSITIONS[current] contains new_status; on terminal: set closed_at=now(); create timeline entry event_type="status_changed" with event_data={from, to}; flush |
| W.3.3.1 | `add_subject(case_id, subject_type, actor_id, employee_id, vendor_entity_id, external_name, notes)` | Validate subject_type in VALID_SUBJECT_TYPES; lookup case; INSERT HawkSubject; timeline entry event_type="subject_added" |
| W.3.4.1 | `add_action(case_id, action_code, actor_id, notes)` | Lookup case; derive track from incident_class via _CLASS_TO_TRACK; validate action_code against track's valid set; INSERT HawkAction; timeline entry event_type="action_added" |

### W.3 vs Q.3 (Fox) Differences

| Aspect | Q.3 Fox | W.3 Hawk |
|--------|---------|---------|
| Case type input | Free-form string from VALID_CASE_TYPES frozenset | incident_type lookup against HawkIncidentType catalog |
| incident_class | Not present | Derived from HawkIncidentType.incident_class |
| de_pv_flag | Not present | Derived from HawkIncidentType.de_pv_flag |
| Action codes | VALID_ACTION_TYPES frozenset (uniform) | Split by resolution track (internal vs external) |
| Not-found behavior | `.one()` raises NoResultFound | `.first()` returns None, caller handles |
| Narrative card | Not present | generate_card() produces versioned structured card |

---

## W.4 — Remediation Routing

**Source:** `hawk/case_service.py` → `add_action()`, `advance_status()`  
**Source:** `hawk/tools.py` → `advance_workflow` tool

Remediation in W is case action recording + status FSM advancement. There is no separate "remediation routing" service — the action code captures the resolution disposition; the status FSM gates advancement.

| L4 ID | Activity | Behavior |
|-------|----------|----------|
| W.4.1.1 | Record resolution action | `add_action(case_id, action_code, actor_id)` — validates track, creates HawkAction, timeline entry |
| W.4.1.2 | Advance to closed/referred_to_le | `advance_status(case_id, "closed" or "referred_to_le", actor_id)` — sets closed_at, creates timeline entry |
| W.4.1.3 | Approval gate before close | MCP tool `advance_workflow` with target_status="closed" — investigator confirms before status advances |
| W.4.1.4 | Cross-domain dispatch | For actions affecting other modules (e.g., labor disciplinary → HR system): W.5.5 remediation routing tool dispatches to target module's API |

---

## W.5 — MCP Investigator Tools (W.5.1–W.5.6)

**Source:** `hawk/tools.py`  
**CanaryGO server:** `cmd/hawk` MCP server

Full tool manifest:

| Tool | Purpose | Key Params |
|------|---------|-----------|
| `create_case` | Open new Hawk case | merchant_id, location_id, incident_type, opened_by, narrative, source_code |
| `get_case` | Case detail by ID | case_id |
| `list_cases` | List cases with filters | merchant_id, status, incident_class, limit, offset |
| `advance_workflow` | Advance case through FSM | case_id, new_status, actor_id — validates VALID_TRANSITIONS |
| `add_subject` | Link subject to case | case_id, subject_type, actor_id, employee_id/vendor_entity_id/external_name |
| `add_action` | Record resolution action | case_id, action_code, actor_id, notes |
| `generate_card` | Generate narrative card | case_id, actor_id → versioned markdown card |
| `get_timeline` | Case audit trail | case_id → HawkTimeline entries ordered ASC |
| `get_wizard_template` | Incident type wizard | incident_type → guided card template |

### W.5.7 — generate_card() L4 Activities

**Source:** `hawk/card_service.py` → `HawkCardService.generate_card()`

| L4 ID | Activity | Behavior |
|-------|----------|----------|
| W.5.7.1 | Load case + relationships | Query HawkCase; load case.subjects and case.actions via ORM |
| W.5.7.2 | Determine next card version | If case.card_id exists: lookup prior HawkCard; next_version = prior.card_version + 1. If no prior card: next_version = 1. |
| W.5.7.3 | Invalidate prior card | If prior_card exists and prior_card.invalidated_at is None: set invalidated_at = now() |
| W.5.7.4 | Build card body | `_build_card_body(case, subjects, actions)` → structured markdown with case summary, subject list, action log |
| W.5.7.5 | Build frontmatter JSONB | Structured metadata: case_id, merchant_id, incident_type, incident_class, status, card_version, generated_at |
| W.5.7.6 | INSERT HawkCard | Fields: case_id, merchant_id, card_version, card_body, frontmatter, generated_by=actor_id |
| W.5.7.7 | Link card to case | `case.card_id = card.id`; flush |
| W.5.7.8 | Timeline entry | event_type="card_generated"; event_data={card_id, card_version} |

---

## Module W Data Model — Unified Case Schema

**One schema. Fox writes into Hawk tables.** The `chirp_alert_id` field on `hawk_cases` is the tell — the design always intended LP cases to live in the Hawk schema. The Python prototype implemented separate Fox tables as a build-speed shortcut; that is prototype debt. CanaryGO uses the unified schema.

Tables:
- `hawk_cases` — ALL cases, all domains. Fields: status, incident_class, incident_type, de_pv_flag, opened_by, closed_at, **chirp_alert_id** (FK to LP alert — present only on Fox-created cases), card_id
- `hawk_incident_types` — catalog of valid incident types with display_name, incident_class, de_pv_flag. LP types (theft, void_abuse, cash_variance, return_abuse, etc.) are rows in this table.
- `hawk_sources` — source code catalog (CHIRP_ALERT, MANUAL, DEVICE_ALERT, etc.)
- `hawk_subjects` — case subjects across all domains (employee_id, vendor_entity_id, external_name, subject_type)
- `hawk_actions` — resolution actions with track-validated action codes
- `hawk_timeline` — append-only audit trail (event_type, actor_id, description, event_data JSONB)
- `hawk_cards` — versioned narrative cards (card_body, frontmatter JSONB, card_version, invalidated_at)

---

## W Module vs Q Module: Fox is the LP Pathway INTO Hawk (Resolves OVERLAP #4 from Lint Report)

**Hawk is the unified case management system. Fox is the LP alert-to-case creation pathway.** Fox does not own tables — it writes into Hawk tables.

| | Fox (Q.3) | Hawk (W.3) |
|---|---|---|
| **What it is** | LP alert → case creation pathway + LP-specific MCP tools | Unified case management system and investigator surface |
| **Tables** | None — writes to `hawk_cases` via chirp_alert_id | Owns all case tables |
| **Case creation trigger** | LP rule fires → alert → investigator creates case | Manual, cross-domain exception, device alert, any source |
| **incident_type** | LP types from hawk_incident_types catalog | All types across all domains |
| **UI surface** | Alert notification → case-from-alert flow | Full case management interface, cross-domain views |
| **MCP tools** | LP-specific tools (create_case_from_alert, link_alert, etc.) operating on Hawk tables | Full case CRUD, advance_workflow, generate_card, etc. |

**Go implementation:** `cmd/fox` provides LP-specific case creation tools. `cmd/hawk` owns the unified schema and full case management surface. No `fox_cases` table. The distinction is in tooling and UX, not data ownership.

---

*Pass: GRO-670 / GRO-675 | W L4 spec complete | hawk/ confirmed as W module | OVERLAP #4 resolved in notes | cmd/hawk ≠ unknown*

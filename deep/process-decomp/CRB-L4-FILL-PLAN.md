---
type: process-decomp
artifact: l4-fill-plan
pass-date: 2026-04-28
source: GRO-670 / GRO-675
method: CRB L4 sourcing strategy — merged with A/B/C scope framework
version: 1
---

# CRB L4 Fill Plan — 2026-04-28

**Governing thesis:** The 357 MISSING-L4 flags in CRB-LINT-REPORT.md are not uniformly a documentation problem. For Category A processes — the ~120 L3s Canary owns — L4 activities already exist as working Python code in the Canary prototype (`Canary/canary/services/`). The L4 fill pass for Category A is a **code-to-spec translation**, not a documentation search. For Category B, L4s derive from the NCR/Counterpoint REST API docs. For Category C, no workflow L4s are needed — export API surface design only.

This reframes GRO-675 (L4 documentation pass) into three parallel tracks with distinct sources, sequences, and ownership.

---

## Revised GRO-675 Framing

| Track | Scope | L3 Count | L4 Source | Method |
|-------|-------|----------|-----------|--------|
| **Track A — Code Translation** | Category A: Canary owns | ~120 | Canary Python codebase (`Canary/canary/services/`) | Read Python service → extract function signatures, data contracts, state machines → write Go implementation spec |
| **Track B — API Docs** | Category B: Interface layer on Counterpoint | ~162 | NCR Counterpoint REST API documentation + PS_DOC schema | Map endpoint → request/response contract → Go struct + handler spec |
| **Track C — Export Surface** | Category C: Retailer has another solution | ~117 | Canary canonical data model (output schema only) | Specify export API endpoints only; no workflow L4s |

**Impact on lint report:** MISSING-L4 count stays at 357 until fill pass runs, but the resolution path and urgency changes by track. Track A (Category A) should be prioritized — these L4s are what a Go engineer needs to build Canary's core competency correctly.

---

## Track A — Category A Python Service Map

### Module T — Transaction Pipeline (Category A L3s)

The TSP pipeline is the best-documented subsystem in the codebase. Every sub-consumer has its own file with a processing sequence comment that is already L4-quality.

| L3 ID | L3 Process | Python Source(s) | L4 Extraction Note |
|-------|-----------|-----------------|-------------------|
| T.2.3 | Hash-before-parse | `tsp/consumers/sub1_seal.py` | `process_message()` Step 2: SHA-256(raw_payload) verify before JSON parse — explicit ordering constraint, patent-critical |
| T.2.4 | Seal record write | `tsp/consumers/sub1_seal.py` | Step 7: INSERT EvidenceRecord — write-once, advisory lock per merchant_id; model at `canary/models/sales/evidence.py` |
| T.2.5 | Fanout routing | `tsp/consumers/sub2_parse.py`, `sub4_detect.py` | Sub2 parses canonical event; Sub4 fans out to detection engine |
| T.2.6 | Mutation-lock | `tsp/consumers/sub1_seal.py` | Advisory lock + INSERT-only constraint; no UPDATE/DELETE path in code |
| T.4.1–T.4.9 | Canonical event publication (SALE, RETURN, VOID, PAYMENT, TAX, AUDIT, routing, customer upsert) | `tsp/stream_publisher.py`, `tsp/enrichers/square.py` | Event type routing table + enrichment schema; Counterpoint equivalent is `tsp/enrichers/` (new enricher per source) |
| T.5.1–T.5.5 | Merkle anchoring | `tsp/merkle.py`, `tsp/consumers/sub3_merkle.py` | `build_tree()`: sort→double-hash leaves→pad to power of 2→build bottom-up→generate proof. `verify_proof()`: recompute root from proof path. Patent #63/991,596 |
| T.7.1–T.7.12 | Substrate contracts | `tsp/tools.py` | MCP tool definitions = substrate API contracts for downstream consumers |

**Key invariants from sub1_seal.py (must be preserved in Go):**
- `BATCH_SIZE = 1` — chain integrity requires single-message processing
- Advisory lock per `merchant_id` before chain hash computation
- Hash verification (BEFORE parse) is the patent-critical ordering; never swap

---

### Module Q — Loss Prevention (all 38 L3s)

Q is the most complete subsystem in the Python prototype. L4s can be extracted with high confidence.

| L2 | L3 IDs | Python Source(s) | L4 Extraction Note |
|----|--------|-----------------|-------------------|
| Q.1 Substrate ingestion | Q.1.1–Q.1.5 | `tsp/consumers/sub4_detect.py`, `chirp/rule_engine.py` | Sub4 bridges TSP output to Chirp detection input; `rule_engine.py` contains the dispatch logic |
| Q.2 Detection rules | Q.2.1–Q.2.10 | `chirp/rule_definitions.py`, `chirp/stateless_engine.py`, `chirp/rule_engine.py` | `RULE_CATALOG` dict in rule_definitions = authoritative rule spec; `evaluate_stateless()` in stateless_engine = Tier 1 impl; `rule_engine.py` = Tier 2/3 dispatch |
| Q.3 Case management (Fox) | Q.3.1–Q.3.5 | `fox/case_service.py`, `fox/tools.py` | `FoxCaseService` class: create_case, get_case, list_cases, update_case_status (validated state machine), add_subject, get_timeline, verify_chain, link_alert. VALID_* frozensets = state machine spec. Note: chain_hash computed by PostgreSQL trigger, NOT app code (P0-3, B-001) |
| Q.4 Alert triggers | Q.4.1–Q.4.4 | `alert_lifecycle.py` | Alert creation on rule fire; trigger → alert handoff contract |
| Q.5 Alert delivery | Q.5.1–Q.5.4 | `alerts/tools.py`, `notification_service.py`, `notification_dispatcher.py`, `notification_preferences.py` | lifecycle_summary, resolve_alert, dismiss_alert tools; notification routing and preferences model |
| Q.6 Allow-list management | Q.6.1–Q.6.5 | `chirp/threshold_manager.py`, `alert_config.py` | `ThresholdManager`: cache→DB→defaults resolution chain; `apply_sensitivity()`, `apply_template()`, `get_available_templates()` |
| Q.7 MCP investigator tools | Q.7.1–Q.7.6 | `chirp/tools.py`, `fox/tools.py`, `alerts/tools.py` | Full tool manifest already exists — these are the Go MCP server tool definitions |

**Fox state machine (from VALID_STATUSES frozenset):**
```
open → investigating → pending_review → escalated → closed
                                                  → referred_to_le
```
This is the L4 state machine spec for Q.3.2.

**Chirp rule tiers (from rule_definitions.py):**
- Tier 1: Stateless — evaluate_stateless() — pure function, no I/O
- Tier 2: Valkey counters — velocity-based rules
- Tier 3: Full DB — cross-transaction correlation rules

---

### Module N — LP Substrate Config (Category A L3s)

| L3 ID | L3 Process | Python Source(s) | L4 Extraction Note |
|-------|-----------|-----------------|-------------------|
| N.4.1 | Drawer config thresholds | `chirp/threshold_manager.py` | ThresholdManager.get_merchant_thresholds() — cash_drawer fields; feeds Q-DC-01 |
| N.4.2 | Discount cap config | `chirp/threshold_manager.py`, `alert_config.py` | discount_threshold fields in threshold model |
| N.4.3 | Void reason codes | `chirp/threshold_manager.py` | void_reason_codes allow-list in threshold model |
| N.4.4 | Comp reason codes | `chirp/threshold_manager.py` | comp_reason_codes allow-list |
| N.5.1–N.5.2 | Device health + connectivity alerts | `health_check/heartbeat.py`, `health_check/runner.py`, `notification_service.py` | Heartbeat monitors POS health; notification_service routes alerts |

---

### Module C — Customer Intelligence (Category A L3s)

| L3 ID | L3 Process | Python Source(s) | L4 Extraction Note |
|-------|-----------|-----------------|-------------------|
| C.2.1–C.2.4 | Customer risk scoring + behavioral pattern detection | `employee_risk_scoring.py`, `heatmap_scoring.py` | Risk scoring logic; heatmap_scoring.py provides the spatial/behavioral pattern model |
| C.6.1–C.6.4 | Investigator surface (lookup, history, risk score, cross-module context) | `identity/tools.py`, `identity/external_id_resolver.py`, `fox/tools.py` | identity/tools = customer lookup MCP surface; fox/tools = cross-case subject context |

---

### Module D — Distribution Analytics (Category A L3s)

| L3 ID | L3 Process | Python Source(s) | L4 Extraction Note |
|-------|-----------|-----------------|-------------------|
| D.4.1–D.4.5 | Transfer-loss reconciliation + adjudication | `analytics/tools.py`, `velocity_engine.py` | velocity_engine: `compute_baseline()` / `detect_anomaly()` — XPLOSS DNA, Poisson-process velocity monitoring. Day-of-week + hour-of-day pattern learning. Anomaly types: spike, drop, zero |
| D.5.1–D.5.4 | Distribution reconciliation analytics | `analytics/tools.py`, `dashboard_queries.py` | Analytics surface on inventory variance; chart_queries.py for visualization |

---

### Module F — Finance Analytics (Category A L3s)

| L3 ID | L3 Process | Python Source(s) | L4 Extraction Note |
|-------|-----------|-----------------|-------------------|
| F.2.1–F.2.4 | Financial metrics connected to LP outcomes | `analytics/tools.py`, `dashboard.py`, `dashboard_queries.py`, `dashboard_tiles.py`, `chart_queries.py` | LP-connected financial surfaces: shrink cost, recovery rate, variance by period |

---

### Module S — Space/Range Analytics (Category A L3s)

| L3 ID | L3 Process | Python Source(s) | L4 Extraction Note |
|-------|-----------|-----------------|-------------------|
| S.5.1–S.5.3 | Item lifecycle / drift detection and alerts | `velocity_engine.py` | `detect_anomaly()` with item-scoped baseline — spike/drop on item KPIs |
| S.7.1–S.7.3 | Category analytics + margin target surface | `analytics/tools.py`, `chirp/threshold_manager.py` | S.7.2 margin targets stored in threshold model; feed Q-ME-01 |

---

### Module P — Pricing Intelligence (Category A L3s)

| L3 ID | L3 Process | Python Source(s) | L4 Extraction Note |
|-------|-----------|-----------------|-------------------|
| P.2.1–P.2.3 | Promotional window inference from price variance | `chirp/rule_definitions.py` | Promo inference prevents Q false positives — look for promo detection logic in rule catalog; price variance signal from item data |

---

### Module M — B2B Detection (Category A L3s)

| L3 ID | L3 Process | Python Source(s) | L4 Extraction Note |
|-------|-----------|-----------------|-------------------|
| M.4.1–M.4.5 | B2B detection rules Q-M-01 through Q-M-05 | `chirp/rule_definitions.py`, `chirp/rule_engine.py` | B2B rules in RULE_CATALOG routed through Chirp pipeline; same execution path as standard Q rules |

---

### Module L — Labor/LP Context (Category A L3s)

| L3 ID | L3 Process | Python Source(s) | L4 Extraction Note |
|-------|-----------|-----------------|-------------------|
| L.3.3 | Employee productivity signal to Q (LP context) | `employee_risk_scoring.py`, `analytics/tools.py` | Productivity metrics computed from transaction velocity; signal surfaced to Q investigator |

---

### Module E — Execution (all 14 L3s)

**Key discovery:** `hawk/` in the Python prototype IS the W module. `cmd/hawk` in CanaryGO maps to W (Execution), not an unknown package. The `cmd/bull` unknown is still unresolved.

| L2 | Python Source(s) | L4 Extraction Note |
|----|-----------------|-------------------|
| E.1–E.2 Exception detection + aggregation | `velocity_engine.py`, `chirp/rule_engine.py` | Cross-domain anomaly detection generalizes Chirp beyond LP |
| E.3 Case CRUD (cross-domain Fox) | `hawk/case_service.py` | HawkCaseService extends Fox pattern to all domains; FSM: `advance_workflow()` |
| E.4 Remediation routing | `hawk/tools.py` | `add_action()`, `advance_workflow()` — dispatch remediation to target module |
| E.5 MCP investigator tools | `hawk/tools.py` | Full tool manifest: create_case, get_case, list_cases, advance_workflow, add_subject, add_action, generate_card, get_timeline, get_wizard_template |

**Hawk-specific additions vs Fox:**
- `generate_card()` — narrative card generation (not in Fox)
- `get_wizard_template()` — incident type wizard (not in Fox)
- `advance_workflow()` — FSM with explicit workflow advancement (Fox uses `update_case_status()`)

These additions are the W-over-Fox generalization — the L4 spec difference between Q.3 and E.3.

---

## Track B — Category B Counterpoint API Source Map

L4 activities for Category B are derived from NCR Counterpoint REST API documentation and the PS_DOC schema. No Python code to translate — these are net-new integrations.

| Module | L2 / L3 Group | Primary API Doc Source | Secondary Source |
|--------|--------------|----------------------|-----------------|
| T.1 | Transaction ingestion pipeline | `GET /Documents` endpoint spec — request params, response schema, pagination, auth | PS_DOC + child table schema |
| T.3 | DOC_TYP-keyed parsing | PS_DOC field catalog — DOC_TYP values, header fields, PS_DOC_LIN, PS_DOC_PMT, audit log | Counterpoint data dictionary |
| T.6 | Historical backfill | `/Documents` with date range + offset params; sealed ledger replay spec | Internal replay design |
| C.1 | Customer profile sync | `GET /Customers` endpoint — fields, pagination, delta sync | PS_CUST table schema |
| C.3–C.5 | Customer search, history, privacy | `GET /Customers/{id}`, `/Documents?customer=` | Privacy model (internal) |
| N.1–N.3 | Store config ingestion | `GET /StoreSettings` — ~150 fields from PS_STR_CFG_PS; device registration endpoints | PS_STR_CFG_PS field list |
| S.1–S.4 | Item catalog (17 endpoints) | All IM_ITEM endpoints — PRIC_1–N, discount matrix, UOM, bundle rules | PS_DOC_LIN_PRICE schema |
| D.1–D.2 | Inventory snapshot (7 endpoints) | `GET /Inventory` endpoints — location filter, delta processing | PS_INV table schema |
| D.3 | Transfer lifecycle | XFER document type via `/Documents` — DOC_TYP=XFER | Transfer status fields |
| F.1 | PayCode + TaxCode cache | `GET /PayCodes`, `GET /TaxCodes` — 24h cache strategy | Secure Pay registration API |
| F.4–F.5 | Payment flow + Secure Pay | NSPTransaction schema, Secure Pay registration, tokenization flow | Counterpoint Secure Pay docs |
| O.6–O.7 | Receiving + RTV lifecycle | RECVR and RTV document types via `/Documents` — DOC_TYP=RECVR, DOC_TYP=RTV | Receiving workflow fields |
| P.1 | Price observation | IM_ITEM price fields — PRIC_1 through PRIC_N, discount matrix | PS_DOC_LIN_PRICE |

**Note on T.2.1–T.2.2 (receipt stamp + dedup):** These are infrastructure L3s. L4 spec comes from internal idempotency design, not Counterpoint docs.

---

## Track C — Category C Export API Surface

No workflow L4s required. For each Category C module, specify the export API endpoint shape and the data Canary surfaces. The retailer's existing system calls Canary; Canary does not own the workflow.

| Module | Category C L3s | Export API Surface |
|--------|---------------|-------------------|
| O.1–O.5, O.8 | Forecasting, ROP, OTB, PO engine | `GET /api/v1/forecast/{item_id}` — historical demand + projected units + confidence interval. `GET /api/v1/inventory/replenishment-candidates` — items below ROP. `GET /api/v1/open-to-buy/{period}` — OTB balance. Planning tools call these; Canary doesn't own the PO. |
| O.4 | PO suggestion (export) | `GET /api/v1/suggested-orders` — suggested quantity per item per vendor. O.4.4 write-back (POST /Document to Counterpoint) is v2+ only — default posture is export. |
| F.3, F.6 | Stock ledger, financial reporting | `GET /api/v1/analytics/inventory-value` — inventory position by location/category. Financial reporting stays in QuickBooks/Sage. |
| P.3–P.6 | Markdown, clearance, comp pricing, promotion calendar | `GET /api/v1/promotions` — promotion calendar read (for Q LP accuracy). Markdown and clearance workflows stay in Counterpoint. |
| S.6 | Range planning | `GET /api/v1/analytics/range-performance` — sell-through, turn, GMROI by item/category. Range decisions stay with buyer. |
| M.1–M.3, M.5 | B2B account mgmt, credit/invoicing, AR | `GET /api/v1/b2b/analytics` — B2B transaction patterns for LP context. Account and AR management stays in Counterpoint + QuickBooks. |
| L.1–L.2, L.4–L.5 | Employee sync, scheduling, payroll | `GET /api/v1/analytics/labor-productivity` — transactions/hour, productivity signals for LP. Scheduling and payroll stay in ADP/Homebase/Gusto. |

---

## Fill Sequencing

### Week 1 — Track A Priority (Category A, no UX dependency)

Spec systematic Category A L4s from codebase. Priority order:

1. **Q module (all 38 L3s)** — fox/case_service.py + chirp/* = complete source. Highest value. Go engineer needs this first.
2. **T module Category A L3s** (T.2.3, T.2.4–T.2.6, T.4.1–T.4.9, T.5.1–T.5.5) — sub1_seal.py + merkle.py = precise spec available.
3. **N.4.x LP substrate config** — threshold_manager.py = complete source.
4. **W module (all 14 L3s)** — hawk/case_service.py + hawk/tools.py = complete source. Confirm `cmd/hawk` = W module.

### Week 2 — Track B Priority (Category B systematic L3s)

Spec Category B L4s from Counterpoint API docs. Priority order:

1. **T.1 Transaction ingestion** (T.1.1–T.1.9) — `GET /Documents` is the foundation everything runs on.
2. **S.1–S.4 Item catalog** (17 endpoints) — needed for Q item context and LP accuracy.
3. **C.1 Customer sync** (C.1.1–C.1.5) — needed for investigator surface.
4. **D.1–D.2 Inventory snapshot** (7 endpoints) — needed for transfer-loss analytics.

### Week 3+ — Remaining Track A + Track B

- Track A: C.2.x risk scoring, D.4–D.5 analytics, F.2.x LP analytics, S.5.x drift, P.2.x promo inference
- Track B: N.1–N.3 store config, F.1 PayCode/TaxCode, F.4–F.5 payment flow, O.6–O.7 receiving/RTV
- Track C: Export API specs (low urgency — needed for v1.1, not launch)

### Blocked until ASSUMPTION-A-01 resolved

All 12 Module A L3s (regardless of track) remain blocked pending Jeffe's decision on Module A scope. See GRO-674.

---

## Updated GRO-675 Issue Description

> **Revised scope:** L4 fill pass is three parallel tracks, not one uniform documentation pass.
>
> **Track A (Category A, ~120 L3s):** Code-to-spec translation from Canary Python prototype. Source files confirmed: `chirp/`, `fox/`, `tsp/consumers/`, `tsp/merkle.py`, `evidence_chain.py`, `velocity_engine.py`, `impact_scoring.py`, `hawk/`, `alerts/`, `notification_service.py`. Week 1 priority: Q module + T evidentiary L3s.
>
> **Track B (Category B, ~162 L3s):** L4s from NCR Counterpoint REST API docs. Source: `/Documents` endpoint, IM_ITEM endpoints, PS_DOC schema, PS_STR_CFG_PS. Week 2 priority: T.1 ingestion + S.1–S.4 item catalog.
>
> **Track C (Category C, ~117 L3s):** Export API surface only. No workflow L4s. Spec the endpoint shape; retailer's systems own the workflow.

---

## Codebase Intel: Confirmed Service-to-Module Mapping

Derived from Python prototype service directory, to inform CanaryGO `cmd/` package assignment:

| Python Service | CanaryGO `cmd/` Package | CRB Module | Status |
|---------------|------------------------|-----------|--------|
| `tsp/` | `cmd/tsp` | T | DOCUMENTED |
| `chirp/` | `cmd/chirp` | Q (detection) | DOCUMENTED |
| `fox/` | `cmd/fox` | Q (case mgmt) | DOCUMENTED |
| `alerts/` + `alert_lifecycle.py` | `cmd/alert` | Q (alert delivery) | DOCUMENTED |
| `hawk/` | `cmd/hawk` | **W (Execution)** | **CONFIRMED HERE** — hawk IS the W module |
| `identity/` | `cmd/identity` | Auth/tenant infra | DOCUMENTED |
| `evidence_chain.py` | `cmd/tsp` (sub1) | T.2.x (evidentiary) | DOCUMENTED |
| `velocity_engine.py` | `cmd/analytics` or `cmd/chirp` | D.4, S.5, E.1 | INFERRED — single engine, multi-module use |
| `impact_scoring.py` | `cmd/alert` | Q.4 (alert impact) | INFERRED |
| `condor/` | `cmd/owl`? | Cross-module intelligence | INFERRED — benchmarks + external intel |
| `analytics/` | `cmd/analytics` | F, D, S analytics | DOCUMENTED |
| `employee_risk_scoring.py` | `cmd/employee` | C.2, L.3 | INFERRED |
| `notification_service.py` + `notification_dispatcher.py` | `cmd/alert` | Q.5 | INFERRED |
| `health_check/` | `cmd/edge`? | N.5 device health | INFERRED — confirms edge = N module |

**`cmd/bull` remains UNKNOWN.** Likely infrastructure (job queue runner, ETL runner) — `etl_runner.py` and `period_aggregation.py` in the Python prototype are the candidates. Inspect `cmd/bull` to confirm.

---

*Pass: GRO-670 / GRO-675 | L4 Fill Plan v1 | A/B/C tracks confirmed | hawk/=W module discovery | cmd/bull still unknown*

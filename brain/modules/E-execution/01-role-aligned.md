---
title: W — Role Alignment
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-e, work-execution, exception-detection, case-management, cross-domain, v3]
sources:
  - Canary-Retail-Brain/modules/E-execution.md
  - Canary-Retail-Brain/modules/Q-loss-prevention.md
  - Canary-Retail-Brain/platform/stock-ledger.md
  - Canary-Retail-Brain/platform/spine-13-prefix.md
last-compiled: 2026-04-24
----

# Canary Module — W (Execution)

## Summary

W (Execution) is the cross-domain exception detection and case management surface. **v3 design — implementation deferred.** This wiki article is the Canary-specific crosswalk for the v3 W module. The canonical, vendor-neutral module spec lives at `Canary-Retail-Brain/modules/E-execution.md`.

W is the capstone of the Canary Retail Spine. It generalizes Q's (Loss Prevention) Chirp+Fox pattern across all domains: inventory, commercial, pricing, labor, and space. W detects exceptions everywhere and correlates them. When a customer appears in both a fraud alert (Q) and a return-abuse pattern (P), W connects them in one case, not two. W is the retail operating system's immune system.

## Code surface

| Concern | File | Status | Notes |
|---|---|---|---|
| Exception signal schema | `Canary/canary/models/app/exceptions.py` (projected) | no code yet | Generic exception record: id, source_module, rule_id, rule_name, severity, signal_data, created_at |
| Domain-specific rules | `Canary/canary/services/work/domain_rules/` (projected) | no code yet | Rule catalogs per domain (inventory_rules.py, pricing_rules.py, labor_rules.py, space_rules.py, etc.) |
| Exception detector | `Canary/canary/services/work/exception_detector.py` (projected) | no code yet | Subscribes to all spine module streams; evaluates rules; fires exceptions |
| Cross-domain aggregator | `Canary/canary/services/work/cross_domain_aggregator.py` (projected) | no code yet | Correlates exceptions by subject; detects multi-domain patterns |
| Case management | `Canary/canary/services/work/case_service.py` (projected) | no code yet | Case CRUD and lifecycle (extends Q's Fox model to all domains) |
| Evidence chain | `Canary/canary/services/work/evidence_chain.py` (projected) | no code yet | Hash-chained INSERT-only evidence tracking; inherits from Q's Fox |
| MCP tools | `Canary/canary/blueprints/work_mcp.py` (projected) | no code yet | Tools: exception-search, case-crud, evidence-aggregation, cross-domain-correlation, remediation-routing, case-analytics |
| Configuration | `Canary/config.py` extensions (projected) | no code yet | Would add `EXCEPTION_AUTO_ESCALATION_RULES` (per domain), `SUBJECT_CORRELATION_WINDOW_HOURS`, `DOMAIN_VISIBILITY_POLICY` |

## Schema crosswalk

W would write to the `app` schema (configuration and master data). Anticipated tables:

| Table | Owner | Purpose |
|---|---|---|
| `exceptions` | W | All detected exceptions: id, merchant_id, source_module, rule_id, severity (info/warning/critical), signal_data (JSON), auto_escalate_flag, case_id_if_escalated |
| `exception_rules` | W | Rule catalog per domain: id, domain (Q/S/P/L/D/J/F), rule_id, rule_name, description, severity_threshold, auto_escalate_flag |
| `cases` | W | Case aggregation: id, merchant_id, case_type (multi_domain_exception), status, investigator_id, created_at (inherited Fox model) |
| `case_exceptions` | W | Junction: case_id, exception_id (one case can span multiple exceptions) |
| `case_subjects` | W | Subjects of interest per case: case_id, subject_type (customer/employee/vendor), subject_id, role_in_case |
| `case_timeline` | W | Append-only audit log: id, case_id, action_type, actor_id, timestamp, details (inherited Fox model) |
| `case_evidence` | W | INSERT-only evidence: id, case_id, evidence_type (file/screenshot/log), source_module, file_hash, chain_hash (inherited Fox model) |
| `remediation_requests` | W | Requests to modules for remediation: id, case_id, target_module, remediation_type (refund/restock/adjustment/payroll_correction), status |

W reads from (no write):

| Table | Owner | Why |
|---|---|---|
| All exception streams | Q, S, P, L, D, J, F | W subscribes to all domains' exception publishers |
| Subject identities | R, L | W looks up customer/employee records for subject context |

## SDD crosswalk

No v3 SDDs exist yet for W. Canary's current SDDs only cover v1 modules (T, Q, architecture, data-model) and projected v2 modules (C, D, F, J).

Projected SDD structure (future):
- `Canary/docs/sdds/v3/work-execution.md` — cross-domain exception detection, rule evaluation, auto-escalation, case aggregation, evidence inheritance from Fox
- Section: Ledger relationship (reconciler role, exception signal consumption)
- Section: Integration with Q (inheritance pattern), S (space exceptions), P (pricing exceptions), L (labor exceptions), D/J/F (inventory/forecast/finance exceptions)

## Where this module fits on the spine

| Axis | Cell | Notes |
|---|---|---|
| [[../projects/RetailSpine\|Retail Spine]] | v3 Capstone | W is the final ring of the spine; it reads all other modules |
| [[../projects/RetailSpine\|Retail Spine]] Ledger roles | Reconciler + Cross-domain Analyzer | W reads all spine outputs; publishes aggregated exception cases |
| Reference implementation | Q (Loss Prevention) | W generalizes Q's Chirp+Fox pattern across all domains |
| Upstream feeder | W reads from Q, S, P, L, D, J, F (all spine modules) | |
| Downstream consumer | Investigator agents; remediation workflows; store operations dashboard | |

## Open Canary-specific questions

1. **Cross-domain visibility control.** Should a Loss Prevention investigator see labor exceptions, or only LP-relevant exceptions? Should visibility be role-based or case-based? Current assumption: role-based at v3; case-escalation grants visibility.
2. **Auto-escalation per domain.** Q has 6 auto-escalating rules. How many in S (space), P (pricing), L (labor), etc.? Should thresholds be tunable per merchant? Current assumption: domain-specific thresholds at v3; per-merchant tuning at v3.1.
3. **Remediation automation.** When W detects a pricing error, should it automatically route to P for correction, or create a case for manual approval? Current assumption: manual approval (case) at v3; automated routing deferred to v3.1.
4. **Subject correlation timing.** When correlating exceptions by subject (customer/employee), what time window should W use? One hour? One day? Configurable? Current assumption: configurable; default 24 hours.
5. **Evidence inheritance from Fox.** Should W reuse Q's Fox evidence schema (hash-chained, INSERT-only, trigger-enforced), or design a new W-specific evidence model? Current assumption: inherit Fox model at v3.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-module-q-loss-prevention|Q (Loss Prevention) — reference implementation]]
- [[canary-module-s-space|S (Space)]]
- [[canary-module-p-pricing-promotion|P (Pricing & Promotion)]]
- [[canary-module-l-labor|L (Labor)]]
- [[canary-module-d-distribution|D (Distribution)]]
- [[canary-module-o-orders|J (Orders)]]
- [[canary-module-f-finance|F (Finance)]]
- [[../platform/RetailSpine|Retail Spine — Module relationships]]
- [[../platform/stock-ledger|Stock Ledger — Perpetual-Inventory Movement Ledger]]

## Sources

- `Canary-Retail-Brain/modules/E-execution.md` — canonical module spec
- `Canary-Retail-Brain/modules/Q-loss-prevention.md` — Chirp detection and Fox case management reference
- `Canary-Retail-Brain/platform/spine-13-prefix.md` — spine architecture and module dependencies

---

**Status:** Canary module E is design-phase. No code yet. Foundationally dependent on Q's Fox evidence-chain infrastructure. Ready for SDD drafting and schema design when Q's implementation is stable and v2 modules (C/D/F/J) are shipping.

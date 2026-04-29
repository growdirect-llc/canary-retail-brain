---
type: process-decomp
artifact: lint-report
pass-date: 2026-04-28
source: GRO-670
status: COMPLETE
---

# CRB Lint Report — 2026-04-28

**Pass date:** 2026-04-28 | **Executor:** ALX | **Review gate:** Jeffe

---

## Summary

| Flag | Count | Severity | Notes |
|------|-------|----------|-------|
| MISSING-L4 | 357 | High | Every L3 in corpus — universal; expected at this pass stage |
| UNSUPPORTED-INFERENCE | 3 | Medium | N (cmd/edge), L (all L3s), F.5 (tokenization) |
| PHANTOM-SUBSYSTEM | 0 | — | No phantom subsystem references found |
| OVERLAP | 4 | Low | D/J (receiving), T/F (payment parsing), Q/C (B2B rules), Q/W (case management) |
| ANALYSIS-LEAK | 0 | — | No evaluative or motive-attribution language found in decomp files |
| UNTAGGED | 0 | — | All L3/L4 entries carry provenance tags |
| CONFLICTING | 1 | Critical | ASSUMPTION-A-01 — Module A scope conflict |

**Total findings: 365 across 13 modules** (357 are the universal MISSING-L4; 8 are non-L4 findings)

---

## Findings

### MISSING-L4 — All Modules (357 findings)

Every L3 process in the corpus has L4 marked "TBD: L4 implementation detail pending." This is universal and expected — the functional decomp files were produced to L3 granularity; L4 was not in scope for the authoring pass.

**This is not a defect in the decomp files.** The MISSING-L4 flag is recorded here per SOP requirements.

**Resolution path:** Documentation-based L4 derivation pass (see CRB-GAP-LIST.md Part 2 for prioritized targets and documentation sources). User has source documentation available.

| Module | L3 Count | MISSING-L4 Count |
|--------|---------|-----------------|
| T — Transaction Pipeline | 41 | 41 |
| Q — Loss Prevention | 38 | 38 |
| R — Customer | 32 | 32 |
| N — Device | 27 | 27 |
| A — Asset Management | 12 | 12 |
| C — Commercial / B2B | 26 | 26 |
| D — Distribution | 35 | 35 |
| F — Finance | 31 | 31 |
| J — Forecast & Order | 47 | 47 |
| S — Space / Range / Display | 36 | 36 |
| P — Pricing & Promotion | 33 | 33 |
| L — Labor & Workforce | 15 | 15 |
| W — Work Execution | 14 | 14 |
| **TOTAL** | **357** | **357** |

---

### UNSUPPORTED-INFERENCE — 3 findings

An L3 is marked `INFERRED` but the supporting basis was not explicitly quoted from a source document. Per SOP, INFERRED assertions require a supporting statement traceable to a source.

| # | Module | L3 ID | L3 Process | Flag | Detail |
|---|--------|-------|-----------|------|--------|
| 1 | N | N.1.1–N.6.5 (all 27) | All Device / Store Config L3s | UNSUPPORTED-INFERENCE | The mapping of Module N to `cmd/edge` is stated as INFERRED in the process map. The basis is "edge agent" naming convention in the CanaryGO repo. No source document explicitly assigns N to `cmd/edge`. **Resolution:** Inspect `cmd/edge` source code to confirm it handles store config / device management; update tag to DOCUMENTED if confirmed. |
| 2 | F | F.5.1–F.5.4 | Tokenization / Secure Pay flows | UNSUPPORTED-INFERENCE | F.5 is mapped to `cmd/identity` (INFERRED). The basis is that tokenization concerns are typically handled in identity/auth infrastructure. No source document confirms `cmd/identity` handles tokenization for F. **Resolution:** Inspect `cmd/identity` source; confirm or reassign. |
| 3 | L | L.1.1–L.5.2 (all 15) | All Labor & Workforce L3s | UNSUPPORTED-INFERENCE | All L L3s are INFERRED from the schema crosswalk in the wiki narrative (tables: employees, shifts, time_entries, breaks, absences, productivity_metrics, payroll_exports). The wiki is the authoritative source for L, but the L3 process names were derived by the decomp executor — not quoted directly from the wiki. **Resolution:** Re-read `canary-module-l-labor-workforce.md` and annotate each L3 with its supporting wiki passage; update tags accordingly. |

---

### PHANTOM-SUBSYSTEM — 0 findings

No L3 process references a Go subsystem that cannot be found in the known `cmd/` package list. All Mapped L3s point to confirmed packages: `cmd/tsp`, `cmd/chirp`, `cmd/fox`, `cmd/alert`, `cmd/customer`, `cmd/asset`, `cmd/inventory`, `cmd/transfer`, `cmd/receiving`, `cmd/item`, `cmd/pricing`, `cmd/analytics`, `cmd/report`, `cmd/identity`, `cmd/employee`.

**Note:** `cmd/edge` carries an UNSUPPORTED-INFERENCE flag (above) but is not phantom — it is a real package whose scope is unconfirmed. It is not listed as a PHANTOM-SUBSYSTEM.

---

### OVERLAP — 4 findings

L3 processes that appear to describe the same behavior across two modules. These are boundary cases, not errors — they reflect genuine shared responsibility between subsystems. Each should be reviewed at the Jeffe gate to confirm the boundary is intentional.

| # | Module A | L3 ID (A) | Module B | L3 ID (B) | Overlap Description | Recommended Disposition |
|---|----------|-----------|----------|-----------|---------------------|-------------------------|
| 1 | D — Distribution | D.1.1–D.2.6 (inventory snapshots) | A — Asset Management | A.2.1–A.2.5 (inventory position tracking) | Both describe inventory position tracking. D tracks inventory at the snapshot/delta level for distribution purposes; A tracks inventory at the asset item type level for non-saleable classification. | Confirmed separate concerns — D is quantity-over-time; A is item-type metadata. Document boundary explicitly in both modules. |
| 2 | T — Transaction Pipeline | T.3.4 (payment-line flattening) | F — Finance | F.4.1–F.4.5 (payment flow parsing, Secure Pay) | T parses and flattens payment lines; F owns the Secure Pay / tokenization / NSPTransaction flows. | T owns the parsing step; F owns the financial instrument and tokenization layer. T.3.4 produces the input F.4 consumes. Not a true overlap — confirm the handoff contract is explicit (currently implicit). |
| 3 | Q — Loss Prevention | Q.7.1–Q.7.6 (MCP tools surface) | C — Commercial / B2B | C.4.1–C.4.5 (B2B detection rules Q-C-01 through Q-C-05) | C.4.x detection rules are documented as routing through Q's Chirp pipeline. The rules are C's domain but the execution surface is Q's. | Intentional — document explicitly that C.4.x rules are Q-pipeline extensions, not C-pipeline. Ensure C epic (GRO-652) references Q epic (GRO-651) as a dependency for C.4.x implementation. |
| 4 | Q — Loss Prevention | Q.3.1–Q.3.5 (case management via Fox) | W — Work Execution | W.3.1–W.3.3 (case CRUD extending Fox across all domains) | Q uses Fox for LP cases; W generalizes Fox across all domains. At v3, W's case management replaces Q's standalone Fox usage or wraps it. | W is the v3 generalization — Q Fox is the v2 reference implementation W extends. This is intentional inheritance, not a conflict. Confirm at W SDD authoring stage whether Q's Fox tables are consumed directly by W or W creates separate tables with the same schema. |

---

### ANALYSIS-LEAK — 0 findings

No evaluative claims, motive attributions, or opinion language was found in the process map, gap list, or pass manifest. All L3 descriptions use behavior-only language per SOP guardrails.

**Checked patterns:**
- "better than" / "worse than" comparisons → none found
- Motive attribution ("because they want to", "in order to maximize") → none found
- Quality assessments ("well-designed", "poorly structured") → none found
- Forward-looking speculation outside of INFERRED-tagged assertions → none found

---

### UNTAGGED — 0 findings

All L3 processes in the process map carry a provenance tag (DOCUMENTED, INFERRED, or GAP). No untagged entries found.

---

### CONFLICTING — 1 finding (Critical)

| # | Module | Finding | Detail | Resolution Required |
|---|--------|---------|--------|---------------------|
| 1 | A | ASSUMPTION-A-01 — Module A scope conflict | The canonical Canary spec (Bubble) describes Module A as device-anomaly detection (monitoring hardware behavior, detecting device failures, flagging anomalous device-level patterns). The functional decomp card (`canary-module-a-functional-decomposition.md`) describes Module A as item-asset-management — tracking non-saleable items via `IM_ITEM.ITEM_TYP` (tools, equipment, supplies) using `cmd/asset` and `cmd/inventory`. These are categorically different systems. Both sources are primary; neither is subordinate per SOP. | **Jeffe must resolve.** Per SOP: "If source docs contradict each other, document both versions with CONFLICTING tag; do not resolve; flag for Jeffe at review gate." This is a founder decision about the scope of Module A in the v2 build. All 12 A L3s are blocked until resolved. |

---

## Lint Disposition Table

| Flag | Count | Action Required | Owner |
|------|-------|----------------|-------|
| MISSING-L4 | 357 | Documentation-based L4 pass (see CRB-GAP-LIST.md Part 2) | ALX (next pass) |
| UNSUPPORTED-INFERENCE | 3 | Codebase inspection: `cmd/edge`, `cmd/identity`; L wiki re-annotation | ALX |
| PHANTOM-SUBSYSTEM | 0 | None | — |
| OVERLAP | 4 | Review at Jeffe gate; document boundary contracts | Jeffe |
| ANALYSIS-LEAK | 0 | None | — |
| UNTAGGED | 0 | None | — |
| CONFLICTING | 1 | ASSUMPTION-A-01 — founder decision required | Jeffe |

---

## Pass Readiness

Phase 3 is complete. The following conditions must be met before Phase 5 (Jeffe review gate):

- [x] CRB-PASS-MANIFEST.md — complete
- [x] CRB-PROCESS-MAP.md — complete (357 L3s, 212 mapped, 145 GAP)
- [x] CRB-GAP-LIST.md — complete
- [x] CRB-LINT-REPORT.md — this file
- [ ] Phase 4: Linear issue updates — PENDING (see CRB-GAP-LIST.md Part 5)
- [ ] Phase 5: Jeffe review gate — PENDING

**Blocking items for Jeffe gate:**
1. CONFLICTING: ASSUMPTION-A-01 scope decision
2. OVERLAP #4: Q Fox vs W Case management inheritance model (confirm at W SDD authoring)
3. UNSUPPORTED-INFERENCE #1: `cmd/edge` scope confirmation

---

*Pass: GRO-670 | Phase 3 complete | Next: Phase 4 — Linear issue updates*

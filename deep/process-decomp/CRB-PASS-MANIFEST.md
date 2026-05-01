---
type: process-decomp
artifact: pass-manifest
pass-date: 2026-04-28
pass-type: full-corpus
status: IN PROGRESS — Phase 1/2 complete; Phase 3–5 pending
---

# CRB Process Decomposition — Pass Manifest

**Pass date:** 2026-04-28 | **Initiated by:** GRO-670 | **Executor:** ALX | **Review gate:** Jeffe

---

## Corpus Inventory

### Functional Decomposition Files (11 of 13 modules)

| Module | File | Last Compiled | Status |
|--------|------|---------------|--------|
| T — Transaction Pipeline | `wiki/canary-module-t-functional-decomposition.md` | 2026-04-25 | CURRENT |
| Q — Loss Prevention | `wiki/canary-module-q-functional-decomposition.md` | 2026-04-25 | CURRENT |
| C — Customer | `wiki/canary-module-c-functional-decomposition.md` | 2026-04-25 | CURRENT |
| N — Device | `wiki/canary-module-n-functional-decomposition.md` | 2026-04-26 | CURRENT |
| A — Asset Management | `wiki/canary-module-a-functional-decomposition.md` | 2026-04-26 | CURRENT |
| C — Commercial / B2B | `wiki/canary-module-m-functional-decomposition.md` | 2026-04-26 | CURRENT |
| D — Distribution | `wiki/canary-module-d-functional-decomposition.md` | 2026-04-26 | CURRENT |
| F — Finance | `wiki/canary-module-f-functional-decomposition.md` | 2026-04-26 | CURRENT |
| J — Orders | `wiki/canary-module-o-functional-decomposition.md` | 2026-04-26 | CURRENT |
| S — Space / Range / Display | `wiki/canary-module-s-functional-decomposition.md` | 2026-04-26 | CURRENT |
| P — Pricing & Promotion | `wiki/canary-module-p-functional-decomposition.md` | 2026-04-26 | CURRENT |

### Narrative-Only Files (no functional decomp — 2 modules)

| Module | File | Last Compiled | Status |
|--------|------|---------------|--------|
| L — Labor | `wiki/canary-module-l-labor.md` | 2026-04-24 | NARRATIVE-ONLY — L3s derived from narrative; all tagged INFERRED |
| W — Execution | `wiki/canary-module-e-execution.md` | 2026-04-24 | NARRATIVE-ONLY — L3s derived from narrative; all tagged INFERRED |

### CanaryGO Subsystem Reference (cmd/ packages)

Source: CanaryGO repo `cmd/` directory, inspected 2026-04-28.

| cmd/ package | Primary Module Mapping |
|---|---|
| `cmd/tsp` | T — Transaction Pipeline |
| `cmd/chirp` | Q — Loss Prevention (detection engine) |
| `cmd/fox` | Q — Loss Prevention (case management) |
| `cmd/alert` | Q — Loss Prevention (alert delivery) |
| `cmd/customer` | C — Customer |
| `cmd/asset` | A — Asset Management |
| `cmd/inventory` | A / D — Asset lifecycle + Distribution snapshots |
| `cmd/transfer` | D — Distribution (XFER) |
| `cmd/receiving` | D / J — Receiving (RECVR) |
| `cmd/returns` | T — Returns (RTV partial) |
| `cmd/item` | S — Space / Range / Display (catalog) |
| `cmd/pricing` | P — Pricing & Promotion |
| `cmd/employee` | L — Labor |
| `cmd/analytics` | F — Finance (analytics) |
| `cmd/report` | F — Finance (reporting) |
| `cmd/owl` | AI analyst surface (cross-module) |
| `cmd/edge` | N — Device / Store Config (INFERRED) |
| `cmd/gateway` | API gateway (cross-module infrastructure) |
| `cmd/identity` | Auth / tenant (infrastructure) |
| `cmd/bull` | Unknown — needs codebase inspection |
| `cmd/hawk` | Unknown — needs codebase inspection |

**Unmapped modules:** C (Commercial/B2B), J forecasting/OTB, W (Execution) — no dedicated cmd/ package found. Confirmed GAPs.

---

## Pass Scope

**Pass type:** Full-corpus (all 13 modules)

**Modules in scope for this pass:** All 13

**Reason:** GRO-670 — first formal decomp pass against GRO-668 SDD v1.1 corpus update

---

## Phase Completion Tracking

| Phase | Description | Status | Date |
|-------|-------------|--------|------|
| Phase 0 | Pre-pass setup & corpus inventory | ✅ COMPLETE | 2026-04-28 |
| Phase 1 | L1→L4 decomposition (read all source files) | ✅ COMPLETE | 2026-04-28 |
| Phase 2 | L3→subsystem mapping + CRB-PROCESS-MAP.md + CRB-GAP-LIST.md | ✅ COMPLETE | 2026-04-28 |
| Phase 3 | Lint pass + CRB-LINT-REPORT.md | ✅ COMPLETE | 2026-04-28 |
| Phase 4 | Linear issue updates | ✅ COMPLETE | 2026-04-28 |
| Phase 5 | Jeffe review gate | ⏳ PENDING | — |

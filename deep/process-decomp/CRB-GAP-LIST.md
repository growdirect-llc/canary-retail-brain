---
type: process-decomp
artifact: gap-list
pass-date: 2026-04-28
source: GRO-670
status: COMPLETE
---

# CRB Gap List — 2026-04-28

**Pass date:** 2026-04-28 | **Initiated by:** GRO-670 | **Executor:** ALX | **Review gate:** Jeffe

---

## Summary

| Gap Category | Count | Notes |
|---|---|---|
| Structural subsystem GAPs (L3 processes with no cmd/ mapping) | 145 | C=26, J-forecast/OTB/PO=33, W=14, L=15, misc=57 |
| Universal L4 gap (L3s with TBD L4 activities) | 357 | Every L3 in the corpus — see Part 2 |
| Assumption gaps (unresolved, block implementation) | 7 | See Part 3 |
| Unknown cmd/ packages (purpose unconfirmed) | 2 | cmd/bull, cmd/hawk |

**L4 documentation note:** The user has source documentation (NCR/Counterpoint API specs, vendor process docs, retail ops references) that can be used to fill L4 activities once the gap list is produced. See Part 4 for the highest-priority L4 targets.

---

## Part 1 — Structural Subsystem GAPs

These are L3 processes where no CanaryGO `cmd/` package exists to receive the implementation. Each requires either a new package to be built or an explicit assignment to an existing package before the L3 can be implemented.

### 1A. Module M — Commercial / B2B (26 L3s — full module GAP)

**Root cause:** No `cmd/commercial` package exists in CanaryGO. C is derived from C (Customer) and F (Finance) data; it has no dedicated Counterpoint endpoints of its own.

**Build constraint:** C requires Module C and Module F to be stable first. It is Module 4 in the v2 ring.

| L3 ID | L3 Process | Provenance | Required Subsystem |
|-------|-----------|------------|-------------------|
| M.1.1 | B2B customer flag write | DOCUMENTED | `cmd/commercial` (new) |
| M.1.2 | Account tier assignment | DOCUMENTED | `cmd/commercial` (new) |
| M.1.3 | Account-customer link | DOCUMENTED | `cmd/commercial` (new) |
| M.1.4 | Account hierarchy (parent/child) | DOCUMENTED | `cmd/commercial` (new) |
| M.1.5 | Account status lifecycle | DOCUMENTED | `cmd/commercial` (new) |
| M.2.1 | Spending limit enforcement | DOCUMENTED | `cmd/commercial` (new) |
| M.2.2 | Credit terms configuration | DOCUMENTED | `cmd/commercial` (new) |
| M.2.3 | Invoice generation | DOCUMENTED | `cmd/commercial` (new) |
| M.2.4 | Payment terms tracking | DOCUMENTED | `cmd/commercial` (new) |
| M.2.5 | Open items aging | DOCUMENTED | `cmd/commercial` (new) |
| M.3.1 | Contract pricing agreement storage | DOCUMENTED | `cmd/commercial` (new) |
| M.3.2 | Volume tier pricing application | DOCUMENTED | `cmd/commercial` (new) |
| M.3.3 | B2B discount schedule management | DOCUMENTED | `cmd/commercial` (new) |
| M.3.4 | Contract expiry enforcement | DOCUMENTED | `cmd/commercial` (new) |
| M.4.1 | B2B detection rule Q-M-01 (volume threshold) | DOCUMENTED | `cmd/chirp` (routes through Q pipeline) |
| M.4.2 | B2B detection rule Q-M-02 (account-only tender) | DOCUMENTED | `cmd/chirp` |
| M.4.3 | B2B detection rule Q-M-03 (invoice-only payment) | DOCUMENTED | `cmd/chirp` |
| M.4.4 | B2B detection rule Q-M-04 (repeat-pattern purchasing) | DOCUMENTED | `cmd/chirp` |
| M.4.5 | B2B detection rule Q-M-05 (PO reference present) | DOCUMENTED | `cmd/chirp` |
| M.5.1 | B2B reporting — sales by account | DOCUMENTED | `cmd/commercial` (new) |
| M.5.2 | B2B reporting — invoice aging | DOCUMENTED | `cmd/commercial` (new) |
| M.5.3 | B2B reporting — contract compliance | DOCUMENTED | `cmd/commercial` (new) |
| M.5.4 | B2B reporting — volume vs tier | DOCUMENTED | `cmd/commercial` (new) |
| M.5.5 | Account statement generation | DOCUMENTED | `cmd/commercial` (new) |
| M.5.6 | AR export to accounting system | DOCUMENTED | `cmd/commercial` (new) |
| M.5.7 | Cross-module contract registry (C substrate contracts) | DOCUMENTED | `cmd/commercial` (new) |

**Note:** M.4.x (B2B detection rules Q-M-01 through Q-M-05) routes through `cmd/chirp` — these are not a new-subsystem gap, but they require explicit Q-pipeline extension work documented in Q.

---

### 1B. Module O — Orders: Forecasting / ROP / OTB / PO Engine (33 L3s — partial module GAP)

**Root cause:** `cmd/receiving` covers O.6 (Receiving) and O.7 (Returns/RTV) — 14 L3s mapped. The remaining 33 L3s covering statistical forecasting, ROP/safety-stock calculation, OTB management, and automated PO generation have no corresponding cmd/ package.

**Cross-module dependency:** J.8a (promotional demand isolation) requires P.6.3 (promotion calendar) — this is a load-bearing inter-module contract.

| L3 ID | L3 Process | Provenance | Required Subsystem |
|-------|-----------|------------|-------------------|
| O.1.1 | Historical sales series construction | DOCUMENTED | `cmd/forecast` (new) |
| O.1.2 | Seasonality curve fitting | DOCUMENTED | `cmd/forecast` (new) |
| O.1.3 | Trend detection | DOCUMENTED | `cmd/forecast` (new) |
| O.1.4 | Promotion uplift isolation | DOCUMENTED | `cmd/forecast` (new) |
| O.1.5 | Forecast confidence scoring | DOCUMENTED | `cmd/forecast` (new) |
| O.1.6 | Forecast model selection per SKU | DOCUMENTED | `cmd/forecast` (new) |
| O.1.7 | Forecast output publication | DOCUMENTED | `cmd/forecast` (new) |
| O.2.1 | Lead time calculation per vendor | DOCUMENTED | `cmd/forecast` (new) |
| O.2.2 | Safety stock calculation | DOCUMENTED | `cmd/forecast` (new) |
| O.2.3 | ROP (reorder point) calculation | DOCUMENTED | `cmd/forecast` (new) |
| O.2.4 | EOQ (economic order quantity) calculation | DOCUMENTED | `cmd/forecast` (new) |
| O.2.5 | Min/max quantity enforcement | DOCUMENTED | `cmd/forecast` (new) |
| O.2.6 | Service level target management | DOCUMENTED | `cmd/forecast` (new) |
| O.3.1 | Budget constraint load | DOCUMENTED | `cmd/forecast` (new) |
| O.3.2 | OTB calculation (planned vs actual) | DOCUMENTED | `cmd/forecast` (new) |
| O.3.3 | OTB balance tracking | DOCUMENTED | `cmd/forecast` (new) |
| O.3.4 | OTB alert on budget breach | DOCUMENTED | `cmd/forecast` (new) |
| O.3.5 | OTB reporting surface | DOCUMENTED | `cmd/forecast` (new) |
| O.4.1 | Suggested order generation | DOCUMENTED | `cmd/forecast` (new) |
| O.4.2 | Vendor grouping and MOQ enforcement | DOCUMENTED | `cmd/forecast` (new) |
| O.4.3 | Order approval workflow | DOCUMENTED | `cmd/forecast` (new) |
| O.4.4 | PO write-back to Counterpoint (`POST /Document`, DOC_TYP=PO) | DOCUMENTED | `cmd/forecast` (new) — **First write-back in Canary** |
| O.4.5 | PO status tracking | DOCUMENTED | `cmd/forecast` (new) |
| O.5.1 | Replenishment calendar management | DOCUMENTED | `cmd/forecast` (new) |
| O.5.2 | Vendor lead-time calendar | DOCUMENTED | `cmd/forecast` (new) |
| O.5.3 | Order cadence rules per vendor | DOCUMENTED | `cmd/forecast` (new) |
| O.5.4 | Blackout / holiday calendar integration | DOCUMENTED | `cmd/forecast` (new) |
| O.8.1 | Promotional demand isolation (requires P.6.3) | DOCUMENTED | `cmd/forecast` (new) |
| O.8.2 | Event demand isolation (non-promotional spikes) | DOCUMENTED | `cmd/forecast` (new) |
| O.8.3 | New-item bootstrap forecasting (no history) | DOCUMENTED | `cmd/forecast` (new) |
| O.8.4 | Discontinued-item sell-through forecasting | DOCUMENTED | `cmd/forecast` (new) |
| O.8.5 | Weather-signal demand adjustment | INFERRED | `cmd/forecast` (new) |
| O.8.6 | Cross-SKU substitution demand adjustment | INFERRED | `cmd/forecast` (new) |

**Critical path note (O.4.4):** O.4.4 is the first place Canary writes back to Counterpoint. This has significant architectural implications — the write-back pattern must be established and tested before O.4.4 can be implemented.

---

### 1C. Module E — Execution (~14 L3s — full module GAP, v3)

**Root cause:** W is a v3 capstone design. No `cmd/work` or equivalent package exists. No SDD has been written. Implementation depends on Q's Fox evidence-chain infrastructure being stable.

**Design reference:** `canary-module-e-execution.md` — all tables and services are projected (no code yet).

| L3 ID | L3 Process | Provenance | Required Subsystem |
|-------|-----------|------------|-------------------|
| E.1.1 | Exception signal schema (generic exception record) | INFERRED | `cmd/work` (new, v3) |
| E.1.2 | Domain-specific rule catalogs (inventory, pricing, labor, space) | INFERRED | `cmd/work` (new, v3) |
| E.1.3 | Exception detector — subscribes to all spine module streams | INFERRED | `cmd/work` (new, v3) |
| E.1.4 | Rule evaluation engine per domain | INFERRED | `cmd/work` (new, v3) |
| E.1.5 | Exception auto-escalation logic | INFERRED | `cmd/work` (new, v3) |
| E.2.1 | Cross-domain exception aggregator by subject | INFERRED | `cmd/work` (new, v3) |
| E.2.2 | Multi-domain pattern detection | INFERRED | `cmd/work` (new, v3) |
| E.2.3 | Subject correlation (customer/employee) with time-window | INFERRED | `cmd/work` (new, v3) |
| E.3.1 | Case CRUD and lifecycle (extends Fox across all domains) | INFERRED | `cmd/work` (new, v3) |
| E.3.2 | Evidence chain (hash-chained, INSERT-only, inherits Fox model) | INFERRED | `cmd/work` (new, v3) |
| E.3.3 | Case-exception junction management | INFERRED | `cmd/work` (new, v3) |
| E.4.1 | Remediation routing to target modules | INFERRED | `cmd/work` (new, v3) |
| E.4.2 | Remediation request status tracking | INFERRED | `cmd/work` (new, v3) |
| E.5.1 | MCP tools (exception-search, case-crud, evidence-aggregation, cross-domain-correlation, remediation-routing, case-analytics) | INFERRED | `cmd/work` (new, v3) |

**Implementation gate:** W cannot be implemented until Q's Fox evidence-chain infrastructure is stable and v2 ring modules (C, D, F, J) are shipping.

---

### 1D. Module L — Labor (~15 L3s — narrative-only, cmd/employee target)

**Root cause:** L is a v3 design with no functional decomp file. `cmd/employee` exists as a named package in CanaryGO but its current scope is unknown. All L3s are INFERRED from the schema crosswalk in the wiki narrative.

| L3 ID | L3 Process | Provenance | Required Subsystem |
|-------|-----------|------------|-------------------|
| L.1.1 | Employee record sync from Counterpoint | INFERRED | `cmd/employee` |
| L.1.2 | Role and permission mapping | INFERRED | `cmd/employee` |
| L.1.3 | Employee-store assignment | INFERRED | `cmd/employee` |
| L.2.1 | Shift schedule management | INFERRED | `cmd/employee` |
| L.2.2 | Time entry recording | INFERRED | `cmd/employee` |
| L.2.3 | Break tracking | INFERRED | `cmd/employee` |
| L.2.4 | Absence recording | INFERRED | `cmd/employee` |
| L.3.1 | Productivity metric calculation (transactions/hour, items/hour) | INFERRED | `cmd/employee` |
| L.3.2 | Productivity comparison vs store average | INFERRED | `cmd/employee` |
| L.3.3 | Productivity signal publication to Q (LP context) | INFERRED | `cmd/employee` |
| L.4.1 | Payroll export generation | INFERRED | `cmd/employee` |
| L.4.2 | Pay period reconciliation | INFERRED | `cmd/employee` |
| L.4.3 | Labor cost allocation by store/department | INFERRED | `cmd/employee` |
| L.5.1 | Labor scheduling interface | INFERRED | `cmd/employee` |
| L.5.2 | DC labor scheduling (distribution center) | INFERRED | `cmd/employee` |

**Note:** All L L3s map to `cmd/employee` (not a new-package gap), but since `cmd/employee`'s current scope hasn't been inspected against these L3s, all 15 should be validated against the existing package before filing as Mapped.

---

### 1E. Miscellaneous Structural GAPs (57 L3s — cross-module)

These are individual L3 processes across otherwise-mapped modules where the specific L3 has no clear subsystem assignment (INFERRED subsystem or boundary ambiguity).

| Module | L3 ID | L3 Process | Provenance | Gap Detail |
|--------|-------|-----------|------------|-----------|
| A | A.1.1–A.3.5 | All Asset Management L3s | DOCUMENTED | ASSUMPTION-A-01 scope conflict unresolved — subsystem is either `cmd/asset` (item-asset) or a new device-anomaly subsystem per canonical Bubble spec |
| N | N.1.1–N.6.5 | All Device L3s (27) | DOCUMENTED | `cmd/edge` mapping is INFERRED — not confirmed by codebase inspection |
| F | F.5.1–F.5.4 | Tokenization / secure-pay flows | INFERRED | Mapped to `cmd/identity` (INFERRED) — not confirmed |
| D | D.4.1–D.4.5 | Transfer-loss reconciliation | DOCUMENTED | Canary-native; no Counterpoint endpoint; `cmd/transfer` is target but D.4 reconciliation logic is a new capability gap |
| D | D.5.1–D.5.4 | Distribution reconciliation reports | DOCUMENTED | Canary-native; `cmd/transfer` target; no existing reconciliation surface |
| J | O.6.8–O.6.14 | DC-delivery and appointment flows (within cmd/receiving) | INFERRED | Receiving package scope unclear — DC delivery vs vendor direct split |
| P | P.2.1 | Promotional window inference from price variance | INFERRED | P observes `IM_ITEM` price fields — no dedicated Counterpoint promo endpoint; detection approach unconfirmed |
| cmd/bull | — | Unknown package — no module mapping identified | — | Needs codebase inspection |
| cmd/hawk | — | Unknown package — no module mapping identified | — | Needs codebase inspection |

---

## Part 2 — Universal L4 Gap

**Every L3 process in the entire CRB corpus (357 total) has L4 marked TBD.**

This is not a deficiency of the decomp pass — it reflects that the functional decomp files themselves do not yet specify implementation-level activities. L4 is the atomic step level that maps to individual Go functions, handlers, or jobs.

### L4 Gap by Module

| Module | L3 Count | L4 Status | Priority for Documentation Resolution |
|--------|---------|-----------|--------------------------------------|
| T — Transaction Pipeline | 41 | All TBD | Medium — T is the most mature module; L4s are inferable from the `cmd/tsp` codebase |
| Q — Loss Prevention | 38 | All TBD | High — detection rules are well-documented; L4s can be derived from rule catalogs |
| C — Customer | 32 | All TBD | High — Counterpoint endpoints documented; L4s are directly mappable |
| N — Device | 27 | All TBD | Medium — `PS_STR_CFG_PS` field list provides strong L4 anchors for N.1/N.2 |
| A — Asset Management | 12 | All TBD | Low (blocked on ASSUMPTION-A-01 scope resolution) |
| C — Commercial / B2B | 26 | All TBD | Medium — M.4.x L4s can be derived from Q rule catalog patterns |
| D — Distribution | 35 | All TBD | High — Counterpoint endpoints documented; `cmd/transfer` + `cmd/receiving` scope clear |
| F — Finance | 31 | All TBD | High — PayCode/TaxCode/Secure Pay endpoints documented in wiki |
| J — Orders | 47 | All TBD | High — O.6/O.7 (receiving, RTV) directly mappable; O.1–O.5 need forecasting algorithm docs |
| S — Space / Range / Display | 36 | All TBD | High — 17 Counterpoint endpoints documented; largest catalog surface |
| P — Pricing & Promotion | 33 | All TBD | High — `IM_ITEM` price fields and `PS_DOC_LIN_PRICE` documented |
| L — Labor | 15 | All TBD | Low (v3 design; no functional decomp) |
| W — Execution | 14 | All TBD | Low (v3 capstone; blocked on Q Fox stabilization) |
| **TOTAL** | **357** | **All TBD** | |

### L4 Documentation Candidates

The following L3 processes are the highest-leverage targets for documentation-based L4 resolution, because source documents (Counterpoint API spec, RapidPOS, NCR docs, vendor specs) directly describe the implementation steps:

| Priority | Module | L3 ID | L3 Process | Documentation Source |
|----------|--------|-------|-----------|---------------------|
| P1 | T | T.1.1 | Counterpoint poll-ingress via `GET /Documents` | NCR/Counterpoint REST API spec — `/Documents` endpoint parameters, pagination, watermark behavior |
| P1 | T | T.3.3–T.3.8 | Field extraction (header, payment, tax, line, audit, pricing) | NCR/Counterpoint data model — `PS_DOC`, `PS_DOC_PMT`, `PS_DOC_TAX`, `PS_DOC_LIN`, `PS_DOC_LIN_PRICE` schemas |
| P1 | R | C.1.1–C.1.5 | Customer profile read-through to Counterpoint | NCR/Counterpoint `GET /Customers`, `GET /Customer` — field mapping to Canary `customers` table |
| P1 | N | N.1.1–N.2.6 | Store config ingestion (`PS_STR_CFG_PS`, ~150 fields) | NCR/Counterpoint `GET /StoreSettings` or equivalent — field list documented in N module wiki |
| P1 | F | F.1.1–F.1.5 | PayCode caching and tax code ingestion | NCR/Counterpoint PayCode + TaxCode endpoints (cached 24h) |
| P1 | S | S.1.1–S.2.8 | Item catalog ingestion (17 Counterpoint endpoints) | NCR/Counterpoint Item endpoints — field-by-field mapping documented in S module wiki |
| P1 | D | D.1.1–D.2.6 | Inventory snapshot ingestion (7 Counterpoint endpoints) | NCR/Counterpoint Inventory endpoints — snapshot vs delta pattern |
| P1 | D | D.3.1–D.3.8 | Transfer lifecycle (`PS_DOC` DOC_TYP=XFER) | NCR/Counterpoint Document omnibus — XFER document structure and status fields |
| P1 | J | O.6.1–O.6.7 | Receiving lifecycle (`PS_DOC` DOC_TYP=RECVR) | NCR/Counterpoint Document omnibus — RECVR structure; receiving confirmation fields |
| P2 | Q | Q.2.1–Q.2.10 | Detection rule evaluation (11 rule families, 24 rules) | Q rule catalog (`canary-module-q-counterpoint-rule-catalog.md`) — each rule has explicit trigger logic |
| P2 | P | P.1.1–P.1.6 | Price observation via `IM_ITEM` price fields | NCR/Counterpoint `IM_ITEM` schema — PRIC_1 through PRIC_N fields, discount matrix |
| P2 | P | P.2.1 | Promotional window inference from `PS_DOC_LIN_PRICE` variance | NCR/Counterpoint `PS_DOC_LIN_PRICE` — promotion flag fields (ASSUMPTION-P-01 must be resolved first) |
| P2 | F | F.4.1–F.4.5 | Payment flow parsing (NSPTransaction, Secure Pay) | NCR Secure Pay API — NSPTransaction endpoint (no APIKey required; registration option) |
| P3 | J | O.4.4 | PO write-back to Counterpoint (`POST /Document`, DOC_TYP=PO) | NCR/Counterpoint `POST /Document` — first Canary write-back; field requirements for PO creation |
| P3 | J | O.1.1–O.3.5 | Forecasting, ROP, OTB calculation engine | Retail forecasting algorithm docs (not Counterpoint-specific; statistical methods) |

**Action:** When the user provides documentation for the above, map each source doc to the L3 IDs in this table and derive L4 activities from the documented API parameters, field names, and operation sequences.

---

## Part 3 — Assumption Gaps

These are unresolved assumptions in the functional decomp files that directly block L3 or L4 implementation. Each requires a decision from Jeffe or real-customer validation before the affected L3s can be marked implementation-ready.

| Assumption ID | Module | Description | Impact | Resolution Path |
|---|---|---|---|---|
| ASSUMPTION-A-01 | A | **Scope conflict** — canonical Canary spec (Bubble) describes A as device-anomaly detection; the functional decomp card describes A as item-asset-management via `IM_ITEM.ITEM_TYP`. These are different products. | All 12 A L3s are blocked until scope is resolved. If device-anomaly, a new subsystem is needed. If item-asset, `cmd/asset` proceeds as mapped. | Jeffe decision: which A definition is authoritative for v2? |
| ASSUMPTION-N-02 | N | **Drawer-close event modeling** — N.4 (LP substrate) provides drawer config thresholds to Q, but how drawer-close events are represented and routed is undocumented. | N.4 is the highest-leverage L2 for Q dependency. Mis-modeling the drawer-close event would break LP detection rules that depend on drawer state. | Real-customer data inspection — confirm how `PS_DOC` captures end-of-drawer events |
| ASSUMPTION-D-03 | D | **RECVR confirmation signal** — D's receiving confirmation flow (D.3.6) depends on T.4.7 routing RECVR documents to J, but the confirmation signal path back to D is unspecified. | D.3 transfer lifecycle and O.6 receiving lifecycle may have a circular dependency if confirmation isn't clearly modeled. | Codebase inspection — confirm how `cmd/receiving` signals completion back to inventory |
| ASSUMPTION-Q-05 | Q | **Dead-count workflow** — Q's dead-count process (cashier count before blind close) is described in the allow-list (Q.6) but the exact workflow event sequence is undocumented. | Q rule Q-DC-01 (drawer discrepancy) depends on this workflow. If the event sequence is wrong, the rule fires on false positives. | Real-customer workflow observation or NCR/Counterpoint documentation of end-of-day close sequences |
| ASSUMPTION-J-06 | J | **OTB representation** — O.3 (OTB Management) assumes OTB is tracked as a Canary-native budget construct, not read from Counterpoint. Whether Counterpoint has a budget/OTB surface is undocumented. | O.3.1–O.3.5 (5 L3s) could be fully GAP or partially mappable if Counterpoint carries budget data. | NCR/Counterpoint API inspection — check for budget or OTB-related endpoints |
| ASSUMPTION-J-08 | J | **Buyer v2 workflow** — O.4 assumes a buyer approval workflow for suggested orders before PO write-back. The approval UX model (MCP tools surface vs dedicated workflow) is unspecified. | O.4.3 (order approval) and O.4.4 (PO write-back) are blocked on this — the approval step gates the first Canary write-back. | Jeffe design decision: MCP-tool-based approval flow or dedicated workflow surface? |
| ASSUMPTION-P-01 | P | **`PS_DOC_LIN_PRICE` population** — P.2 (Promotion Detection) depends on `PS_DOC_LIN_PRICE` being populated per transaction. Whether this table is actually written by Counterpoint in garden-center deployments is unverified. | P.2.1 (promotional window inference) entirely depends on this field being populated. If it isn't, the entire promotional detection approach must change. | Real-customer data inspection — query `PS_DOC_LIN_PRICE` count against recent transactions |

---

## Part 4 — Unknown cmd/ Packages

Two cmd/ packages exist in the CanaryGO repo whose module mapping is unconfirmed.

| Package | Status | Required Action |
|---------|--------|----------------|
| `cmd/bull` | Unknown — purpose not determined | Inspect package source; determine which CRB module(s) it serves; update PASS-MANIFEST and PROCESS-MAP |
| `cmd/hawk` | Unknown — purpose not determined | Inspect package source; determine which CRB module(s) it serves; update PASS-MANIFEST and PROCESS-MAP |

If either package is the authoritative home for one of the structural GAP modules (C, J-forecast, W, or L), the gap count above should be updated accordingly.

---

## Part 5 — Linear Issue Backlog (Phase 4 Input)

The following new Linear issues should be created in Canary.GO as Backlog items with Label `Blueprint`:

| Issue Title | Module | L3 Count | Milestone | Notes |
|---|---|---|---|---|
| Gap: C — No cmd/commercial subsystem (26 L3s) | C | 26 | M4 — Module Spine | C requires R and F stable first |
| Gap: J — No forecast/ROP/OTB/PO subsystem (33 L3s) | J | 33 | M4 — Module Spine | Critical path: O.4.4 is first write-back to Counterpoint |
| Gap: W — Execution cmd/work not built (v3, 14 L3s) | W | 14 | M5 — v3 Ring | Blocked on Q Fox stabilization |
| Gap: L — Labor cmd/employee scope needs validation (15 L3s) | L | 15 | M4 — Module Spine | cmd/employee exists; scope TBD |
| Gap: A — ASSUMPTION-A-01 scope conflict blocks all A L3s | A | 12 | M3 — v2 Core | Founder decision required |
| Gap: Universal L4 — 357 L3s have no L4 activities (documentation pass needed) | ALL | 357 | M4 — Module Spine | User has documentation; see Part 2 L4 documentation candidates |
| Gap: cmd/bull and cmd/hawk — module mapping unknown | — | — | M3 — v2 Core | Inspect codebase first |

The following existing module epics (GRO-647 through GRO-659) should receive a comment linking to the corresponding decomp file and noting any CONFLICTING findings:

| Epic | Module | Comment content |
|------|--------|----------------|
| GRO-647 | T | Link to CRB-PROCESS-MAP.md T section; note all 41 L3s mapped to cmd/tsp; all L4s TBD |
| GRO-648 | R | Link to CRB-PROCESS-MAP.md R section; note all 32 L3s mapped to cmd/customer; 9 ASSUMPTIONs |
| GRO-649 | N | Link to CRB-PROCESS-MAP.md N section; note cmd/edge mapping is INFERRED; ASSUMPTION-N-02 |
| GRO-650 | A | Link to CRB-PROCESS-MAP.md A section; note ASSUMPTION-A-01 scope conflict — BLOCKED |
| GRO-651 | Q | Link to CRB-PROCESS-MAP.md Q section; note 38 L3s mapped; 12 ASSUMPTIONs; M.4.x adds 5 rules |
| GRO-652 | C | Link to CRB-PROCESS-MAP.md C section; note all 26 L3s GAP; new cmd/commercial required |
| GRO-653 | D | Link to CRB-PROCESS-MAP.md D section; note D.4/D.5 are Canary-native GAPs; ASSUMPTION-D-03 |
| GRO-654 | F | Link to CRB-PROCESS-MAP.md F section; note F.5 tokenization INFERRED to cmd/identity |
| GRO-655 | J | Link to CRB-PROCESS-MAP.md J section; note 33 L3s GAP for forecast/OTB/PO; ASSUMPTION-J-06, J-08 |
| GRO-656 | S | Link to CRB-PROCESS-MAP.md S section; note all 36 L3s mapped to cmd/item; 17 endpoints |
| GRO-657 | P | Link to CRB-PROCESS-MAP.md P section; note ASSUMPTION-P-01 critical; P.6.3→J.8a dependency |
| GRO-658 | L | Link to CRB-PROCESS-MAP.md L section; note narrative-only; all 15 L3s INFERRED |
| GRO-659 | W | Link to CRB-PROCESS-MAP.md W section; note v3 capstone; all 14 L3s GAP; blocked on Q Fox |

---

*Pass: GRO-670 | Phase 2 complete | Next: Phase 3 — CRB-LINT-REPORT.md*

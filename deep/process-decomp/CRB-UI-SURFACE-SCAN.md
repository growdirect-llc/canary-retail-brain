---
type: process-decomp
artifact: ui-surface-scan
pass-date: 2026-04-28
source: GRO-670
method: CATz Phase II — To-Be Workshop input (aspirational heat-map layer)
---

# CRB UI Surface Scan — 2026-04-28

**Governing thesis:** Before L4 activities can be specified, every L3 must be classified as either requiring a designed user surface or operating entirely as a background process. UI-surface L3s need UX decisions first; systematic L3s can be speced from API docs alone. This file is the input to the CATz Phase II To-Be Workshops — it defines the aspirational heat-map.

---

## Module Summary

| Module | Total L3s | UI-Surface | Systematic | Mixed | Notes |
|--------|---------|-----------|-----------|-------|-------|
| T — Transaction Pipeline | 41 | 1 | 40 | 0 | Almost entirely background pipe |
| Q — Loss Prevention | 38 | 12 | 26 | 0 | Alert delivery + investigator tools + allow-list admin |
| R — Customer | 32 | 14 | 18 | 0 | Investigator search + profile + risk surface |
| N — Device | 27 | 10 | 17 | 0 | Store config admin + device health |
| A — Asset Management | 12 | 1 | 11 | 0 | Blocked on ASSUMPTION-A-01 |
| C — Commercial / B2B | 26 | 16 | 5 | 5 | Account management + invoicing + contract pricing |
| D — Distribution | 35 | 8 | 22 | 5 | Transfer workflow + reconciliation dashboard |
| F — Finance | 31 | 8 | 23 | 0 | Reporting + budget mgmt surface |
| J — Forecast & Order | 47 | 16 | 25 | 6 | Receiving clerk + buyer approval + OTB dashboard |
| S — Space / Range / Display | 36 | 22 | 14 | 0 | Largest UI surface in corpus |
| P — Pricing & Promotion | 33 | 14 | 19 | 0 | Promotion calendar + markdown + clearance workflows |
| L — Labor | 15 | 7 | 8 | 0 | Scheduling + time entry + payroll export |
| W — Work Execution | 14 | 6 | 8 | 0 | Cross-domain case management + remediation |
| **TOTAL** | **357** | **135** | **200** | **22** | **38% require UI; 56% systematic; 6% mixed** |

**What "Mixed" means:** the L3 has both a background computation step and a user-facing output or input step (e.g., forecasting engine + forecast review dashboard). The L4 split within the L3 will separate them.

---

## Surface Type Index

UI-surface L3s grouped by the surface they require. This is the UX planning scaffold — each surface type maps to a distinct design conversation.

### Surface Type 1 — MCP Investigator Tools
*Agent-accessible tools surfaced to investigators, buyers, store managers via the MCP layer. These define the Canary operator experience.*

| Module | L3 ID | Tool / Surface | Notes |
|--------|-------|---------------|-------|
| T | T.7.x | Audit proof generation and verification tool | Seal record verification for investigators |
| Q | Q.7.1 | Alert search and filter tool | Investigator primary workflow |
| Q | Q.7.2 | Case create/update/close tool | Case management entry point |
| Q | Q.7.3 | Evidence attach tool | Hash-chained evidence submission |
| Q | Q.7.4 | Rule management tool | Allow-list and rule config surface |
| Q | Q.7.5 | Case analytics tool | LP performance dashboard |
| Q | Q.7.6 | Cross-case pattern tool | Multi-case correlation view |
| R | R.6.1 | Customer lookup tool | Investigator customer search |
| R | R.6.2 | Purchase history tool | Transaction history by customer |
| R | R.6.3 | Risk score surface | Customer risk indicator on investigator view |
| R | R.6.4 | Cross-module subject context | Customer presence across cases |
| S | S.7.1 | Item catalog search tool | Item lookup for investigators + buyers |
| S | S.7.2 | Category margin target tool | Margin exception context on item |
| J | J.4.3 | Order approval tool | Buyer approves/rejects suggested PO |
| W | W.5.1 | Exception search tool | Cross-domain exception query |
| W | W.5.2 | Case CRUD tool | W-level case creation (all domains) |
| W | W.5.3 | Evidence aggregation tool | Cross-domain evidence view |
| W | W.5.4 | Cross-domain correlation tool | Subject-based pattern surface |
| W | W.5.5 | Remediation routing tool | Dispatch remediation request to target module |
| W | W.5.6 | Case analytics tool | Cross-domain case performance |

---

### Surface Type 2 — Dashboard / Reporting
*Read-heavy surfaces — data visualization, trend analysis, KPI tracking. Output of systematic calculations; no user input required beyond filters.*

| Module | L3 ID | Dashboard / Report | Notes |
|--------|-------|-------------------|-------|
| Q | Q.7.5 | LP performance analytics | Case closure rates, rule fire rates, recovery |
| F | F.6.1 | Financial summary dashboard | Daily/weekly/period P&L surface |
| F | F.6.2 | Stock ledger view | Inventory value by location/category |
| F | F.6.3 | Tax liability report | Multi-authority tax summary |
| F | F.6.4 | Payment method report | Tender mix and Secure Pay summary |
| F | F.6.5 | AR aging dashboard (B2B) | Open items by account and age |
| J | J.3.5 | OTB dashboard | Budget vs actual open-to-buy by period |
| J | J.1.7 | Forecast output display | Forecast vs actual with confidence bands |
| J | J.2.6 | Service level dashboard | Fill rate by item/category |
| P | P.4.1 | Competitive pricing dashboard | Price position vs market |
| P | P.4.2 | Price change history | Price movement audit trail |
| S | S.6.1 | Range performance dashboard | Item-level sell-through, turn, GMROI |
| S | S.7.3 | Category performance view | Margin and volume by category |
| D | D.5.1 | Distribution reconciliation report | Transfer variance by lane |
| D | D.5.2 | Inventory balance report | Snapshot vs perpetual comparison |
| L | L.3.1 | Productivity dashboard | Transactions/hour by employee vs store average |
| L | L.4.2 | Payroll period summary | Labor cost by store/department/period |

---

### Surface Type 3 — Workflow / Approval
*User must take an action to advance a business process. These require defined state machines and approval UX.*

| Module | L3 ID | Workflow | User Action Required |
|--------|-------|---------|---------------------|
| J | J.4.3 | PO approval | Buyer approves or rejects suggested purchase order |
| J | J.6.1 | Receiving initiation | Receiving clerk opens receiving session |
| J | J.6.2 | Receiving line confirmation | Clerk confirms received quantities per line |
| J | J.6.3 | Receiving discrepancy resolution | Clerk flags short shipment or overage |
| J | J.6.7 | Receiving close and post | Clerk closes receiving document |
| J | J.7.1 | Return initiation (RTV) | Initiates vendor return request |
| J | J.7.2 | RTV quantity confirmation | Confirms outbound quantities |
| J | J.7.4 | RTV credit reconciliation | Matches credit memo to RTV |
| D | D.3.1 | Transfer initiation | Store or DC initiates stock transfer |
| D | D.3.5 | Transfer receipt confirmation | Receiving location confirms delivery |
| D | D.4.1 | Transfer-loss adjudication | Manager reviews transfer variance and assigns cause |
| C | C.2.3 | Invoice approval | AR approves or disputes invoice |
| C | C.2.5 | Open items aging review | AR reviews aging and initiates collection action |
| P | P.3.1 | Markdown approval | Buyer or manager approves markdown event |
| P | P.5.1 | Clearance initiation | Buyer initiates clearance sell-through |
| P | P.5.2 | Clearance depth adjustment | Buyer adjusts clearance price cadence |
| W | W.4.1 | Remediation approval | Investigator approves remediation request before routing |
| L | L.2.1 | Shift schedule approval | Manager approves published schedule |
| L | L.4.1 | Payroll export approval | Manager approves payroll period before export |

---

### Surface Type 4 — Configuration / Admin
*User configures platform behavior. These are lower-frequency but high-stakes — wrong config directly affects LP detection, pricing, or compliance.*

| Module | L3 ID | Config Surface | Stakes |
|--------|-------|---------------|--------|
| N | N.3.1 | Device registration | Register POS terminals and peripherals |
| N | N.4.1 | Drawer config | Cash drawer thresholds → feeds Q LP rules directly |
| N | N.4.2 | Discount cap config | Max discount per reason code → Q Q-DR-01 input |
| N | N.4.3 | Void reason codes | Valid void reason list → Q Q-VO-01 allow-list input |
| N | N.4.4 | Comp reason codes | Valid comp reason list → Q Q-CO-01 allow-list input |
| Q | Q.6.1 | Dead-count allow-list | Known-good dead-count cashiers per store |
| Q | Q.6.2 | Known-discount allow-list | Pre-approved discount patterns per store |
| Q | Q.6.3 | Admin-void allow-list | Authorized admin-void reason codes |
| Q | Q.6.4 | Manager-comp allow-list | Authorized comp reason codes |
| Q | Q.6.5 | Training-mode flag | Suppress LP firing during training sessions |
| C | C.3.1 | Contract pricing setup | Set contract price tiers per B2B account |
| C | C.3.4 | Contract expiry management | Configure contract renewal windows |
| C | C.1.1 | B2B customer flag | Mark customer accounts as B2B |
| C | C.1.2 | Account tier assignment | Assign volume/credit tier to B2B account |
| J | J.5.1 | Replenishment calendar config | Set order cadence windows per vendor |
| J | J.5.4 | Blackout calendar | Configure holiday/blackout order windows |
| P | P.6.1 | Promotion setup | Define promotion event, items, dates, discount |
| P | P.6.3 | Promotion calendar | Publish promotion calendar → J.8.1 dependency |
| P | P.3.2 | Markdown schedule config | Configure markdown timing and depth |
| S | S.3.1 | Mix-and-match bundle config | Define bundle rules and component eligibility |
| S | S.4.1 | Fractional unit config | Set UOM and sell-by-weight rules per item |
| S | S.2.1 | Item display attribute config | Planogram and display-location assignment |
| L | L.5.1 | Labor scheduling config | Set scheduling rules and labor targets per store |

---

### Surface Type 5 — Alert / Notification Delivery
*Platform pushes information to a user. These define notification format, routing, and acknowledgment model.*

| Module | L3 ID | Alert Surface | Delivery Mode |
|--------|-------|--------------|--------------|
| Q | Q.5.1 | LP alert delivery | Push alert to investigator on rule fire |
| Q | Q.5.2 | Alert routing config | Route by severity/type/store to correct investigator |
| Q | Q.5.3 | Alert acknowledgment | Investigator acknowledges/dismisses alert |
| Q | Q.5.4 | Escalation delivery | Escalate unacknowledged alert to manager |
| N | N.5.1 | Device health alert | Alert when POS terminal or peripheral fails |
| N | N.5.2 | Connectivity alert | Alert on store network loss |
| J | J.3.4 | OTB budget breach alert | Alert buyer when OTB is exceeded |
| S | S.5.1 | Item drift alert | Alert when item attributes shift unexpectedly |
| S | S.5.2 | Item lifecycle alert | Alert on item status transitions (new/active/clearance/discontinued) |
| W | W.1.5 | Cross-domain exception alert | Alert when W detects multi-domain pattern requiring investigation |

---

## Systematic L3 Summary

These processes have no user-facing surface requirement. L4 activities can be derived directly from API documentation and schema specs. No UX design required before implementation.

| Module | Systematic L3 IDs | Count | Primary Source for L4 |
|--------|------------------|-------|----------------------|
| T | T.1.1–T.6.5 (all except T.7 contracts) | 40 | Counterpoint `/Documents` endpoint + PS_DOC schema |
| Q | Q.1.1–Q.2.10, Q.3.1–Q.4.5 | 26 | Q rule catalog + Chirp detection engine logic |
| R | R.1.1–R.1.5, R.5.1–R.5.4 | 18 | Counterpoint `/Customers` + privacy model |
| N | N.1.1–N.2.6 | 17 | Counterpoint StoreSettings + PS_STR_CFG_PS field list |
| A | A.1.1–A.3.5 (pending ASSUMPTION-A-01) | 11 | IM_ITEM.ITEM_TYP field spec |
| C | C.4.1–C.4.5 (Q pipeline extensions) | 5 | Q rule catalog (Q-C-01 through Q-C-05) |
| D | D.1.1–D.2.6 (inventory snapshots) | 22 | Counterpoint Inventory endpoints |
| F | F.1.1–F.5.4 | 23 | Counterpoint PayCode/TaxCode + Secure Pay NSPTransaction |
| J | J.1.1–J.2.6, J.8.2–J.8.6 | 25 | Statistical forecasting algorithm docs + Counterpoint receiving |
| S | S.1.1–S.1.8 (ingestion only) | 14 | Counterpoint Item endpoints (17 endpoints) |
| P | P.1.1–P.2.1, P.4.3–P.4.5 | 19 | IM_ITEM price fields + PS_DOC_LIN_PRICE |
| L | L.1.1–L.1.3, L.3.1–L.3.3 | 8 | Counterpoint employee sync + productivity calc |
| W | W.1.1–W.2.3 | 8 | Exception schema + rule evaluation logic |

---

## Mixed L3s — Require Both Systematic Spec and UI Design

These L3s have a background computation step AND a user-facing output. The L4 split within each L3 will separate the systematic activities (spec from docs) from the UI activities (requires design).

| Module | L3 ID | Process | Systematic Piece | UI Piece |
|--------|-------|---------|-----------------|---------|
| J | J.1.1–J.1.7 | Demand forecasting | Statistical calculation | Forecast review surface (J.1.7) |
| J | J.3.1–J.3.3 | OTB calculation | Budget vs actual calc | OTB balance display |
| J | J.4.1–J.4.2 | Suggested order generation | Order quantity calc | Suggested order review list |
| J | J.4.4–J.4.5 | PO write-back + status | POST to Counterpoint | PO status display |
| D | D.3.2–D.3.4 | Transfer in-transit tracking | Sync from Counterpoint | In-transit status display |
| D | D.4.2–D.4.3 | Loss reconciliation calc | Variance calculation | Variance review screen |
| C | C.5.1–C.5.4 | B2B reporting | Metric aggregation | Report display surface |
| P | P.3.3–P.3.5 | Markdown monitoring | Price change detection | Markdown effectiveness display |
| L | L.3.2–L.3.3 | Productivity scoring | Score calculation | Score display on investigator surface |

---

## CATz To-Be Workshop Input

This scan maps directly to the CATz Phase II workstream structure:

| CATz Artifact | Feeds From This Scan | Output |
|---|---|---|
| To-Be Workshop decks (one per domain) | Surface Type 3 (workflows) + Surface Type 4 (config) | Per-domain user journey maps |
| Aspirational heat-map | All Surface Type tags | Full-coverage UI vs systematic grid |
| Development effort estimate | UI-surface count (135) vs systematic (200) | Design days + build-test days split |
| IT Architecture Options — per-option slide skeleton | Systematic L3 count → determines backend build scope | Backend architecture spec |
| RFP Package attachments | UI-surface L3s by module | Vendor capability coverage requirements |

**Immediate next step (CATz Phase II, Workstream 1):** Run one To-Be Workshop deck per domain using the Surface Type 3 (Workflow) and Surface Type 4 (Config) L3s as the process inventory. Each workflow L3 becomes a swim-lane step; each config L3 becomes an admin screen. The systematic L3s are excluded from the workshop and handed directly to implementation spec.

**L4 fill sequencing from here:**
1. **Week 1:** Spec systematic L4s for T, R, S, D from Counterpoint API docs (no UX needed — P1 in GRO-675)
2. **Week 2:** Run To-Be workshops for Q (LP investigator), J (receiving + buyer), N (store config) — highest-leverage UI surfaces
3. **Week 3+:** Spec UI L4s from To-Be workshop outputs; continue systematic fills for F, P, N

---

*Pass: GRO-670 | UI Surface Scan complete | CATz Phase II To-Be Workshop input ready*

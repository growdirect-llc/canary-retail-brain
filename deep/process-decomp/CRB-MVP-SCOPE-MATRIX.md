---
type: process-decomp
artifact: mvp-scope-matrix
pass-date: 2026-04-28
source: GRO-670
method: CATz Phase II — product scope / build vs. integrate framework
version: 2 — recast from Bucket 1/2/3 to A/B/C
---

# CRB MVP Scope Matrix — 2026-04-28 (v2)

**Governing thesis:** Canary never owns the transaction of record. The retailer already has systems that create items, process transactions, generate invoices, manage payroll, and plan orders. Canary's job is to read all of that, add intelligence the retailer can't get anywhere else, alert in real time, and expose clean APIs so every other tool can plug in. The L3 processes split along three lines:

| Category | What It Is | Build Posture |
|---|---|---|
| **A — Canary owns** | LP intelligence, evidentiary engine, real-time alerting, store ops analytics. No SMB equivalent exists. | Build everything. This is the product. |
| **B — Interface layer on Counterpoint** | Read-through to NCR/Counterpoint. Retailer creates the data there; Canary reads, canonicalizes, and exposes it. | Build fully — this is the API footprint. Nothing in A works without it. |
| **C — Retailer has another solution** | Planning, forecasting, full financial management, labor/payroll, promotion lifecycle, B2B AR. Canary provides data exports and analytics surfaces, not workflow replacement. | Build APIs and analytics surfaces only. Don't own the workflow. |

---

## Category A — Canary Owns (~120 L3s)

The proprietary intelligence + evidentiary layer. Loss prevention analytics, real-time alerting, store ops visibility, hash-chained evidence. Nothing in the SMB market delivers this for specialty retail. This is what Canary is.

### Q — Loss Prevention (all 38 L3s) ← THE CORE PRODUCT

| L2 | L3 IDs | What It Is |
|----|--------|-----------|
| Q.1 Substrate ingestion | Q.1.1–Q.1.5 | Reads the transaction substrate Q's rules fire against |
| Q.2 Detection rules | Q.2.1–Q.2.10 | 23 rules, 10 families, garden-center tuned. The LP intelligence engine |
| Q.3 Case management (Fox) | Q.3.1–Q.3.5 | Hash-chained INSERT-only evidence. The evidentiary backbone |
| Q.4 Alert triggers | Q.4.1–Q.4.4 | Detection → delivery bridge |
| Q.5 Alert delivery | Q.5.1–Q.5.4 | Real-time alert to investigator |
| Q.6 Allow-list management | Q.6.1–Q.6.5 | Garden center tuning — false-positive control |
| Q.7 MCP investigator tools | Q.7.1–Q.7.6 | The surface an investigator actually works in |

### Canary-Distinctive L3s in Other Modules (~82 L3s)

These exist specifically because Canary is the intelligence layer — not because another system would do them.

**Evidentiary layer (Module T)**
| L3 ID | Process | Why Category A |
|-------|---------|---------------|
| T.2.3 | Hash-before-parse | Patent-critical ordering constraint. Canary's evidentiary integrity depends on this |
| T.2.4–T.2.6 | Seal record write, fanout routing, mutation-lock | Tamper-evidence layer applied at the transaction grain |
| T.4.1–T.4.9 | Canonical event publication (SALE, RETURN, VOID, PAYMENT, TAX, AUDIT, routing, customer upsert) | Canary's canonical data model — the intelligence substrate above the raw Counterpoint data |
| T.5.1–T.5.5 | Merkle anchoring (tree, root hash, leaf linkage, audit proof, verification) | The L2 blockchain anchoring. One of the three platform accountability rails |
| T.7.1–T.7.12 | Substrate contracts | Canary's internal API contract surface — what T owes every downstream module |

**LP substrate configuration (Module N)**
| L3 ID | Process | Why Category A |
|-------|---------|---------------|
| N.4.1 | Drawer config thresholds | Feeds Q Q-DC-01 (drawer discrepancy). LP fires off this baseline |
| N.4.2 | Discount cap config | Feeds Q Q-DR-01 (abnormal discount). The "what's too much" line |
| N.4.3 | Void reason codes | Feeds Q Q-VO-01 allow-list |
| N.4.4 | Comp reason codes | Feeds Q Q-CO-01 allow-list |
| N.5.1–N.5.2 | Device health + connectivity alerts | Canary alerting layer on store infrastructure |

**Customer intelligence surface (Module R)**
| L3 ID | Process | Why Category A |
|-------|---------|---------------|
| R.2.1–R.2.4 | Customer risk scoring and behavioral pattern detection | Canary intelligence — no Counterpoint equivalent |
| R.6.1–R.6.4 | Investigator surface (lookup, history, risk score, cross-module context) | How the investigator acts on a Q alert. Canary's operator UX |

**Analytics intelligence (Modules D, F, S, P, W)**
| Module | L3 IDs | Process | Why Category A |
|--------|--------|---------|---------------|
| D | D.4.1–D.4.5 | Transfer-loss reconciliation + adjudication | Canary detects shrink in transit. No Counterpoint equivalent |
| D | D.5.1–D.5.4 | Distribution reconciliation analytics | Canary analytics surface on inventory variance |
| F | F.2.1–F.2.4 | Financial metrics connected to LP outcomes | Canary's "here's what shrink cost you" surface |
| S | S.5.1–S.5.3 | Item lifecycle / drift detection and alerts | Canary detects when item attributes shift unexpectedly |
| S | S.7.1–S.7.3 | Category analytics and margin target surface | S.7.2 (margin targets) feeds Q-ME-01 margin exception detection |
| P | P.2.1–P.2.3 | Promotional window inference from price variance | Canary infers promotions because Counterpoint has no promo API. Prevents Q false positives |
| C | C.4.1–C.4.5 | B2B detection rules Q-C-01 through Q-C-05 | Routes through Q's Chirp pipeline. B2B LP intelligence |
| L | L.3.3 | Employee productivity signal to Q (LP context) | Connects labor data to LP investigation. Canary intelligence |
| W | W.1.1–W.5.6 | Cross-domain exception detection, aggregation, case management, remediation, MCP tools | The v3 capstone. W is Canary's immune system — generalizes Q across all domains |

---

## Category B — Interface Layer on Counterpoint (~120 L3s)

Canary reads this data from NCR Counterpoint, canonicalizes it, and makes it available to Category A. The retailer creates and owns this data in Counterpoint. Canary never replaces these workflows — it reads their output.

Building this layer fully is the API footprint strategy: any future integration, partner connector, or analytics module plugs into clean canonical data without touching Counterpoint directly.

| Module | L3 IDs | What Canary Reads | Counterpoint Owns |
|--------|--------|------------------|------------------|
| T.1 | T.1.1–T.1.9 | Transaction ingestion pipeline (`GET /Documents`, watermarks, auth, pagination, retry) | Every transaction, return, void, transfer, receipt |
| T.3 | T.3.1–T.3.8 | DOC_TYP-keyed parsing + field extraction (header, payment, tax, line items, audit log, pricing) | PS_DOC and all child tables |
| T.6 | T.6.1–T.6.5 | Historical backfill and replay from sealed ledger | Historical transaction archive |
| T.2 (partial) | T.2.1, T.2.2 | Receipt stamp + dedup / idempotency | — (infrastructure) |
| R.1 | R.1.1–R.1.5 | Customer profile sync (read-through, no PII at rest) | Customer master |
| R.3–R.5 | R.3.1–R.5.4 | Customer search, purchase history, privacy/consent | Customer transaction and AR data |
| N.1–N.3 | N.1.1–N.3.5 | Store config ingestion (~150 fields from PS_STR_CFG_PS), device registration | All store configuration parameters |
| S.1–S.4 | S.1.1–S.4.5 | Item catalog (17 endpoints), display config, mix-and-match, fractional units | Item master, pricing, UOM, bundle rules |
| D.1–D.2 | D.1.1–D.2.6 | Inventory snapshot (7 endpoints), delta processing | Inventory position across locations |
| D.3 | D.3.1–D.3.8 | Transfer lifecycle (XFER documents via T.4.7 routing) | Transfer creation, in-transit, receipt confirmation |
| F.1 | F.1.1–F.1.5 | PayCode cache (24h), TaxCode cache, Secure Pay registration | Payment and tax reference data |
| F.4–F.5 | F.4.1–F.5.4 | Payment flow parsing (NSPTransaction, Secure Pay), tokenization | Payment instrument and Secure Pay infrastructure |
| J.6–J.7 | J.6.1–J.6.14, J.7.1–J.7.7 | Receiving lifecycle (RECVR documents), RTV lifecycle | Inbound goods receipt, vendor returns |
| P.1 | P.1.1–P.1.6 | Price observation via IM_ITEM price fields (PRIC_1–N, discount matrix) | All item pricing |

**The API footprint argument:** Build all of Category B fully, not just the slices Category A immediately needs. A Counterpoint VAR, an ERP integration, a BI tool, a future Canary module — all of them plug in at the B layer. Canary becomes the cleanest Counterpoint data surface in the market. That's a durable competitive moat that strengthens the NCR partnership.

---

## Category C — Retailer Has Another Solution (~117 L3s)

The retailer already manages these functions in Counterpoint, QuickBooks, spreadsheets, ADP, Homebase, or a dedicated planning tool. Canary's role here is **data provider and analytics surface, not workflow owner.** Build APIs and read-only analytics. Don't build the workflow.

| Module / L2 | L3 Count | Retailer's Existing Solution | Canary's Correct Role |
|---|---|---|---|
| J.1–J.5, J.8 — Forecasting, ROP, OTB, PO engine | 33 | Buyer spreadsheets, dedicated planning tool (JDA/Blue Yonder at scale), or Counterpoint's basic replenishment | Export clean historical data and inventory position via API. Let planning tools consume it. PO *suggestions* are an analytics surface, not a workflow Canary owns |
| F.3, F.6 — Stock ledger, financial reporting | 8 | Counterpoint stock ledger + QuickBooks/Sage | Canary provides LP-connected financial analytics (shrink cost, recovery rate). General financial reporting stays in accounting software |
| P.3–P.6 — Markdown management, clearance, competitive pricing, promotion calendar | 20 | Counterpoint manages markdown and promotion setup. Dedicated markdown optimization tools exist at scale | Canary reads promotion events from Counterpoint for LP accuracy (P.2.1). Canary can expose promotion calendar data via API. Don't build the promotion creation workflow |
| S.6 — Range planning | 4 | Buyer spreadsheets, dedicated range planning tools | Canary provides sell-through, turn, and GMROI analytics for range decisions. The decision stays with the buyer |
| C.1–C.3, C.5 — B2B account management, credit/invoicing, contract pricing, AR reporting | 21 | Counterpoint customer accounts + QuickBooks AR + accounting software | Canary detects B2B LP patterns (Category A, via Q). Account and AR management stays in existing systems. Canary can expose B2B analytics via API |
| L.1–L.2, L.4–L.5 — Employee sync, time/attendance, payroll, scheduling | 14 | ADP, Homebase, Deputy, Gusto, or whatever the retailer uses | Canary reads employee data for LP context (L.3.3 → Category A). Scheduling and payroll stay in labor systems. Canary exports productivity analytics via API |
| J.4 — PO generation and write-back | 5 | Counterpoint manages PO documents. Buyer executes in Counterpoint | J.4.1–J.4.3: Canary can surface suggested orders as an analytics output. J.4.4 (write-back to Counterpoint): build only if buyer workflow clearly benefits; default posture is export-to-buyer's-workflow, not Canary-owns-the-PO |

### The Write-Back Question

Canary reads everything. The only identified write-back in the corpus is J.4.4 (`POST /Document`, DOC_TYP=PO). The correct decision framework:

> *Does the retailer benefit more from Canary pushing the PO into Counterpoint automatically, or from Canary exporting the PO suggestion to whatever workflow the buyer already uses?*

At the SMB ICP ($10M–$50M), the answer is likely **export**. The buyer has a process. Canary surfaces the intelligence; the buyer executes in Counterpoint. The write-back pattern matters more as retailers grow and want automation. Build the export API first; the write-back is a v2+ decision.

---

## Module-Level Summary

| Module | Category A | Category B | Category C | Primary Role |
|--------|-----------|-----------|-----------|-------------|
| T — Transaction Pipeline | ~28 (Merkle, canonical events, seal) | ~23 (ingestion, parsing, replay) | 0 | Intelligence substrate + evidentiary layer |
| Q — Loss Prevention | 38 (all) | 0 | 0 | THE CORE PRODUCT |
| R — Customer | ~8 (risk scoring, investigator surface) | ~24 (sync, search, history, privacy) | 0 | Read-through + LP investigator context |
| N — Device | ~7 (LP substrate config, health alerts) | ~20 (config ingestion, device mgmt) | 0 | Store config read + LP threshold surface |
| A — Asset Management | ~2 (drift analytics) | ~10 (item-type read-through) | 0 | BLOCKED — ASSUMPTION-A-01 |
| C — Commercial/B2B | ~5 (B2B detection rules via Q) | 0 | ~21 (account mgmt, AR, contracts) | B2B LP intelligence only; AR in existing systems |
| D — Distribution | ~8 (transfer-loss recs, analytics) | ~27 (snapshot, transfer read) | 0 | Inventory intelligence + transfer shrink detection |
| F — Finance | ~4 (LP-connected analytics) | ~19 (PayCode, payment, tokenization) | ~8 (stock ledger, general reporting) | LP-impact finance analytics; not GL replacement |
| J — Forecast & Order | 0 | ~14 (receiving, RTV read-through) | ~33 (forecasting, OTB, PO engine) | Receiving data + export API for planning tools |
| S — Space/Range/Display | ~7 (drift, category analytics) | ~25 (item catalog, display, bundles) | ~4 (range planning) | Item intelligence + category LP context |
| P — Pricing & Promotion | ~3 (promo inference, LP accuracy) | ~10 (price observation) | ~20 (markdown, clearance, promo mgmt) | Promo intelligence for LP accuracy; not pricing tool |
| L — Labor | ~1 (productivity → Q signal) | 0 | ~14 (scheduling, payroll, time entry) | LP labor context only; payroll stays in labor systems |
| W — Work Execution | ~14 (all — v3 capstone) | 0 | 0 | Cross-domain LP immune system |
| **TOTAL** | **~125** | **~162** | **~120** | |

*Note: totals are approximate; a small number of L3s straddle boundaries and are counted in the dominant category.*

---

## Build Roadmap Implied by This Framework

**Launch (v1):** All Category A + all Category B. ~285 L3s. This is Canary: LP intelligence fully operational, complete Counterpoint API footprint, real-time alerting, evidentiary anchoring, clean canonical data available for every future integration.

**v1.1 — Category C analytics surfaces (not workflows):** Export APIs for planning tools (J data), B2B analytics (C data), labor context (L data). The retailer's planning tool, accounting software, and labor system can pull from Canary. Canary becomes the data hub.

**v2+ — Selective workflow absorption:** Based on customer demand, absorb specific Category C workflows where Canary can demonstrably beat the existing solution. The candidate list: J.4 PO approval workflow (once receiving volume justifies it), S.6 range analytics (if no planning tool is connected), P.6 promotion calendar (if it directly improves Q accuracy).

---

*Pass: GRO-670 | v2 of MVP scope matrix — A/B/C framework replacing Bucket 1/2/3 | Source: CRB-PROCESS-MAP.md + CRB-UI-SURFACE-SCAN.md*

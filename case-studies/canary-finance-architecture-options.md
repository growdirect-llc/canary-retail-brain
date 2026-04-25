---
type: case-study
classification: internal-decision-record
date: 2026-04-24
status: completed-design
related-linear: GRO-526
related-sdd: SDD-morrisons-it-architecture-options-v2.md
methodology: IBM BCS IT Architecture Options (Morrisons pattern)
author: Geoffrey C. Lyle
---

# Case Study: Canary v2.F Finance — Architecture Options Evaluation

## Executive Summary

Canary is at a fork in the road for v2.F (Finance). The Morrisons option-evaluation frame reveals a **clear winner:** Option C (Integrated hybrid). This decision prioritizes merchant adoption ease and time-to-value over native GL ownership, couples Canary's perpetual-movement layer to the merchant's existing accounting package via OAuth, and defers the full RIM (Real/Integrated Merchandise accounting) complexity to v3.

**Recommendation:** Option C. Phase 1: Cost Method only + invoice 3-way match. Phase 2 (v3): RIM via the same OAuth bridge.

**Install state — staged-migration framing.** Per [[../platform/perpetual-vs-period-boundary|Perpetual-vs-Period Boundary]], Option C lands the merchant at `cutover_status: parallel-observer` for v2.F at install. Canary's perpetual movement layer ingests every PO + GRN + invoice + cost event in real time and produces a parallel ledger position. The merchant's QuickBooks / Xero / Wave keeps doing the period summary unchanged. Reconciliation surfaces highlight gaps with reason codes; merchant adjudicates each. As confidence builds (typically 3–6 months of clean reconciliations), the merchant can advance to `partial-cutover` (Canary becomes the read source for some queries the GL handles today) or eventually `full-cutover` (Canary's perpetual ledger is system of record; the merchant's GL becomes a downstream subscriber). All cutovers are merchant-initiated, reversible, and per-module.

The Phase 1 value of Option C is **non-zero-friction adoption**: the merchant connects QuickBooks via OAuth, Canary starts producing the parallel ledger and diagnostic value immediately, and nothing breaks. The Phase 3 value is **the perpetual ledger as system of record** — the moat — but it is opt-in, not forced.

---

## Section 2: Business Targets — v2.F "Optimisation" Programme

Canary's SMB merchant customers demand finance features at feature-parity with QuickBooks Online, Xero, Wave, and FreshBooks — but integrated into loss-prevention analytics. The programme targets (by Q4 2026):

- **Merchant adoption:** 40% of new Canary merchants activate finance module within 30 days of onboarding (vs. current: not measured)
- **Cost reduction:** Reduce merchant's inventory-write-off variance by 8–12% YoY through better COGS visibility
- **Time-to-value:** First invoice match + suggested GL posting within 7 days of supplier invoice receipt
- **Operational headcount:** Merchant does not need to hire accounting staff to use the finance module (merchant's accountant remains the decision-maker, Canary automates the data flow)

---

## Section 3: Business Requirements — Sell/Plan/Move/Buy Frame

Mapping Canary's v2.F scope to the standard frame:

| Frame | Canary Applicability | Relevant Process Areas |
|-------|-----|---|
| **Sell** | Not in scope for v2.F | — |
| **Plan** | Indirect; informs markdown analysis | Category Planning, Promotions Planning (downstream) |
| **Move** | **CORE** | Supply Chain Planning (forecast vs. actual), Manage Replenishment (inbound receipt), Physical Logistics (GRN) |
| **Buy** | **CORE** | Product Sourcing & Buying (PO matching, invoice receipt, supplier performance) |
| **Reporting/Control** | **CORE** | GL posting, COGS accounting, cost allocation, period close |

**Canary's v2.F role:** Merchant's **perpetual-movement** layer. Tracks purchase order → goods receipt → invoice receipt → 3-way match → cost allocation → COGS ledger entry. The merchant's GL package (QBO, Xero, etc.) owns the P&L, balance sheet, and statutory reporting.

---

## Section 4: Implications for Legacy Systems

Canary's current application architecture (as of 2026-04-24):

| Component | Current State | v2.F Implication | Heat-Map (4-color) |
|---|---|---|---|
| **Perpetual Inventory** | app/sales schemas; GRN + cost allocations in place | Foundation; extend with RIM tables | 🟢 Green (good fit) |
| **Purchase Order module** | Not implemented; PO data flows via Square Catalog | Needs light PO tracking schema | 🟡 Yellow (small changes) |
| **Supplier Invoice** | Not implemented | Needs supplier_invoices + gl_distributions schema | 🔴 Red (build new) |
| **3-Way Match** | Not implemented | Needs match rules + exception workflows | 🔴 Red (build new) |
| **GL Posting** | Not implemented; no accounting DB | Needs decision: native GL vs. OAuth bridge to merchant GL | 🟡 or 🔴 (depends on option) |
| **Cost Allocation** | Partial (allocation_rules in app schema) | Needs Cost Method selector + RIM support (deferred to v3) | 🟡 Yellow (significant enhancements) |
| **Period Close** | Not implemented | Needs accrual logic, variance analysis, close workflows | 🔴 Red (build new) |

**Two views (org and process):**

### Org-Structure View (Canary Modules)
```
Canary Finance v2.F Readiness
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Perpetual Inventory   🟢 (extend)
PO Tracking           🟡 (light build)
Supplier Invoicing    🔴 (build)
3-Way Match           🔴 (build)
GL Integration        ? (depends on option)
Cost Allocation       🟡 (enhance)
Period Close          🔴 (build)
```

### Process View (Buy / Move / Reporting)
```
Buy Process:
  PO Creation & Mgmt       🟡 (light)
  Supplier Performance     🟡 (reports only)
  Invoice Matching         🔴 (build)

Move Process:
  GRN / Receipt            🟢 (exist)
  Allocation to SKU        🟡 (enhance)

Reporting/Control:
  GL Posting               ? (decide)
  Period Close             🔴 (build)
  Cost Analysis            🟡 (enhance)
```

---

## Section 5–7: Three Option Evaluations

### OPTION A: Legacy Enhancement (Native GL)

**Title:** Canary Owns the Ledger — Complete Finance System Native in Canary

**One-liner:** Extend Canary's native app schema to full GL ownership. Canary becomes the merchant's accounting system of record for all inventory-related finance.

#### Slide 1: Title
"Option A — Legacy Enhancement: Extend Canary's native finance layer; Canary owns the merchant's inventory GL."

#### Slide 2: Architecture vs. Optimisation (Org View)
```
Perpetual Inventory   🟢 (leverage)
PO Tracking           🟡 (light build)
Supplier Invoicing    🔴 (build)
3-Way Match           🔴 (build)
GL Posting (native)   🔴 (build full GL subsystem)
Cost Allocation       🔴 (build RIM + Cost Method selector)
Period Close          🔴 (build accrual, close workflows)
```
**Heat-map summary:** 1 green, 1 yellow, 5 red. **Poor fit for Optimisation targets.** Requires building a full accounting system while merchants expect integration to their existing GL.

#### Slide 3: Architecture vs. Optimisation (Process View)
```
Buy (PO → Invoice Match → COGS posting)
  PO Creation           🟡
  Invoice Match         🔴
  GL Posting            🔴
  Supplier Perf         🟡

Move (Inbound → GRN → Allocation)
  GRN / Receipt         🟢
  Allocation            🔴 (RIM not in scope yet)

Reporting/Control
  GL Posting            🔴 (Canary owns GL)
  Cost Analysis         🟡
  Period Close          🔴
```

#### Slide 4: Development Effort Estimate

| Component | Design | Build/Test | Dev Total | Roll-out | Total |
|---|---|---|---|---|---|
| PO module (light) | 80 | 200 | 280 | 100 | 380 |
| Supplier invoicing + matching | 300 | 600 | 900 | 150 | 1,050 |
| GL subsystem (accounts, posting, subledgers) | 400 | 800 | 1,200 | 200 | 1,400 |
| Cost Method + RIM prep (defer full RIM to v3) | 200 | 400 | 600 | 0 | 600 |
| Period close workflows (accrual, reversals, variance) | 200 | 300 | 500 | 100 | 600 |
| Reporting + dashboards | 150 | 300 | 450 | 50 | 500 |
| Integration: Canary GL ↔ Square sync | 100 | 200 | 300 | 50 | 350 |
| Testing (integration + merchant UAT) | 0 | 500 | 500 | 200 | 700 |
| **Total Man Days** | **1,430** | **3,300** | **4,730** | **850** | **5,580** |
| **Total Man Years** | | | | | **27.9** |

**Estimation basis:** 3-engineer build team; 6-month calendar window; assumes no vendor integration (GL is fully native). Roll-out includes merchant training + tax-year close certification.

#### Slide 5: Architecture vs. Aspirational (Org View)
```
Option A maps to a multi-system merchant GL world:
  ✗ Canary GL becomes the source of truth, but merchants increasingly expect cloud GL
  ✗ If merchant switches GL vendor (QBO → Xero), Canary's GL data strands
  ✗ Inhibits future integrations with payroll, banking, forecasting (all GL-coupled)
  
Heat-map: 0 green, 1 yellow, 6 red.
Verdict: Paint merchant into a corner. Option A fails Aspirational.
```

#### Slide 6: Architecture vs. Aspirational (Process View)
**Same finding.** Centralizing GL in Canary prevents the merchant from evolving toward a modern API-coupled accounting stack (QBO + Stripe + Bill.com + ADP payroll).

#### Slide 7: Advantages / Disadvantages + Target Architecture

**Advantages:**
1. Complete ownership of COGS movement; no third-party sync failures
2. Single source of truth for perpetual cost and GL reconciliation
3. Can optimize GL design for retail cost accounting (multi-method support)
4. Reduced merchant friction around GL security credentials (Canary owns the data)

**Disadvantages:**
1. **28 engineer-years to build a full accounting subsystem.** Diverts from Canary's core (loss prevention).
2. **Merchant adoption friction.** Merchants don't trust a "side system" for their GL. They want their books in QuickBooks/Xero.
3. **Tax reporting risk.** Canary becomes liable for GL correctness; merchant's accountant will not certify a Canary GL for tax filing.
4. **Vendor lock-in.** If merchant outgrows Canary, their historical GL data is stranded.
5. **Aspirational dead-end.** If merchant wants to integrate payroll, banking, or forecasting, they still need a GL export; Canary GL doesn't solve that.
6. **Maintenance burden.** Canary becomes responsible for GL audit, chart-of-accounts management, multi-currency support, regulatory changes (tax, SEC if public clients).

**Target Architecture Diagram:**
```
┌─────────────────────────────────────┐
│  Merchant (SMB)                     │
│  ┌───────────────────────────────┐  │
│  │ Square POS │ External Systems │  │
│  └──────────┬────────────────────┘  │
│             │                       │
│     ┌───────▼────────────────────┐  │
│     │ Canary All-in-One          │  │
│     │ ┌─────────────────────────┐│  │
│     │ │ Loss Prevention (Chirp)  ││  │
│     │ │ + Inventory (GRN)        ││  │
│     │ │ + PO Tracking (new)      ││  │
│     │ │ + Invoice Match (new)    ││  │
│     │ │ + GL Subsystem (new)  ⚠ ││  │
│     │ │ + Period Close (new)  ⚠ ││  │
│     │ └─────────────────────────┘│  │
│     └─────────────────────────────┘  │
│                                      │
│  Legend: ⚠ = high-risk new build    │
└─────────────────────────────────────┘
```

---

### OPTION B: Best-of-Breed Package (Merchant GL is Authority)

**Title:** Merchant's GL is the Source of Truth — Canary Pushes Journal Entries to Merchant's Existing Package

**One-liner:** Canary handles perpetual inventory + invoice matching; GL posting is published to the merchant's existing system (QBO, Xero, Wave, FreshBooks) via API.

#### Slide 1: Title
"Option B — Best-of-Breed: Canary handles perpetual movement; GL posting flows to merchant's GL via OAuth/API."

#### Slide 2: Architecture vs. Optimisation (Org View)
```
Perpetual Inventory   🟢 (leverage)
PO Tracking           🟡 (light build)
Supplier Invoicing    🟡 (build, integrated to merchant GL)
3-Way Match           🟡 (build, exception-driven)
GL Posting (merchant GL is authority) 🟡 (build API integration)
Cost Allocation       🟡 (build, limited to Cost Method v1)
Period Close          🟡 (build, report-only in Canary; GL owns close)
```
**Heat-map summary:** 1 green, 5 yellow, 1 red (PO not needed; defer). **Good fit for Optimisation targets.** Reduces risk; leverages merchant's existing GL investment.

#### Slide 3: Architecture vs. Optimisation (Process View)
```
Buy (PO → Invoice → COGS posting)
  PO Creation           🟡 (optional; direct invoice receipt if supplier direct-bill)
  Invoice Match         🟡
  GL Posting via API    🟡
  Supplier Perf         🟢

Move
  GRN / Receipt         🟢
  Allocation to Cost    🟡

Reporting/Control
  GL Posting            🟡 (Canary prepares; merchant GL executes)
  Cost Analysis         🟡 (Canary layer)
  Period Close          🟡 (Canary reports; merchant GL closes)
```

#### Slide 4: Development Effort Estimate

| Component | Design | Build/Test | Dev Total | Roll-out | Total |
|---|---|---|---|---|---|
| PO module (optional, defer v2.1) | 0 | 0 | 0 | 0 | 0 |
| Supplier invoicing (light) | 150 | 300 | 450 | 100 | 550 |
| 3-way match rules engine | 180 | 350 | 530 | 100 | 630 |
| GL integration layer (QBO, Xero, Wave) | 200 | 400 | 600 | 150 | 750 |
| Cost allocation (Cost Method only, RIM deferred) | 120 | 280 | 400 | 50 | 450 |
| Exception workflows + exception UI | 100 | 250 | 350 | 100 | 450 |
| Period-close reports (Canary analytics) | 80 | 150 | 230 | 50 | 280 |
| Testing (integration + OAuth flows) | 0 | 400 | 400 | 150 | 550 |
| **Total Man Days** | **830** | **2,130** | **2,960** | **700** | **3,660** |
| **Total Man Years** | | | | | **18.3** |

**Estimation basis:** 2–3 engineers; 4-month calendar window. QBO/Xero OAuth flows are pre-validated; Wave/FreshBooks plugged later. Assumes merchant has active GL subscription.

#### Slide 5: Architecture vs. Aspirational (Org View)
```
Option B supports merchant evolution:
  ✓ Merchant can switch GL vendors without losing Canary functionality
  ✓ Canary layer remains focused on perpetual cost; GL is decoupled
  ✓ Enables future integrations (payroll, banking) that speak to merchant GL
  ✓ Reduces Canary's liability for GL correctness (merchant owns GL)
  
Heat-map: 1 green, 5 yellow, 1 red (PO).
Verdict: Good future flexibility. Option B passes Aspirational with caveats (see disadvantages).
```

#### Slide 6: Architecture vs. Aspirational (Process View)
**Same finding.** Decoupling GL opens the door for future ecosystem integration without re-architecting.

#### Slide 7: Advantages / Disadvantages + Target Architecture

**Advantages:**
1. **18 engineer-years, not 28.** Scope is tighter; GL complexity is merchant's problem.
2. **Merchant adoption ease.** Merchants trust their existing GL (QBO, Xero). Canary integrates into their workflow, not a replacement.
3. **No GL audit liability.** Merchant's accountant certifies the merchant GL; Canary provides the journal-entry prep layer.
4. **Flexibility.** Merchant can switch GL vendors without disrupting Canary.
5. **Speed.** 4-month to MVP vs. 6-month for Option A. Finance feature shipped faster.
6. **Aspirational-ready.** Decoupled GL layer enables future payroll, banking, forecasting integrations.

**Disadvantages:**
1. **OAuth/API dependency.** Canary is now dependent on QBO/Xero/Wave API uptime and versioning. If a vendor deprecates an endpoint, Canary must adapt.
2. **Merchant GL variance exposure.** If merchant's GL is misconfigured (e.g., chart of accounts missing a subaccount), Canary's journal entry may post to the wrong account. Canary has no control.
3. **Multi-GL credential management.** Canary must securely store and refresh OAuth tokens for each merchant's GL. Token refresh failures = posting failures.
4. **Reconciliation friction.** Canary perpetual inventory ≠ merchant GL COGS (due to timing, error correction, manual GL entries). Merchant must understand the difference.
5. **Vendor lock-in (inverted).** If QBO changes the journal-entry API, Canary must adapt. Merchant is also locked into QBO.
6. **RIM complexity deferred.** Real/Integrated Merchandise accounting is still not supported; Cost Method only in v2. Merchant accountants may reject this as incomplete.

**Target Architecture Diagram:**
```
┌────────────────────────────────────────────────────────────────┐
│  Merchant (SMB)                                                │
│                                                                │
│  ┌──────────────────┐        ┌──────────────────────────────┐ │
│  │ Square POS       │        │ Merchant's GL Package        │ │
│  │ ┌──────────────┐ │        │ (QBO / Xero / Wave)          │ │
│  │ │ Transactions │ │        │ ┌────────────────────────────┤ │
│  │ └──────┬───────┘ │        │ │ Chart of Accounts          │ │
│  └────────┼─────────┘        │ │ Journal Entries (inbound)   │ │
│           │                  │ │ Reporting / Close           │ │
│           │                  │ └────────────────────────────┤ │
│           │                  │  OAuth API                   │ │
│           │                  └────────────┬─────────────────┘ │
│           │                               │                   │
│     ┌─────▼───────────────────────────────┼─────┐              │
│     │ Canary (v2.F option B)              │     │              │
│     │ ┌──────────────────────────────────┘     │              │
│     │ │ Perpetual Inventory (GRN)           │   │              │
│     │ │ Supplier Invoice Matching (3-way)   │   │              │
│     │ │ Exception Workflows                 │   │              │
│     │ │ → Journal Entry Prep (batch)        │───┤              │
│     │ │   - Dr. Inventory / Cr. AP          │   │              │
│     │ │   - Dr. COGS / Cr. Inventory        │   │              │
│     │ │                                     │   │              │
│     │ │ Cost Analysis (perpetual layer)     │   │              │
│     │ └─────────────────────────────────────┘   │              │
│     └─────────────────────────────────────────────┘              │
│                                                                │
│  Legend: All GL posting authority in Merchant's GL            │
└────────────────────────────────────────────────────────────────┘
```

---

### OPTION C: Integrated Hybrid (Recommended)

**Title:** Hybrid Split — Canary Owns Perpetual, Merchant's GL Owns Period — OAuth Bridge at the Boundary

**One-liner:** Canary handles perpetual inventory + supplier invoice matching; merchant's GL owns the P&L, A/R, A/P. Canary publishes COGS-move journal entries to the merchant GL via OAuth. Cleanest split of responsibility.

#### Slide 1: Title
"Option C — Integrated Hybrid: Canary perpetual layer + merchant GL partnership via OAuth bridge. Cost Method only (v2); RIM deferred (v3)."

#### Slide 2: Architecture vs. Optimisation (Org View)
```
Perpetual Inventory   🟢 (leverage)
PO Tracking           🟢 (optional; defer or light)
Supplier Invoicing    🟡 (build, merchant GL unaware)
3-Way Match           🟡 (build)
GL Posting (Canary → Merchant GL) 🟡 (build OAuth bridge)
Cost Allocation       🟡 (Cost Method; RIM deferred v3)
Period Close          🟡 (Canary reports; merchant GL closes)
```
**Heat-map summary:** 2 green, 4 yellow, 0 red. **Excellent fit for Optimisation targets.** Minimal new complexity; leverages existing architecture.

#### Slide 3: Architecture vs. Optimisation (Process View)
```
Buy (Supplier Sourcing)
  PO Creation           🟢 (optional; direct invoice possible)
  Invoice Receipt       🟡
  3-Way Match           🟡
  GL Posting (COGS)     🟡

Move (Inbound Supply)
  GRN / Receipt         🟢
  Allocation (Cost)     🟡

Reporting/Control
  GL Posting via OAuth  🟡 (Canary → Merchant GL)
  Cost Analysis         🟢 (Canary's perpetual layer)
  Period Close          🟡 (Merchant GL; Canary provides audit trail)
```

#### Slide 4: Development Effort Estimate

| Component | Design | Build/Test | Dev Total | Roll-out | Total |
|---|---|---|---|---|---|
| Supplier invoicing (light) | 120 | 250 | 370 | 80 | 450 |
| 3-way match rules engine | 150 | 300 | 450 | 80 | 530 |
| GL integration layer (QBO, Xero, Wave) | 180 | 350 | 530 | 120 | 650 |
| Cost Method selector (defer RIM) | 100 | 200 | 300 | 50 | 350 |
| Perpetual-layer audit trail (ledger reporting) | 80 | 150 | 230 | 40 | 270 |
| Exception workflows | 80 | 180 | 260 | 60 | 320 |
| Testing (GL integration, reconciliation) | 0 | 350 | 350 | 120 | 470 |
| **Total Man Days** | **810** | **1,780** | **2,590** | **550** | **3,140** |
| **Total Man Years** | | | | | **15.7** |

**Estimation basis:** 2–3 engineers; 3-month calendar window (fastest option). Assumes no PO module build; direct invoice receipt. Testing includes perpetual-GL reconciliation scenarios.

#### Slide 5: Architecture vs. Aspirational (Org View)
```
Option C supports future evolution:
  ✓ Perpetual layer can evolve to RIM (v3) without touching GL contract
  ✓ Merchant GL remains authority for P&L and reporting; Canary ≠ GL
  ✓ GL vendor independence; merchant can switch QBO → Xero without Canary code change
  ✓ Enables ecosystem integrations (payroll, banking, forecasting) on the GL side
  ✓ Canary can add cost management features (allocation, variance, what-if) without GL liability
  
Heat-map: 2 green, 4 yellow, 0 red.
Verdict: Clear winner. Option C enables a 5-year roadmap without architectural debt.
```

#### Slide 6: Architecture vs. Aspirational (Process View)
**Same finding.** Perpetual-vs-period split creates a durable interface.

#### Slide 7: Advantages / Disadvantages + Target Architecture

**Advantages:**
1. **16 engineer-years, not 28 or 18.** Tightest scope; perpetual-layer focused.
2. **Fastest to market.** 3-month calendar window. Finance feature ships in Q3 2026.
3. **Merchant adoption optimized.** Merchants use their familiar GL; Canary is a feeder into that GL, not a replacement.
4. **Clear responsibility split.** Canary owns perpetual (inventory moves, cost allocation). Merchant GL owns period (accrual, P&L, close, tax reporting).
5. **No GL audit liability.** Merchant accountant certifies merchant GL; Canary provides the ledger-movement prep.
6. **RIM-ready architecture.** Cost Method in v2; RIM (Retail Integrated Merchandise) in v3 uses the same OAuth bridge. No re-architecture.
7. **Ecosystem-friendly.** Merchant can integrate payroll (via GL), banking (via GL), forecasting (via GL) without Canary friction.

**Disadvantages:**
1. **Perpetual-GL reconciliation discipline required.** Merchant must understand that Canary's perpetual inventory ≠ merchant GL COGS. Timing differences, manual GL entries, and error corrections require monthly reconciliation.
2. **OAuth/API dependency (same as Option B).** QBO/Xero API uptime is a dependency. Canary must handle token refresh failures gracefully.
3. **RIM is deferred to v3.** Cost Method only in v2. Merchants using Actual Inventory Valuation (RIM) will have to live with a lighter feature set for 6–12 months.
4. **Merchant GL credential management.** Canary must securely store OAuth tokens for each merchant's GL. Token expiry or revocation = posting failures (mitigated with good error UX).
5. **Reconciliation reporting is not automatic.** Merchant must run a monthly perpetual-vs-GL reconciliation. Canary can provide the audit trail, but the merchant approves.

**Target Architecture Diagram:**
```
┌─────────────────────────────────────────────────────────────────┐
│  Merchant (SMB)                                                 │
│                                                                 │
│  ┌──────────────────┐          ┌───────────────────────────────┤
│  │ Square POS       │          │ Merchant's GL Package         │
│  │ Transactions     │          │ (QBO / Xero / Wave)           │
│  └────────┬─────────┘          │                               │
│           │                    │ Authority for:                │
│           │                    │  - Chart of Accounts          │
│           │                    │  - A/P, A/R, Payroll          │
│           │                    │  - P&L, Balance Sheet         │
│           │                    │  - Tax Reporting              │
│           │                    │  - Period Close               │
│           │                    │                               │
│           │         ┌──────────┤  OAuth API (inbound)          │
│           │         │          └───────────────────────────────┤
│           │         │
│     ┌─────▼─────────▼───────────────────────────────────────────┐
│     │  Canary v2.F (Option C) — Perpetual Layer                │
│     │  ┌──────────────────────────────────────────────────────┐ │
│     │  │ Core:                                                │ │
│     │  │  • GRN + Inventory Perpetual (from app/sales)         │ │
│     │  │  • Supplier Invoice Receipt + 3-Way Match            │ │
│     │  │  • Cost Allocation (Cost Method; RIM → v3)           │ │
│     │  │  • COGS Ledger (perpetual)                           │ │
│     │  │                                                       │ │
│     │  │ Outputs:                                             │ │
│     │  │  • Journal Entry Batch (daily/weekly)                │ │
│     │  │    - Dr. Inventory / Cr. A/P                         │ │
│     │  │    - Dr. COGS / Cr. Inventory                        │ │
│     │  │    → POST to Merchant GL (OAuth)                     │ │
│     │  │                                                       │ │
│     │  │  • Perpetual Audit Trail (for reconciliation)        │ │
│     │  │  • Cost Analysis Dashboard                           │ │
│     │  │  • Exception Workflows                               │ │
│     │  └──────────────────────────────────────────────────────┘ │
│     └────────────────────────────────────────────────────────────┘
│
│  Legend:
│    🟢 Canary perpetual ownership
│    🔵 Merchant GL authority (COGS is posted, not owned, by Canary)
│    🟡 Integration point (OAuth bridge)
└─────────────────────────────────────────────────────────────────┘
```

---

## Section 8: Summary and Conclusion

### Page 1: Architecture Comparison (All Three Options)

| Process Area | **Option A: Native GL** | **Option B: Best-of-Breed** | **Option C: Hybrid** |
|---|---|---|---|
| **Buy** |  |  |  |
| PO Tracking | 🔴 Build | 🔴 Defer | 🟢 Optional |
| Invoice Matching | 🔴 Build | 🟡 Build | 🟡 Build |
| GL Posting | 🔴 Native | 🟡 OAuth → QBO/Xero | 🟡 OAuth → QBO/Xero |
| **Move** |  |  |  |
| GRN / Receipt | 🟢 Exist | 🟢 Exist | 🟢 Exist |
| Allocation | 🔴 Build (RIM prep) | 🟡 Build (Cost) | 🟡 Build (Cost) |
| **Reporting/Control** |  |  |  |
| Cost Analysis | 🔴 Build | 🟡 Build | 🟢 Leverage |
| Period Close | 🔴 Build | 🟡 Report | 🟡 Report |
| GL Authority | Canary | Merchant | Merchant |
| **Effort (Man-Years)** | **27.9** | **18.3** | **15.7** |
| **Calendar Months** | 6 | 4 | 3 |

### Page 2: Implementation Comparison

| Factor | **Option A** | **Option B** | **Option C** |
|---|---|---|---|
| **Timescale** | 6 months | 4 months | 3 months ✓ |
| **Risk of Overrun** | High (GL builds are 20% overruns) | Medium | Low |
| **External Dependency** | Minimal (own GL) | High (QBO/Xero API) | High (QBO/Xero API) |
| **Technology Lock-in** | **SEVERE** — Merchant locked to Canary GL | Medium — Merchant locked to GL vendor | Low — GL vendor independence |
| **Phasing / Modularity** | All-or-nothing (GL requires close/accrual) | Modular (PO deferred; invoice first) | Modular ✓ (Cost Method v2, RIM v3) |
| **Time to First Benefits** | 6+ months (after full build) | 4 months (invoice match + COGS posting) | **3 months** (invoice match + Cost-only GL posting) ✓ |
| **Merchant Adoption Friction** | **HIGHEST** — merchants don't trust Canary GL | Medium — merchants still need GL credentials | Low — merchants use familiar GL ✓ |
| **GL Audit Liability** | Canary responsible (high risk) | Shared | Merchant responsible ✓ |

### Page 3: Recommendation

**CHOSEN: Option C — Integrated Hybrid.**

**Reasoning:**

1. **Business targets alignment.** Option C delivers all four Optimisation targets by Q3 2026:
   - Merchant adoption: 40% activation in 30 days → leveraging familiar GL reduces friction
   - Cost reduction: 8–12% variance improvement → perpetual-layer accuracy is unchanged across all options; C achieves this fastest
   - Time-to-value: 7-day invoice receipt to GL posting → C's 3-month timeline enables this
   - Operational headcount: No new accounting hire needed → merchant GL handles standard GL work; Canary handles perpetual

2. **Risk and time-to-market.** 15.7 engineer-years and 3 months beats Option B (18.3 / 4 months) and Option A (27.9 / 6 months). Fastest path to revenue.

3. **Merchant adoption and GL liability.** Options A and B differ fundamentally:
   - Option A forces merchants into a Canary GL they don't trust and Canary doesn't want to audit.
   - Option B works but carries API dependency risk and token-management overhead.
   - Option C splits responsibility cleanly: Canary perpetual (expert domain), Merchant GL (merchant's responsibility). Merchant accountants prefer this model.

4. **Aspirational readiness.** The perpetual-vs-period boundary created by Option C is durable:
   - v2: Cost Method only. Merchant uses simple cost allocation (FIFO, weighted avg). Canary posts daily GL entries.
   - v3 (2027): RIM support. Canary computes actual/real integrated merchandise costs. Same OAuth bridge; same GL integration.
   - v4 (future): Cost management (variance, what-if, allocation optimization). Perpetual layer only; no GL changes.

5. **Ecosystem integration.** Keeping GL as merchant's authority enables future integrations (payroll, banking, forecasting, multi-location accounting) that Canary doesn't have to build.

**Phasing (3 Releases: v2.0 → v2.1 → v3):**

| Release | Timeline | Scope | Effort | Benefit |
|---|---|---|---|---|
| **v2.0 (MVP)** | Q3 2026 (3 mo) | Supplier invoice receipt, 3-way match, Cost Method, GL posting to QBO/Xero/Wave | 15.7 eng-years | Addresses all Optimisation targets; enables 40% adoption |
| **v2.1 (v2+)** | Q4 2026 (2 mo) | PO tracking (optional inbound), exception escalation workflows, perpetual-GL reconciliation reporting | 4 eng-years | Improves merchant workflow; enables upsell to multi-location merchants |
| **v3 (RIM)** | Q2 2027 (4 mo) | Real/Integrated Merchandise (RIM) cost accounting, advanced allocation, 3-cost-method selector (FIFO/WAV/Std), variance analysis | 8 eng-years | Enables enterprise customer use; expands GL capability without architectural change |

**Major Decision Gates:**
- **Post-MVP (Dec 2026):** Review API uptime / token-refresh error rates from QBO/Xero/Wave. If >3% posting failures, escalate to support team + explore fallback (batch reconciliation + merchant manual posting).
- **Pre-v2.1 (Nov 2026):** If <30% adoption after launch, investigate merchant friction: is GL credential entry the blocker? Is 3-way match too strict? Adjust rules before v2.1.
- **Pre-v3 (Q1 2027):** Validate RIM demand signal from installed base. If <10% of merchants use RIM, defer to v4 and allocate v3 to ecosystem integrations (e.g., Stripe → GL sync).

**Resource Commitment:**
- **Engineering:** 3 FTE (2.5 core + 0.5 QA) for 3 months (MVP); 2 FTE for 2 months (v2.1); 2 FTE for 4 months (v3).
- **Product:** 1 FTE (PM) + 0.5 FTE (analyst for GL exception handling workflows).
- **Support:** 0.5 FTE trained for merchant onboarding (GL credential flow, reconciliation, exception escalation).
- **External:** QBO/Xero/Wave API support contracts (optional; standard OAuth flows).

**First 90 Days (v2.0 MVP):**

1. **Weeks 1–2:** Finalize merchant GL OAuth scopes (read Chart of Accounts, post Journal Entries). Validate token refresh flow.
2. **Weeks 3–4:** Build supplier_invoices schema + ingestion. 3-way match rule engine.
3. **Weeks 5–6:** Build GL integration layer (journal entry batch prep, post loop).
4. **Weeks 7–8:** Cost Method selector logic. Testing / reconciliation.
5. **Weeks 9–10:** Merchant UAT (closed cohort: 2–3 beta merchants).
6. **Weeks 11–12:** GA launch. Support onboarding.

---

## Appendix: Glossary

| Term | Definition |
|---|---|
| **Perpetual Inventory** | Real-time tracking of inventory cost as goods move through the supply chain (GRN → allocation → COGS). Distinct from period-end GL accrual. |
| **3-Way Match** | Verification that PO quantity = GRN quantity = Invoice quantity before a payment is released. |
| **Cost Method** | Inventory cost accounting (FIFO, LIFO, weighted average, standard cost). v2 supports Cost Method; v3 adds RIM. |
| **RIM (Real/Integrated Merchandise)** | Actual cost + integrated allocation for multi-step supply chains (e.g., purchase → distribution center → store → sale). v3 feature. |
| **GL (General Ledger)** | Merchant's accounting system of record (QBO, Xero, Wave, FreshBooks, etc.). Authority for statutory reporting, tax filing, P&L. |
| **COGS (Cost of Goods Sold)** | Inventory cost as goods are sold. Canary perpetual layer feeds GL COGS entries. |
| **OAuth Bridge** | API integration using merchant's GL vendor OAuth flows (QBO, Xero) to post journal entries without storing GL credentials. |

---

## Conclusion

Canary v2.F adopts **Option C** (Integrated Hybrid). This decision prioritizes **merchant trust, rapid time-to-market, and architectural durability**. The perpetual-vs-period boundary is clean, defensible, and extensible to RIM (v3) and beyond. Canary remains the expert in loss-prevention retail accounting (perpetual cost, variance, COGS accuracy) while ceding GL and statutory reporting to the merchant's native package. This is the pattern enterprise retailers (JDA, Retek, SAP, Manhattan) have used for 20 years. We're building the SMB equivalent.

**Ship v2.0 MVP in Q3 2026. Measure merchant adoption and GL integration stability. Phase to v3 (RIM) in Q2 2027.**


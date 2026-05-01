---
title: Canary Functional Decomp — Gap Ledger
tags: [canary, functional-decomp, meta]
status: current
created: 2026-04-26
last-compiled: 2026-04-26
---

# Canary Functional Decomp — Gap Ledger

Findings from the GRO-608 next-level consistency pass across all 11 completed functional decomposition articles. Five criteria checked per article; gaps graded P1 (blocking / load-bearing), P2 (structural), P3 (narrative completeness). Modules L and W remain on hold and are not included.

---

## Criterion 1 — Cross-Module Dependency Symmetry

Eight of eleven modules fully reciprocate their dependency claims. Three do not (D, J, Q) — plus N partially.

### P1 — Load-bearing asymmetries

| Gap | Source claim | Missing reciprocal | Action |
|---|---|---|---|
| J ↔ P | J.8a: P.6.3 promotion calendar is load-bearing to J forecasting | P lists J in companions but does NOT assert P.6.3 is architecturally critical to J | Add explicit reciprocal contract statement in P.6.3 or P contracts section |
| A ↔ Q | A.3.1: asset-item registry provides allow-list exclusion consumed by Q detection rules | Q lists A in companions but does NOT claim dependency on A.3.1 | Q must reciprocate that Q.2 detection rules depend on A.3.1 filtering |

### P2 — Structural asymmetries

| Gap | Source claim | Missing reciprocal | Action |
|---|---|---|---|
| D ↔ A | A.2.1: reads D.6.1 SOH snapshot + D.6.3 TRANSFER-VARIANCE | D lists A but does not state D.6.1/D.6.3 are consumed by A | Add D contract statement for A read-dependency |
| N ↔ Q | N.5: provides LP threshold substrate + drawer-session context to Q | Q lists N in companions but does not reciprocate N.5 contracts | Q must reciprocate N.5 as upstream contract provider |
| F ↔ J | F.5.2: PO cost-flow contract consumed by J replenishment costing | J lists F but does not reciprocate F.5.2 centrality | J must add explicit reciprocal reference to F.5.2 |
| T ↔ D | T type-routes XFER documents to D via T.4.7 | D lists T as downstream but does not reciprocate T.4.7 type-routing contract | D must explicitly reciprocate T.4.7 in D.6.2 or contracts section |

---

## Criterion 2 — L4 Pointers Complete

**Systemic finding:** All non-canonical modules lack L4 stubs or `→ TBD` pointers on most L3 processes. Module Q and its rule catalog companion are the sole complete examples. The gap is structural — these modules were written to L3 depth with an implicit assumption that L4 would be a later authoring pass. That pass is now explicit.

| Module | L3 count | L4 status | Specific gaps |
|---|---|---|---|
| A | 12 | ✗ None | All 12 L3 processes (A.1.1–A.1.5, A.2.1–A.2.4, A.3.1–A.3.4) missing stubs |
| C | 26 | ✗ None | All 26 L3 processes (M.1–M.5) missing stubs |
| D | 29 | ✗ None | All 29 L3 processes (D.1–D.5) missing stubs |
| F | 28 | ✗ None | All 28 L3 processes (F.1–F.6) missing stubs |
| J | ~40 | ⚠ Mostly complete | O.1.6 (like-item forecasting): no L4 stub; O.2.6 (lead-time variance): deferred "v2.1" but no concrete L4 commitment |
| N | 27 | ✓ Complete | All reference canary-module-n-device.md + §6.5 |
| P | ~35 | ⚠ Partial | P.2.1 (promotional window inference): no SDD crosswalk; P.4.5 (cold-start elasticity): ASSUMPTION-P-07 with no algorithm; P.5.3 (linked-item price deps): no L4 schema |
| Q | 38 | ✓ Complete | Canonical — rule catalog + SDK + SDD cross-references throughout |
| R | ~30 | ✗ None | All L3 processes missing stubs |
| S | ~35 | ✗ None | All L3 processes missing stubs |
| T | ~40 | ✗ None | All L3 processes missing stubs |

**Resolution applied in this pass:** `→ TBD` stubs added to all silent L3 processes in A, C, D, F, R, S, T. O.1.6 and O.2.6 upgraded to explicit TBD with author note. P.2.1, P.4.5, P.5.3 given algorithm-stub templates.

---

## Criterion 3 — User Stories Comprehensive

| Module | Stories present | Gaps identified |
|---|---|---|
| A | 14 | Asset-zone reassignment across store locations; reclassification triggered by unplanned retail sale of a fixture item |
| C | 32 | Seasonal tier reclassification (retail→wholesale during spring contractor ramp); credit-hold override workflow; tier inconsistency between historical and current transactions |
| D | 38 | Hub-and-spoke transfer with intermediate stop; transfer reversal before destination receives; split-transfer recommendation across multiple understocked locations; transfer audit context differs by actor (warehouse mgr vs store mgr) |
| F | 41 | PayCode creation during onboarding (post-bootstrap new tender type); tax-code line-level override; gift-card partial redemption (insufficient balance); multi-currency AR transaction; replacement-card balance reassignment on card loss/damage |
| J | 68 | ✓ Complete |
| N | 33 | Multi-device enrollment / workstation-to-station mapping (N.2.3); per-store config drift detection at scale across multi-location tenant |
| P | 44 | Stacked promotions (multiple active promos on same item); cross-category promotion spillover; markdown execution failure/rollback (buyer reverts markdown in Counterpoint, Canary must detect and sync) |
| Q | 71 | ✓ Complete |
| R | 47 | Profile-extension deferred to v3 (explicitly flagged); cross-company customer collision detection (C.5.3 scenario) |
| S | 52 | Owl eCommerce integration implicit in S.5.2 — no explicit investigator-surface user story |
| T | 64 | Offline-mode document handling absent (ASSUMPTION-T-05 exists but no corresponding user story) |

---

## Criterion 4 — Counterpoint Substrate Table Present

| Module | Status | Detail |
|---|---|---|
| A | ✓ by design | Derived module; no own endpoints; substrate entirely from S. Intentional posture documented. |
| C | ✗ Missing | Reads AR_CUST, Customer_OpenItems, AR_CUST_CTL (from R) — enumerated in text, not tabulated |
| D | ✗ Missing | 7 inventory endpoints (Inventory_ByLocation, Items_ByLocation, Item_Inventory, InventoryLocations, InventoryControl, InventoryCost, InventoryEC) listed in executive summary, not mapped to L2 areas |
| F | ✗ Missing | ~12 endpoints (PayCodes, TaxCodes, GiftCards, NSPTransaction, Tokenize, Customer OpenItems, etc.) in text, no tabular mapping |
| J | ✓ Complete | L3-to-substrate reads mapped; document type routing explicit (PO/PREQ/RECVR/RTV) |
| N | ✓ Complete | Store, Station, DeviceConfig, Workgroup, Tokenize enumerated per section |
| P | ✗ Missing | No endpoint-mapping table at all. IM_ITEM and PS_DOC_LIN_PRICE referenced in prose only |
| Q | ✓ Complete | 14-row CRDM table; canonical format |
| R | ✗ Missing | Endpoint reads present in text; no tabular mapping |
| S | ✗ Missing | Substrate reads in text; no tabular mapping |
| T | ✗ Missing | Transaction pipeline substrate described narratively; no mapping table |

**Modules needing substrate tables added:** C, D, F, P, R, S, T (7 of 11).

---

## Criterion 5 — Canary Detection Hook Identified

| Module | Status | Detail |
|---|---|---|
| A | N/A | Observer-only module; no detection surface. Contracts feed Q but A does not itself detect. |
| C | ✗ Partial | M.4 defines rules (B2B-CREDIT-01, B2B-AR-01, etc.) but rule catalog ownership unclear — not cross-referenced to Q rule families or Chirp ingest point |
| D | ✓ Complete | D.4.5 → Q alert with D.4.1 evidence; D.6.3 TRANSFER-VARIANCE → Q-IS-03; D.6.5 UNATTRIBUTED-MOVEMENT → Q anomaly correlation |
| F | ✓ Complete | F.7.3 → Q-TC-01; F.7.8 → Q-TM-02; F.7.2 → Q-TC-01; F.7.1 → Q tender-mix rules |
| J | ✓ Complete | O.6 receiving + O.7 RTV → Q-IS-01/02/04; O.4 recommendation state machine; O.8 contracts explicit |
| N | ✗ Gap | N.4 supplies LP threshold substrate to Q but no statement of which Chirp rule family each N L2 area triggers |
| P | ✗ Gap | P.2.6 (undeclared promotions) mentions "event published to Q" but does not name Q rule family; P.6.7 tangential; elasticity signal injection into O.1.4 not explicitly named as Chirp input |
| Q | ✓ Complete | Canonical — 10 rule families, all with detection hook mappings |
| R | ✗ Missing | No detection-hook registry |
| S | ✗ Missing | No detection-hook registry |
| T | ✗ Missing | No detection-hook registry |

---

## Priority Matrix

| Priority | Item | Modules affected |
|---|---|---|
| P1 | Reciprocate J↔P promotional-demand isolation contract | J, P |
| P1 | Reciprocate A↔Q asset-item registry filtering dependency | A, Q |
| P2 | Add Counterpoint substrate mapping tables | C, D, F, P, R, S, T |
| P2 | Add detection hook sections (name Chirp rule family per L2) | C, N, P, R, S, T |
| P2 | Reciprocate D↔A and N↔Q and F↔J and T↔D structural contracts | D, N, J, T |
| P2 | L4 stubs (`→ TBD`) on all silent L3 processes | A, C, D, F, R, S, T |
| P3 | Add missing user stories (enumerated per module above) | A, C, D, F, N, P, R, S, T |
| P3 | Clarify M.4 rule ownership vs Q rule catalog | C |
| P3 | Make P.4.5 cold-start elasticity algorithm explicit | P |

---

*Generated: GRO-608 consistency pass, 2026-04-26. Canonical reference: canary-module-q-functional-decomposition.md.*

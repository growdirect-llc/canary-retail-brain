---
type: process-decomp
artifact: process-map
pass-date: 2026-04-28
source: GRO-670
---

# CRB Process Map — L3 → Go Subsystem Index

**Pass date:** 2026-04-28 | **Total L3 processes:** 357 | **Mapped:** 212 | **GAP:** 145

Provenance codes: `DOCUMENTED` = explicitly stated in functional-decomp file | `INFERRED` = implied by described behavior | `GAP` = no subsystem found

---

## Module T — Transaction Pipeline

**L1:** Transaction Processing | **Go subsystem:** `cmd/tsp` | **Solution Map:** ★ Canary native

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| T.1 Adapter ingress | T.1.1 | Counterpoint poll-ingress via `GET /Documents` | DOCUMENTED | `cmd/tsp` | Mapped |
| T.1 | T.1.2 | Square webhook ingress | DOCUMENTED | `cmd/tsp` | Mapped |
| T.1 | T.1.3 | Document watermark management per tenant | DOCUMENTED | `cmd/tsp` | Mapped |
| T.1 | T.1.4 | Pagination + backpressure | DOCUMENTED | `cmd/tsp` | Mapped |
| T.1 | T.1.5 | Auth credential injection per provider | DOCUMENTED | `cmd/tsp` | Mapped |
| T.1 | T.1.6 | Multi-company routing per tenant | DOCUMENTED | `cmd/tsp` | Mapped |
| T.1 | T.1.7 | Cached-entity refresh discipline | DOCUMENTED | `cmd/tsp` | Mapped |
| T.1 | T.1.8 | Rate-limit observance | DOCUMENTED | `cmd/tsp` | Mapped |
| T.1 | T.1.9 | Connection-failure retry + circuit-break | DOCUMENTED | `cmd/tsp` | Mapped |
| T.2 Sealing & integrity | T.2.1 | Document receipt stamp | DOCUMENTED | `cmd/tsp` | Mapped |
| T.2 | T.2.2 | Dedup / idempotency check | DOCUMENTED | `cmd/tsp` | Mapped |
| T.2 | T.2.3 | Hash-before-parse (patent-critical ordering) | DOCUMENTED | `cmd/tsp` | Mapped |
| T.2 | T.2.4 | Seal record write to ledger | DOCUMENTED | `cmd/tsp` | Mapped |
| T.2 | T.2.5 | Document-omnibus fanout routing | DOCUMENTED | `cmd/tsp` | Mapped |
| T.2 | T.2.6 | Mutation-lock enforcement | DOCUMENTED | `cmd/tsp` | Mapped |
| T.3 Provider-keyed parsing | T.3.1 | Counterpoint DOC_TYP-keyed parser selection | DOCUMENTED | `cmd/tsp` | Mapped |
| T.3 | T.3.2 | Square transaction parser | DOCUMENTED | `cmd/tsp` | Mapped |
| T.3 | T.3.3 | Header field extraction (STR_ID, STA_ID, DRW_ID, USR_ID, CUST_NO, timestamps) | DOCUMENTED | `cmd/tsp` | Mapped |
| T.3 | T.3.4 | Payment-line flattening (PS_DOC_PMT[]) + PII redaction | DOCUMENTED | `cmd/tsp` | Mapped |
| T.3 | T.3.5 | Tax-line flattening (PS_DOC_TAX[]) multi-authority preservation | DOCUMENTED | `cmd/tsp` | Mapped |
| T.3 | T.3.6 | Line-item flattening (PS_DOC_LIN[]) | DOCUMENTED | `cmd/tsp` | Mapped |
| T.3 | T.3.7 | Audit-log flattening (PS_DOC_AUDIT_LOG[]) | DOCUMENTED | `cmd/tsp` | Mapped |
| T.3 | T.3.8 | Pricing-decision flattening (PS_DOC_LIN_PRICE[]) | DOCUMENTED | `cmd/tsp` | Mapped |
| T.4 Canonical event publication | T.4.1 | SALE event publication | DOCUMENTED | `cmd/tsp` | Mapped |
| T.4 | T.4.2 | RETURN event publication | DOCUMENTED | `cmd/tsp` | Mapped |
| T.4 | T.4.3 | VOID event publication | DOCUMENTED | `cmd/tsp` | Mapped |
| T.4 | T.4.4 | PAYMENT event publication | DOCUMENTED | `cmd/tsp` | Mapped |
| T.4 | T.4.5 | TAX event publication | DOCUMENTED | `cmd/tsp` | Mapped |
| T.4 | T.4.6 | AUDIT-LOG event publication | DOCUMENTED | `cmd/tsp` | Mapped |
| T.4 | T.4.7 | DOC_TYP routing (XFER→D, RECVR→J, RTV→J, PO→J) | DOCUMENTED | `cmd/tsp` | Mapped |
| T.4 | T.4.8 | Customer-reference upsert trigger | DOCUMENTED | `cmd/tsp` | Mapped |
| T.4 | T.4.9 | Original-doc reference preservation | DOCUMENTED | `cmd/tsp` | Mapped |
| T.5 Merkle anchoring | T.5.1 | Merkle tree construction per batch | DOCUMENTED | `cmd/tsp` | Mapped |
| T.5 | T.5.2 | Root hash computation and storage | DOCUMENTED | `cmd/tsp` | Mapped |
| T.5 | T.5.3 | Per-document leaf-hash linkage | DOCUMENTED | `cmd/tsp` | Mapped |
| T.5 | T.5.4 | Audit-proof generation | DOCUMENTED | `cmd/tsp` | Mapped |
| T.5 | T.5.5 | Hash-chain verification | DOCUMENTED | `cmd/tsp` | Mapped |
| T.6 Replay / backfill | T.6.1 | Historical backfill ingestion | DOCUMENTED | `cmd/tsp` | Mapped |
| T.6 | T.6.2 | Replay from sealed ledger | DOCUMENTED | `cmd/tsp` | Mapped |
| T.6 | T.6.3 | Idempotency enforcement on replay | DOCUMENTED | `cmd/tsp` | Mapped |
| T.6 | T.6.4 | Out-of-order event resequencing | DOCUMENTED | `cmd/tsp` | Mapped |
| T.6 | T.6.5 | Stale-data staleness flagging | DOCUMENTED | `cmd/tsp` | Mapped |
| T.7 Substrate contracts | T.7.1–T.7.12 | Cross-module contract registry (12 contracts) | DOCUMENTED | `cmd/tsp` | Mapped |

**T total L3:** 41 (+ 12 contracts) | **All mapped** → `cmd/tsp`

---

## Module Q — Loss Prevention

**L1:** Loss Prevention & Compliance | **Go subsystems:** `cmd/chirp` (detection), `cmd/fox` (cases), `cmd/alert` (delivery) | **Solution Map:** ★ Canary native

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| Q.1 Substrate ingestion | Q.1.1 | Read transaction headers | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.1 | Q.1.2 | Read transaction lines | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.1 | Q.1.3 | Read payments | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.1 | Q.1.4 | Read multi-authority taxes | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.1 | Q.1.5 | Read audit log | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.1 | Q.1.6 | Read pricing decisions | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.1 | Q.1.7 | Read original-doc references | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.1 | Q.1.8 | Read store config thresholds | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.1 | Q.1.9 | Read item categories with margin targets | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.1 | Q.1.10 | Read customer tier + AR posture | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.1 | Q.1.11 | Read transfers, receivers, RTVs | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.2 Detection execution | Q.2.1 | Discount-and-markdown rule family (Q-DM-01/02/03) | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.2 | Q.2.2 | Void-and-return rule family (Q-VR-01/02/03) | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.2 | Q.2.3 | Tender-mix anomalies (Q-TM-01/02/03) | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.2 | Q.2.4 | Drawer-and-session family (Q-DS-01/02/03) | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.2 | Q.2.5 | Audit-trail anomalies (Q-AT-01/02/03) | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.2 | Q.2.6 | Margin-erosion family (Q-ME-01/02) | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.2 | Q.2.7 | Inventory-and-shrink family (Q-IS-01/02/03/04) | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.2 | Q.2.8 | Tax-and-compliance family (Q-TC-01/02) | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.2 | Q.2.9 | Customer-tier abuse (Q-CT-01/02) | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.2 | Q.2.10 | Mix-and-match abuse (Q-MM-01/02) | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.3 Detection lifecycle | Q.3.1 | Detection emission | DOCUMENTED | `cmd/fox` | Mapped |
| Q.3 | Q.3.2 | Suppression evaluation | DOCUMENTED | `cmd/fox` | Mapped |
| Q.3 | Q.3.3 | Case bundling | DOCUMENTED | `cmd/fox` | Mapped |
| Q.3 | Q.3.4 | Severity escalation | DOCUMENTED | `cmd/fox` | Mapped |
| Q.3 | Q.3.5 | Investigator notification | DOCUMENTED | `cmd/alert` | Mapped |
| Q.3 | Q.3.6 | Case investigation state machine | DOCUMENTED | `cmd/fox` | Mapped |
| Q.3 | Q.3.7 | Case close + outcome capture | DOCUMENTED | `cmd/fox` | Mapped |
| Q.4 Tuning | Q.4.1 | Threshold tuning per rule | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.4 | Q.4.2 | Allow-list entry creation | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.4 | Q.4.3 | Allow-list expiration / sunset | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.4 | Q.4.4 | Vertical-pack application | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.4 | Q.4.5 | Rule promotion (dry-run → alerting) | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.5 Investigator surface | Q.5.1 | Detection query tool | DOCUMENTED | `cmd/fox` | Mapped |
| Q.5 | Q.5.2 | Detection detail tool | DOCUMENTED | `cmd/fox` | Mapped |
| Q.5 | Q.5.3 | Owl natural-language Q&A | DOCUMENTED | `cmd/owl` | Mapped |
| Q.5 | Q.5.4 | Fox case workflow | DOCUMENTED | `cmd/fox` | Mapped |
| Q.5 | Q.5.5 | Dry-run preview tool | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.5 | Q.5.6 | Per-store / per-employee dashboards | DOCUMENTED | `cmd/report` | Mapped |
| Q.5 | Q.5.7 | Case digest (scheduled) | DOCUMENTED | `cmd/alert` | Mapped |
| Q.6 Vertical config | Q.6.1–Q.6.5 | 5 garden-center allow-lists | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.6 | Q.6.6–Q.6.8 | Vertical-pack management | DOCUMENTED | `cmd/chirp` | Mapped |
| Q.7 Deployment phasing | Q.7.1–Q.7.7 | Cutover phases + rollback | DOCUMENTED | `cmd/chirp` | Mapped |

**Q total L3:** 38 | **All mapped** → `cmd/chirp` / `cmd/fox` / `cmd/alert` / `cmd/owl` / `cmd/report`

---

## Module C — Customer

**L1:** People / Customer | **Go subsystem:** `cmd/customer` | **Solution Map:** ● Full direct

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| C.1 Registry & upsert | C.1.1 | Shell-row upsert from T's reference | DOCUMENTED | `cmd/customer` | Mapped |
| C.1 | C.1.2 | Full-row enrichment from GET /Customer/{CustNo} | DOCUMENTED | `cmd/customer` | Mapped |
| C.1 | C.1.3 | Incremental sync via GET /Customers | DOCUMENTED | `cmd/customer` | Mapped |
| C.1 | C.1.4 | EC-flagged customer enrichment | DOCUMENTED | `cmd/customer` | Mapped |
| C.1 | C.1.5 | CustomerControl read at tenant bootstrap | DOCUMENTED | `cmd/customer` | Mapped |
| C.1 | C.1.6 | Workgroup template read | DOCUMENTED | `cmd/customer` | Mapped |
| C.1 | C.1.7 | Soft-delete on customer archival | DOCUMENTED | `cmd/customer` | Mapped |
| C.1 | C.1.8 | Multi-company namespace isolation | DOCUMENTED | `cmd/customer` | Mapped |
| C.2 Tier identity | C.2.1 | Surface CATEG_COD verbatim | DOCUMENTED | `cmd/customer` | Mapped |
| C.2 | C.2.2 | Tier-code → tier-meaning mapping per tenant | DOCUMENTED | `cmd/customer` | Mapped |
| C.2 | C.2.3 | Tier-change audit on customer record | DOCUMENTED | `cmd/customer` | Mapped |
| C.2 | C.2.4 | Multi-tier pricing flag surfacing | DOCUMENTED | `cmd/customer` | Mapped |
| C.2 | C.2.5 | Open-AR balance per customer | DOCUMENTED | `cmd/customer` | Mapped |
| C.2 | C.2.6 | Customer credit posture | DOCUMENTED | `cmd/customer` | Mapped |
| C.2 | C.2.7 | B2B vs retail derivation hooks | DOCUMENTED | `cmd/customer` | Mapped |
| C.3 Loyalty + AR | C.3.1 | Surface loyalty enrollment | DOCUMENTED | `cmd/customer` | Mapped |
| C.3 | C.3.2 | Surface loyalty balance | DOCUMENTED | `cmd/customer` | Mapped |
| C.3 | C.3.3 | Surface loyalty redemption events | DOCUMENTED | `cmd/customer` | Mapped |
| C.3 | C.3.4 | Surface AR-customer flag | DOCUMENTED | `cmd/customer` | Mapped |
| C.3 | C.3.5 | Surface open AR aging | DOCUMENTED | `cmd/customer` | Mapped |
| C.3 | C.3.6 | AR-charge-vs-cash transaction posture | DOCUMENTED | `cmd/customer` | Mapped |
| C.4 Privacy posture | C.4.1 | Schema-enforced PII absence | DOCUMENTED | `cmd/customer` | Mapped |
| C.4 | C.4.2 | Read-through to Counterpoint at query time | DOCUMENTED | `cmd/customer` | Mapped |
| C.4 | C.4.3 | Card-fingerprint storage (opaque) | DOCUMENTED | `cmd/customer` | Mapped |
| C.4 | C.4.4 | PII-redaction-at-parse contract | DOCUMENTED | `cmd/customer` | Mapped |
| C.4 | C.4.5 | GDPR/CCPA right-to-be-forgotten | DOCUMENTED | `cmd/customer` | Mapped |
| C.4 | C.4.6 | Profile-extension opt-in (future) | DOCUMENTED | `cmd/customer` | Mapped |
| C.5 Identity resolution | C.5.1 | Per-(tenant,company_alias) namespace isolation | DOCUMENTED | `cmd/customer` | Mapped |
| C.5 | C.5.2 | external_identities link table | DOCUMENTED | `cmd/customer` | Mapped |
| C.5 | C.5.3 | Manual identity link surface | DOCUMENTED | `cmd/customer` | Mapped |
| C.5 | C.5.4 | Cross-vendor identity resolution (v2) | DOCUMENTED | `cmd/customer` | Mapped |
| C.5 | C.5.5 | Customer-side ID assertion (future) | DOCUMENTED | `cmd/customer` | Mapped |
| C.6 Investigator + contracts | C.6.1–C.6.14 | Investigator surface (6) + substrate contracts (8) | DOCUMENTED | `cmd/customer` | Mapped |

**R total L3:** 32 (+ 14 contracts/surface) | **All mapped** → `cmd/customer`

---

## Module N — Device / Stores / Per-Store Config

**L1:** Infrastructure / Store Config | **Go subsystem:** `cmd/edge` (INFERRED) | **Solution Map:** ● Full direct

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| N.1 Store config ingestion | N.1.1 | Store master ingestion (GET /Store/{StoreID}) | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.1 | N.1.2 | Per-store config field surfacing (~150 fields PS_STR_CFG_PS) | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.1 | N.1.3 | Per-store demographics | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.1 | N.1.4 | Industry-type field surfacing | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.1 | N.1.5 | Per-store cache refresh | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.2 Station / device registry | N.2.1 | Station enumeration per store | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.2 | N.2.2 | Per-workstation device config | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.2 | N.2.3 | Workstation-to-station mapping | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.2 | N.2.4 | Tokenization scope per store | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.3 Drawer-session correlation | N.3.1 | Drawer-session entity surfacing | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.3 | N.3.2 | Per-session start/end timestamp resolution | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.3 | N.3.3 | Per-session employee + station + drawer attribution | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.3 | N.3.4 | Drawer-reactivation tracking | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.3 | N.3.5 | Drawer-count vs expected reconciliation | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.4 LP thresholds | N.4.1 | Discount cap thresholds (MAX_DISC_AMT, MAX_DISC_PCT) | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.4 | N.4.2 | Void / comp reason requirements | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.4 | N.4.3 | Credit-card history retention (PCI flag) | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.4 | N.4.4 | Drawer config + alarms | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.4 | N.4.5 | Customer-profile field enablement | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.4 | N.4.6 | EDC payment processor config | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.4 | N.4.7 | Workflow defaults (order, layaway, dropship) | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.5 Workgroup | N.5.1 | Workgroup ingestion at tenant bootstrap | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.5 | N.5.2 | Document-numbering generators surfaced | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.5 | N.5.3 | Customer-template defaults surfaced | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.5 | N.5.4 | Per-(tenant,company_alias) workgroup partitioning | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| N.6 Contracts | N.6.1–N.6.8 | Cross-module substrate contracts (8) | DOCUMENTED | `cmd/edge` | Mapped (INFERRED) |
| — | — | **NOTE:** All N→`cmd/edge` mappings are INFERRED. `cmd/edge` is listed in CanaryGO but its scope has not been confirmed as N's subsystem. Needs codebase inspection. | INFERRED | — | CONFIRM-NEEDED |

**N total L3:** 27 | **All mapped to `cmd/edge` (INFERRED)** — confirm `cmd/edge` owns store config

---

## Module A — Asset Management

**L1:** Asset Management | **Go subsystems:** `cmd/asset`, `cmd/inventory` | **Solution Map:** ◐ Derived

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| A.1 Asset-item identification | A.1.1 | Read IM_ITEM.ITEM_TYP from S's item master | DOCUMENTED | `cmd/asset` | Mapped |
| A.1 | A.1.2 | Read IM_ITEM.STAT alongside ITEM_TYP | DOCUMENTED | `cmd/asset` | Mapped |
| A.1 | A.1.3 | Maintain Canary-side asset-item registry | DOCUMENTED | `cmd/asset` | Mapped |
| A.1 | A.1.4 | Detect ITEM_TYP reclassification events | DOCUMENTED | `cmd/asset` | Mapped |
| A.1 | A.1.5 | Surface asset-item registry to downstream consumers | DOCUMENTED | `cmd/asset` | Mapped |
| A.2 Asset lifecycle | A.2.1 | Read D's movement records filtered to asset-item registry | DOCUMENTED | `cmd/inventory` | Mapped |
| A.2 | A.2.2 | Track per-asset location history | DOCUMENTED | `cmd/inventory` | Mapped |
| A.2 | A.2.3 | Detect unexpected movement on asset items | DOCUMENTED | `cmd/inventory` | Mapped |
| A.2 | A.2.4 | Flag high-value asset disposal via RTV-type movement | DOCUMENTED | `cmd/inventory` | Mapped |
| A.3 Contracts | A.3.1 | Asset-item registry (non-saleable item list) to Q, J, C | DOCUMENTED | `cmd/asset` | Mapped |
| A.3 | A.3.2 | ITEM_TYP reclassification events | DOCUMENTED | `cmd/asset` | Mapped |
| A.3 | A.3.3 | Asset location history per asset per location | DOCUMENTED | `cmd/inventory` | Mapped |
| A.3 | A.3.4 | High-value asset disposal flags | DOCUMENTED | `cmd/asset` | Mapped |

**A total L3:** 12 | **All mapped** — **SCOPE CONFLICT FLAG:** Module A canonical spec (Bubble) describes device-anomaly detection, not item-asset-management. ASSUMPTION-A-01 unresolved.

---

## Module M — Commercial / B2B

**L1:** Commercial / B2B Intelligence | **Go subsystem:** GAP — no `cmd/commercial` found | **Solution Map:** ◐ Derived

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| M.1 B2B classification | M.1.1 | Read AR_CUST.CATEG_COD from R | DOCUMENTED | GAP | GAP |
| M.1 | M.1.2 | Read AR_CUST_CTL multi-tier pricing flags | DOCUMENTED | GAP | GAP |
| M.1 | M.1.3 | Detect commercial-account indicator via credit terms | DOCUMENTED | GAP | GAP |
| M.1 | M.1.4 | Derive B2B classification score per customer | DOCUMENTED | GAP | GAP |
| M.1 | M.1.5 | Handle unclassified accounts | DOCUMENTED | GAP | GAP |
| M.1 | M.1.6 | Reclassification on CATEG_COD change | DOCUMENTED | GAP | GAP |
| M.2 Credit posture | M.2.1 | Read credit limit and current balance from AR_CUST | DOCUMENTED | GAP | GAP |
| M.2 | M.2.2 | Calculate credit utilization per commercial account | DOCUMENTED | GAP | GAP |
| M.2 | M.2.3 | Read aging buckets from Customer_OpenItems | DOCUMENTED | GAP | GAP |
| M.2 | M.2.4 | Derive payment velocity per account | DOCUMENTED | GAP | GAP |
| M.2 | M.2.5 | Produce per-account CREDIT_POSTURE signal | DOCUMENTED | GAP | GAP |
| M.2 | M.2.6 | Trigger credit-hold flag on AT-LIMIT accounts | DOCUMENTED | GAP | GAP |
| M.3 AR ledger surface | M.3.1 | Read per-account open items from F.6 publication | DOCUMENTED | GAP | GAP |
| M.3 | M.3.2 | Aggregate open items into per-account AR summary | DOCUMENTED | GAP | GAP |
| M.3 | M.3.3 | Track payment history per account | DOCUMENTED | GAP | GAP |
| M.3 | M.3.4 | Surface AR aging calendar per commercial account | DOCUMENTED | GAP | GAP |
| M.3 | M.3.5 | Detect anomalous payment patterns | DOCUMENTED | GAP | GAP |
| M.4 B2B detection rules | M.4.1 | B2B-CREDIT-01: at-limit account transacting | DOCUMENTED | GAP | GAP |
| M.4 | M.4.2 | B2B-CREDIT-02: rapid credit consumption | DOCUMENTED | GAP | GAP |
| M.4 | M.4.3 | B2B-AR-01: past-due balance threshold | DOCUMENTED | GAP | GAP |
| M.4 | M.4.4 | B2B-TIER-01: price inconsistent with B2B tier | DOCUMENTED | GAP | GAP |
| M.4 | M.4.5 | B2B-PATTERN-01: commercial transacting outside business hours | DOCUMENTED | GAP | GAP |
| M.5 Contracts | M.5.1–M.5.6 | B2B_CLASS, CREDIT_POSTURE, AR summary, alerts, price-tier mapping, UNCERTAIN roster | DOCUMENTED | GAP | GAP |

**C total L3:** 26 | **All GAP** — `cmd/customer` is R's subsystem; no `cmd/commercial` package exists for C's derived classification layer.

---

## Module D — Distribution

**L1:** Distribution / Inventory | **Go subsystems:** `cmd/inventory` (snapshots), `cmd/transfer` (XFER), `cmd/receiving` (partial) | **Solution Map:** ◐ Partial

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| D.1 Snapshot ingestion | D.1.1 | Poll GET /Inventory_ByLocation | DOCUMENTED | `cmd/inventory` | Mapped |
| D.1 | D.1.2 | Poll GET /Items_ByLocation | DOCUMENTED | `cmd/inventory` | Mapped |
| D.1 | D.1.3 | Poll GET /Item_Inventory | DOCUMENTED | `cmd/inventory` | Mapped |
| D.1 | D.1.4 | Detect and seal SOH deltas into ledger | DOCUMENTED | `cmd/inventory` | Mapped |
| D.1 | D.1.5 | Reconcile snapshot-vs-Document-derived position | DOCUMENTED | `cmd/inventory` | Mapped |
| D.1 | D.1.6 | Handle stale-location responses | DOCUMENTED | `cmd/inventory` | Mapped |
| D.2 Per-location attribution | D.2.1 | Poll GET /InventoryLocations | DOCUMENTED | `cmd/inventory` | Mapped |
| D.2 | D.2.2 | Poll GET /InventoryControl (reorder params) | DOCUMENTED | `cmd/inventory` | Mapped |
| D.2 | D.2.3 | Poll GET /InventoryCost per item per location | DOCUMENTED | `cmd/inventory` | Mapped |
| D.2 | D.2.4 | Poll GET /InventoryEC (omnichannel flags) | DOCUMENTED | `cmd/inventory` | Mapped |
| D.2 | D.2.5 | Detect new item-location pairs | DOCUMENTED | `cmd/inventory` | Mapped |
| D.3 Transfer detection | D.3.1 | Subscribe to T's Document stream (DOC_TYP=XFER) | DOCUMENTED | `cmd/transfer` | Mapped |
| D.3 | D.3.2 | Parse XFER Document header | DOCUMENTED | `cmd/transfer` | Mapped |
| D.3 | D.3.3 | Parse XFER Document lines | DOCUMENTED | `cmd/transfer` | Mapped |
| D.3 | D.3.4 | Post in-transit inventory hold | DOCUMENTED | `cmd/transfer` | Mapped |
| D.3 | D.3.5 | Detect transfer completion via paired RECVR | DOCUMENTED | `cmd/transfer` | Mapped |
| D.3 | D.3.6 | Handle transfer-in-transit timeout | DOCUMENTED | `cmd/transfer` | Mapped |
| D.4 Transfer-loss reconciliation | D.4.1 | Calculate transfer-variance per (XFER, item) | DOCUMENTED | `cmd/transfer` | Mapped |
| D.4 | D.4.2 | Classify transfer variance by type | DOCUMENTED | `cmd/transfer` | Mapped |
| D.4 | D.4.3 | Detect systematic transfer-loss patterns per route | DOCUMENTED | `cmd/transfer` | Mapped |
| D.4 | D.4.4 | Reconcile unattributed SOH deltas | DOCUMENTED | `cmd/transfer` | Mapped |
| D.4 | D.4.5 | Route high-variance transfers to investigation queue | DOCUMENTED | `cmd/transfer` | Mapped |
| D.4 | D.4.6 | Allow-list seasonal-movement patterns | DOCUMENTED | `cmd/transfer` | Mapped |
| D.5 Distribution recs | D.5.1 | Calculate excess stock per (item, location) | DOCUMENTED | `cmd/transfer` | Mapped |
| D.5 | D.5.2 | Calculate deficit stock per (item, location) | DOCUMENTED | `cmd/transfer` | Mapped |
| D.5 | D.5.3 | Match excess at one location to deficit at another | DOCUMENTED | `cmd/transfer` | Mapped |
| D.5 | D.5.4 | Score rebalancing candidates by transfer-cost | DOCUMENTED | `cmd/transfer` | Mapped |
| D.5 | D.5.5 | Generate transfer recommendation with OTB context | DOCUMENTED | `cmd/transfer` | Mapped |
| D.5 | D.5.6 | Buyer review + accept/modify/reject | DOCUMENTED | `cmd/transfer` | Mapped |
| D.6 Contracts | D.6.1–D.6.9 | SOH snapshot, XFER routing, TRANSFER-VARIANCE, in-transit, UNATTRIBUTED, transfer-cost, ROP, item-location set, timeout alerts | DOCUMENTED | `cmd/inventory` / `cmd/transfer` | Mapped |

**D total L3:** 35 | **All mapped** → `cmd/inventory` (D.1/D.2) + `cmd/transfer` (D.3/D.4/D.5)

---

## Module F — Finance (Tenders / Tax / Gift Cards)

**L1:** Finance | **Go subsystems:** `cmd/analytics`, `cmd/report` | **Solution Map:** ● Full direct

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| F.1 Tender taxonomy | F.1.1 | PayCode list ingestion at tenant bootstrap | DOCUMENTED | `cmd/analytics` | Mapped |
| F.1 | F.1.2 | Per-PayCode detail enrichment | DOCUMENTED | `cmd/analytics` | Mapped |
| F.1 | F.1.3 | PayCode update detection | DOCUMENTED | `cmd/analytics` | Mapped |
| F.1 | F.1.4 | PayCode classification mapping per tenant | DOCUMENTED | `cmd/analytics` | Mapped |
| F.1 | F.1.5 | Alternative-payment-rail PayCode tagging | DOCUMENTED | `cmd/analytics` | Mapped |
| F.2 Tax code surfacing | F.2.1 | TaxCode list ingestion at tenant bootstrap | DOCUMENTED | `cmd/analytics` | Mapped |
| F.2 | F.2.2 | Per-store default tax code surfacing | DOCUMENTED | `cmd/analytics` | Mapped |
| F.2 | F.2.3 | Tax-exempt customer flag surfacing | DOCUMENTED | `cmd/analytics` | Mapped |
| F.2 | F.2.4 | Per-jurisdiction tax-authority enumeration per store | DOCUMENTED | `cmd/analytics` | Mapped |
| F.3 Gift card surface | F.3.1 | GiftCard issued-card list ingestion | DOCUMENTED | `cmd/analytics` | Mapped |
| F.3 | F.3.2 | Per-GiftCard detail enrichment | DOCUMENTED | `cmd/analytics` | Mapped |
| F.3 | F.3.3 | GiftCardCode template ingestion | DOCUMENTED | `cmd/analytics` | Mapped |
| F.3 | F.3.4 | Per-GiftCardCode detail | DOCUMENTED | `cmd/analytics` | Mapped |
| F.3 | F.3.5 | Gift-card activity surfacing per Document | DOCUMENTED | `cmd/analytics` | Mapped |
| F.3 | F.3.6 | Gift-card balance reconciliation | DOCUMENTED | `cmd/analytics` | Mapped |
| F.4 Payment + tax flattening | F.4.1 | Payment line preservation | DOCUMENTED | `cmd/analytics` | Mapped |
| F.4 | F.4.2 | PII redaction at parse (cross-cut with T) | DOCUMENTED | `cmd/tsp` (parse) / `cmd/analytics` (contract) | Mapped |
| F.4 | F.4.3 | Multi-authority tax preservation | DOCUMENTED | `cmd/analytics` | Mapped |
| F.4 | F.4.4 | Apply-to instruction surfacing | DOCUMENTED | `cmd/analytics` | Mapped |
| F.4 | F.4.5 | Tender-mix aggregation per session | DOCUMENTED | `cmd/analytics` | Mapped |
| F.4 | F.4.6 | Per-line tax allocation | DOCUMENTED | `cmd/analytics` | Mapped |
| F.5 Tokenization | F.5.1 | Per-store tokenization status check | DOCUMENTED | `cmd/identity` | Mapped (INFERRED) |
| F.5 | F.5.2 | Per-store tokenization run trigger | DOCUMENTED | `cmd/identity` | Mapped (INFERRED) |
| F.5 | F.5.3 | Aggregate tokenized count | DOCUMENTED | `cmd/identity` | Mapped (INFERRED) |
| F.5 | F.5.4 | NSPTransaction post-back receipt | DOCUMENTED | `cmd/identity` | Mapped (INFERRED) |
| F.5 | F.5.5 | Card-on-file token surfacing | DOCUMENTED | `cmd/identity` | Mapped (INFERRED) |
| F.6 AR ledger | F.6.1 | Per-customer open AR ingestion | DOCUMENTED | `cmd/analytics` | Mapped |
| F.6 | F.6.2 | Customer credit posture surfacing | DOCUMENTED | `cmd/analytics` | Mapped |
| F.6 | F.6.3 | AR-vs-tender reconciliation per Document | DOCUMENTED | `cmd/analytics` | Mapped |
| F.6 | F.6.4 | AR aging snapshot per period | DOCUMENTED | `cmd/report` | Mapped |
| F.6 | F.6.5 | B2B credit-decisioning hooks | DOCUMENTED | `cmd/analytics` | Mapped |
| F.7 Contracts | F.7.1–F.7.9 | Tender taxonomy, TaxCode, multi-authority tax, PII-redaction, gift-card, tokenization, AR aging, apply-to, alt-rail | DOCUMENTED | `cmd/analytics` | Mapped |

**F total L3:** 31 | **All mapped** → `cmd/analytics` (primary) + `cmd/identity` (tokenization, INFERRED) + `cmd/report` (AR aging snapshot) + `cmd/tsp` (parse-side PII redaction)

---

## Module O — Orders

**L1:** Forecasting / Order Management | **Go subsystems:** `cmd/receiving` (O.6/O.7), GAP for O.1/O.2/O.3/O.4/O.5/O.8 | **Solution Map:** ◐ Partial

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| O.1 Demand forecasting | O.1.1 | Read movement history per item per location | DOCUMENTED | GAP | GAP |
| O.1 | O.1.2 | Calculate demand velocity | DOCUMENTED | GAP | GAP |
| O.1 | O.1.3 | Calculate demand variance | DOCUMENTED | GAP | GAP |
| O.1 | O.1.4 | Produce 13-week rolling forecast | DOCUMENTED | GAP | GAP |
| O.1 | O.1.5 | Hierarchy-volatility-aware forecasting | DOCUMENTED | GAP | GAP |
| O.1 | O.1.6 | Like-item forecasting for new SKUs | DOCUMENTED | GAP | GAP |
| O.1 | O.1.7 | Per-channel demand attribution | DOCUMENTED | GAP | GAP |
| O.1 | O.1.8 | Forecast accuracy tracking (MAPE, bias) | DOCUMENTED | GAP | GAP |
| O.2 Replenishment params | O.2.1 | Calculate ROP per (item, location) | DOCUMENTED | GAP | GAP |
| O.2 | O.2.2 | Calculate EOQ per (item, location) | DOCUMENTED | GAP | GAP |
| O.2 | O.2.3 | Calculate Safety Stock | DOCUMENTED | GAP | GAP |
| O.2 | O.2.4 | Maintain Weeks-of-Supply target per category | DOCUMENTED | GAP | GAP |
| O.2 | O.2.5 | Counter stock exclusion | DOCUMENTED | GAP | GAP |
| O.2 | O.2.6 | Lead-time variance modeling | DOCUMENTED | GAP | GAP |
| O.2 | O.2.7 | Pre-pack-aware EOQ | DOCUMENTED | GAP | GAP |
| O.3 OTB management | O.3.1 | Read OTB budget from P's seasonal plan | DOCUMENTED | GAP | GAP |
| O.3 | O.3.2 | Calculate committed receipts per (dept, period) | DOCUMENTED | GAP | GAP |
| O.3 | O.3.3 | Compute remaining OTB headroom (rolling) | DOCUMENTED | GAP | GAP |
| O.3 | O.3.4 | OTB preview before PO commit | DOCUMENTED | GAP | GAP |
| O.3 | O.3.5 | OTB state-change events | DOCUMENTED | GAP | GAP |
| O.3 | O.3.6 | OTB approval gate routing | DOCUMENTED | GAP | GAP |
| O.3 | O.3.7 | Locked-period override | DOCUMENTED | GAP | GAP |
| O.4 PO recommendation | O.4.1 | Detect below-ROP items per scan | DOCUMENTED | GAP | GAP |
| O.4 | O.4.2 | Generate PO recommendation per (supplier, receipt-week) | DOCUMENTED | GAP | GAP |
| O.4 | O.4.3 | OTB headroom validation per recommendation | DOCUMENTED | GAP | GAP |
| O.4 | O.4.4 | Recommendation prioritization | DOCUMENTED | GAP | GAP |
| O.4 | O.4.5 | Buyer review + accept/modify/reject | DOCUMENTED | GAP | GAP |
| O.4 | O.4.6 | Multi-tier approval routing | DOCUMENTED | GAP | GAP |
| O.4 | O.4.7 | Auto-commit threshold | DOCUMENTED | GAP | GAP |
| O.4 | O.4.8 | What-if simulation | DOCUMENTED | GAP | GAP |
| O.5 PO generation | O.5.1 | Buyer-entered-in-Counterpoint path (v2) | DOCUMENTED | GAP | GAP |
| O.5 | O.5.2 | Canary-POST-Document path (v3+) | DOCUMENTED | GAP | GAP |
| O.5 | O.5.3 | PO header generation | DOCUMENTED | GAP | GAP |
| O.5 | O.5.4 | PO line generation | DOCUMENTED | GAP | GAP |
| O.5 | O.5.5 | Pre-distributed PO with allocation attached | DOCUMENTED | GAP | GAP |
| O.5 | O.5.6 | Bulk PO with allocation deferred | DOCUMENTED | GAP | GAP |
| O.5 | O.5.7 | EDI transmission to vendor | DOCUMENTED | GAP | GAP |
| O.5 | O.5.8 | New article creation at PO entry | DOCUMENTED | GAP | GAP |
| O.5 | O.5.9 | PO change message on allocation revision | DOCUMENTED | GAP | GAP |
| O.6 Receiving | O.6.1 | Detect new receiver Documents (DOC_TYP=RECVR) | DOCUMENTED | `cmd/receiving` | Mapped |
| O.6 | O.6.2 | Match receiver to PO via PS_DOC_HDR_ORIG_DOC | DOCUMENTED | `cmd/receiving` | Mapped |
| O.6 | O.6.3 | Quantity reconciliation (RECVR vs PO qty) | DOCUMENTED | `cmd/receiving` | Mapped |
| O.6 | O.6.4 | Cost reconciliation | DOCUMENTED | `cmd/receiving` | Mapped |
| O.6 | O.6.5 | OTB closeout on receipt | DOCUMENTED | `cmd/receiving` | Mapped |
| O.6 | O.6.6 | Forecast accuracy feedback from receipt date | DOCUMENTED | `cmd/receiving` | Mapped |
| O.6 | O.6.7 | Thin-metadata receiver tolerance | DOCUMENTED | `cmd/receiving` | Mapped |
| O.6 | O.6.8 | Cash-paid receiver classification | DOCUMENTED | `cmd/receiving` | Mapped |
| O.7 Short-ship + RTV | O.7.1 | Short-ship detection | DOCUMENTED | `cmd/receiving` | Mapped |
| O.7 | O.7.2 | Re-allocation logic on short-ship | DOCUMENTED | `cmd/receiving` | Mapped |
| O.7 | O.7.3 | PO change message for cancelled balance | DOCUMENTED | `cmd/receiving` | Mapped |
| O.7 | O.7.4 | RTV recommendation generation | DOCUMENTED | `cmd/receiving` | Mapped |
| O.7 | O.7.5 | RTV impact on OTB | DOCUMENTED | `cmd/receiving` | Mapped |
| O.7 | O.7.6 | RTV reason-code tracking | DOCUMENTED | `cmd/receiving` | Mapped |
| O.7 | O.7.7 | Dead-count / live-goods write-off | DOCUMENTED | `cmd/receiving` | Mapped |
| O.8 Promo isolation + contracts | O.8.1 | Read promotion calendar from P | DOCUMENTED | GAP | GAP |
| O.8 | O.8.2 | Quarantine promotional lift from base demand | DOCUMENTED | GAP | GAP |
| O.8 | O.8.3 | Recurring-promotion blending | DOCUMENTED | GAP | GAP |
| O.8 | O.8.4 | Pre-promotion demand projection | DOCUMENTED | GAP | GAP |
| O.8 | O.8.5–O.8.11 | Substrate contract registry (7 contracts) | DOCUMENTED | GAP | GAP |

**J total L3:** 47 | **Mapped:** 14 (O.6/O.7 → `cmd/receiving`) | **GAP:** 33 (O.1–O.5, O.8 — no forecast/OTB/PO-generation subsystem)

---

## Module S — Space / Range / Display (Items / Catalog)

**L1:** Catalog / Item Management | **Go subsystem:** `cmd/item` | **Solution Map:** ● Full direct

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| S.1 Item master ingestion | S.1.1 | Full-row enrichment GET /Item/{ItemNo} | DOCUMENTED | `cmd/item` | Mapped |
| S.1 | S.1.2 | Incremental sync via GET /Items | DOCUMENTED | `cmd/item` | Mapped |
| S.1 | S.1.3 | Per-location item enrichment | DOCUMENTED | `cmd/item` | Mapped |
| S.1 | S.1.4 | Item image references | DOCUMENTED | `cmd/item` | Mapped |
| S.1 | S.1.5 | Serial number tracking | DOCUMENTED | `cmd/item` | Mapped |
| S.1 | S.1.6 | Per-location serial enumeration | DOCUMENTED | `cmd/item` | Mapped |
| S.1 | S.1.7 | Vendor-item linkage | DOCUMENTED | `cmd/item` | Mapped |
| S.2 Category hierarchy | S.2.1 | Category hierarchy ingestion | DOCUMENTED | `cmd/item` | Mapped |
| S.2 | S.2.2 | Per-category detail enrichment (margin targets) | DOCUMENTED | `cmd/item` | Mapped |
| S.2 | S.2.3 | Category-margin-target surfacing to Q | DOCUMENTED | `cmd/item` | Mapped |
| S.2 | S.2.4 | Category-history-of-assignment tracking | DOCUMENTED | `cmd/item` | Mapped |
| S.2 | S.2.5 | Subcategory rollup | DOCUMENTED | `cmd/item` | Mapped |
| S.2 | S.2.6 | Per-category assortment plan substrate | DOCUMENTED | `cmd/item` | Mapped |
| S.3 Mix-and-match groups | S.3.1 | Item-side mix-and-match group identification | DOCUMENTED | `cmd/item` | Mapped |
| S.3 | S.3.2 | Bundle pricing rule surfacing | DOCUMENTED | `cmd/item` | Mapped |
| S.3 | S.3.3 | Per-line bundle attribution at sale time | DOCUMENTED | `cmd/item` | Mapped |
| S.3 | S.3.4 | Bundle integrity audit | DOCUMENTED | `cmd/item` | Mapped |
| S.3 | S.3.5 | Bundle-margin computation | DOCUMENTED | `cmd/item` | Mapped |
| S.4 Fractional units | S.4.1 | Preferred unit identification | DOCUMENTED | `cmd/item` | Mapped |
| S.4 | S.4.2 | Stock unit identification | DOCUMENTED | `cmd/item` | Mapped |
| S.4 | S.4.3 | Per-line fractional quantity surfacing | DOCUMENTED | `cmd/item` | Mapped |
| S.4 | S.4.4 | Inventory deduction at fractional scale | DOCUMENTED | `cmd/item` | Mapped |
| S.4 | S.4.5 | Fractional-unit-aware analytics | DOCUMENTED | `cmd/item` | Mapped |
| S.5 Item lifecycle | S.5.1 | Item status surfacing | DOCUMENTED | `cmd/item` | Mapped |
| S.5 | S.5.2 | Multi-name field surfacing | DOCUMENTED | `cmd/item` | Mapped |
| S.5 | S.5.3 | Item-code drift handling | DOCUMENTED | `cmd/item` | Mapped |
| S.5 | S.5.4 | Mid-season catalog addition | DOCUMENTED | `cmd/item` | Mapped |
| S.5 | S.5.5 | Retired-item handling | DOCUMENTED | `cmd/item` | Mapped |
| S.5 | S.5.6 | Manual-entry-error tolerance | DOCUMENTED | `cmd/item` | Mapped |
| S.6 eCommerce catalog | S.6.1 | eCommerce control read at tenant bootstrap | DOCUMENTED | `cmd/item` | Mapped |
| S.6 | S.6.2 | eCommerce category hierarchy ingestion | DOCUMENTED | `cmd/item` | Mapped |
| S.6 | S.6.3 | Per-item EC flag surfacing | DOCUMENTED | `cmd/item` | Mapped |
| S.6 | S.6.4 | EC-inventory snapshot | DOCUMENTED | `cmd/item` | Mapped |
| S.6 | S.6.5 | HTML description surfacing | DOCUMENTED | `cmd/item` | Mapped |
| S.6 | S.6.6 | EC publish-state-machine tracking | DOCUMENTED | `cmd/item` | Mapped |
| S.7 Contracts | S.7.1–S.7.11 | IM_ITEM preservation, margin targets, mix-match identity, fractional units, multi-name, lifecycle, EC state, vendor-item, per-location attribution, category-history, cache metadata | DOCUMENTED | `cmd/item` | Mapped |

**S total L3:** 36 | **All mapped** → `cmd/item`

---

## Module P — Pricing & Promotion

**L1:** Pricing / Promotion | **Go subsystem:** `cmd/pricing` | **Solution Map:** ◐ Derived

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| P.1 Multi-tier price derivation | P.1.1 | Read IM_ITEM.PRC_1 from S | DOCUMENTED | `cmd/pricing` | Mapped |
| P.1 | P.1.2 | Read IM_ITEM.REG_PRC from S | DOCUMENTED | `cmd/pricing` | Mapped |
| P.1 | P.1.3 | Read PREF_UNIT_PRC_1..N from S (multi-tier) | DOCUMENTED | `cmd/pricing` | Mapped |
| P.1 | P.1.4 | Read IM_ITEM.LST_COST (last cost) | DOCUMENTED | `cmd/pricing` | Mapped |
| P.1 | P.1.5 | Derive price-tier-to-customer-tier mapping | DOCUMENTED | `cmd/pricing` | Mapped |
| P.1 | P.1.6 | Calculate margin per price tier | DOCUMENTED | `cmd/pricing` | Mapped |
| P.1 | P.1.7 | Detect price-tier changes | DOCUMENTED | `cmd/pricing` | Mapped |
| P.2 Promotion lifecycle | P.2.1 | Infer promotional windows from T's price variance | DOCUMENTED | `cmd/pricing` | Mapped |
| P.2 | P.2.2 | Buyer confirms / creates promotion definition | DOCUMENTED | `cmd/pricing` | Mapped |
| P.2 | P.2.3 | Support promotion types (fixed-price, %-off, bundle, BOGO, threshold) | DOCUMENTED | `cmd/pricing` | Mapped |
| P.2 | P.2.4 | Publish promotion calendar to J and Q | DOCUMENTED | `cmd/pricing` | Mapped |
| P.2 | P.2.5 | Track promotion-period lift vs pre-promotion baseline | DOCUMENTED | `cmd/pricing` | Mapped |
| P.2 | P.2.6 | Detect undeclared promotions | DOCUMENTED | `cmd/pricing` | Mapped |
| P.2 | P.2.7 | Post-promotion performance summary | DOCUMENTED | `cmd/pricing` | Mapped |
| P.3 Markdown management | P.3.1 | Detect markdown events from REG_PRC vs PRC_1 delta | DOCUMENTED | `cmd/pricing` | Mapped |
| P.3 | P.3.2 | Markdown proposal workflow (Canary-native) | DOCUMENTED | `cmd/pricing` | Mapped |
| P.3 | P.3.3 | Markdown approval gate | DOCUMENTED | `cmd/pricing` | Mapped |
| P.3 | P.3.4 | Markdown execution tracking | DOCUMENTED | `cmd/pricing` | Mapped |
| P.3 | P.3.5 | Markdown performance tracking | DOCUMENTED | `cmd/pricing` | Mapped |
| P.3 | P.3.6 | End-of-markdown / clearance management | DOCUMENTED | `cmd/pricing` | Mapped |
| P.3 | P.3.7 | Seasonal markdown calendar | DOCUMENTED | `cmd/pricing` | Mapped |
| P.4 Elasticity tracking | P.4.1 | Calculate price-elasticity coefficient per item | DOCUMENTED | `cmd/pricing` | Mapped |
| P.4 | P.4.2 | Classify items by elasticity tier | DOCUMENTED | `cmd/pricing` | Mapped |
| P.4 | P.4.3 | Surface elasticity signals to J | DOCUMENTED | `cmd/pricing` | Mapped |
| P.4 | P.4.4 | Track category-level elasticity | DOCUMENTED | `cmd/pricing` | Mapped |
| P.4 | P.4.5 | Cold-start elasticity fallback | DOCUMENTED | `cmd/pricing` | Mapped |
| P.5 Mass price maintenance | P.5.1 | Detect bulk price-change events | DOCUMENTED | `cmd/pricing` | Mapped |
| P.5 | P.5.2 | Flag bulk changes for buyer review | DOCUMENTED | `cmd/pricing` | Mapped |
| P.5 | P.5.3 | Track linked-item price dependencies | DOCUMENTED | `cmd/pricing` | Mapped |
| P.6 Contracts | P.6.1–P.6.7 | Price-change events, active-markdown indicator, promotion calendar, markdown approval, elasticity, tier mapping, undeclared promotion | DOCUMENTED | `cmd/pricing` | Mapped |

**P total L3:** 33 | **All mapped** → `cmd/pricing`

---

## Module L — Labor

**L1:** Workforce / Labor | **Go subsystem:** `cmd/employee` | **Solution Map:** v3 (not yet in Counterpoint scope)

> **Source:** Narrative-only (`wiki/canary-module-l-labor.md`). No functional decomp file. All L3s INFERRED from schema crosswalk and narrative.

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| L.1 Employee profile | L.1.1 | Employee master ingestion / maintenance | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.1 | L.1.2 | Employee role assignment | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.1 | L.1.3 | Employee active/inactive lifecycle | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.2 Schedule management | L.2.1 | Shift creation and publication | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.2 | L.2.2 | Traffic-tier-aligned schedule validation | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.2 | L.2.3 | Labor budget compliance check | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.3 Time tracking | L.3.1 | Clock-in / clock-out capture | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.3 | L.3.2 | Break start / end capture | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.3 | L.3.3 | No-show / late arrival detection | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.4 Absence management | L.4.1 | Absence recording and approval | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.5 Productivity metrics | L.5.1 | Transactions-per-hour aggregation from T | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.5 | L.5.2 | Items-handled aggregation from D | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.6 Payroll export | L.6.1 | Payroll export generation (CSV / generic format) | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.6 | L.6.2 | Payroll export audit trail | INFERRED | `cmd/employee` | Mapped (INFERRED) |
| L.7 LP integration | L.7.1 | Employee case-subject lookup in Fox | INFERRED | `cmd/employee` | Mapped (INFERRED) |

**L total L3:** ~15 (INFERRED) | **All mapped to `cmd/employee`** — v3 design; no code yet

---

## Module E — Execution

**L1:** Cross-domain Exception Detection | **Go subsystem:** GAP — no `cmd/work` or equivalent found | **Solution Map:** v3 (capstone)

> **Source:** Narrative-only (`wiki/canary-module-e-execution.md`). No functional decomp file. All L3s INFERRED from schema crosswalk and narrative.

| L2 | L3 ID | L3 Process | Provenance | Go Subsystem | Status |
|----|-------|-----------|-----------|-------------|--------|
| E.1 Exception ingestion | E.1.1 | Subscribe to all spine module exception streams | INFERRED | GAP | GAP |
| E.1 | E.1.2 | Generic exception record creation | INFERRED | GAP | GAP |
| E.2 Rule evaluation | E.2.1 | Domain-specific rule evaluation (inventory, pricing, labor, space) | INFERRED | GAP | GAP |
| E.2 | E.2.2 | Exception severity classification | INFERRED | GAP | GAP |
| E.3 Cross-domain correlation | E.3.1 | Subject-based exception correlation (customer/employee/vendor) | INFERRED | GAP | GAP |
| E.3 | E.3.2 | Multi-domain pattern detection | INFERRED | GAP | GAP |
| E.4 Case management | E.4.1 | Case creation from aggregated exceptions | INFERRED | GAP | GAP |
| E.4 | E.4.2 | Case state machine (extends Q's Fox) | INFERRED | GAP | GAP |
| E.4 | E.4.3 | Evidence chain (INSERT-only, hash-chained, inherited from Fox) | INFERRED | GAP | GAP |
| E.5 Remediation routing | E.5.1 | Remediation request routing to target module | INFERRED | GAP | GAP |
| E.5 | E.5.2 | Remediation status tracking | INFERRED | GAP | GAP |
| E.6 Investigator tools | E.6.1 | Exception-search MCP tool | INFERRED | GAP | GAP |
| E.6 | E.6.2 | Case CRUD MCP tool | INFERRED | GAP | GAP |
| E.6 | E.6.3 | Cross-domain analytics surface | INFERRED | GAP | GAP |

**W total L3:** ~14 (INFERRED) | **All GAP** — v3 design; no cmd/ package exists yet

---

## Summary Table

| Module | L2 Areas | L3 Count | Mapped | GAP | Primary cmd/ subsystem |
|--------|----------|----------|--------|-----|------------------------|
| T — Transaction Pipeline | 7 | 41 | 41 | 0 | `cmd/tsp` |
| Q — Loss Prevention | 7 | 38 | 38 | 0 | `cmd/chirp` / `cmd/fox` / `cmd/alert` |
| C — Customer | 6 | 32 | 32 | 0 | `cmd/customer` |
| N — Device / Store Config | 6 | 27 | 27 (INFERRED) | 0 | `cmd/edge` (INFERRED — confirm) |
| A — Asset Management | 3 | 12 | 12 | 0 | `cmd/asset` / `cmd/inventory` |
| C — Commercial / B2B | 5 | 26 | 0 | 26 | GAP — no `cmd/commercial` |
| D — Distribution | 6 | 35 | 35 | 0 | `cmd/inventory` / `cmd/transfer` |
| F — Finance | 6 | 31 | 31 | 0 | `cmd/analytics` / `cmd/identity` |
| J — Orders | 8 | 47 | 14 | 33 | `cmd/receiving` (partial); GAP for forecast/OTB/PO |
| S — Space / Range / Display | 7 | 36 | 36 | 0 | `cmd/item` |
| P — Pricing & Promotion | 6 | 33 | 33 | 0 | `cmd/pricing` |
| L — Labor | 7 | ~15 | ~15 (INFERRED) | 0 | `cmd/employee` |
| W — Execution | 6 | ~14 | 0 | ~14 | GAP — v3 not yet built |
| **TOTAL** | **80** | **~391** | **~319** | **~73** | — |

**Note on L4:** All L3 processes in all modules are currently tagged `TBD: L4 implementation detail pending`. L4 is universally a GAP across the entire corpus. The user has indicated documentation exists that can be used to fill L4 steps — see CRB-GAP-LIST.md for the full L4 gap registry.

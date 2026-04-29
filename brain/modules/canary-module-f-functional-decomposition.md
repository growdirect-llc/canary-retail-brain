---
classification: internal
type: wiki
sub-type: module-functional-decomposition
date: 2026-04-26
last-compiled: 2026-04-26
status: draft v1 (archetype — no real customer engagement)
module: F
solution-map-cell: ● Full direct (Counterpoint PayCode / TaxCode / GiftCard / Document_Payments / NSPTransaction — ~12 endpoints)
companion-modules: [T, R, Q, J, C]
companion-substrate: [ncr-counterpoint-api-reference.md, ncr-counterpoint-document-model.md, ncr-counterpoint-endpoint-spine-map.md]
companion-context: [garden-center-operating-reality.md, ncr-counterpoint-rapid-pos-relationship.md, rapid-pos-counterpoint-user-pain-points.md]
companion-canary-spec: Canary-Retail-Brain/modules/F-finance.md
companion-canary-crosswalk: Brain/wiki/canary-module-f-finance.md
companion-catz: CATz/proof-cases/specialty-smb-counterpoint-solution-map.md
methodology-note: "Sister card to canary-module-q/t/r/j/s-functional-decomposition.md. Same template per CATz/method/artifacts/module-functional-decomposition.md. F is a substrate module shared by T (per-Document payments + tax), R (AR ledger), J (PO cost flow), and Q (tender + tax abuse rules) — its L2 split reflects the cross-cutting nature."
---

# Module F (Finance — Tenders / Tax / Gift Cards) — Functional Decomposition

> **Artifact layer.** Third of three Canary module artifact layers:
> 1. **Canonical spec** (vendor-neutral) — `Canary-Retail-Brain/modules/F-finance.md`
> 2. **Code/schema crosswalk** (Canary-specific) — `Brain/wiki/canary-module-f-finance.md`
> 3. **Functional decomposition** (Counterpoint-substrate-aware, L2/L3 + user stories) — *this card*

## Governing thesis

F owns the **tender, tax, and gift-card substrate** for the spine. Counterpoint exposes a flexible PayCode taxonomy (any tender — cash, card, AR, gift card, alternative-payment-rail — definable by the customer), a TaxCode list with multi-authority preservation per Document, a GiftCard family with per-code template support, and a Secure Pay tokenization surface. Every payment activity flows through T's Document polling (`PS_DOC_PMT[]` is per-Document) — F surfaces the *configuration*, T surfaces the *activity*, and the two together feed Q's tender-mix anomalies and the AR-vs-tender reconciliation that bridges to R.

For a Lawn & Garden tenant specifically, three vertical realities shape F's posture: (1) **multi-tier tender mix is real** — landscaper customers pay AR (open ledger), retail walk-ins pay card or cash, gift cards are seasonally heavy (Mother's Day / holidays); (2) **multi-authority tax stacking is the norm** — city + county + state preserved per Document line is required for tax-authority reconciliation without external joins; (3) **alternative payment rails are an opportunity** — Zelle / Venmo / Cash App / Bitcoin Lightning can fit in the PayCode taxonomy for vendor-side payments, and Canary can pull the wallet activity into CRDM as a Canary-native option-(e) wedge.

F is **● Full direct** in every Counterpoint Solution Map cell, but the cell hides three concerns: (1) **PayCode + TaxCode are cached server-side 24h** so polling discipline matters, (2) **the Secure Pay tokenization surface has unique authentication semantics** — three endpoints don't require an APIKey but require the registration option enabled, and (3) **AR ledger surfacing cross-cuts R** — `Customer_OpenItems` is technically a Customer endpoint but its use is finance-shaped (aging buckets, B2B credit posture, collection workflows).

## Executive summary

| Dimension | Count | Source |
|---|---|---|
| L2 process areas | 6 | This card |
| L3 functional processes | 31 | This card |
| Counterpoint endpoints in F's path | ~12 (PayCode / PayCodes / TaxCodes / GiftCard / GiftCards / GiftCardCode / GiftCardCodes / Tokenize endpoints / NSPTransaction / Document_Payments) | API reference |
| Cached entities (24h server-side) | 2 (PayCodes, TaxCodes — also GiftCardCodes likely) | API reference cache discipline |
| Cross-cuts with T | 1 (per-Document payment + tax flattening — F.4) | T.3 + T.7 |
| Cross-cuts with R | 1 (AR ledger surfacing — F.6) | R.3.5 |
| Substrate contracts F owes downstream | 9 | This card §F.7 |
| Assumptions requiring real-customer validation | 9 | Tagged `ASSUMPTION-F-NN` |
| User stories enumerated | 41 | Observer + actor mix; cast in §Operating notes |

**Posture:** archetype-shaped against Counterpoint specifically. The PayCode taxonomy flexibility is treated as a feature — F surfaces whatever the customer has defined without normalization. Alternative-payment-rail integration (Zelle / Venmo / Lightning) is flagged as a Canary-native option, not bundled into the substrate path.

## L1 → L2 → L3 framework

```
L1 (Solution Map cell)         F = ● Full direct (Counterpoint tender / tax / gift card / Secure Pay surface — ~12 endpoints)
                                 │
L2 (Process areas)               ├── F.1  Tender taxonomy (PayCode)
                                 ├── F.2  Tax code surfacing
                                 ├── F.3  Gift card surface
                                 ├── F.4  Per-Document payment + tax flattening   (cross-cut with T)
                                 ├── F.5  Tokenization + Secure Pay (NSPTransaction)
                                 ├── F.6  AR ledger surfacing                     (cross-cut with R, J)
                                 └── F.7  Cross-module substrate contracts
                                 │
L3 (Functional processes)       (31 — enumerated per L2 below)
                                 │
L4 (Implementation detail)      Lives in SDDs + module specs
                                  (Canary-Retail-Brain/modules/F-finance.md,
                                   docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md §6.3)
```

## L4 implementation stubs

All L3 processes below are stub-pending at L4. Until an SDD section or module spec covers a process explicitly, treat the following as open:

| L3 ID | L4 stub |
|---|---|
| F.1.1 | → TBD: L4 implementation detail pending |
| F.1.2 | → TBD: L4 implementation detail pending |
| F.1.3 | → TBD: L4 implementation detail pending |
| F.1.4 | → TBD: L4 implementation detail pending |
| F.1.5 | → TBD: L4 implementation detail pending |
| F.2.1 | → TBD: L4 implementation detail pending |
| F.2.2 | → TBD: L4 implementation detail pending |
| F.2.3 | → TBD: L4 implementation detail pending |
| F.2.4 | → TBD: L4 implementation detail pending |
| F.3.1 | → TBD: L4 implementation detail pending |
| F.3.2 | → TBD: L4 implementation detail pending |
| F.3.3 | → TBD: L4 implementation detail pending |
| F.3.4 | → TBD: L4 implementation detail pending |
| F.3.5 | → TBD: L4 implementation detail pending |
| F.3.6 | → TBD: L4 implementation detail pending |
| F.4.1 | → TBD: L4 implementation detail pending |
| F.4.2 | → TBD: L4 implementation detail pending |
| F.4.3 | → TBD: L4 implementation detail pending |
| F.4.4 | → TBD: L4 implementation detail pending |
| F.4.5 | → TBD: L4 implementation detail pending |
| F.4.6 | → TBD: L4 implementation detail pending |
| F.5.1 | → TBD: L4 implementation detail pending |
| F.5.2 | → TBD: L4 implementation detail pending |
| F.5.3 | → TBD: L4 implementation detail pending |
| F.5.4 | → TBD: L4 implementation detail pending |
| F.5.5 | → TBD: L4 implementation detail pending |
| F.6.1 | → TBD: L4 implementation detail pending |
| F.6.2 | → TBD: L4 implementation detail pending |
| F.6.3 | → TBD: L4 implementation detail pending |
| F.6.4 | → TBD: L4 implementation detail pending |
| F.6.5 | → TBD: L4 implementation detail pending |

---

## F.1 — Tender taxonomy (PayCode)

**Purpose.** Counterpoint's `PayCode` is the customer-defined tender taxonomy. Every distinct tender (CASH, VISA, MC, AMEX, CHECK, AR, GIFTCARD, custom alternative-payment-rail entries) is a row. F surfaces the taxonomy at tenant bootstrap and re-syncs on cache invalidation.

**Companion cards.** `ncr-counterpoint-api-reference` § "Pay codes / tax", `ncr-counterpoint-endpoint-spine-map` § "Pay codes / tax — module F".

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| F.1.1 | PayCode list ingestion at tenant bootstrap | `GET /PayCodes` | **Cached server-side 24h**; `ServerCache: no-cache` for first poll of each cycle |
| F.1.2 | Per-PayCode detail enrichment | `GET /PayCode/{Paycode}` | Single-tender enrichment when a transaction surfaces an unknown PayCode |
| F.1.3 | PayCode update detection | `PUT /PayCode` write surface (rare for Canary; mostly tenant-side admin action) | Cache invalidation on update |
| F.1.4 | PayCode classification mapping per tenant | Canary-side tenant config: which PayCodes are CASH / CARD / AR / GIFT / ALT-WALLET / OTHER | Substrate for Q-TM-01 (cash-only register pattern) — needs to know which codes count as "cash" |
| F.1.5 | Alternative-payment-rail PayCode tagging | Per-tenant tagging of customer-defined PayCodes for Zelle / Venmo / Cash App / Lightning | Substrate for the Canary-native alt-payment-rail wedge per garden-center wiki § "Alternative payment rails" |

### User stories

- *As F, I want the PayCode taxonomy ingested at tenant bootstrap and refreshed daily, so Q's tender-mix rules always see the current set of defined tenders.*
- *As an Operator onboarding a new garden-center tenant in Owl, I want to map each PayCode to a classification (cash / card / AR / gift / alt-wallet / other) interactively, with auto-suggestion based on PayCode descriptors.*
- *As a Garden-Center Buyer who pays specialty growers via Zelle, I want to add a "ZELLE-VENDOR" PayCode in Counterpoint and have Canary recognize it as an alt-wallet vendor-payment tender, routing the resulting receivers correctly.*
- *As Q (Q-TM-01), I want the per-tenant cash-PayCode set available so cash-only register patterns are computed against the right tender denominator.*

## F.2 — Tax code surfacing

**Purpose.** Counterpoint's `TaxCodes` list defines the available tax-code rows. The actual tax application per transaction lives in the Document — `PS_DOC_TAX[]` carries multi-authority preservation per line (city + county + state stacked). F surfaces both the TaxCode list (config) and the per-Document tax detail (activity, via T cross-cut in F.4).

**Companion cards.** `ncr-counterpoint-api-reference` § "Pay codes / tax", `ncr-counterpoint-document-model` § "Taxes (`PS_DOC_TAX[]`)".

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| F.2.1 | TaxCode list ingestion at tenant bootstrap | `GET /TaxCodes` | **Cached server-side 24h**; `TX_COD` list |
| F.2.2 | Per-store default tax code surfacing | Cross-cut with N — `PS_STR_CFG_PS.AR_TAX_COD`, `DFLT_TAX_COD_METH` | Per-store tax code applied by default; substrate for Q-TC-01 mismatch rule |
| F.2.3 | Tax-exempt customer flag surfacing | Cross-cut with R — `AR_CUST.IS_TAX_EXEMPT` (or equivalent — **ASSUMPTION-R-06**) | Customer-side tax exemption flag; substrate for Q-TC-02 abuse rule |
| F.2.4 | Per-jurisdiction tax-authority enumeration per store | Derived from store's expected tax stack (e.g., MEMTN store should always have MEMPHIS + SHELBY + TN) | Substrate for Q-TC-01 (multi-authority mismatch detection) |

### User stories

- *As F, I want the TaxCode list refreshed daily and per-store default tax codes joined inline, so Q-TC-01 mismatch detection has both the expected and actual tax stacks available without round-trips.*
- *As an Operator, I want per-store expected-jurisdiction-stacks captured at onboarding (e.g., "Glendora store: LA + LA-COUNTY + CA"), so Q can flag tax-stack mismatches deterministically.*
- *As Q (Q-TC-02), I want tax-exempt customer status accessible per transaction so retail-pattern usage of exemption can pattern-detect.*

## F.3 — Gift card surface

**Purpose.** Counterpoint's GiftCard family covers issued gift cards (`GiftCard` / `GiftCards`) plus the gift-card code template (`GiftCardCode` / `GiftCardCodes` — the SKU-like entity for new gift-card issuance). F surfaces both. Per-Document gift-card activity (sale of new card, redemption of existing card) flows through T's Document polling (`PS_DOC_GFC[]`).

**Companion cards.** `ncr-counterpoint-api-reference` § "Gift card", `ncr-counterpoint-document-model` § "PS_DOC_GFC".

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| F.3.1 | GiftCard issued-card list ingestion | `GET /GiftCards` | Paginated; per-card balance + status |
| F.3.2 | Per-GiftCard detail enrichment | `GET /GiftCard/{GiftCardNo}` | `SY_GFC` lookup |
| F.3.3 | GiftCardCode template ingestion | `GET /GiftCardCodes` | Likely cached 24h (template metadata) |
| F.3.4 | Per-GiftCardCode detail | `GET /GiftCardCode/{GiftCardCode}` | `SY_GFC_COD` — code template |
| F.3.5 | Gift-card activity surfacing per Document | Cross-cut with T — `PS_DOC_GFC[]` flattened in T.3.x | Activity (sale, redemption, balance change) flows through Document polling |
| F.3.6 | Gift-card balance reconciliation | Per-card balance vs sum of all activity events | Substrate for Q-related balance-mismatch detection (gift-card abuse pattern) |

### User stories

- *As F, I want every issued gift card's balance available without per-query Counterpoint round-trips, so Owl analytics on gift-card outstanding-liability are fast.*
- *As Q, I want gift-card redemption activity correlated to the original card's issuance and prior activity, so over-redemption or balance-mismatch patterns are detectable.*
- *As a Garden-Center GM in Owl, I want to ask "what's our outstanding gift-card liability" and get a real-time number drillable to per-card detail.*

## F.4 — Per-Document payment + tax flattening (cross-cut with T)

**Purpose.** The actual payment and tax activity lives in `PS_DOC_PMT[]` and `PS_DOC_TAX[]` per Document. T's parser flattens both. F's role is to define the canonical shape these flatten into and the contracts that downstream consumers (Q, R, C) read against. **This L2 explicitly cross-cuts with T.3.4 (payment flattening) and T.3.5 (tax flattening) — the work happens in T's parser; F owns the contract.**

**Companion cards.** `ncr-counterpoint-document-model` § "Payments" + § "Taxes", `canary-module-t-functional-decomposition.md` T.3.4 + T.3.5.

### L3 processes

| ID | L3 process | Substrate (read by T, contract owned by F) | Notes |
|---|---|---|---|
| F.4.1 | Payment line preservation | `PS_DOC_PMT[]` flattened to `Events.payments` | Per-payment: PAY_COD, PAY_COD_TYP, AMT, HOME_CURNCY_AMT, CARD_IS_NEW, SWIPED, EDC_AUTH_FLG, currency, FX detail |
| F.4.2 | PII redaction at parse | `SIG_IMG`, `SIG_IMG_VECTOR` redacted in T.3.4; F asserts compliance | Signature images NEVER persisted; F's contract that R / Q / Owl never see them |
| F.4.3 | Multi-authority tax preservation | `PS_DOC_TAX[]` flattened with each `AUTH_COD` row preserved | City + county + state stacked, never summed at parse |
| F.4.4 | Apply-to instruction surfacing | `PS_DOC_PMT_APPLY[]` (sale vs AR-charge vs deposit) | Substrate for AR vs cash-sale distinction at the payment level |
| F.4.5 | Tender-mix aggregation per session | Substrate for Q-TM-01 (cash-only register pattern) | F provides the summing helper; Q applies the threshold |
| F.4.6 | Per-line tax allocation | `PS_DOC_LIN.TAX_AMT_ALLOC` joined to per-line tax | Substrate for line-level margin computation including tax |

### User stories

- *As F, I want every PII-sensitive payment field (`SIG_IMG`, raw PAN, raw CVV) confirmed redacted at the T-parser layer before it reaches CRDM, so F never has to filter in downstream queries.*
- *As Q (Q-TC-01), I want every Document's full multi-authority tax stack available in `Events.transaction_taxes` so jurisdiction-mismatch detection has the true breakdown, not a summed total.*
- *As Q (Q-TM-02), I want payment apply-to instructions available so a "card paid, then changed to cash" tender-swap pattern is detectable from `PS_DOC_PMT_APPLY` audit-log delta.*
- *As Owl, I want to answer "what's my tender mix this week by store" and get card / cash / AR / gift / alt-wallet split with per-store drilldown.*

## F.5 — Tokenization + Secure Pay (NSPTransaction)

**Purpose.** Counterpoint's Secure Pay tokenization surface is unique within the API — three of its endpoints (`POST /NSPTransaction`, `POST /Store/{StoreId}/Tokenize`, `GET /Store/{StoreId}/TokenizeInfo`) **don't require an APIKey** but require the registration option enabled. The card-on-file tokenization replaces raw PAN with a token; F surfaces the token + tokenization status, never the PAN.

**Companion cards.** `ncr-counterpoint-api-reference` § "Tokenization", `ncr-counterpoint-phase-0-context-brief` § "Three company-scoped endpoints don't require an APIKey".

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| F.5.1 | Per-store tokenization status check | `GET /Store/{StoreId}/Tokenize` | Status of tokenization on the store's cards-on-file; no APIKey, registration option required |
| F.5.2 | Per-store tokenization run trigger | `POST /Store/{StoreId}/Tokenize` | Tokenizes existing cards-on-file; rare operational action |
| F.5.3 | Aggregate tokenized count | `GET /Stores/Tokenized` | Cross-store summary |
| F.5.4 | NSPTransaction post-back receipt | `POST /NSPTransaction` (Monetra Secure Pay) | Receives Secure Pay transaction events; cross-cuts T's payment surface |
| F.5.5 | Card-on-file token surfacing | Customer cards-on-file via `AR_CUST_CARDS` (R cross-cut) | Token only; PAN never persisted in CRDM |

### User stories

- *As F, I want per-tenant tokenization status visible at a glance so customers operating Secure Pay see "all cards tokenized" or "N cards still pending tokenization" — the latter is a PCI-relevant gap.*
- *As Canary's Compliance Story, I want the tokenization-only contract enforced — F never persists PAN, F never even sees PAN past the parser layer.*
- *As an Operator triaging a card-related issue, I want to look up a card-on-file by token and see its tokenization status + last-charged-date + customer reference, without ever exposing the PAN.*

## F.6 — AR ledger surfacing (cross-cut with R, J)

**Purpose.** Counterpoint's AR ledger (`Customer_OpenItems` + customer-record AR fields) is technically a Customer endpoint but its semantics are finance-shaped — aging buckets, credit posture, collection workflows. F surfaces the AR ledger and provides the contracts that R (per-customer AR exposure), J (PO cost flow into AR), and C (B2B credit posture) read against.

**Companion cards.** `canary-module-r-functional-decomposition.md` § R.3.5 (R-side surface), `ncr-counterpoint-api-reference` § "Customer — Module R" § Customer_OpenItems.

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| F.6.1 | Per-customer open AR ingestion | `GET /Customer/{CustNo}/OpenItems` (R-shared endpoint) | AR aging by customer; current / 30 / 60 / 90+ buckets |
| F.6.2 | Customer credit posture surfacing | `AR_CUST.CR_RATE`, `NO_CR_LIM`, `BAL` (R cross-cut) | Substrate for B2B credit decisioning |
| F.6.3 | AR-vs-tender reconciliation per Document | Cross-cut with F.4.4 — `PS_DOC_PMT_APPLY[]` showing payment-applied-to-AR vs direct-sale | Reconciles AR receipts to outstanding invoices |
| F.6.4 | AR aging snapshot per period | Aggregated across customers; per `(department or store, period)` | Reporting + collection workflow substrate |
| F.6.5 | B2B credit-decisioning hooks | Per-customer credit-limit + current balance + open AR | Substrate for C (commercial / B2B classification — derived module) |

### User stories

- *As F, I want every B2B customer's open AR aging available without per-query Counterpoint round-trips, so collection workflows in Fox can prioritize without latency.*
- *As J, I want PO cost flow (committed receipts, realized receipts) reconciled against F's AR aging so the buying triangle (J + F + C) closes the loop.*
- *As Owl, I want to answer "which landscaper accounts are 60+ days overdue" and get a sorted list with per-customer drill-down to the open invoices.*
- *As an LP Analyst (Q.6 vertical pack), I want AR-customer status available so Q-TM-01 (cash-only register pattern) doesn't fire on stations that disproportionately serve AR-paying landscapers (where lower cash share is expected).*

## F.7 — Cross-module substrate contracts

**Purpose.** F supplies tender + tax + AR substrate to T (parse), Q (rules), R (AR view), J (cost flow), and C (B2B credit). This L2 is the contract registry. Symmetric to T.7 / R.6 / S.7 / J.8b.

### L3 contracts (registry)

| ID | Contract | Owner downstream | What F promises |
|---|---|---|---|
| F.7.1 | PayCode taxonomy availability | T (parse), Q (tender-mix rules) | Per-tenant PayCode list + classification mapping refreshed daily |
| F.7.2 | TaxCode list + per-store default | T (parse), Q (Q-TC-01 mismatch) | TaxCodes + per-store expected jurisdiction stack inline on every Document join |
| F.7.3 | Multi-authority tax preservation | Q (Q-TC-01) | `PS_DOC_TAX[]` rows preserved per authority; never summed at parse |
| F.7.4 | PII-redaction guarantee | All | `SIG_IMG`, raw PAN, raw CVV redacted at parser; F asserts non-presence in CRDM |
| F.7.5 | Gift-card balance + activity | Q (over-redemption rules), Owl (liability queries) | Per-card balance + activity stream available; balance-mismatch detectable |
| F.7.6 | Tokenization status per store | Operator (PCI compliance dashboard) | Tokenization count + per-card status surfaced |
| F.7.7 | AR aging per customer | R (R.3.5 surface), J (PO cost flow), C (B2B credit) | Open AR by customer, aging bucketed |
| F.7.8 | Per-Document apply-to instructions | Q (Q-TM-02 tender-swap detection) | `PS_DOC_PMT_APPLY[]` preserved per payment |
| F.7.9 | Alt-payment-rail PayCode tagging | Q (vendor-payment classification), Owl (alt-rail analytics) | Per-tenant alt-rail PayCode list available; substrate for the Canary-native option-(e) wedge |

### User stories

- *As F, I want every contract in F.7 enforced via the contract test suite, so a silent break (e.g., tax authorities accidentally summed) shows up at conformance test, not at first Q-TC-01 false-negative.*
- *As Q, I want to assert at boot that F surfaces all contracted fields including the per-store expected jurisdiction stack and the multi-authority preservation, so a contract break shows up at startup.*
- *As Canary's Compliance Story, I want the PII-redaction guarantee (F.7.4) audit-testable — periodic checks confirm `SIG_IMG` and raw PAN are not present anywhere in CRDM.*

## Counterpoint Endpoint Substrate

The following Counterpoint endpoints are the direct API surface for Module F's L3 processes. Each row maps to the CRDM entity F materializes and the L2 process area that owns it.

| Counterpoint Endpoint | CRDM Entity | L2 Process Area |
|---|---|---|
| PayCodes | PayCode registry | F.1 (Tender classification) |
| PayCode/{PayCode} | Individual PayCode | F.1 (PayCode detail) |
| TaxCodes | Tax code registry | F.2 (Tax classification) |
| GiftCards | Gift card registry | F.3 (Gift card lifecycle) |
| GiftCard/{GiftCardNo} | Individual gift card | F.3 (Balance / redemption) |
| GiftCardCodes | Gift card code registry | F.3 (Code validation) |
| Store/{StoreId}/Tokenize | PAN tokenization | F.5 (PII redaction) |
| Store/{StoreId}/TokenizeInfo | Token metadata | F.5 (Token audit) |
| NSPTransaction | NSP transaction log | F.5 (Network transaction substrate) |
| Customer/{CustNo}/OpenItems | AR open items | F.6 (AR aging) |
| AR_CUST | Customer AR master | F.6 (Credit posture) |
| PS_STR_CFG_PS | Store tax defaults | F.2 (Default tax-code context from N) |

---

## Assumptions requiring real-customer validation

| ID | Assumption | What it blocks | Resolution path |
|---|---|---|---|
| ASSUMPTION-F-01 | PayCode classification at customer level — which codes are CASH / CARD / AR / GIFT — is per-tenant config, no API enumeration | F.1.4 onboarding workflow | Per-customer at onboarding — engagement-knowable |
| ASSUMPTION-F-02 | Tax-exempt customer field name on `AR_CUST` (`IS_TAX_EXEMPT` assumed; mirrors ASSUMPTION-R-06) | F.2.3 substrate path; Q-TC-02 | Sandbox DB schema inspection |
| ASSUMPTION-F-03 | Per-store expected jurisdiction stack — captured at onboarding from store-tax-code config | F.2.4 substrate path; Q-TC-01 | Per-store at onboarding — engagement-knowable |
| ASSUMPTION-F-04 | NSPTransaction usage scope — most L&G customers may not have Secure Pay deployed; tokenization may be N/A | F.5 entire L2 priority | Customer interview — likely deferred unless Secure Pay confirmed |
| ASSUMPTION-F-05 | GiftCardCode template caching — assumed cached 24h alongside other config endpoints | F.3.3 cache discipline | API doc deep-read or sandbox |
| ASSUMPTION-F-06 | AR aging bucket granularity — Counterpoint may return current/30/60/90+ or finer | F.6.1 substrate completeness | Sandbox DB inspection |
| ASSUMPTION-F-07 | Alt-payment-rail PayCode customer adoption — most customers may not use it, but the Canary-native wedge depends on the surface being there | F.1.5 + F.7.9 priority | Customer interview |
| ASSUMPTION-F-08 | Apply-to instructions completeness — `PS_DOC_PMT_APPLY[]` may not be present on all Document types | F.4.4 substrate path; Q-TM-02 | Sandbox + sample Documents across types |
| ASSUMPTION-F-09 | Per-line tax allocation field — `PS_DOC_LIN.TAX_AMT_ALLOC` assumed; needs verification | F.4.6 substrate path | Sandbox sample Document inspection |

**Highest-leverage gaps:** F-01 (PayCode classification mapping) and F-03 (per-store expected jurisdiction stacks). Both are engagement-knowable only — every customer has unique conventions. Capture both at onboarding as part of the CATz Phase II To-Be Workshop output.

## Customer-specific overrides

*Empty until a real customer engagement starts. Format reserved:*

```
Customer: <name>
PayCode classification mapping:
  <PayCode value> | <CASH | CARD | AR | GIFT | ALT-WALLET | OTHER>
  ...
Alt-payment-rail PayCodes (if any):
  <PayCode> → <wallet name>
Per-store expected tax jurisdiction stacks:
  <STR_ID> | [<authority1>, <authority2>, <authority3>, ...]
Tax-exempt customer convention: <field name + value pattern>
Secure Pay deployed: <yes — N stores | no>
Tokenization status target: <100% / partial / N/A>
AR ledger active: <yes — typical aging buckets | no>
Disabled F.x processes (with reason):
  F.x.x: <reason>
ASSUMPTION resolutions:
  ASSUMPTION-F-NN: resolved as <answer>; source: <evidence>
  ...
```

## Additional user stories

The following user stories expand F's coverage across onboarding, override workflows, split-tender redemption, AR currency, and gift-card recovery scenarios. They supplement the per-L2 stories above.

- *As a store admin, I need to add a new PayCode during onboarding (after initial bootstrap) so that a non-standard tender type accepted at this location is properly classified from day one.*
- *As a cashier supervisor, I need to override the system-defaulted tax code on a specific line item so that a tax-exempt product sold with a regular receipt is correctly classified.*
- *As a customer, I need to apply a gift card to a purchase where the card balance is less than the purchase total so that the partial balance is applied and the remainder charged to another tender.*
- *As an accounts receivable manager, I need to view AR aging in local currency for a Canadian B2B customer so that I can assess credit posture without manual currency conversion.*
- *As a store manager, I need to reassign the balance from a lost or damaged gift card to a replacement card so that the customer's stored value is preserved.*

---

## Operating notes

**Cast of actors:**

| Actor | Role | Lives where |
|---|---|---|
| Tender Taxonomy Sync | PayCode ingester | Canary-internal (F.1) |
| Tax Code Sync | TaxCode ingester | Canary-internal (F.2) |
| Gift Card Sync | GiftCard ingester | Canary-internal (F.3) |
| Tokenization Status Monitor | Per-store Secure Pay status | Canary-internal (F.5) |
| AR Surface | Per-customer AR ledger projection | Canary-internal (F.6) |
| Operator | F config + onboarding | Canary side |
| Owl / Fox | Analyst-facing surface | Canary-internal |

**F is an unusually cross-cut module.** F.4 explicitly cross-cuts with T (where the parsing actually happens — F owns the contract, not the parser). F.6 cross-cuts with R (Customer_OpenItems is a Customer endpoint by URL but a Finance concern by semantics). Both cross-cuts are intentional — modules-by-semantics, not modules-by-endpoint-URL.

**The PayCode taxonomy flexibility is a feature.** Counterpoint customers can define any tender they want. F preserves the customer's taxonomy verbatim and lets per-tenant classification mapping (F.1.4) layer the meaning on top. This is what enables the alternative-payment-rail wedge (F.1.5 / F.7.9) — Zelle / Venmo / Lightning fit naturally as customer-defined PayCodes.

**Three Secure Pay endpoints have unique auth.** `POST /NSPTransaction`, `POST /Store/{StoreId}/Tokenize`, `GET /Store/{StoreId}/TokenizeInfo` don't require an APIKey but do require the registration option. T.1.5 auth injection has to know about this exception per endpoint family.

## Related

- `Canary-Retail-Brain/modules/F-finance.md` — L1 canonical spec
- `canary-module-f-finance.md` — L2 Canary code/schema crosswalk
- `canary-module-q-functional-decomposition.md` — sister card; F.2.4 + F.4 + F.7.x drive Q-TM and Q-TC rule families
- `canary-module-t-functional-decomposition.md` — sister card; T.3.4 + T.3.5 (parsing) implements F.4 contracts
- `canary-module-r-functional-decomposition.md` — sister card; R.3.4 + R.3.5 (AR-customer + AR aging surface) reads from F.6
- `canary-module-j-functional-decomposition.md` — sister card; J.6.4 (cost reconciliation) and J.8.5 (PO recommendation as substrate) bridge with F's AR posture
- `ncr-counterpoint-api-reference.md` — full PayCode / TaxCode / GiftCard / Tokenization detail
- `ncr-counterpoint-document-model.md` — `PS_DOC_PMT[]` + `PS_DOC_TAX[]` + `PS_DOC_GFC[]` substrate
- `ncr-counterpoint-endpoint-spine-map.md` — per-endpoint × CRDM × spine map for F family
- `ncr-counterpoint-rapid-pos-relationship.md` — multi-tier tender + multi-authority tax mapping
- `garden-center-operating-reality.md` — alt-payment-rail wedge context, multi-tier tender mix
- `rapid-pos-counterpoint-user-pain-points.md` — eCommerce sync + payment-terminal pain themes
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — F row = ● Full direct
- (CATz) `method/artifacts/module-functional-decomposition.md` — the artifact template this card follows

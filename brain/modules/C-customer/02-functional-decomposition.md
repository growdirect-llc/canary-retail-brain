---
title: R — Functional Decomp
classification: internal
type: wiki
sub-type: module-functional-decomposition
date: 2026-04-25
last-compiled: 2026-04-25
status: draft v1 (archetype — no real customer engagement)
module: R
solution-map-cell: ● Full direct (Counterpoint Customer family — 17 endpoints; the best-covered domain in the API)
companion-modules: [T, Q, P, C, F, N]
companion-substrate: [ncr-counterpoint-api-reference.md, ncr-counterpoint-endpoint-spine-map.md]
companion-context: [garden-center-operating-reality.md, ncr-counterpoint-rapid-pos-relationship.md]
companion-canary-spec: Canary-Retail-Brain/modules/C-customer.md
companion-catz: CATz/proof-cases/specialty-smb-counterpoint-solution-map.md
methodology-note: "Sister card to canary-module-q-functional-decomposition.md and canary-module-t-functional-decomposition.md. Same template; same L1→L4 framework. R inherits T's customer-reference upserts (T.7.7) and feeds Q's tier-aware allow-lists (Q.6) and P-derived multi-tier pricing observations."
---

# Module C (Customer) — Functional Decomposition

> **Artifact layer.** Third of three Canary module artifact layers:
> 1. **Canonical spec** (vendor-neutral) — `Canary-Retail-Brain/modules/C-customer.md`
> 2. **Code/schema crosswalk** (Canary-specific) — `Brain/wiki/canary-module-c-customer.md` *(planned for Q/T/R; exists for J/P/F/C)*
> 3. **Functional decomposition** (Counterpoint-substrate-aware, L2/L3 + user stories) — *this card*

## Governing thesis

R owns the **People entity** in CRDM, specifically the customer subset. Counterpoint exposes the richest People surface of any spine module — **17 endpoints** covering AR_CUST + addresses + notes + cards + open AR + control + workgroup-driven defaults — and adds two capabilities Square has no equivalent for: **multi-tier pricing identity** (`AR_CUST.CATEG_COD`) and **embedded loyalty** (12 LOY_* fields per customer). For a Lawn & Garden tenant specifically, the multi-tier identity is the load-bearing feature: every Q rule that distinguishes wholesale from retail behavior depends on R, every P-derived pricing observation depends on R, every C-derived B2B classification depends on R.

R holds a deliberate **inversion of the dominant industry default**: the Canary v1 spec stores no PII at rest. Counterpoint, by contrast, holds full PII (name, email, phone, address, card-on-file, AR ledger, loyalty history). R's Counterpoint posture must reconcile these two: the Canary-side privacy commitment AND the Counterpoint-side full customer record. The reconciliation is **read-through-to-Counterpoint at query time**, not "ingest everything Counterpoint knows."

R is **● Full direct** in every Counterpoint Solution Map cell, but the cell hides three real architectural decisions: (1) multi-company-per-tenant customer namespace handling, (2) the privacy-posture reconciliation just described, and (3) tier-code conventions that vary per-VAR and per-customer (every Counterpoint deployment uses CATEG_COD differently — there is no universal taxonomy).

## Counterpoint Endpoint Substrate

| Counterpoint Endpoint | CRDM Entity | L2 Process Area |
|---|---|---|
| AR_CUST | Customer master | C.1 (Customer identity), C.5 (Credit posture) |
| Customer/{CustNo}/OpenItems | Open AR items | C.3 (AR aging), C.4 (Payment history) |
| AR_CUST_CTL | Credit control | C.5 (Credit limit / tier) |
| PS_DOC_HDR (customer-linked) | Transaction headers | C.2 (Behavioral pattern), C.3 (Purchase history) |
| AR_CUST.IS_TAX_EXEMPT | Tax exemption flag | C.1 (Customer tax classification — sourced to F.2) |

## Executive summary

| Dimension | Count | Source |
|---|---|---|
| L2 process areas | 6 | This card |
| L3 functional processes | 32 | This card |
| Counterpoint endpoints in R's path | 17 (Customer family) | API reference |
| AR_CUST loyalty fields | 12 | API reference + relationship wiki |
| Garden-center tier conventions enumerated | 5 (walk-in, member, landscaper, project, wholesale) | garden-center-operating-reality |
| Privacy-posture L3 processes | 4 | Q.4 |
| Substrate contracts R owes downstream | 8 | This card §C.6 |
| Assumptions requiring real-customer validation | 9 | Tagged `ASSUMPTION-R-NN` |
| User stories enumerated | 47 | Observer-perspective; actor ∈ {Registry, Projection, Owl, Fox, Operator, Store GM, LP Analyst} |

**Posture:** archetype-shaped against Counterpoint specifically. The privacy-first v1 design (no PII at rest) is preserved. Per-VAR tier-code variance is acknowledged as a discovery surface at every customer onboarding — there is no universal `CATEG_COD` mapping.

## L1 → L2 → L3 framework

```
L1 (Solution Map cell)         R = ● Full direct (Counterpoint Customer family — 17 endpoints)
                                 │
L2 (Process areas)               ├── C.1  Customer registry & upsert
                                 ├── C.2  Tier identity & multi-tier pricing context
                                 ├── C.3  Loyalty + AR ledger surfacing
                                 ├── C.4  Privacy posture (no PII at rest)
                                 ├── C.5  Identity resolution (cross-company, future cross-vendor)
                                 └── C.6  Investigator surface + downstream contracts
                                 │
L3 (Functional processes)       (32 — enumerated per L2 below)
                                 │
L4 (Implementation detail)      Lives in SDDs + module specs
                                  (Canary-Retail-Brain/modules/C-customer.md,
                                   docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md §6.2)
```

## C.1 — Customer registry & upsert

**Purpose.** Maintain one row per merchant per Counterpoint customer (per company alias, for multi-company tenants). T's parsed transaction stream triggers shell-row upserts before R has polled the Customer endpoint; R catches up async. The registry is the FK target every other module depends on for People references.

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| C.1.1 | Shell-row upsert from T's reference | T's `transaction.created` carrying `CUST_NO` | Triggered before R has polled the customer record; row created with `CUST_NO`, `merchant_id`, `company_alias`, `db_status='pending_enrichment'` → TBD: L4 implementation detail pending |
| C.1.2 | Full-row enrichment from `GET /Customer/{CustNo}` | `AR_CUST` + nested `AR_CUST_NOTE` / `AR_SHIP_ADRS` / `AR_CUST_CARDS` | Called when shell row needs enrichment OR on poll cadence → TBD: L4 implementation detail pending |
| C.1.3 | Incremental sync via `GET /Customers` | `RS_UTC_DT`-filtered paginated workhorse | Counterpoint-recommended incremental path; respects watermark per `(tenant, company_alias)` → TBD: L4 implementation detail pending |
| C.1.4 | EC-flagged customer enrichment | `GET /Customers/EC` | Online-customer subset; same registry, separate poll cadence → TBD: L4 implementation detail pending |
| C.1.5 | CustomerControl read at tenant bootstrap | `GET /CustomerControl` | Tier definitions + loyalty enable + customer-default fields; **cached server-side 24h**; T.1.7 cache discipline applies → TBD: L4 implementation detail pending |
| C.1.6 | Workgroup template read | `GET /Workgroup/{WorkgroupID}` | Numbering defaults + tier defaults that drive `POST /Customer` from the Counterpoint side → TBD: L4 implementation detail pending |
| C.1.7 | Soft-delete on customer archival | `db_status='archived'` rather than DELETE | Preserves audit trail; re-activated on return, never duplicated → TBD: L4 implementation detail pending |
| C.1.8 | Multi-company namespace isolation | Per-`(tenant_id, company_alias)` registry partition | One Canary tenant with N Counterpoint companies has N independent customer namespaces — never bleed across → TBD: L4 implementation detail pending |

### User stories

- *As R, I want T's `CUST_NO` references to immediately upsert a shell row so transaction events never reference unknown customers, even if the Customer endpoint hasn't been polled yet.*
- *As R, I want the `GET /Customers` incremental poll to respect a per-`(tenant, company_alias)` watermark so I never re-fetch already-consumed customers and never miss a customer modified during my last cycle.*
- *As an Operator in Owl, I want to ask "which customer references are still in shell-row state for tenant X" and get an enrichment-lag report so stale references surface before they break downstream queries.*
- *As an Operator at a multi-company tenant, I want CUST_NO=12345 in `companyA` and CUST_NO=12345 in `companyB` to be unambiguously different customers in R, with the company alias preserved in every join key.*

## C.2 — Tier identity & multi-tier pricing context

**Purpose.** This is the load-bearing L&G capability. Counterpoint's `AR_CUST.CATEG_COD` is the multi-tier pricing identity field; for a garden-center tenant, the typical taxonomy is `RETAIL / MEMBER / LANDSCAPER / PROJECT / WHOLESALE`. Q.2.9 (customer-tier abuse), Q.6.x vertical-pack tier-aware allow-lists, and P-derived multi-tier pricing observations all depend on R surfacing the tier cleanly.

**No universal taxonomy.** Every Counterpoint deployment uses `CATEG_COD` differently. Per-VAR conventions vary; per-customer conventions vary within a VAR. This L2 surfaces the field; tier-meaning interpretation is a per-tenant configuration that gets captured at onboarding (see ASSUMPTION-R-03).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| C.2.1 | Surface `CATEG_COD` per customer | `AR_CUST.CATEG_COD` | Preserved verbatim; no normalization (different tenants use different code conventions) → TBD: L4 implementation detail pending |
| C.2.2 | Tier-code → tier-meaning mapping per tenant | Tenant config table; populated at onboarding | E.g., `WHL → wholesale`, `LSC → landscaper`, `MBR → member`, `RET → retail` → TBD: L4 implementation detail pending |
| C.2.3 | Tier-change audit on customer record | `AR_CUST.LST_MAINT_DT` + `LST_MAINT_USR_ID` deltas | Substrate for Q.2.9 (Q-CT-02 pre-purchase tier upgrade rule) → TBD: L4 implementation detail pending |
| C.2.4 | Multi-tier pricing flag surfacing | `AR_CUST_CTL` (CustomerControl) multi-tier flags | Substrate for P-derived pricing rule observations → TBD: L4 implementation detail pending |
| C.2.5 | Open-AR balance per customer | `GET /Customer/{CustNo}/OpenItems` | AR aging; substrate for C-derived B2B classification + Q-TC-02 (tax-exempt abuse adjacent) → TBD: L4 implementation detail pending |
| C.2.6 | Customer credit posture | `AR_CUST.CR_RATE`, `NO_CR_LIM`, `BAL` | Substrate for C and risk-adjacent rules → TBD: L4 implementation detail pending |
| C.2.7 | B2B vs retail derivation hooks | Pattern-detect over C.2.1 + C.2.5 + transaction shape | Feeds C-derived B2B classification; the C module is "derived from R" per Solution Map → TBD: L4 implementation detail pending |

### User stories

- *As Q.2.9, I want every customer's tier code (`CATEG_COD`) and its tenant-specific meaning available on every transaction join, so the wholesale-on-retail-pattern rule fires correctly across tenants with different code conventions.*
- *As Q.2.9, I want tier-change events on a customer record exposed as their own substrate (`C.2.3`) so the pre-purchase tier-upgrade rule can correlate against transaction timestamps.*
- *As an LP Analyst at a garden center, I want to see the per-customer history "RET → LSC → WHL" with audit timestamps when investigating a tier-abuse case, so legitimate sales-rep promotions are visible.*
- *As an Operator onboarding a Counterpoint tenant in Owl, I want to declare the tier-code → tier-meaning mapping interactively, with auto-suggested mappings inferred from the customer's existing AR_CUST data.*
- *As C (the derived B2B module), I want the union of `AR_CUST.CATEG_COD ∈ wholesale-tier-set` plus `AR_CUST.NO_CR_LIM > 0` plus `OpenItems` non-empty to identify B2B customers without reaching into Counterpoint twice.*

## C.3 — Loyalty + AR ledger surfacing

**Purpose.** Counterpoint embeds 12 loyalty fields per customer (`LOY_PGM_COD`, `LOY_PTS_BAL`, `LOY_CARD_NO`, etc.) plus a full AR ledger via `Customer_OpenItems`. R surfaces both as substrate without persisting PII; loyalty + AR shape feeds C.6 contracts to downstream modules (Q for velocity rules, F for AR-vs-tender reconciliation, future C for B2B account behavior).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| C.3.1 | Surface loyalty enrollment | `AR_CUST.LOY_PGM_COD` + `LOY_CARD_NO` (existence flags only — not card values) | R stores the enrolled-yes/no flag, not the card number → TBD: L4 implementation detail pending |
| C.3.2 | Surface loyalty balance | `AR_CUST.LOY_PTS_BAL` (numeric only) | Integer; safe to persist; substrate for repeat-purchase detection → TBD: L4 implementation detail pending |
| C.3.3 | Surface loyalty redemption events | Document line items with loyalty-redemption indicator | Substrate for Q-related redemption-pattern rules; loyalty redemption captured in T's transaction stream → TBD: L4 implementation detail pending |
| C.3.4 | Surface AR-customer flag | `AR_CUST.IS_AR_CUST` or equivalent (**ASSUMPTION-R-04**) | Distinguishes AR-charge-eligible customers from cash-only → TBD: L4 implementation detail pending |
| C.3.5 | Surface open AR aging | `Customer_OpenItems` aging buckets | Substrate for F (AR collection workflows downstream) and C (B2B credit posture) → TBD: L4 implementation detail pending |
| C.3.6 | AR-charge-vs-cash transaction posture | Pattern-detect over C.3.4 + transaction tender mix | Feeds Q-TM-01 (cash-only register pattern) — wholesale customers paying AR shift expected tender mix → TBD: L4 implementation detail pending |

### User stories

- *As R, I want loyalty enrollment and balance surfaced as integer-shape substrate so downstream rules can pattern-match without R ever persisting PII.*
- *As Q, I want loyalty redemption events available alongside transaction events so redemption-pattern rules (over-redemption per session, redemption-then-refund pattern) can fire.*
- *As F, I want per-customer open AR aging (current / 30 / 60 / 90+) available without joining back to Counterpoint, so AR collection workflows can run from CRDM.*
- *As an LP Analyst at a garden center, I want loyalty redemption activity per cashier per session visible — loyalty-redemption-then-refund is a known fraud pattern in retail.*

## C.4 — Privacy posture (no PII at rest)

**Purpose.** R is the most architecturally opinionated module: **the v1 implementation deliberately stores no PII at rest**. Names, emails, phone numbers, addresses are intentionally not in R's tables. Counterpoint holds them; Canary reads at query time when the workflow demands it. This L2 owns that posture and the schema enforcement that makes it structural, not procedural.

**Why this matters for Counterpoint.** Square's customer surface is lighter. Counterpoint's `AR_CUST` carries deep PII (name, email, phone, multiple ship-to addresses, card-on-file, AR ledger, loyalty history). The naive integration would ingest all of it. R deliberately doesn't.

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| C.4.1 | Schema-enforced PII absence | `customers` table has no string columns for personal data | Hard constraint at the DDL layer; can't be bypassed at application layer → TBD: L4 implementation detail pending |
| C.4.2 | Read-through to Counterpoint at query time | When workflow demands name / email / address: parser fetches from `GET /Customer/{CustNo}` per request | No caching beyond request scope; never persisted → TBD: L4 implementation detail pending |
| C.4.3 | Card-fingerprint storage (opaque) | `card_profiles` holds Counterpoint's tokenized fingerprint (`AR_CUST_CARDS` token) | Token, not PAN; not reversible in Canary → TBD: L4 implementation detail pending |
| C.4.4 | PII-redaction-at-parse contract | T.3.4 + T.7.10 redact `SIG_IMG`, `SIG_IMG_VECTOR`, raw PAN; R asserts compliance | R never receives those bytes; T-side redaction is pre-condition → TBD: L4 implementation detail pending |
| C.4.5 | GDPR/CCPA right-to-be-forgotten | Soft-delete on R + vendor-side deletion request | Single soft-delete suffices on Canary side; vendor (Counterpoint) handles its own → TBD: L4 implementation detail pending |
| C.4.6 | Profile-extension opt-in (future / per-merchant flag) | Per-tenant feature flag + extension table | Default off; enabling requires explicit data-handling agreement; out of v1 → TBD: L4 implementation detail pending |

### User stories

- *As Canary's Compliance Story, I want the schema itself to enforce no-PII-at-rest in R, so a future engineer cannot accidentally introduce a name column without an explicit migration that triggers compliance review.*
- *As R, I want every read-through to Counterpoint to be request-scoped and never cached — the query returns the data, the data evaporates from Canary.*
- *As an LP Analyst investigating a case in Fox, I want customer name + contact info displayed in the case view by reading-through to Counterpoint at click time, with the read audit-logged so privacy review can prove no bulk extraction.*
- *As Canary's Product Owner, I want a profile-extension opt-in path that explicitly requires a data-handling agreement, so customers who genuinely need first-party PII storage have a path that's not ad-hoc.*
- *As an Auditor, I want to confirm that a full database exfiltration of R yields only opaque IDs and integer aggregates — re-identification requires also breaching Counterpoint.*

## C.5 — Identity resolution (cross-company, future cross-vendor)

**Purpose.** A single Canary tenant may run multiple Counterpoint companies (multi-company-per-tenant is real) and may eventually run Square-in-store + Counterpoint-online (cross-vendor). Today: per-`(tenant, company_alias)` namespaces are independent. v2: explicit identity resolution surface for cross-namespace customers.

### L3 processes

| ID | L3 process | Scope | Notes |
|---|---|---|---|
| C.5.1 | Per-`(tenant, company_alias)` namespace isolation | Counterpoint multi-company today | Same as C.1.8; no auto-merge across companies → TBD: L4 implementation detail pending |
| C.5.2 | `external_identities` link table | Cross-namespace identity scaffold | Exists in Canary already (per GRO-267); links opt-in, never auto-derived → TBD: L4 implementation detail pending |
| C.5.3 | Manual identity link surface | Operator MCP tool | "Link Counterpoint customer X in companyA to Counterpoint customer Y in companyB"; audit-logged, soft-revocable → TBD: L4 implementation detail pending |
| C.5.4 | Cross-vendor identity resolution (v2) | Square + Counterpoint same-customer matching | Matching policy undecided: deterministic (email match) / probabilistic / customer-confirmed; out of v1 → TBD: L4 implementation detail pending |
| C.5.5 | Customer-side ID assertion (future) | Customer logs into Canary-merchant portal, asserts identity link | Future surface; out of v1 → TBD: L4 implementation detail pending |

### User stories

- *As R, I want cross-company customer references treated as independent until an Operator explicitly links them, so multi-company tenants don't get accidental customer merges from same `CUST_NO` collision.*
- *As an Operator at a multi-company garden-center chain in Owl, I want to manually link two Counterpoint customer records (e.g., a landscaper who shops at both `armstrong-glendora` and `armstrong-irvine` companies) with one MCP call, audit-logged.*
- *As Canary's Product Owner, I want cross-vendor identity resolution explicitly punted to v2 with a documented matching-policy decision required before build — getting this wrong silently merges different customers and has GDPR consequences.*

## C.6 — Investigator surface + downstream contracts

**Purpose.** R outputs feed two surfaces: (1) read-only customer queries from Owl/Fox/Operator MCP tools, and (2) substrate contracts to downstream modules. **This L2 is symmetric to T.7 — same producer-view-of-contracts pattern.**

### L3 processes (investigator surface)

| ID | L3 process | Surface | Actor |
|---|---|---|---|
| C.6.1 | Customer lookup by `CUST_NO` | `canary-identity` MCP tool, read-only | LP Analyst, Investigator → TBD: L4 implementation detail pending |
| C.6.2 | Customer lookup by card fingerprint | Same MCP, opaque token only | Investigator → TBD: L4 implementation detail pending |
| C.6.3 | Customer transaction history projection | LTV / count / temporal bounds; aggregates derived from T | LP Analyst, Store GM → TBD: L4 implementation detail pending |
| C.6.4 | Owl natural-language Q&A over customers | "Show me top wholesale customers by YTD revenue" | Store GM, Exec → TBD: L4 implementation detail pending |
| C.6.5 | Read-through-to-Counterpoint for PII-bearing fields | At click time in Fox case view | Investigator (audit-logged) → TBD: L4 implementation detail pending |
| C.6.6 | Cohort projection (segment-by-tier, segment-by-LTV) | Aggregates from C.2 + C.3 | Marketing-adjacent (out of v1, deferred to v3) → TBD: L4 implementation detail pending |

### L3 contracts (substrate registry — symmetric to T.7)

| ID | Contract | Owner downstream | What R promises |
|---|---|---|---|
| C.6.7 | Tier code surfaced verbatim | Q (Q.2.9), C (derived) | `AR_CUST.CATEG_COD` preserved exactly; tier-meaning mapping available per-tenant → TBD: L4 implementation detail pending |
| C.6.8 | Tier-change audit | Q (Q-CT-02) | Tier deltas with timestamp + actor available as event substrate → TBD: L4 implementation detail pending |
| C.6.9 | Loyalty enrollment + balance | Q, repeat-purchase rules | Integer balance + enrolled flag; no card numbers → TBD: L4 implementation detail pending |
| C.6.10 | Open AR aging buckets | F, C | Per-customer aging without round-trip to Counterpoint → TBD: L4 implementation detail pending |
| C.6.11 | Multi-tier pricing flag | P (derived) | `AR_CUST_CTL` multi-tier indicators surfaced for pricing-rule observation → TBD: L4 implementation detail pending |
| C.6.12 | Tax-exempt customer flag | Q (Q-TC-02) | `AR_CUST.IS_TAX_EXEMPT` or equivalent (**ASSUMPTION-R-06**) surfaced as boolean → TBD: L4 implementation detail pending |
| C.6.13 | Customer-namespace attribution | All | Every R reference carries `(tenant_id, company_alias)` — never bleed across companies → TBD: L4 implementation detail pending |
| C.6.14 | PII-absence guarantee | All | Downstream consumers cannot pull PII from R; must read-through to Counterpoint via C.4.2 with audit → TBD: L4 implementation detail pending |

### User stories

- *As an LP Analyst in Fox, I want to look up a customer by `CUST_NO` and see their tier, LTV, transaction count, AR balance, and loyalty status — without needing PII to investigate a case.*
- *As an LP Analyst, I want to click through to "show contact info" only when I need to actually contact the customer, with the read audit-logged for compliance review.*
- *As Q (Q.6.x vertical pack), I want to assert at boot that R surfaces tier code, tier-meaning mapping, AR aging, and tax-exempt flag for the active tenant — failing fast if the substrate contract is broken.*
- *As a Store GM in Owl, I want to ask "show me wholesale customers I haven't seen in 60 days" and get a per-customer drilldown without leaving the conversation.*
- *As Marketing (deferred v3), I want cohort projections by tier × LTV available as a queryable surface — but only when the profile-extension opt-in (C.4.6) is enabled and the data-handling agreement is in place.*

## Canary Detection Hooks

| R Process | → Detection Surface | Signal Description |
|---|---|---|
| C.2 (Behavioral pattern routing) | Q-IS rule family | Customer behavioral anomalies (velocity spikes, unusual return patterns, cross-location activity) are published as Q-IS accumulation signals |
| C.5.3 (Cross-company customer collision) | Q-DM-03 | Customers detected under multiple company IDs with shared PAN or contact data are flagged to Q-DM-03 for identity-manipulation review |
| C.4 (Payment history) | Q-TM rule family | Unusual payment velocity or tender-mix for a known customer feeds Q-TM tender-monitoring rules |

## Additional User Stories

- *As a loss prevention analyst, I need to detect when the same customer appears under two different company IDs with matching contact information so I can investigate potential account manipulation.*
- *As a store manager, I need customer profile extensions (loyalty tier, spend band) to be available in Canary reporting even before v3 enrichment, so I can filter investigation queues by customer segment.*

## Assumptions requiring real-customer validation

These markers exist because the answer requires either a Rapid Garden POS sandbox database, a real customer's `AR_CUST` corpus, or both.

| ID | Assumption | What it blocks | Resolution path |
|---|---|---|---|
| ASSUMPTION-R-01 | `CUST_NO` cardinality across companies — same value in companyA and companyB are different customers (assumed) | C.1.8, C.5.1 namespace isolation correctness | Sandbox multi-company test or docs confirmation |
| ASSUMPTION-R-02 | "CASH" sentinel `CUST_NO` — Counterpoint convention for non-customer transactions | C.1.1 shell-row upsert filtering (don't create CASH customer rows) | Sandbox DB inspection — confirm sentinel value(s) |
| ASSUMPTION-R-03 | Per-customer tier-code conventions — `CATEG_COD` value meanings (`WHL`, `LSC`, `RET` etc.) vary per VAR / per customer | C.2.2 (tier-meaning mapping); every tier-aware Q rule | Per-tenant onboarding discovery; no universal answer |
| ASSUMPTION-R-04 | AR-customer flag field name — `AR_CUST.IS_AR_CUST` assumed; not directly visible in current sample | C.3.4 substrate path | Sandbox DB schema inspection |
| ASSUMPTION-R-05 | Loyalty enrollment indicators — which of the 12 LOY_* fields are the boolean enrollment vs balance vs card | C.3.1, C.3.2 surface decisions | Sandbox sample data + AR_CUST schema docs |
| ASSUMPTION-R-06 | Tax-exempt customer field name — likely `IS_TAX_EXEMPT` or via `TAX_COD = NOTAX`; needs confirmation | C.6.12 contract; Q-TC-02 substrate | Sandbox DB inspection |
| ASSUMPTION-R-07 | EC (eCommerce) customer relationship — is `GET /Customers/EC` a filter view of `GET /Customers` or a separate table | C.1.4 vs C.1.3 implementation | Sandbox endpoint inspection |
| ASSUMPTION-R-08 | Workgroup customer-template scope — does Workgroup affect customer reads or only customer creation defaults | C.1.6 — may or may not be in steady-state read path | Documentation read or sandbox test |
| ASSUMPTION-R-09 | Multi-name plant convention impact on R — none expected (item-side, not customer-side), but flagged in case Rapid POS extends customer record with garden-specific fields | C.4.1 schema-enforced PII absence — extensions could violate without explicit migration | Per-customer at onboarding |

**Highest-leverage gaps:** R-03 (tier-code conventions) — load-bearing for every L&G-distinctive Q rule. Cannot be assumed at platform level; must be discovered per-tenant. Capture as part of CATz Phase II To-Be Workshop output.

## Customer-specific overrides

*Empty until a real customer engagement starts. Format reserved:*

```
Customer: <name>
Counterpoint deployment: <single-company | multi-company (N companies)>
Company aliases: [<alias1>, <alias2>, ...]
Tier-code mapping (C.2.2):
  CATEG_COD value | meaning
  ---             | ---
  WHL             | wholesale
  LSC             | landscaper
  MBR             | member
  RET             | retail
  PRJ             | project (one-time landscape)
  ...
Loyalty program in use: <yes — program name | no>
Loyalty enrollment field convention: <which LOY_* field>
AR ledger active: <yes | no>
Tax-exempt convention: <field name + value convention>
Profile-extension opt-in: <off — default | on — DPA reference>
Disabled R.x processes (with reason):
  R.x.x: <reason>
ASSUMPTION resolutions:
  ASSUMPTION-R-NN: resolved as <answer>; source: <evidence>
  ...
Manual identity links (C.5.3):
  <link entry list>
```

## Operating notes

- R inherits T.7.7 (T's customer-reference upsert contract) — every transaction reference upserts a shell row in R before the transaction event publishes. R's C.1.1 is the receiver of T.7.7. The two contracts must stay symmetric; drift between them silently breaks downstream joins.
- R is the **substrate provider for two derived modules** (P-derived multi-tier pricing, C-derived B2B classification) per the Solution Map. The L3 processes in C.2 and C.3 are explicitly designed to surface fields those derivations need.
- The privacy-first posture (C.4) is a **deliberate inversion** of the dominant industry default. It is a marketable property of the platform, not just a technical choice. Customers who genuinely need first-party PII opt in via C.4.6 with a documented data-handling agreement; default is off.
- Tier-code conventions (ASSUMPTION-R-03) are load-bearing AND not platform-knowable. Every customer engagement needs explicit tier-mapping discovery during CATz Phase II To-Be Workshops. This is a methodology hook as much as an engineering one.

## Related

- `Canary-Retail-Brain/modules/C-customer.md` — module-level architectural spec (CRDM, BSTs, schema, agent surface, security posture); referenced throughout
- `canary-module-q-functional-decomposition.md` — sister card; C.6.7-C.6.12 contracts are consumed by Q.1 + Q.2.9 + Q.6
- `canary-module-t-functional-decomposition.md` — sister card; T.7.7 (customer-ref upsert) is the producer-side of C.1.1
- `ncr-counterpoint-api-reference.md` — full Customer family (17 endpoints) detail; CustomerControl semantics; cached-data discipline
- `ncr-counterpoint-endpoint-spine-map.md` — per-endpoint × CRDM × spine map for Customer family
- `ncr-counterpoint-rapid-pos-relationship.md` — feature-to-API mapping (multi-tier pricing → CATEG_COD; loyalty → 12 LOY_* fields); referenced in C.2 and C.3
- `garden-center-operating-reality.md` — customer-tier reality for L&G (walk-in / member / landscaper / project / wholesale); referenced in C.2
- `rapid-pos-counterpoint-user-pain-points.md` — pricing-rules complexity, customer-tier handling pain themes
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — R row = ● Full direct; this card is the L2/L3 expansion of that cell
- (CATz, proposed) `method/artifacts/module-functional-decomposition.md` — the artifact template this card proves out alongside Q and T

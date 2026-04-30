---
classification: internal
type: wiki
sub-type: module-functional-decomposition
date: 2026-04-25
last-compiled: 2026-04-25
status: draft v1 (archetype — no real customer engagement)
module: T
solution-map-cell: ● Full direct (Counterpoint Document family — 11 endpoints)
companion-modules: [R, N, S, F, D, J, Q]
companion-substrate: [ncr-counterpoint-document-model.md, ncr-counterpoint-api-reference.md, ncr-counterpoint-endpoint-spine-map.md]
companion-context: [garden-center-operating-reality.md, ncr-counterpoint-rapid-pos-relationship.md]
companion-canary-spec: Canary-Retail-Brain/modules/T-transaction-pipeline.md
companion-catz: CATz/proof-cases/specialty-smb-counterpoint-solution-map.md
methodology-note: "Sister card to canary-module-q-functional-decomposition.md. Same template; same L1→L4 framework. T and Q are tightly coupled — T's substrate contracts to Q drive most of T.7."
---

# Module T (Transaction Pipeline) — Functional Decomposition

> **Artifact layer.** Third of three Canary module artifact layers:
> 1. **Canonical spec** (vendor-neutral) — `Canary-Retail-Brain/modules/T-transaction-pipeline.md`
> 2. **Code/schema crosswalk** (Canary-specific) — `Brain/wiki/canary-module-t-transaction-pipeline.md` *(planned for Q/T/R; exists for J/P/F/C)*
> 3. **Functional decomposition** (Counterpoint-substrate-aware, L2/L3 + user stories) — *this card*

## Governing thesis

T is the **inbound edge of every spine module**. Every detection (Q), every customer projection (R), every device telemetry signal (N), every margin computation (P-derived), every transfer reconciliation (D), every PO match (J) — all eventually trace back to a row T wrote. If T is wrong, every downstream answer is wrong.

For a Counterpoint-shaped tenant, T's functional surface is dominated by **two architectural pivots that distinguish it from the Square baseline**: (1) ingress is poll-only, not webhook-driven, and (2) the inbound payload is **Document-shaped omnibus** — sales, returns, voids, transfers, POs, RTVs, GFC transactions all arrive through one endpoint family discriminated by `DOC_TYP`. The decomposition must accommodate both shapes (Square = webhook + Payment-shaped; Counterpoint = poll + Document-shaped) because the substrate-decoupling work documented in the Apr 25 delivery spec demands it.

T is **● Full direct** in every Counterpoint Solution Map cell, but the cell hides real architectural difficulty: poll cadence discipline, type-routing on `DOC_TYP`, watermark management per `(tenant, entity)`, multi-company-per-tenant identity, and the Document-omnibus pattern that lights up D and J modules from the same poll loop that lights up T.

## Counterpoint Endpoint Substrate

| Counterpoint Endpoint | CRDM Entity | L2 Process Area |
|---|---|---|
| PS_DOC_HDR | Transaction header | T.1 (Document ingestion), T.2 (Document type routing) |
| PS_DOC_LIN | Transaction line | T.1 (Line-item ingestion), T.3 (Tender decomposition) |
| PS_DOC_LIN_PRICE | Line price | T.3 (Price-realized capture — sourced to P) |
| PS_DOC_PMT | Payment records | T.4 (Tender capture — sourced to F) |
| Events.transactions | Transaction event stream | T.1 (EJ spine ingestion — see canary-ej-spine-and-sales-audit) |
| Store/{StoreId}/Transactions | Store transaction list | T.1 (Polling substrate) |

## Executive summary

| Dimension | Count | Source |
|---|---|---|
| L2 process areas | 6 | This card |
| L3 functional processes | 41 | This card |
| Counterpoint endpoints in steady-state path | 4 (Document × GET, Customer/Items/Stores deltas) | Endpoint spine map |
| Document types T must type-route on (`DOC_TYP`) | 8+ | Document model wiki |
| Downstream consumer modules | 7 (R, N, S, F, D, J, Q) | This card §T.4 |
| Substrate contracts T owes downstream | 12 | This card §T.6 |
| Assumptions requiring real-customer validation | 9 | Tagged `ASSUMPTION-T-NN` |
| User stories enumerated | 64 | Observer-perspective; actor ∈ {Adapter, Sealer, Parser, Anchor, Operator, Replay-tool} |

**Posture:** archetype-shaped against Counterpoint specifically, with explicit accommodation for the Square baseline staying live. No real Counterpoint customer engaged. The Q card's L3s drove most of T.6 (substrate contracts to downstream); see Q's §Q.1 for the consumer-side perspective.

## L1 → L2 → L3 framework

```
L1 (Solution Map cell)         T = ● Full direct (Counterpoint Document family)
                                 │
L2 (Process areas)               ├── T.1  Adapter ingress (poll OR webhook, per source)
                                 ├── T.2  Sealing & integrity (raw-bytes hash chain)
                                 ├── T.3  Provider-keyed parsing (Document → CanonicalEvent)
                                 ├── T.4  Canonical event publication (downstream dispatch)
                                 ├── T.5  Merkle anchoring (batch tree, anchor cadence)
                                 ├── T.6  Replay, backfill & idempotency
                                 └── T.7  Cross-module substrate contracts
                                 │
L3 (Functional processes)       (41 — enumerated per L2 below)
                                 │
L4 (Implementation detail)      Lives in SDDs + module specs
                                  (Canary-Retail-Brain/modules/T-transaction-pipeline.md,
                                   docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md,
                                   2026-04-25-canary-for-rapidpos-delivery-spec.md cycles 7-8)
```

## T.1 — Adapter ingress

**Purpose.** Receive vendor-shaped transactional events. Two ingress shapes must coexist on the same downstream pipeline: **webhook push** (Square — works today) and **poll pull** (Counterpoint — to be built). The substrate-decoupling pass defined in the delivery spec ensures the downstream consumers (T.2 onward) can't tell them apart.

**Provider key.** Every event entering T.1 carries `(provider, tenant_id)` from the moment it enters. Provider is derived from request signature (webhook) or known at construction time (poll loop). No event reaches T.2 without provider attribution.

### L3 processes

| ID | L3 process | Provider scope | Notes |
|---|---|---|---|
| T.1.1 | Webhook receipt + HMAC validation | Square | Existing; signature key per merchant rotated at onboarding → TBD: L4 implementation detail pending |
| T.1.2 | Webhook idempotency check | Square | Valkey DB 3 dedupe by `(merchant_id, source_event_id)`, 24h TTL → TBD: L4 implementation detail pending |
| T.1.3 | Poll worker per `(tenant, entity_type)` | Counterpoint (today); future Aloha | Reads adapter's `poll_intervals()`; respects per-entity cadence → TBD: L4 implementation detail pending |
| T.1.4 | Watermark management per poll cursor | Counterpoint | Stored as `(tenant_id, company_alias, entity_type) → last_RS_UTC_DT`; advances on successful page consume → TBD: L4 implementation detail pending |
| T.1.5 | Poll authentication injection | Counterpoint | HTTP Basic `<CompanyAlias>.<UserName>:password` + APIKey header per request; credentials read from `pos_tenant_credentials` → TBD: L4 implementation detail pending |
| T.1.6 | Multi-company-per-tenant routing | Counterpoint | Single Canary tenant may have N Counterpoint companies; poll loop iterates over all `company_alias` per tenant → TBD: L4 implementation detail pending |
| T.1.7 | Server-cache discipline | Counterpoint | `ServerCache: no-cache` for first poll of each cycle on cached entities; never on Documents (transactional, uncached server-side) → TBD: L4 implementation detail pending |
| T.1.8 | Rate-limit / 429 backoff | Counterpoint | Exponential backoff; per-tenant poll budget → TBD: L4 implementation detail pending |
| T.1.9 | On-prem reachability handling | Counterpoint | Customer's API server may be on-prem with no public IP; fall back to customer-side agent or document the constraint at onboarding → TBD: L4 implementation detail pending |
| T.1.10 | Backfill ingress (one-shot) | All | At tenant install, walk the relevant entity surface from epoch via paginated GET; same downstream pipeline; tag rows `source_type=BATCH` → TBD: L4 implementation detail pending |

### User stories

- *As the Counterpoint poll worker, I want a watermark per `(tenant, company_alias, entity_type)` so I never re-fetch already-consumed Documents and never miss a Document committed during my last cycle.*
- *As the Counterpoint poll worker, I want to know my per-tenant rate budget so a busy tenant doesn't starve a sibling tenant on the same Canary node.*
- *As an Operator in Owl, I want to ask "is the Counterpoint poll loop healthy for tenant X" and get last-successful-poll timestamps per entity type with explicit drift warnings.*
- *As an Operator, I want to force a one-shot `ServerCache: no-cache` poll on demand when I suspect cache staleness, without blowing up downstream.*
- *As an Operator onboarding a Counterpoint tenant, I want connection-test feedback (auth ok / APIKey ok / company alias resolves / sample entity returns) before I commit the credentials.*

## T.2 — Sealing & integrity

**Purpose.** Hash every received event over its raw bytes before any business logic runs, then chain those hashes per tenant to produce an append-only evidence ledger. The chain survives every downstream operation including parser changes — because the hash is over bytes-as-arrived, not over a parsed shape.

**Stage ordering is patent-critical.** Hash before parse. Parse is fallible; hash is not. Every later integrity claim depends on this ordering.

### L3 processes

| ID | L3 process | Notes |
|---|---|---|
| T.2.1 | Raw-bytes hash | SHA-256 over the unparsed payload as it crossed the ingress boundary → TBD: L4 implementation detail pending |
| T.2.2 | Per-tenant chain hash | `SHA-256(previous_chain_hash || event_hash)`; serialized via `pg_advisory_xact_lock(merchant_id)` → TBD: L4 implementation detail pending |
| T.2.3 | Evidence record write | `evidence_records` row with provider, tenant, raw bytes, hash, chain hash, ingest timestamp → TBD: L4 implementation detail pending |
| T.2.4 | Per-event ingestion-log lifecycle | `ingestion_log` tracks received → sealed → parsed → published → completed/failed transitions → TBD: L4 implementation detail pending |
| T.2.5 | Source-type marker | Every evidence row carries `source_type ∈ {WEBHOOK, POLLING, BATCH}` so downstream can disambiguate without inspecting bytes → TBD: L4 implementation detail pending |
| T.2.6 | Provider marker | Every evidence row carries `provider ∈ {square, counterpoint, ...}` — the substrate-decoupling load-bearing field → TBD: L4 implementation detail pending |

### User stories

- *As Canary's compliance posture, I want every byte of every received event sealed before any parser touches it, so a parser bug tomorrow cannot retroactively alter the integrity record.*
- *As an Auditor, I want to walk the evidence chain for a tenant from epoch to current and verify every link, without depending on any parsed shape.*
- *As Replay-tool, I want to re-run the parser against sealed bytes without re-sealing, so parser bugfixes reprocess history without breaking the chain.*

## T.3 — Provider-keyed parsing

**Purpose.** Convert vendor-shaped sealed bytes into `CanonicalEvent` rows. This is the L2 where the Document-omnibus pattern lives. For Counterpoint, **one polled Document fans out into multiple CanonicalEvents** — transaction header, lines flattened, payments flattened, taxes flattened, audit log entries flattened, pricing decisions flattened, original-doc references resolved.

**Dispatch shape.** Parser registry keyed by `(provider, event_type)` for webhooks, `(provider, entity_type)` for poll. Adding a third provider requires no edits to dispatch — just registry entry.

### L3 processes

| ID | L3 process | Provider scope | Notes |
|---|---|---|---|
| T.3.1 | Provider/source-code dispatch | All | `webhook_dispatch.py` and `tsp/consumers/sub2_parse.py` lookup by `(provider, event_type/entity_type)` → TBD: L4 implementation detail pending |
| T.3.2 | Document type-routing on `DOC_TYP` | Counterpoint | T-routes to `transaction.created`; XFER → `transfer.created` (D); PO/PREQ/RECVR/RTV → J events; GFC → `gift_card.activity` (F) → TBD: L4 implementation detail pending |
| T.3.3 | Document line flattening | Counterpoint | `PS_DOC_LIN[]` → `Events.transaction_lines` rows; per-line `LIN_TYP` (S/R/O/B/L/etc.) preserved → TBD: L4 implementation detail pending |
| T.3.4 | Document payment flattening | Counterpoint | `PS_DOC_PMT[]` → `Events.payments`; PII-sensitive fields (`SIG_IMG`, `SIG_IMG_VECTOR`) **redacted at parser, never persisted** → TBD: L4 implementation detail pending |
| T.3.5 | Document tax flattening | Counterpoint | `PS_DOC_TAX[]` → `Events.transaction_taxes`; multi-authority preserved (city + county + state stack) → TBD: L4 implementation detail pending |
| T.3.6 | Document audit-log flattening | Counterpoint | `PS_DOC_AUDIT_LOG[]` → `Events.audit_log_entries`; **`ACTIV` and `LOG_ENTRY` preserved verbatim** for Q rule pattern-matching → TBD: L4 implementation detail pending |
| T.3.7 | Pricing-decision flattening | Counterpoint | `PS_DOC_LIN_PRICE[]` → `Events.pricing_decisions`; per-line pricing rule applied (Q + P-derived substrate) → TBD: L4 implementation detail pending |
| T.3.8 | Original-document reference resolution | Counterpoint | `PS_DOC_HDR_ORIG_DOC[]` → `Events.original_doc_refs`; links return → original sale, void → original sale → TBD: L4 implementation detail pending |
| T.3.9 | Square-shaped legacy parsing | Square | 16 existing parser modules; refactored into `services/pos/square/parsers/` per Cycle 7; behavior unchanged → TBD: L4 implementation detail pending |
| T.3.10 | Idempotency on parse | All | Keyed on `(provider, tenant, external_id)`; parsing the same sealed event twice produces the same canonical rows → TBD: L4 implementation detail pending |
| T.3.11 | Parse-failure quarantine | All | Failed parses do NOT block the seal chain; logged + dead-lettered for inspection; re-runnable via Replay-tool → TBD: L4 implementation detail pending |
| T.3.12 | Schema-drift fingerprinting | All | Per-source `SchemaFingerprint`; Counterpoint payloads compute against Counterpoint baseline, never Square — fixes the L3B-04 cross-provider drift-alert bug → TBD: L4 implementation detail pending |

### User stories

- *As the Counterpoint parser, I want to type-route on `DOC_TYP` cleanly so a single polled Document produces transaction events, transfer events, or PO events — without the call site needing to know which.*
- *As the Counterpoint parser, I want PII-sensitive fields (`SIG_IMG`) redacted before any row reaches the database, so signature images literally never enter Canary's storage.*
- *As Q (Q.1.5 in the Q card), I want `PS_DOC_AUDIT_LOG.ACTIV` and `LOG_ENTRY` preserved verbatim — Q's rules pattern-match on these strings and any normalization breaks them.*
- *As Replay-tool, I want to re-run parsing against sealed bytes for a date range without re-emitting downstream events, so I can validate parser bugfixes against history.*
- *As an Operator, I want parse failures visible in a quarantine queue with the sealed bytes preserved, so I can diagnose without the parser blocking ingestion.*

## T.4 — Canonical event publication

**Purpose.** Hand sealed-and-parsed CanonicalEvents to downstream consumers. Every consumer reads from the same canonical surface; none reach into provider-specific shapes. This L2 owns the publication contract and the per-consumer dispatch.

### L3 processes

| ID | L3 process | Consumer module | Notes |
|---|---|---|---|
| T.4.1 | Publish to `canary:detection` stream | Q | Every transaction-related CanonicalEvent; Q's chirp engine subscribes → TBD: L4 implementation detail pending |
| T.4.2 | Publish to R-relevant subscribers | R | New customer references trigger upserts; transaction velocity feeds R's projections → TBD: L4 implementation detail pending |
| T.4.3 | Publish device telemetry to N | N | Per-`STR_ID/STA_ID/DRW_ID` telemetry; drawer-session correlation substrate → TBD: L4 implementation detail pending |
| T.4.4 | Publish line items to S consumers | S | Item identity references; sales velocity feeds S projections → TBD: L4 implementation detail pending |
| T.4.5 | Publish tender + tax to F consumers | F | Per-Document tender mix and per-authority tax detail → TBD: L4 implementation detail pending |
| T.4.6 | Publish transfer events to D | D | DOC_TYP=XFER routes here; source/dest store reconciliation → TBD: L4 implementation detail pending |
| T.4.7 | Publish PO/RECVR/RTV events to J | J | DOC_TYP=PO/PREQ/RECVR/RTV routes here; vendor reconciliation substrate → TBD: L4 implementation detail pending |
| T.4.8 | Per-consumer subscription ack tracking | All | Confirm each consumer processed; expose lag per consumer → TBD: L4 implementation detail pending |

### User stories

- *As Q's Chirp engine, I want every parsed transaction to arrive on `canary:detection` within seconds of the Document being polled, with the substrate snapshot inline (not as FK references).*
- *As R, I want every new `CUST_NO` reference in a transaction to trigger an upsert into the customer registry, even if the Customer record itself hasn't been polled yet (R catches up async).*
- *As D, I want only DOC_TYP=XFER events on my subscription — not every transaction; type-routing is T.3's job, not mine.*
- *As an Operator, I want per-consumer lag visible (Q at 2s, R at 8s, D at 15s) so a slow consumer doesn't silently fall behind.*

## T.5 — Merkle anchoring

**Purpose.** Batch sealed event hashes into a Merkle tree, anchor the root, expose per-event inclusion proofs. Today the anchor is mocked; v2 anchors as a Bitcoin ordinal inscription. This L2 is least urgent for Counterpoint cutover but most differentiating for the platform pitch.

### L3 processes

| ID | L3 process | Notes |
|---|---|---|
| T.5.1 | Inscription pool accumulation | Sealed event hashes accumulate in `inscription_pool` per tenant per cadence window → TBD: L4 implementation detail pending |
| T.5.2 | Merkle tree construction | Deterministic tree over the pool window; root is the anchor commitment → TBD: L4 implementation detail pending |
| T.5.3 | Per-event inclusion proof | `event_inscriptions` rows carry the path from event hash to root for each batched event → TBD: L4 implementation detail pending |
| T.5.4 | Anchor handoff (mock today) | v1: mock anchor with deterministic-but-fake commitment; v2: Bitcoin ordinal inscription → TBD: L4 implementation detail pending |
| T.5.5 | Cadence policy | Per-tenant or platform-wide; needs commitment (per-batch / per-day / per-100k-events) → TBD: L4 implementation detail pending |
| T.5.6 | Proof retrieval surface | Operator can fetch per-event inclusion proof and verify against anchor → TBD: L4 implementation detail pending |

### User stories

- *As Canary's Compliance Story, I want every sealed event to carry a verifiable inclusion proof that anchors back to a public commitment, so "the data wasn't tampered with after the fact" is provable, not asserted.*
- *As an Operator, I want to fetch any event's inclusion proof and walk it manually to the anchor, without depending on Canary's own systems.*
- *As Canary's Product Owner, I want the anchor cadence published as an SLA before tenants depend on it for compliance attestation.*

## T.6 — Replay, backfill & idempotency

**Purpose.** Operational discipline. Three concerns intersect: replay (re-process sealed bytes through a fixed parser), backfill (initial historical pull at tenant install), idempotency (same input produces same output every time). All three converge on the principle: **the seal is the source of truth, not the parsed rows**.

### L3 processes

| ID | L3 process | Notes |
|---|---|---|
| T.6.1 | Parse-only replay | Re-run T.3 against sealed bytes; does NOT re-seal, does NOT re-anchor → TBD: L4 implementation detail pending |
| T.6.2 | Per-tenant backfill at install | One-shot historical pull from epoch (or tenant-specified start); same downstream pipeline; `source_type=BATCH` marker → TBD: L4 implementation detail pending |
| T.6.3 | Backfill SLA per tenant | Published completion target per entity type; 1d for Documents-from-90d-ago is reasonable; longer history = longer SLA → TBD: L4 implementation detail pending |
| T.6.4 | Idempotency at every stage | T.1 ingress (dedup), T.2 seal (per-event hash idempotent), T.3 parse (per-canonical-row idempotent) → TBD: L4 implementation detail pending |
| T.6.5 | Retroactive parser-change reclassification handling | When a parser change retroactively changes event type (e.g., `PAID_OUT` → `POST_VOID`), downstream Q rules may double-fire — needs explicit policy → TBD: L4 implementation detail pending |
| T.6.6 | Per-event reprocess-on-demand | Operator can target a specific `(provider, tenant, external_id)` and force re-parse; useful for one-off bugfix verification → TBD: L4 implementation detail pending |
| T.6.7 | Backfill progress observability | Per-tenant completion %, per-entity-type, with rate estimate → TBD: L4 implementation detail pending |

### User stories

- *As Replay-tool, I want to take a date range, re-parse every sealed event in it, and dry-run the new canonical rows against the existing rows so I can see exactly what changed before committing.*
- *As an Operator onboarding a Counterpoint tenant with 3 years of history, I want a published backfill SLA per entity type so I can set tenant-side expectations without guessing.*
- *As Canary's Product Owner, I want a documented policy for parser-change reclassification so when `PAID_OUT` semantically becomes `POST_VOID`, Q doesn't double-fire detections on the historical events.*

## T.7 — Cross-module substrate contracts

**Purpose.** T owes downstream modules specific guarantees about the canonical surface. This L2 is the contract registry: which fields, which preservation rules, which freshness commitments. **Q's §Q.1 is the consumer view of these contracts; T.7 is the producer view.**

**Why it matters.** A downstream module's L3 process can quietly fail if T silently changes a field's preservation. Naming the contracts here makes silent breakage impossible without explicit T-side change.

### L3 contracts (registry)

| ID | Contract | Owner downstream | What T promises |
|---|---|---|---|
| T.7.1 | Audit-log verbatim preservation | Q (Q.1.5) | `ACTIV` and `LOG_ENTRY` strings preserved exactly — no normalization, no trimming → TBD: L4 implementation detail pending |
| T.7.2 | Original-doc-ref array always present | Q (Q.2.2) | Empty array means "no link"; missing array means "T didn't populate" — distinguishable → TBD: L4 implementation detail pending |
| T.7.3 | Pricing-decision per-line snapshot | Q (Q.1.6), P (derived) | `PS_DOC_LIN_PRICE` flattened with `PRC_JUST_STR`, `PRC_RUL_SEQ_NO`, `UNIT_PRC` per line → TBD: L4 implementation detail pending |
| T.7.4 | Multi-authority tax preservation | Q (Q.2.8), F | `PS_DOC_TAX[]` rows preserved per authority; not summed → TBD: L4 implementation detail pending |
| T.7.5 | Drawer-session linkage | Q (Q.2.4), N | Every transaction carries `DRW_ID + DRW_SESSION_ID + USR_ID` for drawer-shrinkage rule chains → TBD: L4 implementation detail pending |
| T.7.6 | DOC_TYP type-routing completeness | D, J, F | Every documented `DOC_TYP` routes to a CanonicalEvent type; unknown DOC_TYP routes to a quarantine event with full payload → TBD: L4 implementation detail pending |
| T.7.7 | Customer reference upsert | R | Every `CUST_NO` reference triggers an R upsert before the transaction event publishes (or at the same time, with R catching up async per its T-card-defined posture) → TBD: L4 implementation detail pending |
| T.7.8 | Item reference resolution | S, P-derived | Every `ITEM_NO` on a line carries enough context (category, mix-match group, vendor) for downstream joins without re-hitting Counterpoint → TBD: L4 implementation detail pending |
| T.7.9 | Substrate freshness signal | Q, every consumer | Every CanonicalEvent carries `polled_at` so consumers can suppress stale-substrate alerts → TBD: L4 implementation detail pending |
| T.7.10 | PII redaction at parse | All | `SIG_IMG`, `SIG_IMG_VECTOR`, raw PAN, raw CVV — never reach `evidence_records` past the parser; redacted in-flight → TBD: L4 implementation detail pending |
| T.7.11 | Provider attribution | All | Every CanonicalEvent carries `provider` so consumer-side rule applicability (e.g., Square-only rules vs Counterpoint-only) is enforceable → TBD: L4 implementation detail pending |
| T.7.12 | Tenant + company alias attribution | All | Every CanonicalEvent carries `(tenant_id, company_alias)` so multi-company-per-tenant Counterpoint deployments don't bleed events across companies → TBD: L4 implementation detail pending |

### User stories

- *As Q, I want to assert at boot that all 12 T.7 contracts hold against the current T deployment, so a silent contract break shows up at startup, not at first detection-miss.*
- *As R, I want T's contract to upsert a Customer reference before the transaction event publishes — even if the upsert is "shell row, more data coming" — so my projections never reference unknown customers.*
- *As Canary's Product Owner, I want a contract-test suite (per Cycle 7 §7.3 in the delivery spec) that runs every contract in T.7 against every registered provider's adapter — Square, Counterpoint, future Aloha.*

## Canary Detection Hooks

| T Process | → Detection Surface | Signal Description |
|---|---|---|
| T.2 (Document type routing) | All downstream modules | T is the spine — every detection rule in Q, D, F, P, R depends on T's type-routing being correct. T does not itself fire Chirp rules; it is the ingest substrate |
| T.3 (Tender decomposition) | Q-TM rule family | Tender-mix anomalies detected during T.3 decomposition (e.g., unusual split-tender patterns, voided tenders) are published as Q-TM-01/02 signals |
| T.4.7 (XFER routing to D) | D detection pipeline | T.4.7 routes XFER-type documents to D's transfer-loss detection pipeline. T is the upstream source; D.3 is the consumer |
| T.5 (Return/void processing) | Q-IS rule family | Returns and voids routed through T.5 are accumulation inputs for Q-IS-02 (return-fraud pattern) and Q-IS-04 (void accumulation) |

## Additional User Stories

- *As a store manager, I need Canary to correctly ingest and classify transactions captured in offline mode (when the Counterpoint station was disconnected) so that my LP and sales reports are not understated for offline periods.*

## Assumptions requiring real-customer validation

These markers exist because the answer requires either a Counterpoint sandbox database, a real customer's Document corpus, or both.

| ID | Assumption | What it blocks | Resolution path |
|---|---|---|---|
| ASSUMPTION-T-01 | Full `DOC_TYP` code list — sample only confirmed `T` for ticket; XFER/RECVR/PO/PREQ/RTV/GFC inferred from Workgroup numbering | T.3.2 type-routing completeness; T.7.6 contract | Sandbox DB inspection; multiple sample payloads needed |
| ASSUMPTION-T-02 | Void `DOC_TYP` code and whether voids reference original via `PS_DOC_HDR_ORIG_DOC` | T.3.2 + T.7.2 (original-doc contract) | Sandbox DB workflow test — execute a void and inspect |
| ASSUMPTION-T-03 | Other `LIN_TYP` codes beyond S, R, O, B, L, D — full taxonomy from `PS_STR_CFG_PS.LIN_TYP_*` | T.3.3 line flattening completeness | Sandbox config inspection |
| ASSUMPTION-T-04 | `IS_DOC_COMMITTED = "N"` semantics — do uncommitted Documents appear in GET / should we ingest them | T.1.3 poll-loop scope (skip uncommitted? ingest as draft?) | Sandbox workflow test |
| ASSUMPTION-T-05 | `IS_OFFLINE` Document handling — what changes at sync time when offline-processed events catch up | T.6 backfill + idempotency edge case | Sandbox DB or customer with offline-mode stores |
| ASSUMPTION-T-06 | Counterpoint sandbox / FTP credentials — published path exists per `Brain/wiki/ncr-counterpoint-sandbox-setup-checklist.md`, but does the team actually have them | T.1 entire ingress build path can't smoke-test without these | Operator action — request from NCR partner contact |
| ASSUMPTION-T-07 | On-prem reachability for production tenants — customer Counterpoint API server may have no public IP | T.1.9 (on-prem reachability) — may force customer-side agent or tunneled architecture | Per-customer at onboarding |
| ASSUMPTION-T-08 | API option enablement rate across the installed base — Counterpoint REST is a paid `registration.ini` add-on | If <50% of base has API enabled, T may need direct-DB fallback as primary path | Customer-side discovery; possibly direct-DB SDD addition |
| ASSUMPTION-T-09 | Rapid POS proprietary tables on top of standard Counterpoint schema | Whether T must extend its parser surface for Rapid-specific data | Direct conversation with Rapid POS / customer |

**Highest-leverage gaps:** T-01 / T-02 (full DOC_TYP + void semantics) — these are the load-bearing structural assumptions for type-routing. Sandbox access (T-06) unblocks all of T-01 / T-02 / T-03 / T-04 / T-05 in one move.

## Customer-specific overrides

*Empty until a real customer engagement starts. Format reserved:*

```
Customer: <name>
Counterpoint deployment shape: <on-prem | hosted | hybrid>
API hosting: <self-hosted Windows port 52000 | other>
Multi-company: <yes — N companies | no — single company>
Company aliases: [<alias1>, <alias2>, ...]
Backfill window: <epoch | <date> | <N years>>
Per-tenant poll budget: <reqs/min cap>
On-prem reachability path: <direct | customer-agent | tunnel>
Rapid POS extensions in scope: <yes — extension list | no>
Disabled DOC_TYPs (with reason):
  <type>: <reason>
  ...
ASSUMPTION resolutions:
  ASSUMPTION-T-NN: resolved as <answer>; source: <evidence>
  ...
```

## Operating notes

- T and Q are **the most coupled module pair**. T.7 substrate contracts are largely driven by Q's §Q.1 consumer needs. Drift between T.7 (this card) and Q.1 (the Q card) means a contract was silently broken.
- The poll-only ingress for Counterpoint is the architectural pivot from the Square baseline. Cycle 7 in the delivery spec scaffolds the substrate to accept poll-shaped ingress; Cycle 8 builds the actual poller. This card describes the steady-state shape; the build sequencing lives in the delivery spec.
- **Document is omnibus.** A single `GET /Document` poll cycle produces fan-out into T (transactions), D (transfers), J (POs/RTVs), F (gift card transactions), and Q substrate (audit log). The L3 type-routing in T.3.2 is what makes this work; the L2 publication in T.4 is what fans it out cleanly.
- The Square baseline stays live unchanged through every cycle (Apr 25 spec § "Park Square" decision). T.3.9 is the only L3 that touches Square; everything else in T.3 is provider-keyed dispatch.

## Related

- `Canary-Retail-Brain/modules/T-transaction-pipeline.md` — module-level architectural spec (CRDM, BSTs, schema, agent surface, security posture); referenced by every T.x section
- `canary-module-q-functional-decomposition.md` — sister card; T.7 contracts ↔ Q.1 consumer needs
- `ncr-counterpoint-document-model.md` — Document substrate detail (DOC_TYP, audit log, pricing, taxes, original-doc refs); referenced throughout T.3 and T.7
- `ncr-counterpoint-api-reference.md` — full API surface, auth, caching, error codes; referenced by T.1
- `ncr-counterpoint-endpoint-spine-map.md` — per-endpoint × CRDM × spine map; referenced by T.1 and T.4
- `2026-04-25-canary-for-rapidpos-delivery-spec.md` — Cycles 7-8 build sequencing for the substrate decoupling and Counterpoint adapter
- `docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md` — primary SDD; T.4 architecture comes from this
- `garden-center-operating-reality.md` — vertical-specific data noise patterns (manual entry errors, item-code drift); referenced by T.6 (parse-failure tolerance posture)
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — T row = ● Full direct; this card is the L2/L3 expansion of that cell
- (CATz, proposed) `method/artifacts/module-functional-decomposition.md` — the artifact template this card proves out alongside Q

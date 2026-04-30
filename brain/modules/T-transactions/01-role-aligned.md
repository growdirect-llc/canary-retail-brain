---
title: T — Role Alignment
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-t, transactions, poslog, tsp]
sources:
  - Canary-Retail-Brain/modules/T-transaction-pipeline.md
  - Canary/canary/models/sales/transactions.py
  - Canary/canary/blueprints/webhooks_tsp.py
  - Canary/docs/sdds/v2/webhook-pipeline.md
last-compiled: 2026-04-24
----

# Canary Module — T (Transaction Pipeline)

## Summary

T is the inbound edge of Canary. It receives Square webhooks, hashes
the raw bytes before parsing, seals them into a per-merchant evidence
chain, parses them into the `sales` schema, and hands the
parsed event off to the Chirp detection engine. T is the upstream
feeder for every other module on the [[../projects/RetailSpine|Retail
Spine]]; if T's ledger is wrong, every downstream answer is wrong.

This wiki article is the **Canary-specific crosswalk** for T. The
canonical, vendor-neutral module spec lives in the brain at
`Canary-Retail-Brain/modules/T-transaction-pipeline.md`. This article
points at the actual Canary code, tables, and SDDs that implement it.

## Code surface

| Concern | File | Notes |
|---|---|---|
| Webhook receipt | `Canary/canary/blueprints/webhooks_tsp.py` | HMAC validation + raw-byte hash *before* JSON parse (patent-critical ordering) |
| Sub 1 — seal | `Canary/canary/services/tsp/consumers/sub1_seal.py` | Chain hash compute under `pg_advisory_xact_lock` per merchant |
| Sub 2 — parse + dispatch | `Canary/canary/services/webhook_dispatch.py` | Routes by `event_type` to one of 6 Square parsers |
| Sub 3 — Merkle | `Canary/canary/services/tsp/consumers/sub3_merkle.py` + `Canary/canary/services/tsp/merkle.py` | Batch ≥100 events or ≥600s; mock anchor (Sprint 6) |
| Sub 4 — detection handoff | (consumed by Q/Chirp) | T's responsibility ends when event lands on `canary:detection` stream |
| Square OAuth | `Canary/canary/services/square_oauth.py` | AES-256-GCM at rest; auto-refresh on retrieval |
| Onboarding | `Canary/canary/services/onboarding/coordinator.py` | 3-step: webhook register → initial sync → baseline calc |
| Square parsers | `Canary/canary/services/parsers/square_*.py` | 6 modules: payment, order, loyalty, payout, dispute, auxiliary |
| Square HMAC validator | `Canary/canary/services/tsp/validators/square.py` | Timing-safe `hmac.compare_digest` |

## Schema crosswalk

T writes to the `sales` schema and reads (only) from `app`.

**Owns (write):**

| Table | Pattern | Purpose |
|---|---|---|
| `evidence_records` | write-once | Hash-chained sealed event records (forensic backbone — see [[canary-data-model#schema-sales-square-crdm|canary-data-model §Sales]]) |
| `ingestion_log` | mutable lifecycle | Per-event status: receipt → processing → completion/failure |
| `transactions` | append-only | Every Square payment, refund, void, no-sale, paid-in/out, exchange |
| `transaction_line_items` | append-only | Per-transaction line detail (FK → `transactions.id`) |
| `transaction_tenders` | append-only | Tender mix per transaction |
| `refund_links` | append-only junction | Refunds → original payments |
| `cash_drawer_shifts` | append-only | Drawer session boundaries |
| `cash_drawer_events` | append-only | Drawer open/close/skim events |
| `inscription_pool` | mutable | Batched event hashes awaiting anchor |
| `event_inscriptions` | append-only | Per-event Merkle inclusion proofs |

**Reads (no write):**

| Table | Owner | Why |
|---|---|---|
| `app.merchants` | platform | Tenant resolution from webhook signing key |
| `app.square_oauth_tokens` | platform | Token retrieval for backfill / polling |
| `app.merchant_locations` | future C/D | Validate `location_id` |
| `app.merchant_devices` | future N | Validate `device_id` |
| `app.merchant_employees` | future L | Validate `employee_id` |

## SDD crosswalk

| SDD | Path | T's relationship |
|---|---|---|
| webhook-pipeline | `Canary/docs/sdds/v2/webhook-pipeline.md` | Primary spec — entire HMAC → hash → seal → parse → score flow |
| chirp | `Canary/docs/sdds/v2/chirp.md` | Downstream consumer; T hands off here |
| fox | `Canary/docs/sdds/v2/fox.md` | Downstream of Chirp; uses T's evidence chain for chain-of-custody |
| data-model | `Canary/docs/sdds/v2/data-model.md` | Defines the 3-schema layout T writes into |
| raas | `Canary/docs/sdds/v2/raas.md` | Bitcoin ordinals anchoring (Sub 3 inscription) — currently mock |
| architecture | `Canary/docs/sdds/v2/architecture.md` | System-wide; T is one of 16 services |

## Stream contracts

T publishes two Valkey streams:

| Stream | Producer | Consumer | Payload |
|---|---|---|---|
| `canary:events` | webhook endpoint | `sub1-seal` | 9-field message: event_id, merchant_id, source, source_event_id, event_type, event_hash (hex), raw_payload (UTF-8), received_at (ISO 8601), parse_failed |
| `canary:detection` | `sub2-parse` | Chirp engine (Q) | Parsed canonical event (transaction-shaped) ready for rule evaluation |

Idempotency: Valkey DB 3, key = `(merchant_id, source_event_id)`, TTL 24h.

## Detection-rule integration

The 37 frozen Chirp rules read from `sales` tables T owns. Tier
breakdown ([[canary-detection|Canary Detection Engine]] for the full
catalog):

- **Tier 1 (stateless, 6 rules)** — Fire during webhook receipt before
  Sub 2 finishes. Read no DB. Rules: C-004, C-007, C-009, C-010, C-011,
  C-502.
- **Tier 2 (windowed, 9 rules)** — Valkey-counter aggregation over T's
  stream.
- **Tier 3 (full DB, 14 rules)** — SQLAlchemy queries against
  `sales` tables.

Critical rules (C-009, C-104, C-204, C-301, C-502, C-602) auto-escalate
to Fox case creation.

## Where T fits on the spine

T is one of the [[../projects/RetailSpine|Retail Spine]] Differentiated-Five
modules (T+R+N+A+Q). Per the
[[../projects/RetailSpine#4-store-operations-management|Store
Operations § BST inventory]], T is the primary feeder for two BSTs:

1. **Loss Prevention Analysis** — T's stream is what Chirp evaluates
2. **Transaction Profitability Analysis** — `transactions.amount_cents`
   × `transaction_tenders` × processing fees is the source data

T contributes to many other BSTs (Purchase Profiles, Market Basket,
Product Analysis, eCommerce Analysis, Financial Mgmt Accounting, Income
Analysis) but doesn't own them — they're computed by downstream
projection services.

## Open Canary-specific questions

These are the schema-mapping gaps that surfaced while building this
crosswalk and need resolution in the v0.6 schema-mapping pass on the
Retail Spine:

1. **`merchant_employees` ownership.** T reads this table but no module
   currently owns curation. Likely the future L (Labor & Workforce)
   module — but L is v3, and T needs the FK target to exist now.
   Today the table is populated as a side-effect of Square sync during
   onboarding, with no owning service.
2. **`merchant_locations` ownership.** Same problem. Locations are
   currently treated as platform infrastructure rather than as a
   spine module's territory. Should the Places registry be a v1
   shim under T, or wait for D (Distribution) in v2?
3. **Cross-vendor identity.** T has no model for unifying transactions
   from a hypothetical Square-in-store + Shopify-online merchant.
   Belongs in R/N conjointly per the canonical brain article, but
   the FK shape that would carry it lives in T.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-data-model|Canary Data Model]] — 3-schema layout (`app` / `sales` / `metrics`)
- [[canary-architecture|Canary Architecture]] — 16-service system view
- [[canary-detection|Canary Detection Engine]] — how Chirp consumes T's stream
- [[retail-integration-spine|Retail Integration Spine]] — vendor-neutral integration patterns
- [[retail-spine-solex-crosswalk|Solex Crosswalk]] — T's stream observed end-to-end

## Sources

- `Canary-Retail-Brain/modules/T-transaction-pipeline.md` — canonical vendor-neutral spec
- `Canary/canary/models/sales/transactions.py` — core transaction model (Transaction, refund_links)
- `Canary/canary/models/sales/line_items.py` — TransactionLineItem
- `Canary/canary/models/sales/ingestion.py` — IngestionLog
- `Canary/canary/blueprints/webhooks_tsp.py` — webhook endpoint
- `Canary/canary/services/tsp/consumers/sub1_seal.py` — seal stage
- `Canary/canary/services/tsp/consumers/sub3_merkle.py` — Merkle stage
- `Canary/canary/services/webhook_dispatch.py` — parse routing
- `Canary/canary/services/parsers/square_*.py` — 6 Square parsers
- `Canary/canary/services/square_oauth.py` — OAuth lifecycle
- `Canary/canary/services/onboarding/coordinator.py` — onboarding pipeline
- `Canary/docs/sdds/v2/webhook-pipeline.md` — primary SDD
- `Canary/docs/sdds/v2/chirp.md` — downstream consumer SDD
- `Canary/docs/sdds/v2/fox.md` — case management SDD
- `Canary/docs/retail-capability-model.md` §4.1 — detection-and-notification pattern

---
title: Q — Role Alignment
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-q, chirp, fox, loss-prevention, detection, case-management]
sources:
  - Canary-Retail-Brain/modules/Q-loss-prevention.md
  - Canary/canary/services/chirp/
  - Canary/canary/services/fox/
  - Canary/canary/models/fox/
  - Canary/docs/sdds/v2/chirp.md
  - Canary/docs/sdds/v2/fox.md
last-compiled: 2026-04-24
----

# Canary Module — Q (Loss Prevention) — Chirp + Fox

## Summary

Q is Canary's loss-prevention surface — Chirp (detection engine, 37
frozen rules across 10 categories, 3-tier evaluation) plus Fox (case
management with INSERT-only chain-of-custody evidence enforced at
the PostgreSQL trigger layer). Q is the most fully-implemented of
the [[../projects/RetailSpine|Retail Spine]] Differentiated-Five
modules and the reference implementation for v3 W (Work Execution),
which will generalize the same pattern to every domain on the spine.

This wiki article is the Canary-specific crosswalk for Q. The
canonical, vendor-neutral spec lives at
`Canary-Retail-Brain/modules/Q-loss-prevention.md`.

## Code surface

### Chirp (detection)

| Concern | File | Notes |
|---|---|---|
| Rule catalog (frozen, 37 rules) | `Canary/canary/services/chirp/rule_definitions.py` | RULE_CATALOG dataclass |
| Tier 1 stateless engine | `Canary/canary/services/chirp/stateless_engine.py` | 6 rules, fire during webhook receipt |
| Tier 2/3 engine | `Canary/canary/services/chirp/rule_engine.py` | `ChirpRuleEngine` class |
| Threshold manager | `Canary/canary/services/chirp/threshold_manager.py` | Per-merchant overrides + Valkey cache |
| MCP tools (10) | `Canary/canary/services/chirp/tools.py` | Read + threshold-write surface |
| MCP blueprint | `Canary/canary/blueprints/chirp_mcp.py` | Route registration |
| Alert lifecycle | `Canary/canary/services/alert_lifecycle.py` | TTL, archival, age decay |

### Fox (case management)

| Concern | File | Notes |
|---|---|---|
| Case service | `Canary/canary/services/fox/case_service.py` | `FoxCaseService` |
| Evidence chain | `Canary/canary/services/evidence_chain.py` | Hash chain verification |
| MCP tools (8) | `Canary/canary/services/fox/tools.py` | Case + evidence ops |
| MCP blueprint | `Canary/canary/blueprints/fox_mcp.py` | Route registration |
| Case model | `Canary/canary/models/fox/cases.py` | `fox_cases`, `fox_case_alerts`, `fox_case_timeline`, `fox_case_actions` |
| Subject model | `Canary/canary/models/fox/subjects.py` | `fox_subjects` |
| Evidence model | `Canary/canary/models/fox/evidence.py` | `fox_evidence`, `fox_evidence_access_log` |

## Schema crosswalk

**Critical clarification:** Fox tables live in the `app` schema, not
in a dedicated `fox` schema. The Python module path
`canary/models/fox/` is organizational only. Per
`Canary/canary/models/base.py`, only three schemas exist: `app`,
`sales`, `metrics`. Fox classes inherit from `AppBase` →
`MetaData(schema="app")`.

**Owns (write) — all in `app` schema:**

| Table | Pattern | Purpose |
|---|---|---|
| `detection_rules` | seeded (37 rows) | Frozen rule catalog; not tenant-scoped |
| `merchant_rule_config` | mutable | Per-merchant threshold overrides |
| `alerts` | append-only | Rule firings |
| `alert_history` | append-only | Alert status transitions |
| `fox_cases` | mutable + soft-delete | Investigation root |
| `fox_case_alerts` | mutable junction | Cases ↔ alerts |
| `fox_case_timeline` | append-only, hash-chained | Audit log |
| `fox_case_actions` | append-only + soft-delete | Investigation outcomes |
| `fox_subjects` | mutable + soft-delete | People/entities of interest |
| `fox_evidence` | INSERT-only (trigger-enforced), hash-chained | Chain-of-custody evidence |
| `fox_evidence_access_log` | INSERT-only (trigger-enforced) | Evidence read audit |

**Reads (no write):**

| Table | Owner | Why |
|---|---|---|
| `sales.transactions` | T | Rule evaluation input |
| `sales.transaction_line_items` | T | Sweethearting / discount rules |
| `sales.transaction_tenders` | T | Untendered-order rule |
| `sales.refund_links` | T | Rapid-refund / refund-rate rules |
| `sales.cash_drawer_*` | T | Cash drawer rules |
| `sales.timecards` | T | Off-clock / break / wrong-location rules |
| `sales.gift_card_*` | T | Gift card rules |
| `sales.disputes` | T | Dispute rules |
| `sales.invoices` | T | Invoice rules |
| `app.customers` | R | Customer-as-subject context |
| `sales.devices` | N | Device-as-context for rules |

## Chirp rule catalog (37 rules)

Per `Canary/canary/services/chirp/rule_definitions.py`:

| Category | Range | Rules |
|---|---|---|
| Payment | C-001 — C-011 | RAPID_REFUND · EXCESSIVE_REFUND_RATE · ROUND_AMOUNT_PATTERN · AFTER_HOURS_TRANSACTION · CARD_VELOCITY · SPLIT_TENDER_PATTERN · HIGH_VALUE_REFUND · MANUAL_ENTRY_SPIKE · SQUARE_DELAY_HOLD · PARTIAL_AUTHORIZATION · NO_SALE_DETECTED |
| Cash Drawer | C-101 — C-104 | NO_SALE_ABUSE · CASH_VARIANCE · PAID_OUT_ANOMALY · AFTER_HOURS_DRAWER |
| Order | C-201 — C-204 | EXCESSIVE_DISCOUNT_RATE · LINE_ITEM_VOID_RATE · SWEETHEARTING · UNTENDERED_ORDER |
| Timecard | C-301 — C-303 | OFF_CLOCK_TRANSACTION · BREAK_TRANSACTION · WRONG_LOCATION |
| Void | C-501, C-502 | HIGH_VOID_RATE · POST_VOID_ALERT |
| Gift Card | C-601, C-602 | GIFT_CARD_LOAD_VELOCITY · GIFT_CARD_DRAIN |
| Loyalty | C-801 — C-804 | RAPID_POINT_ACCUMULATION · BULK_REDEMPTION · CROSS_LOCATION_VELOCITY · ENROLLMENT_FRAUD |
| Composite | C-901 | SRA_THRESHOLD_BREACH |
| Dispute | C-D01 — C-D03 | DISPUTE_CREATED · DISPUTE_LOST · DISPUTE_VELOCITY |
| Invoice | C-I01 — C-I03 | INVOICE_OVERDUE · INVOICE_CHARGE_FAILED · HIGH_VALUE_INVOICE_UNPAID |

**Auto-escalating to Fox cases (6 rules):** C-009, C-104, C-204,
C-301, C-502, C-602.

## SDD crosswalk

| SDD | Path | Q's relationship |
|---|---|---|
| chirp | `Canary/docs/sdds/v2/chirp.md` | Primary spec — rules, tiers, sensitivity, MCP tools |
| fox | `Canary/docs/sdds/v2/fox.md` | Primary spec — cases, evidence, chain of custody, INSERT-only enforcement |
| alert | `Canary/docs/sdds/v2/alert.md` | Alert domain — `detection_rules`, `merchant_rule_config`, `alerts`, `alert_history` |
| data-model | `Canary/docs/sdds/v2/data-model.md` | Schema definitions |

## Where Q fits on the spine

Q is one of the [[../projects/RetailSpine|Retail Spine]] Differentiated-Five
modules. Per [[../projects/RetailSpine#4-store-operations-management|Store
Operations § BST inventory]], Q is the **primary owner** of:

- **Loss Prevention Analysis** (Q *is* this BST)

And co-owner with [[canary-module-a-asset-management|A]] of
**Suspicious Activity Analysis** (Q owns transaction-level; A owns
device-level).

Q is the v1 reference for the v3 [[../projects/RetailSpine|spine's W
module]] — generalized detection + case across every domain.

## MCP tool surfaces

| Server | Tool count | File |
|---|---|---|
| `canary-chirp` | 10 | `Canary/canary/services/chirp/tools.py` |
| `canary-fox` | 8 | `Canary/canary/services/fox/tools.py` |

Q is the most agent-rich module on v1.

## Open Canary-specific questions

1. **Notification workflow for `referred_to_le`.** Code comments
   mark this as deferred — needs an HR + legal notification path.
2. **Evidence file storage.** Fox stores file refs + SHA-256 hashes;
   blobs themselves currently land on local disk. S3 / virus scan /
   EXIF extraction all deferred per code comments.
3. **Cross-merchant subject linking.** Pairs with R's
   `external_identities` work — needed when an employee at one
   merchant is a customer at another.
4. **Sensitivity-preset UX.** Spec exists in the chirp SDD; the
   threshold-bundle switching UX is not yet built.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-data-model|Canary Data Model]]
- [[canary-architecture|Canary Architecture]]
- [[canary-detection|Canary Detection Engine]] — full Chirp doc
- [[canary-module-t-transactions|Canary Module — T]] — primary input
- [[canary-module-r-customer|Canary Module — R]]
- [[canary-module-n-device|Canary Module — N]]
- [[canary-module-a-asset-management|Canary Module — A]]

## Sources

- `Canary-Retail-Brain/modules/Q-loss-prevention.md` — canonical vendor-neutral spec
- `Canary/canary/services/chirp/rule_definitions.py` — frozen 37-rule catalog
- `Canary/canary/services/chirp/rule_engine.py` — Tier 2/3 evaluator
- `Canary/canary/services/chirp/stateless_engine.py` — Tier 1 evaluator
- `Canary/canary/services/chirp/threshold_manager.py` — per-merchant thresholds
- `Canary/canary/services/chirp/tools.py` — Chirp MCP tools
- `Canary/canary/services/fox/case_service.py` — case CRUD
- `Canary/canary/services/evidence_chain.py` — hash-chain verification
- `Canary/canary/services/alert_lifecycle.py` — TTL / archival
- `Canary/canary/models/fox/cases.py` — case model (lives in `app` schema)
- `Canary/canary/models/fox/subjects.py` — subjects of interest
- `Canary/canary/models/fox/evidence.py` — INSERT-only evidence chain
- `Canary/canary/models/app/detection.py` — rule + alert tables
- `Canary/canary/models/base.py` — `AppBase` confirms `app` schema for Fox
- `Canary/docs/sdds/v2/chirp.md` — primary detection SDD
- `Canary/docs/sdds/v2/fox.md` — primary case management SDD
- `Canary/docs/sdds/v2/alert.md` — alert domain SDD
- `Canary/docs/sdds/v2/data-model.md` — schema spec

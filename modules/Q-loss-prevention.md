---
classification: confidential
owner: GrowDirect LLC
type: module-article
prefix: Q
codename: Chirp + Fox
status: v1 (shipping)
sibling-modules: [T, R, N, A]
---

# Q — Loss Prevention

Q is the loss-prevention surface — the module retailers buy on day
one, the workload everyone else in this market also ships, and the
reference implementation for the [[../platform/spine-13-prefix#v3-full-spine-s-p-l-w|
W (Work Execution)]] module that will generalize this pattern to
every domain in v3.

Q decomposes into two named subsystems:

- **Chirp** — the detection engine. Reads T's parsed transaction
  stream, evaluates rules across three tiers, fires alerts.
- **Fox** — the case management surface. Promotes alerts to cases,
  manages investigation lifecycle, holds the chain-of-custody
  evidence locker.

Q is one of the [[../platform/spine-13-prefix#v1-differentiated-five-t-r-n-a-q|
Differentiated-Five]] modules at v1, and it is the most fully
implemented of the five. The detection rule catalog is frozen at
**37 rules across 10 categories**; the case management surface has
INSERT-only evidence chains enforced at the database trigger layer.

## Purpose

Q owns three jobs:

1. **Detect.** Evaluate every transaction T produces against the
   frozen rule catalog. Tier the work so that low-cost rules fire
   without DB access, mid-cost rules use Valkey-cached aggregates,
   and high-cost rules query the full schema.
2. **Alert.** Produce append-only alert records. Track lifecycle
   (created → acknowledged → escalated → resolved) with timestamped
   notes. Auto-escalate critical rules to case creation.
3. **Investigate.** Provide the human-review surface — Fox cases
   with assigned investigators, classified subjects of interest,
   chain-of-custody evidence, and resolution narratives that
   survive an LP outcome (restitution, prosecution support).

Q does **not** own:

- Transaction ingestion. That's T.
- Customer or device curation. R and N.
- Multivariate device-level anomaly detection. A.
- Generalized exception handling beyond LP. That's W in v3.

## BST cells Q populates

Q is the primary owner of the LP surface and a feeder for adjacent
Store Operations BSTs.

| Domain | BST | Q's role |
|---|---|---|
| Store Operations | **Loss Prevention Analysis** | Primary owner — Q *is* this BST |
| Store Operations | **Suspicious Activity Analysis** | Co-owner with [[A-asset-management|A]] (Q owns transaction-level; A owns device-level) |
| Store Operations | Cashier Performance Measurement | Feeder — alert frequency by employee |
| Store Operations | Service Delivery Analysis | Feeder — pipeline-health alarms (non-suppressible) |
| Customer Management | Customer Complaints Analysis | Feeder via Fox case linkage to customers |

The canonical "what LP looks like" report inventory from RBIS slide
41 — Baseline Exception, Cashier Exceptions (over/under, voids),
Inventory Discrepancy, Employee Schedule Compliance Associated with
Loss, Receiver Exception — all map to Q's rule catalog plus Fox case
classification.

## CRDM entities touched

| CRDM entity | Q's relationship | How |
|---|---|---|
| **Workflows** | **Owns** the Case subset | Fox cases are CRDM Workflows |
| Events | Reads | T's transactions are Q's input |
| People | Reads | Customer / employee FK on transactions; subjects of interest in Fox |
| Things | Reads | Device / item FK on transactions; evidence files in Fox |
| Places | Reads | Location FK on transactions; per-location alert routing |

Q's posture: **Q is a Workflow factory that derives Cases from
detected Events.** It owns the Case lifecycle but no entity
identities — those belong to R, N, and the future Places registry.

## Detection architecture (Chirp)

Three-tier rule evaluation. Tier choice is per-rule, baked into the
frozen catalog.

| Tier | When fires | DB access | Rule count |
|---|---|---|---|
| **Tier 1 — Stateless** | During webhook receipt, before Sub 2 finishes parsing | none — operates on raw payload | 6 |
| **Tier 2 — Lightweight** | After parse, against Valkey-cached windowed aggregates | Valkey only, no SQL | 9 |
| **Tier 3 — Full DB** | After parse, against `sales` schema queries | full SQLAlchemy | 22 |

Tier 1 rules are **fire-and-forget** during webhook receipt — they
add zero perceptible latency to T's webhook path. Tier 3 rules run
in the detection consumer (`sub4-detect`) and are bounded by
per-merchant query budgets.

## Rule catalog (37 frozen)

Categories, in catalog order:

| Category | Rules | Trigger surface |
|---|---|---|
| **Payment** | C-001 through C-011 (11 rules) | Payments, refunds, voids, manual entry, partial auth, no-sale |
| **Cash Drawer** | C-101 through C-104 (4 rules) | No-sale abuse, cash variance, paid-out anomaly, after-hours |
| **Order** | C-201 through C-204 (4 rules) | Discount rate, line-item void, sweethearting, untendered |
| **Timecard** | C-301 through C-303 (3 rules) | Off-clock transaction, break transaction, wrong location |
| **Void** | C-501, C-502 (2 rules) | High void rate, post-void alert |
| **Gift Card** | C-601, C-602 (2 rules) | Load velocity, drain |
| **Loyalty** | C-801 through C-804 (4 rules) | Point accumulation, bulk redemption, cross-location velocity, enrollment fraud |
| **Composite** | C-901 (1 rule) | SRA threshold breach (multi-rule aggregation) |
| **Dispute** | C-D01 through C-D03 (3 rules) | Dispute created, dispute lost, dispute velocity |
| **Invoice** | C-I01 through C-I03 (3 rules) | Overdue, charge-failed, high-value unpaid |

The catalog is **frozen** — adding a rule is a release event, not a
configuration change. Per-merchant tuning happens through threshold
overrides on existing rules, not through new-rule authoring.

## Auto-escalation to cases

Six rules auto-promote alerts to Fox cases:

- C-009 SQUARE_DELAY_HOLD (payment delay anomaly)
- C-104 AFTER_HOURS_DRAWER (cash drawer outside business hours)
- C-204 UNTENDERED_ORDER (order without matched tender)
- C-301 OFF_CLOCK_TRANSACTION (employee transaction off-clock)
- C-502 POST_VOID_ALERT (void after transaction completion)
- C-602 GIFT_CARD_DRAIN (gift card balance depletion pattern)

These are the rules where the LP signal-to-noise ratio is high
enough to skip the alert-triage step and create an investigatable
case immediately.

## Case management architecture (Fox)

Fox's tables enforce three integrity rules:

1. **`fox_cases`, `fox_subjects`, `fox_case_actions`** — operational
   records, soft-deletable. Status transitions tracked in audit
   columns.
2. **`fox_case_timeline`** — append-only audit log. Hash-chained.
   Every status transition, assignment change, evidence addition
   logs a row. Insertion order is cryptographically guaranteed.
3. **`fox_evidence`** and **`fox_evidence_access_log`** — INSERT-only,
   enforced at the PostgreSQL trigger layer. Every evidence file
   carries `(file_hash, previous_chain_hash, chain_hash)`. Access is
   logged on every read; the log itself is also INSERT-only.

This is the chain-of-custody backbone. Forensic LP outcomes
(restitution proceedings, prosecution referrals, insurance claims)
require evidence that is durable, tamper-evident, and chain-of-
custody-ordered. Fox provides this structurally.

## Case lifecycle

`fox_cases.status` transitions:

```
open → investigating → pending_review →
  → closed
  → escalated → referred_to_le
```

`fox_cases.case_type` classification:

- theft
- fraud
- policy_violation
- cash_variance
- return_abuse
- other

`fox_subjects.subject_type` classification:

- employee
- customer
- vendor
- unknown

## Schema crosswalk

Q writes across the `app` schema. **Note:** Fox tables live in `app`,
not in a dedicated `fox` schema. The Python module path
(`canary/models/fox/`) is organizational; the database schema is
`app` for all Fox tables.

| Table | Pattern | Purpose |
|---|---|---|
| `detection_rules` | seeded | Rule catalog (37 rows; not tenant-scoped) |
| `merchant_rule_config` | mutable | Per-merchant threshold overrides |
| `alerts` | append-only | Per-rule firings, scoped to merchant |
| `alert_history` | append-only | Status transitions per alert |
| `fox_cases` | mutable + soft-delete | Investigation root |
| `fox_case_alerts` | mutable junction | Cases ↔ alerts |
| `fox_case_timeline` | append-only, hash-chained | Audit log |
| `fox_case_actions` | append-only + soft-delete | Investigation outcomes |
| `fox_subjects` | mutable + soft-delete | People/entities of interest |
| `fox_evidence` | INSERT-only, hash-chained, trigger-enforced | Chain-of-custody evidence |
| `fox_evidence_access_log` | INSERT-only, trigger-enforced | Evidence access audit |

Q reads from `sales.*` (T's surface) for rule evaluation and from
`app.customers` / `sales.devices` for subject context.

## Service-name markers (v0.7 microservice index)

| Service slot | Responsibility | Currently lives in |
|---|---|---|
| `q-chirp-stateless` | Tier 1 stateless rule evaluation (in-process during webhook) | `canary/services/chirp/stateless_engine.py` |
| `q-chirp-engine` | Tier 2/3 evaluation (consumer service) | `canary/services/chirp/rule_engine.py` |
| `q-chirp-thresholds` | Per-merchant threshold management + Valkey cache | `canary/services/chirp/threshold_manager.py` |
| `q-chirp-rules` | Frozen rule catalog | `canary/services/chirp/rule_definitions.py` |
| `q-alert-lifecycle` | TTL, archival, age decay on alerts | `canary/services/alert_lifecycle.py` |
| `q-fox-case` | Case CRUD, lifecycle transitions | `canary/services/fox/case_service.py` |
| `q-fox-evidence-chain` | Chain-hash verification | `canary/services/evidence_chain.py` |
| `q-chirp-mcp` | Chirp MCP tools (10 tools) | `canary/services/chirp/tools.py` + `canary/blueprints/chirp_mcp.py` |
| `q-fox-mcp` | Fox MCP tools (8 tools) | `canary/services/fox/tools.py` + `canary/blueprints/fox_mcp.py` |

**Perpetual-vs-period boundary.** Canary owns: detection (Chirp) + case (Fox). Merchant tool owns: insurance claims / restitution tracking (in merchant HR or accounting). Default implementation route: `integrated-hybrid`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (Q's inputs):

- T's `canary:detection` Valkey stream — every parsed transaction
- T's evidence chain (for case-evidence integrity verification)
- R's customer registry (for customer-as-subject context)
- N's device registry (for device-as-context context)
- Future A's signals (when A is built — A produces Chirp-style
  alerts on the same channel)

**Downstream consumers** (who reads Q):

- Investigator agents via `canary-fox` MCP tools
- Threshold-tuning workflows via `canary-chirp` MCP tools
- Notification subsystems (alert routing — see open question 4)
- Future v3 W (Work Execution) — generalized exception surface
  reads Q's case patterns

## Agent surface

Two MCP servers:

- **`canary-chirp`** — 10 tools. Rule introspection, threshold
  management, alert search, alert lifecycle ops, sensitivity-preset
  management.
- **`canary-fox`** — 8 tools. Case CRUD, subject management,
  evidence upload + access, timeline reads, case search.

Q is the most agent-rich module on the v1 spine. The investigator
workflow is heavily agent-mediated by design — the human reviews and
decides; the agent gathers context and prepares evidence.

## Security posture

- **Auth.** Tenant-scoped at every read and write. Case access
  honors investigator-assignment when configured.
- **PII handling.** Subjects of interest may carry PII (employee
  names, customer references). Stored under tenant scope; access
  logged via `fox_evidence_access_log` for evidence reads.
- **Evidence integrity.** Trigger-enforced INSERT-only on
  `fox_evidence` — no UPDATE, no DELETE possible at the database
  layer. Chain hash is `SHA-256(previous_chain_hash || file_hash)`;
  any tamper attempt fails verification.
- **Pipeline-health alarm.** Non-suppressible per
  [[../platform/overview|the canonical detection-and-notification
  pattern]]. Operators must distinguish "no alerts because nothing's
  wrong" from "no alerts because we lost visibility."

## Open questions

1. **HR / law-enforcement referral notification.** Cases that
   transition to `referred_to_le` need a notification workflow to
   internal HR + legal. Not yet built. Marked deferred in code
   comments.
2. **External evidence storage.** Fox stores file references and
   hashes; the file blobs themselves currently sit on local disk.
   S3/blob-store integration, virus scanning on upload, and EXIF /
   metadata extraction are deferred.
3. **Cross-DB subject linking.** A subject of interest who's an
   employee at one merchant and a customer at another (or a
   contractor across multiple) has no platform-level identity link.
   Pairs with R's `external_identities` work.
4. **Sensitivity presets.** Chirp supports per-merchant threshold
   overrides; "presets" (conservative / balanced / aggressive bundles
   that adjust many thresholds at once) are documented in the SDD
   but the UX for switching presets is not yet built.

## Roadmap status

- **v1 (shipping)** — Chirp 37-rule catalog. Three-tier evaluation.
  Fox case management with INSERT-only evidence chain. Two MCP
  surfaces.
- **v1.x** — Notification workflows, S3 evidence storage, sensitivity
  preset UX.
- **v2** — Cross-merchant subject linking. Investigator-agent tooling
  expansion. A-source signal consumption (when A ships).
- **v3** — Generalize the Chirp+Fox pattern into [[../platform/spine-13-prefix#v3-full-spine-s-p-l-w|
  W (Work Execution)]]: same detection-rule + case-management shape,
  applied to merchandising, inventory, vendor-performance, labor,
  and asset-condition domains.

## Related

- [[../platform/spine-13-prefix|13-prefix spine]]
- [[../platform/crdm|Canonical Retail Data Model]]
- [[../platform/overview|Platform overview]] — §What makes it
  different (evidence-first)
- [[../platform/worked-example-solex|Solex worked example]] —
  produces the LP signal Q observes
- [[T-transaction-pipeline]] — Q's primary input
- [[R-customer]] — sibling Differentiated-Five module
- [[N-device]] — sibling Differentiated-Five module
- [[A-asset-management]] — future signal source for Q

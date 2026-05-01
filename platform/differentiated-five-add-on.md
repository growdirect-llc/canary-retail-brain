---
classification: confidential
owner: GrowDirect LLC
type: platform-doc
date: 2026-04-24
tags: [differentiated-five, positioning, v1, smb-retail]
nav_order: 6

---

# The Differentiated-Five — T + R + N + A + Q

Canary Retail's v1 shipping platform is organized as a five-module bundle called the Differentiated-Five (abbreviated T+R+N+A+Q). These five modules represent the add-on layer that distinguishes Canary Retail as a platform above the commodity loss-prevention baseline that every retail-tech vendor ships.

## The bundle in one sentence

**The v1 add-on layer that closes the gap between SMB POS and enterprise retail tech.**

Concrete: T and Q are what every LP vendor sells (transaction ingestion, detection rules). R, N, and A are what enterprise retail platforms use but no SMB-tier vendor productizes. Canary ships all five as one integrated platform.

## What v1 is worth — the prize, sized

The Canary Retail Diagnostic produced for an archetype SMB specialty merchant (8 stores, £12m revenue, illustrative — full case study at [[../case-studies/canary-retail-diagnostic-archetype]]) quantified the v1 LP prize at **£280k–£420k of annual EBIT uplift** for that archetype. The diagnostic decomposed the figure to specific Chirp rule activations:

- **OFF_CLOCK_TRANSACTION (C-301)** — eliminating ghost-employee + post-shift theft patterns
- **UNTENDERED_ORDER (C-204)** — closing the no-tender shrink hole that POS reports cannot see
- **POST_VOID (C-502)** — surfacing void-after-tender patterns invisible to standard reports
- **AFTER_HOURS_DRAWER (C-104)** — flagging cash-drawer access outside business hours
- **GIFT_CARD_DRAIN (C-602)** — detecting gift-card-as-cash-out exfiltration patterns
- **SQUARE_DELAY_HOLD (C-009)** — escalating Square's own delayed-payment holds for review

**v1 is the wedge that gets Canary in the door.** The bigger prize comes from v2 (£1.2m–£1.8m for inventory + replenishment), but no merchant signs up for v2 without the v1 wedge proving the platform first. The Differentiated-Five is calibrated to deliver a credible, quantified, audit-trailed prize in Phase 1 (parallel-observer mode, zero adoption friction per the [[perpetual-vs-period-boundary|staged migration]]).

The prize size is per-archetype-merchant — merchants will compute their own when the VSM ([[../../GrowDirect/Brain/wiki/growdirect-viewpoint-virtual-store-manager|Virtual Store Manager]]) runs the diagnostic against their actual transaction stream in Phase 1.

## The five modules

### T — Transaction Pipeline

**POS-agnostic ingestion; seal → parse → merkle → detect**

T is the inbound edge of the entire platform. Every operational signal — every detection, metric, case, and ARTS projection — traces back to a transaction that landed through T. T owns three responsibilities:

1. Receive retail events from external sources (today: Square webhooks; tomorrow: Shopify, Clover, generic POSLog feeds)
2. Seal every received event into an append-only, hash-chained evidence record **before** any business logic runs — the raw bytes are hashed, not a parsed shape, so later parser changes don't invalidate prior evidence
3. Stream sealed events to downstream subscribers (Q, R, N, A)

T implements a four-stage Valkey-streamed pipeline: webhook → seal → parse → merkle → detect. The architecture is patent-critical because it hashes raw bytes *before* JSON parsing. Parsing is fallible; hashing is not. Every downstream integrity claim depends on this ordering.

T currently accepts events from three sources: webhooks (push, near-real-time, signed), polling (pull, periodic, for backfill), and batch (file or admin-initiated import). All three paths funnel into the same seal → parse → merkle → detect pipeline.

### C — Customer

**ARTS Customer Model; unified customer entity**

R owns the People entity in the CRDM frame, specifically the customer subset. It is the module retailers ask about second (after the loss-prevention pitch) and the module that positions Canary as more than a point solution: every customer identifier on every transaction routes through R, every channel that talks to a customer routes through R, and every downstream projection that asks "who is this person across our business" reads R.

R's posture is deliberately minimal at v1: no PII at rest, no stored profile beyond aggregate metrics, only the vendor identifier and the things you can compute from the transaction stream. This is an architectural choice, not a roadmap gap. R owns three responsibilities:

1. Curate the customer entity — one row per customer per merchant, keyed by the upstream vendor's identifier (Square's `customer_id` today)
2. Compute derived customer state — lifetime value, transaction count, first-seen, last-seen — facts you can derive from the transaction ledger without storing anything the customer didn't already give the merchant's POS
3. Provide the agent and analyst surface for customer questions — "Who is this person?" "What have they bought?" "Are they a regular or a one-off?" — via read-only MCP tools

The privacy-first posture is load-bearing: the `customers` table has no string columns for personal data. Customer phone numbers from Square loyalty webhooks are hashed at the parser layer before they reach R. The consequence: a full database exfiltration of R yields vendor customer IDs and integer aggregates; re-identification requires also breaching Square.

R adopts the ARTS Customer Model's identity layer and defers demographic and contact layers. Minimal fields at v1: `square_customer_id`, `lifetime_value_cents`, `first_seen_at`, `last_seen_at`, `transaction_count`. When workflows demand Name/Email/Address, R reaches back to Square. When a retailer wants to store PII for first-party agent workflows, that's an opt-in extension table; the default is off.

### N — Device

**ARTS Device Model; asset registry for POS, scanners, IoT**

N owns the device subset of CRDM Things. Every POS terminal, scanner, register, kitchen display, IoT sensor, and physical store device is a first-class tracked entity in N. This is a deliberate departure from how SMB retail tech treats devices today: most platforms treat a register as an attribute on a transaction (`device_id` as a string field), not as an entity with its own lifecycle, identity, and analytics surface.

N's model and schema are production-ready; the live Square sync is gated on an OAuth scope expansion. The platform can ingest device records via webhook and direct API call; the self-service merchant onboarding-time pull awaits scope.

N owns three responsibilities:

1. Curate the device entity — one row per device per merchant, keyed by the upstream vendor's identifier (Square's `device_id` today)
2. Hold device telemetry — software version, OS version, network posture, battery state, charging state — every operational signal the vendor exposes about the device, stored as both typed columns (for query) and a JSONB safety net (for forward compatibility)
3. Provide the asset registry that [[A-asset-management|A]] runs anomaly detection against — per-device baselines and multivariate threat scoring require N as the FK source

N adopts the ARTS Device Model with full type coverage: DeviceID, SerialNumber, DeviceName, OSVersion, ApplicationVersion, NetworkAddress, NetworkConnection, PowerState, LocationID, Manufacturer/Model. The JSONB `raw_square_object` field carries the complete Square API response; any ARTS field the vendor exposes that isn't yet typed in a column is still queryable from JSONB.

Devices live in the `sales` schema, not `app`, because they are ingested operational facts from a vendor, not configuration state owned by Canary.

### A — Asset Management

**Bubble — anomaly detection over the asset registry, per-store baselines**

A — codename Bubble — is where Canary's asset-tier edge emerges. While Q detects anomalies in the *transaction stream* ("this transaction looks wrong"), A detects anomalies in the *device estate* ("this device is acting wrong").

A's purpose is to maintain per-device baselines and detect when devices depart from expected behavior. A "baseline" is the expected range of behavior for a device in a store at a specific time-of-day-of-week — derived from observed history. Baselines update continuously; A holds the projection. When a device's observed behavior departs from its baseline by more than a configured tolerance, A fires a signal that becomes a Q alert (or, in v3, a W work item) for human review.

A is the multivariate anomaly-detection workload on the v1 spine. Q's rules are largely univariate threshold checks; A's bubble model is a different shape: it holds multiple dimensions (transaction count per hour, average transaction value, void rate, refund rate, network posture, time-between-transactions, employee-mix) and fires a single signal when the device departs the "bubble" across those dimensions.

**v1 status reality check:** The spine ships A as v1 because the architectural commitment is real and the infrastructure is in place (baseline_calculator, metrics risk tables, N's registry). The dedicated A-specific surface — anomaly rules, per-device baselines, the Bubble detection layer — is in design (not yet code-complete). The foundation is built; the A-specific projection and detection layer is what v1.x needs to ship.

### Q — Loss Prevention

**Detection engine (Chirp) + case management (Fox); 37 rules across 10 categories**

Q is the loss-prevention surface — the reference implementation for the [[spine-13-prefix|W (Execution)]] module that will generalize this pattern to every domain in v3. Q decomposes into two named subsystems:

- **Chirp** — the detection engine. Reads T's parsed transaction stream, evaluates rules across three tiers, fires alerts.
- **Fox** — the case management surface. Promotes alerts to cases, manages investigation lifecycle, holds the chain-of-custody evidence locker.

Q's detection rule catalog is frozen at **37 rules across 10 categories**: Payment (11 rules), Cash Drawer (4), Order (4), Timecard (3), Void (2), Gift Card (2), Loyalty (4), Composite (1), Dispute (3), Invoice (3). The catalog is frozen — adding a rule is a release event, not a configuration change. Per-merchant tuning happens through threshold overrides on existing rules, not through new-rule authoring.

Chirp evaluates rules in three tiers:

| Tier | When fires | DB access | Rule count |
|---|---|---|---|
| Tier 1 — Stateless | During webhook receipt, before Sub 2 finishes parsing | none — operates on raw payload | 6 |
| Tier 2 — Lightweight | After parse, against Valkey-cached windowed aggregates | Valkey only, no SQL | 9 |
| Tier 3 — Full DB | After parse, against sales schema queries | full SQLAlchemy | 22 |

Tier 1 rules are fire-and-forget during webhook receipt — they add zero perceptible latency to T's webhook path. Six rules auto-promote alerts to Fox cases (C-009, C-104, C-204, C-301, C-502, C-602) — these are the rules where signal-to-noise is high enough to skip alert triage and create investigatable cases immediately.

Fox provides the case management surface with three integrity guarantees:

1. `fox_cases`, `fox_subjects`, `fox_case_actions` are operational records, soft-deletable; status transitions tracked in audit columns
2. `fox_case_timeline` is append-only and hash-chained — every status transition, assignment change, evidence addition logs a row; insertion order is cryptographically guaranteed
3. `fox_evidence` and `fox_evidence_access_log` are INSERT-only, enforced at the PostgreSQL trigger layer — no UPDATE, no DELETE possible. Every evidence file carries chain hashes; any tamper attempt fails verification

This is the chain-of-custody backbone. LP outcomes (restitution, prosecution referrals, insurance claims) require evidence that is durable, tamper-evident, and chain-of-custody-ordered. Fox provides this structurally.

## The market gap — why R+N+A are enterprise-only today

T and Q are a commodity. Every LP vendor ships transaction ingestion and detection rules. Most ship them poorly (missing seal, minimal customization, no cross-vendor support), but they ship them. A retailer evaluating Canary against Square Cash Register or Toast LP sees the same rule catalog and similar detection capability.

R+N+A are not a commodity at SMB tier. Enterprise platforms (SAP, Oracle Retail, Salesforce Commerce Cloud) ship them because enterprise buyers demand unified customer identity across channels, device-as-entity modeling, and multivariate asset anomaly detection. These are table-stakes in enterprise retail. SMB-tier tools don't ship them because:

1. **Multi-channel customer identity is complex.** A customer who appears in Square in-store and Shopify online needs cross-vendor identity linkage. The matching policy (deterministic? probabilistic? customer-confirmed?) is hard. The privacy and GDPR implications are harder. Most SMB-tier vendors avoid the problem.

2. **Device-as-entity modeling is unfamiliar to SMB vendors.** The architecture is "transaction has device_id string" rather than "transaction FKs to device entity." Shifting the model requires schema rework, telemetry capture, device lifecycle management, and new query patterns. Most SMB tools don't bother.

3. **Multivariate anomaly scoring is expensive and requires scale.** Building per-device baselines, tracking multivariate dimensions, computing Mahalanobis distance or isolation-forest scores — these operations are technically hard and need operational signal from dozens of devices before they're statistically valid. A 20-device deployment makes per-device baselines noisy. Enterprise operations have 500+ devices; SMB average is 5–10. The ROI threshold is higher.

Because R+N+A are missing, an SMB retailer who wants them has to buy separate systems: a CDP or customer-data platform for R, an MDM or asset-management platform for N, and a separate analytics tool for A. This is where Canary's platform thesis emerges.

## The platform thesis

From the [[spine-13-prefix|13-prefix spine]]:

> You get the LP module everyone charges for, plus the customer / device / asset tier nobody charges for, because they're the same platform.

This is the load-bearing sentence. It captures why Canary Retail can afford to ship R+N+A at v1 when competitors can't:

- **Single operational schema.** People × Places × Things × Events × Workflows. R reads the People slot; N reads the Things slot; both feed into the same CRDM. No separate customer identity system, no separate asset management platform. One schema, one tenant scoping, one audit trail.
- **Unified data pipeline.** T's transaction stream populates R (customer upserts), N (device first-seen), A (baseline observation), and Q (rule evaluation). The stream flows once; every downstream consumer samples what it needs. No multi-vendor data sync or warehouse federation.
- **Shared evidence chain.** T seals raw bytes; Q's Fox cases preserve evidence in append-only chains. This infrastructure is reused by R (customer audit trail), N (device telemetry versioning), and A (baseline revision history). One integrity model, deployed across all five modules.
- **Single agent mesh.** Every module exposes MCP tools. The agent population is unified — one operational team, one set of agent tools, one memory bus for context recall. Not five separate agent populations.

The corollary: Canary can ship R+N+A as core platform because they are not an add-on feature pack bolted onto an existing loss-prevention engine. They are peers on the same operational substrate. The cost of building and maintaining them is shared across the entire platform, not isolated in a "premium tier."

## How v1 sets up v2 and v3

The Differentiated-Five is not the end state; it is the foundation.

Once a retailer runs on v1 — transaction ingestion, loss detection, customer unity, device registry, anomaly baselines — the next operational ask is almost always: "Can you also handle our buying, inventory movement, and financial flow?" This is where v2 ships four more modules (C/D/F/J) to close the commercial, distribution, finance, and forecast-order gaps.

And once v2 is live, v3 generalizes the Chirp+Fox pattern — detection rules, case management, evidence chain, alert routing — to every operational domain: merchandising discrepancies (S), promotion execution (P), labor anomalies (L), and W (Execution) as the unified exception surface.

Each ring on the spine sits on the previous ring's foundation: v2 assumes T/R/N/A/Q are live and proven; v3 assumes v2 is operational. The operational schema doesn't fork at v2; it expands. New modules read and write the same People × Places × Things × Events × Workflows frame. New detection rules feed into the same Fox case management surface. New agent meshes extend the same MCP toolkit and memory bus.

This is why Canary ships as a platform, not a point solution. The first-ring Differentiated-Five is small enough to be buildable, deep enough to be differentiated, and foundational enough that subsequent rings are not speculative — they are extensions of a proven model.

## Related

- [[spine-13-prefix|13-prefix spine]] — full module catalog and v2/v3 roadmap
- [[overview|Platform overview]] — positioning and SMB collapse evidence
- [[arts-adoption|ARTS Adoption]] — standards alignment (T/R/N)
- [[T-transaction-pipeline|T (Transaction Pipeline)]]
- [[R-customer|C (Customer)]]
- [[N-device|N (Device)]]
- [[A-asset-management|A (Asset Management)]]
- [[Q-loss-prevention|Q (Loss Prevention)]]

## Sources

- [[spine-13-prefix|13-prefix spine]] — v1 differentiated-five definition and positioning
- [[overview|Platform overview]] — SMB collapse thesis and platform market positioning
- [[T-transaction-pipeline|T (Transaction Pipeline)]] — seal → parse → merkle → detect architecture
- [[R-customer|C (Customer)]] — privacy-first posture and ARTS mapping
- [[N-device|N (Device)]] — device-as-entity and ARTS mapping
- [[A-asset-management|A (Asset Management)]] — Bubble design and baseline architecture
- [[Q-loss-prevention|Q (Loss Prevention)]] — Chirp + Fox, 37-rule catalog, chain-of-custody

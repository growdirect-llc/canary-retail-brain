---
card-type: platform-thesis
card-id: platform-stack-commitment
card-version: 1
domain: platform
layer: cross-cutting
status: approved
agent: ALX
tags: [stack, gcp, vendor, buy-vs-build, anti-amazon, no-hand-rolling, core-ip, saas, cloud-commitment, walmart-precedent]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

Canary's vendor and platform commitment posture. We run on Google Cloud Platform end-to-end. We buy managed services for everything that isn't core IP or pure retail-domain logic. We hand-roll only the patent-protected algorithms, the agent topology, and the retail-specific business rules that make us defensible. The discipline is **"no hand-rolling outside core competency."**

## Purpose

Sole-founder operations cannot carry the cognitive load of multi-cloud, multi-vendor, custom-everything architectures. Every minute spent rebuilding a problem someone else has already solved at scale (auth, billing, email, monitoring) is a minute not spent on the platform's actual moat. The discipline of vendor commitment IS the operational scalability strategy. It is also a credentialing statement — partners, investors, auditors, and regulators all read "we run on Google" as a proxy for an entire compliance and security baseline they would otherwise have to evaluate piece by piece.

## The three categories

Three buckets, each with a clear treatment rule:

**Core IP** — patent-protected algorithms, evidentiary architecture, ILDWAC, RaaS chain, multi-POS substrate, the agent PMO topology, the SDD methodology itself. **Hand-roll. This IS the company.**

**Pure domain** — retail-specific business logic that's NOT generic SaaS: item master, receiving disposition, three-way match, OTB enforcement, return fraud scoring, vendor scorecard logic. **Hand-roll. Encoded in the SDD library.**

**Commodity SaaS plumbing** — compute, DB, auth, email, billing, internal admin, observability, CI/CD, error tracking, secrets, mobile shell, embedded analytics. **Buy. Rebuilding any of these is technical debt before you ship.**

The discipline only works if you actively enforce it. The pull to hand-roll "just this small piece" is constant.

## The substrate (GCP — all managed)

| Need | Service |
|---|---|
| Compute | Cloud Run |
| Postgres 17 + pgvector | Cloud SQL |
| Cache / queue (Valkey/Redis) | Memorystore |
| Async / events | Pub/Sub + Cloud Tasks + Eventarc |
| Object storage | Cloud Storage |
| Secrets | Secret Manager |
| Observability | Cloud Logging + Monitoring + Trace + Profiler + Error Reporting |
| CI/CD | Cloud Build → Artifact Registry |
| DNS / TLS | Cloud DNS + Certificate Manager |
| Network edge | Cloud Load Balancing + Cloud Armor |
| Auth | Identity Platform (Firebase Auth backend) |
| AI / inference | Vertex AI (hosts Anthropic Claude + embeddings) |
| Workspace | Google Workspace (email, collab, docs) |
| Web analytics | GA4 + GSC + Tag Manager + Looker Studio |

Roughly 14 services, one vendor relationship, one billing account, one IAM mental model.

## Per-vendor SaaS plumbing (the "not Google" 20%)

Where Google doesn't compete:

| Need | Vendor | Why not Google |
|---|---|---|
| Subscription billing | Stripe | Google has no equivalent |
| Transactional email at volume | SendGrid (or Postmark) | Workspace SMTP relay caps at ~2k/day |
| SMS | Twilio | Industry default |
| Internal admin | Retool | Builds in days against Cloud SQL |
| Embedded merchant analytics | Metabase Cloud | Looker Studio is for us; embedded for merchants is different |
| Error tracking (frontend) | Sentry | Cloud Error Reporting handles backend |
| API docs portal | Mintlify | OpenAPI to portal in one day |
| Bitcoin L2 anchor | OrdinalsBot | Specialist service |

Roughly 8 vendor relationships outside of Google.

## What stays hand-rolled — the IP

The framework. Everything else is substrate:

- TSP pipeline (hash-before-parse, chain hash, Merkle inscription) — patent-critical
- ILDWAC five-dimension cost model in satoshis
- Chirp detection rules (37 retail-domain rules)
- Fox case management with hash chain
- Hawk return fraud scoring
- Multi-POS adapter substrate
- CRDM (Canonical Retail Data Model) — ARTS-aligned but Canary-specific
- The agent topology — Controller, 27 domain agents, infrastructure agents
- MCP tool surfaces per service
- L402 + Lightning integration — see [[platform-l402-ildwac-moat]]
- The SDD library + Brain wiki + memory bus content
- Multi-tier assortment routing — see [[platform-multi-tier-assortment]]
- Per-subject cryptographic erasure pattern — see [[platform-cryptographic-erasure]]
- Keyed PII hashing — see [[platform-pii-hashing]]

## Why not AWS — the positioning

Three of the largest grocery retailers in the US (Walmart, Target, Kroger) explicitly avoid AWS for the same structural reason: every dollar paid to AWS funds Amazon's retail operations, which compete with the retailers paying. For a retail-tools SaaS, hosting on the platform that funds your customers' direct competitor is a misalignment that VARs and merchants name immediately.

The position is the orthodox one from the customer side, not the heterodox one. Walmart bans suppliers from running on AWS. Target avoids it. Kroger has migrated off. We are joining established retail-vendor practice, not breaking from it.

The line: **"We don't run on Amazon's infrastructure because we work for the merchants Amazon is hunting."**

## Why Google — the honest qualifier

Google has its own retail conflicts:

- Google Search Ads / Shopping Ads compete for retailer marketing dollars
- Google Shopping mediates discovery on Google's terms
- Vertex AI / Gemini scrape retailer content for AI training
- BigQuery for Retailers competes for data warehouse spend

We are not picking Google because Google is altruistic. We are picking the lesser conflict — Google's friction is at the discovery / advertising / data layer, not at the transaction layer where Amazon competes directly. The transaction-layer conflict (Amazon) is acute and existential. The discovery-layer conflict (Google) is structural and indirect. For a retail-tools SaaS, the difference matters.

The framing: **"We picked Google because Amazon directly competes with our customers and Google doesn't. Google has its own interests in retail and we keep our eyes open about them. We pick the lesser conflict and we don't pretend it's a moral choice."**

## The 99.99% chained-SLA reality

Each Google service hits its individual SLA, but chained SLAs multiply down. A request touching Cloud Run + Cloud SQL + Pub/Sub + Cloud Storage + Memorystore has an upper bound of ~99.7% — about 26 hours of downtime per year, not 52 minutes.

The 99.99% target is achieved by architectural patterns ON TOP of the substrate:

- Idempotency at every write boundary (TSP invariant #5)
- Append-only / hash-chain (raas, fox, evidence_records)
- Pub/Sub fan-out + dead letter (TSP)
- Async by default (hot path returns fast; slow work runs in workers)
- Per-merchant blast radius (`WHERE merchant_id = $1` at every query)
- Cryptographic erasure (preserves chain integrity through erasure)
- Graceful degradation (Owl down → direct rule eval; anchor down → queue async)

The substrate gets us to 99.95% per service. Our framework gets us to 99.99% end-to-end.

## Insurance and compliance — the prerequisite framing

Being on GCP isn't insurance. It's the prerequisite to BEING insured. Cyber insurance underwriters have a security questionnaire that gates the quote — encryption at rest, MFA, IAM, audit logging, certifications, incident response plan, data classification policy. Self-hosted or hybrid setups fail the questionnaire or get punitively priced.

The GCP commitment satisfies most of the questionnaire automatically. The remaining items are the compliance dispatches we filed (GRO-686 through GRO-699). Closing those dispatches converts "underwriteable" into "well-covered at reasonable rates." The Workspace fee is the entry ticket; the dispatches are the policy itself.

## Invariants

- Anything that isn't core IP or pure retail-domain logic gets bought, not built. The discipline only works if it's enforced; the pull to hand-roll one more piece is constant.
- Every vendor commitment is to a single primary vendor for its category. Multi-vendor for one category (two billing providers, two email providers) is the bug to avoid, not the resilience strategy.
- Vendor commitments are assessed on operational fit, cost/value, and conflict-surface — not on which vendor is "the good guy." Every platform layer has competing interests. We navigate them with eyes open.
- The substrate's SLA is necessary but not sufficient. End-to-end resilience is built on top via idempotency, append-only, async, blast-radius, and graceful degradation patterns.

## Sources

- The full `docs/sdds/go-handoff/` corpus — every SDD assumes this commitment
- `docs/sdds/go-handoff/data-classification-inventory.md` — the compliance dispatch backlog (GRO-686 → GRO-699) is also the insurance-readiness checklist
- 2026-04-29 GCP commitment thread

## Related

- [[platform-architectural-continuity]] — the conceptual frame for why our architecture is composed of proven primitives
- [[platform-l402-ildwac-moat]] — the composition that uses Bitcoin / Lightning at the agent-billing layer
- [[platform-data-classification]] — the four-tier scheme that drives encryption and retention
- [[platform-pii-hashing]] — keyed-HMAC standard
- [[platform-cryptographic-erasure]] — per-subject DEK pattern for append-only tables
- [[platform-multi-tier-assortment]] — store / warehouse / expanded routing
- [[raas-receipt-as-a-service]] — the chain backbone
- [[platform-thesis]] — broader platform context

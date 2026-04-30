---
title: Engineering Posture
classification: confidential
---

# Engineering posture

For the IT partner. The non-functional requirements, scale posture, security baseline, and compliance design. Day-one architecture, not a roadmap.

## Stack

GCP-native end to end. Single primary cloud. No multi-cloud, no AWS — Walmart / Target / Kroger anti-Amazon posture.

| Layer | Choice |
|---|---|
| Cloud | Google Cloud Platform |
| Compute | Cloud Run (autoscaling, request-driven) |
| Database | Cloud SQL Postgres 17 + pgvector + pg_trgm extensions |
| Connection pooling | PgBouncer (transaction-mode, max 200 clients per service) |
| Cache | Memorystore (Valkey-compatible) |
| Async | Pub/Sub + Cloud Tasks + Eventarc |
| AI / inference | Vertex AI (Anthropic Claude + embeddings) |
| Object storage | Cloud Storage with CMEK via Cloud KMS |
| Secrets | GCP Secret Manager (no env files in production) |
| Edge | Cloud Load Balancing + Cloud Armor + Certificate Manager + Cloud DNS |
| Observability | Cloud Logging + Monitoring + Trace + Profiler + Error Reporting |
| Language | Go 1.21+ |
| HTTP | Chi |
| DB driver | pgx + sqlc (type-safe SQL queries) |
| Migrations | golang-migrate or goose |
| Identity | Home-grown service with `coreos/go-oidc`, `crewjam/saml`, `go-ldap/ldap`, `elimity-com/scim` library stack — federated to customer's IdP, no Identity Platform dependency |

The discipline: **anything not core IP or pure retail-domain logic gets bought, not built.** What's core IP: TSP pipeline, ILDWAC cost model, RaaS receipt chain, multi-POS adapter substrate, agent topology, the SDD library itself. What's bought: every GCP service plus eight specialist SaaS for billing (Stripe), email (SendGrid), SMS (Twilio), internal admin (Retool), embedded merchant analytics (Metabase Cloud), error tracking (Sentry), API docs (Mintlify), Bitcoin L2 anchor (OrdinalsBot — when enabled).

## Multi-tenancy — schema-per-tenant

Every merchant gets a dedicated Postgres schema (`tenant_{merchant_uuid}`). Application code sets `SET search_path TO tenant_{merchant_id}, public` per request based on the JWT `merchant_id` claim. This produces strong isolation at the database layer — a query without a tenant context resolves nothing in tenant-scoped tables.

| Schema | Scope | Contents |
|---|---|---|
| `public` | Global | Reference data: source systems, role definitions, detection rule library, lookup tables |
| `tenant_{merchant_id}` | Per-merchant | All operational tables — alerts, cases, employees, products, locations, transactions, evidence |
| `audit` | Cross-cutting | Authentication events, role changes, cross-tenant query audit, key rotations |
| `analytics` | Cross-tenant materialized | Aggregated rollups — anonymized; never row-level tenant content |

**Cross-tenant admin queries** use a dedicated admin role with explicit grants and full audit logging. Cross-tenant analytics are pre-materialized into the `analytics` schema; admin queries hit the materialization, not the tenant schemas, to avoid lock contention.

**Sharding posture:** V1 Cloud SQL primary + 2 read replicas (comfortable to ~5,000 tenants). V2 trigger: AlloyDB for Postgres when tenant count exceeds 5,000 OR p95 query latency on the largest tenant exceeds 500ms. V3 trigger: application-level sharding by `org_id` range when AlloyDB read replicas no longer suffice.

## Scale posture

| Surface | Target |
|---|---|
| Compute | Horizontal via Cloud Run, autoscale per service to demand |
| Reads | Cloud SQL read replicas + Valkey hot cache |
| Writes | Primary; PgBouncer transaction-mode pooling |
| Async | Pub/Sub for fan-out, Cloud Tasks for delayed/scheduled, Eventarc for cross-service routing |
| Cache | Memorystore Valkey, prefixed `raas:{merchant_id}:{domain}:{key}` (per-tenant blast radius) |
| Per-merchant query scope | Always `WHERE merchant_id = $1` or schema-scoped via `search_path` |

Throughput target per merchant namespace: **500K events per hour sustained write throughput** under nominal load, with degradation-free concurrent OLTP at transaction volumes well below the batch ceiling. Conservative against modern Postgres on GCP — the constraint is network ingress and hash computation, not the database write path.

MCP tool latency targets (P99 under nominal load):

| Tool class | P99 target |
|---|---|
| Namespace read (Valkey hot) | <10ms |
| Event log query (recent, indexed) | <100ms |
| Event write + hash + chain entry | <2s |
| Smart contract evaluation (three-way match) | <500ms |
| `verify_chain()` external call | <1s |

## Security baseline

**Encryption everywhere.**

| Layer | Mechanism |
|---|---|
| At rest (DB) | Cloud SQL CMEK with Cloud KMS (customer-managed keys) |
| At rest (object storage) | Cloud Storage CMEK with Cloud KMS |
| At rest (field-level Restricted / Sensitive) | AES-256-GCM via internal security primitives |
| In transit (external) | TLS 1.3 only via Cloud Load Balancing |
| In transit (service-to-service) | mTLS via Cloud Run service mesh |
| Secrets | GCP Secret Manager (never env files in production) |
| Per-subject DEK (PII in append-only tables) | Cryptographic erasure pattern: per-customer key in a mutable table; destroy the key, the ciphertext becomes unreadable, the chain stays intact |
| PII lookup hashes | HMAC-SHA256 with per-domain keyed-hash secrets — plain SHA-256 prohibited for any PII whose plaintext domain is enumerable |

**Network perimeter.**

- VPC-SC perimeter around Cloud SQL + Memorystore + Cloud Storage + Vertex AI + Secret Manager
- Cloud Armor at the edge — DDoS protection + WAF rules
- All ingress through Cloud Load Balancing → Cloud Run
- Egress via VPC NAT for external dependencies
- Cloud SQL on private IP only — public IP never enabled

**IAM.**

- Per-service Cloud Run service accounts with minimum required IAM bindings
- IAM database authentication for human admin; service accounts via Cloud SQL Auth Proxy with per-service IAM identity
- No service has cross-tenant default access; cross-tenant grants are explicit, audited, time-bounded

**Audit.**

- Cloud Audit Logs at Admin Activity, Data Access, and System Event tiers
- Application-level audit logs to the `audit` schema (per-tenant)
- Authentication events, role changes, cross-tenant queries, key rotations, encryption key operations all written to `audit`
- Audit log access itself is audited

## Backup, DR, SLA

**Backup:**

- PITR enabled with 7-day continuous recovery window
- Daily automated backups, 35-day retention
- Weekly logical export to Cloud Storage with 7-year retention for financial data
- Per-tenant restore via `pg_dump --schema={tenant_schema}` + `pg_restore` to a recovery instance

**Disaster recovery:**

- Cross-region read replica in a different GCP region
- **RPO: 5 minutes** (continuous WAL streaming)
- **RTO: 30 minutes** (failover + DNS swap)
- Quarterly DR drill — actual failover, actual replica serving, actual fail-back, documented in runbook

**Production SLAs:**

| Surface | Uptime | RPO | RTO |
|---|---|---|---|
| Platform overall | 99.95% | 5 min | 30 min |
| Customer-facing API | 99.9% | 5 min | 30 min |
| POS write path (highest tier) | 99.95% | 5 min | 15 min |
| Internal services (analytics, reporting) | 99.5% | 1 hour | 4 hours |
| Audit log ingestion | 99.99% | 0 (sync) | 5 min |

**Breach notification SLA:** 72 hours per GDPR. Internal target: 24 hours from confirmed breach to merchant notification.

## Compliance posture

| Standard | Posture | Audit target |
|---|---|---|
| SOC 2 Type 2 | Day-one design — controls baked in; readiness audit at month 6 | Month 12 |
| ISO 27001 | Alignment from day one; certification optional for early customers, required for enterprise tier | Month 24 |
| PCI DSS | Level 4 minimum (small merchants); Level 2 architecture readiness | Continuous |
| GDPR | Cryptographic erasure pattern, DSAR pipeline, data classification — designed in. No retrofit. | Continuous |
| CCPA | Subset of GDPR controls — same plumbing | Continuous |
| HIPAA-adjacent | Verticals with health-adjacent merchandise (pet pharma, OTC) — controls map to the data classification scheme | As required per merchant |

## Optional features — opt-in via env flag, default off

The platform is designed to operate correctly with all of the following disabled. None are required for the core product to function.

| Feature | Env flag | Default | What's affected when off |
|---|---|---|---|
| L402 enforcement (Lightning settlement on paid tool calls) | `L402_ENABLED` | `false` | Agent calls authenticate via platform JWT only; OTB tracked but not Lightning-settled |
| L402 OTB hard-enforcement (PO blocking) | `feature.l402_enforcement_enabled` | `false` (tracking-only) | OTB drift surfaces as alerts; never blocks PO creation |
| ILDWAC five-dimension cost model | `ILDWAC_ENABLED` | `false` | Standard ILWAC (Item × Location × WAC) operates |
| Satoshi denomination at accounting layer | `BITCOIN_STANDARD_ENABLED` | `false` | Fiat MAC is the canonical accounting unit |
| Blockchain evidence anchoring | `BLOCKCHAIN_ANCHOR_ENABLED` | `false` | Internal SHA-256 chain operates; public anchoring queue dormant |
| Vendor smart contracts | `VENDOR_CONTRACTS_ENABLED` | `false` | Vendor compliance via standard chargeback workflow |

The required core: SHA-256 → receipt → RaaS namespace. Everything else is extension.

## Identity — home-grown, federated to your IdP

Canary's identity service is platform-built. It accepts your IdP via OIDC, SAML, LDAP-via-bridge, or SCIM provisioning. Your users authenticate against Okta / Azure AD / Google Workspace / your custom IdP; the platform validates the federated token, maps your IdP groups to platform roles via a per-merchant configuration, and issues a platform JWT for downstream services to consume.

You do not give Canary your password or your directory. Canary speaks your IdP's protocol and brokers the federation. SCIM provisioning automates user lifecycle.

## Related

- [Why Canary](../why/why) — the rails this engineering posture supports
- [How to engage](../modes/modes) — the engagement modes this posture is designed for
- [Modules](../modules/modules) — the operational module library running on this posture

---
card-type: format-spec
card-id: agent-card-format
card-version: 3
domain: platform
layer: cross-cutting
status: approved
last-compiled: 2026-04-29
---

# Agent Card Format

The agent card format is the standard for knowledge units that agents consume via the memory bus. It replaces relational lookup tables with flat files that embed into pgvector through the existing seed pipeline. No new DB schema is required — the `growdirect_memory` vector store is the only persistence layer.

## Design Principles

**One concept per card.** A card holds exactly one idea — a signal, an agent, a hierarchy axis, a lifecycle gate. If a card needs subsections for multiple concepts, split it.

**Every section embeds independently.** The memory bus seeder chunks by heading. Each section must make sense when retrieved without the rest of the card. Write sections as if they will be read cold.

**Frontmatter is machine data.** All relational facts (what feeds what, which agent owns this, which module consumes it) live in frontmatter arrays. The body is prose that embeds well. Agents can filter on frontmatter fields before running semantic search.

**No volatile data.** Row counts, live metrics, and current-state summaries do not belong in cards. Cards capture structure, relationships, constraints, and context.

---

## Frontmatter Schema

### Required fields

| Field | Type | Values |
|-------|------|--------|
| `card-type` | enum | `signal-feed` · `agent-profile` · `org-layer` · `field-hierarchy` · `role-binding` · `domain-module` · `lifecycle-gate` · `infra-capability` · `platform-thesis` · `runbook` · `format-spec` |
| `card-id` | string | kebab-case unique identifier, stable across versions |
| `card-version` | integer | Increment on any substantive change |
| `domain` | enum | `lp` · `merchandising` · `finance` · `labor` · `platform` · `local-market` · `cross-cutting` |
| `layer` | enum | `domain` · `infra` · `local-market` · `cross-cutting` |
| `status` | enum | `draft` · `approved` |

### Optional fields

| Field | Type | Purpose |
|-------|------|---------| 
| `agent` | string | Agent that owns or primarily uses this card |
| `feeds` | array | card-ids or module codes this concept feeds into |
| `receives` | array | card-ids or module codes that feed into this concept |
| `tags` | array | Search terms for memory bus recall |
| `milestone` | string | M1–M6 PMO milestone (domain modules only) |
| `last-compiled` | date | ISO 8601, set by content-engine lint |
| `needs-review` | boolean | Set by content-engine lint on frontmatter issues |

---

## Body Conventions

### Section headings (use these in order, omit any that don't apply)

```
## What this is
One-sentence definition. This is the identity chunk — retrieved first by semantic search.

## Purpose
Agent-facing "why this exists." What problem does it solve, what decision does it inform.

## Structure
For hierarchies, role models, org layers: the data shape, constraints, enumerations.

## Signal
For signal feeds: what the signal contains, frequency, format, quality characteristics.

## Consumers
Which agents or modules use this. What they do with it. Be specific about the action, not just the name.

## Sources
Where the data comes from. External systems, feeds, human inputs.

## Routing
How it flows through the agent network. Show the chain explicitly.

## When to run
**Runbook cards only.** The trigger condition — what state means this procedure is needed. Be specific: "Docker stack is down and dispatch work is about to begin" not "whenever you need to restart Docker."

## Preconditions
**Runbook cards only.** What must be true before starting. Ordered list. If a precondition is not met, the procedure must not proceed.

## Canonical steps
**Runbook cards only.** Exact commands in order, with expected output noted inline. No paraphrasing — copy-paste fidelity is the standard.

## Verification
**Runbook cards only.** How to confirm the procedure succeeded. A query, a health check, a curl — something observable that produces a pass/fail signal.

## Failure modes
**Runbook cards only.** Known failure patterns with recovery steps. Each mode: symptom → cause → fix. No speculation — only confirmed failures.

## Invariants
Hard constraints. What must always be true. What must never happen. Agents enforce these.

## Related
Links to related cards using [[card-id]] syntax. One line per related card with a brief note.
```

---

## How Cards Enter the Memory Bus

Cards in `Brain/wiki/` (including subdirectories) are picked up by the seed pipeline:

```bash
python3 services/memory-bus/scripts/seed_standalone.py
```

The seeder chunks each card at heading boundaries and embeds each chunk with `qwen3-embedding:8b` (1024-dim). Chunks are stored in `growdirect_memory` with the file path and heading as metadata.

**Agent recall:**
```
memory_recall("social threat detection signal local market")
memory_recall("merchant org hierarchy head office role")
memory_recall("geography hierarchy LP district")
```

**Filtered recall (frontmatter fields):** The seeder stores frontmatter as chunk metadata. Future memory bus versions will support pre-filter by `card-type`, `domain`, or `layer` before vector search.

---

## Versioning

Increment `card-version` on any substantive change. The seed pipeline is incremental by mtime — a version bump forces re-embedding even if the file timestamp doesn't change (when using `--force`). Do not reset `card-version` to 1 on edits; that signals a rewrite, not an update.

---

## Card Directory

All agent cards live in `Brain/wiki/cards/`. Subdirectories are permitted for large domains but the flat directory is preferred until there are more than ~50 cards.

| Card | ID | Type |
|------|----|------|
| [Merchant Org Hierarchy](cards/merchant-org-hierarchy.md) | merchant-org-hierarchy | org-layer |
| [Geography Hierarchy](cards/geography-hierarchy.md) | geography-hierarchy | field-hierarchy |
| [Category Hierarchy](cards/category-hierarchy.md) | category-hierarchy | field-hierarchy |
| [Role Binding Model](cards/role-binding-model.md) | role-binding-model | role-binding |
| [Local Market Agent](cards/local-market-agent.md) | local-market-agent | agent-profile |
| [Signal: Seasonality](cards/signal-seasonality.md) | signal-seasonality | signal-feed |
| [Signal: Weather + Zone SEO](cards/signal-weather-seo.md) | signal-weather-seo | signal-feed |
| [Signal: Social Threat Detection](cards/signal-social-threat.md) | signal-social-threat | signal-feed |
| [Signal: Civil Services](cards/signal-civil-services.md) | signal-civil-services | signal-feed |
| [Signal: Community Intelligence](cards/signal-community-intel.md) | signal-community-intel | signal-feed |
| [Signal: Property & Landlord](cards/signal-property-landlord.md) | signal-property-landlord | signal-feed |
| [Infra: Blockchain Evidence Anchor](cards/infra-blockchain-evidence-anchor.md) | infra-blockchain-evidence-anchor | infra-capability |
| [Infra: L402 OTB Settlement](cards/infra-l402-otb-settlement.md) | infra-l402-otb-settlement | infra-capability |
| [Platform Thesis](cards/platform-thesis.md) | platform-thesis | platform-thesis |
| [Platform: Closed-Loop Attribution](cards/platform-closed-loop-attribution.md) | platform-closed-loop-attribution | platform-thesis |
| [Platform: Retailer Lifecycle Test](cards/platform-retailer-lifecycle-test.md) | platform-retailer-lifecycle-test | infra-capability |
| [Platform: ALX as VSM](cards/platform-alx-vsm.md) | platform-alx-vsm | platform-thesis |
| [Runbook: Memory Bus Seed](cards/runbook-memory-bus-seed.md) | runbook-memory-bus-seed | runbook |
| [Runbook: Docker Startup](cards/runbook-docker-startup.md) | runbook-docker-startup | runbook |
| [Runbook: Brain Wiki Commit](cards/runbook-brain-wiki-commit.md) | runbook-brain-wiki-commit | runbook |
| [Runbook: Create a Runbook](cards/runbook-create-runbook.md) | runbook-create-runbook | runbook |
| [Runbook: Vault Publish](cards/runbook-vault-publish.md) | runbook-vault-publish | runbook |
| [Retail: Vendor Lifecycle](cards/retail-vendor-lifecycle.md) | retail-vendor-lifecycle | domain-module |
| [Retail: Vendor Compliance Standards](cards/retail-vendor-compliance-standards.md) | retail-vendor-compliance-standards | domain-module |
| [Retail: Vendor Scorecard](cards/retail-vendor-scorecard.md) | retail-vendor-scorecard | domain-module |
| [Retail: Chargeback Matrix](cards/retail-chargeback-matrix.md) | retail-chargeback-matrix | domain-module |
| [Retail: Purchase Order Model](cards/retail-purchase-order-model.md) | retail-purchase-order-model | domain-module |
| [Retail: Three-Way Match](cards/retail-three-way-match.md) | retail-three-way-match | domain-module |
| [Retail: Receiving Disposition](cards/retail-receiving-disposition.md) | retail-receiving-disposition | domain-module |
| [Retail: Inventory Valuation / MAC](cards/retail-inventory-valuation-mac.md) | retail-inventory-valuation-mac | domain-module |
| [Retail: Inventory Audit](cards/retail-inventory-audit.md) | retail-inventory-audit | domain-module |
| [Retail: Backroom Cost Transfer](cards/retail-backroom-cost-transfer.md) | retail-backroom-cost-transfer | domain-module |
| [Retail: Merchandise Financial Planning](cards/retail-merchandise-financial-planning.md) | retail-merchandise-financial-planning | domain-module |
| [Retail: Demand Forecasting](cards/retail-demand-forecasting.md) | retail-demand-forecasting | domain-module |
| [Retail: Replenishment Model](cards/retail-replenishment-model.md) | retail-replenishment-model | domain-module |
| [Retail: AP / Vendor Terms](cards/retail-ap-vendor-terms.md) | retail-ap-vendor-terms | domain-module |
| [Retail: Merchandise Hierarchy](cards/retail-merchandise-hierarchy.md) | retail-merchandise-hierarchy | domain-module |
| [Retail: Site Management](cards/retail-site-management.md) | retail-site-management | domain-module |
| [Retail: Event Management](cards/retail-event-management.md) | retail-event-management | domain-module |
| [Retail: Operations KPIs](cards/retail-operations-kpis.md) | retail-operations-kpis | domain-module |
| [Retail: Assortment Management](cards/retail-assortment-management.md) | retail-assortment-management | domain-module |
| [Retail: Sales Audit](cards/retail-sales-audit.md) | retail-sales-audit | domain-module |
| [Retail: Import Management](cards/retail-import-management.md) | retail-import-management | domain-module |
| [Retail: Space, Range & Display](cards/retail-space-range-management.md) | retail-space-range-management | domain-module |
| [Retail: Item Authorization](cards/retail-item-authorization.md) | retail-item-authorization | domain-module |
| [RaaS: Receipt as a Service](cards/raas-receipt-as-a-service.md) | raas-receipt-as-a-service | infra-capability |
| [Platform: Enterprise Document Services](cards/platform-enterprise-document-services.md) | platform-enterprise-document-services | platform-thesis |
| [ICP: Murdoch's Reference Implementation](cards/icp-murdochs-reference.md) | icp-murdochs-reference | platform-thesis |
| [Platform: Proof Case](cards/platform-proof-case.md) | platform-proof-case | platform-thesis |
| [Platform: Wyoming Ecosystem](cards/platform-wyoming-ecosystem.md) | platform-wyoming-ecosystem | platform-thesis |
| [Platform: Field Capture](cards/platform-field-capture.md) | platform-field-capture | platform-thesis |
| [Platform: Performance NFRs](cards/platform-performance-nfrs.md) | platform-performance-nfrs | platform-thesis |
| [Platform: PwC Benchmarks](cards/platform-pwc-benchmarks.md) | platform-pwc-benchmarks | platform-thesis |
| [Store: Network Integrity Monitoring](cards/store-network-integrity.md) | store-network-integrity | platform-thesis |
| [Platform: PII Hashing](cards/platform-pii-hashing.md) | platform-pii-hashing | platform-thesis |
| [Platform: Multi-Tier Assortment](cards/platform-multi-tier-assortment.md) | platform-multi-tier-assortment | platform-thesis |
| [Platform: Cryptographic Erasure](cards/platform-cryptographic-erasure.md) | platform-cryptographic-erasure | platform-thesis |
| [Platform: Data Classification](cards/platform-data-classification.md) | platform-data-classification | platform-thesis |
| [Platform: Stack Commitment](cards/platform-stack-commitment.md) | platform-stack-commitment | platform-thesis |
| [Platform: Architectural Continuity](cards/platform-architectural-continuity.md) | platform-architectural-continuity | platform-thesis |
| [Platform: L402 + ILDWAC Moat](cards/platform-l402-ildwac-moat.md) | platform-l402-ildwac-moat | platform-thesis |

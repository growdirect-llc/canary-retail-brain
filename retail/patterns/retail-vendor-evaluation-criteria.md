---
tags: [retail, vendor-evaluation, procurement, wiki]
project: retail
type: wiki
last-compiled: 2026-04-28
needs-review: 2026-05-12
---

# Retail Platform Vendor Evaluation Criteria

How enterprise retailers evaluate retail management platform vendors. Derived from a documented enterprise RFP process (IBM-facilitated, $4M+ contract) and industry analyst vendor rating methodology.

## Analyst Rating Dimensions

| Dimension | Category | What's Assessed |
|-----------|---------|-----------------|
| Corporate Viability | Strategy | Market position, customer base, partnership ecosystem, international presence |
| Financial Stability | Strategy | Revenue trajectory, profitability, acquisition risk |
| Marketing | Strategy | Product roadmap credibility, release velocity, messaging clarity |
| Organization | Strategy | Management team continuity, regional coverage |
| Product / Service | Market Offerings | Module maturity, installed base per module, live customer count |
| Technology / Methodology | Market Offerings | Architecture quality, scalability evidence, integration approach |
| Pricing Structure | Market Offerings | License model, subscription options, total cost predictability |
| Support / Account Management | Customer Service | Support SLAs, implementation quality track record |

## RFP Selection Criteria (Enterprise Buyer Model)

Typical weighting in a formal software selection process:

| Criterion | Description | Weight Range |
|-----------|-------------|-------------|
| Software Functionality | Functional coverage against requirements matrix | 30–40% |
| Software Technology | Architecture, scalability, integration, platform independence | 15–25% |
| Total Costs | License, implementation, ongoing maintenance | 15–25% |
| Vendor Support | Implementation methodology, PS team quality, on-time/on-budget track record | 10–20% |
| Vendor Vision / Viability | Financial health, roadmap, acquisition risk | 5–15% |
| Industry Experience | Customer references in same segment, module deployment at comparable scale | 5–10% |

## Functional Assessment Process

1. Issue functional requirements spreadsheet (typically 1,000+ line items covering all modules in scope)
2. Vendor self-assessment: each requirement rated as standard / configurable / custom development / not available
3. Scoring weighted by requirement priority (mandatory / high / medium / low)
4. Short-list to 2 vendors for scripted demonstration
5. Demonstration scripts exercise highest-priority scenarios live in vendor's environment
6. Site visits to reference customers in same retail segment

## Technical Assessment Checklist

| Area | Key Questions |
|------|--------------|
| Scalability | What benchmarks exist? Largest installation by store count / SKU count / transaction volume? |
| Integration | What is the integration bus architecture? How are external system connections supported? What is the Foundation Data approach? |
| Database platform | Single-database vendor dependency? Oracle only, or others? |
| OS platform | Unix-only, or multi-platform? |
| Architecture | Separate DB/App tier? Can components be independently scaled? |
| Upgrade path | What is the upgrade process? What customizations break? |
| Disaster recovery | What is the RTO/RPO? Is standby environment supported? |
| Batch architecture | What is the restart/recovery mechanism? Multi-threading approach? |

## Customer Reference Evaluation

When evaluating customer references, verify:

| Check | Why |
|-------|-----|
| Which modules are live vs. merely licensed | Licensed ≠ implemented; many modules are licensed but only partially deployed |
| Implementation duration: actual vs. planned | Actuals reveal delivery quality; vendor timelines are optimistic |
| Scope reductions during implementation | Cuts indicate the original scope was not achievable on time/budget |
| Version currently running | Old versions = missed upgrade cycles; indicates implementation complexity or instability |
| Third-party SI involvement | Large implementations typically require an SI separate from the software vendor |
| Custom extension count | High count = standard product didn't fit; increases upgrade cost and risk |

## Total Cost of Ownership Model

| Cost Category | Typical Range | Notes |
|---------------|--------------|-------|
| Software license | $2M – $8M | Scales with store count and module count; per-store subscription models emerging |
| Implementation services | 1.5–3× license fee | Higher for complex integrations; lower for clean greenfield |
| Training | 10–15% of license | Commonly underestimated |
| Annual maintenance | 18–22% of license per year | Includes version upgrades |
| Infrastructure | $500K – $2M | Servers, storage, network — Unix + Oracle stack |
| Internal IT team | Ongoing cost | DBA, functional admin, integration support |

At the $4M license level (14 modules, 300 stores), total 5-year TCO typically runs $15–25M including implementation and maintenance.

## Red Flags in Vendor Proposals

| Red Flag | Interpretation |
|----------|---------------|
| References all using only 1–2 modules | Core product only; newer modules lack live evidence |
| "Available in next release" for mandatory requirements | Future roadmap risk; not production-proven |
| Services revenue growing faster than license revenue | Difficult implementations requiring more services work; potential product-fit problem |
| Consulting partner required to close all deals | Vendor depends on SI; implementation quality risk |
| Rapid succession of CEO/management changes | Strategy instability; roadmap credibility risk |
| Proposal scope reduction under time pressure | Vendor cannot deliver full scope; surfaces during implementation |
| Competitor references used as proof points | Own customer base insufficient to support claims |

## Selection Process Schedule Reference

| Activity | Typical Duration |
|----------|----------------|
| RFP issued to pre-selected vendors | Day 0 |
| Proposals due | 3 weeks |
| Short-list selection | Week 4–5 |
| Demonstration scripts to short-listed vendors | Week 5 |
| Scripted demonstrations (2 vendors) | Weeks 6–8 |
| Customer site visits | Week 9–10 |
| Preferred vendor notification | Week 12–16 |

## Related Cards

- [[retail-module-decomposition]] — what to evaluate in the functional requirements spreadsheet
- [[retail-implementation-methodology]] — what to assess in vendor support evaluation
- [[retail-transaction-volume-benchmarks]] — reference benchmarks for scalability assessment

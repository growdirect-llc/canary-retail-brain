---
card-type: domain-module
card-id: retail-operations-kpis
card-version: 2
domain: cross-cutting
layer: cross-cutting
status: approved
agent: ALX
receives: [retail-vendor-scorecard, retail-merchandise-financial-planning, retail-inventory-audit, retail-three-way-match, retail-replenishment-model, retail-event-management, retail-ap-vendor-terms]
tags: [KPIs, operations, performance-indicators, scorecard, benchmarks, retail-metrics, operations-agent]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

The retail operations KPI framework: the performance indicators used to measure the health of merchandising, inventory, vendor, and financial operations — and the benchmarks against which performance is evaluated. This is the input specification for the Operations Agent's monitoring and alerting mandate.

## Purpose

KPIs provide the signal that separates normal operations from situations requiring intervention. Without a defined KPI framework, every anomaly requires investigation to determine whether it matters. With one, the Operations Agent can automatically classify performance against established thresholds and surface only the exceptions that require human attention. The framework also provides the accountability structure: a buyer who knows that turnover and gross margin are their KPIs behaves differently than one operating without measurement.

## Structure

**Merchandising and inventory KPIs:**

| KPI | Definition | Benchmark target |
|-----|-----------|-----------------|
| Inventory turnover | Net sales ÷ average inventory at retail | Varies by category; fast-moving consumables: 12–26x annual |
| Weeks of supply | On-hand units ÷ average weekly sales rate | 4–8 weeks for most categories |
| In-stock rate | % of store-visits where item is available on shelf | 95%+ target |
| Comp-store sales % | Sales growth vs. prior year, same-store base | Positive; budget-dependent |
| Gross margin % | Gross profit ÷ net sales | Category-dependent; 30–50% typical in specialty retail |
| Initial markup % | (Retail − cost) ÷ retail | 45–55% for specialty retail before allowances |
| Markdown rate | Markdown $ ÷ gross sales | < 10% for well-managed assortments |
| Sell-through rate | Units sold ÷ units received during a period | 85%+ for seasonal items at season end |
| Forecast accuracy (MAPE) | Mean Absolute Percentage Error of demand forecast | < 20% MAPE for stable SKUs |

**Vendor performance KPIs:**

| KPI | Definition | Benchmark target |
|-----|-----------|-----------------|
| Fill rate | Units shipped ÷ units ordered | 95%+ |
| On-time delivery | % deliveries within agreed window | 95%+ |
| ASN accuracy | % of ASNs matching physical receipt | 98%+ |
| EDI compliance | % of EDI transactions correct and on-time | 98%+ |
| Invoice accuracy | % of invoices matching PO without adjustment | 95%+ |
| Chargeback resolution time | Days from chargeback issue to vendor credit | < 30 days |
| Vendor scorecard composite | Weighted average across all compliance dimensions | ≥ 85 (on 100-point scale) |

**Receiving and inventory accuracy KPIs:**

| KPI | Definition | Benchmark target |
|-----|-----------|-----------------|
| Shrink rate | Shrink $ ÷ sales $ | < 1.5% for specialty retail |
| Perpetual inventory accuracy | % of items where book on-hand matches physical count within tolerance | 95%+ |
| Three-way match rate | % of invoices matched without exception on first pass | 90%+ |
| Empty shelf rate | % of items with phantom inventory (positive book, empty shelf) | < 2% |
| Receiving discrepancy rate | % of receipts with a quantity or quality exception | < 5% |

**Financial operations KPIs:**

| KPI | Definition | Benchmark target |
|-----|-----------|-----------------|
| Discount capture rate | % of available early-payment discounts captured | 95%+ |
| Invoice processing cycle time | Days from invoice receipt to approval | 3–5 days |
| Invoice exception rate | % of invoices requiring manual resolution | < 5% |
| Chargeback $ as % of purchases | Total chargeback deductions ÷ total purchase value | < 2% (high suggests vendor quality issues; very low suggests under-enforcement) |
| Co-op utilization rate | Co-op funds claimed ÷ co-op funds accrued | 95%+ |

## Consumers

The Operations Agent is the primary consumer of this framework — it monitors all KPIs at defined intervals, computes trend lines, and triggers alerts when metrics breach thresholds or show sustained negative trajectory. Buyers use KPIs in planning sessions and vendor negotiations. Finance uses KPIs in period-end reporting. The Platform Ops function uses cross-merchant KPI benchmarks to surface insights about how a given merchant compares to peer retailers.

## Invariants

- KPI thresholds must be defined before the measurement period begins. Retroactive threshold adjustment to make performance look better is analytically worthless and commercially misleading.
- Leading indicators (in-stock rate, forecast accuracy, ASN compliance) predict lagging indicators (gross margin, shrink, turnover). The Operations Agent monitors both. Monitoring only lagging indicators produces slow reaction times.
- Benchmarks are reference points, not universal targets. A margin-optimized specialty retailer and a volume-driven mass merchant have different targets for the same KPIs. Benchmark calibration by merchant profile is required.

## Platform (2030)

**Agent mandate:** Operations Agent IS the KPI monitoring system. This card is the Operations Agent's monitoring specification. Every KPI in this framework is monitored continuously — not at period end, not in a weekly dashboard meeting. Operations Agent computes leading indicators first (in-stock rate, forecast accuracy, ASN compliance) because they predict lagging indicators (gross margin, shrink, turnover) with sufficient lead time to intervene. The Operations Agent's primary output is exception alerts; normal performance generates no noise.

**From batch reporting to continuous exception surfacing.** Traditional retail KPI monitoring is a reporting function: an analyst pulls a dashboard weekly, operations leadership reviews it in a meeting, decisions are made two weeks after the data was generated. In Canary Go, every KPI in this framework has a defined threshold and a monitoring rule in Operations Agent. When a KPI breaches threshold — or when its trajectory suggests breach within N periods — an alert surfaces to the merchant dashboard immediately. The merchant sees only the exceptions that require human attention. Operations Agent handles the monitoring; merchants handle the decisions.

**L402-gated analytics depth.** Operations Agent provides two tiers of KPI access. At baseline, all merchants see threshold alerts and current-period KPI values. At Operations Standard tier, merchants access trend analytics, multi-period comparison, and the inter-KPI correlation surface — how declining forecast accuracy is tracking against in-stock rate degradation, or how fill rate decline is leading chargeback rate growth. At Premium tier, cross-merchant benchmarking compares a given merchant's KPIs against anonymized peer performance, converting a 92% in-stock rate from an ambiguous number into "you're 3 points below comparable merchants in your category."

**MCP surface.** `kpi_dashboard(merchant_id)` returns current values for all KPIs against their thresholds in a single call. `kpi_trend(kpi_name, period)` returns the time series with threshold bands. `kpi_alerts(merchant_id)` returns active threshold breaches sorted by severity. `benchmark(kpi_name, merchant_profile)` returns anonymized peer benchmarks for context. All calls return structured data optimized for agent consumption — numbers and classification, not narrative.

**RaaS.** All KPIs derive from receipt events; KPI integrity is a direct function of receipt event completeness and sequencing. A missing or out-of-order receipt event produces a wrong KPI, and wrong KPIs produce wrong decisions. KPI computation must operate on the audited, sequenced receipt record — not raw POS data; monitoring on unaudited data produces values that diverge from financial actuals once sales audit closes. `kpi_dashboard(merchant_id)` pre-aggregated and Valkey-cached (sub-200ms full dashboard load). `kpi_trend(kpi_name, period)` from SQL indexed on (merchant_id, kpi_name, period_date) — rolling N-period queries must not full-scan. KPI aggregates are pre-computed views over the receipt event log, not real-time joins. KPI history exportable for investor reporting and period-end financial review.

## Related

- [[retail-vendor-scorecard]] — vendor KPIs feed from scorecard dimensions
- [[retail-merchandise-financial-planning]] — financial KPIs anchor to plan commitments
- [[retail-inventory-audit]] — shrink rate and inventory accuracy KPIs sourced from audit results
- [[retail-three-way-match]] — match rate and invoice exception KPIs sourced from AP matching data

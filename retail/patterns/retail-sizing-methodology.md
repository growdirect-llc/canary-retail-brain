---
tags: [retail, sizing, infrastructure, wiki]
project: retail
type: wiki
last-compiled: 2026-04-28
needs-review: 2026-05-12
---

# Retail System Sizing Methodology

Sizing a retail management platform requires translating business-volume inputs into hardware and batch-window requirements. This card documents the canonical input variables, sizing process, and reference points derived from enterprise implementations.

## Input Variables

### Organizational Dimensions

| Variable | Description | Example Range |
|----------|-------------|---------------|
| Store count | Total number of locations (corporate + franchise + DC) | 50 – 40,000 |
| DC count | Distribution centers | 1 – 20 |
| Corporate users | Head office users | 100 – 2,000 |
| Concurrent users | Simultaneous active sessions | 50–60% of corporate user count |
| Store connections | Stores with direct system connectivity | 0 – full store count |

### Item / SKU Dimensions

| Variable | Example Range |
|----------|---------------|
| Active item / SKU count | 5,000 – 500,000 |
| Item × location combinations | SKU count × store count (e.g., 110K items × 300 stores = 33M) |
| New items per period | Weekly cadence; varies by format |
| Average UOM per item | Units, weight, volume variants |

### Transaction Dimensions

| Variable | Example Range |
|----------|---------------|
| Daily sales transactions | 10,000 – 30M+ line items |
| Monthly purchase orders | 10,000 – 500,000 |
| PO lines per order | 8 – 100+ |
| Replenishment SKU/location combinations | Equals or exceeds item × location count |
| Vendor count | 100 – 10,000 |

### Processing Window

The batch window is the binding constraint in most implementations.

| Question | Significance |
|----------|-------------|
| What time does POS close? | Sales transactions available after this |
| What time must replenishment orders be committed? | Sets the batch deadline |
| Available overnight window | Typically 4–8 hours |
| Trickle-mode requirement? | Near-real-time sales posting during day compresses overnight batch |

## Sizing Process

1. **Collect inputs** — org dimensions, item count, transaction volumes, batch window
2. **Calculate SKU/location product** — this is the primary scale driver for replenishment and forecasting
3. **Identify binding constraint** — sales audit, replenishment, or forecasting (whichever is largest relative to window)
4. **Apply benchmark ratios** — map client volumes to reference benchmarks (see [[retail-transaction-volume-benchmarks]])
5. **Size processor count** — throughput scales with CPU count; use benchmark machine configs as reference
6. **Add 20–50% headroom** — growth buffer standard in enterprise retail engagements
7. **Validate with volume test** — benchmark against expected load before go-live

## Volume-to-Hardware Reference Points

| Workload | Volume | Window | Machine Config |
|----------|--------|--------|---------------|
| Sales audit + stock ledger | 16M transactions / 200 stores | 3 hours | 24-CPU RISC, 450 MHz class |
| Sales audit + stock ledger | 30M line items / 40,000 stores | 8 hours | 24-CPU RISC, 600 MHz class |
| Replenishment | 13.8M SKU/locations | ~1.8 hours | 24-CPU RISC, 450 MHz class |
| Demand forecasting | 60M time series | 56 minutes | 24-CPU RISC, 450 MHz class |
| Demand forecasting | 119M time series | 30 minutes | 12-CPU RISC, 600 MHz class |
| User load (OLTP) | 250 concurrent users | Continuous | 8-CPU DB + app servers |
| User load (OLTP) | 1,492 concurrent users | Continuous | 32-CPU DB + 5× app servers |

*Hardware configs are early-2000s RISC baselines. Normalize to current equivalent processor throughput.*

## Real-World Input Example (Mid-Market Drug Chain)

Katz Group Canada — 310 corporate stores, 1,264 independent stores, 70 franchise stores:

| Input Variable | Value |
|----------------|-------|
| Consolidated annual sales | CD$4.2B |
| Active items (CPG) | 110,000 |
| Active items (Rx) | 9,000 |
| Vendors (CPG) | 3,000 |
| Vendors (Rx) | 150 |
| Monthly purchase orders | 270,000 |
| Avg replenishment lines/store | 8 |
| Head office users | 400 |
| Concurrent sessions | 200 |

Growth projection: 20–50% increase anticipated over planning horizon.

## Key Sizing Pitfalls

| Pitfall | Problem |
|---------|---------|
| Undercounting item × location | The replenishment driver is the cross-product, not just item count or store count |
| Ignoring trickle processing | Near-real-time POS posting reduces the overnight window; model both modes |
| Single environment sizing | Volume test environment must be production-matched hardware |
| Missing growth buffer | Retail businesses grow 20–50% in 2–3 years; size for the 3-year state |
| Conflating batch and OLTP load | Mixed workload (batch running while users are active) requires separate capacity modeling |

## Related Cards

- [[retail-transaction-volume-benchmarks]] — detailed benchmark data
- [[retail-architecture-patterns]] — server topology
- [[retail-restart-recovery-patterns]] — batch processing patterns that affect sizing

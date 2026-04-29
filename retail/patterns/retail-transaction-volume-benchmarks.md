---
tags: [retail, benchmarks, performance, scaling, wiki]
project: retail
type: wiki
last-compiled: 2026-04-28
needs-review: 2026-05-12
---

# Retail Transaction Volume Benchmarks

Reference benchmarks from enterprise retail system scale testing. All figures are from documented production or pre-production scale tests. Hardware specs are early-2000s RISC/Unix baselines; normalize to current processor throughput when applying.

## Sales Processing Benchmarks

| Retailer Profile | Volume | Stores | Target Window | Actual Time | Machine |
|-----------------|--------|--------|---------------|-------------|---------|
| Large hypermarket | 16M transactions | 200 | 4 hours | 148 min | HP v2500, 32×440MHz CPU |
| Large drug chain | 16M transactions | 200 | 3 hours | 79 min | IBM RS6000 S80, 24×450MHz CPU |
| Specialty electronics (trickle) | 80,000 transactions | 450 | 40 min | 20 min | HP N4000, 8×550MHz CPU |
| Specialty electronics (trickle) | 20,000 transactions | 450 | 10 min | 7 min | HP N4000, 8×550MHz CPU |
| Postal / high-store-count | 30M line items (10M txns) | 40,000 | 8 hours | 444 min | IBM p680, 24×600MHz CPU |

**Key ratio**: 16M transactions across 200 stores = 80K transactions/store. The postal benchmark demonstrates that store count is not the binding constraint — transaction line volume is.

## Replenishment Processing Benchmarks

| Retailer Profile | Volume (SKU/locations) | Target Window | Actual Time | Machine |
|-----------------|------------------------|---------------|-------------|---------|
| Large hypermarket | 13.776M | 4 hours | 111 min | HP v2500, 32×440MHz CPU |
| Large drug chain | 13.766M | 3 hours | 60 min | IBM RS6000 S80, 24×450MHz CPU |

Replenishment scales the SKU-count × location-count cross product. 13.8M combinations is ~115K SKUs × 120 stores, or ~28K SKUs × 500 stores.

## Demand Forecasting Benchmarks

| Application | SKUs | Stores | Time Series (total) | Time | Machine |
|-------------|------|--------|----------------------|------|---------|
| Demand forecasting — drug | 12,000 | 5,000 | 60M | 56 min | IBM S80, 24×450MHz CPU |
| Promotion planning — hardlines | 4,330 | 1,022 | 4.4M | 51 min | IBM RS6000, 4×333MHz CPU |
| Demand forecasting — general | 109,000 | 1,100 | 119M | 30 min | IBM p680, 12×600MHz CPU |

The 109K-SKU / 1,100-store benchmark demonstrates that a full mid-market assortment can be forecast in a single batch run. At 119M time series in 30 minutes, throughput is ~4M series/min.

## Mixed Workload (Batch + Online Concurrent)

| Retailer | Concurrent Users | Concurrent Batch | Avg Response |
|----------|-----------------|-----------------|--------------|
| Large hypermarket | 1,260 | 13.8M SKU/loc replenishment | N/A |
| Specialty electronics | 2,000 | 11,260 sales records/run | < 0.7 sec |
| Specialty electronics | 4,000 | 22,320 sales records/run | < 0.7 sec |
| Specialty electronics | 6,000 | 33,480 sales records/run | < 0.6 sec |

Mixed workload at 2,000–6,000 concurrent users with active sales processing running in parallel held sub-second response times. Total server utilization during peak user tests: under 35%.

## User Load Benchmarks

| Retailer | Concurrent Users | Response Time | DB Server | App Servers |
|----------|-----------------|---------------|-----------|-------------|
| Large hypermarket | 1,492 active | N/A measured | HP v2500, 32×440MHz | 1× HP V2500 + 2× HP V2250 + 5× N4000 |
| Specialty electronics | 230 | < 3 sec | Sun 4500, 8×400MHz | Included on DB |
| Postal service | 250 | < 3 sec | IBM p680, 24×600MHz | 2× Sun 420 |

**Rule of thumb**: Sub-3-second interactive response time is the enterprise retail OLTP baseline. Design targets should be ≤ 3 sec at peak concurrent load.

## Retailer Scale Reference

| Retailer Type | Store Count | SKU Count | Concurrent Users | Distinguishing Factor |
|---------------|-------------|-----------|-----------------|----------------------|
| Large grocery / hypermarket | 200–500 | 50K–200K | 500–1,500 | Highest transaction volumes; VAT processing |
| Drug / pharmacy chain | 200–2,600 | 9K–120K | 200–1,200 | Mixed Rx/CPG; regulatory complexity |
| Specialty electronics | 450 | 50K–100K | 200–800 | Trickle sales processing every 10 min |
| Postal / government | 40,000 | 250 | 200–500 | Ultra-high store count, low SKU |
| Discount / dollar | 4,600 | 20K–50K | 300–600 | High transaction density per store |

## Scaling Principles Derived from Benchmarks

1. **CPU count is the primary lever** — throughput scales near-linearly with processor count to at least 32 CPUs
2. **Separate DB from App server** — co-located configurations reduce both DB and App throughput
3. **Array processing** — bulk SQL (not scalar) is required to hit these volumes; row-by-row processing would miss the window by 10–100×
4. **Multi-threading** — partition by store or department; threads are independent and restart independently on failure
5. **Volume test early** — client-site volume tests must run before go-live; vendor lab benchmarks are approximations

## Related Cards

- [[retail-sizing-methodology]] — how to use these benchmarks for sizing
- [[retail-architecture-patterns]] — hardware topology
- [[retail-restart-recovery-patterns]] — batch architecture that enables these throughput levels

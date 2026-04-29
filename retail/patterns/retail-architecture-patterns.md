---
tags: [retail, architecture, infrastructure, wiki]
project: retail
type: wiki
last-compiled: 2026-04-28
needs-review: 2026-05-12
---

# Retail Platform Architecture Patterns

Enterprise retail management systems follow a consistent tiered deployment pattern. This card documents that topology, service boundary conventions, and environment separation practices derived from production implementations at large retailers (40K+ stores to 200-store chains).

## Canonical Tier Model

| Tier | Components | Notes |
|------|-----------|-------|
| Database | Core OLTP DB, Data Warehouse DB | Separated onto distinct physical servers |
| Application | Merchandise, Distribution, Planning app servers | Each functional area gets dedicated app tier |
| Integration | Message bus (JMS/EAI), ETL engine | Runs on dedicated server; never co-located with DB |
| BI/Reporting | Data warehouse application, web tier | Windows servers common for BI tools; Unix for everything else |
| Client | Browser, store terminals, remote access | Connected via TCP/IP; no thick clients in later generations |

## Standard Environment Set

| Environment | Purpose | Hardware Ratio |
|-------------|---------|----------------|
| Production | Live operations | Full capacity |
| Volume Test / QA | Pre-release benchmark + integration test | Production-matched hardware strongly preferred |
| Development | Feature development, debugging | Consolidated single server; all roles co-located |

Separating Volume Test from QA matters: QA validates correctness; volume test validates throughput under expected load. Merging them introduces noise.

## Server Role Separation (Production Pattern)

| Server Role | Services Hosted | OS |
|-------------|----------------|-----|
| Core OLTP DB | Merchandise DB, OLTP App Server, Integration Bus App Server | Unix (AIX or HP-UX) |
| Data Warehouse DB | DW database, Demand Forecasting app server, Store Operations app server | Unix |
| Planning App | Financial planning, assortment planning, key planning app servers | Unix |
| BI App | DW application layer, analytics web tier | Windows |
| BI Web | DW web-facing reporting | Windows |

## Disk and Storage Pattern

- FC (Fibre Channel) for primary database storage — not SCSI-2 except in lower-tier environments
- RAID on primary disk arrays
- Tape backup connected to production environment
- Storage arrays benchmarked at 500 GB–1.1 TB raw for large retailers

## Scalability Mechanism

Retail systems scale horizontally by adding Unix server capacity (processors) and vertically within Oracle via array processing and multi-threading. The primary lever is processor count on the database server — benchmarks show near-linear throughput improvement up to 32 CPUs.

## Network

- Ethernet TCP/IP backbone between servers
- Firewall between internal cluster and internet-facing clients
- Remote access for corporate and store users through standard WAN/VPN
- Store clients poll or push sales data to central; no real-time transactional coupling required for store-to-HQ

## Key Design Invariants

1. Never co-locate the integration bus with the OLTP database — the JMS broker competes for memory and I/O
2. Data warehouse runs a separate Oracle instance — DW ETL jobs running against the same schema as OLTP creates lock contention
3. Planning and optimization apps (forecasting, assortment) are CPU-bound; benefit most from dedicated app server resources
4. Dev environment collapse is acceptable; QA/Vol-Test collapse is not

## Related Cards

- [[retail-sizing-methodology]] — hardware sizing inputs and reference configs
- [[retail-transaction-volume-benchmarks]] — benchmark data by retailer type
- [[retail-integration-patterns]] — integration bus architecture

---
title: The 13-Module Spine
classification: confidential
nav_order: 1

---

# The 13-module spine

Canary is built around 13 functional modules. Together they cover the full retail business cycle from merchandise planning through store operations and financial settlement.

The spine is a closed graph — every operational event traces to a specific module, and every module's outputs feed defined downstream modules. The closed-graph property is what makes the accountability rails work: every dollar of inventory, every minute of labor, every dollar of OTB has a node where it lives, a meter that measures it, and a contract that governs it.

## Core modules — Differentiated Five (V1, shipping)

The five modules that distinguish Canary from a baseline retail platform.

| Module | Code | Purpose | Status |
|---|---|---|---|
| [Transaction Pipeline](T-transaction-pipeline) | T | POS-agnostic ingestion; seal → parse → merkle → detect | Shipping |
| [Customer](R-customer) | R | Customer identity, loyalty, return-fraud risk score | Shipping |
| [Device](N-device) | N | Device manifest, network monitoring, skimmer detection | Shipping |
| [Asset Management](A-asset-management) | A | Fixture and non-saleable item registry; cross-module exclusion filter | Shipping |
| [Loss Prevention](Q-loss-prevention) | Q | Detection rule engine + case management + analyst surface | Shipping |

## Operational core (V2, design complete)

The merchandising operations layer.

| Module | Code | Purpose |
|---|---|---|
| [Commercial](C-commercial) | C | Vendor portfolio, contracts, OTB, range strategy |
| [Distribution](D-distribution) | D | DC and inter-store transfers, vendor receiving, RTV |
| [Finance](F-finance) | F | Three-way match, MAC, AP, period close, GL reconciliation |
| [Forecast & Order](J-forecast-order) | J | Demand forecasting, suggested order quantity, vendor collaboration |

## Full spine (V3, design complete)

The full operational footprint.

| Module | Code | Purpose |
|---|---|---|
| [Space, Range & Display](S-space-range-display) | S | Planograms, fixtures, shelf-edge labels, reset scheduling |
| [Pricing & Promotion](P-pricing-promotion) | P | Price history, promotional events, markdown management |
| [Labor & Workforce](L-labor-workforce) | L | Scheduling, time tracking, productivity (currently on hold) |
| [Work Execution](W-work-execution) | W | Task dispatch, completion attestation (currently on hold) |

## Reading order

If you want to understand the platform from a single module, [Loss Prevention (Q)](Q-loss-prevention) is the most self-contained — it shows the detection engine, case workflow, and evidence chain in one place.

If you want to understand the operational backbone, read [Transaction Pipeline (T)](T-transaction-pipeline) → [Distribution (D)](D-distribution) → [Finance (F)](F-finance). That trio is the receipt-to-payment cycle.

If you want to understand the differentiation, read [Asset Management (A)](A-asset-management) — it shows how the cross-module asset filter works, which is the kind of structural integration that's foundational to the platform.

## What's in each module page

Each module page below describes:

- **Purpose** — what the module does and why
- **Multi-tenant context** — schema-per-tenant pattern; per-tenant tables and cross-tenant analytics surfaces
- **Optional Features posture** — how the module behaves with each Optional Feature flag enabled or disabled
- **Data model** — full DDL with indexes, constraints, and access patterns
- **API contract** — REST endpoints and MCP tools
- **SLA commitments** — P50, P99, hard limits per operation
- **Failure modes** — detection, recovery, blast radius
- **Compliance** — PII classification, retention, patent scope where applicable

These are engineering specifications. They are the source of truth for the implementation. Module pages are precise — they assume retail-domain fluency and reward careful reading.

For a non-engineering view, read [Experience](../experience/experience).

---
card-type: domain-module
card-id: canary-ildwac
card-version: 1
domain: finance
layer: domain
feeds:
  - canary-blockchain-anchor
receives:
  - canary-identity
  - canary-receiving
  - canary-inventory
tags: [ildwac, cost-model, provenance, weighted-average-cost, patent-protected, five-dimension, wac]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: ildwac

## What this is

Item × Location × Device × MCP × Port × Weighted-Average-Cost. **Patent-protected (#63/991,596).** Computes a five-dimension cost model where every cost lineage is traceable to its provenance (which device/port/MCP touched the goods at each step). The reference state is slow-moving; recomputes on receiving events are change-feed.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9082` |
| Axis | B — Resource APIs |
| Tier mix | Reference (cost-model state, lineage, devices, snapshots) · Change-feed (recomputes on receiving) · Bulk window (period snapshots for accounting close) |
| Owned tables | `app.ildwac_cost_state`, `app.ildwac_lineage`, `app.ildwac_recompute_jobs`, `app.ildwac_snapshots` |
| Tier mapping rule | **Stream-tier ILDWAC operations would burn the model — never expose ILDWAC as real-time. Do not change this tier mapping.** |

## Purpose

Cost lineage tracked across five dimensions. Aggregations roll up: WAC[item, location] → WAC[item] → merchant. Recompute triggers: new receipt event from canary-receiving with `evidence_record_id`; manual ops trigger; period close from canary-report.

## Patent-protected behavior

Provenance weighting (the way device/MCP/port lineage influences cost weighting) is patent-protected. External-facing partner docs document the API; internal SDDs document the algorithm.

## Dependencies

- canary-identity, canary-receiving (receipt events with evidence_record_id)
- canary-inventory (position context)
- canary-blockchain-anchor (snapshot hash anchoring)

## Consumers

- canary-l402-otb (cost basis for OTB reconciliation)
- canary-commercial (chargeback cost attribution)
- canary-report (period-close attestation)
- BI/finance tools

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-ildwac
- Card: [[ilwac-extended-bitcoin-standard]] (founder intent + Bitcoin-standard concept)
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-bulk-window]]

---
card-type: platform-thesis
card-id: platform-closed-loop-attribution
card-version: 1
domain: platform
layer: cross-cutting
feeds:
  - platform-thesis
  - retail-inventory-audit
  - retail-chargeback-matrix
  - retail-backroom-cost-transfer
receives:
  - merchant-org-hierarchy
  - retail-vendor-lifecycle
  - retail-receiving-disposition
tags: [closed-loop, accountability, cycle-count, garbage-collection, loss-attribution, shrink, proportional-charging, stack-wide, layers]
status: approved
last-compiled: 2026-04-29
---

# Platform: Closed-Loop Attribution

## What this is

A governance model in which every loss — physical, data, network, or commercial — is attributed to the node that caused it, charged proportionately, and never pooled into an unowned overhead category. The cycle count is the garbage collection pass; the delta is the bill.

## Purpose

Closes the accountability gap that retail has historically accepted as unavoidable. In an open-loop system, variance pools into "shrinkage" and the offending node escapes. In a closed-loop system, the graph knows what should be there, the sweep surfaces what is not, and attribution reaches the source — not the nearest downstream absorber.

Agents use this model when: building accountability reports, routing escalations to the correct module owner, attributing infrastructure cost overruns, or evaluating whether a variance has been fully closed or merely relocated.

## Structure

The closed-loop model runs five attribution layers simultaneously. Every layer has garbage. Every layer runs a GC sweep. Every sweep produces a delta. Every delta belongs to a node.

| Layer | What accumulates | The sweep | Offender class |
|-------|-----------------|-----------|---------------|
| Commercial / GTM | Dead stock, backroom inventory, conversion miss, demand window miss | Sell-through vs plan, velocity by seller, markdown rate by buyer | Buyer, planner, forecast, hiring decision |
| Physical inventory | Inventory variance — theft, damage, vendor shortage, miscount | Cycle count vs perpetual ledger | Vendor, ops, floor execution, equipment |
| System data | Orphaned records, stale cache, UOM drift, catalog mismatch | Referential integrity check, schema audit | Integration, migration, developer, vendor API |
| Network / protocol | Bad packets, dead letters, retry storms, failed handshakes | DLQ audit, packet loss review | Source service, integration partner, infra config |
| Compute / code | Slow queries, memory leaks, oversized model calls, redundant roundtrips | Cost-per-action audit, performance profiler | Author, release, architectural decision |

## Invariants

- **Unknown is not a valid attribution class.** If attribution cannot be completed, the incompletion is itself a signal and must be surfaced, not swallowed.
- **Relocating cost is not resolving it.** Moving inventory to the back room, moving data to an archive, or moving a failure to a dead letter queue does not close the accountability loop. The cost follows the source node, not the physical location.
- **Carrying cost is a margin cost, not an ops cost.** Every day an unresolved inventory position ages, it accrues cost that belongs to the upstream decision-maker who created the position — not to the store or service that inherited it.
- **Proportional charging, not flat allocation.** A node responsible for 8% of volume but 40% of variance owns 40% of the delta pool. Flat allocation is the mechanism of open loops.

## Consumers

- **Controller agent** — uses this model to route escalations, attribute cross-module variances, and score module performance against plan
- **Module Q (Loss Prevention)** — operationalizes physical and transaction layer attribution via Chirp rules and Fox cases
- **Module M (Merchandising)** — accountable for commercial layer failures; buyer and planner performance is measured against this model
- **Module D (Distribution)** — vendor shortage and receiving discrepancy attribution path
- **Infrastructure agents (CPA)** — compute and network layer attribution; cost-per-action audit against this model

## Related

- [[Brain/wiki/canary-closed-loop-cost-attribution|Closed Loop — Full Wiki Article]] — complete five-layer model with full offender taxonomy and proportional charging detail
- [[Brain/wiki/cards/platform-thesis|Platform Thesis]] — Rail 1 (No Unknown Loss) is the macro statement; this card is the operational mechanism
- [[Brain/wiki/cards/retail-backroom-cost-transfer|Retail: Backroom Cost Transfer]] — the specific pattern of pushing inventory cost downstream; governed by this model
- [[Brain/wiki/cards/retail-inventory-audit|Retail: Inventory Audit]] — physical layer sweep mechanics
- [[Brain/wiki/cards/retail-chargeback-matrix|Retail: Chargeback Matrix]] — vendor attribution and chargeback execution at the physical layer
- [[Brain/wiki/cards/retail-vendor-scorecard|Retail: Vendor Scorecard]] — vendor-level proportional charging surface

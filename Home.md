---
classification: confidential
owner: GrowDirect LLC
---

# Canary Retail

GrowDirect LLC's retail operating system for small and mid-sized
specialty retailers with online footprint.

## Platform

- [[platform/overview]] — positioning, audience, what's different
- [[platform/spine-13-prefix]] — the module spine (C/D/F/J/S/P/T/R/N/L/Q/W/A)
- [[platform/crdm]] — canonical retail data model (People × Places
  × Things × Events × Workflows)
- [[platform/arts-adoption]] — POSLog, Customer, Device, Site
  standards alignment
- [[platform/differentiated-five-add-on]] — T+R+N+A+Q (the add-on
  layer that distinguishes Canary Retail on top of retail baseline)

## Substrate (financial-accounting layer the spine sits on)

- [[platform/stock-ledger]] — perpetual-inventory movement ledger;
  the integrity surface every module communicates across
- [[platform/retail-accounting-method]] — RIM vs Cost Method, Open
  To Buy as the planning constraint
- [[platform/satoshi-cost-accounting]] — sub-cent unit cost as
  Canary's innovation; closes the 2002-vintage two-decimal gap
- [[platform/satoshi-precision-operating-model]] — the **top-down
  precision commitment**: extends satoshi precision from COGS to
  Customer Acquisition Cost + SG&A + IoT-tracked movement events.
  Every cost decomposed to its originating event with audit trail.
  Unifies the 13-module spine as instruments of cost decomposition.
- [[platform/perpetual-vs-period-boundary]] — the staged migration
  story: Phase 1 Canary runs in parallel observer mode (zero
  adoption friction); Phase 2 the merchant cuts over modules to
  Canary one at a time at their own pace; Phase 3 the stock ledger
  itself swaps to Canary as system of record (the moat). Until the
  ledger swap, every module is independently cutoverable and
  reversible. `integrated-hybrid` is the default route for every
  spine module. Established by [[case-studies/canary-finance-architecture-options|v2.F ADR]].

## Modules — full 13-module spine

**v1 — Differentiated-Five (shipping):**

- [[modules/T-transaction-pipeline]] — POS-agnostic ingestion; seal → parse → merkle → detect; ledger PUBLISHER (sale verb)
- [[modules/R-customer]] — ARTS Customer Model; identity layer + external_identities scaffold
- [[modules/N-device]] — ARTS Device Model; every device as first-class asset
- [[modules/A-asset-management]] — Bubble (anomaly detection over device population)
- [[modules/Q-loss-prevention]] — Chirp (37-rule detection) + Fox (INSERT-only case mgmt)

**v2 — CRDM expansion (design complete):**

- [[modules/C-commercial]] — items, departments, suppliers, OTB; ledger PUBLISHER (cost-update events)
- [[modules/D-distribution]] — receipts, transfers, RTVs; PRIMARY ledger PUBLISHER (6 verbs)
- [[modules/F-finance]] — PO/invoice 3-way match, RIM/Cost choice, period close; ledger RECONCILER + PUBLISHER (GL)
- [[modules/J-forecast-order]] — demand forecast + replenishment; ledger SUBSCRIBER + PUBLISHER (orders)

**v3 — Full spine (design complete):**

- [[modules/S-space-range-display]] — planogram, fixtures, shelf-edge labels; ledger SUBSCRIBER + GATEKEEPER (ordering gate)
- [[modules/P-pricing-promotion]] — promotion engine, markdowns, elasticity; ledger PUBLISHER (price/markdown events)
- [[modules/L-labor-workforce]] — scheduling, time tracking, productivity; ledger PUBLISHER (time entries) + SUBSCRIBER
- [[modules/W-work-execution]] — generalizes Q's Chirp+Fox to whole spine; ledger RECONCILER + cross-domain analyzer

**Module manifests** (machine-readable companions): see [[platform/module-manifest-schema]]. First example: `modules/T-transaction-pipeline.manifest.yaml`.

## Integrations

- `integrations/pos-adapters.md` — Square (live), future: Lightspeed,
  Clover, NCR, RAPID
- `integrations/payments.md`
- `integrations/ecommerce.md`
- `integrations/security-hardware.md`
- `integrations/mdm-and-itam.md`

## Architecture

- [[architecture/service-mesh]]
- [[architecture/tsp-pipeline]]
- [[architecture/detection-engine]]
- [[architecture/case-management]]
- [[architecture/evidence-chain]]

## Case studies (abstracted)

- `case-studies/smb-specialty-archetype.md`
- `case-studies/multi-store-apparel.md`
- `case-studies/food-and-beverage.md`
- `case-studies/sporting-goods.md`
- `case-studies/mlm-direct-selling.md`

## Persona — the Virtual Store Manager (VSM)

- `.claude/skills/canary-vsm.md` — composed agent persona that knows the entire 13-module spine via the existing Owl runtime. v1 Owl speaks T/R/N/Q today; gains modules as they ship. The merchant's single conversational front door.
- [[platform/module-manifest-schema]] — the machine-readable manifest format every module ships alongside its prose `.md`; the executable spec the VSM and orchestrator read

## Roadmap

- [[roadmap/v1-differentiated-five]] — T+R+N+A+Q shipping
- [[roadmap/v2-crdm-expansion]] — C/D/F/J modules (design complete; implementation pending)
- [[roadmap/v3-full-spine]] — S/P/L/W (design complete; implementation deferred until v2 stabilizes)

## Siblings

- `~/CATz/` — Canary Agent Taskforce: GrowDirect's methodology
  vault (how GrowDirect designs and delivers — agent-native)
- `~/GrowDirect/Canary/` — product code

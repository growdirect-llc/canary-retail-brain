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

> **Status (2026-04-26):** All 13 module manifests are deepened with entities + MCP tools + integrations + security + CRDM alignment. All 13 narratives audited (≥1500 words each). The manifests are now machine-readable specs the VSM and orchestrator consume directly.

**v1 — Differentiated-Five (shipping; manifests deepened ✓):**

- [[modules/T-transaction-pipeline]] — POS-agnostic ingestion; seal → parse → merkle → detect; ledger PUBLISHER (sale verb)
- [[modules/R-customer]] — ARTS Customer Model; identity layer + external_identities scaffold; multi-tier (retail / landscaper / commercial / wholesale)
- [[modules/N-device]] — ARTS Device Model; every device as first-class asset; tokenization records for Counterpoint NSPTransaction surface
- [[modules/A-asset-management]] — non-saleable physical assets (equipment, fixtures, greenhouses, tractors, IoT devices); registry + lifecycle + depreciation + maintenance
- [[modules/Q-loss-prevention]] — Chirp (38-rule detection incl. Q-CP-01 restricted-item compliance) + Fox (INSERT-only case mgmt)

**v2 — CRDM expansion (design complete; manifests deepened ✓):**

- [[modules/C-commercial]] — items, departments, suppliers, OTB; ledger PUBLISHER (cost-update events)
- [[modules/D-distribution]] — receipts, transfers, RTVs, adjustments, cycle-counts, allocations; PRIMARY ledger PUBLISHER (6 verbs)
- [[modules/F-finance]] — PO/invoice 3-way match, RIM/Cost choice, period close, GL outbox; ledger RECONCILER + PUBLISHER (GL)
- [[modules/J-forecast-order]] — demand forecast + replenishment; vendor scoring + seasonal pre-book carry-forward; ledger SUBSCRIBER + PUBLISHER (orders)

**v3 — Full spine (design complete; manifests deepened ✓):**

- [[modules/S-space-range-display]] — items, categories, planograms, mix-and-match groups, shelf-edge labels; ledger SUBSCRIBER + GATEKEEPER (ordering gate)
- [[modules/P-pricing-promotion]] — multi-tier pricing, promotion engine, markdowns, elasticity; ledger PUBLISHER (price/markdown events)
- [[modules/L-labor-workforce]] — scheduling, time tracking, productivity, ghost-employee detection feed; **Canary-native option (d)** per Counterpoint SDD §6.12; ledger PUBLISHER (labor cost) + SUBSCRIBER
- [[modules/W-work-execution]] — daily ops tasks + checklists + cross-domain exception-signal subscription; **Canary-native option (d)** per Counterpoint SDD §6.13; **status: design-parked, Phase 6+ shipping**; ledger SUBSCRIBER

**Module manifests** (machine-readable companions): see [[platform/module-manifest-schema]]. Every module ships both `<letter>-<name>.manifest.yaml` (executable spec) and `<letter>-<name>.md` (prose narrative) under `modules/`.

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

## Case studies

**Architectural & vertical (live):**

- [[case-studies/canary-finance-architecture-options]] — v2.F ADR establishing the integrated-hybrid default route across the spine
- [[case-studies/canary-iot-vendor-strategy]] — IoT vendor evaluation framework for v3+ Module L / S integration
- [[case-studies/canary-retail-diagnostic-archetype]] — generic SMB specialty diagnostic shape

**Recently authored (pending merge to main):**

- `case-studies/canary-ncr-product-line-decision.md` — NCR product-line ADR (Aloha vs Counterpoint vs Voyix), [Counterpoint locked](https://linear.app/growdirect/issue/GRO-560). On `origin/laptop/gro-560-ncr-product-line-decision-adr`.
- `case-studies/lawn-and-garden-rapidpos-suite.md` — full-stack L&G operating-platform playbook (the offer side). [GRO-588](https://linear.app/growdirect/issue/GRO-588). On `origin/laptop/gro-588-lg-rapidpos-suite-playbook`.
- `case-studies/lawn-and-garden-catz-phase1-diagnostic.md` — L&G specialty retail CATz Phase I diagnostic (the demand side; complement to the playbook). [GRO-596](https://linear.app/growdirect/issue/GRO-596). On `origin/laptop/gro-588-lg-rapidpos-suite-playbook`.

**Aspirational / placeholder (not yet authored):**

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

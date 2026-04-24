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

## Modules (linked to spine)

- [[modules/t-transaction-pipeline]] — TSP, POS-agnostic, webhook-first
- [[modules/r-customer]] — ARTS Customer Model
- [[modules/n-device]] — ARTS Device Model
- [[modules/a-asset-management]] — Bubble / threat detection /
  asset registry
- [[modules/q-loss-prevention]] — detection engine + case management
- `modules/c-commercial.md` — items, departments, suppliers (roadmap)
- `modules/d-distribution.md` — inventory movement (roadmap)
- `modules/f-finance.md` — PO, invoice (roadmap)
- `modules/j-forecast-order.md` — forecast + ordering (roadmap)
- `modules/s-space-range-display.md` — SRD (roadmap)
- `modules/p-pricing-promotion.md` — promotion engine (roadmap)
- `modules/l-labor-workforce.md` — labor and workforce (roadmap)
- `modules/w-work-execution.md` — generalized detection + case for
  all domains (roadmap)

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

## Roadmap

- [[roadmap/v1-differentiated-five]] — T+R+N+A+Q shipping
- [[roadmap/v2-crdm-expansion]] — C/D/F/J modules
- [[roadmap/v3-full-spine]] — remaining modules + governance

## Siblings

- `~/KATZ/` — methodology vault (how GrowDirect designs and
  delivers)
- `~/GrowDirect/Canary/` — product code

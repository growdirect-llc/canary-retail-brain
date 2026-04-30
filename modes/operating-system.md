---
title: Operating System Mode
classification: confidential
nav_order: 2

---

# Operating system

## What this is

Canary as the retail backbone. Replace the on-premise backoffice. The platform runs the operational loops — receiving, replenishment, three-way match, inventory, sales audit, loss prevention, KPI surfacing — continuously. The merchant steps in for strategy, signing authority, and customer-facing work.

## Who it's for

Specialty retailers, ~$5M to ~$50M annual sales, running aging Counterpoint, Epicor, or Retek-derivative backoffices. Wearing every hat. Want the department they cannot afford to hire.

## What changes

| Before | After |
|---|---|
| Backoffice server in a closet, SQL Server license, MSP contract, IT contractor on retainer | Cloud-native platform, no on-premise hardware, no MSP scope for the backoffice |
| Capex on hardware refresh every 3–5 years | Operating expense, predictable, scales with revenue |
| POS terminal as expensive endpoint | POS terminal as thin client; intelligence in the platform |
| One person who knows how it works (single point of failure) | Operational knowledge in the platform; merchant operates from the dashboard |
| Spreadsheet-driven OTB, manual reconciliation, monthly close | OTB as a wallet; automatic reconciliation; KPIs surface in real time |
| Annual physical inventory shock | Continuous shrink attribution; annual count confirms the accrual rather than producing a surprise |

## What stays the same

The merchant's customers. Their assortment. Their judgment. Their relationships with vendors. Their role on the floor.

## Starting move

Inventory and receipt history import. The platform's identity service stands up the merchant's namespace, ingests twelve months of transactions and PO records, and produces a baseline KPI dashboard. From there modules phase in at the merchant's pace — the platform does not require a big-bang cutover. Each module is independently cutoverable and reversible.

## Implementation posture

- **Phase 1 (week 1–4):** Namespace + history ingest. Baseline KPI dashboard live. Existing POS continues as system of record.
- **Phase 2 (month 2–6):** Module cutover, one at a time. Loss prevention typically first (immediate value, low operational risk). Then receiving, then commercial / OTB. The merchant chooses the sequence.
- **Phase 3 (month 6+):** The platform's stock ledger becomes system of record. Backoffice software contracts and hardware are retired.

The phasing is the discipline. Every cutover is reversible up to Phase 3. The merchant never bets the whole operation on a date.

## Pricing posture (placeholder — under negotiation per merchant)

Canary's commercial structure follows a base subscription plus a meter on payroll-to-revenue ratio (per the platform thesis). The base is predictable; the meter aligns Canary's revenue with merchant operational efficiency. Specific tiers, base prices, and meter rates are negotiated per engagement and per channel partner.

## Related

- [Why Canary](../why/why) — the three rails and the meter model this mode delivers
- [Transformation mode](transformation) — the project-scoped engagement that often precedes operating-system commitment
- [Modules](../modules/modules) — the 13-module spine that runs the operational loops
- [Engineering](../engineering/nfrs) — NFRs, scale, security, compliance for the IT partner

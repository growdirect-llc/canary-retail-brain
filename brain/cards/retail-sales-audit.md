---
card-type: domain-module
card-id: retail-sales-audit
card-version: 1
domain: finance
layer: domain
status: approved
feeds: [retail-operations-kpis, retail-inventory-valuation-mac]
receives: [retail-site-management, retail-merchandise-hierarchy]
tags: [sales-audit, POS, transaction-audit, till-balancing, over-short, cash-reconciliation, ACH, ReSA, financial-control]
last-compiled: 2026-04-29
---

## What this is

The retail sales audit model: the process of validating, reconciling, and correcting POS transaction data from store close through financial posting — including till balancing, over/short management, transaction-level exception resolution, and the automated clearing house (ACH) settlement that moves validated sales data into financial systems.

## Purpose

Sales audit is the financial control point between the store and the general ledger. Every sale, return, void, tender, and cash movement that occurs in a store must be validated before it enters the financial record. Without sales audit, POS errors — whether from cashier mistakes, system failures, or fraud — flow directly into inventory, revenue, and cash reporting. Sales audit catches these errors at the source, at the store/day level, before they compound across weeks and periods. It is also the primary cashier accountability mechanism: the till balance reveals whether a cashier's drawer matches what the POS recorded.

## Structure

**POS data flow** — Sales audit sits between the POS system and the financial/merchandising systems. At store day-close, the POS transmits a transaction file to the sales audit system. Sales audit validates the file, applies audit rules, resolves exceptions, and releases approved transactions downstream to inventory, financial reporting, and replenishment.

**System variables and audit rules** — Audit rules are user-defined validation criteria applied to incoming POS transactions. Rules control: acceptable over/short thresholds by store and till type, transaction types requiring mandatory review, tender type validation (check amounts, card authorization codes), and totals reconciliation (register total vs. expected total). Rule wizards allow non-technical users to build validation logic without programming. Well-configured rules focus audit attention on genuine exceptions — not every transaction.

**Sales audit maintenance** — Foundation data for the audit process: store configurations (which stores are audited, at what frequency), register configurations, cashier IDs, tender types, and totaling structures. Audit maintenance data must be current — a new register not configured in sales audit produces unmatched transactions.

**Transaction maintenance** — The core audit workflow. Auditors review flagged transactions, apply corrections, and post adjustments. Transaction exceptions fall into categories: voids and no-sales above threshold, returns without receipt, price overrides, tender discrepancies, and system-generated error transactions. Each exception type has a defined resolution path. Interactive exception navigation guides the auditor through resolution in priority order — highest-dollar exceptions first.

**Store/day close audit** — The primary reconciliation event. At day close, the system compares: (1) cashier-counted till amounts against POS-recorded tender totals by till and tender type; (2) total net sales per register against expected totals derived from transaction detail; (3) store-level totals against independently transmitted summary data. The result is an over/short position per till, per register, and per store. Over/short outside tolerance requires investigation and sign-off before the store/day is posted to the general ledger.

**Over/short management** — Over/short positions are classified by cause: cashier counting error, cashier handling error (making change incorrectly), POS error, or unexplained. Unexplained over/short above a defined threshold triggers a loss prevention review. Chronic over/short at a specific till or cashier is a fraud signal. Historical over/short trending by cashier is a key LP metric.

**ACH maintenance** — For stores that accept checks, the sales audit system manages the automated clearing house (ACH) file: the electronic batch that submits check data to the banking network for clearing. ACH maintenance covers bank account configuration, batch submission timing, and returned item (NSF) processing.

**Audit trail** — Every correction, override, and adjustment made in the sales audit system is recorded with user ID, timestamp, and reason code. The audit trail is a legal record — it must be tamper-evident and complete. Auditors cannot delete transactions; they can only post adjustments against them. The audit trail is the evidentiary foundation for any financial restatement or loss investigation.

## Consumers

The Finance/GL module receives validated, posted sales data from sales audit at store/day close. The Inventory module updates on-hand quantities based on validated sales (not raw POS data). The Loss Prevention function reads over/short history and cashier exception reports as primary investigation inputs. The Operations Agent monitors store/day close completion rates and over/short trends as operational health indicators.

## Invariants

- No sales data posts to the general ledger without a completed sales audit close for that store/day. Unaudited data in financial reports is a control failure.
- The audit trail is append-only. Corrections are adjustments against the original record — not overwriting it.
- Over/short thresholds must be configured per store and tender type before go-live. A sales audit system with no rules configured passes everything and catches nothing.

## Platform (2030)

**Agent mandate:** Finance Agent owns sales audit execution — rule application, exception triage, and ACH submission. Operations Agent monitors store/day close completion rates and over/short trends continuously. Loss Prevention function reads cashier exception data from the Operations Agent surface, not from periodic reports. No agent posts adjustments to the GL without merchant authorization for exceptions above the defined threshold.

**Real-time exception detection vs. end-of-day batch.** Traditional sales audit is a next-morning batch process: the store closes, the file transmits overnight, auditors work the exception queue the following day. In the Canary Go posture, the Operations Agent monitors the POS transaction stream in real time during the business day. Tender discrepancies, excessive voids, and unusual return patterns surface as intra-day alerts — before the store closes — when intervention is still actionable. End-of-day reconciliation remains required for GL posting; real-time monitoring provides the early warning layer.

**Blockchain evidence anchor for audit trail.** The Canary Go evidentiary model applies to sales audit corrections. Each audit adjustment — till override, transaction correction, over/short resolution — is hashed and anchored on the L2 evidence chain at the time it is posted. The audit trail is not just a database record; it is an on-chain timestamped event. For loss prevention investigations, this means the correction record is cryptographically tamper-evident, not just access-controlled in a database that an admin could modify.

**Cashier over/short as Operations Agent signal.** Traditional over/short analysis runs as a periodic LP report. Operations Agent monitors cashier-level over/short patterns continuously. When a cashier's rolling over/short frequency or magnitude exceeds the LP threshold, the alert surfaces immediately — not at the next monthly review. Pattern-based signals (cashier always short on specific tender types, over/short correlated with specific shift times) are surfaced as investigation candidates, not just statistics.

**MCP surface.** `store_close_status(site_id, date)` returns audit completion status and over/short position. `cashier_exceptions(site_id, period)` returns cashier-level over/short history ranked by frequency and magnitude. `audit_exceptions(site_id, date)` returns unresolved transaction exceptions with priority ranking. `daily_sales(site_id, date)` returns validated net sales by department after audit close — the canonical sales figure for financial and inventory systems.

**RaaS.** Sales audit is the primary input gate for the receipt chain. Every validated POS transaction is a receipt event; the audit close is the event that makes the receipt canonical — the timestamp after which receipt data may enter financial and inventory systems. Unaudited data must not enter the receipt chain. Till balance events, correction events, and over/short resolutions are all sequenced within the store/day close window; an adjustment posted after close is a new event, never a retroactive change to the closed receipt. `daily_sales(site_id, date)` from SQL indexed on (site_id, business_date); `store_close_status(site_id, date)` from Valkey hot cache (polled by downstream systems waiting for close confirmation before they can proceed). Cashier over/short queries (rolling 13 weeks per cashier) indexed on (cashier_id, business_date). Validated sales and audit correction log exportable for GL, inventory, replenishment, and LP investigation.

## Related

- [[retail-operations-kpis]] — over/short rate and store close completion rate are LP and financial operations KPIs
- [[retail-inventory-valuation-mac]] — validated sales trigger MAC updates; unaudited POS data must not update inventory
- [[retail-site-management]] — store configuration drives audit rule assignment and till structure
- [[retail-ap-vendor-terms]] — ACH maintenance parallels the banking integration in AP settlement

---
date: 2026-04-24
type: platform-substrate
owner: GrowDirect LLC
classification: confidential
tags: [substrate, architectural-principle, perpetual-vs-period, integration-pattern, integrated-hybrid, boundary]
---

# The Perpetual-vs-Period Boundary

> **Architectural commitment.** Canary's *perpetual movement layer* runs in
> parallel with whatever the merchant uses today. The merchant's existing
> tools — accounting package, payroll, CRM, POS, e-commerce, supplier portal —
> stay the system of record at install. As trust builds, the merchant cuts
> over module by module from their existing tool to Canary's perpetual layer.
> The cutover is independent per module. Until the merchant swaps the
> *stock ledger itself* to Canary as system of record, every layer remains
> modular and reversible.

## The staged migration — parallel run → modular cutover → stock-ledger swap

The boundary is **not** a static "Canary owns X / merchant owns Y forever"
arrangement. It is a three-phase migration the merchant controls.

### Phase 1 — Parallel observer (install + early operation)

Canary boots up alongside the merchant's existing tools. The perpetual
movement layer ingests every transaction, every receipt, every adjustment
event in real time and computes the perpetual ledger position. The
merchant's existing accounting / payroll / CRM keeps doing its job
unchanged. Both are computed; nobody is replaced.

The value Canary delivers in Phase 1:

- **Diagnostic** — VSM produces a Clarks-format diagnostic any time the
  merchant asks. It reads from Canary's perpetual ledger and answers
  questions the merchant's existing tools cannot answer (because their
  existing tools are period-summary, not perpetual).
- **Reconciliation surfaces** — Canary's perpetual position is compared
  to the merchant's existing tool's period summary. Where they disagree,
  Canary surfaces the gap with reason codes. The merchant decides whether
  Canary or the existing tool is correct in each case.
- **Loss prevention** — Q's Chirp + Fox runs against the perpetual stream
  immediately, no cutover required. This is the v1 wedge: full LP value
  in Phase 1 with zero migration friction.
- **IoT instrumentation expansion** — every IoT device the merchant adds
  (door counter, shelf RFID, cold-chain sensor, in-store positioning beacon,
  computer-vision people-counter) becomes another movement source on the
  perpetual ledger. The merchant's existing tools have no path to consume
  this signal; Canary's perpetual layer ingests it natively and surfaces it
  through the VSM. Each new IoT integration is a Phase-1 add — zero cutover
  friction, immediate value. The full operating-model implication is named
  in [[satoshi-precision-operating-model|Satoshi-Precision Operating Model]].

**Adoption friction in Phase 1: zero.** Merchant changes nothing. They
just connect Canary, give it OAuth, and start getting the parallel signal.

### Phase 2 — Modular cutover (per-module, merchant-paced)

As the merchant's confidence in Canary's perpetual ledger grows (typically
3–6 months of clean reconciliations), they begin cutting over individual
modules from their existing tools to Canary as the system of record for
that module's domain.

Each module is independently cutoverable. Order is the merchant's choice
but typically follows merchant pain:

- **High-pain first:** modules where the existing tool is most painful.
  E.g., a merchant on legacy LP software cuts over Q (Loss Prevention)
  immediately because Canary's Chirp+Fox is materially better. A merchant
  on QuickBooks Online but doing inventory in spreadsheets cuts over D
  (Distribution) early.
- **Low-pain later:** modules where the existing tool is "good enough."
  E.g., a merchant happy with Gusto for payroll keeps L (Labor) in
  parallel-observer mode indefinitely — Canary publishes time-clock events
  to Gusto via API and that's all.

After Phase 2, the merchant has a hybrid: some modules where Canary is
system of record, others where the existing tool still is. The perpetual
ledger underneath all of them remains Canary's authoritative copy.

**Adoption friction in Phase 2: incremental.** Each cutover is a deliberate
merchant decision. Switching cost grows incrementally with each cutover.

### Phase 3 — Stock-ledger swap (the sticky end-state)

The perpetual stock ledger itself becomes the merchant's authoritative
record. From this point, every other tool the merchant uses is a
*subscriber* of Canary's ledger rather than an independent authority.
QuickBooks reads its monthly inventory adjustment from Canary instead of
running its own; Gusto reads payroll inputs from Canary's labor movements;
the merchant's POS reads SOH from Canary's ledger instead of its own
internal inventory module.

This is the **moat phase**. The merchant has multiple tools, but they are
all downstream of one perpetual ledger of record — Canary's. Switching
cost is now high (the merchant would have to migrate every dependent
tool's read path back to its own internal source). Canary is the
substrate.

**Phase 3 is opt-in, not forced.** Some merchants will live in Phase 2
forever and that is fine — they still consume Canary's perpetual signal,
they just keep the period-summary system of record in their existing
tool. Canary's revenue is the same; the strategic position is weaker but
the merchant is happier.

### Implementation route × cutover phase

The `implementation_route` field on the module manifest names the
*long-term shape* the module is designed for. A new `cutover_status`
field (per-merchant, runtime state — not per-module manifest) names the
*current phase* for that merchant for that module.

| route | parallel-observer | partial-cutover | full-cutover |
|---|---|---|---|
| `legacy-native` | n/a — module has no merchant equivalent; Canary always system of record | n/a | n/a |
| `package-integration` | Canary publishes events to merchant package; merchant package owns state | merchant elects to read state back from Canary for some queries | full subscription — merchant package becomes a Canary read-replica |
| `integrated-hybrid` | Canary owns perpetual; merchant tool owns period; both computed | merchant elects to read period summary from Canary's rollup of its perpetual | merchant tool reads everything from Canary; ledger swap complete |
| `multi-route` | merchant chooses route at install | merchant can change route per module without losing history | n/a |

The Morrisons frame told us *what shape* each module ships in. The
parallel→cutover staging tells us *how the merchant gets there* without
forced migration.

## Why this principle exists

The Morrisons IT Architecture v2.F (Finance) ADR (`Canary-Retail-Brain/case-studies/canary-finance-architecture-options.md`)
evaluated three implementation routes for v2.F:

- **Legacy native** — Canary builds full GL, owns the merchant's accounting system of record
- **Package integration** — Canary publishes events into the merchant's QuickBooks/Xero; merchant's package owns operational state
- **Integrated hybrid** — Canary owns the perpetual movement layer (POs, invoices, 3-way match, COGS posting); merchant's existing GL owns the P&L, A/P, A/R

Option C (integrated hybrid) won on every axis: 15.7 eng-years vs 27.9 (legacy)
or 18.3 (package); 3-month time-to-market vs 6 months or 4 months; highest
merchant adoption (merchants do not abandon their existing accounting); no
GL liability on Canary's side; cleanly extensible to RIM in v3.

The recommendation generalizes. The same boundary applies to every spine
module that touches a domain where merchants already have a tool. **Integrated
hybrid is the default Canary implementation route.**

## The boundary, defined

The perpetual movement layer:

- **Records every operational event in real time, at unit-of-measure granularity, against the canonical retail data model**
- Posts signed movements to the [[stock-ledger|stock ledger]] with conservation, cost-method consistency, and cycle-count reconciliation invariants
- Owns the cross-module integrity surface — every other module reads/writes through it
- Lives in Canary's `app` / `sales` / `metrics` schemas (potentially extended per module)

The period-summary layer:

- **Aggregates perpetual events into time-bounded summaries (period close, payroll run, monthly statement, quarterly report)**
- Posts journal entries to a chart of accounts; runs reconciliations against external sources (bank, supplier statements, tax filings)
- Owns the regulatory and tax surface — tax filings, financial statements, payroll filings
- Lives in the merchant's existing system (QuickBooks, Xero, Gusto, Paychex, Salesforce, NetSuite, etc.)

The boundary lives at the seam between operational signal (perpetual) and aggregate posting (period). Every Canary module declares where this seam lives for its domain.

## Why this boundary works for SMB merchants

Three reasons:

1. **Merchants don't abandon working tools.** An SMB retailer running QuickBooks for accounting will not switch to "Canary GL" no matter how good Canary's GL is. They will switch to an LP-and-inventory tool that respects their existing accounting and feeds it correctly. Same logic for payroll, CRM, e-commerce.

2. **Period summary is regulated; perpetual movement is not.** Tax filings, payroll filings, financial statements all come out of the period-summary layer. Canary owning that surface means Canary inheriting the regulatory burden — tax certifications per jurisdiction, payroll-tax accuracy guarantees, audit-trail attestation. The merchant's existing tool already carries this; let it.

3. **Perpetual is the strategic position; period is commodity.** The perpetual movement layer is what nobody else ships at SMB tier. Period-summary is shipped by every accounting package, every payroll system, every CRM. The product wedge is on the perpetual side. The period side is a commodity Canary should integrate to, not rebuild.

## The boundary, per module

Every spine module declares its perpetual-vs-period boundary in its manifest's `implementation_route` field (see [[module-manifest-schema#implementation-route|Module Manifest Schema § Implementation Route]]). The default is `integrated-hybrid`. The boundary placement per module:

| Prefix | Module | Perpetual layer (Canary owns) | Period layer (merchant tool owns) |
|---|---|---|---|
| **T** | Transaction Pipeline | All — sealed transaction stream | None (T is `legacy-native`; no merchant equivalent) |
| **R** | Customer | Unified identity + behavioral signals | CRM/loyalty campaigns (Klaviyo, Mailchimp, etc.) |
| **N** | Device | Device registry + telemetry | MDM/asset-management (Jamf, Kandji, etc.) |
| **A** | Asset Management | Per-device anomaly detection | None (no merchant-side equivalent at SMB tier) |
| **Q** | Loss Prevention | Detection (Chirp) + case (Fox) | Insurance claims / restitution tracking (merchant's HR or accounting) |
| **C** | Commercial | SKU/supplier identity + cost-update events | Supplier contract management; long-term planning (merchant ERP if any) |
| **D** | Distribution | Receipt / transfer / RTV / adjustment movements | Inventory valuation period close (merchant accounting) |
| **F** | Finance | Invoice match (3-way), COGS posting events | GL, A/P, A/R, P&L (QuickBooks / Xero / Wave) |
| **J** | Forecast & Order | Demand signal + forecast + ROP | Long-range merchandise planning (merchant tool if any) |
| **S** | Space, Range, Display | Planogram authoring + ordering gate | Capital fixture planning (merchant capex tool if any) |
| **P** | Pricing & Promotion | Markdown + price-change events that revalue ledger | Price display at POS; pricing strategy (merchant's commercial team) |
| **L** | Labor & Workforce | Time-clock entries + scheduled-shift movements | Payroll calculation, tax filing (Gusto / Paychex / ADP) |
| **W** | Work Execution | Cross-domain exception detection + case management | Compliance reporting + audit (merchant's external auditors) |

## What this means for product, sales, and engineering

**Product.** Every new module decision starts with: *what's the merchant already running for this domain?* If something already runs, the default is integrated-hybrid against it. If nothing runs, legacy-native is on the table.

**Sales.** The pitch is no longer "Canary replaces your stack." It is "Canary makes your stack actually work, by giving it the perpetual signal it has always needed and never had." This is a softer sell — merchants don't have to switch anything to start. They add Canary alongside what they already use.

**Engineering.** The integration surface is real work. Each `integrated-hybrid` module ships an OAuth flow + an event-publishing pipeline + a reconciliation surface (so when the merchant's period-summary tool disagrees with Canary's perpetual ledger, there's a defined reconciliation path). The boundary is engineered, not assumed.

## The corollary on positioning

This sharpens the [[../../GrowDirect/Brain/wiki/growdirect-viewpoint-virtual-store-manager|GrowDirect viewpoint]] one click deeper. Canary is **not** the merchant's one-stop shop in the sense of "we replace everything." Canary is **the operational substrate behind the merchant's existing one-stop-shop tools** — the perpetual layer that makes their accounting / payroll / CRM / POS actually correct.

The Virtual Store Manager (VSM) is the conversational front door over that perpetual layer; it speaks the perpetual truth to the merchant ("here's what actually happened today; here's what your other tools will summarize this month"). The merchant's other tools handle the aggregation and the regulatory filings. Two surfaces, one source of truth — Canary's perpetual ledger.

## Open questions

1. **Reconciliation cadence per module.** When the merchant's QuickBooks shows £120 of inventory adjustment for the month and Canary's perpetual ledger shows £127 of cumulative shrink + RTV + cycle-count variance, who's right and who's surfaced first? Each integrated-hybrid module needs a reconciliation policy.
2. **Certification / partnership posture.** QuickBooks Online has a partner program. So does Xero, Gusto, Klaviyo. Should Canary aim for "official integration" status with each merchant tool we hybrid against, and what's the bar?
3. **Multi-route at install time.** Some merchants want native (no existing tool to integrate to). Some want package (existing tool, just plug in). Some want hybrid. The manifest schema supports `multi-route` but it has install-time UX implications we have not designed.

## Related

- [[stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]] — the substrate the perpetual layer posts to
- [[retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]] — the period-layer concepts the boundary is designed against
- [[satoshi-cost-accounting|Satoshi-Level Cost Accounting]] — the sub-cent precision that lives on the perpetual side
- [[module-manifest-schema|Module Manifest Schema]] — `implementation_route` field definition
- [[spine-13-prefix|The Canary Retail Spine — 13 Modules]] — every module declares its boundary
- [[../../GrowDirect/Brain/wiki/growdirect-viewpoint-virtual-store-manager|GrowDirect Viewpoint — VSM on a Perpetual Ledger]]
- [[../case-studies/canary-finance-architecture-options|v2.F Finance Architecture Options ADR]] — the decision that established this principle
- [[../../GrowDirect/Brain/wiki/canary-architecture-decisions-index|Canary Architecture Decisions Index]]

## Sources

- v2.F Finance Architecture Options ADR (this principle's worked-example origin)
- Morrisons IT Architecture Final Deliverable v1.0 (IBM BCS, 2006) — the Sell/Plan/Move/Buy + Legacy/Package/Integrated frame
- Retek RMS perpetual-inventory ledger pattern (the substrate the perpetual side posts to)
- GrowDirect Viewpoint — Virtual Store Manager on a Perpetual Ledger

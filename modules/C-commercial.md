---
classification: confidential
owner: GrowDirect LLC
type: module-spec
prefix: C
status: v2 (design)
sibling-modules: [D, F, J]
---

# C — Commercial

The commercial module owns the item catalog, merchandising hierarchy, supplier master, and Open-to-Buy (OTB) allocation across the retail organization. C is the principal source of truth for what the retailer sells, how it is organized, who supplies it, and how much budget remains to purchase new inventory.

C is one of the [[spine-13-prefix#v2-crdm-expansion-c-d-f-j|v2 CRDM expansion]] modules. It closes the commercial-dimension gap that single-channel systems miss: multi-store assortment, department and supplier hierarchies, OTB enforcement at the buyer level, and cost-update propagation across the stock ledger when supplier prices change.

## Purpose

C owns four jobs:

1. **Curate the item and merchandising catalog.** One row per SKU per organization, with hierarchy (department → class → subclass), supplier linkage, and cost/retail attributes. Items that cannot be curated do not exist on the stock ledger.
2. **Calculate and enforce Open-to-Buy.** Per-department or per-buyer OTB budgets in retail or cost currency. When a Distribution module (D) attempts to receive a purchase order, C validates it against available OTB headroom; overages are either rejected or flagged for re-plan depending on merchant policy.
3. **Publish cost-update events.** When supplier landed cost changes (invoice variance, supplier price adjustment, tariff/duty variance), C publishes a ledger movement that revalues on-hand inventory and posts cost-of-goods variance to the general ledger.
4. **Provide the buyer and merchandiser surface.** Read-only and write-capable MCP tools for item-master lookup, assortment validation, OTB headroom inquiry, cost-update auditing, and supplier performance analysis.

C does **not** own:

- Pricing and markdown strategy. That belongs to [[P-pricing-promotion|P (Pricing & Promotion)]] in v3.
- Forecasting and replenishment recommendations. That belongs to [[J-forecast-order|J (Forecast & Order)]].
- Physical space allocation and planograms. That belongs to [[S-space-range-display|S (Space, Range, Display)]] in v3.
- Invoice matching and financial close. That belongs to [[F-finance|F (Finance)]].

## CRDM entities touched

| CRDM entity | C's relationship | How |
|---|---|---|
| **Things** | **Owns** the SKU/item subset | One row per SKU per organization with hierarchy, supplier link, cost/retail |
| **Places** | Reads | Joins to department/location hierarchy for OTB allocation; doesn't curate Places itself |
| **Events** | Reads | Subscribes to stock-ledger movements to track on-hand and cost basis for OTB calculation |
| **Workflows** | Triggers | Publishes cost-update events that become ledger movements (owned by D/F co-publishers) |
| **People** | Reads | Identifies buyer/merchandiser owners of departments; doesn't curate People itself |

C's posture: **C is a Things registry (SKU master) that publishes cost-update events into the stock ledger and enforces OTB constraints on incoming purchase orders.** C reads ledger state to calculate OTB headroom; C does not modify ledger directly.

## ARTS mappings

ARTS does not define a Merchandise Hierarchy or Supplier Master specification. Canary defines these internally:

| Canary construct | Definition |
|---|---|
| Merchandise Hierarchy | Organization-specific tree: division → department → class → subclass → SKU, where each node has cost-method designation (RIM or Cost Method per [[../platform/retail-accounting-method#choosing-between-them—decision-matrix|Retail Accounting Method]]) |
| SKU Master | Item entity with UPC, supplier cost, retail price, cost-method assignment, cost-complement allocation (RIM) or FIFO/weighted-average designation (Cost Method) |
| Supplier Master | Vendor entity with payment terms, invoice-reconciliation policy, performance SLA tracking, cost-variance tolerance thresholds |

Cross-reference to ARTS:

- ARTS POSLog includes `catalog_object_id` (C's SKU ID)
- ARTS Customer Model has no Supplier or Hierarchy construct (retail-facing, not back-office)

## Ledger relationship

**C is PUBLISHER and CO-ANALYST for Open-to-Buy calculation.**

Movements C publishes to the stock ledger:

| Movement | Trigger | Effect on ledger |
|---|---|---|
| **Cost-update event** | Supplier invoice variance (reIM module finding discrepancy) or supplier price change | Posts `+/-` cost adjustment to on-hand inventory at landed-cost layer; posts GL variance entry |
| **Reclassification event** (future) | Item moves from one cost-method department to another | Posts value revaluation if cost-method changes (RIM → Cost or vice versa) |

Ledger reads C consumes:

- **Stock-on-hand (SOH)** — current quantity and value per item per location, read from the ledger snapshot. C uses SOH to calculate OTB headroom: `OTB = Planned EOH + Planned Receipts + Planned Markdowns − Planned Sales − Current SOH`.
- **Movement history** — inbound receipts, sales velocity (via integration with J Forecast & Order), markdowns (via integration with P Pricing & Promotion). Used to validate OTB model assumptions.

**Co-owner of OTB calculation** — C calculates OTB headroom; F (Finance) owns the RIM/Cost-Method choice that determines the currency (retail dollars vs cost dollars); J (Forecast & Order) owns the demand forecast that feeds planned sales and markdowns into the OTB formula.

**Perpetual-vs-period boundary.** Canary owns: SKU/supplier identity + cost-update events. Merchant tool owns: supplier contract management; long-term commercial planning (merchant ERP if any). Default implementation route: `integrated-hybrid`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (data producers):

- Supplier invoice/purchase order system (cost data, landed cost)
- Internal buyer/merchandiser input (assortment changes, department hierarchy, supplier mapping)
- Finance system (cost-method designation per department, GL account mapping)

**Downstream consumers** (data subscribers):

- **D (Distribution)** — C provides item-master lookup for receiving; D queries C to validate an item exists and has a cost method before posting a receipt movement
- **F (Finance)** — C publishes cost-update events; F subscribes to post cost-variance entries to the GL
- **J (Forecast & Order)** — J reads C's item master and OTB headroom to constrain replenishment recommendations; J requests OTB headroom check before suggesting a PO
- **P (Pricing & Promotion)** — P reads C's item master and publishes markdown events that C and F coordinate on cost revaluation
- **Q (Loss Prevention)** — Q reads C's item master and supplier hierarchy for context in exception workflows (e.g., "which supplier has high shrink rates")

## Agent surface

C exposes MCP tool families for buyer and merchandiser workflows:

- **Item-master lookup** — query SKU, UPC, hierarchy, supplier, cost/retail, cost method
- **OTB headroom inquiry** — check available OTB per department / per buyer with drill-down to SOH, planned sales, planned markdowns
- **Cost-update audit trail** — inspect all cost-update events posted to an item over a date range; see GL impact
- **Supplier performance** — query variance rates, invoice-match percentage, on-time delivery, cost-change frequency
- **Assortment validation** — check which items are eligible for a store, department, or location based on space/range constraints (read-only; modification is S's responsibility in v3)
- **Department OTB re-plan** — (restricted) adjust OTB ceiling for a department, triggering downstream recalculation of headroom and PO-recommendation gates in J

## Security posture

- **Auth.** All writes (OTB adjustment, cost-update approval) require `buyer` or `merchandiser` role. MCP tool-level role checking enforced.
- **Tenant scoping.** Every row carries `merchant_id`; every read is row-level-secured to the requesting merchant. Item master is merchant-specific (no shared catalogs at v2).
- **PII handling.** Supplier names and contact data are stored as opaque text; no email/phone fields in C's schema. Supplier contact is resolved at query time via external CRM integration.
- **Auditability.** Every cost-update event is logged with `posted_by`, `posted_at`, `reason_code` (supplier price change, tariff, variance resolution, etc.). Cost-update audit trail is immutable.
- **OTB enforcement.** D module checks C before accepting receipt; if over-OTB, D flags the receipt for C's approval (soft mode) or rejects it outright (strict mode, per merchant config).

## Roadmap status

- **v2 (design)** — Item master, department hierarchy, supplier master, OTB calculation and enforcement. Cost-update events to stock ledger. Read-only and restricted-write MCP tools for buyer workflows. No cross-merchant catalog; no dynamic pricing within C (pricing owned by P in v3).
- **v2.1** — Reclassification support when items move between RIM and Cost-Method departments. Extended supplier performance analytics.
- **v3** — Integration with S (Space, Range, Display) for assortment-eligibility gating. Integration with P (Pricing & Promotion) for markdown-driven cost revaluation.

## Open questions

1. **OTB currency choice.** Should OTB be expressed in retail dollars (natural for RIM departments) or cost dollars (natural for Cost Method departments)? Per-merchant config? Or per-department?
2. **Multi-store assortment.** Do all stores carry all items, or is there a store-level assortment matrix? If matrix, who owns it — C (item master) or S (space) in v3?
3. **Supplier cost reconciliation.** When an invoice variance is found (ReIM module), who initiates the cost-update event — Finance (F) or Commercial (C)? Current assumption: F publishes, C reads and logs.
4. **Cross-merchant shared items.** If GrowDirect ever operates multiple brands/concepts under one platform, can they share an item master, or must it be duplicated per merchant?

## Related

- [[../platform/stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]]
- [[../platform/retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]]
- [[../platform/crdm|Canonical Retail Data Model (CRDM)]]
- [[../platform/spine-13-prefix|The Canary Retail Spine — 13 Modules]]
- [[D-distribution|D (Distribution)]]
- [[F-finance|F (Finance)]]
- [[J-forecast-order|J (Forecast & Order)]]
- [[P-pricing-promotion|P (Pricing & Promotion)]] (v3, future integration)
- [[S-space-range-display|S (Space, Range, Display)]] (v3, future integration)

## Sources

- [[../../GrowDirect/Brain/wiki/secure-merchandising-rfp-evant-response-2003|Merchandising System RFP — Evant Response (2003)]] — catalog and hierarchy design reference
- [[../../GrowDirect/Brain/wiki/katz-scm-2003-archetype|Katz SCM 2003 Archetype]] — supplier and assortment sourcing patterns
- [[../../GrowDirect/Brain/wiki/retek-rms-perpetual-inventory|Retek RMS — Perpetual-Inventory Movement Ledger]] — cost-update and cost-method treatment reference

---

*Classification: confidential. Owner: GrowDirect LLC. Created 2026-04-24. C (Commercial) is a v2 module spec within the Canary Retail Spine. It is design-stage; implementation is pending.*

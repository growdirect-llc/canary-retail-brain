---
classification: confidential
owner: GrowDirect LLC
type: module-spec
prefix: D
status: v2 (design)
sibling-modules: [C, F, J]
---

# D — Distribution

The distribution module owns inventory movement across the retail organization: receipts from suppliers, transfers between locations, returns to vendors, inventory adjustments, and cycle-count reconciliation. D is the primary publisher of movements to the stock ledger; more of the ledger's canonical verbs originate in D than in any other module.

D is one of the [[spine-13-prefix#v2-crdm-expansion-c-d-f-j|v2 CRDM expansion]] modules. It closes the multi-location inventory gap: moving stock from warehouse to store, between stores, and back to suppliers; tracking in-transit inventory; reconciling physical counts to ledger snapshots.

## Purpose

D owns four jobs:

1. **Publish receipt movements.** When stock arrives from a supplier (PO matched to a bill of lading / BOL), post a receipt movement to the stock ledger with quantity, landed cost, and receipt-authorization code. Receipt is the first moment on-hand inventory is available for replenishment or sale.
2. **Publish transfer movements.** When inventory moves from location A (warehouse or store) to location B, post a transfer movement with quantity and any location-specific up-charges (freight, handling). Transfers reserve inventory during transit.
3. **Publish return-to-vendor (RTV) movements.** When stock is returned to the supplier (overstock correction, damage, end-of-season), post an RTV movement with quantity and reason code; cost is reversed at the return-approval stage.
4. **Publish inventory-adjustment and cycle-count movements.** When a physical count or audit finds discrepancies, post an adjustment movement with quantity delta and reason code (shrink, damage, found, gift, etc.). Adjustments are how the ledger reconciles to physical reality.

D does **not** own:

- Demand forecasting or replenishment optimization. That belongs to [[J-forecast-order|J (Forecast & Order)]].
- Cost reconciliation against supplier invoices. That belongs to [[F-finance|F (Finance)]].
- Operational execution (warehouse pickers, truck drivers, receiving staff). That belongs to [[W-work-execution|W (Work Execution)]] in v3.

## CRDM entities touched

| CRDM entity | D's relationship | How |
|---|---|---|
| **Events** | **Owns** the inventory-movement subset | Every receipt, transfer, RTV, adjustment, and cycle-count is a CRDM Event published to the stock ledger |
| **Things** | Reads | Foreign-keys item (SKU) and device (scanner, receiving workstation) on movements; doesn't curate |
| **Places** | Reads | Foreign-keys location (store, warehouse) on movements; doesn't curate Places itself |
| **Workflows** | Emits events | D publishes movements; F and Q subscribe and create Workflows (variance cases, exception escalations) |
| **People** | Reads | Identifies receiver/distributor who posted the movement; doesn't curate |

D's posture: **D is an Event factory that publishes inventory movements to the stock ledger.** D depends on C (item master), F (cost method validation), and J (demand forecast visibility) to understand the moves it publishes.

## Ledger relationship

**D is the PRIMARY PUBLISHER of stock-ledger movements.**

Movements D publishes:

| Movement | Trigger | Ledger effect | Reason codes |
|---|---|---|---|
| **Receipt (PO)** | Incoming stock matched to PO and receipt authorization | `+qty at cost` to on-hand; landed cost posted | PO number, receipt date, supplier variance |
| **ASN / In-transit** | Advanced Ship Notice received before physical arrival | `+qty pending` to in-transit inventory; holds value | ASN number, expected receipt date, carrier |
| **Transfer** | Stock move from location A to location B authorized | `-qty A, +qty B`; up-charges if applicable | Transfer request, transit-reason code, cost-center allocation |
| **Allocation** | Warehouse allocates stock to store orders (WH → store 1:N) | Reserves qty per store; holds value per store | Allocation order, demand plan, distribution center |
| **RTV (Return to Vendor)** | Stock returned to supplier (overstock, damage, end-of-season) | `-qty, -cost` reversal; cost deduction | RTV authorization, reason (defect, overstock, markdown overage, etc.) |
| **Inventory adjustment** | Physical count, receiving discrepancy, or audit finding | `+/-qty` with reason code; in-place or to shrink account | Count variance, shortage, overage, damage, gift, found, waste |
| **Cycle count** | Physical inventory reconciliation at snapshot date | Posts delta between physical count and ledger snapshot | Count date, variance reason (shrink, recordation error, theft), count type (unit-only or unit+dollar) |
| **Reclassification** (future) | Item moves from one location category to another | Value move only (no qty move) | Old location, new location, effective date |

Ledger reads D consumes:

- **Current SOH snapshot** — D queries the ledger at the moment a cycle count is initiated to establish the baseline that physical reality will reconcile against.
- **Movement history** — D may read recent receipt/transfer history to validate location status or forecast expected stock.

**Perpetual-vs-period boundary.** Canary owns: receipt / transfer / RTV / adjustment / cycle-count movements. Merchant tool owns: inventory-valuation period close (merchant accounting). Default implementation route: `integrated-hybrid`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (event producers):

- Purchase order system (POs generate receipt expectations)
- Warehouse management system (WMS) or manual receiving (ASN arrival, receipt authorization)
- Store operations (transfer requests, RTV requests)
- Inventory counting system (cycle-count data, physical count sheets)

**Downstream consumers** (data subscribers):

- **F (Finance)** — F subscribes to receipt movements to reconcile supplier invoices (ReIM module); F subscribes to RTV movements to reverse cost entries. F reads inventory-adjustment movements to validate shrink attribution.
- **C (Commercial)** — C reads receipt movements to validate OTB consumption; C reads transfer movements to track stock position by location.
- **J (Forecast & Order)** — J subscribes to movement history (receipts, sales via T, RTVs) to derive demand forecast and validate replenishment points.
- **Q (Loss Prevention)** — Q reads adjustment movements (especially shrink-attributed ones) to correlate with detection rules and case evidence.
- **W (Work Execution)** — W reads movements and flags anomalies (impossible quantities, timing inconsistencies, out-of-policy reason codes).

## Agent surface

D exposes MCP tool families for distribution and operations workflows:

- **Receipt posting** — authorize and post a receipt movement given PO number, BOL, received quantity, and cost
- **Transfer posting** — authorize and post a transfer movement given source location, destination, quantity, and up-charges
- **RTV posting** — post a return-to-vendor movement given RTV number, quantity, and reason code
- **Adjustment posting** — post an inventory adjustment with reason code (shrink, damage, found, etc.)
- **Cycle-count initialization** — snapshot current ledger state and initiate a physical count
- **Cycle-count reconciliation** — post count-adjustment movements to bring ledger into agreement with physical reality
- **In-transit visibility** — query inventory in-transit between locations, with expected arrival date
- **Location-level SOH** — query current on-hand per item per location from the ledger
- **Movement audit trail** — inspect all movements posted to an item or location over a date range

## Security posture

- **Auth.** Receipt, transfer, RTV, and adjustment postings require `warehouse-manager`, `receiver`, or `distribution-lead` role. Cycle-count posting requires `inventory-manager` role.
- **Tenant scoping.** Every movement carries `merchant_id`; every read is row-level-secured. D cannot post movements for another merchant.
- **Reason-code enforcement.** Every adjustment movement requires a mandatory reason code from a fixed list (shrink, damage, found, gift, waste, reconciliation, etc.). Invalid reason codes are rejected at validation time.
- **Auditability.** Every movement is hash-chained on the ledger; insertion order is cryptographically guaranteed. Movement audit trail is immutable.
- **Physical-reality reconciliation.** A cycle-count movement cannot post a variance that exceeds a per-merchant policy threshold (e.g., max 5% variance per count) without escalation to a manager.

## Roadmap status

- **v2 (design)** — Receipt, transfer, RTV, inventory-adjustment, and cycle-count movements. MCP tools for posting and querying movements. Integration with C for OTB validation (D checks with C before posting receipt if over-OTB). Integration with F for cost-method validation. No advanced features like allocation optimization or multi-location transfer planning.
- **v2.1** — Allocation optimization (WH → stores 1:N) with demand-weighted allocation logic. In-transit inventory visibility and expected-arrival-date tracking.
- **v3** — Integration with W (Work Execution) for anomaly detection and exception escalation. Integration with S (Space, Range, Display) for location-level assortment validation (item cannot be transferred to a location where it is not authorized to sell).

## Open questions

1. **ASN timing.** Should D post an ASN movement before physical receipt, or only after receipt is authorized? Current assumption: before (in-transit hold), with conversion to on-hand at receipt.
2. **Receiving discrepancy handling.** If received quantity doesn't match PO quantity (e.g., 98 received vs 100 ordered), is that posted as an inventory adjustment (shrink/overage) or as a separate "receiving variance" movement type?
3. **Location-level cost tracking.** Does D track cost per location (e.g., different freight cost to different stores), or is all landed cost centralized in C and D just moves quantities with marginal up-charges?
4. **Multi-location transfer chains.** If stock needs to move WH → DC → store, is that posted as two transfers or one transfer with intermediate node?

## Related

- [[../platform/stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]]
- [[../platform/crdm|Canonical Retail Data Model (CRDM)]]
- [[../platform/spine-13-prefix|The Canary Retail Spine — 13 Modules]]
- [[C-commercial|C (Commercial)]]
- [[F-finance|F (Finance)]]
- [[J-forecast-order|J (Forecast & Order)]]
- [[W-work-execution|W (Work Execution)]] (v3, future integration)
- [[S-space-range-display|S (Space, Range, Display)]] (v3, future integration)

## Sources

- [[../../GrowDirect/Brain/wiki/secure-5-inventory|Secure 5 Inventory]] — inventory-movement model and BOH/RTN/ADJ/RCT/EOH ledger pattern
- [[../../GrowDirect/Brain/wiki/retek-rms-perpetual-inventory|Retek RMS — Perpetual-Inventory Movement Ledger]] — movement verb taxonomy and RIB integration bus pattern
- [[../../GrowDirect/Brain/wiki/secure-retail-operating-model-2006|Secure Retail Operating Model (2006)]] — distribution center and store-DC transfer workflows

---

*Classification: confidential. Owner: GrowDirect LLC. Created 2026-04-24. D (Distribution) is a v2 module spec within the Canary Retail Spine. It is design-stage; implementation is pending.*

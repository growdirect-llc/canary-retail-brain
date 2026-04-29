---
card-type: domain-module
card-id: retail-inventory-valuation-mac
card-version: 2
domain: finance
layer: domain
status: approved
feeds: [retail-ap-vendor-terms, retail-merchandise-financial-planning]
receives: [retail-three-way-match, retail-receiving-disposition, retail-purchase-order-model]
tags: [inventory-valuation, MAC, moving-average-cost, landed-cost, full-cost, finance, COGS, stock-ledger]
last-compiled: 2026-04-29
---

## What this is

The inventory valuation model for retail: Moving Average Cost (MAC), the full landed cost components, and the transaction-trigger rules that govern when MAC is updated versus held constant.

## Purpose

MAC is the financial backbone of retail inventory accounting. It determines the cost of goods sold, the book value of on-hand inventory, and the basis for gross margin reporting. If MAC is wrong — because of missing freight costs, untracked allowances, or inconsistent transaction handling — every downstream financial report is wrong. The MAC model also underpins OTB planning and vendor profitability analysis. Accurate MAC requires consistent application across all transactions, not case-by-case accounting decisions.

## Structure

**MAC calculation** — Moving Average Cost is calculated by dividing the post-transaction extended inventory value by the post-transaction on-hand quantity. This is computed in real time at each triggering transaction. MAC is maintained at the SKU × site level (each item at each location has its own MAC). Minimum calculation precision is three decimal places; display rounds to two.

**Full cost model** — Beyond the vendor invoice cost, a retailer's true cost per unit includes components that most systems fail to capture systematically. The full cost model maintains both a standard MAC (for financial reporting) and a "full cost" field for internal decision-making:

| Cost component | What it covers |
|----------------|---------------|
| Vendor invoice cost | Base cost per unit as on PO |
| Expected vendor rebates | Volume and promotional rebates earned but not yet settled |
| Expected vendor allowances | Off-invoice and billback allowances |
| Cost of writing a PO | Administrative cost allocated per order |
| Cost of paying an invoice | AP processing cost per invoice |
| Cost of carrying inventory | Holding cost (capital + storage) |
| DC receiving and handling | Per-unit cost of receiving, put-away, picking, packing at DC |
| Inbound freight (DC) | Freight cost from vendor to DC, allocated by weight, cube, value, or units |
| Outbound freight (DC to store) | Freight cost from DC to store per unit |
| Store receiving and handling | Per-unit cost at store receiving |
| Shrink factor | Expected loss rate applied to unit cost |

**MAC trigger rules** — The following transactions automatically update MAC:

- Receipt of purchase order (cost, discounts, warehouse allowance, freight allowance)
- Freight estimation at PO receipt — estimated freight is allocated to each item's MAC proportional to weight, cube, value, or unit count (the allocation method is set per PO)
- Freight variance settlement — when actual freight differs from estimate and inventory is still on hand, variance is applied to affected items' MAC
- Expense transfers that increase on-hand quantities at a cost different from current MAC
- Style-to-style transfers (SKU reclassification) — receiving SKU MAC is updated
- Site-to-site transfers — receiving site MAC is updated
- Broker fee adjustments (where applicable)
- When post-transaction on-hand is zero and then goes positive: MAC is replaced with transaction cost

The following transactions do **not** update MAC:

- Sales (sales reduce quantity, COGS flows at current MAC, but MAC itself is unchanged)
- Customer returns (returns restore quantity at current MAC)
- Physical inventory adjustments
- Expense transfers that decrease on-hand
- Transactions that would result in zero or negative post-transaction on-hand
- Transactions that would produce a negative MAC

**Manual MAC adjustment** — When MAC must be corrected outside of a normal transaction flow (e.g., after a system error), a manual adjustment is authorized with a cross-reference number and allocated proportionally by units on hand across the affected sites. Manual adjustments trigger alerts to inventory managers and pricing analysts when the adjustment exceeds a predefined threshold (% or $ by vendor at item-site level).

## Consumers

The Finance module computes COGS from MAC at each sale. The Inventory module maintains MAC per SKU per site. Pricing analysts receive automatic alerts on significant MAC changes so retail price recommendations can be updated. The Merchandise Financial Planning process uses MAC to compute gross margin vs. plan. The Operations Agent monitors MAC health — specifically, frequency of manual adjustments and freight variance magnitudes — as indicators of data quality problems.

## Invariants

- MAC is always maintained at minimum three decimal places for calculation. Rounding to fewer decimals mid-transaction compounds errors across high-volume items.
- A transaction that would produce a negative MAC must not be posted without manual review and override. Negative MAC is always a data integrity signal.
- Freight estimation method (by weight, cube, value, or units) is set per PO and cannot be changed after the PO is receipted. Consistency is required for variance tracking.

## Platform (2030)

**Agent mandate:** Operations Agent owns MAC health monitoring. Business Agent reads MAC for gross margin planning and pricing decisions. Neither agent writes MAC directly — MAC is updated by the transaction engine; agents observe and alert.

**Dual cost basis — MAC + Satoshi.** Traditional MAC (fiat, local currency) is required for GAAP compliance and is fully supported. Canary Go runs MAC in parallel with a satoshi-denominated full cost basis per the ILDWAC extended Bitcoin standard. The satoshi cost basis tracks what each unit of inventory cost in Bitcoin-equivalent terms at time of receipt. This is not a replacement for GAAP MAC — it is an additional cost dimension that enables Bitcoin-native vendor settlement, L402-denominated OTB, and inflation-adjusted profitability analysis that fiat-only MAC cannot provide. When a vendor is paid via Lightning settlement, the satoshi cost of that payment is recorded against the relevant POs and updates the satoshi cost layer. Two cost ledgers run side by side. Merchants who don't use Bitcoin see only the fiat MAC. Merchants in the Bitcoin-native flow see both.

**Smart contract layer.** Vendor allowance credits and subsequent settlement adjustments — the events that most frequently corrupt MAC in traditional systems — are smart contract events on the AVAX vendor subnet. When a volume rebate accrues, the contract emits an event. When the settlement period closes, the contract executes the credit automatically. The event feeds the MAC adjustment workflow with a verifiable on-chain reference, eliminating the "we sent you a credit but the system never got it" category of disputes. Freight variance settlement follows the same pattern for smart-contract-enrolled carriers.

**Real-time anomaly detection.** Traditional MAC monitoring is batch: an analyst runs a report at period end and finds that MAC has drifted on 40 items. The Canary Go Operations Agent monitors MAC continuously. Alert triggers: (1) MAC changes by more than N% in a single transaction on a high-volume item — signals a bad receipt cost; (2) manual MAC adjustment volume exceeds baseline — signals systemic data quality failure; (3) freight variance magnitude exceeds the defined tolerance — signals the freight estimation method needs recalibration. Alerts surface to the merchant dashboard and to the Operations Agent incident queue in real time, not at month end.

**MCP surface.** `mac_lookup(sku, site)` returns current MAC for a given item-location. `mac_history(sku, site, n_periods)` returns the MAC time series with transaction-level audit trail. `cost_basis_delta(sku, site)` returns the gap between fiat MAC and satoshi cost basis — the signal for Bitcoin-native profitability analysis. These are low-bandwidth calls — a single MCP round-trip returns cost basis context for an agent that is making a pricing or ordering decision. Agents do not recompute MAC; they query it.

**RaaS.** MAC updates are triggered by receipt events — cost basis at any point in time is derivable only from the correctly ordered sequence of receipt events. This is the accounting definition of the perpetual inventory method; it works only if event sequence is preserved. Out-of-order processing produces an incorrect cost basis that compounds across every subsequent sale and margin calculation. `mac(item_id, site_id)` from Valkey hot cache (sub-100ms; called on every transaction for margin computation). Dual storage: Valkey for current MAC, SQL append-only event log for MAC history enabling point-in-time reconstruction for period-end audit. MAC history exportable for financial audit and period-end reporting.

## Related

- [[retail-three-way-match]] — confirmed receipts trigger the primary MAC update
- [[retail-receiving-disposition]] — defective allowances and RTV transactions affect MAC
- [[retail-merchandise-financial-planning]] — MAC is the cost basis for OTB and gross margin planning
- [[retail-ap-vendor-terms]] — subsequent settlement adjustments (rebates, allowances) flow back into MAC

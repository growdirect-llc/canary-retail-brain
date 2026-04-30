---
title: Satoshi-Level Cost Accounting — Sub-Cent Unit Cost on the Stock Ledger
date: 2026-04-24
type: platform-substrate
owner: GrowDirect LLC
classification: confidential
tags: [satoshi-cost, micropayment, l402, lightning, sub-cent, unit-cost, canary-innovation]
nav_order: 10

---

# Satoshi-Level Cost Accounting — Sub-Cent Unit Cost on the Stock Ledger

**Governing thesis.** The perpetual stock ledger as inherited from 2002-vintage retail systems (Retek, Oracle Retail, JDA) was constrained to two-decimal currency: unit costs round to $0.01, which is fine for items costing $10–$100 but catastrophic for fractional-cent items (shipping micro-fees per unit, loyalty-points cost basis, metered API consumption per transaction, Lightning channel routing fees). Canary's innovation is **satoshi-level cost accounting** — unit cost tracked in satoshis (the atomic unit of Bitcoin: 1 sat = 0.00000001 BTC ≈ $0.0001 USD at current rates) at the ledger layer, with fiat rounding captured at posting time. The ledger schema carries both `cost_msat BIGINT` (millisatoshis, for fine-grain precision) and `cost_usd_cents INT` (fiat rounding). Reconciliation tolerates the rounding gap. This is not "Bitcoin for Bitcoin's sake." It is the **only available unit for cost accounting on a retail ledger that wants to track agent-mediated transactions, metered consumption, and sub-cent operational costs**. The Goose implementation (GRO-117, already shipping) is the production proof: the GasMeter service prices 11 Canary operations from 0 to 500 sats and posts to per-merchant prepaid wallets. Extending that pattern to unit-cost-on-goods is the next move.

> **Note:** This article is the COGS-side foundation of the precision principle. The full operating-model commitment — extending satoshi precision to Customer Acquisition Cost, SG&A, and IoT-tracked movement events — is named in [[satoshi-precision-operating-model|Satoshi-Precision Operating Model]]. Read that article for the spine-wide implication; this article remains the COGS-specific deep dive.

---

## The 2002 Ledger's Hidden Constraint

The perpetual stock ledger as designed at Retek and Oracle Retail in the 1990s–2000s was built for a currency world: USD, GBP, EUR, with two-decimal precision. Cost accounting worked as follows:

**Unit cost = total cost of goods ÷ quantity received.**

For a case of 12 units at $12 landed cost: $12 ÷ 12 = $1.00 per unit. Rounded to the nearest cent.

For a case of 24 units at $1.20 landed cost: $1.20 ÷ 24 = $0.05 per unit. Fine.

For 500 units of an item at $0.97 cost: $0.97 ÷ 500 = **$0.00194 per unit.** Rounds to $0.00. The ledger now carries a unit cost of $0.00, and all 500 units on-hand are valued at $0.

This rounding works for soft-line and hard-line goods because the per-unit cost is usually high enough that $0.01 rounding is negligible. A $50 sweater with a unit cost of $25 — a 2 basis points rounding error — is undetectable.

It fails catastrophically for fractional-cent items:

### Use Cases Where $0.01 Rounding Breaks Down

**1. Shipping fees per unit**

An e-commerce fulfillment center adds a shipping/handling fee to SKUs. The fee structure is $0.005 per unit (half a cent). The ledger cannot record this cost per unit. The fee either disappears entirely (rounding to $0.00) or is lumped into a blanket "shipping" cost center that is never allocated to individual items.

**2. Loyalty-points cost basis**

A point-of-sale system offers customer loyalty points at a rate of 1 point per dollar spent. The retailer's cost per point (redemption liability) is $0.0067 USD (1 point = $0.67 redemption value, amortized across 100 points per customer session). Ledger rounding: $0.01. The cost basis is 1.5× overstated.

**3. Metered API and tool consumption**

Canary's agents (Chirp for detection, Fox for case management, Owl for analytics) consume compute and storage. The GasMeter service charges per operation in satoshis. Chirp's fraud check is 5 sats (~$0.0005). Fox's case creation is 20 sats (~$0.002). These costs are real and must be attributed to the merchant's SKU if the operation was triggered by a sale event for that SKU. Ledger rounding: $0.01. The cost is either $0.00 or the ledger carries no entry at all.

**4. Lightning channel routing fees**

The Goose (Canary's Lightning integration, GRO-117) allows merchants to accept Bitcoin payments via Lightning Network. A single Lightning routing fee is typically 1–100 millionths of a BTC — i.e., 1–100 satoshis. If the ledger carries a unit cost of $0.01, a $0.05 routing fee on a 1-BTC (~$40K) transaction is unmeasurable (rounding to $0.00).

**5. Agent-tool metering at the L402 layer**

The L402 protocol (see [[../../GrowDirect/Brain/wiki/growdirect-the-l402|The L402]]) implements HTTP 402 Payment Required: callers submit a request, receive an invoice for satoshis, pay the invoice, and get the response. A merchant API call might cost 10 sats (~$0.001). Multiply this across hundreds of calls per transaction and the per-unit cost becomes material. Rounding to $0.01 erases it.

### The Pattern

Every one of these is a **real cost incurred by Canary on behalf of the merchant**. Each cost needs to be:

1. Tracked at posting time (recorded in the ledger)
2. Attributed to the specific merchant and operation
3. Allocated to the specific SKU or transaction that triggered the cost
4. Reconciled monthly (did the actual costs match the attributed costs?)

The 2002 ledger cannot do this because it cannot express costs smaller than $0.01. The solution is not to lump these costs into a blanket "miscellaneous" account (which they often are, which is how they disappear from margin calculations). The solution is to extend the ledger's cost precision.

---

## The Canary Innovation — Satoshi-Level Cost Accounting

### The Schema Pattern

The stock ledger schema gains **two cost columns instead of one**:

```sql
CREATE TABLE ledger_movements (
    id UUID PRIMARY KEY,
    item_id UUID,
    location_id UUID,
    posted_at TIMESTAMP,
    
    -- quantity (unchanged)
    quantity_units NUMERIC,
    quantity_base_uom VARCHAR,
    
    -- cost: fiat (rounding-aware)
    cost_usd_cents INTEGER,          -- e.g., 500 for $5.00
    
    -- cost: satoshi-level (precise)
    cost_msat BIGINT,                -- e.g., 500000 for 500 millisatoshis
    
    -- rate: what was the conversion at posting time?
    satoshi_to_usd_rate NUMERIC(12,10),  -- e.g., 0.0000234 (1 sat = ~$0.000023)
    
    -- movement type and reason
    movement_type VARCHAR,           -- receipt, sale, transfer, etc.
    reason_code VARCHAR,
    
    -- who posted it
    posted_by VARCHAR,
    merchant_id UUID
);
```

### How It Works

When a movement is posted:

1. **Calculate the satoshi cost.** If the cost is a metered operation (e.g., Chirp detection = 5 sats), the satoshi value is the source of truth.
2. **Capture the rate.** Look up the current BTC/USD exchange rate at posting time. Record it in `satoshi_to_usd_rate`.
3. **Calculate the fiat cost.** `cost_usd_cents = ROUND(cost_msat × satoshi_to_usd_rate / 100000)`. (Note: 1 msat = 0.001 sats; 1 cent = $0.01; conversion is `msat × rate ÷ 100000`.)
4. **Post both.** The ledger carries both columns.

### Example

Chirp detects a refund anomaly and triggers a case. The cost of the Chirp operation is 5 sats (billed to GrowDirect, passed through to the merchant). The operation was triggered by a sale event for SKU #42 at Store #5.

At posting time, the rate is 1 sat = $0.000024 (i.e., 1 BTC = $41,666).

- `cost_msat = 5000` (5 sats = 5000 millisatoshis)
- `satoshi_to_usd_rate = 0.000024`
- `cost_usd_cents = ROUND(5000 × 0.000024 ÷ 100000) = ROUND(0.0012) = 0` 

The fiat rounding produces $0.00 (rounding down). The satoshi value is preserved: 5000 msat.

**Reconciliation logic:** At month-end, sum all `cost_msat` for the merchant. Sum all `cost_usd_cents`. Calculate the expected fiat value using the average rate for the month. If actual fiat ≠ expected fiat by less than 1%, accept the variance (rounding tolerance). If greater, investigate.

This tolerates rounding because the satoshi side is the source of truth. The fiat side is the business-facing value; the satoshi side is the auditable settlement record.

### Why This Solves the Problem

1. **Sub-cent operations are tracked.** A 1-sat operation ($0.000024) is recorded in the ledger, not lost to rounding.
2. **Attribution is precise.** Every metered cost is posted to the item and location that triggered it.
3. **Reconciliation is possible.** The satoshi side of the ledger is compared to actual Lightning payments or GasMeter charges. Rounding variance is tracked separately.
4. **Rate capture is audit-ready.** The rate at posting time is recorded. If the IRS ever wants to know "what was the cost basis of this item in BTC?", the ledger has the answer.

---

## The Goose Proof Point — GRO-117 Shipping

The Goose implementation ([[../../GrowDirect/Brain/wiki/growdirect-the-goose|The Goose — Bitcoin Money Machine]]) is the production evidence that satoshi-level cost accounting works.

The GasMeter service prices 11 Canary operations:

| Operation | Cost (sats) |
|---|---|
| Chirp fraud detection | 5–20 sats |
| Fox case creation | 20 sats |
| Owl search query | 1 sat |
| Condor event seal | 0.5 sats |
| TSP validation check | 50 sats |
| Identity master lookup | 1 sat |
| Device registry check | 2 sats |
| Asset anomaly detection | 10 sats |
| Loss-prevention rule eval | 3 sats |
| Forecast recommendation | 25 sats |
| Planning schedule update | 5 sats |

Each Canary module that performs an operation calls the GasMeter API. The API returns a Lightning invoice denominated in satoshis. The merchant's prepaid wallet (funded in BTC or via fiat→BTC gateway) pays the invoice. Settlement takes milliseconds.

The GasMeter ledger records every charge:

```
merchant_id | operation | sats | posted_at | status
--------------------------------------------------
m123        | Chirp     | 8    | 2026-04-24T11:23:45Z | settled
m123        | Fox       | 20   | 2026-04-24T11:23:46Z | settled
m456        | Owl       | 1    | 2026-04-24T11:23:47Z | settled
```

Canary's Owl agent (the merchant-facing analytics interface) can now answer questions like:

> _"How much did I spend on Chirp detections yesterday?"_

Response: "47 sats (approximately $0.0011) — 7 fraud alerts at an average of 6.7 sats each."

This is a **real accounting surface** that works only because costs are denominated in satoshis, not USD cents. Rounding 47 sats to USD produces $0.00 (if rates are ~$0.000024 per sat). The satoshi side preserves the precision.

### How This Extends to Goods

The GasMeter pattern extends directly to unit cost on goods:

```sql
INSERT INTO ledger_movements (
    item_id, location_id, 
    movement_type, reason_code,
    quantity_units, 
    cost_msat, satoshi_to_usd_rate,
    movement_at
) VALUES (
    'sku-42-widget', 'store-5',
    'receipt', 'PO-2026-0424-001',
    100,
    5000,  -- 100 widgets, $0.05 total satoshi cost (5000 msat total)
           -- → 50 sats per unit or 0.5 msat per unit
    0.000024,  -- rate at posting time
    NOW()
)
```

In this example, a receipt of 100 units includes a shipping fee (metered from GasMeter or another provider) of 5000 msat (5 sats, ~$0.00012 total, or ~0.12 sats per unit).

The fiat rounding: $0.00012 ÷ 100 units = $0.0000012 per unit → rounds to $0.00 per unit.

The satoshi side: 50 sats ÷ 100 units = 0.5 sat per unit. Precise.

Month-end reconciliation sums all cost_msat values and compares to actual Lightning or GasMeter charges. Discrepancies are investigated. Rounding variance is accepted within tolerance.

---

## L402 — The Broader Auth+Payment Layer

The L402 protocol (see [[../../GrowDirect/Brain/wiki/growdirect-the-l402|The L402]]) is broader than just the Goose. It applies satoshi-level billing to **API access, metered consumption, and any service that needs atomic, micropayment-gated access**.

Examples:

- **API access.** A Canary partner API call costs satoshis; the caller pays per call.
- **Content access.** A merchant querying specialized analytics or reports pays satoshis per query.
- **Tool access.** An agent calling a gated Canary tool (e.g., advanced Owl search) pays satoshis per call.

In all cases, the L402 layer:

1. Receives the request
2. Returns HTTP 402 with a BOLT11 Lightning invoice (denominated in satoshis)
3. Client pays the invoice
4. Handler returns the response
5. Satoshi charge is recorded in the service ledger

The same satoshi-level accounting applies everywhere. Costs are preserved at precision; rounding variance is tracked; settlement is final.

---

## Why This Is "Canary Native," Not "Bitcoin for Bitcoin's Sake"

Some might argue: "Why use Bitcoin satoshis? Why not just use millionths of a dollar?"

Three reasons:

1. **The unit is economically atomic.** A satoshi is the smallest unit of Bitcoin. It is not an arbitrary subdivision. The Lightning Network's fee structure, BTC's block-reward halving, and the global monetary architecture all reference satoshis as the atomic unit. Using sats aligns Canary's accounting with the monetary layer it settles on.

2. **Settlement is non-stateful.** Traditional accounting requires trust between parties (bank, processor, clearing house). Bitcoin settlement requires no trust — the proof is on-chain. A Lightning payment of 5 sats to a merchant is final. No chargebacks, no reversal risk. Canary's accounting can be built on settlements that are cryptographically final, not procedurally final.

3. **Reuses existing rails.** Canary doesn't need to build payment infrastructure. Lightning Network already exists, is battle-tested, and can route satoshi payments at scale. Goose (GRO-117) already ships. The infrastructure is done. Extending to unit-cost-accounting is leveraging what's already running.

This is not "we prefer Bitcoin." It is "we need an atomic unit of account that is both tiny (satoshis work; cents don't) and operationally final (Bitcoin works; credit cards don't)."

---

## Open Questions

1. **Fiat-rate capture cadence.** Should the rate be captured per transaction (exact) or daily (batch, simpler)? For SMB retail, daily is likely sufficient. Transactions posted the same day would use the same rate.

2. **Tax treatment of satoshi-denominated unit cost.** If a merchant's cost basis is recorded in satoshis and the merchant files taxes in USD, how does the IRS treat BTC-denominated cost? This is an unsettled question in tax law. Canary should consult with accounting/tax counsel before shipping this feature.

3. **Accounting standards alignment.** GAAP and IFRS do not yet codify satoshi-denominated cost basis. Merchants may face audit friction if their auditor is unfamiliar with the approach. This is educational friction, not a technical blocker, but it should be anticipated.

4. **FX variance accounting.** If a cost is recorded in satoshis but the merchant's reporting currency is USD, the cost basis is exposed to BTC/USD rate changes. Should the merchant record an unrealized FX gain/loss? This is a complex question for accountants. Canary should publish guidance.

---

## Implementation Roadmap

**Phase 1 (already complete):** GasMeter satoshi billing on agent operations (GRO-117 shipping).

**Phase 2 (next):** Extend the stock ledger schema to carry `cost_msat` alongside `cost_usd_cents`. Implement the reconciliation logic.

**Phase 3:** Canary's D (Distribution) and C (Commercial) modules post receipts with satoshi-denominated freight and handling costs (using GasMeter rates or supplier-specific rates).

**Phase 4:** F (Finance) module implements satoshi-to-fiat reconciliation at period close. GL posting carries both satoshi and fiat values.

**Phase 5:** Merchant dashboard and reporting expose satoshi cost data. Merchants can see per-item cost in both sats and USD.

---

## Related

- [[stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]]
- [[retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]]
- [[../../GrowDirect/Brain/wiki/growdirect-white-paper-micropayment|Micropayment Strategy White Paper]]
- [[../../GrowDirect/Brain/wiki/growdirect-the-goose|The Goose — Canary metering on Lightning (GRO-117)]]
- [[../../GrowDirect/Brain/wiki/growdirect-the-l402|L402 — the validation gate and protocol-level payment layer]]
- [[spine-13-prefix|The Canary Retail Spine — 13 Modules]]
- [[crdm|Canonical Retail Data Model (CRDM)]]

---

*Classification: confidential. Owner: GrowDirect LLC. Created 2026-04-24. This is a platform substrate document. Satoshi-level cost accounting is a Canary innovation that closes the fractional-cent cost gap in perpetual-inventory ledgers. It is production-proven on the Goose (GRO-117) and ready for extension to goods cost on the stock ledger.*

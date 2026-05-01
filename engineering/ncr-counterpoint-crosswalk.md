---
tags: [canary, go, ncr, counterpoint, vendor-crosswalk, adapter, cadence, cost-model, var, channel-partner, multi-var]
last-compiled: 2026-05-01
related: [canary-go-cadence-ladder, canary-go-endpoint-library, canary-go-satoshi-cost-model, canary-go-rapidpos-crosswalk, channel-revshare-architecture]
---

# Canary Go ↔ NCR Counterpoint (Direct VAR) — Vendor Crosswalk

> **Governing thesis.** NCR Counterpoint reaches the SMB specialty market through multiple VAR channels. RapidPOS is one VAR with a defined commercial relationship; **other VARs and direct-NCR deployments require a multi-channel attribution model** keyed by `var_of_record` at merchant onboarding rather than by `source_code` alone. This crosswalk documents the architectural refinement and surfaces it as the canonical model for any future NCR-direct or alternative-VAR deployment. The technical adapter is identical to the RapidPOS path (canary-bull + canary-edge); the commercial layer differentiates.

This crosswalk is a companion to [[canary-go-rapidpos-crosswalk|the RapidPOS crosswalk]] and clarifies the multi-VAR reality. **NCR Voyix is NOT a Canary partner** (per memory `project_ncr_voyix_is_competitor`) — they compete in LP/analytics. The "NCR direct" path here means merchants that purchased Counterpoint through any channel other than RapidPOS, including some who hold direct NCR contracts.

## The multi-VAR architectural reality

A single POS source (`counterpoint`) reaches merchants through multiple commercial channels:

| Channel | Status | Commercial relationship |
|---|---|---|
| RapidPOS (Counterpoint VAR) | **Active partner** | 20% rev-share, defined |
| Other regional VARs | TBD per VAR | Potential partner channels — onboard with defined rev-share |
| NCR-direct | TBD per merchant | Some merchants hold direct NCR contracts; no NCR-side channel partner; rev-share defaults to 0 unless specific arrangement |
| NCR Voyix | **Competitor — not partner** | Do not pursue partnership; integration access strategy routes through customer, not via NCR partnership |

**The key insight:** `SourceCode = "counterpoint"` does not uniquely identify a commercial channel. A second axis — VAR-of-record at merchant onboarding — is required for correct rev-share attribution.

## Architectural refinement: `var_of_record`

The current cost-calibration YAML keys channel rev-share by `source_code`. This is correct for single-channel sources (Square, Shopify) but breaks for multi-VAR sources (Counterpoint).

### Current model (works for single-channel sources)

```yaml
revshare:
  channels:
    counterpoint:                       # keyed by source_code
      partner_id: "rapidpos-uuid"
      share: 0.20
      lightning_address: "rapidpos@payments.example"
```

### Refined model (works for multi-VAR sources)

```yaml
revshare:
  channel_partners:                     # keyed by partner_id
    rapidpos:
      partner_id: "rapidpos-uuid"
      share: 0.20
      lightning_address: "rapidpos@payments.example"
      sources: ["counterpoint"]         # which source codes this partner channels
    ncr-direct:
      partner_id: null                  # null = no rev-share recipient
      share: 0.0
      lightning_address: null
      sources: ["counterpoint"]
    other-counterpoint-var:
      partner_id: "var-x-uuid"
      share: 0.15                       # negotiated per-VAR
      lightning_address: "varx@..."
      sources: ["counterpoint"]
```

### Onboarding side

`canary-identity` records `var_of_record` per merchant at connection time:

```sql
-- app.merchants table addition
ALTER TABLE app.merchants ADD COLUMN var_of_record UUID NULL;
ALTER TABLE app.merchants ADD COLUMN var_of_record_label TEXT NULL;  -- human label
```

Onboarding flow:
1. Sales / partner conversation establishes which VAR introduced this merchant
2. `POST /merchants` includes `var_of_record_label` field (e.g., `"rapidpos"`, `"ncr-direct"`)
3. `canary-identity` resolves label → `partner_id` from `revshare.channel_partners` config
4. Merchant created with `var_of_record` populated

### Rollup side

The period-end rollup query joins through merchant to channel partner:

```sql
WITH events AS (
    SELECT 
        e.merchant_id,
        m.var_of_record AS channel_partner_id,
        SUM(e.sat_cost) AS total_sats
    FROM metrics.cost_events e
    JOIN app.merchants m ON e.merchant_id = m.id
    WHERE e.occurred_at >= $1 
      AND e.occurred_at < $2
      AND e.source_code IN (
          SELECT unnest(sources) 
          FROM jsonb_array_elements_text(
              (SELECT revshare->'channel_partners'->m.var_of_record_label->'sources' 
               FROM app.current_cost_calibration)
          ) AS sources
      )
    GROUP BY e.merchant_id, m.var_of_record
)
```

This query is the architectural commitment that gets baked into `internal/cost/rollup.go` in the next refinement pass.

## NCR-direct adapter substrate

Same as RapidPOS — `canary-bull` cloud + `canary-edge` on-prem. The adapter is identical; the commercial attribution is the differentiator.

| Property | Value |
|---|---|
| Canary binaries | `canary-bull` (cloud, port `:8085`) + `canary-edge` (on-prem) |
| Inbound pattern | Polling client + edge-agent push |
| Authentication | API key per merchant (Counterpoint-issued, customer-held) |
| `SourceCode` | `counterpoint` (same as RapidPOS) |
| `var_of_record` | `ncr-direct` (or specific VAR) |
| Channel rev-share | Per VAR; defaults to 0 for direct-NCR-contract merchants |

## Tier mix

Identical to RapidPOS — Counterpoint is the same backend regardless of channel. See [[canary-go-rapidpos-crosswalk#tier-mix-for-counterpoint-via-rapidpos-merchants]].

## Cost-model worked example — NCR-direct merchant

Single-store NCR-direct Counterpoint merchant:

| Input | Value |
|---|---|
| Transactions / month | 12,000 |
| Active locations | 1 |
| POS sources | 1 (Counterpoint) |
| Agent decisions / day | 2,000 |
| Retention preference | 1 year |

Forecast:

```
Ingestion (Change-feed):  12K × 5 × 4   = 240K sats
Detection + cases:        12K × 720     = 8.6M sats
Storage:                  12K × 365 × 0.05 = 219K sats
Agent decisions:          2K × 7,500    = 15M sats
Multi-location:           1 × 50K       = 50K sats
Adapter overhead:         100K
Edge overhead:            200K
Anchor amortized:         20K
Platform floor:           200K
─────────────────────────────────────────────────
TOTAL:                    ~24.6M sats / month
                          ≈ $15 / month at $60K BTC
```

**Channel rev-share for this merchant:** 0 (NCR-direct, no VAR partner). All 24.6M sats accrue to Canary.

For comparison, the same merchant on a competitive seat-based platform with multi-store ops would land $200-400/mo. Single-store, the Counterpoint license + VAR support contract is typically $150-300/mo. Canary lands meaningfully cheaper while adding the AI / accountability rails layer.

## Why this refinement matters

Three reasons the multi-VAR model is non-negotiable:

1. **Commercial fairness.** A merchant onboarded by RapidPOS generates RapidPOS rev-share. A merchant onboarded direct generates none. A merchant onboarded by VAR-X generates VAR-X rev-share. The platform's rev-share architecture must accurately reflect the commercial reality, not the technical adapter.
2. **Regulatory cleanliness.** Once verifiable usage statements are anchored to L2, channel rev-share splits are part of the same verifiable record. A single-channel-per-source model would produce false rev-share attribution. The L2-anchored statement would be wrong; the moat would be compromised.
3. **VAR ecosystem expansion.** The architecture must support 5+ VAR partners on Counterpoint with different rev-share terms without code changes — only calibration. The `var_of_record` model handles N partners trivially; the source-code keying handles 1.

## Implementation status

| Component | Status |
|---|---|
| Source-code keyed rev-share (single VAR) | ✅ Specced in `satoshi-cost-rollup.md` Layer 4 |
| `var_of_record` field on `app.merchants` | ⚪ Refinement to add in cost-rollup SDD revision |
| Calibration YAML schema with `channel_partners` | ⚪ To be revised in next calibration version |
| Rollup query joining through merchant for channel attribution | ⚪ To be implemented in `internal/cost/rollup.go` |
| Multi-VAR onboarding flow in `canary-identity` | ⚪ To be added |

The refinement is bounded — it's a calibration-schema change, a single ALTER TABLE, and a rollup-query rewrite. None of it requires re-architecture; all of it is captured here as the canonical direction.

## Partner integration touchpoints

For NCR-direct or alternative-VAR partner conversations:

- **VAR partner registration** — define the partner's `partner_id`, rev-share, Lightning address. Add to `revshare.channel_partners`. No code change.
- **Merchant onboarding tagging** — sales captures which VAR introduced the merchant; `POST /merchants` includes `var_of_record_label`.
- **Per-VAR settlement reports** — `GET /revshare/channels?partner_id=&period=` returns per-period rev-share for one channel.
- **NCR-Voyix is not a partner** — do not pursue. They compete in the LP/analytics layer; integration access strategy routes through the customer.

## See also

- [[canary-go-rapidpos-crosswalk]] — companion crosswalk for the active VAR partner
- [[canary-go-cadence-ladder]] · [[canary-go-satoshi-cost-model]] · [[canary-go-endpoint-library]]
- [[channel-revshare-architecture]] — the rev-share primitive
- [[ncr-counterpoint-api-reference]] · [[ncr-counterpoint-connection-runbook]] — operational integration detail
- Memory: `project_ncr_voyix_is_competitor`, `project_bart_var_partnership`, `project_rapidpos_stakeholders`, `project_canary_rapidpos_primary_shift`
- SDD: `docs/sdds/go-handoff/bull.md` · `docs/sdds/go-handoff/satoshi-cost-rollup.md`

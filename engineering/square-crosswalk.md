---
tags: [canary, go, square, vendor-crosswalk, adapter, cadence, cost-model, hawk]
last-compiled: 2026-05-01
related: [canary-go-cadence-ladder, canary-go-endpoint-library, canary-go-satoshi-cost-model, canary-hawk]
---

# Canary Go ↔ Square — Vendor Crosswalk

> **Governing thesis.** Square is Canary's reference adapter target — webhook-native, ARTS-aligned semantics, no channel-partner overhead. The cadence ladder maps cleanly: webhooks land in Stream tier, OAuth + connection mutations live there too, and the bulk of Square's data flows through Change-feed and Reference tiers. **No channel rev-share applies** — Square is a direct-to-merchant relationship. The cost-model worked example for a typical Square SMB merchant lands ~$24-$36/month against Square's own ~$240/month seat baseline, plus Canary doesn't take a transaction-value percentage. The article is structured for partner integration teams and merchant-facing collateral.

This crosswalk is the cadence-ladder + cost-model lens on Square. Operational integration detail lives in [[growdirect-sales-square-opportunity]] and the canary-hawk SDD; this article is the partner-facing positioning document.

## Adapter substrate

| Property | Value |
|---|---|
| Canary binary | `canary-hawk` (port `:8082`) |
| Inbound pattern | Webhook receiver (Square pushes events to Canary) |
| Authentication | OAuth 2 with refresh-token rotation |
| Wire format | Square Order/Payment/Customer JSON → CRDM (ARTS POSLog) normalization |
| `SourceCode` value | `square` |
| Channel partner | None — direct merchant relationship |
| Edge agent required | No (cloud-native; Square is SaaS) |
| Bulk-import lifecycle | `POST /imports/items` for catalog drops (Square Catalog API export) |

Square's webhook model is the cleanest possible adapter target: the POS pushes events to Canary in real time over HTTPS with HMAC-SHA256 signature verification. No polling watermark, no edge agent, no on-prem deployment. The full cadence ladder is exercised by Square ingestion despite the model's simplicity.

## Tier mix for Square merchants

| Tier | Square traffic shape | Examples |
|---|---|---|
| **Stream** | Webhook events from Square | Order created, payment captured, refund issued, inventory adjusted |
| **Change-feed** | Cursor-paginated tail reads when ops need replay | `GET /transactions?cursor=&since=` after webhook outage |
| **Daily batch** | EOD reconciliation runs | `POST /reconciliation/run` — Canary count vs Square count |
| **Bulk window** | Catalog imports + period exports | Initial migration: full Square Catalog → Canary `item` master via `/imports/items` |
| **Reference** | Lookups + masters | Customer profile reads, item-master lookups, compliance state |

The dominant tier is **Stream** — Square's webhook stream is the heartbeat. Failure mode: heartbeat lost → alert pattern `heartbeat-lost` → recovery via replay queue from last-acked event ID.

## Cost-model worked example

Typical Square SMB merchant — single-store specialty retail with online presence:

| Input | Value |
|---|---|
| Transactions / month | 8,000 |
| Active locations | 1 |
| POS sources | 1 (Square only) |
| Agent decisions / day | 1,500 |
| Retention preference | 1 year |
| Compliance complexity | 1 |

Forecast (illustrative — calibrated values at deploy):

```
Ingestion + processing (Stream tier):    8K × 5 sats × 30 = 1.2M sats
Detection + cases:                       8K × 720 sats     = 5.76M sats
Storage:                                 8K × 365 × 0.05   = 146K sats
Agent decisions:                         1.5K × 7,500      = 11.25M sats
Multi-location:                          1 × 50K           = 50K sats
Adapter overhead:                        1 × 100K          = 100K sats
Anchor amortized:                        20K sats
Platform floor:                          200K sats
─────────────────────────────────────────────────────────────────────
TOTAL:                                   ~18.7M sats / month
                                         ≈ $11 / month at $60K BTC
                                         ≈ $7.50 / month at $40K BTC
```

Square baseline for same merchant:

| Component | Amount |
|---|---|
| Square Plus monthly fee | $79 |
| Per-transaction fee (~2.6% × $40 avg ticket × 8K txns) | $8,320 — but absorbed into transaction value |
| Effective software cost | $79/mo |

Canary delta: **~85% cheaper than Square Plus**, plus Canary doesn't take a percentage of transaction value. For an enterprise Square Plus at $165/mo, the gap widens further.

## Channel rev-share

**Zero.** Square is not a channel partner. Canary's relationship with Square merchants is direct.

In the rev-share configuration:

```yaml
revshare:
  channels:
    square:
      share: 0.0
```

The full satoshi accumulation flows to Canary; no per-period split.

## Square-specific adapter behavior

Three operational nuances worth knowing:

1. **OAuth refresh on the merchant's terms.** Square's OAuth tokens require refresh; canary-hawk handles this transparently but the merchant's `Disconnect` action revokes Canary's access immediately. The `DELETE /oauth/disconnect` endpoint is a clean off-ramp.
2. **Square Online channel attribution.** Square Online (formerly Weebly) is the same backend as in-store Square — a Square Online order is a `square` SourceCode event with a channel-distinguishing field in the metadata, not a separate adapter. Canary-hawk handles both.
3. **Webhook signature verification is strict.** Every webhook must verify the `X-Square-Signature` header. Failure returns 401 (not 400) — Square interprets repeated 401s as a key issue and pauses delivery. canary-gateway handles HMAC; canary-hawk handles Square-specific subscription state.

## What's documented

| Concern | Where |
|---|---|
| Adapter implementation | `docs/sdds/go-handoff/hawk.md` |
| Square OAuth contract | canary-hawk endpoint table (`/oauth/connect`, `/oauth/callback`) |
| Webhook receiver | canary-gateway (port 8080) `/webhooks/square` |
| CRDM normalization | `internal/crdm/transaction.go` Square mapping helpers |
| Cost model implications | This article + [[canary-go-satoshi-cost-model]] |
| Sales positioning | [[growdirect-sales-square-opportunity]] |
| Diagnostic forecast | `POST /usage/forecast` with `pos_sources: ["square"]` |

## Partner integration touchpoints

For Square-merchant integrations and migrations:

- **Direct OAuth onboarding** — merchant authorizes Canary via standard Square OAuth flow. No partner intermediary.
- **No co-sell motion** — Canary sells direct to Square merchants. Pricing is fully Canary's — no rev-share dilution.
- **No special channel pricing** — Square merchants get the same satoshi forecast as any other merchant on the same flow profile.

## See also

- [[canary-go-cadence-ladder]] — tier model
- [[canary-go-satoshi-cost-model]] — pricing mechanism
- [[canary-go-endpoint-library]] — endpoint surface
- [[growdirect-sales-square-opportunity]] — sales positioning context
- [[canary-rapidpos-crosswalk]] · [[canary-ncr-counterpoint-crosswalk]] — channel-bearing vendor crosswalks
- SDD: `docs/sdds/go-handoff/hawk.md`

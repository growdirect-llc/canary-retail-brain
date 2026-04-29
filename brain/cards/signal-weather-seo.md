---
card-type: signal-feed
card-id: signal-weather-seo
card-version: 1
domain: local-market
layer: local-market
feeds:
  - module-t
  - module-j
  - module-c
  - module-p
receives:
  - geography-hierarchy
tags: [signal, weather, seo, footfall, demand, zone, real-time, content]
status: approved
last-compiled: 2026-04-28
---

# Signal: Weather + Zone SEO

Weather is a dual-purpose signal: an operational feed that impacts footfall, cold-chain logistics, and shrink risk; and a content/search signal that shapes what consumers are searching for in the geography zone right now. Both surfaces are delivered by the local market agent.

## Purpose

Weather is the fastest-moving demand modifier available to a retailer. A cold snap shifts search intent from summer clearance to outerwear. A heat wave spikes beverage and fan demand. A storm reduces footfall and raises click-and-collect volume. The local market agent monitors weather at zone level and surfaces two distinct signals to two distinct consumers: the operational signal to Forecast and Transactions, and the content/SEO signal to Commercial.

## Signal

### Operational weather signal

| Component | Description | Frequency |
|-----------|-------------|-----------|
| **Current conditions** | Temperature, precipitation, wind by GEO_DISTRICT zone | Hourly |
| **Forecast window** | 7-day zone forecast | Daily refresh |
| **Footfall impact index** | Predicted footfall modifier for next 24h (rain, snow, extreme heat) | Daily, intraday on severe events |
| **Cold-chain alert** | Temperature threshold breach risk for perishables in transit or receiving | Event-triggered |

### Zone SEO signal

| Component | Description | Frequency |
|-----------|-------------|-----------|
| **Trending search terms** | Top rising queries in the geography zone related to retail categories | Daily |
| **Category search shift** | Delta in search volume by category vs 7-day average (e.g., +38% outerwear queries) | Daily |
| **Content opportunity flag** | Weather-driven content/promotion prompt for Commercial agent | Event-triggered on significant shift |

## Sources

- Weather API (zone-level, configurable provider per geography)
- Search trend API (Google Trends or equivalent, scoped to GEO_DISTRICT geography)

## Consumers

| Consumer | Signal | Action |
|----------|--------|--------|
| **Module T (Transaction Pipeline)** | Operational — footfall modifier | Adjusts expected transaction volume for the day; surfaces to store manager dashboard |
| **Module J (Forecast)** | Operational — 7-day forecast | Adjusts replenishment timing and safety stock for weather-sensitive categories |
| **Module C (Commercial)** | SEO — category search shift | Triggers content/promotion opportunity aligned to current search intent |
| **Module P (Pricing & Promotion)** | SEO — trending search terms | Surfaces high-demand SKUs for promotional consideration when search demand is rising |

## Invariants

- The SEO signal is a content opportunity flag, not a pricing instruction. Module P decides whether to act — the signal surfaces the opportunity.
- Cold-chain alerts are event-triggered, not scheduled. They must arrive at Module J and the VAR ops team within 30 minutes of threshold breach.
- Zone SEO scope is GEO_DISTRICT. Narrower scoping (per-store search trends) is not supported at SMB data volumes.

## Related

- [[local-market-agent]] — delivers this signal
- [[signal-seasonality]] — seasonality + weather interact; cold season onset is both a seasonal and weather event
- [[geography-hierarchy]] — zones map to GEO_DISTRICT nodes

---
card-type: signal-feed
card-id: signal-seasonality
card-version: 1
domain: local-market
layer: local-market
feeds:
  - module-j
  - module-p
  - module-c
receives:
  - geography-hierarchy
  - category-hierarchy
tags: [signal, seasonality, demand, calendar, forecast, pricing, promotion]
status: approved
last-compiled: 2026-04-28
---

# Signal: Seasonality

Seasonality is the demand calendar overlay that models predictable, recurring variation in consumer demand by category and geography. It is not real-time — it is a structured forward-looking curve that the Forecast, Pricing, and Commercial agents use to shape plans before the season arrives.

## Purpose

SMB retailers on Counterpoint operate without the demand planning infrastructure that tier-1 retailers take for granted. The seasonality signal gives the local market agent the ability to inject a calibrated demand curve into the Forecast and Pricing modules — holiday windows, back-to-school, weather-driven seasonal transitions, local event calendars. Without it, the Forecast module plans from historical transaction data alone and misses the forward signal.

## Signal

The seasonality signal is a structured calendar of demand multipliers and event windows:

| Component | Description | Granularity |
|-----------|-------------|-------------|
| **Demand multipliers** | Index (1.0 = baseline) by category and week | CAT_CATEGORY × GEO_DISTRICT × week |
| **Event windows** | Named periods (Holiday, Back-to-School, Harvest, etc.) with start/end dates | GEO_REGION × named event |
| **Transition windows** | Seasonal transition periods where category mix shifts (Summer → Fall) | CAT_DEPT × GEO_REGION × date range |
| **Local event overlays** | Non-national events: regional festivals, school schedules, sports seasons | GEO_DISTRICT × event name × date range |

Signal frequency: updated weekly by the local market agent. Major event windows are seeded 90 days forward; multipliers are revised as the window approaches.

## Sources

- National retail calendar (NRF, major holiday schedules)
- Regional school district calendars (local market agent scrapes or subscribes)
- Local event listings (Chamber of Commerce feed — see [[signal-community-intel]])
- Historical transaction patterns from Module T (used to calibrate multipliers for the geography)

## Consumers

| Consumer | Action |
|----------|--------|
| **Module J (Forecast & Order)** | Applies demand multipliers to forecast buckets; triggers early replenishment orders ahead of peak windows |
| **Module P (Pricing & Promotion)** | Schedules promotional windows aligned to seasonal peaks; suppresses discount promotions during high-demand periods |
| **Module C (Commercial)** | Commercial strategy adjusts OTB allocation by season; adjusts range emphasis |

## Invariants

- Seasonality multipliers are overlays, not overrides. Module J applies them to the base forecast; they do not replace the statistical model.
- Local event overlays are GEO_DISTRICT scoped. They are not propagated to other districts.
- The signal is forward-looking only. Historical seasonality patterns live in Module T's transaction history — the agent does not re-model the past.

## Related

- [[local-market-agent]] — the agent that sources and delivers this signal
- [[signal-weather-seo]] — weather is a related real-time signal that interacts with seasonal demand
- [[category-hierarchy]] — demand multipliers are applied at CAT_CATEGORY level
- [[geography-hierarchy]] — multipliers are scoped to GEO_DISTRICT or GEO_REGION

---
card-type: signal-feed
card-id: signal-community-intel
card-version: 1
domain: local-market
layer: local-market
feeds:
  - module-m
  - module-q
  - signal-seasonality
receives:
  - geography-hierarchy
tags: [signal, community, chamber-of-commerce, bbb, notice-board, local, intel, commercial]
status: approved
last-compiled: 2026-04-28
---

# Signal: Community Intelligence

Community intelligence aggregates public local business signals from Chamber of Commerce bulletins, BBB reports, community notice boards, and local business associations. It is a low-frequency, high-context feed that surfaces neighborhood-level changes that affect retail operations and commercial strategy.

## Purpose

The Chamber of Commerce knows when a new competitor is opening. The BBB tracks complaint patterns that indicate fraud or organized schemes targeting local businesses. Community notice boards flag events that drive footfall or block access. None of this data flows through traditional retail analytics. The local market agent monitors these sources and surfaces actionable intelligence to Commercial and LP — not as alerts, but as context updates that agents can factor into decisions.

## Signal Components

| Component | Source | Frequency | Consumer |
|-----------|--------|-----------|----------|
| **Chamber bulletins** | Local Chamber of Commerce newsletter/feed | Weekly | Module M (Merchandising) |
| **Competitor opening/closing** | Chamber membership changes, permit notices, local press | Event-triggered | Module M (Merchandising), Module O (Forecast) |
| **BBB complaint patterns** | BBB public complaint feed for the district | Weekly | Module Q (LP), Legal & Compliance |
| **Community notice board** | Local neighborhood platforms (Nextdoor, city boards) | Daily | Module Q (LP), footfall context |
| **Local event calendar** | Community events driving footfall or traffic impact | Weekly | [[signal-seasonality]] overlay, Module T |
| **Business association alerts** | BID (Business Improvement District) security bulletins | Event-triggered | Module Q (LP) |

## Routing

Community intelligence is context, not an alert stream. The local market agent delivers it as a weekly intelligence digest to the consuming agents, with event-triggered delivery only for high-priority items (competitor opening, BID security bulletin, BBB fraud pattern).

```
Community Sources (Chamber, BBB, boards, BID)
  → Local Market Agent (aggregation + triage)
    → Module M (Merchandising) [weekly digest + competitor events]
    → Module Q (LP) [BBB fraud patterns + BID security bulletins]
    → signal-seasonality [local event calendar overlay]
```

## BBB Complaint Patterns

BBB data is an LP input, not a commercial one. Complaint spikes for a specific product type or vendor can indicate a fencing network or fraud scheme targeting the district's retailers. The local market agent flags patterns (not individual complaints) to Module Q as background intelligence. No individual consumer PII from BBB complaints is ingested.

## Invariants

- Community intelligence is a digest feed. It does not trigger automated actions — it informs agent reasoning.
- Competitor intelligence (new openings, closures) is delivered to Module M as a context update. The Commercial agent decides whether it changes OTB, range, or promotional strategy.
- BBB data is used at the pattern level only. Individual complaint details are not stored.
- Community notice board monitoring is restricted to public boards. Closed neighborhood groups and private platforms are not monitored.

## Related

- [[local-market-agent]] — aggregates and delivers this signal
- [[signal-seasonality]] — local event calendar feeds into the seasonality overlay
- [[signal-property-landlord]] — related commercial intelligence; property signals complement community intel
- [[geography-hierarchy]] — scoped to GEO_DISTRICT

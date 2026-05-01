---
card-type: agent-profile
card-id: local-market-agent
card-version: 1
domain: local-market
layer: local-market
feeds:
  - module-q
  - module-o
  - module-m
  - module-p
  - fox-case-management
receives:
  - geography-hierarchy
  - signal-seasonality
  - signal-weather-seo
  - signal-social-threat
  - signal-civil-services
  - signal-community-intel
  - signal-property-landlord
tags: [agent, local-market, geography, intelligence, lp, orc, seasonality, weather]
status: approved
last-compiled: 2026-04-28
---

# Local Market Agent

The local market agent is the real-time external intelligence layer for a geography node. One agent is instantiated per GEO_REGION or GEO_DISTRICT. It monitors all external signal feeds for that geography and surfaces actionable intelligence to the domain module agents that need it.

## Purpose

Domain module agents (Q, J, C, P) operate on internal retailer data. They have no native awareness of what is happening in the external environment — weather shifts, organized retail crime on social platforms, civil unrest, seasonal demand curves, landlord bulletins. The local market agent fills that gap. It is not a PMO agent; it does not own a module or manage a delivery phase. It is a continuous intelligence feed anchored to a geography.

## Identity

| Attribute | Value |
|-----------|-------|
| **Layer** | Local market (below domain PMO, feeds up) |
| **Instantiation** | One per GEO_REGION or GEO_DISTRICT node |
| **Lifecycle** | Always-on once geography is onboarded; no SI gate |
| **Escalation target** | Module Q agent → Controller if LP-relevant; Module M agent for commercial signals |

## Signal Feeds

The local market agent aggregates six external signal feeds. Each feed is a separate card; the agent is the integration point.

| Feed | Card | Primary Consumer |
|------|------|-----------------|
| Seasonality | [[signal-seasonality]] | J (Forecast), P (Pricing) |
| Weather + Zone SEO | [[signal-weather-seo]] | T (Transaction), J (Forecast), commercial content |
| Social Threat Detection | [[signal-social-threat]] | Q (LP), Fox Case Management |
| Civil Services Liaison | [[signal-civil-services]] | Q (LP), Legal & Compliance |
| Community Intelligence | [[signal-community-intel]] | C (Commercial), Q (LP) |
| Property & Landlord | [[signal-property-landlord]] | A (Asset Mgmt), F (Finance), C (Commercial) |

## Context

The agent carries two contexts simultaneously:

**Geography context:** The Region or District this agent is anchored to. Population density, crime statistics, competitor footprint, seasonal patterns, weather zone, civil services jurisdiction, property landscape (mall, strip, standalone, anchor tenant).

**Retailer context:** The stores operating within this geography — their format, volume tier, LP profile, category range, and current incident history. This context is seeded from CRDM and updated from module Q alerts.

## Routing Principles

- LP signals (social threat, civil services) route to Module Q agent. The local market agent does not contact civil services directly — all external communication goes through the routing chain defined in [[signal-civil-services]].
- Commercial signals (seasonality, weather, community intel) route to Module M or Module P agent depending on whether the signal is about demand shift or promotional opportunity.
- Property signals route to Module A (Asset Management) for lease/TI tracking and Module F (Finance) for CAM cost impact.
- The local market agent does not surface raw feed data to the founder or VAR team. It surfaces processed signals with a recommended action and a consuming agent.

## Invariants

- One local market agent per geography node at GEO_REGION or GEO_DISTRICT level. Never per-store.
- The agent does not hold operational retailer data (transaction records, employee PII, case details). It holds geography-level intelligence only.
- All civil services communication is mediated by Legal & Compliance. The local market agent flags; it does not communicate.
- Social threat signals are leads, not confirmed cases. Fox Case Management receives them as flagged leads requiring human LP investigation.

## Related

- [[geography-hierarchy]] — the axis this agent is anchored to
- [[signal-social-threat]] — ORC, flash mob, eBay/marketplace resale monitoring
- [[signal-civil-services]] — LP liaison routing chain
- [[signal-property-landlord]] — mall security, TI, CAM signals

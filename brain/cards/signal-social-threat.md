---
card-type: signal-feed
card-id: signal-social-threat
card-version: 1
domain: lp
layer: local-market
feeds:
  - module-q
  - fox-case-management
receives:
  - geography-hierarchy
tags: [signal, lp, orc, flash-mob, social-media, ebay, organized-retail-crime, threat]
status: approved
last-compiled: 2026-04-28
---

# Signal: Social Threat Detection

Social threat detection monitors public social media and marketplace platforms for signals of organized retail crime (ORC), flash mob coordination, and stolen product resale in the district geography. All signals are leads — unverified intelligence delivered to LP for investigation, not confirmed cases.

## Purpose

Organized retail crime announces itself on social platforms before it executes. Flash mob events are coordinated on TikTok, Instagram, and closed messaging groups. Stolen product surfaces on eBay, Facebook Marketplace, and OfferUp within hours of a theft event. The local market agent monitors these surfaces continuously and delivers flagged leads to Module Q and Fox Case Management. Human LP investigators own the triage and any escalation beyond that.

## Signal

### Flash mob / coordination monitoring

| Component | Description |
|-----------|-------------|
| **Coordination signals** | Posts, stories, or DMs in public channels referencing store names, addresses, or retail ORC terminology in the district geography |
| **Velocity spike** | Sudden increase in geo-tagged social activity near a store location outside normal hours |
| **Known ORC terminology** | Slang terms, coded language, and hashtags associated with organized shoplifting coordination |

### Stolen product resale monitoring

| Component | Description |
|-----------|-------------|
| **SKU match** | Product listings on eBay, Facebook Marketplace, OfferUp matching in-stock SKUs at prices below cost |
| **Seller proximity** | Seller location signals within GEO_DISTRICT footprint |
| **Listing velocity** | Spike in listings of specific SKUs correlated temporally with store shrink events |
| **New-in-box, high-volume** | Sealed product listings in quantities inconsistent with individual ownership |

## Sources

- Social media monitoring API (public platform data only — no authenticated scraping)
- Marketplace listing APIs (eBay API, Facebook Marketplace scrape, OfferUp public feed)
- CRDM SKU inventory (to match listing products against in-stock items)

## Routing

```
Social/Marketplace Platforms
  → Local Market Agent (monitoring + pattern match)
    → Module Q (LP) [flagged lead with signal evidence]
      → Fox Case Management [lead opened as potential ORC case]
        → Human LP investigator [owns triage and investigation]
          → [[signal-civil-services]] routing chain [if case substantiated]
```

The local market agent never contacts civil services, stores personally identifiable information, or takes enforcement action. It surfaces patterns; humans decide what they mean.

## Invariants

- All signals delivered to Module Q are flagged leads, not confirmed cases. Fox Case Management opens them as leads requiring investigation before any action is taken.
- No PII from social platforms is stored by the local market agent. Pattern matching operates on public posts and listing metadata — not on user identities.
- Listing price vs. cost comparison requires Module P to provide current cost data. The agent does not cache cost data independently.
- Flash mob signals are time-sensitive. The agent must deliver a flash mob lead to Module Q within 15 minutes of detection during business hours.
- The agent does not post, reply, or engage on social platforms. It is read-only.

## Consumers

| Consumer | Action |
|----------|--------|
| **Module Q (Loss Prevention)** | Receives the flagged lead with signal type, evidence summary, and severity. Q agent decides whether to escalate to Fox or dismiss. |
| **Fox Case Management** | If Q agent escalates, Fox opens an ORC lead case with the social evidence attached via the Fox evidence chain. |

## Related

- [[local-market-agent]] — the agent that runs this monitoring
- [[signal-civil-services]] — the routing chain that activates if a Fox case is substantiated
- [[geography-hierarchy]] — signals are scoped to GEO_DISTRICT

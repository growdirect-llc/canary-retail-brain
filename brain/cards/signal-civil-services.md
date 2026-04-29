---
card-type: signal-feed
card-id: signal-civil-services
card-version: 1
domain: lp
layer: local-market
feeds:
  - module-q
  - legal-compliance-agent
receives:
  - geography-hierarchy
  - signal-social-threat
  - fox-case-management
tags: [signal, lp, civil-services, law-enforcement, police, routing, compliance, orc]
status: approved
last-compiled: 2026-04-28
---

# Signal: Civil Services

Civil services is the LP-to-law-enforcement communication channel. It is not a data feed into the platform — it is a governed outbound routing chain through which substantiated cases and incident reports reach civil authorities. Inbound civil services alerts (BOLO, warrant notifications, neighborhood advisories) flow back in as intelligence for Module Q.

## Purpose

Loss prevention at SMB scale rarely has a dedicated law enforcement liaison. The local market agent fills that gap — but with a critical constraint: no information about individuals, suspects, or unverified incidents reaches civil services without Legal & Compliance sign-off. The routing chain enforces this. The agent monitors; it does not communicate.

## Routing Chain

All civil services communication follows this chain without exception:

```
Local Market Agent (flags signal or receives inbound alert)
  → Module Q (Loss Prevention agent) [triage and decision]
    → Fox Case Management [case substantiation and evidence packaging]
      → Legal & Compliance Agent [liability review, communication approval]
        → Civil Services (law enforcement, transit police, city services)
```

No step can be bypassed. The Legal & Compliance agent is the communication authority — it owns what is sent, in what format, and to which jurisdiction.

## Signal Components

### Outbound (platform → civil services)

| Component | Trigger | L&C Gate |
|-----------|---------|----------|
| **Incident report** | Fox case reaches `referred_to_le` status | Yes — L&C reviews before filing |
| **CCTV evidence referral** | LP agent requests law enforcement review of footage | Yes — Fox evidence chain must be complete |
| **ORC pattern brief** | District-level ORC pattern substantiated across multiple Fox cases | Yes — anonymized, district-scoped |
| **Coordinated response request** | Flash mob threat confirmed; local police coordination needed | Yes — time-sensitive L&C fast-track |

### Inbound (civil services → platform)

| Component | Description | Consumer |
|-----------|-------------|----------|
| **BOLO (Be On Lookout)** | Law enforcement alert for known individuals operating in the district | Module Q — flagged intelligence, not stored PII |
| **Warrant notification** | Alert that a subject in an active Fox case has an outstanding warrant | Fox Case Management → Module Q |
| **Neighborhood advisory** | General district safety advisory from police (event, unrest, elevated risk) | Module Q, Local Market Agent for footfall context |

## Jurisdiction Scoping

Civil services routing is scoped to **GEO_DISTRICT**. Each district node in the geography hierarchy carries:
- Primary law enforcement jurisdiction (city police, county sheriff, transit authority)
- Non-emergency contact protocol
- Evidence submission format preference

The Legal & Compliance agent maintains jurisdiction records per GEO_DISTRICT. These are not stored in the platform DB — they live in the L&C agent's context and are referenced at communication time.

## Invariants

- No outbound communication reaches civil services without Legal & Compliance agent approval.
- No PII about suspects or persons of interest is transmitted to civil services unless the Fox case is at `referred_to_le` status with a complete evidence chain.
- Inbound BOLO and warrant data is treated as intelligence only — it is flagged to Module Q but not stored as a permanent record in the platform DB. The legal basis for storing law enforcement intelligence varies by jurisdiction; L&C governs this.
- The local market agent receives inbound civil services alerts and routes them — it does not act on them directly.

## Related

- [[signal-social-threat]] — the detection chain that often precedes a civil services referral
- [[local-market-agent]] — the agent anchored to this geography's civil services jurisdiction
- [[geography-hierarchy]] — routing scoped to GEO_DISTRICT

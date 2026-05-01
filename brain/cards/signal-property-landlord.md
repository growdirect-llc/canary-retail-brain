---
card-type: signal-feed
card-id: signal-property-landlord
card-version: 1
domain: local-market
layer: local-market
feeds:
  - module-a
  - module-f
  - module-m
  - module-q
receives:
  - geography-hierarchy
tags: [signal, property, landlord, mall, ti, cam, lease, security, tenant-improvements]
status: approved
last-compiled: 2026-04-28
---

# Signal: Property & Landlord

Property and landlord intelligence covers the relationship between the retailer and the physical property they occupy. For stores in malls, shopping centers, or landlord-managed properties, this signal surfaces shared security protocols, incident bulletins, tenant improvement (TI) allowance drawdown, CAM charge forecasts, and lease lifecycle events.

## Purpose

For SMB retailers in managed properties, the landlord relationship is a material operational and financial factor. Mall security has CCTV coverage, shared radio channels, and incident protocols that LP should be integrated with. TI allowances are negotiated cash on the table that drives capex decisions. CAM charges are a P&L line item that fluctuates and needs forecasting. None of this surfaces through POS data. The local market agent monitors the property relationship and routes signals to the modules that own the relevant decisions.

## Signal Components

### Security & Operations

| Component | Description | Consumer |
|-----------|-------------|----------|
| **Mall/property security** | Shared incident protocols, joint CCTV access agreements, shared radio channels | Module Q (LP) |
| **Property security bulletins** | Landlord-issued threat advisories, event notifications, access changes | Module Q (LP), Module O (Forecast — footfall impact) |
| **Anchor tenant events** | Major anchor tenant sales, closures, or events that drive or suppress footfall | Module O (Forecast), Module M (Merchandising) |

### Financial & Lease

| Component | Description | Consumer |
|-----------|-------------|----------|
| **TI allowance tracking** | Tenant improvement allowance negotiated in lease — drawdown milestones, remaining balance, expiry date | Module A (Asset Management), Module F (Finance) |
| **CAM charge forecast** | Common area maintenance charge projections and actuals vs. lease estimate | Module F (Finance), Module M (Merchandising) |
| **Lease renewal window** | Notification when lease renewal decision window opens (typically 6–12 months before expiry) | Module F (Finance), Legal & Compliance |
| **Lease escalation triggers** | CPI or fixed-rate rent escalation events per lease terms | Module F (Finance) |

## Routing

```
Property/Landlord Sources (property mgmt portal, lease documents, bulletin feeds)
  → Local Market Agent (monitoring + classification)
    → Module Q [security + incident bulletins]
    → Module A (Asset Management) [TI drawdown, lease lifecycle]
    → Module F (Finance) [CAM actuals, escalation triggers, lease renewal]
    → Module M (Merchandising) [anchor tenant events, footfall context]
```

## Ownership Boundary

The local market agent surfaces the external property signals. The domain modules own the internal accounting and decision treatment:

| Domain | Owns |
|--------|------|
| **Module A** | TI allowance asset accounting, lease schedule |
| **Module F** | CAM expense forecasting, P&L treatment |
| **Legal & Compliance** | Lease terms, renewal authority, CAM dispute review |
| **Module Q** | LP integration with property security — shared protocols, joint response |

The local market agent does not store lease documents, CAM invoices, or TI agreements. It surfaces milestones and events from these sources; the documents themselves are in the ops team's document management system.

## Invariants

- Mall/property security integration is LP-to-property-security only. It does not give the property access to Canary data. Information flow is inbound (bulletins) and coordinated outbound (incident notification under LP protocols).
- TI allowance data is financial — it flows to Module A and F only. It is not a commercial signal.
- CAM charges are actuals + forecast only. Disputes go through Legal & Compliance — the platform does not auto-dispute.
- Lease renewal window notifications are informational — they prompt the ops team to engage the VAR account manager. The platform does not negotiate leases.

## Related

- [[local-market-agent]] — delivers this signal
- [[signal-civil-services]] — mall security and civil services are distinct channels; both route through LP but must not be conflated
- [[signal-community-intel]] — community intel and property intel together cover the external commercial landscape for the geography
- [[geography-hierarchy]] — scoped to GEO_STORE (per-property) within GEO_DISTRICT

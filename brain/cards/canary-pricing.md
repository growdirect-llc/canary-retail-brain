---
card-type: domain-module
card-id: canary-pricing
card-version: 1
domain: merchandising
layer: domain
feeds:
  - canary-analytics
receives:
  - canary-identity
  - canary-item
  - canary-inventory
tags: [pricing, price-rules, promotions, markdowns, effective-price, stacking, audit-trail]
milestone: M4
status: approved
last-compiled: 2026-04-30
---

# Canary Service: pricing

## What this is

Rule-side store for pricing — price rules, promotional campaigns, markdown lifecycles, and historical price audit. **Does not execute basket calculation** (that's the POS today; Phase 4 of the long arc adds Canary's basket engine).

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:8094` |
| Axis | B — Resource APIs |
| Tier mix | Reference (effective-price resolver, single-rule reads) · Change-feed (filtered lists) · Stream (mutations, state transitions) · Bulk window (rule + campaign imports) |
| Owned tables | `app.price_rules`, `app.promotions`, `app.promotion_rules`, `app.markdowns`, `app.markdown_approvals`, `app.price_history` |
| Effective-price precedence | markdown > promotion > rule > base price |
| Markdown lifecycle | `PROPOSED → APPROVED → SCHEDULED → APPLIED → EXPIRED` |

## Purpose

Pricing rule store with effective-price resolver and explicit promotion stacking semantics. Stacking resolved server-side with `applied_rules[]` audit trail returned to caller — partners building margin-attribution analytics can trace every applied discount back to its source rule.

## Dependencies

- canary-identity, canary-item (base prices)
- canary-inventory (low-velocity markdown triggers)

## Consumers

- POS adapters (effective-price calls during basket build)
- canary-analytics (publishes effective-price changes for downstream metric attribution)
- BI tools (margin attribution)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-pricing
- Cards: [[tier-reference]], [[tier-change-feed]], [[tier-stream]], [[tier-bulk-window]]

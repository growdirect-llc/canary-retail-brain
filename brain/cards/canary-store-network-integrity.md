---
card-type: domain-module
card-id: canary-store-network-integrity
card-version: 1
domain: lp
layer: domain
feeds:
  - canary-fox
  - canary-alert
receives:
  - canary-identity
  - canary-tsp
  - canary-bull
  - canary-transfer
tags: [store-network-integrity, cross-location, anomaly-detection, collusion, pattern-correlation, multi-store]
status: approved
last-compiled: 2026-04-30
---

# Canary Service: store-network-integrity (SNI)

## What this is

Multi-store correlation and cross-location anomaly detection. Where canary-chirp evaluates rules within a single location's transaction stream, SNI correlates patterns across locations — collusion rings, transfer-loss conspiracies, schedule-coordinated shrink, regional fraud campaigns. Pairs with canary-bull for transfer-side intelligence and canary-fox for case escalation.

## Tier mix and axis

| Property | Value |
|---|---|
| Port | `:9088` |
| Axis | B — Resource APIs |
| Tier mix | Change-feed (anomaly tail) · Reference (single-anomaly reads, correlation graph) · Stream (escalate / dismiss) · Daily batch (correlation evaluator — windows of hours-to-days) |
| Owned tables | `app.network_anomalies`, `app.network_correlations`, `app.network_pattern_classes` |
| Anomaly schema | severity · pattern_class · locations[] (with role: source/destination/peripheral) · subjects[] · evidence[] · confidence · detected_at · correlation_window |

## Purpose

Cross-location correlation as a first-class capability. Cross-merchant detection is an explicit super-admin operation requiring documented authorization (strict merchant scoping by default). The daily-batch tier on the correlation evaluator matches the natural cadence of multi-day pattern emergence — stream-tier correlation would over-fit on noise.

## Dependencies

- canary-identity, canary-tsp (transaction context)
- canary-bull (transfer-side signals)
- canary-transfer (variance events)
- canary-alert (escalation routing)
- canary-fox (case opening on confirmed pattern)

## Consumers

- canary-fox (case subjects with location-graph + subject-graph evidence)
- canary-alert (alerts for emerging patterns)
- LP investigators (forensic review)

## See also

- SDD: `docs/sdds/go-handoff/microservice-architecture.md` §canary-store-network-integrity
- Cards: [[tier-change-feed]], [[tier-reference]], [[tier-stream]], [[tier-daily-batch]]

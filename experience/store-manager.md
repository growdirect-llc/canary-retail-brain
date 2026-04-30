---
title: The Store Manager
classification: confidential
---

# The store manager

## Your day

Open the store. Manage the shift. Respond to receiving, customer issues, planogram changes, occasional LP escalation. Close the store.

## What the platform does for you

Continuous monitoring of every operational signal — receiving variance, planogram compliance, register exception patterns, device anomalies. Real-time alerts on what needs your attention. Automated handling of what does not.

## Where you step in

| Decision | Trigger | What you do |
|---|---|---|
| Receiving disposition | Damaged or short shipment at the dock | Confirm reason code; matrix decides; vendor disposition triggered automatically |
| Reset execution | Scheduled planogram reset | Execute per brief; capture before/after; compliance scored automatically |
| Skimmer / rogue device investigation | Operations Agent alert (real-time) | Physical inspection; decide whether to escalate to LP |
| Customer escalation | Service issue beyond cashier authority | Personal involvement; refund authorization above cashier limit |
| Schedule exception | Late arrival, no-show, swap request | Approve / deny; agent records adherence event |
| Cash drawer over/short above tolerance | End-of-shift reconciliation | Investigate; sign off on adjustment |

## What the platform never asks of you

- Reconciling tills manually — sales audit closes the day automatically.
- Filing receiving discrepancy paperwork — the chain handles attribution and the vendor disposition matrix routes the response.
- Chasing a vendor about a missed delivery — the carrier scorecard handles attribution.
- Calculating shrink rate manually — Operations Agent surfaces it continuously.
- Manually checking which planogram is current — the planogram service is the source of truth; reset compliance is scored against it.
- Building an LP case binder for a suspected pattern — the chain IS the binder.

## What's on your dashboard

| Tile | What it shows |
|---|---|
| **Today's exceptions** | Receiving variance, register exception patterns, device anomalies — ranked by severity |
| **Schedule status** | Adherence rate, no-shows, late arrivals; remaining shifts |
| **Receiving queue** | Inbound shipments today; ETA; ASN match status |
| **Reset calendar** | Upcoming planograms with execution dates and labor estimate |
| **Cash drawer status** | Each register's over/short trajectory; cashiers approaching threshold |
| **LP signals** | Detection alerts your store has triggered; cases under investigation |

## What changes for the store experience

The platform becomes operational backstop, not an additional system to manage. The signals that would have lived in someone's memory or been missed entirely now surface as alerts. The decisions that need a human still need a human — Canary doesn't make discretionary calls. But the work between the alert and the decision shrinks dramatically.

A receiving discrepancy used to mean: count, recount, fill out a form, file it, hope the vendor responds. Now it means: confirm the reason code on the dock app, the disposition matrix routes, the vendor scorecard records, the chargeback (if applicable) computes automatically.

A skimmer-pattern alert used to mean: nothing, because no one was looking. Now it means: alert pings, you walk to the register, you make a judgment call, you escalate if warranted, the chain records the investigation.

## Related

- [The merchant](merchant) — your reporting line, who consumes the strategic rollup of your store's operations
- [The LP investigator](lp-investigator) — who you escalate to on LP cases
- [Modules](../modules/modules) — the operational machinery behind your dashboard

---
title: Experience by Role
classification: confidential
---

# Experience by role

What it actually looks like to use Canary, by who you are.

The platform abstracts to "agents run the loops, merchants run the store" — but that compresses into different daily reality depending on the role. The pages below describe the day from inside.

| Role | What you see | Where you step in |
|---|---|---|
| [The merchant](merchant) | Strategic dashboard, OTB wallet, exception queue | Annual planning, signing on financial deviations, customer-facing work |
| [The store manager](store-manager) | Operational signals, alert queue, planogram compliance | Receiving disposition, reset execution, escalations |
| [The LP investigator](lp-investigator) | Detection alerts, case queue, evidence chain | Case triage, investigation judgment, civil-services referrals via L&C |
| [The vendor](vendor) | Scorecard, contract terms, pending credits | Compliance, contract dispute resolution |
| [The external party](external-party) | Verification surfaces — auditor, regulator, lender, insurer | Verifiable claim checking via `verify_chain` and read-only APIs |

## What's the same across all roles

- **The platform handles the operational machinery.** Every role sees signals that need attention, not data they have to assemble.
- **Decisions are the human's job.** Triage, judgment, signing authority, customer-facing work — these stay human. Routine operations stay agent.
- **The audit trail is universal.** Every action by any actor — human or agent — produces a hash-chained record. Everyone is accountable; no one is exempt.

## What's different by role

The merchant sees a strategic dashboard and the financial wallets. The store manager sees the operational signals for their store. The LP investigator sees cases. The vendor sees their own scorecard. The external party sees verification surfaces.

None of these are dumbed-down views of the same data. They are different projections of the same underlying chain — each role gets the surface they need, scoped by their authentication context. A store manager cannot see another store's transactions. A vendor cannot see another vendor's scorecard. An auditor sees only what the merchant has explicitly granted access to.

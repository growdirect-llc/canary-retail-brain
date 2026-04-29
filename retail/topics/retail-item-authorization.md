---
card-type: domain-module
card-id: retail-item-authorization
card-version: 1
domain: cross-cutting
layer: cross-cutting
status: approved
agent: ALX
feeds: [retail-replenishment-model, retail-assortment-management]
receives: [retail-assortment-management, retail-site-management, retail-space-range-management, retail-merchandise-hierarchy, retail-vendor-lifecycle]
tags: [item-authorization, salability, blue-laws, age-restriction, recall, listing, planogram, regulatory, POS-gate, item-eligibility, operational-block]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

The unified item authorization model: the convergence of item master eligibility, site-level regulatory restrictions, planogram listing state, and operational blocks into a single salability gate — the definitive answer to "is this item authorized for sale at this store right now, and why or why not?"

## Purpose

This is the gap Retek never closed. Item status lived in the item master. Regulatory restrictions lived in the site master — when they were maintained at all. Planogram listing state lived in the space planning system, loosely synchronized on a batch cycle. Operational blocks (recall, LP hold, merchant clearance-only designation, legal hold) lived in POS parameter files, spreadsheet emails to the POS team, and, frequently, nowhere recoverable at all. The POS became the de facto convergence point — it had to carry local copies of all these dimensions in its own parameter database — with all the synchronization failure modes that implies. An item cleared for recall in the item master might remain saleable at POS for days. An age-restricted item might sell freely at a store in a jurisdiction where local ordinance requires electronic ID verification. A planogram reset might remove an item from the shelf while the listing system still authorizes replenishment.

Item authorization exists as a distinct model because no other module owns the convergence. Each upstream system owns one dimension. No upstream system owns the synthesized answer. Without a unified authorization model, the POS is the system of record by default — and that is the worst possible place for it to be.

## Structure

Item authorization has four dimensions. All four must resolve to "authorized" for a transaction to proceed. A block on any single dimension produces a salability denial, with a reason code indicating which dimension blocked and why.

**Dimension 1 — Item eligibility**

Item-level flags maintained in the item master that govern universal eligibility regardless of site:

- *Active status* — item must be in Active status; Discontinued Sale and Hold block sales at POS
- *Recall flag* — issued by the merchant, compliance, or legal team; immediately blocks sale at all sites regardless of physical inventory status
- *Age-restricted* — item requires electronic age verification at POS; classification code (tobacco, alcohol, lottery, firearms, adult content) determines which verification protocol applies
- *Hazardous* — governs transport and disposal restrictions; may restrict sale in certain channels
- *WIC / EBT eligible* — governs tender type restrictions; these are eligibility flags, not blocks, but they constrain transaction types

Item eligibility is binary and site-agnostic. An item under recall is blocked at every store simultaneously, not routed through store-by-store updates.

**Dimension 2 — Site regulatory zone**

Site-level configuration that overlays item eligibility with jurisdiction-specific restrictions. The regulatory zone is a property of the site, not the item. One item may be fully authorized at Store A and restricted at Store B because of their respective regulatory zones.

- *Blue laws* — Sunday sale restrictions on specific merchandise categories (most commonly alcohol); the site's jurisdictional blue law calendar specifies which categories are restricted on which days and hours
- *Hours restrictions* — sale of specific item classes (alcohol, lottery) prohibited before or after defined local hours regardless of store operating hours
- *Age verification ordinance* — state and local variation on minimum purchase age (tobacco: 21 federal, but some states differ) and required verification method (visual check vs. electronic scan vs. facial estimation)
- *Controlled substance scheduling* — state-level scheduling for OTC pharmaceuticals, CBD products, and other regulated substances varies materially across jurisdictions; the site's state determines which items in these categories are restricted or require pharmacist-adjacent protocols
- *Local prohibition* — municipality-level restrictions on specific merchandise categories (fireworks, certain beverages, specific chemicals) that override chain-level assortment decisions

Regulatory zone data must be maintained in the site master and kept current. Regulatory change (e.g., federal minimum tobacco age increase) requires a systematic sweep of the site regulatory configuration, not store-by-store updates. The regulatory zone is the configuration layer that localizes a national assortment to a specific legal environment.

**Dimension 3 — Planogram listing state**

An item is authorized for sale only at stores where it is listed on an active planogram. This is the assortment management control: the planogram defines the physical range, and the listing state is the system's representation of that range.

- *Listed* — item appears on an active planogram assigned to this store; sale authorized from this dimension
- *Not listed* — item has no planogram assignment at this store; sale blocked; this is the intended behavior for items not stocked at a specific format or cluster
- *De-listed, stock remaining* — item removed from planogram but clearance stock exists; sale authorized under clearance protocol only; replenishment blocked
- *Planogram in transition* — reset in progress; authorization state during a reset window requires explicit handling; a reset that removes items from the planogram must coordinate with POS authorization to avoid selling items that are no longer physically present on the shelf

The listing state dimension is what prevents phantom replenishment and ensures that the POS and the replenishment system agree on what is stocked at a given location. It is also the mechanism by which a range decision (remove item from small-format stores) propagates to actual sale restriction at those stores.

**Dimension 4 — Operational blocks**

Explicit blocks placed by authorized operational teams, each with a defined scope, reason code, and expiry protocol:

- *Loss prevention hold* — LP team blocks an item at one or more sites due to fraud pattern, theft concentration, or investigation; block is site-scoped, not chain-wide; typically time-bounded pending investigation outcome
- *Merchant block* — buyer places a block on a specific item or item group; use cases include: clearance-only designation (allow sale but block reorder), seasonal end-of-run (block new receipts and new sales), or temporary withdrawal pending a supply chain problem
- *Recall (operational)* — distinct from the item eligibility recall flag in Dimension 1; this is the operational process by which a supplier recall notice is translated into a system block; the Dimension 1 flag is the outcome; the operational block workflow is how it gets there
- *Store operations block* — store-level block placed by store management for local reasons (damaged display, local health code issue, in-store event conflict); narrowest scope, shortest expected duration

Each operational block must carry: the blocking authority (team + individual), the block scope (chain / region / site / site group), the reason code, the creation timestamp, and an expiry protocol (explicit date, event-based release, or manual review). Blocks without expiry protocols become orphaned and invisible.

## The convergence failure

The traditional Retek implementation kept all four dimensions in separate systems with no unified query surface. The consequences were predictable:

- Recalled items remained saleable at POS until the POS team processed a manual parameter update — sometimes 24–48 hours after the recall was issued in the item master
- Age-restricted items sold without verification at sites where the site master's regulatory zone data was stale or misconfigured
- Items removed from planograms continued generating replenishment orders because the listing system was not updated in the same transaction as the planogram change
- Operational blocks issued by LP or compliance lived in email threads and were manually translated into POS parameter files by a separate team — with transcription error rate commensurate with the manual process
- No one could answer "what items are currently blocked at Site X and why" without querying four systems and reconciling the results

The POS parameter file was the practical system of record because it was the enforcement point. Every authorization dimension had to be translated into a POS parameter update before it took effect. That translation step was where recalls were delayed, blue law schedules were misconfigured, and operational blocks were lost.

## Consumers

The POS system is the primary enforcement consumer: authorization state must be available at the point of transaction, with reason codes for customer-facing messaging when a sale is denied. The Replenishment module consumes listing state from Dimension 3 — it should not be possible to generate a replenishment order for an item that is not listed at a site. The Operations Agent monitors authorization state changes and their propagation to POS — specifically the latency between a block being issued and it taking effect at the point of sale. The Merchant dashboard consumes the authorization profile for assortment health monitoring: items blocked for >N days, items with stale regulatory zone configurations, items whose listing state and replenishment state disagree.

## Invariants

- A recall block must propagate to POS authorization within a defined SLA. The current state of an item's recall flag must not require a manual POS update step — it must cascade automatically to all affected sites.
- Regulatory zone configuration must be maintained at the site level, not the item level. An item is not "a blue-law item." A site is "in a blue-law jurisdiction." The distinction matters: updating an item's regulatory classification requires touching every item in the affected category; updating a site's jurisdictional profile touches one record and applies to all items automatically.
- Planogram changes and listing state changes must be transactionally coupled. A planogram reset that changes the item set must update listing state in the same event, not in a subsequent batch job.
- Operational blocks must carry an expiry protocol at creation. A block with no expiry is a permanent restriction that will not be reviewed until it causes a problem.

## Platform (2030)

**Agent mandate:** Technical Agent owns authorization state management — it is the system that receives upstream events (planogram publication, item status change, recall issuance, regulatory zone update) and propagates them to the authorization record in real time. Operations Agent monitors authorization latency (time from block issuance to POS enforcement), stale regulatory zone configurations, and listing-replenishment disagreements as continuous signals. Business Agent receives authorization exception escalations — items blocked for extended periods without resolution, regulatory zone conflicts that require merchant-level decisions.

**`item_authorized` as a single-call contract state query.** In the Canary Go model, authorization is not a POS parameter file. It is a contract state query. `item_authorized(item_id, site_id)` evaluates all four dimensions against current state — item eligibility from the item master contract, regulatory zone from the site configuration, listing state from the planogram event log, operational blocks from the active block registry — and returns a boolean plus a structured reason if denied. The POS does not carry local copies of these dimensions. It calls the authorization surface at transaction time and enforces the result. This eliminates the "POS parameter update lag" failure mode entirely: there is no parameter file to update. The authorization state is live.

**Recall propagation as a contract event.** When a recall block is issued — by the merchant, by a supplier notification, or by a regulatory authority — it is a contract event on the item master. Technical Agent receives the event and immediately updates the authorization record across all affected site contracts. The recall is effective the moment the event is confirmed. The latency between "recall issued" and "item blocked at POS" is the contract event propagation time, not the POS parameter update cycle time. For smart-contract-native items, the supplier can issue a recall notification as a signed contract event — cryptographically attributable, timestamped on-chain, and automatically propagated to all retailer site authorizations without requiring a manual supplier communication workflow.

**Regulatory zone as site configuration, not item configuration.** The site configuration contract holds the complete regulatory zone profile: blue law schedule by day and hour, age verification requirements by item classification, controlled substance scheduling by state, and any local prohibitions. When a regulatory change occurs (federal minimum age increase, state scheduling change), Technical Agent updates the affected site configurations in bulk. Every item authorization query for those sites immediately reflects the updated regulatory zone — no item-by-item update required. The site regulatory profile is the single point of truth for jurisdictional compliance; it does not live in the item master and does not require per-item maintenance.

**Operations Agent: authorization health as a continuous signal.** Traditional authorization management is reactive: a recalled item sells, someone notices, an investigation follows. Operations Agent monitors authorization state proactively. Key signals: (1) items with active blocks where no expiry protocol is set — orphaned blocks that will never be reviewed; (2) items listed at a site but with authorization disagreement between the listing dimension and any other dimension — the item is listed but blocked, meaning replenishment is running for an item that cannot be sold; (3) sites with regulatory zone configurations that have not been reviewed since the last relevant regulatory change in their jurisdiction; (4) authorization latency metric — time from upstream event (recall issued, planogram published, status changed) to authorization state updated, monitored per event type.

**MCP surface.** `item_authorized(item_id, site_id)` returns authorization status (boolean), denial reason code and dimension if denied, and the timestamp of the last state evaluation. `authorization_blocks(item_id)` returns all active blocks across all four dimensions with scope, reason code, blocking authority, and expiry protocol. `site_authorization_profile(site_id)` returns the complete regulatory zone configuration: blue law schedule, age verification requirements by item classification code, and active ordinances. `authorization_changes(site_id, period)` returns items whose authorization state changed in the window with the dimension that changed and the triggering event — the change log that POS systems can pull to refresh their local cache rather than querying every item on every transaction. `authorization_conflicts(site_id)` returns items with inconsistent state across dimensions — listed but blocked, authorized but de-listed, recalled at item level but not propagated to site-level block — the exception queue for Technical Agent remediation.

**RaaS.** Authorization state changes — recall issued, block placed or lifted, regulatory zone updated, listing changed — are sequenced events. The authorization state at the time of any POS transaction must be reconstructible from the event log: a recall issued at 2pm must block transactions after 2pm; transactions before 2pm were authorized. This is the evidentiary basis for any dispute about whether an item should have been sold. `item_authorized(item_id, site_id)` from Valkey hot cache (sub-20ms; called at POS transaction time — high call volume at scale). `authorization_changes(site_id, period)` is a SQL delta feed, not a full recompute, enabling POS systems to refresh their local cache incrementally rather than pulling full state. Authorization event log in SQL append-only, indexed on (site_id, event_type, event_timestamp) for ad hoc LP investigation queries. Authorization history exportable for regulatory audit, LP investigation, and POS reconciliation.

## Related

- [[retail-assortment-management]] — item lifecycle status (Dimension 1) and listing state (Dimension 3) originate here
- [[retail-site-management]] — site regulatory zone configuration (Dimension 2) is maintained in the site master
- [[retail-space-range-management]] — planogram publication events trigger listing state changes that update Dimension 3
- [[retail-merchandise-hierarchy]] — item classification codes (age-restriction type, controlled substance class) are hierarchy-level properties that feed regulatory zone mapping
- [[retail-vendor-lifecycle]] — supplier recall notifications are a vendor event that triggers Dimension 1 and Dimension 4 updates simultaneously
- [[retail-replenishment-model]] — listing state from Dimension 3 gates replenishment order generation; authorization conflicts surface as replenishment exceptions

---
title: C — Functional Decomp
classification: internal
type: wiki
sub-type: module-functional-decomposition
date: 2026-04-26
last-compiled: 2026-04-26
status: draft v1 (archetype — no real customer engagement)
module: C
solution-map-cell: ◐ Derived — no dedicated Counterpoint B2B endpoint family; derived from AR_CUST tier/credit fields, AR_CUST_CTL multi-tier flags, Customer_OpenItems AR aging, and behavioral pattern from T
companion-modules: [C, F, T, Q]
companion-substrate: [ncr-counterpoint-api-reference.md, ncr-counterpoint-endpoint-spine-map.md]
companion-context: [garden-center-operating-reality.md]
companion-canary-spec: Canary-Retail-Brain/modules/M-merchandising.md
companion-canary-crosswalk: Brain/wiki/canary-module-m-merchandising.md
companion-catz: CATz/proof-cases/specialty-smb-counterpoint-solution-map.md
methodology-note: "Sister card to d, a, p functional-decomp cards. First fully-derived module in this batch — C has no own Counterpoint endpoints; all L2s read from R + F substrate or derive classification from AR fields. The garden-center landscaper / wholesale / project-tier reality is the primary vertical lens shaping the B2B classification design."
---

# Module M (Merchandising) — Functional Decomposition

> **Artifact layer.** Third of three Canary module artifact layers:
> 1. **Canonical spec** (vendor-neutral) — `Canary-Retail-Brain/modules/M-merchandising.md`
> 2. **Code/schema crosswalk** (Canary-specific) — `Brain/wiki/canary-module-m-merchandising.md`
> 3. **Functional decomposition** (Counterpoint-substrate-aware, L2/L3 + user stories) — *this card*

## Governing thesis

C is the **B2B intelligence layer** of the Canary spine — the surface that distinguishes wholesale accounts, landscaper clients, and project-tier buyers from casual retail consumers. Against the Counterpoint substrate, C has no dedicated endpoint family of its own. Everything C knows about a commercial customer is derived from AR fields that Counterpoint already surfaces through the Customer and Customer_OpenItems endpoints: account category codes (`AR_CUST.CATEG_COD`), credit terms (`AR_CUST.NO_CR_LIM`, `CR_RATE`, `BAL`), multi-tier control flags (`AR_CUST_CTL`), and outstanding AR balances (`Customer_OpenItems`). C reads these from R's substrate publications and builds B2B classification on top of them.

The opportunity is real: at a garden center, 20-40% of gross revenue typically comes from commercial accounts (landscapers buying for projects, nurseries reselling wholesale, municipality contracts). These accounts operate on different credit terms, purchase at different price tiers, and carry different risk profiles than retail walk-in traffic. Counterpoint stores all of this — but doesn't surface it as a distinct B2B-intelligence layer. Canary does.

The derived-module shape is the load-bearing design constraint. C cannot fire without R (customer master) and F (AR ledger) being in place. This ordering is a build-sequence constraint, not just a data dependency: C is the Module 4 in the Canary v2 ring, behind R (Module 2) and F (Module 3). The L2 split below reflects this dependency chain explicitly.

## Executive summary

| Dimension | Count | Source |
|---|---|---|
| L2 process areas | 5 | This card |
| L3 functional processes | 26 | This card |
| Counterpoint endpoints in C's path | 0 dedicated; inherits from R's `AR_CUST`, `AR_CUST_CTL`, `Customer_OpenItems` | API reference |
| Counterpoint-substrate L2 areas | 0 own; C reads R + F publications | Solution Map cell |
| Canary-native L2 areas | 3 (M.1 B2B classification, M.2 credit posture, M.4 B2B Q rules) | CATz proof case |
| Derived L2 areas | 2 (M.3 AR ledger surface cross-cut with F.6, M.5 substrate contracts) | F module dependency |
| Substrate contracts C owes downstream | 6 | This card §M.5 |
| Assumptions requiring real-customer validation | 8 | Tagged `ASSUMPTION-C-NN` |
| User stories enumerated | 32 | Observer + analyst mix; cast in §Operating notes |

**Posture:** first fully-derived module in this decomposition pass. C contributes no own Counterpoint polling; all substrate comes from R and F. The B2B classification and credit-posture L2s are Canary-native intelligence built on top of R's customer substrate and F's AR ledger. Garden-center vertical context — landscaper tiers, project-PO billing, municipality accounts — shapes every L2.

## Counterpoint Endpoint Substrate

| Counterpoint Endpoint | CRDM Entity | L2 Process Area |
|---|---|---|
| AR_CUST | Customer master | M.1 (Classification), M.5 (Credit posture) |
| Customer_OpenItems | Open AR items | M.2 (Payment velocity), M.3 (AR aging) |
| AR_CUST_CTL | Credit control | M.1 (Tier derivation), M.5 (Credit limit) |
| PS_DOC_HDR / PS_DOC_LIN | Transaction history | M.2 (Behavioral pattern routing) |

## L1 → L2 → L3 framework

```
L1 (Solution Map cell)         C = ◐ Derived
                                 │  (no own Counterpoint endpoints;
                                 │   derived from R's AR_CUST/AR_CUST_CTL substrate
                                 │   + F's AR ledger + T's behavioral pattern)
                                 │
L2 (Process areas)               ├── M.1  B2B classification derivation    ★ Canary-native (from R)
                                 ├── M.2  Per-customer credit posture       ★ Canary-native (from R + F)
                                 ├── M.3  AR ledger surface                 ◐ Derived (cross-cut F.6)
                                 ├── M.4  B2B-specific detection rules      ★ Canary-native (cross-cut Q)
                                 └── M.5  Cross-module substrate contracts
                                 │
L3 (Functional processes)       (26 — enumerated per L2 below)
                                 │
L4 (Implementation detail)      Canary-Retail-Brain/modules/M-merchandising.md
                                  + canary-module-m-merchandising.md (schema crosswalk)
                                  + future Canary/docs/sdds/v2/commercial.md
```

## M.1 — B2B classification derivation

**Coverage posture.** ★ Canary-native, built from R's substrate. Counterpoint stores account categorization in `AR_CUST.CATEG_COD` but does not differentiate B2B from retail algorithmically. Canary derives B2B classification from a combination of account-category codes, credit-terms configuration, and transaction behavioral pattern from T.

**Companion cards.** `canary-module-c-functional-decomposition.md` (C.2 tier identity, C.3 loyalty + AR — C inherits both), `garden-center-operating-reality.md` (landscaper / wholesale / project-tier vertical reality).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| M.1.1 | Read `AR_CUST.CATEG_COD` per customer from R's substrate | R's customer publication (C.2) | Account category code; Canary maps customer-configured codes to B2B tier (e.g., "LAND" = landscaper, "WHOLE" = wholesale) → TBD: L4 implementation detail pending |
| M.1.2 | Read `AR_CUST_CTL` multi-tier pricing flags | R's customer publication | `AR_CUST_CTL` controls which price tier the customer accesses (Price 1/2/3); tier access is the strongest B2B signal in Counterpoint → TBD: L4 implementation detail pending |
| M.1.3 | Detect commercial-account indicator via credit terms | C.3 — `AR_CUST.NO_CR_LIM` / `CR_RATE` presence | Cash customers have no credit config; commercial accounts have credit terms; credit existence = commercial strong-signal → TBD: L4 implementation detail pending |
| M.1.4 | Derive B2B classification score per customer | M.1.1 (category code match) + M.1.2 (price-tier access) + M.1.3 (credit terms) + T's average-order-value pattern | Multi-signal derivation; merchant-configurable weight; outputs B2B_CLASS: retail / commercial / wholesale / project-tier → TBD: L4 implementation detail pending |
| M.1.5 | Handle unclassified accounts (no category code, no credit terms, default tier) | Canary-native fallback | Default classification based on T's behavioral pattern alone; flagged as CLASSIFICATION-UNCERTAIN → TBD: L4 implementation detail pending |
| M.1.6 | Reclassification on CATEG_COD change | R event stream — when R detects CATEG_COD update | Classification must update within one R-poll cycle; downstream M.2/M.3 consumers notified → TBD: L4 implementation detail pending |

### User stories

- *As C's Classifier, I want every Counterpoint customer with non-default price-tier access (`AR_CUST_CTL` price-2/3 flags) identified as commercial-strong-signal, regardless of whether their CATEG_COD has been set — price-tier access is the most reliable B2B indicator in the substrate.*
- *As a Garden-Center Account Manager in Owl, I want to ask "show me all commercial accounts" and get a ranked list by B2B classification tier (landscaper / wholesale / project / uncertain), with the signals that drove the classification visible.*
- *As C's Classifier, I want CATEG_COD reclassifications propagated within one R-poll cycle — a landscaper who gets reclassified to wholesale should see their M.2 credit posture recalculated immediately.*
- *As an Operator, I want CLASSIFICATION-UNCERTAIN accounts flagged in the onboarding review queue — accounts with no category code, no credit terms, and below-threshold average order value need a human decision on B2B status.*

## M.2 — Per-customer credit posture

**Coverage posture.** ★ Canary-native, built from R's substrate and F's AR ledger. Counterpoint stores credit limit and balance in `AR_CUST`; Canary's contribution is building a credit posture signal — current utilization, aging pattern, payment-velocity — that Counterpoint doesn't surface as a risk score.

**Companion cards.** `canary-module-c-functional-decomposition.md` (C.3 loyalty + AR), `canary-module-f-functional-decomposition.md` (F.6 AR ledger — M.3 below is the cross-cut).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| M.2.1 | Read credit limit and current balance from `AR_CUST` via C.3 | R's AR surface | `AR_CUST.NO_CR_LIM` (unlimited credit flag), `AR_CUST.CR_RATE` (credit rating), `AR_CUST.BAL` (current balance) → TBD: L4 implementation detail pending |
| M.2.2 | Calculate credit utilization per commercial account | `AR_CUST.BAL` / `AR_CUST.CRDLIM` | Utilization = current balance / credit limit; high utilization is an account health signal → TBD: L4 implementation detail pending |
| M.2.3 | Read aging buckets from `Customer_OpenItems` via C.3 | R's AR aging surface | Current / 30 / 60 / 90+ day aging; F.6's cross-cut surfaces the same data from the finance side → TBD: L4 implementation detail pending |
| M.2.4 | Derive payment velocity per account | Trailing payment pattern from `Customer_OpenItems` close dates | Fast-paying accounts vs. chronic-slow accounts; velocity is a C-native signal not in Counterpoint → TBD: L4 implementation detail pending |
| M.2.5 | Produce per-account credit posture signal | M.2.2 utilization + M.2.3 aging + M.2.4 velocity | Output: `CREDIT_POSTURE` enum: current / watch / past-due / at-limit; drives M.4 Q-rule eligibility → TBD: L4 implementation detail pending |
| M.2.6 | Trigger credit-hold flag on AT-LIMIT accounts | M.2.5 → alert → account manager | Credit holds in Counterpoint are operator-set; Canary surfaces the signal, doesn't write back to Counterpoint → TBD: L4 implementation detail pending |

### User stories

- *As C's Credit Engine, I want per-account credit utilization recalculated after each payment recorded in `Customer_OpenItems`, so the CREDIT_POSTURE signal reflects real-time balance, not last-week's snapshot.*
- *As a Garden-Center Account Manager, I want to ask "which commercial accounts are past 60 days on their balance?" and get a ranked list with current balance, credit limit, and payment velocity — so I can prioritize outreach before accounts hit the formal collections threshold.*
- *As C, I want CREDIT_POSTURE:AT-LIMIT accounts to surface an alert to the account manager before the next transaction — Counterpoint doesn't prevent a new sale to an at-limit account; Canary should surface the warning.*
- *As an LP Analyst (Q.6), I want accounts with deteriorating credit posture (trending toward past-due) cross-referenced against recent high-value transactions — a landscaper maxing their credit right before going dark is a Q-relevant pattern.*

## M.3 — AR ledger surface (cross-cut with F.6)

**Coverage posture.** ◐ Derived — cross-cut with F's AR module. The AR ledger (open items, aging, payment history) is owned by F.6 from the finance side; C surfaces the same data through the account-management lens. This L2 is the contractual handshake between C and F — two modules reading the same substrate for different analytical purposes.

**Companion cards.** `canary-module-f-functional-decomposition.md` (F.6 AR ledger — this L2 is C's read of F's surface).

### L3 processes

| ID | L3 process | Source | Notes |
|---|---|---|---|
| M.3.1 | Read per-account open items from F.6 publication | F.6's AR ledger surface | Open invoices, amounts, due dates; C reads from F's AR publication, not directly from Counterpoint → TBD: L4 implementation detail pending |
| M.3.2 | Aggregate open items into per-account AR summary | C's account-management projection over F.6 | Total outstanding, oldest open item date, count of past-due items — account-management view → TBD: L4 implementation detail pending |
| M.3.3 | Track payment history per account | F.6's payment-event stream | Payments recorded in `Customer_OpenItems` close events; C tracks payment pattern (amount, timing, method) → TBD: L4 implementation detail pending |
| M.3.4 | Surface AR aging calendar per commercial account | C's account-management surface | 0-30-60-90+ day aging per account; visible to account managers and sales reps in Owl → TBD: L4 implementation detail pending |
| M.3.5 | Detect anomalous payment patterns | M.3.3 payment history vs. M.2.4 velocity baseline | A normally-fast-paying landscaper who starts paying slowly is a M.4 input signal → TBD: L4 implementation detail pending |

### User stories

- *As an Account Manager in Owl, I want a per-account AR summary (total outstanding, oldest item, aging buckets) visible alongside the customer's transaction history — not a separate AR module the operations team lives in.*
- *As C, I want F.6's AR ledger as my substrate for M.3 — I do not want to poll `Customer_OpenItems` independently. If F.6 polls it, I read from F.6's publication. One poller per endpoint.*
- *As C's Anomaly Detector, I want accounts whose payment velocity has slowed more than 20% vs. their 90-day baseline flagged as a M.4 Q-rule input — slow-pay trend is a leading indicator, not a lagging one.*

## M.4 — B2B-specific detection rules (cross-cut with Q)

**Coverage posture.** ★ Canary-native. B2B-specific detection rules are Canary-native — Counterpoint has no analytics over commercial accounts. These rules cross-cut Q's detection engine and are triggered by C's signals (credit posture, classification tier, AR pattern).

**Companion cards.** `canary-module-q-functional-decomposition.md` (Q-rule catalog — C-family rules cross-cut Q's detection framework).

### L3 processes

| ID | L3 process | Trigger | Notes |
|---|---|---|---|
| M.4.1 | B2B-CREDIT-01: At-limit account continues transacting | M.2.5 AT-LIMIT + T's transaction stream | A commercial account at credit limit making new purchases — alert to account manager → TBD: L4 implementation detail pending |
| M.4.2 | B2B-CREDIT-02: Rapid credit consumption before going dark | M.2.2 utilization velocity spike | Account that has been at <20% utilization suddenly consuming 80% in two weeks is a collections risk signal → TBD: L4 implementation detail pending |
| M.4.3 | B2B-AR-01: Past-due balance crosses threshold | M.2.3 aging bucket transition to 60+ | Threshold configurable; default 60-day past-due triggers account manager alert → TBD: L4 implementation detail pending |
| M.4.4 | B2B-TIER-01: Transaction price inconsistent with B2B tier | T's transaction price-level vs. M.1.2 tier assignment | A wholesale account being sold at retail price (or vice versa) is an account-setup inconsistency → TBD: L4 implementation detail pending |
| M.4.5 | B2B-PATTERN-01: Commercial account transacting outside business hours | T's transaction timestamp vs. account classification | A flagged-commercial account transacting at 9pm Sunday may indicate account-sharing (ASSUMPTION-C-06) → TBD: L4 implementation detail pending |

### Canary Detection Hooks

M.4 rules are cataloged in the Q rule catalog under the **Q-C** (Commercial / B2B) family. C derives the input signals; Q fires the alert via Chirp. These are account-management alerts, not LP fraud alerts — routed to the account manager surface in Owl rather than the LP queue.

| M.4 rule | Q catalog entry | Chirp alert type |
|---|---|---|
| M.4.1 B2B-CREDIT-01 (at-limit transacting) | **Q-M-01** | Account-management alert → Owl account manager surface |
| M.4.2 B2B-CREDIT-02 (rapid credit consumption) | **Q-M-02** | Account-management alert → Owl (pre-delinquency) |
| M.4.3 B2B-AR-01 (past-due threshold) | **Q-M-03** | Account-management alert → Owl account manager surface |
| M.4.4 B2B-TIER-01 (price-tier mismatch) | **Q-M-04** | Data-quality flag → store manager (not LP queue) |
| M.4.5 B2B-PATTERN-01 (after-hours commercial) | **Q-M-05** | Low signal → escalates when combined with Q-M-01/02 |

See `canary-module-q-counterpoint-rule-catalog.md` §Commercial / B2B for substrate, logic, parameters, and allow-list for each rule.

### User stories

- *As Q's Detection Engine (C-rule family), I want M.4.1 B2B-CREDIT-01 to fire an alert to the account manager — not a fraud alert — when an at-limit commercial account attempts a new purchase. The operator decides whether to override the credit hold.*
- *As an Account Manager in Owl, I want M.4.2 (rapid credit-consumption spike) surfaced as a proactive alert before the account hits the formal past-due threshold — the signal should arrive when the account is still recoverable.*
- *As C's Rule Engine, I want B2B-TIER-01 (price-tier mismatch) to fire as a data-quality flag, not a fraud detection — it most likely means the account was set up incorrectly in Counterpoint, not that someone is gaming the system.*
- *As a store manager, I need to reclassify a customer from retail to wholesale tier during the spring landscape-contractor season so that their pricing reflects their current purchase volume.*
- *As an account manager, I need to approve a one-time credit-hold override for a trusted B2B account that is temporarily over-limit so that they can complete a critical end-of-season order.*
- *As a loss prevention analyst, I need to detect when a customer's current tier (WHOLESALE) conflicts with their historical transactions (RETAIL pricing) so I can flag potential retroactive pricing abuse.*

## M.5 — Cross-module substrate contracts

**Purpose.** C is a derived module — it depends on R and F for its substrate, and it promises classification signals to Q and the account-management surface. These contracts are the dependency chain that makes C safe to build after R and F are stable.

| ID | Contract | Owner downstream | What C promises |
|---|---|---|---|
| M.5.1 | B2B classification per customer (`B2B_CLASS` enum) | Q (rule eligibility), Owl (account-management surface), J (wholesale-tier replenishment context) | Updated within one R-poll cycle of any CATEG_COD or price-tier change → TBD: L4 implementation detail pending |
| M.5.2 | `CREDIT_POSTURE` signal per commercial account | Q (M.4 rules), Account manager (Owl alert) | Recalculated after each payment event or balance change; history preserved → TBD: L4 implementation detail pending |
| M.5.3 | AR summary per commercial account (total outstanding, aging, velocity) | F.6 (cross-cut, symmetric), Owl (account management) | C reads from F.6's AR publication; M.5.3 is the account-management projection of F.6's finance-side view → TBD: L4 implementation detail pending |
| M.5.4 | B2B-specific alert events (M.4.1–M.4.5) | Q's alert pipeline, Account manager (Owl) | B2B alerts are distinct from Q's transaction-level fraud alerts; classified as account-management alerts, not LP alerts → TBD: L4 implementation detail pending |
| M.5.5 | Price-tier assignment per commercial account | T's transaction pipeline (for price-level validation), J (PO recommendation tier context) | C's price-tier read from `AR_CUST_CTL` is surfaced to T's transaction validation and J's recommendation engine → TBD: L4 implementation detail pending |
| M.5.6 | CLASSIFICATION-UNCERTAIN flag roster | Operator onboarding queue | Unresolved accounts flagged for human classification decision at onboarding or periodic review → TBD: L4 implementation detail pending |

### User stories

- *As Q's Rule Engine, I want C's B2B_CLASS and CREDIT_POSTURE signals as inputs so M.4.x rules can fire without C re-deriving classification from scratch at rule-evaluation time.*
- *As J's Recommendation Engine, I want price-tier context for commercial accounts (M.5.5) so that wholesale-tier accounts don't get replenishment recommendations calibrated for retail-unit sale velocity.*
- *As an Account Manager, I want M.5.6 CLASSIFICATION-UNCERTAIN flagged accounts surfaced in a review queue at onboarding, so I'm not discovering mystery accounts when they first hit a credit alert.*

## Assumptions requiring real-customer validation

| ID | Assumption | What it blocks | Resolution path |
|---|---|---|---|
| ASSUMPTION-C-01 | `AR_CUST.CATEG_COD` is consistently configured by L&G Counterpoint operators — some operators may not set category codes | M.1.1 classification signal reliability | Customer catalog inspection; if codes are sparse, M.1.2 (price-tier access) becomes the primary signal |
| ASSUMPTION-C-02 | `AR_CUST_CTL` multi-tier flags are the definitive Counterpoint B2B signal — assumed based on Counterpoint schema; not confirmed as the operational convention | M.1.2 and M.5.5 price-tier contract | Sandbox inspection of AR_CUST_CTL fields and how they interact with POS transaction price level |
| ASSUMPTION-C-03 | Garden-center commercial accounts represent 20-40% of gross revenue — assumed from vertical domain knowledge, not customer-confirmed | C module design-priority justification | Customer revenue-mix interview at kickoff |
| ASSUMPTION-C-04 | Landscaper / wholesale / project-tier is a useful classification taxonomy for L&G garden centers — customer may use different tier names or have more/fewer tiers | M.1.4 tier taxonomy and M.1.5 unclassified handling | Customer interview at onboarding; taxonomy is merchant-configurable |
| ASSUMPTION-C-05 | `Customer_OpenItems` is populated by L&G Counterpoint operators — some smaller operators may not use Counterpoint's AR module | M.3 and M.2.3 AR aging availability | Customer interview; if AR module not in use, M.3 and M.2.3 are empty; M.2.5 CREDIT_POSTURE falls back to credit-field-only signals |
| ASSUMPTION-C-06 | B2B-PATTERN-01 (commercial account transacting outside business hours) is an operationally useful signal — may produce too many false positives if landscapers legitimately transact in evenings | M.4.5 rule calibration | Real customer transaction timing data; likely needs vertical allow-list |
| ASSUMPTION-C-07 | Canary does not write B2B classification back to Counterpoint (one-way read) | M.1.4 classification destination | Design decision: Canary-side only; confirmed by NCR-as-competitor framing (no write-back to Counterpoint without explicit per-customer opt-in) |
| ASSUMPTION-C-08 | F.6 is the single poller for `Customer_OpenItems` — C reads from F.6's publication, not independently | M.3 architecture and M.5.3 contract correctness | Phase III SDD coordination between C and F |

**Highest-leverage gaps:** ASSUMPTION-C-01 (CATEG_COD configuration) and ASSUMPTION-C-05 (AR module in use) are the two substrate-availability gaps that most affect C's classification fidelity. Both are engagement-knowable at customer onboarding — not platform-knowable from sandbox alone. ASSUMPTION-C-02 (AR_CUST_CTL price-tier as definitive B2B signal) is platform-knowable from sandbox inspection and should be resolved before Phase 1 adapter work begins.

## Customer-specific overrides

*Empty until a real customer engagement starts. Format reserved:*

```
Customer: <name>
B2B tier taxonomy: <landscaper/wholesale/project-tier (default) | <customer-specific tiers>>
CATEG_COD to tier mapping: <standard mapping | customer-specific>
AR module in use: <yes | no — M.3 and M.2.3 empty>
Credit hold mode: <alert-only (default) | block-transaction>
B2B-CREDIT alert threshold: <AT-LIMIT (default) | >XX% utilization>
B2B-AR past-due threshold: <60 days (default) | <N> days>
Price-tier access signal: <AR_CUST_CTL (default) | customer-specific override>
Disabled C.x processes (with reason):
  C.x.x: <reason>
ASSUMPTION resolutions:
  ASSUMPTION-C-NN: resolved as <answer>; source: <evidence>
  ...
```

## Operating notes

**Cast of actors:**

| Actor | Role | Lives where |
|---|---|---|
| Classifier | Derives B2B classification from R substrate | Canary-internal (M.1) |
| Credit Engine | Calculates credit posture from R + F substrate | Canary-internal (M.2) |
| AR Surface | Projects F.6's AR ledger through the account-management lens | Canary-internal (M.3) |
| B2B Rule Engine | Evaluates M.4 rules; routes alerts to Q's pipeline | Canary-internal (M.4) |
| Account Manager | Human-in-the-loop for credit posture alerts and classification decisions | Customer org |
| Owl / Fox | Account-management surface + investigation queue | Canary-internal |

**C is a derived module — build sequence matters.** C cannot function without R (customer master, AR fields) and F (AR ledger). The build sequence constraint is load-bearing: C is not an early-sprint candidate. It is the Module 4 in the v2 ring, behind R and F.

**The B2B signal in Counterpoint is distributed, not concentrated.** Unlike Square (which doesn't carry B2B metadata at all), Counterpoint carries useful signals across multiple fields — but none of them is a single "this is a commercial account" flag. C's value is the multi-signal derivation that turns CATEG_COD + price-tier + credit-terms + behavioral pattern into a clean classification. That synthesis doesn't exist in Counterpoint and is a genuine Canary contribution.

**Garden-center vertical context is load-bearing for C.** The landscaper / wholesale / project-tier taxonomy is not a generic retail construct — it's the specific commercial-account structure that garden centers operate with. Municipality contracts (parks departments, school districts), landscape contractors buying for large installation projects, and wholesale nursery accounts all have different risk profiles. C's classification must accommodate this without over-generalizing.

## Related

- `Canary-Retail-Brain/modules/M-merchandising.md` — L1 canonical spec
- `canary-module-m-merchandising.md` — L2 Canary code/schema crosswalk
- `canary-module-c-functional-decomposition.md` — sister card; C inherits C.2 (tier identity) and C.3 (loyalty + AR); R is C's primary substrate dependency
- `canary-module-f-functional-decomposition.md` — sister card; M.3 reads from F.6's AR ledger; F is C's secondary substrate dependency
- `canary-module-q-functional-decomposition.md` — sister card; M.4 rules route to Q's detection pipeline; Q-rule catalog C-family
- `canary-module-t-functional-decomposition.md` — sister card; T's transaction stream is M.1.4's behavioral-pattern input and M.4.5's rule substrate
- `ncr-counterpoint-api-reference.md` — AR_CUST, AR_CUST_CTL, Customer_OpenItems field context
- `ncr-counterpoint-endpoint-spine-map.md` — C-column placement (no dedicated endpoints; derived from R's AR surface)
- `garden-center-operating-reality.md` — landscaper / wholesale / project-tier reality; municipality accounts; B2B revenue mix
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — C row = ◐ Derived; this card is the L2/L3 expansion of that cell

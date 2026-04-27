---
classification: internal
type: wiki
sub-type: module-functional-decomposition
date: 2026-04-26
last-compiled: 2026-04-26
module: N
solution-map-cell: ● Full direct (Counterpoint Store / Station / DeviceConfig / Workgroup / Tokenize — 6 endpoints; ~150 fields per PS_STR_CFG_PS)
companion-modules: [T, Q, F, R, S]
companion-substrate: [ncr-counterpoint-api-reference.md, ncr-counterpoint-endpoint-spine-map.md]
companion-context: [garden-center-operating-reality.md, ncr-counterpoint-rapid-pos-relationship.md]
companion-canary-spec: Canary-Retail-Brain/modules/N-device.md
companion-canary-crosswalk: Brain/wiki/canary-module-n-device.md
companion-catz: CATz/proof-cases/specialty-smb-counterpoint-solution-map.md
methodology-note: "Sister card to canary-module-q/t/r/j/s/f-functional-decomposition.md. Same template per CATz/method/artifacts/module-functional-decomposition.md. N looks small (6 endpoints) but is dense — `PS_STR_CFG_PS` carries ~150 fields per store, most of which are Q substrate (LP thresholds, drawer config, void-comp reasons). N's true scope is store config, not just device registry."
---

# Module N (Device — Stores / Stations / Per-Store Config) — Functional Decomposition

> **Artifact layer.** Third of three Canary module artifact layers:
> 1. **Canonical spec** (vendor-neutral) — `Canary-Retail-Brain/modules/N-device.md`
> 2. **Code/schema crosswalk** (Canary-specific) — `Brain/wiki/canary-module-n-device.md`
> 3. **Functional decomposition** (Counterpoint-substrate-aware, L2/L3 + user stories) — *this card*

## Governing thesis

N is the **store and per-store config substrate** for the spine. The endpoint count is small (6 — Store, Station, DeviceConfig, Workgroup, two Tokenize) but the field density is enormous: `PS_STR_CFG_PS` carries roughly **150 fields per store** covering LP thresholds (max discount caps, void-comp reasons, credit-card history retention), drawer discipline (auto-drawer activation, count, reconciliation, reactivation alarms), tax defaults, ticket numbering, EDC payment processor config, customer-profile field enablement, and dropship/layaway/order workflow settings. Most of these fields are **Q substrate**, not just device-inventory metadata.

For a Lawn & Garden tenant specifically, N matters because: (1) **per-store discount caps and void-comp reasons** are the customer-tunable thresholds Q-DM-01 and Q-VR-x rules read against; (2) **drawer-session correlation** (`DRW_ID + DRW_SESSION_ID + USR_ID` on every Document) is the substrate for the entire Q.2.4 drawer-and-session detection family; (3) **multi-store tenant operation** (a regional H&G chain with 5-30 stores) needs per-store config delivered cleanly, not collapsed.

N is **● Full direct** in every Counterpoint Solution Map cell, but the cell hides one structural choice: **N owns the per-store config table even though `PS_STR_CFG_PS` looks like it belongs in `Places.stores`**. This card makes that explicit — N.4 is the LP-substrate L2, dedicated to surfacing the threshold fields Q reads against.

## Executive summary

| Dimension | Count | Source |
|---|---|---|
| L2 process areas | 6 | This card |
| L3 functional processes | 27 | This card |
| Counterpoint endpoints in N's path | 6 (Store, Station, DeviceConfig, Workgroup, Tokenize × 2) | API reference |
| Cached entities (24h server-side) | 4 (Stores, Stations, Workstations, Workgroup-related) | API reference cache discipline |
| Per-store config fields surfaced | ~150 (`PS_STR_CFG_PS`) | API reference |
| LP-threshold fields (Q substrate) | ~10 (MAX_DISC_AMT, MAX_DISC_PCT, USE_VOID_COMP_REAS, RETAIN_CR_CARD_NO_HIST, AUTO_DRW_*, ALLOW_DRW_REACTIV, etc.) | API reference + Q rule catalog |
| Substrate contracts N owes downstream | 8 | This card §N.6 |
| Assumptions requiring real-customer validation | 7 | Tagged `ASSUMPTION-N-NN` |
| User stories enumerated | 33 | Observer + actor mix; cast in §Operating notes |

**Posture:** archetype-shaped against Counterpoint specifically. The per-store config surface (N.4) is treated as load-bearing because it's where Q's tunability lives — not as a config-management afterthought.

## L1 → L2 → L3 framework

```
L1 (Solution Map cell)         N = ● Full direct (Counterpoint Store / Station / DeviceConfig / Workgroup / Tokenize)
                                 │
L2 (Process areas)               ├── N.1  Store master + config ingestion
                                 ├── N.2  Station / device registry
                                 ├── N.3  Drawer-session correlation     (Q substrate)
                                 ├── N.4  Per-store thresholds + LP substrate    (Q substrate; load-bearing)
                                 ├── N.5  Workgroup + tenant-bootstrap defaults
                                 └── N.6  Cross-module substrate contracts
                                 │
L3 (Functional processes)       (27 — enumerated per L2 below)
                                 │
L4 (Implementation detail)      Lives in SDDs + module specs
                                  (Canary-Retail-Brain/modules/N-device.md,
                                   docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md §6.5)
```

## N.1 — Store master + config ingestion

**Purpose.** Pull `PS_STR` (store master) plus `PS_STR_CFG_PS` (per-store config — ~150 fields) into CRDM at tenant bootstrap. Refresh on cache invalidation. The config payload is the densest in the spine; surfacing it cleanly is N's primary job.

**Companion cards.** `ncr-counterpoint-api-reference` § "Store config field richness (PS_STR_CFG_PS)", `ncr-counterpoint-endpoint-spine-map` § "Store / device — module N".

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| N.1.1 | Store master ingestion | `GET /Store/{StoreID}` | `PS_STR` + nested `PS_STR_CFG_PS`; **cached server-side 24h** |
| N.1.2 | Per-store config field surfacing | `PS_STR_CFG_PS` (~150 fields) | All fields preserved verbatim; downstream consumers (Q, F, R) read what they need |
| N.1.3 | Per-store demographics | Address, contact, manager, hours | Substrate for store-level reporting + per-store comp/non-comp segmentation |
| N.1.4 | Industry-type field surfacing | `PS_STR_CFG_PS.INDUSTRY_TYP` | E.g., "R" = Retail; may differ in garden-center / nursery deployments — **ASSUMPTION-N-04** |
| N.1.5 | Per-store cache refresh | `ServerCache: no-cache` for first poll of cycle when config-change suspected | Standard cache discipline |

### User stories

- *As N, I want every `PS_STR_CFG_PS` field surfaced so Q can read whatever threshold it needs without per-rule special-casing — the field set is large but the surface contract is uniform.*
- *As an Operator onboarding a multi-store tenant in Owl, I want all stores' configs ingested at bootstrap with confirmation that no store is missing or has malformed config.*
- *As a Garden-Center GM, I want per-store comp/non-comp tagging captured so analytics treat new stores correctly (no false drift alerts on a brand-new location with thin history).*

## N.2 — Station / device registry

**Purpose.** Per-station detail (`PS_STA` via `GET /Store/{StoreID}/Station/{StationID}`) plus device-level configuration (`GET /DeviceConfig/{WorkstationID}` — note: missing from the README chart per phase-0 brief). Stations are the per-register identity used for `STA_ID` references on every Document.

**Companion cards.** `ncr-counterpoint-api-reference` § "Spine Module N — Device / Stores / Stations", `ncr-counterpoint-phase-0-context-brief` § "DeviceConfig exists but missing from chart".

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| N.2.1 | Station enumeration per store | `GET /Store/{StoreID}/Station/{StationID}` | `PS_STA`; cached 24h |
| N.2.2 | Per-workstation device config | `GET /DeviceConfig/{WorkstationID}` | Per-physical-device config; chart omission noted but endpoint real |
| N.2.3 | Workstation-to-station mapping | Cross-cut from device config to PS_STA | Substrate for hardware-level Q rules (e.g., per-workstation activity) |
| N.2.4 | Tokenization scope per store | `GET /Store/{StoreId}/Tokenize`, `GET /Stores/Tokenized` | Cross-cut with F.5 (tokenization L2) |

### User stories

- *As N, I want every station registered and joinable from any Document's `STA_ID` reference, so per-station Q rules (Q-TM-01 cash-only register pattern) have full station context.*
- *As an Operator, I want device-config inconsistencies flagged at ingestion (e.g., a workstation registered in DeviceConfig but no matching `PS_STA` row) so configuration drift surfaces operationally.*
- *As Q, I want per-workstation auditability — when a Document audit log shows `CURR_WKSTN_NAM`, I want to join it cleanly to a known device record.*

## N.3 — Drawer-session correlation (Q substrate)

**Purpose.** Every Document carries `DRW_ID + DRW_SESSION_ID + USR_ID`. Drawer-session correlation is the substrate for the entire Q.2.4 (drawer-and-session) detection family — drawer-shrinkage, post-close activity, drawer reactivation patterns. N's role is to surface drawer sessions as a queryable entity, not just per-Document metadata.

**Companion cards.** `canary-module-q-functional-decomposition.md` § Q.2.4 (consumer of drawer-session substrate), `ncr-counterpoint-api-reference` § "Cash drawer" (PS_STR_CFG_PS subset).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| N.3.1 | Drawer-session entity surfacing | Inferred from `DRW_ID + DRW_SESSION_ID` deltas across Documents | N constructs the session entity; Counterpoint may not surface it directly via endpoint |
| N.3.2 | Per-session start/end timestamp resolution | First Document with the session ID = start; close events from audit log = end | **ASSUMPTION-N-02**: drawer-close event modeling unknown |
| N.3.3 | Per-session employee + station + drawer attribution | `(USR_ID, STA_ID, DRW_ID)` on every Document in the session | Substrate for Q.2.4 family + per-employee performance analytics |
| N.3.4 | Drawer-reactivation tracking | Per `PS_STR_CFG_PS.ALLOW_DRW_REACTIV` enabled stores; events from audit log | Substrate for Q-DS-03 (drawer reactivation pattern) |
| N.3.5 | Drawer-count vs expected reconciliation | Drawer reconciliation events (likely audit-log entries) | Substrate for Q-DS-01 (drawer-shrinkage) |

### User stories

- *As N, I want a queryable drawer-session entity per `(STA_ID, DRW_ID, DRW_SESSION_ID)` with start/end timestamps and member-Documents available, so Q's Q.2.4 family doesn't have to reconstruct sessions from scratch every time.*
- *As Q (Q-DS-02), I want post-close activity detectable — any audit log entry on a Document committed after its drawer's session-close timestamp.*
- *As an LP Analyst investigating a Q-DS-01 drawer-shrinkage case, I want to see the full drawer session: opening count, all transactions, closing count, expected count, variance — all on one screen.*

## N.4 — Per-store thresholds + LP substrate (Q substrate; load-bearing)

**Purpose.** This is where N earns its keep. `PS_STR_CFG_PS` carries the customer-tunable LP thresholds Q rules read against — discount caps, void-comp requirements, credit-card history retention (PCI-relevant), customer-profile field enablement. These aren't device-config trivia; they're the operational tunability surface for the LP layer.

**Companion cards.** `canary-module-q-counterpoint-rule-catalog.md` (every Q-DM-, Q-VR-, Q-DS-, Q-AT- rule reads from these fields), `ncr-counterpoint-api-reference` § "Store config field richness".

### L3 processes

| ID | L3 process | Substrate (PS_STR_CFG_PS field) | Notes |
|---|---|---|---|
| N.4.1 | Discount cap thresholds | `MAX_DISC_AMT`, `MAX_DISC_PCT`, `MIN_DISC_PCT_TO_PRT` | Substrate for Q-DM-01 (discount-cap exceeded) |
| N.4.2 | Void / comp reason requirements | `USE_VOID_COMP_REAS` | Substrate for Q-VR-x (void-and-return rule family) |
| N.4.3 | Credit-card history retention | `RETAIN_CR_CARD_NO_HIST` (PCI-relevant) | PCI compliance flag; substrate for compliance dashboards |
| N.4.4 | Drawer config + alarms | `AUTO_DRW_ACTIV`, `AUTO_DRW_CNT`, `AUTO_DRW_RECON`, `ALLOW_DRW_REACTIV`, `USE_OPN_DRW_ALARM` | Substrate for Q.2.4 family |
| N.4.5 | Customer-profile field enablement | `USE_PROF_ALPHA_1..5`, `USE_PROF_COD_1..5`, `USE_PROF_DAT_1..5`, `USE_PROF_NO_1..5` | Per-store custom-field slots active; cross-cut with R |
| N.4.6 | EDC payment processor config | `EDC_PROCESSOR`, `EDC_MERCH_NO`, `SERV_NAM_1`, `EDC_MODE`, AVS / CVV settings | Cross-cut with F (Secure Pay status) |
| N.4.7 | Workflow defaults (order, layaway, backorder, dropship) | Per-store quote validity days, order deposit minimums, dropship config | Substrate for J cross-cuts (workflow-aware replenishment) + per-store BOPIS readiness |

### User stories

- *As N, I want every LP-threshold field (N.4.1–N.4.4) joined inline on every store-context query, so Q-DM-01 / Q-VR-x / Q-DS-x rules don't need a second lookup per detection.*
- *As an Operator at a multi-store tenant, I want a per-store threshold dashboard showing all 10 LP thresholds at a glance, with deltas highlighted (e.g., Store A's MAX_DISC_PCT is 20%, all other stores are 15%).*
- *As Canary's Compliance Story, I want PCI-relevant flags (N.4.3) surfaced and trended, so a customer's credit-card-history-retention setting drift is visible operationally.*
- *As Q (Q-DM-01), I want each store's `MAX_DISC_PCT` available without a separate read, so discount-cap-exceeded detection runs in one pass over Document lines.*
- *As C (B2B-derived), I want EDC and workflow defaults available so per-store B2B account behavior is contextualized.*

## N.5 — Workgroup + tenant-bootstrap defaults

**Purpose.** `Workgroup` carries per-tenant numbering defaults (`NXT_TKT_NO`, `NXT_HOLD_NO`, `NXT_QUOT_NO`, `NXT_ORD_NO`, `NXT_LWY_NO`, `NXT_XFER_NO`, `NXT_RECVR_NO`, `NXT_PO_NO`, `NXT_PREQ_NO`, `NXT_RTV_NO`, `NXT_GFC_NO`, `NXT_AR_DOC_NO`) plus customer-template defaults that drive `POST /Customer` from the Counterpoint side. N surfaces these at tenant bootstrap; downstream consumers (T, R, J) reference them.

**Companion cards.** `ncr-counterpoint-document-model` § DOC_TYP taxonomy (cross-references to NXT_*_NO), `canary-module-r-functional-decomposition.md` § R.1.6 (Workgroup template read).

### L3 processes

| ID | L3 process | Substrate | Notes |
|---|---|---|---|
| N.5.1 | Workgroup ingestion at tenant bootstrap | `GET /Workgroup/{WorkgroupID}` | Cached; rarely changes |
| N.5.2 | Document-numbering generators surfaced | Per-Document-type next-number fields | Substrate for T's DOC_TYP routing + J's PO numbering |
| N.5.3 | Customer-template defaults surfaced | Workgroup-driven defaults that influence customer creation | Cross-cut with R.1.6 |
| N.5.4 | Per-`(tenant, company_alias)` workgroup partitioning | Multi-company tenants may have N workgroups | Mirrors R.1.8 multi-company namespace isolation |

### User stories

- *As N, I want workgroup defaults available at tenant bootstrap so T's parser can interpret DOC_TYP-to-numbering correctly without querying Counterpoint per Document.*
- *As R, I want the workgroup customer-template defaults available when a shell-row upsert occurs, so R can populate sensible defaults for fields not yet present.*
- *As J, I want the per-Document-type next-number generators known so PO recommendations can be reconciled to the resulting Counterpoint PO numbers.*

## N.6 — Cross-module substrate contracts

**Purpose.** N supplies store-and-config substrate to Q (LP thresholds), T (DOC_TYP routing context), R (workgroup defaults), F (EDC + tokenization), and J (workflow defaults). This L2 is the contract registry. Symmetric to T.7 / R.6 / S.7 / F.7 / J.8b.

### L3 contracts (registry)

| ID | Contract | Owner downstream | What N promises |
|---|---|---|---|
| N.6.1 | Store master + per-store config inline | Q (every threshold-aware rule), F (per-store tax defaults), R (per-store customer-profile slots) | Full `PS_STR + PS_STR_CFG_PS` joined to every store-context query |
| N.6.2 | LP thresholds inline on every transaction | Q (Q-DM-01, Q-VR-x, Q-DS-x family) | `MAX_DISC_AMT/PCT`, `USE_VOID_COMP_REAS`, drawer config exposed per transaction join |
| N.6.3 | Drawer-session entity queryable | Q (Q.2.4 family) | Per-`(STA_ID, DRW_ID, DRW_SESSION_ID)` session with start/end + member-Documents |
| N.6.4 | Station + workstation registry | T (parse — `STA_ID` resolution), Q (per-station rules) | Every Station + DeviceConfig record ingested + linkable from `STA_ID` / `CURR_WKSTN_NAM` |
| N.6.5 | Workgroup defaults inline | T (DOC_TYP routing), R (customer-template), J (numbering generators) | Numbering generators + customer-template defaults at tenant bootstrap |
| N.6.6 | Industry-type field | Vertical-pack application (Q.6) | `INDUSTRY_TYP` exposed for vertical-pack auto-application logic |
| N.6.7 | Per-`(tenant, company_alias)` partitioning | Multi-company tenants — all downstream | Stores + workgroups partitioned cleanly per company alias |
| N.6.8 | Cache-discipline metadata | All | `last_polled_at` per N entity so consumers can detect stale config |

### User stories

- *As N, I want every contract in N.6 enforced via the contract test suite, so a silent break (e.g., LP thresholds dropped from join) shows up at conformance test.*
- *As Q, I want to assert at boot that N surfaces all `PS_STR_CFG_PS` LP-threshold fields, so a contract break shows up at startup not at first Q-DM-01 false-negative.*
- *As Canary's Product Owner, I want N's per-store config delivered uniformly across all stores in a multi-store tenant, with per-store drift surfaced as an operational signal not a silent inconsistency.*
- *As an IT administrator, I need to enroll multiple workstations and map each to its assigned station in a single onboarding workflow so that a new store location is fully configured before opening day.*
- *As a multi-store operations manager, I need Canary to alert me when a store's device configuration drifts from the approved template (e.g., unauthorized station added or removed) so I can remediate before it affects LP thresholds.*

## Canary Detection Hooks

N is a foundational substrate module. Its direct detection contribution routes through N.4 (LP threshold configuration) and N.5 (drawer-session context) — N does not fire detections itself, but its substrate gates which Q rules fire and at what sensitivity.

**N detection hooks:**

- **N.4 (LP threshold substrate) → Q.1.4 store-config context:** N.4 publishes drawer-count thresholds, cash-over/short limits, and variance bands consumed by Q.1.4. Any change to N.4 thresholds requires Q rule re-evaluation.
- **N.4 (drawer session config) → Q-DM rule family:** N's drawer-session parameters gate which Q-DM rules fire. Drawer open/close context from N feeds Q-DM-01 (drawer reactivation) trigger evaluation.
- **N.5 (store-demographic config) → Q-IS rule family:** N.5 store config (location type, hours, tenant profile) provides the spatial + operational context that Q-IS accumulation rules use to set baseline expectations.

---

## Assumptions requiring real-customer validation

| ID | Assumption | What it blocks | Resolution path |
|---|---|---|---|
| ASSUMPTION-N-01 | Full `PS_STR_CFG_PS` field set — sample-derived schema may not cover ~150 fields completely | N.1.2 substrate completeness | Sandbox DB schema inspection |
| ASSUMPTION-N-02 | Drawer-close / drawer-count event modeling — captured in `PS_DOC_AUDIT_LOG`, separate KeyValueData, or different endpoint | N.3.2 entire L3; Q-DS-01 substrate path | Sandbox workflow test (mirrors ASSUMPTION-Q-02) |
| ASSUMPTION-N-03 | DeviceConfig endpoint behavior — chart omission means undocumented details may exist | N.2.2 completeness | API doc deep-read or sandbox |
| ASSUMPTION-N-04 | Industry-type values — `R` = Retail confirmed; garden-center / nursery deployments may use different code | N.1.4; vertical-pack auto-application | Customer interview at onboarding |
| ASSUMPTION-N-05 | Customer-profile slot conventions — which `USE_PROF_*` slots are actively used per store | N.4.5; cross-cut with R per-tenant config | Per-customer at onboarding — engagement-knowable |
| ASSUMPTION-N-06 | EDC processor diversity across stores — most multi-store tenants use one processor; some may use multiple | N.4.6; F.5 cross-cut | Customer interview |
| ASSUMPTION-N-07 | Workgroup multi-instance per tenant — single Workgroup typical, but multi-company tenants may have N | N.5.4 partitioning | Per-customer at onboarding |

**Highest-leverage gaps:** N-02 (drawer-close event modeling) — load-bearing for the entire Q.2.4 detection family. Until resolved (sandbox test or doc deep-read), Q-DS-01 substrate path is uncertain.

## Customer-specific overrides

*Empty until a real customer engagement starts. Format reserved:*

```
Customer: <name>
Stores in scope: [<STR_ID list>]
Per-store demographics + tier:
  <STR_ID> | <demographics> | <comp / non-comp / new>
Per-store LP threshold overrides (where they differ from defaults):
  <STR_ID> | MAX_DISC_PCT=<>, USE_VOID_COMP_REAS=<>, ALLOW_DRW_REACTIV=<>
EDC processor per store:
  <STR_ID> | <processor + EDC_MERCH_NO>
Customer-profile slots actively used:
  PROF_ALPHA_1 → <semantic label>
  PROF_COD_1 → <...>
  ...
Workgroup(s): [<workgroup-ID list>]
Industry type per store: <R | other code>
Disabled N.x processes (with reason):
  N.x.x: <reason>
ASSUMPTION resolutions:
  ASSUMPTION-N-NN: resolved as <answer>; source: <evidence>
  ...
```

## Operating notes

**Cast of actors:**

| Actor | Role | Lives where |
|---|---|---|
| Store Master Sync | PS_STR + config ingester | Canary-internal (N.1) |
| Station Registry | Per-station registry maintainer | Canary-internal (N.2) |
| Drawer Session Resolver | Per-session entity constructor | Canary-internal (N.3) |
| LP Threshold Surface | Per-store threshold projection | Canary-internal (N.4) |
| Workgroup Sync | Tenant-bootstrap defaults | Canary-internal (N.5) |
| Operator | Per-store config + onboarding | Canary side |
| Owl / Fox | Analyst-facing surface | Canary-internal |
| Garden-Center GM | Per-store config queries | Customer side |

**N is small in endpoint count, dense in field surface.** Six endpoints; ~150 fields per `PS_STR_CFG_PS`. Most modules grow L3 count from many endpoints; N grows it from one rich endpoint. This is the inverse pattern of T (many DOC_TYPs through one endpoint family).

**N.4 is load-bearing for Q tunability.** Q rules don't hardcode thresholds — they read from N. A customer that sets `MAX_DISC_PCT = 20%` at one store and `15%` at another gets per-store rule application without any Q-side configuration. The substrate is per-store, the rule is uniform.

**Drawer-session correlation (N.3) is the highest-frequency cross-module dependency.** Every Document carries the session keys; Q.2.4's entire family reads from this. The drawer-close event modeling (ASSUMPTION-N-02) is the single highest-leverage discovery for this module.

**Workgroup multi-instance behavior matters for multi-company tenants** (Counterpoint allows N companies per API server, each potentially with their own Workgroup config). The R.1.8 / N.5.4 partitioning contract must hold across both modules.

## Related

- `Canary-Retail-Brain/modules/N-device.md` — L1 canonical spec
- `canary-module-n-device.md` — L2 Canary code/schema crosswalk
- `canary-module-q-functional-decomposition.md` — sister card; N.4 LP-threshold contracts drive Q.2.1 (discount-and-markdown) + Q.2.2 (void-and-return) + Q.2.4 (drawer-and-session)
- `canary-module-t-functional-decomposition.md` — sister card; T.1.6 (multi-company routing) + T.7.5 (drawer-session linkage) cross with N.5.4 + N.3
- `canary-module-r-functional-decomposition.md` — sister card; R.1.6 (workgroup template) + R.4.5 (PII via per-store profile slots) cross with N.5 + N.4.5
- `canary-module-f-functional-decomposition.md` — sister card; F.2.2 (per-store default tax) + F.5 (tokenization) cross with N.4.6 + N.2.4
- `canary-module-s-functional-decomposition.md` — sister card; S.1.3 (per-location item enrichment) cross with N's location identity
- `ncr-counterpoint-api-reference.md` — full Store / Station / DeviceConfig / Workgroup / Tokenize detail; "Store config field richness" section
- `ncr-counterpoint-endpoint-spine-map.md` — per-endpoint × CRDM × spine map for N family
- `ncr-counterpoint-rapid-pos-relationship.md` — per-store discount caps + drawer discipline mapping
- `garden-center-operating-reality.md` — multi-store regional chain context
- (CATz) `proof-cases/specialty-smb-counterpoint-solution-map.md` — N row = ● Full direct
- (CATz) `method/artifacts/module-functional-decomposition.md` — the artifact template this card follows

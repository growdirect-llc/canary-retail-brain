---
type: case-study
classification: internal-decision-record
date: 2026-04-25
status: completed-design
related-linear: GRO-560
related-sdd: docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md
methodology: IBM BCS IT Architecture Options (Morrisons pattern)
author: Geoffrey C. Lyle
---

# Case Study: Canary NCR Product-Line Decision — Architecture Options

## Executive Summary

NCR's POS portfolio is not a single thing. It is three product lines pointed at three different merchant populations, with three different API surfaces and three different vendor postures toward Canary as a third-party analytics layer on top. The decision in front of us — which line gets the first integration adapter — drives the entire NCR-side scaffolding: API surface, OAuth shape, event schema, sandbox path, and which merchant population we can land in 2026.

Three options evaluated below using the Morrisons option-evaluation frame. **Recommendation: Option B — Counterpoint first.** Counterpoint is the closest merchant-profile analog to Canary's existing Square sweet spot, the first concrete deployment target (a Boutique Home & Garden chain) already runs it, the friendly VAR channel (Bart Monahan / Rapid POS) is a Counterpoint reseller, the API documentation is publicly available on GitHub, and the access strategy routes through the customer license-holder rather than through NCR Voyix corporate — which sidesteps the structural problem that Voyix is a competitor for SMB analytics, not a partner.

**Sequence:** Counterpoint Q3 2026 (adapter MVP, Phase 0–1 already in flight under GRO-558) → Voyix/Silver Q2 2027 (revisit when installed base + API maturity catch up and the partnership posture is reassessed) → Aloha is a separate restaurant-vertical motion, not next-up on the retail roadmap.

---

## Strategic Context

The Canary perpetual-ledger substrate today ingests Square. Square is the proof case. The next move is the second adapter — and the choice of second adapter is the choice of merchant population for 2026–2027.

Three things shape the decision:

1. **A real customer is in front of us.** A Boutique Home & Garden chain, multi-store, runs NCR Counterpoint v8.5+. That is the first concrete deployment target for the second adapter, not a hypothetical.
2. **There is a friendly VAR channel.** Bart Monahan operates Rapid POS, which is a whitelabel Counterpoint reseller. His installed base runs Counterpoint underneath. A working relationship there is a distribution channel for the Counterpoint adapter.
3. **NCR Voyix corporate is a competitor, not a partner.** Per memory `project_ncr_voyix_is_competitor.md`, integration access strategy must route through the customer (license holder), not through an NCR partnership. Any product-line choice that requires NCR-Voyix-as-partner cooperation has structural friction we do not control.

The canonical positioning we have chosen for this season (per memory `project_canary_canonical_positioning.md`) is:

- **WHAT:** Multi-store merchandising and store ops for SMB, on top of the Counterpoint API backbone
- **WHO:** Rapid POS delivery experts
- **HOW:** Our method is CATz

That positioning constrains the option set. Aloha and Voyix would each force a different positioning narrative, and both narratives put us closer to NCR Voyix as a counterparty rather than further from it.

---

## Section 1: Business Target Each Option Addresses

Each option opens up a different US merchant population. The segment-sizing is rough, derived from public NCR Voyix segment disclosures + trade publication estimates; treat as order-of-magnitude.

### Option A — Aloha First (Restaurants)

- **Merchant profile:** Mid-size restaurant chains, quick-service, casual-dining. Multi-location operators are the sweet spot.
- **US installed base:** ~80,000 sites (per NCR Voyix investor materials; Aloha is the legacy Radiant restaurant POS line).
- **Vertical fit with Canary today:** **Low.** Restaurant operations (menu modifiers, check splits, server tip pools, kitchen display, table service) are a fundamentally different transaction shape than retail. The Q (Loss Prevention) rule catalog Canary has built for retail does not transfer cleanly — restaurant fraud patterns (comp abuse, void-and-revoid on server tabs, cash-tip skimming, refire abuse) are a different rule family.
- **Strategic read:** Big TAM, wrong shape. Pursuing Aloha first forks the product into two verticals before either is durable.

### Option B — Counterpoint First (Specialty Retail SMB)

- **Merchant profile:** Specialty retail SMB — garden centers, gun shops, food/wine, feed-and-tack, pet, sporting goods, hobby, gift, apparel. Single-store and small-chain operators.
- **US installed base:** ~6,000–14,000 sites across all Counterpoint VAR verticals; midpoint ~9,000 (per `Brain/wiki/rapid-pos-counterpoint-market-research-tam.md`). Primary garden-center subsegment ~700–1,800 stores, midpoint ~1,200.
- **Vertical fit with Canary today:** **High.** Specialty retail SMB is the same merchant shape as Canary's existing Square base — single-tender retail transactions with line items, customer-attached purchases, multi-store inventory, employee-driven loss patterns. Q rules are 80%+ portable; Module T/R/N/F slot in directly.
- **Strategic read:** Smaller TAM than Aloha, but it is the merchant population the platform is already shaped for, plus there is a real customer and a real VAR channel waiting.

### Option C — Voyix/Silver First (Modern SMB)

- **Merchant profile:** Modern API-first SMB. NCR's own play against Square + Shopify POS at the small end of the market.
- **US installed base:** Smallest of the three lines today. NCR Voyix does not break out Silver / Voyix-Commerce installed base explicitly in investor materials; trade-publication estimates put it well under 10,000 active SMB sites in the US.
- **Vertical fit with Canary today:** **Medium-High.** Modern API surface is the closest to Square's shape technically (REST + OAuth + webhooks). Merchant profile is the same shape as Square. But the partnership posture is the worst of the three options — Voyix corporate is the direct competitor, and integration access is gated by NCR partner programs that we do not currently have.
- **Strategic read:** Modern surface, smallest base, highest partnership friction. Strategic candidate for a later year when either the partnership posture changes or the installed base grows enough to justify a customer-routed integration play.

**Adoption success metric (chosen option):** First Counterpoint customer in production by end of Q3 2026, with Module T (transactions) + Module R (customer) + Module F (finance/tender) producing parity-quality detections to the Square baseline within 60 days of go-live. Second customer onboarded via the Bart / Rapid POS channel by end of Q4 2026.

---

## Section 2: Solution Overview (Architecture Sketches)

Each option implies a different adapter shape. The Counterpoint sketch below is the high-level shape only; full architecture detail lives in `docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md` §1.

### Option B — Counterpoint Adapter (Recommended)

```
┌────────────────────────────────┐         ┌──────────────────────────┐
│  Customer site (e.g. H&G chain)│         │  Canary infrastructure   │
│                                │         │                          │
│  ┌──────────────────────────┐  │         │  ┌────────────────────┐  │
│  │  NCR Counterpoint v8.5+  │  │         │  │  TSP Counterpoint  │  │
│  │  (Windows on-prem)       │  │         │  │     adapter        │  │
│  └────────────┬─────────────┘  │         │  └─────────┬──────────┘  │
│               │                │         │            │             │
│               ▼                │         │            ▼             │
│  ┌──────────────────────────┐  │ HTTPS   │  ┌────────────────────┐  │
│  │  Counterpoint REST API   │◄─┼─────────┼──┤  Polling / fetch   │  │
│  │  Server (.NET 4.5.2)     │  │ Basic+  │  └─────────┬──────────┘  │
│  │  Windows host, port 8889 │  │ APIKey  │            │             │
│  └──────────────────────────┘  │         │            ▼             │
│                                │         │  ┌────────────────────┐  │
└────────────────────────────────┘         │  │  CRDM (Postgres)   │  │
                                           │  └─────────┬──────────┘  │
                                           │            │             │
                                           │            ▼             │
                                           │  ┌────────────────────┐  │
                                           │  │  Q (Chirp) + Fox + │  │
                                           │  │  dashboards        │  │
                                           │  └────────────────────┘  │
                                           └──────────────────────────┘
```

- **Path:** Counterpoint REST API (customer-side, Windows, on-prem) → TSP Counterpoint adapter (Canary-side, polling) → CRDM (Postgres) → downstream Q/Fox/dashboards.
- **Auth:** HTTP Basic with `<company>.<username>:<password>` per Counterpoint company + APIKey header per request.
- **Ingress shape:** Polling-only. No webhooks (Counterpoint REST API does not push).
- **Multi-company:** One Canary tenant may map to multiple Counterpoint companies; resolved via `<company-alias>.<user>` auth prefix and a `counterpoint_company_alias` column on the CRDM tenant join.
- **Detail:** see SDD §1 (architecture), §3 (auth), §4 (CRDM alignment), §6 (per-module mappings).

### Option A — Aloha Adapter (Sketch)

```
┌─────────────────────────────┐        ┌──────────────────────────┐
│ Restaurant site (multi-loc) │        │  Canary infrastructure   │
│                             │        │                          │
│  ┌───────────────────────┐  │        │  ┌────────────────────┐  │
│  │  Aloha Restaurant POS │  │        │  │  TSP Aloha adapter │  │
│  │  (Radiant lineage)    │  │        │  │  (new)             │  │
│  └───────────┬───────────┘  │        │  └─────────┬──────────┘  │
│              │              │        │            │             │
│              ▼              │ HTTPS  │            ▼             │
│  ┌───────────────────────┐  │ OAuth  │  ┌────────────────────┐  │
│  │  Aloha Cloud API      │◄─┼────────┼──┤ Webhook + polling  │  │
│  │  (NCR partner gated)  │  │  + ?   │  └─────────┬──────────┘  │
│  └───────────────────────┘  │        │            │             │
└─────────────────────────────┘        │            ▼             │
                                       │  ┌────────────────────┐  │
                                       │  │  CRDM + new        │  │
                                       │  │  restaurant model  │  │
                                       │  │  (modifiers, check │  │
                                       │  │   splits, kitchen) │  │
                                       │  └─────────┬──────────┘  │
                                       │            │             │
                                       │            ▼             │
                                       │  ┌────────────────────┐  │
                                       │  │  Q rebuilt for     │  │
                                       │  │  restaurant fraud  │  │
                                       │  │  patterns          │  │
                                       │  └────────────────────┘  │
                                       └──────────────────────────┘
```

- **Auth:** OAuth (NCR-partner-gated, application credentials issued through partner program).
- **Ingress shape:** Webhooks where available + polling for backfill.
- **Event model burden:** Restaurant transaction shape requires net-new CRDM extensions — `Events.modifiers`, `Events.check_splits`, `Events.tip_pools`, `Workflows.kitchen_orders`. None of this exists in Canary today.
- **Q burden:** Rebuild detection rules around restaurant patterns (comp abuse, void-and-revoid on tabs, cash tip skim, refire abuse, ghost-server). Net-new rule family.

### Option C — Voyix/Silver Adapter (Sketch)

```
┌─────────────────────────────┐        ┌──────────────────────────┐
│ Modern SMB site             │        │  Canary infrastructure   │
│                             │        │                          │
│  ┌───────────────────────┐  │        │  ┌────────────────────┐  │
│  │  NCR Voyix / Silver   │  │        │  │  TSP Voyix adapter │  │
│  │  POS                  │  │        │  │  (new)             │  │
│  └───────────┬───────────┘  │        │  └─────────┬──────────┘  │
│              │              │        │            │             │
│              ▼              │ HTTPS  │            ▼             │
│  ┌───────────────────────┐  │ OAuth  │  ┌────────────────────┐  │
│  │  Voyix Cloud REST     │◄─┼────────┼──┤ Webhook-primary    │  │
│  │  (NCR partner gated)  │  │        │  └─────────┬──────────┘  │
│  └───────────────────────┘  │        │            │             │
└─────────────────────────────┘        │            ▼             │
                                       │  ┌────────────────────┐  │
                                       │  │  CRDM (existing    │  │
                                       │  │  retail shape OK)  │  │
                                       │  └─────────┬──────────┘  │
                                       │            │             │
                                       │            ▼             │
                                       │  ┌────────────────────┐  │
                                       │  │  Q (mostly         │  │
                                       │  │  portable from     │  │
                                       │  │  Square)           │  │
                                       │  └────────────────────┘  │
                                       └──────────────────────────┘
```

- **Auth:** OAuth, NCR-partner-gated.
- **Ingress shape:** Cloud-native REST + webhooks (closest to Square shape).
- **CRDM fit:** Existing retail event shape works — no net-new entities needed.
- **Adapter cost:** Lower than Aloha (no vertical mismatch), comparable to Counterpoint, but with high re-discovery cost because the Voyix API surface is not yet mapped in our corpus.
- **Partnership cost:** Highest of the three — direct competitor, partner program enrollment required.

---

## Section 3: Technical Fit (Modules Touched)

Canary has a 13-module spine (T R N A Q C D F J S P L W). Each option exercises a different subset of the spine and at different depth.

| Module | Option A — Aloha | Option B — Counterpoint | Option C — Voyix |
|---|---|---|---|
| **T (Transaction)** | Heavy rebuild (restaurant shape) | Direct map, full coverage | Direct map, full coverage |
| **R (Customer)** | Light (most restaurants don't capture customer at order) | Full coverage; B2B / multi-tier customers central in H&G | Full coverage; modern customer attach |
| **N (Device)** | Heavy (kitchen displays, KDS, server tablets new) | Full coverage; Store + Station + DeviceConfig endpoints | Full coverage; cloud-managed devices |
| **A (Asset)** | Out of scope first wave | Light (asset-flagged items) | Light (similar to Counterpoint) |
| **Q (Loss Prevention)** | **Net-new rule family** (restaurant patterns) | 80%+ portable from Square; H&G allow-list framework already drafted | Mostly portable from Square |
| **C (Commercial)** | Out of scope (restaurants rarely B2B) | **Full coverage** — H&G landscaper / contractor B2B is core | Light |
| **D (Distribution)** | Out of scope (single-site cooking) | Full coverage; multi-store transfers via InventoryLocations | Light (modern SMB rarely multi-store) |
| **F (Finance / Tender)** | Heavy (tip pools, server-bank, cash drops) | Full coverage; PayCode + GiftCard endpoints | Full coverage |
| **J (Forecast / Order)** | Out of scope first wave | Vendor + replenishment endpoints (some derived) | Light coverage in modern API |
| **S (Space / Range / Display)** | Net-new (menu / modifier hierarchy) | Full coverage; Item + Category + Serial endpoints | Full coverage |
| **P (Pricing / Promotion)** | Out of scope first wave | **Derived only** (no Counterpoint endpoint family for promotions) | Direct (modern API has dedicated promo surface) |
| **L (Labor / Workforce)** | Out of scope (Counterpoint has none either) | **Not sourceable from Counterpoint REST** — see SDD §6.12; product wedge under separate decision | Light or none — Voyix surface unconfirmed |
| **W (Work Execution)** | Out of scope | **Not sourceable from Counterpoint REST** — see SDD §6.13 | Unknown |

**Read of the table:**

- **Option B** lights up T, R, N, F, S as primary (Phase 1 priority modules) plus C, D as broad secondary. This matches Canary's current spine investment closely. The Counterpoint gap on L and W is real but is a separate product decision, not a blocker for Phase 1 (see SDD §6.12 / §6.13).
- **Option A** lights up T, R, N, F but in a fundamentally different shape. Module Q has to be rebuilt. Modules S and J fork into restaurant equivalents. Net-new spine work, not extension.
- **Option C** lights up the same modules as Counterpoint at a similar depth, with a slightly cleaner pricing/promotion story but a less explored API surface. The unknown is the largest entry on the line.

---

## Section 4: Integration Touchpoints (APIs, Auth, Sandbox, Docs)

| Touchpoint | Option A — Aloha | Option B — Counterpoint | Option C — Voyix |
|---|---|---|---|
| **API style** | REST (Aloha Cloud) + legacy SOAP for older deployments | REST (95 documented endpoints, v2.4) | REST + webhooks, modern shape |
| **Auth model** | OAuth via NCR partner credentials | HTTP Basic (`<company>.<user>:<pwd>`) + APIKey header per request | OAuth via NCR partner credentials |
| **Push vs. pull** | Webhook + polling | **Polling only** (no push) | Webhook-primary (closest to Square) |
| **Sandbox availability** | NCR-partner-gated; cost + enrollment process | Customer-license-gated (test instance on customer's Windows host) or VAR-provided lab (Bart's Rapid POS) | NCR-partner-gated |
| **Sandbox cost** | Partner-program tier-dependent | Effectively free if customer or VAR provides the lab; nonzero if Canary stands up its own Windows host | Partner-program tier-dependent |
| **Rate limits** | Published per partner tier | Per Counterpoint API server config; default 100/req batch, 1000 max | Modern cloud-typical (Square-like) |
| **Documentation accessibility** | NCR partner portal (gated; NDA-bound) | **Public on GitHub** at `github.com/NCRCounterpointAPI/APIGuide` | NCR partner portal (gated) |
| **OpenAPI spec** | Not public | **Derived spec already in repo** at `docs/sdds/canary/ncr-counterpoint-openapi.yaml` (validates; 71 paths, 95 ops, 49 schemas) | Not public |
| **Customer host requirement** | Cloud (no customer infra) | **Per-customer Windows host** (.NET 4.5.2, port 8889) | Cloud (no customer infra) |
| **License gating** | NCR partnership | Customer's `registration.ini` API user option (paid add-on) | NCR partnership |

**The Counterpoint integration is deepest in our corpus.** SDD `docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md` covers architecture, auth, CRDM mapping, and per-module endpoints. The connection runbook (`Brain/wiki/ncr-counterpoint-connection-runbook.md`) covers stand-up. The OpenAPI spec validates clean. Aloha and Voyix have none of this groundwork — both options would start with a corpus-extraction pass before any adapter code.

**The access posture is the load-bearing difference.** Counterpoint integration is per-customer (the customer's license, the customer's APIKey, the customer's Windows host). NCR Voyix corporate is not in the loop. Aloha and Voyix both put NCR Voyix corporate in the loop as the credential issuer — a structural dependency on a competitor.

---

## Section 5: Risk Profile

### Option B — Counterpoint Risks

| Risk | Severity | Mitigation | Residual |
|---|---|---|---|
| **Per-customer Windows host requirement** | Medium | Document host requirements in onboarding runbook; offer Canary-edge-box option for customers without infra; Bart/Rapid POS may host on customer's behalf | Medium-Low |
| **`registration.ini` API user option is paid add-on** | Medium-High | Customer-side gate; surface as a precondition during sales conversation; for VAR-channel deals, Bart can package it | Medium |
| **NCR Voyix-as-competitor framing** | Medium | Access strategy routes through customer license-holder, not partnership; communications stay neutral (data access / connector framing, not LP/analytics) | Low (structural mitigation) |
| **Multi-company per tenant complexity** | Medium | CRDM `tenant_id` × `counterpoint_company_alias` join; SDD §7.6 documents the model | Low |
| **v2.4 breaking-ish change on `USR_ENTD_PRC` price-override semantics** | Low-Medium | Adapter version detection via `DB_CTL.DB_VER`; per-version branching where required; SDD §7.5 documents | Low |
| **Polling-only ingress (no push)** | Medium | Default 1-minute poll cadence; configurable per endpoint; idempotent upserts on Counterpoint primary keys | Low |
| **Modules L + W have no Counterpoint coverage** | Medium-High | Documented in SDD §6.12 / §6.13; product-strategic decision parked under separate dispatch (`project_canary_native_labor_module_opportunity.md`); not a Phase 1 blocker | Medium (acknowledged gap) |

### Option A — Aloha Risks

| Risk | Severity | Mitigation | Residual |
|---|---|---|---|
| **NCR partnership gating** | High | Enroll in NCR partner program; partnership-tier negotiation | Medium-High (NCR-corporate-controlled) |
| **Vertical mismatch** | **Very High** | Restaurant Q rules are a net-new family; Modules S/J fork; CRDM extensions for modifiers / check splits / tip pools | High (architectural cost) |
| **Sandbox cost** | Medium | Partner-tier dependent; budget allocation required | Medium |
| **Documentation gated** | Medium | NDA-bound; corpus extraction would require partner access | Medium |
| **No friendly VAR channel** | High | No Bart-equivalent for Aloha in our network | High (distribution gap) |
| **First-customer absence** | High | No concrete Aloha customer in front of us | High (no anchor deployment) |

### Option C — Voyix Risks

| Risk | Severity | Mitigation | Residual |
|---|---|---|---|
| **NCR-direct-competition friction** | **Very High** | Voyix is the SMB analytics competitor; partner-program access negotiation is a competitor relationship | High (structural; cannot fully mitigate) |
| **Smallest installed base today** | High | Wait for installed-base growth; revisit Q2 2027 | Medium (time-mitigated) |
| **API surface still maturing** | Medium-High | Re-discovery cost on every endpoint; corpus extraction needed | Medium-High |
| **Sandbox + partner-program cost** | Medium | Same partner-program enrollment as Aloha | Medium |
| **No friendly VAR channel** | High | No Bart-equivalent; NCR Voyix sells direct | High (distribution gap) |
| **Documentation gated** | Medium | NDA-bound | Medium |
| **First-customer absence** | High | No concrete Voyix customer in front of us | High (no anchor deployment) |

**Comparative read:** Counterpoint's risks are operational and bounded (Windows host, license gate, multi-company complexity) and have either documented mitigations or accepted residuals. Aloha and Voyix both carry **structural risks** (NCR-corporate gating, missing distribution channel, missing first customer) that Canary cannot mitigate from its side.

---

## Section 6: Cost & Timeline

### Effort Estimate per Option

| Component | Option A — Aloha | Option B — Counterpoint | Option C — Voyix |
|---|---|---|---|
| API corpus extraction + OpenAPI derivation | 4 eng-weeks (NCR partner doc; gated) | **0 eng-weeks (already complete; in repo)** | 4 eng-weeks (gated; NDA-bound) |
| Adapter framework + auth + ingress | 6 eng-weeks (OAuth flow + webhook + polling) | 4 eng-weeks (Basic + APIKey + polling) | 4 eng-weeks (OAuth + webhook) |
| CRDM mapping + per-module schema | 8 eng-weeks (net-new restaurant entities) | 3 eng-weeks (extends existing retail shape) | 3 eng-weeks (extends existing retail shape) |
| Phase 1 priority modules (T R F N + restaurant equivalents) | 12 eng-weeks (rule rebuild + new shapes) | 4 eng-weeks (Phase 1 dispatch already drafted) | 5 eng-weeks (re-discovery on each) |
| Q rule porting + new pattern catalog | 10 eng-weeks (net-new restaurant Q rules) | 2 eng-weeks (mostly portable; H&G allow-list ready) | 3 eng-weeks (mostly portable from Square) |
| Catalog modules (P, S) | 8 eng-weeks (menu / modifier hierarchy) | 3 eng-weeks (Item + Category endpoints) | 3 eng-weeks |
| Operations modules (D, J) | Out of scope first wave | 3 eng-weeks | 2 eng-weeks |
| Tertiary modules (A, C) | Out of scope first wave | 2 eng-weeks | 1 eng-week |
| Cutover playbook + monitoring | 4 eng-weeks | 2 eng-weeks (Phase 5 dispatch already drafted) | 3 eng-weeks |
| Testing + first-customer pilot | 6 eng-weeks | 3 eng-weeks (Boutique H&G chain ready) | 6 eng-weeks (no anchor customer) |
| **Total adapter eng-weeks** | **~58** | **~26** | **~34** |
| **Calendar (assuming 1.5–2 FTE)** | 6–8 months | **3–4 months** | 4–5 months |

**The Counterpoint estimate is anchored.** Phase 0 (substrate) is already in flight under GRO-558. The Phase 1–5 dispatches are already drafted (`Brain/dispatches/2026-04-25-ncr-counterpoint-*.md`). The OpenAPI spec validates. The connection runbook exists. Bart's Rapid POS lab is a candidate sandbox path. The Boutique H&G chain is a real first deployment.

The Aloha and Voyix estimates carry significant uncertainty — every line above the "first customer" row would need partner-program enrollment, documentation extraction, and net-new design work before adapter development could start.

### Phasing for Counterpoint (Recommended)

| Quarter | Phase | Modules | Status |
|---|---|---|---|
| **Q3 2026 (in flight)** | Phase 0a + 0b + 0c | TSP source-aware substrate + Counterpoint adapter shell | 0a complete; 0b in progress; 0c not started — see SDD §8 + Phase 0 strategic refinement |
| **Q3 2026** | Phase 1 | T, R, F, N (L deferred per SDD §6.12) | Dispatch drafted: `Brain/dispatches/2026-04-25-ncr-counterpoint-priority-modules.md` |
| **Q4 2026** | Phase 2 | P (derived), S (catalog) — H&G-critical | Dispatch drafted: `2026-04-25-ncr-counterpoint-catalog-modules.md` |
| **Q1 2027** | Phase 3 | D, J (W deferred per SDD §6.13) | Dispatch drafted: `2026-04-25-ncr-counterpoint-operations-modules.md` |
| **Q2 2027** | Phase 4 | A, C, Q (Q last because it consumes earlier-phase outputs) | Dispatch drafted: `2026-04-25-ncr-counterpoint-tertiary-modules.md` |
| **Q2 2027** | Phase 5 | Cutover + monitoring + Boutique H&G first deployment | Dispatch drafted: `2026-04-25-ncr-counterpoint-cutover.md` |

---

## Section 7: Advantages & Disadvantages per Option

### Option A — Aloha: Advantages

1. **Largest installed base** of the three (~80,000 US sites). Big TAM.
2. **Single-vertical focus** — restaurants are a coherent segment with shared operational vocabulary.
3. **Mature product** — Aloha has been in market since the Radiant era; vendor APIs are stable.
4. **Distinct competitive lane** — restaurant-vertical analytics is a different competitive set than retail (Toast, Sapaad, Restaurant365, etc.); Canary would be a new entrant rather than a Voyix competitor.

### Option A — Aloha: Disadvantages

1. **Wrong vertical for the existing platform.** Q rules, CRDM event shape, Module S taxonomy all need restaurant equivalents. ~58 eng-weeks vs ~26 for Counterpoint.
2. **No first customer in front of us.** No Aloha-running merchant in the network; no anchor deployment.
3. **No friendly VAR channel** for Aloha equivalent to Bart for Counterpoint.
4. **NCR partnership-program gating** for documentation, sandbox, and credentials.
5. **Forks the product roadmap** — committing to Aloha first creates a parallel restaurant-vertical product line that competes for engineering attention with the retail base.
6. **Doesn't satisfy the canonical positioning** ("multi-store merchandising and store ops for SMB on the Counterpoint API backbone") — would require renarrating the company.

### Option B — Counterpoint: Advantages

1. **Concrete first deployment** — Boutique H&G chain is real, multi-store, ready.
2. **Friendly VAR channel** — Bart Monahan / Rapid POS as distribution + lab + customer pipeline.
3. **Public documentation** — `github.com/NCRCounterpointAPI/APIGuide` is open; OpenAPI spec already derived and validates clean.
4. **Access strategy through customer, not NCR Voyix corporate** — sidesteps the structural competitor problem.
5. **Vertical fit with Canary today is high** — specialty retail SMB is the same shape as the Square base; Q rules are 80%+ portable; spine modules T/R/N/F slot in directly.
6. **Phase 0 substrate work already in flight** under GRO-558; SDD + dispatches for all five phases already drafted.
7. **Canonical positioning already aligned** ("Counterpoint API backbone" is the chosen narrative).

### Option B — Counterpoint: Disadvantages

1. **Smaller installed base** than Aloha (~9,000 vs ~80,000 sites). Smaller TAM ceiling.
2. **Per-customer Windows host requirement** — every deployment needs a Windows machine running Counterpoint API server.
3. **Multi-company complexity** — one customer may have multiple Counterpoint companies; CRDM accommodates but adds modeling cost.
4. **Polling only, no webhooks** — slightly higher latency vs push-based ingress.
5. **`registration.ini` API user option is a paid add-on** — customer-side cost gate.
6. **Modules L (Labor) and W (Work Execution) cannot be sourced from Counterpoint REST** — real coverage gap; product-strategic decision parked.

### Option C — Voyix: Advantages

1. **Modern API surface** — REST + OAuth + webhooks; closest to Square's shape technically.
2. **Strategic positioning** — Voyix is the line NCR is investing in; growing share over time.
3. **CRDM fit is direct** — no net-new entity work needed.
4. **Cloud-native** — no per-customer Windows host requirement.
5. **Q rules mostly portable from Square.**

### Option C — Voyix: Disadvantages

1. **NCR Voyix is the direct competitor** for SMB analytics. Highest partnership friction of the three.
2. **Smallest installed base today** (well under 10k US SMB sites).
3. **API surface not yet mapped** in our corpus — re-discovery cost on every endpoint.
4. **No friendly VAR channel** — Voyix sells direct.
5. **No first customer in front of us.**
6. **Partnership posture is the load-bearing risk** and is not under our control — NCR Voyix decides whether and on what terms to grant integration access.

---

## Section 8: Summary, Comparison, Recommendation

### Comparison Across Options

| Dimension | Option A — Aloha | Option B — Counterpoint | Option C — Voyix |
|---|---|---|---|
| **Adapter eng-weeks** | ~58 | **~26** | ~34 |
| **Calendar to first customer** | 6–8 months | **3–4 months** | 4–5 months |
| **US installed base** | ~80,000 | ~9,000 (specialty SMB) | <10,000 (modern SMB) |
| **NCR-corporate friction** | High | **Low (customer-routed)** | Very High (direct competitor) |
| **Vertical fit with current platform** | Low (restaurants ≠ retail) | **High (specialty retail SMB)** | Medium-High |
| **Q-rule portability from Square** | ~10% (rebuild) | **80%+ (port)** | ~80%+ (port) |
| **Public documentation** | No (NCR partner gated) | **Yes (GitHub, public)** | No (NCR partner gated) |
| **OpenAPI spec available** | No | **Yes (in repo, validates)** | No |
| **First customer in front of us** | No | **Yes (Boutique H&G chain)** | No |
| **Friendly VAR channel** | No | **Yes (Bart / Rapid POS)** | No |
| **Canonical positioning alignment** | Forces renarration | **Already aligned** | Forces renarration |
| **Phase 0 substrate already in flight** | No | **Yes (GRO-558)** | No |

### Heat-Map Summary (Axes: Vertical Fit × NCR-Corporate Friction)

```
              LOW FRICTION    HIGH FRICTION
              ◄──────────────►

HIGH FIT      Option B ✓
              (Counterpoint)
              ★★★★★

                              Option C
                              (Voyix)
                              ★★☆☆☆

LOW FIT                       Option A
                              (Aloha)
                              ★★★☆☆

Vertical fit with existing Canary platform:
  Option A: ★☆☆ (restaurants — wrong shape)
  Option B: ★★★★★ (specialty retail SMB — same shape as Square base)
  Option C: ★★★★☆ (modern SMB — same shape, less mapped)

NCR-corporate friction (lower is better):
  Option A: ★★★ (NCR-partner-gated for credentials + docs)
  Option B: ★★★★★ (customer-routed access; NCR not in the loop)
  Option C: ★★ (direct-competitor partnership; structural friction)

First-customer readiness:
  Option A: 0 customers
  Option B: 1 customer ready (Boutique H&G chain)
  Option C: 0 customers
```

### Recommendation

**CHOSEN: Option B — Counterpoint first.**

**Rationale:**

1. **A real customer is in front of us.** The Boutique H&G chain runs Counterpoint, multi-store, ready to deploy. The other two options have no anchor deployment.
2. **The friendly VAR channel is Counterpoint.** Bart Monahan / Rapid POS = Counterpoint reseller. That is distribution, lab access, and customer pipeline rolled together. No equivalent exists for Aloha or Voyix.
3. **The canonical positioning is already Counterpoint-shaped.** "Multi-store merchandising and store ops for SMB on the Counterpoint API backbone" is the narrative we have committed to externally and internally. Aloha and Voyix would force a re-narration.
4. **The vertical fit is direct.** Specialty retail SMB is the same merchant shape as the Square base. Q rules port. Spine modules slot in. ~26 adapter eng-weeks vs ~58 for Aloha.
5. **The access strategy avoids the NCR-Voyix-as-competitor problem.** Counterpoint integration is customer-routed (license, APIKey, Windows host all customer-side). Aloha and Voyix both put NCR Voyix corporate in the loop as gatekeeper.
6. **The substrate work is already in flight.** Phase 0a complete, 0b in progress, 0c queued. SDD, OpenAPI spec, runbook, all five phase dispatches drafted. Picking another option means throwing this work away.
7. **The TAM is sufficient for 2026–2027.** ~9,000 US specialty SMB sites is enough merchant population to anchor a vertical product motion through 2027. Aloha's ~80k is not the right population, and Voyix's <10k is the same TAM with worse access posture.

### First 90 Days (Counterpoint)

This work is already underway under GRO-558 + the Phase 0 dispatch package. Restated here for the ADR record:

1. **Weeks 1–2:** Complete Phase 0b — register `'counterpoint'` source, extend CHECK constraints, multi-company decision, source-aware dispatch tables, per-source schema-drift fingerprinting.
2. **Weeks 3–4:** Phase 0c — Counterpoint adapter shell, polling worker, Counterpoint validators, fixture suite. Stand up Bart-provided lab or Canary edge box.
3. **Weeks 5–6:** Phase 1 priority modules — T (transactions via `/Documents`), R (customer via `/Customers`), F (tender via PayCode + GiftCard), N (devices via Store + Station + DeviceConfig). L deferred per SDD §6.12.
4. **Weeks 7–8:** First-customer integration testing against Boutique H&G chain; Q rules ported and validated against H&G allow-list framework (`Brain/wiki/canary-module-q-counterpoint-rule-catalog.md`).
5. **Weeks 9–10:** Phase 2 catalog modules — P (derived from Item + CustomerControl), S (Item + Category + Serial + Image endpoints). H&G-specific custom-field handling (mix-and-match flat tracking, plant attributes).
6. **Weeks 11–12:** First Boutique H&G production deployment; monitoring + alerting per SDD §7.4.

### Decision Gates

- **Post-Phase-0 review (end Q3 2026):** Adapter shell stable, Counterpoint API connection reliable, first-customer Phase 1 modules producing parity-quality detections to Square baseline. Proceed to Phase 2 catalog modules.
- **Post-MVP review (end Q4 2026):** First production customer (Boutique H&G chain) running stable; second customer onboarded via Bart / Rapid POS channel. Validate adoption rate and Q-rule portability metrics.
- **Voyix evaluation gate (Q2 2027):** Re-evaluate Option C. Has Voyix installed base grown? Has the partnership posture changed? Are there customer requests routing through Counterpoint customers asking for Voyix coverage? If yes, scope a Voyix adapter as Phase 6.
- **Aloha evaluation gate (Q4 2027 or later):** Aloha is a separate restaurant-vertical product motion, not next-up on the retail roadmap. Re-evaluate only when (a) restaurant-vertical Q rule family is independently funded or (b) a concrete Aloha customer enters the pipeline.

---

## Appendix: Glossary

| Term | Definition |
|---|---|
| **Aloha** | NCR's restaurant POS line, originating from the Radiant Systems acquisition. Large installed base in mid-size restaurant chains, quick-service, casual-dining. Distinct vertical from retail. |
| **Counterpoint** | NCR's specialty retail POS for SMB. Windows-based, on-premise. REST API documented publicly at `github.com/NCRCounterpointAPI/APIGuide`. Strong in garden, gun, food/wine, feed-and-tack, pet, sporting, hobby, gift, apparel verticals. |
| **CounterPro** | Cloud-hosted variant of Counterpoint promoted by NCR Voyix. Same conceptual product line; deployment topology differs. |
| **NCR Voyix** | The corporate entity that owns Aloha + Counterpoint + Silver/Voyix POS lines after the NCR Atleos / NCR Voyix split. Direct competitor to Canary in the SMB-analytics layer; integration access strategy must therefore route through customers, not partnerships. |
| **Rapid POS** | Whitelabel Counterpoint reseller operated by Bart Monahan. Friendly VAR channel for Canary. Customer base runs Counterpoint underneath the Rapid POS branding. |
| **Silver** | NCR's earlier modern-SMB POS line, predecessor to current Voyix-Commerce SMB offerings. |
| **TSP** | Transaction Stream Pipeline — Canary's Module T ingress + seal + parse + merkle + detect pipeline. The adapter for any new POS plugs in here. |
| **Voyix (POS line)** | NCR's modern API-first SMB POS. Smaller installed base than Aloha or Counterpoint today; positioned by NCR Voyix as the growth play against Square + Shopify POS. |

---

## Related

- `docs/sdds/canary/ncr-counterpoint-retail-spine-integration.md` — full Counterpoint SDD (architecture, auth, CRDM mapping, per-module endpoints)
- `docs/sdds/canary/ncr-counterpoint-openapi.yaml` — derived OpenAPI 3.0 spec (validates; 71 paths, 95 ops, 49 schemas)
- `Brain/wiki/ncr-counterpoint-api-reference.md` — endpoint catalog overview
- `Brain/wiki/ncr-counterpoint-phase-0-context-brief.md` — strategic context + Phase 0 handoff brief
- `Brain/wiki/ncr-counterpoint-endpoint-spine-map.md` — per-endpoint × CRDM × spine table
- `Brain/wiki/ncr-counterpoint-connection-runbook.md` — Windows-host stand-up runbook
- `Brain/wiki/canary-tsp-pipeline.md` — current TSP architecture (the adapter plugs into this)
- `Brain/wiki/rapid-pos-counterpoint-market-research-tam.md` — TAM estimates for Counterpoint specialty SMB
- `Brain/wiki/canary-module-q-counterpoint-rule-catalog.md` — 23 Counterpoint-substrate-aware Q rules with H&G allow-list framework
- `Brain/wiki/dispatch-coordination-protocol.md` — protocol this ADR participates in
- `Brain/wiki/canary-architecture-decisions-index.md` — decisions index where this ADR is registered
- `Canary-Retail-Brain/case-studies/canary-iot-vendor-strategy.md` — sibling ADR using the same Morrisons frame
- `Canary-Retail-Brain/case-studies/canary-finance-architecture-options.md` — sibling ADR using the same Morrisons frame
- `Canary-Retail-Brain/modules/T-transaction-pipeline.md` — Module T (the adapter pattern reference)

---

## Conclusion

Canary's NCR-side scaffolding is shaped to **Counterpoint**. The Q3 2026 deliverable is a working Counterpoint adapter, plugged into the source-aware TSP substrate that GRO-558 is building this week, sufficient to onboard the Boutique Home & Garden chain as the anchor first deployment. Phase 1 priority modules (T, R, F, N) ship in Q3; catalog modules (P, S) in Q4; operations (D, J) in Q1 2027; tertiary (A, C, Q) and cutover playbook in Q2 2027.

The Counterpoint choice is not a forever choice — it is the first slot. **Voyix gets a re-evaluation gate in Q2 2027** when the installed base is larger and the partnership posture can be reassessed. Aloha is a separate restaurant-vertical motion, not on the immediate roadmap; re-evaluate when either restaurant-vertical Q-rule investment is independently funded or a concrete Aloha customer enters the pipeline.

The structural reason Counterpoint wins is that it routes around the NCR-Voyix-as-competitor problem. Customer-license-holder access strategy, friendly VAR channel via Rapid POS, public documentation, and a real first customer all point the same direction. The other two options each require NCR Voyix corporate as a counterparty, which is a structural friction Canary cannot mitigate from its side of the table.

**Ship Counterpoint adapter MVP in Q3 2026. Anchor on Boutique H&G chain. Distribute through Bart / Rapid POS. Revisit Voyix in Q2 2027. Defer Aloha as a separate vertical motion.**

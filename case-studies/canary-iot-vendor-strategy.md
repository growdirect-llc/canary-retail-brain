---
type: case-study
classification: internal-decision-record
date: 2026-04-24
status: completed-design
related-linear: GRO-546
related-sdd: satoshi-precision-operating-model.md
methodology: IBM BCS IT Architecture Options (Morrisons pattern)
author: Geoffrey C. Lyle
---

# Case Study: Canary IoT Vendor Strategy — Architecture Options

## Executive Summary

Canary is at an inflection point. The perpetual-ledger substrate now encompasses not just transactions (T) but inventory movements (D), cost events (C/F), and labor time-entries (L). The next wave of perpetual-ledger movement sources is IoT: foot traffic (door counters), shelf state (RFID sensors), dwell-and-flow (in-store positioning), cold-chain (temperature probes), and equipment health (IoT devices). The decision: which vendors does Canary integrate with first, and under what implementation route?

Three options evaluated below using the Morrisons option-evaluation frame. **Recommendation: Option C (Multi-Vendor Adapter Framework — BYOI with Typed Integration)** — lowest cost, broadest market entry, merchant ownership of vendor relationships, fastest payoff on the perpetual-ledger vision.

**The Choice:** Option C lands at `multi-route` (per vendor, per merchant). Each merchant chooses which IoT vendors they bring (BYOI — Bring Your Own IoT). Canary provides a typed adapter framework. Merchant brings Density door counter, Impinj RFID, Verkada cameras, monnit temperature probes, or any new vendor. Canary ingests via the adapter; perpetual movements flow to the ledger; merchant retains vendor relationship, contract, and margin. Canary owns the ledger surface; merchant owns the hardware and vendor management.

**Install state — staged migration framing.** Per [[../platform/perpetual-vs-period-boundary|Perpetual-vs-Period Boundary]], Option C lands the merchant at `cutover_status: parallel-observer` for IoT at install. Canary's perpetual movement layer reads every door-count event, every shelf-state change, every dwell signal, and produces perpetual observations. The merchant's existing tools (legacy POS inventory, merchandising system, traffic-analysis tool) keep operating unchanged. Both are computed in parallel; no forced cutover. As trust builds and IoT signal becomes critical to operations, merchants can elect to cutover modules (e.g., "use Canary's foot-traffic forecast instead of our legacy system's headcount estimate").

---

## Business Context: Satoshi-Precision Operating Model

The [[../platform/satoshi-precision-operating-model|Satoshi-Precision Operating Model]] establishes the strategic vision: every operational event — from POS transaction through inventory movement through labor time-entry to environmental sensor reading — becomes an immutable event on the perpetual ledger. IoT is the next layer of that vision.

Current perpetual-ledger sources (v1–v2):
- **T (Transaction):** Every POS sale, refund, void (6+ million events/month for a 50-store chain)
- **D (Distribution):** Every receipt, transfer, RTV, adjustment, cycle-count
- **L (Labor):** Every clock in/out, break, absence
- **C/F (Commercial/Finance):** Cost updates, supplier events

Future perpetual-ledger sources (v3+):
- **IoT foot traffic (doors):** Real-time foot-count at entry/exit + peak-time analysis
- **IoT shelf-state (RFID):** Shelf occupation per item per location, stockout detection, on-shelf price compliance
- **IoT dwell-and-flow (video/positioning):** Customer dwell time per zone, cross-shopping patterns, bottleneck detection
- **IoT cold-chain (temperature):** Equipment temperature, alarm events, product-safety compliance
- **IoT equipment health:** POS uptime, refrigerator status, freezer function, network connectivity

Each new IoT source is a movement type on the perpetual ledger. The Morrisons frame below evaluates how to establish vendor partnerships that maximize adoption, control cost, and preserve merchant choice.

---

## Section 1: Business Target This Option Addresses

**Merchant IoT adoption target (by 2027 end):**

- **Segment 1 — "Already Have IoT"** (~15% of SMB base): Merchants who already deployed Density door counters, Impinj shelf RFID, or Verkada cameras. Target: "Let's connect what you already own to Canary's ledger without replacing your vendor."
- **Segment 2 — "Plan to Deploy"** (~35% of SMB base): Merchants interested in foot-traffic analysis, shrink-reduction analytics, or labor-productivity tracking. Target: "Choose your vendor; Canary connects it."
- **Segment 3 — "Not Committed"** (~50% of SMB base): Merchants with no IoT strategy yet. Target: "IoT ROI is clear once you see foot-traffic + shrink correlation; we'll guide the conversation once you're ready."

**Adoption success metric:** Canary is selected as the integration substrate for IoT (not the vendor). Merchant's vendor choice is preserved. Canary's margin is the adapter integration, not the hardware resale.

---

## Section 2: Solution Overview (Architecture Sketch)

### Option C — Multi-Vendor Adapter Framework (BYOI Model)

```
┌────────────────────────────────────────────────────────────┐
│  Merchant (SMB)                                            │
│                                                            │
│  ┌─────────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐   │
│  │  Density    │ │  Impinj  │ │ Verkada │ │ monnit  │   │
│  │  Counters   │ │  RFID    │ │ Cameras │ │ Temp    │   │
│  │  (BYOI)     │ │  (BYOI)  │ │ (BYOI)  │ │ (BYOI)  │   │
│  └─────┬───────┘ └────┬─────┘ └────┬────┘ └────┬────┘   │
│        │              │            │           │         │
│  ┌─────▼──────────────▼────────────▼───────────▼─────┐   │
│  │  Canary IoT Adapter Framework                  │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │ TypedIoTEventSchema                     │   │   │
│  │  │  • DoorCount { timestamp, location,    │   │   │
│  │  │              entry, exit, nPeople }    │   │   │
│  │  │  • ShelfState { location, item_id,     │   │   │
│  │  │               present, quantity }      │   │   │
│  │  │  • DwellEvent { zone, duration,        │   │   │
│  │  │              customer_segment }        │   │   │
│  │  │  • TemperatureAlert { device,          │   │   │
│  │  │                    temp, threshold }   │   │   │
│  │  │  • EquipmentHealth { device, status }  │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  │                                                 │   │
│  │  Vendor Adapters (plug-in pattern)            │   │
│  │  ├─ density_adapter.py                        │   │
│  │  ├─ impinj_adapter.py                         │   │
│  │  ├─ verkada_adapter.py                        │   │
│  │  ├─ monnit_adapter.py                         │   │
│  │  └─ [future vendor adapters...]              │   │
│  │                                                 │   │
│  │  ┌────────────────────────────────────────┐   │   │
│  │  │ Perpetual-Ledger Publisher             │   │   │
│  │  │  → IoT Events → Stock Ledger           │   │   │
│  │  │  → Movement types: foot_traffic_event  │   │   │
│  │  │                   shelf_state_event    │   │   │
│  │  │                   equipment_event      │   │   │
│  │  └────────────────────────────────────────┘   │   │
│  └───────────────────────────────────────────────┘   │
│                       │                              │
│     ┌─────────────────▼──────────────────┐           │
│     │  Canary Stock Ledger               │           │
│     │  (Perpetual Movement Publisher)    │           │
│     │                                    │           │
│     │  foot_traffic_event                │           │
│     │  shelf_state_event                 │           │
│     │  equipment_event                   │           │
│     │  → VSM diagnostic queries          │           │
│     │  → Forecast + replenishment input  │           │
│     │  → Space + labor optimization      │           │
│     └────────────────────────────────────┘           │
└────────────────────────────────────────────────────────┘
```

**Key design principle:** Merchant owns IoT vendor relationship. Canary provides the contract (adapter pattern) between vendor's API and Canary's perpetual ledger. Each new vendor is a new adapter module. Merchant has full control over which vendors are added, when, and at what cost.

---

## Section 3: Technical Fit (Modules Touched)

### Which Canary Modules Extend With IoT

| Module | Extension | Leverage | Status |
|---|---|---|---|
| **T (Transaction)** | Foot-traffic events enrich transaction stream (peak-time sales correlation) | Read foot-count; correlate to transaction spikes | Existing hooks in VSM |
| **D (Distribution)** | Shelf-state events validate on-hand accuracy (stockout alerts, over-stock warnings) | Read RFID shelf state; compare to ledger SOH | New: RFID integration point |
| **J (Forecast & Order)** | Foot traffic + dwell-and-flow input to demand forecast; stockout alerts feed replenishment | Read foot-count + dwell; input to ML demand model | New: IoT signal to forecast engine |
| **S (Space, Range, Display)** | Shelf-state RFID + camera validation of planogram compliance; stockout automation | Read RFID occupancy; validate planogram position occupation | New: IoT validation layer |
| **L (Labor & Workforce)** | Foot traffic + zone dwell input to labor scheduling optimization | Read foot-traffic per hour + zone dwell; input to schedule-optimization algorithm | New: IoT signal to scheduling |
| **P (Pricing & Promotion)** | On-shelf price-label compliance via camera vision; markdown velocity via dwell | Read camera shelf images; compare displayed price to list; dwell patterns | New: camera integration for pricing |
| **Q (Loss Prevention)** | Equipment-health alerts (fridge/freezer failures, cash-drawer tampering), stockout investigations | Read equipment status; alert on anomalies | New: IoT alert routing to Q |
| **W (Work Execution)** | Cross-domain exception detection includes IoT anomalies (shelf vacancy, equipment failure) | Read all IoT exception signals; aggregate with other domain signals | New: W subscribes to IoT exceptions |

**Impact:** IoT extends the perpetual ledger's observability to the physical store. Forecast, labor scheduling, space optimization, and loss prevention all improve with real-time environmental signal.

---

## Section 4: Integration Touchpoints (APIs, Event Schema, Credentials)

### Adapter Pattern

Each vendor integration is an adapter module: Vendor API → TypedIoTEventSchema → Canary Ledger.

**Vendor Adapter Structure (Template):**

```
canary-iot/adapters/{vendor_name}_adapter.py

class {VendorName}Adapter(IotAdapter):
  def __init__(self, merchant_id, vendor_api_key, vendor_api_secret):
    self.merchant_id = merchant_id
    self.client = vendor_sdk.Client(api_key, api_secret)
    
  def subscribe_events(self):
    # Connect to vendor webhook or polling endpoint
    
  def transform_event(self, vendor_event) -> TypedIoTEvent:
    # Vendor-specific payload → TypedIoTEventSchema
    # Timestamp normalization, coordinate mapping, unit conversion
    
  def publish_ledger_movement(self, typed_event) -> LedgerMovement:
    # TypedIoTEvent → Stock Ledger movement verb
    # foot_traffic_event, shelf_state_event, equipment_event
```

**Typed Event Schema (OpenAPI / Pydantic):**

```python
class DoorCountEvent(TypedIoTEvent):
  timestamp: datetime
  merchant_id: UUID
  location_id: UUID
  entry_count: int
  exit_count: int
  npeople_in_store: int
  confidence: float  # vendor-provided confidence
  
class ShelfStateEvent(TypedIoTEvent):
  timestamp: datetime
  merchant_id: UUID
  location_id: UUID
  zone_id: str  # planogram zone
  item_id: str  # SKU
  present: bool
  quantity: int (if measurable)
  confidence: float
  
class TemperatureEvent(TypedIoTEvent):
  timestamp: datetime
  merchant_id: UUID
  location_id: UUID
  device_id: str  # fridge/freezer identifier
  temperature_c: float
  threshold_min: float
  threshold_max: float
  alert: bool
```

### Integration Touchpoints

| Touchpoint | Mechanism | Ownership |
|---|---|---|
| **Vendor OAuth / API Key** | Each merchant provides vendor credentials to Canary (e.g., Density API key, Impinj RFID reader credentials). Canary stores securely (encrypted vault). | Merchant owns vendor relationship; Canary stores credentials with encryption at rest + rotate tokens per best practice. |
| **Webhook vs. Polling** | Vendor chooses: Density supports webhooks; Impinj polling; Verkada webhooks. Adapter handles both patterns. | Adapter pattern abstraction; vendor differences are encapsulated. |
| **Coordinate & Unit Normalization** | Vendor proprietary coordinates (Verkada uses pixel coordinates; Density uses lat/long) → Canary zone/location canonical. | Adapter responsible for mapping. |
| **Frequency & Latency** | Density: 1 event per minute (door counts). Impinj: 1 event per 5 seconds (shelf reads). Verkada: continuous video (events on movement). Canary ingests at vendor frequency; ledger snapshot is per-minute. | Adapter buffers; Canary aggregates to 1-minute ledger snapshots to match T (Transaction Pipeline) granularity. |
| **Authentication at Merchant Install** | Merchant provides vendor API credentials during onboarding. Canary validates connectivity via test event. | Self-service merchant UI: "Connect your Density account" → OAuth redirect or API-key entry. |

---

## Section 5: Risk Profile (Build, Integration, Vendor Lock-in, Market Risk)

### Risk Assessment

| Risk | Option C | Mitigation | Residual |
|---|---|---|---|
| **Build risk — Adapter complexity** | Medium | Adapter template is code-generated; unit tests per vendor; smoke test on live merchant data | Low — template reduces per-vendor variance |
| **Vendor API stability** | Medium-High | Vendor APIs change (Density added new fields in 2025; Verkada deprecated endpoints twice). | Medium — vendor changes require adapter update; 2-week turnaround typical. Monitor vendor API status pages; subscribe to deprecation warnings. |
| **Merchant credential management** | Medium | Storing API keys in vault; token refresh failures = data gap. | Medium-Low — implement retry + fallback logging; merchant notified when credential refresh fails. Fallback: batch reconciliation once credentials restored. |
| **Vendor lock-in (merchant-side)** | **LOW** | Merchant owns vendor relationship. If merchant wants to switch from Density to Axis door counter, they provide new vendor credentials; Canary creates new adapter. No data loss. | **Very Low** — merchant has full optionality. |
| **Vendor lock-in (Canary-side)** | Low | Adapter pattern means each vendor is isolated. Adding vendor X does not change vendor Y's integration. | **Very Low** — new vendors are additive; no regression risk. |
| **Market risk — IoT adoption rate** | Medium | If SMB base is slow to adopt IoT (capital spend + vendor evaluation friction), ROI on Canary's adapter build is delayed. | Medium — mitigated by targeting "already have IoT" segment first (15% of base); case studies + ROI proofs of concept. |
| **Data quality / hallucinations** | Medium | Door counters can miscount (reflections, crowds). RFID can miss items (radio shadows). Vendor sensor noise in the ledger. | Medium-Low — Canary can apply statistical outlier detection; VSM explains anomalies with confidence scores. Merchant aware that IoT is observational, not truth. |

---

## Section 6: Cost & Timeline (Rough Engineer-Years and Quarters)

### Effort Estimate

| Component | Design | Build/Test | Dev Total | Roll-out | Total |
|---|---|---|---|---|---|
| **Adapter framework (base)** | 40 | 100 | 140 | 40 | 180 |
| **TypedIoTEventSchema + validator** | 30 | 60 | 90 | 20 | 110 |
| **Perpetual-ledger IoT movement types** | 50 | 100 | 150 | 30 | 180 |
| **Density adapter (door counting)** | 30 | 80 | 110 | 40 | 150 |
| **Impinj adapter (shelf RFID)** | 40 | 100 | 140 | 50 | 190 |
| **Verkada adapter (video/occupancy)** | 50 | 120 | 170 | 60 | 230 |
| **monnit adapter (temperature)** | 30 | 60 | 90 | 20 | 110 |
| **VSM IoT diagnostic tools** | 60 | 100 | 160 | 40 | 200 |
| **J (Forecast) IoT integration** | 50 | 100 | 150 | 40 | 190 |
| **S (Space) shelf-state validation** | 40 | 80 | 120 | 30 | 150 |
| **Testing (end-to-end + merchant pilot)** | 0 | 200 | 200 | 100 | 300 |
| **Documentation + onboarding training** | 40 | 40 | 80 | 20 | 100 |
| **Total Man Days** | **500** | **1,140** | **1,640** | **530** | **2,170** |
| **Total Man Years** | | | | | **10.9** |

**Timeline:**
- **Q3 2026 (3 months):** Framework + TypedSchema + Density adapter (MVP). Pilot with 2–3 beta merchants.
- **Q4 2026 (3 months):** Impinj + Verkada adapters. Expand pilot to 10–15 merchants.
- **Q1 2027 (2 months):** monnit adapter + J (Forecast) integration. General availability.
- **Q2+ 2027:** New vendor adapters on-demand (Axis, Axis, Philips, etc.), advanced features (ML anomaly detection on sensor streams).

**Effort allocation:** 2–3 FTE engineers for 11 months (framework, adapters, integrations) + 1 FTE product/systems designer for schema + integrations.

---

## Section 7: Advantages & Disadvantages

### Advantages

1. **Merchant choice preserved.** Merchant brings their own IoT vendors. No Canary-as-hardware-company friction. Merchant controls costs and vendor relationships.
2. **Broadest market entry.** The 15% of SMBs with "already have IoT" can activate immediately. The 35% planning IoT have flexibility on vendor. Low friction.
3. **Fastest time-to-value.** Merchant's existing Density counter starts feeding the perpetual ledger in days (new adapter, not new hardware).
4. **Lowest cost to Canary.** 10.9 eng-years vs 27.9 (native) or 20+ (single-vendor partnership). Adapters are smaller, templated builds.
5. **Vendor independence.** If Density is acquired or deprecated, Canary adds Axis counter and merchant switches; no re-architecture.
6. **Scalable to new vendors.** Adding vendor X (Philips, Axis, GoPro) is a new adapter module; no core platform changes. Roadmap is predictable.
7. **Perpetual-ledger vision delivered.** IoT observability is added to the ledger without forced cutover. Merchant in parallel-observer mode; can cutover to Canary analytics once ROI is clear.
8. **Competitive moat.** No competitor has this breadth of IoT integration at SMB tier. Merchants will consolidate on Canary as their IoT-to-ledger integration platform.

### Disadvantages

1. **Vendor API churn.** Density, Impinj, Verkada all update APIs. Each update requires adapter maintenance. Vendor deprecation cycle = Canary support burden. Mitigated by templated adapter pattern + automated testing, but still ongoing cost.
2. **Data quality discipline required.** Door counters hallucinate (reflections). RFID misses items. Shelf cameras mis-detect items. Merchant must understand IoT as observational layer, not ground truth. Canary has no control over sensor quality.
3. **Merchant credential management friction.** Merchant must obtain vendor API keys, enter them in Canary UI, and manage refresh/rotation. If merchant loses vendor API key, data gap. Mitigated with good error UX + email alerts, but still merchant responsibility.
4. **Integration testing burden.** Adapters must be tested against live vendor hardware (Density demo unit, Impinj reader in lab, Verkada camera in store). Lab setup costs + ongoing compatibility testing across vendor firmware versions.
5. **Coordination complexity.** Multiple vendors = multiple vendors' uptime dependencies. If Density API goes down, door-count signal halts (but RFID/video continue). Merchant must manage these dependencies.
6. **Revenue model unclear.** Canary gets margin on adapter integrations (one-time + ongoing support). But margin per adapter is smaller than native build (merchants own hardware cost). Revenue is integration consulting, not hardware resale.
7. **Merchant education required.** "BYOI" requires merchants to understand they're choosing vendors. Requires more pre-sales education than "Canary provides everything."

---

## Section 8: Summary and Recommendation

### Comparison: Options A, B, C

| Factor | **Option A: Native Stack** | **Option B: Single-Vendor Partnership** | **Option C: Multi-Vendor Adapter Framework** |
|---|---|---|---|
| **Build effort (eng-years)** | 25–30 | 18–22 | 10.9 |
| **Time to first merchant (calendar)** | 7–8 months | 5–6 months | **3–4 months** |
| **Vendor optionality for merchant** | None (Canary hardware only) | Limited (Canary partners with Density; merchants stuck) | **Full** (merchant chooses any vendor + adapters) |
| **Canary vendor lock-in risk** | None (Canary IS vendor) | **HIGH** (committed to 1–2 vendors) | **Very Low** (adapters are isolated) |
| **Merchant hardware cost** | Canary buys sensors, resells margin | Reseller margin on partner's hardware | **Merchant owns; Canary margin is integration only** |
| **Go-to-market ease** | High friction (merchants learn new vendor) | Medium friction (partner vendor familiar) | **Low friction** (merchant's existing vendor is supported) |
| **Operational headcount** | Hardware supply chain + support | Hardware supply chain + partner relationships | **Integration/adapter support only** |
| **Strategic moat** | Hardware is commoditizing | Vendor relationship is switching cost | **Breadth of adapter coverage is moat** |
| **Perpetual-ledger vision alignment** | Full (Canary controls everything) | Partial (vendor relationship is limit) | **Full + merchant optionality** |

### Heat-Map Summary (Axes: Merchant Adoption Ease × Build Cost × Strategic Optionality × Time-to-First-Merchant)

```
             LOW COST        HIGH COST
             ◄────────────►
         
HIGH EASE    Option C ✓      Option A
             (Multi-V)       (Native)
             ★★★★★          ★★☆☆☆
             
LOW EASE     Option B        
             (Single-V)
             ★★★☆☆

Strategic Optionality:
  Option A: ★☆☆ (Canary locked to own hardware)
  Option B: ★★☆ (Canary locked to 1–2 vendor partnerships)
  Option C: ★★★★★ (Adapter-based independence)

Time-to-First-Merchant:
  Option A: 7–8 months (full native build)
  Option B: 5–6 months (partner integration + hardware)
  Option C: 3–4 months (adapter framework + pilot)
```

**CLEAR WINNER: Option C.**

### Recommendation

**Chosen: Option C — Multi-Vendor IoT Adapter Framework (BYOI Model).**

**Rationale:**

1. **Business alignment.** Option C delivers on all IoT adoption targets: segment 1 (already have IoT) activates immediately; segment 2 (planning) has vendor flexibility; segment 3 (not committed) has lower friction to entry. Merchant adoption is maximized.

2. **Cost and timeline.** 10.9 eng-years in 11 months beats both alternatives. Phase 1 (Q3 2026) includes framework + Density + 2-vendor pilot. GA in Q1 2027. 3–4 month first-merchant time-to-value vs. 7–8 months (native).

3. **Operational simplicity.** No hardware supply chain. No vendor relationships to manage (merchant owns those). Canary's operational footprint is integration engineering, not logistics.

4. **Strategic durability.** Adapters are additive. Adding vendor X does not change vendor Y. Merchant gets to pick vendors and can switch without Canary friction. This is the shape that survives the next 5 years of vendor consolidation and innovation.

5. **Perpetual-ledger vision.** IoT becomes a first-class movement source on the ledger. Merchants can observe foot traffic, shelf state, equipment health in parallel with existing tools. As confidence builds, merchants cut over to Canary's IoT-derived analytics (forecast, labor scheduling, space optimization).

6. **Competitive positioning.** No SMB competitor has this breadth and flexibility of IoT integration. Canary becomes the integration substrate, not a hardware vendor. The moat is the adapter breadth + perpetual-ledger observability, not proprietary sensors.

### Phasing (4 Quarters)

| Quarter | Deliverable | Scope | Effort |
|---|---|---|---|
| **Q3 2026** | Framework + Density MVP | Adapter base, TypedSchema, Density door-counter, VSM diagnostic tools | 4.5 eng-years |
| **Q4 2026** | Impinj + Verkada | RFID shelf-state, video occupancy, S (Space) integration | 3.5 eng-years |
| **Q1 2027** | monnit + GA | Temperature monitoring, J (Forecast) integration, general availability | 2.2 eng-years |
| **Q2+ 2027** | New vendors (on-demand) | Axis, Philips, GoPro adapters; advanced detection (ML outlier filters) | TBD per vendor |

### First 90 Days (Q3 2026 MVP)

1. **Weeks 1–2:** Finalize TypedIoTEventSchema (OpenAPI + Pydantic). Validate coordinate normalization and unit conversion logic. 
2. **Weeks 3–4:** Build adapter framework base (IotAdapter abstract class, vendor credential vault, webhook/polling dispatcher).
3. **Weeks 5–6:** Implement Density adapter (door-count events, timestamp normalization, Density API polling). 
4. **Weeks 7–8:** Perpetual-ledger movement publisher (foot_traffic_event → stock ledger movements). VSM diagnostic tools (foot-traffic queries, per-location summaries).
5. **Weeks 9–10:** Integration testing with live Density hardware + beta merchant pilot (2 merchants). 
6. **Weeks 11–12:** GA launch with Density as reference implementation. Documentation + merchant onboarding training.

### Resource Commitment

- **Engineering:** 2–3 FTE for framework + adapters + integrations (11 months).
- **Product:** 1 FTE (PM) for schema definition, integration prioritization, vendor roadmap.
- **Systems/DevOps:** 0.5 FTE for credential vault, webhook infrastructure, vendor API monitoring.
- **Support:** 0.5 FTE trained for adapter troubleshooting, credential management, vendor API deprecation handling.

### Decision Gates

- **Post-MVP (Oct 2026):** Review Density adapter stability, VSM diagnostic adoption, beta merchant feedback. Proceed to Impinj/Verkada if >3 merchants activated and <5% data-loss incidents.
- **Post-GA (Mar 2027):** Evaluate adoption rate by segment. If <10% of "already have IoT" segment activates, investigate blocker (UX, vendor integration friction, or ROI narrative).
- **Pre-Q2 (Jun 2027):** Validate next-vendor priority from merchant feedback. Axis vs. Philips vs. GoPro. Plan Q2+ roadmap accordingly.

---

## Appendix: Glossary

| Term | Definition |
|---|---|
| **BYOI** | Bring Your Own IoT. Merchant provides vendor hardware and API credentials; Canary provides integration. |
| **TypedIoTEventSchema** | Canonical event structure (OpenAPI / Pydantic) that all vendor adapters normalize to. Decouples vendor APIs from Canary ledger. |
| **Adapter Pattern** | Vendor-specific code (e.g., density_adapter.py) that translates vendor API responses to TypedIoTEventSchema. Templates reduce per-vendor variance. |
| **Perpetual-Ledger Movement** | IoT events (door-count, shelf-state, equipment-health) published as movements to the stock ledger, where they feed forecasting, space optimization, and diagnostics. |
| **Parallel-Observer Mode** | Merchant's existing IoT system and Canary's IoT ledger both compute in parallel. No forced cutover; merchant chooses when to switch to Canary-driven analytics. |
| **Vendor API Deprecation** | Vendor updates API contract (adds fields, removes endpoints). Adapter must be updated. Typical turnaround: 2–4 weeks. |
| **Vendor Lock-in (Merchant)** | Merchant is locked into one vendor. Option C avoids this by supporting multi-vendor adapters. |
| **Vendor Lock-in (Canary)** | Canary is locked into one vendor relationship. Option C avoids this via adapter isolation. |

---

## Related

- [[../platform/satoshi-precision-operating-model|Satoshi-Precision Operating Model]] — The vision that IoT is the next wave of perpetual-ledger movement sources
- [[../platform/perpetual-vs-period-boundary|Perpetual-vs-Period Boundary]] — Staged migration framing (parallel-observer → modular-cutover → full-cutover) that applies to IoT adoption
- [[../modules/J-forecast-order.md|Module J — Forecast & Order]] — Integrates foot-traffic IoT signal into demand forecasting
- [[../modules/S-space-range-display.md|Module S — Space, Range, Display]] — Integrates shelf-state IoT (RFID) for planogram compliance validation
- [[../modules/L-labor-workforce.md|Module L — Labor & Workforce]] — Integrates foot-traffic signal for labor scheduling optimization
- [[canary-finance-architecture-options.md|v2.F Finance Architecture Options ADR]] — The Morrisons pattern reference; Option C (Integrated Hybrid) is the model this IoT ADR extends

---

## Conclusion

Canary's IoT vendor strategy is **Option C: Multi-Vendor Adapter Framework**. This decision prioritizes **merchant choice, rapid market entry, and perpetual-ledger vision completion**. The adapter pattern is the shape that scales with the IoT ecosystem: as new vendors emerge (Axis, Philips, GoPro, startups), Canary adds adapters; merchant optionality is preserved; operational footprint stays small.

**Ship framework + Density MVP in Q3 2026. Pilot with 10–15 merchants. Expand to Impinj + Verkada in Q4. GA in Q1 2027. Roadmap: new vendors on-demand, advanced analytics (ML, cross-merchant patterns) in v2.**

**By 2027 end, Canary is the SMB retail industry's IoT integration substrate. Merchants bring vendors; Canary connects them to the perpetual ledger.**

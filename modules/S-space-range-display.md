---
classification: confidential
owner: GrowDirect LLC
type: module-spec
prefix: S
status: v3 (design)
sibling-modules: [C, D, P, L, W]
---

# S — Space, Range, Display

S owns the physical merchandising surface: planograms, fixture inventory, shelf-edge label compilation, and range allocation per location and zone. S is the canonical "where the product is" — the geographic and spatial binding that closes the handoff between merchandise planning and store operations.

S is one of the [[spine-13-prefix#v3-full-spine-s-p-l-w|v3 full-spine expansion]] modules. It completes the three-canonical model — merchandising (C), specification (implied, shared with TTL backbones), and now space (S) — that the Intactix and Tesco suites pioneered. An item cannot be orderable at a location until S has assigned it a place on the planogram.

## Purpose

S owns four jobs:

1. **Planogram authoring and management.** Store-level and zone-level planograms (micro-planograms) with capacity constraints, pack-configuration assignments, and facings allocation. Planograms are the source of truth for what the floor looks like and what capacity exists.
2. **Fixture and space inventory.** Master data: store fixture layouts, shelf dimensions, linear footage per zone, capacity per shelf. The physical constraints that planograms must respect.
3. **Shelf-edge label (SEL) compilation and delivery.** Automatic compilation of the three-canonical layer (merchandising price/identity + planogram location/facings + specification compliance) into printable shelf-edge label instructions. Daily batch SEL generation; emergency facings updates when planograms change mid-period.
4. **Ordering gate enforcement.** C (Commercial) and J (Forecast & Order) read S's planogram assignment to validate that an item is authorized at a location before order recommendation or receipt acceptance. If an item has no planogram assignment, it cannot be ordered.

S does **not** own:

- Demand forecasting or replenishment recommendations. That belongs to [[J-forecast-order|J (Forecast & Order)]].
- Pricing and promotion strategy. That belongs to [[P-pricing-promotion|P (Pricing & Promotion)]].
- Pack configuration and specification authoring. That belongs to the merchandising master and specification layer (C and external spec canonical).
- Store layout and construction. S manages the as-is fixture inventory, not the physical remodel.

## CRDM entities touched

| CRDM entity | S's relationship | How |
|---|---|---|
| **Things** | Owns the Planogram subset | Per-location planogram assignments with item FKs to C's items |
| **Places** | Owns the Fixture subset | Store fixture master, shelf dimensions, zone definitions |
| **Workflows** | Reads | Reads ledger movements to validate on-hand against planogram capacity; alerts if over-capacity |
| **Events** | Reads | Subscribes to stock-ledger movements to enforce inventory compliance |
| **People** | Reads | Store operations staff; planogram authors (merchandisers) |

S's posture: **S is a Fixture-and-Planogram registry that gates item orderability and drives shelf-edge label compilation.** S does not modify the ledger; S reads the ledger to validate inventory compliance.

## ARTS mappings

ARTS does not define Planogram or Fixture Management specifications. Canary defines these internally, drawing on the Intactix and Tesco SRD reference models:

| Canary construct | Definition | Reference |
|---|---|---|
| **Planogram (macro)** | Store-level floor plan with zone definitions, fixture assignments, linear footage per zone | Intactix Space Planning / Floor Planning |
| **Planogram (micro)** | Shelf-level planogram with item assignments, facings, pack configurations, capacity constraints | Intactix Space Planning; Tesco SRD S-prefix interfaces |
| **Fixture Master** | Inventory of physical shelving: shelf ID, dimensions (height, width, depth), linear footage, capacity units, zone assignment | Intactix IKB; Tesco SRD fixture data |
| **Shelf-Edge Label (SEL)** | Compiled label instruction set per rail per night; includes item identity (UPC, description), price, planogram location, compliance marks | Tesco TTL (Tesco Technical Library) + SRD S039 (SEL batch) |

Cross-reference to ARTS:

- ARTS POSLog includes `item_id` and `location_id` (S can join to validate location-level planogram)
- ARTS has no Planogram or Fixture construct (store-operations focused)

## Ledger relationship

**S is SUBSCRIBER and GATEKEEPER for the ordering pipeline.**

S does NOT publish movements to the stock ledger. Instead:

- S **reads** current stock-on-hand (SOH) per item per location from the ledger
- S **reads** movement history to validate inventory compliance with planogram capacity
- S **enforces** the ordering gate: item cannot be ordered at a location until S has assigned it a planogram position at that location

The ordering-gate mechanism is the substrate-level innovation that closes the integration loop. It inverts the industry-standard sequence: 
- **Old model:** Buyer commits PO → Store receives → Merchandiser figures out where to put it
- **S model:** Merchandiser assigns planogram → Buyer commits PO → Store receives → Merchandiser confirms placement

When C (Commercial) or J (Forecast & Order) attempt to recommend or post a receipt for an item at a location, they query S first: "Is this item assigned to a planogram at this location?" If not, the PO is rejected and the buyer is directed to S to request planogram assignment.

Movement reads for validation:

- **Stock-on-hand (SOH) per item per location** — compared against planogram capacity. Alert if inventory exceeds capacity (overstocking, shrink risk).
- **Movement history per item per location** — trend velocity, stockout frequency, restocking intervals. Used to validate planogram capacity adequacy.

**Perpetual-vs-period boundary.** Canary owns: planogram authoring + ordering gate. Merchant tool owns: capital fixture planning (merchant capex tool if any). Default implementation route: `integrated-hybrid`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (data producers):

- Store operations input (planogram authoring, fixture updates, zone reconfigurations)
- C (Commercial) — item master for planogram assignment
- Stock ledger — SOH and movement history for validation
- Internal spec canonical (TTL or equivalent) — pack configurations, label compliance rules

**Downstream consumers** (data subscribers):

- **C (Commercial)** — reads planogram assignments to validate items are "orderable" before accepting OTB constraints
- **J (Forecast & Order)** — reads planogram assignments and capacity to constrain replenishment recommendations
- **D (Distribution)** — reads planogram assignments on receipt to validate item placement is ready
- **P (Pricing & Promotion)** — reads planogram assignments on price changes to validate signage/label impact
- **SEL/labeling system** — daily batch consumes planogram data + price/compliance data to compile shelf-edge labels
- **Store operations dashboard** — displays planogram capacity utilization, stockout alerts, over-capacity warnings

## Agent surface

S exposes MCP tool families for store operations and merchandising workflows:

- **Planogram authoring** — create/edit store-level and zone-level planograms; assign items to shelves with pack configuration and facings
- **Capacity validation** — check planogram capacity utilization (current SOH vs. assigned capacity); receive over-capacity alerts
- **Fixture management** — query fixture master; request fixture updates (new shelf, dimension change, zone reconfig)
- **Orderability check** — confirm whether an item is planogram-assigned at a location (gate for PO entry)
- **SEL compilation monitoring** — view daily SEL batch status; request emergency facings update for mid-period planogram changes
- **Movement trend analysis** — query item velocity and restocking intervals per location to validate capacity adequacy

## Security posture

- **Auth.** All writes (planogram changes, fixture updates) require `store_operations` or `merchandiser` role. MCP tool-level role checking enforced.
- **Tenant scoping.** Every planogram and fixture record carries `merchant_id`; every read is row-level-secured.
- **Capacity governance.** Planogram assignments enforce merchandise hierarchy and cost-method constraints (items from RIM departments cannot share shelf space with Cost-Method items without explicit override).
- **Auditability.** Every planogram change (item assignment, facings change, pack configuration update) is logged with `changed_by`, `changed_at`, `reason_code` (plano refresh, seasonal reset, emergency restock, etc.).
- **SEL integrity.** Shelf-edge labels are compiled deterministically from planogram + price + compliance data; label compile failures are escalated to store operations immediately.

## Roadmap status

- **v3 (design)** — Planogram authoring and management. Fixture master. Planogram-capacity validation. Ordering gate enforcement (blocks PO/receipt if item not assigned). SEL compilation driver (contracts with external label system). Read-only and restricted-write MCP tools for store operations workflows.
- **v3.1** — Zone-level micro-planograms with advanced capacity modeling (shelf-specific weights, compressible vs. rigid fixtures).
- **v3.2** — Planogram optimization engine (suggest item assignments based on velocity, margin, shrink patterns).
- **v3.3** — Integration with P (Pricing & Promotion) for signage-change impact analysis (markdown events trigger SEL re-compile).

## Open questions

1. **Planogram authorization scope.** Can every store manager author planograms for their store, or must a central merchandiser approve planogram changes? Per-merchant policy?
2. **Capacity unit standardization.** Is capacity always measured in "units" (items), or do some retailers want weight/volume (for bulk/bulk items)? Pack-configuration handling for mixed-unit items?
3. **Multi-location assortment matrix.** Does S maintain a location-to-item assortment matrix (store A carries item X, store B doesn't), or is assortment uniform across all locations? Current assumption: uniform at v3, matrix at v3.1.
4. **SEL system integration.** Is the SEL compile target an external labeling system (Sysrepublic CRDM, competitor), or does Canary own SEL generation? Integration contract / API shape?
5. **Fixture-update impact on capacity.** When a store requests a fixture update (new shelf, remodel), how does S validate that remaining capacity is adequate for existing planogram? Conflict resolution workflow?

## Related

- [[../platform/stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]]
- [[../platform/retail-accounting-method|Retail Accounting Method — RIM, Cost Method, Open To Buy]]
- [[../platform/spine-13-prefix|The Canary Retail Spine — 13 Modules]]
- [[../../GrowDirect/Brain/wiki/intactix-canonical-validation|Intactix 2006 — Canonical Validation of RetailSpine]]
- [[../../GrowDirect/Brain/wiki/tesco-technical-library|Tesco Technical Library — The Third Canonical Layer]]
- [[../../GrowDirect/Brain/wiki/third-branch|The Third Branch]]
- [[../../GrowDirect/Brain/wiki/srd-shelf-edge-label|Shelf-Edge Label Compilation and Delivery]]
- [[C-commercial|C (Commercial)]]
- [[D-distribution|D (Distribution)]]
- [[J-forecast-order|J (Forecast & Order)]]
- [[P-pricing-promotion|P (Pricing & Promotion)]]
- [[W-work-execution|W (Work Execution)]]

## Sources

- [[../../GrowDirect/Brain/wiki/intactix-canonical-validation|Intactix Enterprise Suite 2006.2.0 Integration Guides (5 documents)]]
- [[../../GrowDirect/Brain/wiki/tesco-technical-library|Tesco Technical Library Functional Specification V1.0 and Integration Guides]]
- [[../../GrowDirect/Brain/wiki/srd-shelf-edge-label|Fresh & Easy / Tesco SRD Architecture (323 files, 30+ S-prefix interface specifications)]]
- [[../../GrowDirect/Brain/wiki/third-branch|The Third Branch — Operating lineage and three-canonical framing]]

---

*Classification: confidential. Owner: GrowDirect LLC. Created 2026-04-24. S (Space, Range, Display) is a v3 module spec within the Canary Retail Spine. It is design-stage; implementation is deferred pending v2 ring (C/D/F/J) stabilization.*

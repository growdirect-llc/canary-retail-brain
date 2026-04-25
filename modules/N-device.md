---
classification: confidential
owner: GrowDirect LLC
type: module-article
prefix: N
status: v1 (model shipping; sync gated on OAuth scope)
sibling-modules: [T, R, A, Q]
---

# N — Device

N owns the device subset of CRDM Things. Every POS terminal, scanner,
register, kitchen display, IoT sensor, and physical store device is
a first-class tracked entity in N. This is a deliberate departure
from how SMB-tier retail tech treats devices today: most platforms
treat a register as an attribute on a transaction (`device_id` as a
string field), not as an entity with its own lifecycle, identity,
and analytics surface.

N is one of the [[../platform/spine-13-prefix#v1-differentiated-five-t-r-n-a-q|
Differentiated-Five]] modules at v1. The model and schema are
production-ready; the live Square sync is gated on an OAuth scope
expansion that has not yet shipped. The platform can ingest device
records via webhook and direct API call today; the
self-service-merchant onboarding-time pull awaits scope.

## Purpose

N owns three jobs:

1. **Curate the device entity.** One row per device per merchant,
   keyed by the upstream vendor's identifier (today: Square's
   `device_id`). Every transaction T processes points at a device;
   N is the FK target.
2. **Hold device telemetry.** Software version, OS version, network
   posture, battery state, charging state — every operational signal
   the vendor exposes about the device. Stored as both typed columns
   (for query) and a JSONB safety net (for forward compatibility).
3. **Provide the asset registry [[A-asset-management|A]] runs against.**
   A's anomaly detection requires per-device baselines. N is the
   table A profiles.

N does **not** own:

- Detection rules over devices. Q owns rule definitions; N provides
  the FK target for any device-conditioned rule.
- Per-device baselines. Those are A's projection over N's registry.
- Device decommissioning workflows. Adjacent; not yet built.

## BST cells N populates

N is the device-side curator. It is the primary owner of a few
operationally-flavored BSTs and the FK target for many more.

| Domain | BST | N's role |
|---|---|---|
| Store Operations | **Suspicious Activity Analysis** | Primary feeder — device-conditioned anomalies |
| Store Operations | **Loss Prevention Analysis** | Feeder via FK — cashier-on-device patterns |
| Store Operations | Performance Measurement | Feeder — device throughput, uptime |
| Store Operations | Service Delivery Analysis | Feeder — device availability, network state |
| Multi-Channel | eCommerce Analysis | Not applicable — N covers physical devices |

Device-side BSTs that don't yet have a clear owner: device-portfolio
analysis, device-lifecycle reporting, device-vendor performance.
Probably belong in N at v2 once the registry has enough signal.

## CRDM entities touched

| CRDM entity | N's relationship | How |
|---|---|---|
| **Things** | **Owns** the device subset | One row in `devices` per merchant per Square device |
| Places | Reads | FK `location_id` to the Place registry |
| Events | Reads | T's transactions FK to N's `device_id` for telemetry correlation |
| People | Reads | `employee_id` on transactions joins to identify cashier-on-device |
| Workflows | Triggers | A's anomaly detection produces Workflow signals on N's registry |

N's posture: **N is a Things registry that mirrors vendor device state
plus a JSONB capture of everything the vendor sends.** N curates the
typed surface; the JSONB column ensures no vendor field is lost when
the vendor adds something Canary doesn't yet have a column for.

## ARTS mapping

N is the home of [[../platform/crdm#relationship-to-arts|ARTS Device
Model]] adoption.

| ARTS Device Model construct | N's column |
|---|---|
| Device.DeviceID | `devices.square_device_id` (vendor-namespaced) |
| Device.SerialNumber | `devices.serial_number` |
| Device.DeviceName | `devices.device_name` |
| Device.OSVersion | `devices.os_version` |
| Device.ApplicationVersion | `devices.app_version` |
| Device.NetworkAddress | `devices.ip_address` |
| Device.NetworkConnection | `devices.network_connection_type`, `wifi_network_name`, `wifi_network_strength` |
| Device.PowerState | `devices.battery_percentage`, `charging_state` |
| Device.LocationID | `devices.location_id` (FK to Place registry) |
| Device.Manufacturer / Model | covered in `raw_square_object` JSONB |
| Device.Status | derived from `db_status` + telemetry decay |

The JSONB `raw_square_object` field carries the complete Square API
response. Any ARTS Device field the vendor exposes that isn't yet
typed in Canary's columns is still queryable from JSONB.

## Schema choice

N's tables live in the `sales` schema, not `app`. This is unusual
for a registry and worth explaining.

The reasoning: device records, like transactions, are append-only-ish
operational facts ingested from a vendor. They mutate (status
updates, version bumps), but they are not configuration state owned
by Canary — they mirror vendor truth. The `sales` schema is the
"things we ingested from a vendor" schema; placing the device
registry there keeps the ingestion surface coherent.

Trade-off: N readers need to know to join across `app` (locations,
employees) and `sales` (devices). Cross-schema joins are first-class
in PostgreSQL but require explicit schema qualification in queries.
The clarity of "ingested vendor data lives in sales" is judged worth
the join cost.

## Schema crosswalk

N writes to the `sales` schema.

| Table | Owner | Pattern | Purpose |
|---|---|---|---|
| `devices` | N | mutable (status updates) | Device registry; one row per merchant per Square device |

N reads (no write):

| Table | Owner | Why N reads |
|---|---|---|
| `app.merchants` | platform | Tenant resolution |
| `app.merchant_locations` | future Places registry | Validate `location_id` FK |
| `sales.transactions` | T | Telemetry correlation; cross-reference patterns |

## Service-name markers (v0.7 microservice index)

| Service slot | Responsibility | Currently lives in |
|---|---|---|
| `n-registry` | Device entity CRUD, FK target | `canary/models/sales/devices.py` |
| `n-sync-square` | Square Devices API pull (gated on `DEVICES_READ` scope) | not yet implemented |
| `n-telemetry-hooks` | Device-state webhook ingestion | T's webhook surface (no dedicated module today) |
| `n-health-check` | Device-health surface for ops dashboards | `canary/services/health_check/generators/devices.py` |
| `n-jsonb-extract` | Vendor-field-to-column promotion utilities | not yet implemented (JSONB queried directly today) |

**Perpetual-vs-period boundary.** Canary owns: device registry + telemetry. Merchant tool owns: MDM/asset-management (Jamf, Kandji, etc.). Default implementation route: `integrated-hybrid`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (where device data lands in N):

- Square Devices API — pull, periodic. *Currently gated on
  `DEVICES_READ` OAuth scope which Canary has not yet acquired.*
- Square device-state webhooks (where the vendor exposes them)
- T's transaction stream — first-seen new `device_id`s upsert
  minimal device records

**Downstream consumers** (who reads N):

- **A (Asset Management)** — primary consumer; per-device baselines
  and anomaly scoring run against N's registry
- **Q (Loss Prevention)** — chirp rules conditioning on device
  identity (e.g., `C-303 WRONG_LOCATION`) join through N
- **T (Transaction Pipeline)** — FK validation
- **Future health/operations dashboards** — fleet-wide device posture

## Agent surface

N has no dedicated MCP server at v1. Device queries surface through:

- Q's investigator tools (case context: "what device was this on?")
- T's pipeline-health introspection (parse-failure rate by device)

A future `canary-fleet` MCP server is anticipated for v2 once the
sync pipeline is unblocked and the registry has enough signal to
support fleet-management workflows.

## Security posture

- **Auth.** Tenant-scoped. Every device row carries `merchant_id`;
  RLS enforces isolation.
- **Tenant scoping.** `app.merchants` FK ensures device records
  cannot leak across tenants.
- **PII handling.** Device records contain no human PII. Network
  addresses (`ip_address`) are operational identifiers, not personal.
- **Vendor token scope.** Gating sync on `DEVICES_READ` is a
  least-privilege posture: Canary doesn't read what it isn't yet
  using.
- **JSONB safety.** The `raw_square_object` field is treated as
  trusted vendor input. PII filters apply at parser time if vendor
  fields ever carry personal data (none currently do for the
  device-model surface).

## Open questions

1. **`DEVICES_READ` OAuth scope acquisition.** Blocks N's sync. The
   path is: petition Square for the scope, get approval, push a
   token-rotation pass to existing merchants. Engineering work is
   small; the gating is administrative. Until done, N's registry
   populates only opportunistically (from transaction-FK first-seen).
2. **Schema location.** `sales` vs. `app` for the device registry
   is a defensible choice but should be documented at the
   `data-model.md` SDD level so future readers don't trip on it.
3. **JSONB-to-column promotion cadence.** When Square adds a new
   device field, the JSONB picks it up; promoting it to a typed
   column for query performance is a manual decision. No policy
   today.
4. **Cross-vendor device identity.** Same problem as customer
   identity — a retailer running Square on terminals and Shopify on
   web has device namespaces in two systems with no platform-level
   identity model. Belongs in N when adapter #2 ships in T.
5. **Decommissioning workflow.** A device that leaves a store
   (returned, broken, replaced) needs a workflow. Today: `db_status`
   flips to `archived` and that's it. Real lifecycle (return-to-
   vendor, replacement-tracking) is unbuilt.

## Roadmap status

- **v1 (shipping)** — Model + schema production-ready. Opportunistic
  population from T's transaction stream. JSONB safety net.
- **v1.x** — `DEVICES_READ` scope acquisition unblocks self-service
  device sync at onboarding.
- **v2** — Fleet-management MCP surface. Device-decommissioning
  workflow. Cross-vendor device identity (paired with T's adapter
  #2).
- **v3+** — Predictive maintenance signals. Device-vendor performance
  analytics.

## Related

- [[../platform/spine-13-prefix|13-prefix spine]]
- [[../platform/crdm|Canonical Retail Data Model]]
- [[../platform/overview|Platform overview]]
- [[T-transaction-pipeline]] — provides FK references and opportunistic populator
- [[R-customer]] — sibling Differentiated-Five module
- [[A-asset-management]] — primary downstream consumer; runs anomaly detection over N
- [[Q-loss-prevention]] — sibling Differentiated-Five module

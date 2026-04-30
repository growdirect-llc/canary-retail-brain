---
title: N — Role Alignment
date: 2026-04-24
type: wiki
status: active
tags: [canary, retail-spine, module-n, device, asset-registry, arts]
sources:
  - Canary-Retail-Brain/modules/N-device.md
  - Canary/canary/models/sales/devices.py
last-compiled: 2026-04-24
----

# Canary Module — N (Device)

## Summary

N is Canary's device registry — every POS terminal, scanner, and IoT
device tracked as a first-class CRDM Thing. Mirrors Square's device
model with a JSONB safety net for vendor-field forward-compatibility.
The model lives in the `sales` schema, not `app`, because devices are
ingested vendor truth rather than Canary configuration state.

**Status note:** The model and schema are production-ready. The
self-service Square Devices API sync is **gated on the `DEVICES_READ`
OAuth scope**, which Canary has not yet acquired. Until then, N
populates opportunistically from transaction FK first-seen.

This wiki article is the Canary-specific crosswalk for N. The
canonical, vendor-neutral spec lives at
`Canary-Retail-Brain/modules/N-device.md`.

## Code surface

| Concern | File | Notes |
|---|---|---|
| Device model | `Canary/canary/models/sales/devices.py` | `devices` table, `sales` schema |
| Health-check generator | `Canary/canary/services/health_check/generators/devices.py` | Operational health surface |
| Square device sync | (not yet implemented) | Blocked on `DEVICES_READ` scope |

## Schema crosswalk

N writes to the `sales` schema (one table at v1).

**Owns (write):**

| Table | Pattern | Purpose |
|---|---|---|
| `devices` | mutable (status / version updates) | Device registry; one row per merchant per Square device |

**Reads (no write):**

| Table | Owner | Why |
|---|---|---|
| `app.merchants` | platform | Tenant resolution |
| `app.merchant_locations` | future Places registry | Validate `location_id` FK |
| `sales.transactions` | T | Telemetry correlation |

## Devices table — column inventory

(All in `sales.devices`, per `Canary/canary/models/sales/devices.py`.)

| Column | Type | Notes |
|---|---|---|
| `id` | String UUID | PK |
| `merchant_id` | String | TenantMixin FK |
| `square_device_id` | String | Square device identifier |
| `location_id` | String | FK to location (indexed) |
| `serial_number` | String | Device serial |
| `device_name` | String | Friendly name |
| `os_version`, `app_version` | String | Software versions |
| `network_connection_type`, `wifi_network_name`, `wifi_network_strength`, `ip_address` | String | Network posture |
| `battery_percentage`, `charging_state` | String | Power state |
| `raw_square_object` | JSONB | Complete Square API response (forward compatibility) |
| `created_at`, `updated_at` | DateTime | Standard |

Indexes: `(merchant_id, location_id)`, `(merchant_id, serial_number)`,
`(merchant_id, square_device_id)`.

## SDD crosswalk

| SDD | Path | N's relationship |
|---|---|---|
| data-model | `Canary/docs/sdds/v2/data-model.md` | Device table definition (sales schema) |
| multi-pos-architecture-proof | `Canary/docs/sdds/v2/multi-pos-architecture-proof.md` | Device registry as multi-POS-support foundation |

## Where N fits on the spine

N is one of the [[../projects/RetailSpine|Retail Spine]] Differentiated-Five
modules. Per [[../projects/RetailSpine#4-store-operations-management|Store
Operations § BST inventory]], N is a primary feeder for:

- **Suspicious Activity Analysis** (device-conditioned anomalies)
- **Loss Prevention Analysis** (cashier-on-device patterns via FK)
- **Performance Measurement** (device throughput / uptime)
- **Service Delivery Analysis** (device availability)

N is the FK target for device-conditioned Chirp rules and the registry
[[canary-module-a-asset-management|A (Asset Management)]] runs anomaly
detection against.

## MCP tool surface

No dedicated `canary-fleet` MCP server at v1. Device queries surface
through Q's investigator tools (case context) and T's pipeline-health
introspection. A `canary-fleet` server is anticipated for v2 once
sync is unblocked.

## Open Canary-specific questions

1. **`DEVICES_READ` OAuth scope.** Single biggest blocker for N.
   Engineering work to consume the scope is small; the gating is
   administrative (Square approval + token-rotation pass to existing
   merchants).
2. **Schema location (`sales` vs `app`).** N is a registry that
   lives in `sales` because devices are ingested vendor truth. This
   choice should be documented in `Canary/docs/sdds/v2/data-model.md`
   so future readers don't trip on it.
3. **JSONB-to-column promotion policy.** No policy for when a new
   Square device field gets promoted from `raw_square_object` JSONB
   to a typed column.
4. **Cross-vendor device identity.** When T gets a non-Square
   adapter, devices from that vendor will need a unification model.
   Pairs with the same gap in R.
5. **Decommissioning workflow.** Device returned / broken / replaced
   has no real lifecycle — just `db_status = 'archived'`. Vendor-
   return tracking, replacement-tracking are unbuilt.

## Related

- [[../projects/RetailSpine|Retail Spine MOC]]
- [[canary-data-model|Canary Data Model]]
- [[canary-architecture|Canary Architecture]]
- [[canary-module-t-transactions|Canary Module — T (Transaction Pipeline)]]
- [[canary-module-r-customer|Canary Module — R (Customer)]]

## Sources

- `Canary-Retail-Brain/modules/N-device.md` — canonical vendor-neutral spec
- `Canary/canary/models/sales/devices.py` — Device model
- `Canary/canary/services/health_check/generators/devices.py` — device health surface
- `Canary/docs/sdds/v2/data-model.md` — schema definition
- `Canary/docs/sdds/v2/multi-pos-architecture-proof.md` — device registry rationale

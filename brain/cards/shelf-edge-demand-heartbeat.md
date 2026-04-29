---
card-type: protocol-spec
card-id: shelf-edge-demand-heartbeat
card-version: 1
domain: platform
layer: edge
feeds:
  - module-s
  - module-j
  - module-q
  - heartbeat-protocol
  - temporal-retail-mesh
receives:
  - edge-fabric-overview
  - map-agent-l3
tags: [heartbeat, shelf-edge, demand-signal, nano, iot, module-s, module-j, nats, inference]
status: approved
last-compiled: 2026-04-28
---

# Shelf Edge Demand Heartbeat — The Demand Signal IS the Heartbeat

The shelf node heartbeat is not a system health check with a demand signal
attached. The demand signal is the heartbeat. A shelf edge node's proof of
life is the structured shelf state it emits — facing count, depletion rate,
gap detection. A silent shelf node is not just a connectivity problem; it is
an unknown inventory state, which is a Rail 1 violation.

Nano inference is the translator. Raw camera and sensor data is not
structured enough to push onto the NATS bus. Nano runs on the shelf edge
box, converts visual and sensor input into a structured `ShelfHeartbeat`
payload, and emits it on the same heartbeat infrastructure as every other
node. The MAP agent above it sees a heartbeat — it does not need to know
Nano produced it.

## Payload Contract

```go
type ShelfHeartbeat struct {
    NodeID       uuid.UUID         `json:"node_id"`
    MerchantID   uuid.UUID         `json:"merchant_id"`
    Timestamp    time.Time         `json:"timestamp"`
    Sequence     uint64            `json:"seq"`
    Location     ShelfLocation     `json:"location"`
    DemandSignal ShelfDemandSignal `json:"demand_signal"`
    Anomaly      *ShelfAnomaly     `json:"anomaly,omitempty"`
    Signature    []byte            `json:"sig"`
}

type ShelfLocation struct {
    StoreID     uuid.UUID `json:"store_id"`
    Aisle       string    `json:"aisle"`
    Bay          int      `json:"bay"`
    LayoutCoords [2]float64 `json:"coords"` // store floor plan coordinates
}

type ShelfDemandSignal struct {
    SKUID           uuid.UUID       `json:"sku_id"`
    FacingCount     int             `json:"facing_count"`
    FacingCapacity  int             `json:"facing_capacity"`
    DepletionRatePH float64         `json:"depletion_rate_ph"` // units per hour
    EstHoursToZero  float64         `json:"est_hours_to_zero"`
    GapDetected     bool            `json:"gap_detected"`
    ConfidenceScore float64         `json:"confidence"`        // Nano inference confidence
}

type ShelfAnomaly struct {
    Type        string  `json:"type"` // "product_moved", "wrong_sku", "pricing_mismatch"
    Confidence  float64 `json:"confidence"`
    Description string  `json:"description"`
}
```

NATS topic: `store.<merchant_id>.shelf.<node_id>.heartbeat`

## Inference Stack at the Node

```
Camera + weight sensor + RFID
        ↓
  Nano inference
  (visual → structured ShelfDemandSignal)
        ↓
  ShelfHeartbeat assembled + signed
        ↓
  NATS JetStream (LAN)
        ↓
  MAP_S agent receives, evaluates, forwards to cloud on variance
```

Nano's job is narrow: translate unstructured physical state into a
structured demand signal. It does not decide what to do with the signal.
The MAP agent decides.

## Downstream Consumers

| Module | What it receives | What it does with it |
|--------|-----------------|---------------------|
| S — Space, Range & Display | FacingCount, GapDetected, LayoutCoords | Shelf compliance scoring, facing audit |
| J — Forecast & Order | DepletionRatePH, EstHoursToZero | Intra-day forecast adjustment, replenishment trigger |
| Q — Loss Prevention | ShelfAnomaly (product_moved, wrong_sku) | Fox case candidate — product movement without a transaction |

## Replenishment Trigger (Temporal Workflow)

When `EstHoursToZero` drops below the store's replenishment lead time
threshold, the MAP_S agent starts a Temporal workflow:

```
ShelfReplenishmentWorkflow
  → Activity: CheckBackroomStock (Module A)
  → Activity: CommitReplenishmentTask (Module W — work dispatch)
  → Activity: AdjustForecast (Module J — intra-day)
  → Activity: UpdateShelfPlan (Module S — facing record)
```

The replenishment loop is closed entirely on the LAN. No cloud round-trip
required. Internet outage does not stop shelf replenishment.

## Failure Mode

A shelf node that stops emitting for >30s triggers the standard heartbeat
failure path (Module N + Q auto-open Fox case). The Fox case type is
`device_silent` not `theft` — but the LP agent reviews it because a
silenced shelf camera is also a theft precondition.

## Invariant Extension

Extends invariant 9:
> Every physical node emits signed heartbeats. A shelf node's heartbeat
> carries a demand signal produced by on-device Nano inference. A silent
> shelf is an unknown inventory state — Rail 1 violation.

---
card-type: research-archive
card-id: fireball-demand-signal-origin
card-version: 1
domain: platform
layer: cross-cutting
feeds:
  - shelf-edge-demand-heartbeat
  - edge-fabric-overview
  - heartbeat-protocol
  - map-agent-l3
receives: []
tags: [fireball, origin, demand-signal, pos, biztalk, microsoft, pwc, marks-spencer, supply-chain, history]
status: approved
last-compiled: 2026-04-28
source-path: Brain/raw/inbox/Heartbeat/
---

# Fireball — Origin of the Demand Signal Architecture

**Project:** Fireball Ultimate Supply Chain Initiative — Retail Point-Of-Sale Demand Signal Orchestration  
**Period:** 2000–2002  
**Partners:** Microsoft Consulting Services · PwC · Procter & Gamble · Marks & Spencer · Meijer  
**Source:** `Brain/raw/inbox/Heartbeat/` (Fireball Documentation, M&S Case Study, Phase-I Assessment, Go-to-Market)

---

## The Core Thesis (unchanged in 25 years)

> *The Supply Chain must have a real-time signal that indicates the state of demand.*

The single driving concept: consumer demand, not forecasts, must drive the entire supply chain. To accomplish this, one capability must become pervasive at every scale — from the world's largest retailer to the smallest mom-and-pop outlet.

Fireball was the first serious attempt to build it. The technology of the era — BizTalk Server, MSMQ, WAN routing — could not fully deliver it. The thesis was correct. The infrastructure was the bottleneck.

---

## What Fireball Actually Built

### M&S Implementation (Production, ~2001)

435 stores, £13.2B revenue, UK's premier clothing, food, and financial services retailer.

| Layer | Technology | Contract |
|-------|-----------|---------|
| In-store | Windows NT 4.0 + SQL Server 6.5 + MSMQ + Visual Basic | Extract POS transaction data, convert to BizTalk XML, post to MSMQ |
| Network | MSMQ over WAN | Route data from 300+ stores to data center |
| Data center | BizTalk Server farm + MSMQ/MQSeries Bridge + COMTI | Transform, route, deliver to S/390, CICS/DB2 destinations |
| Return path | Same infrastructure | Event-driven promotions pushed back to stores |

**Scale:** 250 store transactions/second inbound to BizTalk, 250/second onward to central applications. Up to 5 GB/day at peak trading.

**Vision beyond Phase I:** Flexible infrastructure backbone extending to 500+ suppliers. Any data, anywhere in M&S or supplier base, without reworking when a link in the chain changes.

**Key requirements M&S cited:**
- Adaptability — generic solution, no rework when any link changes
- Richness — basket-level sales data, not just totals
- Timeliness — near real-time, not overnight batch
- Flexibility — 24 hours/day, not traditional batch windows
- Bidirectionality — event-driven promotions back to store

### P&G Proof of Concept (Origin)

P&G's vision: reduce out-of-stocks to near zero, reduce inventory buffers by 50%. Projected P&G savings from a demand-driven supply chain: $900M.

The PoC scope: capture the demand signal at the POS and orchestrate its movement in near real-time throughout the supply chain. Experiment with delivering actions back through the supply chain in response to the signal.

### Meijer Extended Pilot

Scaling to 15 stores. Developing standardized retail adapters for:
- **NCR 4690 / 4680** — the same NCR Counterpoint lineage that Canary Go's Bull adapter targets 25 years later
- Systech adapter integration
- XML standards for data interchange

---

## What Fireball Could Not Deliver

The architecture had a structural bottleneck: the demand signal traveled store → WAN → BizTalk farm → central systems. Every step added latency. Best-practice demand signal propagation in 2001 was 9–16 hours. Fireball aimed to reduce this to "near real-time" — but "near real-time" over a WAN through a centralized BizTalk farm is not the same as real-time on a LAN.

The store could not operate autonomously during WAN outage. The intelligence lived in the data center. The store was a data source, not a decision node.

The agents they needed did not exist. The orchestration was infrastructure-driven, not intelligence-driven. BizTalk routed messages; it did not reason about them.

---

## What Canary Go Completes

| Fireball (2001) | Canary Go (2026) |
|-----------------|-----------------|
| BizTalk Server farm (centralized) | NATS JetStream on store LAN (edge-native) |
| MSMQ over WAN | MAP agent on LAN — no WAN dependency for local decisions |
| XML message routing | Temporal durable workflows + structured Go value objects |
| "Near real-time" (minutes) | Real-time (sub-second on LAN) |
| WAN outage = store goes blind | LAN outage resilience — MAP agent keeps running |
| 250 tx/sec to central BizTalk | NATS handles 10M+ msg/sec on commodity hardware |
| NCR 4690/4680 adapter (unfinished) | Bull adapter — NCR Counterpoint REST (Phase I complete) |
| Human-mediated response | Autonomous MAP agent decision + Temporal dispatch |
| Demand signal → central forecast | Shelf-edge Nano inference → ShelfHeartbeat → MAP_S + MAP_J |
| Promotions pushed from center | Work tasks dispatched from edge (Module E) |

The infrastructure gap is closed. NATS + Go + Temporal delivers what BizTalk + MSMQ + WAN could not.

---

## The Heartbeat Connection

Fireball's folder is named `Heartbeat`. The demand signal is the pulse of the store — Fireball understood this metaphorically. Canary Go makes it literal: the `ShelfHeartbeat` struct carries the Nano-inferred demand signal as the node's proof of life. A silent shelf is not just a connectivity problem; it is an unknown inventory state.

The concept Fireball named. The architecture Canary Go ships.

---

## Related

- [[shelf-edge-demand-heartbeat]] — the `ShelfHeartbeat` struct that completes the Fireball thesis
- [[heartbeat-protocol]] — the signed node heartbeat protocol
- [[edge-fabric-overview]] — the full edge architecture
- [[map-agent-l3]] — the intelligence layer Fireball was missing
- Source: `Brain/raw/inbox/Heartbeat/Phase-I Pilot Assessment.doc`
- Source: `Brain/raw/inbox/Heartbeat/MS Overview/Fireball Vision Scope.doc`
- Source: `Brain/raw/inbox/Heartbeat/Retail Biztalk Resource Kit/Documentation/Include/Marks and Spencer Case Study.doc`

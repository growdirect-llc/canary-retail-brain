---
classification: confidential
owner: GrowDirect LLC
type: module-spine
---

# The Canary Retail Spine — 13 Modules

Canary Retail's module catalog is organized along a 13-prefix spine.
Each prefix is a letter that names both the module and its slug
namespace in the codebase. The spine is deliberately exhaustive —
it covers the full operating surface of an SMB specialty retailer
from customer-facing commerce through back-office governance.

## The spine, at a glance

| Prefix | Module | Status | One-liner |
|---|---|---|---|
| **T** | Transaction Pipeline | v1 (shipping) | POS-agnostic ingestion; seal → parse → merkle → detect |
| **R** | Customer | v1 (shipping) | ARTS Customer Model; unified customer entity |
| **N** | Device | v1 (shipping) | ARTS Device Model; asset registry for POS / scanners / IoT |
| **A** | Asset Management | v1 (shipping) | Bubble — anomaly detection over the asset registry |
| **Q** | Loss Prevention | v1 (shipping) | Detection engine + case management |
| **C** | Commercial | v2 | Items, departments, suppliers |
| **D** | Distribution | v2 | Inventory movement, store-DC transfers |
| **F** | Finance | v2 | Purchase orders, invoices, reconciliation |
| **J** | Forecast & Order | v2 | Demand forecast, automated ordering |
| **S** | Space, Range, Display | v3 | SRD planning, planogram integration |
| **P** | Pricing & Promotion | v3 | Promotion engine, markdown management |
| **L** | Labor & Workforce | v3 | Labor model, scheduling, time tracking |
| **W** | Work Execution | v3 | Generalized detection + case for all domains (Chirp+Fox over the whole spine) |

## v1 — Differentiated-Five (T + R + N + A + Q)

These five ship at v1 because together they answer the question: "What
do SMB specialty retailers have that nobody else productizes?"

- **T** and **Q** are the classical LP workload — transaction
  ingestion and rule-based detection. Everyone ships these, most ship
  them poorly.
- **R**, **N**, and **A** are where Canary differentiates. Unified
  customer across channels (R), every device as a first-class asset
  (N), and threat detection over the asset registry (A) — these are
  standard in enterprise retail tech but missing from SMB-tier tools.

v1's pitch: "You get the LP module everyone charges for, plus the
customer / device / asset tier nobody charges for, because they're
the same platform."

## v2 — CRDM expansion (C + D + F + J)

Once a retailer runs on v1, the next ask is almost always: "Can you
also handle our buying, inventory movement, and financial flow?"
These four modules answer that question without pulling the
retailer toward an ERP replacement.

## v3 — Full spine (S + P + L + W)

Space/range/display, pricing/promotion, labor/workforce, and
generalized work-execution across all domains. This is the full
retail operating platform, delivered module-by-module rather than as
a single cutover.

## Dependencies

Modules depend on:

- **CRDM** — the canonical retail data model. Every module reads
  and writes the shared People × Places × Things × Events ×
  Workflows entities.
- **ARTS adoption** — POSLog, Customer, Device, Site standards
  frame the entity definitions for T/R/N modules.
- **Evidence chain** — hash-chained intake and append-only
  timelines underlie all modules; Q and W depend on it most
  directly.
- **Agent mesh** — every module has an agent population backing its
  tooling. The agent mesh architecture lives in the KATZ vault
  (`cbm-v2/agent-strategy.md`) — open the sibling vault to read it.

## Per-module detail

See `modules/<prefix>-<name>.md` for the per-module deep-dive. Each
module article covers:

- Purpose
- CRDM entities touched
- ARTS mappings (where applicable)
- Integrations (upstream sources, downstream consumers)
- Agent surface (what agent tools the module exposes)
- Security posture (auth, tenant scoping, PII handling)
- Roadmap status

## Related

- [[overview]]
- [[crdm]]
- [[arts-adoption]]
- [[differentiated-five-add-on]]

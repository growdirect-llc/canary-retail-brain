---
classification: confidential
owner: GrowDirect LLC
type: module-spec
prefix: W
status: v3 (design)
sibling-modules: [S, P, L]
---

# W — Work Execution

W is the generalized exception detection and case management surface that extends Q's (Loss Prevention) Chirp+Fox pattern across every domain in the retail spine. W detects policy violations, rule breaches, and anomalies in inventory, commercial, pricing, labor, and space domains — then routes exceptions to the appropriate workflow.

W is one of the [[spine-13-prefix#v3-full-spine-s-p-l-w|v3 full-spine expansion]] modules and the capstone of the spine. It is the retail operating system's immune system: every module publishes its invariant violations to W; W correlates them, escalates, and ensures visibility. Without W, violations go undetected and compound silently.

## Purpose

W owns two jobs:

1. **Cross-domain exception detection.** Read all spine modules' movements and signals; evaluate against rule catalogs (one per domain). Detect policy violations, rule breaches, and anomalies. Auto-escalate high-confidence violations to case creation.
2. **Case management and remediation.** Promote exceptions to cases. Manage investigation lifecycle. Assign investigators. Collect evidence. Track resolution. Route to appropriate remediation workflow (refund, restock, adjustment, referral).

W does **not** own:

- Domain-specific rule authoring. Each module owns its own rules (Q owns LP rules, S owns space rules, P owns promotion rules, etc.).
- Remediation execution. If a case requires a refund, the appropriate module (T, D, P) executes it.
- Customer or employee profile management. That belongs to R and L.

## CRDM entities touched

| CRDM entity | W's relationship | How |
|---|---|---|
| **Workflows** | Owns the Exception subset | W cases are CRDM Workflows; they aggregate exceptions across domains |
| **Events** | Reads (all spine) | W subscribes to every module's published events and exception signals |
| **People** | Reads | Investigators, subjects of interest (employees, customers, vendors) |
| **Things** | Reads | Items, devices, fixtures involved in exceptions |
| **Places** | Reads | Locations where exceptions occurred |

W's posture: **W is a Workflow factory that derives Cases from detected exceptions across all spine domains.** It owns the exception-aggregation and case-escalation logic but no entity identities — those belong to other modules.

## ARTS mappings

ARTS does not define cross-domain exception detection or work-execution specifications. Canary generalizes Q's pattern:

| Canary construct | Definition | Reference |
|---|---|---|
| **Exception rule (domain-specific)** | Policy or invariant violation rule; evaluated per domain (LP rules, inventory rules, pricing rules, space rules, labor rules) | Q's frozen 37-rule catalog is the v1 reference; W generalizes the pattern |
| **Auto-escalation policy** | Threshold at which an exception automatically promotes to case creation (high-confidence violations skip triage) | Q's 6 auto-escalating rules provide the pattern; W applies it to all domains |
| **Case (cross-domain)** | Investigation root for any exception (theft, fraud, policy violation, inventory discrepancy, pricing error, labor anomaly, space failure) | Q's Fox case model; W generalizes to all domains |
| **Evidence chain** | Append-only, hash-chained audit log of case evidence across all domains | Q's Fox evidence model; W inherits the chain-of-custody discipline |

Cross-reference to ARTS:

- ARTS POSLog carries multi-domain context (transaction, customer, device, employee, location) — all ARTS dimensions feed into W exception detection

## Ledger relationship

**W is RECONCILER and CROSS-DOMAIN ANALYZER for all spine modules.**

W does NOT publish movements to the stock ledger. Instead:

- W **reads** all spine modules' published events and exception signals
- W **evaluates** each domain's rule catalog against observed events
- W **publishes** exception alerts (unconfirmed violations)
- W **escalates** high-confidence violations to case creation
- W **aggregates** exceptions across domains (e.g., is this customer involved in both inventory shrink and return fraud? Is this employee involved in both cash variance and missing inventory?)

The cross-domain aggregation is the load-bearing innovation. A single customer might trigger:
- **Q (Loss Prevention):** return fraud alert
- **S (Space, Range, Display):** over-capacity alert on planogram
- **L (Labor):** unusual scheduling request (time-off just before Q alert)
- **P (Pricing):** price-match abuse attempt

W reads all four signals, detects the pattern, and escalates to a single multi-domain case rather than four separate siloed cases.

Movement reads for exception detection:

- **Q (Loss Prevention) streams** — detection rule firings, auto-escalation signals
- **S (Space) streams** — capacity violations, over-stocking alerts
- **P (Pricing) streams** — price-discrepancy flags, markdown policy violations
- **L (Labor) streams** — schedule anomalies, time-entry variance, productivity outliers
- **D (Distribution) streams** — inventory movement exceptions (impossible quantities, missing receipts, transfer discrepancies)
- **J (Forecast) streams** — replenishment plan anomalies (demand forecast misses, order anomalies)
- **Stock ledger (F)** — any movement with violation flags or reason-code anomalies

**Perpetual-vs-period boundary.** Canary owns: cross-domain exception detection + case management. Merchant tool owns: compliance reporting + audit (merchant's external auditors). Default implementation route: `integrated-hybrid`. ([[../platform/perpetual-vs-period-boundary|principle]] · [[../platform/module-manifest-schema#implementation-route|manifest field]])

## Integrations

**Upstream sources** (exception publishers):

- **Q (Loss Prevention)** — Chirp detection rule firings; Fox case signals
- **S (Space, Range, Display)** — capacity violations, planogram conflict alerts
- **P (Pricing & Promotion)** — price-discrepancy flags, markdown policy violations
- **L (Labor & Workforce)** — schedule anomalies, time-entry variance, productivity outliers
- **D (Distribution)** — receipt discrepancies, transfer variances, RTV anomalies
- **J (Forecast & Order)** — forecast-vs-actual misses, order anomalies
- **F (Finance)** — invoice variances, GL reconciliation mismatches

**Downstream consumers** (W's outputs):

- **Investigator agents** — via W's case MCP tools
- **All spine modules** — W may request remediation (D posts adjustment, T issues refund, S revalidates planogram, etc.)
- **Escalation workflows** — cases that require external action (law enforcement, regulatory reporting)
- **Store operations dashboard** — exception summary, case status, escalation alerts

## Agent surface

W exposes MCP tool families for cross-domain exception management and case investigation:

- **Exception search and triage** — query exceptions by domain, time range, severity, subject; filter by rule category
- **Case CRUD and lifecycle** — create cases from exceptions, assign investigators, track status transitions
- **Evidence aggregation** — attach evidence from multiple domains to a single case; verify evidence chain integrity
- **Cross-domain correlation** — find all exceptions involving a specific subject (customer/employee/vendor) across all domains
- **Remediation routing** — request remediation (refund, restock, adjustment, payroll correction); track remediation status
- **Case analytics and reporting** — case velocity, resolution time, remediation success rate; identify patterns

## Security posture

- **Auth.** Case creation and investigator assignment require `investigator` or `manager` role. Evidence access is logged. MCP tool-level role checking enforced.
- **Tenant scoping.** Every exception and case carries `merchant_id`; every read is row-level-secured.
- **PII handling.** Cases may involve customer/employee subjects (PII). Access is logged via audit trail. Export is restricted.
- **Evidence integrity.** Inherited from Q's Fox model: INSERT-only evidence chains, hash-chained, trigger-enforced at the database layer.
- **Cross-domain visibility control.** A case may involve exceptions from multiple domains; visibility is based on investigator's role permissions (e.g., LP investigator may not see labor exceptions without explicit escalation).
- **Audit trail.** Every case transition, assignment, and evidence addition is logged. Chain-of-custody is maintained across all domains.

## Roadmap status

- **v3 (design)** — Cross-domain exception detection over Q, S, P, L, D, J, F streams. Auto-escalation to case creation for high-confidence violations. Case management with inherited Fox model (INSERT-only evidence chains). Cross-domain correlation and pattern detection. Read-only and restricted-write MCP tools for investigator workflows.
- **v3.1** — Automated remediation workflows (D automatically posts adjustments, T issues refunds, etc. based on case resolution).
- **v3.2** — Pattern learning (W learns common exception signatures and predicts escalation likelihood). Investigator-skill routing (assign cases to investigators with relevant expertise).
- **v3.3** — Predictive anomaly detection (W predicts exceptions before they occur, based on historical patterns and real-time signals).

## Open questions

1. **Cross-domain visibility scope.** Should an LP investigator (focused on loss prevention) be able to see all exceptions involving a subject, or only LP-domain exceptions? Per-merchant policy or role-based? Current assumption: role-based at v3; configurable per merchant at v3.1.
2. **Auto-escalation policy generalization.** Q has 6 auto-escalating rules (high signal-to-noise). How many rules should auto-escalate in other domains (S, P, L)? Domain-specific tuning or uniform threshold? Current assumption: domain-specific at v3.
3. **Remediation routing logic.** When W detects a pricing error in an online transaction, should it automatically route to P for price correction, or create a case for manual review? When inventory is missing, should it automatically route to D for adjustment? Current assumption: create cases; automated remediation deferred to v3.1.
4. **Subject linking across domains.** A customer in one exception and an employee in another may be the same person (e.g., employee-turned-customer or contractor-turned-vendor). Should W attempt to link subjects, or is that manual? Current assumption: manual at v3; automated linking deferred to v3.2.
5. **Time-range correlation window.** How long a time window should W use when correlating exceptions for cross-domain pattern detection? One hour? One day? One week? Per-merchant tuning? Current assumption: configurable window; default 24 hours.

## Related

- [[../platform/stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]]
- [[../platform/spine-13-prefix|The Canary Retail Spine — 13 Modules]]
- [[Q-loss-prevention|Q (Loss Prevention) — reference implementation for exception detection and case management]]
- [[S-space-range-display|S (Space, Range, Display)]]
- [[P-pricing-promotion|P (Pricing & Promotion)]]
- [[L-labor-workforce|L (Labor & Workforce)]]
- [[D-distribution|D (Distribution)]]
- [[J-forecast-order|J (Forecast & Order)]]
- [[F-finance|F (Finance)]]

## Sources

- [[../platform/spine-13-prefix|The Canary Retail Spine — 13 Modules (W is the capstone)]]
- [[Q-loss-prevention|Q (Loss Prevention) — Chirp detection architecture and Fox case management model]]

---

*Classification: confidential. Owner: GrowDirect LLC. Created 2026-04-24. W (Work Execution) is a v3 module spec within the Canary Retail Spine. It is design-stage; implementation is deferred pending v2 ring (C/D/F/J) stabilization and Q's evidence-chain infrastructure maturity.*

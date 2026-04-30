---
date: 2026-04-24
type: platform-doc
owner: GrowDirect LLC
classification: confidential
tags: [manifest, schema, agents-as-code, infrastructure-as-code, module-spine, declarative-infrastructure]
---

# Module Manifest Schema — Spine Modules as Code

**Governing principle.** The Canary Retail Spine is not just prose; it is
machine-readable, agent-executable infrastructure-as-code. Each of the 13 modules
ships with two artifacts: a prose article (narrative, decisions, context) and a
structured YAML manifest (tool signatures, entity schemas, ledger relationships,
dependencies). The manifest is the executable spec that agents and orchestration
systems read to discover what a module publishes, subscribes to, and reconciles
against.

---

## Why a Manifest

Documentation has three roles:
1. **Narration** — prose articles that explain decisions and reasoning to humans
2. **Reference** — the canonical spec humans and machines read to understand structure
3. **Execution** — the machine-readable spec that agents and CI/CD systems consume

The prose article handles (1) and part of (2). The manifest handles (2) fully and
(3) entirely. Both live together; the article references the manifest, the manifest
references the article.

### The Agent Consumption Cycle

When the VSM starts (or when modules are added at runtime), it:
1. Reads all module manifests in `Canary-Retail-Brain/modules/`
2. Discovers tool signatures, ledger relationships, integrity constraints
3. Registers MCP tools and tells Owl what this merchant can ask about
4. Grounds memory search in the manifest's purpose/entities/ledger_role

When the orchestrator runs (validating movement publisher/subscriber wiring):
1. Reads all manifests
2. For each module that publishes movements, checks subscribers are registered
3. For each subscriber, verifies it can consume the ledger verbs the publisher posts
4. Validates cycle-count reconciliation (conservat, matching, cost-method consistency)

When quality-assurance agent generates test fixtures:
1. Reads manifests
2. Extracts entity schemas + integrity constraints
3. Generates minimal valid row sets that exercise all constraints

No prose can be parsed this way. The manifest is the integration point.

---

## Schema Definition

Every module manifest is a YAML file named `<prefix>-<name>.manifest.yaml`. The
full schema (field by field):

### Root Fields

```yaml
prefix: string          # Single letter: T, R, N, A, Q, C, D, F, J, S, P, L, W
name: string            # Kebab-case slug, lowercase, alphanumeric + hyphen only
version: string         # Semantic version: v1, v2, v3, etc. (not 1.0.0 format)
status: enum            # shipping | design | implementation-pending | backlog
purpose: string         # One-sentence mission statement
```

### Entity Schema

```yaml
entities:
  - name: string                      # Table name (e.g., transactions, merchants)
    schema: enum                      # app | sales | metrics
    primary_columns:
      - name: string                  # Column name
        type: string                  # PostgreSQL type (UUID, INT, TEXT, BIGINT, etc.)
        nullable: boolean              # default: false
        default: string | null         # optional; e.g., uuid.uuid4, CURRENT_TIMESTAMP
    indexes:
      - name: string                  # Index name (e.g., idx_transactions_merchant)
        columns: [string]              # List of column names
        unique: boolean                 # default: false
    write_pattern: enum               # insert-only | append-only | 
                                      # mutable+soft-delete | mutable
    integrity_constraints:
      - type: enum                    # fk | unique | check | conservation
        columns: [string]              # Columns involved
        detail: string                 # Human-readable description
        enforcement: string             # database-trigger | application | runtime
```

### Ledger Relationship

```yaml
ledger_relationship:
  role: enum            # publisher | subscriber | reconciler | multiple
  verbs:
    - string            # List of verbs this module publishes/consumes:
                        # receipt, sale, return, rTV, transfer, adjustment,
                        # cycle_count, shrink, reclassification, cost_update, etc.
  impact: string        # One-sentence summary of how this module affects ledger
```

### Accounting Relationship

```yaml
accounting_relationship:
  otb_role: enum        # commits-against | consumes-headroom | publishes-eoh | n/a
  valuation_method_owner: boolean
                        # True if this module owns RIM vs Cost decision for
                        # any dimension; false otherwise
  cost_method_publisher: boolean
                        # True if this module publishes cost-update events
                        # (supplier variance, landed-cost changes)
  margin_calc_contributor: boolean
                        # True if this module's data feeds margin reporting
```

### ARTS Alignment

```yaml
arts_alignment:
  poslog_adoption: string             # Description of POSLog adoption (if any)
  customer_model_alignment: boolean   # Does this module adopt ARTS customer model
  device_model_alignment: boolean     # Does this module adopt ARTS device model
  site_model_alignment: boolean       # Does this module adopt ARTS site/location
                                      # model
  notes: string                       # Any caveats or differences from ARTS spec
```

### Integrations

```yaml
integrations:
  upstream:
    - module: string                  # Prefix of upstream module (e.g., T, R, N)
      relationship: string             # publishes_to_me | I_read_state_from |
                                      # I_reconcile_against
      verbs: [string]                 # Movement verbs involved (if ledger-based)
  downstream:
    - module: string                  # Prefix of downstream module
      relationship: string             # subscribes_to_me | reads_my_state |
                                      # reconciles_against_me
      verbs: [string]                 # Movement verbs involved
```

### MCP Tools

```yaml
mcp_tools:
  - name: string                      # MCP tool name (no canary- prefix)
    signature: string                 # Function signature as docstring
    params:
      - name: string
        type: string
        required: boolean
        description: string
    returns:
      - name: string
        type: string
        description: string
    idempotency: enum                 # idempotent | idempotent-on-key |
                                      # not-idempotent
    rate_limit: string                # e.g., 100 calls/minute (if applicable)
```

### Agent Role Bindings

```yaml
agent_role_bindings:
  - agent: string                     # Skill or agent name that composes this
                                      # module (e.g., canary-vsm, canary-verify)
    capabilities: [string]            # What capabilities this agent gains by
                                      # binding this module
```

### Dependencies

```yaml
dependencies:
  modules:
    - prefix: string                  # Module prefix
      read_only: boolean              # Does this module only read from it,
                                      # or write to it too?
      verbs: [string]                 # Ledger verbs involved
  external:
    - service: string                 # External service name (e.g., Square API)
      endpoint: string                # API or service endpoint
      rate_limit: string              # Rate limit if applicable
```

### Security

```yaml
security:
  auth:
    required: boolean                 # Does this module require authentication?
    method: enum                      # oauth | api-key | bearer-token | none
  tenant_scoping:
    primary_key: string               # Column that enforces tenant isolation
                                      # (e.g., merchant_id)
  pii_handling:
    categories: [string]              # customer-email, customer-phone,
                                      # employee-ssn, etc.
    retention_days: integer           # How long PII is retained (if any)
    encryption: boolean               # Is PII encrypted at rest?
```

### Implementation Route (design-time / per-module)

```yaml
implementation_route:
  primary: enum                       # legacy-native | package-integration |
                                      # integrated-hybrid | multi-route
  rationale: string                   # One-sentence justification for the choice
  perpetual_owner: string             # Which side owns the perpetual movement
                                      # layer at full cutover? (canary | merchant-system | shared)
  period_owner: string                # Which side owns the period-summary layer
                                      # at install (Phase 1)? (canary | merchant-system | shared)
  alternatives_considered: [string]   # List of route names evaluated and why
                                      # they were rejected (free-text)
  adr_reference: string               # Path to ADR case study if this decision
                                      # was formally evaluated (Morrisons frame)
```

**Field semantics — derived from the v2.F (Finance) ADR (`Canary-Retail-Brain/case-studies/canary-finance-architecture-options.md`):**

- **`legacy-native`** — Canary builds the module entirely native, owns both perpetual movement layer AND period-summary layer from day one. Pick this when no merchant-side equivalent exists with sufficient ledger-grade discipline (e.g., T transaction sealing). No cutover phase applies — Canary is system of record at install.
- **`package-integration`** — Module integrates to a merchant's existing package (QuickBooks, Xero, Gusto, Salesforce, etc.). Canary publishes movement events; merchant package owns the operational state. Pick this when the merchant already runs the system of record and just needs Canary's signal flowing into it.
- **`integrated-hybrid`** — At install, Canary owns the perpetual movement layer (computing in parallel); merchant's existing package owns the period-summary layer. The boundary lives at the perpetual-vs-period seam. **This is the Canary default** for v2/v3 modules. Subject to the staged-migration story below — the merchant cuts over from existing tool to Canary at their own pace.
- **`multi-route`** — Module supports more than one route; merchant chooses at install time. Use sparingly — increases test surface and support cost.

**Default for new modules:** `integrated-hybrid`. The Morrisons v2.F ADR established this as the architectural commitment that maximizes merchant adoption at install while preserving Canary's strategic perpetual-ledger position long-term.

### Cutover Status (runtime / per-merchant per-module)

The `implementation_route` is the design-time *shape* a module ships in.
Per merchant, each module also has a runtime *cutover phase* — where that
merchant currently sits on the parallel-run → modular-cutover → stock-ledger-swap
migration path defined in [[perpetual-vs-period-boundary]].

This is **not** a manifest-file field. It lives in per-merchant runtime
state (likely `app.merchant_module_cutover_status` table). Documenting the
shape here so module designers know what runtime state the system tracks:

```yaml
# Per-merchant per-module runtime state (not authored in manifest)
cutover_status:
  module: string                      # Module prefix (T, R, N, ...)
  merchant_id: UUID                   # Which merchant
  phase: enum                         # parallel-observer | partial-cutover | full-cutover
  cutover_date: timestamp             # When this merchant moved to current phase
  reconciliation_period_days: integer # How many days of clean reconciliation
                                      # preceded the most recent phase advance
  prior_system: string                # Free-text — what they used before
                                      # (e.g., "QuickBooks Online", "Excel only",
                                      # "Lightspeed Inventory")
  cutover_initiated_by: string        # merchant-self-service | sales-engineering |
                                      # automated-promotion-rule
```

**Default at install:** every module that is `legacy-native` starts at
`full-cutover` (Canary IS the only option). Every other module
(`package-integration` or `integrated-hybrid` or `multi-route`) starts at
`parallel-observer`.

**Phase advances are merchant-initiated**, never silently auto-promoted.
The system can suggest a phase advance when reconciliation has been clean
for N days, but the merchant must accept.

**Phase reverts are supported.** A merchant who cuts over a module to
Canary and decides 60 days later they want to go back to their prior tool
can revert that module to `parallel-observer` without losing history.

The `cutover_status` field is what the VSM reads to know which authority
to cite in answers (Canary's perpetual ledger vs the merchant's existing
tool's period summary). Different merchants of the same SKU profile may
get different VSM answers based on their cutover state.

---

## Example Manifest — T (Transaction Pipeline) v1

Below is the complete manifest for T, the Transaction Pipeline module, as a
worked example. Source of truth: `/Users/gclyle/Canary-Retail-Brain/modules/T-transaction-pipeline.md`
and Brain wiki `canary-module-t-transactions.md`.

See the next section (at end of file) for YAML.

---

## How Agents Consume Manifests

### VSM (Virtual Store Manager) at Startup

```python
# Pseudocode: Owl/VSM initialization
manifests = glob("Canary-Retail-Brain/modules/*.manifest.yaml")
for manifest_file in manifests:
    manifest = yaml.load(manifest_file)
    prefix, name = manifest['prefix'], manifest['name']
    
    # Register MCP tools
    for tool in manifest['mcp_tools']:
        owl.register_tool(f"canary-{prefix.lower()}", tool['name'])
    
    # Prime memory with module purpose
    memory.index(f"{prefix}: {manifest['purpose']}")
    
    # Validate ledger role
    if manifest['ledger_relationship']['role'] == 'publisher':
        owl.subscribe_to_movements(
            module=prefix,
            verbs=manifest['ledger_relationship']['verbs']
        )
```

At runtime, merchant asks: "Why is shrink up in dairy?"
- VSM router: classification = root_cause + shrink
- Memory search: "shrink" matches modules with ledger role = publisher
  or reconciler that touch shrink verb
- Results: D (Distribution), Q (Loss Prevention), F (Finance)
- VSM: composes calls to canary-distribution, canary-finance, stock-ledger
- Output: candidate causes with evidence

### Orchestrator (Movement Validation)

```python
# Validate publisher/subscriber wiring
manifests = glob("Canary-Retail-Brain/modules/*.manifest.yaml")
publishers = {m['prefix']: m for m in manifests 
              if m['ledger_relationship']['role'] in ['publisher', 'multiple']}

for pub_prefix, pub_manifest in publishers.items():
    pub_verbs = set(pub_manifest['ledger_relationship']['verbs'])
    
    for verb in pub_verbs:
        # Find all subscribers expecting this verb
        subscribers = find_subscribers_for(verb)
        for sub in subscribers:
            assert sub_prefix in [d['prefix'] for d in 
                    pub_manifest['dependencies']['modules']]
```

### Quality-Assurance Agent (Test Fixture Generation)

```python
# Generate minimal test fixtures
manifest = yaml.load("T-transaction-pipeline.manifest.yaml")

for entity in manifest['entities']:
    # Extract constraints
    constraints = entity['integrity_constraints']
    fk_constraints = [c for c in constraints if c['type'] == 'fk']
    unique_constraints = [c for c in constraints if c['type'] == 'unique']
    
    # Generate minimal valid rows
    rows = []
    for i in range(1, 5):  # 4 test rows
        row = {
            'id': uuid.uuid4(),
            'merchant_id': merchant_uuid,
            'created_at': datetime.now(),
            'transaction_date': datetime.now(),
            # ... populate columns per schema
        }
        # Ensure uniqueness constraints
        if unique_constraints:
            row['external_id'] = f"square-{i}-{uuid.uuid4()}"
        rows.append(row)
    
    # Verify all constraints
    for row in rows:
        assert_integrity(row, entity['integrity_constraints'])
```

---

## Lifecycle

### Authoring

Module manifest is authored alongside the prose article during the Design stage.
Ownership: module author + architect. QA: spec reviewer.

### Validation

In CI/CD:
1. Schema validation: `yq` or `pyyaml` against schema definition above
2. Cross-reference validation: every module in dependencies exists
3. Ledger validation: every verb in ledger_relationship is in stock-ledger.md
4. Tool validation: every MCP tool can be discovered in code

### Codegen (Future)

A future agent reads manifest and emits:
- SQLAlchemy model stubs (entities + columns + constraints)
- Alembic migration scaffolds (schema creation)
- MCP tool interface stubs (function signatures, docstrings)
- Test fixture factories (constraint-aware test data generators)

---

## Open Questions

### 1. Authorship: Manifest-First vs Code-First?

**Question:** Should manifests be written before code (spec-first) or extracted
from code (reverse-engineered)?

**Recommendation:** **Spec-first.** Manifest is written during Design stage,
side-by-side with prose SDD. Code is written TDD against the manifest. This
ensures the executable spec is canonical. Reverse-engineering fails when code
drifts (which it always does).

### 2. Versioning: Semantic, Major-Only, or Timestamp?

**Question:** How strictly should manifests be versioned? Can a v1.1 ship with
breaking changes to tool signatures?

**Recommendation:** **Semantic versioning at module level, immutable-patch at
tool level.** A module can move from v1 to v2 with new capabilities, but a
tool's signature (params + returns) is immutable once shipped. If a tool signature
changes, it's a new tool. This prevents merchant code from breaking at runtime.

### 3. Format: YAML, JSON, or Protocol Buffers?

**Question:** Is YAML the right serialization?

**Recommendation:** **Keep YAML.** It is human-editable, Git-friendly, and
widely supported. JSON is noisier for humans. Protocol Buffers add complexity
without benefit for this use case (manifests are small, non-streaming).

---

## Related

- [[stock-ledger|Stock Ledger — The Perpetual-Inventory Movement Ledger]] — the
  verbs and invariants manifests declare
- [[spine-13-prefix|The Canary Retail Spine — 13 Modules]] — module catalog
- [[crdm|CRDM — Canonical Retail Data Model]] — entity relationships
- [[../../GrowDirect/Brain/wiki/growdirect-viewpoint-virtual-store-manager|Viewpoint
  — The Virtual Store Manager]] — manifest consumers
- `Canary-Retail-Brain/modules/T-transaction-pipeline.manifest.yaml` — concrete
  example (this file, v1)

---

## Sources

- RMS (Retek Retail Management System, 2002) — perpetual-inventory ledger pattern
- ARTS Technical Specification — data model patterns (POSLog, Customer, Device,
  Site models)
- Tesco Technical Library — ledger verb taxonomy and period-close workflows
- GrowDirect Viewpoint — VSM + spine integration
- Stock Ledger specification — movement verbs, conservation/reconciliation invariants
- Canary-Retail-Brain modules — T/R/N/A/Q (v1), C/D/F/J (v2), S/P/L/W (v3)

---

*Module Manifest Schema v1.0*
*Last updated: 2026-04-24*

---
card-type: infra-capability
card-id: platform-retailer-lifecycle-test
card-version: 1
domain: platform
layer: cross-cutting
feeds:
  - module-t
  - module-j
  - module-c
  - module-p
  - module-d
  - module-f
  - module-q
  - module-a
  - module-l
  - module-w
  - module-r
  - module-n
  - module-s
receives: []
tags: [test, methodology, lifecycle, retailer, financial-plan, merchandise-plan, buy-plan, distribution, sales, burn-in]
status: approved
last-compiled: 2026-04-28
---

# Platform: Retailer Lifecycle Test Methodology

The retailer lifecycle test is the platform's canonical burn-in methodology. A synthetic retailer comes online from zero — financial plan through first sale through measurement cycle. Every transaction type, every item type, every attribute populated completely. No nulls, no shortcuts. The closed graph guarantees comprehensiveness: if a node exists on the spine, there is a test event for it.

## Purpose

The 13-module spine is a closed graph. The test methodology exploits that property: a complete retailer lifecycle exercises every edge in the graph exactly once in the correct sequence. If the test passes end-to-end, the platform is correct. If a module fails to receive its expected input, the gap is immediately locatable — not buried in a unit test assertion on a mocked data structure, but visible as a missing event in the lifecycle sequence.

This also enables the autonomous build cycle. As each module is implemented, it is inserted into the lifecycle test harness. The test runs continuously. Every new service that comes online either receives correct events from its upstream or it doesn't. There is no ambiguity about integration readiness.

## Lifecycle Sequence

The test data mirrors the real sequence a retailer follows from onboarding to steady-state operation:

```
1. Financial Plan          → Module F receives budget allocations, OTB wallet funded
2. Merchandise Plan        → Module S receives range and space plan by category
3. Buy Plan                → Module C receives commercial strategy, OTB committed
4. Purchase Orders         → Module J generates orders from forecast + buy plan
5. Distribution            → Module D receives POs, tracks inbound shipments
6. Receiving               → Module A logs received inventory, reconciles against PO
7. Price Setup             → Module P sets base prices and promotional rules
8. Device Onboarding       → Module N registers POS devices and locations
9. Workforce Schedule      → Module L schedules labor against forecast demand
10. Transactions           → Module T processes sales, returns, voids across all types
11. Customer Activity      → Module R logs loyalty earn, redemption, customer events
12. LP Events              → Module Q detects anomalies, Fox cases opened
13. Work Execution         → Module W dispatches tasks triggered by module events
14. Replenishment Cycle    → Module J generates next forecast, triggers reorder
15. Period Close           → Module F reconciles actuals against plan, surfaces variances
16. Measurement            → All modules report against their performance contracts
```

## Data Requirements

Every test event must be fully populated — every field, every attribute, every foreign key relationship. This is not optional. A sparse test payload that passes because nullable fields are ignored will fail in production where those fields carry real business meaning.

**Item attributes required at minimum:**
- SKU, description, UPC, cost, retail price, department, category, sub-category, vendor, unit of measure, pack size, season code, replenishment method, storage type

**Transaction types required:**
- Sale (cash, card, split tender), return (with receipt, without receipt), void, exchange, layaway, gift card purchase, gift card redemption, loyalty redemption, employee discount, manager override, no-sale

**Org coverage required:**
- At least one Region → two Districts → three Stores → multiple Departments
- At least two Buyers across different Departments
- At least one District LP, one Store Manager, one Head Office Finance role

## Autonomous Build Cycle

The lifecycle test harness enables continuous autonomous integration:

```
Agent builds module → inserts into test harness
  → Test runs lifecycle sequence
    → Module receives expected upstream events?
      YES → integration confirmed, SI gate criteria partially met
      NO  → gap surfaces immediately, agent identifies missing upstream dependency
```

The Controller tracks harness coverage as a network health metric. A module with 0% lifecycle test coverage cannot advance to Hardening. A module with 100% coverage has demonstrated it can receive, process, and emit every event type the spine sends it.

This is also how the platform self-improves in support mode: a new detection rule, a pricing strategy change, a commercial lever adjustment — insert the changed behavior into the lifecycle test, run the sequence, measure the delta against the baseline. The impact of any change is measurable before it ships.

## Invariants

- Test data is fully populated. No nullable field left null unless the business rule explicitly permits it in production.
- The lifecycle sequence runs in order. Module F must receive its budget allocation before Module C can commit OTB. The sequence is not parallelizable — it mirrors causal retail reality.
- Every module has a baseline score on the lifecycle test before it can enter Hardening. The baseline is the SLA floor for Service Introduction.
- The test harness is owned by the Controller agent. Individual domain agents may extend it for their module but cannot modify the core sequence.

## Related

- [[platform-thesis]] — the closed graph property that makes this methodology work
- [[merchant-org-hierarchy]] — org coverage requirements for the test data set
- [[category-hierarchy]] — item attribute requirements derive from the category hierarchy
- [[role-binding-model]] — role coverage across all hierarchy types required in test data

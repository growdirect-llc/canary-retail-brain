---
title: Platform — Deep Technical Reads
classification: confidential
---

# Platform — deep technical reads

This section holds deeper technical content for engineers, architects, and partners doing detailed integration design. Not required for a CIO read of the platform — see [Platform overview](../overview) for the front-door read.

## Contents

| Topic | What it covers |
|---|---|
| [spine-13-prefix](spine-13-prefix) | The 13-letter module spine, module dependency graph, build order |
| [differentiated-five-add-on](differentiated-five-add-on) | The V1 differentiated module set: T + R + N + A + Q |
| [perpetual-vs-period-boundary](perpetual-vs-period-boundary) | Phase migration model — observer mode → cutover → system of record |
| [retail-accounting-method](retail-accounting-method) | RIM vs Cost method, OTB as planning constraint, integrated-hybrid posture |
| [module-manifest-schema](module-manifest-schema) | Machine-readable module descriptor format |
| [satoshi-cost-accounting](satoshi-cost-accounting) | Sub-cent unit cost model — optional architectural direction |
| [satoshi-precision-operating-model](satoshi-precision-operating-model) | Full-stack Bitcoin standard — optional architectural direction |

## Reading order for engineers

1. **[spine-13-prefix](spine-13-prefix)** — orient on the module structure
2. **[differentiated-five-add-on](differentiated-five-add-on)** — understand which modules ship first and why
3. **[perpetual-vs-period-boundary](perpetual-vs-period-boundary)** — understand the migration discipline
4. **[retail-accounting-method](retail-accounting-method)** — understand the accounting choice
5. **[module-manifest-schema](module-manifest-schema)** — understand the machine-readable companion to module specs

## On the satoshi pages

[satoshi-cost-accounting](satoshi-cost-accounting) and [satoshi-precision-operating-model](satoshi-precision-operating-model) document architectural direction, not currently-implemented behavior. Per [Engineering posture](../../engineering/nfrs) "Optional Features," all Bitcoin / Lightning / blockchain-anchor features are env-gated and default off. The platform operates correctly with all of them disabled. These pages describe what the platform looks like when the merchant opts in. A merchant choosing operating-system mode without opting in to the Bitcoin standard never encounters these mechanisms — fiat MAC operates, the chain is internally hash-anchored, and standard ILWAC handles cost accounting.

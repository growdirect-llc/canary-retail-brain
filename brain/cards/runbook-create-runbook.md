---
card-type: runbook
card-id: runbook-create-runbook
card-version: 1
domain: platform
layer: cross-cutting
status: approved
tags: [runbook, meta, process, knowledge-management, agent-card-format]
last-compiled: 2026-04-29
---

## What this is

The procedure for creating a new runbook card. A runbook is required whenever a script, CLI procedure, or operational sequence is introduced that an agent will need to execute correctly across sessions. This card is the canonical reference for when and how to write one.

## When to run

Create a runbook card when **any** of the following is true:

- A new script is committed that agents will invoke (seeder, migration runner, deploy script, health check)
- A multi-step procedure exists that has caused confusion or rediscovery errors in a prior session
- A procedure has known failure modes worth capturing — if it has broken once, it will break again
- A procedure is environment-specific (laptop vs mini, Docker vs host) and the distinction is non-obvious
- An operational invariant exists that an agent might accidentally violate (e.g., "never run X while Y is running")

Do **not** create a runbook card for:
- One-off commands run once and never repeated
- Procedures fully documented in a script's `--help` output with no non-obvious failure modes
- Procedures that belong in an SDD as an acceptance criterion (those stay in the SDD)

## Preconditions

1. The procedure being documented is stable enough to commit — do not write a runbook for a script that is still changing rapidly
2. You have run the procedure at least once and know its actual failure modes, not hypothetical ones
3. A corresponding [[agent-card-format]] entry exists for `runbook` as a valid `card-type` (it does as of card-version 2 of agent-card-format)

## Canonical steps

```
1. Choose a card-id: runbook-<operation-name> in kebab-case
   Examples: runbook-memory-bus-seed, runbook-docker-startup, runbook-db-migrate

2. Create the file at Brain/wiki/cards/runbook-<operation-name>.md

3. Fill in required frontmatter:
   card-type: runbook
   card-id: runbook-<operation-name>
   card-version: 1
   domain: <platform | canary | cove | cross-cutting>
   layer: <cross-cutting | infra | domain>
   status: draft   ← start as draft; promote to approved after first successful use
   agent: ALX
   tags: [runbook, <relevant-keywords>]
   last-compiled: <today>
   needs-review: false

4. Fill in the body using this section order (omit sections that don't apply):
   ## What this is       ← one sentence
   ## When to run        ← specific triggers, not "whenever you need it"
   ## Preconditions      ← ordered; if unmet, procedure must not proceed
   ## Canonical steps    ← exact commands with expected output inline
   ## Verification       ← observable pass/fail signal
   ## Failure modes      ← symptom → cause → fix; confirmed failures only
   ## Invariants         ← what must never happen
   ## Related            ← links to the script file, infra card, dependent runbooks

5. Add the card to the directory in Brain/wiki/agent-card-format.md:
   | [Runbook: <Name>](cards/runbook-<name>.md) | runbook-<name> | runbook |

6. Commit with Brain/wiki/ changes — post-commit hook seeds it automatically
   git add Brain/wiki/cards/runbook-<name>.md Brain/wiki/agent-card-format.md
   git commit -m "feat(brain): add runbook card for <operation>"
```

## Verification

After committing:

```bash
# Confirm it seeded
tail -5 /tmp/memory-bus-seed.log
# Should show the new card as "new ... ok"

# Confirm it is recalled
# memory_recall("<key phrase from the runbook>") should return it at similarity > 0.70
```

## Failure modes

**Writing a runbook before the procedure is stable**
- Symptom: runbook is out of date within a session of creation
- Fix: use `status: draft` in frontmatter until the procedure has been executed successfully at least once in production; promote to `approved` after first verified use

**Runbook body too abstract — no actual commands**
- Symptom: card reads like a wiki article, not an operational reference; agent still has to guess commands
- Fix: every runbook must have a `## Canonical steps` section with copy-paste-ready commands; prose explanation belongs in `## What this is` or a wiki article, not in steps

**Runbook duplicates an SDD acceptance criterion**
- Symptom: card describes what the system should do, not how to operate it
- Fix: acceptance criteria stay in the SDD; runbooks document operating the system after it is built

## Invariants

- Every runbook card has a `## Canonical steps` section. A runbook without steps is a wiki article — rename or restructure it.
- Runbook cards capture confirmed failure modes only. Speculative failure modes belong in a design doc, not a runbook.
- `status: draft` until the procedure has been executed successfully in production. `status: approved` is a quality signal, not a formality.
- When a script changes in a way that affects invocation, failure modes, or invariants — the runbook card version bumps in the same commit.

## Related

- [[agent-card-format]] — the full card format spec; runbook is one card-type within it
- [[runbook-memory-bus-seed]] — example runbook (script invocation)
- [[runbook-docker-startup]] — example runbook (environment setup)
- [[runbook-brain-wiki-commit]] — example runbook (git workflow)

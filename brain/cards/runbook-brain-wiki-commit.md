---
card-type: runbook
card-id: runbook-brain-wiki-commit
card-version: 1
domain: platform
layer: cross-cutting
status: approved
tags: [runbook, brain, wiki, git, post-commit, hook, seeding, incremental]
last-compiled: 2026-04-29
---

## What this is

The procedure for committing changes to `Brain/wiki/` and verifying that the post-commit hook correctly triggers an incremental memory bus seed. Brain wiki content is not live in `memory_recall()` until it has been seeded.

## When to run

Any commit that touches files under `Brain/wiki/` — new cards, updated cards, new wiki articles, updated articles. The hook fires automatically, but verification is the agent's responsibility.

## Preconditions

1. Docker shared infra is up and memory bus is reachable (see [[runbook-docker-startup]])
2. Ollama is warm on the laptop — the post-commit hook runs `seed_standalone.py` which calls Ollama
3. No concurrent seed process is running: `pgrep -f seed_standalone.py` returns empty

## Canonical steps

```bash
# 1. Stage Brain/wiki/ changes (specific files preferred over -A)
git add Brain/wiki/cards/my-new-card.md

# 2. Commit — the post-commit hook fires automatically
git commit -m "feat(brain): add runbook card for X"

# Hook output (appears after commit):
# [memory-bus] Brain/wiki changes detected — running incremental seed...
# [memory-bus] Seeder running in background. Log: /tmp/memory-bus-seed.log

# 3. Monitor the background seed
tail -f /tmp/memory-bus-seed.log
# Wait for: Done: N new, M updated, 0 skipped (empty), 0 failed

# 4. If Brain/wiki/ was not the only change and you want to force a manual seed:
python3 services/memory-bus/scripts/seed_standalone.py
```

## Verification

```bash
# Confirm the new card appears in alx_memories
docker exec growdirect_postgres psql -U growdirect -d growdirect_memory -c \
  "SELECT metadata->>'source_file', created_at FROM alx_memories WHERE metadata->>'source_file' LIKE '%my-new-card%';"

# Live recall test
# memory_recall("key phrase from the new card") should return it at similarity > 0.75
```

## Failure modes

**Hook did not fire — no `[memory-bus]` output after commit**
- Symptom: commit succeeded but no hook output
- Cause: hook not installed, or hook file is not executable
- Fix:
  ```bash
  # Check hook exists and is executable
  ls -la .git/hooks/post-commit
  # If missing, reinstall:
  cat > .git/hooks/post-commit << 'EOF'
  #!/bin/sh
  CHANGED=$(git diff --name-only HEAD~1 HEAD 2>/dev/null | grep "^Brain/wiki/")
  if [ -n "$CHANGED" ]; then
    echo "[memory-bus] Brain/wiki changes detected — running incremental seed..."
    cd "$(git rev-parse --show-toplevel)"
    python3 services/memory-bus/scripts/seed_standalone.py >> /tmp/memory-bus-seed.log 2>&1 &
    echo "[memory-bus] Seeder running in background. Log: /tmp/memory-bus-seed.log"
  fi
  EOF
  chmod +x .git/hooks/post-commit
  ```
- Note: hooks are not tracked by git — must be reinstalled after a fresh clone

**Hook fired but seed failed silently**
- Symptom: hook output appeared, but `tail /tmp/memory-bus-seed.log` shows embedding failures or the card is missing from `alx_memories`
- Cause: Ollama cold, lock conflict, or DB connection issue
- Fix: run `python3 services/memory-bus/scripts/seed_standalone.py` manually and watch stdout for errors

**Lock held from hook firing during a manual seed**
- Symptom: `ERROR: Another seed process is already running`
- Cause: post-commit hook triggered an incremental seed that is still running while you try to run manually
- Fix: `tail -f /tmp/memory-bus-seed.log` to watch the background seed finish, then run manually if needed; or `pgrep -f seed_standalone.py` and wait

**Multiple post-commit hooks fired from a batch commit touching many cards**
- Symptom: multiple background seeds competing; lock held errors in log
- Cause: each commit in a rebase/squash sequence fires the hook
- Fix: the `fcntl.flock` in `seed_standalone.py` prevents concurrent runs — the second hook invocation will exit immediately with the lock error and log it. The first completes. Run a manual incremental seed after the batch to catch any missed files.

## Invariants

- `Brain/wiki/` changes are not live in `memory_recall()` until seeded. Do not assume a committed card is queryable without verifying.
- The hook runs `seed_standalone.py` in the background — it does not block the commit or the shell.
- SDD changes (`docs/sdds/`, `docs/superpowers/`) do **not** trigger the hook. Run the seeder manually after SDD commits.
- The hook is not tracked by git. It must be reinstalled after a fresh clone of the repo.

## Related

- [[runbook-memory-bus-seed]] — the seeder this hook invokes
- [[runbook-docker-startup]] — precondition for this procedure
- `.git/hooks/post-commit` — the hook file (not tracked, must reinstall on fresh clone)

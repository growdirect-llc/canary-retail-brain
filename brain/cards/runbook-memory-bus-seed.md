---
card-type: runbook
card-id: runbook-memory-bus-seed
card-version: 1
domain: platform
layer: cross-cutting
status: approved
tags: [runbook, memory-bus, seeding, pgvector, alx_memories, seed_standalone]
last-compiled: 2026-04-29
---

## What this is

The procedure for seeding Brain/wiki content, agent cards, and SDDs into `alx_memories` so that `memory_recall()` can surface them. Runs on the laptop (Ollama required). The mini never runs this — it restores from `brain.sql`.

## When to run

- After adding or modifying any file in `Brain/wiki/` (including `cards/`)
- After adding or modifying any SDD in `docs/sdds/` or `docs/superpowers/`
- The post-commit hook fires automatically for `Brain/wiki/` changes — but run manually after SDD changes or if the hook is known to have missed a run
- Never run on the mini — no Ollama at runtime there

## Preconditions

1. Docker shared infra stack is up: `cd ~/GrowDirect/devops && docker compose up -d`
2. Ollama is warm — verify with `curl -s http://127.0.0.1:11434/api/tags | python3 -m json.tool | grep name`; if no models listed, wait or run a warm-up embed
3. `growdirect_memory` database is reachable: `docker exec growdirect_postgres psql -U growdirect -d growdirect_memory -c "\dt"` must return the `alx_memories` table
4. No other seed process is running: check with `pgrep -f seed_standalone.py`; if one is live, wait for it

## Canonical steps

```bash
# Incremental (default) — only embeds new/modified files
python3 services/memory-bus/scripts/seed_standalone.py

# Expected output pattern:
# Found N files — X up to date, Y to embed
# [  1/Y] [new   ] Brain/wiki/cards/some-card.md ... ok
# Done: Y new, 0 updated, 0 skipped (empty), 0 failed

# Full reseed — drops all session_id='seed-standalone' rows, re-embeds everything
python3 services/memory-bus/scripts/seed_standalone.py --drop-first

# Dry run — preview what would be seeded without writing anything
python3 services/memory-bus/scripts/seed_standalone.py --dry-run
```

**Target table:** `alx_memories` with `session_id = 'seed-standalone'`. The script writes to `alx_memories` — this is the table `memory_recall()` queries. Never write to `seed_embeddings`; that table is a deprecated backup.

## Verification

```bash
# Count seed-standalone rows
docker exec growdirect_postgres psql -U growdirect -d growdirect_memory -c \
  "SELECT count(*) FROM alx_memories WHERE session_id = 'seed-standalone';"

# Confirm a specific card was seeded
docker exec growdirect_postgres psql -U growdirect -d growdirect_memory -c \
  "SELECT source_file FROM (SELECT metadata->>'source_file' as source_file FROM alx_memories WHERE session_id = 'seed-standalone') t WHERE source_file LIKE '%cards/%' ORDER BY 1;"

# Live recall test via MCP (requires memory bus running)
# memory_recall("ALX viable system model VSM") should return platform-alx-vsm.md at similarity > 0.75
```

## Failure modes

**Ollama timeout / embedding failed**
- Symptom: `WARN: embedding failed — Read timeout` or high failed count in final summary
- Cause: Ollama model cold (not loaded into VRAM)
- Fix: warm up with `curl -s http://127.0.0.1:11434/api/embed -d '{"model":"qwen3-embedding:8b","input":"test"}' | head -1`, then rerun the seeder

**Lock conflict: another seed process is running**
- Symptom: `ERROR: Another seed process is already running (lock held at /tmp/growdirect-seed.lock)`
- Cause: post-commit hook fired an incremental seed that hasn't finished, or a previous seed crashed without releasing the lock
- Fix: `pgrep -f seed_standalone.py` — if a live process exists, wait; if no process exists, `rm /tmp/growdirect-seed.lock` then rerun

**Rows seeded but memory_recall returns stale results**
- Symptom: recall returns low-similarity (< 0.65) old content instead of newly seeded cards
- Cause: memory bus container is stale (cached connection pool, not picking up new rows)
- Fix: `docker restart growdirect_memory_bus && sleep 5` then re-test recall

**`alx_memories_memory_type_check` constraint violation**
- Symptom: `ERROR: new row for relation "alx_memories" violates check constraint`
- Cause: SOURCES in `seed_standalone.py` has an invalid `memory_type` value
- Fix: valid types are `decision · finding · context · architecture · session_summary · procedure · context_block · work_product · team_profile · foundation` — update the SOURCES dict

## Invariants

- The seeder writes only to `alx_memories`. Never to `seed_embeddings`.
- `--drop-first` deletes only `session_id = 'seed-standalone'` rows — it does not touch `seed-clean` or any agent-session rows.
- Ollama must be the Docker container (`growdirect_ollama`), not a native host install. The seeder targets `http://127.0.0.1:11434` which maps to the container port.
- The seeder runs only on the laptop. The mini restores from `brain.sql`.

## Related

- [[agent-card-format]] — the card format this runbook is part of
- [[runbook-docker-startup]] — must run before this procedure if Docker is down
- `services/memory-bus/scripts/seed_standalone.py` — the script this runbook documents
- `docs/sdds/canary/alx.md` — ALX/memory-bus architecture SDD

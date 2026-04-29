---
card-type: runbook
card-id: runbook-docker-startup
card-version: 1
domain: platform
layer: cross-cutting
status: approved
tags: [runbook, docker, startup, devops, memory-bus, canary-go, mini, laptop]
last-compiled: 2026-04-29
---

## What this is

The procedure for bringing up the GrowDirect Docker stacks in the correct order on either machine. There are two stacks: shared infra (always first) and app stacks (after). The mini has an additional Canary Go stack.

## When to run

- At the start of any state session on the mini — Docker must be confirmed up before any dispatch work begins (Mini Docker Gate rule)
- Any time `curl -s http://127.0.0.1:8003/mcp` returns no response or connection refused
- After a machine restart
- After `docker compose down` was run for any reason

## Preconditions

1. Docker Desktop is running (Mac: check the whale icon in the menu bar)
2. You are in the correct repo: `git -C ~/GrowDirect rev-parse --show-toplevel` should return the GrowDirect path

## Canonical steps

### Laptop

```bash
# 1. Shared infra (postgres, valkey, ollama, pgadmin, memory-bus)
cd ~/GrowDirect/devops && docker compose up -d

# 2. Verify memory bus is reachable
curl -s http://127.0.0.1:8003/mcp | head -1
# Expected: {"jsonrpc":"2.0"... or similar MCP response (not empty, not connection refused)
```

### Mac mini

```bash
# 1. Shared infra
cd ~/GrowDirect/devops && docker compose up -d

# 2. Canary Go stack (compose lives in deploy/, not devops/)
cd ~/GrowDirect/CanaryGo && docker compose -f deploy/docker-compose.yml up -d

# 3. Verify memory bus reachable
curl -s http://127.0.0.1:8003/mcp | head -1
# Must return a response. If not: diagnose before proceeding with any dispatch.
```

### Health check (both machines)

```bash
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "postgres|valkey|ollama|memory_bus"
# All four should show "Up" — none should show "unhealthy" or "Restarting"
```

## Verification

```bash
# Memory bus alive
curl -s http://127.0.0.1:8003/mcp | head -1
# Non-empty response = bus is up

# Postgres reachable
docker exec growdirect_postgres psql -U growdirect -d growdirect_memory -c "SELECT 1;" 
# Should return: (1 row)

# Ollama loaded (laptop only)
curl -s http://127.0.0.1:11434/api/tags | python3 -c "import sys,json; m=json.load(sys.stdin)['models']; print(f'{len(m)} models loaded')"
# Should show at least 1 model
```

## Failure modes

**Memory bus unhealthy after `docker compose up`**
- Symptom: `docker ps` shows `growdirect_memory_bus` as `(unhealthy)`
- Cause: memory bus started before postgres was fully ready (startup race)
- Fix: `docker restart growdirect_memory_bus` — the bus will reconnect on restart

**Ollama restart kills a running seed**
- Symptom: seed process fails mid-run with embedding errors after Ollama restart
- Cause: `docker compose up -d` restarted Ollama because its healthcheck changed
- Fix: never restart Ollama while a seed is running; check `pgrep -f seed_standalone.py` first

**`POSTGRES_PASSWORD` missing error during `docker compose up`**
- Symptom: `error while interpolating services.postgres.environment: variable POSTGRES_PASSWORD is not set`
- Cause: `.env` file missing from `devops/`
- Fix: use `docker restart <container>` for individual container restarts rather than `docker compose up` if `.env` is absent; or restore `.env` from the project secrets store

**`docker compose up` for Canary Go fails on mini**
- Symptom: `no configuration file provided: not found`
- Cause: running from wrong directory or wrong `-f` flag
- Fix: compose file is at `CanaryGo/deploy/docker-compose.yml` — always specify `-f deploy/docker-compose.yml` from the `CanaryGo/` root

## Invariants

- Shared infra stack always starts before any app stack.
- Memory bus health check must pass before any dispatch work on the mini.
- Never restart Ollama while `seed_standalone.py` is running.
- The mini never runs the seeder (`seed_standalone.py`) — Ollama is not a runtime dependency on the mini.

## Related

- [[runbook-memory-bus-seed]] — procedure that depends on this stack being up
- [[platform-alx-vsm]] — ALX's operating environment; Docker is the runtime
- `devops/docker-compose.yml` — shared infra compose file
- `CanaryGo/deploy/docker-compose.yml` — Canary Go stack (mini only)

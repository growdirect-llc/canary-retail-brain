---
card-type: runbook
card-id: runbook-cowork-memory-bus-setup
card-version: 2
domain: platform
layer: cross-cutting
status: approved
tags: [memory-bus, cowork, mcp, configuration, setup, pgvector, claude-desktop]
last-compiled: 2026-04-29
---

## What this is

The procedure for wiring the GrowDirect Memory Bus (ALX) into Cowork mode so that memory tools are available in every Cowork session.

## Purpose

Cowork reads MCP servers from `claude_desktop_config.json`, not from project-level `.mcp.json` files. The memory-bus is defined only in project `.mcp.json` files for Claude Code CLI use. Without this procedure, Cowork sessions have no access to `memory_recall`, `memory_store`, or any other ALX tools.

## When to run

Run this procedure when any of the following is true:

- A new Mac or fresh Claude install is set up and Cowork sessions cannot call memory tools
- `claude_desktop_config.json` has been reset or overwritten (e.g. after a Claude app update)
- A new developer joins and needs ALX access in their Cowork sessions
- Memory bus tools are not appearing in the Cowork deferred tools list after a session start

Do **not** run if memory-bus tools are already present in the Cowork deferred tools list — check first.

## Preconditions

1. The memory-bus Docker service is running: `docker ps | grep growdirect_memory_bus` returns a running container
2. Port 8003 is bound: `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8003/mcp` returns `406` (not 000 or connection refused)
3. You have write access to `~/Library/Application Support/Claude/claude_desktop_config.json`
4. The Cowork desktop app is installed and has been launched at least once (so the config file exists)
5. Node.js and npm are installed: `node --version` and `npm --version` both return version strings. The `mcp-remote` package is fetched via `npx` on first use — no explicit install required, but npm must be present.

## Canonical steps

**Step 1 — Verify the service is reachable**
```bash
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8003/mcp
```
Expected output: `406`
A `406` means the server is up and rejecting requests that lack the required `Accept` headers — this is correct behaviour. `000` or `Connection refused` means the Docker stack is not running.

**Step 2 — Add memory-bus to claude_desktop_config.json**

> **Critical format note:** Cowork desktop app only supports stdio-based MCP servers — it cannot use `type: "http"` entries (that format is Claude Code CLI only). The correct approach is `mcp-remote`, an npm package that wraps the HTTP MCP server as a stdio process Cowork can launch.

```bash
python3 - <<'EOF'
import json

path = '/Users/{USERNAME}/Library/Application Support/Claude/claude_desktop_config.json'
with open(path, 'r') as f:
    config = json.load(f)

config.setdefault('mcpServers', {})['memory-bus'] = {
    'command': 'npx',
    'args': ['mcp-remote', 'http://127.0.0.1:8003/mcp']
}

with open(path, 'w') as f:
    json.dump(config, f, indent=2)

print('Done')
EOF
```
Replace `{USERNAME}` with the macOS username (e.g. `gclyle`).
Expected output: `Done`

**Step 3 — Verify the config was written correctly**
```bash
python3 -c "
import json
with open('/Users/{USERNAME}/Library/Application Support/Claude/claude_desktop_config.json') as f:
    d = json.load(f)
print(json.dumps(d.get('mcpServers', {}), indent=2))
"
```
Expected output:
```json
{
  "memory-bus": {
    "command": "npx",
    "args": ["mcp-remote", "http://127.0.0.1:8003/mcp"]
  }
}
```

**Step 4 — Restart the Cowork desktop app**
Quit and relaunch the Claude desktop app. The new MCP server is only loaded at startup.

**Step 5 — Confirm tools are available in a new Cowork session**
In a new Cowork session, ask: *"list your available MCP tools"* or look for `memory-bus` tools in the deferred tools list in the system reminder. You should see tools named with the `memory-bus` prefix.

## Verification

Perform a live recall to confirm the connection is end-to-end functional. In a Cowork session after restart:

1. Open a new session
2. Ask Claude: *"use the memory-bus to recall 'meta runbook'"*
3. Expected: Claude returns the `runbook-create-runbook` card content

Alternatively, run a raw health check from Terminal before restarting:
```bash
# Step 1 — Initialize a session and capture session ID
SESSION=$(curl -si -X POST 'http://127.0.0.1:8003/mcp' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' \
  | grep -i mcp-session-id | awk '{print $2}' | tr -d '\r')
echo "Session: $SESSION"

# Step 2 — Run a recall
curl -s -X POST 'http://127.0.0.1:8003/mcp' \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H "mcp-session-id: $SESSION" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"memory_recall","arguments":{"query":"meta runbook","limit":1,"api_key":"growdirect-memory-dev-key"}}}' \
  | python3 -c "
import sys, json, re
raw = sys.stdin.read()
m = re.search(r'data: (.+)', raw)
d = json.loads(m.group(1))
r = json.loads(d['result']['content'][0]['text'])
print('PASS — matches:', len(r['matches']))
"
```
Expected output: `PASS — matches: 1`

## Failure modes

**Symptom:** `curl` to port 8003 returns `000` or `Connection refused`
**Cause:** Docker stack is not running or the memory-bus container has exited
**Fix:** Run `docker compose -f /Users/{USERNAME}/GrowDirect/docker-compose.yml up -d memory-bus` and wait 10 seconds, then retry step 1.

---

**Symptom:** Config write returns `FileNotFoundError`
**Cause:** Claude desktop app has never been launched — the config file does not exist yet
**Fix:** Launch the Claude desktop app once, let it initialise, then retry step 2.

---

**Symptom:** Memory-bus tools do not appear in Cowork deferred tools list after restart
**Cause (a):** The config was written correctly but `mcpServers` was accidentally nested inside `preferences` rather than at the top level
**Fix:** Open `claude_desktop_config.json`, confirm `mcpServers` is a top-level key alongside `preferences`. If it is nested inside `preferences`, cut it out and paste it at the top level. Restart again.

**Cause (b):** The entry was written with `"type": "http"` format instead of the `mcp-remote` stdio format
**Fix:** Replace the entry. The `type: "http"` format is for Claude Code CLI (`.mcp.json`) only — Cowork desktop does not support it. The correct format is:
```json
"memory-bus": {
  "command": "npx",
  "args": ["mcp-remote", "http://127.0.0.1:8003/mcp"]
}
```

---

**Symptom:** Cowork session shows MCP load error dialog for memory-bus
**Cause:** `npx` is not on the PATH that Cowork sees, or npm is not installed
**Fix:** Confirm `which npx` returns a path in Terminal. If Node is installed via nvm, the shell profile may not be loaded by desktop apps. Workaround: use the absolute path to npx (e.g. `/Users/{USERNAME}/.nvm/versions/node/<version>/bin/npx`) in the `command` field instead of `"npx"`.

---

**Symptom:** `memory_recall` returns `{"error": "invalid api key"}`
**Cause:** The `api_key` parameter was omitted or the key value has changed
**Fix:** Pass `api_key: "growdirect-memory-dev-key"` explicitly in every tool call. The authoritative key is in `GrowDirect/services/memory-bus/memory_bus/config.py`.

---

**Symptom:** Session-start returns `{"error": "Missing session ID"}`
**Cause:** Calling a tool endpoint directly without first completing the MCP `initialize` handshake
**Fix:** Always call `initialize` first to obtain a session ID, then pass it as the `mcp-session-id` header on all subsequent calls. See the verification curl block above.

## Invariants

- `mcpServers` must be a top-level key in `claude_desktop_config.json` — never nested inside `preferences`
- The memory-bus Docker container must be running before the Cowork app starts; MCP connection errors at startup are not retried automatically
- Never commit `growdirect-memory-dev-key` to a public repository — it is a development key only

## Related

- [[agent-card-format]] — format spec all cards including this one follow
- [[runbook-create-runbook]] — meta procedure for when and how to write a runbook card

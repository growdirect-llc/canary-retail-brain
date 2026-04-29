---
type: process-decomp
artifact: l4-spec
module: T — Transaction Pipeline (Category A L3s only)
pass-date: 2026-04-28
source: GRO-670 / GRO-675
method: Track A — Python codebase translation
python-sources:
  - Canary/canary/services/tsp/consumers/sub1_seal.py
  - Canary/canary/services/tsp/consumers/sub2_parse.py
  - Canary/canary/services/tsp/consumers/sub3_merkle.py
  - Canary/canary/services/tsp/consumers/sub4_detect.py
  - Canary/canary/services/tsp/merkle.py
  - Canary/canary/services/tsp/stream_publisher.py
  - Canary/canary/services/tsp/tools.py
  - Canary/canary/services/evidence_chain.py
confidence: HIGH — all L4s derived from production code; patent-critical invariants annotated
note: Category B T L3s (T.1 ingestion, T.3 parsing, T.6 backfill) sourced from Counterpoint API docs — see CRB-GAP-LIST.md
---

# CRB L4 Spec — Module T: Transaction Pipeline (Category A)

**Scope:** This file covers only Category A L3s in Module T — the evidentiary layer, canonical event publication, Merkle anchoring, and substrate contracts. Category B L3s (T.1 ingestion, T.3 parsing, T.6 backfill replay) are sourced from NCR/Counterpoint API documentation; see CRB-L4-FILL-PLAN.md Track B.

---

## T.2 — Evidence Pipeline (Category A: T.2.3, T.2.4, T.2.5, T.2.6)

### T.2.3 — Hash-Before-Parse

**Source:** `tsp/consumers/sub1_seal.py` → `process_message()`  
**Patent significance:** The ordering constraint (hash verification BEFORE JSON parse) is the basis for patent application #63/991,596. This ordering must not be changed in the Go implementation.

**PRD reference:** TSP-03 v1.2 §228-282, Processing sequence Steps 2-3

| L4 ID | Activity | Implementation Detail |
|-------|----------|-----------------------|
| T.2.3.1 | Receive stream message | `XREADGROUP sub1-seal` → message with 9 fields: event_id, merchant_id, source, source_event_id, event_type, event_hash, raw_payload, received_at, parse_failed |
| T.2.3.2 | Validate required fields | Check all of: event_id, merchant_id, source, event_hash, raw_payload, received_at are non-empty; publish to dead_letter on missing field |
| T.2.3.3 | Recompute event hash | `SHA-256(raw_payload.encode('utf-8'))` → compare hex digest to event_hash field |
| T.2.3.4 | Hash mismatch handling | On mismatch: log CRITICAL; publish to `canary:dead_letter` stream; do NOT XACK; return False |
| T.2.3.5 | Parse only after hash match | JSON-decode raw_payload after hash verified — NOT before. This is the invariant. |

### T.2.4 — Seal Record Write

**Source:** `tsp/consumers/sub1_seal.py` Steps 4-8; `evidence_chain.py`  
**Invariant:** EvidenceRecord is INSERT-only. No UPDATE, no DELETE path anywhere in the codebase.  
**Invariant:** chain_hash computed by PostgreSQL trigger `compute_entry_hash()` BEFORE INSERT (P0-3, B-001). Application code sets event_hash only; trigger computes chain_hash from previous record.

| L4 ID | Activity | Implementation Detail |
|-------|----------|-----------------------|
| T.2.4.1 | Acquire advisory lock | `pg_try_advisory_lock(merchant_id_hash)` per merchant_id before chain hash computation |
| T.2.4.2 | Read previous chain hash | `SELECT chain_hash FROM evidence_records WHERE merchant_id=? ORDER BY sealed_at DESC LIMIT 1` |
| T.2.4.3 | Compute chain hash (application layer — pre-trigger era) | `compute_chain_hash(event_hash: bytes, previous_chain_hash: Optional[bytes]) → bytes` Genesis: `SHA-256(event_hash)`. Subsequent: `SHA-256(bytes(prev) + bytes(event_hash))` — raw BYTEA concatenation, NO delimiter |
| T.2.4.4 | INSERT evidence record | Model: EvidenceRecord. Fields: event_id, merchant_id, source, source_event_id, event_type, event_hash (BYTEA), raw_payload, received_at, sealed_at=now(). chain_hash field populated by trigger. |
| T.2.4.5 | XACK message | Only after successful INSERT. On exception: do NOT XACK (message redelivered by Valkey). |
| T.2.4.6 | Release advisory lock | In finally block — always release even on error |

**`compute_chain_hash()` contract (evidence_chain.py):**
```
Genesis record (previous_chain_hash is None):
  chain_hash = SHA-256(event_hash)

Subsequent record:
  chain_hash = SHA-256(bytes(previous_chain_hash) + bytes(event_hash))
  # Raw BYTEA concatenation. No pipe, no delimiter, no encoding.
```

### T.2.5 — Fanout Routing

**Source:** `tsp/stream_publisher.py`, sub1/sub2/sub3/sub4 consumer groups  
**Architecture:** One Valkey stream (`canary:events`, DB 4). Three independent consumer groups read in parallel. Each group maintains its own offset.

| L4 ID | Activity | Implementation Detail |
|-------|----------|-----------------------|
| T.2.5.1 | Initialize consumer groups | `init_consumer_groups()`: XGROUP CREATE canary:events sub1-seal $ MKSTREAM; XGROUP CREATE canary:events sub2-parse $ MKSTREAM; XGROUP CREATE canary:events sub3-merkle $ MKSTREAM. MUST run before TSP-01 starts publishing. |
| T.2.5.2 | sub1-seal: hash → seal | Consumes all events; verifies hash; writes EvidenceRecord; XACK |
| T.2.5.3 | sub2-parse: parse → CRDM | Consumes all events; routes by event_type via webhook_dispatch registry; writes CRDM models to canary_sales; publishes to detection stream for LP-critical events |
| T.2.5.4 | sub3-merkle: accumulate → tree | Consumes all events; accumulates event_hashes in Valkey sorted set; builds Merkle tree on threshold; does NOT XACK individual events until batch commits |
| T.2.5.5 | sub4-detect: detect | Consumes LP-critical events from detection stream; routes to Chirp rule engine |

**Stream publisher contract (9-field message schema, TSP-01):**
- `event_id` — UUID, platform-generated
- `merchant_id` — tenant identifier
- `source` — "square", "counterpoint", etc.
- `source_event_id` — upstream event ID for dedup
- `event_type` — canonical event type (SALE, RETURN, VOID, etc.)
- `event_hash` — SHA-256 hex of raw_payload
- `raw_payload` — original webhook body, unmodified
- `received_at` — ISO-8601 timestamp
- `parse_failed` — "true" / "false"

**Stream client config:**
- DB 4 (isolated from cache DBs 0-3 — prevents volatile-lru eviction of stream data)
- socket_timeout=30s (must exceed XREADGROUP block_ms of 5s)
- socket_connect_timeout=5s

### T.2.6 — Mutation-Lock

**Source:** `tsp/consumers/sub1_seal.py`; PostgreSQL model constraints

| L4 ID | Activity | Implementation Detail |
|-------|----------|-----------------------|
| T.2.6.1 | INSERT-only evidence | EvidenceRecord has no UPDATE path. No `db.query(EvidenceRecord).filter().update()` anywhere in codebase. |
| T.2.6.2 | PostgreSQL trigger owns chain_hash | `compute_entry_hash()` trigger runs BEFORE INSERT on evidence_records. Application MUST NOT set chain_hash or previous_chain_hash — trigger reads previous record and computes. (P0-3, B-001) |
| T.2.6.3 | Advisory lock per merchant | `pg_try_advisory_lock()` before any chain operation — prevents concurrent hash chain race condition |
| T.2.6.4 | Dead-letter on integrity failure | Failed XACK leaves message in pending entries; Valkey XAUTOCLAIM redelivers for retry |

---

## T.4 — Canonical Event Publication (T.4.1–T.4.9)

**Source:** `tsp/stream_publisher.py`, `tsp/enrichers/square.py`

The canonical event types the platform publishes. Each maps to a specific CRDM write in sub2-parse. Counterpoint enricher will parallel the Square enricher — same event type taxonomy, different field mapping.

| L4 ID | Event Type | CRDM Target | Notes |
|-------|-----------|-------------|-------|
| T.4.1.1 | SALE | SaleTransaction | Primary revenue event |
| T.4.2.1 | RETURN | ReturnTransaction | Negative revenue; feeds C-007, C-001 |
| T.4.3.1 | VOID / POST_VOID | VoidTransaction | Feeds C-501, C-502 |
| T.4.4.1 | PAYMENT | PaymentRecord | Tender detail; feeds F.4 payment flow |
| T.4.5.1 | TAX | TaxRecord | Multi-authority tax line |
| T.4.6.1 | AUDIT | AuditLogEntry | Operator action log |
| T.4.7.1 | XFER routing | TransferDocument | Routed to D.3 transfer lifecycle via DOC_TYP=XFER |
| T.4.8.1 | Customer upsert | CustomerRecord | Merge on source_customer_id; feeds R module |
| T.4.9.1 | Publication via stream_publisher | XADD canary:events | All canonical events published via `get_stream_client().xadd()` with 9-field schema |

**Sub2 routing pattern:**
- LP-critical event types: full parse → CRDM write → publish to detection sub-stream
- Log-only event types: XACK without CRDM write (accepted but not analyzed)
- Unknown event types: publish to dead_letter; XACK

---

## T.5 — Merkle Anchoring (T.5.1–T.5.5)

**Source:** `tsp/merkle.py`, `tsp/consumers/sub3_merkle.py`  
**Patent:** Application #63/991,596, FIG. 1 Nodes 5/6

### T.5.1–T.5.2 — Batch Accumulation and Threshold

| L4 ID | Activity | Implementation Detail |
|-------|----------|-----------------------|
| T.5.1.1 | Accumulate event hashes | Sub3 reads event_hash from stream message; ZADD to Valkey sorted set `canary:batch:current` with ULID score |
| T.5.1.2 | Track message IDs without XACK | Accumulate pending Valkey message IDs; DO NOT XACK individual events during accumulation |
| T.5.2.1 | Count threshold check | count >= BATCH_COUNT_THRESHOLD (default 100) |
| T.5.2.2 | Time threshold check | time since first event in batch >= BATCH_TIME_THRESHOLD_SECONDS (default 600s / 10 min) |
| T.5.2.3 | Trigger on either threshold | Whichever fires first — count or time |

### T.5.3 — Merkle Tree Construction

**Source:** `tsp/merkle.py` → `build_tree(event_hashes: list[bytes]) → MerkleResult`

| L4 ID | Step | Implementation Detail |
|-------|------|-----------------------|
| T.5.3.1 | Sort hashes | Sort `event_hashes` by hex representation — `sorted(hashes, key=lambda h: h.hex())`. Deterministic ordering is required for proof verification. |
| T.5.3.2 | Double-hash leaves | Each leaf = `SHA-256(event_hash)` — second preimage resistance. This is different from internal nodes. |
| T.5.3.3 | Pad to power of 2 | If len(leaves) not a power of 2: duplicate last leaf until len = next power of 2 |
| T.5.3.4 | Build tree bottom-up | Level 0 = leaves. Each parent = `SHA-256(left_child + right_child)`. Continue until 1 node remains = root. |
| T.5.3.5 | Generate proof paths | For each leaf, generate MerkleProof: list of (sibling_hash, direction) tuples from leaf to root |
| T.5.3.6 | Return MerkleResult | NamedTuple: root_hash, tree_levels, proof_paths, leaf_count |

### T.5.4 — Inscription Pool Write

| L4 ID | Activity | Implementation Detail |
|-------|----------|-----------------------|
| T.5.4.1 | Transaction boundary | BEGIN TRANSACTION before any inscription writes |
| T.5.4.2 | INSERT inscription_pool | Tree root hash, batch metadata, merchant_id, batch_size |
| T.5.4.3 | INSERT event_inscriptions | One row per event in batch: event_id → inscription_pool_id (foreign key) |
| T.5.4.4 | COMMIT and XACK | Only after successful COMMIT: XACK all batch message IDs as a batch |
| T.5.4.5 | Clear accumulator | DELETE Valkey sorted set `canary:batch:current` after XACK |
| T.5.4.6 | Inscription dispatch | Sprint 6: MOCK_INSCRIPTION=true → mock OrdinalsBot response. Sprint 7+: live OrdinalsBot API. |

### T.5.5 — Audit Proof Verification

**Source:** `tsp/merkle.py` → `verify_proof(event_hash: bytes, proof: MerkleProof, expected_root: bytes) → bool`

| L4 ID | Activity | Implementation Detail |
|-------|----------|-----------------------|
| T.5.5.1 | Start from leaf hash | current = `SHA-256(event_hash)` (same double-hash as build_tree) |
| T.5.5.2 | Walk proof path | For each (sibling, direction) in proof: if direction=left: current = SHA-256(sibling + current); if direction=right: current = SHA-256(current + sibling) |
| T.5.5.3 | Compare to expected root | Return current == expected_root |
| T.5.5.4 | MCP tool surface | `verify_proof` exposed as investigator MCP tool — takes event_id, returns {valid: bool, root_hash, proof_path} |

---

## T.7 — Substrate Contracts (T.7.1–T.7.12)

**Source:** `tsp/tools.py`  
**Purpose:** MCP tool API surface that downstream modules (Q, R, D, F, W) call to interact with the TSP substrate.

These are the Go `cmd/tsp` MCP server tools. The full tool manifest must be read from `tsp/tools.py` directly. Key contracts:

| Contract | What It Guarantees to Downstream |
|----------|----------------------------------|
| Evidence record exists for every processed event | Sub1 XACK only after INSERT |
| Hash chain is unbroken | Advisory lock + PostgreSQL trigger |
| Merkle root exists for every batch | Sub3 INSERT before XACK |
| Canonical event types are stable | event_type vocabulary defined in stream publisher |
| Audit proof available for any event | verify_proof() reachable via MCP tool |

---

## Key Invariants Summary for Go Implementation

| # | Invariant | Source |
|---|-----------|--------|
| 1 | Hash verification BEFORE JSON parse (patent-critical) | sub1_seal.py `process_message()` Step 2→3 |
| 2 | BATCH_SIZE=1 for sub1 (chain integrity) | sub1_seal.py constant |
| 3 | chain_hash computed by PostgreSQL trigger, NOT app code | P0-3, B-001 |
| 4 | Advisory lock per merchant_id before chain operation | sub1_seal.py Steps 4-5 |
| 5 | EvidenceRecord is INSERT-only | No UPDATE path in codebase |
| 6 | Stream client on DB 4 (separate from cache DBs) | stream_publisher.py |
| 7 | Three consumer groups must be created BEFORE publisher starts | stream_publisher.py `init_consumer_groups()` |
| 8 | Sub3 does NOT XACK individual events during accumulation | sub3_merkle.py — holds pending IDs |
| 9 | Merkle leaves are double-hashed (second-preimage resistance) | merkle.py `build_tree()` |
| 10 | Pad to power of 2 by duplicating last leaf | merkle.py `build_tree()` |

---

*Pass: GRO-670 / GRO-675 | T Category A L4 spec complete | Patent invariants annotated | Category B T L3s (ingestion, parsing, backfill) pending Counterpoint API doc pass*

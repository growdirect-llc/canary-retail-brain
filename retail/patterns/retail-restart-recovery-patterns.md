---
tags: [retail, batch, resilience, operations, wiki]
project: retail
type: wiki
last-compiled: 2026-04-28
needs-review: 2026-05-12
---

# Retail Batch Restart and Recovery Patterns

Large-scale retail batch processing (sales audit, replenishment, forecasting) handles tens of millions of transactions per nightly run. A single failure without restart capability would require full reprocessing — unacceptable given 3–8 hour batch windows. This card documents the canonical restart/recovery architecture.

## Design Goals

| Goal | Mechanism |
|------|-----------|
| Resume from failure point | Commit bookmarks written before each commit |
| Prevent halts from large volume | Commit counters cap logical unit of work size |
| Parallel execution | Multi-threading by business dimension |
| No DBA required to restart | Restart logic in application layer |
| Execution audit | Batch statistics tracked per run in history tables |

## Logical Unit of Work (LUW) Pattern

The LUW is the fundamental unit of atomic batch processing:

```
LUW = (transaction key, commit counter threshold)

Example: SKU/store combination; commit every 10,000 combinations
```

**Processing flow:**
1. Process transactions
2. When commit counter reaches threshold: write restart bookmark to `restart_bookmark` table
3. Commit data changes
4. Continue processing

**On failure:** roll back to last commit point → retrieve bookmark → resume from bookmark position.

## Restart Table Schema

| Table | Purpose | Key Columns |
|-------|---------|------------|
| `restart_control` | Program configuration | program_name, num_threads, commit_max_ctr, process_flag, update_allowed |
| `restart_program_status` | Current execution state | restart_name, thread_val, program_status, restart_flag, current_pid, err_message |
| `restart_program_history` | Historical run log | restart_name, start_time, finish_time, commit_ctr |
| `restart_bookmark` | Resume position | restart_name, thread_val, bookmark_string, application_image |
| `restart_view` | Driver/thread assignment | driver_name, num_threads, driver_value, thread_val |

## Query-Based vs File-Based Restart

| Mode | Restart Data Stored | Resume Mechanism |
|------|--------------------|--------------------|
| Query-based | Last processed key value (e.g., last SKU/store) | WHERE clause on driving query excludes already-processed rows |
| File-based | Byte offset in input file at last commit | File seek to byte position; read from that offset |

**API functions:**
- Query-based: `restart_init()`, `restart_commit()`
- File-based: `restart_file_init()`, `restart_file_commit()`

### Query-Based Processing Flow (Priming Fetch Pattern)

```
1. restart_init()
2. Priming fetch (first row)
3. Loop:
   a. Process row
   b. Fetch next row
   c. If LUW key changed AND commit_ctr >= max:
      - Write restart_bookmark
      - Commit
      - Reset commit_ctr
4. Close logic
```

### File-Based Processing Flow

```
1. restart_file_init()
2. Open file; seek to bookmark byte offset
3. Outer loop (buffer batch of records):
   a. Inner loop (process individual records)
   b. End inner loop
   c. Commit
   d. restart_file_commit()
4. End outer loop
5. Close logic
```

## Multi-Threading

Threading divides the driving dataset into discrete segments processed by parallel instances:

| Dimension | Example Threading |
|-----------|------------------|
| Department | Thread 1: depts 1000–1999, Thread 2: depts 2000–2999 |
| Store | Thread 1: stores 1–500, Thread 2: stores 501–1000 |
| File | One file per thread; file-based processing never shares files |

Threading is controlled by `restart_control.num_threads`. A stored procedure partitions the driving cursor into segments by thread value. Each thread writes its own bookmark independently — restarts replay only the failed thread's segment, not the full job.

## Array Processing

All batch programs use array bind variables rather than scalar SQL:

- SELECT, INSERT, UPDATE, DELETE all use array bind variables
- Array size = `restart_control.commit_max_ctr` (or a multiple)
- Reduces server/client round trips and network traffic at high volumes
- Most impactful above 1M rows per batch program

**Tuning the commit counter:**
- Too low → excessive bookmark I/O; slower overall throughput
- Too high → longer rollback on failure + more memory pressure
- Typical range: 1,000–50,000 rows depending on row width

## Operational Scenarios

| Scenario | Behavior |
|----------|---------|
| Network blip during batch | Rolls back to last commit point; restart picks up at bookmark |
| DB server crash | Rolls back to last commit; restart from bookmark after DB recovery |
| Partial file delivery | File-based restart resumes at last committed byte offset |
| Hung thread | Other threads continue; hung thread can be killed and restarted independently |
| Failed replenishment run | Restart only reprocesses uncommitted SKU/location combinations |

## Related Cards

- [[retail-transaction-volume-benchmarks]] — volume levels this architecture must sustain
- [[retail-sizing-methodology]] — commit_max_ctr settings affect sizing
- [[retail-architecture-patterns]] — server topology supporting parallel threads

---
card-type: platform-thesis
card-id: platform-field-capture
card-version: 2
domain: platform
layer: cross-cutting
status: approved
agent: ALX
tags: [field-capture, mobile, MCP, fox-case, evidence-chain, hash, pgvector, event-templates, LP, receiving, voice, photo, RaaS, case-management]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

The field capture layer of the evidence chain: the pipeline by which a field operative — LP investigator, store manager, receiving clerk, merchant — captures an event on their phone in free text or voice, has it structured by a process-aware agent into a canonical event schema, and writes it directly to the hash chain. The timestamp, the photo payload, and the receiver attribution are all locked at the moment of capture — not when the operative gets back to the office.

## The governing principle: the agent at the process node

The field capture agent is not a passive structuring tool waiting to be told what happened. It is present at the process node with full context of expected state. It already has the PO open. It already knows what the ASN said. It already knows the vendor, the item, the expected quantity, the dock door, the arrival window.

When the receiving clerk says "47 out of 50" — that is a complete event. The agent does not need anything else. It knows the 3-unit short is on this specific line item, from this vendor, against this PO, and whether the variance exceeds the chargeback tolerance threshold. It writes a fully structured, hash-verified receiving discrepancy event with every required field populated — because it was already following the process, not waiting to be told about it.

The operative's input is always a delta from the agent's known expected state. That is why it can be so minimal. The agent handles the rest because it already knows what expected state is. This is the difference between an AI that transcribes field notes and an AI that participates in the process. The field operative is not dictating a report — they are confirming or deviating from a process the agent is already running.

This principle generalizes to every process node. At the POS: the agent knows the authorized items, the planogram, the expected basket. At the return desk: the agent has the receipt hash and the return policy already loaded. In the aisle during a cycle count: the agent knows what the planogram says should be there. In every case, the operative's input is the minimum possible signal — the deviation from expected state — and the agent constructs the complete, structured, hash-ready event from that signal plus the context it already holds.

## Purpose

The hash chain without field capture is only as good as what gets typed into a desktop system hours after the event occurred. That gap is where evidence integrity fails in practice: the LP observation happens in the aisle, the case note gets written from memory at end of shift, the timestamp on the note doesn't match the CCTV timestamp. Contested. Inadmissible. Lost.

The harder problem — the one that all prior case management systems failed to solve — is the tradeoff between ease of capture and consistency. Give the operative a form and you get consistent structure but low compliance. Give them a free text field and you get compliance but no consistency: "short shpmt 3 crtns" and "vendor only brought 47 of 50 units" are the same event, completely unsearchable against each other, unstructured for any downstream process.

The process-aware agent eliminates this tradeoff. The operative gets genuinely free input — text, voice, whatever comes naturally in the moment. The agent structures it against the canonical event template using the context it already holds from following the process. The chain receives a precisely formatted, consistently structured event. pgvector indexes the structured output for semantic search. Every future query — "all receiving discrepancies at store 042 in the last 90 days involving this vendor" — works because the structuring happened at write time, not at search time, and it was performed against a canonical schema every time.

## The field capture pipeline

**Step 1 — Capture.** Field operative opens their phone. Takes a photo if relevant. Dictates an observation — thirty seconds of natural language describing what they see, where they are, what event type it is. Tells the agent via MCP: "Fox case observation, store 042, receiving dock, vendor delivery discrepancy, three cartons short on PO 88421."

**Step 2 — Event type matching.** The agent receives the input and runs semantic search against the event type template library in pgvector. The templates are wiki cards — canonical schemas for every event type the platform recognizes: Fox case observation, receiving discrepancy, LP hold placement, inventory adjustment, store operations block, planogram reset deviation, age verification failure, NICS delay hold, return fraud attempt, and so on. The agent identifies the matching template and maps the dictated input to the required and optional fields of that schema.

**Step 3 — Structuring.** The agent structures the natural language input into the canonical event record. Required fields are populated from the dictation. Missing required fields trigger a follow-up prompt — "what is the PO number?" — before the record is finalized. The photo is attached as a payload hash. The operative's identity, their device, and the timestamp are captured automatically as receiver attribution fields. The agent presents the structured record for a one-tap confirmation before writing.

**Step 4 — Hash and chain entry.** The confirmed event record is canonicalized, hashed (SHA-256 of the canonical JSON including all payload hashes), sequenced within the merchant's event stream, and written to the chain. The hash includes the prior event's hash. The entry is permanent from this moment. The operative receives a receipt hash on their phone — confirmation that the event is in the chain.

**Step 5 — Case routing.** Depending on the event type and its configured routing rules, the chain entry triggers downstream actions: Fox case creation or update, LP alert to district manager, receiving discrepancy notification to vendor, inventory adjustment queued for audit review. Routing is configured per event type in the template card — the field operative does not decide what happens next, the template does.

## Event type templates

Every event type is a wiki card in the `Brain/wiki/cards/` directory, embedded in pgvector, and queryable by the agent at capture time. Each template card defines:

- **Required fields** — must be present before the event can be hashed and written
- **Optional fields** — captured if available, not blocking if absent
- **Receiver attribution requirements** — which receiver fields are mandatory for this event type (cashier ID, dock door, LP badge number, etc.)
- **Payload types** — what attachments are valid (photo, video, audio clip, document scan)
- **Routing rules** — what downstream actions the event triggers
- **Hash chain entry format** — the canonical JSON schema the agent uses to construct the hashable payload
- **Retention and portability** — how long the event is retained, what export format is supported for regulatory or legal purposes

The template library is the intelligence layer. The agent does not need to know how to structure a NICS delay hold — it reads the template. Adding a new event type is adding a new wiki card and seeding it into pgvector. No code change required.

## The infrastructure that already exists

The field capture pipeline is not a new system. It is a new interface to infrastructure already built:

- **pgvector memory bus** — already stores event type templates as embeddings; semantic search already finds the right template from natural language input
- **Hash chain (RaaS)** — already sequences and hashes events; the field capture event is a receipt-class event entering the same chain as every POS transaction and DC receipt
- **MCP surface** — already the interface contract; the phone is another MCP client, the field operative is another receiver
- **Receiver attribution** — already a first-class field on every chain entry; the operative's ID is the same attribution mechanism as the cashier ID on a POS transaction

What does not exist yet: the mobile capture UI and the field-to-chain pipeline that connects phone input to the MCP surface. That is the build. Everything else is already in place.

## Evidence integrity properties

A field capture event has the same evidence integrity guarantees as any other chain entry:

- **Timestamp** is the moment of capture — not the moment of desktop entry
- **Photo payload** is hashed into the event record — the image cannot be altered after capture without breaking the hash
- **Receiver attribution** identifies the specific person and device that captured the event — not "LP team" but "badge 4421, iPhone 15, store 042"
- **Sequence position** places the event in the ordered timeline of all events for this merchant — a Fox case observation captured at 14:23:07 is provably prior to the LP hold placement at 14:31:44
- **Chain integrity** means any party — district LP, insurer, legal counsel, regulatory auditor — can verify the complete event sequence without trusting the retailer's word

This is the evidentiary standard that makes LP cases defensible and insurance claims verifiable. The evidence exists in the chain before the subject of the investigation knows they are being investigated.

## Consumers

**Canary LP module** — Fox case events from field capture flow directly into the case management workflow; no manual data entry, no reconstruction from notes; the case timeline is the hash chain sequence

**Receiving module** — field capture of receiving discrepancies creates sequenced ASN variance events that trigger vendor chargebacks automatically if the discrepancy exceeds tolerance

**Operations Agent** — monitors field capture volume and latency by store and event type; low capture rate in a store with high shrink is itself a signal

**Legal and compliance** — export of the complete event sequence for a case in portable, independently verifiable format; the hash chain is the discovery document

**Insurer / lender** — third-party verification of event sequences without requiring access to internal systems; `verify_chain` is the audit tool

## Invariants

- A field capture event must be written to the chain before the operative leaves the location. A draft that sits on the phone and syncs later is not field capture — it is delayed desktop entry with a mobile interface. The chain entry must be immediate or the timestamp integrity guarantee is void.
- The photo payload must be hashed at capture, not at upload. The hash on the phone is the proof that the image was not altered between capture and chain entry.
- Receiver attribution must identify the individual, not the role. "Store manager" is not attribution. Badge number or authenticated user ID is attribution.
- Event type matching must use the canonical template. An agent that writes a free-form event to the chain without schema validation is creating an unstructured record that cannot be reliably queried, routed, or exported. Template conformance is mandatory before chain entry.

## Related

- [[raas-receipt-as-a-service]] — the hash chain infrastructure that field capture events enter
- [[retail-item-authorization]] — operational blocks placed by LP in the field are field capture events
- [[retail-receiving-disposition]] — receiving discrepancies captured in the field are field capture events
- [[retail-chargeback-matrix]] — vendor chargebacks triggered by field capture receiving events
- [[infra-blockchain-evidence-anchor]] — the L1/L2 anchoring layer that makes field capture events externally verifiable
- [[platform-proof-case]] — field capture is a key component of the evidence integrity proof

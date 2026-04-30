---
card-type: platform-thesis
card-id: platform-cryptographic-erasure
card-version: 1
domain: platform
layer: cross-cutting
status: approved
tags: [gdpr, ccpa, erasure, right-to-be-forgotten, encryption, append-only, raas, evidence-chain, key-destruction, dsar]
last-compiled: 2026-04-29
nav_order: 13

---

## What this is

The pattern that makes an append-only / immutable / hash-chained table compatible with the right-to-erasure obligations of GDPR Article 17 and equivalent laws (CCPA §1798.105, etc.). PII fields in append-only tables are stored as ciphertext encrypted with a per-subject AES-256-GCM key. The key lives in a separate, mutable lookup table. To erase a subject's data, the platform destroys their key. The ciphertext remains in the immutable table — but it is now unreadable forever. The chain integrity is intact; the personal data is gone.

## Purpose

The platform's evidentiary architecture rests on append-only tables — `evidence_records`, `raas_events`, `audit_log`, `transactions`. Append-only is the property that makes the chain trustworthy: no one can rewrite history, not the merchant, not Canary, not an attacker. The hash sequence enforces it.

GDPR Article 17 and equivalent laws require the platform to render an individual's personal data inaccessible on request. "We cannot delete the row, the table is append-only" is not a defense. The regulator does not care about the data structure — they care about the practical effect.

The cryptographic erasure pattern reconciles these. The row stays. The hash chain stays. The integrity proof stays. But the personal data inside the row is encrypted under a key that has been destroyed. Decrypting the field is now computationally infeasible. The personal data is, for every operational and regulatory purpose, gone.

This is not a workaround. It is the canonical answer for any system that combines integrity guarantees with privacy obligations. It is what every modern hash-chained system that processes PII must implement.

## The pattern

**Per-subject DEK.** Every data subject (customer, employee, vendor contact) gets their own data encryption key. The DEK is a 32-byte random AES-256-GCM key generated at first encounter and stored in a mutable lookup table — the canonical name in this platform is `raas_subject_keys`.

**PII fields encrypted with the subject's DEK.** Any append-only table that needs to write a PII field for that subject — name, email, phone, address — encrypts the field with the subject's DEK before the row is sealed. The append-only table contains only ciphertext.

**Read path: lookup, decrypt, return.** A normal query loads the ciphertext from the append-only table, looks up the subject's DEK from the mutable table, decrypts the field, returns the plaintext. The decryption is invisible to the caller; the API surface returns plaintext on every read.

**Erasure: destroy the DEK.** When a subject requests erasure, the platform deletes their row from the mutable DEK table. From that moment forward, every read against their ciphertext fails — there is no key. The append-only table is unchanged; the integrity chain is unchanged; but the PII is unrecoverable.

**Verification: post-erasure decrypt must fail.** The DSAR pipeline must verify that, after destruction, every ciphertext that referenced the destroyed key cannot be decrypted. A failed decrypt is the success signal. A successful decrypt is a control failure that must be investigated.

## What "subject" means

The DEK key is per-subject, not per-row. The subject is the person whose data is encrypted. The mapping from subject to DEK is one-to-one for the lifetime of that subject's data on the platform. A customer with 10,000 transactions has one DEK; all 10,000 transaction rows reference the same DEK. Erasing that one DEK renders all 10,000 rows' PII inaccessible at once.

The subject identity is platform-scoped, not merchant-scoped. The same person buying from two merchants on the platform is two distinct subjects from the platform's perspective — different DEKs, different erasure scopes, different audit trails. This is necessary because the legal relationship is between the merchant and their customer; Canary is the processor for each merchant separately.

## Where this pattern is canonical

| Append-only table | PII fields it carries | Erasure status |
|---|---|---|
| `sales.evidence_records` | Full webhook `raw_payload` (cardholder names, emails, addresses) | **Pattern not yet applied** — H.P0.6 in [data-classification-inventory.md](../../docs/sdds/go-handoff/data-classification-inventory.md) |
| `sales.transactions` | `customer_id` mapping; card-adjacent data | Pattern not yet applied |
| `sales.transaction_tenders`, `transaction_line_items` | Card data, customer info | Pattern not yet applied |
| `app.audit_log` | `actor_id`, `ip_address`, action details | Pattern not yet applied |
| `app.notification_log` | Recipient identifiers | Pattern not yet applied |
| `app.raas_events` | Per-event PII varies; some events embed customer attribution | **Pattern applied** — see `raas.md` L416–445 (the reference implementation) |
| `ecom.ecom_orders` | Customer name, email, shipping address | **Pattern applied** — see `ecom-channel.md` L596–621 |
| `app.context_json` (store-brain) | In-store session context | **Pattern applied** — see `store-brain.md` L302 |

The pattern exists in three SDDs. The work — Linear dispatch GRO-691 — is to extend it uniformly to the five tables where it is missing.

## Special case — `evidence_records`

`evidence_records` is the hardest case in the platform because the integrity chain depends on the row contents. The pattern still works — but with one caveat the architect must internalize.

The chain hash is over `event_hash`, which is `SHA-256(raw_payload_bytes)` computed before any parsing. If the platform encrypts `raw_payload` with the subject DEK before storage, the `event_hash` must still be computed over the **original wire bytes**, not the ciphertext. Otherwise erasure would invalidate the hash chain — every prior event would still verify, but the erased event would not, and the chain would be broken.

The correct sequence:

1. Receive raw payload bytes.
2. Compute `event_hash = SHA-256(raw_payload_bytes)`.
3. Compute `chain_hash` from prior event's chain hash + this event hash.
4. Encrypt the raw payload with the subject DEK.
5. Write the row: `{event_hash, chain_hash, ciphertext_payload, subject_id}`.

After erasure of the subject DEK:

- `event_hash` and `chain_hash` are unchanged. Chain verification still passes.
- `ciphertext_payload` is unreadable. The PII is gone.
- The platform can prove the event happened (chain verifies) without revealing what was in the event (no key).

This is the property that makes the hash chain compatible with privacy law. The integrity proof is hash-only; the personal data is cryptographically separate.

## DSAR pipeline integration

The erasure path is one branch of the broader Data Subject Access Request (DSAR) pipeline. The pipeline must:

1. **Verify the requester** — confirm the request is from the subject or their authorized representative. Verification is proportionate to the data sensitivity.
2. **Identify the subject's data** — the platform maintains a subject-to-DEK mapping; that table is the index of all data subject to erasure.
3. **Apply exemptions** — some data must be retained despite an erasure request: legal holds, regulatory retention windows (SOX 7y, financial 6y), legal-claims defense. Document the exemption basis.
4. **Destroy the unexempted DEKs** — delete the DEK rows. Log the destruction in `app.audit_log` (which is itself encrypted under a separate platform-administrative DEK that is not subject-scoped).
5. **Verify destruction** — re-read a sample of rows for the subject; decryption must fail.
6. **Notify the subject** — confirmation of completion within the regulatory deadline (GDPR: 30 days, +60 with notice; CCPA: 45 days, +45 with notice).

## Why not just delete the row?

Three reasons.

**Integrity.** The hash chain enforces append-only by design. Deleting a row breaks the chain — every subsequent event's `chain_hash` becomes unverifiable. The chain is the platform's evidentiary backbone; breaking it for one erasure request invalidates every claim against it.

**Audit.** Append-only is also a regulatory expectation in some contexts. SOX requires evidence of financial event sequencing. PCI requires audit trails of access. Deleting "for one customer" is a control failure even if the customer requested it.

**Practical scale.** A customer with 10,000 transactions across five tables is a hard delete operation that touches 10,000+ rows, has cascading foreign-key implications, and is non-atomic. A single DEK destruction is one row, atomic, instantly verifiable.

Cryptographic erasure makes the chain integrity property and the privacy obligation co-exist instead of conflict.

## Invariants

- Personal data in append-only tables is stored as ciphertext only. Plaintext PII in an append-only column is a design failure that breaks the erasure path before it begins.
- The DEK is per-subject, not per-row, not per-merchant. A new DEK per row defeats the bulk-erasure property; a per-merchant DEK over-broadens erasure beyond the requesting subject.
- DEKs are stored in a separate, mutable table — never co-located with the ciphertext. If the DEK rides with the ciphertext in the same row, deletion is structurally impossible.
- Hash chain values are computed over plaintext bytes (or hash values of plaintext), never over ciphertext. Encryption happens after the hash, not before.
- Post-erasure verification is a required step. A destruction that "should have" worked but is not verified is not a complete erasure.

## Sources

- `docs/sdds/go-handoff/raas.md` L416–445 — the reference implementation, the canonical pattern in this platform
- `docs/sdds/go-handoff/ecom-channel.md` L596–621 — applied to `ecom_orders`
- `docs/sdds/go-handoff/store-brain.md` L302 — applied to `context_json`
- `docs/sdds/go-handoff/data-classification-inventory.md` Section H.P0.6 — the gap analysis driving uniform extension; Linear GRO-691

## Related

- [[platform-pii-hashing]] — the keyed-hash standard for fields where the platform never needs the plaintext back; complements this pattern (encryption when round-trip is needed; hashing when not)
- [[raas-receipt-as-a-service]] — the chain backbone that this pattern protects
- [[infra-blockchain-evidence-anchor]] — the L1/L2 anchor where chain integrity is externally verifiable
- [[platform-data-classification]] — the four-tier scheme that drives which fields require this pattern

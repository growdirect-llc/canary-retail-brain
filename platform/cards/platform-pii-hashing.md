---
card-type: platform-thesis
card-id: platform-pii-hashing
card-version: 1
domain: platform
layer: cross-cutting
status: approved
agent: ALX
tags: [pii, security, hashing, hmac, keyed-hash, phone, email, low-entropy, gdpr, ccpa, glba]
last-compiled: 2026-04-29
needs-review: false
---

## What this is

The platform's standard for storing PII as a one-way hash when the field needs to be queryable for deduplication or cross-reference but the plaintext must never round-trip back. The construction is HMAC-SHA256 with a per-domain server-side secret key. Plain SHA-256 over PII is prohibited — its plaintext domain is small enough to enumerate, and any read access to the hash column trivially recovers the plaintext.

## Purpose

Some PII fields cannot be encrypted-and-decrypted because the platform genuinely never needs to recover the plaintext — only to test "is this the same person who showed up before?" Loyalty phone-number lookup is the canonical case. The naive answer is plain SHA-256, justified as "one-way." That justification is wrong when the plaintext space is small.

The North American Numbering Plan is roughly 10^10 candidates. The global mobile phone space is under 10^13. An attacker who reads a `phone_hash` column from a leaked backup, a compromised replica, a SQL-injection vector elsewhere, or as an insider with DBA access can precompute SHA-256 for the entire NANP space in well under an hour on a single commodity GPU and join the rainbow table back against every row. Email addresses are similar — the candidate space for any specific customer base is enumerable.

The keyed HMAC blocks the offline brute force. The same input with the same key always produces the same output, so deduplication and cross-reference still work. But an attacker without the key cannot precompute the rainbow table. The cost of compromise drops from "everyone's phone number" to "no recovery without compromising the secret separately."

## Construction

```
phone_hash = HMAC-SHA256(PHONE_HASH_KEY, normalize(phone))
```

```
customer_email_hash = HMAC-SHA256(EMAIL_HASH_KEY, normalize(email))
```

The Go primitive lives in `internal/security/pii_hash.go` as `HashPII(normalized string, key []byte) []byte`. The output is 32 bytes (BYTEA in Postgres, never TEXT). Storage as TEXT is a smell — it implies the hash is being treated as opaque text rather than as binary cryptographic output.

## Normalization rules

Normalization must run before HMAC, never after, and must be deterministic so the same person always produces the same hash. Domain-specific:

- **Phone.** Strip non-digit characters. Prepend `+` and country code if missing (default `+1` for US/CA per merchant settings). Reject inputs that do not parse to a valid E.164 number. `(415) 555-0100`, `415-555-0100`, and `+14155550100` collapse to one hash.
- **Email.** Lowercase, strip whitespace, no Punycode rewrites. `Customer@Example.com` and `customer@example.com` collapse to one hash. Plus-tag handling (`user+tag@example.com` vs `user@example.com`) is a deliberate choice — current default does NOT strip the `+tag` portion because it is a deliverable address; revisit if a merchant requests it.

## Per-domain keys

Each PII hash key is its own key class, loaded from Secrets Manager as its own environment variable, with its own rotation schedule. Reusing one key across domains creates two failure modes from one compromise.

| Key class | Domain | Source SDD |
|---|---|---|
| `PHONE_HASH_KEY` | Phone numbers (loyalty, customer contact) | `tsp-parse.md` loyalty parser → `loyalty_accounts.phone_hash` |
| `EMAIL_HASH_KEY` | Email addresses written to RaaS chain payloads for cross-channel correlation | `ecom-channel.md` → `customer_email_hash` |

Each key is exactly 32 bytes (256-bit). Same constraint as `CANARY_ENCRYPTION_KEY`. Generated with `openssl rand -hex 32`. Loaded by `runtime.InitSecurity()` at service startup; missing key fatals the service rather than degrading silently.

## Immutable chain context — key versioning

If the hash is written into an append-only or on-chain payload (e.g., the RaaS chain anchored to Bitcoin L2), key rotation cannot retroactively re-hash historical events. The chain is sealed.

The pattern: store the hash with a key version index. Chain payload carries `{key_version: N, hash: <bytes>}`. Verification at any point in time looks up the key version, retrieves the appropriate (still-retained) historical key, and recomputes. Old key versions are retired from new writes but never deleted. Rotation procedure must keep all prior versions available indefinitely for verification queries.

This is different from the encryption key rotation pattern, where ciphertext can be re-encrypted under a new key. Hash keys cannot be rotated forward without breaking historical hashes — they can only be added.

## When to use a hash, when to use encryption

The decision is whether the platform ever needs the plaintext back.

| Situation | Use |
|---|---|
| Need to query equality (dedup, cross-reference) and never need plaintext back | **Keyed hash** (this card) |
| Need to display the plaintext to an authorized user | **AES-256-GCM encryption** with `CANARY_ENCRYPTION_KEY` |
| Need both — display in normal flow, but support "right to be forgotten" deletion | **Per-subject AES-256-GCM** (see [[platform-cryptographic-erasure]]) |
| Plaintext is genuinely public and integrity is the only concern | **Plain SHA-256** is fine — content addressing of webhooks, Merkle leaf hashing, evidence chain hash |

The mistake to avoid: choosing plain SHA-256 because "it's a hash, hashes are one-way." The one-way property only holds when the input space is large enough to defeat brute force. For PII, the input space is too small.

## Invariants

- Plain SHA-256 is prohibited for any PII whose plaintext domain is enumerable (phone, email, ZIP code, partial address, license plate, etc.). If a new field needs hashing for lookup, it gets a new keyed-hash class — not a SHA-256 shortcut.
- Hash keys MUST NOT be reused for any other purpose. A key reused for both HMAC-PII and JWT-signing creates a cross-protocol attack surface.
- Normalization happens before HMAC, never after. The normalization function is part of the contract — changing it without a key rotation breaks dedup determinism.
- Keys are loaded from Secrets Manager via `runtime.InitSecurity()`. Keys in environment files are a one-commit exposure incident; treat the env-file path as transitional only.

## Sources

- `docs/sdds/go-handoff/go-security.md` → "PII Hashing Keys" subsection — the canonical Go-side definition
- `docs/sdds/go-handoff/tsp-parse.md` — `phone_hash` write site (loyalty parser)
- `docs/sdds/go-handoff/ecom-channel.md` — `customer_email_hash` write site (chain events)
- `docs/sdds/go-handoff/data-classification-inventory.md` Section A — the consolidated inventory of which fields use which protection

## Related

- [[platform-cryptographic-erasure]] — when the field needs to round-trip plaintext AND support GDPR erasure, the encryption-with-key-destruction pattern, not a hash
- [[raas-receipt-as-a-service]] — the chain anchor that consumes `customer_email_hash` events
- [[infra-blockchain-evidence-anchor]] — the on-chain context that drives the key-version requirement

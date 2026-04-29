---
card-type: platform-thesis
card-id: platform-data-classification
card-version: 1
domain: platform
layer: cross-cutting
status: approved
tags: [classification, pii, security, compliance, gdpr, ccpa, pci, glba, encryption, retention, audit]
last-compiled: 2026-04-29
---

## What this is

The four-tier data classification scheme used across the Canary platform. Every field that touches personal, financial, or operational data carries a classification. The classification drives encryption posture, audit logging, retention windows, and access control. The four tiers are restricted, sensitive, internal, and public.

## Purpose

A platform that handles transaction data, employee records, customer contact information, vendor financial data, and inventory across multiple POS sources cannot treat every field the same. PCI cardholder data demands different controls than a SKU. An employee's home address demands different protection than the count of items received at a dock door.

A consistent classification scheme is the substrate that makes everything else legible. When an SDD declares a field as "sensitive," that one word determines the encryption requirement (AES-256-GCM at rest), the access logging requirement (audit log on every read), the retention window default, the role required to read the field, and the regulatory regime that applies. Without a shared scheme, every SDD invents its own controls, drift accumulates, and the platform fails its first compliance review.

The scheme also drives the inventory artifact. `data-classification-inventory.md` is structured around these four tiers — Section A consolidates every field across the SDD library by classification, and Section B maps each classification to the regulations it triggers.

## The four tiers

| Tier | Definition | Treatment | Examples |
|---|---|---|---|
| **Restricted** | Highest sensitivity. Compromise produces direct regulatory and customer-impact harm. | AES-256-GCM at rest with `CANARY_ENCRYPTION_KEY`. Access logged on every read. Restricted to specific roles via JWT scope. Field-level audit when feasible. | Full webhook `raw_payload` (contains cardholder data); `parsed_payload`; `transaction.payload` forensic copy; recipient JSONB blobs that may contain customer PII |
| **Sensitive** | Personal or financial data covered by privacy or compliance regimes. Compromise produces customer harm and regulatory exposure. | AES-256-GCM at rest where round-trip is needed. HMAC-SHA256 keyed hash where lookup is needed but plaintext round-trip is not (see [[platform-pii-hashing]]). Tenant-scoped access. Audit on read for highest-sensitivity subset. | Customer name, email, phone, shipping address; employee name, email, phone; bank account holder name and routing number; card BIN, last4, expiry, fingerprint; IP addresses; loyalty `phone_hash`; chain `customer_email_hash` |
| **Internal** | Operational data not directly identifying an individual but specific to the merchant's operation. Compromise produces business-confidentiality harm rather than personal-privacy harm. | Tenant-scoped access via `WHERE merchant_id = $1`. No special encryption requirement beyond at-rest database encryption. No per-read audit log. | Merchant IDs, tenant partition keys; SKUs, item descriptions; on-hand quantities; transaction line items without customer attribution; webhook event IDs and types |
| **Public** | Data that is intentionally non-sensitive or already published. Hashes, public ledger entries, public-facing identifiers. | No restriction beyond integrity controls. Hashes verified on read; chain entries verified by Merkle proof. | `event_hash` (SHA-256 of webhook body); `chain_hash`; `merkle_root`; on-chain Bitcoin L2 inscriptions; published Merkle proofs |

The scheme is anchored in `docs/sdds/go-handoff/data-model.md` L55–61. Other SDDs reference and apply the scheme; they do not redefine the tiers. Cross-SDD drift on classification of a single field is itself a finding (see Section D of the inventory artifact).

## Treatment matrix

The classification determines the controls. The controls are not negotiated per-field — they follow from the classification.

| Control | Restricted | Sensitive | Internal | Public |
|---|---|---|---|---|
| Encryption at rest | AES-256-GCM (mandatory) | AES-256-GCM where round-trip needed; keyed-hash where not | DB-level only | None required |
| Access logging on read | Yes (every read) | Yes for high-sensitivity subset (financial, payment, employee surveillance) | No | No |
| Tenant scope (merchant_id WHERE clause) | Yes | Yes | Yes | Generally no — public data is not tenant-scoped |
| Role required (JWT) | Restricted role set (LP officer, admin, owner) | Tenant role set (cashier and above for read; admin for write) | Tenant role set | None — public endpoints |
| Default retention | Long (regulatory minimum where applicable) | Per regulation; default 12–24 months | Per business need | Forever (public, immutable) |
| Erasure path | Per-subject DEK destruction (see [[platform-cryptographic-erasure]]) | DEK destruction or hard delete | Hard delete | N/A — not applicable to public data |

The matrix is the contract. An SDD that declares a field "sensitive" and then specifies plaintext storage with no audit logging has either misclassified the field or violated the matrix. Both are findings.

## How a field gets a classification

The decision tree is mechanical:

1. **Does the field contain cardholder data, raw PII webhook payloads, or other regulated-sensitive content where a single record's compromise is materially harmful?** → Restricted.
2. **Does the field directly identify an individual or carry information protected by GDPR / CCPA / GLBA / PCI / state privacy laws?** → Sensitive.
3. **Is the field merchant-confidential operational data without direct individual identification?** → Internal.
4. **Is the field a hash, public ledger entry, or otherwise intentionally non-sensitive?** → Public.

When in doubt, classify higher. Reclassifying down is easy; reclassifying up after the field has shipped without controls is a remediation project.

## What the scheme is NOT

It is not a synonym for "regulated by GDPR." Restricted data is regulated; sensitive data is regulated; internal data may also have business-confidentiality obligations even though no privacy law applies. The classification names sensitivity, not regulatory regime. The regulatory regime is mapped separately in `data-classification-inventory.md` Section B.

It is not a substitute for a privacy notice or a DPA. The classification is the engineering control surface. The legal posture (what regulations apply, what notices are required, what contracts must say) is layered on top.

It is not a "permissions" scheme by itself. Roles and permissions reference the classification — a role grants access to a tier-and-domain combination — but the classification is the data property, not the role property.

## When a new field arrives

The procedure for any new field added to any SDD:

1. Determine classification using the decision tree above.
2. Specify treatment per the matrix — encryption, retention, audit, access role.
3. Add the field to the canonical SDD's data model.
4. If the field crosses an SDD boundary (e.g., it is read by another service), confirm both SDDs use the same classification. Drift = finding.
5. If the classification is restricted or sensitive, register the field in `data-classification-inventory.md` Section A before the SDD lands.

The procedure is mechanical. An SDD review that does not validate this procedure on every new sensitive field has not done a security review.

## Invariants

- Every field in every SDD that touches personal, financial, employee, payment, vendor, or merchant-confidential data carries an explicit classification. "Implicit" classification is a smell.
- The classification of a field is consistent across every SDD that references it. A field labeled "internal" in one SDD and "sensitive" in another is broken; the field is one of the two, not both.
- The treatment matrix is followed without exception. A "sensitive" field stored plaintext is a control failure regardless of how convenient the plaintext is.
- The classification is set when the field is introduced, not retrofitted later. Retrofitting is a remediation project (the platform currently has 14 P0 retrofits — see Section H of the inventory).

## Sources

- `docs/sdds/go-handoff/data-model.md` L55–61 — the canonical definition of the four tiers
- `docs/sdds/go-handoff/data-classification-inventory.md` — the consolidated inventory applying the scheme to every field across the SDD library
- `docs/sdds/go-handoff/go-security.md` — the encryption primitives and key management that implement the controls

## Related

- [[platform-pii-hashing]] — the keyed-hash standard for the lookup-only sensitive subset
- [[platform-cryptographic-erasure]] — the per-subject DEK pattern for restricted/sensitive fields in append-only tables
- [[raas-receipt-as-a-service]] — the chain backbone where classification drives what enters the chain in the clear
- [[infra-blockchain-evidence-anchor]] — the public ledger context for the public tier

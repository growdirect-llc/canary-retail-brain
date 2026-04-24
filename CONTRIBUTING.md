---
classification: confidential
owner: GrowDirect LLC
---

# Contributing

## Authoring rules

These rules are non-negotiable for every file in this vault.

1. **No client names.** Current or prior. No retailer, vendor, or
   partner named in a way that identifies a specific engagement.
2. **No former-company references.** No IBM, no prior-employer
   lineage, no prior-product names.
3. **All attribution to GrowDirect LLC.** The methodology, the
   frames, the templates — owned by GrowDirect.
4. **Published external standards are permitted.** ARTS, NRF, PCI,
   ISO, OWASP. Cite as "adoption of [standard]," not as "borrowed
   from [former engagement]."
5. **Derived methodology language is fine** — the frames may be
   informed by practice; the expression here is GrowDirect's.
6. **Every markdown file carries confidentiality frontmatter:**
   `classification: confidential` and `owner: GrowDirect LLC`.

## Branch naming

Working branches use one of: `feat/*`, `fix/*`, `chore/*`,
`docs/*`, `gro-NNN-*`. AI-agent-generated random names get
merged and deleted, or evaluated and deleted, within 7 days of
creation.

## Root-level files

No `.md` at vault root except: `README.md`, `NOTICE.md`,
`ACKNOWLEDGMENT.md`, `SECURITY.md`, `CONTRIBUTING.md`, `Home.md`,
`LICENSE` (if applicable). Everything else lives in a topic
directory.

## Cross-vault references

- Internal GrowDirect Brain references external vault articles
  where appropriate. External vaults (KATZ, Canary-Retail-Brain)
  NEVER reference internal GrowDirect Brain by path. If internal
  context is needed, abstract it first.
- Wikilinks within this vault are relative to the vault root.
- Cross-vault links use prose, not wikilinks (vaults open separately).

## Review before committing externally-visible content

Before merging any new file or significant edit to `main`, verify:

- [ ] No prior-client names
- [ ] No former-company references
- [ ] No internal infrastructure paths
- [ ] Confidentiality frontmatter present
- [ ] Attribution consistent with GrowDirect LLC

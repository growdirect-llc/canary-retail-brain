---
card-type: runbook
card-id: runbook-vault-publish
card-version: 1
domain: platform
layer: cross-cutting
status: approved
tags: [runbook, vault, publish, catz, crb, ncr, github-pages, jekyll, brain, content-push]
last-compiled: 2026-04-29
---

## What this is

The procedure for publishing curated Brain content from GrowDirect (the factory vault) to one or more of the three external companion vaults: CATz, CRB, and NCR. Each vault is a public GitHub repo rendered via GitHub Pages. GrowDirect is the only source of truth — vault content is never edited in the vault repo directly.

## When to run

Run this procedure when:
- A new Brain wiki card has been committed and is ready for external audience visibility
- A card has been materially updated and the vault copy is stale
- A new vault section (folder) is being initialized for the first time
- An investor, partner, or VAR audience is about to access the vault and content needs to be current

Do not run speculatively. Only publish content that has been reviewed, committed to GrowDirect, and is approved-status in its card frontmatter. Draft cards (`status: draft`) and `needs-review: true` cards do not get published.

## Vault directory

| Vault | Repo | Audience | Published URL | Content scope |
|---|---|---|---|---|
| CATz | `growdirect-llc/catz` | Investors / partners / clients | `https://catz.growdirect.io` | Method, strategy, platform thesis, proof case, ICP reference |
| CRB | `growdirect-llc/canary-retail-brain` | Investors / partners / clients | `https://crb.growdirect.io` | Product architecture, retail spine, module docs, RaaS/EDS |
| NCR | `growdirect-llc/ncr` | NCR Counterpoint VARs | `https://ncr.growdirect.io` | NCR Counterpoint-specific integration and co-sell content |

## Content scope per vault

**CATz** — the method and strategy surface. Publish to CATz:
- `Brain/wiki/cards/platform-thesis.md`
- `Brain/wiki/cards/platform-proof-case.md`
- `Brain/wiki/cards/icp-murdochs-reference.md`
- `Brain/wiki/cards/platform-enterprise-document-services.md`
- `Brain/wiki/cards/platform-pwc-benchmarks.md`
- `Brain/wiki/` method and strategy articles (anything a board-level reader should see)
- Do NOT publish: infra runbooks, agent profiles, internal org hierarchy cards, draft/needs-review cards

**CRB** — the product and retail brain surface. Publish to CRB:
- All `Brain/wiki/cards/retail-*.md` cards (approved only)
- `Brain/wiki/cards/raas-receipt-as-a-service.md`
- `Brain/wiki/cards/platform-enterprise-document-services.md`
- `Brain/wiki/cards/platform-performance-nfrs.md`
- `Brain/wiki/cards/retail-item-authorization.md`
- Module-level SDDs that are suitable for partner/prospect review
- Do NOT publish: internal runbooks, signal feed cards (competitive sensitivity), draft cards

**NCR** — the VAR co-sell surface. Publish to NCR:
- NCR Counterpoint-specific integration content from `Brain/`
- Co-sell toolkit content scoped to NCR VARs
- Do NOT publish: content about other POS vendors, internal competitive analysis, draft cards

When uncertain whether a card belongs in a vault, the default is: if it would embarrass the company if a competitor read it, keep it internal.

## Preconditions

1. `gh` CLI is authenticated: `gh auth status` returns active
2. The content to publish has been committed to GrowDirect on the current branch
3. All cards being published have `status: approved` and `needs-review: false` in frontmatter
4. No draft content, fabricated examples, or placeholder text is in the files being published
5. You have reviewed the diff — know exactly which files are changing and why

## Canonical steps

### Step 1 — Clone the target vault transiently

```bash
# Replace <vault> with: catz | canary-retail-brain | ncr
VAULT=catz
gh repo clone growdirect-llc/$VAULT /tmp/$VAULT-$$
```

The `$$` suffix makes the clone directory unique to this shell session. Never use a fixed path like `/tmp/catz` — that creates a persistent clone, which violates the no-local-copy rule.

### Step 2 — Copy curated content from GrowDirect

```bash
# Example: publishing a set of platform thesis cards to CATz
cp ~/GrowDirect/Brain/wiki/cards/platform-thesis.md /tmp/$VAULT-$$/method/
cp ~/GrowDirect/Brain/wiki/cards/platform-proof-case.md /tmp/$VAULT-$$/method/
cp ~/GrowDirect/Brain/wiki/cards/icp-murdochs-reference.md /tmp/$VAULT-$$/method/

# Adjust the destination folder to match the vault's existing structure.
# Check what folders exist in the vault before copying:
ls /tmp/$VAULT-$$/
```

### Step 3 — Strip internal frontmatter fields

Vault-published cards should not expose internal operational metadata. Before committing, strip or replace these fields from copied files:

```bash
# Fields to remove/replace in vault copies (sed or manual edit):
# agent: ALX          → remove
# needs-review: ...   → remove
# card-version: ...   → keep (useful for version tracking)
# last-compiled: ...  → keep
```

A future tooling pass will automate this. For now: review each copied file and remove fields that are agent-internal.

### Step 4 — Handle Obsidian wikilinks

Jekyll (which renders the GitHub Pages sites) does not natively render Obsidian-style `[[wikilinks]]`. Convert any wikilinks in copied files before committing to the vault:

```bash
# Run the wikilink conversion script (lives in each vault repo under _tooling/)
python3 /tmp/$VAULT-$$/_tooling/convert_wikilinks.py /tmp/$VAULT-$$/

# If the conversion script doesn't exist yet, convert manually:
# [[card-id]] → [card-id](card-id.md)
# [[path/card-id]] → [card-id](path/card-id.md)
# [[card-id|Display Text]] → [Display Text](card-id.md)
```

Spot-check at least 3 files after conversion to confirm no `[[` strings remain.

### Step 5 — Commit and push to the vault

```bash
git -C /tmp/$VAULT-$$ add -A
git -C /tmp/$VAULT-$$ status   # review what's changing before committing

git -C /tmp/$VAULT-$$ commit -m "content: publish <brief description of what changed>"
# Example: "content: add platform-thesis v2, proof-case, Murdoch's ICP reference"

git -C /tmp/$VAULT-$$ push
```

Commit message style: `content: <what>` for content pushes. `fix: <what>` for corrections. `structure: <what>` for folder/navigation changes.

### Step 6 — Verify GitHub Pages build

```bash
# Check the Pages build status via gh CLI
gh api repos/growdirect-llc/$VAULT/pages

# Or watch the Actions run:
gh run list --repo growdirect-llc/$VAULT --limit 3
```

Wait for the Pages build to complete (typically 1–3 minutes). Then spot-check the live published URL — verify at minimum: the home page loads, and at least one of the newly published pages renders correctly with no broken wikilinks.

### Step 7 — Clean up the transient clone

```bash
rm -rf /tmp/$VAULT-$$
```

Verify it's gone:
```bash
ls /tmp/$VAULT-$$ 2>&1   # should return: No such file or directory
```

## Verification

After the transient clone is deleted:

1. **Published site renders** — open the vault URL in a browser and confirm the updated content appears
2. **No wikilink rendering artifacts** — spot-check pages for raw `[[` strings that didn't convert
3. **No internal content exposed** — review published pages for agent-only fields, draft markers, or internal-only context that should not be public
4. **GrowDirect is still the source of truth** — run `git -C ~/GrowDirect status` and confirm no uncommitted changes were introduced by the publish process

## Failure modes

**`gh repo clone` fails — authentication error**
- Symptom: `error: authentication required` or 404
- Cause: `gh` auth token expired or missing write access to `growdirect-llc`
- Fix: `gh auth login` and re-authenticate; confirm you have push access to `growdirect-llc` org

**Pushed content but Pages site not updating**
- Symptom: push succeeded but live URL still shows old content after 5+ minutes
- Cause: GitHub Pages build failed silently, or CDN cache
- Fix: check Actions tab on the vault repo for a failed Pages build; check for Jekyll config errors introduced by the new content

**Wikilink conversion produced broken links**
- Symptom: internal navigation links on the published site return 404
- Cause: the conversion script produced paths that don't match the actual file structure in the vault
- Fix: check the rendered 404 URL — the path tells you which wikilink wasn't resolved correctly; manually correct in the vault repo via a new transient clone cycle

**Accidentally left persistent clone**
- Symptom: `/tmp/catz-<something>` directory still exists after the session
- Cause: cleanup step was skipped
- Fix: `rm -rf /tmp/catz-*` (and equivalent for other vaults); confirm with `ls /tmp/ | grep -E 'catz|canary-retail|ncr'`

**Draft content published accidentally**
- Symptom: a card with `status: draft` or `needs-review: true` is now live
- Fix: immediately clone the vault again, remove or replace the file with a placeholder, push, verify the live page is corrected, clean up

## Multi-vault publish

When publishing the same content to multiple vaults (e.g., `platform-enterprise-document-services.md` belongs in both CATz and CRB), run the procedure once per vault. Do not try to clone both simultaneously — finish one complete cycle (clone → copy → commit → push → verify → cleanup) before starting the next.

## Invariants

- GrowDirect is the only place where vault content is authored. Never edit a file inside a transient vault clone that you don't intend to immediately commit and push. Never edit the vault repo via the GitHub web editor.
- A card is not published until it is committed to GrowDirect first. The GrowDirect commit is the source record; the vault push is a projection.
- Draft cards never get published. `needs-review: true` cards never get published.
- The transient clone must be deleted before the session ends. No exceptions.
- Internal frontmatter fields (`agent:`, `needs-review:`) are stripped before publishing. The vault is a public surface.

## Related

- [[runbook-brain-wiki-commit]] — the commit procedure that must precede any vault publish
- [[runbook-memory-bus-seed]] — seed the memory bus after committing; separate from vault publish
- `Brain/dispatches/2026-04-26-three-vault-jekyll-pages-architecture.md` — the architecture decision behind this runbook
- `Brain/projects/CATz.md` — CATz project MOC with external repo link
- `Brain/projects/CanaryRetailBrain.md` — CRB project MOC with external repo link

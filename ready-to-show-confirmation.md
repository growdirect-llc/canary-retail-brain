---
classification: confidential
owner: GrowDirect LLC
date: 2026-04-24
type: dry-run-verification
scope: Canary-Retail-Brain
---

# Canary-Retail-Brain — Cold-Reader Verification

## Verdict

**PASS**

Vault is ready to show under NDA / acknowledgment. No blocking regressions.
Two minor observations recorded below (non-blocking).

## Per-Dimension Results

| Dimension | Status | Notes |
|---|---|---|
| Repo-root standards | PASS | README, NOTICE, ACKNOWLEDGMENT, SECURITY, CONTRIBUTING, Home all present and render cleanly. |
| Confidentiality markings | PASS (with note) | All platform/* + Home.md + SECURITY.md + CONTRIBUTING.md carry `classification: confidential` + `owner: GrowDirect LLC`. README.md lacks frontmatter (acceptable per task spec). NOTICE.md and ACKNOWLEDGMENT.md also lack frontmatter — conventional for legal documents; flagging as observation, not regression. |
| No prior-client names | PASS | Full-vault case-insensitive grep for Kroger / Walmart / Tesco / Meijer / Appriss / Sysrepublic / Retek / PwC / Harrods / Staples / Coles / Fireball / Clarks / Morrisons / Circuit City returned zero hits. |
| No former-company refs | PASS (with note) | Only "IBM" hit is in `CONTRIBUTING.md` line 14, as part of the rule text itself ("No IBM, no prior-employer lineage"). This is a meta-reference defining the rule, not a lineage reference. Zero hits for Appriss, Sysrepublic, BCS. |
| No personal names from prior engagements | PASS | Zero hits for Don Boyle, John Teller, Drew Riegler, Tanya Kovacik, Garry Birkhofer, AJ Crawford, Bob Walters. |
| Attribution consistency | PASS | All attribution is to "GrowDirect LLC" / "Canary Retail" across README, NOTICE, ACKNOWLEDGMENT, SECURITY, CONTRIBUTING, and the three platform articles. Single contact address (`contact@growdirect.io`, `security@growdirect.io`). No stray ownership references. |
| Platform frame is coherent | PASS | overview + spine-13-prefix + CRDM read as a unified architectural story. Differentiated-Five (T+R+N+A+Q) is defined once in overview, echoed consistently in the spine table, and reinforced in README and Home.md. The CRDM article explains why the same five-entity frame underlies every module. |
| ARTS adoption clear | PASS | CRDM article explicitly calls out POSLog → Events, Customer Model → People, Device Model → Things, Site Model → Places. Overview calls the adoption "runtime schema, not an integration veneer." CONTRIBUTING permits standards citations as "adoption of [standard]." No lineage/claim-beyond-adoption language found. |
| Internal coherence | PASS | All resolvable wikilinks inside the populated slice (overview ↔ spine ↔ crdm ↔ Home) work. Unresolved wikilinks (`arts-adoption`, `differentiated-five-add-on`, `modules/*`, `architecture/*`, `roadmap/*`) map to directories that exist but are intentionally unpopulated — declared as first-draft state in the task brief and the Home.md "(roadmap)" annotations. |
| Cold-reader narrative | PASS | See below. |

## Regressions

None.

## Positives worth noting

- **Tight legal perimeter.** NOTICE + ACKNOWLEDGMENT + README form a coherent access-control story: what the repo is, who may read it, and what they're agreeing to by reading it. The acknowledgment language is pragmatic (evaluation / collaboration scope, reasonable care standard, survival clause) rather than aggressive — appropriate for an NDA-gated partner review.
- **SECURITY.md scopes correctly.** It distinguishes documentation-vault confidentiality (access control) from product security (which is pointed at the Canary product repo) and from platform-level key management (pointed at GrowDirect platform repo). A technical reader will trust that the right controls live in the right places.
- **CONTRIBUTING.md is the rulebook.** Authoring rules are explicit, testable, and include a pre-merge checklist. This is exactly what a partner evaluating rigor wants to see.
- **The Differentiated-Five pitch lands in one sentence.** From overview.md: "You get the LP module everyone charges for, plus the customer / device / asset tier nobody charges for, because they're the same platform." That is a shippable elevator pitch.
- **CRDM cross-domain claim is credible.** The model is presented as genuinely platform-level (People × Places × Things × Events × Workflows) with the HOA/residential example used as evidence of generality. A partner will read this as "real architecture, not a single-product schema dressed up."
- **ARTS adoption framing is disciplined.** Presented as adoption of published standards, not as proprietary innovation over them. POSLog / Customer / Device / Site mapped directly to CRDM entities. This is the right posture — credible with retail-standards-aware readers, legally clean, no lineage exposure.
- **Roadmap is honest.** v1 ships the Differentiated-Five, v2 expands, v3 completes the spine. Reader knows what exists today, what is next, what is later. No over-claiming.

## Cold-reader narrative

After reading Home.md → overview.md, a partner under NDA will understand:

- **What it is.** A retail operating system for SMB specialty retailers (~3–300 stores) with an online footprint. POS-agnostic, ARTS-standards-native, multi-tenant SaaS. Sits above the POS, not instead of it.
- **Who it's for.** SMB specialty — multi-store apparel, F&B specialty, sporting goods, MLM/direct-selling with storefronts. Retailers who need more than a POS, less than an enterprise suite, and cannot absorb a 12-month Big-4 transformation.
- **What makes it different.** Six points, each crisp: ARTS-native, POS-agnostic by architecture, CRDM abstraction, multi-tenant from v1, agent-native, evidence-first.
- **What ships now.** The Differentiated-Five: Transaction Pipeline (T), Customer (R), Device (N), Asset Management (A), Loss Prevention (Q). Stated once, repeated consistently, reinforced in the spine table.
- **Where it's going.** v2 adds CRDM expansion (C/D/F/J). v3 completes the spine (S/P/L/W). Reader can see a three-release arc.

The overview sells; the spine proves the platform is exhaustively scoped; the CRDM proves the data model is general enough to back every module. Together the three articles establish that Canary Retail is a platform with architectural discipline, not a rebranded point tool.

## Minor observations (non-blocking)

1. **Legal-document frontmatter.** NOTICE.md and ACKNOWLEDGMENT.md lack the `classification: confidential` / `owner: GrowDirect LLC` frontmatter. Task spec accepted README.md as exception; applying the same courtesy to NOTICE and ACKNOWLEDGMENT is reasonable (they are themselves the confidentiality notices). If strict compliance with CONTRIBUTING rule 6 is preferred, add the frontmatter block to both.
2. **Cross-vault wikilink.** `platform/spine-13-prefix.md` line 78 uses a wikilink to `../../CATz/cbm-v2/agent-strategy`. CONTRIBUTING rule "Cross-vault references" specifies cross-vault links should use prose, not wikilinks (vaults open separately). Swap to prose ("see the CATz CBM v2 Agent Strategy article") if strict compliance is desired.

Neither observation blocks showing the vault. Both are 30-second fixes if you want a clean bill.

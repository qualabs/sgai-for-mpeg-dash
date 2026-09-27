# What is published here, and where it came from

| | |
|---|---|
| **Candidate promoted** | `v12.6` |
| **Promoted on** | 2026-09-27 |
| **Promoted by** | the coordinator, applying the criterion in `CLAUDE.md` |
| **Previously published** | `v7.2`, promoted manually on 2026-09-17 with no criterion |

The files in this directory are `output/v12.6-sgai-spec.md` and its
sidecars `output-analysis/v12.6-{spec-validation,detail-review,dash-conformance-audit,comparison}.md`,
renamed without the version prefix. `inputs.sha256` records the inputs
(`context/`, `context-analysis/`, `prompts/`) the candidate was built from;
`bin/check-dist-freshness.py` compares against it.

**Why it was promoted.** Both halves of the criterion held:
`bin/check-promotable.py` exited `0` on the v12.6 sidecars
(`PROMOTABLE=si BLOCKERS=0 NEEDS_HUMAN=0 PIPELINE=0 CONTEXT_CHANGE=0
UNCERTAIN=0`, 10 items open and not blocking, published in the
sidecars), and `comparison.md` gives `BETTER THAN PUBLISHED` against
`v7.2`.

**This record exists for two readers.**

A person asking "which build is this?" — the unversioned filenames are
deliberate, so the answer is not in the name, and git history alone does
not distinguish a promotion from an edit.

And the build orchestrator, which numbers the next candidate from
`output/`. `output/` was kept at this promotion, so the next major is
`v13`.

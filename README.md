# SGAI for MPEG-DASH

This project designs and prototypes a complete **Server-Guided Ad
Insertion (SGAI)** specification for **MPEG-DASH**, covering **both linear and
non-linear ads**. The output is a full SGAI specification that extends
**MPEG-DASH 6th edition** — absorbing and clarifying the linear SGAI
primitives already in the spec (`InsertPresentation`,
`ReplacePresentation`, `ListMPD`) as the baseline, and introducing the
new constructs required for non-linear ads (overlays, side-by-side,
pause ads, L-shapes, banners, fullscreen interactive layers) that
coexist with the linear flow under the same architecture. The bulk of
the design work targets the non-linear delta; linear is preserved as
the established baseline and may receive minor clarifications or
extensions where the gap analysis surfaces them.

## Layout

```
projects/sgai-for-mpeg-dash/
├── README.md             this file — what / how to read / how to regenerate
├── CLAUDE.md             conventions for subagents touching this project
├── context/              inputs — technical specification of the target spec
├── prompts/              build scripts — .prompt files run by an LLM agent
├── context-analysis/     pre-spec artefacts — derived from context/ and consumed by the spec build
├── dist/                 the published spec and its analyses — what the project stands behind
├── output/               candidate specs, one per build iteration (vN-sgai-spec.md)
├── output-analysis/      per-candidate analyses of the spec (validation, detail-review, audit) + ad-hoc research / errata (vN- prefix)
├── .github-ai/           GitHub-feedback pipelines (Stages 5 & 6) — issues/ + prs/ prompts + output-issues/ + output-prs/ scratch (gitignored)
├── proposal-drafts/      historical drafts kept for reference
└── .project/             governance — PROJECT.md, LOG.md, phases/, decisions/
```

### `context/`
The canonical, self-contained statement of the proposal. Files are
numbered for reading order (`NN-name.md`); `99-glossary.md` is always
last. Authored by humans (Qualabs working group). Source of truth.

### `prompts/`
Verb-oriented build scripts grouped by pipeline stage. The
orchestrator (`build-all.prompt`) lives at the root of `prompts/`;
the other prompts live in stage subfolders: `1-pre-spec/`,
`2-build/`, `3-post-spec/`, `4-auto-refine/`. Each file declares
its **Inputs**, **Output**, and **Skip if** rule at the top, then
the body is the substantive prompt for the LLM agent that runs it.
The agent is expected to be invoked from the project root. See
`prompts/README.md` for the folder layout, the pipeline flow
diagram, and the "When to use which prompt" table.

### `context-analysis/`
**Pre-spec** generated artefacts: inputs that the spec build
consumes. Derived from `context/`. Each file standalone — no
numeric prefix, no required reading order. Currently includes the
DASH gap analysis, UC coverage matrix, error semantics matrix, and
conformance assertions.

### `dist/`
The published spec and its three analyses, under names that carry
no version: `sgai-spec.md`, `spec-validation.md`,
`detail-review.md`, `dash-conformance-audit.md`, `comparison.md`.
This is what the project stands behind, and the only place to look
for that. The filenames are stable because the link to the spec has
to survive the next build; the spec's own title has never carried a
version either.

A build never writes here. Files arrive by **promotion**: a
candidate in `output/` is judged good enough to become the
published one, and is moved. The criterion for that judgement is
**not defined yet** — promotion is a human act today.

### `output/`
Candidate specs, one file per build iteration:
`v<N>-sgai-spec.md`. A candidate is what a build produced, not what
the project publishes; the two coincide only for as long as the
last promotion holds. Every analysis of a candidate — validation sidecar,
detail-review log, DASH conformance audit, ad-hoc studies — lives
in `output-analysis/` instead. Files are **not** overwritten
between runs, so the candidate history is preserved. The iteration number
`N` is computed by the `build-all` orchestrator as
`max(existing v* in output/) + 1` (or `1` for the first build).

### `output-analysis/`
Every analysis of a specific candidate. Two flavours, same
folder:
- **Per-iteration analyses produced by `build-all`**:
  `v<N>-spec-validation.md` (Step 7 — sidecar validation),
  `v<N>-detail-review.md` (Step 7.5 — micro-consistency review
  log), `v<N>-dash-conformance-audit.md` (Step 8 — DASH 6th
  conformance audit). These share the spec's `v<N>` prefix so the
  build iteration is auditable as a set.
- **Ad-hoc analyses created by hand** when a specific output needs
  deeper investigation: research informing the next build, errata
  clarifying a prior audit, follow-up studies grounded against a
  particular `vN-sgai-spec.md`.

The split mirrors `context/` → `context-analysis/`: the spec is
the artefact, everything that validates / reviews / audits it is
analysis on top.

### `.project/`
Governance scaffolding from the `create-project` skill. Phases,
tasks, decisions (ADRs), chronological log. See
`.project/PROJECT.md` for current status.

## How to read

To read **the specification**, open `dist/sgai-spec.md` — that is
the published one. To read **what the project is proposing and
why**, start with `context/01-intro.md` and follow the document
index TOC. For project status and history, jump to
`.project/PROJECT.md`.

## How to regenerate artefacts

Each prompt declares Inputs / Output / Skip rule at the top.
Re-running a prompt regenerates its output when the skip rule says
the inputs are fresher than the existing output.

- **Gap analysis**: invoke
  `prompts/1-pre-spec/analyze-dash-gap.prompt`. Reads `context/`,
  writes `context-analysis/dash-gap-analysis.md` (overwrite).
- **Spec**: invoke `prompts/2-build/build-spec.prompt`. Reads
  `context/` + `context-analysis/`, writes
  `output/v<N>-sgai-spec.md` (no overwrite), where `N` is the
  iteration number resolved as
  `max(existing v*-sgai-spec.md) + 1`.
- **Full pipeline (orchestrator)**: invoke
  `prompts/build-all.prompt`. Chains every step (1-pre-spec,
  2-build, 3-post-spec, and the 4-auto-refine convergence loop),
  honouring each prompt's skip rule and logging a per-step
  `[BUILT|SKIPPED]` line. See `prompts/README.md` for the folder
  layout, the pipeline diagram, and the "When to use which prompt"
  table.

Skip rules are mtime-based: an output is considered fresh when its
mtime is newer than the newest mtime in its inputs. Touch a `context/`
file to force a rebuild of downstream artefacts.

### Minor refinement (v\<N.M+1\>)

When `context/` has NOT changed but the most recent analyses
(validation sidecar, detail-review log, DASH conformance audit)
surface issues that can be fixed without changing requirements,
use `prompts/4-auto-refine/refine-spec.prompt` to produce a delta-only refinement:

- **Input**: the latest `output/v<N.M>-sgai-spec.md` plus the
  three matching analysis sidecars in `output-analysis/`.
- **Output**: `output/v<N.M+1>-sgai-spec.md`. Sections without
  issues are carried over byte-identical; every applied edit is
  annotated with an inline HTML comment `<!-- refine: <issue-id> -->`
  so the refinement is auditable.
- **Constraint**: requirements stay fixed. Issues that require a
  new requirement or a new architectural decision are deferred to
  the next major build under a "Refinement gaps" section appended
  to the refined spec.

After a refine, re-running `validate-spec`,
`review-spec-details`, and `audit-dash-conformance` against the
new candidate produces its three sidecars. Then run
`prompts/4-auto-refine/compare-spec-versions.prompt` to emit
`output-analysis/v<N.M>-comparison.md`: a per-category issue-count
table comparing the candidate against **what is published in
`dist/`**, with a verdict line (`BETTER THAN PUBLISHED` / `NO
BETTER THAN PUBLISHED` / `WORSE THAN PUBLISHED`).

The baseline is the published build rather than the candidate
generated just before, because that is the question a promotion
needs answered: not "did this round move", but "is this better
than what we currently give as good". The verdict is an input to
the promotion decision and not the decision itself.

### Incremental (v\<N.M+1\>)

When `context/` changed by a bounded delta, `prompts/build-incremental.prompt`
applies it to the latest candidate instead of regenerating the spec:
only the affected sections change, and
`output-analysis/v<N.M+1>-context-delta.md` maps each change to where
it landed. Which of the three scales (major, incremental, minor) to
use is the operator's call — see `CLAUDE.md` for the decision rule.

## GitHub issues pipeline (Stage 5)

A separate pipeline triages and drafts responses to open GitHub
issues on the repo. It runs manually today (cron deferred):

```bash
# Dry-run (default) — drafts artefacts under .github-ai/output-issues/
# without posting anything to GitHub.
claude -p "$(cat .github-ai/prompts/issues/orchestrate-issues.prompt)"

# Live — posts comments and applies labels for trusted authors.
claude -p "$(cat .github-ai/prompts/issues/orchestrate-issues.prompt)" -- --live
```

The pipeline classifies each open issue (Flow A meta / Flow B
substantive feedback / Flow C generated-artefact pointer / SKIP),
detects severity and language, runs an impact analysis against
`context/` for Flow B (grounded against the base standard when the
keyword detector trips), and
drafts a flow-appropriate response. Issues from authors listed in
`TRUSTED_GH_USERS` (see `.env.agent.example`) get the full auto
cycle in live mode; outsiders' drafts are held with
`ai-needs-review` for manual sign-off. See `CLAUDE.md` →
"GitHub issues pipeline (Stage 5)" for the full contract and
decisions log.

## Status

See `.project/PROJECT.md` for the current phase, open threads, and
decisions log.

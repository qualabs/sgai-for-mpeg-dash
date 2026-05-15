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
├── README.md          this file — what / how to read / how to regenerate
├── CLAUDE.md          conventions for subagents touching this project
├── context/              inputs — technical specification of the target spec
├── prompts/           build scripts — .prompt files run by an LLM agent
├── context-analysis/  pre-spec artefacts — derived from context/ and consumed by the spec build
├── output/            spec only — the principal deliverable per build iteration (vN-sgai-spec.md)
├── output-analysis/   per-iteration analyses of the spec (validation, detail-review, audit) + ad-hoc research / errata (vN- prefix)
├── proposal-drafts/   historical drafts kept for reference
└── .project/          governance — PROJECT.md, LOG.md, phases/, decisions/
```

### `context/`
The canonical, self-contained statement of the proposal. Files are
numbered for reading order (`NN-name.md`); `99-glossary.md` is always
last. Authored by humans (Qualabs working group). Source of truth.

### `prompts/`
Verb-oriented build scripts (`analyze-dash-gap.prompt`,
`build-spec.prompt`, `build-all.prompt`). Each file declares its
**Inputs**, **Output**, and **Skip if** rule at the top, then the
body is the substantive prompt for the LLM agent that runs it. The
agent is expected to be invoked from the project root.

### `context-analysis/`
**Pre-spec** generated artefacts: inputs that the spec build
consumes. Derived from `context/`. Each file standalone — no
numeric prefix, no required reading order. Currently includes the
DASH gap analysis, UC coverage matrix, error semantics matrix, and
conformance assertions.

### `output/`
The spec itself, and only that. One file per iteration:
`v<N>-sgai-spec.md`. The spec is the principal deliverable each
build produces. Every analysis of the spec — validation sidecar,
detail-review log, DASH conformance audit, ad-hoc studies — lives
in `output-analysis/` instead. Files are **not** overwritten
between runs, so build history is preserved. The iteration number
`N` is computed by the `build-all` orchestrator as
`max(existing v* in output/) + 1` (or `1` for the first build).

### `output-analysis/`
Every analysis of a specific output iteration. Two flavours, same
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

Start with `context/01-intro.md` and follow the document index TOC.
For project status and history, jump to `.project/PROJECT.md`.

## How to regenerate artefacts

Each prompt declares Inputs / Output / Skip rule at the top.
Re-running a prompt regenerates its output when the skip rule says
the inputs are fresher than the existing output.

- **Gap analysis**: invoke `prompts/analyze-dash-gap.prompt`.
  Reads `context/`, writes `context-analysis/dash-gap-analysis.md`
  (overwrite).
- **Spec**: invoke `prompts/build-spec.prompt`. Reads `context/` +
  `context-analysis/`, writes `output/v<N>-sgai-spec.md` (no
  overwrite), where `N` is the iteration number resolved as
  `max(existing v*-sgai-spec.md) + 1`.
- **Both with skip-if-fresh logic**: invoke
  `prompts/build-all.prompt`. Orchestrator that chains the two,
  honouring each step's skip rule and logging a per-step
  `[BUILT|SKIPPED]` line.

Skip rules are mtime-based: an output is considered fresh when its
mtime is newer than the newest mtime in its inputs. Touch a `context/`
file to force a rebuild of downstream artefacts.

### Minor refinement (v\<N.M+1\>)

When `context/` has NOT changed but the most recent analyses
(validation sidecar, detail-review log, DASH conformance audit)
surface issues that can be fixed without changing requirements,
use `prompts/refine-spec.prompt` to produce a delta-only refinement:

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
new minor version checks whether the refinement converged. Major
vs minor is currently a manual call — see `CLAUDE.md` for the
decision rule.

## Status

See `.project/PROJECT.md` for the current phase, open threads, and
decisions log.

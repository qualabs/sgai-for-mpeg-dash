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
├── spec-source/          the source of the spec — prose, schema, examples, use-case vectors
├── dist/                 the published spec and its analyses — what the project stands behind
├── output/               candidate specs, one per build iteration (vN-sgai-spec.md), assembled from spec-source/
├── output-analysis/      per-candidate analyses and records (validation, detail-review, conformance tests, audit, patches) + ad-hoc research / errata (vN- prefix)
├── bin/                  the checks and tools the build runs — code, not prompts
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
numeric prefix, no required reading order. The build reads the
DASH gap analysis, the error semantics matrix and the IAB ad-template
catalogue; the UC coverage matrix and the conformance assertions are
kept as records and no longer regenerated.

### `spec-source/`
The source of the spec, and the only place it is edited.
`sgai-spec.src.md` is the prose, with directives that
`bin/assemble-spec.py` replaces by files (`{{example:…}}`, `{{xsd}}`,
`{{include:…}}`) or by the build iteration (`{{version}}`). `syntax/`
holds the extension schema and `syntax.yaml`, from which the §5 tables
in `syntax/tables/` are generated; `examples/` the examples as
fixtures, each with a declared class (`index.yaml`); `scenarios/` the
use cases as vectors. It is always the source of the newest candidate
in `output/`. Edits are patches applied by `bin/apply-spec-patch.py`.

### `dist/`
The published spec, its extension schema and its analyses, under names
that carry no version: `sgai-spec.md`, `sgai-extension.xsd`,
`spec-validation.md`, `detail-review.md`, `conformance-tests.md` and
`.json`, `dash-conformance-audit.md`, `comparison.md`, `trace.json`,
with `PROVENANCE.md` saying which candidate they came from.
This is what the project stands behind, and the only place to look
for that. The filenames are stable because the link to the spec has
to survive the next build; the spec's own title has never carried a
version either.

A build never writes here. Files arrive by **promotion**:
`bin/promote.py v<N>` runs every gate (among them, the conformance
tests exit `0` and the candidate beats what is published) and copies
the set only when all hold.

### `output/`
Candidate specs, one per build iteration: `v<N>-sgai-spec.md`,
assembled from `spec-source/`, with its extension schema `v<N>-sgai-extension.xsd`, extracted by code from
the spec's §5.10.1 block. A candidate is what a build produced, not what
the project publishes; the two coincide only for as long as the
last promotion holds. Every analysis of a candidate — validation sidecar,
detail-review log, DASH conformance audit, ad-hoc studies — lives
in `output-analysis/` instead. Files are **not** overwritten
between runs, so the candidate history is preserved.

### `output-analysis/`
Every analysis of a specific candidate. Two flavours, same
folder:
- **Per-candidate files written by the orchestrators**: the
  conformance tests (`v<N>-conformance-tests.md` and `.json`,
  verdicts computed by code), the validation (`v<N>-spec-validation.md`
  with its machine summary and its trace, `v<N>-trace.json`), the
  names review (`v<N>-detail-review.md`), the LLM's suspicions
  (`v<N>-dash-conformance-audit.md`, a complement and never evidence),
  the comparison against `dist/` (`v<N>-comparison.md`), and the
  records of how the candidate was made: its patches, the trace of a
  `context/` delta and the hashes of the source it was assembled from.
  The full list is under "Naming conventions" in `CLAUDE.md`. They
  share the spec's `v<N>` prefix so the build iteration is auditable as
  a set.
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

## How to test conformance

Whether the spec conforms to MPEG-DASH 6th edition, and to its own
requirements in `context/03`, is decided by code, not by an LLM:

    python3 bin/check-dash-conformance.py --source spec-source   # levels 1-2, as the build runs it
    python3 bin/check-dash-conformance.py dist/sgai-spec.md      # the same on an assembled document
    python3 bin/check-dash-conformance.py --demo                 # positives and broken-on-purpose cases

`--players` adds dash.js and Shaka playing every main MPD, and
`--dashif` the DASH-IF conformance tool as a second auditor. What each
needs installed is in `SETUP.md`. Every script in `bin/` says in its
`--help` what its green covers and what it does not.

## How to regenerate artefacts

The spec is not written from scratch: every build edits
`spec-source/` by patches and assembles the candidate from it. The two
orchestrators are the entry points (how to invoke them, and why the
environment variable they need is not optional, is in `CLAUDE.md` →
"How to invoke a build"):

- **`prompts/build-all.prompt`** — a major: the checks on `context/`,
  the pre-spec steps, the `context/` delta applied to the newest
  candidate with no cap on how much changes, the analyses, and the
  refinement loop.
- **`prompts/build-incremental.prompt`** — a bounded `context/` delta
  into the latest candidate: only the affected sections change, and
  `output-analysis/v<N.M+1>-context-delta.md` maps each change to where
  it landed. It stops with `MAJOR RECOMMENDED` when the delta is too
  large or needs structure the spec does not have.

Each prompt declares Inputs / Output / Skip rule at the top. The
pre-spec steps skip by the hashes of their inputs
(`bin/step-inputs.py`), never by date. Which of the three scales
(major, incremental, minor) to use is the operator's call — see
`CLAUDE.md` for the decision rule. `context/` must be committed before
either runs.

### Minor refinement (v\<N.M+1\>)

When `context/` has NOT changed but the latest analyses surface issues
that can be fixed without changing requirements, the refinement loop
(Step 9 of both orchestrators) runs
`prompts/4-auto-refine/refine-spec.prompt` round by round:

- Each round reads only the sections its issues point at and writes a
  **patch** (`output-analysis/v<N.M+1>-patch.json`), which
  `bin/apply-spec-patch.py` applies to `spec-source/` and records; the
  spec carries no annotations. What a minimal edit cannot resolve goes
  to `output-analysis/v<N.M+1>-refine-gaps.md`, and requirements stay
  fixed.
- The round is assembled and linted, then judged: conformance tests,
  the validation of the units whose sections changed, the names, and
  `bin/check-promotable.py` as the stop condition. The audit is not
  re-run inside the loop.
- `bin/compare-candidates.py` compares the candidate with **what is
  published in `dist/`**, unit by unit, and gives a verdict (`BETTER` /
  `NO BETTER` / `WORSE THAN PUBLISHED`). `WORSE` undoes the round
  (`bin/apply-spec-patch.py --reverse`).

The baseline is the published build rather than the candidate
generated just before, because that is the question a promotion
needs answered: not "did this round move", but "is this better
than what we currently give as good". The verdict decides whether to
keep refining; promotion is `bin/promote.py`.

### Measuring a run

`python3 bin/measure-run.py <session-id>` reports what each step of a
run cost in tokens, read from its Claude Code transcript. Run it right
after the run: transcripts are deleted after 30 days.

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

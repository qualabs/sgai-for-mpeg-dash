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
├── analysis/          pre-spec artefacts — inputs the spec build consumes
├── output/            spec + post-spec artefacts (validation sidecar, etc.), dated per build
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

### `analysis/`
**Pre-spec** generated artefacts: inputs that the spec build
consumes. Each file standalone — no numeric prefix, no required
reading order. Currently includes the DASH gap analysis, UC coverage
matrix, error semantics matrix, and conformance assertions.

### `output/`
The spec itself plus any **post-spec** derived artefacts (validation
sidecar, future test reports, future version diffs). Dated filenames
(e.g. `YYYY-MM-DD-sgai-spec.md`, `YYYY-MM-DD-spec-validation.md`)
preserve build history — files are **not** overwritten between
runs, and a spec and its sidecars share the same date stamp so the
set is auditable together.

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
  Reads `context/`, writes `analysis/dash-gap-analysis.md` (overwrite).
- **Spec**: invoke `prompts/build-spec.prompt`. Reads `context/` +
  `analysis/`, writes `output/<today>-sgai-spec.md` (no overwrite).
- **Both with skip-if-fresh logic**: invoke
  `prompts/build-all.prompt`. Orchestrator that chains the two,
  honouring each step's skip rule and logging a per-step
  `[BUILT|SKIPPED]` line.

Skip rules are mtime-based: an output is considered fresh when its
mtime is newer than the newest mtime in its inputs. Touch a `context/`
file to force a rebuild of downstream artefacts.

## Status

See `.project/PROJECT.md` for the current phase, open threads, and
decisions log.

# sgai-for-mpeg-dash — conventions for subagents

This project produces a complete SGAI specification for MPEG-DASH that covers
**both linear and non-linear ads**, extending MPEG-DASH 6th edition.
Linear SGAI exists in 6th edition (`InsertPresentation` /
`ReplacePresentation` / `ListMPD`) and is absorbed as the baseline; the
non-linear extension is the principal design delta.

This file documents conventions for subagents and for myself in
future sessions working on this project. For *what* the project is,
how to read it, and how to regenerate artefacts, see `README.md`.
For governance (phases, tasks, decisions), see `.project/PROJECT.md`.

This project lives as a **separate git repo** with its own
`.git/` and remote at `git@github.com:qualabs/sgai-for-mpeg-dash.git`.
It is **gitignored from the parent `cto-assistant` repo by design**
(separate repo lifecycle — see `.project/decisions/`). The repo
has active git history; commit + push is the standard workflow.

## Layout

```
projects/sgai-for-mpeg-dash/
├── README.md          user-facing — what / how to read / how to build
├── CLAUDE.md          this file — conventions for subagents
├── context/              inputs — canonical, human-authored spec
├── prompts/           build scripts — .prompt files for LLM agents
├── context-analysis/  pre-spec artefacts — derived from context/ and consumed by the spec build
├── output/            spec + per-iteration build artefacts (versioned per build, vN-)
├── output-analysis/   ad-hoc research / errata about a specific output iteration
├── proposal-drafts/   historical drafts kept for reference
└── .project/          governance from the create-project skill
```

What does NOT go where:

- `context/` — no generated artefacts, no analysis, no scratch. Only
  the human-authored canonical spec files. If you generated it from
  the spec, it does not live in `context/`. **`context/` MUST be
  self-contained**: files inside `context/` MUST NOT reference any
  artefact under `context-analysis/`, `output/` or `output-analysis/`,
  neither as a "see also" pointer nor as a source for substantive
  content. The dependency arrow is strictly
  `context/` → `context-analysis/` → `output/` → `output-analysis/`;
  pointers in the reverse direction invert the layering. When a
  `context/` document needs additional information to stand on its
  own (a concept, a baseline citation, a vocabulary anchor), that
  information either lives directly inside `context/` or cites the
  primary external source (an ISO spec, an IAB document, an RFC) —
  never our own downstream derivatives. The test: someone reading
  only `context/` MUST have everything they need to understand the
  spec we want to generate; if they would need to open something in
  `context-analysis/`, `output/` or `output-analysis/` to follow
  along, the missing piece belongs back inside `context/`.
- `prompts/` — only `.prompt` files. No build scripts in other
  languages, no helpers, no READMEs.
- `context-analysis/` — only **pre-spec** generated artefacts that
  the spec build consumes as inputs (gap analysis, UC coverage
  matrix, error semantics, conformance assertions). Derived from
  `context/`. No human-authored notes; those go to
  `.project/decisions/` or inside the spec. No post-spec
  artefacts — those go to `output/` or `output-analysis/`.
- `output/` — the per-iteration spec itself and any **post-spec**
  artefacts produced by `build-all` for the same iteration
  (validation sidecar, detail review, DASH conformance audit). All
  versioned per build with a `vN-` prefix so the iteration set is
  auditable together. No half-built artefacts from intermediate
  steps — those go to `context-analysis/`. No ad-hoc research or
  errata — those go to `output-analysis/`. Never edit by hand;
  if a build came out wrong, fix the context or the prompt and rebuild.
- `output-analysis/` — **post-spec** ad-hoc analyses that examine
  a specific output iteration: research informing the next build,
  errata clarifying a prior audit, conformance studies grounded
  against a particular `vN-sgai-spec.md`. Filename prefix is
  `vN-` where `N` is the iteration of the spec the analysis
  references. Not part of the build pipeline — created by hand
  when a specific output needs deeper investigation.
- `.project/decisions/` — ADRs and decision records. Architecture
  decisions live here, not in `context/`.

## Naming conventions

- **`context/` files**: numeric prefix `NN-name.md` defining reading
  order. `99-glossary.md` always last. Renumbering is allowed only
  when adding/removing a file changes the canonical sequence — when
  it happens, update the TOC in `01-intro.md` and every cross-ref.
- **`prompts/` files**: verb-oriented, kebab-case, `.prompt`
  suffix (`analyze-dash-gap.prompt`, `build-spec.prompt`,
  `build-all.prompt`). Each prompt opens with a header block
  declaring **Inputs / Output / Skip if** before the `---` divider.
- **`context-analysis/` files**: no numeric prefix. Each artefact
  standalone, named for what it analyses
  (`dash-gap-analysis.md`).
- **`output/` files**: version **prefix** `vN-`, where N is the
  iteration number of the build that produced the artefact. The
  filesystem sorts builds by iteration. Current patterns:
  `v<N>-sgai-spec.md` (the spec), `v<N>-spec-validation.md`
  (validation sidecar), `v<N>-detail-review.md` (detail review log
  from Step 7.5), `v<N>-dash-conformance-audit.md` (DASH 6th
  conformance audit). New post-spec artefacts follow
  `v<N>-<artefact>.md`. N is computed by the build-all orchestrator
  as `max(v* in output/) + 1`. Files are **not overwritten**; each
  build keeps history.
- **`output-analysis/` files**: prefix `vN-` matching the
  iteration of the spec the analysis is grounded against. Each
  file references the spec / audit / validation under its
  iteration directly. Not produced by `build-all`; created by
  hand when a specific output needs deeper investigation
  (ad-hoc research, errata, follow-up studies).
- **General**: kebab-case for filenames. English for all content
  inside `context/`, `prompts/`, `context-analysis/`, `output/`,
  `output-analysis/`, `README.md`, and this `CLAUDE.md` (matching
  the rest of the project content).

## How to add a new analysis

1. Create `prompts/<verb>-<noun>.prompt` with the standard header
   (Inputs / Output / Skip if) and substantive body.
2. Add a corresponding step to `prompts/build-all.prompt` so the
   orchestrator runs it with the same skip-if-fresh contract.
3. Decide where the output lives: pre-spec build input →
   `context-analysis/`, per-iteration build artefact → `output/`,
   ad-hoc post-spec study about a specific iteration →
   `output-analysis/`.

## How to modify the spec

Edit the file in `context/` directly. Downstream artefacts
(`context-analysis/`, `output/`) are now stale by mtime; re-run
`prompts/build-all.prompt` and the orchestrator regenerates only
the steps whose inputs moved.

When renumbering or renaming files in `context/`:

- Update the TOC in `context/01-intro.md`.
- Update every cross-ref in the other `context/*.md` files.
- Update refs from `context-analysis/*.md` (use
  `../context/<file>` paths).
- Update refs in `.project/` (`PROJECT.md`, `phases/`,
  `decisions/`). Be conservative with `LOG.md`: historical entries
  reference the old layout — preserve them verbatim; only update
  live navigational references.

## Cross-reference conventions

- Inside `context/`: relative refs without prefix
  (`[02-actors.md](02-actors.md)` or `./02-actors.md`).
- From `context-analysis/`, `output/` or `output-analysis/` to
  `context/`: parent-relative (`../context/02-actors.md`).
- From `.project/` to `context/`: parent-relative
  (`../context/02-actors.md`).
- From `prompts/` to inputs: parent-relative (`../context/`,
  `../context-analysis/`, `../output/`, `../output-analysis/`) —
  the prompt-runner is expected to execute from the project root,
  so paths inside the prompt body read naturally as
  `../context/...`.

## NotebookLM integration

When a prompt needs authoritative content from a published spec
(e.g. MPEG-DASH 6th edition), invoke the `notebooklm` skill against
the relevant notebook (currently:
"streaming formats / DASH 6th"). Cite section numbers when
available. Tag claims that could not be verified against the
authoritative source as `[inferred]`.

## ADRs and decisions

Architecture and process decisions live in `.project/decisions/`,
not in `context/`. When a decision affects the spec (e.g. choosing a
specific syntactic construct), the ADR is the record of *why*; the
spec carries the *what*.

## Tone for the spec and generated artefacts

Technical, direct, no fluff. Match the existing style of `context/`:
short paragraphs, explicit grounding (section references where
verifiable), tables only when comparing something. No marketing
language, no apologies, no filler.

For artefacts that quote or extend the MPEG-DASH 6th edition (the
spec, the gap analysis), use RFC 2119 vocabulary
(MUST / SHOULD / MAY) when stating requirements. Reference the RFC
explicitly at the top of any document that uses these terms.

## Tone for future subagents reading this file

Pragmatism > exhaustiveness. If a section here does not save the
next subagent time, cut it. If a new pattern emerges across 2-3
tasks, capture it.

# sgai-for-mpeg-dash — conventions for subagents

This project produces a complete SGAI norm for MPEG-DASH that covers
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
├── analysis/          pre-norm artefacts — inputs the norm build consumes
├── output/            norm + post-norm artefacts (validation sidecar, etc.), dated per build
├── proposal-drafts/   historical drafts kept for reference
└── .project/          governance from the create-project skill
```

What does NOT go where:

- `context/` — no generated artefacts, no analysis, no scratch. Only
  the human-authored canonical spec files. If you generated it from
  the spec, it does not live in `context/`.
- `prompts/` — only `.prompt` files. No build scripts in other
  languages, no helpers, no READMEs.
- `analysis/` — only **pre-norm** generated artefacts that the norm
  build consumes as inputs (gap analysis, UC coverage matrix, error
  semantics, conformance assertions). No human-authored notes; those
  go to `.project/decisions/` or inside the spec. No post-norm
  artefacts (validation sidecar, test reports, etc.) — those go to
  `output/`.
- `output/` — the dated norm itself and any **post-norm** derived
  artefacts that are built from the norm draft (validation sidecar,
  future test reports, future version diffs). All dated per build so
  the pair / set is auditable together. No half-built artefacts from
  intermediate steps — those go to `analysis/`. Never edit by hand;
  if a build came out wrong, fix the context or the prompt and rebuild.
- `.project/decisions/` — ADRs and decision records. Architecture
  decisions live here, not in `context/`.

## Naming conventions

- **`context/` files**: numeric prefix `NN-name.md` defining reading
  order. `99-glossary.md` always last. Renumbering is allowed only
  when adding/removing a file changes the canonical sequence — when
  it happens, update the TOC in `01-intro.md` and every cross-ref.
- **`prompts/` files**: verb-oriented, kebab-case, `.prompt`
  suffix (`analyze-dash-gap.prompt`, `build-norm.prompt`,
  `build-all.prompt`). Each prompt opens with a header block
  declaring **Inputs / Output / Skip if** before the `---` divider.
- **`analysis/` files**: no numeric prefix. Each artefact
  standalone, named for what it analyses (`dash-gap-analysis.md`).
- **`output/` files**: dated, ISO 8601. Current patterns:
  `sgai-norm-YYYY-MM-DD.md` (the norm) and
  `norm-validation-YYYY-MM-DD.md` (validation sidecar). New
  post-norm artefacts follow `<artefact>-YYYY-MM-DD.md`. Files are
  **not overwritten**; each build keeps history.
- **General**: kebab-case for filenames. English for all content
  inside `context/`, `prompts/`, `analysis/`, `output/`, `README.md`,
  and this `CLAUDE.md` (matching the rest of the project content).

## How to add a new analysis

1. Create `prompts/<verb>-<noun>.prompt` with the standard header
   (Inputs / Output / Skip if) and substantive body.
2. Add a corresponding step to `prompts/build-all.prompt` so the
   orchestrator runs it with the same skip-if-fresh contract.
3. Decide where the output lives: intermediate → `analysis/`,
   final deliverable → `output/`.

## How to modify the spec

Edit the file in `context/` directly. Downstream artefacts
(`analysis/`, `output/`) are now stale by mtime; re-run
`prompts/build-all.prompt` and the orchestrator regenerates only
the steps whose inputs moved.

When renumbering or renaming files in `context/`:

- Update the TOC in `context/01-intro.md`.
- Update every cross-ref in the other `context/*.md` files.
- Update refs from `analysis/*.md` (use `../context/<file>` paths).
- Update refs in `.project/` (`PROJECT.md`, `phases/`,
  `decisions/`). Be conservative with `LOG.md`: historical entries
  reference the old layout — preserve them verbatim; only update
  live navigational references.

## Cross-reference conventions

- Inside `context/`: relative refs without prefix
  (`[02-actors.md](02-actors.md)` or `./02-actors.md`).
- From `analysis/` or `output/` to `context/`: parent-relative
  (`../context/02-actors.md`).
- From `.project/` to `context/`: parent-relative
  (`../context/02-actors.md`).
- From `prompts/` to inputs: parent-relative (`../context/`,
  `../analysis/`, `../output/`) — the prompt-runner is expected to
  execute from the project root, so paths inside the prompt body
  read naturally as `../context/...`.

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
norm, the gap analysis), use RFC 2119 vocabulary
(MUST / SHOULD / MAY) when stating requirements. Reference the RFC
explicitly at the top of any document that uses these terms.

## Tone for future subagents reading this file

Pragmatism > exhaustiveness. If a section here does not save the
next subagent time, cut it. If a new pattern emerges across 2-3
tasks, capture it.

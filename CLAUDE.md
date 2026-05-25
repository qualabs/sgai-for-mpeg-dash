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
├── README.md             user-facing — what / how to read / how to build
├── CLAUDE.md             this file — conventions for subagents
├── context/              inputs — canonical, human-authored spec
├── prompts/              build scripts — .prompt files for LLM agents
├── context-analysis/     pre-spec artefacts — derived from context/ and consumed by the spec build
├── output/               spec only — the principal deliverable per build iteration (versioned, vN-sgai-spec.md)
├── output-analysis/      per-iteration analyses of the spec (validation, detail-review, audit) + ad-hoc research / errata
├── output-github-issues/ Stage 5 scratch (gitignored) — per-issue triage / impact / response drafts
├── proposal-drafts/      historical drafts kept for reference
└── .project/             governance from the create-project skill
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
- `output/` — the per-iteration spec itself, and only that. One
  file per iteration: `v<N>-sgai-spec.md`. The spec is the principal
  deliverable each build produces. Any post-spec artefact — the
  validation sidecar, the detail-review log, the DASH conformance
  audit — belongs to `output-analysis/`, not here. No half-built
  artefacts from intermediate steps — those go to `context-analysis/`.
  Never edit by hand; if a build came out wrong, fix the context
  or the prompt and rebuild.
- `output-analysis/` — every analysis of a specific output
  iteration. This includes both (a) the per-iteration analyses
  produced by `build-all` (validation sidecar, detail review,
  DASH conformance audit) and (b) ad-hoc analyses created by hand
  when a specific output needs deeper investigation (research
  informing the next build, errata clarifying a prior audit,
  follow-up conformance studies grounded against a particular
  `vN-sgai-spec.md`). Filename prefix is `vN-` where `N` is the
  iteration of the spec the analysis references. The split with
  `output/` mirrors `context/` → `context-analysis/`: the spec is
  the artefact; everything that validates / reviews / audits it is
  analysis on top.
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
  filesystem sorts builds by iteration. Only one canonical pattern:
  `v<N>-sgai-spec.md` (the spec). N is computed by the build-all
  orchestrator as `max(v* in output/) + 1`. Files are **not
  overwritten**; each build keeps history.
- **`output-analysis/` files**: prefix `vN-` matching the
  iteration of the spec the analysis is grounded against.
  Per-iteration analyses produced by `build-all`:
  `v<N>-spec-validation.md` (validation sidecar, Step 7),
  `v<N>-detail-review.md` (detail review log, Step 7.5),
  `v<N>-dash-conformance-audit.md` (DASH 6th conformance audit,
  Step 8). Ad-hoc analyses created by hand follow
  `v<N>-<name>.md` (e.g. `v3-non-video-carrier-research.md`,
  `v3-non-video-carrier-research-errata-1.md`).
- **General**: kebab-case for filenames. English for all content
  inside `context/`, `prompts/`, `context-analysis/`, `output/`,
  `output-analysis/`, `README.md`, and this `CLAUDE.md` (matching
  the rest of the project content).

## How to add a new analysis

1. Pick the pipeline stage and matching subfolder under `prompts/`:
   pre-spec generated input → `prompts/1-pre-spec/`, spec build
   itself → `prompts/2-build/`, per-iteration analysis of the spec
   → `prompts/3-post-spec/`, minor-refinement step
   → `prompts/4-auto-refine/`. The `build-all.prompt` orchestrator
   stays at the root of `prompts/`.
2. Create `prompts/<stage-folder>/<verb>-<noun>.prompt` with the
   standard header (Inputs / Output / Skip if) and substantive
   body.
3. Add a corresponding step to `prompts/build-all.prompt` so the
   orchestrator runs it with the same skip-if-fresh contract; the
   reference inside `build-all.prompt` uses the full path
   `prompts/<stage-folder>/<file>.prompt`.
4. Decide where the output lives: pre-spec build input →
   `context-analysis/`, the spec itself → `output/`, per-iteration
   analysis of the spec OR ad-hoc post-spec study about a specific
   iteration → `output-analysis/`.
5. Update `prompts/README.md`: the folder layout if a new
   subfolder appears, the "When to use which prompt" table, and
   the pipeline diagram if the new prompt changes the flow.

## How to modify the spec

Edit the file in `context/` directly. Downstream artefacts
(`context-analysis/`, `output/`, `output-analysis/`) are now stale
by mtime; re-run `prompts/build-all.prompt` and the orchestrator
regenerates only the steps whose inputs moved.

When renumbering or renaming files in `context/`:

- Update the TOC in `context/01-intro.md`.
- Update every cross-ref in the other `context/*.md` files.
- Update refs from `context-analysis/*.md` (use
  `../context/<file>` paths).
- Update refs in `.project/` (`PROJECT.md`, `phases/`,
  `decisions/`). Be conservative with `LOG.md`: historical entries
  reference the old layout — preserve them verbatim; only update
  live navigational references.

## Minor refinement (vN.M+1)

Two iteration scales coexist in this project:

- **Major (vN+1)** — `context/` changed: new / modified / dropped
  requirements, new constructs, or a new architectural decision.
  Re-run `prompts/build-all.prompt`; the orchestrator regenerates
  the spec and the analyses from scratch.
- **Minor (vN.M+1)** — `context/` unchanged. The latest analyses
  (`v<N.M>-spec-validation.md`, `v<N.M>-detail-review.md`,
  `v<N.M>-dash-conformance-audit.md`) surfaced issues that can be
  fixed without altering requirements. Use the minor-refinement
  path:

  ```bash
  claude -p "$(cat prompts/4-auto-refine/refine-spec.prompt)" \
    > /dev/shm/refine.out 2> /dev/shm/refine.err
  ```

  This produces `output/v<N.M+1>-sgai-spec.md` from
  `output/v<N.M>-sgai-spec.md` plus the three analysis sidecars
  matching `v<N.M>`. The refinement is delta-only: sections without
  issues are carried over byte-identical, and every applied edit is
  annotated with an inline HTML comment
  `<!-- refine: <issue-id> -->` for audit.

  After the refine, optionally re-run `validate-spec`,
  `review-spec-details`, and `audit-dash-conformance` against the
  new minor version to check whether the refinement converged
  (i.e., the new analyses surface fewer or no remaining issues).

  Then run `compare-spec-versions` to emit the convergence table:

  ```bash
  claude -p "$(cat prompts/4-auto-refine/compare-spec-versions.prompt)" \
    > /dev/shm/compare.out 2> /dev/shm/compare.err
  ```

  This produces `output-analysis/v<N.M+1>-comparison.md` with a
  per-category issue-count table (vN.M vs vN.M+1, Δ, Trend) and a
  verdict line (`ON TRACK` / `STALLED` / `REGRESSION`). Use it to
  decide whether to keep refining (`vN.M+2`) or escalate to a major
  build (`vN+1`).

**When to choose minor vs major**:

| Trigger                                                      | Path  |
|--------------------------------------------------------------|-------|
| Requirement added / changed / dropped                        | Major |
| New architectural decision (new construct, retired construct)| Major |
| Wording precision / cross-reference fixes                    | Minor |
| DASH conformance remedy for a Marginal or Non-conforming item| Minor |
| Renaming an attribute when an existing flagged issue says so | Minor |

Note: there is no orchestrator auto-detection yet — minor
refinement is dispatched manually. Future work: have `build-all`
auto-detect mtime conditions and choose major vs minor. For now,
the operator decides.

## GitHub issues pipeline (Stage 5)

A separate stage handles inbound GitHub issues on
`qualabs/sgai-for-mpeg-dash`. The build pipeline (Stages 1..4)
produces the spec; Stage 5 reacts to external feedback on it.

### Entry point

Manual invocation (D7 — cron deferred):

```bash
# Default — dry-run, never posts to GitHub.
claude -p "$(cat prompts/5-github-issues/orchestrate-issues.prompt)"

# Explicit live mode — drafts AND posts comments + applies labels.
claude -p "$(cat prompts/5-github-issues/orchestrate-issues.prompt)" -- --live
```

The six prompts live under `prompts/5-github-issues/`:

- `orchestrate-issues.prompt` — the Stage-5 orchestrator. Reads
  `.env.agent`, queries GitHub, drives the per-issue loop, emits
  the end-of-run summary block.
- `detect-issues.prompt` — lists open issues whose label set does
  not contain `ai-triaged`, `ai-responded`, `ai-skipped`,
  `ai-needs-review`, or `ai-conversation-cap-hit`.
- `triage-issue.prompt` — classifies each issue: `flow` (A / B /
  C / SKIP), `severity` (cosmetic / spec-detail / requirements /
  architectural), `lang` (ISO-639-1 with `en` fallback per D4),
  `trusted` boolean, and `cycle_count` (anti-loop, D5).
- `analyze-impact.prompt` — Flow B only. Validates the issue's
  claims against `context/`, identifies affected artefacts, picks
  a recommended action. Queries NotebookLM only if specific
  keywords appear in the issue body (D6): `DASH`, `ISO 23009`,
  `IAB`, `SCTE-35`, `SCTE`, `MPEG`, `CMAF`, `HLS`.
- `propose-response.prompt` — drafts a flow-appropriate reply in
  the detected language. Adds the auto-draft disclaimer at the
  top when `severity ∈ {requirements, architectural}` (D3).
  Every draft ends with the hidden marker
  `<!-- sgai-issues: ai-cycle -->` used by future runs to count
  cycles.
- `post-response.prompt` — only fires in `--live` mode for
  **trusted** authors. Posts the comment via `gh issue comment`
  and applies the labels `ai-responded`, `severity:<X>`,
  `flow:<A|B|C>`.

### Decisions encoded in the pipeline

| ID | Decision |
| --- | --- |
| D1 | Default mode is `--dry-run`. `--live` posts to GitHub. |
| D2 | Trusted authors (`TRUSTED_GH_USERS` in `.env.agent`) get the full auto cycle. Outsiders' drafts are held with `ai-needs-review` and surfaced to Nicolas via Telegram for manual decision. He may optionally promote them into `TRUSTED_GH_USERS` afterwards. |
| D3 | `severity:requirements` (and `severity:architectural` by extension) carry an explicit AI-disclaimer blockquote at the top of the response. |
| D4 | Language detection falls back to English when inconclusive. |
| D5 | Anti-loop cap of 3 AI cycles per issue. Enforced by `detect-issues`: when `cycle_count >= 4`, apply label `ai-conversation-cap-hit` and drop the issue before triage. |
| D6 | NotebookLM is queried only when the keyword detector trips. |
| D7 | Trigger is manual today. Cron is future work. |

### Scratch directory

Per-issue artefacts go to `output-github-issues/issue-<N>/` with a
**meta + per-cycle** layout:

```
output-github-issues/issue-<N>/
├── meta.md            ← regenerated every orchestrator run
├── cycle-1/
│   ├── triage.md      ← always written
│   ├── impact.md      ← only for Flow B issues
│   └── response.md    ← the drafted reply (payload posted by post-response)
├── cycle-2/           ← created when the OP has replied to the cycle-1 reply
│   └── ...
└── cycle-3/           ← capped at 3 by D5 (anti-loop)
```

- `meta.md` — a snapshot of the issue at the moment of this
  orchestrator run: title, URL, author + trust, created /
  updated / state, current labels, full original body
  (blockquoted verbatim), and a comments timeline table. It is
  **always overwritten** on every run — no history. The cycle
  subfolders point back to it as the up-to-date context anchor.
- `cycle-<C>/` — one subfolder per AI cycle. Cycle 1 is the first
  time the AI processes the issue. A new cycle is started when
  `detect-issues` observes that the OP has commented after the
  most recent AI response (each posted AI comment carries the
  marker `<!-- sgai-issues: ai-cycle -->` so the counter is
  unambiguous). Cycle 4+ is **blocked** by D5: `detect-issues`
  applies the `ai-conversation-cap-hit` label and the issue never
  reaches the per-issue loop.

The whole directory is **gitignored** (see project `.gitignore`).
Posted responses live on GitHub; the repo never commits them.
The `.gitkeep` is whitelisted so the empty directory survives
checkouts.

### Cycle counting (D5 enforcement)

`detect-issues.prompt` is the single source of truth for the cycle
index. For each open un-handled issue it runs:

```bash
gh issue view <N> --json comments \
  --jq '[.comments[] | select(.body | contains("<!-- sgai-issues: ai-cycle -->"))] | length'
```

Let `ai_marker_count` be the returned integer. Then
`cycle_count = ai_marker_count + 1`. If `cycle_count >= 4` the
issue hits the anti-loop cap (D5): `detect-issues` applies
`ai-conversation-cap-hit` (in `--live` mode) and excludes the
issue from the orchestrator's loop. Downstream prompts
(`triage-issue`, `analyze-impact`, `propose-response`,
`post-response`) simply echo the cycle index passed in by the
orchestrator and use it to:

- pick the output path (`cycle-<C>/...`),
- adjust tone when `cycle_count > 1` (the response acknowledges
  the prior AI cycle and addresses the OP's new feedback, without
  re-litigating already-validated claims).

### Reporting to Nicolas

The Stage-5 orchestrator never sends Telegram messages directly.
At the end of each run it emits a fenced summary block to stdout
between `=== SGAI-ISSUES RUN SUMMARY ===` and `=== END SUMMARY ===`.
The parent agent (whichever session invoked the orchestrator)
relays that block to Nicolas — with special attention to the
`needs-review` subsection (outsiders waiting on Nicolas's call).

### When NOT to invoke Stage 5

- During an active major build (`build-all`). The two
  orchestrators run independently and never share state, but it
  is clearer to run them sequentially.
- When `context/` is being edited interactively. The triage
  classification uses the current state of `context/`; running
  Stage 5 mid-edit produces classifications against a half-edited
  baseline.
- When the operator has not reviewed the prior run's
  `ai-needs-review` queue. Re-running before clearing the queue
  is fine — it just inflates the outsider backlog without
  Nicolas's attention.

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

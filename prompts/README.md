# `prompts/` — guide

This folder holds every `.prompt` file the build pipeline executes.
Prompts are grouped by their position in the pipeline. The
`build-all` orchestrator lives at the root and calls every other
prompt by relative path.

## Folder layout

```
prompts/
├── README.md                       this file
├── build-all.prompt                orchestrator (root) — Stages 1..4
├── 1-pre-spec/                     pre-spec generated inputs
│   ├── analyze-dash-gap.prompt
│   ├── build-uc-coverage-matrix.prompt
│   ├── build-error-semantics.prompt
│   ├── extract-conformance-assertions.prompt
│   └── analyze-iab-ad-templates.prompt
├── 2-build/                        the spec itself
│   └── build-spec.prompt
├── 3-post-spec/                    per-iteration analyses of the spec
│   ├── validate-spec.prompt
│   ├── review-spec-details.prompt
│   └── audit-dash-conformance.prompt
├── 4-auto-refine/                  minor-refinement convergence loop
│   ├── refine-spec.prompt
│   └── compare-spec-versions.prompt
└── 5-github-issues/                GitHub issues triage + auto-response pipeline
    ├── orchestrate-issues.prompt   stage-5 orchestrator (separate from build-all)
    ├── detect-issues.prompt
    ├── triage-issue.prompt
    ├── analyze-impact.prompt
    ├── propose-response.prompt
    └── post-response.prompt
```

Stage 5 is **not** chained into `build-all` — it has a separate
orchestrator (`5-github-issues/orchestrate-issues.prompt`) that
runs manually today (D7) and writes its scratch artefacts to
`output-github-issues/<issue-N>/` (gitignored). See the
"GitHub issues pipeline" section of `../CLAUDE.md` for the full
flow and the D-decisions that shape it.

## Pipeline flow

```
                      build-all (orchestrator)
                             │
                             ▼
   ┌──────────────────────────────────────────────────────────┐
   │                       1-pre-spec/                        │
   │  analyze-dash-gap → context-analysis/dash-gap-analysis  │
   │  build-uc-coverage-matrix → uc-coverage-matrix          │
   │  build-error-semantics → error-semantics                │
   │  extract-conformance-assertions → conformance-assertions │
   │  analyze-iab-ad-templates → iab-ad-templates            │
   └────────────────────────────┬─────────────────────────────┘
                                ▼
   ┌──────────────────────────────────────────────────────────┐
   │                        2-build/                          │
   │  build-spec → output/v<N>-sgai-spec.md                  │
   └────────────────────────────┬─────────────────────────────┘
                                ▼
   ┌──────────────────────────────────────────────────────────┐
   │                       3-post-spec/                       │
   │  validate-spec → v<N>-spec-validation.md                │
   │  review-spec-details → v<N>-detail-review.md            │
   │  audit-dash-conformance → v<N>-dash-conformance-audit.md │
   └────────────────────────────┬─────────────────────────────┘
                                ▼
   ┌──────────────────────────────────────────────────────────┐
   │                     4-auto-refine/                       │
   │  ┌── loop (gated by BUILD_ALL_AUTO_REFINE,              │
   │  │         capped at MAX_REFINEMENTS) ───────────────┐  │
   │  │  refine-spec → v<N>.<M+1>-sgai-spec.md           │  │
   │  │  (re-run 3-post-spec/* against the new minor)     │  │
   │  │  compare-spec-versions → v<N>.<M+1>-comparison.md │  │
   │  │  verdict: ON TRACK → continue                     │  │
   │  │           STALLED  → break (converged)            │  │
   │  │           REGRESSION → rollback, break            │  │
   │  └───────────────────────────────────────────────────┘  │
   └──────────────────────────────────────────────────────────┘
```

Stage 5 runs as a **separate orchestrator** (not chained into the
build-all flow above):

```
                 orchestrate-issues (manual; --dry-run | --live)
                                 │
                                 ▼
   ┌──────────────────────────────────────────────────────────┐
   │                    5-github-issues/                      │
   │  detect-issues  → list open issues w/o handling labels   │
   │  for each:                                               │
   │    triage-issue → output-github-issues/<N>/triage.md     │
   │    analyze-impact (Flow B only)                          │
   │                 → output-github-issues/<N>/impact.md     │
   │    propose-response                                      │
   │                 → output-github-issues/<N>/response.md   │
   │    post-response (only if trusted author + --live)       │
   │                 → comment + labels on GitHub             │
   │  summary block → stdout (parent agent relays to Telegram)│
   └──────────────────────────────────────────────────────────┘
```

`output-github-issues/` is gitignored — issue artefacts are
local-only scratch. The canonical record of posted responses
lives on GitHub itself.

## When to use which prompt

| Prompt                              | When to invoke                                                          | Lives in            |
|-------------------------------------|-------------------------------------------------------------------------|---------------------|
| `build-all`                         | Full major build from scratch (steps 1-8 + auto-refine loop step 9)     | root                |
| `analyze-dash-gap`                  | `context/` changed; pre-spec gap analysis is stale                      | `1-pre-spec/`       |
| `build-uc-coverage-matrix`          | `context/03-requirements.md` or `context/04-use-cases.md` changed       | `1-pre-spec/`       |
| `build-error-semantics`             | `context/03-requirements.md` or `context/05-dash-linear-interfaces.md` changed | `1-pre-spec/` |
| `extract-conformance-assertions`    | Any `context/` file changed (extractor reads the whole folder)          | `1-pre-spec/`       |
| `analyze-iab-ad-templates`          | Always (live external source; runs every build)                         | `1-pre-spec/`       |
| `build-spec`                        | Any of the inputs above changed; produces the next `v<N>-sgai-spec.md`  | `2-build/`          |
| `validate-spec`                     | New spec exists without matching `v<N>-spec-validation.md`              | `3-post-spec/`      |
| `review-spec-details`               | New spec / validation sidecar / naming-and-namespaces changed           | `3-post-spec/`      |
| `audit-dash-conformance`            | New spec exists without matching `v<N>-dash-conformance-audit.md`       | `3-post-spec/`      |
| `refine-spec`                       | Minor refinement on existing spec; called by Step 9 (or by hand)        | `4-auto-refine/`    |
| `compare-spec-versions`             | Compare two consecutive minor versions; emits the convergence verdict   | `4-auto-refine/`    |
| `orchestrate-issues`                | Process open GitHub issues end-to-end (triage → response). Dry-run default; `--live` to post | `5-github-issues/` |
| `detect-issues`                     | Fetch open issues missing any handling label; sub-step of orchestrator  | `5-github-issues/`  |
| `triage-issue`                      | Classify one issue: flow / severity / lang / trust / cycle count        | `5-github-issues/`  |
| `analyze-impact`                    | Flow B only: validate claims against `context/`, surface affected files | `5-github-issues/`  |
| `propose-response`                  | Draft a flow-appropriate reply in the detected language                 | `5-github-issues/`  |
| `post-response`                     | Live mode + trusted author: post comment + apply labels                 | `5-github-issues/`  |

Each prompt declares its full **Inputs / Output / Skip if** contract
in its own header — this table is a quick-pick index, not the spec.

## Minor vs major iteration

Two iteration scales coexist (see `../CLAUDE.md` for the full rule):

| Trigger                                                      | Path  |
|--------------------------------------------------------------|-------|
| Requirement added / changed / dropped                        | Major |
| New architectural decision (new construct, retired construct)| Major |
| Wording precision / cross-reference fixes                    | Minor |
| DASH conformance remedy for a Marginal or Non-conforming item| Minor |
| Renaming an attribute when a flagged issue says so           | Minor |

- **Major** runs the whole pipeline (`build-all`): regenerates
  `1-pre-spec/` outputs as needed, builds a fresh `v<N>-sgai-spec.md`,
  then re-runs the post-spec analyses against that new spec. After
  the major, Step 9 (auto-refine) attempts minor iterations
  automatically.
- **Minor** can be triggered standalone by running
  `prompts/4-auto-refine/refine-spec.prompt` and then re-running
  the three post-spec analyses against the new `v<N>.<M+1>` spec.
  The orchestrator's Step 9 automates this loop.

## Step 9 — auto-refinement loop

After Step 8 finishes the major build, `build-all` enters a
refinement loop (gated by env var `BUILD_ALL_AUTO_REFINE`, default
`true`; capped at `MAX_REFINEMENTS`, default `5`).

Per iteration `K`, the loop:

1. Calls `4-auto-refine/refine-spec.prompt` → produces
   `v<N>.<M+1>-sgai-spec.md` (delta-only edits, every change
   annotated with `<!-- refine: <issue-id> -->`).
2. Re-runs `3-post-spec/validate-spec.prompt`,
   `3-post-spec/review-spec-details.prompt`, and
   `3-post-spec/audit-dash-conformance.prompt` against the new
   minor version → three fresh sidecars.
3. Calls `4-auto-refine/compare-spec-versions.prompt` → emits
   `v<N>.<M+1>-comparison.md` with a verdict line.
4. Reads the verdict and decides:
   - **ON TRACK** (net issue count went down) → accept the new
     minor, set `M := M+1`, loop again.
   - **STALLED** (issue count unchanged) → converged; break loop.
   - **REGRESSION** (net issue count went up) → rollback (delete
     the five just-generated files), keep the previous head, break
     loop.
5. If `K == MAX_REFINEMENTS` without a natural break → cap
   reached, keep the last accepted minor, break loop.

On runtime errors (model failure, timeout, sidecar generation
exception) the loop breaks, keeping the last successful iteration.

### Configuration

| Env var                  | Default | Effect                                                          |
|--------------------------|---------|-----------------------------------------------------------------|
| `BUILD_ALL_AUTO_REFINE`  | `true`  | When `false`, Step 9 is skipped entirely.                       |
| `MAX_REFINEMENTS`        | `5`     | Hard cap on iterations of the loop.                             |

Both are read from `.env.agent`. See `../.env.agent.example` for
the canonical list of env vars.

### ON TRACK / REGRESSION criterion

The verdict is computed by
`4-auto-refine/compare-spec-versions.prompt`:

- **ON TRACK** — any net reduction in total issue count across the
  three categories (spec validation, detail review, DASH
  conformance), weighted equally. Cross-category trades are
  accepted as long as the net is negative.
- **REGRESSION** — strict. A net increase of `+1` or more triggers
  rollback. No tolerance for "fixed 5, broke 6".
- **STALLED** — net delta is zero.

## Prompt conventions

- Filenames: verb-oriented, kebab-case, `.prompt` suffix.
- Header: every prompt opens with **Inputs / Output / Skip if**
  before the `---` divider. The body is the substantive prompt.
- Paths inside a prompt body are **parent-relative**
  (`../context/`, `../output/`, etc.) — the prompt-runner runs from
  the project root, so paths read naturally as `../context/...`
  from a prompt's perspective.
- Cross-references between prompts use the full repo path from
  `prompts/` (e.g. `prompts/3-post-spec/validate-spec.prompt`).

## Adding a new prompt

1. Decide which folder it belongs to based on its position in the
   pipeline (pre-spec input, spec build, post-spec analysis, or
   refinement step).
2. Create `prompts/<folder>/<verb>-<noun>.prompt` with the
   standard header.
3. Add a step to `prompts/build-all.prompt` so the orchestrator
   runs it with the same skip-if-fresh contract.
4. Update the "When to use which prompt" table above.

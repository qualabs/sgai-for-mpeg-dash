# `prompts/` — guide

This folder holds every `.prompt` file the build pipeline executes.
Prompts are grouped by their position in the pipeline. The
`build-all` orchestrator lives at the root and calls every other
prompt by relative path.

## Folder layout

```
prompts/
├── README.md                       this file
├── build-all.prompt                orchestrator (root) — major: Stages 1..4
├── build-incremental.prompt        orchestrator (root) — incremental: a context/ delta into the latest candidate
├── 1-pre-spec/                     pre-spec generated inputs
│   ├── analyze-dash-gap.prompt
│   ├── build-error-semantics.prompt
│   └── analyze-iab-ad-templates.prompt
├── 2-build/                        the delta on spec-source/ (major and incremental)
│   └── apply-context-delta.prompt
├── 3-post-spec/                    per-iteration analyses of the spec
│   ├── validate-spec.prompt
│   ├── review-spec-details.prompt
│   └── audit-dash-conformance.prompt
└── 4-auto-refine/                  minor-refinement convergence loop
    └── refine-spec.prompt
```

What does not need judgement is code in `../bin/`, called from the
prompts: assembling the spec, generating the §5 tables, applying and
undoing patches, lint, conformance, the scenario vectors, the trace,
the comparison, the promotion. Retired prompts, with what replaced
them: `build-spec` (a major is `apply-context-delta` in major mode, ADR
0067), `compare-spec-versions` (`bin/compare-candidates.py`, ADR 0070),
`extract-conformance-assertions` and `build-uc-coverage-matrix` (nothing
read them; their `context-analysis/` files stay as records, ADR 0072).

Stages 5 (GitHub issues) and 6 (GitHub PRs) live **outside** this
folder, under `../.github-ai/`:

```
.github-ai/
├── issues/                         Stage 5 — GitHub issues triage + auto-response
│   ├── orchestrate-issues.prompt   stage-5 orchestrator (separate from build-all)
│   ├── detect-issues.prompt
│   ├── triage-issue.prompt
│   ├── analyze-impact.prompt
│   ├── propose-response.prompt
│   └── post-response.prompt
├── prs/                            Stage 6 — GitHub PRs review
│   ├── orchestrate-prs.prompt      stage-6 orchestrator (separate from build-all)
│   ├── detect-prs.prompt
│   ├── triage-pr.prompt
│   ├── analyze-pr.prompt
│   ├── propose-review.prompt
│   └── post-review.prompt
├── output-issues/                  Stage 5 scratch (gitignored)
└── output-prs/                     Stage 6 scratch (gitignored)
```

Stages 5 and 6 are **not** chained into `build-all` — each has a
separate orchestrator that runs manually today (D7) and writes its
scratch artefacts to its own gitignored folder
(`.github-ai/output-issues/` for Stage 5,
`.github-ai/output-prs/` for Stage 6). See the "GitHub issues pipeline"
and "GitHub PRs pipeline" sections of `../CLAUDE.md` for the full
flows and the D-decisions that shape each.

## Pipeline flow

```
               build-all (major) / build-incremental
                             │
                             ▼
   ┌──────────────────────────────────────────────────────────┐
   │  gates 0–0.7: bin/check-normative-base, check-context-*  │
   │                       1-pre-spec/                        │
   │  (skip by input hashes: bin/step-inputs.py)              │
   │  analyze-dash-gap → context-analysis/dash-gap-analysis  │
   │  build-error-semantics → error-semantics                │
   │  analyze-iab-ad-templates → iab-ad-templates (always)   │
   └────────────────────────────┬─────────────────────────────┘
                                ▼
   ┌──────────────────────────────────────────────────────────┐
   │                        2-build/                          │
   │  apply-context-delta (major: no cap; incremental: cap)  │
   │    artefacts first (fixtures, XSD, vectors), checked by │
   │    check-dash-conformance --source, check-scenarios;    │
   │    then prose by section patches (apply-spec-patch)     │
   │    → spec-source/ patched, delta-patch-<k>.json,        │
   │      context-delta.md                                    │
   │  bin/assemble-spec → output/v<N>-sgai-spec.md           │
   │  bin/lint-spec, check-incremental scope (blocking)      │
   │  6.1 bin/emit-extension-xsd                             │
   │        → output/v<N>-sgai-extension.xsd (blocking)      │
   └────────────────────────────┬─────────────────────────────┘
                                ▼
   ┌──────────────────────────────────────────────────────────┐
   │                       3-post-spec/                       │
   │  8.0 bin/check-dash-conformance --source (code, first)  │
   │        → v<N>-conformance-tests.md / .json              │
   │  7   validate-spec → v<N>-spec-validation.md            │
   │        + .summary.json, v<N>-trace.json (check-trace)   │
   │  7.5 review-spec-details (names only, edits nothing)    │
   │        → v<N>-detail-review.md (+ .patch.json)          │
   │  8   audit-dash-conformance → v<N>-dash-conformance-    │
   │        audit.md (what changed; blocks nothing)          │
   └────────────────────────────┬─────────────────────────────┘
                                ▼
   ┌──────────────────────────────────────────────────────────┐
   │                     4-auto-refine/                       │
   │  ┌── loop (gated by BUILD_ALL_AUTO_REFINE,              │
   │  │         capped at MAX_REFINEMENTS) ───────────────┐  │
   │  │  refine-spec → v<N>.<M+1>-patch.json              │  │
   │  │  assemble, lint, 6.1, 8.0, 7 (changed units),     │  │
   │  │  7.5; the audit is carried, not re-run            │  │
   │  │  bin/check-promotable → stop condition            │  │
   │  │  bin/compare-candidates → v<N>.<M+1>-comparison   │  │
   │  │    (candidate vs what is published in dist/)      │  │
   │  │  verdict: BETTER THAN PUBLISHED   → continue      │  │
   │  │           NO BETTER THAN PUBLISHED → break        │  │
   │  │           WORSE THAN PUBLISHED    → --reverse,    │  │
   │  │                                     break         │  │
   │  └───────────────────────────────────────────────────┘  │
   └──────────────────────────────────────────────────────────┘
```

No step above writes to `../dist/`. The pipeline produces
**candidates**; `dist/` holds the **published** build, and a
candidate gets there by promotion — `bin/promote.py`, run outside the
pipeline (the `dist/` entry of "Layout" in `../CLAUDE.md`). Throughout,
`spec-source/` is the source of the newest candidate in `output/`: a
step that edits it either assembles a candidate or undoes its edit.

The legacy Players (`bin/check-dash-conformance.py --players`, level
3a) are not a pipeline step: they inform and do not block, and run by
hand or in the demo (`--demo`).

Stage 5 runs as a **separate orchestrator** (not chained into the
build-all flow above):

```
                 orchestrate-issues (manual; --dry-run | --live)
                                 │
                                 ▼
   ┌──────────────────────────────────────────────────────────────┐
   │                  .github-ai/prompts/issues/                          │
   │  detect-issues  → list open issues w/o handling labels       │
   │                   AND compute cycle_count per issue;         │
   │                   drop cycle_count >= 4 (D5 cap hit, label)  │
   │  for each surviving issue (cycle C in {1,2,3}):              │
   │    regenerate meta.md → issue-<N>/meta.md (fresh each run)   │
   │    triage-issue → issue-<N>/cycle-<C>/triage.md              │
   │    analyze-impact (Flow B only)                              │
   │                 → issue-<N>/cycle-<C>/impact.md              │
   │    propose-response                                          │
   │                 → issue-<N>/cycle-<C>/response.md            │
   │    post-response (only if trusted author + --live)           │
   │                 → comment + labels on GitHub                 │
   │  summary block → stdout (parent agent relays to Telegram)    │
   └──────────────────────────────────────────────────────────────┘
```

Per-issue artefact layout under `.github-ai/output-issues/`:

```
.github-ai/output-issues/issue-<N>/
├── meta.md            regenerated every run (no history)
├── cycle-1/           first AI cycle on the issue
│   ├── triage.md
│   ├── impact.md      (Flow B only)
│   └── response.md
├── cycle-2/           created when OP replied to cycle-1
│   └── ...
└── cycle-3/           capped at 3 by D5 (anti-loop)
```

`.github-ai/output-issues/` is gitignored — issue artefacts are
local-only scratch. The canonical record of posted responses
lives on GitHub itself.

Stage 6 mirrors the same shape against pull requests:

```
                 orchestrate-prs (manual; --dry-run | --live)
                                 │
                                 ▼
   ┌──────────────────────────────────────────────────────────────┐
   │                   .github-ai/prompts/prs/                            │
   │  detect-prs    → list open non-draft PRs w/o handling labels │
   │                  AND compute cycle_count per PR;             │
   │                  drop cycle_count >= 4 (D5 cap hit, label)   │
   │  for each surviving PR (cycle C in {1,2,3}):                 │
   │    regenerate meta.md → pr-<N>/meta.md (fresh each run)      │
   │    triage-pr   → pr-<N>/cycle-<C>/triage.md                  │
   │    analyze-pr  → pr-<N>/cycle-<C>/analyze.md                 │
   │                  (four axes: content / convention /          │
   │                   scope / downstream)                        │
   │    propose-review → pr-<N>/cycle-<C>/review.md               │
   │                     (verdict: LGTM | SUGGESTIONS |           │
   │                      BLOCKERS | SCOPE-MISMATCH)              │
   │                     (routing: comment | review)              │
   │    post-review (only if trusted author + --live)             │
   │                 → comment OR review (event=COMMENT only,     │
   │                   D12: never approve / request-changes /     │
   │                   merge) + labels on GitHub                  │
   │  summary block → stdout (parent agent relays to Telegram)    │
   └──────────────────────────────────────────────────────────────┘
```

Per-PR artefact layout under `.github-ai/output-prs/`:

```
.github-ai/output-prs/pr-<N>/
├── meta.md            regenerated every run (no history)
├── cycle-1/           first AI cycle on the PR
│   ├── triage.md
│   ├── analyze.md     (always — the four axes per D13)
│   └── review.md      (carries machine-readable meta header)
├── cycle-2/           created when author pushed new commits / replied
│   └── ...
└── cycle-3/           capped at 3 by D5 (anti-loop)
```

`.github-ai/output-prs/` is gitignored — PR artefacts are local-only
scratch. The canonical record of posted reviews lives on GitHub
itself.

## When to use which prompt

| Prompt                              | When to invoke                                                          | Lives in            |
|-------------------------------------|-------------------------------------------------------------------------|---------------------|
| `build-all`                         | Major: the `context/` delta with no cap, allowed to add and retire constructs (steps 0-8, + auto-refine loop step 9); also the minor path when `context/` did not move | root |
| `build-incremental`                 | `context/` changed by a bounded delta; absorb it into the latest candidate | root |
| `analyze-dash-gap`                  | `context/` changed; pre-spec gap analysis is stale                      | `1-pre-spec/`       |
| `build-error-semantics`             | `context/03-requirements.md` or `context/05-dash-linear-interfaces.md` changed | `1-pre-spec/` |
| `analyze-iab-ad-templates`          | Always (live external source; runs every build)                         | `1-pre-spec/`       |
| `apply-context-delta`               | Called by both orchestrators (`MODE=major` / `incremental`): applies `git diff <anchor>..HEAD -- context/` to `spec-source/` by patches, assembles the next candidate, writes its patches and `context-delta` trace | `2-build/` |
| `validate-spec`                     | After the conformance tests of a new candidate: per criterion, with the trace (`v<N>-trace.json`) and summary; scoped to changed units in a refine | `3-post-spec/` |
| `review-spec-details`               | New candidate: judges only the names `bin/name-candidates.py` lists; edits nothing, returns a patch | `3-post-spec/` |
| `audit-dash-conformance`            | Once per major or incremental, over what changed: suspicions no test covers, no verdict (`v<N>-dash-conformance-audit.md`) | `3-post-spec/` |
| `refine-spec`                       | Minor refinement as a patch on `spec-source/`; called by Step 9     | `4-auto-refine/`    |
| `orchestrate-issues`                | Process open GitHub issues end-to-end (regenerate `meta.md` + per-cycle triage/impact/response). Dry-run default; `--live` to post | `.github-ai/prompts/issues/` |
| `detect-issues`                     | Fetch open issues missing any handling label; computes `cycle_count` and drops issues at the D5 cap (`>= 4`, label `ai-conversation-cap-hit`) | `.github-ai/prompts/issues/`  |
| `triage-issue`                      | Classify one issue for cycle `C`: flow / severity / lang / trust; echoes `cycle_count` from `detect-issues` | `.github-ai/prompts/issues/`  |
| `analyze-impact`                    | Flow B only, cycle `C`: validate claims against `context/`, surface affected files | `.github-ai/prompts/issues/`  |
| `propose-response`                  | Draft a flow-appropriate reply in the detected language for cycle `C`; acknowledges prior cycle when `C > 1` | `.github-ai/prompts/issues/`  |
| `post-response`                     | Live mode + trusted author: post `cycle-<C>/response.md` and apply labels | `.github-ai/prompts/issues/`  |
| `orchestrate-prs`                   | Process open GitHub PRs end-to-end (regenerate `meta.md` + per-cycle triage/analyze/review). Dry-run default; `--live` to post comment / `--comment` review | `.github-ai/prompts/prs/`     |
| `detect-prs`                        | Fetch open non-draft PRs missing any handling label; computes `cycle_count` and drops PRs at the D5 cap (`>= 4`, label `pr:ai-conversation-cap-hit`) | `.github-ai/prompts/prs/`     |
| `triage-pr`                         | Classify one PR for cycle `C`: trust / severity / lang / files-touched / claim-summary; echoes `cycle_count` from `detect-prs` | `.github-ai/prompts/prs/`     |
| `analyze-pr`                        | Walk the four axes (content / convention / scope / downstream) and emit findings categorised by axis, severity, and granularity (generic vs line-specific) | `.github-ai/prompts/prs/`     |
| `propose-review`                    | Draft a verdict-appropriate review in the detected language for cycle `C`; pick verdict (LGTM / SUGGESTIONS / BLOCKERS / SCOPE-MISMATCH) and routing (comment vs review); acknowledges prior cycle when `C > 1` | `.github-ai/prompts/prs/`     |
| `post-review`                       | Live mode + trusted author: post `cycle-<C>/review.md` as comment OR review (event=COMMENT) with optional inline comments, and apply verdict-driven labels. NEVER approve / request-changes / merge (D12) | `.github-ai/prompts/prs/`     |

Each prompt declares its full **Inputs / Output / Skip if** contract
in its own header — this table is a quick-pick index, not the spec.

## Three iteration scales

| Trigger                                                                  | Path        |
|--------------------------------------------------------------------------|-------------|
| Requirement added / changed / dropped, the delta bounded                 | Incremental |
| New architectural decision (new construct, retired construct)            | Major       |
| A delta too large to be an increment, or one the incremental cannot place| Major       |
| Wording precision / cross-reference fixes                                | Minor       |
| Fix for a conformance-test `FAIL`                                         | Minor       |
| Renaming an attribute when a flagged issue says so                       | Minor       |

All three edit `../spec-source/` by patches and assemble the candidate
from it; none regenerates the prose from scratch.

- **Major** (`build-all`) applies the `context/` delta to the newest
  candidate with `2-build/apply-context-delta.prompt` in major mode:
  no cap on how much changes, and allowed to add and retire constructs
  and sections. Then its analyses and Step 9.
- **Incremental** (`build-incremental`) takes the latest candidate
  `v<N.M>` and the `context/` commits since it was built, and produces
  `v<N.M+1>` with only the affected sections changed and a trace
  (`output-analysis/v<N.M+1>-context-delta.md`) mapping each change to
  where it landed. Then the same analyses, the comparison, and Step 9.
  "Bounded" is not the operator's guess: the path recommends a major,
  and stops, when `bin/check-incremental.py scope` finds the change over
  `INCREMENTAL_MAX_CHANGED_FRACTION` of the spec (default 30%) or the
  apply step classes a change `needs-structure`; and it ends `DEGRADED`
  when `degradation` finds a document that lost what it had.
- **Minor** (Step 9 of both orchestrators) fixes what the analyses
  found, with `context/` fixed; by contract it takes no new requirement.
  With `context/` unchanged since the newest candidate, `build-all`
  skips the delta and runs only the loop.

## Step 9 — auto-refinement loop

After the delta and its analyses, both orchestrators enter a
refinement loop (gated by env var `BUILD_ALL_AUTO_REFINE`, default
`true`; capped at `MAX_REFINEMENTS`, default `5`). A round reads
sections, never the document.

Per iteration `K`, the loop:

1. Calls `4-auto-refine/refine-spec.prompt` → a patch on
   `spec-source/`, recorded in `v<N>.<M+1>-patch.json` (with
   `v<N>.<M+1>-refine-gaps.md` for what a minimal edit cannot resolve).
   It includes the ops of the previous round's
   `detail-review.patch.json`, if any.
2. Assembles `v<N>.<M+1>-sgai-spec.md` (`bin/assemble-spec.py`), lints
   it (a lint finding undoes the round and retries once), and emits its
   extension XSD (Step 6.1). Then the conformance tests (Step 8.0), the
   validation of the units whose sections changed (`bin/check-trace.py
   stale`), and the names (Step 7.5). The audit is carried unchanged
   from the previous candidate, not re-run.
3. Runs `../bin/check-promotable.py`, the loop's stop condition
   (`build-all` 9.5 and 9.5a own the branches): pipeline work keeps
   the loop going; a `context/` change a written source dictates
   stops it for the invoker to apply; a decision for a person stops
   it only after a fresh re-check found no source that answers it.
4. Runs `../bin/compare-candidates.py v<N>.<M+1>` → emits
   `v<N>.<M+1>-comparison.md` with a verdict line, measured against
   the published build in `../dist/`.
5. Reads the verdict and decides:
   - **BETTER THAN PUBLISHED** → accept the new minor, set `M := M+1`,
     loop again.
   - **NO BETTER THAN PUBLISHED** → break loop.
   - **WORSE THAN PUBLISHED** → rollback: `bin/apply-spec-patch.py
     --reverse` on the round's patch record, check that `spec-source/`
     assembles the previous candidate again, delete the round's files,
     keep the previous head, break loop.

   Accepting a minor here means the loop keeps building on it. It
   does **not** promote anything into `../dist/`.
6. If `K == MAX_REFINEMENTS` without a natural break → cap
   reached, keep the last accepted minor, break loop.

On runtime errors (model failure, timeout, sidecar generation
exception) the loop breaks, keeping the last successful iteration; a
patch applied but never assembled is undone, so the source stays the
newest candidate's.

### Configuration

| Env var                  | Default | Effect                                                          |
|--------------------------|---------|-----------------------------------------------------------------|
| `BUILD_ALL_AUTO_REFINE`  | `true`  | When `false`, Step 9 is skipped entirely.                       |
| `MAX_REFINEMENTS`        | `5`     | Hard cap on iterations of the loop.                             |

Both are read from `.env.agent`. See `../.env.agent.example` for
the canonical list of env vars.

### Verdict criterion

The verdict is the rule written in `../bin/compare-candidates.py`
(its `--help`), always against the published build in `../dist/`:
unit by unit on the units both sides walked, never count against
count. The audit's suspicions are reported and never enter it. When
the two populations are not comparable, or `../dist/` holds no
sidecars, there is no verdict and the loop breaks rather than guessing.

### The promotion criterion

Nothing here decides when a candidate becomes the published build.
The loop's verdicts govern whether to keep refining; promotion into
`../dist/` is `../bin/promote.py v<N>`, run outside the pipeline: it
runs every gate and copies the published set only when all hold.

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
   runs it under a skip rule of its own.
4. Update the "When to use which prompt" table above.

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

## The two layers, and who is in which

`context/` is the **WHAT**: what the system has to be able to do, what
obliges whom, what is out of scope. Iterating requirements happens here.

The build is the **HOW**: which construct carries each capability, which
attribute holds it, how it is expressed in a manifest. An agent
generating the specification is here.

**A requirement that fixes the carrier has crossed into the other
layer.** *"The Publisher MAY declare that the window presents only
once"* is the WHAT; whether that travels in an attribute of our own or
in a field the base standard already provides is the HOW, and the build
decides it.

**And delegating the HOW only works when whoever decides knows the
alternatives.** A carrier named nowhere does not enter the comparison,
and then the HOW is not chosen — it falls out by default. This has
already happened once: a capability was carried by a new attribute
without the base standard's own field ever being weighed, because
nothing said that field existed. Carrier conventions therefore live in
`context/06-naming-and-namespaces.md`, which is HOW and not WHAT, and so
does not contradict this rule.

## Layout

```
projects/sgai-for-mpeg-dash/
├── README.md             user-facing — what / how to read / how to build
├── CLAUDE.md             this file — conventions for subagents
├── context/              inputs — canonical, human-authored spec
├── prompts/              build scripts — .prompt files for LLM agents
├── context-analysis/     pre-spec artefacts — derived from context/ and consumed by the spec build
├── spec-source/          the source of the spec — prose with directives, XSD + syntax.yaml, example fixtures, UC vectors, behaviour tests
├── dist/                 the published spec + its analyses — unversioned names; arrives by promotion, never by build
├── output/               candidate specs and their extension XSD, one per build iteration (vN-sgai-spec.md, vN-sgai-extension.xsd), assembled from spec-source/
├── output-analysis/      per-candidate analyses and records (validation + trace, detail-review, conformance tests, audit, patches, comparison) + ad-hoc research / errata
├── .github-ai/           GitHub-feedback pipelines (Stages 5 & 6) — prompts + scratch
│   ├── prompts/
│   │   ├── issues/       Stage 5 prompts — GitHub issues triage + auto-response
│   │   └── prs/          Stage 6 prompts — GitHub PRs review
│   ├── output-issues/    Stage 5 scratch (gitignored) — per-issue triage / impact / response drafts
│   └── output-prs/       Stage 6 scratch (gitignored) — per-PR triage / analyze / review drafts
├── bin/                  executable checks the build runs; not prompts
├── reference-player/     the reference Player — a module on pinned dash.js 5.3.0, its edge vectors and the demo
├── proposal-drafts/      historical drafts kept for reference
└── .project/             governance from the create-project skill
```

What does NOT go where:

- `context/` — no generated artefacts, no analysis, no scratch. Only
  the human-authored canonical spec files. If you generated it from
  the spec, it does not live in `context/`. **`context/` MUST be
  self-contained**: files inside `context/` MUST NOT reference any
  artefact under `context-analysis/`, `spec-source/`, `output/` or
  `output-analysis/`, neither as a "see also" pointer nor as a source
  for substantive content. The dependency arrow is strictly
  `context/` → `context-analysis/` → `spec-source/` → `output/` →
  `output-analysis/`;
  pointers in the reverse direction invert the layering. When a
  `context/` document needs additional information to stand on its
  own (a concept, a baseline citation, a vocabulary anchor), that
  information either lives directly inside `context/` or cites the
  primary external source (an ISO spec, an IAB document, an RFC) —
  never our own downstream derivatives. The test: someone reading
  only `context/` MUST have everything they need to understand the
  spec we want to generate; if they would need to open something
  downstream of it to follow
  along, the missing piece belongs back inside `context/`.
- `prompts/` — only `.prompt` files. No build scripts in other
  languages, no helpers, no READMEs. An executable a prompt needs to
  invoke lives in `bin/` and is called from the prompt body.
- `bin/` — executable checks and helpers the build invokes. Something
  belongs here rather than in a prompt when it must be able to **fail**:
  a prompt can be reasoned around, a non-zero exit cannot. Flags and
  formats live in each script's `--help`, not here, and so does what its
  green covers and what it does not — a check read as answering more
  than it asks is how a green becomes misleading. The exits are shared:
  `0` nothing found (or done), `1` found (or refused), `2` cannot tell,
  `64` wrong command line. The `2` is the point: uncertainty wins over
  both others, because zero findings is also what a check that never
  ran looks like, and `64` is kept apart so a misspelled flag can never
  be read as a verdict about the build.

  **Gates on `context/`** (Steps 0–0.7 of `build-all`, blocking):
  - `check-normative-base.py` (Step 0) — `context/00-normative-base.md`
    still describes the copy of the standard on disk.
  - `check-context-coherence.py` (0.5) — `context/` holds together:
    identifiers defined, no duplicates, links resolving.
  - `check-context-vocabulary.py` (0.6) — values used outside the closed
    enumeration that declares them, enumerated items with no token, a
    term a requirement confines to illustrative material used outside
    it, RFC 2119 modals that bind no one, a normative file that obliges
    no one, frequent terms with no glossary entry, open questions
    missing from the register. Every rule is read off `context/`
    itself, so it ships with no list of what today's `context/` says,
    and its green means nothing was found rather than that something
    was excused. No enumeration, glossary or register is a `2`: the rule
    never ran.
  - `check-context-interfaces.py` (0.7) — each row of 03's "Interfaces"
    index points to one existing criterion held by the party that writes
    that interface, no element is indexed twice, no retired identifier is
    cited outside the "Retired identifiers" table, no criterion vanished
    without a row there.

  **The source and the document** (ADR 0060–0062, 0066):
  - `assemble-spec.py` — expands the directives of
    `spec-source/sgai-spec.src.md` into `output/v<N>-sgai-spec.md` (and
    `v<N>-source.sha256`), or says whether a document is that assembly
    byte for byte (`--check`). `--check` against the newest candidate is
    the invariant every step that edits `spec-source/` keeps.
  - `gen-syntax-tables.py` — generates the §5 tables
    (`spec-source/syntax/tables/`) from the extension XSD, ISO's
    `DASH-MPD.xsd` and `syntax.yaml`, or checks they are current; every
    override and every disagreement with the schemas is listed.
  - `spec-section.py` — reads the prose, or an assembled spec, by section
    key, so an agent loads what it edits and not the file.
    `spec_sections.py` is the one section split every script shares.
  - `apply-spec-patch.py` — the only way the prose and the artefacts of
    `spec-source/` are edited: a JSON patch of section and file ops,
    refused whole when a `find` is not unique, a directive is touched,
    a section changes that the patch does not declare, or the change is
    over `--max-fraction`. `--record` writes the patch record (the trace
    of an edit, with what undoing it needs); `--reverse` undoes a
    recorded patch byte for byte, or refuses.
  - `strip-legacy-annotations.py` — the one-time patch that removes the
    old pipeline's marks (inline `refine` / `delta` comments, the
    "Refinement gaps" section, a hand-typed build iteration). Idempotent:
    the apply step runs it every build, and it finds nothing after the
    first.
  - `emit-extension-xsd.py` (Step 6.1) — copies the spec's §5.10.1
    `xs:schema` block byte for byte to `v<N>-sgai-extension.xsd` beside
    the candidate, only if it compiles with ISO's 6th-edition
    `DASH-MPD.xsd`. Nothing about whether the extensions conform.

  **Judged by code:**
  - `lint-spec.py` — an assembled document is editorially clean:
    references resolve, ids defined once, namespace prefixes declared,
    no draft markers, no HTML comments, no gaps section.
  - `check-dash-conformance.py` (Step 8.0) — the conformance verdict is
    its exit, not an LLM's reading (ADR 0053): level 1 (the extension XSD
    and the examples against ISO/IEC 23009-1 6th edition) and level 2
    (the document criteria of `context/03`). The build runs it with
    `--source spec-source`: each fixture by the class
    `examples/index.yaml` declares, plus the source-only rules (ADR
    0063). Its green says every rule decidable by code passed on the
    instances the source contains; nothing about what is
    `NOT_VERIFIABLE` (listed with its reason) nor about constructs with
    no example. `--players` (level 3a), `--demo` and `--behaviour` are
    not build steps; `--behaviour` runs the behaviour tests and the UC
    vectors on the reference Player in Chromium, and is opt-in (ADR
    0087): nothing in the project runs it, and
    `test_behaviour_opt_in.py` guards that.
    `conformance/` is the code behind it: `dash/` the level-1 rule
    catalogue, `spec/` the level-2 one, each rule with its quoted
    sentence, `fixtures/` the committed negatives — a rule's green is
    only as good as its transcription, and its negative is what shows
    it can fail. `players/` pins the legacy Players (dash.js 5.3.0,
    Shaka 5.3.6, headless Chromium through Playwright); they inform and
    do not block (ADR 0057), so they run by hand. `dashif/` builds the
    pinned DASH-IF conformance tool (`v3.1.0`) as a second auditor whose
    findings never change the exit (`--dashif`, bridged by
    `conformance/dashif.py`); its XSD verdict is the 5th edition's and is
    discarded.
  - `check-scenarios.py` — the UC vectors of `spec-source/scenarios/`
    cover every UC × class of `context/04`, are well formed, rest on
    green fixtures, and were written against each UC as it is now (a
    stale hash is a `2`). The apply step runs it in its artefact loop.
    It runs no Player: whether one behaves as a vector says is
    `--behaviour`'s.
  - `check-behaviour.py` — every criterion the level-2 catalogue sends
    to level 3 has a behaviour test in `spec-source/behaviour/` or an
    `index.yaml` entry with its `NOT_VERIFIABLE` reason, and each test
    was written against its criterion as it is now. Shares the schema
    and checks of `check-scenarios.py`; runs no Player either.
  - `check-trace.py` — the validation's trace (`v<N>-trace.json`): every
    unit of the population has an entry, its sections exist, its
    quotations are literal, the rules it names exist and decide.
    `sources` gives each unit its verdict source from the conformance
    tests, `stale` the units whose sections changed between two
    candidates (what a refine's validation walks), `batch` what a
    walker reads for a batch of units.
  - `validate.py` (Step 7) — the whole validation as code: population,
    sources, what is walked by mode, batches, merge, trace, sidecar and
    summary. The model only answers single-turn calls with no tools and no
    `CLAUDE.md`: the walkers (`walk-batches.py`) and the open search.
  - `walk-batches.py` — runs the walkers as single-turn calls and
    validates every answer by code (schema, verdict values, sections that
    exist, quotations literal in their section, a quotation for every
    verdict but `gap`/`governance`); what fails gets one retry and then
    `not-verifiable`, never `met`.
  - `validation-summary.py` — writes `v<N>-spec-validation.summary.json`
    from the sidecar with `check-promotable.py`'s own parsers: scripts
    read the summary, never the prose.
  - `name-candidates.py` — the names of the extension schema equal or
    close to a name of ISO's schema, with the sections that mention
    them; the list `review-spec-details` judges, not a verdict.
  - `check-promotable.py` — the auto-refine loop's stop condition and a
    promotion gate: it reads the candidate's validation, detail review
    and `conformance-tests.json` (the audit only for its suspicions,
    which never block), checks that the walk covered every obligation
    `context/` states, and reports what blocks grouped by **who lifts
    it** — the pipeline, the coordinator applying a `context/` change a
    written source dictates, or a person — as the validation routed it
    (§5 of `validate-spec.prompt` owns the routing rule).
    `--population` prints the units that must be walked; the validation
    reads that list rather than counting on its own.
  - `check-incremental.py` — `anchor` (which commit's `context/` a
    candidate was built from), `scope` (the new candidate changed exactly
    the sections its trace and its patches declare, and not more than
    the cap; a major passes `--max-fraction inf`) and `degradation`
    (units the delta did not touch did not fall from `met` to a blocking
    verdict, and the modals did not drop). It imports
    `check-promotable.py`'s parser so the two cannot read a sidecar
    differently.
  - `compare-candidates.py` — a candidate against what is published in
    `dist/`, unit by unit on the units both walked, by the rule its
    `--help` writes (ADR 0070); writes `v<N>-comparison.md`. Populations
    that are not comparable are a `2`, never a verdict.
  - `step-inputs.py` — whether a pre-spec step has to run again, by the
    hashes of its inputs recorded beside its output, never by date
    (ADR 0072).
  - `promote.py` — the promotion: every gate, then the copy (below,
    under `dist/`).

  **Outside the build:**
  - `check-dist-freshness.py` — whether `dist/` was built from the inputs
    as they stand now: `context/`, `context-analysis/`, `prompts/` and
    `spec-source/` against the hashes in `dist/inputs.sha256`, naming
    every file that moved. By content, never by date. With no manifest
    it fails: an unrecorded `dist/` is one whose inputs nobody knows.
  - `measure-run.py` — what a run cost per step (input, cache, output,
    calls), read from its Claude Code transcript, counting each API call
    once (ADR 0074). Run it on the session id **right after the run**:
    transcripts are deleted after 30 days.
  - `reference-player/test/edges/run-edges.py` and
    `reference-player/demo/demo.py` — the reference's edge vectors of
    the linear model (E1–E14) and the recorded demo session; opt-in
    like `--behaviour`, whose harness they use. Their READMEs say how.

  **Dependencies.** Most scripts need only the standard library; which
  ones need `lxml`, PyYAML or `jsonschema`, which re-run themselves
  under `uv`, and how to run the whole suite (`bin/test_*.py`) is in
  `SETUP.md` → "Dependencies".
- `context-analysis/` — only **pre-spec** generated artefacts that
  the spec build consumes as inputs (gap analysis, error semantics,
  IAB ad templates). Derived from `context/`. No human-authored
  notes; those go to `.project/decisions/` or inside the spec. No
  post-spec artefacts — those go to `output/` or `output-analysis/`.
  `uc-coverage-matrix.md` and `conformance-assertions.md` are records
  of retired steps (ADR 0072): nothing regenerates or reads them.
- `spec-source/` — the source of the spec (ADR 0060), and the only
  place the spec is edited. `sgai-spec.src.md` is the prose, with
  directives `bin/assemble-spec.py` expands: `{{example:…}}`, `{{xsd}}`,
  `{{include:…}}` (a generated fragment) and `{{version}}`. `syntax/`
  holds the extension schema `sgai-extension.xsd`, `syntax.yaml` (what
  a schema cannot say) and `tables/`, the §5 tables generated from both
  — never edited by hand. `examples/` holds the examples as fixtures,
  each with the class `index.yaml` declares. `scenarios/` holds the
  use cases as vectors (`UC-NN.yaml`, `schema.json`, their `fixtures/`;
  `README.md` says how one is written). `behaviour/` holds one or more
  behaviour tests per criterion of `context/03` that needs a Player
  (`R<n>.<m>[-<k>].yaml`, same schema, `index.yaml` for those with
  none; its `README.md` says how one is written). **Invariant: `spec-source/` is
  always the source of the newest candidate in `output/`** —
  `bin/assemble-spec.py --check` on it exits 0 —, so every step that
  edits it either assembles a new candidate or undoes its edit. Edits
  are patches (`bin/apply-spec-patch.py`), never free-hand writes.
- `reference-player/` — the reference Player's code (ADR 0075, 0076):
  `src/` the module loaded on the unmodified pinned dash.js 5.3.0 of
  `bin/players/`, `test/edges/` its edge vectors, `demo/` the demo,
  `spike/` the T-01 spike (ADR 0075). No spec content and no
  behaviour tests: those are in `spec-source/`.
- `dist/` — the published spec and its analyses, under names with no
  version: `sgai-spec.md`, `sgai-extension.xsd`,
  `spec-validation.md`, `detail-review.md`, `conformance-tests.md`,
  `conformance-tests.json`, `dash-conformance-audit.md`,
  `comparison.md`, `trace.json`, plus `PROVENANCE.md` (which candidate)
  and `inputs.sha256`. This is what the
  project stands behind; anyone asking "what does the spec say" is
  answered from here and from nowhere else.

  **No build writes here.** Files arrive by **promotion** — a
  candidate and its extension XSD in `output/` and its sidecars in
  `output-analysis/` are
  judged good enough and moved in, replacing what was there. A build
  step that writes into `dist/` has confused producing a candidate
  with publishing one, which is the distinction this directory
  exists to hold.

  **The promotion criterion is `bin/promote.py v<N>`** (ADR 0073): it
  runs every gate — the candidate is the assembly of `spec-source/`,
  lint clean, its trace checks, `check-promotable.py` exits `0`, the
  comparison says `BETTER THAN PUBLISHED`, the conformance tests on the
  source exit `0`, and every file of the published set exists — and
  copies the set only when all hold. A conformance `FAIL` blocks; a
  `NOT_VERIFIABLE` does not. The LLM audit blocks nothing: a suspicion
  of it blocks only once it is a rule that fails. The Players inform
  and do not block (ADR 0057). The coordinator runs it, and when it
  exits `0` tells the project lead what was promoted; it does not ask.
  Anything short of all gates stays a candidate, and the script names
  every gate that failed.

  The unversioned names are deliberate. A link to the spec has to
  survive the next build, and the spec's own title carries no version
  either (`# SGAI for Linear and Non-Linear Ads in MPEG-DASH`), so a
  versioned filename was the only place the version lived. History
  lives in git and in `output/`.
- `output/` — the candidate spec and its extension XSD, and only
  that. Two files per build iteration: `v<N>-sgai-spec.md`, assembled
  from `spec-source/`, and `v<N>-sgai-extension.xsd`, the spec's
  §5.10.1 block extracted by code (ADR 0047). A candidate is what a build
  produced; it becomes what the project publishes only if it is
  promoted into `dist/`. Any post-spec artefact — the validation
  sidecar, the detail-review log, the conformance tests, the audit —
  belongs to `output-analysis/`, not here. Never edit by hand: a
  candidate is the assembly of its source, and if a build came out
  wrong, fix the context, the prompt or the code and rebuild.
- `output-analysis/` — every analysis and record of a specific
  candidate. This includes both (a) what the orchestrators write per
  candidate (validation sidecar with its trace and summary, detail
  review, conformance tests, audit, comparison, the patches and the
  source manifest; the list is under "Naming conventions") and (b)
  ad-hoc analyses created by hand
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
  suffix (`analyze-dash-gap.prompt`, `apply-context-delta.prompt`,
  `build-all.prompt`). Each prompt opens with a header block
  declaring **Inputs / Output / Skip if** before the `---` divider.
- **`context-analysis/` files**: no numeric prefix. Each artefact
  standalone, named for what it analyses
  (`dash-gap-analysis.md`).
- **`output/` files**: version **prefix** `vN-`, where N is the
  iteration number of the build that produced the artefact. The
  filesystem sorts builds by iteration. Two canonical patterns:
  `v<N>-sgai-spec.md` (the spec) and `v<N>-sgai-extension.xsd` (its
  extension schema). N is computed by the build-all
  orchestrator as `max(v* in output/) + 1`. Files are **not
  overwritten**; each build keeps history.
- **`output-analysis/` files**: prefix `vN-` matching the
  iteration of the spec the analysis is grounded against. Written
  per candidate by the orchestrators:
  - how it was made: `v<N>-delta-patch-<k>.json` (a major's or an
    incremental's patch records, `k = 0` the legacy cleanup when there
    was one) and `v<N>-context-delta.md` (its trace, with the `context/`
    commits it covers), or `v<N>-patch.json` and, when something could
    not be resolved, `v<N>-refine-gaps.md` (a refine);
    `v<N>-source.sha256` (the source files it was assembled from);
  - what was found: `v<N>-conformance-tests.md` and `.json` (Step 8.0),
    `v<N>-spec-validation.md` with `v<N>-spec-validation.summary.json`
    and `v<N>-trace.json` (Step 7), `v<N>-detail-review.md` and, when
    it has a sure fix, `v<N>-detail-review.patch.json` (Step 7.5),
    `v<N>-dash-conformance-audit.md` (Step 8, carried unchanged inside
    the refine loop), `v<N>-comparison.md` (`bin/compare-candidates.py`).

  Ad-hoc analyses created by hand follow
  `v<N>-<name>.md` (e.g. `v3-non-video-carrier-research.md`,
  `v3-non-video-carrier-research-errata-1.md`).
- **General**: kebab-case for filenames. English for all content
  inside `context/`, `prompts/`, `context-analysis/`, `spec-source/`, `output/`,
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
   orchestrator runs it under a skip rule of its own; the
   reference inside `build-all.prompt` uses the full path
   `prompts/<stage-folder>/<file>.prompt`.
4. Decide where the output lives: pre-spec build input →
   `context-analysis/`, the candidate spec → `output/`, per-candidate
   analysis of the spec OR ad-hoc post-spec study about a specific
   candidate → `output-analysis/`. Never `dist/`: a step writes
   candidates, and promotion is not a step.
5. Update `prompts/README.md`: the folder layout if a new
   subfolder appears, the "When to use which prompt" table, and
   the pipeline diagram if the new prompt changes the flow.

## How to modify the spec

Edit the file in `context/` directly, and commit it: a build absorbs
the `context/` commits since its base was built, and an uncommitted
change is a delta no commit records. Then run an incremental or a
major (below); each step skips by its own rule (the pre-spec steps by
the hashes of their inputs, `bin/step-inputs.py`). Nobody edits
`spec-source/` or `output/` by hand to change what the spec says: the
spec changes through the pipeline's patches, so every change has a
record. `dist/` is not regenerated — it stays as published until a
candidate is promoted over it. What it does go stale against is its
**inputs**, and `bin/check-dist-freshness.py` names every file that
moved since the published build was made.

### How to invoke a build

```bash
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 \
  claude -p "$(cat prompts/build-all.prompt)"
```

**The environment variable is not optional.** `claude -p` terminates a
run after waiting 600 seconds for background tasks, and this pipeline
dispatches subagents by contract — the apply step, the audit and each
refine run in fresh subagent contexts (the validation is `bin/validate.py`,
whose model calls are single-turn). Without the
variable the run is killed **while collecting work that has already
been done and paid for** — and it reports the step it was waiting on as
still running, because the orchestrator's last message is composed
before the subagent delivers. That is worse than failing: the work is
on disk, the run that would have used it is gone, and the log says the
opposite.

The same applies to any prompt invoked on its own that dispatches a
subagent.

When renumbering or renaming files in `context/`:

- Update the TOC in `context/01-intro.md`.
- Update every cross-ref in the other `context/*.md` files.
- Update refs from `context-analysis/*.md` (use
  `../context/<file>` paths).
- Update refs in `.project/` (`PROJECT.md`, `phases/`,
  `decisions/`). Be conservative with `LOG.md`: historical entries
  reference the old layout — preserve them verbatim; only update
  live navigational references.

### How to measure a run

```bash
python3 bin/measure-run.py <session-id>
```

Run it right after the run, on the session id of the `claude -p` that
ran it: Claude Code deletes transcripts after 30 days, and with them
the only record of what each step cost. It reports tokens per step, not
money.

## Iteration scales: major, incremental, minor

Three iteration scales coexist in this project. All three edit
`spec-source/` by patches and assemble the candidate from it; none
rewrites the prose from scratch (ADR 0067). What they differ in is how
much may change and what triggers them.

- **Major (vN+1)** — a new architectural decision (a construct added
  or retired), or a `context/` delta too large or too structural for
  the incremental path. Run `prompts/build-all.prompt` (above; a
  `MAJOR_BRIEF` names the ADRs or the instruction that ask for the new
  construct): the gates and pre-spec steps, then
  `prompts/2-build/apply-context-delta.prompt` in major mode on the
  newest candidate — the same delta path as an incremental, with no
  cap on how much changes and allowed to add and retire constructs and
  sections. Then the post-spec steps and the Step 9 loop.
- **Incremental (vN.M+1)** — `context/` changed by a bounded delta:
  requirements added, changed or dropped that the existing spec has a
  place for. Run the incremental orchestrator:

  ```bash
  CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 \
    claude -p "$(cat prompts/build-incremental.prompt)"
  ```

  It takes the latest candidate `v<N.M>` and
  `git diff <anchor>..HEAD -- context/`, where the anchor is what
  `bin/check-incremental.py anchor v<N.M>` prints (never worked out by
  hand). The apply step edits the artefacts first (fixtures, schema,
  vectors, in a loop with the conformance and scenario checks), then the
  prose by section patches, and assembles `v<N.M+1>`, with
  `output-analysis/v<N.M+1>-context-delta.md` mapping each change to
  where it landed. The path stops and says `MAJOR RECOMMENDED` when the
  change exceeds `INCREMENTAL_MAX_CHANGED_FRACTION` of the spec or needs
  structure the spec does not have, and `DEGRADED` when the result lost
  what the base had (`bin/check-incremental.py --help`); a failure
  restores `spec-source/` to the base's. It never starts the major
  itself.
- **Minor (vN.M+1)** — `context/` unchanged; the latest analyses
  surfaced issues that can be fixed without altering requirements. This
  is Step 9 of both orchestrators, and it runs on its own after a major
  or an incremental. To run it without a delta, run `build-all` with
  `context/` unchanged since the newest candidate: Step 6 skips and the
  loop starts from that candidate. Each round
  (`prompts/4-auto-refine/refine-spec.prompt`) reads only the sections
  its issues point at and writes a patch
  (`output-analysis/v<N.M+1>-patch.json`, with
  `v<N.M+1>-refine-gaps.md` for what it could not resolve); the round is
  assembled and linted, then the conformance tests, the validation of
  the units whose sections changed, the names, and
  `bin/check-promotable.py` as the stop condition. The audit is not
  re-run in the loop: it is carried (ADR 0071).
  `bin/compare-candidates.py` then judges the round against **what is
  published in `dist/`** (`BETTER` / `NO BETTER` / `WORSE THAN
  PUBLISHED`); `WORSE` undoes the round with
  `bin/apply-spec-patch.py --reverse`. The baseline is the published
  build because the useful question is whether this beats what the
  project currently gives as good. The verdict decides whether to keep
  refining, not whether to promote.

**Which scale**:

| Trigger                                                                  | Path        |
|--------------------------------------------------------------------------|-------------|
| Requirement added / changed / dropped, the delta bounded                 | Incremental |
| New architectural decision (new construct, retired construct)            | Major       |
| A delta too large to be an increment, or one the incremental cannot place| Major       |
| Wording precision / cross-reference fixes                                | Minor       |
| Fix for a conformance-test `FAIL`                                         | Minor       |
| Renaming an attribute when an existing flagged issue says so             | Minor       |

The operator picks the path. What the incremental path decides on its
own is only whether it has to give up and hand over to a major.

## GitHub issues pipeline (Stage 5)

A separate stage handles inbound GitHub issues on
`qualabs/sgai-for-mpeg-dash`. The build pipeline (Stages 1..4)
produces the spec; Stage 5 reacts to external feedback on it.

### Entry point

Manual invocation (D7 — cron deferred):

```bash
# Default — dry-run, never posts to GitHub.
claude -p "$(cat .github-ai/prompts/issues/orchestrate-issues.prompt)"

# Explicit live mode — drafts AND posts comments + applies labels.
claude -p "$(cat .github-ai/prompts/issues/orchestrate-issues.prompt)" -- --live
```

The six prompts live under `.github-ai/prompts/issues/`:

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
  a recommended action, and projects the verdict into a binary
  **issue disposition** (`RESOLVED-BY-RESPONSE` /
  `NEEDS-NEXT-STEP`, D14) that `propose-response` adopts verbatim
  for the response's `## Issue conclusion` section. Queries
  the base standard only if specific keywords appear in the issue body
  (D6): `DASH`, `ISO 23009`, `IAB`, `SCTE-35`, `SCTE`, `MPEG`,
  `CMAF`, `HLS`.
- `propose-response.prompt` — drafts a flow-appropriate reply in
  the detected language. Adds the auto-draft disclaimer at the
  top when `severity ∈ {requirements, architectural}` (D3).
  Picks the binary **issue conclusion**
  (`RESOLVED-BY-RESPONSE` / `NEEDS-NEXT-STEP`, D14) and appends
  a mandatory `## Issue conclusion` section with either a
  closing rationale paragraph (RESOLVED-BY-RESPONSE) or a
  `### Next steps` action list (NEEDS-NEXT-STEP). Embeds a
  machine-readable metadata header
  (`<!-- sgai-issues-meta: ... -->`, including `conclusion` +
  `conclusion_reason`) so `post-response` does not re-parse the
  body. Every draft ends with the hidden marker
  `<!-- sgai-issues: ai-cycle -->` used by future runs to count
  cycles.
- `post-response.prompt` — only fires in `--live` mode for
  **trusted** authors. Parses the meta header, posts the comment
  via `gh issue comment`, and applies labels: `ai-responded`,
  `severity:<X>`, `flow:<A|B|C>`, plus exactly one of
  `issue:can-close` (`conclusion: resolved`) or
  `issue:needs-next-step` (`conclusion: needs-next-step`) per
  D14.

### Decisions encoded in the pipeline

| ID | Decision |
| --- | --- |
| D1 | Default mode is `--dry-run`. `--live` posts to GitHub. |
| D2 | Trusted authors (`TRUSTED_GH_USERS` in `.env.agent`) get the full auto cycle. Outsiders' drafts are held with `ai-needs-review` and surfaced to the project lead via Telegram for manual decision. He may optionally promote them into `TRUSTED_GH_USERS` afterwards. |
| D3 | `severity:requirements` (and `severity:architectural` by extension) carry an explicit AI-disclaimer blockquote at the top of the response. |
| D4 | Language detection falls back to English when inconclusive. |
| D5 | Anti-loop cap of 3 AI cycles per issue. Enforced by `detect-issues`: when `cycle_count >= 4`, apply label `ai-conversation-cap-hit` and drop the issue before triage. |
| D6 | The base standard is consulted only when the keyword detector trips. |
| D7 | Trigger is manual today. Cron is future work. |
| D14 | Each Stage 5 response ends with a binary **issue conclusion**: **RESOLVED-BY-RESPONSE** (`conclusion: resolved`) or **NEEDS-NEXT-STEP** (`conclusion: needs-next-step`). Resolved when the AI's response covers what the issue raiser asked (context pointer, decision clarification, duplicate, out-of-scope) AND no change is required to spec / ADRs / docs. Needs-next-step when the issue requires future action (PR against `context/`, ADR under `.project/decisions/`, WG input, follow-up issue, clarification from the raiser, partial-incorporate, defer). For Flow B issues, `analyze-impact.prompt` declares the disposition in `impact.md` under `## Issue disposition`; `propose-response.prompt` adopts it verbatim and writes it into the response's `## Issue conclusion` section plus the machine-readable header `<!-- sgai-issues-meta: ... conclusion: ... conclusion_reason: ... -->`. Flow A and Flow C draftees decide the conclusion directly from the response content. Labels mapped: `issue:can-close` if resolved; `issue:needs-next-step` if needs-next-step — applied by `post-response.prompt` (mutually exclusive). Orthogonal to `flow` (A/B/C) and `severity` — flow and severity characterise what the AI did; the conclusion characterises what the maintainer / WG / raiser does next. Mirrors Stage 6 D11 (MERGEABLE / NEEDS-WORK). |
| D15 | An issue whose body carries `<!-- sgai-issues: ours -->` is dropped by `detect-issues` in every mode, including an explicit `--issue <N>` re-run. The marker is added by whoever publishes it, at the end of the body; it is an HTML comment and invisible on GitHub. **The filter is on direction, not on author**: these are the `[DISCUSSION]` questions this project posts *to* the working group, so there is no inbound feedback to triage, and without the marker they route to Flow B like any other issue naming `context/` files. Replacing it with an author filter breaks D2, under which a trusted author's issue gets the full automatic cycle. The reasoning is in `detect-issues.prompt` §2b. |

### Scratch directory

Per-issue artefacts go to `.github-ai/output-issues/issue-<N>/` with a
**meta + per-cycle** layout:

```
.github-ai/output-issues/issue-<N>/
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

### Reporting to the project lead

The Stage-5 orchestrator never sends Telegram messages directly.
At the end of each run it emits a fenced summary block to stdout
between `=== SGAI-ISSUES RUN SUMMARY ===` and `=== END SUMMARY ===`.
The parent agent (whichever session invoked the orchestrator)
relays that block to the project lead — with special attention to the
`needs-review` subsection (outsiders waiting on the project lead's call).

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
  The project lead's attention.

## GitHub PRs pipeline (Stage 6)

A separate stage handles inbound GitHub pull requests on
`qualabs/sgai-for-mpeg-dash`. The build pipeline (Stages 1..4)
produces the spec; Stage 5 reacts to external feedback on it via
issues; Stage 6 reacts to external feedback via PRs — i.e. diffs
that the author wants merged.

### Entry point

Manual invocation (D7 — cron deferred):

```bash
# Default — dry-run, never posts to GitHub.
claude -p "$(cat .github-ai/prompts/prs/orchestrate-prs.prompt)"

# Explicit live mode — drafts AND posts comment / --comment review +
# applies labels.
claude -p "$(cat .github-ai/prompts/prs/orchestrate-prs.prompt)" -- --live
```

The six prompts live under `.github-ai/prompts/prs/`:

- `orchestrate-prs.prompt` — the Stage-6 orchestrator. Reads
  `.env.agent`, queries GitHub, drives the per-PR loop, emits the
  end-of-run summary block.
- `detect-prs.prompt` — lists open non-draft PRs whose label set
  does not contain `pr:ai-reviewed`, `pr:ai-needs-review`, or
  `pr:ai-conversation-cap-hit`.
- `triage-pr.prompt` — classifies each PR: `trusted` boolean,
  `severity` (cosmetic / spec-detail / requirements /
  architectural), `lang` (ISO-639-1 with `en` fallback per D4),
  `files_touched` (grouped by root), `claim_summary`, and
  `cycle_count` (anti-loop, D5).
- `analyze-pr.prompt` — walks the four axes (D13): content
  validation (claims vs `context/` + the base standard when
  keywords trip D6), convention compliance (`CLAUDE.md` rules:
  naming, file placement, cross-refs), scope coherence (PR body
  vs actual diff), downstream impact (stale `context-analysis/`,
  `spec-source/`, `output/`, `output-analysis/` per the dependency
  arrow). Emits findings categorised by axis, severity (blocker /
  suggestion / info), and granularity (generic / line-specific).
- `propose-review.prompt` — drafts a verdict-appropriate review
  in the detected language. Adds the auto-draft disclaimer at the
  top when `severity ∈ {requirements, architectural}` (D3).
  Picks the verdict (`LGTM` / `SUGGESTIONS` / `BLOCKERS` /
  `SCOPE-MISMATCH`, D11), the binary **mergeable conclusion**
  (`MERGEABLE` / `NEEDS-WORK`, D11) and the routing (`comment` vs
  `review`, D8) based on findings. Appends a mandatory `##
  Mergeable decision` section with either a rationale paragraph
  (MERGEABLE) or a `Path to merge` action list (NEEDS-WORK).
  Embeds a machine-readable metadata header
  (`<!-- sgai-prs-meta: ... -->`, now including `mergeable` +
  `mergeable_reason`) so `post-review` does not re-parse the
  analysis. Every draft ends with the hidden marker
  `<!-- sgai-prs: ai-cycle -->` used by future runs to count
  cycles.
- `post-review.prompt` — only fires in `--live` mode for
  **trusted** authors. Posts either a top-level comment (`gh pr
  comment`) or a `--comment` review (`gh pr review --comment`,
  state=COMMENT only — D12 forbids approve / request-changes /
  merge) with optional inline comments for line-specific findings
  (D9). Applies labels: `pr:ai-reviewed` always, plus
  `pr:has-blockers` (verdict=BLOCKERS) or `pr:scope-mismatch`
  (verdict=SCOPE-MISMATCH), plus `pr:needs-work` when
  `mergeable: false` and the verdict is not BLOCKERS /
  SCOPE-MISMATCH.

### Decisions encoded in the pipeline

| ID | Decision |
| --- | --- |
| D1 | Default mode is `--dry-run`. `--live` posts to GitHub. |
| D2 | Trusted authors (`TRUSTED_GH_USERS` in `.env.agent`, reused from Stage 5) get the full auto cycle. Outsiders' drafts are held with `pr:ai-needs-review` and surfaced to the project lead via Telegram for manual decision. |
| D3 | `severity:requirements` (and `severity:architectural` by extension) carry an explicit AI-disclaimer blockquote at the top of the review. |
| D4 | Language detection falls back to English when inconclusive. |
| D5 | Anti-loop cap of 3 AI cycles per PR. Enforced by `detect-prs`: when `cycle_count >= 4`, apply label `pr:ai-conversation-cap-hit` and drop the PR before triage. |
| D6 | The base standard is consulted only when the keyword detector trips (against PR body **and** diff text). |
| D7 | Trigger is manual today. Cron is future work. |
| D8 | Routing is conditional. `comment` (top-level) when verdict is `LGTM` with no line-specific findings or `SUGGESTIONS` with no line-specific findings. `review` (formal `gh pr review --comment`, state=COMMENT) when the review carries line-specific findings (hybrid: summary + inline), or when verdict is `BLOCKERS` / `SCOPE-MISMATCH` (registered as a review for visibility). |
| D9 | Inline vs generic comments are conditional on finding granularity. A `generic` finding lives in the summary body with a `path:line` text ref. A `line-specific` finding becomes an inline comment via the Pulls API (`event=COMMENT`) anchored to `path` + `line` on the `RIGHT` side of the diff. Hybrid is allowed: line-specific inline + summary body. |
| D11 | Four verdicts (`LGTM` / `SUGGESTIONS` / `BLOCKERS` / `SCOPE-MISMATCH`) **plus** a binary mergeable conclusion: **MERGEABLE** (`mergeable: true`) or **NEEDS-WORK** (`mergeable: false`). The verdict characterises what the review found; the mergeable conclusion characterises what the author should do next — they are orthogonal. Mergeable defaults to `true` when verdict ∈ {`LGTM`, `SUGGESTIONS`} AND no open points TBD identified AND no unverifiable load-bearing claims AND no broken cross-refs. Else `false`. Labels mapped: `pr:ai-reviewed` always; `pr:has-blockers` if `BLOCKERS`; `pr:scope-mismatch` if `SCOPE-MISMATCH`; `pr:needs-work` if `mergeable: false` AND verdict ∉ {`BLOCKERS`, `SCOPE-MISMATCH`} (the mergeable signal is additive only when neither verdict-driven label already conveys "not ready to merge"). |
| D12 | The AI MUST NEVER `gh pr review --approve`, `gh pr review --request-changes`, or `gh pr merge`. Approval and merge are exclusively human decisions. `post-review.prompt` enforces this as a hard guard — any draft / routing that requests those actions aborts the post and surfaces in the failed section of the summary. |
| D13 | Analysis walks four axes: (1) **Content validation** — claims vs `context/` + DASH 6th (the primary copy, if D6 trips). **Sub-step**: identify open points TBD declared by the author (TBD / TODO / FIXME / "open questions" / "deferred" markers in the PR body, in diffed `context/` files, in `.project/decisions/`, in `.project/PROJECT.md` threads; `[?]` placeholders; ADRs left in `Status: proposed`). Each open point becomes a finding with `axis=content`, `severity=info`, `granularity=generic`, and `blocks_merge: true` — flagged for the mergeable decision (D11) even when not a verdict-level blocker. (2) **Convention compliance** — naming, file placement, cross-refs vs `CLAUDE.md`; broken internal cross-refs introduced or modified by the PR are flagged with `blocks_merge: true`. (3) **Scope coherence** — PR body / title vs actual diff (scope creep detection). (4) **Downstream impact** — which artefacts go stale on merge given the dependency arrow `context/ → context-analysis/ → spec-source/ → output/ → output-analysis/`. |

### Scratch directory

Per-PR artefacts go to `.github-ai/output-prs/pr-<N>/` with a **meta +
per-cycle** layout:

```
.github-ai/output-prs/pr-<N>/
├── meta.md            ← regenerated every orchestrator run
├── cycle-1/
│   ├── triage.md      ← always written
│   ├── analyze.md     ← always written (the four axes)
│   └── review.md      ← the drafted review (carries machine-readable
│                         meta header; payload posted by post-review)
├── cycle-2/           ← created when the author pushed new commits or
│                         replied to the cycle-1 review
│   └── ...
└── cycle-3/           ← capped at 3 by D5 (anti-loop)
```

- `meta.md` — a snapshot of the PR at the moment of this
  orchestrator run: title, URL, author + trust, created / updated /
  state, draft flag, base / head refs, diff size, files touched
  (with per-file +/- and change type), current labels, full
  original body (blockquoted verbatim), and a comments timeline
  (issue-style comments + review summaries, merged
  chronologically). It is **always overwritten** on every run — no
  history. The cycle subfolders point back to it as the up-to-date
  context anchor.
- `cycle-<C>/` — one subfolder per AI cycle. Cycle 1 is the first
  time the AI processes the PR. A new cycle is started when
  `detect-prs` observes that the author has pushed new commits or
  replied to the most recent AI review (each posted AI review
  carries the marker `<!-- sgai-prs: ai-cycle -->` so the counter
  is unambiguous). Cycle 4+ is **blocked** by D5: `detect-prs`
  applies the `pr:ai-conversation-cap-hit` label and the PR never
  reaches the per-PR loop.

The whole directory is **gitignored** (see project `.gitignore`).
Posted reviews live on GitHub; the repo never commits them. The
`.gitkeep` is whitelisted so the empty directory survives
checkouts.

### Cycle counting (D5 enforcement)

`detect-prs.prompt` is the single source of truth for the cycle
index. For each open un-handled non-draft PR it runs:

```bash
gh pr view <N> --json comments,reviews \
  --jq '([.comments[]?,.reviews[]?] | map(select(.body | contains("<!-- sgai-prs: ai-cycle -->"))) | length)'
```

Let `ai_marker_count` be the returned integer. Then `cycle_count =
ai_marker_count + 1`. If `cycle_count >= 4` the PR hits the anti-
loop cap (D5): `detect-prs` applies `pr:ai-conversation-cap-hit`
(in `--live` mode) and excludes the PR from the orchestrator's
loop. Downstream prompts (`triage-pr`, `analyze-pr`,
`propose-review`, `post-review`) simply echo the cycle index
passed in by the orchestrator and use it to:

- pick the output path (`cycle-<C>/...`),
- adjust tone when `cycle_count > 1` (the review acknowledges the
  prior AI cycle and addresses the author's new commits or replies,
  without re-litigating findings that were already settled).

Inline review comments are NOT counted toward the cycle — only the
summary body of a `gh pr review --comment` (or a top-level `gh pr
comment`) carries the marker. See `detect-prs.prompt §"Inline
review comments are not counted"`.

### Reporting to the project lead

The Stage-6 orchestrator never sends Telegram messages directly.
At the end of each run it emits a fenced summary block to stdout
between `=== SGAI-PRS RUN SUMMARY ===` and `=== END SUMMARY ===`.
The parent agent (whichever session invoked the orchestrator)
relays that block to the project lead — with special attention to the
`needs-review` subsection (outsiders waiting on the project lead's call)
and to any verdict of `BLOCKERS` / `SCOPE-MISMATCH` (where the
author should likely revise before the maintainer merges).

### When NOT to invoke Stage 6

- During an active major build (`build-all`). The orchestrators
  run independently and never share state, but it is clearer to
  run them sequentially.
- When `context/` is being edited interactively. The analysis
  cross-checks claims against the current state of `context/`;
  running Stage 6 mid-edit produces a content-axis verdict against
  a half-edited baseline.
- When the operator has not reviewed the prior run's
  `pr:ai-needs-review` queue. Re-running before clearing the queue
  is fine — it just inflates the outsider backlog without
  The project lead's attention.

## Cross-reference conventions

- Inside `context/`: relative refs without prefix
  (`[02-actors.md](02-actors.md)` or `./02-actors.md`).
- From `context-analysis/`, `output/` or `output-analysis/` to
  `context/`: parent-relative (`../context/02-actors.md`).
- From `.project/` to `context/`: parent-relative
  (`../context/02-actors.md`).
- From `prompts/` to inputs: parent-relative (`../context/`,
  `../context-analysis/`, `../spec-source/`, `../output/`,
  `../output-analysis/`) —
  the prompt-runner is expected to execute from the project root,
  so paths inside the prompt body read naturally as
  `../context/...`.

## Grounding against the standard

The edition this project is written against, and the copy used to
verify claims about it, are declared in `context/00-normative-base.md`
and nowhere else. `bin/check-normative-base.py` confirms before every
build that the declaration still describes the file on disk.

**That copy is not in this repository and must not travel into it.**
Quote clauses, never pages.

**And the extraction carries personal data on every page.** Its headers
and footers repeat who obtained the document and under what order, so
that text sits *between* the sentences worth quoting, not somewhere a
reader would think to avoid. Copying a passage out of the extraction is
how it gets into a file here. None of it belongs in this repository:
an artefact recording which source it used names **the edition**, and
nothing about the copy. This has already happened once and was caught
before publication.

When a prompt needs authoritative content and the primary copy is not
at hand, **the step fails rather than proceeding on memory**. Step 0
of `build-all` already refuses to start a build without it, so a step
that runs has it; a prompt invoked outside the pipeline says so and
stops. Cite clause numbers **and quote the sentence**, and tag any
claim that could not be verified against the primary copy as
`[inferred]`.

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

Requirements follow the writing rule at the top of
`context/03-requirements.md` ("How requirements are written"); it is not
restated here.

Requirements are self-contained and concise. State what a requirement
mandates, not how it differs from other requirements. Do not compare
one requirement to another (no decorative "unlike R_x" / "R_y, by
contrast") unless the distinction is normatively necessary because an
implementer could otherwise conflate two constructs (for example two
different carriers), and then state it once, minimally. A reader should
be able to understand a requirement without holding the rest of the
requirement set in their head.

For artefacts that quote or extend the MPEG-DASH 6th edition (the
spec, the gap analysis), use RFC 2119 vocabulary
(MUST / SHOULD / MAY) when stating requirements. Reference the RFC
explicitly at the top of any document that uses these terms.

## Tone for future subagents reading this file

Pragmatism > exhaustiveness. If a section here does not save the
next subagent time, cut it. If a new pattern emerges across 2-3
tasks, capture it.

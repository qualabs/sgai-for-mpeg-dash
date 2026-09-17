# Pipeline defects: what is open, what is unverified, what only a run can tell

**Read-only inventory, 2026-09-17.** Nothing here is fixed by this
document. Every entry says where it is recorded, or says that it is
recorded nowhere, which is itself a finding.

**There is no pre-existing catalogue of pipeline defects.** The items
below were reassembled from `.project/LOG.md`, the v7.2 comparison
sidecar and the prompts themselves. `TASKS.md` for this phase has zero
open items. Anyone who remembered "a list of seven" was remembering the
v7.2 comparison's table of *spec* defects fixed by the refinement
(`output-analysis/v7.2-comparison.md`, §(d)), which is a different
thing.

---

## (a) Open defects — known, unfixed

### a1. The convergence verdict sums counts whose bases move

`compare-spec-versions.prompt` adds one number per category across two
iterations and calls the sum `Total issues`. When a *denominator*
changes between the two runs — a validator counting different objects,
an audit inventorying a different number of constructs — the delta
measures the change of instrument, not a change in the spec.

It is not hypothetical. `output-analysis/v7.2-comparison.md` §"Metric
caveats" (L146) decomposes v7.1→v7.2's `+4` and attributes **+3 to a
changed audit denominator** and **+2 to a reclassification between
independent validators**, i.e. more than the entire reported
regression. The `REGRESSION` verdict that run emitted is an artefact.

- **Recorded**: `output-analysis/v7.2-comparison.md` L146–L200, as a
  caveat about that iteration. **Not recorded anywhere as a defect of
  the step.**
- **State**: open in the general case. One instance is now guarded:
  `prompts/4-auto-refine/compare-spec-versions.prompt` L94–L96 warns
  about the requirement→criterion denominator change introduced today.
  Nothing warns about the audit's denominator, which is the one that
  actually fired.
- **Cost**: not evident. The honest fix is for each sidecar to report
  its denominator and for the comparison to refuse a delta across
  unequal ones — but whether the sidecars can report it reliably is
  unknown without running them.

### a2. `audit-dash-conformance.prompt` still grounds against NotebookLM

The audit prompt instructs the agent to query NotebookLM per construct
(L10, L64–L66, L98). Since 2026-09-15 the project's primary source is
the purchased PDF: `context/00-normative-base.md` declares it,
`bin/check-normative-base.py` gates the build on it, and the project
`CLAUDE.md` now states that the notebook is a derivative the PDF
outranks.

The prompt was never updated. The v7.2 audit went to the PDF anyway and
tagged itself `[GROUNDED_BY=iso-23009-1-2026-pdf]` — a value the prompt
does not define, since its enumeration is `notebooklm / spec-only /
fetch-failed` (L98). **The agent did the right thing and the prompt
still says the wrong one**, so the next run's correctness depends on
whoever runs it repeating that judgement.

- **Recorded**: nowhere. Found while compiling this inventory.
- **State**: open.
- **Cost**: evident and small — the prompt's grounding section and its
  `GROUNDED_BY` enumeration.

### a3. A blocked notebook degrades the build silently

Recorded in `.project/LOG.md` (the entry headed *"Still open, and it
decides whether the next build is worth running"*): a modal dialog
intercepts the submit click. The failure mode is the dangerous one —
**it does not fail**. Steps 1 and 8 degrade to `spec-only`, the build
completes, the conformance audit is performed blind, and the only
notice is one line in a file the project measured as unopened for three
and a half months.

- **Recorded**: `.project/LOG.md`, the "Still open" section.
- **State**: **unknown whether it still matters.** If a2 is fixed and
  the audit grounds against the PDF, the notebook leaves the critical
  path and this stops being a build risk. Those two entries should be
  decided together.
- **Cost**: not evident — it depends on a2.

### a4. `context/` states some obligations without a modal

17 of the 108 conformance criteria carry no RFC 2119 keyword. They are
not one kind: some are definitions, some are scope declarations, and
**some are obligations written in the indicative** — `R20.3`
("Overlapping windows … **are ordered** by presentation time"),
`R17.1` ("the Player **renders** the pause-ad form and **suspends** the
overlay"), `R18.1` ("The specification **documents** the MPD event URL
pattern").

This is the same defect the generated spec was just found to have, one
layer up, in the input that is supposed to be the source of truth.

- **Recorded**: nowhere before today. The rewritten validation step now
  reports them (`validate-spec.prompt` §4.2, verdict
  `source-has-no-modal`) rather than fixing them.
- **State**: open, and it is 17 separate judgements, not one edit.
- **Cost**: not evident — each one needs deciding, and three of the 17
  were written by this project within the last two days.

---

## (b) Fixed today, **not yet verified** — the risk is believing they are done

None of these has been through a build. Each was applied to an input and
its effect on the output is unobserved.

| Fix | Commit | What would show it worked |
|---|---|---|
| DP-2's example kept the modal, so it stops teaching indicative mood | `b803dd1` | the next spec carries MUST in its body, not 4 occurrences all of which are boilerplate |
| The validation step reports per obligation, with citations, and distinguishes `contradicted` / `force-lost` / `gap` | `b89238f` | the next `v<N>-spec-validation.md` has ~163 rows, and `UC-14` appears as `gap` |
| The background element hangs off the slot (`context/` was already right; the *generated* spec was wrong) | — | the next spec stops carrying `<svta:BackgroundElement>` as a `<svta:RenderableAsset>` child |
| Empty resolution falls through to the next window | `4a8d3ce` | the next spec's fall-through list includes the no-candidates case |
| `@noJump`, the decoder count, the glossary, `pause-fullscreen`/`pause-partial`, DR-9, DR-10 | `1396d24`, `4a8d3ce` | each has a specific passage to look for |

**The distinction that matters**: an open defect risks continuing to
break things. An unverified fix risks *being counted as done*. The
second is quieter.

---

## (c) Only a run can answer these

- **Whether fixing DP-2's example is enough.** The generator may be
  taking the indicative from elsewhere — most of `context/`'s prose
  outside the criteria is in the indicative. One example changed; the
  surrounding register did not.
- **Whether the rewritten validation step is affordable.** It now walks
  ~163 units instead of 33. The reading cost should be unchanged — the
  spec is read once either way — but no instrumented run exists, so
  this is a prediction.
- **Whether the generator obeys `context/` when `context/` is
  unambiguous.** The background element was stated correctly in
  `context/` twice, once as a MUST, and the build did the opposite. If
  it happens again, the defect is in `build-spec.prompt`, not in the
  input — and that is a different repair.
- **Whether the three existing spec heads are worth keeping.** v7, v7.1
  and v7.2 all predate every fix above.

---

## Found while compiling this, not previously reported

- **a2** — the audit prompt still names NotebookLM as its authority,
  and emits a `GROUNDED_BY` value it does not define.
- **The absence of a catalogue.** There was no list. Three of the four
  open items were recoverable only by reading a 1900-line `LOG.md`, a
  sidecar's caveat section, and the prompts. This file is the first
  place they sit together, and it will be stale the moment something is
  fixed without updating it — which is the failure mode it exists to
  document, so it should be the first thing checked, not trusted.

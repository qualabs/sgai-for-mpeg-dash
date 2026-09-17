# Proposal: verifying requirements against the generated spec

**Status: PROPOSAL — nothing implemented.** No prompt, script or
`context/` file is changed by this document.

## The finding that reframes the request

**The step already exists.** Step 7 of the pipeline
(`prompts/3-post-spec/validate-spec.prompt`, run as a fresh subagent)
already produces an *R coverage map* — one row per requirement, with a
status, the spec sections that satisfy it, and notes — and its findings
are already routed into buckets that drive Step 9's refinement loop. The
sidecar is already the input to the next iteration, which is what
*"que esa sea también la iteración"* asks for.

**And it reported the defect that prompted this request.** The
background-element contradiction appears in `v7.2-spec-validation.md`,
in R26's row, as the words *"R26.1 residual: the background is a child
of the option element rather than of the slot"*.

So the gap is not a missing step. It is that **the existing step reports
a contradiction in a form nothing acts on.** That is a narrower problem
and a cheaper one to fix.

## How the pipeline works today

The pipeline is **not a program**. It is a set of `.prompt` files under
`prompts/`, executed by an LLM agent. The entry point is:

```bash
CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 \
  claude -p "$(cat prompts/build-all.prompt)"
```

`prompts/build-all.prompt` is the orchestrator: it reads the other
prompts and dispatches them in order. `bin/` holds only the two
executable gates, which is why the pipeline is not there.

| Step | What runs | Produces |
|---|---|---|
| 0 | `bin/check-normative-base.py` | aborts if the declared edition no longer describes the copy of the standard on disk |
| 0.5 | `bin/check-context-coherence.py` | aborts if `context/` has dangling identifiers, duplicates or broken links |
| 1–5 | `prompts/1-pre-spec/*` | 5 artefacts in `context-analysis/` — gap analysis, UC coverage matrix, error semantics, conformance assertions, IAB catalogue |
| 6 | `prompts/2-build/build-spec.prompt` | `output/v<N>-sgai-spec.md` — the spec |
| 7 | `prompts/3-post-spec/validate-spec.prompt` (**fresh subagent**) | `output-analysis/v<N>-spec-validation.md` — gaps, edge cases, ambiguities, **the R coverage map**, and a disposition routing every finding |
| 7.5 | `review-spec-details.prompt` | `v<N>-detail-review.md` + in-place autofixes for deterministic corrections |
| 8 | `audit-dash-conformance.prompt` (**fresh subagent**) | `v<N>-dash-conformance-audit.md` — the spec against the base standard |
| 9 | `4-auto-refine/*` | loops refine → re-validate → compare, up to `MAX_REFINEMENTS`, emitting `v<N>.<M>` and a comparison with an `ON TRACK` / `STALLED` / `REGRESSION` verdict |

**Both gates run before anything is generated and both look only at
`context/`.** Nothing between Step 6 and Step 9 asks whether the
generated document says what `context/` told it to say — Step 7 asks
whether each requirement is *covered*, which is a different question.

## What is actually wrong with Step 7

Four things, in descending order of how much they cost:

1. **It has no verdict for "the spec says the opposite."** The status
   vocabulary is `full` / `partial` / `gap` / `governance`. A
   contradiction has nowhere to go, so it lands in `partial` — the same
   bucket as "the chapter does not carry all of it yet". Those two need
   opposite responses and get the same one.
2. **It runs at requirement granularity, not criterion.** There are
   **33** requirements and **108** conformance criteria. `MUST` lives at
   the criterion level; the map indexes at the level above it, so a
   violated criterion is reported in a note on its parent's row.
3. **It does not require a citation.** The column is *"spec sections
   that satisfy it"* — a list of section numbers, not quoted text. A
   row cannot be audited without re-reading the spec, so nobody does.
4. **Use cases are not checked against the generated spec at all.**
   Step 2 builds a UC coverage matrix, but it is *pre-spec* and derived
   from `context/`: it says what the cases demand, never whether the
   generated document contains them. There are **14** use cases and no
   step that looks for them in the output.

## The proposal

**Strengthen Step 7 rather than add a Step 8.5.** Four changes:

- **Index by criterion.** One row per `R<n>.<m>`, 108 rows, plus the
  governance requirements that have no criteria.
- **Add two verdicts** to the vocabulary: `contradicted` — the spec
  states something the criterion forbids, or forbids something it
  requires — and `absent`, distinct from `partial`.
- **Require evidence in both directions.** A `met` row carries a quoted
  passage and its location. A `contradicted` row carries **the passage
  that breaks it**, quoted, which is the half Nicolás asked for and the
  half that does not exist today.
- **Extend the same table to use cases**: one row per UC, verdict plus
  the quoted section of the generated spec that walks it.

**How it drives the iteration.** It already does; the change is what
gets routed. Today's disposition sends findings to three buckets that
Step 9 consumes. A `contradicted` row is unambiguous by construction —
the spec says X, the criterion says not-X — so it belongs in the
**Actionable TODO** bucket that `refine-spec` applies without a human.
A `partial` row stays where it is. That single re-routing is what turns
the document into the iteration instead of a report about it.

## Cost

**What is measured:**

| | |
|---|---|
| Requirements / criteria / use cases | 33 / 108 / 14 |
| Generated spec | 4 802 lines, 260 KB |
| `context/03-requirements.md` | 1 664 lines, 95 KB |
| What Step 7 emits today | 575 lines, 46 KB |

**What is not measured, and is therefore not estimated:** what a Step 7
run costs in tokens or wall-clock time. No instrumented run exists. A
number here would be invented, and this proposal is about a decision on
scope where an invented number is worse than a blank.

**On linearity** — the shape matters more than the number. A pass that
re-reads the spec once per criterion is 108 × 260 KB and is not worth
proposing. The pass that is worth proposing reads the spec **once** and
emits 108 verdicts from it, so the cost is dominated by reading the two
documents (355 KB, on the order of 90 000 tokens by the usual
four-characters-per-token conversion — a conversion, not a measurement)
and grows with the *spec*, not with the criterion count. Going from 33
rows to 108 rows changes the output, not the input.

## What this does not solve

**The verifier shares the reader with the builder.** Both are the same
kind of model reading the same `context/`. If a sentence admits two
readings, the builder picks one and the verifier can pick the same one
and see no conflict. Step 7 already mitigates this by running as a
**fresh subagent** with no context overlap — that is real and it is why
the background defect was caught at all — but a fresh context is not a
different reader.

**What actually helps is changing the question, not the reader.**
*"Is this requirement covered?"* invites agreement; *"quote the passage
that satisfies it, and if none does, quote the one that breaks it"*
forces contact with the text. That is the mechanism behind the
citation requirement above, and it is the only part of this proposal
with evidence behind it — the same move is what surfaced three false
findings in `context/` this week.

**It cannot see an error in `context/` itself.** The check compares the
spec against `context/`, so anything wrong *in* `context/` verifies as
correct. This is not hypothetical: the `@noJump` and the decoder-count
errors were both consistent all the way down, and every layer agreed
with the layer below it. Only a check against the base standard found
them, and that is Step 8's job, not this one's.

**A green here means the identifiers and the quotations line up.** It
does not mean the specification is right.

## The cheaper alternative

**Verify only what is forbidden.** `context/03-requirements.md` carries
**36** `MUST NOT` lines. A pass restricted to those asks one question —
*does the generated spec do this?* — against a third of the criteria and
with no judgement about coverage or completeness.

It would have caught the case that prompted this request: R26.1 says
the background element *"MUST be carried as a composition attribute of
the slot / layout, **not** as a separate presentation option"*, and the
generated spec carries it as a child of the option element. A
prohibition and its violation, both quoted, with nothing to weigh.

**What it gives up** is everything the full pass adds: it says nothing
about whether a requirement is covered, nothing about use cases, and
nothing about the requirements that only require. It is not a smaller
version of the full check — it is a different, narrower one.

**What it costs** is the same input read once against 36 rows instead
of 108. The saving is in the output and the judgement, not in the
reading.

## A third option this proposal did not expect: mechanical traceability

A purely mechanical check was dismissed while drafting this, on the
assumption that the generated spec already carries the criterion
identifiers so a traceability grep would pass trivially. **Measured,
the assumption is false**: of the 108 criteria in
`context/03-requirements.md`, **103 do not appear anywhere in
`output/v7.2-sgai-spec.md`**.

That is not a defect. The generated spec is a standards-style document
written for the working group, and a document of that kind does not
carry another project's bookkeeping identifiers. It expresses the
requirement; it does not cite it.

But it means a **third option exists** and it is the cheapest of the
three: **require the generated spec to carry a marker per criterion**,
in the way it already carries `<!-- refine: ... -->` comments for
audited edits. Then traceability is a `grep` — zero judgement, zero
tokens, and a missing criterion is found by a script rather than by a
reader.

**What it costs is the document.** Markers are internal bookkeeping
placed in a text meant for outside readers, and they are invisible
only until someone views the source. It also proves the weakest thing
of the three: that each criterion was *mentioned*, not that it was
honoured. It would not have caught the case that prompted this
request — a marker on R26.1 would sit happily beside a passage
contradicting it.

**So the three options answer different questions**: markers answer
*was every criterion addressed*, the `MUST NOT` pass answers *is
anything forbidden being done*, and the full per-criterion pass answers
*is each one honoured, with the evidence*. Only the second would have
caught the background element, and only the third would have caught it
along with the reason.

**And the contradiction itself is not mechanically detectable by any of
them.** It is between *slot* and *option* — two words both present in
the spec and both correct elsewhere in it. Nothing mechanical separates
the correct use from the wrong one.

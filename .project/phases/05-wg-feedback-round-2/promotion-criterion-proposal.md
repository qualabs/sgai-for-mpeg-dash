# What has to be true before a candidate becomes the published build

A proposal, not an implementation. Nothing in `context/`, `prompts/` or
`bin/` is touched by this document.

It assumes the build model settled in the same phase — `output/` holds
candidates, `dist/` holds the published build, and a candidate arrives
in `dist/` by promotion — and does not revisit it.

## What the criterion is, in one sentence

A candidate is promotable when **nothing in it is contradicted**, and
everything else that is open is **visible to whoever opens the published
build**.

Two properties, and the second is the one that makes the first
achievable. A specification with open questions is publishable; a
specification that hides them is not. That is the same distinction
ADR 0008 drew when it refused to omit `@noJump` silently: *"a construct
absent from a specification says nothing about whether anyone considered
it."*

**There is no score.** No count is compared against a threshold and no
count is compared against the previous build. The exhaustive walk the
validation step now performs makes the estimate unnecessary — what is
unmet can be read off, one unit at a time, so there is nothing to
approximate. A number was also the thing that could lie: the
`REGRESSION` verdict of v7.1 → v7.2 was an artefact, +3 of its +4
attributable to a changed audit denominator.

One count survives, and it is not a metric: **units walked against units
that exist** (§3). It does not say whether the spec improved. It says
whether the step looked. Those are different questions and only the
second can be answered by counting.

## 1. What blocks, verdict by verdict

Two tiers. **Blocking** means the published document would be wrong or
unverified. **Open** means it would be incomplete — publishable, on one
condition stated after the table.

| Source | Verdict | Blocks | Why |
|---|---|---|---|
| coverage map | `contradicted` | **yes** | The document says something a criterion forbids. Publishing it publishes the contradiction. |
| coverage map | `gap` | **yes** | An obligation `context/` states and the spec does not address. The published spec does not do what the project says it does. |
| coverage map | `force-lost` | **yes** | The substance arrived and the obligation did not. An implementer reading a description where a MUST belongs is not bound by it — the spec fails at the one thing a spec does. |
| coverage map | `partial` | no | Part of an obligation is stated. Incomplete, not wrong. |
| coverage map | `met` | no | — |
| coverage map | `governance` | no | The criterion constrains how the document is written; no passage can satisfy or break it. |
| coverage map (question 2) | `source-has-no-modal` | no | A defect in `context/`, not in the candidate. It does not block publishing a spec that faithfully reflects `context/` — it degrades trust in every `met` on those 17 units, which is a caveat, not a gate. |
| detail review | `Flagged` | no | The step declined to autofix because the edit is not mechanical. All five v7.2 flags carry an explicit recommendation; they are work, not wrongness. |
| detail review | `Autofixes applied` | no | Already fixed. |
| DASH audit | `Non-conforming` | **yes** | A contradiction with the base standard. The one class of defect whose cost is borne outside this project. |
| DASH audit | `Marginal` | no | Mixed by construction — of v7.2's seven, three were "align and be done", three were open questions, one was a wording fix. The verdict does not carry which. |
| DASH audit | `[fetch-failed]` | **yes** | The audit could not locate the item in the primary copy. Publishing it publishes an unverified conformance claim as a verified one, which is worse than publishing a known gap. |

### The condition that makes the second tier safe

An open item must be **visible to whoever opens the published build**.
It already is: `dist/` holds the three sidecars next to the spec, so
every `partial`, every `Flagged`, every `Marginal` travels with the
document it qualifies. No new artefact is needed, and this is the
argument for why `dist/` carries the sidecars rather than the spec
alone.

The rule has a consequence worth stating: **a promotion that ships the
spec without its sidecars is not a promotion under this criterion.**

### Your reading, against the real cases

**`contradicted` blocks always — confirmed.** Nothing in the v7.2
classification argues otherwise, and the two 1b-contradicts items that
survived reclassification (R3.2, the hybrid type on a single-decoder
device with two opposite answers; R21, a surface §4.6.9 authorises that
its own tables make unreachable) are exactly what a reader would hit.

**Including when the contradiction is Nicolás's decision — confirmed,
and it is the stronger half.** A block that lifts itself is not a block.
The point of making it visible is the escalation, and there is no
mechanism here that can resolve A-1, A-2 or A-3 without him.

One correction to the framing. 1a is not the same shape as 1b: NC2 and
M4 are contradictions **with the standard**, and they arrive as
`Non-conforming` in the audit, not as `contradicted` in the coverage
map. Both block, by different rows of the table. What this requires is
that the gate **deduplicate across sidecars before reporting** — `G-6 =
M3`, `G-7 = M1`, `G-8 = detail flag 1` in v7.2 — or the same item is
listed three times and the short list stops being short.

**1b [silent] does not block — confirmed, with one condition that does
not hold today.** *"Está declarado, no roto"* is right about declared
silence. But none of the sixteen is declared anywhere a reader of the
spec would find it. `G-1` (no timebase or rounding rule for cap
arithmetic) is silent in the sense that nobody wrote anything — a reader
cannot tell it from an oversight, which is the exact failure ADR 0008
refused.

So: **a deliberately-open item needs a place to be declared, and there
is no verdict for it.** Today it surfaces as a `gap` or as an
Ambiguity, and under the table above a `gap` blocks. Either the gate
blocks on things Nicolás has already decided to leave open, or it stops
blocking on `gap` and loses the verdict that catches real omissions.

The way out is not a new verdict. It is that **declared-open is a fact
about `context/`, not a judgement about the candidate**: an
Out-of-Scope item or an accepted ADR says the question is deliberately
left open. The gate reads that from `context/` — where it is auditable
and stable — and downgrades the matching unit from blocking to open.
A model is not asked to decide what was deliberate.

This is the one thing the criterion needs that does not exist yet, and
it is an edit to `context/`, not to a prompt.

**`gap` blocks — confirmed, with no real case to check it against.**
v7.2's coverage map has zero `gap` rows (17 `full`, 10 `partial`, 3
`governance`), so the verdict is untested at the map level. The real
evidence is `G-5` in the Gaps section — the Positioning Templates
section R10.3 requires does not exist — which is what a `gap` row will
look like, and which should stop a publication. UC-14 is the designed
case: the validation step's own acceptance test expects it as `gap`.

**`partial` probably does not block — refuted for v7.2, confirmed
going forward, and the difference matters.** Against the real cases,
**none of v7.2's ten partials was a partial.** They were 1b
contradictions (R3, R21, R26, R12, R1/NC2), duplicates of findings
already counted (R4, R7, R19), a terminology defect (R14), and one
already resolved (R28). Read literally, "ten partials do not block"
would have waved through three self-contradictions.

That was a property of the **old map**, which indexed by requirement:
`partial` on `R3` was a container holding "R3.1 and R3.3 met, R3.2 has
two opposite answers", and the contradiction lived inside a cell. The
per-criterion map removes the container — R3.2 gets its own row and its
own `contradicted`. So `partial` becomes what its definition says.

**This is a prediction, not a measurement.** No sidecar produced by the
rewritten map exists yet. The first run is where it is checked, and the
check is specific: read the `partial` rows and confirm each is a partial
rather than a contradiction wearing a softer word.

## 2. Where the who-resolves classification comes from

**It already exists, and no new step is needed.** §5 of
`validate-spec.prompt` routes every finding into `5.a` (the fix is
unambiguous and inside the spec — refine-spec applies it), `5.b` (the
remedy is not unique — it waits for the owner), `5.c` (it requires
editing `context/`). That is who resolves it, in different words:

| Disposition | Who closes it |
|---|---|
| `5.a` | the pipeline — nobody has to decide anything |
| `5.b` | Nicolás |
| `5.c` | Nicolás, then a major build |

**What is missing is coverage, not vocabulary.** §5 routes Gaps, Edge
cases and Ambiguities. It does **not** route the coverage-map rows, and
nothing routes the audit's items or the detail flags. The manual
classification in `v7.2-findings-classified.md` had to be done by hand
precisely because those three populations arrive unrouted.

**The change: make the disposition mandatory for every non-`met`
coverage row, every `Non-conforming` / `Marginal` audit item, and every
detail flag.** One column, in the step that already defines the
vocabulary. That is the cheapest correct answer — cheaper than a new
step, and cheaper than re-deriving the routing later from prose.

It also pays for itself immediately on the mixed verdicts. `Marginal`
does not block by itself, but a `Marginal` whose disposition is `5.a`
is a defect with a known correct fix that nobody applied — and *that*
blocks. The disposition decides where the verdict cannot.

**Two values, not four categories.** The 1a/1b/2/3 split of
`v7.2-findings-classified.md` was written to explain *why* the process
stalls, and it distinguishes a standards decision from a product one.
The gate needs neither distinction: both say "Nicolás". Reproducing
four categories to use two of them would be work with no consumer.

## 3. Who evaluates it

**A script.** `bin/check-promotable.py`, a sibling of the two checks
already in `bin/`, reading the candidate's three sidecars in
`output-analysis/`.

It is deterministic because the inputs are tables with a fixed column:
count the rows carrying a blocking verdict, subtract the ones a
`context/` declaration marks deliberately open, print what is left. No
reading comprehension is required to do that, and a criterion that
depends on someone reading carefully is the failure mode being removed
from this repo.

**Three exits, not two.**

| Exit | Meaning |
|---|---|
| `0` | Nothing blocks. Promotable. |
| `1` | Blocked, with the list. |
| `2` | Cannot tell — a sidecar is missing, unparseable, or the arithmetic below does not close. |

The third is the one that matters. "Cannot tell" must never be
reachable from the same code path as "nothing blocks": **zero blocking
rows is also what a walk that never happened looks like.**

**The arithmetic that makes exit 0 mean something.** The script derives
the expected population from `context/` the same way the validation step
does — every `R<n>.<m>` bullet, every RFC 2119 keyword outside a
criterion bullet, every `UC-<n>` — and compares the total against the
rows in the coverage map. A mismatch is exit 2, naming the missing
units. This is the load-bearing part of the whole design: without it
the gate certifies a truncated walk as a clean build, and with it a
truncated walk cannot pass as anything.

**What stays a judgement**: producing the verdicts. That is §5.

## 4. What it prints when it is blocked

Not "not promotable". The useful output is **the short list of what
blocks it and who lifts it**, grouped by who — because the two groups
are acted on by different people on different days.

```
BLOQUEADO — 5 items

Necesita a Nicolás (3)
  A-2   contradicted   @earliestResolutionTimeOffset: obligacion del Publisher
                       o atributo opcional. §4.3.5 contra R2.1/R4.1.
  R3.2  contradicted   tipo hibrido en device de un solo decoder: dos
                       respuestas opuestas. §7.5.4 y Annex D.5 contra §8.4.
  NC2   non-conforming vaciar una oportunidad: §4.6.8 angosta una condicion
                       de §5.16.2.2.6. Decision de estandar.

Lo destraba el pipeline (2)
  UC-14 gap            el spec no recorre el caso. refine-spec / build.
  G-5   gap            falta la seccion de Positioning Templates que R10.3
                       exige. refine-spec.

Abierto y NO bloquea (14) — viaja publicado en los sidecars
  10 partial · 3 flagged · 1 marginal
  (detalle en output-analysis/v<N>-spec-validation.md)

No certificado por esta promocion
  17 criterios sin modal en context/: la fuerza no se pudo verificar.
```

Four properties of that block, each there for a reason:

- **Grouped by who, not by severity.** Severity orders a list nobody
  can act on; "who" is what makes it two work queues.
- **One line per item, with the location.** The detail is already in
  the sidecar and does not need repeating.
- **The open items are counted, not listed.** They do not block, and
  printing fourteen lines nobody has to act on is how the five that
  matter get skimmed past.
- **The last section is what the promotion is *not* saying.** A gate
  that only reports what it checked reads as if it checked everything.

**It prints when nothing blocks, too** — the same block, with an empty
first two groups. "Promotable, and here is what is open anyway" is the
sentence a promotion decision needs; a bare green is not.

Run today against what is in `dist/`, this criterion says **the
published build does not meet it** — v7.2 carries two `Non-conforming`
items and at least three self-contradictions. That is not an argument
against the criterion. It is the first evidence that it is not vacuous,
and it is the honest description of a build that was promoted because
the restructure had to start from something.

## 5. What it does not solve

**The verdicts are a model's, and the gate is exactly as good as they
are.** A criterion marked `met` with a quotation that does not actually
state the obligation is indistinguishable, in the table, from one that
does. The quotation requirement raises the cost of a wrong `met` — the
model has to produce a passage — but the model also chooses the passage.
This failure is silent, it is the most likely one, and nothing in this
design catches it. What would catch it is a second pass that re-reads a
sample of `met` rows against the spec, and that is a different proposal.

**The gate measures the map, not the specification.** Everything above
is computed from three documents *about* the candidate. If a unit never
got a row, it cannot block. The population arithmetic of §3 is the only
defence and it is a good one, but it verifies that rows exist — not that
any row was reached by reading the spec.

**Nothing here validates `context/`.** Every verdict answers "does the
output say what `context/` says". A criterion whose text is itself wrong
produces a clean `met` and a defective published spec. NC2 and M4 are
that class: the standard says one thing, `context/` says another, and
the only step that looks outward is the DASH audit. That is the reason
`Non-conforming` and `[fetch-failed]` block despite being the verdicts
most expensive to clear — they are the project's only contact with an
authority that did not come from inside it.

**`met` on a document-level criterion is the weakest row in the
table.** Twenty-nine criteria constrain how the document is written
("the spec uses RFC 2119 consistently"), and no quoted passage can
demonstrate a property of a whole document — the evidence is necessarily
a sample. A script counting rows counts these beside the runtime ones,
and they are not the same kind of claim. They are not excluded here,
because excluding them would quietly shrink the population the
arithmetic checks; they are named so that a clean run is not read as
proving something it cannot prove.

**And the boring one that will actually happen first**: the sidecars are
markdown written by a model, and a table whose columns drift breaks the
parser. That surfaces as exit 2, which is the correct behaviour and will
still be experienced as the gate being broken. It is worth deciding in
advance that exit 2 is never worked around by hand.

## What this proposal does not decide

- **The format of the declared-open record in `context/`.** §1 says it
  is needed and says where it lives; which construct carries it is a
  `context/` design question.
- **Whether promotion is automated once the gate is green.** The gate
  answers "may it be promoted", never "promote it". Nothing here moves a
  file.
- **What happens to a candidate that is blocked forever.** Two of v7.2's
  blockers are standards decisions that may not resolve for months. A
  policy for publishing with a declared, blocking divergence is a
  decision for Nicolás and is deliberately absent rather than guessed.

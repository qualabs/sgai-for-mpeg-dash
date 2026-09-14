# Tasks — phase 05-wg-feedback-round-2

| id   | brief                                                                                          | status  | plan | evidence |
| ---- | ---------------------------------------------------------------------------------------------- | ------- | ---- | -------- |
| T-01 | Compare `context/` against the WG agreements extract and **emit one task per proposed change**  | pending | —    | —        |
| T-02 | Settle the eleven unresolved transcript readings (§4) with David, starting with the deadline    | pending | —    | —        |
| T-03 | **Verify the four claimed spec contradictions against the primary sources** (gates T-01)        | done    | —    | [`tasks/T-03/verdicts.md`](tasks/T-03/verdicts.md) — A2 `spec-does-not-express-its-intent` (drafting), A6 `contradiction` (lands on UC-04, not R22), A7 `contradiction`, A8 `compatible` (an addition); corrections written back into the extract |
| T-04 | **Make R5's flexibility explicit in `context/`** — drafting, not design                          | done    | —    | `context/03-requirements.md` R5 gist + prose + core-invariant row; `context/02-actors.md` APS section; `context/99-glossary.md` two entries. The R18 scope question resolved via R18.2 + R29 |
| T-05 | **State that an APS may return exactly one option** — new requirement and/or use case             | partly landed | —    | The explicit statement is in `context/03-requirements.md` R5 and `context/02-actors.md`; only the paired use case remains |

`T-06` onward do **not** exist yet by design: they are the **output of
T-01**. T-01 is a task that generates tasks. Until it runs, this phase
has a backlog of five.

**Execution order is not numbering order.** `T-03` is numbered after
`T-01` — the repo convention is sequential ids with no renumbering of
what already exists — but it runs **before** T-01 emits anything, because
it tests the premise T-01 is built on. If T-03 finds that A2 does not
contradict R5, a large part of T-01's output changes shape or disappears.
The dependency is stated in both tasks.

`T-04` and `T-05` are **not** in that chain: both stand on their own
(see their blocks for why) and can run at any time, including first.
They divide one problem — **T-04 clarifies what is already written,
T-05 states what is not written yet** — and each block carries the
boundary so they do not overlap.

---

## T-01 — Compare `context/` against the WG agreements extract and emit one task per proposed change

- **Objective:** turn the 2026-08-19 SVTA Ads WG call into a decidable
  backlog. Establish, for every item the WG agreed or proposed, whether
  the committed spec already says it, contradicts it, or is silent on
  it — and emit **one task per proposed change or addition**, so the
  changes can be decided one at a time between Nicolás and the agent
  rather than as a single undifferentiated document.

- **What it must cover:**

  **What is compared against what.** The three source-of-truth spec
  files — `context/02-actors.md`, `context/03-requirements.md`,
  `context/04-use-cases.md` — against the items in
  [`svta-wg-2026-08-19-agreements.md`](svta-wg-2026-08-19-agreements.md):
  the agreements A1–A15 and the open proposals O1–O7. Items in §3
  (mentioned without conclusion) are **not** compared — they carry no
  action by construction. Where an item plainly lands outside those
  three files, name the file it does touch
  (`06-naming-and-namespaces.md` for the namespace and vocabulary
  items, `07-backward-compat-checklist.md`,
  `08-dash-extension-rules.md`, `99-glossary.md`,
  `05-dash-linear-interfaces.md` for the empty-break response) — but do
  not go looking for work there beyond what an item requires.

  **Start here**, in this order: the agreements extract in this folder;
  then `PHASE.md` in this folder for the framing and the two known
  conflicts; then the three `context/` files. Read
  `.project/phases/02-wg-feedback-round-1/hassoun-feedback-crossref.md`
  for the form a comparison took in round 1 — but note the deliverable
  is different this time (tasks, not a report). Check
  `.project/decisions/` for ADRs an item may collide with: `0001`
  (spatial caps deferred to IAB CTV) is load-bearing for the layout and
  vocabulary items, and `0002` / `0003` are `proposed`, so an item may
  reach into a phase that has not executed. Read the design principles
  at the top of `03-requirements.md` (DP-1, DP-1.1, DP-1.2, DP-2, DP-3)
  before proposing any new construct — DP-1.1 in particular rejects
  speculative constructs, and DP-3 already carries the skip-as-last-
  resort principle that O2 builds on.

  **The output is one task per proposed change — not a document with a
  list.** This is the point of the task and the reason it exists.
  Nicolás and the agent will iterate the changes **one at a time**, and
  that requires each change to carry its own status, its own thread and
  its own close. A report listing nineteen items has one status for
  nineteen decisions and is therefore useless for the purpose. Concretely:
  append rows to the table in this file, one per change, each with its
  own detailed block below, following the TASKS.md schema of the
  `create-project` skill. A summary artefact **may** be saved as T-01's
  evidence in `tasks/T-01/` to record the comparison itself — the
  already-covered and no-op findings have to land somewhere — but it is
  a by-product. If the tasks were not created, the task is not done.

  **What each generated task must carry**, at minimum, so it can be
  discussed with no other document open:
  - **What is proposed** — stated in one or two sentences, in the WG's
    own terms, with the verbatim quote when the wording is load-bearing.
  - **Who proposed it** — the person, and whether anyone objected or
    argued the other way. In a working group the provenance of a
    proposal is part of its weight: an item closed on silence is not the
    same as one where an alternative was argued and not adopted.
  - **Which `context/` file(s) it touches**, and which requirement, use
    case or actor section specifically (R-number, UC-number, actor
    heading).
  - **What has to be decided** — the actual question for Nicolás, posed
    so it can be answered. Not "review R5", but the choice and its
    consequence.
  - **Its classification**, carried over from the extract: agreed at the
    WG (A-item) or still open (O-item). The two are not the same kind of
    task — an A-item asks whether we accept what the WG agreed; an
    O-item asks what we want to propose back.

  **Classify before emitting.** Not every item is a change. Sort each
  one as: **already covered** by the committed spec (no task — record it
  in the evidence artefact with the construct that covers it);
  **contradicts** the committed spec (task, and the task must enumerate
  every dependent construct before proposing an edit); **absent** from
  the spec (task, an addition); or **explicitly out of scope** (task,
  but a small one — an out-of-scope statement, not a feature). Mark each
  generated task's weight so the trivial ones can be grouped into a
  single pass instead of being iterated one by one. Mark each one
  **design** (what the spec permits or requires changes) or **drafting**
  (what the spec permits stays, its wording changes) — the two need
  different decisions from Nicolás, and conflating them is what T-04
  exists to undo.

  **Two items are structural in the form they were reported** and must
  be handled as such, not as ordinary rows. The reported form is below,
  followed by **T-03's verdict on all four claims, which is the framing
  to work from**. **A2** (device
  capability travels up to the ADS, which returns a single presentation)
  is *reported* as contradicting R5 and everything built on it: R5.1–R5.7, the APS's "produce candidates with renderable
  presentation options" responsibility in `02-actors.md`, the
  ordered-fallback decision recorded in `LOG.md` for 2026-05-27, and the
  whole of UC-09 — which exists solely to demonstrate the model A2
  contradicts. It reaches phase `03-custom-layout`, which leans on the
  R5 ordered fallback; it does **not** reach `04-multiview`, which
  carries no reference to R5 and rests on the R3 / R22 decoder-budget
  reasoning — that phase is reached by A6, not by A2 (measured against
  both phases' own files in
  [`tasks/T-03/verdicts.md`](tasks/T-03/verdicts.md)). Where the
  verdict below confirms a contradiction, that item's task must
  enumerate the full dependency set before proposing an edit and be
  marked as blocking every dependent task. **A7** (pausing during an ad
  break does not raise a pause ad) points against R17's pause-ad
  priority and touches R16, R21, R25, UC-05 and UC-08; the same
  treatment applies at smaller scale.

  **T-03's verdict — the framing to work from**
  ([`tasks/T-03/verdicts.md`](tasks/T-03/verdicts.md)):

  - **A2 is drafting, not structure.** Every normative clause of R5
    already permits the arrangement A2 describes; what fails is the
    wording, at four sites. Nothing normative moves, so **neither
    `03-custom-layout` nor `04-multiview` is blocked by it**, and the
    items in this family collapse into T-04 and T-05 rather than
    becoming design tasks of their own.
  - **A6 contradicts, and it lands on UC-04** — not on R22, which is
    narrower than the WG rule but consistent with it. Adopting A6
    retires a use case.
  - **A7 contradicts**, and UC-08 is that exact state resolved the
    other way. R21 is only re-referenced; R16, R25 and UC-05 are not
    reached.
  - **A8 is compatible** — an absence, so an addition rather than a
    change, and a MUST-support rather than a MAY.

  **The scope of this task does not change.** It still emits one task
  per proposed change or addition, over the same item set. What the
  verdict changes is which bucket A2's items land in — drafting rather
  than structure — not how many items there are.

  **Constraints.** Do **not** edit anything in `context/` — this phase
  plans the spec change and does not make it; every edit is a later
  task with its own decision. Do **not** resolve the eleven readings in
  §4 of the extract by inference: where an item depends on one of them,
  the generated task says so and points at T-02. Do **not** collapse
  the agreed/open distinction — the two produce different questions.
  Do **not** silently drop an item because it looks already covered:
  every A- and O-item must appear in the output either as a task or as
  a recorded already-covered finding, so the extract can be walked
  end-to-end against the result. Preserve the numbering of the extract
  (A1..A15, O1..O7) in every generated task so the audit trail back to
  the transcript survives.

  **Depends on T-03.** T-03 verifies, against the primary sources,
  whether the four contradictions this task's inputs assert are real. Do
  **not** emit any task deriving from **A2, A6, A7 or A8** before T-03
  has returned a verdict on that pair, and prefer to wait for T-03
  entirely — its A2 verdict is the premise most of this task's output
  rests on. Where T-03's verdict is `indeterminate`, the task this
  produces is a **question for the WG**, not a spec change (see T-03's
  definition of done). T-02 runs in parallel and informs some of the
  generated tasks; it does not gate this one.

  **Check T-04's outcome before emitting.** T-04 makes R5's designed
  flexibility explicit in `context/`. If it has landed, **any candidate
  whose supposed conflict was really "the spec does not say it permits
  this" is already resolved there** and must not be emitted again as a
  design change; say which candidates T-04 absorbed. If it has not landed
  yet, mark those candidates as belonging to that family rather than
  inventing a parallel fix. **The same applies to T-05**, which states
  outright that an APS may return a single option: it is a second route
  by which candidates in that family dissolve, and anything it covers
  must not be re-emitted here either.

- **Definition of done:** every A- and O-item in the extract is
  accounted for exactly once — either as a new row in this file's table
  with its detailed block below, or as an already-covered / no-op
  finding recorded in `tasks/T-01/`. Walking the extract from A1 to O7
  hits an accounted-for item every time, with none left over.
  No task deriving from A2, A6, A7 or A8 was emitted before T-03
  returned a verdict on that pair. A2 and A7 each have a task that lists
  their full dependency set and is marked as blocking — unless T-03
  found the pair compatible, in which case the finding is recorded and
  no change task is emitted. Every generated task states its proposal, its
  proposer, the `context/` file and construct it touches, the decision
  it asks for, and its A/O classification. `context/` is byte-identical
  to how T-01 found it.

## T-02 — Settle the eleven unresolved transcript readings (§4) with David

- **Objective:** remove the ambiguity the automatic transcript
  introduced, so the generated tasks are decided against what was
  actually said rather than against a plausible reading of it. The
  deadline comes first: it sets the pace of everything else in the
  phase.

- **What it must cover:** the eleven items in §4 of
  [`svta-wg-2026-08-19-agreements.md`](svta-wg-2026-08-19-agreements.md).
  They are not equally urgent — three of them change what we build:
  §4.1 (the deadline, "buy the RENS meeting" — most likely the Rennes
  MPEG meeting, but the date is what matters), §4.7 (whether
  `concurrent-static` is a presentation element or only a placement-type
  token), §4.8 (whether the placement-type list is ordered and whether
  order expresses preference), §4.9 (where in the MPD the declaration
  lives — David breaks off mid-sentence asking whether it is on a
  Period) and §4.10 (whether the one-experience-at-a-time rule binds
  only what this spec controls, which materially bounds A6). The rest
  are names and references (§4.2–§4.6, §4.11) and can be settled in
  passing. Start from the extract; each item already carries the
  verbatim quote to put in front of David. Constraint: ask, do not
  infer — an inferred answer recorded as settled is worse than an open
  question. Venue: the WG Slack channel or the next call, whichever
  comes first; David asked for comments on his document [56:09], which
  is a third option for the substantive five.

- **Definition of done:** each of the eleven items is either answered,
  with the answer written into the extract in place of the open
  reading, or explicitly marked as not worth chasing. The deadline
  (§4.1) is a date, or a stated "David does not have one yet".

## T-03 — Verify the four claimed spec contradictions against the primary sources

- **Objective:** establish whether the four contradictions asserted in
  the agreements extract are real. The extract claims that **A2**
  contradicts R5, **A7** points against R17, **A8** is absent from the
  spec, and **A6** is broader than R22. Those claims travelled through
  two layers of interpretation — an automatic transcript, then a
  reading of it — and the reading is what is in doubt. This task tests
  the claims against what the transcript and the spec **literally say**,
  and returns a verdict per pair. Overturning a claim is as valuable a
  result as confirming it: it is what stops T-01 from generating tasks
  for changes the spec may not need.

- **What it must cover:**

  **Verify against the primary sources. The extract is the artifact
  under test.** Re-reading
  [`svta-wg-2026-08-19-agreements.md`](svta-wg-2026-08-19-agreements.md)
  proves nothing — it is the claim, not the evidence. Use it only as an
  index to find which quotes and which requirements a pair involves,
  then go to the sources themselves:

  - **The transcript.** Google Doc
    `1E_B_53VRaBm8TwJYKTouFxZvSq2MabkO-1l0NIiIdPA` ("Advertising WG
    Call", 19 Aug 2026), the only record of the call. Export it with
    `gws drive files export --params '{"fileId":"1E_B_53VRaBm8TwJYKTouFxZvSq2MabkO-1l0NIiIdPA","mimeType":"text/markdown"}' -o <file>`
    (the `-o` path must be inside the working directory — `cd` to a temp
    dir under `/dev/shm/` first). Read every supporting quote **in its
    surrounding turns**, not as an isolated line: who asked what
    immediately before, what was said immediately after, whether anyone
    objected. **If a quote's meaning depends on a sentence that breaks
    off mid-way, that is itself the finding** — it makes the pair
    `indeterminate`, not a contradiction.
  - **The literal spec text**, not a paraphrase of it: R5 with
    R5.1–R5.7, R17 with R17.1–R17.4, R22 with R22.1, and R16 / R21 /
    R25 in `context/03-requirements.md`; the design principles DP-1
    through DP-3 at the top of the same file; the **Ad Presentation
    Server** section of `context/02-actors.md` (specifically "Produce
    candidates with renderable presentation options") and its Boundary
    Summary; **UC-09** in `context/04-use-cases.md`, plus UC-05 and
    UC-08 for the A7 pair.
  - **Nicolás's written comment on the WG doc**, reproduced verbatim in
    the extract's A2. This is the single most important input to the A2
    pair, because **it argues the opposite of the arrangement recorded as
    A2**: it defends letting the device choose at
    spec level and calls "the APS sends one option" an *implementation*
    decision. Two of its three bullets bear directly on the hypotheses
    below — *"the URL to the APS is not under this spec"* and
    *"implementations may send only 1 options if they don't want the
    device to choose"*. Read it together with the surrounding doc body
    quoted in the extract's A1 — the "Capabilities detection" question and
    its two branches — not only the comment on its own.
  - **The declared design intent behind R5**, from its author. Asked why
    R5 says what it says, Nicolás confirmed that it was written for the
    widest range it could carry: the APS **may** send the options
    ordered; the device **may** send its capabilities if it has them, and
    that is optional; and an implementation that does not want to offer a
    choice simply has the APS send one option, leaving the Player nothing
    to select. If the optional capability signal goes unused and the APS
    returns everything, the device chooses; if the APS sends a single
    option, the APS holds control. The spec is flexible and the
    implementation may vary. **This is settled and is NOT under
    verification**: the author of R5 has
    confirmed the intent in writing, and confirmed that his comment on the
    WG doc is the faithful statement of it. **R5 is a superset, not a
    prescription, and the A2 shape — the APS sending a single option — is
    one of the implementations it is meant to permit.** Take it as given.
  - **The ordered-fallback decision record.** It is a **`LOG.md` entry,
    not an ADR** — `.project/LOG.md`, the entry headed
    `## 2026-05-27 — decisions: positional ordered fallback (normative)
    + advertiser-owned background fill (Option A)`, together with
    **phase 02's own T-04 / T-05 notes** in
    `.project/phases/02-wg-feedback-round-1/TASKS.md` (that phase's ids,
    not this one's). Read the
    *rationale*, not just the outcome: that entry records that the spec
    previously modelled preference as **optional** ADS-supplied priority
    hints and that the decision made document order normative. Whether
    A2 collides with that decision or merely with its wording depends on
    what the decision was actually protecting.

  **Return one of three verdicts per pair, and all three are valid
  results:**

  - **`contradiction`** — the two cannot both hold. State which
    construct must give, and what depends on it.
  - **`compatible`** — the apparent conflict dissolves on reading the
    literal text. State why, precisely enough that the next reader does
    not have to redo the work.
  - **`indeterminate`** — the transcript does not settle what the WG
    meant. This is expected to be the outcome for several pairs, and it
    is a real result, not a failure to reach one.

  **The question about R5 is no longer what it means — it is whether the
  text says it.** The intent is fixed by its author (above), so do not
  spend effort reconstructing it. What remains is narrower and entirely
  textual: **does R5 as written let a reader outside this project see
  that the single-option, APS-decides case is conformant?** A WG reader
  has only the words. If the words read as an obligation to offer choice,
  the gap is in the drafting, not in the design — and **T-04 owns fixing
  it**. Report the gap; do not fix it here.

  **A fourth outcome is admissible, and is now the expected one for A2:
  the spec does not express its own flexibility.** R5 was designed as a
  superset; if its text does not convey that — for instance if "MUST
  render the first option whose form and layout its device can satisfy"
  reads as mandating client-side selection rather than describing what a
  Player does *when given* several options — then the finding is
  **neither a contradiction nor a compatibility**: it is a **drafting
  defect**, and **T-04 is already open to act on it**. Label it as such,
  so T-01 does not emit a design change where the spec only needs to say
  what it already means.

  **Do not force a verdict.** If the honest answer is "we need David to
  say what he meant", that **is** the answer, and what it produces is a
  concrete question for the WG rather than a change to the spec. A
  forced `contradiction` costs far more than an admitted
  `indeterminate`: it sends T-01 to generate rework against a spec that
  may be fine.

  **Three of the eleven open readings in §4 land directly on A2's
  mechanics**, which is the specific reason this pair is in doubt:
  §4.8 (whether the placement-type list is ordered, and whether order
  expresses preference), §4.9 (where in the MPD the declaration lives —
  David breaks off mid-sentence asking whether it is on a Period), and
  §4.7 (whether `concurrent-static` is a presentation element or only a
  placement-type token). **If order expresses preference, the distance
  between A2 and R5 narrows sharply.** Test that explicitly rather than
  assuming either way.

  **Hypotheses to test for each pair.** These are candidate readings to
  check against the sources, not findings — several may be wrong, and
  the task may surface better ones:

  - **A2 vs R5 — the layer question**, now with the author's own words
    behind it. R5 governs the **resolution document** the APS returns to
    the Player. A2 describes the **ad request** going the other way,
    Player → APS → ADS. Nicolás's comment states the boundary directly:
    *"the URL to the APS is not under this spec (you could send a
    queryparam with capabilities in your implementation if you like)"*.
    If the request leg is outside this spec's scope, A2 may not touch R5
    at all. **Cross-check against R18**, which already declares the ADS
    and APS API contracts out of scope, and against R18.1 / R18.2 — if
    R18 already excludes the request leg, that is close to dispositive
    for this pair, and the finding is that the two requirements were
    never in the same territory.
  - **A2 vs R5 — the cardinality question.** R5.5 says a candidate
    **MAY** carry multiple presentation options; the comment says
    *"implementations may send only 1 options if they don't want the
    device to choose"*. If the ADS narrows upstream and the APS returns
    one option, does anything in R5 *require* more than one, or is a
    single-option candidate already conformant? Check R5.1's "one or
    more" against R5.5's "MAY", and check whether R5.2's "MUST render
    the first option whose form and layout its device can satisfy" is an
    obligation to *offer* choice or merely a rule for resolving choice
    when it was offered.
  - **A2 vs R5.4 — the "not required to" question.** R5.4 says neither
    the ADS nor the APS **MUST be required** to maintain a device-class
    matrix. A2 has the APS receiving device information, and the comment
    treats sending capabilities as an optional implementation liberty.
    Determine whether R5.4 *forbids* the APS from knowing about the
    device or merely declines to *mandate* it. The two readings give
    opposite verdicts.
  - **A2 — what did the call conclude, and on what support?** The comment
    cited around A2 argues the opposite of A2, and the transcript of that
    stretch breaks down. Two questions sit next to each other there —
    where capability *detection* happens (**A1**, which Nicolás
    did agree to) and who *chooses* the presentation (**A2**, on which the
    comment argues for the device) — so the passage can be read as bearing
    on either.
    Establish which of the two the room was on, because the answer changes
    what A2 even *is*: if the support was for A1, then A2 has less backing
    than the extract credited it with, and the WG's position on it is
    unsettled rather than agreed. Read the 10:08 and 10:49 turns
    against the comment side by side. If the transcript cannot settle it,
    this becomes the single most valuable question to put to the WG.
  - **A6 vs R22 — contradiction or gap.** R22 bounds simultaneity
    **within** the non-linear family; A6 states the rule **across**
    families. Silence is not contradiction. Check whether R22 is simply
    narrower than A6 (a gap to fill) rather than incompatible with it,
    and note that R17 already legislates one cross-family case, which
    means the spec is not entirely silent on the axis.
  - **A7 vs R17 — are these the same state?** R17 governs a pause-ad
    against an active **overlay**. A7 governs pausing during an **ad
    break**. Determine whether "an overlay is active" and "an ad break
    is running" denote the same condition in this spec's model. If they
    do not, the two rules may never meet.
  - **A8 vs the Player-dismiss vocabulary — absence, not conflict.**
    The spec's "dismiss" always means the Player dismissing on resume
    (R16, R21). A viewer-initiated skip appears to be absent rather
    than forbidden. Absence is an addition, not a contradiction, and
    the verdict should say which it is.

  **Constraints.** Do **not** edit `context/` — this task produces a
  verdict, not a change. Do **not** resolve any §4 reading by
  inference: where a verdict depends on one, say so and hand the
  question to T-02 rather than picking the likelier meaning. Quote
  **both sides verbatim** in the output — the transcript line and the
  spec line — so the verdict can be audited without reopening the
  sources. **Where the verification overturns something the extract
  asserts, correct the extract**, including the "Consequence for our
  spec" note on the affected item; leaving a disproved claim in the
  phase material corrupts the audit trail for everything downstream.

  **This task gates T-01** on the A2, A6, A7 and A8 items. It does not
  depend on T-02, though T-02's answers would settle several
  `indeterminate` verdicts if they arrive first.

- **Definition of done:** each of the four pairs — A2 vs R5, A6 vs R22,
  A7 vs R17, A8 vs the Player-dismiss vocabulary — carries exactly one
  verdict from `contradiction` / `compatible` / `indeterminate` /
  `spec-does-not-express-its-intent`, each grounded in **both** a
  verbatim quote from a primary source read in context **and** the
  literal spec text it is measured against, both reproduced in the
  output. For A2 specifically: the output states whether R5's
  **text** conveys the flexibility its author has confirmed it was
  designed to have (the intent itself is given, not verified); the R18
  scope question is answered; and the question of what the call concluded
  on A2, and on what support, has an answer or a question addressed to
  the WG. Every
  `indeterminate` verdict ends in a concrete, answerable question
  addressed to a named person (David for the WG's intent, Nicolás for
  our own). Every verdict labels the work it implies as **design** (what
  the spec requires changes) or **drafting** (what the spec requires
  stays, its wording changes). Every verdict that overturns the extract
  has been written back into the extract. The result is saved to
  `tasks/T-03/`. `context/` is byte-identical to how T-03 found it.

## T-04 — Make R5's flexibility explicit in `context/`

- **Objective:** R5 was designed as a **superset** — a spec that permits
  a range of implementations rather than prescribing one — and its
  author has confirmed that in writing. The text does not obviously say
  so: its wording can be read as mandating device-side selection, and
  this phase's own extract initially read it that way. Make the
  permissiveness legible, so that a reader who has only the words
  reaches the conclusion the author intended. **This is a drafting task,
  not a design task: it changes what the spec *says*, not what the spec
  *allows*.** Nothing that is conformant today stops being conformant,
  and nothing that is non-conformant today becomes allowed.

- **What it must cover:**

  **The authoritative statement of the intent** is Nicolás's comment on
  the WG doc, reproduced verbatim in the extract's A2. He has confirmed it is the
  faithful formulation of what he wants `context/` to say, so it is the
  target, not an input to be re-litigated. Its three operative points:

  1. The APS **may** send the presentation options as an ordered list.
  2. The device **may** send its capabilities if it has them — **this is
     optional**, not required.
  3. An implementation **may** send a single option, in which case
     **control sits with the APS**; if it sends them all, control sits
     with the device.

  Plus the framing that has to survive into the text: **the spec is
  flexible and implementations vary. Both ends of that range are
  conformant — neither is the correct one.** A reader must not be able
  to finish R5 believing that one of the two is privileged.

  Plus the scope statement: **"the URL to the APS is not under this
  spec"**. Cross-check it against **R18**, which already declares the
  ADS / APS API contracts out of scope, and against R18.1 / R18.2. Then
  **decide** — and record the decision — whether R18 already carries
  this adequately and only needs to be easier to find from R5, or
  whether R5 itself has to state it. Both are defensible; picking one
  without checking R18 is not.

  **Where to look and what to touch.** Start with R5 and R5.1–R5.7 in
  `context/03-requirements.md`, then R18, then the **Ad Presentation
  Server** section of `context/02-actors.md` (specifically "Produce
  candidates with renderable presentation options", which is phrased as
  an obligation) and its Boundary Summary line on selecting the ad to
  render. Read the design principles first: **DP-1.1 rejects
  speculative constructs and DP-2 requires positive obligations rather
  than enumerated prohibitions** — expressing permissiveness must not
  turn into a list of things an implementer may not do, and must not add
  a construct whose only job is to announce flexibility. The likely
  shape of the fix is therefore wording and framing, not new attributes.
  Also check the `99-glossary.md` entry for "presentation option", which
  may carry the same implicit assumption.

  **The boundary with T-05.** These two tasks divide the same problem
  and must not overlap. **T-04 fixes what is there**: it audits R5 and
  the APS section and clarifies the existing wording where it fails to
  convey the permissiveness. It is **subtractive of ambiguity — it adds
  no new artefact**: no new requirement, no new use case. **T-05 adds
  what is missing**: an explicit statement that an APS may return exactly
  one option, and/or the use case that demonstrates it. So if, while
  auditing, this task concludes that the text cannot be made clear by
  rewording alone and something new has to be stated, that is **T-05's
  finding to act on** — record it and hand it over rather than growing
  this task's scope. Note that **UC-09 demonstrates only one of the two
  permitted implementations** (the APS returns everything, the device
  chooses); that observation belongs to T-05, which owns whether to
  answer it with a companion example.

  **Constraints.** Do **not** change what the spec permits or requires —
  if a candidate edit would make a currently-conformant implementation
  non-conformant, or vice versa, it is out of scope for this task and
  belongs to a design task instead. Do **not** renumber requirements or
  use cases. Do **not** add a construct to express flexibility (DP-1.1).
  If the work turns out to require a semantic change rather than a
  wording change, stop and say so rather than proceeding — that is a
  finding, and it would mean the intent and the current design actually
  differ.

  **Dependencies: none, deliberately.** This task does **not** wait for
  T-03. The intent is already confirmed by R5's author, so clarifying the
  wording is justified whatever verdict T-03 reaches on A2 — if T-03
  finds the text does not convey the intent, this is the fix; if it finds
  the text is fine, this task closes cheaply as "no change needed" with
  the reasoning recorded. Nobody should block on T-03 to start here.

  **The relation to T-01 runs the other way.** If this task lands, **a
  number of the 19 candidate change items stop being design changes and
  collapse into this one drafting problem** — anything whose supposed
  conflict was really "the spec does not say it permits this". T-01 must
  therefore check this task's outcome before emitting items in that
  family, and say which of its candidates were absorbed here.

- **Definition of done:** R5 (with its sub-requirements) states plainly
  that the ordered-options mechanism is a **permission, not an
  obligation**; that the device supplying capabilities is optional; and
  that a single-option response with the APS holding control is
  conformant — with neither end of the range presented as preferred. The
  APS section of `02-actors.md` no longer reads as obliging multiple
  options. The R18 question is decided and the decision recorded. No new
  requirement and no new use case were added — anything the audit finds
  to be *missing* rather than *unclear* is written up and handed to T-05.
  A reader given only `context/` — no ADRs, no LOG, no phase material —
  gets no further from answering "may an APS return exactly one
  presentation option and decide the layout itself?" with "yes" than the
  existing wording allows; where wording
  alone cannot get them there, the gap is recorded for T-05. No
  requirement changed what it permits or forbids; the diff is wording,
  framing and, if the task so decides, one example.

## T-05 — State in `context/` that an APS may return exactly one option

> **Its core has landed; what remains is the use case.** The explicit statement
> this task was created to add is now in `context/` — R5's prose carries that
> carrying several options is the form the requirement asks for, that carrying
> exactly one is equally admissible, that an implementation which does not want
> the Player choosing sends a single option, and that the choice then sits with
> the APS or with the ADS that returned one to it; the APS section of
> `02-actors.md`, R5's gist, the core-invariant row and two `99-glossary.md`
> entries carry the short form. It landed inside the application of the A2
> drafting fixes, on Nicolás's instruction, rather than through this task.
> **What is left for T-05 is only the open question below**: whether to add the
> companion use case that pairs with UC-09. Do not re-state the permission — it
> is already written, and writing it twice is what this note exists to prevent.


- **Objective:** put into `context/` an explicit, findable statement that
  **an APS may return exactly one presentation option** — and, on the
  strength of it, that doing so is a conformant implementation in which
  the APS holds the choice rather than the device. Nicolás asked for this
  directly: a requirement, a clarification, or something in `context/`
  that says an APS may return one option — possibly a use case explaining
  that the APS wants to offer only one option. Where T-04 removes
  ambiguity from what is already written, this task **adds the thing that
  is not written**.

- **What it must cover:**

  **Decide the form, with an argument. Three candidates, not mutually
  exclusive:**

  1. **A clarification inside R5** — the smallest change.
  2. **A new requirement** that states the permission head-on.
  3. **A use case** that shows an APS choosing to return one option.

  A criterion worth applying, though the task owns the call: **a
  requirement says what is permitted; a use case shows why someone would
  want it.** Nicolás's framing — an APS that *wants* to offer only one
  option — is a **motivation**, not a rule, and motivations read better as
  a use case. **His message leans toward the use case**, and that is the
  preference of the spec's owner, so start from it as the leading option
  rather than as one of two equals. It is a preference and not an
  instruction: if the analysis lands elsewhere, say why, and say it to
  him rather than deciding silently.

  **The cost of the use-case route is in scope, not a surprise.** Adding
  a use case means: the next free **UC number**; the *"Total UC count"*
  line and both matrices in
  `context-analysis/uc-coverage-matrix.md`, which enumerate UC-01..UC-12
  explicitly; `context-analysis/dash-gap-analysis.md`, which maps each UC
  against DASH; and the UC cross-references in
  `context/03-requirements.md`, `context/05-dash-linear-interfaces.md`
  and `context/07-backward-compat-checklist.md`. The derived artefacts
  are regenerable — `prompts/1-pre-spec/build-uc-coverage-matrix.prompt`
  builds the matrix — so prefer regenerating over hand-editing, and check
  `CLAUDE.md` ("How to modify the spec") for which downstream steps go
  stale.

  **Numbering has a live collision risk — check before picking.** The
  highest landed requirement is **R28**, but phases `03-custom-layout`
  and `04-multiview` have already *proposed* **R29** and **R30**
  respectively, and both phases record "next free UC number — fixed at
  execution" for their own use cases. Neither has executed, so nothing is
  committed, but two unexecuted phases are holding informal claims on the
  numbers immediately after the current maximum. Read
  `.project/phases/03-custom-layout/` and
  `.project/phases/04-multiview/` before choosing, and if the pick would
  collide, raise it rather than quietly taking the number — renumbering
  later is exactly the churn the repo convention exists to avoid.

  **If a use case is added, it forms a pair with UC-09, and the pair is
  the point.** UC-09 shows the device choosing from an ordered list; the
  new one shows the APS deciding and sending one option. **Together they
  teach that the spec is a superset far better than any adjective in a
  requirement can** — which is the whole reason this is worth its cost.

  **But the pair carries a failure mode this task must actively prevent:
  two use cases can read as two *modes* of the spec rather than two
  *implementations of the same rule*.** If they land as "mode A" and
  "mode B", the misunderstanding gets worse, not better — a reader would
  then look for which mode to declare, and there is nothing to declare.
  So the text of **both** (UC-09 included — editing it is in scope for
  this) must make plain that they exercise **one rule, R5, differently**;
  that the difference lives in the **implementation**, not in the spec;
  and that **neither is the canonical path**. Do not introduce any name,
  label, flag or attribute that could be read as selecting between them.
  Under DP-1.1, a construct whose only purpose is to announce which mode
  you are in must not exist.

  **Start here**: R5 and R5.1–R5.7 plus DP-1.1 / DP-2 in
  `context/03-requirements.md`; UC-09 in `context/04-use-cases.md`, read
  in full, since it is both the model to follow and a file to edit; the
  APS section of `context/02-actors.md`; the verbatim comment reproduced
  in the extract's A2, which is the authoritative statement of the
  intent; and `CLAUDE.md` for the house style — requirements are
  self-contained and concise, and do not compare themselves to other
  requirements.

  **The same hard limit as T-04: this clarifies and exemplifies; it does
  not change what the spec permits.** Nothing conformant today may become
  non-conformant, or vice versa. **If writing it surfaces that a semantic
  change is actually needed, stop and report** — that would mean the
  intent and the current design genuinely differ, which is a finding for
  Nicolás, not an edit to push through.

  **Dependencies: none, deliberately.** Like T-04, this does not wait for
  T-03: the intent is already confirmed by R5's author, so stating it is
  justified whatever verdict T-03 reaches. If T-04 runs first, read its
  output to avoid restating what it already clarified. **The relation to
  T-01 runs the other way**: if this lands, it is a second route by which
  several of the 19 candidate items stop being design changes, and T-01
  must check this task's outcome and report which candidates it absorbed.

- **Definition of done:** `context/` contains an explicit statement that
  an APS may return exactly one presentation option, and that this is
  conformant with the choice sitting at the APS. The chosen form —
  clarification, requirement, use case, or a combination — is recorded
  with the reasoning, and if it diverges from Nicolás's stated preference
  for a use case, the divergence was raised with him rather than decided
  silently. Any number taken does not collide with the R29 / R30 / next-UC
  claims held by phases 03 and 04, or the collision was raised. If a use
  case was added: the coverage matrix and gap analysis are regenerated
  (not hand-patched), the UC count line is correct, and **both** the new
  case and UC-09 state that they exercise the same rule differently with
  neither being canonical. No construct exists whose purpose is to select
  between the two. A reader given only `context/` can answer "may an APS
  return exactly one presentation option and decide the layout itself?"
  with "yes", and can point at the sentence that says so. No requirement
  changed what it permits or forbids.

# Where our execution behaviour meets DASH's — the survey before the edits

**Status: SURVEY — nothing applied.** `context/` is untouched by this
document.

Nicolás decided the criterion: **adopt the base specification's execution
model verbatim wherever it already answers, and declare an extension only
where it does not.** This is the survey of where that criterion lands,
produced before any edit so the scope is visible while it is still a
conversation and not a diff.

Line numbers are in the text extraction of ISO/IEC 23009-1:2026 and are
reproducible from it. Every negative claim below carries its control,
because a negative claim is the kind that has already fooled us twice.

## Summary

| | Rows | What adopting costs |
|---|---|---|
| **Coincide** — DASH already says what we say | 2 | Nothing. Cite instead of restate. |
| **Diverges** — DASH answers, we answer differently | 4 | Behaviour changes. One is new. |
| **DASH answers, we are silent** | 4 | New text. Two are whole attributes we never mention. |
| **We answer, DASH does not** | 3 | Nothing. These are the legitimate extension. |
| **Neither answers** | 1 | Candidate for an MPEG comment, not for us. |

**The two known cases are three, and the survey found a fourth.** Beyond
them, the criterion opens territory the spec has never written about at
all: what happens on a seek.

---

## Coincide — adopt means cite, not change

### C-1. Applying the spec never breaks primary playback

- **DASH** (§5.16.2.2.5, PDF 11547): *"If no event can be successfully
  executed, the playback continues uninterrupted."* And §5.16.2.2.6
  (PDF 11616): *"A failed execution results in smooth continued playback
  of the main media presentation."*
- **Us**: DP-3's hard invariant, and R1.4.
- **Verdict**: identical. Ours currently reads as our own design
  principle; it is the base model's rule. Citing it costs nothing and
  removes a place where a reader could think we invented it.

### C-2. Which overlapping window is served first

- **DASH** (§5.16.2.2.5 step 2, PDF 11536): events are applied *"in its
  priority order (from oldest PRT to the most recent)"*, the queue being
  ordered by presentation time.
- **Us**: R20.1's *"the first overlapping window it encounters"*, now
  anchored by R20.2 to document order inside one `EventStream`.
- **Verdict**: the same selection. Worth stating that it is, because
  R20.1 and DASH arrive there by different wording.

---

## Diverges — DASH answers, and we answer differently

### D-1. What a failed resolution does to the rest of the queue *(known)*

- **DASH** (§5.16.2.2.5 step d, PDF 11541): *"If execution fails, steps
  a-c above are repeated for next events in QE, until: — Execution
  succeeds, or — PRT of the topmost event in the queue is in the future
  …, or — The queue is empty."*
- **Us**: R20.1 falls through **only** when the first window cannot be
  accessed. A `200` carrying no candidates ends the chain.
- **Adopting** inverts the fall-through condition: any failed execution
  tries the next event.

### D-2. Whether the opportunity survives *(known — decided)*

- **DASH**: `E.c` is *"Execution counter (number of times alternative MPD
  playback **successfully started**)"* (§5.16.2.2.2, PDF 11432). The
  queue admits an event when *"either E.executeOnce is false, or both
  E.executeOnce is true and E.c = 0"* (§5.16.2.2.3, PDF 11480). And
  NOTE 3 (PDF 11618): *"The counter E.c has not been incremented due to
  the failure, consequently if E.c = 0 the event can still be executed
  in the future even if the value of `@executeOnce` is `"true"`."*
- **Us**: the opportunity is spent.
- **Adopting inverts ours.** The counter rises only when an ad actually
  started; an empty slot does not consume the opportunity.

### D-3. The duration cap when the event fires late *(known)*

- **DASH** (§5.16.4, PDF 11870): `@clip`, default `"true"` — the
  alternative presentation *"shall terminate at the latest at time
  PRT + APDmax"*; with `"false"`, *"at time PRTA + APDmax"*. And
  `APDadj = max(APDmax - PRTA + PRT, 0)` (PDF 11252).
- **Us**: R4 treats the cap as a pure duration and never mentions
  lateness, which lands a literal reader on DASH's **non**-default.
- **Adopting** makes the cap mean *until when* on the replacement path
  and *how long* elsewhere — with the asymmetry stated, because `@clip`
  exists only on `ReplacePresentation`. The structural reason: insertion
  resumes at `RT = PRTA`, so there is no original slot end to preserve.

### D-4. A `200` carrying a document that does not parse — **new**

- **DASH** (§5.3.2.6.3 step 5, PDF 2874): *"In case the resulting
  in-memory MPD is invalid, the resolution fails and is reverted"*, which
  feeds §5.16.2.2.6's *"The playback of the alternative presentation
  cannot start"* and therefore D-1's next-event behaviour.
- **Us**: R20.1 enumerates inaccessibility as *"the APS does not
  respond, the request fails at the transport level, or the response
  carries a final HTTP status other than `200`"*. **A `200` carrying an
  invalid document matches none of those, so it is "accessible" and the
  Player MUST NOT fall through.** R30 explicitly excludes it from the
  empty case (*"not a document that fails to parse"*), so nothing in our
  spec covers it.
- **Why it matters**: the 200-strict rule was written to stop an empty
  resolution from being read as a failure. It also, unintentionally,
  stops a **real** failure from being read as one.
- **This item exists separately only because D-1 was not adopted.**
  D-1's rule is "any failed execution tries the next event", and an
  invalid document is a failed execution, so adopting D-1 covers this
  case without enumerating it. Applied on its own — which is what was
  done, in `0c39793` — the enumeration is what closes the hole. If NC2
  later resolves toward adopting D-1, this becomes redundant rather
  than wrong, and a reader finding it then should know why it is
  there.

---

## DASH answers, we are silent

### S-1. Seek

- **DASH** (§5.16.2.2.1, PDF 11407): a seek *"results in shifting the
  playhead position and thus causes re-execution of the event if the
  playhead position is smaller than or equal to EAP"*; the queue is
  reset on every seek (§5.16.2.2.3).
- **Us**: nothing. **Control**: `seek` appears zero times across
  `context/*.md`; the same grep finds `playhead` eight times, so the
  instrument works.

### S-2. Events that may not be skipped — `@noJump`

- **DASH** (§5.16.5, PDF 11983): *"If non-zero, the playhead may not
  move forward from any point for which PHP < PRT to any point where
  PHP > EAP without executing this event."* Value 1 executes all such
  events; value 2 only the latest.
- **Us**: nothing. **Control**: `noJump` appears zero times in
  `context/`; the same sweep finds `@maxDuration` 13 times and `@clip`
  4, so the instrument finds attributes.
- This is a Publisher-facing capability — forbidding ad-break skipping —
  that we inherit and never mention.

### S-3. A cap of zero

- **DASH** (§5.16.5, PDF 11955): *"If the value of `@maxDuration` is
  zero, the event is not executed."*
- **Us**: R4.1 requires a cap on every slot and says nothing about zero.
  A zero cap is not a very small slot; it is an opportunity that never
  fires.

### S-4. An absent cap

- **DASH** (§5.16.5, PDF 11955): *"If absent, the value is assumed to be
  infinity, in which case the current presentation resumes only when the
  alternative presentation terminates."*
- **Us**: R4.1 makes the cap mandatory. That is **stricter**, not
  contradictory — but it is an extension we never declared as one.
- This also answers `G-1`'s sibling `G-2` ("no Player behaviour when a
  slot carries no `@maxDuration`"), which can leave the open list.

---

## We answer, DASH does not — the legitimate extension

These are where "declare an extension" applies. Each carries its control,
since each is a negative claim about the standard.

- **E-1. Ordering and skipping of candidates inside one resolution
  document** (R5.3, R5.7, R7). DASH's model resolves an event to one
  alternative presentation; the notion of several candidates walked in
  order, each skippable on a device-capability test, has no counterpart.
  **Control**: the standard's own vocabulary for this area is `merge`
  (9 hits, §5.3.2.6.3), which describes combining an imported MPD into a
  Linked Period — not selecting among alternatives.
- **E-2. A sequence of non-linear forms inside one slot** (R14.1, R22).
  DASH's non-linear surface is the storyline scheme
  `urn:mpeg:dash:nonlinearplayback:2020` (Annex L, PDF 1553), which
  signals branching of the main storyline, not overlay advertising.
  **Control**: the term is present 6 times and every occurrence is that
  scheme.
- **E-3. Device-capability negotiation** (R29). Nothing in the execution
  model takes device capability as an input.

---

## Neither answers

- **N-1. The timebase and rounding of the cap** (`G-1`). `@maxDuration`
  is *"expressed in units of `EventStream@timescale`"* (PDF 11942) while
  the alternative presentation's duration is an `xs:duration`, and
  `APDA = min(APD, APDmax)` mixes them. **Control**: `rounding` appears
  zero times in the standard; the stem `round` appears five times and
  all five are *around* or *background*. So the gap is inherited, not
  ours, and the right destination is a comment to MPEG rather than a
  requirement of our own.

---

## Scope, stated before any edit

Adopting the criterion touches, at minimum:

| Requirement | Why |
|---|---|
| **DP-3**, **R1.4** | C-1 — cite the base rule instead of asserting it |
| **R20.1** | D-1 and D-4 — the fall-through condition and the invalid-document hole |
| **R20** body | C-2 — name the base selection rule |
| **R30**, and §4.6.8 downstream | D-2 — invert "the opportunity is spent" |
| **R4**, **R4.1**, **R4.2**, **R4.3**, **R14.2** | D-3, S-3, S-4 — the cap's meaning, zero, and absence |
| **new** | S-1, S-2 — seek and `@noJump`, where the spec has never written anything |

That is **six requirements edited and two areas written from scratch**,
not two consequences applied. The two new areas are the reason this is
worth a decision rather than a batch of commits: inheriting `@noJump`
gives the Publisher a capability our spec never offered, and writing
seek behaviour means deciding what a mid-ad seek does to an opportunity
that has already been counted.

## What this survey does not do

- **It applies nothing.** No `context/` file is edited by this document.
- **It does not decide D-3's asymmetry.** That the cap means two
  different things on two paths is a consequence of adopting; whether
  that is acceptable is not this document's call.
- **It does not extend to the non-linear families beyond E-1..E-3.**
  Overlays and pause ads have no `PRT`/`PRTA` model in the base
  specification, so most of the execution model simply does not reach
  them — which is itself a finding the edits will have to state rather
  than leave implicit.

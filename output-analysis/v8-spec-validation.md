[GROUNDED_BY=spec-only]

# Spec validation — v8 (2026-09-17)

Built against:
- spec: `../output/v8-sgai-spec.md` (7641 lines)
- `context/` at git SHA: `8547827f69e761d934cb0936afaa51e9c232941d`
- population: `bin/check-promotable.py --population` — 168 units (123 criteria, 31 prose, 14 use cases)

## Method, and two things a reader has to know before the tables

**Grounding is spec-only.** The primary copy of ISO/IEC 23009-1:2026 was not
opened for this pass. Every base-specification sentence quoted below is quoted
*as the spec under review quotes it*, and is evidence about the spec's text and
not about the standard. No claim here rests on a base-specification fact this
document verified independently; nothing is tagged `[inferred]` because nothing
is asserted about the base standard on its own authority.

**The prompt's acceptance test for this step is stale, and the run proceeded
anyway.** `prompts/3-post-spec/validate-spec.prompt` §4.1 states that UC-14 was
added to `context/04-use-cases.md` after the newest spec was generated, that the
current output therefore does not walk it, and that a run reporting anything
other than `gap` for UC-14 has not walked the use cases. That is false of v8.
UC-14 is walked in the spec body at §7.5.9 (L2873) and in a dedicated Annex N
(L7128-7405) whose §N.8 covers all five device classes. Reporting `gap` to
satisfy the instruction would have been reporting a finding that is not there,
so the row says `met` and the instruction is reported as the defect instead.
The check the instruction was reaching for — *did this walk actually happen* —
is answered instead by the population arithmetic: every one of the 168 ids
`--population` prints appears exactly once in §4, each with a located quotation.

## Gaps (7)

### G-1 — The normative chapters carry no RFC 2119 modal at all

- **Where it is needed:** chapters 4 to 8, which is where every actor
  obligation in the document lives.
- **What is missing:** not a fact from `context/` — the obligation force.
  The document declares the RFC 2119 vocabulary at L9-12: *"The key words
  MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT,
  RECOMMENDED, MAY and OPTIONAL in this document are to be interpreted as
  described in IETF RFC 2119."* It then uses **none** of MUST, MUST NOT,
  SHALL, SHALL NOT or REQUIRED anywhere in the body. Chapter 4 — 780 lines
  titled *Conformance*, containing §4.3 Publisher obligations, §4.4 ADS
  obligations, §4.5 APS obligations and §4.6 Player obligations — contains
  six occurrences of `MAY` and nothing else. Chapters 6 and 7 contain no
  RFC 2119 keyword of any kind.
- **The document says otherwise about itself.** §8 opens at L2894 with
  *"Where a row below states a \"MUST\", it restates an obligation chapter 4
  already carries."* No row of §8.1 states a MUST, and chapter 4 carries
  none to restate. This is the only occurrence of the string `MUST` in the
  body outside the RFC 2119 declaration, and it asserts the existence of
  what is absent.
- **What an implementer does today:** reads §4.6 as a description of a
  reference Player. Nothing in the document distinguishes §4.6.1 *"the
  Player keeps primary-content playback uninterrupted"* — which `context/`
  states as a MUST — from §8.4 *"The conservative posture is to treat an
  unverified capability as absent"*, which is explicitly non-normative
  guidance. Both are declarative sentences in the present tense.
- **Consequence for this map:** 82 of the 168 rows in §4 are `force-lost`
  for this one reason. They are not 82 defects; they are one defect with 82
  cited locations, and T1 is the single edit that closes all of them.
- **Cited rules:** DP-2 (*"the normative modal stays"*), R20.6 (*"R20.5 MUST
  be carried as a normative Player obligation"*), and
  `projects/sgai-for-mpeg-dash/CLAUDE.md` § *Tone for the spec* (*"use RFC
  2119 vocabulary (MUST / SHOULD / MAY) when stating requirements"*).
- Routed to **5.a**. See Actionable TODO T1.

### G-2 — R32.4's out-of-scope declaration lives outside the specification

- **Where it is needed:** §4.6.11 or §5.2.2.3, where `request-again` is
  defined.
- **What is missing:** R32.4 obliges the specification to declare out of
  scope whether a second resolution request inside one pause is the same
  opportunity or a new one. §4.6.11 (L854-873) defines `request-again` and
  says nothing about it. The declaration exists only at L7638, inside the
  *Build notes* block, which opens at L7511 with *"This block is **not part
  of the specification**."*
- **What an implementer does today:** guesses, or reads the build notes as
  though they were normative. Two APSs counting the same pause differently
  is exactly the state R32.4 exists to legitimise explicitly rather than by
  silence.
- Routed to **5.a**. See Actionable TODO T3.

### G-3 — The APS half of R5.4 is never stated

- **Where it is needed:** §4.5 (APS obligations).
- **What is missing:** R5.4 binds the ADS **and** the APS: *"Neither the ADS
  nor the APS MUST be required to maintain a device-class matrix or a
  per-Player capability view to produce candidates."* §4.4.4 (L560) states it
  for the ADS in those words. §4.5 states nothing equivalent; §4.5.9 is about
  tolerating an absent parameter, which is a different claim, and §7.3
  (L2743) grants the APS a narrowing freedom without saying a device view is
  optional.
- **What an implementer does today:** an APS conformance check could
  reasonably demand a capability model, which is what R5.4 exists to
  prevent. UC-13's D4 row depends on the opposite being true.
- Routed to **5.a**. See Actionable TODO T4.

### G-4 — R13.1's alternative carrier is dropped without the omission being documented

- **Where it is needed:** §4.5.6 and §5.5.
- **What is missing:** R13.1 admits *"DASH callback events (**or an
  equivalent baseline DASH construct**)"*. §4.5.6 (L604) admits only the
  callback scheme, and §5.5 (L2071) states *"This specification introduces no
  tracking scheme of its own"* — which is a different proposition. The
  narrowing may well be right (R13.4 calls reuse mandatory), but R8.2 obliges
  the specification to document a deliberate omission inline, and this one is
  not documented anywhere.
- **What an implementer does today:** cannot tell whether an APS that used
  another baseline construct is non-conformant or merely unusual.
- Routed to **5.b** — the remedy depends on resolving A-5 first.

### G-5 — A full-screen takeover on an overlay slot has no defined effect on the primary timeline

- **Where it is needed:** §5.1.3 and §4.6.4.
- **What is missing:** §3.2 (L301) admits the `linear` token on *"an overlay
  slot, as the full-screen takeover option of last resort"*, and §5.3.7.3
  (L1991) budgets it as *"1, reused sequentially across ad and primary
  content"* — i.e. the primary content stops. §5.1.3 (L1277) says of the same
  slot family that the Player *"composites the chosen form on or alongside
  the primary content, **which keeps playing**"*. The two cannot both hold
  for the option D2 and D5 land on in UC-09 and Annex I. Nothing states where
  the primary timeline resumes after such a takeover, or what the overlay
  window's cap bounds while it runs.
- **Which reading `context/` supports:** UC-09 option 4 — *"a linear-style
  video ad that replaces the primary content for the slot, played
  sequentially (primary stops, ad plays, primary resumes)"*. §5.3.3 and
  §5.3.7.3 match it; §5.1.3's blanket sentence does not.
- **What an implementer does today:** on D2 and D5 — the two classes that
  reach option 4 — the behaviour of the most common fallback in the document
  is undefined.
- Routed to **5.a**. See Actionable TODO T2.

### G-6 — What a zero `@maxDuration` means on a pause-trigger window

- **Where it is needed:** §4.3.2 and §4.6.4.
- **What is missing:** §4.3.2 (L479) states *"A declared cap of zero means the
  opportunity does not fire"*, inheriting the base specification's rule for
  an event whose cap bounds a presentation. On a pause-trigger window the cap
  bounds something else entirely — §4.6.4 (L680): *"@maxDuration on a
  pause-trigger window bounds the display duration of a single pause ad
  before automatic dismissal"*. Zero then reads two ways: the window never
  fires, or every pause ad is dismissed immediately.
- **What an implementer does today:** picks one. The two differ by whether a
  resolution request is issued at all, which is observable at the APS.
- Routed to **5.b**.

### G-7 — No construct carries UC-03's per-slot concurrency cap

- **Where it is needed:** §5.1.3.1.
- **What is missing:** UC-03's Publisher intent includes *"Maximum number of
  concurrent overlays for this slot is bounded"*. §5.1.3.1 (L1351) declines
  it explicitly and gives a good reason: *"At most one non-linear form is
  active at any instant (§4.6.7), so an attribute whose only admissible value
  is 1 would restate a rule the specification already fixes"* — which is
  DP-1.1 applied correctly. The gap is in `context/`, not in the spec.
- **What an implementer does today:** nothing; the intent is unreachable.
- Routed to **5.c** — the use case is what needs the edit.

## Edge cases (6)

### EC-1 — `@executeOnce="true"` on a pause window, with `repeat` or `request-again`

- **Trigger:** a pause-trigger window declares `@executeOnce="true"` (§5.1.4.1
  L1413) and the APS answers with `@onCandidatesExhausted="repeat"` (§5.2.2.3
  L1650), or `request-again`. The viewer pauses for longer than the candidate
  sequence lasts.
- **Why it matters:** §4.6.12 (L875) says *"the Player presents **at most one
  pause ad** for that window for the duration of the session"*, and §4.6.12
  (L879) says the window *"is consumed when a pause ad **begins rendering**"*.
  §4.6.11 says `repeat` means *"Present the sequence again from the start, for
  as long as the pause lasts"* — that is a second, third and fourth pause ad
  beginning to render on a window already consumed. The two obligations are
  jointly unsatisfiable, and a Player has to pick which one to break.
- **Responsible actor:** the Player, and neither `context/` nor the spec says
  which rule wins. R34.2 and R32.1 are written independently of each other and
  neither mentions the other.
- Routed to **5.b**.

### EC-2 — `@executeOnce="true"` on an overlay window carrying several candidates

- **Trigger:** an overlay window declares `@executeOnce="true"`, and its
  resolution document carries three candidates.
- **Why it matters:** §5.1.3.1 (L1338) defines the attribute on an overlay
  window as *"the window yields at most one overlay **presentation** for the
  session"*, while §4.6.7 (L750) has the same window present *"candidates one
  after another in declared order"*. Whether "one presentation" means one
  window execution or one rendered form decides whether candidates 2 and 3
  ever appear. The same word does different work in the two sentences.
- **Responsible actor:** the Player. `context/` is silent: R34 gives the
  once-per-session capability to the pause family only, and no requirement
  defines `@executeOnce` on an overlay window at all.
- Routed to **5.b**.

### EC-3 — Two tracking event streams on one candidate, with different timescales

- **Trigger:** a `video` presentation option whose sub-MPD carries a callback
  `<EventStream>` at `timescale="90000"`, on a candidate that also carries one
  at `timescale="1000"` — both placements admitted by §5.5.2 (L2126).
- **Why it matters:** §5.5.2 (L2131) says *"the Player fires the union, with
  beacons sharing an `@id`, or carrying the same URL at the same
  `@presentationTime`, fired once"*. Both keys are ambiguous across two
  streams: `@id` is unique within a stream and nothing makes it unique across
  two, and *"the same `@presentationTime`"* compares raw integers that are in
  different units. The de-duplication rule R6.5 mandates therefore either
  over-fires or under-fires exactly in the case §5.5.2 created by admitting
  two placements.
- **Responsible actor:** the Player; the spec is silent on normalising the
  timebase before comparing, and `context/` (R6.5) assumes one carrier.
- Routed to **5.b**.

### EC-4 — A live pause outliving the time-shift buffer

- **Trigger:** live content, the viewer pauses inside a pause-trigger window
  for longer than `MPD@timeShiftBufferDepth`.
- **Why it matters:** R25.1 promises the presentation time stays frozen *"for
  the full duration of the pause"* without qualification, which is a promise
  no Player can keep once the buffer has rolled past. The spec **handles it**
  — §4.6.17 (L947) bounds the freeze by the time-shift buffer and states the
  resumption position — so this is a case the output fixed and the input still
  overstates.
- **Responsible actor:** the Player; the spec is complete and `context/` is
  the one that is silent.
- Routed to **5.c** — R25.1 is what needs the bound written into it.

### EC-5 — An overlay slot whose `@maxDuration` outlasts its own `<Event>@duration`

- **Trigger:** an overlay `<Event>` with `duration="30000"` whose
  `<svta:OverlayPresentation>` declares `maxDuration="45000"`.
- **Why it matters:** R14.2 says the cap is enforced *"when the cumulative
  duration would exceed **the slot's opportunity window**"*, treating the cap
  and the window as one bound. §4.6.4 and §4.6.7 enforce `@maxDuration` and
  never consult the declaring event's `@duration`, and §3.1 (L230) defines the
  opportunity window as exactly that `@duration`. So an overlay can be
  rendered 15 seconds past the window that authorised it, conformantly.
- **Responsible actor:** the Player. `context/` conflates the two bounds
  (A-6); the spec silently picks the cap.
- Routed to **5.b**.

### EC-6 — A hybrid slot whose linear portion declares `@clip="false"`

- **Trigger:** §5.1.5's hybrid slot — a `<ReplacePresentation>` event and an
  `<svta:OverlayPresentation>` event at the same `@presentationTime` — where
  the replacement event carries `@clip="false"`, which §4.6.4 (L677) says makes
  the slot *"end later than scheduled"*.
- **Why it matters:** the overlay window's own bound did not move. §4.6.4
  (L703) says cap arithmetic runs on the presentation timeline and only a
  non-advancing timeline stops it accruing, and a replacement keeps the primary
  timeline advancing. So the overlay expires while the linear ad it was
  composed over is still running, and nothing says whether that is intended.
- **Responsible actor:** the Player. `context/` does not pair R4.6 with R14 or
  with the hybrid case of UC-04.
- Routed to **5.b**.

## Ambiguities (7)

### A-1 — Which families the cap bounds by cumulative duration

- **Context passage:** `context/03-requirements.md` L352, R4.2: *"Where the cap
  bounds cumulative duration — **the non-linear families**, and linear insertion
  — the Player MUST stop rendering once the cumulative duration of the accepted
  candidates would exceed it"*. Against L442, R31.2: *"The Publisher-declared
  slot cap (R4) MUST NOT be interpreted as bounding the duration of a pause
  slot… on a pause slot it bounds **neither**"*.
- **Reading 1:** "the non-linear families" is plural and means overlay and
  pause, so a pause slot's cap bounds cumulative duration. R4.2 says this.
- **Reading 2:** the pause family is carved out, so the cap bounds nothing
  there. R31.2 says this.
- **Reading 3, which is neither:** the cap bounds the display duration of one
  pause ad. `context/04-use-cases.md` UC-05 Publisher intent says *"Maximum
  display duration before automatic dismissal is bounded"*.
- **What the spec assumed:** reading 3. §4.6.4 (L680): *"@maxDuration on a
  pause-trigger window bounds the display duration of a single pause ad before
  automatic dismissal."* It is the only reading that leaves the attribute R4.1
  makes mandatory with any work to do, and it is grounded in a use case — but
  it comes from neither R4 nor R31, which are the two requirements that discuss
  the cap.
- **Tighter sentence:** in R4.2, replace *"the non-linear families"* with *"the
  overlay family"*; in R31.2, add *"On a pause slot the cap bounds the display
  duration of one pause ad before automatic dismissal, and not the slot."*
- Routed to **5.c**.

### A-2 — UC-03's Publisher intent names constructs the closed set does not have

- **Context passage:** `context/04-use-cases.md` L290-296, UC-03 Publisher
  intent: *"Allowed layouts for this slot are restricted to a subset declared by
  the Publisher (e.g. banner, corner, L-shape, side-by-side, **sidebar**)"* and
  *"Maximum number of concurrent overlays for this slot is bounded."*
- **Reading 1:** the examples are indicative prose and the closed set of R12
  governs; the concurrency cap is a real Publisher declaration.
- **Reading 2:** both bullets are pre-R12, pre-R22 residue.
- **What the spec assumed:** reading 2. `banner` and `sidebar` appear nowhere in
  §3.2, and §5.1.3.1 (L1351) declines the concurrency attribute citing the
  single-active-form rule — which is DP-1.1 applied correctly, since R22.1 fixes
  the value at one.
- **Tighter sentence:** replace the layout examples with tokens from R12
  (`overlay-corner`, `squeezeback-l-shape`, `squeezeback-double-box`), and drop
  the concurrency bullet with a pointer to R22.1.
- Routed to **5.c**. See also G-7.

### A-3 — Whether a narrowing that changes what an absent attribute means is an override

- **Context passage:** `context/03-requirements.md` L143, R1.3: *"The
  specification MUST NOT alter or override the semantics of any pre-existing
  MPEG-DASH 6th edition construct."* Against L398, R4.10: *"The Player MUST NOT
  present ads from such a slot"*, where the base specification's own reading of
  an absent `@maxDuration` is unbounded (R4.8).
- **Reading 1:** requiring an attribute the base schema makes optional is a
  profile-style restriction on which documents conform, which R4.8 says is what
  a profile does; no semantics change.
- **Reading 2:** giving an absent attribute an outcome opposite to the base
  specification's stated one — no ad, rather than an unbounded one — is
  overriding its semantics for any Player implementing this specification.
- **What the spec assumed:** reading 1, and it flags the tension itself. §4.3.2
  (L470) calls it *"a deliberate narrowing… which is what a profile-style
  restriction does"*; §4.6.4 (L714) then says *"This position diverges from the
  base specification and is open… A reader should not take this rule as
  settled."* The same narrowing is applied a second time, unremarked, to
  callback `<Event>@id` at §5.5.1 (L2109).
- **Tighter sentence:** add to R1.3 *"Requiring an attribute the base schema
  declares optional, and fixing the behaviour when it is absent, is a narrowing
  and not an override, provided the specification records it as such (R4.8)."*
- Routed to **5.c**.

### A-4 — R26.1's "composition attribute of the slot / layout"

- **Context passage:** `context/03-requirements.md` L1045, R26.1: *"The
  background element of a side-by-side / double-box layout MUST be carried as a
  composition attribute of the slot / layout, not as a separate presentation
  option (R5)."*
- **Reading 1 (slot):** it belongs on the Publisher's slot declaration in the
  main MPD.
- **Reading 2 (layout):** it belongs on whatever construct carries the layout,
  wherever that lives.
- **What the spec assumed:** reading 2. §5.3.7.2 (L1948) carries it as a
  `<svta:BackgroundElement>` child of the `<svta:RenderableAsset>` whose
  `@layout` is `squeezeback-double-box-with-background`, and argues the point
  at L1942: *"It is a composition attribute of the layout rather than one of the
  candidate's alternative presentation options: the Player does not walk it the
  way it walks the options."* Reading 2 is the only admissible one, because R26
  itself says the background element is *"the **advertiser's** creative, owned by
  the advertiser and not the Publisher or platform"*, so it cannot travel on the
  Publisher's declaration.
- **Why this matters beyond wording:** an earlier pass of this step reported
  R26.1 as `contradicted` on reading 1. It is not contradicted; the ambiguity is
  in the criterion. That verdict is reversed here.
- **Tighter sentence:** replace *"of the slot / layout"* with *"of the layout
  that presents it"*.
- Routed to **5.c**.

### A-5 — How free the APS is to use a tracking carrier other than the callback scheme

- **Context passage:** three requirements, three forces. L1450, R6.2:
  *"Implementations **SHOULD** carry tracking beacons as `<Event>` entries inside
  an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015`"*. L1497,
  R13.1: *"the APS MUST express them using DASH callback events (**or an
  equivalent baseline DASH construct**)"*. L1512, R13.4: *"reuse of the DASH
  baseline callback mechanism is **mandatory**"*.
- **Reading 1:** the APS may use another baseline construct (R6.2's SHOULD,
  R13.1's parenthesis).
- **Reading 2:** the callback scheme is the only admissible carrier (R13.4).
- **What the spec assumed:** reading 2. §4.5.6 (L604) admits the callback scheme
  and nothing else, and drops R13.1's parenthesis without recording the omission
  — which is G-4.
- **Tighter sentence:** if reading 2 is intended, change R6.2's SHOULD to MUST
  and delete R13.1's parenthesis; R13.4 already says so and the other two should
  stop contradicting it.
- Routed to **5.c**.

### A-6 — Whether the cap and the opportunity window are one bound or two

- **Context passage:** `context/03-requirements.md` L1169, R14.2: the Player
  enforces the cap *"when the cumulative duration would exceed **the slot's
  opportunity window**"*.
- **Reading 1:** they are the same number, and R14.2 names it loosely.
- **Reading 2:** they are two independent bounds — `@maxDuration` on the
  presentation element and `@duration` on the declaring `<Event>` — and the
  shorter wins.
- **What the spec assumed:** reading 1, silently. §4.6.4 and §4.6.7 enforce
  `@maxDuration` only; the declaring event's `@duration` is defined as the
  opportunity window at §3.1 (L230) and then never consulted again.
- **Tighter sentence:** in R14.2, say *"would exceed the cap"*, and add a
  criterion stating whether a non-linear presentation may outlive the
  `<Event>@duration` that declared its window.
- Routed to **5.c**. See EC-5.

### A-7 — The criteria whose force cannot be checked, because `context/` states none

Per §4.2 of this step's own definition, a criterion carrying no RFC 2119 keyword
is recorded as `source-has-no-modal` and listed here, because its force cannot be
compared against the output. In v8's population there are **23** of them, not the
17 the prompt names:

`R18.1`, `R18.2`, `R29.1`, `R29.7`, `R4.7`, `R4.8`, `R4.11`, `R12.4`, `R32.4`, `R34.3`, `R34.4`, `R17.1`, `R17.2`, `R17.3`, `R17.4`, `R17.5`, `R20.3`, `R20.5`, `R6.6`, `R13.5`, `R33.3`, `R28.3`, `R10.3`

They are not one kind. Some are definitions (R29.1, R34.4), some are scope
declarations (R18.2, R33.3, R10.3, R4.8, R32.4), and some are plainly
obligations written in the indicative in `context/` itself — R17.1 *"the Player
renders the pause-ad form and suspends the overlay rendering"*, R17.5 *"the
Player presents the pause ad and suspends the linear ad"*, R20.3 *"Overlapping
windows of one family are ordered by presentation time, oldest first"*, R20.5
*"Each window in a fallback chain binds the candidates it serves with its own
declarations"*. For that last group the defect is in the input: a spec that
restates them in the indicative has done exactly what the input did, and this
step has nothing to compare against.

Note the self-referential edge: R20.6 exists **because** R20.5 carries no modal,
and R20.6 does carry one. That is the pattern the rest of the group is missing.

- Routed to **5.c**.

## Obligation coverage map

Every unit `bin/check-promotable.py --population` prints, in the order it
prints them, one row each — 168 units: 123 criteria, 31 prose obligations, 14 use
cases. Verdict counts: **met 81 · force-lost 82 · partial 4 · gap 1 ·
contradicted 0 · governance 0**.

**Read the `force-lost` column before anything else.** All 82 of them have the
same cause, G-1: the substance is in the spec, at the location each row quotes,
and the RFC 2119 modal the criterion states is not. They are one defect with 82
citations, and Actionable TODO **T1** closes the whole class.

| Unit | Kind | Verdict | Disposition | Evidence — quoted passage and location | Notes |
|------|------|---------|-------------|----------------------------------------|-------|
| `DP-1#p1` | `document` | `met` | — | §5.3.1 L1791: "This specification declares no priority or ranking attribute on the option: document order is the preference order (§5.3.5), and a second declaration of the same fact would be a value that could contradict the first." | Also §5.1.3.1 L1351 declines a maximum-concurrency attribute on the same ground. |
| `DP-1.1#p1` | `document` | `met` | — | §5.1.3.1 L1351: "This specification declares no maximum-concurrency attribute on the slot. At most one non-linear form is active at any instant (§4.6.7), so an attribute whose only admissible value is 1 would restate a rule the specification already fixes." | — |
| `DP-1.1#p2` | `document` | `met` | — | §5.1.3.1 L1354: "a value disagreeing with it would be unenforceable." | No attribute in §5 has a single admissible value. |
| `DP-1.2#p1` | `document` | `met` | — | §4.6.14 L911: "cap enforcement (§4.6.4) and beacon scheduling (§4.6.15) operate on the presentation-timeline duration, which stays the single canonical value." | §5.4.1 L2058 applies the same rule to the two declared durations. |
| `DP-2#p1` | `document` | `met` | — | §4.6.1 L650: "Keep the primary content playing." — every §4.6.x heading and body states a positive action rather than a prohibition. | The modal that DP-2 says must stay is absent everywhere (G-1); the positive framing DP-2 asks for is present. |
| `DP-2#p2` | `document` | `met` | — | Chapters 4-8 contain zero occurrences of "MUST NOT" (verified by grep over L390-3090). | Vacuously satisfied: there is no prohibition list because there is no normative vocabulary at all (G-1). |
| `DP-2#p3` | `document` | `met` | — | §4.6.15 L914: "Execute the tracking schedule the document carries." — stated as what the Player does, not as what it may not do. | — |
| `DP-2#p4` | `document` | `met` | — | §4.6.15 L915: "the Player fires each beacon at its scheduled relative time"; §4.6.15 L917: "the Player stops firing the remaining beacons at the trim boundary." | — |
| `DP-3#p1` | `document` | `met` | — | §4.1 L419: "The governing invariant. Applying this specification never breaks primary-content playback." | Restated per-condition in §8.1 and in §4.6.1. |
| `R1#p1` | `document` | `met` | — | §1 L32: "This specification defines Server-Guided Ad Insertion for both linear and non-linear advertising in MPEG-DASH, as a complete extension of the base specification named in chapter 2." | §4.7 carries the non-breaking half. |
| `R1#p2` | `runtime` | `force-lost` | `5.a` | §4.7.6 L1120, Legacy behaviour column: "The whole <EventStream> is skipped by the per-scheme rule; the element is discarded with its subtree" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. §4.1 L413 additionally argues the obligation cannot be placed on a Player that predates this specification; the outcome is stated, the obligation is not. |
| `R1#p3` | `document` | `met` | — | §4.7.1 L1001: "Every construct this specification introduces is expressed through one of three extension points of the base specification" | — |
| `R1.1` | `runtime` | `force-lost` | `5.a` | §4.7 L996: "What §4.7 fixes is that such a Player ignores every construct introduced here cleanly, without crashing and without a visible artefact, and keeps playing the primary content." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. The spec states the outcome and declines the obligation on the legacy Player (§4.1 L413), redirecting it to the Publisher at §4.3.9. |
| `R1.2` | `document` | `met` | — | §4.7.1 L1005 table: "Foreign-namespace open content / DASH §5.2.1"; "Application-level event streams / DASH §5.10"; "Vendor descriptor schemes / DASH §5.8.4.8, DASH §5.8.4.9" | The three extension points match the admissible set the criterion enumerates; §4.7.2 rules out the RFC 4337-bound paths the criterion forbids. |
| `R1.3` | `document` | `partial` | `5.b` | §4.6.4 L708: "A slot declaration carrying no @maxDuration is not a slot this specification defines (§4.3.2). The Player presents no ad from such a slot and continues with the primary content." | The spec narrows two baseline attributes from optional to required (@maxDuration §4.3.2, callback Event@id §5.5.1) and flags the first as diverging from the base specification's semantics in its own blockquote at L714. Whether a narrowing that changes what an absent attribute means is an override is what R1.3 and R4.10 disagree about (A-3). |
| `R1.4` | `runtime` | `force-lost` | `5.a` | §4.6.1 L654: "When resolving or rendering an accepted ad fails at runtime - a decode error, a malformed candidate, a mid-ad network loss - the Player aborts that ad and continues the primary content." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R2.1` | `runtime` | `force-lost` | `5.a` | §4.3.1 L462: "The constraints that apply to an ad slot - the cap, the admissible layouts, the resolution-timing bound, any once-per-session bound - are declared in the MPD by the Publisher. No actor infers them at runtime." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R2.2` | `runtime` | `force-lost` | `5.a` | §4.4.1 L545: "It selects which ads serve an opportunity, how many and in what order, and emits them in its own format."; §4.5.1 L575: "The APS returns HTTP 200 with a body that parses and validates" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R2.3` | `runtime` | `force-lost` | `5.a` | §4.6.3 L666: "Before rendering anything from a candidate, the Player checks each presentation option against (a) what its device can satisfy and (b) the @allowedLayouts of the window that served the candidate. Only an option that satisfies both is rendered." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R2.4` | `document` | `met` | — | §4.2 L432 table assigns every decision this specification defines to exactly one of the four actors, and §4.1 L394: "An implementation claims conformance as one actor." | — |
| `R11#p1` | `document` | `met` | — | §6.7 L2686: "Nothing in chapters 4, 5 or 7 depends on the decision document being VAST, on any VAST version, or on VAST existing at all." | — |
| `R11#p2` | `runtime` | `force-lost` | `5.a` | §4.5 L570: "Every obligation below is checked against the resolution document alone, which is the one artefact on the path to the Player that this specification defines." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. The Player-side statement that it never talks to the ADS is at §6.1 L2577-2585. |
| `R11#p3` | `document` | `met` | — | §2 L157: "Informative only. Named in illustrative material about what an Ad Decision Server typically emits (§6.7)." | — |
| `R11.1` | `document` | `met` | — | §2 L157: "No construct, obligation or behaviour in chapters 4 to 8 depends on VAST or on any VAST version." | VAST 4.x is named but not as required. |
| `R11.2` | `runtime` | `force-lost` | `5.a` | §6.7 L2654: "This leg is not defined by this specification." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R11.3` | `document` | `partial` | `5.a` | §2 L157, inside the table headed "## 2. Normative references": "IAB Tech Lab, Video Ad Serving Template (VAST) 4.x / Any 4.x / Informative only." | The two §6.7 references sit in a section that declares itself informative (L2656), which satisfies the criterion. The chapter-2 row does not: it is in a normative chapter, is not in an annex, and is flagged 'Informative only' rather than as illustrative. Closed by T5. |
| `R18.1` | `document` | `met` | — | §5.1 L1185 table gives the event URL per family; §5.2 defines both resolution-document shapes; §5.8 defines the request. | source-has-no-modal (A-7). |
| `R18.2` | `scope` | `met` | — | §1.2 L105: "The request the Ad Presentation Server makes of it, and the format of the decision it returns, are agreed between those two parties and are not defined here (§6.7)." | source-has-no-modal (A-7). |
| `R29.1` | `document` | `met` | — | §5.8.2 L2420: "The parameters are inputs about the device - statements of what it supports - and not conclusions about which ad experiences can be served. Deriving the second from the first is the APS’s work." | source-has-no-modal (A-7). The set is three parameters, §5.8.2 L2424. |
| `R29.2` | `runtime` | `met` | — | §5.8.3 L2456: "Sending a reserved parameter is optional. A conformant Player sends all of them, some of them, or none." | The source states OPTIONAL and MAY; the spec writes lowercase 'optional'. A permission loses less than an obligation, so this is not force-lost, but T1 covers it. |
| `R29.3` | `runtime` | `force-lost` | `5.a` | §4.6.22 L988: "A parameter whose value the Player does not have, or does not disclose, is omitted entirely rather than sent empty" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R29.4` | `runtime` | `force-lost` | `5.a` | §4.6.22 L990: "a parameter the Player attaches that is not one of the reserved names carries a vendor-specific prefix, so that reserved names added in a later edition stay free." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R29.5` | `runtime` | `force-lost` | `5.a` | §4.5.9 L629: "The APS produces candidates for a resolution request that carries none of the reserved capability parameters of §5.8.2." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R29.6` | `document` | `met` | — | §5.8.2 L2439 table: each of the five classes of §3.4 has a distinct triple of sgaiVideoDecoders / sgaiImageOverlay / sgaiHtmlOverlay values. | The acceptance test the criterion states is run in the document itself. |
| `R29.7` | `document` | `met` | — | §5.8.4 L2471: "A reserved parameter absent from the resolution request means its value is undetermined: the Player did not determine it, or did not disclose it. Absence does not assert that the device lacks the capability." | source-has-no-modal (A-7). |
| `R4#p1` | `runtime` | `force-lost` | `5.a` | §4.6.4 L687: "the Player stops rendering once the cumulative duration would exceed it, even when the stop falls mid-ad" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R4.1` | `runtime` | `force-lost` | `5.a` | §4.3.2 L467: "Every ad slot the MPD declares, linear or non-linear, carries @maxDuration." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. §5.1.1 L1225 marks @maxDuration 'optional in the base schema; required under this specification'. |
| `R4.2` | `runtime` | `force-lost` | `5.a` | §4.6.4 L687: "Where the cap bounds cumulative duration the Player stops rendering once the cumulative duration would exceed it, even when the stop falls mid-ad" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. The families the spec assigns to cumulative duration are overlay and linear insertion, not 'the non-linear families' the criterion names: the pause family is excluded (A-1). |
| `R4.3` | `runtime` | `force-lost` | `5.a` | §4.6.4 L677 table, Linear replacement row: "With @clip at its default true the alternative presentation shall terminate at the latest at time PRT + APDmax" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R4.4` | `scope` | `met` | — | §4.4.3 L555: "The slot cap is not the ADS’s to respect. A conformance check on an ADS passes even when the cumulative duration of the candidates it returned exceeds the slot cap." | A declared non-obligation; question 2 does not apply. |
| `R4.5` | `runtime` | `force-lost` | `5.a` | §4.6.4 L688: "it enforces against actual rendered length rather than declared length" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R4.6` | `runtime` | `force-lost` | `5.a` | §4.6.4 L677: "the end the Publisher scheduled, whatever time the event actually fired, so a late start shortens the ad rather than moving the end." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R4.7` | `runtime` | `met` | — | §4.3.2 L479: "A declared cap of zero means the opportunity does not fire, which is the base specification’s own rule. A zero cap is not a very short slot." | source-has-no-modal (A-7). What a zero cap means on a pause window, where the cap bounds one ad rather than the slot, is not stated (EC-5). |
| `R4.8` | `scope` | `met` | — | §4.3.2 L470: "This is a deliberate narrowing of the base specification, which treats an absent value as unbounded. The narrowing restricts which documents conform and changes no construct’s semantics, which is what a profile-style restriction does." | source-has-no-modal (A-7). |
| `R4.9` | `runtime` | `force-lost` | `5.a` | §4.6.4 L696: "The Player converts the candidate’s duration into the cap’s timescale before comparing, rounding the converted value up to the next whole unit. A candidate whose converted duration equals the cap exactly is admitted." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R4.10` | `runtime` | `force-lost` | `5.a` | §4.6.4 L708: "A slot declaration carrying no @maxDuration is not a slot this specification defines. The Player presents no ad from such a slot and continues with the primary content." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. The provisional status the criterion requires is carried at §4.6.4 L714 and in the Open points table L7633. |
| `R4.11` | `runtime` | `met` | — | §4.6.4 L703: "Cap arithmetic runs on the presentation timeline, so an interval during which that timeline does not advance does not accrue against the cap: a form suspended while the viewer is paused resumes with the remaining cap it had when it was suspended." | source-has-no-modal (A-7). |
| `R31.1` | `runtime` | `force-lost` | `5.a` | §4.6.2 L662: "For a pause-trigger window the Player issues the request when a viewer pause begins inside the window; a pause that begins outside every such window produces no request." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R31.2` | `runtime` | `force-lost` | `5.a` | §4.6.4 L680 table, Pause row: "Nothing. A pause slot’s duration is set by the viewer (§4.6.10). @maxDuration on a pause-trigger window bounds the display duration of a single pause ad before automatic dismissal." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. The third meaning the spec gives the pause cap comes from UC-05 Publisher intent, not from R4 or R31 (A-1). |
| `R12.1` | `document` | `met` | — | §3.2 L299 table maps each of the nine accepted tokens to an IAB ad type and visual placement; §2 L156 cites "IAB Tech Lab, Ad Format Guidelines for Digital Video and CTV" as the source of that vocabulary. | §5.3.3 L1841: 'The admissible values are exactly the tokens of §3.2.' |
| `R12.2` | `runtime` | `force-lost` | `5.a` | §4.3.3 L484: "Each token in a slot’s @allowedLayouts is one of the tokens of §3.2, each of which maps one-to-one to an IAB-defined ad type or visual placement." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R12.3` | `runtime` | `force-lost` | `5.a` | §4.5.4 L595: "Every presentation option’s @layout is a token of §3.2, and every creative carries a media type inside the admissible set of §3.3." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R12.4` | `document` | `met` | — | §3.2 L322: "Each token carries the IAB’s spatial bound by reference. This specification inherits those bounds from the IAB guidelines rather than restating them, and declares no dimensional attribute on the slot or on a presentation option." | source-has-no-modal (A-7). |
| `R15.1` | `document` | `met` | — | §3.3 L340: "Exactly three creative-carrier forms are admissible"; L350: "A carrier outside these three - a raw script, a vector image as payload, a document format, a proprietary binary - is out of scope, and no annex, example or implementation note in this document adds one." | Verified: no fourth carrier appears in the annexes. |
| `R15.2` | `runtime` | `force-lost` | `5.a` | §4.5.4 L595: "every creative carries a media type inside the admissible set of §3.3." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R15.3` | `runtime` | `met` | — | §4.6.20 L975: "The Player MAY skip such a candidate and fall through as in §4.6.6" | One of the six MAY occurrences in chapter 4; the source modal is MAY and it survives. |
| `R5#p1` | `runtime` | `force-lost` | `5.a` | §4.6.5 L721: "the Player evaluates the options in document order and renders the first whose form and layout it can satisfy on its device and whose layout the window admits." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R5#p2` | `runtime` | `force-lost` | `5.a` | §4.6.6 L728: "A candidate with no satisfiable option is skipped and the Player advances to the next candidate in the resolution document." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R5#p3` | `runtime` | `force-lost` | `5.a` | §4.6.3 L666: "the Player checks each presentation option against (a) what its device can satisfy and (b) the @allowedLayouts of the window that served the candidate." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R5.1` | `runtime` | `force-lost` | `5.a` | §4.5.3 L583: "Each candidate carries one or more presentation options as an ordered list whose document order is the preference order. How many a candidate carries is the APS’s decision: no maximum, and no minimum beyond one." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R5.2` | `runtime` | `force-lost` | `5.a` | §4.6.5 L721: "For an accepted candidate the Player evaluates the options in document order and renders the first whose form and layout it can satisfy" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R5.3` | `runtime` | `force-lost` | `5.a` | §4.6.6 L730: "Only once every candidate is exhausted does the Player continue with the primary content." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R5.4` | `scope` | `partial` | `5.a` | §4.4.4 L560: "A device-capability view is optional. Producing candidates requires no device-class matrix and no per-Player capability view at the ADS. An implementation that holds one is equally conformant." | The criterion binds the ADS and the APS. The statement is made for the ADS only; §4.5 places no equivalent on the APS, and §4.5.9 speaks about tolerating an absent parameter rather than about holding a device view. Closed by T4. |
| `R5.5` | `runtime` | `met` | — | §5.3.5 L1886: "Carrying several options is the form this specification asks for"; §4.5.3 L590: "Carrying exactly one is equally admissible" | Source modal is MAY; permission preserved. |
| `R5.6` | `runtime` | `force-lost` | `5.a` | §4.6.5 L724: "An option that fails either check is passed over and the Player moves to the next option in document order. The Player renders no form its device cannot render." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R5.7` | `runtime` | `force-lost` | `5.a` | §4.6.6 L728: "A candidate with no satisfiable option is skipped and the Player advances to the next candidate in the resolution document." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R7#p1` | `runtime` | `force-lost` | `5.a` | §4.6.7 L736: "The Player presents the candidates in the order the resolution document declares." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R7#p2` | `runtime` | `force-lost` | `5.a` | §4.6.7 L740: "the candidates that survive are presented in the order the document declared them, without reordering, deduplication or rearrangement." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R7.1` | `runtime` | `force-lost` | `5.a` | §4.6.7 L736: "The Player presents the candidates in the order the resolution document declares." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R7.2` | `runtime` | `met` | — | §4.6.7 L738: "It MAY drop a candidate that has no satisfiable option or whose declared duration would overrun the cap" | Source modal MAY; preserved. |
| `R7.3` | `runtime` | `met` | — | §4.6.4 L691: "The Player MAY additionally drop a candidate before playback when its declared duration alone would push the cumulative duration past the cap." | Source modal MAY; preserved. |
| `R7.4` | `runtime` | `force-lost` | `5.a` | §4.6.7 L740: "without reordering, deduplication or rearrangement." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R7.5` | `runtime` | `force-lost` | `5.a` | §4.6.4 L692: "drop-before-play on declared duration is permitted, trim-during-play on actual length is required." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. 'is required' is the closest chapter 4 comes to a modal, and it is not one of the RFC 2119 keywords §0 declares. |
| `R30.1` | `runtime` | `force-lost` | `5.a` | §4.5.7 L617: "An opportunity that resolved with no ads is answered with a well-formed, complete resolution document carrying no candidates (§5.2.3), served with 200 and a body." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R30.2` | `runtime` | `force-lost` | `5.a` | §4.6.8 L797: "An empty resolution does not consume the opportunity."; §8.1 E4 L2908: "do not count the attempt as an execution, so an @executeOnce=“true” slot stays executable" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R3.1` | `document` | `met` | — | §3.4 L363 enumerates D1..D5 by decoder count and surface type; §5.3.7.3 L1971 gives the satisfiable classes for every layout-and-form pair; §7.5 and Annexes A-N walk each scenario per class. | — |
| `R3.2` | `runtime` | `force-lost` | `5.a` | §5.3.7.3 L1971 table, Satisfiable on column, gives a defined outcome for every class on every layout; §4.6.6 L728 defines the skip path. | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R3.3` | `runtime` | `force-lost` | `5.a` | §4.6.5 L726: "The Player renders no form its device cannot render." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R16.1` | `runtime` | `force-lost` | `5.a` | §4.6.10 L840: "On the pause-to-play transition the Player removes any rendered pause-ad form from the screen within one rendering frame" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R16.2` | `runtime` | `force-lost` | `5.a` | §4.6.10 L841: "and stops firing beacons scheduled for it; beacons scheduled at relative times after the transition fall outside the pause ad’s active window." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R32.1` | `runtime` | `force-lost` | `5.a` | §4.5.10 L636: "A resolution document for a pause slot declares which of repeat, request-again and stop applies when the candidates run out while the viewer is still paused. Absent the declaration the Player applies stop." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R32.2` | `runtime` | `force-lost` | `5.a` | §4.6.11 L867: "Under request-again a resolution document carrying no candidates is treated as stop for the remainder of that pause." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R32.3` | `runtime` | `force-lost` | `5.a` | §4.6.11 L872: "When the viewer resumes, the Player returns to the primary content immediately, whether or not an ad is mid-presentation." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R32.4` | `scope` | `gap` | `5.a` | — (nothing in the spec to quote in either direction) | The specification body nowhere declares this question out of scope. The sentence exists only in the Open points table at L7638, inside a block the document opens by saying at L7511: “This block is not part of the specification.” A scope declaration that lives outside the specification is not a scope declaration the specification makes. See G-2. |
| `R34.1` | `runtime` | `met` | — | §5.1.4.1 L1413: @executeOnce is Required=no, default false, "When true, the window yields at most one pause ad for the session" | Source modal MAY; the optionality is carried by the schema default. |
| `R34.2` | `runtime` | `force-lost` | `5.a` | §4.6.12 L875: "On a pause-trigger window declared @executeOnce=“true” the Player presents at most one pause ad for that window for the duration of the session, and a later qualifying pause inside the same window leaves the primary content uninterrupted." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. Its interaction with repeat and request-again (§4.6.11) is undefined: see EC-1. |
| `R34.3` | `runtime` | `met` | — | §4.6.12 L879: "The window is consumed when a pause ad begins rendering, not when the pause occurs: a pause that resolves to no renderable candidate leaves the window available." | source-has-no-modal (A-7). |
| `R34.4` | `document` | `met` | — | §5.1.4.1 L1415: "Why @executeOnce carries the baseline name. The capability is the pause family’s counterpart of the single-execution bound the base specification gives a timeline event." | source-has-no-modal (A-7). |
| `R19#p1` | `runtime` | `force-lost` | `5.a` | §4.6.14 L902: "Every ad form, linear or non-linear, is rendered at the speed the primary content is playing at the moment the ad is presented" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R19.1` | `runtime` | `force-lost` | `5.a` | §4.6.14 L902: "Every ad form, linear or non-linear, is rendered at the speed the primary content is playing at the moment the ad is presented" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R19.2` | `runtime` | `force-lost` | `5.a` | §4.6.14 L904: "the Player does not force an ad to 1x while the primary content runs at another speed." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R19.3` | `runtime` | `force-lost` | `5.a` | §4.6.14 L908: "The Player derives the wall-clock on-screen length as duration / playback_speed - a 10-second form at 2x is on screen for five seconds - while cap enforcement and beacon scheduling operate on the presentation-timeline duration" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R19.4` | `runtime` | `force-lost` | `5.a` | §4.6.14 L906: "A form’s declared duration is a value on the presentation timeline for every form, including image and html, which have no intrinsic media." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R21.1` | `runtime` | `force-lost` | `5.a` | §4.6.10 L846: "A pause ad MAY be presented fullscreen, occupying the whole screen surface, or as a partial overlay composited over the paused primary frame" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. The two MAY halves survive; the MUST half - keeping at most one non-linear form active during a partial pause ad - is stated in the indicative at §4.6.13 L897. |
| `R25#p1` | `runtime` | `force-lost` | `5.a` | §4.6.17 L937: "the Player keeps its presentation time frozen inside that window for the duration of the pause, even though the live edge keeps advancing in wall-clock time" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R25.1` | `runtime` | `force-lost` | `5.a` | §4.6.17 L943: "A decision to resume at the live edge is a Player action occurring after the resume from pause, outside the pause-ad window." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. §4.6.17 L947 adds a time-shift-buffer bound the criterion does not contemplate; it narrows rather than contradicts (EC-4). |
| `R26.1` | `runtime` | `force-lost` | `5.a` | §5.3.7.2 L1942: "It is a composition attribute of the layout rather than one of the candidate’s alternative presentation options: the Player does not walk it the way it walks the options, it composites it as part of rendering the layout once that layout is chosen." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. Reversal of a prior verdict: the earlier build read the <svta:BackgroundElement> placement inside <svta:RenderableAsset> as a contradiction. It is not. R26.1 forbids the background element being a separate presentation option, and it is not one; the spec argues the point explicitly, and UC-10 Notes use the same words. The criterion’s phrase 'slot / layout' is what made the two readings possible (A-4). |
| `R26.2` | `runtime` | `force-lost` | `5.a` | §4.6.19 L969: "For a side-by-side / double box it composites the shrunk primary content and the ad as the two boxes; where the advertiser supplied a background element it places it in the uncovered bands, and where none was supplied the uncovered region renders as black." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R26.3` | `runtime` | `force-lost` | `5.a` | §5.3.7.3 L1982 table: "squeezeback-double-box-with-background / video / 2 (primary + ad) / image surface for the background / D1" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. The element-type reasoning the criterion requires is stated at §5.3.7.3 L1996. |
| `R27.1` | `runtime` | `force-lost` | `5.a` | §5.3.7.1 L1911: "The L-shape has one ad creative - a single URL carrying an image, a video or an HTML creative - and that creative is always placed full-frame in the background." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R27.2` | `runtime` | `force-lost` | `5.a` | §4.6.19 L966: "For an L-shape the Player composites the two elements - the full-frame ad creative in the background and the shrunk primary content on top of it - with the ad creative covering the whole frame." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R27.3` | `runtime` | `force-lost` | `5.a` | §5.3.7.3 L1976 table rows for squeezeback-l-shape: video -> D1, D2; image -> D1, D3, D4; html -> D1, D3 | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R14.1` | `runtime` | `force-lost` | `5.a` | §4.6.7 L750: "Within a non-linear slot, candidates are presented one after another in declared order, each starting when the previous ends" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R14.2` | `runtime` | `force-lost` | `5.a` | §4.6.7 L751: "and the cap is enforced against the cumulative duration of that sequence." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. The criterion says the cap is enforced against 'the slot’s opportunity window'; the spec enforces @maxDuration and never the window’s own <Event>@duration (EC-6). |
| `R14.3` | `document` | `met` | — | §5.1.3.1 L1351: "This specification declares no maximum-concurrency attribute on the slot."; §4.6.7 L743: "At any instant at most one non-linear form is active on the screen." | No construct in §5 implies parallel rendering. |
| `R17.1` | `runtime` | `met` | — | §4.6.13 L890: "An active overlay is suspended for the duration of the pause" | source-has-no-modal (A-7). |
| `R17.2` | `runtime` | `met` | — | §4.6.13 L890: "and restored on resume if its own window is still open" | source-has-no-modal (A-7). |
| `R17.3` | `runtime` | `met` | — | §4.6.13 L891: "where the overlay window expired during the pause, the Player leaves the overlay surface clear on resume." | source-has-no-modal (A-7). |
| `R17.4` | `document` | `met` | — | §4.6.13 L900: "This specification carries no construct that lets the Publisher, the ADS or the APS invert it." | source-has-no-modal (A-7). |
| `R17.5` | `runtime` | `met` | — | §4.6.13 L894: "A linear ad occupying the screen is suspended and resumed from where it stopped when the viewer resumes." | source-has-no-modal (A-7). |
| `R20.1` | `runtime` | `force-lost` | `5.a` | §4.6.8 L757: "An attempt on a window that produces no ad is a failed execution, and on a failed execution the Player attempts the next overlapping window of the same family." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. All four failure conditions the criterion enumerates are carried at §4.6.8 L771-779. |
| `R20.2` | `runtime` | `force-lost` | `5.a` | §4.3.4 L490: "All the opportunity windows of one family that share a <Period> are authored as <Event> entries inside a single <EventStream>." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R20.3` | `runtime` | `met` | — | §4.6.9 L811: "Order overlapping windows by presentation time, oldest first. Where two windows carry the same presentation time, the Player takes them in the order they appear inside the <EventStream>." | source-has-no-modal (A-7). The not-document-order clarification is at L819. |
| `R20.4` | `runtime` | `force-lost` | `5.a` | §4.6.8 L806: "A resolution document whose family does not match the slot that requested it is a failure to resolve, and the Player continues down the chain." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R20.5` | `runtime` | `met` | — | §4.6.9 L828: "Each window in a chain binds the candidates it serves with its own allowed layouts and its own cap. A window does not inherit the declarations of the window it stands in for." | source-has-no-modal (A-7). |
| `R20.6` | `document` | `partial` | `5.a` | §4.6.9 L828: "Each window in a chain binds the candidates it serves with its own allowed layouts and its own cap." | Half of the change of status the criterion demands is made: the rule now sits in chapter 4 under Player obligations rather than in informative material. The other half is not: it carries no normative modal, so a reader applying the RFC 2119 convention the document declares at L9 finds a description. This is the one criterion that names the defect G-1 generalises. Closed by T1. |
| `R22.1` | `runtime` | `force-lost` | `5.a` | §4.6.7 L743: "At any instant at most one non-linear form is active on the screen. Sequenced forms - one ending, the next beginning - are in scope; two forms on screen at the same instant are not." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. The decoder-budget rationale the criterion states is at L746. |
| `R6#p1` | `document` | `met` | — | §5.5 L2066: "Timeline-scheduled beacons - impression, start, quartiles, complete - are carried as <Event> entries inside an <EventStream> of scheme urn:mpeg:dash:event:callback:2015" | §5.5.1 fixes the shape, §5.5.2 the placement, §5.5.3 the timebase. |
| `R6#p2` | `runtime` | `force-lost` | `5.a` | §4.6.21 L981: "An event scheme URI, an extension element or a foreign namespace the Player does not implement is ignored together with its whole subtree, and the primary content continues uninterrupted." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R6.1` | `document` | `met` | — | §5.5 L2068 and §5.5.1 L2084 give the carrier shape, its three EventStream attributes and its two Event attributes. | — |
| `R6.2` | `runtime` | `met` | — | §4.5.6 L604: "Beacons are <Event> entries inside an <EventStream> of scheme urn:mpeg:dash:event:callback:2015, with presentation times on the ad’s own presentation timeline (§5.5)." | The source modal is SHOULD and the spec states the carrier flatly, which is stronger rather than weaker. Whether the APS retains the SHOULD-level freedom the criterion grants is what R6.2, R13.1 and R13.4 disagree about (A-5). |
| `R6.3` | `document` | `met` | — | §5.5 L2073: "Why the callback scheme is reused as it stands. Nothing in it needed extending for ads, and a parallel scheme would have split tracking across two carriers for no semantic gain." | Source modal MAY; no new carrier is introduced, so the condition never arises. |
| `R6.4` | `runtime` | `force-lost` | `5.a` | §4.6.21 L981: "An event scheme URI, an extension element or a foreign namespace the Player does not implement is ignored together with its whole subtree" | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R6.5` | `runtime` | `force-lost` | `5.a` | §4.6.15 L920: "De-duplication is scoped to the candidate that carries the beacons. Two beacons carrying the same @id in two different candidates of one resolution document are two distinct beacons and the Player fires both." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R6.6` | `runtime` | `met` | — | §4.6.15 L924: "Where the beacon carrier sits inside a candidate rather than in a <Period>, its presentation times resolve against that candidate’s own presentation." | source-has-no-modal (A-7). |
| `R6.7` | `document` | `met` | — | §5.5.2 L2136 note: "A validation procedure that reports such a document valid while skipping the foreign-namespace subtree has not checked the tracking carrier at all. Tooling implementing this specification scans inside <svta:Candidate> as well, and a validation report states which of the two it did." | Reinforced by §8.8 L3054 and by test T-D3 at L7470. |
| `R13#p1` | `document` | `met` | — | §5.5 L2066 defines the carrier and §5.5.3 L2152 the timebase: "Every <Event>@presentationTime inside a resolution document is expressed relative to the start of the ad’s own presentation." | — |
| `R13.1` | `runtime` | `force-lost` | `5.a` | §4.5.6 L604: "Beacons are <Event> entries inside an <EventStream> of scheme urn:mpeg:dash:event:callback:2015, with presentation times on the ad’s own presentation timeline." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. The criterion’s alternative - 'or an equivalent baseline DASH construct' - is dropped with no stated reason, which R8.2 asks for (G-5). |
| `R13.2` | `runtime` | `force-lost` | `5.a` | §4.6.15 L914: "For an accepted candidate the Player fires each beacon at its scheduled relative time, preserving the ADS’s authority over the schedule." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R13.3` | `runtime` | `force-lost` | `5.a` | §4.6.15 L916: "Where the cap trims the ad before a scheduled beacon’s time, the Player stops firing the remaining beacons at the trim boundary." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R13.4` | `document` | `met` | — | §5.5 L2071: "This specification introduces no tracking scheme of its own." | Verified against §2.1: the two scheme URIs this edition mints are opportunity-declaration schemes, not tracking schemes. |
| `R13.5` | `runtime` | `met` | — | §4.5.6 L610: "Whether the transcription is faithful - that no beacon was added, dropped or reordered - is part of the contract the APS and the ADS maintain directly." | source-has-no-modal (A-7). |
| `R23.1` | `document` | `met` | — | §5.7 L2245 defines <svta:AdSystem>, <svta:AdTitle>, <svta:Advertiser> and <svta:UniversalAdId> in the SVTA namespace, and L2254: "This carrier is optional on both ends by design: nothing obliges an APS to emit it or a Player to read it." | — |
| `R24#p1` | `runtime` | `force-lost` | `5.a` | §4.7.2 L1018: "The media axis is closed, and that is why non-audiovisual creatives ride elsewhere." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R24#p2` | `runtime` | `force-lost` | `5.a` | §4.5.5 L599: "The URL of an image or html creative travels on the carrier of §5.3.2." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R24.1` | `runtime` | `force-lost` | `5.a` | §5.3.2 L1811 table: "(a) Foreign-namespace open content: the URL as an attribute on a new element / DASH §5.2.1 / Selected." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. §4.7.2 L1040 additionally rules out the application/mp4 wrapper workaround. |
| `R33.1` | `document` | `met` | — | §5.9 L2500: "This specification defines no metric of its own for it. The quantity is derived from the PlayList metric of DASH Annex D.4.6." | — |
| `R33.2` | `runtime` | `force-lost` | `5.a` | §4.6.18 L961: "A Player that reports metrics derives the paused interval from the PlayList entries as §5.9 describes, and counts no playback period that stopped on Rebuffering as a pause opportunity." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R33.3` | `scope` | `met` | — | §5.9 L2535: "How a measurement reaches anyone is out of scope, and the base specification takes the same position about its own metrics." | source-has-no-modal (A-7). |
| `R33.4` | `runtime` | `force-lost` | `5.a` | §4.3.8 L516: "Content carrying pause-trigger windows requests the PlayList metric through the base specification’s Metrics element (§5.9)." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R28#p1` | `runtime` | `force-lost` | `5.a` | §5.6 L2170: "The resolution document carries the ad’s ClickThrough URL and its associated click-tracking URLs in a single normative carrier, so that every Player conformant to this specification reads them the same way." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R28.1` | `runtime` | `force-lost` | `5.a` | §4.5.8 L622: "When a candidate carries a ClickThrough, its URL and any click-tracking URLs accompanying it travel together in the carrier of §5.6." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R28.2` | `runtime` | `force-lost` | `5.a` | §4.6.16 L931: "A Player conformant to this specification reads the ClickThrough URL from the carrier of §5.6 and, when the viewer activates the ClickThrough, opens or hands off the destination and fires each accompanying click-tracking URL once." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `R28.3` | `runtime` | `met` | — | §4.5.8 L626: "Whether a ClickThrough the ADS declared reaches the document at all is, like beacon fidelity, an APS-to-ADS matter." | source-has-no-modal (A-7). |
| `R8.1` | `document` | `met` | — | §5 L1174: "Every new construct states inline why an existing construct of the base specification was not reused"; §5.1.3 L1281, §5.3 L1748, §5.6 L2176 and §5.8.2 L2400 each carry that justification. | <svta:BackgroundElement> (§5.3.7.2) and <svta:ClickTracking> (§5.6.1) carry no justification of their own; each is a sub-part of a construct whose justification is given. |
| `R8.2` | `document` | `met` | — | §5.1.6 L1464: "Considered and not reused."; §5.3.2 L1816: "Why neither descriptor."; §5.2.2.2 L1637 records why MPD@type=list was declined. | One omission is undocumented: R13.1’s 'equivalent baseline DASH construct' alternative (G-5). |
| `R9.1` | `document` | `met` | — | §5.1 L1197: "Why the event stream, and not a container of our own."; §5.2.1 L1482 reuses DASH §8.14; §5.5 L2073 reuses the callback scheme; §5.4 L2022 reuses the SPS profile. | — |
| `R9.2` | `document` | `met` | — | §5.1.3 L1287: "Three constructs elsewhere come close enough to be weighed, and each is rejected for a stated reason"; §5.3 L1751 weighs Preselection, @selectionPriority and the fallback scheme. | — |
| `R9.3` | `document` | `met` | — | §5.1.3 L1289 weighs the supplementary video descriptor, DASH Annex H SRD and DASH Annex L; §5.3.2 L1809 weighs four DASH-conformant carriers and records which was selected. | — |
| `R10.1` | `document` | `met` | — | §1.2 L100: "A layout engine. Spatial arrangement inside a layout is delegated to HTML5 and CSS, and the layout vocabulary is the IAB’s." | The delegation appears only in the scope chapter; §4.6.19 and §5.3.7 compose layouts without naming HTML5/CSS. Question 1 is satisfied. |
| `R10.2` | `document` | `met` | — | §1.2 L102: "This specification declares no positioning attribute, no coordinate model and no dimensional cap of its own" | — |
| `R10.3` | `scope` | `met` | — | §1.2 L103: "where an ad sits inside its layout follows from the IAB ad type the layout token names (§3.2)." | source-has-no-modal (A-7). |
| `OOS-1#p1` | `document` | `met` | — | §1.2 L102: "This specification declares no positioning attribute, no coordinate model and no dimensional cap of its own" | — |
| `OOS-4#p1` | `runtime` | `force-lost` | `5.a` | §1.2 L116: "A scripted creative is wrapped in an HTML document rather than delivered as a script." | Chapter 4 states this substance in the indicative; no RFC 2119 modal appears anywhere in chapters 4-8 (G-1). Closed by T1. |
| `UC-01` | `use-case` | `met` | — | §7.5.1 L2777 and Annex A. A.6 L3299-3318 walks D1, D2, D3, D4 and D5; each class renders the video form on one decoder reused sequentially, which is the outcome UC-01 states for all five. | Publisher intent 'non-linear forms not allowed' needs no construct: a linear slot resolves to a ListMPD, which §5.3.3 L1847 says carries the linear layout as 'the only form'. |
| `UC-02` | `use-case` | `met` | — | §7.5.1 L2777 and Annex B. B.6 L3532-3550 walks all five classes. The trick-play variant is carried at §4.6.14 L908: "a 10-second form at 2x is on screen for five seconds". | — |
| `UC-03` | `use-case` | `met` | — | §7.5.3 L2796 and Annex C. C.6 L3819-3890 walks all five: "D1 takes the richest option on offer, D2 takes a video overlay and declines every non-video surface, D3 takes HTML or image, D4 takes image, and D5 declines the opportunity" (§7.5.3 L2801). | Two Publisher-intent items of UC-03 have no construct: the concurrency cap, declined on purpose at §5.1.3.1 L1351, and the layout names 'banner' and 'sidebar', which are outside the closed set of §3.2 (A-2). |
| `UC-04` | `use-case` | `met` | — | §7.5.4 L2808 and Annex D. D.6 L4162-4220 walks all five. The one-decoder arithmetic UC-04 corrected is carried at §7.5.4 L2816: "The linear ad occupies the surface but does not consume a second decoder: it replaces the primary content on the one decoder rather than joining it." | UC-04’s open question - whether the Publisher can link the two portions of a break - is answered at §5.1.5 L1451: 'This specification defines no construct that links the two portions.' |
| `UC-05` | `use-case` | `met` | — | §7.5.5 L2820 and Annex E. E.6 L4491-4537 walks all five; E.7 L4538 is the live variant and §4.6.17 L937 carries the freeze. | UC-05’s two open questions are answered: speculative-versus-lazy resolution at §8.5 L3014, and decoder re-tasking on a single-decoder class at §5.3.7.3 L1985 with the conservative posture at §8.4 L2995. |
| `UC-06` | `use-case` | `met` | — | §7.5.2 L2788 and Annex F. F.6 L4814-4831 walks all five; F.7 L4832 works the cap arithmetic. | — |
| `UC-07` | `use-case` | `met` | — | §7.5.8 L2866 and Annex G. G.7 L5150: "Behaviour is identical on D1 through D5, because what determines it is the Player’s vintage and the content type, not the device’s decoder or surface budget." | Matches UC-07, which states the behaviour does not vary by class. The live-versus-VOD split is at §4.7.7 L1132 and G.6 L5061. |
| `UC-08` | `use-case` | `met` | — | §7.5.7 L2857 and Annex H. H.6 L5516-5575 walks all five, including D5 where neither surface renders. | — |
| `UC-09` | `use-case` | `met` | — | Annex I. I.4 L5736-5774 walks all five against the same four-option ordered list: D1 to option 1, D2 to option 4, D3 and D4 to option 2, D5 to option 4. | The three-outcome emergence UC-09 demonstrates is reproduced, including the D2 element-type contrast at §5.3.7.3 L1996. |
| `UC-10` | `use-case` | `met` | — | Annex J. J.6 L6102-6155 walks all five; J.7 L6156 is the D2 explanation. | The background element is a composition attribute of the layout and not a fourth option, §5.3.7.2 L1942. |
| `UC-11` | `use-case` | `met` | — | Annex K. K.8 L6377: "The outcome does not vary across D1 to D5. All five read the same carrier, open the same destination and fire the same click-tracking URLs." | Matches UC-11, which states device class does not change the behaviour. The legacy-inert case is at K.7 L6367. |
| `UC-12` | `use-case` | `met` | — | §7.5.6 L2841 and Annex L. L.9 L6719: "Which window is served does not vary across D1 to D5." L.4, L.5 and L.6 walk the three paths UC-12 enumerates. | UC-12’s central point - an empty document is a failed execution and the chain continues - is carried at §4.6.8 L778 and §8.1 E4. |
| `UC-13` | `use-case` | `met` | — | Annex M. M.3 to M.7, L6811-7086, walk D1 to D5, each declaring a different subset and receiving a different narrowed document; M.6 L6967 is the D4 case that declares nothing and receives all four options. | M.8 L7087 states the identical-outcome conclusion UC-13 demonstrates. |
| `UC-14` | `use-case` | `met` | — | §7.5.9 L2873 and Annex N. N.8 L7390-7405 walks all five over a replacement that is not advertising; N.6 L7354 does the decoder bookkeeping and N.7 L7377 separates the two portions. | NOTE: the prompt’s stated acceptance test for this step - that a correct walk reports UC-14 as gap - is stale against v8. UC-14 is walked in the spec body and in a dedicated annex. See the Method note. |

## Disposition of findings

Routed here: the 7 Gaps, 6 Edge cases and 7 Ambiguities of §1-§3, and every
coverage-map row of §4 whose verdict is not `met`.

**What is NOT routed, and why.** Items 3 and 4 of this step's routing
obligation — every `Non-conforming` and `Marginal` item of
`../output-analysis/v8-dash-conformance-audit.md`, and every flagged item of
`../output-analysis/v8-detail-review.md` — could not be routed because **neither
file exists**. `output-analysis/` contains only this sidecar. Both are produced
by Steps 7.5 and 8, which run *after* this step, so at the moment this step runs
there is nothing to route. This is a fixed ordering problem in the pipeline, not
an omission of this run: see the note at the end of §5.c.

| Bucket | Who closes it | Rows |
|--------|---------------|------|
| `5.a` | the pipeline — nobody has to decide anything | 5 TODOs, covering 85 coverage rows and 3 gaps |
| `5.b` | the owner of the specification | 8 |
| `5.c` | the owner, then a major build | 8 |

### 5.a Actionable TODOs (5)

| # | Finding ref | Criterion | Spec section | Concrete edit | Citation |
|---|-------------|-----------|--------------|---------------|----------|
| T1 | G-1; R20.6; and every `force-lost` row of §4: `R1#p2`, `R1.1`, `R1.4`, `R2.1`, `R2.2`, `R2.3`, `R11#p2`, `R11.2`, `R29.3`, `R29.4`, `R29.5`, `R4#p1`, `R4.1`, `R4.2`, `R4.3`, `R4.5`, `R4.6`, `R4.9`, `R4.10`, `R31.1`, `R31.2`, `R12.2`, `R12.3`, `R15.2`, `R5#p1`, `R5#p2`, `R5#p3`, `R5.1`, `R5.2`, `R5.3`, `R5.6`, `R5.7`, `R7#p1`, `R7#p2`, `R7.1`, `R7.4`, `R7.5`, `R30.1`, `R30.2`, `R3.2`, `R3.3`, `R16.1`, `R16.2`, `R32.1`, `R32.2`, `R32.3`, `R34.2`, `R19#p1`, `R19.1`, `R19.2`, `R19.3`, `R19.4`, `R21.1`, `R25#p1`, `R25.1`, `R26.1`, `R26.2`, `R26.3`, `R27.1`, `R27.2`, `R27.3`, `R14.1`, `R14.2`, `R20.1`, `R20.2`, `R20.4`, `R22.1`, `R6#p2`, `R6.4`, `R6.5`, `R13.1`, `R13.2`, `R13.3`, `R24#p1`, `R24#p2`, `R24.1`, `R33.2`, `R33.4`, `R28#p1`, `R28.1`, `R28.2`, `OOS-4#p1` | 1 (DP-X / R-X.Y violation cited by ID) and 3 (internal contradiction between two spec sites, one reading matching `context/`) | §4.3, §4.4, §4.5, §4.6 throughout; §8 L2894 | Insert the RFC 2119 modal each cited criterion states, at each location the coverage map quotes. Mechanically: in §4.3.x, §4.4.x, §4.5.x and §4.6.x replace the indicative verb with the criterion's own modal — §4.6.1 *the Player keeps* → *the Player MUST keep*; §4.6.5 *renders the first* → *MUST render the first*; §4.5.3 *Each candidate carries* → *Each candidate MUST carry*; and so on for each of the 82 rows, using the modal the source criterion states (MUST, MUST NOT, MAY, SHOULD) and not a stronger one. Leave the six existing `MAY` occurrences alone. The §8 L2894 sentence then becomes true rather than needing deletion. | DP-2 (*the normative modal stays*); R20.6 (*R20.5 MUST be carried as a normative Player obligation*); IETF RFC 2119, invoked by the spec at L9-12; `projects/sgai-for-mpeg-dash/CLAUDE.md` § *Tone for the spec and generated artefacts* |
| T2 | G-5 | 3 (two spec sites disagree; exactly one reading matches `context/`) | §5.1.3 L1277 | Qualify the blanket sentence. Replace *"composites the chosen form on or alongside the primary content, which keeps playing"* with *"composites the chosen form on or alongside the primary content, which keeps playing — except where the selected option's `@layout` is `linear`, the full-screen takeover of last resort, which replaces the primary content for the duration of the option and resumes it where it stopped (§5.3.7.3)."* | R5 / UC-09 option 4 (*"a linear-style video ad that replaces the primary content for the slot, played sequentially — primary stops, ad plays, primary resumes"*), which §5.3.3 L1847 and §5.3.7.3 L1991 already follow |
| T3 | G-2; `R32.4` | 1 (R-X.Y violation cited by ID) | §4.6.11 L873, and L7638 | Move the sentence into the specification. Append to §4.6.11, after *"whether or not an ad is mid-presentation"*: *"Whether a second resolution request inside one pause is the same opportunity or a new one is out of scope. The two readings are identical at the Player — it requests, it renders what arrives, and it stops on resume, in both — and differ only in accounting between the APS and the ADS, which this specification does not observe (§1.2)."* Leave the Open points row where it is; it then points at a statement the specification makes. This is a `gap` row and a gap is normally 5.b, because nothing is written and the remedy is authoring; it qualifies as 5.a only because the exact sentence already exists at L7638 and moves verbatim. If the owner judges that wording wrong, this becomes a 5.b. | R32.4 (*"Whether a second resolution request within one pause is the same opportunity or a new one is **out of scope**"*) |
| T4 | G-3; `R5.4` | 1 (R-X.Y violation cited by ID) | §4.5, after §4.5.9 L634 | Add one obligation, mirroring §4.4.4: *"**4.5.12 A device-capability view is optional.** Producing candidates requires no device-class matrix and no per-Player capability view at the APS either. An APS that holds one is equally conformant, and an APS that holds none answers every request (§4.5.9)."* Renumber nothing else; §4.5.11 stays. | R5.4 (*"**Neither** the ADS **nor the APS** MUST be required to maintain a device-class matrix or a per-Player capability view to produce candidates"*) |
| T5 | `R11.3` | 1 (R-X.Y violation cited by ID) | §2 L157 | Move the VAST row out of the normative-references table. Delete it from the table headed *2. Normative references* and add, after that table, a short block: *"**Informative references.** IAB Tech Lab, Video Ad Serving Template (VAST) 4.x — illustrative only. Named in §6.7 as an example of what an Ad Decision Server typically emits. No construct, obligation or behaviour in this document depends on VAST or on any VAST version."* | R11.3 (*"Any reference to VAST in the spec MUST be in an annex or in a non-normative note explicitly flagged as illustrative"*) |

Each TODO's Finding ref column carries the unit ids it closes, so `bin/check-promotable.py` routes them without re-deriving anything.

### 5.b Flagged for review (8)

| # | Finding ref | Spec section | Why uncertain | Resolutions considered |
|---|-------------|--------------|---------------|------------------------|
| F1 | EC-1 | §4.6.11 L854, §4.6.12 L875 | `@executeOnce="true"` and `repeat` are jointly unsatisfiable, and neither `context/` nor the spec ranks them. Whichever wins, some Publisher or APS declaration silently stops meaning what it says. | (a) `@executeOnce` bounds *windows consumed*, so `repeat` re-presents freely inside the one consumed pause — the window is spent either way, so this costs nothing and keeps both features. (b) `@executeOnce` bounds *pause ads rendered*, so `repeat` is inert on such a window. (c) Forbid the combination at authoring time and have a validator flag it. (a) reads best against §4.6.12's own *"consumed when a pause ad begins rendering"*, but it is a requirement-level call. |
| F2 | EC-2 | §5.1.3.1 L1338, §4.6.7 L750 | The word *presentation* does different work in the two sentences, and `context/` defines `@executeOnce` for the pause family only (R34), never for an overlay window. | (a) One *window execution*: all the document's candidates play, the window then never fires again. (b) One *rendered form*: the first candidate plays and the rest are dropped. (a) is the reading consistent with §4.6.7; (b) is what §5.1.3.1's wording suggests. |
| F3 | EC-3 | §5.5.2 L2126-2134 | The de-duplication keys R6.5 mandates are not well-defined across the two carrier placements §5.5.2 admits on one candidate. Fixing it means choosing a normalisation rule, which changes what a conformant Player fires. | (a) Compare presentation times after converting both to a common timebase, and scope `@id` uniqueness to the stream. (b) Make the two placements mutually exclusive on one candidate. (c) Declare the candidate-level stream authoritative and ignore the sub-MPD's. |
| F4 | EC-5; A-6 | §4.6.4 L672, §4.6.7 L750 | Whether a non-linear presentation may outlive the `<Event>@duration` that declared its window is a requirement-level question `context/` conflates (A-6), and the answer changes what a Publisher's window declaration means. | (a) The shorter of cap and window ends the slot. (b) The cap alone governs, and the window only gates when the opportunity may be resolved. The spec silently implements (b). |
| F5 | EC-6 | §5.1.5 L1438, §4.6.4 L677 | Pairing `@clip="false"` on a hybrid break's linear portion with the concurrent overlay's own window is not addressed anywhere, and extending the overlay would mean extending a window the Publisher declared. | (a) The overlay ends with its own window, and the linear ad finishes alone. (b) The overlay's remaining cap follows the extended presentation. (a) preserves the Publisher's declaration; (b) preserves the composition UC-04 describes. |
| F6 | G-6 | §4.3.2 L479, §4.6.4 L680 | Zero on a pause window has two readings because the attribute means something different there, and choosing one decides whether a resolution request is issued at all — which is observable at the APS and therefore a contract change. | (a) Zero means the window does not fire, uniform with every other family. (b) Zero means an unbounded pause ad, since the cap is not a slot bound there. (a) is the safer default and matches the base specification's own rule; it needs saying either way. |
| F7 | G-4 | §4.5.6 L604, §5.5 L2071 | The narrowing is probably right, but it depends on resolving A-5 in `context/` first; applying it here would settle a requirement-level disagreement inside the spec. | (a) Keep the narrowing and document the omission inline per R8.2. (b) Restore R13.1's alternative and say what an equivalent baseline construct would be. (a) once A-5 is resolved. |
| F8 | `R1.3`; A-3 | §4.3.2 L470, §4.6.4 L708, §5.5.1 L2109 | Whether the spec's two narrowings override base semantics is what R1.3 and R4.10 disagree about. The spec already flags the first as open; the second — callback `<Event>@id` from optional to required — is applied unremarked and nobody has weighed it. | (a) Both are profile-style narrowings, record the second as the first is recorded. (b) The `@maxDuration` one is an override and R4.10 should be withdrawn, which is the working-group question §4.6.4 L714 already raises. |

### 5.c Deferred to `context/` (8)

| # | Finding ref | `context/` file to edit | Suggested edit | Leverage rationale |
|---|-------------|-------------------------|----------------|--------------------|
| C1 | A-1 | `context/03-requirements.md` — R4.2 L352, R31.2 L442 | In R4.2 replace *"the non-linear families"* with *"the overlay family"*. In R31.2 append: *"On a pause slot the cap bounds the display duration of one pause ad before automatic dismissal, and not the slot."* | Highest. Two requirements contradict each other about the meaning of the attribute R4.1 makes mandatory on every slot, and the spec had to reach into a use case to find a third meaning. Every pause-family row of §4 rests on this. |
| C2 | A-5; G-4 | `context/03-requirements.md` — R6.2 L1450, R13.1 L1497, R13.4 L1512 | Raise R6.2's SHOULD to MUST and delete R13.1's *"(or an equivalent baseline DASH construct)"*, or say explicitly what an equivalent construct is. R13.4 already calls reuse mandatory. | Three requirements state three different forces for one rule. Until they agree, no spec text can be validated against them and G-4 cannot be closed either way. |
| C3 | A-2; G-7 | `context/04-use-cases.md` — UC-03 L290-296 | Replace the layout examples with tokens from R12 (`overlay-corner`, `squeezeback-l-shape`, `squeezeback-double-box`); drop the *"Maximum number of concurrent overlays"* bullet, pointing at R22.1. | UC-03 is the central non-linear scenario and is cited by UC-08, UC-09 and UC-10. It currently asks for one construct the spec refuses on principle and names two layouts outside the closed set. |
| C4 | A-4 | `context/03-requirements.md` — R26.1 L1045 | Replace *"a composition attribute of the slot / layout"* with *"a composition attribute of the layout that presents it"*. | One word closes a criterion that a prior pass of this step read as `contradicted` and this one reads as satisfied. A criterion two competent readers grade oppositely is measuring the reader. |
| C5 | A-3 | `context/03-requirements.md` — R1.3 L143 | Append: *"Requiring an attribute the base schema declares optional, and fixing the behaviour when it is absent, is a narrowing and not an override, provided the specification records it as such (R4.8)."* | R1.3 as written forbids what R4.10 mandates. The spec resolved it by writing its own divergence note; the requirement set should not need the spec to do that. |
| C6 | A-6; EC-5 | `context/03-requirements.md` — R14.2 L1169 | Replace *"would exceed the slot's opportunity window"* with *"would exceed the cap"*, and add a criterion saying whether a non-linear presentation may outlive the `<Event>@duration` that declared its window. | The cap and the window are two numbers a Publisher declares independently, and no requirement says which one ends an overlay. |
| C7 | EC-4 | `context/03-requirements.md` — R25.1 L1016 | Bound the freeze: *"…for the duration of the pause or until the time-shift buffer no longer contains the paused position, whichever is sooner."* | R25.1 promises something no Player can deliver. The spec found the bound and wrote it in (§4.6.17 L947); the requirement should carry it so the next build does not have to re-derive it. |
| C8 | A-7 | `context/03-requirements.md` — R17.1, R17.2, R17.3, R17.5, R20.3, R20.5 | Give each an RFC 2119 modal. They are Player obligations written in the indicative, which is the same defect G-1 reports in the output. | 23 of 123 criteria carry no modal, so question 2 of this step cannot be asked of them at all. Six of the 23 are plainly obligations and fixing those makes the map's force column mean something. |

**A ninth item belongs here and is not a `context/` edit, so it has no row.**
This step is obliged to route the DASH conformance audit's `Non-conforming` and
`Marginal` items and the detail review's flags, and it runs **before** either
sidecar exists — Steps 7.5 and 8 produce them afterwards. As the pipeline is
ordered today that obligation can never be met on a first pass, and the routing
either lands in the wrong sidecar or lands in a re-run of this step that nothing
schedules. The fix belongs in `prompts/build-all.prompt` or in
`prompts/3-post-spec/validate-spec.prompt`, not in `context/`, so it is reported
rather than routed.

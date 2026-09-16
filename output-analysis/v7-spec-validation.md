[GROUNDED_BY=notebooklm]

# Spec validation — v7 (2026-09-15)

Built against:
- spec: `../output/v7-sgai-spec.md` (4581 lines, 8 chapters + annexes A–N)
- `context/` at git SHA: `cb10ae1` (HEAD; last commit touching `context/` is `38e782f`; working tree clean for `context/`)
- `context-analysis/`: `dash-gap-analysis.md`, `uc-coverage-matrix.md`,
  `error-semantics.md`, `conformance-assertions.md`, `iab-ad-templates.md`
  (all modified-but-uncommitted at time of validation)

Grounding: two MPEG-DASH 6th edition claims that findings below depend on were
verified against the authoritative source through the `notebooklm` skill
(notebook `bb67e20c`), and are quoted verbatim where used — the
`@earliestResolutionTimeOffset` default (§5.16.5.2, Table 63) and the execution-failure
conditions of §5.16.2.2.6. Every other DASH claim in this document is taken from
`../context-analysis/dash-gap-analysis.md`, which is a declared input of this step;
full clause-by-clause grounding of the spec against the base specification is Step 8
(`audit-dash-conformance`), not this one.

**Finding count: 20** — Gaps 8, Edge cases 5, Ambiguities 7.
Disposition: §5.a **5**, §5.b **10**, §5.c **5**.

---

## Gaps (8)

### G-1 — The ClickThrough carrier has no normative placement on the linear path

- **Spec section that needs it**: §5.6 (`../output/v7-sgai-spec.md:1867`), §4.7.3.
- **What is missing**: §5.6 defines `<svta:Click>` and then fixes its placement in
  one sentence — *"The element is a child of `<svta:Candidate>`"* (`:1912`).
  `<svta:Candidate>` exists only inside an Overlay Resolution Document (§5.2.2), so
  the normative chapter states no placement for a **linear** ad, whose resolution
  document is a `ListMPD` with no candidates in it. The only statement of where the
  click lives on a linear ad is Annex K.2 (`:4146`), and Annex K is marked
  *Informative*. The §4.7.3 backward-compatibility audit table (`:1026`) likewise
  lists only the `<svta:Candidate>` placement.
- **Why `context/` does not close it**: R28.1 (`context/03-requirements.md:1162`)
  requires the ClickThrough and its click-tracking to sit *"in the normative carrier
  this specification defines, and not elsewhere"*, and
  `context/05-dash-linear-interfaces.md:~420` maps VAST `<ClickThrough>` /
  `<ClickTracking>` onto that carrier **inside the linear VAST → ListMPD table** —
  so the linear path is in R28's scope, and `context/` correctly leaves the
  placement to the spec.
- **What an implementer does today**: guesses between a `ListMPD` `<Period>` child,
  the sub-MPD's `<MPD>` root, and the sub-MPD's `<Period>`. Three APSs pick three
  placements and no Player reads all three — which is precisely the
  non-interoperability R28 exists to prevent.
- See Actionable TODO **T4**.

### G-2 — No Player behaviour for a slot authored without `@maxDuration`

- **Spec section that needs it**: §4.6.4, §8.1 row E9 (`:2565`).
- **What is missing**: §4.3.2 makes `@maxDuration` a Publisher obligation, and E9
  observes that *"a slot with no cap declared leaves the Player without the value
  this row depends on, which is why §4.3.2 makes it mandatory"* — but states no
  Player response for the manifest that omits it anyway. The case is not
  hypothetical for the linear family: §5.1.1's own attribute table records
  `@maxDuration` as optional in the base schema with default `2251799813685247`
  (`:1094`), so a legacy-authored or careless slot arrives with an effectively
  unbounded cap and §4.6.4's arithmetic degenerates silently rather than failing.
- **Why `context/` does not close it**: R4.1 binds the Publisher only.
  `../context-analysis/error-semantics.md` marks this **UNDEFINED** on row E9 in
  those words.
- **What an implementer does today**: guesses — inherit the baseline unbounded
  default (the slot never trims) or decline the slot (the slot never fills). The two
  are opposite outcomes.

### G-3 — No Positioning Templates section, and no positioning mechanism for a non-HTML form

- **Spec section that needs it**: §1.2 (`:91`), §3.1 *Layout*, §5.3.3.
- **What is missing**: R10.3 (`context/03-requirements.md:1241`) requires position
  semantics to *"be expressed via the Positioning Templates section using HTML5 /
  CSS primitives"*; OOS-3 (`:1258`) and `context/02-actors.md:41` point at the same
  section, and `context/03-requirements.md:1279` names it as part of the proposal.
  The spec has no such section — a literal grep for "positioning template" across
  the spec returns nothing. The spec instead states that positions *"are not
  expressible in spec-level attributes"* and delegates to HTML5 / CSS. That
  delegation works for an `html` form; it does not exist for an `image` form, which
  has no document for CSS to apply to. The token's IAB bound (§3.2) constrains the
  **area** of a Corner Overlay, not where an image sits for the plain `overlay`
  token, which §3.2 defines as *"(none — plain image or HTML overlay)"*.
- **What an implementer does today**: proprietary placement for image overlays,
  which is per-Player and therefore not interoperable.

### G-4 — The hybrid-break decision on a single-decoder device is stated only non-normatively

- **Spec section that needs it**: §4.6 (Player obligations); currently §8.4
  (`:2657`) and Annex D.5 (`:3355`).
- **What is missing**: UC-04's open questions (`context/04-use-cases.md:535-542`)
  state that *"whether D3 / D4 must always decline the overlay portion of a hybrid
  break … the spec must declare it explicitly"*. The spec answers it — the Player
  presents the linear portion alone — but the answer lives in chapter 8, which
  declares itself **non-normative** (`:2537`), and in an *Informative* annex.
- **Why that matters beyond bookkeeping**: R3.2
  (`context/03-requirements.md:600`) makes undefined per-class behaviour
  *non-conforming* for every ad opportunity type the spec defines, and §1.1 defines
  the hybrid slot as one of them. A conformance claim cannot rest on a chapter that
  disclaims normativity.
- **What an implementer does today**: follows §8.4, or does not — both are
  conformant, so the same manifest produces an overlay on one D3 Player and not on
  another.

### G-5 — The empty **linear** resolution document trips a second baseline execution-failure condition the divergence note does not cover

- **Spec section that needs it**: §5.2.3 (`:1486`) and the divergence box in §4.6.8
  (`:822`).
- **What is missing**: §4.6.8 declares one narrowing of the base specification's
  execution model — the base falls through on *"a resolution error **and** a
  zero-duration alternative presentation"*, and this specification falls through on
  the first only. Verified against the source: ISO/IEC 23009-1 6th ed. §5.16.2.2.6
  reads *"Execution fails if at least one of the conditions below is true at PRTA:
  — APDA is determined to be 0. — @executeOnce is set to "true", and E.c > 0 … —
  The playback of the alternative presentation cannot start. The reasons … include
  … — Alternative MPD is a List MPD, and merge process resulted in no available
  media."* The spec's chosen encoding for a linear no-fill — a `list` MPD carrying
  `<Period id="no-fill" duration="PT0S"/>` and no `<ImportedMPD>` — satisfies
  **both** the zero-duration condition and the "List MPD whose merge resulted in no
  available media" condition. §4.6.8 narrows only the first.
- **What an implementer does today**: applies the spec's narrowing to the
  zero-duration trigger, applies the baseline to the merge-empty trigger, and falls
  through to the fallback window on exactly the case §5.2.3 and R30 exist to keep
  distinguishable.

### G-6 — No signal for an overlay candidate doubling as the pause-ad candidate

- **Spec section that needs it**: §5.1.4, §7.5.6.
- **What is missing**: UC-08 (`context/04-use-cases.md:858-861`) says the Player
  re-resolves the APS for the pause-ad slot *"unless the Publisher's MPD signals
  that the overlay candidate doubles as the pause-ad candidate"*. The spec defines
  no such signal. §8.7's closest case — an overlay window and a pause-trigger window
  at the same position with the same `@uri` (`:2704`) — is two resolution requests
  against one endpoint, not one candidate serving two windows.
- **What an implementer does today**: always re-resolves. Harmless, but it means a
  `context/` sentence describes a manifest nobody can author.

### G-7 — R1.3 as written forbids the narrowing §4.6.8 declares

- **Spec section that needs it**: none — this is a `context/` gap the spec surfaced.
- **What is missing**: R1.3 (`context/03-requirements.md:134`) is absolute —
  *"The specification MUST NOT alter or override the semantics of any pre-existing
  MPEG-DASH 6th edition construct."* §4.6.8's divergence overrides the
  execution-failure semantics of §5.16.2.2 for the linear family and says so
  (*"a Player implementing this specification applies the rule stated here"*).
  `../context-analysis/dash-gap-analysis.md` G7 independently concludes the
  divergence is unavoidable if R20.1 and R30 are both to hold, so the requirement
  set is internally inconsistent: R1.3 forbids what R20.1 + R30 require.
- **What an implementer does today**: reads §1 and §4.1's "alters no baseline
  semantics" claim, reaches §4.6.8, and cannot tell which of the two is binding.
  See Ambiguity **A-2** for the spec-internal half of this.

### G-8 — R25.1 promises a freeze the base specification does not permit

- **Spec section that needs it**: none — the spec is the correct half.
- **What is missing**: R25.1 (`context/03-requirements.md:721`) requires the Player
  to keep presentation time frozen *"for the full duration of the pause"*. §4.6.9
  (`:877`) bounds the freeze at `MPD@timeShiftBufferDepth` and dismisses the pause ad
  at that boundary, which is what the base specification's resumption-trimming rules
  force (`dash-gap-analysis.md` G9). A Player conformant to the spec is
  non-conformant to R25.1 as written.
- **What an implementer does today**: follows the spec, correctly, and fails a
  conformance check written from R25.1.

---

## Edge cases (5)

### EC-1 — A viewer pause inside a pause-trigger window while a **linear** ad is playing

- **Trigger**: a linear slot and a pause-trigger window whose spans overlap (the
  hybrid authoring of §5.1.5 makes this a one-line manifest change), and the viewer
  pauses while the linear take-over is on screen.
- **Why it matters**: §4.6.9 arbitrates pause-ad against **overlay**, and nothing
  arbitrates pause-ad against an in-progress **linear** ad. Three things are
  unstated: whether the pause-trigger window is live at all while the main timeline
  is suspended by an alternative presentation; whether the paused frame the pause ad
  composites over may be an ad frame; and what the linear ad's cap arithmetic and
  beacon schedule do across the pause.
- **Responsible actor**: Player. `context/` is silent — UC-05 and UC-08 both assume
  the thing being paused is the primary content.

### EC-2 — Whether the slot cap accrues while a non-linear form is paused

- **Trigger**: a 10 s-capped overlay, the viewer pauses 5 s in and stays paused for
  60 s of wall clock, outside any pause-trigger window.
- **Why it matters**: §4.6.4 enforces the cap against *"actual rendered length"*,
  while Annex H.3 (`:3788`) establishes that the overlay's **window** clock follows
  the primary timeline and therefore freezes. Whether the **cap** freezes with it is
  not stated. One reading removes the overlay 5 s into the pause; the other holds it
  on screen for the whole pause and removes it 5 s after the resume.
- **Responsible actor**: Player. `context/` is silent (R4.5 speaks of "actual
  rendered length" without defining it across a pause).

### EC-3 — The slot cap and a candidate's duration are in different unit systems, with no stated conversion

- **Trigger**: any drop-before-play evaluation on a non-linear slot.
- **Why it matters**: `@maxDuration` on `<svta:OverlayPresentation>` is
  `xs:unsignedLong` in the parent `<EventStream>@timescale` units (`:1179`), and
  `<svta:Candidate>@duration` is `xs:duration` (ISO 8601) in a **different document**
  that carries no timescale at all (`:1447`). To compare them the Player converts,
  and the spec never says so, never says which side is normalised, and never fixes
  rounding at a timescale boundary. §5.4.1 reconciles the *candidate* duration with
  the *sub-MPD* duration and does not touch this pairing.
- **Responsible actor**: Player. `context/` is silent; R4.2 assumes the two are
  comparable.

### EC-4 — A `200` resolution document of the wrong family for the slot

- **Trigger**: an APS returns a `ListMPD` for an overlay slot, or an Overlay
  Resolution Document for a linear one. Well-formed, schema-valid, wrong profile.
- **Why it matters**: §4.5.1 puts the obligation on the APS and stops there. E3
  covers a body that is *"not well-formed XML, carries an unknown root element, or
  fails schema validation"* — none of which this is; E5 covers a document that
  carries no candidates — which this does not. The condition falls between the two
  rows and inherits no behaviour.
- **Responsible actor**: Player. `context/` is silent.

### EC-5 — `@allowedLayouts` is not bound to the slot family

- **Trigger**: a Publisher lists `pause-ad` in an `<svta:OverlayPresentation>`'s
  `@allowedLayouts`, or `overlay-corner` in a `<svta:PauseAdPresentation>`'s.
- **Why it matters**: §3.2's "Where it appears" column and §5.3.3's *"Admissible on
  overlay slots"* / *"Admissible on pause-trigger windows"* read as an intent, not an
  obligation: neither §5.1.3.1 nor §5.1.4.1 constrains the token list by family, and
  §4.6.5's Player check is exact-token membership in `@allowedLayouts` and nothing
  else. A `pause-ad` option therefore passes the Publisher check on a playing —
  not paused — surface, and the spec defines no rendering for that.
- **Responsible actor**: Publisher declares, Player validates. `context/` is silent;
  R12.2 constrains the vocabulary, not the family binding.
- See Flagged **F7**.

---

## Ambiguities (7)

### A-1 — A list of `<svta:Candidate>` is a sequence and a set of alternatives at once

- **Context passages**: R14 (`context/03-requirements.md:838-881`) — *"A non-linear
  ad slot MAY be filled by more than one ad form played in sequence … the Player
  presents them one after another, in the order the forms appear in the resolution
  document"*; against R5.3 / R5.7 (`:491`, `:509`) and R7 (`:515`) — the Player
  *"MUST skip any candidate that carries no form renderable on its device and fall
  through to the next candidate"*.
- **The two readings of the v7 document**:
  1. **Alternatives.** §3.1 defines the term: *"In a linear `ListMPD` the Periods
     are played in declared order rather than selected among; the selection sense of
     'candidate' applies to the non-linear document"* (`:253`). §4.6.6, §8.1 E6 and
     test **T-E6** (`:4516`) all describe walking candidates and stopping at the
     first that renders.
  2. **Sequence.** §4.6.7 (`:790`), Annex C.7 (`:3217`), §7.5.3 (`:2387`) and test
     **T-P7** (`:4537`) all describe *"a 30 s overlay window whose document carries
     three 10 s candidates"* rendering *"one after another, in document order"*.
- **Which the draft assumed**: both, in different chapters. The two are not
  reconcilable at the decisive moment — **what the Player does after a candidate
  renders successfully while further candidates remain**. Reading 1 says it is done;
  reading 2 says it plays the next one. The spec never states which, and
  `<svta:OverlayList>` (§5.2.2.3) carries no attribute that would let a document say
  which it meant, so the APS cannot express the difference either.
- **A tighter context sentence**: R14 should state the mapping onto the document
  explicitly — e.g. *"several candidates in one resolution document are a sequence
  presented one after another; the several presentation options inside one candidate
  are alternatives, of which the Player renders exactly one. R5.3's fall-through to
  the next candidate drops an unsatisfiable member of the sequence; it does not end
  the slot."*
- See Flagged **F1**.

### A-2 — §1 and §4.1 claim no baseline semantics are altered; §4.6.8 declares that they are

- **Context passage**: R1.3 (`context/03-requirements.md:134`).
- **The two readings**: (i) §4.6.8's narrowing is a *client-behaviour profile* layered
  on the baseline, leaving every construct's semantics intact, so §1's *"it alters no
  baseline semantics"* (`:25`) and §4.1's *"no pre-existing base specification
  semantics are altered"* (`:500`) still hold; (ii) it overrides §5.16.2.2's normative
  execution rule for the linear family — which is how §4.6.8 itself words it —
  and the two claims are then false as written.
- **Which the draft assumed**: (i) implicitly, by leaving §1 and §4.1 unqualified,
  while §4.6.8 states (ii) explicitly. R8.2 requires a deliberate departure to be
  documented inline; §4.6.8 does that, and §1 / §4.1 contradict it three thousand
  lines earlier.
- **A tighter context sentence**: see **G-7** — the durable fix is on R1.3. The
  spec-internal contradiction is separately and unambiguously fixable.
- See Actionable TODO **T5**.

### A-3 — §4.6.7 says "form" where §3.1 defines "form" as a dimension of an option

- **Context passage**: R14.1 (`context/03-requirements.md:866`), which says *"forms"*
  loosely because `context/` has no syntax yet.
- **The two readings**: §3.1 fixes the vocabulary — *"**Form.** The creative-carrier
  dimension of a presentation option: a single media type … `video`, `image` or
  `html`"* (`:258`). Read against that definition, §4.6.7's *"when the resolution
  document declares more than one form for one slot, the Player presents them one
  after another"* (`:791`) says that a candidate offering a video option **and** an
  image option is a two-item sequence — the exact opposite of §4.6.5, where those two
  are alternatives and the Player renders one.
- **Which the draft assumed**: the sequence sense of *candidate*, not of *form* —
  Annex C.7 and T-P7 both sequence **candidates**. §4.6.7 is using the word the spec
  defined for something else.
- **A tighter sentence**: §4.6.7 should say *"more than one **candidate**"*. This does
  not resolve A-1, but it removes one of the two sites that create it.
- See Actionable TODO **T1**.

### A-4 — The background element is Publisher-gated by token in the spec and advertiser-decided in `context/`

- **Context passage**: R26.2 (`context/03-requirements.md:754`) — *"When the
  advertiser supplies a background element, the Player MUST place it in the uncovered
  bands. When the advertiser supplies no background element, the uncovered region
  renders as black."* The presence of a background is the advertiser's call and
  nobody else's.
- **The two readings**: (i) splitting IAB *Double Box Video* and *Double Box Video +
  Background* into two tokens, `squeezeback-double-box` and
  `squeezeback-double-box-with-background` (§3.2, `:366`), is the faithful 1:1 IAB
  mapping R12.2 demands; (ii) it makes the background's presence a **layout** the
  Publisher admits or refuses through `@allowedLayouts`, so a Publisher listing only
  `squeezeback-double-box` blocks an advertiser-supplied background and a Publisher
  listing only the `-with-background` token blocks a background-less one — which R26.2
  does not contemplate.
- **Which the draft assumed**: (i), and inherited (ii) without saying so. Annex J.2
  (`:4015`) works around it by listing both tokens, which is evidence the constraint is
  real rather than theoretical.
- **A tighter context sentence**: R26 should state whether a Publisher may admit one
  variant and refuse the other, or whether the two are one layout whose third element
  is optional.
- See Flagged **F2**.

### A-5 — `[inferred]` on a claim the base specification states in prose

- **Context passage**: none — this is the spec's own convention, declared at `:10`:
  *"Claims that could not be verified against it are tagged `[inferred]`."*
- **The two readings**: the tag appears four times (`:1095`, `:1105`, `:1180`, `:1239`)
  and carries one distinct claim — that `@earliestResolutionTimeOffset` defaults to
  60 s when absent. The note at `:1105` argues the value is *"the semantic default
  carried in the clause's prose"*, i.e. the spec knows the claim is sourced, and tags
  it unverified anyway.
- **Which the draft assumed**: that "no schema default" means "unverified". Verified
  against the source: the XML Schema of §5.16.6 declares
  `<xs:attribute name="earliestResolutionTimeOffset" type="xs:unsignedLong"/>` with no
  default, **and** Table 63 of §5.16.5.2 states *"The default is 60 seconds in units of
  timescale."* The claim is verified; the tag is wrong, and the cross-reference to
  `<ImportedMPD>`'s `60.0` schema default is no longer the justification.
- See Actionable TODO **T2**.

### A-6 — `@maxDuration` on the linear events is required and defaulted in the same row

- **Context passage**: R4.1 (`context/03-requirements.md:297`).
- **The two readings**: §5.1.1's attribute table reads *Required* = *"no in the base
  schema; **yes under this specification**"* and, in the same row, *Default* =
  `2251799813685247` (unbounded) (`:1094`). If the attribute is required under this
  specification the default is unreachable; if the default is reachable the attribute
  is not required. §5.1.3.1 and §5.1.4.1 state the non-linear case cleanly — Required
  *yes*, Default `—`.
- **Which the draft assumed**: required, per §4.3.2 — but the row leaves a
  conformance-checker two columns that disagree, and G-2 is what happens downstream
  when an implementer takes the Default column at its word.
- See Flagged **F3**.

### A-7 — §4.2 lists a concurrency cap no construct expresses

- **Context passages**: `context/02-actors.md:36` (*"maximum number of concurrent
  overlays"*), `:165`, `:190` (*"duration cap, concurrency cap"*),
  `context/04-use-cases.md:285`, `:328`.
- **The two readings**: §4.2's decision table assigns the Publisher *"allowed layouts,
  duration cap, **concurrency cap**"* (`:513`), while §5.1.3.1 states the opposite in
  full — *"This specification declares no maximum-concurrency attribute on the slot.
  At most one non-linear form is active at any instant (§4.6.7), so an attribute whose
  only admissible value is `1` would restate a rule the specification already fixes"*
  (`:1191`).
- **Which the draft assumed**: the §5.1.3.1 reading, and it is the one `context/`
  supports: R22.1 (`context/03-requirements.md:1012`) fixes the bound at one active
  form, and DP-1.1 (`:29`) forbids a construct whose only admissible value is fixed by
  another rule. §4.2 is the leftover of a construct that was correctly dropped.
- See Actionable TODO **T3**. The `context/` side of the same finding —
  `02-actors.md` and `04-use-cases.md` still declaring the cap — is recorded in T3's
  notes rather than as its own row.

---

## R coverage map

| R | Status | Spec sections that satisfy it | Notes |
|---|---|---|---|
| R1 | partial | §1, §4.6.2, §4.6.3, §4.7.1–§4.7.3, §5.1.3.3, §5.1.4.2, §5.3.6, Annex G, T-P15 | R1.1 / R1.2 / R1.4 full. **R1.3 unmet**: §4.6.8 overrides §5.16.2.2's execution-failure semantics for the linear family. See G-5, G-7, A-2. |
| R2 | full | §4.2, §4.3, §4.4, §4.5, §4.6.1 | R2.1–R2.4 all carried; the four-actor table is the direct expression of R2. |
| R3 | partial | §3.4, §4.6.5, §5.3.7.3, §7.5, Annexes A.6/B.5/C.6/D.5/E.4/F.5/G.5/H.4/I.5/J.4/K.5/L.5/M.8 | R3.3 full, R3.1 **partial**: the five classes are enumerated normatively but the per-class behaviour per opportunity type lives only in annexes marked *Informative*; §7.5 gives prose, not the matrix. R3.2 unmet for the hybrid type — see G-4. |
| R4 | full | §4.3.2, §4.6.4, §5.1.1, §5.1.3.1, §5.1.4.1, §8.1 E9/E10, Annex F.4, T-E9, T-E10, T-P6 | Drop-before-play / trim-during-play both stated with the right modal verbs. Residuals: G-2 (no cap declared), EC-2 (cap across a pause), EC-3 (unit conversion). |
| R5 | full | §4.5.3, §4.6.5, §4.6.6, §5.3, §5.3.5, Annexes C/I/M, T-P3, T-P4 | R5.1–R5.7 all carried. Residual: A-1 (what "next candidate" means after a success). |
| R6 | full | §2.1, §4.5.6, §4.6.3, §5.5, §5.5.1 | Callback scheme reused verbatim; no parallel scheme introduced. |
| R7 | full | §4.6.4, §4.6.6, §5.2.1, §8.1 E9, Annex F.4, T-E9 | Order preserved, drop allowed, re-ordering and deduplication excluded. |
| R8 | governance | §4.1, §5.1, §5.1.3, §5.1.4, §5.1.6, §5.2.2, §5.3, §5.3.2, §5.5, §5.6, §5.7 | Every new construct carries a *"Why a new construct"* block and every non-reuse a *"Considered and not reused"*. **Residual**: R8.2 is met inside §4.6.8 and contradicted by §1 / §4.1 — A-2. |
| R9 | governance | §4.7.1, §5.1, §5.2.1, §5.4, §5.5, §5.1.6, §5.3 | Reuse-before-invention argued construct by construct, including the three rejected ordering primitives. |
| R10 | governance | §1.2, §3.1 *Layout*, §3.2 | R10.1 / R10.2 met. **R10.3 unmet**: no Positioning Templates section exists, and an `image` form has no HTML/CSS surface to carry position — G-3. |
| R11 | governance | §3.5, §4.4.6, §6.7 | R11.1 / R11.2 met. **R11.3 partially unmet**: §3.1's ADS definition (`:282`) names VAST inside a normative chapter with no illustrative flag; §3.5 and §4.4.6 carry the flag, §6.7 is declared non-normative. |
| R12 | full | §3.2, §4.3.3, §4.5.4, §5.3.3, §1.2 | Closed enumeration, exact-token matching, IAB bounds inherited by reference, off-surface types excluded. Residuals: A-4 (double-box split), EC-5 (token/family binding). |
| R13 | full | §4.4.2, §4.5.6, §4.6.10, §5.5.1, §5.5.3, §8.3, §4.5 closing note | Schedule authorship upstream; R13.3 trim boundary and R13.5 fidelity-outside-scope both carried. |
| R14 | partial | §4.6.7, §7.5.3, Annex C.7, T-P7 | R14.2 / R14.3 full. **R14.1 partial**: the sequencing rule is stated, but the resolution document cannot express that it is a sequence rather than a set of alternatives — A-1, A-3. |
| R15 | full | §3.3, §4.5.4, §5.3.2, §1.2, §8.1 E8 | Exactly three carriers; scripted creatives routed to `text/html`; no carrier added in an annex. |
| R16 | full | §4.6.9, §7.5.5, Annex E, T-P8 | One-rendering-frame dismissal and beacon cessation both stated. |
| R17 | full | §4.6.9, §7.5.6, Annex H, §8.1 E15, T-P10 | Priority stated as non-invertible, with the surviving-window restore rule. |
| R18 | governance | §1.2, §4.1, §6.7, §6.8 | The APS↔ADS row is the only one marked "Bilateral / Outside this specification". |
| R19 | full | §4.6.12, §5.5.3, §7.5.1, Annex B.5 trick-play | `duration / playback_speed` derived, never duplicated; cap and beacons on the presentation timeline. |
| R20 | full | §4.6.8, §5.1.6, §7.5.9, Annex L, T-P13 | Behaviour matches R20.1 exactly, including the `200`-with-no-candidates carve-out. The cost of that match is the R1.3 conflict — G-5, G-7. |
| R21 | full | §4.6.9 (first bullet), §5.3.7.3 `pause-ad` rows, Annex E.4 | Fullscreen and partial both admissible; resource release permitted, not required. |
| R22 | full | §1.2, §4.6.7, §8.1 E15, T-E15 | Single-active-form bound stated with the decoder-budget rationale. |
| R23 | governance | §5.7, §4.7.3 | Named place, optional on both ends, legacy-discarded. Minor residual: `context/05` expects the linear-side placement on `<ImportedMPD>`; §5.7 names only `<svta:Candidate>`. |
| R24 | full | §4.5.5, §4.7.2, §5.3.2, T-P16 | DR-6(a) carrier chosen and the two rejected carriers argued. The orphan flagged by `uc-coverage-matrix.md` is closed at the spec level: §4.7.2 states the rule, §5.3.2 states the carrier, T-P16 is the observable the matrix asked for. |
| R25 | partial | §4.6.9 (last bullet), §7.5.5, Annex E.5, T-P9 | The spec is correct and R25.1 is not: §4.6.9 bounds the freeze at `MPD@timeShiftBufferDepth`, R25.1 promises it *"for the full duration of the pause"* — G-8. |
| R26 | partial | §3.2, §5.3.7.2, §5.3.7.3, Annex J | R26.1 / R26.3 full. **R26.2 partial**: the spec makes the presence of a background element a Publisher-gated layout token, where R26.2 makes it the advertiser's call alone — A-4. |
| R27 | full | §3.2, §5.3.7.1, §5.3.7.3, Annexes I.3/I.4, J.5 | One creative, always full-frame, two elements, no third filler; budget driven by the creative's media type. |
| R28 | partial | §4.5.8, §4.6.11, §5.6, §5.6.1, Annex K, T-P12 | R28.2 / R28.3 full and the non-linear carrier is normative. **R28.1 partial**: the carrier has no normative placement on the linear path — G-1. |
| R29 | full | §4.5.9, §4.5.10, §4.6.13, §5.8.2, §5.8.3, §5.8.4, Annex M, T-P14 | R29.1–R29.7 all carried, including the R29.6 acceptance table that tells D1–D5 apart and the `x-<vendor>-` prefix rule. |
| R30 | full | §4.5.7, §5.2.3, §4.6.8, §8.1 E5, T-E5, T-P17 | `200` + body + no candidates, distinguishable from failure, with the un-requested fallback window as the observable. Residual: G-5 on the linear encoding. |

**Verdict.** No requirement is a `gap`. Eight are `partial`: **R1** (R1.3),
**R3** (R3.1, R3.2), **R10** (R10.3), **R11** (R11.3), **R14** (R14.1), **R25**
(R25.1), **R26** (R26.2), **R28** (R28.1). Of those, R1 / R25 / R10 are partial
because `context/` is wrong or absent, not the spec; R3 / R11 / R14 / R26 / R28 are
partial because the spec is.

---

## Disposition of findings

### 5.a Actionable TODOs (5)

| # | Finding ref | Criterion | Spec section | Concrete edit | Citation |
|---|---|---|---|---|---|
| **T1** | A-3 | 4 (naming consistency) | §4.6.7, line 791 | Replace *"when the resolution document declares more than one form for one slot"* with *"when the resolution document declares more than one **candidate** for one slot"*, and in the following clause *"in the order the forms appear in the document"* with *"in the order the candidates appear in the document"*. `form` is reserved by §3.1 for the creative-carrier dimension of an option. | §3.1 *Form* (`../output/v7-sgai-spec.md:258`); R14.1 (`../context/03-requirements.md:866`) |
| **T2** | A-5 | 2 (self-flagged marker) | §5.1.1 (`:1095`, `:1105`), §5.1.3.1 (`:1180`), §5.1.4.1 (`:1239`) | Delete the four `` `[inferred]` `` markers. Rewrite the note at `:1105` to: *"The base specification declares `@earliestResolutionTimeOffset` in the XML Schema of §5.16.6 with no schema default; the 60-second default is stated in the prose of §5.16.5.2, Table 63 — 'The default is 60 seconds in units of timescale.' An implementation that needs the value to be unambiguous declares it explicitly on the slot, which §4.3.5 asks for in any case."* Drop the `<ImportedMPD>`-consistency clause, which is no longer the justification. | ISO/IEC 23009-1:2025 §5.16.5.2, Table 63 (verified this session); §5.16.6 schema |
| **T3** | A-7 | 3 (internal contradiction; DP-1.1 is the context-grounded reading) | §4.2, line 513 | In the decision table, replace *"allowed layouts, duration cap, concurrency cap"* with *"allowed layouts and duration cap"*. No construct expresses a concurrency cap and §5.1.3.1 explains why one must not exist. Note for the owner: `../context/02-actors.md:36,:165,:190` and `../context/04-use-cases.md:285,:328` still declare the cap and need the matching edit at the next major build. | DP-1.1 (`../context/03-requirements.md:29`); R22.1 (`:1012`) |
| **T4** | G-1 | 1 (R28.1 violation) | §5.6 (after line 1914), §4.7.3 table | Add to §5.6, normatively: *"On a linear slot the same element is the carrier and is carried as foreign-namespace open content on the `ListMPD` `<Period>` of the ad it belongs to, which a legacy Player discards with its subtree exactly as it discards the element inside a candidate."* Add the matching row to the §4.7.3 audit table: `<svta:Click>` | `<Period>` child in a `ListMPD` | §5.2.1 foreign namespace | Discarded with its subtree; the click is inert | The Period is valid without it | Foreign-namespace open content. This promotes the statement Annex K.2 (`:4146`) already makes informatively; it introduces no new construct. | R28.1 (`../context/03-requirements.md:1162`); DASH §5.2.1 open content via DR-2 (`../context/08-dash-extension-rules.md:33`) |
| **T5** | A-2 | 1 (R8.2: a departure must be documented, not contradicted) | §1 line 25, §4.1 line 500 | §1: replace *"and it alters no baseline semantics"* with *"and it alters no baseline construct semantics, with one declared exception: the narrowing of the alternative-MPD fall-through condition stated in §4.6.8."* §4.1: replace *"that no pre-existing base specification semantics are altered"* with *"that no pre-existing base specification semantics are altered other than the single narrowing declared in §4.6.8"*. This removes the internal contradiction without deciding the R1.3 question, which is G-7's. | R8.2 (`../context/03-requirements.md:1201`); R1.3 (`:134`) |

### 5.b Flagged for review (10)

| # | Finding ref | Spec section | Why uncertain | Resolutions considered |
|---|---|---|---|---|
| **F1** | A-1 | §3.1, §4.6.6, §4.6.7, §5.2.2.3, Annex C.7 | The decisive case — what the Player does after a candidate renders successfully while further candidates remain — has two defensible answers, and fixing it either way changes what an existing conformant document means. This is the largest open item in v7. | (a) Candidates are always a sequence; R5.3's fall-through drops a member. (b) Candidates are always alternatives, and a sequence is expressed by a new wrapper or a `@sequence` flag on `<svta:OverlayList>`. (c) Amend R14 in `context/` first and let the next major build carry the syntax. (a) costs nothing syntactically but silently changes Annex I and M, where four candidates would become a four-ad sequence; (b) adds a construct DP-1.1 will challenge. |
| **F2** | A-4 | §3.2, §5.3.3, §5.3.7.2 | Collapsing the two double-box tokens satisfies R26.2 and breaks the 1:1 IAB mapping R12.2 asks for; keeping them satisfies R12.2 and leaves the Publisher able to veto an advertiser's background. Neither is free. | (a) Keep both tokens and state in §5.3.7.2 that a Publisher admitting the double box SHOULD list both. (b) Collapse to one token with the background as an optional child. (c) Amend R26 to state the Publisher's gate explicitly. |
| **F3** | A-6 | §5.1.1 table, line 1094 | The row is fixable two ways with different consequences for a conformance checker: strike the Default column (the attribute is required, no default reachable) or keep it and downgrade Required to SHOULD. §4.3.2 says required; the base schema says defaulted. | (a) Required = yes, Default = `—`, with a note that the base schema's `2251799813685247` applies only to documents not authored under this specification. (b) Keep both columns and add the Player rule G-2 asks for. |
| **F4** | G-2 | §4.6.4, §8.1 E9 | Two opposite defensible Player responses for a slot with no cap: inherit the baseline unbounded default, or decline the slot. The first monetises a malformed manifest; the second enforces §4.3.2. `context/` decides neither. | (a) Treat an absent cap as unbounded and state it. (b) Decline the slot and fall through to primary content. (c) Leave it and mark E9 explicitly UNDEFINED, as `error-semantics.md` does. |
| **F5** | G-4 | §8.4, §4.6 | The content of the answer is settled; what is uncertain is whether promoting it into §4.6 makes it a **MUST** (which §8.4's own wording resists: *"an implementation that knows its platform can do better"*) or a **SHOULD**. Getting this wrong forbids a capability some platforms genuinely have. | (a) Move §8.4's second paragraph into §4.6 as a SHOULD with the device-property escape retained. (b) Add a §4.6 clause that only fixes the *defined-behaviour* obligation R3.2 needs, leaving the choice open. (c) Leave it in §8 and amend R3.2. |
| **F6** | G-5 | §5.2.3 linear shape, §4.6.8 divergence box | Two remedies with different blast radii: widen the divergence to a second baseline condition (more override, more R1.3 pressure) or re-encode the linear no-fill so it trips neither (which may have no conformant encoding, since `Period` cardinality is 1..N). | (a) Extend §4.6.8's box to name both conditions. (b) Change the linear empty document — e.g. a Period with a non-zero `@duration` carrying an `<AdaptationSet>` of no media, which DR-7 forbids, or a distinct profile URI. (c) Restrict the empty resolution to the non-linear family and define the linear no-fill some other way. |
| **F7** | EC-5 | §5.1.3.1, §5.1.4.1, §5.3.3 | The constraint is obvious in intent but its strength is not: forbidding a `pause-ad` token on an overlay slot is a MUST NOT, which DP-2 pushes back on, and the positive form ("draws its tokens from the overlay rows of §3.2") needs §3.2 to gain a machine-readable family column. | (a) Add a family column to §3.2 and a positive obligation to §4.3.3. (b) State it in §5.3.3's prose only. (c) Leave it to the Player's render-time check and add an §8.7 degenerate-authoring bullet. |
| **F8** | EC-3 | §5.1.3.1, §5.2.2.4, §5.4.1 | Where to state the conversion is a real choice — §4.6.4 (a Player obligation), §5.4.1 (which already reconciles two declared durations) or §5.2.2.4 — and whether to fix rounding at all. Getting rounding wrong is worse than leaving it open. | (a) Extend §5.4.1 with a third paragraph normalising both to seconds. (b) State it in §4.6.4 as part of the cap arithmetic. (c) Require `<svta:Candidate>@duration` to be expressed in the slot's timescale instead of `xs:duration`, which contradicts §5.2.1.1's precedent. |
| **F9** | EC-4 | §4.5.1, §8.1 E3 | Whether a wrong-family document is an access failure (try the fallback window) or a declined opportunity is the same open question E3 already records for an unusable body, and the spec deliberately left that one open. Deciding one without the other splits the treatment. | (a) Widen E3 to cover "unusable **or of the wrong profile for the slot family**". (b) Add row E16. (c) Leave both open and say so once. |
| **F10** | EC-2 | §4.6.4, Annex H.3 | Both readings of "actual rendered length" across a pause are defensible and the annex only settles the **window** clock, not the cap. A decision here also touches EC-1. | (a) State that the cap accrues on the presentation timeline, so it freezes with it — consistent with §4.6.12's presentation-timeline rule. (b) State that it accrues on wall clock while the form is visible. (a) is the more consistent with §4.6.12 and is the likely answer, but it makes a capped overlay outlive a long pause. |

### 5.c Deferred to `context/` (5)

| # | Finding ref | `context/` file to edit | Suggested edit | Leverage rationale |
|---|---|---|---|---|
| **D1** | G-7 | `03-requirements.md`, R1.3 (`:134`) | Add a second sentence: *"A client-behaviour rule of the base specification MAY be narrowed when a requirement of this document cannot otherwise be satisfied; every such narrowing is stated inline at the point of divergence (R8.2) and enumerated in the specification's conformance chapter. The syntax and meaning of a base specification construct are never altered."* | Highest leverage in the set. As written, R1.3 forbids what R20.1 + R30 jointly require, so the requirement set is internally inconsistent and **every** build will either violate R1.3 or violate R20.1. It also unblocks T5 and F6, both of which currently have to work around the contradiction rather than resolve it. |
| **D2** | G-8 | `03-requirements.md`, R25 and R25.1 (`:700-727`) | Replace *"for the full duration of the pause"* with *"for as long as the viewer remains paused and the resumption time stays inside the time-shift buffer"*, and add R25.2: *"(Player) When the pause outlives `MPD@timeShiftBufferDepth`, the Player dismisses the pause-ad and ceases its remaining beacons at the boundary, exactly as on a resume."* | R25.1 currently makes a conformant Player non-conformant. The spec already carries the correct behaviour (§4.6.9), so this edit costs one build and permanently removes a false conformance failure. `dash-gap-analysis.md` G9 reached the same conclusion independently, which is the second case that makes it a pattern rather than a one-off. |
| **D3** | A-1 / R14 | `03-requirements.md`, R14 (`:838-881`) | Add to R14: *"A resolution document expresses a sequence as several candidates and alternatives as several presentation options inside one candidate. The Player presents the candidates one after another in document order; R5.3's fall-through drops a candidate with no satisfiable option and continues with the next member of the sequence rather than ending the slot."* | Resolves F1 at the level where it originates. Without it the spec has to pick one reading with no requirement behind it, and the two readings produce different viewer-visible behaviour on every multi-candidate non-linear document — including Annexes C, I and M as they stand. |
| **D4** | G-3 | `03-requirements.md`, R10.3 (`:1241`) and OOS-3 (`:1258`) | Drop the reference to a "Positioning Templates section" and restate: *"Position semantics inside a layout are out of scope. For an `html` form they are expressed with HTML5 / CSS primitives inside the creative; for an `image` form the layout token's IAB spatial bound is the only spec-level constraint and finer placement is the creative's own."* Update `02-actors.md:41` to match. | The section has never existed in any build and the spec deliberately declines to create one (R10.2 forbids a parallel layout system). Leaving R10.3 pointing at it guarantees a permanent `partial` on R10 in every future validation — the cheapest possible removal of a recurring finding. |
| **D5** | EC-1 | `04-use-cases.md`, UC-05 and UC-08 | Add a variant to UC-05: a pause inside the pause-trigger window **while a linear ad is on screen** — whether the window is live, what surface the pause ad composites over, and what the linear ad's cap and beacon schedule do across the pause. Also drop or make expressible UC-08's *"unless the Publisher's MPD signals that the overlay candidate doubles as the pause-ad candidate"* (`:858-861`), which closes **G-6** in the same edit. | The hybrid authoring of §5.1.5 makes the combination a one-line manifest away, and the spec has no rule for it at all — a genuine undefined behaviour under R3.2, not a wording gap. Bundling G-6 into the same UC edit keeps it to one build. |

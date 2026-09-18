[GROUNDED_BY=iso-23009-1-2026-pdf]

# Spec validation — v9 (2026-09-18)

Built against:
- spec: `../output/v9-sgai-spec.md`
- context/ at git SHA: 8547827f69e761d934cb0936afaa51e9c232941d

Grounding: claims this validation makes about the base standard were checked
against the primary copy of ISO/IEC 23009-1:2026 (Sixth edition, 2026-07)
declared in `context/00-normative-base.md`. Clause numbers and sentences are
quoted; nothing about the copy itself is recorded here.

**What this walk covered.** `bin/check-promotable.py --population` names 168
units — 123 conformance criteria, 31 prose obligations, 14 use cases. All 168
were walked and all 168 carry a row in §4. No unit was skipped.

**What it could NOT cover, stated per item rather than left silent:**

- **§5 items 3 and 4 — the conformance-audit and detail-review routings — could
  not be produced.** `output-analysis/v9-dash-conformance-audit.md` and
  `output-analysis/v9-detail-review.md` do not exist when this step runs:
  `prompts/build-all.prompt` places `validate-spec` at Step 7 and those two at
  Steps 7.5 and 8. The requirement is structurally unsatisfiable at this
  position in the pipeline, not merely unmet in this run. Recorded as A-9.
- **The step's declared acceptance test (`UC-14` must come back `gap`) does not
  hold against v9 and was not applied as written.** `validate-spec.prompt`
  §4.1 states that UC-14 postdates the newest spec so the current output does
  not walk it. v9 does walk it: Annex N (L8149-8381) covers the scenario and
  L8363-8380 walks all five device classes with rows that match
  `context/04-use-cases.md` UC-14 exactly. UC-14 is therefore recorded `met`.
  The instrument was not skipped — it was run and it returned the opposite of
  what the prompt predicts, which is reported rather than forced. Recorded as
  A-10; the prompt's paragraph is what needs updating.

## Gaps (5)

**G-1 — The extension schema §4.6 mandates validating against does not exist.**
§4.6 (L1167-1183) makes four numbered checks obligatory of any procedure
claiming to validate a resolution document, and step 2 is *"The extension
subtree validates against the schema of `urn:svta:dash:sgai:2026`, which means
the validator is given that schema rather than left to skip what it cannot
resolve"*. No XML schema for that namespace appears anywhere in the spec or its
annexes. `context/` does not carry one either. **What an implementer does
today:** writes their own schema from the attribute tables of §5.2-§5.7 and
gets a different one from every other implementer, or skips step 2 and reports
the document valid — which is the precise outcome §4.6 L1160-1165 exists to
prevent.

**G-2 — A linear window has no `@allowedLayouts`, and §4.5.2 validates against
one.** §4.5.2 (L766-769) obliges the Player to validate every candidate against
*"that window's `@allowedLayouts`, its `@maxDuration`, and the admissible
creative carriers of §3.3"*, and §4.5.3 (L787-788) makes the layout match a
condition of rendering. `<InsertPresentation>` (§5.1.1, L1737-1745) and
`<ReplacePresentation>` (§5.1.2, L1782-1786) carry no such attribute — they are
inherited verbatim from the base standard, and a `ListMPD` Period carries no
`@layout` either. `context/` does not say whether the layout check is inert on
the linear family or whether a linear window is expected to declare one.
**What an implementer does today:** treats the check as vacuous on linear
slots, which is probably right and is nowhere written.

**G-3 — Where a non-linear slot's presentation timeline starts is never fixed.**
§5.5.3 (L2742-2746) resolves every beacon time *"relative to the start of the
ad's own presentation"* and has the Player *"add the ad's start position on the
primary timeline to each relative value"*. Nothing states what that start
position is for the first candidate of an overlay slot: the window is the
`<Event>`'s `@presentationTime` and `@duration` (§5.1.3, L1802-1803), and the
resolution may arrive at any instant from the Earliest Resolution Time onward.
**What an implementer does today:** anchors at the window's `@presentationTime`
or at first render, and the two differ by the resolution latency — which moves
every beacon.

**G-4 — `R32.4`'s scope declaration is absent from the spec.** The criterion
requires the specification to declare out of scope whether a second resolution
request inside one pause is the same opportunity or a new one. §1.3 (L119-160)
lists seven exclusions and this is not among them, and no other passage
addresses it. **What an implementer does today:** counts it either way; the
Player behaviour is identical, but an APS and an ADS reconciling requests
against opportunities disagree silently.

**G-5 — `@maxDuration` on a pause window is given a semantics `context/` never
defines.** §4.5.4 (L819-820), §5.1.4 (L1939) and §6.3 (L3212-3214) all make it
*"the display of **one** pause ad before automatic dismissal"*, and §5.1.4
marks it `Required: yes`. R31.2 says the cap bounds neither an end nor a
cumulative duration on a pause slot *"because there is no authored duration for
it to bound"*, and grants no third reading. "Automatic dismissal" is defined
nowhere, and no Player obligation anywhere obliges the dismissal: §4.5.10 and
§7.6 never mention the cap. **What an implementer does today:** invents the
dismissal, or ignores a required attribute.

## Edge cases (4)

**EC-1 — A candidate that passes one of §4.5.2's three checks and fails
another.** §4.5.2 (L769-771) defines only two outcomes: a candidate that
*"satisfies them"* is eligible, one that *"satisfies none is skipped"*. Three
independent checks run (allowed layouts, cap, carrier), so the mixed case —
the common one — falls in neither branch. **Why it matters:** a candidate whose
layout is admitted but whose duration exceeds the cap has no defined
disposition at the point the spec validates it. **Responsible:** the Player;
`context/` is silent, R2.3 saying only *"render only those that satisfy them"*.

**EC-2 — `repeat` against "presenting each exactly once".** §4.5.5 (L864-866)
obliges the Player to present the surviving candidates *"presenting each
exactly once"*; §4.5.11 (L1020-1021) defines `repeat` as *"present the sequence
again from the start, for as long as the pause lasts"*. **Why it matters:** the
two are in the same normative chapter and a Player obeying §4.5.5 cannot
perform `repeat`, which R32.1 makes a required behaviour. **Responsible:** the
Player. `context/` is not ambiguous here — R32's `repeat` is explicit — so the
spec is what has to give. See Actionable TODO T2.

**EC-3 — A pause that outlives the time-shift buffer.** §4.5.10 (L1006-1012)
bounds the live freeze by the buffer and clips the resumption point to its
edge; §8.9 (L3815-3818) then leaves open whether the pause ad is dismissed at
that boundary or kept until the viewer acts. **Why it matters:** R25.1 promises
the freeze *"for the full duration of the pause"* with no bound, so the spec
narrows a MUST and then leaves the narrowing's own behaviour undecided, in a
chapter that declares itself non-normative. **Responsible:** the Player;
`context/` never mentions a time-shift buffer, so the bound has no requirement
behind it.

**EC-4 — A fullscreen pause ad on a class with no compositing surface.**
§3.4 (L485) admits `pause-fullscreen` with an `image` or `html` creative on D2;
§5.3.7.3 (L2589-2590) does not. §3.4 admits a `video` one on D5; §5.3.7.3
(L2588) omits D5 from that row while its own closing paragraph (L2610-2611)
says *"D5 presents no ad surface of any kind (§3.4), so the question does not
arise"* — and Annex E (L5322-5330) has D5 render exactly that ad. **Why it
matters:** §4.5.3 sends the Player to §5.3.7.3, so the table that decides is
the outlier, and D2, D4 and D5 have no determinate outcome for a fullscreen
pause ad. **Responsible:** the Player. `context/` supports §5.3.7.3 for the
image and HTML rows (UC-05 D2, D4) and conflicts with itself on the D5 video
row (R21.1 permits the release; UC-05 D5 declines the opportunity).

## Ambiguities (10)

**A-1 — Which actors' conformance clauses carry normative force.** §4.2
(Publisher), §4.3 (ADS) and §4.4 (APS) state every obligation in the
indicative under a chapeau — *"A conformant Publisher:"* (L561), *"A conformant
APS returns, for each request it answers, a document that satisfies all of the
following."* (L654). Measured across the whole document: §4.2 carries 0 `MUST`,
§4.3 0, §4.4 0, chapter 5 0, chapter 6 0, against 45 in §4.5, 1 in §4.6 and 37
in chapter 7 — 83 in total, every one of them binding the Player.
**Two readings:** the chapeau confers the force of the clause on each bullet
(ISO convention), or it does not and only §4.5 and chapter 7 bind anyone.
**What the spec assumed:** the first, implicitly — it never says so, and §4.1
(L516-554), which is where it would be said, discusses only the scoping of
Player obligations. **A tighter sentence in `context/`:** none is needed;
this one is resolved in the spec, by either adding the modals or stating in
§4.1 that a conformance clause binds in the indicative. It is the single cause
of 14 of this walk's 16 `force-lost` rows.

**A-2 — `R1.3` against `R4.8` / `R4.10`.** R1.3 forbids altering the semantics
of any pre-existing MPEG-DASH construct. R4.10 obliges the Player to present no
ads from a slot carrying no cap, where the base standard reads the absence as
infinity — *"If absent, the value is assumed to be infinity, in which case the
current presentation resumes only when the alternative presentation
terminates"* (verified in the primary copy, §5.16.5.2). **Two readings:** the
narrowing is a profile restriction and changes no semantics (R4.8's own
argument, and §4.2 L575-577 repeats it), or it assigns a pre-existing construct
a new consequence (R1.3's plain text, and §4.8.5 L1581-1582 asserts the spec
*"does not"* do that). **What the spec assumed:** both, in different sections,
which is why §4.5.4 L845-850 and §4.8.5 L1581-1582 read as contradictory to
anyone holding both. **A tighter sentence in `context/`:** R1.3 should say
whether a profile-style narrowing of an attribute's absent-value default counts
as altering semantics.

**A-3 — `R26.1`'s "composition attribute of the slot / layout".** The criterion
forbids the background element being *"a separate presentation option"* and
requires it be *"a composition attribute of the slot / layout"*. **Two
readings:** an attribute of the slot declaration the Publisher authors, or an
attribute of the layout the chosen option names. **What the spec assumed:** the
second — `<svta:BackgroundElement>` is a child of the `<svta:RenderableAsset>`
whose `@layout` is `squeezeback-double-box-with-background` (§5.3.1 L2339), and
§5.3.7.2 L2558-2561 states *"It is a composition attribute of the layout, not a
presentation option. The Player does not walk it the way it walks the ordered
options"*. That is the only reading consistent with R26's own *"It is the
advertiser's creative … owned by the advertiser and not the Publisher or
platform"*; a slot-level attribute would be Publisher-owned. The row is `met`
on that basis and not inherited from the earlier iteration that called it
`contradicted`. **A tighter sentence in `context/`:** R26.1 should say
"of the presentation option's layout" and drop "slot".

**A-4 — Twenty-six declared criteria carry no RFC 2119 keyword.**
`context-analysis/conformance-assertions.md` §5 enumerates them: R1.2c, R4.7,
R4.8, R4.11, R6.5a, R6.6, R10.3, R12.4, R13.5, R17.1, R17.2, R17.3, R17.4,
R17.5, R18.1, R18.2, R20.3, R20.5, R27.3a, R28.3, R29.1, R29.7, R32.4, R33.3,
R34.3, R34.4. Each is recorded `source-has-no-modal` in the Force column of §4.
`validate-spec.prompt` §4.2 puts the figure at 17; the pre-spec analysis, which
derives it from `context/` directly, puts it at 23 plus 3 split criteria. The
prompt's number is the stale one. **What the spec assumed:** MUST, in every
case where the criterion describes runtime behaviour — §4.5.9 for the whole of
R17 is the clearest instance, and it is stronger than its source.

**A-5 — `R15.3` grants a permission the spec removes.** R15.3: *"The Player MAY
skip a candidate whose creative carrier mimeType is not in the admissible
set"*. §4.5.2 (L766-771) makes validation a MUST and states the skip
unconditionally. **Two readings:** the MAY is a genuine permission and a Player
that renders such a candidate conforms, or it is a MUST written loosely. **What
the spec assumed:** the second. The direction is strengthening, so nothing is
lost operationally, but a Player conforming to R15.3 would violate §4.5.2.

**A-6 — `R4.2`'s "every non-linear family" against `R31.2`.** R4.2 makes the cap
bound cumulative duration on *"the non-linear families, and linear insertion"*;
R31.2 exempts the pause family. §4.5.4 reproduces both two lines apart — L815-817
*"on every non-linear family it bounds *how long*"* then L819-820 carving pause
out — without saying the second overrides the first. **What the spec assumed:**
the exemption. **A tighter sentence in `context/`:** R4.2 should name the
families it covers rather than the class.

**A-7 — `R6.4` and `R6#p2` ask for an obligation the spec argues cannot be
made.** Both require Players to safely ignore unknown namespaces. §4.1
(L548-553) argues *"An obligation on a Player that has never heard of this
specification is not available to be made, here or in any other extension of
the base standard"*, and the behaviour appears only in §8.2 (L3647) and Annex O,
both non-normative. The same shape costs R1.1 its modal. **Two readings:** the
criteria bind a *conformant* Player (attainable, and the spec should state it in
chapter 4), or they bind any Player (unattainable). **What the spec assumed:**
that neither is worth stating, which leaves the obligation nowhere.

**A-8 — `R26.2` and `R27.2` state Player compositing MUSTs that §1.3 delegates
away.** §1.3 (L152-160) says *"The composition of two visual surfaces is
likewise left to the implementation"*, citing the base standard's own position;
R26.2 and R27.2 require the Player to composite the boxes and the L-shape.
**What the spec assumed:** the delegation, stating both layouts in the
indicative only (§5.3.7.1 L2518-2521, §5.3.7.2 L2536-2539).

**A-9 — §5 of this step's own prompt cannot be satisfied at Step 7.** Items 3
and 4 route items from sidecars produced at Steps 7.5 and 8, which do not exist
when Step 7 runs. Recorded so the omission reads as a contract defect rather
than as an incomplete walk.

**A-10 — the step's acceptance test contradicts the artefact it tests.** See the
header. v9 walks UC-14 in Annex N across all five device classes; the prompt
asserts it cannot.

## Obligation coverage map

168 rows, one per unit named by `bin/check-promotable.py --population`.
Counts: **met 135, force-lost 16, partial 12, contradicted 4, gap 1,
governance 0.** `Force` answers §4.2's second question: `preserved` the modal
survived, `lost` it did not, `n/a` the unit is document-level or scope,
`source-has-no-modal` the criterion states an obligation with no RFC 2119
keyword (§3, A-4).

| Unit | Kind | Verdict | Disposition | Force | Evidence — quoted passage and location | Notes |
|------|------|---------|-------------|-------|----------------------------------------|-------|
| `DP-1#p1` | document | partial | 5.b | preserved | §5.3.7.2, L2541-2544: *"A candidate offering the double box **without** a background uses the `squeezeback-double-box` token and carries no `<svta:BackgroundElement>`. A candidate offering it **with** one uses `squeezeback-double-box-with-background` and carries exactly one."* | The same fact is carried twice — by the token and by the element's presence — with no derivation rule. Two further instances: `@form="video"` (§5.3.1, L2332) is determined by the presence of `<ImportedMPD>` and the absence of `@assetUrl` on the same element; `MPD@type` is required at its own declared default (§5.2.2, L2214). |
| `DP-1.1#p1` | document | met | — | preserved | §5.1.3, L1884-1887: *"No maximum-concurrency attribute is declared on the slot. At most one non-linear form is active at any instant (§4.5.8), so an attribute whose only admissible value is `1` would restate a fixed rule, and any other value would be unenforceable."* | The principle is applied and its reasoning shown. No speculative "future edition" construct found anywhere. |
| `DP-1.1#p2` | document | contradicted | 5.b | n/a | §5.5.1, L2689: *"`@value` … yes … `1`, the value the base specification fixes for this scheme"*; §5.2.2, L2214: *"`@type` … yes … `static` … `static` on this document"* | Two attributes declared **required** whose only admissible value is fixed by another rule (`@value`) or equal to the attribute's own default (`@type`) — the shape this principle forbids, and the one §5.1.3 L1884-1887 argues against. `@value`'s premise is in fact verifiable: the primary copy states `EventStream@value` `1` for this scheme in the Table of §5.10.4.5.3, so the `[inferred]` tag on it is removable (T5). |
| `DP-1.2#p1` | document | partial | 5.b | preserved | §5.4, L2651-2657: *"**The sub-MPD's `Period@duration` is canonical** … The parent document's value is **derived from it** by the APS when the resolution document is produced"* | The canonical source is named, but the derived value is written into the markup of a second document, which is what this principle excludes (*"computed at runtime by the implementer, not duplicated in the markup"*). L2659-2663 accepts the drift and fixes only its consequence. Defensible for the stated reason (avoiding a second fetch); recorded as a departure because nothing records it as one. |
| `DP-2#p1` | document | met | — | preserved | Measured across chapters 4-7 (L514-3614): **0** occurrences of `MUST NOT` against **83** of `MUST`. | Instrument checked: the same search returns the one whole-file hit at L14, the RFC 2119 boilerplate, so the zero is the document and not a broken search. |
| `DP-2#p2` | document | met | — | preserved | Same measurement. | — |
| `DP-2#p3` | document | met | — | preserved | §4.5.13, L1081-1083: *"Beacons scheduled past a trim boundary (§4.5.4), and past the dismissal of a pause ad on resume (§4.5.10), fall outside the ad's active window."* | The principle's own worked example — beacons after the slot end — is carried positively, as it asks. |
| `DP-2#p4` | document | met | — | preserved | §4.5.5, L864-866: *"the Player MUST preserve the declared order of the surviving candidates, presenting each exactly once"* | R7's two prohibitions arrive as one positive MUST. Caveat: in §4.2 and §4.4 the zero-prohibition count is obtained by carrying no modal at all rather than by rephrasing (A-1). |
| `DP-3#p1` | runtime | met | — | preserved | §4.5.15, L1104-1106: *"the Player MUST abort that ad and continue playing the primary content uninterrupted"*, with the observable at L1108-1112: *"no freeze and no blank slate; no tracking beacon fires for the opportunity that failed; and the viewer cannot tell that an ad opportunity existed."* | Also §4.5.3 L793-794 and §4.5.6 L927-930. |
| `R1#p1` | document | met | — | preserved | §1.1, L72-77: *"This specification reuses those constructs verbatim … and extends them only where the baseline leaves an ad deployment without an answer"* | — |
| `R1#p2` | runtime | met | — | preserved | §7.9, L3552-3560, and the Legacy-test column of §4.7.13, L1444-1455: *"Skipped silently; primary content plays"* | — |
| `R1#p3` | document | met | — | preserved | §4.7, L1229-1231: *"**Every construct this specification introduces is (a)**, and none uses a descriptor."* | Per-construct extension rule in each §4.7.x row; (c1) and (c2) are kept apart at L1223-1227 because their legacy costs differ. |
| `R1.1` | runtime | force-lost | 5.c | lost | §7.9, L3558-3560: *"Such a Player therefore skips the overlay window, the pause window and every element they carry, never reaches the APS, and plays the primary content uninterrupted."* | Criterion says a legacy Player MUST ignore and continue; the spec carries it purely in the indicative, deliberately: §4.1 L548-551 argues *"An obligation on a Player that has never heard of this specification is not available to be made"*, citing DASH §8.1 NOTE 1. The remedy is not a wording edit — it is deciding whether R1.1 binds a conformant Player or nobody (A-7). |
| `R1.2` | document | met | — | n/a | §4.7, L1229-1230, backed per construct by the audit table L1442-1456, each row naming its DASH extension rule. | Caveat: the profile URI (§4.7.10) and the request-type URN (§4.7.11) ride carriers outside R1.2's three-item enumeration; the spec answers at L1400-1401 and `context/08-dash-extension-rules.md` DR-1 sanctions a vendor profile URI, so not scored as a break. DR-10 of that file still says the non-linear resolution document *"declares no profile"*, which v9 contradicts — a `context/` staleness, routed at 5.c. |
| `R1.3` | document | contradicted | 5.c | n/a | §4.5.4, L845-848: *"A slot declaration carrying **no** cap is not a slot this specification defines: the Player MUST present no ads from it and MUST continue with the primary content."* | The criterion forbids altering a pre-existing construct's semantics; the base standard's absent-`@maxDuration` default is quoted by the spec itself at L572-574. §4.8.5 L1581-1582 asserts the opposite general position. The divergence is **mandated by R4.10**, so the build had no way to satisfy both criteria — this is a conflict inside `context/` (A-2), not a build error. Flagged provisional at L851-856 and §8.12. |
| `R1.4` | runtime | met | — | preserved | §7.10, L3593-3594: *"the Player MUST abort that ad and continue the primary content uninterrupted, with no visible artefact."* | Also §4.5.15 L1104-1106 and the §8.2 condition row L3646. |
| `R2.1` | runtime | met | — | lost (A-1) | §4.2, L570: *"**Declares a maximum duration on every slot**, linear or non-linear"*, under *"A conformant Publisher:"* (L561); the not-inferred-at-runtime half at §4.5.2 L773-775: *"Validation is the Player's alone: neither the ADS nor the APS is bound by the Publisher's declarations."* | Substance complete. Force rests on the ISO-style chapeau rather than on a modal — §4.2 carries 0 `MUST` (A-1). |
| `R2.2` | runtime | met | — | lost (A-1) | §4.3, L633-638: *"**The slot cap does not bind the ADS.** … enforcement sits with the Player (§4.5.4) … This sentence bounds a *checker*, not the ADS's behaviour."* | All three clauses present. The criterion's own modal is malformed in `context/` — *"Neither MUST be expected to enforce"* inverts the release it intends (see `context-analysis/conformance-assertions.md` §5). |
| `R2.3` | runtime | met | — | preserved | §4.5.2, L766-769: *"Before anything is rendered, the Player MUST validate each candidate against the declarations of the window that served it: that window's `@allowedLayouts`, its `@maxDuration`, and the admissible creative carriers of §3.3."* | "render only those that satisfy them" carried by §4.5.3 L791-794. |
| `R2.4` | document | met | — | n/a | §4.1, L518-525: *"This specification defines conformance for four roles … Each is checked against a different artefact"*; applied at §4.4 L727-729: *"the resolution document cannot show what the ADS declared, so it cannot carry that obligation."* | The "MUST be rejected or redesigned" half is demonstrated by instance rather than stated as a rule. |
| `R11#p1` | document | met | — | preserved | §2, L178-183: *"IAB VAST 4.x is referenced informatively only. This specification depends on no VAST version"* | Only seven VAST mentions in 8663 lines; none in chapters 4, 5 or 7. |
| `R11#p2` | document | met | — | preserved | §6.6, L3287-3289: *"This specification depends on no version of VAST, and on no particular decision format: the ADS is free to emit another one, and an APS that consumes it is equally conformant."* | — |
| `R11#p3` | document | met | — | preserved | §6.6, L3285: *"**This section is non-normative.** It imposes no obligation on any actor."* | — |
| `R11.1` | document | met | — | n/a | §2, L178-182 (as above). | Verified exhaustively: no normative chapter cites a VAST version as required. |
| `R11.2` | runtime | met | — | lost | §4.3, L647-649: *"The ADS's output format, and the exchange between the APS and the ADS, are outside this specification and agreed bilaterally by those two parties."*; §6.5 table L3278 gives the APS-ADS row as *"**Outside this specification.**"* | The Player has no ADS-facing row in §6.5's interface table, which is what makes the criterion structurally true. The categorical form (*"the Player issues no request to the ADS"*) sits only in Annex O, T-10 L8448, which is informative. |
| `R11.3` | document | partial | 5.b | n/a | Satisfied at §6.6, L3285. **Not** satisfied at §3 Terms, L215: *"It emits a decision document, typically VAST."* | L215 is in neither an annex nor a note flagged illustrative in place; it is rescued only by the document-wide flag at L180-181. One local qualifier closes it. |
| `R18.1` | document | met | — | source-has-no-modal | §6.4, L3241-3244 (the event URL) and §5.2.2 L2108-2111 with the attribute tables at L2209-2255 (the resolution document). | Both Player-visible artefacts specified in full. |
| `R18.2` | scope | met | — | source-has-no-modal | §4.3, L647-649; §1.3 L130-135. | The R29 exception is honoured and the two parameter sources are kept from colliding: §5.8.3 L3015-3019, *"A Publisher authoring a `<RequestParam>` query template (§5.8.1) draws its parameter names from outside the reserved set."* |
| `R29.1` | document | met | — | source-has-no-modal | §5.8.2, L2975-2977: *"The parameters are **inputs about the device** — statements of what it supports — and not conclusions about which ad experiences can be served. Deriving the second from the first is the APS's work."* | "fixed when the syntax is specified" satisfied by the three-row table at L2955-2959. |
| `R29.2` | runtime | met | — | preserved | §5.8.3, L3007-3008: *"Sending a reserved parameter is **OPTIONAL**. A Player conformant to this specification MAY send all of them, some of them, or none."* | Restated at §4.5.1 L756-757. |
| `R29.3` | runtime | met | — | preserved | §4.5.1, L758-760: *"Where the Player has no value for a reserved parameter, or chooses not to disclose it, the Player MUST omit that parameter entirely."* | — |
| `R29.4` | runtime | met | — | preserved | §4.5.1, L760-762: *"A parameter outside the reserved set MUST carry a vendor prefix of the form `x-<vendor>-`, so that names reserved by a later edition stay free."* | — |
| `R29.5` | runtime | force-lost | 5.a (T4) | lost | §4.4, L719-722: *"**The answer depends on no reserved capability parameter.** The APS tolerates the absence of every reserved parameter of §5.8 and produces candidates without receiving any of them"* | Two APS MUSTs arrive in the indicative. §4.4's chapeau is framed around the returned **document**, and tolerance of an absent input is not a property of a document, so the chapeau does not grammatically reach this bullet even under A-1's generous reading. |
| `R29.6` | document | met | — | n/a | §5.8.2, L2983-2992: *"The set is minimal against its acceptance test, which is that the three axes separate the five device classes of §3.4"*, with the five-row table. | Re-derived against §3.4 L462-468: all five declarations are pairwise distinct. Closure argued at L3002-3003. |
| `R29.7` | document | met | — | source-has-no-modal | §5.8.4, L3023-3026 and L3034-3037: *"An APS that resolves conservatively … and an APS that assumes the most capable case are **both conformant**."* | Every clause present, including the two-conformant-APSs consequence. |
| `R4#p1` | runtime | met | — | preserved | §4.5.4, L826-829: *"Where an accepted candidate's actual rendered length exceeds the cap, the Player MUST stop rendering at the bound, even mid-ad, enforcing against actual length rather than declared length."* | — |
| `R4.1` | runtime | met | — | preserved | §7.2, L3366: *"The Publisher MUST declare the slot's cap on the opportunity element"*; §5.1.1 L1740 marks `@maxDuration` *"optional in the base schema; **required under this specification**"*; §5.1.3 L1865 and §5.1.4 L1939 both `Required: yes`. | The only modal is in §7.2 and is scoped to the linear break; non-linear coverage rests on the `Required: yes` rows plus §4.2 L570 (A-1). |
| `R4.2` | runtime | met | — | preserved | §7.4, L3435: *"The Player MUST enforce the slot cap against the sequence's cumulative length."*; §4.5.4 L815-817. | See A-6: L815-817 says "every non-linear family" and L819-820 carves pause out two lines later without saying it overrides. |
| `R4.3` | runtime | met | — | preserved | §4.5.4, L826-828: *"the Player MUST stop rendering at the bound, even mid-ad"*; §7.2 L3372. | The criterion's *"regardless of ADS metadata or candidate count"* clause appears only at §8.2 L3645, which chapter 8 declares non-normative. |
| `R4.4` | runtime | met | — | preserved | §4.3, L633-636; §7.2 L3387: *"The ADS MAY return a decision whose total length exceeds the cap; the cap is enforced downstream, by the Player."* | The criterion bounds a checker and the spec says so in those words. |
| `R4.5` | runtime | met | — | preserved | §4.5.4, L826-829 (as R4#p1). | — |
| `R4.6` | runtime | met | — | preserved | §4.5.4, L811-814: *"The Player MUST honour whichever the event declares — an event declaring `@clip="false"` ending later than the scheduled end is the base specification moving the bound, not the Player exceeding it."* | Same site carries an `[inferred]` on the `@clip="false"` end position (L811) while §5.1.2 L1793-1795 asserts the identical claim untagged. |
| `R4.7` | runtime | met | — | source-has-no-modal | §4.5.4, L843-845: *"A declared cap of zero means the opportunity does not fire, which is the base specification's own rule (DASH §5.16.5.2)."* | Verified in the primary copy: *"If the value of @maxDuration is zero, the event is not executed"*, §5.16.5.2. |
| `R4.8` | document | met | — | source-has-no-modal | §4.2, L570-583, carrying both base-spec quotes the criterion asks for (§5.16.5.2 and §8.1). | — |
| `R4.9` | runtime | met | — | preserved | §4.5.4, L833-838: *"the Player MUST convert the candidate's duration into the cap's timescale, **rounding up** to the next whole unit. A candidate whose converted duration equals the cap exactly is admitted."* | Worked twice in the annexes (C.6 L4619-4626, I.6 L6857-6866). |
| `R4.10` | runtime | met | — | preserved | §4.5.4, L845-848. | Carried as a MUST including the criterion's own provisionality (L851-856, §8.12 L3873-3879). It is what puts R1.3 in conflict (A-2). |
| `R4.11` | runtime | met | — | source-has-no-modal | §4.5.4, L839-842: *"**Cap arithmetic runs on the presentation timeline.** An interval in which that timeline does not advance does not accrue, so a form suspended during a pause (§4.5.9) resumes with the cap it had."* | — |
| `R31.1` | runtime | met | — | preserved | §4.5.1, L748-752: *"The Player MUST request a resolution document when a viewer pause begins inside a pause opportunity window; a pause beginning outside every such window leaves the primary content paused and the Player idle."* | The negative half arrives as the DP-2 positive form. |
| `R31.2` | runtime | partial | 5.c | lost | Half stated: §6.3, L3212-3214: *"The window's `@maxDuration` bounds the display of **one** pause ad before automatic dismissal, and bounds neither the slot nor the pause."* Half exceeded: §4.5.4, L819-820, which assigns the cap a per-ad display semantics R31.2 never grants. | See G-5. The attribute is `Required: yes` on the pause window, "automatic dismissal" is defined nowhere, and no Player obligation obliges it. |
| `R12.1` | document | met | — | n/a | §5.3.3, L2394-2396: *"The admissible values are exactly the tokens below, which map 1:1 onto IAB-defined ad types and visual placements; this specification mints none of them and accepts nothing outside this list."*; §3.2 L381 declares the subclause normative and L386-388 cites the IAB source. | — |
| `R12.2` | runtime | force-lost | 5.b | lost | §3.2, L402-403: *"A Publisher declaring the layouts a window admits draws every token from this table."*; §4.2 L585; §5.1.3 L1866. | Instrument-verified: the intersection of `MUST` lines with `layout|token|enumerat` is empty across all 8663 lines, against a control intersection of 8 lines for `cap`. Both the MUST and the MUST NOT vanish. Compounding it, `@allowedLayouts` is typed *"whitespace-separated token list"* rather than an enum, so nothing enforces it at validation either while `@layout` is closed (§5.3.3). |
| `R12.3` | runtime | met | — | lost (A-1) | §4.4, L694-696: *"**Form metadata is emitted only for accepted ad types**, drawn from the set of §3.2; conformance is checked against the document rather than against the ADS's internal decision."* | Enforced in practice by the closed `@layout` enum plus §4.6's validation MUST (L1167, L1181-1183). |
| `R12.4` | document | met | — | source-has-no-modal | §3.2, L413-419: *"**Spatial bounds are inherited by normative reference.** … This specification introduces no dimensional attribute and re-declares no dimension in the manifest"* | Both worked examples the criterion names (Corner Overlay 25%, L-Shape 60%) appear at L394 and L396. |
| `R15.1` | document | met | — | preserved | §3.3, L448-451: *"These three are the admissible set wherever this document, its annexes and its examples discuss creative carriers."* | Verified empirically over all 8663 lines: the media-type inventory is exactly `video/mp4`, `audio/mp4`, `application/mp4`, `text/html`, `image/{jpeg,png,webp}` and `application/dash+xml`. No fourth carrier leaks into an annex. |
| `R15.2` | runtime | partial | 5.c | lost | APS half: §4.4, L681-683: *"**Creatives are inside the admissible carrier set, on carriers the base standard admits.**"* Publisher half: no passage. | §4.2's Publisher list carries no creative-carrier obligation, and §5.1.3 / §5.1.4 give the Publisher no form-declaring attribute at all — only `@allowedLayouts`. The criterion's *"forms declared by the Publisher"* has no construct to attach to, which reads as a stale clause in `context/` rather than a spec omission. |
| `R15.3` | runtime | contradicted | 5.b | strengthened | §4.5.2, L766-771: *"Before anything is rendered, the Player MUST validate each candidate … A candidate that satisfies them is eligible; one that satisfies none is skipped"* | The criterion grants a permission (MAY skip); the spec removes the discretion. Direction is strengthening, so nothing is lost operationally, but a Player conforming to R15.3 violates §4.5.2 (A-5). The same sentence is the site of EC-1. |
| `R5#p1` | runtime | met | — | preserved | §4.5.3, L780-782: *"The Player MUST walk the options in document order and render the **first** that satisfies both"* | — |
| `R5#p2` | runtime | met | — | preserved | §4.5.3, L791-794. | — |
| `R5#p3` | runtime | met | — | preserved | §4.5.3, L783-789, naming the two checks — the device budget of §3.4 and the window's `@allowedLayouts` by exact token comparison. | — |
| `R5.1` | runtime | met | — | preserved | §7.3, L3413-3415: *"The APS MUST carry the options as an ordered list in preference order; a candidate carrying exactly one option is equally conformant and places the suitability call with the APS."* | Cardinality at §4.4 L676-677. |
| `R5.2` | runtime | met | — | preserved | §4.5.3, L780-783. | — |
| `R5.3` | runtime | met | — | preserved | §4.5.3, L792-794: *"the Player MUST skip that candidate and continue with the next. Once every candidate has been walked, the Player MUST continue with the primary content."* | — |
| `R5.4` | runtime | partial | 5.b | lost | ADS half: §4.3, L639-642: *"**The ADS holds no device-capability view.** Producing candidates without a device-class matrix is conformant; holding one is equally conformant"*. APS half: no statement. | The criterion names both actors. Instrument-verified: `device-class matrix|capability view|per-Player` returns exactly the two §4.3 lines across the whole file. §5.8.4 L3028-3031 mentions *"an APS … when it holds no device view at all"* as an aside inside a different rule, not as the release. |
| `R5.5` | runtime | met | — | preserved | §4.4, L674-679: *"**Presentation options are an ordered list in preference order.** … no maximum, no minimum beyond one."* | — |
| `R5.6` | runtime | met | — | preserved | §4.5.3, L780-791, ending *"An option failing either check is passed over and the Player evaluates the next in document order."* | The criterion's MUST NOT arrives as the DP-2 positive form. |
| `R5.7` | runtime | met | — | preserved | §4.5.3, L792-794; order preservation on fall-through at §4.5.5 L863-866. | — |
| `R7#p1` | runtime | met | — | preserved | §4.5.5, L860-861: *"The Player MUST present the candidates of a resolution document in the order the document declares, each starting when the previous ends."* | — |
| `R7#p2` | runtime | met | — | preserved | §4.5.5, L864-866. | Polarity flipped per DP-2; the modal survives. |
| `R7.1` | runtime | met | — | preserved | §4.5.5, L860-861. | — |
| `R7.2` | runtime | met | — | preserved | §4.5.5, L862-863: *"It MAY drop a candidate with no satisfiable presentation option (§4.5.3)"* | — |
| `R7.3` | runtime | met | — | preserved | §4.5.5, L863; §4.5.4 L822-824: *"**Drop before play.** The Player MAY drop a candidate before playback when its declared duration would push the cumulative duration past the cap."* | — |
| `R7.4` | runtime | met | — | preserved | §4.5.5, L863-866: *"the Player MUST preserve the declared order of the surviving candidates, presenting each exactly once."* | All three prohibitions survive in positive form. The "exactly once" clause is what collides with `repeat` (EC-2, T2) — the collision is with R32.1, not with this criterion. |
| `R7.5` | runtime | met | — | preserved | §4.5.4, L826-829; §7.2 L3380-3382. | — |
| `R30.1` | runtime | force-lost | 5.b | lost | §4.4, L667-672: *"**An unfilled opportunity is a document carrying no candidates** — well-formed, complete, served `200` with a body."*; §5.2.3, L2257-2261: *"not a `204`, not a `404`, not an error status."* | Substance complete on both sides and both sites are in normative chapters, but no modal binds the APS anywhere. Chapter 7 never restates it: the only chapter-7 hits are the Player-side failed-execution list at L3529-3531. |
| `R30.2` | runtime | met | — | preserved | §4.5.6, L940-943: *"A conformant Player MUST apply the same rule to the windows defined here: an attempt that produced no ad leaves a once-only window executable."* | Both base-spec quotes present and verified against the primary copy (§5.16.2.2.2 counter; §5.16.2.2.6 NOTE 3, *"The counter E.c has not been incremented due to the failure"*). |
| `R3.1` | document | met | — | n/a | §7.2 L3360-3364 (linear, class-invariant), §7.3 L3399-3407, §7.5 L3449-3455, §7.6 L3469-3475 — a per-class table for each opportunity type; classes enumerated at §3.4 L462-469. | All four opportunity types are enumerated per class in normative chapter 7. The pause enumeration is the one contradicted downstream (EC-4). |
| `R3.2` | runtime | partial | 5.a (T1) | preserved | Obligation stated: §4.5.3, L791-794. Definedness not delivered: §5.3.7.3, L2570-2572: *"Every layout-and-form pair has a row, so a Player of any class has a defined outcome for every opportunity"* | That claim is falsified by its own table twice over. (a) §5.3.7.3 L2588-2590 disagrees with §3.4 L485 and §7.6 L3472-3475 on `pause-fullscreen` for D2, D4 and D5 (EC-4). (b) The table has no row for `linear` with an `image` or an `html` creative, while §3.4 L480 gives both D1..D5 — so two layout-and-form pairs have no row at all. §4.5.3 L784-785 sends the Player to this table, so the indeterminacy is the operative one. |
| `R3.3` | runtime | met | — | preserved | §4.5.3, L780-785: *"the Player renders only a form and layout whose decoder and compositing budget its device class supplies (§3.4)"* | "renders only" inside the MUST carries the prohibition; no separate MUST NOT is needed. |
| `R16.1` | runtime | met | — | preserved | §4.5.10, L993-995: *"The Player MUST dismiss any rendered pause ad within one rendering frame of the pause-to-play transition"* | Restated §7.6 L3479-3480. |
| `R16.2` | runtime | met | — | preserved | §4.5.10, L995-997: *"and MUST stop firing the beacons scheduled for it from that transition onward"* | Matches the criterion's out-of-scope carve-out for later beacons. |
| `R32.1` | runtime | force-lost | 5.b | lost on the APS half | APS half, §4.4 L711-712, indicative: *"**Every pause resolution document declares an exhaustion behaviour**, in `@onCandidatesExhausted`."* Player half, §4.5.11 L1028: *"Where the document declares nothing, the Player MUST apply `stop`"* | The APS half rests on §4.4's chapeau alone (A-1), and two sites pull against it: §5.2.2 L2224 marks the attribute `Required: no`, and Annex O T-16 (L8459) accepts *"or omits it and is read as `stop`"* as conformant — so the only executable check of the obligation passes on the behaviour it forbids. |
| `R32.2` | runtime | met | — | preserved | §4.5.11, L1022-1024: *"where that request returns a document carrying no candidates, the Player MUST apply `stop` for the remainder of that pause"* | — |
| `R32.3` | runtime | met | — | preserved | §4.5.11, L1032-1033: *"On resume the Player MUST return to the primary content immediately, including mid-presentation."* | Restated §7.6 L3480-3481. |
| `R32.4` | scope | gap | 5.c | source-has-no-modal | No passage. §1.3 (L119-160) lists seven exclusions and this is not among them; no other site addresses whether a second request inside one pause is the same opportunity or a new one. | See G-4. A reader cannot tell the silence was chosen. |
| `R34.1` | runtime | met | — | preserved | §4.2, L603-605: *"**MAY bound a pause window to once per session**, with `@executeOnce="true"`; a window that omits it yields a pause ad on every qualifying pause."* | Consistent with §5.1.4 L1942 (`Required: no`, default `false`). |
| `R34.2` | runtime | met | — | preserved | §4.5.11, L1037-1040: *"the Player MUST present at most one pause ad for that window for the session, and MUST leave the primary content uninterrupted on a later qualifying pause inside it."* | — |
| `R34.3` | runtime | met | — | source-has-no-modal | §4.5.11, L1040-1043: *"The window is consumed when a pause ad **begins rendering**, so a pause that resolves to no renderable candidate leaves it available"* | Stated three times consistently (§4.5.11, §5.1.4 L1942, §7.6 L3488-3494) and grounded on the base standard's counter rule. |
| `R34.4` | document | met | — | source-has-no-modal | §5.1.4, L1945-1953: *"**The once-per-session bound reuses the baseline capability with the render event substituted for the playhead event.** `@executeOnce` keeps its baseline name, type and default because it is the same capability"* | — |
| `R19#p1` | runtime | met | — | preserved | §4.5.12, L1047-1050: *"The Player MUST render every ad form, linear or non-linear, at the playback speed of the primary content at the moment the ad is presented"* | — |
| `R19.1` | runtime | met | — | preserved | §4.5.12, L1047-1050; restated §7.11 L3603-3605. | — |
| `R19.2` | runtime | met | — | preserved | §7.11, L3603-3605: *"following that speed where it differs from 1x"* | The criterion's MUST NOT arrives as an equivalent positive MUST that targets the forbidden behaviour directly. |
| `R19.3` | runtime | met | — | preserved | §4.5.12, L1054-1059: *"The Player MUST derive the wall-clock on-screen length as `duration / playback_speed` … Cap enforcement (§4.5.4) and beacon scheduling (§4.5.13) run on the presentation timeline."* | Both halves present. |
| `R19.4` | runtime | met | — | preserved | §4.5.12, L1052-1055: *"A form's declared `duration` is a value on the **presentation timeline** for every form, including `image` and `html`, which have no intrinsic media."* | — |
| `R21.1` | runtime | met | — | preserved | Both surfaces admissible: §5.1.4 L1940. Release: §7.6 L3475, *"which the Player MAY render by releasing the primary content's resources"*, and §3.4 L502-503. Single active form during a partial pause ad: §4.5.8 L961-962 with §4.5.9 L977-980. | All three clauses carried with the right modal. It is R21.1's release clause that puts the spec at odds with UC-05's D5 row (see UC-05). |
| `R25#p1` | runtime | met | — | preserved | §4.5.10, L999-1001: *"**In live content the Player MUST keep its presentation time frozen inside the pause window for the duration of the pause**, even as the live edge advances in wall-clock time."* | — |
| `R25.1` | runtime | partial | 5.c | preserved on the freeze | Freeze: §4.5.10 L999-1001. Narrowing: §4.5.10 L1006-1008: *"**That freeze is bounded by the time-shift buffer.** Where the pause outlives the buffer, the resumption point is clipped to the buffer edge"* | The criterion says *"for the full duration of the pause"* with no bound; the spec bounds it, correctly citing the base standard's clipping rule (verified in the primary copy, §5.16.2.2.5), and then leaves the boundary behaviour an open point in a non-normative chapter (§8.9 L3815-3818). `context/` never mentions a time-shift buffer, so the narrowing has no requirement behind it (EC-3). The criterion's second sentence appears only in the indicative (L1010-1012, §7.6 L3486-3487). |
| `R26.1` | runtime | met | — | carried as a schema constraint | §5.3.7.2, L2558-2561: *"**It is a composition attribute of the layout, not a presentation option.** The Player does not walk it the way it walks the ordered options of §5.3.5"*; cardinality §5.3.1 L2339; removal analysis §4.7.6 L1322-1323. | Re-derived, not inherited from the earlier iteration that scored it `contradicted`. The criterion forbids one thing — carrying the background *as a separate presentation option* — and the element is never an entry in the walk list. See A-3 for the residual ambiguity in the criterion's own wording, and the note under `R26.3` for the effect the two-token split has. |
| `R26.2` | runtime | force-lost | 5.c | lost | §5.3.7.2, L2536-2539: *"A **background element** MAY fill those bands; where none is present they render as black."* | Three Player MUSTs in the criterion, zero in the spec, and §1.3 L152-160 pulls the other way: *"The composition of two visual surfaces is likewise left to the implementation."* Either that delegation is the intended position and R26.2 is wrong in `context/`, or chapter 7 needs the rows (A-8). |
| `R26.3` | runtime | met | — | preserved via §4.5.3 | §5.3.7.3, L2585-2587 (budget rows: `video` D1; `image` D1, D3, D4; `html` D1, D3, each naming the image surface for the background), enforced by §4.5.3 L784-785; still-image constraint §5.3.7.2 L2553-2554; D2 exclusion reasoned at L2599-2601. | Matches the criterion row by row, element-type-not-count reasoning included. Side effect worth a WG note: splitting the layout into two tokens (§3.2 L397-398) means a candidate offering the box with and without a background emits two otherwise identical options — Annex J L7051-7053 — so the presence of the background is in practice resolved by the very walk §5.3.7.2 L2559 says it is not subject to. |
| `R27.1` | runtime | met | — | source-has-no-modal | §5.3.7.1, L2515-2518: *"An L-shape presentation option carries exactly **one** ad creative — a single URL carrying an image, a video or an HTML creative — and that creative is placed full-frame in the background."*; ownership at L2529-2531. | Enforced structurally by §5.3.1 L2330-2339: one `@form`, one `@assetUrl` or one `<ImportedMPD>` per option, so an APS cannot emit two creatives on one L-shape option. |
| `R27.2` | runtime | force-lost | 5.c | lost | §5.3.7.1, L2518-2521: *"The shrunk primary content is composited **on top of** it, in one region of the screen"* | No Player MUST for L-shape composition in chapter 4 or 7. The criterion's *"occupying its **declared** region"* has nothing behind it either: §5.3.7 L2508-2512 states *"**This specification declares no positioning vocabulary**: no coordinates, no dimensions, no anchors, no z-order attribute."* Same root as R26.2 (A-8). |
| `R27.3` | runtime | met | — | preserved via §4.5.3 | §5.3.7.3, L2579-2581: `squeezeback-l-shape` `video` → D1, D2; `image` → D1, D3, D4; `html` → D1, D3, enforced by §4.5.3 L784-785. | Consistent with §3.4 L482. This is the one layout whose two budget tables agree. |
| `R14.1` | runtime | met | — | preserved | §4.5.5, L860-861: *"The Player MUST present the candidates of a resolution document in the order the document declares, each starting when the previous ends."* | — |
| `R14.2` | runtime | met | — | preserved | §7.4, L3435; §4.5.4 L815-816; trim MUST at §4.5.4 L826-827. | — |
| `R14.3` | document | met | — | n/a | §7.4, L3436-3438: *"No construct here expresses concurrent composition of two non-linear forms, which leaves the single-active-form bound with nothing to author around it."* | `<svta:BackgroundElement>` explicitly declassified as a form at §5.3.7.2 L2558. |
| `R17.1` | runtime | met | — | source-has-no-modal (spec is stronger) | §4.5.9, L975-980: *"The Player MUST: — **suspend a coexisting overlay** and present the pause ad, whatever the pause ad's surface"* | — |
| `R17.2` | runtime | met | — | source-has-no-modal | §4.5.9, L983-985: *"on resume, **dismiss the pause ad within one rendering frame**, stop its remaining beacons, and **restore the suspended form only while its window is still open**"* | Also §7.7 L3509-3511. |
| `R17.3` | runtime | met | — | source-has-no-modal | §4.5.9, L985-986: *"where that window expired during the pause, the Player MUST keep the surface clear"* | — |
| `R17.4` | document | met | — | source-has-no-modal | §4.5.9, L988-989: *"This priority is not configurable: this specification carries no construct by which the Publisher, the ADS or the APS inverts it."* | Repeated §7.7 L3515-3516. |
| `R17.5` | runtime | met | — | source-has-no-modal | §4.5.9, L981-982: *"**suspend a linear ad that occupies the screen**, resuming it from the point at which it was suspended when the viewer resumes"* | §7.7 L3507-3508 carries it too. |
| `R20.1` | runtime | met | — | preserved | §4.5.6, L889-892: *"An attempt on a window that produces no ad is a **failed execution**, and on a failed execution the Player MUST attempt the next window of the family"*, with the five conditions at L900-914 and the end-of-chain MUST at L927-930. | The spec adds the wrong-family condition (R20.4) as a fifth. Both base-spec quotes verified against the primary copy (§5.16.2.2.5, §5.16.2.2.6). |
| `R20.2` | runtime | force-lost | 5.b | lost | §4.2, L592-593: *"**Authors all windows of one family that share a `<Period>` as `<Event>` entries inside a single `<EventStream>`**"*; §5.1.6 L2002-2003: *"All windows of one family in a `<Period>` **are authored** in a single `<EventStream>`"* | Criterion says "MUST be authored". Instrument-verified: `clustered` / `one Event Stream` returns L593, L2003, L4257, L7475, L8432, every one indicative or a quotation of the base standard. The DASH sentence it rests on is exact (verified: *"all Events of one type shall be clustered in one Event Stream"*). |
| `R20.3` | runtime | met | — | source-has-no-modal | §4.5.6, L878-880: *"The Player MUST order the overlapping windows by presentation time, oldest first, breaking ties by the order in which the events appear inside the `<EventStream>`."* | — |
| `R20.4` | runtime | met | — | preserved | §4.5.6, L921-925: *"The Player MUST treat it as a failure to resolve and continue down the chain; reading it as an empty resolution would let one misrouted response silence every remaining window"* | The spec follows R20.1 and R30, which is the reading `context-analysis/conformance-assertions.md` §5 identifies as correct; R20.4's own explanatory prose in `context/` is the stale half and says the chain ends. Routed at 5.c under the `context/` cluster. |
| `R20.5` | runtime | met | — | source-has-no-modal | §4.5.7, L949-951: *"When the Player falls through to a second window, it MUST validate that window's candidates against that window's declarations."* | — |
| `R20.6` | document | met | — | n/a | §4.5.7, L955-957: *"This is a Player obligation and is stated as one: a rule that decides which presentation option reaches the screen binds only where it can be obeyed, and an illustration is read rather than obeyed."* | §4.5.7 is normative and carries R20.5 as a MUST; §7.8 L3539-3541 restates it. The change of status R20.6 asks for happened. |
| `R22.1` | runtime | met | — | preserved | §4.5.8, L961-962: *"At any instant the Player MUST keep at most **one** non-linear ad form active on the screen."* | The criterion's second half is subsumed by "at most one". |
| `R6#p1` | document | met | — | preserved | §5.5, L2666-2672 (carrier), §5.5.2 L2710-2714 (the two admissible positions), §5.5.3 L2742-2746 (timebase). | — |
| `R6#p2` | runtime | partial | 5.c | lost | §4.1, L546-553, which recasts the obligation on the author and argues the Player-side half *"is not available to be made"*. | No Player obligation to safely ignore unknown namespaces exists in chapters 4-7; the behaviour is stated only at §8.2 L3647 and in Annex O, both non-normative. Same root as R1.1 and R6.4 (A-7). |
| `R6.1` | document | met | — | preserved | §5.5, L2666-2667: *"Timeline-scheduled beacons — impression, start, quartiles, complete — ride the callback event scheme of DASH §5.10.4.5."*, with the carrier shape at §5.5.1 and the positions table at §5.5.2. | — |
| `R6.2` | runtime | met | — | hardened; no modal used | §4.4, L698-700: *"**Beacons are callback events on the ad's presentation timeline** — `<Event>` entries inside an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015`"*; §5.5.1 L2688 binds `@schemeIdUri` *"for every tracking carrier under this specification"*. | The criterion is a SHOULD; the spec states it as an exceptionless condition, in the indicative. `SHOULD` occurs three times in 8663 lines and none of them is this. |
| `R6.3` | document | met | — | n/a | §5.5, L2667-2668: *"**This specification mints no tracking scheme.**"* | Met by compliance. The escape hatch itself is absent: `gap analysis` returns 0 hits in the spec against 2 in `context/03-requirements.md` (control verified), so a future editor reading only the spec finds no gate to pass. |
| `R6.4` | runtime | partial | 5.c | lost | §8.2, L3647: *"Ignores the unknown construct with its whole subtree and keeps playing the primary content"* — chapter 8, which L3619-3621 declares non-normative. | §4.7 covers the **author's** removal-safety duty (DASH §5.2.1), a different obligation on a different actor. Same root as R6#p2 and R1.1 (A-7). |
| `R6.5` | runtime | met | — | preserved | §4.5.13, L1076-1078: *"Two beacons carrying the same `@id` in two different candidates of one document are two distinct beacons and the Player MUST fire both."* | Within-candidate collapse at L1074-1076; §5.5.4 L2770-2775. |
| `R6.6` | runtime | met | — | source-has-no-modal | §4.5.13, L1069-1072: *"the Player MUST resolve its presentation times against **that candidate's own presentation**, rather than against a `<Period>` the carrier does not sit in."* | — |
| `R6.7` | document | met | — | preserved | §4.6, L1160-1162 and L1167-1168: *"a procedure that claims to validate a resolution document MUST perform them"*, with four numbered steps and the default failure named at L1195-1198. | The criterion's own wording, satisfied normatively. What the steps depend on does not exist — see G-1. |
| `R13#p1` | document | met | — | preserved | §4.5.13, L1063-1067: *"the Player MUST execute the tracking schedule the resolution document carries, firing each beacon at its specified relative time. The schedule is the ADS's; this specification fixes the carrier and the timebase rather than the fractions, the granularity or the count."* | — |
| `R13.1` | runtime | force-lost | 5.b | lost | §4.4, L698-701: *"**Beacons are callback events on the ad's presentation timeline** … timed relative to the presentation of the ad that carries them."* | Criterion places a MUST on the APS. Restated absolutely but modally at §5.5.3 L2742-2744. Only two `APS MUST` exist in the document (L3413, L3436) and neither is this. |
| `R13.2` | runtime | met | — | preserved | §4.5.13, L1063-1065. | — |
| `R13.3` | runtime | force-lost | 5.a (T3) | lost | §4.5.13, L1081-1083: *"**Where the ad stops early, the beacons stop with it.** Beacons scheduled past a trim boundary (§4.5.4) … fall outside the ad's active window."*; §4.5.4 L829-830. | The nearest modal is a participial clause at §7.2 L3381-3382 where the MUST governs the trim, not the beacons. Contrast §4.5.10 L995-997, where the structurally identical pause case does carry *"MUST stop firing the beacons"* — two adjacent cases, two force levels. |
| `R13.4` | document | met | — | preserved | §5.5, L2667-2668; §2.1 L200-201 lists the callback scheme among the URIs reused without redefinition. | The two new event schemes are opportunity-declaration schemes, not tracking ones. |
| `R13.5` | runtime | met | — | source-has-no-modal | §4.4, L727-729: *"The conversion from the ADS's decision format, and the fidelity of that transcription, sit in the APS-to-ADS contract: the resolution document cannot show what the ADS declared, so it cannot carry that obligation."* | Explicitly located outside, with the reason, in a normative chapter — not silently dropped. |
| `R23.1` | document | met | — | preserved | §5.7, L2851-2856 (four elements, 0..1 each, in the extension namespace) and L2858-2859: *"**Emitting and reading are both optional.** Nothing obliges an APS to emit these elements or a Player to read them"* | — |
| `R24#p1` | document | force-lost | 5.b | lost | §4.4, L690-692: *"A still image or an HTML document travels as an attribute value on `<svta:RenderableAsset>`, which is foreign-namespace open content and inherits no media-type constraint to escape."* | The prohibition itself is nowhere in chapters 4-7; the positive carrier is. |
| `R24#p2` | document | force-lost | 5.b | lost | §5.3.2, L2360: *"**(a)** Foreign-namespace open content … **Selected.**"*, with the four-carrier comparison at L2358-2363. | Same unit sentence as `R24#p1`; the DR-6 enumeration is present and correct. |
| `R24.1` | runtime | force-lost | 5.b | lost | §4.4, L690-692; §5.3.2 L2350-2354: *"The media axis is closed to non-MP4 media types along the whole resolution path"* | The MUST NOT appears only at §8.2 L3644 and Annex O E-09 / T-15, all non-normative. Compounding it, the supporting cross-references at L2103, L2351 and L2367 point at §4.7.2 and §4.7.3, which in v9 are `<svta:PauseAdPresentation>` and `<svta:OverlayList>` and mention no media type — the constraint they mean is at §4.4 L683-692 (T4). |
| `R33.1` | document | met | — | preserved | §5.9, L3043-3044: *"Pause-ad delivery is measured with the base specification's play-list metric, and this specification defines no metric of its own."* | Also §4.5.16 L1120-1122. |
| `R33.2` | runtime | met | — | preserved | §4.5.16, L1120-1122 and L1138-1140: *"A playback period whose stretch stopped on `Rebuffering` is a stall rather than a pause opportunity, and the Player MUST derive no paused interval from it."* | The `Rebuffering` exclusion survives as a positive MUST despite the document carrying no MUST NOT at all. |
| `R33.3` | document | met | — | source-has-no-modal | §5.9, L3073-3080: *"**How a measurement reaches anyone is out of scope**"*, with the base standard's own position quoted. | Verified against the primary copy, §5.9.1. |
| `R33.4` | runtime | force-lost | 5.b | lost | §4.2, L597-602: *"**Requests the play-list metric on content carrying pause windows**, through the `<Metrics>` element of the main MPD."*; §5.9 L3060-3061. | Both loci indicative. §4.2's bullet even reproduces the criterion's own rationale. The only `Publisher MUST` in the document is L3366, about the cap. |
| `R28#p1` | document | force-lost | 5.b | lost | §5.6, L2785-2787: *"The resolution document carries the ad's ClickThrough URL and its click-tracking URLs in a single carrier, so that a Player conformant to this specification reads them the same way."* | Indicative in §5.6 and in §4.4 L706. The Player-side half does carry its MUST (§4.5.14 L1093-1096), so only the document-side obligation is unmodalised. |
| `R28.1` | document | force-lost | 5.b | lost | §4.4, L706-709: *"**The ClickThrough and its click-tracking travel in `<svta:Click>`.** … a ClickThrough carried elsewhere is a violation the document itself shows."* | Carrier fully defined at §5.6.1 L2809-2818. Force rests on §4.4's chapeau (A-1). |
| `R28.2` | runtime | met | — | preserved | §4.5.14, L1093-1096: *"a Player conformant to this specification MUST read the ClickThrough URL and, on viewer activation, open it or hand it to the platform, and fire every `<svta:ClickTracking>` URL the element carries."* | Scoping argued at §4.1 L527-553 and §5.6.1 L2821-2829. |
| `R28.3` | scope | met | — | source-has-no-modal | §4.4, L727-729; reinforced §4.3 L647-649. | Same pattern as R13.5 — the obligation is located outside with its reason, not dropped. |
| `R8.1` | document | partial | 5.b | preserved | §4.8, L1466-1469: *"This section records, for every construct introduced here, why an existing construct of the base standard could not carry it"* | 10 of the 12 constructs §4.7.13 enumerates are covered by §4.8.1-§4.8.2. **Two are not named in §4.8**: the two event scheme URIs (row L1452) and the resolution-document profile URI (row L1453). Both have substantive rationale elsewhere (§5.1.3 L1811-1825; §5.2.2 L2145-2158), so this is a register gap rather than an unjustified construct — but R8.1's register is what a reviewer reads. `@form` (§5.3.1 L2332) has no justification anywhere. |
| `R8.2` | document | met | — | preserved | §4.8.3-§4.8.10, L1522-1682: eight constructs weighed and not taken, ending L1679-1681: *"a construct simply absent from a specification says nothing about whether anyone considered it."* | Plus `BaseURL` alternatives at §5.1.6 L2020-2026. The strongest area of the document. |
| `R9.1` | document | met | — | preserved | §5.1, L1709: *"**The event machinery is reused, not extended.**"*; §4.8.1 L1471-1494 reuses the two alternative-MPD elements, the callback scheme and the play-list metric unchanged. | — |
| `R9.2` | document | met | — | preserved | §4.8.2, L1501-1506: *"Extending the alternative-MPD elements to mean both would give one element two execution models, and a reader would have to consult an attribute to learn which."* | — |
| `R9.3` | document | met | — | preserved | §4.8.2, L1513-1515: *"There is nothing on that axis to relax; there is something absent from it."*; §4.8.1 L1487-1489: *"the one property needed beyond it — a de-duplication key — is obtained by narrowing an existing optional attribute to required."* | Extension-before-invention considered and its outcome recorded. |
| `R10.1` | document | met | — | preserved | §5.3.7, L2507-2509: *"Spatial arrangement inside a layout is delegated to HTML5 and CSS and to the IAB-defined layout the token names."* | Echoed §1.3 L124-126. |
| `R10.2` | document | met | — | preserved | §5.3.7, L2508-2510: *"**This specification declares no positioning vocabulary**: no coordinates, no dimensions, no anchors, no z-order attribute."* | §4.8.4 L1555-1561 records why SRD was not reused, on the same ground. |
| `R10.3` | document | met | — | source-has-no-modal | §3.2, L386-388: *"This specification adopts those identifiers and defines **no** ad type and **no** layout value of its own."*; §3.2 L417-419. | The token strings are minted here in kebab-case; their semantics and spatial bounds are inherited by normative reference. |
| `OOS-1#p1` | scope | met | — | n/a | §1.3, L124-126: *"**A parallel layout engine.** Spatial arrangement is delegated to HTML5 and CSS and to the IAB-defined layouts named in §3.2; a second layout standard would compete with them rather than complete them."* | Plus §5.3.7 L2508-2510. |
| `OOS-4#p1` | scope | met | — | n/a | §1.3, L135-138: *"Raw scripts, vector payloads, documents and proprietary binary creatives are outside the admissible set of §3.3; a sender needing a scripted creative wraps the script in an HTML document and uses the HTML form."* | Also §3.3 L446 and §5.3.2 L2347. |
| `UC-01` | use-case | met | — | n/a | Annex A, L3901-4068, with §A.6 L4058-4067: *"The outcome is identical on all five device classes D1 to D5 (§3.4)."* and the reason (a linear ad needs no second decoder and no overlay surface). | All five classes present and each says what UC-01 says: the same full-screen pre-roll, then the primary content. |
| `UC-02` | use-case | met | — | n/a | Annex B, L4069-4232, with §B.6 L4221-4231: *"As in Annex A, the outcome is the same on D1 to D5."*, naming the decoder hand-off on D3-D5 and the optional pre-buffer on D1-D2. | Matches UC-02 including its D2 pre-buffer note. The trick-play variant is carried by §7.11 and §4.5.12. |
| `UC-03` | use-case | met | — | n/a | Annex C, §C.5.1-§C.5.6, L4531-4609, with the per-class summary at L4603-4609: D1 and D2 the video L-shape, D3 the HTML corner, D4 the image lower third, D5 skipped. | Five classes walked option by option against a stated budget. D5's decline is stated as a defined result, not a failure (L4595-4599), which is what UC-03's D5 row says. |
| `UC-04` | use-case | met | — | n/a | Annex D, §D.6.1-§D.6.6, L4922-4979, summary L4975-4979: D1 and D2 the video lower third, D3 the HTML lower third, D4 the image corner, D5 the linear ad alone. | Matches UC-04 row for row, including the point the case's own note settles — D3 and D4 are not excluded from a hybrid break — with the base standard's listen-mode clause quoted (verified in the primary copy, §4.2). |
| `UC-05` | use-case | contradicted | 5.c | n/a | Annex E, §E.5.5, L5322-5330: *"PA-3 is a `pause-fullscreen` `video` option, and this is where the fullscreen surface earns its place … the Player MAY release the primary content's decoder and buffers and give the decoder to the ad. D5's single decoder is enough. **PA-3 wins.**"* | All five classes are walked, but D5 says the opposite of what the case says. `context/04-use-cases.md` UC-05 D5: *"no overlay capability of any kind. Per R3, declines the pause-ad opportunity entirely. What the user sees: nothing."* The spec's position is grounded in R21.1, which permits releasing the primary content's resources *"to present a fullscreen video, image, or web page"*. So `context/` conflicts with itself and the build followed the requirement over the use case. UC-05's D5 row is the half that has to move. |
| `UC-06` | use-case | met | — | n/a | Annex F, §F.6 L5704-5712: *"The outcome is the same on D1 to D5 … On D1 and D2 the second decoder may pre-buffer ad N+1 while ad N plays; on D3, D4 and D5 the single decoder is reused between ads."* | Matches UC-06, cap arithmetic included. |
| `UC-07` | use-case | met | — | n/a | Annex G, §G.9 L5964-5974: *"The outcome is identical on D1 to D5, and for a different reason than in the linear annexes: here it does not depend on the hardware at all."*; the content-dependent Publisher choice at §7.9 L3568-3577 and §G.7. | Both branches the case names — live as an expected loss, on-demand with a baseline break authored alongside — are carried, and §G.3 shows the document after namespace removal. |
| `UC-08` | use-case | partial | 5.c | n/a | Annex H, §H.5.1-§H.5.6, L6314-6386, summary L6380-6386. | All five classes are walked and the cross-family priority is stepped through at §H.6. Two rows do not say what the case says. D2 and D5 render an overlay (a `linear` takeover) and a `pause-fullscreen` video pause ad where UC-08 declines both. The overlay half is authoring, not disagreement — the annex's window admits `linear` (L6028) and UC-03's Publisher intent does not — but the pause half is the same D5 conflict as `UC-05`, so the case's D5 row and the annex cannot both stand. |
| `UC-09` | use-case | met | — | n/a | Annex I, §I.5.1-§I.5.6, L6748-6851, summary L6829-6836: D1 option 1, D2 option 4, D3 and D4 option 2, D5 option 4. | Identical to UC-09's own outcomes, reached by the same reasoning, including the instructive D2 case where two decoders still lose to a non-video third element. |
| `UC-10` | use-case | met | — | n/a | Annex J, §J.5.1-§J.5.6, L7099-7196, summary L7180-7187. | Matches UC-10: D1 renders, D2 declines on the background element, D3 and D4 render the image variant, D5 declines. The two independent budgets are separated explicitly at L7189-7191. |
| `UC-11` | use-case | met | — | n/a | Annex K, §K.8 L7440-7455: *"Which option renders varies by class; what happens on activation does not."*, with the five-row table; the obligation itself at §4.5.14 L1093-1096. | Includes the case's backward-compatibility note (§7.9 L3583-3585) and its no-click-tracking variant (§K.7). |
| `UC-12` | use-case | met | — | n/a | Annex L, §L.4 (per-attempt failure modes), §L.5 (wrong family), §L.6 (no candidates), §L.7 (each window binds its own), §L.8 L7776-7782: *"Which window is served does not vary across D1 to D5."* | All three paths the case admits are walked. The exhaustion path is carried normatively at §4.5.6 L927-930 and §7.8 L3542-3546. |
| `UC-13` | use-case | met | — | n/a | Annex M, §M.3 and §M.5 L8114-8127, whose five-row table gives D1 option 1, D2 option 4, D3 option 2, D4 all four options emitted and option 2 rendered, D5 option 4. | Identical to UC-13, including the D4 row where the Player declares nothing and the APS therefore emits the UC-09 document. |
| `UC-14` | use-case | met | — | n/a | Annex N, §N.8 L8363-8380: D1 and D2 the video corner overlay, D3 the HTML lower third, D4 the image corner, D5 declined. | Matches UC-14 row for row, and §N.7 carries the case's own point that the cap and the layouts come from the overlay window while the replacement carries none of an ad's obligations. **This is the row `validate-spec.prompt` §4.1 predicts will be `gap`**; it is not, and the prompt's paragraph is what is stale (A-10). |

## Disposition of findings

Every Gap, Edge case and Ambiguity of §1-§3, and every §4 row whose verdict is
not `met`, is routed below. The conformance-audit and detail-review items §5
items 3 and 4 ask for **could not be routed**: those two sidecars are produced
at Steps 7.5 and 8 and do not exist at Step 7. See A-9 — the omission is a
contract defect, not an incomplete walk.

| Bucket | Who closes it |
|--------|---------------|
| `5.a` | the pipeline — nobody has to decide anything |
| `5.b` | the owner of the specification |
| `5.c` | the owner, then a major build |

**Why so few blocking rows reach 5.a.** Of the 21 blocking rows, 14 of the 16
`force-lost` share one cause (A-1): §4.2, §4.3 and §4.4 carry no RFC 2119 modal
at all. The remedy is not a wording edit at a cited location — it is a decision
about whether an ISO-style conformance chapeau binds in the indicative, which
changes the force of roughly forty statements at once. That is 5.b by
construction. The two `force-lost` rows whose remedy is local and independent of
that decision (`R13.3`, `R29.5`) do take 5.a slots.

### 5.a Actionable TODOs (5)

| #  | Finding ref | Criterion | Spec section | Concrete edit | Citation |
|----|-------------|-----------|--------------|---------------|----------|
| T1 | `EC-4`, `R3.2` | 3 — internal contradiction, one reading matches `context/` | §3.4 L485, §7.6 L3472-3475, §5.3.7.3 L2588-2590 | Make the three `pause-fullscreen` rows agree. For `image` and `html`, adopt §5.3.7.3's values (`image` → D1, D3, D4; `html` → D1, D3) and correct §3.4 L485 and the D2 and D4 cells of §7.6, because `context/04-use-cases.md` UC-05 D2 and D4 decline an image-or-HTML-only pause candidate. For `video`, add D5 to §5.3.7.3's satisfiability cell and delete the clause *"D5 presents no ad surface of any kind (§3.4), so the question does not arise"* at L2610-2611, because §3.4 L485, §7.6 L3475 and Annex E §E.5.5 all render it there. | `context/03-requirements.md` R3.2 (*"undefined behaviour is non-conforming"*), R21.1 (the fullscreen release), `context/04-use-cases.md` UC-05 D2 / D4 |
| T2 | `EC-2` | 3 — internal contradiction, one reading matches `context/` | §4.5.5 L864-866 | Qualify *"presenting each exactly once"* so it binds one pass over the candidate list rather than the whole slot — e.g. *"presenting each exactly once per pass"* — and add the pointer to §4.5.11. `context/` is unambiguous on the other side: R32 defines `repeat` as presenting the sequence again. | `context/03-requirements.md` R32.1, R7.4 |
| T3 | `R13.3` | 5 — a `force-lost` row; the substance is present and only the modal is missing | §4.5.13 L1081-1083 | Rewrite as an obligation: *"Where the ad stops early the Player MUST stop firing its remaining beacons; a beacon scheduled past a trim boundary (§4.5.4) or past the dismissal of a pause ad on resume (§4.5.10) falls outside the ad's active window."* §4.5.10 L995-997 is the model — the structurally identical pause case already carries the MUST. | `context/03-requirements.md` R13.3 |
| T4 | `R29.5` | 5 — a `force-lost` row; independent of A-1 because §4.4's chapeau is framed around the returned document and cannot reach a statement about tolerating an absent input | §4.4 L719-722 | Rewrite the bullet as two obligations: *"The APS MUST tolerate the absence of every reserved parameter of §5.8 and MUST be able to produce candidates without receiving any of them."* | `context/03-requirements.md` R29.5 |
| T5 | `R24.1`, `A-1` | 4 — a cross-reference item the `review-spec-details` taxonomy covers | §5.3.7.3 L2588 and L2609; §5.2.1 L2103; §5.3.2 L2351 and L2367 | Five stale pointers. L2588 and L2609 send the reader to §8.4 for *"the conservative Player behaviour"* on decoder re-tasking; §8.4 is *Tracking-only decision entries* and the string "re-task" appears nowhere in chapter 8 — either point at the text that carries it or state the conservative default in place, since two device classes currently rest on a conditional with no stated default. L2103, L2351 and L2367 cite §4.7.2 and §4.7.3 for *"the media-type constraint"*; in v9 those are `<svta:PauseAdPresentation>` and `<svta:OverlayList>` and mention no media type. The constraint they mean is at §4.4 L683-692. | `prompts/3-post-spec/review-spec-details.prompt`, cross-ref category |

### 5.b Flagged for review (14)

| #  | Finding ref | Spec section | Why uncertain | Resolutions considered |
|----|-------------|--------------|---------------|------------------------|
| F1 | `A-1`; and the rows it causes: `R12.2`, `R20.2`, `R13.1`, `R24.1`, `R24#p1`, `R24#p2`, `R33.4`, `R30.1`, `R28.1`, `R28#p1`, `R32.1` | §4.2 L556-621, §4.3 L623-650, §4.4 L651-730 | The three non-Player conformance clauses carry zero RFC 2119 modals against 83 elsewhere. Whether the chapeaux *"A conformant Publisher:"* and *"A conformant APS returns … a document that satisfies all of the following"* confer normative force is a drafting convention the spec never states, and the answer changes the status of roughly forty statements at once. A mechanical pass that inserts MUSTs would also have to decide where SHOULD belongs (R6.2 is a SHOULD in `context/` and arrives as an exceptionless rule). | (a) state in §4.1 that a conformance clause binds in the indicative, changing nothing else; (b) rewrite §4.2-§4.4 as modal obligations, which is the larger edit and the one that makes each bullet independently citable; (c) leave it and accept that only the Player is bound, which is what a literal reader gets today. |
| F2 | `DP-1.1#p2` | §5.5.1 L2689, §5.2.2 L2214, §5.2.1 L2045 | Two attributes are declared required whose only admissible value is fixed by another rule (`EventStream@value`) or equals the attribute's own default (`MPD@type`) — the shape DP-1.1 forbids and §5.1.3 L1884-1887 argues against for `@maxConcurrency`. But both are baseline attributes whose presence the base standard's own tables expect, so dropping them may produce a document a base validator rejects. | (a) drop both from the required column and let the defaults stand; (b) keep them and record in §5.5.1 and §5.2.2 why a baseline attribute at its own default is not the construct DP-1.1 forbids; (c) keep `@type` (base-schema expectation) and drop `@value`. |
| F3 | `R15.3` | §4.5.2 L766-771 | `context/` grants a permission (*"The Player MAY skip"*) and the spec removes the discretion. Strengthening is usually safe, but it makes a Player that conforms to R15.3 non-conformant to §4.5.2, and the criterion's own rationale (*"such a candidate signals a non-conformant ADS, APS, or Publisher"*) suggests the permission was deliberate. | (a) restore the MAY in §4.5.2 for the carrier check only; (b) keep the MUST and change R15.3 in `context/`; (c) split the sentence so the layout and cap checks stay MUST and the carrier check becomes MAY. |
| F4 | `R5.4` | §4.3 L639-642 | The criterion releases **both** the ADS and the APS from holding a device-capability view; the spec states it for the ADS only. Whether the APS deserves the same release is not obvious — §5.8.2 exists precisely so an APS *may* hold one, and R29 makes that a first-class path. | (a) add the APS to §4.3's bullet with the same "holding one is equally conformant" clause; (b) add it to §4.4 instead, where APS obligations live; (c) leave it and narrow R5.4 to the ADS in `context/`. |
| F5 | `DP-1#p1`, `DP-1.2#p1` | §5.3.7.2 L2541-2544, §5.4 L2649-2663 | Two redundancies the design principles forbid, each with a stated reason for existing. The background fact is carried by both the layout token and the element's presence, with no canonical side named; the candidate's `@duration` is a markup copy of the sub-MPD's canonical `Period@duration`. Removing either costs something real — the token split is what lets a Publisher admit the box without the background, and the duplicated duration is what avoids a second fetch before a drop-before-play decision. | (a) name the canonical side in each case and state the derivation, which satisfies DP-1.2 without changing the markup; (b) collapse the two double-box tokens into one and let the element's presence decide, which breaks `@allowedLayouts` granularity; (c) record both as deliberate departures from DP-1 in §4.8. |
| F6 | `R8.1` | §4.8 | Two of the twelve constructs §4.7.13 enumerates — the two event scheme URIs and the resolution-document profile URI — have no entry in §4.8's register, and `@form` has no justification anywhere. Whether a URI counts as a "construct" for R8.1 is the open question; the spec treats it as one in §4.7 and not in §4.8. | (a) add three short §4.8 entries pointing at the rationale already written in §5.1.3 and §5.2.2; (b) state in §4.8's preamble that URIs are audited in §4.7 and justified where they are defined; (c) write the missing `@form` justification, which is needed either way. |
| F7 | `R11.3` | §3 Terms, L215 | *"It emits a decision document, typically VAST."* is the one in-place VAST mention outside an annex or a flagged note. Fixing it is one clause; whether it needs fixing depends on whether R11.3's *"non-normative note explicitly flagged as illustrative"* is satisfied by the document-wide flag at L180-181. | (a) add *"(illustrative; this specification depends on no VAST version — see §2)"* in place; (b) widen R11.3 in `context/` to admit a document-wide flag. |
| F8 | `R3.2` second half — the two missing budget rows | §5.3.7.3 L2570-2572 and the table | §5.a cap overflow, not uncertainty. The table claims *"Every layout-and-form pair has a row"* and has none for `linear` with an `image` or an `html` creative, while §3.4 L480 gives both D1..D5. Safe to apply once a slot frees: add the two rows, or narrow the claim to the layouts that admit more than one form. | (a) add the two rows from §3.4 L480; (b) rewrite the claim as "every pair the enumeration admits". |
| F9 | the `[inferred]` tags the primary copy resolves | §5.2.1 L2100, §5.2.2 L2191, §5.2.3 L2302, §5.3.4 L2437, §5.4 L2640, §5.5.1 L2689, §5.5.1 L2702, §5.9 L3070, Annex N L8172 | §5.a cap overflow, not uncertainty. Nine tags whose claim this validation checked against the primary copy of ISO/IEC 23009-1:2026 and found stated there directly, so each can be replaced by its clause citation: the List profile extends the CMAF profile (§8.14); a profile check removes extension-namespace content the profile does not include (§8.1, step 4 of the modification procedure); `Period` has no `minOccurs` and defaults to 1 (the schema in Annex B); `ImportedMpdType` admits foreign attributes and no foreign child elements (the type definition in §5.3.2.6.2); the Single-Period Static profile excludes MPD-level `Metrics` and `SupplementalProperty` (§8.15.2, the prohibited-elements list); `EventStream@value` is 1 for the callback scheme (the parameter table of §5.10.4.5.3); `Event@messageData` is `use="prohibited"` in the 6th-edition schema (§5.10.2.3); and the Advanced Linear profile names blackouts beside advertisement insertion (§8.13.1). The remaining tags at L546, L811, L1721, L1762, L1928, L2888, L4213 and L5855 were not checked in this run and stay as they are. | (a) replace each tag with the clause citation; (b) leave them and accept that a load-bearing claim reads as unverified. |
| F10 | `R6.3` | §5.5 L2667-2668 | The spec obeys the rule (*"This specification mints no tracking scheme"*) but never states the condition under which a new tracking carrier would be admissible. `gap analysis` returns zero hits in the spec against two in `context/03-requirements.md` (control verified). Whether a future-editor gate belongs in a specification or in its governance is the open question. | (a) add one sentence to §5.5 carrying R6.3's condition; (b) leave it to `.project/decisions/`. |
| F11 | `EC-1` | §4.5.2 L769-771 | The eligibility rule defines only "satisfies them" and "satisfies none" across three independent checks, leaving the mixed case unstated. The obvious fix — any failure skips the candidate — may be wrong for the cap check, where §4.5.4 offers a *drop-before-play* the Player MAY decline to take. | (a) state that a failure of any check makes the candidate ineligible; (b) separate the cap check out, since §4.5.4 already governs it with a MAY; (c) restructure §4.5.2 as three named checks with an outcome each. |
| F12 | `G-1` | §4.6 L1177-1183 | The mandated validation step names a schema the specification does not publish. Publishing one is a real commitment — versioning, hosting, keeping it aligned with §5 — and §8.12 already records that the interoperability-point question is undecided. | (a) publish the schema as an annex and reference it; (b) state in §4.6 that step 2 is performed against the attribute tables of §5 until a schema is published; (c) drop step 2, which gives back the outcome §4.6 exists to prevent. |
| F13 | `G-3` | §5.5.3 L2742-2746 | Where a non-linear slot's presentation timeline starts is never fixed, so *"the ad's start position on the primary timeline"* has no referent for the first candidate. The choice between the window's `@presentationTime` and first render is a real one: they differ by the resolution latency, which moves every beacon. | (a) anchor at first render, consistent with §5.5.3's own rule for `image` and `html`; (b) anchor at the window's `@presentationTime`; (c) leave it to the implementation and say so. |
| F14 | `G-2` | §4.5.2 L766-769, §4.5.3 L787-788 | Both obligations validate a candidate against the window's `@allowedLayouts`, which a linear window has no attribute to carry. Treating the check as vacuous on the linear family is probably right and is nowhere written; adding the attribute to the inherited events would extend a construct R1.3 protects. | (a) state in §4.5.2 that the layout check applies to the non-linear families only; (b) give the `ListMPD` Period a layout token, which adds a construct; (c) leave it. |

### 5.c Deferred to `context/` (9)

| #  | Finding ref | `context/` file to edit | Suggested edit | Leverage rationale |
|----|-------------|-------------------------|----------------|--------------------|
| D1 | `UC-05`, `UC-08`, `A-2` adjacent | `context/04-use-cases.md` | Rewrite UC-05's D5 row, and the UC-08 D5 row that derives from it, so a `pause-fullscreen` `video` candidate renders on D5 by releasing the primary content's resources. The cases predate R21.1, which grants exactly that release. UC-05 D2 and D4 stay as they are — they are what T1 aligns the spec to. | The single highest-leverage `context/` edit: it is the only place where a requirement and a use case give opposite answers about what reaches a viewer's screen, it is the root of two of the four `contradicted` rows, and every future build reproduces the conflict until it is resolved. |
| D2 | `R1.3`, `A-2` | `context/03-requirements.md` | Say in R1.3 whether a profile-style narrowing of an attribute's absent-value default counts as altering a pre-existing construct's semantics. R4.8 argues it does not; R1.3 as written says it does; the spec asserts both, at §4.5.4 L845-848 and §4.8.5 L1581-1582. | Resolves a `contradicted` row the build cannot fix, and removes the one place where two normative sections of the spec read as opposites. |
| D3 | `R31.2`, `G-5` | `context/03-requirements.md` | Give R31 a criterion fixing what `@maxDuration` bounds on a pause window, since R31.2 removes both of R4's readings and offers no third. Define the dismissal it implies, or say the attribute is absent on a pause window. | The attribute is `Required: yes` and a Player obligation is missing behind it; today the spec invents a semantics and no criterion checks it. |
| D4 | `R32.4`, `G-4` | `context/03-requirements.md` | Either move R32.4 into the Out of Scope list, where a scope declaration belongs, or give it a criterion the spec can satisfy by stating the exclusion in §1.3. | The only `gap` in 168 units, and it is a criterion asking the spec to declare a silence rather than to do anything. |
| D5 | `R1.1`, `R6.4`, `R6#p2`, `A-7` | `context/03-requirements.md` | Scope R1.1, R6.4 and R6#p2 to a Player conformant to this specification, or move them to a statement about the document's carriers. §4.1 L548-553 argues an obligation on a Player that predates the specification is not available to be made, and the base standard's §8.1 NOTE 1 supports it. | Three blocking rows with one cause, and the spec's position is the defensible one — the requirements are what ask for something unattainable. |
| D6 | `R26.2`, `R27.2`, `A-8` | `context/03-requirements.md` | Decide whether the Player is obliged to composite the squeezeback layouts. §1.3 L152-160 delegates composition to the implementation, following the base standard; R26.2 and R27.2 state three Player MUSTs against it. R27.2's *"occupying its declared region"* also names a region nothing declares, since R10.2 forbids a positioning vocabulary. | Two blocking rows, and the requirement set currently contradicts its own delegation. |
| D7 | `R25.1`, `EC-3` | `context/03-requirements.md` | Add the time-shift buffer to R25: either bound the freeze by it, which is what the base standard's clipping rule forces, or state that the freeze is promised past it and say how. Then settle whether the pause ad is dismissed at the buffer boundary. | The spec narrows a MUST with no requirement behind the narrowing, and parks the consequence as an open point in a non-normative chapter. |
| D8 | `R15.2` | `context/03-requirements.md` | Drop *"and forms declared by the Publisher"* from R15.2, or give the Publisher a form-declaring construct. Today the Publisher declares `@allowedLayouts` and nothing about carriers, so half the criterion has nothing to attach to. | A criterion that cannot be satisfied by any spec produces a permanent `partial`. |
| D9 | `R20.4`'s explanatory prose; `context/08-dash-extension-rules.md` DR-10 | `context/03-requirements.md`, `context/08-dash-extension-rules.md` | Two stale passages `context-analysis/conformance-assertions.md` §5 already identified and this walk confirms the spec resolved correctly. R20.4's rationale still says a resolution carrying no candidates ends the chain, against R20.1 and R30; DR-10 still says the non-linear resolution document *"declares no profile"*, against the profile URI v9 mints and requires. | Neither changes a verdict — the spec took the right side of both — but a reader routed to R20.4 or DR-10 lands on a flat contradiction of what the spec does. |

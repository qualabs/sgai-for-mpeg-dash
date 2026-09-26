[GROUNDED_BY=spec-only]

# Spec validation — v10 (2026-09-25)

Built against:

- spec: `../output/v10-sgai-spec.md` (8759 lines, chapters 1–8 + Annexes A–Q)
- `../context/` at git SHA: `22ae6f8` (`context/` clean in the working tree)
- `../context-analysis/`: working tree has uncommitted modifications in
  `conformance-assertions.md`, `dash-gap-analysis.md`, `error-semantics.md`,
  `iab-ad-templates.md`, `uc-coverage-matrix.md`; read as they stand on disk
- population: `bin/check-promotable.py --population` — 203 units
  (156 criteria, 31 prose obligations, 16 use cases), walked by exactly those ids
- the base standard was not consulted; claims the spec makes about it are
  taken as the spec states them

## Summary

| Verdict | Rows |
|---|---|
| `met` | 84 |
| `force-lost` | 103 |
| `contradicted` | 7 |
| `partial` | 9 |
| `gap` | 0 |
| `governance` | 0 |

**One cause dominates the map.** The spec contains no MUST, SHALL or REQUIRED
outside its RFC 2119 declaration. `grep -o '\bMUST\b' <file> | wc -l` gives
v10 = 1 (L7, the declaration itself), `output/v9.1-sgai-spec.md` = 89,
`output/v9-sgai-spec.md` = 85, `context/03-requirements.md` = 201 — the same
grep finds the keyword where it is present. L10 says the key words apply
*"when, and only when, they appear in all capitals"*, and §4.1 L603-605 says
*"The obligations are stated positively — what the actor does"*. Every
obligation of §4.2–§4.5 is an indicative item under *"A conformant X:"*, so by
the spec's own L10 rule none of them carries a requirement level. That is 101
of the 103 `force-lost` rows (the other two, R1#p2 and R1.1, are deliberate and
belong to A-1). The substance is present in every one of them; the modal is
not. It is routed as a single Actionable TODO (T1, §5.a), because DP-2 fixes
the direction — *"the normative modal stays"* — and the modal to restore is the
one `context/` states for each row.

The probable origin is outside both `context/` and the spec:
`prompts/2-build/build-spec.prompt` L199-202 (*"state the positive obligation
only — what the actor does"*) reads, literally, as an instruction to write the
indicative, while L111-112 of the same prompt requires *"MUST / SHOULD / MAY
language per RFC 2119"*. A refine can restore the modals in v10.x; a major
rebuild from the unchanged prompt is likely to drop them again. That prompt is
not an input this step routes, so it is recorded here and not in §5.

The DASH conformance audit and detail review for v10
(`v10-dash-conformance-audit.md`, `v10-detail-review.md`) did not exist when
this step ran, so §5 routes no `NC`/`M` audit item and no detail-review flag.

**UC-14 is `met`, not `gap`.** `validate-spec.prompt` §4.1 names a `gap` on
UC-14 as this step's acceptance test, on the premise that UC-14 was added after
the newest spec was generated. For v10 the premise is false: Annex N
(L7799-8067, *"A non-linear ad over a replacement that is not advertising"*)
walks UC-14 in full, with all five device classes. The acceptance test is
stale; the other fifteen use-case rows are the evidence that the use cases
were walked.

## Gaps (1)

### G-1 — Request-level extension hooks are not among the admissible extension points

- **Spec**: §4.7.5, §4.7.6 L1298-1299, §5.8.1 L2798-2807. The spec carries a
  request-type URN in the base `RequestParam@includeInRequests` (relying on
  the DASH Table I.4 drop rule) and reserved query parameters on the
  resolution request URL, which R29 itself requires.
- **Missing in `context/`**: `08-dash-extension-rules.md` (DR-1..DR-10) and
  R1.2 enumerate only MPD-level hooks (foreign namespace, event streams,
  descriptors). Neither admits nor forbids a token in a base attribute or a
  query parameter.
- **Implementer today**: follows the spec's own argument that the Table I.4
  drop rule makes the URN safe; nothing in `context/` confirms it. Routed 5.c.

## Edge cases (8)

### EC-1 — A blackout replacement with no `@maxDuration` is skipped

- **Trigger**: a base-conformant `ReplacePresentation` blackout (UC-14 shape)
  that omits `@maxDuration`.
- **Why it matters**: §4.5.1 item 7 L810 (*"A window whose `@maxDuration` is
  absent presents no ad, and the primary content continues"*), §4.8.3 L1353
  (*"a slot without one presents no ad — including an inherited linear
  event"*) and N.2 L7873 (*"Without one, the event would not be executed"*)
  make an SGAI Player play the programme that should be blacked out. §4.8.3's
  justification (*"A Publisher who omits the cap notices at once — nothing
  sells"*) does not hold for a non-ad replacement: the failure is a rights
  violation, not a missed sale. UC-14 says a Player cannot tell a slate from
  an ad, so the cap rule reaches it.
- **Actor**: Publisher (authoring), Player (execution). `context/` is silent:
  R4.10 (03:432-436) speaks only of *"ads from such a slot"*. Routed 5.c.

### EC-2 — `@executeOnce` linear or overlay window answered with unrenderable candidates

- **Trigger**: a once-only linear or overlay window whose resolution carries
  candidates, none renderable on the device.
- **Why it matters**: §4.5.6 item 4 L923-928 says this is not a failed
  execution; §4.5.6 item 6 says only an *empty* resolution consumes nothing.
  Whether the window is consumed is stated for pause (§4.5.10 item 6 L1017,
  *"consumed when a pause ad begins rendering"*) and not for linear/overlay.
  One Player never shows the break again on that device; another retries.
- **Actor**: Player. `context/` covers only the empty resolution (R30.2). The
  base counter ("playback successfully started") answers it, but the spec has
  to write the sentence. Routed 5.b.

### EC-3 — An ad that ends before its declared duration

- **Trigger**: an accepted insertion or overlay ad whose actual length is
  shorter than declared (R4.5 covers only the longer case).
- **Why it matters**: drop-before-play of the next candidate (§4.5.4 item 3
  L871) and the trim point depend on whether the cumulative sum uses declared
  or actual lengths.
- **Actor**: Player. `context/` is silent (R4.2 says *"cumulative duration of
  the accepted candidates"*). Routed 5.c.

### EC-4 — A per-ad base skip inside a linear slot

- **Trigger**: a List MPD Period carries `PlaybackRestrictions@skipAfter`.
- **Why it matters**: the spec lets the viewer skip that ad and continue with
  the next (§5.2.4 L2141-2150, §4.5.14 item 2 L1073), resolving it by saying a
  skip is not a dismissal. R35 says the unit of dismissal is the slot, *"never
  an individual ad inside it"*, and R35.4 forbids advancing after a dismissal.
  `context/` does not make the skip/dismissal distinction.
- **Actor**: Player. `context/` silent on per-ad base skip controls. Routed 5.c.

### EC-5 — A held resolution expires while its ad is on screen

- **Trigger**: an early resolution reaches `@usableFor` while an overlay or
  pause ad from it is rendering (a long pause with `request-again`, or a
  candidate list still being walked).
- **Why it matters**: R36.5 checks usability only *"when the opportunity
  fires"*; whether remaining candidates or a `request-again` may come from the
  stale document is undecided. The spec (§4.5.1 item 5, §4.5.11) is silent.
- **Actor**: Player. `context/` silent. Routed 5.c.

### EC-6 — Playback speed changes, or reaches zero or below, during an ad

- **Trigger**: a speed change, scrub or rewind while an overlay or linear ad
  is presented.
- **Why it matters**: R19.1 fixes the speed *"at the moment the ad is
  presented"*, and R19.3 divides by `playback_speed`, undefined at 0 and
  meaningless below it. The spec (§4.5.12 L1032-1047) inherits the silence.
- **Actor**: Player. `context/` covers only a constant non-1× speed
  (04-use-cases.md L267). Routed 5.c.

### EC-7 — Options of one candidate with different durations share one tracking schedule

- **Trigger**: a candidate with, say, a 15 s video option and a 10 s image
  option, and a schedule authored for one of them.
- **Why it matters**: tracking is per candidate (§5.5.2; §8.13 L3767
  *"options of one candidate with different durations share one
  schedule"*), so `complete` never fires on the shorter option and quartiles
  fire at the wrong fraction. The ADS cannot know which option the Player
  picks.
- **Actor**: ADS (schedule), APS (placement). `context/` silent:
  `grep -n -i 'per-option\|different durations' context/*.md` returns nothing.
  Routed 5.c.

### EC-8 — An overlay window reached closed at a live resume

- **Trigger**: an active overlay window, a pause inside a pause window, the
  viewer paused past the overlay window's end in wall-clock time, live
  content.
- **Why it matters**: R17.3 is written as expiry *"during the pause"*, which
  cannot happen on a frozen presentation timeline (R25); the window can only
  be found closed at the resume position (time-shift edge or live edge). The
  spec already reads it that way (§4.5.9 item 2 L973-976; test L-21 L8644).
- **Actor**: Player. `context/` silent on the live-resume variant. Routed 5.c
  (restate R17.3 in terms of the resume position).

## Ambiguities (31)

A-1 to A-24 are passages of `context/` that admit two readings. A-25 to A-30
are places where the spec itself reads two ways against `context/`. A-31 lists
the criteria whose force cannot be checked because `context/` gives them no
modal (§4.2 of the prompt).

### A-1 — R1 / R1.1 bind a Player that does not implement the specification

- **Passage**: 03-requirements.md L119-122 (R1 body), L130-133 (R1.1): MUST on
  *"a Player that does not implement the new mechanisms"*.
- **Readings**: (1) a runtime obligation on the legacy Player; (2) a document
  guarantee that follows from where constructs are placed (ADR 0009, DR-8).
- **Spec assumed** (2): §1.4 L187-195, §4.1 L621-624 (*"No obligation here
  binds a Player that does not implement this specification"*). Hence R1#p2
  and R1.1 `force-lost` on purpose.
- **Tighter**: *"Every construct MUST sit at an extension point whose base
  semantics let a Player that does not implement this specification ignore it
  and continue the primary content."* (R1.1 becomes a document criterion.)

### A-2 — R2.2 against R38.4

- **Passage**: R2.2 L182-189 (*"this specification places no such obligation
  on the ADS or the APS"*) vs R38.4 L1197 (*"The APS MUST NOT return an option
  whose layout is outside the set it received"*).
- **Readings**: the APS enforces no Publisher constraint / none except the
  forwarded layouts.
- **Spec assumed** the second (§4.4 L773-775).
- **Tighter R2.2**: *"… places no such obligation on the ADS, and on the APS
  none beyond R38.4 and R39."*

### A-3 — DP-1.2 against the pre-fetch duration of a video option

- **Passage**: DP-1.2 L35-42 (derived values *"not duplicated in the
  markup"*) vs R4.9 L424-431 and R10 (drop-before-play needs a duration before
  the sub-MPD is fetched).
- **Readings**: the option's `@duration` is a forbidden duplicate of
  `Period@duration` / an admitted exception.
- **Spec assumed** the exception, declaring the sub-MPD canonical (§5.4
  L2559-2568). Hence DP-1.2#p1 `contradicted`.
- **Tighter**: DP-1.2 names the pre-fetch copy for drop-before-play as an
  admitted exception, with the sub-MPD canonical — or forbids it and says how
  drop-before-play works without it.

### A-4 — R1.3 (never alter base semantics) against R4.10 / R1.5

- **Passage**: R1.3 L148-150 (absolute MUST NOT alter), R1.5 L162-164
  (recorded departures allowed), R4.10 L432-437.
- **Readings**: an inherited linear event with no `@maxDuration` plays
  uncapped on a base Player and presents no ad on an SGAI Player — an
  alteration / a permitted narrowing.
- **Spec assumed** narrowing (§4.8.3 L1353), conceding the difference (§1.4
  L181-184). EC-1 is the case where it bites.
- **Tighter R1.3**: *"… MUST NOT alter the semantics of any pre-existing
  construct; restricting which documents conform (R4.8) is not an
  alteration."*

### A-5 — R11: "implementations MUST be VAST-version-agnostic"

- **Passage**: R11 body L203-204.
- **Readings**: an APS must accept any VAST version / nothing in the
  specification may depend on a VAST version. For the Player it is
  structural; for the APS, whose conversion is bilateral (R18), reading 1 is
  undefined.
- **Spec assumed** the second (§2 L233-234). Hence R11#p2 `partial`.
- **Tighter**: *"No obligation of this specification depends on the ADS's
  decision format or its version."*

### A-6 — R31.1 (request at the pause) against R36.5 (reuse an early resolution)

- **Passage**: R31.1 L472-475 vs R36.5 L1124-1126.
- **Readings**: request at every qualifying pause / hold a usable resolution,
  requesting only if none is held.
- **Spec assumed** the second (§4.5.1 item 3 L793; §6.3 L3283; §8.9).
- **Tighter**: *"When a viewer pause begins inside a pause opportunity window,
  the Player MUST hold a resolution usable under R36.5, requesting one at that
  moment if it holds none."*

### A-7 — R4.9: rounding per ad or on the sum

- **Passage**: R4.9 L427-431.
- **Readings**: round each converted duration up, then sum / sum, then round.
  Two ads converting to 14999.4 units each give 30000 or 29999.
- **Spec assumed** per ad (§4.5.4 item 4 L877).
- **Tighter**: *"… MUST round each candidate's converted duration up, before
  the cumulative sum of R4.2 is taken."*

### A-8 — R15.2: "forms declared by the Publisher"

- **Passage**: R15.2 L619-622.
- **Readings**: Publisher-authored alternative content (a slate) must use an
  admissible carrier / a dead clause — no requirement gives the Publisher a
  form to declare.
- **Spec assumed** neither and states no Publisher obligation. Hence R15.2
  `partial`.
- **Tighter**: name the Publisher construct, or drop *"and forms declared by
  the Publisher"*.

### A-9 — R12.4 against R39

- **Passage**: R12.4 L597-599 (*"no dimensional attribute is introduced on
  the slot declaration"*), no exception for R39's custom region.
- **Spec assumed** R39 wins (§3.4.2 L514).
- **Tighter**: *"… for an enumerated IAB layout; the custom region of R39 is
  the one exception."*

### A-10 — R7.2 (MAY drop) against R5.3 (MUST skip)

- **Passage**: R7.2 L750-751 vs R5.3 L692-694, the same unrenderable
  candidate.
- **Readings**: dropping is optional / mandatory, R7.2 merely excepting it
  from the order.
- **Spec assumed** mandatory (§4.5.3 L844, §4.5.5 L890).
- **Tighter R7.2**: *"A candidate skipped under R5.3 is not a violation of the
  order R7.1 requires."*

### A-11 — R34.2: "at most one pause ad for that window"

- **Passage**: R34.2 L968-971.
- **Readings**: one ad (the first candidate only) / one pause's worth of pause
  ads, with later pauses getting none (what the gist "a viewer who pauses
  again inside it is not shown another" suggests).
- **Spec reads it both ways**: §4.5.10 item 6 L1014-1015 (*"presents at most
  one pause ad for that window for the whole session"*) states the first;
  Annex E sets `executeOnce="true"` (E.1 L5100-5101) and presents p1 then p2
  in one pause (E.6) and more under `repeat` (E.7). The normative site matches
  the letter of `context/`, the annex its gist, so this is not a 5.a
  alignment.
- **Tighter**: *"On a window declared once-per-session, the Player MUST
  present pause ads in at most one pause for that window for the duration of
  the session; within that pause the slot plays out as declared (R32)."*

### A-12 — R35.8: which linear skip declaration counts

- **Passage**: R35.8 L1044-1050: *"R35.1's default applies only where neither
  the event nor the resolution document declares anything"* and *"a Player of
  this specification and a base Player treat the same linear event the same
  way"*.
- **Readings**: (1) only a written `@skipAfter` counts, an omitted one falls to
  R35.1 (non-dismissible) — also what `06-naming-and-namespaces.md` suggests
  (*"a `@skipAfter` a Publisher writes"*); (2) the schema default `PT0S` is a
  declaration, so every linear slot is dismissible and R35.1 never applies on
  linear.
- **Spec assumed** (2): §5.2.4 L2129-2139 (*"the non-dismissible default of
  the non-linear families never governs a linear slot"*). Under reading (1)
  that sentence is what R35.8 forbids, hence R35.8 `contradicted`, routed to
  `context/` because the criterion's own last sentence supports (2). A second
  question hides in *"the resolution document declares"*: the spec treats
  `PlaybackRestrictions@skipAfter` as per-ad, not slot-level (EC-4).
- **Tighter**: *"On a linear slot the Player MUST honour the event's
  `@skipAfter` with its base meaning, including its schema default `PT0S`;
  R35.1's default never applies to a linear slot."* — or the opposite, if (1)
  is intended.

### A-13 — D5 and the pause ad (UC-05, UC-08) against R37

- **Passage**: 04-use-cases.md L657-662 (UC-05 D5 *"declines the pause-ad
  opportunity entirely"*), L977-988 (UC-08 D5), L681 (re-tasking named for D3,
  D4 only); R37 covers any single-decoder device.
- **Spec assumed** D5 MAY present a fullscreen video pause ad by re-tasking,
  declining remaining conformant (§3.6 L578, §5.3.7, §7.6, E.6, H.9).
- **Tighter**: *"D3, D4 and D5 may re-task the decoder to present a fullscreen
  video form; declining remains conformant."* — or exclude D5 explicitly.

### A-14 — R36.4: must the APS always declare the usable lifetime

- **Passage**: R36.4 L1119-1122: *"the APS MUST declare how long that
  resolution remains usable. A resolution document that does not declare it
  remains usable for as long as its opportunity window lasts."*
- **Readings**: mandatory on every non-linear document, absence tolerated but
  non-conformant / absence is itself the declaration "the window's length".
- **Spec assumed** the second (§4.4 item 11 L760-761).
- **Tighter**: *"… a document that declares nothing remains usable for as long
  as its window lasts, and an APS whose decision stays good for less MUST
  declare it."*

### A-15 — R36.6: "no usable candidate"

- **Passage**: R36.6 L1127-1129.
- **Readings**: the document carries no candidate / it carries candidates none
  of which this device can render.
- **Spec reads it both ways**: §4.5.1 item 5 L803 (*"a new one that yields no
  usable candidate is an empty resolution"*, so a failed execution that moves
  to the next window) vs §4.5.6 item 4 L923-928 (*"A resolution document
  carrying candidates of the right family is not a failed execution … ends …
  at the primary content"*). Neither site matches `context/` uniquely because
  `context/` allows both. If `context/` settles on the first reading, the fix
  becomes 5.a: L803 reads *"carries no candidate"*.
- **Tighter**: *"When a re-resolution carries no candidate, the Player MUST
  treat it as an empty resolution (R30); one whose candidates are all
  unrenderable is handled as any other resolution (R5.6)."*

### A-16 — R14.2 (cap over non-linear candidates) against R31.2 (no cap on pause)

- **Passage**: R14.2 L1493-1497 vs R31.2 L476-479.
- **Spec assumed** R31.2 (§4.5.4 L864, *"Pause / **Nothing**"*).
- **Tighter R14.2**: *"… against the cumulative duration of the sequence of
  **overlay** candidates; on a pause slot the cap bounds no duration (R31.2)."*

### A-17 — R26.1: slot or layout, and the Publisher's role

- **Passage**: R26 L1359 (*"an attribute of the slot / layout composition"*),
  R26.1 L1369-1371 (actor *"APS + Publisher"*).
- **Readings**: a slot-level attribute the Publisher could declare / a
  layout-level attribute of the option, emitted by the APS.
- **Spec assumed** the second: `@backgroundUrl` on `<svta:RenderableAsset>`
  (§5.3.1 L2248, §4.4 item 8 L750), with no Publisher role. It is not a
  separate option, so R26.1 is not `contradicted`.
- **Tighter**: *"The background element MUST be carried on the presentation
  option whose layout is the double-box-with-background, as an attribute of
  that layout and not as an option of its own; the APS emits it."*

### A-18 — Universal ad identifier: no carrier, or an optional one

- **Passage**: 05-dash-linear-interfaces.md L444: *"this spec deliberately
  does not add one"* and *"An APS that still wants to propagate it MAY do so
  on a best-effort SVTA-namespaced attribute (R23)"*.
- **Spec assumed** an optional carrier, as an element `<svta:UniversalAdId>`
  (§5.7), while L2762 says *"No carrier is mandated for the universal ad
  identifier."*
- **Tighter**: *"The specification MAY define an optional SVTA-namespaced
  element for the universal ad identifier; it mandates none."* — or *"defines
  no element for it"*.

### A-19 — UC-07: does a current Player play the standard break

- **Passage**: 04-use-cases.md L815-822 (*"the legacy fallback only"*,
  *"simply ignored by current Players"*).
- **Readings**: a current Player ignores the base break / executes it because
  it is a base event (R1.5).
- **Spec assumed** the second: §7.9 L3486-3488 (*"A Player of this
  specification executes that break as well … and additionally takes the SGAI
  path"*), G.9. Hence UC-07 `contradicted`.
- **Tighter**: state that a current Player executes the standard break and the
  viewer sees both, or add a requirement defining how a current Player
  recognises and skips the fallback.

### A-20 — UC-08: "unless the Publisher's MPD signals that the overlay candidate doubles as the pause-ad candidate"

- **Passage**: 04-use-cases.md L884-886.
- **Readings**: a reuse signal exists and suppresses the pause request / no
  such signal; R31.1 applies.
- **Spec assumed** the second; no requirement defines the signal. Hence UC-08
  `partial`. Already raised in `context-analysis/context-audit-ciego.md`
  L880-900.
- **Tighter**: delete the clause.

### A-21 — Side-by-side on D2 (UC-03, UC-10)

- **Passage**: UC-03 L318-327 and L367-372; UC-10 L1175, L1188, table row L88
  (names `squeezeback-double-box` for a layout with a background, and gives
  D2 *"side-by-side declined"*); R12 token table 03:534-535 reserves
  `squeezeback-double-box-background` for the backgrounded variant.
- **Readings**: side-by-side is always three elements, D2 never renders it /
  a no-background double box exists and D2 renders it with black bands.
- **Spec assumed** the second, admitting both tokens (§5.3.7 L2491, L2494;
  J.7 L6888).
- **Tighter**: *"The allowed-layout set includes
  `squeezeback-double-box-background` and `squeezeback-double-box`; on D2 the
  backgrounded variant is declined, and a video ad in `squeezeback-double-box`
  (black bands) is satisfiable."*

### A-22 — UC-04: an L-shape over a linear takeover

- **Passage**: 04-use-cases.md L441-445 (intent: overlay lower-third only, no
  squeezeback over a linear ad) vs L495-546 (D3/D4 describe an L-shape that
  shrinks "the primary content").
- **Readings**: squeezeback is excluded during the takeover / admitted, in
  which case what is shrunk is the linear ad, and nothing says so.
- **Spec assumed** the intent (D.1: *"admits no squeezeback over a
  takeover"*).
- **Tighter**: drop the L-shape branch from D3/D4, or admit it and state what
  element is shrunk.

### A-23 — UC-12: "whatever its shape" against R20.1

- **Passage**: 04-use-cases.md L1341 (an attempt that produces no ad is a
  failed execution *"whatever its shape"*) vs R20.1 L1637-1643.
- **Spec assumed** R20.1: L.7 L7458 (*"It does not attempt 702"*).
- **Tighter UC-12**: *"An attempt that obtains no usable resolution document —
  including a well-formed one with no candidates — is a failed execution; a
  document whose candidates the device cannot render is not (R20.1)."*

### A-24 — UC-16: overlay form unstated

- **Passage**: 04-use-cases.md L1683-1687 and table row L94 (D2 *"same"* as
  D1).
- **Readings**: a video overlay (D2 renders it) / an image or HTML overlay (D2
  skips it).
- **Spec assumed** image creatives (P.4), so D2 renders nothing (P.6 L8504).
  Hence UC-16 `partial`.
- **Tighter**: state the form, and make the D2 cell agree with it.

### A-25 — The normative-language declaration against how chapter 4 states obligations (spec-internal)

- **Sites**: L7-10 (*"when, and only when, they appear in all capitals"*) vs
  §4.1 L603-605 (*"The obligations are stated positively — what the actor
  does"*) and every item of §4.2–§4.5.
- **Readings**: an indicative item under *"A conformant X:"* binds / binds
  nothing. Under the spec's own L10 it binds nothing, which is how this map
  reads it (prompt §4.2).
- **`context/` side**: DP-2 L44-56, *"the normative modal stays"*, with the
  worked example *"the Player MUST fire tracking beacons within the slot
  window"*. v9.1 carried MUST in §4.5.13, §4.5.15 and §4.5.16, so R13.2,
  R13.3, R28.2, R33.2, R6.5 and R6.6 are regressions from `met`.
- See Actionable TODO T1.

### A-26 — The APS checked against the resolution document, and against the decision (spec-internal)

- **Sites**: §4.1 L610-614 (*"An APS obligation is checked against the
  resolution document alone … how faithfully the APS transcribed it, belongs
  to the APS-to-ADS contract"*) and the Q.2.3 heading L8602, against §4.4
  item 5 L736-737 (*"The options it emits keep the order the decision gave
  them."*), test S-4 L8609 (*"Reorder them: reported against the known
  decision"*) and C.4 L4532 (*"the options inside each candidate follow the
  order the decision gave them (§4.4, item 5)"*).
- **`context/` side**: R5.1 (*"Conformance is checked against the APS's
  resolution document"*), R13.5, R28.3 — the §4.1 reading. Hence R5.1
  `contradicted`.
- See Actionable TODO T2.

### A-27 — `@layout` is required on a List MPD Period where its only value is fixed (spec-internal, DP-1)

- **Sites**: §5.3.1 L2245 (`@layout` *"yes"*), schema L3121 (`use="required"`),
  §5.3.3 L2325 (*"A List MPD Period (linear) / `linear`"*), §5.2.1 L1848
  (*"each with `@layout="linear"`"*), and the List MPD example at A.3 L3868
  (`<svta:RenderableAsset form="image" layout="linear"`). The other
  `layout="linear"` occurrences (L6517, L7338, L7625, L7670, L8275) sit on
  overlay candidates, where `linear` is one choice among several and stays.
- **`context/` side**: DP-1 (no redundant information) and DP-1.1 (no value
  another rule already fixes). The same table already applies the right
  pattern to `@duration` (*"absent on a List MPD Period, whose `@duration`
  applies"*). Hence DP-1#p1 and DP-1.1#p2 `contradicted`.
- See Actionable TODO T3.

### A-28 — §6.6: illustrative or normative (spec-internal, R11.3)

- **Sites**: §2 L235-236 (*"the field mappings are illustrative (§6.6, Annex
  A, Annex C)"*) vs §6 L3160-3161 (*"The flows are normative in what they
  exchange"*), with no illustrative flag on §6.6.
- **Why not 5.a**: the §6.6 table is also the R11.4 coverage statement, so
  flagging it illustrative or rewording §2 are both defensible. Routed 5.b.

### A-29 — "Uninterrupted" defined by a list of prohibitions (DP-2)

- **Site**: §4.5.16 L1117-1119 (*"no visible artefact: no freeze, no blank
  slate, no error surface unless the application opted into one, and no beacon
  fired"*).
- **Why not 5.a**: the positive restatement is a wording choice with more than
  one form. Routed 5.b.

### A-30 — Test S-10 checks that a ClickThrough arrived (R28.3)

- **Site**: S-10 L8615 (input *"An ad with tracking and a ClickThrough"*, pass
  *"`<svta:Click>` carries the ClickThrough"*) and §4.4 item 9 *"when the ad
  has one"*.
- **Why it matters**: R28.3 puts whether the APS carried a ClickThrough the
  ADS decided outside this specification; S-10 reads as checking it. Weaker
  instance of A-26: the test can be recast as a check on the document's shape
  or dropped. Routed 5.b.

### A-31 — Criteria with no RFC 2119 keyword

21 criteria carry none of MUST / SHALL / REQUIRED / SHOULD / MAY / RECOMMENDED
/ OPTIONAL (counted over each criterion bullet of 03-requirements.md). Their
force cannot be checked against the output; the map records Q2 as
`source-has-no-modal`.

| Reads as | Criteria |
|---|---|
| Obligation written in the indicative | R1.5, R18.1, R29.8, R4.7, R12.4, R34.4, R37.3, R38.3, R17.4 |
| Definition | R29.1, R29.7 |
| Scope declaration or record | R18.2, R4.8, R32.4, R35.7, R36.7, R38.6, R13.5, R33.3, R28.3, R10.3 |

The first row is the defect: an obligation `context/` states without a modal
cannot arrive `force-lost`, so the map cannot tell whether it arrived with its
force. Routed 5.c.

## Obligation coverage map

One row per unit of `bin/check-promotable.py --population`, in its order.
`Kind` says which of the two questions apply (prompt §4.2); the Q2 answer is
in `Notes`. Line numbers are of `../output/v10-sgai-spec.md`.

| Unit | Kind | Verdict | Disposition | Evidence — quoted passage and location | Notes |
|------|------|---------|-------------|----------------------------------------|-------|
| DP-1#p1 | document | contradicted | 5.a | §5.2.1, L1848: *"Further presentation options for the same ad, each with `@layout="linear"`"*; §5.3.3, L2325: *"A List MPD Period (linear) / `linear`"*; §5.3.1 makes `@layout` required | Q2: n/a (document). On a List MPD Period `@layout` is required yet fully determined by the parent construct. Fix: `@layout` absent on a List MPD Period (same pattern §5.3.1 already uses for `@duration`). |
| DP-1.1#p1 | document | met | — | §5.8.4, L2924: *"Every parameter name beginning with `sgai` is reserved to this and later editions"* (the only forward-looking construct, and it is R29.4-mandated); no construct found justified by a future edition (grep 'later edition/future' L156, L247, L1372, L2925) | Q2: n/a (document). |
| DP-1.1#p2 | document | contradicted | 5.a | §5.3.3, L2325: *"A List MPD Period (linear) / `linear`"* with §5.3.1 L2245 `@layout` / *"yes"* | Q2: n/a (document). Same instance as DP-1#p1: its only admissible value there is fixed by another rule. One edit fixes both. |
| DP-1.2#p1 | document | contradicted | 5.c | §5.4, L2559-2563: *"One ad is described by a duration twice ... The sub-MPD's value is canonical ... The parent's value is derived from it by the APS when it produces the resolution document"*; §5.3.1 L2246 | Q2: n/a (document). DP-1.2 says the others are derived at runtime, *"not duplicated in the markup"*; the spec duplicates it in markup (option `@duration` of a video form). Context needs it for drop-before-play (R4.9 / R10), so context must say whether this is an admitted exception (A-3). |
| DP-2#p1 | document | contradicted | 5.a | L7 boilerplate is the only MUST in the document; §4.1, L604-605: *"The obligations are stated positively — what the actor does"* | Q2: n/a (document). DP-2 states *"the normative modal stays"*; the spec kept the positive side and dropped the modal everywhere. One systemic TODO: restore RFC 2119 MUST in §4.2-§4.5 (and §5 obligation prose). See A-25, T1.|
| DP-2#p2 | document | partial | 5.b | No MUST NOT anywhere in the spec (grep = 0 outside L7). But §4.5.16, L1117-1119: *"Continuing "uninterrupted" means no visible artefact: no freeze, no blank slate, no error surface unless the application opted into one, and no beacon fired"* | Q2: n/a (document). One enumerated prohibition list defining a term negatively; the positive restatement is a wording choice. |
| DP-2#p3 | document | met | — | §4.5.13, L1055-1056: *"When the cap trims an ad, the Player stops firing that ad's remaining beacons at the trim boundary."* | Q2: n/a (document). The example prohibition is expressed positively, as DP-2 asks. |
| DP-2#p4 | document | partial | 5.a | §4.5.13, L1051-1053: *"the Player executes the tracking schedule the resolution document carries, firing each beacon at its time relative to the ad's presentation"* | Q2: n/a (document). Positive form present; the modal DP-2's own example carries (*"MUST fire"*) is not. Same systemic TODO as DP-2#p1. |
| DP-3#p1 | document | met | — | §1.1, L90-94: *"The invariant. Applying this specification never breaks the playback of the primary content. When an opportunity cannot be honoured ... the Player skips it and the primary content continues."*; §4.5.16 L1113-1115 | Q2: n/a (document). No construct found that breaks primary playback; the runtime side is R1.4. |
| R1#p1 | document | met | — | §1.1, L60: *"as a complete extension of the base specification named in chapter 2"*; §1.4 L178-179 | Q2: n/a (document). |
| R1#p2 | runtime | force-lost | 5.c | §1.4, L187-189: *"Every construct this specification adds is ignored by a Player that does not implement it, and the primary content keeps playing."* | Q2: force lost. Deliberate: §1.4 L189-195 and ADR 0009 / DR-8 say no construct can oblige a legacy Player. Context still binds it with MUST. |
| R1#p3 | document | met | — | §4.7, L1184-1185: *"No construct of this specification uses (c1) or (c2), and none invokes a new delivery format"*; §4.7.6 audit table | Q2: n/a (document). Every MPD construct sits at (a) or (b). The request-level exception is under R1.2. |
| R1.1 | runtime | force-lost | 5.c | §4.1, L621-624: *"No obligation here binds a Player that does not implement this specification (§1.4). What this specification guarantees for such a Player is structural"* | Q2: force lost, on purpose. Same cause as R1#p2 (ADR 0009). |
| R1.2 | document | partial | 5.c | §4.7.6, L1298-1299: *"Reserved query parameters / resolution request URL / RFC 3986 query"* and *"`urn:svta:dash:sgai-resolution:2026` / `RequestParam@includeInRequests` / DASH Table I.4"* | Q2: n/a (document). All MPD element and attribute constructs use (a)/(b). The request-type URN (a token in a base attribute, relying on the Table I.4 drop rule) and the query parameters use hooks outside the enumeration in 08 (G-1). |
| R1.3 | document | met | — | §4.8.3, L1353: *"The narrowing restricts which documents conform and changes no construct's meaning, which is what a profile does (DASH §8.1)"*; §4.8.10 keeps base `@skipAfter` meaning | Q2: n/a (document). The framing matches context R4.8. The observable Player difference on an uncapped linear event is noted in A-4. |
| R1.4 | runtime | force-lost | 5.a | §4.5.16, L1104-1107: *"When resolving or rendering an accepted ad fails at runtime ... the Player aborts that ad and continues the primary content uninterrupted."* | Q2: force lost (indicative restates a MUST). |
| R1.5 | document | met | — | §1.4, L178-183: *"Where the base specification answers a question, its answer is the one this specification adopts ... Where it departs from a base answer anyway, the departure is recorded as an exception with its reason (§4.8.3)"* | Q2: source-has-no-modal. |
| R2.1 | runtime | force-lost | 5.a | §4.2, L652-655: *"Declares every constraint on a slot in the main MPD ... and leaves none of them to be inferred at runtime by the ADS, the APS or the Player."* | Q2: force lost. |
| R2.2 | runtime | force-lost | 5.a | §4.3, L699: *"Decides which ads to serve for an opportunity, how many and in what order"*; §4.4, L727: *"Converts the ADS's decision, in whatever format the two agreed, into that document."* | Q2: force lost. The "no enforcement obligation" part is present (L711, L773). It clashes in context with R38.4, |
| R2.3 | runtime | force-lost | 5.a | §4.5.2, L817-819: *"The Player validates every candidate against the declarations of the window that served it before rendering anything, and renders only candidates that satisfy them."* | Q2: force lost. |
| R2.4 | document | met | — | §4.1, L645-646: *"every construct is expressible within the four-actor division of §1.2"*; §1.2 table L105-112 | Q2: n/a (document). No construct found that moves a role across actors. The APS layout filter (§4.4 item 6) is context-mandated by R38.4. |
| R11#p1 | document | met | — | §2, L231-234: *"IAB Tech Lab VAST ... version 4.x, is cited as the typical decision format of an ADS. No actor is required to use VAST or any particular version of it"* | Q2: n/a (document). VAST is only an informative reference. |
| R11#p2 | runtime | partial | 5.c | §2, L233-234: *"No actor is required to use VAST or any particular version of it"*; §1.2, L116: *"The Player never talks to the ADS"* | Q2: force lost. The spec carries a non-requirement and not the obligation that implementations be version-agnostic. For an APS the obligation is undefined given the bilateral conversion (R18) (A-5). |
| R11#p3 | document | met | — | §2, L233-234 (as above); §4.3, L704-705: *"typically VAST, though it is not bound to VAST and MAY emit another format"* | Q2: n/a (document). |
| R11.1 | document | met | — | §2, L233-236: *"every mention of VAST in the normative chapters names it as the typical case"*. The only version citations are L231 (informative reference) and L4048 (Annex A.7). | Q2: n/a (document). Checked with grep 'VAST' over L1-3775. |
| R11.2 | runtime | force-lost | 5.a | §1.2, L116-117: *"The Player never talks to the ADS: the resolution document is the only thing it reads about an ad."* | Q2: force lost. A structural fact, with no Player obligation stated. |
| R11.3 | document | partial | 5.b | §6.6, L3330-3331: *"What the resolution document can express is what makes the conversion possible for the ad behaviours a VAST-based decision carries today:"* followed by a mapping table in normative chapter 6 (L3160-3161: *"The flows are normative in what they exchange"*) | Q2: n/a (document). Typical-case sentences are fine (L110, L704, L3325). The §6.6 table is behaviour-level, but §2 L235-236 itself calls it a field mapping (*"the field mappings are illustrative (§6.6, Annex A, Annex C)"*), and §6.6 does not flag it as illustrative. |
| R11.4 | document | met | — | §6.6, L3333-3335: *"Behaviour in the decision / Where it lands in the resolution document"* ... *"The ads of a break, in order / List MPD Periods (§5.2.1) or candidates (§5.2.2), in document order"* (table continues to L3344: creatives, tracking, ClickThrough, metadata, skip/dismiss, no ads) | Q2: n/a (document). The uncarried ones (`<Error>`, `<AdServingId>`) are recorded at L4135 and in context 05 L445. |
| R11.5 | document | met | — | Annex A.7, L4043-4044: *"This subsection is illustrative. It constrains no implementation and defines no semantics."*; Annex C.8 L4681 (non-linear VAST example) | Q2: force carried (SHOULD satisfied). |
| R18.1 | document | met | — | §5.8, L2769: *"The Player resolves a window by an HTTP GET against its `@uri`."*; §6.4 table L3293-3304; §5.2 resolution documents | Q2: source-has-no-modal. |
| R18.2 | scope | met | — | §1.3, L135-140: *"the APS-to-ADS exchange ... Those parties agree it bilaterally."*; §6.4, L3306-3307: *"The parameters the Publisher arranges with its APS, beyond the ones this specification reserves, remain bilateral."* | Q2: source-has-no-modal. |
| R29.1 | document | met | — | §5.8.2, L2836-2838: *"The parameters are inputs about the device — statements of what it supports — and not conclusions about which ad experiences can be served"*; the set is three parameters (L2832-2834) | Q2: source-has-no-modal. |
| R29.2 | runtime | met | — | §5.8.4, L2908-2909: *"Sending a capability parameter is OPTIONAL. A Player MAY send all three, some, or none."* | Q2: force carried (OPTIONAL / MAY). |
| R29.3 | runtime | force-lost | 5.a | §5.8.4, L2910-2911: *"A parameter the Player has no value for, or does not disclose, is omitted entirely — never sent empty or with a placeholder."* | Q2: force lost. |
| R29.4 | runtime | force-lost | 5.a | §5.8.4, L2925-2927: *"A parameter a Player attaches that is not a reserved name carries a vendor prefix of the form `x-<vendor>-`"* | Q2: force lost. |
| R29.5 | runtime | force-lost | 5.a | §4.4, L765-767: *"Answers without any capability parameter. The APS produces candidates whether or not the request carries any reserved capability parameter"* | Q2: force lost. |
| R29.6 | document | met | — | §5.8.2, L2840-2848: *"The three axes are what separates the device classes of §3.6"*, with five distinct declarations D1-D5, consistent with §3.6 L557-563 | Q2: n/a (document). |
| R29.7 | document | met | — | §5.8.4, L2912-2918: *"A reserved parameter that is absent means its value is undetermined ... Absence does not assert that the device lacks the capability. How an APS resolves an undetermined value is its own decision"* | Q2: source-has-no-modal. |
| R29.8 | document | met | — | §5.8.3, L2892-2894: *"These two are the exceptions to optional sending. Every other reserved parameter is the Player's to send or not"* | Q2: source-has-no-modal. |
| R4#p1 | runtime | force-lost | 5.a | §4.5.4, L862: "The Player stops rendering once that duration would exceed the cap, even mid-ad." | Q2: force lost. Source "The Player MUST enforce it, stopping at the bound even when the stop falls mid-ad" (L331) arrives in the indicative; the spec has no MUST anywhere Fix: restate as "The Player MUST ..." |
| R4.1 | runtime | force-lost | 5.a | §4.2 item 2, L656: "Declares `@maxDuration` on every ad slot of every family" | Q2: force lost. Substance complete (tables L1554/L1632/L1709 "yes"; XSD use="required" L3066/L3077), but §4.2 is a list of indicatives under "A conformant Publisher:". Fix: "MUST declare". |
| R4.2 | runtime | force-lost | 5.a | §4.5.4 table, L862: "Linear, insertion / How long: the cumulative duration of what the slot presents / The Player stops rendering once that duration would exceed the cap, even mid-ad." | Q2: force lost. Overlay row (L863) "As for insertion" covers non-linear. Indicative. |
| R4.3 | runtime | force-lost | 5.a | §4.5.4 item 1, L866: "The Player extends no slot beyond what the cap bounds for its family, whatever the ADS metadata or the number of candidates say." | Q2: force lost. @clip="false" carve-out carried at L861 and §5.1.2. MUST NOT arrives as indicative. |
| R4.4 | runtime | force-lost | 5.a | §4.3, L711: "The ADS is not required to respect the slot cap when selecting candidates, and a conformance check on an ADS passes whatever the cumulative duration of the candidates it returned" | Q2: force lost. "MUST NOT fail solely because..." restated as "passes"; substance present. |
| R4.5 | runtime | force-lost | 5.a | §4.5.4 item 2, L868: "The cap is enforced against actual rendered length, not declared length" | Q2: force lost. Passive indicative, no actor bound. |
| R4.6 | runtime | force-lost | 5.a | §4.5.4 table, L861: "The presentation ends no later than the end the base `@clip` semantics fix: with `@clip="true"` (the default) the scheduled end, so a late start shortens it" | Q2: force lost. Also §5.1.2 prose; no MUST honour. |
| R4.7 | runtime | met | — | §4.5.1 item 7, L812: "A window whose `@maxDuration` is zero does not fire." | Q2: source-has-no-modal. Also §4.2 item 2 L659 and tables L1554/L1632/L1709; base sentence quoted L1568. |
| R4.8 | scope | met | — | §4.8.3, L1353: "Every slot declares a cap; a slot without one presents no ad — including an inherited linear event" / "The narrowing restricts which documents conform and changes no construct's meaning, which is what a profile does (DASH §8.1)." | Q2: source-has-no-modal. Narrowing recorded, base infinity default quoted at L1561-L1566. |
| R4.9 | runtime | force-lost | 5.a | §4.5.4 item 4, L876: "The Player converts the duration into the cap's timescale and rounds up to the next whole unit" / "a converted duration equal to the cap is admitted." | Q2: force lost. Two MUSTs restated as indicative. Spec adds "each ad's duration separately, before the cumulative sum" — a reading context does not state. |
| R4.10 | runtime | force-lost | 5.a | §4.5.1 item 7, L810: "A window whose `@maxDuration` is absent presents no ad, and the primary content continues. The absence is not read as the base specification's unbounded default." | Q2: force lost. MUST NOT / MUST continue arrive as indicative. Inherited linear case covered at L1353. |
| R4.11 | runtime | force-lost | 5.a | §4.5.4 item 5, L880: "The cap is measured on the presentation timeline. An interval in which the presentation timeline does not advance accrues nothing" | Q2: force lost. Both MUST and MUST NOT indicative. |
| R31.1 | runtime | force-lost | 5.a | §4.5.1 item 3, L793: "When a viewer pause begins inside a pause window, the Player holds a usable resolution for it: one obtained earlier and still usable (§5.2.5), or one it requests at that moment. A pause that begins outside every pause window triggers no request." | Q2: force lost. Also the spec reads "MUST request" as "holds a usable resolution" to reconcile with R36; that reading is a context ambiguity (A-6, 5.c), not a spec defect. |
| R31.2 | runtime | force-lost | 5.a | §4.5.10 item 7, L1020: "The cap does not bound a pause slot (§4.5.4)." / §4.5.4 table L864: "The cap is declared and bounds no duration." | Q2: force lost. Stated as semantics; "MUST NOT be interpreted as bounding" not carried as an obligation on Publisher or Player. |
| R12.1 | document | met | — | §3.4.2, L467: "These are the only values a Publisher writes in `@allowedLayouts` and the only values an APS writes in an option's `@layout`." / L518: "Tokens outside this table are not admissible anywhere" / §2, L211: "The source of every ad type and visual placement accepted in §3.4" | Q2: n/a (document). Table L469-L481 maps each token to its IAB type; `custom` flagged as the one exception (L514); XSD enum L3014-L3024 matches the 11 tokens exactly. |
| R12.2 | runtime | force-lost | 5.a | §4.2 item 6, L671: "Draws allowed layouts only from the tokens of §3.4.2" / §3.4.2 L518: "Tokens outside this table are not admissible anywhere, including Publisher-private layout names" | Q2: force lost. Complete token list, bare `pause`/`squeezeback` exclusion (L501) present; MUST / MUST NOT arrive as indicative. |
| R12.3 | runtime | force-lost | 5.a | §4.4 item 6, L738: "Emits only admissible layouts: tokens of §3.4.2, admissible for the document's family" | Q2: force lost. "checked against the resolution document" carried at §4.1 L608-L611. |
| R12.4 | document | met | — | §3.4.2, L507: "The spatial bounds are inherited by reference. Each accepted placement implies the bound the IAB guidelines declare for it" / "introduces no dimensional attribute" | Q2: source-has-no-modal. Spatial-bound column in table L469-L481. `@customRegion` on the slot is the R39 exception (L514); |
| R15.1 | document | met | — | §3.5, L540: "The admissible creative carriers are exactly three. No annex, example or note of this document adds another." | Q2: n/a (document). Consistent at §4.4 item 7 (L744), §5.3.2 (L2253), XSD FormType video/image/html; grep for svg/vpaid/simid/webp/webm finds only exclusions (L143-L148) and §8.6 (L3639). |
| R15.2 | runtime | partial | 5.c | §4.4 item 7, L744: "Emits only admissible creatives: every option's form is one of the three of §3.5, its creative is served with a media type §3.5 lists for that form" | Q2: force lost. APS half present, indicative. Publisher half absent: §4.2 states no creative-carrier obligation; only informative §8.6 L3634 names "the Publisher" as non-conformant. Context never defines what Publisher-declared forms are (A-8). |
| R15.3 | runtime | met | — | §4.5.3 item 5, L851: "A Player MAY skip a candidate whose creative is served with a media type outside §3.5, which signals a non-conformant APS or Publisher." | Q2: force carried. Spec drops "ADS" from the signalled parties, consistent with R15.2's check against the APS document. |
| R5#p1 | runtime | force-lost | 5.a | §4.5.3, L830-831: "For each candidate, the Player walks the presentation options in document order** and renders the **first** one that satisfies both" | Q2: force lost. Source "The Player MUST render the first presentation option..." (03 L650); spec states it indicatively. Edit: "the Player MUST render the first...". |
| R5#p2 | runtime | force-lost | 5.a | §4.5.3, L844-846: "A candidate with no option passing both checks is skipped**, and the Player moves to the next candidate. Only when every candidate is exhausted does it continue with the primary content." | Q2: force lost. Source "MUST skip candidates with no satisfiable option" (03 L652). |
| R5#p3 | runtime | force-lost | 5.a | §4.5.3, L835-837: "**(b) the window** — its `@layout` is in the window's allowed layouts: the declared `@allowedLayouts`, or the family default when none is declared (§3.4.3)" | Q2: force lost. Source "The Player MUST select per device capabilities and the Publisher's allowed layouts" (03 L671). |
| R5.1 | runtime | contradicted | 5.a | §4.4 item 5, L736-737: "The options it emits keep the order the decision gave them." and Annex Q.2.3 S-4, L8609: "Reorder them: reported against the known decision" | Q2: force lost as well (L734 "Carries each candidate's presentation options as an ordered list in preference order" is indicative). The ordered-list, one-or-more, no-maximum substance is met (L735, schema L3102 `maxOccurs="unbounded"`). R5.1 fixes that conformance "is checked against the APS's resolution document, which is the only artefact on the path to the Player"; item 5's last sentence and S-4 check the APS against the ADS decision. Contradicts §4.1 L610-614 and the Q.2.3 heading L8602. Fix: drop L736-737 sentence and S-4's decision-based control. |
| R5.2 | runtime | force-lost | 5.a | §4.5.3, L830-831: "the Player walks the presentation options in document order** and renders the **first** one that satisfies both" | Q2: force lost. |
| R5.3 | runtime | force-lost | 5.a | §4.5.3, L844-846: "A candidate with no option passing both checks is skipped**, and the Player moves to the next candidate. Only when every candidate is exhausted does it continue with the primary content." | Q2: force lost (two MUSTs in source, both indicative). Pause exception at §4.5.11 L1029-1030 matches context R32 (03 L889), not a contradiction. |
| R5.4 | document | met | — | §4.3, L714-715: "Nor is the ADS required to hold a device-class matrix or a per-Player capability view." and §4.4, L773-774: "The APS is not required to enforce the Publisher's constraints — the Player does — nor to hold a device-class matrix." | Q2: n/a (document). Context tags it runtime (ADS + APS) but its object is how the specification is read. The "keeping one is equally conformant" half is carried by §4.4 item 14 L770-771 ("MAY use capability parameters and forwarded declarations to narrow the options") and Annex M (L6685-6687). |
| R5.5 | runtime | met | — | §4.4 item 5, L735-736: "one or more per candidate; how many is the APS's decision" and §5.3.4, L2345-2346: "The order of the `<svta:RenderableAsset>` children of a candidate is the preference order" | Q2: force carried (source modal is MAY; permission stated as the APS's decision). |
| R5.6 | runtime | force-lost | 5.a | §4.5.3, L840-841: "An option that fails either check is not rendered**, and the Player moves to the next option in document order." | Q2: force lost. Both checks (device L832-834, window/family default L835-837) present; source "MUST resolve ... MUST NOT be rendered" arrives indicative. |
| R5.7 | runtime | force-lost | 5.a | §4.5.3, L844-846: "A candidate with no option passing both checks is skipped**, and the Player moves to the next candidate." | Q2: force lost. Order preservation carried by §4.5.5 L892. |
| R7#p1 | runtime | force-lost | 5.a | §4.5.5, L889-890: "The Player presents the candidates of a resolution document in the order the document declares" | Q2: force lost. Source "the Player MUST play the ads in the order" (03 L724). |
| R7#p2 | runtime | force-lost | 5.a | §4.5.5, L892-893: "The Player does not reorder, deduplicate or otherwise rearrange them" | Q2: force lost. Source "MUST NOT re-order, deduplicate" (03 L729); a prohibition stated as a description. |
| R7.1 | runtime | force-lost | 5.a | §4.5.5, L889-891: "The Player presents the candidates of a resolution document in the order the document declares**, dropping only a candidate with no renderable option (§4.5.3) or one dropped before play under §4.5.4." | Q2: force lost. Exceptions map exactly to R7.2 / R7.3. |
| R7.2 | runtime | met | — | §4.5.5, L890-891: "dropping only a candidate with no renderable option (§4.5.3)" | Q2: force carried (source MAY; spec makes it the mandatory skip of §4.5.3 L844, which R5.3 requires — see Ambiguity 1). |
| R7.3 | runtime | met | — | §4.5.4 item 3, L871-873: "The Player MAY drop a candidate before playback** when its declared duration would push the cumulative duration past the cap ("drop before play")." | Q2: force carried. |
| R7.4 | runtime | force-lost | 5.a | §4.5.5, L892-893: "The survivors keep their order.** The Player does not reorder, deduplicate or otherwise rearrange them" | Q2: force lost. |
| R7.5 | runtime | force-lost | 5.a | §4.5.4 item 2, L868-870: "The cap is enforced against actual rendered length**, not declared length: an accepted ad whose actual length exceeds its declared duration is trimmed where the cap falls ("trim during play")." | Q2: force lost. Pause family exempt by §4.5.4 table L864, consistent with context R31. |
| R30.1 | runtime | force-lost | 5.a | §4.4 item 4, L731-733: "Expresses an opportunity that resolved to no ads as an empty resolution** (§5.2.3): a well-formed, complete document carrying no candidate, served with `200` and a body." and §5.2.3, L2038: "It is not an empty body, not a `204`, not a `404`" | Q2: force lost. Both halves (MUST ... MUST NOT) present, neither as an obligation. |
| R30.2 | runtime | force-lost | 5.a | §4.5.6 item 6, L933-935: "A failed execution consumes nothing.** An empty resolution does not count as an execution: a linear event with `@executeOnce="true"` remains executable" | Q2: force lost. Pause extension at §4.5.10 item 6 L1017-1019. |
| R3.1 | document | met | — | §3.6, L565: "Every class has a defined outcome for every opportunity type: render, fall back to a later option, or skip and continue with the primary content." followed by the D1-D5 x opportunity table | Q2: n/a (document). Table covers linear, overlay, pause, hybrid, overlay-crossing-pause, custom, overlapping windows, ClickThrough, predating Player. D5 pause cell departs from UC-05 D5 |
| R3.2 | runtime | force-lost | 5.a | §4.5.16 item 2, L1112: "On every device class and for every opportunity type, the Player produces a defined behaviour" | Q2: force lost. Indicative; "undefined behaviour is non-conforming" not stated. The whole spec carries no MUST outside the boilerplate (A-25). |
| R3.3 | runtime | force-lost | 5.a | §4.5.3 item 4, L848: "The Player renders only forms its device can render." | Q2: force lost. MUST NOT restated in the indicative. |
| R16.1 | runtime | force-lost | 5.a | §4.5.10 item 1, L987: "the Player removes any rendered pause ad within one rendering frame" | Q2: force lost. |
| R16.2 | runtime | force-lost | 5.a | §4.5.10 item 2, L990: "From that transition on, the Player fires no further beacon of the dismissed pause ad" | Q2: force lost. Out-of-scope clause for later beacons carried. |
| R32.1 | runtime | met | — | §5.2.2 attribute table, L1963: "`@onCandidatesExhausted` / on a document whose `@family` is `pause`; absent on an overlay document / enum / a Player reading a pause document without it applies `stop`" | Q2: force carried (Required column binds the APS; Default column fixes `stop`). §4.6 step 4 L1158 checks "appears on pause documents only" and does not check presence; minor. |
| R32.2 | runtime | force-lost | 5.a | §4.5.11, L1027: "Under `request-again`, a document carrying no candidates, or none the device can render, is `stop` for the rest of that pause" | Q2: force lost. Spec widens to "none the device can render"; context says only no candidates (harmless extension). |
| R32.3 | runtime | force-lost | 5.a | §4.5.10 item 1, L988: "returns to the primary content immediately, whether or not an ad is mid-presentation." | Q2: force lost. |
| R32.4 | scope | met | — | §5.2.6, L2219: "Whether a second request within one pause is the same opportunity or a new one is not decided here." | Q2: n/a (scope); source-has-no-modal. Rationale and measurement pointer (§5.9) carried. |
| R34.1 | runtime | met | — | §4.2 item 9, L680: "MAY declare `@executeOnce="true"` on a pause window to bound it to one pause ad per session." | Q2: force carried (MAY). Default `false` in §5.1.4 table L1712 carries "a window that does not carry it yields a pause ad on every qualifying pause". |
| R34.2 | runtime | force-lost | 5.a | §4.5.10 item 6, L1014: "On a window with `@executeOnce="true"`, the Player presents at most one pause ad for that window for the whole session" | Q2: force lost. Annex E contradicts the literal reading (two ads under executeOnce); see A-11. |
| R34.3 | runtime | force-lost | 5.a | §4.5.10 item 6, L1017: "The window is consumed when a pause ad **begins rendering**, not when the pause occurs: a pause that resolves to no renderable candidate leaves the window available." | Q2: force lost. |
| R34.4 | document | met | — | §5.1.4, L1728: "The once-per-session bound reuses the base capability with the render event substituted for the playhead event." plus §4.8.1 row "`@executeOnce` and the execution counter / The once-per-session pause window" | Q2: n/a (document); source-has-no-modal. |
| R35.1 | runtime | met | — | §5.2.4, L2095: "absent / The slot is not dismissible. Dismissal is granted, never assumed." | Q2: force carried by construction: the carrier makes omission the declaration, so the APS cannot fail to declare; §4.4 item 10 L757 restates it in the indicative. |
| R35.2 | runtime | met | — | §5.2.4, L2096-2097: "`PT0S` / The slot is dismissible from its first rendered frame." / "`PTnS` (n > 0) / The slot becomes dismissible n seconds, on the presentation timeline, after its first rendered frame." | Q2: force carried by construction (presence of `@dismissAfter` requires a value). |
| R35.3 | runtime | force-lost | 5.a | §4.5.14 item 1, L1068: "On a non-linear slot, the Player makes dismissal available only as `@dismissAfter` declares" ... "for as long as the slot is on screen, and not before." | Q2: force lost. Scoped to non-linear; linear covered by item 2 (see R35.8). |
| R35.4 | runtime | force-lost | 5.a | §4.5.14 item 3, L1079: "A dismissal ends the whole slot. The Player stops presenting every ad of the slot and advances to no other ad or form within it." | Q2: force lost. Per-ad skip on linear via PlaybackRestrictions sits beside it (Edge case E1). |
| R35.5 | runtime | force-lost | 5.a | §4.5.14 item 4, L1081: "A dismissed slot does not shorten the primary content. Where the slot bounded a region of the primary timeline, the Player continues from where the primary content stands and skips none of it." | Q2: force lost. "compress" not named; covered only by "does not shorten". |
| R35.6 | runtime | force-lost | 5.a | §4.5.14 item 5, L1084: "The Player fires the beacons scheduled up to the moment of the dismissal, and none scheduled after it." | Q2: force lost. |
| R35.7 | scope | met | — | §4.5.14, L1091: "How dismissal is offered — a control, a gesture, a remote button — is out of scope." | Q2: n/a (scope); source-has-no-modal. |
| R35.8 | runtime | contradicted | 5.c | §5.2.4, L2129-2139: "An event that omits the attribute has the base value `PT0S` ... **the non-dismissible default of the non-linear families never governs a linear slot**, because every linear event has a skip value under the base schema." | Q2: force lost (L1073 "the Player honours the base declarations" is indicative). R35.8 says "R35.1's default applies only where neither the event nor the resolution document declares anything", i.e. there is a linear case where the default applies; the spec says there is none. The spec follows the criterion's last sentence (same behaviour as a base Player). Context is ambiguous (A-12), so the fix is in context/. |
| R36.1 | runtime | met | — | §4.2 item 8, L677: "MAY declare `@earliestResolutionTimeOffset` on an overlay or pause window, and declares `0` when it wants the window resolved only when it fires." Default in §5.1.3, L1635 and §5.1.4, L1711: "60 s in `@timescale` units" | Q2: force carried (MAY). The 60 s default and the zero offset are both there. |
| R36.2 | runtime | force-lost | 5.a | §4.5.1 item 2, L787: "An overlay window is resolved no earlier than its earliest resolution time" | Q2: force lost. The criterion is a Player MUST NOT; the spec uses a passive indicative. The substance matches, including the default via L788-789. |
| R36.3 | runtime | force-lost | 5.a | §4.5.1 item 3, L791-792: "A pause window is resolved no earlier than its earliest resolution time**, computed against the window's start and never against the pause." | Q2: force lost. The criterion is a MUST NOT and the spec uses the indicative. The reference against the start, not the pause, is carried. |
| R36.4 | runtime | force-lost | 5.a | §4.4 item 11, L760-761: "Declares `@usableFor` whenever its decision stays good for less than the window lasts** (§5.2.5); omitting it declares that the document is usable for the whole window." | Q2: force lost. The criterion is an APS MUST and the spec uses the indicative. The spec also reads "MUST declare" as "declare it when shorter than the window", which follows from the context default but is not the literal MUST |
| R36.5 | runtime | force-lost | 5.a | §4.5.1 item 5, L800-802: "When an overlay or pause opportunity fires, the Player checks that the resolution it holds is still usable.** A resolution past its `@usableFor` is not presented: the Player requests a new one" | Q2: force lost. The criterion has three MUSTs (check, request, MUST NOT present) and all three are in the indicative. |
| R36.6 | runtime | force-lost | 5.a | §4.5.1 item 5, L802-804: "a new one that yields no usable candidate is an empty resolution (§4.5.6) — the expired resolution is never used as a fallback." | Q2: force lost. The spec has the MUST and the MUST NOT as descriptions. The link to empty resolution conflicts with §4.5.6 item 4 when candidates are present but none can be rendered (A-15). |
| R36.7 | document | met | — | §4.5.1 item 4, L797: "Resolving early is a permission, never an obligation.** A Player that resolves only when the opportunity fires is conformant whatever offset the window carries." Repeated in §7.11, L3514. | Q2: source-has-no-modal. |
| R37.1 | runtime | met | — | §4.5.10 item 4, L999-1002: "The Player MAY pause by any mechanism that suspends the primary content and later resumes it from the position at which it was suspended, including one that releases the primary content's decoding resources for the pause." | Q2: force carried (MAY). |
| R37.2 | runtime | force-lost | 5.a | §4.5.10 item 4, L1002-1004: "On resume it continues the primary content from that position; a mechanism that cannot restore the position is not a pause under this specification, whatever it is called." | Q2: force lost. The criterion is a Player MUST and the spec uses the indicative. The definitional second sentence is carried. |
| R37.3 | document | met | — | §4.5.10 item 4, L998-999: "A pause is what the viewer experiences, not how the Player achieves it." §3.6, L593-594: "a Player that keeps the decoder holding the paused frame and presents only non-video pause forms is equally conformant." | Q2: source-has-no-modal. No spec criterion found that assumes one pause mechanism: §5.3.7 L2500 presents decoder release as a condition ("when the Player releases"), not as a requirement. |
| R38.1 | runtime | met | — | §4.2 item 6, L673-674: "Declaring `@allowedLayouts` is OPTIONAL; a window that declares none admits its family's default (§3.4.3)." §3.4.3, L535-536: "an overlay window that declares nothing does not admit the `linear` full-screen takeover — and it does not admit `custom`" | Q2: force carried (OPTIONAL). The §3.4.3 table has the right per-family sets: 7 overlay/squeezeback tokens for overlay, 2 pause tokens for pause. |
| R38.2 | runtime | force-lost | 5.a | §5.8.3, L2873-2874: "When a non-linear window declares `@allowedLayouts`, the Player sends the declared set to the APS on the resolution request" and L2880 "the window's `@allowedLayouts` value, unchanged" | Q2: force lost. The criterion is a Player MUST. The spec has an indicative sentence plus a table cell "Required: yes", which is not an RFC 2119 keyword. The "nothing is sent" branch is carried at L2887. |
| R38.3 | document | met | — | §5.8.3, L2880: "`sgaiAllowedLayouts` / yes, on the resolution request of a non-linear window that declares `@allowedLayouts`" and §5.8.4: "Every parameter name beginning with `sgai` is reserved" | Q2: source-has-no-modal. The carrier is normative and is a reserved query parameter, as the criterion's example gives. |
| R38.4 | runtime | force-lost | 5.a | §4.4 item 6, L738-741: "Emits only admissible layouts**: tokens of §3.4.2, admissible for the document's family (§5.3.3), and within the set the request forwarded (`sgaiAllowedLayouts`) or, when it forwarded none, within the family default (§3.4.3)." | Q2: force lost. The criterion is an APS MUST NOT; the spec uses the indicative plus a lowercase "required" in the paragraph after §4.4. |
| R38.5 | runtime | force-lost | 5.a | §4.5.3 item 1(b), L835 "its `@layout` is in the window's allowed layouts"; item 2, L840-843: "An option that fails either check is not rendered** ... The check holds whether or not the Player forwarded the allowed layouts" | Q2: force lost. The criterion has a MUST check and a MUST NOT render; both are in the indicative. The rule that forwarding does not remove the check is carried. |
| R38.6 | scope | met | — | §5.8.3, L2896-2897: "Linear windows carry no layout declaration and are outside this rule." Also §3.4.3: "Linear windows carry no allowed-layout declaration" | Q2: n/a (scope); source-has-no-modal. |
| R39.1 | document | met | — | §5.3.5, L2369-2372: "`custom` is **optional for every actor**. A Publisher, an APS and a Player that do not support it are conformant. It applies to the overlay family only, and it is the one layout for which this specification defines a position." §3.4.2: "`custom` is the one exception to the IAB mapping and to the absence of positions." | Q2: n/a (document). Note: the context says "OPTIONAL" and the spec writes lowercase "optional", but the conformance sentence carries the substance. |
| R39.2 | runtime | met | — | §5.3.5, L2401-2403: "A Publisher that admits `custom` lists it in `@allowedLayouts` and MAY declare `@customRegion`. With no region declared, the region is the whole viewport, `0,0,100,100`." | Q2: force carried (MAY). "lists" is indicative in context too. The notation (x,y,w,h in percent, origin top-left) is at L2377-2383; the integer domain is the spec's narrowing (a HOW choice). |
| R39.3 | runtime | force-lost | 5.a | §5.8.3, L2875-2876: "When it declares `@customRegion`, the Player sends that too." and L2881 "`sgaiCustomRegion` / yes, on the resolution request of an overlay window that declares `@customRegion`" | Q2: force lost. The criterion is a Player MUST; the spec uses the indicative plus "Required: yes". |
| R39.4 | runtime | force-lost | 5.a | §4.4 item 6, L741-743: "A `custom` option carries a `@customRectangle` lying inside the region the request forwarded, or inside the viewport when it forwarded none." §5.3.1, L2249 "yes when `@layout` is `custom`"; §5.3.5, L2407 "It MAY be smaller than the region." | Q2: force lost for the three MUST/MUST NOT (carry, lie inside, not extend beyond); the MAY is carried. |
| R39.5 | runtime | force-lost | 5.a | §4.5.3 item 1(b), L837-839: "For a `custom` option, the Player also supports `custom` and the `@customRectangle` lies inside the window's region, or the viewport when none is declared (§5.3.5)." item 4, L848-850: "A Player that does not support `custom` treats every `custom` option as not renderable." | Q2: force lost. The MUST check and MUST NOT render are in the indicative. Moving to the next option is carried at L840-841. |
| R19#p1 | runtime | force-lost | 5.a | §4.5.12, L1034: "The Player renders every ad form, linear or non-linear, at the playback speed of the primary content" | Q2: force lost. Substance complete (wall-clock derivation in item 2); the MUST arrives in the indicative. |
| R19.1 | runtime | force-lost | 5.a | §4.5.12, L1034-1036: "The Player renders every ad form, linear or non-linear, at the playback speed of the primary content** at the moment the ad is presented" | Q2: force lost. Indicative. |
| R19.2 | runtime | force-lost | 5.a | §4.5.12, L1036: "and does not force an ad to 1× when the primary content plays at another speed" | Q2: force lost. MUST NOT restated as "does not". |
| R19.3 | runtime | force-lost | 5.a | §4.5.12, L1039-1043: "wall-clock length of a form is derived as `duration / playback_speed` ... Cap enforcement and beacon scheduling use the presentation-timeline duration" | Q2: force lost. Both halves present (derivation; cap and beacons on the presentation timeline), indicative. |
| R19.4 | runtime | force-lost | 5.a | §4.5.12, L1044-1047: "This holds for every form**, including `image` and `html`, which have no intrinsic media: their declared duration is a presentation-timeline value and their wall-clock length is derived the same way" | Q2: force lost. Indicative. |
| R21.1 | runtime | force-lost | 5.a | §4.5.10 item 3, L993-997: "The Player MAY present a pause ad fullscreen or as a partial overlay ... For a partial one, the paused frame stays visible and any coexisting overlay stays suspended (§4.5.9)" | Q2: force lost. The two MAYs are carried with their modal. The MUST (at most one non-linear form active in a partial pause) is indicative here and in §4.5.8 L950. |
| R25#p1 | runtime | force-lost | 5.a | §4.5.10 item 5, L1005-1007: "In live content, while the viewer is paused inside a pause window, the Player keeps its presentation time frozen inside that window** for the full duration of the pause" | Q2: force lost. Indicative. |
| R25.1 | runtime | force-lost | 5.a | §4.5.10 item 5, L1006-1012: "the Player keeps its presentation time frozen inside that window ... Where the Player resumes after the pause — at the frozen position, at the oldest position the time-shift buffer still holds, or at the live edge — is a Player action that follows the resume and lies outside the pause window" | Q2: force lost. Both MUSTs present in substance, indicative. §8.8 L3667 adds the buffer case (informative chapter). |
| R26.1 | runtime | force-lost | 5.a | §4.4 item 8, L750-752: "Carries a background image on every `squeezeback-double-box-background` option** in `@backgroundUrl`, as a composition attribute of the layout (§5.3.6)" | Q2: force lost. Not a separate option (§5.3.6 L2462: "The background is a composition attribute of the layout, not an option"). The carrier is an attribute of the option element (`@backgroundUrl`, §5.3.1 L2248), not of the slot. The criterion's "slot / layout" admits that reading; Publisher, a named actor of R26.1, carries nothing in the spec. |
| R26.2 | runtime | force-lost | 5.a | §5.3.6, L2450-2452 and L2455-2457: "puts the shrunk primary content and the ad in two boxes side by side. The two boxes leave bands uncovered, and without a background those bands render **black**" / "adds a third element: the advertiser's **background image** at `@backgroundUrl`, filling the uncovered bands" | Q2: force lost. All three parts are present (the two boxes, the background in the bands, black when there is none), stated as a description of the layout and not as a Player obligation. |
| R26.3 | runtime | force-lost | 5.a | §5.3.7, L2477-2478 and L2491 / L2494: "This table is the rule that makes an option satisfiable or not: the Player evaluates it (§4.5.3)" / "`squeezeback-double-box` / `video` / 2 (primary + ad) / none / D1, D2" / "`squeezeback-double-box-background` / `video` / 2 (primary + ad) / image, for the background / D1" | Q2: force lost. The rows match context/ against §3.6 L557-563: video needs 2 decoders; an image background excludes D2. The two MUST NOTs arrive as §4.5.3 L840 "An option that fails either check is not rendered". |
| R27.1 | runtime | force-lost | 5.a | §5.3.6, L2437-2439: "The L-shape — `squeezeback-l-shape-upper-left`, `squeezeback-l-shape-upper-right` — carries exactly **one** ad creative, an image, a video or an HTML document, and that creative is always **full-frame, in the background**" | Q2: force lost. Descriptive. The syntax enforces it structurally (one `@assetUrl`, and "The element has no children" at L2251), but the APS obligation is not stated with a modal. |
| R27.2 | runtime | force-lost | 5.a | §5.3.6, L2440-2442: "The Player shrinks the primary content into the region the token names and composites it **on top of** the creative" | Q2: force lost. Indicative. |
| R27.3 | runtime | force-lost | 5.a | §5.3.7, L2488: "`squeezeback-l-shape-*` / `video` / 2 (full-frame creative + shrunk primary) / none / D1, D2" (image row: D1, D3, D4; html row: D1, D3) | Q2: force lost. The budget matches context/. The MUST NOT is carried only through §4.5.3 L840, in the indicative. |
| R14.1 | runtime | force-lost | 5.a | §4.5.8 item 2, L955-957: "When a non-linear document carries more than one candidate, the Player presents them in sequence**, in document order, each starting when the previous one ends" | Q2: force lost. Indicative. |
| R14.2 | runtime | force-lost | 5.a | §4.5.4, L863 and L866-867: "Overlay / **How long**: the cumulative duration of what the slot presents" / "The Player extends no slot beyond what the cap bounds for its family" | Q2: force lost. Trim and drop are covered in items 2-3 (L868, L871). The pause family is exempted (L864: "Pause / **Nothing**"), following R31.2 rather than the letter of R14.2 (A-16). |
| R14.3 | document | met | — | §4.5.8 item 1, L950: "At any instant the Player keeps at most one non-linear ad form active on screen"; sequencing is by document order only (L956) | Q2: n/a (document). Property checked: the schema §5.10 has no construct that orders or parallelises forms beyond document order (the elements are OverlayPresentation, PauseAdPresentation, OverlayList, Candidate, RenderableAsset, Click and the metadata). `grep -i 'simultaneous/concurrent/render-then/in parallel'` turns up only the hybrid (linear + non-linear), which R22 permits. |
| R17.1 | runtime | force-lost | 5.a | §4.5.9 item 1, L967-969: "While the viewer is paused inside a pause window and an overlay is active, the Player renders the pause ad and suspends the overlay" | Q2: force lost. Indicative. |
| R17.2 | runtime | force-lost | 5.a | §4.5.9 item 2, L971-973: "On resume, the Player dismisses the pause ad and restores the overlay if the overlay's window is still open at the position where playback resumes" | Q2: force lost. Indicative. |
| R17.3 | runtime | force-lost | 5.a | §4.5.9 item 2, L975-976: "on live content the resume position (§8.8) may lie past the window's end, and then the overlay is over and the surface stays clear" | Q2: force lost. The spec recasts "expired during the pause" as "past the window's end at the resume position", because presentation time is frozen during the pause (Edge case E1). |
| R17.4 | document | met | — | §4.5.9 item 4, L981-982: "The priority is fixed: pause ad above overlay, and above a linear ad, during a pause. No construct lets any actor invert it." | Q2: source-has-no-modal. Property checked: the schema §5.10 has no priority attribute. `grep -i priority` hits only §4.5.9, §4.8.7 (`@selectionPriority`, not reused), §5.1.5 (the base queue) and §7.7. |
| R17.5 | runtime | force-lost | 5.a | §4.5.9 item 3, L977-980: "When a viewer pause begins inside a pause window while a linear ad occupies the screen, the Player presents the pause ad and suspends the linear ad**, and on resume continues the linear ad from where it was suspended" | Q2: force lost. All three MUSTs are present in substance, in the indicative. |
| R20.1 | runtime | force-lost | 5.a | §4.5.6 items 2-5, L902-904 and L930-931: "An attempt that produces no ad is a failed execution, and on a failed execution the Player attempts the next overlapping window of the family" / "the Player continues with the primary content uninterrupted" | Q2: force lost. Substance complete: the four failure modes (plus a fifth, wrong family) in the L911 table; linear adopted and non-linear extended (L906-908); a document with candidates is not a failed execution (L923). |
| R20.2 | runtime | force-lost | 5.a | §4.2 item 5, L668-669: "Authors every window of one family in a Period inside a single `<EventStream>`** of that family's scheme (§5.1.5)" | Q2: force lost. Only the quoted base-spec text carries "shall" (§5.1.5 L1761); the Publisher obligation is indicative. |
| R20.3 | runtime | force-lost | 5.a | §4.5.6 item 1, L898-900: "When windows of one family overlap in time, the Player orders them by presentation time, oldest first, and takes windows with equal presentation times in the order they appear in the stream" | Q2: force lost. The extension to the non-linear families and the tie-break are stated as ours at §5.1.5 L1774-1784. |
| R20.4 | runtime | force-lost | 5.a | §4.5.2 item 2, L820-824: "A document is a resolution of the requested slot only if its family matches ... Any other document is a failed execution of that window (§4.5.6), and none of its candidates is presented" | Q2: force lost. §4.5.6 table L921 continues the chain. Indicative. |
| R20.5 | runtime | force-lost | 5.a | §4.5.7, L943-946: "The Player validates the candidates each window of a fallback chain serves against **that window's own** declarations — its allowed layouts, its custom region and its cap — and never against those of the window it stands in for" | Q2: force lost. Substance complete (a superset: it adds the custom region). Indicative. |
| R20.6 | document | met | — | §4.5.7, L941-946 (chapter 4, which is normative per L20: "Chapters 1 to 7 are normative"; §4.1 L602-603: "it satisfies every obligation of §4.2 to §4.5 addressed to that actor") | Q2: n/a (document). The rule is in a normative Player section and has test L-19 (L8642), not only in informative material. It carries no RFC 2119 keyword either (see R20.5). |
| R22.1 | runtime | force-lost | 5.a | §4.5.8 item 1, L950-953: "At any instant the Player keeps at most one non-linear ad form active on screen.** The bound keeps the device from ever needing more than the primary content plus one ad form" | Q2: force lost. Both the MUST and the MUST NOT are indicative. |
| R6#p1 | document | met | — | §5.5, L2576: *"This specification mints no tracking scheme."*; §5.5.2, L2621: *"Directly inside the `<svta:Candidate>`; there is no sub-MPD to host it"* | Carrier shape (§5.5.1), placement (§5.5.2) and timebase (§5.5.3) are all specified. Q2: n/a (document) |
| R6#p2 | runtime | force-lost | 5.a | §4.5.13 item 5, L1062: *"The Player ignores extension elements and attributes of a namespace it does not implement"* | Substance present in indicative only. Q2: force lost. Same cause as every force-lost row (A-25, T1) |
| R6.1 | document | met | — | §5.5.2, L2617-2621: *"Linear ad / Inside the sub-MPD's Period, or on the List MPD Period of the ad"*; *"Non-linear candidate, `image` or `html` option / Directly inside the `<svta:Candidate>`; there is no sub-MPD to host it"* | Q2: n/a (document) |
| R6.2 | runtime | met | — | §4.4 item 9, L753: *"Translates the ADS's tracking schedule into callback events"*; §5.5, L2576 | Callback scheme is the only tracking carrier the spec defines and §4.6 step 3 validates it, so the SHOULD holds by construction. Q2: force carried (SHOULD, strengthened) |
| R6.3 | document | met | — | §5.5, L2576: *"This specification mints no tracking scheme."*; §2.1, L262: *"This specification mints no tracking scheme and no profile."* | No new carrier, so the gate is not exercised. Q2: n/a (document) |
| R6.4 | runtime | force-lost | 5.a | §4.5.13 item 5, L1062: *"The Player ignores extension elements and attributes of a namespace it does not implement"* | Same passage as R6#p2. Q2: force lost |
| R6.5 | runtime | force-lost | 5.a | §5.5.4, L2677-2682: *"De-duplication is **scoped to the ad**: the `<svta:Candidate>` on a non-linear document ... the Player fires both."*; §4.5.13 item 3, L1058 | Scope and both-fire rule present; Player obligation indicative. Q2: force lost |
| R6.6 | runtime | force-lost | 5.a | §4.5.13 item 4, L1060: *"A callback stream inside a `<svta:Candidate>` resolves against that candidate's own presentation."* | Also §5.5.2 L2634. Q2: force lost |
| R6.7 | document | met | — | §4.6, L1161: *"A validation report states which steps it ran."*; §4.6 step 3 scans *"inside every `<svta:Candidate>`"* | Property holds: four-step procedure incl. candidate-hosted carrier. Q2: n/a (document) |
| R13#p1 | document | met | — | §5.5.1, L2611: *"Which beacons exist, how many, and when, are the ADS's. This specification fixes the carrier and the timebase"*; §5.5.3, L2648 | No hardcoded fractions (L2661). Q2: n/a (document) |
| R13.1 | runtime | force-lost | 5.a | §4.4 item 9, L753-754: *"Translates the ADS's tracking schedule into callback events (§5.5), with times relative to each ad's presentation"* | Form and timebase present, indicative. Q2: force lost |
| R13.2 | runtime | force-lost | 5.a | §4.5.13 item 1, L1051: *"For every ad accepted for rendering, the Player executes the tracking schedule the resolution document carries"* | v9.1 carried a MUST here; v10 dropped it. Q2: force lost |
| R13.3 | runtime | force-lost | 5.a | §4.5.13 item 2, L1055: *"When the cap trims an ad, the Player stops firing that ad's remaining beacons at the trim boundary."* | Regression from v9.1 (was MUST). Q2: force lost |
| R13.4 | document | met | — | §5.5, L2576: *"This specification mints no tracking scheme."*; L2582: *"A parallel scheme would split tracking across two carriers"* | Q2: n/a (document) |
| R13.5 | scope | met | — | §4.1, L612-614: *"what the ADS decided, and how faithfully the APS transcribed it, belongs to the APS-to-ADS contract"*; Q.8, L8750 | Boundary stated. But (§4.4 item 5 / S-4 check fidelity against the decision). Q2: source-has-no-modal |
| R23.1 | document | met | — | §5.7, L2752: *"Emitting and reading are both optional, and the carrier is non-interoperable by design."* | Elements in `urn:svta:dash:sgai:2026` (§2.1 L242). on `<svta:UniversalAdId>`. Q2: n/a (document) |
| R24#p1 | runtime | force-lost | 5.a | §4.4 item 7, L748: *"addressed by `@assetUrl` and never by a `@mimeType` on an Adaptation Set or a Representation"* | Prohibition present, indicative. Q2: force lost |
| R24#p2 | runtime | force-lost | 5.a | §5.3.2, L2282: *"**(a)** Foreign-namespace open content: the URL as an attribute of an element of this specification / DASH §5.2.1 / **Selected.**"* | Carrier is DR-6 (a), described not required. Q2: force lost |
| R24.1 | runtime | force-lost | 5.a | §4.4 item 7, L744-749: *"an image or HTML creative is addressed by `@assetUrl` and never by a `@mimeType` on an Adaptation Set or a Representation"* (indicative, under *"A conformant APS"*) | Document half holds (DR-6 carrier chosen); APS half indicative. Q2: force lost |
| R33.1 | document | met | — | §5.9, L2941: *"this specification defines no metric of its own"* | Q2: n/a (document) |
| R33.2 | runtime | force-lost | 5.a | §4.5.17, L1123-1125: *"A Player that reports metrics derives the paused interval from the `PlayList` entries as §5.9 describes, and counts no playback period that stopped on `Rebuffering`"* | Regression from v9.1 (was MUST on both halves). Q2: force lost |
| R33.3 | scope | met | — | §5.9, L2983: *"How a measurement reaches anyone is out of scope"*; §1.3, L173 | Q2: source-has-no-modal |
| R33.4 | runtime | force-lost | 5.a | §4.2 item 10, L682: *"Requests the play-list metric with a `<Metrics>` element on the main MPD whenever the content carries pause windows"* | Also §5.9 L2964 indicative. P-7 tests it. Q2: force lost |
| R28#p1 | document | met | — | §5.6, L2692-2694: *"in one carrier, so that every Player conformant to this specification reads them the same way"*; §5.6.1 tables | Carrier explicitly defined. APS force is R28.1's row. Q2: n/a (document) |
| R28.1 | runtime | force-lost | 5.a | §4.4 item 9, L754-756: *"carries a ClickThrough, when the ad has one, in `<svta:Click>` together with any click-tracking URLs"*; §5.6.1, L2735 | "not elsewhere" only implied by L2735 *"is not a ClickThrough this specification recognises"*. Q2: force lost |
| R28.2 | runtime | force-lost | 5.a | §4.5.15, L1097: *"A Player conformant to this specification **reads `<svta:Click>`** and, when the viewer activates the ClickThrough, opens ... and fires every `<svta:ClickTracking>` URL once per activation"* | Regression from v9.1 (was MUST). Q2: force lost |
| R28.3 | scope | partial | 5.b | §4.1, L612-614: *"how faithfully the APS transcribed it, belongs to the APS-to-ADS contract"* | Generic boundary only; ClickThrough not named. §4.4 item 9 *"when the ad has one"* and S-10 L8615 (input *"An ad with tracking and a ClickThrough"*, pass *"`<svta:Click>` carries the ClickThrough"*) read as checking arrival of a declared ClickThrough, which R28.3 puts outside. Q2: source-has-no-modal |
| R8.1 | document | met | — | §4.8, L1303: *"Every construct this specification introduces states inline why an existing construct could not be reused"*; §4.8.2 table L1328-1344 | Event scheme URIs and resolution URN now justified (v9.1 gap closed). `@backgroundUrl` has no own row; covered by the image-has-no-media-axis reasoning (§5.3.2). Q2: n/a (document) |
| R8.2 | document | met | — | §4.8.4, L1359: *"The supplementary video descriptor — weighed, not taken"*; §4.8.5-§4.8.11 | Q2: n/a (document) |
| R9.1 | document | met | — | §4.8.1 table L1307-1326; §5.1, L1504: *"The event machinery is reused, not extended."* | Q2: n/a (document) |
| R9.2 | document | met | — | §4.8.2, L1328: *"Introduced, and why nothing existing fits"* (table) | Q2: n/a (document) |
| R9.3 | document | met | — | §5.1.3, L1604: *"Why a new element and not an attribute on the alternative-MPD events."*; §5.3.2 carrier table (c1)/(c2) | Extension considered and outcome recorded. Q2: n/a (document) |
| R10.1 | document | met | — | §1.3, L127-128: *"Spatial arrangement inside a layout is delegated to HTML5 and CSS"* | Q2: n/a (document) |
| R10.2 | document | met | — | §5.3.6, L2428: *"This specification declares no positioning vocabulary except the `custom` rectangle."* | Q2: n/a (document) |
| R10.3 | scope | met | — | §1.3, L132: *"Position semantics inside a layout — left, right, top, bottom, which corner."*; L129-130 *"with the single exception of the optional `custom` overlay layout"* | R39 exception stated. Q2: source-has-no-modal |
| OOS-1#p1 | document | met | — | §1.3, L127-129: *"A layout engine. ... This specification declares no positioning vocabulary of its own"* | Q2: n/a (document) |
| OOS-4#p1 | runtime | force-lost | 5.a | §1.3, L144-145: *"A scripted creative is wrapped in an HTML document and carried as `text/html`."* | Sender obligation indicative. Q2: force lost |
| UC-01 | use-case | met | — | Annex A (§A.1-A.6); §A.6, L4027: "The outcome is the same on D1 to D5. A linear video ad and the primary content are sequential on one decoder"; §A.1, L3786: "no non-linear ad over the break or over the opening of the film"; §7.2 L3374 "Every device class can present a linear break" | All five classes covered (D1-D2 pre-buffer MAY, D3-D5 one decoder), bounded cap (A.5 step 4), clean handoff, film from first frame (A.5 step 8). Matches UC D1-D5. Q2: n/a (use-case) |
| UC-02 | use-case | met | — | Annex B; §B.8, L4366: "The outcome is the same on D1 to D5, for all three viewers. A linear video ad and the primary content are sequential on one decoder"; trick-play §B.7 and §7.2 L3379: "At 1.5× or 2×, the ad plays at the same speed" | D1/D2 optional pre-buffer, D3-D5 switch one decoder at each boundary, as UC. Annex walks the replacement (live) case; insertion covered by §7.2 and Annex F. Trick-play variant walked with cap/beacons on presentation timeline. Q2: n/a (use-case) |
| UC-03 | use-case | met | — | Annex C §C.6; L4601: "D2 declines option 1. It has the two decoders, but the background is a still image"; L4605: "D3 declines options 1 and 2, because each needs a second video decoder"; L4613: "D5 declines all four options"; D2 side-by-side via §5.3.7 L2491: "`squeezeback-double-box` / `video` / 2 (primary + ad) / none / D1, D2" | D1 first option in order; D2 video overlay (side-by-side only for the no-background double box); D3 HTML; D4 image (walked as an image L-shape, then image lower third); D5 skip. Cap (C.7), one-on-screen (C.1), playback speed (C.7) present. Context UC-03 D2 is internally inconsistent with its own side-by-side definition; see Ambiguity 3. Q2: n/a (use-case) |
| UC-04 | use-case | met | — | Annex D §D.7; L5026: "D2 accepts option 1 on its second decoder. Had the candidate offered only options 2 and 3, D2 would decline the overlay"; L5030: "D3 declines option 1 and accepts option 2. It composites the HTML lower-third over the linear ad"; L5035: "D5 declines all three options. The candidate is skipped, and the linear ad plays alone" | All five classes walked, one-decoder budget per ADR 0012 matches UC D3/D4 arithmetic; independence of portions (D.1, D.8) matches OOS-8. UC D3/D4 L-shape branch is not walked, consistent with the UC's own intent (lower-third only); see Ambiguity 4. Q2: n/a (use-case) |
| UC-05 | use-case | met | — | Annex E §E.6; L5298: "A Player on D3, D4 or D5 MAY satisfy the fullscreen video option by releasing the paused content's decoder"; L5306: "D2 / option 1, fullscreen video (second decoder) / skipped: an image surface is not satisfiable on D2"; L5312: "D5, decoder kept / skipped: no option satisfiable / skipped / none" | Window of validity, pause outside window yields nothing (E.1, §7.6), resume removes ad and continues from paused position (E.8), live variant with frozen presentation time (E.10). D3/D4 conservative choice (HTML / image) shown alongside R37 re-tasking. Spec extends the MAY to D5, which UC-05 D5 does not; the UC's decline remains a conformant row. See Ambiguity 5. Q2: n/a (use-case) |
| UC-06 | use-case | met | — | Annex F; §F.7, L5768: "The outcome is the same on D1 to D5. Every ad is a linear video"; F.6 step 4: "the cumulative presentation reaches 60 s and the Player stops rendering it" | N decided by ADS (F.1), order preserved, cut at cap mid-ad, D1/D2 pre-buffer MAY, D3-D5 single decoder. Drop-before-play shown as the other R14 outcome (context 03-requirements.md L738). Q2: n/a (use-case) |
| UC-07 | use-case | contradicted | 5.c | §7.9, L3486-3488: "A Player of this specification executes that break as well — it is a base event, resolved as the base specification defines — and additionally takes the SGAI path"; also §G.9 | Skip-and-continue, live = expected loss, VOD standard break authored unconditionally, device-class invariance (G.10 L6070) all met. But UC-07 (04-use-cases.md L815-817, L822) says the standard break is "the legacy fallback only" and "simply ignored by current Players"; the spec has a current Player play both. Spec follows R1.5 (base event is executed); context must say which outcome it wants or supply a requirement for a mechanism. Q2: n/a (use-case) |
| UC-08 | use-case | partial | 5.c | Annex H; §H.1, L6092: "While paused inside the pause window with an overlay active, the Player renders the pause ad and suspends the overlay"; §H.9 L6387 D2 fullscreen video; L6396: "On D5 with resources kept, nothing renders in either slot"; H.7 L6320: "requests the pause document, and presents q1" | All five classes walked, suspend/restore, clock frozen, window expiry (H.8 Branch B) match. Not carried: the UC's alternative flow "unless the Publisher's MPD signals that the overlay candidate doubles as the pause-ad candidate" (04-use-cases.md L885). No requirement defines that signal and it conflicts with R31.1 (MUST request on a pause inside a window); the spec follows R31.1. Context must drop the clause or define it. Q2: n/a (use-case) |
| UC-09 | use-case | met | — | Annex I.6, L6641-6677, walk table + prose: "D2 owns the two decoders option 1 needs and still declines it" (L6662); I.7, L6681: "One ordered list, emitted identically to every viewer, and one device-agnostic declaration produce the correct layout on each class: D1 on the double box, D3 and D4 on the L-shape, D2 and D5 on the takeover." | All five classes walked, same options in same order, same outcome per class as UC-09 (D1 opt 1, D2 opt 4, D3/D4 opt 2, D5 opt 4), D2 element-type contrast and D5-vs-D2 different paths stated. Q2: n/a (use-case) |
| UC-10 | use-case | met | — | Annex J.7, L6861-6898: "D2 declines option 1. It has the two decoders, but the background is an image surface and D2 composites none. It accepts option 2: the same video in the same box, with black bands." (L6868-6870); J.6 budget table L6844-6851 covers video / image / HTML ad per class | All five classes; both background cases (advertiser background, black bands) exercised; background as layout attribute not walked (J.1). D2 renders a no-background double box, which UC-10 D2 text does not mention but its own rule ("the background is the blocker, not the decoder count") implies — see Ambiguity 1. Q2: n/a (use-case) |
| UC-11 | use-case | met | — | Annex K.7, L7144-7156: "What an activation does is the same on every device class; the class decides only whether an ad is on screen to be activated." / D1 row L7152: "opens the destination, fires every click-tracking URL once"; K.6 L7136: "The ad plays and its ClickThrough is inert" | Linear and non-linear, click separate from callback beacons (K.5 table), legacy inert click (K.6), all five classes. Q2: n/a (use-case) |
| UC-12 | use-case | met | — | Annex L.4, L7254-7270 (three paths: empty then ad / all empty / none reachable); L.8 L7466: "Window selection is the same on every device class: which window is served depends on what each attempt returned, never on the device"; L.6 per-class table L7400-7406 | Spec uses three windows instead of two; the three UC paths map one-to-one. L.7 L7458 "It does not attempt 702" follows R20.1 (non-renderable candidates are not a failed execution) and contradicts the literal UC-12 wording "whatever its shape" — context-internal, see Ambiguity 2. Q2: n/a (use-case) |
| UC-13 | use-case | met | — | Annex M.3 L7547-7567 (five requests, D3 omits HTML axis, D4 sends nothing); M.7 L7755-7770: "D4 is the Annex I case exactly: a Player that declares nothing leaves the APS unable to narrow" (L7769); M.8 L7794: "The outcome per class equals Annex I's." | All five classes; single option emitted for D1/D2/D3/D5, full list for D4; Player check retained; undetermined-axis policy is the APS's. Q2: n/a (use-case) |
| UC-14 | use-case | met | — | Annex N.6, L7992-8038: "D2 declines both options, because it composites no image or HTML over video. The slate plays alone. A `video` overlay option, had the candidate offered one, would composite on D2's second decoder" (L8014-8017); L8037: "Row for row, this is the hybrid row of §3.6, with the slate in the place of the linear ad." | The v10 spec DOES walk UC-14 (Annex N), contrary to validate-spec.prompt §4.1's acceptance-test note, which is stale for v10. ReplacePresentation to a Publisher List MPD, no ADS/APS, overlay with image+HTML options, tracking/Click/cap only on the overlay (N.5), five classes match UC. Minor deviation: overlay window covers part of the span (L7807 "over part of the same span") where UC says "covering the same span" (04-use-cases.md:1577); does not change the demonstration. Q2: n/a (use-case) |
| UC-15 | use-case | met | — | Annex O.6, L8232-8255: D1/D3/D4 "L-shape"; L8246: "D2 and D5 get no ad. The empty resolution is a failed execution"; L8249: "takeover both classes could have played is never offered, because the Publisher excluded it"; O.7 L8342: "Forwarding the set moves the choice upstream; it does not move the check." | Forwarded set on every request (O.3), APS filters by set then capability in ADS order, non-conforming APS case walked on all five classes. Q2: n/a (use-case) |
| UC-16 | use-case | partial | 5.c | Annex P.6, L8498-8512: "Supports `custom`; D1, D3 or D4 / device passes; window passes; contained / the custom overlay at `65,8,25,20`" (L8502); L8504: "D2 / fails: image surface / fails: image surface / nothing: candidate skipped, primary content continues" | Custom-supporting and non-supporting Players, containment check, outside-region rectangle and D5 skip all match. D2 does not say what UC-16 says: the coverage table (04-use-cases.md:94) gives D2 "same" as D1 (custom overlay inside the region), the spec skips D2 because it chose image creatives. UC-16 never states the overlay form, so context must fix either the form or the D2 cell. See A-24. Q2: n/a (use-case) |

## Disposition of findings

### 5.a Actionable TODOs (3)

| # | Finding ref | Criterion | Spec section | Concrete edit | Citation |
|----|-------------|-----------|--------------|---------------|----------|
| T2 | A-26, R5.1 | 6 (contradicted row) / 3 (two spec sites, §4.1 matches context) | §4.4 item 5; Annex Q.2.3 S-4; C.4 | Delete the sentence *"The options it emits keep the order the decision gave them."* (L736-737). In S-4 (L8609) replace the input/pass/fail with a check on the document alone: input *"A resolution document with a multi-option candidate"*, pass *"Options in preference order (§5.3.4)"*, fail *"An option list the Player cannot read as ordered: reported"*, or delete S-4. In C.4 L4531-4532 replace *"and the options inside each candidate follow the order the decision gave them (§4.4, item 5)"* with *"and the options inside each candidate are in preference order (§5.3.4)"*. | R5.1 (*"Conformance is checked against the APS's resolution document"*); spec §4.1 L610-614 |
| T3 | A-27, DP-1#p1, DP-1.1#p2 | 1 (DP violation cited by ID) | §5.3.1; §5.3.3; §5.2.1; §5.10 schema; A.3 | §5.3.1 L2245 `@layout` Required cell: *"yes on a non-linear candidate; absent on a List MPD Period, whose family fixes it to `linear`"*. Schema L3121: drop `use="required"` and add the rule to the same prose that already governs `@duration`. §5.3.3 L2325: row reads *"A List MPD Period (linear) / none: the attribute is absent, and the option is `linear`"*. §5.2.1 L1848: *"each with `@form` `image` or `html`"* (drop *"each with `@layout="linear"`"*). A.3 L3868: remove `layout="linear"` from the `<svta:RenderableAsset>`. Overlay-candidate occurrences are untouched. | DP-1, DP-1.1 (03-requirements.md L21-36) |
| T1 | A-25, DP-2#p1, DP-2#p4, R1.4, R2.1, R2.2, R2.3, R11.2, R29.3, R29.4, R29.5, R4#p1, R4.1, R4.2, R4.3, R4.4, R4.5, R4.6, R4.9, R4.10, R4.11, R31.1, R31.2, R12.2, R12.3, R5#p1, R5#p2, R5#p3, R5.2, R5.3, R5.6, R5.7, R7#p1, R7#p2, R7.1, R7.4, R7.5, R30.1, R30.2, R3.2, R3.3, R16.1, R16.2, R32.2, R32.3, R34.2, R34.3, R35.3, R35.4, R35.5, R35.6, R36.2, R36.3, R36.4, R36.5, R36.6, R37.2, R38.2, R38.4, R38.5, R39.3, R39.4, R39.5, R19#p1, R19.1, R19.2, R19.3, R19.4, R21.1, R25#p1, R25.1, R26.1, R26.2, R26.3, R27.1, R27.2, R27.3, R14.1, R14.2, R17.1, R17.2, R17.3, R17.5, R20.1, R20.2, R20.3, R20.4, R20.5, R22.1, R6#p2, R6.4, R6.5, R6.6, R13.1, R13.2, R13.3, R24#p1, R24#p2, R24.1, R33.2, R33.4, R28.1, R28.2, OOS-4#p1 | 1 (DP-2 cited) / 5 (force-lost rows) | L7-10; §4.1 L603-605; §4.2–§4.5 and every other site cited by a `force-lost` row above | (a) Replace §4.1 L604-605 *"The obligations are stated positively — what the actor does — and what lies outside an obligation is outside the contract."* with *"Each obligation is stated positively, with its RFC 2119 keyword; what lies outside an obligation is outside the contract."* (b) At each location a `force-lost` row of the map cites, restate the indicative verb with the modal `context/` gives that unit — *"The Player renders …"* becomes *"The Player MUST render …"*; a `MUST NOT` of `context/` becomes the positive MUST of the same bound where DP-2's form allows it, else `MUST NOT`. No other wording changes; substance, numbering and anchors stay. R1#p2 and R1.1 are excluded (5.c, A-1). | DP-2 (03-requirements.md L44-56, *"the normative modal stays"*); RFC 2119 as declared at spec L7-10 |

T1 is one TODO over many sites: it is one convention applied uniformly, the
sites are the ones the map already quotes, and no edit removes an anchor
another TODO targets. T2 and T3 touch sites T1 does not rewrite (L736-737 is
a sentence T2 deletes, not an obligation T1 restates). Apply T2 and T3 first,
then T1.

### 5.b Flagged for review (4)

| # | Finding ref | Spec section | Why uncertain | Resolutions considered |
|----|-------------|--------------|---------------|------------------------|
| B1 | EC-2 | §4.5.6 items 4, 6; §4.5.10 item 6 | Answer derivable from the base counter, but writing it for linear/overlay is authoring a new sentence, not fixing one. | (a) *"A window is consumed when an ad of its slot begins rendering"*, all families; (b) linear/overlay consumed on execution per the base counter. |
| B2 | A-28, R11.3 | §2 L235-236; §6.6 | §6.6 is also the R11.4 coverage statement; two defensible fixes. | (a) Flag the §6.6 table as illustrative; (b) reword §2 so §6.6 is the normative coverage statement and not a field mapping. |
| B3 | A-29, DP-2#p2 | §4.5.16 L1117-1119 | The positive restatement has more than one form. | (a) *"the primary content continues from the position it had, with its tracking and controls as before"*; (b) keep the list as a definition of a term, not an obligation. |
| B4 | A-30, R28.3 | Annex Q.2.3 S-10 L8615; §4.4 item 9 | Same pattern as T2 but the test also checks carrier shape, which is in scope. | (a) Recast S-10 to check only that a present `<svta:Click>` is well-formed; (b) drop the ClickThrough clause from S-10. |

### 5.c Deferred to context/ (27)

Ordered by leverage; the first five are the ones to take first.

| # | Finding ref | `context/` file to edit | Suggested edit | Leverage rationale |
|----|-------------|-------------------------|----------------|--------------------|
| C1 | EC-1 | 03-requirements.md R4.1 / R4.10 | Say whether the cap rule applies to every `ReplacePresentation`/`InsertPresentation` or only to ad slots, and how the Player tells them apart if the latter. | A blackout without `@maxDuration` plays the programme it should hide: a rights failure, not a missed sale. |
| C2 | A-12, R35.8 | 03-requirements.md R35.8; 06-naming-and-namespaces.md | Pick a reading: the `PT0S` schema default counts as a declaration (R35.1 never applies on linear) or only a written `@skipAfter` counts. Align 06. | Decides whether every linear slot is dismissible; the spec and 06 currently disagree. |
| C3 | A-11 | 03-requirements.md R34.2 | *"… present pause ads in at most one pause for that window …; within that pause the slot plays out as declared (R32)."* | Annex E and §4.5.10 already disagree in the spec; either rebuild reproduces one of them. |
| C4 | A-15 | 03-requirements.md R36.6 | *"When a re-resolution carries no candidate …; one whose candidates are all unrenderable is handled as any other resolution (R5.6)."* | Two spec sites disagree; the answer turns into a 5.a edit at L803. |
| C5 | A-19, UC-07 | 04-use-cases.md UC-07 | State that a current Player executes the standard break too, or add a requirement for a mechanism that lets it skip the fallback. | The only `contradicted` use case. |
| C6 | A-1, R1#p2, R1.1 | 03-requirements.md R1, R1.1 | Recast as a document criterion on where constructs sit (A-1 wording). | Removes two permanent `force-lost` rows no spec edit can close. |
| C7 | A-3, DP-1.2#p1 | 03-requirements.md DP-1.2 | Name the pre-fetch duration of a video option as an admitted exception, sub-MPD canonical. | Removes a permanent `contradicted` row. |
| C8 | G-1, R1.2 | 08-dash-extension-rules.md; R1.2 | Admit request-level hooks (a token in a base attribute with a drop rule; query parameters), or scope R1.2 to MPD constructs. | R29 requires query parameters that R1.2 does not admit. |
| C9 | A-5, R11#p2 | 03-requirements.md R11 | *"No obligation of this specification depends on the ADS's decision format or its version."* | Makes an unverifiable APS obligation checkable. |
| C10 | A-8, R15.2 | 03-requirements.md R15.2 | Name the Publisher construct, or drop *"and forms declared by the Publisher"*. | Removes a dead clause. |
| C11 | A-20, UC-08 | 04-use-cases.md UC-08 L884-886 | Delete the reuse-signal clause. | Already raised in context-audit-ciego.md and still present. |
| C12 | A-24, UC-16 | 04-use-cases.md UC-16 | State the overlay form; align the D2 cell. | |
| C13 | A-31 | 03-requirements.md | Give a modal to the nine indicative obligations (R1.5, R18.1, R29.8, R4.7, R12.4, R34.4, R37.3, R38.3, R17.4). | Their force is uncheckable today. |
| C14 | A-4 | 03-requirements.md R1.3 | *"… restricting which documents conform (R4.8) is not an alteration."* | |
| C15 | A-2 | 03-requirements.md R2.2 | *"… and on the APS none beyond R38.4 and R39."* | |
| C16 | A-6 | 03-requirements.md R31.1 | *"… MUST hold a resolution usable under R36.5, requesting one at that moment if it holds none."* | |
| C17 | A-7 | 03-requirements.md R4.9 | Round each converted duration before the sum. | |
| C18 | A-9 | 03-requirements.md R12.4 | Except R39's custom region. | |
| C19 | A-10 | 03-requirements.md R7.2 | *"A candidate skipped under R5.3 is not a violation of the order R7.1 requires."* | |
| C20 | A-13 | 04-use-cases.md UC-05, UC-08 | Add D5 to the re-tasking note, or exclude it. | |
| C21 | A-14 | 03-requirements.md R36.4 | Absence means the window's length; declare only when shorter. | |
| C22 | A-16 | 03-requirements.md R14.2 | Restrict to overlay candidates. | |
| C23 | A-17 | 03-requirements.md R26, R26.1 | Carrier on the option, emitted by the APS; drop the Publisher from the actor, or define its role. | |
| C24 | A-18 | 05-dash-linear-interfaces.md L444 | One statement: optional element, or none. | |
| C25 | A-21 | 04-use-cases.md UC-03, UC-10 | Name both double-box tokens and the D2 outcome of each. | |
| C26 | A-22, A-23 | 04-use-cases.md UC-04, UC-12 | UC-04: drop or define the L-shape over a takeover. UC-12: align with R20.1. | |
| C27 | EC-3, EC-4, EC-5, EC-6, EC-7, EC-8 | 03-requirements.md R4.2, R35, R36.5, R19, R6/R13, R17.3 | EC-3: declared or actual length in the cumulative sum. EC-4: whether a base per-ad skip survives R35's slot granularity. EC-5: usability of a held resolution after firing. EC-6: speed changes and speed ≤ 0 during an ad. EC-7: per-option schedules, or schedules relative to the option's duration. EC-8: R17.3 in terms of the resume position. | Each is silent in `context/`; the spec cannot choose without a requirement. |

### 5.d Routing notes

- Every row of the map whose verdict is not `met` or `governance` appears in
  exactly one table above: 101 `force-lost` + DP-2#p1 + DP-2#p4 + R5.1 +
  DP-1#p1 + DP-1.1#p2 in 5.a; DP-2#p2, R11.3, R28.3 in 5.b; R1#p2, R1.1, R1.2,
  R11#p2, R15.2, DP-1.2#p1, R35.8, UC-07, UC-08, UC-16 in 5.c.
- Force-lost rows whose criterion is also ambiguous in `context/` (R31.1 /
  A-6, R4.9 / A-7, R34.2 / A-11, R36.4 / A-14, R36.6 / A-15, R14.2 / A-16,
  R26.1 / A-17) stay in T1: the modal is missing whichever reading `context/`
  settles on. The ambiguity travels separately in 5.c.
- No DASH conformance audit item and no detail-review flag is routed: neither
  v10 sidecar existed when this step ran.

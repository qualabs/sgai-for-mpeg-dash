[GROUNDED_BY=spec-only]

# Spec validation — v11 (2026-09-26)

This document uses RFC 2119 vocabulary only where it quotes `context/` or the
spec.

Built against:

- spec: `../output/v11-sgai-spec.md` (7126 lines, chapters 1–8, Annexes A–R)
- `../context/` at git SHA: `f9c76f1` (last commit touching `context/`; HEAD is
  `a732edf`; `git status --short context/` empty)
- `../context-analysis/`: the working tree carries uncommitted edits to
  `conformance-assertions.md`, `dash-gap-analysis.md`, `error-semantics.md`,
  `iab-ad-templates.md`, `uc-coverage-matrix.md`; read as they stand on disk
- population: `bin/check-promotable.py --population`, 211 units (164
  criteria, 30 prose obligations, 17 use cases), walked by exactly those ids
- the base standard was not consulted. Claims the spec makes about it are
  taken as the spec states them; where a finding depends on a base fact it is
  tagged `[inferred]`
- `v11-dash-conformance-audit.md` and `v11-detail-review.md` did not exist in
  `output-analysis/` when this step ran (`ls output-analysis | grep v11` empty),
  so §5 routes no audit item and no detail-review flag

## Summary

| Verdict | Rows |
|---|---|
| `met` | 206 |
| `force-lost` | 0 |
| `contradicted` | 1 |
| `partial` | 4 |
| `gap` | 0 |
| `governance` | 0 |

**The v11 chapter 4 carries its modals.** Every `context/` MUST the walk
visited arrives in chapter 4 as a numbered criterion with its keyword
(`PUB-n`, `ADS-n`, `APS-n`, `PLY-n`, `DOC-n`). Every `MUST NOT` in the spec
(`grep -n 'MUST NOT\|MUST NEVER\|SHALL NOT'`, 61 lines, two of them the BCP 14 boilerplate at L7 and L589) traces to a `context/` prohibition or to
`context/06-naming-and-namespaces.md` L44 (PUB-8), so DP-2 holds and no row is
`force-lost`.

**The one `contradicted` row is DP-1.2#p1.** `<svta:Ad>@duration` and the
video sub-MPD's `Period@duration` are two declarations of one value, and the
spec reconciles them by the base Linked-Period rule (keep the smaller) rather
than deriving one from the other (§5.3.1 L2216). DP-1.2 admits that rule only
for the base's own pair. The remedy needs a `context/` decision (A-5, 5.c).

**Three spec-internal defects have a unique fix** (T1–T3): §4.7.3 and §4.7.4
name the window schemes `urn:mpeg:dash:sgai-*` where every other site and
`context/06` L30-31 say `urn:svta:dash:sgai-*`; test R-PUB-5 says "`on-top`
only on pause windows", the inverse of §5.1.6; two cross-references carry a
`DASH` prefix on this document's own sections.

**UC-14 is `met`, not `gap`.** `validate-spec.prompt` §4.1 makes a UC-14 `gap`
this step's acceptance test, because UC-14 was added after the newest spec was
generated. That premise is false for v11: §7.14 (L3231-3255) and Annex N
(L6239-6437) walk UC-14, and N.6 gives all five device classes plus the legacy
Player. The four use-case rows that are not `met` or that carry notes (UC-08,
UC-12, UC-16) are the evidence that the use cases were walked.

**The pause cap is the largest open question** (G-1). `context/` requires a
cap on every pause window (R4.1), says it bounds nothing there (R4 prose,
R31.2), and computes every cap on a timeline a pause does not advance (R4.11).
The spec gives it a meaning of its own — one pass through a document's
candidates — and lists it as open (§8.13 item 8).

## Gaps (3)

### G-1 — What the required cap of a pause window bounds

- **Spec section:** §4.5.4 table L939 and PLY-24 L941-944 ("one pass of a pause
  resolution document"); §5.1.4 L1988; §5.2.6 L2199 ("Each pass is bounded by
  the window's cap"); §8.13 item 8 L3503-3504; R-PLY-17 L6987.
- **What `context/` is missing:** R4.1 requires a maximum on every pause slot;
  R4 prose (03-requirements L381-383) and R31.2 (L495-499) say the cap bounds
  neither an end nor a cumulative duration on a pause slot; R4.11 (L467-473)
  computes the cap on the presentation timeline, which "a pause does not
  advance". Read together, the declaration is required and inert.
- **What an implementer does today:** follows the spec's per-pass reading, or
  treats `@durationCap` on a pause window as a mandatory attribute with no
  effect. Under the second reading `repeat` is unbounded per pass. Both are
  defensible from `context/`. See EC-1 for the timeline half.

### G-2 — Points the spec declares open are not recorded as open in `context/`

- **Spec section:** §8.13 L3474-3506 lists nine open questions (Advanced
  Linear profile; supersede timing; the timeline an `on-top` window's cap
  accrues on; a live pause beyond the time-shift buffer; precedence between the
  two base skip controls; a pause window inside an alternative presentation;
  pause-window applicability during a linear ad; the pause cap; the empty List
  MPD shape).
- **What `context/` is missing:** the "Deliberately open" table of
  03-requirements (L2299-2306) is empty and states that "no silence in this
  specification has been declared deliberate yet".
- **What an implementer does today:** reads §8.13 as the spec's answer
  ("Where the specification needed an answer to be implementable, it gives
  one"), with no record in `context/` that the owner chose any of them.

### G-3 — A standalone resolution document is not among the admissible extension points

- **Spec section:** §4.7.6 L1674-1695 (C4, `<svta:OverlayList>`), §4.8.2
  L1770.
- **What `context/` is missing:** R1.2 (L141-154) requires every new construct
  to be expressed through foreign-namespace open content, application-level
  Event Streams or descriptor schemes. The non-linear resolution document is a
  new root element outside any MPD; none of the three describes it. The spec
  classifies it as carrier (a) and argues it is "reached only through a
  window's `@uri`, which only a Player of this specification resolves".
- **What an implementer does today:** accepts the spec's argument. The
  question is whether R1.2 governs only constructs inside MPDs; `context/`
  does not say.

## Edge cases (1)

### EC-1 — Which timeline runs while a pause ad is on screen

- **Trigger:** a pause ad with a non-zero `@dismissAfter`, tracking beacons
  after time 0, or a `repeat` document whose per-pass cap must be reached.
- **Why it matters:** §5.2.4 L2152-2153 measures the dismissal delay "on the
  presentation timeline of the slot, like the cap (PLY-31)"; §5.5.2 L2409-2410
  says beacon times "stop accruing while the presentation timeline does not
  advance"; PLY-31 L970-973 does the same for the cap. During a pause the
  primary presentation timeline does not advance (R4.11). If "presentation
  timeline" is the primary one, a pause ad's beacons never fire, its dismissal
  never becomes available, and a pass never ends. Annex H.7 L5279 fires the
  pause ad's beacons at wall clock 10 s and 40 s while media time is frozen at
  5:10, and Annex E.7 treats a pass as 50 s of pause, so the annexes read the
  candidate's own timeline (PLY-82 L1272-1275 "that candidate's own
  presentation").
- **Responsible actor:** the Player. `context/` is silent: R35.2 measures "from
  the moment the slot begins rendering" and names no timeline; R4.11 names the
  presentation timeline for the cap.

## Ambiguities (15)

### A-1 — R26.1: "composition attribute of the slot / layout"

- **Context:** 03-requirements L1390-1392.
- **Readings:** (a) an attribute of the Publisher's slot declaration; (b) an
  attribute of the layout as carried by the option that names it.
- **Spec assumed (b):** APS-13 L780-782, "a composition attribute of the option
  (`@background`, §5.3.6)"; §5.3.6 L2300. R26 prose makes the background the
  advertiser's creative, which the Publisher cannot supply.
- **Tighter sentence:** "The APS MUST carry the background image as an
  attribute of the option whose layout is `squeezeback-double-box-background`,
  and not as a separate presentation option."

### A-2 — R17.5 against R40.4 for a pause window with no relation

- **Context:** R17.5 L1567-1574; R40.4 L1830-1835.
- **Readings:** (a) any pause window whose span contains the pause preempts a
  linear ad (R17.5 as written); (b) only a window applicable to the
  presentation being output does, because a window with the default relation
  presents only over its own presentation's content (R40.4).
- **Spec assumed (b):** PLY-55 L1124-1131 defines "applicable" as a window in
  the linear ad's own MPD or an `on-top` window of the triggering
  presentation; §8.13 item 7 lists it as open.
- **Tighter sentence (R17.5):** "When a viewer pause begins inside a pause
  opportunity window that applies to the linear ad under R40 …".

### A-3 — R40.1: supersede on a pause window

- **Context:** R40.1 L1815-1817 admits supersede or on top on any non-linear
  window.
- **Spec:** §5.1.6 L2017-2021 and the schema's `OnTopOnlyType` L2692-2696 admit
  only `on-top` on a pause window, because whether a pause window presents an
  ad is unknown at the linear event's presentation time.
- **Readings:** (a) R40.1 grants the Publisher supersede on pause windows; (b)
  supersede is meaningless there and the spec may withhold it.
- **Tighter sentence (R40.1):** "… supersede or on top; a pause window declares
  only on top."

### A-4 — R40.4: "the window presents nothing further"

- **Context:** R40.4 L1833-1835.
- **Readings:** (a) once an alternative presentation begins inside the span,
  the window presents nothing more, whether or not a form was on screen; (b)
  only a window whose form was cut stops; one with nothing on screen resumes
  over the primary content after the alternative presentation.
- **Spec assumed (b):** Annex D.8 L4386-4390, "the window, whose span starts at
  the break, presents over the programme after the break for what remains of
  the span (PLY-49)".
- **Tighter sentence:** state whether the rest of the span is presented after
  the alternative presentation ends, in both cases.

### A-5 — DP-1.2 against `<svta:Ad>@duration` (DP-1.2#p1)

- **Context:** DP-1.2 L37-48.
- **Spec:** §5.3.1 L2216, `@duration` is "the canonical value for the slot
  arithmetic; for a video option, the Player reconciles it with the sub-MPD's
  `Period@duration` by keeping the smaller of the two, as the base does for a
  Linked Period". DOC-6 L1348-1350 then claims every other value "has exactly
  one canonical declaration, and the others are derived from it".
- **Readings:** (a) the pair is a duplication DP-1.2 forbids; (b) it is the
  base rule applied by analogy, which DP-1.2 admits only for the base's own
  pair. The sub-MPD must carry `Period@duration` (SPS), and drop-before-play
  (R7.3) and image or HTML forms need the declared duration before any
  sub-MPD is fetched, so neither declaration can simply go.
- **Tighter sentence (DP-1.2):** name this pair as a second admitted
  exception, or say which one is derived.

### A-6 — R15.2: "forms declared by the Publisher"

- **Context:** R15.2 L638-645.
- **Spec:** PUB-17 L695-696 restates it, but no construct of the spec lets a
  Publisher declare a form; the Publisher declares layouts.
- **Readings:** (a) an obligation on a construct that does not exist; (b) a
  reference to `@allowedLayouts`, which carries no media type.
- **Tighter sentence:** drop the Publisher clause from R15.2, or name the
  construct.

### A-7 — UC-08: "unless the Publisher's MPD signals that the overlay candidate doubles as the pause-ad candidate"

- **Context:** 04-use-cases L895-899.
- **Spec:** no construct carries such a signal; §7.8 and Annex H always resolve
  the pause window separately. No requirement defines the signal either.
- **Tighter sentence:** delete the clause from UC-08, or add the requirement.

### A-8 — UC-16: the overlay form is unstated

- **Context:** UC-16 L1716-1746 and its coverage row L94 ("same" for D2).
- **Spec:** Annex P uses image options; P.6 L6685 has D2 skip, which the
  coverage row contradicts. A video `custom` overlay would render on D2.
- **Tighter sentence:** name the form in UC-16 and align the D2 cell.

### A-9 — UC-12: "An attempt that produces no ad is a failed execution, whatever its shape"

- **Context:** 04-use-cases L1355-1360 against R20.1's last paragraph
  (03-requirements L1658-1664): a document with candidates none of which is
  renderable is not a failed execution.
- **Spec assumed R20.1:** §7.12 path 4 L3181-3183, PLY-41 L1042-1045, Annex L.7.
- **Tighter sentence:** "… whatever its shape, except a document carrying
  candidates (R20.1)".

### A-10 — The window scheme URIs, two ways (spec-internal)

- **Sites:** §4.7.3 L1608 `@schemeIdUri="urn:mpeg:dash:sgai-overlay:2026"`;
  §4.7.4 L1636 `@schemeIdUri="urn:mpeg:dash:sgai-pause-trigger:2026"`. Against
  §2.1 L286-287, §5.1 L1908-1909, §5.1.3 L1945, §5.1.4 L1976, every annex MPD
  (21 occurrences of `urn:svta:dash:sgai-overlay:2026`) and `context/06` L30-31.
- **The reading that matches `context/`:** `urn:svta:dash:`. The other also
  mints a URN in MPEG's namespace. See Actionable TODO T1.

### A-11 — Test R-PUB-5: "`on-top` only on pause windows" (spec-internal)

- **Site:** Annex R.2.1 L6935.
- **Against:** §5.1.6 L2017 ("On a pause window, `@linearRelation` takes only
  the value `on-top`"), PUB-11 L666-669 and Annex D.2 L4227, where an overlay
  window declares `on-top`. The test inverts the rule and would fail Annex D's
  own document. See Actionable TODO T2.

### A-12 — `DASH` prefix on this document's own sections (spec-internal)

- **Sites:** §2.1 L285, "Defined in" column: "DASH §5" (this document's §5; the
  other rows cite §5.1.3, §5.1.4, §5.8.1); Annex R.2.5 L7026, "DASH §2, §6.6"
  (this document's chapter 2, where the VAST reference is). See Actionable TODO
  T3.
- **§1.3 L156** "(DASH §4.8.9)": this document has no §4.8.9 and the `@noJump`
  exclusion is in §4.8.4. Whether the base has a §4.8.9 on this point was not
  checked `[inferred]`, so this site is flagged (5.b) rather than fixed.

### A-13 — `overlay-lower-third` "across the bottom 30% of the frame"

- **Site:** §3.4.2 L497.
- **Against:** R12.4 (L612-619) and §3.4.2 L521-525: IAB bounds are inherited
  by reference, not re-declared. `context/` gives numbers for the squeezeback
  tokens and names "Corner Overlay no more than 25%" and "L-Shape primary
  content 60%" as examples; it states no lower-third figure. The 30% is an
  unsourced claim about the IAB guidelines.
- **Readings:** (a) a restatement of an IAB bound, which needs its source; (b)
  a definition of the token, which R12.4 forbids.

### A-14 — `@skipAfter` precedence and the `ServiceDescription` skip control

- **Context:** R35.8 L1063-1071 names "the base specification's own skip
  declaration" in the singular.
- **Spec:** §5.2.4 L2155-2175 orders `@skipAfter` on the event before
  `PlaybackRestrictions@skipAfter`, and says the order "is this
  specification's: the base states no precedence between its two skip
  controls"; §8.13 item 5 lists it as open.
- **Tighter sentence (R35.8):** name which base declarations count, and their
  order when both are written.

### A-15 — Criteria with no RFC 2119 keyword

22 criteria of `context/03-requirements.md` carry no RFC 2119 keyword (script
over the criterion bullets; the same script finds the keyword in R4.1, so it
reads them): R1.5, R18.1, R18.2, R29.1, R29.7, R29.8, R4.7, R4.8, R12.4, R32.4,
R34.4, R35.7, R36.7, R37.3, R38.3, R38.6, R17.4, R40.8, R13.5, R33.3, R28.3,
R10.3.

- **Obligations written in the indicative:** R1.5 ("takes precedence … adopts
  it and cites it"), R18.1 ("documents"), R12.4 ("inherits these bounds"),
  R34.4 ("is recorded as such"), R38.3 ("is normative and defined by this
  specification"), R17.4 ("carries no construct"), R37.3 ("states no
  requirement"), R29.8 ("the Player is required to send them"), R4.7 ("means
  the opportunity does not fire"), R40.8 ("is a recorded exception").
- **Scope declarations or definitions:** R18.2, R29.1, R29.7, R4.8, R32.4,
  R35.7, R36.7, R38.6, R13.5, R33.3, R28.3, R10.3.

Question 2 of the map is recorded as `source-has-no-modal` for all 22.

## Obligation coverage map

One row per unit of `bin/check-promotable.py --population`, in its order.
`Kind` says which of the two questions apply (prompt §4.2); the Q2 answer is
in `Notes`. Line numbers are of `../output/v11-sgai-spec.md`.

| Unit | Kind | Verdict | Disposition | Evidence — quoted passage and location | Notes |
|------|------|---------|-------------|----------------------------------------|-------|
| DP-1#p1 | document | met | — | DOC-36 L1487-1489: "A construct MUST NOT carry information already determined by its element name and namespace, by its parent, or by another attribute of the same construct"; §5.3.2 L2243-2244: "The form is not a separate attribute: `@mimeType` determines it" | The one duplicated value found is scored under DP-1.2#p1. |
| DP-1.1#p1 | document | met | — | DOC-36 L1489-1490: "A construct MUST NOT be introduced in case a future edition relaxes something" | |
| DP-1.1#p2 | document | met | — | DOC-36 L1490-1491: "a construct whose only admissible value matches its default, or is fixed by another rule, MUST NOT exist"; §4.8.2 L1766 (`@durationCap` exists because its default differs from `@maxDuration`'s) | `<svta:Tracking>@value="1"` is the base `EventStreamType`'s attribute with the base's value (Table 47), not a construct of this spec. |
| DP-1.2#p1 | document | contradicted | 5.c | §5.3.1 L2216: "The canonical value for the slot arithmetic; for a video option, the Player reconciles it with the sub-MPD's `Period@duration` by keeping the smaller of the two, as the base does for a Linked Period" | Two declarations reconciled by min, not one derived from the other; DP-1.2 admits that only for the base pair (A-5). |
| DP-2#p1 | document | met | — | DOC-37 L1492-1494: "Where this specification states an obligation of its own, it states the positive obligation"; §1.4 L222-225 | |
| DP-2#p2 | document | met | — | DOC-37 L1493-1494: "prohibitions the requirements it implements state are kept as prohibitions"; every `MUST NOT` in the spec traces to `context/` (grep, 61 lines) | |
| DP-2#p3 | document | met | — | PLY-58 L1143-1145: "the Player MUST cease firing the tracking beacons scheduled for the dismissed pause ad" | R16.2's wording, not the negative form DP-2 rejects. |
| DP-2#p4 | document | met | — | PLY-77 L1238-1239: "The Player MUST fire the tracking events the resolution document scheduled up to the moment of the dismissal" | |
| DP-3#p1 | document | met | — | §4.1 L611-614: "Applying this specification MUST NEVER break primary-content playback. When an opportunity cannot be honoured, the Player skips it and continues"; DOC-38 L1495-1496 | |
| R1#p1 | document | met | — | §1.4 L187-188: "This specification **extends** the base specification and alters nothing in it"; DOC-3 L1328-1329 | |
| R1#p2 | document | met | — | DOC-1 L1313-1317: "Every construct this specification introduces MUST sit at an extension point where removing it … leaves a valid MPD whose primary content plays uninterrupted" | Stated as a document property, as R1 now asks. |
| R1.1 | document | met | — | DOC-1 L1313-1317 (above); §4.7.3–§4.7.7 per construct | |
| R1.2 | document | met | — | DOC-2 L1318-1327: "Every new construct MUST be expressed through foreign-namespace open content …, an application-level Event Stream …, or a descriptor scheme … New constructs MUST NOT be introduced by a path that violates the chain"; PUB-14 L681-687 | Standalone resolution document: G-3. |
| R1.3 | document | met | — | DOC-3 L1328-1331: "This specification MUST NOT alter or override the semantics of any construct of the base specification"; PUB-15 L688-689 | The one departure is recorded (§4.8.3). |
| R1.4 | runtime | met | — | PLY-86 L1291-1294: "the Player MUST abort that ad and continue playing the primary content uninterrupted" | Q2: yes. |
| R1.5 | document | met | — | DOC-4 L1332-1338: "the base answer takes precedence: this specification adopts it and cites it (§4.8.1) … A decision that departs from the base answer anyway is recorded with its reason (§4.8.3)" | Q2: source-has-no-modal. |
| R2.1 | runtime | met | — | PUB-1 L620-623: "The Publisher MUST declare the constraints applicable to an ad slot … in the MPD. They are not inferred at runtime" | Q2: yes. |
| R2.2 | runtime | met | — | ADS-2 L716-717: "The ADS MUST decide which ads to serve and output them as its decision document"; APS-1 L734-735: "The APS MUST convert the ADS's decision into the resolution document" | Q2: yes. |
| R2.3 | runtime | met | — | PLY-1 L832-834: "The Player MUST validate the candidates of a resolution document against the constraints the Publisher declared, and render only those that satisfy them" | Q2: yes. |
| R2.4 | document | met | — | DOC-5 L1339-1343: "Every mechanism this specification introduces MUST be expressible within the four-actor contract" | |
| R11#p1 | document | met | — | DOC-7 L1354-1355: "This specification MUST NOT depend on any version of VAST or on VAST as a protocol" | |
| R11#p2 | runtime | met | — | DOC-7 L1356: "Conformant implementations MUST be VAST-version-agnostic" | Q2: yes. |
| R11#p3 | document | met | — | DOC-7 L1355-1356: "and MUST NOT impose VAST as a precondition for any actor" | |
| R11.1 | document | met | — | DOC-8 L1357-1358; §2 L276-279: VAST 4.x listed under "Informative references … No normative clause of this document requires VAST or any VAST version" | |
| R11.2 | runtime | met | — | PLY-2 L836-837: "The Player MUST be able to operate regardless of whether the ADS uses VAST: it reads only the resolution document" | Q2: yes. |
| R11.3 | document | met | — | DOC-9 L1359-1363; §1.2 L103: "typically VAST, though it is not bound to VAST"; §6.6 heading L2953 "(informative)" | |
| R11.4 | document | met | — | DOC-10 L1364-1367; §6.6 table L2962-2977 | |
| R11.5 | document | met | — | DOC-11 L1368-1370; Annex A.7 L3713-3789, C.8 L4135-4184 | |
| R18.1 | document | met | — | DOC-12 L1374-1376: "This specification documents the Player-visible interface: the MPD event URL (served by the APS), the resolution request (§5.8), and the resolution document (§5.2)" | Q2: source-has-no-modal. |
| R18.2 | scope | met | — | §1.3 L118-121: "The request the APS sends to the ADS … are agreed between those parties, outside this specification"; DOC-12 L1378-1379 | Q2: source-has-no-modal. |
| R29.1 | document | met | — | DOC-13 L1380-1382: "The capability parameters are **inputs about the device** … and not conclusions about which ad experiences can be served"; §5.8.2 L2516-2528 | Q2: source-has-no-modal. |
| R29.2 | runtime | met | — | PLY-12 L872-875: "Sending a capability parameter is OPTIONAL. A Player MAY send all of them, some of them, or none" | Q2: yes. |
| R29.3 | runtime | met | — | PLY-13 L876-878: "the Player MUST omit that parameter entirely rather than send it with an empty or placeholder value" | Q2: yes. |
| R29.4 | runtime | met | — | PLY-14 L879-881: "MUST carry a vendor-specific prefix (§5.8.4)" | Q2: yes. |
| R29.5 | runtime | met | — | APS-15 L787-789: "The APS MUST tolerate the absence of any capability parameter, and MUST be able to produce ad candidates without receiving any of them" | Q2: yes. |
| R29.6 | document | met | — | DOC-13 L1382-1384: "The set MUST be able to express the capability axes that distinguish the device classes"; §5.8.2 L2532-2540: "No two rows are equal" | |
| R29.7 | document | met | — | DOC-14 L1385-1389: "Absence does not assert that the device lacks the capability" | Q2: source-has-no-modal. |
| R29.8 | document | met | — | DOC-15 L1390-1393: "The forwarded allowed layouts and the forwarded custom region are the exceptions to the optionality of PLY-12" | Q2: source-has-no-modal. |
| R4#p1 | runtime | met | — | PLY-24 L941-944: "the Player MUST stop rendering once the cumulative duration … would exceed it, even if the stop falls mid-ad" | Q2: yes. |
| R4.1 | runtime | met | — | PUB-2 L624-626: "The Publisher MUST declare a cap (`@durationCap`, §5.1.3) on every overlay window and every pause window. On an inherited linear event the cap is the base specification's `@maxDuration`, which the Publisher MAY omit" | Q2: yes. What the pause cap bounds: G-1. |
| R4.2 | runtime | met | — | PLY-24 L941-944 (above) | Q2: yes. Adds one pass of a pause document (G-1). |
| R4.3 | runtime | met | — | PLY-25 L945-949: "The Player MUST NOT extend a slot beyond what the cap bounds for that slot's family" | Q2: yes. |
| R4.4 | runtime | met | — | ADS-1 L713-715: "A conformance check on the ADS MUST NOT fail solely because the cumulative duration of its returned candidates exceeds the cap" | Q2: yes. |
| R4.5 | runtime | met | — | PLY-26 L950-952: "the Player MUST enforce the cap against actual length, not declared length" | Q2: yes. |
| R4.6 | runtime | met | — | PLY-27 L953-956: "the Player MUST honour the base clip semantics" | Q2: yes. |
| R4.7 | runtime | met | — | PUB-3 L631-635: "A declared cap of zero means the opportunity does not fire"; PLY-30 L969 | Q2: source-has-no-modal. |
| R4.8 | document | met | — | PUB-2 L626-630: "an absent `@maxDuration` keeps its base meaning"; PLY-29 L966-968: "An inherited linear event with no `@maxDuration` is outside this criterion" | Q2: source-has-no-modal. |
| R4.9 | runtime | met | — | PLY-28 L957-962: "MUST round the converted value **up** … A candidate whose converted duration equals the cap exactly is admitted" | Q2: yes. |
| R4.10 | runtime | met | — | PLY-29 L963-966: "The Player MUST NOT present ads from such a window and MUST continue with the primary content" | Q2: yes. |
| R4.11 | runtime | met | — | PLY-31 L970-973: "The Player MUST compute the cap on the presentation timeline. An interval during which the presentation timeline does not advance MUST NOT accrue against the cap" | Q2: yes. Timeline of a pause ad: EC-1. |
| R31.1 | runtime | met | — | PLY-11 L867-869: "The Player MUST request a resolution document when a viewer pause begins inside a pause window, and MUST NOT request one for a pause that begins outside every such window" | Q2: yes. |
| R31.2 | runtime | met | — | PLY-32 L974-978: "The Publisher-declared cap MUST NOT be interpreted as bounding the duration of a pause slot" | Q2: yes. The per-pass bound the spec adds: G-1. |
| R12.1 | document | met | — | DOC-17 L1400-1403: "This specification MUST NOT accept a value outside that enumeration, and MUST cite the IAB source"; §3.4.1 L474-483 | |
| R12.2 | runtime | met | — | PUB-4 L636-638: "MUST use only the tokens of §3.4.2. Publisher-private layout names MUST NOT appear" | Q2: yes. |
| R12.3 | runtime | met | — | APS-8 L763-764: "The APS MUST NOT emit form metadata for an ad type or visual placement outside the tokens of §3.4.2" | Q2: yes. |
| R12.4 | document | met | — | §3.4.2 L521-525: "Each token implies the spatial bound the IAB guidelines declare … introduces no dimensional attribute on the slot declaration"; DOC-18 L1404-1406 | Q2: source-has-no-modal. Lower-third 30%: A-13. |
| R15.1 | document | met | — | §3.5 L546-547: "The admissible creative carriers are **exactly three**, and no annex, example or implementation note of this document adds another"; DOC-19 L1407-1409 | |
| R15.2 | runtime | met | — | APS-10 L768-769; PUB-17 L695-696: "Forms the Publisher declares MUST carry a creative whose media type falls under one of the three forms" | Q2: yes. Publisher clause has no construct: A-6. |
| R15.3 | runtime | met | — | PLY-5 L844-846: "The Player MAY skip a candidate whose creative media type is outside §3.5" | Q2: yes (MAY). |
| R5#p1 | runtime | met | — | PLY-17 L892-894: "render the **first** option whose form and layout it can satisfy on its device" | Q2: yes. |
| R5#p2 | runtime | met | — | PLY-20 L905-908: "the Player MUST skip that candidate and fall through to the next candidate" | Q2: yes. |
| R5#p3 | runtime | met | — | PLY-18 L895-900: "The Player MUST resolve option selection by walking the options in document order and checking each against (a) its device's capabilities and (b) the layouts the window admits" | Q2: yes. |
| R5.1 | runtime | met | — | APS-5 L748-751: "Each ad candidate MUST carry one or more presentation options … as an ordered list, where document order is the preference order" | Q2: yes. |
| R5.2 | runtime | met | — | PLY-17 L892-894 (above) | Q2: yes. |
| R5.3 | runtime | met | — | PLY-20 L905-908: "when the candidates are exhausted, the Player MUST continue with the primary content" | Q2: yes. |
| R5.4 | document | met | — | ADS-3 L720-723; APS-7 L758-762: "This specification MUST NOT be read as obliging the APS to maintain a device-class matrix" | |
| R5.5 | runtime | met | — | APS-6 L752-755: "An ad candidate MAY carry multiple presentation options … their document order is the preference order the Player follows" | Q2: yes (MAY). |
| R5.6 | runtime | met | — | PLY-18 L895-900: "an option that fails either MUST NOT be rendered, and the Player moves to the next option" | Q2: yes. |
| R5.7 | runtime | met | — | PLY-20 L905-908 (above) | Q2: yes. |
| R7#p1 | runtime | met | — | PLY-33 L987-989: "the Player MUST play the candidates in the order the resolution document declares" | Q2: yes. |
| R7#p2 | runtime | met | — | PLY-36 L995-996: "The Player MUST NOT re-order, deduplicate, or otherwise rearrange the remaining candidates" | Q2: yes. |
| R7.1 | runtime | met | — | PLY-33 L987-989 (above) | Q2: yes. |
| R7.2 | runtime | met | — | PLY-34 L990-991: "The Player MAY drop a candidate that has no form renderable on its device" | Q2: yes (MAY). |
| R7.3 | runtime | met | — | PLY-35 L992-994: "The Player MAY drop a candidate before playback ("drop before play")" | Q2: yes (MAY). |
| R7.4 | runtime | met | — | PLY-36 L995-996 (above) | Q2: yes. |
| R7.5 | runtime | met | — | PLY-37 L997-999: "the Player MUST trim it mid-rendering ("trim during play")" | Q2: yes. |
| R30.1 | runtime | met | — | APS-4 L745-747: "MUST be expressed as a resolution document carrying no candidates (§5.2.3), and MUST NOT be expressed as an error response or as a response without a body" | Q2: yes. |
| R30.2 | runtime | met | — | PLY-44 L1056-1061: "A resolution carrying no candidates MUST NOT count as an execution of the opportunity" | Q2: yes. |
| R3.1 | document | met | — | DOC-20 L1410-1412; §3.6 L562-568; chapter 7 per-class tables | |
| R3.2 | runtime | met | — | PLY-3 L838-841: "A Player on any device class MUST produce a defined behaviour — render, fall back, or skip" | Q2: yes. |
| R3.3 | runtime | met | — | PLY-4 L842-843: "The Player MUST NOT attempt to render a form … that its device class cannot render" | Q2: yes. |
| R16.1 | runtime | met | — | PLY-57 L1141-1142: "the Player MUST remove any rendered pause ad from the screen within one rendering frame" | Q2: yes. |
| R16.2 | runtime | met | — | PLY-58 L1143-1145: "the Player MUST cease firing the tracking beacons scheduled for the dismissed pause ad" | Q2: yes. |
| R32.1 | runtime | met | — | APS-22 L824-826: "A resolution document for a pause window MUST declare which exhaustion behaviour applies"; PLY-65 L1182-1183: "Absent the declaration, the Player MUST apply `stop`" | Q2: yes. |
| R32.2 | runtime | met | — | PLY-66 L1185-1186: "Under `request-again`, a resolution document carrying no candidates MUST be treated as `stop`" | Q2: yes. |
| R32.3 | runtime | met | — | PLY-60 L1150-1151: "the Player MUST return to the primary content immediately, whether or not an ad is mid-presentation" | Q2: yes. |
| R32.4 | scope | met | — | §4.5.11 L1188-1189: "Whether a second resolution request within one pause is the same opportunity or a new one is out of scope"; §1.3 L175-176 | Q2: source-has-no-modal. |
| R34.1 | runtime | met | — | PUB-10 L663-665: "The Publisher MAY declare a pause window as once-per-session (`@executeOnce="true"`)" | Q2: yes (MAY). |
| R34.2 | runtime | met | — | PLY-63 L1167-1170: "the Player MUST present at most one pause ad for that window for the duration of the session" | Q2: yes. |
| R34.3 | runtime | met | — | PLY-64 L1171-1173: "The Player MUST treat such a window as consumed when a pause ad **begins rendering**" | Q2: yes. |
| R34.4 | document | met | — | PLY-64 L1173-1176: "This is the base specification's counter rule … restated for a trigger that is the viewer"; §4.8.1 L1754 | Q2: source-has-no-modal. |
| R35.1 | runtime | met | — | APS-19 L812-815: "The APS MUST declare, for each slot it resolves, whether the viewer may dismiss it" | Q2: yes. |
| R35.2 | runtime | met | — | APS-20 L816-819: "the APS MUST declare the number of seconds that MUST elapse, from the moment the slot begins rendering" | Q2: yes. Timeline during a pause: EC-1. |
| R35.3 | runtime | met | — | PLY-74 L1228-1230: "the Player MUST NOT offer the viewer a way to dismiss the slot. After it has, the Player MUST make dismissal available" | Q2: yes. |
| R35.4 | runtime | met | — | PLY-75 L1231-1233: "The Player MUST stop presenting every ad of that slot" | Q2: yes. |
| R35.5 | runtime | met | — | PLY-76 L1234-1237: "the Player MUST continue from where the primary content stands, and MUST NOT compress or skip any part of it" | Q2: yes. |
| R35.6 | runtime | met | — | PLY-77 L1238-1241 | Q2: yes. |
| R35.7 | scope | met | — | L1251-1252: "How the dismissal is offered — a control, a gesture, a remote button — is out of scope"; §1.3 L173-174 | Q2: source-has-no-modal. |
| R35.8 | runtime | met | — | PLY-78 L1242-1245: "the Player MUST honour that declaration as the base specification defines it, and it governs the slot" | Q2: yes. Which base declarations count: A-14. |
| R36.1 | runtime | met | — | PUB-9 L657-662: "A window that declares nothing may be resolved up to 60 seconds ahead" | Q2: yes (MAY). |
| R36.2 | runtime | met | — | PLY-6 L850-852: "On an overlay window, the Player MUST NOT resolve earlier than the offset" | Q2: yes. |
| R36.3 | runtime | met | — | PLY-7 L853-856: "The offset is computed against the start of the window and never against the pause" | Q2: yes. |
| R36.4 | runtime | met | — | APS-21 L820-823: "the APS MUST declare how long that resolution remains usable (`@validFor`, §5.2.5)" | Q2: yes. |
| R36.5 | runtime | met | — | PLY-9 L860-863: "the Player MUST check whether the resolution it holds is still usable … MUST NOT present candidates from the expired resolution" | Q2: yes. |
| R36.6 | runtime | met | — | PLY-10 L864-866: "MUST treat it as a resolution carrying no candidates and MUST NOT fall back on the expired one" | Q2: yes. |
| R36.7 | document | met | — | PLY-8 L857-859: "Resolving early is a permission and never an obligation" | Q2: source-has-no-modal. |
| R37.1 | runtime | met | — | PLY-56 L1137-1140: "A Player MAY implement a pause by any mechanism that suspends the primary content and later resumes it" | Q2: yes (MAY). |
| R37.2 | runtime | met | — | PLY-59 L1146-1149: "the Player MUST continue the primary content from the position at which it was suspended" | Q2: yes. |
| R37.3 | document | met | — | PLY-56 L1137-1140; §5.3.7 L2325 and L2334-2343 treat decoder release as the Player's choice | Q2: source-has-no-modal. |
| R38.1 | runtime | met | — | PUB-5 L639-641: "A window that declares none admits the family default of §3.4.3"; §3.4.3 L537-539: "does **not** include `linear` … and it does not include `custom`" | Q2: yes (OPTIONAL). |
| R38.2 | runtime | met | — | PLY-15 L882-885: "the Player MUST send the declared set, unchanged, on the resolution request" | Q2: yes. |
| R38.3 | document | met | — | §5.8.3 L2544-2547 (`sgai-allowed-layouts`); DOC-15 L1393-1394: "The way they travel is normative and defined in §5.8.3" | Q2: source-has-no-modal. |
| R38.4 | runtime | met | — | APS-9 L765-767: "The APS MUST NOT return an option whose layout is outside the set of allowed layouts it received" | Q2: yes. |
| R38.5 | runtime | met | — | PLY-19 L901-904: "the Player MUST check that the option it selects uses a layout the window admits, and MUST NOT render it otherwise" | Q2: yes. |
| R38.6 | scope | met | — | DOC-16 L1395-1396: "Inherited linear events carry no allowed-layouts declaration, and the forwarding of PLY-15 does not apply to them" | Q2: source-has-no-modal. |
| R39.1 | document | met | — | DOC-21 L1413-1415: "Supporting `custom` is OPTIONAL for every actor … it applies only to overlay windows" | |
| R39.2 | runtime | met | — | PUB-6 L642-645: "It MAY also declare a custom region on the window" | Q2: yes (MAY). |
| R39.3 | runtime | met | — | PLY-16 L886-888: "the Player MUST send it on the resolution request together with the allowed layouts" | Q2: yes. |
| R39.4 | runtime | met | — | APS-12 L775-779: "MUST carry the overlay's rectangle … and that rectangle MUST lie entirely inside the region" | Q2: yes. |
| R39.5 | runtime | met | — | PLY-21 L909-913: "the Player MUST check that its rectangle lies inside the window's custom region … and MUST NOT render it otherwise" | Q2: yes. |
| R19#p1 | runtime | met | — | PLY-67 L1197-1199: "The Player MUST render every ad form, linear or non-linear, at the same playback speed as the primary content" | Q2: yes. |
| R19.1 | runtime | met | — | PLY-67 L1197-1199 (above) | Q2: yes. |
| R19.2 | runtime | met | — | PLY-68 L1200-1201: "The Player MUST NOT force an ad to 1x" | Q2: yes. |
| R19.3 | runtime | met | — | PLY-69 L1202-1205: "The Player MUST compute a form's wall-clock on-screen duration as `duration / playback_speed`" | Q2: yes. |
| R19.4 | runtime | met | — | PLY-70 L1206-1209: "The Player MUST derive the wall-clock length of such a form as `duration / playback_speed`" | Q2: yes. |
| R21.1 | runtime | met | — | PLY-61 L1152-1160: "The Player MAY present a pause ad fullscreen … When it is partial, the Player MUST keep at most one non-linear form active during the pause" | Q2: yes. |
| R25#p1 | runtime | met | — | PLY-62 L1161-1164: "the Player MUST keep its presentation time frozen inside that window for the full duration of the pause" | Q2: yes. |
| R25.1 | runtime | met | — | PLY-62 L1161-1166 (above, and "MUST be treated as a Player action occurring after the resume") | Q2: yes. |
| R26.1 | runtime | met | — | APS-13 L780-782: "The background image of a double-box layout MUST be carried as a composition attribute of the option (`@background`, §5.3.6), not as a separate presentation option" | Q2: yes. "Slot / layout" read as the layout on the option: A-1. |
| R26.2 | runtime | met | — | PLY-71 L1213-1216: "the Player MUST place it in the uncovered bands; when it carries none, the uncovered region renders black" | Q2: yes. |
| R26.3 | runtime | met | — | PLY-22 L914-920: "MUST NOT be selected on a single-decoder device … MUST NOT be selected on a device that cannot composite that surface type over video" | Q2: yes. |
| R27.1 | runtime | met | — | APS-14 L783-786: "An L-shape option MUST carry exactly one ad creative — the full-frame background creative" | Q2: yes. |
| R27.2 | runtime | met | — | PLY-72 L1217-1220: "The Player MUST composite the two elements of an L-shape" | Q2: yes. |
| R27.3 | runtime | met | — | PLY-23 L921-927: "an image or HTML full-frame creative MUST NOT be selected on a device that cannot composite that surface type together with video" | Q2: yes. |
| R14.1 | runtime | met | — | PLY-46 L1069-1072: "the Player MUST present them in sequence, in the order they appear in the document, each starting when the previous one ends" | Q2: yes. |
| R14.2 | runtime | met | — | PLY-47 L1074-1076: "The Player MUST enforce the window's cap against the cumulative duration of the sequence" | Q2: yes. |
| R14.3 | document | met | — | DOC-23 L1426-1429: "This specification MUST NOT introduce a construct that implies or requires the simultaneous rendering of two or more non-linear forms" | |
| R17.1 | runtime | met | — | PLY-52 L1116-1118: "the Player MUST render the pause ad and MUST suspend the overlay's rendering" | Q2: yes. |
| R17.2 | runtime | met | — | PLY-53 L1120-1121: "the Player MUST dismiss the pause ad and MUST restore the overlay if the overlay window is still active" | Q2: yes. |
| R17.3 | runtime | met | — | PLY-54 L1122-1123: "the Player MUST keep the overlay surface clear on resume" | Q2: yes. |
| R17.4 | document | met | — | L1133: "No construct lets the Publisher, the ADS or the APS invert this priority"; DOC-24 L1430-1432 | Q2: source-has-no-modal. |
| R17.5 | runtime | partial | 5.c | PLY-55 L1124-1131: "When a viewer pause begins inside a pause window applicable to the presentation being output while a linear ad occupies the screen, the Player MUST present the pause ad … A pause window is applicable to a linear ad when it is declared in that ad's own MPD (PLY-51) or when it is a window of the triggering presentation that declares `on-top`" | Q2: yes for the part carried. A primary-MPD pause window with no relation is excluded, which R17.5 as written includes (A-2). |
| R20.1 | runtime | met | — | PLY-38 L1008-1012; PLY-39 L1019-1033: "The Player MUST treat the four ways an attempt can fail alike … the Player MUST continue with the primary content uninterrupted" | Q2: yes. |
| R20.2 | runtime | met | — | PUB-7 L646-647: "All opportunity windows of one family that share a `Period` MUST be authored as `Event` entries inside a **single** `EventStream`" | Q2: yes. |
| R20.3 | runtime | met | — | PLY-40 L1034-1037: "The Player MUST order overlapping windows of one family by presentation time, oldest first … the Player MUST take them in the order in which they appear" | Q2: yes. |
| R20.4 | runtime | met | — | PLY-42 L1046-1050: "The Player MUST treat it as a failed execution, MUST NOT present any of its candidates in the slot" | Q2: yes. |
| R20.5 | runtime | met | — | PLY-43 L1051-1055: "The Player MUST bind the candidates each window of a fallback chain serves with **that window's own** declarations … The Player MUST NOT apply the declarations of the window it stands in for" | Q2: yes. |
| R20.6 | document | met | — | DOC-25 L1433-1435: "MUST be carried as a normative Player obligation, not only in informative material; it is"; PLY-43 is in normative chapter 4 | |
| R22.1 | runtime | met | — | PLY-45 L1065-1067: "the Player MUST keep at most **one** non-linear ad form active on the screen" | Q2: yes. |
| R40.1 | runtime | partial | 5.c | PUB-11 L666-669: "Declaring a relation on a non-linear window is OPTIONAL. A window declares at most one relation, supersede or on top"; §5.1.6 L2017: "On a **pause window**, `@linearRelation` takes only the value `on-top`" | Q2: yes. Supersede on a pause window, which R40.1 admits, is withheld (A-3). |
| R40.2 | runtime | met | — | PUB-12 L670-673: "MUST declare it either by a window in that alternative presentation's own MPD, or by a window of the triggering presentation that declares `on-top`" | Q2: yes. |
| R40.3 | runtime | met | — | PLY-48 L1093-1099: "the Player MUST present the window and MUST NOT execute the inherited linear events … the Player MUST execute those events as the base specification defines" | Q2: yes. |
| R40.4 | runtime | met | — | PLY-49 L1100-1104: "the Player MUST present its forms only while the content of the presentation whose MPD declares the window is being output, and MUST execute every inherited linear event it overlaps" | Q2: yes. "Nothing further": A-4. |
| R40.5 | runtime | met | — | PLY-50 L1105-1108: "the Player MUST present it also while an alternative presentation that starts within its span is active" | Q2: yes. |
| R40.6 | runtime | met | — | PLY-51 L1109-1112: "The Player MUST process the non-linear windows declared in an alternative presentation's MPD as that presentation's own" | Q2: yes. |
| R40.7 | document | met | — | DOC-26 L1436-1440: "This specification MUST NOT add anything to the inherited linear events, or to their `EventStream`s, to carry it" | |
| R40.8 | document | met | — | §4.8.3 L1789-1796: "A superseded linear event is not executed while its window presents an ad (PLY-48) … The departure is declared explicitly by the Publisher" | Q2: source-has-no-modal. |
| R6#p1 | document | met | — | DOC-28 L1448-1449: "This specification MUST specify how in-band ad tracking beacons are carried"; §5.5 | |
| R6#p2 | runtime | met | — | PLY-83 L1276-1278: "A Player MUST safely ignore unknown namespaces on tracking-related extension elements" | Q2: yes. |
| R6.1 | document | met | — | DOC-28 L1448-1449 (above); §5.5.1, §5.5.2 | |
| R6.2 | runtime | met | — | APS-16 L797-800: "The APS SHOULD carry tracking beacons as `Event` entries of an event stream of scheme `urn:mpeg:dash:event:callback:2015`" | Q2: yes (SHOULD). |
| R6.3 | document | met | — | DOC-29 L1454-1456: "A new tracking carrier MAY be introduced only when the callback scheme cannot express the required semantics … none is introduced" | |
| R6.4 | runtime | met | — | PLY-83 L1276-1278 (above) | Q2: yes. |
| R6.5 | runtime | met | — | PLY-81 L1262-1271: "two beacons carrying the same `@id` in two different candidates are two distinct beacons that the Player MUST fire both. On a List MPD the base scope applies unchanged" | Q2: yes. |
| R6.6 | runtime | met | — | PLY-82 L1272-1275: "The Player MUST resolve the presentation times of an `<svta:Tracking>` element against **that candidate's own presentation**" | Q2: yes. |
| R6.7 | document | met | — | DOC-30 L1457-1460; §5.10.2 L2810-2830: "A report that does not state that the schema of §5.10.1 was loaded is not a report of validity" | |
| R13#p1 | document | met | — | DOC-28 L1449-1451: "and MUST define a mechanism that lets the ADS direct which beacons fire and at which points" | |
| R13.1 | runtime | met | — | APS-16 L795-797: "the APS MUST express them as DASH callback events (§5.5), with timings relative to the ad's presentation timeline" | Q2: yes. |
| R13.2 | runtime | met | — | PLY-79 L1256-1258: "the Player MUST execute the tracking schedule it reads from the resolution document" | Q2: yes. |
| R13.3 | runtime | met | — | PLY-80 L1260-1261: "the Player MUST stop firing the remaining beacons at the trim boundary" | Q2: yes. |
| R13.4 | document | met | — | DOC-29 L1453-1454: "This specification MUST NOT introduce a new tracking event scheme" | |
| R13.5 | scope | met | — | §1.3 L122-127: "So are the fidelity of the tracking transcription (that the APS neither adds, removes nor reorders the beacons the ADS declared)" | Q2: source-has-no-modal. |
| R23.1 | document | met | — | DOC-32 L1465-1468; §5.7 L2457-2459: "Emitting it is optional for the APS and reading it is optional for the Player" | |
| R24#p1 | runtime | met | — | APS-11 L770-772: "the asset URL MUST NOT be expressed as `@mimeType` on an `AdaptationSet` or `Representation` reached through any path bound by IETF RFC 4337" | Q2: yes. |
| R24#p2 | runtime | met | — | APS-11 L772-774: "It MUST be carried as foreign-namespace content (§5.3)" | Q2: yes. |
| R24.1 | runtime | met | — | APS-11 L770-774 (above) | Q2: yes. |
| R33.1 | document | met | — | DOC-33 L1469-1471: "This specification MUST NOT define a metric of its own for pause-ad delivery"; §5.9 L2618 | |
| R33.2 | runtime | met | — | PLY-88 L1302-1304: "MUST derive the paused interval from the `PlayList` entries … and MUST NOT count a playback period that stopped on `Rebuffering`" | Q2: yes. |
| R33.3 | scope | met | — | DOC-33 L1471-1473; §5.9 L2618-2620: "how a measurement reaches anyone is out of scope" | Q2: source-has-no-modal. |
| R33.4 | runtime | met | — | PUB-13 L674-675: "Content carrying pause windows MUST request the `PlayList` metric through the base specification's `Metrics` element" | Q2: yes. |
| R28#p1 | runtime | met | — | APS-17 L803-806: "the ClickThrough URL and any click-tracking URL accompanying it MUST be carried in `<svta:ClickThrough>` (§5.6)"; DOC-31 L1461-1464 | Q2: yes. |
| R28.1 | runtime | met | — | APS-17 L803-806 (above, "and not elsewhere") | Q2: yes. |
| R28.2 | runtime | met | — | PLY-84 L1282-1284: "A Player conformant to this specification MUST read the ClickThrough URL … and fire its associated click-tracking when the viewer activates the ClickThrough" | Q2: yes. |
| R28.3 | scope | met | — | §1.3 L124-127: "and whether a ClickThrough the ADS declared reaches the resolution document at all" | Q2: source-has-no-modal. |
| R8.1 | document | met | — | DOC-34 L1477-1478; §4.8.2 L1762-1782 | |
| R8.2 | document | met | — | DOC-34 L1479-1480; §4.8.4 L1813-1850 | |
| R9.1 | document | met | — | DOC-35 L1481-1482; §4.8.1 L1744-1758 | |
| R9.2 | document | met | — | DOC-35 L1482-1484: "A new construct MUST NOT be introduced unless an existing one cannot be made to fit" | |
| R9.3 | document | met | — | DOC-35 L1484-1486; §4.8.2 column "Why no base construct could be reused, or extended" | |
| R10.1 | document | met | — | DOC-22 L1419-1420: "Spatial arrangement of overlays MUST be delegated to HTML5 / CSS layout primitives" | |
| R10.2 | document | met | — | DOC-22 L1420-1421: "this specification MUST NOT define a parallel layout standard for overlay placement" | |
| R10.3 | scope | met | — | §1.3 L130-136: "no position vocabulary inside a layout (left, right, top, bottom) … The one exception is the optional `custom` overlay layout" | Q2: source-has-no-modal. |
| OOS-1#p1 | document | met | — | §1.3 L130-132: "This specification defines no parallel layout standard"; DOC-22 | |
| OOS-4#p1 | runtime | met | — | §1.3 L137-140: "A sender that needs a scripted creative MUST wrap the script inside an HTML document and carry it as `text/html`" | Q2: yes. |
| UC-01 | use-case | met | — | §7.2 L2992-3007: "D1, D2 … Plays the first renderable candidate on one decoder … D3, D4, D5 … The same on its single decoder"; Annex A.6 L3702-3711 | All five classes; linear-only, bounded. |
| UC-02 | use-case | met | — | §7.2 L2992-3007; Annex B.5-B.8 L3904-3950, incl. B.7 trick-play at 2x | All five classes; trick-play variant walked. |
| UC-03 | use-case | met | — | §7.4 L3026-3032 table D1-D5: "D2 … a double box with a video ad and no background is renderable if admitted … D5 … Declines"; Annex C.6 L4106-4118 | All five classes as the UC states. |
| UC-04 | use-case | met | — | §7.6 L3054-3060 table D1-D5: "D3 … Composites an image or HTML overlay on top: the linear ad holds the one decoder the primary content released"; Annex D.7 L4363-4375 | All five classes; `on-top` declared as UC-04 requires. |
| UC-05 | use-case | met | — | §7.7 L3078-3084 table D1-D5: "D3 … MAY instead release the primary content's decoder to play a video option (PLY-56)"; Annex E.6 L4525-4533; live variant E.10 L4581-4636 | All five classes; live freeze walked. |
| UC-06 | use-case | met | — | §7.3 L3014-3018: "On every class the Player plays the candidates back to back in document order, reusing its decoder (D3 to D5) or pre-buffering the next ad on the second one (D1, D2)"; Annex F.5-F.7 | All five classes; cap cut mid-ad (F.5). |
| UC-07 | use-case | met | — | §7.16 L3274-3288: "Live content, or on-demand content with no fallback authored — the primary content plays uninterrupted … On-demand content with a standard linear break authored under a superseding window — the legacy Player plays the break"; Annex G.10 L5100-5104 "D1 to D5" | Uniform across classes; live/VOD split and supersede as UC-07 states. |
| UC-08 | use-case | partial | 5.c | §7.8 L3107-3113 table D1-D5; Annex H.7-H.9 L5273-5306 | All five classes walked as the UC states. The UC's alternative ad response (overlay candidate doubling as pause candidate) has no construct (A-7). |
| UC-09 | use-case | met | — | §7.9 L3131-3137: D1 renders 1, D2 4, D3 2, D4 2, D5 4; Annex I.6 L5471-5479 | Matches UC-09 per class. |
| UC-10 | use-case | met | — | §7.10 L3151-3157 table D1-D5; Annex J.7 L5624-5637 | D2 declines on the background element type; D3 image/HTML, D4 image only, D5 declines. |
| UC-11 | use-case | met | — | §7.11 L3161-3166: "every class opens the ClickThrough destination (or hands it off) and fires each click-tracking URL once"; Annex K.5-K.7 | D1-D5 identical; legacy inert. |
| UC-12 | use-case | met | — | §7.12 L3168-3187: paths 1-3 as the UC lists; "The chain selects the window and is device-agnostic"; Annex L.4, L.8 | Path 4 follows R20.1 against the UC's "whatever its shape" (A-9). |
| UC-13 | use-case | met | — | Annex M.3 L6029-6035 (D3 omits the HTML axis, D4 declares nothing), M.4 L6044-6050, M.7 L6213-6219 "Same as Annex I: yes" for D1-D5 | All five classes as the UC states. |
| UC-14 | use-case | met | — | §7.14 L3241-3248 table D1-D5 plus Legacy; Annex N.6 L6406-6413; primary-timeline window variants §7.14 L3250-3254 and N.7 L6424-6437 | Walked; the prompt's premise that the build predates UC-14 does not hold for v11. |
| UC-15 | use-case | met | — | §7.15 L3259-3266: "D1, D3 and D4 render an image L-shape; D2 and D5 have no renderable allowed layout and skip"; Annex O.5-O.7 | Non-conforming APS case walked (O.7). |
| UC-16 | use-case | partial | 5.c | §7.15 L3268-3272; Annex P.6 L6681-6685: "D2, D5 … neither image option renders; skips" | The UC's coverage row has D2 render the custom overlay; the form is unstated in the UC (A-8). |
| UC-17 | use-case | met | — | §7.13 L3219-3229 table D1-D5 plus Legacy; Annex Q.5 L6872-6879; failure shapes Q.6 L6884-6899 | Matches UC-17 per class, incl. late execution. |

## Disposition of findings

### 5.a Actionable TODOs (3)

| #  | Finding ref | Criterion | Spec section | Concrete edit | Citation |
|----|-------------|-----------|--------------|---------------|----------|
| T1 | A-10 | 3 | §4.7.3 item 1 L1608; §4.7.4 item 1 L1636 | L1608: replace `urn:mpeg:dash:sgai-overlay:2026` with `urn:svta:dash:sgai-overlay:2026`; L1636: replace `urn:mpeg:dash:sgai-pause-trigger:2026` with `urn:svta:dash:sgai-pause-trigger:2026` | `context/06-naming-and-namespaces.md` L25-31 (pattern `urn:svta:dash:<construct>:<year>`, the two URIs named); R1.2 |
| T2 | A-11 | 3 | Annex R.2.1, R-PUB-5 L6935 | Pass cell: replace "at most one `@linearRelation` per window, `on-top` only on pause windows" with "at most one `@linearRelation` per window; on a pause window only `on-top`" | R40.1 (03-requirements L1815-1817); spec §5.1.6 L2017 |
| T3 | A-12 | 4 | §2.1 L285; Annex R.2.5 L7026 | L285 "Defined in" cell: "DASH §5" → "§5"; L7026 "Where" cell: "DASH §2, §6.6, Annexes A.7, C.8" → "§2, §6.6, Annexes A.7, C.8" | R11.1 (L215-216) for L7026's reference; the spec's own reference convention L18-20 ("a bare `§n` … refers to this document") |

### 5.b Flagged for review (3)

| #  | Finding ref | Spec section | Why uncertain | Resolutions considered |
|----|-------------|--------------|---------------|------------------------|
| f-1 | EC-1 | §5.2.4 L2152-2153; §5.5.2 L2409-2410; PLY-31; Annex H.7 L5279 | Three sites name "the presentation timeline", which is frozen during a pause; the annexes run a pause ad on its own timeline | Define the timeline of a slot as the candidate's own presentation (PLY-82) for dismissal, beacons and the per-pass cap; or measure pause-ad dismissal on the wall clock |
| f-2 | A-12 (L156) | §1.3 L156 | Whether the base has a clause 4.8.9 on this point was not checked `[inferred]` | Replace "(DASH §4.8.9)" with "(§4.8.4)"; or keep it if it is a base clause and quote it |
| f-3 | A-13 | §3.4.2 L497 | "Bottom 30%" is an IAB bound restated without a source in `context/`; R12.4 inherits bounds by reference | Drop the figure and keep "across the bottom of the frame"; or cite the IAB section that states it |

### 5.c Deferred to context/ (12)

Ordered by leverage.

| #  | Finding ref | `context/` file to edit | Suggested edit | Leverage rationale |
|----|-------------|-------------------------|----------------|--------------------|
| d-1 | G-1 | 03-requirements.md (R4.1, R4 prose, R31.2, R4.11) | Say what a pause window's cap bounds, or stop requiring one on pause windows | A mandatory attribute whose meaning the spec had to invent; decides whether `repeat` is bounded |
| d-2 | DP-1.2#p1, A-5 | 03-requirements.md (DP-1.2) | Admit `<svta:Ad>@duration` and the video sub-MPD's `Period@duration` as a reconciled pair under the base rule, or say which is derived | The only `contradicted` row; a design principle the spec cannot satisfy together with R7.3 and SPS |
| d-3 | G-2 | 03-requirements.md ("Deliberately open") | Decide, or record as deliberately open, the nine questions of spec §8.13 | The spec declares open what `context/` never opened |
| d-4 | R17.5, A-2 | 03-requirements.md (R17.5) | Restrict R17.5 to pause windows that apply to the linear ad under R40 | Keeps R17.5 `partial`; R17.5 and R40.4 read two ways |
| d-5 | R40.1, A-3 | 03-requirements.md (R40.1) | State that a pause window declares only on top | Keeps R40.1 `partial` |
| d-6 | A-4 | 03-requirements.md (R40.4) | Say whether the rest of the span is presented after the alternative presentation ends | Two readings of "presents nothing further" |
| d-7 | G-3 | 03-requirements.md (R1.2); 08-dash-extension-rules.md | Say whether a standalone document reached only through a window's `@uri` is admissible, and under which rule | R1.2 enumerates only in-MPD extension points |
| d-8 | A-14 | 03-requirements.md (R35.8) | Name which base skip declarations count, and their order | The spec fixed an order the base does not state |
| d-9 | UC-08, A-7 | 04-use-cases.md (UC-08) | Delete the reuse-signal clause, or add the requirement | Keeps UC-08 `partial` |
| d-10 | UC-16, A-8 | 04-use-cases.md (UC-16, coverage row) | Name the form; align the D2 cell | Keeps UC-16 `partial` |
| d-11 | A-9, A-6, A-1 | 04-use-cases.md (UC-12); 03-requirements.md (R15.2, R26.1) | UC-12: except documents carrying candidates; R15.2: drop the Publisher clause or name the construct; R26.1: "an attribute of the option whose layout …" | Wording; the spec already reads each one way |
| d-12 | A-15 | 03-requirements.md | Give R1.5, R18.1, R12.4, R34.4, R38.3, R17.4, R37.3, R29.8, R4.7, R40.8 their modal | Obligations whose force no validation can check |

### 5.d Routing notes

- T1–T3 are the only findings with a unique byte-level fix. The one
  `contradicted` row (DP-1.2#p1) is not in §5.a: its remedy is not expressed by
  the two quotations, because neither declaration can be removed (A-5).
- EC-1 is 5.b and not 5.c: the timeline wording was added by the spec, not by
  `context/`.
- No row is `force-lost`, so §5.a criterion 5 selected nothing.

### 5.e DASH conformance audit and detail review

`v11-dash-conformance-audit.md` and `v11-detail-review.md` were absent from
`output-analysis/` when this step ran, so no audit item and no detail-review
flag is routed here. A later run of this step, or a manual routing, has to add
them once they exist.

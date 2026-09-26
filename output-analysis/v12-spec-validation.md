[GROUNDED_BY=spec-only]

# Spec validation — v12 (2026-09-26)

Built against:
- spec: `../output/v12-sgai-spec.md` (7313 lines)
- context/ at git SHA: `536351fe77f00cff7ef8290de72a89205c0a4a3a` (HEAD, which is also the last commit touching `context/`; `context/` has no uncommitted changes. `context-analysis/` has five uncommitted modified files, read as they stand on disk.)
- population: `bin/check-promotable.py --population`, 211 units (164 criteria, 30 prose obligations, 17 use cases), walked exactly by id

The key words MUST, MUST NOT, SHOULD and MAY in quotations below are the
spec's and `context/`'s, interpreted per IETF RFC 2119 / RFC 8174.
Line numbers (`L…`) refer to `../output/v12-sgai-spec.md` unless a path
is given. The base standard was not consulted; every claim below is
grounded in the spec and `context/` only.

**One instruction of the prompt was not followed, and why.** §4.1 says a
run that does not report `UC-14` as `gap` has not walked the use cases.
UC-14 is walked in this candidate — §7.14 (L3337-3361) and Annex N, with
D1–D5, the legacy Player and the three primary-timeline relations — so
reporting `gap` would be false. It is reported `met` with its evidence.
The acceptance test in the prompt is stale against `context/` and the build.

## Gaps (4)

### G-1 — What the required cap of a pause window bounds

- **Spec section:** §4.5.4 (L988), PLY-24 (L990-993), PLY-32 (L1033-1037), §5.1.4 `@durationCap` (L2113); self-listed at §8.13 item 9 (L3629-3632): *"the cap required on pause windows bounds one pass through a document's candidates (§4.5.4)."*
- **What the context is missing:** R4.1 requires a cap on every pause slot (`../context/03-requirements.md` L393-395), while R4's prose says *"A **pause** slot has no declared duration for a cap to bound"* (L381-383), R31.2 says on a pause slot it *"bounds neither"* (L495-499), and UC-05 says *"No maximum display duration"* (`../context/04-use-cases.md` L591-592). A mandatory value with no meaning; how it interacts with `@onExhausted="repeat"` is also unstated.
- **What an implementer does today:** follows the spec's "one pass" invention, which appears nowhere in `context/`.
- **Routing:** 5.c (D-1).

### G-2 — The spec's open questions are not recorded as open in `context/`

- **Spec section:** §8.13 (L3588-3661), fourteen numbered questions.
- **What the context is missing:** the "Deliberately open" table of `../context/03-requirements.md` (L2297-2316) is empty, *"and that is a statement: **no silence in this specification has been declared deliberate yet.**"* Every question §8.13 answers provisionally (Advanced Linear profile, supersede timing, on-top cap, live pause beyond the buffer, skip-control precedence, pause window inside an alternative presentation, PLY-55 applicability, supersede on pause windows, the pause cap, the empty List MPD, the standalone document, two linear permissions, the `svta` NID, use-case wording) is therefore an unchosen silence.
- **What an implementer does today:** takes the provisional answers as settled.
- **Routing:** 5.c (D-2).

### G-3 — The standalone non-linear resolution document is not among R1.2's extension points

- **Spec section:** DOC-2 (L1390-1392), §4.7.6 (L1784-1787), §8.13 item 11 (L3644-3646).
- **What the context is missing:** R1.2 (`../context/03-requirements.md` L141-153) enumerates foreign-namespace open content, application Event Streams and descriptor schemes; `<svta:OverlayList>` is none. DR-10 (`../context/08-dash-extension-rules.md`) settles its profile, not its admissibility. The spec reads the enumeration as covering only documents a legacy Player reads, and says so is open.
- **What an implementer does today:** accepts the spec's reading; a literal R1.2 audit rejects the whole non-linear path. Coverage row R1.2 is `partial` for this reason.
- **Routing:** 5.c (D-3).

### G-4 — VAST ad verification and icons have no place in §6.6

- **Spec section:** DOC-10 (L1440-1443), §6.6 (L3055-3080), which claims *"every ad behaviour a VAST-based ADS expresses has a place in the resolution document"* (L3058-3060).
- **What is missing:** `<AdVerifications>` / OMID and `<Icons>` are neither mapped nor declared not carried. A case-insensitive search of the spec for `AdVerification`, `OMID`, `Icons`, `viewab` returns 0 lines (the same search over `../context/05-dash-linear-interfaces.md` finds L516, which excludes VAST verification from the linear baseline only). R11.4 says independence from VAST is *"not a licence to leave uncovered what the deployed ecosystem already does."*
- **What an implementer does today:** an APS fed by VAST drops verification and AdChoices icons silently, or carries them in a proprietary extension.
- **Routing:** 5.b (F-4). Coverage row R11.4 is `partial`.

## Edge cases (5)

### EC-1 — `@validFor="PT0S"` on a document obtained at or after the moment the opportunity fires

- **Trigger:** a document with `validFor="PT0S"` requested when the opportunity fires (it arrives after APS latency), or the second document under `request-again`, requested mid-pause.
- **Why it matters:** §5.2.5 (L2305-2312) measures `@validFor` *"from the moment the Player receives the document"* and says `PT0S` means usable *"only if it arrives when the opportunity fires"*; PLY-9 (L908) checks only at the fire instant. A Player that also checks at presentation finds the document expired on arrival and re-requests or presents nothing; one that checks only at fire time presents it.
- **Responsible actor:** Player. `context/` is silent: R36.4/R36.5 give no starting instant.
- **Routing:** 5.b (F-5).

### EC-2 — `@dismissAfter` across the documents and passes of one pause slot

- **Trigger:** under `request-again` the second pause document declares a different `@dismissAfter`; under `repeat`, a new pass starts.
- **Why it matters:** PLY-75 (L1298-1303) makes the slot *"the rest of that pause"*, PLY-74 (L1293-1297) measures the delay *"from the moment the slot begins rendering"*, and §5.2.4 puts `@dismissAfter` on each `<svta:OverlayList>`. Which declaration governs, and whether the delay restarts per pass, is unstated; a viewer can be offered dismissal and then lose it.
- **Responsible actor:** Player and APS. `context/` is silent (R35.1/R35.2 against R32 `request-again`).
- **Routing:** 5.b (F-6).

### EC-3 — A pause inside a pause window, with an overlay on screen, when no pause ad renders

- **Trigger:** the pause resolution yields no ad (empty, failed, or nothing renderable on the device, e.g. D2 with image/HTML options only).
- **Why it matters:** PLY-52 (L1181-1184) ties suspending the overlay to rendering the pause ad; §7.8 D2 (L3216) has the overlay suspended with no ad (*"else the paused frame stays clean"*). No normative text says whether the overlay stays suspended; two Players differ in what the viewer sees and in overlay beacon accounting.
- **Responsible actor:** Player. `context/` R17.1 (`../context/03-requirements.md` L1562-1565) conditions on presenting the pause ad and is silent on the other case.
- **Routing:** 5.b (F-7).

### EC-4 — Beacon `@id` collisions across the sub-MPDs of one List MPD

- **Trigger:** an APS assembles a List MPD from two ad servers whose sub-MPDs each number callback events from `1`.
- **Why it matters:** after the Linked Period merge the streams share one `@id` scope (PLY-81), and the spec cites the base as ignoring an already-processed event (L2512-2514): the second ad's colliding beacons are not fired and impressions are lost without error. §5.5.1 (L2511-2515) states uniqueness indicatively (*"An APS that assembles a List MPD therefore numbers the beacons of its sub-MPDs uniquely"*) and Annex R (L7145) tests it under APS-16, which carries no such obligation (L841-848).
- **Responsible actor:** APS. `context/` R6.5 (`../context/03-requirements.md` L1919) states the scope and no APS obligation.
- **Routing:** 5.b (F-8).

### EC-5 — A Publisher query parameter using a reserved `sgai-` name

- **Trigger:** the Publisher writes `sgai-allowed-layouts=…` (or another reserved name) into a window's `@uri` query, which §5.8.1 permits (L2611-2613: *"The Player keeps that query unchanged and appends its own parameters to it"*); the Player appends its own, and the APS receives the name twice.
- **Why it matters:** §5.8.4 (L2665) *"The prefix `sgai-` is reserved to this specification"* binds no actor; §4.7.7 (L1802-1803) and §5.8.5 (L2680-2681) claim the names cannot collide, which assumes an unwritten Publisher obligation. A duplicated `sgai-allowed-layouts` makes APS-9's input ambiguous.
- **Responsible actor:** Publisher. `context/` R29.4 constrains only the Player.
- **Routing:** 5.b (F-9).

## Ambiguities (17)

### A-1 — Player-side ranking and deduplication

- **Context passage:** `../context/02-actors.md` L177-180 (*"The Player may apply additional client-side criteria (ranking, ordering, deduplication, simultaneity caps), but it must operate within the validated subset."*) against `../context/03-requirements.md` L748-749 (R7 prose) and L774-776 (R7.4, no re-order or deduplication).
- **Readings:** (a) the Player may rank/deduplicate inside the validated set; (b) it may only drop.
- **Spec assumed:** both — PLY-1 (L882-883) *"Any client-side criterion it adds (ranking, deduplication) operates inside the validated subset."* and PLY-36 (L1054-1055) *"The Player MUST NOT re-order, deduplicate, or otherwise rearrange the remaining candidates"*. Coverage rows R7#p2 and R7.4 are `contradicted`.
- **Tighter context sentence:** in `02-actors.md`: "The Player may drop candidates that fail validation or that it cannot render (R7.2, R7.3); it does not re-order or deduplicate the remaining ones (R7.4)."
- **Routing:** 5.b (F-1) for the spec; 5.c companion (D-4).

### A-2 — Whether R2.2 exempts the APS from Publisher constraints

- **Context passage:** R2.2 (`../context/03-requirements.md` L189-194: *"this specification places no such obligation on the ADS or the APS"*) against R38.4 (L1226-1228) and R39.4 (L1261-1264), which bind the APS to the allowed layouts and the custom region.
- **Readings:** (a) R2.2 is absolute and R38.4/R39.4 contradict it; (b) R2.2 covers constraints the APS is not given on the request.
- **Spec assumed:** (b) — ADS-2 (L761-764) exempts only the ADS; APS-9 (L810) and APS-12 (L821) bind the APS.
- **Tighter context sentence:** R2.2: "…on the ADS, nor on the APS beyond the layouts and region it receives on the resolution request (R38.4, R39.4)."
- **Routing:** 5.c (D-5).

### A-3 — R1.3 has no exception; supersede is recorded against R1.5 only

- **Context passage:** R1.3 (`../context/03-requirements.md` L155-157) against R40.8 (L1865-1873, *"a recorded exception to R1.5"*).
- **Readings:** not executing a base event the base would execute (a) alters base semantics and needs an R1.3 exception, or (b) leaves the event's semantics intact.
- **Spec assumed:** (b), while listing the departure next to DOC-3 (L1400-1403) and in §4.8.3 (L1879-1892).
- **Tighter context sentence:** R40.8: "…and is not an alteration under R1.3: the base event keeps its semantics for every Player that executes it."
- **Routing:** 5.c (D-6).

### A-4 — Whether drop-before-play and the non-renderable List MPD are departures R1.5 must record

- **Context passage:** R1.5 (`../context/03-requirements.md` L165-172) against the drop-before-play permission (L757-772).
- **Readings:** (a) departures needing R40.8-style records; (b) the spec's own answers where the base leaves the Player free.
- **Spec assumed:** neither; §8.13 item 12 (L3647-3653) *"This edition states both as its own rules and has not recorded either as a departure (§4.8.3)."* Coverage row R1.5 is `partial`.
- **Tighter context sentence:** at the drop-before-play criterion and PLY-41's source (R20.1), either "a recorded exception to R1.5: <reason>" or "not a departure: <reason>".
- **Routing:** 5.c (D-7).

### A-5 — "No dimensional attribute on the slot declaration" against `@customRegion`

- **Context passage:** R12.4 (`../context/03-requirements.md` L612-619) against R39.2 (L1254-1256).
- **Readings:** R12.4 absolute (then `@customRegion` breaks it) or scoped to the IAB layouts' bounds.
- **Spec assumed:** the scoped reading, without saying so — DOC-18 (L1480-1482) against `@customRegion` (L2086).
- **Tighter context sentence:** R12.4: "; the `custom` region of R39 is the one exception and is not a spatial bound of an IAB layout."
- **Routing:** 5.c (D-13).

### A-6 — MUST skip (R5.3) and MAY drop (R7.2) for the same candidate

- **Context passage:** R5.3 (`../context/03-requirements.md` L711-714) against R7.2 (L769-770).
- **Readings:** R7.2 as a permission relative to R7.1's order, or a Player that may keep an unrenderable candidate (impossible under PLY-4, L890-891).
- **Spec assumed:** both verbatim — PLY-20 (L954-957), PLY-34 (L1049-1050). No behavioural divergence.
- **Tighter context sentence:** R7.2: "Dropping a candidate R5.3 requires skipping does not breach R7.1."
- **Routing:** 5.c (D-14).

### A-7 — "At most one pause ad" on a once-per-session window

- **Context passage:** R34 gist (`../context/03-requirements.md` L953) and R34.2 (L987-990).
- **Readings:** (a) one ad candidate, cutting a multi-candidate, `repeat` or `request-again` sequence in the first pause; (b) the ads of one qualifying pause.
- **Spec assumed:** neither explicitly — PLY-63 (L1232) copies the criterion; Annex E.10 walks a single-candidate case only.
- **Tighter context sentence:** R34.2: "…present pause ads during at most one qualifying pause inside that window for the session; within that pause the document's candidates and exhaustion behaviour (R32) apply as usual."
- **Routing:** 5.c (D-8).

### A-8 — "Composition attribute of the slot / layout" for the double-box background

- **Context passage:** R26.1 (`../context/03-requirements.md` L1398-1400).
- **Readings:** (a) "slot" = the window in the MPD; (b) "layout" = the layout as carried, which is `@layout` on the option. The forbidden form (a separate option) is avoided under both.
- **Spec assumed:** (b) — APS-13 (L826-828) *"carried as a composition attribute of the option (`@background`, §5.3.6), not as a separate presentation option."* Coverage row R26.1 is `met` on that reading.
- **Tighter context sentence:** "…a composition attribute of the presentation option whose layout is the double box with background…".
- **Routing:** 5.c (D-15).

### A-9 — R17.5 unconditional against R40.4

- **Context passage:** R17.5 (`../context/03-requirements.md` L1575-1583) against R40.4 (L1843-1846).
- **Readings:** (a) any pause window covering the instant fires over a linear ad (contradicts R40.4); (b) only windows R40 makes applicable to the linear presentation.
- **Spec assumed:** (b) — PLY-55 (L1189-1196), self-listed at §8.13 item 7. Coverage row R17.5 is `partial`.
- **Tighter context sentence:** R17.5: "…inside a pause opportunity window that R40 makes applicable to the linear presentation…".
- **Routing:** 5.c (D-9).

### A-10 — Supersede on a pause window

- **Context passage:** R40.1 (`../context/03-requirements.md` L1828-1830), for every non-linear window.
- **Readings:** supersede admissible on pause windows, or meaningless there because presenting depends on an unknown viewer pause.
- **Spec assumed:** the second — §5.1.6 (L2142) *"On a **pause window**, `@linearRelation` takes only the value `on-top`"*, schema `OnTopOnlyType` (L2847); self-listed at §8.13 item 8. Coverage row R40.1 is `partial`.
- **Tighter context sentence:** R40.1: "On a pause window only on top is admissible."
- **Routing:** 5.c (D-10).

### A-11 — Whether `<svta:Tracking>` is a new tracking carrier

- **Context passage:** R6.3 (`../context/03-requirements.md` L1912), R6.6 (L1930), R6.7 (L1935).
- **Readings:** (a) the carrier is the callback-scheme `EventStreamType` content, only hosted under an SVTA name, so none is introduced; (b) a new carrier, whose justification must be R6.3's precondition (the callback scheme cannot express the semantics).
- **Spec assumed:** both — DOC-29 (L1530-1532) *"none is introduced"*; §4.8.2 (L1864) lists `<svta:Tracking>` as introduced, justified by schema placement rather than by R6.3's precondition.
- **Tighter context sentence:** R6.3: "Hosting callback-scheme events in an element of the base `EventStreamType` under the SVTA namespace, where the base schema declares no `EventStream`, is not a new tracking carrier."
- **Routing:** 5.b (F-10); context sentence optional.

### A-12 — UC-01 / UC-02: an image or HTML fallback on a linear candidate

- **Context passage:** `../context/04-use-cases.md` L139-145 and L213-219 (*"optionally with an image or HTML form as a fallback"*).
- **Readings:** the design must carry it, or the phrase is descriptive.
- **Spec assumed:** descriptive — §4.8.4 (L1963-1964) *"image or HTML alternatives for a linear slot are not carried in this edition."* Coverage rows UC-01, UC-02 are `partial`.
- **Tighter context sentence:** "Each candidate is a video form; this edition carries no non-video fallback on a linear candidate."
- **Routing:** 5.c (D-11).

### A-13 — UC-08: the overlay candidate that "doubles as the pause-ad candidate"

- **Context passage:** `../context/04-use-cases.md` L895-899. No requirement names this capability.
- **Spec assumed:** no construct (§8.13 L3657-3658). Coverage row UC-08 is `partial`.
- **Tighter context sentence:** delete the "unless …" clause, or add a requirement carrying it.
- **Routing:** 5.c (D-12).

### A-14 — UC-09, D4: option 3 or option 4

- **Context passage:** `../context/04-use-cases.md` L1126-1128 (*"fallen to option 4"*).
- **Spec assumed:** option 3, the image lower-third, which D4 can render (Annex I.6, L5657). The spec is right and the use case wrong; UC-09 stays `met`.
- **Tighter context sentence:** "landed on option 3, the image banner".
- **Routing:** 5.c (D-16).

### A-15 — UC-12 "whatever its shape" against R20.1

- **Context passage:** `../context/04-use-cases.md` L1355-1356 and coverage cell L84, against R20.1's closing paragraph (*"A resolution document that carries candidates is not a failed execution, whatever the Player then does with them."*).
- **Spec assumed:** R20.1 — §7.12 path 4 (L3287-3289). UC-12 stays `met`.
- **Tighter context sentence:** "produces no ad" → "obtains no resolution document carrying candidates".
- **Routing:** 5.c (D-17).

### A-16 — UC-16 names no overlay form; its D2 cell

- **Context passage:** `../context/04-use-cases.md` L94 (D2 "same" as D1) and L1731-1733 (no form named).
- **Spec assumed:** image forms, so D2 skips (Annex P.6, L6863). Coverage row UC-16 is `partial`.
- **Tighter context sentence:** name the forms in the Ad response and set D2 to "skip (no non-video surface)".
- **Routing:** 5.c (D-18).

### A-17 — 22 criteria carry no RFC 2119 keyword

- **Context passage:** R1.5, R18.1, R18.2, R29.1, R29.7, R29.8, R4.7, R4.8, R12.4, R32.4, R34.4, R35.7, R36.7, R37.3, R38.3, R38.6, R17.4, R40.8, R13.5, R28.3, R33.3, R10.3 in `../context/03-requirements.md`.
- **Readings:** most are scope declarations or document properties; R4.7 (*"A declared cap of zero means the opportunity does not fire"*) and R37.3 are obligations written in the indicative. Question 2 cannot be checked for any of them.
- **Spec assumed:** the spec states each property; coverage rows carry `Q2 source-has-no-modal`.
- **Tighter context sentence:** add the modal to each indicative obligation (at least R4.7, R37.3).
- **Routing:** 5.c (D-19).

## Obligation coverage map

Question 2 (force) is recorded in *Notes*: `Q2 kept` where the source's
modal arrives as a modal, `Q2 n/a` for document-level, scope and use-case
units, `Q2 source-has-no-modal` where the criterion carries no RFC 2119
keyword (A-17). No row is `force-lost`.

Totals: 211 units — 196 `met`, 10 `partial`, 2 `contradicted`,
3 `governance`, 0 `force-lost`, 0 `gap`. Blocking verdicts
(`contradicted`, `gap`, `force-lost`): 2 rows, R7#p2 and R7.4, both 5.b.

| Unit | Kind | Verdict | Disposition | Evidence — quoted passage and location | Notes |
|------|------|---------|-------------|----------------------------------------|-------|
| DP-1#p1 | document | met | — | §4.6 DOC-36, L1563-1565: *"A construct MUST NOT carry information already determined by its element name and namespace, by its parent, or by another attribute of the same construct."* Property holds at §5.3.2 L2367-2368: *"The form is not a separate attribute: `@mimeType` determines it, and a second declaration could only contradict the first."* | Q2 n/a. |
| DP-1.1#p1 | document | met | — | §4.6 DOC-36, L1565-1566: *"A construct MUST NOT be introduced in case a future edition relaxes something"* | Q2 n/a. No speculative construct found in §5.1-§5.3 attribute tables. |
| DP-1.1#p2 | document | met | — | §4.6 DOC-36, L1566-1567: *"a construct whose only admissible value matches its default, or is fixed by another rule, MUST NOT exist."* | Q2 n/a. `@linearRelation` on a pause window admits only `on-top`, which differs from the default (§5.1.6), so it is not a single-value construct. |
| DP-1.2#p1 | document | met | — | §4.6 DOC-6, L1420-1422: *"Every other value this specification needs in two places has exactly one canonical declaration, and the others are derived from it at runtime (§5.2.2, §5.3)."*; §5.3.2 L2356: *"Present if and only if the form is image or HTML. A video option's duration is the `Period@duration` of its sub-MPD, which this attribute does not restate (DOC-6)."* | Q2 n/a. The v11.1 duplication (`@duration` on video options) is gone in v12. |
| DP-2#p1 | document | met | — | §4.6 DOC-37, L1568-1570: *"Where this specification states an obligation of its own, it states the positive obligation; prohibitions the requirements it implements state are kept as prohibitions."* | Q2 n/a. Sampled the chapter-4 MUST NOTs (PUB-8, PLY-6/7/9/10/11, PLY-42, PLY-74..77, PLY-88): each traces to a context MUST NOT, so none is a spec-added prohibition. |
| DP-2#p2 | document | governance | — | — | The keyword appears quoted inside a rationale sentence (*"a long list of 'MUST NOT' items invites confusion"*); it binds no actor. |
| DP-2#p3 | document | governance | — | — | The keyword appears inside DP-2's counter-example (*"instead of saying 'the Player MUST NOT fire tracking beacons after the slot end'"*): illustrative, it binds no actor. |
| DP-2#p4 | document | governance | — | — | The keyword appears inside DP-2's illustrative positive rewrite (*"say 'the Player MUST fire tracking beacons within the slot window'"*). It is an example of wording, and the actual tracking obligations are R6/R13 and R35. |
| DP-3#p1 | document | met | — | §4.1, L644-645: *"Applying this specification MUST NEVER break primary-content playback."*; §4.6 DOC-38, L1571-1572: *"Applying this specification MUST NEVER break primary-content playback."* | Q2 n/a. The v11.1 break (MPD-level `EssentialProperty` for `RequestParam`) is gone: PUB-18 L731-741 requires a `SupplementalProperty` under an allowing profile and otherwise does not use the scheme; C5 (L1791-1806) does not use Annex I.3. |
| R1#p1 | document | met | — | §1.4, L190-191: *"This specification **extends** the base specification and alters nothing in it."*; DOC-3 L1400-1401: *"This specification MUST NOT alter or override the semantics of any construct of the base specification."* | Q2 n/a. |
| R1#p2 | document | met | — | §4.6 DOC-1, L1385-1388: *"Every construct this specification introduces MUST sit at an extension point where removing it — as a Player that does not implement this specification does under the base rules for unrecognised elements and attributes (DASH §5.2.1) — leaves a valid MPD whose primary content plays"* | Q2 n/a. The construct-by-construct walk is §4.7.3-§4.7.8. |
| R1.1 | document | met | — | §4.6 DOC-1, L1385-1389 (quoted at R1#p2), shown per construct in §4.7.8 L1814-1818 (every row `OK`). | Q2 n/a. The v11.1 contradiction (C5 costing the whole MPD) is resolved in v12 (see DP-3#p1). |
| R1.2 | document | partial | 5.c | §4.6 DOC-2, L1390-1392: *"Every new construct MUST be expressed through foreign-namespace open content (DASH §5.2.1), an application-level Event Stream (DASH §5.10), or a descriptor scheme (DASH §5.8.4.8 / DASH §5.8.4.9)."*; the spec leaves an exception open at §4.7.6 L1784-1787: *"Whether a standalone document of this kind counts among the extension points the base-first rule enumerates — foreign-namespace open content, application event streams, descriptor schemes — is recorded among the questions of §8.13."* | Q2 n/a (PUB-14 L715-716 carries the Publisher MUST). `<svta:OverlayList>` fits none of the three enumerated points, and the spec flags this itself (§8.13 item 11, L3644-3646). G-3. |
| R1.3 | document | met | — | §4.6 DOC-3, L1400-1403: *"This specification MUST NOT alter or override the semantics of any construct of the base specification. The one place where a Player of this specification does not execute a base event the base would execute is recorded in §4.8.3 with its reason."*; PUB-15 L722-723. | Q2 n/a. The supersede departure is recorded, but context records it as an exception to R1.5 (R40.8), while R1.3 itself is absolute. A-3. |
| R1.4 | runtime | met | — | §4.5.17 PLY-86, L1363-1366: *"When resolving or rendering an accepted ad fails at runtime — for example a decode error, a malformed candidate, or a mid-ad network loss — the Player MUST abort that ad and continue playing the primary content uninterrupted."* | Q2 kept. |
| R1.5 | document | partial | 5.c | §4.6 DOC-4, L1404-1410: *"the base answer takes precedence: this specification adopts it and cites it (§4.8.1). It defines its own answer only where the base gives none, and declares that answer as an extension (§4.8.2). A decision that departs from the base answer anyway is recorded with its reason (§4.8.3)."*; the spec admits two unrecorded candidates at §8.13 item 12, L3652-3653: *"This edition states both as its own rules and has not recorded either as a departure (§4.8.3)."* | Q2 source-has-no-modal. PLY-35 (drop before play, where the base trims) and PLY-41 are not in §4.8.3. A-4. |
| R2.1 | runtime | met | — | §4.2 PUB-1, L653-656: *"The Publisher MUST declare the constraints applicable to an ad slot — its cap, its allowed layouts, its relation to linear events, its once-per-session bound, its early-resolution offset — in the MPD. They are not inferred at runtime by the ADS, the APS or the Player."* | Q2 kept. |
| R2.2 | runtime | met | — | §4.3 ADS-2, L761-764: *"The ADS MUST decide which ads to serve and output them as its decision document — typically VAST, though the ADS is not bound to it. Enforcing the Publisher's constraints is the Player's obligation, and this specification places none on the ADS."*; §4.4 APS-1, L779-780: *"The APS MUST convert the ADS's decision into the resolution document carrying the ad candidates"* | Q2 kept. R2.2's closing clause also says no enforcement obligation falls on the APS. The spec drops "or the APS" and has the APS enforce layouts (APS-9 L810, APS-12 L821), as context R38.4 and R39.4 require. A-2. |
| R2.3 | runtime | met | — | §4.5.1 PLY-1, L880-882: *"The Player MUST validate the candidates of a resolution document against the constraints the Publisher declared, and render only those that satisfy them."* | Q2 kept. |
| R2.4 | document | met | — | §4.6 DOC-5, L1411-1414: *"Every mechanism this specification introduces MUST be expressible within the four-actor contract of §1.2. A mechanism that would require an actor to take on a responsibility outside its role MUST be rejected or redesigned"* | Q2 n/a. |
| R11#p1 | document | met | — | §4.6 DOC-7, L1430-1431: *"This specification MUST NOT depend on any version of VAST or on VAST as a protocol"* | Q2 n/a. |
| R11#p2 | runtime | met | — | §4.6 DOC-7, L1432: *"Conformant implementations MUST be VAST-version-agnostic."* | Q2 kept. |
| R11#p3 | document | met | — | §4.6 DOC-7, L1431-1432: *"and MUST NOT impose VAST as a precondition for any actor."* | Q2 n/a. |
| R11.1 | document | met | — | §4.6 DOC-8, L1433-1434: *"The normative chapters MUST NOT cite a specific VAST version as required."* The property holds: VAST 4.x is listed only under the informative references (§2, L279-282): *"No normative clause of this document requires VAST or any VAST version."* | Q2 n/a. An `awk` over lines 1-3665 finds VAST only at L104, 120, 279-282, 459, 762, 885, 1428-1445 and 2949-3076 (§6.6 is marked informative), and none of these requires a version. |
| R11.2 | runtime | met | — | §4.5.1 PLY-2, L884-885: *"The Player MUST be able to operate regardless of whether the ADS uses VAST: it reads only the resolution document."*; §1.2 L112: *"The Player never talks to the ADS."* | Q2 kept. |
| R11.3 | document | met | — | §4.6 DOC-9, L1435-1439: *"A normative statement MUST NOT require VAST, and MUST NOT describe an actor's behaviour in terms only a VAST deployment satisfies. VAST is named as the typical case only where the same sentence states that the actor is not bound to it."* The property holds at L762: *"typically VAST, though the ADS is not bound to it."* | Q2 n/a. The field mappings are in §6.6 (informative) and Annexes A.7 and C.8 (all annexes informative, L3668). |
| R11.4 | document | partial | 5.b | §4.6 DOC-10, L1440-1443: *"This specification MUST cover the ad behaviours a VAST-based ADS can express, so that an APS fed by VAST can build a resolution document for each of them using only the semantics defined here. §6.6 tabulates that coverage."*; §6.6 L3058-3060: *"The table shows that every ad behaviour a VAST-based ADS expresses has a place in the resolution document"* | Q2 n/a. §6.6 maps pods, creatives, tracking, click-through, skip, metadata, no-fill, wrappers, tracking-only ads, UniversalAdId and Error, but ad verification (`<AdVerifications>`/OMID) and `<Icons>` are neither mapped nor declared not carried: a case-insensitive search of the spec for `AdVerification`, `OMID`, `Icons`, `viewab` returns 0 lines (the same search finds `AdVerifications` in `../context/05-dash-linear-interfaces.md` L516, which states VAST verification is not enumerated in the linear baseline). G-4. |
| R11.5 | document | met | — | §4.6 DOC-11, L1444-1446: *"Annexes A.7 and C.8 do; they constrain no implementation."*; A.7 L3885-3886: *"This is one way an APS converts it; nothing here is required."* | Q2 n/a. |
| R18.1 | document | met | — | §4.6 DOC-12, L1450-1452: *"This specification documents the Player-visible interface: the MPD event URL (served by the APS), the resolution request (§5.8), and the resolution document (§5.2)."* | Q2 source-has-no-modal. |
| R18.2 | scope | met | — | §1.3, L119-122: *"The request the APS sends to the ADS, the format of the ADS's decision document (VAST or any other), the decisioning inputs and the frequency-capping signals are agreed between those parties, outside this specification."*; DOC-12 L1453-1455: *"The Publisher's arrangement with the APS for the event URL remains bilateral, except for the parameters §5.8 defines."* | Q2 source-has-no-modal. |
| R29.1 | document | met | — | §4.6 DOC-13, L1456-1458: *"The capability parameters are **inputs about the device** — what it supports — and not conclusions about which ad experiences can be served; deriving the second from the first is the APS's."*; the set is fixed at §5.8.2 L2627-2630. | Q2 source-has-no-modal. |
| R29.2 | runtime | met | — | §4.5.2 PLY-12, L920-921: *"Sending a capability parameter is OPTIONAL. A Player MAY send all of them, some of them, or none"* | Q2 kept. |
| R29.3 | runtime | met | — | §4.5.2 PLY-13, L924-926: *"When the Player has no value for a capability parameter, or does not disclose it, the Player MUST omit that parameter entirely rather than send it with an empty or placeholder value."* | Q2 kept. |
| R29.4 | runtime | met | — | §4.5.2 PLY-14, L927-929: *"A parameter the Player adds that is not one of the reserved names of §5.8 MUST carry a vendor-specific prefix (§5.8.4), so that reserved names added by a later edition cannot collide with it."* | Q2 kept. The prefix binds only the Player, so the Publisher's `@uri` query can still use `sgai-` names. EC-5. |
| R29.5 | runtime | met | — | §4.4 APS-15, L833-834: *"The APS MUST tolerate the absence of any capability parameter, and MUST be able to produce ad candidates without receiving any of them."* | Q2 kept. |
| R29.6 | document | met | — | §4.6 DOC-13, L1458-1460: *"The set MUST be able to express the capability axes that distinguish the device classes of §3.6; §5.8.2 shows that it tells all five apart."*; §5.8.2 L2639-2643 (the D1-D5 rows), L2645: *"No two rows are equal."* | Q2 n/a. Checked against context 04 L58-67: the D1-D5 values in the table match. |
| R29.7 | document | met | — | §4.6 DOC-14, L1462-1463: *"its value is undetermined — the Player did not determine it, or did not disclose it. Absence does not assert that the device lacks the capability."*; APS-15 L835-837: *"how the APS resolves an undetermined value is its own decision, and two APSs that resolve it differently are both conformant."* | Q2 source-has-no-modal. |
| R29.8 | document | met | — | §4.6 DOC-15, L1466-1469: *"The forwarded allowed layouts and the forwarded custom region are the exceptions to the optionality of PLY-12: when a window declares them, the Player is required to send them (PLY-15, PLY-16). Every other reserved parameter remains optional."* | Q2 source-has-no-modal. The obligation itself carries MUST in PLY-15 (L930) and PLY-16 (L934). |
| R4#p1 | runtime | met | — | §4.5.4 PLY-24, L992-993: *"Player MUST stop rendering once the cumulative duration of the accepted candidates would exceed it, even if the stop falls mid-ad."* | Q2 kept. Sentence: "The Player MUST enforce it, stopping at the bound even when the stop falls mid-ad." (03 L340). |
| R4.1 | runtime | met | — | §4.2 PUB-2, L657-658: *"The Publisher MUST declare a cap (`@durationCap`, §5.1.3) on every overlay window and every pause window."*; L659-660: *"the cap is the base specification's `@maxDuration`, which the Publisher MAY omit"* | Q2 kept. What the mandatory pause cap bounds: G-1. |
| R4.2 | runtime | met | — | §4.5.4 PLY-24, L990-993: *"Where the cap bounds cumulative duration — overlay windows, one pass of a pause resolution document, and linear insertion — the Player MUST stop rendering once the cumulative duration of the accepted candidates would exceed it, even if the stop falls mid-ad."* | Q2 kept. "One pass" for the pause family is the spec's reading of a context silence (G-1). |
| R4.3 | runtime | met | — | §4.5.4 PLY-25, L994-998: *"The Player MUST NOT extend a slot beyond what the cap bounds for that slot's family, regardless of ADS metadata or candidate count. On a replacement slot the bound is the scheduled end, so an event declaring `@clip="false"` ends later than that end without violating this criterion"* | Q2 kept. |
| R4.4 | runtime | met | — | §4.3 ADS-1, L758-760: *"The ADS is NOT required to respect the cap when selecting candidates. A conformance check on the ADS MUST NOT fail solely because the cumulative duration of its returned candidates exceeds the cap."* | Q2 kept. |
| R4.5 | runtime | met | — | §4.5.4 PLY-26, L999-1001: *"When the actual rendered length of an accepted candidate exceeds its declared duration, the Player MUST enforce the cap against actual length, not declared length ("trim during play")."* | Q2 kept. |
| R4.6 | runtime | met | — | §4.5.4 PLY-27, L1002-1005: *"On an inherited replacement slot, the Player MUST honour the base clip semantics: unless the event declares otherwise, the presentation ends at the scheduled end of the slot, and a late start shortens it rather than moving that end."*; insertion: table L986 *"`@clip` does not exist on insertion."* | Q2 kept. |
| R4.7 | runtime | met | — | §4.2 PUB-3, L664: *"A declared cap of zero means the opportunity does not fire."*; L668: *"A zero cap is not a very short slot."*; §4.5.4 PLY-30, L1024: *"A cap of zero means the opportunity does not fire (PUB-3)."* | Q2 source-has-no-modal. |
| R4.8 | document | met | — | §4.2 PUB-2, L659-663: *"which the Publisher MAY omit; an absent `@maxDuration` keeps its base meaning, *"If absent, the value is assumed to be infinity, in which case the current presentation resumes only when the alternative presentation terminates"*"*; PLY-29, L1021-1023: *"An inherited linear event with no `@maxDuration` is outside this criterion: the Player executes it with its base semantics."* | Q2 n/a. (Source also carries no modal.) |
| R4.9 | runtime | met | — | §4.5.4 PLY-28, L1008-1011: *"The Player MUST convert the candidate's duration into the cap's timescale before comparing the two, and MUST round the converted value **up** to the next whole unit of that timescale. A candidate whose converted duration equals the cap exactly is admitted."* | Q2 kept. |
| R4.10 | runtime | met | — | §4.5.4 PLY-29, L1018-1021: *"An overlay or pause window carrying no `@durationCap` is not a window this specification defines. The Player MUST NOT present ads from such a window and MUST continue with the primary content; reading the absence as an unbounded default is not admissible."* | Q2 kept. Inherited linear carve-out at L1021-1023. |
| R4.11 | runtime | met | — | §4.5.4 PLY-31, L1025-1029: *"The Player MUST compute the cap on the presentation timeline — for a slot, its slot timeline (§3.1). An interval during which the presentation timeline does not advance MUST NOT accrue against the cap, so a form suspended while the viewer is paused resumes with the remaining cap it had when it was suspended."* | Q2 kept. |
| R31.1 | runtime | met | — | §4.5.2 PLY-11, L915-917: *"The Player MUST request a resolution document when a viewer pause begins inside a pause window, and MUST NOT request one for a pause that begins outside every such window."* | Q2 kept. |
| R31.2 | runtime | met | — | §4.5.4 PLY-32, L1033-1037: *"The Publisher-declared cap MUST NOT be interpreted as bounding the duration of a pause slot. It bounds an end on a replacement slot and a cumulative duration elsewhere; on a pause slot there is no authored duration for it to bound, and PLY-24 applies to one pass of a document, not to the pause."* | Q2 kept. Same silence as G-1 (what the required pause cap does bound). |
| R12.1 | document | met | — | §3.4.2, L508-510: *"The following tokens are the **complete** list of layout values this specification accepts. Every token except `custom` names one IAB ad type or visual placement."*; §4.6 DOC-17, L1478-1479: *"MUST NOT accept a value outside that enumeration, and MUST cite the IAB source for the values it accepts (chapter 2)."*; schema `LayoutTokenType` enumeration L2744-2756 | Q2 n/a. IAB source cited at §3.4 L483-484. |
| R12.2 | runtime | met | — | §4.2 PUB-4, L669-671: *"A Publisher declaring allowed layouts MUST use only the tokens of §3.4.2. Publisher-private layout names MUST NOT appear in the allowed-layouts declaration of a window."* | Q2 kept. Bare `squeezeback`/`pause` excluded at §3.4.2 L537 (*"The bare `squeezeback` and `pause` are not tokens"*). |
| R12.3 | runtime | met | — | §4.4 APS-8, L808-809: *"The APS MUST NOT emit form metadata for an ad type or visual placement outside the tokens of §3.4.2."* | Q2 kept. Check-against-APS-document clause carried at §4.3 closing paragraph (L770-772). |
| R12.4 | document | met | — | §4.6 DOC-18, L1480-1482: *"Each accepted layout implies the spatial bound the IAB guidelines declare for it, inherited by reference; no dimensional attribute is introduced on the slot declaration."* | Q2 n/a. (Source carries no modal.) Tension with `@customRegion` on the window: A-5. |
| R15.1 | document | met | — | §3.5, L579-580: *"The admissible creative carriers are **exactly three**, and no annex, example or implementation note of this document adds another:"*; DOC-19 L1483-1485. No other creative mimeType found in the document (only `application/dash+xml`, `image/png`, `image/jpeg`, `text/html` on options; `video/mp4`/`audio/mp4` only inside sub-MPDs). | Q2 n/a. |
| R15.2 | runtime | met | — | §4.4 APS-10, L813-814: *"Ad candidates in the resolution document MUST carry a creative whose media type falls under one of the three forms of §3.5."*; §4.2 PUB-17, L729-730: *"Forms the Publisher declares MUST carry a creative whose media type falls under one of the three forms of §3.5."* | Q2 kept. |
| R15.3 | runtime | met | — | §4.5.1 PLY-5, L892-894: *"The Player MAY skip a candidate whose creative media type is outside §3.5; such a candidate signals a non-conformant ADS, APS or Publisher."* | Q2 kept (MAY). |
| R5#p1 | runtime | met | — | §4.5.3 PLY-17, L940-942: *"The Player MUST evaluate the presentation options of an accepted candidate **in document order**, and render the **first** option whose form and layout it can satisfy on its device."* | Q2 kept. Sentence: "The Player MUST render the first presentation option whose form and layout its device can satisfy" (03 L669-671). |
| R5#p2 | runtime | met | — | §4.5.3 PLY-20, L954-957: *"If no option of a candidate satisfies PLY-18, the Player MUST skip that candidate and fall through to the next candidate in document order; when the candidates are exhausted, the Player MUST continue with the primary content."* | Q2 kept. Sentence: "and MUST skip candidates with no satisfiable option" (03 L671). Pause exception at PLY-65. |
| R5#p3 | runtime | met | — | §4.5.3 PLY-18, L943-949: *"The Player MUST resolve option selection by walking the options in document order and checking each against (a) its device's capabilities and (b) the layouts the window admits"* … *"It renders the first option that satisfies both"* | Q2 kept. Sentence: "The Player MUST select per device capabilities and the Publisher's allowed layouts" (03 L690-692). |
| R5.1 | runtime | met | — | §4.4 APS-5, L793-796: *"Each ad candidate MUST carry one or more presentation options (each a form plus its layout) as an ordered list, where document order is the preference order. How many options a candidate carries is the APS's decision: this specification sets no maximum, and no minimum beyond one."* | Q2 kept. |
| R5.2 | runtime | met | — | §4.5.3 PLY-17, L940-942: *"The Player MUST evaluate the presentation options of an accepted candidate **in document order**, and render the **first** option whose form and layout it can satisfy on its device."* | Q2 kept. |
| R5.3 | runtime | met | — | §4.5.3 PLY-20, L954-957: *"the Player MUST skip that candidate and fall through to the next candidate in document order; when the candidates are exhausted, the Player MUST continue with the primary content."* | Q2 kept. MUST-skip vs PLY-34 MAY-drop: A-6. |
| R5.4 | runtime | met | — | §4.3 ADS-3, L765-768: *"This specification MUST NOT be read as obliging the ADS to maintain a device-class matrix or a per-Player capability view in order to produce candidates."*; §4.4 APS-7, L803-807: *"This specification MUST NOT be read as obliging the APS to maintain a device-class matrix or a per-Player capability view in order to produce candidates."* | Q2 kept. |
| R5.5 | runtime | met | — | §4.4 APS-6, L797-800: *"An ad candidate MAY carry multiple presentation options, each pairing a form with an admissible layout. The options form a single ordered list, and their document order is the preference order the Player follows."* | Q2 kept (MAY). |
| R5.6 | runtime | met | — | §4.5.3 PLY-18, L943-949: *"checking each against (a) its device's capabilities and (b) the layouts the window admits — the tokens of the declared `@allowedLayouts` that its family can present (§3.4.3), or the family default when none is declared. It renders the first option that satisfies both; an option that fails either MUST NOT be rendered, and the Player moves to the next option."* | Q2 kept. |
| R5.7 | runtime | met | — | §4.5.3 PLY-20, L954-957: *"If no option of a candidate satisfies PLY-18, the Player MUST skip that candidate and fall through to the next candidate in document order; when the candidates are exhausted, the Player MUST continue with the primary content."* | Q2 kept. |
| R7#p1 | runtime | met | — | §4.5.5 PLY-33, L1046-1048: *"Given a resolution document with more than one candidate, the Player MUST play the candidates in the order the resolution document declares, except for candidates dropped under PLY-34 or PLY-35."* | Q2 kept. Sentence: "the Player MUST play the ads in the order the resolution document declares" (03 L743-745). |
| R7#p2 | runtime | contradicted | 5.b | Breaking: §4.5.1 PLY-1, L882-883: *"Any client-side criterion it adds (ranking, deduplication) operates inside the validated subset."* — while PLY-36, L1054-1055 states *"The Player MUST NOT re-order, deduplicate, or otherwise rearrange the remaining candidates"* | Q2 kept. Sentence: "but it MUST NOT re-order, deduplicate, or otherwise rearrange the remaining candidates" (03 L748-749). Spec both permits and forbids Player dedup/ranking; context 02-actors L178-180 backs PLY-1, so not 5.a. A-1, F-1. |
| R7.1 | runtime | met | — | §4.5.5 PLY-33, L1046-1048: *"the Player MUST play the candidates in the order the resolution document declares, except for candidates dropped under PLY-34 or PLY-35."* | Q2 kept. |
| R7.2 | runtime | met | — | §4.5.5 PLY-34, L1049-1050: *"The Player MAY drop a candidate that has no form renderable on its device."* | Q2 kept (MAY). |
| R7.3 | runtime | met | — | §4.5.5 PLY-35, L1051-1053: *"The Player MAY drop a candidate before playback ("drop before play") when its declared duration would push the cumulative slot duration past the cap."* | Q2 kept (MAY). Departure-from-base status left open by the spec itself (L1060-1065, §8.13). |
| R7.4 | runtime | contradicted | 5.b | Breaking: §4.5.1 PLY-1, L882-883: *"Any client-side criterion it adds (ranking, deduplication) operates inside the validated subset."*; satisfying site: PLY-36, L1054-1055: *"The Player MUST NOT re-order, deduplicate, or otherwise rearrange the remaining candidates after applying PLY-34 or PLY-35."* | Q2 kept. Two spec sites disagree; context 02-actors L178-180 supports PLY-1's reading, so the fix is not unique → 5.b (and 5.c for 02-actors). A-1, F-1, D-4. |
| R7.5 | runtime | met | — | §4.5.5 PLY-37, L1056-1058: *"If a candidate is accepted and its actual rendered length exceeds the cap, the Player MUST trim it mid-rendering ("trim during play")."* | Q2 kept. |
| R30.1 | runtime | met | — | §4.4 APS-4, L790: *"An opportunity that resolved with no ads MUST be expressed as a resolution document carrying no candidates (§5.2.3), and MUST NOT be expressed as an error response or as a response without a body."*; shapes per family in §5.2.3, L2244 | Q2 kept |
| R30.2 | runtime | met | — | §4.5.6 PLY-44, L1117: *"A resolution carrying no candidates MUST NOT count as an execution of the opportunity. Where the opportunity is an inherited event with `@executeOnce="true"`, it remains executable afterwards"*; pause windows via PLY-64, L1237: *"A pause that resolves to no renderable candidate MUST leave the window available."* | Q2 kept. PLY-44 names only inherited events for `@executeOnce`; the pause window's `@executeOnce` is covered by PLY-64 and §5.2.3 L2249 (*"does not consume the opportunity (PLY-44, PLY-64)"*). |
| R3.1 | document | met | — | §4.6 DOC-20, L1486: *"This specification MUST enumerate the supported device classes and, for each, the expected behaviour for each opportunity type (§3.6, chapter 7, Annexes A to Q)."*; §3.6 table L597-601 (D1-D5); ch. 7 per-class tables (e.g. §7.4 L3132-3136, §7.7 L3186-3190) | Q2 n/a |
| R3.2 | runtime | met | — | §4.5.1 PLY-3, L886: *"A Player on any device class MUST produce a defined behaviour — render, fall back, or skip — for every opportunity type this specification defines. Undefined behaviour is non-conforming."* | Q2 kept |
| R3.3 | runtime | met | — | §4.5.1 PLY-4, L890: *"The Player MUST NOT attempt to render a form (video, image, HTML) that its device class cannot render."* | Q2 kept |
| R16.1 | runtime | met | — | §4.5.10 PLY-57, L1206: *"Upon a pause-to-play transition by the viewer, the Player MUST remove any rendered pause ad from the screen within one rendering frame."* | Q2 kept |
| R16.2 | runtime | met | — | §4.5.10 PLY-58, L1208: *"Upon the same transition, the Player MUST cease firing the tracking beacons scheduled for the dismissed pause ad; beacons scheduled after the transition fall outside its active window."* | Q2 kept |
| R32.1 | runtime | met | — | §4.4 APS-22, L872: *"A resolution document for a pause window MUST declare which exhaustion behaviour applies — `repeat`, `request-again` or `stop` (`@onExhausted`, §5.2.6)."*; §4.5.11 PLY-65, L1245: *"Absent the declaration, the Player MUST apply `stop`."* | Q2 kept |
| R32.2 | runtime | met | — | §4.5.11 PLY-66, L1250: *"Under `request-again`, a resolution document carrying no candidates MUST be treated as `stop` for the remainder of that pause."* | Q2 kept |
| R32.3 | runtime | met | — | §4.5.10 PLY-60, L1215: *"When the viewer resumes, the Player MUST return to the primary content immediately, whether or not an ad is mid-presentation."* | Q2 kept |
| R32.4 | scope | met | — | §1.3, L178-179: *"Whether a second resolution request within one pause is the same opportunity or a new one"*; §4.5.11 L1253: *"Whether a second resolution request within one pause is the same opportunity or a new one is out of scope."* | Q2 source-has-no-modal |
| R34.1 | runtime | met | — | §4.2 PUB-10, L697: *"The Publisher MAY declare a pause window as once-per-session (`@executeOnce="true"`, §5.1.4). A window that does not carry the declaration yields a pause ad on every qualifying pause."* | Q2 kept |
| R34.2 | runtime | met | — | §4.5.10 PLY-63, L1232: *"On a window declared once-per-session, the Player MUST present at most one pause ad for that window for the duration of the session. A later qualifying pause inside the same window MUST leave the primary content uninterrupted."* | Q2 kept. "At most one pause ad" left as ambiguous as in context (A-7). |
| R34.3 | runtime | met | — | §4.5.10 PLY-64, L1236: *"The Player MUST treat such a window as consumed when a pause ad **begins rendering**, and not when the pause occurs. A pause that resolves to no renderable candidate MUST leave the window available."* | Q2 kept |
| R34.4 | document | met | — | §4.8.1, L1843: *"Once-per-session on a pause window \| The name `@executeOnce` and the counter rule (E.c increments when playback *"successfully starts"*)"*; PLY-64 L1238: *"This is the base specification's counter rule — E.c counts executions that *"successfully started"* (Table 58) — restated for a trigger that is the viewer and not the playhead."* | Q2 source-has-no-modal. Property holds: the construct reuses the base name `@executeOnce` (§5.1.4 L2116). |
| R35.1 | runtime | met | — | §4.4 APS-19, L858: *"The APS MUST declare, for each overlay or pause slot it resolves, whether the viewer may dismiss it (`@dismissAfter`, §5.2.4). A resolution document that does not declare it leaves the slot non-dismissible: the capability is granted and never assumed."* | Q2 kept |
| R35.2 | runtime | met | — | §4.4 APS-20, L864: *"Where dismissal is allowed, the APS MUST declare the number of seconds that MUST elapse, from the moment the slot begins rendering, before the viewer may dismiss it. A declared delay of zero means the slot is dismissible immediately."* | Q2 kept |
| R35.3 | runtime | met | — | §4.5.14 PLY-74, L1293: *"Before the declared dismissal delay has elapsed, the Player MUST NOT offer the viewer a way to dismiss the slot. After it has, the Player MUST make dismissal available for as long as the slot is on screen."* | Q2 kept |
| R35.4 | runtime | met | — | §4.5.14 PLY-75, L1298: *"A dismissal ends the **whole slot**. The Player MUST stop presenting every ad of that slot and MUST NOT advance to another ad or another form within it."* | Q2 kept |
| R35.5 | runtime | met | — | §4.5.14 PLY-76, L1304: *"A dismissed slot does not shorten the primary content. Where the slot bounded a region of the primary timeline, the Player MUST continue from where the primary content stands, and MUST NOT compress or skip any part of it."* | Q2 kept |
| R35.6 | runtime | met | — | §4.5.14 PLY-77, L1308: *"The Player MUST fire the tracking events the resolution document scheduled up to the moment of the dismissal, and MUST NOT fire those scheduled after it."* | Q2 kept |
| R35.7 | scope | met | — | §1.3, L176-177: *"— a control, a gesture, a remote button (§4.5.14)."* (item headed *"How a dismissal is offered to the viewer"*); §4.5.14 L1323: *"How the dismissal is offered — a control, a gesture, a remote button — is out of scope."* | Q2 source-has-no-modal |
| R35.8 | runtime | met | — | §4.5.14 PLY-78, L1312: *"On a linear slot, the Player MUST apply the base specification's own skip declaration and its default as the base specification defines them, and they govern the slot (§5.2.4): where nothing is declared, the base default applies and the slot is skippable as the base specification makes it"*; L1318: *"The default of APS-19 does not apply to a linear slot"* | Q2 kept |
| R36.1 | runtime | met | — | §4.2 PUB-9, L691: *"The Publisher MAY declare, on an overlay or pause window, how far ahead of the window a Player may resolve it (`@earliestResolutionTimeOffset`, §5.1.3). A window that declares nothing may be resolved up to 60 seconds ahead, the base specification's default. A Publisher that wants a window resolved only when it fires declares an offset of zero."* | Q2 kept |
| R36.2 | runtime | met | — | §4.5.2 PLY-6, L898: *"On an overlay window, the Player MUST NOT resolve earlier than the offset — declared, or the default of 60 seconds — before the start of the window."* | Q2 kept |
| R36.3 | runtime | met | — | §4.5.2 PLY-7, L901: *"On a pause window, the Player MUST NOT resolve earlier than the offset — declared, or the default of 60 seconds — before the start of the window. The offset is computed against the start of the window and never against the pause, which has no authored time."* | Q2 kept |
| R36.4 | runtime | met | — | §4.4 APS-21, L868: *"Where a resolution may have been obtained ahead of the opportunity, the APS MUST declare how long that resolution remains usable (`@validFor`, §5.2.5). A resolution document that does not declare it remains usable for as long as its window lasts."* | Q2 kept. Reference instant (receipt) is the spec's choice, §5.2.5 L2306 (EC-1). |
| R36.5 | runtime | met | — | §4.5.2 PLY-9, L908: *"When the opportunity fires, the Player MUST check whether the resolution it holds is still usable (§5.2.5). If it is not, the Player MUST request a new one and MUST NOT present candidates from the expired resolution."* | Q2 kept |
| R36.6 | runtime | met | — | §4.5.2 PLY-10, L912: *"When a re-resolution yields no usable candidate, the Player MUST treat it as a resolution carrying no candidates and MUST NOT fall back on the expired one."* | Q2 kept |
| R36.7 | document | met | — | §4.5.2 PLY-8, L905: *"Resolving early is a permission and never an obligation. A Player that resolves only when the opportunity fires is conformant, whatever offset the window carries."* | Q2 source-has-no-modal |
| R37.1 | runtime | met | — | §4.5.10 PLY-56, L1202: *"A Player MAY implement a pause by any mechanism that suspends the primary content and later resumes it from the position at which it was suspended, including one that releases the primary content's decoding resources for the duration of the pause."* | Q2 kept |
| R37.2 | runtime | met | — | §4.5.10 PLY-59, L1211: *"On resume, the Player MUST continue the primary content from the position at which it was suspended. A mechanism that cannot restore that position is not a pause under this specification, whatever it is called."* | Q2 kept |
| R37.3 | document | partial | 5.b | §4.5.10 PLY-56, L1202: *"A Player MAY implement a pause by any mechanism that suspends the primary content"*; §8.7 L3536: *"A pause frees a decoder only if the Player chooses to free it."* | Q2 source-has-no-modal. The document prescribes no mechanism, but carries no counterpart of R37.3's reading rule (*"a criterion elsewhere that appears to assume one mechanism is to be read as this requirement defines it"*), while several passages assume a held frame (e.g. §5.3.7 L2455 *"1 (holding the paused frame) or none"*, PLY-61 *"composited over the paused primary frame"*). F-2. |
| R38.1 | runtime | met | — | §4.2 PUB-5, L673-675: *"Declaring the allowed layouts on a non-linear window is OPTIONAL. A window that declares none admits the family default of §3.4.3."*; §3.4.3 L570-572: *"The family default does **not** include `linear` — an overlay window that declares nothing does not admit the full-screen takeover — and it does not include `custom`, which a window admits only by listing it."* | Q2 kept. Family default table L565-568 matches R12's Overlay+Squeezeback / Pause-ad entries. |
| R38.2 | runtime | met | — | §4.5.2 PLY-15, L930-933: *"When the window declares allowed layouts, the Player MUST send the declared set, unchanged, on the resolution request (§5.8.3). When the window declares none, nothing is sent, and the set that binds the APS and the Player is the family default."* | Q2 kept. |
| R38.3 | document | met | — | §4.6 DOC-15, L1469-1470: *"The way they travel is normative and defined in §5.8.3."*; §5.8.3 L2651: *"`sgai-allowed-layouts` \| The value of the window's `@allowedLayouts`, unchanged."* (reserved `sgai-` parameter, §5.8.4 L2665) | Q2 n/a; source-has-no-modal. |
| R38.4 | runtime | met | — | §4.4 APS-9, L810-812: *"The APS MUST NOT return an option whose layout is outside the set of allowed layouts it received on the request or, when it received none, outside the family default of §3.4.3 for the window's family."* | Q2 kept. |
| R38.5 | runtime | met | — | §4.5.3 PLY-19, L950-953: *"Before rendering, the Player MUST check that the option it selects uses a layout the window admits, and MUST NOT render it otherwise. Forwarding the set to the APS does not remove this check"* | Q2 kept. Fall-through to next option: PLY-18 L948-949. |
| R38.6 | scope | met | — | §4.6 DOC-16, L1471-1472: *"Inherited linear events carry no allowed-layouts declaration, and the forwarding of PLY-15 does not apply to them."*; §5.8.3 L2654: *"They are not sent for inherited linear events."* | Q2 n/a; source-has-no-modal. |
| R39.1 | document | met | — | §4.6 DOC-21, L1489-1491: *"Supporting `custom` is OPTIONAL for every actor. It carries no IAB ad type, it is the only layout for which this specification defines a position, and it applies only to overlay windows."*; §3.4.2 L510-511 | Q2 n/a. |
| R39.2 | runtime | met | — | §4.2 PUB-6, L676-679: *"A Publisher that admits `custom` on an overlay window lists it in `@allowedLayouts`. It MAY also declare a custom region on the window (`@customRegion`, §5.3.5); with none declared, the region is the whole video viewport."* | Q2 kept. Units/origin: §5.3.5 L2392-2404 and schema `PercentRectType`. |
| R39.3 | runtime | met | — | §4.5.2 PLY-16, L934-936: *"When the window declares a custom region, the Player MUST send it on the resolution request together with the allowed layouts, as §5.8.3 defines."* | Q2 kept. |
| R39.4 | runtime | met | — | §4.4 APS-12, L821-825: *"An option with layout `custom` MUST carry the overlay's rectangle in percent of the video viewport (`@rect`, §5.3.5), and that rectangle MUST lie entirely inside the region the APS received on the request, or inside the viewport when it received none. It MAY be smaller than the region; it MUST NOT extend beyond it."* | Q2 kept. |
| R39.5 | runtime | met | — | §4.5.3 PLY-21, L958-962: *"Before rendering a `custom` option, the Player MUST check that its rectangle lies inside the window's custom region (or the viewport when none is declared), and MUST NOT render it otherwise; the option is then not renderable and the Player moves to the next one. A Player that does not support `custom` treats every `custom` option as not renderable."* | Q2 kept. |
| R19#p1 | runtime | met | — | §4.5.12 PLY-67, L1262-1264: *"The Player MUST render every ad form, linear or non-linear, at the same playback speed as the primary content at the moment the ad is presented."* | Q2 kept. Unit = R19 prose "All ad content ... MUST be rendered at the same playback speed". |
| R19.1 | runtime | met | — | §4.5.12 PLY-67, L1262-1264: *"The Player MUST render every ad form, linear or non-linear, at the same playback speed as the primary content at the moment the ad is presented."* | Q2 kept. |
| R19.2 | runtime | met | — | §4.5.12 PLY-68, L1265-1266: *"The Player MUST NOT force an ad to 1x when the primary content is playing at a different speed."* | Q2 kept. |
| R19.3 | runtime | met | — | §4.5.12 PLY-69, L1267-1270: *"The Player MUST compute a form's wall-clock on-screen duration as `duration / playback_speed`, not as the raw `duration`. Cap enforcement and beacon scheduling operate on the presentation-timeline `duration`."* | Q2 kept. Walked in §7.20 L3429-3431 and B.7 L4111-4115. |
| R19.4 | runtime | met | — | §4.5.12 PLY-70, L1271-1274: *"A form's declared duration is a value on the presentation timeline for every form, including those with no intrinsic media (image, HTML). The Player MUST derive the wall-clock length of such a form as `duration / playback_speed`, exactly as for a video."* | Q2 kept. |
| R21.1 | runtime | met | — | §4.5.10 PLY-61, L1217-1225: *"The Player MAY present a pause ad fullscreen, occupying the entire screen, or as a partial overlay composited over the paused primary frame ... When it is partial, the Player MUST keep at most one non-linear form active during the pause: any coexisting overlay is suspended while the pause ad is shown."* | Q2 kept (MAY and MUST both carried). |
| R25#p1 | runtime | met | — | §4.5.10 PLY-62, L1226-1229: *"In live content, while the viewer is paused inside a pause window, the Player MUST keep its presentation time frozen inside that window for the full duration of the pause, regardless of the live edge advancing in wall-clock time."* | Q2 kept. Unit = R25 prose "the Player's presentation time MUST freeze inside that window". |
| R25.1 | runtime | met | — | §4.5.10 PLY-62, L1229-1231: *"Any decision to resume at the live edge MUST be treated as a Player action occurring after the resume from pause, outside the pause window."* | Q2 kept. |
| R26.1 | runtime | met | — | §4.4 APS-13, L826-828: *"The background image of a double-box layout MUST be carried as a composition attribute of the option (`@background`, §5.3.6), not as a separate presentation option."*; §5.3.6 L2429: *"The background is a composition attribute, never an option, and is always a still image."* | Q2 kept. Met under the reading that the layout is carried by the option (`@layout` on `<svta:RenderableAsset>`); context says "slot / layout". A-8 (D-15). |
| R26.2 | runtime | met | — | §4.5.13 PLY-71, L1278-1281: *"The Player MUST composite the primary content and the ad as the two boxes of a double-box layout. When the option carries a background image, the Player MUST place it in the uncovered bands; when it carries none, the uncovered region renders black."* | Q2 kept. |
| R26.3 | runtime | met | — | §4.5.3 PLY-22, L963-969: *"A double-box option whose ad is a **video** needs two concurrent video decoders plus an image surface for the background, and MUST NOT be selected on a single-decoder device. ... A non-video element — the ad when it is an image or HTML, or the background image — MUST NOT be selected on a device that cannot composite that surface type over video."* | Q2 kept. Budget table §5.3.7 L2447-2452 (background+video ad D1 only). |
| R27.1 | runtime | met | — | §4.4 APS-14, L829-832: *"An L-shape option MUST carry exactly one ad creative — the full-frame background creative — as an image, a video, or an HTML document. The shrunk primary content is not a creative the APS supplies; it is the primary content the Player shrinks."* | Q2 kept. |
| R27.2 | runtime | met | — | §4.5.13 PLY-72, L1282-1285: *"The Player MUST composite the two elements of an L-shape — the full-frame creative in the background and the shrunk primary content on top of it — with the creative covering the whole frame and the primary content scaled into the region its layout token names (§3.4.2)."* | Q2 kept. |
| R27.3 | runtime | met | — | §4.5.3 PLY-23, L970-976: *"A **video** creative consumes a second one, so the L-shape is not satisfiable on a single-decoder device. An **image or HTML** creative consumes a surface of that type; an image or HTML full-frame creative MUST NOT be selected on a device that cannot composite that surface type together with video."* | Q2 kept (source's own video clause is indicative; its MUST NOT is carried). |
| R14.1 | runtime | met | — | §4.5.7 PLY-46, L1130-1133: *"When the resolution document of a non-linear window declares more than one candidate, the Player MUST present them in sequence, in the order they appear in the document, each starting when the previous one ends."* | Q2 kept. |
| R14.2 | runtime | met | — | §4.5.7 PLY-47, L1135-1137: *"The Player MUST enforce the window's cap against the cumulative duration of the sequence of non-linear candidates it presents, trimming or dropping per PLY-24 to PLY-37."* | Q2 kept. |
| R14.3 | document | met | — | §4.6 DOC-23, L1502-1505: *"This specification MUST NOT introduce a construct that implies or requires the simultaneous rendering of two or more non-linear forms. Sequencing inside a slot is carried by the candidates' document order and by no separate primitive."* | Q2 n/a. No parallel-render construct found in §5 (candidates only via `<svta:Ad>` order, L2343). |
| R17.1 | runtime | met | — | §4.5.9 PLY-52, L1181-1184: *"While the viewer is paused inside a pause window and an overlay is active, the Player MUST render the pause ad and MUST suspend the overlay's rendering."* | Q2 kept. No-pause-ad case: EC-3. |
| R17.2 | runtime | met | — | §4.5.9 PLY-53, L1185-1186: *"On resume, the Player MUST dismiss the pause ad and MUST restore the overlay if the overlay window is still active."* | Q2 kept. |
| R17.3 | runtime | met | — | §4.5.9 PLY-54, L1187-1188: *"If the overlay window expired during the pause, the Player MUST keep the overlay surface clear on resume; the overlay is over."* | Q2 kept. Walked in H.8 L5466-5472. |
| R17.4 | document | met | — | §4.5.9 L1198: *"No construct lets the Publisher, the ADS or the APS invert this priority."*; §4.6 DOC-24 L1506-1508 | Q2 n/a; source-has-no-modal. |
| R17.5 | runtime | partial | 5.c | §4.5.9 PLY-55, L1189-1196: *"When a viewer pause begins inside a pause window applicable to the presentation being output while a linear ad occupies the screen, the Player MUST present the pause ad and MUST suspend the linear ad ... A pause window is applicable to a linear ad when it is declared in that ad's own MPD (PLY-51) or when it is a window of the triggering presentation that declares `on-top` (PLY-50)."* | Q2 kept. Carried only for "applicable" windows; a default-relation pause window of the primary MPD is excluded, which R17.5 does not say but R40.4 implies. Context-internal tension, A-9. |
| R20.1 | runtime | met | — | §4.5.6 PLY-38, L1071-1073: *"An attempt **on a window** that does not produce an ad is a failed execution, and on a failed execution the Player MUST attempt the next overlapping window of the same family."*; PLY-39 L1080-1094 (four conditions + continue uninterrupted); PLY-41 L1103-1106 | Q2 kept. |
| R20.2 | runtime | met | — | §4.2 PUB-7, L680-681: *"All opportunity windows of one family that share a `Period` MUST be authored as `Event` entries inside a **single** `EventStream`."* | Q2 kept. §5.10.2.1 quote and no-`@value` rationale L682-688, PUB-8 L689-690. |
| R20.3 | runtime | met | — | §4.5.6 PLY-40, L1095-1098: *"The Player MUST order overlapping windows of one family by presentation time, oldest first. Where two windows carry the same presentation time, the Player MUST take them in the order in which they appear inside the `EventStream`."* | Q2 kept. |
| R20.4 | runtime | met | — | §4.5.6 PLY-42, L1107-1111: *"A resolution document whose `@family` does not match the window that requested it is not a resolution of that window. The Player MUST treat it as a failed execution, MUST NOT present any of its candidates in the slot, and MUST continue down the chain of PLY-38"* | Q2 kept. |
| R20.5 | runtime | met | — | §4.5.6 PLY-43, L1112-1115: *"The Player MUST bind the candidates each window of a fallback chain serves with **that window's own** declarations — its allowed layouts, its custom region and its cap. The Player MUST NOT apply the declarations of the window it stands in for."* | Q2 kept. |
| R20.6 | document | met | — | PLY-43 sits in normative §4.5.6, L1112-1116; §4.6 DOC-25, L1509-1511: *"The rule that each window of a fallback chain binds its own candidates (PLY-43) MUST be carried as a normative Player obligation, not only in informative material; it is."* | Q2 n/a. |
| R22.1 | runtime | met | — | §4.5.7 PLY-45, L1126-1128: *"At any instant, the Player MUST keep at most **one** non-linear ad form active on the screen. The Player MUST NOT present two or more non-linear ad forms simultaneously."* | Q2 kept. |
| R40.1 | runtime | partial | 5.c | §4.2 PUB-11, L700-703: *"Declaring a relation on a non-linear window is OPTIONAL. A window declares at most one relation, supersede or on top (`@linearRelation`, §5.1.6)"*; narrowed at §5.1.6 L2142: *"On a **pause window**, `@linearRelation` takes only the value `on-top`"* | Q2 kept. Supersede, which R40.1 admits on any non-linear window, is withdrawn for pause windows (schema `OnTopOnlyType` L2847). A-10. |
| R40.2 | runtime | met | — | §4.2 PUB-12, L704-707: *"A Publisher that wants a non-linear ad presented during an alternative presentation MUST declare it either by a window in that alternative presentation's own MPD, or by a window of the triggering presentation that declares `on-top`."* | Q2 kept. |
| R40.3 | runtime | met | — | §4.5.8 PLY-48, L1154-1160: *"When a window declares **supersede**, the Player MUST present the window and MUST NOT execute the inherited linear events whose presentation time falls within its span. When the window presents no ad — every attempt to resolve it is a failed execution (PLY-38, PLY-39), or the device can render none of its candidates (PLY-20) — the Player MUST execute those events as the base specification defines"* | Q2 kept. |
| R40.4 | runtime | met | — | §4.5.8 PLY-49, L1161-1165: *"When a window declares **no relation**, the Player MUST present its forms only while the content of the presentation whose MPD declares the window is being output, and MUST execute every inherited linear event it overlaps with its base semantics. A form on screen when an alternative presentation begins ends there, and the window presents nothing further."* | Q2 kept. PLY-49 L1166-1169 fixes "nothing further" as the rest of the span; consistent with §7.6 L3173-3176. |
| R40.5 | runtime | met | — | §4.5.8 PLY-50, L1170-1173: *"When a window declares **on-top**, the Player MUST present it also while an alternative presentation that starts within its span is active, composited over that presentation, within the device's capability and PLY-45. The inherited linear event executes with its base semantics."* | Q2 kept. |
| R40.6 | runtime | met | — | §4.5.8 PLY-51, L1174-1177: *"The Player MUST process the non-linear windows declared in an alternative presentation's MPD as that presentation's own: they are presented over its content, and PLY-48 to PLY-50 apply to them against the alternative presentations it triggers in turn."* | Q2 kept. |
| R40.7 | document | met | — | §4.6 DOC-26, L1512-1516: *"This specification MUST NOT add anything to the inherited linear events, or to their `EventStream`s, to carry it"*; §5.1.1 L2038: *"This specification adds no attribute to it and no element under it (DOC-26)."*; carrier weighed per 06 conventions §4.8.2 L1859 | Q2 n/a. `@linearRelation` appears only on `svta:` windows (schema L2833, L2847). |
| R40.8 | document | met | — | §4.8.3 L1879-1885: *"A Player of this specification does not execute a base event the base would execute. The departure is declared explicitly by the Publisher, who authored both the event and the window, on a construct this specification defines; and a Player that does not implement this specification, which does not recognise the window, executes the base event exactly as the base defines."*; DOC-3 L1400-1403 | Q2 n/a; source-has-no-modal. |
| R6#p1 | document | met | — | §4.6 DOC-28, L1524: *"This specification MUST specify how in-band ad tracking beacons are carried in the resolution document"*; carrier defined in §5.5, L2492: *"In-band ad tracking beacons ride the base callback scheme `urn:mpeg:dash:event:callback:2015` (DASH §5.10.4.5)."* | Q2 n/a |
| R6#p2 | runtime | met | — | §4.5.15 PLY-83, L1348: *"A Player MUST safely ignore unknown namespaces on tracking-related extension elements, under the base rules for elements and attributes it does not recognise."* | Q2 kept |
| R6.1 | document | met | — | §4.6 DOC-28, L1524-1525: *"This specification MUST specify how in-band ad tracking beacons are carried in the resolution document"*; §5.5.1 (List MPD sub-MPD) and §5.5.2 `<svta:Tracking>` (non-linear), L2490-2560. | Q2 n/a |
| R6.2 | runtime | met | — | §4.4 APS-16, L843-848: *"The APS SHOULD carry tracking beacons as `Event` entries of an event stream of scheme `urn:mpeg:dash:event:callback:2015`: in the sub-MPD of a List MPD candidate, and in the `<svta:Tracking>` element of an `<svta:Ad>`. The APS produces these entries by translating the tracking events the ADS declared."* | Q2 kept (SHOULD preserved). Non-linear carrier is `<svta:Tracking>` (an `EventStreamType` element), A-11. |
| R6.3 | document | met | — | §4.6 DOC-29, L1530-1532: *"A new tracking carrier MAY be introduced only when the callback scheme cannot express the required semantics, and only after a documented gap analysis; none is introduced."*; §4.8.2 L1864 gives the reasoning for `<svta:Tracking>`: *"The beacons reuse the callback scheme and the base `EventStreamType` whole."* | Q2 n/a. DOC-29 says no carrier is introduced while §4.8.2 lists `<svta:Tracking>` as introduced; A-11. |
| R6.4 | runtime | met | — | §4.5.15 PLY-83, L1348: *"A Player MUST safely ignore unknown namespaces on tracking-related extension elements, under the base rules for elements and attributes it does not recognise."* | Q2 kept |
| R6.5 | runtime | met | — | §4.5.15 PLY-81, L1334-1343: *"The de-duplication key for in-band beacons is scoped to **the candidate** that carries them in an `<svta:OverlayList>`: within a candidate, beacons sharing an `@id`, or the same URL at the same presentation time, fire once, and two beacons carrying the same `@id` in two different candidates are two distinct beacons that the Player MUST fire both. On a List MPD the base scope applies unchanged"* | Q2 kept. APS-side consequence stated only indicatively (L2514), EC-4. |
| R6.6 | runtime | met | — | §4.5.15 PLY-82, L1344-1347: *"The Player MUST resolve the presentation times of an `<svta:Tracking>` element against **that candidate's own presentation** — its time 0 is the instant the candidate begins rendering — and not against a `Period` the element does not sit in."* | Q2 kept |
| R6.7 | document | met | — | §4.6 DOC-30, L1533-1534: *"This specification MUST state how a resolution document carrying the candidate-level beacon carrier is validated (§5.10.2)."*; §5.10.2 L2914-2916: *"a validator that has not been given this specification's schema skips every `svta` element, and the tracking carrier inside it, and still reports the"* document valid, followed by the four validity conditions. | Q2 n/a |
| R13#p1 | document | met | — | §4.6 DOC-28, L1525-1528: *"and MUST define a mechanism that lets the ADS direct which beacons fire and at which points relative to the ad's presentation (§5.5). It prescribes no fractions, granularity or beacon count."* | Q2 n/a |
| R13.1 | runtime | met | — | §4.4 APS-16, L841-843: *"When the resolution document carries tracking instructions, the APS MUST express them as DASH callback events (§5.5), with timings relative to the ad's presentation timeline."* | Q2 kept. Spec narrows "callback events (or an equivalent baseline DASH construct)" to callback events only; compatible. |
| R13.2 | runtime | met | — | §4.5.15 PLY-79, L1328-1331: *"Given an ad accepted for rendering, the Player MUST execute the tracking schedule it reads from the resolution document, firing each beacon at its specified relative time. The ADS is the authority over the schedule; the Player decides neither which beacons fire nor when."* | Q2 kept |
| R13.3 | runtime | met | — | §4.5.15 PLY-80, L1332-1333: *"If the cap trims the ad before a scheduled beacon's time, the Player MUST stop firing the remaining beacons at the trim boundary."* | Q2 kept |
| R13.4 | document | met | — | §4.6 DOC-29, L1529-1530: *"This specification MUST NOT introduce a new tracking event scheme; it reuses the base callback scheme."*; §5.5 L2496-2497: *"No tracking scheme is introduced."* | Q2 n/a |
| R13.5 | scope | met | — | §1.3, L122-128: *"So are the fidelity of the tracking transcription (that the APS neither adds, removes nor reorders the beacons the ADS declared) and whether a ClickThrough the ADS declared reaches the resolution document at all: the ADS declares both and receives the resulting requests, so it is in a position to enforce them, and the resolution document is not, because it does not show what was declared."* | Q2 source-has-no-modal |
| R23.1 | document | met | — | §4.6 DOC-32, L1541-1544: *"This specification MUST define, in the namespace `urn:svta:dash:sgai:2026`, the elements that carry creative metadata with no native DASH carrier, and MUST state that emitting them and reading them are both optional (§5.7)."*; §5.7 defines `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>` (L2593-2595), schema L2870. | Q2 n/a |
| R24#p1 | runtime | met | — | §4.4 APS-11, L815-817: *"When a non-AV form (image, HTML) is carried, the asset URL MUST NOT be expressed as `@mimeType` on an `AdaptationSet` or `Representation` reached through any path bound by IETF RFC 4337."* | Q2 kept |
| R24#p2 | runtime | met | — | §4.4 APS-11, L817-820: *"It MUST be carried as an attribute of an element in the namespace `urn:svta:dash:sgai:2026` (`<svta:RenderableAsset>@src`, §5.3.2), which is carrier (a) of DR-6 (§4.7.1)."* | Q2 kept. Spec narrows "one of the DR-6 carriers" to carrier (a); choice justified in §4.8.2 L1863. |
| R24.1 | runtime | met | — | §4.4 APS-11, L815-820: *"the asset URL MUST NOT be expressed as `@mimeType` on an `AdaptationSet` or `Representation` reached through any path bound by IETF RFC 4337. It MUST be carried as an attribute of an element in the namespace `urn:svta:dash:sgai:2026`"*; DR-6 enumerated at L1640. | Q2 kept (spec-document half satisfied by the same passage and §4.8.2 L1863). |
| R33.1 | document | met | — | §4.6 DOC-33, L1545-1547: *"This specification MUST NOT define a metric of its own for pause-ad delivery; the quantity is derived from the base `PlayList` metric (§5.9)."*; §5.9 L2723: *"No metric is added (DOC-33)"*. | Q2 n/a |
| R33.2 | runtime | met | — | §4.5.18 PLY-88, L1374-1376: *"A Player that reports metrics MUST derive the paused interval from the `PlayList` entries as §5.9 describes, and MUST NOT count a playback period that stopped on `Rebuffering` as a pause opportunity."* | Q2 kept |
| R33.3 | scope | met | — | §4.6 DOC-33, L1547-1549: *"The transport by which any measurement reaches the Publisher, the APS or the ADS is out of scope, as it is for the base specification's own metrics."*; also §1.3: *"How a measurement reaches the Publisher, the APS or the ADS"*. | Q2 source-has-no-modal |
| R33.4 | runtime | met | — | §4.2 PUB-13, L708-711: *"Content carrying pause windows MUST request the `PlayList` metric through the base specification's `Metrics` element (DASH §5.9). Collection is triggered by the service provider, not by the Player"* | Q2 kept |
| R28#p1 | runtime | met | — | §4.4 APS-17, L849-851: *"When a candidate carries a ClickThrough, the ClickThrough URL and any click-tracking URL accompanying it MUST be carried in `<svta:ClickThrough>` (§5.6), and not elsewhere."*; §5.6 L2563-2564: *"`<svta:ClickThrough>` carries a candidate's ClickThrough URL and its click-tracking URLs together, so that every Player conformant to this"* specification reads the same two fields. | Q2 kept |
| R28.1 | runtime | met | — | §4.4 APS-17, L849-852: *"When a candidate carries a ClickThrough, the ClickThrough URL and any click-tracking URL accompanying it MUST be carried in `<svta:ClickThrough>` (§5.6), and not elsewhere. Whether a ClickThrough has click-tracking URLs is the advertiser's decision."* | Q2 kept |
| R28.2 | runtime | met | — | §4.5.16 PLY-84, L1354-1356: *"A Player conformant to this specification MUST read the ClickThrough URL of `<svta:ClickThrough>` and fire its associated click-tracking when the viewer activates the ClickThrough."* | Q2 kept |
| R28.3 | scope | met | — | §1.3, L124-128: *"and whether a ClickThrough the ADS declared reaches the resolution document at all: the ADS declares both and receives the resulting requests, so it is in a position to enforce them, and the resolution document is not, because it does not show what was declared."* | Q2 source-has-no-modal |
| R8.1 | document | met | — | §4.6 DOC-34, L1553-1554: *"Every new construct MUST be accompanied by an inline justification of why no existing base construct could be reused"*; property holds in §4.8.2 (L1850-1872), one row per introduced construct (schemes, windows, `@durationCap`, `@allowedLayouts`, `<svta:OverlayList>`, `<svta:Tracking>`, `<svta:ClickThrough>`, `@dismissAfter`, `@validFor`, etc.). | Q2 n/a |
| R8.2 | document | met | — | §4.6 DOC-34, L1555-1556: *"every deliberate omission of a base construct a reader might expect MUST be documented with the decision (§4.8)."*; property holds in §4.8.4 *Weighed, and not taken* (L1911-1964), e.g. `@selectionPriority`, `MPD@type="list"`, `RequestParam`, `@noJump`. | Q2 n/a |
| R9.1 | document | met | — | §4.6 DOC-35, L1557-1558: *"This specification MUST reuse existing base machinery — events, manifests, presentations, schemes — wherever possible."*; property holds in §4.8.1 *Reused unchanged* (L1831-1848). | Q2 n/a |
| R9.2 | document | met | — | §4.6 DOC-35, L1558-1560: *"A new construct MUST NOT be introduced unless an existing one cannot be made to fit"*; §4.8.2 heading L1850: *"Introduced, and why nothing existing fits"*. | Q2 n/a |
| R9.3 | document | met | — | §4.6 DOC-35, L1560-1562: *"before introducing one this specification MUST consider whether an extension of an existing construct would suffice, and record the outcome (§4.8.2, §4.8.4)."*; §4.8.2 column header: *"Why no base construct could be reused, or extended"*. | Q2 n/a |
| R10.1 | document | met | — | §4.6 DOC-22, L1495-1496: *"Spatial arrangement of overlays MUST be delegated to HTML5 / CSS layout primitives"*; §1.3 L131-132. | Q2 n/a |
| R10.2 | document | met | — | §4.6 DOC-22, L1496-1497: *"and this specification MUST NOT define a parallel layout standard for overlay placement."* Property holds: the only geometry is `custom` `@rect` (§5.3.5). | Q2 n/a |
| R10.3 | scope | met | — | §1.3, L133-137: *"defines no parallel layout standard and no position vocabulary inside a layout (left, right, top, bottom); where an ad sits inside its layout follows from the IAB ad type the layout token names. The one exception is the optional `custom` overlay layout (§5.3.5), whose rectangle is a position by definition."* | Q2 source-has-no-modal |
| OOS-1#p1 | scope | met | — | §4.6 DOC-22, L1496-1497: *"this specification MUST NOT define a parallel layout standard for overlay placement."*; §1.3 L131-133: *"Spatial arrangement of overlays is delegated to HTML5 and CSS, aligned with the IAB CTV guidelines."* | Q2 n/a (modal kept in DOC-22 anyway) |
| OOS-4#p1 | scope | met | — | §1.3, L138-141: *"raw JavaScript, SVG as payload, PDF, proprietary binary creatives. A sender that needs a scripted creative MUST wrap the script inside an HTML document and carry it as `text/html`."* | Q2 n/a (sender obligation keeps its MUST) |
| UC-01 | use-case | partial | 5.c | §7.2, L3102-3103: *"D1, D2 \| Plays the first renderable candidate on one decoder; a second decoder MAY pre-buffer the ad. Enforces the cap at playback."* / *"D3, D4, D5 \| The same on its single decoder: the linear ad and the primary content are sequential, not concurrent."*; A.6 L3877; against the Ad response: §4.8.4 L1963-1964: *"image or HTML alternatives for a linear slot are not carried in this edition."* | Q2 n/a. All five classes walked and matching the UC (pre-roll, first frame L3106). The UC's optional image / HTML fallback on a linear candidate cannot be expressed; spec self-flags it at §8.13 item 14 (L3657-3660). A-12. |
| UC-02 | use-case | partial | 5.c | §7.2, L3106-3107: *"and at or near the slot position for a mid-roll"*; B.8 L4122: *"D3, D4, D5 \| Plays the ad on its single decoder, the live channel having stopped being output."*; trick-play §7.20 and B.7 | Q2 n/a. All five classes walked, pre-buffer on D1/D2 (L3102), trick-play variant present. Same linear-fallback gap as UC-01 (§4.8.4 L1963-1964). A-12. |
| UC-03 | use-case | met | — | §7.4, L3133: *"D2 \| Renders a video option (second decoder); skips image and HTML options, which it cannot composite; a double box with a video ad and no background is renderable if admitted."*; C.6 L4288: *"D5 \| all fail \| all fail \| nothing \| nothing"* | Q2 n/a. D1–D5 present in §7.4 table and C.6, each as the UC states (D2 video or side-by-side, D3 HTML/image, D4 image, D5 decline). |
| UC-04 | use-case | met | — | §7.6, L3162: *"D3 \| Composites an image or HTML overlay on top: the linear ad holds the one decoder the primary content released (DASH §4.2), and the overlay needs one surface."*; D.7 L4548: *"D5 \| plays \| declined: no overlay surface"* | Q2 n/a. D1–D5 present in §7.6 and D.7; `on-top` declaration and its absence (PLY-49) walked at L3152-3176, as R40.4/R40.5 in the UC. |
| UC-05 | use-case | met | — | §7.7, L3188: *"D3 \| Renders an HTML or image option over the paused frame. It MAY instead release the primary content's decoder to play a video option (PLY-56), restoring the position on resume."*; E.6 L4704: *"D2 \| video fullscreen, second decoder over the held frame \| image: fails \| the video; then candidate 2 is skipped"* | Q2 n/a. D1–D5 present; live variant L3194-3195. The UC's "no maximum display duration" is honoured: the pause cap bounds one pass, not the slot (L988, L2113). |
| UC-06 | use-case | met | — | §7.3, L3118-3120: *"On every class the Player plays the candidates back to back in document order, reusing its decoder (D3 to D5) or pre-buffering the next ad on the second one (D1, D2)."*; F.7 L5041 | Q2 n/a. All classes; stop at cap even mid-ad (L3122); drop-before-play is R7.3, not a departure. |
| UC-07 | use-case | met | — | §7.16, L3389-3390: *"**Live content, or on-demand content with no fallback authored** — the primary content plays uninterrupted, no ad is shown, no error surfaces."*; G.10 L5283: *"D1 to D5 \| Plays the episode, the standard break at 900 s, and nothing non-linear. No error surfaces."* | Q2 n/a. Uniform across D1–D5 as the UC states; live and VOD branches (G.8) and supersede fallback walked. The v11.1 breaking passage in §4.7.7 is gone in v12 (C5 now "A legacy Player never issues the request", L1799-1800). |
| UC-08 | use-case | partial | 5.c | §7.8, L3216: *"D2 \| Overlay (video) suspended; a video pause ad shown on the second decoder if offered, else the paused frame stays clean; overlay restored."*; H.9 L5482: *"D5 \| none \| none \| none"*; spec self-flag §8.13 L3657-3658: *"overlay candidate could double as a pause candidate has no construct"* | Q2 n/a. D1–D5 present and as the UC states (suspend, pause ad, restore; branch B H.8). The UC's "unless the Publisher's MPD signals that the overlay candidate doubles as the pause-ad candidate" has no construct. A-13. |
| UC-09 | use-case | met | — | §7.9, L3240: *"D2 \| fails: background is an image \| fails: image creative \| fails: image \| satisfiable \| 4"*; I.6 L5657: *"D4 \| fails: needs 2 decoders \| passes \| — \| — \| 2 \| As D3. Had the creative been HTML, D4 would have skipped it and landed on option 3."* | Q2 n/a. D1→1, D2→4, D3→2, D4→2, D5→4, as the UC. The D4 aside says option 3 where the UC says option 4; the spec is correct under §3.6 and the UC parenthetical is wrong. A-14 (D-16). |
| UC-10 | use-case | met | — | §7.10, L3260: *"D2 \| declines: the background is an image \| declines \| declines"*; J.7 L5808: *"D2 \| fails: the background is an image \| fails: image \| fails: HTML \| fails: image \| nothing — the window presents no ad"* | Q2 n/a. D1–D5 present in §7.10 and J.7; with/without background (black) walked (L3253-3255, J.1). |
| UC-11 | use-case | met | — | §7.11, L3269-3272: *"every class opens the ClickThrough destination (or hands it off) and fires each click-tracking URL once (PLY-84). This is separate from the timeline beacons; the click has no presentation time."*; K.7 L5976: *"D1 to D5 read the carrier and fire the click identically."* | Q2 n/a. Class-independent as the UC states; legacy click inert (L3272, K.6). |
| UC-12 | use-case | met | — | §7.12, L3279-3281: *"The first answers with the empty document and the second with an ad: the first attempt failed, the second is attempted, the viewer sees the second's ad."*; L.8 L6145: *"Choosing the window is device-agnostic: D1 to D5 walk the chain identically."* | Q2 n/a. The UC's three paths walked (§7.12, L.4) plus a fourth (unrenderable candidates, PLY-41, L3287-3289) that follows R20.1 but reads against the UC's "whatever its shape" wording. A-15 (D-17). |
| UC-13 | use-case | met | — | M.7 L6396: *"D4 \| all four \| walks: 1 fails (2 decoders), 2 passes \| L-shape \| yes"*; M.3 L6211: *"the HTML axis is omitted: the Player cannot determine it when it issues the request, and sends nothing rather than an empty value (PLY-13)."* | Q2 n/a. D1–D5 present in M.3/M.4/M.7, each as the UC (D3 omits HTML axis, D4 declares nothing, APS conservative on undetermined axis). |
| UC-14 | use-case | met | — | §7.14, L3340-3342: *"The overlay window is declared in the **slate's** MPD, over the slate's timeline (PUB-12, PLY-51)."*; table L3350-3353 (*"D2 \| Composites a video overlay; declines image and HTML."* … *"D5 \| Declines."*) plus Legacy row; N.6 L6587: *"D2 \| declined: both options are non-video surfaces"* | Q2 n/a. NOT gap: v12 walks UC-14 in §7.14 and Annex N with D1–D5 and the legacy Player, optional `@maxDuration` (L3342-3344), and the three primary-timeline relations (L3356-3360, N.7). The prompt's "UC-14 must be gap" acceptance test is stale. |
| UC-15 | use-case | met | — | §7.15, L3368-3371: *"D1, D3 and D4 render an image L-shape; D2 and D5 have no renderable allowed layout and skip. The full-screen takeover a D2 could have played is not offered, because the Publisher excluded it."*; O.6 L6728 | Q2 n/a. D1–D5 present as the UC; non-conforming APS walked (O.7). |
| UC-16 | use-case | partial | 5.c | P.6 L6863: *"D2, D5 \| neither image option renders; skips"*; §7.15 L3378: *"D5 skips as in every overlay case."* | Q2 n/a. Supporting / non-supporting Player and D5 as the UC states; D2 skips, where the UC coverage cell gives D2 "same" as D1. Divergence comes from the annex's image-only forms, which the UC does not fix; spec self-flags at L3659-3660 (§8.13 item 14). A-16. |
| UC-17 | use-case | met | — | §7.13, L3328: *"D2 \| No option renderable; the break executes."*; Q.5 L7058: *"D2 \| neither option renders: no ad \| executed at 15:00 \| a 30-second full-screen break; the programme resumes at 15:00"* | Q2 n/a. D1–D5 and legacy present as the UC; failure branch (Q.6, L3333-3335) and early resolution with forwarded layouts (Q.5) walked. |

## Disposition of findings

### 5.a Actionable TODOs (0)

No finding qualifies. There is no `[inferred]`, `TODO`, `FIXME` or `[?]`
marker in the spec (the search matches only the definition of
`[inferred]` at L23, which shows it finds the marker when present). The
two `contradicted` rows (R7#p2, R7.4) come from two spec sites that
disagree, but `context/` backs both readings (`02-actors.md` L177-180
for PLY-1, R7.4 for PLY-36), so criterion 3's "exactly one reading
matches `context/`" does not hold and the tie-breaker sends them to 5.b.

| #  | Finding ref | Criterion | Spec section | Concrete edit | Citation |
|----|-------------|-----------|--------------|---------------|----------|

### 5.b Flagged for review (10)

| #  | Finding ref | Spec section | Why uncertain | Resolutions considered |
|----|-------------|--------------|---------------|------------------------|
| F-1 | R7#p2, R7.4, A-1 | PLY-1 (L882-883), PLY-36 (L1054-1055) | The spec both permits and forbids Player ranking/deduplication; `context/` carries both readings. | (1) Delete "(ranking, deduplication)" from PLY-1, aligning with R7.4; (2) keep client-side selection and narrow PLY-36 — requires amending R7.4 (D-4). |
| F-2 | R37.3 | §4.5.10 (L1200 ff.), §5.3.7 (L2455), PLY-61 | R37.3's reading rule (a criterion that appears to assume one pause mechanism is read per R37) has no counterpart, while several passages assume a held frame. | (1) Add one sentence restating R37.3 after PLY-59; (2) reword the held-frame passages to be mechanism-neutral. |
| F-4 | R11.4, G-4 | DOC-10 (L1440-1443), §6.6 (L3055-3080) | Covering verification and icons is authoring with design choices; declaring them not carried may itself breach R11.4's last sentence. | (1) Add §6.6 rows carrying `<AdVerifications>` and `<Icons>` (e.g. via §5.7 metadata or a new element); (2) declare them not carried and record the narrowing in `context/`. |
| F-5 | EC-1 | §5.2.5 (L2305-2312), PLY-9 (L908) | Which instant a lifetime runs from, for a document requested at fire time. | (1) Exempt documents requested at or after the fire instant; (2) define `PT0S` as "usable for the opportunity that caused the request". |
| F-6 | EC-2 | PLY-74, PLY-75 (L1293-1303), §5.2.4 | Which `@dismissAfter` governs a slot spanning two documents or passes. | (1) The first document's declaration holds for the pause; (2) each document's own, restarted on arrival; (3) restarted per `repeat` pass. |
| F-7 | EC-3 | PLY-52 (L1181-1184), §7.8 (L3216) | Overlay state during a pause with no pause ad. | (1) Suspended for the whole pause, as §7.8 walks; (2) suspended only while a pause ad is on screen. |
| F-8 | EC-4 | §5.5.1 (L2511-2515), APS-16 (L841-848), Annex R (L7145) | A test with no criterion behind it; the remedy is a choice about the APS contract. | (1) Add to APS-16 an obligation of distinct `@id` across the List MPD; (2) drop the Annex R check. |
| F-9 | EC-5 | §5.8.1 (L2611-2613), §5.8.4 (L2665), §4.7.7 (L1802-1803) | The reservation binds no one; two defensible fixes. | (1) PUB criterion: the `@uri` query carries no `sgai-` name; (2) define which occurrence the APS reads. |
| F-10 | A-11 | DOC-29 (L1530-1532), §4.8.2 (L1864) | Aligning either site changes what R6.3 is claimed to permit. | (1) Drop "none is introduced" and justify against R6.3; (2) state in DOC-29 that hosting under the SVTA name is not a new carrier (and in `context/`). |

### 5.c Deferred to context/ (19)

Ordered by leverage. The prompt asks for the top 3-5; every row is listed
because each routes a coverage row or a finding that must be routed (§5,
items 1 and 2).

| #  | Finding ref | `context/` file to edit | Suggested edit | Leverage rationale |
|----|-------------|-------------------------|----------------|--------------------|
| D-1 | G-1 | `03-requirements.md` (R4, R4.1, R4.2, R31.2), `04-use-cases.md` (UC-05) | Say what the required pause cap bounds (one pass through one document's candidates, reset per pass), or drop the requirement for pause windows. | Every pause window carries a mandatory value whose meaning is the spec's invention; PLY-24, PLY-32 and `repeat` rest on it. |
| D-3 | G-3, R1.2 | `03-requirements.md` (R1.2), `08-dash-extension-rules.md` | "The enumeration governs constructs placed in a document a Player that does not implement this specification reads; a document reached only through a construct such a Player ignores is outside it." | A literal R1.2 rejects the whole non-linear resolution path. |
| D-2 | G-2 | `03-requirements.md` ("Deliberately open") | Record each §8.13 question as deliberately open, or answer it. | Fourteen answers an implementer needs are unowned silences. |
| D-4 | A-1 (companion of F-1) | `02-actors.md` (L177-180) | "The Player may drop candidates that fail validation or that it cannot render (R7.2, R7.3); it does not re-order or deduplicate the remaining ones (R7.4)." | Removes the source of the only `contradicted` rows. |
| D-9 | R17.5, A-9 | `03-requirements.md` (R17.5) | Restrict to pause windows R40 makes applicable to the linear presentation. | Direct conflict between two requirements. |
| D-10 | R40.1, A-10 | `03-requirements.md` (R40.1) | Admit only on top on a pause window. | The spec already withdraws the permission; `context/` still grants it. |
| D-7 | R1.5, A-4 | `03-requirements.md` (drop-before-play criterion, R20.1) | Record each as an exception to R1.5 with its reason, or state why it is not a departure. | R1.5 requires departures to be recorded; the spec has two it does not list. |
| D-5 | A-2 | `03-requirements.md` (R2.2) | "…on the ADS, nor on the APS beyond the layouts and region it receives on the resolution request (R38.4, R39.4)." | R2.2 literally contradicts two APS criteria. |
| D-6 | A-3 | `03-requirements.md` (R40.8 or R1.3) | State that supersede is not an alteration under R1.3, or that R1.5 exceptions are not alterations. | R1.3 is absolute and the spec relies on an unwritten exception. |
| D-8 | A-7 | `03-requirements.md` (R34.2) | "…pause ads during at most one qualifying pause…; within that pause R32 applies as usual." | Two readings change what the viewer sees in the first pause. |
| D-11 | UC-01, UC-02, A-12 | `04-use-cases.md` (UC-01, UC-02) | "Each candidate is a video form; this edition carries no non-video fallback on a linear candidate." | Two core linear cases describe a response the spec cannot express. |
| D-12 | UC-08, A-13 | `04-use-cases.md` (UC-08) | Strike the "unless … doubles as the pause-ad candidate" clause, or add a requirement for it. | A use case names a capability no requirement carries. |
| D-18 | UC-16, A-16 | `04-use-cases.md` (UC-16, coverage L94) | Name the forms; set D2 to "skip (no non-video surface)". | Coverage table and the spec's walk disagree on D2. |
| D-15 | A-8 | `03-requirements.md` (R26.1) | "…of the presentation option whose layout is the double box with background…". | Keeps a future build from moving it into the MPD. |
| D-13 | A-5 | `03-requirements.md` (R12.4) | Name R39's `custom` region as the one exception. | Low; the spec already follows R39. |
| D-14 | A-6 | `03-requirements.md` (R7.2) | "Dropping a candidate R5.3 requires skipping does not breach R7.1." | Low; no behavioural divergence. |
| D-16 | A-14 | `04-use-cases.md` (UC-09, D4, L1127-1128) | "landed on option 3, the image banner". | Corrects a walk that contradicts the device model. |
| D-17 | A-15 | `04-use-cases.md` (UC-12 L1355, coverage L84) | "produces no ad" → "obtains no resolution document carrying candidates". | Low; the spec follows R20.1. |
| D-19 | A-17 | `03-requirements.md` (the 22 criteria of A-17) | Add the modal to each indicative obligation (R4.7, R37.3 at least). | Question 2 cannot be checked for 22 criteria. |

### Audit and detail-review items

§5 items 3 and 4 require routing every `Non-conforming` and `Marginal`
item of `v12-dash-conformance-audit.md` and every flag of
`v12-detail-review.md`. Neither sidecar existed in `output-analysis/`
when this validation was written (`ls output-analysis/v12*` matched only
this file), so there is nothing of v12 to route. The v11.1 sidecars
analyse another candidate and are not routed here.

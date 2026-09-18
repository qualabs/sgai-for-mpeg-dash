[GROUNDED_BY=spec-only]

# Conformance assertions

Every RFC 2119 obligation in `context/`, normalised to one row per
testable assertion. Chapter 10 (Test cases) absorbs this table
directly: each row is one test.

Actors are the four of the model (`../context/02-actors.md`) —
**Publisher**, **ADS**, **APS**, **Player** — plus `spec document`
for document-level obligations and `all` for an assertion binding
two or more runtime actors at once. When a source criterion labels
itself with one runtime actor plus `spec document`, the Actor cell
carries the runtime actor if the obligation is checkable on that
actor's artefact, and `spec document` otherwise.

Assertion IDs inside `../context/03-requirements.md` reuse the
`R<N>.<n>` conformance-criterion ID verbatim. Obligations in that
same file that sit **outside** a `Conformance criteria` block carry
`DP03` (design principles) or `P03` (requirement-body prose and the
Out of Scope list). Assertions in the other files carry a per-file
prefix: `IN01` (`01-intro.md`), `A2` (`02-actors.md`), `UC04`
(`04-use-cases.md`), `I05` (`05-dash-linear-interfaces.md`), `N06`
(`06-naming-and-namespaces.md`), `B07`
(`07-backward-compat-checklist.md`), `D08`
(`08-dash-extension-rules.md`), `G99` (`99-glossary.md`).

**Splitting rule.** A declared criterion that imposes two obligations
differing in actor, in triggering condition, or in what they oblige is
**two assertions** and is carried as two rows, suffixed `a` / `b` / `c`
on the criterion ID (`R20.1a`…`R20.1d`). The suffix is an index into
one criterion, never a new criterion: `R20.1a` and `R20.1b` are both
`R20.1` in `context/`. 123 criteria are declared in
`context/03-requirements.md`; they yield 145 rows.

**Folding rule.** A sentence that restates an obligation already
carried by another sentence **in the same file** is folded into one
row; every folded line is listed below so nothing disappears
silently. A restatement in a **different** file keeps its own row,
because the per-source-doc count (§3) and the orphan analysis (§4)
depend on knowing which file carries the obligation.

Folded restatements — `03-requirements.md`: requirement-body prose at
`:113`, `:116`, `:117`, `:157`, `:185`, `:188`, `:189`, `:237`,
`:240`, `:297`, `:592`, `:594`, `:612`, `:613`, `:663`, `:666`,
`:668`, `:676`, `:922`, `:953`, `:956`, `:966`, `:999`, `:1030`,
`:1093`, `:1136`, `:1381`, `:1427`, `:1429`, `:1434`, `:1436`,
`:1483`, `:1552`, `:1554`, `:1638`, and OOS-1 at `:1745`, all restate
a criterion of their own requirement. `04-use-cases.md`: `:847`
restates `:804`, `:1184` restates `:1175`.
`05-dash-linear-interfaces.md`: `:434` and `:467` restate `:435`.
`08-dash-extension-rules.md`: the DR-7 heading at `:190` and `:196`
restate `:209`.

Excluded, with reason: `03-requirements.md:45`, `:49`, `:54`, `:55`
(DP-2 prose quoting the words MUST / MUST NOT to illustrate an
authoring style, not to impose an obligation); `:1407` (a permission
granted to a *future* edition, binding nothing in this one);
`06-naming-and-namespaces.md:153` (a normative preference — "the
preferred encoding is…" — carrying no RFC 2119 keyword; see §5).

**Two rows are flagged `[CONTRADICTION]`.** `context/03-requirements.md`
states two incompatible outcomes for a well-formed resolution document
that carries no candidates. The rows below follow R20.1 and R30, which
are the normative criteria and implement accepted ADR 0011; R20.4's
RATIONALE prose (`:1354`-`:1362`) asserts the opposite and is stale.
See §5.

| Assertion ID | Source | Actor | Condition | Obligation |
|--------------|--------|-------|-----------|------------|
| DP03.1 | context/03-requirements.md:24 | spec document | Given a construct being authored | MUST NOT carry information already determined by its own context — its element name and namespace, its parent construct, or another attribute on the same construct. |
| DP03.2 | context/03-requirements.md:30 | spec document | Given a construct justified only by a possible future relaxation | MUST NOT be introduced. |
| DP03.3 | context/03-requirements.md:33 | spec document | Given a construct whose only admissible value matches its own default OR is fixed by another rule | MUST NOT exist in the spec. |
| DP03.4 | context/03-requirements.md:40 | spec document | Given the same value or relationship appearing in several places in the spec or in a generated MPD | Exactly one declaration is canonical and the others MUST be derived from it at runtime, not duplicated in the markup. |
| DP03.5 | context/03-requirements.md:61 | all | (unconditional) | Applying this specification MUST NEVER break primary-content playback; when an opportunity cannot be honoured, graceful skip-and-continue is mandatory. |
| R1.1 | context/03-requirements.md:125 | Player | Given an `MPD` carrying an SGAI construct the Player does not implement | MUST ignore the unknown construct and continue playing the primary content uninterrupted. |
| R1.2a | context/03-requirements.md:129 | spec document | Given a new SGAI construct introduced by this proposal | MUST be expressed using one of the extension points enumerated in `08-dash-extension-rules.md` — foreign-namespace open content (§5.2.1, DR-2 / DR-3), application-level Event Streams (§5.10), or vendor descriptor schemes (§5.8.4.8 / §5.8.4.9). |
| R1.2b | context/03-requirements.md:135 | spec document | Given a new SGAI construct introduced by this proposal | MUST NOT be introduced by a path that violates the §5.3.2.6 / §8.15 / §7.3 / RFC 4337 chain when reached via `<ImportedMPD>` (DR-1), nor by inline AdaptationSet / Representation under a ListMPD-level Period (DR-5). |
| R1.2c | context/03-requirements.md:138 | spec document | Given a construct that invokes Annex F (DR-4) | Admissible only when the construct genuinely requires DASH segment-delivery semantics for a non-ISO-BMFF format AND the spec is willing to publish a new Interoperability Point URI. `[no RFC 2119 keyword]` |
| R1.3 | context/03-requirements.md:143 | spec document | (unconditional) | MUST NOT alter or override the semantics of any pre-existing MPEG-DASH 6th edition construct. |
| R1.4 | context/03-requirements.md:146 | Player | Given resolving or rendering an accepted ad fails at runtime (decode error, malformed candidate, mid-ad network loss) | MUST abort that ad and continue playing the primary content uninterrupted. |
| R2.1 | context/03-requirements.md:165 | Publisher | Given constraints applicable to an ad slot (max duration, opt-in policies, layout templates) | MUST be declared by the Publisher in the `MPD`, not inferred at runtime by the ADS, the APS or the Player. |
| R2.2a | context/03-requirements.md:169 | ADS | Given an ad opportunity to fill | MUST decide which ads to serve and output them as its decision document (typically VAST). |
| R2.2b | context/03-requirements.md:170 | APS | Given the ADS's decision document | MUST convert it into the resolution document carrying the ad candidates. |
| R2.2c | context/03-requirements.md:172 | ADS + APS | Given a Publisher-declared constraint such as the slot duration cap | Neither MUST be expected to enforce it. `[RFC 2119 misuse — see §5]` |
| R2.3 | context/03-requirements.md:174 | Player | Given the candidates in a resolution document | MUST validate them against the Publisher-declared constraints and render only those that satisfy them. |
| R2.4 | context/03-requirements.md:177 | spec document | Given every new mechanism the specification introduces | MUST be expressible within the four-actor contract; a mechanism that would require an actor to take on a responsibility outside its role MUST be rejected or redesigned. |
| R11.1 | context/03-requirements.md:193 | spec document | Given the normative chapters of the spec | MUST NOT cite a specific VAST version as required. |
| R11.2 | context/03-requirements.md:195 | Player | (unconditional) | MUST be able to operate regardless of whether the ADS uses VAST; the Player reads only the resolution document the APS produces. |
| R11.3 | context/03-requirements.md:203 | spec document | Given any reference to VAST in the spec | MUST be in an annex or in a non-normative note explicitly flagged as illustrative. |
| R18.1 | context/03-requirements.md:225 | spec document | (unconditional) | The specification documents the MPD event URL pattern (Player-visible input, served by the APS) and the resolution document format (Player-visible output, produced by the APS). `[no RFC 2119 keyword]` |
| R18.2 | context/03-requirements.md:229 | Publisher + ADS + APS | Given the APS-to-ADS contract for ad-decisioning invocation | Established and maintained by those parties directly, outside this specification; the Publisher-APS arrangement for the event URL stays bilateral except for the R29 parameters. `[no RFC 2119 keyword]` |
| R29.1 | context/03-requirements.md:251 | spec document | Given the reserved capability parameters | They are inputs about the device, not conclusions about which ad experiences can be served; the specification reserves a set, not a single value. `[no RFC 2119 keyword]` |
| R29.2 | context/03-requirements.md:258 | Player | (unconditional) | Sending a reserved parameter is OPTIONAL; a conformant Player MAY send all of them, some of them, or none. |
| R29.3 | context/03-requirements.md:261 | Player | Given the Player has no value for a reserved parameter, or does not disclose it | MUST omit that parameter entirely rather than send it with an empty or placeholder value. |
| R29.4 | context/03-requirements.md:265 | Player | Given a parameter on the resolution request that is not one of the reserved names | MUST carry a vendor-specific prefix so a reserved name added in a later edition cannot collide with it. |
| R29.5 | context/03-requirements.md:268 | APS | Given a resolution request missing any or all reserved parameters | MUST tolerate the absence and MUST be able to produce ad candidates without receiving any of them. |
| R29.6 | context/03-requirements.md:272 | spec document | Given the device classes the specification enumerates (R3.1) | The reserved set MUST be able to express the capability axes that distinguish them; a set that cannot tell two enumerated classes apart does not satisfy this. |
| R29.7 | context/03-requirements.md:276 | spec document | Given a reserved parameter absent from the resolution request | Its value is undetermined; absence does NOT assert that the device lacks the capability, and how an APS resolves an undetermined value is not defined here. `[no RFC 2119 keyword]` |
| R4.1 | context/03-requirements.md:349 | Publisher | Given any ad slot, linear or non-linear, defined in the `MPD` | MUST declare a maximum duration on it. |
| R4.2 | context/03-requirements.md:352 | Player | Given a family where the cap bounds cumulative duration (the non-linear families, and linear insertion) | MUST stop rendering once the cumulative duration of the accepted candidates would exceed the cap, even if the stop falls mid-ad. |
| R4.3 | context/03-requirements.md:356 | Player | (unconditional) | MUST NOT extend a slot beyond what the cap bounds for that slot's family (R4.6), regardless of ADS metadata or candidate count. |
| R4.4 | context/03-requirements.md:362 | ADS | Given the cumulative duration of the ADS's returned candidates exceeds the cap | A conformance check on the ADS MUST NOT fail solely for that reason. |
| R4.5 | context/03-requirements.md:366 | Player | Given an accepted candidate whose actual rendered length exceeds its declared duration | MUST enforce the cap against actual length, not declared length ("trim during play"). |
| R4.6 | context/03-requirements.md:370 | Player | Given an inherited linear replacement slot | MUST honour the base specification's clip semantics: unless the event declares otherwise the presentation ends at the scheduled end of the slot and a late start shortens it rather than moving that end. |
| R4.7 | context/03-requirements.md:376 | Publisher + Player | Given a declared cap of zero | The opportunity does not fire; the event is not executed (§5.16.5). A zero cap is not a very short slot. `[no RFC 2119 keyword]` |
| R4.8 | context/03-requirements.md:381 | spec document | Given the base specification treats an absent `@maxDuration` as infinity | R4.1's mandatory cap is a deliberate profile-style narrowing (§8.1), recorded so a reader who finds the unbounded default knows it was excluded on purpose. `[no RFC 2119 keyword]` |
| R4.9 | context/03-requirements.md:390 | Player | Given a cap in units of the parent `<EventStream>@timescale` and a candidate duration as an ISO 8601 `xs:duration` | MUST convert the candidate's duration into the cap's timescale before comparing, and MUST round the converted value up to the next whole unit; a converted duration equal to the cap is admitted. |
| R4.10 | context/03-requirements.md:398 | Player | Given a slot declaration carrying no maximum duration | MUST NOT present ads from that slot and MUST continue with the primary content; reading the absence as the base specification's unbounded default is not admissible. `[provisional — open with the working group]` |
| R4.11 | context/03-requirements.md:414 | Player | Given an interval during which the presentation timeline does not advance (a form suspended under R17 while the viewer is paused) | The interval does not accrue against the cap, and the form resumes with the remaining cap it had when suspended. `[no RFC 2119 keyword]` |
| R31.1a | context/03-requirements.md:438 | Player | Given a viewer pause that begins inside a pause opportunity window | MUST request a resolution document. |
| R31.1b | context/03-requirements.md:440 | Player | Given a viewer pause that begins outside every pause opportunity window | MUST NOT request a resolution document. |
| R31.2 | context/03-requirements.md:442 | Publisher + Player | Given a pause slot | The Publisher-declared slot cap (R4) MUST NOT be interpreted as bounding its duration; there is no authored duration for it to bound. |
| R12.1a | context/03-requirements.md:521 | spec document | Given an ad-type or visual-placement value | The spec MUST NOT accept a value outside the enumeration of R12 (linear, overlay with corner / lower-third, squeezeback with L-shape / double-box, pause with `pause-fullscreen` / `pause-partial`). |
| R12.1b | context/03-requirements.md:524 | spec document | Given each accepted ad-type or placement value | MUST cite the IAB source that defines it. |
| R12.2a | context/03-requirements.md:525 | Publisher | Given a Publisher declaring allowed layouts on a slot | MUST use names drawn from the enumerated set, each mapping 1:1 to an IAB-defined ad type or visual placement. |
| R12.2b | context/03-requirements.md:527 | Publisher | Given a Publisher-private layout name, or an IAB value outside the enumerated set | MUST NOT appear in the allowed-layouts declaration on the slot. |
| R12.3 | context/03-requirements.md:530 | APS | Given form metadata for an ad type or visual placement outside the enumerated set | MUST NOT be emitted in the resolution document; conformance is checked against the APS's resolution document, not the ADS's decision document. |
| R12.4 | context/03-requirements.md:535 | spec document | Given an enumerated layout | It implies the spatial bound the IAB CTV Ad Format Guidelines declare for that layout, inherited by normative reference; no dimensional attribute is introduced on the slot declaration. `[no RFC 2119 keyword]` |
| R15.1a | context/03-requirements.md:557 | spec document | Given any place where creative carrier types are discussed | MUST enumerate exactly the admissible set: video, image, HTML. |
| R15.1b | context/03-requirements.md:559 | spec document | Given an annex, example or implementation note | A new carrier type MUST NOT be added there. |
| R15.2 | context/03-requirements.md:561 | Publisher + APS | Given an ad candidate in the resolution document, or a form declared by the Publisher | MUST carry a creative whose mimeType falls under one of the three admissible categories. |
| R15.3 | context/03-requirements.md:569 | Player | Given a candidate whose creative carrier mimeType is not in the admissible set | MAY skip that candidate; it signals a non-conformant ADS, APS or Publisher. |
| R5.1 | context/03-requirements.md:622 | APS | Given each ad candidate in the resolution document | MUST carry one or more renderable presentation options (each a form plus its layout) as an ordered list whose document order is the preference order; no maximum, and no minimum beyond one. |
| R5.2 | context/03-requirements.md:630 | Player | Given an accepted candidate with presentation options | MUST evaluate the options in document order and render the first one whose form and layout it can satisfy on its device. |
| R5.3 | context/03-requirements.md:634 | Player | Given a candidate carrying no form renderable on the device | MUST skip it and fall through to the next candidate; when the candidates are exhausted the Player MUST continue with the primary content. |
| R5.4 | context/03-requirements.md:638 | ADS + APS | Given the production of ad candidates | Neither MUST be required to maintain a device-class matrix or a per-Player capability view. `[RFC 2119 misuse — see §5]` |
| R5.5 | context/03-requirements.md:641 | APS | Given one ad candidate | MAY carry multiple presentation options, each pairing a form with an admissible layout, as a single ordered list whose document order is the preference order. |
| R5.6 | context/03-requirements.md:645 | Player | Given the presentation options of a candidate | MUST walk them in document order, checking each against device capabilities AND the Publisher-declared allowed layouts, and render the first that satisfies both; an option failing either MUST NOT be rendered. |
| R5.7 | context/03-requirements.md:652 | Player | Given no presentation option on a candidate satisfies R5.6 | MUST skip that candidate and fall through to the next in the resolution document preserving R7's order, or to the primary content when exhausted. |
| R7.1 | context/03-requirements.md:685 | Player | Given a resolution document with more than one ad candidate | MUST play the candidates in the order the resolution document declares, except for candidates dropped under R7.2 or R7.3. |
| R7.2 | context/03-requirements.md:689 | Player | Given a candidate with no form renderable on the device (R3 / R5) | MAY drop it. |
| R7.3 | context/03-requirements.md:691 | Player | Given a candidate whose declared duration would push the cumulative slot duration past the cap (R4) | MAY drop it before playback ("drop before play"). |
| R7.4 | context/03-requirements.md:694 | Player | Given the candidates remaining after R7.2 / R7.3 | MUST NOT re-order, deduplicate or otherwise rearrange them. |
| R7.5 | context/03-requirements.md:697 | Player | Given an accepted candidate whose actual rendered length exceeds the cap | MUST trim mid-rendering ("trim during play") per R4. |
| R30.1 | context/03-requirements.md:755 | APS | Given an opportunity that resolved with no ads | MUST be expressed as a well-formed resolution document carrying no candidates, and MUST NOT be expressed as an error response or as a response without a body. |
| R30.2 | context/03-requirements.md:759 | Player | Given a resolution carrying no candidates | MUST NOT count it as an execution of the opportunity; where the event carries `@executeOnce="true"` the event remains executable afterwards (§5.16.2.2.2, §5.16.2.2.6 NOTE 3). `[CONTRADICTION — see §5]` |
| R3.1 | context/03-requirements.md:786 | spec document | (unconditional) | MUST enumerate the supported device classes and, for each class, the expected behaviour for every ad opportunity type covered by the use cases. |
| R3.2 | context/03-requirements.md:789 | Player | Given any supported device class and any ad opportunity type defined in the spec | MUST produce a defined behaviour (render, fall back, or skip); undefined behaviour is non-conforming. |
| R3.3 | context/03-requirements.md:793 | Player | Given an ad form (video, image, HTML) the device class cannot render | MUST NOT attempt to render it. |
| R16.1 | context/03-requirements.md:813 | Player | Given a pause-to-play transition by the viewer | MUST remove any rendered pause-ad form from the screen within one rendering frame. |
| R16.2 | context/03-requirements.md:816 | Player | Given the same pause-to-play transition | MUST cease firing tracking beacons scheduled for the dismissed pause-ad. |
| R32.1a | context/03-requirements.md:853 | APS | Given a resolution document for a pause slot | MUST declare which of the three exhaustion behaviours applies: repeat, request-again, or stop. |
| R32.1b | context/03-requirements.md:854 | Player | Given a resolution document for a pause slot carrying no exhaustion declaration | MUST apply `stop`. |
| R32.2 | context/03-requirements.md:856 | Player | Given `request-again` and a new resolution document that carries no candidates (R30) | MUST treat it as `stop` for the remainder of that pause. |
| R32.3 | context/03-requirements.md:859 | Player | Given the viewer resumes playback during a pause slot | MUST return to the primary content immediately, whether or not an ad is mid-presentation. |
| R32.4 | context/03-requirements.md:862 | spec document | Given a second resolution request inside one pause | Whether it is the same opportunity or a new one is out of scope; the two readings are identical at the Player and differ only in APS-to-ADS accounting (R18). `[no RFC 2119 keyword]` |
| R34.1 | context/03-requirements.md:903 | Publisher | Given a pause opportunity window | MAY declare it once-per-session; the declaration is optional and a window without it yields a pause ad on every qualifying pause. |
| R34.2a | context/03-requirements.md:907 | Player | Given a window declared once-per-session | MUST present at most one pause ad for that window for the duration of the session. |
| R34.2b | context/03-requirements.md:909 | Player | Given a later qualifying pause inside a once-per-session window already consumed | MUST leave the primary content uninterrupted. |
| R34.3 | context/03-requirements.md:911 | Player | Given a pause inside a once-per-session window | The window is consumed when a pause ad begins rendering and not when the pause occurs; a pause that resolves to no renderable candidate leaves the window available. `[no RFC 2119 keyword]` |
| R34.4 | context/03-requirements.md:914 | spec document | (unconditional) | The once-per-session capability is recorded as the pause family's counterpart of the base specification's single-execution bound, not as a new kind of control. `[no RFC 2119 keyword]` |
| R19.1 | context/03-requirements.md:935 | Player | Given any ad form, linear or non-linear, at the moment it is presented | MUST render it at the same playback speed as the primary content. |
| R19.2 | context/03-requirements.md:938 | Player | Given the primary content playing at a speed other than 1x | MUST NOT force the ad to 1x; the ad follows the primary content's speed. |
| R19.3 | context/03-requirements.md:941 | Player | Given an ad form's declared duration | MUST compute the effective on-screen wall-clock duration as `duration / playback_speed`, while cap enforcement (R4) and beacon scheduling (R13) operate on the presentation-timeline `duration`. |
| R19.4 | context/03-requirements.md:947 | Player | Given a form with no intrinsic media (`image`, `html`) | MUST treat its declared duration as a presentation-timeline value and derive its wall-clock length as `duration / playback_speed`, exactly as for a media-backed form. |
| R21.1a | context/03-requirements.md:985 | Player | Given a pause-ad form to present | MAY present it fullscreen, occupying the entire screen surface, or as a partial overlay composited over the paused primary frame. |
| R21.1b | context/03-requirements.md:988 | Player | Given a fullscreen pause-ad | MAY release the resources held by the primary content and by any pre-existing overlay in order to present a fullscreen video, image or web page. |
| R21.1c | context/03-requirements.md:990 | Player | Given a partial-overlay pause-ad | MUST keep at most one non-linear ad form active during the pause (R22); any coexisting overlay is suspended while the pause-ad is shown (R17). |
| R25.1a | context/03-requirements.md:1016 | Player | Given live content and a viewer paused inside a pause-ad window | MUST keep its presentation time frozen inside that window for the full duration of the pause, regardless of the live edge advancing in wall-clock time. |
| R25.1b | context/03-requirements.md:1020 | Player | Given a decision to resume at the live edge | MUST treat it as a Player action occurring after the resume from pause, outside the pause-ad window. |
| R26.1 | context/03-requirements.md:1045 | Publisher + APS | Given the background element of a side-by-side / double-box layout | MUST be carried as a composition attribute of the slot / layout, not as a separate presentation option (R5). |
| R26.2a | context/03-requirements.md:1048 | Player | Given a side-by-side / double-box layout | MUST composite the primary content and the ad as the two boxes of the layout. |
| R26.2b | context/03-requirements.md:1050 | Player | Given the advertiser supplies a background element | MUST place it in the uncovered bands; where the advertiser supplies none the uncovered region renders as black. |
| R26.3a | context/03-requirements.md:1062 | Player | Given a side-by-side layout whose ad is a video (two concurrent video decoders plus an image surface) | MUST NOT be selected on a single-decoder device (R3 / R5). |
| R26.3b | context/03-requirements.md:1068 | Player | Given a non-video element — the ad as image or HTML, or the image background | MUST NOT be selected on a device that cannot composite that surface type on top of video (e.g. an image background on a video-only-overlay device such as D2). |
| R27.1 | context/03-requirements.md:1101 | Publisher + APS | Given an L-shape / squeezeback presentation option | MUST carry exactly one ad creative — the full-frame background creative — as an image, a video or a web/HTML surface (R15); the shrunk primary content is not a creative the ADS / APS supplies. |
| R27.2 | context/03-requirements.md:1106 | Player | Given an L-shape / squeezeback layout | MUST composite its two elements with the ad creative covering the whole frame and the shrunk primary content occupying its declared region on top. |
| R27.3a | context/03-requirements.md:1111 | Player | Given an L-shape whose full-frame ad creative is a video (a second video decoder) | Not satisfiable on a single-decoder device (R3 / R5). `[no RFC 2119 keyword]` |
| R27.3b | context/03-requirements.md:1122 | Player | Given an L-shape whose full-frame ad creative is an image or HTML | MUST NOT be selected on a device that cannot composite that surface type together with video (R3 / R5). |
| R14.1 | context/03-requirements.md:1164 | Player | Given a resolution document for a non-linear slot declaring more than one ad candidate | MUST present the candidates in sequence, in the order they appear in the document, each starting when the previous one ends. |
| R14.2 | context/03-requirements.md:1169 | Player | Given a sequence of non-linear candidates | MUST enforce the Publisher-declared slot cap (R4) against their cumulative duration, trimming or dropping per R4 / R7 when it would exceed the slot's opportunity window. |
| R14.3 | context/03-requirements.md:1174 | spec document | (unconditional) | MUST NOT introduce a construct that implies or requires the parallel rendering of two or more non-linear ad forms; sequencing carries no separate "render-then" primitive beyond declared candidate order. |
| R17.1 | context/03-requirements.md:1209 | Player | Given the viewer is paused inside a pause-ad window AND an overlay is active | Renders the pause-ad form and suspends the overlay rendering. `[no RFC 2119 keyword]` |
| R17.2 | context/03-requirements.md:1213 | Player | Given a resume from pause with the overlay slot window still active | Dismisses the pause-ad (R16) and restores the overlay rendering. `[no RFC 2119 keyword]` |
| R17.3 | context/03-requirements.md:1216 | Player | Given the overlay slot window expired during the pause | Keeps the overlay surface clear on resume; the overlay is over. `[no RFC 2119 keyword]` |
| R17.4 | context/03-requirements.md:1219 | spec document | (unconditional) | Carries no construct that lets the Publisher, the ADS or the APS invert the pause-ad-over-overlay priority. `[no RFC 2119 keyword]` |
| R17.5 | context/03-requirements.md:1222 | Player | Given a viewer pause beginning inside a pause opportunity window while a linear ad occupies the screen | Presents the pause ad and suspends the linear ad, resuming it from where it was suspended when the viewer resumes. `[no RFC 2119 keyword]` |
| R20.1a | context/03-requirements.md:1271 | Player | Given ad opportunity windows of the same family overlapping in time within the primary `MPD` | MUST select the first overlapping window (R20.3) and attempt to resolve it. |
| R20.1b | context/03-requirements.md:1275 | Player | Given an attempt on a window that does not produce an ad (a failed execution) | MUST attempt the next overlapping window of the same family (§5.16.2.2.5, step 2). |
| R20.1c | context/03-requirements.md:1283 | Player | Given any of the four failure conditions — no response or transport failure, a final HTTP status other than 200, a 200 whose body does not parse as a resolution document, or a well-formed resolution document carrying no candidates (R30) | MUST treat all four alike as a failed execution. `[CONTRADICTION — see §5]` |
| R20.1d | context/03-requirements.md:1297 | Player | Given every overlapping window of the family has been attempted and none produced an ad | MUST continue with the primary content uninterrupted (§5.16.2.2.5). |
| R20.2 | context/03-requirements.md:1319 | Publisher | Given all opportunity windows of one family that share a `Period` | MUST be authored as `<Event>` entries inside a single `<EventStream>` (§5.10.2.1). |
| R20.3 | context/03-requirements.md:1326 | Player | Given overlapping windows of one family | Ordered by presentation time, oldest first; where two windows carry the same presentation time, by the order in which they appear inside the `EventStream`. Not document order. `[no RFC 2119 keyword]` |
| R20.4 | context/03-requirements.md:1347 | Player | Given a resolution document whose family does not match the slot that requested it | MUST treat it as a failure to resolve and continue down the R20.1 chain, and MUST NOT treat it as a resolution carrying no candidates. `[CONTRADICTION — the criterion holds; its own RATIONALE prose at :1354-:1362 contradicts R20.1c and R30. See §5]` |
| R20.5 | context/03-requirements.md:1363 | Player | Given a window in a fallback chain | Binds the candidates it serves with its own allowed layouts and its own maximum duration; it does not inherit the declarations of the window it stands in for. `[no RFC 2119 keyword]` |
| R20.6 | context/03-requirements.md:1370 | spec document | Given the rule stated in R20.5 | MUST be carried as a normative Player obligation, not only in informative material. |
| R22.1a | context/03-requirements.md:1412 | Player | Given any instant `t` | MUST keep at most one non-linear ad form active on the screen. |
| R22.1b | context/03-requirements.md:1413 | Player | Given two or more non-linear ad forms available to present | MUST NOT present them simultaneously; the device never needs more than main content plus one ad form's video decoder concurrently (R3). |
| R6.1 | context/03-requirements.md:1448 | spec document | (unconditional) | MUST specify how in-band ad tracking beacons are carried in the resolution document. |
| R6.2 | context/03-requirements.md:1450 | APS | Given tracking beacons to carry | SHOULD carry them as `<Event>` entries inside an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015` in the ad `MPD` or sub-`MPD`, translated from the tracking events the ADS declared. |
| R6.3 | context/03-requirements.md:1455 | spec document | Given the callback scheme cannot express the required semantics | A new tracking carrier MAY be introduced only then, and only after a documented gap analysis per R9. |
| R6.4 | context/03-requirements.md:1459 | Player | Given an unknown namespace on a tracking-related extension element | MUST safely ignore it, per the DASH extension rules invoked by R1. |
| R6.5a | context/03-requirements.md:1462 | APS + Player | Given beacons within one candidate sharing an `@id`, or the same URL at the same presentation time | Fire once; the de-duplication key is scoped to the candidate that carries them. `[no RFC 2119 keyword]` |
| R6.5b | context/03-requirements.md:1466 | Player | Given two beacons carrying the same `@id` in two different candidates of one resolution document | They are two distinct beacons and the Player MUST fire both. |
| R6.6 | context/03-requirements.md:1468 | Player | Given the beacon carrier is an `<EventStream>` hosted as foreign-namespace open content inside a candidate | Its presentation times are resolved against that candidate's own presentation, not against a `<Period>` the element does not sit in. `[no RFC 2119 keyword]` |
| R6.7 | context/03-requirements.md:1473 | spec document | Given a resolution document carrying the candidate-level beacon carrier | MUST state how it is validated; a procedure that reports the document valid while skipping the foreign-namespace subtree has not checked the tracking carrier at all. |
| R13.1 | context/03-requirements.md:1497 | APS | Given the resolution document carries tracking instructions | MUST express them using DASH callback events (or an equivalent baseline DASH construct), with timings relative to the ad's presentation timeline. |
| R13.2 | context/03-requirements.md:1504 | Player | Given an ad accepted for rendering | MUST execute the tracking schedule read from the resolution document, firing each beacon at its specified relative time. |
| R13.3 | context/03-requirements.md:1509 | Player | Given R4 trims the ad before a scheduled beacon's time | MUST stop firing the remaining beacons at the trim boundary. |
| R13.4 | context/03-requirements.md:1512 | spec document | (unconditional) | MUST NOT introduce a new tracking event scheme; reuse of the DASH baseline callback mechanism is mandatory. |
| R13.5 | context/03-requirements.md:1515 | ADS + APS | Given the fidelity of the beacon transcription (nothing added, removed or reordered) | Part of the APS-to-ADS contract those parties maintain directly, outside this specification (R18). `[no RFC 2119 keyword]` |
| R23.1 | context/03-requirements.md:1541 | spec document | Given generic application-level metadata with no native DASH carrier (`AdSystem`, `AdTitle`, etc.) | MUST define the extension elements that carry it in the SVTA Ads WG namespace, and MUST state that emitting them and reading them are both optional. |
| R24.1a | context/03-requirements.md:1560 | APS | Given a non-AV ad form (`mediaType ∈ {html, image, …}`) carried in the resolution document | Its asset URL MUST NOT be expressed as `@mimeType` on an AdaptationSet or Representation reached through any path bound by RFC 4337 (DR-1, DR-5). |
| R24.1b | context/03-requirements.md:1566 | APS | Given the same non-AV asset URL | MUST be carried via one of the §5.2.1 / §5.10 / §5.8.4.x carriers enumerated by DR-6, per R1.2. |
| R33.1 | context/03-requirements.md:1614 | spec document | (unconditional) | MUST NOT define a metric of its own for pause-ad delivery; the quantity is derived from the `PlayList` metric of Annex D.4.6. |
| R33.2 | context/03-requirements.md:1619 | Player | Given a Player that reports metrics | MUST derive the paused interval from the `PlayList` entries (a stretch stopped on `UserRequest` up to the next entry whose `starttype` is `Resume`), and MUST NOT count a playback period that stopped on `Rebuffering` as a pause opportunity. |
| R33.3 | context/03-requirements.md:1623 | spec document | Given the transport by which a measurement reaches the Publisher, the APS or the ADS | Out of scope, as it is for the base specification's own metrics (§5.9.1). `[no RFC 2119 keyword]` |
| R33.4 | context/03-requirements.md:1626 | Publisher | Given content carrying pause opportunity windows | MUST request the `PlayList` metric through the base specification's `Metrics` element, since collection is triggered by the service provider and not by the Player (§5.9.1). |
| R28.1 | context/03-requirements.md:1654 | APS | Given an ad candidate in the resolution document carries a ClickThrough | The ClickThrough URL and any accompanying click-tracking URLs MUST be carried in the normative carrier this specification defines, and not elsewhere. |
| R28.2 | context/03-requirements.md:1663 | Player | Given the viewer activates a ClickThrough on a Player conformant to this specification | MUST read the ClickThrough URL and fire its associated click-tracking. |
| R28.3 | context/03-requirements.md:1666 | ADS + APS | Given whether a ClickThrough the ADS declared reaches the resolution document at all | Part of the APS-to-ADS contract those parties maintain directly, outside this specification (R18). `[no RFC 2119 keyword]` |
| R8.1 | context/03-requirements.md:1690 | spec document | Given every new construct the proposal introduces | MUST be accompanied by an inline justification stating why an existing MPEG-DASH construct could not be reused. |
| R8.2 | context/03-requirements.md:1693 | spec document | Given a deliberate omission of an existing MPEG-DASH construct a reader might expect to see reused | MUST be documented inline with the design decision. |
| R9.1 | context/03-requirements.md:1708 | spec document | (unconditional) | MUST reuse existing MPEG-DASH machinery (events, manifests, presentations, schemes) wherever possible. |
| R9.2 | context/03-requirements.md:1711 | spec document | Given an existing construct that can be made to fit | A new construct MUST NOT be introduced. |
| R9.3 | context/03-requirements.md:1713 | spec document | Given the proposal is about to introduce a new construct | MUST first consider whether an extension to an existing construct would suffice, and document the outcome of that consideration. |
| R10.1 | context/03-requirements.md:1729 | spec document | Given the spatial arrangement of overlays | MUST be delegated to HTML5 / CSS layout primitives. |
| R10.2 | context/03-requirements.md:1731 | spec document | (unconditional) | MUST NOT define a parallel layout standard for overlay placement. |
| R10.3 | context/03-requirements.md:1733 | spec document | Given position semantics inside a layout (left, right, top, bottom) | Out of scope; where an ad sits follows from the IAB CTV ad type the `@layout` token names and is rendered with HTML5 / CSS primitives. This specification declares no positioning vocabulary of its own. `[no RFC 2119 keyword]` |
| P03.1 | context/03-requirements.md:552 | APS | Given an HTML creative carried as `text/html` | MAY contain inline `<script>` per HTML5 semantics; the script runs under the device's HTML capability contract and is not a separate carrier. |
| P03.2 | context/03-requirements.md:1761 | Publisher + APS | Given a sender that needs a scripted creative (OOS-4) | MUST wrap the script inside an HTML document and use `text/html` per R15; raw JavaScript, SVG-as-payload, PDF and proprietary binary creatives are out of scope. |
| IN01.1 | context/01-intro.md:51 | spec document | Given each new construct the spec introduces | MUST apply the verification checklist of `07-backward-compat-checklist.md`, so legacy Player compatibility is auditable per construct. |
| A2.1 | context/02-actors.md:48 | ADS | Given the ADS's decision document | Typically VAST, but the ADS is not bound to VAST and MAY emit another format; it performs no conversion into the MPD-native / SGAI format. |
| UC04.1 | context/04-use-cases.md:304 | APS | Given a candidate's presentation option | MAY be a partial-screen layout — L-shape / squeezeback or side-by-side / double-box, which are modelled differently. |
| UC04.2 | context/04-use-cases.md:785 | Player | Given a legacy Player encountering an unrecognised event type or construct in the manifest (UC-07) | MUST skip the unknown construct and continue playing the primary content as if it were not present. |
| UC04.3 | context/04-use-cases.md:802 | Publisher | Given live / real-time content whose SGAI opportunity falls through on a legacy Player | SHOULD treat the opportunity as a loss on legacy Players; live content cannot be held to splice a standard break without losing real content. |
| UC04.4 | context/04-use-cases.md:804 | Publisher | Given non-live / VOD content carrying an SGAI construct | MAY, and SHOULD where monetising the opportunity matters, author a standard linear break alongside the SGAI construct using only baseline MPEG-DASH constructs, authored unconditionally because Player version is not detectable from the manifest. |
| UC04.5 | context/04-use-cases.md:839 | spec document | Given any new construct the proposal introduces | MUST be expressible via extension points that produce the UC-07 skip-and-continue outcome on legacy Players. |
| UC04.6 | context/04-use-cases.md:860 | Player | Given a pause-ad presented while an overlay coexists (UC-08) | MAY be fullscreen or a partial overlay over the paused primary frame; either way it is the only ad surface visible and the overlay is suspended. |
| UC04.7 | context/04-use-cases.md:1175 | APS + Player | Given a side-by-side / double-box layout leaving bands uncovered (UC-10) | A background element — a still image, never a video and never a web/HTML surface — MAY fill the uncovered region. |
| I05.1 | context/05-dash-linear-interfaces.md:34 | APS | Given an APS that holds a view of the device | MAY narrow the option list and send a single form, the choice then sitting with the APS; the Player-visible interface is unchanged. |
| I05.2 | context/05-dash-linear-interfaces.md:383 | spec document | Given the non-linear chapters of the spec carrying non-AV asset URLs (HTML, image, other) | MUST carry them outside the AdaptationSet / Representation axis, via one of the carriers enumerated in DR-6. |
| I05.3 | context/05-dash-linear-interfaces.md:433 | Player | Given the ClickThrough carrier on a Player conformant to this specification | MUST read it, and fires the click-tracking when the viewer activates the ClickThrough rather than on the callback timeline. |
| I05.4 | context/05-dash-linear-interfaces.md:433 | Player | Given the R23 SVTA-namespaced generic metadata (`AdSystem`, `AdTitle`, `Advertiser`) | MAY be safely ignored; no interoperable carrier is mandated for it and dropping it breaks nothing in the ad presentation. |
| I05.5 | context/05-dash-linear-interfaces.md:435 | APS | Given VAST `<UniversalAdId>`, which this spec leaves on the VAST / ADS side | MAY be preserved on a best-effort SVTA-namespaced attribute / element on the corresponding `ImportedMPD` (R23), but no carrier is mandated for it. |
| N06.1 | context/06-naming-and-namespaces.md:4 | spec document | Given any new construct the SGAI spec introduces | MUST follow the naming conventions of this document, which chapters 5 (Syntax) and 8 (Examples) consume. |
| N06.2 | context/06-naming-and-namespaces.md:22 | spec document | Given a new event scheme introduced by this spec | MUST use the year-pinned pattern `urn:svta:dash:<construct>:<year>` under the SVTA Ads WG namespace; reusing an existing scheme URI with altered semantics across editions is not permitted. |
| N06.3 | context/06-naming-and-namespaces.md:37 | Player | Given a Player implementing edition N + 1 | SHOULD recognise both `:N:` and `:N+1:` URIs and treat them per the backward-compatibility rules in that edition's spec. |
| N06.4 | context/06-naming-and-namespaces.md:48 | APS | Given an implementation carrying tracking beacons for ads introduced by this spec | MUST reuse the MPEG-DASH 6th edition baseline tracking callback scheme; a parallel tracking scheme under `urn:svta:dash:*` is out of scope. |
| N06.5 | context/06-naming-and-namespaces.md:55 | spec document | Given a Qualabs-private experimental extension that is not part of this specification | MUST use the Qualabs vendor namespace `urn:qualabs:<feature>:<year>`; such URIs are not normative and not part of the SGAI spec. |
| N06.6 | context/06-naming-and-namespaces.md:86 | spec document | Given a construct introduced by this spec that places a baseline DASH child inside an SGAI element | MUST honour the authoring rule stated in DR-3 — a baseline child nested inside a foreign-namespace element carries no legacy guarantee. |
| N06.7 | context/06-naming-and-namespaces.md:93 | spec document | Given a construct whose semantics change in a new edition | MUST use a new `<year>` suffix on its scheme URI under `urn:svta:dash:<construct>:<year>`. |
| N06.8 | context/06-naming-and-namespaces.md:96 | spec document | Given a construct whose semantics are unchanged in a new edition | MAY keep its existing URI. |
| N06.9 | context/06-naming-and-namespaces.md:98 | spec document | Given the spec's chapter 2 (Normative references) | MUST list the URIs introduced by the current edition explicitly. |
| N06.10 | context/06-naming-and-namespaces.md:107 | spec document | Given the accepted layout names for overlay templates, which the IAB defines and maintains | MUST reference those IAB-defined values without inventing new layout names at chapter level. |
| N06.11 | context/06-naming-and-namespaces.md:112 | spec document | Given the layout vocabulary | MUST map 1:1 to IAB-defined ad-type values; no publisher-private or spec-private layout names are admissible. |
| N06.12 | context/06-naming-and-namespaces.md:143 | spec document | Given a component that is in essence the same as one already defined in MPEG-DASH 6th edition or its profile annexes | MUST reuse the existing baseline construct with all its characteristics — name, default values, permitted value domain, units, semantics — and MUST NOT introduce a new identifier. |
| B07.1 | context/07-backward-compat-checklist.md:5 | spec document | Given every new construct the spec introduces | MUST follow this checklist, so the ignore-if-unknown guarantee is auditable per construct rather than left to a generic claim. |
| B07.2 | context/07-backward-compat-checklist.md:13 | spec document | Given the spec's chapter 4 (Conformance) and chapter 10 (Test cases) | MUST apply the verification procedure this checklist defines. |
| B07.3 | context/07-backward-compat-checklist.md:17 | spec document | Given each new construct C | MUST explicitly answer the eight checklist questions in C's specification chapter. |
| B07.4 | context/07-backward-compat-checklist.md:19 | spec document | Given a checklist item left unanswered for a construct | SHOULD block publication. |
| B07.5 | context/07-backward-compat-checklist.md:37 | spec document | Given C's placement in the DASH XML hierarchy | The construct's chapter MUST name the applicable DR-N rule from `08-dash-extension-rules.md` and cite the section documenting the ignore-if-unknown rule. |
| B07.6 | context/07-backward-compat-checklist.md:48 | spec document | Given C introduces a new namespace | The construct MUST be in an extension namespace per `06-naming-and-namespaces.md`. |
| B07.7 | context/07-backward-compat-checklist.md:53 | spec document | Given C invokes Annex F (DR-4) | The chapter MUST state which new Interoperability Point URI is published in `MPD@profiles`, and justify why the §5.2.1 / §5.10 / §5.8.4.x DR-6 carriers are not sufficient. |
| B07.8 | context/07-backward-compat-checklist.md:67 | spec document | Given the legacy-Player behaviour walk-through for C | MUST be present in C's chapter as an explicit prose paragraph, not implicit. |
| B07.9 | context/07-backward-compat-checklist.md:79 | spec document | Given C removed from the document | MUST still leave a document that parses and plays, with no legacy-required sibling or parent attribute made inconsistent by C's presence. |
| B07.10 | context/07-backward-compat-checklist.md:84 | spec document | Given each new construct C | MUST have a corresponding chapter-10 test case modelled on UC-07: a representative MPD/ListMPD containing C, a legacy Player harness, and the expected silent skip with no beacon for C. |
| B07.11 | context/07-backward-compat-checklist.md:91 | Player | Given a legacy Player encountering C in any case | MUST ignore C; this is the invariant the per-construct test verifies. |
| B07.12 | context/07-backward-compat-checklist.md:99 | Publisher | Given non-live / VOD content carrying C | MAY author a standard linear break alongside C using only baseline constructs a legacy Player renders, in which case the legacy Player skips C and plays the standard break. |
| B07.13 | context/07-backward-compat-checklist.md:127 | spec document | Given C's specification chapter | MUST link to this checklist and confirm each item is satisfied. |
| B07.14 | context/07-backward-compat-checklist.md:128 | spec document | Given a construct chapter that omits the checklist confirmation | Reviewers SHOULD reject it. |
| B07.15 | context/07-backward-compat-checklist.md:154 | spec document | Given the carrier classification of C against DR-6 | (c1) supplemental descriptors and (c2) essential descriptors MUST NOT be classified together; one degrades and the other removes the parent element, and a construct classified as "(c)" states nothing auditable. |
| B07.16 | context/07-backward-compat-checklist.md:160 | spec document | Given a construct that fits none of (a) / (b) / (c1) / (c2) | MUST justify why Annex F (DR-4) is invoked and what new Interoperability Point URI is published. |
| B07.17 | context/07-backward-compat-checklist.md:162 | spec document | Given C's carrier classification | MUST be stated explicitly in the construct's chapter; leaving it implicit is a checklist failure. |
| B07.18 | context/07-backward-compat-checklist.md:167 | spec document | Given the shipped spec | SHOULD carry an audit table summarising checklist status per construct, where a `FAIL` in any column blocks publication. |
| B07.19 | context/07-backward-compat-checklist.md:179 | spec document | Given the enumerated anti-patterns that silently break the ignore-if-unknown contract | Reviewers MUST flag them. |
| B07.20 | context/07-backward-compat-checklist.md:194 | Publisher + APS | Given a non-AV ad asset | MUST be carried via one of the DR-6 carriers; a non-MP4 `@mimeType` on an AdaptationSet or Representation reached via `<ImportedMPD>` (DR-1) or inside a ListMPD-level Period (DR-5) is an anti-pattern. |
| D08.1 | context/08-dash-extension-rules.md:14 | spec document | Given an edition bump of the base standard | This file MUST be re-validated section by section; rules are not blindly carried forward, and `bin/check-normative-base.py` makes the obligation observable. |
| D08.2 | context/08-dash-extension-rules.md:33 | APS | Given a non-AV ad asset on a sub-MPD referenced from a ListMPD via `<ImportedMPD>` (DR-1) | MUST be carried via one of the carriers enumerated in DR-6; SPS offers no extension point for non-MP4 MIME types. |
| D08.3 | context/08-dash-extension-rules.md:41 | spec document | Given the MPD schema's `<xs:any namespace='##other' processContents='lax'/>` on every container (§5.2.1) | A foreign-namespace element MAY appear as a child of any DASH container, including `<Period>`, `<AdaptationSet>`, `<Event>`, and other foreign-namespace elements. |
| D08.4 | context/08-dash-extension-rules.md:44 | Publisher | Given an MPD carrying foreign-namespace attributes or elements | MUST be authored such that, once they are removed, the result is still a valid DASH document conforming to the base specification (§5.2.1). |
| D08.5 | context/08-dash-extension-rules.md:89 | spec document | Given a construct that nests a baseline DASH element inside a foreign-namespace parent | MUST still satisfy §5.2.1 once the foreign-namespace parent is removed; no legacy behaviour may be assumed for the nested baseline child (DR-3). |
| D08.6 | context/08-dash-extension-rules.md:134 | Publisher + APS | Given a per-AdaptationSet `@profiles` declaration | MUST be a subset of MPD-level `@profiles` (§5.3.7.2 Table 16), so an SPS-rooted document cannot promote one AdaptationSet to a broader profile to escape RFC 4337. |
| D08.7 | context/08-dash-extension-rules.md:209 | Publisher + APS | Given tracking for a non-AV ad that needs presentation-time alignment across a non-zero-duration Period | MUST share a Period with at least one AdaptationSet, or live outside a non-zero-duration Period (§5.3.2.2 Table 4); an events-only Period is closed. |
| D08.8 | context/08-dash-extension-rules.md:254 | Player | Given the R28 ClickThrough carrier on a Player conformant to this specification | MUST be read; the guarantee is scoped to Players conformant to this specification, because DASH specifies no Player behaviour (DR-8). |
| D08.9 | context/08-dash-extension-rules.md:254 | Player | Given the R23 generic metadata carrier | MAY be ignored; this is the contrast R28 exists to draw, and both obligations address the same Players. |
| D08.10 | context/08-dash-extension-rules.md:299 | spec document | Given a construct that uses `EssentialProperty` or `SupplementalProperty` (§5.8.4.8 / §5.8.4.9) | MUST state which of the two it uses and why, since an unrecognised scheme costs the parent element on one and only the descriptor on the other (DR-9). |
| G99.1 | context/99-glossary.md:51 | Player | Given a capability parameter on the resolution request | MAY be attached; the names are reserved by this specification, sending any of them is optional, one the Player cannot or will not populate is omitted rather than sent empty, and an absent parameter means undetermined (R29). |
| G99.2 | context/99-glossary.md:83 | ADS | Given the ADS's decision document | Typically VAST (IAB), though the ADS is not bound to VAST and MAY emit another format; it does not convert its output into the MPD-native / SGAI resolution document. |

**Table order.** `context/03-requirements.md` first, in ascending
source-line order (which is why the requirement numbers are not
sequential — the file groups them thematically), then the remaining
files in numeric order.

## 1. Assertions per R

145 of the 210 rows come from a `Conformance criteria` block, against
the 123 criteria declared in `context/03-requirements.md`. The
remaining 65 are the design principles, the two prose obligations, and
the eight other `context/` files.

R1: 6, R2: 6, R3: 3, R4: 11, R5: 7, R6: 8, R7: 5, R8: 2, R9: 3,
R10: 3, R11: 3, R12: 6, R13: 5, R14: 3, R15: 4, R16: 2, R17: 5,
R18: 2, R19: 4, R20: 9, R21: 3, R22: 2, R23: 1, R24: 2, R25: 2,
R26: 5, R27: 4, R28: 3, R29: 7, R30: 2, R31: 3, R32: 5, R33: 4,
R34: 5.

Plus DP03: 5 (design principles), P03: 2 (requirement-body prose and
the Out of Scope list).

Every declared criterion appears. The spread is informative: R4
(11 rows) and R20 (9) carry the most testable surface, and R23 carries
one — a single document-level obligation whose whole content is that
the carrier exists and is optional.

## 2. Assertions per actor

Exact Actor-cell tally:

| Actor cell | Rows |
|---|---|
| Player | 84 |
| spec document | 76 |
| APS | 18 |
| Publisher | 11 |
| Publisher + APS | 7 |
| ADS | 4 |
| ADS + APS | 4 |
| Publisher + Player | 2 |
| APS + Player | 2 |
| Publisher + ADS + APS | 1 |
| all | 1 |

Rolled up — rows binding each actor at all, counting shared cells
once per actor and the `all` row for every runtime actor:

| Actor | Rows binding it |
|---|---|
| Player | 89 |
| spec document | 76 |
| APS | 33 |
| Publisher | 22 |
| ADS | 10 |

The ADS's 10 rows are the model working as designed: six of them say
what the ADS is *not* obliged to do (R2.2c, R4.4, R5.4) or delegate to
the APS-to-ADS contract this specification does not observe (R13.5,
R18.2, R28.3). Only R2.2a and A2.1 / G99.2 state a positive ADS
obligation, and those are about emitting a decision document at all.

## 3. Assertions per source doc

| Source doc | Rows |
|---|---|
| `context/03-requirements.md` | 152 |
| `context/07-backward-compat-checklist.md` | 20 |
| `context/06-naming-and-namespaces.md` | 12 |
| `context/08-dash-extension-rules.md` | 10 |
| `context/04-use-cases.md` | 7 |
| `context/05-dash-linear-interfaces.md` | 5 |
| `context/99-glossary.md` | 2 |
| `context/01-intro.md` | 1 |
| `context/02-actors.md` | 1 |
| `context/00-normative-base.md` | 0 |
| **Total** | **210** |

`00-normative-base.md` carries no RFC 2119 sentence, which is correct
for what it is: a declaration of which edition the project is written
against, verified by `bin/check-normative-base.py` rather than by a
conformance test.

The 58 rows outside `03-requirements.md` are not decoration. Twenty of
them — the whole backward-compat checklist — are the only place the
R1 guarantee becomes auditable per construct, and twelve more are the
naming policy that keeps a construct from being minted twice.

## 4. Orphan assertions

Obligations outside `context/03-requirements.md` that do not map
cleanly onto any requirement. Each is a signal that a requirement is
missing, or that an R needs to absorb the orphan.

**Two orphans state the same missing requirement, in two files.**

- **UC04.3** (`04-use-cases.md:802`) — the Publisher SHOULD treat a
  live-content opportunity as a loss on legacy Players.
- **UC04.4** (`04-use-cases.md:804`) and **B07.12**
  (`07-backward-compat-checklist.md:99`) — for VOD the Publisher MAY
  (and SHOULD, where monetising matters) author a standard linear
  break alongside the SGAI construct as the legacy fallback.

  R1 obliges the *spec* to use extension points whose semantics let a
  legacy Player skip, and R1.1 obliges the legacy Player to skip. What
  neither says is what the **Publisher** authors so the opportunity is
  not simply lost — which is the only lever anyone has over the
  outcome, since Player version is not detectable from the manifest.
  That is a Publisher-side criterion missing from R1 (an **R1.5**),
  and it is currently stated only in a use case and a checklist, where
  nothing binds it.

**The naming and versioning policy has no requirement behind it.**
N06.2, N06.5, N06.7, N06.8, N06.9 (year-pinned scheme URIs, the
Qualabs vendor namespace, and the three versioning rules) oblige the
spec document with no R to answer to. R8 and R9 govern *justifying*
and *minimising* constructs, not *naming* them. Either a governance
requirement absorbs the naming policy, or `06-naming-and-namespaces.md`
is acknowledged as normative in its own right — which it already
behaves as, since R34 delegates the naming of its construct to it.

- **N06.3** (`06-naming-and-namespaces.md:37`) is the sharpest case:
  it is a **runtime Player obligation** ("a Player implementing
  edition N + 1 SHOULD recognise both `:N:` and `:N+1:` URIs") sitting
  in a naming document, exercised by no UC and traceable to no R.
  Cross-edition Player behaviour is a requirement-level question.
- **N06.12** (`:143`) — reuse the baseline construct with all its
  characteristics rather than minting a new identifier — is the one
  that arguably belongs to **R9.1**, which today says "reuse existing
  MPEG-DASH machinery". Absorbing it would make R9.1 testable on
  identifiers, not just on machinery.

**Four checklist assertions are publication governance, not
conformance.** B07.4 (unanswered items SHOULD block publication),
B07.14 (reviewers SHOULD reject chapters omitting the confirmation),
B07.18 (the spec SHOULD ship an audit table), B07.19 (reviewers MUST
flag the anti-patterns). They bind a review process, and no R
establishes that process. They are testable only against a published
document, so chapter 10 cannot build a test from them; they belong in
a governance requirement (an extension of R8) or explicitly outside
the conformance set.

**B07.15 / D08.10 state an obligation R1.2 permits but does not
impose.** R1.2 admits vendor descriptor schemes (§5.8.4.8 / §5.8.4.9)
as an extension point without distinguishing the two elements. The
obligation to say *which* one a construct uses and *why* — and never
to classify them together — exists only in the checklist and in DR-9.
Given that the choice decides whether a legacy client loses the
descriptor or the whole parent element, it should be a criterion under
R1.2.

**D08.1** (`08-dash-extension-rules.md:14`) obliges the *context set
itself* to be re-validated on an edition bump. No R governs the
maintenance of `context/`; the obligation is real and is enforced by
`bin/check-normative-base.py`, which is the right place for it, but it
has no requirement to point at.

**A2.1 / G99.2 — the ADS's freedom to emit a non-VAST decision
document is stated twice outside R11 and by no criterion inside it.**
R11.1 and R11.3 bind the spec document; R11.2 binds the Player. The
actor whose freedom R11 exists to protect — the ADS — is bound by no
R11 criterion. R11 needs an ADS-facing criterion, or it protects a
freedom it never grants.

The remaining non-R assertions map cleanly: UC04.1 → R5.5 / R12,
UC04.2 → R1.1, UC04.5 → R1.2a, UC04.6 → R21.1, UC04.7 → R26.2b,
I05.1 → R5.1 / R5.5, I05.2 → R24.1b, I05.3 → R28.2, I05.4 → R23.1,
I05.5 → R23.1, N06.1 → R1.2a, N06.4 → R13.4, N06.6 → R1.2a,
N06.10 / N06.11 → R12.1 / R12.2, B07.1 / B07.2 / B07.3 / B07.5 /
B07.8 / B07.9 / B07.10 / B07.11 / B07.13 / B07.17 → R1.1 / R1.2,
B07.6 → R1.2a, B07.7 / B07.16 → R1.2c, B07.20 → R24.1b,
D08.2 → R24.1b, D08.3 / D08.4 / D08.5 / D08.6 / D08.7 → R1.2,
D08.8 → R28.2, D08.9 → R23.1, G99.1 → R29.2, IN01.1 → B07.1 / R1.

### Cross-reference with the UC coverage matrix

`uc-coverage-matrix.md` reports a different kind of orphan — a
requirement no use case exercises. The two views answer different
questions and both matter: an R can be fully covered by assertions and
by no test scenario.

| R | Assertions | Binding a runtime actor | UC coverage |
|---|---|---|---|
| R24 | 2 | 2 (APS) | none |
| R32 | 5 | 4 | none |
| R33 | 4 | 2 | none |
| R34 | 5 | 4 | none |
| R14 | 3 | 2 (Player) | one pointer only |

**Sixteen assertions belong to a requirement no use case exercises,
and twelve of them bind a runtime actor.** That is the number worth
carrying forward: a document-level assertion with no UC is checked by
reading the spec, but a Player or APS obligation with no UC has no
scenario in which anything observes it.

- **R32** and **R34** are real gaps, as the matrix says. R32's four
  runtime rows (R32.1a, R32.1b, R32.2, R32.3) are the three exhaustion
  behaviours and the `stop` default, and nothing exercises any of them.
  R34's four (R34.1, R34.2a, R34.2b, R34.3) need a viewer who pauses
  twice inside one window.
- **R24 is a UC gap and not a governance reclassification.** Both its
  assertions bind the **APS** and are checkable on the resolution
  document: R24.1a forbids a carrier, R24.1b mandates one. An
  obligation verifiable on an artefact an actor produces is not
  governance, whatever the criterion's `(APS / spec document)` label
  suggests. At the assertion level R24.1 is well anchored — I05.2,
  B07.20 and D08.2 restate it from three independent files — and the
  missing piece is exactly a UC showing a non-AV asset URL travelling
  in a DR-6 carrier.
- **R33 splits three ways, not two.** R33.1 and R33.3 are governance
  (`spec document`). R33.4 binds the **Publisher** (the `Metrics`
  element must be declared) and is UC-expressible. So is **R33.2**,
  which binds the **Player**: deriving the paused interval from
  `PlayList` entries, and not counting a period that stopped on
  `Rebuffering`, is observable behaviour. A UC that only covers R33.4
  leaves the Player half unexercised.
- **R11 is not purely governance at the assertion level.** R11.2 binds
  the Player, and is exercisable: an ADS emitting a non-VAST decision
  document, with the Player rendering from the APS's resolution
  document unchanged. What R11 genuinely lacks is an ADS-facing
  criterion (see A2.1 / G99.2 above), so it is orphaned at the
  assertion level in a way closing the UC gap would not fix.
- **R14** is the near-orphan: UC-12 points at it, but no use case
  plays two non-linear candidates back to back, which is R14.1's
  actual obligation, and none tests the cap against their cumulative
  duration, which is R14.2's.

`error-semantics.md` (E1..E15) introduces no obligation absent from
this table: every `R<N>.<n>` it cites resolves to a row above.

## 5. Ambiguity findings

Sentences whose obligation strength cannot be read off the text. None
was resolved by invention; each is recorded as a finding.

### The contradiction about a resolution carrying no candidates

`context/03-requirements.md` gives two opposite outcomes for the same
`200` response — a well-formed resolution document that carries no
candidates.

- **R20.1** (`:1294`) lists it as the fourth way an attempt can fail,
  quoting the base specification's *"Alternative MPD is a List MPD,
  and merge process resulted in no available media"*, and **R30**'s
  body (`:708`) says the same: *"the attempt produced no ad, so it is
  a failed execution and the next overlapping window of the family is
  attempted."* Under this reading the chain **continues**.
- **R20.4**'s RATIONALE prose (`:1350`, `:1356`-`:1359`) says the
  opposite: *"It MUST NOT be treated as a resolution carrying no
  candidates, which ends the chain"*, and *"A resolution carrying no
  candidates is an answer … which is why the chain ends there rather
  than asking again."* Under this reading the chain **ends**.

The rows above follow R20.1 and R30 — the normative criteria, and the
implementation of accepted ADR 0011. R20.4's *criterion* is unaffected
and is carried as written: a wrong-family document is a failure to
resolve. It is R20.4's explanatory prose that is stale, predating the
ADR it cites, and it is the one place a test author would read the
wrong outcome. **The fix belongs in `context/`, which this analysis
does not edit.**

### Declared criteria carrying no RFC 2119 keyword

**Twenty-three declared conformance criteria carry no RFC 2119
keyword at all**, and three more carry one in only part of the
criterion (R1.2, R6.5, R27.3 — split above so the keywordless half is
visible). They are written in the indicative ("the Player
renders…", "the specification documents…"), so a test author cannot
tell MUST from SHOULD. Marked `[no RFC 2119 keyword]` in the table:
R1.2c, R4.7, R4.8, R4.11, R6.5a, R6.6, R10.3, R12.4, R13.5, R17.1,
R17.2, R17.3, R17.4, R17.5, R18.1, R18.2, R20.3, R20.5, R27.3a,
R28.3, R29.1, R29.7, R32.4, R33.3, R34.3, R34.4.

Four clusters, four different fixes:

- **R17.1, R17.2, R17.3, R17.5** describe runtime Player behaviour
  during a pause and are plainly MUST in intent — R17's body calls the
  priority "not Publisher-configurable" and "the only admissible
  composition". The whole of R17's runtime surface is keywordless,
  which makes it the single largest untyped block in the set.
  **Add MUST.**
- **R20.3, R20.5, R34.3, R6.5a, R6.6, R4.11** state runtime rules
  that decide observable outcomes — window ordering, which window's
  declarations bind, when a once-per-session window is consumed,
  beacon de-duplication and its timebase, cap arithmetic across a
  suspension. Each is a test a chapter-10 author would have to invent
  a modal for. **Add MUST.** R20.6 already establishes the precedent:
  it exists precisely to promote R20.5 to a normative Player
  obligation, and R20.5 itself still carries no keyword.
- **R1.2c, R4.7, R4.8, R10.3, R12.4, R17.4, R27.3a, R29.1, R29.7,
  R32.4, R33.3, R34.4** are statements *about the spec* — what it
  inherits, what it documents, what it declines to define. They may be
  correct as non-normative notes, but then they should not sit in a
  `Conformance criteria` block, because chapter 10 will try to build a
  test from each.
- **R13.5, R18.2, R28.3** delegate explicitly to the APS-to-ADS
  contract "outside this specification". They are **negative scope
  statements**, and a criterion that declares something unverifiable is
  a scope exclusion, not a conformance criterion. Candidates for the
  Out of Scope list.

### RFC 2119 misuse

**`MUST NEVER` is not RFC 2119** (`03-requirements.md:61`, DP-3:
"applying this specification MUST NEVER break primary-content
playback"). The intent is unambiguous; the vocabulary is not. Use
`MUST NOT`.

**"Neither MUST be expected" / "Neither MUST be required" inverts the
modal.** `R2.2c` (`:172`) and `R5.4` (`:638`) use MUST where the
intent is a *release* from an obligation — nobody is obliged to expect
anything. As written, "Neither MUST be expected to enforce" reads as
an obligation to expect. The RFC 2119 form is "MUST NOT be required
to", or plain "need not". Both criteria are load-bearing: they are
what keeps a conformance check off the ADS.

**A normative preference with no keyword** —
`06-naming-and-namespaces.md:153`: "the preferred encoding is a
**single attribute** carrying a space-separated string of tokens, NOT
a nested element wrapper". It is an authoring rule with a stated
rationale and a stated exception, i.e. a SHOULD in everything but the
word. Excluded from the table for lack of a keyword; **add SHOULD**
and it becomes N06.13.

**Lowercase "must" carries normative weight in two places**
(`02-actors.md:170`, "it must operate within the validated subset";
`03-requirements.md:157`, "The design must enforce the separation").
Both are restated in uppercase by a criterion (R5.6 / R2.x), so
nothing is lost today — but the lowercase form is invisible to any
keyword-based extraction, including this one.

### DP-2 against the requirement set it governs

**DP-2 is an authoring policy the spec cannot state about itself
without self-reference** (`03-requirements.md:44`): "Obligations are
positive… The spec does NOT enumerate prohibitions." It quotes MUST
and MUST NOT only to illustrate, so it produces no assertion — yet the
table above carries 36 rows whose obligation is a MUST NOT or a
MUST NEVER. DP-2 and the requirement set as authored are in tension;
whether the tension is real (DP-2 governs the *generated spec*, not
the requirements) should be stated in DP-2 itself.

### One criterion declares itself unsettled

**R4.10** (`:398`) mandates that a Player present no ads from a slot
declaring no maximum duration, and then states that the position "is
provisional", diverges from the base specification, and "is open with
the working group rather than settled here". It is carried as a MUST
row because that is what it says, but a chapter-10 test built on it
tests a position the specification tells its reader not to treat as
closed. It is the only criterion in the set that does this.

# Conformance assertions

`[GROUNDED_BY=spec-only]`

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

**Folding rule.** A sentence that restates an obligation already
carried by another sentence **in the same file** is folded into one
row; every folded line is listed below so nothing disappears
silently. A restatement in a **different** file keeps its own row,
because the per-source-doc count (§3) and the orphan analysis (§4)
depend on knowing which file carries the obligation.

Folded restatements — `03-requirements.md`: requirement-body prose at
`:104`, `:107`, `:108`, `:173`, `:176`, `:177`, `:225`, `:228`,
`:282`, `:285`, `:449`, `:451`, `:469`, `:470`, `:520`, `:523`,
`:525`, `:533`, `:636`, `:662`, `:665`, `:671`, `:704`, `:735`,
`:798`, `:982`, `:1027`, `:1029`, `:1034`, `:1036`, `:1135`, `:1137`,
`:1156`, and OOS-1 at `:1250`, all restate a criterion of their own
requirement. `04-use-cases.md`: `:826` restates `:783`, `:1163`
restates `:1154`. `05-dash-linear-interfaces.md`: `:464` restates
`:434`. `08-dash-extension-rules.md`: `:151` restates `:142`.

Excluded, with reason: `03-requirements.md:45`, `:49`, `:52` (DP-2
prose quoting the words MUST / MUST NOT to illustrate an authoring
style, not to impose an obligation); `:1007` (a permission granted to
a *future* edition, binding nothing in this one);
`06-naming-and-namespaces.md:130` (a normative preference —
"the preferred encoding is…" — carrying no RFC 2119 keyword; see §5).

| Assertion ID | Source | Actor | Condition | Obligation |
|--------------|--------|-------|-----------|------------|
| DP03.1 | context/03-requirements.md:24 | spec document | Given a construct being authored | MUST NOT carry information already determined by its own context — its element name and namespace, its parent construct, or another attribute on the same construct. |
| DP03.2 | context/03-requirements.md:30 | spec document | Given a construct justified only by a possible future relaxation | MUST NOT be introduced. |
| DP03.3 | context/03-requirements.md:33 | spec document | Given a construct whose only admissible value matches its own default OR is fixed by another rule | MUST NOT exist in the spec. |
| DP03.4 | context/03-requirements.md:40 | spec document | Given the same value or relationship appearing in several places in the spec or in a generated MPD | Exactly one declaration is canonical and the others MUST be derived from it at runtime, not duplicated in the markup. |
| DP03.5 | context/03-requirements.md:59 | all | (unconditional) | Applying this specification MUST NEVER break primary-content playback; when an opportunity cannot be honoured, graceful skip-and-continue is mandatory. |
| P03.1 | context/03-requirements.md:409 | APS | Given an HTML creative carried as `text/html` | MAY contain inline `<script>` per HTML5 semantics; the script runs under the device's HTML capability contract and MUST NOT be treated as a separate carrier. |
| P03.2 | context/03-requirements.md:841 | APS | Given a non-linear ad slot | The resolution document MAY declare more than one ad form for it, played in sequence. |
| P03.3 | context/03-requirements.md:1066 | spec document | (unconditional) | MUST define a tracking mechanism that lets the ADS instruct the Player which beacons to fire and at which points relative to the ad's presentation. |
| P03.4 | context/03-requirements.md:1265 | APS | Given a sender that needs a scripted creative (OOS-4) | MUST wrap the script inside an HTML document and use `text/html` per R15; raw `application/javascript` is out of scope. |
| R1.1 | context/03-requirements.md:116 | Player | Given an `MPD` carrying an SGAI construct the Player does not implement | MUST ignore the unknown construct and continue playing the primary content uninterrupted. |
| R1.2 | context/03-requirements.md:120 | spec document | Given a new SGAI construct introduced by this proposal | MUST be expressed through §5.2.1 foreign-namespace open content (DR-2 / DR-3), §5.10 application-level Event Streams, or §5.8.4.8 / §5.8.4.9 vendor descriptors; MUST NOT be introduced by a path violating the §5.3.2.6 / §8.15 / §7.3 / RFC 4337 chain (DR-1, DR-5). Annex F (DR-4) is admissible only with a genuine segment-delivery need plus a new Interoperability Point URI. |
| R1.3 | context/03-requirements.md:134 | spec document | (unconditional) | MUST NOT alter or override the semantics of any pre-existing MPEG-DASH 6th edition construct. |
| R1.4 | context/03-requirements.md:137 | Player | Given resolving or rendering an accepted ad fails at runtime (decode error, malformed candidate, mid-ad network loss) | MUST abort that ad and continue playing the primary content uninterrupted. |
| R2.1 | context/03-requirements.md:153 | Publisher | Given an ad slot declared in the `MPD` | Constraints applicable to the slot (max duration, opt-in policies, layout templates) MUST be declared by the Publisher in the `MPD`, not inferred at runtime by ADS, APS or Player. |
| R2.2 | context/03-requirements.md:157 | all | Given an ad opportunity being resolved | The ADS MUST decide which ads to serve and output its decision document; the APS MUST convert that output into the resolution document; neither MUST be expected to enforce Publisher-declared constraints. |
| R2.3 | context/03-requirements.md:162 | Player | Given a resolution document | MUST validate the candidates against the Publisher-declared constraints and render only those that satisfy them. |
| R2.4 | context/03-requirements.md:165 | spec document | Given a new mechanism introduced by the specification | MUST be expressible within the four-actor contract; a mechanism requiring an actor to take on a responsibility outside its role MUST be rejected or redesigned. |
| R3.1 | context/03-requirements.md:597 | spec document | (unconditional) | MUST enumerate the supported device classes and, for each, the expected behaviour for every ad opportunity type covered by the use cases. |
| R3.2 | context/03-requirements.md:600 | Player | Given any supported device class and any ad opportunity type defined in the spec | MUST produce a defined behaviour (render, fall back, or skip); undefined behaviour is non-conforming. |
| R3.3 | context/03-requirements.md:604 | Player | Given an ad form (video, image, HTML) the device class cannot render | MUST NOT attempt to render it. |
| R4.1 | context/03-requirements.md:297 | Publisher | Given any ad slot, linear or non-linear, defined in the `MPD` | MUST declare a maximum duration on it. |
| R4.2 | context/03-requirements.md:300 | Player | Given the cumulative duration of accepted candidates would exceed the Publisher-declared cap | MUST stop rendering at the cap boundary, even if the stop falls mid-ad. |
| R4.3 | context/03-requirements.md:304 | Player | (unconditional) | MUST NOT extend a slot beyond the Publisher-declared cap, regardless of ADS metadata or candidate count. |
| R4.4 | context/03-requirements.md:307 | ADS | Given the cumulative duration of the ADS's returned candidates exceeds the cap | A conformance check on the ADS MUST NOT fail on that ground alone; the ADS is not required to respect the cap. |
| R4.5 | context/03-requirements.md:311 | Player | Given an accepted candidate's actual rendered length exceeds its declared duration | MUST enforce the cap against actual length, not declared length ("trim during play"). |
| R5.1 | context/03-requirements.md:479 | APS | Given each ad candidate in the resolution document | MUST carry one or more renderable presentation options (form plus layout) as an ordered list whose document order is the preference order; no maximum, no minimum beyond one. |
| R5.2 | context/03-requirements.md:487 | Player | Given the presentation options of an accepted candidate | MUST evaluate them in document order and render the first option whose form and layout the device can satisfy. |
| R5.3 | context/03-requirements.md:491 | Player | Given a candidate carrying no form renderable on the device | MUST skip it and fall through to the next candidate; once candidates are exhausted the Player MUST continue with the primary content. |
| R5.4 | context/03-requirements.md:495 | all | Given the ADS and the APS producing candidates | Neither MUST be required to maintain a device-class matrix or a per-Player capability view. |
| R5.5 | context/03-requirements.md:498 | APS | Given an ad candidate | MAY carry multiple presentation options, each pairing a form with an admissible layout, as a single ordered list whose document order is the preference order. |
| R5.6 | context/03-requirements.md:502 | Player | Given presentation-option selection on an accepted candidate | MUST walk the options in document order, checking each against (a) device capabilities and (b) the Publisher-declared allowed layouts, and render the first that satisfies both; an option failing either MUST NOT be rendered. |
| R5.7 | context/03-requirements.md:509 | Player | Given no presentation option on a candidate satisfies R5.6 | MUST skip that candidate and fall through to the next candidate in the resolution document (preserving the R7 order) or, when exhausted, to the primary content. |
| R6.1 | context/03-requirements.md:1048 | spec document | (unconditional) | MUST specify how in-band ad tracking beacons are carried in the resolution document. |
| R6.2 | context/03-requirements.md:1050 | APS | Given tracking beacons carried in the resolution document | SHOULD carry them as `<Event>` entries inside an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015` in the ad `MPD` or sub-`MPD`. |
| R6.3 | context/03-requirements.md:1055 | spec document | Given the callback scheme cannot express the required semantics AND a gap analysis per R9 is documented | A new tracking carrier MAY be introduced; absent both conditions it MUST NOT. |
| R6.4 | context/03-requirements.md:1059 | Player | Given unknown namespaces on tracking-related extension elements | MUST safely ignore them, per the DASH extension rules invoked by R1. |
| R7.1 | context/03-requirements.md:542 | Player | Given a resolution document with more than one ad candidate | MUST play the candidates in the order the resolution document declares, except for candidates dropped under R7.2 / R7.3. |
| R7.2 | context/03-requirements.md:546 | Player | Given a candidate with no form renderable on the device (R3 / R5) | MAY drop it. |
| R7.3 | context/03-requirements.md:548 | Player | Given a candidate whose declared duration would push the cumulative slot duration past the cap (R4) | MAY drop it before playback ("drop before play"). |
| R7.4 | context/03-requirements.md:551 | Player | Given the candidates remaining after R7.2 / R7.3 | MUST NOT re-order, deduplicate, or otherwise rearrange them. |
| R7.5 | context/03-requirements.md:554 | Player | Given an accepted candidate whose actual rendered length exceeds the cap | MUST trim mid-rendering ("trim during play") per R4. |
| R8.1 | context/03-requirements.md:1198 | spec document | Given a new construct introduced by the proposal | MUST be accompanied by an inline justification stating why an existing MPEG-DASH construct could not be reused. |
| R8.2 | context/03-requirements.md:1201 | spec document | Given a deliberate omission of an existing MPEG-DASH construct a reader might expect to see reused | MUST be documented inline with the design decision. |
| R9.1 | context/03-requirements.md:1216 | spec document | (unconditional) | MUST reuse existing MPEG-DASH machinery (events, manifests, presentations, schemes) wherever possible. |
| R9.2 | context/03-requirements.md:1219 | spec document | Given an existing construct can be made to fit | A new construct MUST NOT be introduced. |
| R9.3 | context/03-requirements.md:1221 | spec document | Given a new construct is about to be introduced | MUST first consider whether an extension to an existing construct would suffice, and document the outcome of that consideration. |
| R10.1 | context/03-requirements.md:1237 | spec document | Given the spatial arrangement of overlays | MUST be delegated to HTML5 / CSS layout primitives. |
| R10.2 | context/03-requirements.md:1239 | spec document | (unconditional) | MUST NOT define a parallel layout standard for overlay placement. |
| R10.3 | context/03-requirements.md:1241 | spec document | Given position semantics inside a layout (left, right, top, bottom) | Out of scope for the spec; MUST be expressed via the Positioning Templates section using HTML5 / CSS primitives. |
| R11.1 | context/03-requirements.md:181 | spec document | Given the normative chapters of the spec | MUST NOT cite a specific VAST version as required. |
| R11.2 | context/03-requirements.md:183 | Player | Given an ADS that may or may not use VAST | A Player MUST be able to operate either way; it never talks to the ADS and reads only the resolution document the APS produces. |
| R11.3 | context/03-requirements.md:191 | spec document | Given any reference to VAST in the spec | MUST sit in an annex or in a non-normative note explicitly flagged as illustrative. |
| R12.1 | context/03-requirements.md:378 | spec document | Given the accepted ad-type and visual-placement values | They are exactly those enumerated in R12, each mapped to its IAB definition; the spec MUST NOT accept a value outside the enumeration and MUST cite the IAB source for the values it accepts. |
| R12.2 | context/03-requirements.md:382 | Publisher | Given a Publisher declaring allowed layouts on a slot | MUST use names drawn from the enumerated set, each mapping 1:1 to an IAB-defined ad type or visual placement; Publisher-private names and IAB values outside the set MUST NOT appear. |
| R12.3 | context/03-requirements.md:387 | APS | Given the resolution document the APS emits | MUST NOT carry form metadata for an ad type or visual placement outside the enumerated set; conformance is checked against the resolution document, not the ADS's decision document. |
| R12.4 | context/03-requirements.md:392 | spec document | Given each enumerated layout | The spatial bound the IAB CTV Ad Format Guidelines declare for that layout is inherited by normative reference; no dimensional attribute is introduced on the slot declaration. `[no RFC 2119 keyword]` |
| R13.1 | context/03-requirements.md:1080 | APS | Given the resolution document carries tracking instructions | MUST express them as DASH callback events (or an equivalent baseline DASH construct), with timings relative to the ad's presentation timeline. |
| R13.2 | context/03-requirements.md:1087 | Player | Given an ad accepted for rendering | MUST execute the tracking schedule read from the resolution document, firing each beacon at its specified relative time. |
| R13.3 | context/03-requirements.md:1092 | Player | Given R4 trims the ad before a scheduled beacon's time | MUST stop firing remaining beacons at the trim boundary. |
| R13.4 | context/03-requirements.md:1095 | spec document | (unconditional) | MUST NOT introduce a new tracking event scheme; reuse of the DASH baseline callback mechanism is mandatory. |
| R13.5 | context/03-requirements.md:1098 | all | Given beacon-transcription fidelity (the APS neither adds, removes, nor reorders the beacons the ADS declared) | It is part of the APS-to-ADS contract those parties maintain directly, outside this specification (R18); the resolution document cannot show it. `[no RFC 2119 keyword]` |
| R14.1 | context/03-requirements.md:866 | Player | Given a resolution document for a non-linear slot declaring more than one ad form | MUST present the forms in sequence, in the order they appear in the resolution document, each starting when the previous one ends. |
| R14.2 | context/03-requirements.md:871 | Player | Given the cumulative duration of a sequence of non-linear forms | MUST enforce the Publisher-declared slot cap (R4) against it, trimming or dropping per R4 / R7 when it would exceed the slot's opportunity window. |
| R14.3 | context/03-requirements.md:875 | spec document | (unconditional) | MUST NOT introduce a construct implying or requiring the parallel rendering of two or more non-linear ad forms, and MUST NOT add a "render-then" primitive beyond the declared form order. |
| R15.1 | context/03-requirements.md:414 | spec document | Given creative carrier types are discussed anywhere in the spec | MUST enumerate exactly video, image and HTML; new carrier types MUST NOT be added in annexes, examples, or implementation notes. |
| R15.2 | context/03-requirements.md:418 | all | Given ad candidates in the APS's resolution document and forms declared by the Publisher | MUST carry a creative whose mimeType falls under one of the three admissible categories; conformance is checked against the resolution document and the Publisher's declaration. |
| R15.3 | context/03-requirements.md:426 | Player | Given a candidate whose creative carrier mimeType is outside the admissible set | MAY skip it; such a candidate signals a non-conformant ADS, APS or Publisher. |
| R16.1 | context/03-requirements.md:624 | Player | Given a pause-to-play transition by the viewer | MUST remove any rendered pause-ad form from the screen within one rendering frame. |
| R16.2 | context/03-requirements.md:627 | Player | Given the same pause-to-play transition | MUST cease firing tracking beacons scheduled for the dismissed pause-ad. |
| R17.1 | context/03-requirements.md:910 | Player | Given the viewer is paused inside a pause-ad window AND an overlay is active | Renders the pause-ad form and suspends the overlay rendering. `[no RFC 2119 keyword]` |
| R17.2 | context/03-requirements.md:914 | Player | Given a resume from pause | Dismisses the pause-ad (per R16) and restores the overlay rendering if the overlay slot window is still active. `[no RFC 2119 keyword]` |
| R17.3 | context/03-requirements.md:917 | Player | Given the overlay slot window expired during the pause | Keeps the overlay surface clear on resume. `[no RFC 2119 keyword]` |
| R17.4 | context/03-requirements.md:920 | spec document | (unconditional) | Carries no construct that lets the Publisher, the ADS or the APS invert the pause-ad-over-overlay priority. `[no RFC 2119 keyword]` |
| R18.1 | context/03-requirements.md:213 | spec document | (unconditional) | Documents the MPD event URL pattern (Player-visible input, served by the APS) and the resolution document format (Player-visible output, produced by the APS). `[no RFC 2119 keyword]` |
| R18.2 | context/03-requirements.md:217 | all | Given the APS-to-ADS contract for ad-decisioning invocation, and the Publisher's arrangement with the APS for the event URL | Established and maintained by those parties directly, outside this specification, except for the parameters this specification defines on the Player's resolution request (R29). `[no RFC 2119 keyword]` |
| R19.1 | context/03-requirements.md:649 | Player | Given any ad form, linear or non-linear, being presented | MUST render it at the same playback speed as the primary content at the moment of presentation. |
| R19.2 | context/03-requirements.md:652 | Player | Given the primary content is playing at a speed other than 1x | MUST NOT force the ad to 1x; the ad follows the primary content's speed. |
| R19.3 | context/03-requirements.md:655 | Player | Given an ad form's effective on-screen duration | MUST compute it as `duration / playback_speed`, not as the raw `duration`; cap enforcement (R4) and beacon scheduling (R13) still operate on the presentation-timeline `duration`. |
| R20.1 | context/03-requirements.md:965 | Player | Given two or more ad opportunity windows of the same family overlapping in time in the primary `MPD` | MUST select the first overlapping window and attempt to resolve its resolution document; MUST resort to a subsequent window ONLY when the first's resolution document is inaccessible (no APS response, transport failure, or a final HTTP status other than `200`); when it is accessible — including a `200` carrying no candidates per R30 — MUST NOT fall through. |
| R21.1 | context/03-requirements.md:690 | Player | Given a pause-ad form to present | MAY present it fullscreen or as a partial overlay over the paused primary frame; when fullscreen, MAY release the resources held by the primary content and by any pre-existing overlay; when partial, MUST keep at most one non-linear ad form active during the pause (R22), suspending any coexisting overlay (R17). |
| R22.1 | context/03-requirements.md:1012 | Player | Given any instant `t` | MUST keep at most ONE non-linear ad form active on the screen and MUST NOT present two or more simultaneously. |
| R23.1 | context/03-requirements.md:1124 | spec document | (unconditional) | MUST define, in the SVTA Ads WG namespace, the extension elements carrying generic application-level metadata with no native DASH carrier (`AdSystem`, `AdTitle`, etc.), and MUST state that emitting them and reading them are both optional. |
| R24.1 | context/03-requirements.md:1143 | APS | Given a non-AV ad form (`mediaType` in {html, image, …}) carried in the resolution document | The asset URL MUST NOT be expressed as `@mimeType` on an AdaptationSet or Representation reached through any path bound by RFC 4337 (DR-1, DR-5), and MUST be carried via one of the §5.2.1 / §5.10 / §5.8.4.x carriers enumerated by DR-6. |
| R25.1 | context/03-requirements.md:721 | Player | Given live content and a viewer paused inside a pause-ad window | MUST keep its presentation time frozen inside that window for the full duration of the pause, regardless of the live edge advancing; any decision to resume at the live edge MUST be treated as a Player action occurring after the resume, outside the pause-ad window. |
| R26.1 | context/03-requirements.md:750 | all | Given the background element of a side-by-side / double-box layout | MUST be carried as a composition attribute of the slot / layout, not as a separate presentation option (R5). |
| R26.2 | context/03-requirements.md:753 | Player | Given a side-by-side / double-box layout | MUST composite the primary content and the ad as the two boxes; MUST place an advertiser-supplied background element in the uncovered bands; with no background element the uncovered region renders as black. |
| R26.3 | context/03-requirements.md:758 | Player | Given a side-by-side layout whose ad is a video (two concurrent video decoders plus an image surface) | MUST NOT select it on a single-decoder device (R3 / R5); a non-video element — the ad as image / HTML, or the image background — MUST NOT be selected on a device that cannot composite that surface type on top of video. |
| R27.1 | context/03-requirements.md:806 | all | Given an L-shape / squeezeback presentation option | MUST carry exactly one ad creative, the full-frame background creative, as an image, a video or a web/HTML surface (R15); the shrunk primary content is not a supplied creative. |
| R27.2 | context/03-requirements.md:811 | Player | Given an L-shape layout | MUST composite its two elements — the full-frame ad creative in the background and the shrunk primary content on top — with the creative covering the whole frame and the primary content occupying its declared region. |
| R27.3 | context/03-requirements.md:816 | Player | Given an L-shape whose full-frame ad creative is a video (second video decoder) | The L-shape is NOT satisfiable on a single-decoder device (R3 / R5); an image / HTML full-frame creative MUST NOT be selected on a device that cannot composite that surface type together with video. |
| R28.1 | context/03-requirements.md:1162 | APS | Given an ad candidate in the resolution document carrying a ClickThrough | The ClickThrough URL and any accompanying click-tracking URL(s) MUST be carried in the normative carrier this specification defines, and not elsewhere. |
| R28.2 | context/03-requirements.md:1171 | Player | Given the viewer activates a ClickThrough | MUST read the ClickThrough URL and fire its associated click-tracking. |
| R28.3 | context/03-requirements.md:1174 | all | Given whether a ClickThrough the ADS declared reaches the resolution document at all | It is part of the APS-to-ADS contract those parties maintain directly, outside this specification (R18). `[no RFC 2119 keyword]` |
| R29.1 | context/03-requirements.md:239 | spec document | Given the reserved capability parameters | They are inputs about the device, not conclusions about which ad experiences can be served; deriving the second from the first is the APS's job. The reservation is a set, not a single value. `[no RFC 2119 keyword]` |
| R29.2 | context/03-requirements.md:246 | Player | Given the resolution request the Player issues | Sending a reserved parameter is OPTIONAL: a conformant Player MAY send all of them, some of them, or none. |
| R29.3 | context/03-requirements.md:248 | Player | Given the Player has no value for a reserved parameter, or does not disclose it | MUST omit that parameter entirely rather than send it with an empty or placeholder value. |
| R29.4 | context/03-requirements.md:252 | Player | Given a parameter that is not one of the reserved names | MUST carry a vendor-specific prefix, so reserved names added in a later edition cannot collide with it. |
| R29.5 | context/03-requirements.md:255 | APS | Given a resolution request missing any or all reserved parameters | MUST tolerate the absence and MUST be able to produce ad candidates without receiving any of them. |
| R29.6 | context/03-requirements.md:259 | spec document | Given the reserved parameter set | MUST be able to express the capability axes that distinguish the device classes the specification enumerates (R3.1); a set that cannot tell two enumerated classes apart does not satisfy this. |
| R29.7 | context/03-requirements.md:263 | spec document | Given a reserved parameter absent from the resolution request | Its value is undetermined — not an assertion that the device lacks the capability; the spec does not define how an APS resolves an undetermined value, and two APSs resolving it differently are both conformant. `[no RFC 2119 keyword]` |
| R30.1 | context/03-requirements.md:570 | APS | Given an opportunity that resolved with no ads | MUST be expressed as a resolution document carrying no candidates, and MUST NOT be expressed as an error response or as a response without a body. |
| IN01.1 | context/01-intro.md:47 | spec document | Given each new construct the spec introduces | MUST apply the backward-compat verification checklist of `07-backward-compat-checklist.md`. |
| A2.1 | context/02-actors.md:48 | ADS | Given the ADS responds to an ad request | MAY emit a decision format other than VAST; it performs no conversion into the MPD-native / SGAI format. |
| UC04.1 | context/04-use-cases.md:294 | APS | Given a candidate's presentation option | MAY be a partial-screen layout (L-shape / squeezeback, or side-by-side / double-box). |
| UC04.2 | context/04-use-cases.md:764 | Player | Given a legacy Player encountering an unrecognised event type or construct in the manifest (UC-07) | MUST skip the unknown construct and continue playing the primary content as if it were not present. |
| UC04.3 | context/04-use-cases.md:781 | Publisher | Given live / real-time content whose opportunity falls through to a legacy Player | SHOULD treat the opportunity as an expected loss on legacy Players, not as an error. |
| UC04.4 | context/04-use-cases.md:783 | Publisher | Given non-live / VOD content carrying an SGAI construct | MAY author a standard linear break alongside it, using only baseline MPEG-DASH 6th edition constructs a legacy Player already renders. |
| UC04.5 | context/04-use-cases.md:783 | Publisher | Given non-live / VOD content where monetising the opportunity matters | SHOULD author that standard linear break as the legacy fallback. |
| UC04.6 | context/04-use-cases.md:818 | spec document | Given any new construct the proposal introduces | MUST be expressible via extension points that produce the skip-and-continue outcome on legacy Players. |
| UC04.7 | context/04-use-cases.md:839 | Player | Given a pause-ad form presented while a coexisting overlay is active (UC-08) | MAY present it fullscreen or as a partial overlay; either way it is the only ad surface visible during the pause and the overlay is suspended (R17 / R22). |
| UC04.8 | context/04-use-cases.md:1154 | APS | Given a side-by-side / double-box layout leaving bands uncovered (UC-10) | A third element, a still-image background (never video, never web/HTML), MAY fill the uncovered region. |
| I05.1 | context/05-dash-linear-interfaces.md:34 | APS | Given an APS that holds a view of the device | MAY narrow the option list and send a single form; the choice then sits with the APS and the Player-visible interface is unchanged. |
| I05.2 | context/05-dash-linear-interfaces.md:382 | spec document | Given the non-linear chapters of the spec carry non-AV asset URLs (HTML, image, other) | MUST carry them outside the AdaptationSet axis, via one of the carriers enumerated in DR-6. |
| I05.3 | context/05-dash-linear-interfaces.md:432 | spec document | Given the ClickThrough carrier compared against the best-effort metadata carrier of R23 | The click MUST work cross-Player and MUST NOT be silently ignored; the carrier is normative and interoperable (R28). |
| I05.4 | context/05-dash-linear-interfaces.md:433 | Player | Given `<AdSystem>` / `<AdTitle>` / `<Advertiser>` carried as SVTA Ads WG namespaced attributes or elements (R23) | MAY safely ignore them; dropping them breaks nothing in the ad presentation. |
| I05.5 | context/05-dash-linear-interfaces.md:434 | APS | Given VAST `<UniversalAdId>`, for which this spec mandates no DASH carrier | MAY propagate it on a best-effort SVTA-namespaced attribute (R23); it otherwise stays on the VAST / ADS side. |
| N06.1 | context/06-naming-and-namespaces.md:4 | spec document | Given any new construct introduced by the SGAI spec | MUST follow the naming conventions of `06-naming-and-namespaces.md`. |
| N06.2 | context/06-naming-and-namespaces.md:22 | spec document | Given a new event scheme introduced by this spec | MUST use the year-pinned pattern `urn:svta:dash:<construct>:<year>` under the SVTA Ads WG namespace. |
| N06.3 | context/06-naming-and-namespaces.md:37 | Player | Given a Player implementing edition N + 1 | SHOULD recognise both the `:N:` and `:N+1:` URIs and treat them per that edition's backward-compatibility rules. |
| N06.4 | context/06-naming-and-namespaces.md:48 | APS | Given an implementation carrying tracking beacons for ads introduced by this spec | MUST reuse the MPEG-DASH 6th edition baseline callback scheme; a parallel tracking scheme under `urn:svta:dash:*` is out of scope. |
| N06.5 | context/06-naming-and-namespaces.md:55 | spec document | Given a Qualabs-private experimental extension that is not part of this specification | MUST use the Qualabs vendor namespace `urn:qualabs:<feature>:<year>`. |
| N06.6 | context/06-naming-and-namespaces.md:87 | spec document | Given a baseline DASH element authored alongside an SGAI extension element | MUST honour the DR-3 authoring rule: a baseline child legacy clients must process goes at a baseline position, a child to be hidden from legacy goes inside the foreign-namespace subtree. |
| N06.7 | context/06-naming-and-namespaces.md:94 | spec document | Given a construct whose semantics change in a new edition | MUST use a new `<year>` suffix on its scheme URI. |
| N06.8 | context/06-naming-and-namespaces.md:97 | spec document | Given a construct whose semantics are unchanged in a new edition | MAY keep its existing URI. |
| N06.9 | context/06-naming-and-namespaces.md:99 | spec document | Given the spec's chapter 2 (Normative references) | MUST list the URIs introduced by the current edition explicitly. |
| N06.10 | context/06-naming-and-namespaces.md:108 | spec document | Given the accepted layout names for overlay templates | MUST reference the IAB-defined values without inventing new layout names at chapter level. |
| N06.11 | context/06-naming-and-namespaces.md:113 | spec document | Given the layout vocabulary | MUST map 1:1 to IAB-defined ad-type values; no publisher-private or spec-private layout names are admissible. |
| N06.12 | context/06-naming-and-namespaces.md:120 | spec document | Given a component that is in essence the same as one already defined in MPEG-DASH 6th edition or its profile annexes | MUST reuse the existing baseline construct with all its characteristics — name, default values, permitted value domain, units, semantics. |
| B07.1 | context/07-backward-compat-checklist.md:5 | spec document | Given every new construct the spec introduces | MUST follow the backward-compat checklist. |
| B07.2 | context/07-backward-compat-checklist.md:13 | spec document | Given the spec's chapter 4 (Conformance) and chapter 10 (Test cases) | MUST apply the verification procedure this checklist defines. |
| B07.3 | context/07-backward-compat-checklist.md:17 | spec document | Given each new construct C | MUST explicitly answer the checklist's eight questions in C's specification chapter. |
| B07.4 | context/07-backward-compat-checklist.md:19 | spec document | Given an unanswered checklist item | SHOULD block publication. |
| B07.5 | context/07-backward-compat-checklist.md:37 | spec document | Given the construct's chapter | MUST name the applicable DR-N rule from `08-dash-extension-rules.md` for C's placement. |
| B07.6 | context/07-backward-compat-checklist.md:48 | spec document | Given a new namespace | The construct MUST be in an extension namespace per `06-naming-and-namespaces.md`. |
| B07.7 | context/07-backward-compat-checklist.md:53 | spec document | Given a construct invoking Annex F (DR-4) | The chapter MUST state which new Interoperability Point URI is published in `MPD@profiles` and justify why the DR-6 carriers are not sufficient. |
| B07.8 | context/07-backward-compat-checklist.md:67 | spec document | Given the legacy-Player behaviour walk-through for C | MUST be present in C's chapter as an explicit prose paragraph, not implicit. |
| B07.9 | context/07-backward-compat-checklist.md:79 | spec document | Given C removed from the document | MUST still leave a document that parses and plays. |
| B07.10 | context/07-backward-compat-checklist.md:84 | spec document | Given each new construct | MUST have a corresponding chapter-10 test case modelled on UC-07. |
| B07.11 | context/07-backward-compat-checklist.md:91 | Player | Given a legacy Player encountering C in the UC-07 test | MUST ignore C in every case — silent skip, no tracking beacon for C. |
| B07.12 | context/07-backward-compat-checklist.md:99 | Publisher | Given non-live / VOD content in the UC-07 test | MAY author a standard linear break alongside C, using only baseline constructs a legacy Player renders. |
| B07.13 | context/07-backward-compat-checklist.md:127 | spec document | Given the construct's chapter | MUST link to this checklist and confirm each item is satisfied. |
| B07.14 | context/07-backward-compat-checklist.md:128 | spec document | Given a construct chapter omitting the checklist confirmation | Reviewers SHOULD reject it. |
| B07.15 | context/07-backward-compat-checklist.md:144 | spec document | Given a construct whose carrier fits none of the DR-6 options (a) / (b) / (c) | MUST justify why Annex F (DR-4) is invoked and what new Interoperability Point URI is published. |
| B07.16 | context/07-backward-compat-checklist.md:146 | spec document | Given the carrier classification of C | MUST be stated explicitly in C's chapter; leaving it implicit is a checklist failure. |
| B07.17 | context/07-backward-compat-checklist.md:151 | spec document | Given the shipped spec | SHOULD carry an audit table summarising the checklist status for every new construct; a `FAIL` in any column blocks publication. |
| B07.18 | context/07-backward-compat-checklist.md:163 | spec document | Given any of the enumerated anti-patterns that silently break the ignore-if-unknown contract | Reviewers MUST flag them. |
| B07.19 | context/07-backward-compat-checklist.md:178 | APS | Given non-AV ad assets | MUST be carried via one of the DR-6 carriers, never via a non-MP4 `@mimeType` on an AdaptationSet or Representation reached via `<ImportedMPD>` (DR-1) or inside a ListMPD-level Period (DR-5). |
| D08.1 | context/08-dash-extension-rules.md:12 | spec document | Given a DASH edition bump | `08-dash-extension-rules.md` MUST be re-validated section by section; rules are not blindly carried forward. |
| D08.2 | context/08-dash-extension-rules.md:22 | APS | Given a document bound to the Single-Period Static profile | A vendor profile URI MAY be appended in `@profiles`, but it can only ADD constraints, never relax the RFC 4337 `@mimeType` restriction. |
| D08.3 | context/08-dash-extension-rules.md:30 | APS | Given a non-MP4 ad asset in a sub-MPD referenced from a ListMPD via `<ImportedMPD>` | MUST be carried via one of the DR-6 carriers, not on an AdaptationSet or Representation. |
| D08.4 | context/08-dash-extension-rules.md:38 | spec document | Given DASH §5.2.1 open content | A foreign-namespace element MAY appear as a child of any DASH container, including `<Period>`, `<AdaptationSet>`, `<Event>`, and other foreign-namespace elements. |
| D08.5 | context/08-dash-extension-rules.md:41 | APS | Given an MPD carrying foreign-namespace attributes and elements | MUST be authored such that, once those are removed, the result is still a valid DASH document. |
| D08.6 | context/08-dash-extension-rules.md:97 | APS | Given per-AdaptationSet `@profiles` | MUST be a subset of MPD-level `@profiles`, so an SPS-rooted document cannot promote one AdaptationSet to a broader profile to escape RFC 4337. |
| D08.7 | context/08-dash-extension-rules.md:136 | APS | Given a Period whose `@duration` is non-zero | MUST contain at least one AdaptationSet (§5.3.2.2 Table 4). |
| D08.8 | context/08-dash-extension-rules.md:142 | APS | Given a slot whose tracking requires presentation-time alignment across a non-zero duration | MUST carry at least one AdaptationSet in that Period, or carry the asset and tracking outside any non-zero-duration Period; the empty-Period tracking carrier is closed. |
| G99.1 | context/99-glossary.md:51 | Player | Given a capability parameter on the resolution request | MAY be attached; sending any of them is optional, one the Player cannot or will not populate is omitted rather than sent empty, and an absent parameter means undetermined, not unsupported (R29). |
| G99.2 | context/99-glossary.md:71 | ADS | Given the ADS's decision document | MAY be a format other than VAST; the ADS is not bound to VAST. |

## 1. Assertions per R

Counted over the `R<N>.<n>` conformance-criterion rows only (92 rows).

R1: 4 · R2: 4 · R3: 3 · R4: 5 · R5: 7 · R6: 4 · R7: 5 · R8: 2 ·
R9: 3 · R10: 3 · R11: 3 · R12: 4 · R13: 5 · R14: 3 · R15: 3 ·
R16: 2 · R17: 4 · R18: 2 · R19: 3 · R20: 1 · R21: 1 · R22: 1 ·
R23: 1 · R24: 1 · R25: 1 · R26: 3 · R27: 3 · R28: 3 · R29: 7 ·
R30: 1

Three requirements carry an obligation in their **prose body that no
criterion of theirs restates**, so the criterion count understates
them: R13 (+P03.3, the spec MUST define the tracking mechanism —
R6.1 has the equivalent criterion, R13 does not), R14 (+P03.2, the
resolution document MAY declare several forms for one slot — R14.1
binds only the Player's reading of it), R15 (+P03.1, `text/html` MAY
carry inline `<script>` and that script is not a separate carrier).

## 2. Assertions per actor

| Actor | Count |
|---|---|
| Player | 50 |
| APS | 24 |
| Publisher | 7 |
| ADS | 3 |
| spec document | 64 |
| all | 9 |
| **Total** | **157** |

The shape is the model working as designed: the Player carries the
runtime enforcement burden (R2 / R4 / R5 / R7), the `spec document`
bucket carries the governance and authoring obligations (R8 / R9 /
R10 plus all of `06` and `07`), and the ADS is bound by only three
assertions — R4.4 and A2.1 / G99.2, all three of them *freedoms*
rather than duties, which is exactly what R2 and R18 intend.

## 3. Assertions per source doc

| Source doc | Count |
|---|---|
| `../context/01-intro.md` | 1 |
| `../context/02-actors.md` | 1 |
| `../context/03-requirements.md` | 101 |
| `../context/04-use-cases.md` | 8 |
| `../context/05-dash-linear-interfaces.md` | 5 |
| `../context/06-naming-and-namespaces.md` | 12 |
| `../context/07-backward-compat-checklist.md` | 19 |
| `../context/08-dash-extension-rules.md` | 8 |
| `../context/99-glossary.md` | 2 |
| **Total** | **157** |

`03-requirements.md` splits into 92 criterion rows, 5 design-principle
rows (DP03) and 4 prose rows (P03).

## 4. Orphan assertions

MUST / SHOULD / MAY obligations found **outside**
`../context/03-requirements.md` that no requirement absorbs.

**Naming and versioning — no R governs it.** `06-naming-and-namespaces.md`
is normative from its first line and nothing in the requirement set
points at it. R1.2 enumerates the admissible *extension points*, not
the naming policy.

- **N06.1** (`:4`), **N06.2** (`:22`), **N06.5** (`:55`),
  **N06.7** (`:94`), **N06.8** (`:97`), **N06.9** (`:99`),
  **N06.12** (`:120`) — URN pattern, year-pinning, vendor namespace,
  per-edition URI lifecycle, chapter-2 listing, and reuse of a
  baseline construct *with all its characteristics*. **A new
  governance requirement is implied** (naming / namespace /
  versioning policy); alternatively N06.12 absorbs into R9 as a
  criterion, since R9.1's "reuse wherever possible" is strictly
  weaker than "reuse with name, defaults, value domain, units and
  semantics".
- **N06.3** (`:37`) — the only obligation in `06` that binds a
  *runtime* actor: a Player implementing edition N + 1 SHOULD
  recognise both `:N:` and `:N+1:` URIs. It is a cross-edition
  compatibility duty that R1 (single-edition backward compat) does
  not reach. **Absorb into R1 as a criterion**, or into the new
  naming R.
- **N06.6** (`:87`) — the DR-3 authoring rule (baseline children
  visible to legacy go at a baseline position). R1.2 cites DR-2 /
  DR-3 as extension points but imposes no authoring rule.
  **Absorb into R1.2.**
- **N06.10 / N06.11** (`:108`, `:113`) — the spec MUST reference
  IAB-defined layout values and map the vocabulary 1:1. Adjacent to
  R12.1 / R12.2 but a different test: R12 governs the values in the
  MPD and in the resolution document, these govern the spec's own
  chapter-level vocabulary. **Absorb into R12 as a spec-document
  criterion.**

**Publisher-side legacy authoring — no R binds the Publisher.**

- **UC04.3** (`04-use-cases.md:781`), **UC04.4 / UC04.5** (`:783`),
  **B07.12** (`07-backward-compat-checklist.md:99`) — for live
  content the Publisher SHOULD treat a legacy fall-through as an
  expected loss; for VOD the Publisher MAY, and SHOULD where
  monetisation matters, author a standard linear break alongside the
  SGAI construct. R1 binds the Player (R1.1), the spec (R1.2, R1.3)
  and the Player again (R1.4) — **never the Publisher**, even though
  the Publisher is the actor who authors the fallback. **Absorb into
  R1 as a Publisher criterion.**

**Publication gating — procedural obligations with no R behind them.**

- **B07.4** (`:19`), **B07.14** (`:128`), **B07.17** (`:151`),
  **B07.18** (`:163`) — unanswered checklist items SHOULD block
  publication, reviewers SHOULD reject unconfirmed chapters, the spec
  SHOULD ship an audit table, reviewers MUST flag the anti-patterns.
  These gate the spec's release and live only in `07`. **Absorb into
  the R8 / R9 governance group**, or accept `07` as a normative annex
  the requirement set cites explicitly.
- **IN01.1** (`01-intro.md:47`) — the index line stating that the spec
  MUST apply the checklist to each new construct is today the only
  place the requirement set is told the checklist exists, and it is a
  navigational index rather than a requirement. Same fix as above.
- **D08.1** (`08-dash-extension-rules.md:12`) — every DR-N MUST be
  re-validated section by section on a DASH edition bump. Governance
  of the context set itself; no R covers it. **Absorb into the R8 /
  R9 governance group.**

**DASH baseline facts that a requirement depends on but does not state.**

- **D08.7 / D08.8** (`:136`, `:142`) — DR-7: a non-zero-duration
  Period MUST carry at least one AdaptationSet, which closes the
  "empty-Period tracking carrier" design. It constrains any carrier
  R6 or R24 picks and **neither requirement cites it**. **Absorb into
  R6 (tracking carrier) and R24 (non-AV asset carrier).**
- **D08.5** (`:41`) — the MPD MUST stay a valid DASH document once
  foreign-namespace content is removed. This is the precondition that
  makes R1.1 achievable, stated nowhere in R1. **Absorb into R1.2.**
- **D08.6** (`:97`) — per-AdaptationSet `@profiles` MUST be a subset
  of MPD-level `@profiles`. The baseline fact that closes the escape
  hatch R24.1 depends on. **Absorb into R24 as supporting text**, or
  leave it as a DR that R24 cites.

**Actor freedoms with no requirement carrying them.**

- **A2.1** (`02-actors.md:48`) and **G99.2** (`99-glossary.md:71`) —
  the ADS MAY emit a decision format other than VAST. R11 binds the
  spec (R11.1, R11.3) and the Player (R11.2) but **never binds the
  ADS**, so the actor whose freedom the requirement exists to protect
  has no criterion. **Absorb into R11 as R11.4.**
- **I05.5** (`05-dash-linear-interfaces.md:434`) — VAST
  `<UniversalAdId>` is out of scope of the DASH carrier; an APS MAY
  propagate it best-effort via R23. A scope exclusion stated only
  inside an interface table. **Absorb into R23**, or add it to the
  Out of Scope list as OOS-7.

**Not orphans** (listed so the next pass does not re-open them):
UC04.1 / UC04.7 / UC04.8 (R5 / R21 / R26), UC04.2 (R1.1), UC04.6
(R1.2), I05.1 (R5.1 / R5.5), I05.2 (R24.1), I05.3 (R28), I05.4
(R23.1), N06.4 (R13.4), B07.1 / B07.2 / B07.3 / B07.5..B07.11 /
B07.13 / B07.15 / B07.16 (R1 verification procedure), B07.19 and
D08.3 (R24.1), D08.2 / D08.4 (R1.2), G99.1 (R29).

### Cross-reference with the UC coverage matrix

`uc-coverage-matrix.md` flags **R11** and **R24** as orphan Rs (no UC
exercises them). The two gaps are different in kind and do not
overlap:

- **R11** is orphaned at both levels. No UC makes the ADS's decision
  format visible, *and* the only assertions binding the ADS on that
  freedom (A2.1, G99.2) sit outside R11. Closing the UC gap alone
  still leaves R11 with no ADS-binding criterion.
- **R24** is orphaned only at the UC level. At the assertion level it
  is well anchored: R24.1 is restated by
  `05-dash-linear-interfaces.md:382`,
  `07-backward-compat-checklist.md:178` and
  `08-dash-extension-rules.md:30` — three independent folds. The
  missing piece is a UC showing the asset URL travelling, exactly as
  the matrix proposes.

`error-semantics.md` (E1..E16) introduces no obligation absent from
this table: every E row's Player / Publisher / APS / ADS column
resolves to a criterion listed above.

## 5. Ambiguity findings

Sentences whose obligation strength cannot be read off the text. None
was resolved by invention; each is recorded as a finding.

**Eleven declared conformance criteria carry no RFC 2119 keyword.**
They are written in the indicative ("the Player renders…", "the
specification documents…"), so a test author cannot tell MUST from
SHOULD. They are R12.4, R13.5, R17.1, R17.2, R17.3, R17.4, R18.1,
R18.2, R28.3, R29.1, R29.7 — marked `[no RFC 2119 keyword]` in the
table. Three clusters, three different fixes:

- **R17.1 / R17.2 / R17.3** describe runtime Player behaviour during
  a pause and are plainly MUST in intent — R17's body calls the
  priority "not Publisher-configurable" and "the only admissible
  composition". They read as prose because the block was written
  descriptively. **Add MUST.**
- **R12.4, R17.4, R18.1, R29.1, R29.7** are statements *about the
  spec* (what it inherits, what it documents, what it declines to
  define) rather than obligations on anyone. They may be correct as
  non-normative notes, but then they should not sit in a
  `Conformance criteria` block, because chapter 10 will try to build
  a test from each.
- **R13.5, R18.2, R28.3** delegate explicitly to the APS-to-ADS
  contract "outside this specification". They are **negative scope
  statements**, and a criterion that declares something unverifiable
  is a scope exclusion, not a conformance criterion. Candidates for
  the Out of Scope list.

**`MUST NEVER` is not RFC 2119** (`03-requirements.md:59`, DP-3:
"applying this specification MUST NEVER break primary-content
playback"). The intent is unambiguous; the vocabulary is not. Use
`MUST NOT`.

**A normative preference with no keyword** —
`06-naming-and-namespaces.md:130`: "the preferred encoding is a
**single attribute** carrying a space-separated string of tokens,
NOT a nested element wrapper". It is an authoring rule with a stated
rationale and a stated exception, i.e. a SHOULD in everything but
the word. Excluded from the table for lack of a keyword; **add
SHOULD** and it becomes N06.13.

**DP-2 is an authoring policy the spec cannot state about itself
without self-reference** (`03-requirements.md:44`): "Obligations are
positive… The spec does NOT enumerate prohibitions." It quotes MUST
and MUST NOT only to illustrate, so it produces no assertion — yet
the set above contains 29 rows carrying a MUST NOT. DP-2
and the requirement set as authored are in tension; whether the
tension is real (DP-2 governs the *generated spec*, not the
requirements) should be stated in DP-2 itself.

**Lowercase "must" carries normative weight in two places**
(`02-actors.md:170`, "it must operate within the validated subset";
`03-requirements.md:145`, "The design must enforce the separation").
Both are restated in uppercase by a criterion (R5.6 / R2.x), so
nothing is lost today — but the lowercase form is invisible to any
keyword-based extraction, including this one.

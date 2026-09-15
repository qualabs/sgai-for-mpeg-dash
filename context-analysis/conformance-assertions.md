# Conformance assertions

`[GROUNDED_BY=spec-only]`

Every RFC 2119 obligation in `context/`, normalised to one row per
testable assertion. Chapter 10 (Test cases) absorbs this table
directly: each row is one test.

Actors are the four of the model (`context/02-actors.md`) —
**Publisher**, **ADS**, **APS**, **Player** — plus `spec document`
for document-level obligations and `all` for an assertion binding
more than one runtime actor.

Assertion IDs inside `context/03-requirements.md` reuse the
`R<N>.<n>` conformance-criterion ID verbatim. Assertions outside it
carry a per-file prefix: `A2` (`02-actors.md`), `UC04`
(`04-use-cases.md`), `I05` (`05-dash-linear-interfaces.md`), `N06`
(`06-naming-and-namespaces.md`), `B07`
(`07-backward-compat-checklist.md`), `D08`
(`08-dash-extension-rules.md`), `G99` (`99-glossary.md`).

| Assertion ID | Source | Actor | Condition | Obligation |
|--------------|--------|-------|-----------|------------|
| R1.1 | context/03-requirements.md:116 | Player | Given an `MPD` carrying an SGAI construct the Player does not implement | MUST ignore the unknown construct and continue playing the primary content uninterrupted. |
| R1.2 | context/03-requirements.md:120 | all | Given a new SGAI construct introduced by this proposal | MUST be expressed through §5.2.1 foreign-namespace open content (DR-2 / DR-3), §5.10 application-level Event Streams, or §5.8.4.8 / §5.8.4.9 vendor descriptors; MUST NOT be introduced by a path violating the §5.3.2.6 / §8.15 / §7.3 / RFC 4337 chain (DR-1, DR-5). Annex F (DR-4) admissible only with genuine segment-delivery need plus a new Interoperability Point URI. |
| R1.3 | context/03-requirements.md:134 | all | (unconditional) | The specification MUST NOT alter or override the semantics of any pre-existing MPEG-DASH 6th edition construct. |
| R1.4 | context/03-requirements.md:137 | Player | Given resolving or rendering an accepted ad fails at runtime (decode error, malformed candidate, mid-ad network loss) | MUST abort that ad and continue playing the primary content uninterrupted. |
| R2.1 | context/03-requirements.md:153 | Publisher | Given an ad slot declared in the `MPD` | Constraints applicable to the slot (max duration, opt-in policies, layout templates) MUST be declared by the Publisher in the `MPD`, not inferred at runtime by ADS, APS, or Player. |
| R2.2 | context/03-requirements.md:157 | all | Given an ad opportunity being resolved | The ADS MUST decide which ads to serve and output its decision document; the APS MUST convert that output into the resolution document; neither MUST be expected to enforce Publisher-declared constraints. |
| R2.3 | context/03-requirements.md:162 | Player | Given a resolution document | MUST validate the candidates against Publisher-declared constraints and render only those that satisfy them. |
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
| R5.2 | context/03-requirements.md:487 | Player | Given an accepted candidate | MUST evaluate its presentation options in document order and render the first whose form and layout the device can satisfy. |
| R5.3 | context/03-requirements.md:491 | Player | Given a candidate carrying no form renderable on the device | MUST skip it and fall through to the next candidate; once candidates are exhausted MUST continue with the primary content. |
| R5.4 | context/03-requirements.md:495 | all | (unconditional) | Neither the ADS nor the APS MUST be required to maintain a device-class matrix or a per-Player capability view to produce candidates. |
| R5.5 | context/03-requirements.md:498 | APS | Given an ad candidate | MAY carry multiple presentation options, each pairing a form with an admissible layout, in a single ordered list whose document order is the preference order. |
| R5.6 | context/03-requirements.md:502 | Player | Given the walk over a candidate's presentation options | MUST check each option in document order against (a) device capabilities and (b) the Publisher-declared allowed layouts; an option failing either MUST NOT be rendered and the Player moves to the next. |
| R5.7 | context/03-requirements.md:509 | Player | Given no presentation option on a candidate satisfies R5.6 | MUST skip that candidate and fall through to the next in the order R7 requires, or to primary content when exhausted. |
| R6.1 | context/03-requirements.md:1048 | spec document | (unconditional) | MUST specify how in-band ad tracking beacons are carried in the resolution document. |
| R6.2 | context/03-requirements.md:1050 | APS | Given tracking beacons to carry | SHOULD carry them as `<Event>` entries inside an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015` in the ad `MPD` or sub-`MPD`. |
| R6.3 | context/03-requirements.md:1055 | spec document | Given the callback scheme cannot express the required semantics | A new tracking carrier MAY be introduced, and only after a documented gap analysis per R9. |
| R6.4 | context/03-requirements.md:1059 | Player | Given an unknown namespace on a tracking-related extension element | MUST safely ignore it, per the DASH extension rules invoked by R1. |
| R7.1 | context/03-requirements.md:542 | Player | Given a resolution document with more than one ad candidate | MUST play the candidates in the order the resolution document declares, except those dropped under R7.2 / R7.3. |
| R7.2 | context/03-requirements.md:546 | Player | Given a candidate with no form renderable on the device (R3 / R5) | MAY drop it. |
| R7.3 | context/03-requirements.md:548 | Player | Given a candidate's declared duration would push the cumulative slot duration past the cap (R4) | MAY drop it before playback ("drop before play"). |
| R7.4 | context/03-requirements.md:551 | Player | Given drops under R7.2 / R7.3 have been applied | MUST NOT re-order, deduplicate, or otherwise rearrange the remaining candidates. |
| R7.5 | context/03-requirements.md:554 | Player | Given an accepted candidate's actual rendered length exceeds the cap | MUST trim mid-rendering ("trim during play") per R4. |
| R8.1 | context/03-requirements.md:1195 | spec document | Given a new construct introduced by the proposal | MUST be accompanied by an inline justification stating why an existing MPEG-DASH construct could not be reused. |
| R8.2 | context/03-requirements.md:1198 | spec document | Given a deliberate omission of an existing MPEG-DASH construct a reader might expect to see reused | MUST be documented inline with the design decision. |
| R9.1 | context/03-requirements.md:1213 | spec document | (unconditional) | MUST reuse existing MPEG-DASH machinery (events, manifests, presentations, schemes) wherever possible. |
| R9.2 | context/03-requirements.md:1216 | spec document | Given an existing construct can be made to fit | A new construct MUST NOT be introduced. |
| R9.3 | context/03-requirements.md:1218 | spec document | Before introducing a new construct | MUST consider whether an extension to an existing construct would suffice, and document the outcome of that consideration. |
| R10.1 | context/03-requirements.md:1234 | spec document | Given the spatial arrangement of overlays | MUST be delegated to HTML5 / CSS layout primitives. |
| R10.2 | context/03-requirements.md:1236 | spec document | (unconditional) | MUST NOT define a parallel layout standard for overlay placement. |
| R10.3 | context/03-requirements.md:1238 | spec document | Given position semantics inside a layout (left, right, top, bottom) | Out of scope for the spec; MUST be expressed via the Positioning Templates section using HTML5 / CSS primitives. |
| R11.1 | context/03-requirements.md:181 | spec document | Given the normative chapters of the spec | MUST NOT cite a specific VAST version as required. |
| R11.2 | context/03-requirements.md:183 | Player | (unconditional) | MUST be able to operate regardless of whether the ADS uses VAST; the Player reads only the resolution document the APS produces and never talks to the ADS. |
| R11.3 | context/03-requirements.md:191 | spec document | Given any reference to VAST in the spec | MUST be in an annex or in a non-normative note explicitly flagged as illustrative. |
| R12.1 | context/03-requirements.md:378 | spec document | Given the accepted ad-type and visual-placement values | MUST be exactly those R12 enumerates; the spec MUST NOT accept a value outside the enumeration and MUST cite the IAB source for each accepted value. |
| R12.2 | context/03-requirements.md:382 | Publisher | Given an allowed-layouts declaration on a slot | MUST use names drawn from the enumerated set; Publisher-private layout names and IAB values outside the set MUST NOT appear. |
| R12.3 | context/03-requirements.md:387 | APS | Given the resolution document | MUST NOT emit form metadata for an ad type or visual placement outside the enumerated set; conformance is checked against the resolution document, not the ADS's decision document. |
| R12.4 | context/03-requirements.md:392 | spec document | Given an enumerated layout | Inherits the IAB CTV Ad Format Guidelines spatial bound by normative reference; no dimensional attribute is introduced on the slot declaration. |
| R13.1 | context/03-requirements.md:1080 | APS | Given the resolution document carries tracking instructions | MUST express them using DASH callback events (or an equivalent baseline DASH construct), with timings relative to the ad's presentation timeline. |
| R13.2 | context/03-requirements.md:1087 | Player | Given an ad accepted for rendering | MUST execute the tracking schedule read from the resolution document, firing each beacon at its specified relative time. |
| R13.3 | context/03-requirements.md:1092 | Player | Given R4 trims the ad before a scheduled beacon's time | MUST stop firing the remaining beacons at the trim boundary. |
| R13.4 | context/03-requirements.md:1095 | spec document | (unconditional) | MUST NOT introduce a new tracking event scheme; reuse of the DASH baseline callback mechanism is mandatory. |
| R13.5 | context/03-requirements.md:1098 | all | Given the fidelity of the APS's transcription of the ADS-declared beacons | MUST be enforced through the bilateral APS-to-ADS contract (R18); the resolution document cannot show it, since it does not show what was declared. |
| R14.1 | context/03-requirements.md:866 | Player | Given a non-linear slot whose resolution document declares more than one ad form | MUST present the forms in sequence, in the order they appear in the document, each starting when the previous ends. |
| R14.2 | context/03-requirements.md:871 | Player | Given a sequence of non-linear forms | MUST enforce the Publisher-declared slot cap (R4) against their cumulative duration, trimming or dropping per R4 / R7. |
| R14.3 | context/03-requirements.md:875 | spec document | (unconditional) | MUST NOT introduce a construct that implies or requires the parallel rendering of two or more non-linear ad forms, nor a "render-then" primitive beyond declared form order. |
| R15.1 | context/03-requirements.md:414 | spec document | Wherever creative carrier types are discussed | MUST enumerate exactly video / image / HTML; new carrier types MUST NOT be added in annexes, examples, or implementation notes. |
| R15.2 | context/03-requirements.md:418 | all | Given an ad candidate in the resolution document or a Publisher-declared form | MUST carry a creative whose mimeType falls under one of video / image / HTML; conformance is checked against the resolution document and the Publisher's declaration. |
| R15.3 | context/03-requirements.md:426 | Player | Given a candidate whose creative carrier mimeType is outside the admissible set | MAY skip it; such a candidate signals a non-conformant ADS, APS, or Publisher. |
| R16.1 | context/03-requirements.md:624 | Player | Given a pause-to-play transition by the viewer | MUST remove any rendered pause-ad form from the screen within one rendering frame. |
| R16.2 | context/03-requirements.md:627 | Player | Given the same pause-to-play transition | MUST cease firing tracking beacons scheduled for the dismissed pause-ad. |
| R17.1 | context/03-requirements.md:910 | Player | Given the viewer is paused inside a pause-ad window AND an overlay is active | MUST render the pause-ad form and suspend the overlay rendering. |
| R17.2 | context/03-requirements.md:914 | Player | Given resume from pause | MUST dismiss the pause-ad (R16) and restore the overlay rendering if the overlay slot window is still active. |
| R17.3 | context/03-requirements.md:917 | Player | Given the overlay slot window expired during the pause | MUST keep the overlay surface clear on resume. |
| R17.4 | context/03-requirements.md:920 | spec document | (unconditional) | MUST carry no construct that lets the Publisher, the ADS, or the APS invert the pause-ad-over-overlay priority. |
| R18.1 | context/03-requirements.md:213 | spec document | (unconditional) | MUST document the MPD event URL pattern (Player-visible input, served by the APS) and the resolution document format (Player-visible output, produced by the APS). |
| R18.2 | context/03-requirements.md:217 | all | Given the APS-to-ADS contract for ad-decisioning invocation | MUST be established and maintained bilaterally outside this specification, except for the parameters R29 defines on the Player's resolution request. |
| R19.1 | context/03-requirements.md:649 | Player | Given any ad form, linear or non-linear | MUST render it at the same playback speed as the primary content at the moment the ad is presented. |
| R19.2 | context/03-requirements.md:652 | Player | Given the primary content is playing at a speed other than 1x | MUST NOT force the ad to 1x; the ad follows the primary content's speed. |
| R19.3 | context/03-requirements.md:655 | Player | Given an ad form's effective on-screen duration | MUST compute it as `duration / playback_speed`, not as the raw `duration`; cap enforcement (R4) and beacon scheduling (R13) operate on the presentation-timeline `duration`. |
| R20.1 | context/03-requirements.md:965 | Player | Given two or more same-family opportunity windows overlap in time in the primary `MPD` | MUST select the first encountered and attempt to resolve its resolution document; MUST resort to a subsequent window ONLY when the first is inaccessible (APS does not respond, transport-level failure, final HTTP status other than `200`); a `200` carrying no candidates (R30) is accessible, so the Player MUST NOT fall through. |
| R21.1 | context/03-requirements.md:690 | Player | Given a pause-ad form | MAY present it fullscreen (and MAY then release the resources held by the primary content and any pre-existing overlay) or as a partial overlay over the paused frame; when partial, MUST keep at most one non-linear form active (R22), the coexisting overlay being suspended (R17). |
| R22.1 | context/03-requirements.md:1012 | Player | At any instant `t` | MUST keep at most ONE non-linear ad form active on screen and MUST NOT present two or more simultaneously, so the device never needs more than main content plus one ad form's decoder. |
| R23.1 | context/03-requirements.md:1124 | spec document | (unconditional) | MUST define, in the SVTA Ads WG namespace, the extension elements carrying generic application-level metadata with no native DASH carrier (`AdSystem`, `AdTitle`, etc.), and MUST state that emitting and reading them are both optional. |
| R24.1 | context/03-requirements.md:1143 | all | Given a non-AV ad form (`mediaType ∈ {html, image, ...}`) carried in the resolution document | The asset URL MUST NOT be expressed as `@mimeType` on an AdaptationSet or Representation reached through an RFC 4337-bound path (DR-1, DR-5); it MUST be carried via one of the §5.2.1 / §5.10 / §5.8.4.x carriers enumerated by DR-6. |
| R25.1 | context/03-requirements.md:721 | Player | Given live content and the viewer paused inside a pause-ad window | MUST keep its presentation time frozen inside that window for the full duration of the pause, regardless of the live edge advancing; any resume-at-live-edge decision MUST be treated as a Player action after the resume, outside the window. |
| R26.1 | context/03-requirements.md:750 | all | Given a background element in a side-by-side / double-box layout | MUST be carried as a composition attribute of the slot / layout, not as a separate presentation option (R5). |
| R26.2 | context/03-requirements.md:753 | Player | Given a side-by-side / double-box layout | MUST composite the primary content and the ad as the two boxes and MUST place a supplied background element in the uncovered bands; when the advertiser supplies none, the uncovered region renders as black. |
| R26.3 | context/03-requirements.md:758 | Player | Given a side-by-side whose ad is a video (two concurrent decoders) or an image / HTML surface (one decoder) | A video side-by-side MUST NOT be selected on a single-decoder device; a non-video element MUST NOT be selected on a device that cannot composite that surface type on top of video (R3 / R5). |
| R27.1 | context/03-requirements.md:806 | all | Given an L-shape / squeezeback presentation option | MUST carry exactly one ad creative — the full-frame background — as an image, a video, or a web/HTML surface (R15); the shrunk primary content is not a creative the ADS / APS supplies. |
| R27.2 | context/03-requirements.md:811 | Player | Given an L-shape layout | MUST composite the full-frame ad creative in the background with the shrunk primary content on top, the creative covering the whole frame and the content occupying its declared region. |
| R27.3 | context/03-requirements.md:816 | Player | Given the L-shape's full-frame creative is a video (two decoders) or an image / HTML surface (one decoder plus surface) | A video L-shape is NOT satisfiable on a single-decoder device; an image / HTML full-frame creative MUST NOT be selected on a device that cannot composite that surface type together with video (R3 / R5). |
| R28.1 | context/03-requirements.md:1162 | APS | Given an ad candidate carrying a ClickThrough | The carrier MUST hold both the ClickThrough URL and its associated click-tracking URL(s); a ClickThrough present without its click-tracking is a violation the resolution document shows. |
| R28.2 | context/03-requirements.md:1168 | Player | Given the viewer activates the ClickThrough | MUST read the ClickThrough URL and fire its associated click-tracking. |
| R28.3 | context/03-requirements.md:1171 | all | Given whether an ADS-declared ClickThrough reaches the resolution document at all | MUST be enforced through the bilateral APS-to-ADS contract (R18); the resolution document cannot show it. |
| R29.1 | context/03-requirements.md:239 | spec document | (unconditional) | The reserved parameters MUST be inputs about the device — statements of what it supports — and not conclusions about which ad experiences can be served; what is reserved is a set, fixed when the syntax is specified. |
| R29.2 | context/03-requirements.md:246 | Player | Given the resolution request | Sending a reserved parameter is OPTIONAL: a conformant Player MAY send all of them, some of them, or none. |
| R29.3 | context/03-requirements.md:248 | Player | Given the Player has no value for a reserved parameter, or does not disclose it | MUST omit that parameter entirely rather than send it with an empty or placeholder value. |
| R29.4 | context/03-requirements.md:252 | Player | Given a parameter that is not one of the reserved names | MUST carry a vendor-specific prefix, so reserved names added in a later edition cannot collide with it. |
| R29.5 | context/03-requirements.md:255 | APS | Given a resolution request missing any reserved parameter | MUST tolerate the absence and MUST be able to produce ad candidates without receiving any of them. |
| R29.6 | context/03-requirements.md:259 | spec document | Given the device classes R3.1 enumerates | The reserved set MUST be able to express the capability axes that distinguish them; a set that cannot tell two enumerated classes apart does not satisfy R29. |
| R29.7 | context/03-requirements.md:263 | spec document | Given a reserved parameter absent from the resolution request | Its value MUST be read as undetermined; absence does NOT assert that the device lacks the capability, and how an APS resolves an undetermined value is not defined here. |
| R30.1 | context/03-requirements.md:570 | APS | Given an opportunity that resolved with no ads | MUST be expressed as a resolution document carrying no candidates, and MUST NOT be expressed as an error response or as a response without a body. |
| A2.1 | context/02-actors.md:48 | ADS | Given the ADS's decision document | Typically VAST, but the ADS is not bound to VAST and MAY emit another format; it performs no conversion into the MPD-native / SGAI format the Player consumes. |
| UC04.1 | context/04-use-cases.md:781 | Publisher | Given live / real-time content whose SGAI opportunity falls through on a legacy Player | SHOULD treat the opportunity as an expected loss on legacy Players, not as an error. |
| UC04.2 | context/04-use-cases.md:783 | Publisher | Given non-live / VOD content carrying an SGAI construct | MAY (and SHOULD, where monetising the opportunity matters) author a standard linear break alongside it, using only baseline constructs a legacy Player renders, as the legacy fallback. |
| I05.1 | context/05-dash-linear-interfaces.md:433 | APS | Given VAST `<UniversalAdId>` | Out of scope of the DASH carrier this spec defines; an APS MAY propagate it best-effort on an SVTA-namespaced attribute / element (R23), and no carrier is mandated for it. |
| N06.1 | context/06-naming-and-namespaces.md:22 | spec document | Given a new event scheme introduced by this spec | MUST use the year-pinned pattern `urn:svta:dash:<construct>:<year>`; reusing an existing scheme URI with altered semantics across editions is not permitted. |
| N06.2 | context/06-naming-and-namespaces.md:37 | Player | Given a Player implementing edition N + 1 | SHOULD recognise both `:N:` and `:N+1:` URIs and treat them per the backward-compatibility rules of that edition. |
| N06.3 | context/06-naming-and-namespaces.md:48 | APS | Given tracking beacons for ads introduced by this spec | MUST reuse the MPEG-DASH 6th edition baseline callback scheme; a parallel tracking scheme under `urn:svta:dash:*` is out of scope. |
| N06.4 | context/06-naming-and-namespaces.md:55 | spec document | Given a Qualabs-private experimental extension that is not part of this specification | MUST use the `urn:qualabs:<feature>:<year>` vendor namespace; such URIs are non-normative and not part of the spec. |
| N06.5 | context/06-naming-and-namespaces.md:87 | spec document | Given a construct introduced by this spec | MUST honour the DR-3 authoring rule: a baseline element wrapped inside a foreign-namespace parent is invisible to legacy clients, a sibling is visible. |
| N06.6 | context/06-naming-and-namespaces.md:94 | spec document | Given a construct whose semantics change in a new edition | MUST use a new `<year>` suffix on its scheme URI. |
| N06.7 | context/06-naming-and-namespaces.md:97 | spec document | Given a construct whose semantics are unchanged across editions | MAY keep its existing URI. |
| N06.8 | context/06-naming-and-namespaces.md:99 | spec document | Given the spec's chapter 2 (Normative references) | MUST list the URIs introduced by the current edition explicitly. |
| N06.9 | context/06-naming-and-namespaces.md:108 | spec document | Given the accepted layout names for overlay templates | MUST reference the IAB-defined values without inventing new layout names at chapter level. |
| N06.10 | context/06-naming-and-namespaces.md:113 | spec document | Given the layout vocabulary | MUST map 1:1 to IAB-defined ad-type values; no publisher-private or spec-private layout names are admissible. |
| N06.11 | context/06-naming-and-namespaces.md:120 | spec document | Given a component in essence the same as one already defined in MPEG-DASH 6th edition or its profile annexes | MUST reuse the existing baseline construct with all its characteristics — name, default values, permitted value domain, units, semantics. |
| N06.12 | context/06-naming-and-namespaces.md:130 | spec document | Given a list-shaped property whose elements are single-valued tokens | SHOULD be encoded as a single attribute carrying a space-separated token string, not a nested element wrapper with per-item children. |
| B07.1 | context/07-backward-compat-checklist.md:13 | spec document | Given the spec's chapter 4 (Conformance) and chapter 10 (Test cases) | MUST apply the verification procedure this checklist defines. |
| B07.2 | context/07-backward-compat-checklist.md:17 | spec document | Given each new construct C the spec introduces | MUST explicitly answer the eight checklist items in C's specification chapter. |
| B07.3 | context/07-backward-compat-checklist.md:19 | spec document | Given an unanswered checklist item | SHOULD block publication. |
| B07.4 | context/07-backward-compat-checklist.md:37 | spec document | Given C's specification chapter | MUST name the applicable DR-N rule from `08-dash-extension-rules.md` for C's placement. |
| B07.5 | context/07-backward-compat-checklist.md:48 | spec document | Given C introduces a new namespace | MUST be in an extension namespace per `06-naming-and-namespaces.md`. |
| B07.6 | context/07-backward-compat-checklist.md:53 | spec document | Given C invokes Annex F (DR-4) | The chapter MUST state which new Interoperability Point URI is published in `MPD@profiles` and justify why the §5.2.1 / §5.10 / §5.8.4.x carriers are not sufficient. |
| B07.7 | context/07-backward-compat-checklist.md:67 | spec document | Given the legacy-Player behaviour walk-through for C | MUST be present in C's chapter as explicit prose, not implicit. |
| B07.8 | context/07-backward-compat-checklist.md:79 | spec document | Given C removed from the document | The remaining document MUST still parse and play. |
| B07.9 | context/07-backward-compat-checklist.md:84 | spec document | Given each new construct C | MUST have a chapter-10 test case modelled on UC-07; the legacy Player MUST ignore C in every case (silent skip, no beacon for C, no FATAL-level error, observable playback continues). |
| B07.10 | context/07-backward-compat-checklist.md:127 | spec document | Given C's specification chapter | MUST link to this checklist and confirm each item is satisfied. |
| B07.11 | context/07-backward-compat-checklist.md:128 | spec document | Given a construct chapter that omits the checklist confirmation | Reviewers SHOULD reject it. |
| B07.12 | context/07-backward-compat-checklist.md:144 | spec document | Given a construct not fitting DR-6 carrier (a), (b) or (c) | MUST justify why Annex F (DR-4) is invoked and what new Interoperability Point URI is published. |
| B07.13 | context/07-backward-compat-checklist.md:146 | spec document | Given each new construct's DR-6 carrier classification | MUST be stated explicitly in the construct's chapter; leaving it implicit is a checklist failure. |
| B07.14 | context/07-backward-compat-checklist.md:151 | spec document | Given the shipped spec | SHOULD carry an audit table summarising checklist status per construct; a `FAIL` in any column blocks publication. |
| B07.15 | context/07-backward-compat-checklist.md:163 | spec document | Given the enumerated ignore-if-unknown anti-patterns | Reviewers MUST flag them. |
| D08.1 | context/08-dash-extension-rules.md:12 | spec document | Given a bump of the ISO/IEC 23009-1 edition | Every DR-N rule MUST be re-validated section by section; rules are not blindly carried forward. |
| D08.2 | context/08-dash-extension-rules.md:22 | all | Given an SPS-bound document reached via `<ImportedMPD>` (DR-1) | A vendor profile URI MAY be appended in `@profiles`, but vendor profiles can only ADD constraints; there is no extension point inside SPS for non-MP4 MIME types. |
| D08.3 | context/08-dash-extension-rules.md:38 | spec document | Given DASH §5.2.1 open content (DR-2) | A foreign-namespace element MAY appear as a child of any DASH container, including `<Period>`, `<AdaptationSet>`, `<Event>`, and other foreign-namespace elements. |
| D08.4 | context/08-dash-extension-rules.md:41 | all | Given an MPD carrying foreign-namespace attributes and elements (DR-2) | MUST be authored such that, after those are removed, the result is still a valid DASH document conforming to the specification. |
| D08.5 | context/08-dash-extension-rules.md:97 | all | Given a per-AdaptationSet `@profiles` (DR-5) | MUST be a subset of the MPD-level `@profiles`; an SPS-rooted document cannot promote a single AdaptationSet to a broader profile to escape RFC 4337. |
| D08.6 | context/08-dash-extension-rules.md:142 | all | Given a slot whose tracking requires presentation-time alignment across a non-zero duration (DR-7) | MUST share a Period with at least one AdaptationSet, or carry the asset and tracking outside any non-zero-duration Period. |

**129 assertions.** By RFC 2119 keyword: **MUST / MUST NOT 109**,
**SHOULD 7**, **MAY 13**.

Ten rows state a flat normative fact carrying no explicit RFC 2119
keyword and are normalised to MUST: R17.1, R18.1, R18.2, R29.1,
R29.7, R13.5, R28.3, N06.12 (normalised to SHOULD — the source says
"the preferred encoding is"), D08.2 and D08.3 (normalised to MAY —
the source states a DASH permission as fact). One row carries two
keywords: UC04.2 reads "MAY (and SHOULD, where monetising the
opportunity matters)" and is counted under MAY.

## 1. Assertions per R

R1: 4 · R2: 4 · R3: 3 · R4: 5 · R5: 7 · R6: 4 · R7: 5 · R8: 2 ·
R9: 3 · R10: 3 · R11: 3 · R12: 4 · R13: 5 · R14: 3 · R15: 3 ·
R16: 2 · R17: 4 · R18: 2 · R19: 3 · R20: 1 · R21: 1 · R22: 1 ·
R23: 1 · R24: 1 · R25: 1 · R26: 3 · R27: 3 · R28: 3 · R29: 7 ·
R30: 1 — **92 total**, R1..R30 with no gaps.

## 2. Assertions per actor

| Actor | Count |
|---|---|
| Player | 45 |
| spec document | 52 |
| APS | 10 |
| Publisher | 5 |
| ADS | 2 |
| all | 15 |

`all` covers R1.2, R1.3, R2.2, R5.4, R13.5, R15.2, R18.2, R24.1,
R26.1, R27.1, R28.3, D08.2, D08.4, D08.5, D08.6.

## 3. Assertions per source doc

| File | Count |
|---|---|
| `context/01-intro.md` | 0 |
| `context/02-actors.md` | 1 |
| `context/03-requirements.md` | 92 |
| `context/04-use-cases.md` | 2 |
| `context/05-dash-linear-interfaces.md` | 1 |
| `context/06-naming-and-namespaces.md` | 12 |
| `context/07-backward-compat-checklist.md` | 15 |
| `context/08-dash-extension-rules.md` | 6 |
| `context/99-glossary.md` | 0 |

Eighteen further RFC 2119 sentences outside `03-requirements.md`
restate an assertion already in the table and would generate a
duplicate test, so they are folded rather than given a row:
`01-intro.md:47` → B07.1; `04-use-cases.md:294` → R5.5 / R27.1,
`:764` → R1.1, `:818` → R1.2, `:826` → UC04.2, `:839` → R21.1,
`:1154` and `:1163` → R26.1 / R26.2;
`05-dash-linear-interfaces.md:34` → R5.1 / R5.5, `:381` → R24.1,
`:431` → R28.1 / R28.2, `:432` → R23.1, `:463` → I05.1;
`07-backward-compat-checklist.md:99` → UC04.2, `:178` → R24.1;
`08-dash-extension-rules.md:30` → R24.1; `99-glossary.md:51` →
R29.2 / R29.3 / R29.7, `:71` → A2.1. The glossary contributes no
independent obligation — by design, it defers to R12 for the ad-type
vocabulary and to R5 / R29 for the rest.

`02-actors.md` allocates most actor responsibilities without RFC
2119 keywords; R2.1–R2.4 are the normalised form of that allocation,
so only the one keyworded sentence gets its own row.

## 4. Orphan assertions

Thirty-seven assertions live outside `03-requirements.md`. Fifteen
findings below group the ones that no R1..R30 criterion covers.
Ordered by how load-bearing the gap is.

- **D08.4** — `08-dash-extension-rules.md:41`. The MPD must stay a
  valid DASH document after every foreign-namespace element and
  attribute is removed. *This is the operative test behind R1.1 and
  R1.2, and no R states it.* R1.1 asserts the legacy Player's
  behaviour and R1.2 constrains the extension point chosen, but
  neither says the residue must be valid — which is what a
  conformance harness can actually run. **Absorb into R1 as a new
  criterion.**
- **B07.1 … B07.15** — the whole per-construct checklist. R1 demands
  graceful degradation; no R criterion mandates the *procedure* that
  makes it auditable per construct (name the DR-N rule, prose
  walk-through, sibling check, UC-07-modelled test, carrier
  classification, audit table). Fifteen document-level obligations
  with no requirement behind them. **Implies a new governance R
  alongside R8 / R9**, or a new R1 criterion pointing at
  `07-backward-compat-checklist.md` as normative.
- **UC04.1 / UC04.2** — `04-use-cases.md:781` and `:783`. Publisher
  authoring policy for the legacy fallback: live opportunities are an
  expected loss; for VOD a standard linear break MAY (SHOULD, where
  monetisation matters) be authored alongside the SGAI construct. The
  only Publisher-binding SHOULD in the whole set, and B07.9's test
  case depends on it. **Implies a new R**; R1 is about the Player
  ignoring the construct, not about what the Publisher authors
  beside it.
- **N06.6 / N06.7 / N06.8** — `06-naming-and-namespaces.md:94`, `:97`,
  `:99`. Edition versioning of scheme URIs, and chapter 2 listing the
  current edition's URIs. No R covers the spec's own edition
  lifecycle. **Implies a new R**, or a criterion under R1 (the
  ignore-if-unknown guarantee is what year-pinning protects).
- **N06.1** — `:22`. The year-pinned `urn:svta:dash:<construct>:<year>`
  pattern for new event schemes. **Absorb into R1.2**, which
  enumerates admissible extension points but says nothing about how
  their URIs are named.
- **N06.5** — `:87`. Constructs must honour the DR-3 authoring rule.
  **Absorb into R1.2**, same reason.
- **N06.2** — `:37`. A Player implementing edition N+1 SHOULD
  recognise both `:N:` and `:N+1:` URIs. Player-binding, and no R
  imposes any cross-edition obligation on a Player. **Needs an R**;
  it is the counterpart to N06.6 on the runtime side.
- **N06.11** — `:120`. Reuse a baseline construct *with all its
  characteristics* — name, defaults, value domain, units, semantics.
  Strictly stronger than R9.1 ("reuse wherever possible"). **Absorb
  into R9 as a new criterion**; otherwise reuse-in-name-only passes
  R9.1.
- **N06.4** — `:55`. Qualabs vendor namespace for private extensions.
  No R governs non-spec namespaces. **Absorb into R1.2** or leave
  explicitly non-normative.
- **N06.12** — `:130`. Space-separated token attribute preferred over
  a nested element wrapper. Authoring style with no R behind it.
  **Absorb into R9** (minimise constructs) or mark non-normative.
- **N06.9 / N06.10** — `:108`, `:113`. The spec must reference
  IAB-defined layout values and map the vocabulary 1:1. Adjacent to
  R12.1 / R12.2 but not the same test: R12 governs the values in the
  MPD and the resolution document, these govern the spec's own
  chapter-level vocabulary. **Absorb into R12 as a criterion binding
  the spec document.**
- **D08.6** — `08-dash-extension-rules.md:142`. DR-7: a non-zero-duration
  Period must carry at least one AdaptationSet, which closes the
  "empty-Period tracking carrier" design. It constrains any carrier
  R6 or R24 picks, and neither cites it. **Absorb into R6 (tracking
  carrier) and R24 (non-AV asset carrier).**
- **D08.1** — `:12`. Re-validate every DR-N rule on a DASH edition
  bump. Governance of the context set itself; no R covers it.
  **Absorb into the R8 / R9 governance group.**
- **D08.5** — `:97`. Per-AdaptationSet `@profiles` must be a subset of
  MPD-level `@profiles`. A DASH baseline fact that closes the escape
  hatch R24.1 depends on. **Absorb into R24 as supporting text**, or
  leave as a DR the R cites.
- **A2.1** — `02-actors.md:48`. The ADS MAY emit a decision format
  other than VAST. R11 binds the spec (R11.1, R11.3) and the Player
  (R11.2) but **never binds the ADS**, so the actor whose freedom the
  requirement exists to protect has no criterion. **Absorb into R11
  as R11.4.**
- **I05.1** — `05-dash-linear-interfaces.md:433`. VAST
  `<UniversalAdId>` is out of scope of the DASH carrier; an APS MAY
  propagate it best-effort via R23. **Absorb into R23**, or add it to
  the Out of Scope list as OOS-7 — today it is a scope exclusion
  stated only inside an interface table.

### Cross-reference with the UC coverage matrix

`uc-coverage-matrix.md` flags **R11** and **R24** as orphan Rs (no UC
exercises them). The two gaps are different in kind and do not
overlap:

- **R11** is orphaned at both levels. No UC makes the ADS's decision
  format visible, *and* the one assertion that binds the ADS (A2.1)
  sits in `02-actors.md` instead of in R11. Closing the UC gap alone
  still leaves R11 with no ADS-binding criterion.
- **R24** is orphaned only at the UC level. At the assertion level it
  is well anchored: R24.1 is restated by
  `05-dash-linear-interfaces.md:381`,
  `07-backward-compat-checklist.md:178` and
  `08-dash-extension-rules.md:30` — three independent folds. The
  missing piece is a UC that shows the asset URL travelling, exactly
  as the matrix proposes.

`error-semantics.md` (E1..E16) introduces no obligation absent from
this table: every E row's Player / Publisher / APS / ADS column
resolves to an R criterion listed above.

[GROUNDED_BY=spec-only]

# Conformance assertions extracted from context/

Normalised RFC 2119 MUST / SHOULD / MAY sentences across every file
in `../context/`. Assertions that live inside `Conformance criteria`
blocks in `../context/03-requirements.md` retain their canonical
`R<N>.<n>` ID; assertions outside those blocks are renamed with a
short prefix derived from the source file.

| Assertion ID | Source | Actor | Condition | Obligation |
|--------------|--------|-------|-----------|------------|
| R1.1 | context/03-requirements.md:33 | Player | Given an MPD containing an SGAI construct that the Player does not implement | MUST ignore the unknown construct and continue playing the primary content uninterrupted. |
| R1.2 | context/03-requirements.md:36 | norm document | (unconditional) | Every new SGAI construct introduced by the proposal MUST be expressed using a MPEG-DASH 6th edition extension point whose ignore-if-unknown semantics are already defined. |
| R1.3 | context/03-requirements.md:40 | norm document | (unconditional) | The norm MUST NOT alter or override the semantics of any pre-existing MPEG-DASH 6th edition construct. |
| R2.1 | context/03-requirements.md:50 | Broadcaster | Given an ad slot | Constraints applicable to the slot (max duration, opt-in policies, layout templates) MUST be declared by the Broadcaster in the MPD. |
| R2.2 | context/03-requirements.md:54 | ADS | Given a resolution request | The ADS MUST produce ad candidates as a resolution document; MUST NOT be expected to enforce Broadcaster-declared constraints. |
| R2.3 | context/03-requirements.md:57 | Player | Given ADS-returned candidates | MUST validate against Broadcaster-declared constraints and render only those that satisfy them. |
| R2.4 | context/03-requirements.md:60 | norm document | Given any new mechanism introduced by the norm | MUST be expressible within the three-actor contract; mechanisms outside the contract MUST be rejected or redesigned. |
| R3.1 | context/03-requirements.md:74 | norm document | (unconditional) | The norm MUST enumerate the supported device classes and, for each class, the expected behaviour for each ad opportunity type covered by the use cases. |
| R3.2 | context/03-requirements.md:77 | Player | Given any ad opportunity type defined in the norm | MUST produce a defined behaviour (render, fall back, or skip); undefined behaviour is non-conforming. |
| R3.3 | context/03-requirements.md:80 | Player | Given an ad form (video, image, HTML) that the device class cannot render | MUST NOT attempt to render that form. |
| R4.1 | context/03-requirements.md:101 | Broadcaster | Given an ad slot in the MPD | MUST declare a maximum duration on the slot (linear or non-linear). |
| R4.2 | context/03-requirements.md:104 | Player | Given cumulative duration of accepted candidates would exceed the declared cap | MUST stop rendering at the cap boundary, even if the stop falls mid-ad. |
| R4.3 | context/03-requirements.md:108 | Player | Given any ad slot | MUST NOT extend a slot beyond the Broadcaster-declared cap, regardless of ADS metadata or candidate count. |
| R4.4 | context/03-requirements.md:111 | ADS | Given candidate selection | The ADS is NOT required to respect the cap; a conformance check MUST NOT fail solely because cumulative duration exceeds the cap. |
| R4.5 | context/03-requirements.md:115 | Player | Given an accepted candidate whose actual rendered length exceeds its declared duration | MUST enforce the cap against actual length, not declared length ("trim during play"). |
| R5.1 | context/03-requirements.md:143 | ADS | Given an ad candidate returned by the ADS | MUST carry one or more renderable forms (e.g. video, image, HTML); MAY rank them via ADS hints. |
| R5.2 | context/03-requirements.md:146 | Player | Given an accepted candidate with multiple renderable forms | MUST choose, among the renderable forms, the best form it can render on its device. |
| R5.3 | context/03-requirements.md:149 | Player | Given a candidate with no form renderable on the device | MUST skip it, falling back to the next candidate or to primary content per configured policy. |
| R5.4 | context/03-requirements.md:152 | ADS | Given candidate production | MUST NOT be required to maintain a device-class matrix or per-Player capability view. |
| R5.5 | context/03-requirements.md:155 | ADS | Given a single ad candidate | MAY carry multiple forms and multiple admissible layouts; ADS hints MAY rank both dimensions. |
| R5.6 | context/03-requirements.md:158 | Player | Given form/layout selection on a candidate | MUST intersect (a) device caps, (b) Broadcaster `@allowedLayouts`, (c) ADS priority hints; combinations failing any one MUST NOT be rendered. |
| R5.7 | context/03-requirements.md:163 | Player | Given no form/layout combination on a candidate satisfies R5.6 | MUST skip that candidate and fall through to the next ADS-returned candidate (preserving R7 order) or, when exhausted, to primary content. |
| R6.1 | context/03-requirements.md:184 | norm document | (unconditional) | MUST specify how in-band ad tracking beacons are carried in the resolution document. |
| R6.2 | context/03-requirements.md:186 | Broadcaster, ADS | Given a tracking carrier | SHOULD carry tracking beacons as `<Event>` entries inside an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015` in the ad MPD or sub-MPD. |
| R6.3 | context/03-requirements.md:190 | norm document | Given a new tracking carrier is proposed | MAY be introduced only when the callback scheme cannot express the required semantics, and only after a documented gap analysis per R9. |
| R6.4 | context/03-requirements.md:194 | ADS, Broadcaster | Given application-level metadata with no native DASH carrier | MAY be conveyed via vendor-namespaced extension elements. |
| R6.5 | context/03-requirements.md:198 | Player | Given unknown namespaces on tracking-related extension elements | MUST safely ignore them per DASH extension rules invoked by R1. |
| R7.1 | context/03-requirements.md:224 | Player | Given an ADS resolution document with more than one candidate | MUST play candidates in ADS-declared order, except those dropped under R7.2 / R7.3. |
| R7.2 | context/03-requirements.md:227 | Player | Given a candidate with no form renderable on the device | MAY drop it. |
| R7.3 | context/03-requirements.md:230 | Player | Given a candidate whose declared duration would push cumulative slot duration past the cap | MAY drop it before playback ("drop before play"). |
| R7.4 | context/03-requirements.md:233 | Player | After applying R7.2 / R7.3 | MUST NOT re-order, deduplicate, or otherwise rearrange the remaining candidates. |
| R7.5 | context/03-requirements.md:236 | Player | Given an accepted candidate whose actual rendered length exceeds the cap | MUST trim mid-rendering ("trim during play") per R4. |
| R8.1 | context/03-requirements.md:307 | norm document | Given a new construct introduced by the proposal | MUST be accompanied by an inline justification stating why an existing MPEG-DASH construct could not be reused. |
| R8.2 | context/03-requirements.md:311 | norm document | Given a deliberate omission of an existing MPEG-DASH construct | MUST be documented inline with the design decision. |
| R9.1 | context/03-requirements.md:321 | norm document | (unconditional) | MUST reuse existing MPEG-DASH machinery (events, manifests, presentations, schemes) wherever possible. |
| R9.2 | context/03-requirements.md:324 | norm document | Given a candidate new construct | MUST NOT introduce it unless an existing one cannot be made to fit. |
| R9.3 | context/03-requirements.md:327 | norm document | Before introducing a new construct | MUST consider whether an extension to an existing construct would suffice, and document the outcome. |
| R10.1 | context/03-requirements.md:338 | norm document | (unconditional) | Spatial arrangement of overlays MUST be delegated to HTML5 / CSS layout primitives. |
| R10.2 | context/03-requirements.md:340 | norm document | (unconditional) | The norm MUST NOT define a parallel layout standard for overlay placement. |
| R10.3 | context/03-requirements.md:342 | norm document | Given position semantics inside a layout | MUST be expressed via Positioning Templates using HTML5 / CSS primitives. |
| R11.1 | context/03-requirements.md:247 | norm document | (unconditional) | Normative chapters MUST NOT cite a specific VAST version as required. |
| R11.2 | context/03-requirements.md:249 | Player | Given an ADS that does not use VAST | MUST be able to operate against it. |
| R11.3 | context/03-requirements.md:252 | norm document | Given a reference to VAST in the norm | MUST appear in an annex or non-normative note explicitly flagged as illustrative. |
| R12.1 | context/03-requirements.md:266 | norm document | (unconditional) | The list of accepted ad-type values MUST be sourced from IAB definitions, with a reference to the IAB source. |
| R12.2 | context/03-requirements.md:269 | Broadcaster | Given a layout declaration on a slot | MUST use names that map 1:1 to IAB-defined ad-type values (no broadcaster-private layout names in `@allowedLayouts`). |
| R12.3 | context/03-requirements.md:273 | ADS | Given a candidate's form metadata | MUST NOT emit form metadata for ad types not part of the IAB-defined set used by this norm's edition. |
| R13.1 | context/03-requirements.md:285 | Player | Given a non-linear ad accepted for rendering | MUST fire an impression beacon at the instant the overlay becomes visible to the user. |
| R13.2 | context/03-requirements.md:288 | Player | Given quartile tracking on a non-linear ad | SHOULD fire quartile beacons timed against the Broadcaster-declared overlay window, not against the ad's internal duration. |
| R13.3 | context/03-requirements.md:291 | Player | Given R4 trims the overlay before all quartiles fire | MUST stop firing beacons at the trim boundary. |
| R13.4 | context/03-requirements.md:294 | norm document | (unconditional) | MUST NOT introduce a new tracking event scheme; reuse of the linear baseline tracking mechanism is mandatory. |
| A2.1 | context/02-actors.md:81 | Player | Given an ADS-returned candidate that violates the slot constraints | MUST discard it (Player as enforcer of Broadcaster's policy). |
| A2.2 | context/02-actors.md:84 | Player | Given a set of validated candidates | MUST operate within the validated subset (additional client-side ranking allowed). |
| A2.3 | context/02-actors.md:62 | ADS | Given Broadcaster-declared constraints | MUST NOT be required to validate its response against them (validation is Player's responsibility). |
| UC04.1 | context/04-use-cases.md:80 | Player | Given no candidate has a renderable form on the device | MUST decline the slot gracefully (skip is a valid outcome, not a failure). |
| UC04.2 | context/04-use-cases.md:707 | Broadcaster | Given a manifest construct that legacy Players may encounter | MUST express it via an MPEG-DASH 6th edition extension point whose ignore-if-unknown semantics yield silent skip. |
| I05.1 | context/05-dash-linear-interfaces.md:212 | Broadcaster | Given InsertPresentation and ReplacePresentation events on the same Period | `@returnOffset`, `@clipDuration`, `@startWithOffset` MUST appear only on ReplacePresentation. |
| I05.2 | context/05-dash-linear-interfaces.md:307 | Player | Given a ListMPD whose cumulative Period duration exceeds the parent SGAI event `@maxDuration` | MUST terminate playback at the cap (§5.16.5). |
| I05.3 | context/05-dash-linear-interfaces.md:317 | Player | Given a callback EventStream of scheme `urn:mpeg:dash:event:callback:2015` inside an ad MPD | MUST fire an HTTP GET to each Event's embedded URL at the corresponding `presentationTime` and discard the response body. |
| I05.4 | context/05-dash-linear-interfaces.md:373 | ADS adapter | Given a tracking-only VAST `<Ad>` (no MediaFile) | MUST NOT synthesise a media-less ad MPD; resulting ListMPD omits the entry under the silent-skip policy. |
| N06.1 | context/06-naming-and-namespaces.md:22 | norm document | Given a new event scheme introduced by the norm | MUST use the year-pinned pattern `urn:svta:dash:<construct>:<year>`. |
| N06.2 | context/06-naming-and-namespaces.md:43 | norm document | Given tracking carrier semantics | MUST inherit the existing DASH 6th edition callback scheme; introducing a parallel tracking scheme under `urn:svta:dash:*` is out of scope. |
| N06.3 | context/06-naming-and-namespaces.md:81 | Player | Given unknown XML namespaces | MUST ignore them per DASH extension rules. |
| N06.4 | context/06-naming-and-namespaces.md:108 | Broadcaster | Given `@allowedLayouts` declaration | MUST use names that map 1:1 to IAB-defined ad-type / layout values. |
| C07.1 | context/07-backward-compat-checklist.md:17 | norm document | Given any new construct C introduced by the norm | MUST explicitly answer the 7-item per-construct checklist (placement, extension rule, walk-through, sibling check, UC-07 test, namespace, doc cross-reference). |
| C07.2 | context/07-backward-compat-checklist.md:74 | norm document | Given any new construct C | MUST ship a UC-07-modelled test case in chapter 10 (representative MPD, legacy Player harness, expected silent-skip behaviour). |
| G99.1 | context/99-glossary.md:23 | norm document | Given the Overlay umbrella term | MUST reference IAB-defined sub-types normatively and MUST NOT introduce new sub-types. |

## Assertions per R

- R1: 3
- R2: 4
- R3: 3
- R4: 5
- R5: 7
- R6: 5
- R7: 5
- R8: 2
- R9: 3
- R10: 3
- R11: 3
- R12: 3
- R13: 4

R-block total: 50.

## Assertions per actor

- Broadcaster: 7 (R2.1, R4.1, R6.2 [shared], UC04.2, I05.1, N06.4, C07.1 [shared])
- ADS: 7 (R2.2, R4.4, R5.1, R5.4, R5.5, R6.2 [shared], R12.3, I05.4, A2.3) — net 8 unique
- Player: 24 (R1.1, R2.3, R3.2, R3.3, R4.2, R4.3, R4.5, R5.2, R5.3, R5.6, R5.7, R6.5, R7.1..R7.5, R11.2, R13.1..R13.3, A2.1, A2.2, UC04.1, I05.2, I05.3, N06.3)
- norm document: 19 (R1.2, R1.3, R2.4, R3.1, R6.1, R6.3, R8.1, R8.2, R9.1, R9.2, R9.3, R10.1, R10.2, R10.3, R11.1, R11.3, R12.1, R13.4, N06.1, N06.2, C07.1, C07.2, G99.1, UC04.2)
- all (cross-cutting): 0

Counts approximate; some rows bind two actors (e.g. R6.2 binds
Broadcaster and ADS). The dominant binding is shown in the table.

## Assertions per source doc

- context/03-requirements.md: 50 (R-block assertions, dominant)
- context/02-actors.md: 3
- context/04-use-cases.md: 2
- context/05-dash-linear-interfaces.md: 4
- context/06-naming-and-namespaces.md: 4
- context/07-backward-compat-checklist.md: 2
- context/99-glossary.md: 1

Total: 66 assertions. The non-R sources contribute 16 ancillary
assertions, of which roughly half are corollaries to R1, R6, R12.

## Orphan assertions

The following assertions live outside `03-requirements.md`'s R blocks
and do not map cleanly to a single existing R. For each, the most
plausible absorption target is noted.

- **A2.1** (`02-actors.md:81`, Player MUST discard violating
  candidates) — implicit corollary of R2.3; consider absorbing into
  R2.3 by tightening its wording from "render only those that
  satisfy" to "discard those that do not satisfy".
- **I05.4** (`05-dash-linear-interfaces.md:373`, ADS adapter MUST NOT
  synthesise media-less ad MPDs from tracking-only VAST `<Ad>`) — this
  is an ADS-adapter implementation rule; not currently captured by any
  R. Candidate: a new sub-clause under R2 (ADS obligations) or under
  R11 (since it concerns the VAST→ListMPD adapter). Recommended
  absorption: R2.2 (ADS MUST emit valid ad candidates only).
- **C07.1** and **C07.2** (`07-backward-compat-checklist.md`) — these
  formalise the verification procedure for R1. Consider absorbing the
  per-construct checklist obligation into R1.2 or splitting into a
  governance R8-style document-level assertion.
- **G99.1** (`99-glossary.md:23`, Overlay sub-types defined by IAB,
  no new sub-types in the glossary) — duplicates R12.1 and R12.2.
  Recommended absorption: R12 already covers this; G99.1 is redundant
  and can be dropped from the glossary's normative content (left as
  informative cross-reference only).

These signals do not indicate missing Rs but point to redundancies
between the requirements block and ancillary files. The next spec
iteration could tighten R2 to subsume A2.1 / I05.4 and drop G99.1.

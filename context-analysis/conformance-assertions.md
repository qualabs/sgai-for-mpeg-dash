[GROUNDED_BY=spec-only]

# Conformance assertions

Normative obligations extracted from `../context/`. Each row is actionable
as a chapter-10 test case. RFC 2119 keywords (MUST, MUST NOT, SHOULD,
SHOULD NOT, MAY) preserved verbatim; see
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119).

## Assertions

| Assertion ID | Source | Actor | Condition | Obligation |
|---|---|---|---|---|
| R1.1 | context/03-requirements.md:45 | Player | Given an MPD contains an SGAI construct the Player does not implement | A conforming legacy Player MUST ignore the unknown construct and continue playing the primary content uninterrupted. |
| R1.2 | context/03-requirements.md:49 | spec document | (unconditional) | Every new SGAI construct introduced by this proposal MUST be expressed using one of the extension points enumerated in DR-1..DR-6 (foreign-namespace open content §5.2.1, application-level Event Streams §5.10, vendor descriptor schemes §5.8.4.8/§5.8.4.9; Annex F admissible only under DR-4 conditions). |
| R1.3 | context/03-requirements.md:63 | spec document | (unconditional) | The specification MUST NOT alter or override the semantics of any pre-existing MPEG-DASH 6th edition construct. |
| R2.1 | context/03-requirements.md:73 | Broadcaster | Given an ad slot is declared in the MPD | Constraints applicable to the slot (max duration, opt-in policies, layout templates) MUST be declared by the Broadcaster in the MPD, not inferred at runtime by the ADS or the Player. |
| R2.2 | context/03-requirements.md:77 | ADS | (unconditional) | The ADS MUST produce ad candidates as a resolution document; it MUST NOT be expected to enforce Broadcaster-declared constraints. |
| R2.3 | context/03-requirements.md:80 | Player | Given an ADS-returned candidate set | The Player MUST validate candidates against Broadcaster-declared constraints and render only those that satisfy them. |
| R2.4 | context/03-requirements.md:83 | spec document | (unconditional) | Every new mechanism introduced by the specification MUST be expressible within the three-actor contract; any mechanism requiring an actor to take on an out-of-role responsibility MUST be rejected or redesigned. |
| R3.1 | context/03-requirements.md:97 | spec document | (unconditional) | The specification MUST enumerate the supported device classes and, for each class, the expected behaviour for each ad opportunity type covered by the use cases. |
| R3.2 | context/03-requirements.md:100 | Player | Given any supported device class and any ad opportunity type defined in the spec | The Player MUST produce a defined behaviour (render, fall back, or skip); undefined behaviour is non-conforming. |
| R3.3 | context/03-requirements.md:104 | Player | Given an ad form not renderable on the Player's device class | The Player MUST NOT attempt to render that form. |
| R4.1 | context/03-requirements.md:124 | Broadcaster | Given an ad slot (linear or non-linear) defined in the MPD | The Broadcaster MUST declare a maximum duration on the slot. |
| R4.2 | context/03-requirements.md:127 | Player | Given the cumulative duration of accepted candidates would exceed the Broadcaster-declared cap | The Player MUST stop rendering at the cap boundary, even if the stop falls mid-ad. |
| R4.3 | context/03-requirements.md:131 | Player | (unconditional) | The Player MUST NOT extend a slot beyond the Broadcaster-declared cap regardless of ADS metadata or candidate count. |
| R4.4 | context/03-requirements.md:134 | ADS | (unconditional) | The ADS is NOT required to respect the cap when selecting candidates; an ADS conformance check MUST NOT fail solely because cumulative returned-candidate duration exceeds the cap. |
| R4.5 | context/03-requirements.md:138 | Player | Given the actual rendered length of an accepted candidate exceeds its declared duration | The Player MUST enforce the cap against actual length, not declared length ("trim during play"). |
| R5.1 | context/03-requirements.md:161 | ADS | (unconditional) | Each ad candidate returned by the ADS MUST carry one or more renderable forms (e.g. video, image, HTML); the ADS MAY rank them via ADS hints. |
| R5.2 | context/03-requirements.md:164 | Player | Given an accepted candidate with multiple renderable forms | The Player MUST choose the best form it can render on its device. |
| R5.3 | context/03-requirements.md:167 | Player | Given a candidate that carries no form renderable on the device | The Player MUST skip the candidate, falling back to the next candidate or to primary content per the configured policy. |
| R5.4 | context/03-requirements.md:170 | ADS | (unconditional) | The ADS MUST NOT be required to maintain a device-class matrix or a per-Player capability view to produce candidates. |
| R5.5 | context/03-requirements.md:173 | ADS | (unconditional) | An ad candidate MAY carry multiple forms and MAY carry multiple admissible layouts; ADS-supplied priority hints MAY rank both dimensions independently. |
| R5.6 | context/03-requirements.md:176 | Player | Given any form/layout selection | The Player MUST resolve selection by intersecting (a) device capabilities, (b) Broadcaster-declared allowed layouts, and (c) ADS-supplied priority hints; combinations that fail any of the three MUST NOT be rendered. |
| R5.7 | context/03-requirements.md:181 | Player | Given no form/layout combination on a candidate satisfies R5.6 | The Player MUST skip the candidate and fall through to the next ADS-returned candidate (preserving R7 order) or, when exhausted, to primary content. |
| R6.1 | context/03-requirements.md:202 | spec document | (unconditional) | The specification MUST specify how in-band ad tracking beacons are carried in the resolution document. |
| R6.2 | context/03-requirements.md:204 | all | (unconditional) | Implementations SHOULD carry tracking beacons as `<Event>` entries inside an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015` in the ad MPD or sub-MPD. |
| R6.3 | context/03-requirements.md:208 | spec document | Given the callback scheme cannot express the required tracking semantics | A new tracking carrier MAY be introduced only after a documented gap analysis per R9. |
| R6.4 | context/03-requirements.md:212 | all | Given application-level metadata has no native DASH carrier (`ClickThrough`, `AdSystem`, `AdTitle`, `UniversalAdId`, etc.) | The metadata MAY be conveyed via vendor-namespaced extension elements. |
| R6.5 | context/03-requirements.md:216 | Player | Given an unknown namespace on a tracking-related extension element | The Player MUST safely ignore it, per the DASH extension rules invoked by R1. |
| R6.6 | context/03-requirements.md:219 | all | Given a non-AV ad form (`mediaType ∈ {html, image, ...}`) is carried | The asset URL MUST NOT be expressed as `@mimeType` on an AdaptationSet or Representation reached through any path bound by RFC 4337 (DR-1, DR-5); it MUST be carried via one of the §5.2.1 / §5.10 / §5.8.4.x carriers enumerated by DR-6. |
| R7.1 | context/03-requirements.md:250 | Player | Given an ADS resolution document with more than one ad candidate | The Player MUST play candidates in the order declared by the ADS, except for candidates dropped under R7.2 or R7.3. |
| R7.2 | context/03-requirements.md:254 | Player | Given a candidate with no form renderable on the device | The Player MAY drop the candidate (R3 / R5). |
| R7.3 | context/03-requirements.md:256 | Player | Given a candidate whose declared duration would push cumulative slot duration past the cap | The Player MAY drop the candidate before playback ("drop before play"). |
| R7.4 | context/03-requirements.md:259 | Player | (unconditional) | After applying R7.2 / R7.3, the Player MUST NOT re-order, deduplicate, or otherwise rearrange the remaining candidates. |
| R7.5 | context/03-requirements.md:262 | Player | Given an accepted candidate whose actual rendered length exceeds the cap | The Player MUST trim mid-rendering ("trim during play") per R4. |
| R8.1 | context/03-requirements.md:373 | spec document | Given every new construct introduced by the proposal | An inline justification stating why an existing MPEG-DASH construct could not be reused MUST accompany it. |
| R8.2 | context/03-requirements.md:376 | spec document | Given every deliberate omission of an existing MPEG-DASH construct a reader might expect to see reused | The omission MUST be documented inline with the design decision. |
| R9.1 | context/03-requirements.md:387 | spec document | (unconditional) | The proposal MUST reuse existing MPEG-DASH machinery (events, manifests, presentations, schemes) wherever possible. |
| R9.2 | context/03-requirements.md:390 | spec document | (unconditional) | A new construct MUST NOT be introduced unless an existing one cannot be made to fit. |
| R9.3 | context/03-requirements.md:392 | spec document | Given a proposal to introduce a new construct | The proposal MUST first consider whether an extension to an existing construct would suffice, and document the outcome. |
| R10.1 | context/03-requirements.md:404 | spec document | (unconditional) | Spatial arrangement of overlays MUST be delegated to HTML5 / CSS layout primitives. |
| R10.2 | context/03-requirements.md:406 | spec document | (unconditional) | The specification MUST NOT define a parallel layout standard for overlay placement. |
| R10.3 | context/03-requirements.md:408 | spec document | Given any positioning semantics inside a layout (left, right, top, bottom, etc.) | These MUST be expressed via the Positioning Templates section using HTML5 / CSS primitives and are out of scope for the spec body. |
| R11.1 | context/03-requirements.md:273 | spec document | (unconditional) | The normative chapters of the spec MUST NOT cite a specific VAST version as required. |
| R11.2 | context/03-requirements.md:275 | Player | Given an ADS that does not use VAST | A Player MUST be able to operate against it. |
| R11.3 | context/03-requirements.md:278 | spec document | Given any reference to VAST in the spec | The reference MUST be in an annex or in a non-normative note explicitly flagged as illustrative. |
| R12.1 | context/03-requirements.md:292 | spec document | (unconditional) | The list of accepted ad-type values in the spec MUST be sourced from IAB definitions, and a reference to the IAB source MUST be included. |
| R12.2 | context/03-requirements.md:295 | Broadcaster | Given a Broadcaster declares allowed layouts on a slot | Broadcasters MUST use names that map 1:1 to IAB-defined ad-type values (no broadcaster-private layout names). |
| R12.3 | context/03-requirements.md:299 | ADS | (unconditional) | The ADS MUST NOT emit form metadata for ad types outside the IAB-defined set used by this spec's edition. |
| R13.1 | context/03-requirements.md:311 | Player | Given a non-linear ad is accepted for rendering | The Player MUST fire an impression beacon at the instant the overlay becomes visible to the user. |
| R13.2 | context/03-requirements.md:314 | Player | Given a non-linear ad is rendering | The Player SHOULD fire quartile beacons timed against the Broadcaster-declared overlay window, not against the ad's internal duration. |
| R13.3 | context/03-requirements.md:317 | Player | Given R4 trims the overlay before all quartiles fire | The Player MUST stop firing beacons at the trim boundary. |
| R13.4 | context/03-requirements.md:320 | spec document | (unconditional) | The specification MUST NOT introduce a new tracking event scheme; reuse of the linear baseline tracking mechanism is mandatory. |
| R14.1 | context/03-requirements.md:334 | Player | (unconditional, at every time t) | The Player MUST present at most one form from a non-linear opportunity at any given moment; other simultaneously-active opportunities MUST be deferred or skipped per policy. |
| R14.2 | context/03-requirements.md:338 | spec document | (unconditional) | The specification MUST NOT introduce constructs that imply or require parallel non-linear form rendering. |
| R15.1 | context/03-requirements.md:352 | spec document | (unconditional, wherever creative carrier types are discussed) | The specification MUST enumerate the admissible set as exactly {video, image, HTML}; new carrier types MUST NOT be added in annexes, examples, or implementation notes. |
| R15.2 | context/03-requirements.md:356 | all | (unconditional) | Ad candidates returned by the ADS and forms declared by the Broadcaster MUST carry a creative whose mimeType falls under one of {video, image, HTML}. |
| R15.3 | context/03-requirements.md:360 | Player | Given a candidate whose creative carrier mimeType is not in the admissible set | The Player MAY skip the candidate; such a candidate signals a non-conformant ADS or Broadcaster. |
| UC04.1 | context/04-use-cases.md:687 | Player | Given a legacy Player encounters an unrecognized SGAI event type or construct in the manifest | The Player MUST skip the unknown construct and continue playing the primary content as if the construct were not present (restatement of R1.1 in UC-07). |
| UC04.2 | context/04-use-cases.md:705 | spec document | (unconditional) | Any new construct introduced by the proposal MUST be expressible via extension points that produce the UC-07 outcome on legacy Players (restatement of R1.2). |
| I05.1 | context/05-dash-linear-interfaces.md:335 | spec document | Given the non-linear chapters of the spec carry non-AV asset URLs (HTML, image, other) | These URLs MUST be carried outside the AdaptationSet axis, via one of the carriers enumerated in DR-6 (restatement of R6.6 / R1.2). |
| N06.1 | context/06-naming-and-namespaces.md:22 | spec document | Given a new event scheme introduced by this spec | The scheme URI MUST follow the year-pinned pattern `urn:svta:dash:<construct>:<year>`. |
| N06.2 | context/06-naming-and-namespaces.md:37 | Player | Given a Player implementing edition N+1 of this spec | The Player SHOULD recognise both `:N:` and `:N+1:` scheme URIs and treat them per the backward-compatibility rules in edition N+1. |
| N06.3 | context/06-naming-and-namespaces.md:48 | all | Given an implementation carrying tracking beacons for ads introduced by this spec | The implementation MUST reuse the MPEG-DASH 6th edition baseline tracking callback scheme (restatement of R13.4 from the namespace-policy side). |
| N06.4 | context/06-naming-and-namespaces.md:89 | spec document | Given a construct introduced by this spec under a foreign namespace | The construct MUST honour the DR-3 authoring rule (legacy parsers discard foreign-namespace subtrees in full; baseline children that legacy must see go at sibling, not nested, position). |
| N06.5 | context/06-naming-and-namespaces.md:96 | spec document | Given a construct whose semantics change across editions of this spec | A new `<year>` suffix MUST be used on its scheme URI. |
| N06.6 | context/06-naming-and-namespaces.md:99 | spec document | Given a construct whose semantics are unchanged across editions | The construct MAY keep its existing scheme URI. |
| N06.7 | context/06-naming-and-namespaces.md:101 | spec document | (unconditional) | The spec's chapter 2 (Normative references) MUST list the URIs introduced by the current edition explicitly. |
| N06.8 | context/06-naming-and-namespaces.md:110 | spec document | (unconditional, layout vocabulary) | The spec MUST reference the IAB-defined layout values without inventing new layout names at chapter level (restatement of R12.1 from the namespace-policy side). |
| N06.9 | context/06-naming-and-namespaces.md:115 | Broadcaster | Given a Broadcaster declares allowed layouts on a slot | The layout vocabulary MUST map 1:1 to IAB-defined ad-type values; no broadcaster-private or spec-private layout names are admissible (restatement of R12.2). |
| N06.10 | context/06-naming-and-namespaces.md:123 | spec document | Given a new element or attribute that represents the same semantic concept as an existing MPEG-DASH 6th edition construct (same kind of value, same units, same role) | The new identifier MUST reuse the baseline name verbatim. |
| N06.11 | context/06-naming-and-namespaces.md:131 | spec document | Given a new attribute that shares a name with a baseline DASH attribute but differs in semantics (different unit, reference frame, or domain of values) | The new identifier MUST be renamed (prefix, suffix, or full rename) so the difference is visible at the call site. |
| N06.12 | context/06-naming-and-namespaces.md:143 | spec document | Given SGAI-namespaced elements need an attribute scoped like baseline `@earliestResolutionTimeOffset` but in `EventStream@timescale` units | The SGAI attribute MUST NOT reuse the baseline name verbatim (worked example of N06.11). |
| N06.13 | context/06-naming-and-namespaces.md:147 | spec document | Given the duration attribute of a non-linear sub-MPD Period | The spec MUST use `@duration` (not invent `@overlayDuration` or similar), since the underlying semantics match the DASH baseline (worked example of N06.10). |

## Assertions per R

- R1: 3
- R2: 4
- R3: 3
- R4: 5
- R5: 7
- R6: 6
- R7: 5
- R8: 2
- R9: 3
- R10: 3
- R11: 3
- R12: 3
- R13: 4
- R14: 2
- R15: 3

Total in R-blocks: 56.

## Assertions per actor

- Player: 25
- spec document: 32
- ADS: 6
- all: 5
- Broadcaster: 4

Total: 72.

## Assertions per source doc

- context/02-actors.md: 0
- context/03-requirements.md: 56
- context/04-use-cases.md: 2
- context/05-dash-linear-interfaces.md: 1
- context/06-naming-and-namespaces.md: 13
- context/99-glossary.md: 0

Total: 72.

## Orphan assertions

Orphans are RFC 2119 sentences outside `context/03-requirements.md` that
do not map cleanly to one of R1..R15. UC04.1, UC04.2, I05.1, N06.3,
N06.8 and N06.9 are excluded — they restate R1.1, R1.2, R6.6, R13.4,
R12.1 and R12.2 respectively, mapping cleanly to existing requirements.

- **N06.1** (06-naming-and-namespaces.md:22): year-pinned URN pattern
  `urn:svta:dash:<construct>:<year>` for every new event scheme.
  Signals a missing R on naming / URI policy (or an extension of R1.2
  covering URI shape, not only XML extension points).
- **N06.2** (06-naming-and-namespaces.md:37): forward-compat for a
  Player implementing edition N+1 (SHOULD recognise both `:N:` and
  `:N+1:` URIs). Signals a missing R on cross-edition forward
  compatibility for Players, complementing R1's older-Player direction.
- **N06.5** (06-naming-and-namespaces.md:96): semantics change → new
  `<year>` suffix on scheme URI. Versioning obligation; absorbs with
  N06.1 into the same missing R on naming / versioning policy.
- **N06.6** (06-naming-and-namespaces.md:99): semantics unchanged →
  scheme URI MAY be kept. Versioning permission; same family as N06.5.
- **N06.7** (06-naming-and-namespaces.md:101): chapter 2 (Normative
  references) MUST list current-edition URIs explicitly. Spec-doc
  structural obligation; could absorb into R9 (governance) or stand as
  a new thin R on spec-document structure.
- **N06.10** (06-naming-and-namespaces.md:123): same-semantics
  identifier MUST reuse baseline DASH name verbatim. Naming consistency
  obligation; signals a missing R on naming consistency with the
  baseline DASH vocabulary.
- **N06.11** (06-naming-and-namespaces.md:131): shared-name-differing-
  semantics identifier MUST be renamed. Same family as N06.10 — both
  belong to the same proposed naming-consistency R.
- **N06.12** (06-naming-and-namespaces.md:143): SGAI attribute analogous
  to `@earliestResolutionTimeOffset` in `EventStream@timescale` units
  MUST NOT reuse the baseline name. Worked example refining N06.11;
  folds into the same proposed naming-consistency R.
- **N06.13** (06-naming-and-namespaces.md:147): `Period@duration` of a
  non-linear sub-MPD MUST be `@duration` (not invented). Worked example
  refining N06.10; folds into the same proposed naming-consistency R.

Suggested consolidation: introduce one new R covering naming / URI /
versioning policy (absorbs N06.1, N06.2, N06.5, N06.6, N06.10, N06.11,
N06.12, N06.13), and either fold N06.7 into R9 or introduce a thin R on
spec-document structure (chapter 2 must list edition URIs). The first
proposed R is the larger gap and explains most of the orphan volume.

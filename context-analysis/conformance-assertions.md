[GROUNDED_BY=spec-only]

# Conformance assertions

Normative obligations extracted from `../context/`. Each row is
actionable as a test in spec chapter 10. R<N>.<n> IDs are reused
verbatim from `../context/03-requirements.md`; ancillary MUST /
SHOULD / MAY sentences in other context files use the file-prefixed
ID convention (`A2.<n>`, `I05.<n>`, `N06.<n>`, `G99.<n>`).

| Assertion ID | Source | Actor | Condition | Obligation |
|--------------|--------|-------|-----------|------------|
| R1.1 | context/03-requirements.md (R1) | Player | Given an MPD containing an SGAI construct not implemented | MUST ignore the unknown construct and continue primary content uninterrupted |
| R1.2 | context/03-requirements.md (R1) | Publisher / spec document | (unconditional) | Every new SGAI construct MUST be expressed using one of the extension points in 08-dash-extension-rules.md (DR-2 / DR-3, §5.10, §5.8.4.x); MUST NOT use paths that violate the DR-1 / DR-5 chain |
| R1.3 | context/03-requirements.md (R1) | Publisher / spec document | (unconditional) | MUST NOT alter or override the semantics of any pre-existing MPEG-DASH 6th edition construct |
| R2.1 | context/03-requirements.md (R2) | Publisher | (unconditional) | Slot constraints (max duration, opt-in policies, layout templates) MUST be declared in the MPD, not inferred at runtime |
| R2.2 | context/03-requirements.md (R2) | ADS + APS | (unconditional) | ADS MUST decide which ads to serve and output as decision document; APS MUST convert to resolution document; neither MUST be expected to enforce Publisher constraints |
| R2.3 | context/03-requirements.md (R2) | Player | Given a candidate in the resolution document | MUST validate against Publisher-declared constraints and render only those that satisfy them |
| R2.4 | context/03-requirements.md (R2) | spec document | (unconditional) | Every new mechanism MUST be expressible within the four-actor contract |
| R3.1 | context/03-requirements.md (R3) | spec document | (unconditional) | MUST enumerate supported device classes and, for each, the expected behaviour for every ad opportunity type covered by the UCs |
| R3.2 | context/03-requirements.md (R3) | Player | For every ad opportunity type defined in the spec | MUST produce a defined behaviour (render, fall back, or skip); undefined behaviour is non-conforming |
| R3.3 | context/03-requirements.md (R3) | Player | (unconditional) | MUST NOT attempt to render an ad form (video, image, HTML) that its device class cannot render |
| R4.1 | context/03-requirements.md (R4) | Publisher | For every ad slot in the MPD | MUST declare a maximum duration |
| R4.2 | context/03-requirements.md (R4) | Player | When cumulative duration of accepted candidates would exceed cap | MUST stop rendering at the cap boundary, even mid-ad |
| R4.3 | context/03-requirements.md (R4) | Player | (unconditional) | MUST NOT extend a slot beyond the Publisher-declared cap regardless of ADS metadata or candidate count |
| R4.4 | context/03-requirements.md (R4) | ADS | (unconditional) | NOT required to respect the cap when selecting candidates; conformance check MUST NOT fail solely because ADS cumulative duration exceeds cap |
| R4.5 | context/03-requirements.md (R4) | Player | When actual rendered length exceeds declared duration | MUST enforce cap against actual length, not declared length (trim-during-play) |
| R5.1 | context/03-requirements.md (R5) | APS | Each candidate in the resolution document | MUST carry one or more renderable presentation options as an ordered list, document order = preference order, preserved from ADS without reordering |
| R5.2 | context/03-requirements.md (R5) | Player | Given an accepted candidate | MUST evaluate options in document order and render the first whose form and layout it can satisfy |
| R5.3 | context/03-requirements.md (R5) | Player | When a candidate has no form renderable on the device | MUST skip the candidate, falling back per policy |
| R5.4 | context/03-requirements.md (R5) | ADS + APS | (unconditional) | NOT required to maintain a device-class matrix or per-Player capability view to produce candidates |
| R5.5 | context/03-requirements.md (R5) | ADS | (unconditional) | MAY emit candidates carrying multiple presentation options; options form a single ordered list (document order = ADS preference) |
| R5.6 | context/03-requirements.md (R5) | Player | Given options to walk | MUST walk in document order and, for each, check against device capabilities AND Publisher-declared allowed layouts; render first option that satisfies both |
| R5.7 | context/03-requirements.md (R5) | Player | When no option on a candidate satisfies R5.6 | MUST skip the candidate, fall through to next candidate preserving R7 order, or to primary content when exhausted |
| R6.1 | context/03-requirements.md (R6) | spec document | (unconditional) | MUST specify how in-band ad tracking beacons are carried in the resolution document |
| R6.2 | context/03-requirements.md (R6) | APS | (unconditional) | SHOULD carry tracking beacons as `<Event>` entries inside an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015` |
| R6.3 | context/03-requirements.md (R6) | spec document | When introducing a new tracking carrier | MAY do so only if callback scheme cannot express the required semantics AND only after documented gap analysis per R9 |
| R6.4 | context/03-requirements.md (R6) | Player | (unconditional) | MUST safely ignore unknown namespaces on tracking-related extension elements per R1 |
| R7.1 | context/03-requirements.md (R7) | Player | Given a resolution document with multiple candidates | MUST play candidates in the order declared by ADS (preserved by APS), except for candidates dropped under R7.2/R7.3 |
| R7.2 | context/03-requirements.md (R7) | Player | Candidate has no form renderable on device (R3/R5) | MAY drop the candidate |
| R7.3 | context/03-requirements.md (R7) | Player | Candidate's declared duration would push cumulative past cap | MAY drop before playback (drop-before-play) |
| R7.4 | context/03-requirements.md (R7) | Player | (unconditional) | MUST NOT re-order, deduplicate, or rearrange remaining candidates after R7.2/R7.3 |
| R7.5 | context/03-requirements.md (R7) | Player | Accepted candidate's actual rendered length exceeds cap | MUST trim mid-rendering (trim-during-play) per R4 |
| R8.1 | context/03-requirements.md (R8) | spec document | Every new construct | MUST be accompanied by inline justification of why an existing MPEG-DASH construct could not be reused |
| R8.2 | context/03-requirements.md (R8) | spec document | Every deliberate omission of an existing reusable construct | MUST be documented inline with the design decision |
| R9.1 | context/03-requirements.md (R9) | spec document | (unconditional) | MUST reuse existing MPEG-DASH machinery wherever possible |
| R9.2 | context/03-requirements.md (R9) | spec document | (unconditional) | A new construct MUST NOT be introduced unless an existing one cannot be made to fit |
| R9.3 | context/03-requirements.md (R9) | spec document | Before introducing a new construct | MUST consider whether an extension to an existing construct would suffice; outcome MUST be documented |
| R10.1 | context/03-requirements.md (R10) | spec document | (unconditional) | Spatial arrangement of overlays MUST be delegated to HTML5/CSS layout primitives |
| R10.2 | context/03-requirements.md (R10) | spec document | (unconditional) | MUST NOT define a parallel layout standard for overlay placement |
| R10.3 | context/03-requirements.md (R10) | spec document | (unconditional) | Position semantics inside a layout MUST be expressed via the Positioning Templates section using HTML5/CSS primitives |
| R11.1 | context/03-requirements.md (R11) | spec document | Normative chapters | MUST NOT cite a specific VAST version as required |
| R11.2 | context/03-requirements.md (R11) | Player | (unconditional) | MUST be able to operate regardless of whether the ADS uses VAST |
| R11.3 | context/03-requirements.md (R11) | spec document | Any reference to VAST in the spec | MUST be in an annex or a non-normative note explicitly flagged as illustrative |
| R12.1 | context/03-requirements.md (R12) | spec document | (unconditional) | List of accepted ad-type values MUST be sourced from IAB definitions; reference to IAB source MUST be included |
| R12.2 | context/03-requirements.md (R12) | Publisher | Declaring allowed layouts on a slot | MUST use names that map 1:1 to IAB-defined ad-type values |
| R12.3 | context/03-requirements.md (R12) | APS | In the resolution document | MUST NOT emit form metadata for ad types outside the IAB-defined set used by this spec's edition |
| R13.1 | context/03-requirements.md (R13) | ADS + APS | (unconditional) | ADS MUST declare tracking schedule (which beacons, at which relative times); APS MUST transcribe verbatim using DASH callback events, timings relative to ad presentation timeline; APS adds / removes / reorders no beacons |
| R13.2 | context/03-requirements.md (R13) | Player | Given an ad accepted for rendering | MUST execute the tracking schedule it reads from the resolution document |
| R13.3 | context/03-requirements.md (R13) | Player | If R4 trims the ad before a scheduled beacon's time | MUST stop firing remaining beacons at the trim boundary |
| R13.4 | context/03-requirements.md (R13) | spec document | (unconditional) | MUST NOT introduce a new tracking event scheme; reuse of the DASH baseline callback mechanism is mandatory |
| R14.1 | context/03-requirements.md (R14) | Player | Resolution document for a non-linear slot declares >1 ad form | MUST present forms in sequence in document order; each form starts when previous ends |
| R14.2 | context/03-requirements.md (R14) | Player | (unconditional) | MUST enforce Publisher-declared slot cap (R4) against the cumulative duration of the form sequence, trimming or dropping per R4/R7 |
| R14.3 | context/03-requirements.md (R14) | spec document | (unconditional) | MUST NOT introduce a construct that implies or requires parallel rendering of two or more non-linear ad forms |
| R15.1 | context/03-requirements.md (R15) | spec document | Wherever creative carrier types are discussed | MUST enumerate the admissible set {video, image, HTML} exactly; new carrier types MUST NOT be added in annexes / examples / notes |
| R15.2 | context/03-requirements.md (R15) | APS + Publisher | Ad candidates in the resolution document AND Publisher-declared forms | MUST carry a creative whose mimeType falls under one of the three admissible categories |
| R15.3 | context/03-requirements.md (R15) | Player | Candidate whose creative carrier mimeType is not in the admissible set | MAY skip the candidate |
| R16.1 | context/03-requirements.md (R16) | Player | Upon pause-to-play transition by viewer | MUST remove any rendered pause-ad form from the screen within one rendering frame |
| R16.2 | context/03-requirements.md (R16) | Player | Upon the same transition | MUST cease firing tracking beacons scheduled for the dismissed pause-ad |
| R17.1 | context/03-requirements.md (R17) | Player | While viewer paused inside a pause-ad window AND an overlay is active | MUST render the pause-ad and suspend the overlay |
| R17.2 | context/03-requirements.md (R17) | Player | On resume from pause | MUST dismiss the pause-ad and restore overlay rendering if overlay slot window still active |
| R17.3 | context/03-requirements.md (R17) | Player | If overlay slot window expired during the pause | MUST keep the overlay surface clear on resume |
| R17.4 | context/03-requirements.md (R17) | spec document | (unconditional) | MUST carry no construct that lets Publisher / ADS / APS invert pause-ad-over-overlay priority |
| R18.1 | context/03-requirements.md (R18) | spec document | (unconditional) | MUST document the MPD event URL pattern (Player-visible input) and the resolution document format (Player-visible output) |
| R18.2 | context/03-requirements.md (R18) | Publisher / APS / ADS | (unconditional) | Bilateral contracts (Publisher↔APS event URL; APS↔ADS decisioning invocation) MUST be established and maintained outside this specification |
| R19.1 | context/03-requirements.md (R19) | Player | (unconditional) | MUST render every ad form at the same playback speed as the primary content at the moment of presentation |
| R19.2 | context/03-requirements.md (R19) | Player | When primary is at non-1x speed | MUST NOT force an ad to 1x; the ad follows primary speed |
| R19.3 | context/03-requirements.md (R19) | Player | (unconditional) | MUST compute effective on-screen (wall-clock) duration as `duration / playback_speed`; cap enforcement and beacon scheduling operate on the presentation-timeline `duration` |
| R20.1 | context/03-requirements.md (R20) | Player | Same-family ad opportunity windows overlap in time in the primary MPD | MUST select the first overlapping window and attempt to resolve; MUST resort to subsequent windows ONLY when cannot access first's resolution document; MUST NOT fall through when first's resolution doc is accessible |
| R21.1 | context/03-requirements.md (R21) | Player | Presenting a pause-ad form | MUST present fullscreen, occupying the entire screen surface; MUST NOT render as a partial overlay; MAY release primary content and overlay resources |
| R22.1 | context/03-requirements.md (R22) | Player | At any instant `t` | MUST keep at most one non-linear ad form active on screen; MUST NOT present two or more simultaneously |
| R23.1 | context/03-requirements.md (R23) | APS | Application-level metadata with no native DASH carrier declared in ADS VAST | MAY convey via vendor-namespaced extension elements in the resolution document |
| R24.1 | context/03-requirements.md (R24) | APS / spec document | Non-AV ad form (mediaType ∈ {html, image, ...}) | Asset URL MUST NOT be expressed as `@mimeType` on AdaptationSet/Representation reached through any RFC 4337-bound path (DR-1, DR-5); MUST be carried via one of the §5.2.1 / §5.10 / §5.8.4.x carriers (DR-6) per R1.2 |
| R25.1 | context/03-requirements.md (R25) | Player | In live content, viewer paused inside a pause-ad window | MUST keep presentation time frozen inside that window for the full duration of the pause, regardless of live edge advancing; any resume-at-live-edge MUST be treated as a Player action after resume |
| R26.1 | context/03-requirements.md (R26) | APS + Publisher | Layout that leaves screen partially uncovered | Background fill MUST be carried as a composition attribute of the slot/layout, NOT as a separate presentation option (R5) |
| R26.2 | context/03-requirements.md (R26) | Player | Layout that leaves the screen partially uncovered | MUST composite the three elements (primary, ad, background fill); MAY composite Publisher fallback when no advertiser background and Publisher declared one |
| R26.3 | context/03-requirements.md (R26) | Player | Side-by-side layout | Element count and type determine admissible device classes; side-by-side with video ad needs two decoders + image surface and MUST NOT be selected on single-decoder device |
| A2.1 | context/02-actors.md | APS | Across renderable presentation options | MUST be presented as an ordered list whose document order is the preference order, the Player rendering the first satisfiable option |
| A2.2 | context/02-actors.md | Player | (unconditional) | MUST validate each candidate against MPD-declared constraints; any candidate that violates them MUST be discarded |
| I05.1 | context/05-dash-linear-interfaces.md | APS | All `<Event @presentationTime>` in the resolution document (`ListMPD` / single-period alt MPD) | MUST be expressed relative to the start of the ad break (slot start), not relative to wall-clock or primary content timeline |
| I05.2 | context/05-dash-linear-interfaces.md | Player | Cumulative sum of ListMPD Period durations vs parent SGAI event `@maxDuration` | MUST terminate playback at the cap (§5.16.5) when the sum exceeds the parent cap |
| I05.3 | context/05-dash-linear-interfaces.md | Publisher | `InsertPresentation` event | "shall not appear if the MPD type is dynamic" (§5.16.3) — restricted to VOD content |
| N06.1 | context/06-naming-and-namespaces.md | spec document | Any new event scheme introduced by this spec | MUST use the year-pinned pattern `urn:svta:dash:<construct>:<year>` under the SVTA Ads WG namespace |
| N06.2 | context/06-naming-and-namespaces.md | spec document | Reusing an existing scheme URI across editions with altered semantics | Is NOT permitted; a fresh URI per edition is required |
| N06.3 | context/06-naming-and-namespaces.md | spec document | When this spec needs to express a component equivalent to one already defined in MPEG-DASH 6th edition | MUST reuse the existing baseline construct with all its characteristics (name, defaults, value domain, units, semantics) |

## Assertions per R

- R1: 3, R2: 4, R3: 3, R4: 5, R5: 7, R6: 4, R7: 5, R8: 2, R9: 3, R10: 3
- R11: 3, R12: 3, R13: 4, R14: 3, R15: 3, R16: 2, R17: 4, R18: 2, R19: 3, R20: 1
- R21: 1, R22: 1, R23: 1, R24: 1, R25: 1, R26: 3
- **Total R-block assertions: 75**

## Assertions per actor

- Publisher: 8 (R1.2, R1.3, R2.1, R4.1, R12.2, R15.2 shared, R18.2 shared, I05.3)
- ADS: 5 (R2.2 shared, R4.4, R5.4 shared, R5.5, R13.1 shared)
- APS: 12 (R2.2 shared, R5.1, R5.4 shared, R6.2, R12.3, R13.1 shared, R15.2 shared, R18.2 shared, R23.1, R24.1 shared, R26.1 shared, A2.1, I05.1)
- Player: 35 (R1.1, R2.3, R3.2, R3.3, R4.2, R4.3, R4.5, R5.2, R5.3, R5.6, R5.7, R6.4, R7.1, R7.2, R7.3, R7.4, R7.5, R11.2, R13.2, R13.3, R14.1, R14.2, R15.3, R16.1, R16.2, R17.1, R17.2, R17.3, R19.1, R19.2, R19.3, R20.1, R21.1, R22.1, R25.1, R26.2, R26.3, A2.2, I05.2)
- spec document: 17 (R1.2 shared, R1.3 shared, R2.4, R3.1, R6.1, R6.3, R8.1, R8.2, R9.1, R9.2, R9.3, R10.1, R10.2, R10.3, R11.1, R11.3, R13.4, R14.3, R15.1, R17.4, R18.1, R24.1 shared, N06.1, N06.2, N06.3)
- all / shared assertions counted under each actor they bind (some
  R<N>.<n> rows bind two actors — counted in both groups above)

## Assertions per source doc

- `context/03-requirements.md`: 75
- `context/02-actors.md`: 2
- `context/05-dash-linear-interfaces.md`: 3
- `context/06-naming-and-namespaces.md`: 3
- **Total in this matrix: 83**

## Orphan assertions

MUST / SHOULD / MAY sentences found outside `context/03-requirements.md`
that do not map cleanly to one of R1..R26:

- **I05.3** (`context/05-dash-linear-interfaces.md`, slot-mechanism
  choice section): the `InsertPresentation` restriction to
  VOD-only ("shall not appear if the MPD type is dynamic", §5.16.3
  baseline) is a DASH 6th constraint the spec must surface as a
  Publisher authoring rule. **Suggested absorption**: into R2 (the
  Publisher's slot declaration obligation) or surface in a new R
  governing slot-mechanism choice across content types. Today it
  lives only in the linear-interfaces reference.
- **N06.2** (`context/06-naming-and-namespaces.md`, versioning
  section): the prohibition against reusing existing scheme URIs
  across editions with altered semantics is an authoring rule
  binding the spec document. **Suggested absorption**: into R1 (R1
  is about backward compatibility across editions; the year-pin
  rule is the mechanical guarantee that R1 holds across edition
  bumps), or treat as a sub-criterion of R8 (justification).
- **N06.3** (`context/06-naming-and-namespaces.md`, "Naming
  consistency with baseline DASH" section): the requirement to
  reuse an existing DASH 6th construct (with all its
  characteristics) when an SGAI construct is conceptually
  equivalent. **Suggested absorption**: into R9 — this is the
  positive form of R9.1 ("reuse existing machinery wherever
  possible"), with the extra teeth that reuse must preserve name /
  defaults / value domain / units / semantics. R9 could absorb
  this as R9.4 in a future edition.

The orphans surfaced above are conformant signals — DASH-edition
mechanics and authoring-consistency rules — but they would be
clearer if absorbed back into the R1 / R8 / R9 governance Rs. No
new R is implied; the existing Rs can host them.

[GROUNDED_BY=spec-only]

# Conformance assertions

Normative obligations extracted from `../context/`. Each row is actionable as a chapter-10 test case. RFC 2119 keywords preserved verbatim.

| Assertion ID | Source | Actor | Condition | Obligation |
|---|---|---|---|---|
| R1.1 | context/03-requirements.md:30 | Player | MPD contains an SGAI construct the Player does not implement | Legacy Player MUST ignore the unknown construct and continue primary content uninterrupted. |
| R1.2 | context/03-requirements.md:34 | spec document | New SGAI construct introduced by this proposal | MUST be expressed via §5.2.1 / §5.10 / §5.8.4.8-9 extension points; MUST NOT use DR-1/DR-5 paths; Annex F admissible only under DR-4 conditions. |
| R1.3 | context/03-requirements.md:48 | spec document | Any pre-existing MPEG-DASH 6th edition construct | The spec MUST NOT alter or override its semantics. |
| R2.1 | context/03-requirements.md:58 | Broadcaster | Ad slot present in MPD | Slot constraints (max duration, opt-ins, layouts) MUST be declared by the Broadcaster in the MPD, not inferred at runtime. |
| R2.2 | context/03-requirements.md:62 | ADS | ADS produces ad candidates | MUST produce candidates as a resolution document; MUST NOT be expected to enforce Broadcaster constraints. |
| R2.3 | context/03-requirements.md:65 | Player | ADS-returned candidates received | MUST validate candidates against Broadcaster-declared constraints and render only those that satisfy them. |
| R2.4 | context/03-requirements.md:68 | spec document | New mechanism proposed | MUST be expressible within the three-actor contract; MUST be rejected/redesigned otherwise. |
| R3.1 | context/03-requirements.md:82 | spec document | (unconditional) | Spec MUST enumerate supported device classes and per-class expected behaviour for each ad opportunity type. |
| R3.2 | context/03-requirements.md:85 | Player | Any supported device class, any defined ad opportunity type | MUST produce a defined behaviour (render, fall back, or skip); undefined behaviour is non-conforming. |
| R3.3 | context/03-requirements.md:89 | Player | Device class cannot render an ad form | MUST NOT attempt to render that form. |
| R4.1 | context/03-requirements.md:109 | Broadcaster | Every ad slot (linear or non-linear) in MPD | MUST declare a maximum duration. |
| R4.2 | context/03-requirements.md:112 | Player | Cumulative duration of accepted candidates would exceed cap | MUST stop rendering at the cap boundary, even mid-ad. |
| R4.3 | context/03-requirements.md:116 | Player | (unconditional) | MUST NOT extend a slot beyond the Broadcaster-declared cap regardless of ADS metadata or candidate count. |
| R4.4 | context/03-requirements.md:119 | ADS | Conformance check on ADS | MUST NOT fail solely because cumulative candidate duration exceeds the cap. |
| R4.5 | context/03-requirements.md:123 | Player | Actual rendered length of accepted candidate exceeds declared duration | MUST enforce cap against actual length, not declared length. |
| R5.1 | context/03-requirements.md:146 | ADS | Ad candidate returned | MUST carry one or more renderable forms; MAY rank them via ADS hints. |
| R5.2 | context/03-requirements.md:149 | Player | Accepted candidate with multiple renderable forms | MUST choose the best form it can render on its device. |
| R5.3 | context/03-requirements.md:152 | Player | Candidate has no form renderable on device | MUST skip it, falling back to next candidate or primary content per policy. |
| R5.4 | context/03-requirements.md:155 | ADS | Producing candidates | MUST NOT be required to maintain a device-class matrix or per-Player capability view. |
| R5.5 | context/03-requirements.md:158 | ADS | Ad candidate | MAY carry multiple forms and MAY carry multiple admissible layouts; ADS priority hints MAY rank both dimensions independently. |
| R5.6 | context/03-requirements.md:161 | Player | Form/layout selection | MUST intersect (a) device caps, (b) Broadcaster-allowed layouts, (c) ADS priority hints; combinations failing any MUST NOT be rendered. |
| R5.7 | context/03-requirements.md:166 | Player | No form/layout combination satisfies R5.6 | MUST skip the candidate; fall through to next ADS-returned candidate or to primary content. |
| R6.1 | context/03-requirements.md:187 | spec document | (unconditional) | Spec MUST specify how in-band ad tracking beacons are carried in the resolution document. |
| R6.2 | context/03-requirements.md:189 | all | Implementations carrying tracking beacons | SHOULD carry beacons as `<Event>` inside an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015` in the ad MPD or sub-MPD. |
| R6.3 | context/03-requirements.md:193 | spec document | Introducing a new tracking carrier | MAY be done only when callback scheme cannot express the required semantics, and only after documented R9 gap analysis. |
| R6.4 | context/03-requirements.md:197 | all | Application-level metadata with no native DASH carrier (ClickThrough, AdSystem, AdTitle, UniversalAdId, etc.) | MAY be conveyed via vendor-namespaced extension elements. |
| R6.5 | context/03-requirements.md:201 | Player | Tracking-related extension element in unknown namespace | MUST safely ignore it. |
| R6.6 | context/03-requirements.md:204 | all | Non-AV ad form (mediaType ∈ {html, image, ...}) carried | Asset URL MUST NOT be `@mimeType` on AdaptationSet/Representation reachable via DR-1/DR-5; MUST use a §5.2.1 / §5.10 / §5.8.4.x carrier per DR-6. |
| R7.1 | context/03-requirements.md:235 | Player | ADS resolution document has more than one candidate | MUST play candidates in ADS-declared order except those dropped under R7.2/R7.3. |
| R7.2 | context/03-requirements.md:239 | Player | Candidate has no form renderable on device | MAY drop it (R3/R5). |
| R7.3 | context/03-requirements.md:241 | Player | Declared duration would push cumulative slot duration past cap | MAY drop the candidate before playback ("drop before play"). |
| R7.4 | context/03-requirements.md:244 | Player | After applying R7.2/R7.3 | MUST NOT re-order, deduplicate, or otherwise rearrange remaining candidates. |
| R7.5 | context/03-requirements.md:247 | Player | Accepted candidate's actual rendered length exceeds cap | MUST trim mid-rendering ("trim during play") per R4. |
| R8.1 | context/03-requirements.md:318 | spec document | New construct introduced by the proposal | MUST be accompanied by inline justification why an existing MPEG-DASH construct could not be reused. |
| R8.2 | context/03-requirements.md:321 | spec document | Deliberate omission of an existing MPEG-DASH construct a reader might expect | MUST be documented inline with the design decision. |
| R9.1 | context/03-requirements.md:332 | spec document | Designing any new mechanism | Proposal MUST reuse existing MPEG-DASH machinery wherever possible. |
| R9.2 | context/03-requirements.md:335 | spec document | (unconditional) | A new construct MUST NOT be introduced unless an existing one cannot be made to fit. |
| R9.3 | context/03-requirements.md:337 | spec document | Before introducing a new construct | Proposal MUST consider whether an extension to an existing construct would suffice, and document the outcome. |
| R10.1 | context/03-requirements.md:349 | spec document | Spatial arrangement of overlays | MUST be delegated to HTML5/CSS layout primitives. |
| R10.2 | context/03-requirements.md:351 | spec document | (unconditional) | Spec MUST NOT define a parallel layout standard for overlay placement. |
| R10.3 | context/03-requirements.md:353 | spec document | Position semantics inside a layout | Out of scope for the spec; MUST be expressed via Positioning Templates using HTML5/CSS primitives. |
| R11.1 | context/03-requirements.md:258 | spec document | Normative chapters of the spec | MUST NOT cite a specific VAST version as required. |
| R11.2 | context/03-requirements.md:260 | Player | ADS does not use VAST at all | MUST be able to operate against such an ADS. |
| R11.3 | context/03-requirements.md:263 | spec document | Any reference to VAST in the spec | MUST be in an annex or non-normative note flagged as illustrative. |
| R12.1 | context/03-requirements.md:277 | spec document | List of accepted ad-type values in the spec | MUST be sourced from IAB definitions; a reference to the IAB source MUST be included. |
| R12.2 | context/03-requirements.md:280 | Broadcaster | Declaring allowed layouts on a slot | MUST use names that map 1:1 to IAB-defined ad-type values (no broadcaster-private names). |
| R12.3 | context/03-requirements.md:284 | ADS | Emitting form metadata | MUST NOT emit ad types outside the IAB-defined set used by this spec edition. |
| R13.1 | context/03-requirements.md:296 | Player | Non-linear ad accepted for rendering | MUST fire an impression beacon at the instant overlay becomes visible. |
| R13.2 | context/03-requirements.md:299 | Player | Firing quartile beacons | SHOULD time them against the Broadcaster-declared overlay window, not the ad's internal duration. |
| R13.3 | context/03-requirements.md:302 | Player | R4 trims overlay before all quartiles fire | MUST stop firing beacons at the trim boundary. |
| R13.4 | context/03-requirements.md:305 | spec document | (unconditional) | Spec MUST NOT introduce a new tracking event scheme; reuse of linear baseline mechanism is mandatory. |
| UC04.1 | context/04-use-cases.md:687 | Player | Encounters unrecognised event type or construct in manifest | MUST skip the unknown construct and continue primary content as if not present. |
| UC04.2 | context/04-use-cases.md:705 | spec document | Any new construct introduced by the proposal | MUST be expressible via extension points that yield silent skip on legacy Players. |
| I05.1 | context/05-dash-linear-interfaces.md:335 | spec document | Non-linear chapters carrying non-AV asset URLs (HTML, image, other) | MUST place them outside the AdaptationSet axis, via a DR-6 carrier. |
| N06.1 | context/06-naming-and-namespaces.md:22 | spec document | New event scheme introduced by this spec | MUST use the year-pinned pattern `urn:svta:dash:<construct>:<year>`. |
| N06.2 | context/06-naming-and-namespaces.md:37 | Player | Implementing edition N+1 | SHOULD recognise both `:N:` and `:N+1:` URIs per backward-compat rules of that edition. |
| N06.3 | context/06-naming-and-namespaces.md:48 | all | Implementations carrying tracking beacons for SGAI ads | MUST reuse the MPEG-DASH 6th edition baseline tracking callback scheme. |
| N06.4 | context/06-naming-and-namespaces.md:55 | spec document | Qualabs-private experimental extension not part of this spec | MUST use the Qualabs vendor namespace `urn:qualabs:<feature>:<year>`. |
| N06.5 | context/06-naming-and-namespaces.md:89 | spec document | Construct introduced by this spec | MUST honour the DR-3 authoring rule for foreign-namespace subtree placement. |
| N06.6 | context/06-naming-and-namespaces.md:96 | spec document | Construct's semantics change across editions | MUST use a new `<year>` suffix on its scheme URI. |
| N06.7 | context/06-naming-and-namespaces.md:99 | spec document | Construct's semantics unchanged across editions | MAY keep its existing URI. |
| N06.8 | context/06-naming-and-namespaces.md:101 | spec document | Each edition of this spec | Chapter 2 (Normative references) MUST list URIs introduced by the current edition explicitly. |
| N06.9 | context/06-naming-and-namespaces.md:110 | spec document | Referencing accepted layout names | MUST reference IAB-defined values without inventing new layout names at chapter level. |
| N06.10 | context/06-naming-and-namespaces.md:115 | spec document | Layout vocabulary used by the spec | MUST map 1:1 to IAB-defined ad-type values; no spec-private layout names admissible. |
| N06.11 | context/06-naming-and-namespaces.md:123 | spec document | New element/attribute represents same semantic concept as a baseline DASH construct | New identifier MUST reuse the baseline name verbatim. |
| N06.12 | context/06-naming-and-namespaces.md:131 | spec document | New attribute shares name with baseline DASH attribute but differs in semantics | New identifier MUST be renamed so difference is visible at call site. |
| N06.13 | context/06-naming-and-namespaces.md:143 | spec document | SGAI-namespaced element needs an attribute scoped like `@earliestResolutionTimeOffset` but in different units | MUST NOT reuse the baseline name verbatim. |
| N06.14 | context/06-naming-and-namespaces.md:147 | spec document | Non-linear sub-MPD Period duration equals parent slot's overlay window | Spec MUST use `@duration` (not invent `@overlayDuration` or similar). |

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

## Assertions per actor

- Broadcaster: 3
- ADS: 7
- Player: 21
- spec document: 32
- all: 5

## Assertions per source doc

- context/02-actors.md: 0 (no RFC 2119 keywords)
- context/03-requirements.md: 51
- context/04-use-cases.md: 2
- context/05-dash-linear-interfaces.md: 1
- context/06-naming-and-namespaces.md: 14
- context/99-glossary.md: 0 (no RFC 2119 keywords)

## Orphan assertions

MUST/SHOULD/MAY found outside `context/03-requirements.md` that do not map cleanly to R1..R13.

| Assertion ID | Source | Summary | Suggested absorption |
|---|---|---|---|
| N06.1 | context/06-naming-and-namespaces.md:22 | Year-pinned `urn:svta:dash:<construct>:<year>` pattern for new schemes. | New R for "naming policy" (URN/year-pin); R1 only constrains extension *points*, not URN shape. |
| N06.2 | context/06-naming-and-namespaces.md:37 | Player implementing edition N+1 SHOULD recognise both `:N:` and `:N+1:` URIs. | New R for "cross-edition Player compatibility"; not covered by R1's legacy-Player rule. |
| N06.4 | context/06-naming-and-namespaces.md:55 | Qualabs vendor extensions MUST use `urn:qualabs:<feature>:<year>`. | Out-of-spec policy; flag as non-normative or absorb into naming-policy R alongside N06.1. |
| N06.6 | context/06-naming-and-namespaces.md:96 | Semantics change across editions MUST bump `<year>` suffix. | New R for "versioning policy"; complement to N06.1. |
| N06.7 | context/06-naming-and-namespaces.md:99 | Unchanged semantics MAY keep existing URI. | Same versioning R as N06.6. |
| N06.11 | context/06-naming-and-namespaces.md:123 | Same semantics as baseline → reuse baseline name verbatim. | New R for "naming consistency with baseline DASH"; not covered by R8/R9 (those govern reuse of constructs, not names). |
| N06.12 | context/06-naming-and-namespaces.md:131 | Same name as baseline but different semantics → rename. | Same naming-consistency R as N06.11. |
| N06.13 | context/06-naming-and-namespaces.md:143 | SGAI attribute with timescale units MUST NOT reuse `@earliestResolutionTimeOffset` verbatim. | Specific application of N06.11/N06.12; same naming-consistency R. |
| N06.14 | context/06-naming-and-namespaces.md:147 | Non-linear sub-MPD Period duration MUST use `@duration`, not `@overlayDuration`. | Specific application of N06.11; same naming-consistency R. |

Net signal: a **naming/versioning policy R** is missing from chapter 03 and should be added (covers N06.1, N06.4, N06.6, N06.7, N06.11–N06.14). N06.2 implies a separate **cross-edition Player compatibility R** distinct from R1's legacy-skip rule.

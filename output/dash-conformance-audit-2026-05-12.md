[GROUNDED_BY=notebooklm]

# DASH conformance audit — SGAI spec v2

**Audit target**: `output/sgai-spec-2026-05-12.md` (commit 565ddb3).
**Reference**: MPEG-DASH 6th edition (ISO/IEC 23009-1:2025).
**Method**: inventory of every construct introduced or reused by the
spec + 7 grounded queries against the "Streaming Protocols — DASH,
HLS, C2PA, DRM" notebook in NotebookLM (DASH-6th source loaded).
Each construct receives a verdict (Conforming / Marginal /
Non-conforming) against the cited DASH rule. The spec's own
backward-compat audit table (Chapter 5 §5.10) is an internal check;
this audit is independent.

## Scope

In scope: every new scheme URI, new XML element, new attribute on a
new or baseline element, new profile-URI usage, new structural
arrangement of baseline elements, and re-use of the callback event
scheme. Examples in annexes A through E are audited as concrete
instances of the chapter 5 constructs.

Out of scope: design-level concerns already raised in
`spec-validation-2026-05-12.md` (gaps, edge cases) — those are about
under-specification, not DASH-schema conformance. This audit only
asks: *given the spec's wording, would a DASH-6th-conformant Player
parse and execute the construct as the spec intends, or would the
DASH rules reject it / interpret it differently?*

## Method summary

- Inventory built from §5.1 (Document tree overview), §5.2 (Scheme
  URIs), §5.3 (common attributes), §5.4 (linear slot elements),
  §5.5 (non-linear slot elements), §5.6 (ListMPD shape), §5.7
  (sub-MPD SPS profile), §5.8 (tracking callback), §5.10 (spec's
  own backward-compat table), and annexes A through E.
- 7 NotebookLM queries against the DASH-6th notebook (active
  notebook: "Streaming Protocols — DASH, HLS, C2PA, DRM"). 7
  completed; 0 failed.
- Each construct assessed against the cited rule.

## Inventory and verdicts

Legend: V = Conforming (verified against DASH-6th cite),
M = Marginal (ambiguous, requires spec clarification),
N = Non-conforming (violates DASH-6th rule as written).

| ID | Construct | Type | Placement | Verdict | Rationale (DASH-6th cite) |
|----|-----------|------|-----------|---------|---------------------------|
| C-01 | `urn:svta:dash:sgai-overlay:2026` | New scheme URI | `EventStream@schemeIdUri` | V | §5.10.1 — DASH client subscribes to known schemes and ignores unknown Event Streams; new vendor scheme is the canonical extension point. |
| C-02 | `urn:svta:dash:sgai-pause-trigger:2026` | New scheme URI | `EventStream@schemeIdUri` | V | Same as C-01. |
| C-03 | `urn:svta:dash:sgai-list:2026` | New profile URI | `MPD@profiles` (alongside `urn:mpeg:dash:profile:list:2024`) | V (semantics); see C-22 (delimiter) | §8.14 — ListMPD profile may be carried alongside vendor-defined profile URIs (Interoperability Points pattern). |
| C-04 | `<svta:OverlayPresentation>` | New XML element | Child of `<Event>` (under svta-namespaced EventStream) | V | §5.2.1 — EventType carries `<xs:any namespace="##other" processContents="lax"/>`; foreign-namespaced children are valid extension points. |
| C-05 | `<svta:PauseAdPresentation>` | New XML element | Child of `<Event>` | V | Same as C-04. |
| C-06 | `<svta:CandidateForms>` | New XML element | Child of `<Period>` in non-linear ListMPD | V | §5.2.1 — PeriodType carries `<xs:any namespace="##other" processContents="lax"/>`. §8.14 explicitly permits foreign-namespace children on Period. |
| C-07 | `<svta:Form>` | New XML element | Child of `<svta:CandidateForms>` | V | Internal to svta-namespace subtree; ignore-if-unknown by ancestor (C-06). |
| C-08 | `<ImportedMPD>` placed inside `<svta:Form>` (not direct child of `<Period>`) | Structural arrangement | Inside non-linear ListMPD Period | M | §5.3.2.6 — ImportedMPD is schema-defined as a child of PeriodType. Nesting it inside `<svta:Form>` is not contemplated by the schema; semantics of `@earliestResolutionTimeOffset` ("offset from PeriodStart") become ambiguous when the parent is `<svta:Form>` and not `<Period>`. Legacy parsers are unaffected (whole svta subtree is opaque); SGAI-aware Players need an explicit semantic equivalence rule. |
| C-09 | `@maxDuration` on `<svta:OverlayPresentation>` / `<svta:PauseAdPresentation>` | New attribute on new element | N/A (whole element is svta) | V | New attribute on foreign-namespace element — not bound by the §5.16.5 AlternativeMPDEventType schema. Spec correctly restates §5.16.5 enforcement semantics (P-05). |
| C-10 | `@earliestResolutionTimeOffset` on new svta elements | Re-use of baseline attribute name on new element | N/A (whole element is svta) | M | §5.3.2.6.1 Table 5 defines `@earliestResolutionTimeOffset` in seconds as an attribute on ImportedMPD. Spec §5.3 declares the same attribute name on svta slot elements in `EventStream@timescale` units. Different unit semantics under the same attribute name is a readability hazard; not a schema violation (different element, different namespace), but worth disambiguating. |
| C-11 | `@allowedLayouts` on new svta elements | New attribute on new element | N/A | V | Free-form attribute on foreign-namespace element. |
| C-12 | `@maxConcurrency` on `<svta:OverlayPresentation>` | New attribute on new element | N/A | V | Same as C-11. |
| C-13 | `@windowStart` / `@windowEnd` / `@allowVideoForm` on `<svta:PauseAdPresentation>` | New attribute on new element | N/A | V | Same as C-11. |
| C-14 | `@candidateId` / `@candidatePriority` on `<svta:CandidateForms>` | New attribute on new element | N/A | V | Same as C-11. |
| C-15 | `@formId` / `@mediaType` / `@admissibleLayouts` / `@formPriority` / `@duration` on `<svta:Form>` | New attribute on new element | N/A | V | Same as C-11. |
| C-16 | Re-use of `<InsertPresentation>` and `<ReplacePresentation>` from §5.16.3 / §5.16.4 | Baseline elements, used as-is | Child of `<Event>` (linear-scheme EventStream) | V | §5.16.3 / §5.16.4. Spec states no semantic change. |
| C-17 | Re-use of `<ImportedMPD>` in linear ListMPD | Baseline element, used as-is | Direct child of `<Period>` | V | §5.3.2.6.1. `@uri` (not `@url`) is the canonical attribute name; spec's §5.6.1 and annex A both use `uri=` correctly. |
| C-18 | Re-use of `urn:mpeg:dash:event:callback:2015` for ad tracking | Baseline scheme, used as-is | `EventStream@schemeIdUri` inside per-form sub-MPD's Period | V | §5.10.4.x — callback scheme is general-purpose but VAST-aligned; Period-level placement is the spec-mandated location. |
| C-19 | Callback `Event@presentationTime` scheduled against the Broadcaster-declared overlay window (not against the form's intrinsic asset duration) | New tracking-time-base semantics on a baseline scheme | Per-form sub-MPD `Event/@presentationTime` | M | §5.10 specifies that `@presentationTime` is measured from PeriodStart of the sub-MPD's Period. Spec states "scheduled against the parent slot's `@maxDuration` window" (§5.7). This is consistent ONLY if the sub-MPD Period@duration is set equal to the slot window (not the asset duration). Spec does not state this requirement explicitly — implementations may set Period@duration = asset duration and break the alignment. |
| C-20 | Per-form sub-MPD `<AdaptationSet mimeType="text/html">` (Annex B §B.4) | Baseline element with new mimeType value | Inside SPS-profile sub-MPD | N | §8.15 inherits §7.3 MIME-type rules; §7.3 requires `@mimeType` per IETF RFC 4337, which limits SPS to `video/mp4`, `audio/mp4`, `application/mp4`. `text/html` is NOT a registered SPS mimeType. The spec violates SPS by directly using `text/html` for HTML forms. |
| C-21 | Per-form sub-MPD with image-form `mimeType="image/png"` (implied by §5.5 mediaType=image and annex B §B.4 prose) | Baseline element with new mimeType value | Inside SPS-profile sub-MPD | N | Same as C-20 — `image/png` is not RFC-4337-registered for SPS. Must be wrapped in `application/mp4` (e.g. as a single-sample track) to conform to §8.15. |
| C-22 | `MPD@profiles="urn:mpeg:dash:profile:list:2024 urn:svta:dash:sgai-list:2026"` (space-separated, Annex B §B.3) | Re-use of MPD@profiles attribute | MPD root | M | §5.3.1.2 and §8.14 describe `@profiles` as a "comma-separated list of profile identifiers". Spec's annex B uses **space-separated** in the example. Real-world DASH parsers commonly accept whitespace tokenisation, but the spec language is strict. Either re-format annex B as `profiles="urn:mpeg:dash:profile:list:2024,urn:svta:dash:sgai-list:2026"` or state the delimiter intent explicitly. |
| C-23 | Single-Period Static Profile per-form sub-MPD with exactly one Period, `MPD@type="static"`, no Xlink, no nested ImportedMPD, no Alternative MPD events | Re-use of SPS profile §8.15 | All per-ad / per-form sub-MPDs | V | §8.15 restrictions match the spec's §5.7 wording. |
| C-24 | Carrying a vendor namespace (e.g. `urn:qualabs:sgai:2026`) on per-form sub-MPD for VAST-equivalent metadata | Foreign namespace usage | Children of `<ImportedMPD>` or `<svta:Form>` | V | §5.2.1 open content model. Spec correctly defers metadata semantics to vendor namespaces (§5.9, §8.5). |
| C-25 | Period inside non-linear ListMPD with NO `<ImportedMPD>` direct child (ImportedMPD lives inside `<svta:Form>`) | Structural arrangement | Non-linear ListMPD Period | M | §8.14 permits both "Linked Periods" (with ImportedMPD) and "regular Periods". A non-linear Period with neither standard ImportedMPD nor any AdaptationSet is technically a "regular Period that yields nothing" to a legacy parser, which then falls through to no-fill (annex E §E.3). Schema-valid, but the spec should make this explicit: every non-linear Period is intentionally a regular Period whose ad payload is carried in foreign-namespace extension content. |
| C-26 | `@returnOffset` / `@clipDuration` / `@startWithOffset` on `<ReplacePresentation>` re-used per §5.16.4 | Baseline attributes, used as-is | On `<ReplacePresentation>` | V | §5.16.4 / §5.16.5 — spec's §5.3 wording matches the baseline behaviour. |
| C-27 | `<EventStream>` carrying SGAI slots in the Broadcaster's primary MPD | Re-use of baseline element | Child of Period in primary MPD | V | §5.10.1 placement; primary MPD is not constrained by ListMPD profile (which forbids Alternative MPD events on the ListMPD itself — irrelevant for the Broadcaster's primary MPD). |

## NotebookLM findings (highlights)

- **Q1 (§5.2.1 extension rules)**: confirmed by source. MPD, Period,
  AdaptationSet, and Event all carry `<xs:any namespace="##other"
  processContents="lax"/>` in MPDtype / PeriodType /
  AdaptationSetType / EventType. `<xs:anyAttribute>` wildcard is
  also pervasive. Ignore-if-unknown is normative.
- **Q2 (§5.10.1 / §5.10.3.3.1)**: confirmed. Unknown
  `Event@schemeIdUri` → DASH client "subscribes" only to known
  schemes, ignores unknown Event Streams; emsg with unknown scheme
  MUST be ignored.
- **Q3 (§8.14 ListMPD)**: confirmed. ListMPD strictly prohibits
  Alternative MPD events and XLink **within the ListMPD itself**.
  Period inside ListMPD may carry ImportedMPD AND EventStream AND
  ServiceDescription AND foreign-namespace children. MPD@profiles
  is a comma-separated list of profile identifiers; vendor URIs
  alongside ListMPD URI are explicitly permitted.
- **Q4 (§8.15 SPS mimeType)**: confirmed restrictive. SPS inherits
  §7.3 → IETF RFC 4337 → mimeType ∈ {`video/mp4`, `audio/mp4`,
  `application/mp4`}. Non-ISO-BMFF mimeTypes (`text/html`,
  `image/png`) are NOT permitted; must be wrapped in
  `application/mp4`.
- **Q5 (§5.16.3 / §5.16.4 / §5.16.5)**: confirmed. `@presentationTime`
  = single instant (window start). `Event@duration` =
  active "slot duration on main media timeline", not the
  alternative's playback duration. `@maxDuration` on
  AlternativeMPDEventType bounds the alternative's playback
  duration; Player MUST terminate exactly at this boundary if
  exceeded. `@maxDuration="0"` → event not executed at all.
- **Q6 (callback scheme)**: confirmed. `@presentationTime` =
  relative to Period start (of the sub-MPD's Period).
  EventStream-with-callback-scheme placement = **Period level
  only** (not MPD-level, not AdaptationSet-level). 0..N Event
  children. General-purpose by design but VAST-aligned by intent.
- **Q7 (§5.3.2.6 ImportedMPD)**: confirmed. Attribute is `@uri`
  (not `@url`); only other attribute is `@earliestResolutionTimeOffset`
  in seconds (default 60). **Placement: schema-defined as a child of
  PeriodType, exclusively.** Imported MPDs MUST conform to the SPS
  profile (§8.15) per §5.3.2.6.1.

## Non-conforming items detail

### N-1: SPS sub-MPD with `mimeType="text/html"` (C-20)

**Conflict**: §8.15 → §7.3 → IETF RFC 4337. The SPS profile
restricts Representation `@mimeType` to RFC-4337-registered
MPEG-4-system MIME types (`video/mp4`, `audio/mp4`,
`application/mp4`). Annex B §B.4 of the spec declares
`<AdaptationSet mimeType="text/html" contentType="application">`
for an HTML form sub-MPD. This violates SPS conformance, and the
spec's per-form sub-MPDs are explicitly required to be SPS-profile
(§5.7).

**Suggested fix**: package HTML payload as `application/mp4` (a
single-sample subtitle/metadata-style track carrying the HTML
asset as the sample data), and signal the HTML payload via
`@codecs` or a vendor-namespaced descriptor on the AdaptationSet.
Alternatively, drop SPS conformance for non-video forms and
introduce a new profile URI for "single-period non-BMFF asset"
sub-MPDs — but this is a much larger change and contradicts
chapter 5 §5.7.

### N-2: SPS sub-MPD with `mimeType="image/png"` (C-21)

**Conflict**: same as N-1. The spec's `mediaType="image"` form
class (§5.5) implies image MIME types on the sub-MPD AdaptationSet.
Annex B §B.4 prose says "swapping the `<AdaptationSet>` content for
`image/png`". `image/png` is not an SPS-permitted mimeType.

**Suggested fix**: same as N-1 — wrap the image asset in
`application/mp4` (single-sample track) and use vendor signalling
for the underlying asset format. Alternatively, decouple image
forms from the SPS sub-MPD model entirely (e.g. reference the
image via a direct URL inside the `<svta:Form>` element rather
than via `<ImportedMPD>` to a sub-MPD).

## Marginal items detail

### M-1: `<ImportedMPD>` inside `<svta:Form>`, not direct child of `<Period>` (C-08, C-25)

**Ambiguity**: §5.3.2.6 schema-pins `<ImportedMPD>` as a child of
PeriodType. The spec's non-linear ListMPD places `<ImportedMPD>`
two levels deep inside `<svta:CandidateForms>` / `<svta:Form>`. A
strict reading of the schema says this is foreign-namespace content
(opaque) that happens to *contain* an element named `ImportedMPD`
— but a legacy DASH parser does not descend into the foreign
subtree, so the nested `<ImportedMPD>` is invisible to it.
SGAI-aware Players need a normative statement that they MUST treat
this nested `<ImportedMPD>` with the same semantics as a
Period-direct-child `<ImportedMPD>`, including the
`@earliestResolutionTimeOffset` time base ("offset from
PeriodStart" — but PeriodStart of which Period? the enclosing
ListMPD Period, presumably).

**Suggested clarification**: in chapter 5 §5.6.2, add: "An
SGAI-aware Player MUST interpret an `<ImportedMPD>` element nested
within a `<svta:Form>` as if it were a direct child of the
enclosing `<Period>`, including the `@earliestResolutionTimeOffset`
semantics defined by §5.3.2.6.1."

### M-2: Callback `Event@presentationTime` time base in non-linear sub-MPDs (C-19)

**Ambiguity**: §5.10 measures `@presentationTime` from the sub-MPD's
PeriodStart. Spec §5.7 says non-linear tracking is "scheduled
against the parent slot's `@maxDuration` window". These are
consistent only if `Period@duration` of the per-form sub-MPD = the
Broadcaster-declared overlay window (not the form's intrinsic
asset duration). The spec does not pin this; annex B §B.4 shows
`Period @duration="PT20S"` and the slot is also 20 s, so it lines
up — but only coincidentally as the form's intrinsic asset
duration also happens to be 20 s. If the asset were 10 s and the
overlay window 20 s, the sub-MPD Period@duration is undefined by
the spec.

**Suggested clarification**: in §5.7, state: "For non-linear ads,
the per-form sub-MPD's `Period@duration` MUST equal the parent
slot's `@maxDuration` (the Broadcaster-declared overlay window),
regardless of the form's intrinsic asset duration. Tracking
`Event@presentationTime` values are then naturally aligned with
the overlay window per §5.10."

### M-3: `@earliestResolutionTimeOffset` unit collision (C-10)

**Ambiguity**: §5.3.2.6.1 Table 5 defines
`@earliestResolutionTimeOffset` in **seconds** as an attribute of
`<ImportedMPD>`. The spec's §5.3 declares an attribute of the same
name on the new svta slot elements (`<OverlayPresentation>`,
`<PauseAdPresentation>`, etc.) in **`EventStream@timescale`
units** (typically milliseconds). Same attribute name, different
type, different namespace, different unit. This is technically
schema-clean (different elements), but is a readability /
implementer-error hazard.

**Suggested clarification**: rename the svta attribute (e.g.
`svta:ertOffsetTicks`) OR explicitly call out the unit difference
in §5.3, e.g. add a row: "Note: this attribute on svta elements
uses `EventStream@timescale` units; on `<ImportedMPD>` (§5.3.2.6.1)
the same-named attribute is in seconds. Implementers MUST NOT mix
the two."

### M-4: `MPD@profiles` delimiter — space vs comma (C-22)

**Ambiguity**: §5.3.1.2 / §8.14 describe `@profiles` as a
"comma-separated list of profile identifiers". Spec annex B §B.3
and annex D §D.3 use **space-separated** values
(`profiles="urn:mpeg:dash:profile:list:2024 urn:svta:dash:sgai-list:2026"`).
Real-world parsers commonly tolerate whitespace, but a strict
DASH-6th parser may reject or mis-tokenise.

**Suggested clarification**: change all annex examples to
comma-separated (`profiles="urn:mpeg:dash:profile:list:2024,urn:svta:dash:sgai-list:2026"`)
to match the DASH language verbatim. No spec-text change needed.

## Open questions surfaced

- **OQ-1**: Spec references `urn:mpeg:dash:profile:advanced-linear:2025`
  in annex A §A.2 (`profiles="urn:mpeg:dash:profile:advanced-linear:2025"`
  on the Broadcaster's primary MPD). NotebookLM was not queried on
  whether this profile URI is defined by DASH-6th; the audit
  assumes it is a real DASH-6th profile but does not verify.
  Worth a follow-up query.
- **OQ-2**: Spec references `urn:mpeg:dash:schema:urlparam:2025` for
  `<up:UrlParamInfo>` in annex A §A.2. NotebookLM was not queried
  on the exact namespace and §I.4 wording. Assumed conforming;
  worth a verification query if the annex is to be normative.
- **OQ-3**: Whether the comma-vs-space delimiter on `@profiles` is
  actually strict in DASH-6th or whether the schema declares it as
  `xs:string` and real-world parsers tokenise on whitespace.
  NotebookLM gave the prose wording but the schema-level type is
  not verified.

## Summary

- **Total constructs audited**: 27
- **Conforming**: 21 (C-01..C-07, C-09, C-11..C-18, C-23, C-24, C-26, C-27)
- **Marginal**: 4 (C-08/C-25 = M-1, C-10 = M-3, C-19 = M-2, C-22 = M-4)
- **Non-conforming**: 2 (C-20 = N-1, C-21 = N-2 — both SPS-profile
  mimeType violations on HTML and image form sub-MPDs).

**Priority for the next spec iteration**: resolve N-1 / N-2
(SPS mimeType for non-video forms) before publication, as these
break the §5.7 SPS-conformance assertion of every non-video
per-form sub-MPD. M-1 and M-2 are also high-impact for SGAI-aware
Player implementers and should be promoted to a normative
clarification. M-3 and M-4 are editorial.

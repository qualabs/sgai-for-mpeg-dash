[GROUNDED_BY=notebooklm]

# SGAI for MPEG-DASH — Linear and Non-Linear Server-Guided Ad Insertion

**Edition**: 2026-05-12 (draft)

**Status**: Working draft prepared for SVTA Ads WG review.

**Conformance vocabulary**: The key words **MUST**, **MUST NOT**,
**SHOULD**, **SHOULD NOT**, **MAY**, **RECOMMENDED** in this document
are to be interpreted as described in **IETF RFC 2119** (Bradner,
1997). Lower-case usage of the same words has no special meaning.

This document is self-contained. A reader of this document does not
require access to any other working-group artefact to implement a
conformant Player, Broadcaster, or Ad Decision Server (ADS).

---

## Chapter 1 — Scope

This document specifies **Server-Guided Ad Insertion (SGAI)** for
MPEG-DASH, covering both **linear** ads (replacing or inserting into
the primary content timeline) and **non-linear** ads (composited on
top of, or alongside, the primary content while it plays).

This specification extends MPEG-DASH 6th edition (ISO/IEC 23009-1:2025):

- The linear SGAI primitives `InsertPresentation`,
  `ReplacePresentation`, `ListMPD`, and the callback event scheme
  `urn:mpeg:dash:event:callback:2015` are **absorbed as the linear
  baseline**, with the clarifications stated in chapters 4
  (Conformance), 5 (Syntax), 6 (Interfaces), and 7 (Expected
  behaviour) of this document.
- **Non-linear SGAI** is the principal new content. This document
  introduces the constructs that let a Broadcaster declare a
  non-linear ad opportunity, an ADS return multi-form / multi-layout
  ad candidates, and a Player select the highest-fidelity renderable
  form per device class and Broadcaster-declared policy.

This specification covers:

- Pre-roll, mid-roll, and multi-ad-break linear slots.
- Coexisting overlay, hybrid linear + overlay, and pause-triggered
  ads (the three foundational non-linear scenarios).
- A defined Player behaviour for each ad opportunity type on each
  of five device classes (D1 through D5; see chapter 3).
- A tracking semantics that reuses the linear DASH callback scheme
  for non-linear ads, with quartile anchors retargeted to the
  Broadcaster-declared overlay window.

This specification explicitly **does not** cover:

- Server-side ad insertion / stitching (SSAI / SSR).
- Post-roll slots (a future-phase candidate).
- Companion ads and multi-screen ad coordination.
- Menu Ads, In Scene Ads, and Screensaver Ads (informative entries
  in chapter 3 only; these fire outside the primary playback session
  or are composited into the content itself, and are not addressed
  by the SGAI machinery in this edition).
- The ADS's internal decisioning logic (targeting, frequency capping,
  brand safety, competitive separation, fill-rate considerations).
- DRM, content protection, codec negotiation, and CDN authentication
  (governed by orthogonal MPEG-DASH and DASH-IF guidelines).
- Spatial position semantics inside a layout (left vs right, exact
  pixel offsets) — delegated to HTML5 / CSS as the layout substrate
  (see chapter 4).

The intended audience is implementers of Players, Broadcaster
manifest authoring systems, and ADSs that produce ad candidates
against this specification.

---

## Chapter 2 — Normative references

The following documents are referenced normatively. Implementations
conforming to this specification MUST comply with the cited editions or
later (where the later edition preserves the cited semantics).

- **ISO/IEC 23009-1:2025(E)** — *Information technology — Dynamic
  adaptive streaming over HTTP (DASH) — Part 1: Media presentation
  description and segment formats*, 6th edition (FDIS / Final Draft
  International Standard). Referenced sections: §4.7, §5.2.1, §5.10
  (event framework, callback events), §5.16 (Alternative MPD events
  including `InsertPresentation` §5.16.3 and `ReplacePresentation`
  §5.16.4 / §5.16.5), §8.14 (ListMPD profile), §8.15 (Single-Period
  Static Profile), §I.4 (Extended HTTP GET parametrisation).
- **IETF RFC 2119** — *Key words for use in RFCs to Indicate
  Requirement Levels* (Bradner, March 1997).
- **IETF RFC 8174** — *Ambiguity of Uppercase vs Lowercase in RFC
  2119 Key Words* (Leiba, May 2017).
- **IAB Tech Lab — Ad Format Guidelines for Digital Video and CTV**,
  Final Release May 2026. Live, non-snapshotted reference:
  https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e
  The ad-type names and their canonical visual templates listed in
  chapter 3 of this specification are sourced from this document and are
  authoritative as of the IAB document's current revision.
- **W3C HTML Living Standard** and **W3C CSS Specifications** —
  Whichever revisions are supported by the target Player runtime.
  Overlay spatial placement is delegated to HTML5 / CSS layout
  primitives.

Informative references (do not bind conformance):

- **IETF RFC 3986** — *Uniform Resource Identifier (URI)*.
- **IAB Tech Lab Video Ad Serving Template (VAST) 4.x** — Used
  illustratively in annex A only. **This specification has no normative
  dependency on any VAST version** (see Chapter 4 §4.4).

---

## Chapter 3 — Terms, definitions, abbreviations

For the purposes of this document, the following terms and
definitions apply.

### 3.1 Core terms

- **Ad Decision Server (ADS)** — server that returns the ad
  candidates eligible for a given slot. Owns targeting, frequency
  capping, brand safety filtering, competitive separation, ordering,
  and fill-rate logic. **Not** responsible for enforcing Broadcaster-
  declared slot constraints.
- **Ad slot** — opportunity declared by the Broadcaster in the
  primary content's MPD where an ad may be rendered. Has a type
  (linear / non-linear) and a Broadcaster-declared maximum duration.
- **Broadcaster** — entity that owns the primary content and the
  viewer's screen. Declares ad slots in the primary MPD and the
  constraints (allowed layouts, duration cap, concurrency cap)
  applicable to each.
- **Candidate** — single ad returned by the ADS as eligible for a
  slot. A candidate carries one or more renderable forms.
- **Form** — a single renderable rendition of a candidate. A
  candidate's forms typically include some subset of video, image,
  and HTML.
- **Layout** — spatial template a non-linear form is composited into.
  The accepted layout vocabulary is sourced from the IAB document
  cited in chapter 2; see §3.3 below for the normative list of
  accepted ad-type values for this edition.
- **Linear ad** — ad whose form replaces the primary content for the
  duration of a slot. Pre-roll, mid-roll, and break ads are linear.
- **Non-linear ad** — ad whose form is composited alongside or on
  top of the primary content. Coexisting overlay, hybrid linear +
  overlay, and pause-triggered ads are non-linear.
- **Player** — client-side entity that reads the MPD, queries the
  ADS, validates the candidates against Broadcaster-declared
  constraints, selects the form to render, and composes the ad on
  screen. The Player is the **enforcer** of the Broadcaster's
  policy.
- **Resolution document** — XML document returned by the ADS in
  response to the Player's resolution request. For linear slots,
  this is a `ListMPD` (see Chapter 5 §5.4). For non-linear slots,
  this is a `ListMPD` carrying candidate-set metadata per Period
  (see Chapter 5 §5.5).
- **Slot constraint** — single attribute on a slot that the Player
  MUST validate ADS-returned candidates against (max duration,
  allowed layouts, concurrency cap).
- **Tracking beacon** — fire-and-forget HTTP GET that the Player
  emits at specified instants of an ad's playback (impression,
  start, quartile boundaries, complete). Carried via the callback
  event scheme `urn:mpeg:dash:event:callback:2015`.

### 3.2 Device classes

This specification enumerates five device classes that capture the rendering
capabilities relevant to non-linear ad composition. Codec support,
DRM, and network conditions are orthogonal to this enumeration and
are not addressed by the device class.

| Class | Video decoders | Image overlay | HTML overlay | Video-on-video overlay |
|-------|---------------|---------------|--------------|------------------------|
| D1 | 2 or more | yes | yes | yes |
| D2 | 2 | no | no | yes |
| D3 | 1 | yes | yes | no |
| D4 | 1 | yes | no | no |
| D5 | 1 | no | no | no |

D1 is the top-tier class; D5 is the worst-case class. A conformant
Player MUST identify the device's class according to this table and
follow the per-class expected behaviour defined in chapter 7 for
each ad opportunity type.

### 3.3 Accepted ad-type values

The accepted ad-type values for this edition of the specification are sourced
from the IAB document cited in chapter 2. The specification itself does not
introduce ad-type values beyond what the IAB document publishes;
Broadcasters declaring allowed layouts in the MPD MUST use names
that map 1:1 to entries in the IAB catalogue.

For this edition, the following IAB ad-type values are recognised in
the slot's `@allowedLayouts` attribute (Chapter 5 §5.3):

| Ad-type identifier | IAB ad-type | Addressed by this edition |
|--------------------|-------------|---------------------------|
| `linear-ad` | Linear Ad | yes (Chapter 5 §5.4) |
| `pause-ad` | Pause Ad | yes (Chapter 5 §5.5, Chapter 7 §7.4) |
| `overlay` | Overlay (Corner, Lower-Third) | yes (Chapter 5 §5.5, Chapter 7 §7.2) |
| `squeezeback` | Squeezeback (L-Shape, Frame, Double-Box, Double-Box + Background) | yes (Chapter 5 §5.5, Chapter 7 §7.2) |
| `menu-ad` | Menu Ad | informative; not addressed at runtime in this edition |
| `in-scene-ad` | In Scene Ads | informative; not addressed at runtime in this edition |
| `screensaver-ad` | Screensaver Ad | informative; not addressed at runtime in this edition |

For overlay-style ad types whose visual templates have multiple
sub-positions (e.g. Corner Overlay vs Lower-Third Overlay for
`overlay`; L-Shape vs Frame vs Double-Box vs Double-Box + Background
for `squeezeback`), Broadcasters MUST express the admissible
sub-positions on the `@allowedLayouts` attribute using the IAB
canonical sub-position names verbatim: `corner-overlay`,
`lower-third-overlay`, `l-shape`, `frame`, `double-box`,
`double-box-background`. Sub-position lists are comma-separated.

### 3.4 Abbreviations

- **ABR** — Adaptive Bitrate.
- **ADS** — Ad Decision Server.
- **CDN** — Content Delivery Network.
- **CMAF** — Common Media Application Format.
- **DASH** — Dynamic Adaptive Streaming over HTTP.
- **ERT** — Earliest Resolution Time (the earliest instant at which
  a Player MAY resolve a slot's ADS URL).
- **HLS** — HTTP Live Streaming.
- **IAB** — Interactive Advertising Bureau.
- **MPD** — Media Presentation Description (the DASH manifest).
- **OTT** — Over-the-top.
- **SGAI** — Server-Guided Ad Insertion.
- **SPS** — Single-Period Static Profile (DASH §8.15).
- **SVTA** — Streaming Video Technology Alliance.
- **VAST** — Video Ad Serving Template (IAB Tech Lab).

---

## Chapter 4 — Conformance

A conformant implementation of this specification MUST satisfy all the
obligations stated in §4.1 (Broadcaster), §4.2 (ADS), and §4.3
(Player) appropriate to its role. §4.4 lists cross-cutting
obligations that bind any actor that authors normative material
against this specification (in practice, the spec author).

### 4.1 Broadcaster conformance

A conformant Broadcaster MUST satisfy the following:

- **B-01**: Declare every ad slot in the primary MPD as an `<Event>`
  child of an `<EventStream>` whose `@schemeIdUri` carries one of
  the year-pinned URIs introduced by this specification (see Chapter 5 §5.2)
  or the linear baseline URIs inherited from MPEG-DASH 6th edition
  (§5.16).
- **B-02**: On every ad slot (linear or non-linear), declare the
  maximum duration the slot may occupy (the `@maxDuration`
  attribute, in `EventStream@timescale` units). The Broadcaster
  MUST declare this attribute on every slot; the absence of
  `@maxDuration` on a slot defined by this specification is non-conforming.
- **B-03**: For non-linear ad slots, declare the admissible layouts
  on the `@allowedLayouts` attribute using only the IAB ad-type
  names listed in §3.3. Layout names outside that set are
  non-conforming.
- **B-04**: For non-linear ad slots, declare the maximum number of
  concurrent rendered candidates on the `@maxConcurrency` attribute.
  Defaults to `1` if absent (interpreted as "one overlay at a time").
- **B-05**: Express every new SGAI construct via an MPEG-DASH 6th
  edition extension point whose ignore-if-unknown semantics are
  already defined: open content model on known parents (§5.2.1),
  unknown attribute rule on known elements (§5.2.1), unknown
  `Event@schemeIdUri` rule (§5.10.1 / §5.10.3.3.1). A Broadcaster
  MUST NOT place a new mandatory element in a position whose legacy
  schema declares the position as a required field with no
  extension hook.

### 4.2 ADS conformance

A conformant ADS MUST satisfy the following:

- **A-01**: In response to a Player's resolution request for a slot,
  return one of: (a) a `ListMPD` body (see Chapter 5 §5.4 for
  linear slots, §5.5 for non-linear slots); (b) an empty `ListMPD`
  (canonical no-fill signal); (c) an HTTP error status. The ADS
  MUST NOT return any other body shape; in particular, a 4xx status
  MUST NOT be used to signal soft no-fill (use an empty `ListMPD`
  instead).
- **A-02**: Carry, in each `<Period>` of a non-linear `ListMPD`
  response, the candidate's full set of renderable forms and
  admissible layouts. A candidate offering only one form is
  acceptable; a candidate offering zero forms is non-conforming.
- **A-03**: The ADS is NOT required to enforce the Broadcaster's
  `@maxDuration` cap. A conformance check on the ADS MUST NOT fail
  solely because the cumulative duration of its returned candidates
  exceeds the cap declared on the slot.
- **A-04**: The ADS is NOT required to maintain a device-class
  matrix or a per-Player capability view. Candidates returned by
  the ADS are device-agnostic; per-device fitness is the Player's
  determination.
- **A-05**: The ADS MUST emit candidate form-and-layout metadata
  using only the IAB ad-type names accepted for this edition
  (Chapter 3 §3.3).
- **A-06**: The ADS MUST NOT depend on any specific VAST version
  for its contract with the Player. The Player ↔ ADS wire is
  `ListMPD`; the ADS's upstream protocol (VAST, OpenRTB, proprietary)
  is the ADS's internal concern, opaque to the Player.

### 4.3 Player conformance

A conformant Player MUST satisfy the following:

- **P-01**: For every ad opportunity type defined in this specification,
  produce a defined behaviour on every device class D1..D5
  (render, fall back to a lower-fidelity form, or skip). Undefined
  behaviour is non-conforming.
- **P-02**: Validate every ADS-returned candidate against the
  Broadcaster-declared slot constraints (max duration, allowed
  layouts, concurrency cap). Candidates that violate any constraint
  MUST be discarded; only validated candidates MAY be rendered.
- **P-03**: For a candidate that passes validation, choose the form
  to render by intersecting (a) the device's rendering capabilities
  (Chapter 3 §3.2), (b) the slot's `@allowedLayouts` (B-03), and
  (c) the ADS-supplied priority hints (Chapter 5 §5.5). A form /
  layout combination that fails any one of the three MUST NOT be
  rendered.
- **P-04**: If no form / layout combination on the highest-ranked
  candidate satisfies P-03, skip the candidate and evaluate the
  next one in ADS-declared order. If no candidate is renderable on
  the device, decline the slot and continue the primary content
  uninterrupted ("skip is a valid outcome, not a failure").
- **P-05**: Enforce the Broadcaster-declared `@maxDuration` on every
  ad slot. If the cumulative duration of accepted candidates would
  exceed the cap, the Player MUST stop rendering at the cap
  boundary, even if the stop falls mid-ad. The cap MUST be enforced
  against the **actual rendered length** of accepted candidates,
  not against their declared length. The Player MUST NOT extend a
  slot beyond the cap, regardless of ADS metadata or candidate
  count.
- **P-06**: Play the candidates that pass P-02 / P-03 in the order
  declared by the ADS, except for candidates dropped under P-04 or
  P-05's drop-before-play (a candidate whose declared duration
  would push the cumulative slot duration past the cap MAY be
  dropped before playback). After applying drops, the Player MUST
  NOT re-order, deduplicate, or otherwise rearrange the remaining
  candidates.
- **P-07**: Fire tracking beacons declared in the ad MPD or sub-MPD
  via the callback event scheme `urn:mpeg:dash:event:callback:2015`
  (Chapter 5 §5.6). Beacon emission is fire-and-forget; the Player
  MUST NOT alter playback based on beacon HTTP status. The Player
  MUST safely ignore unknown XML namespaces on tracking-related
  extension elements.
- **P-08** (non-linear specific): For a non-linear ad accepted for
  rendering, the Player MUST fire an impression beacon at the
  instant the overlay becomes visible to the user. The Player
  SHOULD fire quartile beacons timed against the Broadcaster-
  declared overlay window (P-05's `@maxDuration`), not against the
  ad form's intrinsic duration. If the overlay is trimmed under
  P-05 before all quartiles fire, the Player MUST stop firing
  beacons at the trim boundary.
- **P-09**: A legacy Player that does not implement an SGAI
  construct introduced by this specification MUST ignore the unknown
  construct and continue playing the primary content uninterrupted.
  (This obligation is satisfied by the Broadcaster's B-05; the
  Player obligation is to honour MPEG-DASH 6th edition's
  ignore-if-unknown rules without modification.)
- **P-10**: The Player MUST be able to operate against an ADS
  whose upstream protocol does not include VAST. The Player ↔ ADS
  contract is `ListMPD`; VAST is not a precondition on the Player
  side.

### 4.4 Cross-cutting obligations (spec-document level)

- **D-01**: This specification MUST NOT alter or override the semantics of
  any pre-existing MPEG-DASH 6th edition construct.
- **D-02**: This specification MUST NOT introduce a new tracking event
  scheme. Tracking for both linear and non-linear ads reuses the
  callback event scheme `urn:mpeg:dash:event:callback:2015` defined
  in MPEG-DASH 6th edition.
- **D-03**: The list of accepted ad-type values (Chapter 3 §3.3)
  MUST be sourced from the IAB document cited in chapter 2.
  Introducing new ad-type names at spec level is out of scope; that
  authority is held by the IAB.
- **D-04**: Spatial arrangement of overlays MUST be delegated to
  HTML5 / CSS layout primitives. This specification does not define a
  parallel layout standard. Position semantics inside a layout
  (left vs right corner, exact offsets) are expressed via the
  HTML5 / CSS layer.
- **D-05**: The normative chapters (4 through 7) of this specification MUST
  NOT cite a specific VAST version as required. References to VAST
  appear only in informative annexes flagged as illustrative.

---

## Chapter 5 — Syntax

This chapter specifies the manifest constructs introduced by this
specification. The linear baseline constructs (`InsertPresentation`,
`ReplacePresentation`, the `ListMPD` profile and `ImportedMPD`
element, the callback event scheme) are inherited from MPEG-DASH 6th
edition and are described here only insofar as the SGAI specification
constrains or clarifies their usage. Non-linear constructs
(`OverlayPresentation`, `PauseAdPresentation`, the candidate-set
metadata on `<Period>` entries inside a non-linear `ListMPD`) are
new.

### 5.1 Document tree overview

The Broadcaster's primary MPD carries one or more `<EventStream>`
elements declaring SGAI slots; each `<Event>` inside an
`<EventStream>` carries the slot's parameters in a child element
whose tag depends on the slot type:

- `<InsertPresentation>` — linear, insertion-style slot (pre-roll,
  break inserted into the timeline).
- `<ReplacePresentation>` — linear, replacement-style slot (mid-roll
  on a live timeline).
- `<OverlayPresentation>` — non-linear, coexisting-overlay slot
  (UC-03 type).
- `<PauseAdPresentation>` — non-linear, pause-triggered slot
  (UC-05 type) carrying a window of validity for pause behaviour.

The ADS returns a `ListMPD` resolution document; each `<Period>` in
the `ListMPD` either:

- imports an external per-ad sub-MPD via `<ImportedMPD>` (the linear
  pattern), or
- imports per-form sub-MPDs and carries candidate-set metadata via
  a `<CandidateForms>` extension element (the non-linear pattern).

The per-ad / per-form sub-MPDs use the MPEG-DASH Single-Period Static
Profile (`urn:mpeg:dash:profile:sps:2024`, §8.15) and carry tracking
beacons inside an `<EventStream>` of scheme
`urn:mpeg:dash:event:callback:2015`.

### 5.2 Scheme URIs introduced by this edition

The specification introduces three event scheme URIs under the SVTA Ads WG
namespace. The year suffix pins the edition.

| Scheme URI | Purpose | Carrying element |
|------------|---------|------------------|
| `urn:svta:dash:sgai-overlay:2026` | Non-linear coexisting overlay slot | `<OverlayPresentation>` |
| `urn:svta:dash:sgai-pause-trigger:2026` | Non-linear pause-triggered slot | `<PauseAdPresentation>` |
| `urn:svta:dash:sgai-list:2026` | Resolution document profile carrying candidate-set metadata for non-linear slots | `MPD@profiles` on a non-linear `ListMPD` (additional to `urn:mpeg:dash:profile:list:2024`) |

The linear baseline schemes from MPEG-DASH 6th edition are reused
verbatim and are NOT re-versioned by this edition:

- `urn:mpeg:dash:event:alternativeMPD:insert:2025` —
  `<InsertPresentation>`.
- `urn:mpeg:dash:event:alternativeMPD:replace:2025` —
  `<ReplacePresentation>`.
- `urn:mpeg:dash:profile:list:2024` — `ListMPD` profile.
- `urn:mpeg:dash:profile:sps:2024` — Single-Period Static Profile.
- `urn:mpeg:dash:event:callback:2015` — tracking callback events.

The XML namespace for new elements and attributes introduced by this
specification is:

  `urn:svta:dash:sgai:2026`

referred to throughout this document by the prefix `svta:`.

### 5.3 Attributes common to all SGAI slot child elements

The four slot child elements (`<InsertPresentation>`,
`<ReplacePresentation>`, `<OverlayPresentation>`,
`<PauseAdPresentation>`) share a common set of attributes inherited
from the MPEG-DASH 6th edition baseline plus extensions introduced
by this specification.

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@url` (alias `@uri` in XML schema) | yes | URI | — | URL the Player resolves against the ADS for this slot. Must remain constant across MPD updates. |
| `@maxDuration` | yes | xs:unsignedInt (in `EventStream@timescale` units) | — | Maximum cumulative rendered duration of the slot. The Player enforces the cap per P-05. |
| `@earliestResolutionTimeOffset` | no | xs:unsignedInt (units) | 60 (DASH 6th default for §5.16) | Time window before the slot's `presentationTime` during which the Player MAY resolve the ADS URL. |
| `@allowedLayouts` | yes (on non-linear); ignored (on linear) | xs:string (comma-separated list of IAB layout names from §3.3) | — | Admissible layouts for this slot. Applies to `<OverlayPresentation>` and `<PauseAdPresentation>`. On linear slots, omit. |
| `@maxConcurrency` | no | xs:unsignedInt | 1 | Maximum number of concurrently rendered candidates on this slot. Applies to `<OverlayPresentation>` only; ignored on others. |

Additional attributes specific to `<ReplacePresentation>` (inherited
from MPEG-DASH 6th edition §5.16.4):

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@returnOffset` | no | xs:unsignedInt (units) | playhead at alternative-end | Time offset from the event's `presentationTime` at which the main presentation resumes after the ad. |
| `@clipDuration` (XML alias `@clip`) | no | xs:boolean | true | If true, alternative presentation must terminate no later than `presentationTime + @maxDuration` (regardless of execution delay). If false, terminates at `actualExecutionTime + @maxDuration`. |
| `@startWithOffset` | no | xs:boolean | false | If true and alternative execution is delayed past `presentationTime`, the Player skips into the ad by the delay amount, keeping wall-clock alignment. Inapplicable when `@clipDuration` is false. |

Additional attributes specific to `<PauseAdPresentation>`:

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@windowStart` | yes | xs:unsignedInt (in `EventStream@timescale` units, relative to `Period@start`) | — | Start of the validity window during which a pause by the user permits an overlay ad. |
| `@windowEnd` | yes | xs:unsignedInt (same units) | — | End of the validity window. A pause outside `[@windowStart, @windowEnd]` does not trigger an overlay. |
| `@allowVideoForm` | no | xs:boolean | false | If true, the Player MAY render a video form on top of the paused frame on devices that can re-task the primary decoder. If false (the default), the Player MUST skip video forms in this scenario. |

### 5.4 Linear slots — `<InsertPresentation>` and `<ReplacePresentation>`

These elements are inherited from MPEG-DASH 6th edition §5.16.3 /
§5.16.4 without semantic change. They appear as child elements of an
`<Event>` whose parent `<EventStream>` carries
`@schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"` or
`@schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"`
respectively.

Behaviour:

- `<InsertPresentation>` pauses the main timeline at
  `Event@presentationTime`; the alternative presentation plays; when
  it ends, the main timeline resumes from where it paused.
- `<ReplacePresentation>` does not pause the main timeline; main
  media time continues to advance in the background while the
  alternative plays; when it ends, main playback resumes at the
  position determined by `@returnOffset` (or the natural playhead
  position if `@returnOffset` is absent).

Resolution document: the ADS responds with a `ListMPD` (§5.4 of
this chapter, or the linear-baseline ListMPD pattern described in
this section) whose Periods reference per-ad sub-MPDs via
`<ImportedMPD>` (§5.5 below).

Short inline example (full MPDs are in annex A):

```xml
<EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
             timescale="1000">
  <Event id="101" presentationTime="0" duration="15000">
    <InsertPresentation url="https://ads.example.com/decision/preroll"
                        earliestResolutionTimeOffset="0"
                        maxDuration="15000"/>
  </Event>
</EventStream>
```

### 5.5 Non-linear slots — `<OverlayPresentation>` and `<PauseAdPresentation>`

These elements are new in this specification and live in the `svta:` namespace
declared in §5.2.

`<OverlayPresentation>` declares a coexisting-overlay slot. The
primary content continues to play; an overlay is composited over it
for at most `@maxDuration` units. The element appears as a child of
an `<Event>` whose parent `<EventStream>` carries
`@schemeIdUri="urn:svta:dash:sgai-overlay:2026"`.

`<PauseAdPresentation>` declares a pause-triggered slot. Inside the
window `[@windowStart, @windowEnd]`, if the user pauses playback, the
Player MAY render an overlay on top of the paused frame. Outside that
window, a pause does not trigger an overlay. The element appears as a
child of an `<Event>` whose parent `<EventStream>` carries
`@schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026"`.

Both elements use the attributes defined in §5.3. The
`@allowedLayouts` attribute on these elements MUST carry only the IAB
layout names listed in §3.3 (e.g.
`@allowedLayouts="corner-overlay,lower-third-overlay"` for an
overlay slot that admits two sub-positions).

Short inline example (the full MPDs and ListMPDs are in annex B):

```xml
<EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
             timescale="1000">
  <Event id="201" presentationTime="120000" duration="20000">
    <svta:OverlayPresentation url="https://ads.example.com/decision/overlay"
                              maxDuration="20000"
                              allowedLayouts="corner-overlay,lower-third-overlay,l-shape"
                              maxConcurrency="1"
                              earliestResolutionTimeOffset="10000"/>
  </Event>
</EventStream>
```

### 5.6 Resolution document — `ListMPD` shape for SGAI

Both linear and non-linear slots use the MPEG-DASH 6th edition
`ListMPD` profile (`urn:mpeg:dash:profile:list:2024`, §8.14) as the
top-level container of the resolution document. The Player evaluates
the `ListMPD` Periods in declared order.

#### 5.6.1 Linear `ListMPD`

Each `<Period>` carries one `<ImportedMPD>` linking to a per-ad
sub-MPD that MUST be constrained to the Single-Period Static Profile
(`urn:mpeg:dash:profile:sps:2024`, §8.15) per the DASH 6th edition
requirement on `ImportedMPD` links.

`<ImportedMPD>` attributes (inherited from MPEG-DASH 6th edition
§5.3.2.6.1):

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@uri` | yes | URI | — | URI of the imported per-ad sub-MPD. |
| `@earliestResolutionTimeOffset` | no | xs:unsignedInt (seconds, default 60) | 60 | Offset in seconds from the parent Period's start at which the Player MAY issue the request for the imported sub-MPD. Inherited from §5.3.2.6.1 (Table 5). |

The cumulative Period duration is bounded by the slot's
`@maxDuration` from the parent `<InsertPresentation>` /
`<ReplacePresentation>`; the Player trims at the cap per P-05.

#### 5.6.2 Non-linear `ListMPD`

The `MPD@profiles` attribute carries both
`urn:mpeg:dash:profile:list:2024` (the base ListMPD profile) and
`urn:svta:dash:sgai-list:2026` (this specification's candidate-set profile).
Each `<Period>` represents a single ad candidate. The candidate's
forms are carried in a `<svta:CandidateForms>` child element, with
one `<svta:Form>` per renderable form.

`<svta:CandidateForms>` attributes:

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@candidateId` | yes | xs:string | — | Stable identifier for the candidate inside the resolution document. |
| `@candidatePriority` | no | xs:unsignedInt | 100 | ADS-supplied priority hint across candidates. Higher value = higher priority. The Player MAY use this to rank candidates; it is a hint, not an obligation. |

`<svta:Form>` attributes:

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@formId` | yes | xs:string | — | Stable identifier for the form inside the candidate. |
| `@mediaType` | yes | xs:string (enum) | — | Form's media class. Enum below. |
| `@admissibleLayouts` | yes | xs:string (comma-separated list of IAB layout names) | — | Layouts on which this form may render. MUST be a subset of the slot's `@allowedLayouts`. |
| `@formPriority` | no | xs:unsignedInt | 100 | ADS-supplied priority hint among forms in this candidate. Higher value = higher priority. |
| `@duration` | yes | xs:unsignedInt (in `EventStream@timescale` units of the parent slot) | — | Form's intrinsic duration. Used by the Player for drop-before-play (P-06) and as the upper bound for the rendered length subject to P-05. |

`@mediaType` enum:

| Enum value | Description |
|------------|-------------|
| `video` | Form is a video rendition. Requires device capability for video-on-video composition (D1 / D2) or single-decoder retasking (D3, only in `<PauseAdPresentation>` with `@allowVideoForm="true"`). |
| `image` | Form is a static image rendition. Requires image overlay capability (D1 / D3 / D4). |
| `html` | Form is an HTML / DOM rendition. Requires HTML overlay capability (D1 / D3). |

Each `<svta:Form>` element contains exactly one `<ImportedMPD>`
child linking to the per-form sub-MPD (constrained to SPS per
§5.5.1 above).

Short inline example (full ListMPDs in annex B and C):

```xml
<Period id="cand-1" duration="PT20S">
  <svta:CandidateForms candidateId="cand-1" candidatePriority="80">
    <svta:Form formId="cand-1-html" mediaType="html"
               admissibleLayouts="corner-overlay,lower-third-overlay"
               formPriority="100" duration="20000">
      <ImportedMPD uri="creatives/cand-1-html.mpd"/>
    </svta:Form>
    <svta:Form formId="cand-1-image" mediaType="image"
               admissibleLayouts="corner-overlay"
               formPriority="50" duration="20000">
      <ImportedMPD uri="creatives/cand-1-image.mpd"/>
    </svta:Form>
  </svta:CandidateForms>
</Period>
```

### 5.7 Per-form / per-ad sub-MPD — Single-Period Static Profile

Sub-MPDs reached by `<ImportedMPD>` MUST conform to the Single-Period
Static Profile (`urn:mpeg:dash:profile:sps:2024`, §8.15):

- Exactly one `<Period>` element. `Period@duration` is mandatory.
- `MPD@type` is `static`.
- No `<Xlink>` references; no Alternative MPD events; no nested
  `<ImportedMPD>` (sub-MPDs are leaves).

The sub-MPD carries the media (`<AdaptationSet>` /
`<Representation>` / `<SegmentBase>` or `<SegmentTemplate>`) plus a
tracking `<EventStream>` of scheme
`urn:mpeg:dash:event:callback:2015` whose `<Event>` entries declare
the beacons to fire at given offsets within the form.

For non-linear ads, the tracking `<Event>` `@presentationTime`
values are scheduled against the **parent slot's `@maxDuration`
window** (the Broadcaster-declared overlay window), not against the
form's intrinsic `@duration`. The Player follows P-07 / P-08 for
emission.

### 5.8 Tracking — callback event scheme

This specification does NOT introduce a new tracking scheme. Both linear and
non-linear ads carry tracking beacons via the callback event scheme
`urn:mpeg:dash:event:callback:2015` inherited from MPEG-DASH 6th
edition (§4.7 / §5.10.4.5).

`<EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015">`
inside a per-ad / per-form sub-MPD carries one `<Event>` per beacon.
Each `<Event>` has:

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@id` | yes | xs:string | — | Identifier of the beacon (stable per sub-MPD). |
| `@presentationTime` | yes | xs:unsignedInt (in `EventStream@timescale` units) | — | Offset within the slot's window at which the Player fires the beacon. For linear: offset within the candidate's intrinsic duration. For non-linear: offset within the Broadcaster-declared overlay window. |

The `<Event>`'s text content is the beacon URL. The Player fires an
HTTP GET to that URL at the scheduled `@presentationTime`, treats
the response body as an opaque ack, and discards it.

Quartile naming conventions (impression at offset 0, then quartiles
at 25 / 50 / 75 / 100 % of the relevant window, then complete) are
informative; the Player MUST fire whatever `<Event>` entries the
sub-MPD declares, at the times the sub-MPD schedules them, subject
to P-07 and P-08.

### 5.9 Application-level metadata (VAST equivalents)

VAST application-level metadata (`ClickThrough`, `AdSystem`,
`AdTitle`, `UniversalAdId`) has no native MPEG-DASH carrier. This
specification does not introduce one. Implementations that need to carry such
metadata SHOULD use vendor-namespaced extension elements alongside
the per-form sub-MPD; the Player MUST safely ignore unknown
namespaces (P-07).

Recommended carrier: a vendor-namespaced element under
`urn:qualabs:sgai:2026` (Qualabs vendor namespace) or any equivalent
vendor URN. The specification does not pin the vendor namespace because
multiple vendors will coexist; the Player's obligation is uniform
across vendor namespaces (ignore-if-unknown).

### 5.10 Backward-compat audit table

Every new construct introduced in this chapter passes the per-
construct backward-compat checks listed below. A FAIL in any column
blocks publication.

| Construct | Placement | Extension rule | Walk-through | Sibling check | Legacy-Player test | Namespace | Status |
|-----------|-----------|----------------|--------------|---------------|--------------------|-----------|--------|
| `<svta:OverlayPresentation>` (child of `<Event>`) | Inside `<Event>` inside `<EventStream>` | Unknown `Event@schemeIdUri` rule (§5.10.1 / §5.10.3.3.1) — legacy Player ignores entire `<EventStream>` | Parser sees `<EventStream>` with unknown scheme → subscription model skips → primary continues | No required sibling on `<Event>` impacted | annex E test case T-E1 | `urn:svta:dash:sgai:2026` | OK |
| `<svta:PauseAdPresentation>` (child of `<Event>`) | Same as above | Same as above | Same as above | Same | annex E test case T-E2 | `urn:svta:dash:sgai:2026` | OK |
| `<svta:CandidateForms>` (child of `<Period>`) | Inside `<Period>` inside `<MPD>` (in a `ListMPD`) | Open content model on `<Period>` (§5.2.1, `<xs:any namespace="##other" processContents="lax"/>`) | Parser sees unknown element inside `<Period>` → skips per open content model → remaining `<Period>` parses normally → legacy `<ImportedMPD>` if present is used; otherwise Period yields no ad → slot is no-fill | `<Period>` has no required sibling impacted | annex E test case T-E3 | `urn:svta:dash:sgai:2026` | OK |
| `<svta:Form>` (child of `<svta:CandidateForms>`) | Inside `<svta:CandidateForms>` | Same as above (entire ancestor is unknown to legacy) | Same as above | n/a (whole ancestor is unknown to legacy) | annex E test case T-E3 | `urn:svta:dash:sgai:2026` | OK |
| `@windowStart` / `@windowEnd` on `<svta:PauseAdPresentation>` | XML attributes on a new element | Unknown attribute rule on a known element does not apply (whole element is new) | Legacy Player never reaches these attributes (parent unknown by R1) | n/a | annex E test case T-E2 | `urn:svta:dash:sgai:2026` | OK |
| `@allowedLayouts`, `@maxConcurrency`, `@allowVideoForm` on new elements | XML attributes on new elements | Same as above | Same as above | n/a | covered by annex E test cases T-E1, T-E2 | `urn:svta:dash:sgai:2026` | OK |

---

## Chapter 6 — Interfaces

This chapter specifies the Broadcaster ↔ ADS ↔ Player message flows
and the transports / payload shapes that bind them. Linear baseline
flows are inherited from MPEG-DASH 6th edition with the
clarifications stated in §6.2. Non-linear extensions are new
(§6.3).

### 6.1 Component inventory

| Actor | Emits | Consumes |
|-------|-------|----------|
| Broadcaster | Primary MPD with SGAI `<EventStream>` elements; primary content segments via CDN | Nothing at runtime (authoring-time only) |
| Player | MPD fetch request; ADS resolution request at slot activation; tracking beacons (HTTP GET) | Primary MPD; `ListMPD` from ADS; per-form / per-ad sub-MPDs from ADS or ad CDN; ad segments from ad CDN |
| ADS | `ListMPD` (linear or non-linear shape per Chapter 5 §5.4 / §5.5) | Player's resolution request; (internal) upstream ad decisioning |

### 6.2 Linear flow

Once the Player has fetched the primary MPD and is playing primary
content, the linear SGAI flow is timeline-triggered:

1. The Broadcaster's MPD declares one or more `<Event>` elements
   inside `<EventStream>` elements scoped to the linear SGAI
   schemes. Each `<Event>` carries `<InsertPresentation>` or
   `<ReplacePresentation>` as a child.
2. As the playhead approaches an event's
   `Event@presentationTime − @earliestResolutionTimeOffset` (the
   Earliest Resolution Time, ERT), the Player picks a randomised
   instant between the ERT and `Event@presentationTime` and issues
   an HTTP GET to the slot's `@url`, augmented with any query
   parameters declared by an MPD-level `UrlParamInfo` descriptor
   (§I.4 of MPEG-DASH 6th edition).
3. The ADS replies with a `ListMPD` body (Chapter 5 §5.6.1). Each
   `<Period>` of the `ListMPD` references a per-ad sub-MPD via
   `<ImportedMPD>`.
4. The Player fetches each sub-MPD from its `<ImportedMPD>` `@uri`,
   then fetches the ad segments from the ad CDN.
5. The Player validates each candidate against the slot's
   `@maxDuration` (P-02) and renders the validated candidates in
   ADS-declared order, enforcing the cap per P-05 (drop-before-play
   on declared duration; trim-during-play on actual rendered
   length).
6. At each scheduled `@presentationTime` inside the sub-MPD's
   tracking `<EventStream>`, the Player fires the corresponding
   beacon HTTP GET (P-07).

On `<InsertPresentation>` end, main timeline resumes from the paused
position; on `<ReplacePresentation>` end, main timeline resumes at
the position determined by `@returnOffset` (or natural playhead if
absent).

### 6.3 Non-linear flow

Non-linear slots follow a similar timeline-triggered or pause-
triggered pattern, with the resolution document shape from Chapter 5
§5.6.2 (candidate-set, multiple forms per candidate).

1. The Broadcaster's MPD declares the slot via
   `<svta:OverlayPresentation>` or `<svta:PauseAdPresentation>`
   inside an `<Event>` with the matching scheme URI from §5.2.
2. For `<svta:OverlayPresentation>`: the slot is timeline-triggered;
   the Player resolves the ADS URL at a randomised instant in the
   ERT window (same logic as linear).
3. For `<svta:PauseAdPresentation>`: the slot is pause-triggered.
   The Player observes user-pause events; if the pause time falls
   inside the window `[@windowStart, @windowEnd]`, the Player MAY
   resolve the ADS URL on demand at the moment of pause. The
   Player MAY alternatively pre-fetch the resolution document at
   ERT and cache it for the duration of the window. Pre-fetch versus
   on-demand is an implementation choice with latency / targeting-
   freshness trade-offs.
4. The ADS replies with a non-linear `ListMPD` (Chapter 5 §5.6.2),
   each `<Period>` carrying a `<svta:CandidateForms>` block with one
   or more `<svta:Form>` entries, each `<svta:Form>` linking to a
   per-form sub-MPD via `<ImportedMPD>`.
5. The Player ranks candidates by `@candidatePriority` and, for the
   highest-ranked candidate, walks `<svta:Form>` entries by
   `@formPriority`, selecting the first form whose `@mediaType` and
   `@admissibleLayouts` satisfy P-03 (device caps × slot
   `@allowedLayouts` × ADS hints).
6. The Player fetches the selected form's sub-MPD via the form's
   `<ImportedMPD>` `@uri`, then fetches segments / image / HTML
   asset from the ad CDN.
7. The Player composites the form on top of the primary content
   using HTML5 / CSS layout primitives (D-04). For video forms on
   D1 / D2, the second video decoder is used; for image / HTML
   forms on D1 / D3 / D4, the appropriate overlay surface is used.
8. The Player fires the impression beacon at the instant the
   overlay becomes visible (P-08), then fires quartile beacons at
   25 / 50 / 75 / 100 % of the Broadcaster-declared overlay window
   (`@maxDuration` from the slot), then fires the complete beacon
   when the window elapses or the overlay is dismissed (whichever
   comes first).
9. If P-05 trims the overlay before all quartiles fire, the Player
   stops firing beacons at the trim boundary.

### 6.4 Interface contracts

| Source | Target | Transport | Format | Direction | Error semantics |
|--------|--------|-----------|--------|-----------|-----------------|
| Player | Broadcaster CDN | HTTP / HTTPS | DASH MPD (XML) | request / response (pull) | HTTP status codes; on 4xx / 5xx the Player retries or aborts the session per its own policy. |
| Player | Broadcaster CDN | HTTP / HTTPS | Media segments (ISO BMFF / CMAF) | request / response (pull) | DASH-IF segment-retry guidelines apply. |
| Player | ADS | HTTP / HTTPS | Request: query params per `UrlParamInfo` (§I.4). Response: `ListMPD` (XML) | request / response (pull, sync) | HTTP status codes; empty `ListMPD` or 4xx / 5xx → Player falls through to primary content per Chapter 8 §8.1. |
| Player | Ad CDN | HTTP / HTTPS | Per-ad / per-form sub-MPDs (XML); ad segments | request / response (pull) | Same as Broadcaster CDN; per-form failure skips that form and falls back to next form / candidate. |
| Player | Tracking endpoint | HTTP / HTTPS | HTTP GET, body-less | fire-and-forget (push) | Errors logged best-effort; never alter playback. |
| ADS | (internal) upstream | (out of scope) | (out of scope) | (out of scope) | ADS adapter translates upstream errors into HTTP errors or empty `ListMPD` toward the Player. |

All transport is over HTTPS in production. Authentication, DRM, and
token exchange layer on top of HTTPS per DASH-IF guidelines and are
out of scope.

---

## Chapter 7 — Expected behaviour per scenario

This chapter specifies the Player's expected behaviour for each ad
opportunity type across each device class D1..D5 from Chapter 3
§3.2. The behaviour is normative and binds Player conformance via
P-01.

The five scenarios covered are:

- §7.1 — Linear slot (covers pre-roll, mid-roll, multi-ad break).
- §7.2 — Coexisting overlay.
- §7.3 — Hybrid linear + overlay.
- §7.4 — Pause-triggered ad.
- §7.5 — Legacy Player encountering new constructs (cross-cutting).

Deep walk-throughs with full MPDs and ListMPDs are in the annexes.

### 7.1 Linear slot

Applies to slots declared via `<InsertPresentation>` or
`<ReplacePresentation>`, including multi-ad-break slots (where the
`ListMPD` carries multiple `<Period>` entries).

| Class | Behaviour |
|-------|-----------|
| D1 | Highest-fidelity linear playback. One of the two decoders renders the ad's video form; the second MAY be used to pre-buffer the next candidate. R4 enforced at playback. |
| D2 | Same as D1. Linear-only does not exercise overlay composition; the absence of non-video overlay capability is irrelevant. |
| D3 | Single decoder renders the ad sequentially with the primary content (primary stops, ad plays, primary resumes). R4 enforced at playback. |
| D4 | Same as D3. |
| D5 | Same as D3. Linear ads are sequential, not concurrent; no overlay capability needed. |

### 7.2 Coexisting overlay

Applies to slots declared via `<OverlayPresentation>`. Primary
content continues to play; an overlay is composited over it for at
most `@maxDuration`.

| Class | Behaviour |
|-------|-----------|
| D1 | Walks candidates by `@candidatePriority`, then walks forms by `@formPriority` on the highest-ranked candidate. Picks the highest-priority renderable form (any of video, image, HTML). Composes via HTML5 / CSS on top of primary. |
| D2 | If the highest-ranked candidate's highest-priority renderable form is video AND it admits one of the slot's allowed layouts, renders that video form on the second decoder as a video-on-video overlay. If no candidate has a renderable video form, AND `side-by-side` is in `@allowedLayouts`, renders the candidate's video form in a side-by-side composition. Otherwise declines the slot. Image and HTML forms are never renderable on D2 in this scenario. |
| D3 | Walks forms; skips video forms (single-decoder cannot composite a second video on top of the primary). Picks HTML if available, else image. Composes via HTML5 / CSS. |
| D4 | Walks forms; skips video and HTML. Picks image if available; if not, skips the candidate and tries the next. If no candidate offers an image form, declines the slot. |
| D5 | No overlay surface of any kind. Declines the slot; primary content continues uninterrupted. |

### 7.3 Hybrid linear + overlay

Applies to a break where the Broadcaster declares both a linear slot
and a non-linear overlay slot active over the same time window. The
two slots resolve independently against the ADS.

| Class | Behaviour |
|-------|-----------|
| D1 | Linear and overlay are both rendered. Linear on one decoder; overlay via HTML5 / CSS (HTML or image) or the second decoder (video form). |
| D2 | Linear on the primary decoder. Overlay renders only if its selected form is video (rendered on the second decoder as a video-on-video composition on top of the linear ad). If overlay candidate offers only HTML / image forms, the overlay portion is declined; the linear portion plays full-screen, no overlay. |
| D3 | Linear on the single decoder. Overlay portion is declined (the device cannot composite over a linear ad's video on a single decoder; the conservative default per R2 / R3 in the source spec). |
| D4 | Same as D3. |
| D5 | Linear on the single decoder. Overlay portion is declined (no overlay surface). |

### 7.4 Pause-triggered ad

Applies to slots declared via `<PauseAdPresentation>`. A pause by the
user inside `[@windowStart, @windowEnd]` triggers the slot.

| Class | Behaviour |
|-------|-----------|
| D1 | On pause inside the window: walks forms; picks the highest-fidelity renderable form (video on the second decoder, or HTML / image via the appropriate overlay surface, depending on `@allowVideoForm` and form priorities). On resume, dismisses the overlay. |
| D2 | On pause inside the window: the primary decoder holds the paused frame. The second decoder is free; if the candidate carries a video form, renders it as a video-on-video overlay. HTML / image forms are not renderable on D2. If no video form is available, declines the slot. |
| D3 | On pause inside the window: walks forms. If `@allowVideoForm="true"` AND the Player can re-task the single decoder for a video form on top of the paused frame, renders the video form. Otherwise picks HTML if available, else image. |
| D4 | On pause inside the window: skips video (single decoder, primary holds the paused frame). Skips HTML (no HTML overlay surface). Picks image if available; if not, declines the slot. |
| D5 | On pause inside the window: no overlay surface. Declines the slot; the paused frame stays on screen until the user resumes. |

A pause outside `[@windowStart, @windowEnd]` never triggers a slot,
regardless of device class.

### 7.5 Legacy Player encountering new constructs

A Player that does not implement the constructs introduced by this
specification encounters them as unknown elements (`<svta:OverlayPresentation>`,
`<svta:PauseAdPresentation>`, `<svta:CandidateForms>`,
`<svta:Form>`) and as `<EventStream>` elements with unknown
`@schemeIdUri` values.

| Class | Behaviour |
|-------|-----------|
| D1..D5 (uniform) | Per MPEG-DASH 6th edition §5.10.1 (event subscription model) and §5.2.1 (open content model + unknown attribute rule), the legacy Player skips the unknown `<EventStream>` and unknown elements silently. Playback continues with primary content uninterrupted. No tracking beacon is fired. No error surfaces to the user. |

Behaviour does not vary across device classes because the
graceful-degradation outcome depends on the Player version, not on
device capabilities (P-09).

---

## Chapter 8 — Implementation notes

This chapter is **non-normative**. It contains guidance for
implementers that supports the obligations in chapters 4 through 7
but does not extend them.

### 8.1 Error semantics — Player behaviour by failure class

The Player will encounter a variety of failures during SGAI
exchanges. The conformant behaviour for each is summarised below.
"Fall through to primary content" means: no visible artefact, no
tracking beacon fired for the failed slot, primary playback
continues from the playhead position.

| Failure class | Player MUST | Player MAY |
|---------------|-------------|------------|
| HTTP timeout on ADS | Fall through to primary content. | Retry once within the slot window if time permits. |
| HTTP 4xx / 5xx on ADS | Fall through to primary content. | Retry on 5xx with backoff. Suppress retries on 4xx. |
| DNS / TCP / TLS failure | Fall through to primary content. | Log network class for telemetry. |
| Malformed XML in resolution document | Fall through to primary content. | Log parse error. |
| Schema-invalid resolution document | Fall through to primary content. | Partial recovery if salvageable (drop offending candidate, keep others). |
| Unknown root element / unknown profile URI | Fall through to primary content. | Log unknown element once per session. |
| No candidate has a renderable form on the device | Skip candidate; if no candidate renders, decline slot; fall through. | Log telemetry. |
| Unknown event scheme on a Broadcaster `<EventStream>` | Ignore the `<EventStream>` per MPEG-DASH 6th edition §5.10.1. Continue primary content. | Log scheme once. |
| Declared cumulative duration would exceed cap | MAY drop candidate before playback (drop-before-play). Continue with remaining candidates in ADS-declared order. | — |
| Actual rendered length exceeds cap mid-rendering | Stop rendering at cap boundary (trim-during-play). | Stop firing remaining tracking beacons at trim boundary. |
| Tracking beacon HTTP failure | Continue playback. | Log; surface to application via implementation-defined API. |
| Late ADS response (after slot has resolved) | Treat as no-fill — do not inject the ad post-hoc. Drop the late response. | Log latency. |

Order of precedence when multiple failures stack on the same
exchange (top wins): transport → resolution-document level →
constraint surfacing → per-candidate decode-time → per-candidate
playback-time → tracking failures (non-fatal).

### 8.2 Tracking-only candidates (no form)

An upstream ad-decisioning system may emit candidates that carry only
tracking beacons and no renderable form (a "tracking pixel" record).
Such candidates have no place in a non-linear `ListMPD` under this
specification because A-02 requires every candidate to carry at least one
form. The ADS adapter SHOULD silently skip these records during the
upstream → `ListMPD` conversion; the resulting `ListMPD` simply
omits the entry. The Player never sees them.

### 8.3 ADS pre-fetch on pause-triggered slots

For `<svta:PauseAdPresentation>` slots, the Player has two viable
strategies:

- **On-demand resolution**: defer the ADS resolution request to the
  moment the user pauses inside `[@windowStart, @windowEnd]`. Lowest
  latency tolerance, freshest targeting.
- **Pre-fetch at ERT**: resolve the ADS URL at the slot's ERT and
  cache the resolution document for the lifetime of the window. Best
  pause-to-overlay latency, but the ad metadata may be stale by the
  time the user pauses.

Both are conformant. Implementations SHOULD pick one strategy per
deployment based on the latency / targeting trade-off; mixed
strategies inside a single session are discouraged for
predictability.

### 8.4 D5 / non-renderable: privacy and impression accounting

On devices that will inevitably skip a slot (typically D5 for
non-linear opportunities), the Player still has a choice about
whether to issue the ADS resolution request at all. Issuing the
request supports impression accounting and frequency-capping signals
at the ADS layer; skipping the request saves bandwidth and avoids
exposing the viewer to extraneous tracking. This specification does not
mandate one choice over the other; both are conformant. Deployments
SHOULD pick a policy that aligns with their privacy posture.

### 8.5 Vendor-namespaced metadata

When carrying VAST application-level metadata (`ClickThrough`,
`AdSystem`, `AdTitle`, `UniversalAdId`) on per-form sub-MPDs,
implementations SHOULD:

- Use a stable vendor URN (e.g. `urn:qualabs:sgai:2026`,
  `urn:vendor-x:ad-meta:2026`).
- Place vendor elements as children of `<ImportedMPD>` or as
  children of `<svta:Form>`, so the metadata travels with the form
  it describes.
- Document the vendor schema separately from this specification; the SGAI
  specification imposes no shape on vendor extensions beyond the
  ignore-if-unknown contract.

### 8.6 Surfacing errors to the application layer

The Player MAY expose ad-slot error events to the application layer
via an implementation-defined API (callbacks, event bus, observable
streams). This specification does not specify the API shape; common patterns
include:

- An `adslot-error` event with fields `{slotId, errorClass, detail}`
  where `errorClass` matches the §8.1 failure-class taxonomy.
- A `tracking-beacon-failure` event with fields `{beaconId, status,
  url}`.

Conformance does not require any specific API; the obligation is
behavioural (primary content does not freeze, blank, or display an
error overlay unless the application has explicitly opted in).

---

## Annex A — Linear pre-roll walk-through (UC-01)

### A.1 Scenario

A pre-roll slot is declared at the start of a piece of OTT content.
The slot allows linear forms only and is capped at 15 s. The ADS
returns a single-ad `ListMPD`.

### A.2 Broadcaster's primary MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xmlns:up="urn:mpeg:dash:schema:urlparam:2025"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     type="static"
     minBufferTime="PT2S"
     mediaPresentationDuration="PT45M"
     profiles="urn:mpeg:dash:profile:advanced-linear:2025">

  <EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025">
    <up:UrlParamInfo includeInRequests="altmpd"
                     queryTemplate="video_profile=$urn:mpeg:dash:state:video$&amp;session_id=$urn:mpeg:dash:state:cmcd#sid$"/>
  </EssentialProperty>

  <Period id="1" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="101" presentationTime="0" duration="15000">
        <InsertPresentation url="https://ads.example.com/decision/preroll"
                            earliestResolutionTimeOffset="0"
                            maxDuration="15000"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4D401F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="video/init.mp4"
                       media="video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### A.3 ADS `ListMPD` response

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-05-12T10:00:00Z">

  <BaseURL>https://ads.example.com/delivery/</BaseURL>

  <Period id="ad_01" duration="PT15S">
    <ImportedMPD uri="creative_101.mpd" earliestResolutionTimeOffset="0"/>
  </Period>
</MPD>
```

### A.4 Per-ad sub-MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S"
     publishTime="2026-05-12T10:00:00Z">

  <Period id="1" duration="PT15S" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="impression">https://tracker.example.com/impression?ad=101</Event>
      <Event presentationTime="0"     id="start">https://tracker.example.com/start?ad=101</Event>
      <Event presentationTime="3750"  id="q1">https://tracker.example.com/q1?ad=101</Event>
      <Event presentationTime="7500"  id="q2">https://tracker.example.com/q2?ad=101</Event>
      <Event presentationTime="11250" id="q3">https://tracker.example.com/q3?ad=101</Event>
      <Event presentationTime="15000" id="complete">https://tracker.example.com/complete?ad=101</Event>
    </EventStream>

    <AdaptationSet mimeType="video/mp4" codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <Representation id="v1" bandwidth="2500000" width="1280" height="720">
        <BaseURL>media/video_101.mp4</BaseURL>
        <SegmentBase indexRange="0-850"/>
      </Representation>
    </AdaptationSet>
  </Period>
</MPD>
```

### A.5 Per-device-class decision walk-through

| Class | Player decision | What the user sees |
|-------|-----------------|--------------------|
| D1 | Resolves ADS at session start. One candidate; one video form. Renders the video form on one decoder (the second is unused for a linear-only slot). Enforces 15 s cap. Fires impression / start at t=0, quartiles at 3.75 / 7.5 / 11.25 s, complete at 15 s. | A 15 s full-screen ad before the primary content begins. |
| D2 | Same as D1. | Same as D1. |
| D3 | Resolves ADS. Plays the video form on the single decoder, sequentially before the primary content. Cap enforced. | Same as D1. |
| D4 | Same as D3. | Same as D3. |
| D5 | Same as D3. Linear is sequential; no overlay surface needed. | Same as D3. |

---

## Annex B — Coexisting overlay with multi-form / multi-layout candidate (UC-03)

### B.1 Scenario

The Broadcaster declares a mid-content non-linear slot at offset
PT2M of the primary content, capped at 20 s, admitting Corner Overlay,
Lower-Third Overlay, and L-Shape layouts. The ADS returns two
candidates, the first of which is a **multi-form, multi-layout**
candidate (three forms: HTML, image, video; the HTML and image forms
each admit multiple layouts).

This annex demonstrates the multi-form / multi-layout case mandated
by chapter 5 §5.6.2.

### B.2 Broadcaster's primary MPD (slot declaration only)

```xml
<EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
             timescale="1000">
  <Event id="201" presentationTime="120000" duration="20000">
    <svta:OverlayPresentation xmlns:svta="urn:svta:dash:sgai:2026"
                              url="https://ads.example.com/decision/overlay"
                              maxDuration="20000"
                              allowedLayouts="corner-overlay,lower-third-overlay,l-shape"
                              maxConcurrency="1"
                              earliestResolutionTimeOffset="10000"/>
  </Event>
</EventStream>
```

### B.3 ADS non-linear `ListMPD` response

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:list:2024 urn:svta:dash:sgai-list:2026"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-05-12T10:00:00Z">

  <BaseURL>https://ads.example.com/delivery/</BaseURL>

  <!-- Candidate 1 — multi-form, multi-layout -->
  <Period id="cand-1" duration="PT20S">
    <svta:CandidateForms candidateId="cand-1" candidatePriority="80">
      <svta:Form formId="cand-1-html" mediaType="html"
                 admissibleLayouts="corner-overlay,lower-third-overlay"
                 formPriority="100" duration="20000">
        <ImportedMPD uri="creatives/cand-1-html.mpd"/>
      </svta:Form>
      <svta:Form formId="cand-1-image" mediaType="image"
                 admissibleLayouts="corner-overlay,lower-third-overlay,l-shape"
                 formPriority="70" duration="20000">
        <ImportedMPD uri="creatives/cand-1-image.mpd"/>
      </svta:Form>
      <svta:Form formId="cand-1-video" mediaType="video"
                 admissibleLayouts="corner-overlay"
                 formPriority="50" duration="20000">
        <ImportedMPD uri="creatives/cand-1-video.mpd"/>
      </svta:Form>
    </svta:CandidateForms>
  </Period>

  <!-- Candidate 2 — single form, single layout (fallback) -->
  <Period id="cand-2" duration="PT20S">
    <svta:CandidateForms candidateId="cand-2" candidatePriority="40">
      <svta:Form formId="cand-2-image" mediaType="image"
                 admissibleLayouts="corner-overlay"
                 formPriority="100" duration="20000">
        <ImportedMPD uri="creatives/cand-2-image.mpd"/>
      </svta:Form>
    </svta:CandidateForms>
  </Period>
</MPD>
```

### B.4 Per-form sub-MPDs (representative — HTML form)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S"
     publishTime="2026-05-12T10:00:00Z">

  <Period id="1" duration="PT20S" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="impression">https://tracker.example.com/impression?cand=1&amp;form=html</Event>
      <Event presentationTime="5000"  id="q1">https://tracker.example.com/q1?cand=1&amp;form=html</Event>
      <Event presentationTime="10000" id="q2">https://tracker.example.com/q2?cand=1&amp;form=html</Event>
      <Event presentationTime="15000" id="q3">https://tracker.example.com/q3?cand=1&amp;form=html</Event>
      <Event presentationTime="20000" id="complete">https://tracker.example.com/complete?cand=1&amp;form=html</Event>
    </EventStream>

    <AdaptationSet mimeType="text/html"
                   contentType="application">
      <Representation id="html1" bandwidth="50000">
        <BaseURL>creatives/cand-1.html</BaseURL>
      </Representation>
    </AdaptationSet>
  </Period>
</MPD>
```

The image and video form sub-MPDs follow the same shape, swapping
the `<AdaptationSet>` content for `image/png` and `video/mp4`
respectively. Tracking offsets in each sub-MPD are scheduled against
the **20 s overlay window** declared by the Broadcaster, not against
the form's intrinsic asset duration. The Player uses these offsets
verbatim per P-08.

### B.5 Per-device-class decision walk-through

| Class | Player decision | What the user sees |
|-------|-----------------|--------------------|
| D1 | Validates both candidates (each within 20 s, layouts within allowed set, maxConcurrency=1 honoured). Picks `cand-1` (priority 80 > 40). Walks forms by `@formPriority`: HTML (100, admits corner-overlay & lower-third-overlay — both allowed). Renders HTML on Corner Overlay layout via HTML5/CSS. Fires impression at overlay-visible instant; quartiles at 5/10/15 s relative to the 20 s window; complete at 20 s. | Primary keeps playing. An HTML overlay appears in the corner for 20 s, then disappears. |
| D2 | Walks forms on `cand-1`. HTML (100) → not renderable (D2 cannot composite non-video on top of video). Image (70) → not renderable. Video (50) → renderable, but `@admissibleLayouts="corner-overlay"` and the slot allows corner-overlay. Renders the video form on the second decoder as a video-on-video corner overlay. | Primary keeps playing. A small video plays in the corner for 20 s. |
| D3 | Walks forms on `cand-1`. HTML (100) → renderable on D3 (HTML overlay surface). Renders HTML on Corner Overlay layout (highest-priority admissible layout for HTML). | Primary keeps playing. An HTML overlay appears in the corner for 20 s. |
| D4 | Walks forms on `cand-1`. HTML (100) → not renderable on D4 (no HTML overlay surface). Image (70) → renderable; admits corner-overlay, lower-third-overlay, l-shape. Renders image on Corner Overlay (highest-priority admissible). | Primary keeps playing. A static image appears in the corner for 20 s. |
| D5 | Walks forms on `cand-1`. No form renderable. Walks `cand-2`. Same — no overlay surface. Declines the slot. | Primary keeps playing. Nothing changes on screen. |

This annex is the multi-form / multi-layout showcase required by
the spec output's annex policy.

---

## Annex C — Hybrid linear + overlay walk-through (UC-04)

### C.1 Scenario

Mid-content break: a linear slot capped at 30 s plus a concurrent
overlay slot capped at 30 s, admitting Lower-Third Overlay only. The
ADS returns one linear candidate and one overlay candidate
independently.

### C.2 Broadcaster's primary MPD (slot declarations only)

```xml
<EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
             timescale="1000">
  <Event id="301" presentationTime="600000" duration="30000">
    <ReplacePresentation url="https://ads.example.com/decision/midroll"
                         earliestResolutionTimeOffset="30000"
                         maxDuration="30000"
                         returnOffset="30000"
                         clipDuration="30000"
                         startWithOffset="false"/>
  </Event>
</EventStream>

<EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
             timescale="1000">
  <Event id="302" presentationTime="600000" duration="30000">
    <svta:OverlayPresentation xmlns:svta="urn:svta:dash:sgai:2026"
                              url="https://ads.example.com/decision/midroll-overlay"
                              maxDuration="30000"
                              allowedLayouts="lower-third-overlay"
                              maxConcurrency="1"
                              earliestResolutionTimeOffset="20000"/>
  </Event>
</EventStream>
```

### C.3 ADS responses (linear + non-linear)

**Linear `ListMPD`** (the `cand-mid-1` Period imports a per-ad sub-
MPD analogous to annex A but 30 s):

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024" type="list" minBufferTime="PT1S">
  <BaseURL>https://ads.example.com/delivery/</BaseURL>
  <Period id="cand-mid-1" duration="PT30S">
    <ImportedMPD uri="creative_midroll_201.mpd"/>
  </Period>
</MPD>
```

**Non-linear `ListMPD`** (one candidate, two forms — video for D1/D2,
image for D4):

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:list:2024 urn:svta:dash:sgai-list:2026"
     type="list" minBufferTime="PT1S">
  <BaseURL>https://ads.example.com/delivery/</BaseURL>
  <Period id="ov-cand-1" duration="PT30S">
    <svta:CandidateForms candidateId="ov-cand-1" candidatePriority="100">
      <svta:Form formId="ov-cand-1-video" mediaType="video"
                 admissibleLayouts="lower-third-overlay"
                 formPriority="100" duration="30000">
        <ImportedMPD uri="creatives/ov-cand-1-video.mpd"/>
      </svta:Form>
      <svta:Form formId="ov-cand-1-image" mediaType="image"
                 admissibleLayouts="lower-third-overlay"
                 formPriority="50" duration="30000">
        <ImportedMPD uri="creatives/ov-cand-1-image.mpd"/>
      </svta:Form>
    </svta:CandidateForms>
  </Period>
</MPD>
```

### C.4 Per-device-class decision walk-through

| Class | Linear portion | Overlay portion | What the user sees |
|-------|----------------|-----------------|--------------------|
| D1 | Plays linear ad on decoder 1. | Walks forms on `ov-cand-1`: video (100) → renderable on decoder 2 as video-on-video. Renders. | Linear ad full-screen + a video lower-third overlay on top of it for 30 s. |
| D2 | Plays linear ad on decoder 1. | Video form renderable on decoder 2 (video-on-video). Renders. | Same as D1. |
| D3 | Plays linear ad on single decoder. | Per chapter 7 §7.3, overlay portion is declined on single-decoder devices in hybrid scenarios (conservative default). | Linear ad full-screen, no overlay. |
| D4 | Same as D3. | Declined. | Same as D3. |
| D5 | Plays linear ad on single decoder. | Declined (no overlay surface). | Same as D3. |

---

## Annex D — Pause-triggered ad walk-through (UC-05)

### D.1 Scenario

The Broadcaster declares a pause-triggered slot active from PT5M to
PT35M of the primary content. Maximum overlay duration is 15 s.
Allowed layouts are full-screen and partial-screen (Pause Ad
templates from IAB §3.3). `@allowVideoForm` is true. The ADS returns
one candidate with image + video forms.

### D.2 Broadcaster's primary MPD (slot declaration only)

```xml
<EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026"
             timescale="1000">
  <Event id="401" presentationTime="0">
    <svta:PauseAdPresentation xmlns:svta="urn:svta:dash:sgai:2026"
                              url="https://ads.example.com/decision/pause"
                              maxDuration="15000"
                              allowedLayouts="fullscreen,partial-screen"
                              windowStart="300000"
                              windowEnd="2100000"
                              allowVideoForm="true"
                              earliestResolutionTimeOffset="300000"/>
  </Event>
</EventStream>
```

### D.3 ADS non-linear `ListMPD`

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:list:2024 urn:svta:dash:sgai-list:2026"
     type="list" minBufferTime="PT1S">
  <BaseURL>https://ads.example.com/delivery/</BaseURL>
  <Period id="pause-cand-1" duration="PT15S">
    <svta:CandidateForms candidateId="pause-cand-1" candidatePriority="100">
      <svta:Form formId="pause-cand-1-image" mediaType="image"
                 admissibleLayouts="fullscreen,partial-screen"
                 formPriority="100" duration="15000">
        <ImportedMPD uri="creatives/pause-cand-1-image.mpd"/>
      </svta:Form>
      <svta:Form formId="pause-cand-1-video" mediaType="video"
                 admissibleLayouts="fullscreen"
                 formPriority="80" duration="15000">
        <ImportedMPD uri="creatives/pause-cand-1-video.mpd"/>
      </svta:Form>
    </svta:CandidateForms>
  </Period>
</MPD>
```

### D.4 Per-device-class decision walk-through

| Class | Pause inside window → Player decision | What the user sees |
|-------|---------------------------------------|--------------------|
| D1 | Walks forms by priority. Image (100) is renderable (HTML/image overlay surface). Renders the image on Full-screen layout. (D1 could also pick the video form on the second decoder if priorities favoured it; here the ADS ranks image higher.) | Paused frame on screen with a full-screen image overlay. Resume dismisses. |
| D2 | Walks forms. Image (100) → not renderable on D2. Video (80) → renderable on the second decoder. Renders the video form on Full-screen layout. | Paused frame on screen with a video overlay. Resume dismisses. |
| D3 | Walks forms. Image (100) → renderable. Renders image. (With `@allowVideoForm="true"`, the Player MAY re-task the single decoder for the video form, but priority favours image; the Player picks image per `@formPriority`.) | Paused frame on screen with a full-screen image overlay. Resume dismisses. |
| D4 | Walks forms. Image (100) → renderable. Renders image. (Video on D4 with single decoder is not feasible regardless of `@allowVideoForm`, but here image wins on priority anyway.) | Same as D3. |
| D5 | Walks forms. No form renderable. Declines slot. | Paused frame on screen with nothing else. Resume continues playback. |

A pause **outside** `[PT5M, PT35M]` never triggers the slot; the
Player simply pauses and resumes with no overlay.

---

## Annex E — Legacy Player test cases (UC-07 / chapter 5 §5.10)

This annex provides representative test cases that verify the
ignore-if-unknown contract per chapter 4 D-01 and chapter 7 §7.5.

### E.1 T-E1 — Legacy Player + `<svta:OverlayPresentation>`

Input MPD: annex B §B.2 (primary MPD with an
`<OverlayPresentation>` slot).

Legacy Player implementation: a Player that conforms to MPEG-DASH
6th edition (§5.10.1 event subscription, §5.2.1 open content) but
does not implement `urn:svta:dash:sgai-overlay:2026`.

Expected behaviour: the legacy Player observes the `<EventStream>`
with scheme `urn:svta:dash:sgai-overlay:2026`, does not recognise the
scheme URI, and per §5.10.1 ignores the entire `<EventStream>`.
Playback continues with primary content uninterrupted. No tracking
beacon is fired. No error log at FATAL level.

Pass criteria: observable playback continues; no errors logged at
FATAL level; no overlay rendered; the slot's `<EventStream>` is
absent from any observable state surfaced to the application.

### E.2 T-E2 — Legacy Player + `<svta:PauseAdPresentation>`

Input MPD: annex D §D.2.

Legacy Player: as above.

Expected behaviour: same as T-E1 — the legacy Player ignores the
unknown `<EventStream>` scheme; the user's pause behaviour produces
no overlay; primary playback resumes on user-initiated resume.

Pass criteria: same as T-E1.

### E.3 T-E3 — Legacy Player + non-linear `ListMPD`

Input: a hypothetical `ListMPD` reaching a legacy Player that does
not implement the candidate-set extension (`urn:svta:dash:sgai-
list:2026`).

This case is normally unreachable: a legacy Player that ignored the
overlay `<EventStream>` (T-E1) never resolves the ADS URL, never
receives the `ListMPD`. The test case is included for completeness
to verify the open-content-model behaviour on `<Period>`:

Legacy Player: parses the `ListMPD`. Each `<Period>` contains a
`<svta:CandidateForms>` element. Per §5.2.1, the legacy Player's
schema validates the open-content `<xs:any namespace="##other"
processContents="lax"/>` wildcard, treats `<svta:CandidateForms>`
as unknown content, and skips it. If the `<Period>` contained an
inline `<ImportedMPD>` sibling, the Player would use it; in the
non-linear shape there is no `<ImportedMPD>` at the `<Period>` level
(it lives inside `<svta:Form>`), so the Period yields no
referenceable ad MPD. The Player treats the Period as a no-fill
entry and falls through to primary content. No tracking beacon is
fired.

Pass criteria: the unknown elements parse-skip; no error at FATAL
level; primary content continues.

---

## Annex F — Test cases and conformance criteria summary

This annex restates the error-class taxonomy from chapter 8 §8.1 as
a test-case template and links each test case to the conformance
clause it exercises. Implementers can use this as the basis of a
conformance test suite.

| Test ID | Failure class exercised | Conformance clauses | Expected Player behaviour |
|---------|--------------------------|---------------------|---------------------------|
| T-F01 | HTTP timeout on ADS resolution | P-04 (decline slot, fall through) | No ad rendered; primary continues; no tracking beacon fired. |
| T-F02 | HTTP 4xx (e.g. 403) on ADS | P-04 | Same as T-F01. |
| T-F03 | HTTP 5xx on ADS | P-04 | Same as T-F01. |
| T-F04 | DNS / TCP / TLS failure to ADS | P-04 | Same as T-F01. |
| T-F05 | Malformed XML in `ListMPD` | P-02, P-04 | Same as T-F01; parse error logged. |
| T-F06 | Schema-invalid `ListMPD` (e.g. `<svta:Form>` without `@mediaType`) | P-02, P-04 | Offending candidate dropped; remaining candidates evaluated; if none, slot declined. |
| T-F07 | Unknown root element / unknown profile URI | P-04, P-09 | Slot declined; primary continues. |
| T-F08 | No candidate has a renderable form (e.g. D5 + overlay) | P-04 | Slot declined gracefully. |
| T-F09 | Unknown `Event@schemeIdUri` on Broadcaster MPD | P-09 | Entire `<EventStream>` ignored; primary continues. |
| T-F10 | Declared cumulative duration > cap | P-05, P-06 | Drop-before-play permitted; remaining candidates played in order. |
| T-F11 | Actual rendered length > cap (trim-during-play) | P-05, P-08 | Stop at cap boundary; remaining tracking beacons suppressed. |
| T-F12 | Tracking beacon HTTP failure | P-07 | Playback uninterrupted; beacon failure logged. |
| T-F13 | Late ADS response (after slot resolved) | P-04 | Late response dropped; no post-hoc injection. |
| T-E1, T-E2, T-E3 | Legacy Player encounters new constructs | P-09 | See annex E. |
| T-M01 (multi-form D1) | Annex B D1 walk-through | P-03, P-06, P-08 | HTML form rendered on Corner Overlay; quartiles fired against the 20 s overlay window. |
| T-M02 (multi-form D2 fallback) | Annex B D2 walk-through | P-03, P-04, P-06 | Video form rendered on Corner Overlay (video-on-video); HTML/image skipped per D2 caps. |
| T-M03 (multi-form D5 decline) | Annex B D5 walk-through | P-04 | All candidates exhausted; slot declined; primary continues. |
| T-PAUSE01 (pause inside window) | Annex D | P-03, P-04, P-06, P-08 | Image overlay on paused frame (D1, D3, D4); video on second decoder (D2); slot declined (D5). |
| T-PAUSE02 (pause outside window) | Annex D §D.4 | (none — slot not active) | No overlay; pause behaviour unaffected. |

This concludes the spec document.

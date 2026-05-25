# SGAI for Linear and Non-Linear Ads in MPEG-DASH

> Build metadata
> - Iteration: v5 (major build)
> - Generated against MPEG-DASH 6th edition (ISO/IEC 23009-1:2025, FDIS).
> - RFC 2119 keywords (MUST, SHOULD, MAY) appear throughout the
>   normative chapters; their meaning is inherited from RFC 2119 /
>   RFC 8174. Per the spec's drafting principle DP-2, normative
>   obligations are stated as positive requirements (the action the
>   actor takes); the space outside the positive obligation is
>   implicitly out of scope.
> - Grounding: spec-only against `context/` and `context-analysis/`
>   inputs at build time. Claims that could not be verified against
>   the authoritative MPEG-DASH 6th edition source are tagged
>   `[inferred]`.

## 1. Scope

This specification defines **Server-Guided Ad Insertion (SGAI)** in
MPEG-DASH for **both linear and non-linear ads**. It is a complete
extension of MPEG-DASH 6th edition: the linear SGAI mechanism
defined in ISO/IEC 23009-1:2025 §5.16 (`<InsertPresentation>`,
`<ReplacePresentation>`) and §8.14 (`ListMPD` profile) is absorbed as
the baseline, and a non-linear extension is layered on top using
DASH 6th's normative extension points without altering any baseline
semantics.

Linear SGAI is carried forward unchanged. The non-linear extension
introduces constructs for overlays (corner / lower-third / banner),
content-resize compositions (squeezeback / L-shape / frame /
double-box), pause-triggered ads, and the hybrid case of a linear
ad with a concurrent overlay on top.

A conformant implementation of this specification:

- Plays primary content uninterrupted on a Player that does not
  implement the constructs introduced here (graceful degradation).
- Preserves the semantics of every pre-existing MPEG-DASH 6th
  edition construct.
- Implements every new construct via DASH 6th edition extension
  points whose ignore-if-unknown semantics make backward
  compatibility auditable per construct.

Audience: Player implementers, ad-server vendors, broadcast
authoring teams, and DASH-aware tooling authors. Reading prerequisite
is familiarity with MPEG-DASH 6th edition Sections 5.2.1, 5.10, 5.16,
8.14, 8.15, and Annex F.

### 1.1 What this specification covers

- Linear ad slots (pre-roll, mid-roll, multi-ad break) carried by
  the MPEG-DASH 6th edition `<InsertPresentation>` and
  `<ReplacePresentation>` events.
- Non-linear ad slots (overlay) carried by a new
  `<svta:OverlayPresentation>` event.
- Pause-triggered ad windows carried by a new
  `<svta:PauseAdPresentation>` event.
- Hybrid slots, declared as two co-located events (one linear, one
  non-linear) at the same `presentationTime`.
- Composition of an overlay window that crosses a pause-ad window
  (see Annex H).

### 1.2 What this specification leaves out of scope

- Server-side ad insertion / stitching (SSAI / SSR).
- Post-roll slots at the very end of a playback session.
- Companion / multi-screen ads beyond what IAB defines as CTV end
  cards.
- Native ads rendered in the Player chrome rather than the video
  pane.
- A parallel spatial-layout system: spatial arrangement of overlays
  is delegated to HTML5 / CSS layout primitives, and positions
  inside a layout (left, right, top, bottom, etc.) are not
  expressible in spec-level attributes.
- The ADS's internal decisioning logic (targeting, frequency
  capping, brand-safety filtering, competitive separation,
  ordering).
- The ADS API contract: this specification documents the
  Player-visible interface — the MPD event URL referenced by the
  Broadcaster, and the resolution document the ADS returns — and
  treats the ADS internal contract (invocation parameters,
  decisioning inputs, frequency-cap signals) as opaque, agreed
  bilaterally between the Broadcaster and the ADS out of band.
- Creative carriers outside the admissible set defined in §3.2.
  Senders that need scripted creatives wrap the script inside an
  HTML document and use `text/html`.
- Parallel non-linear ad rendering. At most one non-linear ad form
  is active on the screen at any given moment.
- Enhancement-layer video overlays (LCVC / scalable-codec
  enhancement layer composited as an overlay over the primary's
  base layer). A future edition MAY address this.
- Multi-view editorial concurrent content (non-ad concurrent
  content). The carriers defined here cover ad use cases only.
- Audio composition policy between an overlay's audio track and
  the primary's audio track. Players treat overlay audio
  per-implementation; a future edition MAY introduce a normative
  policy.
- Authentication, DRM, encryption, token-exchange transport flows.
  They layer on top of HTTPS per DASH-IF guidance and are
  orthogonal to SGAI.

## 2. Normative references

The following documents, in whole or in part, are normatively
referenced in this specification and are indispensable for its
application. For dated references, only the cited edition applies.
For undated references, the latest edition (including amendments)
applies.

- **ISO/IEC 23009-1:2025(E)** — *Information technology — Dynamic
  adaptive streaming over HTTP (DASH) — Part 1: Media presentation
  description and segment formats* (MPEG-DASH 6th edition; FDIS
  stage). Canonical:
  <https://standards.iso.org/iso-iec/23009/-1/ed-6/en>. Sections
  referenced normatively in this specification:
  §5.2.1 (foreign-namespace open content);
  §5.3.2.6 (`<ImportedMPD>` and the SPS profile binding);
  §5.8.4.8, §5.8.4.9 (`<EssentialProperty>` and
  `<SupplementalProperty>` vendor descriptors);
  §5.10 (`<EventStream>` and event scheme
  `urn:mpeg:dash:event:callback:2015`);
  §5.16 (Alternative MPD Insertion / Replacement Events;
  `<InsertPresentation>`, `<ReplacePresentation>`);
  §7.3 (Single-Period MPD MIME type restrictions);
  §8.12 (CMAF on-demand profile);
  §8.14 (`ListMPD` profile, URI `urn:mpeg:dash:profile:list:2024`);
  §8.15 (Single-Period Static profile, SPS);
  Annex F (non-ISO-BMFF delivery, Interoperability Point URIs);
  Annex I.3.1 / I.4 (URL parameterisation, scheme
  `urn:mpeg:dash:urlparam:2025`; the `<UrlParamInfo>` element is
  defined directly in the core MPD namespace
  `urn:mpeg:dash:schema:mpd:2011`).
  NOTE: Two known schema-vs-prose splits inside DASH 6th are
  inherited by this specification. (i) §5.16.3 and §5.16.4 name the
  URL attribute on `<InsertPresentation>` / `<ReplacePresentation>`
  as `@url` in the Table 62 prose, while the normative
  `AlternativeMPDEventType` XML schema declares
  `<xs:attribute name="uri">`. This specification uses the prose
  name `@url` throughout. (ii) The URL-parameterisation child
  element is named `<UrlParamInfo>` in §I.3.1 prose (type
  `ExtendedUrlInfoType`, Table I.3) and `<RequestParam>` in the
  semantic tables of §5.3 (Tables 3, 4, 16, 44). This specification
  follows the §I.3.1 prose name `<UrlParamInfo>`. Implementers
  using a strict schema validator should expect the alternate names
  in DASH-6th-conformant tooling.
- **IETF RFC 2119** — *Key words for use in RFCs to Indicate
  Requirement Levels*. <https://www.rfc-editor.org/rfc/rfc2119>.
- **IETF RFC 8174** — *Ambiguity of Uppercase vs Lowercase in RFC
  2119 Key Words*. <https://www.rfc-editor.org/rfc/rfc8174>.
- **IETF RFC 4337** — *MIME Type Registration for MPEG-4*. Pins the
  admissible `@mimeType` values on `<AdaptationSet>` /
  `<Representation>` reached via `<ImportedMPD>` to `video/mp4`,
  `audio/mp4`, `application/mp4`.
  <https://www.rfc-editor.org/rfc/rfc4337>.
- **IAB Tech Lab — Ad Format Guidelines for Digital Video and CTV**
  (Final Release, May 2026). Live source:
  <https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e>.
  Authoritative source for the accepted ad-type vocabulary used by
  §3.2. The reference is to the live document, not to a snapshot,
  because the IAB owns the vocabulary's lifecycle.
- **W3C HTML Living Standard** — <https://html.spec.whatwg.org/>.
  Defines `text/html` semantics, including inline `<script>`
  execution.
- **W3C CSS Layout Modules** — relevant W3C CSS specifications for
  the spatial arrangement of overlays. Specific modules
  (Positioning, Flexbox, Grid) are non-normative for this spec;
  the binding is *use the standard, do not invent a parallel one*.

### 2.1 Scheme URIs and namespaces introduced by this edition

The following URIs are introduced normatively by this edition. A
Player implementing this edition recognises them. Year pinning
ensures that any future edition that changes the semantics of a
construct publishes under a new URI, so a legacy Player that
recognises only the older URI continues to apply the older
semantics (or, if it predates this edition entirely, silently
ignores the construct).

| URI | Used as | Construct |
|-----|---------|-----------|
| `urn:svta:dash:event:sgai-overlay:2026` | `<EventStream>@schemeIdUri` | The Broadcaster's non-linear opportunity declaration. The carrying `<Event>` element's `presentationTime` and `duration` define the overlay window. |
| `urn:svta:dash:event:sgai-pause-trigger:2026` | `<EventStream>@schemeIdUri` | The Broadcaster's pause-trigger window declaration. The `<Event>` `presentationTime` and `duration` define the window during which a viewer pause permits an overlay. |
| `urn:svta:dash:profile:sgai-overlay-list:2026` | `MPD@profiles` (on the non-linear resolution document) | Declares the resolution document conforming to the non-linear extension defined in §5.2.2. |
| `urn:svta:dash:sgai:2026` | XML namespace | The SVTA Ads WG extension namespace. Container for every SGAI element and attribute introduced by this edition. |

URIs inherited unchanged from MPEG-DASH 6th edition are referenced
in §5.1.1, §5.1.2, and §5.5; this section does not restate them.

## 3. Terms, definitions, abbreviations

### 3.1 Core terms

- **Ad opportunity (or slot).** A position on the primary content
  timeline at which the Broadcaster permits an ad to be rendered.
  Declared by the Broadcaster as an `<Event>` inside an
  `<EventStream>` whose `schemeIdUri` corresponds to the
  opportunity type (linear insert, linear replace, non-linear
  overlay, pause-trigger). The opportunity carries the slot's
  constraints (allowed layouts, maximum duration, etc.) as
  attributes on its scheme-specific child element.
- **Linear ad.** An ad whose form replaces the primary content for
  the duration of the slot. The Player switches its source from
  the main timeline to the ad timeline and back.
- **Non-linear ad.** An ad whose form is composited on top of, or
  alongside, the primary content during the slot, while primary
  playback continues.
- **Resolution document.** The XML document an Ad Decision Server
  returns when the Player resolves the slot's `@url`. For linear
  slots, this document is a `ListMPD` (§8.14 of the base
  specification). For non-linear slots, this document is an
  Overlay Resolution Document (§5.2.2) conforming to
  `urn:svta:dash:profile:sgai-overlay-list:2026`.
- **Candidate.** An entry in a non-linear resolution document
  representing one ad eligible for the slot. A candidate carries
  one or more renderable *forms* (see below). Linear `ListMPD`
  Periods are not candidates in the selection sense; the Player
  plays them in order without picking.
- **Form (or renderable form).** A single rendering option on a
  candidate, characterised by a media type (`video`, `image`, or
  `html`) and one layout token. A candidate may expose multiple
  forms (e.g. one video form, one image form, one HTML form) so
  the Player can pick the highest-fidelity form its device can
  render.
- **Layout.** A spatial arrangement of an overlay on top of (or
  alongside) the primary content, identified by a token defined by
  the IAB Ad Format Guidelines (see §3.2). Spatial positioning
  inside a layout is delegated to HTML5 / CSS and is out of scope
  here.
- **Broadcaster.** The party that owns the primary content and
  declares ad opportunities in the main MPD. Authority for *when*
  ads appear, *what kind* of slot they fill, and *what constraints*
  bind the slot.
- **Ad Decision Server (ADS).** The server that returns ad
  candidates when the Player resolves the slot URL. Authority for
  *which ads* fill the slot, *how many*, and *in what order*. Not
  responsible for enforcing the Broadcaster's slot constraints.
- **Player.** The client that reads the MPD, queries the ADS,
  validates the ADS response against Broadcaster-declared
  constraints, selects and composes the ad, and tracks the
  rendering. The Player is the enforcer of the Broadcaster's
  policy.
- **Slot cap.** A maximum total duration the Broadcaster declares
  on each ad opportunity (linear or non-linear), expressed as
  `@maxDuration` on the slot's scheme-specific child element. The
  Player enforces the cap against actual rendered length, trimming
  mid-ad if necessary.
- **Tracking carrier.** The construct used to convey impression
  and quartile beacons. This spec reuses the baseline DASH callback
  event scheme `urn:mpeg:dash:event:callback:2015` (§5.10 of the
  base specification) for both linear and non-linear ads.
- **Fall through.** A Player behaviour in which the slot is
  declined and primary content continues uninterrupted. Triggered
  when no candidate is renderable, when the resolution document is
  empty, when the ADS request fails, or when no admissible
  form / layout combination satisfies the slot's constraints.
- **Sub-MPD.** An MPD reached via `<ImportedMPD>` from a parent
  document (a `ListMPD` Period for linear, or a video-form
  `<svta:RenderableAsset>`'s `<ImportedMPD>` child for non-linear).
  Bound by §5.3.2.6 of the base specification to the SPS profile
  (§8.15) and therefore to `video/mp4` / `audio/mp4` /
  `application/mp4` on every Representation's `@mimeType`.
- **`@mediaType` vs `@mimeType`.** Two distinct attributes with
  non-overlapping domains used by this specification.
  `@mediaType` (on `<svta:RenderableAsset>`, §5.3.1) is the
  spec-side creative-carrier enum whose admissible values are
  `video`, `image`, `html` (§5.3.2). `@mimeType` (on
  `<AdaptationSet>` / `<Representation>` reached via
  `<ImportedMPD>`, §5.3.4) is the baseline DASH IANA MIME type
  bound by RFC 4337 to `video/mp4` / `audio/mp4` / `application/mp4`.
  The two attributes carry distinct semantics and serve different
  axes; this spec keeps them strictly separate.

### 3.2 Accepted ad-type / layout vocabulary

The accepted ad-type and layout vocabulary is sourced from the IAB
Tech Lab *Ad Format Guidelines for Digital Video and CTV* (May
2026 release; see chapter 2 for the live source). This
specification reuses IAB-defined ad-type values verbatim; chapter
3 enumerates the spec-side identifiers that map 1:1 to IAB-defined
names. Updates to the IAB vocabulary update the admissible token
set for this spec without a new edition, subject to the
cross-edition URI policy in §4.5.

The token in column *Spec-side identifier* is the value that
appears in `allowedLayouts` on a slot declaration and in `@layout`
on a renderable form (see §5.3.3 for the enum constraint per slot
type).

| Spec-side identifier | IAB ad type | Category | Notes |
|----------------------|-------------|----------|-------|
| `linear` | Linear Ad | Linear / in-stream | Baseline carried by `<InsertPresentation>` / `<ReplacePresentation>` and `ListMPD` (§5.1.1, §5.1.2, §5.2.1). |
| `pause-ad` | Pause Ad | Non-linear / viewer-initiated overlay | Display or video. Persists while the viewer is paused inside a Broadcaster-declared pause-trigger window. Carried by `<svta:PauseAdPresentation>` (§5.1.4). |
| `menu-ad` | Menu Ad | Non-linear / UI-embedded | Inside the smart-TV or streaming-app UI. CTV-only. |
| `squeezeback` | Squeezeback | Non-linear / content-resized | Primary content is shrunk; ad occupies the freed area. Sub-tokens MAY refine the rendering: `squeezeback-l-shape`, `squeezeback-frame`, `squeezeback-double-box`, `squeezeback-double-box-with-background`. |
| `overlay` | Overlay | Non-linear / over-content | Primary content is preserved at full size; ad is composited on top. Sub-tokens MAY refine: `overlay-corner`, `overlay-lower-third`. |
| `in-scene` | In Scene Ad | Non-linear / composited-into-content | Branded element inside the programming (virtual signage). Non-interactive by IAB definition. |
| `screen-saver-ad` | Screen Saver Ad | Non-linear / device-initiated overlay | Begins after a device-initiated inactivity timeout. |
| `companion-ad` | Companion Ad | Companion / wrap-around | Display only. Not generally available on CTV except as end card. |

A Broadcaster declaring `allowedLayouts` on a non-linear slot uses
tokens drawn from this enumeration (including documented
sub-tokens). An ADS returning a candidate form's `@layout` uses
tokens drawn from the same enumeration. The matching rule applied
by the Player is **exact-token enumeration**: an `allowedLayouts`
declaration admits only the tokens it lists literally; a parent
token (e.g. `overlay`) does not implicitly admit its sub-tokens
(e.g. `overlay-corner`). A Broadcaster who wants both
`overlay-corner` and `overlay-lower-third` lists both explicitly.

Interactivity envelopes (e.g. SIMID) and direct-response overlays
(e.g. composited QR codes) are referenced informatively by the IAB
document; this spec carries them at the per-creative payload level
(inside the form's asset), not at the slot or form metadata
level. They are not part of the chapter-5 syntax surface.

### 3.3 Abbreviations

- **ADS** — Ad Decision Server (§3.1).
- **CMAF** — Common Media Application Format (ISO/IEC 23000-19).
- **DASH** — Dynamic Adaptive Streaming over HTTP.
- **ERT** — Earliest Resolution Time (defined in §5.16 of the base
  specification; reused by this spec; see §5.1.1).
- **IAB** — Interactive Advertising Bureau (Tech Lab).
- **IOP URI** — Interoperability Point URI (DASH Annex F).
- **MPD** — Media Presentation Description (the DASH manifest).
- **SGAI** — Server-Guided Ad Insertion.
- **SPS** — Single-Period Static profile (§8.15 of the base
  specification).
- **SVTA** — Streaming Video Technology Alliance.
- **VAST** — Video Ad Serving Template (IAB Tech Lab). Referenced
  illustratively only (§6.6 and the annexes); this spec does not
  depend on any specific VAST version.

### 3.4 Device classes

This specification enumerates five device classes in order of
decreasing rendering capability. The classes capture only the
rendering features relevant to SGAI; they do not address codec
support, DRM, or network conditions, which are orthogonal.

| Device class | Video decoders | Image overlay on top of video | HTML overlay on top of video |
|--------------|----------------|-------------------------------|------------------------------|
| **D1** (top-tier) | 2 or more | Yes | Yes |
| **D2** | 2 | No | No (video-on-video composition only) |
| **D3** | 1 | Yes | Yes |
| **D4** | 1 | Yes | No |
| **D5** (worst case) | 1 | No | No |

The Player is the sole authority on its device class. The ADS
returns the same multi-form candidates to every viewer; the Player
picks per device (see §4.3).

## 4. Conformance

This specification is conformant against three actors. Each
actor's obligations are listed below. An implementation that
satisfies all obligations of its actor role conforms to this
edition of SGAI.

Throughout this chapter, RFC 2119 keywords (MUST, SHOULD, MAY)
carry the interoperability semantics of RFC 2119 / RFC 8174. Per
the drafting principle DP-2, normative obligations are stated as
positive requirements — the action the actor takes. The space
outside the positive obligation is implicitly out of scope of this
specification.

### 4.1 The three-actor contract

The architecture rests on a three-actor model:

- The **Broadcaster** owns the primary content and declares ad
  opportunities and their constraints in the main MPD.
- The **ADS** returns ad candidates when the Player resolves the
  slot's `@url`. The ADS does not enforce
  Broadcaster-declared constraints; it is free to return candidates
  that, taken together, would exceed the slot cap or use a layout
  the Broadcaster did not allow — enforcement is the Player's
  responsibility.
- The **Player** reads the MPD, parses slot constraints, queries
  the ADS, validates each candidate against the constraints,
  selects and composes the ad, and tracks the rendering.

Authority over the on-screen experience is held jointly by the
Broadcaster (who declares) and the Player (who enforces). The ADS
provides candidates but is not normatively bound by the slot
constraints. This separation lets a single ADS serve multiple
Broadcasters with heterogeneous policies, and lets the Player
guarantee the Broadcaster's constraints even when the ADS is an
external, non-audited service.

Every construct introduced by this specification is expressible
within this contract.

### 4.2 Broadcaster obligations

A conforming Broadcaster:

- **B-1**. Declares each ad opportunity as an `<Event>` inside an
  `<EventStream>` whose `schemeIdUri` matches one of the schemes
  listed in §2.1 (for non-linear slots) or in §5.16 of the base
  specification (for linear slots). The `<Event>` is placed inside
  a `<Period>` of the main MPD.
- **B-2**. Declares a maximum slot duration on every opportunity
  (linear or non-linear) as `@maxDuration` on the slot's
  scheme-specific child element, in `<EventStream>@timescale`
  units.
- **B-3**. Declares the admissible layouts on every non-linear
  opportunity via the `allowedLayouts` attribute on the
  scheme-specific child element (§5.1.3, §5.1.4). The token set is
  drawn from the layout vocabulary in §3.2.
- **B-4**. Expresses every construct introduced by this spec via
  the DASH 6th edition extension points enumerated below (the
  *carrier closure* set):
  - §5.2.1 foreign-namespace open content under the SVTA Ads WG
    namespace `urn:svta:dash:sgai:2026`. Used for new elements and
    attributes attached to baseline DASH containers.
  - §5.10 application-level Event Streams under year-pinned
    `schemeIdUri` values listed in §2.1. Used for slot declarations
    whose semantics are bound to a presentation-time window.
  - §5.8.4.8 / §5.8.4.9 vendor descriptors
    (`<EssentialProperty>` / `<SupplementalProperty>`). Used
    sparingly.
- **B-5**. Carries every non-AV (`text/html` / image) ad-creative
  asset URL via one of the three SGAI carriers in §5.3.1: the
  `@assetUrl` attribute on `<svta:RenderableAsset>` for one-shot
  fetch, an `<EventStream>` payload for presentation-time-aligned
  delivery, or a vendor descriptor (§5.8.4.x). The
  `<AdaptationSet>` / `<Representation>` axis is reserved for
  ISO-BMFF AV creatives, as bound by RFC 4337 through SPS (§8.15)
  and the CMAF profile (§8.12). This separation reflects the
  baseline DASH constraint, not a new SGAI rule.
- **B-6**. Authors the resolution URL on the slot's `@url`. The
  URL refers to the Broadcaster's ADS endpoint and MAY be
  parameterised via `<UrlParamInfo>` (§5.7).
- **B-7**. For hybrid linear + overlay slots, places two
  independent events at the same `presentationTime`: one on a
  linear scheme (§5.1.1 or §5.1.2) and one on the overlay scheme
  (§5.1.3). Each event declares its independent constraints and
  URL.

### 4.3 ADS obligations

A conforming ADS:

- **A-1**. Responds to the Player's resolution request with a
  resolution document that validates against the profile declared
  in its `MPD@profiles`. For linear slots, the response is a
  `ListMPD` (§8.14 of the base specification). For non-linear
  overlay or pause-trigger slots, the response is an Overlay
  Resolution Document declaring
  `urn:svta:dash:profile:sgai-overlay-list:2026` (§5.2.2).
- **A-2**. Populates every non-linear candidate with one or more
  renderable forms. The ADS MAY rank forms via the `@priority`
  attribute (§5.3.5).
- **A-3**. Restricts every form's creative-carrier media type to
  the admissible set defined in §3.2 cross-referenced with §5.3.2:
  `video` (MP4 ISO-BMFF per the DASH baseline mp4 constraint),
  `image` (IAB-defined image formats), or `html` (`text/html`).
- **A-4**. Carries ad-tracking beacons inside the resolution
  document (or its sub-MPDs) using the MPEG-DASH callback event
  scheme `urn:mpeg:dash:event:callback:2015` (§5.10.4.5 of the
  base specification). The placement of the tracking carrier (in
  the sub-MPD for ad-intrinsic timing; inside
  `<svta:RenderableAsset>` for slot-window timing) is governed by
  §5.5.2.
- **A-5**. For non-linear tracking, authors
  `<Event>@presentationTime` for each beacon **relative to the
  Broadcaster-declared slot window** — i.e., aligned to
  `@maxDuration` on the slot — when the tracking carrier is
  attached to the form via §5.5.3. Quartile beacons for a 20-second
  slot are authored at 5000, 10000, 15000, 20000 ms (per the ADS's
  chosen schedule). For tracking attached to a video form's
  sub-MPD, `<Event>@presentationTime` is relative to the ad's
  intrinsic timeline (§5.5.2), matching the linear baseline.
- **A-6**. Uses only layout tokens drawn from the §3.2 enumeration
  on every form's `@layout` attribute.

A conforming ADS is **not** required to:

- Enforce the slot's cap (R4.4). An ADS that returns candidates
  whose cumulative duration exceeds the cap is conforming; the
  Player enforces the cap (§4.4.3).
- Maintain a device-class matrix or a per-Player capability view
  (R5.4). The Player picks per device.

The ADS-side protocol (URL syntax, query parameters, request /
response payload between the ADS and any upstream ad-decisioning
backend) is not part of this specification's contract. The
ADS-Broadcaster bilateral invocation contract is established and
maintained out of band. This specification documents the
Player-visible interface only: the slot's `@url` (input) and the
resolution-document format (output).

A conforming ADS MAY also (non-normatively):

- Carry application-level metadata that has no native DASH
  carrier (e.g. `ClickThrough`, `AdSystem`, `AdTitle`,
  `UniversalAdId`) via vendor-namespaced extension elements per
  §5.6.
- Internally derive its response from a VAST 4.x upstream input
  (see §6.6 for an informative description of the conversion).
  This is internal to the ADS; conformant Players operate equally
  well against an ADS that does not use VAST at all.

### 4.4 Player obligations

A conforming Player:

#### 4.4.1 Graceful degradation

For every `<EventStream>` whose `schemeIdUri` it does not
implement, the Player ignores the entire stream and continues
playing primary content uninterrupted. No tracking beacon is
fired for the ignored slot. This behaviour is the *fall through*.
It is the worst-case outcome of every error condition in §8.1 and
the admissible response when the Player cannot honour the
opportunity.

#### 4.4.2 Constraint validation

For every opportunity whose scheme the Player implements:

- The Player parses the slot's constraints from the
  scheme-specific child element on the `<Event>` (§5.1).
- For each candidate returned by the ADS, the Player validates
  every renderable form against (a) the device's rendering
  capability (§3.4), (b) the Broadcaster-declared
  `allowedLayouts`, and (c) the admissible creative carriers
  (§3.2 cross-referenced with §5.3.2). A form is rendered only
  when it satisfies all three.

#### 4.4.3 Cap enforcement

The Player enforces the Broadcaster-declared slot cap on
**actual rendered length**, not declared length. When the
cumulative duration of accepted candidates would exceed the cap,
the Player stops rendering at the cap boundary, even if the stop
falls mid-ad. The Player keeps the slot bounded by the declared
cap regardless of ADS metadata or candidate count.

The Player MAY drop a candidate *before* playing it when its
declared duration would push the cumulative slot duration past the
cap ("drop before play"). When the Player accepts a candidate and
the candidate's actual rendered length exceeds the cap, the Player
trims at the cap boundary mid-rendering ("trim during play"). At
the trim boundary the Player stops firing tracking beacons.

#### 4.4.4 Ordering and dropping

For a non-linear opportunity with more than one candidate, the
Player plays the candidates in the order declared by the ADS,
except for candidates dropped because they have no renderable
form / layout combination (per §4.4.2) or because their declared
duration would push the cumulative slot duration past the cap
(per §4.4.3, "drop before play"). After applying these drops, the
Player preserves the relative order of the remaining candidates.

For a non-linear opportunity, the Player plays **at most one**
accepted candidate (the first admissible in declared order). Once
one candidate has been accepted and rendered, the slot is filled
and the remaining candidates are not evaluated. The full
selection algorithm — including this "stop after one accepted
candidate" termination — is specified in §7.3 step 5.

For a `ListMPD` returned for a linear slot, every Period plays in
declared order and the same drop-before-play / trim-during-play
arithmetic applies against the parent event's `@maxDuration`.

#### 4.4.5 Form selection within a candidate

When an accepted candidate carries more than one form, the Player
picks the form that maximises (a) renderability on the device,
(b) admissibility under the Broadcaster-declared
`allowedLayouts`, and (c) the ADS-supplied `@priority`. The
selection algorithm is specified in §7.3. The Player renders only
a form whose media type its device can render.

When no form on a candidate satisfies the three-way intersection,
the Player skips that candidate (fall through to the next
candidate, preserving order, or — when exhausted — to primary
content).

#### 4.4.6 Tracking

For every candidate accepted for rendering, the Player fires the
impression beacon at the instant the ad becomes visible to the
viewer. The Player SHOULD fire quartile beacons (25 %, 50 %,
75 %, 100 %) timed against the **Broadcaster-declared overlay
window** (`@maxDuration` on the slot) for non-linear ads, or
against the **ad's intrinsic duration** for linear ads. At the
trim boundary (§4.4.3) the Player stops firing remaining
quartile beacons.

Beacon transport is via the MPEG-DASH callback event scheme
`urn:mpeg:dash:event:callback:2015`: the Player issues an HTTP
GET to the URL embedded in each `<Event>` carried by an
`<EventStream>` of that scheme at the corresponding
`presentationTime`. Beacon failures are non-fatal: the Player
continues playback regardless.

#### 4.4.7 Single-form concurrent rendering

At any time *t* the Player presents at most one non-linear ad
form. When two non-linear opportunities overlap in time (e.g. an
overlay window and a pause-ad window), the Player serialises
their presentation per §4.4.8.

#### 4.4.8 Pause-ad lifecycle and priority

When a pause-ad opportunity (§5.1.4) is active and the viewer
pauses primary content inside its window of validity:

- The Player resolves the pause-ad slot's `@url` (or reuses a
  speculative pre-fetch per §8.5), receives an Overlay Resolution
  Document, and selects an admissible form per §4.4.5.
- The pause-ad form is rendered on top of the paused primary
  frame.
- When an overlay opportunity (§5.1.3) is also active at the same
  instant, the Player renders the pause-ad form on top and
  suspends the overlay rendering. The overlay's slot-window clock
  continues advancing on the primary timeline; the pause itself
  does not freeze the overlay's slot window.

On a pause-to-play transition by the viewer:

- The Player removes the rendered pause-ad form from the screen
  within one rendering frame.
- The Player stops firing pause-ad tracking beacons; beacons
  scheduled for relative times after the transition fall outside
  the pause-ad's active window and are out of scope.
- When an overlay slot is still active (its declared window has
  not expired), the Player restores the overlay rendering from
  where it was suspended.
- When the overlay slot's window expired during the pause, the
  Player keeps the overlay surface clear; the overlay is over.

The pause-ad always takes priority over a concurrently active
overlay during the pause; this priority is not
Broadcaster-configurable.

#### 4.4.9 Click-through interaction

For a candidate carrying a `<svta:Click>` child (§5.6.1), the
Player exposes the candidate's `@through` URL as an interactive
target on the rendered form. The interaction surface is
device-class dependent and follows the host environment's
interaction conventions:

- **Remote-controllable surfaces** (CTV, set-top boxes): the
  Player binds the form to the device's *select* / *OK* input.
  When the viewer activates it, the Player opens the `@through`
  URL via the device's URL-opening mechanism.
- **Pointer-driven surfaces** (web browsers, mobile devices in
  landscape Player): the Player binds the form to the standard
  click / tap event of the host environment.

When `@trackingUrl` is present on `<svta:Click>`, the Player
fires it as an HTTP GET on the interaction event, in addition to
opening the destination URL. The click-tracking beacon follows
the same fire-and-forget semantics as quartile beacons (§4.4.6).

#### 4.4.10 Unknown-namespace tolerance

The Player safely ignores unknown XML namespaces on extension
elements and attributes attached to MPD / `ListMPD` / Overlay
Resolution Document constructs (e.g. vendor-private metadata
under `urn:qualabs:sgai:2026`). Ignoring the construct does not
abort the candidate or the slot.

### 4.5 Cross-edition compatibility

A Player implementing edition *N* of this specification SHOULD
recognise constructs declared with the URIs of edition *N − 1*
and treat them per the backward-compatibility rules in edition
*N*. A construct whose semantics are unchanged between editions
MAY keep its URI; a construct whose semantics change is published
under a new year-pinned URI (§2.1).

### 4.6 Pre-roll non-linear scope

Pre-roll slots (i.e. opportunities at `presentationTime=0` on the
first `<Period>` of the main MPD) are linear-only in this
edition. A conforming Broadcaster's pre-roll opportunity is
declared via `<InsertPresentation>` (VOD) or
`<ReplacePresentation>` (live). The
`<svta:OverlayPresentation>` and `<svta:PauseAdPresentation>`
schemes are reserved for non-zero `presentationTime` in this
edition. A future edition MAY relax this, and the cross-edition
URI policy (§4.5) governs the transition.

## 5. Syntax

This chapter defines the XML constructs introduced by this
specification. Constructs reused without change from MPEG-DASH 6th
edition are cited but not restated; readers consult the base
specification for the full schema of those constructs.

Throughout this chapter the namespace prefix `svta:` denotes
`urn:svta:dash:sgai:2026`. The pre-existing DASH namespace is the
default, written without a prefix. The examples in this chapter
are illustrative; complete examples live in the annexes.

### 5.1 Main MPD events

The Broadcaster declares each ad opportunity as an `<Event>`
inside an `<EventStream>`. The scheme URI on the `<EventStream>`
identifies the opportunity type. The `<Event>`'s child element
carries the slot's constraints.

#### 5.1.1 `<InsertPresentation>` (linear, inherited)

`<InsertPresentation>` is defined by §5.16.3 of the base
specification and is reused unchanged here. It declares a linear
ad opportunity whose alternative presentation is inserted into
the main timeline at the event's `presentationTime`. When the
alternative ends, the main timeline resumes from the position
where it paused.

The carrying `<EventStream>` declares
`schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"`. The
attributes on `<InsertPresentation>` are defined verbatim in
§5.16.3 of the base specification.

NOTE (inherited DASH 6th issue): see chapter 2 for the
schema-vs-prose split on the URL attribute (`@url` in the prose,
`@uri` in the schema). This specification follows the prose name
`@url`.

Per §5.16.3 of the base specification, `<InsertPresentation>` is
admissible only on a `<MPD>` whose `@type="static"` (VOD content).
A Broadcaster authoring a live MPD uses `<ReplacePresentation>`
(§5.1.2) instead.

#### 5.1.2 `<ReplacePresentation>` (linear, inherited)

`<ReplacePresentation>` is defined by §5.16.4 of the base
specification and is reused unchanged here. It declares a linear
ad opportunity whose alternative presentation replaces a bounded
span of primary content. The main media time advances while the
ad plays, and at the end the Player resumes at the playhead
position determined by `@returnOffset`.

The carrying `<EventStream>` declares
`schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"`. The
attributes on `<ReplacePresentation>` are defined verbatim in
§5.16.4 of the base specification, including `@returnOffset`
(`xs:unsignedLong`, no default, expressed in
`<EventStream>@timescale` units; the offset, measured from the
slot's `presentationTime`, at which primary playback resumes
after the alternative completes) and `@startWithOffset`
(`xs:boolean`, default `false`; when `true`, the alternative is
started at the offset rather than from its origin).

The `@maxDuration` attribute on either `<InsertPresentation>` or
`<ReplacePresentation>` is the authoritative slot cap; the
Player enforces it per §4.4.3.

Per §5.16.5 of the base specification, the
`@earliestResolutionTimeOffset` and `@maxDuration` attributes on
both `<InsertPresentation>` and `<ReplacePresentation>` are
expressed in `<EventStream>@timescale` units (ticks, not
seconds). This unit choice matches the convention used by the
SGAI-side non-linear attributes in §5.1.3 / §5.1.4 and is
distinct from `<ImportedMPD>@earliestResolutionTimeOffset` which
is in seconds (§5.3.4 below; §5.3.2.6.1 of the base
specification).

#### 5.1.3 `<svta:OverlayPresentation>` (non-linear, new)

`<svta:OverlayPresentation>` declares a non-linear ad
opportunity whose ad is composited on top of, or alongside, the
primary content during the slot's window. The carrying
`<EventStream>` declares
`schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"`. The
`<Event>`'s `presentationTime` and `duration` define the overlay
window on the primary content timeline, expressed in
`<EventStream>@timescale` units.

**Justification (R8 / R9).** No baseline DASH 6th construct
declares a non-linear ad opportunity: §5.16 events are strictly
linear (alternative presentation replaces or pauses the main
timeline). The §5.10 application-level Event Stream mechanism
provides the carrier; this construct is the year-pinned scheme
URI on top of it. Reuse of `<InsertPresentation>` /
`<ReplacePresentation>` was rejected because their normative
semantics ("stops the playback of the current Media Presentation
till the end of the Alternative Media Presentation") explicitly
exclude the coexisting-overlay scenario.

##### Attributes

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `url` | Yes | xs:anyURI | — | Resolution URL the Player invokes to obtain the Overlay Resolution Document. The URL resolves to a document declaring `urn:svta:dash:profile:sgai-overlay-list:2026` (§5.2.2). |
| `earliestResolutionTimeOffsetTicks` | No | xs:unsignedLong | `0` | Offset, in `<EventStream>@timescale` units, subtracted from `presentationTime` to compute the Earliest Resolution Time (ERT). The Player picks a randomised instant between ERT and `presentationTime` at which to issue the resolution request. Renamed from the baseline `@earliestResolutionTimeOffset` because the baseline name on `<ImportedMPD>` (§5.3.2.6.1 of the base specification) carries seconds, while the SGAI-side attribute carries `<EventStream>@timescale` ticks. The `Ticks` suffix surfaces the unit difference at the call site. |
| `maxDuration` | Yes | xs:unsignedLong | — | Maximum overlay window length, in `<EventStream>@timescale` units. The Player enforces this cap on actual rendered length (§4.4.3). Semantics match §5.16.5 of the base specification; the attribute name is reused verbatim because the underlying semantics match. |
| `allowedLayouts` | Yes | xs:string | — | Space-separated list of layout tokens drawn from §3.2. Each token is one of the IAB-defined ad-type identifiers (or a documented sub-token). At least one token is present. |

##### Layout token semantics

The `allowedLayouts` value is a single attribute carrying a
space-separated list of tokens. The encoding matches the DASH
convention for token-list attributes (`@codecs`, `@profiles`).
A Broadcaster who needs to constrain the rendering to a single
layout lists one token (e.g.
`allowedLayouts="overlay-corner"`).

The matching rule is **exact-token enumeration**: a Broadcaster's
`allowedLayouts` declaration admits only the tokens it lists
literally. A parent token does not implicitly admit its
sub-tokens. A Broadcaster who wants to admit, for example, both
`overlay-corner` and `overlay-lower-third` lists both
explicitly; listing only `overlay` admits only the bare `overlay`
token.

The admissible tokens on `<svta:OverlayPresentation>` are
constrained per §5.3.3 below to the overlay-family and
content-resize-family tokens; pause-ad-family,
screen-saver-family, and companion-family tokens are scoped to
their own scheme (§5.1.4) or out of scope for this edition (see
§1.2).

##### Children

The element has no required children. A Broadcaster MAY attach
application-defined vendor-namespaced children (e.g. campaign
linkage hints); the Player handles unknown namespaces per
§4.4.10.

##### Legacy Player behaviour

A Player that does not implement
`urn:svta:dash:event:sgai-overlay:2026` ignores the entire
`<EventStream>` and continues playing primary content. The
`<svta:OverlayPresentation>` element and its attributes are
discarded together with the unknown scheme; legacy Players never
reach the `@url` resolution step. This satisfies the
backward-compatibility per-construct checklist (carrier (b) =
§5.10 Event Stream; legacy walk-through: stream skipped at
`schemeIdUri` mismatch; required-sibling check: no baseline
sibling depends on this element; ignore semantics: §5.10 +
§5.2.1 NOTE 2).

##### Worked example (short, illustrative)

```xml
<EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026" timescale="1000">
  <Event id="201" presentationTime="120000" duration="20000">
    <svta:OverlayPresentation
        xmlns:svta="urn:svta:dash:sgai:2026"
        url="https://ads.example.com/decision/overlay-mid120"
        earliestResolutionTimeOffsetTicks="10000"
        maxDuration="20000"
        allowedLayouts="overlay-corner overlay-lower-third"/>
  </Event>
</EventStream>
```

Complete examples live in Annex C (UC-03), Annex D (UC-04), and
Annex E (UC-05).

#### 5.1.4 `<svta:PauseAdPresentation>` (non-linear, new)

`<svta:PauseAdPresentation>` declares a **pause-trigger window**:
during this window, when the viewer pauses the primary content,
the Player MAY render an ad on top of the paused frame. The
carrying `<EventStream>` declares
`schemeIdUri="urn:svta:dash:event:sgai-pause-trigger:2026"`. The
`<Event>`'s `presentationTime` and `duration` define the
**window of validity** on the primary content timeline; outside
this window a viewer pause produces no ad opportunity.

**Justification (R8 / R9).** Reuse of `<svta:OverlayPresentation>`
was rejected because the pause-trigger semantics (slot activated
on viewer interaction, not on playhead crossing) require a
different scheme URI on the carrying `<EventStream>` for legacy
Players to discriminate them cleanly. The two schemes share most
of their syntactic surface intentionally.

##### Attributes

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `url` | Yes | xs:anyURI | — | Resolution URL the Player invokes when the viewer pauses inside the window. The URL resolves to an Overlay Resolution Document (§5.2.2). |
| `maxDuration` | Yes | xs:unsignedLong | — | Maximum display duration of the pause ad, in `<EventStream>@timescale` units, applied from the moment the ad becomes visible until automatic dismissal. The Player enforces this cap on actual rendered length (§4.4.3). |
| `allowedLayouts` | Yes | xs:string | — | Space-separated list of layout tokens. The canonical token for this scheme is `pause-ad`; `overlay-*` tokens MAY also be admissible when the Broadcaster wants to permit the same creative templates as a coexisting overlay. At least one token is present. |

##### Legacy Player behaviour

A Player that does not implement
`urn:svta:dash:event:sgai-pause-trigger:2026` ignores the entire
`<EventStream>`. The viewer's pause then produces no ad, and the
paused frame remains on screen until the viewer resumes —
exactly as if the proposal were absent.

##### Worked example (short, illustrative)

```xml
<EventStream schemeIdUri="urn:svta:dash:event:sgai-pause-trigger:2026" timescale="1000">
  <Event id="301" presentationTime="60000" duration="600000">
    <svta:PauseAdPresentation
        xmlns:svta="urn:svta:dash:sgai:2026"
        url="https://ads.example.com/decision/pause-ad"
        maxDuration="30000"
        allowedLayouts="pause-ad"/>
  </Event>
</EventStream>
```

Complete example lives in Annex E. A worked composition of an
overlay window crossing a pause-ad window lives in Annex H.

#### 5.1.5 Co-located events (hybrid linear + overlay)

A Broadcaster declares a *hybrid* slot — a linear ad takes over
the screen and a non-linear overlay is composited on top of it
during the same break — as **two independent events at the same
`presentationTime`**: one on a linear scheme (§5.1.1 or §5.1.2)
and one on the overlay scheme (§5.1.3). The Player resolves the
two events independently against the ADS (two separate
resolution requests against the two URLs).

The two events MAY declare different `allowedLayouts`: the
overlay portion of a hybrid slot is typically restricted to
non-overlapping layouts (e.g. `overlay-lower-third`,
not `squeezeback-*`, because the underlying content is itself an
ad).

When the two declared windows differ in length, the **shorter
window governs the overlay's display**: the overlay is dismissed
at whichever of its own `maxDuration` or the underlying linear
slot's end comes first. (An overlay window longer than the linear
window would imply the overlay continues over primary content
after the linear ad completes; that is an authoring error and
the spec's enforcement is clamp-to-linear-end.)

### 5.2 Resolution documents

The Broadcaster's event carries a `@url` the Player resolves
against the ADS. The ADS replies with a *resolution document*.
This spec defines two profiles: the linear `ListMPD` (inherited
unchanged) and a new Overlay Resolution Document.

#### 5.2.1 Linear `ListMPD` (`urn:mpeg:dash:profile:list:2024`)

The linear resolution document is `ListMPD` as defined by §8.14
of the base specification. It is reused unchanged here.

A linear `ListMPD` is a *playlist of MPDs*: each `<Period>`
references a per-ad sub-MPD via `<ImportedMPD>`, and the Player
plays the periods back-to-back in declared order. The sub-MPDs
are SPS-conformant per §8.15 (bound by §5.3.2.6) and therefore
carry video creative on `video/mp4` Representations.

##### Period-level attributes (reused from §8.14)

The Period-level attributes used by SGAI are summarised below
for convenience; the authoritative schema is §8.14 of the base
specification.

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `id` | Yes | xs:string | — | Stable identifier for the ad slot inside the pod. Used by the Player for tracking. |
| `duration` | Yes (in ListMPD) | xs:duration | — | Declared duration of this ad slot. Drives the Player's cap arithmetic against the parent event's `@maxDuration`. |

##### Period-level children

| Element | Cardinality | Description |
|---------|-------------|-------------|
| `<ImportedMPD>` | 1 (typical) | Reference to the per-ad sub-MPD by URI; SPS-conformant. |

Complete linear examples live in Annexes A, B, and F.

#### 5.2.2 Overlay Resolution Document (`urn:svta:dash:profile:sgai-overlay-list:2026`)

The non-linear resolution document declares
`MPD@profiles="urn:svta:dash:profile:sgai-overlay-list:2026"` (in
addition to any inherited DASH profiles). Its root is `<MPD>` so
DASH-aware tooling can parse the envelope. The candidate-and-form
content lives under a new `<svta:OverlayList>` child element
placed inside a single `<Period>` of the document; this preserves
the §5.3.2.2 Table 4 rule of "every non-zero-duration `<Period>`
contains at least one `<AdaptationSet>`" by making the document's
`<Period>@duration="PT0S"`.

**Justification (R8 / R9).** `ListMPD` was considered as the
non-linear carrier (it is a known DASH-conformant resolution
document) but was rejected: `ListMPD`'s normative semantics is
*play every Period in order*, which does not match the non-linear
contract of *select at most one candidate*. A new profile URI
distinguishes the two semantics at the response parsing layer
without re-using `ListMPD`'s identifier for an incompatible
meaning. The `<svta:OverlayList>` payload uses §5.2.1
foreign-namespace open content under the SVTA Ads WG namespace
(DR-2 carrier), so no new authoring rule beyond the year-pinned
profile URI is required.

##### Document shape

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S">
  <Period id="overlay-resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="..." priority="...">
        <svta:RenderableAsset .../>
        <svta:RenderableAsset .../>
        <!-- ... more forms ... -->
      </svta:Candidate>
      <svta:Candidate id="..." priority="...">
        <!-- ... -->
      </svta:Candidate>
      <!-- ... more candidates ... -->
    </svta:OverlayList>
  </Period>
</MPD>
```

The document is **not** a `ListMPD`. A reader who confuses the
two will not run aground on parsing — the SVTA profile URI is
declared explicitly — but the semantics differ: `ListMPD`
prescribes "play all periods in order", whereas the Overlay
Resolution Document prescribes "for each candidate the Player
accepts, render at most one form; for the slot, render at most
one candidate at a time (per §4.4.7)".

The `<Period>@duration="PT0S"` choice is intentional: it lets the
non-linear resolution document live inside an SPS-shaped envelope
(single `<Period>`, well-formed `<MPD>`) without triggering the
§5.3.2.2 Table 4 "Period must contain at least one
AdaptationSet" requirement for non-zero-duration Periods, while
still parsing cleanly as a DASH document.

##### `<svta:OverlayList>` children

| Element | Cardinality | Description |
|---------|-------------|-------------|
| `<svta:Candidate>` | 1..N | Ordered list of candidates returned by the ADS. The Player attempts them in declared order, skipping any that have no renderable / admissible form. |

##### `<svta:Candidate>` attributes

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `id` | Yes | xs:string | — | Identifier for tracking and diagnostics. Stable across the resolution document. |
| `adId` | No | xs:string | — | ADS-internal ad identifier (analogue of VAST's `@id`). Informational; the Player MUST NOT key behaviour off it. |
| `priority` | No | xs:nonNegativeInteger | `0` | Candidate-level ordering hint emitted by the ADS. Informational; the Player honours the declared candidate order (§4.4.4) and uses `@priority` only as a tie-breaker hint within a candidate's forms (§5.3.5). |

##### `<svta:Candidate>` children

| Element | Cardinality | Description |
|---------|-------------|-------------|
| `<svta:RenderableAsset>` | 1..N | Forms available for this candidate. At least one form is present; the Player picks at most one per §4.4.5. |
| `<svta:Click>` | 0..1 | Application-level click-through metadata (§5.6.1). Optional. |
| `<svta:UniversalAdId>` | 0..1 | Application-level Universal Ad ID metadata (§5.6.2). Optional. |
| Vendor-namespaced extensions | 0..N | Any other application-level metadata MAY be attached under a vendor namespace; the Player ignores unknown namespaces safely. |

### 5.3 `<svta:RenderableAsset>`

`<svta:RenderableAsset>` is the form-level construct on a
non-linear candidate. Each form declares a media type, a layout,
a declared duration, an optional priority, and the asset
location. The Player's selection algorithm (§7.3) consumes
forms as the unit of validation.

#### 5.3.1 Attributes

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `mediaType` | Yes | xs:string | — | The form's creative-carrier type. Enum constrained by §5.3.2. |
| `layout` | Yes | xs:string | — | Layout token. Enum constrained by §5.3.3 (a subset of §3.2). |
| `duration` | Yes | xs:duration | — | Declared length of the form, in seconds (the standard `xs:duration` unit). Drives the Player's drop-before-play arithmetic (§4.4.3). For `image` and `html` forms whose intrinsic length is undefined, `@duration` is the *intended display duration*; the Player MAY trim it earlier when the slot cap is reached. |
| `priority` | No | xs:nonNegativeInteger | `0` | ADS-supplied ranking inside the candidate. Higher means more preferred. Consumed by the Player's form-selection algorithm (§7.3) when more than one form is admissible. |
| `assetUrl` | Conditional | xs:anyURI | — | For `image` and `html` forms, the absolute HTTP(S) URL of the creative asset. Present when `@mediaType` is `image` or `html`. Absent when `@mediaType` is `video` (the video creative is carried by a child `<ImportedMPD>`; see §5.3.4). |

#### 5.3.2 Enum: `@mediaType`

| Enum value | Description |
|------------|-------------|
| `video` | Video form. The creative is carried by a child `<ImportedMPD>` referencing an SPS-conformant sub-MPD (§5.3.4). The sub-MPD's Representations carry `video/mp4` (and optionally `audio/mp4`) per the DASH baseline. |
| `image` | Image form. The creative is at `@assetUrl`; its Content-Type is one of the IAB-defined image formats (`image/png`, `image/jpeg`, `image/gif`). |
| `html` | HTML form. The creative is at `@assetUrl`; its Content-Type is `text/html`. The HTML document MAY contain inline `<script>` under HTML5 semantics; the script runs inside the device's HTML capability contract, not as a separate carrier. |

A value outside this enumeration is non-conformant. A Player
encountering such a value skips the form (§4.4.5); the candidate
is treated as if the offending form were absent.

#### 5.3.3 Enum: `@layout`

The `@layout` value is a single token drawn from the §3.2
enumeration. The admissibility set varies by slot scheme:

| Slot scheme | Admissible `@layout` tokens |
|-------------|-----------------------------|
| `urn:svta:dash:event:sgai-overlay:2026` (`<svta:OverlayPresentation>`) | `overlay`, `overlay-corner`, `overlay-lower-third`, `squeezeback`, `squeezeback-l-shape`, `squeezeback-frame`, `squeezeback-double-box`, `squeezeback-double-box-with-background`, `in-scene`, `menu-ad` |
| `urn:svta:dash:event:sgai-pause-trigger:2026` (`<svta:PauseAdPresentation>`) | `pause-ad`, `overlay`, `overlay-corner`, `overlay-lower-third` |

A form whose `@layout` is admissible by the spec but not by the
Broadcaster's `allowedLayouts` declaration on the slot is
rejected by the Player (§4.4.2); see §4.4.5 for the selection
algorithm.

#### 5.3.4 `<ImportedMPD>` child (for `mediaType="video"`)

When `@mediaType="video"`, the form carries the creative via a
child `<ImportedMPD>` element. The element's attributes are
defined verbatim in §5.3.2.6 of the base specification; the
relevant ones are `@uri` (the sub-MPD URL) and
`@earliestResolutionTimeOffset` (seconds, per §5.3.2.6.1 of the
base specification — note the unit difference from the SGAI-side
`@earliestResolutionTimeOffsetTicks` in §5.1.3 above).

The sub-MPD is SPS-conformant (§8.15 of the base specification).
Its `<AdaptationSet>` / `<Representation>` carry the video
creative on the AdaptationSet axis; the `@mimeType` on every
Representation is `video/mp4` / `audio/mp4` / `application/mp4`
per §7.3 / RFC 4337.

This is the only `@mimeType` axis a non-linear ad uses. Image
and HTML forms carry the asset on `@assetUrl` per §5.3.1 — that
keeps the non-AV asset URLs outside the AdaptationSet axis,
where the SPS / CMAF inheritance binds `@mimeType` to RFC 4337.

NOTE: Although this construct re-uses the baseline DASH
`<ImportedMPD>` XML shape, it is interpreted under SGAI semantics
defined in this section, not under the baseline §5.3.2.6
placement rules of the base specification. A baseline DASH parser
following the §5.2.1 fallback model strips the entire
`<svta:RenderableAsset>` subtree (together with its
`<ImportedMPD>` child) and never reaches this element; only
SGAI-aware Players parse it.

#### 5.3.5 Priority semantics

`@priority` is informational. The Player consults it when
choosing among admissible forms but MAY override it (e.g. when
the highest-priority admissible form's layout fails device-class
capability). `@priority` does not change the candidate-level
order returned by the ADS — that order is binding (§4.4.4).

### 5.4 Sub-MPD (SPS profile)

A sub-MPD reached via `<ImportedMPD>` from any of:

- a `ListMPD` Period (linear),
- a non-linear video-form `<svta:RenderableAsset>`,

conforms to the SPS profile (§8.15 of the base specification). It
is a single-Period document whose Representations carry only the
RFC 4337 MIME types. The `<Period>@duration` declares the ad's
intrinsic length.

The sub-MPD carries the ad's tracking carrier inline (§5.5).
Application-level metadata (e.g. `<svta:Click>`,
`<svta:UniversalAdId>`) MAY be attached to the sub-MPD root
under a vendor namespace; the Player handles unknown namespaces
per §4.4.10.

A sub-MPD is illustrated in Annexes A, B, C (Candidate 1
Form 1.1), and F.

#### 5.4.1 Period duration reconciliation

For a video-form `<svta:RenderableAsset>`, two duration values
appear in the resolution flow:

- `@duration` on `<svta:RenderableAsset>` (§5.3.1): the ADS's
  declared duration for the form, in `xs:duration`.
- `<Period>@duration` inside the sub-MPD reached via
  `<ImportedMPD>`: the sub-MPD's intrinsic ad duration.

The two SHOULD agree. When they disagree, the Player treats the
sub-MPD's `<Period>@duration` as authoritative for actual-length
arithmetic (§4.4.3, trim during play) and the
`<svta:RenderableAsset>@duration` as a hint used only for
drop-before-play (§4.4.3). The ADS SHOULD keep the two values
aligned.

### 5.5 Tracking carrier

This specification reuses MPEG-DASH 6th edition's callback event
scheme `urn:mpeg:dash:event:callback:2015` (§5.10.4.5 of the base
specification) for all ad-tracking beacons. No new tracking
scheme is introduced.

#### 5.5.1 Carrier shape

A tracking beacon is encoded as an `<Event>` inside an
`<EventStream>` whose
`schemeIdUri="urn:mpeg:dash:event:callback:2015"`. The
`<Event>`'s `text()` is the beacon URL the Player issues an HTTP
GET against at the `<Event>`'s `presentationTime` within the
carrying `<EventStream>@timescale`.

```xml
<EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1" timescale="1000">
  <Event presentationTime="0"     id="b-impression">https://tracker.example.com/impression?ad=c1f1</Event>
  <Event presentationTime="0"     id="b-start">https://tracker.example.com/start?ad=c1f1</Event>
  <Event presentationTime="5000"  id="b-q1">https://tracker.example.com/firstQuartile?ad=c1f1</Event>
  <Event presentationTime="10000" id="b-q2">https://tracker.example.com/midpoint?ad=c1f1</Event>
  <Event presentationTime="15000" id="b-q3">https://tracker.example.com/thirdQuartile?ad=c1f1</Event>
  <Event presentationTime="20000" id="b-complete">https://tracker.example.com/complete?ad=c1f1</Event>
</EventStream>
```

#### 5.5.2 Where the tracking carrier lives

The tracking carrier's location is the *timing reference* for
the beacons:

| Carrier location | Timing reference | Use |
|------------------|------------------|-----|
| Inside a `video` form's SPS sub-MPD (§5.4) | The sub-MPD's `<Period>` timeline (i.e. the ad's intrinsic timeline) | Linear ad tracking; non-linear `video`-form tracking that quartile-aligns to the ad's intrinsic duration. |
| Inside the Overlay Resolution Document, as a child of `<svta:RenderableAsset>` (§5.5.3) | The Broadcaster-declared overlay window (i.e. `@maxDuration` on the slot) | Non-linear ad tracking that quartile-aligns to the overlay window, not the ad. This is the **preferred** placement for non-linear quartile beacons (§4.4.6). |

For non-linear `image` and `html` forms (which have no SPS
sub-MPD), the tracking carrier is attached to the form itself in
the Overlay Resolution Document (§5.5.3).

#### 5.5.3 Tracking for non-video forms

For `image` and `html` forms, the `<svta:RenderableAsset>` MAY
carry an `<EventStream>` child of scheme
`urn:mpeg:dash:event:callback:2015`. The
`<EventStream>@timescale` governs the unit; the
`<Event>@presentationTime` is interpreted relative to the moment
the form becomes visible (i.e. the impression instant).

NOTE: Although this construct re-uses the baseline DASH
`<EventStream>` XML shape, it is interpreted under SGAI semantics
defined in this section, not under the baseline §5.10.2.1
semantics of the base specification. The baseline rule places
`<EventStream>` as a direct child of `<Period>` with
`<Event>@presentationTime` measured relative to the carrying
Period's start; the SGAI placement here is inside
`<svta:RenderableAsset>` with `<Event>@presentationTime` measured
relative to the form-visible instant. A baseline DASH parser
following the §5.2.1 fallback model strips the entire
`<svta:RenderableAsset>` subtree (together with its
`<EventStream>` child) and never reaches this element; only
SGAI-aware Players parse it. This re-interpretation is admissible
because the `<EventStream>` lives inside a foreign-namespace
parent (DR-2 / DR-3) — legacy parsers discard it entirely.

```xml
<svta:RenderableAsset xmlns:svta="urn:svta:dash:sgai:2026"
                      mediaType="image" layout="overlay-corner"
                      duration="PT20S" priority="40"
                      assetUrl="https://ads.example.com/c1/banner.png">
  <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" timescale="1000">
    <Event presentationTime="0"     id="b-impression">https://tracker.example.com/impression?ad=c1f3</Event>
    <Event presentationTime="5000"  id="b-q1">https://tracker.example.com/firstQuartile?ad=c1f3</Event>
    <Event presentationTime="10000" id="b-q2">https://tracker.example.com/midpoint?ad=c1f3</Event>
    <Event presentationTime="15000" id="b-q3">https://tracker.example.com/thirdQuartile?ad=c1f3</Event>
    <Event presentationTime="20000" id="b-complete">https://tracker.example.com/complete?ad=c1f3</Event>
  </EventStream>
</svta:RenderableAsset>
```

#### 5.5.4 Beacon timing

A Player rendering a non-linear ad fires the impression beacon
at `presentationTime="0"` relative to the moment the form
becomes visible. The Player SHOULD fire quartile beacons at
25 %, 50 %, 75 %, 100 % of the **Broadcaster-declared overlay
window** (`@maxDuration` on the slot), not at 25 %, 50 %, 75 %,
100 % of the ad's intrinsic duration when the two differ. When
the slot cap is hit before all quartiles fire ("trim during
play", §4.4.3), the Player stops firing remaining quartile
beacons at the trim boundary.

For linear ads, the timing reference is the ad's intrinsic
timeline (the sub-MPD's `<Period>` timeline). Quartile beacons
fire at 25 %, 50 %, 75 %, 100 % of the ad's intrinsic duration.

### 5.6 Application-level metadata

DASH 6th edition defines no native carrier for the
application-level VAST metadata that ADSs commonly need to emit:
`<ClickThrough>`, `<ClickTracking>`, `<AdSystem>`, `<AdTitle>`,
`<UniversalAdId>`. This specification carries those metadata via
vendor-namespaced child elements of `<svta:Candidate>` (or,
equivalently, of an inline sub-MPD's `<MPD>` root for linear
ads).

This spec normatively defines two such elements as common
shorthand. Any other application metadata MAY be carried via a
vendor-private namespace (e.g. `urn:qualabs:sgai:2026`); the
Player handles unknown namespaces per §4.4.10.

#### 5.6.1 `<svta:Click>`

Carries click-through and click-tracking URLs for the candidate.

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `through` | Yes | xs:anyURI | — | The destination URL opened when the viewer interacts with the ad. The Player's interaction binding follows §4.4.9. |
| `trackingUrl` | No | xs:anyURI | — | Beacon URL fired on viewer interaction. Fire-and-forget HTTP GET, same shape as a callback-scheme beacon. |

#### 5.6.2 `<svta:UniversalAdId>`

Carries the IAB Universal Ad ID for the candidate.

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `idRegistry` | Yes | xs:string | — | The registry that issued the ID (e.g. `ad-id.org`). |
| `value` | Yes | xs:string | — | The ID value itself. |

#### 5.6.3 Other application-level metadata

Any other application metadata (e.g. `<AdSystem>`, `<AdTitle>`,
custom campaign linkage attributes) is carried via a
vendor-private namespace (e.g. `urn:qualabs:sgai:2026`). The
Player handles unknown namespaces per §4.4.10; ADSs and
Broadcasters relying on consumer-side processing of this metadata
do so out of band.

#### 5.6.4 Legacy-Player behaviour

The `<svta:Click>`, `<svta:UniversalAdId>`, and any
vendor-private metadata elements are foreign-namespace children
of baseline DASH containers. Legacy Players discard them together
with their subtree per §5.2.1 NOTE 2 of the base specification.
They do not interfere with primary playback.

### 5.7 URL parameterisation

The MPD-level URL-parameterisation descriptor (§I.4 of the base
specification, scheme `urn:mpeg:dash:urlparam:2025`) is reused
unchanged. Per §I.3.1 of the base specification, the descriptor
is declared by a pair of sibling elements: an empty
`<EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025"/>`
acts as the scheme flag, and one or more `<UrlParamInfo>` elements
— defined directly in the core MPD namespace
`urn:mpeg:dash:schema:mpd:2011` — appear as direct children of
`<MPD>`, `<Period>`, `<AdaptationSet>`, `<Preselection>`, or
`<EventStream>`. The Broadcaster MAY declare query parameters to
append to the resolution-request URL via the descriptor's
`@queryTemplate`, with `@includeInRequests` scoping the descriptor
to the request kind (e.g. `altmpd` for both linear and non-linear
ADS resolution).

This spec uses the same descriptor for non-linear resolution
URLs `[inferred]`. The vocabulary substitution semantics of §I.4
are general enough to cover both linear `ListMPD` and non-linear
Overlay Resolution Document URLs; the spec relies on that
generality and does not introduce a new parameterisation
mechanism.

## 6. Interfaces

This chapter specifies the runtime interactions between actors:
who calls whom, with what transport, with what payload, and what
the error semantics are. Every interface in this chapter is
HTTPS in production.

### 6.1 Broadcaster → Player (main MPD)

The Broadcaster's main MPD is the source of every ad opportunity.
The Player fetches it as a regular DASH MPD via HTTP GET. The
MPD's SGAI events (linear and non-linear) are discovered by
parsing the `<EventStream>` declarations against the scheme URIs
listed in §2.1 and in §5.16 of the base specification.

The Player consumes the MPD via a pull (HTTP GET) at session
start, and refreshes it on `@minimumUpdatePeriod` for live
content.

### 6.2 Player → ADS (resolution request)

The Player issues an HTTP GET to the `@url` declared on the
slot's `<InsertPresentation>` / `<ReplacePresentation>` /
`<svta:OverlayPresentation>` / `<svta:PauseAdPresentation>`. The
URL MAY be augmented at runtime by query parameters declared via
`<UrlParamInfo>` (§5.7).

The Player issues the request at a randomised instant between
the Earliest Resolution Time (ERT = `presentationTime` minus
`@earliestResolutionTimeOffset` for linear, or
`presentationTime` minus `@earliestResolutionTimeOffsetTicks` for
non-linear overlays) and the slot's `presentationTime`. For
pause-trigger slots, the ERT is the moment the viewer pauses;
the request fires immediately on pause inside the window of
validity.

The response carries a resolution document: a `ListMPD` for
linear slots, an Overlay Resolution Document for non-linear
slots. The HTTP status code semantics are:

| Status | Player behaviour |
|--------|------------------|
| 200, body is a parseable, schema-valid resolution document | Proceed with §6.3. |
| 200, body is empty (zero candidates / zero `<Period>`s) | Fall through; no tracking beacons fired. |
| 200, body is unparseable or schema-invalid | Treat as if no resolution document was returned; fall through. |
| 4xx / 5xx / timeout / DNS failure | Fall through. Player MAY retry within the slot's resolution window; once the window closes, abandon. |
| 200, response arrives past `presentationTime` for linear or past the overlay window's end for non-linear | Discard the late response; fall through. |

### 6.3 ADS → Player (resolution response)

The ADS's response is the resolution document. For non-linear
slots the document is structured per §5.2.2; for linear slots
per §5.2.1.

The ADS uses the §3.2 layout vocabulary and the §5.3.2 mediaType
enumeration; tokens outside these enumerations cause the Player
to skip the offending form (§4.4.5).

The ADS MAY return:

- an empty document (no candidates / no Periods) — a *no-fill*
  signal. This is conforming behaviour; the Player falls through.
- a single candidate with a single form — the minimum
  conforming non-linear response.
- multiple candidates each with multiple forms — the typical
  shape, exercising the Player's selection algorithm (§7.3).

### 6.4 Player → Ad CDN (segment fetch)

For `video`-form candidates, the Player fetches the SPS sub-MPD
referenced via `<ImportedMPD>` and the segments it declares.
The CDN is whatever the ADS configured; the Player has no view
into the choice. Transport is HTTPS; error semantics follow
DASH-IF segment-level retry guidelines and are not restated
here.

For `image` and `html` forms, the Player fetches the asset at
`@assetUrl` via HTTP GET. When the fetch fails, the form fails to
render; the Player skips the form and re-evaluates the candidate
per §4.4.5.

### 6.5 Player → Tracking endpoint (beacon fire)

The Player fires HTTP GETs against the URLs embedded in the
tracking `<Event>` elements (§5.5). The body of the response is
discarded; failures are non-fatal and do not abort the candidate
or the slot.

### 6.6 ADS internal: VAST → resolution document (non-normative)

The Player-facing interface this spec defines is HTTP +
`ListMPD` / Overlay Resolution Document. The de-facto industry
ad-decisioning protocol on the upstream side is **IAB VAST 4.x**.
ADSs in production typically receive ad responses as VAST from
one or more upstream sources (DSPs, ad servers, exchanges) and
transform them into the resolution document the Player expects.
The transformation is illustrated informatively in the table
below; conformant implementations are VAST-version-agnostic and
operate against an ADS that does not use VAST at all.

For convenience, the standard VAST 4.x → SGAI mapping is sketched
below for the **linear** case (`ListMPD` target):

| VAST 4.x source | Target in linear resolution document |
|-----------------|--------------------------------------|
| `<Ad>` (Inline) | One `<Period>` containing one `<ImportedMPD>` entry in the `ListMPD`. |
| `<Ad>` (Wrapper) | Resolved recursively until an `<Ad>` (Inline) is reached. |
| `<Creatives>/<Linear>/<Duration>` | `Period@duration` on the `ListMPD` Period and `Period@duration` on the sub-MPD. |
| `<MediaFile>` (per encoding) | One `<Representation>` inside the sub-MPD's `<AdaptationSet>`. |
| `<TrackingEvents>/<Tracking event="...">` | Inline `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015` inside the sub-MPD, with one `<Event>` per VAST tracking event timed at the corresponding offset. |
| `<Impression>` | Callback event at offset `0` inside the sub-MPD. |
| `<ClickThrough>` / `<ClickTracking>` | Carried as a `<svta:Click>` child of the candidate (non-linear) or as a vendor-namespaced attribute on the `<ImportedMPD>` (linear). |
| `<UniversalAdId>` | Carried as a `<svta:UniversalAdId>` child of the candidate. |
| `<AdSystem>`, `<AdTitle>`, `<Advertiser>` | Vendor-namespaced attributes / elements on `<svta:Candidate>` or on the sub-MPD root. |

For the **non-linear** case, the VAST 4.x source has no direct
analogue (VAST 4.x defines `<NonLinear>` but not the multi-form
candidate / multi-layout abstraction this spec uses). The ADS
adapter constructs `<svta:Candidate>` and its
`<svta:RenderableAsset>` children from the VAST `<NonLinear>`,
`<Companion>`, and custom-template entries based on its own
decisioning logic; this is an ADS-internal concern (see §4.3 for
the actor boundary).

## 7. Expected behaviour

This chapter specifies normatively what each actor does at
runtime for each opportunity type. The annexes carry the heavy
walk-throughs and full XML; this chapter is the normative
behavioural envelope.

### 7.1 Broadcaster behaviour

The Broadcaster authors the main MPD. For each ad opportunity:

- Chooses the opportunity type (linear insert, linear replace,
  overlay, pause-trigger) and the corresponding scheme URI
  (§5.1).
- Decides the slot's `presentationTime`, `duration`,
  `@earliestResolutionTimeOffset` (linear) /
  `@earliestResolutionTimeOffsetTicks` (non-linear), and
  `@maxDuration`.
- For non-linear slots, declares `allowedLayouts` (a subset of
  §3.2).
- Authors the resolution URL on the slot's `@url`. The URL
  refers to the Broadcaster's ADS endpoint and MAY be
  parameterised via `<UrlParamInfo>` (§5.7).
- For hybrid linear + overlay slots, places two co-located
  events on the timeline at the same `presentationTime`
  (§5.1.5), each declaring its independent constraints and URL.

### 7.2 ADS behaviour

The ADS receives the Player's resolution request and returns a
resolution document.

For **linear** slots:

- Applies its decisioning logic (targeting, frequency capping,
  brand safety, competitive separation) to its ad pool.
- Assembles an ordered sequence of one or more ads into a
  `ListMPD`, with one `<Period>` per ad and one `<ImportedMPD>`
  per Period pointing at the per-ad sub-MPD.
- Embeds tracking events inside each sub-MPD (§5.5).

For **non-linear** slots:

- Applies the same decisioning logic to its ad pool.
- For each chosen candidate, builds one `<svta:Candidate>` and
  populates it with one or more `<svta:RenderableAsset>` forms.
- Each form declares its `@mediaType` (`video` / `image` /
  `html`), `@layout` (token in §3.2), `@duration`, optional
  `@priority`, and the asset location (`@assetUrl` for
  non-video forms, `<ImportedMPD>` child for video forms).
- Embeds tracking events either inside the video sub-MPD or as
  a child of `<svta:RenderableAsset>` (§5.5.2). Beacon
  `<Event>@presentationTime` values for non-linear tracking are
  authored relative to the slot window per §A-5 (§4.3) when
  carried on `<svta:RenderableAsset>`.

The ADS does not:

- Cap its returned candidates' total duration against the slot's
  cap (the Player enforces).
- Filter forms by device class (the Player picks).

### 7.3 Player validation and selection

The Player's per-slot algorithm:

1. **Discovery.** Parse the main MPD. For each `<Event>` whose
   scheme URI matches one the Player implements, queue an
   activation at the corresponding ERT (or, for pause-trigger,
   queue a pause-window state).
2. **Resolution.** At the activation instant (or at viewer
   pause inside a pause-trigger window), issue an HTTP GET to
   the slot's `@url` augmented by `<UrlParamInfo>` (§5.7).
3. **Response handling.** If the response is missing,
   unparseable, empty, or late, fall through (§4.4.1). Else
   parse the resolution document.
4. **For linear slots** (`ListMPD`):
   - Play each `<Period>` in declared order.
   - For each Period, fetch the sub-MPD via `<ImportedMPD>` and
     play its single Period's media segments.
   - Drop-before-play: skip a Period whose declared
     `Period@duration` would push cumulative slot duration past
     the parent event's `@maxDuration`.
   - Trim-during-play: if a Period's actual rendered length
     would push cumulative duration past the cap, stop at the
     cap mid-segment.
   - Fire tracking events scheduled inside the sub-MPD as the
     playhead reaches them.
5. **For non-linear slots** (Overlay Resolution Document):
   - For each `<svta:Candidate>` in declared order:
     1. Build the candidate's *admissible form set*: forms for
        which (a) `@mediaType` is renderable on the device (per
        §3.4 / §4.4.5), AND (b) `@layout` is in the
        Broadcaster's `allowedLayouts` set, AND (c) the
        creative carrier mimeType is in the §3.2 admissible
        enumeration.
     2. If the set is empty, skip the candidate (§4.4.5).
     3. Else pick the form whose `@priority` is highest in the
        admissible set, breaking ties on `@mediaType` (`video`
        preferred over `html` preferred over `image`, as a
        default `[inferred]`).
     4. If accepted, render the form per §7.4. Fire impression
        and quartile beacons per §5.5 / §4.4.6.
     5. Stop after one accepted candidate (the slot is filled).
   - If no candidate yielded a renderable form, fall through.

### 7.4 Compositing rules

The Player composes the ad on screen according to the form's
`@mediaType` and the device's capabilities:

- **Video form, multi-decoder device.** The video form is
  composited on top of the primary video using a second decoder.
  The layout token (`overlay-corner`, etc.) indicates the spatial
  placement, which the Player realises via HTML5 / CSS
  positioning on the corresponding video element.
- **Video form, single-decoder device.** The video form cannot
  be composited concurrently with primary playback. For
  `<svta:OverlayPresentation>` slots the Player skips the form.
  For `<svta:PauseAdPresentation>` slots the Player MAY re-task
  the single decoder to play the ad video on top of the paused
  frame; doing so requires preserving the paused position so the
  viewer resumes correctly on dismissal. The conservative
  default for this edition is to skip the video form on
  single-decoder pause-ad opportunities and prefer `html` or
  `image` if available.
- **Image form.** The image is rendered via the device's
  image-overlay surface, positioned per the layout token via
  HTML5 / CSS.
- **HTML form.** The HTML document is rendered via the
  device's HTML-overlay surface (an in-Player WebView or
  equivalent), positioned via HTML5 / CSS layout.

Spatial positioning (left / right / top / bottom inside a
layout) is delegated entirely to HTML5 / CSS; this spec defines
no positioning attributes.

### 7.5 Tracking semantics

Per §4.4.6 and §5.5.4, the Player fires:

- The **impression beacon** at `presentationTime="0"` relative
  to form-visible.
- **Quartile beacons** (25 %, 50 %, 75 %, 100 %) timed against
  the Broadcaster-declared overlay window (`@maxDuration` on
  the slot) for non-linear ads, or against the ad's intrinsic
  duration for linear ads.
- The **complete beacon** at the end of the slot (or at the
  trim boundary if §4.4.3 trim-during-play applies first).

Tracking is fire-and-forget. The Player continues rendering
regardless of tracking transport failures.

### 7.6 Pause-and-overlay composition

When an overlay slot is active and the viewer pauses primary
content inside an overlapping pause-trigger window, the Player:

1. Suspends the overlay rendering (the rendered surface is
   cleared from the screen for the duration of the pause).
2. Resolves the pause-ad opportunity per §4.4.8 and renders the
   selected pause-ad form on top of the paused primary frame.
3. On viewer resume: dismisses the pause-ad within one
   rendering frame (§4.4.8), stops firing pause-ad beacons, and
   restores the overlay rendering when the overlay's slot
   window is still active. The overlay's slot-window clock
   tracked the primary timeline during the pause and continued
   advancing; when the window expired during the pause, the
   overlay surface stays clear on resume.

This composition is illustrated in Annex H (UC-08).

### 7.7 Per-device-class expected behaviour

The matrix below summarises, for each opportunity type, the
Player's dominant behaviour by device class. It is not a
substitute for the per-device walk-throughs in the annexes.

| Opportunity | D1 | D2 | D3 | D4 | D5 |
|-------------|----|----|----|----|----|
| Pre-roll (linear) | Full-fidelity video. | Same as D1. | Single-decoder sequential. | Same as D3. | Same as D3. |
| Mid-roll (linear) | Full-fidelity video, possible pre-buffer on 2nd decoder. | Same. | Single-decoder sequential. | Same. | Same. |
| Overlay (non-linear) | Highest-fidelity form (HTML / image / video). | Video form via 2nd decoder, or side-by-side if `allowedLayouts` permits; skip if neither. | HTML / image overlay. | Image overlay. | Skip (fall through). |
| Hybrid linear + overlay | Linear + concurrent overlay (any form). | Linear + concurrent video-form overlay only; skip overlay portion if no video form. | Linear only (overlay declined, conservative default). | Same. | Linear only. |
| Pause-ad | Highest-fidelity form (HTML / image / video over paused frame). | Video form over paused frame via 2nd decoder; skip if no video form. | HTML / image over paused frame. | Image over paused frame. | Skip. |
| Overlay × pause-ad composition (UC-08) | Overlay → pause-ad on pause, overlay restored on resume. | Same; pause-ad declined if no video form. | Overlay (HTML/image) → pause-ad (HTML/image), restored on resume. | Overlay (image) → pause-ad (image), restored on resume. | Both declined; primary paused frame stays clean. |
| Multi-ad break (linear) | Full sequence with cap arithmetic. | Same. | Same on single decoder. | Same. | Same. |
| Legacy Player encountering new construct | Primary continues uninterrupted (fall through). | Same. | Same. | Same. | Same. |

"Skip" / "fall through" is always an admissible outcome and is
not a failure.

## 8. Implementation notes

This chapter is non-normative. It collects guidance for
implementers based on conditions that recur in practice.

### 8.1 Error semantics

The table below enumerates the error conditions a Player will
encounter at runtime, the actions it takes, the actions it MAY
take, and the obligations the Broadcaster and ADS hold to
prevent or recover. It consolidates the cross-references that
chapters 4 and 6 carry inline.

| ID | Condition | Player action | Player MAY | Broadcaster / ADS obligation |
|----|-----------|---------------|------------|-----------------------------|
| E1 | Resolution request fails at transport (HTTP 4xx/5xx, timeout, DNS / TCP / TLS). | Fall through to primary content. Keep primary playback uninterrupted. | Apply a bounded retry inside the slot resolution window; abandon retries once the window closes. | ADS SHOULD bound its response latency to the slot window; Broadcaster SHOULD set `@earliestResolutionTimeOffset` to leave room for one retry. |
| E2 | Resolution document received but unparseable or schema-invalid. | Treat as if no document was returned; fall through. | Log for diagnostics. | ADS emits documents that validate against the profile they declare. |
| E3 | Resolution document well-formed but empty (no candidates / no Periods). | Fall through. No tracking beacons fired. | Surface a non-normative no-fill event to the application layer. | ADS MAY emit empty deliberately as a no-fill signal — this is conforming. |
| E4 | Resolution document arrives past slot window. | Discard; fall through. Keep primary playback uninterrupted. | Reuse the response for a later slot only if that slot's `@earliestResolutionTimeOffset` permits; otherwise discard. | ADS honours the slot's resolution window; when it cannot, returns early with an empty document (E3). |
| E5 | Player does not implement the SGAI event scheme URI (legacy on a new construct). | Ignore the event; continue playing primary content (graceful degradation). | None. | Broadcaster expresses every new construct via an extension point with `ignore-if-unknown` semantics. |
| E6 | A candidate carries no form renderable on the device (intersection of device caps, `allowedLayouts`, and form admissibility is empty). | Skip the candidate; fall through to the next candidate in declared order. If exhausted, fall through to primary content. | Surface a non-normative candidate-skipped event. | ADS SHOULD return at least one candidate with a broadly renderable form (e.g. video) so that fall-through is the worst case, not the default case. |
| E7 | A form's `@layout` is admissible by the spec but not by the Broadcaster's `allowedLayouts` declaration. | Reject the form; evaluate the candidate's other forms. If none remain, treat as E6. | Log layout name and reason. | Broadcaster declares `allowedLayouts` using IAB-defined names only (§3.2). ADS uses tokens drawn from the §3.2 enumeration on every form's `@layout`. |
| E8 | A form's creative-carrier `@mediaType` is outside the admissible set in §3.2 / §5.3.2. | Reject the form. If no admissible form remains on the candidate, treat as E6. | Skip the entire candidate (an extra-cautious default), flag the resolution document as non-conformant for diagnostics. | ADS / Broadcaster restrict every form's mimeType to {`video`, `image`, `html`}. Scripted creatives are wrapped in `text/html`. |
| E9 | Cumulative declared duration of accepted candidates would exceed the slot cap if the next candidate is added ("drop before play"). | Apply R7.3 / R7.4: preserve the relative order of the remaining candidates after dropping. | Drop the offending candidate based on declared duration; drop only that one or drop all subsequent ones — both are conforming. | Broadcaster declares `@maxDuration` on every slot. ADS is not required to respect the cap (the cap is Player-enforced). |
| E10 | Actual rendered length of an accepted candidate exceeds its declared duration, pushing cumulative slot duration past the cap ("trim during play"). | Stop rendering exactly at the cap boundary, even mid-ad. Keep the slot bounded by the cap. Stop firing tracking beacons at the trim boundary. | Surface a non-normative slot-trimmed event. | ADS / Broadcaster keep declared duration aligned with actual length when feasible; the Player is the authoritative enforcer. |
| E11 | Ad media-segment or asset fetch fails during playback (HTTP, timeout, decoder, DRM key-exchange on an ad asset). | Abort the current candidate. Resume at the next candidate in declared order; re-apply cap arithmetic against rendered-so-far. If no candidates remain, fall through. | Surface a non-normative candidate-failed event. May tear down the entire slot per Player policy. | ADS SHOULD point at CDNs with availability comparable to the Broadcaster CDN. |
| E12 | Tracking beacon delivery fails (HTTP error, timeout, DNS). | Continue playback uninterrupted. Treat beacon failures as non-fatal. | Retry with bounded backoff; log; surface via an implementation-defined API. | ADS embeds beacons under the callback scheme reused from linear SGAI; relies on the Player only for transport, not for state correctness. |
| E13 | Unknown vendor namespace or unrecognised extension element on the resolution document or its sub-MPDs. | Safely ignore. Continue evaluating the candidate or the slot. | Pass the ignored data verbatim to the application layer for opportunistic consumption. | ADS / Broadcaster MAY use vendor-namespaced extensions for app metadata that has no native DASH carrier; do not rely on Players consuming them. |
| E14 | ADS returns a resolution document whose profile does not match the slot type (e.g. a `ListMPD` to a non-linear overlay slot, or an Overlay Resolution Document to a linear slot). | Treat as E2 (schema-mismatch flavour). Fall through. | Log the profile mismatch for diagnostics. | ADS authors the response profile per §4.3 A-1 (linear ⇒ `ListMPD`, non-linear ⇒ Overlay Resolution Document). |

#### 8.1.1 Order of precedence

When more than one condition applies, the Player applies them in
this order (short-circuit at the first match):

1. **Transport** — E1 (resolution-request transport) before E11
   (ad-segment / asset transport).
2. **Document-level** — E2 (parse / schema), E14 (profile
   mismatch), E3 (empty), E4 (late) before any per-candidate
   evaluation.
3. **Constraint surfacing** — E5 (unknown event scheme), E7
   (disallowed layout), E8 (inadmissible carrier) before
   per-candidate device evaluation.
4. **Per-candidate decode-time** — E6 (no renderable form)
   before any duration evaluation.
5. **Per-candidate playback-time** — E9 (drop before play)
   before E10 (trim during play); E11 (asset failure) preempts
   E10 on the affected candidate.
6. **Tracking failures (non-fatal)** — E12 and E13 are
   evaluated independently and do not influence the slot
   outcome.

#### 8.1.2 Fall-through definition

"Fall through to primary content uninterrupted" means: no
visible artefact (no freeze, no blank slate, no error overlay
unless the application has explicitly opted in via an
implementation-defined API); no tracking beacon fired for the
failed slot; primary playback continues from the position it
would have held had the SGAI event not existed. For
`<ReplacePresentation>` slots specifically, "uninterrupted"
means the playhead continues advancing on the main timeline at
wall-clock pace; the Player does not pause main media time
waiting for an ADS response that ultimately failed.

#### 8.1.3 Surfacing errors to the application layer

The Player MAY expose any of the error rows above to the
embedding application via an implementation-defined API (e.g. a
JavaScript event on a web Player, a delegate callback on a
native SDK). The API shape is non-normative. Implementers
SHOULD prioritise surfacing E3 (no-fill), E8 (inadmissible
carrier), E10 (trim), and E11 (candidate failure).

### 8.2 Tracking-only VAST inputs

When the ADS receives a VAST `<Ad>` (Inline) entry with no
`<MediaFile>` (a tracking-only ad), the ADS cannot synthesise a
sub-MPD with no media. The industry convention is split between
silent skip and emitting VAST `<Error>` code 403; the
authoritative source consulted did not resolve this question.
This spec recommends silent skip — the resulting resolution
document omits the entry — pending a normative reference
emerging from the IAB.

### 8.3 Late callbacks

When a tracking beacon's `presentationTime` arrives after the
slot has trimmed (E10) or after a candidate has been aborted
(E11), the Player keeps the beacon unfired. This is the
quartile-stop rule (§4.4.6) extended to all beacons.

### 8.4 Device-class fallbacks

Several open questions in the use cases resolve to Player-side
policy, not spec rules:

- Whether the Player issues an ADS request on devices that will
  certainly skip the opportunity (e.g. D5 on an overlay slot) to
  support impression accounting. This spec does not mandate
  either; Players SHOULD document their choice in their
  conformance statement.
- Whether single-decoder devices (D3, D4) re-task the decoder to
  play a video form on top of a paused primary frame. The
  conservative default is to skip the video form and prefer
  HTML / image.
- Whether D3 / D4 always decline the overlay portion of a
  hybrid break. The conservative default is to decline; the
  Broadcaster's `allowedLayouts` declaration on the overlay
  event is the lever that opts in when the Broadcaster
  considers HTML / image overlay on top of a linear ad video a
  renderable composition.

### 8.5 Speculative pre-fetch for pause ads

The Player MAY pre-fetch the ADS resolution for a pause-trigger
slot speculatively when the MPD loads, trading latency on viewer
pause for targeting-freshness on the ad shown. The Player MAY
also defer the resolution until the viewer actually pauses,
trading targeting-freshness for latency. Implementers SHOULD
pick based on their viewer's expected interaction patterns.

### 8.6 Image-form intrinsic duration

`<svta:RenderableAsset @mediaType="image">` has no intrinsic
duration. The `@duration` attribute on the form is the
*intended display duration*; the Player treats it identically
to a video form's declared duration for drop-before-play and
trim-during-play arithmetic.

### 8.7 Degenerate authoring cases

A Broadcaster authoring `@maxDuration="0"` on a slot, or
declaring `allowedLayouts` populated entirely with tokens
inadmissible under §5.3.3 for the slot's scheme, produces a slot
that no candidate can fill. The Player's behaviour is the
standard fall-through (§4.4.1, E6); the slot produces no ad and
primary content continues. These cases are authoring errors;
diagnostics SHOULD surface them through the implementation-
defined API per §8.1.3.

### 8.8 Per-construct backward-compatibility audit

Every new construct introduced by this specification — the two
SGAI event schemes (`urn:svta:dash:event:sgai-overlay:2026`,
`urn:svta:dash:event:sgai-pause-trigger:2026`), the SVTA-namespaced
elements (`<svta:OverlayPresentation>`,
`<svta:PauseAdPresentation>`, `<svta:OverlayList>`,
`<svta:Candidate>`, `<svta:RenderableAsset>`, `<svta:Click>`,
`<svta:UniversalAdId>`), and the new profile URI
(`urn:svta:dash:profile:sgai-overlay-list:2026`) — has been
audited against the backward-compatibility checklist:

| Construct | Placement | Extension rule (DR) | Walk-through | Sibling check | UC-07 test | Namespace | Status |
|-----------|-----------|---------------------|--------------|---------------|------------|-----------|--------|
| `urn:svta:dash:event:sgai-overlay:2026` | `<EventStream>@schemeIdUri` inside `<Period>` | §5.10 + §5.2.1 NOTE 2 (DR-2/3, carrier (b)) | §5.1.3 / §G.2 | No baseline sibling depends on it | Annex G (TC-01) | SVTA Ads WG namespace | OK |
| `urn:svta:dash:event:sgai-pause-trigger:2026` | `<EventStream>@schemeIdUri` inside `<Period>` | §5.10 + §5.2.1 NOTE 2 (DR-2/3, carrier (b)) | §5.1.4 / §G.2 | No baseline sibling depends on it | Annex G (TC-01 generalised to the pause-trigger scheme) | SVTA Ads WG namespace | OK |
| `<svta:OverlayPresentation>` | Child of `<Event>` (foreign-namespace) | §5.2.1 (DR-2/3, carrier (a)) | §5.1.3 | No baseline sibling | Annex G | `urn:svta:dash:sgai:2026` | OK |
| `<svta:PauseAdPresentation>` | Child of `<Event>` (foreign-namespace) | §5.2.1 (DR-2/3, carrier (a)) | §5.1.4 | No baseline sibling | Annex G | `urn:svta:dash:sgai:2026` | OK |
| `<svta:OverlayList>` | Child of `<Period>` (in the Overlay Resolution Document, foreign-namespace) | §5.2.1 (DR-2/3, carrier (a)) | §5.2.2 | `<Period>@duration="PT0S"` keeps §5.3.2.2 Table 4 satisfied | Annex C | `urn:svta:dash:sgai:2026` | OK |
| `<svta:Candidate>` | Child of `<svta:OverlayList>` | §5.2.1 (DR-2/3, carrier (a)) | §5.2.2 | No baseline sibling | Annex C | `urn:svta:dash:sgai:2026` | OK |
| `<svta:RenderableAsset>` | Child of `<svta:Candidate>` | §5.2.1 (DR-2/3, carrier (a)) | §5.3 | No baseline sibling | Annex C | `urn:svta:dash:sgai:2026` | OK |
| `<svta:Click>` | Child of `<svta:Candidate>` | §5.2.1 (DR-2/3, carrier (a)) | §5.6.1 / §5.6.4 | No baseline sibling | Annex C | `urn:svta:dash:sgai:2026` | OK |
| `<svta:UniversalAdId>` | Child of `<svta:Candidate>` | §5.2.1 (DR-2/3, carrier (a)) | §5.6.2 / §5.6.4 | No baseline sibling | Annex C | `urn:svta:dash:sgai:2026` | OK |
| `urn:svta:dash:profile:sgai-overlay-list:2026` | `MPD@profiles` value on the Overlay Resolution Document | §8.1 Profile URN (year-pinned) | §5.2.2 | Inherits SPS-shape envelope (zero-duration Period) | Annex C | n/a (profile URN) | OK |

The table demonstrates that every new construct lives under
`urn:svta:dash:sgai:2026` (or as a year-pinned scheme URI),
follows one of the DR-6 carrier options ((a) foreign-namespace
open content; (b) Event Stream payload), and produces the UC-07
fall-through on legacy Players.

## Annex A — UC-01: Pre-roll (linear)

This annex walks through the canonical pre-roll slot end-to-end:
the Broadcaster's main MPD, the ADS's `ListMPD`, the per-ad
sub-MPD, and the per-device-class behaviour.

### A.1 Scenario

The viewer starts playback of "Movie X". The Broadcaster has
declared a single pre-roll ad opportunity at the start of the
session: a 15-second linear ad takes over the screen before the
primary content begins. When the ad completes, the primary
content starts from its first frame. Non-linear forms are not
permitted for this slot.

### A.2 Main MPD (relevant excerpt)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:up="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:advanced-linear:2025"
     minBufferTime="PT2S">

  <EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025"/>
  <UrlParamInfo includeInRequests="altmpd"
                queryTemplate="video_profile=$urn:mpeg:dash:state:video$&amp;session_id=$urn:mpeg:dash:state:cmcd#sid$"/>

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

### A.3 Resolution document (`ListMPD`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-05-20T00:00:00Z">

  <BaseURL>https://ads.example.com/delivery/</BaseURL>

  <Period id="ad_01" duration="PT15S">
    <ImportedMPD uri="creative_201.mpd" earliestResolutionTimeOffset="0"/>
  </Period>
</MPD>
```

### A.4 Sub-MPD (SPS profile)

The per-ad sub-MPD carries the video creative and the inline
callback tracking events. Quartile beacons fire at 3.75 s, 7.5 s,
11.25 s, and 15 s relative to the ad's start.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S"
     publishTime="2026-05-20T00:00:00Z">

  <Period id="1" duration="PT15S" start="PT0S">

    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="10">https://tracker.example.com/impression?ad=201</Event>
      <Event presentationTime="0"     id="11">https://tracker.example.com/start?ad=201</Event>
      <Event presentationTime="3750"  id="12">https://tracker.example.com/firstQuartile?ad=201</Event>
      <Event presentationTime="7500"  id="13">https://tracker.example.com/midpoint?ad=201</Event>
      <Event presentationTime="11250" id="14">https://tracker.example.com/thirdQuartile?ad=201</Event>
      <Event presentationTime="15000" id="15">https://tracker.example.com/complete?ad=201</Event>
    </EventStream>

    <AdaptationSet mimeType="video/mp4" codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <Representation id="v1" bandwidth="2500000" width="1280" height="720">
        <BaseURL>media/video_201.mp4</BaseURL>
        <SegmentBase indexRange="0-850"/>
      </Representation>
    </AdaptationSet>
  </Period>
</MPD>
```

### A.5 Per-device-class behaviour

| Device | Behaviour |
|--------|-----------|
| D1 | Reads slot rules (linear, 15 s cap). Plays the candidate's video form on one of its decoders. Primary content starts after the ad. |
| D2 | Same as D1. The absence of non-video overlay capability is irrelevant for a linear-only slot. |
| D3 | Plays the video form on the single decoder, then reuses the same decoder for the primary content. Sequential play; no concurrent rendering needed. |
| D4 | Same as D3. |
| D5 | Same as D3. Linear ads don't need overlay capability. |

## Annex B — UC-02: Mid-roll (linear)

This annex covers the canonical mid-roll: a linear ad takes over
the primary content at a chosen point on the timeline, plays for
a bounded duration, and hands back to primary content.

### B.1 Scenario

The viewer is watching "Movie X". At `presentationTime=PT6M` the
Broadcaster has declared a 30-second mid-roll opportunity. The ad
replaces a bounded span of primary content; on completion, the
Player resumes at the playhead position determined by
`@returnOffset`.

### B.2 Main MPD (relevant excerpt)

```xml
<EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
             timescale="1000">
  <Event id="102" presentationTime="360000" duration="30000">
    <ReplacePresentation url="https://ads.example.com/decision/midroll"
                         earliestResolutionTimeOffset="60000"
                         maxDuration="30000"
                         returnOffset="0"
                         startWithOffset="false"/>
  </Event>
</EventStream>
```

### B.3 Resolution document (`ListMPD`, two-ad pod)

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     publishTime="2026-05-20T00:06:00Z">

  <BaseURL>https://ads.example.com/delivery/</BaseURL>

  <Period id="ad_02_01" duration="PT15S">
    <ImportedMPD uri="creative_202.mpd" earliestResolutionTimeOffset="0"/>
  </Period>
  <Period id="ad_02_02" duration="PT15S">
    <ImportedMPD uri="creative_203.mpd" earliestResolutionTimeOffset="15"/>
  </Period>
</MPD>
```

### B.4 Sub-MPD

Same shape as Annex A §A.4; the tracking events fire at quartiles
of the ad's own 15-second timeline.

### B.5 Per-device-class behaviour

| Device | Behaviour |
|--------|-----------|
| D1 | Plays the two 15-second ads back-to-back. The second decoder MAY pre-buffer the next ad while the first plays — Player implementation detail. Returns to primary at the slot end. |
| D2 | Same as D1. |
| D3 | Single-decoder sequential. No pre-buffer of ad N+1 while ad N plays. |
| D4 | Same as D3. |
| D5 | Same as D3. |

## Annex C — UC-03: Coexisting overlay (multi-form showcase)

**This annex demonstrates the multi-form / multi-layout candidate
required of the non-linear extension.** It is the principal proof
that a single Overlay Resolution Document, returned by a
device-agnostic ADS, can satisfy the rendering heterogeneity of
all five device classes.

### C.1 Scenario

The viewer is watching "Movie X". At `presentationTime=PT2M`
the Broadcaster has declared a non-linear overlay slot with a
20-second window. Allowed layouts are `overlay-corner` and
`overlay-lower-third` (the IAB Overlay ad type). The Broadcaster
wants the highest-fidelity rendering each viewer's device can
support but excludes content-resizing layouts (`squeezeback-*`)
for this slot.

The ADS returns two candidates. Candidate 1 is the high-value
spot: it carries a video form, two HTML forms (one per layout
sub-token), and an image form — four options for the same
advertiser. Candidate 2 is the fallback: it carries only an
image form, suitable for low-capability devices.

### C.2 Main MPD (relevant excerpt)

```xml
<EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026" timescale="1000">
  <Event id="301" presentationTime="120000" duration="20000">
    <svta:OverlayPresentation
        xmlns:svta="urn:svta:dash:sgai:2026"
        url="https://ads.example.com/decision/overlay-mid120"
        earliestResolutionTimeOffsetTicks="10000"
        maxDuration="20000"
        allowedLayouts="overlay-corner overlay-lower-third"/>
  </Event>
</EventStream>
```

### C.3 Resolution document (Overlay Resolution Document)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     publishTime="2026-05-20T00:02:00Z">

  <Period id="overlay-resolution" duration="PT0S">
    <svta:OverlayList>

      <!-- Candidate 1: high-value, multi-form, multi-layout -->
      <svta:Candidate id="c1" adId="campaign-XYZ-spot-1" priority="100">

        <!-- Form 1.1: video, corner overlay (preferred on multi-decoder devices) -->
        <svta:RenderableAsset mediaType="video" layout="overlay-corner"
                              duration="PT20S" priority="100">
          <ImportedMPD uri="https://ads.example.com/c1/video.mpd"
                       earliestResolutionTimeOffset="5"/>
        </svta:RenderableAsset>

        <!-- Form 1.2: HTML, corner overlay (preferred on D3) -->
        <svta:RenderableAsset mediaType="html" layout="overlay-corner"
                              duration="PT20S" priority="80"
                              assetUrl="https://ads.example.com/c1/banner.html">
          <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" timescale="1000">
            <Event presentationTime="0"     id="b-imp-c1f2">https://tracker.example.com/impression?ad=c1&amp;form=html</Event>
            <Event presentationTime="5000"  id="b-q1-c1f2">https://tracker.example.com/firstQuartile?ad=c1&amp;form=html</Event>
            <Event presentationTime="10000" id="b-q2-c1f2">https://tracker.example.com/midpoint?ad=c1&amp;form=html</Event>
            <Event presentationTime="15000" id="b-q3-c1f2">https://tracker.example.com/thirdQuartile?ad=c1&amp;form=html</Event>
            <Event presentationTime="20000" id="b-cpl-c1f2">https://tracker.example.com/complete?ad=c1&amp;form=html</Event>
          </EventStream>
        </svta:RenderableAsset>

        <!-- Form 1.3: HTML, lower-third (alternate layout for HTML-capable devices) -->
        <svta:RenderableAsset mediaType="html" layout="overlay-lower-third"
                              duration="PT20S" priority="60"
                              assetUrl="https://ads.example.com/c1/lower-third.html">
          <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" timescale="1000">
            <Event presentationTime="0"     id="b-imp-c1f3">https://tracker.example.com/impression?ad=c1&amp;form=html-l3</Event>
            <Event presentationTime="20000" id="b-cpl-c1f3">https://tracker.example.com/complete?ad=c1&amp;form=html-l3</Event>
          </EventStream>
        </svta:RenderableAsset>

        <!-- Form 1.4: image, corner overlay (fallback for D4) -->
        <svta:RenderableAsset mediaType="image" layout="overlay-corner"
                              duration="PT20S" priority="40"
                              assetUrl="https://ads.example.com/c1/banner.png">
          <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" timescale="1000">
            <Event presentationTime="0"     id="b-imp-c1f4">https://tracker.example.com/impression?ad=c1&amp;form=img</Event>
            <Event presentationTime="5000"  id="b-q1-c1f4">https://tracker.example.com/firstQuartile?ad=c1&amp;form=img</Event>
            <Event presentationTime="10000" id="b-q2-c1f4">https://tracker.example.com/midpoint?ad=c1&amp;form=img</Event>
            <Event presentationTime="15000" id="b-q3-c1f4">https://tracker.example.com/thirdQuartile?ad=c1&amp;form=img</Event>
            <Event presentationTime="20000" id="b-cpl-c1f4">https://tracker.example.com/complete?ad=c1&amp;form=img</Event>
          </EventStream>
        </svta:RenderableAsset>

        <svta:Click through="https://advertiser.example.com/landing?utm=overlay"
                    trackingUrl="https://tracker.example.com/click?ad=c1"/>
        <svta:UniversalAdId idRegistry="ad-id.org" value="XYZ12345"/>
      </svta:Candidate>

      <!-- Candidate 2: image-only fallback -->
      <svta:Candidate id="c2" adId="campaign-ABC-spot-1" priority="50">
        <svta:RenderableAsset mediaType="image" layout="overlay-corner"
                              duration="PT20S" priority="50"
                              assetUrl="https://ads.example.com/c2/banner.png">
          <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" timescale="1000">
            <Event presentationTime="0"     id="b-imp-c2">https://tracker.example.com/impression?ad=c2</Event>
            <Event presentationTime="20000" id="b-cpl-c2">https://tracker.example.com/complete?ad=c2</Event>
          </EventStream>
        </svta:RenderableAsset>
      </svta:Candidate>

    </svta:OverlayList>
  </Period>
</MPD>
```

### C.4 Video sub-MPD for Candidate 1 Form 1.1

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S"
     publishTime="2026-05-20T00:02:00Z">

  <Period id="1" duration="PT20S" start="PT0S">

    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1" timescale="1000">
      <Event presentationTime="0"     id="b-imp-c1f1">https://tracker.example.com/impression?ad=c1&amp;form=video</Event>
      <Event presentationTime="0"     id="b-start-c1f1">https://tracker.example.com/start?ad=c1&amp;form=video</Event>
      <Event presentationTime="5000"  id="b-q1-c1f1">https://tracker.example.com/firstQuartile?ad=c1&amp;form=video</Event>
      <Event presentationTime="10000" id="b-q2-c1f1">https://tracker.example.com/midpoint?ad=c1&amp;form=video</Event>
      <Event presentationTime="15000" id="b-q3-c1f1">https://tracker.example.com/thirdQuartile?ad=c1&amp;form=video</Event>
      <Event presentationTime="20000" id="b-cpl-c1f1">https://tracker.example.com/complete?ad=c1&amp;form=video</Event>
    </EventStream>

    <AdaptationSet mimeType="video/mp4" codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <Representation id="v1" bandwidth="1500000" width="640" height="360">
        <BaseURL>https://ads.example.com/c1/video.mp4</BaseURL>
        <SegmentBase indexRange="0-850"/>
      </Representation>
    </AdaptationSet>
  </Period>
</MPD>
```

### C.5 Per-device-class behaviour

The Player walks Candidate 1 first (declared order).

| Device | Picks form | Why |
|--------|-----------|-----|
| D1 | Form 1.1 (video, `overlay-corner`) | Highest `@priority`; video is renderable on a 2-decoder device; layout is in `allowedLayouts`. |
| D2 | Form 1.1 (video, `overlay-corner`) | Same as D1. D2 supports video-on-video composition via second decoder. |
| D3 | Form 1.2 (HTML, `overlay-corner`) | Form 1.1 fails (single decoder cannot composite video concurrently with primary). Form 1.2 wins among admissible: HTML is renderable, layout is admissible, `@priority=80`. |
| D4 | Form 1.4 (image, `overlay-corner`) | Form 1.1 fails (single decoder). Forms 1.2 and 1.3 fail (no HTML overlay surface). Form 1.4 wins: image is renderable, layout is admissible. |
| D5 | None on Candidate 1; Candidate 2 also fails; fall through. | D5 has no overlay capability at all. All four forms on Candidate 1 fail. Candidate 2's only form (image) also fails. Player falls through to primary content uninterrupted. |

Notably, the **same resolution document** drove five different
rendering outcomes. The ADS did not know the device class; it
returned a multi-form candidate, and the Player picked.

The Player fires impression and quartile beacons against the
form's own carrier, timed against the slot's `@maxDuration=20000`
(i.e. the 20-second overlay window declared by the Broadcaster).
If a viewer dismisses the overlay early or the slot is trimmed
mid-rendering, the Player stops firing beacons at that point.

## Annex D — UC-04: Hybrid linear + overlay

### D.1 Scenario

At `presentationTime=PT6M` the Broadcaster has declared a hybrid
slot: a 30-second linear ad takes over the screen, and a
20-second overlay (corner, image / HTML) is composited on top of
the linear ad during the same break. The two portions are
independent slots, co-located on the timeline (§5.1.5).

### D.2 Main MPD (relevant excerpt)

Two co-located events at `presentationTime=360000`:

```xml
<!-- Linear portion -->
<EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
             timescale="1000">
  <Event id="401" presentationTime="360000" duration="30000">
    <ReplacePresentation url="https://ads.example.com/decision/midroll-linear"
                         earliestResolutionTimeOffset="60000"
                         maxDuration="30000"
                         returnOffset="0"
                         startWithOffset="false"/>
  </Event>
</EventStream>

<!-- Overlay portion (concurrent) -->
<EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026" timescale="1000">
  <Event id="402" presentationTime="360000" duration="20000">
    <svta:OverlayPresentation
        xmlns:svta="urn:svta:dash:sgai:2026"
        url="https://ads.example.com/decision/midroll-overlay"
        earliestResolutionTimeOffsetTicks="60000"
        maxDuration="20000"
        allowedLayouts="overlay-lower-third"/>
  </Event>
</EventStream>
```

### D.3 Player behaviour

The Player resolves both URLs independently. The linear
resolution returns a `ListMPD` (one Period, one ad of 30 s); the
overlay resolution returns an Overlay Resolution Document (one
candidate, multiple forms). The Player plays the linear ad
full-screen and composites the overlay on top, where the
device's capability and `allowedLayouts="overlay-lower-third"`
permit.

When the overlay window (20 s) is shorter than the linear window
(30 s), the overlay is dismissed at 20 s and the linear continues
alone until 30 s. The shorter window governs the overlay's
display (§5.1.5).

### D.4 Per-device-class behaviour

| Device | Behaviour |
|--------|-----------|
| D1 | Plays the linear ad full-screen. Composites the lower-third overlay (any form, e.g. HTML) on top via the HTML overlay surface. |
| D2 | Plays the linear ad full-screen. If the overlay candidate has a video form, composites it on top via the second decoder; otherwise declines the overlay portion (no HTML / image surface on D2). The linear ad still plays. |
| D3 | Plays the linear ad full-screen. The overlay portion is declined by default (conservative). The linear ad still plays. |
| D4 | Same as D3. |
| D5 | Plays the linear ad full-screen. No overlay capability at all. |

## Annex E — UC-05: Pause-triggered ad

### E.1 Scenario

The Broadcaster has declared a pause-trigger window starting at
1 minute into the content and lasting 10 minutes. Inside this
window, when the viewer pauses, the Player renders an ad on top
of the paused primary frame. The ad is dismissed when the viewer
resumes or the 30-second display cap is reached.

### E.2 Main MPD (relevant excerpt)

```xml
<EventStream schemeIdUri="urn:svta:dash:event:sgai-pause-trigger:2026" timescale="1000">
  <Event id="501" presentationTime="60000" duration="600000">
    <svta:PauseAdPresentation
        xmlns:svta="urn:svta:dash:sgai:2026"
        url="https://ads.example.com/decision/pause-ad"
        maxDuration="30000"
        allowedLayouts="pause-ad overlay-corner"/>
  </Event>
</EventStream>
```

### E.3 Resolution document (Overlay Resolution Document)

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     publishTime="2026-05-20T00:05:30Z">

  <Period id="overlay-resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="p1" adId="pause-campaign-1" priority="80">
        <svta:RenderableAsset mediaType="html" layout="pause-ad"
                              duration="PT30S" priority="80"
                              assetUrl="https://ads.example.com/p1/page.html">
          <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" timescale="1000">
            <Event presentationTime="0"     id="b-imp-p1">https://tracker.example.com/impression?ad=p1</Event>
            <Event presentationTime="30000" id="b-cpl-p1">https://tracker.example.com/complete?ad=p1</Event>
          </EventStream>
        </svta:RenderableAsset>

        <svta:RenderableAsset mediaType="image" layout="pause-ad"
                              duration="PT30S" priority="50"
                              assetUrl="https://ads.example.com/p1/image.png">
          <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" timescale="1000">
            <Event presentationTime="0"     id="b-imp-p1-img">https://tracker.example.com/impression?ad=p1&amp;form=img</Event>
          </EventStream>
        </svta:RenderableAsset>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

### E.4 Per-device-class behaviour

| Device | Behaviour |
|--------|-----------|
| D1 | Viewer pauses → Player renders the HTML form (`@priority=80`) on top of the paused frame via HTML overlay surface. Dismissed on resume. |
| D2 | No video form; HTML and image not renderable. Player declines the pause-ad. Paused frame stays on screen until viewer resumes. |
| D3 | HTML form is rendered via HTML overlay surface on top of paused frame. Dismissed on resume. |
| D4 | HTML not available; image form is rendered. Dismissed on resume. |
| D5 | No overlay capability; pause-ad declined. Paused frame stays on screen. |

## Annex F — UC-06: Multi-ad break (linear)

### F.1 Scenario

The Broadcaster has declared a mid-content multi-ad break: at
`presentationTime=PT12M` the slot accepts a sequence of linear
ads totalling at most 90 seconds. The ADS decides the count and
order.

### F.2 Main MPD (relevant excerpt)

```xml
<EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
             timescale="1000">
  <Event id="601" presentationTime="720000" duration="90000">
    <ReplacePresentation url="https://ads.example.com/decision/multi-ad-break"
                         earliestResolutionTimeOffset="60000"
                         maxDuration="90000"
                         returnOffset="0"
                         startWithOffset="false"/>
  </Event>
</EventStream>
```

### F.3 Resolution document (`ListMPD`, three candidates)

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     publishTime="2026-05-20T00:12:00Z">
  <BaseURL>https://ads.example.com/delivery/</BaseURL>

  <Period id="ad_06_01" duration="PT30S">
    <ImportedMPD uri="creative_601.mpd" earliestResolutionTimeOffset="0"/>
  </Period>
  <Period id="ad_06_02" duration="PT30S">
    <ImportedMPD uri="creative_602.mpd" earliestResolutionTimeOffset="20"/>
  </Period>
  <Period id="ad_06_03" duration="PT45S">  <!-- pushes total past the 90s cap -->
    <ImportedMPD uri="creative_603.mpd" earliestResolutionTimeOffset="55"/>
  </Period>
</MPD>
```

### F.4 Player cap arithmetic

Declared durations: 30 + 30 + 45 = 105 s. Cap: 90 s. The Player
applies drop-before-play (§4.4.3): Period `ad_06_03`'s declared
45 s would push cumulative duration to 105 s (15 s over). The
Player drops `ad_06_03` and plays only the first two ads,
totalling 60 s. The break ends at 60 s; primary content resumes
at the slot end.

Alternative behaviour: the Player MAY play `ad_06_03` for 30 s
(reaching the 90 s cap exactly) and apply trim-during-play
(§4.4.3). Both behaviours conform.

### F.5 Per-device-class behaviour

| Device | Behaviour |
|--------|-----------|
| D1 | Sequential play of two (or three trimmed) ads; the second decoder MAY pre-buffer the next ad. |
| D2 | Same as D1. |
| D3 | Single decoder reused sequentially; no pre-buffer. |
| D4 | Same as D3. |
| D5 | Same as D3. |

## Annex G — UC-07: Legacy Player encounters new constructs

### G.1 Scenario

A Player that predates this proposal receives a manifest that
uses the new `<svta:OverlayPresentation>` event (or the new
`<svta:PauseAdPresentation>` event). The Player has no awareness
of the new scheme URIs or namespaces.

### G.2 Expected behaviour (uniform across D1..D5)

The legacy Player encounters the `<EventStream>` whose
`schemeIdUri` is `urn:svta:dash:event:sgai-overlay:2026` (or
`urn:svta:dash:event:sgai-pause-trigger:2026`). Because the
scheme URI is unknown, the Player ignores every `<Event>` carried
on the stream. The `<svta:OverlayPresentation>` element and its
attributes — which live inside the `<Event>` — are discarded
together with the unknown scheme.

The Broadcaster's main MPD remains a valid DASH document because
the SGAI events use foreign-namespace open content under §5.2.1
of the base specification: removing the SVTA-namespaced elements
leaves a document that is still §5.2.1-conformant.

Primary content continues to play uninterrupted. No tracking
beacon is fired for the ignored opportunity.

### G.3 Why this works

- The `<EventStream>@schemeIdUri` is the legacy Player's
  decision point: an unknown scheme is silently skipped per
  §5.10 of MPEG-DASH 6th edition.
- The SVTA-namespaced child elements live inside the `<Event>`,
  so even a Player that parses the `<Event>` (because some
  unrelated scheme it implements is also on the same Period)
  discards the SGAI child via §5.2.1 foreign-namespace open
  content (a legacy parser removes the full subtree per the
  §5.2.1 NOTE 2 discard semantic).
- The new schemes use year-pinned URIs (`...:2026`), so a
  future-edition Player that implements `:2027` recognises both
  `:2026` (this edition) and `:2027` (its own) and applies the
  appropriate semantics per the cross-edition policy (§4.5).

Behaviour is uniform across device classes: a top-tier device
running a legacy Player produces the same outcome as a worst-case
device running a legacy Player — primary content continues
unmodified.

## Annex H — UC-08: Overlay window crosses a pause-ad window

### H.1 Scenario

The Broadcaster has authored both an overlay slot (UC-03 shape)
and a pause-trigger window (UC-05 shape) whose windows overlap.
The viewer pauses primary playback while the overlay is on
screen, inside the pause-ad window. Per §4.4.8 and §7.6, the
pause-ad takes priority over the overlay during the pause; on
resume, the pause-ad is dismissed and the overlay is restored
when its slot window is still active.

### H.2 Main MPD (relevant excerpt)

Two events on independent EventStreams whose windows overlap:

```xml
<!-- Overlay slot: 20 s window at PT2M -->
<EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026" timescale="1000">
  <Event id="801" presentationTime="120000" duration="20000">
    <svta:OverlayPresentation
        xmlns:svta="urn:svta:dash:sgai:2026"
        url="https://ads.example.com/decision/overlay-mid120"
        earliestResolutionTimeOffsetTicks="10000"
        maxDuration="20000"
        allowedLayouts="overlay-corner overlay-lower-third"/>
  </Event>
</EventStream>

<!-- Pause-trigger window: PT1M to PT11M -->
<EventStream schemeIdUri="urn:svta:dash:event:sgai-pause-trigger:2026" timescale="1000">
  <Event id="802" presentationTime="60000" duration="600000">
    <svta:PauseAdPresentation
        xmlns:svta="urn:svta:dash:sgai:2026"
        url="https://ads.example.com/decision/pause-ad"
        maxDuration="30000"
        allowedLayouts="pause-ad overlay-corner"/>
  </Event>
</EventStream>
```

### H.3 Timeline

Suppose the viewer pauses at `presentationTime=PT2M10S` (10
seconds into the overlay window, 70 seconds into the pause-ad
window):

| Wall-clock event | Player action |
|------------------|---------------|
| PT2M10S — viewer pauses | Suspends overlay rendering (§4.4.8 step). Resolves pause-ad slot's `@url`. |
| PT2M10S + resolution latency — pause-ad rendered | Renders selected pause-ad form on top of paused frame. Fires pause-ad impression beacon. |
| Viewer remains paused for 20 s | Pause-ad continues. Overlay slot-window clock advances on the primary timeline (it tracks `presentationTime`, which is frozen during pause), so the overlay-slot remaining-time arithmetic uses primary clock, not wall clock. |
| PT2M30S equivalent (viewer resumes) | Dismisses pause-ad within one frame. Stops pause-ad beacons. Inspects overlay slot: `presentationTime=PT2M10S` (resume position) + 10 s consumed before pause = 10 s already played out of 20 s overlay window. Restores overlay rendering. |
| PT2M20S in primary timeline — overlay window naturally expires | Dismisses overlay. Fires overlay complete beacon if not already done. |

The overlay's slot-window clock is anchored to the primary
content timeline (`<EventStream>@timescale` ticks against
`presentationTime`). During the pause, the primary timeline is
frozen, so the overlay's remaining time does not tick down. On
resume, the overlay continues from where it was suspended and
expires at the natural end of its declared window.

### H.4 Per-device-class behaviour

| Device | Overlay rendering | On pause | On resume |
|--------|-------------------|----------|-----------|
| D1 | Highest-fidelity overlay (e.g. HTML or video). | Overlay cleared; pause-ad (HTML / image / video over paused frame) rendered. | Pause-ad dismissed; overlay restored when window remaining. |
| D2 | Video overlay via second decoder, or skipped if no video form. | Same; pause-ad declined when only HTML/image forms are present (D2 does not composite non-video on top of video / paused frame). | Overlay restored when window remaining and was originally rendered. |
| D3 | HTML or image overlay via HTML/CSS layer. | Overlay cleared; pause-ad (HTML / image) rendered. | Overlay restored when window remaining. |
| D4 | Image overlay. | Overlay cleared; pause-ad (image) rendered. | Overlay restored when window remaining. |
| D5 | Overlay declined (no overlay capability). | Pause-ad also declined; paused frame stays clean. | Nothing to restore; primary continues. |

## Annex I — Test cases and conformance criteria

This annex consolidates the test cases an implementer (Player,
Broadcaster, or ADS) can run against a candidate implementation
to assess conformance. Each test maps to one or more chapter-4
obligations and one or more chapter-8 §8.1 error rows.

### I.1 Test case index

| Test ID | Chapter / §  | Error row | Scenario | Pass criterion |
|---------|--------------|-----------|----------|----------------|
| TC-01 | §4.4.1, §6.2 | E5 | Legacy Player receives an MPD with `urn:svta:dash:event:sgai-overlay:2026` event stream. | Player ignores the event; primary content plays uninterrupted; no ADS request fired; no beacon fired. |
| TC-02 | §4.4.1, §6.2 | E1 | Player issues resolution request; ADS endpoint times out. | Player falls through to primary; no beacon fired; primary playback uninterrupted. |
| TC-03 | §4.4.1, §6.3 | E2 | ADS returns malformed XML (truncated mid-element). | Player treats as no response; falls through; logs at non-FATAL level. |
| TC-04 | §4.4.1, §6.3 | E3 | ADS returns Overlay Resolution Document with zero `<svta:Candidate>` children. | Player falls through; no beacon fired; this is conforming ADS behaviour. |
| TC-05 | §6.2 | E4 | ADS returns resolution document 200 ms after slot's `presentationTime`. | Player discards late response; falls through; subsequent slot evaluations are unaffected. |
| TC-06 | §4.4.2, §4.4.5 | E6 | Resolution document has one candidate with one form; Player's device class lacks the form's required surface. | Player skips the candidate; falls through (no further candidates). |
| TC-07 | §4.4.2 | E7 | Form's `@layout="squeezeback-frame"` but Broadcaster's `allowedLayouts="overlay-corner"`. | Player rejects the form; evaluates other forms on the candidate; falls through when no admissible form remains. |
| TC-08 | §5.3.2, §4.4.5 | E8 | Form's `@mediaType="video/webm"` (outside admissible set). | Player skips the form; evaluates remaining forms; treats candidate as E6 when no admissible form remains. |
| TC-09 | §4.4.3 | E9 | `ListMPD` declares 30 + 30 + 45 = 105 s; cap is 90 s. | Player drops the 45 s Period before play; plays the first two; resumes primary at 60 s. |
| TC-10 | §4.4.3 | E10 | `ListMPD` Period declares 30 s; actual rendered length is 35 s; cap is 30 s. | Player stops rendering exactly at 30 s; complete beacon does not fire (or fires only the impression). |
| TC-11 | §4.4.4 | — | Resolution document has 3 candidates; candidate 2 has no admissible form. | Player plays candidate 1, skips candidate 2 (the rest preserves order, i.e. candidate 3 follows). |
| TC-12 | §4.4.5 | E6 | Candidate 1 has 4 forms (video, HTML×2, image); test on D1, D2, D3, D4, D5. | D1 + D2 pick the video form; D3 picks an HTML form; D4 picks the image form; D5 falls through. (Annex C demonstrates this.) |
| TC-13 | §4.4.6, §5.5 | — | Non-linear ad accepted; overlay window 20 s. | Player fires impression beacon at form-visible; quartile beacons at 5, 10, 15 s relative to form-visible; complete at 20 s. |
| TC-14 | §4.4.6, §4.4.3 | E10 | Non-linear ad's actual length 22 s; overlay window cap 20 s. | Player trims at 20 s; complete and any beacons past 20 s do not fire. |
| TC-15 | §4.4.7 | — | Two non-linear opportunities overlap in time (overlay + pause-ad triggered by viewer pause). | Player serialises: renders the pause-ad on pause; restores the overlay on resume. Never two non-linear forms simultaneously. |
| TC-16 | §4.4.10 | E13 | Candidate carries unknown `<acme:Targeting>` element. | Player ignores it safely; candidate plays normally; no abort. |
| TC-17 | §5.1.4 | (UC-05) | Pause-trigger window 1 min 0 s to 11 min 0 s; viewer pauses at 5 min 30 s. | Player issues resolution request; renders ad on top of paused frame; dismisses on resume. |
| TC-18 | §5.1.4 | (UC-05) | Pause-trigger window 1 min 0 s to 11 min 0 s; viewer pauses at 12 min 0 s. | Player does not issue resolution request; paused frame stays on screen until resume. |
| TC-19 | §5.1.5 | (UC-04) | Two co-located events at the same `presentationTime`: one `<ReplacePresentation>`, one `<svta:OverlayPresentation>`. | Player issues two independent resolution requests; plays the linear ad with the overlay composited (where device caps allow). |
| TC-20 | §6.5 | E12 | Tracking beacon GET returns 500. | Player continues playback; beacon failure is non-fatal; no abort. |
| TC-21 | §4.4.5 | E11 | A video form's sub-MPD segment fetch returns 500 mid-playback. | Player aborts current candidate; resumes at next candidate in declared order; re-applies cap arithmetic against rendered-so-far; when no candidates remain, falls through. |
| TC-22 | §4.4.8, §7.6 | — | Overlay slot active; viewer pauses inside an overlapping pause-ad window (Annex H). | Player suspends overlay; renders pause-ad; on resume dismisses pause-ad and restores overlay when slot window remaining. Beacons fired per §4.4.6 and §4.4.8. |
| TC-23 | §4.4.9, §5.6.1 | — | Candidate carries `<svta:Click @through="..." @trackingUrl="...">`. Viewer activates the form on a CTV remote. | Player opens `@through` URL via device URL mechanism; fires `@trackingUrl` HTTP GET; non-fatal on tracking failure. |
| TC-24 | §6.3, §8.1 (E14) | E14 | Non-linear slot's resolution returns a `ListMPD` (profile mismatch). | Player falls through (treats as E14); no candidate is rendered; primary content uninterrupted. |
| TC-25 | §5.4.1 | — | Video form's `<svta:RenderableAsset>@duration="PT20S"` but sub-MPD's `<Period>@duration="PT22S"`. | Player applies drop-before-play arithmetic against PT20S (the form's declared length) and trim-during-play against PT22S (the sub-MPD's actual length), per §5.4.1. |

### I.2 Per-chapter conformance highlights

| Chapter | Obligations |
|---------|-------------|
| 4 (Conformance) | Three-actor split; Broadcaster declares constraints; ADS returns candidates; Player validates and enforces. |
| 5 (Syntax) | Foreign-namespace open content under `urn:svta:dash:sgai:2026`; year-pinned scheme URIs for event streams; preferred token-list encoding (single attribute, space-separated). |
| 6 (Interfaces) | HTTP(S) pull semantics on every interface; HTTP status code semantics for ADS responses; segment-level retry follows DASH-IF guidance. |
| 7 (Behaviour) | Player selection algorithm: walk candidates in declared order, walk forms by `@priority`, intersect device caps × `allowedLayouts` × form admissibility; honour declared candidate order. Pause-and-overlay composition: pause-ad has priority; overlay restored on resume. |
| 8 (Implementation notes) | Non-normative guidance on error surfacing, tracking-only VAST inputs, late callbacks, single-decoder pause-ad behaviour, speculative pre-fetch, image-form intrinsic duration, degenerate authoring cases. |

### I.3 Final notes

The error matrix and the test cases are intentionally
intertwined. Each error condition has at least one test case
that exercises it; each test case has at least one error row
that documents the expected behaviour. An implementer who runs
all twenty-five test cases successfully has covered the
principal conformance surface. The matrix and the per-test
mappings provide the audit trail.

This edition's normative surface is closed by chapters 4 to 7
and the syntactic content of chapter 5. Chapter 8 is
non-normative but useful; the annexes are informative but
mandatory to ship. A future edition that changes the semantics
of any construct introduced here publishes under a new
year-pinned URI (§4.5).

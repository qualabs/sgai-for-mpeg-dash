# SGAI for Linear and Non-Linear Ads in MPEG-DASH

> - Minor refinement v7.1 -> v7.2: issues raised by
>   `v7.1-spec-validation.md`, `v7.1-detail-review.md` and
>   `v7.1-dash-conformance-audit.md`, applied without changing
>   requirements or architecture. Every edit is annotated inline with
>   an HTML comment naming the issue id it comes from.
> - Generated against MPEG-DASH 6th edition (ISO/IEC 23009-1:2026,
>   Sixth edition, 2026-07).
> - RFC 2119 keywords (MUST, SHOULD, MAY) appear throughout the
>   normative chapters. Their meaning is inherited from RFC 2119 and
>   RFC 8174. Normative obligations are stated as positive
>   requirements — the action the actor takes. The space outside the
>   positive obligation is implicitly out of scope.
> - Grounding: the MPEG-DASH 6th edition claims in this document were
>   checked against the authoritative source. Claims that could not be
>   verified against it are tagged `[inferred]`.

## 1. Scope

This specification defines **Server-Guided Ad Insertion (SGAI)** in
MPEG-DASH for **both linear and non-linear ads**, as a complete
extension of MPEG-DASH 6th edition.

<!-- refine: v7-dash-conformance-audit.md#M9 -->
<!-- refine: v7-spec-validation.md#T5 -->
Linear SGAI already exists in ISO/IEC 23009-1:2026 — the
`<InsertPresentation>` and `<ReplacePresentation>` events of §5.16 and
the List MPD profile of §8.14 — and is absorbed here as the baseline.
This specification carries it forward with clarifications and the
minor extensions the non-linear work surfaced, and it alters no
baseline construct semantics, with one declared exception: the
narrowing of the alternative-MPD fall-through condition stated in
§4.6.8.

The **non-linear extension is the principal new content**: an
opportunity declaration for overlays and for pause-triggered ads, a
resolution document in which one ad candidate offers an ordered list
of renderable presentation options, a normative ClickThrough carrier,
a reserved set of device-capability parameters on the resolution
request, and the composition rules that bound what reaches the screen.
Every new construct is expressed through a DASH 6th edition extension
point whose ignore-if-unknown semantics make backward compatibility
auditable construct by construct.

A conformant implementation of this specification:

- Plays primary content uninterrupted on a Player that does not
  implement the constructs introduced here.
- Preserves the semantics of every pre-existing MPEG-DASH 6th edition
  construct.
- Keeps primary-content playback intact when an ad opportunity cannot
  be honoured, at authoring time or at runtime.

Audience: Player implementers, ad-server vendors, publisher authoring
teams, and DASH-aware tooling authors. The reading prerequisite is
familiarity with MPEG-DASH 6th edition §5.2.1, §5.10, §5.16, §8.14 and
§8.15.

### 1.1 What this specification covers

- Linear ad slots — pre-roll, mid-roll and multi-ad break — carried by
  the MPEG-DASH 6th edition `<InsertPresentation>` and
  `<ReplacePresentation>` events and resolved through a `ListMPD`.
- Non-linear overlay slots carried by the `<svta:OverlayPresentation>`
  event element.
- Pause-triggered ad windows carried by the
  `<svta:PauseAdPresentation>` event element.
- Hybrid slots — a linear slot and a non-linear overlay slot declared
  at the same position on the primary timeline, composed during the
  same break.
- The squeezeback family: the L-shape (a full-frame ad creative with
  the shrunk primary content composited on top) and the side-by-side /
  double-box (two boxes plus an advertiser background element filling
  the bands they leave uncovered).
- Device-aware resolution of one ad across heterogeneous devices,
  through an ordered list of presentation options the Player walks,
  and through the reserved capability parameters the Player MAY
  declare on the resolution request so the APS can resolve the choice
  upstream instead.
- The ClickThrough and its click-tracking, carried normatively so
  every conformant Player fires them identically.
- Tracking beacons for linear and non-linear ads, carried on the
  baseline DASH callback event scheme.
- The distinction between an opportunity that resolved to no ads and
  one that failed to resolve.

### 1.2 What this specification leaves out of scope

- Server-side ad insertion and stitching (SSAI / SSR). This edition
  covers client-side ad rendering.
- Post-roll slots.
- Ads rendered off the video surface: menu / guide / EPG ads,
  home-screen and launcher ads, screensaver ads, and companion /
  multi-screen ads. They live in the Player chrome or the application
  UI, not on the playing or paused video, and belong to the
  application's ad integration.
- Ads composited into the content upstream of the Player (in-scene /
  virtual signage).
- A parallel spatial-layout system. Spatial arrangement of overlays is
  delegated to HTML5 / CSS layout primitives; positions inside a
  layout (left, right, top, bottom) are not expressible in spec-level
  attributes, and the spatial bounds of each accepted layout are
  inherited by normative reference from the IAB CTV guidelines rather
  than re-declared here.
- The ADS's internal decisioning logic — targeting, frequency capping,
  brand-safety filtering, competitive separation, ordering.
- The APS-to-ADS and ADS-side API contracts. This specification
  documents only the **Player-visible** interface: the MPD event URL
  the Publisher references, which resolves to the APS; the parameters
  the Player attaches to its resolution request; and the resolution
  document the APS returns. The Publisher↔APS arrangement for the
  event URL, and the APS↔ADS decisioning exchange, are agreed
  bilaterally outside this specification.
- Creative carriers outside the admissible set of §3.3 — raw
  `application/javascript`, SVG-as-payload, PDF, proprietary binary
  creatives. A sender that needs a scripted creative wraps the script
  inside an HTML document and uses `text/html`.
- Interactive ad frameworks such as SIMID. An ad built on one is
  delivered by that framework; this edition defines no non-linear form
  that carries such a payload.
- Simultaneous presentation of two or more non-linear ad forms. At any
  instant at most one non-linear ad form is active on screen (§4.6.7).
  A future edition MAY relax this and introduce concurrency semantics
  with explicit conflict-resolution and decoder-budget rules.
- Single-decoder slice or tile replacement, in which one decoder
  carries both the primary content and the ad. The technique exists
  and is most practical in HEVC and AV1; this edition's
  decoder-budget reasoning assumes one decoder per concurrent form.
- Audio composition policy between an overlay's audio track and the
  primary content's audio track. A future edition MAY introduce a
  normative policy.
- Authentication, DRM, encryption and token-exchange flows. They layer
  on top of HTTPS per DASH-IF guidance and are orthogonal to SGAI.

## 2. Normative references

The following documents, in whole or in part, are normatively
referenced in this specification and are indispensable for its
application. For dated references, only the cited edition applies. For
undated references, the latest edition (including amendments) applies.

<!-- refine: v7-detail-review.md#flag-4 -->
A reference of the form §N or Annex X, given without qualification, is
to this document. A reference to the base specification always names
it.

<!-- refine: v7-dash-conformance-audit.md#M9 -->
- **ISO/IEC 23009-1:2026(en)** — *Information technology — Dynamic
  adaptive streaming over HTTP (DASH) — Part 1: Media presentation
  description and segment formats* (MPEG-DASH 6th edition, Sixth
  edition, 2026-07). Canonical:
  <https://standards.iso.org/iso-iec/23009/-1/ed-6/en>. Referred to
  throughout this document as **the base specification**. Clauses
  referenced normatively:

  | Clause | Subject |
  |---|---|
  | §4.7, §5.10.4.5 | Callback event scheme `urn:mpeg:dash:event:callback:2015` |
  | §5.2.1 | Foreign-namespace open content, and the whole-subtree discard of an unimplemented foreign element |
  | §5.3.2.2 | `Period` and `AdaptationSet` cardinality |
  | §5.3.2.6 | `<ImportedMPD>` and its binding to the Single-Period Static profile |
  | §5.3.7.2 | `@selectionPriority`, `@maxPlayoutRate` |
  | §5.3.11 | `Preselection` |
  | §5.6 | `BaseURL` alternatives and `@serviceLocation` |
  | §5.8.4.8, §5.8.4.9 | `<EssentialProperty>` and `<SupplementalProperty>` descriptors |
  | §5.10 | `<EventStream>`, `<Event>`, and the per-scheme ignore-if-unknown rule |
  | §5.11.3 | MPD fallback scheme `urn:mpeg:dash:fallback:2016` |
  | §5.16 | Alternative Media Presentations: §5.16.2.2 the execution model, §5.16.3 `<InsertPresentation>`, §5.16.4 `<ReplacePresentation>`, §5.16.5.2 the `@maxDuration` termination rule |
  | §7.3 | MIME-type restriction inherited by single-period profiles |
  | §8.12 | CMAF-based profiles |
  | §8.14 | List MPD profile, URI `urn:mpeg:dash:profile:list:2024` |
  | §8.15 | Single-Period Static profile, URI `urn:mpeg:dash:profile:sps:2024` |
  | Annex F | Non-ISO-BMFF delivery formats and Interoperability Point URIs |
  | Annex H | Spatial Relationship Description `urn:mpeg:dash:srd:2014` |
  | Annex I | Extended HTTP GET parameterisation, scheme `urn:mpeg:dash:urlparam:2025`, and the I.4 state vocabulary |
  | Annex K | `<PlaybackRate>` |
  | Annex L | `urn:mpeg:dash:nonlinearplayback:2020` |

- **IETF RFC 2119** — *Key words for use in RFCs to Indicate
  Requirement Levels*. <https://www.rfc-editor.org/rfc/rfc2119>.
- **IETF RFC 8174** — *Ambiguity of Uppercase vs Lowercase in RFC 2119
  Key Words*. <https://www.rfc-editor.org/rfc/rfc8174>.
- **IETF RFC 4337** — *MIME Type Registration for MPEG-4*. Pins the
  admissible `@mimeType` values on `<AdaptationSet>` and
  `<Representation>` inside any document bound to the Single-Period
  Static profile to `video/mp4`, `audio/mp4` and `application/mp4`.
  <https://www.rfc-editor.org/rfc/rfc4337>.
- **IETF RFC 6381** — *The "Codecs" and "Profiles" Parameters for
  "Bucket" Media Types*. Governs the `@codecs` strings authored in
  every MPD this specification defines.
  <https://www.rfc-editor.org/rfc/rfc6381>.
- **IAB Tech Lab — Ad Format Guidelines for Digital Video and CTV**
  (Final Release, May 2026). Live source:
  <https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e>.
  Authoritative source for the ad-type and visual-placement vocabulary
  accepted by §3.2, and for the spatial bound each accepted placement
  carries. The reference is to the live document, not to a snapshot,
  because the IAB owns the vocabulary's lifecycle; the subset this
  edition accepts is nevertheless fixed by §3.2 and does not widen
  when the IAB publishes a new type.
- **W3C HTML Living Standard** — <https://html.spec.whatwg.org/>.
  Defines `text/html` semantics, including inline `<script>`
  execution.
- **W3C CSS layout modules** — the spatial arrangement of overlays is
  delegated to them; this specification defines no layout primitive of
  its own.

### 2.1 Scheme URIs and namespaces introduced by this edition

The URIs below are introduced normatively by this edition. A Player
implementing this edition recognises them. The year suffix is the
edition year: a future edition that changes the semantics of a
construct publishes it under a new URI, so a Player that recognises
only the older URI keeps applying the older semantics, and a Player
that predates this edition entirely ignores the construct.

| URI | Used as | Construct |
|-----|---------|-----------|
| `urn:svta:dash:sgai:2026` | XML namespace (prefix `svta:` throughout this document) | The SVTA Ads WG extension namespace. Every XML element and attribute this edition introduces lives in it. |
| `urn:svta:dash:event:sgai-overlay:2026` | `<EventStream>@schemeIdUri` | The Publisher's non-linear overlay opportunity declaration (§5.1.3). |
| `urn:svta:dash:event:sgai-pause-trigger:2026` | `<EventStream>@schemeIdUri` | The Publisher's pause-trigger window declaration (§5.1.4). |
| `urn:svta:dash:profile:sgai-overlay-list:2026` | `MPD@profiles` on a non-linear resolution document | Declares a resolution document conforming to §5.2.2. |

URIs inherited unchanged from the base specification —
`urn:mpeg:dash:event:alternativeMPD:insert:2025`,
`urn:mpeg:dash:event:alternativeMPD:replace:2025`,
`urn:mpeg:dash:event:callback:2015`,
`urn:mpeg:dash:profile:list:2024`,
`urn:mpeg:dash:profile:sps:2024`,
`urn:mpeg:dash:urlparam:2025` — keep their baseline URIs and their
baseline semantics. This edition introduces no tracking scheme: the
callback scheme is reused as-is.

Vendor-private experimental constructs that are not part of this
specification live under a vendor namespace of the form
`urn:<vendor>:<feature>:<year>` and are not normative here.

## 3. Terms, definitions, abbreviations

### 3.1 Core terms

- **Ad opportunity (slot).** A position on the primary content
  timeline at which the Publisher permits an ad to be rendered.
  Declared as an `<Event>` inside an `<EventStream>` whose
  `@schemeIdUri` identifies the slot family — linear insert, linear
  replace, non-linear overlay, or pause trigger. The event's
  scheme-specific child element carries the slot's constraints.
- **Slot family.** One of the three categories of ad opportunity this
  specification defines: **linear**, **overlay**, and **pause ad**.
  The family governs which constructs may appear on the slot, which
  resolution document the slot resolves to, and how two overlapping
  windows relate (§4.6.8).
- **Linear ad.** An ad whose form takes over the primary content
  surface for the duration of the slot. The Player switches its
  rendering source from the main timeline to the ad timeline and back.
- **Non-linear ad.** An ad that coexists with the primary content:
  composited on top of it, or presented alongside it with the primary
  content shrunk to share the frame, without interrupting playback.
- **Resolution request.** The HTTP GET the Player issues against the
  slot's `@uri` when the playhead reaches the slot's Earliest
  Resolution Time. The Player MAY attach the reserved capability
  parameters of §5.8.
- **Resolution document.** The XML document the APS returns in
  response to the resolution request. For a linear slot it is a
  `ListMPD` (§5.2.1). For an overlay or pause-ad slot it is an
  Overlay Resolution Document (§5.2.2).
- **Candidate.** One ad offered for the slot by the resolution
  document. A candidate carries one or more renderable presentation
  options. In a linear `ListMPD` the Periods are played in declared
  order rather than selected among; the selection sense of "candidate"
  applies to the non-linear document.
- **Form.** The creative-carrier dimension of a presentation option: a
  single media type drawn from the admissible set of §3.3 — `video`,
  `image` or `html`.
- **Layout.** The spatial-arrangement dimension of a presentation
  option, identified by a token that maps 1:1 to an IAB-defined ad
  type or visual placement (§3.2). Positioning inside a layout is
  delegated to HTML5 / CSS and is out of scope here.
- **Presentation option.** A `(form + layout)` pairing carried on a
  candidate. A candidate carries one or more, as an **ordered list**
  whose document order is the preference order. A candidate carrying
  exactly one option leaves the choice with the APS, or with the ADS
  that returned a single option to it.
- **Capability parameter.** A reserved query parameter the Player MAY
  attach to the resolution request, stating what its device can render
  (§5.8). Sending any of them is optional; a parameter the Player
  cannot or will not populate is omitted rather than sent empty, and
  an absent parameter means its value is **undetermined**, not that
  the device lacks the capability.
- **Publisher.** The party that owns the primary content and the
  viewer's screen. Declares ad opportunities and their constraints in
  the main MPD. Authority for *when* an ad may appear, *what kind* of
  slot it fills, and *what constraints* bind the slot.
- **Ad Decision Server (ADS).** The server that decides which ads to
  serve, how many, and in what order, and that declares the tracking
  schedule. Emits a decision document — typically VAST, though it is
  not bound to VAST. It does not produce the resolution document the
  Player reads, and it is not normatively bound by the Publisher's
  slot constraints.
- **Ad Presentation Server (APS).** The server between the Player and
  the ADS. Exposes the endpoint the Publisher references in the slot's
  `@uri`, obtains the ADS's decision, and converts it into the
  resolution document the Player understands. Translates the
  ADS-declared tracking events into DASH callback events. A
  translation and presentation layer, not the ad-decisioning authority
  and not the constraint enforcer.

  In real deployments the APS is often a module of the ADS rather
  than a separately deployed service. This specification presents it
  as a distinct actor to describe its responsibilities clearly,
  independent of how it is ultimately implemented.
- **Player.** The client that reads the main MPD, issues the
  resolution request, validates the resolution document against the
  Publisher's constraints, selects and composes the ad, and executes
  the tracking schedule. Enforcer of the Publisher's policy.
- **Slot cap.** The maximum duration the Publisher declares on every
  ad opportunity, linear or non-linear, as `@maxDuration` on the
  slot's scheme-specific child element. The Player enforces it against
  actual rendered length, trimming mid-ad when required.
- **Earliest Resolution Time (ERT).** The earliest instant at which
  the Player issues the resolution request for a slot, computed as the
  slot event's `presentationTime` minus its
  `@earliestResolutionTimeOffset`.
- **Tracking carrier.** The construct that conveys timeline-scheduled
  beacons — impression, start, quartiles, complete. This specification
  reuses the baseline callback event scheme
  `urn:mpeg:dash:event:callback:2015` for linear and non-linear ads
  alike, and introduces no scheme of its own (§5.5).
- **Fall through.** The Player declines the opportunity and primary
  content continues uninterrupted, with no visible artefact and no
  beacon fired for the declined opportunity. Distinct from advancing
  to the next candidate, which stays inside the same opportunity
  (§4.6.6).
- **Sub-MPD.** An MPD reached through `<ImportedMPD>` from a parent
  document — a `ListMPD` Period for a linear ad, or a video
  presentation option for a non-linear one. Bound by §5.3.2.6 of the
  base specification to the Single-Period Static profile, and
  therefore to `video/mp4`, `audio/mp4` and `application/mp4` on every
  Representation's `@mimeType`.
- **Background element.** The still image that fills the bands a
  side-by-side / double-box layout leaves uncovered. It is the
  advertiser's creative and a composition attribute of the layout, not
  one of the candidate's alternative presentation options (§5.3.7).

  <!-- refine: v7-detail-review.md#flag-1 -->

### 3.2 Accepted ad-type and visual-placement values

Ad types and their visual templates are defined and maintained by the
IAB. This specification references those definitions normatively and
introduces no ad-type category and no visual template of its own.

On top of that principle, this edition accepts an explicit **closed
subset** of the IAB catalogue: four ad types, all rendered on or
within the video surface. The table below is the complete set a
conformant Publisher, APS and Player handle under this edition. Each
row names the IAB ad type it maps to and, where the IAB type has named
visual placements, the placement.

The enumeration is edition-scoped by design. An IAB ad type or visual
placement absent from the table is out of scope for this edition, and
a type or placement the IAB publishes later does not enter scope
automatically; widening the set requires a new edition of this
specification. This is a deliberate per-edition snapshot, not a
runtime limitation to work around.

| Token | IAB ad type | IAB visual placement | Where it appears |
|---|---|---|---|
| `linear` | Linear Ad | Full viewing pane | Linear slots. Also the full-screen takeover offered as a last-resort presentation option on a non-linear candidate: a placement of `linear`, not a separate ad type. |
| `overlay` | Overlay | (none — plain image or HTML overlay) | Overlay slots. |
| `overlay-corner` | Overlay | Corner Overlay | Overlay slots. |
| `overlay-lower-third` | Overlay | Lower Third Overlay | Overlay slots. |
| `squeezeback-l-shape` | Squeezeback | L-Shape | Overlay slots. One full-frame ad creative with the shrunk primary content composited on top (§5.3.7.1). |
| `squeezeback-double-box` | Squeezeback | Double Box Video | Overlay slots. Two boxes; the uncovered bands render as black when the advertiser supplies no background element (§5.3.7.2). |
| `squeezeback-double-box-with-background` | Squeezeback | Double Box Video + Background | Overlay slots. Same two boxes with an advertiser-supplied background element filling the uncovered bands (§5.3.7.2). |
| `pause-ad` | Pause Ad | Fullscreen or Partial Screen | Pause-ad slots. Which surface applies is a property of the option the Player selects (§7.5.5). |

The tokens above are the complete admissible value space for
`@allowedLayouts` on a slot declaration (§5.1.3, §5.1.4) and for
`@layout` on a presentation option (§5.3.1). The matching rule the
Player applies is **exact-token enumeration**: an `@allowedLayouts`
declaration admits exactly the tokens it lists literally. `overlay`
does not implicitly admit `overlay-corner`; a Publisher who wants both
lists both.

Each token carries the spatial bound the IAB CTV Ad Format Guidelines
declare for that placement — for example a Corner Overlay occupying no
more than 25 % of the frame, or a Squeezeback L-Shape leaving the
primary content at 60 % of the frame. Those bounds are inherited by
normative reference to the IAB document (§2). This specification
introduces no dimensional attribute on the slot declaration and
re-declares no dimension of its own.

IAB ad types outside the table — Menu Ad, Screen Saver Ad, Companion
Ad, In Scene Ads — are out of scope for this edition (§1.2). Because
the accepted set is closed, anything not listed is already out of
scope; §1.2 names the off-video-surface category explicitly so the
exclusion is unambiguous.

Interactivity is orthogonal to the ad type. The IAB document describes
it in its own sections and it is not an ad type; this specification
carries it, when present, inside the creative payload and not as slot
or option metadata.

### 3.3 Admissible creative carriers

<!-- refine: v7-detail-review.md#flag-1 -->
The admissible creative-carrier formats for this edition are exactly
three. They are the value space of `@form` on a presentation
option (§5.3.1).

| `@form` | Carrier | Concrete media types |
|---|---|---|
| `video` | ISO-BMFF video, carried as a sub-MPD reached through an `<ImportedMPD>` child (§5.4) | `video/mp4`, `audio/mp4`, `application/mp4` on the sub-MPD's Representations, per RFC 4337 |
| `image` | Still image at a flat HTTP(S) URL carried on the option itself | `image/jpeg`, `image/png`, `image/webp` |
| `html` | HTML document at a flat HTTP(S) URL carried on the option itself | `text/html`. Inline `<script>` MAY appear and runs under the device's HTML capability contract per the HTML Living Standard; the script is not a separate carrier. |

New carrier types are not added in annexes, examples or
implementation notes. A sender that needs a scripted creative wraps
the script inside an HTML document and uses `@form="html"`.

### 3.4 Device classes

This specification enumerates five device classes, in decreasing order
of rendering capability. A class captures only the two axes that
govern what an ad form can do on screen: how many video decoders the
device runs concurrently, and which surface types it composites on top
of video. Codec support, DRM and network conditions are orthogonal and
are not part of the classification.

| Class | Concurrent video decoders | Image surface over video | HTML surface over video |
|---|---|---|---|
| **D1** — top tier | 2 or more | Yes | Yes |
| **D2** | 2 | No | No |
| **D3** | 1 | Yes | Yes |
| **D4** | 1 | Yes | No |
| **D5** — worst case | 1 | No | No |

D2 is the instructive class: it composites **video on video** using
its second decoder, and composites no non-video surface at all.

The Player is the sole authority on what its own device can render.
Neither the ADS nor the APS is required to hold a device-class matrix
or a per-Player capability view; an implementation whose APS does hold
one is equally conformant, and the Player's own check is unchanged
either way (§4.6.5).

The two axes above are what the reserved capability parameters of §5.8
express, and the acceptance test for that parameter set is that it
tells these five classes apart.

### 3.5 Abbreviations

- **ADS** — Ad Decision Server.
- **APS** — Ad Presentation Server.
- **CMAF** — Common Media Application Format (ISO/IEC 23000-19).
- **CTV** — Connected TV.
- **DASH** — Dynamic Adaptive Streaming over HTTP.
- **ERT** — Earliest Resolution Time.
- **IAB** — Interactive Advertising Bureau (Tech Lab).
- **MPD** — Media Presentation Description, the DASH manifest.
- **SGAI** — Server-Guided Ad Insertion.
- **SPS** — Single-Period Static profile (§8.15 of the base
  specification).
- **SVTA** — Streaming Video Technology Alliance.
- **VAST** — Video Ad Serving Template (IAB Tech Lab). Referenced
  illustratively only; this specification depends on no VAST version
  and does not require VAST anywhere.

## 4. Conformance

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL
NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY** and
**OPTIONAL** in this specification are to be interpreted as described
in RFC 2119 and RFC 8174, when, and only when, they appear in all
capitals.

Every obligation in this chapter is stated as a **positive**
obligation: the action an actor takes, the construct an authoring
party produces, the value a Player computes. The space outside the
positive obligation is implicitly out of scope. This is deliberate:
the set of forbidden behaviours is unbounded, and a long enumeration
of prohibitions invites both confusion and silent gaps, while the
positive obligation defines the contract exactly.

### 4.1 Conformance scope

An implementation claiming conformance to this specification
implements one or more of the four actor roles — Publisher, ADS, APS,
Player — and satisfies the positive obligations of every role it
implements. An implementation MAY implement several roles; a
deployment in which the APS is a module of the ADS satisfies the
obligations of both.

Conformance is checked against **artefacts this specification
defines**:

- For the Publisher, the main MPD it authors.
- For the APS, the resolution document it returns.
- For the Player, its observable runtime behaviour.
- For the ADS, the obligations below and nothing else: its decision
  document is not an artefact this specification defines, and reaches
  the Player only through the APS.

Three obligations are **document-level** — they bind this
specification rather than any implementation, and are satisfied by the
text itself: that every new construct is expressed through a base
specification extension point (§4.7), that no pre-existing base
specification semantics are altered other than the single narrowing
declared in §4.6.8, and that every new construct
carries an inline justification for why an existing construct was not
reused (§5).

### 4.2 The four-actor contract

The separation below is normative. A mechanism that would require an
actor to take on a responsibility outside its role is outside this
specification.

| Decision | Actor |
|---|---|
| *When* an ad opportunity appears on the timeline | Publisher |
| *Which* slot family, and what constraints bind the slot — allowed layouts and duration cap | Publisher | <!-- refine: v7-spec-validation.md#T3 -->
| *Which* ads are eligible, *how many* fill a multi-ad opportunity, and *in what order* | ADS |
| Targeting, frequency capping, brand-safety filtering, competitive separation | ADS |
| The tracking schedule: which beacons fire and at which relative times | ADS |
| Converting the decision into the resolution document the Player reads | APS |
| Translating the ADS's tracking events into DASH callback events in that document | APS |
| *What the Player discloses about its device* on the resolution request | Player |
| *Validating* each candidate against the Publisher's declared constraints | Player |
| *Selecting* the ad and the presentation option to render | Player |
| *Compositing and rendering* the ad over the primary content | Player |

Authority over the on-screen experience is held jointly by the
Publisher, who declares, and the Player, who enforces. Neither the ADS
nor the APS is normatively bound by the slot constraints. That
separation is what lets one ADS serve several Publishers, through
their APSs, under heterogeneous policies, and lets a Player guarantee
the Publisher's constraints even when the ADS and the APS are
external, non-audited services.

### 4.3 Publisher obligations

A conformant Publisher:

**4.3.1** Declares every ad opportunity in the main MPD as an
`<Event>` inside an `<EventStream>` of the scheme corresponding to the
slot family (§5.1), so that the constraints applicable to the slot are
read from the manifest rather than inferred at runtime by the ADS, the
APS or the Player.

**4.3.2** Declares `@maxDuration` on every ad slot it authors, linear
or non-linear (§5.1).

**4.3.3** Declares, on every non-linear slot, the `@allowedLayouts`
token list that bounds the slot, drawing every token from the
enumeration of §3.2 (§5.1.3, §5.1.4).

**4.3.4** Declares `@uri` on every slot, resolving to the APS endpoint
that answers the resolution request for that slot.

**4.3.5** Declares `@earliestResolutionTimeOffset` on every slot with a
value that leaves the APS a usable head start before the slot's
`presentationTime`.

**4.3.6** Expresses every SGAI construct it authors through one of the
base specification extension points enumerated in §4.7, so that a
Player that does not implement the construct ignores it and keeps
playing the primary content.

**4.3.7** For **VOD** content (`MPD@type="static"`), MAY author a
standard linear break using baseline constructs alongside an SGAI
opportunity, so that a Player predating this specification plays the
standard break while a Player implementing this specification takes
the SGAI path. Where monetising the opportunity on legacy Players
matters, the Publisher SHOULD author it: the Publisher cannot detect a
viewer's Player version from the manifest, so the fallback is authored
unconditionally and is simply ignored by Players that take the SGAI
path.

**4.3.8** For **live** content (`MPD@type="dynamic"`), treats an
opportunity that falls through on a legacy Player as an expected loss.
Live content cannot be held to splice in a standard break without
losing real content, so skip-and-continue is the outcome the Publisher
authors for (§7.5.7).

**4.3.9** When it declares two or more opportunity windows of the same
slot family overlapping in time, authors them as a **chain**: the
first window is the one to serve and the remaining ones are fallbacks
(§4.6.8).

**4.3.10** When it declares a slot whose `@allowedLayouts` includes a
side-by-side / double-box token, understands that the background
element filling the uncovered bands is the advertiser's creative, and
declares no dimension for it (§5.3.7.2).

### 4.4 ADS obligations

A conformant ADS:

**4.4.1** Decides which ads to serve for an opportunity, how many, and
in what order, and emits them in its decision document.

**4.4.2** Declares the tracking schedule in that decision document —
which beacons exist, and at which times relative to the ad's
presentation. The ADS holds authority over the schedule; the Player
executes what reaches it, and this specification fixes the carrier and
the timebase rather than the fractions, the granularity or the beacon
count.

**4.4.3** Is free to select candidates whose cumulative duration
exceeds the Publisher's declared cap. A conformance check on the ADS
succeeds regardless of that overflow: the cap is the Player's to
enforce (§4.6.4).

**4.4.4** Produces its decision without a device-class matrix and
without a per-Player capability view. An ADS that maintains one is
equally conformant; neither is required.

**4.4.5** Treats a decision that carries no ads as a legitimate
outcome. No-fill is a decision, not a failure (§4.5.7).

**4.4.6** Is bound to no ad-decisioning protocol by this
specification. VAST is the de-facto upstream format and appears in
this document illustratively only.

### 4.5 APS obligations

Conformance for the APS is checked against the **resolution document**
it returns, which is the only artefact on the path to the Player that
this specification defines. A conformant APS:

**4.5.1** Answers the resolution request with a resolution document of
the profile that matches the slot family: a `ListMPD` (§5.2.1) for a
linear slot, an Overlay Resolution Document (§5.2.2) for an overlay or
pause-ad slot.

**4.5.2** Emits a document that is valid against the base
specification schema, extended only through the extension points of
§4.7.

**4.5.3** Carries each candidate's presentation options as an
**ordered list** whose document order is the preference order (§5.3.5).
How many options a candidate carries is the APS's decision: this
specification sets no maximum and no minimum beyond one. Carrying
several is the form this specification asks for, because a candidate
with several resolves on devices the ADS and the APS know nothing
about. Carrying exactly one is equally admissible, and the
responsibility for that option's suitability then sits with the APS,
or with the ADS that returned a single option to it.

**4.5.4** Emits form metadata only for the ad types and visual
placements enumerated in §3.2, and creatives whose media type falls in
the admissible set of §3.3.

**4.5.5** Carries every non-AV asset URL — image and HTML — on one of
the DASH-conformant carriers of §5.3.2, which keeps it off the
`@mimeType` axis bound by RFC 4337 (§4.7.2).

**4.5.6** Expresses the tracking instructions it received as `<Event>`
entries inside an `<EventStream>` of scheme
`urn:mpeg:dash:event:callback:2015`, timed relative to the ad's
presentation timeline (§5.5). This specification introduces no
tracking scheme, and conformance is checked against the document
alone: the document fixes the form the instructions take and the
timebase they use, and it does not reveal how many beacons the ADS
declared.

**4.5.7** Expresses an opportunity that resolved to **no ads** as a
resolution document carrying no candidates, with an HTTP `200` status
and a body (§5.2.3). That is what lets an unfilled opportunity be
reported as unfilled rather than as a failure to resolve.

**4.5.8** When a candidate carries a ClickThrough, carries the
ClickThrough URL and any click-tracking URLs accompanying it in the
carrier of §5.6, so that every conformant Player reads them the same
way. Whether a ClickThrough has any associated click-tracking URL is
the advertiser's decision and is not constrained here.

**4.5.9** Produces candidates for a resolution request that carries
**none** of the reserved capability parameters of §5.8, and tolerates
the absence of any individual one. An APS that required a parameter in
order to answer would make the parameters' optionality unattainable
for the Player.

**4.5.10** When the resolution request does carry capability
parameters, MAY narrow the options it emits to those the declaration
admits, and emits the surviving options in the order the ADS gave
them. How an APS resolves a parameter whose value is undetermined —
because the Player omitted it — is the APS's decision, and two APSs
that resolve it differently are both conformant (§5.8.4).

**4.5.11** Declares, for each non-linear candidate, the candidate's
duration, so the Player can evaluate the slot cap before playback
(§5.2.2.4).

Two fidelity properties are **outside** this specification and belong
to the APS-to-ADS contract the two parties maintain directly: that the
APS neither adds, removes nor reorders the beacons the ADS declared,
and that a ClickThrough the ADS declared reaches the resolution
document at all. The ADS declares both and receives their results, so
it is in a position to enforce them; the resolution document is not,
because it does not show what was declared.

### 4.6 Player obligations

A conformant Player:

#### 4.6.1 Reads and validates

Reads the main MPD, parses the slot constraints the Publisher declared
for each opportunity, resolves the slot's `@uri` at or after the
Earliest Resolution Time, and validates each candidate in the returned
document against those constraints before anything reaches the screen.
A candidate that satisfies the constraints is eligible; one that does
not is passed over in favour of the next (§4.6.6).

#### 4.6.2 Keeps primary-content playback intact

Continues playing the primary content uninterrupted whenever an ad
opportunity cannot be honoured — at authoring time, at resolution
time, or at runtime. This includes an unknown construct in the
manifest, a resolution request that fails, a document that carries no
usable candidate, and an accepted ad that fails while being resolved
or rendered (a decode error, a malformed candidate, a mid-ad network
loss). The Player aborts the ad and keeps the primary content running.

This is the floor of the whole specification: applying it never breaks
primary-content playback, and an opportunity that cannot be honoured
degrades into a graceful skip.

#### 4.6.3 Ignores what it does not implement

Ignores an event scheme, an extension element or a namespace it does
not implement, together with its whole subtree, and keeps playing the
primary content. This behaviour is the base specification's, inherited
rather than invented (§4.7).

#### 4.6.4 Enforces the slot cap

Enforces the Publisher-declared `@maxDuration` on every slot:

- **Drop before play.** The Player MAY drop a candidate whose
  **declared** duration would push the cumulative slot duration past
  the cap.
- **Trim during play.** When the **actual** rendered length of an
  accepted candidate reaches the cap, the Player stops rendering at
  the cap boundary, even when the stop falls mid-ad, and enforces
  against actual length rather than declared length.
- The Player keeps the slot within the cap regardless of the metadata
  the ADS produced or the number of candidates the document carries.
- On a non-linear slot whose document declares a sequence of forms,
  the cap is enforced against the **cumulative** duration of the
  sequence (§4.6.7).

When the Player trims an ad, it stops firing that ad's remaining
beacons at the trim boundary (§4.6.10).

#### 4.6.5 Selects the presentation option

For each eligible candidate, walks the candidate's presentation
options **in document order** and renders the **first** option that
satisfies both:

1. the device's own capabilities — the form's decoder-and-surface
   budget (§5.3.7.3) against what the device runs; and
2. the slot's `@allowedLayouts`, matched as an exact token.

The Player renders that option and stops walking. Document order is
the only ordering input: this specification carries no priority or
ranking attribute on an option.

No presentation option reaches the screen without passing this check.
That holds equally for an option the APS computed from the Player's
own declared capabilities (§5.8): declaring narrows what arrives, and
does not make what arrives authoritative. If the device's state
changed between the request and the render, or the APS derived an
option the device cannot satisfy, the Player passes over the candidate
as it would any other.

#### 4.6.6 Preserves the document's order, and falls through candidate by candidate

Plays the candidates in the order the resolution document declares.
The Player MAY drop a candidate that has no satisfiable presentation
option, and MAY drop one whose declared duration would overflow the
cap; the candidates that survive keep their declared order, with no
re-ordering and no deduplication applied to them.

When no option on a candidate is satisfiable, the Player advances to
the **next candidate** in the document. It continues with the primary
content once every candidate has been exhausted — falling through to
primary content is the last resort, not the first response to a
candidate that does not fit.

#### 4.6.7 Keeps one non-linear form on screen

Keeps **at most one** non-linear ad form active on the screen at any
instant `t`.

<!-- refine: v7-spec-validation.md#T1 -->
A non-linear slot MAY be filled by several forms played in sequence:
when the resolution document declares more than one **candidate** for
one slot, the Player presents them one after another, in the order the
candidates appear in the document, each starting when the previous one
ends —
the same ordering contract that governs linear candidates. The slot
cap applies to their cumulative duration (§4.6.4).

The bound exists for device-resource reasons. Two concurrent video
overlays would require the device to decode the primary content plus
two ad forms — three concurrent decoders — and many target devices run
only two. Bounding the slot to one active form at a time means the
device never needs more than the primary content plus one ad form,
which is feasible across every device class of §3.4. The base
specification applies the same reasoning to linear ads through its
single-alternative model.

#### 4.6.8 Resolves overlapping windows of the same family as a chain

When two or more opportunity windows of the **same slot family**
overlap in time in the main MPD, the Player selects the **first**
window it encounters and attempts to resolve its resolution document.
The remaining overlapping windows are fallback: the Player resorts to
a subsequent one only when it **cannot access** the first window's
resolution document — the APS does not respond, the request fails at
the transport level, or the response carries a final HTTP status other
than `200`.

A `200` carrying a resolution document with no candidates is
**accessible**: the opportunity resolved, and it resolved to no ads.
The Player serves that answer — it continues with the primary content
— and leaves the remaining windows untouched.

> **Divergence from the base specification, stated inline.** The base
> specification's alternative-MPD execution model (§5.16.2.2)
> already provides first-window-wins with a fallback chain: events are
> queued by presentation time, the topmost executes, Listen Mode
> suspends main-timeline event processing while an alternative plays,
> and a failed execution falls through to the next event in queue
> order. This specification inherits that shape and **narrows one
> condition**. The base model falls through on two triggers — a
> resolution error **and** a zero-duration alternative presentation.
> This specification falls through on the first only, because an
> opportunity that resolved to no ads is an answer, and treating it as
> a failure would make an unfilled opportunity indistinguishable from
> a broken one, which is exactly the distinction §5.2.3 exists to
> create. For the linear family, where the two rules meet, a Player
> implementing this specification applies the rule stated here.

This rule selects *which window is served*. The sequence of forms
inside the served window's resolution document is governed
independently by §4.6.7.

#### 4.6.9 Composes the pause-ad lifecycle

A pause-ad form is admissible only while the primary content is
paused, inside a Publisher-declared pause-trigger window. A conformant
Player:

- Presents the pause-ad form on a pause transition that falls inside
  the window, either **fullscreen** or as a **partial overlay**
  composited over the paused primary frame, according to the option it
  selected. When the pause-ad is fullscreen, the Player MAY release
  the resources held by the primary content and by any pre-existing
  overlay in order to present a fullscreen video, image or web page.
  When it is partial, the paused primary frame stays visible
  underneath it.
- Removes the rendered pause-ad from the screen within one rendering
  frame of the pause-to-play transition, and ceases firing that
  pause-ad's beacons from that transition onward. Beacons scheduled at
  relative times after the transition fall outside the pause-ad's
  active window.
- While the viewer is paused inside a pause-ad window and an overlay
  is active, renders the pause-ad and suspends the overlay. On resume,
  dismisses the pause-ad and restores the overlay when the overlay's
  slot window is still open; when the overlay's window expired during
  the pause, the Player keeps the overlay surface clear. This priority
  holds whether the pause-ad is fullscreen or partial, and this
  specification carries no construct that lets the Publisher, the ADS
  or the APS invert it.
- In **live** content, keeps its presentation time frozen inside the
  pause-ad window while the viewer remains paused, even though the
  live edge keeps advancing in wall-clock time: the window is anchored
  to the Player's frozen presentation time, so the pause-ad stays
  admissible. A decision to resume at the live edge is a Player action
  occurring **after** the resume from pause, outside the pause-ad
  window.

  The freeze holds within the bound the base specification sets. When
  the pause lasts long enough that the resumption time falls before
  the start of the time-shift buffer, the base specification requires
  the playhead to be trimmed to the oldest available segment; a seek
  back to live is trimmed to the live edge. At that boundary the
  Player dismisses the pause-ad and ceases its remaining beacons,
  exactly as it does on a resume. `MPD@timeShiftBufferDepth` is
  therefore the effective ceiling on the freeze, and a Publisher that
  wants a longer pause-ad window on live content sets the buffer
  accordingly.

#### 4.6.10 Executes the tracking schedule

Executes the tracking schedule it reads from the resolution document,
firing each beacon at its specified time relative to the ad's
presentation, and preserving the schedule's authorship upstream. The
Player fires the beacons the document carries; it does not decide
which beacons exist or at what fractions of the presentation they sit.

The Player stops firing an ad's remaining beacons at a trim boundary
(§4.6.4) and at a pause-ad dismissal (§4.6.9).

A beacon that fails — transport error, timeout, non-2xx response —
leaves the ad and the primary content unaffected; a beacon failure is
non-fatal and never reaches the viewer.

#### 4.6.11 Fires the click on activation

Reads the ClickThrough URL and its associated click-tracking URLs from
the carrier of §5.6, and on viewer activation opens the ClickThrough
destination and fires each associated click-tracking URL once.

The click carries no presentation time: it fires when the viewer acts
and never on the timeline. This is what separates it from the beacons
of §4.6.10, which the Player schedules by presentation time through
the callback scheme.

#### 4.6.12 Renders at the primary content's speed

Renders every ad form, linear or non-linear, at the same playback
speed as the primary content at the moment the ad is presented, rather
than forcing the ad to 1× while the primary content runs at another
speed.

A presentation window — presentation time plus duration — does not
define the wall-clock time the ad stays on screen. The Player computes
the effective on-screen length as `duration / playback_speed`: a
10-second ad presented while the primary content runs at 2× occupies
5 seconds of wall clock. `duration` remains the single canonical value
expressed on the presentation timeline and the wall-clock length is
derived from it, never duplicated. Cap enforcement (§4.6.4) and beacon
scheduling (§4.6.10) operate on the presentation-timeline `duration`;
on-screen behaviour follows the derived value.

#### 4.6.13 Declares what it chooses to declare

MAY attach any subset of the reserved capability parameters of §5.8 to
its resolution request — all of them, some of them, or none. When the
Player has no value for a reserved parameter, or does not disclose its
value, it omits that parameter entirely rather than sending it with an
empty or placeholder value. A parameter the Player adds that is not
one of the reserved names carries a vendor-specific prefix, so that
reserved names added in a later edition remain free (§5.8.3).

### 4.7 Extension points and backward compatibility

This specification introduces every new construct through one of the
base specification's own extension points, so the ignore-if-unknown
behaviour a legacy Player exhibits is inherited rather than asserted.

<!-- refine: v7-detail-review.md#flag-11 -->
<!-- refine: v7.1-spec-validation.md#T2 -->
<!-- refine: v7.1-detail-review.md#flag-2 -->
A label of the form **DR-N** in this chapter names the extension rule
of the base specification the construct relies on, so that the audit
below is checkable rule by rule: **DR-1** the Single-Period Static
binding of any document reached through `<ImportedMPD>` (§5.3.2.6,
§8.15, §7.3); **DR-2** foreign-namespace open content (§5.2.1 of the
base specification); **DR-3** the whole-subtree discard of an
unimplemented foreign element (§5.2.1 NOTE 2 of the base
specification); **DR-4** the Annex F path to a non-ISO-BMFF delivery
format (Annex F.2, §8.1); **DR-5** the closed `<AdaptationSet>` axis
on the List MPD path (§8.14, §8.12, §5.3.7.2); **DR-6** the three
carriers admissible for a non-AV asset — **(a)** foreign-namespace
open content, **(b)** an application-level Event Stream (§5.10),
**(c)** a vendor descriptor (§5.8.4.8, §5.8.4.9); **DR-7** the
at-least-one-`<AdaptationSet>`-per-Period rule (§5.3.2.2, Table 4).
Every clause or annex cited in a DR-N label is a clause or annex of
the base specification.

#### 4.7.1 Admissible extension points

| Extension point | Base clause | Used by |
|---|---|---|
| Foreign-namespace open content | §5.2.1 (DR-2, discard per DR-3) | Every XML element and attribute in `urn:svta:dash:sgai:2026` (§5.1.3, §5.1.4, §5.2.2, §5.3, §5.6, §5.7) — carrier class DR-6(a) |
| Application-level Event Streams | §5.10 (DR-6(b)) | The overlay and pause-trigger opportunity declarations, and the tracking carrier (§5.1, §5.5) |
| Vendor descriptor schemes | §5.8.4.8, §5.8.4.9 (DR-6(c)) | Admissible as an alternative carrier; not used by this edition, for the reason recorded in §5.3.2. The MPEG-defined `urn:mpeg:dash:urlparam:2025` descriptor of §5.8.1 is not a vendor scheme and is audited on its own row in §4.7.3 |

A DASH client that does not implement a foreign namespace removes the
**entire** XML node including its subtree. That whole-subtree discard
is the authoring lever this specification uses: a baseline element
placed as a **sibling** of an SGAI element stays visible to a legacy
Player, while a baseline element **nested inside** an SGAI element is
opaque to it. Each construct in §5 states which side of that line it
sits on.

<!-- refine: v7-detail-review.md#flag-4 -->
<!-- refine: v7-detail-review.md#flag-11 -->
An Annex F construction of the base specification (DR-4) — a new
delivery format with a new Interoperability Point URI in
`MPD@profiles` — is admissible only when
a construct genuinely requires DASH segment-delivery semantics for a
non-ISO-BMFF format. This edition introduces none, because every
non-AV creative it carries is a flat HTTP URL to a renderable asset,
for which the cost of a new Interoperability Point is not justified.

#### 4.7.2 The closed media axis

The `<AdaptationSet>` / `<Representation>` axis is closed to non-MP4
media types along the whole resolution path, for two independent
reasons that this specification inherits rather than works around:

- A document reached through `<ImportedMPD>` is bound to the
  Single-Period Static profile, which inherits §7.3 of the base
  specification and constrains every Representation's `@mimeType` to
  the RFC 4337 registry — `video/mp4`, `audio/mp4`, `application/mp4`.
  A vendor profile URI may be appended, but a profile adds constraints
  and never relaxes them.
- An inline `<AdaptationSet>` under a List-MPD-level `<Period>`
  inherits the List MPD profile, itself an extension of the ISO-BMFF
  CMAF profile, and therefore the same constraint; and a
  per-AdaptationSet `@profiles` value is a subset of the MPD-level
  one, so no single AdaptationSet can be promoted out of it.

Beyond the profile chain, the base specification does not define the
carriage of a still image or an HTML document as a Representation at
all: it is designed for segmented, timed media. Image Adaptation Sets
exist in the wider ecosystem, but they originate in the DASH-IF
Interoperability Points and in ISO/IEC 23009-15, not in the document
this specification extends.

<!-- refine: v7-detail-review.md#flag-11 -->
A further rule narrows where a carrier may sit even after its type is
chosen (DR-7): at least one `<AdaptationSet>` is present in each
`<Period>` unless the Period's `@duration` is zero. An "events-only
Period" of non-zero duration is therefore not a legal carrier.

The consequence for this specification: image and HTML asset URLs
travel on the foreign-namespace carrier of §5.3.2, and never on an
`@mimeType` reached through a path bound by RFC 4337. Wrapping a
non-MP4 payload in an `application/mp4` Representation solely to
satisfy the registry is not an admissible workaround: the wrapper adds
no segment-delivery semantics for the underlying format.

#### 4.7.3 Per-construct backward-compatibility audit

Every construct this edition introduces is audited below against the
same checklist: where it sits in the document tree, which extension
rule governs the ignore-if-unknown behaviour, what a legacy Player
does when it meets the construct, whether removing the construct
leaves a document that still parses and plays, and which carrier class
it uses.

<!-- refine: v7.1-spec-validation.md#T2 -->
| Construct | Placement | Extension rule | Legacy Player | Sibling check | Carrier class |
|---|---|---|---|---|---|
| `urn:svta:dash:event:sgai-overlay:2026` EventStream | `<Period>` child in the main MPD | §5.10 of the base specification, per-scheme skip | Skips the EventStream and every Event it carries; primary content continues | Removing it leaves a valid MPD | Event Stream (§5.10) |
| `urn:svta:dash:event:sgai-pause-trigger:2026` EventStream | `<Period>` child in the main MPD | §5.10 of the base specification, per-scheme skip | Skips it; a viewer pause produces no ad and no side effect | Removing it leaves a valid MPD | Event Stream (§5.10) |
| `<svta:OverlayPresentation>` | `<Event>` child | §5.2.1 of the base specification, foreign namespace | Discarded with its whole subtree, together with the skipped Event | The Event carries no baseline child that a legacy Player needs | Foreign-namespace open content |
| `<svta:PauseAdPresentation>` | `<Event>` child | §5.2.1 of the base specification, foreign namespace | Discarded with its whole subtree | Same | Foreign-namespace open content |
| `<svta:OverlayList>` | `<Period>` child in the resolution document | §5.2.1 of the base specification, foreign namespace | Never reached: the slot that resolves to this document is itself skipped at the main-MPD level | The enclosing Period is valid without it | Foreign-namespace open content |
| `<svta:Candidate>` | `<svta:OverlayList>` child | §5.2.1 of the base specification, foreign namespace | Discarded with the parent subtree | n/a — never reached | Foreign-namespace open content |
| `<svta:RenderableAsset>` | `<svta:Candidate>` child | §5.2.1 of the base specification, foreign namespace | Discarded with the parent subtree | n/a — never reached | Foreign-namespace open content |
| `<svta:BackgroundElement>` | `<svta:RenderableAsset>` child | §5.2.1 of the base specification, foreign namespace | Discarded with the parent subtree | n/a — never reached | Foreign-namespace open content |
| `<svta:Click>` | `<svta:Candidate>` child | §5.2.1 of the base specification, foreign namespace (DR-2, DR-3) | Discarded with the parent subtree; the click is inert on a legacy Player | n/a — never reached | Foreign-namespace open content — DR-6(a) |
| `<svta:Click>` | `<Period>` child in a `ListMPD` | §5.2.1 of the base specification, foreign namespace (DR-2, DR-3) | Discarded with its subtree; the click is inert | The Period is valid without it | Foreign-namespace open content — DR-6(a) | <!-- refine: v7-spec-validation.md#T4 -->
| `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>`, `<svta:UniversalAdId>` | `<svta:Candidate>` child | §5.2.1 of the base specification, foreign namespace (DR-2, DR-3) | Discarded with the parent subtree; nothing in the ad presentation depends on them | n/a — never reached | Foreign-namespace open content — DR-6(a) |
| Reserved capability parameters | Query string on the resolution request | Not an MPD construct | An APS that does not implement them answers without them | n/a | HTTP query parameter (§5.8) — outside the DR-6 enumeration |
| `<EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025">`, the Publisher's query-template descriptor (§5.8.1) | `<MPD>` child, after the last `<Period>`; the `<RequestParam>` sits inside the slot's `<EventStream>` | §5.8.4.8 descriptor semantics | **Not skip-and-continue.** A Player predating the base specification's 6th edition does not recognise the scheme; per §5.8.4.8 NOTE 1 it ignores the parent element, and per NOTE 2, an MPD-level descriptor it cannot process leads it to terminate the presentation | Removing it leaves a valid MPD; the resolution request then carries no author-declared parameters | Baseline descriptor used for its own purpose, not an SGAI carrier | <!-- refine: v7-dash-conformance-audit.md#M6 -->

<!-- refine: v7-dash-conformance-audit.md#M6 -->
Every row of the table but the last shares one legacy-Player
walk-through, and it is stated once here. A legacy Player parsing a
main MPD authored per this specification meets the SGAI `<EventStream>`
first. It does not implement the scheme URI, so it skips the
EventStream and every `<Event>` inside it, and the foreign-namespace
child element inside each Event is discarded with it. The remaining
document is exactly the baseline MPD — the primary content's
`<Period>`, its `<AdaptationSet>`s, and whatever standard linear break
the Publisher authored as the VOD fallback — which parses and plays.
Nothing the legacy Player needs was nested inside an SGAI element:
every baseline construct is a sibling of the SGAI constructs, never a
child. Because the legacy Player never recognises the opportunity, it
never issues the resolution request, so it never reaches a resolution
document either. It logs no error above the informational level,
renders no artefact, and fires no beacon for the skipped opportunity.

<!-- refine: v7-dash-conformance-audit.md#M6 -->
The last row is the exception, and it bounds the legacy-fallback
guarantee of §4.3.7: that guarantee holds for a Player implementing
the base specification's 6th edition, which recognises
`urn:mpeg:dash:urlparam:2025`. A Publisher who needs the guarantee to
hold on a Player predating that edition authors no `<RequestParam>`
query template.

## 5. Syntax

This chapter defines the constructs an implementation authors and
reads. Every attribute block is presented as a table; every new
construct states inline why an existing base specification construct
was not reused, and every deliberate decision not to reuse a construct
a reader might expect is recorded with it.

### 5.1 Ad opportunity declarations in the main MPD

A Publisher declares each ad opportunity as an `<Event>` inside an
`<EventStream>` in the main MPD. The `<EventStream>@schemeIdUri`
identifies the slot family; the `<Event>`'s scheme-specific child
element carries the slot constraints.

| Slot family | `<EventStream>@schemeIdUri` | Child element of `<Event>` | Resolution document |
|---|---|---|---|
| Linear, insert | `urn:mpeg:dash:event:alternativeMPD:insert:2025` | `<InsertPresentation>` | `ListMPD` (§5.2.1) |
| Linear, replace | `urn:mpeg:dash:event:alternativeMPD:replace:2025` | `<ReplacePresentation>` | `ListMPD` (§5.2.1) |
| Overlay | `urn:svta:dash:event:sgai-overlay:2026` | `<svta:OverlayPresentation>` | Overlay Resolution Document (§5.2.2) |
| Pause ad | `urn:svta:dash:event:sgai-pause-trigger:2026` | `<svta:PauseAdPresentation>` | Overlay Resolution Document (§5.2.2) |

The `<Event>` carrier itself uses the baseline attributes of §5.10 of
the base specification — `@id`, `@presentationTime`, `@duration` — with
the time base given by `@timescale` on the parent `<EventStream>`. The
scheme-specific child element is the SGAI attribute carrier.

**Why the Event Stream, and not a new container.** `<EventStream>` plus
`<Event>` is the base specification's authoring vehicle for
timeline-anchored signalling, and its per-scheme skip rule is already
the ignore-if-unknown behaviour a legacy Player needs. Introducing a
container of our own would have re-derived both and would have had to
argue its own legacy semantics from scratch.

#### 5.1.1 `<InsertPresentation>` (linear, inherited)

Reused verbatim from §5.16.3 of the base specification. The Publisher
declares an `<Event>` whose `presentationTime` marks a point on the
primary timeline at which the alternative presentation is inserted
**without consuming any of the primary timeline**. When the
alternative presentation ends, primary content resumes from where it
was paused.

The element carries the attributes of `AlternativeMPDEventType`:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | yes | `xs:anyURI` | — | URL the Player resolves at or after the Earliest Resolution Time. Resolves to the APS endpoint. |
| `@maxDuration` | no in the base schema; **yes under this specification** | `xs:unsignedLong` | `2251799813685247` (unbounded) | The slot cap. Expressed in the parent `<EventStream>@timescale` units. An alternative presentation that runs past it is terminated at the cap. A Publisher authoring under this specification declares a real value rather than relying on the unbounded default (§4.3.2). |
| `@earliestResolutionTimeOffset` | no | `xs:unsignedLong` | 60 s when absent | Offset subtracted from the event's `presentationTime` to obtain the Earliest Resolution Time, in `@timescale` units. |
| `@executeOnce` | no | `xs:boolean` | `false` | When `true`, the event executes at most once in the session. |
| `@noJump` | no | `xs:integer` | `0` | Baseline seek-interaction control for the slot. |
| `@skipAfter` | no | `xs:duration` | `PT0S` | Baseline skip-offset control for the slot. |
| `@serviceDescriptionId` | no | `xs:unsignedInt` | — | Identifies the service description that applies to the alternative presentation. |

Children: `<SupplementalProperty>` (zero or more) and
foreign-namespace open content, both inherited from
`AlternativeMPDEventType`.

<!-- refine: v7-spec-validation.md#T2 -->
<!-- refine: v7-dash-conformance-audit.md#M8 -->
> The base specification declares `@earliestResolutionTimeOffset` in
> the XML Schema of §5.16.6 with no schema default; the 60-second
> default is stated in the prose of §5.16.5.2, Table 63 — "The
> default is 60 seconds in units of timescale." An implementation
> that needs the value to be unambiguous declares it explicitly on
> the slot, which §4.3.5 asks for in any case.

Constraint inherited from the base specification: this event does not
appear when `MPD@type` is `dynamic`. It addresses an operation in
which the playhead can be stopped for an indefinite period, which is
an on-demand or pre-recorded operation. Live content uses
`<ReplacePresentation>` (§5.1.2).

Legacy-Player behaviour: provided by the baseline per-scheme skip rule
of §5.10 (§4.7.3).

#### 5.1.2 `<ReplacePresentation>` (linear, inherited)

Reused verbatim from §5.16.4 of the base specification. The Publisher
declares an `<Event>` whose `presentationTime` and `duration` mark a
span of the primary timeline that the alternative presentation
**replaces**. Primary media time keeps advancing while the ad plays,
and on completion the Player resumes at the position determined by
`@returnOffset`.

`AlternativeMPDReplaceEventType` extends `AlternativeMPDEventType`, so
every attribute of §5.1.1 applies, plus:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@returnOffset` | no | `xs:unsignedLong` | — | Offset that determines the playhead position at which primary content resumes after the alternative presentation. |
| `@clip` | no | `xs:boolean` | `true` | When `true`, an alternative presentation whose execution starts late is trimmed so it does not run past `@maxDuration`. The attribute carries no duration of its own. |
| `@startWithOffset` | no | `xs:boolean` | `false` | When `true`, a delayed alternative presentation skips into its own timeline by the elapsed delay, staying aligned with the wall clock. When `false`, it starts from its first frame. |

<!-- refine: v7.1-dash-conformance-audit.md#M6 -->
All conditional restrictions the base specification places on these
attributes in §5.16.4 and §5.16.5.2 apply unchanged; the table above
restates names, types and defaults only.

`@returnOffset`, `@clip` and `@startWithOffset` are exclusive to
`<ReplacePresentation>`; `<InsertPresentation>` carries neither of the
three.

Legacy-Player behaviour: as in §5.1.1.

#### 5.1.3 `<svta:OverlayPresentation>` (non-linear, new)

Declares a non-linear overlay opportunity. The opportunity window is
the parent `<Event>`'s `presentationTime` and `duration`. The Player
resolves the slot's `@uri` at or after the Earliest Resolution Time,
validates the candidates against the constraints below, and composites
the chosen form on or alongside the primary content, which keeps
playing.

**Why a new construct.** The base specification's ad machinery —
alternative-MPD events and the List MPD profile — is substitutive by
definition: an alternative presentation completely replaces or precedes
the content on the main timeline. The edition provides no metadata
element, spatial-layout attribute or rendering schema for compositing an
ad over active video, and nothing elsewhere fills the role. The Spatial
Relationship Description of Annex H of the base specification positions
encoded video tracks inside a shared coordinate system for tiling and
region-of-interest use cases; it is neither a compositor nor an overlay
layout facility, and reusing it would both misuse the construct and
build the parallel layout system this specification declines to build.
The `urn:mpeg:dash:nonlinearplayback:2020` scheme of Annex L of the
base specification, despite its name, models interactive storylines as
a graph of Periods with viewer decision points; it defines no overlay
rendering and no ad semantics. A new
opportunity declaration is therefore unavoidable, and it is minimised:
it is an `<Event>` child element carrying attributes, nothing more.

##### 5.1.3.1 Attributes

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | yes | `xs:anyURI` | — | URL the Player resolves at or after the Earliest Resolution Time. Resolves to the APS endpoint; the response conforms to §5.2.2. |
| `@maxDuration` | yes | `xs:unsignedLong` | — | The slot cap, in the parent `<EventStream>@timescale` units, enforced against the cumulative rendered length of the forms presented in this slot. Name, units and termination semantics are those of `@maxDuration` in §5.16.5.2 of the base specification. |
| `@earliestResolutionTimeOffset` | no | `xs:unsignedLong` | 60 s when absent | Offset subtracted from the event's `presentationTime` to obtain the Earliest Resolution Time, in `@timescale` units. Same name, type and semantics as on the linear events. |
| `@allowedLayouts` | yes | whitespace-separated list of tokens | — | The layout tokens admissible on this slot, each drawn from §3.2. The Player matches a candidate option's `@layout` against this list by exact token. |
| `@executeOnce` | no | `xs:boolean` | `false` | As in §5.1.1. |

<!-- refine: v7-dash-conformance-audit.md#NC4 -->
**Encoding note.** `@allowedLayouts` is a single attribute carrying a
whitespace-separated token list rather than a nested element with one
child per token, matching the encoding the base specification already
uses for `@dependencyId` and the other attributes it types as
`StringVectorType`. The element form is warranted only when each item
carries its own attributes or children, which a layout token does
not.

**On concurrency.** This specification declares no
maximum-concurrency attribute on the slot. At most one non-linear form
is active at any instant (§4.6.7), so an attribute whose only
admissible value is `1` would restate a rule the specification already
fixes, and a value that disagreed with it would be unenforceable.

##### 5.1.3.2 Children

None. Every slot constraint is carried as an attribute.

##### 5.1.3.3 Legacy-Player behaviour

A Player that does not implement
`urn:svta:dash:event:sgai-overlay:2026` applies the baseline
per-scheme skip rule: the parent `<EventStream>` is skipped together
with every `<Event>` it carries, and the foreign-namespace
`<svta:OverlayPresentation>` element is discarded with its whole
subtree. Primary content continues uninterrupted. Removing the whole
`<EventStream>` from the document leaves a valid MPD that parses and
plays, and no baseline element the legacy Player needs is nested
inside the SGAI element.

#### 5.1.4 `<svta:PauseAdPresentation>` (non-linear, new)

Declares a **pause-trigger window**: an interval on the primary
timeline during which a viewer pause permits a pause ad. Outside the
window, a pause permits none. The window is the parent `<Event>`'s
`presentationTime` and `duration`.

**Why a new construct, and why this shape.** Every DASH event is
scheduled against the media presentation timeline and dispatched when
the playhead reaches it; a pause halts the playhead, and with it
playhead-triggered event processing. The edition defines no MPD
element and no event construct triggered by a pause — the pause
appears in the edition only as a reporting record in the playout
metrics. The shape follows from that asymmetry: what is declared on
the timeline is the **window of validity**, which a timeline-scheduled
event expresses natively, while the **trigger** is Player-side and
fires on the pause transition inside that window. Annex L of the base
specification already splits a construct the same way, anchoring an
event stream on the timeline while resolving the viewer's interaction
off it.

##### 5.1.4.1 Attributes

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | yes | `xs:anyURI` | — | URL the Player resolves to obtain the pause-ad resolution document (§5.2.2). |
| `@maxDuration` | yes | `xs:unsignedLong` | — | Maximum display duration of the pause ad before automatic dismissal, in the parent `<EventStream>@timescale` units. Name, units and termination semantics are those of `@maxDuration` in §5.16.5.2 of the base specification. | <!-- refine: v7.1-detail-review.md#flag-4 -->
| `@earliestResolutionTimeOffset` | no | `xs:unsignedLong` | 60 s when absent | Offset subtracted from the event's `presentationTime` to obtain the Earliest Resolution Time. The Player MAY resolve speculatively at that time or lazily at the moment of pause (§8.5). |
| `@allowedLayouts` | yes | whitespace-separated list of tokens | — | The layout tokens admissible on this window. The token a pause-ad form carries is `pause-ad`; a Publisher declaring a pause-trigger window lists it. |
| `@executeOnce` | no | `xs:boolean` | `false` | As in §5.1.1. |

##### 5.1.4.2 Legacy-Player behaviour

A Player that does not implement
`urn:svta:dash:event:sgai-pause-trigger:2026` skips the
`<EventStream>` and its events, and a viewer pause produces no ad and
no side effect. The window is invisible to it.

#### 5.1.5 Hybrid slots — a linear slot with a concurrent overlay

A hybrid break is authored as **two events at the same
`presentationTime`**: one carrying `<InsertPresentation>` or
`<ReplacePresentation>` for the take-over portion, and one carrying
`<svta:OverlayPresentation>` for the overlay composited on top of it.

The two events are independent at authoring time and at runtime. The
Player resolves the two `@uri` values separately, validates and
selects from each resolution document independently, and composes the
chosen linear ad with the chosen overlay during the same break. This
specification defines no construct that links the two portions — a
Publisher that wants the overlay restricted during a take-over
expresses it through that event's own `@allowedLayouts`, and a
Publisher that wants no overlay during a take-over declares no overlay
event at that position.

#### 5.1.6 Overlapping windows of the same family

Two or more events of the same slot family whose windows overlap in
time form a **fallback chain**: the first is the window to serve, the
rest are backups reached only when the first window's resolution
document cannot be accessed. The Player-side rule is §4.6.8; no
attribute declares the chain, because the overlap itself is the
declaration.

**Considered and not reused.** `BaseURL` alternatives with
`@serviceLocation` (§5.6 of the base specification) offer alternative
locations for the **same** resource and are the right tool for
origin-level robustness on a sub-MPD or segment fetch, not for chaining
two different opportunities. The MPD fallback scheme
`urn:mpeg:dash:fallback:2016` (§5.11.3 of the base specification) chains
whole presentations on an unrecoverable playout error; its ordering rule
— the content author expresses preference by order, the first having the
highest preference — is the same rule this specification applies, and it
is cited here as the edition's own precedent for
document-order-as-preference, but its granularity is a whole
presentation rather than an opportunity window.

### 5.2 Resolution documents

#### 5.2.1 Linear `ListMPD`

Reused from §8.14 of the base specification. The APS answers a linear
slot's resolution request with an MPD whose `@type` is `list` and
whose `@profiles` includes `urn:mpeg:dash:profile:list:2024`. Each
`<Period>` is one ad in the break, played back-to-back in declared
order: a List MPD is a playlist of ads the ADS already chose and
ordered, not a candidate set the Player selects from.

Two profile rules bound the document and are inherited unchanged:
a List MPD carries no Alternative MPD events, and no XLink attributes
at any level. Remote resolution inside a List MPD therefore goes
through `<ImportedMPD>` and nowhere else. The first rule has a
consequence worth stating: a resolution document cannot declare a
nested ad opportunity inside itself, so every overlay and pause-ad
window is signalled from the main MPD.

##### 5.2.1.1 Period attributes

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@id` | yes | `xs:string` | — | Period identifier, unique within the document. |
| `@duration` | yes | `xs:duration` | — | Declared duration of this ad, as an ISO 8601 duration. The Player uses it for drop-before-play cap evaluation (§4.6.4) without first fetching the sub-MPD. |

##### 5.2.1.2 Period children

A Period carries one `<ImportedMPD>` pointing at the ad's sub-MPD
(§5.4). The base specification also admits inline `<AdaptationSet>` /
`<Representation>` under a List-MPD-level Period; that shape is
permitted and inherits the RFC 4337 media-type constraint of §4.7.2.
The `<ImportedMPD>` shape is the one this specification uses in its
examples, because it keeps each creative's metadata sharded per ad.

##### 5.2.1.3 `<ImportedMPD>`

Reused verbatim from §5.3.2.6 of the base specification. The imported
MPD's URL is the element's **text content**, not an attribute; the
element's type extends `xs:anyURI` through simple content.

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@earliestResolutionTimeOffset` | no | `xs:double` | `60.0` | Seconds before this Period's start at which the Player MAY pre-fetch the sub-MPD, smoothing CDN load. |

> **Unit note.** `@earliestResolutionTimeOffset` appears in two
> contexts with different unit bases, both inherited from the base
> specification. On a slot event (§5.1.1 to §5.1.4) it is
> `xs:unsignedLong` in the parent `<EventStream>@timescale` units. On
> `<ImportedMPD>` it is `xs:double` in **seconds**. A reader
> determines the base from the parent element; authoring tools SHOULD
> surface the parent element alongside the value.

A Period carrying an `<ImportedMPD>` is a Linked Period, and the
imported document is restricted to the Single-Period Static profile
(§5.4).

#### 5.2.2 Overlay Resolution Document (non-linear, new)

The APS answers an overlay or pause-ad slot's resolution request with
an Overlay Resolution Document: an MPD whose `@profiles` includes
`urn:svta:dash:profile:sgai-overlay-list:2026`, carrying the
candidates in a foreign-namespace `<svta:OverlayList>` element.

**Why this shape.** The List MPD structure was the starting point and
most of it is reused: the document is an MPD, the candidate list keeps
declared order as the preference order, and video creatives are still
reached through `<ImportedMPD>` into an SPS sub-MPD. What the List MPD
cannot express is the construct the non-linear case needs — a single
candidate offering an ordered list of alternative presentation options
— because its Periods are a sequence to play, not alternatives to
choose among (§5.3.5). The candidate list is therefore carried in the
extension namespace, inside a document that is otherwise a
conformant MPD.

##### 5.2.2.1 Document shape

The document is an `MPD` carrying a single `<Period>` whose
`@duration` is `PT0S` and whose only child is the foreign-namespace
`<svta:OverlayList>`.

The zero duration is load-bearing rather than cosmetic. The base
specification requires at least one `<AdaptationSet>` in each
`<Period>` **unless** the Period's `@duration` is zero, and an
Overlay Resolution Document carries no AdaptationSet at all: the
candidates' media is reached through their own presentation options,
not through the enclosing Period. Declaring `PT0S` is what makes the
document conformant, and it also expresses the truth — the enclosing
Period presents nothing itself; it is the anchor the candidate list
hangs from. The candidates carry their own durations (§5.2.2.4).

`<Period>` admits foreign-namespace children through the open content
of §5.2.1 of the base specification, so the `<svta:OverlayList>`
placement is conformant, and a DASH-aware validator that scans
`<Period>` children for foreign-namespace elements finds it under a
canonical anchor.

<!-- refine: v7.1-dash-conformance-audit.md#M5 -->
A resolution document is a conforming **MPD** used as a carrier, and
not itself a Media Presentation: it describes no media of its own, and
each candidate's media is reached through that candidate's own
presentation options. The base specification's Media-Presentation
conformance rule — at least one Representation in each Period of the
profile-specific MPD (§8.1 of the base specification) — is therefore
not the ladder this document is measured against.

Skeleton:

<!-- refine: v7-detail-review.md#flag-1 -->
<!-- refine: v7-dash-conformance-audit.md#NC1 -->
```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-15T16:00:00Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-1" duration="PT10S">
        <svta:RenderableAsset form="video"
                              layout="squeezeback-double-box-with-background">
          <svta:BackgroundElement assetUrl="https://cdn.example.com/bg-1.png"/>
          <ImportedMPD>https://cdn.example.com/ad-1-video.mpd</ImportedMPD>
        </svta:RenderableAsset>
        <svta:RenderableAsset form="image"
                              layout="squeezeback-l-shape"
                              assetUrl="https://cdn.example.com/ad-1-lshape.png"/>
        <svta:RenderableAsset form="image"
                              layout="overlay-corner"
                              assetUrl="https://cdn.example.com/ad-1-corner.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0" id="1">https://tracker.example.com/impression?ad=1</Event>
          <Event presentationTime="5000" id="2">https://tracker.example.com/midpoint?ad=1</Event>
          <Event presentationTime="10000" id="3">https://tracker.example.com/complete?ad=1</Event>
        </EventStream>
        <svta:Click clickThroughUrl="https://advertiser.example.com/landing">
          <svta:ClickTracking>https://tracker.example.com/click?ad=1</svta:ClickTracking>
        </svta:Click>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

##### 5.2.2.2 `MPD` attributes on an Overlay Resolution Document

<!-- refine: v7.1-spec-validation.md#T5 -->
| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@profiles` | yes | comma-separated list of `xs:anyURI` | — | Includes `urn:svta:dash:profile:sgai-overlay-list:2026`. §8.1 of the base specification defines the value as a comma-separated list and forbids a comma inside a profile identifier. | <!-- refine: v7-dash-conformance-audit.md#NC4 -->
| `@minBufferTime` | yes | `xs:duration` | — | Baseline MPD attribute. `PT0S` on this document, which buffers nothing itself. |
| `@mediaPresentationDuration` | yes | `xs:duration` | — | `PT0S`, consistent with the single zero-duration Period. The base specification makes this attribute conditional when the last Period declares a `@duration`; this profile declares it unconditionally, which is a constraint added rather than relaxed. |
| `@publishTime` | yes | `xs:dateTime` | — | The instant the APS produced the document. |

<!-- refine: v7-detail-review.md#flag-3 -->
> **On the name.** "Overlay" in *Overlay Resolution Document*, in the
> profile URI `urn:svta:dash:profile:sgai-overlay-list:2026` and in
> `<svta:OverlayList>` names the **non-linear family as a whole** —
> overlay slots and pause-trigger windows alike (§5.1). It is not the
> `overlay` layout token of §3.2, which names one spatial arrangement.
> A pause-ad document is an Overlay Resolution Document and declares
> that profile URI.

##### 5.2.2.3 `<svta:OverlayList>`

| Child | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:Candidate>` | no | 0..n | The ads offered for the slot, in the order the ADS decided. Zero children is the empty resolution of §5.2.3. |

The element carries no attributes.

##### 5.2.2.4 `<svta:Candidate>`

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@id` | yes | `xs:string` | — | Candidate identifier, unique within the document. |
| `@duration` | yes | `xs:duration` | — | The candidate's declared duration on the presentation timeline, as an ISO 8601 duration. The Player uses it for drop-before-play cap evaluation (§4.6.4) and as the basis for the derived wall-clock on-screen length (§4.6.12). |

| Child | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:RenderableAsset>` | yes | 1..n | The candidate's presentation options, as an ordered list. Document order is the preference order (§5.3). |
| `<EventStream>` (callback scheme) | no | 0..1 | The candidate's tracking schedule (§5.5). |
| `<svta:Click>` | no | 0..1 | The candidate's ClickThrough and its click-tracking (§5.6). |
| `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>`, `<svta:UniversalAdId>` | no | 0..1 each | Application-level metadata (§5.7). |

#### 5.2.3 The empty resolution document

An opportunity that resolved and produced **no ads** is expressed as a
resolution document carrying no candidates, served with HTTP `200` and
a body. It is not an error status, and not a response without a body.

The Player's behaviour is unchanged by the distinction: it continues
with the primary content, as it does whenever the candidates are
exhausted. What the distinction buys is elsewhere — an unfilled
opportunity can be reported as unfilled rather than as a failure to
resolve (§4.6.8, §8.1), and the fallback chain has a well-defined
trigger.

**Non-linear.** The document of §5.2.2 with an empty
`<svta:OverlayList>`:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-15T16:00:00Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList/>
  </Period>
</MPD>
```

**Linear.** A `ListMPD` carrying a single `<Period>` whose `@duration`
is `PT0S` and which carries no `<ImportedMPD>`:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT0S"
     publishTime="2026-09-15T16:00:00Z">
  <Period id="no-fill" duration="PT0S"/>
</MPD>
```

Both shapes are chosen against the same schema constraint. `<Period>`
is declared with `maxOccurs="unbounded"` and an omitted `minOccurs`,
which defaults to `1`, so a resolution document carrying zero Periods
does not validate; and at least one `<AdaptationSet>` is required in
each Period unless the Period's `@duration` is zero, which is why the
degenerate Period declares `PT0S`. The answer has the same shape for
a linear slot and a non-linear one: one Period of zero duration,
carrying nothing to present.

<!-- refine: v7.1-dash-conformance-audit.md#M5 -->
As in §5.2.2.1, both shapes are conforming MPDs used as carriers
rather than Media Presentations, so the per-Period Representation rule
of §8.1 of the base specification does not reach them either.

### 5.3 `<svta:RenderableAsset>` — the presentation option

A `<svta:RenderableAsset>` is **one** renderable presentation option
on a candidate: a creative-carrier form paired with a layout. A
candidate carries its options as an ordered list of these elements.

**Why a new construct.** No construct in the base specification lets a
single ad candidate offer an ordered list of alternative presentations
and have the client render the first it can satisfy. Three constructs
express ordered preference and each is scoped elsewhere. `Preselection`
(§5.3.11 of the base specification) combines media content components
across Adaptation Sets into one experience intended for joint decoding
and rendering — NGA track mixing, base plus enhancement layer,
stereoscopic video — so it orders media variants of one presentation
rather than alternative presentations of one ad, and the client is not
required to take the first in document order. `@selectionPriority`
(§5.3.7.2 of the base specification) is a non-binding author hint on
`RepresentationBaseType` where higher integers express higher preference
— the opposite direction from document order, and applied after
capability filtering rather than as the walk itself.
`urn:mpeg:dash:fallback:2016` (§5.11.3 of the base specification) states
this specification's ordering rule almost verbatim, but at the
granularity of whole MPD URLs and triggered by an unrecoverable playout
error rather than by a capability check. Reusing any of the three would
put an ad-level choice on a media-level construct, or invert the
ordering convention. The option element is therefore new, and it is kept
minimal: two attributes and, for a video form, one baseline child.

#### 5.3.1 Attributes

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@form` | yes | enum (`video` \| `image` \| `html`) | — | The creative-carrier form, as defined in §3.1. Value space in §5.3.2. | <!-- refine: v7-detail-review.md#flag-1 -->
| `@layout` | yes | token | — | The layout, drawn from the enumeration of §3.2. The Player matches it against the slot's `@allowedLayouts` by exact token. Value space in §5.3.3. |
| `@assetUrl` | conditional | `xs:anyURI` | — | The creative's URL when `@form` is `image` or `html`. Absent when `@form` is `video`, where the creative is reached through the `<ImportedMPD>` child (§5.3.4). |

This specification declares no priority or ranking attribute on the
option: document order is the preference order (§5.3.5), and a second
declaration of the same fact would be a value that could contradict
the first.

<!-- refine: v7-detail-review.md#flag-1 -->
#### 5.3.2 Enum: `@form`

| Enum value | Description |
|---|---|
| `video` | ISO-BMFF video, reached through the `<ImportedMPD>` child of this element (§5.3.4). Representations inside the sub-MPD carry `video/mp4`, `audio/mp4` or `application/mp4`. |
| `image` | Still image at `@assetUrl`. Concrete media types: `image/jpeg`, `image/png`, `image/webp`. |
| `html` | HTML document at `@assetUrl`. Concrete media type: `text/html`. Inline `<script>` MAY appear and runs under the device's HTML capability contract; the script is not a separate carrier. |

**Why the non-AV asset URL rides on the element and not on a
Representation.** The media axis is closed to non-MP4 media types
along the whole resolution path (§4.7.2), for two independent reasons
— the profile chain that binds every imported document to the
Single-Period Static profile and its RFC 4337 restriction, and the
fact that the base specification does not define the carriage of a
still image or an HTML document as a Representation at all. Of the
three DASH-conformant carriers that remain, this specification uses
**foreign-namespace open content**: `@assetUrl` on the option element.
An Event Stream payload carrier was considered and not used, because
the asset URL is a one-fetch static value with no presentation-time
alignment of its own. A vendor descriptor carrier was considered and
not used, because its placement is constrained to `AdaptationSet`,
`Representation` and `Sub-Representation`, so it inherits the same
media-type restriction unless it is hosted inside a foreign-namespace
parent — at which point it is the carrier already chosen, with an
extra level of indirection.

#### 5.3.3 Enum: `@layout`

The admissible values are exactly the tokens of §3.2. Which of them
are admissible **on a given slot** is the Publisher's declaration:

| Enum value | Description |
|---|---|
| `linear` | The full-screen takeover. Admissible on an overlay slot as the option of last resort, and inside a linear slot's `ListMPD`, where it is the only form. |
| `overlay` | Plain image or HTML overlay with no named placement. Admissible on overlay slots. |
| `overlay-corner` | Corner overlay. Admissible on overlay slots. |
| `overlay-lower-third` | Lower-third overlay. Admissible on overlay slots. |
| `squeezeback-l-shape` | L-shape: one full-frame ad creative with the shrunk primary content on top (§5.3.7.1). Admissible on overlay slots. |
| `squeezeback-double-box` | Two boxes; the uncovered bands render as black (§5.3.7.2). Admissible on overlay slots. |
| `squeezeback-double-box-with-background` | Two boxes plus an advertiser background element filling the uncovered bands (§5.3.7.2). Admissible on overlay slots. |
| `pause-ad` | Pause ad over the paused primary frame, fullscreen or partial. Admissible on pause-trigger windows. |

An option whose `@layout` is absent from the slot's
`@allowedLayouts` fails the Publisher check, and the Player moves to
the next option in document order (§4.6.5).

#### 5.3.4 `<ImportedMPD>` child, for a video form

When `@form` is `video`, the creative is carried through an
`<ImportedMPD>` child, reused verbatim from §5.3.2.6 of the base
specification: the sub-MPD's URL is the element's text content, and
its single attribute is `@earliestResolutionTimeOffset` (`xs:double`,
default `60.0`, in seconds).

The child is a **core-namespace** element inside a
foreign-namespace parent. That placement is permitted — the namespace
boundary is lexical, and §5.3.2.6 does not constrain the parent of
`<ImportedMPD>` — and it is deliberate: nesting the baseline element
inside the SGAI element is what makes it opaque to a legacy Player,
which is the behaviour this construct wants, since a legacy Player
that could see the sub-MPD reference would have no slot to play it in.
A schema for `<svta:RenderableAsset>` admits the core-namespace
`<ImportedMPD>` as a first-class child.

#### 5.3.5 Document order is the preference order

The order of the `<svta:RenderableAsset>` children inside a
`<svta:Candidate>` is the preference order. The Player evaluates the
options in that order and renders the first whose form and layout it
can satisfy (§4.6.5).

Carrying several options is the form this specification asks for: a
candidate with several resolves on devices the ADS and the APS know
nothing about, which is what lets one decision serve a heterogeneous
population. Carrying exactly one is equally admissible, and the
Player-visible interface is the same either way — nothing in the
document distinguishes "the APS narrowed the list" from "this is all
there was".

#### 5.3.6 Legacy-Player behaviour and the required-sibling check

`<svta:RenderableAsset>` appears only inside a `<svta:Candidate>`,
inside a `<svta:OverlayList>`, inside a resolution document that a
legacy Player never requests — because the slot that would have
triggered the request was skipped at the main-MPD level (§5.1.3.3,
§5.1.4.2). Were the document nonetheless parsed by a legacy Player, it
would discard `<svta:OverlayList>` with its whole subtree and be left
with a valid MPD carrying one zero-duration Period.

#### 5.3.7 Layout composition

##### 5.3.7.1 L-shape / squeezeback

The L-shape has **one** ad creative — a single URL carrying an image,
a video or an HTML creative — and that creative is **always** placed
full-frame in the background. The shrunk primary content is
composited **on top of** it, in one region of the screen; the "L" is
the band of the background creative that stays visible around the
shrunk primary content, commonly the side and the bottom.

The layout therefore puts **two** elements on screen: the full-frame
ad creative and the shrunk primary content on top of it. There is no
separate third filler element — the ad creative already covers the
whole frame, so the region around the shrunk primary content *is* the
ad creative. This matches the IAB squeezeback model, in which assets
are provided in an underlay format: a full-frame branded creative with
a cutout for the content.

The L-shape is a presentation option like any other: a candidate lists
it among its ordered options, and the Player renders it when the
device can satisfy it.

##### 5.3.7.2 Side-by-side / double-box and the background element

In a side-by-side / double-box layout the shrunk primary content and
the ad are composed as two on-screen boxes that leave bands
uncovered. A **background element** MAY fill those bands; when none is
present they render as black.

The background element is a still **image** — a branding surface,
never a video and never a web/HTML surface, so it never consumes a
video decoder. It is the **advertiser's** creative, mirroring the IAB
"Double Box Video + Background" model, and it is a composition
attribute of the layout rather than one of the candidate's alternative
presentation options: the Player does not walk it the way it walks the
options, it composites it as part of rendering the layout once that
layout is chosen.

It is carried as a `<svta:BackgroundElement>` child of the
`<svta:RenderableAsset>` whose `@layout` is
`squeezeback-double-box-with-background`:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@assetUrl` | yes | `xs:anyURI` | — | URL of the advertiser's background image. Concrete media types as in §5.3.2 for `image`. |

<!-- refine: v7.1-spec-validation.md#T4 -->
| Child of `<svta:RenderableAsset>` | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:BackgroundElement>` | yes, when `@layout` is `squeezeback-double-box-with-background` | 1..1 | Exactly one background element on that layout, and none (0..0) on every other layout. |

A candidate that offers the double box **without** a background
element uses the `squeezeback-double-box` token and carries no
`<svta:BackgroundElement>`; the uncovered bands then render as black.

##### 5.3.7.3 Decoder-and-surface budget per layout

The number and type of concurrent elements a layout puts on screen
<!-- refine: v7-detail-review.md#flag-5 -->
determine which device classes can composite it. This table is what
the Player evaluates in §4.6.5, and what an APS that received
capability parameters evaluates in §5.8.2.

| Layout | Form of the ad creative | Video decoders | Non-video surfaces | Satisfiable on |
|---|---|---|---|---|
| `overlay`, `overlay-corner`, `overlay-lower-third` | `video` | 2 (primary + ad) | none | D1, D2 |
| `overlay`, `overlay-corner`, `overlay-lower-third` | `image` | 1 (primary) | image surface over video | D1, D3, D4 |
| `overlay`, `overlay-corner`, `overlay-lower-third` | `html` | 1 (primary) | HTML surface over video | D1, D3 |
| `squeezeback-l-shape` | `video` | 2 (full-frame creative + shrunk primary) | none | D1, D2 |
| `squeezeback-l-shape` | `image` | 1 (shrunk primary) | image surface for the full-frame creative | D1, D3, D4 |
| `squeezeback-l-shape` | `html` | 1 (shrunk primary) | HTML surface for the full-frame creative | D1, D3 |
| `squeezeback-double-box` | `video` | 2 (primary + ad) | none | D1, D2 |
| `squeezeback-double-box` | `image` | 1 (primary) | image surface for the ad | D1, D3, D4 |
| `squeezeback-double-box` | `html` | 1 (primary) | HTML surface for the ad | D1, D3 |
| `squeezeback-double-box-with-background` | `video` | 2 (primary + ad) | image surface for the background | D1 |
| `squeezeback-double-box-with-background` | `image` | 1 (primary) | image surface for the ad **and** image surface for the background | D1, D3, D4 |
| `squeezeback-double-box-with-background` | `html` | 1 (primary) | HTML surface for the ad **and** image surface for the background | D1, D3 |
| `pause-ad` | `video` | 1 (the primary content is paused and holds its frame; on a device that cannot re-task the decoder, 2) | none | D1, D2; D3–D4 when the device can re-task the decoder holding the paused frame (§8.4) | <!-- refine: v7.1-spec-validation.md#T1 -->
| `pause-ad` | `image` | 1 (paused primary) | image surface over the paused frame | D1, D3, D4 |
| `pause-ad` | `html` | 1 (paused primary) | HTML surface over the paused frame | D1, D3 |
| `linear` (full-screen takeover) | `video` | 1, reused sequentially across ad and primary content | none | D1, D2, D3, D4, D5 |

Two readings of this table are worth making explicit, because they are
where the device-class outcome stops being obvious:

- **D2 owns two decoders and still declines the three-element
  side-by-side.** The blocker is the background element, an image
  surface D2 cannot composite — the rule is element **type**, not
  element **count**.
- **The full-screen takeover is the only row satisfiable on every
  class**, because it needs no concurrent composition at all: one
  decoder, reused sequentially. That is what makes it the useful
  last option on a candidate's ordered list.

A pause ad is the one case in which a single-decoder device may be
able to present a **video** form: the primary content is paused, so
the decoder that holds the paused frame may be re-taskable. Whether a
given device can do so, and what "paused" then means for the primary
content, is a device property this specification does not decide; the
conservative Player behaviour is described in §8.4.

### 5.4 Sub-MPD (Single-Period Static profile)

Every `<ImportedMPD>` — from a `ListMPD` Period (§5.2.1.3) or from a
video presentation option (§5.3.4) — points at a sub-MPD bound to the
Single-Period Static profile of §8.15 of the base specification. That
binding is structural rather than a choice: the base specification
restricts any document reached through `<ImportedMPD>` to that
profile, and the profile inherits §7.3 of the base specification,
which constrains every Representation's `@mimeType` to `video/mp4`,
`audio/mp4` and `application/mp4`.

A sub-MPD authored under this specification:

| Property | Value |
|---|---|
| `@profiles` | includes `urn:mpeg:dash:profile:sps:2024` |
| `@type` | `static` |
| `<Period>` | exactly one, with `@duration` present |
| `<AdaptationSet>` / `<Representation>` | the ad's media, with `@mimeType` from the RFC 4337 registry |
| `<EventStream>` (callback scheme) | optional; carries the ad's tracking schedule (§5.5.2) |

`@codecs` values in every MPD this specification defines — main MPD,
`ListMPD`, Overlay Resolution Document, sub-MPD — follow RFC 6381,
which makes the codec identifier case-sensitive and recommends
lowercase hexadecimal: `avc1.4d401f`. The examples in the annexes
follow that convention throughout.

#### 5.4.1 Reconciling the declared durations

A candidate's `@duration` in the parent resolution document and the
sub-MPD's `Period@duration` describe the same ad. The parent's value
is the one the Player reads for drop-before-play cap evaluation
(§4.6.4), because it is available without a second fetch. The cap
itself is enforced against **actual rendered length** whatever either
document declared (§4.6.4, trim during play), so a disagreement
between the two changes what the Player can predict, never what it
enforces.

### 5.5 Tracking carrier

<!-- refine: v7.1-detail-review.md#flag-3 -->
Timeline-scheduled beacons — impression, start, quartiles, complete
— are carried as `<Event>` entries inside an `<EventStream>` of scheme
`urn:mpeg:dash:event:callback:2015`, defined in §4.7 of the base
specification and in its §5.10.4.5. This specification introduces
**no** tracking scheme of its own.

**Why the callback scheme is reused as-is.** It already is a beacon
carrier: an `<EventStream>` at Period level or an inband `emsg`,
on-start dispatch, the client firing an HTTP GET to the URL carried in
the event at the event's presentation time and discarding the response
without parsing it. Nothing in it needed extending for ads, and a
parallel scheme would have split tracking across two carriers for no
semantic gain.

#### 5.5.1 Carrier shape

<!-- refine: v7-dash-conformance-audit.md#NC1 -->
```xml
<EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
             value="1" timescale="1000">
  <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=1</Event>
  <Event presentationTime="0"     id="2">https://tracker.example.com/start?ad=1</Event>
  <Event presentationTime="2500"  id="3">https://tracker.example.com/firstQuartile?ad=1</Event>
  <Event presentationTime="5000"  id="4">https://tracker.example.com/midpoint?ad=1</Event>
  <Event presentationTime="7500"  id="5">https://tracker.example.com/thirdQuartile?ad=1</Event>
  <Event presentationTime="10000" id="6">https://tracker.example.com/complete?ad=1</Event>
</EventStream>
```

Attributes on the `<EventStream>`:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@schemeIdUri` | yes | `xs:anyURI` | — | `urn:mpeg:dash:event:callback:2015` for every tracking carrier under this specification. |
| `@value` | yes | `xs:string` | — | `1`, the value Table 47 of the base specification fixes for this scheme. Every tracking carrier authored under this specification declares it. | <!-- refine: v7-dash-conformance-audit.md#M3 -->
| `@timescale` | yes | `xs:unsignedInt` | — | Time base for `<Event>@presentationTime`. `1000`, giving millisecond resolution, is the value used throughout this document. |

Attributes on each `<Event>`:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@presentationTime` | yes | `xs:unsignedLong` | — | When the Player fires the beacon, in `@timescale` units, measured from the start of **this ad's** presentation. |
| `@id` | yes | `xs:unsignedLong` | — | Identifier of the beacon, used by the Player for de-duplication and by the implementation for logging. The type is the base specification's own (§5.10.2.3), narrowed from optional to required. | <!-- refine: v7-dash-conformance-audit.md#NC1 -->

The element's text content is the absolute HTTP(S) URL the Player
GETs at the scheduled time.

The quartile names in the example are the ADS's schedule as it reached
the document, not a schedule this specification prescribes. This
specification fixes the carrier and the timebase; which beacons exist,
how many, and at which fractions of the presentation they sit are the
ADS's, and the Player executes what the document carries.

#### 5.5.2 Where the carrier lives

| Ad | Position of the tracking `<EventStream>` |
|---|---|
| Linear | Inside the sub-MPD's `<Period>`, one per ad |
| Non-linear, `video` form | Inside the form's sub-MPD `<Period>`, **or** directly inside the `<svta:Candidate>`. The two positions are equivalent. |
| Non-linear, `image` or `html` form | Directly inside the `<svta:Candidate>`; there is no sub-MPD to host it. |

When a candidate carries a tracking `<EventStream>` and its video
form's sub-MPD carries one as well, the Player fires the union, with
beacons that share an `@id`, or the same URL at the same
`presentationTime`, fired once.

<!-- refine: v7.1-dash-conformance-audit.md#NC2 -->
> **Note for tooling.** The base specification places `<EventStream>`
> only as a child of `<Period>` (§5.3.2.3 of the base specification).
> Carrying it directly inside `<svta:Candidate>` is admissible as
> foreign-namespace open content but is novel relative to that
> canonical placement, so a validator or analytics pipeline that
> locates callback event streams by scanning only `<Period>` children
> misses the carrier attached to a non-video candidate. Tooling
> implementing this specification scans inside `<svta:Candidate>` as
> well.

#### 5.5.3 The timebase

Every `<Event>@presentationTime` inside a resolution document is
expressed **relative to the start of the ad's own presentation** —
never to the primary timeline, never to wall-clock. A beacon on the
ad's first frame declares `presentationTime="0"`; quartile beacons for
a 10-second ad at `timescale="1000"` sit at 2500, 5000 and 7500. The
Player adds the ad's start position on the primary timeline to each
relative value to obtain the firing point.

An `image` or `html` form has no segment-aligned media to anchor that
origin, so the Player establishes the ad's presentation timeline at
the moment the asset becomes visible: offset 0 is the first rendered
frame of the image or of the HTML document.

Beacon scheduling runs on the presentation timeline, so a primary
content playing at a speed other than 1× moves the wall-clock instants
at which beacons fire without changing their scheduled presentation
times (§4.6.12).

### 5.6 ClickThrough carrier

The resolution document carries the ad's ClickThrough URL and its
associated click-tracking URLs in a single normative carrier, so that
every conformant Player reads them the same way.

**Why a new construct, and why not the callback scheme.** The base
specification defines no carrier for click-through metadata, and —
more fundamentally — no user-triggered event of any kind: every event,
event stream and timed metadata track is evaluated against the media
presentation timeline, and the callback scheme in particular fires its
GET when the playhead reaches the event's presentation time. A
ClickThrough activation has no presentation time; it happens when the
viewer acts, or never. The callback scheme is therefore the right
carrier for impressions and quartiles and the wrong one for the click.
The base specification itself splits the two concerns the same way in
Annex L, where the event sits on the timeline while the viewer's
interaction is resolved off it through a callback URL.

This carrier is **normative and interoperable**, which is what
separates it from the best-effort metadata of §5.7: the click works
across Players, rather than being silently ignored by some of them.

#### 5.6.1 `<svta:Click>`

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@clickThroughUrl` | yes | `xs:anyURI` | — | The destination the Player opens, or hands off to the platform, when the viewer activates the click. |

| Child | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:ClickTracking>` | no | 0..n | One click-tracking URL, carried as the element's text content. The Player fires each one once, at the moment of activation. |

Whether a ClickThrough carries any click-tracking at all is the
advertiser's decision. A `<svta:Click>` with no `<svta:ClickTracking>`
child is a complete, conformant declaration: the Player opens the
destination and fires nothing.

```xml
<svta:Click xmlns:svta="urn:svta:dash:sgai:2026"
            clickThroughUrl="https://advertiser.example.com/landing">
  <svta:ClickTracking>https://tracker.example.com/click?ad=1</svta:ClickTracking>
  <svta:ClickTracking>https://thirdparty.example.net/c?id=1</svta:ClickTracking>
</svta:Click>
```

<!-- refine: v7-spec-validation.md#T4 -->
On a non-linear slot the element is a child of `<svta:Candidate>`, so
the ClickThrough travels with the ad rather than with the slot: a
Publisher configures nothing beyond permitting the ad. On a linear
slot the same element is the carrier and is carried as
foreign-namespace open content on the `ListMPD` `<Period>` of the ad
it belongs to, which a legacy Player discards with its subtree
exactly as it discards the element inside a candidate.

<!-- refine: v7-dash-conformance-audit.md#M4 -->
> **Note on profile signalling.** §8.1 of the base specification
> removes, for a profile-conformance check, every extension-namespace
> element the declared profile does not explicitly include. A
> `ListMPD` whose `@profiles` names only
> `urn:mpeg:dash:profile:list:2024` therefore has its `<svta:Click>`
> removed by that procedure, and a client bound to the list profile
> alone is entitled to drop it.

On a Player that predates this specification the click is inert: the
carrier is discarded with its parent subtree, the ad renders, and no
click fires.

### 5.7 Application-level metadata

Generic application-level creative metadata that has no native DASH
carrier — the identity of the ad system, the creative's title, the
advertiser, a universal ad identifier — rides on extension elements in
the SVTA Ads WG namespace, as children of `<svta:Candidate>`.

This carrier is **optional on both ends by design**: nothing obliges
an APS to emit it or a Player to read it, and a legacy Player discards
the elements with the parent subtree. What this specification fixes is
that the place exists and is named; nothing in the ad presentation
depends on anyone using it.

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `<svta:AdSystem>@value` | yes, when the element is present | `xs:string` | — | Identifier of the ad system that produced the decision. |
| `<svta:AdTitle>@value` | yes, when the element is present | `xs:string` | — | Human-readable title of the creative. |
| `<svta:Advertiser>@value` | yes, when the element is present | `xs:string` | — | Human-readable identifier of the advertiser. |
| `<svta:UniversalAdId>@idRegistry` | yes, when the element is present | `xs:string` | — | Registry that scopes the identifier, for example `ad-id.org`. |
| `<svta:UniversalAdId>@value` | yes, when the element is present | `xs:string` | — | The registry-scoped identifier of the creative. |

Each of the four elements is an OPTIONAL child of
`<svta:Candidate>`, at most once.

`<svta:UniversalAdId>` is listed here deliberately rather than as a
normative carrier of its own. A universal ad identifier serves ad
tracking and reconciliation on the decisioning side, which the
upstream ad standards already handle; this specification does not
replicate that carrier in the resolution document. An APS that wants
to propagate the identifier anyway has a named place for it, and no
Player behaviour depends on it. This is the deliberate contrast with
the ClickThrough of §5.6, which is mandated because the click has to
work cross-Player.

### 5.8 The resolution request

The Player issues the resolution request as an HTTP GET against the
slot's `@uri`. Two independent sources contribute query parameters to
that URL: the Publisher's author-declared template (§5.8.1) and the
Player's own capability declaration (§5.8.2).

#### 5.8.1 Publisher-declared parameters

<!-- refine: v7-dash-conformance-audit.md#NC2 -->
The Publisher MAY declare a query template on the main MPD through the
base specification's extended HTTP GET parameterisation: a
`<RequestParam>` element of type `ExtendedUrlInfoType`, enabled by an
`<EssentialProperty>` descriptor with
`@schemeIdUri="urn:mpeg:dash:urlparam:2025"`. Annex I.3.1 of the base
specification requires that descriptor to be **present and empty**,
and carries the `<RequestParam>` element itself at a DASH hierarchy
element — `MPD`, `Period`, `AdaptationSet`, `Representation`,
`Preselection` or `EventStream` — rather than inside the descriptor.
Authoring it inside the slot's own `<EventStream>` scopes the template
to the slot that owns it. The attribute that scopes the template to a
slot's resolution request is `@includeInRequests`, whose admissible
values are a whitespace-separated list of request types; the value
that names an alternative-MPD resolution request is **`altmpd`**.

<!-- refine: v7-dash-conformance-audit.md#NC3 -->
The empty descriptor is an `<MPD>` child and `MPDtype` is an ordered
`xs:sequence` in which `EssentialProperty` follows `Period`, so it is
authored **after** the last `</Period>`.

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">
  <Period id="1" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="101" presentationTime="0" duration="20000">
        <InsertPresentation uri="https://aps.example.com/decision/preroll"
                            maxDuration="20000"/>
      </Event>
      <RequestParam includeInRequests="altmpd"
                    queryTemplate="video_profile=$urn:mpeg:dash:state:video$&amp;session_id=$urn:mpeg:dash:state:cmcd#sid$"/>
    </EventStream>
    <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
    </AdaptationSet>
  </Period>
  <EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025"/>
</MPD>
```

At resolution time the Player substitutes the state-vocabulary
variables with live values and appends the resulting query string to
the slot's `@uri`. This specification extends that mechanism in no
way.

#### 5.8.2 Player-declared capability parameters

This specification reserves a set of **query-parameter names** the
Player MAY attach to the resolution request, stating what its device
can render. Which of them travel is the Player's decision, taken at
runtime; no declaration by the Publisher, the APS or the ADS is
required before a Player sends them.

**Why these are not carried by the author-declared template.** The
base specification's upstream channel is the mechanism of §5.8.1, and
it misses on both axes. Its payload is session state — the `@codecs`
and `@bandwidth` of what is playing, selected language, trick-play
state, per-event execution counters and deltas, throughput, service
location — and it contains no parameter for decoder count, image
rendering or HTML-overlay support: it reports what is *playing* and
what has *run*, not what the device can *render*. And its parameter
set is authored by the content author in the MPD, so a Player cannot
add an axis to a template it did not write. The two neighbouring
mechanisms miss for their own reasons: CMCD carries operational
delivery state, and `ServiceDescription` runs the opposite way,
letting the service prescribe consumption targets to the client. The
reserved set below is new by necessity rather than by preference.

The parameters are **inputs about the device** — statements of what it
supports — and not conclusions about which ad experiences can be
served. Deriving the second from the first is the APS's work.

| Parameter | Required | Type | Default | Description |
|---|---|---|---|---|
| `sgaiVideoDecoders` | no | unsigned integer, `1` or greater | — (absent means undetermined, §5.8.4) | How many video decoders the device runs concurrently, counting the one presenting the primary content. |
| `sgaiImageOverlay` | no | boolean (`true` \| `false`) | — (absent means undetermined) | Whether the device composites a still image on top of, or alongside, playing video. |
| `sgaiHtmlOverlay` | no | boolean (`true` \| `false`) | — (absent means undetermined) | Whether the device composites an HTML surface on top of, or alongside, playing video. |

Example:

```
GET /decision/overlay?slot=mid1&sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=false
```

The set is minimal against its acceptance test, which is that it tells
the five device classes of §3.4 apart:

| Declaration | Class |
|---|---|
| `sgaiVideoDecoders=2`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=true` | D1 |
| `sgaiVideoDecoders=2`, `sgaiImageOverlay=false`, `sgaiHtmlOverlay=false` | D2 |
| `sgaiVideoDecoders=1`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=true` | D3 |
| `sgaiVideoDecoders=1`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=false` | D4 |
| `sgaiVideoDecoders=1`, `sgaiImageOverlay=false`, `sgaiHtmlOverlay=false` | D5 |

A fourth axis would have to distinguish two classes these three
already separate, so none is reserved. A boolean is used rather than
an enumerated surface list because a list has no way to say "no
surfaces at all" that is distinguishable from an empty value, and
§5.8.3 requires a parameter the Player will not populate to be
**omitted** rather than emptied.

#### 5.8.3 Sending, omitting, and extending

- Sending a reserved parameter is **optional**. A conformant Player
  sends all of them, some of them, or none.
- When the Player has no value for a reserved parameter, or does not
  disclose its value, it **omits the parameter entirely** rather than
  sending it with an empty or placeholder value.
- A parameter the Player attaches that is not one of the reserved
  names carries a vendor-specific prefix of the form `x-<vendor>-`, so
  that reserved names added in a later edition stay free.
- The reserved names are reserved on the resolution request as a
  whole. A Publisher authoring a `<RequestParam>` query template
  (§5.8.1) draws its parameter names from outside the reserved set, so
  the two sources compose on one URL without collision.

#### 5.8.4 What an absent parameter means

A reserved parameter absent from the resolution request means its
value is **undetermined**: the Player did not determine it, or did not
disclose it. Absence does not assert that the device lacks the
capability.

This specification does not define how an APS resolves an undetermined
value. An APS that resolves it conservatively — emitting no option
that depends on the undetermined axis — and an APS that assumes the
most capable case are both conformant, and they will emit different
documents to the same Player. What does not vary is that the Player
checks whatever arrives before rendering it (§4.6.5).

An APS answers a request that carries none of the reserved parameters
by emitting the candidate's options unnarrowed (§4.5.9). A Player that
declares nothing therefore receives the full ordered list and resolves
the choice itself — which is the same document an APS emits when it
holds no device view at all.

## 6. Interfaces

This chapter describes the message flows between the four actors, the
transports they run on, and the payloads they carry. Everything below
the Player↔APS boundary is Player-visible and normative; the APS↔ADS
exchange appears once, marked non-normative, because it is what the
APS converts *from* and this specification defines only what it
converts *to*.

### 6.1 The end-to-end flow

```
                                        primary content (Publisher CDN)
                                                   ^
                                                   | (3) GET segments
                                                   |
 +-------------+   (1) GET main MPD   +----------+ |  (5) GET ad segments / assets
 | Publisher   |<---------------------|          |-+-------------------------> ad CDN
 | (encoder +  |                      |          |
 |  packager + |--(2) MPD with -------|  Player  |   On the resolution response:
 |   CDN)      |     SGAI events      |          |     (6) validate vs MPD constraints
 +-------------+                      |          |     (7) enforce @maxDuration
                                      |          |     (8) fire beacons on the timeline
                                      +----+-----+     (9) fire the click on activation
                                        |    ^
                        (4a) GET        |    |  (4b) 200 OK
                     <slot @uri>?<q>    |    |  resolution document (XML)
                                        v    |
                                      +----------+  (4c) ad decisioning
                                      |   APS    |<----------------------> ADS
                                      | (adapter)|   (decision document,
                                      +----------+    typically VAST)
```

1. The Player issues a `GET` for the main MPD.
2. The Publisher serves the MPD, carrying one or more SGAI
   opportunities as `<EventStream>` / `<Event>` pairs (§5.1). Each
   event's `@uri` resolves to the APS.
3. The Player fetches primary segments and plays the main timeline.
4. As the playhead approaches an event's `presentationTime` minus its
   `@earliestResolutionTimeOffset` — the Earliest Resolution Time —
   the Player picks an instant between the ERT and the event's
   `presentationTime` and issues the resolution request (4a). The APS
   replies `200 OK` with the resolution document (4b). Internally the
   APS obtains the ad decision (4c) and converts it.
5. The Player fetches the ad's media: segments from the ad CDN for a
   video form, the asset at `@assetUrl` for an image or HTML form.
6. The Player validates each candidate against the slot constraints
   the Publisher declared (§4.6.1).
7. The Player enforces `@maxDuration` (§4.6.4).
8. The Player fires the timeline-scheduled beacons through the
   callback carrier (§5.5).
9. On viewer activation, the Player opens the ClickThrough and fires
   its click-tracking (§5.6).

<!-- refine: v7.1-spec-validation.md#T3 -->
At the end of a linear alternative presentation the Player resumes the
main timeline per the event's semantics: an insert resumes where the
main timeline was paused, a replace resumes at the position determined
by `@returnOffset`, because main media time kept advancing while the
ad played. A non-linear slot does not suspend the main timeline,
except when the option the Player selects is the `linear` full-screen
takeover, which plays sequentially with the primary content
(§5.3.7.3).

A Player that does not implement the SGAI event scheme never reaches
step 4, so it never reaches steps 5 to 9 either. Its flow is steps 1,
2 and 3, and the primary content plays uninterrupted.

### 6.2 Publisher → Player: the main MPD

| | |
|---|---|
| Transport | HTTP/HTTPS, pull |
| Payload | DASH MPD (XML) |
| Carries | Primary content Periods, plus one `<EventStream>` per SGAI opportunity (§5.1), plus optionally a `<RequestParam>` query template (§5.8.1) and a standard linear break authored as the VOD legacy fallback (§4.3.7) |
| Errors | HTTP status codes. On 4xx / 5xx the Player retries or aborts the session per DASH-IF guidance; ad behaviour is not involved. |

The Publisher is an authoring-time actor: it emits nothing at runtime
and guarantees nothing at runtime. Every unmet Publisher obligation
degrades into a Player-side skip, never into interrupted playback.

### 6.3 Player → APS: the resolution request

| | |
|---|---|
| Transport | HTTP/HTTPS GET, pull, synchronous |
| Payload | Query parameters on the slot's `@uri`: the Publisher-declared template (§5.8.1) and the Player's reserved capability parameters (§5.8.2) |
| Timing | At an instant between the Earliest Resolution Time and the event's `presentationTime`. Spreading that instant randomly across the window smooths APS load. |
| Cardinality | One request per slot. Wrapper resolution and any upstream hops happen inside the APS; the Player sees one round trip. |

### 6.4 APS → Player: the resolution response

| | |
|---|---|
| Transport | HTTP/HTTPS, response to §6.3 |
| Payload | `ListMPD` (§5.2.1) for a linear slot; Overlay Resolution Document (§5.2.2) for an overlay or pause-ad slot |
| Success | `200` with a document body. A `200` carrying **no candidates** is also success: the opportunity resolved, and it resolved to no ads (§5.2.3). |
| Failure | A transport-level failure, or a final status other than `200`. The Player treats the window as unresolvable and falls through to the next overlapping same-family window if the Publisher declared one, else to primary content (§4.6.8). |

### 6.5 Player → ad CDN: fetching the creative

| | |
|---|---|
| Transport | HTTP/HTTPS, pull |
| Payload | For a `video` form, the sub-MPD and then its media segments. For an `image` or `html` form, the asset at `@assetUrl`. |
| Errors | An ad segment or asset that fails leaves the Player on the primary content: it aborts that ad and continues, optionally advancing to the next candidate (§4.6.2, §8.1 row E11). |

### 6.6 Player → tracking endpoints

| | |
|---|---|
| Transport | HTTP/HTTPS GET, fire-and-forget |
| Payload | None. The URL is the message; the Player discards the response body. |
| Timing | Timeline-scheduled beacons at their `presentationTime` relative to the ad's presentation (§5.5.3); click-tracking at the instant of viewer activation (§5.6). |
| Errors | Non-fatal. A failed beacon leaves the ad and the primary content unaffected and never reaches the viewer. |

### 6.7 APS → ADS, and the conversion (non-normative)

The APS obtains the ad decision from the ADS and converts it into the
resolution document. Neither the request nor the decision document's
format is defined by this specification: the APS-to-ADS contract is
agreed bilaterally by those parties. The mapping below is included
because VAST is the de-facto upstream format and implementers ask how
the two line up. It is illustrative, and conformance to this
specification depends on none of it.

| Decision-document element (VAST vocabulary) | Resolution-document target |
|---|---|
| An inline ad in a linear pod | One `<Period>` with one `<ImportedMPD>` in the `ListMPD` (§5.2.1) |
| An inline ad for a non-linear slot | One `<svta:Candidate>` in the Overlay Resolution Document (§5.2.2) |
| A wrapper / redirect chain | Resolved inside the APS until an inline ad is reached; invisible to the Player |
| The creative's duration | `Period@duration` on the `ListMPD` Period and on the sub-MPD; `<svta:Candidate>@duration` for a non-linear candidate |
| Each media file of a video creative | One `<Representation>` inside an `<AdaptationSet>` of the sub-MPD; several media files collapse into one ABR ladder |
| A non-linear creative that is an image or an HTML document | `@assetUrl` on a `<svta:RenderableAsset>` (§5.3.1) |
| The tracking events and the impression | `<Event>` entries in a callback `<EventStream>`, at the matching relative times (§5.5) |
| The click-through and its click trackers | `<svta:Click>` with its `<svta:ClickTracking>` children (§5.6) |
| Ad system, ad title, advertiser, universal ad id | The optional metadata elements of §5.7 |
| A decision carrying no ads | A resolution document carrying no candidates (§5.2.3) |
| An error signalled by the ADS | Nothing in the document. How the APS reacts belongs to the APS-to-ADS contract; what the Player observes is an opportunity that yields no candidates, and it continues with the primary content. |

Two conversion cases are worth naming because they have no
Player-visible answer. A decision entry that carries **tracking only**
and no media cannot become a candidate, since there is no creative to
render; whether the APS omits it silently or signals upstream is
APS-internal policy, and the Player-visible half is covered by the
empty resolution of §5.2.3. And the **fidelity** of the transcription
— that the beacons and the ClickThrough the ADS declared all reach the
document — is enforceable by the ADS, which declared them and receives
their results, and not by the document, which does not show what was
declared.

### 6.8 Interface contracts summary

| Source | Target | Transport | Payload | Failure behaviour |
|---|---|---|---|---|
| Player | Publisher CDN | HTTPS | Main MPD, primary segments | DASH baseline retry / abort |
| Player | APS | HTTPS | Request: query parameters. Response: resolution document | `200` with no candidates is an answer; transport failure or non-`200` triggers the fallback window if declared, else primary content |
| Player | Ad CDN | HTTPS | Sub-MPD, ad segments, image / HTML assets | Abort the ad, continue the primary content |
| Player | Tracking endpoint | HTTPS | Beacon GET, body-less | Non-fatal, optionally retried, never surfaced to the viewer |
| APS | ADS | Bilateral | Bilateral | Outside this specification |

All transport runs over HTTPS in production. Authentication, DRM and
token exchange layer on top of it per DASH-IF guidance and are
orthogonal to SGAI.

## 7. Expected behaviour

This chapter states, per actor and per scenario, what an
implementation does. The deep walk-throughs — complete MPDs,
resolution documents and sub-MPDs — live in the annexes.

### 7.1 Publisher behaviour

The Publisher acts once, at authoring time, and produces one artefact:
the main MPD. For each opportunity it decides the slot family, the
position and length of the window, the cap, the allowed layouts, and
the APS endpoint, and it encodes all of them in the manifest so that
they are normative for the slot rather than inferred at runtime.

Two authoring choices recur:

- **Insert or replace, for a linear slot.** An insert introduces the
  ad without consuming any primary timeline and is for content whose
  playhead can be stopped indefinitely — on-demand or pre-recorded.
  A replace substitutes a bounded span of the primary timeline and is
  for live or linear content, where there is no meaningful frame zero
  of the primary stream to preserve. The base specification confines
  the insert event to non-`dynamic` MPDs, which is the rule behind the
  choice.
- **Whether to author a legacy fallback.** For VOD, a standard linear
  break authored with baseline constructs alongside the SGAI
  opportunity monetises the slot on Players that predate this
  specification. For live, the opportunity is an expected loss on
  those Players (§4.3.7, §4.3.8).

### 7.2 ADS behaviour

The ADS receives an ad request from the APS and decides which ads to
serve, how many, and in what order, applying its own targeting,
frequency capping, brand-safety filtering, competitive separation and
fill-rate logic. It declares the tracking schedule with the decision.

The number of ads in an opportunity is an ADS decision: the Publisher
declares the *space* — the cap and the allowed layouts — and does not
prescribe how many ads fill it. The ADS optimises the slot within that
envelope and is not required to respect the cap; the Player enforces
it.

The ADS holds no view of the device and returns the same decision to
every viewer unless its own logic says otherwise. A decision that
carries no ads is a legitimate outcome.

### 7.3 APS behaviour

On each resolution request the APS obtains the ad decision, converts
it into the resolution document for the slot family, and answers.
The conversion maps creatives onto presentation options, durations
onto the document's duration attributes, and the ADS's tracking events
onto callback events, preserving the order the ADS decided.

When the request carries capability parameters the APS MAY narrow the
options it emits, keeping the surviving options in the ADS's order.
When it carries none, the APS emits the options unnarrowed. Either way
the document it produces looks the same to the Player, and the Player
checks what it receives before rendering it.

### 7.4 Player behaviour: the common loop

For every opportunity, on every device class, the Player runs the same
loop:

1. **Read** the slot's constraints from the main MPD.
2. **Resolve** the slot's `@uri` at or after the Earliest Resolution
   Time, attaching whichever capability parameters it chooses to
   declare.
3. **Validate** each candidate against the slot's constraints.
4. **Walk** the surviving candidates in document order; for each, walk
   its presentation options in document order and render the first
   that satisfies both the device's budget and the slot's allowed
   layouts.
5. **Enforce** the cap against actual rendered length while the ad
   plays.
6. **Fire** the beacons the document scheduled, and the click when the
   viewer activates it.
7. **Fall through** to the primary content when the candidates are
   exhausted, when the document carries none, when the request failed,
   or when an accepted ad fails at runtime.

Declining the opportunity is a valid outcome of that loop and not a
failure. It is also the **last** step, reached only once every
candidate and every option has been tried.

### 7.5 Per-scenario behaviour

#### 7.5.1 Linear slot at the start of a session, and mid-content

The Publisher declares a linear slot — at `presentationTime="0"` for
the start of the session, at the chosen position for a mid-content
break — allowing linear forms only and bounding the duration. The
resolution document is a `ListMPD` whose Periods are the ads to play,
in order.

The Player plays the ads back-to-back, switching its rendering source
between the primary content and the ad and back, and enforces the cap
against the rendered length. Because a linear ad and the primary
content are sequential rather than concurrent, the behaviour is the
same on every device class: a single decoder is reused across the ad
and the primary content, and no overlay surface is involved. A device
with a second decoder MAY pre-buffer the next ad on it, which is an
implementation detail with no effect on the Publisher's constraints.

When the primary content is playing at a speed other than 1×, the ad
renders at that same speed; the cap and the beacon schedule stay on
the presentation timeline, so neither changes with the speed, while
the ad's wall-clock time on screen is the derived value (§4.6.12).

**Annexes A and B** walk the two cases end to end.

#### 7.5.2 Multi-ad break

A single linear slot filled by several ads played back-to-back with no
primary content between them. The Publisher bounds the total; how many
ads fit inside is the ADS's decision.

The Player plays the candidates in the document's order and enforces
the cap against the **cumulative** rendered length: when the running
total reaches the cap, it stops, even if the ad in progress has not
finished. It MAY also drop a candidate before playback when the
candidate's declared duration would overflow the cap. The candidates
that survive keep their declared order.

**Annex F** walks the arithmetic.

#### 7.5.3 Coexisting overlay

The Publisher declares an overlay slot: non-linear forms allowed, a
restricted set of layouts, a bounded duration. The primary content
keeps playing throughout.

The Player resolves the slot, validates the candidates, and walks the
selected candidate's options in document order, rendering the first
its device can satisfy against the budget of §5.3.7.3. The
per-device-class outcome is not authored anywhere: it emerges from
that walk. On a top-tier device the first option usually wins; on a
device that composites video on video but no other surface, a video
overlay or a side-by-side without a background element may win while
every image and HTML option fails; on a single-decoder device with
image and HTML surfaces, the video option fails for want of a second
decoder and an HTML or image option wins; on a device with no overlay
capability of any kind, every option that requires concurrent
composition fails and the Player either renders a full-screen takeover
option if the candidate offers one, or declines the opportunity and
keeps the primary content running.

A slot MAY be filled by several forms in sequence — a 30-second
overlay window carrying three 10-second forms is presented as one,
then the next, then the next, each starting when the previous ends —
with the cap applied to their cumulative duration. At no instant is
more than one form on screen.

**Annex C** walks the multi-form case; **Annex I** walks the ordered
options across all five device classes.

#### 7.5.4 Hybrid: a linear ad with a concurrent overlay

Two events at the same position: a linear take-over and an overlay on
top of it. The Player resolves and validates each independently and
composes the two.

Whether the overlay portion reaches the screen depends on what the
device can composite **while the linear ad occupies the video
surface**. A device with a second decoder composites a video overlay
on top of the linear ad. A device with overlay surfaces but a single
decoder presents the linear portion alone when the overlay option
needs to be composited on top of the linear ad's video, and MAY
present a squeezeback option whose budget it can satisfy. A device
with no overlay capability presents the linear portion alone. In every
case the linear portion plays and the break completes.

**Annex D** walks the case.

#### 7.5.5 Pause-triggered ad

The Publisher declares a window of validity. A pause inside the window
permits a pause ad; a pause outside it permits none.

On a pause transition inside the window, the Player resolves the slot
— speculatively ahead of time or lazily at the pause (§8.5) — selects
an option, and presents it over the paused primary frame, fullscreen
or partial. On resume it dismisses the pause ad within one rendering
frame and ceases its remaining beacons.

Because the primary content is paused, the decoder holding the paused
frame may be re-taskable, so a video pause ad can be satisfiable even
on a single-decoder device. Whether a given device can do that is a
device property; the conservative behaviour is in §8.4.

In live content, the Player's presentation time freezes inside the
window for as long as the viewer stays paused, up to the ceiling the
time-shift buffer sets (§4.6.9).

**Annex E** walks the case.

#### 7.5.6 An overlay window crossing a pause-ad window

An overlay is on screen and the viewer pauses inside a pause-ad
window. The pause ad takes priority: the Player suspends the overlay,
resolves and presents the pause ad, and on resume dismisses the pause
ad and restores the overlay if the overlay's window is still open. The
overlay's window clock follows the primary timeline, so it froze
during the pause; the overlay ends when its declared window expires,
not because of the pause.

The priority holds whether the pause ad is fullscreen or partial, so
at no instant are two non-linear forms composited together. When the
device can render neither surface, both opportunities are declined and
the pause and resume have no ad-related effect.

**Annex H** walks the case.

#### 7.5.7 A Player that predates this specification

The Player meets an event scheme it does not implement, skips the
`<EventStream>` and every event inside it, and keeps playing. It never
issues a resolution request, so the ADS is never consulted and no
beacon fires for the opportunity.

What the viewer sees depends on what the **Publisher** authored, and
that is content-dependent:

- **Live, or VOD with no fallback authored** — the primary content
  plays uninterrupted, no ad is rendered, no error surfaces.
- **VOD with a standard break authored as the fallback** — the legacy
  Player plays the standard break it does understand, then resumes the
  primary content.

The outcome does not vary across device classes: it depends on the
Player's version and on the content type, not on the device's
hardware. A top-tier device running a legacy Player behaves exactly
like a worst-case device running one.

**Annex G** walks the case.

#### 7.5.8 ClickThrough

An ad is on screen and the viewer activates the click — a select on a
CTV remote, a tap on a phone. The Player opens the ClickThrough
destination and fires each associated click-tracking URL once.

The behaviour does not vary across device classes: it depends on the
device's input mechanism, not on its decoder or surface budget. On a
Player that predates this specification the click is inert.

**Annex K** walks the case.

#### 7.5.9 Overlapping windows of the same family

Two overlay windows overlap in the main MPD. The Player serves the
first and treats the second as a backup, reaching for it only when it
cannot access the first window's resolution document. Three paths end
the scenario, and all three leave the primary content playing:

1. The first window answers with a document carrying no candidates.
   The opportunity resolved, and it resolved to no ads. The second
   window is not touched.
2. The first window cannot be accessed and the second answers with a
   document carrying one candidate. The Player validates that candidate
   against the second window's own constraints and renders it: the
   fallback was used as declared, end to end.
   <!-- refine: v7-detail-review.md#flag-6 -->
3. Neither window can be accessed and no further fallback is
   declared. The chain is exhausted, no candidate was ever accepted,
   and the Player skips the opportunity.

This is window selection rather than rendering, so it is
device-agnostic: the device class affects only how the forms inside
the chosen window render.

**Annex L** walks the case.

#### 7.5.10 One ad across five device classes, resolved two ways

The same candidate, the same ordered options and the same
device-agnostic allowed-layout set produce the same rendered result on
each device class under either division of labour:

- **The Player discloses nothing.** The APS emits every option. Each
  Player walks the list and renders the first it can satisfy. The
  five classes land on three different layouts without any actor
  upstream of the Player holding a device-class matrix.
- **The Player declares its capabilities.** The APS resolves against
  the declaration and emits a single option. The Player checks that
  option against its own capability and the Publisher's allowed
  layouts, and renders it — or passes over the candidate if the check
  fails.

Neither is canonical. What moved is where the capability check was
resolved, not what the viewer sees. And the two meet at the edge: a
Player that declares nothing leaves the APS unable to narrow, and an
APS that cannot narrow emits the full ordered list — so the first case
is what the second APS produces when it is told nothing.

**Annexes I and M** walk the two.

## 8. Implementation notes

This chapter is **non-normative**. It records the guidance an
implementer needs where the normative chapters leave a decision open,
and names the places where this specification deliberately states no
obligation.

### 8.1 Error semantics

Fifteen conditions cover the ways an ad opportunity can fail to be
honoured on the Player-visible interfaces. For each, the table gives
what the Player does, what it MAY additionally do, and what the other
actors carry.

Out of the table's scope: the APS↔ADS exchange, which reaches the
Player only as E1, E2 or E5; primary-content delivery errors and
DRM / token exchange, which are DASH baseline concerns orthogonal to
SGAI; and the document-level obligations, which a runtime cannot
violate.

| ID | Condition | Player response | Player MAY | Other actors |
|---|---|---|---|---|
| **E1** | The resolution request fails at transport level: DNS unresolvable, connection refused, TLS handshake failure, or timeout before any final status. | Treat the window as unresolvable: fall through to the next overlapping same-family window when the Publisher declared one, else continue with the primary content uninterrupted (§4.6.8). | Re-attempt within the interval between the ERT and the event's `presentationTime`; surface the failure through an implementation-defined API. This specification fixes no retry count, backoff or deadline. | Publisher: declare a fallback window where continuity matters, and an `@earliestResolutionTimeOffset` wide enough to leave room. APS: serve the slot's `@uri` for the whole window. |
| **E2** | The resolution request returns a final status other than `200`, including an APS that refuses to answer because a capability parameter was absent. | Same as E1. | Re-attempt before the event's `presentationTime`; log. | APS: tolerate the absence of every reserved parameter and produce candidates without any of them (§4.5.9); an absent parameter is undetermined, never unsupported (§5.8.4). |
| **E3** | The response is `200` but the body is not well-formed XML, carries an unknown root element, or fails schema validation. | Render nothing from that document and continue playing the primary content uninterrupted (§4.6.2). | Log the parse or validation failure. A `200` carrying an unusable body is neither the accessible-and-empty case of §5.2.3 nor one of the access failures of §4.6.8; treating it as an access failure and trying the fallback window is the reading most consistent with the intent, and a Player that instead declines the opportunity is also within the normative text. | APS: emit a document valid against the base specification schema plus the extension points of §4.7. |
| **E4** | The resolution document arrives after the slot window has elapsed. | Keep the slot within the Publisher-declared cap rather than extending it to play the late document, and keep the primary content uninterrupted. | Discard the document, or retain it for a later still-unresolved window of the same family. The base specification defines late *execution* of a linear event — `@clip` trims to `@maxDuration`, `@startWithOffset` decides whether a delayed ad starts at its first frame — but a document that lands after the window is over has no corresponding rule, and this specification adds none. | Publisher: declare an `@earliestResolutionTimeOffset` that gives the APS a usable head start. APS: answer inside the window it was asked in. |
| **E5** | The response is `200` and the document carries no candidates — the opportunity resolved to no ads. | Continue with the primary content uninterrupted, exactly as when the candidates are exhausted, and leave any fallback window untouched: the opportunity resolved (§4.6.8, §5.2.3). | Report the opportunity as **unfilled** rather than failed, through an implementation-defined API. This is the distinction with the most operational value in the whole table. | APS: express a no-ads decision as a document carrying no candidates, never as an error status and never as a bodiless response (§4.5.7). ADS: none — no-fill is a decision, not a failure. |
| **E6** | No presentation option on a candidate is satisfiable: the device renders none of the offered forms, or every offered layout needs more decoders or surfaces than the device has. | Skip that candidate and advance to the next in document order; continue with the primary content only once every candidate is exhausted (§4.6.6). | Report the skip. | APS: carry the options as an ordered list in preference order (§4.5.3). Neither ADS nor APS is required to hold a device-class matrix; a candidate carrying a single option places the suitability call upstream. |
| **E7** | An option names a layout the Publisher did not allow on the slot, or one outside the enumeration of §3.2. | Do not render that option; move to the next in document order, and skip the candidate when none passes both the device check and the allowed-layouts check (§4.6.5). | Report the rejected layout name. | Publisher: draw allowed-layout names only from §3.2 (§4.3.3). APS: emit form metadata only for the enumerated types and placements (§4.5.4). |
| **E8** | A candidate's creative carrier is outside the admissible set of §3.3, or a non-AV asset URL is expressed as `@mimeType` on a path bound by RFC 4337. | Render no form the device cannot render. | Skip the candidate as a non-conformant upstream signal and fall through as in E6. For a carrier outside the admissible set that the device nevertheless *can* render, this specification states no obligation: rendering it and skipping it are both unconstrained. | APS and Publisher: every creative carries a media type inside the admissible set, and non-AV asset URLs travel on the carrier of §5.3.2 (§4.5.5). |
| **E9** | A candidate's **declared** duration would push the cumulative slot duration past the cap. | Keep the slot within the cap whatever the ADS metadata or the candidate count say; keep the surviving candidates in document order (§4.6.4, §4.6.6). | Drop that candidate before playback on declared duration alone. Accepting it instead defers the case to E10. | Publisher: declare `@maxDuration` on every slot (§4.3.2). A slot with no cap declared leaves the Player without the value this row depends on, which is why §4.3.2 makes it mandatory. ADS: not required to respect the cap; a conformance check on it does not fail on cumulative overflow. |
| **E10** | An accepted candidate's **actual** rendered length exceeds its declared duration, or the sequence reaches the cap mid-ad. | Stop rendering at the cap boundary even mid-ad, enforcing against actual and not declared length, and stop firing the remaining beacons at the trim boundary (§4.6.4, §4.6.10). | Surface the trim. | ADS and APS: declared durations that match the creatives reduce trims but are not a conformance condition. Cap arithmetic runs on the presentation timeline; the wall-clock length is derived from it (§4.6.12). |
| **E11** | Rendering an accepted candidate fails at runtime: an ad segment returns 4xx / 5xx, a decode error occurs, the network is lost mid-ad. | Abort that ad and continue playing the primary content uninterrupted (§4.6.2). | Advance to the next candidate in document order, or end the break — Player policy. Retry the ad segment per DASH-IF guidance before aborting. | APS: reference ad media reachable for the duration of the slot. |
| **E12** | An event scheme URI, extension element or namespace in the main MPD or in the resolution document is unknown to the Player. | Ignore the unknown construct together with its whole subtree and keep playing the primary content (§4.6.3). | Log the unknown scheme or namespace. | Publisher and APS: express every new construct through one of the extension points of §4.7, and alter no pre-existing base specification semantics. |
| **E13** | A beacon or a click-tracking request fails: transport error, timeout, non-2xx. | Leave the ad and the primary content unaffected: a beacon failure is non-fatal and never reaches the viewer (§4.6.10). | Retry and log; the retry policy is implementation-defined. | APS: carry beacons on the callback scheme, timed on the ad's presentation timeline (§4.5.6). ADS: owns which beacons exist and when. |
| **E14** | A beacon is scheduled for a moment the ad never reaches: past a trim boundary, or after a pause ad was dismissed on resume. | Stop firing the remaining beacons at the trim boundary, and cease a pause ad's beacons from the pause-to-play transition onward (§4.6.4, §4.6.9). | Report the unfired beacons. | ADS and APS: schedules are relative to the ad's presentation timeline, so a schedule that overruns the slot is trimmed by the Player rather than rejected upstream. |
| **E15** | The resolution document implies two non-linear forms on screen at the same instant, or a pause-ad window opens while an overlay is rendering. | Keep at most one non-linear form active: present sequenced forms one after another in the declared order, and during a pause suspend the overlay and render the pause ad, restoring the overlay on resume only if its window is still open (§4.6.7, §4.6.9). | Report the suspended form. | APS: declare forms as a sequence, never as a concurrent composition. No actor has a construct that inverts the pause-ad-over-overlay priority. Overlapping windows of one family are a declared fallback chain, not a concurrency case. |

#### 8.1.1 What "fall through to primary content" means

No visible artefact — no freeze, no blank slate, no error overlay
unless the application explicitly opted in; no beacon fired for the
opportunity that failed; and primary-content playback continuing on
its own timeline. The viewer cannot tell that an ad opportunity
existed.

Falling through at the **candidate** level is a different move: the
Player advances to the next candidate in document order and reaches
primary content only once every candidate is exhausted.

#### 8.1.2 Order of precedence

When several conditions arise on the same exchange, they apply in this
order:

1. **Transport** — E1, E2. No document, so nothing downstream applies.
2. **Document level** — E3, E4, E5. The document is unusable, late, or
   legitimately empty. E5 is terminal for the opportunity: it
   resolved, so no fallback window is tried.
3. **Constraint surfacing** — E7, E8, E9. Publisher-declared
   constraints validated against each candidate before anything is
   rendered.
4. **Per-candidate, at decode time** — E6, E11. What the device can
   satisfy and what the ad CDN delivers.
5. **Per-candidate, at playback time** — E10, E15. The cap against
   actual length, and the single-active-form bound.
6. **Tracking failures** — E13, E14. Non-fatal throughout.

E12 is orthogonal: an unknown construct is ignored wherever it
appears, at any level, and never advances the Player to the next step.

#### 8.1.3 Surfacing conditions to the application

Everything in the "Player MAY" column that reports, logs or exposes a
condition is non-normative: this specification defines no event name,
no payload and no delivery mechanism, and a Player that exposes
nothing is conformant. The distinction worth exposing first is the
unfilled opportunity (E5) versus the failed resolution (E1, E2, E3),
because that is the pair an operator needs to tell apart and the pair
that looks identical at the playout layer.

One boundary is normative rather than a matter of API shape: an error
overlay is a visible artefact, so a Player that renders one on any row
of this table has broken the fall-through guarantee unless the
application explicitly opted in.

### 8.2 Decision entries that carry tracking and no media

A decision entry with tracking instructions and no creative cannot
become a candidate: there is nothing to render, and a candidate with
no presentation option is not expressible. Whether the APS drops the
entry silently or signals the condition upstream is APS-internal
policy, agreed with the ADS. What the Player sees is the number of
candidates the document carries, and if that number is zero, the
opportunity resolved to no ads (§5.2.3).

### 8.3 Late callbacks

A beacon whose scheduled presentation time has already passed when the
Player reaches it — because the ad started late, because the document
arrived late, or because a trim moved the boundary — is not fired: the
schedule is anchored to the ad's presentation, and a moment the ad
never reached has no beacon to fire. An implementation that fires
late-but-within-the-ad beacons on catch-up rather than dropping them
should do so only inside the ad's rendered window; past the trim
boundary, E14 applies.

### 8.4 Device-class fallbacks

Two device questions recur and this specification decides neither,
because both are properties of the device rather than of the contract.

**Re-tasking the decoder for a video pause ad.** The primary content
is paused, so the decoder holding the paused frame may be available
for an ad video. Whether a given single-decoder device can re-task it,
and what happens to the paused frame while it does, varies by
platform. The conservative implementation skips the video option on a
single-decoder device in this scenario and takes the image or HTML
option instead; an implementation that knows its platform can do
better, and the Player's own capability check is the only gate either
way.

**An overlay on top of a linear ad on a single-decoder device.** In a
hybrid break the linear ad occupies the video surface, so an overlay
composited on top of it requires the device to composite a second
surface over a surface that is itself an ad. Where the device cannot
guarantee that concurrently, the Player presents the linear portion
alone and the overlay portion is declined — which leaves the break
complete and the viewer with a full-screen linear ad.

### 8.5 Resolving a pause-ad slot: speculatively or lazily

A pause-trigger window can be resolved two ways, and both are
conformant:

- **Speculatively**, at the window's Earliest Resolution Time, so the
  document is in hand when the viewer pauses. Lower latency at the
  pause; the decision is older by the time it is used, and it is
  fetched even for the majority of windows in which nobody pauses.
- **Lazily**, at the moment of pause. Fresher targeting and no wasted
  requests; the viewer waits for the round trip before the ad appears.

The trade-off is latency against targeting freshness and request
volume. An implementation that resolves speculatively should treat the
`@maxDuration` and `@allowedLayouts` it validated against as the
values in the manifest at the moment of the pause, not at the moment
of the fetch.

### 8.6 An image form has no intrinsic duration

A video creative carries its own length; an image does not, and an
HTML document does not. For those forms the candidate's declared
`@duration` is the length, and the Player treats the moment the asset
becomes visible as the origin of the ad's presentation timeline
<!-- refine: v7-detail-review.md#flag-9 -->
(§5.5.3). An implementation that renders an image form for as long as
the slot window lasts, ignoring the candidate's declared duration, is
ignoring a value the document does declare.

### 8.7 Degenerate authoring cases

- **A slot whose `@allowedLayouts` names one token and whose
  candidates all offer others.** Every option fails the Publisher
  check, every candidate is skipped, and the opportunity is declined.
  This is a Publisher–ADS mismatch that looks, from the Player, like a
  slot that never fills.
- **A slot whose `@maxDuration` is shorter than the shortest
  candidate.** The Player may drop every candidate before play, or
  accept the first and trim it almost immediately. Both are
  conformant; the second shows the viewer a fragment of an ad.
- **An overlay window and a pause-trigger window declared at the same
  position with the same `@uri`.** They are different families, so the
  chain rule of §4.6.8 does not apply: both are live, and the priority
  rule of §4.6.9 governs what the viewer sees during a pause.
- **A resolution document whose candidate declares a duration longer
  than the slot window.** Drop-before-play applies, and the Player
  advances to the next candidate.

### 8.8 Validators and analytics pipelines

Two placements in this specification are conformant but novel against
the base specification's canonical shapes, and tooling that assumes
the canonical shapes misses them:

- A callback `<EventStream>` carried directly inside
  `<svta:Candidate>` rather than under a `<Period>` (§5.5.2).
- A core-namespace `<ImportedMPD>` carried inside the
  foreign-namespace `<svta:RenderableAsset>` (§5.3.4).

A validator implementing this specification scans inside the SGAI
elements as well as the canonical DASH locations. A schema authored
for the SGAI namespace declares the core-namespace `<ImportedMPD>` as
an admissible child of `<svta:RenderableAsset>`.

## Annex A — Pre-roll (linear)

*Informative.*

### A.1 Scenario

The viewer starts playback of an on-demand title. The Publisher has
declared an ad opportunity at the very beginning of the session,
before the primary content begins: a linear slot, non-linear forms not
allowed, capped at 20 seconds. One linear ad is presented; when it
completes, the primary content starts from its first frame.

Because the content is on-demand, the Publisher uses
`<InsertPresentation>`: the ad does not consume any of the primary
timeline, and after it the main timeline resumes from where it was
held. The slot's `@uri` resolves to the APS; the Player issues the
resolution request at an instant between the Earliest Resolution Time
and the event's `presentationTime`, and receives a `ListMPD` carrying
one Period.

### A.2 Main MPD

<!-- refine: v7-dash-conformance-audit.md#NC2 -->
<!-- refine: v7-dash-conformance-audit.md#NC3 -->
```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">

  <Period id="1" start="PT0S">

    <!-- Linear pre-roll: insert, capped at 20 s -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="101" presentationTime="0" duration="20000">
        <InsertPresentation uri="https://aps.example.com/decision/preroll"
                            earliestResolutionTimeOffset="0"
                            maxDuration="20000"/>
      </Event>
      <!-- Query parameters the Publisher wants on the resolution request -->
      <RequestParam includeInRequests="altmpd"
                    queryTemplate="session_id=$urn:mpeg:dash:state:cmcd#sid$"/>
    </EventStream>

    <!-- Primary content -->
    <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="video/init.mp4"
                       media="video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
      <Representation id="v2" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>

  </Period>

  <!-- Enables the urlparam:2025 scheme; the descriptor carries no content -->
  <EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025"/>
</MPD>
```

The Earliest Resolution Time is `presentationTime` minus
`@earliestResolutionTimeOffset`, which is `0 − 0 = 0`: the Player
resolves at session start, which is the only option for a pre-roll.

### A.3 Resolution request

```
GET https://aps.example.com/decision/preroll?session_id=a1b2c3d4
```

This Player declares no capability parameters — the slot is
linear-only, so no option depends on an overlay surface (§5.8.2).

### A.4 Resolution document (`ListMPD`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-09-15T16:00:00Z">

  <BaseURL>https://adcdn.example.com/delivery/</BaseURL>

  <Period id="ad_01" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="0">creative_101.mpd</ImportedMPD>
  </Period>

</MPD>
```

The ad is 15 seconds against a 20-second cap, so nothing is trimmed.
`Period@duration` is declared at the `ListMPD` level so the Player can
do the slot arithmetic before fetching the sub-MPD.

### A.5 Sub-MPD

<!-- refine: v7-dash-conformance-audit.md#M7 -->
<!-- refine: v7-dash-conformance-audit.md#NC1 -->
```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S"
     publishTime="2026-09-15T16:00:00Z">

  <Period id="1" duration="PT15S">

    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=101</Event>
      <Event presentationTime="0"     id="2">https://tracker.example.com/start?ad=101</Event>
      <Event presentationTime="3750"  id="3">https://tracker.example.com/firstQuartile?ad=101</Event>
      <Event presentationTime="7500"  id="4">https://tracker.example.com/midpoint?ad=101</Event>
      <Event presentationTime="11250" id="5">https://tracker.example.com/thirdQuartile?ad=101</Event>
      <Event presentationTime="15000" id="6">https://tracker.example.com/complete?ad=101</Event>
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

### A.6 Per-device-class behaviour

| Class | Player decision | What the viewer sees |
|---|---|---|
| D1 | Reads the linear-only slot rules, plays the ad on one decoder, enforces the cap at playback. The second decoder and the overlay surfaces are not exercised. | The session starts with a full-screen ad, then the title's first frame. |
| D2 | Same as D1. The absence of non-video overlay capability changes nothing on a linear-only slot. | Same as D1. |
| D3 | Plays the ad on the single decoder, then reuses the same decoder for the primary content. A linear ad and the primary content are sequential, so one decoder is enough. | Same as D1. |
| D4 | Same as D3. | Same as D3. |
| D5 | Same as D3. Linear ads need no overlay capability and no second decoder. | Same as D3. |

The behaviour is uniform, which is the point of the annex: a linear
slot is the one case where device class does not change the outcome.

## Annex B — Mid-roll (linear)

*Informative.*

### B.1 Scenario

The viewer is watching live content when the playhead reaches a
Publisher-declared mid-content slot at six minutes. The slot replaces
a 30-second span of the primary timeline; when the ads complete,
primary content resumes at the position `@returnOffset` determines,
because main media time kept advancing while the ads played.

The Publisher uses `<ReplacePresentation>` because the content is
live: there is no meaningful frame zero of the primary stream to
preserve, and the insert event is not admissible on a `dynamic` MPD.
`@earliestResolutionTimeOffset` is one minute, so the Player may
resolve any time in the minute before the break.

### B.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     type="dynamic"
     availabilityStartTime="2026-09-15T15:00:00Z"
     publishTime="2026-09-15T15:55:00Z"
     minimumUpdatePeriod="PT2S"
     timeShiftBufferDepth="PT1H"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:isoff-live:2011">

  <Period id="1" start="PT0S">

    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
                 timescale="1000">
      <Event id="102" presentationTime="360000" duration="30000">
        <ReplacePresentation uri="https://aps.example.com/decision/midroll"
                             earliestResolutionTimeOffset="60000"
                             maxDuration="30000"
                             returnOffset="0"
                             clip="true"
                             startWithOffset="false"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4d401f"
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

The Earliest Resolution Time is `360000 − 60000 = 300000` ms — five
minutes in. The Player picks an instant between that and the event's
`presentationTime` and issues the request then.

`@clip="true"` means an execution that starts late is trimmed so the
alternative presentation does not run past `@maxDuration`.
`@startWithOffset="false"` means a delayed ad starts from its first
frame rather than skipping into its own timeline.

### B.3 Resolution document (`ListMPD`, two-ad pod)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-09-15T15:56:12Z">

  <BaseURL>https://adcdn.example.com/delivery/</BaseURL>

  <Period id="ad_01" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="0">creative_201.mpd</ImportedMPD>
  </Period>

  <Period id="ad_02" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="15">creative_202.mpd</ImportedMPD>
  </Period>

</MPD>
```

The two ads total 30 seconds against a 30-second cap. The second
`<ImportedMPD>` declares a 15-second pre-fetch offset so the Player
can fetch the second sub-MPD while the first ad plays.

### B.4 Sub-MPD

Identical in shape to Annex A.5, with its own creative and its own
beacon URLs. The tracking `<EventStream>` sits inside the sub-MPD's
`<Period>`, one per ad, and its times are relative to that ad's own
first frame — so the second ad's `complete` beacon is at
`presentationTime="15000"` within its own sub-MPD, not at 30000.

### B.5 Per-device-class behaviour

| Class | Player decision | What the viewer sees |
|---|---|---|
| D1 | Transitions from primary to ad and back. May pre-buffer ad 1 on the second decoder while the primary finishes its last frames. | Playback transitions to two full-screen ads, then back to the live content near the slot position. | <!-- refine: v7-detail-review.md#flag-10 -->
| D2 | Same as D1, including the pre-buffer. Slot rules are device-agnostic; the Publisher declares nothing different for D2. | Same as D1. No overlay is involved. |
| D3 | Plays the ads on the single decoder, sequentially with the primary content: primary stops, ads play, primary resumes. No pre-buffering. | Same as D1. |
| D4 | Same as D3. | Same as D3. |
| D5 | Same as D3. | Same as D3. |

**Trick-play variant.** If the viewer is watching at 2× when the slot
triggers, the ads render at 2× as well, so the pod occupies 15 seconds
of wall clock instead of 30. The cap and the beacon schedule are on
the presentation timeline, so neither changes: the `complete` beacon
of ad 1 still fires at presentation time 15000 within its own
timeline, and the cap still allows 30000 units of presentation time.

## Annex C — Coexisting overlay (multi-form, multi-layout)

*Informative.*

### C.1 Scenario

The viewer is watching an on-demand title. The Publisher has declared
an ad opportunity that runs **on top of** the primary content without
interrupting it: the primary keeps playing, an overlay is composited
over it for a bounded window, and then it disappears.

This is the central non-linear scenario, and the one where device
heterogeneity matters most. The Publisher declares one
device-agnostic set of allowed layouts. The ADS returns **one
candidate carrying four presentation options** — the multi-form,
multi-layout case this annex exists to show — and the APS transcribes
them in order. Each device class walks the same four options and
renders the first it can satisfy, so a single decision resolves
correctly on hardware the ADS and the APS know nothing about.

The slot window is 20 seconds and the cap is 10 seconds: the
opportunity is open for 20 seconds of primary content, and whatever
form is chosen is removed after 10 seconds of rendered length.

### C.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">

  <Period id="1" start="PT0S">

    <!-- Non-linear overlay opportunity: window 120 s .. 140 s, cap 10 s -->
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="301" presentationTime="120000" duration="20000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/overlay?slot=301"
            earliestResolutionTimeOffset="10000"
            maxDuration="10000"
            allowedLayouts="squeezeback-double-box-with-background squeezeback-l-shape overlay-corner linear"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4d401f"
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

A legacy Player meets an `<EventStream>` whose scheme it does not
implement, skips it with every `<Event>` inside, and plays the title
from beginning to end. Nothing it needs was nested inside the SGAI
element: the primary `<AdaptationSet>` is a sibling.

### C.3 Resolution request

```
GET https://aps.example.com/decision/overlay?slot=301
```

This Player declares no capability parameters, so the APS narrows
nothing (§5.8.4) and emits every option the ADS returned. Annex M
shows the same ad with the Player declaring.

### C.4 Resolution document

<!-- refine: v7-detail-review.md#flag-1 -->
<!-- refine: v7-dash-conformance-audit.md#NC1 -->
```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-15T16:02:00Z">

  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>

      <svta:Candidate id="cand-301-a" duration="PT10S">

        <!-- option 1: side-by-side, video ad, advertiser background -->
        <svta:RenderableAsset form="video"
                              layout="squeezeback-double-box-with-background">
          <svta:BackgroundElement assetUrl="https://adcdn.example.com/301/bg.png"/>
          <ImportedMPD earliestResolutionTimeOffset="5">https://adcdn.example.com/301/video.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <!-- option 2: L-shape, image full-frame creative -->
        <svta:RenderableAsset form="image"
                              layout="squeezeback-l-shape"
                              assetUrl="https://adcdn.example.com/301/lshape.png"/>

        <!-- option 3: corner overlay, HTML creative -->
        <svta:RenderableAsset form="html"
                              layout="overlay-corner"
                              assetUrl="https://adcdn.example.com/301/corner.html"/>

        <!-- option 4: full-screen takeover, video -->
        <svta:RenderableAsset form="video" layout="linear">
          <ImportedMPD earliestResolutionTimeOffset="5">https://adcdn.example.com/301/takeover.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=301</Event>
          <Event presentationTime="5000"  id="2">https://tracker.example.com/midpoint?ad=301</Event>
          <Event presentationTime="10000" id="3">https://tracker.example.com/complete?ad=301</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://advertiser.example.com/301">
          <svta:ClickTracking>https://tracker.example.com/click?ad=301</svta:ClickTracking>
        </svta:Click>

        <svta:AdSystem value="example-ads"/>
        <svta:AdTitle value="Autumn campaign, 10s"/>
      </svta:Candidate>

    </svta:OverlayList>
  </Period>
</MPD>
```

Three things in this document are worth pointing at:

- The enclosing `<Period>` declares `duration="PT0S"`. It presents
  nothing itself — it is the anchor the candidate list hangs from —
  and the zero duration is what makes a Period with no
  `<AdaptationSet>` conformant (§5.2.2.1).
- The image and HTML creatives carry their URLs on `@assetUrl`, on the
  option element. They cannot ride on a `<Representation>`: the media
  axis is closed to non-MP4 media types along the whole resolution
  path (§4.7.2).
- The tracking `<EventStream>` sits directly inside the candidate
  rather than inside a sub-MPD, because three of the four options have
  no sub-MPD to host it. Its times are relative to the moment the
  chosen form becomes visible, whichever form that turns out to be.

### C.5 Video sub-MPD for option 1

<!-- refine: v7-dash-conformance-audit.md#M7 -->
```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S"
     publishTime="2026-09-15T16:02:00Z">
  <Period id="1" duration="PT10S">
    <AdaptationSet mimeType="video/mp4" codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <Representation id="v1" bandwidth="1800000" width="960" height="540">
        <BaseURL>https://adcdn.example.com/301/video_960.mp4</BaseURL>
        <SegmentBase indexRange="0-780"/>
      </Representation>
    </AdaptationSet>
  </Period>
</MPD>
```

The representation is 960×540 rather than full-frame because the ad
occupies one box of a side-by-side composition. The sub-MPD is bound
to the Single-Period Static profile by the `<ImportedMPD>` that
reaches it, so every `@mimeType` in it comes from the RFC 4337
registry.

### C.6 Per-device-class behaviour

The Player walks the four options in document order and stops at the
first that satisfies both the device budget (§5.3.7.3) and the slot's
`@allowedLayouts`.

| Class | Option 1 — side-by-side, video ad, image background | Option 2 — L-shape, image creative | Option 3 — corner overlay, HTML | Option 4 — takeover, video | Renders |
|---|---|---|---|---|---|
| D1 | 2 decoders + image surface: **satisfiable** | — | — | — | **Option 1** |
| D2 | Two decoders available, but the background is an image element D2 cannot composite: fails | Needs an image surface: fails | Needs an HTML surface: fails | One decoder, reused sequentially: **satisfiable** | **Option 4** |
| D3 | Needs 2 decoders: fails | 1 decoder + image surface: **satisfiable** | — | — | **Option 2** |
| D4 | Needs 2 decoders: fails | 1 decoder + image surface: **satisfiable** | — | — | **Option 2** |
| D5 | Fails on both counts | No image surface: fails | No HTML surface: fails | One decoder, reused sequentially: **satisfiable** | **Option 4** |

What the viewer sees:

- **D1** — the primary content shrinks into one box, the ad video
  plays in the other, and the advertiser's background image fills the
  bands around them.
- **D2** — a full-screen video ad of bounded duration replaces the
  primary content, which resumes when it ends. This is the instructive
  row: D2 owns the two decoders the side-by-side video needs and still
  lands on the takeover, because every earlier option needs a
  non-video surface it cannot composite.
- **D3, D4** — the primary content shrinks into one region composited
  on top of the image creative that fills the whole frame; the band of
  the creative visible around it forms the "L".
- **D5** — the same outcome as D2, reached for a different reason: D5
  has no overlay capability at all, where D2 has it for video only.

Five classes, three different layouts, from one ordered list emitted
identically to every viewer and one device-agnostic allowed-layout
set. No actor upstream of the Player declared a per-class layout.

### C.7 Sequenced forms in one slot

The same slot could be filled by a sequence instead of a single form.
A 30-second overlay window whose document declares three candidates of
10 seconds each is presented as the first, then the second, then the
third, each starting when the previous ends, with the cap applied to
their cumulative length. At no instant are two of them on screen
together.

## Annex D — Hybrid: a linear ad with a concurrent overlay

*Informative.*

### D.1 Scenario

The Publisher has declared a mid-content break whose ad experience is
hybrid: a linear ad takes over the screen **and** a non-linear overlay
is composited on top of it during the same break. The two portions
belong to the same break and are selected independently — the ADS does
not cross-reference one against the other, and this specification
defines no construct that links them.

The Publisher restricts the overlay portion to a lower-third layout:
an L-shape on top of a linear ad would fight the ad's own composition,
and the Publisher declares that by listing only the tokens it wants.
The break is capped at 30 seconds and the overlay at 10.

### D.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">

  <Period id="1" start="PT0S">

    <!-- take-over portion -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="401" presentationTime="600000" duration="30000">
        <InsertPresentation uri="https://aps.example.com/decision/hybrid-linear"
                            earliestResolutionTimeOffset="30000"
                            maxDuration="30000"/>
      </Event>
    </EventStream>

    <!-- overlay portion, same presentationTime -->
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="402" presentationTime="600000" duration="10000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/hybrid-overlay"
            earliestResolutionTimeOffset="30000"
            maxDuration="10000"
            allowedLayouts="overlay-lower-third"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4d401f"
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

Two events at the same `presentationTime`, in two different
`<EventStream>`s, with two different `@uri` values. They are different
**families**, so the same-family chain rule does not apply: neither is
a fallback for the other, and both are live.

### D.3 Resolution documents

The linear portion resolves to a `ListMPD` exactly as in Annex A.4,
carrying one 30-second ad.

The overlay portion resolves to an Overlay Resolution Document
carrying one candidate with two options — a video lower-third and an
image lower-third:

<!-- refine: v7-detail-review.md#flag-1 -->
<!-- refine: v7-dash-conformance-audit.md#NC1 -->
```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-15T16:09:30Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-402" duration="PT10S">
        <svta:RenderableAsset form="video" layout="overlay-lower-third">
          <ImportedMPD>https://adcdn.example.com/402/strip.mpd</ImportedMPD>
        </svta:RenderableAsset>
        <svta:RenderableAsset form="image"
                              layout="overlay-lower-third"
                              assetUrl="https://adcdn.example.com/402/strip.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=402</Event>
          <Event presentationTime="10000" id="2">https://tracker.example.com/complete?ad=402</Event>
        </EventStream>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

### D.4 Player behaviour

The Player resolves the two `@uri` values separately, validates the
linear candidates against the linear slot's constraints and the
overlay candidates against the overlay slot's, and selects one from
each. It then plays the linear ad while compositing the chosen overlay
on top of it.

The overlay's budget is evaluated against what the device can do
**while the linear ad occupies the video surface**. That is the whole
difference between this annex and Annex C: in Annex C the surface
underneath is the primary content, here it is another ad, and either
way it is a video the device is decoding.

### D.5 Per-device-class behaviour

| Class | Linear portion | Overlay portion | What the viewer sees |
|---|---|---|---|
| D1 | Plays on one decoder | Video lower-third on the second decoder, or the image form on an image surface — the video option comes first and is satisfiable, so it wins | A full-screen linear ad with a lower-third strip composited on top of it |
| D2 | Plays on one decoder | Video lower-third on the second decoder: video-on-video is exactly what D2 does | Same as D1 |
| D3 | Plays on the single decoder | The video option needs a second decoder and fails. The image option would need a surface composited over the linear ad's video, which this device cannot guarantee concurrently, so the overlay portion is declined (§8.4) | A full-screen linear ad, no overlay on top |
| D4 | Plays on the single decoder | Same as D3 | Same as D3 |
| D5 | Plays on the single decoder | No overlay capability of any kind: declined | Same as D3 |

In every row the linear portion plays and the break completes. The
overlay is additive: when it cannot be composited, the viewer sees the
break they would have seen without it.

## Annex E — Pause-triggered ad

*Informative.*

### E.1 Scenario

The Publisher has declared a window during which, if the viewer
pauses, a pause ad is permitted: from ten minutes to twenty minutes
into the content. A pause outside that window permits nothing.

While the window is active and the viewer is paused, the pause ad is
presented over the paused primary frame — fullscreen or as a partial
overlay, depending on the option selected. When the viewer resumes,
the ad is dismissed within one rendering frame and the primary content
continues from the paused position.

### E.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">

  <Period id="1" start="PT0S">

    <!-- pause-trigger window: 600 s .. 1200 s, ad capped at 30 s -->
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-pause-trigger:2026"
                 timescale="1000">
      <Event id="501" presentationTime="600000" duration="600000">
        <svta:PauseAdPresentation
            uri="https://aps.example.com/decision/pause?slot=501"
            earliestResolutionTimeOffset="30000"
            maxDuration="30000"
            allowedLayouts="pause-ad"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4d401f"
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

The event declares the **window of validity** on the timeline. The
trigger is not on the timeline: it is the viewer's pause, which the
Player detects. That split is what the construct exists for — a DASH
event is dispatched when the playhead reaches its presentation time,
and a pause is precisely the moment the playhead stops moving.

### E.3 Resolution document

<!-- refine: v7-detail-review.md#flag-1 -->
<!-- refine: v7-dash-conformance-audit.md#NC1 -->
```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-15T16:11:00Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-501" duration="PT30S">

        <!-- option 1: HTML pause card, fullscreen -->
        <svta:RenderableAsset form="html"
                              layout="pause-ad"
                              assetUrl="https://adcdn.example.com/501/card.html"/>

        <!-- option 2: image pause card -->
        <svta:RenderableAsset form="image"
                              layout="pause-ad"
                              assetUrl="https://adcdn.example.com/501/card.png"/>

        <!-- option 3: video pause ad -->
        <svta:RenderableAsset form="video" layout="pause-ad">
          <ImportedMPD>https://adcdn.example.com/501/pause.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=501</Event>
          <Event presentationTime="15000" id="2">https://tracker.example.com/midpoint?ad=501</Event>
          <Event presentationTime="30000" id="3">https://tracker.example.com/complete?ad=501</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://advertiser.example.com/501"/>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

The `<svta:Click>` carries no `<svta:ClickTracking>` child: this
advertiser declared a destination and no click tracker, which is a
complete declaration (§5.6.1).

### E.4 Per-device-class behaviour

| Class | Player decision | What the viewer sees |
|---|---|---|
| D1 | Walks the options: the HTML card is satisfiable on an HTML surface over the paused frame. Renders option 1. | A rich pause card over the paused frame, dismissed on resume. |
| D2 | Options 1 and 2 need non-video surfaces D2 lacks: both fail. Option 3 is video, and the second decoder is free while the primary holds the paused frame: satisfiable. | A video pause ad over the paused frame, dismissed on resume. |
| D3 | Option 1 is satisfiable on an HTML surface. Renders option 1. | Same as D1. |
| D4 | Option 1 needs HTML, which D4 lacks: fails. Option 2 is an image over the paused frame: satisfiable. | A static image over the paused frame, dismissed on resume. |
| D5 | No overlay capability of any kind. Every option fails and the candidate is skipped; no further candidate exists, so the Player declines the opportunity. | Nothing. The paused frame stays on screen until the viewer resumes. |

On D3 and D4 the video option was never reached. Had it been — had the
device offered no image or HTML surface — the Player would have had to
decide whether it can re-task the decoder holding the paused frame.
The conservative behaviour is to skip the video option on a
single-decoder device in this scenario (§8.4).

### E.5 The live variant: the presentation-time freeze

If the content is live and the viewer pauses inside the window, the
Player's presentation time **freezes** inside the window while the
live edge keeps advancing in wall-clock time. The window is anchored
to the frozen presentation time, so the pause ad stays admissible for
as long as the viewer remains paused. On resume the ad is dismissed;
if the Player then jumps to the live edge, that jump is a Player
action after the resume, outside the window.

The freeze has a ceiling. When the pause lasts long enough that the
resumption time falls before the start of the time-shift buffer, the
base specification requires the playhead to be trimmed to the oldest
available segment, and a seek back to live is trimmed to the live
edge. At that boundary the Player dismisses the pause ad and ceases
its remaining beacons, exactly as on a resume. A Publisher who wants a
longer pause-ad window on live content sets
`MPD@timeShiftBufferDepth` accordingly (§4.6.9).

## Annex F — Multi-ad break

*Informative.*

### F.1 Scenario

A mid-content slot filled by several ads played back-to-back with no
primary content between them. The Publisher declares the break and its
cap; how many ads run inside is the ADS's decision, made against its
own competitive-separation, frequency-capping and ordering logic.

This annex exists for the cap arithmetic, which is where a multi-ad
break differs from a single-ad one.

### F.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">

  <Period id="1" start="PT0S">

    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="601" presentationTime="900000" duration="60000">
        <InsertPresentation uri="https://aps.example.com/decision/pod"
                            earliestResolutionTimeOffset="60000"
                            maxDuration="60000"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4d401f"
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

### F.3 Resolution document (`ListMPD`, three ads over the cap)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-09-15T16:14:00Z">

  <BaseURL>https://adcdn.example.com/delivery/</BaseURL>

  <Period id="ad_01" duration="PT30S">
    <ImportedMPD earliestResolutionTimeOffset="0">creative_601.mpd</ImportedMPD>
  </Period>
  <Period id="ad_02" duration="PT20S">
    <ImportedMPD earliestResolutionTimeOffset="30">creative_602.mpd</ImportedMPD>
  </Period>
  <Period id="ad_03" duration="PT30S">
    <ImportedMPD earliestResolutionTimeOffset="50">creative_603.mpd</ImportedMPD>
  </Period>

</MPD>
```

The ADS returned 80 seconds of ads against a 60-second cap. It was not
required to respect the cap, and a conformance check on it does not
fail because of this.

### F.4 Cap arithmetic

The Player has two admissible readings, and both are conformant:

**Drop before play.** Walking the Periods in order, the cumulative
declared duration is 30, then 50, then 80. The third ad would push the
<!-- refine: v7-detail-review.md#flag-10 -->
total past 60, so the Player may drop it before playback and present
ads 1 and 2 for 50 seconds of the 60-second break. The order of the
survivors is unchanged: no re-ordering, no deduplication, no promotion
of a shorter later ad into the gap.

<!-- refine: v7-detail-review.md#flag-10 -->
**Trim during play.** The Player may instead accept the third ad and
enforce the cap against actual rendered length, stopping at 60 seconds
— ten seconds into ad 3. The remaining beacons of ad 3 are not fired,
because the ad never reached the moments they were scheduled for.

Trim during play is what the Player **must** do whichever reading it
took, because the declared durations are a prediction and the rendered
lengths are the fact: an ad declared at 30 seconds that renders 32 is
trimmed at the cap regardless of the arithmetic done beforehand.

### F.5 Per-device-class behaviour

| Class | Player decision | What the viewer sees |
|---|---|---|
| D1 | Plays each ad in order, switching the decoder source between them. May pre-buffer ad N+1 on the second decoder. | A break of consecutive ads, then the primary content. | <!-- refine: v7-detail-review.md#flag-10 -->
| D2 | Same as D1, including the pre-buffer. | Same as D1. |
| D3 | Same logic, single decoder reused sequentially across the ads and the primary content. No pre-buffering. | Same as D1. |
| D4 | Same as D3. | Same as D3. |
| D5 | Same as D3. | Same as D3. |

## Annex G — A Player that predates this specification

*Informative.*

### G.1 Scenario

A Player implementation that predates this specification receives a
manifest that uses the new constructs — a non-linear opportunity
declared through an event scheme it has never seen. It has no
awareness of the semantics. This is the cross-cutting scenario that
any of the other annexes degrades to when the viewer's Player is old.

### G.2 What the Player does

It meets the `<EventStream>` first, finds a `@schemeIdUri` it does not
implement, and skips the event stream together with every `<Event>`
inside it. The foreign-namespace child element inside each event is
discarded with the whole subtree — a DASH client that does not
implement a foreign namespace removes the entire node, and does not
descend into it looking for known children.

It never recognises an opportunity, so it never issues a resolution
request. The APS is never called, the ADS is never consulted, and no
beacon fires. It logs nothing above the informational level and
renders no artefact.

The remaining document is exactly the baseline MPD: the primary
content's `<Period>` and its `<AdaptationSet>`s, plus whatever
standard break the Publisher authored as the legacy fallback. It
parses and plays.

### G.3 What the viewer sees, and why it is the Publisher's choice

The Player's behaviour is always skip-and-continue. What the viewer
experiences around the skipped construct depends on what the Publisher
authored, and that is content-dependent:

- **Live content.** The opportunity falls through and the ad is an
  expected loss on that Player. Live content cannot be held to splice
  in a standard break without losing real content, so letting the
  legacy Player keep playing the live edge is the only safe outcome.
  The viewer sees uninterrupted primary content and no error.
- **VOD content.** The Publisher may author a standard linear break
  <!-- refine: v7-detail-review.md#flag-10 -->
  alongside the SGAI construct, using only baseline constructs a
  legacy Player already renders. The legacy Player skips the construct
  it does not understand and plays the break it does, so the
  opportunity is monetised instead of lost. A current Player
  recognises the SGAI construct and takes that path; the standard
  break is the legacy fallback only.

The Publisher cannot detect a viewer's Player version from the
manifest, which is why the VOD fallback is authored unconditionally.
Because VOD is not bound to a live edge, inserting a standard break
costs no real content.

### G.4 A VOD manifest carrying both paths

```xml
<Period xmlns:svta="urn:svta:dash:sgai:2026"
        id="1" start="PT0S">

  <!-- SGAI path: a current Player resolves this -->
  <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
               timescale="1000">
    <Event id="701" presentationTime="300000" duration="20000">
      <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay?slot=701"
                                earliestResolutionTimeOffset="10000"
                                maxDuration="10000"
                                allowedLayouts="overlay-lower-third"/>
    </Event>
  </EventStream>

  <!-- legacy fallback: a legacy Player plays this standard break -->
  <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
               timescale="1000">
    <Event id="702" presentationTime="300000" duration="15000">
      <InsertPresentation uri="https://aps.example.com/decision/legacy-break"
                          earliestResolutionTimeOffset="10000"
                          maxDuration="15000"/>
    </Event>
  </EventStream>

  <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4d401f"
                 segmentAlignment="true" startWithSAP="1">
    <SegmentTemplate timescale="1000" duration="2000"
                     initialization="video/init.mp4"
                     media="video/seg_$Number$.m4s"
                     startNumber="1"/>
    <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
  </AdaptationSet>

</Period>
```

A Player implementing this specification recognises both schemes and
resolves the overlay; whether it also plays the legacy break is a
Publisher-authoring matter expressed through the two events' windows.
A legacy Player recognises only the second and plays the standard
break.

### G.5 The outcome does not vary by device class

Behaviour is uniform across D1 to D5 because the graceful-degradation
outcome depends on the Player's version and on the content type, not
on the device's hardware. A device with rich rendering capability
running a legacy Player produces exactly the outcome of a worst-case
device running one.

## Annex H — An overlay window crossing a pause-ad window

*Informative.*

### H.1 Scenario

An overlay is on screen when the viewer pauses, and the pause falls
inside a Publisher-declared pause-ad window. Two opportunities of two
different families are live at the same instant, and the composition
rule decides what the viewer sees: the pause ad takes priority, the
overlay is suspended, and on resume the pause ad is dismissed and the
overlay returns if its own window is still open.

### H.2 Main MPD

```xml
<Period xmlns:svta="urn:svta:dash:sgai:2026"
        id="1" start="PT0S">

  <!-- overlay window: 300 s .. 330 s -->
  <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
               timescale="1000">
    <Event id="801" presentationTime="300000" duration="30000">
      <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay?slot=801"
                                earliestResolutionTimeOffset="10000"
                                maxDuration="30000"
                                allowedLayouts="overlay-lower-third overlay-corner"/>
    </Event>
  </EventStream>

  <!-- pause-ad window: 240 s .. 420 s, overlapping the overlay window -->
  <EventStream schemeIdUri="urn:svta:dash:event:sgai-pause-trigger:2026"
               timescale="1000">
    <Event id="802" presentationTime="240000" duration="180000">
      <svta:PauseAdPresentation uri="https://aps.example.com/decision/pause?slot=802"
                                earliestResolutionTimeOffset="30000"
                                maxDuration="60000"
                                allowedLayouts="pause-ad"/>
    </Event>
  </EventStream>

  <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4d401f"
                 segmentAlignment="true" startWithSAP="1">
    <SegmentTemplate timescale="1000" duration="2000"
                     initialization="video/init.mp4"
                     media="video/seg_$Number$.m4s"
                     startNumber="1"/>
    <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
  </AdaptationSet>

</Period>
```

The two windows overlap, but they belong to **different families**, so
they are not a fallback chain: both are live, and the priority rule
governs.

### H.3 Timeline

| Presentation time | Event | Player |
|---|---|---|
| 290 000 | ERT of the overlay window | Resolves the overlay slot, receives its candidates |
| 300 000 | Overlay window opens | Selects an option and renders the overlay |
| 308 000 | Viewer pauses, inside the pause-ad window | Suspends the overlay, resolves the pause-ad slot (or uses a document fetched speculatively), renders the pause ad over the paused frame. The overlay's window clock stops with the presentation time. |
| — | Viewer stays paused for 40 s of wall clock | Presentation time does not advance. The overlay's 30-second window has consumed 8 seconds and holds there. |
| 308 000 | Viewer resumes | Dismisses the pause ad within one rendering frame, ceases its remaining beacons, and restores the overlay — its window is still open, with 22 seconds left |
| 330 000 | Overlay window expires | Removes the overlay |

The overlay's window follows the **primary timeline**, so it froze
during the pause: the viewer does not lose overlay time to the pause,
and the overlay terminates when its declared window expires rather
than because of the pause.

Had the viewer paused at 328 000 and stayed paused past the overlay's
remaining 2 seconds, the overlay's window would still be measured on
the frozen presentation time, so it would still have those 2 seconds
left on resume. The overlay's window expires only when presentation
time reaches its end, and presentation time does not move while
paused.

### H.4 Per-device-class behaviour

| Class | During play | On pause | On resume |
|---|---|---|---|
| D1 | Overlay renders (HTML or video, whichever option wins) | Overlay suspended; pause ad rendered over the paused frame | Pause ad dismissed, overlay restored for the remainder of its window |
| D2 | Overlay renders only if a video option is offered; otherwise the overlay opportunity was declined | If the pause-ad candidate offers a video option, the second decoder composites it; otherwise the pause ad is declined and the paused frame stays clean | Pause ad dismissed if one was rendered; overlay restored if one was rendering |
| D3 | Overlay renders on the HTML or image surface | Overlay suspended; HTML or image pause ad over the paused frame | Pause ad dismissed, overlay restored on the same surface |
| D4 | Overlay renders on the image surface | Overlay suspended; image pause ad over the paused frame | Pause ad dismissed, image overlay restored |
| D5 | Overlay declined — no surface, no second decoder | Pause ad declined for the same reason. With no overlay to suspend and no pause ad to prioritise, the rule is moot | Nothing changes |

The priority holds whether the pause ad is fullscreen or partial. In
the partial case the paused frame stays visible around it, and the
original overlay is still suspended: at no instant are two non-linear
forms composited together.

## Annex I — One ad, ordered options, resolved across the device classes

*Informative.*

### I.1 Scenario

A single non-linear candidate is offered for an overlay slot. It
carries four presentation options as an ordered list; document order
is the preference order. The ADS emits the **same** ordered list to
every viewer, and the Publisher declares **one device-agnostic
allowed-layout set**. There is no per-device-class variant anywhere in
the manifest or in the resolution document.

The per-class outcome is therefore not authored upstream — it
**emerges at the Player**, when each device walks the same four
options and renders the first it can satisfy against its own
capability and the Publisher's allowed layouts. This annex is the
worked example of that emergence, and it answers directly the question
of whether the Publisher ought to declare layouts per device class:
the ordered fallback plus one device-agnostic allowed-layout set
already produces the right layout per class, without the Publisher,
the ADS or the APS holding a device-class matrix.

In this annex the Player discloses nothing about its device. Annex M
is the same ad with the Player declaring its capabilities and the APS
resolving the choice; every class lands on the same rendered result.

### I.2 Main MPD

```xml
<EventStream xmlns:svta="urn:svta:dash:sgai:2026"
             schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
             timescale="1000">
  <Event id="901" presentationTime="480000" duration="20000">
    <svta:OverlayPresentation
        uri="https://aps.example.com/decision/overlay?slot=901"
        earliestResolutionTimeOffset="15000"
        maxDuration="15000"
        allowedLayouts="squeezeback-double-box-with-background squeezeback-l-shape overlay-corner linear"/>
  </Event>
</EventStream>
```

One allowed-layout set, no per-class variant.

### I.3 Resolution document

<!-- refine: v7-detail-review.md#flag-1 -->
<!-- refine: v7-dash-conformance-audit.md#NC1 -->
```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-15T16:20:00Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-901" duration="PT15S">

        <!-- 1. side-by-side / double box: video ad + advertiser background -->
        <svta:RenderableAsset form="video"
                              layout="squeezeback-double-box-with-background">
          <svta:BackgroundElement assetUrl="https://adcdn.example.com/901/bg.jpg"/>
          <ImportedMPD>https://adcdn.example.com/901/box.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <!-- 2. L-shape: image full-frame creative -->
        <svta:RenderableAsset form="image"
                              layout="squeezeback-l-shape"
                              assetUrl="https://adcdn.example.com/901/lshape.jpg"/>

        <!-- 3. image banner in a corner -->
        <svta:RenderableAsset form="image"
                              layout="overlay-corner"
                              assetUrl="https://adcdn.example.com/901/corner.jpg"/>

        <!-- 4. full-screen takeover video -->
        <svta:RenderableAsset form="video" layout="linear">
          <ImportedMPD>https://adcdn.example.com/901/takeover.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=901</Event>
          <Event presentationTime="7500"  id="2">https://tracker.example.com/midpoint?ad=901</Event>
          <Event presentationTime="15000" id="3">https://tracker.example.com/complete?ad=901</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://advertiser.example.com/901">
          <svta:ClickTracking>https://tracker.example.com/click?ad=901</svta:ClickTracking>
        </svta:Click>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

The four options in order, and what each one costs the device:

1. **Side-by-side / double box with a video ad and an advertiser
   background** — three on-screen elements: the shrunk primary
   content, the ad video, and the background image filling the bands
   the two boxes leave uncovered. Two concurrent video decoders plus
   an image surface.
2. **L-shape with an image full-frame creative** — two on-screen
   elements: the image creative occupying the full frame, and the
   shrunk primary content composited on top of it. One decoder plus an
   image surface.
3. **Image banner in a corner** — one decoder for the primary content
   plus an image overlay surface.
4. **Full-screen takeover video** — a linear-style ad played
   sequentially: the primary content stops, the ad plays, the primary
   content resumes. One decoder, reused; no overlay surface and no
   second decoder.

### I.4 The per-class walk

**D1** — Option 1 needs two decoders plus an image surface. D1 has
both, and `squeezeback-double-box-with-background` is in the allowed
set. The **first** option already passes; the Player renders it and
stops walking.

**D2** — Option 1: D2 has the two decoders for the two videos, but the
background is an **image element** and D2 composites no non-video
content. It fails on its third element. Option 2: the full-frame
creative is an image, needing an image surface D2 lacks. Fails.
Option 3: an image surface again. Fails. Option 4: one decoder reused
sequentially, no concurrent composition at all. **Satisfiable.** The
Player renders option 4.

**D3** — Option 1 needs a second decoder D3 does not have. Fails.
Option 2 needs one decoder for the shrunk primary content plus an
image surface for the full-frame creative; D3 has both.
**Satisfiable.** The Player renders option 2.

**D4** — Option 1 fails on the decoder count. Option 2 needs an image
surface, which D4 has. **Satisfiable**, rendered. Had option 2's
full-frame creative been HTML, D4 would have skipped it and fallen to
option 4.

**D5** — Option 1 fails on both counts. Option 2 needs an image
surface D5 lacks. Option 3 likewise. Option 4 needs no concurrent
composition at all. **Satisfiable**, rendered.

### I.5 Outcome

| Class | Option rendered | What the viewer sees |
|---|---|---|
| D1 | 1 — side-by-side | Primary content in one box, ad video in the other, advertiser background filling the bands |
| D2 | 4 — full-screen takeover | A full-screen ad, then the primary content resumes |
| D3 | 2 — L-shape | Primary content shrunk on top of a full-frame image creative; the visible band forms the "L" |
| D4 | 2 — L-shape | Same as D3 |
| D5 | 4 — full-screen takeover | Same as D2, reached for a different reason |

Five classes, three layouts, one authored decision.

Two contrasts are the point of the annex. **D2 is the instructive
row**: it owns the two decoders the side-by-side video needs and still
declines option 1, because the third element — the background, an
image — is a surface it cannot composite. The rule is element
**type**, not element **count**. And **D2 and D5 share an outcome for
different reasons**: D5 has no overlay capability at all where D2 has
it for video only, and the ordered fallback reaches the same last
option along two different paths.

The two layouts are modelled differently and that is what separates
D3 and D4 from D1. The side-by-side here is a **three-element** layout
carrying a **video** ad, needing two decoders plus an image surface —
out of reach for a single-decoder device. The L-shape is a
**two-element** layout carrying an **image** full-frame creative,
needing one decoder plus one image surface — within reach.

## Annex J — Side-by-side / double box, the three-element layout

*Informative.*

### J.1 Scenario

The Publisher has declared an overlay slot whose allowed layouts
include side-by-side / double box. The shrunk primary content sits
next to the ad on a 16:9 screen, and the two boxes together leave
bands uncovered. A third element — a **background element**, a still
<!-- refine: v7-detail-review.md#flag-10 -->
image, never a video and never an HTML surface — may fill the
uncovered region; when the advertiser supplies none, it renders as
black.

This annex is the worked illustration of that layout: three on-screen
elements, and the device-class reasoning that follows from the
element **count** and the element **type**.

### J.2 Main MPD

```xml
<EventStream xmlns:svta="urn:svta:dash:sgai:2026"
             schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
             timescale="1000">
  <Event id="1001" presentationTime="720000" duration="20000">
    <svta:OverlayPresentation
        uri="https://aps.example.com/decision/overlay?slot=1001"
        earliestResolutionTimeOffset="15000"
        maxDuration="15000"
        allowedLayouts="squeezeback-double-box-with-background squeezeback-double-box"/>
  </Event>
</EventStream>
```

The Publisher lists both tokens: with a background element and
without. It supplies no background of its own — the background is the
advertiser's creative.

### J.3 Resolution document, two variants

**With an advertiser background**, and an image ad rather than a video
one:

<!-- refine: v7-detail-review.md#flag-1 -->
<!-- refine: v7-dash-conformance-audit.md#NC1 -->
```xml
<svta:Candidate xmlns:svta="urn:svta:dash:sgai:2026"
                id="cand-1001-a" duration="PT15S">
  <svta:RenderableAsset form="image"
                        layout="squeezeback-double-box-with-background"
                        assetUrl="https://adcdn.example.com/1001/ad.jpg">
    <svta:BackgroundElement assetUrl="https://adcdn.example.com/1001/bg.jpg"/>
  </svta:RenderableAsset>
  <svta:RenderableAsset form="image"
                        layout="squeezeback-double-box"
                        assetUrl="https://adcdn.example.com/1001/ad.jpg"/>
  <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
               value="1" timescale="1000">
    <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=1001</Event>
    <Event presentationTime="15000" id="2">https://tracker.example.com/complete?ad=1001</Event>
  </EventStream>
</svta:Candidate>
```

**Without an advertiser background**, and with a video ad:

<!-- refine: v7-detail-review.md#flag-1 -->
<!-- refine: v7-dash-conformance-audit.md#NC1 -->
```xml
<svta:Candidate xmlns:svta="urn:svta:dash:sgai:2026"
                id="cand-1001-b" duration="PT15S">
  <svta:RenderableAsset form="video" layout="squeezeback-double-box">
    <ImportedMPD>https://adcdn.example.com/1001/ad.mpd</ImportedMPD>
  </svta:RenderableAsset>
  <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
               value="1" timescale="1000">
    <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=1001b</Event>
    <Event presentationTime="15000" id="2">https://tracker.example.com/complete?ad=1001b</Event>
  </EventStream>
</svta:Candidate>
```

The background element is a **child of the option**, not a fourth
option: the Player does not walk it the way it walks the ordered
options; it composites it as part of rendering the layout once that
layout is chosen.

### J.4 Per-device-class behaviour

For the **first candidate** — image ad with an image background:

| Class | Option 1 — double box with background | Option 2 — double box, no background | Renders |
|---|---|---|---|
| D1 | 1 decoder + image surface for the ad + image surface for the background: **satisfiable** | — | Option 1 |
| D2 | Both elements are non-video surfaces D2 cannot composite: fails | Ad is an image surface: fails | Nothing; the candidate is skipped |
| D3 | 1 decoder + two image surfaces: **satisfiable** | — | Option 1 |
| D4 | 1 decoder + two image surfaces: **satisfiable** | — | Option 1 |
| D5 | No non-video surface of any kind: fails | Fails | Nothing; the candidate is skipped |

For the **second candidate** — video ad, no background:

| Class | Double box, video ad | Renders |
|---|---|---|
| D1 | 2 decoders, no non-video surface needed: **satisfiable** | Yes — bands render as black |
| D2 | 2 decoders, no non-video surface needed: **satisfiable** | Yes — this is the case D2 *can* do |
| D3 | Needs a second decoder: fails | Candidate skipped |
| D4 | Needs a second decoder: fails | Candidate skipped |
| D5 | Needs a second decoder: fails | Candidate skipped |

### J.5 What the two tables show

The element **type** matters as much as the count. D2 owns the
decoders a side-by-side video needs, and it renders the second
candidate happily — but it cannot render the first, whose ad and
background are both non-video surfaces. And D3 and D4, which have one
decoder and image surfaces, are the mirror image: they render the
first candidate and not the second.

That is why a candidate carrying the layout in more than one form is
what makes a side-by-side reach a heterogeneous population: neither
form alone covers D1 through D5, and the ordered pair does.

The L-shape is a different layout with its own budget, not a variant
of this one: it puts **two** elements on screen — the full-frame ad
creative and the shrunk primary content on top — with no separate
background element at all, because the creative itself is the
background (§5.3.7.1).

## Annex K — ClickThrough

*Informative.*

### K.1 Scenario

An ad — linear or non-linear — is on screen. Its resolution document
carries the ClickThrough URL together with one or more click-tracking
URLs. The viewer activates the click: a select on a CTV remote, a tap
on a phone. At the moment of activation the Player opens, or hands
off, the ClickThrough destination and fires each click-tracking URL
once.

The Publisher configures nothing beyond permitting the ad: the
ClickThrough travels with the ad, not with the slot.

### K.2 The carrier in a resolution document

<!-- refine: v7-detail-review.md#flag-1 -->
<!-- refine: v7-dash-conformance-audit.md#NC1 -->
```xml
<svta:Candidate xmlns:svta="urn:svta:dash:sgai:2026"
                id="cand-1101" duration="PT15S">
  <svta:RenderableAsset form="image"
                        layout="overlay-lower-third"
                        assetUrl="https://adcdn.example.com/1101/strip.png"/>

  <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
               value="1" timescale="1000">
    <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=1101</Event>
    <Event presentationTime="7500"  id="2">https://tracker.example.com/midpoint?ad=1101</Event>
    <Event presentationTime="15000" id="3">https://tracker.example.com/complete?ad=1101</Event>
  </EventStream>

  <svta:Click clickThroughUrl="https://advertiser.example.com/autumn?utm_source=ctv">
    <svta:ClickTracking>https://tracker.example.com/click?ad=1101</svta:ClickTracking>
    <svta:ClickTracking>https://thirdparty.example.net/c?cid=1101</svta:ClickTracking>
  </svta:Click>
</svta:Candidate>
```

For a linear ad the same `<svta:Click>` element is the carrier, and it
is reached the same way. A linear `ListMPD` Period that needs to carry
a ClickThrough carries the element as foreign-namespace open content
on the Period, which a legacy Player discards with its subtree exactly
as it discards the element inside a candidate.

### K.3 Two kinds of tracking, two carriers

| | Timeline beacons | Click-tracking |
|---|---|---|
| Carrier | Callback `<EventStream>` (§5.5) | `<svta:ClickTracking>` inside `<svta:Click>` (§5.6) |
| Trigger | The playhead reaching a scheduled presentation time | The viewer activating the click |
| Timing | `presentationTime` relative to the ad's own first frame | None — it fires when the viewer acts, or never |
| Fires if the viewer does nothing | Yes | No |

This is not a stylistic split. Every DASH event is evaluated against
the media presentation timeline, and the callback scheme fires its
HTTP GET when the playhead reaches the event's presentation time. A
click has no presentation time, so the callback scheme cannot express
it, and a separate carrier is the only way to make the click work
identically on every conformant Player.

### K.4 Behaviour

On activation the Player opens the ClickThrough destination — in a
system browser, a platform hand-off, or whatever the device's
convention is — and fires **each** `<svta:ClickTracking>` URL once. A
click-tracking request that fails is non-fatal: the ad and the primary
content are unaffected, and the failure never reaches the viewer.

A `<svta:Click>` that carries no `<svta:ClickTracking>` child is a
complete declaration. The Player opens the destination and fires
nothing.

### K.5 Device classes and legacy Players

The outcome depends on the device's input mechanism — remote select,
tap — and not on its decoder or surface budget. D1 through D5 read the
same carrier and fire the click identically.

A Player that predates this specification renders the ad but never
activates the click: it discards the unknown carrier with its parent
subtree, so the click is inert. Nothing else about the ad changes.

## Annex L — Overlapping windows of the same family, with fallback

*Informative.*

### L.1 Scenario

Two overlay windows overlap in time in the main MPD. They are the same
family, so they are not two concurrent opportunities: they are a
**chain**. The Player takes the first window it encounters and
resolves it; the second is a backup, reached only when the first
window's resolution document cannot be accessed.

Resolving to **no ads** is resolving successfully. A `200` carrying a
document with no candidates is an answer, so the second window stays
untouched and the Player continues with the primary content.

### L.2 Main MPD

```xml
<Period xmlns:svta="urn:svta:dash:sgai:2026"
        id="1" start="PT0S">

  <!-- primary window -->
  <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
               timescale="1000">
    <Event id="1201" presentationTime="600000" duration="30000">
      <svta:OverlayPresentation uri="https://aps-a.example.com/decision/overlay?slot=1201"
                                earliestResolutionTimeOffset="20000"
                                maxDuration="15000"
                                allowedLayouts="overlay-lower-third overlay-corner"/>
    </Event>
  </EventStream>

  <!-- fallback window, overlapping -->
  <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
               timescale="1000">
    <Event id="1202" presentationTime="605000" duration="25000">
      <svta:OverlayPresentation uri="https://aps-b.example.com/decision/overlay?slot=1202"
                                earliestResolutionTimeOffset="20000"
                                maxDuration="15000"
                                allowedLayouts="overlay-lower-third overlay-corner"/>
    </Event>
  </EventStream>

  <AdaptationSet id="1" mimeType="video/mp4" codecs="avc1.4d401f"
                 segmentAlignment="true" startWithSAP="1">
    <SegmentTemplate timescale="1000" duration="2000"
                     initialization="video/init.mp4"
                     media="video/seg_$Number$.m4s"
                     startNumber="1"/>
    <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
  </AdaptationSet>

</Period>
```

The two windows point at two different APS endpoints — which is a
common reason to declare a chain at all. No attribute declares the
relationship: the overlap plus the shared family **is** the
declaration.

### L.3 The three paths

**Path 1 — the first window answers with no candidates.**

```
GET https://aps-a.example.com/decision/overlay?slot=1201
→ 200 OK
```

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-15T16:29:40Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList/>
  </Period>
</MPD>
```

The opportunity resolved, and it resolved to no ads. The Player does
not touch window 1202, renders nothing, and continues with the primary
content. An implementation that reports opportunities to the
application reports this one as **unfilled**, which is different from
failed.

**Path 2 — the first window cannot be accessed, the second answers.**

```
GET https://aps-a.example.com/decision/overlay?slot=1201
→ connection timed out
GET https://aps-b.example.com/decision/overlay?slot=1202
→ 200 OK, one candidate
```

The Player resolves the fallback, validates its candidates against
window 1202's own constraints, and renders. The fallback was used as
declared.

**Path 3 — neither window can be accessed.**

```
GET https://aps-a.example.com/decision/overlay?slot=1201
→ 503
GET https://aps-b.example.com/decision/overlay?slot=1202
→ 503
```

The chain is exhausted with no resolution document obtained, so no
candidate was ever accepted. The Player skips the opportunity and
continues with the primary content: an opportunity that cannot be
honoured is skipped, and applying this specification never breaks
primary-content playback.

### L.4 Why overlap is a chain rather than a concurrency case

If two windows of the same family could both be served, the Player
would have to arbitrate between two simultaneously resolvable ad
presentations at runtime, and serving both would mean two concurrent
non-linear presentations — the same pressure on the device's decoder
and surface budget that the one-form-at-a-time rule exists to avoid.
Concurrency of windows is concurrency of presentation.

Reading the overlap as a declared chain removes the arbitration
entirely: the form this specification defines never asks the device to
present more than one ad at a time, and never asks the Player to
resolve a runtime conflict between two equally valid windows. The
overlap stops being two things to play at once and becomes one primary
window plus its backups.

### L.5 Device classes

This is window **selection**, not rendering, so it is device-agnostic.
D1 through D5 select and fall back identically; the device class
affects only how the forms inside the chosen window render, which is
Annex C's subject.

Once a window is served, the forms inside its resolution document are
sequenced by the in-slot rule: this annex selects the window, and
§4.6.7 sequences what is inside it.

## Annex M — One ad, Player-declared capabilities, resolved by the APS

*Informative.*

### M.1 Scenario

The same candidate as Annex I — the same four presentation options,
the same device-agnostic allowed-layout set. What differs is **where
the capability check is resolved**. Here the Player attaches the
capability parameters it chooses to declare to the resolution request,
and the APS resolves against them, emitting a document whose candidate
carries **exactly one** option: the one the APS computed as renderable
on that device. The Player checks that option against its own
capability and the Publisher's allowed layouts, and renders it — or
passes over the candidate if its own check fails.

Annex I shows the same ad with the Player disclosing nothing and the
APS emitting the full list. Neither case is canonical; they exercise
the same rule from the two ends.

### M.2 Main MPD

Identical to Annex I.2. Nothing the Publisher authors changes: the
capability declaration is the Player's decision, taken at runtime,
and no declaration by the Publisher, the APS or the ADS precedes it.

### M.3 D1 — declares everything

```
GET https://aps.example.com/decision/overlay?slot=901
      &sgaiVideoDecoders=2&sgaiImageOverlay=true&sgaiHtmlOverlay=true
```

The APS finds option 1 satisfiable on that declaration and emits it
alone:

<!-- refine: v7-detail-review.md#flag-1 -->
<!-- refine: v7-dash-conformance-audit.md#NC1 -->
```xml
<svta:Candidate xmlns:svta="urn:svta:dash:sgai:2026"
                id="cand-901" duration="PT15S">
  <svta:RenderableAsset form="video"
                        layout="squeezeback-double-box-with-background">
    <svta:BackgroundElement assetUrl="https://adcdn.example.com/901/bg.jpg"/>
    <ImportedMPD>https://adcdn.example.com/901/box.mpd</ImportedMPD>
  </svta:RenderableAsset>
  <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
               value="1" timescale="1000">
    <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=901</Event>
    <Event presentationTime="15000" id="2">https://tracker.example.com/complete?ad=901</Event>
  </EventStream>
</svta:Candidate>
```

The Player checks the option it received, it passes, and the Player
renders it. The viewer sees the primary content in one box, the ad
video in the other, and the advertiser's background filling the bands
— the same rendered result as Annex I on D1.

### M.4 D2 — declares two decoders and no non-video surface

```
GET ...&sgaiVideoDecoders=2&sgaiImageOverlay=false&sgaiHtmlOverlay=false
```

The APS rules out option 1 on its third element — the background is an
image element this device cannot composite — and options 2 and 3 for
the same reason, both needing an image surface. Option 4 survives on a
single decoder reused sequentially, and the APS emits it alone. The
Player checks it and renders it: a full-screen ad, then the primary
content resumes. The same rendered result as Annex I on D2.

### M.5 D3 — declares an axis it knows, and omits one it does not

```
GET ...&sgaiVideoDecoders=1&sgaiImageOverlay=true
```

This Player declares one video decoder and an image surface, and
**omits** the HTML-surface axis, whose value it cannot determine when
it issues the request. It omits the parameter entirely rather than
sending it empty or with a placeholder.

The APS treats the omitted axis as **undetermined**, and this APS
resolves an undetermined axis conservatively: it emits no option that
depends on it. Option 1 needs a second decoder and is ruled out;
option 2 needs one decoder plus one image surface, depends on no
undetermined axis, and survives. The APS emits option 2 alone; the
Player checks it and renders it. The viewer sees the primary content
shrunk on top of the full-frame image creative — the same rendered
result as Annex I on D3.

An APS that resolved an undetermined axis by assuming the most capable
case would have emitted a different option here, and would be equally
conformant. What does not vary is that the Player checks whatever
arrives before rendering it.

### M.6 D4 — declares nothing

```
GET https://aps.example.com/decision/overlay?slot=901
```

Sending a reserved parameter is optional, and a conformant Player may
send none. The APS receives no device information and must still
produce candidates, so it narrows nothing and emits **all four
options** in the ADS's order — which is exactly the document Annex I
describes.

The Player walks them in document order: option 1 needs a second
decoder and fails; option 2 needs one decoder plus one image surface,
which D4 has. The Player renders option 2 and stops walking. The same
rendered result as Annex I on D4.

This row is where the two annexes stop being alternatives. A Player
that declares nothing leaves the APS unable to narrow, and an APS that
cannot narrow emits the full ordered list. Annex I is not a different
design reached by a different route; it is this one, addressed by a
silent Player.

### M.7 D5 — declares one decoder and no surface

```
GET ...&sgaiVideoDecoders=1&sgaiImageOverlay=false&sgaiHtmlOverlay=false
```

The APS rules out options 1, 2 and 3, each needing a surface this
device lacks. Option 4 survives and is emitted alone. The Player
checks it and renders it: a full-screen ad, then the primary content
resumes. The same rendered result as Annex I on D5.

### M.8 Outcome

| Class | Declared | APS emits | Player renders | Same as Annex I? |
|---|---|---|---|---|
| D1 | 2 decoders, image, HTML | Option 1 alone | Option 1 | Yes |
| D2 | 2 decoders, no surfaces | Option 4 alone | Option 4 | Yes |
| D3 | 1 decoder, image; HTML omitted | Option 2 alone | Option 2 | Yes |
| D4 | nothing | All four, in order | Option 2 | Yes |
| D5 | 1 decoder, no surfaces | Option 4 alone | Option 4 | Yes |

Every class lands on the rendered result it lands on in Annex I, from
the same ad, the same four options and the same Publisher declaration.
What moved is where the capability check was resolved: in Annex I the
APS emits every option and each Player selects among them; here each
Player declares and the APS selects. The viewer-visible outcome is
identical, which is what makes these two divisions of one
responsibility rather than two behaviours to choose between.

### M.9 Two things declaring does not change

**It does not delegate the Player's check.** No presentation option
reaches the screen without passing the Player's own capability check,
and that holds for an option the APS computed from the Player's own
declaration. If the device's state changed between the request and the
render, or the APS derived the wrong option, the Player passes over
the candidate. Declaring narrows what arrives; it does not make what
arrives authoritative.

**A single option does not require a declaration.** A candidate may
carry exactly one option whether or not anything was declared: an APS
that wants the choice to sit with it sends one, and the Player renders
it or passes over the candidate. What a declaration changes is the
basis on which the APS chose that option, not what the Player does
with it — and nothing in the document distinguishes the two cases.

## Annex N — Test cases and conformance criteria

*Informative.* This annex lists, per chapter, what an implementer can
test against. It restates the conditions of §8.1 as test identifiers
and adds the positive-behaviour cases the normative chapters imply.

Each test states the **actor under test**, the **setup**, and the
**observable** that decides pass or fail. An observable that cannot
distinguish a passing implementation from a failing one is not a test:
several cases below therefore pair a positive setup with the negative
setup that should produce the opposite result.

### N.1 Error-condition tests

| Test | Condition | Actor | Setup | Pass observable |
|---|---|---|---|---|
| **T-E1** | Transport failure on the resolution request | Player | Point the slot's `@uri` at an unroutable host. Run twice: once with a fallback window declared, once without. | With a fallback declared, the Player resolves the fallback. Without one, the primary content plays uninterrupted with no artefact and no beacon. The two runs differ, which is what proves the fallback path is exercised. |
| **T-E2** | Non-`200` final status | Player | APS returns `503`. | Same as T-E1. A `200` control run renders the ad, distinguishing the failure path from the success path. |
| **T-E3** | `200` with an unusable body | Player | APS returns `200` with truncated XML. | Nothing renders, primary content is uninterrupted, and the parse failure is distinguishable in logs from T-E5. |
| **T-E4** | Document arrives after the window elapsed | Player | APS delays the response past the slot's `presentationTime` plus `@duration`. | The slot is not extended past the cap to play it; primary content is uninterrupted. |
| **T-E5** | Resolved to no ads | Player | APS returns `200` with an empty candidate list (§5.2.3), with a fallback window declared. | Primary content continues **and the fallback window is not requested**. The un-requested fallback is the observable: it is what separates E5 from E1 and E2, which do request it. |
| **T-E6** | No satisfiable option on a candidate | Player | Offer a candidate with one video-overlay option, on a single-decoder device; then a second candidate with an image option. | The first candidate is skipped and the **second renders**. Falling through to primary content instead is a fail: the fall-through is the last resort, not the response to one unusable candidate. |
| **T-E7** | Layout outside the slot's allowed set | Player | Slot allows `overlay-corner`; candidate's first option declares `overlay-lower-third` and its second declares `overlay-corner`. | The second option renders. Rendering the first is a fail. |
| **T-E8** | Creative carrier outside the admissible set | Player | Candidate's first option declares a media type outside §3.3; second option is a valid image. | No form the device cannot render reaches the screen; the second option renders. |
| **T-E9** | Declared duration overflows the cap | Player | Cap 60 s; three candidates declared 30 s, 20 s, 30 s. | Total rendered length is at most 60 s, and the surviving candidates keep document order — ads 1 and 2 in order, never 1 and 3 promoted. |
| **T-E10** | Actual length exceeds declared | Player | Candidate declares 10 s and its media renders 14 s, against a 12 s cap. | Rendering stops at 12 s, and the beacon scheduled at 14 s does not fire. A control run with a 20 s cap fires it, proving the instrument measures the trim and not the beacon plumbing. |
| **T-E11** | Runtime failure of an accepted ad | Player | Ad CDN returns `404` for the second segment of an accepted ad. | The ad aborts and the primary content continues; no freeze, no error overlay. |
| **T-E12** | Unknown construct | Player | Main MPD carries an SGAI `<EventStream>` whose scheme URI has an unknown year suffix. | The event stream is skipped with its whole subtree; primary content is uninterrupted. |
| **T-E13** | Beacon endpoint failure | Player | Tracking endpoint returns `500` for the impression beacon. | The ad plays to completion and the remaining beacons still fire. |
| **T-E14** | Beacon scheduled past a boundary | Player | Pause ad with a beacon at 30 s; the viewer resumes at 12 s. | The 30 s beacon does not fire. A control run in which the viewer stays paused past 30 s fires it. |
| **T-E15** | Two forms implied at one instant | Player | An overlay is rendering when the viewer pauses inside a pause-ad window. | At every sampled instant exactly one non-linear form is on screen; the overlay is suspended during the pause and restored on resume while its window is open. |

### N.2 Positive-behaviour tests

| Test | Subject | Actor | Setup | Pass observable |
|---|---|---|---|---|
| **T-P1** | Linear pre-roll | Player | Annex A's manifest and documents. | The ad plays before the primary content; the primary content starts at its first frame. |
| **T-P2** | Linear mid-roll with replace semantics | Player | Annex B's manifest. | Primary content resumes at the position `@returnOffset` determines, not where it left off. |
| **T-P3** | Ordered options across device classes | Player | Annex I's document, on each of D1..D5. | Each class renders the option Annex I.5 predicts. Running one document across five devices is the test; a single device proves nothing about the walk. |
| **T-P4** | Document order is preference order | Player | Two options both satisfiable on the device, in a given order; then the same two swapped. | The first-listed renders in each run. The swap is what distinguishes "walks in order" from "happens to prefer this form". |
| **T-P5** | Multi-form candidate resolves on a device the ADS knows nothing about | APS, Player | A candidate with four options, emitted identically to every device. | Every device class renders something, or declines with the primary content intact; no class errors. |
| **T-P6** | Cap enforced against actual length | Player | Annex F's arithmetic. | Total rendered length is at most the cap, with a trim mid-ad if required. |
| **T-P7** | Sequenced forms in one slot | Player | A 30 s overlay window whose document carries three 10 s candidates. | The three render one after another, in document order, one at a time. |
| **T-P8** | Pause-ad lifecycle | Player | Annex E's manifest; pause inside the window, then outside it. | Inside: the ad appears and is dismissed within one rendering frame of the resume. Outside: no ad appears. The outside-the-window run is what proves the window is honoured. |
| **T-P9** | Live presentation-time freeze | Player | Live content, pause inside a pause-ad window, resume after a wall-clock interval shorter than `@timeShiftBufferDepth`. | The pause ad stays admissible for the whole pause; on resume it is dismissed. A second run with a pause longer than the buffer shows the dismissal at the buffer boundary. |
| **T-P10** | Pause ad over a coexisting overlay | Player | Annex H's manifest. | The overlay is suspended on pause and restored on resume with its window's remaining time intact. |
| **T-P11** | Hybrid break | Player | Annex D's manifest, on D1 and on D3. | On D1 both portions render; on D3 the linear portion renders alone and the break completes. |
| **T-P12** | ClickThrough | Player | Annex K's candidate. | On activation the destination opens and each click-tracking URL is requested exactly once. With no activation, none is requested — the no-activation run is what proves the click is not on the timeline. |
| **T-P13** | Overlapping windows | Player | Annex L's manifest, run for each of the three paths. | Path 1 leaves the second window un-requested; path 2 requests it; path 3 ends with primary content. The three runs differ, which is the test. |
| **T-P14** | Capability parameters | Player, APS | Annex M's five declarations. | The Player omits an axis it cannot determine rather than sending it empty; the APS answers a request carrying none of them with candidates. |
| **T-P15** | Legacy compatibility, per construct | Player | For each construct in §4.7.3, a manifest containing it, played on a Player that does not implement this specification. | The construct is skipped silently, no FATAL is logged, and observable playback continues — the primary content for live, or the Publisher-authored standard break for VOD. |
| **T-P16** | Non-AV asset carriage | APS | A resolution document carrying one image candidate and one HTML candidate. | Each asset URL arrives on `@assetUrl` on the option element, and no `@mimeType` outside the RFC 4337 registry appears on any path bound by it. |
| **T-P17** | Empty resolution validates | APS | The two documents of §5.2.3. | Both validate against the base specification schema. A control document with a Period of non-zero duration and no `<AdaptationSet>` fails validation, which is what proves the validator is checking the rule the `PT0S` exists to satisfy. |
| **T-P18** | Playback speed | Player | An ad presented while the primary content runs at 2×. | The ad occupies `duration / 2` of wall clock, and the beacons fire at their scheduled presentation times. |

### N.3 Conformance criteria by chapter

| Chapter | What an implementer tests |
|---|---|
| §3 Terms and vocabulary | Every `@layout` and `@allowedLayouts` token an implementation emits or accepts is in §3.2; every `@form` is in §3.3. |
| §4.3 Publisher | Every slot in the manifest carries `@uri`, `@maxDuration` and, on a non-linear slot, `@allowedLayouts`. |
| §4.4 ADS | A decision whose cumulative duration exceeds the cap still passes; no-fill still passes. |
| §4.5 APS | The resolution document validates, its options are an ordered list, its beacons are callback events, and an unfilled opportunity is a `200` with a body and no candidates. |
| §4.6 Player | T-E1..T-E15 and T-P1..T-P18. |
| §4.7 Extension points | T-P15 for every row of the audit table. |
| §5 Syntax | Every attribute block in this chapter has a corresponding authoring test: emit the construct, validate it, and remove it to confirm the remaining document still parses and plays. |
| §6 Interfaces | One request per slot on the Player↔APS interface; beacons body-less and fire-and-forget; every transport over HTTPS. |
| §7 Expected behaviour | The per-scenario tests T-P1..T-P15. | <!-- refine: v7-detail-review.md#flag-7 -->
| §8 Implementation notes | Non-normative; nothing here is a conformance condition. The guidance is testable only as the implementation's own policy. |

### N.4 What a test harness needs

- **A Player that predates this specification**, for T-P15. Without
  one, the backward-compatibility claim is asserted rather than
  measured.
- **Five device profiles**, or a Player whose decoder count and
  surface support can be constrained at runtime, for T-P3 and T-P5. A
  single top-tier device passes every test in this annex and proves
  nothing about the walk.
- **An APS that can be made to fail deliberately** — timeout,
  non-`200`, truncated body, empty candidate list, and a delayed but
  successful response — for T-E1 to T-E5. The five failures must be
  independently triggerable, because the point of those tests is that
  the Player distinguishes them.
  <!-- refine: v7-detail-review.md#flag-8 -->
- **A beacon collector** that records the URL and the wall-clock
  instant of every request, for T-E10, T-E13, T-E14, T-P12 and T-P18.
  Recording only the URL loses the timing, which is half of what the
  tracking tests measure.

## Refinement gaps

The following items from the v7.1 analyses could not be resolved within
a minor refinement (they require requirement-level changes or
architectural decisions). They are carried forward for the next major
build to address.

| # | Source | Issue ID | Summary | Why minor refinement is insufficient |
|---|--------|----------|---------|--------------------------------------|
| 1 | validation | F-1 (G-3) | `@allowedLayouts` is not bound to the slot family, so `pause-ad` passes every check on an overlay slot and `overlay-corner` on a pause-trigger window | Routed to §5.b. The positive form needs a family column in §3.2 and a new Publisher obligation in §4.3.3 — vocabulary design, not wording |
| 2 | validation | F-2 (G-4) | §7.5.4 states the single-decoder hybrid behaviour and §8.4 denies that this specification decides one | Routed to §5.b. Removing the contradiction means choosing which half is right, which changes an obligation's strength. Same defect as D-6 |
| 3 | validation | F-3 (G-8) | A `ListMPD` declaring only the MPEG list profile loses its `<svta:Click>` to the profile-conformance procedure, so R28 is unmet on the linear path | Routed to §5.b. Every remedy mints a linear-family profile URI that §2.1 does not have, or moves the carrier. Same defect as audit M4 |
| 4 | validation | F-4 (A-3) | §5.1.1 marks `@maxDuration` required under this specification and carries the base schema's unbounded default in the same row | Routed to §5.b. Striking the default and downgrading the obligation report differently to a conformance checker |
| 5 | validation | F-5 (EC-2) | Whether the slot cap accrues while a non-linear form is suspended or paused is unstated | Routed to §5.b. Both readings are defensible, and the choice also settles EC-4 |
| 6 | validation | F-6 (EC-3) | A `200` resolution document of the wrong family for the slot matches neither the E3 nor the E5 row | Routed to §5.b. Deciding it without deciding E3's deliberately open case splits two conditions the Player cannot tell apart at the transport layer |
| 7 | validation | F-7 (EC-4) | A pause inside a pause-trigger window while a linear ad occupies the screen is neither forbidden nor authorised | Routed to §5.b. Allowing or forbidding it changes what the viewer sees during a break, and R22's bound does not reach it |
| 8 | validation | F-8 (EC-6) | `<Event>@id` uniqueness is scoped nowhere, so per-candidate numbering restarting at 1 makes §5.5.2 suppress the second candidate's impression beacon | Routed to §5.b. Scoping the `@id` and scoping the de-duplication key are two different fixes, one of them a runtime obligation |
| 9 | validation | F-9 (A-5) | `pause-ad` collapses two IAB placements into one token while the Squeezeback rows split by placement | Routed to §5.b. Splitting the token or stating the asymmetry both presume the vocabulary decision |
| 10 | validation | F-10 (G-7) | `@executeOnce` has no defined meaning on a pause-trigger window | Routed to §5.b. One reading makes the attribute inert, the other caps the window at one ad per session, and they are opposite viewer-visible outcomes |
| 11 | validation | F-11 (EC-7) | Whose `@allowedLayouts` binds the candidates served from a fallback window is stated only in the informative Annex L.3 | Routed to §5.b. Promoting it adds a normative sentence to §4.6.8, and binding the chain to the first window is defensible |
| 12 | validation | F-12 (A-2) | "Overlay" names the document class, the profile URI and `<svta:OverlayList>` as well as one layout token | Routed to §5.b. A rename is a wire-format change; §5.2.2.2's note already removes the reader-facing ambiguity |
| 13 | validation | F-13 (A-4) | Splitting the double box into two tokens makes an advertiser-supplied background Publisher-gated, an outcome R26.2 does not contemplate | Routed to §5.b. Collapsing or keeping the tokens both change what an existing `@allowedLayouts` declaration means |
| 14 | validation | F-14 (A-6) | A still image's declared `@duration` is consumed at the primary content's playback speed, which the document never states | Routed to §5.b. The alternative — wall clock for non-media forms — breaks DP-1.2's single canonical value |
| 15 | validation | D-1 (EC-1) | Several `<svta:Candidate>` in one document are a sequence in §4.6.7 and a set of alternatives in §4.6.6 | Deferred to `context/03-requirements.md` (R14, R7), read-only here. It is the highest-leverage open item: Annex C.7, T-P7 and the E6 / E9 rows all depend on it |
| 16 | validation | D-2 (R1.3) | R1.3 forbids the §4.6.8 narrowing that R20.1 together with R30 require | Deferred to `context/03-requirements.md`. Two requirements cannot both hold; §1 and §4.1 declare the exception, and the requirement has to admit it. Same root as audit NC1 |
| 17 | validation | D-3 (G-5) | R10.3 requires a Positioning Templates section no build has produced, and an `image` form carries no HTML/CSS surface on which a position could be expressed | Deferred to `context/03-requirements.md` (R10.3) and `context/02-actors.md`. An unmet document-level MUST |
| 18 | validation | D-4 (G-1, G-2) | No timebase or rounding rule for comparing the slot cap with a candidate's `xs:duration`, and no Player behaviour when a slot carries no cap | Deferred to `context/03-requirements.md` (R4). Both are new criteria under a requirement ten use cases exercise |
| 19 | validation | D-5 (A-1) | §2.1's scheme and profile URIs carry an `event:` / `profile:` segment the `context/06` pattern does not admit | Deferred to `context/06-naming-and-namespaces.md`. The classifier does real work, so the spec is the correct half and the policy is the half that is behind |
| 20 | validation | D-6 (G-4) | UC-04's "Notes / open questions" hands the spec the single-decoder hybrid question, and the spec answers it twice, oppositely | Deferred to `context/04-use-cases.md`. Deciding it upstream is what makes R3.2 checkable for the hybrid opportunity type |
| 21 | detail-review | flag-1 | The DR-N labels in §4.7.3 reach 3 of the 11 SGAI-construct rows, and the table carries six of the eight columns `context/07` prescribes | Completing the labels needs a DR-N class for the two opportunity-declaration `<EventStream>` rows, which DR-6 — "the three carriers admissible for a non-AV asset" — does not cover. Widening DR-6 is a definition change |
| 22 | detail-review | flag-4 | §5.1.4.1 describes `@maxDuration` as one pause ad's display time while §5.1.3.1 describes the slot's cumulative rendered length | The missing base-specification anchor was added; aligning the quantity itself decides F-5 and F-10 in passing, and those are §5.b items a minor refinement must not touch |
| 23 | audit | NC1 | §4.6.8 narrows a §5.16.2.2.6 execution-failure condition on the inherited linear schemes, so two Players reading the same scheme URI behave differently | Scoping the narrowing to the SGAI schemes forces a different encoding for the linear no-fill; the alternative drops a document-level conformance claim. Same root as D-2 |
| 24 | audit | M1 | A callback `<EventStream>` directly inside `<svta:Candidate>` cannot be schema-validated there and sits outside the scheme's Period scope | The durable remedy is a `urn:svta:`-namespace carrier mirroring the callback shape — a new construct |
| 25 | audit | M2 | `<ImportedMPD>` inside `<svta:RenderableAsset>` reuses the syntax but not the §5.3.2.6.3 merge model, and has no global element declaration to bind to | The remedy replaces it with an SGAI-namespace element or an attribute — a new construct |
| 26 | audit | M3 | Table I.4 binds `altmpd` to §5.16 requests, so the Publisher's query template does not travel on a non-linear resolution request | The remedy mints a request-type URI and registers it in §2.1 — a new URI and a new registry entry |
| 27 | audit | M4 | A `ListMPD` declaring only the MPEG list profile has its `<svta:Click>` removed by the §8.1 profile-conformance procedure of the base specification | Requires the linear-family profile URI of F-3, which §2.1 does not mint; it publishes a profile URI for the non-linear document only |

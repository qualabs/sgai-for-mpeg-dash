# SGAI for Linear and Non-Linear Ads in MPEG-DASH

**Specification edition**: 2026-05-14
**Status**: Working draft (SVTA Ads WG incubation)
**Authoring venue**: Streaming Video Technology Alliance — Advertisement WG

[GROUNDED_BY=notebooklm]

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**,
**SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**,
and **OPTIONAL** in this document are to be interpreted as described
in IETF RFC 2119, when, and only when, they appear in all capitals.

---

## 1. Scope

This specification defines Server-Guided Ad Insertion (SGAI) for both
**linear** and **non-linear** ads in MPEG-DASH. It extends MPEG-DASH
6th edition (ISO/IEC 23009-1:2025) as a complete SGAI profile:

- **Linear SGAI** — pre-roll, mid-roll, multi-ad break, and other
  screen-take-over ad opportunities — is absorbed as the baseline.
  This specification adopts the MPEG-DASH 6th edition constructs
  `InsertPresentation`, `ReplacePresentation`, and the ListMPD
  profile verbatim, adds clarifications where the baseline leaves
  the Player-side behaviour under-specified (slot validation
  algorithm, drop-before-play semantics, error fall-through), and
  pins the message-flow contract among the three actors defined in
  chapter 4.
- **Non-linear SGAI** — overlays, pause-triggered ads, hybrid
  break-plus-overlay, and the related coexisting-content
  experiences — is introduced as the principal new content of this
  specification. Non-linear ads are signalled by new event schemes
  layered on top of MPEG-DASH 6th edition's `EventStream` mechanism,
  resolved through an overlay-aware extension of the ListMPD shape,
  and rendered by the Player according to the device-aware
  selection algorithm defined in chapter 7.

The specification is **client-side**. Server-side ad insertion
(SSAI) and server-side stitching pipelines are out of scope. The
specification is also **VAST-version-agnostic**: any reference to
VAST in this document is illustrative, confined to non-normative
notes and annexes, and does not impose a precondition on conforming
implementations.

The specification covers the contract between three actors —
Broadcaster, Ad Decision Server (ADS), Player — defined normatively
in chapter 4. It does not specify the internal logic of any actor
beyond that contract: targeting, frequency capping, brand safety,
inventory management, ABR ladder selection, decoder management,
DRM, and authentication are explicitly out of scope.

The specification covers all device classes from top-tier CTV
hardware (multiple decoders, image and HTML overlay surfaces) down
to worst-case hardware (single decoder, no overlay capability). The
device classes themselves are defined in §3.4 and the corresponding
Player obligations in §7.

---

## 2. Normative references

The following documents are referenced normatively. For dated
references, only the edition cited applies. For undated
references, the latest edition of the referenced document
(including any amendments) applies.

| Reference | Title | Edition / version |
|-----------|-------|-------------------|
| ISO/IEC 23009-1:2025 | Information technology — Dynamic adaptive streaming over HTTP (DASH) — Part 1: Media presentation description and segment formats | 6th edition (FDIS) |
| IETF RFC 2119 | Key words for use in RFCs to Indicate Requirement Levels | March 1997 |
| IETF RFC 8174 | Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words | May 2017 |
| IETF RFC 4337 | MIME Type Registrations for MPEG-4 | March 2006 |
| IAB Tech Lab | Ad Format Guidelines for Digital Video and CTV (live document) | May 2026 release |
| W3C HTML 5.x | HyperText Markup Language Living Standard | latest |
| W3C CSS | Cascading Style Sheets, levels 1–4 | latest |

The following URIs are introduced normatively by this edition of
the specification (§3.3, §5):

| URI | Role |
|-----|------|
| `urn:svta:dash:sgai:2026` | XML namespace for elements and attributes introduced by this specification. |
| `urn:svta:dash:sgai-overlay:2026` | `EventStream@schemeIdUri` for non-linear overlay opportunities (§5.1.3). |
| `urn:svta:dash:sgai-pause-trigger:2026` | `EventStream@schemeIdUri` for pause-triggered ad opportunities (§5.1.4). |
| `urn:svta:dash:sgai-layout:2026` | Scheme prefix for the IAB-derived layout vocabulary (§3.2). |
| `urn:svta:dash:profile:sgai-overlay-list:2026` | `MPD@profiles` value advertising conformance to the overlay-aware resolution document defined in §5.2.2. |

The following URIs are inherited from MPEG-DASH 6th edition and
referenced verbatim throughout this specification:

| URI | Role | Source |
|-----|------|--------|
| `urn:mpeg:dash:event:alternativeMPD:insert:2025` | `EventStream@schemeIdUri` for `<InsertPresentation>` (§5.1.1). | ISO/IEC 23009-1, §5.16.3 |
| `urn:mpeg:dash:event:alternativeMPD:replace:2025` | `EventStream@schemeIdUri` for `<ReplacePresentation>` (§5.1.2). | ISO/IEC 23009-1, §5.16.4 |
| `urn:mpeg:dash:event:callback:2015` | `EventStream@schemeIdUri` for tracking callback events (§5.5). | ISO/IEC 23009-1, §4.7 / §5.10.4.5 |
| `urn:mpeg:dash:profile:list:2024` | `MPD@profiles` value advertising ListMPD conformance. | ISO/IEC 23009-1, §8.14 |
| `urn:mpeg:dash:profile:sps:2024` | `MPD@profiles` value advertising Single-Period Static conformance. | ISO/IEC 23009-1, §8.15 |
| `urn:mpeg:dash:schema:mpd:2011` | XML namespace for the DASH MPD schema. | ISO/IEC 23009-1 |
| `urn:mpeg:dash:schema:urlparam:2025` | XML namespace for the §I.4 UrlParam descriptor. | ISO/IEC 23009-1, §I.4 |

---

## 3. Terms, definitions, abbreviations

For the purposes of this document, the following terms,
definitions, and abbreviations apply. Terms defined in
ISO/IEC 23009-1:2025 are inherited verbatim and are not redefined
here.

### 3.1 Core terms

- **SGAI (Server-Guided Ad Insertion)** — A client-side ad
  insertion pattern in which the ad decision is performed by an
  Ad Decision Server. The MPD declares ad opportunities, the
  Player resolves each opportunity against the ADS at the time
  the opportunity activates, and the Player composes the ad on
  screen subject to the constraints declared by the Broadcaster.
- **Broadcaster** — The actor that owns the primary content and
  the viewer's screen. Declares ad opportunities and their
  constraints in the MPD.
- **Ad Decision Server (ADS)** — The actor that returns one or
  more ad candidates eligible for a given ad opportunity. Owns
  targeting, frequency capping, ordering, and other internal
  decisioning logic. Not normatively required to enforce
  Broadcaster-declared constraints (see §4 actor obligations).
- **Player** — The actor that fetches the MPD, resolves ad
  opportunities against the ADS, validates ADS responses against
  the Broadcaster's constraints, selects among admissible
  candidates and forms, and renders the chosen result on screen.
- **Primary content** — The content the Broadcaster wishes to
  show outside ad opportunities.
- **Ad opportunity / slot** — A point or interval in the
  Broadcaster's timeline at which an ad MAY be rendered.
  Linear slots replace or splice primary content for their
  duration; non-linear slots coexist with primary content.
- **Linear ad** — An ad that replaces or splices the primary
  content for the duration of the slot.
- **Non-linear ad** — An ad that is composited on top of, or
  alongside, the primary content without interrupting it.
- **Renderable form** — One concrete rendering of an ad
  candidate (video, image, HTML). A candidate MAY carry multiple
  forms; the Player selects one form per device.
- **Layout** — The on-screen placement template of a non-linear
  ad (e.g. corner overlay, lower third, L-shape squeezeback,
  pause card). Layouts are defined by the IAB; this
  specification references them by name (§3.2).
- **Resolution document** — The XML document returned by the
  ADS in response to the Player's resolution request. Carries one
  or more ad candidates. Inherits the ListMPD shape (§8.14) for
  the linear baseline; extended with the overlay-aware profile
  defined in §5.2.2 for non-linear opportunities.
- **Sub-MPD** — An MPD reached via `<ImportedMPD>` from a parent
  resolution document. SPS-conformant by construction (§8.15).
- **Candidate** — One ad offered by the ADS for a given slot.
  Materialised as either a `<Period>` plus `<ImportedMPD>` pair
  (linear baseline) or a `<Period>` carrying one
  `<svta:RenderableAsset>` set (non-linear / multi-form, §5.2.2).
- **Earliest Resolution Time (ERT)** — The earliest moment at
  which the Player MAY issue the resolution request for an ad
  opportunity. Computed as `presentationTime − @earliestResolutionTimeOffset`
  (ISO/IEC 23009-1 §5.16; reused for non-linear slots, §5.1.3 / §5.1.4).
- **Fall through** — The Player behaviour when an ad opportunity
  cannot be fulfilled: continue playing the primary content
  uninterrupted, fire no tracking beacon for the failed slot,
  surface no visible artefact (no freeze, no blank slate, no
  error overlay) unless the embedding application has opted in
  via an implementation-defined surface.

### 3.2 Layout vocabulary (IAB-defined)

The accepted layout values used by this specification are sourced
from the IAB Tech Lab document *Ad Format Guidelines for Digital
Video and CTV* (live document, May 2026 release). This
specification references those values; it does not introduce new
layout names. Broadcasters and Ad Decision Servers MUST use the
IAB-defined names exactly as enumerated below.

The spec-side identifier is a kebab-cased token derived from the
IAB canonical name. When used as a scheme URI fragment or as a
value in `<svta:AllowedLayouts>` or `<svta:RenderableAsset @layout>`,
the token MUST appear as shown in the **Identifier** column.

| Identifier | IAB name | Class | Notes |
|------------|----------|-------|-------|
| `linear` | Linear Ad | Linear | Baseline in-stream ad slot; rendered via the linear baseline path (`<InsertPresentation>` / `<ReplacePresentation>` / ListMPD). |
| `pause-ad` | Pause Ad | Non-linear, viewer-initiated | Triggered by viewer pause inside a Broadcaster-declared window (§5.1.4). |
| `menu-ad` | Menu Ad | Non-linear, UI-embedded | Placement inside the smart-TV or streaming app UI. Sub-placements `menu-headline-banner`, `menu-in-tile` MAY refine the top-level identifier. |
| `squeezeback` | Squeezeback | Non-linear, content-adjacent | Primary content is resized to free area for the ad. Sub-placements `squeezeback-l-shape`, `squeezeback-frame`, `squeezeback-double-box`, `squeezeback-double-box-with-background` MAY refine the top-level identifier. |
| `overlay` | Overlay | Non-linear, over-content | Composited on top of primary content; primary is not resized. Sub-placements `overlay-corner`, `overlay-lower-third` MAY refine the top-level identifier. |
| `in-scene` | In Scene Ads | Non-linear, in-content composite | Branded element composited into the programming. Non-interactive by definition; tracking-only. |
| `screen-saver-ad` | Screen Saver Ad | Non-linear, device-initiated | OS- or app-initiated overlay after a defined inactivity period. Distinct from `pause-ad`: the trigger actor is the device, not the viewer. |
| `companion-ad` | Companion Ad | Companion | Display-only wrap-around accompanying a master ad. Per IAB, not generally available on CTV except as end card. |

NOTE — The list above mirrors the IAB document at the date of this
edition (May 2026 release). Implementations are expected to consult
the live IAB document for any updates between editions.

The spec MUST NOT define new top-level identifiers in this column.
Sub-placement refinements (e.g. `overlay-corner`) MAY be enumerated
inside an `<svta:AllowedLayouts>` element when a Broadcaster needs
to constrain the rendering surface further than the top-level
identifier allows.

### 3.3 Abbreviations

| Abbreviation | Expansion |
|--------------|-----------|
| ADS | Ad Decision Server |
| CTV | Connected Television |
| CSS | Cascading Style Sheets |
| DASH | Dynamic Adaptive Streaming over HTTP |
| ERT | Earliest Resolution Time |
| FDIS | Final Draft International Standard |
| HTML | HyperText Markup Language |
| IAB | Interactive Advertising Bureau |
| MPD | Media Presentation Description |
| RFC | Request for Comments (IETF) |
| SGAI | Server-Guided Ad Insertion |
| SPS | Single-Period Static (DASH profile) |
| SVTA | Streaming Video Technology Alliance |
| URN | Uniform Resource Name |
| VAST | Video Ad Serving Template (IAB) |
| XML | eXtensible Markup Language |

### 3.4 Device classes

Device classes capture the on-screen rendering capabilities
relevant to ad rendering. They do not address codec support,
network conditions, or DRM, which are orthogonal and out of scope.

| Class | Decoders | Image-on-video | HTML-on-video | Typical hardware |
|-------|----------|----------------|---------------|------------------|
| **D1** | 2 or more | yes | yes | Top-tier CTV, web. |
| **D2** | 2 | no | no (video-on-video composition only) | Mid-tier CTV with dual decoders, no overlay surface. |
| **D3** | 1 | yes | yes | Single-decoder CTV with overlay surfaces; many web Players. |
| **D4** | 1 | yes | no | Constrained CTV with image overlay only. |
| **D5** | 1 | no | no | Worst-case: single decoder, no overlay surface at all. |

The Player MUST be able to assert its device class deterministically
at run time. The taxonomy is defined for the purpose of the
expected-behaviour matrix in chapter 7; conforming Players on
classes between the named tiers MAY implement the more conservative
of the two adjacent tiers.

---

## 4. Conformance

### 4.1 Three-actor contract

This specification is anchored on a three-actor model. Conformance
obligations are stated per actor below. A claim of conformance
identifies the actor whose obligations the implementation satisfies.

The model is normative: the Broadcaster declares what can be
shown; the ADS provides what is available to show; the Player
decides and renders, validating each candidate against what the
Broadcaster declared. The ADS is NOT bound by the Broadcaster's
declared constraints — the Player is the sole enforcer.

This separation is a load-bearing property of the specification.
Mechanisms that require an actor to assume responsibilities outside
its role are non-conformant and MUST be rejected during spec
evolution.

### 4.2 Broadcaster obligations

A conformant Broadcaster:

- **B-1**. MUST declare every ad slot (linear or non-linear) as a
  `<Period>`-level `<EventStream>` carrying an event of one of
  the schemes enumerated in chapter 2: §5.16 linear schemes
  (`urn:mpeg:dash:event:alternativeMPD:insert:2025`,
  `urn:mpeg:dash:event:alternativeMPD:replace:2025`),
  `urn:svta:dash:sgai-overlay:2026`, or
  `urn:svta:dash:sgai-pause-trigger:2026`.
- **B-2**. MUST declare a maximum duration on every ad slot via
  `@maxDuration`, in `EventStream@timescale` units, on the event
  child element (§5.1).
- **B-3**. MUST declare slot-level constraints applicable to the
  Player's validation algorithm (§7.3): for non-linear slots,
  `<svta:AllowedLayouts>` (§5.1.3.1) is REQUIRED; for non-linear
  slots, `<svta:Concurrency @max="…">` (§5.1.3.2) is REQUIRED.
- **B-4**. MUST express any new construct via the
  ignore-if-unknown extension points enumerated in §5.6
  (foreign-namespace open content, application-level event
  streams, vendor descriptor schemes). MUST NOT introduce new
  constructs via paths that violate the SPS / RFC 4337 chain
  (§5.6.5).
- **B-5**. MUST NOT alter or override the semantics of any
  pre-existing MPEG-DASH 6th edition construct. Reusing a
  baseline name with new semantics is non-conformant.
- **B-6**. MUST use layout names that map 1:1 to the
  IAB-defined values of §3.2; broadcaster-private layout names
  are non-conformant.

### 4.3 ADS obligations

A conformant ADS:

- **A-1**. MUST return a resolution document conforming to one of
  the profiles defined in §5.2: the linear baseline
  (`urn:mpeg:dash:profile:list:2024`, §8.14) or the overlay-aware
  profile (`urn:svta:dash:profile:sgai-overlay-list:2026`,
  §5.2.2).
- **A-2**. MUST populate each candidate with at least one
  renderable form (video, image, or HTML, §5.3). The ADS MAY
  populate multiple forms and MAY rank them via ADS hints
  (§5.3.4).
- **A-3**. MUST embed in-band tracking beacons under
  `urn:mpeg:dash:event:callback:2015` (§5.5). MUST NOT introduce
  alternative tracking schemes.
- **A-4**. MUST emit form metadata only for layout names
  enumerated in §3.2.
- **A-5**. MUST NOT be required to enforce the Broadcaster's
  slot constraints (max duration, allowed layouts, concurrency
  cap). A conformance test on the ADS MUST NOT fail solely
  because returned candidates would violate one of those
  constraints. (Enforcement is the Player's responsibility,
  §4.4 / §7.3.)
- **A-6**. MUST NOT be required to maintain a device-class
  matrix or per-Player capability view; the Player resolves
  device capability locally.
- **A-7**. SHOULD honour the slot's resolution window: when the
  ADS cannot meet the deadline, the ADS SHOULD return early with
  an empty resolution document rather than late with content.
  (See §7.4 error E4.)

### 4.4 Player obligations

A conformant Player:

- **P-1**. MUST parse the main MPD and recognise the SGAI event
  schemes enumerated in chapter 2 that the implementation
  declares support for. Schemes the implementation does not
  declare support for MUST be ignored as unknown event schemes
  (§5.16 ignore-if-unknown rule of `EventStream`).
- **P-2**. MUST resolve every supported event by issuing a
  resolution request to the URL on the event's child element
  (`@url`) at any instant between the Earliest Resolution Time
  and the event's `presentationTime`, augmented with the
  parameters declared by the `UrlParamInfo` descriptor in the
  main MPD (§I.4).
- **P-3**. MUST validate every ADS-returned candidate against
  the Broadcaster-declared slot constraints (max duration,
  allowed layouts, concurrency cap) according to the algorithm
  defined in §7.3. Candidates that fail validation MUST NOT be
  rendered.
- **P-4**. MUST honour the ADS-declared candidate order in the
  resolution document, except for candidates dropped under
  P-7 (no renderable form) or P-8 (drop-before-play). MUST NOT
  re-order, deduplicate, or otherwise rearrange the remaining
  candidates (§7.3).
- **P-5**. MUST enforce the Broadcaster-declared `@maxDuration`
  cap against the actual rendered length of each accepted
  candidate. When cumulative rendered length would exceed the
  cap, the Player MUST stop rendering at the cap boundary, even
  if the stop falls mid-ad ("trim during play"). The Player
  MUST NOT extend a slot beyond the cap regardless of ADS
  metadata or candidate count.
- **P-6**. MUST select, among the renderable forms of an
  accepted candidate, the highest-priority form that satisfies
  the intersection (device capabilities × Broadcaster-allowed
  layouts × ADS priority hints) per the algorithm in §7.3.
- **P-7**. MUST skip any candidate that carries no
  form-and-layout combination renderable on its device,
  preserving the declared order of the remaining candidates
  (§7.3).
- **P-8**. MAY drop a candidate before fetching its sub-MPD
  when its declared duration would push cumulative slot
  duration past the cap ("drop before play"). MUST NOT use
  drop-before-play as an excuse to re-order candidates.
- **P-9**. MUST fire tracking beacons embedded under the
  callback scheme (§5.5) at the times indicated by their
  `presentationTime` values, interpreted per §7.5. MUST stop
  firing beacons at the trim boundary established by P-5.
- **P-10**. MUST fall through to primary content uninterrupted
  on every error condition enumerated in §8.1 (E1–E12), firing
  no tracking beacon for the failed slot.
- **P-11**. MUST safely ignore foreign-namespace elements and
  attributes it does not implement, treating their absence as
  the default behaviour (§5.6.5). MUST NOT abort the candidate
  or the slot on an unknown extension.
- **P-12**. MUST NOT depend on VAST for any normative
  obligation. Player implementations against ADSs that do not
  use VAST MUST be conforming with no adapter layer.

### 4.5 Cross-edition compatibility

A Player implementing edition N+1 of this specification SHOULD
recognise both the `:N:` and `:N+1:` versions of the URIs
declared in chapter 2, applying the backward-compatibility rules
established in edition N+1 to any document that references the
older URIs. The default behaviour, when no edition-specific rule
applies, is to apply the semantics of the older edition for an
old URI and the semantics of the newer edition for a new URI.

A Player that predates an edition (a "legacy Player" with respect
to this spec) MUST treat the new URIs as unknown event schemes
or unknown namespaces under the standard MPEG-DASH 6th edition
ignore-if-unknown rules. The expected behaviour in that case is
the fall-through-to-primary-content outcome described as P-10.

---

## 5. Syntax

This chapter defines the on-the-wire syntax of every construct
introduced by this specification and the inherited shape of every
baseline construct cited normatively. Examples are illustrative
and short; complete walk-throughs live in the annexes.

### 5.1 Main MPD events

The main MPD declares ad opportunities as `<Event>` elements inside
`<EventStream>` containers, scoped to a `<Period>`. The Player
recognises the opportunity by the `@schemeIdUri` of the
`<EventStream>`. The semantics of each event are carried by a
child element of the `<Event>` whose tag identifies the opportunity
kind.

Four event kinds are defined:

- §5.1.1 — `<InsertPresentation>` (linear, splice insertion).
  Inherited from MPEG-DASH 6th edition.
- §5.1.2 — `<ReplacePresentation>` (linear, replace insertion).
  Inherited from MPEG-DASH 6th edition.
- §5.1.3 — `<svta:OverlayPresentation>` (non-linear, coexisting
  overlay). NEW.
- §5.1.4 — `<svta:PauseAdTrigger>` (non-linear,
  viewer-initiated overlay on pause). NEW.

#### 5.1.1 `<InsertPresentation>` (linear, inherited)

Scheme URI: `urn:mpeg:dash:event:alternativeMPD:insert:2025`.

Inherited from ISO/IEC 23009-1 §5.16.3. The Player suspends the
primary timeline at the event's `presentationTime`, plays the
resolved alternative presentation, and resumes the primary
timeline at the position where it paused.

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@url` | yes | xs:anyURI | — | The ADS endpoint to resolve when the event activates. |
| `@maxDuration` | yes | xs:unsignedInt | — | Maximum cumulative duration of the inserted ad presentation, in `EventStream@timescale` units. The Player enforces this cap (§7.3, P-5). |
| `@earliestResolutionTimeOffset` | yes | xs:unsignedInt | — | Offset, in seconds, by which the Player MAY pre-fetch the resolution document ahead of the event's `presentationTime`. Defines the Earliest Resolution Time. |

#### 5.1.2 `<ReplacePresentation>` (linear, inherited)

Scheme URI: `urn:mpeg:dash:event:alternativeMPD:replace:2025`.

Inherited from ISO/IEC 23009-1 §5.16.4. The Player switches the
on-screen presentation to the resolved alternative presentation at
the event's `presentationTime`; the primary timeline's media time
advances under the alternative. On completion of the alternative,
the Player resumes at the position determined by `@returnOffset`.

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@url` | yes | xs:anyURI | — | The ADS endpoint to resolve when the event activates. |
| `@maxDuration` | yes | xs:unsignedInt | — | Maximum cumulative duration of the alternative presentation, in `EventStream@timescale` units. The Player enforces the cap (§7.3, P-5). |
| `@earliestResolutionTimeOffset` | yes | xs:unsignedInt | — | Offset, in seconds, by which the Player MAY pre-fetch the resolution document ahead of the event's `presentationTime`. Defines the Earliest Resolution Time. |
| `@returnOffset` | yes | xs:unsignedInt | — | Offset, in `EventStream@timescale` units, at which the Player resumes the primary timeline after the alternative completes. |
| `@clipDuration` | yes | xs:unsignedInt | — | The intended duration of the alternative presentation, in `EventStream@timescale` units. Constrains the Player's trim behaviour when the event executes late. |
| `@startWithOffset` | yes | xs:boolean | — | If `true`, a delayed alternative starts from the offset corresponding to the elapsed wall-clock time rather than from its first frame. |

#### 5.1.3 `<svta:OverlayPresentation>` (non-linear, NEW)

Scheme URI: `urn:svta:dash:sgai-overlay:2026`.

`<svta:OverlayPresentation>` signals that an ad MAY be composited
on top of the primary content during the interval
`[presentationTime, presentationTime + duration)` of the event,
where `duration` is the event's `@duration` (inherited from
`<Event>`). The primary content keeps playing throughout. The
Player resolves the event against the ADS as described in §6.

`<svta:OverlayPresentation>` lives in the
`urn:svta:dash:sgai:2026` XML namespace. Per §5.6.1, foreign-
namespace open content (§5.2.1 of ISO/IEC 23009-1) is the
extension point that legalises its placement under `<Event>` —
and legacy Players that do not implement the namespace discard
the element and its subtree without raising an error.

##### Attributes

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@url` | yes | xs:anyURI | — | The ADS endpoint to resolve when the event activates. |
| `@maxDuration` | yes | xs:unsignedInt | — | Maximum display duration of the overlay, in `EventStream@timescale` units. The Player enforces this cap (§7.3, P-5). Same semantics as `@maxDuration` on `<InsertPresentation>` / `<ReplacePresentation>`. |
| `@earliestResolutionTimeOffset` | yes | xs:unsignedInt | — | Offset, in seconds, by which the Player MAY pre-fetch the resolution document ahead of the event's `presentationTime`. Same units as the baseline §5.16 attribute. |

NOTE — The attribute names `@url`, `@maxDuration`, and
`@earliestResolutionTimeOffset` are reused verbatim from the
baseline §5.16 events because the semantics match exactly
(ADS endpoint, slot cap, ERT in seconds). Reuse keeps the
implementer's mental model uniform across linear and non-linear
opportunities.

##### Children

| Element | Required | Cardinality | Description |
|---------|----------|-------------|-------------|
| `<svta:AllowedLayouts>` | yes | 1 | Enumerates the layout names permitted on this slot (§5.1.3.1). |
| `<svta:Concurrency>` | yes | 1 | Bounds the number of concurrent overlays during the slot (§5.1.3.2). |
| `<svta:Exclusions>` | no | 0..1 | OPTIONAL mutually-exclusive layout pairings (§5.1.3.3). |

##### 5.1.3.1 `<svta:AllowedLayouts>`

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| (none) | — | — | — | All semantics carried by `<svta:Layout>` children. |

| Child element | Required | Cardinality | Description |
|---------------|----------|-------------|-------------|
| `<svta:Layout>` | yes | 1..N | One layout permitted on this slot. |

`<svta:Layout>` attributes:

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@name` | yes | xs:string (enum) | — | Token from the IAB-defined layout vocabulary (§3.2). |

Enum values for `@name`:

| Enum value | Description |
|------------|-------------|
| `linear` | Linear in-stream ad slot — invalid inside `<svta:OverlayPresentation>` (raise validation error). |
| `pause-ad` | Pause Ad — invalid inside `<svta:OverlayPresentation>`; use `<svta:PauseAdTrigger>` (§5.1.4) instead. |
| `menu-ad` | Menu Ad. |
| `squeezeback` | Squeezeback (content resized). |
| `overlay` | Overlay (content not resized). |
| `in-scene` | In Scene Ads (composited into programming). |
| `screen-saver-ad` | Screen Saver Ad. |
| `companion-ad` | Companion Ad. |

Sub-placement refinements (`overlay-corner`, `overlay-lower-third`,
`squeezeback-l-shape`, `squeezeback-frame`, `squeezeback-double-box`,
`squeezeback-double-box-with-background`, `menu-headline-banner`,
`menu-in-tile`) MAY be used as values of `@name` when the
Broadcaster needs to constrain the rendering surface further than
the top-level identifier. The refinement is recognised by the
Player if and only if it is listed in `<svta:AllowedLayouts>`.

##### 5.1.3.2 `<svta:Concurrency>`

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@max` | yes | xs:unsignedInt | — | Maximum number of concurrent overlays the Player MAY render during this slot. `1` is the common case; values greater than `1` allow stacking. |

##### 5.1.3.3 `<svta:Exclusions>`

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| (none) | — | — | — | All semantics carried by `<svta:Pair>` children. |

| Child element | Required | Cardinality | Description |
|---------------|----------|-------------|-------------|
| `<svta:Pair>` | no | 0..N | One mutually-exclusive layout pair. |

`<svta:Pair>` attributes:

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@a` | yes | xs:string | — | Layout identifier of the first member of the pair. |
| `@b` | yes | xs:string | — | Layout identifier of the second member of the pair. |

When `<svta:Pair @a="X" @b="Y"/>` is present, the Player MUST NOT
render layouts `X` and `Y` concurrently during this slot. Order
of the operands is not significant.

##### Example (illustrative, short)

```xml
<EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
             timescale="1000">
  <Event id="201" presentationTime="120000" duration="30000">
    <svta:OverlayPresentation
        xmlns:svta="urn:svta:dash:sgai:2026"
        url="https://ads.example.com/decision/overlay-mid"
        earliestResolutionTimeOffset="10"
        maxDuration="30000">
      <svta:AllowedLayouts>
        <svta:Layout name="overlay-corner"/>
        <svta:Layout name="overlay-lower-third"/>
      </svta:AllowedLayouts>
      <svta:Concurrency max="1"/>
    </svta:OverlayPresentation>
  </Event>
</EventStream>
```

#### 5.1.4 `<svta:PauseAdTrigger>` (non-linear, NEW)

Scheme URI: `urn:svta:dash:sgai-pause-trigger:2026`.

`<svta:PauseAdTrigger>` declares a window of validity during which
viewer-initiated pause permits an overlay ad. Outside the window,
pause does not permit any overlay. The Player consults the set of
active `<svta:PauseAdTrigger>` events when the viewer pauses;
exactly one event whose interval contains the pause instant fires.

The event's `presentationTime` and `duration` (inherited from
`<Event>`) define the window: the window starts at
`presentationTime` and lasts for `duration`
`EventStream@timescale` units. When the viewer pauses inside the
window, the Player resolves `@url` against the ADS and renders the
returned candidate on top of the paused primary frame.

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@url` | yes | xs:anyURI | — | The ADS endpoint to resolve at the pause instant. |
| `@maxDuration` | yes | xs:unsignedInt | — | Maximum display duration of the pause ad, in `EventStream@timescale` units. The Player enforces this cap (§7.3, P-5). |
| `@earliestResolutionTimeOffset` | yes | xs:unsignedInt | — | Offset, in seconds, by which the Player MAY speculatively pre-fetch the resolution document ahead of the window opening. `0` means the Player defers the request to the pause instant. |

| Child element | Required | Cardinality | Description |
|---------------|----------|-------------|-------------|
| `<svta:AllowedLayouts>` | yes | 1 | Enumerates the layout names permitted on this slot (§5.1.3.1, same syntax). The token `pause-ad` (or its sub-placements) MUST appear in the set. |
| `<svta:Concurrency>` | yes | 1 | Bounded to `@max="1"` for `<svta:PauseAdTrigger>`. |
| `<svta:Exclusions>` | no | 0..1 | OPTIONAL; same syntax as §5.1.3.3. |

NOTE — The `<svta:PauseAdTrigger>` and `<svta:OverlayPresentation>`
share the same attribute set and child element shapes. They are
distinguished by their `EventStream@schemeIdUri` because the
**trigger semantics** differ: `<svta:OverlayPresentation>` activates
at `presentationTime`; `<svta:PauseAdTrigger>` activates only when
the viewer pauses inside the window.

##### Example (illustrative, short)

```xml
<EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026"
             timescale="1000">
  <Event id="301" presentationTime="0" duration="3600000">
    <svta:PauseAdTrigger
        xmlns:svta="urn:svta:dash:sgai:2026"
        url="https://ads.example.com/decision/pause"
        earliestResolutionTimeOffset="0"
        maxDuration="60000">
      <svta:AllowedLayouts>
        <svta:Layout name="pause-ad"/>
      </svta:AllowedLayouts>
      <svta:Concurrency max="1"/>
    </svta:PauseAdTrigger>
  </Event>
</EventStream>
```

#### 5.1.5 Co-located events (hybrid linear + overlay)

A Period MAY contain a linear event (§5.1.1 or §5.1.2) and one or
more non-linear events (§5.1.3) at the same `presentationTime`.
Co-located events do not share state at the syntax level; each is
resolved independently by the Player against its own `@url`. The
Player's expected behaviour during co-located activation is
specified in §7.6 (UC-04 hybrid).

The Player MUST NOT introduce implicit cross-event linkage at the
ADS request layer; each event triggers its own resolution
request. Cross-event linkage, when needed, is expressed by
matching `@url` query parameters at the Broadcaster's discretion
(§I.4 `UrlParamInfo`), not by syntax on the events themselves.

### 5.2 Resolution documents

The resolution document is the XML body returned by the ADS in
response to the Player's resolution request. Two profiles are
defined:

- §5.2.1 — `urn:mpeg:dash:profile:list:2024` (linear baseline,
  inherited from §8.14 of ISO/IEC 23009-1).
- §5.2.2 — `urn:svta:dash:profile:sgai-overlay-list:2026`
  (overlay-aware extension, NEW).

The Player MUST select the validation path corresponding to the
profile URI declared in `MPD@profiles` of the resolution document.

#### 5.2.1 Linear baseline ListMPD (`urn:mpeg:dash:profile:list:2024`)

The linear baseline ListMPD is the resolution document for
linear ad opportunities (`<InsertPresentation>` /
`<ReplacePresentation>`). It is inherited verbatim from
ISO/IEC 23009-1 §8.14.

Top-level shape:

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `MPD@type` | yes | xs:string (enum) | — | MUST be `list`. |
| `MPD@profiles` | yes | xs:string | — | MUST include `urn:mpeg:dash:profile:list:2024`. |
| `MPD@publishTime` | yes | xs:dateTime | — | Document emission instant. |

| Child element | Required | Cardinality | Description |
|---------------|----------|-------------|-------------|
| `<BaseURL>` | no | 0..N | OPTIONAL base URL for relative URIs in the document. |
| `<Period>` | yes | 1..N | One Period per ad in the pod, in declared order (§7.3, P-4). |

Each `<Period>` carries:

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@id` | yes | xs:ID | — | Period identifier, unique within the document. |
| `@duration` | yes | xs:duration | — | Declared duration of the ad in this Period. Drives Player pre-validation against the parent event's `@maxDuration`. |

| Child element | Required | Cardinality | Description |
|---------------|----------|-------------|-------------|
| `<ImportedMPD>` | yes | 1 | The sub-MPD reference. The imported document is bound to the SPS profile (§5.3). |

A linear baseline ListMPD MUST NOT carry a `<svta:RenderableAsset>`
under a `<Period>`. Non-AV forms are not expressible in this profile;
ADSs that need to carry them MUST emit the §5.2.2 profile instead.

#### 5.2.2 Overlay-aware resolution document (`urn:svta:dash:profile:sgai-overlay-list:2026`)

The overlay-aware profile extends the linear baseline ListMPD with
support for multi-form candidates: each `<Period>` MAY carry one or
more `<svta:RenderableAsset>` elements alongside (or instead of) the
`<ImportedMPD>` reference. Each `<svta:RenderableAsset>` declares
one renderable form of the candidate; the Player chooses one form
per device per §7.3.

Top-level shape: identical to §5.2.1 except that `MPD@profiles`
MUST include `urn:svta:dash:profile:sgai-overlay-list:2026`. The
ADS MAY include both the linear baseline profile URI and the
overlay-aware profile URI in `@profiles`, in which case the
overlay-aware semantics apply.

Each `<Period>` carries:

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@id` | yes | xs:ID | — | Period identifier, unique within the document. |
| `@duration` | yes | xs:duration | — | Declared maximum duration of the candidate in this Period. For non-linear candidates the value matches the slot's `@maxDuration` window; for linear candidates it matches the candidate's intrinsic length. The attribute name is REUSED VERBATIM from baseline DASH because the semantics match. |

| Child element | Required | Cardinality | Description |
|---------------|----------|-------------|-------------|
| `<ImportedMPD>` | no | 0..1 | An SPS-conformant sub-MPD reference carrying the candidate's video form. OPTIONAL when the candidate has no video form. |
| `<svta:RenderableAsset>` | no | 0..N | One per non-video form of the candidate. OPTIONAL; at least one of `<ImportedMPD>` or `<svta:RenderableAsset>` MUST be present. |
| `<svta:Metadata>` | no | 0..1 | OPTIONAL application-level metadata (§5.6). |

NOTE — The asymmetry — `<ImportedMPD>` for video, `<svta:RenderableAsset>`
for everything else — is forced by ISO/IEC 23009-1 §5.3.2.6,
§8.15, §7.3, and IETF RFC 4337. `<ImportedMPD>` is normatively
bound to the Single-Period Static profile, whose
`Representation@mimeType` is constrained to the RFC 4337
registry (`video/mp4`, `audio/mp4`, `application/mp4`). There is
no DASH-conformant path for a non-MP4 asset on an `AdaptationSet`
/ `Representation` reached through `<ImportedMPD>` or inside a
ListMPD-level `<Period>`. Non-AV ad assets (HTML, image, other)
MUST therefore be carried via a foreign-namespace open content
element (§5.2.1 of ISO/IEC 23009-1) — the role filled by
`<svta:RenderableAsset>`.

NOTE — The Period@duration semantics for a non-linear candidate
match the slot's overlay window. The spec deliberately reuses
`@duration` (rather than introducing `@overlayDuration` or
similar) to honour the naming-consistency rule for new identifiers
that share semantics with the baseline.

##### Example (illustrative, short)

```xml
<Period id="cand_1" duration="PT30S">
  <ImportedMPD uri="https://ads.example.com/cand_1_video.mpd"
               earliestResolutionTimeOffset="0"/>
  <svta:RenderableAsset
      xmlns:svta="urn:svta:dash:sgai:2026"
      mediaType="text/html"
      layout="overlay-lower-third"
      src="https://ads.example.com/cand_1.html"
      priority="10"/>
  <svta:RenderableAsset
      xmlns:svta="urn:svta:dash:sgai:2026"
      mediaType="image/png"
      layout="overlay-corner"
      src="https://ads.example.com/cand_1.png"
      width="640" height="360"
      priority="20"/>
</Period>
```

### 5.3 `<svta:RenderableAsset>`

`<svta:RenderableAsset>` is the foreign-namespace open content
element introduced by this specification to carry a non-video
renderable form of a candidate. It lives under
`<Period>` of the §5.2.2 resolution document, as a sibling of
`<ImportedMPD>`. Multiple `<svta:RenderableAsset>` children are
permitted; each declares one form.

#### 5.3.1 Attributes

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@src` | yes | xs:anyURI | — | The asset URL. Fetched by the Player at render time. |
| `@mediaType` | yes | xs:string (enum) | — | The asset's IANA media type. Drives Player capability matching. |
| `@layout` | yes | xs:string (enum) | — | The layout identifier from §3.2 that applies to this form. |
| `@priority` | no | xs:unsignedInt | `1000` | ADS-supplied priority hint for this form, lower-is-higher-priority. The Player uses this hint to order the forms during selection (§7.3). |
| `@width` | no | xs:unsignedInt | — | Intrinsic width of the asset, in pixels. OPTIONAL but RECOMMENDED for image and video forms. |
| `@height` | no | xs:unsignedInt | — | Intrinsic height of the asset, in pixels. OPTIONAL but RECOMMENDED for image and video forms. |
| `@duration` | no | xs:duration | — | Intrinsic duration of the asset (for animated forms). OPTIONAL; when present, the Player uses this for trim arithmetic. |

#### 5.3.2 Enum values for `@mediaType`

| Enum value | Description |
|------------|-------------|
| `text/html` | HTML document, rendered via an HTML overlay surface. Requires D1, D3 device class capability. |
| `image/png`, `image/jpeg`, `image/webp`, `image/gif` | Static or animated image, rendered via the image overlay surface. Requires image-on-video capability (D1, D3, D4). |
| `application/javascript+html` | HTML5 / JS interactive payload bundled as a single document; treated as `text/html` for capability matching, with the additional requirement that the device supports script execution in the overlay surface. |

ADSs MUST NOT emit `<svta:RenderableAsset @mediaType="…">` with
values outside the above enum. Video forms MUST be carried via
`<ImportedMPD>`, not `<svta:RenderableAsset>`, because video
playback requires the DASH segment delivery semantics that
`<ImportedMPD>` provides and `<svta:RenderableAsset>` does not.

#### 5.3.3 Enum values for `@layout`

The values defined in §3.2 (top-level identifiers and the
sub-placement refinements) are all admissible. Layouts not
enumerated in §3.2 are non-conformant.

#### 5.3.4 Priority semantics

`@priority` orders forms within a candidate from highest-priority
(lowest numeric value) to lowest-priority (highest numeric value).
When two forms carry the same priority, the Player MAY choose
freely among them; the choice MUST be deterministic given the
same input on the same device, so that diagnostics are
reproducible.

Across candidates, ordering is established by the order of
`<Period>` elements in the resolution document (§7.3, P-4). The
ADS MUST NOT use `@priority` to convey across-candidate ordering;
that ordering is conveyed exclusively by `<Period>` order. The
two ordering dimensions are independent and MUST NOT be conflated.

### 5.4 Sub-MPD (SPS profile)

When a candidate's video form is carried via `<ImportedMPD>`, the
imported document is a sub-MPD bound to the Single-Period Static
(SPS) profile (`urn:mpeg:dash:profile:sps:2024`, ISO/IEC 23009-1
§8.15). The sub-MPD's shape is inherited verbatim from §8.15 and
is NOT re-specified here. The relevant constraints for SGAI are:

- The sub-MPD MUST contain exactly one `<Period>`.
- The Period MUST contain at least one `<AdaptationSet>` (§5.3.2.2
  Table 4 of ISO/IEC 23009-1).
- Each `Representation@mimeType` in the sub-MPD MUST be drawn
  from the IETF RFC 4337 registry (`video/mp4`, `audio/mp4`,
  `application/mp4`). The sub-MPD MUST NOT carry non-MP4 mime
  types on `AdaptationSet` or `Representation`.
- The sub-MPD MAY embed an `<EventStream>` of scheme
  `urn:mpeg:dash:event:callback:2015` (§5.5) carrying tracking
  beacons for the candidate.
- The sub-MPD MAY embed application-level metadata via the
  foreign-namespace open content rule of §5.2.1 of
  ISO/IEC 23009-1 — typically a `<svta:Metadata>` child of
  `<Period>` (§5.6).

ADSs MUST NOT wrap a non-MP4 payload (HTML page, image, JSON,
etc.) inside an `application/mp4` `Representation` to circumvent
the RFC 4337 constraint. Such constructions do not add DASH
segment-delivery semantics for the underlying format and are
non-conformant by spirit, even when they parse as DASH.

### 5.5 Tracking carrier

In-band ad tracking beacons (impression, start, quartiles,
complete, and any additional VAST-equivalent event types) MUST be
carried as `<Event>` entries inside an `<EventStream>` of scheme
`urn:mpeg:dash:event:callback:2015` (ISO/IEC 23009-1 §4.7,
§5.10.4.5).

#### 5.5.1 Carrier shape

| Attribute on `<EventStream>` | Required | Type | Default | Description |
|------------------------------|----------|------|---------|-------------|
| `@schemeIdUri` | yes | xs:anyURI | — | MUST be `urn:mpeg:dash:event:callback:2015`. |
| `@timescale` | yes | xs:unsignedInt | — | Tick rate for `presentationTime` on the contained events. |

| Attribute on `<Event>` | Required | Type | Default | Description |
|------------------------|----------|------|---------|-------------|
| `@id` | yes | xs:unsignedInt | — | Event identifier, unique within the `<EventStream>`. |
| `@presentationTime` | yes | xs:unsignedInt | — | The instant at which the Player fires the beacon, interpreted per §7.5. |

The `<Event>` element's text content carries the URL to be fetched
when the event fires. The Player issues an HTTP GET to this URL,
discards the response body, and treats any non-2xx status as a
non-fatal failure (§8.1 error E11).

#### 5.5.2 Where the tracking carrier lives

- **Linear**. The tracking `<EventStream>` lives inside the
  sub-MPD `<Period>` (§5.4), one per ad candidate.
- **Non-linear**. The tracking `<EventStream>` lives inside the
  sub-MPD's `<Period>` for the video form of the candidate.
  When the chosen form is non-video (image, HTML), the resolution
  document's `<Period>` MUST still carry a `<ImportedMPD>` to a
  minimal SPS sub-MPD that wraps the tracking `<EventStream>`,
  or the tracking MUST be carried via a sibling
  `<svta:Metadata>` element pointing back at the same callback
  scheme (see §5.5.3).

#### 5.5.3 Tracking for non-video candidates

When a candidate has no video form (HTML and image only), no
`<ImportedMPD>` is present on the `<Period>`. The Player has no
sub-MPD `<Period>` from which to read the tracking `<EventStream>`.
Two carriers are admissible; both are within the foreign-namespace
open-content extension point of §5.2.1 of ISO/IEC 23009-1:

- **(a) Inline tracking on the resolution-document `<Period>`** —
  an `<EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015">`
  appearing as a child of the `<Period>` in the §5.2.2 resolution
  document, alongside `<svta:RenderableAsset>`. The Player applies
  the same beacon-firing rules as for a sub-MPD tracking carrier,
  with `presentationTime` interpreted relative to the slot
  window (§7.5). When this carrier is used inside a
  `Period@duration` that is non-zero, an `<AdaptationSet>` MUST
  NOT be required by the resolution-document profile because the
  §5.3.2.2 Table 4 constraint is bound to baseline-DASH Periods;
  the overlay-aware profile (§5.2.2) relaxes the AdaptationSet
  requirement for this carrier explicitly. (See §5.6.5 for the
  full extension-rule discussion.)
- **(b) Tracking inside `<svta:Metadata>`** — embedding the
  `<EventStream>` inside the `<svta:Metadata>` foreign-namespace
  child. Equivalent on the wire; preserved for symmetry with the
  application-level metadata carrier (§5.6.1).

ADSs SHOULD prefer carrier (a) for simplicity. Carrier (b) is
RECOMMENDED only when the same `<svta:Metadata>` block carries
other application-level metadata that the ADS wants to keep
syntactically together with the beacon list.

#### 5.5.4 Beacon timing

`presentationTime` on a callback `<Event>` is interpreted by the
Player according to the slot kind:

- **Linear**. `presentationTime` is interpreted against the
  sub-MPD's media-internal timeline (the standard
  §5.10.4.5 semantics).
- **Non-linear**. `presentationTime` is interpreted against the
  Broadcaster-declared overlay window — i.e. the `@maxDuration`
  of the parent `<svta:OverlayPresentation>` or
  `<svta:PauseAdTrigger>` — not against the ad's internal
  duration.

The non-linear remap is performed at resolution time by the ADS
when constructing the sub-MPD or `<svta:Metadata>` block. The
Player applies the standard §5.10.4.5 firing rule with no
remap of its own; the Player therefore inherits the
ignore-if-unknown semantics of the callback scheme unchanged.

NOTE — The non-linear remap is normative to the ADS (§7.5 / §8.1
ADS guarantee). The Player MUST stop firing beacons at the
trim boundary established by §4.4 / §7.3 (P-9); §8.1 row E9
covers the case.

### 5.6 Application-level metadata

The `<svta:Metadata>` element is the foreign-namespace open
content carrier for application-level ad metadata that has no
native MPEG-DASH carrier. Typical contents include click-through
URLs, ad system identifiers, ad titles, and universal ad
identifiers — the VAST-equivalent metadata that production
SGAI deployments traffic alongside the ad payload.

`<svta:Metadata>` lives in `urn:svta:dash:sgai:2026`. It MAY
appear as a child of `<Period>` in a resolution document of
§5.2.2 or of `<Period>` in a sub-MPD (§5.4).

#### 5.6.1 Attributes

`<svta:Metadata>` has no attributes of its own. All payload
fields are carried as child elements.

#### 5.6.2 Children

| Element | Required | Cardinality | Description |
|---------|----------|-------------|-------------|
| `<svta:Click>` | no | 0..1 | Click-through descriptor (§5.6.3). |
| `<svta:AdSystem>` | no | 0..1 | Ad system identifier. Text content: the ad system identifier string emitted by the upstream decisioning system. |
| `<svta:AdTitle>` | no | 0..1 | Human-readable ad title. Text content: the title string. |
| `<svta:UniversalAdId>` | no | 0..N | Universal ad identifier. See §5.6.4. |
| `<EventStream>` (DASH baseline) | no | 0..N | OPTIONAL tracking carrier (§5.5.3 case (b)). |

#### 5.6.3 `<svta:Click>`

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@uri` | yes | xs:anyURI | — | The click-through URL. The Player MAY surface this URL to the embedding application or fire it on viewer click. |
| `@trackingUri` | no | xs:anyURI | — | OPTIONAL click-tracking URL. The Player MAY fire this URL when the click-through is exercised. |

#### 5.6.4 `<svta:UniversalAdId>`

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `@idRegistry` | yes | xs:string | — | The registry under which the identifier is issued (e.g. `ad-id.org`). |
| `@idValue` | yes | xs:string | — | The identifier string. |

#### 5.6.5 Extension rules and legacy compatibility

`<svta:Metadata>` and its children operate under the
foreign-namespace open-content extension point of §5.2.1 of
ISO/IEC 23009-1. A Player that does not implement
`urn:svta:dash:sgai:2026` discards the `<svta:Metadata>` element
together with its full subtree (§5.2.1 NOTE 2). The discard is
recursive: any baseline DASH element nested inside
`<svta:Metadata>` is invisible to legacy Players. This is
intentional — application-level metadata is opaque to legacy
playback by design.

When this opacity matters (e.g. when a baseline DASH element MUST
be visible to legacy Players alongside an SGAI extension), the
authoring rule is to place the baseline element as a **sibling**
of the SGAI extension, not as a child. The §5.2.1 NOTE 2 discard
semantics make this distinction load-bearing.

### 5.7 URL parameterisation

ADS resolution requests inherit the `UrlParamInfo` descriptor
(§I.4 of ISO/IEC 23009-1) verbatim. The descriptor's `@includeInRequests`
attribute MUST include the value `altmpd` for linear opportunities;
this specification introduces no new value for non-linear
opportunities — `altmpd` covers both, because the descriptor's
role is to template the query string for an ADS request and the
ADS request shape is identical across linear and non-linear from
the Player's perspective.

NOTE — A future edition MAY introduce a more specific value
(`overlay`, `pause`) to let the Broadcaster scope different
parameter templates per slot kind. The default rule for this
edition is: a single `UrlParamInfo` descriptor with
`@includeInRequests="altmpd"` applies to all ADS requests issued
by the Player.

---

## 6. Interfaces

This chapter pins the wire-level contracts among the three actors.
Examples are illustrative; complete walk-throughs live in the
annexes.

### 6.1 Broadcaster → Player (main MPD delivery)

| Property | Value |
|----------|-------|
| Transport | HTTPS |
| Direction | Pull (Player initiates) |
| Format | DASH MPD (XML), this specification |
| Content | Primary content tracks + SGAI event streams (§5.1) + `UrlParamInfo` descriptor (§5.7) |
| Error semantics | Standard HTTP status codes. On 4xx/5xx the Player retries or aborts the session per DASH-IF guidance. |

### 6.2 Player → ADS (resolution request)

| Property | Value |
|----------|-------|
| Transport | HTTPS |
| Direction | Pull (Player initiates) |
| Request URL | The `@url` of the activating SGAI event, augmented with the query string templated by the `UrlParamInfo` descriptor (§5.7) |
| Request method | GET |
| Request body | None |
| Request timing | Any instant between the Earliest Resolution Time (`presentationTime − @earliestResolutionTimeOffset`) and `presentationTime` (linear, overlay); for pause-trigger, the pause instant or speculatively earlier when `@earliestResolutionTimeOffset > 0` |
| Response body | A resolution document conforming to §5.2.1 (linear baseline) or §5.2.2 (overlay-aware) |
| Error semantics | §8.1 rows E1–E4 |

### 6.3 ADS → Player (resolution response)

The ADS response carries the resolution document. The shape
depends on the slot kind:

- **Linear**. `urn:mpeg:dash:profile:list:2024` (§5.2.1). One
  `<Period>` per ad in the pod; each `<Period>` references a
  sub-MPD via `<ImportedMPD>`.
- **Non-linear**. `urn:svta:dash:profile:sgai-overlay-list:2026`
  (§5.2.2). One `<Period>` per candidate; each `<Period>` MAY
  carry an `<ImportedMPD>` (video form) and/or one or more
  `<svta:RenderableAsset>` elements (non-video forms). Each
  candidate may carry `<svta:Metadata>` for application-level
  metadata (§5.6).

The Player MUST select the validation path corresponding to the
declared profile URI. The ADS MAY include both URIs in
`@profiles` when the response carries only ISO-BMFF-renderable
candidates and is therefore valid under both profiles; in that
case the overlay-aware semantics apply (§5.2.2).

### 6.4 Player → Ad CDN (segment fetch)

| Property | Value |
|----------|-------|
| Transport | HTTPS |
| Direction | Pull (Player initiates) |
| Format | ISO-BMFF / CMAF segments (video forms only); HTML / image bytes (non-video forms) |
| Error semantics | §8.1 row E10 |

### 6.5 Player → tracking endpoints (beacon firing)

| Property | Value |
|----------|-------|
| Transport | HTTPS |
| Direction | Push (Player initiates), fire-and-forget |
| Format | HTTP GET to the URL in the callback `<Event>` text content (§5.5) |
| Request body | None |
| Response handling | The Player discards the response body. Non-2xx status is treated as a non-fatal failure (§8.1 row E11). |

### 6.6 ADS internal: VAST → resolution document conversion (non-normative)

A typical production ADS deployment receives ad responses as VAST
from one or more upstream sources and adapts them into the
resolution document this specification consumes. The adaptation
is an ADS-internal concern; the Player has no visibility into
the VAST layer.

This specification does not require, mandate, or prohibit any
specific VAST version. The Player ↔ ADS interface (§6.2 / §6.3) is
defined entirely against the resolution document shapes of §5.2;
a Player operating against an ADS that does not use VAST is fully
conforming with no adapter layer.

Annex H carries an illustrative VAST → resolution-document
adapter mapping for context. The mapping is explicitly
non-normative per §4.2 (B-5) and §4.4 (P-12).

---

## 7. Expected behaviour

This chapter specifies the per-actor behavioural obligations. Each
section is a normative algorithm or contract; the deep walk-throughs
of each behaviour against each use case live in the annexes
(A through G).

### 7.1 Broadcaster behaviour

The Broadcaster has no run-time behavioural obligations beyond
the authoring-time discipline of §4.2: declaring each slot via
the appropriate event scheme, populating the required attributes
and children, and respecting the naming and extension-rule
constraints of §5.6.5.

### 7.2 ADS behaviour

At resolution time, the ADS:

1. Receives the Player's resolution request on the URL declared
   by the activating SGAI event (§6.2).
2. Performs its internal decisioning (targeting, frequency
   capping, ordering — out of scope for this specification).
3. Constructs a resolution document conforming to one of the
   profiles of §5.2.
4. For non-video forms, attaches `<svta:RenderableAsset>`
   elements with the appropriate `@mediaType` / `@layout` /
   `@priority` (§5.3).
5. For non-linear slots, places callback `<Event>` entries at
   `presentationTime` values measured against the
   Broadcaster-declared slot window (§5.5.4) rather than the
   ad's internal duration.
6. Returns the resolution document to the Player.

The ADS MUST honour the slot's resolution window: if it cannot
meet the deadline, it SHOULD return early with an empty document
rather than late with content (§8.1 row E4).

### 7.3 Player validation and selection algorithm

The Player applies the following normative algorithm to every
resolution document it receives. The algorithm is stated
imperatively; an implementation MAY restructure the control flow
provided the observable behaviour is identical.

Given a resolution document `D` for slot `S`:

```
1. Read D.MPD@profiles. If D advertises §5.2.2
   (urn:svta:dash:profile:sgai-overlay-list:2026), apply the
   overlay-aware selection path; otherwise (§5.2.1) apply the
   linear baseline path.

2. Let CANDIDATES = D.//Period in document order.
   Let CUMULATIVE = 0.
   Let RENDERED = [] (the candidates accepted for rendering, in
                     order).

3. For each candidate C in CANDIDATES (in document order):
   a. Compute FORMS(C):
        - For linear baseline path: a single video form,
          materialised by C/ImportedMPD.
        - For overlay-aware path: the union of {video form from
          C/ImportedMPD, if present} and {one form per
          C/svta:RenderableAsset}, ordered by ascending
          @priority (lower @priority = higher rank).
   b. Filter FORMS(C) against the device capability matrix of §3.4
      (drop forms the device cannot render).
   c. Filter FORMS(C) against the Broadcaster's
      <svta:AllowedLayouts> (drop forms whose @layout is not in
      the allowed set).
   d. Filter FORMS(C) against any active <svta:Exclusions>
      pairings, given the layouts of forms already selected on
      concurrent candidates (drop forms that would violate an
      exclusion).
   e. If FORMS(C) is empty, skip C and continue with the next
      candidate (P-7). Preserve the order of remaining
      candidates (P-4).
   f. Pick the highest-priority form in FORMS(C). Call it
      FORM(C).
   g. If CUMULATIVE + declared_duration(FORM(C)) > S.@maxDuration,
      MAY drop C ("drop before play", P-8). If C is dropped, skip
      to step 3 for the next candidate.
   h. Accept C with FORM(C). Append (C, FORM(C)) to RENDERED.
      Update CUMULATIVE += declared_duration(FORM(C)).

4. Render the RENDERED list in declared order:
   a. Fetch the segments / asset for each form.
   b. Composite per the layout (§7.4).
   c. As each form plays, monitor actual rendered length. If
      CUMULATIVE_ACTUAL would exceed S.@maxDuration, stop
      rendering exactly at the cap boundary (P-5, "trim during
      play"). Stop firing tracking beacons at the trim boundary
      (P-9).

5. On completion (or trim) of RENDERED, resume primary content
   per the slot kind:
   a. <InsertPresentation>: resume where the main timeline was
      paused (§5.16.3 of ISO/IEC 23009-1).
   b. <ReplacePresentation>: resume at the position determined
      by @returnOffset (§5.16.4).
   c. <svta:OverlayPresentation>: no resume action required —
      the primary timeline was never interrupted; the overlay
      is dismissed (visually removed).
   d. <svta:PauseAdTrigger>: dismiss the overlay when the viewer
      resumes; the primary timeline continues from the paused
      frame.
```

The algorithm's invariants:

- **Order preservation**. The relative order of candidates in
  `RENDERED` matches the document order of `CANDIDATES`. The
  algorithm never re-orders or deduplicates.
- **Cap enforcement**. `CUMULATIVE_ACTUAL` never exceeds
  `S.@maxDuration` at any instant during rendering.
- **Device coverage**. Every form in `RENDERED` is renderable on
  the Player's device class. The algorithm never attempts to
  render an unrenderable form.
- **Constraint coverage**. Every form in `RENDERED` carries a
  layout in `<svta:AllowedLayouts>` and respects every
  applicable `<svta:Exclusions>` pair.

### 7.4 Compositing rules

The on-screen composition of an accepted form is governed by the
form's `@layout` and the device's overlay surfaces. This
specification does NOT define a parallel layout standard. It
defers to:

- **HTML 5 / CSS** for the spatial arrangement of HTML and image
  overlays.
- The **IAB layout vocabulary** (§3.2) for the semantic role of
  each layout token. The IAB document defines the visual
  expectations (aspect ratio, position, content resize policy)
  associated with each token.

Position semantics inside a layout (left, right, top, bottom,
relative percentages) MUST be expressed via HTML5 / CSS
primitives. This specification does not enumerate them.

### 7.5 Tracking semantics

The Player fires tracking beacons embedded under the callback
scheme (§5.5) at the times indicated by their `presentationTime`
values. The interpretation depends on slot kind:

- **Linear**. `presentationTime` is interpreted against the
  sub-MPD's media-internal timeline. Beacons fire when the ad's
  internal playback clock reaches the indicated value.
- **Non-linear**. `presentationTime` is interpreted against the
  Broadcaster-declared overlay window. The ADS is responsible for
  placing beacon `presentationTime` values such that they fire
  at the intended fractions of the slot window (§5.5.4 / §7.2 /
  §8.1 row E9).

Required beacons for non-linear ads:

- **Impression**. MUST fire at the instant the overlay becomes
  visible to the viewer (P-9, R13.1 obligation).
- **Quartile beacons (25%, 50%, 75%, complete)**. SHOULD fire at
  the indicated fractions of the slot window. When the slot is
  trimmed (P-5) before all quartiles fire, the Player MUST stop
  firing beacons at the trim boundary.

The Player MUST NOT introduce its own beacon schedule. Beacons
the ADS did not emit MUST NOT be fired.

### 7.6 Coexisting events (UC-04 hybrid linear + overlay)

When two SGAI events activate at the same `presentationTime` (a
linear event of §5.1.1 / §5.1.2 and one or more non-linear events
of §5.1.3), the Player MUST treat them as independent activations:

1. Resolve each event against its own `@url`; the Player MUST NOT
   collapse the two requests into one. The two responses are
   independent.
2. Validate each response against the corresponding slot
   constraints, separately.
3. Render in parallel: the linear ad on the primary surface, the
   overlay on the overlay surface, subject to device capability.
   On device classes that cannot composite the overlay on top of
   the linear ad (D3 / D4 single-decoder; D5 no overlay), the
   Player MUST decline the overlay portion gracefully (§7.7) and
   render the linear portion only.

The Player MUST NOT introduce cross-event linkage beyond what the
two `<EventStream>` declarations carry. Cross-event linkage,
when needed by the Broadcaster, is expressed in the `@url`
templates (§5.7 / §I.4) — not in the syntax of the events
themselves.

### 7.7 Per-device-class expected behaviour matrix

The matrix below restates the Player's expected behaviour for
each (device class × ad opportunity kind) combination. Entries
read "what the user sees" in the default case where the ADS
returns a well-formed multi-form candidate; degraded outcomes
fall under §8.1.

| Opportunity (slot kind) | D1 | D2 | D3 | D4 | D5 |
|--------------------------|----|----|----|----|----|
| **Linear pre-roll / mid-roll** (§5.1.1, §5.1.2) | Full-screen ad of bounded duration; primary resumes per event semantics. | Same as D1; second decoder MAY pre-buffer. | Same as D1, single decoder reused sequentially. | Same as D3. | Same as D3. |
| **Multi-ad break** (linear pod) | Back-to-back sequence; primary resumes after last ad. | Same as D1. | Single decoder reused sequentially across the pod. | Same as D3. | Same as D3. |
| **Coexisting overlay** (`<svta:OverlayPresentation>`) | Highest-fidelity form (HTML / video / image) composited on top of primary. | Video form composited on second decoder; non-video forms unrenderable (declined per §5.7). Side-by-side MAY apply if `<svta:AllowedLayouts>` contains it. | HTML or image form composited via overlay surface; video form skipped (single decoder). | Image form only; HTML and video skipped. If no image form available, candidate declined. | Decline the opportunity entirely; primary continues uninterrupted. |
| **Hybrid linear + overlay** (§5.1.5) | Linear ad full-screen + overlay composited on top. | Linear ad full-screen + video-form overlay on second decoder if available; otherwise linear only. | Linear ad full-screen, overlay declined (conservative default — see §8.4 for the open question). | Same as D3. | Linear ad full-screen, overlay declined. |
| **Pause-triggered ad** (`<svta:PauseAdTrigger>`) | Highest-fidelity form on top of paused frame; dismissed on resume. | Video form on top of paused frame (primary decoder holds paused frame, second decoder plays ad); non-video forms unrenderable. | HTML or image form on top of paused frame; video form skipped (see §8.4 for the device-capability open question). | Image form only. | Decline the opportunity entirely; paused frame stays until viewer resumes. |
| **Legacy Player encounters new constructs** | Primary continues uninterrupted; the unknown event scheme or foreign-namespace element is silently ignored (§5.6.5). | Same. | Same. | Same. | Same. |

Per §4.4 (P-7, P-10), "decline the opportunity" is always a
conforming outcome. The Player MUST NOT raise an error, fire a
beacon, or surface any visible artefact when it declines.

---

## 8. Implementation notes

This chapter is non-normative. It captures guidance for
implementations addressing scenarios the normative chapters leave
under-specified.

### 8.1 Error semantics

Errors on the Player ↔ Broadcaster, Player ↔ ADS, and Player ↔
tracking endpoint interfaces, plus playback-time and decode-time
failures. Twelve rows cover the principal categories. Player
behaviour columns are normative obligations; ADS / Broadcaster
columns are informative guidance.

| ID | Error condition | Player response (MUST) | Player response (MAY) | ADS / Broadcaster guidance |
|----|-----------------|------------------------|------------------------|------------------------------|
| **E1** | Transport failure on the resolution request to the ADS (HTTP timeout, 4xx, 5xx, DNS unreachable, TCP refused, TLS handshake failure). | Fall through to primary content uninterrupted. MUST NOT block primary playback waiting for the ADS. | Apply a bounded retry inside the window between the Earliest Resolution Time and the slot's `presentationTime`; abandon retries once the window closes. | ADS SHOULD bound its response latency. Broadcaster SHOULD set `@earliestResolutionTimeOffset` large enough to leave room for one retry. |
| **E2** | Resolution document unparseable or schema-invalid (malformed XML, unknown root element, unsupported profile URI, missing required attributes). | Treat as if no document was returned; fall through. MUST NOT attempt partial recovery. | Log the failure for diagnostics. | ADS MUST emit documents that validate against the profile declared in `@profiles`. |
| **E3** | Resolution document well-formed but empty (zero `<Period>` entries). | Fall through. MUST NOT fire any tracking beacon. | Surface a non-normative "no-fill" event to the application layer. | ADS MAY return an empty document deliberately as a no-fill signal; this is conforming. |
| **E4** | Resolution document arrives after the slot window has elapsed. | Discard the late response; fall through. MUST NOT delay primary playback to render a late ad. | Reuse the late response for a subsequent slot only if its scheme allows it; otherwise discard. | ADS MUST honour the slot's resolution window; if it cannot meet the deadline, SHOULD return early with an empty document (E3). |
| **E5** | Player does not implement the SGAI event scheme on the `<EventStream>` (legacy Player encountering a new construct). | Ignore the unknown event and continue primary content uninterrupted. | None. | Broadcaster MUST express every new SGAI construct via an ignore-if-unknown extension point. |
| **E6** | ADS-returned candidate carries no form renderable on the device (no admissible form/layout/device-capability intersection). | Skip the candidate; fall through to the next candidate in declared order. If exhausted, fall through to primary content. | Surface a non-normative "candidate-skipped" event. | ADS SHOULD return at least one candidate with a broadly renderable form (e.g. video) so that fall-through-to-primary is the worst case. |
| **E7** | Candidate declares a layout name not in the Broadcaster's allowed set or not in the IAB-defined enumeration of §3.2. | Reject the form; evaluate other forms on the same candidate. If no admissible form remains, treat as E6. | Log the layout name and the rejection reason. | Broadcaster MUST declare allowed layouts using IAB-defined names. ADS MUST NOT emit form metadata for layouts outside §3.2. |
| **E8** | Cumulative declared duration would exceed the cap if the next candidate is added ("drop before play"). | MAY drop the offending candidate. MUST NOT re-order, deduplicate, or rearrange remaining candidates. | Drop only the candidate that pushes the sum past the cap, or drop all subsequent candidates — both conforming. | Broadcaster MUST declare `@maxDuration` on every slot. ADS is not required to respect the cap. |
| **E9** | Actual rendered length of an accepted candidate exceeds its declared duration, pushing cumulative slot duration past the cap ("trim during play"). | Stop rendering exactly at the cap boundary, even mid-ad. MUST NOT extend past the cap. MUST stop firing tracking beacons at the trim boundary. | Surface a non-normative "slot-trimmed" event. | ADS / Broadcaster MUST NOT rely on declared duration matching actual length for cap arithmetic. |
| **E10** | Ad media segment fetch fails during playback (HTTP 4xx/5xx, timeout, decoder error, DRM key-exchange failure on an ad asset). | Abort the current candidate. Resume the slot at the next candidate in declared order and re-apply cap arithmetic against rendered-so-far. If no candidates remain, fall through to primary content. | Surface a non-normative "candidate-failed" event. MAY tear down the entire slot per Player policy. | ADS SHOULD point at CDNs with availability comparable to the Broadcaster CDN. |
| **E11** | Tracking beacon delivery fails (HTTP error, timeout, DNS failure on a callback URL). | Continue playback uninterrupted. Beacon failures MUST NOT abort the candidate or the slot. | Retry with bounded backoff; log for diagnostics. Surface failures via an implementation-defined API. | ADS / Broadcaster MUST NOT depend on beacon delivery for state correctness. |
| **E12** | Unknown vendor namespace or unrecognised extension element. | Safely ignore. MUST NOT abort the candidate or the slot. | Pass the ignored data verbatim to the application layer for opportunistic consumption. | ADS / Broadcaster MAY use vendor namespaces for application metadata that has no native carrier; MUST NOT rely on Player consumption. |

#### 8.1.1 Order of precedence

When more than one row applies to the same candidate or
exchange, the Player applies them in this order
(short-circuit at the first match):

1. Transport (E1 before E10).
2. Resolution-document level (E2, E3, E4) before any
   per-candidate evaluation.
3. Constraint surfacing (E5, E7) before per-candidate device
   evaluation.
4. Per-candidate decode-time (E6) before any duration evaluation.
5. Per-candidate playback-time (E8 before E9; E10 preempts E9 on
   the affected candidate).
6. Tracking failures (E11, E12) are evaluated independently and
   do not influence slot outcome.

#### 8.1.2 Fall-through definition

"Fall through to primary content uninterrupted" means: no visible
artefact (no freeze, no blank slate, no error overlay unless the
embedding application has opted in via an implementation-defined
API); no tracking beacon fired for the failed slot; primary
playback continues from the position it would have held had the
SGAI event not existed. For `<ReplacePresentation>` slots
specifically, "uninterrupted" means the playhead continues
advancing on the main timeline at wall-clock pace; the Player
does not pause main media time waiting for an ADS response that
ultimately failed.

#### 8.1.3 Surfacing errors to the application layer

The Player MAY expose any of the error events above to the
embedding application via an implementation-defined API (e.g. a
JavaScript event on a web Player, a delegate callback on a
native SDK). The API shape is non-normative and out of scope.
Categories that typically benefit from application surfacing
include: E3 (no-fill), E9 (slot-trimmed), E10 (candidate-failed).

### 8.2 Tracking-only ads (no `<MediaFile>` in VAST input)

A VAST `<Ad>` with no `<MediaFile>` cannot be synthesised into a
resolution document with a renderable form. The ADS adapter has
two policies:

- **Silent skip**. The ADS omits the entry from the resolution
  document. The Player never sees it.
- **Empty document with tracking sidecar**. The ADS emits the
  callback `<Event>` entries inside `<svta:Metadata>` (§5.5.3
  case (b)) and emits the `<Period>` with no `<svta:RenderableAsset>`
  and no `<ImportedMPD>` — which is non-conformant per §5.2.2,
  so this policy is not admissible under this specification.

ADS adapters SHOULD adopt silent skip until a normative carrier
for tracking-only ads is added in a future edition.

### 8.3 Late callbacks

Tracking beacons that the Player attempts to fire after the
ad has trimmed (E9) MUST NOT be sent. The Player's beacon
schedule is anchored to the slot window, not to the ad's
internal duration; once the slot trims, the beacon schedule
terminates.

Beacons that fail to fire on time due to transient network
failures (E11) MAY be retried inside the slot window with a
bounded backoff. Beacons MUST NOT be deferred past the slot
window — a late impression is worse than no impression for the
Broadcaster's bookkeeping.

### 8.4 Device-class fallbacks (open questions for this edition)

Three behaviours are under-determined by the normative chapters
and are flagged here for implementations to resolve consistently:

1. **D3 / D4 hybrid (UC-04)**. Whether the Player MAY composite
   an HTML / image overlay on top of a linear ad's video on
   single-decoder devices with HTML/image surfaces is an open
   question. The conservative default in this edition is to
   decline the overlay portion of a hybrid break on D3 / D4.
   Implementations MAY opt to render the overlay if they are
   confident the on-screen result is clean; the spec does not
   forbid it but does not require it either.
2. **D3 / D4 pause-ad video re-tasking (UC-05)**. Whether the
   single decoder MAY be re-tasked to play a video form on top
   of a paused primary frame, while preserving the paused
   position, is an open device-capability question. The
   conservative default is to skip the video form on
   single-decoder devices in pause-ad scenarios.
3. **D5 always-skip impression accounting**. Whether the
   Player should still issue the ADS resolution request on D5
   (and other always-skip device classes) for impression
   accounting and frequency-capping signals is a privacy /
   bandwidth trade-off this edition does not resolve. Both
   "skip the request entirely" and "issue the request, discard
   the response" are conforming behaviours; implementations
   SHOULD choose deterministically per deployment.

### 8.5 Speculative pre-fetch for pause ads

For `<svta:PauseAdTrigger>` with `@earliestResolutionTimeOffset > 0`,
the Player MAY speculatively pre-fetch the resolution document
ahead of the window opening, so that the pause→render latency is
minimised. The Broadcaster SHOULD weigh the latency benefit
against the privacy implications of an ADS request the viewer
never sees (the pause may never happen). The default for this
edition is `@earliestResolutionTimeOffset = 0` (no speculative
pre-fetch), which defers the request to the pause instant.

### 8.6 Cross-edition compatibility (forward compatibility)

A Player implementing edition N+1 SHOULD recognise both `:N:` and
`:N+1:` versions of the URIs of chapter 2. When both versions
coexist in the same Period (Broadcaster authors a slot in dual
form for backward compatibility), the Player SHOULD prefer the
`:N+1:` version and ignore the `:N:` version, unless the
edition-specific compatibility rules say otherwise. The
authoring rule for cross-edition compatibility lives outside
this edition's normative content.

---

## Annex A — UC-01: Pre-roll (linear)

(Informative walk-through.)

### A.1 Scenario

The user starts playback. The Broadcaster declares a pre-roll
slot at `presentationTime=0` of bounded duration. The ADS returns
a single linear candidate; the Player renders it before the
primary content begins.

### A.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:up="urn:mpeg:dash:schema:urlparam:2025"
     type="dynamic"
     minimumUpdatePeriod="PT2S"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:advanced-linear:2025">

  <EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025">
    <up:UrlParamInfo includeInRequests="altmpd"
                     queryTemplate="session_id=$urn:mpeg:dash:state:cmcd#sid$"/>
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

### A.3 Resolution document (ListMPD)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-05-14T12:00:00Z">

  <BaseURL>https://ads.example.com/delivery/</BaseURL>

  <Period id="ad_01" duration="PT15S">
    <ImportedMPD uri="creative_101.mpd"
                 earliestResolutionTimeOffset="0"/>
  </Period>

</MPD>
```

### A.4 Sub-MPD (SPS profile)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S"
     publishTime="2026-05-14T12:00:00Z">

  <Period id="1" duration="PT15S" start="PT0S">

    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="10">https://tracker.example.com/impression?ad=101</Event>
      <Event presentationTime="0"     id="11">https://tracker.example.com/start?ad=101</Event>
      <Event presentationTime="3750"  id="12">https://tracker.example.com/firstQuartile?ad=101</Event>
      <Event presentationTime="7500"  id="13">https://tracker.example.com/midpoint?ad=101</Event>
      <Event presentationTime="11250" id="14">https://tracker.example.com/thirdQuartile?ad=101</Event>
      <Event presentationTime="15000" id="15">https://tracker.example.com/complete?ad=101</Event>
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

### A.5 Per-device walk-through (D1–D5)

- **D1**. Player selects the single linear candidate; renders the
  video form on a decoder. Cap enforced at playback. Primary
  starts from first frame after the ad completes.
- **D2**. Same as D1. The absence of non-video overlay capability
  is irrelevant for a linear-only slot.
- **D3**. Single decoder reused sequentially (ad, then primary).
  Same observable outcome as D1.
- **D4**. Same as D3.
- **D5**. Same as D3. Linear ads are sequential, not concurrent;
  no overlay capability needed.

---

## Annex B — UC-02: Mid-roll (linear)

(Informative walk-through.)

### B.1 Scenario

While the viewer is watching primary content, the Broadcaster has
declared a mid-roll slot at `presentationTime=PT6M`. The slot
replaces 30 seconds of primary with the ad and transitions back
near the slot position.

### B.2 Main MPD (relevant excerpt)

```xml
<EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
             timescale="1000">
  <Event id="102" presentationTime="360000" duration="30000">
    <ReplacePresentation url="https://ads.example.com/decision/midroll"
                         earliestResolutionTimeOffset="60000"
                         maxDuration="30000"
                         returnOffset="0"
                         clipDuration="30000"
                         startWithOffset="false"/>
  </Event>
</EventStream>
```

### B.3 Resolution document (ListMPD)

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list" publishTime="2026-05-14T12:06:00Z">
  <BaseURL>https://ads.example.com/delivery/</BaseURL>
  <Period id="ad_02" duration="PT30S">
    <ImportedMPD uri="creative_102.mpd"
                 earliestResolutionTimeOffset="60"/>
  </Period>
</MPD>
```

### B.4 Sub-MPD

Mirrors Annex A.4 with a 30-second video and beacons at 0 /
7500 / 15000 / 22500 / 30000 ms.

### B.5 Per-device walk-through

- **D1**. Player switches the primary decoder to the ad track at
  the slot's `presentationTime`. Second decoder MAY pre-buffer
  the ad while the first finishes the last frames of primary;
  this is a Player implementation detail. On completion, resume
  at `presentationTime + @returnOffset = 360000` ms on the main
  timeline.
- **D2**. Same as D1; the second decoder MAY pre-buffer.
- **D3**. Single decoder reused sequentially. Same outcome.
- **D4**. Same as D3.
- **D5**. Same as D3.

---

## Annex C — UC-03: Coexisting overlay (MULTI-FORM SHOWCASE)

(Informative walk-through. **This annex showcases multi-form /
multi-layout candidates** per the requirement that at least one
annex demonstrate device-aware ad selection over a candidate
carrying multiple admissible forms.)

### C.1 Scenario

While the viewer is watching primary content, the Broadcaster has
declared a coexisting overlay slot at `presentationTime=PT2M` of
30 seconds. The slot permits the `overlay-corner` and
`overlay-lower-third` layouts. The ADS returns two candidates;
the first candidate carries three renderable forms (video,
HTML, image) with priority hints; the second is a fallback
image-only candidate.

### C.2 Main MPD (relevant excerpt)

```xml
<EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
             timescale="1000">
  <Event id="201" presentationTime="120000" duration="30000">
    <svta:OverlayPresentation
        xmlns:svta="urn:svta:dash:sgai:2026"
        url="https://ads.example.com/decision/overlay-mid"
        earliestResolutionTimeOffset="10"
        maxDuration="30000">
      <svta:AllowedLayouts>
        <svta:Layout name="overlay-corner"/>
        <svta:Layout name="overlay-lower-third"/>
      </svta:AllowedLayouts>
      <svta:Concurrency max="1"/>
    </svta:OverlayPresentation>
  </Event>
</EventStream>
```

### C.3 Resolution document (overlay-aware)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-05-14T12:02:00Z">

  <BaseURL>https://ads.example.com/delivery/</BaseURL>

  <!-- Candidate 1: multi-form (video + HTML + image), ranked. -->
  <Period id="cand_1" duration="PT30S">
    <!-- Video form via SPS sub-MPD. -->
    <ImportedMPD uri="cand_1_video.mpd"
                 earliestResolutionTimeOffset="0"/>
    <!-- HTML form (highest priority among non-video). -->
    <svta:RenderableAsset
        mediaType="text/html"
        layout="overlay-lower-third"
        src="cand_1.html"
        priority="10"
        width="640" height="180"/>
    <!-- Image form (fallback for HTML-incapable devices). -->
    <svta:RenderableAsset
        mediaType="image/png"
        layout="overlay-corner"
        src="cand_1.png"
        priority="20"
        width="320" height="180"/>
    <!-- Application metadata: click + ad-system. -->
    <svta:Metadata>
      <svta:Click uri="https://landing.example.com/cand_1"
                  trackingUri="https://tracker.example.com/click?ad=201_1"/>
      <svta:AdSystem>example-dsp</svta:AdSystem>
      <svta:AdTitle>Example campaign — May 2026</svta:AdTitle>
      <svta:UniversalAdId idRegistry="ad-id.org"
                          idValue="ABC123XYZ001"/>
    </svta:Metadata>
  </Period>

  <!-- Candidate 2: image-only fallback. -->
  <Period id="cand_2" duration="PT30S">
    <svta:RenderableAsset
        mediaType="image/jpeg"
        layout="overlay-corner"
        src="cand_2.jpg"
        priority="10"
        width="320" height="180"/>
    <svta:Metadata>
      <svta:Click uri="https://landing.example.com/cand_2"/>
    </svta:Metadata>
  </Period>

</MPD>
```

### C.4 Video sub-MPD for Candidate 1

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S"
     publishTime="2026-05-14T12:02:00Z">
  <Period id="1" duration="PT30S" start="PT0S">

    <!-- Beacons timed against the slot window (30s overlay), not the ad's intrinsic duration. -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="20">https://tracker.example.com/impression?ad=201_1</Event>
      <Event presentationTime="7500"  id="21">https://tracker.example.com/firstQuartile?ad=201_1</Event>
      <Event presentationTime="15000" id="22">https://tracker.example.com/midpoint?ad=201_1</Event>
      <Event presentationTime="22500" id="23">https://tracker.example.com/thirdQuartile?ad=201_1</Event>
      <Event presentationTime="30000" id="24">https://tracker.example.com/complete?ad=201_1</Event>
    </EventStream>

    <AdaptationSet mimeType="video/mp4" codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <Representation id="v1" bandwidth="2500000" width="640" height="360">
        <BaseURL>media/cand_1.mp4</BaseURL>
        <SegmentBase indexRange="0-850"/>
      </Representation>
    </AdaptationSet>
  </Period>
</MPD>
```

### C.5 Per-device walk-through

For each device class, the Player applies the §7.3 algorithm to
Candidate 1; if Candidate 1 fails the device, the Player falls
through to Candidate 2; if both fail, the Player declines the
opportunity gracefully.

- **D1** (2+ decoders, HTML + image surfaces). For Cand_1: video
  form is renderable on a second decoder, HTML form is renderable
  via HTML surface, image form is renderable via image surface.
  All three pass device filtering. Layout filtering passes
  (lower-third and corner are both in `<svta:AllowedLayouts>`).
  Priority ordering: HTML (`@priority=10`) outranks image
  (`@priority=20`). The video form has no `@priority` on its
  `<ImportedMPD>` carrier; the Player MAY treat its priority as
  the default `1000` or apply a device-specific tie-break
  defaulting to the lowest-priority form. The choice is
  deterministic per Player. On a typical D1 the Player picks the
  HTML form (best fidelity, no decoder pressure). The HTML
  overlay is composited via the HTML surface; impression beacon
  fires at the instant the overlay becomes visible.
- **D2** (2 decoders, no HTML / image surfaces). For Cand_1:
  video form is renderable on the second decoder; HTML / image
  forms are unrenderable (no overlay surfaces). After filtering,
  only the video form survives; the Player picks it and
  composites it on the second decoder. (Layout
  `overlay-lower-third` or `overlay-corner` is rendered as a
  spatial subset of the video-on-video composition; the IAB
  vocabulary describes the visual expectation, the CSS / HTML
  layout layer in the Player handles the position.)
- **D3** (1 decoder, HTML + image surfaces). For Cand_1: video
  form is unrenderable (single decoder is busy with primary);
  HTML form is renderable; image form is renderable. Priority
  filter picks HTML. The HTML overlay is composited via the HTML
  surface. Same impression/quartile beacon schedule as D1.
- **D4** (1 decoder, image only). For Cand_1: video form
  unrenderable; HTML form unrenderable; image form renderable.
  The image form is selected (`overlay-corner`). Beacons fire at
  the slot window quartiles.
- **D5** (1 decoder, no overlay). For Cand_1: every form is
  unrenderable. The Player skips Cand_1 (§7.3 step 3.e). For
  Cand_2: the image form is also unrenderable. The Player
  declines the opportunity gracefully (§7.7). Primary continues
  uninterrupted. No beacon fires.

This per-device walk-through demonstrates: (i) the candidate
carries multiple admissible forms; (ii) the Player resolves
form selection per device capabilities × Broadcaster-allowed
layouts × ADS priority hints; (iii) skipping is a graceful
outcome and never a failure.

---

## Annex D — UC-04: Hybrid linear + overlay

(Informative walk-through.)

### D.1 Scenario

A mid-content slot at `presentationTime=PT10M` carries a linear
ad take-over (60 seconds) and a coexisting overlay (60 seconds,
banner only). The two events co-locate at the same
`presentationTime`; the Player resolves each against its own
ADS endpoint independently (§7.6).

### D.2 Main MPD (relevant excerpt)

```xml
<Period id="2" start="PT10M">

  <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
               timescale="1000">
    <Event id="402" presentationTime="600000" duration="60000">
      <ReplacePresentation url="https://ads.example.com/decision/midroll-linear"
                           earliestResolutionTimeOffset="60000"
                           maxDuration="60000"
                           returnOffset="0"
                           clipDuration="60000"
                           startWithOffset="false"/>
    </Event>
  </EventStream>

  <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
               timescale="1000">
    <Event id="403" presentationTime="600000" duration="60000">
      <svta:OverlayPresentation
          xmlns:svta="urn:svta:dash:sgai:2026"
          url="https://ads.example.com/decision/midroll-banner"
          earliestResolutionTimeOffset="10"
          maxDuration="60000">
        <svta:AllowedLayouts>
          <svta:Layout name="overlay-corner"/>
        </svta:AllowedLayouts>
        <svta:Concurrency max="1"/>
      </svta:OverlayPresentation>
    </Event>
  </EventStream>

</Period>
```

### D.3 Player behaviour

Per §7.6, the Player issues two independent resolution requests:
one for `event 402` (linear) returning a §5.2.1 ListMPD, one
for `event 403` (overlay) returning a §5.2.2 overlay-aware
document. The two responses are validated and rendered
independently.

### D.4 Per-device walk-through

- **D1**. Linear ad full-screen on decoder 1; banner overlay
  composited via HTML/image surface on top.
- **D2**. Linear ad full-screen on decoder 1; if the overlay
  candidate has a video form on decoder 2, render banner as
  video-on-video. If not (HTML/image only), decline the overlay
  portion; the linear portion renders alone.
- **D3** / **D4**. Conservative default: decline the overlay
  portion when primary "video underneath" is itself an ad on a
  single-decoder device. Render linear only. See §8.4 item 1.
- **D5**. Decline the overlay portion (no overlay capability).
  Render linear only.

---

## Annex E — UC-05: Pause-triggered ad

(Informative walk-through.)

### E.1 Scenario

A window of validity is defined from `presentationTime=0` to
`presentationTime=PT1H` (the entire one-hour primary). If the
viewer pauses inside the window, an overlay ad is composited on
top of the paused primary frame for up to 60 seconds.

### E.2 Main MPD (relevant excerpt)

```xml
<EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026"
             timescale="1000">
  <Event id="301" presentationTime="0" duration="3600000">
    <svta:PauseAdTrigger
        xmlns:svta="urn:svta:dash:sgai:2026"
        url="https://ads.example.com/decision/pause"
        earliestResolutionTimeOffset="0"
        maxDuration="60000">
      <svta:AllowedLayouts>
        <svta:Layout name="pause-ad"/>
      </svta:AllowedLayouts>
      <svta:Concurrency max="1"/>
    </svta:PauseAdTrigger>
  </Event>
</EventStream>
```

### E.3 Resolution document (overlay-aware)

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="list" publishTime="2026-05-14T12:30:00Z">
  <BaseURL>https://ads.example.com/delivery/</BaseURL>
  <Period id="pause_1" duration="PT60S">
    <ImportedMPD uri="pause_1_video.mpd"
                 earliestResolutionTimeOffset="0"/>
    <svta:RenderableAsset
        mediaType="text/html"
        layout="pause-ad"
        src="pause_1.html"
        priority="10"/>
    <svta:RenderableAsset
        mediaType="image/jpeg"
        layout="pause-ad"
        src="pause_1.jpg"
        priority="20"
        width="1920" height="1080"/>
  </Period>
</MPD>
```

### E.4 Per-device walk-through

- **D1**. On pause inside the window, render the highest-fidelity
  form (HTML in this example). Dismiss on resume.
- **D2**. Render the video form on the second decoder while the
  primary decoder holds the paused frame. Non-video forms
  unrenderable on D2 surfaces.
- **D3**. Render the HTML form via the HTML surface (video form
  skipped by §8.4 default).
- **D4**. Render the image form via the image surface (HTML and
  video skipped).
- **D5**. Decline the pause-ad opportunity (no overlay
  capability). Paused frame remains.

---

## Annex F — UC-06: Multi-ad break

(Informative walk-through.)

### F.1 Scenario

The Broadcaster has declared a mid-content slot of bounded
duration that is filled by several ads played back-to-back. How
many ads run inside is an ADS decision; the cap is the only
authoring lever.

### F.2 Main MPD (relevant excerpt)

```xml
<EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
             timescale="1000">
  <Event id="601" presentationTime="900000" duration="90000">
    <ReplacePresentation url="https://ads.example.com/decision/break"
                         earliestResolutionTimeOffset="60000"
                         maxDuration="90000"
                         returnOffset="0"
                         clipDuration="90000"
                         startWithOffset="false"/>
  </Event>
</EventStream>
```

### F.3 Resolution document (ListMPD with three candidates)

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list" publishTime="2026-05-14T12:15:00Z">
  <BaseURL>https://ads.example.com/delivery/</BaseURL>
  <Period id="ad_01" duration="PT30S">
    <ImportedMPD uri="creative_a.mpd"
                 earliestResolutionTimeOffset="0"/>
  </Period>
  <Period id="ad_02" duration="PT30S">
    <ImportedMPD uri="creative_b.mpd"
                 earliestResolutionTimeOffset="30"/>
  </Period>
  <Period id="ad_03" duration="PT30S">
    <ImportedMPD uri="creative_c.mpd"
                 earliestResolutionTimeOffset="60"/>
  </Period>
</MPD>
```

### F.4 Player cap arithmetic

`30 + 30 + 30 = 90` seconds — exactly the cap. Player plays all
three back-to-back. If the actual rendered length of ad_03 runs
over (e.g. encoder slack to 30.5s), the Player trims at the cap
boundary (P-5).

### F.5 Per-device walk-through

- **D1–D5**. All five render the sequence as back-to-back linear
  ads. Multi-decoder devices MAY pre-buffer N+1 while playing N;
  single-decoder devices reuse the decoder sequentially. Same
  observable outcome.

---

## Annex G — UC-07: Legacy Player encounters new constructs

(Informative walk-through.)

### G.1 Scenario

A Player implementation that predates this specification receives
a main MPD containing one or more SGAI constructs introduced by
this specification (e.g. a `<svta:OverlayPresentation>` or a
`<EventStream>` of scheme `urn:svta:dash:sgai-overlay:2026`).
The Player has no awareness of the new semantics.

### G.2 Expected behaviour (uniform across device classes)

- The legacy Player parses the main MPD.
- For unknown `EventStream@schemeIdUri` values, the Player skips
  the entire `<EventStream>` per the §5.10 ignore-if-unknown
  rule. The events inside are never resolved against the ADS.
- For foreign-namespace elements appearing under known DASH
  parents (e.g. `<svta:RenderableAsset>` under `<Period>` in a
  resolution document the legacy Player has nonetheless
  retrieved — which should not happen if the slot was declared
  via a non-linear event scheme, but is possible if the
  Broadcaster also declared the same slot via a known linear
  scheme as a dual-form fallback), the Player discards the
  foreign-namespace element together with its full subtree per
  §5.2.1 NOTE 2 of ISO/IEC 23009-1.
- Primary content continues uninterrupted. No beacon fires. No
  error surfaces.

### G.3 Why this works

The new SGAI mechanisms are expressed exclusively via the
extension points enumerated in chapter 2: foreign-namespace open
content for elements / attributes, new `EventStream@schemeIdUri`
URIs for event schemes, and new profile URIs in `MPD@profiles`
for resolution documents. Every extension point has
ignore-if-unknown semantics defined normatively in MPEG-DASH 6th
edition. The aggregate effect is that legacy Players see the
new constructs as if they were not present.

---

## Annex H — Test cases and conformance criteria summary

(Informative — implementations are encouraged to test against
this set.)

### H.1 Tracking-only VAST input adapter mapping (non-normative)

The mapping below is an illustrative adapter contract that an
ADS deployment MAY follow when it ingests VAST 4.x from upstream
decisioning and emits a resolution document conforming to §5.2.

| VAST 4.x element | Resolution-document target | Notes |
|------------------|----------------------------|-------|
| `<Ad>` (Inline) | one `<Period>` per inline ad | Sequence order preserved. |
| `<Ad>` (Wrapper) | resolved recursively; not directly mapped | Wrapper depth handling is an ADS adapter concern. |
| `<Creatives>/<Linear>/<Duration>` | `Period@duration` | Drives Player cap pre-validation. |
| `<MediaFile>` | `Representation` inside an `AdaptationSet` of the sub-MPD reached via `<ImportedMPD>` | Multiple `<MediaFile>` collapse to an ABR ladder. |
| `<NonLinearAds>/<NonLinear>` (HTML / image creative) | `<svta:RenderableAsset>` with the corresponding `@mediaType` | Per §5.3, non-video forms are carried by the foreign-namespace element. |
| `<TrackingEvents>/<Tracking event="X">` | callback `<Event>` inside an `<EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015">` | Non-linear: place `presentationTime` against the slot window (§5.5.4). |
| `<Impression>` | callback `<Event>` at offset 0 | Fires when overlay becomes visible. |
| `<ClickThrough>` | `<svta:Click @uri>` inside `<svta:Metadata>` | No native DASH carrier; §5.6.3 covers it. |
| `<AdSystem>`, `<AdTitle>` | `<svta:AdSystem>`, `<svta:AdTitle>` inside `<svta:Metadata>` | §5.6.2. |
| `<UniversalAdId>` | `<svta:UniversalAdId>` inside `<svta:Metadata>` | §5.6.4. |
| `<Error>` | translated by ADS into an HTTP error response or an empty resolution document | Player falls through per §8.1 E1 / E3. |

VAST version pinning is intentionally out of scope. This mapping
covers the subset of VAST relevant to the resolution-document
shapes of §5.2; comprehensive VAST coverage is an ADS adapter
concern, not a spec obligation.

### H.2 Conformance test case index

The table below restates the error-semantics rows of §8.1 as
test cases. Each row produces an observable outcome that can be
asserted against a Player implementation.

| Test ID | Construct under test | Trigger | Expected observable outcome |
|---------|----------------------|---------|------------------------------|
| **T-E1** | Player ↔ ADS transport | Issue resolution request against a deliberately unreachable ADS endpoint. | Primary content continues uninterrupted. No beacon fires. |
| **T-E2** | Resolution-document parse | ADS returns malformed XML or an unknown profile URI. | Primary continues. No partial recovery. |
| **T-E3** | Empty resolution document | ADS returns a well-formed document with zero `<Period>`. | Primary continues. No beacon fires. |
| **T-E4** | Late resolution document | ADS replies after `presentationTime`. | Late response discarded. Primary not delayed. |
| **T-E5** | Legacy Player encounters new construct | Author a slot with `<svta:OverlayPresentation>` or a new scheme URI; replay against a Player that does not implement the spec. | Primary continues uninterrupted (UC-07). |
| **T-E6** | Candidate with no renderable form | ADS returns a candidate whose only form is unrenderable on the test device. | Candidate skipped; fall-through to the next candidate or to primary. |
| **T-E7** | Disallowed layout | ADS returns a `<svta:RenderableAsset @layout>` whose value is not in `<svta:AllowedLayouts>`. | Form rejected; evaluate next form. |
| **T-E8** | Drop before play | ADS returns a third candidate whose declared duration would push cumulative past the cap. | Player MAY drop the third candidate. Order of remaining candidates preserved. |
| **T-E9** | Trim during play | Accepted candidate's actual rendered length exceeds its declared duration. | Player stops at the cap, mid-ad. Beacons stop firing at the trim boundary. |
| **T-E10** | Ad segment fetch failure | Ad CDN returns 5xx for a segment of an accepted candidate. | Candidate aborted; next candidate plays (if any); else fall through. |
| **T-E11** | Beacon delivery failure | Tracking endpoint returns 5xx. | Playback continues. Beacon failure non-fatal. |
| **T-E12** | Unknown vendor namespace | Resolution document contains a foreign-namespace element from an unrelated vendor URN. | Foreign element ignored with full subtree. Slot rendering unaffected. |

### H.3 Per-chapter conformance highlights

| Chapter | Principal conformance items |
|---------|------------------------------|
| §4.2 Broadcaster | B-1 declare slot via correct scheme; B-2 `@maxDuration` on every slot; B-3 mandatory `<svta:AllowedLayouts>` / `<svta:Concurrency>` for non-linear; B-4 extension point only; B-5 do not alter baseline; B-6 IAB layout names. |
| §4.3 ADS | A-1 declared profile; A-2 at least one renderable form; A-3 callback-scheme tracking only; A-4 IAB layout names; A-5 / A-6 no enforcement / no device matrix; A-7 honour resolution window. |
| §4.4 Player | P-1 ignore unknown schemes; P-2 resolution windowing; P-3 validate against MPD; P-4 honour ADS order; P-5 cap enforcement against actual length; P-6 form selection algorithm; P-7 skip unrenderable; P-8 drop-before-play; P-9 beacon firing and trim cutoff; P-10 fall-through on error; P-11 ignore unknown extensions; P-12 no VAST dependency. |
| §5 Syntax | Tabular attribute presentation for every new construct; enum tables follow attribute tables. |
| §6 Interfaces | HTTPS transport; one resolution request per activating event; Player ↔ ADS contract identical across linear / non-linear from the wire perspective. |
| §7 Expected behaviour | Normative selection algorithm in §7.3; tracking semantics in §7.5; co-located events in §7.6; per-device matrix in §7.7. |

### H.4 Final notes

This specification is the foundation edition of SGAI for MPEG-DASH
covering linear and non-linear ads under a single three-actor
contract. Items deferred to future editions:

- Post-roll slots.
- Server-side stitching / SSAI integration.
- Companion-ad multi-screen flows.
- Native ads in the Player chrome.
- A dedicated tracking-only-ad carrier (§8.2).
- Per-edition `@includeInRequests` values for the
  `UrlParamInfo` descriptor (§5.7).
- The open device-capability questions in §8.4.

---

*End of specification.*

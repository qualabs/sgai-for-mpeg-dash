# SGAI for Linear and Non-Linear Ads in MPEG-DASH

**Document status.** Candidate specification, build iteration 10. It
becomes the published text only by promotion; until then it is a
candidate like any other.

**Normative language.** The key words "MUST", "MUST NOT", "REQUIRED",
"SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY" and
"OPTIONAL" in this document are to be interpreted as described in
IETF RFC 2119 when, and only when, they appear in all capitals.

**Reading the citations.** "DASH" followed by a clause number (for
example *DASH §5.16.5.2*) refers to the base specification named in
chapter 2. Where this document relies on a sentence of the base
specification it quotes the sentence, because a clause number alone
does not show which rule is meant. A statement about the base
specification that could not be verified against its text is tagged
`[inferred]`.

**Normative and informative content.** Chapters 1 to 7 are normative.
Chapter 8 is informative guidance. The annexes are informative: they
show the normative chapters applied to complete scenarios, and where an
annex and a chapter appear to disagree, the chapter governs.

## Table of contents

1. [Scope](#1-scope)
2. [Normative references](#2-normative-references)
3. [Terms, definitions and abbreviations](#3-terms-definitions-and-abbreviations)
4. [Conformance](#4-conformance)
5. [Syntax](#5-syntax)
6. [Interfaces](#6-interfaces)
7. [Expected behaviour](#7-expected-behaviour)
8. [Implementation notes](#8-implementation-notes)
- Annex A — Pre-roll
- Annex B — Mid-roll
- Annex C — Coexisting overlay (multi-form, multi-layout)
- Annex D — Hybrid: a linear ad with a concurrent overlay
- Annex E — Pause-triggered ad
- Annex F — Multi-ad break
- Annex G — A Player that predates this specification
- Annex H — An overlay window crossing a pause window
- Annex I — One ad, ordered options, resolved across the device classes
- Annex J — Double box, the three-element layout
- Annex K — ClickThrough
- Annex L — Overlapping windows of one family, with fallback
- Annex M — One ad, Player-declared capabilities, resolved by the APS
- Annex N — A non-linear ad over a replacement that is not advertising
- Annex O — Publisher-restricted layouts forwarded to the APS
- Annex P — A `custom` overlay inside a Publisher region
- Annex Q — Test cases and conformance criteria

---

## 1. Scope

### 1.1 What this specification covers

This specification defines **Server-Guided Ad Insertion (SGAI) for both
linear and non-linear ads in MPEG-DASH**, as a complete extension of the
base specification named in chapter 2.

- **Linear SGAI is absorbed as the baseline.** The base specification
  already carries linear SGAI: the alternative-MPD insertion and
  replacement events (`InsertPresentation`, `ReplacePresentation`, DASH
  §5.16) and the List MPD that answers them (DASH §8.14). This
  specification adopts that machinery as it is, states the Player
  obligations the base specification leaves to the client, and adds
  the few clarifications the linear case needs — a declared cap on
  every slot, the ordering of candidates, the tracking and ClickThrough
  carriers.
- **Non-linear SGAI is the principal new content.** Overlays, corner
  and lower-third placements, squeezebacks (L-shape and double box) and
  pause ads have no construct in the base specification. This
  specification defines the opportunity declarations the Publisher
  writes for them, the resolution document the Ad Presentation Server
  returns, the request the Player sends, and the Player behaviour that
  composes the result over the primary content.

The two halves share one architecture: the Publisher declares an
opportunity in the MPD, the Player resolves it against an Ad
Presentation Server, the resolution document carries ordered
candidates, and the Player validates what it receives against what the
Publisher declared before anything reaches the screen.

The specification is written for four readers: the Publisher that
authors MPDs, the operator of an Ad Decision Server, the implementer of
an Ad Presentation Server, and the implementer of a Player.

**The invariant.** Applying this specification never breaks the
playback of the primary content. When an opportunity cannot be
honoured — nothing resolves, nothing is renderable, something fails
mid-ad — the Player skips it and the primary content continues. This is
the base specification's own guarantee for its execution model — *"If
no event can be successfully executed, the playback continues
uninterrupted"* (DASH §5.16.2.2.5), and *"A failed execution results in
smooth continued playback of the main media presentation"* (DASH
§5.16.2.2.6) — extended here to every construct this specification
adds. Within that invariant, when a design choice affects how fully an
opportunity can be used, this specification prefers the choice that
uses it most.

### 1.2 The four actors

Every obligation in this specification binds one of four actors.

| Actor | Owns | Does not own |
|---|---|---|
| **Publisher** | The primary content and the screen. Declares where opportunities are, which family each belongs to, the cap on each, and which layouts each admits. | Which ads fill an opportunity. |
| **Ad Decision Server (ADS)** | The ad decision: how many ads, which ones, in what order, and the tracking schedule. Emits a decision document in its own format — typically VAST, though the ADS is not bound to VAST and MAY emit another format. | Converting its decision into anything the Player reads, and enforcing the Publisher's constraints. |
| **Ad Presentation Server (APS)** | The endpoint the Publisher's opportunity points at. Obtains the decision from the ADS and converts it into the resolution document this specification defines, carrying the ADS's tracking schedule into it. | The ad decision, and enforcing the Publisher's constraints. |
| **Player** | Reading the MPD, resolving opportunities against the APS, validating each candidate against the Publisher's declarations, selecting what its device can render, and composing it on screen. | The ad decision and the tracking schedule. |

The division is what lets one ADS serve many Publishers with different
policies, and lets a Player guarantee a Publisher's constraints when the
ADS and the APS are external services no one audits. The Player never
talks to the ADS: the resolution document is the only thing it reads
about an ad. In deployed systems the APS is often a module of the ADS;
it is described separately here because its responsibilities are
distinct, not because it must be deployed separately.

### 1.3 Out of scope

The following are outside this specification. Each is listed so that
its absence is read as a decision rather than an oversight.

- **A layout engine.** Spatial arrangement inside a layout is delegated
  to HTML5 and CSS and to the IAB-defined layout each token names
  (§3.4). This specification declares no positioning vocabulary of its
  own, with the single exception of the optional `custom` overlay
  layout (§5.3.5), whose rectangle is a position by definition.
- **Position semantics inside a layout** — left, right, top, bottom,
  which corner. They follow from the IAB ad type the layout token names.
- **The ADS's decisioning logic** — targeting, frequency capping, brand
  safety, competitive separation, ordering — and **the APS-to-ADS
  exchange**: its URL, parameters, payloads, decision format and
  version, and the fidelity with which the APS transcribes the decision.
  Those parties agree it bilaterally. This specification defines only
  the Player-visible interface: the opportunity declaration the
  Publisher writes, the resolution request the Player sends, and the
  resolution document the APS returns.
- **Creative carriers other than video, image and HTML.** Raw
  JavaScript, SVG as a payload, PDF and proprietary binary creatives are
  excluded. A scripted creative is wrapped in an HTML document and
  carried as `text/html`.
- **Interactive ad frameworks.** An ad built on a framework such as
  SIMID is delivered by that framework. No layout this edition defines
  carries a SIMID payload.
- **Single-decoder slice or tile replacement**, in which one decoder
  carries both the primary content and the ad. The technique exists in
  the base specification itself: its supplementary video descriptor,
  for VVC, *"enables achieving picture-in-picture using a single VVC
  decoder"*, so that *"separate decoding of the main video and the
  supplementary video"* is avoided (DASH §5.8.5.16.4). This edition's
  decoder-budget reasoning (§5.3.7) assumes one decoder per concurrent
  form, and a later edition may cover the technique.
- **Preventing a viewer from seeking past a non-linear window.** The
  base seek-blocking control `@noJump` is preserved unchanged on the
  inherited linear events, where the ad occupies the timeline. It is
  excluded on the non-linear families (§4.8.9).
- **Linking the two portions of a hybrid break** — for example
  suppressing an overlay when the linear ad beneath it comes from a
  given advertiser. Competitive separation is the ADS's, and enforcing
  it in the Player would require advertiser identity to reach the
  Player (§5.1.6).
- **Ads outside the video surface.** This specification covers only ads
  the Player renders on the playing or paused video. Menu ads,
  home-screen and launcher ads, screen saver ads, companion and
  multi-screen ads, and in-scene ads — a product or sign placed inside
  the scene, which is part of the video frames — are outside it, and no
  layout value covers them.
- **Server-side ad insertion (stitching)** and **post-roll slots.**
- **Reporting transport** for any measurement (§5.9), as for the base
  specification's own metrics.

### 1.4 Relationship to the base specification

**Where the base specification answers a question, its answer is the
one this specification adopts**, and the base clause is cited. This
specification defines its own answer only where the base gives none,
and states it as an extension. Where it departs from a base answer
anyway, the departure is recorded as an exception with its reason
(§4.8.3). A Player implementing this specification and a Player
implementing only the base specification therefore behave the same on
the inherited linear constructs, except where §4.8.3 records otherwise.

**Every construct this specification adds is ignored by a Player that
does not implement it**, and the primary content keeps playing. That
follows from the extension points used (§4.7), each of which the base
specification lets a client ignore. **No construct here obliges a
Player that does not implement this specification**: the base
specification states that *"DASH Client operation is not specified
normatively in this document"* and that *"profiles merely specify
restrictions on MPD and Segments rather than DASH Client behaviour"*
(DASH §8.1, NOTE 1). Every Player obligation in this document binds a
Player conformant to this specification, and only such a Player.

---

## 2. Normative references

The following documents are referred to in the text in such a way that
some or all of their content constitutes requirements of this document.

- **ISO/IEC 23009-1:2026 (Sixth edition, 2026-07)**, *Information
  technology — Dynamic adaptive streaming over HTTP (DASH) — Part 1:
  Media presentation description and segment formats*. Referred to as
  "the base specification" and cited as "DASH §x". Every citation in
  this document is to this edition.
- **IAB Tech Lab, *Ad Format Guidelines for Digital Video and CTV***
  (Final Release, May 2026), the CTV ad-type catalogue. The source of
  every ad type and visual placement accepted in §3.4, and of the
  spatial bound each placement implies. Referenced live, not
  snapshotted:
  https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e ;
  portfolio page https://iabtechlab.com/standards/ctv-ad-portfolio/ .
- **IETF RFC 2119**, *Key words for use in RFCs to Indicate Requirement
  Levels*.
- **IETF RFC 3986**, *Uniform Resource Identifier (URI): Generic
  Syntax* — the query component of the resolution request (§5.8).
- **IETF RFC 4337**, *MIME Type Registration for MPEG-4* — the media
  types a Representation reached through the resolution path may carry.
- **IETF RFC 6381**, *The 'Codecs' and 'Profiles' Parameters for
  "Bucket" Media Types* — `@codecs` values in the examples.
- **W3C HTML Living Standard** and **W3C CSS** — the rendering
  primitives an `html` creative and the spatial arrangement inside a
  layout are delegated to.
- **W3C XML Schema Part 2: Datatypes** — the types in the attribute
  tables (`xs:duration`, `xs:anyURI`, `xs:unsignedLong`, …).

**Informative references.** IAB Tech Lab VAST (Video Ad Serving
Template), version 4.x, is cited as the typical decision format of an
ADS. **No actor is required to use VAST or any particular version of
it**; every mention of VAST in the normative chapters names it as the
typical case, and the field mappings are illustrative (§6.6, Annex A,
Annex C).

### 2.1 URIs this edition introduces

| URI | What it identifies | Defined in |
|---|---|---|
| `urn:svta:dash:sgai:2026` | The XML namespace of every element and attribute this specification introduces. Owned by the SVTA Advertising Working Group, the venue incubating this specification. | §5 |
| `urn:svta:dash:sgai-overlay:2026` | The event scheme of an overlay opportunity window. | §5.1.3 |
| `urn:svta:dash:sgai-pause-trigger:2026` | The event scheme of a pause opportunity window. | §5.1.4 |
| `urn:svta:dash:sgai-resolution:2026` | The request type of the non-linear resolution request, for use in the base specification's `@includeInRequests`. | §5.8.1 |

The `2026` suffix is the edition year. A later edition that changes the
semantics of any of these constructs mints a new URI rather than
reusing one with altered meaning, which is what keeps a Player of this
edition from misreading a later one; a Player implementing a later
edition SHOULD also recognise the URIs of this one.

**URIs this edition reuses rather than introduces:** the linear event
schemes `urn:mpeg:dash:event:alternativeMPD:insert:2025` and
`urn:mpeg:dash:event:alternativeMPD:replace:2025` (DASH §5.16), the List
profile `urn:mpeg:dash:profile:list:2024` (DASH §8.14), the
Single-Period Static profile `urn:mpeg:dash:profile:sps:2024` (DASH
§8.15), the Full profile `urn:mpeg:dash:profile:full:2011` (DASH §8.2),
the callback event scheme `urn:mpeg:dash:event:callback:2015` (DASH
§5.10.4.5) and the URL-parameter scheme `urn:mpeg:dash:urlparam:2025`
(DASH Annex I). **This specification mints no tracking scheme and no
profile.**

---

## 3. Terms, definitions and abbreviations

### 3.1 Terms and definitions

**Ad candidate (candidate).** One ad offered for a slot in a resolution
document. A candidate carries one or more presentation options; the
Player renders at most one of them.

**Ad Decision Server (ADS).** The actor that decides which ads to serve
for an opportunity, how many and in what order, owns the tracking
schedule, and emits its decision in its own format (§1.2).

**Ad Presentation Server (APS).** The actor that answers the Player's
resolution request: it obtains the ADS's decision and converts it into
the resolution document this specification defines (§1.2).

**Ad slot (slot).** What an opportunity window yields when it is
resolved: the stretch of presentation in which the resolved ads are
shown. A viewer dismissal ends a slot (§4.5.14).

**Allowed layouts.** The set of layout tokens a non-linear window
admits: the set the Publisher declares in `@allowedLayouts`, or, when
it declares none, the family default of §3.4.3.

**Base specification.** ISO/IEC 23009-1:2026, the standard this
specification extends. "Base" is used where the point is that a rule
comes from that standard and not from this one.

**Cap.** The maximum a Publisher declares on every slot, in
`@maxDuration`. What it bounds depends on the family (§4.5.4): on a
linear replacement slot, *until when* the presentation may run; on a
linear insertion slot and on an overlay slot, the cumulative duration of
what the slot presents; on a pause slot, nothing, because the viewer
sets its length.

**Capability parameter.** One of the reserved query parameters a Player
MAY attach to the resolution request to state what its device can
render (§5.8.2). An absent capability parameter means its value is
undetermined.

**Custom region.** A rectangle, in percent of the video viewport, within
which a `custom` overlay must lie (§5.3.5).

**Document order.** The order in which elements appear in a document as
written, which is the order an XML parser reports them. Wherever a list
in this specification expresses preference, the first element in
document order is the most preferred, and no attribute carries a
separate ranking.

**Dismissal.** A viewer action that ends a whole ad slot before its
presentation would otherwise end (§4.5.14).

**Double box.** The squeezeback layout in which the shrunk primary
content and the ad occupy two boxes side by side, leaving bands
uncovered; the side-by-side layout of industry usage.

**Empty resolution.** A resolution document that is well-formed and
complete and carries no candidate (§5.2.3). It expresses an opportunity
that resolved to no ads.

**Failed execution.** An attempt on a window that produces no ad: no
resolution document obtained, a document that cannot be parsed, an
empty resolution, or a document of the wrong family (§4.5.6). The term
and its consequence are the base specification's (DASH §5.16.2.2.6).

**Family.** A kind of ad opportunity. There are three: **linear**,
**overlay** and **pause**. The family of a window is given by its event
scheme (§5.1). Overlay and pause together are the **non-linear**
families.

**Form.** The creative-carrier type of a presentation option: `video`,
`image` or `html` (§3.5).

**L-shape.** The squeezeback layout in which one full-frame ad creative
fills the background and the shrunk primary content is composited on
top of it; the visible band of the creative around the content forms
the "L".

**Layout.** The on-screen arrangement a presentation option uses,
named by one layout token of §3.4.

**Layout token.** One value of the closed vocabulary of §3.4.2.

**Legacy Player.** A Player conforming to the base specification that
does not implement this specification. It is a class of implementation,
not a mode: no Player announces itself as legacy.

**Linear ad.** An ad whose form takes over the primary content surface
for the slot.

**List MPD.** The resolution document of the linear family, conforming
to the List profile of the base specification (DASH §8.14).

**Non-linear ad.** An ad that coexists with the primary content —
composited over it, or sharing the frame with it — or that is shown over
the paused primary frame.

**Non-linear resolution document.** The resolution document of the
overlay and pause families (§5.2.2).

**Opportunity window (window).** An `<Event>` in the main MPD declaring
an ad opportunity of one family. Its `@presentationTime` and `@duration`
bound the region of the primary timeline it covers.

**Overlay.** Used in two senses that this document keeps apart. As a
**family**, the non-linear opportunities presented while the primary
content plays. As a **layout token** (`overlay`), one arrangement of the
overlay family: a surface composited over the playing primary content
with no named placement. The document states which sense a sentence
takes wherever both readings are possible.

**Pause window.** An opportunity window of the pause family: the region
of the primary timeline in which a viewer pause triggers a resolution
request. It bounds where, not how long (§4.5.10).

**Presentation option (option).** A pairing of a form and a layout,
offered on a candidate. A candidate carries its options as an ordered
list (§5.3).

**Presentation timeline.** The media timeline of whatever the Player is
presenting. Durations, caps and beacon times in this specification are
measured on it, not on the wall clock.

**Primary content.** The programme the viewer chose — the film, the
episode, the live channel — as distinct from any ad.

**Resolution document.** The document the APS returns when the Player
resolves a window's URL. It is the only thing the Player reads about an
ad.

**Resolution request.** The HTTP GET the Player issues against a
window's `@uri` (§5.8).

**Squeezeback.** A non-linear layout in which the primary content is
shrunk to share the frame with the ad rather than being covered by it.

**Sub-MPD.** An MPD, conforming to the Single-Period Static profile
(DASH §8.15), that carries one video creative.

**Undetermined.** The value of a capability parameter the Player did not
send (§5.8.4).

**Usable lifetime.** How long a non-linear resolution document remains
usable after the Player received it (§5.2.5).

### 3.2 Abbreviations

| Abbreviation | Expansion |
|---|---|
| ADS | Ad Decision Server |
| APS | Ad Presentation Server |
| CTV | Connected TV |
| ERT | Earliest Resolution Time (DASH §5.16.2.1) |
| HTML | HyperText Markup Language |
| IAB | Interactive Advertising Bureau (IAB Tech Lab) |
| MPD | Media Presentation Description |
| PRT | Presentation time of an event (DASH §5.16.2.1) |
| SGAI | Server-Guided Ad Insertion |
| SPS | Single-Period Static profile (DASH §8.15) |
| SVTA | Streaming Video Technology Alliance |
| URN | Uniform Resource Name |
| VAST | Video Ad Serving Template (IAB Tech Lab) |
| VOD | Video on demand |

### 3.3 The three families

| Family | Declared by | What the primary content does | Resolution document |
|---|---|---|---|
| **Linear** | `<InsertPresentation>` or `<ReplacePresentation>` in an alternative-MPD event (DASH §5.16) | Stops (insertion) or keeps advancing unseen (replacement) while the ad takes the screen | List MPD (§5.2.1) |
| **Overlay** | `<svta:OverlayPresentation>` in an event of scheme `urn:svta:dash:sgai-overlay:2026` | Keeps playing; the ad is composited over it or shares the frame | Non-linear resolution document (§5.2.2) |
| **Pause** | `<svta:PauseAdPresentation>` in an event of scheme `urn:svta:dash:sgai-pause-trigger:2026` | Is paused by the viewer; the ad is shown over or in place of the paused frame | Non-linear resolution document (§5.2.2) |

### 3.4 Accepted ad types and layout tokens (normative)

Ad types and their visual placements are **defined and maintained by
the IAB**, in the catalogue named in chapter 2. This specification
defines no ad-type category and no visual template. It accepts a
**closed, edition-scoped subset** of the IAB catalogue: the tokens in
§3.4.2 are the complete set a conformant Publisher, APS and Player
handle under this edition.

**The subset is a snapshot per edition, by design.** An IAB ad type or
placement not listed here is out of scope for this edition, and one the
IAB publishes later does not enter scope automatically: widening the set
requires a new edition of this specification.

#### 3.4.1 The IAB ad types, and which are accepted

| IAB ad type | Accepted | Why |
|---|---|---|
| Linear Ad | Yes — `linear` | A full-viewport ad that takes over the primary content surface for the slot. Pre-roll, mid-roll and multi-ad breaks are timing positions of the one type; the full-screen takeover offered as the last option of a non-linear candidate is a placement of `linear`, not a separate type. |
| Overlay | Yes — `overlay`, `overlay-corner`, `overlay-lower-third` | Composited over the playing content, which is not resized. |
| Squeezeback | Yes — the four `squeezeback-*` tokens | The content is resized to share the frame; no content is covered. The IAB *Frame* placement is not among the accepted ones. |
| Pause Ad | Yes — `pause-fullscreen`, `pause-partial` | Shown while the content is paused. |
| Menu Ad | No | Rendered in the platform interface, not on the video. |
| Screen Saver Ad | No | Initiated by the device after inactivity, not on the video. |
| Companion Ad | No | Rendered outside the player. |
| In Scene Ads | No | Part of the video frames, not rendered over them. |

#### 3.4.2 The layout tokens

These are the only values a Publisher writes in `@allowedLayouts` and
the only values an APS writes in an option's `@layout`. Every token
except `custom` names exactly one IAB ad type or visual placement.

| Token | Family | IAB ad type / placement | What the Player composes | Spatial bound (IAB) |
|---|---|---|---|---|
| `linear` | linear; admissible on an overlay window when listed | *Linear Ad* | The ad takes over the full viewport; the primary content is not shown | The full video viewing pane |
| `overlay` | overlay | *Overlay*, no named placement | A surface over the playing primary content, which is not transformed | As the IAB Overlay definition |
| `overlay-corner` | overlay | *Overlay — Corner Overlay* | A surface in a corner of the frame; which corner follows from the creative | 25 % of the frame |
| `overlay-lower-third` | overlay | *Overlay — Lower Third Overlay* | A surface across the bottom of the frame | 30 % of the bottom of the frame |
| `squeezeback-l-shape-upper-left` | overlay | *Squeezeback — L-Shape* | Primary content shrunk into the **upper-left** 60 % of the frame; the full-frame creative shows across the bottom and up the right edge | Primary content 60 % of the frame |
| `squeezeback-l-shape-upper-right` | overlay | *Squeezeback — L-Shape* | Primary content shrunk into the **upper-right** 60 % of the frame; the creative shows across the bottom and up the left edge | Primary content 60 % of the frame |
| `squeezeback-double-box` | overlay | *Squeezeback — Double Box Video* | Primary content in the centre-left box, the ad in the centre-right box, each 25 % of the frame; the uncovered bands render black | Each box 25 % of the frame |
| `squeezeback-double-box-background` | overlay | *Squeezeback — Double Box Video + Background* | As `squeezeback-double-box`, with an advertiser-branded background image filling the uncovered bands | Each box 25 % of the frame |
| `pause-fullscreen` | pause | *Pause Ad — Fullscreen* | The ad occupies the whole screen surface | The full screen |
| `pause-partial` | pause | *Pause Ad — Partial Screen* | The ad is composited over the paused primary frame, which stays visible around it | A partial-screen unit |
| `custom` | overlay (optional) | none | An overlay placed in the rectangle the option carries, inside the slot's custom region (§5.3.5) | The declared custom region |

**The squeezeback token carries the geometry because nothing else
does.** In a squeezeback the Player shrinks and repositions the primary
content, which it does for no other layout, so it needs the region
before it composes. The creative arrives in the IAB underlay format — a
full-frame image with a cutout for the content — and a hole in an image
is not a rectangle a Player can compute with; the IAB guidelines define
no field that carries one. The two orientations of the L-shape are
therefore two tokens: they are two compositions. This is not a
positioning vocabulary: what the token enumerates is which composition
is in play, not where anything sits inside it.

**Which corner an `overlay-corner` occupies is not a token.** The
Player composites the creative over primary content it does not
transform, so the corner follows from the creative and is rendered with
HTML5 and CSS.

**`pause` and `squeezeback` alone are not tokens.** Neither says which
composition the Player builds: every pause ad is fullscreen or partial,
and every squeezeback is one of the four named ones. Keeping the pause
surfaces apart is also what lets a Publisher admit one and exclude the
other.

**The spatial bounds are inherited by reference.** Each accepted
placement implies the bound the IAB guidelines declare for it, as the
table records. This specification does not re-declare those bounds on
the slot and introduces no dimensional attribute: the bound is a
property of the IAB placement the token names, and a second copy on the
MPD side would be a second source of truth for one value.

**`custom` is the one exception** to the IAB mapping and to the absence
of positions. It has no IAB counterpart, it is optional for every actor,
and it applies to the overlay family only (§5.3.5).

**Tokens outside this table are not admissible anywhere**, including
Publisher-private layout names and IAB placements the table does not
list.

#### 3.4.3 The family default

A non-linear window that declares no `@allowedLayouts` admits exactly
the tokens of its own family:

| Window | Admitted when `@allowedLayouts` is absent |
|---|---|
| Overlay | `overlay`, `overlay-corner`, `overlay-lower-third`, `squeezeback-l-shape-upper-left`, `squeezeback-l-shape-upper-right`, `squeezeback-double-box`, `squeezeback-double-box-background` |
| Pause | `pause-fullscreen`, `pause-partial` |

The default admits no token of another family — an overlay window that
declares nothing does not admit the `linear` full-screen takeover — and
it does not admit `custom`, which a window admits only by listing it.
Linear windows carry no allowed-layout declaration: their only form is
the linear one.

### 3.5 Creative-carrier forms

The admissible creative carriers are **exactly three**. No annex,
example or note of this document adds another.

| Form | What it carries | Media types |
|---|---|---|
| `video` | An ISO-BMFF video creative described by a sub-MPD conforming to the Single-Period Static profile (§5.4) | Representations carry `video/mp4`, `audio/mp4` or `application/mp4`, per RFC 4337 |
| `image` | A still image, in the formats the IAB ad templates define for image creatives; the catalogue names JPEG, PNG and GIF | `image/jpeg`, `image/png`, `image/gif` |
| `html` | An HTML document. It MAY contain inline `<script>`, which runs under the device's HTML capability contract and is not a separate carrier | `text/html` |

### 3.6 Device classes

A device class captures only the rendering capabilities that decide
what this specification's layouts cost: how many video decoders the
device runs concurrently, and which kinds of surface it can composite on
top of video. Codec support, DRM and network conditions are orthogonal
and are handled elsewhere in the Player.

| Class | Concurrent video decoders | Image over video | HTML over video | Video over video |
|---|---|---|---|---|
| **D1** — top tier | 2 or more | yes | yes | yes |
| **D2** | 2 | no | no | yes |
| **D3** | 1 | yes | yes | no |
| **D4** | 1 | yes | no | no |
| **D5** — worst case | 1 | no | no | no |

**Expected behaviour per class and opportunity type.** Every class has
a defined outcome for every opportunity type: render, fall back to a
later option, or skip and continue with the primary content. The table
summarises the dominant outcome; §5.3.7 gives the rule that produces
each cell, and the annexes walk them.

| Opportunity | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|
| Linear slot — pre-roll, mid-roll, multi-ad break | Linear ad(s) | Linear ad(s) | Linear ad(s) on the one decoder | Same as D3 | Same as D3 |
| Overlay window | First option in order: video, image or HTML overlay, or a squeezeback | Video overlay; a double box or L-shape with a video creative; otherwise skip | Image or HTML overlay; squeezeback with an image or HTML creative | Image overlay; squeezeback with an image creative | Skip, unless the window admits `linear` and the candidate offers it |
| Pause window | Any pause form | Video pause ad | Image or HTML pause ad; a fullscreen video pause ad if the Player re-tasks its decoder | Image pause ad; a fullscreen video pause ad as for D3 | A fullscreen video pause ad (decoder re-tasked); otherwise skip |
| Hybrid — linear slot with a concurrent overlay window | Linear ad plus overlay | Linear ad plus a video overlay; otherwise linear only | Linear ad plus an image or HTML overlay | Linear ad plus an image overlay | Linear ad only |
| Overlay window crossing a pause window | Overlay suspended for the pause ad, restored on resume | Same, with a video pause ad | Same, with an image or HTML pause ad | Same, with an image pause ad | Neither renders unless a fullscreen video pause ad is offered |
| Overlay window admitting `custom` | As the overlay row, with the `custom` option rendered where the Player supports `custom` and the rectangle is inside the region; otherwise the next option | Same | Same | Same | Skip |
| Overlapping windows of one family | Window selection and fallback identical on every class; what renders is the chosen window's row | Same | Same | Same | Same |
| ClickThrough on any ad | Identical on every class: the outcome depends on the input mechanism, not on decoders or surfaces | Same | Same | Same | Same |
| Any opportunity, Player that does not implement this specification | Primary content continues; the opportunity is ignored | Same | Same | Same | Same |

**D2 is the instructive class.** It owns two decoders, yet cannot render
an image or HTML surface over video, so an option whose creative or
background is a still image fails on D2 however many decoders it has.
The rule is the element **type**, not only the element **count**.

**A single-decoder device can present a video pause ad.** A pause is
what the viewer experiences — the content stopped where they stopped it
and continues from there — and a Player MAY achieve it by releasing the
primary content's decoder and restoring the content at the suspended
position (§4.5.10). The D3–D5 cells of the pause row describe that
choice; a Player that keeps the decoder holding the paused frame and
presents only non-video pause forms is equally conformant.

---

## 4. Conformance

### 4.1 What conformance means here

An implementation claims conformance **per actor**: as a Publisher, an
ADS, an APS or a Player, and it satisfies every obligation of §4.2 to
§4.5 addressed to that actor. The obligations are stated positively —
what the actor does — and what lies outside an obligation is outside the
contract.

**What a Publisher's and an APS's conformance is checked against.** The
documents they produce: the main MPD for the Publisher, the resolution
document for the APS. An APS obligation is checked against the
resolution document alone, which is the only artefact on the path to
the Player that this specification defines; what the ADS decided, and
how faithfully the APS transcribed it, belongs to the APS-to-ADS
contract, which those parties maintain directly.

**What a Player's conformance is checked against.** Its observable
behaviour on a given main MPD and a given set of resolution documents:
what it requests, what it renders and when, which beacons it fires, and
that the primary content continues.

**What conformance does not reach.** No obligation here binds a Player
that does not implement this specification (§1.4). What this
specification guarantees for such a Player is structural: every
construct it adds sits at an extension point the base specification
lets a client ignore (§4.7), so the primary content keeps playing.

**What conformance to a declared profile does and does not certify.**
A profile check removes every extension-namespace element the profile
does not explicitly include before it checks the document (DASH §8.1),
so a main MPD, a List MPD or a non-linear resolution document is checked
for its declared profile with the constructs of this specification gone.
The document still conforms — the base specification guarantees that
what remains is valid (DASH §5.2.1) — but no declared profile certifies
the SGAI constructs. They are checked against this specification's own
rules, by the procedure of §4.6.

**What this document itself guarantees.** Some obligations bind the
text of this specification rather than an actor at runtime, and are
verified by reading it: the ad-type and layout set is exactly the one of
§3.4, each value mapped to its IAB source; the creative carriers are
exactly the three of §3.5; every new construct states why an existing
one could not be reused, and every deliberate non-reuse is recorded
(§4.8); spatial arrangement is delegated to HTML5 and CSS, with the
`custom` rectangle as the one declared position; no normative statement
requires VAST or any version of it, and every construct is expressible
within the four-actor division of §1.2.

### 4.2 Publisher

A conformant Publisher:

1. **Declares every constraint on a slot in the main MPD** — its cap,
   its family, its allowed layouts, its custom region, its
   early-resolution offset, its once-per-session bound — and leaves none
   of them to be inferred at runtime by the ADS, the APS or the Player.
2. **Declares `@maxDuration` on every ad slot of every family**, linear
   and non-linear (§5.1), and on every alternative-MPD event it authors,
   including a replacement that carries no advertising: a Player cannot
   observe what an alternative presentation depicts. A value of zero declares that the opportunity
   does not fire. Advertising with no fixed end is authored as a chain
   of bounded slots along the primary content.
3. **Authors each opportunity with the construct of its family** (§5.1):
   `<InsertPresentation>` or `<ReplacePresentation>` for linear,
   `<svta:OverlayPresentation>` for overlay, `<svta:PauseAdPresentation>`
   for pause; `<InsertPresentation>` only when `MPD@type` is `static`.
4. **Declares `@id`, `@presentationTime` and `@duration`** on every
   overlay and pause window.
5. **Authors every window of one family in a Period inside a single
   `<EventStream>`** of that family's scheme (§5.1.5), with no `@value`
   on an SGAI scheme's stream.
6. **Draws allowed layouts only from the tokens of §3.4.2** that are
   admissible for the window's family (§5.3.3), and lists `custom` when
   it admits it. Declaring `@allowedLayouts` is OPTIONAL; a window that
   declares none admits its family's default (§3.4.3).
7. **Declares `@customRegion` only on an overlay window whose
   `@allowedLayouts` lists `custom`**, as a rectangle of §5.3.5.
8. MAY declare `@earliestResolutionTimeOffset` on an overlay or pause
   window, and declares `0` when it wants the window resolved only when
   it fires.
9. MAY declare `@executeOnce="true"` on a pause window to bound it to
   one pause ad per session.
10. **Requests the play-list metric** with a `<Metrics>` element on the
    main MPD whenever the content carries pause windows (§5.9).
11. **Authors every SGAI construct so that the document remains valid
    and conformant once the extension namespace is removed** (DASH
    §5.2.1), placing at a baseline position every baseline element a
    Player that does not implement this specification is expected to
    process (§4.7).
12. For on-demand content where monetising an opportunity on a Player
    that predates this specification matters, SHOULD author a standard
    linear break with base constructs alongside the SGAI window (§7.9).
    For live content, an opportunity such a Player cannot honour is an
    expected loss, not an error.

### 4.3 ADS

A conformant ADS:

1. **Decides which ads to serve for an opportunity, how many and in
   what order**, within the envelope the Publisher declared — the number
   of ads in an opportunity is the ADS's decision alone — and applies
   its own targeting, frequency capping, brand safety, competitive
   separation and ordering.
2. **Emits its decision in its own decision document**, typically VAST,
   though it is not bound to VAST and MAY emit another format agreed
   with the APS.
3. **Declares the tracking schedule** in that document: which beacons
   fire, at which times relative to each ad's presentation. The ADS is
   the authority over the schedule.

The ADS is not required to respect the slot cap when selecting
candidates, and a conformance check on an ADS passes whatever the
cumulative duration of the candidates it returned: the Player enforces
the cap. Nor is the ADS required to hold a device-class matrix or a
per-Player capability view. Returning no ads is a legitimate decision,
not a failure.

### 4.4 APS

A conformant APS:

1. **Exposes the endpoint a window's `@uri` resolves to**, and answers
   every resolution request with HTTP `200` and a resolution document of
   the requested family: a List MPD (§5.2.1) for a linear window, a
   non-linear resolution document (§5.2.2) with the matching `@family`
   for an overlay or pause window.
2. **Converts the ADS's decision, in whatever format the two agreed,
   into that document.** How it converts is not defined here.
3. **Produces a document that validates** against the base schema and
   the schema of §5.10, tracking carriers included (§4.6).
4. **Expresses an opportunity that resolved to no ads as an empty
   resolution** (§5.2.3): a well-formed, complete document carrying no
   candidate, served with `200` and a body.
5. **Carries each candidate's presentation options as an ordered list
   in preference order** (§5.3.4), one or more per candidate; how many
   is the APS's decision. The options it emits keep the order the
   decision gave them.
6. **Emits only admissible layouts**: tokens of §3.4.2, admissible for
   the document's family (§5.3.3), and within the set the request
   forwarded (`sgaiAllowedLayouts`) or, when it forwarded none, within
   the family default (§3.4.3). A `custom` option carries a
   `@customRectangle` lying inside the region the request forwarded, or
   inside the viewport when it forwarded none.
7. **Emits only admissible creatives**: every option's form is one of
   the three of §3.5, its creative is served with a media type §3.5
   lists for that form, a video creative is a sub-MPD conforming to the
   Single-Period Static profile (§5.4), and an image or HTML creative is
   addressed by `@assetUrl` and never by a `@mimeType` on an Adaptation
   Set or a Representation.
8. **Carries a background image on every `squeezeback-double-box-background`
   option** in `@backgroundUrl`, as a composition attribute of the
   layout (§5.3.6).
9. **Translates the ADS's tracking schedule into callback events**
   (§5.5), with times relative to each ad's presentation, and carries a
   ClickThrough, when the ad has one, in `<svta:Click>` together with any
   click-tracking URLs (§5.6).
10. **Declares, on every non-linear resolution document, whether the
    slot is dismissible** by carrying `@dismissAfter` when it is and
    omitting it when it is not (§5.2.4).
11. **Declares `@usableFor` whenever its decision stays good for less
    than the window lasts** (§5.2.5); omitting it declares that the
    document is usable for the whole window.
12. **Declares `@onCandidatesExhausted` on every pause document**
    (§5.2.6).
13. **Answers without any capability parameter.** The APS produces
    candidates whether or not the request carries any reserved
    capability parameter, reads an absent one as undetermined, and
    treats a request carrying none as one for which it holds no device
    view (§5.8.4).
14. MAY use capability parameters and forwarded declarations to narrow
    the options it emits, and MAY emit a single option per candidate.

The APS is not required to enforce the Publisher's constraints — the
Player does — nor to hold a device-class matrix. What it is required to
do is not emit what the request told it the Publisher excludes (item 6).

### 4.5 Player

This section states what a conformant Player does. Chapter 7 describes
the resulting behaviour per scenario.

#### 4.5.1 Resolving an opportunity

1. **A linear window is resolved as the base specification defines**:
   between its earliest resolution time and its presentation time, and
   executed under the base execution model (DASH §5.16.2.2).
2. **An overlay window is resolved no earlier than its earliest
   resolution time** — the window's `@presentationTime` minus its
   `@earliestResolutionTimeOffset`, declared or 60 seconds by default —
   and at the latest while the window is still open.
3. **A pause window is resolved no earlier than its earliest resolution
   time**, computed against the window's start and never against the
   pause. When a viewer pause begins inside a pause window, the Player
   holds a usable resolution for it: one obtained earlier and still
   usable (§5.2.5), or one it requests at that moment. A pause that
   begins outside every pause window triggers no request.
4. **Resolving early is a permission, never an obligation.** A Player
   that resolves only when the opportunity fires is conformant whatever
   offset the window carries.
5. **When an overlay or pause opportunity fires, the Player checks that
   the resolution it holds is still usable.** A resolution past its
   `@usableFor` is not presented: the Player requests a new one, and a
   new one that yields no usable candidate is an empty resolution
   (§4.5.6) — the expired resolution is never used as a fallback.
6. **The request carries the forwarded declarations** of §5.8.3
   whenever the window declares them, and MAY carry the capability
   parameters of §5.8.2, omitting any it has no value for or does not
   disclose (§5.8.4). Any other parameter it adds carries a vendor
   prefix.
7. **A window whose `@maxDuration` is absent presents no ad**, and the
   primary content continues. The absence is not read as the base
   specification's unbounded default. A window whose `@maxDuration` is
   zero does not fire.

#### 4.5.2 Validating what it receives

1. **The Player validates every candidate against the declarations of
   the window that served it** before rendering anything, and renders
   only candidates that satisfy them.
2. **A document is a resolution of the requested slot only if its
   family matches**: a List MPD for a linear window, and a non-linear
   resolution document whose `@family` equals the window's family for an
   overlay or pause window. Any other document is a failed execution of
   that window (§4.5.6), and none of its candidates is presented.
3. **A document that cannot be parsed or does not validate** (§4.6) is a
   failed execution of that window.

#### 4.5.3 Selecting a presentation option

1. **For each candidate, the Player walks the presentation options in
   document order** and renders the **first** one that satisfies both:
   - **(a) the device** — its form and layout are satisfiable on the
     device under the budget of §5.3.7, and its creative is one the
     device can render; and
   - **(b) the window** — its `@layout` is in the window's allowed
     layouts: the declared `@allowedLayouts`, or the family default when
     none is declared (§3.4.3). For a `custom` option, the Player also
     supports `custom` and the `@customRectangle` lies inside the
     window's region, or the viewport when none is declared (§5.3.5).
2. **An option that fails either check is not rendered**, and the Player
   moves to the next option in document order. The check holds whether
   or not the Player forwarded the allowed layouts, and whether or not
   the APS narrowed the options from the Player's own declaration.
3. **A candidate with no option passing both checks is skipped**, and
   the Player moves to the next candidate. Only when every candidate is
   exhausted does it continue with the primary content. A skipped
   candidate is not a failed execution of the window.
4. **The Player renders only forms its device can render.** A Player
   that does not support `custom` treats every `custom` option as not
   renderable.
5. A Player MAY skip a candidate whose creative is served with a media
   type outside §3.5, which signals a non-conformant APS or Publisher.

#### 4.5.4 Enforcing the cap

The cap is one Publisher declaration, and what it bounds depends on the
family:

| Family | What the cap bounds | Rule |
|---|---|---|
| Linear, replacement | **Until when** | The presentation ends no later than the end the base `@clip` semantics fix: with `@clip="true"` (the default) the scheduled end, so a late start shortens it; with `@clip="false"`, one cap-length after the actual start. |
| Linear, insertion | **How long**: the cumulative duration of what the slot presents | The Player stops rendering once that duration would exceed the cap, even mid-ad. |
| Overlay | **How long**: the cumulative duration of what the slot presents | As for insertion, and in addition the presentation ends no later than the end of the window on the primary timeline. |
| Pause | **Nothing** | The viewer sets the length of a pause slot. The cap is declared and bounds no duration. |

1. **The Player extends no slot beyond what the cap bounds for its
   family**, whatever the ADS metadata or the number of candidates say.
2. **The cap is enforced against actual rendered length**, not declared
   length: an accepted ad whose actual length exceeds its declared
   duration is trimmed where the cap falls ("trim during play").
3. **The Player MAY drop a candidate before playback** when its declared
   duration would push the cumulative duration past the cap ("drop
   before play").
4. **Timebases are reconciled before comparing.** The cap is in units of
   the window's `EventStream@timescale`; a duration is an `xs:duration`.
   The Player converts the duration into the cap's timescale and rounds
   **up** to the next whole unit — each ad's duration separately, before
   the cumulative sum is taken; a converted duration equal to the cap is
   admitted.
5. **The cap is measured on the presentation timeline.** An interval in
   which the presentation timeline does not advance accrues nothing: a
   form suspended during a pause resumes with the cap it had left when
   it was suspended.
6. The declaring window's cap applies to the candidates of that window
   only (§4.5.7).

#### 4.5.5 Honouring the order of candidates

1. **The Player presents the candidates of a resolution document in the
   order the document declares**, dropping only a candidate with no
   renderable option (§4.5.3) or one dropped before play under §4.5.4.
2. **The survivors keep their order.** The Player does not reorder,
   deduplicate or otherwise rearrange them; ordering happened upstream,
   and the document carries it.

#### 4.5.6 The fallback chain across overlapping windows

1. **When windows of one family overlap in time, the Player orders them
   by presentation time, oldest first, and takes windows with equal
   presentation times in the order they appear in the stream.** It
   attempts the first.
2. **An attempt that produces no ad is a failed execution, and on a
   failed execution the Player attempts the next overlapping window of
   the family.** This is the base specification's rule for the linear
   family — *"If execution fails, steps a-c above are repeated for next
   events in QE, until: — Execution succeeds, or — PRT of the topmost
   event in the queue is in the future (i.e. PRT > PHP), or — The queue
   is empty"* (DASH §5.16.2.2.5) — adopted unchanged, and extended by
   this specification to the overlay and pause families, which the base
   execution model does not reach.
3. **The Player treats all of these alike as a failed execution**, each
   mapped to a condition the base specification lists (DASH
   §5.16.2.2.6):

   | Outcome of the attempt | Base condition |
   |---|---|
   | No response, or failure at the transport level | *"Alternative MPD is unavailable"* |
   | A final HTTP status other than `200` | the same: nothing was obtained |
   | A `200` whose body is not a resolution document the Player can parse or validate | *"Alternative MPD is … invalid"* |
   | A `200` carrying an empty resolution (§5.2.3) | *"Alternative MPD is a List MPD, and merge process resulted in no available media"* |
   | A `200` carrying a document of the wrong family (§4.5.2) | *"Alternative MPD is unavailable or invalid"*: a document that cannot fill the slot. The family test is this specification's. |

4. **A resolution document carrying candidates of the right family is
   not a failed execution**, whatever the Player then does with them. A
   candidate skipped because nothing in it is renderable ends, when
   every candidate is exhausted, at the primary content (§4.5.3) and not
   at the next window: the base condition is media availability after
   the merge, not renderability on one device.
5. **When every overlapping window has been attempted and none produced
   an ad, the Player continues with the primary content
   uninterrupted** — *"If no event can be successfully executed, the
   playback continues uninterrupted"* (DASH §5.16.2.2.5).
6. **A failed execution consumes nothing.** An empty resolution does not
   count as an execution: a linear event with `@executeOnce="true"`
   remains executable, per *"The counter E.c has not been incremented due
   to the failure, consequently if E.c = 0 the event can still be
   executed in the future even if the value of @executeOnce is "true""*
   (DASH §5.16.2.2.6, NOTE 3), and a once-per-session pause window
   remains available (§4.5.10).

#### 4.5.7 Each window binds what it serves

The Player validates the candidates each window of a fallback chain
serves against **that window's own** declarations — its allowed layouts,
its custom region and its cap — and never against those of the window it
stands in for. A declaration belongs to the window that carries it.

#### 4.5.8 One non-linear form at a time, in sequence

1. **At any instant the Player keeps at most one non-linear ad form
   active on screen.** The bound keeps the device from ever needing more
   than the primary content plus one ad form: two concurrent video
   overlays over video would need three decoders, and many devices have
   two.
2. **When a non-linear document carries more than one candidate, the
   Player presents them in sequence**, in document order, each starting
   when the previous one ends. Each contributes the one option the
   Player selected for it; the alternatives inside a candidate are not
   part of the sequence. The cumulative duration is bounded by the cap
   (§4.5.4).
3. The bound is on non-linear forms. A linear presentation and a
   non-linear form on screen together — a hybrid break (§5.1.6) — are
   within it.

#### 4.5.9 Cross-family priority during a pause

1. **While the viewer is paused inside a pause window and an overlay is
   active, the Player renders the pause ad and suspends the overlay**,
   whether the pause ad is fullscreen or partial. The pause ad is the
   only ad surface visible.
2. **On resume, the Player dismisses the pause ad and restores the
   overlay if the overlay's window is still open at the position where
   playback resumes**, continuing it from where it was suspended. On
   on-demand content the frozen presentation time keeps the window open;
   on live content the resume position (§8.8) may lie past the window's
   end, and then the overlay is over and the surface stays clear.
3. **When a viewer pause begins inside a pause window while a linear ad
   occupies the screen, the Player presents the pause ad and suspends
   the linear ad**, and on resume continues the linear ad from where it
   was suspended.
4. The priority is fixed: pause ad above overlay, and above a linear ad,
   during a pause. No construct lets any actor invert it.

#### 4.5.10 The pause family

1. **A pause ad exists only while the primary content is paused.** On
   the pause-to-play transition the Player removes any rendered pause ad
   within one rendering frame and returns to the primary content
   immediately, whether or not an ad is mid-presentation.
2. **From that transition on, the Player fires no further beacon of the
   dismissed pause ad**; beacons scheduled after it fall outside the
   pause ad's active window.
3. **The Player MAY present a pause ad fullscreen or as a partial
   overlay**, as the selected option's layout says. For a fullscreen
   pause ad it MAY release every resource held by the primary content and
   by any pre-existing overlay. For a partial one, the paused frame stays
   visible and any coexisting overlay stays suspended (§4.5.9).
4. **A pause is what the viewer experiences, not how the Player achieves
   it.** The Player MAY pause by any mechanism that suspends the primary
   content and later resumes it from the position at which it was
   suspended, including one that releases the primary content's decoding
   resources for the pause. On resume it continues the primary content
   from that position; a mechanism that cannot restore the position is
   not a pause under this specification, whatever it is called.
5. **In live content, while the viewer is paused inside a pause window,
   the Player keeps its presentation time frozen inside that window** for
   the full duration of the pause, whatever the live edge does in wall
   clock time. The pause window is anchored to that frozen time, so the
   pause ad stays admissible until the viewer resumes. Where the Player
   resumes after the pause — at the frozen position, at the oldest
   position the time-shift buffer still holds, or at the live edge — is a
   Player action that follows the resume and lies outside the pause
   window (§8.8).
6. **On a window with `@executeOnce="true"`, the Player presents at most
   one pause ad for that window for the whole session**, and a later
   qualifying pause inside it leaves the primary content untouched. The
   window is consumed when a pause ad **begins rendering**, not when the
   pause occurs: a pause that resolves to no renderable candidate leaves
   the window available.
7. **The cap does not bound a pause slot** (§4.5.4).

#### 4.5.11 Candidates exhausted inside a pause

When the candidates of a pause document are exhausted and the viewer is
still paused, the Player applies the document's
`@onCandidatesExhausted` (§5.2.6), and `stop` when the document declares
none. Under `request-again`, a document carrying no candidates, or none the
device can render, is `stop` for the rest of that pause, so that one
pause never produces an unbounded series of requests. The fall-through to primary content of
§4.5.3 does not apply here: the primary content is paused.

#### 4.5.12 Playback speed

1. **The Player renders every ad form, linear or non-linear, at the
   playback speed of the primary content** at the moment the ad is
   presented, and does not force an ad to 1× when the primary content
   plays at another speed.
2. **Durations stay on the presentation timeline.** The on-screen
   wall-clock length of a form is derived as `duration /
   playback_speed`; a 10-second ad presented at 2× is on screen for 5
   seconds. Cap enforcement and beacon scheduling use the
   presentation-timeline duration; only the wall-clock behaviour follows
   the derived value.
3. **This holds for every form**, including `image` and `html`, which
   have no intrinsic media: their declared duration is a
   presentation-timeline value and their wall-clock length is derived
   the same way.

#### 4.5.13 Tracking

1. **For every ad accepted for rendering, the Player executes the
   tracking schedule the resolution document carries**, firing each
   beacon at its time relative to the ad's presentation (§5.5.3). It
   decides neither which beacons fire nor when.
2. **When the cap trims an ad, the Player stops firing that ad's
   remaining beacons at the trim boundary.** A beacon scheduled exactly
   at the boundary fires: the ad reached that time.
3. **The Player fires each beacon once within its ad** (§5.5.4), and
   fires both of two beacons that share an `@id` in two different ads.
4. **A callback stream inside a `<svta:Candidate>` resolves against that
   candidate's own presentation.**
5. **The Player ignores extension elements and attributes of a namespace
   it does not implement**, on tracking-related constructs as anywhere
   else, and keeps playing.

#### 4.5.14 Viewer dismissal

1. **On a non-linear slot, the Player makes dismissal available only as
   `@dismissAfter` declares** (§5.2.4): not at all when the attribute is
   absent; otherwise from the declared number of seconds after the
   slot's first rendered frame — measured on the presentation timeline —
   for as long as the slot is on screen, and not before.
2. **On a linear slot, the Player honours the base declarations with
   their base meaning** (§5.2.4): the event's `@skipAfter`, present or
   defaulted, governs skipping the rest of the slot, and a
   `PlaybackRestrictions@skipAfter` in the List MPD governs skipping the
   rest of the ad it scopes. The Player offers neither earlier than its
   declaration allows.
3. **A dismissal ends the whole slot.** The Player stops presenting
   every ad of the slot and advances to no other ad or form within it.
4. **A dismissed slot does not shorten the primary content.** Where the
   slot bounded a region of the primary timeline, the Player continues
   from where the primary content stands and skips none of it.
5. **The Player fires the beacons scheduled up to the moment of the
   dismissal, and none scheduled after it.** A dismissal is an outcome
   of the presentation, not a failure of it.
6. **This applies to every family**, the pause family included: a
   dismissed pause ad gives the viewer the paused frame back without
   resuming.

How dismissal is offered — a control, a gesture, a remote button — is
out of scope. This specification states when it is available and what
it ends.

#### 4.5.15 ClickThrough

A Player conformant to this specification **reads `<svta:Click>`** and,
when the viewer activates the ClickThrough, opens (or hands to the
platform) `@clickThroughUrl` and fires every `<svta:ClickTracking>` URL
once per activation. Click-tracking fires on activation and never on the timeline.

#### 4.5.16 Graceful continuation

1. **When resolving or rendering an accepted ad fails at runtime** — a
   decode error, a malformed candidate, an ad segment that cannot be
   fetched, a network loss mid-ad — **the Player aborts that ad and
   continues the primary content uninterrupted.** This is the base
   specification's own outcome for its execution model — *"A failed
   execution results in smooth continued playback of the main media
   presentation"* (DASH §5.16.2.2.6) — stated for the constructs added
   here.
2. **On every device class and for every opportunity type, the Player
   produces a defined behaviour**: it renders, falls back to a later
   option or candidate, or skips and continues with the primary content.
   Skipping an opportunity it cannot honour is a valid outcome, not a
   failure.
3. **Continuing "uninterrupted" means no visible artefact**: no freeze,
   no blank slate, no error surface unless the application opted into
   one, and no beacon fired for the opportunity that failed.

#### 4.5.17 Deriving the pause-delivery measurement

A Player that reports metrics derives the paused interval from the
`PlayList` entries as §5.9 describes, and counts no playback period that
stopped on `Rebuffering` as a pause opportunity.

### 4.6 Validating a resolution document

A resolution document is valid when it passes all four steps below. A
validation that stops after the first has checked the MPD and not the
advertising, and a report that calls such a document valid has not
checked its tracking carrier at all — which is the outcome a reader is
most likely to arrive at by default, because a schema-driven validator
accepts the extension subtree without looking inside it.

1. **Base schema.** The document validates against the base MPD schema
   (DASH Annex B). The base schema accepts `svta:` content wherever it
   admits `<xs:any namespace="##other" processContents="lax"/>` without
   checking it, so this step passes whatever that content is.
2. **Extension schema.** Every element of the namespace
   `urn:svta:dash:sgai:2026` validates **strictly** against the schema of
   §5.10, and the one base-namespace element admitted inside a
   `<svta:Candidate>` validates strictly as the base `EventStreamType`.
   A validator that processes the extension namespace laxly has not run
   this step.
3. **Tracking carriers.** Every callback `<EventStream>` — in a
   sub-MPD, on a List MPD Period, and **inside every `<svta:Candidate>`**
   — carries `@schemeIdUri="urn:mpeg:dash:event:callback:2015"` and
   `@value="1"`, and each of its `<Event>` elements carries a URL as its
   content. A validator locates these by scanning inside
   `<svta:Candidate>` elements as well as Periods; one that scans Periods
   alone misses every carrier of an image or HTML ad.
4. **Conditional rules.** The rules the schema cannot express hold: the
   document's family matches the requesting window; every option's
   `@layout` is admissible for that family (§5.3.3); `@backgroundUrl`
   appears exactly on `squeezeback-double-box-background` options and
   `@customRectangle` exactly on `custom` options, each rectangle
   satisfying §5.3.5; `@onCandidatesExhausted` appears on pause
   documents only; every non-linear option carries `@duration`.

**A validation report states which steps it ran.** "Valid" without that
statement cannot be told apart from step 1 alone.

Whether an option's layout lies within the window's allowed layouts,
and whether a rectangle lies within the window's region, depend on the
window that requested the document, and are checked by the Player at
runtime (§4.5.3) rather than by validating the document alone.

### 4.7 Backward compatibility, per construct

Every construct this specification introduces is checked against the
same questions: where it sits; which extension point admits it and what
the base specification says a client that does not know it does; what
such a client does, step by step; whether removing it leaves a document
that parses and plays; which test models the legacy case (Annex Q, Q.7);
which namespace it is in; and which carrier class it uses. The carrier
classes are the four the base specification leaves open for anything it
does not define: **(a)** foreign-namespace open content (DASH §5.2.1);
**(b)** an application-level event stream (DASH §5.10); **(c1)** a
`SupplementalProperty` (DASH §5.8.4.9), whose unrecognised scheme makes a
client *"ignore the descriptor"*; **(c2)** an `EssentialProperty` (DASH
§5.8.4.8), whose unrecognised scheme makes it *"ignore the parent element
that contains the descriptor"*. (c1) and (c2) are kept apart because one
degrades and the other removes. **No construct of this specification uses
(c1) or (c2), and none invokes a new delivery format** (§4.8.12).

The walk-through a Player that does not implement this specification
follows is the same for every construct placed as extension content,
and is stated once:

1. The parser reaches an element or attribute in a namespace it does not
   implement.
2. The base specification lets it remove that content: the author has
   guaranteed that *"after XML attributes or elements in the other
   namespaces than the DASH namespace are removed, the result is a valid
   XML document formatted according to that schema and that conforms to
   this document"* (DASH §5.2.1). No error is raised by the base
   specification's rules.
3. The remaining structure parses, because the author guaranteed it.
4. Playback of the primary content continues uninterrupted.

**The authoring lever.** Removal is by namespace, and removing an
element removes what it contains. A baseline element placed as a
**sibling** of an SGAI element stays within reach of such a Player; one
placed **inside** an SGAI element does not, and carries no legacy
guarantee. This specification nests baseline content inside an SGAI
element in exactly one place — the callback `<EventStream>` inside a
`<svta:Candidate>` — and does so deliberately: that tracking belongs to
an ad such a Player never presents.

#### 4.7.1 The two event schemes

- **Placement:** `EventStream@schemeIdUri` of a stream in a Period of
  the main MPD.
- **Extension point:** application-defined event schemes (DASH §5.10,
  carrier class (b)); a client subscribes to the streams of interest and
  ignores the rest (DASH §5.10.1).
- **Walk-through:** the client does not recognise the scheme and does
  not act on the stream; the `<Event>` children carry only
  `<svta:OverlayPresentation>` or `<svta:PauseAdPresentation>`, which it
  removes as extension content. No request is made; a viewer pause
  produces no ad.
- **Removal check:** removing the stream's SGAI content leaves an
  `<EventStream>` with empty `<Event>` elements, which is valid.
- **Namespace:** the scheme URIs are in the SVTA namespace pattern of
  §2.1; the child elements in `urn:svta:dash:sgai:2026`.

#### 4.7.2 `<svta:OverlayPresentation>` and `<svta:PauseAdPresentation>`

- **Placement:** exactly one, as a child of an `<Event>` of the
  family's scheme; all constraints as attributes, no children.
- **Extension point:** foreign-namespace content of `EventType` (DASH
  §5.2.1, §5.10.2.1; class (a)).
- **Walk-through:** the common one above.
- **Required-sibling check:** the elements change no attribute of the
  `<Event>` or of any sibling; a legacy-required element is never nested
  inside them.
- **Namespace:** `urn:svta:dash:sgai:2026`.

#### 4.7.3 The non-linear resolution document

- **Placement:** an MPD whose single zero-duration Period has one child,
  `<svta:OverlayList>`, which contains `<svta:Candidate>`,
  `<svta:RenderableAsset>`, `<svta:Click>` and the metadata elements.
- **Extension point:** foreign-namespace content of `PeriodType` (class
  (a)).
- **Walk-through:** a Player that does not implement this specification
  never requests this document, because it never acted on the window.
  Parsed anyway, the document loses `<svta:OverlayList>` and everything
  under it and is left an MPD with one empty zero-duration Period —
  valid, and presenting nothing.
- **Removal check:** as stated; the MPD-level attributes are base
  attributes with base meaning.
- **Namespace:** `urn:svta:dash:sgai:2026`; the document declares the
  base Full profile.

#### 4.7.4 Extension content on a List MPD Period

- **Constructs:** `<svta:RenderableAsset>`, `<svta:Click>` and the
  metadata elements as children of a List MPD Period.
- **Placement:** after every DASH-namespace child of the Period, as
  `PeriodType` requires.
- **Extension point:** foreign-namespace content of `PeriodType` (class
  (a)).
- **Walk-through:** a base Player removes them and plays the Period's
  `<ImportedMPD>` video as the base specification defines; the ad plays,
  its image and HTML alternatives are unseen, and its ClickThrough is
  inert.
- **Required-sibling check:** the `<ImportedMPD>` stays at its base
  position and is never inside an SGAI element, so the base Player's
  ad is intact.

#### 4.7.5 The capability and forwarding parameters, and the request-type URN

- **Placement:** query parameters on the resolution request; the URN as
  a token in `RequestParam@includeInRequests`.
- **Extension point:** for the parameters, the query component of a URL
  the Publisher's APS owns (RFC 3986); for the URN, the owner-specified
  request type of DASH Table I.4, whose drop rule applies: *"The client
  shall drop unknown URIs from the @includeInRequests and
  @includeInHeaders strings prior to processing them"*.
- **Walk-through:** a Player that does not implement this specification
  sends no reserved parameter, because it never issues a non-linear
  resolution request; on a linear request it sends none either, and the
  APS answers without them. A client unaware of the URN drops the token
  and processes the rest of the attribute.

#### 4.7.6 Aggregated audit

| Construct | Placement | Extension point | Walk-through | Removal / sibling check | Legacy test | Namespace | Carrier class | Status |
|---|---|---|---|---|---|---|---|---|
| `urn:svta:dash:sgai-overlay:2026`, `urn:svta:dash:sgai-pause-trigger:2026` | `EventStream@schemeIdUri` | DASH §5.10.1 | §4.7.1 | OK | Q.7.1, Q.7.2 | SVTA | (b) | OK |
| `<svta:OverlayPresentation>` | child of `<Event>` | DASH §5.2.1 | §4.7 | OK | Q.7.1 | `urn:svta:dash:sgai:2026` | (a) | OK |
| `<svta:PauseAdPresentation>` | child of `<Event>` | DASH §5.2.1 | §4.7 | OK | Q.7.2 | `urn:svta:dash:sgai:2026` | (a) | OK |
| `<svta:OverlayList>` and descendants | child of a zero-duration `<Period>` | DASH §5.2.1 | §4.7.3 | OK | Q.7.3 | `urn:svta:dash:sgai:2026` | (a) | OK |
| `<svta:RenderableAsset>`, `<svta:Click>`, metadata on a List MPD Period | after the DASH children of `<Period>` | DASH §5.2.1 | §4.7.4 | OK | Q.7.4 | `urn:svta:dash:sgai:2026` | (a) | OK |
| Callback `<EventStream>` inside `<svta:Candidate>` | inside an extension element | removed with its parent | §4.7 | OK — authored for implementing Players only | Q.7.3 | base namespace, base scheme | (b), nested in (a) | OK |
| Reserved query parameters | resolution request URL | RFC 3986 query | §4.7.5 | OK | Q.7.5 | `sgai` prefix | not an MPD construct | OK |
| `urn:svta:dash:sgai-resolution:2026` | `RequestParam@includeInRequests` | DASH Table I.4 | §4.7.5 | OK | Q.7.5 | SVTA | not an MPD construct | OK |

### 4.8 Justifications: what is reused, what is introduced, what departs

Every construct this specification introduces states inline why an
existing construct could not be reused, and every deliberate non-reuse
is recorded. This section gathers them.

#### 4.8.1 Reused unchanged

| Base construct | Used for |
|---|---|
| `<InsertPresentation>`, `<ReplacePresentation>` and the alternative-MPD execution model (DASH §5.16) | The linear family, its fallback chain, its failure conditions and its non-consuming failures |
| List MPD profile and `<ImportedMPD>` (DASH §8.14, §5.3.2.6) | The linear resolution document and its per-ad sub-MPDs |
| Single-Period Static profile (DASH §8.15) | Every video creative, linear and non-linear |
| `<EventStream>` / `<Event>` (DASH §5.10) | Every opportunity declaration |
| `@maxDuration` name, units and zero rule | The cap on every family |
| `@earliestResolutionTimeOffset` name, units and 60-second default | Early resolution of overlay and pause windows |
| `@executeOnce` and the execution counter | The once-per-session pause window |
| `@clip`, `@returnOffset`, `@startWithOffset` | Linear replacement, unchanged |
| `@skipAfter` and `PlaybackRestrictions@skipAfter` | Skipping on linear slots, with their base meaning |
| `@noJump` | Linear slots, unchanged |
| Callback event scheme (DASH §5.10.4.5) | Every timeline-scheduled beacon |
| `RequestParam` and the URL-parameter scheme (DASH Annex I) | Publisher-declared request parameters |
| `PlayList` metric and `<Metrics>` (DASH Annex D.4.6, §5.9.1) | Pause-delivery measurement |
| Listen mode (DASH §4.2) | The decoder budget of a hybrid break; suspension of a linear ad under a pause ad |
| Spatial Relationship Description coordinate convention (DASH Annex H) | The `custom` rectangle's notation |
| Document order as preference (DASH §5.11.3) | Presentation-option order |

#### 4.8.2 Introduced, and why nothing existing fits

| Construct | Why no base construct could carry it |
|---|---|
| Overlay and pause event schemes and their child elements | The base ad machinery is substitutive; no base event composes, and none is triggered by a viewer pause (§5.1.3, §5.1.4). |
| Non-linear resolution document (`<svta:OverlayList>`, `<svta:Candidate>`) | A List MPD is a sequence to play, not a set of alternatives (§5.2.2). |
| `<svta:RenderableAsset>` | No base construct offers an ordered list of alternative presentations of one ad (§4.8.7), and image and HTML creatives have no home on the media axis (§5.3.2). |
| `@family` | A family test has no base counterpart, because the base has one family (§5.2.2). |
| `@dismissAfter` | The base skip controls default to skippable everywhere (§4.8.10). |
| `@usableFor` | The base resolution model has no lifetime inside an execution (§5.2.5). |
| `@onCandidatesExhausted` | No base slot outlives its media, so the base has no exhaustion vocabulary (§5.2.6). |
| `@allowedLayouts`, the layout tokens | The base specification has no layout vocabulary at all. |
| `@customRegion`, `@customRectangle` | The base coordinate model is confined to Adaptation Sets and Sub-Representations (§5.3.5); its notation is reused. |
| `<svta:Click>` | The base event model has no event dispatched by a user activation (§5.6). |
| Metadata elements | The base specification carries no ad-system, title or advertiser field. |
| Reserved request parameters | The base request vocabulary is session state, author-declared, and sends a placeholder for an unknown value (§5.8.2). |
| `urn:svta:dash:sgai-resolution:2026` | `altmpd` names alternative-MPD requests only (§5.8.1). |

#### 4.8.3 Where this specification departs from a base answer

Each departure is an exception, recorded with its reason. Everywhere
else the base answer governs.

| Base answer | This specification | Reason |
|---|---|---|
| An absent `@maxDuration` is infinity (DASH §5.16.5.2). | Every slot declares a cap; a slot without one presents no ad — including an inherited linear event, which a base Player would play uncapped. | An unbounded slot buys no capability a chain of bounded slots does not already give, and costs every cap-dependent rule a second reading. A Publisher who omits the cap notices at once — nothing sells — and the fix is one attribute. The narrowing restricts which documents conform and changes no construct's meaning, which is what a profile does (DASH §8.1). |
| The base skip controls default to skippable everywhere. | A non-linear slot that declares nothing is not dismissible. | Dismissal is a property of what was sold and is granted, never assumed (§5.2.4). The linear family keeps the base answer. |
| The base execution queue does not order equal presentation times. | Equal times break by position in the stream (§5.1.5). | An extension where the base gives no answer. |
| The base execution model reaches alternative-MPD events only. | The fallback chain, the failure conditions and the non-consuming failure are extended to the overlay and pause families (§4.5.6). | One behaviour across every family, so an implementer learns one. An extension, not a departure. |
| The base live resumption clips to the time-shift buffer. | Kept unchanged; the freeze of §4.5.10 governs the presentation time during the pause, and the base rule governs the resume (§8.8). | No departure: the two govern different moments. |

#### 4.8.4 The supplementary video descriptor — weighed, not taken

The nearest base construct to composition. *"Supplementary video
services (sometimes referred to as picture-in-picture services) offer
the ability to include a video with a smaller spatial resolution within
a video with a bigger spatial resolution"* (DASH §5.8.5.16). It describes
two Adaptation Sets of **one** presentation, authored together, where a
non-linear ad arrives at runtime in a separate document; it carries no
ad, no layout and no non-video surface, while several layouts here need
an image or HTML surface; and it hands the composition back rather than
specifying it: *"Potential manipulation of the stream and the
composition of the main video and the supplementary video are out of the
scope of the DASH client."* Its single-decoder VVC path is the technique
§1.3 leaves to a later edition.

#### 4.8.5 The Spatial Relationship Description — notation reused, carrier not

Positions encoded video in a shared coordinate system for tiling and
region-of-interest selection, and *"SRD information shall be contained
exclusively in these two MPD elements (AdaptationSet and
SubRepresentation)"* (DASH §H.1). Using it as a composition carrier would
misuse it and build the parallel layout system §1.3 declines. Its
coordinate notation is reused for the `custom` rectangle (§5.3.5).

#### 4.8.6 The nonlinear-playback annex — a precedent, not a carrier

Despite its name, it is not about non-linear ads: *"This Annex provides
Nonlinear Playback capabilities, to serve Interactive Storyline
content"* (DASH §L.1). It defines no overlay, no composition and no ad
semantics. It is cited for its shape — a timeline-anchored event
declaring a window whose resolution happens off the timeline, on a
viewer action — which the pause window shares (§5.1.4).

#### 4.8.7 Ordered preference: fallback scheme, `@selectionPriority`, `Preselection`

- **The MPD fallback scheme** (`urn:mpeg:dash:fallback:2016`, DASH
  §5.11.3) states the ordering rule almost verbatim — *"the first one
  having the highest preference"* — and is cited affirmatively for it.
  It is not reused: its granularity is whole MPD URLs, *"Each MPD may
  contain at most one"* such descriptor, and it is triggered by an
  unrecoverable error rather than by a capability check.
- **`@selectionPriority`** (DASH §5.3.7.2): *"In the absence of other
  information, higher numbers are the preferred selection over lower
  numbers."* It runs in the opposite direction from document order, it
  is a hint on a media-level type rather than on an ad-level choice, and
  it is conditional on there being no other information, which on a
  candidate there always is. Carrying both would put two orderings in
  one element with no rule for which governs.
- **`Preselection`** (DASH §5.3.11) elements *"define user experiences
  that can be selected by the DASH Client"*, but a Preselection combines
  components into one jointly rendered experience rather than offering
  alternatives to choose between.

#### 4.8.8 The URL-parameter mechanism — used for Publisher parameters, not for the Player's

The base mechanism is reused unchanged for what it is for, and one
request type is named for the non-linear resolution request (§5.8.1).
It does not carry the capability parameters or the forwarded
declarations, for the reasons of §5.8.2 and §5.8.3: its vocabulary is
state, its author is the content author, its unknown-variable rule sends
a placeholder, and a literal copy of `@allowedLayouts` would duplicate a
declaration.

#### 4.8.9 The seek-blocking control — preserved on linear, excluded on non-linear

`@noJump` forbids the playhead moving *"from any point for which PHP <
PRT to any point where PHP > EAP without executing this event"* (DASH
§5.16.5.2). On an inherited linear break it is preserved unchanged: the
ad occupies the timeline, so forbidding the jump forbids skipping the ad,
which is what the control exists for. On the overlay and pause families
it is excluded, because the region a non-linear window covers is
programme: the primary content keeps playing underneath the ad, so
forbidding the jump would not oblige the viewer to watch the ad — it
would oblige them to watch a stretch of programme they chose to skip.
This is an exception with a reason, not an omission.

#### 4.8.10 The base skip controls — kept on linear, not reused for non-linear dismissal

Recorded in §5.2.4. Both base controls default to `PT0S`, skippable
everywhere; a non-linear slot here is dismissible only when the APS says
so. The event-level control is also in the Publisher's MPD, which does
not know what was sold. On the linear family the base controls govern
with their base meaning, including the schema default of an omitted
`@skipAfter`, so that a Player of this specification and a base Player
treat the same linear event the same way.

#### 4.8.11 `<ImportedMPD>` — reused on linear, not nested in a non-linear option

Recorded in §5.3.2: its definition places it on a Period of a List MPD,
and a non-linear option is neither. The Single-Period Static binding it
would have brought is adopted by statement (§5.4).

#### 4.8.12 Profiles, and why none is minted

**No profile and no Interoperability Point is minted by this
specification.** A profile URI of its own would declare that a document
carries these constructs without certifying them, because a profile
check removes extension content the profile does not explicitly include
(§4.1); certifying them would need an Interoperability Point that
included the namespace, and *"The owner of the URI is responsible to
provide sufficient semantics on the restrictions and permission of this
interoperability point"* (DASH §8.1) — rules, conformance criteria and a
published URI to maintain across editions. The non-linear resolution
document therefore declares the base Full profile, which restricts
nothing, and does not declare the List profile, which is built for the
alternative-MPD flow and would enrol the document in a family it does
not belong to.

**The cost is stated rather than hidden:** no third-party profile
validator knows how to check the SGAI constructs. Their conformance rests
on the schema of §5.10 and the procedure of §4.6.

**No new delivery format is defined.** An image or an HTML creative is a
flat HTTP resource, not a segmented representation, so the base
specification's guidance for a new media container format with DASH
(DASH Annex F, informative) and the Interoperability Point it would
imply do not apply: a URL on an extension element carries it (§5.3.2).

---

## 5. Syntax

This chapter defines the constructs an implementation authors and
reads. Every attribute block is a table. Around the tables, the prose
carries the reasoning: why this carrier, why this shape, and, for every
construct this specification introduces, why an existing construct of
the base specification could not be reused.

Throughout, the prefix `svta:` is bound to the namespace
`urn:svta:dash:sgai:2026`, and unprefixed element names are in the base
specification's MPD namespace `urn:mpeg:dash:schema:mpd:2011`.

### 5.1 Opportunity declarations in the main MPD

Every ad opportunity is an `<Event>` inside an `<EventStream>` of the
main MPD. The stream's `@schemeIdUri` gives the family; the `<Event>`'s
scheme-specific child element carries the slot's declarations.

| Family | `EventStream@schemeIdUri` | Child of `<Event>` | Resolution document |
|---|---|---|---|
| Linear, insertion | `urn:mpeg:dash:event:alternativeMPD:insert:2025` | `<InsertPresentation>` | List MPD (§5.2.1) |
| Linear, replacement | `urn:mpeg:dash:event:alternativeMPD:replace:2025` | `<ReplacePresentation>` | List MPD (§5.2.1) |
| Overlay | `urn:svta:dash:sgai-overlay:2026` | `<svta:OverlayPresentation>` | Non-linear resolution document (§5.2.2) |
| Pause | `urn:svta:dash:sgai-pause-trigger:2026` | `<svta:PauseAdPresentation>` | Non-linear resolution document (§5.2.2) |

**The event machinery is reused, not extended.** `<EventStream>` with
`<Event>` is the base specification's vehicle for timeline-anchored
signalling — *"Events are timed, i.e. each event starts at a specific
media presentation time and may have a duration"* (DASH §5.10.1) — and
it is already open to a specification like this one: *"The Event
element may contain further XML elements meaningful for a particular
event scheme. These may be defined in this document (e.g. Alternative
MPD and Service Description events, see Table 44) or in some external
namespace"* (DASH §5.10.2.1). This specification adds two scheme URIs
and two child elements, and changes nothing about how a stream is
authored, parsed or dispatched.

**The scheme is what a Player that does not implement it ignores.**
Streams are clustered by scheme so that a client can *"subscribe to an
Event Stream of interest and ignore Event Streams that are of no
relevance or interest"* (DASH §5.10.1). Independently of that, the
document stays conformant for such a Player, because the base
specification places the obligation on the author: *"the MPD shall be
authored such that, after XML attributes or elements in the other
namespaces than the DASH namespace are removed, the result is a valid
XML document formatted according to that schema and that conforms to
this document"* (DASH §5.2.1).

**`@value` on the two SGAI schemes.** The base specification leaves the
value space of `EventStream@value` to the owner of the scheme. The two
schemes of this specification define none: an `<EventStream>` carrying
either scheme carries no `@value`, and a Player ignores one if present.
All windows of one family in a Period share a single stream (§5.1.5), so
nothing needs to tell two such streams apart. The callback scheme of
§5.5 is different: its `@value` is fixed by the base specification.

**The main MPD's `@profiles` is the Publisher's.** Carrying an
opportunity window of any family neither requires nor excludes a
particular profile identifier on the main MPD; the annexes differ from
one another accordingly.

#### 5.1.1 `<InsertPresentation>` — linear insertion, inherited

Reused unchanged from DASH §5.16.3. The alternative presentation is
*"inserted in the media time of the Main Presentation, i.e. time-shift
the part of the Main Presentation which is played after the alternative
Media Presentation"* (DASH §5.16.1): the primary timeline stops for the
ad and resumes from where it stopped. *"The event shall not appear if
the MPD type is "dynamic""* (DASH §5.16.3), because a timeline that can
be stopped for an indefinite period is an on-demand or pre-recorded one;
a live break uses `<ReplacePresentation>`.

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | yes | `xs:anyURI` | — | The APS endpoint the Player resolves. Returns a List MPD (§5.2.1). |
| `@maxDuration` | **yes under this specification**; optional in the base schema | `xs:unsignedLong` | none under this specification (the base default is infinity) | The slot cap, in units of the parent `EventStream@timescale`. On an insertion slot it bounds the cumulative duration of what the slot presents (§4.5.4). Zero means the event is not executed. |
| `@earliestResolutionTimeOffset` | no | `xs:unsignedLong` | 60 s in `@timescale` units | *"specifies the time interval (in units of EventStream@timescale) prior to the Event@presentationTime during which the MPD described in the @uri attribute may be requested. The default is 60 seconds in units of timescale"* (DASH §5.16.5.2). |
| `@executeOnce` | no | `xs:boolean` | `false` | *"specifies whether the event is executed only once during the media presentation"* (DASH §5.16.5.2). |
| `@noJump` | no | `xs:integer` | `0` | The base seek-blocking control, preserved unchanged on the linear family (§4.8.9). |
| `@skipAfter` | no | `xs:duration` | `PT0S` | The base skip control, honoured with its base meaning (§5.2.4). |
| `@serviceDescriptionId` | no | `xs:unsignedInt` | — | The base binding of a service description to the event and the presentation it initiates (DASH §5.16.5.2). |

The `@maxDuration` row is the one departure from the base definition,
and it narrows which documents conform rather than changing what the
attribute means: the base specification reads an absent value as
unbounded — *"If absent, the value is assumed to be infinity, in which
case the current presentation resumes only when the alternative
presentation terminates"* (DASH §5.16.5.2) — and this specification
requires a value on every slot (§4.8.3). The zero rule is inherited as
it stands: *"If the value of @maxDuration is zero, the event is not
executed"* (DASH §5.16.5.2).

#### 5.1.2 `<ReplacePresentation>` — linear replacement, inherited

Reused unchanged from DASH §5.16.4. The alternative presentation
*"may replace a portion of the main Media Presentation. In this case,
the main Media Presentation is not being output, but its media time
progresses at the same speed as the currently playing alternative Media
Presentation"* (DASH §5.16.1). `AlternativeMPDReplaceEventType` extends
`AlternativeMPDEventType`, so every attribute of §5.1.1 applies, plus
three of its own:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@returnOffset` | no | `xs:unsignedLong` | — | Determines the primary timeline position at which the primary content resumes after the alternative presentation (DASH §5.16.4). |
| `@clip` | no | `xs:boolean` | `true` | Which end of the slot the cap fixes. *"If the value of this attribute is "true", the alternative presentation shall terminate at the latest at time PRT + APDmax. If the value is "false", the presentation shall terminate at time PRTA + APDmax"* (DASH §5.16.4, Table 62). |
| `@startWithOffset` | no | `xs:boolean` | `false` | Whether a late alternative presentation starts from its first frame or skips into itself by the lateness (DASH §5.16.4). |

**On a replacement slot the cap bounds *until when*.** With the default
`@clip="true"` the presentation ends at the end the Publisher scheduled,
whatever time the event actually fired, so a late start shortens the ad
instead of moving the end. With `@clip="false"` it ends one cap-length
after its actual start, and the slot ends later than scheduled — the
base specification moving the bound, not the Player exceeding it. On an
insertion slot there is no `@clip` and could be none: insertion stops
the primary timeline, so there is no scheduled end to preserve and a
late start displaces nothing.

#### 5.1.3 `<svta:OverlayPresentation>` — overlay window, new

Declares an overlay opportunity: a region of the primary timeline in
which a non-linear ad may be presented while the primary content keeps
playing. The region is the parent `<Event>`'s `@presentationTime` and
`@duration`.

**Why a new element and not an attribute on the alternative-MPD
events.** Those events are substitutive by definition: *"An alternative
Media Presentation is a presentation that replaces the main Media
Presentation at a certain point on the media timeline for a duration of
time. After the playback of the alternative Media Presentation is
complete, the playback is continued with the main Media Presentation"*
(DASH §5.16.1). An overlay puts two things on screen at once, and an
attribute added to either element would contradict the semantics its
own clause states. The constructs of the base specification that come
closest to composition are weighed in §4.8.4 to §4.8.6.

**Placement.** Exactly one `<svta:OverlayPresentation>` is a child of
the `<Event>`, in the position `EventType` opens to foreign-namespace
content.

`<Event>` attributes, as used on an overlay window:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@id` | yes | `xs:unsignedLong` | — | Identifies the window. Required here because a fallback chain (§5.1.5) and a report of an unfilled window both need to name it. |
| `@presentationTime` | yes | `xs:unsignedLong` | `0` in the base schema | Start of the window, in `EventStream@timescale` units, relative to the Period start and `@presentationTimeOffset`. |
| `@duration` | yes | `xs:unsignedLong` | — | Length of the window. The slot's presentation never extends past the window's end on the primary timeline (§4.5.4). |

`<svta:OverlayPresentation>` attributes:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | yes | `xs:anyURI` | — | The APS endpoint the Player resolves. Returns a non-linear resolution document of family `overlay` (§5.2.2). |
| `@maxDuration` | yes | `xs:unsignedLong` | — | The slot cap, in units of the parent `EventStream@timescale`: the cumulative duration of what the slot presents (§4.5.4). Zero means the window does not fire. Name, units and zero rule are those of the base attribute. |
| `@allowedLayouts` | no | whitespace-separated list of layout tokens | the overlay family default (§3.4.3) | The layouts this window admits, drawn from §3.4.2: overlay-family tokens, `linear`, and `custom`. |
| `@customRegion` | no; admissible only when `@allowedLayouts` lists `custom` | rectangle (§5.3.5) | `0,0,100,100` — the whole viewport | The region inside which a `custom` overlay must lie. |
| `@earliestResolutionTimeOffset` | no | `xs:unsignedLong` | 60 s in `@timescale` units | How far before the window's start the Player may resolve it. Name, type, units and default are those of the base attribute (DASH §5.16.5.2). |

**Early resolution reuses the base construct, default included.** The
base Earliest Resolution Time is *"a media time defined by the value of
Event@presentationTime, minus the value of
AlternativeMPDEventType@earliestResolutionTimeOffset, normalized by the
value of @timescale"* (DASH §5.16.2.1, Table 57). An overlay window's
`@presentationTime` is the start of the window, so the same computation
gives the overlay's earliest resolution time without a new definition.
A window that declares nothing may be resolved 60 seconds before it
starts, as a base event may; a Publisher who wants resolution only when
the window starts declares `0`. The base schema carries no default for
the attribute — the 60 seconds are stated in its semantics, not in the
schema — and this specification follows the semantics.

**No concurrency attribute.** At most one non-linear form is on screen
at any instant (§4.5.8). An attribute whose only admissible value is `1`
would restate a fixed rule, and any other value would be unenforceable,
so the window carries none.

**Encoding of `@allowedLayouts`.** A single attribute carrying a
whitespace-separated token list, rather than a wrapper element with one
child per token, matching the base attributes typed as an XML Schema
list — `@dependencyId` is one — which are whitespace-delimited. The two
base attributes that are comma-separated, `MPD@profiles` and `@codecs`,
are constrained to IETF RFC 6381 productions and are not the model. An
element form is warranted only when each item carries attributes or
children of its own, which a token does not.

```xml
<EventStream xmlns:svta="urn:svta:dash:sgai:2026"
             schemeIdUri="urn:svta:dash:sgai-overlay:2026"
             timescale="1000">
  <Event id="201" presentationTime="600000" duration="30000">
    <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay"
                              maxDuration="30000"
                              allowedLayouts="overlay-lower-third squeezeback-l-shape-upper-left"
                              earliestResolutionTimeOffset="20000"/>
  </Event>
</EventStream>
```

#### 5.1.4 `<svta:PauseAdPresentation>` — pause window, new

Declares a **pause window**: a region of the primary timeline in which a
viewer pause triggers a resolution request. Outside every pause window,
a pause triggers nothing.

**The window declares *where*, not how long.** The parent `<Event>`'s
`@presentationTime` and `@duration` bound the region in which a pause
qualifies. They do not schedule a presentation and say nothing about how
long it lasts: the viewer decides that, and it is unknowable when the
document is authored.

**The trigger is the viewer's pause, not the playhead.** Every event in
the base specification is scheduled against presentation time, and a
pause stops presentation time: the media time and the playhead can
change *"if the media engine is instructed with seek or pause
operations"* (DASH §4.2). A window anchored on the timeline and resolved
by a viewer action off the timeline has a precedent in the base
specification: in its nonlinear-playback annex, *"the
Event@presentationTime and Event@duration attributes are used to
indicate the start and the duration of the selection window"* (DASH
§L.3.4.2), and the choice that resolves the window is made by the viewer
(§4.8.6).

`<Event>` attributes are as for an overlay window (§5.1.3): `@id`,
`@presentationTime` and `@duration` are all required.

`<svta:PauseAdPresentation>` attributes:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | yes | `xs:anyURI` | — | The APS endpoint the Player resolves. Returns a non-linear resolution document of family `pause` (§5.2.2). |
| `@maxDuration` | yes | `xs:unsignedLong` | — | The slot cap, declared on every slot like any other. On a pause window it bounds no duration, because the slot has no authored one (§4.5.4). Zero means the window does not fire; an absent value means no ad is presented from the window. |
| `@allowedLayouts` | no | whitespace-separated list of layout tokens | the pause family default (§3.4.3): `pause-fullscreen pause-partial` | The pause surfaces this window admits: `pause-fullscreen`, `pause-partial`, or both. |
| `@earliestResolutionTimeOffset` | no | `xs:unsignedLong` | 60 s in `@timescale` units | How far before the **start of the window** the Player may resolve it. Name, type, units and default as on an overlay window. |
| `@executeOnce` | no | `xs:boolean` | `false` | When `true`, the window yields at most one pause ad for the whole session (§4.5.10). |

**Why the cap is declared on a window whose length it does not bound.**
Every slot declares a cap, and a slot without one presents nothing
(§4.5.4). An exception for the pause family would give that rule a
second reading in one family, and declaring a cap that bounds nothing
costs one attribute. The two statements do not conflict: one governs
what the Publisher declares, the other what the declaration bounds, and
on a pause slot the viewer supplies the length.

**The early-resolution offset is computed against the start of the
window, never against the pause.** A pause has no authored time to
subtract an offset from. The window's start does: it is the moment the
playhead enters the region in which a pause would produce an ad, and it
is what `@presentationTime` already holds.

**The once-per-session bound reuses the base capability with the render
event substituted for the playhead event.** `@executeOnce` keeps its
base name, type and default because it is the same capability: a
Publisher who can bound a timeline opportunity to one execution bounds a
pause opportunity the same way. What consumes the window follows the
base counter: *"Execution counter (number of times alternative MPD
playback successfully started)"* (DASH §5.16.2.2.2), which a failed
attempt leaves untouched — *"The counter E.c has not been incremented
due to the failure, consequently if E.c = 0 the event can still be
executed in the future even if the value of @executeOnce is "true""*
(DASH §5.16.2.2.6, NOTE 3). Here the event the counter observes is the
first rendered frame of a pause ad, not the playhead crossing a
presentation time. Without this statement the attribute would be either
inert on a pause window or a cap of one pause ad, and those readings
differ by every pause after the first.

```xml
<EventStream xmlns:svta="urn:svta:dash:sgai:2026"
             schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026"
             timescale="1000">
  <Event id="301" presentationTime="0" duration="2520000">
    <svta:PauseAdPresentation uri="https://aps.example.com/decision/pause"
                              maxDuration="30000"
                              allowedLayouts="pause-fullscreen pause-partial"
                              executeOnce="true"/>
  </Event>
</EventStream>
```

#### 5.1.5 Overlapping windows of one family

**One family, one stream per Period.** All windows of one family that
share a Period are `<Event>` entries of a single `<EventStream>`, by the
base specification's own rule: *"A Period shall contain at most one
EventStream element with the same value of the @schemeIdUri attribute
and the value of the @value attribute, i.e. all Events of one type shall
be clustered in one Event Stream"* (DASH §5.10.2.1). Two sibling streams
carrying the same SGAI scheme in one Period do not form a conformant
document.

**Overlap is the declaration of a fallback chain.** Two or more windows
of one family whose regions overlap in time are not concurrent
opportunities: the first is the window to serve, and the rest are
backups the Player attempts only when an attempt produces no ad
(§4.5.6). No attribute declares the chain.

**The order is by presentation time, oldest first; equal times break by
position in the stream.** For the linear family this is the base
specification's own order: the execution queue is *"a priority queue of
references to a subset of events in table T, ordered by the
presentation time PRT"* (DASH §5.16.2.2.2). It is not document order,
which governs when an active event is dispatched to the application
(DASH §5.10.2.1), an earlier and separate step. The tie-break by
position is this specification's: the base queue does not order equal
presentation times, and position is what remains once presentation time
stops separating two windows.

**Each window binds what it serves with its own declarations.** A
fallback window's candidates are validated against that window's
`@allowedLayouts`, `@customRegion` and `@maxDuration`, never against
those of the window it stands in for (§4.5.7).

**Considered and not reused.** `BaseURL` alternatives retry the same
resource from another location. The MPD fallback scheme
`urn:mpeg:dash:fallback:2016` (DASH §5.11.3) chains whole presentations
on an unrecoverable playout error. Neither chains two opportunity
windows.

#### 5.1.6 Hybrid breaks

A hybrid break — a linear ad on screen with a non-linear ad composited
on top of it — introduces no construct. It is authored as **two windows
of two families**: a linear event and an overlay window whose regions
coincide, each in the stream of its own family. The Player resolves the
two `@uri` values independently, validates each resolution document
against its own window, and composes the results.

No construct links the two portions. A Publisher wanting a restricted
overlay during a takeover declares that restriction in the overlay
window's own `@allowedLayouts`; one wanting no overlay there declares no
overlay window. A constraint of the form "if the linear ad is from
advertiser X, suppress the overlay" is not expressible, deliberately:
enforcing it in the Player would require the advertiser's identity to
reach the Player, putting commercial data into a contract about what
may be rendered, and competitive separation already belongs to the ADS.
Exclusivity between the portions is obtained from the ADS.

### 5.2 Resolution documents

#### 5.2.1 List MPD — linear

Reused from DASH §8.14. *"1) List MPDs shall have the value of the
MPD@type attribute set to "list". 2) List MPD shall be identified by the
URN "urn:mpeg:dash:profile:list:2024". This URN shall appear in the
MPD@profiles attribute."* Each `<Period>` is one ad of the break, played
in document order: *"a special simplified type of MPDs needed to
represent a playlist of MPDs"* (DASH §G.29.2). A List MPD is a sequence
of ads the ADS already chose and ordered, not a set of alternatives.

`MPD` attributes on a List MPD:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@profiles` | yes | comma-separated list of profile URIs | — | Includes `urn:mpeg:dash:profile:list:2024` (DASH §8.14, rule 2). |
| `@type` | yes | enum | `static` in the base schema | `list` (DASH §8.14, rule 1). |
| `@minBufferTime` | yes | `xs:duration` | — | Base attribute. |
| `@publishTime` | no | `xs:dateTime` | — | The instant the APS produced the document. |

Per-ad `<Period>`:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@id` | yes | `xs:string` | — | Unique within the document. The de-duplication scope of the ad's beacons (§5.5.4). |
| `@duration` | yes | `xs:duration` | — | Declared length of the ad. The Player reads it for drop-before-play evaluation (§4.5.4) without first fetching the sub-MPD. |

| Child | Required | Cardinality | Description |
|---|---|---|---|
| `<ImportedMPD>` | yes, on a Period that presents an ad | 1 | The sub-MPD of the ad's video creative (§5.4). The URL is the element's text content. |
| `<EventStream>` of the callback scheme | no | 0..1 | The ad's tracking schedule, as the base specification's own List MPD example places it (DASH §G.29.2). Alternatively inside the sub-MPD (§5.5.2). |
| `<ServiceDescription>` with `<PlaybackRestrictions>` | no | 0..N | The base per-ad skip restriction, honoured with its base meaning (§5.2.4). |
| `<svta:RenderableAsset>` | no | 0..N | Further presentation options for the same ad, each with `@layout="linear"` and `@form` `image` or `html` (§5.3). They follow the `<ImportedMPD>` in document order, so the video is the first option. |
| `<svta:Click>` | no | 0..1 | The ad's ClickThrough (§5.6). |
| `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>`, `<svta:UniversalAdId>` | no | 0..1 each | Application-level metadata (§5.7). |

**Position of the extension children.** `PeriodType` closes its sequence
with `<xs:any namespace="##other" processContents="lax"/>`, so every
`svta:` child of a List MPD Period is authored **after** every
DASH-namespace child of that Period.

`<ImportedMPD>` is reused unchanged from DASH §5.3.2.6: *"MPDs
referenced in the ImportedMPD element shall be restricted to the
constraints of a single period profile as defined in 8.15"* (DASH
§5.3.2.6.1). Its one attribute:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@earliestResolutionTimeOffset` | no | `xs:double` | `60.0` | Seconds before this Period's start at which the sub-MPD may be fetched. **Seconds**, unlike the same-named attribute on an event, which is in `EventStream@timescale` units. |

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list" minBufferTime="PT1S"
     publishTime="2026-09-25T12:00:00Z">
  <BaseURL>https://ads.example.com/delivery/</BaseURL>
  <Period id="ad-01" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="0">creative-101.mpd</ImportedMPD>
  </Period>
  <Period id="ad-02" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="10">creative-102.mpd</ImportedMPD>
  </Period>
</MPD>
```

Three rules of the List profile bound the reuse. *"List MPDs shall not
contain XLink attributes defined in subclause 5.5"* (rule 3), so remote
resolution goes through `<ImportedMPD>` and nowhere else. *"List MPDs
shall not contain Alternative MPD events"* (rule 5), so no resolution
document declares an opportunity inside itself: every opportunity of
every family is declared in the main MPD. And the profile *"is an
extension of the ISO-BMFF CMAF Profile"* (DASH §8.14), so an inline
Adaptation Set on a List MPD Period — admissible, since *"it may also
contain regular Periods"* (rule 4) — carries only media types of the RFC
4337 registry; the image and HTML options of a linear ad therefore travel
on `<svta:RenderableAsset>` and never on an Adaptation Set.

#### 5.2.2 Non-linear resolution document — new

The APS answers the resolution request of an overlay or pause window
with a **non-linear resolution document**: an MPD carrying one
zero-duration `<Period>` whose only child is an `<svta:OverlayList>`, the
list of candidates.

**Why an MPD carrying a candidate list, and not a List MPD.** Most of
the List MPD's shape is kept: the document is an MPD, document order is
the order of presentation, and video creatives are still sub-MPDs bound
to the Single-Period Static profile. What a List MPD cannot express is
the construct the non-linear case needs. Its Periods are **a sequence to
play**, and the Player plays them all. A non-linear candidate is **a set
of alternatives to choose among** — an ordered list of presentation
options of which the Player renders exactly one — and no construct of
the base specification carries that meaning (§4.8.7). The list is
therefore carried in the extension namespace, inside a document that is
otherwise a conformant MPD.

**Why the single Period declares zero duration.** A Period without an
Adaptation Set conforms only at zero duration: *"At least one
Adaptation Set shall be present in each Period unless the value of the
@duration attribute of the Period is set to zero"* (DASH §5.3.2.2,
Table 4). The document carries no Adaptation Set — each option reaches
its creative through its own URL (§5.3.2) — so `PT0S` is what makes it
conformant, and it states the truth: the Period presents nothing and is
the anchor the list hangs from.

**Why `static`, and why the Full profile.** The document is not a List
MPD and declares neither `type="list"` nor the List profile: every
mention of `list` in the base specification binds it to Linked Periods
and to the alternative-MPD flow, and this document is reached by
neither. `type="list"` alone would be available — the base specification
defines it in its main body, where *"For Media Presentations with
MPD@type set to "list" the constraints of a static Media Presentation
shall apply"* (DASH §5.3.1.4) — but the two properties it would confer,
static and free of XLink, are declared directly here instead. `@profiles`
is mandatory in the base schema, so the document names the base
specification's Full profile, `urn:mpeg:dash:profile:full:2011`, of which
*"All profiles are a subset"* and which *"includes all features and
Segment Types defined in this document"* (DASH §8.1, §8.2.1). Declaring
it enrols the document in no profile built for another flow and mints no
URI; §4.8.12 records what that costs.

**On the name.** *Overlay* in `<svta:OverlayList>` names the non-linear
families as a whole, not the `overlay` layout token: a pause document is
a non-linear resolution document with the same root, and says which
family it answers in `@family`.

`MPD` attributes:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@profiles` | yes | comma-separated list of profile URIs | — | `urn:mpeg:dash:profile:full:2011`. |
| `@type` | no | enum | `static` | `static`. |
| `@minBufferTime` | yes | `xs:duration` | — | `PT0S`; the document buffers nothing itself. |
| `@mediaPresentationDuration` | yes | `xs:duration` | — | `PT0S`, consistent with the single zero-duration Period. |
| `@publishTime` | no | `xs:dateTime` | — | The instant the APS produced the document. |

`<Period>`: exactly one, with `@duration="PT0S"` and exactly one child,
`<svta:OverlayList>`, authored in the position `PeriodType` opens to
foreign-namespace content.

**`<svta:OverlayList>`** — the answer to one resolution request.

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@family` | yes | enum | — | Which family this document answers. Value space below. A Player that requested a slot of one family and receives a document of the other treats the attempt as a failed execution (§4.5.6). |
| `@dismissAfter` | no | `xs:duration` | absent: the slot is **not** dismissible | Whether, and from when, the viewer may dismiss the slot (§5.2.4). |
| `@usableFor` | no | `xs:duration` | absent: usable for as long as the window lasts | How long the document remains usable after the Player received it (§5.2.5). |
| `@onCandidatesExhausted` | on a document whose `@family` is `pause`; absent on an overlay document | enum | a Player reading a pause document without it applies `stop` | What the Player does when the candidates run out while the viewer is still paused (§5.2.6). |

| `@family` value | Description |
|---|---|
| `overlay` | The document answers an overlay window. |
| `pause` | The document answers a pause window. |

**Why the family is declared and not inferred.** A document of the
wrong family carries candidates of a kind the slot does not admit, and
the Player has to recognise that before it looks at any of them
(§4.5.6). The document's own content cannot settle it: a candidate list
with no admissible option in it is also what a mismatched APS
configuration and an ordinary unrenderable answer both look like.

| Child | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:Candidate>` | no | 0..N | The ads offered for the slot, in the order the ADS decided. Zero children is the empty resolution (§5.2.3). |

**`<svta:Candidate>`** — one ad offered for the slot.

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@id` | yes | `xs:string` | — | Unique within the document. The de-duplication scope of the candidate's beacons (§5.5.4). |

| Child | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:RenderableAsset>` | yes | 1..N | The presentation options, in preference order (§5.3). |
| `<EventStream>` of the callback scheme | no | 0..1 | The candidate's tracking schedule (§5.5). |
| `<svta:Click>` | no | 0..1 | The ClickThrough and its click-tracking (§5.6). |
| `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>`, `<svta:UniversalAdId>` | no | 0..1 each | Application-level metadata (§5.7). |

The children appear in the order of the table.

Skeleton:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T12:00:00Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay" dismissAfter="PT5S">
      <svta:Candidate id="c1">
        <svta:RenderableAsset form="image" layout="overlay-lower-third"
                              duration="PT10S"
                              assetUrl="https://cdn.example.com/banner.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0">https://tracker.example.com/imp?ad=c1</Event>
        </EventStream>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

**What a profile check of this document sees.** A profile-conformance
check first removes *"All elements or attributes that are either (i) in
this document and explicitly excluded by ProfA, or (ii) in an extension
namespace and not explicitly included by ProfA"* (DASH §8.1). The
document is therefore checked with `<svta:OverlayList>` gone, and what
remains — one empty zero-duration Period — is valid. The claim the
document makes is the base specification's first test, that the **MPD**
conforms, and not the second, that a **Media Presentation** conforms,
which requires *"at least one Representation in each Period in the
profile-specific MPD"* (DASH §8.1): the document is an answer to a
request, not a presentation to play. Its SGAI content is checked by the
procedure of §4.6, not by a profile.

#### 5.2.3 The empty resolution

An opportunity that resolved to **no ads** is answered with HTTP `200`
and a resolution document that is well-formed and complete and carries
no candidate. It is not an empty body, not a `204`, not a `404`, and not
a document that fails to parse. The distinction is between a document
that says nothing was sold and no document at all: expressing no-fill as
a document keeps an unfilled opportunity reportable as unfilled, and
keeps one error code from meaning two things.

**Non-linear** — the document of §5.2.2 with an empty list:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay"/>
  </Period>
</MPD>
```

**Linear** — a List MPD whose single Period presents nothing:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list" minBufferTime="PT0S">
  <Period id="no-fill" duration="PT0S"/>
</MPD>
```

Both shapes follow from the same two constraints. A document with no
Period does not validate — the schema declares `<xs:element
name="Period" type="PeriodType" maxOccurs="unbounded"/>`, and an omitted
`minOccurs` is 1 — and a Period of non-zero duration needs an Adaptation
Set. One zero-duration Period carrying nothing to present satisfies both,
for both families.

**What the Player does with it is the base specification's own rule.**
For the linear family the base specification lists *"Alternative MPD is
a List MPD, and merge process resulted in no available media"* among the
conditions under which an execution fails, and *"A failed execution
results in smooth continued playback of the main media presentation"*
(DASH §5.16.2.2.6). The same clause lists an event whose `@executeOnce`
has already fired under the same heading — a case that is correct by
design — so the heading means "this event produced no alternative
presentation this time", not "something went wrong". An empty
resolution is a failed execution, the next overlapping window of the
family is attempted, and the opportunity is not consumed (§4.5.6). This
specification extends the same reading to the non-linear families.

#### 5.2.4 Dismissal declaration

**Non-linear families: `@dismissAfter` on `<svta:OverlayList>`.** The
APS declares, per slot, whether the viewer may dismiss it and how soon:

| `@dismissAfter` | Meaning |
|---|---|
| absent | The slot is not dismissible. Dismissal is granted, never assumed. |
| `PT0S` | The slot is dismissible from its first rendered frame. |
| `PTnS` (n > 0) | The slot becomes dismissible n seconds, on the presentation timeline, after its first rendered frame. |

A dismissal ends the **whole slot**, never one ad inside it (§4.5.14).
The declaration travels with the candidates, in the APS's document, and
not in the Publisher's MPD, because it is a property of the advertising
that was sold: an advertiser who bought guaranteed exposure and one who
did not buy the same slot from the Publisher.

**Why not the base skip controls.** The base specification has the
capability twice. The alternative-MPD events carry `@skipAfter`, which
*"describes an offset in time (in fractional seconds) from the beginning
of the alternative presentation till the moment the rest of that
presentation may be skipped by the application in response to a user
action"*, with *"Zero duration implies that skipping is allowed
everywhere"* and *"Default value is PT0S"* (DASH §5.16.5.2). The service
description carries `PlaybackRestrictions@skipAfter` (DASH Annex K,
Tables K.9 and K.18), whose default is likewise `PT0S`. Both default to
skippable everywhere, and this specification makes a slot nobody
declared dismissible **not** dismissible. Reusing either construct would
bring its default with it, and a construct reused under its base name
with the opposite default is one a reader will misread. The event-level
attribute also sits in the wrong document: the Publisher's MPD, where
the property of a sold ad is not known. `@dismissAfter` is therefore a
field this specification defines, recorded as an exception to reuse in
§4.8.10.

**Linear family: the base declarations govern, with their base
meaning.** A linear slot is an inherited base construct, and on it the
base specification already answers the question:

- **The event's `@skipAfter` governs dismissal of the slot**, as the
  base specification defines it: from the declared offset on, *"the rest
  of that presentation may be skipped by the application in response to
  a user action"*, which is the whole alternative presentation — the
  slot. **An event that omits the attribute has the base value `PT0S`**:
  the schema declares `<xs:attribute name="skipAfter"
  type="xs:duration" default="PT0S"/>` (DASH §5.16.6), and a base Player
  treats the omission as skippable everywhere. A Player of this
  specification treats it the same way, so that the two Players behave
  the same on the same linear event. The consequence is stated rather
  than left to be discovered: **the non-dismissible default of the
  non-linear families never governs a linear slot**, because every
  linear event has a skip value under the base schema.
- **`PlaybackRestrictions@skipAfter` in a List MPD** — a
  `<ServiceDescription>` on an ad's Period, as the base specification's
  own example carries it (*"we can skip this ad having played its first 5
  seconds"*, DASH §G.29.2) — **keeps its base meaning**: it governs
  skipping the rest of the presentation in its scope, that one ad, from
  its offset on. It is a per-ad restriction and not a dismissal of the
  slot, so the two declarations govern different actions and neither
  overrides the other: a viewer may skip that ad once its restriction
  allows it, and may end the slot once the event's `@skipAfter` allows
  it. That the two coexist without a precedence rule is this
  specification's statement; the base specification gives none.
- A List MPD carries no `@dismissAfter`.

"Honoured with its base meaning" is the base specification's semantics
and no more: the base attribute says when skipping *may* be offered, and
a Player of this specification offers skipping of a linear slot or ad no
earlier than the base declaration allows. How the offer is presented — a
control, a gesture, a remote button — is out of scope for every family.

#### 5.2.5 Usable lifetime

A resolution obtained ahead of its window buys latency and spends
freshness. A resolution obtained when the playhead entered a half-hour
pause window is half an hour old if the viewer pauses at its end: the
targeting is stale and the advertiser's budget may be spent. The APS is
the only actor that knows how long its own decision stays good, so the
document says so.

| `@usableFor` | Meaning |
|---|---|
| absent | The document remains usable for as long as its window lasts. |
| a duration | The document remains usable for that long after the Player received it, measured on the Player's wall clock. |
| `PT0S` | The document is usable only if it is received at the moment the window fires; one obtained earlier is re-resolved. |

The measurement is from **receipt**, not from `MPD@publishTime`, so that
no clock shared between the APS and the Player is assumed. A lifetime
declared long enough never to expire gives one resolution per window;
one of `PT0S` gives resolution at the moment of the pause. Both are
positions a deployment may hold, and neither requires a different
construct.

**Why a field of this specification.** Within one execution the base
specification fetches the alternative MPD once, somewhere between the
earliest resolution time and the event's presentation time — *"the
precise timing of the resolution is not defined in this document"*
(DASH §5.16.2.2.1) — and a resolved event is a boolean with no lifetime:
*"if true, then the alternative MPD has been successfully fetched and
resolved"* (DASH §5.16.2.2.2). Across executions the base answer exists
and is kept: *"The alternative MPD is resolved at each execution of the
Event"* (DASH §5.16.2.2.6). Nothing bounds how long a resolution fetched
early remains good. HTTP caching directives were considered and not
used: they govern whether a cache may reuse a response, not whether an
ad decision is still valid, and a Player library is not guaranteed to
expose them to the logic that selects the ad.

`@usableFor` applies to the non-linear families. On the linear family
resolution timing is the base specification's, unchanged.

#### 5.2.6 Exhaustion behaviour of a pause document

A pause slot has no authored duration, so the candidates a document
carries may run out while the viewer is still paused. The document
declares what happens then:

| `@onCandidatesExhausted` | Description |
|---|---|
| `repeat` | Present the candidate sequence again from the start, for as long as the pause lasts. Each pass is a new presentation of each ad, and its tracking schedule is executed again. |
| `request-again` | Request a new resolution document for the same pause. A document received this way that carries no candidates, or none the device can render, is treated as `stop` for the rest of that pause. |
| `stop` | Present no further ad; the paused primary frame is shown. |

**The declaration belongs to the APS and not to the Publisher.** A
Publisher-declared limit on how many documents may be served within a
pause would be answered by APS implementations returning defensively
long candidate lists, since one response would be their only
opportunity — the limit would produce what it exists to prevent. `stop`
is what a Player applies when the declaration is missing: it is what the
viewer would see if the mechanism did not exist, and every Player can
perform it.

Whether a second request within one pause is the same opportunity or a
new one is not decided here. The two readings are identical at the
Player — it requests, renders what arrives, and stops on resume — and
differ only in accounting between the APS and the ADS, which this
specification does not observe. What it does fix is the measurement:
how much of the paused interval carried an ad (§5.9), which is the same
however the requests are counted.

### 5.3 `<svta:RenderableAsset>` — the presentation option

An `<svta:RenderableAsset>` is **one** presentation option: a form paired
with a layout, and the creative that realises them. A candidate carries
its options as an ordered list of these elements, and the Player renders
at most one of them.

**Why a new construct.** No construct of the base specification lets a
single ad offer an ordered list of alternative presentations and have
the client render the first it can satisfy. The three that express
ordered preference are each scoped elsewhere, and §4.8.7 records why
none is reused.

#### 5.3.1 Attributes

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@form` | yes | enum | — | The creative-carrier form (§3.5). Value space in §5.3.2. |
| `@layout` | yes | layout token | — | The layout, drawn from §3.4.2. The Player matches it against the window's allowed layouts by exact token. Value space in §5.3.3. |
| `@duration` | yes on a non-linear candidate; absent on a List MPD Period, whose `@duration` applies | `xs:duration` | — | The option's declared duration on the presentation timeline. For a `video` form it is derived by the APS from the sub-MPD's `Period@duration`, which is canonical (§5.4); for `image` and `html` it is the only source. |
| `@assetUrl` | yes | `xs:anyURI` | — | For `video`, the URL of the sub-MPD (§5.4). For `image` and `html`, the URL of the creative itself. |
| `@backgroundUrl` | yes when `@layout` is `squeezeback-double-box-background`; absent otherwise | `xs:anyURI` | — | The advertiser's background image (§5.3.6). |
| `@customRectangle` | yes when `@layout` is `custom`; absent otherwise | rectangle (§5.3.5) | — | Where the `custom` overlay sits. |

The element has no children.

#### 5.3.2 Enum: `@form`, and why the creative URL is an attribute

| Enum value | Description |
|---|---|
| `video` | ISO-BMFF video. `@assetUrl` addresses a sub-MPD conforming to the Single-Period Static profile (§5.4). |
| `image` | A still image at `@assetUrl`, served with one of the image media types of §3.5. |
| `html` | An HTML document at `@assetUrl`, served as `text/html`. Inline script MAY appear and runs under the device's HTML capability contract. |

The concrete media type of an `image` or `html` creative is the one the
server declares when the creative is fetched, and it is one of those §3.5
lists for the form.

**The media axis is closed to image and HTML along the whole resolution
path**, and not by choice. A document reached through `<ImportedMPD>` is
*"restricted to the constraints of a single period profile as defined in
8.15"* (DASH §5.3.2.6.1); under that profile *"The rules for the MPD as
defined in subclause 7.3 shall apply"* (DASH §8.15.2), and *"The
@mimeType attribute of each Representation shall be provided according
to IETF RFC 4337"* (DASH §7.3.1). The base specification never mentions
a still-image or HTML media type at all. A creative that is not ISO-BMFF
therefore cannot be a Representation anywhere on this path, and wrapping
it in an `application/mp4` Representation to satisfy the registry would
add no segment-delivery semantics for the format it wraps — a
workaround, not a carrier.

Four carriers are open for it, and the choice among them is recorded:

| Carrier | Clause | Verdict |
|---|---|---|
| **(a)** Foreign-namespace open content: the URL as an attribute of an element of this specification | DASH §5.2.1 | **Selected.** One named element whose attributes bind the form, the layout and the creative into one option, and whose position among its siblings is the preference order. |
| (b) An application-level `<Event>` whose content carries the URL | DASH §5.10 | Rejected. Its defining property is alignment to presentation time, and a creative's address has no presentation time. |
| (c1) A `SupplementalProperty` whose `@value` carries the URL | DASH §5.8.4.9 | Rejected. When its scheme is unrecognised *"the DASH Client is expected to ignore the descriptor"* — the lighter legacy cost. |
| (c2) An `EssentialProperty` whose `@value` carries the URL | DASH §5.8.4.8 | Rejected. When its scheme is unrecognised *"the DASH Client is expected to ignore the parent element that contains the descriptor"* — the parent goes with it. |

**Why neither descriptor, and it is not placement.** The base schema
declares both descriptors on `<Event>` and `<EventStream>` as well as on
the media elements, and a descriptor there inherits no media-type
constraint, so the descriptor axis is genuinely open. The reason is what
a descriptor holds: one scheme URI and one value string, where an option
is three inseparable facts — form, layout, creative — plus, on two
layouts, a fourth. Encoding the tuple into one delimited value would
invent a micro-syntax where an element with named attributes says the
same thing in a schema. And the list needs the option to be an element
for a second reason: order among elements is the preference order
(§5.3.4), while order among descriptors on a host carries no such
convention in the base specification. (c1) and (c2) are kept apart
because their legacy costs differ; neither is used by any construct of
this specification.

**Why the video creative is an attribute too, and not `<ImportedMPD>`.**
`<ImportedMPD>` is the base specification's element for a video
creative, and it is reused on the linear family, where it sits where the
base defines it: on a Period of a List MPD. Its definition is bound to
that position — a Period carrying it *"is a Linked Period, which will be
further resolved using the content of the imported MPD"*, and *"This
element shall not appear if the value of MPD@type is not "list""* (DASH
§5.3.2.2, Table 4). A non-linear option is not a Period and its document
is not a List MPD. Nesting the element inside an option would use it
where its own clause says it does not appear, with a processing model —
merging the imported Period into the parent — that has nothing to merge
into. The option therefore carries the sub-MPD's URL in `@assetUrl`, and
§5.4 binds the sub-MPD to the Single-Period Static profile explicitly:
the same binding the base specification applies to every imported MPD,
adopted here by statement rather than by position.

#### 5.3.3 Enum: `@layout`

The value space is the closed token list of §3.4.2, subject to one rule
per family:

| Where the option sits | Admissible `@layout` values |
|---|---|
| A List MPD Period (linear) | `linear` |
| A candidate of an overlay document | The overlay-family tokens, `linear`, and `custom` |
| A candidate of a pause document | `pause-fullscreen`, `pause-partial` |

Which of these a given window admits is that window's allowed layouts
(§3.4.3). An option whose `@layout` the window does not admit fails the
check, and the Player moves to the next option in document order
(§4.5.3).

**A `linear` option on an overlay window** is a full-screen takeover:
the primary content is suspended for the length of the option and
resumes from where it was suspended, as with an insertion. It is the
option that needs no concurrent composition, which is why a candidate
offers it last, and a window admits it only by listing it. While the
takeover suspends the primary content the primary timeline does not
advance, so the window's end does not approach; the takeover is bounded
by the cap, and the window resumes with the primary content.

#### 5.3.4 Document order is the preference order

The order of the `<svta:RenderableAsset>` children of a candidate is the
preference order: the Player renders the first option whose form and
layout its device can satisfy and whose layout the window admits
(§4.5.3). On a List MPD Period the `<ImportedMPD>` video is the first
option and any `<svta:RenderableAsset>` children follow it.

**The convention is the base specification's own.** In its fallback
scheme, *"If multiple URLs are provided, the content author expresses
the preferences of using one of those by the order with the first one
having the highest preference"* (DASH §5.11.3). Expressing preference by
document order is consistency with the base specification, and this
specification adds no ranking attribute beside it (§4.8.7).

**Several options, or exactly one.** A candidate with several options
resolves on devices the ADS and the APS know nothing about, which is
what lets one decision serve a heterogeneous population. A candidate
with exactly one is equally conformant and leaves the choice with the
APS, or with the ADS that returned one option to it. The Player-visible
interface is the same either way, and nothing in the document
distinguishes "the APS narrowed the list" from "this is all there was":
the Player's check does not depend on which it was.

#### 5.3.5 The `custom` layout: region and rectangle (optional)

`custom` is **optional for every actor**. A Publisher, an APS and a
Player that do not support it are conformant. It applies to the overlay
family only, and it is the one layout for which this specification
defines a position.

**The rectangle.** Both `@customRegion` on an overlay window and
`@customRectangle` on an option are rectangles in the same notation:

`x,y,width,height`

four integers from `0` to `100`, in percent of the video viewport, with
the origin at the top-left corner, `x` increasing to the right and `y`
increasing downward. A rectangle satisfies `x + width ≤ 100` and
`y + height ≤ 100`.

**The notation reuses the base specification's coordinate convention.**
Its Spatial Relationship Description uses *"an arbitrary origin (0; 0);
the x-axis is oriented from left to right and the y-axis from top to
bottom"* (DASH §H.2.2), places an object by `object_x`, `object_y`,
`object_width` and `object_height`, each a *"non-negative integer in
decimal representation"*, and carries its parameters as *"a
comma-separated list of values"* (DASH §H.2.1). With the reference space
fixed at 100 × 100, that is exactly this rectangle, and its containment
rule — *"the sum of object_x and object_width is smaller or equal to
total_width"* (DASH Table H.1) — is the rule above. The parameter order,
origin, orientation, integer domain and delimiter are therefore the base
specification's. What is not reused is the descriptor that carries them:
*"SRD information shall be contained exclusively in these two MPD
elements (AdaptationSet and SubRepresentation)"* (DASH §H.1), and a
region sits on a slot declaration and a rectangle on a presentation
option, neither of which is either element.

**The region.** A Publisher that admits `custom` lists it in
`@allowedLayouts` and MAY declare `@customRegion`. With no region
declared, the region is the whole viewport, `0,0,100,100`.

**Containment.** An option's `@customRectangle` lies entirely inside the
region the window declared: `xR ≤ x`, `yR ≤ y`, `x + width ≤ xR +
widthR` and `y + height ≤ yR + heightR`. It MAY be smaller than the
region. A rectangle that is not contained is not renderable (§4.5.3).

```xml
<svta:OverlayPresentation xmlns:svta="urn:svta:dash:sgai:2026" uri="https://aps.example.com/decision/custom"
                          maxDuration="15000"
                          allowedLayouts="custom overlay-lower-third"
                          customRegion="60,5,35,30"/>
...
<svta:RenderableAsset xmlns:svta="urn:svta:dash:sgai:2026" form="image" layout="custom" duration="PT15S"
                      customRectangle="65,8,25,20"
                      assetUrl="https://cdn.example.com/custom.png"/>
```

**Why this is not a layout engine.** One rectangle for one optional
overlay layout, bounded by a Publisher region, is not a parallel layout
standard: it declares where one surface goes, and everything inside the
surface is HTML5 and CSS.

#### 5.3.6 Layout composition

This specification declares no positioning vocabulary except the
`custom` rectangle. What it fixes for each layout is **which elements
the layout puts on screen**, because that is what decides what the
layout costs a device (§5.3.7).

**The overlay layouts** — `overlay`, `overlay-corner`,
`overlay-lower-third` — put two elements on screen: the playing primary
content, untransformed, and the ad surface composited over it.

**The L-shape** — `squeezeback-l-shape-upper-left`,
`squeezeback-l-shape-upper-right` — carries exactly **one** ad creative,
an image, a video or an HTML document, and that creative is always
**full-frame, in the background**. The Player shrinks the primary
content into the region the token names and composites it **on top of**
the creative. The "L" is the band of the creative that stays visible
around the shrunk content. The layout puts **two** elements on screen,
and there is no third: the creative already covers the whole frame, so
the region around the content *is* the creative. This is the IAB
underlay model — a full-frame branded creative with a cutout for the
content. The shrunk primary content is not a creative anyone supplies;
it is the main content the Player shrinks.

**The double box** — `squeezeback-double-box` — puts the shrunk primary
content and the ad in two boxes side by side. The two boxes leave bands
uncovered, and without a background those bands render **black**.

**The double box with background** —
`squeezeback-double-box-background` — adds a third element: the
advertiser's **background image** at `@backgroundUrl`, filling the
uncovered bands. The background is always a still image, never video
and never HTML, so it never consumes a video decoder. It is the
advertiser's creative, following the IAB *Double Box Video + Background*
model.

**The background is a composition attribute of the layout, not an
option.** The Player does not walk it the way it walks the ordered
options; it composites it as part of rendering the layout once that
layout is chosen. Modelling it as an option would put it in a list whose
meaning is "render exactly one of these".

**The pause layouts.** `pause-fullscreen` replaces the whole visual
surface for the duration of the pause, and the Player MAY release every
resource held by the primary content and by any overlay to present it.
`pause-partial` is composited over the paused primary frame, which stays
visible around it.

#### 5.3.7 The decoder-and-surface budget

The number and **type** of concurrent elements a layout puts on screen
decide which device classes can composite it. This table is the rule
that makes an option satisfiable or not: the Player evaluates it
(§4.5.3), and an APS holding capability parameters MAY evaluate it too
(§5.8.2). Every layout-and-form pair has a row, so every device class has
a defined outcome for every option.

| Layout | Form of the ad creative | Video decoders | Non-video surfaces | Satisfiable on |
|---|---|---|---|---|
| `overlay`, `overlay-corner`, `overlay-lower-third`, `custom` | `video` | 2 (primary + ad) | none | D1, D2 |
| same | `image` | 1 (primary) | image over video | D1, D3, D4 |
| same | `html` | 1 (primary) | HTML over video | D1, D3 |
| `squeezeback-l-shape-*` | `video` | 2 (full-frame creative + shrunk primary) | none | D1, D2 |
| `squeezeback-l-shape-*` | `image` | 1 (shrunk primary) | image, for the full-frame creative | D1, D3, D4 |
| `squeezeback-l-shape-*` | `html` | 1 (shrunk primary) | HTML, for the full-frame creative | D1, D3 |
| `squeezeback-double-box` | `video` | 2 (primary + ad) | none | D1, D2 |
| `squeezeback-double-box` | `image` | 1 (primary) | image, for the ad | D1, D3, D4 |
| `squeezeback-double-box` | `html` | 1 (primary) | HTML, for the ad | D1, D3 |
| `squeezeback-double-box-background` | `video` | 2 (primary + ad) | image, for the background | D1 |
| `squeezeback-double-box-background` | `image` | 1 (primary) | image for the ad **and** image for the background | D1, D3, D4 |
| `squeezeback-double-box-background` | `html` | 1 (primary) | HTML for the ad **and** image for the background | D1, D3 |
| `pause-partial` | `video` | 2 (paused primary holding its frame + ad) | none | D1, D2 |
| `pause-partial` | `image` | 1 (paused primary) | image over the paused frame | D1, D3, D4 |
| `pause-partial` | `html` | 1 (paused primary) | HTML over the paused frame | D1, D3 |
| `pause-fullscreen` | `video` | 1: on D1 and D2 a free decoder; on D3–D5 the primary content's decoder, released for the pause | none | D1, D2; D3, D4, D5 when the Player releases the primary content's decoder |
| `pause-fullscreen` | `image` | none for the ad | image surface | D1, D3, D4 |
| `pause-fullscreen` | `html` | none for the ad | HTML surface | D1, D3 |
| `linear` (on a linear slot, or a takeover on an overlay window) | `video` | 1, reused sequentially across ad and primary content | none | D1–D5 |
| `linear` | `image` | none while the ad is shown | image surface | D1, D3, D4 |
| `linear` | `html` | none while the ad is shown | HTML surface | D1, D3 |

Three readings are where the outcome stops being obvious:

- **D2 owns two decoders and still declines the double box with
  background.** The blocker is the background image, a surface type D2
  does not composite. The rule is element type, not element count.
- **A linear ad does not take a second decoder, and so neither does an
  overlay composited over one.** During an alternative presentation the
  base specification does not run two presentations at once: *"For the
  duration of the alternative media presentation, the alternative access
  engine outputs media to the media engine, while the main client will be
  paused or be in a listen mode"*, and an access engine in listen mode
  *"does not output media to the media engine"* (DASH §4.2). The linear
  ad occupies the decoder the primary content released. An image or HTML
  overlay on top of it therefore costs one decoder plus one surface —
  the same budget as an image L-shape — and D3 and D4 can satisfy it
  (§7.5).
- **The full-screen takeover is satisfiable on every class**, because
  it needs no concurrent composition. That is what makes it the useful
  last option of a candidate's list. A fullscreen video pause ad is
  satisfiable on every class for the same reason, on the single-decoder
  classes only when the Player releases the paused content's decoder,
  which a pause permits (§4.5.10).

### 5.4 Sub-MPD

Every video creative is described by a **sub-MPD** conforming to the
Single-Period Static profile of DASH §8.15. On a List MPD it is reached
through `<ImportedMPD>`, which binds it to that profile by the base
specification's own rule (DASH §5.3.2.6.1); from a non-linear option it
is reached through `@assetUrl`, and this specification binds it to the
same profile. That profile is the base specification's own home for an
ad creative: its documents *"are usable on their own and correspond to
common practices of storing individual advertisement creatives"* (DASH
§8.15). Routing every video creative through it reuses an existing
interoperability surface, which is why this specification defines no
creative container of its own.

| Property | Value |
|---|---|
| `MPD@profiles` | includes `urn:mpeg:dash:profile:sps:2024` |
| `MPD@type` | `static` |
| `MPD@mediaPresentationDuration` | absent; the Period carries `@duration` |
| `<Period>` | exactly one, with `@duration` |
| `<AdaptationSet>` / `<Representation>` | the creative's media; every Representation's `@mimeType` from the RFC 4337 registry |
| `<EventStream>` of the callback scheme | optional, inside the Period: the ad's tracking schedule (§5.5.2) |

The profile admits no MPD-level `Metrics`, `ServiceDescription` or
`SupplementalProperty` — *"The MPD shall not include any of the
following attributes or elements"*, a list that names all three (DASH
§8.15.2) — so the play-list metric request of §5.9 lives on the main MPD,
and any descriptor a sub-MPD carries sits inside its Period.

**Reconciling the two declared durations.** One ad is described by a
duration twice: in the parent document (a List MPD Period's `@duration`,
or an option's `@duration`) and in the sub-MPD's `Period@duration`. **The
sub-MPD's value is canonical**: it describes the media that exists and
travels with the creative. The parent's value is derived from it by the
APS when it produces the resolution document, and it is the value the
Player reads for drop-before-play evaluation, because it is available
without a second fetch. A disagreement between the two has a fixed
consequence: the cap is enforced against the **actual rendered length**
whatever either declared (§4.5.4). A stale parent value changes what the
Player can predict before playing, and nothing about what it enforces
while playing.

### 5.5 Tracking carrier

Timeline-scheduled beacons — impression, start, quartiles, completion,
and whatever else the ADS schedules — ride the base callback event
scheme. **This specification mints no tracking scheme.** The callback
scheme is already a beacon carrier: *"DASH Callback events are
indications in the content that it is expected by a DASH Client to issue
an HTTP GET request to a given URL and ignore the HTTP response"*, and
*"A content author may use such an event for tracking play-back of
specific content on a server that is not included in the media path"*
(DASH §5.10.4.5.1). A parallel scheme would split tracking across two
carriers for no semantic gain.

#### 5.5.1 Carrier shape

```xml
<EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
             value="1" timescale="1000">
  <Event presentationTime="0">https://tracker.example.com/impression?ad=1</Event>
  <Event presentationTime="2500">https://tracker.example.com/q1?ad=1</Event>
</EventStream>
```

| `<EventStream>` attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@schemeIdUri` | yes | `xs:anyURI` | — | `urn:mpeg:dash:event:callback:2015`. |
| `@value` | yes | `xs:string` | — | `1`, the value the base specification fixes for this scheme (DASH §5.10.4.5.3, Table 47). |
| `@timescale` | no | `xs:unsignedInt` | `1` | Time base of `Event@presentationTime`. |

| `<Event>` attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@presentationTime` | no | `xs:unsignedLong` | `0` | When the Player fires the beacon, in `@timescale` units, measured from the start of **this ad's** presentation (§5.5.3). |
| `@id` | no | `xs:unsignedLong` | — | Identifies the beacon for de-duplication (§5.5.4). |

The beacon URL is the `<Event>` element's **text content**. The base
specification's Table 47 assigns the HTTP URL to the event value, with
`@messageData` marked deprecated, and the base schema declares
`@messageData` `use="prohibited"`.

Which beacons exist, how many, and when, are the ADS's. This
specification fixes the carrier and the timebase; the Player executes
the schedule the document carries.

#### 5.5.2 Where the carrier lives

| Ad | Position of the tracking `<EventStream>` |
|---|---|
| Linear ad | Inside the sub-MPD's Period, or on the List MPD Period of the ad |
| Non-linear candidate, `video` option | Inside the sub-MPD's Period, or directly inside the `<svta:Candidate>` |
| Non-linear candidate, `image` or `html` option | Directly inside the `<svta:Candidate>`; there is no sub-MPD to host it |

Where both positions of one ad carry a stream, the Player fires their
union, reduced by §5.5.4. A linear ad that offers image or HTML options
beside its video carries its tracking on the List MPD Period: a Player
that selects a non-video option never fetches the sub-MPD, and tracking
placed only there would not fire.

**The consequences of the candidate position.** An `<EventStream>`
inside a `<svta:Candidate>` is a baseline element nested in an extension
element, authored for Players that implement this specification: a
Player that does not implement it removes the candidate and everything
in it. Three consequences follow, and a reader arrives at none of them by
default. **Its presentation times resolve against the candidate's own
presentation**, because the stream sits in no Period whose timeline they
could resolve against (§5.5.3). **Schema validation of the MPD does not
reach it**, since the base schema accepts foreign content at that
position without checking it; §4.6 states how it is checked instead.
**The base clustering rule does not reach it either**: a document with
four candidates carries four streams of the same scheme and value, which
inside one Period would break the rule of DASH §5.10.2.1 and here does
not, because after the removal of the extension namespace none of them
is present. The per-candidate de-duplication scope of §5.5.4 stands
where the clustering rule would have stood.

#### 5.5.3 The timebase

Every beacon time in a resolution document is **relative to the start
of the ad's own presentation** — never to the primary timeline, never to
the wall clock. The Player adds the ad's start to each relative value to
obtain the firing point.

| Beacon (10-second ad, `timescale="1000"`) | `@presentationTime` | Fires at |
|---|---|---|
| impression, start | `0` | the ad's first rendered frame |
| first quartile | `2500` | 25 % of the ad |
| midpoint | `5000` | 50 % |
| third quartile | `7500` | 75 % |
| complete | `10000` | the ad's last frame |

The quartiles are the ADS's schedule in this example, not this
specification's: it prescribes no fraction, no granularity and no count.

For a stream in a sub-MPD or on a List MPD Period, the ad's own
presentation is that Period's timeline. For a stream inside a
`<svta:Candidate>`, it is the presentation of the option the Player
selected for that candidate. An `image` or `html` option has no
segment-aligned media to anchor it, so offset `0` is the moment the
creative first becomes visible.

Beacon times are on the presentation timeline, so primary content
playing at a speed other than 1× moves the wall-clock instants at which
beacons fire without moving their scheduled times (§4.5.12).

#### 5.5.4 De-duplication

De-duplication is **scoped to the ad**: the `<svta:Candidate>` on a
non-linear document, the Period on a List MPD. Within that scope,
beacons sharing an `@id`, and beacons carrying the same URL at the same
presentation time, fire once — including across the two positions of
§5.5.2. Across scopes it does not reach: the same `@id` in two
candidates of one document is two beacons, and the Player fires both.

The scope is the ad and not the document because a beacon identifies an
event in one ad's presentation. A wider scope would suppress the second
impression of two ads that happened to share an identifier, which an APS
assembling a document from several upstream decisions has no way to
prevent.

### 5.6 ClickThrough carrier

The resolution document carries an ad's ClickThrough URL and its
click-tracking URLs in one carrier, so that every Player conformant to
this specification reads them the same way.

**Why the callback scheme is right for impressions and wrong for a
click.** A callback event fires at a scheduled presentation time. A
click has none: it happens when the viewer acts, or never. Carrying
click-tracking on the callback scheme would give the activation a
position on a timeline it does not have.

**The base specification is not silent about user action, and this
carrier follows what is there.** `@skipAfter` declares when the
application may skip *"in response to a user action"* (DASH §5.16.5.2):
a user action with a normative consequence, declared in the document and
resolved when the viewer acts. The ClickThrough carrier has the same
shape.

#### 5.6.1 `<svta:Click>`

A child of `<svta:Candidate>` on a non-linear document, and of the ad's
Period on a List MPD, authored after every DASH-namespace child of that
Period (§5.2.1).

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@clickThroughUrl` | yes | `xs:anyURI` | — | The destination the Player opens, or hands to the platform, when the viewer activates the click. |

| Child | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:ClickTracking>` | no | 0..N | One click-tracking URL, as element text. Fired on activation, not at a presentation time. |

```xml
<svta:Click xmlns:svta="urn:svta:dash:sgai:2026" clickThroughUrl="https://advertiser.example.com/landing">
  <svta:ClickTracking>https://tracker.example.com/click?ad=1</svta:ClickTracking>
  <svta:ClickTracking>https://verifier.example.net/c?id=1</svta:ClickTracking>
</svta:Click>
```

Whether a ClickThrough carries click-tracking is the advertiser's
decision. A `<svta:Click>` with no `<svta:ClickTracking>` is complete:
the Player opens the destination and fires nothing.

A ClickThrough or a click-tracking URL carried anywhere other than this
element is not a ClickThrough this specification recognises, and the
resolution document shows the violation by itself.

### 5.7 Application-level metadata

Generic creative metadata with no carrier in the base specification
rides on four extension elements, each an OPTIONAL child of
`<svta:Candidate>` (or of a List MPD Period), at most once, with its
value as element text.

| Element | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:AdSystem>` | no | 0..1 | The ad system that produced the decision. |
| `<svta:AdTitle>` | no | 0..1 | A human-readable title of the creative. |
| `<svta:Advertiser>` | no | 0..1 | A human-readable identifier of the advertiser. |
| `<svta:UniversalAdId>` | no | 0..1 | A registry-scoped identifier of the creative, carried at most on a best-effort basis. |

**Emitting and reading are both optional, and the carrier is
non-interoperable by design.** Nothing obliges an APS to emit these
elements or a Player to read them; a Player that ignores every one of
them is conformant, and a Player that does not implement this
specification removes them as unknown-namespace content without any
effect on the ad. What this specification fixes is that the place exists
and is named. That is the contrast with §5.6: the ClickThrough carrier is
read by every Player conformant to this specification; this one may be
ignored by any.

**No carrier is mandated for the universal ad identifier.** Its role is
reconciliation on the decisioning side, where the upstream ad standards
already carry it; mandating it here would add a field implementations
populate inconsistently and that no Player behaviour depends on.

### 5.8 The resolution request

The Player resolves a window by an HTTP GET against its `@uri`. Two
independent sources contribute query parameters to that URL: the
Publisher's author-declared template (§5.8.1) and the parameters this
specification reserves for the Player (§5.8.2, §5.8.3).

#### 5.8.1 Publisher-declared parameters

The Publisher MAY parameterise the request through the base
specification's extended HTTP GET parameterisation, unchanged. With the
`urn:mpeg:dash:urlparam:2025` scheme, *"An MPD.EssentialProperty element
with the attribute @schemeIdUri having value of
"urn:mpeg:dash:urlparam:2025" shall be present and have no content"*,
and *"The scheme uses a single element, RequestParam of type
ExtendedUrlInfoType"*, which *"may be present in elements such as but not
limited to MPD, Period, AdaptationSet, Representation, Preselection, or
EventStream"* (DASH §I.3.1). Authored inside a window's own
`<EventStream>`, after its `<Event>` entries, a `<RequestParam>` scopes
the template to that family's windows.

| `RequestParam` attribute (as used here) | Required | Type | Default | Description |
|---|---|---|---|---|
| `@queryTemplate` | yes, to contribute query parameters | `xs:string` | — | The template, substituted by the Player at request time (DASH §I.2.2.2). |
| `@includeInRequests` | yes, to reach a resolution request | whitespace-separated list of request types | `segment` | Which requests carry the parameters. |

| `@includeInRequests` value | Description |
|---|---|
| `altmpd` | The base request type: *"all requests for MPDs representing the alternative Media Presentation, as defined in subclause 5.16"* (DASH Table I.4) — the linear family's resolution requests. |
| `urn:svta:dash:sgai-resolution:2026` | The resolution request of an overlay or pause window, which is not an alternative-MPD request. |

**Why a request-type URN of this specification's own, and why it is
safe.** `altmpd` names alternative-MPD requests, and a non-linear
resolution request is not one. The value space admits a request type
named by its owner — *"a URN or tag URI, where the request type semantics
is understood by the client and specified by the URN / tag URI owner. The
client shall drop unknown URIs from the @includeInRequests and
@includeInHeaders strings prior to processing them as specified in this
Annex"* (DASH Table I.4) — so the URN is the base specification's own
extension hook, and the drop rule is what makes it safe for a client that
does not know it.

```xml
<EventStream xmlns:svta="urn:svta:dash:sgai:2026" schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
  <Event id="201" presentationTime="600000" duration="30000">
    <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay"
                              maxDuration="30000"/>
  </Event>
  <RequestParam includeInRequests="urn:svta:dash:sgai-resolution:2026"
                queryTemplate="sid=$urn:mpeg:dash:state:cmcd#sid$"/>
</EventStream>
```

This specification extends the mechanism in no way beyond naming one
request type.

#### 5.8.2 Player-declared capability parameters

This specification reserves query-parameter names a Player MAY attach
to any resolution request to state what its device can render. Which of
them travel is the Player's decision at runtime; no declaration by the
Publisher, the APS or the ADS is required first.

| Parameter | Required | Type | Default | Description |
|---|---|---|---|---|
| `sgaiVideoDecoders` | no | integer, `1` or greater | absent: undetermined | How many video decoders the device runs concurrently, counting the one presenting the primary content. A value of `2` or more states that the device composites a second video over the first. |
| `sgaiImageOverlay` | no | `true` \| `false` | absent: undetermined | Whether the device composites a still image over, or alongside, playing video. |
| `sgaiHtmlOverlay` | no | `true` \| `false` | absent: undetermined | Whether the device composites an HTML surface over, or alongside, playing video. |

The parameters are **inputs about the device** — statements of what it
supports — and not conclusions about which ad experiences can be served;
deriving the second from the first, with §5.3.7, is the APS's work.

The three axes are what separates the device classes of §3.6:

| Declaration | Class |
|---|---|
| `sgaiVideoDecoders=2&sgaiImageOverlay=true&sgaiHtmlOverlay=true` | D1 |
| `sgaiVideoDecoders=2&sgaiImageOverlay=false&sgaiHtmlOverlay=false` | D2 |
| `sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=true` | D3 |
| `sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=false` | D4 |
| `sgaiVideoDecoders=1&sgaiImageOverlay=false&sgaiHtmlOverlay=false` | D5 |

**Why booleans and not a list of surfaces.** A list has no way to say
"no surfaces" that differs from an empty value, and an empty value is
what §5.8.4 forbids. An empty list and an absent parameter would
collapse into one another, and D5 would be indistinguishable from a
Player that declared nothing. Two booleans keep "declares no image
surface" and "says nothing about image surfaces" apart. No fourth axis
is reserved, because a fourth would have to separate two classes the
three already separate.

**Why not the author-declared template.** The base mechanism of §5.8.1
misses on two independent axes. Its payload is session state — *"there
is a need to express knowledge of the current state of the player"*
(DASH §I.4.1) — and its vocabulary names what is playing and what has
run, never a decoder count or a compositing surface. And it is written
by the content author: a Player cannot add an axis to a template it did
not write. The template does admit variables of a third party's scheme,
but *"In case of a client unaware of a particular scheme the string
"<null> " shall be used as a replacement of the unknown scheme"* (DASH
§I.2.3.3) — a placeholder sent where this specification requires that an
unknown value be omitted (§5.8.4).

#### 5.8.3 The slot's declarations, forwarded

When a non-linear window declares `@allowedLayouts`, the Player sends
the declared set to the APS on the resolution request, so that the ads
chosen upstream are already among those the Publisher allows. When it
declares `@customRegion`, the Player sends that too.

| Parameter | Required | Type | Description |
|---|---|---|---|
| `sgaiAllowedLayouts` | yes, on the resolution request of a non-linear window that declares `@allowedLayouts`; absent otherwise | the window's `@allowedLayouts` value, unchanged, each space percent-encoded as `%20` | The layouts the window admits. |
| `sgaiCustomRegion` | yes, on the resolution request of an overlay window that declares `@customRegion`; absent otherwise | the window's `@customRegion` value, unchanged | The region a `custom` option must lie inside. |

```
GET /decision/overlay?sgaiAllowedLayouts=overlay-lower-third%20squeezeback-l-shape-upper-left&sgaiVideoDecoders=1&sgaiImageOverlay=true
```

**When the window declares nothing, nothing is sent**, and the set that
binds both the APS and the Player is the family default of §3.4.3: the
APS already knows it, because it is fixed by this specification, and
sending it would duplicate a rule on every request.

**These two are the exceptions to optional sending.** Every other
reserved parameter is the Player's to send or not; these carry the
Publisher's declarations and not the device's, so the Player forwards
them whenever they exist. Forwarding does not replace the Player's own
check of what comes back (§4.5.3). Linear windows carry no layout
declaration and are outside this rule.

**Why not the template, again.** Writing the allowed layouts into a
`<RequestParam>` template as a literal would duplicate `@allowedLayouts`
in the MPD — two copies of one declaration, free to drift — and writing
it as a computed variable would leave forwarding to whether the
Publisher authored a template, where this specification makes it
unconditional.

#### 5.8.4 Sending, omitting, extending

- Sending a capability parameter is **OPTIONAL**. A Player MAY send all
  three, some, or none.
- A parameter the Player has no value for, or does not disclose, is
  **omitted entirely** — never sent empty or with a placeholder.
- **A reserved parameter that is absent means its value is
  undetermined**: the Player did not determine it, or did not disclose
  it. Absence does not assert that the device lacks the capability. How
  an APS resolves an undetermined value is its own decision: an APS that
  emits no option depending on the undetermined axis and one that
  assumes the most capable case are both conformant, and they emit
  different documents to the same Player. What does not vary is that the
  Player checks whatever arrives before rendering it.
- A request carrying no capability parameter is answered with the
  candidates' options unnarrowed, which is the document an APS holding no
  device view emits; a Player that declares nothing receives the full
  ordered list and makes the choice itself.
- **Every parameter name beginning with `sgai` is reserved** to this and
  later editions. A parameter a Player attaches that is not a reserved
  name carries a vendor prefix of the form `x-<vendor>-`, so that names
  a later edition reserves cannot collide with it.

#### 5.8.5 Two sources on one URL

The reserved names are reserved on the resolution request as a whole. A
Publisher's `<RequestParam>` template draws its parameter names from
outside them, so the two sources compose without collision: the Player
builds the query string the template produces, then appends the reserved
parameters it sends. Any query component already present in `@uri` is
kept, per RFC 3986.

### 5.9 Declaring the pause-delivery metric

Pause-ad delivery is measured with the base specification's play-list
metric, and **this specification defines no metric of its own**. The
metric is *"A list of playback periods. A playback period is the time
interval between a user action and whichever occurs soonest of the next
user action, the end of playback or a failure that stops playback"*
(DASH Annex D.4.6). Two of its fields carry what a pause slot needs: an
entry's `starttype`, whose value space includes `Resume` (resume from
pause), and a rendered stretch's `stopreason`, which includes
`UserRequest` and `Rebuffering`.

**What is measured is the filled fraction, not the number of
opportunities.** The number of pauses is set by the viewer, who decides
when and how often to pause; a figure that moves for reasons no party
influences reports nothing about how well the slot was served. How much
of the paused interval carried an ad can be influenced — by an APS that
returns candidates keeping the slot filled.

**The paused interval is derived, not measured separately**: it runs
from the end of a playback period whose last rendered stretch stopped on
`UserRequest` to the `start` of the next entry whose `starttype` is
`Resume`. Against it, the time the pause ad was on screen is the filled
fraction. A period that stopped on `Rebuffering` is a stall and not a
pause, and no pause window triggered.

The Publisher of content carrying pause windows requests the metric
with the base `<Metrics>` element on the **main MPD**, because
collection is triggered by the service provider: *"The trigger mechanism
is based on the Metrics element in the MPD"* (DASH §5.9.1).

```xml
<Metrics metrics="PlayList">
  <Range starttime="PT0S"/>
  <Reporting schemeIdUri="urn:example:publisher:reporting:2026"/>
</Metrics>
```

The base schema requires at least one `<Reporting>` child. Its scheme is
the Publisher's: the base specification defines the element and leaves
the reporting mechanism to whoever provides one.

The Single-Period Static profile admits no MPD-level `Metrics` (DASH
§8.15.2), so the main MPD is the only place the request can live.

**How a measurement reaches anyone is out of scope**, as it is for the
base specification's own metrics: *"This document does not define
mechanisms for reporting metrics; however, it does define a set of
metrics and a mechanism that may be used by the service provider to
trigger metric collection and reporting at the clients, if a reporting
mechanism is available"* (DASH §5.9.1).

### 5.10 XML schema of the extension namespace

The schema below is normative for the elements and attributes of the
namespace `urn:svta:dash:sgai:2026`. It imports the base MPD schema for
`EventStreamType`. Where a table in this chapter states a conditional
requirement the schema cannot express — for example that
`@backgroundUrl` appears exactly when `@layout` is
`squeezeback-double-box-background` — the table governs, and §4.6 checks
it.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:svta="urn:svta:dash:sgai:2026"
           xmlns:dash="urn:mpeg:dash:schema:mpd:2011"
           targetNamespace="urn:svta:dash:sgai:2026"
           elementFormDefault="qualified">

  <xs:import namespace="urn:mpeg:dash:schema:mpd:2011"
             schemaLocation="DASH-MPD.xsd"/>

  <!-- Layout tokens: the closed list of §3.4.2 -->
  <xs:simpleType name="LayoutTokenType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="linear"/>
      <xs:enumeration value="overlay"/>
      <xs:enumeration value="overlay-corner"/>
      <xs:enumeration value="overlay-lower-third"/>
      <xs:enumeration value="squeezeback-l-shape-upper-left"/>
      <xs:enumeration value="squeezeback-l-shape-upper-right"/>
      <xs:enumeration value="squeezeback-double-box"/>
      <xs:enumeration value="squeezeback-double-box-background"/>
      <xs:enumeration value="pause-fullscreen"/>
      <xs:enumeration value="pause-partial"/>
      <xs:enumeration value="custom"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="LayoutListType">
    <xs:list itemType="svta:LayoutTokenType"/>
  </xs:simpleType>

  <!-- x,y,width,height in integer percent of the viewport (§5.3.5) -->
  <xs:simpleType name="RectangleType">
    <xs:restriction base="xs:string">
      <xs:pattern value="(100|[1-9]?[0-9]),(100|[1-9]?[0-9]),(100|[1-9]?[0-9]),(100|[1-9]?[0-9])"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="FormType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="video"/>
      <xs:enumeration value="image"/>
      <xs:enumeration value="html"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="FamilyType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="overlay"/>
      <xs:enumeration value="pause"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="ExhaustionType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="repeat"/>
      <xs:enumeration value="request-again"/>
      <xs:enumeration value="stop"/>
    </xs:restriction>
  </xs:simpleType>

  <!-- Opportunity declarations (§5.1.3, §5.1.4) -->
  <xs:element name="OverlayPresentation">
    <xs:complexType>
      <xs:attribute name="uri" type="xs:anyURI" use="required"/>
      <xs:attribute name="maxDuration" type="xs:unsignedLong" use="required"/>
      <xs:attribute name="allowedLayouts" type="svta:LayoutListType"/>
      <xs:attribute name="customRegion" type="svta:RectangleType"/>
      <xs:attribute name="earliestResolutionTimeOffset" type="xs:unsignedLong"/>
      <xs:anyAttribute namespace="##other" processContents="lax"/>
    </xs:complexType>
  </xs:element>

  <xs:element name="PauseAdPresentation">
    <xs:complexType>
      <xs:attribute name="uri" type="xs:anyURI" use="required"/>
      <xs:attribute name="maxDuration" type="xs:unsignedLong" use="required"/>
      <xs:attribute name="allowedLayouts" type="svta:LayoutListType"/>
      <xs:attribute name="earliestResolutionTimeOffset" type="xs:unsignedLong"/>
      <xs:attribute name="executeOnce" type="xs:boolean" default="false"/>
      <xs:anyAttribute namespace="##other" processContents="lax"/>
    </xs:complexType>
  </xs:element>

  <!-- Non-linear resolution document (§5.2.2) -->
  <xs:element name="OverlayList">
    <xs:complexType>
      <xs:sequence>
        <xs:element ref="svta:Candidate" minOccurs="0" maxOccurs="unbounded"/>
      </xs:sequence>
      <xs:attribute name="family" type="svta:FamilyType" use="required"/>
      <xs:attribute name="dismissAfter" type="xs:duration"/>
      <xs:attribute name="usableFor" type="xs:duration"/>
      <xs:attribute name="onCandidatesExhausted" type="svta:ExhaustionType"/>
      <xs:anyAttribute namespace="##other" processContents="lax"/>
    </xs:complexType>
  </xs:element>

  <xs:element name="Candidate">
    <xs:complexType>
      <xs:sequence>
        <xs:element ref="svta:RenderableAsset" maxOccurs="unbounded"/>
        <!-- at most one callback EventStream of the base namespace (§4.6) -->
        <xs:any namespace="urn:mpeg:dash:schema:mpd:2011"
                processContents="strict" minOccurs="0"/>
        <xs:element ref="svta:Click" minOccurs="0"/>
        <xs:element ref="svta:AdSystem" minOccurs="0"/>
        <xs:element ref="svta:AdTitle" minOccurs="0"/>
        <xs:element ref="svta:Advertiser" minOccurs="0"/>
        <xs:element ref="svta:UniversalAdId" minOccurs="0"/>
      </xs:sequence>
      <xs:attribute name="id" type="xs:string" use="required"/>
      <xs:anyAttribute namespace="##other" processContents="lax"/>
    </xs:complexType>
  </xs:element>

  <!-- Presentation option (§5.3) -->
  <xs:element name="RenderableAsset">
    <xs:complexType>
      <xs:attribute name="form" type="svta:FormType" use="required"/>
      <xs:attribute name="layout" type="svta:LayoutTokenType" use="required"/>
      <xs:attribute name="duration" type="xs:duration"/>
      <xs:attribute name="assetUrl" type="xs:anyURI" use="required"/>
      <xs:attribute name="backgroundUrl" type="xs:anyURI"/>
      <xs:attribute name="customRectangle" type="svta:RectangleType"/>
      <xs:anyAttribute namespace="##other" processContents="lax"/>
    </xs:complexType>
  </xs:element>

  <!-- ClickThrough (§5.6) -->
  <xs:element name="Click">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="ClickTracking" type="xs:anyURI"
                    minOccurs="0" maxOccurs="unbounded"/>
      </xs:sequence>
      <xs:attribute name="clickThroughUrl" type="xs:anyURI" use="required"/>
    </xs:complexType>
  </xs:element>

  <!-- Application-level metadata (§5.7) -->
  <xs:element name="AdSystem" type="xs:string"/>
  <xs:element name="AdTitle" type="xs:string"/>
  <xs:element name="Advertiser" type="xs:string"/>
  <xs:element name="UniversalAdId" type="xs:string"/>
</xs:schema>
```

The wildcard inside `Candidate` admits one element of the base MPD
namespace, validated strictly against the base schema. A schema document
cannot declare a local element in another target namespace, so the
further constraint — that this element is an `<EventStream>` of the
callback scheme — is stated here and checked by §4.6 rather than by the
schema.

---

## 6. Interfaces

This chapter states the message flows between the four actors and the
contract of each interface. The flows are normative in what they
exchange and in which actor produces and consumes each message; the
diagrams are illustrative.

The Player talks to three kinds of endpoint: the Publisher's CDN (the
main MPD and the primary content's segments), the APS (resolution
requests), and the endpoints the resolution document names (ad media and
beacons). **It never talks to the ADS.** The APS talks to the ADS over an
interface this specification does not define.

### 6.1 The linear flow

```
 Publisher CDN          Player                     APS                 ADS
      |  GET main MPD     |                          |                   |
      |<------------------|                          |                   |
      |  MPD with an      |                          |                   |
      |  alternative-MPD  |                          |                   |
      |  event            |                          |                   |
      |------------------>|                          |                   |
      |                   | between ERT and PRT:     |                   |
      |                   | GET event @uri           |                   |
      |                   | (+ RequestParam altmpd,  |                   |
      |                   |  + reserved parameters)  |                   |
      |                   |------------------------->|  decision request |
      |                   |                          |------------------>|
      |                   |                          |  decision (VAST   |
      |                   |                          |  or other)        |
      |                   |                          |<------------------|
      |                   |  200 List MPD            |                   |
      |                   |<-------------------------|                   |
      |                   | validate, execute at PRT (DASH §5.16.2.2):  |
      |                   | fetch sub-MPDs and ad segments, play the     |
      |                   | Periods in order, enforce the cap, fire      |
      |                   | beacons, resume per insertion / replacement  |
```

1. The Player fetches the main MPD and plays the primary content.
2. Between an event's earliest resolution time and its presentation
   time, the Player issues the resolution request: an HTTP GET of the
   event's `@uri`, with any `RequestParam` template scoped to `altmpd`
   and any reserved parameters it chooses to send (§5.8).
3. The APS obtains a decision from the ADS and returns a List MPD
   (§5.2.1), or an empty resolution (§5.2.3).
4. At execution, the Player validates the List MPD (§4.6, §4.5.2),
   evaluates each Period's declared duration against the cap (§4.5.4),
   fetches each ad's sub-MPD and media, and presents the Periods in
   order (§4.5.5), firing the schedule each carries (§4.5.13).
5. At the end, the primary content resumes as the base specification
   defines: an insertion where the timeline stopped, a replacement at the
   position `@returnOffset` and `@clip` determine.
6. Any failed execution continues down the chain of overlapping linear
   events and then to the primary content (§4.5.6).

**Resolution timing is the base specification's.** The Player resolves
*"when the playhead is between the ERT and PRT; the precise timing of the
resolution is not defined in this document"* (DASH §5.16.2.2.1). The base
specification suggests, informatively, that *"it can be useful to
randomize the actual resolution time"* when many clients share a playhead
position (DASH §5.16.2.2.6, NOTE 1); that is a server-load practice, not
a Player obligation.

### 6.2 The overlay flow

```
 Player                                   APS                        ADS
   |  from the window's ERT, while the     |                           |
   |  window is still open:                |                           |
   |  GET <OverlayPresentation @uri>       |                           |
   |  ?sgaiAllowedLayouts=… (if declared)  |                           |
   |  &sgaiCustomRegion=…   (if declared)  |                           |
   |  &sgaiVideoDecoders=… (optional) …    |                           |
   |-------------------------------------->|  decision request         |
   |                                       |-------------------------->|
   |                                       |  decision                 |
   |                                       |<--------------------------|
   |  200 non-linear resolution document   |                           |
   |  (family="overlay")                   |                           |
   |<--------------------------------------|                           |
   |  at the window's start: check usable lifetime, validate,         |
   |  walk candidates and options, fetch creatives, composite over    |
   |  the playing primary content in sequence, enforce cap and window |
   |  end, fire beacons, honour dismissal and ClickThrough            |
```

1. From the window's earliest resolution time (§4.5.1), the Player
   issues the resolution request, with the forwarded declarations when
   the window declares them (§5.8.3) and any capability parameters it
   chooses to send (§5.8.2).
2. The APS returns a non-linear resolution document with
   `@family="overlay"`, or an empty resolution.
3. When the window starts, the Player confirms the document is still
   usable (§5.2.5), validates it (§4.6, §4.5.2), and for each candidate in
   order selects the first satisfiable option (§4.5.3).
4. It composites the selected forms over the playing primary content one
   at a time (§4.5.8), stopping at the cap or the window's end, whichever
   comes first (§4.5.4), and executes each ad's tracking schedule.
5. A failed execution moves to the next overlapping overlay window
   (§4.5.6); an exhausted candidate list ends at the primary content.

### 6.3 The pause flow

```
 Player                                   APS                        ADS
   |  playhead enters the pause window (early resolution permitted    |
   |  from the window's ERT):                                          |
   |  … or the viewer pauses inside the window:                       |
   |  GET <PauseAdPresentation @uri>?sgaiAllowedLayouts=… (if declared)|
   |-------------------------------------->|-------------------------->|
   |  200 non-linear resolution document   |<--------------------------|
   |  (family="pause", onCandidatesExhausted=…)                        |
   |<--------------------------------------|                           |
   |  on the pause: check usable lifetime; suspend any overlay or     |
   |  linear ad; present the first satisfiable option; on exhaustion  |
   |  apply repeat / request-again / stop; on resume: remove the      |
   |  pause ad within one frame, stop its beacons, restore what was   |
   |  suspended                                                        |
```

1. The Player MAY resolve a pause window from its earliest resolution
   time, computed against the window's start (§4.5.1); otherwise it
   resolves when the viewer pauses inside the window.
2. When a pause begins inside the window, the Player confirms it holds a
   usable resolution — re-resolving if the one it holds expired — and
   honours `@executeOnce` (§4.5.10).
3. It suspends any active overlay or linear ad (§4.5.9), presents the
   pause candidates in order (§4.5.8), and on exhaustion applies the
   document's declared behaviour (§4.5.11).
4. On resume it removes the pause ad within one rendering frame, fires
   none of its later beacons, restores what it suspended, and continues
   the primary content from the suspended position (§4.5.10).

### 6.4 The resolution request

| Property | Value |
|---|---|
| Method | HTTP GET |
| URL | The window's `@uri`, with the query component built as §5.8.5 describes |
| Publisher-declared parameters | From `<RequestParam>` templates scoped by `@includeInRequests`: `altmpd` for linear windows, `urn:svta:dash:sgai-resolution:2026` for overlay and pause windows (§5.8.1) |
| Forwarded declarations | `sgaiAllowedLayouts` and `sgaiCustomRegion`, whenever the window declares them (§5.8.3) |
| Capability parameters | `sgaiVideoDecoders`, `sgaiImageOverlay`, `sgaiHtmlOverlay`, each OPTIONAL and omitted rather than emptied (§5.8.2, §5.8.4) |
| Other parameters | Vendor-prefixed, `x-<vendor>-…` (§5.8.4) |
| Success response | `200` with a resolution document of the requested family (§5.2) |
| No-fill response | `200` with an empty resolution (§5.2.3) |

The parameters the Publisher arranges with its APS, beyond the ones this
specification reserves, remain bilateral.

### 6.5 Interface contracts

| Source → target | Transport | Payload | Direction | What a failure means |
|---|---|---|---|---|
| Player → Publisher CDN | HTTP(S) | main MPD, primary segments | request / response | Base behaviour; outside this specification. |
| Player → APS | HTTP(S) | resolution request (§6.4) → resolution document (§5.2) | request / response | Every attempt that produces no ad — no response, a non-`200` status, an unparseable or invalid body, an empty resolution, a document of the wrong family — is a failed execution (§4.5.6). |
| Player → ad CDN | HTTP(S) | sub-MPDs, ad segments, image and HTML creatives | request / response | The ad is aborted and the primary content continues (§4.5.16). |
| Player → tracking endpoints | HTTP(S) GET | callback beacons and click-tracking | fire and forget | The response is ignored; a failed beacon never affects the ad or the primary content (§8.2, E13). |
| APS → ADS | bilateral | decision request and decision document | bilateral | Outside this specification. What reaches the Player is a resolution document, an empty resolution, or no document. |

All transport is HTTPS in production. Authentication, DRM and token
exchange layer on top and are outside this specification.

### 6.6 From a decision document to a resolution document

**The conversion is the APS's and is not defined here.** The ADS emits a
decision in its own format — typically VAST, though the ADS is not bound
to VAST and MAY emit another format agreed with the APS — and the APS
builds the resolution document from it. This specification defines the
document the conversion produces, not the conversion.

What the resolution document can express is what makes the conversion
possible for the ad behaviours a VAST-based decision carries today:

| Behaviour in the decision | Where it lands in the resolution document |
|---|---|
| The ads of a break, in order | List MPD Periods (§5.2.1) or candidates (§5.2.2), in document order |
| A linear creative and its duration | A sub-MPD (§5.4) and the Period's `@duration` |
| A non-linear creative (image, HTML, video) with its placement | A `<svta:RenderableAsset>` with `@form`, `@layout` and `@duration` (§5.3) |
| Several creatives or placements for one ad | Several options on one candidate, in preference order (§5.3.4) |
| Timeline tracking (impression, start, quartiles, completion, …) | Callback events relative to the ad's presentation (§5.5) |
| ClickThrough and click-tracking | `<svta:Click>` (§5.6) |
| Ad system, title, advertiser | The optional metadata elements (§5.7) |
| Skippable / dismissible after an offset | `@dismissAfter` on a non-linear slot (§5.2.4); on a linear slot, the base declarations |
| No ads | The empty resolution (§5.2.3) |

Annex A (linear) and Annex C (non-linear) carry illustrative worked
examples of the conversion from a VAST response. They are illustrative:
they constrain no implementation and define no semantics.

---

## 7. Expected behaviour

### 7.1 How to read this chapter

Each section states, for one scenario, what each actor does, in the
normative terms of chapters 4 and 5. The device-class outcomes follow
from §5.3.7 and are summarised in §3.6; the annexes walk each scenario
end to end with complete documents. Where a scenario involves an actor
with nothing scenario-specific to do, that actor is not repeated.

### 7.2 Linear ad break — pre-roll, mid-roll, multi-ad break

- **Publisher.** Declares an `<InsertPresentation>` (on-demand content)
  or `<ReplacePresentation>` event with `@maxDuration`, at the start of
  the timeline for a pre-roll or inside it for a mid-roll, and does not
  prescribe how many ads fill it.
- **ADS.** Decides N ads and their order, within the declared envelope.
- **APS.** Returns a List MPD with one Period per ad, in the ADS's order,
  each with its `@duration`, its `<ImportedMPD>`, and its tracking.
- **Player.** At execution: presents the Periods back to back in order;
  MAY drop before play an ad whose declared duration would pass an
  insertion cap; trims at the cap against actual length; on a
  replacement, ends at the end `@clip` fixes; stops beacons at a trim;
  resumes the primary content as the event type defines. Every device
  class can present a linear break, because a linear ad and the primary
  content are sequential on one decoder; a second decoder, where
  present, MAY pre-buffer the next ad, which is a Player implementation
  detail with no effect on the Publisher's rules.
- **Playback speed.** At 1.5× or 2×, the ad plays at the same speed and
  its wall-clock length is `duration / playback_speed`; the cap and the
  beacon schedule are unchanged on the presentation timeline.

### 7.3 Overlay

- **Publisher.** Declares an overlay window with a cap, and, optionally,
  the layouts it allows.
- **APS.** Returns candidates whose options are within the forwarded set
  or the family default, in preference order, typically several forms
  per candidate so that one answer serves every device class.
- **Player.** Walks candidates in order and each candidate's options in
  order, and renders the first option its device and the window both
  admit, composited over the primary content with HTML5 and CSS; removes
  it when the cap or the window's end is reached. The primary content
  keeps playing throughout. D5, which composites nothing over video,
  skips the window unless the window admits `linear` and a candidate
  offers the takeover.

### 7.4 Sequenced forms within one slot

A 30-second overlay slot whose document declares ad A (10 s), then B
(10 s), then C (10 s) is presented as A, then B, then C, each starting
when the previous ends, one on screen at a time. The Player enforces the
cap against the cumulative duration and trims or drops as §4.5.4 states.
Sequencing inside one slot is independent of the choice among
overlapping windows (§4.5.6): the chain selects which window is served,
the sequence governs what that window's document presents.

### 7.5 Hybrid: a linear ad with a concurrent overlay

- **Publisher.** Declares a linear event and an overlay window over the
  same region, the overlay typically restricted — for example
  `allowedLayouts="overlay-lower-third"`, no squeezeback over a takeover.
- **APS.** Answers the two requests independently.
- **Player.** Validates each document against its own window and
  presents the linear ad with the selected overlay composited on top. The
  budget is one decoder for the linear ad — it holds the decoder the
  primary content released (§5.3.7) — plus one surface for the overlay:
  D1 renders any overlay form; D2 a video overlay on its second decoder,
  declining image and HTML; D3 an image or HTML overlay; D4 an image
  overlay, declining HTML; D5 the linear ad alone.
- **What is not linked.** The two portions are selected independently;
  no construct makes one depend on the other (§5.1.6).

### 7.6 Pause-triggered ad

- **Publisher.** Declares a pause window over the region of the timeline
  in which a pause may carry an ad, with a cap (which bounds nothing
  here), optionally the pause surfaces it allows, and optionally
  `@executeOnce`.
- **APS.** Returns pause candidates, a declared exhaustion behaviour,
  and, where its decision goes stale, `@usableFor`.
- **Player.** On a pause inside the window: presents the first
  satisfiable pause option, fullscreen or partial as its layout says;
  on exhaustion applies the declared behaviour; on resume removes the
  pause ad within one frame and continues from the paused position. A
  pause outside every window produces nothing.
- **Device classes.** D1 presents any pause form. D2 presents a video
  pause ad, on its second decoder over the paused frame or fullscreen,
  and declines image and HTML. D3 and D4 present image (and, on D3, HTML)
  pause ads over the paused frame, and MAY present a fullscreen video by
  releasing the paused content's decoder. D5 declines every form
  composited over the paused frame and MAY present a fullscreen video in
  the same way; declining is equally conformant.
- **Live content.** The presentation time stays frozen inside the window
  for as long as the viewer is paused; the resume position is a Player
  action after the resume (§4.5.10, §8.8).

### 7.7 Cross-family priority

- **Overlay, then pause.** An overlay is on screen and the viewer pauses
  inside a pause window: the overlay is suspended, its window's clock
  frozen with the primary timeline, and the pause ad takes the screen.
  On resume the pause ad goes and the overlay returns, continuing where
  it stopped, if its window is still open; otherwise the surface stays
  clear.
- **Linear, then pause.** A linear ad is on screen and the viewer pauses
  inside a pause window: the pause ad is presented and the linear ad
  suspended; on resume the linear ad continues from where it stopped.
- **D5.** Neither surface renders unless a fullscreen video pause ad is
  offered and the Player releases its decoder; the viewer's pause and
  resume otherwise have no ad-related effect.

### 7.8 Overlapping windows of one family

The Player attempts the oldest window; when it produces an ad, the other
windows are not touched. When it produces none — for any reason in the
table of §4.5.6, a well-formed empty resolution included — the next is
attempted, and each window's candidates are validated against that
window's own declarations. When the chain is exhausted, the primary
content continues. Window selection is the same on every device class;
the device class affects only what renders from the chosen window.

### 7.9 A Player that predates this specification

- **What it does.** It does not recognise the SGAI schemes or namespace,
  removes them, and plays the primary content. It never issues a
  non-linear resolution request, never reads a ClickThrough carrier, and
  fires no beacon of an ad it never presents. On a linear break it
  behaves as a base Player: it plays the List MPD's `<ImportedMPD>` video
  of each Period and ignores the SGAI children beside it.
- **What the viewer sees depends on the Publisher's authoring choice, and
  that choice depends on the content.** For **live** content the
  opportunity is an expected loss on such a Player: the primary content
  plays on. For **on-demand** content the Publisher MAY author a standard
  linear break with base constructs alongside the SGAI window; such a
  Player plays the standard break. A Player of this specification
  executes that break as well — it is a base event, resolved as the base
  specification defines — and additionally takes the SGAI path. Because the Publisher cannot tell from the
  manifest which Player will read it, the fallback is authored
  unconditionally for on-demand content.
- **The outcome does not vary by device class.** It depends on the
  Player's version and on the content type, not on the hardware.

### 7.10 Viewer dismissal

- **Non-linear.** When the APS declared `@dismissAfter`, the Player makes
  dismissal available from that offset; when the viewer dismisses, the
  whole slot ends — no further ad, no further option — the primary
  content continues from where it stands, and the beacons scheduled
  after the dismissal are not fired. With no declaration, the slot is
  not dismissible.
- **Linear.** The event's `@skipAfter`, present or defaulted, and any
  `PlaybackRestrictions` in the List MPD govern as the base specification
  defines them.
- **Pause.** A dismissed pause ad gives the viewer the paused frame back
  without resuming.

### 7.11 Early resolution

A Player MAY resolve an overlay or pause window from its earliest
resolution time. When the window fires, a resolution past its usable
lifetime is replaced by a fresh one, and a fresh one that yields nothing
is an empty resolution — the expired one is never presented. A Player
that resolves only at firing is equally conformant.

### 7.12 Runtime failure during an accepted ad

A decode error, an unfetchable ad segment or a network loss mid-ad
aborts that ad, and the primary content continues without a visible
artefact (§4.5.16). A beacon that fails is not a runtime failure of the
ad.

---

## 8. Implementation notes

*This chapter is informative.*

### 8.1 What this chapter is

Guidance for implementers: how the normative rules combine when
something goes wrong, and what to do in the cases the normative text
leaves to the implementation. Every row of §8.2 restates obligations
from chapters 4 and 5 so the table can be read on its own; where the
implementation has a choice, the table says what the choice is and what
this chapter recommends.

### 8.2 The conditions, and what to do about each

| ID | Condition | What the Player does | Implementation choice | Other actors |
|---|---|---|---|---|
| E1 | The resolution request fails at the transport level (unresolvable name, refused connection, TLS failure, timeout) or returns a final status other than `200`, including an APS that refuses to answer because a capability parameter was absent. | Treats the attempt as a failed execution and attempts the next overlapping window of the family; with none left, continues the primary content (§4.5.6). | Retrying the same window before giving up on it (§8.4). | Publisher: declares a fallback window where continuity matters. APS: answers without any capability parameter. |
| E2 | A `200` whose body does not parse, or does not validate (§4.6). | Failed execution; nothing from that document is rendered. | Logging the failure. | APS: emits a document that passes all four steps of §4.6. |
| E3 | A `200` carrying a well-formed document of the wrong family. | Failed execution; none of its candidates is presented in the slot; the chain continues (§4.5.2, §4.5.6). | Reporting the mismatch — it is the one condition an operator cannot diagnose from the screen. | APS: answers the family that was requested. |
| E4 | A `200` carrying an empty resolution. | Failed execution; the chain continues; the attempt is not an execution, so an `@executeOnce` event stays executable and a once-per-session pause window stays available (§4.5.6, §4.5.10). | Reporting the opportunity as **unfilled** rather than failed. | APS: expresses no-fill as an empty resolution, never as an error. ADS: none — no-fill is legitimate. |
| E5 | A resolution arrives late — after its window opened, or after it closed — or a resolution obtained early has expired when the window fires. | Linear: the base model, with `@clip` shortening a late replacement. Non-linear: an expired resolution is replaced, never presented (§4.5.1). A document arriving after the window closed, or after the pause ended, is discarded; one arriving while the window is still open is presented for what remains of it (§8.5). | How long to wait for a pending request (§8.5). | Publisher: may set the offset to `0`. APS: declares `@usableFor` when its decision goes stale sooner than the window. |
| E6 | The slot declares no `@maxDuration`, or declares zero. | No ad from that slot; with zero, the opportunity does not fire (§4.5.1). | Reporting the defective declaration. | Publisher: a cap on every slot. |
| E7 | No option of a candidate is satisfiable on the device. | Skips the candidate; after the last, continues the primary content; not a failed execution of the window (§4.5.3). | Reporting the skip. | APS: several options in preference order serve devices it knows nothing about. |
| E8 | An option's layout is not admitted: outside §3.4.2, outside the window's allowed layouts or its family default, a `custom` option the Player does not support, or a rectangle outside the region. | The option is not rendered; the next option is tried; the window that served the candidate is the one checked (§4.5.3, §4.5.7). | Reporting the rejected token. | Publisher: tokens from §3.4.2 only. APS: options within the forwarded set or the family default, rectangles within the region. |
| E9 | A creative is served with a media type outside §3.5, or disagrees with its option's `@form`. | Renders nothing its device cannot render (§4.5.3). | Skipping the candidate is permitted and is what this chapter recommends (§8.6). | APS: admissible creatives only. |
| E10 | The cap is reached: a declared duration would pass it, or an actual length exceeds the declared one. | Trims at the cap against actual length, stops beacons there, never extends the slot; converts durations to the cap's timescale rounding up; accrues nothing while the timeline is stopped (§4.5.4). | Dropping before play on the declared duration. | ADS: not required to respect the cap. |
| E11 | Rendering an accepted ad fails: an ad segment returns an error, a decode error, a network loss. | Aborts the ad and continues the primary content (§4.5.16). | Retrying a segment before aborting; moving to the next candidate rather than ending the slot. | APS: creatives reachable for the slot's duration. |
| E12 | An event scheme, element, attribute or namespace the Player does not implement. | Ignores it with its subtree and keeps playing (§4.5.13). | Ignoring the metadata carrier entirely. | Publisher and APS: every construct at an extension point (§4.7). |
| E13 | A beacon or click-tracking request fails, or a beacon falls after a trim, a pause-ad dismissal on resume, or a viewer dismissal. | The ad and the primary content are unaffected; no beacon fires after a trim, after the pause-to-play transition of a pause ad, or after a dismissal; each beacon fires once within its ad (§4.5.13, §4.5.10, §4.5.14). | Retrying a failed beacon. | APS: beacons on the ad's own timebase. ADS: owns the schedule. |
| E14 | A document implies two non-linear forms at once, or a pause begins while an overlay or a linear ad is on screen. | One non-linear form at a time, in document order; the pause ad takes priority and what it displaced is restored on resume (§4.5.8, §4.5.9). | Releasing resources for a fullscreen pause ad. | No actor can invert the priority. |
| E15 | Pause candidates run out while the viewer is still paused, or a once-per-session window is already consumed. | Applies the declared behaviour, `stop` by default; on a consumed window leaves later pauses untouched (§4.5.11, §4.5.10). | Reporting the applied behaviour. | APS: declares the behaviour. |

**Three kinds of fall-through, kept apart.** *Window-level* (E1–E4):
the next overlapping window of the family, then the primary content.
*Candidate-level* (E7–E9): the next candidate of the document already
obtained, then the primary content — never the next window, because a
document of the right family carrying candidates is not a failed
execution. *Ad-level* (E11): the ad is aborted and the primary content
continues. In all three, "uninterrupted" means no freeze, no blank slate,
no error surface the application did not opt into, and no beacon for the
opportunity that failed.

### 8.3 Order of precedence

When several conditions coincide, evaluate them in this order:

1. **Transport** (E1): no document, so nothing downstream applies.
2. **Document** (E2, E3, E4, E5): unusable, misrouted, empty, late or
   expired. E2 to E4 put the Player on the chain of §4.5.6.
3. **Declarations** (E6, E8, E9, E10 before play): the serving window's
   declarations, checked before rendering. E6 first: a slot with no cap
   yields nothing.
4. **Rendering** (E7, E11).
5. **Playback** (E10 during play, E14, E15).
6. **Tracking** (E13), which never aborts an ad.

E12 is orthogonal: an unknown construct is ignored wherever it appears.

### 8.4 Retrying a resolution request

The normative rule is what a failed attempt leads to (§4.5.6), not how
hard the Player tries before calling an attempt failed. Retrying the same
window is an implementation choice, and this chapter recommends keeping
every retry inside the interval in which the window could still produce
an ad:

- **Linear:** between the earliest resolution time and the event's
  presentation time, as the base specification resolves. The base
  specification notes that *"a previous failure to resolve the MPD of the
  same event does not impact the current resolution"* (DASH
  §5.16.2.2.6).
- **Overlay:** before the window's end, and in practice early enough
  that the ad can still be presented for a useful part of the window.
- **Pause:** while the viewer is still paused.

A bounded number of retries with an increasing delay between them keeps
a struggling APS from being overwhelmed by the population of Players
that share a playhead position. Once the Player stops retrying, the
attempt is a failed execution and the next window is attempted. No
retry count, backoff or timeout is normative, and a Player that makes a
single attempt is conformant.

### 8.5 Late documents

A resolution may arrive after the moment it was needed.

- **Linear.** The base model governs: execution happens at the event's
  presentation time with what has been resolved, and a replacement that
  starts late is shortened to the scheduled end under the default
  `@clip="true"`.
- **Overlay.** A document that arrives while the window is still open is
  presented for what remains of the window: the candidates start at
  arrival, in order, and the presentation ends at the cap or the window's
  end, whichever comes first (§4.5.4). This uses as much of the
  opportunity as remains, and the window's end still bounds it. A
  document that arrives after the window closed is discarded, and the
  attempt is a failed execution of that window.
- **Pause.** A document that arrives after the viewer resumed is
  discarded: a pause ad exists only while the content is paused.
- **Abandoning a pending request.** A Player stops waiting for a request
  at the latest when the document could no longer be used — the window's
  end, or the resume — and stopping earlier is recommended when a
  fallback window could still be attempted in time.

Resolving early (§4.5.1) is what keeps these cases rare: the base
default of 60 seconds exists so that a resolution does not have to fit
inside the window it serves.

### 8.6 A creative whose media type is not admissible

A creative served with a media type outside §3.5 is a signal that the
APS, or the Publisher, is not conformant. A Player cannot render what its
device cannot render. When the device *can* render it — a JavaScript
payload a browser engine would execute, an SVG an image decoder happens
to accept — the normative text permits the Player to skip the candidate
and does not require it. **Skipping the candidate is recommended**: a
creative outside the admissible set is outside what the Publisher's
declarations were written against, and rendering it would put on screen
something none of the validation in chapter 4 has checked. Rendering it
remains conformant.

### 8.7 Device-class fallbacks

- **Order the options from richest to most robust.** The takeover
  (`linear`, video) is satisfiable on every class; an image option is
  satisfiable wherever an image surface exists; a video overlay needs a
  second decoder. A candidate that ends with the takeover — where the
  window admits it — resolves on every device class.
- **Count element types, not only decoders.** D2 has two decoders and no
  non-video surface: an option whose creative or background is an image
  fails there (§5.3.7).
- **An APS that narrows from capability parameters** keeps the remaining
  options in the decision's order (§4.4). Keeping the last robust option
  as well protects against a device whose state changed after the
  request; an APS that emits a single option accepts that risk, and the
  Player then skips the candidate if its own check fails.
- **Declaring capabilities narrows what arrives, not what is checked.**
  The Player checks every option it receives, including one the APS
  derived from the Player's own declaration: the device's state may have
  changed since the request, and the APS may have derived wrongly.

### 8.8 The live freeze and the time-shift buffer

In live content the presentation time stays frozen inside the pause
window for the whole pause (§4.5.10), and the pause ad stays admissible
for as long as the viewer is paused. The live stream keeps advancing,
and the time-shift buffer keeps moving with it. Where the Player resumes
is decided after the resume, and the base specification bounds it: the
resumption point is clipped *"to the timeshift buffer (i.e. the time
interval between TSBS and PHPLE)"* (DASH §5.16.2.2.5), and *"If RT is in
the past, the playback shall start from the oldest available media
segment (the edge of the timeshift buffer)"* (DASH §5.16.4, Table 62),
whose NOTE names the cause: *"The above can happen in case a user pauses
the alternative Media Presentation."*

The two rules therefore govern different moments and do not conflict.
While the viewer is paused, the freeze holds, whatever
`MPD@timeShiftBufferDepth` is. At the resume, the pause ad is removed
within one frame, its later beacons are not fired, and the Player
resumes at a position the base rule admits: the frozen position if the
buffer still holds it, the oldest available segment if it does not, or
the live edge if the Player chooses to jump there. None of these is part
of the pause window.

### 8.9 Resolving a pause window

A pause window may be long — a whole programme — and a pause may come at
any point in it. Two strategies are both conformant:

- **Resolve at the pause.** Always fresh, at the cost of the viewer
  waiting for the APS with the surface already due.
- **Resolve early and re-resolve on expiry.** From the window's earliest
  resolution time, holding the document until the pause and replacing it
  if `@usableFor` has run out.

The APS chooses the trade-off through `@usableFor`: a short lifetime
forces fresh decisions; an absent one keeps one resolution for the whole
window. On a once-per-session window, a Player that resolved early and
never presented the ad has not consumed the window.

### 8.10 Tracking-only decision entries

A decision may carry an entry with tracking and no creative. The
resolution document has no place for an ad with nothing to render: every
option carries a creative. What the APS does with such an entry — omit
it, or handle it on the decision side — belongs to the APS-to-ADS
contract. What the Player observes is only what reaches the document: a
candidate with a renderable option, or no candidate.

### 8.11 Surfacing conditions to the application

Everything in the "implementation choice" column of §8.2 that reports,
logs or exposes a condition is non-normative: no event names, payloads or
delivery mechanism are defined, and a Player that exposes nothing is
conformant. Two distinctions carry most of the operational value and are
worth exposing: **unfilled** (E4) versus **failed** (E1, E2, E3), and the
misrouted document (E3). One boundary is normative: an error surface is a
visible artefact, and rendering one breaks the continuity guarantee
unless the application explicitly opted in.

### 8.12 Deriving the pause-delivery measurement

From the `PlayList` metric (§5.9), for each pause:

1. Find a playback period whose last rendered stretch has
   `stopreason` `UserRequest`. Its end is the start of the pause.
2. Find the next entry whose `starttype` is `Resume`. Its `start` is the
   end of the pause.
3. The paused interval lies between them. A period that stopped on
   `Rebuffering` is a stall and is not counted.
4. The filled fraction is the time a pause ad was on screen within that
   interval, divided by the interval.

The measurement counts filled time, not opportunities: how often a
viewer pauses is theirs to decide and reports nothing about how well the
slot was served.

### 8.13 What this edition leaves open

These points are open in the sense that the edition defines no answer
and implementations are free; none of them leaves a Player behaviour
undefined.

- **Whether a second request within one pause is the same opportunity or
  a new one** (§5.2.6): accounting between the APS and the ADS, which
  this specification does not observe.
- **Whether the document should record that the APS narrowed the
  options.** A single-option candidate reads the same whether the APS
  filtered or not (§5.3.4); the Player's check does not depend on it.
- **Signalling support for `custom`.** A Player forwards `custom` in
  `sgaiAllowedLayouts` whether or not it supports the layout, and no
  capability parameter says which; only a fallback option after the
  `custom` one protects a Player that does not support it.
- **Audio during a non-linear form.** This edition does not state whose
  audio plays while a video ad and the primary content are on screen
  together. The IAB guidelines describe the default execution of
  overlays and squeezebacks as requiring no audio.
- **A hybrid break over an insertion.** An insertion stops the primary
  timeline, and an overlay window is anchored on it, so the window does
  not advance during the linear ad. The annexes author hybrid breaks
  over replacements, where the primary media time keeps progressing.
- **Per-option tracking and ClickThrough.** Tracking and the
  ClickThrough are carried per candidate; options of one candidate with
  different durations share one schedule.
- **An Interoperability Point for the SGAI constructs** (§4.8.12): not
  minted; conformance rests on this specification's schema and
  validation procedure.

---

# Annexes

## Annex A — Pre-roll

*This annex is informative.*

### A.1 The scenario

A viewer starts an on-demand film. Before its first frame, the Publisher
wants a linear break of at most 30 seconds, with a clean handoff to the
film: no non-linear ad over the break or over the opening of the film.
How many ads fill the 30 seconds is the ADS's decision; here it returns
two, of 15 and 10 seconds. The second may be skipped after its first 5
seconds; the break as a whole may not be skipped.

On-demand content can stop its timeline for an ad, so the Publisher
declares an insertion (§5.1.1): the film's timeline stays at zero while
the break plays and starts from its first frame afterwards. The clean
handoff needs no construct: the Publisher declares no overlay window over
this region (§5.1.6).

### A.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static" mediaPresentationDuration="PT1H42M"
     minBufferTime="PT2S">
  <BaseURL>https://cdn.example.com/vod/film-2201/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="1" presentationTime="0" duration="1000">
        <InsertPresentation uri="https://aps.example.com/v1/linear/preroll/film-2201"
                            maxDuration="30000"
                            earliestResolutionTimeOffset="0"
                            executeOnce="true"
                            skipAfter="PT30S"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="360000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" mimeType="video/mp4" codecs="avc1.640028"
                      bandwidth="6000000" width="1920" height="1080" frameRate="24"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="24"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="192000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

What each declaration on event `1` does:

| Declaration | Effect |
|---|---|
| `maxDuration="30000"` | The cap: 30 000 units of `timescale="1000"`, i.e. 30 s of cumulative presentation (§4.5.4). |
| `earliestResolutionTimeOffset="0"` | ERT = 0 − 0 = 0: the Player resolves at start-up. The default of 60 s would give a negative ERT, which also means start-up. |
| `duration="1000"` | The event is active during the first second: a viewer who starts at 0 gets the break; one who resumes from a bookmark later in the film does not. |
| `executeOnce="true"` | A seek back to the start does not replay the break once it has played. |
| `skipAfter="PT30S"` | The slot cannot be skipped within its 30-second cap. Omitting it would give the base value `PT0S`, skippable everywhere (§5.2.4). |

### A.3 The List MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list" minBufferTime="PT1S"
     publishTime="2026-09-25T20:00:00Z">
  <BaseURL>https://ads.example.com/creatives/</BaseURL>
  <Period id="ad-7731" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="0">c-7731/creative.mpd</ImportedMPD>
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=7731</Event>
      <Event id="2" presentationTime="0">https://tracker.example.com/start?ad=7731</Event>
      <Event id="3" presentationTime="3750">https://tracker.example.com/q1?ad=7731</Event>
      <Event id="4" presentationTime="7500">https://tracker.example.com/mid?ad=7731</Event>
      <Event id="5" presentationTime="11250">https://tracker.example.com/q3?ad=7731</Event>
      <Event id="6" presentationTime="15000">https://tracker.example.com/complete?ad=7731</Event>
    </EventStream>
    <svta:RenderableAsset form="image" layout="linear"
                          assetUrl="https://ads.example.com/creatives/c-7731/slate.jpg"/>
    <svta:Click clickThroughUrl="https://brand-a.example.com/autumn">
      <svta:ClickTracking>https://tracker.example.com/click?ad=7731</svta:ClickTracking>
    </svta:Click>
    <svta:AdSystem>ExampleADS</svta:AdSystem>
    <svta:AdTitle>Autumn Range 15s</svta:AdTitle>
    <svta:Advertiser>Brand A</svta:Advertiser>
    <svta:UniversalAdId>ad-id.org:BRDA0001000H</svta:UniversalAdId>
  </Period>
  <Period id="ad-7732" duration="PT10S">
    <ImportedMPD earliestResolutionTimeOffset="5">c-7732/creative.mpd</ImportedMPD>
    <ServiceDescription id="1">
      <PlaybackRestrictions skipAfter="PT5S"/>
    </ServiceDescription>
    <svta:Click clickThroughUrl="https://brand-b.example.com/offer"/>
    <svta:AdSystem>ExampleADS</svta:AdSystem>
    <svta:AdTitle>Offer 10s</svta:AdTitle>
  </Period>
</MPD>
```

Points of authoring:

- **Every `svta:` child follows every DASH child** of its Period (§5.2.1).
- **`ad-7731` offers an image slate as a second option.** The
  `<ImportedMPD>` video is the first option; the `<svta:RenderableAsset>`
  follows it and carries no `@duration`, because the Period's `@duration`
  applies (§5.3.1).
- **`ad-7731` carries its tracking on the List MPD Period, not in its
  sub-MPD.** A Player that selects the slate never fetches the sub-MPD,
  so a schedule placed there would never be read. `ad-7732` has only its
  video, so its schedule lives in its sub-MPD (§5.5.2).
- **`ad-7732` is skippable after 5 s** through the base per-ad
  restriction, which coexists with the slot-level `@skipAfter` of the
  event (§5.2.4). A List MPD carries no `@dismissAfter`.
- **`ad-7732`'s `<svta:Click>` has no click-tracking.** That is complete:
  on activation the Player opens the destination and fires nothing
  (§5.6.1).

### A.4 The sub-MPDs

`c-7731/creative.mpd`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/c-7731/</BaseURL>
  <Period id="c-7731" duration="PT15S">
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" mimeType="video/mp4" codecs="avc1.640028"
                      bandwidth="6000000" width="1920" height="1080" frameRate="25"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="96000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

`c-7732/creative.mpd`, carrying its own tracking inside its Period:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/c-7732/</BaseURL>
  <Period id="c-7732" duration="PT10S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=7732</Event>
      <Event id="2" presentationTime="2500">https://tracker.example.com/q1?ad=7732</Event>
      <Event id="3" presentationTime="5000">https://tracker.example.com/mid?ad=7732</Event>
      <Event id="4" presentationTime="7500">https://tracker.example.com/q3?ad=7732</Event>
      <Event id="5" presentationTime="10000">https://tracker.example.com/complete?ad=7732</Event>
    </EventStream>
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="96000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

Both carry exactly one Period with `@duration` and no
`MPD@mediaPresentationDuration` (§5.4). Their `Period@duration` values are
canonical; the List MPD's `PT15S` and `PT10S` are the APS's copies of them.

### A.5 The Player's walk-through

1. **Parse.** Event `1` is an insertion in a static MPD, with a cap of
   30 000 ms. ERT = 0, so the Player resolves before rendering any frame
   of the film.
2. **Request.** `GET https://aps.example.com/v1/linear/preroll/film-2201`.
   A linear window declares no layouts, so nothing is forwarded (§5.8.3);
   capability parameters are the Player's option.
3. **Validate.** `type="list"` with the List profile answers a linear
   window (§4.5.2); the document passes the four steps of §4.6, including
   the scan of the callback stream on `ad-7731`.
4. **Evaluate the cap before play** (§4.5.4):

   | Period | `@duration` | In cap units (ms) | Cumulative | Within 30 000? |
   |---|---|---|---|---|
   | `ad-7731` | `PT15S` | 15 000 | 15 000 | yes |
   | `ad-7732` | `PT10S` | 10 000 | 25 000 | yes |

   Nothing is dropped. 5 000 ms of the cap stay unused; the Player does
   not stretch the break to fill them.
5. **Select an option for `ad-7731`.** The `<ImportedMPD>` video is first
   and the `linear`/`video` row of §5.3.7 is satisfiable on every class,
   so the Player plays the video and never fetches the slate. It would
   reach the slate only if the device could not render the video
   creative — a codec it lacks, for example.
6. **Play `ad-7731`.** The Player fetches `c-7731/creative.mpd`
   (`earliestResolutionTimeOffset="0"`: at the Period's start) and plays
   it full-viewport. The six beacons of the Period fire at ad-local 0, 0,
   3 750, 7 500, 11 250 and 15 000 ms (§5.5.3). Beacons `1` and `2` share a
   time but not a URL or an `@id`, so both fire (§5.5.4).
7. **Play `ad-7732`.** Its sub-MPD may be fetched from 5 s before its
   Period starts, i.e. from 10 s into the break. The five beacons of the
   sub-MPD fire at ad-local 0, 2 500, 5 000, 7 500 and 10 000 ms. From 5 s
   into this ad the Player may offer to skip the rest of it; it offers no
   skip of the slot, whose `@skipAfter` equals the cap.
8. **Resume.** After 25 s of break the film starts from its first frame:
   an insertion resumes where the primary timeline stopped (§5.1.1).
   The execution counter of event `1` is now 1, and `@executeOnce`
   prevents a second run.
9. **ClickThrough.** If the viewer activates the ClickThrough during
   `ad-7731`, the Player opens `https://brand-a.example.com/autumn` and
   fires its one click-tracking URL once (§4.5.15).

If the APS had answered with the linear empty resolution of §5.2.3, the
attempt would be a failed execution: the film starts at once, and, with
the counter still at 0, event `1` remains executable (§4.5.6).

### A.6 Device classes

The outcome is the same on D1 to D5. A linear video ad and the primary
content are sequential on one decoder — the `linear`/`video` row of
§5.3.7 is satisfiable on D1–D5 — and no surface is composited over
video, so neither the decoder count nor the surface types of §3.6 enter
the decision. D1 and D2 MAY use their second decoder to pre-buffer
`ad-7732` or the film's first segments, which changes nothing the
Publisher declared (§7.2).

The slate of `ad-7731` is the one place the classes would differ, and
only when the video is not renderable for another reason: a `linear`
image is satisfiable on D1, D3 and D4 (§5.3.7). On D2 and D5 that ad
would then have no renderable option and be skipped; `ad-7732` would
still play (§4.5.3).

### A.7 Where this List MPD came from: an illustrative VAST response

This subsection is **illustrative**. It constrains no implementation and
defines no semantics. No actor is required to use VAST or any version of
it, and the conversion from a decision document to a resolution document
is the APS's (§6.6).

Suppose the ADS answered the APS with this VAST 4.x InLine response, an
ad pod of two ads:

```xml
<VAST version="4.2">
  <Ad id="7731" sequence="1">
    <InLine>
      <AdSystem version="3.1">ExampleADS</AdSystem>
      <Error><![CDATA[https://tracker.example.com/err?ad=7731&code=[ERRORCODE]]]></Error>
      <Impression id="imp"><![CDATA[https://tracker.example.com/imp?ad=7731]]></Impression>
      <AdServingId>srv-20260925-7731</AdServingId>
      <AdTitle>Autumn Range 15s</AdTitle>
      <Advertiser>Brand A</Advertiser>
      <Creatives>
        <Creative id="c-7731" sequence="1">
          <UniversalAdId idRegistry="ad-id.org">BRDA0001000H</UniversalAdId>
          <Linear>
            <Duration>00:00:15</Duration>
            <TrackingEvents>
              <Tracking event="start"><![CDATA[https://tracker.example.com/start?ad=7731]]></Tracking>
              <Tracking event="firstQuartile"><![CDATA[https://tracker.example.com/q1?ad=7731]]></Tracking>
              <Tracking event="midpoint"><![CDATA[https://tracker.example.com/mid?ad=7731]]></Tracking>
              <Tracking event="thirdQuartile"><![CDATA[https://tracker.example.com/q3?ad=7731]]></Tracking>
              <Tracking event="complete"><![CDATA[https://tracker.example.com/complete?ad=7731]]></Tracking>
            </TrackingEvents>
            <VideoClicks>
              <ClickThrough><![CDATA[https://brand-a.example.com/autumn]]></ClickThrough>
              <ClickTracking><![CDATA[https://tracker.example.com/click?ad=7731]]></ClickTracking>
            </VideoClicks>
            <MediaFiles>
              <MediaFile delivery="progressive" type="video/mp4" width="1920" height="1080"
                         bitrate="6000" codec="avc1.640028"><![CDATA[https://ads.example.com/mezz/c-7731-1080.mp4]]></MediaFile>
              <MediaFile delivery="progressive" type="video/mp4" width="1280" height="720"
                         bitrate="3000" codec="avc1.4d401f"><![CDATA[https://ads.example.com/mezz/c-7731-720.mp4]]></MediaFile>
            </MediaFiles>
          </Linear>
        </Creative>
      </Creatives>
    </InLine>
  </Ad>
  <Ad id="7732" sequence="2">
    <InLine>
      <AdSystem version="3.1">ExampleADS</AdSystem>
      <Impression><![CDATA[https://tracker.example.com/imp?ad=7732]]></Impression>
      <AdServingId>srv-20260925-7732</AdServingId>
      <AdTitle>Offer 10s</AdTitle>
      <Creatives>
        <Creative id="c-7732" sequence="1">
          <Linear skipoffset="00:00:05">
            <Duration>00:00:10</Duration>
            <TrackingEvents>
              <Tracking event="firstQuartile"><![CDATA[https://tracker.example.com/q1?ad=7732]]></Tracking>
              <Tracking event="midpoint"><![CDATA[https://tracker.example.com/mid?ad=7732]]></Tracking>
              <Tracking event="thirdQuartile"><![CDATA[https://tracker.example.com/q3?ad=7732]]></Tracking>
              <Tracking event="complete"><![CDATA[https://tracker.example.com/complete?ad=7732]]></Tracking>
            </TrackingEvents>
            <VideoClicks>
              <ClickThrough><![CDATA[https://brand-b.example.com/offer]]></ClickThrough>
            </VideoClicks>
            <MediaFiles>
              <MediaFile delivery="progressive" type="video/mp4" width="1280" height="720"
                         bitrate="3000" codec="avc1.4d401f"><![CDATA[https://ads.example.com/mezz/c-7732-720.mp4]]></MediaFile>
            </MediaFiles>
          </Linear>
        </Creative>
      </Creatives>
    </InLine>
  </Ad>
</VAST>
```

One field-by-field mapping onto A.3 and A.4:

| VAST field | Where it lands |
|---|---|
| `<Ad sequence="n">` | One List MPD `<Period>`, in sequence order; `Ad@id` gives `Period@id` (`ad-7731`) |
| `<Linear><Duration>` | `Period@duration` in the List MPD (`00:00:15` → `PT15S`), copied from the sub-MPD's `Period@duration`, which is canonical (§5.4) |
| `<MediaFile>` renditions | Representations of the sub-MPD (`v1080`, `v720`); packaging a rendition as a Single-Period Static sub-MPD is the APS's or its creative pipeline's |
| `<Impression>` | Callback event at `presentationTime="0"` (§5.5) |
| `<Tracking event="start">` | Callback event at `0` |
| `<Tracking event="firstQuartile" / "midpoint" / "thirdQuartile">` | Callback events at 25 %, 50 % and 75 % of `Duration`: 3 750, 7 500, 11 250 ms for the 15-s ad |
| `<Tracking event="complete">` | Callback event at `Duration` (15 000 ms) |
| `<ClickThrough>` | `svta:Click@clickThroughUrl` (§5.6) |
| `<ClickTracking>` | `<svta:ClickTracking>` inside that `<svta:Click>` |
| `Linear@skipoffset` | `PlaybackRestrictions@skipAfter` on the ad's Period (`00:00:05` → `PT5S`) |
| `<AdSystem>`, `<AdTitle>`, `<Advertiser>` | `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>` (§5.7) |
| `<UniversalAdId>` | `<svta:UniversalAdId>`, best effort (§5.7) |
| `<Error>`, `<AdServingId>` | Not carried. The error URL is neither a timeline beacon (§5.5) nor a click (§5.6), and the identifier drives no Player behaviour. |

Three things in A.2 and A.3 do not come from this response. **The
cap** is the Publisher's (`maxDuration="30000"`), and the ADS is not
required to respect it (§4.3). **The slot-level skip rule** is the
Publisher's `@skipAfter`; VAST's `skipoffset` becomes only the per-ad
restriction. **The image slate** of `ad-7731` has no field here; it
reaches the APS through whatever the APS and the ADS agreed between
them (§1.3). A VAST companion is not the source: companion ads are
outside this specification (§3.4.1).

---

## Annex B — Mid-roll

*This annex is informative.*

### B.1 The scenario

A viewer is watching a live channel. At 20:00:00 the programme has a
30-second break, which the Publisher fills with a linear ad on the
client. The live timeline cannot stop, so the Publisher declares a
replacement (§5.1.2): while the ad plays, the channel is not shown but
its media time keeps advancing, and when the break ends the channel
resumes at the position the Publisher scheduled. An insertion is not
available here: it does not appear in a dynamic MPD (§5.1.1).

The annex then follows the same break for two viewers the scheduled case
does not cover: one who tunes in 4 seconds after the break started, and
one watching behind the live edge at 1.5×.

### B.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="dynamic"
     availabilityStartTime="2026-09-25T18:00:00Z"
     publishTime="2026-09-25T19:58:30Z"
     minimumUpdatePeriod="PT10S"
     timeShiftBufferDepth="PT30M"
     maxSegmentDuration="PT2S"
     minBufferTime="PT2S">
  <BaseURL>https://live.example.com/ch7/</BaseURL>
  <Period id="p1" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
                 timescale="90000">
      <Event id="7001" presentationTime="648000000" duration="2700000">
        <ReplacePresentation uri="https://aps.example.com/v1/linear/ch7/break-7001"
                             maxDuration="2700000"
                             returnOffset="2700000"
                             clip="true"
                             skipAfter="PT30S"/>
      </Event>
      <RequestParam includeInRequests="altmpd"
                    queryTemplate="sid=$urn:mpeg:dash:state:cmcd#sid$"/>
    </EventStream>
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="0"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" mimeType="video/mp4" codecs="avc1.640028"
                      bandwidth="6000000" width="1920" height="1080" frameRate="50"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="50"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="96000" startNumber="0"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
  <EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025"/>
  <UTCTiming schemeIdUri="urn:mpeg:dash:utc:http-iso:2014"
             value="https://time.example.com/iso"/>
</MPD>
```

The event in its own units (`timescale="90000"`):

| Declaration | Ticks | Seconds | Meaning |
|---|---|---|---|
| `presentationTime` (PRT) | 648 000 000 | 7 200 | 20:00:00, two hours after `availabilityStartTime` |
| `Event@duration` | 2 700 000 | 30 | The event is active from PRT to PRT + 30 s; a switch can happen only inside it |
| `maxDuration` (APDmax) | 2 700 000 | 30 | The cap. On a replacement it bounds *until when* (§4.5.4) |
| `returnOffset` | 2 700 000 | 30 | The channel resumes at PRT + 30 s, however late the ad started |
| `earliestResolutionTimeOffset` | default: 5 400 000 | 60 | ERT = PRT − 60 s = 7 140 s, i.e. 19:59:00 |

`@skipAfter="PT30S"` keeps the slot unskippable within its cap; without
it the base value `PT0S` applies and the slot is skippable everywhere
(§5.2.4). The `<RequestParam>` scoped to `altmpd` adds the session
identifier to this event's resolution request, and the MPD-level
`EssentialProperty` of scheme `urn:mpeg:dash:urlparam:2025`, with no
content, announces the mechanism (§5.8.1).

### B.3 The List MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list" minBufferTime="PT1S"
     publishTime="2026-09-25T19:59:12Z">
  <BaseURL>https://ads.example.com/creatives/</BaseURL>
  <Period id="ad-9001" duration="PT30S">
    <ImportedMPD earliestResolutionTimeOffset="0">c-9001/creative.mpd</ImportedMPD>
    <svta:Click clickThroughUrl="https://brand-c.example.com/season">
      <svta:ClickTracking>https://tracker.example.com/click?ad=9001</svta:ClickTracking>
    </svta:Click>
    <svta:AdSystem>ExampleADS</svta:AdSystem>
    <svta:AdTitle>Season Pass 30s</svta:AdTitle>
  </Period>
</MPD>
```

### B.4 The sub-MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/c-9001/</BaseURL>
  <Period id="c-9001" duration="PT30S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=9001</Event>
      <Event id="2" presentationTime="0">https://tracker.example.com/start?ad=9001</Event>
      <Event id="3" presentationTime="7500">https://tracker.example.com/q1?ad=9001</Event>
      <Event id="4" presentationTime="15000">https://tracker.example.com/mid?ad=9001</Event>
      <Event id="5" presentationTime="22500">https://tracker.example.com/q3?ad=9001</Event>
      <Event id="6" presentationTime="30000">https://tracker.example.com/complete?ad=9001</Event>
    </EventStream>
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" mimeType="video/mp4" codecs="avc1.640028"
                      bandwidth="6000000" width="1920" height="1080" frameRate="25"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="96000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### B.5 The Player's walk-through: the break on schedule

1. **Resolve.** Between ERT (7 140 s) and PRT (7 200 s) the Player issues
   `GET https://aps.example.com/v1/linear/ch7/break-7001?sid=<session id>`.
   The `sid` parameter is the Publisher's template; any reserved
   capability parameter the Player appends comes after it (§5.8.5).
2. **Validate** the List MPD against the linear window (§4.5.2, §4.6).
3. **Compare the ad with the cap.** `PT30S` × 90 000 = 2 700 000 ticks,
   equal to the cap, and a converted duration equal to the cap is
   admitted (§4.5.4).
4. **Switch at PRT.** The channel stops being output while its media time
   keeps advancing (§5.1.2). The Player plays `c-9001` full-viewport and
   fires its six beacons at ad-local 0, 0, 7 500, 15 000, 22 500 and
   30 000 ms.
5. **Return.** The ad ends at PRT + 30 s; the channel resumes at
   RT = PRT + `@returnOffset` = 650 700 000 ticks (7 230 s), where its
   media time now stands.

### B.6 A late start: `@clip` at work

A viewer tunes in at 7 204 s, 4 seconds into the break. The event is
still active (PRT + 30 s has not passed), so the Player executes it at
once: the execution time is PRTA = PRT + 4 s = 648 360 000 ticks. The
quantities are those of DASH §5.16.2.1:

| Quantity | Value | How |
|---|---|---|
| APDmax | 30 s | `maxDuration` 2 700 000 / 90 000 |
| APD | 30 s | the List MPD's one Period |
| ASO | 0 | `@startWithOffset` is absent (default `false`): the ad starts from its first frame |
| APDadj | 26 s | `@clip="true"`: max(APDmax − PRTA + PRT, 0) = max(30 − 4, 0) |
| APDA | 26 s | min(APD − ASO, APDadj) = min(30, 26) |
| End of the ad | PRT + 30 s | PRTA + APDA — the scheduled end, as `@clip="true"` requires (§5.1.2) |
| RT | PRT + 30 s | PRT + `@returnOffset` |

The ad is cut 26 s into its own timeline. Its beacons at 0, 0, 7 500,
15 000 and 22 500 ms fire; `complete` at 30 000 ms falls after the trim
and does not (§4.5.13). The channel resumes at 7 230 s, exactly as for
the on-time viewer, so the late viewer loses 4 seconds of ad, not 4
seconds of programme.

Two neighbouring cases:

- **`@clip="false"`** would end the ad at PRTA + APDmax = PRT + 34 s: the
  base specification moves the bound, and the Player plays the full
  30 s (§5.1.2). The Publisher here chose the scheduled end.
- **A viewer who tunes in at 7 231 s**, after the event stopped being
  active, never switches: the channel plays, and no request is issued
  for this event.

### B.7 The trick-play variant

A viewer is 10 minutes behind the live edge, inside the 30-minute
time-shift buffer, catching up at 1.5×. The Player reaches PRT on
schedule and executes the break at the viewer's speed (§4.5.12):

| | Presentation timeline | Wall clock at 1.5× | Wall clock at 2× |
|---|---|---|---|
| Ad length | 30 s | 20 s | 15 s |
| `q1` beacon (7 500 ms) | 7.5 s | 5 s | 3.75 s |
| `mid` beacon (15 000 ms) | 15 s | 10 s | 7.5 s |
| `q3` beacon (22 500 ms) | 22.5 s | 15 s | 11.25 s |
| `complete` beacon (30 000 ms) | 30 s | 20 s | 15 s |
| Cap | 2 700 000 ticks | unchanged | unchanged |

The wall-clock column is `duration / playback_speed`. Nothing the
Publisher or the APS declared changes: the cap and the beacon schedule
stay on the presentation timeline, and the Player does not force the ad
to 1×. The channel's media time advances at the speed of the ad while it
plays (§5.1.2), so the resumption point is still PRT + 30 s, reached 20
wall-clock seconds after the switch at 1.5×.

### B.8 Device classes

The outcome is the same on D1 to D5, for all three viewers. A linear
video ad and the primary content are sequential on one decoder — the
`linear`/`video` row of §5.3.7 is satisfiable on D1–D5 — and nothing is
composited over video. D1 and D2 MAY use their second decoder to
pre-buffer the ad before PRT and the channel before RT; D3, D4 and D5
switch their one decoder at each boundary. Neither choice changes what
the viewer sees, the cap, or the beacons (§7.2).

---

## Annex C — Coexisting overlay (multi-form, multi-layout)

*This annex is informative.*

### C.1 Scenario

An on-demand title carries one overlay window ten minutes in. While the
primary content keeps playing, a non-linear ad is composited over it or
shares the frame with it for a bounded time, then disappears. The
Publisher admits four layouts in this window and caps the slot at 30
seconds.

The ADS knows nothing about the device. The APS returns the same
document to every Player: two candidates, the first carrying four
presentation options in preference order, the second two. Each Player
walks the options in document order against the budget of §5.3.7 and the
window's allowed layouts (§4.5.3), so one document lands on a different
option on each device class. The two candidates are presented in
sequence, one on screen at a time (§4.5.8).

### C.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static"
     mediaPresentationDuration="PT1H"
     minBufferTime="PT2S">
  <BaseURL>https://cdn.publisher.example.com/vod/title-1234/</BaseURL>
  <Period id="main" duration="PT1H">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
                 timescale="1000">
      <Event id="301" presentationTime="600000" duration="40000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/overlay"
            maxDuration="30000"
            allowedLayouts="squeezeback-double-box-background overlay-corner overlay-lower-third squeezeback-l-shape-upper-left"
            earliestResolutionTimeOffset="20000"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" codecs="avc1.640028"
                      width="1920" height="1080" frameRate="25"/>
      <Representation id="v720" bandwidth="3000000" codecs="avc1.64001f"
                      width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" codecs="mp4a.40.2"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The token order inside `@allowedLayouts` carries no preference: it is a
set. Preference lives only in the order of the options the APS returns
(§5.3.4).

### C.3 The resolution request

The window declares `@allowedLayouts`, so the Player forwards it
unchanged (§5.8.3). This Player sends no capability parameter, so the
APS answers with the options unnarrowed (§5.8.4):

```
GET /decision/overlay?sgaiAllowedLayouts=squeezeback-double-box-background%20overlay-corner%20overlay-lower-third%20squeezeback-l-shape-upper-left
Host: aps.example.com
```

A Player that declares its class (§5.8.2) MAY receive a narrower
document. The Player checks whatever arrives in the same way (§4.5.3).

### C.4 The resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T20:09:40Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay" dismissAfter="PT5S" usableFor="PT5M">
      <svta:Candidate id="a-8841">
        <svta:RenderableAsset form="video"
            layout="squeezeback-double-box-background" duration="PT15S"
            assetUrl="https://ads.example.com/creatives/a-8841/video.mpd"
            backgroundUrl="https://ads.example.com/creatives/a-8841/background.jpg"/>
        <svta:RenderableAsset form="video" layout="overlay-corner"
            duration="PT15S"
            assetUrl="https://ads.example.com/creatives/a-8841/video.mpd"/>
        <svta:RenderableAsset form="html" layout="overlay-lower-third"
            duration="PT15S"
            assetUrl="https://ads.example.com/creatives/a-8841/lower-third.html"/>
        <svta:RenderableAsset form="image"
            layout="squeezeback-l-shape-upper-left" duration="PT15S"
            assetUrl="https://ads.example.com/creatives/a-8841/l-shape.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0">https://tracker.example.com/imp?ad=a-8841</Event>
          <Event presentationTime="3750">https://tracker.example.com/q1?ad=a-8841</Event>
          <Event presentationTime="7500">https://tracker.example.com/mid?ad=a-8841</Event>
          <Event presentationTime="11250">https://tracker.example.com/q3?ad=a-8841</Event>
          <Event presentationTime="15000">https://tracker.example.com/done?ad=a-8841</Event>
        </EventStream>
        <svta:Click clickThroughUrl="https://retail.example.com/spring">
          <svta:ClickTracking>https://tracker.example.com/click?ad=a-8841</svta:ClickTracking>
        </svta:Click>
        <svta:AdSystem>ExampleAdServer</svta:AdSystem>
        <svta:AdTitle>Spring Sale</svta:AdTitle>
        <svta:Advertiser>Example Retail</svta:Advertiser>
        <svta:UniversalAdId>ad-id.org:EXRT0001000H</svta:UniversalAdId>
      </svta:Candidate>
      <svta:Candidate id="a-9120">
        <svta:RenderableAsset form="video" layout="overlay-lower-third"
            duration="PT15S"
            assetUrl="https://ads.example.com/creatives/a-9120/video.mpd"/>
        <svta:RenderableAsset form="image" layout="overlay-lower-third"
            duration="PT15S"
            assetUrl="https://ads.example.com/creatives/a-9120/banner.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0">https://tracker.example.com/imp?ad=a-9120</Event>
          <Event presentationTime="15000">https://tracker.example.com/done?ad=a-9120</Event>
        </EventStream>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

Points worth noting:

- **One video creative serves two options.** Options 1 and 2 of `a-8841`
  point at the same sub-MPD. They differ in layout: a double box with
  the advertiser's background image, or a corner overlay.
- **`@backgroundUrl` appears on option 1 only**, the one
  `squeezeback-double-box-background` option (§5.3.1). The background is
  a composition attribute of that layout, not an option of its own
  (§5.3.6).
- **The tracking schedule sits in the candidate, not in the options.**
  It fires relative to whichever option the Player selected, and offset
  `0` is that option's first visible frame (§5.5.3). The same schedule
  therefore serves the video, HTML and image renderings alike.
- **The candidates follow the ADS's order**, and the options inside
  each candidate follow the order the decision gave them (§4.4 item 5).

### C.5 The sub-MPDs

`a-8841`, shared by options 1 and 2:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/a-8841/</BaseURL>
  <Period id="a-8841" duration="PT15S">
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2500" startNumber="1"
                       initialization="v/$RepresentationID$/init.mp4"
                       media="v/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v540" bandwidth="1500000" codecs="avc1.64001f"
                      width="960" height="540" frameRate="25"/>
    </AdaptationSet>
  </Period>
</MPD>
```

`a-9120`, option 1:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/a-9120/</BaseURL>
  <Period id="a-9120" duration="PT15S">
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2500" startNumber="1"
                       initialization="v/$RepresentationID$/init.mp4"
                       media="v/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080x324" bandwidth="1200000" codecs="avc1.640028"
                      width="1920" height="324" frameRate="25"/>
    </AdaptationSet>
  </Period>
</MPD>
```

Each option's `PT15S` is derived from its sub-MPD's `Period@duration`,
which is the canonical value (§5.4). The overlay creatives carry no
audio, so the primary content's audio is undisturbed.

### C.6 The walk per device class

Every option's `@layout` is in the window's allowed layouts, so the
window check (b) of §4.5.3 passes for all six options. What separates
the classes is the device check (a), read off §5.3.7.

**Candidate `a-8841`:**

| # | Form, layout | What it costs (§5.3.7) | Satisfiable on |
|---|---|---|---|
| 1 | `video`, `squeezeback-double-box-background` | 2 decoders + image surface for the background | D1 |
| 2 | `video`, `overlay-corner` | 2 decoders | D1, D2 |
| 3 | `html`, `overlay-lower-third` | 1 decoder + HTML surface | D1, D3 |
| 4 | `image`, `squeezeback-l-shape-upper-left` | 1 decoder + image surface for the full-frame creative | D1, D3, D4 |

- **D1** accepts option 1. It shrinks the primary content into the
  centre-left box, plays the ad video in the centre-right box on its
  second decoder, and fills the bands with `background.jpg`. Options 2
  to 4 are not considered.
- **D2** declines option 1. It has the two decoders, but the background
  is a still image and D2 composites no image over video. It accepts
  option 2: the ad video in a corner over the untransformed primary
  content, on its second decoder.
- **D3** declines options 1 and 2, because each needs a second video
  decoder. It accepts option 3: the HTML lower-third over the playing
  primary content.
- **D4** declines options 1 and 2 for the decoder and option 3 because
  it renders no HTML over video. It accepts option 4: the full-frame
  image in the background and the primary content, shrunk into the upper
  left 60 % of the frame, on top of it. The image shows across the
  bottom and up the right edge.
- **D5** declines all four options. It has one decoder and no image or
  HTML surface. The candidate is skipped (§4.5.3 item 3).

**Candidate `a-9120`:**

| # | Form, layout | Satisfiable on |
|---|---|---|
| 1 | `video`, `overlay-lower-third` | D1, D2 |
| 2 | `image`, `overlay-lower-third` | D1, D3, D4 |

D1 and D2 accept option 1. D3 and D4 decline it for the decoder and
accept option 2. D5 declines both options and skips this candidate too.

**D5 overall.** Every candidate is skipped, and the primary content
continues uninterrupted. This is not a failed execution of the window:
the document was of the right family and carried candidates (§4.5.6
item 4). No beacon fires. The window does not admit `linear`, so no
full-screen takeover was available to D5. A Publisher wanting to
monetise D5 here would have to list `linear` in `@allowedLayouts`, and a
candidate would have to offer the takeover as its last option (§8.7).

**Walk at a glance:**

| Class | `a-8841` renders | `a-9120` renders | On screen, 600 s to 630 s |
|---|---|---|---|
| D1 | option 1: video double box, image background | option 1: video lower third | double box, then video lower third |
| D2 | option 2: video corner | option 1: video lower third | video corner, then video lower third |
| D3 | option 3: HTML lower third | option 2: image lower third | HTML lower third, then image lower third |
| D4 | option 4: image L-shape, upper left | option 2: image lower third | L-shape, then image lower third |
| D5 | skipped | skipped | primary content only |

### C.7 Timing and cap arithmetic

All window values are in the stream's `timescale="1000"`.

| Quantity | Computation | Value |
|---|---|---|
| Window | `600000` + `40000` | 600.000 s to 640.000 s |
| Earliest resolution time | `600000 − 20000` | 580.000 s |
| Usable until | received at 580.000 s on the primary timeline, `@usableFor` `PT5M` on the wall clock | usable when the window fires 20 s later at 1× |
| `a-8841` | `PT15S` → `15000` | 600.000 s to 615.000 s |
| `a-9120` | `PT15S` → `15000` | 615.000 s to 630.000 s |
| Cumulative against the cap | `15000 + 15000 = 30000` against `maxDuration="30000"` | equal, so admitted (§4.5.4 item 4) |
| Window end | 640.000 s | not reached; the cap ends the slot first |

**The cap binds on actual length, not on the declared one.** Suppose that
on D1 the `a-8841` video actually renders for 15.2 s. Then `a-9120` has
`30000 − 15200 = 14800` left. It is trimmed at 14.8 s, and its `done`
beacon at `15000` does not fire (§4.5.4 item 2; §4.5.13 item 2). On D3
and D4 the first candidate is HTML or an image. These have no intrinsic
media, and their declared `PT15S` is their length.

**If the resolution goes stale.** Suppose the viewer resolves at 580 s,
pauses outside any pause window, and comes back six minutes later. The
five minutes of `@usableFor` have then run out on the wall clock. When the
window fires, the Player requests a new document and never presents the
expired one (§4.5.1 item 5).

**Dismissal.** `dismissAfter="PT5S"` makes the slot dismissible from
605.000 s on the presentation timeline. A dismissal at 612 s ends the
whole slot, and `a-9120` never starts. The `q3` beacon of `a-8841` (at
`11250`, that is 611.250 s) has fired. Its `done` beacon has not, and it
does not fire (§4.5.14). The primary content continues from 612 s.

**Playback speed.** At 2× each 15-second candidate is on screen for 7.5
wall-clock seconds. The cap and the beacon offsets do not change, because
they are on the presentation timeline (§4.5.12).

### C.8 Where this document came from: an illustrative VAST response

**This subsection is illustrative. It constrains no implementation and
defines no semantics. No actor is required to use VAST or any particular
version of it** (chapter 2). The conversion from a decision to a
resolution document is the APS's, and it is not defined by this
specification (§6.6). The response below is abridged. It has not been
validated against the VAST schema, and it covers `a-8841` only.

```xml
<VAST version="4.2">
  <Ad id="a-8841" sequence="1">
    <InLine>
      <AdSystem version="7.1">ExampleAdServer</AdSystem>
      <Impression id="imp"><![CDATA[https://tracker.example.com/imp?ad=a-8841]]></Impression>
      <AdServingId>7f3c-a-8841</AdServingId>
      <AdTitle>Spring Sale</AdTitle>
      <Advertiser>Example Retail</Advertiser>
      <Creatives>
        <Creative id="cr-video" sequence="1">
          <UniversalAdId idRegistry="ad-id.org">EXRT0001000H</UniversalAdId>
          <Linear>
            <Duration>00:00:15</Duration>
            <TrackingEvents>
              <Tracking event="firstQuartile"><![CDATA[https://tracker.example.com/q1?ad=a-8841]]></Tracking>
              <Tracking event="midpoint"><![CDATA[https://tracker.example.com/mid?ad=a-8841]]></Tracking>
              <Tracking event="thirdQuartile"><![CDATA[https://tracker.example.com/q3?ad=a-8841]]></Tracking>
              <Tracking event="complete"><![CDATA[https://tracker.example.com/done?ad=a-8841]]></Tracking>
            </TrackingEvents>
            <VideoClicks>
              <ClickThrough><![CDATA[https://retail.example.com/spring]]></ClickThrough>
              <ClickTracking><![CDATA[https://tracker.example.com/click?ad=a-8841]]></ClickTracking>
            </VideoClicks>
            <MediaFiles>
              <MediaFile delivery="streaming" type="application/dash+xml"
                         width="960" height="540"><![CDATA[https://ads.example.com/creatives/a-8841/video.mpd]]></MediaFile>
            </MediaFiles>
          </Linear>
        </Creative>
        <Creative id="cr-nonlinear" sequence="2">
          <UniversalAdId idRegistry="ad-id.org">EXRT0001000H</UniversalAdId>
          <NonLinearAds>
            <NonLinear id="nl-html" width="1920" height="324"
                       minSuggestedDuration="00:00:15">
              <IFrameResource><![CDATA[https://ads.example.com/creatives/a-8841/lower-third.html]]></IFrameResource>
              <NonLinearClickThrough><![CDATA[https://retail.example.com/spring]]></NonLinearClickThrough>
            </NonLinear>
            <NonLinear id="nl-image" width="1920" height="1080"
                       minSuggestedDuration="00:00:15">
              <StaticResource creativeType="image/png"><![CDATA[https://ads.example.com/creatives/a-8841/l-shape.png]]></StaticResource>
              <NonLinearClickThrough><![CDATA[https://retail.example.com/spring]]></NonLinearClickThrough>
            </NonLinear>
          </NonLinearAds>
        </Creative>
      </Creatives>
      <Extensions>
        <Extension type="example-placement">
          <Placement ref="cr-video"
                     layouts="squeezeback-double-box-background overlay-corner"
                     background="https://ads.example.com/creatives/a-8841/background.jpg"/>
          <Placement ref="nl-html" layouts="overlay-lower-third"/>
          <Placement ref="nl-image" layouts="squeezeback-l-shape-upper-left"/>
        </Extension>
      </Extensions>
    </InLine>
  </Ad>
</VAST>
```

The `example-placement` extension is invented for this illustration. The
VAST core carries no field that names one of the layout tokens of §3.4.2
or a double-box background. How an ADS conveys a placement to the APS
belongs to the contract those two parties agree bilaterally (§1.3).

| In the decision (illustrative) | In the resolution document |
|---|---|
| `Ad@id` | `svta:Candidate@id` |
| `Ad@sequence` and the order of the `Ad` elements | the order of the `svta:Candidate` elements |
| `AdSystem`, `AdTitle`, `Advertiser` | `svta:AdSystem`, `svta:AdTitle`, `svta:Advertiser` |
| `UniversalAdId` with its `@idRegistry` | `svta:UniversalAdId`, carried on a best-effort basis (§5.7) |
| `MediaFile` of type `application/dash+xml` | `@assetUrl` of options 1 and 2, addressing the sub-MPD (§5.4) |
| `Linear/Duration` `00:00:15` | `@duration="PT15S"` on the video options, and the sub-MPD's `Period@duration` |
| `NonLinear/IFrameResource` | option 3, `form="html"`, `@assetUrl` |
| `NonLinear/StaticResource` of `image/png` | option 4, `form="image"`, `@assetUrl` |
| `NonLinear@minSuggestedDuration` | `@duration` of options 3 and 4 |
| the placement extension, `layouts` | one `svta:RenderableAsset` per creative and layout, with `@layout`; the order of creatives, then of listed layouts, gives the option order |
| the placement extension, `background` | `@backgroundUrl` on option 1 |
| `Impression` | callback `Event` at `presentationTime="0"` |
| `Tracking` `firstQuartile`, `midpoint`, `thirdQuartile`, `complete` | callback `Event`s at 25 %, 50 %, 75 % and 100 % of `15000`: `3750`, `7500`, `11250`, `15000` |
| `ClickThrough`, `NonLinearClickThrough` (identical here) | `svta:Click@clickThroughUrl` |
| `ClickTracking` | `svta:ClickTracking` |
| `AdServingId` | not carried; nothing in the Player-visible interface uses it |

Two conversion choices shown here are the APS's own, and a different APS
could make them differently. The first is that the Linear creative's
quartile schedule is applied to the whole candidate. The HTML and image
options therefore fire the same beacons at the same offsets. The second
is that the two click-through destinations collapse into one
`svta:Click`, because the decision gives the same URL for both. Had the
decision given different destinations per creative, one candidate could
not carry them, since a candidate has at most one `svta:Click` (§5.2.2),
and the APS would have to choose one of the destinations.

---

## Annex D — Hybrid: a linear ad with a concurrent overlay

*This annex is informative.*

### D.1 Scenario

A live channel runs a 30-second mid-roll at 30 minutes into its Period.
A linear ad takes over the screen for the break. During the same break,
a non-linear ad is composited on top of the linear ad for up to 15
seconds. The Publisher admits only `overlay-lower-third` for that
overlay, and so admits no squeezeback over a takeover.

The break introduces no construct of its own (§5.1.6). It is authored as
**two windows of two families** over the same region: a linear
replacement event, and an overlay window, each in the stream of its own
family. The main MPD is `dynamic`, so the linear portion uses
`<ReplacePresentation>` (§5.1.1). The Player resolves the two `@uri`
values independently, validates each document against its own window,
and composes the results. The two portions are not linked. A constraint
such as "no overlay from a competitor of the linear advertiser" is not
expressible. Exclusivity between the portions is obtained from the ADS
(§5.1.6).

### D.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="dynamic"
     availabilityStartTime="2026-09-25T18:00:00Z"
     publishTime="2026-09-25T18:29:00Z"
     minimumUpdatePeriod="PT10S"
     timeShiftBufferDepth="PT5M"
     maxSegmentDuration="PT2S"
     minBufferTime="PT2S">
  <BaseURL>https://live.publisher.example.com/channel-7/</BaseURL>
  <Period id="p0" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
                 timescale="1000">
      <Event id="40" presentationTime="1800000" duration="30000">
        <ReplacePresentation uri="https://aps.example.com/decision/linear?break=40"
                             maxDuration="30000"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
                 timescale="1000">
      <Event id="240" presentationTime="1800000" duration="30000">
        <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay?break=40"
                                  maxDuration="15000"
                                  allowedLayouts="overlay-lower-third"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="0"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" codecs="avc1.640028"
                      width="1920" height="1080" frameRate="50"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="0"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" codecs="mp4a.40.2"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

Each window carries its own cap. The linear cap of `30000` bounds *until
when* the replacement may run. The overlay cap of `15000` bounds the
cumulative duration of what the overlay slot presents (§4.5.4). On the
linear event, `Event@duration` keeps its base meaning, the interval in
which the switch may occur (DASH §5.16.4). On the overlay window it is
the region the window covers (§5.1.3).

### D.3 The two resolution requests

```
GET /decision/linear?break=40
Host: aps.example.com

GET /decision/overlay?break=40&sgaiAllowedLayouts=overlay-lower-third
Host: aps.example.com
```

The query already present in each `@uri` is kept (§5.8.5). Only the
overlay request carries `sgaiAllowedLayouts`, because linear windows
carry no layout declaration (§5.8.3). Neither request here carries
capability parameters, so the overlay document arrives unnarrowed. An
APS that received `sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=false`
(D4) MAY emit only the image option (§4.4 item 14).

### D.4 The linear resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list" minBufferTime="PT1S"
     publishTime="2026-09-25T18:29:05Z">
  <Period id="l-5501" duration="PT30S">
    <ImportedMPD>https://ads.example.com/creatives/l-5501/creative.mpd</ImportedMPD>
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0">https://tracker.example.com/imp?ad=l-5501</Event>
      <Event presentationTime="7500">https://tracker.example.com/q1?ad=l-5501</Event>
      <Event presentationTime="15000">https://tracker.example.com/mid?ad=l-5501</Event>
      <Event presentationTime="22500">https://tracker.example.com/q3?ad=l-5501</Event>
      <Event presentationTime="30000">https://tracker.example.com/done?ad=l-5501</Event>
    </EventStream>
  </Period>
</MPD>
```

### D.5 The overlay resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T18:29:05Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay">
      <svta:Candidate id="o-7730">
        <svta:RenderableAsset form="video" layout="overlay-lower-third"
            duration="PT10S"
            assetUrl="https://ads.example.com/creatives/o-7730/video.mpd"/>
        <svta:RenderableAsset form="html" layout="overlay-lower-third"
            duration="PT10S"
            assetUrl="https://ads.example.com/creatives/o-7730/lower-third.html"/>
        <svta:RenderableAsset form="image" layout="overlay-lower-third"
            duration="PT10S"
            assetUrl="https://ads.example.com/creatives/o-7730/lower-third.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0">https://tracker.example.com/imp?ad=o-7730</Event>
          <Event presentationTime="10000">https://tracker.example.com/done?ad=o-7730</Event>
        </EventStream>
        <svta:Click clickThroughUrl="https://brand.example.com/offer">
          <svta:ClickTracking>https://tracker.example.com/click?ad=o-7730</svta:ClickTracking>
        </svta:Click>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

The document carries no `@dismissAfter`, so the overlay slot is not
dismissible (§5.2.4). The linear event declares no `@skipAfter`, so the
base value `PT0S` governs skipping of the linear slot (§5.2.4). The two
defaults are opposite, and each belongs to its own family.

### D.6 The sub-MPDs

The linear ad, `l-5501`, with its own audio:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/l-5501/</BaseURL>
  <Period id="l-5501" duration="PT30S">
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="v/$RepresentationID$/init.mp4"
                       media="v/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" codecs="avc1.640028"
                      width="1920" height="1080" frameRate="50"/>
      <Representation id="v720" bandwidth="2500000" codecs="avc1.64001f"
                      width="1280" height="720" frameRate="50"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="a/$RepresentationID$/init.mp4"
                       media="a/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" codecs="mp4a.40.2"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The overlay's video option, `o-7730`, which is video only:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/o-7730/</BaseURL>
  <Period id="o-7730" duration="PT10S">
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="v/$RepresentationID$/init.mp4"
                       media="v/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080x324" bandwidth="1000000" codecs="avc1.640028"
                      width="1920" height="324" frameRate="50"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### D.7 The budget, and the walk per device class

**The linear ad does not take a second decoder.** During an alternative
presentation, *"the alternative access engine outputs media to the media
engine, while the main client will be paused or be in a listen mode"*,
and an access engine in listen mode *"does not output media to the media
engine"* (DASH §4.2). The linear ad therefore occupies the decoder the
primary content released. The overlay then costs what an overlay over
the primary content would cost. An image or HTML overlay needs the one
decoder plus one surface. A video overlay needs a second decoder
(§5.3.7).

Every class presents the linear ad, because `linear` with `video` is
satisfiable on D1 to D5 (§5.3.7). The overlay walk is as follows. Every
option's layout is `overlay-lower-third`, which the window admits, so
only the device check decides.

| # | Form | Cost on top of the linear ad | Satisfiable on |
|---|---|---|---|
| 1 | `video` | a second decoder | D1, D2 |
| 2 | `html` | an HTML surface | D1, D3 |
| 3 | `image` | an image surface | D1, D3, D4 |

- **D1** accepts option 1. The linear ad is on the first decoder and the
  lower-third video on the second.
- **D2** accepts option 1 on its second decoder. Had the candidate
  offered only options 2 and 3, D2 would decline the overlay, because it
  composites no image or HTML over video. The linear ad would play
  alone.
- **D3** declines option 1 and accepts option 2. It composites the HTML
  lower-third over the linear ad: one decoder plus one HTML surface.
- **D4** declines option 1 for the decoder and option 2 because it
  renders no HTML over video. It accepts option 3, compositing the image
  lower-third over the linear ad: one decoder plus one image surface.
- **D5** declines all three options. The candidate is skipped, and the
  linear ad plays alone. This is not a failed execution of the overlay
  window (§4.5.6 item 4).

**Walk at a glance:**

| Class | Decoders in use | Surfaces in use | Linear portion | Overlay portion |
|---|---|---|---|---|
| D1 | 2 | none | `l-5501` | option 1, video lower third |
| D2 | 2 | none | `l-5501` | option 1, video lower third |
| D3 | 1 | HTML | `l-5501` | option 2, HTML lower third |
| D4 | 1 | image | `l-5501` | option 3, image lower third |
| D5 | 1 | none | `l-5501` | none |

This matches the hybrid row of §3.6. One non-linear form is on screen at
a time, and the linear ad beneath it does not count against that bound
(§4.5.8 item 3).

### D.8 Timing and cap arithmetic

All values are in `timescale="1000"`, relative to the Period start.

| Quantity | Computation | Value |
|---|---|---|
| Linear switch time (PRT) | `presentationTime` | 1800.000 s |
| Linear end, `@clip="true"` (default) | at the latest PRT + `maxDuration` = `1800000 + 30000` | 1830.000 s |
| `l-5501` | `PT30S` → `30000` against the cap of `30000` | fits exactly |
| Overlay window | `1800000` + `30000` | 1800.000 s to 1830.000 s |
| `o-7730` | `PT10S` → `10000` against `maxDuration="15000"` | admitted; on screen 1800.000 s to 1810.000 s |
| Overlay beacons | offsets `0` and `10000` from the overlay's first frame | 1800.000 s and 1810.000 s |

**A late switch shortens the linear ad and leaves the overlay alone.**
Suppose the switch happens 2 s late, at 1802.000 s. With the default
`@clip="true"` the linear ad still ends by 1830.000 s, so it is trimmed to
28 s. Its `done` beacon at `30000` is past the trim and does not fire
(§4.5.4; §4.5.13 item 2). The overlay is anchored to its own window on
the primary timeline, which keeps advancing during a replacement:
*"the main Media Presentation is not being output, but its media time
progresses at the same speed as the currently playing alternative Media
Presentation"* (DASH §5.16.1). The overlay therefore starts at 1800.000 s
as scheduled, and for those 2 s it is composited over the primary
content rather than over the ad. A Publisher that wants the overlay only
over the ad starts the overlay window a few seconds after the linear
event's `@presentationTime`.

**What independence means at runtime.** Each portion's failure is its
own. Suppose the linear resolution is an empty resolution. That is a
failed execution of the linear event, and the primary content plays on
(§4.5.6). The overlay window still resolves and composites over the
primary content, and its budget is then that of an ordinary overlay (the
overlay row of §3.6). Suppose instead the overlay resolution fails. The
linear ad plays alone. Neither document is validated against the other
window's declarations (§4.5.7).

---

## Annex E — Pause-triggered ad

*This annex is informative.*

### E.1 Scenario

An on-demand film of 42 minutes carries one pause window from 600 s to
2400 s of the primary timeline. A viewer pause that begins inside that
region triggers a pause ad; a pause outside it triggers nothing. The
Publisher bounds the window to one pause ad per session
(`@executeOnce="true"`), permits resolution 30 s before the window
opens, and requests the play-list metric so that pause delivery can be
measured (§5.9). The APS answers with two candidates: the first offers
a fullscreen video, then a partial HTML unit, then a partial image; the
second offers a fullscreen image.

The viewer pauses at 1500 s and stays paused for 60 s. The pause ad
exists only while the content is paused (§4.5.10): on resume it is
removed within one rendering frame and the film continues from 1500 s.

### E.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static" minBufferTime="PT2S"
     mediaPresentationDuration="PT42M">
  <BaseURL>https://cdn.publisher.example.com/film-7/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026"
                 timescale="1000">
      <Event id="501" presentationTime="600000" duration="1800000">
        <svta:PauseAdPresentation uri="https://aps.example.com/decision/pause"
                                  maxDuration="60000"
                                  allowedLayouts="pause-fullscreen pause-partial"
                                  earliestResolutionTimeOffset="30000"
                                  executeOnce="true"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" codecs="avc1.640028" bandwidth="6000000"
                      width="1920" height="1080"/>
      <Representation id="v720" codecs="avc1.64001f" bandwidth="3000000"
                      width="1280" height="720"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true">
      <SegmentTemplate timescale="48000" duration="192000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" codecs="mp4a.40.2" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
  <Metrics metrics="PlayList">
    <Range starttime="PT0S"/>
    <Reporting schemeIdUri="urn:example:publisher:reporting:2026"/>
  </Metrics>
</MPD>
```

- The `<Metrics>` element follows the Period, as the MPD schema orders
  them. The base schema requires at least one `<Reporting>` child; its
  scheme is the Publisher's, because the base specification specifies
  no reporting scheme (DASH §5.9.4) and this specification defines no
  reporting transport (§1.3).
- `@maxDuration="60000"` is declared because every slot declares a cap
  (§4.2 item 2). On a pause window it bounds nothing (§4.5.4).
- The stream carries no `@value` (§5.1).

### E.3 Resolution request and timing

The earliest resolution time is computed against the window's start,
never against the pause (§5.1.4):

`ERT = 600000 − 30000 = 570000` ms, that is 570 s of the primary timeline.

Because the window declares `@allowedLayouts`, every resolution request
forwards it (§5.8.3). A D3 Player that discloses its capabilities
sends:

```
GET /decision/pause?sgaiAllowedLayouts=pause-fullscreen%20pause-partial&sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=true
```

A Player that sends no capability parameter receives the options
unnarrowed (§5.8.4). The walk-through below assumes the APS returned
the full list of E.4 to every class.

**Early resolution and `@usableFor`.** The document declares
`usableFor="PT5M"`, measured on the Player's wall clock from receipt
(§5.2.5).

| Player strategy | Viewer pauses at | Age of the held document | Outcome |
|---|---|---|---|
| Resolves at 575 s (received at wall-clock `T0`), plays continuously at 1× | 700 s | `T0 + 125 s` | Usable; presented without a new request. |
| Same | 1500 s | `T0 + 925 s` > 300 s | Expired; not presented. The Player requests a new document at the pause (§4.5.1 item 5). |
| Resolves only at the pause | any time in the window | 0 | Fresh; conformant whatever offset the window carries (§4.5.1 item 4). |

If the fresh request in the second row returns an empty resolution, the
pause carries no ad: the expired document is never used as a fallback,
and the window is not consumed (§4.5.6 item 6).

### E.4 Pause resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T20:25:00Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="pause"
                      dismissAfter="PT5S"
                      usableFor="PT5M"
                      onCandidatesExhausted="request-again">
      <svta:Candidate id="p1">
        <svta:RenderableAsset form="video" layout="pause-fullscreen"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/creatives/p1/p1.mpd"/>
        <svta:RenderableAsset form="html" layout="pause-partial"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/creatives/p1/partial.html"/>
        <svta:RenderableAsset form="image" layout="pause-partial"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/creatives/p1/partial.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=p1</Event>
          <Event id="2" presentationTime="7500">https://tracker.example.com/mid?ad=p1</Event>
          <Event id="3" presentationTime="15000">https://tracker.example.com/complete?ad=p1</Event>
        </EventStream>
        <svta:Click clickThroughUrl="https://advertiser-a.example.com/offer"/>
        <svta:AdSystem>ExampleADS</svta:AdSystem>
        <svta:Advertiser>Advertiser A</svta:Advertiser>
      </svta:Candidate>
      <svta:Candidate id="p2">
        <svta:RenderableAsset form="image" layout="pause-fullscreen"
                              duration="PT10S"
                              assetUrl="https://ads.example.com/creatives/p2/full.jpg"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=p2</Event>
          <Event id="2" presentationTime="10000">https://tracker.example.com/complete?ad=p2</Event>
        </EventStream>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

- `@onCandidatesExhausted` appears because the document is a pause
  document (§4.4 item 12). E.7 walks each of its three values.
- `@dismissAfter="PT5S"` makes the slot dismissible 5 s after its first
  rendered frame (§5.2.4).
- The two candidates share `@id` values on their beacons; the
  de-duplication scope is the candidate, so both impressions fire
  (§5.5.4).

### E.5 Sub-MPD of the video creative

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/p1/</BaseURL>
  <Period id="p1" duration="PT15S">
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="v/$RepresentationID$/init.mp4"
                       media="v/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" codecs="avc1.640028" bandwidth="5000000"
                      width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true">
      <SegmentTemplate timescale="48000" duration="144000" startNumber="1"
                       initialization="a/$RepresentationID$/init.mp4"
                       media="a/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" codecs="mp4a.40.2" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The option's `@duration="PT15S"` is derived from this Period's
`@duration`, which is canonical (§5.4).

### E.6 Player walk-through and device classes

At the pause (1500 s, inside 600–2400 s) the Player confirms it holds a
usable document (E.3), checks that the window is not consumed, and
walks the candidates in order and each candidate's options in order
(§4.5.3). Both window checks pass for every option: every layout is in
`pause-fullscreen pause-partial`. The device check follows §5.3.7.

A Player on D3, D4 or D5 MAY satisfy the fullscreen video option by
releasing the paused content's decoder and restoring the content at
1500 s on resume (§4.5.10 item 4). Declining to release it is equally
conformant; the table shows both choices.

| Class | p1 | p2 | Sequence presented |
|---|---|---|---|
| D1 | option 1, fullscreen video (free decoder) | fullscreen image | p1 15 s, p2 10 s |
| D2 | option 1, fullscreen video (second decoder) | skipped: an image surface is not satisfiable on D2 | p1 15 s |
| D3, decoder released | option 1, fullscreen video | fullscreen image | p1 15 s, p2 10 s |
| D3, decoder kept | option 2, partial HTML over the paused frame | fullscreen image | p1 15 s, p2 10 s |
| D4, decoder released | option 1, fullscreen video | fullscreen image | p1 15 s, p2 10 s |
| D4, decoder kept | option 3, partial image (HTML not satisfiable) | fullscreen image | p1 15 s, p2 10 s |
| D5, decoder released | option 1, fullscreen video | skipped: no image surface | p1 15 s |
| D5, decoder kept | skipped: no option satisfiable | skipped | none |

**Consumption.** The window is consumed when a pause ad begins
rendering (§4.5.10 item 6): at the first rendered frame of p1 on every
row but the last. On the last row nothing rendered, so the window stays
available and a later pause inside it triggers a new attempt. After
consumption, a later pause at, for example, 2000 s leaves the primary
content untouched.

### E.7 Exhaustion inside the pause

On D1 the candidates run out 25 s into the 60 s pause. The Player
applies `@onCandidatesExhausted` (§4.5.11). The three values, with the
pause ending at 60 s:

| Value | 0–25 s | 25–60 s | Ad on screen |
|---|---|---|---|
| `request-again` | p1, p2 | New request at 25 s; E.7.1 | 25 s if the new document is empty |
| `repeat` | p1, p2 | p1 25–40 s, p2 40–50 s, p1 50–60 s | 60 s |
| `stop` | p1, p2 | Paused frame | 25 s |

Under `repeat`, the resume at 60 s falls 10 s into the third
presentation of p1; E.8 applies.

#### E.7.1 The second request

At 25 s the Player sends the same request line as in E.3. In this
walk-through the APS answers with an empty pause document:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="pause" onCandidatesExhausted="stop"/>
  </Period>
</MPD>
```

A document carrying no candidates received under `request-again` is
`stop` for the rest of that pause (§5.2.6): the paused frame is shown
from 25 s to 60 s, and no further request is made during this pause.
Had the APS returned candidates, the Player would have presented them
in order and applied the new document's own `@onCandidatesExhausted`
when they ran out.

### E.8 Resume, dismissal and tracking

**Resume mid-ad.** The viewer resumes 9 s into p1. The Player removes
p1 within one rendering frame and continues the film from 1500 s
(§4.5.10 items 1 and 4). Beacons fired: `imp` (0) and `mid` (7500).
Not fired: `complete` (15000), because it falls after the pause-to-play
transition (§4.5.10 item 2). p2 is never presented. On D3, D4 and D5
with the decoder released, the decoder returns to the primary content
at the suspended position.

**Dismissal.** The slot becomes dismissible at 5 s. The viewer
dismisses at 7 s into p1. The whole slot ends (§4.5.14): p1 is
removed, p2 is not presented, `@onCandidatesExhausted` is not applied
because the slot is over, and `mid` (7500) is not fired. The viewer
gets the paused frame back **without resuming**; the film stays paused
at 1500 s until the viewer plays. The window was consumed at p1's first
frame, so no later pause in the session yields a pause ad.

**Before 5 s** the Player offers no dismissal; the viewer ends the ad
only by resuming.

### E.9 Measuring delivery

The play-list metric records a playback period that stops on
`UserRequest` at 1500 s and a next entry whose `starttype` is `Resume`
60 s later. The paused interval is 60 s (§8.12).

| Exhaustion value on D1 | Ad on screen | Filled fraction |
|---|---|---|
| `repeat` | 60 s | 60 / 60 = 100 % |
| `request-again` (empty second document) | 25 s | 25 / 60 ≈ 41.7 % |
| `stop` | 25 s | 25 / 60 ≈ 41.7 % |

A playback period that stopped on `Rebuffering` is a stall, triggers no
pause window, and is not counted (§4.5.17).

### E.10 Live variant

The same window in a live channel: the MPD is `type="dynamic"` and the
window sits in the current Period.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="dynamic" minBufferTime="PT2S"
     availabilityStartTime="2026-09-25T20:00:00Z"
     publishTime="2026-09-25T20:24:00Z"
     minimumUpdatePeriod="PT30S"
     timeShiftBufferDepth="PT5M">
  <BaseURL>https://live.publisher.example.com/channel-3/</BaseURL>
  <Period id="p-2000" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026"
                 timescale="1000">
      <Event id="511" presentationTime="600000" duration="1800000">
        <svta:PauseAdPresentation uri="https://aps.example.com/decision/pause-live"
                                  maxDuration="60000"
                                  allowedLayouts="pause-fullscreen pause-partial"
                                  earliestResolutionTimeOffset="30000"
                                  executeOnce="true"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" codecs="avc1.640028" bandwidth="6000000"
                      width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true">
      <SegmentTemplate timescale="48000" duration="192000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" codecs="mp4a.40.2" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
  <Metrics metrics="PlayList">
    <Range starttime="PT0S"/>
    <Reporting schemeIdUri="urn:example:publisher:reporting:2026"/>
  </Metrics>
</MPD>
```

The viewer, watching at the live edge, pauses at Period time 1500 s.
While paused, the Player's
presentation time stays frozen at 1500 s, inside the window, whatever
the live edge does (§4.5.10 item 5); the pause ad remains admissible for
the whole pause and the rules of E.6 to E.8 apply unchanged.

Where the Player resumes is decided after the resume (§8.8). With a
5-minute time-shift buffer:

| Pause length | Frozen position 1500 s still in the buffer? | Resume positions a Player may take |
|---|---|---|
| 60 s | yes (live edge ≈ 1560 s, oldest ≈ 1260 s) | the frozen position, or the live edge |
| 8 min | no (live edge ≈ 1980 s, oldest ≈ 1680 s) | the oldest available segment, or the live edge |

In every case the pause ad is removed within one frame at the resume and
its later beacons are not fired. The jump that follows is a Player
action outside the pause window.

---

## Annex F — Multi-ad break

*This annex is informative.*

### F.1 The scenario

Twenty minutes into an on-demand episode, the Publisher declares a
mid-roll break capped at 60 seconds. It does not say how many ads fill
it: that is the ADS's decision alone (§4.3). The ADS returns four ads,
back to back, whose durations add up to more than the cap. The Player
presents them in the order given, with no primary content between them,
and cuts the break at the cap even though that falls in the middle of
the fourth ad. The episode then resumes where it stopped.

### F.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static" mediaPresentationDuration="PT44M"
     minBufferTime="PT2S">
  <BaseURL>https://cdn.example.com/vod/series-5/ep-03/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="12" presentationTime="1200000" duration="1000">
        <InsertPresentation uri="https://aps.example.com/v1/linear/series-5/ep-03/mid-1"
                            maxDuration="60000"
                            executeOnce="true"
                            skipAfter="PT60S"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="360000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" mimeType="video/mp4" codecs="avc1.640028"
                      bandwidth="6000000" width="1920" height="1080" frameRate="25"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="192000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The cap is `maxDuration="60000"` in units of `timescale="1000"`: 60 s
of cumulative presentation (§4.5.4). No `@earliestResolutionTimeOffset`
is declared, so the base default of 60 s applies and ERT is
1 200 000 − 60 000 = 1 140 000 ms, i.e. 19:00 into the episode.

### F.3 The List MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list" minBufferTime="PT1S"
     publishTime="2026-09-25T21:10:04Z">
  <BaseURL>https://ads.example.com/creatives/</BaseURL>
  <Period id="ad-1" duration="PT15.018667S">
    <ImportedMPD earliestResolutionTimeOffset="0">c-501/creative.mpd</ImportedMPD>
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=501</Event>
      <Event id="2" presentationTime="15018">https://tracker.example.com/complete?ad=501</Event>
    </EventStream>
    <svta:AdTitle>Car 15s</svta:AdTitle>
  </Period>
  <Period id="ad-2" duration="PT20S">
    <ImportedMPD earliestResolutionTimeOffset="5">c-502/creative.mpd</ImportedMPD>
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=502</Event>
      <Event id="2" presentationTime="20000">https://tracker.example.com/complete?ad=502</Event>
    </EventStream>
    <svta:AdTitle>Bank 20s</svta:AdTitle>
  </Period>
  <Period id="ad-3" duration="PT15.018667S">
    <ImportedMPD earliestResolutionTimeOffset="5">c-503/creative.mpd</ImportedMPD>
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=503</Event>
      <Event id="2" presentationTime="15018">https://tracker.example.com/complete?ad=503</Event>
    </EventStream>
    <svta:AdTitle>Juice 15s</svta:AdTitle>
  </Period>
  <Period id="ad-4" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="5">c-504/creative.mpd</ImportedMPD>
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=504</Event>
      <Event id="2" presentationTime="3750">https://tracker.example.com/q1?ad=504</Event>
      <Event id="3" presentationTime="7500">https://tracker.example.com/mid?ad=504</Event>
      <Event id="4" presentationTime="11250">https://tracker.example.com/q3?ad=504</Event>
      <Event id="5" presentationTime="15000">https://tracker.example.com/complete?ad=504</Event>
    </EventStream>
    <svta:AdTitle>Phone 15s</svta:AdTitle>
  </Period>
</MPD>
```

Each Period is one ad, played in document order (§5.2.1). The four
streams carry the same `@id` values; that is correct, because
de-duplication is scoped to the Period and the Player fires every one of
them (§5.5.4). The durations of `ad-1` and `ad-3` are not whole
milliseconds: their creatives end on an audio frame boundary, and the
APS copied the value the sub-MPD declares.

### F.4 The sub-MPDs

The four sub-MPDs share one shape and differ in identifier, location and
`Period@duration`. `c-501/creative.mpd`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/c-501/</BaseURL>
  <Period id="c-501" duration="PT15.018667S">
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="96000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

`c-502/creative.mpd`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/c-502/</BaseURL>
  <Period id="c-502" duration="PT20S">
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="96000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

`c-503/creative.mpd`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/c-503/</BaseURL>
  <Period id="c-503" duration="PT15.018667S">
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="96000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

`c-504/creative.mpd`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/c-504/</BaseURL>
  <Period id="c-504" duration="PT15S">
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="96000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### F.5 The arithmetic

**Before play: declared durations in the cap's units.** Each
`Period@duration` is converted into the timescale of the cap and rounded
**up** to the next whole unit (§4.5.4):

| Period | `@duration` | × 1 000 | Rounded up (ms) | Cumulative (ms) | Against 60 000 |
|---|---|---|---|---|---|
| `ad-1` | `PT15.018667S` | 15 018.667 | 15 019 | 15 019 | within |
| `ad-2` | `PT20S` | 20 000 | 20 000 | 35 019 | within |
| `ad-3` | `PT15.018667S` | 15 018.667 | 15 019 | 50 038 | within |
| `ad-4` | `PT15S` | 15 000 | 15 000 | 65 038 | **past the cap by 5 038** |

Rounding up is what keeps a fraction of a unit from sliding under the
cap: truncating `ad-1` and `ad-3` to 15 018 would understate the break by
2 ms. A converted value equal to the cap would be admitted.

**What the Player may do with `ad-4`.** Its declared duration would push
the cumulative duration past the cap, so the Player MAY drop it before
play (§4.5.4). It is not obliged to. The two outcomes are both
conformant:

| Player choice | Ads presented | Break length | Primary content resumes after |
|---|---|---|---|
| Drop before play | `ad-1`, `ad-2`, `ad-3` | 50.037 s | 50.037 s |
| Trim during play | `ad-1` to `ad-3`, and `ad-4` cut mid-ad | 60 s | 60 s |

**During play: the actual rendered length governs.** The cap is enforced
against what is rendered, not against what was declared (§4.5.4 item
2). The first three ads render 15.018 667 + 20 + 15.018 667 =
50.037 334 s, which leaves 60 − 50.037 334 = **9.962 666 s** for `ad-4`.
Had any creative rendered longer than it declared, the trim point would
move earlier by the difference; the cap does not move.

### F.6 The Player's walk-through

This Player trims during play.

1. **Resolve.** Between ERT (19:00) and PRT (20:00) it issues
   `GET https://aps.example.com/v1/linear/series-5/ep-03/mid-1` and
   receives the List MPD of F.3, which it validates (§4.5.2, §4.6).
2. **Pause the episode at 20:00.** The insertion stops the primary
   timeline for the break (§5.1.1).
3. **Present `ad-1`, `ad-2`, `ad-3`** in document order, back to back,
   fetching each sub-MPD no earlier than its `<ImportedMPD>` offset
   allows: `ad-1` at the break's start, the others from 5 s before their
   Periods start. Each ad's impression fires at its first frame and its
   `complete` at its last (ad-local 15 018, 20 000 and 15 018 ms).
4. **Present `ad-4` until the cap.** Its beacons at ad-local 0, 3 750
   and 7 500 ms fire. At 9.962 666 s into `ad-4` the cumulative
   presentation reaches 60 s and the Player stops rendering it. The
   beacons at 11 250 ms (`q3`) and 15 000 ms (`complete`) fall after the
   trim boundary and are not fired (§4.5.13 item 2).
5. **Resume.** The episode continues from 20:00, where it stopped. The
   break took 60 s of presentation timeline and never more (§4.5.4
   item 1).

A Player that drops before play differs only in steps 4 and 5: it never
fetches `c-504/creative.mpd`, fires none of `ad-4`'s beacons, and
resumes the episode after 50.037 s.

The order is the ADS's and survives both choices: the Player does not
reorder the ads, and would not move `ad-4` ahead of a longer ad to fit
the cap better (§4.5.5).

**What neither Player does.** §4.5.4 gives two outcomes for an
overflowing break, drop before play and trim during play. Skipping the
whole break, or cutting back to the end of `ad-3` once `ad-4` has
started, is neither.

### F.7 Device classes

The outcome is the same on D1 to D5. Every ad is a linear video, and the
`linear`/`video` row of §5.3.7 is satisfiable on D1–D5: the ads and the
primary content are sequential on one decoder, switched at each Period
boundary. D1 and D2 MAY pre-buffer ad N+1 on their second decoder while
ad N plays; D3, D4 and D5 cannot, and switch the one decoder from ad to
ad. Pre-buffering is a Player implementation detail and changes neither
the order, the trim point nor the beacons (§7.2).

---

## Annex G — A Player that predates this specification

*This annex is informative.*

### G.1 The scenario

A viewer opens an on-demand documentary on a Player that conforms to the
base specification and does not implement this one. The Publisher's MPD
declares an overlay window ten minutes in and a pause window over the
whole programme. That Player has no knowledge of either: it removes what
it does not recognise and plays the programme (§4.7).

What the viewer sees around those windows is decided by the Publisher,
and the decision depends on the content (§7.9). For on-demand content
the Publisher authors, alongside the SGAI windows, a standard linear
break using base constructs only — here a 15-second pre-roll — which the
older Player plays. For live content it authors the SGAI windows alone
and accepts the opportunity as a loss on that Player (G.8). The
Publisher cannot tell from the manifest which Player will read it, so
the on-demand break is authored unconditionally.

### G.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static" mediaPresentationDuration="PT42M"
     minBufferTime="PT2S">
  <BaseURL>https://cdn.example.com/vod/doc-88/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="1" presentationTime="0" duration="1000">
        <InsertPresentation uri="https://aps.example.com/v1/linear/doc-88/preroll"
                            maxDuration="15000"
                            earliestResolutionTimeOffset="0"
                            executeOnce="true"
                            skipAfter="PT15S"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="2" presentationTime="600000" duration="30000">
        <svta:OverlayPresentation uri="https://aps.example.com/v1/overlay/doc-88/w2"
                                  maxDuration="15000"
                                  allowedLayouts="overlay-lower-third overlay-corner"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026" timescale="1000">
      <Event id="3" presentationTime="0" duration="2520000">
        <svta:PauseAdPresentation uri="https://aps.example.com/v1/pause/doc-88/w3"
                                  maxDuration="30000"
                                  executeOnce="true"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="360000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" mimeType="video/mp4" codecs="avc1.640028"
                      bandwidth="6000000" width="1920" height="1080" frameRate="25"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="192000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
  <Metrics metrics="PlayList">
    <Range starttime="PT0S"/>
    <Reporting schemeIdUri="urn:example:publisher:reporting:2026"/>
  </Metrics>
</MPD>
```

Three event streams, one per family, each with the single stream its
family may have in the Period (§5.1.5); the two SGAI streams carry no
`@value`. Event `1` is the standard break: an inherited construct that
the base specification defines, capped at 15 s as every slot is under
this specification (§4.2). The `<Metrics>` request is there because the
content carries a pause window (§5.9).

### G.3 The same document after removal of the extension namespace

The base specification obliges the author to make this document valid
and conformant once every element and attribute outside the DASH
namespace is removed (DASH §5.2.1). Removing them from G.2 gives:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static" mediaPresentationDuration="PT42M"
     minBufferTime="PT2S">
  <BaseURL>https://cdn.example.com/vod/doc-88/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="1" presentationTime="0" duration="1000">
        <InsertPresentation uri="https://aps.example.com/v1/linear/doc-88/preroll"
                            maxDuration="15000"
                            earliestResolutionTimeOffset="0"
                            executeOnce="true"
                            skipAfter="PT15S"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="2" presentationTime="600000" duration="30000"/>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026" timescale="1000">
      <Event id="3" presentationTime="0" duration="2520000"/>
    </EventStream>
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="360000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" mimeType="video/mp4" codecs="avc1.640028"
                      bandwidth="6000000" width="1920" height="1080" frameRate="25"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="192000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
  <Metrics metrics="PlayList">
    <Range starttime="PT0S"/>
    <Reporting schemeIdUri="urn:example:publisher:reporting:2026"/>
  </Metrics>
</MPD>
```

What remains is a valid MPD. The two SGAI streams survive as streams of
schemes the Player does not know, holding empty `<Event>` elements, which
is valid (§4.7.1). The standard break is untouched: no base element was
nested inside an SGAI element (§4.7).

### G.4 The List MPD of the standard break

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list" minBufferTime="PT1S"
     publishTime="2026-09-25T18:30:00Z">
  <BaseURL>https://ads.example.com/creatives/</BaseURL>
  <Period id="ad-31" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="0">c-5501/creative.mpd</ImportedMPD>
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=5501</Event>
      <Event id="2" presentationTime="7500">https://tracker.example.com/mid?ad=5501</Event>
      <Event id="3" presentationTime="15000">https://tracker.example.com/complete?ad=5501</Event>
    </EventStream>
    <svta:Click clickThroughUrl="https://brand-d.example.com/trial">
      <svta:ClickTracking>https://tracker.example.com/click?ad=5501</svta:ClickTracking>
    </svta:Click>
    <svta:AdTitle>Trial 15s</svta:AdTitle>
  </Period>
</MPD>
```

The APS answers every Player with the same document. The tracking sits
at a base position, on the Period, so both Players fire it; the
ClickThrough and the title sit after every DASH child, where the older
Player removes them (§4.7.4).

### G.5 The sub-MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/c-5501/</BaseURL>
  <Period id="c-5501" duration="PT15S">
    <AdaptationSet contentType="video" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" mimeType="video/mp4" codecs="avc1.4d401f"
                      bandwidth="3000000" width="1280" height="720" frameRate="25"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="48000" duration="96000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" mimeType="audio/mp4" codecs="mp4a.40.2"
                      bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### G.6 The walk-through on the older Player

1. **Parse.** The Player reads G.2 and removes the `svta:` elements, so
   what it works with is G.3. The base specification raises no error for
   the removal (§4.7 step 2).
2. **Standard break.** It recognises the insertion scheme of event `1`,
   computes ERT = 0 − 0 = 0, resolves the `@uri` and receives G.4. It
   removes `<svta:Click>` and `<svta:AdTitle>`, fetches the sub-MPD and
   plays the 15-second ad full-viewport. `@maxDuration` is a base
   attribute, so this Player bounds the ad by the same 15 s. It fires the
   three callback beacons at ad-local 0, 7 500 and 15 000 ms. The
   programme then starts at its first frame.
3. **Overlay window.** At 10:00 it reaches event `2`. The stream's scheme
   is not one it subscribes to (DASH §5.10.1), and the event is empty
   anyway. No request is issued, no beacon fires, and the programme
   plays on with no visible artefact.
4. **Pause window.** The viewer pauses at 25:00. Event `3` sits in a
   stream it also ignores. The paused frame stays on screen until the
   viewer resumes; nothing is requested.
5. **Metrics.** If the Player collects metrics, it collects `PlayList` as
   the base specification defines it.

The viewer saw one ad, the standard break. A Player older still, one that
does not implement the base alternative-MPD events either, ignores event
`1` in the same way as events `2` and `3` and plays the programme with no
ad.

### G.7 Construct by construct

| Construct | Where it sits | What the older Player does | See |
|---|---|---|---|
| Overlay and pause event schemes | `EventStream@schemeIdUri` in the main MPD | Does not act on the stream | §4.7.1 |
| `<svta:OverlayPresentation>`, `<svta:PauseAdPresentation>` | Child of an `<Event>` | Removes it; the `<Event>` is left empty | §4.7.2 |
| Non-linear resolution document | Returned by an overlay or pause `@uri` | Never requested, because the window was never acted on | §4.7.3 |
| `<InsertPresentation>` with `@maxDuration` | Base event | Executes it as the base specification defines, cap included | §5.1.1 |
| `<svta:Click>` and metadata on a List MPD Period | After the Period's DASH children | Removes them; the ad plays, the ClickThrough is inert | §4.7.4 |
| `<svta:RenderableAsset>` on a List MPD Period (not used in G.4) | After the Period's DASH children | Removes it; the `<ImportedMPD>` video plays, and the image or HTML alternative is unseen | §4.7.4 |
| Callback stream on a List MPD Period or in a sub-MPD | Base position | Fires it as a base callback event | §5.5.2 |
| Callback stream inside `<svta:Candidate>` | Inside an extension element | Never reached; the ad it tracks is never presented | §4.7 |
| Reserved query parameters, `urn:svta:dash:sgai-resolution:2026` | Resolution request URL; `@includeInRequests` | Never sends the parameters; drops the URN token if it meets one | §4.7.5 |
| `<Metrics metrics="PlayList">` | Main MPD | Base construct; collected as the base defines | §5.9 |

### G.8 The authoring choice: live and on-demand

| Content | What the Publisher authors | What the older Player shows | What a Player of this specification shows |
|---|---|---|---|
| On-demand | The SGAI windows **and** a standard linear break of base constructs, as G.2 | The standard break, then the programme | See G.9 |
| Live | The SGAI windows only | The channel, uninterrupted | The non-linear ads the windows resolve to |

**On-demand.** Inserting a break into on-demand content costs no
programme: the timeline stops for the ad and resumes where it stopped.
Monetising the opportunity on an older Player is then worth authoring,
and this specification recommends it (§4.2 item 12).

**Live.** A standard break in a live stream is a replacement, and a
replacement takes the place of a span of the channel the viewer would
otherwise see. The Publisher authors the SGAI windows alone:

```xml
<Period id="p1" start="PT0S">
  <EventStream xmlns:svta="urn:svta:dash:sgai:2026"
               schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
    <Event id="2" presentationTime="7800000" duration="30000">
      <svta:OverlayPresentation uri="https://aps.example.com/v1/overlay/ch7/w2"
                                maxDuration="15000"
                                allowedLayouts="overlay-lower-third overlay-corner"/>
    </Event>
  </EventStream>
  <!-- AdaptationSets of the channel -->
</Period>
```

On the older Player the opportunity is an expected loss, not an error
(§4.2 item 12): the channel plays, no request is issued, and nothing
reaches the screen or a tracker.

### G.9 The same document on a Player of this specification

A Player that implements this specification reads G.2 without removing
anything. Event `1` is a linear-family event, and it resolves and
executes it as the base specification defines (§4.5.1 item 1), reading
the `<svta:Click>` of G.4 as well (§4.5.15). Windows `2` and `3` it
serves as §6.2 and §6.3 describe: it resolves the overlay window with
`sgaiAllowedLayouts=overlay-lower-third%20overlay-corner` forwarded
(§5.8.3), and resolves the pause window when the viewer pauses inside
it. The Publisher wrote one document, and each Player takes from it
what it implements.

### G.10 Device classes

The outcome on the older Player does not vary by device class. It
depends on the Player's version and on the content type, not on the
hardware (§7.9): a D1 device running that Player behaves as a D5 device
running it. On a Player of this specification the standard break plays
on every class, since the `linear`/`video` row of §5.3.7 is satisfiable
on D1–D5, and what renders from windows `2` and `3` follows the overlay
and pause rows of §3.6.

---

## Annex H — An overlay window crossing a pause window

*This annex is informative.*

### H.1 Scenario

An on-demand film carries an overlay window from 1200 s to 1260 s with a
30-second cap, and a pause window covering the whole film. The overlay
slot presents two ads in sequence: a lower-third unit of 20 s, then a
corner image of 10 s. The viewer pauses at 1212 s, 12 s into the first
overlay ad, and stays paused for 40 s.

While paused inside the pause window with an overlay active, the Player
renders the pause ad and suspends the overlay (§4.5.9 item 1). The pause
ad is the only ad surface visible, whether it is fullscreen or partial.
On resume the pause ad is dismissed, and the overlay is restored from
where it was suspended if its window is still open (Branch A), or the
surface stays clear if the window closed (Branch B) (§4.5.9 item 2).

### H.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static" minBufferTime="PT2S"
     mediaPresentationDuration="PT42M">
  <BaseURL>https://cdn.publisher.example.com/film-9/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
                 timescale="1000">
      <Event id="601" presentationTime="1200000" duration="60000">
        <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay"
                                  maxDuration="30000"
                                  allowedLayouts="overlay-lower-third overlay-corner"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026"
                 timescale="1000">
      <Event id="602" presentationTime="0" duration="2520000">
        <svta:PauseAdPresentation uri="https://aps.example.com/decision/pause"
                                  maxDuration="60000"
                                  earliestResolutionTimeOffset="0"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" codecs="avc1.640028" bandwidth="6000000"
                      width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true">
      <SegmentTemplate timescale="48000" duration="192000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" codecs="mp4a.40.2" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
  <Metrics metrics="PlayList">
    <Range starttime="PT0S"/>
    <Reporting schemeIdUri="urn:example:publisher:reporting:2026"/>
  </Metrics>
</MPD>
```

- Each family has its own stream, and neither carries `@value`
  (§5.1, §5.1.5).
- The overlay window declares no offset, so its earliest resolution
  time is the 60-second default: `1200000 − 60000 = 1140000` ms, 1140 s.
- The pause window declares `0`: it is resolved when the viewer pauses.
  It declares no `@allowedLayouts` and admits the pause family default,
  `pause-fullscreen pause-partial` (§3.4.3). No `@executeOnce`: every
  qualifying pause may carry a pause ad.
- The `<Metrics>` element is required whenever the content carries
  pause windows (§4.2 item 10); its `<Reporting>` child is required by
  the base schema and its scheme is the Publisher's.

### H.3 Resolution requests

The overlay window declares `@allowedLayouts`, so its request forwards
them (§5.8.3); the pause window declares none, so its request carries
no `sgaiAllowedLayouts`. A Player that sends no capability parameter:

```
GET /decision/overlay?sgaiAllowedLayouts=overlay-lower-third%20overlay-corner
GET /decision/pause
```

The two requests are independent, and each document is validated
against its own window (§4.5.7).

### H.4 Overlay resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T20:40:00Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay">
      <svta:Candidate id="o1">
        <svta:RenderableAsset form="video" layout="overlay-lower-third"
                              duration="PT20S"
                              assetUrl="https://ads.example.com/creatives/o1/o1.mpd"/>
        <svta:RenderableAsset form="html" layout="overlay-lower-third"
                              duration="PT20S"
                              assetUrl="https://ads.example.com/creatives/o1/lt.html"/>
        <svta:RenderableAsset form="image" layout="overlay-lower-third"
                              duration="PT20S"
                              assetUrl="https://ads.example.com/creatives/o1/lt.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=o1</Event>
          <Event id="2" presentationTime="10000">https://tracker.example.com/mid?ad=o1</Event>
          <Event id="3" presentationTime="20000">https://tracker.example.com/complete?ad=o1</Event>
        </EventStream>
      </svta:Candidate>
      <svta:Candidate id="o2">
        <svta:RenderableAsset form="image" layout="overlay-corner"
                              duration="PT10S"
                              assetUrl="https://ads.example.com/creatives/o2/corner.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=o2</Event>
        </EventStream>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

The document declares no `@dismissAfter`, so the overlay slot is not
dismissible (§5.2.4).

### H.5 Pause resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T20:41:12Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="pause" onCandidatesExhausted="stop">
      <svta:Candidate id="q1">
        <svta:RenderableAsset form="video" layout="pause-fullscreen"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/creatives/q1/q1.mpd"/>
        <svta:RenderableAsset form="html" layout="pause-partial"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/creatives/q1/partial.html"/>
        <svta:RenderableAsset form="image" layout="pause-partial"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/creatives/q1/partial.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=q1</Event>
          <Event id="2" presentationTime="15000">https://tracker.example.com/complete?ad=q1</Event>
        </EventStream>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

No `@usableFor`: resolved at the pause, the document is fresh. With
`stop`, the paused frame is shown once q1 ends (§5.2.6).

### H.6 Sub-MPDs of the video creatives

Overlay creative o1:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/o1/</BaseURL>
  <Period id="o1" duration="PT20S">
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="v/$RepresentationID$/init.mp4"
                       media="v/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v540" codecs="avc1.4d401f" bandwidth="1500000"
                      width="960" height="540"/>
    </AdaptationSet>
  </Period>
</MPD>
```

Pause creative q1:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/q1/</BaseURL>
  <Period id="q1" duration="PT15S">
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="v/$RepresentationID$/init.mp4"
                       media="v/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" codecs="avc1.640028" bandwidth="5000000"
                      width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true">
      <SegmentTemplate timescale="48000" duration="144000" startNumber="1"
                       initialization="a/$RepresentationID$/init.mp4"
                       media="a/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" codecs="mp4a.40.2" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The overlay creative carries no audio: it is composited over a primary
content that keeps its own sound.

### H.7 Player walk-through (Branch A: window still open on resume)

| Primary time | Event |
|---|---|
| 1140 s | Earliest resolution time of window 601; the Player may request the overlay document from here on. |
| 1200 s | o1 starts. Beacon `imp` of o1 fires. |
| 1210 s | Beacon `mid` of o1 (10000) fires. |
| 1212 s | The viewer pauses. The pause is inside window 602. The Player suspends o1 at 12 s into it, requests the pause document, and presents q1. |
| paused, 0–15 s | q1 on screen. Beacons `imp` and `complete` of q1 fire. |
| paused, 15–40 s | `stop`: the paused frame is shown. o1 stays suspended. |
| 1212 s, resume | The pause ad is already gone; had it still been on screen it would be removed within one frame (§4.5.10 item 1). Window 601 is open (it ends at 1260 s), so o1 is restored at 12 s into it. |
| 1220 s | o1 ends. Beacon `complete` of o1 (20000) fires. o2 starts. |
| 1230 s | o2 ends. The cap is reached; the slot is over. |

**Cap arithmetic.** The cap is 30000 in units of `timescale="1000"`,
that is 30 s. The cap is measured on the presentation timeline, and an
interval in which the timeline does not advance accrues nothing
(§4.5.4 item 5).

| Interval | Accrued by the overlay slot | Cumulative |
|---|---|---|
| 1200–1212 s (o1) | 12000 | 12000 |
| Pause, 40 s of wall clock | 0 | 12000 |
| 1212–1220 s (o1) | 8000 | 20000 |
| 1220–1230 s (o2) | 10000 | 30000 |

`PT20S` and `PT10S` convert to 20000 and 10000 with no rounding; the
cumulative 30000 equals the cap and is admitted (§4.5.4 item 4). The
window's own end, 1260 s, is not reached.

### H.8 Branch B: the window closed before the resume

Branch B needs the resume to land past the overlay window's end. On
on-demand content the primary timeline is frozen at 1212 s for the
whole pause, so window 601 is always open on resume and Branch A
applies. The branch occurs in live content, where the resume position
is a Player action after the resume (§8.8).

The same two windows in a live channel with `timeShiftBufferDepth="PT5M"`;
the viewer, at the live edge, pauses at 1212 s for 8 minutes:

| Quantity | Value |
|---|---|
| Frozen presentation time during the pause | 1212 s (§4.5.10 item 5) |
| Live edge at resume | ≈ 1212 + 480 = 1692 s |
| Oldest position the buffer holds | ≈ 1692 − 300 = 1392 s |
| End of window 601 | 1260 s |

The frozen position is no longer in the buffer. The Player resumes at
the oldest available segment (≈ 1392 s) or at the live edge (≈ 1692 s);
both lie after 1260 s. The overlay is over and the surface stays clear
(§4.5.9 item 2). o1's `complete` beacon and o2 never fire. The slot
ends having accrued 12000 of its 30000.

### H.9 Device classes

Overlay document (H.4), for window 601 (§5.3.7):

| Class | o1 | o2 | Overlay slot |
|---|---|---|---|
| D1 | video lower-third | image corner | o1 20 s, o2 10 s |
| D2 | video lower-third | skipped: image not satisfiable | o1 20 s |
| D3 | HTML lower-third | image corner | o1 20 s, o2 10 s |
| D4 | image lower-third | image corner | o1 20 s, o2 10 s |
| D5 | skipped | skipped | none; the window does not admit `linear` |

Pause document (H.5), during the pause at 1212 s. "Released" means the
Player releases the resources of the paused primary content and of the
suspended overlay to present the fullscreen video, which it MAY do for a
fullscreen pause ad (§4.5.10 item 3), and restores both on resume.

| Class | q1 | Overlay during the pause |
|---|---|---|
| D1 | option 1, fullscreen video | suspended |
| D2 | option 1, fullscreen video: the second decoder, held by the suspended video overlay, is released for it | suspended; restored on resume |
| D3 | released: option 1, fullscreen video; kept: option 2, partial HTML over the paused frame | suspended |
| D4 | released: option 1, fullscreen video; kept: option 3, partial image | suspended |
| D5 | released: option 1, fullscreen video; kept: no option satisfiable | none was rendered |

With a partial pause ad (D3 or D4, resources kept), the paused frame
stays visible around the pause ad and the overlay stays suspended: the
pause ad is the only ad surface on screen (§4.5.10 item 3).

On D5 with resources kept, nothing renders in either slot: the pause
and the resume have no ad-related effect. On every other row the
resume behaves as H.7 (Branch A) or H.8 (Branch B).

---

## Annex I — One ad, ordered options, resolved across the device classes

*This annex is informative.*

### I.1 The scenario

One ad is offered for one overlay window. The candidate carries four
presentation options, and their document order is the preference order
(§5.3.4):

1. `squeezeback-double-box-background`, a video ad with an advertiser
   background image;
2. `squeezeback-l-shape-upper-left`, a full-frame image creative;
3. `overlay-lower-third`, an image banner;
4. `linear`, a full-screen video takeover.

The Publisher declares one device-agnostic set of allowed layouts that
lists all four tokens. The Player sends no capability parameter
(§5.8.2), so neither the APS nor the ADS holds a view of the device, and
every viewer receives the same document. The five device classes of §3.6
nevertheless land on three different layouts, because each Player walks
the same list against its own budget (§5.3.7) and renders the first
option that passes (§4.5.3).

### I.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static"
     mediaPresentationDuration="PT45M"
     minBufferTime="PT2S">
  <Period id="main" start="PT0S">

    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
                 timescale="1000">
      <Event id="401" presentationTime="600000" duration="60000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/overlay"
            maxDuration="15000"
            allowedLayouts="squeezeback-double-box-background squeezeback-l-shape-upper-left overlay-lower-third linear"
            earliestResolutionTimeOffset="20000"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="https://cdn.example.com/programme/video/init.mp4"
                       media="https://cdn.example.com/programme/video/seg-$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="https://cdn.example.com/programme/audio/init.mp4"
                       media="https://cdn.example.com/programme/audio/seg-$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

| Quantity | Value |
|---|---|
| Window | 600 000 to 660 000 at timescale 1000: 600 s to 660 s |
| Earliest resolution time | 600 000 − 20 000 = 580 000: 580 s (§4.5.1) |
| Cap | 15 000 units: 15 s of cumulative presentation (§4.5.4) |

The window declares `@allowedLayouts`, so the Player forwards it on the
request (§5.8.3) — the one parameter this Player sends:

```
GET /decision/overlay?sgaiAllowedLayouts=squeezeback-double-box-background%20squeezeback-l-shape-upper-left%20overlay-lower-third%20linear
Host: aps.example.com
```

`linear` is admitted only because the window lists it; the overlay
family default does not include it (§3.4.3).

### I.3 The resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T12:09:41Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay">
      <svta:Candidate id="c1">

        <svta:RenderableAsset form="video"
                              layout="squeezeback-double-box-background"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/dbox.mpd"
                              backgroundUrl="https://ads.example.com/c1/background.jpg"/>
        <svta:RenderableAsset form="image"
                              layout="squeezeback-l-shape-upper-left"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/lshape.jpg"/>
        <svta:RenderableAsset form="image"
                              layout="overlay-lower-third"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/banner.png"/>
        <svta:RenderableAsset form="video"
                              layout="linear"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/takeover.mpd"/>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0">https://tracker.example.com/impression?ad=c1</Event>
          <Event presentationTime="3750">https://tracker.example.com/q1?ad=c1</Event>
          <Event presentationTime="7500">https://tracker.example.com/mid?ad=c1</Event>
          <Event presentationTime="11250">https://tracker.example.com/q3?ad=c1</Event>
          <Event presentationTime="15000">https://tracker.example.com/complete?ad=c1</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://advertiser.example.com/landing">
          <svta:ClickTracking>https://tracker.example.com/click?ad=c1</svta:ClickTracking>
        </svta:Click>

        <svta:AdSystem>example-ads</svta:AdSystem>
        <svta:AdTitle>Four presentations of one ad</svta:AdTitle>

      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

- `@backgroundUrl` appears on option 1 only, the one
  `squeezeback-double-box-background` option (§5.3.1, §4.6 step 4).
- The two video options address sub-MPDs; the two image options address
  the creative itself (§5.3.2).
- The tracking schedule sits on the candidate, so the same beacons fire
  whichever option is rendered, at offsets from the start of that
  option's presentation (§5.5.3).
- The document carries no `@dismissAfter`: the slot is not dismissible
  (§5.2.4).
- Every option declares `PT15S`, which converts to 15 000 units at the
  cap's timescale and equals the cap. A converted duration equal to the
  cap is admitted (§4.5.4 item 4). Starting at 600 s, the slot ends at
  615 s, before the window's end at 660 s.

### I.4 The sub-MPDs

`https://ads.example.com/c1/dbox.mpd` — the ad box of option 1. At
960 × 540 it is 25 % of a 1920 × 1080 frame (518 400 of 2 073 600
pixels), the bound the token names (§3.4.2). The shrunk primary content
and the background are composited by the Player around it.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S">
  <Period id="1" duration="PT15S">
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="https://ads.example.com/c1/dbox/init.mp4"
                       media="https://ads.example.com/c1/dbox/seg-$Number$.m4s"/>
      <Representation id="v540" bandwidth="2500000" width="960" height="540"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="https://ads.example.com/c1/dbox/audio-init.mp4"
                       media="https://ads.example.com/c1/dbox/audio-$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

`https://ads.example.com/c1/takeover.mpd` — option 4, at full frame.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S">
  <Period id="1" duration="PT15S">
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="https://ads.example.com/c1/takeover/init.mp4"
                       media="https://ads.example.com/c1/takeover/seg-$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="https://ads.example.com/c1/takeover/audio-init.mp4"
                       media="https://ads.example.com/c1/takeover/audio-$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

Both declare `Period@duration="PT15S"`, which is canonical; the options'
`@duration` values are derived from them (§5.4). Each is five 3-second
segments.

### I.5 Element type and element count

What an option costs is the number **and the type** of the elements it
puts on screen at once (§5.3.6, §5.3.7).

| Option | Elements on screen | Video decoders | Non-video surfaces | Satisfiable on (§5.3.7) |
|---|---|---|---|---|
| 1 | shrunk primary content, ad video, background image | 2 | 1 image | D1 |
| 2 | full-frame image creative, shrunk primary content on top | 1 | 1 image | D1, D3, D4 |
| 3 | primary content, image banner over it | 1 | 1 image | D1, D3, D4 |
| 4 | ad video alone; the primary content is suspended | 1, reused sequentially | none | D1–D5 |

Option 1 has three elements, and the third is a still image. A device
needs the count (two decoders) and the type (an image surface) together.
D2 has the count and not the type; D3 and D4 have the type and not the
count. Option 2 has no third element: the L-shape creative is itself the
full-frame background, and the shrunk primary content is the programme,
not a creative anyone supplies.

### I.6 The walk per device class

Every option's `@layout` is in the window's allowed layouts, so check (b)
of §4.5.3 passes for every option on every class; every outcome below is
decided by check (a), the device.

| Class | Option 1 | Option 2 | Option 3 | Option 4 | Renders |
|---|---|---|---|---|---|
| D1 | passes | — | — | — | 1: double box with background |
| D2 | fails: background is an image | fails: image creative | fails: image creative | passes | 4: takeover |
| D3 | fails: one decoder | passes | — | — | 2: L-shape |
| D4 | fails: one decoder | passes | — | — | 2: L-shape |
| D5 | fails: one decoder, no image surface | fails: no image surface | fails: no image surface | passes | 4: takeover |

"—" marks an option not evaluated, because the walk stopped at the first
that passed.

- **D1** shrinks the primary content into the centre-left box, plays
  the ad in the centre-right box, and fills the uncovered bands with
  `background.jpg`. The background is composited as part of the chosen
  layout; it is not walked as an option (§5.3.6).
- **D2** owns the two decoders option 1 needs and still declines it,
  because the background image is a surface type D2 does not composite.
  Options 2 and 3 fail on the same type. The takeover needs no concurrent
  composition and passes.
- **D3 and D4** fail option 1 on the decoder count and pass option 2:
  one decoder for the shrunk primary content, one image surface for the
  full-frame creative. D4's lack of an HTML surface is irrelevant here,
  because no option ahead of the takeover is HTML.
- **D5** composites nothing over video. It reaches the same option as D2
  by a different path, and it renders an ad at all only because the
  window admits `linear` and the candidate offers it (§3.6, §7.3).

On the takeover, the primary content is suspended at 600 s for the 15 s
of the ad and resumes from 600 s (§5.3.3). Its tracking fires against
the ad's own presentation, from `0` at its first frame to `15000` at its
last.

### I.7 What the scenario shows

One ordered list, emitted identically to every viewer, and one
device-agnostic declaration produce the correct layout on each class: D1
on the double box, D3 and D4 on the L-shape, D2 and D5 on the takeover.
No actor upstream of the Player holds a device-class matrix, and the
Publisher declares no per-device layout set. Annex M serves the same ad
to the same window with the capability check moved to the APS, and every
class lands on the same result.

---

## Annex J — Double box, the three-element layout

*This annex is informative.*

### J.1 Scenario

An on-demand title carries an overlay window that admits the two
double-box layouts. In a double box the primary content is shrunk into
the centre-left box and the ad sits in the centre-right box, each 25 %
of the frame (§3.4.2). The two boxes leave bands uncovered.

- **`squeezeback-double-box`** puts **two** elements on screen, the
  shrunk primary content and the ad. The uncovered bands render black.
- **`squeezeback-double-box-background`** adds a **third** element: the
  advertiser's background image at `@backgroundUrl`, filling the bands
  (§5.3.6). The background is always a still image. It never consumes a
  video decoder, but it always needs an image surface.

The background is a composition attribute of the layout and not an
option of its own. The Player does not walk it. It composites it as part
of rendering the layout, once that layout is chosen (§5.3.6). The ad
itself may be video, image or HTML. Which device can compose the layout
depends on the **type** of each element, not only on how many elements
there are. This annex shows the case where that matters most: D2 has the
two decoders a video double box needs, and still declines the variant
with a background.

### J.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static"
     mediaPresentationDuration="PT50M"
     minBufferTime="PT2S">
  <BaseURL>https://cdn.publisher.example.com/vod/match-0917/</BaseURL>
  <Period id="main" duration="PT50M">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
                 timescale="1000">
      <Event id="410" presentationTime="1500000" duration="30000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/double-box"
            maxDuration="20000"
            allowedLayouts="squeezeback-double-box-background squeezeback-double-box"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" codecs="avc1.640028"
                      width="1920" height="1080" frameRate="50"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" codecs="mp4a.40.2"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The window declares no `@earliestResolutionTimeOffset`, so it may be
resolved from 60 s before it starts (§5.1.3).

### J.3 The resolution request

```
GET /decision/double-box?sgaiAllowedLayouts=squeezeback-double-box-background%20squeezeback-double-box
Host: aps.example.com
```

### J.4 The resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T19:24:10Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay">
      <svta:Candidate id="db-3310">
        <svta:RenderableAsset form="video"
            layout="squeezeback-double-box-background" duration="PT20S"
            assetUrl="https://ads.example.com/creatives/db-3310/box.mpd"
            backgroundUrl="https://ads.example.com/creatives/db-3310/bands.jpg"/>
        <svta:RenderableAsset form="video"
            layout="squeezeback-double-box" duration="PT20S"
            assetUrl="https://ads.example.com/creatives/db-3310/box.mpd"/>
        <svta:RenderableAsset form="html"
            layout="squeezeback-double-box-background" duration="PT20S"
            assetUrl="https://ads.example.com/creatives/db-3310/box.html"
            backgroundUrl="https://ads.example.com/creatives/db-3310/bands.jpg"/>
        <svta:RenderableAsset form="image"
            layout="squeezeback-double-box-background" duration="PT20S"
            assetUrl="https://ads.example.com/creatives/db-3310/box.png"
            backgroundUrl="https://ads.example.com/creatives/db-3310/bands.jpg"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0">https://tracker.example.com/imp?ad=db-3310</Event>
          <Event presentationTime="10000">https://tracker.example.com/mid?ad=db-3310</Event>
          <Event presentationTime="20000">https://tracker.example.com/done?ad=db-3310</Event>
        </EventStream>
        <svta:Click clickThroughUrl="https://sponsor.example.com/match">
          <svta:ClickTracking>https://tracker.example.com/click?ad=db-3310</svta:ClickTracking>
        </svta:Click>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

`@backgroundUrl` appears on every `squeezeback-double-box-background`
option and on no other (§5.3.1; §4.6 step 4). Option 2 is the same
video as option 1 in the same boxes, without the background. That is
the only difference between them, and it is exactly what decides D2.

### J.5 The sub-MPD

Shared by options 1 and 2:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/db-3310/</BaseURL>
  <Period id="db-3310" duration="PT20S">
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="v/$RepresentationID$/init.mp4"
                       media="v/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v960" bandwidth="1800000" codecs="avc1.64001f"
                      width="960" height="540" frameRate="50"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### J.6 The budget, per layout and form

The six double-box rows of §5.3.7, laid out by class:

| Layout | Ad form | Decoders | Non-video surfaces | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|---|---|---|
| `squeezeback-double-box` | `video` | 2 | none | yes | **yes** | no | no | no |
| `squeezeback-double-box` | `image` | 1 | image (ad) | yes | no | yes | yes | no |
| `squeezeback-double-box` | `html` | 1 | HTML (ad) | yes | no | yes | no | no |
| `squeezeback-double-box-background` | `video` | 2 | image (background) | yes | **no** | no | no | no |
| `squeezeback-double-box-background` | `image` | 1 | image (ad) + image (background) | yes | no | yes | yes | no |
| `squeezeback-double-box-background` | `html` | 1 | HTML (ad) + image (background) | yes | no | yes | no | no |

The two bold cells show the rule. With a video ad, adding the background
changes D2's answer from yes to no. It adds no decoder: it adds an
element of a type D2 cannot composite. For D3 and D4 the background
changes nothing, because they already need an image or HTML surface for
the ad, and they have an image surface. D5 composes no double box in any
form: a video ad needs a second decoder, and every other combination
needs a non-video surface.

### J.7 The walk per device class

Both layouts are in the window's allowed layouts, so the window check
passes for all four options. Only the device check decides (§4.5.3).

- **D1** accepts option 1: the video ad in the right box on its second
  decoder, and `bands.jpg` in the bands.
- **D2** declines option 1. It has the two decoders, but the background
  is an image surface and D2 composites none. It accepts option 2: the
  same video in the same box, with black bands. The walk reaches a
  layout D2 can build, and the ad is still delivered.
- **D3** declines options 1 and 2, because each needs a second decoder.
  It accepts option 3: the HTML ad in the right box and `bands.jpg` in
  the bands, on one decoder plus an HTML surface and an image surface.
- **D4** declines options 1 and 2 for the decoder and option 3 because
  it renders no HTML over video. It accepts option 4: the image ad and
  the image background, on one decoder plus image surfaces.
- **D5** declines all four options. The candidate is skipped, and since
  there is no other candidate the primary content continues at full
  frame. No beacon fires, and this is not a failed execution of the
  window (§4.5.6 item 4).

**Walk at a glance:**

| Class | Option 1: video, background | Option 2: video, no background | Option 3: HTML, background | Option 4: image, background | Renders |
|---|---|---|---|---|---|
| D1 | accepted | — | — | — | option 1 |
| D2 | declined: image background | accepted | — | — | option 2, black bands |
| D3 | declined: 2 decoders | declined: 2 decoders | accepted | — | option 3 |
| D4 | declined: 2 decoders | declined: 2 decoders | declined: HTML | accepted | option 4 |
| D5 | declined | declined | declined | declined | none |

**Ordering.** Option 2 sits after option 1, so D1 shows the branded
bands and only D2 falls back to black bands. Reversing the two options
would put black bands on D1 as well, and no class would ever render the
background with the video ad. Richest first, most robust last, is the
ordering §8.7 recommends. It is the ADS's order, though, and the Player
honours whatever order arrives (§4.5.5).

### J.8 Timing and cap arithmetic

| Quantity | Computation | Value |
|---|---|---|
| Window | `1500000` + `30000` | 1500.000 s to 1530.000 s |
| Earliest resolution time | `1500000 − 60000` (default offset) | 1440.000 s |
| Selected option | `PT20S` → `20000` against `maxDuration="20000"` | equal, so admitted (§4.5.4 item 4) |
| On screen | first frame at the window's start | 1500.000 s to 1520.000 s |
| Beacons | offsets `0`, `10000`, `20000` | 1500.000 s, 1510.000 s, 1520.000 s |

At 1520.000 s the Player restores the primary content to full frame, 10
seconds before the window closes. The cap ends the slot, not the window.
The document declares no `@dismissAfter`, so the slot is not dismissible
(§5.2.4). The `@duration` of the video options comes from the sub-MPD's
`Period@duration`, which is canonical (§5.4). For the HTML and image
options the declared `PT20S` is the only source.

---

## Annex K — ClickThrough

*This annex is informative.*

### K.1 Scenario

An on-demand episode carries a linear mid-roll at 300 s and an overlay
window at 900 s. Both ads carry a ClickThrough: a destination the
viewer reaches by activating the ad (a select on a remote, a tap), and
click-tracking URLs the Player fires at that moment. The ClickThrough
travels with the ad in the resolution document, in `<svta:Click>`
(§5.6); the Publisher declares nothing for it beyond the slot.

The activation is a user action. It has no presentation time, fires
only when the viewer acts, and never fires on the timeline (§4.5.15).
That is what separates click-tracking from the callback beacons, which
fire at scheduled times whether or not the viewer does anything.

### K.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static" minBufferTime="PT2S"
     mediaPresentationDuration="PT24M">
  <BaseURL>https://cdn.publisher.example.com/episode-4/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="101" presentationTime="300000" duration="1000">
        <InsertPresentation uri="https://aps.example.com/decision/midroll"
                            maxDuration="30000"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
                 timescale="1000">
      <Event id="201" presentationTime="900000" duration="30000">
        <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay"
                                  maxDuration="20000"
                                  allowedLayouts="overlay-corner overlay-lower-third"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" codecs="avc1.640028" bandwidth="6000000"
                      width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true">
      <SegmentTemplate timescale="48000" duration="192000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" codecs="mp4a.40.2" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

`<InsertPresentation>` is admissible because the MPD is `static`
(§4.2 item 3). The overlay request forwards the declared layouts
(§5.8.3):

```
GET /decision/overlay?sgaiAllowedLayouts=overlay-corner%20overlay-lower-third
```

### K.3 Linear: the List MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list" minBufferTime="PT1S"
     publishTime="2026-09-25T21:00:00Z">
  <Period id="ad-01" duration="PT20S">
    <ImportedMPD earliestResolutionTimeOffset="0">https://ads.example.com/creatives/l1/l1.mpd</ImportedMPD>
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=l1</Event>
      <Event id="2" presentationTime="10000">https://tracker.example.com/mid?ad=l1</Event>
      <Event id="3" presentationTime="20000">https://tracker.example.com/complete?ad=l1</Event>
    </EventStream>
    <svta:Click clickThroughUrl="https://advertiser-b.example.com/landing">
      <svta:ClickTracking>https://tracker.example.com/click?ad=l1</svta:ClickTracking>
      <svta:ClickTracking>https://verifier.example.net/c?id=l1</svta:ClickTracking>
    </svta:Click>
    <svta:AdSystem>ExampleADS</svta:AdSystem>
    <svta:Advertiser>Advertiser B</svta:Advertiser>
  </Period>
</MPD>
```

Every `svta:` child comes after every DASH-namespace child of the Period
(§5.2.1): `<ImportedMPD>` and the callback `<EventStream>` first, then
`<svta:Click>`, then the metadata. The 20 s ad fits the 30 s cap.

Sub-MPD of the linear creative:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/l1/</BaseURL>
  <Period id="l1" duration="PT20S">
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="v/$RepresentationID$/init.mp4"
                       media="v/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" codecs="avc1.640028" bandwidth="5000000"
                      width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true">
      <SegmentTemplate timescale="48000" duration="96000" startNumber="1"
                       initialization="a/$RepresentationID$/init.mp4"
                       media="a/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" codecs="mp4a.40.2" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### K.4 Non-linear: the overlay document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T21:10:00Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay" dismissAfter="PT3S">
      <svta:Candidate id="k1">
        <svta:RenderableAsset form="html" layout="overlay-lower-third"
                              duration="PT10S"
                              assetUrl="https://ads.example.com/creatives/k1/lt.html"/>
        <svta:RenderableAsset form="image" layout="overlay-corner"
                              duration="PT10S"
                              assetUrl="https://ads.example.com/creatives/k1/corner.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=k1</Event>
          <Event id="2" presentationTime="10000">https://tracker.example.com/complete?ad=k1</Event>
        </EventStream>
        <svta:Click clickThroughUrl="https://advertiser-c.example.com/shop">
          <svta:ClickTracking>https://tracker.example.com/click?ad=k1</svta:ClickTracking>
        </svta:Click>
      </svta:Candidate>
      <svta:Candidate id="k2">
        <svta:RenderableAsset form="image" layout="overlay-corner"
                              duration="PT10S"
                              assetUrl="https://ads.example.com/creatives/k2/corner.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=k2</Event>
        </EventStream>
        <svta:Click clickThroughUrl="https://advertiser-d.example.com/"/>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

Inside a candidate the children follow the order of §5.2.2: the options,
then the callback stream, then `<svta:Click>`. Candidate k2 carries a
`<svta:Click>` with no `<svta:ClickTracking>`; that is complete, and on
activation the Player opens the destination and fires nothing (§5.6.1).

### K.5 Player walk-through

**Linear.** The mid-roll runs from 300 s for 20 s. The viewer activates
the ad 6 s in.

| Ad time | What fires | Why |
|---|---|---|
| 0 s | `imp` | callback, `presentationTime="0"` |
| 6 s (activation) | `click?ad=l1` and `c?id=l1`, once each; `advertiser-b` opened or handed to the platform | `<svta:Click>` (§4.5.15) |
| 10 s | `mid` | callback |
| 20 s | `complete` | callback |

The callback beacons keep their schedule on the ad's timeline; the
activation adds two requests at the moment it happens and moves none of
the scheduled ones. What the Player does with the ad itself while the
destination is open is not specified here.

**Non-linear.** The slot runs from 900 s: k1 for 10 s, then k2 for
10 s, a cumulative 20000 against the cap of 20000, admitted. The viewer
activates k1 at 4 s: `click?ad=k1` fires once and `advertiser-c` is
opened. The viewer activates k2 at 914 s: `advertiser-d` is opened and no
request fires.

**No activation.** If the viewer never acts, no click-tracking URL
fires, while every callback beacon still fires at its time.

| | Callback beacon | Click-tracking |
|---|---|---|
| Carrier | `<EventStream>` of `urn:mpeg:dash:event:callback:2015`, URL as `<Event>` text (§5.5) | `<svta:ClickTracking>` inside `<svta:Click>`, URL as element text (§5.6) |
| Trigger | the scheduled time, relative to the ad's start | the viewer's activation |
| Fires if the viewer never acts | yes | no |
| Fired by a Player that does not implement this specification | on a List MPD Period, as that Player handles base callback events; inside a candidate, never | never |

### K.6 A Player that does not implement this specification

- **Linear.** It plays the `<ImportedMPD>` video of the List MPD Period
  as the base specification defines, and removes the `svta:` children
  as extension content (§4.7.4). The ad plays and its ClickThrough is
  inert: an activation does nothing.
- **Non-linear.** It does not recognise the overlay scheme, never
  requests the overlay document, and presents no overlay (§4.7.1).
  There is nothing to click.

The primary content plays in both cases.

### K.7 Device classes

What an activation does is the same on every device class; the class
decides only whether an ad is on screen to be activated. The input is
the device's own (remote select, tap).

| Class | Linear ad | Overlay slot | Activation of a rendered ad |
|---|---|---|---|
| D1 | rendered | k1 HTML lower-third, then k2 | opens the destination, fires every click-tracking URL once |
| D2 | rendered | skipped: neither HTML nor image is satisfiable | same, on the linear ad |
| D3 | rendered | k1 HTML lower-third, then k2 | same |
| D4 | rendered | k1 image corner (HTML not satisfiable), then k2 | same |
| D5 | rendered | skipped | same, on the linear ad |

---

## Annex L — Overlapping windows of one family, with fallback

*This annex is informative.*

### L.1 Scenario

A Publisher declares three overlay windows over the same stretch of an
on-demand programme, each pointing at a different APS. Overlap is the
declaration of a fallback chain (§5.1.5): the windows are not three
concurrent opportunities. The Player attempts the first; when that
attempt produces an ad, the others are not touched; when it produces
none, the next is attempted; when every window has failed, the primary
content continues (§4.5.6).

Each window binds what it serves with its own declarations — allowed
layouts and cap — never with those of the window it stands in for
(§4.5.7). The three windows declare different ones on purpose.

### L.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static" minBufferTime="PT2S"
     mediaPresentationDuration="PT48M">
  <BaseURL>https://cdn.publisher.example.com/match-12/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
                 timescale="1000">
      <Event id="701" presentationTime="900000" duration="60000">
        <svta:OverlayPresentation uri="https://aps-a.example.com/decision/overlay"
                                  maxDuration="30000"
                                  allowedLayouts="squeezeback-l-shape-upper-left overlay-lower-third"/>
      </Event>
      <Event id="702" presentationTime="900000" duration="60000">
        <svta:OverlayPresentation uri="https://aps-b.example.com/decision/overlay"
                                  maxDuration="20000"
                                  allowedLayouts="overlay-lower-third linear"/>
      </Event>
      <Event id="703" presentationTime="905000" duration="55000">
        <svta:OverlayPresentation uri="https://aps-c.example.com/decision/overlay"
                                  maxDuration="15000"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" codecs="avc1.640028" bandwidth="6000000"
                      width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true">
      <SegmentTemplate timescale="48000" duration="192000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" codecs="mp4a.40.2" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

All three windows are `<Event>` entries of one stream, with no `@value`
(§5.1.5). Two sibling streams of the overlay scheme in this Period would
not form a conformant document.

### L.3 Order of the chain

The Player orders overlapping windows by presentation time, oldest
first, and breaks equal times by position in the stream (§4.5.6 item 1):

| Position in chain | Window | `@presentationTime` | Why here |
|---|---|---|---|
| 1 | 701 | 900000 | earliest time; first in the stream among equals |
| 2 | 702 | 900000 | same time as 701, later position |
| 3 | 703 | 905000 | later time |

None declares an offset, so each may be resolved from 60 s before its
start: 840 s for 701 and 702, 845 s for 703. The requests forward what
each window declares (§5.8.3):

```
GET https://aps-a.example.com/decision/overlay?sgaiAllowedLayouts=squeezeback-l-shape-upper-left%20overlay-lower-third
GET https://aps-b.example.com/decision/overlay?sgaiAllowedLayouts=overlay-lower-third%20linear
GET https://aps-c.example.com/decision/overlay
```

Window 703 declares no `@allowedLayouts`; its request carries none, and
the overlay family default binds its options (§3.4.3).

### L.4 The three paths

| Path | 701 | 702 | 703 | Result |
|---|---|---|---|---|
| 1 | empty resolution: failed execution | document with ads (L.5) | not attempted | 702's ads, validated against 702 |
| 2 | empty resolution | empty resolution | empty resolution | primary content, uninterrupted |
| 3 | no response | no response | no response | primary content, uninterrupted |

On path 2 each APS answers `200` with the empty document of §5.2.3:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay"/>
  </Period>
</MPD>
```

On path 3 no document is obtained at all, so no candidate is ever
accepted, and the Player continues with the primary content with no
visible artefact and no beacon fired (§4.5.16 item 3). From the Player's
side, path 1 is indistinguishable from one where 701 could not be
reached: both are failed executions of 701 (§4.5.6 item 3).

**Variants of the first attempt.** Each of the following is a failed
execution of 701, and each leads to 702 exactly as the empty resolution
does:

| 701 answers | Base condition it maps to (§4.5.6 table) |
|---|---|
| `503 Service Unavailable` | nothing was obtained |
| `200` with an HTML error page, or with a truncated MPD | invalid: the body cannot be parsed or validated |
| `200` with the empty document above | the merge left no available media |
| `200` with a pause document (below) | a document that cannot fill the slot |

The wrong-family document is well formed, valid, and carries a
renderable candidate. The Player recognises it by `@family` before it
looks at any candidate (§4.5.2 item 2), and presents none of them:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="pause" onCandidatesExhausted="stop">
      <svta:Candidate id="x1">
        <svta:RenderableAsset form="image" layout="pause-partial"
                              duration="PT10S"
                              assetUrl="https://ads.example.com/creatives/x1/pause.png"/>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

### L.5 The fallback window's document

Window 702 answers path 1 with:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T21:30:00Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay" dismissAfter="PT5S">
      <svta:Candidate id="b1">
        <svta:RenderableAsset form="image" layout="squeezeback-l-shape-upper-left"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/creatives/b1/underlay.png"/>
        <svta:RenderableAsset form="image" layout="overlay-lower-third"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/creatives/b1/lt.png"/>
        <svta:RenderableAsset form="video" layout="linear"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/creatives/b1/b1.mpd"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=b1</Event>
          <Event id="2" presentationTime="15000">https://tracker.example.com/complete?ad=b1</Event>
        </EventStream>
      </svta:Candidate>
      <svta:Candidate id="b2">
        <svta:RenderableAsset form="image" layout="overlay-lower-third"
                              duration="PT10S"
                              assetUrl="https://ads.example.com/creatives/b2/lt.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event id="1" presentationTime="0">https://tracker.example.com/imp?ad=b2</Event>
          <Event id="2" presentationTime="10000">https://tracker.example.com/complete?ad=b2</Event>
        </EventStream>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

The first option of b1 is a squeezeback, which 702 does not admit. It
is outside the set the request forwarded, so emitting it falls short
of §4.4 item 6; the Player rejects it whatever the APS did (§4.5.3
item 2).

Sub-MPD of b1's takeover:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://ads.example.com/creatives/b1/</BaseURL>
  <Period id="b1" duration="PT15S">
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="v/$RepresentationID$/init.mp4"
                       media="v/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" codecs="avc1.640028" bandwidth="5000000"
                      width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true">
      <SegmentTemplate timescale="48000" duration="144000" startNumber="1"
                       initialization="a/$RepresentationID$/init.mp4"
                       media="a/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" codecs="mp4a.40.2" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### L.6 Which options pass, per window and device class

The Player checks each option against the device (§5.3.7) and against
the window that served it. Under 702 the allowed layouts are
`overlay-lower-third linear`:

| Class | b1 option 1 (image squeezeback) | b1 option 2 (image lower-third) | b1 option 3 (video `linear`) | b1 renders | b2 (image lower-third) |
|---|---|---|---|---|---|
| D1 | fails the window | passes | — | option 2 | passes |
| D2 | fails the window | fails the device | passes | option 3, takeover | fails the device: skipped |
| D3 | fails the window | passes | — | option 2 | passes |
| D4 | fails the window | passes | — | option 2 | passes |
| D5 | fails the window | fails the device | passes | option 3, takeover | fails the device: skipped |

**Cap arithmetic under 702** (`maxDuration="20000"`, `timescale="1000"`):

| Class | b1 | b2 | Cumulative declared | Outcome |
|---|---|---|---|---|
| D1, D3, D4 | 15000 | 10000 | 25000 > 20000 | b2 dropped before play, or trimmed 5 s into b2 with `complete` not fired (§4.5.4, §4.5.13 item 2) |
| D2, D5 | 15000 | skipped | 15000 | b1 only |

**The same document, had 701 served it.** 701 admits
`squeezeback-l-shape-upper-left overlay-lower-third` and caps at 30000:

| Class | b1 | b2 | Cumulative |
|---|---|---|---|
| D1, D3, D4 | option 1, image squeezeback | passes | 25000 ≤ 30000: both play in full |
| D2, D5 | skipped: options 1 and 2 fail the device, option 3 fails the window (`linear` not listed) | skipped | none |

The document is identical in both tables; the results differ only
because the declarations belong to the window that served it (§4.5.7).

### L.7 Candidates that are not renderable end at the primary content

On a D2 device, 701 answers with a document of the right family whose
options are all image or HTML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay">
      <svta:Candidate id="u1">
        <svta:RenderableAsset form="html" layout="squeezeback-l-shape-upper-left"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/creatives/u1/underlay.html"/>
        <svta:RenderableAsset form="image" layout="overlay-lower-third"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/creatives/u1/lt.png"/>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

This is not a failed execution: the document carries candidates of the
right family (§4.5.6 item 4). On D2 both options fail the device, u1 is
skipped, the candidates are exhausted, and the Player continues with
the primary content (§4.5.3 item 3). **It does not attempt 702**, even
though 702 would have offered D2 a takeover. The base condition is
media availability after the merge, not renderability on one device.
On D1, D3 and D4 the same document renders u1 (D1 and D3 the HTML
squeezeback, D4 the image lower-third). On D5 it ends as on D2.

### L.8 Device classes

Window selection is the same on every device class: which window is
served depends on what each attempt returned, never on the device
(§7.8). The class decides only what renders from the served window, as
L.6 and L.7 show.

---

## Annex M — One ad, Player-declared capabilities, resolved by the APS

*This annex is informative.*

### M.1 The scenario

The ad, its four options and the window are those of Annex I. The
decision the APS obtains from the ADS carries, in this order:

1. `squeezeback-double-box-background`, a video ad with a background image;
2. `squeezeback-l-shape-upper-left`, a full-frame image creative;
3. `overlay-lower-third`, an image banner;
4. `linear`, a full-screen video takeover.

What differs from Annex I is where the capability check is resolved. Each
Player attaches the capability parameters it chooses to send (§5.8.2),
and this APS uses them to narrow (§4.4 item 14): it removes every option
the declared values rule out under §5.3.7 and emits the first survivor
alone. When the request carries no capability parameter it narrows
nothing and emits all four (§5.8.4). An axis the request omits is
undetermined, and this APS resolves an undetermined axis conservatively:
it emits no option whose satisfiability depends on it.

### M.2 The main MPD

Identical to Annex I; repeated so that this annex reads on its own.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static"
     mediaPresentationDuration="PT45M"
     minBufferTime="PT2S">
  <Period id="main" start="PT0S">

    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
                 timescale="1000">
      <Event id="401" presentationTime="600000" duration="60000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/overlay"
            maxDuration="15000"
            allowedLayouts="squeezeback-double-box-background squeezeback-l-shape-upper-left overlay-lower-third linear"
            earliestResolutionTimeOffset="20000"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="https://cdn.example.com/programme/video/init.mp4"
                       media="https://cdn.example.com/programme/video/seg-$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="https://cdn.example.com/programme/audio/init.mp4"
                       media="https://cdn.example.com/programme/audio/seg-$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The window runs from 600 s to 660 s, resolves no earlier than
600 000 − 20 000 = 580 000 (580 s), and caps the slot at 15 000 units
(15 s).

### M.3 The five requests

The window declares `@allowedLayouts`, so **every** request carries
`sgaiAllowedLayouts`, including the one that declares nothing about the
device: it is the Publisher's declaration, not the Player's, and its
forwarding is not optional (§5.8.3). Let `L` stand for its value:

```
L = squeezeback-double-box-background%20squeezeback-l-shape-upper-left%20overlay-lower-third%20linear
```

```
D1  GET /decision/overlay?sgaiAllowedLayouts=L&sgaiVideoDecoders=2&sgaiImageOverlay=true&sgaiHtmlOverlay=true
D2  GET /decision/overlay?sgaiAllowedLayouts=L&sgaiVideoDecoders=2&sgaiImageOverlay=false&sgaiHtmlOverlay=false
D3  GET /decision/overlay?sgaiAllowedLayouts=L&sgaiVideoDecoders=1&sgaiImageOverlay=true
D4  GET /decision/overlay?sgaiAllowedLayouts=L
D5  GET /decision/overlay?sgaiAllowedLayouts=L&sgaiVideoDecoders=1&sgaiImageOverlay=false&sgaiHtmlOverlay=false
```

D3 does not know, when it issues the request, whether its HTML surface
will be available, so it omits `sgaiHtmlOverlay` entirely rather than
sending it empty (§5.8.4). D4 sends no capability parameter, which is
equally conformant.

### M.4 What the APS derives

What each option depends on, read off §5.3.7:

| Option | Needs |
|---|---|
| 1 | `sgaiVideoDecoders` ≥ 2 **and** `sgaiImageOverlay=true` |
| 2 | `sgaiImageOverlay=true` |
| 3 | `sgaiImageOverlay=true` |
| 4 | nothing beyond one decoder |

| Request | Option 1 | Option 2 | Option 3 | Option 4 | Emits |
|---|---|---|---|---|---|
| D1 | survives | survives | survives | survives | option 1 alone |
| D2 | ruled out: no image surface | ruled out | ruled out | survives | option 4 alone |
| D3 | ruled out: one decoder | survives | survives | survives | option 2 alone |
| D4 | not narrowed | not narrowed | not narrowed | not narrowed | all four, in order |
| D5 | ruled out | ruled out | ruled out | survives | option 4 alone |

On D3 the undetermined HTML axis rules nothing out, because no option
ahead of the survivor is HTML.

### M.5 The resolution documents

The D4 document, which carries all four options, is the document of
Annex I:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T12:09:41Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay">
      <svta:Candidate id="c1">

        <svta:RenderableAsset form="video"
                              layout="squeezeback-double-box-background"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/dbox.mpd"
                              backgroundUrl="https://ads.example.com/c1/background.jpg"/>
        <svta:RenderableAsset form="image"
                              layout="squeezeback-l-shape-upper-left"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/lshape.jpg"/>
        <svta:RenderableAsset form="image"
                              layout="overlay-lower-third"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/banner.png"/>
        <svta:RenderableAsset form="video"
                              layout="linear"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/takeover.mpd"/>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0">https://tracker.example.com/impression?ad=c1</Event>
          <Event presentationTime="7500">https://tracker.example.com/mid?ad=c1</Event>
          <Event presentationTime="15000">https://tracker.example.com/complete?ad=c1</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://advertiser.example.com/landing">
          <svta:ClickTracking>https://tracker.example.com/click?ad=c1</svta:ClickTracking>
        </svta:Click>

      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

The other four documents differ only in the `<svta:OverlayList>`. The
MPD root, the Period, and the candidate's `<EventStream>` and
`<svta:Click>` are as above, elided here.

D1:

```xml
<svta:OverlayList xmlns:svta="urn:svta:dash:sgai:2026" family="overlay">
  <svta:Candidate id="c1">
    <svta:RenderableAsset form="video"
                          layout="squeezeback-double-box-background"
                          duration="PT15S"
                          assetUrl="https://ads.example.com/c1/dbox.mpd"
                          backgroundUrl="https://ads.example.com/c1/background.jpg"/>
    <!-- callback EventStream and svta:Click as in the D4 document -->
  </svta:Candidate>
</svta:OverlayList>
```

D2 and D5 (the same list):

```xml
<svta:OverlayList xmlns:svta="urn:svta:dash:sgai:2026" family="overlay">
  <svta:Candidate id="c1">
    <svta:RenderableAsset form="video" layout="linear" duration="PT15S"
                          assetUrl="https://ads.example.com/c1/takeover.mpd"/>
    <!-- callback EventStream and svta:Click as in the D4 document -->
  </svta:Candidate>
</svta:OverlayList>
```

D3:

```xml
<svta:OverlayList xmlns:svta="urn:svta:dash:sgai:2026" family="overlay">
  <svta:Candidate id="c1">
    <svta:RenderableAsset form="image"
                          layout="squeezeback-l-shape-upper-left"
                          duration="PT15S"
                          assetUrl="https://ads.example.com/c1/lshape.jpg"/>
    <!-- callback EventStream and svta:Click as in the D4 document -->
  </svta:Candidate>
</svta:OverlayList>
```

A candidate carrying one option is conformant (§5.3.4), and nothing in
it records that the APS narrowed (§8.13). Every option keeps `PT15S`,
which converts to 15 000 units and equals the cap, so it is admitted
(§4.5.4 item 4).

### M.6 The sub-MPDs

`https://ads.example.com/c1/dbox.mpd`, the 960 × 540 ad box of option 1:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S">
  <Period id="1" duration="PT15S">
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="https://ads.example.com/c1/dbox/init.mp4"
                       media="https://ads.example.com/c1/dbox/seg-$Number$.m4s"/>
      <Representation id="v540" bandwidth="2500000" width="960" height="540"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="https://ads.example.com/c1/dbox/audio-init.mp4"
                       media="https://ads.example.com/c1/dbox/audio-$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

`https://ads.example.com/c1/takeover.mpd`, the full-frame takeover of
option 4:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S">
  <Period id="1" duration="PT15S">
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="https://ads.example.com/c1/takeover/init.mp4"
                       media="https://ads.example.com/c1/takeover/seg-$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="https://ads.example.com/c1/takeover/audio-init.mp4"
                       media="https://ads.example.com/c1/takeover/audio-$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### M.7 The Player's check per device class

Each Player checks what it received against its own device and the
window's allowed layouts before rendering (§4.5.3), whatever the APS
derived.

| Class | Options received | Device check | Window check | Renders | Same as Annex I |
|---|---|---|---|---|---|
| D1 | 1 | passes | passes | 1: double box with background | yes |
| D2 | 4 | passes | passes | 4: takeover | yes |
| D3 | 2 | passes | passes | 2: L-shape | yes |
| D4 | 1, 2, 3, 4 | 1 fails (one decoder); 2 passes | passes | 2: L-shape | yes |
| D5 | 4 | passes | passes | 4: takeover | yes |

D4 is the Annex I case exactly: a Player that declares nothing leaves
the APS unable to narrow, and the APS emits the full ordered list.

### M.8 What the scenario shows

- **Declaring does not delegate the Player's check.** The option the
  APS derived from the Player's own declaration is still checked
  (§4.5.3 item 2, §8.7). If D1's image surface is unavailable when the
  window fires — the device's state changed after the request — its one
  option fails, the candidate is skipped, and the primary content
  continues. That is a candidate-level skip, not a failed execution of
  the window (§4.5.6 item 4). Emitting a single option buys that risk:
  had the APS kept the takeover after option 1, as §8.7 recommends for
  an APS that narrows, the same D1 would have landed on the takeover.
- **A single option does not require a declaration.** An APS MAY emit
  one option per candidate whether or not the request carried anything
  (§4.4 item 14). The declaration changes the basis on which the APS
  chose the option, not what the Player does with it.
- **The policy for an undetermined axis is the APS's** (§5.8.4). In
  this scenario the conservative policy and a most-capable policy emit
  the same option to D3, because nothing ahead of option 2 depends on
  the HTML axis. They diverge when an option that depends on the
  undetermined axis precedes the survivor: had option 2 been an HTML
  L-shape, the conservative APS would emit option 3 and a most-capable
  APS option 2, both conformant. The Player checks whichever arrives.
- **The outcome per class equals Annex I's.** What moved is which actor
  selected among the options, not what the viewer sees.

---

## Annex N — A non-linear ad over a replacement that is not advertising

*This annex is informative.*

### N.1 Scenario

A live channel blacks out a two-minute span of its programme in one
region. The Publisher replaces that span with its own slate, which has
its own audio. It also declares an overlay window over part of the same
span. The replacement carries no advertising. The overlay does.

**This specification does not specify blackouts.** How a Publisher
decides to black out, what the slate shows and how rights are enforced
are all outside it. The case is here because the base specification's
replacement tool is not an advertising mechanism: it names blackouts
among its applications (DASH §5.16.1, §8.13.1). The case is the clearest
demonstration that the surface underneath a non-linear ad need not be an
ad. The replacement is authored with the base construct, and resolves to
a List MPD that the Publisher serves from its own endpoint. No ADS, no
APS and no ad candidate take part in it.

### N.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="dynamic"
     availabilityStartTime="2026-09-25T18:00:00Z"
     publishTime="2026-09-25T18:59:00Z"
     minimumUpdatePeriod="PT10S"
     timeShiftBufferDepth="PT5M"
     maxSegmentDuration="PT2S"
     minBufferTime="PT2S">
  <BaseURL>https://live.publisher.example.com/channel-7/region-3/</BaseURL>
  <Period id="p0" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
                 timescale="1000">
      <Event id="70" presentationTime="3600000" duration="120000">
        <ReplacePresentation uri="https://publisher.example.com/blackout/region-3/slate-list.mpd"
                             maxDuration="120000"
                             skipAfter="PT120S"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
                 timescale="1000">
      <Event id="270" presentationTime="3630000" duration="60000">
        <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay?slot=270"
                                  maxDuration="20000"
                                  allowedLayouts="overlay-lower-third overlay-corner"/>
      </Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="0"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" codecs="avc1.640028"
                      width="1920" height="1080" frameRate="50"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="0"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" codecs="mp4a.40.2"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The replacement declares `@maxDuration` because every linear event under
this specification does. Without one, the event would not be executed
(§4.5.1 item 7; §4.8.3). On a replacement the cap bounds *until when*
the presentation runs (§4.5.4). Here that means the slate ends by
3720.000 s, whatever it depicts.

### N.3 The two resolutions

```
GET /blackout/region-3/slate-list.mpd
Host: publisher.example.com

GET /decision/overlay?slot=270&sgaiAllowedLayouts=overlay-lower-third%20overlay-corner
Host: aps.example.com
```

The first request goes to the Publisher's own server, and the base
execution model governs it as it governs any alternative-MPD request
(§4.5.1 item 1). The second is an ordinary overlay resolution request.

**The slate's List MPD**, served by the Publisher:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list" minBufferTime="PT1S">
  <Period id="slate-region-3" duration="PT120S">
    <ImportedMPD>https://cdn.publisher.example.com/slates/regional-blackout.mpd</ImportedMPD>
  </Period>
</MPD>
```

It carries no callback stream, no `svta:Click` and no metadata, because
it is not an ad.

**The overlay resolution document**, from the APS:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static" minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T18:59:20Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay" dismissAfter="PT0S">
      <svta:Candidate id="n-6021">
        <svta:RenderableAsset form="html" layout="overlay-lower-third"
            duration="PT20S"
            assetUrl="https://ads.example.com/creatives/n-6021/lower-third.html"/>
        <svta:RenderableAsset form="image" layout="overlay-corner"
            duration="PT20S"
            assetUrl="https://ads.example.com/creatives/n-6021/corner.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0">https://tracker.example.com/imp?ad=n-6021</Event>
          <Event presentationTime="10000">https://tracker.example.com/mid?ad=n-6021</Event>
          <Event presentationTime="20000">https://tracker.example.com/done?ad=n-6021</Event>
        </EventStream>
        <svta:Click clickThroughUrl="https://advertiser.example.com/landing">
          <svta:ClickTracking>https://tracker.example.com/click?ad=n-6021</svta:ClickTracking>
        </svta:Click>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

`dismissAfter="PT0S"` makes the overlay slot dismissible from its first
rendered frame (§5.2.4). Dismissing it removes the overlay only. The
slate is a different window of a different family, and it keeps
playing.

### N.4 The slate's sub-MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static" minBufferTime="PT2S">
  <BaseURL>https://cdn.publisher.example.com/slates/regional-blackout/</BaseURL>
  <Period id="slate" duration="PT120S">
    <AdaptationSet contentType="video" mimeType="video/mp4"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="v/$RepresentationID$/init.mp4"
                       media="v/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="2000000" codecs="avc1.640028"
                      width="1920" height="1080" frameRate="50"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" lang="en"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="a/$RepresentationID$/init.mp4"
                       media="a/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" codecs="mp4a.40.2"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The overlay's options are HTML and image, so the overlay has no sub-MPD.

### N.5 What each portion carries

| | Replacement (slate) | Overlay |
|---|---|---|
| Resolved against | the Publisher's own endpoint | the APS |
| Document | List MPD | non-linear resolution document, `family="overlay"` |
| Tracking | none | callback stream in the candidate |
| ClickThrough | none | `svta:Click` |
| `@maxDuration` | `120000`: until when the slate runs | `20000`: how long the ad slot presents |
| Dismissal | the event's `@skipAfter` with its base meaning (§5.2.4); `PT120S` equals the span, so no skip is offered within it | `dismissAfter="PT0S"` |

Only the overlay is an ad. What the two portions share is the screen,
not the contract.

### N.6 The budget, and the walk per device class

**The budget is the hybrid break's (§7.5).** During any alternative
presentation one access engine outputs media, and the main client *"will
be paused or be in a listen mode"* (DASH §4.2). The slate therefore
occupies the decoder the primary content released, exactly as a linear
ad would. A Player cannot observe whether the video it decodes is an
advertisement, a slate or the programme. The rule of §5.3.7 counts
decoders and surface types and nothing else, and it gives the same
answer.

The slate plays on every class, since `linear` with `video` is
satisfiable on D1 to D5. Both overlay options are admitted by the
window, so only the device check decides:

| # | Form, layout | Cost on top of the slate | Satisfiable on |
|---|---|---|---|
| 1 | `html`, `overlay-lower-third` | an HTML surface | D1, D3 |
| 2 | `image`, `overlay-corner` | an image surface | D1, D3, D4 |

- **D1** accepts option 1 and composites the HTML lower-third over the
  slate.
- **D2** declines both options, because it composites no image or HTML
  over video. The slate plays alone. A `video` overlay option, had the
  candidate offered one, would composite on D2's second decoder, as in
  Annex D.
- **D3** accepts option 1: one decoder for the slate plus an HTML
  surface.
- **D4** declines option 1 because it renders no HTML over video. It
  accepts option 2, compositing the image in a corner over the slate.
- **D5** declines both options, and the slate plays alone.

For D2 and D5 the candidate is skipped. That is not a failed execution
of the overlay window (§4.5.6 item 4), and no overlay beacon fires.

**Walk at a glance:**

| Class | Decoders in use | Surfaces in use | Under | Overlay |
|---|---|---|---|---|
| D1 | 1 | HTML | slate | option 1, HTML lower third |
| D2 | 1 | none | slate | none |
| D3 | 1 | HTML | slate | option 1, HTML lower third |
| D4 | 1 | image | slate | option 2, image corner |
| D5 | 1 | none | slate | none |

Row for row, this is the hybrid row of §3.6, with the slate in the place
of the linear ad.

### N.7 Timing and cap arithmetic

All values are in `timescale="1000"`, relative to the Period start.

| Quantity | Computation | Value |
|---|---|---|
| Slate switch (PRT) | `presentationTime` | 3600.000 s |
| Slate end, `@clip="true"` (default) | at the latest `3600000 + 120000` | 3720.000 s |
| Slate media | `PT120S` → `120000` | fills the span exactly |
| Overlay window | `3630000` + `60000` | 3630.000 s to 3690.000 s, inside the slate span |
| Overlay earliest resolution | `3630000 − 60000` (default offset) | 3570.000 s, before the blackout begins |
| `n-6021` | `PT20S` → `20000` against `maxDuration="20000"` | equal, so admitted; on screen 3630.000 s to 3650.000 s |

The overlay window lies on the primary timeline, and that timeline keeps
advancing while the slate plays. On a replacement *"the main Media
Presentation is not being output, but its media time progresses at the
same speed as the currently playing alternative Media Presentation"*
(DASH §5.16.1). The overlay therefore starts at 3630.000 s of the
primary timeline, which is 30 s into the slate. For the same reason, the
20 seconds the overlay cap measures are the same 20 seconds whether they
are counted on the slate's timeline or on the primary one.

Suppose the viewer dismisses the overlay at 3635 s. The overlay slot
ends, and the `mid` and `done` beacons do not fire (§4.5.14). The slate
continues to 3720.000 s, after which the primary content resumes as the
base return rules of DASH §5.16.4 determine.

---

## Annex O — Publisher-restricted layouts forwarded to the APS

*This annex is informative.*

### O.1 The scenario

The Publisher admits only two layouts on an overlay window,
`overlay-lower-third` and `squeezeback-l-shape-upper-left`: on this slot
it wants the primary content neither halved by a double box nor
interrupted by a takeover. The Player forwards that set on the
resolution request (§5.8.3), next to the capability parameters it
declares (§5.8.2).

The ADS decides the same ad as Annex I, with four options in this order:

1. `squeezeback-double-box-background`, a video ad with a background image;
2. `squeezeback-l-shape-upper-left`, a full-frame image creative;
3. `overlay-lower-third`, an image banner;
4. `linear`, a full-screen video takeover.

The APS removes every option whose layout is outside the forwarded set
(§4.4 item 6), then the ones the declared capabilities rule out (§4.4
item 14), and emits the survivors in the decision's order (§4.4 item 5).
The Player checks what arrives before rendering it (§4.5.3).

### O.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static"
     mediaPresentationDuration="PT45M"
     minBufferTime="PT2S">
  <Period id="main" start="PT0S">

    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
                 timescale="1000">
      <Event id="501" presentationTime="1200000" duration="30000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/overlay"
            maxDuration="15000"
            allowedLayouts="overlay-lower-third squeezeback-l-shape-upper-left"
            earliestResolutionTimeOffset="20000"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="https://cdn.example.com/programme/video/init.mp4"
                       media="https://cdn.example.com/programme/video/seg-$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="https://cdn.example.com/programme/audio/init.mp4"
                       media="https://cdn.example.com/programme/audio/seg-$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The window runs from 1200 s to 1230 s, resolves no earlier than
1 200 000 − 20 000 = 1 180 000 (1180 s), and caps the slot at 15 000
units (15 s). `@allowedLayouts` is a set: the order in which the
Publisher wrote the two tokens expresses no preference.

### O.3 The requests

Each class declares its full capability set (§5.8.2). Let `L` stand for
the forwarded value, the attribute with each space as `%20`:

```
L = overlay-lower-third%20squeezeback-l-shape-upper-left
```

```
D1  GET /decision/overlay?sgaiAllowedLayouts=L&sgaiVideoDecoders=2&sgaiImageOverlay=true&sgaiHtmlOverlay=true
D2  GET /decision/overlay?sgaiAllowedLayouts=L&sgaiVideoDecoders=2&sgaiImageOverlay=false&sgaiHtmlOverlay=false
D3  GET /decision/overlay?sgaiAllowedLayouts=L&sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=true
D4  GET /decision/overlay?sgaiAllowedLayouts=L&sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=false
D5  GET /decision/overlay?sgaiAllowedLayouts=L&sgaiVideoDecoders=1&sgaiImageOverlay=false&sgaiHtmlOverlay=false
```

### O.4 What the APS derives

| Option | Removed by the forwarded set | Needs (§5.3.7) |
|---|---|---|
| 1 double box with background | yes: token not in `L` | — |
| 2 L-shape, image | no | an image surface |
| 3 lower third, image | no | an image surface |
| 4 takeover, video | yes: token not in `L` | — |

| Request | Survivors | Emits |
|---|---|---|
| D1, D3, D4 | 2, 3 | one candidate, options 2 then 3 |
| D2, D5 | none | the empty resolution |

### O.5 The resolution documents

D1, D3 and D4 receive the same document. The survivors keep the order
the decision gave them, so the L-shape comes first although the
Publisher wrote the lower third first in its set.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T12:19:41Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay">
      <svta:Candidate id="c1">
        <svta:RenderableAsset form="image"
                              layout="squeezeback-l-shape-upper-left"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/lshape.jpg"/>
        <svta:RenderableAsset form="image"
                              layout="overlay-lower-third"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/banner.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0">https://tracker.example.com/impression?ad=c1</Event>
          <Event presentationTime="15000">https://tracker.example.com/complete?ad=c1</Event>
        </EventStream>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

Both options are images, so no sub-MPD is fetched. `PT15S` converts to
15 000 units and equals the cap, so it is admitted (§4.5.4 item 4); the
slot ends at 1215 s, before the window's end at 1230 s.

D2 and D5 receive the empty resolution (§5.2.3):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay"/>
  </Period>
</MPD>
```

### O.6 The walk per device class

| Class | Received | Option 2: device / window | Option 3 | Outcome |
|---|---|---|---|---|
| D1 | options 2, 3 | passes / passes | — | L-shape |
| D2 | empty resolution | — | — | failed execution; no other window overlaps; primary content continues |
| D3 | options 2, 3 | passes / passes | — | L-shape |
| D4 | options 2, 3 | passes / passes | — | L-shape |
| D5 | empty resolution | — | — | as D2 |

- **D1, D3, D4** render the L-shape: the primary content shrunk into the
  upper-left 60 % of the frame, composited over the full-frame image
  creative. The APS already emitted only allowed layouts; the Player
  checks the option against the window's set anyway (§4.5.3 item 2).
- **D2 and D5** get no ad. The empty resolution is a failed execution:
  the Player attempts the next overlapping overlay window, finds none,
  and continues the primary content (§4.5.6). Nothing is consumed. The
  takeover both classes could have played is never offered, because the
  Publisher excluded it, and the screen is the Publisher's (§1.2).

Had D2 declared nothing, the APS would have sent options 2 and 3, D2
would have failed both on the device check and skipped the candidate —
the same viewer outcome, reached as a candidate-level skip instead of a
failed execution (§8.2).

### O.7 A non-conforming APS

An APS that ignores the forwarded set returns the decision unfiltered,
takeover first:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T12:19:41Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay">
      <svta:Candidate id="c1">
        <svta:RenderableAsset form="video"
                              layout="linear"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/takeover.mpd"/>
        <svta:RenderableAsset form="image"
                              layout="squeezeback-l-shape-upper-left"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/lshape.jpg"/>
        <svta:RenderableAsset form="image"
                              layout="overlay-lower-third"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/banner.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0">https://tracker.example.com/impression?ad=c1</Event>
          <Event presentationTime="15000">https://tracker.example.com/complete?ad=c1</Event>
        </EventStream>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

The takeover's sub-MPD, `https://ads.example.com/c1/takeover.mpd`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S">
  <Period id="1" duration="PT15S">
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="https://ads.example.com/c1/takeover/init.mp4"
                       media="https://ads.example.com/c1/takeover/seg-$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="https://ads.example.com/c1/takeover/audio-init.mp4"
                       media="https://ads.example.com/c1/takeover/audio-$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The document validates: `linear` is admissible on an overlay document
(§5.3.3), and whether an option lies within the window's set is not a
property of the document alone (§4.6). It is the APS that is
non-conformant, for emitting a layout the request told it the
Publisher excludes (§4.4 item 6). The Player's runtime check is what
catches it:

| Class | Option takeover | Option L-shape | Option lower third | Renders |
|---|---|---|---|---|
| D1 | device passes; **window fails** | passes | — | L-shape |
| D2 | device passes; **window fails** | device fails | device fails | nothing: candidate skipped, primary content continues |
| D3 | device passes; **window fails** | passes | — | L-shape |
| D4 | device passes; **window fails** | passes | — | L-shape |
| D5 | device passes; **window fails** | device fails | device fails | nothing: as D2 |

The takeover is satisfiable on every class and rendered on none: it is
discarded without being rendered, and the Player moves to the next option
(§4.5.3). The viewer outcome matches the conforming case. Forwarding the
set moves the choice upstream; it does not move the check.

---

## Annex P — A `custom` overlay inside a Publisher region

*This annex is informative.*

### P.1 The scenario

An overlay window admits the `custom` layout and bounds where a custom
overlay may go: a region in the upper right of the viewport, where the
programme's own graphics never appear. It also admits
`overlay-lower-third`. The APS places the custom overlay by a rectangle
and offers a lower-third banner after it. The Player checks the
rectangle against the region before rendering.

**`custom` is optional for every actor** (§5.3.5). A Publisher, an APS
and a Player that do not support it are all conformant. That is why the
APS offers a fallback: one ordered list serves a Player that supports
`custom` and one that does not.

### P.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="static"
     mediaPresentationDuration="PT45M"
     minBufferTime="PT2S">
  <Period id="main" start="PT0S">

    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026"
                 timescale="1000">
      <Event id="601" presentationTime="900000" duration="30000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/custom"
            maxDuration="15000"
            allowedLayouts="custom overlay-lower-third"
            customRegion="60,5,35,30"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="https://cdn.example.com/programme/video/init.mp4"
                       media="https://cdn.example.com/programme/video/seg-$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="https://cdn.example.com/programme/audio/init.mp4"
                       media="https://cdn.example.com/programme/audio/seg-$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

| Quantity | Value |
|---|---|
| Window | 900 000 to 930 000 at timescale 1000: 900 s to 930 s |
| Earliest resolution time | no offset declared, so the default 60 s: 900 s − 60 s = 840 s (§4.5.1) |
| Cap | 15 000 units: 15 s |
| Region `60,5,35,30` | x 60 % to 95 %, y 5 % to 35 % of the video viewport; 60 + 35 = 95 ≤ 100 and 5 + 30 = 35 ≤ 100, so it is a rectangle (§5.3.5) |

`@customRegion` is admissible here because `@allowedLayouts` lists
`custom` (§4.2 item 7). The family default would not admit `custom`; a
window admits it only by listing it (§3.4.3).

### P.3 The request

The window declares both `@allowedLayouts` and `@customRegion`, so the
Player forwards both (§5.8.3). This Player sends no capability
parameter:

```
GET /decision/custom?sgaiAllowedLayouts=custom%20overlay-lower-third&sgaiCustomRegion=60,5,35,30
Host: aps.example.com
```

Every Player of this specification sends these two parameters,
including one that does not support `custom`: they carry the
Publisher's declarations, not the device's. No reserved parameter
states whether a Player supports `custom` (§5.8.2), so the APS cannot
tell the two kinds of Player apart, and the fallback option is what
serves the second.

### P.4 The resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:full:2011"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-25T12:14:30Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList family="overlay">
      <svta:Candidate id="c1">
        <svta:RenderableAsset form="image"
                              layout="custom"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/custom.png"
                              customRectangle="65,8,25,20"/>
        <svta:RenderableAsset form="image"
                              layout="overlay-lower-third"
                              duration="PT15S"
                              assetUrl="https://ads.example.com/c1/banner.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0">https://tracker.example.com/impression?ad=c1</Event>
          <Event presentationTime="7500">https://tracker.example.com/mid?ad=c1</Event>
          <Event presentationTime="15000">https://tracker.example.com/complete?ad=c1</Event>
        </EventStream>
        <svta:Click clickThroughUrl="https://advertiser.example.com/landing"/>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

`@customRectangle` appears on the `custom` option only (§5.3.1, §4.6
step 4). Both options are images, so there is no sub-MPD. `PT15S`
converts to 15 000 units, equal to the cap, and is admitted (§4.5.4
item 4); the slot runs from 900 s to 915 s.

### P.5 The containment check

The Player tests the four inequalities of §5.3.5 with the region
`xR,yR,widthR,heightR = 60,5,35,30` and the rectangle
`x,y,width,height = 65,8,25,20`:

| Test | Values | Holds |
|---|---|---|
| `xR ≤ x` | 60 ≤ 65 | yes |
| `yR ≤ y` | 5 ≤ 8 | yes |
| `x + width ≤ xR + widthR` | 65 + 25 = 90 ≤ 60 + 35 = 95 | yes |
| `y + height ≤ yR + heightR` | 8 + 20 = 28 ≤ 5 + 30 = 35 | yes |

The rectangle lies inside the region and is smaller than it, which is
permitted. On a 1920 × 1080 viewport it spans x 1248 to 1728 pixels and
y 86.4 to 302.4 pixels; the conversion is the Player's, and the
rectangle is declared only in percent.

### P.6 The walk

| Player | Option 1 `custom` image | Option 2 `overlay-lower-third` image | Renders |
|---|---|---|---|
| Supports `custom`; D1, D3 or D4 | device passes; window passes; contained | — | the custom overlay at `65,8,25,20` |
| Does not support `custom`; D1, D3 or D4 | not renderable (§4.5.3 item 4) | passes | the lower-third banner |
| D2 | fails: image surface | fails: image surface | nothing: candidate skipped, primary content continues |
| D5 | fails: no surface | fails: no surface | nothing: as D2 |

- The two D1/D3/D4 Players render different options from one document,
  and both are conformant.
- D2 and D5 skip the candidate; this is not a failed execution of the
  window, because the document carried a candidate of the right family
  (§4.5.6 item 4). The window admits no `linear`, so no takeover can
  reach D5 here.

### P.7 A rectangle outside the region

An APS returns the same candidate with the custom option placed at
`50,10,40,20`:

```xml
<svta:RenderableAsset xmlns:svta="urn:svta:dash:sgai:2026" form="image"
                      layout="custom"
                      duration="PT15S"
                      assetUrl="https://ads.example.com/c1/custom.png"
                      customRectangle="50,10,40,20"/>
```

| Test | Values | Holds |
|---|---|---|
| `xR ≤ x` | 60 ≤ 50 | **no** |
| `yR ≤ y` | 5 ≤ 10 | yes |
| `x + width ≤ xR + widthR` | 50 + 40 = 90 ≤ 95 | yes |
| `y + height ≤ yR + heightR` | 10 + 20 = 30 ≤ 35 | yes |

The rectangle is well-formed — 50 + 40 = 90 ≤ 100 and 10 + 20 = 30 ≤
100 — so the document still validates (§4.6 step 4). It ends inside the
region but starts 10 points to its left, so it is not contained. The
region is a property of the window, and containment is checked by the
Player at runtime (§4.6). The APS is non-conformant for emitting it
(§4.4 item 6).

A Player that supports `custom` discards the option without rendering
it and moves to option 2, the lower-third banner (§4.5.3 item 2). A
Player that does not support `custom` never reaches the rectangle and
renders option 2 as before. D2 and D5 are unaffected. No custom overlay
lands outside the region the Publisher declared.

---

## Annex Q — Test cases and conformance criteria

*This annex is informative. It summarises what an implementer can test
against; the obligations themselves are in chapters 4 to 7.*

### Q.1 How to read a test case

Each row names one observable property, the input that exercises it,
and the outcome that passes. An input is a main MPD, a resolution
document, a device class, and — where it matters — a viewer action.
Where a row passes by *not* doing something, the pass criterion names
the observation that shows it: a request log, a beacon log, a frame
capture.

A test that cannot fail tests nothing. Each Player row therefore comes
with its **control**: the same input with the one property changed, for
which the outcome must differ. A row whose outcome does not change when
its control is run has measured the harness, not the Player.

| Column | Meaning |
|---|---|
| ID | Stable identifier of the test |
| Section | The section whose obligation the test checks |
| Input | What is fed to the implementation under test |
| Pass | What is observed when the implementation conforms |
| Control | The variation for which the observation must differ |

### Q.2 Chapter 4 — conformance, per actor

#### Q.2.1 Publisher (checked against the main MPD)

| ID | Section | Input | Pass | Control |
|---|---|---|---|---|
| P-1 | §4.2 item 2 | Every slot of every family | Each carries `@maxDuration` | Remove one: the check reports that slot |
| P-2 | §4.2 item 3 | A main MPD with `MPD@type="dynamic"` | No `<InsertPresentation>` appears | Add one: reported |
| P-3 | §4.2 item 4 | Every overlay and pause window | `@id`, `@presentationTime`, `@duration` present | Remove `@duration`: reported |
| P-4 | §4.2 item 5 | Two windows of one family in one Period | Both in one `<EventStream>`, no `@value` | Split into two streams: reported |
| P-5 | §4.2 item 6 | Every `@allowedLayouts` | Tokens from §3.4.2, admissible for the family | Add `squeezeback` or a private name: reported |
| P-6 | §4.2 item 7 | Every `@customRegion` | Present only with `custom` listed; a valid rectangle | Region without `custom`: reported |
| P-7 | §4.2 item 10 | Content with pause windows | A `<Metrics metrics="PlayList">` on the main MPD | Remove it: reported |
| P-8 | §4.2 item 11 | The main MPD with the `svta:` namespace removed | Valid against the base schema | Nest a required base element inside an `svta:` element: removal leaves an invalid document |

#### Q.2.2 ADS

| ID | Section | Input | Pass | Control |
|---|---|---|---|---|
| A-1 | §4.3 | A decision whose ads exceed the slot cap in total | The ADS is not failed for it | — (a pass that does not depend on the cap) |
| A-2 | §4.3 | A decision carrying no ads | Accepted as a legitimate decision | — |

The ADS's decision document is not what this specification checks: an
ADS's conformance is observable only through what an APS makes of its
decision, and the fidelity of that transcription is bilateral.

#### Q.2.3 APS (checked against the resolution document alone)

| ID | Section | Input | Pass | Control |
|---|---|---|---|---|
| S-1 | §4.4 item 1 | A request to a linear window; to an overlay window; to a pause window | `200` with a List MPD; with `@family="overlay"`; with `@family="pause"` | Swap the family: S-1 reports it |
| S-2 | §4.4 item 3 | Every resolution document | Passes all four steps of §4.6 | Break a candidate-hosted callback stream's `@value`: step 3 fails |
| S-3 | §4.4 item 4 | A decision with no ads | `200`, a body, an empty resolution of §5.2.3 | Answer `204` or `404`: reported |
| S-4 | §4.4 item 5 | A multi-option decision | Options in the decision's order | Reorder them: reported against the known decision |
| S-5 | §4.4 item 6 | A request carrying `sgaiAllowedLayouts` | No option outside the forwarded set | Include one outside it: reported |
| S-6 | §4.4 item 6 | A request without `sgaiAllowedLayouts` to an overlay window | No option outside the overlay family default; no `linear`, no `custom` | Emit `linear`: reported |
| S-7 | §4.4 item 6 | A request carrying `sgaiCustomRegion` | Every `custom` rectangle inside the region | Rectangle beyond it: reported |
| S-8 | §4.4 item 7 | Every option | Form in §3.5; video `@assetUrl` resolves to an SPS sub-MPD; no image or HTML on a `@mimeType` of an Adaptation Set or Representation | Put a PNG on a Representation: reported |
| S-9 | §4.4 item 8 | Every `squeezeback-double-box-background` option | Carries `@backgroundUrl` | Remove it: reported |
| S-10 | §4.4 item 9 | An ad with tracking and a ClickThrough | Callback events relative to the ad; `<svta:Click>` carries the ClickThrough and its click-tracking | Put click-tracking on the callback stream: reported |
| S-11 | §4.4 item 10 | A non-linear slot the decision marks dismissible after 5 s; one it marks non-dismissible | `@dismissAfter="PT5S"`; no `@dismissAfter` | — |
| S-12 | §4.4 item 12 | Every pause document | `@onCandidatesExhausted` present | Remove it: reported |
| S-13 | §4.4 item 13 | A request with no capability parameter | `200` with candidates | Requiring a parameter (answering non-`200` without it): reported |

#### Q.2.4 Player

| ID | Section | Input | Pass | Control |
|---|---|---|---|---|
| L-1 | §4.5.1 item 2 | An overlay window with `@earliestResolutionTimeOffset` absent | No resolution request earlier than 60 s before the window's start | Offset `0`: no request before the start |
| L-2 | §4.5.1 item 3 | A pause window; a pause inside it and a pause outside every window | One request, for the pause inside | — |
| L-3 | §4.5.1 item 5 | An early resolution with `@usableFor="PT10S"`, the window firing 30 s later | A new request at firing; nothing from the first document rendered | `@usableFor` absent: the first document is used |
| L-4 | §4.5.1 item 6 | A window declaring `@allowedLayouts` and `@customRegion` | The request carries both, unchanged | The window declares neither: neither is sent |
| L-5 | §4.5.1 item 6 | A Player with no value for an axis | The parameter is absent from the request, not empty | — |
| L-6 | §4.5.1 item 7 | A window without `@maxDuration`; a window with `0` | No ad from either; primary content continues | A valid cap: the ad plays |
| L-7 | §4.5.2 | An overlay window answered with `@family="pause"` | Failed execution; nothing rendered; the next window attempted | `@family="overlay"`: rendered |
| L-8 | §4.5.3 | A candidate whose first option fails the device check and second passes | The second option renders | First option satisfiable: it renders |
| L-9 | §4.5.3 | An option whose layout is outside the window's allowed layouts, received from a non-conforming APS | Not rendered; the next option is tried | Layout inside: rendered |
| L-10 | §4.5.3 | A candidate with no satisfiable option, then a satisfiable one | The second candidate renders; no request to a fallback window | — |
| L-11 | §4.5.4 | An insertion slot capped at 20 s with two 15 s ads | The second ad is trimmed at 20 s cumulative; its later beacons do not fire | Cap 30 s: both ads complete |
| L-12 | §4.5.4 | A replacement slot, `@clip` default, executed 4 s late | The slot ends at the scheduled end | `@clip="false"`: it ends 4 s later |
| L-13 | §4.5.4 item 4 | A cap of `15000` at timescale 1000; a candidate of `PT15.0004S` | Converted to `15001`, exceeds the cap | `PT15S`: converted to `15000`, admitted |
| L-14 | §4.5.4 item 5 | An overlay suspended by a 60 s pause with 10 s of cap left | 10 s of cap remain on resume | — |
| L-15 | §4.5.5 | Three candidates, the second unrenderable | Presented as first, third | — |
| L-16 | §4.5.6 | Two overlapping windows; the first answers each outcome of the §4.5.6 table in turn | The second window is attempted after each | The first answers with a renderable candidate: the second is not requested |
| L-17 | §4.5.6 item 1 | Two windows with equal presentation times | Attempted in stream order | — |
| L-18 | §4.5.6 item 6 | An `@executeOnce="true"` linear event answered with an empty resolution, then traversed again | Executed on the second traversal | The first traversal plays an ad: no second execution |
| L-19 | §4.5.7 | A fallback window with different allowed layouts from the first | The fallback's candidates are checked against the fallback's own set | — |
| L-20 | §4.5.8 | A non-linear document with three candidates | Presented one at a time, in order; never two concurrently | — |
| L-21 | §4.5.9 | An active overlay, then a pause inside a pause window | Pause ad visible, overlay not; on resume overlay restored if its window is open | Live content resuming past the overlay window's end: surface clear |
| L-22 | §4.5.9 item 3 | A linear ad on screen, then a pause inside a pause window | Pause ad presented; linear ad resumes from where it stopped | — |
| L-23 | §4.5.10 item 1 | A pause ad on screen, then resume | Removed within one rendering frame; no beacon after the transition | — |
| L-24 | §4.5.10 item 5 | Live content, a pause inside a pause window lasting longer than the time-shift buffer | Presentation time frozen for the whole pause; the pause ad admissible throughout; resume at a position the base rule admits | — |
| L-25 | §4.5.10 item 6 | An `@executeOnce="true"` pause window; a first pause resolving to no renderable candidate, then a second pause | The second pause presents a pause ad | The first pause presents one: the second presents none |
| L-26 | §4.5.11 | Pause candidates exhausted while paused, for each value of `@onCandidatesExhausted`, and with it absent | Repeat / a new request / stop; absent behaves as `stop` | — |
| L-27 | §4.5.11 | `request-again` answered with an empty resolution | `stop` for the rest of the pause | — |
| L-28 | §4.5.12 | A 10 s image overlay at 2× | 5 s of wall clock; beacons at their presentation-timeline times | 1×: 10 s |
| L-29 | §4.5.13 | Two candidates each with a beacon `@id="1"` | Both fire | Two beacons `@id="1"` in one candidate: one fires |
| L-30 | §4.5.13 item 4 | A candidate-hosted callback stream on an image option | Times resolve from the image's first visible frame | — |
| L-31 | §4.5.14 | A non-linear slot with `@dismissAfter="PT5S"` | Dismissal available from 5 s, not before; dismissal ends every remaining ad of the slot; beacons after it do not fire | `@dismissAfter` absent: no dismissal offered |
| L-32 | §4.5.14 item 2 | A linear event with `@skipAfter` omitted; with `@skipAfter="PT10S"` | Skipping permitted from the start; from 10 s | — |
| L-33 | §4.5.15 | A candidate with `<svta:Click>` and two click-tracking URLs; the viewer activates | Destination opened; both URLs fired once, at activation | No activation: neither fires |
| L-34 | §4.5.16 | An ad segment returning `404` mid-ad | Ad aborted; primary content continues with no visible artefact | — |
| L-35 | §4.5.3 item 4 | A `custom` option on a Player that does not support `custom` | Not rendered; the next option renders | A Player that supports it: rendered when contained |

### Q.3 Chapter 5 — syntax

| ID | Section | Check | Pass |
|---|---|---|---|
| X-1 | §5.1.3, §5.1.4 | `<svta:OverlayPresentation>` / `<svta:PauseAdPresentation>` against §5.10 | Valid; `@uri` and `@maxDuration` present |
| X-2 | §5.2.1 | A List MPD | `type="list"`, the List profile URN, each ad Period with `@id`, `@duration`, `<ImportedMPD>`, `svta:` children after DASH children |
| X-3 | §5.2.2 | A non-linear document | Full profile, `static`, one `PT0S` Period with one `<svta:OverlayList>` carrying `@family` |
| X-4 | §5.2.3 | An empty resolution of each family | Matches one of the two shapes |
| X-5 | §5.3.1 | Every `<svta:RenderableAsset>` | `@form`, `@layout`, `@assetUrl`; `@duration` on non-linear options; conditional attributes exactly where §5.3.1 says |
| X-6 | §5.3.3 | Every `@layout` | Admissible for the document's family |
| X-7 | §5.3.5 | Every rectangle | Four integers 0–100, `x + width ≤ 100`, `y + height ≤ 100` |
| X-8 | §5.4 | Every sub-MPD | SPS profile, one Period with `@duration`, RFC 4337 media types |
| X-9 | §5.5 | Every callback stream, including those inside candidates | Scheme `urn:mpeg:dash:event:callback:2015`, `@value="1"`, URL as content |
| X-10 | §5.8 | Every resolution request | Reserved names spelled as §5.8.2 and §5.8.3; no empty value; any other parameter vendor-prefixed |

### Q.4 Chapter 6 — interfaces

| ID | Section | Check | Pass |
|---|---|---|---|
| I-1 | §6.4 | Requests from a Player to the APS, captured | GET of the window's `@uri`; parameters per §6.4 |
| I-2 | §6.5 | Requests from a Player, captured across a session | No request to any ADS endpoint |
| I-3 | §6.5 | A tracking endpoint returning `500` | The ad and the primary content are unaffected |
| I-4 | §5.8.1 | A `<RequestParam>` scoped to `urn:svta:dash:sgai-resolution:2026` | Its parameters on non-linear requests; not on linear ones |
| I-5 | §5.8.5 | A template and reserved parameters on one request | Both present, no name collision, `@uri`'s own query kept |

### Q.5 Chapter 7 — expected behaviour, per scenario

| ID | Section | Scenario | Annex | Pass, on D1..D5 |
|---|---|---|---|---|
| B-1 | §7.2 | Pre-roll | A | Linear ad then primary content, on every class |
| B-2 | §7.2 | Mid-roll, live, trick play | B | Ad at the primary content's speed; cap and beacons on the presentation timeline |
| B-3 | §7.3 | Coexisting overlay, multi-form | C | Each class renders the first option §5.3.7 admits for it; D5 skips |
| B-4 | §7.5 | Hybrid break | D | D1 any overlay; D2 video only; D3 image or HTML; D4 image; D5 linear only |
| B-5 | §7.6 | Pause ad | E | Pause ad only while paused; removed within one frame on resume |
| B-6 | §7.2 | Multi-ad break | F | Ads in order; trimmed at the cap |
| B-7 | §7.9 | Legacy Player | G | Primary content, or the standard break on on-demand content |
| B-8 | §7.7 | Overlay crossing a pause window | H | Overlay suspended, restored if its window is open |
| B-9 | §7.3 | One ad, ordered options | I | D1 double box with background; D2 takeover; D3, D4 L-shape; D5 takeover |
| B-10 | §7.3 | Double box with background | J | D2 declines the background layout; D3 renders the HTML form, D4 the image form |
| B-11 | §4.5.15 | ClickThrough | K | Identical on every class |
| B-12 | §7.8 | Overlapping windows | L | Fallback after every failed execution; not after an unrenderable document |
| B-13 | §7.3 | Declared capabilities, single option | M | The same rendered result per class as B-9 |
| B-14 | §7.5 | Overlay over a non-advertising replacement | N | As B-4 |
| B-15 | §7.3 | Forwarded allowed layouts | O | D1, D3, D4 L-shape; D2, D5 skip |
| B-16 | §7.3 | `custom` overlay | P | Rendered where supported and contained; otherwise the lower-third; D5 skips |

### Q.6 Error conditions

Each row of §8.2 maps to the tests that exercise it.

| Condition | Tests |
|---|---|
| E1 — transport failure or non-`200` | L-16, S-13 |
| E2 — unparseable or invalid document | L-16, S-2 |
| E3 — document of the wrong family | L-7, S-1 |
| E4 — empty resolution | L-16, L-18, L-25, S-3 |
| E5 — late or expired resolution | L-3, L-12 |
| E6 — no cap, or a zero cap | L-6, P-1 |
| E7 — nothing satisfiable on the device | L-8, L-10 |
| E8 — layout not admitted | L-9, L-19, L-35, S-5, S-6, S-7 |
| E9 — creative media type outside §3.5 | S-8 |
| E10 — cap reached | L-11, L-12, L-13, L-14 |
| E11 — runtime failure of an accepted ad | L-34 |
| E12 — unknown construct | Q.7 |
| E13 — beacon failure, or a beacon after a trim, a resume or a dismissal | I-3, L-11, L-23, L-31 |
| E14 — two non-linear forms, or a pause over an overlay or a linear ad | L-20, L-21, L-22 |
| E15 — exhausted pause candidates, consumed window | L-25, L-26, L-27 |

### Q.7 Backward compatibility, per construct

Each construct of §4.7 has one test modelled on the legacy scenario of
Annex G. The harness is a Player that implements the base specification
and not this one. **The invariant every test checks is that the
construct is ignored**: no request caused by it, no beacon fired for it,
no error at fatal level, and playback continuing. What the viewer then
sees depends on the Publisher's authoring choice — the primary content
for live content, a standard linear break where the Publisher authored
one for on-demand content — and that break is a base construct outside
these tests.

| ID | Construct | Input | Pass |
|---|---|---|---|
| Q.7.1 | Overlay scheme and `<svta:OverlayPresentation>` | A main MPD with an overlay window | No request to its `@uri`; primary content uninterrupted |
| Q.7.2 | Pause scheme and `<svta:PauseAdPresentation>` | A main MPD with a pause window; a pause inside it | No request; the paused frame stays; resume continues |
| Q.7.3 | Non-linear resolution document, including candidate-hosted tracking | The document fed directly to the parser | Parses; one empty zero-duration Period remains; nothing presented; no beacon |
| Q.7.4 | Extension content on a List MPD Period | A List MPD whose Period carries `<svta:RenderableAsset>` and `<svta:Click>` | The `<ImportedMPD>` video plays; no image or HTML option presented; the click inert |
| Q.7.5 | Reserved parameters and the request-type URN | A `<RequestParam>` whose `@includeInRequests` holds `altmpd` and the URN | The URN token dropped; `altmpd` parameters still sent on linear requests |

### Q.8 What is not tested here

- The APS-to-ADS exchange and the fidelity of the transcription, which
  are bilateral.
- How dismissal or a ClickThrough is offered to the viewer — the
  control, the gesture, the button.
- Reporting transport for any metric.
- Retry counts, backoff and timeouts of the resolution request, which
  are implementation choices (§8.4).

---


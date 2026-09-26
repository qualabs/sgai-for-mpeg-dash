# SGAI for Linear and Non-Linear Ads in MPEG-DASH

**Status:** candidate specification, build iteration 11.
**Namespace of the constructs it introduces:** `urn:svta:dash:sgai:2026`.
**Incubation venue:** SVTA Ads Working Group.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and
"OPTIONAL" in this document are to be interpreted as described in BCP 14
(IETF RFC 2119, IETF RFC 8174) when, and only when, they appear in all
capitals, as shown here.

Chapters 1 to 7 are normative. Chapter 8 is informative. The annexes are
informative and mandatory in this document: each walks one scenario end to
end with complete documents, and the last one lists what an implementer can
test against.

**References.** `DASH §n`, `DASH Annex X` and `Table n` refer to the base
specification (ISO/IEC 23009-1:2026); a bare `§n` or `Annex X` refers to this
document. Quotations from the base specification are given in italics between
quotation marks, with the clause they come from. A statement about the base
specification that could not be verified against its text is tagged
`[inferred]`.

## Table of contents

1. Scope
2. Normative references
3. Terms, definitions and abbreviations
4. Conformance
5. Syntax
6. Interfaces
7. Expected behaviour
8. Implementation notes (informative)

Annexes (informative):

- Annex A — Pre-roll
- Annex B — Mid-roll
- Annex C — Coexisting overlay, several forms and layouts
- Annex D — Hybrid: a linear break with an overlay composited on top
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
- Annex Q — A non-linear ad that supersedes a linear break
- Annex R — Test cases and conformance criteria

---

## 1. Scope

### 1.1 What this specification covers

This specification defines Server-Guided Ad Insertion (SGAI) for **both
linear and non-linear ads** in MPEG-DASH, as a complete extension of the
sixth edition of MPEG-DASH (ISO/IEC 23009-1:2026, referred to below as *the
base specification*).

- **Linear SGAI is the baseline, absorbed as it stands.** The base
  specification already carries linear ad insertion: the Alternative MPD
  Insertion and Replacement events (`InsertPresentation`,
  `ReplacePresentation`, DASH §5.16) and the List MPD that an ad server returns
  for them (DASH §8.14). This specification adopts those constructs with their
  base semantics and adds to the linear path only what the base does not
  answer: a normative ClickThrough carrier, optional creative metadata, a
  dismissal declaration in the resolution document, and the Player
  obligations that tie the linear path to the non-linear one.
- **Non-linear SGAI is the principal new content.** The base specification
  has no construct for an ad that shares the screen with the primary
  content. This specification adds two opportunity windows (overlay and
  pause), a resolution document for them, an ordered list of presentation
  options per ad, the closed layout vocabulary those options draw from,
  the composition rules for each layout, and the Player behaviour that
  keeps the primary content playing whatever happens to the ad.

The ad types this edition supports are a closed subset of the IAB CTV ad
portfolio, all rendered on or within the video surface: **linear**,
**overlay** (corner, lower-third, and plain), **squeezeback** (two L-shape
orientations and two double-box forms), and **pause ads** (fullscreen and
partial). Chapter 3 lists them.

The specification is written for four audiences: Publishers authoring
MPDs, operators of Ad Presentation Servers, Player implementers, and
anyone auditing that the three interoperate.

### 1.2 The four actors

Every obligation in this document binds one of four actors, or this
document itself.

| Actor | Owns | Does not own |
|---|---|---|
| **Publisher** | The primary content and the screen. Declares, in the MPD, where ad opportunities are, of which kind, and under which constraints (maximum duration, allowed layouts, the window's relation to linear events). | Which ads fill an opportunity. |
| **Ad Decision Server (ADS)** | The ad decision: how many ads, which ones, in what order; targeting, frequency capping, brand safety, competitive separation; the tracking schedule. It answers in its own decision format — typically VAST, though it is not bound to VAST. | Converting its decision into anything a Player reads, and enforcing the Publisher's constraints. |
| **Ad Presentation Server (APS)** | The endpoint the MPD event's `@uri` points to. It obtains the decision from the ADS and converts it into the **resolution document** the Player reads, translating the ADS's tracking events into DASH callback events. | Deciding which ads to serve, and enforcing the Publisher's constraints. |
| **Player** | Reading the MPD, resolving opportunities against the APS, validating every candidate against what the Publisher declared, choosing what its device can render, composing it, and keeping the primary content playing. | The ad decision, and the tracking schedule. |

In deployed systems the APS is often a module of the ADS. It is kept
separate here because its responsibility is distinct: the ADS's format
comes in, the resolution document this specification defines goes out.

The Player never talks to the ADS. The interface this specification
defines is the one the Player sees: the MPD event URL, the request the
Player sends to it, and the resolution document that comes back. The
APS-to-ADS exchange and the ADS-side API are outside it (§1.3).

### 1.3 Out of scope

- **The APS-to-ADS and ADS-side contracts.** The request the APS sends
  to the ADS, the format of the ADS's decision document (VAST or any
  other), the decisioning inputs and the frequency-capping signals are
  agreed between those parties, outside this specification. So are the
  fidelity of the tracking transcription (that the APS neither adds,
  removes nor reorders the beacons the ADS declared) and whether a
  ClickThrough the ADS declared reaches the resolution document at all:
  the ADS declares both and receives the resulting requests, so it is in
  a position to enforce them, and the resolution document is not,
  because it does not show what was declared.
- **The ADS's decisioning logic**: targeting, frequency capping, brand
  safety filtering and every other business rule.
- **A layout engine.** Spatial arrangement of overlays is delegated to
  HTML5 and CSS, aligned with the IAB CTV guidelines. This specification
  defines no parallel layout standard and no position vocabulary inside
  a layout (left, right, top, bottom); where an ad sits inside its layout
  follows from the IAB ad type the layout token names. The one exception
  is the optional `custom` overlay layout (§5.3.5), whose rectangle is a
  position by definition.
- **Creative carriers other than video, image and HTML** (§3.5): raw
  JavaScript, SVG as payload, PDF, proprietary binary creatives. A sender
  that needs a scripted creative MUST wrap the script inside an HTML
  document and carry it as `text/html`.
- **Interactive ad frameworks** such as SIMID. An ad built on such a
  framework is delivered by that framework. SIMID is not among the ad
  types this edition supports, and this edition defines no non-linear
  form that carries a SIMID payload.
- **Single-decoder slice or tile replacement**, where one decoder
  carries both the primary content and the ad. The technique exists and
  is most practical in HEVC and AV1; this edition's decoder-budget
  reasoning assumes one decoder per concurrent form.
- **Preventing a viewer from seeking past a non-linear window.** The base
  specification's `@noJump` is preserved unchanged on the inherited
  linear events, where the ad occupies the timeline and forbidding the
  jump forbids skipping the ad. It is not carried on the non-linear
  windows: the primary content keeps playing underneath a non-linear ad,
  so forbidding the jump there would oblige the viewer to watch a stretch
  of programme they chose to skip, not the ad. This is an exception and
  not an omission (DASH §4.8.9).
- **Linking the two portions of a hybrid break.** No construct lets a
  Publisher declare a constraint between a linear ad and an overlay
  composited on top of it ("if the linear ad is from advertiser X,
  suppress the overlay"), and a Player is never asked to enforce one.
  Enforcing it in the Player would require the advertiser's identity to
  reach the Player, and competitive separation is already the ADS's
  responsibility; exclusivity between the portions is obtained from the
  ADS.
- **Ads outside the video surface**: menu ads, home-screen and launcher
  ads, screen-saver ads, companion or multi-screen ads, and in-scene ads
  (virtual product placement, which is part of the video frames rather
  than something the Player renders over them). The contract this
  specification defines is between a manifest and the Player that plays
  it; these ads are outside it and are not candidates for a later
  edition.
- **Server-side ad insertion (stitching)** and **post-roll slots.**
- **How a dismissal is offered to the viewer** — a control, a gesture, a
  remote button (§4.5.14).
- **Whether a second resolution request within one pause is the same
  opportunity or a new one** (§4.5.11).
- **How a measurement reaches the Publisher, the APS or the ADS**
  (§5.9).
- **Blackouts.** Annex N uses one to show that the presentation under a
  non-linear ad need not be an ad; this specification does not specify
  how a Publisher blacks out content.
- **Authentication, DRM and token exchange**, which layer on top of HTTPS
  as for any DASH content.

### 1.4 Relationship to the base specification

This specification **extends** the base specification and alters nothing
in it. Three rules govern every construct it adds, and chapter 4 states
them as obligations:

1. **The base answer comes first.** Where the base specification already
   defines a behaviour, a default or a construct for a question this
   specification has to answer, this specification adopts it and cites
   it. It defines its own answer only where the base gives none, and
   declares that answer as an extension. The departures it makes anyway
   are listed, each with its reason, in §4.8.3.
2. **Nothing added can break a Player that ignores it.** Every construct
   sits at an extension point of the base specification whose base
   semantics let a Player that does not implement this specification
   remove it and continue playing the primary content. The base states
   the authoring obligation this relies on: *"the MPD shall be authored
   such that, after XML attributes or elements in the other namespaces
   than the DASH namespace are removed, the result is a valid XML document
   formatted according to that schema and that conforms to this
   document"* (DASH §5.2.1).
3. **Nothing added can compel a Player that ignores it.** The base
   specification states that *"as DASH Client operation is not specified
   normatively in this document, it is also unspecified how a DASH Client
   conforms to a particular profile. Hence, profiles merely specify
   restrictions on MPD and Segments rather than DASH Client behaviour"*
   (DASH §8.1, NOTE 1). Every Player obligation in this document therefore
   binds **a Player conformant to this specification**, and no sentence in
   it promises what every Player will do.

The design principles that govern the constructs are three, and each is
applied as an obligation on this document in §4.6:

- **Keep it simple; information is not redundant.** A construct does not
  carry what its element name, its namespace, its parent or another
  attribute already determines, and no construct exists "in case a future
  edition relaxes it".
- **Obligations are positive.** Where this document adds an obligation of
  its own, it states the action to take, not a list of prohibitions; what
  lies outside the positive obligation is out of scope. Prohibitions the
  requirements themselves state are kept as prohibitions.
- **Maximise the ad opportunity, never at the cost of playback.**
  Applying this specification never breaks primary-content playback: when
  an opportunity cannot be honoured, skip-and-continue is mandatory. The
  base specification states the same invariant for its own execution
  model: *"If no event can be successfully executed, the playback
  continues uninterrupted"* (DASH §5.16.2.2.5), and *"A failed execution
  results in smooth continued playback of the main media presentation"*
  (DASH §5.16.2.2.6).

---

## 2. Normative references

The following documents are referred to in such a way that some or all of
their content constitutes requirements of this document.

- **ISO/IEC 23009-1:2026 (Sixth edition, 2026-07)**, *Information
  technology — Dynamic adaptive streaming over HTTP (DASH) — Part 1: Media
  presentation description and segment formats*. The base specification.
  Clauses relied on: DASH §4.2 (client model), DASH §5.2.1 (extension by other
  namespaces), DASH §5.3.1.4 (`MPD@type="list"`), DASH §5.3.2 (Period, Table 4;
  Linked Periods and `ImportedMPD`, DASH §5.3.2.6, Table 5), DASH §5.8.4.8 and
  DASH §5.8.4.9 (Essential and Supplemental descriptors), DASH §5.9 (Metrics),
  DASH §5.10 (Events, Tables 43 and 44; callback event, DASH §5.10.4.5, Table 47),
  DASH §5.16 (Alternative Media Presentations, Tables 57 to 63), DASH §7.3.1,
  DASH §8.1 (profiles), DASH §8.12.4.3, DASH §8.13, DASH §8.14 (List profile), DASH §8.15
  (Single-Period Static profile), DASH Annex D.4.6 (`PlayList` metric,
  Table D.5), DASH Annex H (Spatial Relationship Description), DASH Annex I.3 and
  I.4 (extended request parametrisation, Tables I.3 to I.5), DASH Annex K.3.8
  (playback restrictions, Tables K.9 and K.18).
- **IAB Tech Lab, *Ad Format Guidelines for Digital Video and CTV*** —
  the IAB CTV ad portfolio and its visual placements. Live document, not
  snapshotted: <https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e>;
  portfolio page: <https://iabtechlab.com/standards/ctv-ad-portfolio/>.
  The accepted ad-type values of §3.4 and the spatial bound of each layout
  come from this document.
- **IETF RFC 2119** and **IETF RFC 8174** (BCP 14), *Key words for use in
  RFCs to Indicate Requirement Levels*.
- **IETF RFC 3986**, *Uniform Resource Identifier (URI): Generic Syntax*
  — query parameters and percent-encoding of the resolution request.
- **IETF RFC 4337**, *MIME Type Registration for MPEG-4* — the media types
  a Representation of an ISO-BMFF presentation may carry.
- **W3C XML Schema 1.1 Part 2: Datatypes** — `xs:duration`,
  `xs:anyURI`, `xs:unsignedLong` and the list types used in chapter 5.
- **WHATWG HTML Living Standard** and **W3C CSS** — the `text/html`
  creative form and the layout primitives spatial arrangement is
  delegated to.

**Informative references.**

- **IAB Tech Lab, VAST (Video Ad Serving Template) 4.x.** Cited only as
  the typical decision format an ADS emits and in the illustrative
  conversions of Annexes A and C. No normative clause of this document
  requires VAST or any VAST version.

### 2.1 URIs this edition introduces

| URI | What it identifies | Defined in |
|---|---|---|
| `urn:svta:dash:sgai:2026` | The XML namespace of every element and attribute this specification introduces. | §5 |
| `urn:svta:dash:sgai-overlay:2026` | The event scheme of an overlay opportunity window. | §5.1.3 |
| `urn:svta:dash:sgai-pause-trigger:2026` | The event scheme of a pause opportunity window. | §5.1.4 |
| `urn:svta:dash:sgai-resolution:2026` | The request type, in the sense of DASH Annex I.3.6 of the base specification, of the resolution request for an overlay or pause window. | §5.8.1 |

The tracking callback scheme is **not** among them. This specification
reuses the base specification's `urn:mpeg:dash:event:callback:2015`
(DASH §5.10.4.5); that scheme follows the base edition's lifecycle, not this
specification's.

**Versioning.** The `<year>` suffix is the edition year of this
specification. A later edition that changes the semantics of a construct
mints a new URI for it with the new year; a construct whose semantics are
unchanged keeps its URI. A Player implementing edition N + 1 SHOULD
recognise the URIs of both editions and treat each per that edition's
backward-compatibility rules. A URI is never reused with altered
semantics: a fresh URI per edition is what keeps the "ignore if unknown"
guarantee clean for a Player that knows only the earlier one.

**Vendor extensions.** Experimental extensions that are not part of this
specification use a vendor namespace of their own, not
`urn:svta:dash:*`; the vendor namespace `urn:qualabs:<feature>:<year>` is
reserved for Qualabs-private extensions, which are not normative.

---

## 3. Terms, definitions and abbreviations

### 3.1 Terms and definitions

- **Base specification** — ISO/IEC 23009-1:2026, the standard this
  specification extends. "Base" is used when the point is that a rule
  comes from that standard and not from this one.
- **Primary content** — the programme the viewer chose to watch, as
  distinct from any ad. It is what the MPD describes before any SGAI
  construct is added.
- **Presentation** — a Media Presentation in the sense of the base
  specification. The primary content is one; an alternative presentation
  started by an inherited linear event is another, run by a second
  instance of the client: *"there are two instances of DASH access
  engine, main and the alternative, both working as described above"*
  (DASH §4.2).
- **Ad opportunity, slot** — a point or region of a presentation's
  timeline where the Publisher allows an ad. *Slot* is used for the
  opportunity together with what fills it.
- **Family** — a kind of ad opportunity. This edition has three:
  **linear** (the ad takes over the screen), **overlay** (the ad shares
  the screen with primary content that keeps playing), and **pause** (the
  ad is shown while the viewer has paused). Overlay and pause together are
  the **non-linear** families.
- **Inherited linear event** — an Alternative MPD Insertion event
  (`InsertPresentation`, DASH §5.16.3) or Replacement event
  (`ReplacePresentation`, DASH §5.16.4) of the base specification, used as a
  linear ad opportunity. The base names advertisement as *"a key use
  case"* (DASH §5.16.1) and blackouts beside it; this specification uses the
  insertion for splice-style breaks and the replacement for break-style
  ads, and neither event tells a Player whether its alternative
  presentation is an ad.
- **Opportunity window, window** — the construct this specification
  defines for a non-linear opportunity: an `Event` of an overlay or
  pause-trigger scheme, spanning `[Event@presentationTime,
  Event@presentationTime + Event@duration)` on the timeline of the
  presentation whose MPD declares it (§5.1).
- **Span** — that interval.
- **Resolution request** — the HTTP GET a Player issues against an
  opportunity's `@uri` to obtain its resolution document.
- **Resolution document** — what the APS returns for a resolution
  request, describing the ad or ads to render and how. For an inherited
  linear event it is a List MPD (DASH §8.14) or a single-period alternative
  MPD; for an overlay or pause window it is the non-linear resolution
  document `<svta:OverlayList>` (§5.2.2). It is the only thing the Player
  reads about an ad.
- **Candidate** — one ad in a resolution document. In a List MPD a
  candidate is one `Period`; in a non-linear resolution document it is one
  `<svta:Ad>`.
- **Presentation option, option** — a form together with a layout,
  offered for a candidate. A candidate carries one or more, as an ordered
  list.
- **Form** — the creative carrier of an option: video, image or HTML
  (§3.5).
- **Layout** — the spatial arrangement of an option, named by one layout
  token (§3.4.2).
- **Document order** — the order in which elements appear in the document
  as written, which is the order an XML parser reports them in. Wherever a
  list expresses a preference, the first element in document order is the
  most preferred, and nothing outside the document carries that ranking.
- **Preference order** — the order in which a Player considers the
  options of a candidate; always document order.
- **Cap** — the maximum a Publisher declares on a slot. On an inherited
  linear event it is the base `@maxDuration`; on an overlay or pause
  window it is `@durationCap` (§5.1.3). What it bounds depends on the
  family (§4.5.4).
- **Failed execution** — an attempt on an opportunity that produced no
  alternative presentation or no ad, in the base specification's sense
  (DASH §5.16.2.2.6). It is not an error: the base places an event whose
  `@executeOnce` has already fired under the same heading. The four
  shapes an attempt on a resolution document can take and still fail are
  listed in §4.5.6.
- **Fallback chain** — the overlapping windows of one family, taken in
  order, the next attempted only when the previous one produced no ad.
- **Relation** — what a non-linear window declares about the inherited
  linear events it overlaps: nothing (the default), **supersede** or
  **on top** (§5.1.6).
- **Capability parameter** — a reserved query parameter a Player MAY
  attach to a resolution request, stating what its device supports
  (§5.8.2). An absent capability parameter means its value is
  **undetermined**, not that the device lacks the capability.
- **Forwarded declaration** — a slot declaration the Player is required
  to copy onto the resolution request: the allowed layouts and the custom
  region (§5.8.3).
- **Dismissal** — the viewer ending a whole slot before it would have
  ended (§5.2.4).
- **Usable lifetime** — how long a resolution document obtained ahead of
  its opportunity stays usable (§5.2.5).
- **Exhaustion behaviour** — what a Player does when the candidates of a
  pause resolution document run out while the viewer is still paused
  (§5.2.6).
- **Device class** — the rendering capability of a device relevant to
  this specification (§3.6).
- **Legacy Player** — a Player conforming to the base specification that
  does not implement this one. It is a class of implementation, not a
  mode; no Player announces itself as legacy, and nothing in this
  specification can oblige one.
- **Foreign-namespace open content** — elements and attributes from a
  namespace other than DASH's, admitted under DASH containers by
  `<xs:any namespace="##other" processContents="lax"/>` and
  `<xs:anyAttribute namespace="##other" processContents="lax"/>` in the
  base schema, and removable under DASH §5.2.1.
- **Sub-MPD** — an MPD referenced by URL from a resolution document: the
  target of an `ImportedMPD` in a List MPD, or the video creative of a
  non-linear option. Both are Single-Period Static MPDs (DASH §8.15).
- **Spec document** *(scope label)* — the scope given to a conformance
  criterion that binds this document's own text rather than an actor at
  runtime (§4.1).

### 3.2 Abbreviations

| Abbreviation | Expansion |
|---|---|
| ADS | Ad Decision Server |
| APS | Ad Presentation Server |
| CTV | Connected TV |
| EAP | End of active interval of an event (base, Table 57) |
| ERT | Earliest resolution time (base, Table 57) |
| HTML | HyperText Markup Language |
| IAB | Interactive Advertising Bureau (IAB Tech Lab) |
| MPD | Media Presentation Description |
| PRT | Event presentation time (base, Table 57) |
| PRTA | Actual event presentation time, the execution time (base, Table 57) |
| RT | Resumption time of the main presentation (base, Table 57) |
| SGAI | Server-Guided Ad Insertion |
| SPS | Single-Period Static profile (base, DASH §8.15) |
| SRD | Spatial Relationship Description (DASH Annex H) |
| VAST | Video Ad Serving Template (IAB) |
| VOD | Video on demand |

### 3.3 The three families

| Family | Opportunity construct | Resolution document | What the screen does |
|---|---|---|---|
| Linear | `InsertPresentation` or `ReplacePresentation` event (base, DASH §5.16) | List MPD (base, DASH §8.14), or a single-period alternative MPD | The ad takes over the screen; the primary content is not output. |
| Overlay | Overlay window: `Event` of scheme `urn:svta:dash:sgai-overlay:2026` carrying `<svta:OverlayPresentation>` | `<svta:OverlayList family="overlay">` | The ad shares the screen with the primary content, which keeps playing — composited over it, or with the primary content shrunk (squeezeback). |
| Pause | Pause window: `Event` of scheme `urn:svta:dash:sgai-pause-trigger:2026` carrying `<svta:PauseAdPresentation>` | `<svta:OverlayList family="pause">` | While the viewer is paused inside the window, the ad is shown fullscreen or over the paused frame. |

**The word *overlay* is used in two vocabularies, and this document says
which one it means.** As a **family**, it is the overlay family of the
table above. As a **layout token**, `overlay` is one spatial arrangement
(§3.4.2). The resolution document of both non-linear families is named
`OverlayList`: in that name, and in `<svta:OverlayPresentation>`,
*overlay* takes the family reading for the non-linear document, and a
pause document travels under the same name because a pause ad is a
non-linear ad, not because it is laid out as an overlay. Names that
select a spatial arrangement are layout tokens and are governed by the IAB
vocabulary.

### 3.4 Accepted ad types and layout tokens (normative)

The ad types and their visual placements are defined and maintained by the
IAB (IAB Tech Lab, *Ad Format Guidelines for Digital Video and CTV*,
chapter 2). This specification references those definitions normatively; it does
not define ad types or visual templates, and it does not accept the whole
IAB catalogue. This edition supports a **closed, edition-scoped subset**,
all rendered on or within the video surface. An IAB ad type or placement
not listed here is out of scope for this edition, and one the IAB publishes
later does not enter scope automatically: widening the set requires a new
edition of this specification.

#### 3.4.1 The IAB ad types, and which are accepted

| IAB ad type | Accepted | Values in this specification | Reason |
|---|---|---|---|
| Linear Ad | Yes | `linear` | Full-viewport takeover of the primary content surface for the slot. Pre-roll, mid-roll and multi-ad breaks are timing positions of this one type; the full-screen takeover offered as a fallback option of a non-linear candidate is a placement of `linear`, not a separate type. |
| Overlay | Yes | `overlay`, `overlay-corner`, `overlay-lower-third` | IAB *Corner Overlay* and *Lower Third Overlay* are the named placements; a plain overlay with no named placement is the base `overlay`. |
| Squeezeback | Yes | `squeezeback-l-shape-upper-left`, `squeezeback-l-shape-upper-right`, `squeezeback-double-box`, `squeezeback-double-box-background` | IAB *L-Shape* in its two orientations, *Double Box Video* and *Double Box Video + Background*. IAB *Frame* is not among the accepted placements. |
| Pause Ad | Yes | `pause-fullscreen`, `pause-partial` | IAB *Fullscreen* and *Partial Screen* placements of the pause experience. |
| Menu Ad | No | — | Rendered in the platform interface, not on the video. |
| Screen Saver Ad | No | — | Started by the operating system or application after inactivity, off the video. |
| Companion Ad | No | — | Rendered outside the player. |
| In Scene Ads | No | — | Part of the video frames, not rendered over them. |

#### 3.4.2 The layout tokens

The following tokens are the **complete** list of layout values this
specification accepts. Every token except `custom` names one IAB ad type or
visual placement. `custom` is the only value with no IAB counterpart
(§5.3.5).

| Token | IAB ad type / placement | Family | Composition |
|---|---|---|---|
| `linear` | Linear Ad | linear (also offered as the full-screen takeover option of a non-linear candidate) | The ad occupies the full viewport; the primary content is not output while it plays. |
| `overlay` | Overlay (no named placement) | overlay | Composited over playing primary content, which is not resized. |
| `overlay-corner` | Corner Overlay | overlay | Composited over playing primary content; the IAB bounds it to 25% of the frame. Which corner is not a token: it follows from the creative and is rendered with HTML5 / CSS. |
| `overlay-lower-third` | Lower Third Overlay | overlay | Composited over playing primary content, across the bottom 30% of the frame. |
| `squeezeback-l-shape-upper-left` | Squeezeback, L-Shape | overlay | The primary content occupies the **upper-left 60%** of the frame; the ad runs across the bottom and up the right edge. |
| `squeezeback-l-shape-upper-right` | Squeezeback, L-Shape | overlay | The primary content occupies the **upper-right 60%** of the frame; the ad runs across the bottom and up the left edge. |
| `squeezeback-double-box` | Squeezeback, Double Box Video | overlay | The primary content occupies the **centre-left 25%** of the frame and the ad the **centre-right 25%**; the uncovered bands render black. |
| `squeezeback-double-box-background` | Squeezeback, Double Box Video + Background | overlay | As `squeezeback-double-box`, over an advertiser-branded background image that fills the uncovered bands. |
| `pause-fullscreen` | Pause Ad, Fullscreen | pause | The ad occupies the entire screen surface while the viewer is paused. |
| `pause-partial` | Pause Ad, Partial Screen | pause | The ad is composited over the paused primary frame, which remains visible underneath. |
| `custom` | — (no IAB counterpart; optional) | overlay | Composited over playing primary content inside a rectangle the APS gives in percent of the video viewport (§5.3.5). |

**The squeezeback tokens carry the geometry because nothing else does.**
In a squeezeback the Player shrinks and repositions the primary content,
which it does for no other form, so it needs the region before it
composes. The IAB creative arrives as an underlay whose cutout shows the
region to a viewer, but a hole in an image is not a rectangle a Player can
compute with, and the IAB guidelines define no field that carries one. Two
orientations of the L-shape are therefore two tokens, because they are two
compositions. This is not a position vocabulary: what the token names is
which composition is in play, not where something sits inside it.

**The bare `squeezeback` and `pause` are not tokens**, because neither says
which composition the Player builds. `pause-fullscreen` and `pause-partial`
are separate so that a Publisher can admit one surface and exclude the
other.

**Spatial bounds are inherited by reference.** Each token implies the
spatial bound the IAB guidelines declare for its placement (for example a
Corner Overlay no more than 25% of the frame, the primary content of an
L-Shape 60% of the frame). This specification does not re-declare them and
introduces no dimensional attribute on the slot declaration.

#### 3.4.3 The family default

A window that declares no allowed layouts admits the tokens of its own
family and no others:

| Window | Admitted when `@allowedLayouts` is absent |
|---|---|
| Overlay | `overlay`, `overlay-corner`, `overlay-lower-third`, `squeezeback-l-shape-upper-left`, `squeezeback-l-shape-upper-right`, `squeezeback-double-box`, `squeezeback-double-box-background` |
| Pause | `pause-fullscreen`, `pause-partial` |

The family default does **not** include `linear` — an overlay window that
declares nothing does not admit the full-screen takeover — and it does not
include `custom`, which a window admits only by listing it.

Inherited linear events carry no allowed-layouts declaration; the layout of
a List MPD candidate is `linear` by construction.

### 3.5 Creative-carrier forms

The admissible creative carriers are **exactly three**, and no annex,
example or implementation note of this document adds another:

| Form | Carried as | `@mimeType` of the option (§5.3) |
|---|---|---|
| **Video** | A Single-Period Static MPD whose Representations carry ISO-BMFF media, under the base specification's MP4 constraints (DASH §7.3.1: *"The @mimeType attribute of each Representation shall be provided according to IETF RFC 4337"*). | `application/dash+xml` |
| **Image** | A still image in a format the IAB guidelines admit for the layout. | an `image/*` type, for example `image/png`, `image/jpeg` |
| **HTML** | An HTML document, which MAY contain inline `<script>` under HTML5 semantics; the script runs under the device's HTML capability, not as a separate carrier. | `text/html` |

### 3.6 Device classes

The device class captures only what this specification depends on: how
many video decoders the device can run at once, and which kinds of surface
it can composite over video. Codec support, DRM and network conditions are
orthogonal.

| Class | Concurrent video decoders | Image over video | HTML over video | Video over video |
|---|---|---|---|---|
| **D1** — top tier | 2 or more | yes | yes | yes |
| **D2** | 2 | no | no | yes |
| **D3** | 1 | yes | yes | no |
| **D4** | 1 | yes | no | no |
| **D5** — worst case | 1 | no | no | no |

A second video composited over the primary content needs a second
decoder; image and HTML surfaces need no decoder. During an alternative
presentation the base specification outputs one presentation at a time —
*"the alternative access engine outputs media to the media engine, while
the main client will be paused or be in a listen mode"* (DASH §4.2) — so a
linear ad occupies the decoder the primary content has just stopped
using, and an overlay composited over a linear ad needs the same budget as
one composited over the primary content.

The expected behaviour of every class for every opportunity type is given
in chapter 7 and walked through, with documents, in Annexes A to Q.

---

## 4. Conformance

### 4.1 What conformance means here

A Publisher, an ADS, an APS or a Player claims conformance to this
specification by satisfying every MUST and MUST NOT addressed to it in this
chapter and in chapters 5 to 7. Each criterion below carries an identifier
(`PUB-n`, `ADS-n`, `APS-n`, `PLY-n`, `DOC-n`) that Annex R uses to name its
tests.

**What each actor is checked against.**

| Actor | Checked against |
|---|---|
| Publisher | The main MPD it publishes, and the MPDs of the alternative presentations it authors. |
| ADS | Nothing this specification defines: its output never reaches the Player. The one criterion addressed to it (ADS-1) is a limit on what may be held against it. |
| APS | The resolution document it returns, and its answer to a resolution request. It is the only artefact on the path to the Player that this specification defines, so conformance is never checked against the ADS's internal decision document. |
| Player | Its observable behaviour on a given main MPD, resolution document and viewer action. |
| This document | Its own text. A criterion labelled `DOC` binds this specification — what it must or must not contain — and is checked by reading it, not by observing a session. |

**Whom a Player obligation binds.** Every `PLY` criterion binds a Player
conformant to this specification. The base specification does not govern
Player behaviour (§1.4), so nothing here obliges a Player that does not
implement this specification; what such a Player does is guaranteed by the
placement of each construct (§4.7), which is a property of the document and
not a promise about the Player.

**The invariant every criterion is subordinate to.** Applying this
specification MUST NEVER break primary-content playback. When an
opportunity cannot be honoured, the Player skips it and continues; when an
accepted ad fails, the Player abandons it and continues.

### 4.2 Publisher

**Declaring opportunities.**

- **PUB-1.** The Publisher MUST declare the constraints applicable to an ad
  slot — its cap, its allowed layouts, its relation to linear events, its
  once-per-session bound, its early-resolution offset — in the MPD. They are
  not inferred at runtime by the ADS, the APS or the Player.
- **PUB-2.** The Publisher MUST declare a cap (`@durationCap`, §5.1.3) on
  every overlay window and every pause window. On an inherited linear event
  the cap is the base specification's `@maxDuration`, which the Publisher
  MAY omit; an absent `@maxDuration` keeps its base meaning, *"If absent,
  the value is assumed to be infinity, in which case the current
  presentation resumes only when the alternative presentation terminates"*
  (DASH §5.16.5.2, Table 63).
- **PUB-3.** A declared cap of zero means the opportunity does not fire. On
  an inherited linear event this is the base rule, *"If the value of
  @maxDuration is zero, the event is not executed"* (DASH §5.16.5.2, Table 63);
  on an overlay or pause window a `@durationCap` of zero has the same
  meaning. A zero cap is not a very short slot.
- **PUB-4.** A Publisher declaring allowed layouts MUST use only the tokens
  of §3.4.2. Publisher-private layout names MUST NOT appear in the
  allowed-layouts declaration of a window.
- **PUB-5.** Declaring the allowed layouts on a non-linear window is
  OPTIONAL. A window that declares none admits the family default of
  §3.4.3.
- **PUB-6.** A Publisher that admits `custom` on an overlay window lists it
  in `@allowedLayouts`. It MAY also declare a custom region on the window
  (`@customRegion`, §5.3.5); with none declared, the region is the whole
  video viewport.
- **PUB-7.** All opportunity windows of one family that share a `Period`
  MUST be authored as `Event` entries inside a **single** `EventStream`.
  The base admits at most one `EventStream` per scheme-and-value pair in a
  Period — *"A Period shall contain at most one EventStream element with the
  same value of the @schemeIdUri attribute and the value of the @value
  attribute, i.e. all Events of one type shall be clustered in one Event
  Stream"* (DASH §5.10.2.1) — and the SGAI schemes carry no `@value` (PUB-8), so
  two sibling streams of one SGAI scheme in one Period are not a conformant
  document.
- **PUB-8.** An `EventStream` carrying an SGAI event scheme MUST NOT carry
  `@value`.
- **PUB-9.** The Publisher MAY declare, on an overlay or pause window, how
  far ahead of the window a Player may resolve it
  (`@earliestResolutionTimeOffset`, §5.1.3). A window that declares nothing
  may be resolved up to 60 seconds ahead, the base specification's default.
  A Publisher that wants a window resolved only when it fires declares an
  offset of zero.
- **PUB-10.** The Publisher MAY declare a pause window as once-per-session
  (`@executeOnce="true"`, §5.1.4). A window that does not carry the
  declaration yields a pause ad on every qualifying pause.
- **PUB-11.** Declaring a relation on a non-linear window is OPTIONAL. A
  window declares at most one relation, supersede or on top
  (`@linearRelation`, §5.1.6); a window that declares neither has the
  default relation.
- **PUB-12.** A Publisher that wants a non-linear ad presented during an
  alternative presentation MUST declare it either by a window in that
  alternative presentation's own MPD, or by a window of the triggering
  presentation that declares `on-top`.
- **PUB-13.** Content carrying pause windows MUST request the `PlayList`
  metric through the base specification's `Metrics` element (DASH §5.9).
  Collection is triggered by the service provider, not by the Player: *"The
  trigger mechanism is based on the Metrics element in the MPD"* (DASH §5.9.1).

**Placing what it authors.**

- **PUB-14.** Every construct of this specification the Publisher authors
  MUST be expressed through one of the extension points §4.7 enumerates:
  foreign-namespace open content (DASH §5.2.1), application-level Event Streams
  (DASH §5.10), or descriptor schemes (DASH §5.8.4.8 / DASH §5.8.4.9). It MUST NOT be
  introduced through an `@mimeType` on an `AdaptationSet` or
  `Representation` of a document reached through `ImportedMPD`, nor through
  an inline `AdaptationSet` or `Representation` of a List MPD Period.
- **PUB-15.** The Publisher's use of this specification MUST NOT alter or
  override the semantics of any construct of the base specification.
- **PUB-16.** A baseline element that a legacy Player is expected to
  process MUST be placed at a baseline position — as a sibling of an SGAI
  element, never inside one. A baseline element nested inside an SGAI
  element is authored for Players of this specification, and no legacy
  behaviour is assumed for it.
- **PUB-17.** Forms the Publisher declares MUST carry a creative whose media
  type falls under one of the three forms of §3.5.

**Content-dependent authoring for older Players.** A legacy Player skips
every construct of this specification (Annex G). For **live** content the
Publisher SHOULD treat a non-linear opportunity as an expected loss on
legacy Players: live content cannot be held to splice in a break without
losing real content. For **on-demand** content the Publisher MAY, and
SHOULD where monetising the opportunity matters, author a standard linear
break over the same span, using only base constructs, and declare on the
window that it supersedes the break (§5.1.6): a legacy Player then plays the
break, and a Player of this specification presents the window and plays the
break only when the window presents no ad. The Publisher cannot tell from
the manifest which Player a viewer has, so the fallback is authored
unconditionally.

### 4.3 ADS

- **ADS-1.** The ADS is NOT required to respect the cap when selecting
  candidates. A conformance check on the ADS MUST NOT fail solely because
  the cumulative duration of its returned candidates exceeds the cap.
- **ADS-2.** The ADS MUST decide which ads to serve and output them as its
  decision document — typically VAST, though the ADS is not bound to it.
  Enforcing the Publisher's constraints is the Player's obligation, and
  this specification places none on the ADS.
- **ADS-3.** This specification MUST NOT be read as obliging the ADS to
  maintain a device-class matrix or a per-Player capability view in order
  to produce candidates. An ADS that keeps one is conformant; one that does
  not is equally conformant.

The set of ad types, the admissible forms and the tracking schedule all
originate in the ADS's decision, but conformance to them is checked against
the APS's resolution document (§4.4), because that is the document the
Player reads.

### 4.4 APS

**Producing the resolution document.**

- **APS-1.** The APS MUST convert the ADS's decision into the resolution
  document carrying the ad candidates: a List MPD or single-period
  alternative MPD for an inherited linear event, an `<svta:OverlayList>`
  for an overlay or pause window. How it converts from the ADS's format is
  not defined by this specification.
- **APS-2.** The APS MUST answer the slot that was requested: the
  `@family` of an `<svta:OverlayList>` is that of the window whose `@uri`
  the request was issued against.
- **APS-3.** The APS MUST emit a document valid against the base schema and
  the schema of §5.10, with every construct of this specification at an
  extension point §4.7 admits.
- **APS-4.** An opportunity that resolved with no ads MUST be expressed as a
  resolution document carrying no candidates (§5.2.3), and MUST NOT be
  expressed as an error response or as a response without a body.
- **APS-5.** Each ad candidate MUST carry one or more presentation options
  (each a form plus its layout) as an ordered list, where document order is
  the preference order. How many options a candidate carries is the APS's
  decision: this specification sets no maximum, and no minimum beyond one.
- **APS-6.** An ad candidate MAY carry multiple presentation options, each
  pairing a form with an admissible layout. The options form a single
  ordered list, and their document order is the preference order the Player
  follows. An APS that wants the choice to sit with it sends exactly one
  option; the choice, and the responsibility for its suitability, then sit
  with the APS or with the ADS that returned a single option to it.
- **APS-7.** This specification MUST NOT be read as obliging the APS to
  maintain a device-class matrix or a per-Player capability view in order
  to produce candidates. An APS that keeps one, or that derives one from
  the capability parameters it receives, is conformant; one that does not
  is equally conformant.
- **APS-8.** The APS MUST NOT emit form metadata for an ad type or visual
  placement outside the tokens of §3.4.2.
- **APS-9.** The APS MUST NOT return an option whose layout is outside the
  set of allowed layouts it received on the request or, when it received
  none, outside the family default of §3.4.3 for the window's family.
- **APS-10.** Ad candidates in the resolution document MUST carry a
  creative whose media type falls under one of the three forms of §3.5.
- **APS-11.** When a non-AV form (image, HTML) is carried, the asset URL
  MUST NOT be expressed as `@mimeType` on an `AdaptationSet` or
  `Representation` reached through any path bound by IETF RFC 4337. It
  MUST be carried as foreign-namespace content (§5.3), which is one of the
  carriers §4.7.1 enumerates.
- **APS-12.** An option with layout `custom` MUST carry the overlay's
  rectangle in percent of the video viewport (`@rect`, §5.3.5), and that
  rectangle MUST lie entirely inside the region the APS received on the
  request, or inside the viewport when it received none. It MAY be smaller
  than the region; it MUST NOT extend beyond it.
- **APS-13.** The background image of a double-box layout MUST be carried as
  a composition attribute of the option (`@background`, §5.3.6), not as a
  separate presentation option.
- **APS-14.** An L-shape option MUST carry exactly one ad creative — the
  full-frame background creative — as an image, a video, or an HTML
  document. The shrunk primary content is not a creative the APS supplies;
  it is the primary content the Player shrinks.
- **APS-15.** The APS MUST tolerate the absence of any capability parameter,
  and MUST be able to produce ad candidates without receiving any of them.
  An absent parameter is undetermined; how the APS resolves an undetermined
  value is its own decision, and two APSs that resolve it differently are
  both conformant.

**Tracking, ClickThrough, metadata.**

- **APS-16.** When the resolution document carries tracking instructions,
  the APS MUST express them as DASH callback events (§5.5), with timings
  relative to the ad's presentation timeline. The APS SHOULD carry tracking
  beacons as `Event` entries of an event stream of scheme
  `urn:mpeg:dash:event:callback:2015`: in the sub-MPD of a List MPD
  candidate, and in the `<svta:Tracking>` element of an `<svta:Ad>`. The
  APS produces these entries by translating the tracking events the ADS
  declared.
- **APS-17.** When a candidate carries a ClickThrough, the ClickThrough URL
  and any click-tracking URL accompanying it MUST be carried in
  `<svta:ClickThrough>` (§5.6), and not elsewhere. Whether a ClickThrough
  has click-tracking URLs is the advertiser's decision.
- **APS-18.** The APS MAY carry creative metadata in the elements of §5.7;
  emitting them is optional.

**Declarations on the resolution document.**

- **APS-19.** The APS MUST declare, for each slot it resolves, whether the
  viewer may dismiss it (§5.2.4). A resolution document that does not
  declare it leaves the slot non-dismissible: the capability is granted and
  never assumed.
- **APS-20.** Where dismissal is allowed, the APS MUST declare the number of
  seconds that MUST elapse, from the moment the slot begins rendering,
  before the viewer may dismiss it. A declared delay of zero means the slot
  is dismissible immediately.
- **APS-21.** Where a resolution may have been obtained ahead of the
  opportunity, the APS MUST declare how long that resolution remains usable
  (`@validFor`, §5.2.5). A resolution document that does not declare it
  remains usable for as long as its window lasts.
- **APS-22.** A resolution document for a pause window MUST declare which
  exhaustion behaviour applies — `repeat`, `request-again` or `stop`
  (`@onExhausted`, §5.2.6).

### 4.5 Player

#### 4.5.1 Validating and rendering

- **PLY-1.** The Player MUST validate the candidates of a resolution
  document against the constraints the Publisher declared, and render only
  those that satisfy them. Any client-side criterion it adds (ranking,
  deduplication) operates inside the validated subset.
- **PLY-2.** The Player MUST be able to operate regardless of whether the
  ADS uses VAST: it reads only the resolution document.
- **PLY-3.** A Player on any device class MUST produce a defined behaviour —
  render, fall back, or skip — for every opportunity type this
  specification defines. Undefined behaviour is non-conforming. Chapter 7
  gives the behaviour per class.
- **PLY-4.** The Player MUST NOT attempt to render a form (video, image,
  HTML) that its device class cannot render.
- **PLY-5.** The Player MAY skip a candidate whose creative media type is
  outside §3.5; such a candidate signals a non-conformant ADS, APS or
  Publisher.

#### 4.5.2 Resolving an opportunity

- **PLY-6.** On an overlay window, the Player MUST NOT resolve earlier than
  the offset — declared, or the default of 60 seconds — before the start of
  the window.
- **PLY-7.** On a pause window, the Player MUST NOT resolve earlier than the
  offset — declared, or the default of 60 seconds — before the start of the
  window. The offset is computed against the start of the window and never
  against the pause, which has no authored time.
- **PLY-8.** Resolving early is a permission and never an obligation. A
  Player that resolves only when the opportunity fires is conformant,
  whatever offset the window carries.
- **PLY-9.** When the opportunity fires, the Player MUST check whether the
  resolution it holds is still usable (§5.2.5). If it is not, the Player
  MUST request a new one and MUST NOT present candidates from the expired
  resolution.
- **PLY-10.** When a re-resolution yields no usable candidate, the Player
  MUST treat it as a resolution carrying no candidates and MUST NOT fall
  back on the expired one.
- **PLY-11.** The Player MUST request a resolution document when a viewer
  pause begins inside a pause window, and MUST NOT request one for a pause
  that begins outside every such window. The pause window bounds where a
  pause produces an ad, not how long the resulting slot lasts: that is set
  by the viewer.
- **PLY-12.** Sending a capability parameter is OPTIONAL. A Player MAY send
  all of them, some of them, or none; which travel is its decision, taken
  at runtime, and no declaration by the Publisher, the APS or the ADS is
  needed first.
- **PLY-13.** When the Player has no value for a capability parameter, or
  does not disclose it, the Player MUST omit that parameter entirely rather
  than send it with an empty or placeholder value.
- **PLY-14.** A parameter the Player adds that is not one of the reserved
  names of §5.8 MUST carry a vendor-specific prefix (§5.8.4), so that
  reserved names added by a later edition cannot collide with it.
- **PLY-15.** When the window declares allowed layouts, the Player MUST send
  the declared set, unchanged, on the resolution request (§5.8.3). When the
  window declares none, nothing is sent, and the set that binds the APS and
  the Player is the family default.
- **PLY-16.** When the window declares a custom region, the Player MUST send
  it on the resolution request together with the allowed layouts, as §5.8.3
  defines.

#### 4.5.3 Selecting a presentation option

- **PLY-17.** The Player MUST evaluate the presentation options of an
  accepted candidate **in document order**, and render the **first** option
  whose form and layout it can satisfy on its device.
- **PLY-18.** The Player MUST resolve option selection by walking the
  options in document order and checking each against (a) its device's
  capabilities and (b) the layouts the window admits — the declared
  `@allowedLayouts`, or the family default when none is declared. It renders
  the first option that satisfies both; an option that fails either MUST NOT
  be rendered, and the Player moves to the next option.
- **PLY-19.** Before rendering, the Player MUST check that the option it
  selects uses a layout the window admits, and MUST NOT render it otherwise.
  Forwarding the set to the APS does not remove this check, and neither does
  an option the APS computed from the Player's own capability parameters.
- **PLY-20.** If no option of a candidate satisfies PLY-18, the Player MUST
  skip that candidate and fall through to the next candidate in document
  order; when the candidates are exhausted, the Player MUST continue with
  the primary content.
- **PLY-21.** Before rendering a `custom` option, the Player MUST check that
  its rectangle lies inside the window's custom region (or the viewport when
  none is declared), and MUST NOT render it otherwise; the option is then not
  renderable and the Player moves to the next one. A Player that does not
  support `custom` treats every `custom` option as not renderable.
- **PLY-22.** A double-box option whose ad is a **video** needs two
  concurrent video decoders plus an image surface for the background, and
  MUST NOT be selected on a single-decoder device. A double-box option whose
  ad is an image or HTML needs one decoder, a surface for the ad and an
  image surface for the background. A non-video element — the ad when it is
  an image or HTML, or the background image — MUST NOT be selected on a
  device that cannot composite that surface type over video.
- **PLY-23.** The decoder-and-surface budget of an L-shape is driven by the
  media type of its full-frame creative. The shrunk primary content always
  consumes one decoder. A **video** creative consumes a second one, so the
  L-shape is not satisfiable on a single-decoder device. An **image or
  HTML** creative consumes a surface of that type; an image or HTML
  full-frame creative MUST NOT be selected on a device that cannot
  composite that surface type together with video.

#### 4.5.4 Enforcing the cap

The cap is one Publisher declaration that bounds different things by
family, because the base specification makes it so.

| Slot | Cap | What it bounds |
|---|---|---|
| Inherited replacement (`ReplacePresentation`) | `@maxDuration` | **Until when.** With `@clip` at its default `"true"`, *"the alternative presentation shall terminate at the latest at time PRT + APDmax"* (DASH §5.16.4, Table 62): a late start shortens the ad instead of moving the end. With `@clip="false"` it terminates at PRTA + APDmax. |
| Inherited insertion (`InsertPresentation`) | `@maxDuration` | **How long.** Insertion stops the primary timeline and resumes it at RT = PRTA (DASH §5.16.2.2.1, step 5; Table 57), so there is no scheduled end to preserve: the cumulative duration of what plays. `@clip` does not exist on insertion. |
| Overlay window | `@durationCap` | The cumulative duration of what the window presents. |
| Pause window | `@durationCap` | The cumulative duration of **one pass** through the candidates of one resolution document. It does not bound the pause slot, which lasts as long as the viewer stays paused (PLY-32). |

- **PLY-24.** Where the cap bounds cumulative duration — overlay windows,
  one pass of a pause resolution document, and linear insertion — the
  Player MUST stop rendering once the cumulative duration of the accepted
  candidates would exceed it, even if the stop falls mid-ad.
- **PLY-25.** The Player MUST NOT extend a slot beyond what the cap bounds
  for that slot's family, regardless of ADS metadata or candidate count. On
  a replacement slot the bound is the scheduled end, so an event declaring
  `@clip="false"` ends later than that end without violating this
  criterion: it is the base specification moving the bound.
- **PLY-26.** When the actual rendered length of an accepted candidate
  exceeds its declared duration, the Player MUST enforce the cap against
  actual length, not declared length ("trim during play").
- **PLY-27.** On an inherited replacement slot, the Player MUST honour the
  base clip semantics: unless the event declares otherwise, the presentation
  ends at the scheduled end of the slot, and a late start shortens it rather
  than moving that end.
- **PLY-28.** The cap is stated in the units of the parent
  `EventStream@timescale`; a candidate's declared duration is an
  `xs:duration`. The Player MUST convert the candidate's duration into the
  cap's timescale before comparing the two, and MUST round the converted
  value **up** to the next whole unit of that timescale. A candidate whose
  converted duration equals the cap exactly is admitted.
- **PLY-29.** An overlay or pause window carrying no `@durationCap` is not a
  window this specification defines. The Player MUST NOT present ads from
  such a window and MUST continue with the primary content; reading the
  absence as an unbounded default is not admissible. An inherited linear
  event with no `@maxDuration` is outside this criterion: the Player
  executes it with its base semantics.
- **PLY-30.** A cap of zero means the opportunity does not fire (PUB-3).
- **PLY-31.** The Player MUST compute the cap on the presentation timeline.
  An interval during which the presentation timeline does not advance MUST
  NOT accrue against the cap, so a form suspended while the viewer is paused
  resumes with the remaining cap it had when it was suspended.
- **PLY-32.** The Publisher-declared cap MUST NOT be interpreted as bounding
  the duration of a pause slot. It bounds an end on a replacement slot and a
  cumulative duration elsewhere; on a pause slot there is no authored
  duration for it to bound, and PLY-24 applies to one pass of a document,
  not to the pause.

Overflow policies other than stopping at the bound — skip the break
entirely, trim at the previous ad boundary, fail closed — are not defined by
this edition. `@clip` is the base's own policy for a late replacement and is
honoured as such.

#### 4.5.5 Honouring the order of candidates

- **PLY-33.** Given a resolution document with more than one candidate, the
  Player MUST play the candidates in the order the resolution document
  declares, except for candidates dropped under PLY-34 or PLY-35.
- **PLY-34.** The Player MAY drop a candidate that has no form renderable on
  its device.
- **PLY-35.** The Player MAY drop a candidate before playback ("drop before
  play") when its declared duration would push the cumulative slot duration
  past the cap.
- **PLY-36.** The Player MUST NOT re-order, deduplicate, or otherwise
  rearrange the remaining candidates after applying PLY-34 or PLY-35.
- **PLY-37.** If a candidate is accepted and its actual rendered length
  exceeds the cap, the Player MUST trim it mid-rendering ("trim during
  play").

Drop-before-play on declared duration is permitted; trim-during-play on
actual length is mandatory. The base specification trims rather than drops
(*"For insertion events, APDA = min(APD, APDmax)"*, Table 57); dropping a
List MPD Period before play is this specification's permission.

#### 4.5.6 The fallback chain across overlapping windows

- **PLY-38.** When opportunity windows of one family overlap in time within
  a presentation, the Player MUST select the first overlapping window
  (PLY-40) and attempt to resolve it. An attempt **on a window** that does
  not produce an ad is a failed execution, and on a failed execution the
  Player MUST attempt the next overlapping window of the same family. For
  the linear family this is the base rule: *"If execution fails, steps a-c
  above are repeated for next events in QE, until: — Execution succeeds, or
  — PRT of the topmost event in the queue is in the future (i.e. PRT > PHP),
  or — The queue is empty."* (DASH §5.16.2.2.5, step 2 d). For the non-linear
  families, which the base execution model does not reach, this
  specification extends the same rule.
- **PLY-39.** The Player MUST treat the four ways an attempt can fail
  alike, each mapping to a condition of DASH §5.16.2.2.6:

  | The attempt | Base condition |
  |---|---|
  | The APS does not respond, or the request fails at the transport level. | *"Alternative MPD is unavailable or invalid"* — unavailable. |
  | The response carries a final HTTP status other than `200`. | The same: nothing was obtained. |
  | The response is a `200` whose body is not a resolution document the Player can parse. | *"Alternative MPD is unavailable or invalid"* — invalid. |
  | The response is a well-formed resolution document that carries no candidates (§5.2.3). | *"Alternative MPD is a List MPD, and merge process resulted in no available media"*. |

  When every overlapping window of the family has been attempted and none
  produced an ad, the Player MUST continue with the primary content
  uninterrupted: *"If no event can be successfully executed, the playback
  continues uninterrupted"* (DASH §5.16.2.2.5). Where the Publisher declared no
  fallback window, that is the behaviour after the single attempt.
- **PLY-40.** The Player MUST order overlapping windows of one family by
  presentation time, oldest first. Where two windows carry the same
  presentation time, the Player MUST take them in the order in which they
  appear inside the `EventStream`. For the linear family this is the base
  queue, *"ordered by the presentation time PRT"* (DASH §5.16.2.2.2) and processed
  *"from oldest PRT to the most recent"* (DASH §5.16.2.2.5); it is not document
  order. The tie-break by document position is this specification's, and it
  is extended with the rest of the rule to the non-linear families.
- **PLY-41.** A resolution document carrying candidates is **not** a failed
  execution, whatever the Player then does with them. A candidate skipped
  because the device can satisfy none of its options ends at the primary
  content (PLY-20), not at the next window. The one exception is PLY-42.
- **PLY-42.** A resolution document whose `@family` does not match the
  window that requested it is not a resolution of that window. The Player
  MUST treat it as a failed execution, MUST NOT present any of its
  candidates in the slot, and MUST continue down the chain of PLY-38 to the
  next overlapping window of the window's family.
- **PLY-43.** The Player MUST bind the candidates each window of a fallback
  chain serves with **that window's own** declarations — its allowed
  layouts, its custom region and its cap. The Player MUST NOT apply the
  declarations of the window it stands in for. A declaration belongs to the
  window that carries it.
- **PLY-44.** A resolution carrying no candidates MUST NOT count as an
  execution of the opportunity. Where the opportunity is an inherited event
  with `@executeOnce="true"`, it remains executable afterwards: *"The counter
  E.c has not been incremented due to the failure, consequently if E.c = 0
  the event can still be executed in the future even if the value of
  @executeOnce is "true""* (DASH §5.16.2.2.6, NOTE 3).

#### 4.5.7 One non-linear form at a time, in sequence

- **PLY-45.** At any instant, the Player MUST keep at most **one**
  non-linear ad form active on the screen. The Player MUST NOT present two
  or more non-linear ad forms simultaneously. The bound exists so the device
  never needs more than the primary content plus one ad form's decoder.
- **PLY-46.** When the resolution document of a non-linear window declares
  more than one candidate, the Player MUST present them in sequence, in the
  order they appear in the document, each starting when the previous one
  ends. Each candidate contributes the one option the Player selected for
  it; the alternatives inside a candidate are not part of the sequence.
- **PLY-47.** The Player MUST enforce the window's cap against the
  cumulative duration of the sequence of non-linear candidates it presents,
  trimming or dropping per PLY-24 to PLY-37.

The in-slot sequence (PLY-46) and the fallback chain (PLY-38) are
independent: the chain selects which window is served; the sequence governs
the candidates inside the selected window's resolution document.

#### 4.5.8 The window's relation to inherited linear events

The base specification carries advertising and blackouts through the same
alternative-presentation events (*"for applications such as pre-roll and
mid-roll advertisement, as well as blackouts"*, DASH §5.16.1), and neither event
scheme gives `EventStream@value` a value space that could tell them apart
(*"This value is currently not required"*, Table 59; *"This value is
currently not used"*, Table 61). Whether an alternative presentation is an
ad is not observable by a Player, and no rule here depends on it. Whether one
is **active** is observable, and the window declares what follows from it.

- **PLY-48.** When a window declares **supersede**, the Player MUST present
  the window and MUST NOT execute the inherited linear events whose
  presentation time falls within its span. When the window presents no ad —
  every attempt to resolve it is a failed execution (PLY-38, PLY-39), or the
  device can render none of its candidates (PLY-20) — the Player MUST execute
  those events as the base specification defines, including its rules for an
  execution that starts after an event's presentation time (§7.13).
- **PLY-49.** When a window declares **no relation**, the Player MUST present
  its forms only while the content of the presentation whose MPD declares
  the window is being output, and MUST execute every inherited linear event
  it overlaps with its base semantics. A form on screen when an alternative
  presentation begins ends there, and the window presents nothing further.
- **PLY-50.** When a window declares **on-top**, the Player MUST present it
  also while an alternative presentation that starts within its span is
  active, composited over that presentation, within the device's capability
  and PLY-45. The inherited linear event executes with its base semantics.
- **PLY-51.** The Player MUST process the non-linear windows declared in an
  alternative presentation's MPD as that presentation's own: they are
  presented over its content, and PLY-48 to PLY-50 apply to them against the
  alternative presentations it triggers in turn.

#### 4.5.9 Cross-family priority during a pause

- **PLY-52.** While the viewer is paused inside a pause window and an
  overlay is active, the Player MUST render the pause ad and MUST suspend
  the overlay's rendering. This holds whether the pause ad is fullscreen or
  partial: during the pause the pause ad is the only ad surface visible.
- **PLY-53.** On resume, the Player MUST dismiss the pause ad and MUST
  restore the overlay if the overlay window is still active.
- **PLY-54.** If the overlay window expired during the pause, the Player MUST
  keep the overlay surface clear on resume; the overlay is over.
- **PLY-55.** When a viewer pause begins inside a pause window applicable to
  the presentation being output while a linear ad occupies the screen, the
  Player MUST present the pause ad and MUST suspend the linear ad, and MUST
  resume the linear ad from where it was suspended when the viewer resumes.
  The pause ad is dismissed on resume (PLY-57). A pause window is applicable
  to a linear ad when it is declared in that ad's own MPD (PLY-51) or when it
  is a window of the triggering presentation that declares `on-top`
  (PLY-50).

No construct lets the Publisher, the ADS or the APS invert this priority.

#### 4.5.10 The pause family

- **PLY-56.** A Player MAY implement a pause by any mechanism that suspends
  the primary content and later resumes it from the position at which it was
  suspended, including one that releases the primary content's decoding
  resources for the duration of the pause.
- **PLY-57.** Upon a pause-to-play transition by the viewer, the Player MUST
  remove any rendered pause ad from the screen within one rendering frame.
- **PLY-58.** Upon the same transition, the Player MUST cease firing the
  tracking beacons scheduled for the dismissed pause ad; beacons scheduled
  after the transition fall outside its active window.
- **PLY-59.** On resume, the Player MUST continue the primary content from
  the position at which it was suspended. A mechanism that cannot restore
  that position is not a pause under this specification, whatever it is
  called.
- **PLY-60.** When the viewer resumes, the Player MUST return to the primary
  content immediately, whether or not an ad is mid-presentation.
- **PLY-61.** The Player MAY present a pause ad fullscreen, occupying the
  entire screen, or as a partial overlay composited over the paused primary
  frame; which one applies is a property of the layout the Player selects
  (`pause-fullscreen`, `pause-partial`). When the pause ad is fullscreen,
  the Player MAY release the resources held by the primary content and by
  any pre-existing overlay to present a fullscreen video, image or web page.
  When it is partial, the Player MUST keep at most one non-linear form
  active during the pause: any coexisting overlay is suspended while the
  pause ad is shown.
- **PLY-62.** In live content, while the viewer is paused inside a pause
  window, the Player MUST keep its presentation time frozen inside that
  window for the full duration of the pause, regardless of the live edge
  advancing in wall-clock time. Any decision to resume at the live edge MUST
  be treated as a Player action occurring after the resume from pause,
  outside the pause window.
- **PLY-63.** On a window declared once-per-session, the Player MUST present
  at most one pause ad for that window for the duration of the session. A
  later qualifying pause inside the same window MUST leave the primary
  content uninterrupted.
- **PLY-64.** The Player MUST treat such a window as consumed when a pause ad
  **begins rendering**, and not when the pause occurs. A pause that resolves
  to no renderable candidate MUST leave the window available. This is the
  base specification's counter rule — E.c counts executions that
  *"successfully started"* (Table 58) — restated for a trigger that is the
  viewer and not the playhead.

#### 4.5.11 Candidates exhausted inside a pause

- **PLY-65.** When the candidates of a pause resolution document are
  exhausted while the viewer is still paused, the Player MUST apply the
  behaviour the document declares (§5.2.6). Absent the declaration, the
  Player MUST apply `stop`. The fall-through to primary content of PLY-20
  does not apply: the primary content is paused.
- **PLY-66.** Under `request-again`, a resolution document carrying no
  candidates MUST be treated as `stop` for the remainder of that pause.

Whether a second resolution request within one pause is the same
opportunity or a new one is out of scope. The two readings are identical at
the Player — it requests, renders what arrives, and stops on resume — and
differ only in accounting between the APS and the ADS, which this
specification does not observe. What it does measure, how much of the paused
interval carried an ad (§5.9), is the same under both.

#### 4.5.12 Playback speed

- **PLY-67.** The Player MUST render every ad form, linear or non-linear, at
  the same playback speed as the primary content at the moment the ad is
  presented.
- **PLY-68.** The Player MUST NOT force an ad to 1x when the primary content
  is playing at a different speed.
- **PLY-69.** The Player MUST compute a form's wall-clock on-screen duration
  as `duration / playback_speed`, not as the raw `duration`. Cap
  enforcement and beacon scheduling operate on the presentation-timeline
  `duration`.
- **PLY-70.** A form's declared duration is a value on the presentation
  timeline for every form, including those with no intrinsic media (image,
  HTML). The Player MUST derive the wall-clock length of such a form as
  `duration / playback_speed`, exactly as for a video.

#### 4.5.13 Composition

- **PLY-71.** The Player MUST composite the primary content and the ad as
  the two boxes of a double-box layout. When the option carries a
  background image, the Player MUST place it in the uncovered bands; when it
  carries none, the uncovered region renders black.
- **PLY-72.** The Player MUST composite the two elements of an L-shape — the
  full-frame creative in the background and the shrunk primary content on
  top of it — with the creative covering the whole frame and the primary
  content scaled into the region its layout token names (§3.4.2).
- **PLY-73.** Spatial arrangement inside a layout is rendered with HTML5 /
  CSS primitives; the Player composites an `overlay-corner` creative over
  primary content it does not transform, and the corner follows from the
  creative.

#### 4.5.14 Viewer dismissal

- **PLY-74.** Before the declared dismissal delay has elapsed, the Player
  MUST NOT offer the viewer a way to dismiss the slot. After it has, the
  Player MUST make dismissal available for as long as the slot is on screen.
- **PLY-75.** A dismissal ends the **whole slot**. The Player MUST stop
  presenting every ad of that slot and MUST NOT advance to another ad or
  another form within it.
- **PLY-76.** A dismissed slot does not shorten the primary content. Where
  the slot bounded a region of the primary timeline, the Player MUST
  continue from where the primary content stands, and MUST NOT compress or
  skip any part of it.
- **PLY-77.** The Player MUST fire the tracking events the resolution
  document scheduled up to the moment of the dismissal, and MUST NOT fire
  those scheduled after it. A dismissal is an outcome of the presentation,
  not a failure of it.
- **PLY-78.** On a linear slot whose event carries the base specification's
  own skip declaration, written explicitly by the Publisher, the Player MUST
  honour that declaration as the base specification defines it, and it
  governs the slot (§5.2.4). The base default that applies when the event
  writes nothing is not a declaration: where neither the event nor the
  resolution document declares anything, the slot is non-dismissible. A
  Player of this specification and a base Player treat the same linear
  event the same way.

How the dismissal is offered — a control, a gesture, a remote button — is
out of scope.

#### 4.5.15 Tracking

- **PLY-79.** Given an ad accepted for rendering, the Player MUST execute the
  tracking schedule it reads from the resolution document, firing each
  beacon at its specified relative time. The ADS is the authority over the
  schedule; the Player decides neither which beacons fire nor when.
- **PLY-80.** If the cap trims the ad before a scheduled beacon's time, the
  Player MUST stop firing the remaining beacons at the trim boundary.
- **PLY-81.** The de-duplication key for in-band beacons is scoped to **the
  candidate** that carries them in an `<svta:OverlayList>`: within a
  candidate, beacons sharing an `@id`, or the same URL at the same
  presentation time, fire once, and two beacons carrying the same `@id` in
  two different candidates are two distinct beacons that the Player MUST
  fire both. On a List MPD the base scope applies unchanged: *"The scope of
  the @id for each Event is within the same @schemeIdURI and @value pair
  over the duration of the current media presentation"* (Table 44), so the
  ads of one List MPD, the streams merged from their sub-MPDs included,
  share one scope.
- **PLY-82.** The Player MUST resolve the presentation times of an
  `<svta:Tracking>` element against **that candidate's own presentation** —
  its time 0 is the instant the candidate begins rendering — and not against
  a `Period` the element does not sit in.
- **PLY-83.** A Player MUST safely ignore unknown namespaces on
  tracking-related extension elements, under the base rules for elements and
  attributes it does not recognise.

#### 4.5.16 ClickThrough and metadata

- **PLY-84.** A Player conformant to this specification MUST read the
  ClickThrough URL of `<svta:ClickThrough>` and fire its associated
  click-tracking when the viewer activates the ClickThrough. The click has
  no presentation time and is never fired from the timeline.
- **PLY-85.** Reading the metadata elements of §5.7 is optional; a Player MAY
  ignore them.

#### 4.5.17 Graceful continuation

- **PLY-86.** When resolving or rendering an accepted ad fails at runtime —
  for example a decode error, a malformed candidate, or a mid-ad network
  loss — the Player MUST abort that ad and continue playing the primary
  content uninterrupted. This matches what the base specification requires
  of its own execution model (*"A failed execution results in smooth
  continued playback of the main media presentation"*, DASH §5.16.2.2.6).
- **PLY-87.** A Player MUST ignore `@value` on an `EventStream` carrying an
  SGAI event scheme.

#### 4.5.18 Deriving the pause-delivery measurement

- **PLY-88.** A Player that reports metrics MUST derive the paused interval
  from the `PlayList` entries as §5.9 describes, and MUST NOT count a
  playback period that stopped on `Rebuffering` as a pause opportunity.

### 4.6 This document

These criteria bind this specification's own text. Each names where the
document satisfies it.

**Relationship to the base.**

- **DOC-1.** Every construct this specification introduces MUST sit at an
  extension point where removing it — as a Player that does not implement
  this specification does under the base rules for unrecognised elements
  and attributes (DASH §5.2.1) — leaves a valid MPD whose primary content plays
  uninterrupted. §4.7 shows it construct by construct.
- **DOC-2.** Every new construct MUST be expressed through foreign-namespace
  open content (DASH §5.2.1), an application-level Event Stream (DASH §5.10), or a
  descriptor scheme (DASH §5.8.4.8 / DASH §5.8.4.9). New constructs MUST NOT be
  introduced by a path that violates the chain DASH §5.3.2.6 → DASH §8.15 → DASH §7.3 →
  IETF RFC 4337 for a document reached through `ImportedMPD`, nor through an
  inline `AdaptationSet` or `Representation` of a List MPD Period. A new
  delivery format under DASH Annex F is admissible only when the construct
  genuinely requires DASH segment delivery for a format other than ISO-BMFF
  and this specification publishes a new Interoperability Point URI; no
  construct of this edition invokes it.
- **DOC-3.** This specification MUST NOT alter or override the semantics of
  any construct of the base specification. The one place where a Player of
  this specification does not execute a base event the base would execute
  is recorded in §4.8.3 with its reason.
- **DOC-4.** Where the base specification already defines a behaviour, a
  default or a construct for a question this specification has to answer,
  the base answer takes precedence: this specification adopts it and cites
  it (§4.8.1). It defines its own answer only where the base gives none,
  and declares that answer as an extension (§4.8.2). A decision that
  departs from the base answer anyway is recorded with its reason
  (§4.8.3).
- **DOC-5.** Every mechanism this specification introduces MUST be
  expressible within the four-actor contract of §1.2. A mechanism that would
  require an actor to take on a responsibility outside its role MUST be
  rejected or redesigned; the exclusion of hybrid-break linkage (§1.3) is
  one such rejection.
- **DOC-6.** Where two declarations the base specification itself provides
  are reconciled by its own rule, the base rule is adopted and the pair is
  not treated as a duplication. A Linked Period's `@duration` and its
  imported Period's `Period@duration` are such a pair: the base keeps the
  smaller of the two (DASH §5.3.2.6.3, step 3 d iii). Every other value this
  specification needs in two places has exactly one canonical declaration,
  and the others are derived from it at runtime (§5.2.2, §5.3).

**VAST.**

- **DOC-7.** This specification MUST NOT depend on any version of VAST or on
  VAST as a protocol, and MUST NOT impose VAST as a precondition for any
  actor. Conformant implementations MUST be VAST-version-agnostic.
- **DOC-8.** The normative chapters MUST NOT cite a specific VAST version as
  required.
- **DOC-9.** A normative statement MUST NOT require VAST, and MUST NOT
  describe an actor's behaviour in terms only a VAST deployment satisfies.
  VAST is named as the typical case only where the same sentence states that
  the actor is not bound to it. Field mappings, message examples and
  versions are in Annexes A.7 and C.8 and in §6.6, which are illustrative.
- **DOC-10.** This specification MUST cover the ad behaviours a VAST-based
  ADS can express, so that an APS fed by VAST can build a resolution
  document for each of them using only the semantics defined here. §6.6
  tabulates that coverage.
- **DOC-11.** An annex SHOULD carry a worked example of an APS building a
  resolution document from a VAST response. Annexes A.7 and C.8 do; they
  constrain no implementation.

**The interface.**

- **DOC-12.** This specification documents the Player-visible interface: the
  MPD event URL (served by the APS), the resolution request (§5.8), and the
  resolution document (§5.2). It does not define the request used to obtain
  the ADS's decision, nor the format of that decision. The Publisher's
  arrangement with the APS for the event URL remains bilateral, except for
  the parameters §5.8 defines.
- **DOC-13.** The capability parameters are **inputs about the device** —
  what it supports — and not conclusions about which ad experiences can be
  served; deriving the second from the first is the APS's. The set MUST be
  able to express the capability axes that distinguish the device classes
  of §3.6; §5.8.2 shows that it tells all five apart.
- **DOC-14.** A capability parameter absent from the resolution request means
  its value is undetermined — the Player did not determine it, or did not
  disclose it. Absence does not assert that the device lacks the capability.
  This specification does not define how an APS resolves an undetermined
  value.
- **DOC-15.** The forwarded allowed layouts and the forwarded custom region
  are the exceptions to the optionality of PLY-12: when a window declares
  them, the Player is required to send them (PLY-15, PLY-16). Every other
  reserved parameter remains optional. The way they travel is normative and
  defined in §5.8.3.
- **DOC-16.** Inherited linear events carry no allowed-layouts declaration,
  and the forwarding of PLY-15 does not apply to them.

**Vocabulary and forms.**

- **DOC-17.** The accepted ad-type and layout values are exactly those of
  §3.4, each mapped to its IAB definition, plus the optional `custom`. This
  specification MUST NOT accept a value outside that enumeration, and MUST
  cite the IAB source for the values it accepts (chapter 2).
- **DOC-18.** Each accepted layout implies the spatial bound the IAB
  guidelines declare for it, inherited by reference; no dimensional
  attribute is introduced on the slot declaration.
- **DOC-19.** This specification MUST enumerate the exact admissible set of
  creative carriers wherever carrier types are discussed (§3.5); new carrier
  types MUST NOT be added in annexes, examples or implementation notes.
- **DOC-20.** This specification MUST enumerate the supported device classes
  and, for each, the expected behaviour for each opportunity type (§3.6,
  chapter 7, Annexes A to Q).
- **DOC-21.** Supporting `custom` is OPTIONAL for every actor. It carries no
  IAB ad type, it is the only layout for which this specification defines a
  position, and it applies only to overlay windows.

**Layout.**

- **DOC-22.** Spatial arrangement of overlays MUST be delegated to HTML5 /
  CSS layout primitives, and this specification MUST NOT define a parallel
  layout standard for overlay placement. Position semantics inside a layout
  are out of scope; the one exception is `custom`.

**Composition rules.**

- **DOC-23.** This specification MUST NOT introduce a construct that implies
  or requires the simultaneous rendering of two or more non-linear forms.
  Sequencing inside a slot is carried by the candidates' document order and
  by no separate primitive.
- **DOC-24.** This specification carries no construct that lets the
  Publisher, the ADS or the APS invert the priority of a pause ad over an
  overlay or a linear ad.
- **DOC-25.** The rule that each window of a fallback chain binds its own
  candidates (PLY-43) MUST be carried as a normative Player obligation, not
  only in informative material; it is.
- **DOC-26.** The relation of a non-linear window to inherited linear events
  is declared on the window this specification defines (§5.1.6). This
  specification MUST NOT add anything to the inherited linear events, or to
  their `EventStream`s, to carry it: the same base event means the same
  thing to every Player.
- **DOC-27.** For the non-linear families, which the base execution model
  does not reach, this specification extends the base fallback rule and the
  base ordering rule (PLY-38, PLY-40) so that one behaviour governs every
  family.

**Tracking, ClickThrough, metadata.**

- **DOC-28.** This specification MUST specify how in-band ad tracking beacons
  are carried in the resolution document, and MUST define a mechanism that
  lets the ADS direct which beacons fire and at which points relative to the
  ad's presentation (§5.5). It prescribes no fractions, granularity or
  beacon count.
- **DOC-29.** This specification MUST NOT introduce a new tracking event
  scheme; it reuses the base callback scheme. A new tracking carrier MAY be
  introduced only when the callback scheme cannot express the required
  semantics, and only after a documented gap analysis; none is introduced.
- **DOC-30.** This specification MUST state how a resolution document
  carrying the candidate-level beacon carrier is validated (§5.10.2). A
  validation that reports such a document valid while skipping the
  foreign-namespace subtree has not checked the tracking carrier at all.
- **DOC-31.** The ClickThrough carrier is normative and defined explicitly
  (§5.6), so that every Player conformant to this specification reads it the
  same way. The guarantee is scoped to those Players and can only be scoped
  that way (§1.4).
- **DOC-32.** This specification MUST define, in the namespace
  `urn:svta:dash:sgai:2026`, the elements that carry creative metadata with
  no native DASH carrier, and MUST state that emitting them and reading them
  are both optional (§5.7).
- **DOC-33.** This specification MUST NOT define a metric of its own for
  pause-ad delivery; the quantity is derived from the base `PlayList` metric
  (§5.9). The transport by which any measurement reaches the Publisher, the
  APS or the ADS is out of scope, as it is for the base specification's own
  metrics.

**Governance.**

- **DOC-34.** Every new construct MUST be accompanied by an inline
  justification of why no existing base construct could be reused, and
  every deliberate omission of a base construct a reader might expect MUST
  be documented with the decision (§4.8).
- **DOC-35.** This specification MUST reuse existing base machinery —
  events, manifests, presentations, schemes — wherever possible. A new
  construct MUST NOT be introduced unless an existing one cannot be made to
  fit, and before introducing one this specification MUST consider whether
  an extension of an existing construct would suffice, and record the
  outcome (§4.8.2, §4.8.4).
- **DOC-36.** A construct MUST NOT carry information already determined by
  its element name and namespace, by its parent, or by another attribute of
  the same construct. A construct MUST NOT be introduced in case a future
  edition relaxes something, and a construct whose only admissible value
  matches its default, or is fixed by another rule, MUST NOT exist.
- **DOC-37.** Where this specification states an obligation of its own, it
  states the positive obligation; prohibitions the requirements it
  implements state are kept as prohibitions.
- **DOC-38.** Applying this specification MUST NEVER break primary-content
  playback.

**Names.**

- **DOC-39.** New event schemes MUST use the pattern
  `urn:svta:dash:<construct>:<year>`; constructs whose semantics change in a
  later edition MUST use a new year; chapter 2 MUST list the URIs this
  edition introduces (§2.1). Tracking beacons for ads of this specification
  MUST reuse the base callback scheme.
- **DOC-40.** Where a component is in essence the same as one already
  defined in the base specification, this specification MUST reuse the base
  construct with all its characteristics — name, default, value domain,
  units, semantics — and does not mint a new identifier for it. Where a base
  construct's default cannot be inherited, its name is not reused (§4.8.2).
- **DOC-41.** The layout names this specification accepts are the IAB's;
  it MUST reference them without inventing layout names of its own, the one
  exception being `custom`.

**Backward compatibility.**

- **DOC-42.** For every construct it introduces, this specification MUST
  answer the checklist of §4.7.2 in the construct's own entry, MUST state
  its carrier classification explicitly, and MUST NOT classify a
  Supplemental descriptor and an Essential descriptor carrier together.
  Every construct MUST have a legacy-Player test in Annex R.

### 4.7 Backward compatibility, per construct

#### 4.7.1 The base-specification facts this relies on

The placement of every construct follows from ten facts about the base
specification. They are restated here, with the clause each rests on, so
that each construct entry below can name the ones that govern it.

- **DR-1 — A document reached through `ImportedMPD` is Single-Period
  Static, and SPS constrains every Representation to IETF RFC 4337.**
  *"MPDs referenced in the ImportedMPD element shall be restricted to the
  constraints of a single period profile as defined in 8.15"* (DASH §5.3.2.6.1);
  SPS applies *"The rules for the MPD as defined in subclause 7.3"*
  (DASH §8.15.2); and DASH §7.3.1: *"The @mimeType attribute of each Representation
  shall be provided according to IETF RFC 4337."* No non-MP4 creative can sit
  on an `AdaptationSet` or `Representation` there.
- **DR-2 — Foreign-namespace open content is the extension point for new XML
  constructs.** The base schema admits `<xs:any namespace="##other"
  processContents="lax"/>` in `MPD`, `Period`, `EventStream`, `Event` and
  `AlternativeMPDEventType`, and `<xs:anyAttribute namespace="##other"
  processContents="lax"/>` on `MPD`, `Period`, `Event` and
  `AlternativeMPDEventType`; `EventStream` admits foreign elements and no
  foreign attributes (DASH §5.10.2.3), and `ImportedMPD` admits foreign
  attributes and no children (DASH §5.3.2.6.2). DASH §5.2.1 requires that removing
  them leaves a valid, conformant MPD.
- **DR-3 — A baseline element nested inside a foreign-namespace element
  carries no legacy guarantee.** DASH §5.2.1 defines the removal by namespace and
  addresses no DASH-namespace child nested inside a foreign element.
  Removing an element removes what it contains; that is ordinary XML and
  the reading this specification assumes, so a baseline element a legacy
  Player is expected to process is placed as a sibling, never inside
  (PUB-16).
- **DR-4 — DASH Annex F is informative; a new delivery format binds only through
  an Interoperability Point URI.** DASH §8.1: restrictions defined outside the
  base document are *"Interoperability Points"* signalled in
  `MPD@profiles`, and *"The owner of the URI is responsible to provide
  sufficient semantics on the restrictions and permission of this
  interoperability point"*.
- **DR-5 — The `AdaptationSet` / `Representation` axis of a List MPD is
  closed to non-MP4 media.** The List profile *"is an extension of the
  ISO-BMFF CMAF Profile"* (DASH §8.14), whose Adaptation Sets require *"The
  @mimeType shall be set to "<contentType>/mp4""* (DASH §8.12.4.3).
- **DR-6 — Four carriers exist for a non-AV asset**: (a) foreign-namespace
  open content (DASH §5.2.1); (b) an Event Stream payload (DASH §5.10); (c1) a
  `SupplementalProperty` descriptor (DASH §5.8.4.9); (c2) an `EssentialProperty`
  descriptor (DASH §5.8.4.8). Descriptors sit on `Period`, `EventStream`,
  `Event` and `AlternativeMPDEventType` as well as on `AdaptationSet`,
  `Representation` and `SubRepresentation`.
- **DR-7 — A Period of non-zero duration holds at least one Adaptation
  Set.** *"At least one Adaptation Set shall be present in each Period
  unless the value of the @duration attribute of the Period is set to
  zero."* (DASH §5.3.2.2, Table 4).
- **DR-8 — The base specification does not govern Player behaviour** (DASH §8.1,
  NOTE 1, quoted in §1.4). No construct can compel a legacy Player; the
  guarantee is a property of the document.
- **DR-9 — The two descriptors differ in what a legacy client drops.**
  *"If the scheme or the value for this descriptor is not recognized, the
  DASH Client is expected to ignore the parent element that contains the
  descriptor"* (DASH §5.8.4.8, NOTE 1), against *"… is expected to ignore the
  descriptor"* (DASH §5.8.4.9, NOTE).
- **DR-10 — `MPD@type="list"` and the List profile.** DASH §8.14 rule 1 requires
  List MPDs to declare `type="list"`, and rule 2 the profile URN
  `urn:mpeg:dash:profile:list:2024`; the profile is *"intended for use in
  conjunction with the Alternative MPD event"*. DASH §5.3.1.4 also defines the
  type on its own: *"For Media Presentations with MPD@type set to "list" the
  constraints of a static Media Presentation shall apply."*

**The legacy expectation for unknown event schemes.** The base clusters
events by scheme so that a client can *"subscribe to an Event Stream of
interest and ignore Event Streams that are of no relevance or interest"*
(DASH §5.10.1): a client that does not implement a scheme ignores its stream.

#### 4.7.2 The checklist

Each construct entry below answers the same eight questions: (1) where the
construct lives; (2) which extension point and which DR facts govern its
removal; (3) what a legacy Player does with it, step by step; (4) whether any
required sibling or parent attribute changes meaning when it is present, and
whether removing it still leaves a document that parses and plays; (5) the
legacy test in Annex R; (6) its namespace; (7) confirmation that the
checklist is answered; (8) its carrier classification — (a), (b), (c1) or
(c2) of DR-6. An unanswered item blocks publication.

#### 4.7.3 C1 — The overlay window

1. **Placement.** An `EventStream` element, child of `Period`, with
   `@schemeIdUri="urn:svta:dash:sgai-overlay:2026"`, holding `Event`
   elements; each `Event` holds exactly one `<svta:OverlayPresentation>`
   child element (§5.1.3). Optional in the Period.
2. **Extension point.** The `EventStream` is an application-level Event
   Stream (DASH §5.10); the child element is foreign-namespace open content of
   `Event` (DR-2). DR-3 governs anything nested in it: nothing baseline is.
3. **Legacy walk-through.** (i) The parser meets the `EventStream` while
   reading the Period. (ii) It does not implement the scheme and ignores the
   stream (DASH §5.10.1); a client that removes foreign-namespace content first
   drops the `<svta:OverlayPresentation>` and is left with a well-formed
   `Event` of an unknown scheme. No error is raised. (iii) The rest of the
   Period parses unchanged. (iv) Playback of the primary content continues;
   no request is issued to the window's `@uri`, which the legacy Player never
   sees as a URL to fetch.
4. **Sibling check.** No base element or attribute changes meaning in its
   presence. The `@linearRelation` of the window binds only a Player of this
   specification; the inherited linear events it names are untouched
   (DOC-26). Removing the stream leaves a valid Period that plays.
5. **Legacy test.** R-BC-1.
6. **Namespace.** `urn:svta:dash:sgai:2026` for the element; the scheme URI
   follows `urn:svta:dash:<construct>:<year>`.
7. **Checklist answered:** yes.
8. **Carrier.** (b) Event Stream for the window, carrying (a)
   foreign-namespace content for its declarations. No descriptor is used.

#### 4.7.4 C2 — The pause window

1. **Placement.** An `EventStream` child of `Period` with
   `@schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026"`, its `Event`
   elements each holding one `<svta:PauseAdPresentation>` (§5.1.4).
2. **Extension point.** As C1: (b) with (a), DR-2, DR-3.
3. **Legacy walk-through.** As C1. The legacy Player's pause is an ordinary
   pause; it requests nothing.
4. **Sibling check.** The `Metrics` element the Publisher adds for pause
   delivery (§5.9) is a base construct a legacy Player may use as the base
   defines; it changes no other element. Removing the stream leaves a valid
   Period.
5. **Legacy test.** R-BC-2.
6. **Namespace.** As C1.
7. **Checklist answered:** yes.
8. **Carrier.** (b) with (a).

#### 4.7.5 C3 — Extension content in a List MPD

1. **Placement.** In a List MPD returned for an inherited linear event:
   `<svta:ClickThrough>` and the metadata elements of §5.7 as children of a
   `Period`, siblings of its `ImportedMPD`; the `svta:dismissAfter`
   attribute on the `MPD` element (§5.2.1, §5.2.4).
2. **Extension point.** Foreign-namespace open content of `Period` and a
   foreign attribute of `MPD` (DR-2). The Linked Period merge keeps them:
   among what survives it are *"any elements from a different namespace"*
   (DASH §5.3.2.6.3, step 3 b ix).
3. **Legacy walk-through.** (i) A legacy Player that implements the base
   linear path fetches the List MPD and meets the elements while reading
   each Period. (ii) It removes them under DASH §5.2.1 without error. (iii) The
   `ImportedMPD` sibling is untouched and is resolved as the base defines.
   (iv) The ad plays; the ClickThrough is inert, and dismissal follows the
   base `@skipAfter` of the event.
4. **Sibling check.** `ImportedMPD`, `Period@duration` and the callback
   `EventStream` of the sub-MPD keep their base meaning. Removing the
   elements leaves a valid List MPD.
5. **Legacy test.** R-BC-3.
6. **Namespace.** `urn:svta:dash:sgai:2026`.
7. **Checklist answered:** yes.
8. **Carrier.** (a).

#### 4.7.6 C4 — The non-linear resolution document

1. **Placement.** A standalone XML document, root element
   `<svta:OverlayList>`, returned by the APS for an overlay or pause window
   (§5.2.2). It is not an MPD and is not embedded in one.
2. **Extension point.** It is reached only through a window's `@uri`, which
   only a Player of this specification resolves. Inside it, the
   `<svta:Tracking>` element reuses the base `EventStreamType` whole; the
   video form of an option references an SPS sub-MPD by URL, which is a
   base document.
3. **Legacy walk-through.** (i) A legacy Player never parses it: it ignored
   the window that points to it (C1, C2). (ii)–(iv) do not arise; the
   primary content plays.
4. **Sibling check.** No base document refers to it; nothing base changes
   meaning. The sub-MPDs it references are ordinary SPS MPDs.
5. **Legacy test.** R-BC-4 (the legacy Player issues no request to the
   window's `@uri`).
6. **Namespace.** `urn:svta:dash:sgai:2026`.
7. **Checklist answered:** yes.
8. **Carrier.** (a): every non-AV asset URL is an attribute of a
   foreign-namespace element (`<svta:RenderableAsset>`); no descriptor and
   no `AdaptationSet` carries one.

#### 4.7.7 C5 — The resolution request parameters and the request-type URN

1. **Placement.** Reserved query parameters on the resolution request
   (§5.8.2, §5.8.3); the request-type URN `urn:svta:dash:sgai-resolution:2026`
   as a key in `RequestParam@includeInRequests` (§5.8.1).
2. **Extension point.** The query parameters are not in any MPD. The URN is
   the base's own extension point for request types: *"a URN or tag URI,
   where the request type semantics is understood by the client and
   specified by the URN / tag URI owner. The client shall drop unknown URIs
   from the @includeInRequests and @includeInHeaders strings prior to
   processing them as specified in this Annex."* (DASH Annex I.3.6, Table I.4).
3. **Legacy walk-through.** (i) A legacy Player that implements DASH Annex I.3
   reads the `RequestParam`. (ii) It drops the unknown URN from
   `@includeInRequests`, as the base instructs. (iii) The remaining keys are
   processed as usual. (iv) No request of this specification is issued.
4. **Sibling check.** Other keys of the same `RequestParam` keep their
   meaning. A `RequestParam` whose only key is the URN applies to no base
   request once the URN is dropped.
5. **Legacy test.** R-BC-5.
6. **Namespace.** The URN follows `urn:svta:dash:<construct>:<year>`; the
   reserved parameter names carry the prefix `sgai-` (§5.8.4).
7. **Checklist answered:** yes.
8. **Carrier.** Not an asset carrier; not a document construct.

#### 4.7.8 Aggregated audit

| Construct | Placement | Extension rule | Walk-through | Sibling check | Legacy test | Namespace | Carrier | Status |
|---|---|---|---|---|---|---|---|---|
| C1 Overlay window | `Period` / `EventStream` / `Event` / `<svta:OverlayPresentation>` | DASH §5.10 Event Stream; DASH §5.2.1 (DR-2, DR-3) | §4.7.3 | OK | R-BC-1 | SVTA | (b) + (a) | OK |
| C2 Pause window | `Period` / `EventStream` / `Event` / `<svta:PauseAdPresentation>` | DASH §5.10; DASH §5.2.1 (DR-2, DR-3) | §4.7.4 | OK | R-BC-2 | SVTA | (b) + (a) | OK |
| C3 List MPD extension content | `Period` children; `MPD` attribute | DASH §5.2.1; DASH §5.3.2.6.3, step 3 b ix (DR-2) | §4.7.5 | OK | R-BC-3 | SVTA | (a) | OK |
| C4 `<svta:OverlayList>` | Standalone document | Reached only through C1 / C2 | §4.7.6 | OK | R-BC-4 | SVTA | (a) | OK |
| C5 Request parameters, request-type URN | Resolution request; `RequestParam@includeInRequests` | DASH Annex I.3.6 | §4.7.7 | OK | R-BC-5 | SVTA / `sgai-` | — | OK |

**Anti-patterns rejected.** No construct of this edition places a mandatory
element where the base declares a required field with no extension hook,
reuses a base element name with new semantics, depends on a sibling a legacy
Player cannot interpret without a fallback it can execute, uses a scheme URI
without a year, places a non-MP4 `@mimeType` on an `AdaptationSet` or
`Representation` reached through `ImportedMPD` or inside a List MPD Period,
or wraps a non-MP4 payload in an `application/mp4` Representation to satisfy
IETF RFC 4337.

### 4.8 Justifications: what is reused, what is introduced, what departs

#### 4.8.1 Reused unchanged

| Need | Base construct adopted | Clause |
|---|---|---|
| Linear slots, their cap, clip, resumption | `InsertPresentation`, `ReplacePresentation`, `@maxDuration`, `@clip`, `@returnOffset`, `@startWithOffset`, RT | DASH §5.16.3–DASH §5.16.5; Tables 57, 62, 63 |
| Linear once-only, seek blocking, skip | `@executeOnce`, `@noJump`, `@skipAfter` on the inherited events | Table 63 |
| Linear resolution document | List MPD with Linked Periods and `ImportedMPD`, SPS sub-MPDs | DASH §8.14, DASH §5.3.2.6, DASH §8.15 |
| Candidate duration on a List MPD | Linked Period `@duration` reconciled with the imported `Period@duration` by the base rule (the smaller wins) | DASH §5.3.2.6.3, step 3 d iii |
| Window span | `Event@presentationTime`, `Event@duration`, `EventStream@timescale`, `Event@id` | Tables 43, 44 |
| Fallback and ordering | The execution queue ordered by PRT, fall-through on a failed execution, continued playback when none succeeds | DASH §5.16.2.2.2, DASH §5.16.2.2.5 |
| Empty resolution | A failed execution that does not increment E.c | DASH §5.16.2.2.6 and NOTE 3 |
| Early resolution on a window | `@earliestResolutionTimeOffset`: same name, units of `EventStream@timescale`, default 60 seconds — *"specifies the time interval (in units of EventStream@timescale) prior to the Event@presentationTime during which the MPD described in the @uri attribute may be requested. The default is 60 seconds in units of timescale"* | Table 63 |
| Once-per-session on a pause window | The name `@executeOnce` and the counter rule (E.c increments when playback *"successfully starts"*) | Tables 58, 63; DASH §5.16.2.2.6 |
| Tracking | Callback scheme `urn:mpeg:dash:event:callback:2015` with `EventStream@value="1"` and the URL as event value; the `EventStreamType` for the candidate-level carrier | DASH §5.10.4.5, Table 47; DASH §5.10.2.3 |
| Publisher parameters on the non-linear request | `RequestParam` of DASH Annex I.3, with a request type identified by a URN | DASH Annex I.3.6, Table I.4 |
| Pause-delivery measurement | `PlayList` metric and the `Metrics` trigger | DASH Annex D.4.6, Table D.5; DASH §5.9.1 |
| The `custom` rectangle's notation | The SRD convention: origin top-left, x to the right, y downward, width and height in a reference space; containment as *"the sum of object_x and object_width is smaller or equal to total_width"* | DASH Annex H.2.2, Table H.1 |

#### 4.8.2 Introduced, and why nothing existing fits

| Construct | Why no base construct could be reused, or extended |
|---|---|
| Event schemes `urn:svta:dash:sgai-overlay:2026` and `urn:svta:dash:sgai-pause-trigger:2026` | The base has one ad tool and it is a switch: an alternative presentation *"replaces the main Media Presentation at a certain point on the media timeline"* (DASH §5.16.1), and nothing composites two outputs. Reusing the alternative-MPD schemes would give them a second meaning only a Player of this specification reads. The base has no pause trigger: *"Events are timed, i.e. each event starts at a specific media presentation time"* (DASH §5.10.1). |
| `<svta:OverlayPresentation>`, `<svta:PauseAdPresentation>` | Modelled on `InsertPresentation` / `ReplacePresentation`, which are child elements of `Event`; `EventType` admits foreign children (DASH §5.10.2.3). `AlternativeMPDEventType` itself is not reused because its `@maxDuration` defaults to infinity and a window's cap cannot (below). |
| `@durationCap` | `@maxDuration` exists and bounds the same kind of thing, but its default is *"infinity"* (Table 63). A window without a cap is not a window this specification defines (PLY-29), and the naming rule reuses a base construct only with all its characteristics, default included (DOC-40). A new name is therefore the honest one; it keeps the base's units. |
| `@allowedLayouts` | The base has no ad-form or layout vocabulary. It is a list of single-valued tokens, so it is one attribute carrying a space-separated list, as the base's `@dependencyId` (`StringVectorType`, an XML Schema list) does. |
| `@customRegion`, `@rect` | DASH Annex H SRD has the geometry but not the placement: *"SRD information shall be contained exclusively in these two MPD elements (AdaptationSet and SubRepresentation)"* (DASH Annex H.1). Its notation is reused (§4.8.1) with a reference space of 100 × 100; its comma separator is not, because this specification's list attributes are space-separated. |
| `@linearRelation` | No base construct says what an event is or how another relates to it: the alternative-MPD events carry `@uri`, `@earliestResolutionTimeOffset`, `@serviceDescriptionId`, `@maxDuration`, `@executeOnce`, `@noJump`, `@skipAfter` (Table 63) and, for replacement, `@returnOffset`, `@clip`, `@startWithOffset` (Table 62); `EventStream@value` has no value space (Tables 59, 61). Three carriers were weighed. **An attribute on the window** was taken: the relation is a single value, its absence is the default, and a closed enumeration names the other two. **A descriptor on the window** would carry the same value behind a scheme URI and a `@value` for no gain. **A value space on the window's scheme** collides with the rule that SGAI streams carry no `@value` (PUB-8) and, since one family's windows in a Period share one stream (PUB-7), would bind every window of the stream at once, where the relation is per window. |
| `<svta:OverlayList>` | The linear resolution document is an MPD; the non-linear one has no base shape. It is not an MPD because an MPD must declare `@profiles` (the attribute is `use="required"` in `MPDtype`) and no existing profile fits: the List profile is for documents reached by an Alternative MPD event and is an extension of the CMAF profile (DR-10), and minting a profile or Interoperability Point would mean defining and publishing restrictions this edition does not need. The cost is stated: a validator has no profile URI to check it against, and its conformance rests on this specification's schema (§5.10) and on the base types it reuses. |
| `<svta:Ad>` | A candidate of a non-linear document carries a duration, ordered options, tracking, a ClickThrough and metadata; no base element holds that set outside a Period. |
| `<svta:RenderableAsset>` | An option's creative may be an image or HTML, and the `AdaptationSet` / `Representation` axis is closed to them (DR-1, DR-5). Of the four carriers of DR-6, (a) is taken: one fetch, a named element with the URL as an attribute. (b) would carry the URL as an event payload bound to a presentation time an option does not have; (c1) and (c2) would need a parent `AdaptationSet` the document does not have, and hosting them inside a foreign element collapses them into (a) with worse readability. The form is not a separate attribute: it is determined by `@mimeType` (§3.5), and carrying both would be redundant (DOC-36). |
| `<svta:Tracking>` | The beacons reuse the callback scheme and the base `EventStreamType` whole. The element is named in the SVTA namespace rather than being a DASH-namespace `EventStream`, because the base schema declares `EventStream` only as a local element of `Period`, `AdaptationSet` and their kin: a DASH-namespace `EventStream` inside a foreign element has no declaration a validator can check it against, and under `processContents="lax"` it would be skipped — exactly the unvalidated tracking carrier DOC-30 exists to prevent. |
| `<svta:ClickThrough>` | The base has no user-activated event: events are timed (DASH §5.10.1), and the callback *"is expected by a DASH Client to issue an HTTP GET request to a given URL"* (DASH §5.10.4.5.1) when dispatched on the timeline. The one user-driven mechanism, the nonlinear-playback annex, has the application choose the next Period (*"The application makes decisions upon which the user selects which Period to consume after the end of the currently active period"*, DASH Annex L.2) and fires no URL on activation. It anchors its event to the timeline and handles the interaction outside the timeline trigger, which is the split this carrier follows. |
| Metadata elements (§5.7) | No base element carries `AdSystem`, `AdTitle` or `Advertiser`; DASH §5.2.1 gives them a place. |
| `@dismissAfter` | The base skip control exists twice — `@skipAfter` on the alternative-MPD events and `PlaybackRestrictions@skipAfter` in the service description — and both default to skippable everywhere: *"Zero duration implies that skipping is allowed everywhere … Default value is PT0S"* (Table 63), *"The default value of 0 implies that skipping is allowed everywhere"* (Table K.9). A slot nobody declared dismissible is non-dismissible here (APS-19), and a construct cannot be reused without its default. `@skipAfter` keeps its base meaning wherever the Publisher writes it on a linear event (PLY-78). |
| `@validFor` | The base resolves at each execution (*"The alternative MPD is resolved at each execution of the Event"*, DASH §5.16.2.2.6) and leaves reuse to HTTP caching (NOTE 5). `MPD@availabilityEndTime` — whose stale-import rule makes a resolution fail when *"its value is smaller than the current time NOW"* (DASH §5.3.2.6.3, step 1 c) — was weighed: it is an absolute date about segment availability, where what the APS knows is a relative lifetime of its decision, and the document it would sit on is not an MPD. |
| `@onExhausted` | No base behaviour applies while the primary content is paused and the candidates run out. |
| `@family` | A Player must be able to tell that a document is of the wrong family (PLY-42); both non-linear families share one root element, so the family is declared. |
| `@background` | The double-box background is a composition attribute of the layout (APS-13); no base element composes two outputs. |
| Capability and forwarding parameters (§5.8.2, §5.8.3) | The base state vocabulary expresses what is currently playing — codec and bandwidth of the playing Representations, language, encryption, CMCD keys, execution state (DASH Annex I.4.2, Table I.5) — and has no device-capability axis: it cannot tell D1 from D5. The base parameter mechanism is author-declared (DASH Annex I.3), whereas which capability parameters travel is the Player's decision. |
| Request-type URN (§5.8.1) | Reuses `RequestParam` rather than introducing a parameter mechanism, through the URN extension point Table I.4 provides. |

#### 4.8.3 Where this specification departs from a base answer

One decision departs from what the base specification would do with a base
construct, and it is declared:

- **A superseded linear event is not executed while its window presents an
  ad (PLY-48).** A Player of this specification does not execute a base
  event the base would execute. The departure is declared explicitly by the
  Publisher, who authored both the event and the window, on a construct this
  specification defines; and a Player that does not implement this
  specification, which does not recognise the window, executes the base event
  exactly as the base defines. When the window presents no ad, the event is
  executed with its base semantics.

The following look like departures and are not: each is this
specification's own answer to a question the base does not ask, carried on
a construct of its own.

- The cap of an overlay or pause window has no "absent means infinity"
  default. It is `@durationCap`, not `@maxDuration`; on the inherited linear
  events an absent `@maxDuration` keeps its base meaning.
- An undeclared non-linear slot is non-dismissible. The declaration is
  `@dismissAfter`, not `@skipAfter`; an explicit `@skipAfter` on a linear
  event is honoured as the base defines it.
- The tie-break by document position among windows of equal presentation
  time: the base queue orders by PRT and does not resolve ties.
- The fallback chain and the PRT ordering applied to the non-linear
  families, which the base execution model does not reach.

#### 4.8.4 Weighed, and not taken

- **Carrying non-AV assets in descriptors (c1, c2) or event payloads (b).**
  See `<svta:RenderableAsset>` above. No construct of this edition uses a
  descriptor, so the choice between `SupplementalProperty` (the parent
  survives a legacy client) and `EssentialProperty` (the parent is dropped)
  does not arise; on anything in the primary content path
  `EssentialProperty` would be unavailable anyway, because dropping the
  parent would break primary-content playback.
- **`MPD@type="list"` on the non-linear document.** Declaring it enrols the
  document in constraints written for the linear path (DR-10), and the
  document is not an MPD.
- **Minting a profile or Interoperability Point.** A profile would declare
  that a document carries these constructs; it would not make anyone honour
  them (DR-8). It would also not certify them in an MPD: for profile
  conformance the base removes *"All elements or attributes that are either
  (i) in this document and explicitly excluded by ProfA, or (ii) in an
  extension namespace and not explicitly included by ProfA"* (DASH §8.1, step 4).
- **Ordering options with `@selectionPriority`, a fallback scheme or
  `Preselection`.** Those rank Adaptation Sets of one media content; options
  here are of different forms, most of them not media, and document order
  already carries the ranking with no second declaration to drift from it.
- **`<ImportedMPD>` inside a non-linear option.** `ImportedMPD` is a child
  of a Linked Period and triggers the Linked Period merge (DASH §5.3.2.6.3); an
  option is not a Period. The video form references its SPS sub-MPD by
  `@src` instead, and the sub-MPD is the same kind of document a List MPD
  imports.
- **`@noJump` on the non-linear windows.** Excluded, for the reason in §1.3;
  preserved unchanged on the inherited linear events.
- **The base skip controls for non-linear dismissal.** See `@dismissAfter`
  above.
- **Presentation options on List MPD candidates.** A List MPD candidate is
  one Period and one imported presentation; the media axis cannot carry an
  image or HTML fallback (DR-1, DR-5), and a non-media linear form would need
  a timeline construct the base does not have. A linear candidate therefore
  carries exactly one option — its video, layout `linear` — which the
  single-option rule admits; image or HTML alternatives for a linear slot are
  not carried in this edition.

#### 4.8.5 Profiles

- The main MPDs of the annexes declare `urn:mpeg:dash:profile:isoff-live:2011`
  or `urn:mpeg:dash:profile:isoff-on-demand:2011`. The Advanced Linear
  profile (`urn:mpeg:dash:profile:advanced-linear:2025`) announces *"Support
  for a restricted set of DASH events"* (DASH §8.13.1) and states that
  *"EventStream elements may indicate Alternative MPD (5.16) and Callback
  (5.10.4.5) event schemes"* (DASH §8.13.2.2) next to *"Periods and
  Representations which do not conform to the constraints in this subclause
  may not be presented"* (DASH §8.13.2.1). Whether an SGAI event stream in an
  Advanced Linear MPD makes its Period non-conforming is not settled by the
  text; chapter 8 records it among the questions this edition leaves open.
- The non-linear resolution document declares no profile (§4.8.2).
- List MPDs declare `urn:mpeg:dash:profile:list:2024` and sub-MPDs
  `urn:mpeg:dash:profile:sps:2024`, as the base requires or permits.

---

## 5. Syntax

### 5.0 Conventions

- The DASH namespace is `urn:mpeg:dash:schema:mpd:2011`. The namespace of
  every element and attribute this specification introduces is
  `urn:svta:dash:sgai:2026`, written with the prefix `svta` in this document.
  The prefix is not significant; the namespace is.
- `@attr` denotes an XML attribute; element names are capitalised.
- Every attribute block is a table with the columns *Attribute*,
  *Required*, *Type*, *Default*, *Description*. *Required* is **M**
  (mandatory), **O** (optional), **OD** (optional with a default) or
  **CM** (conditionally mandatory, the condition stated in the
  description). Where an attribute takes a value from an enumeration, the
  table of values follows immediately or names the section that defines it.
- Types are those of W3C XML Schema Part 2 unless defined here. Two list
  types are defined here:
  - **`LayoutTokenList`** — a space-separated list of layout tokens
    (§3.4.2). The delimiter is a space, as in the base specification's
    `@dependencyId` (`StringVectorType`, an XML Schema list type).
  - **`PercentRect`** — four `xs:decimal` values, space-separated, in the
    order *x y width height*, each between 0 and 100 inclusive, in percent
    of the video viewport with the origin at its top-left corner, x growing
    to the right and y downward; x + width and y + height do not exceed 100.
    This is the SRD notation of the base (DASH Annex H.2.2) with a reference
    space of 100 × 100.
- **`DismissAfterType`** — either an `xs:duration` or the token `never`.

### 5.1 Opportunity declarations in the main MPD

Every opportunity is an `Event` inside an `EventStream` of a `Period`, as in
the base specification. The event scheme names the family; the child element
of the `Event` carries the opportunity's declarations.

| Family | `EventStream@schemeIdUri` | Child of `Event` |
|---|---|---|
| Linear, insertion | `urn:mpeg:dash:event:alternativeMPD:insert:2025` (base) | `InsertPresentation` (base) |
| Linear, replacement | `urn:mpeg:dash:event:alternativeMPD:replace:2025` (base) | `ReplacePresentation` (base) |
| Overlay | `urn:svta:dash:sgai-overlay:2026` | `<svta:OverlayPresentation>` |
| Pause | `urn:svta:dash:sgai-pause-trigger:2026` | `<svta:PauseAdPresentation>` |

#### 5.1.1 `InsertPresentation` — linear insertion, inherited

Adopted unchanged from the base specification (DASH §5.16.3, DASH §5.16.5). The event
*"shall not appear if the MPD type is "dynamic""* (DASH §5.16.3). This
specification adds no attribute to it and no element under it (DOC-26).

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | M | `xs:anyURI` | — | The APS endpoint. Resolves to a List MPD or a single-period alternative MPD. |
| `@earliestResolutionTimeOffset` | OD | `xs:unsignedLong` | 60 s in units of `EventStream@timescale` | As the base: the MPD *"can be retrieved at any time between PRT – T and PRT"* (Table 63). |
| `@serviceDescriptionId` | O | `xs:unsignedInt` | — | As the base; a `PlaybackRestrictions@skipAfter` it references is honoured under §5.2.4. |
| `@maxDuration` | OD | `xs:unsignedLong` | infinity | The cap, in units of `EventStream@timescale`. Absent means infinity; zero means the event is not executed (Table 63). What it bounds is given in §4.5.4. |
| `@executeOnce` | OD | `xs:boolean` | `false` | As the base. |
| `@noJump` | OD | `xs:integer` | `0` | As the base. |
| `@skipAfter` | OD | `xs:duration` | `PT0S` | As the base; honoured under §5.2.4 when written explicitly. |

#### 5.1.2 `ReplacePresentation` — linear replacement, inherited

Adopted unchanged (DASH §5.16.4, DASH §5.16.5). It carries every attribute of §5.1.1,
plus:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@returnOffset` | O | `xs:unsignedLong` | — | As the base: the offset from `Event@presentationTime` at which the main presentation resumes. |
| `@clip` | OD | `xs:boolean` | `true` | As the base: `true` terminates the alternative presentation *"at the latest at time PRT + APDmax"*, `false` at PRTA + APDmax (Table 62). |
| `@startWithOffset` | OD | `xs:boolean` | `false` | As the base. |

#### 5.1.3 The overlay window

**Event usage.** The base attributes of `EventStream` and `Event`, as this
scheme uses them.

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `EventStream@schemeIdUri` | M | `xs:anyURI` | — | `urn:svta:dash:sgai-overlay:2026`. |
| `EventStream@value` | — | `xs:string` | — | Not present (PUB-8). A Player ignores one if present (PLY-87). |
| `EventStream@timescale` | O | `xs:unsignedInt` | `1` (base) | Units of `Event@presentationTime`, `Event@duration`, `@durationCap` and `@earliestResolutionTimeOffset`. |
| `Event@presentationTime` | OD | `xs:unsignedLong` | `0` (base) | The start of the window's span, relative to the start of the Period as the base defines. |
| `Event@duration` | M | `xs:unsignedLong` | — | The length of the span. A window without it is not a window this specification defines, and the Player treats it as PLY-29 treats a window without a cap. |
| `Event@id` | M | `xs:unsignedLong` | — | Unique in the `EventStream`, as the base requires of event identifiers. |
| `Event@status` | OD | `EventStatusType` | `repeat` (base) | As the base (DASH §5.10.2.4). |

Each `Event` contains exactly one `<svta:OverlayPresentation>`.

**`<svta:OverlayPresentation>`.**

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | M | `xs:anyURI` | — | The APS endpoint. Resolves to an `<svta:OverlayList family="overlay">`. The Publisher MAY encode slot constraints as query parameters of this URL, by bilateral arrangement with the APS. |
| `@durationCap` | M | `xs:unsignedLong` | — | The cap, in units of `EventStream@timescale`: the cumulative duration of what the window presents. Zero means the window does not fire. |
| `@earliestResolutionTimeOffset` | OD | `xs:unsignedLong` | 60 s in units of `EventStream@timescale` | How far before `Event@presentationTime` the Player may resolve the window. Name, units and default are the base's (Table 63). Zero means only at the start of the window. |
| `@allowedLayouts` | O | `LayoutTokenList` | the family default (§3.4.3) | The layouts the window admits, drawn from §3.4.2. |
| `@customRegion` | O | `PercentRect` | the whole viewport | The region inside which a `custom` option's rectangle lies (§5.3.5). Present only when `@allowedLayouts` lists `custom`. |
| `@linearRelation` | O | enum, §5.1.6 | the default relation | How the window relates to the inherited linear events it overlaps. |

**What the span means.** The window's forms are presented only inside its
span, on the timeline of the presentation whose MPD declares the window: a
form still on screen when the span ends ends there. The presentation also
ends when the cap is reached (PLY-24) or the candidates are exhausted. When
the playhead enters the span after its start (a join or a seek), the Player
MAY resolve the window and present for the remainder of the span.

#### 5.1.4 The pause window

**Event usage.** As §5.1.3, with
`EventStream@schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026"`. The span
is the region of the primary timeline inside which a viewer pause triggers a
resolution request (PLY-11). The window schedules no presentation and
predicts none.

Each `Event` contains exactly one `<svta:PauseAdPresentation>`.

**`<svta:PauseAdPresentation>`.**

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | M | `xs:anyURI` | — | The APS endpoint. Resolves to an `<svta:OverlayList family="pause">`. |
| `@durationCap` | M | `xs:unsignedLong` | — | The cap, in units of `EventStream@timescale`: the cumulative duration of one pass through the candidates of one resolution document (§4.5.4). It does not bound the pause. |
| `@earliestResolutionTimeOffset` | OD | `xs:unsignedLong` | 60 s in units of `EventStream@timescale` | How far before the start of the window the Player may resolve it. Computed against `Event@presentationTime`, never against the pause. |
| `@allowedLayouts` | O | `LayoutTokenList` | the family default (§3.4.3) | The layouts the window admits. |
| `@executeOnce` | OD | `xs:boolean` | `false` | When `true`, the window yields at most one pause ad for the whole session (PLY-63, PLY-64). The name is the base's, and so is the counter rule: the window is consumed when a pause ad successfully starts rendering. |
| `@linearRelation` | O | enum, §5.1.6 | the default relation | Takes only the value `on-top` on a pause window (§5.1.6). |

#### 5.1.5 Overlapping windows of one family

Windows of one family whose spans overlap form a fallback chain (PLY-38).
The Publisher authors them as `Event` entries of the family's single
`EventStream` in the Period (PUB-7), in non-decreasing presentation time as
the base requires (*"Events in Event Streams shall be ordered such that
their presentation time is non-decreasing"*, Table 43). Windows of equal
presentation time are tried in the order they appear. Each window binds what
it serves with its own declarations (PLY-43). Overlapping windows of
**different** families are not a chain: they are governed by the
cross-family rules of §4.5.9.

#### 5.1.6 The relation to inherited linear events

`@linearRelation` declares what the window does when an inherited linear
event overlaps it. Absence is the default relation.

| Enum value | Description |
|---|---|
| *(absent)* | **Default.** The window is presented only over the content of the presentation whose MPD declares it. It does not replace an inherited linear event, and it is not composited over an alternative presentation (PLY-49). Two ads on screen at once never come from an overlap nobody declared. |
| `supersede` | The window stands in for the inherited linear events whose `Event@presentationTime` falls within its span. A Player of this specification presents the window and does not execute those events, and executes them after all when the window presents no ad (PLY-48). A legacy Player ignores the window and plays the linear events, so the linear break is the legacy fallback of the non-linear offering (Annex Q, Annex G). |
| `on-top` | The window is presented also while an alternative presentation that starts within its span is active, composited over it: a hybrid break (PLY-50, Annex D). |

On a **pause window**, `@linearRelation` takes only the value `on-top`:
whether a pause window presents an ad depends on whether the viewer pauses,
which is unknown at the presentation time of the linear event it would
supersede. `on-top` on a pause window makes it applicable while a linear ad
that starts within its span occupies the screen (PLY-55).

A non-linear ad presented during an alternative presentation that is not
advertising — a blackout slate — is declared in that presentation's own MPD
(PUB-12, PLY-51, Annex N). Declaring `supersede` over a blackout would show
the programme the Publisher blacked out: the Player cannot see that the
replacement is a blackout, which is why the declaration is the Publisher's.

#### 5.1.7 A window, in short

```xml
<Period xmlns="urn:mpeg:dash:schema:mpd:2011"
        xmlns:svta="urn:svta:dash:sgai:2026" id="p1">
  <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
    <Event id="1" presentationTime="120000" duration="30000">
      <svta:OverlayPresentation uri="https://aps.example.com/nl/overlay/1"
          durationCap="30000"
          allowedLayouts="overlay-lower-third squeezeback-l-shape-upper-left"/>
    </Event>
  </EventStream>
  <!-- primary AdaptationSets follow -->
</Period>
```

### 5.2 Resolution documents

#### 5.2.1 List MPD — linear

The resolution document of an inherited linear event is a List MPD (DASH §8.14)
or a single-period alternative MPD, as the base defines. A List MPD
candidate is one `Period`, normally a Linked Period whose `ImportedMPD`
references an SPS sub-MPD (§5.4). Candidates play in document order. The
candidate's duration is the Linked Period's `@duration` reconciled with the
imported `Period@duration` by the base rule: the Linked Period's value is
replaced by the imported one *"if the latter is smaller"* (DASH §5.3.2.6.3, step
3 d iii).

This specification adds the following to a List MPD, and nothing else.

**On the `MPD` element:**

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@svta:dismissAfter` | O | `DismissAfterType` | `never` | The dismissal declaration of the slot (§5.2.4). The APS writes it on every List MPD it returns (APS-19). |

**In full:**

| Where | Construct | Required | Description |
|---|---|---|---|
| `MPD` | `@svta:dismissAfter` | O | The dismissal declaration of the slot (§5.2.4). Type `DismissAfterType`; absent means `never`. |
| `Period` (a candidate) | `<svta:ClickThrough>` | 0..1 | The candidate's ClickThrough (§5.6). |
| `Period` (a candidate) | `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>` | 0..1 each | Creative metadata (§5.7). |

All three are foreign-namespace content that the Linked Period merge keeps
(§4.7.5). Tracking of a List MPD candidate is in its sub-MPD, as the base
does it (§5.5).

**Why the List MPD is not given presentation options.** See §4.8.4: a List
MPD candidate carries exactly one option, its video with layout `linear`.

#### 5.2.2 `<svta:OverlayList>` — the non-linear resolution document

The resolution document of an overlay or pause window. It is a standalone XML
document, served with media type `application/xml`, whose root element is
`<svta:OverlayList>`. *Overlay* in the name takes the family reading for the
non-linear document (§3.3). It declares no profile (§4.8.2).

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@family` | M | enum | — | The family of the window this document resolves. |
| `@dismissAfter` | O | `DismissAfterType` | `never` | The dismissal declaration (§5.2.4). The APS always writes it (APS-19); a document without it leaves the slot non-dismissible. |
| `@validFor` | O | `xs:duration` | the remainder of the window's span | How long the document stays usable after the Player receives it (§5.2.5). |
| `@onExhausted` | CM | enum, §5.2.6 | `stop` | The exhaustion behaviour. Written on every document with `@family="pause"` (APS-22); absent on `@family="overlay"`. |

| Enum value of `@family` | Description |
|---|---|
| `overlay` | Resolves an overlay window. |
| `pause` | Resolves a pause window. |

| Element | Cardinality | Description |
|---|---|---|
| `<svta:Ad>` | 0 … N | A candidate (§5.3.1). Document order is the order of presentation. |

A document with no `<svta:Ad>` is the empty resolution (§5.2.3).

```xml
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
    xmlns:svta="urn:svta:dash:sgai:2026"
    family="overlay" dismissAfter="PT5S" validFor="PT10M">
  <svta:Ad duration="PT15S">
    <svta:RenderableAsset src="https://cdn.example.com/a1/banner.png"
        mimeType="image/png" layout="overlay-lower-third"/>
  </svta:Ad>
</svta:OverlayList>
```

#### 5.2.3 The empty resolution

An opportunity the ADS did not sell is expressed as a document, not as an
error (APS-4). The document is well-formed and complete: it declares itself a
resolution document and carries every element the syntax requires. What it
does not carry is a candidate.

| Family | Shape |
|---|---|
| Overlay, pause | `<svta:OverlayList>` with its `@family` (and, for pause, `@onExhausted`), and no `<svta:Ad>`. |
| Linear | A List MPD with one `Period` of `@duration="PT0S"` and no `ImportedMPD` and no `AdaptationSet`. `MPDtype` requires at least one `Period` (its `Period` element has no `minOccurs="0"`), and a Period of zero duration is the one Period that may hold no Adaptation Set (DR-7). Its merge yields no media, which is the base's *"Alternative MPD is a List MPD, and merge process resulted in no available media"* (DASH §5.16.2.2.6). |

It is **not** an empty HTTP body, **not** a `204`, **not** a `404`, and
**not** a document that fails to parse. For the Player it is a failed
execution (PLY-39) that does not consume the opportunity (PLY-44, PLY-64).

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="list"
     profiles="urn:mpeg:dash:profile:list:2024" minBufferTime="PT1S">
  <Period id="none" duration="PT0S"/>
</MPD>
```

#### 5.2.4 Dismissal declaration

The unit of dismissal is the **slot**: the viewer ends the whole slot, never
one ad inside it. Whether a slot may be dismissed, and how soon, are
properties of the advertising that was sold, so the APS declares them in the
resolution document.

| Enum value of `@dismissAfter` / `@svta:dismissAfter` | Description |
|---|---|
| `never`, or absent | The slot is not dismissible. |
| an `xs:duration` *D* | The slot becomes dismissible once *D* has elapsed from the moment it began rendering, and stays dismissible while it is on screen. `PT0S` means immediately. |

The elapsed time is measured on the presentation timeline of the slot, like
the cap (PLY-31).

**On a linear slot, the base skip declaration governs when the Publisher
writes one.** The Player determines dismissal of an inherited linear slot in
this order, and the first that applies governs:

1. `@skipAfter` written explicitly on the event's `InsertPresentation` or
   `ReplacePresentation`, with its base meaning: *"an offset in time (in
   fractional seconds) from the beginning of the alternative presentation
   till the moment the rest of that presentation may be skipped by the
   application in response to a user action"*; *"Duration equal to or
   exceeding the presentation duration implies that skipping is disallowed
   for its whole duration"* (Table 63).
2. `PlaybackRestrictions@skipAfter` written explicitly in the
   `ServiceDescription` the event references through `@serviceDescriptionId`,
   with its base meaning (Tables K.9, K.18).
3. `@svta:dismissAfter` on the List MPD.
4. Otherwise the slot is non-dismissible.

"Written explicitly" means present in the document as authored; a default
that a schema-aware parser fills in is not a declaration. The order between
items 1 and 2 is this specification's: the base states no precedence
between its two skip controls.

On an overlay or pause slot the declaration is `@dismissAfter` on the
`<svta:OverlayList>`, and it applies to every family this edition defines,
pause included: a paused viewer can resume to end a pause ad, and dismissal
gives the surface back without resuming.

#### 5.2.5 Usable lifetime

Resolving early buys latency and spends freshness. `@validFor` states how
long a resolution obtained ahead of its opportunity stays usable, measured
from the moment the Player receives the document. When the opportunity fires
— the start of an overlay window, or a qualifying pause — the Player checks
it (PLY-9). A document without `@validFor` stays usable until the end of its
window's span. A large `@validFor` means the window is resolved once; `PT0S`
means the resolution is usable only if it arrives when the opportunity fires.

#### 5.2.6 Exhaustion behaviour of a pause document

A pause slot has no declared duration, so its candidates may run out while
the viewer is still paused. `@onExhausted` declares what follows.

| Enum value | Description |
|---|---|
| `repeat` | The Player presents the sequence again from its first candidate, for as long as the pause lasts. Each pass is bounded by the window's cap. |
| `request-again` | The Player requests a new resolution document for the same pause. A document carrying no candidates ends the pause's ads (PLY-66). |
| `stop` | The Player presents no further ad; the paused primary frame is shown. The default: it is what the viewer would see if the mechanism did not exist, and every Player can do it. |

The declaration belongs to the APS and not to the Publisher: a
Publisher-declared limit on how many documents may be served would be
answered by APSs returning defensively long lists, the outcome the limit
would exist to prevent.

### 5.3 Candidates and presentation options

#### 5.3.1 `<svta:Ad>`

A candidate of a non-linear resolution document.

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@duration` | M | `xs:duration` | — | The declared duration of the candidate on the presentation timeline, for every form, image and HTML included (PLY-70). The canonical value for the slot arithmetic; for a video option, the Player reconciles it with the sub-MPD's `Period@duration` by keeping the smaller of the two, as the base does for a Linked Period. |

| Element | Cardinality | Description |
|---|---|---|
| `<svta:RenderableAsset>` | 1 … N | The presentation options, in preference order (§5.3.4). |
| `<svta:Tracking>` | 0 … 1 | The candidate's tracking beacons (§5.5). |
| `<svta:ClickThrough>` | 0 … 1 | The candidate's ClickThrough (§5.6). |
| `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>` | 0 … 1 each | Creative metadata (§5.7). |

#### 5.3.2 `<svta:RenderableAsset>` — the presentation option

One option: a form together with its layout.

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@src` | M | `xs:anyURI` | — | The creative: an SPS sub-MPD for the video form, the image, or the HTML document. |
| `@mimeType` | M | `xs:string` | — | The media type of `@src`. Determines the form (table below). |
| `@layout` | M | layout token | — | One token of §3.4.2 (§5.3.3). |
| `@rect` | CM | `PercentRect` | — | The overlay's rectangle. Present if and only if `@layout="custom"` (§5.3.5). |
| `@background` | CM | `xs:anyURI` | — | The advertiser's background image. Present if and only if `@layout="squeezeback-double-box-background"` (§5.3.6). |

| `@mimeType` | Form |
|---|---|
| `application/dash+xml` | Video. `@src` references an SPS MPD (§5.4). |
| `image/*` (for example `image/png`, `image/jpeg`) | Image. |
| `text/html` | HTML. |

The form is not a separate attribute: `@mimeType` determines it, and a second
declaration could only contradict the first.

#### 5.3.3 `@layout`

The value is one token of the table in §3.4.2, which lists the enumeration.
The token names the composition the Player builds (§5.3.6).

#### 5.3.4 Document order is the preference order

The `<svta:RenderableAsset>` children of an `<svta:Ad>` form one ordered
list. There is no priority or ranking attribute: the first option in
document order is the most preferred. The Player walks the list and renders
the first option whose form its device can render and whose layout the
window admits (PLY-17, PLY-18). Several options let one candidate resolve on
devices the ADS and the APS know nothing about; a single option leaves the
choice with the APS (APS-6).

#### 5.3.5 The `custom` layout (optional)

`custom` places an overlay in a rectangle given in percent of the video
viewport. It applies to overlay windows only and is optional for every actor
(DOC-21).

- The Publisher admits it by listing `custom` in `@allowedLayouts`, and MAY
  bound it with `@customRegion` on the window; with no region, the region is
  the whole viewport.
- The Player forwards both on the resolution request (§5.8.3).
- The APS carries the rectangle in `@rect`, inside the region it received
  (APS-12).
- The Player checks containment before rendering (PLY-21): with region
  (*rx ry rw rh*) and rectangle (*x y w h*), the option is renderable when
  *x ≥ rx*, *y ≥ ry*, *x + w ≤ rx + rw* and *y + h ≤ ry + rh*.

```xml
<!-- on the window -->
<svta:OverlayPresentation xmlns:svta="urn:svta:dash:sgai:2026"
    uri="https://aps.example.com/nl/overlay/7"
    durationCap="20000" allowedLayouts="custom overlay-lower-third"
    customRegion="60 5 35 30"/>
```

```xml
<!-- in the resolution document -->
<svta:RenderableAsset xmlns:svta="urn:svta:dash:sgai:2026"
    src="https://cdn.example.com/a7/bug.png"
    mimeType="image/png" layout="custom" rect="65 8 25 20"/>
```

#### 5.3.6 Layout composition

| Layout | Elements on screen | Composition |
|---|---|---|
| `linear` (as an option of a non-linear candidate) | the ad | The full-screen takeover. On a static presentation the Player suspends the primary content and resumes it from the suspended position when the candidate ends, as an insertion does; on a dynamic presentation the primary media time keeps progressing while the ad plays and the Player resumes at the position it has reached, as a replacement does. The base admits insertion only in static MPDs (DASH §5.16.3), which is the reason for the split. |
| `overlay`, `overlay-corner`, `overlay-lower-third`, `custom` | primary content, ad | The ad is composited over the playing primary content, which is not resized. |
| `squeezeback-l-shape-upper-left`, `squeezeback-l-shape-upper-right` | full-frame creative, shrunk primary content | The creative covers the whole frame in the background; the primary content is scaled into the region the token names and composited on top of it. The "L" is the band of the creative left visible. There is no third element (PLY-72). |
| `squeezeback-double-box` | primary content, ad | The two boxes of §3.4.2; the uncovered bands render black. |
| `squeezeback-double-box-background` | primary content, ad, background image | The two boxes, over the image of `@background`, which fills the uncovered bands (PLY-71). The background is a composition attribute, never an option, and is always a still image. |
| `pause-fullscreen` | the ad | The ad occupies the entire screen while the viewer is paused. |
| `pause-partial` | paused primary frame, ad | The ad is composited over the paused frame, which remains visible. |

#### 5.3.7 The decoder-and-surface budget

A Player decides whether an option is satisfiable from the elements it puts
on screen and their types. The primary content always holds one video
decoder while it is output.

| Layout and form | Video decoders | Surfaces over video | Satisfiable on |
|---|---|---|---|
| `overlay*` / `custom`, video | 2 | — | D1, D2 |
| `overlay*` / `custom`, image | 1 | image | D1, D3, D4 |
| `overlay*` / `custom`, HTML | 1 | HTML | D1, D3 |
| L-shape, video creative | 2 | — | D1, D2 |
| L-shape, image creative | 1 | image | D1, D3, D4 |
| L-shape, HTML creative | 1 | HTML | D1, D3 |
| `squeezeback-double-box`, video ad | 2 | — | D1, D2 |
| `squeezeback-double-box`, image ad | 1 | image | D1, D3, D4 |
| `squeezeback-double-box`, HTML ad | 1 | HTML | D1, D3 |
| `squeezeback-double-box-background`, video ad | 2 | image (background) | D1 |
| `squeezeback-double-box-background`, image ad | 1 | image (ad and background) | D1, D3, D4 |
| `squeezeback-double-box-background`, HTML ad | 1 | HTML (ad), image (background) | D1, D3 |
| `linear` takeover, video | 1, reused sequentially | — | D1 to D5 |
| `pause-fullscreen` / `pause-partial`, video | 2, or 1 when the Player releases the primary content's decoder for the pause (PLY-56) | — | D1, D2; D3 and D4 when the decoder is released |
| `pause-fullscreen` / `pause-partial`, image | 1 (holding the paused frame) or none | image | D1, D3, D4 |
| `pause-fullscreen` / `pause-partial`, HTML | 1 or none | HTML | D1, D3 |

`overlay*` stands for `overlay`, `overlay-corner` and `overlay-lower-third`.
While an alternative presentation is output, the linear ad holds the decoder
the primary content released (DASH §4.2), and an overlay composited on top of it
needs the budget of the same row.

**D5 and a fullscreen pause ad.** A fullscreen pause ad replaces the whole
visual surface, and the Player MAY release the primary content to present it
(PLY-61). Whether D5, which composites nothing over video, can show a
fullscreen video or image once the primary content is released is a
property of the device this specification does not model: the device
classes of §3.6 describe composition over video. The walk-throughs of
chapter 7 and the annexes take the conservative reading that D5 declines
the pause ad; a D5 Player that presents a fullscreen pause ad after
releasing the primary content, and restores it on resume (PLY-59), is
equally conformant.

### 5.4 Sub-MPD

A sub-MPD is the video creative of a List MPD candidate (through
`ImportedMPD`) or of a non-linear option (through `@src`). In both cases it
is a Single-Period Static MPD (DASH §8.15): `MPD@type="static"`, exactly one
`Period` carrying `@duration`, no `MPD@mediaPresentationDuration`, no
`MPD@availabilityStartTime`, no XLink, and none of the MPD-level elements
DASH §8.15.2 excludes (`Metrics` and `SupplementalProperty` among them). Its
Representations carry ISO-BMFF media with `@mimeType` per IETF RFC 4337
(DR-1). It MAY declare `urn:mpeg:dash:profile:sps:2024` in `@profiles`.

| Sub-MPD of | Carries tracking | Carries ClickThrough / metadata |
|---|---|---|
| A List MPD candidate | Yes: a callback `EventStream` in its Period (§5.5.1). | No: they are on the List MPD Period (§5.2.1). |
| A non-linear option | No: tracking belongs to the candidate, whichever option renders (§5.5.2). | No: they are on the `<svta:Ad>`. |

### 5.5 Tracking carrier

In-band ad tracking beacons ride the base callback scheme
`urn:mpeg:dash:event:callback:2015` (DASH §5.10.4.5). A callback event *"is
expected by a DASH Client to issue an HTTP GET request to a given URL and
ignore the HTTP response"* (DASH §5.10.4.5.1); in an MPD its `EventStream@value`
is `1` and the event's value is the HTTP URL (Table 47). No tracking scheme
is introduced. The ADS decides which beacons exist and when; the APS
transcribes them; the Player executes them (PLY-79). Nothing here fixes
fractions, granularity or count: quartiles are one schedule an ADS may
choose.

#### 5.5.1 On a List MPD candidate

As the base does it: an `EventStream` of the callback scheme in the Period of
the candidate's sub-MPD, times relative to that Period. It is placed in the
sub-MPD and not in the List MPD Period, because in the Linked Period merge an
imported `EventStream` with the same scheme and value **replaces** the Linked
Period's (DASH §5.3.2.6.3, step 3 c iv), so a beacon stream in both places would
lose one of them.

The callback streams of all the sub-MPDs of one List MPD share one `@id`
scope once merged (PLY-81), and the base ignores an event whose scheme,
value and `@id` it has already processed when `@status` is absent
(DASH §5.10.2.4). An APS that assembles a List MPD therefore numbers the beacons
of its sub-MPDs uniquely across the whole List MPD (Annexes A.4, F.4).

#### 5.5.2 On a non-linear candidate: `<svta:Tracking>`

`<svta:Tracking>` is an element of the base type `EventStreamType`: it takes
the attributes and children of an `EventStream` (DASH §5.10.2.3), and its `Event`
children are DASH-namespace `Event` elements.

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@schemeIdUri` | M | `xs:anyURI` | — | `urn:mpeg:dash:event:callback:2015`. |
| `@value` | M | `xs:string` | — | `1`, as Table 47 requires for the callback scheme. |
| `@timescale` | O | `xs:unsignedInt` | `1` | As the base. |
| `@presentationTimeOffset` | OD | `xs:unsignedLong` | `0` | As the base, subtracted from each event's presentation time. |

| Element | Cardinality | Description |
|---|---|---|
| `Event` (DASH namespace) | 0 … N | One beacon. `@presentationTime` is relative to the start of the candidate (below); `@id` is the de-duplication key; the content is the beacon URL. Non-decreasing presentation times, as the base requires. |

**The timebase.** Time 0 of a `<svta:Tracking>` is the instant the candidate
begins rendering, whichever of its options rendered (PLY-82). A beacon at
`presentationTime="0"` fires when the candidate starts; one at the
candidate's duration fires when it completes. Times are on the presentation
timeline, so they follow the playback speed (PLY-69) and stop accruing while
the presentation timeline does not advance.

**De-duplication.** Within one `<svta:Ad>`, beacons sharing an `@id`, or the
same URL at the same presentation time, fire once. The same `@id` in two
candidates of one document names two beacons (PLY-81).

**Trimming, dismissal, resume.** Beacons scheduled after a trim boundary,
after a dismissal, or after the viewer resumes from a pause ad are not fired
(PLY-80, PLY-77, PLY-58).

```xml
<svta:Tracking xmlns="urn:mpeg:dash:schema:mpd:2011"
    xmlns:svta="urn:svta:dash:sgai:2026"
    schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
    timescale="1000">
  <Event presentationTime="0" id="1">https://t.example.com/imp?ad=a1</Event>
  <Event presentationTime="7500" id="2">https://t.example.com/mid?ad=a1</Event>
  <Event presentationTime="15000" id="3">https://t.example.com/done?ad=a1</Event>
</svta:Tracking>
```

### 5.6 ClickThrough carrier

`<svta:ClickThrough>` carries a candidate's ClickThrough URL and its
click-tracking URLs together, so that every Player conformant to this
specification reads the same two fields and fires the click identically.
Click-tracking is not carried by the callback scheme: an activation is a user
interaction with no presentation time, and the base defines no
user-triggered event (§4.8.2).

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | M | `xs:anyURI` | — | The destination opened, or handed off to the device, when the viewer activates the ClickThrough. |
| `@trackingUris` | O | list of `xs:anyURI`, space-separated | — | The click-tracking URLs. On activation the Player issues an HTTP GET to each once and ignores the response, as for a callback. Absent when the advertiser declared none. |

It is a child of `<svta:Ad>` in a non-linear document, and of the candidate's
`Period` in a List MPD. How the activation is offered (remote select, tap) is
the device's; the outcome does not depend on the device class.

```xml
<svta:ClickThrough xmlns:svta="urn:svta:dash:sgai:2026"
    uri="https://brand.example.com/offer"
    trackingUris="https://t.example.com/click?ad=a1 https://t2.example.net/c?id=9"/>
```

### 5.7 Application-level metadata

Creative metadata with no native DASH carrier has a defined place. Emitting
it is optional for the APS and reading it is optional for the Player; a
legacy Player removes it; nothing in the presentation depends on it.

| Element | Cardinality | Type | Description |
|---|---|---|---|
| `<svta:AdSystem>` | 0 … 1 | `xs:string` | The ad system that served the ad. |
| `<svta:AdTitle>` | 0 … 1 | `xs:string` | The ad's title. |
| `<svta:Advertiser>` | 0 … 1 | `xs:string` | The advertiser. |

They sit on `<svta:Ad>` and on a List MPD candidate `Period`. A universal
ad identifier is deliberately not given a carrier: it serves reconciliation
on the ADS side, where the decision document already carries it.

### 5.8 The resolution request

The resolution request is an HTTP GET to the opportunity's `@uri`. For an
inherited linear event it is the base request; for a window it is issued as
§4.5.2 states. Three sources can add query parameters to it, and they share
one URL.

#### 5.8.1 Publisher-declared parameters

- The Publisher MAY write slot constraints directly into the query of `@uri`,
  by bilateral arrangement with the APS.
- The Publisher MAY attach `RequestParam` templates of DASH Annex I.3 to the
  window's `EventStream`, with `@includeInRequests` containing the request
  type **`urn:svta:dash:sgai-resolution:2026`**, which identifies the
  resolution requests of overlay and pause windows. The base defines the
  request type `altmpd` for the alternative MPD of an inherited event and
  lets a URN name any other: *"a URN or tag URI, where the request type
  semantics is understood by the client and specified by the URN / tag URI
  owner"* (Table I.4). The DASH Annex I.3 signalling applies unchanged, including
  the MPD-level `EssentialProperty` of scheme `urn:mpeg:dash:urlparam:2025`
  that the base requires for `RequestParam` (DASH Annex I.3.1).

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static" profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT45M" minBufferTime="PT2S">
  <Period id="p1">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="120000" duration="30000">
        <svta:OverlayPresentation uri="https://aps.example.com/nl/overlay/1?slot=mid1"
            durationCap="30000"
            allowedLayouts="overlay-lower-third squeezeback-l-shape-upper-left"/>
      </Event>
      <RequestParam includeInRequests="urn:svta:dash:sgai-resolution:2026"
          queryTemplate="sid=$urn:mpeg:dash:state:cmcd#sid$"/>
    </EventStream>
    <!-- primary AdaptationSets follow -->
  </Period>
  <!-- MPD-level descriptors follow the Periods (and Metrics) in MPDtype -->
  <EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025"/>
</MPD>
```

#### 5.8.2 Player-declared capability parameters

The Player MAY attach the following reserved parameters. They state what the
device supports; which ad experiences follow from that is the APS's to
derive.

| Parameter | Value | Meaning |
|---|---|---|
| `sgai-video-decoders` | a non-negative integer | The number of video decoders the device can run concurrently, the one the primary content uses included. |
| `sgai-image-over-video` | `1` or `0` | Whether the device can composite an image over video. |
| `sgai-html-over-video` | `1` or `0` | Whether the device can composite HTML over video. |
| `sgai-custom-layout` | `1` or `0` | Whether the Player supports the optional `custom` layout. |

Video over video needs a second decoder, so it is expressed by
`sgai-video-decoders` of 2 or more.

**The set tells the device classes apart.**

| Class | `sgai-video-decoders` | `sgai-image-over-video` | `sgai-html-over-video` |
|---|---|---|---|
| D1 | ≥ 2 | 1 | 1 |
| D2 | 2 | 0 | 0 |
| D3 | 1 | 1 | 1 |
| D4 | 1 | 1 | 0 |
| D5 | 1 | 0 | 0 |

No two rows are equal.

#### 5.8.3 The window's declarations, forwarded

| Parameter | Value | When |
|---|---|---|
| `sgai-allowed-layouts` | The value of the window's `@allowedLayouts`, unchanged. | Required whenever the window declares `@allowedLayouts` (PLY-15). Absent otherwise; the family default then binds. |
| `sgai-custom-region` | The value of the window's `@customRegion`, unchanged. | Required whenever the window declares `@customRegion` (PLY-16). |

They are not sent for inherited linear events.

#### 5.8.4 Sending, omitting, extending

- Each parameter is appended to the query of `@uri` as `name=value`,
  separated by `&`, with `?` first when `@uri` has no query. Names and values
  are percent-encoded per IETF RFC 3986; the space of a list value is
  encoded as `%20`.
- A parameter without a value the Player can determine, or chooses not to
  disclose, is omitted, never sent empty or with a placeholder (PLY-13). An
  omitted parameter is undetermined, not "no" (DOC-14).
- The prefix `sgai-` is reserved to this specification. A parameter the
  Player adds that is not reserved carries a vendor prefix of the form
  `x-<vendor>-` (PLY-14), for example `x-acme-model`.
- The APS answers with or without any of them (APS-15).

```
GET /nl/overlay/1?slot=mid1&sid=6e2f&sgai-video-decoders=1&sgai-image-over-video=1
    &sgai-allowed-layouts=overlay-lower-third%20squeezeback-l-shape-upper-left HTTP/1.1
Host: aps.example.com
```

(The request line is folded here for width.)

#### 5.8.5 Two sources on one URL

The Publisher's query, the `RequestParam` output and the Player's reserved
parameters share the URL. They cannot collide on the reserved names, which
carry the `sgai-` prefix; the Publisher's and the vendor's are theirs to keep
apart.

### 5.9 Declaring and deriving the pause-delivery measurement

What is worth measuring on a pause slot is how much of the paused interval
carried an ad, not how many pauses occurred: the number of pauses is the
viewer's, and a figure that moves for reasons no party influences reports
nothing about how well the slot was served. The filled fraction can be
influenced, by the APS returning candidates that keep the slot filled.

**Declaring it.** Content carrying pause windows requests the base
`PlayList` metric (DASH Annex D.4.6) with the base `Metrics` element (DASH §5.9) at MPD
level (PUB-13). The base requires at least one `Reporting` descriptor and
defines no reporting scheme (*"No reporting scheme is specified in this
document"*, DASH §5.9.4); the scheme is the service provider's.

```xml
<Metrics metrics="PlayList">
  <Reporting schemeIdUri="urn:example:reporting:2026" value="collector-1"/>
</Metrics>
```

**Deriving it.** The `PlayList` metric is *"A list of playback periods. A
playback period is the time interval between a user action and whichever
occurs soonest of the next user action, the end of playback or a failure that
stops playback"* (Table D.5). Two of its fields carry what a pause slot
needs:

- an entry's `starttype`, whose values include `Resume` — *"Resume from
  pause"*;
- a trace entry's `stopreason`, whose values include `UserRequest` and
  `Rebuffering`.

The **paused interval** is the interval from the end of a playback period
whose last trace entry stopped on `UserRequest` to the `start` of the next
entry whose `starttype` is `Resume`. A period that stopped on `Rebuffering`
is not a pause, and no pause window triggered (PLY-88). The **filled
fraction** is the time the pause ad was on screen within that interval,
divided by the interval.

No metric is added (DOC-33), and how a measurement reaches anyone is out of
scope, as it is for the base: *"This document does not define mechanisms for
reporting metrics"* (DASH §5.9.1).

### 5.10 XML schema of the extension namespace

#### 5.10.1 Schema

```xml
<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           xmlns:svta="urn:svta:dash:sgai:2026"
           xmlns:dash="urn:mpeg:dash:schema:mpd:2011"
           targetNamespace="urn:svta:dash:sgai:2026"
           elementFormDefault="qualified"
           attributeFormDefault="unqualified">

  <xs:import namespace="urn:mpeg:dash:schema:mpd:2011"
             schemaLocation="DASH-MPD.xsd"/>

  <!-- Simple types -->
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

  <xs:simpleType name="LayoutTokenListType">
    <xs:list itemType="svta:LayoutTokenType"/>
  </xs:simpleType>

  <xs:simpleType name="PercentType">
    <xs:restriction base="xs:decimal">
      <xs:minInclusive value="0"/>
      <xs:maxInclusive value="100"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="PercentRectType">
    <xs:restriction>
      <xs:simpleType>
        <xs:list itemType="svta:PercentType"/>
      </xs:simpleType>
      <xs:length value="4"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="NeverType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="never"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="DismissAfterType">
    <xs:union memberTypes="xs:duration svta:NeverType"/>
  </xs:simpleType>

  <xs:simpleType name="LinearRelationType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="supersede"/>
      <xs:enumeration value="on-top"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="OnTopOnlyType">
    <xs:restriction base="svta:LinearRelationType">
      <xs:enumeration value="on-top"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="FamilyType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="overlay"/>
      <xs:enumeration value="pause"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="OnExhaustedType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="repeat"/>
      <xs:enumeration value="request-again"/>
      <xs:enumeration value="stop"/>
    </xs:restriction>
  </xs:simpleType>

  <xs:simpleType name="URIListType">
    <xs:list itemType="xs:anyURI"/>
  </xs:simpleType>

  <!-- Opportunity windows (children of dash:Event) -->
  <xs:element name="OverlayPresentation" type="svta:OverlayPresentationType"/>
  <xs:complexType name="OverlayPresentationType">
    <xs:sequence>
      <xs:any namespace="##other" processContents="lax" minOccurs="0" maxOccurs="unbounded"/>
    </xs:sequence>
    <xs:attribute name="uri" type="xs:anyURI" use="required"/>
    <xs:attribute name="durationCap" type="xs:unsignedLong" use="required"/>
    <xs:attribute name="earliestResolutionTimeOffset" type="xs:unsignedLong"/>
    <xs:attribute name="allowedLayouts" type="svta:LayoutTokenListType"/>
    <xs:attribute name="customRegion" type="svta:PercentRectType"/>
    <xs:attribute name="linearRelation" type="svta:LinearRelationType"/>
    <xs:anyAttribute namespace="##other" processContents="lax"/>
  </xs:complexType>

  <xs:element name="PauseAdPresentation" type="svta:PauseAdPresentationType"/>
  <xs:complexType name="PauseAdPresentationType">
    <xs:sequence>
      <xs:any namespace="##other" processContents="lax" minOccurs="0" maxOccurs="unbounded"/>
    </xs:sequence>
    <xs:attribute name="uri" type="xs:anyURI" use="required"/>
    <xs:attribute name="durationCap" type="xs:unsignedLong" use="required"/>
    <xs:attribute name="earliestResolutionTimeOffset" type="xs:unsignedLong"/>
    <xs:attribute name="allowedLayouts" type="svta:LayoutTokenListType"/>
    <xs:attribute name="executeOnce" type="xs:boolean" default="false"/>
    <xs:attribute name="linearRelation" type="svta:OnTopOnlyType"/>
    <xs:anyAttribute namespace="##other" processContents="lax"/>
  </xs:complexType>

  <!-- Non-linear resolution document -->
  <xs:element name="OverlayList" type="svta:OverlayListType"/>
  <xs:complexType name="OverlayListType">
    <xs:sequence>
      <xs:element name="Ad" type="svta:AdType" minOccurs="0" maxOccurs="unbounded"/>
      <xs:any namespace="##other" processContents="lax" minOccurs="0" maxOccurs="unbounded"/>
    </xs:sequence>
    <xs:attribute name="family" type="svta:FamilyType" use="required"/>
    <xs:attribute name="dismissAfter" type="svta:DismissAfterType"/>
    <xs:attribute name="validFor" type="xs:duration"/>
    <xs:attribute name="onExhausted" type="svta:OnExhaustedType"/>
    <xs:anyAttribute namespace="##other" processContents="lax"/>
  </xs:complexType>

  <xs:complexType name="AdType">
    <xs:sequence>
      <xs:element name="RenderableAsset" type="svta:RenderableAssetType" maxOccurs="unbounded"/>
      <xs:element name="Tracking" type="dash:EventStreamType" minOccurs="0"/>
      <xs:element ref="svta:ClickThrough" minOccurs="0"/>
      <xs:element ref="svta:AdSystem" minOccurs="0"/>
      <xs:element ref="svta:AdTitle" minOccurs="0"/>
      <xs:element ref="svta:Advertiser" minOccurs="0"/>
      <xs:any namespace="##other" processContents="lax" minOccurs="0" maxOccurs="unbounded"/>
    </xs:sequence>
    <xs:attribute name="duration" type="xs:duration" use="required"/>
    <xs:anyAttribute namespace="##other" processContents="lax"/>
  </xs:complexType>

  <xs:complexType name="RenderableAssetType">
    <xs:attribute name="src" type="xs:anyURI" use="required"/>
    <xs:attribute name="mimeType" type="xs:string" use="required"/>
    <xs:attribute name="layout" type="svta:LayoutTokenType" use="required"/>
    <xs:attribute name="rect" type="svta:PercentRectType"/>
    <xs:attribute name="background" type="xs:anyURI"/>
    <xs:anyAttribute namespace="##other" processContents="lax"/>
  </xs:complexType>

  <!-- Carriers shared by both resolution documents -->
  <xs:element name="ClickThrough" type="svta:ClickThroughType"/>
  <xs:complexType name="ClickThroughType">
    <xs:attribute name="uri" type="xs:anyURI" use="required"/>
    <xs:attribute name="trackingUris" type="svta:URIListType"/>
    <xs:anyAttribute namespace="##other" processContents="lax"/>
  </xs:complexType>

  <xs:element name="AdSystem" type="xs:string"/>
  <xs:element name="AdTitle" type="xs:string"/>
  <xs:element name="Advertiser" type="xs:string"/>

  <!-- Attribute on the MPD element of a List MPD -->
  <xs:attribute name="dismissAfter" type="svta:DismissAfterType"/>

</xs:schema>
```

The global attribute `svta:dismissAfter` is the namespace-qualified form used
on a List MPD's `MPD` element; on `<svta:OverlayList>` the same declaration
is the unqualified `@dismissAfter`. Co-occurrence rules that XML Schema 1.0
does not express — `@rect` if and only if `@layout="custom"`, `@background`
if and only if `@layout="squeezeback-double-box-background"`,
`@customRegion` only with `custom` in `@allowedLayouts`, `@onExhausted` on
pause documents only, containment of `@rect`, and `@mimeType` among the three
forms — are normative in chapter 5 and are checked as §5.10.2 states.

#### 5.10.2 Validating a resolution document

The base schema processes foreign content with `processContents="lax"`: a
validator that has not been given this specification's schema skips every
`svta` element, and the tracking carrier inside it, and still reports the
document valid. That report has not checked the carrier at all. A resolution
document is valid under this specification when all of the following hold:

1. **List MPD.** The document is valid against the base schema
   (`DASH-MPD.xsd`) **with the schema of §5.10.1 loaded**, so that every
   `svta` element and attribute present is validated rather than skipped; it
   conforms to DASH §8.14; and every sub-MPD it imports conforms to DASH §8.15.
2. **`<svta:OverlayList>`.** The document is valid against the schema of
   §5.10.1, which imports `DASH-MPD.xsd`: every `<svta:Tracking>` is thereby
   validated against the base `EventStreamType`, and every `Event` in it
   against the base `EventType`.
3. **Co-occurrence and value rules** of chapter 5 that the schema does not
   express are checked by the validator or by the Player (PLY-18, PLY-21).
4. **A validator reports which schemas it loaded.** A report that does not
   state that the schema of §5.10.1 was loaded is not a report of validity
   under this specification.

---

## 6. Interfaces

### 6.1 The interfaces, and who is on each side

| Interface | From → To | Transport | Payload | Defined by |
|---|---|---|---|---|
| MPD fetch | Player → Publisher CDN | HTTPS GET | DASH MPD with SGAI events | Base; the events: §5.1 |
| Primary media | Player → Publisher CDN | HTTPS GET | Segments | Base |
| Resolution request | Player → APS | HTTPS GET | Query parameters (§5.8) | This specification |
| Resolution response | APS → Player | HTTPS, `200` | List MPD, single-period alternative MPD, or `<svta:OverlayList>` | Base (linear); this specification (non-linear) |
| Sub-MPD and ad media | Player → ad CDN | HTTPS GET | SPS MPD, segments, images, HTML | Base (MPD, segments); §3.5 (forms) |
| Tracking beacons | Player → tracking endpoints | HTTPS GET, response ignored | none | Base callback semantics (DASH §5.10.4.5) |
| Click-tracking | Player → tracking endpoints | HTTPS GET on activation, response ignored | none | §5.6 |
| Decision request and response | APS ↔ ADS | agreed bilaterally | typically VAST, not required | Out of scope |

The Player talks to the APS and never to the ADS.

```
  Publisher CDN                                      ad CDN, tracking
      ^  | MPD with                                        ^
      |  | windows and events                              | sub-MPDs, media,
      |  v                                                 | beacons, clicks
   +-----------------------------------------------------------+
   |                         Player                            |
   |  validates against the MPD · selects per device · renders |
   +-----------------------------------------------------------+
                 | resolution request        ^ resolution document
                 | (@uri + parameters)       | (List MPD / OverlayList)
                 v                           |
              +---------------------------------+     decision
              |               APS               |<------------------> ADS
              | converts the decision, carries  |  (typically VAST;
              | the ADS's tracking schedule     |   out of scope)
              +---------------------------------+
```

### 6.2 The linear flow

1. The Player fetches the main MPD. Linear opportunities are
   `InsertPresentation` or `ReplacePresentation` events (§5.1.1, §5.1.2).
2. Between the event's earliest resolution time and its presentation time,
   the Player resolves `@uri` against the APS: *"The alternative MPD is
   fetched from the URL specified in AlternativeMPDEventType@uri and is
   resolved when the playhead is between the ERT and PRT"* (DASH §5.16.2.2.1,
   step 2). The base notes that randomising the instant *"can be useful … to
   avoid overloading the servers"* (DASH §5.16.2.2.6, NOTE 1).
3. The APS obtains the decision from the ADS and returns a List MPD, each
   candidate a Linked Period importing an SPS sub-MPD (§5.2.1), or the empty
   List MPD (§5.2.3).
4. The Player validates the candidates, drops what it may, and resolves the
   Linked Periods, which *"are not to be resolved earlier than PeriodStart -
   ImportedMPD@earliestResolutionTimeOffset"* (DASH §5.3.2.6.1).
5. At PRT the event executes: the alternative presentation replaces the
   output of the primary content. The Player plays the candidates in order,
   enforces the cap (§4.5.4) and fires the sub-MPDs' callback beacons.
6. The main presentation resumes at RT: PRTA for an insertion; for a
   replacement, `PRT + @returnOffset` if present, otherwise PRTA + APDA
   with `@clip="false"`, otherwise PRT + APDA (Table 57).

A failed execution at any step leaves the primary content playing
(PLY-38, PLY-39).

### 6.3 The overlay flow

1. The main MPD carries an overlay window (§5.1.3).
2. From the window's earliest resolution time — `Event@presentationTime`
   minus `@earliestResolutionTimeOffset`, 60 seconds by default — and no
   earlier (PLY-6), the Player MAY resolve it; at the latest it resolves when
   the window starts. The request carries the forwarded declarations and any
   capability parameters (§5.8).
3. The APS returns an `<svta:OverlayList family="overlay">` (§5.2.2), or the
   empty one.
4. When the window starts, the Player checks the document is still usable
   (PLY-9), validates it against the window's declarations, selects one
   option per candidate (§4.5.3) and presents the candidates in sequence
   (PLY-46) over the playing primary content, within the span and the cap.
5. Each candidate's `<svta:Tracking>` fires from the instant it starts
   (PLY-82). A ClickThrough fires on activation (PLY-84).
6. The window ends when the span ends, the cap is reached, the candidates
   are exhausted, or the viewer dismisses the slot.

An attempt that produces no document with candidates moves to the next
overlapping overlay window (PLY-38), and with none the primary content just
continues.

### 6.4 The pause flow

1. The main MPD carries a pause window (§5.1.4) and a `Metrics` request for
   `PlayList` (§5.9).
2. The Player MAY resolve the window ahead of any pause, from the window's
   earliest resolution time, and holds the document for its usable lifetime
   (§5.2.5).
3. When the viewer pauses inside the span, the Player uses the held document
   if it is still usable, or requests one (PLY-11, PLY-9). A pause outside
   every pause window requests nothing.
4. It presents the candidates in sequence over the paused frame or
   fullscreen (PLY-61), suspending any overlay (PLY-52). In live content its
   presentation time stays frozen inside the window (PLY-62).
5. When the candidates run out while the viewer is still paused, the
   document's exhaustion behaviour applies (PLY-65).
6. When the viewer resumes, the pause ad is removed within one frame, its
   remaining beacons are not fired, and the primary content continues from
   where it stopped (PLY-57 to PLY-60).

### 6.5 The resolution response

| APS response | What the Player does |
|---|---|
| `200` with a valid resolution document of the requested family carrying candidates | Validates and presents (§4.5.3). Candidates that turn out unrenderable end at the primary content (PLY-41). |
| `200` with a valid resolution document carrying no candidates | Failed execution; next overlapping window of the family (PLY-39). |
| `200` with a document of the wrong family | Failed execution; next overlapping window (PLY-42). |
| `200` with a body that does not parse or is not valid | Failed execution; next overlapping window (PLY-39). |
| Any final status other than `200` | Failed execution; next overlapping window (PLY-39). |
| No response, transport failure | Failed execution; next overlapping window (PLY-39). |

An APS that has nothing to serve answers with the empty document (APS-4),
never with an error status: an unfilled opportunity is then reported as
unfilled, and error codes keep one meaning.

### 6.6 From a decision document to a resolution document (informative)

The ADS answers in its own format; the conversion into the resolution
document is the APS's and is not defined here. The table shows that every ad
behaviour a VAST-based ADS expresses has a place in the resolution document,
which is what lets an APS fed by VAST build one using only the semantics of
this specification. VAST is named because it is the typical case; the ADS is
not bound to it. Annexes A.7 and C.8 work two conversions through.

| Behaviour a VAST response can express | VAST element (illustrative) | Resolution document |
|---|---|---|
| A pod of ads in order | several `<Ad>`, `@sequence` | List MPD Periods, or `<svta:Ad>` elements, in document order |
| A linear creative, its encodings | `<Linear>`, `<MediaFiles>/<MediaFile>` | SPS sub-MPD, one Representation per encoding |
| A creative's duration | `<Duration>` | Linked Period `@duration`; `<svta:Ad>@duration` |
| A non-linear creative (image, HTML) | `<NonLinear>` with `<StaticResource>`, `<HTMLResource>`, `<IFrameResource>` | `<svta:RenderableAsset>` with `image/*` or `text/html` |
| Alternative renditions of one ad | several resources or creatives of one `<Ad>` | several `<svta:RenderableAsset>` in preference order |
| Impression and progress tracking | `<Impression>`, `<TrackingEvents>/<Tracking event="…">` | callback events: in the sub-MPD (linear), in `<svta:Tracking>` (non-linear) |
| Click-through and click-tracking | `<ClickThrough>`, `<ClickTracking>`, `<NonLinearClickThrough>`, `<NonLinearClickTracking>` | `<svta:ClickThrough>` |
| Skippable after an offset | `@skipoffset` | `@svta:dismissAfter` / `@dismissAfter` |
| Ad system, title, advertiser | `<AdSystem>`, `<AdTitle>`, `<Advertiser>` | §5.7 elements, optional |
| No fill | a response with no `<Ad>` | the empty resolution (§5.2.3) |
| Wrapper chains | `<Wrapper>`, `<VASTAdTagURI>` | resolved by the APS before it answers; invisible to the Player |
| An ad with tracking and no media | `<Ad>` with no `<MediaFile>` | not a candidate: a resolution document cannot carry an ad with nothing to render; §8.10 |
| A universal ad identifier | `<UniversalAdId>` | not carried; stays on the ADS side (§5.7) |
| An error signalled by the ADS | `<Error>` | the APS's reaction is part of the APS-to-ADS contract; the Player observes an empty resolution or a failed execution |

---

## 7. Expected behaviour

### 7.1 How to read this chapter

Each section states, for one scenario, what the Publisher declares, what the
APS returns, and what the Player does on each device class of §3.6. The
obligations are those of chapter 4; this chapter applies them. "Declines" or
"skips" is a defined outcome and not a failure: the Player continues with the
primary content, and no visible artefact appears. The annexes walk each
scenario with complete documents.

### 7.2 Linear break — pre-roll and mid-roll

**Declared.** An `InsertPresentation` (static MPDs only, DASH §5.16.3) or
`ReplacePresentation` event, with a cap. **Returned.** A List MPD of one or
more candidates, each a video.

| Class | Player |
|---|---|
| D1, D2 | Plays the first renderable candidate on one decoder; a second decoder MAY pre-buffer the ad. Enforces the cap at playback. |
| D3, D4, D5 | The same on its single decoder: the linear ad and the primary content are sequential, not concurrent. |

The viewer sees a full-screen ad of bounded duration, then the primary
content — from its first frame for a pre-roll, and at or near the slot
position for a mid-roll. With `@clip="true"`, a replacement that executes
late is shortened so that its end stays where the Publisher scheduled it
(Annex B).

### 7.3 Multi-ad break

**Declared.** One linear event with a cap on the whole break; how many ads
fill it is the ADS's. **Returned.** A List MPD of N candidates in order.

On every class the Player plays the candidates back to back in document
order, reusing its decoder (D3 to D5) or pre-buffering the next ad on the
second one (D1, D2). It MAY drop, before play, a candidate whose declared
duration would push the break past the cap (PLY-35), keeps the order of the
rest (PLY-36), and stops at the cap even mid-ad (PLY-24, PLY-26).

### 7.4 Coexisting overlay

**Declared.** An overlay window with a cap and, typically, allowed layouts.
**Returned.** Candidates whose options are typically video, HTML and image
forms in several layouts.

| Class | Player |
|---|---|
| D1 | Every form is renderable; the first option whose layout the window admits wins. |
| D2 | Renders a video option (second decoder); skips image and HTML options, which it cannot composite; a double box with a video ad and no background is renderable if admitted. |
| D3 | Skips video options (no second decoder); renders the first HTML or image option. |
| D4 | Skips video and HTML options; renders the first image option. |
| D5 | Renders nothing: every option needs a surface or a decoder it lacks. Declines. |

The primary content keeps playing in every case. A candidate with no
renderable option is skipped for the next (PLY-20); when none remains, the
window presents nothing.

### 7.5 Sequenced forms within one slot

A window whose document carries several candidates presents them one after
another, in document order, each starting when the previous one ends
(PLY-46); at most one non-linear form is on screen at any instant (PLY-45).
A 30-second window whose document carries three 10-second candidates A, B, C
presents A, then B, then C. The cap bounds the sum (PLY-47).

### 7.6 Hybrid: a linear break with an overlay on top

**Declared.** A linear event and an overlay window whose span contains the
event's presentation time and which declares `@linearRelation="on-top"`,
typically with a restricted layout set. **Returned.** Two independent
resolution documents, one per opportunity; the ADS does not cross-reference
them.

| Class | Player |
|---|---|
| D1 | Plays the linear ad and composites the overlay on top, on the second decoder for a video form or on an image or HTML surface. |
| D2 | Composites a video overlay on the second decoder; declines image and HTML overlays; the linear ad plays either way. |
| D3 | Composites an image or HTML overlay on top: the linear ad holds the one decoder the primary content released (DASH §4.2), and the overlay needs one surface. |
| D4 | Composites an image overlay; declines an HTML one. |
| D5 | Plays the linear ad; declines the overlay. |

**While composited over the alternative presentation**, the overlay's cap
accrues on the timeline of the presentation being output (PLY-31): during an
insertion the primary timeline stops, and the overlay's time runs with the
linear ad. The form ends at the latest when the alternative presentation
ends; the window then continues over the primary content for what remains of
its span and its cap.

**Without `on-top`**, a Player of this specification plays the break and
presents the overlay only over the primary content around it (PLY-49).

### 7.7 Pause-triggered ad

**Declared.** A pause window with a cap, typically `pause-fullscreen` and
`pause-partial` allowed. **Returned.** Pause candidates with image, HTML and
optionally video options, and an exhaustion behaviour.

| Class | Player |
|---|---|
| D1 | Renders the first admissible option; the second decoder is free for a video. |
| D2 | Renders a video option on the second decoder, over the paused frame held by the first; declines image and HTML options. |
| D3 | Renders an HTML or image option over the paused frame. It MAY instead release the primary content's decoder to play a video option (PLY-56), restoring the position on resume. |
| D4 | Renders an image option; the same release applies to video. |
| D5 | Declines (§5.3.7). |

A pause outside every pause window shows nothing. On resume the pause ad is
removed within one frame and the primary content continues from where it
stopped (PLY-57, PLY-59). **Live content:** the Player's presentation time
stays frozen inside the window while the viewer is paused, whatever the live
edge does (PLY-62); a jump to the live edge after resuming is outside the
window. **Once per session:** on a window with `@executeOnce="true"`, a later
pause inside it shows nothing, unless the earlier pause produced no rendered
ad (PLY-63, PLY-64). **Exhaustion:** `repeat` plays the sequence again,
`request-again` asks the APS for more, `stop` leaves the paused frame
(PLY-65).

### 7.8 An overlay window crossing a pause window

An overlay is on screen when the viewer pauses inside a pause window. The
Player suspends the overlay and presents the pause ad (PLY-52), fullscreen or
partial, as the only ad surface. On resume it removes the pause ad and
restores the overlay from where it was suspended if the overlay window is
still active (PLY-53); the overlay's clock followed the primary timeline and
froze during the pause, so no cap was spent (PLY-31). If the overlay window
expired during the pause, the overlay surface stays clear (PLY-54).

| Class | Player |
|---|---|
| D1 | Overlay suspended; pause ad shown (highest form admitted); overlay restored. |
| D2 | Overlay (video) suspended; a video pause ad shown on the second decoder if offered, else the paused frame stays clean; overlay restored. |
| D3 | HTML or image overlay suspended; HTML or image pause ad shown; overlay restored. |
| D4 | Image overlay suspended; image pause ad shown; overlay restored. |
| D5 | Neither is rendered; pause and resume have no ad effect. |

The same priority holds against a linear ad: a pause inside a pause window
applicable to the linear presentation suspends the linear ad, shows the
pause ad, and resumes the linear ad where it stopped (PLY-55).

### 7.9 One ad, ordered options, across the device classes

**Declared.** An overlay window with one device-agnostic allowed-layout set
that includes `squeezeback-double-box-background`,
`squeezeback-l-shape-upper-left`, `overlay-lower-third` and `linear`.
**Returned.** One candidate with four options in order: (1) double box with a
video ad and an image background; (2) L-shape with an image creative; (3)
image lower-third; (4) full-screen video takeover.

**When the Player declares nothing**, the APS returns all four, and each
Player walks them:

| Class | Option 1 | Option 2 | Option 3 | Option 4 | Renders |
|---|---|---|---|---|---|
| D1 | satisfiable | — | — | — | 1 |
| D2 | fails: background is an image | fails: image creative | fails: image | satisfiable | 4 |
| D3 | fails: needs 2 decoders | satisfiable | — | — | 2 |
| D4 | fails: needs 2 decoders | satisfiable | — | — | 2 |
| D5 | fails | fails | fails | satisfiable | 4 |

**When the Player declares its capabilities** (§5.8.2), an APS that narrows
emits the first surviving option alone, and every class lands on the same
option; a Player that declares nothing receives all four and walks them. The
Player checks whatever arrives (PLY-19). Neither division of the
responsibility is canonical (APS-6, APS-7).

### 7.10 Double box, the three-element layout

A double box puts the shrunk primary content and the ad side by side and
fills the uncovered bands with the advertiser's background image, or black
when the layout is `squeezeback-double-box`.

| Class | Video ad + background | Image ad + background | HTML ad + background |
|---|---|---|---|
| D1 | renders | renders | renders |
| D2 | declines: the background is an image | declines | declines |
| D3 | declines: needs 2 decoders | renders | renders |
| D4 | declines | renders | declines: no HTML |
| D5 | declines | declines | declines |

A declined option passes to the next one (PLY-18).

### 7.11 ClickThrough

On activation — a select on a remote, a tap — every class opens the
ClickThrough destination (or hands it off) and fires each click-tracking URL
once (PLY-84). This is separate from the timeline beacons; the click has no
presentation time. A legacy Player renders the ad and leaves the click inert.

### 7.12 Overlapping windows of one family

Two overlay windows overlap; the Player orders them by presentation time and
position (PLY-40) and attempts the first. The paths:

1. The first answers with the empty document and the second with an ad: the
   first attempt failed, the second is attempted, the viewer sees the
   second's ad. Nothing distinguishes this, at the Player, from a first
   window that could not be reached.
2. Both answer with the empty document: the chain is exhausted and the
   primary content continues.
3. Neither can be reached and no further window exists: the chain is
   exhausted with no document, and the primary content continues.
4. The first answers with candidates none of which the device can render:
   this is not a failed execution, and the Player continues with the primary
   content without attempting the second (PLY-41).

Each window binds its own candidates with its own declarations (PLY-43). The
chain selects the window and is device-agnostic; the device class governs
only what renders inside it.

### 7.13 A window that supersedes a linear break

**Declared.** A linear event and an overlay window whose span contains the
event's presentation time and which declares `@linearRelation="supersede"`.
**Returned.** A resolution document for the window; a List MPD for the
break, only if it is executed.

The Player presents the window and does not execute the break (PLY-48). It
executes the break only when the window **presents no ad**: every attempt on
the window's chain failed, or none of its candidates is renderable. The
timing of that fallback follows the base rules for an event that executes
after its presentation time:

- **Known before PRT.** The break executes at PRT as authored.
- **Known after PRT, while the event is still active** (PRT ≤ PHP < EAP).
  The break executes late, at PRTA = PHP, *"PRT ≤ PRTA ≤ EAP"* (Table 57). A
  replacement with `@clip="true"` still ends at PRT + APDmax, so it is
  shortened; `@startWithOffset` applies as the base defines. An insertion
  starts late and plays its full cap.
- **Known after EAP.** *"If the event is no longer active, it is ignored"*
  (DASH §5.16.2.2.1, step 4): the break is not executed and the primary content
  continues.

To keep the fallback reachable, the Player SHOULD resolve the window early
enough to know the outcome before PRT, and MAY resolve the break's `@uri`
within its own earliest-resolution interval in parallel, as the base
permits. A Publisher who wants the break to remain a fallback throughout the
window authors its `Event@duration` to cover the window's span. A superseded
event that is not executed has not been executed: its E.c stays unchanged.

| Class | Result (window offering an image L-shape and an HTML lower-third) |
|---|---|
| D1 | L-shape rendered; break not executed. |
| D2 | No option renderable; the break executes. |
| D3, D4 | L-shape rendered; break not executed. |
| D5 | No overlay surface; the break executes. |
| Legacy | Ignores the window; plays the break. |

When the window fails to resolve — no answer, an error, an unparsable body,
or the empty document — every class executes the break. No Player presents
both.

### 7.14 A non-linear ad over a replacement that is not advertising

A Publisher replaces a span with a blackout slate, an alternative
presentation of its own, and wants an overlay during it. The overlay window
is declared in the **slate's** MPD, over the slate's timeline (PUB-12,
PLY-51). The slate's replacement event MAY declare no `@maxDuration`, when
the blackout's end is unknown; it then runs until it terminates, as the base
defines. The budget is that of a hybrid break: the slate holds the decoder the
primary content released.

| Class | Player |
|---|---|
| D1 | Composites the overlay over the slate (second decoder for video; image or HTML surface otherwise). |
| D2 | Composites a video overlay; declines image and HTML. |
| D3 | Composites an image or HTML overlay. |
| D4 | Composites an image overlay; declines HTML. |
| D5 | Declines. |
| Legacy | Plays the slate; ignores the window. |

A window on the **primary** timeline over the same span behaves by its
relation: with none it presents only over the primary content and ends when
the slate begins (PLY-49); with `on-top` it is composited over the slate
(PLY-50); with `supersede` it would stand in for the replacement and show the
programme the Publisher blacked out (§5.1.6). Only the overlay is an ad: it
carries the tracking, the ClickThrough and the cap; the slate carries none.

### 7.15 Restricted layouts and the `custom` layout

**Restricted layouts.** The Player forwards `@allowedLayouts` unchanged
(PLY-15); the APS returns only options inside it (APS-9); the Player still
checks each option before rendering (PLY-19). With `overlay-lower-third` and
`squeezeback-l-shape-upper-left` allowed: D1, D3 and D4 render an image
L-shape; D2 and D5 have no renderable allowed layout and skip. The full-screen
takeover a D2 could have played is not offered, because the Publisher
excluded it. An APS that ignored the set and returned the takeover first
would see it discarded by the Player, who moves to the next option.

**`custom`.** With `custom overlay-lower-third` allowed and a region, the
Player forwards both (PLY-16). A Player that supports `custom` renders a
contained rectangle (PLY-21); one that does not treats the option as not
renderable and falls to the lower-third. A rectangle outside the region is
discarded without rendering. D5 skips as in every overlay case.

### 7.16 A Player that predates this specification

A legacy Player meets the windows and ignores them (§4.7); it never resolves
their `@uri`, and it removes the `svta` content of a List MPD while playing
the linear ad. Its outcome depends on the Publisher's authoring and not on the
device:

- **Live content, or on-demand content with no fallback authored** — the
  primary content plays uninterrupted, no ad is shown, no error surfaces.
- **On-demand content with a standard linear break authored under a
  superseding window** — the legacy Player plays the break, then the primary
  content.

A Player of this specification on the same document presents the window and
plays the break only when the window presents no ad (§7.13).

### 7.17 Viewer dismissal

The Player offers dismissal only once the declared delay has elapsed from the
start of the slot, and then for as long as the slot is on screen (PLY-74). A
dismissal ends every ad of the slot (PLY-75), fires the beacons scheduled up
to that instant and none after (PLY-77), and leaves the primary content where
it stands — nothing is compressed or skipped (PLY-76). On a linear slot, an
explicit base `@skipAfter` governs (§5.2.4). A slot with no declaration is not
dismissible.

### 7.18 Early resolution

The Player MAY resolve an overlay or pause window from its earliest
resolution time onward and not before (PLY-6, PLY-7), and holds the document
for its usable lifetime. When the opportunity fires with an expired document,
the Player resolves again and never presents the expired one; a
re-resolution without usable candidates is the empty resolution (PLY-9,
PLY-10). A Player that resolves only at the moment of the opportunity is
conformant (PLY-8).

### 7.19 Runtime failure during an accepted ad

A decode error, a malformed candidate or a network loss mid-ad aborts that
ad, and the primary content continues uninterrupted (PLY-86). Whether the
Player tries the next candidate or ends the slot is its policy (§8.4).

### 7.20 Playback speed

At 1.5x or 2x, ads play at the primary content's speed (PLY-67): a 10-second
ad at 2x occupies 5 seconds of wall clock (PLY-69). The cap and the beacon
schedule stay on the presentation timeline and do not change with the speed.

---

## 8. Implementation notes (informative)

### 8.1 What this chapter is

Guidance for implementers. It restates, per error condition, the normative
response of chapter 4 so that the chapter can be read on its own, and adds
advice where the normative text leaves a choice. Nothing here adds an
obligation.

**Continuing with the primary content** means, throughout: no visible
artefact — no freeze, no blank slate, no error overlay unless the application
explicitly opted in; no tracking beacon fired for the opportunity that failed;
and the primary content playing on its own timeline. Three different moves
lead there:

- **Window-level fall-through** (E1 to E4) moves to the next overlapping
  window of the family, and reaches the primary content only when the family
  is exhausted.
- **Candidate-level fall-through** (E7 to E9) moves to the next candidate of
  the document already obtained, and reaches the primary content only when the
  candidates are exhausted — never the next window.
- **Supersede fall-back**: when a superseding window presents no ad by either
  route, what continues is the inherited linear break it stood in for, not
  the bare primary content (§7.13).

### 8.2 The conditions, and what to do about each

| ID | Condition | Player response (chapter 4) | Player choices | Other actors |
|---|---|---|---|---|
| E1 | The resolution request fails at transport level (DNS, TCP, TLS, timeout before a final status) or returns a final status other than `200`, including an APS that refuses because a capability parameter is absent. | Failed execution; attempt the next overlapping window of the family; when all have been attempted, continue with the primary content (PLY-38, PLY-39). On a superseding window, execute the linear events it stands in for, with the base late-execution rules (PLY-48). | Retry within the interval between the earliest resolution time and the opportunity (§8.4); expose the failure to the application. | Publisher: declare a fallback window where continuity matters; one `EventStream` per family per Period (PUB-7). APS: answer without any capability parameter (APS-15). |
| E2 | `200`, but the body does not parse, has an unknown root element, or is not valid (§5.10.2). | As E1 (PLY-39); render nothing from that document. | Log the parse or validation failure. | APS: valid documents, tracking subtree included (APS-3). |
| E3 | `200`, a valid document whose `@family` is not the window's. | Failed execution; present none of its candidates; next window (PLY-42). | Report the mismatch. | APS: answer the slot requested (APS-2). |
| E4 | `200`, a valid document carrying no candidates. | Failed execution; next window; the opportunity is not consumed — an `@executeOnce` event stays executable and a once-per-session pause window stays available (PLY-39, PLY-44, PLY-64). | Report the opportunity as unfilled rather than failed. | APS: no-fill is the empty document, never an error (APS-4). ADS: no-fill is a legitimate decision. |
| E5 | The document arrives after the window has elapsed, or a document obtained early has expired when the opportunity fires. | Never extend a slot past its cap's bound (PLY-25); on a late replacement, `@clip` shortens (PLY-27). An expired document is never presented: re-resolve, and treat a re-resolution with no usable candidate as E4 (PLY-9, PLY-10). | Resolve early within the offset (PLY-6 to PLY-8); discard a document that lands after its window (§8.5). | Publisher: an offset of zero forbids early resolution (PUB-9). APS: declare `@validFor` (APS-21). |
| E6 | An overlay or pause window with no `@durationCap` (or no `Event@duration`), or any slot with a cap of zero. | No ads from an uncapped window; primary content (PLY-29). A zero cap does not fire (PLY-30). An inherited linear event with no `@maxDuration` is not this condition: it executes with its base semantics. | Report the defective declaration. | Publisher: a cap on every overlay and pause window (PUB-2); non-linear advertising with no fixed end is a chain of bounded windows. |
| E7 | No option of a candidate is satisfiable on the device. | Skip the candidate, try the next; primary content only when all are exhausted (PLY-20); not the next window (PLY-41). On a superseding window whose candidates are all unrenderable, execute the linear events (PLY-48). | Report the skip. | APS: options in preference order (APS-5). |
| E8 | An option names an inadmissible layout: outside §3.4.2, Publisher-private, bare `squeezeback` or `pause`, not in the serving window's set, of another family on a window that declares none, or `custom` unsupported or outside the region. | Do not render it; next option; skip the candidate when none passes (PLY-18 to PLY-21). Check against the window that served the candidate (PLY-43). | Report the rejected name. | Publisher: tokens of §3.4.2 only (PUB-4). APS: nothing outside the set received (APS-8, APS-9); `@rect` inside the region (APS-12). |
| E9 | A creative outside the three forms, or a non-AV asset URL on an IETF RFC 4337-bound `@mimeType` path. | Never render a form the device cannot render (PLY-4). | Skip the candidate as a non-conformant signal (PLY-5), and fall through as in E7. For an inadmissible form the device *can* render, rendering and skipping are both unconstrained (§8.6). | APS, Publisher: the three forms only (APS-10, PUB-17); non-AV assets as foreign-namespace content (APS-11). |
| E10 | A candidate's declared duration would exceed the cap, or its actual length exceeds its declared duration. | Stop at the bound even mid-ad, against actual length (PLY-24, PLY-26); stop beacons at the trim (PLY-80); round the converted duration up and admit an exact match (PLY-28); accrue nothing while the timeline does not advance (PLY-31); keep the survivors in order (PLY-36). | Drop before play on declared duration (PLY-35). | ADS: not bound by the cap (ADS-1). |
| E11 | Rendering an accepted ad fails: an ad segment returns an error, a decode error, a network loss. | Abort that ad; continue with the primary content (PLY-86). | Retry the segment before aborting; then skip to the next candidate or end the slot (§8.4). | APS: media reachable for the slot's duration. |
| E12 | An unknown scheme, element or namespace in the MPD or the resolution document. | Ignore it with what it contains; keep playing (DASH §5.2.1; PLY-83). | Log it; ignore the metadata elements entirely (PLY-85). | Publisher, APS: every construct at an admitted extension point (PUB-14). |
| E13 | A beacon or click-tracking request fails, or a beacon falls after a trim, a resume from a pause ad, or a dismissal. | Keep the ad and the primary content unaffected; beacon failures never reach the viewer. Do not fire after a trim (PLY-80), a resume (PLY-58) or a dismissal (PLY-77). De-duplicate per candidate, and per presentation on a List MPD (PLY-81). | Retry and log. | APS: beacons as callback events on the candidate's timeline (APS-16); ClickThrough in its carrier (APS-17). ADS: owns the schedule. |
| E14 | Two forms would share the screen: two non-linear forms at once; a pause during an overlay or a linear ad; an alternative presentation starting while a window presents. | At most one non-linear form (PLY-45); sequence in order (PLY-46). Pause: suspend the overlay or the linear ad, show the pause ad, restore on resume if the window is still open (PLY-52 to PLY-55). Alternative presentation: end the form unless the window declares `on-top` (PLY-49, PLY-50). | Release resources for a fullscreen pause ad (PLY-61). | No construct inverts the pause priority (DOC-24). |
| E15 | The pause candidates run out while the viewer is paused, or the pause window was already consumed. | Apply the declared behaviour, `stop` by default (PLY-65); `request-again` with an empty answer is `stop` (PLY-66); return to the primary content immediately on resume (PLY-60). Once per session: at most one pause ad per window (PLY-63). | Report the behaviour applied. | APS: declare `@onExhausted` (APS-22). |

### 8.3 Order of precedence

1. **Transport** (E1): no document, nothing downstream applies.
2. **Resolution document** (E2 to E5): unusable, misrouted, empty, late or
   expired. E2 to E4 put the Player on the fallback chain.
3. **The serving window's declarations** (E6, E8, E9, and E10's drop before
   play). E6 first: an uncapped overlay or pause window yields nothing.
4. **Per candidate, before rendering** (E7, E11 at decode).
5. **Per candidate, while rendering** (E10's trim, E14, E15).
6. **Tracking** (E13): never aborts an ad.

E12 applies wherever an unknown construct appears. The supersede fall-back
runs after steps 1 to 4 have left the window with no ad.

### 8.4 Retrying a resolution request

This specification fixes no retry count, backoff or deadline for the
resolution request. The base says of its own request: *"An HTTP GET request
can fail, however if the response contains the Retry-After HTTP header … the
HTTP client can attempt to retrieve the alternative MPD later"*, and that
*"This retry mechanism is out of scope of this document"* (DASH §5.16.2.2.6,
NOTE 4). A Player that retries does best to do so only while the opportunity is
still ahead, and to prefer moving to the next window of the chain over
retrying the first when the chain has one. A retry that succeeds is a
successful attempt; what counts as failure is only the final outcome of the
attempt.

The same freedom holds for a failed ad segment inside an accepted candidate:
retry, then skip to the next candidate, or end the slot. The primary content
continues in every case.

### 8.5 Late documents

A non-linear document that arrives after its window's span has ended has
nothing to present into; the Player discards it and presents nothing. A
document that arrives inside the span is presented for what remains of the
span and the cap. A pending request whose window has ended can be abandoned.
For linear events the base rules govern late execution, as §7.13 applies
them.

### 8.6 A creative whose media type is not admissible

Skipping it is permitted and advisable: it signals a non-conformant APS or
Publisher, and rendering it would hide the defect. When the device happens to
be able to render it, the specification does not require skipping; a Player
that renders it is not, for that alone, non-conformant.

### 8.7 Device-class fallbacks

A Player need not know its class by name. What it needs at selection time is
three facts — its free video decoders, and whether it can composite an image
or HTML over video — and the budget of §5.3.7. Two practical notes:

- **Count the primary content's decoder.** An overlay over the primary
  content, and an overlay over a linear ad, both leave one decoder for the ad
  (DASH §4.2).
- **A pause frees a decoder only if the Player chooses to free it.** Holding
  the paused frame keeps the decoder busy; releasing it and restoring the
  position on resume is a pause (PLY-56, PLY-59).

### 8.8 The live freeze and the time-shift buffer

The freeze keeps the pause ad admissible for as long as the viewer stays
paused. It does not make old media available: a live presentation can only
resume inside its time-shift buffer, and the base says of its own resumption
that *"If RT is in the past, the playback shall start from the oldest
available media segment (the edge of the timeshift buffer)"* (Table 62,
NOTE 1). A Player whose frozen position leaves the buffer during a long pause
resumes at the oldest available media when the viewer resumes; the pause ad
was dismissed at that instant in any case. Whether such a resumption is still
a pause in the sense of PLY-59 is left open (§8.13).

### 8.9 Resolving a pause window

Resolving on entry into the window and holding the document hides the APS
latency from a viewer who pauses; resolving at the pause keeps the decision
fresh. `@validFor` lets the APS choose per resolution: a long lifetime means
one resolution per window, `PT0S` means one per pause. A Player that resolves
early does well to randomise the instant inside the interval the offset allows, as
the base advises for its own events, to spread load across viewers entering
the window together.

### 8.10 Tracking-only decision entries

A decision may carry an ad with tracking and no media. A resolution document
cannot carry it as a candidate — there is nothing to render — so an APS
omits it. Whether to report the impression opportunity to the ADS some other
way is part of the APS-to-ADS contract.

### 8.11 Surfacing conditions to the application

No event names, payloads or delivery mechanism are defined, and a Player that
exposes nothing is conformant. Two distinctions carry the most operational
value: **unfilled** (E4) against **failed** (E1, E2, E3); and the misrouted
document (E3), which an operator cannot diagnose from the screen. An error
overlay is a visible artefact and breaks the continuation guarantee unless the
application opted in.

### 8.12 Deriving the pause-delivery measurement

A Player that reports metrics can compute, per pause, the paused interval
from its `PlayList` entries (§5.9) and the pause ad's on-screen time from its
own rendering log, and report the filled fraction however its reporting scheme
carries it. Counting pauses is not the measure: the viewer sets that number.

### 8.13 What this edition leaves open

The following questions are not settled by this edition. Where the
specification needed an answer to be implementable, it gives one, and says so
here so that a later edition can revisit it deliberately.

1. **SGAI event streams under the Advanced Linear profile.** Whether an
   Advanced Linear MPD carrying an SGAI event stream has a non-conforming
   Period, given *"Support for a restricted set of DASH events"* (DASH §8.13.1)
   and *"may not be presented"* (DASH §8.13.2.1). The annexes use the live and
   on-demand profiles. Needs input from the base specification's editors.
2. **Supersede timing.** §7.13 applies the base late-execution rules to a
   break executed after its window presented no ad; how early a Player must
   resolve to keep the fallback reachable is left to the Player.
3. **Which timeline an on-top window's cap accrues on.** §7.6 reads it as the
   timeline of the presentation being output, and ends the form when the
   alternative presentation ends.
4. **A live pause longer than the time-shift buffer** (§8.8).
5. **Precedence between the two base skip controls** on one linear event
   (§5.2.4 takes the event attribute first).
6. **A pause window inside an alternative presentation.** The `Metrics`
   request of PUB-13 sits at MPD level, and an SPS MPD may not carry
   `MPD.Metrics` (DASH §8.15.2); whether a pause window in an alternative
   presentation is covered by the main MPD's request is not settled
   [inferred: whether an alternative presentation reached through `@uri` is
   SPS-bound was not established; only `ImportedMPD` targets are].
7. **When a pause window is applicable during a linear ad** (PLY-55): this
   edition reads it as a window of the linear ad's own MPD or an `on-top`
   window of the triggering presentation.
8. **A pause cap.** A pause slot has no authored duration; the cap required on
   pause windows bounds one pass through a document's candidates (§4.5.4).
9. **The empty List MPD shape** (§5.2.3) rests on a zero-duration Period
   being acceptable under the List profile's CMAF constraints [inferred].

---

# Annexes

All annexes are informative. Host names are examples. Every document is
complete as it would travel, unless a comment says otherwise. Times in
`EventStream` elements use `timescale="1000"` (milliseconds).

## Annex A — Pre-roll

### A.1 The scenario

A viewer starts an on-demand episode. Before the first frame of the episode,
the Publisher allows up to 30 seconds of linear advertising and nothing
non-linear: it wants a clean hand-off from the ad to the programme. The ADS
fills the slot with two ads, 15 and 10 seconds. The ads take over the screen;
when they end, the episode starts from its first frame.

The Publisher uses the base insertion event: the programme is on demand, and
an insertion leaves the programme's timeline intact.

### A.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT44M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/show42/ep07/</BaseURL>
  <Period id="main" start="PT0S">
    <!-- Pre-roll: an Alternative MPD Insertion event at the start. -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="1" presentationTime="0" duration="5000">
        <InsertPresentation uri="https://aps.example.com/linear/preroll?show=42&amp;ep=7"
                            earliestResolutionTimeOffset="0"
                            maxDuration="30000"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" bandwidth="3000000" width="1280" height="720"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

`@earliestResolutionTimeOffset="0"` makes the Player resolve at the start
of playback, the only time a pre-roll can be resolved. `Event@duration`
keeps the event active for the first 5 seconds, so a viewer who joins
slightly late still gets it.

### A.3 The List MPD

The APS answers `GET https://aps.example.com/linear/preroll?show=42&ep=7`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="list"
     profiles="urn:mpeg:dash:profile:list:2024"
     minBufferTime="PT2S"
     svta:dismissAfter="never">
  <Period id="ad-101" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="0">https://ads-cdn.example.com/cr/101/cr101.mpd</ImportedMPD>
    <svta:ClickThrough uri="https://brand-a.example.com/spring"
                       trackingUris="https://t.example.com/click?cr=101"/>
    <svta:AdSystem>ExampleAds</svta:AdSystem>
    <svta:AdTitle>Spring range, 15 s</svta:AdTitle>
  </Period>
  <Period id="ad-102" duration="PT10S">
    <ImportedMPD earliestResolutionTimeOffset="10">https://ads-cdn.example.com/cr/102/cr102.mpd</ImportedMPD>
    <svta:AdSystem>ExampleAds</svta:AdSystem>
    <svta:AdTitle>Coffee, 10 s</svta:AdTitle>
  </Period>
</MPD>
```

Each `Period` is a candidate; they play in document order. The second
`ImportedMPD` may be resolved from 10 seconds before its PeriodStart, that
is, 5 seconds into the first ad. The slot is not dismissible.

### A.4 The sub-MPDs

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/101/</BaseURL>
  <Period id="cr101" duration="PT15S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                 timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=101</Event>
      <Event presentationTime="0" id="2">https://t.example.com/start?cr=101</Event>
      <Event presentationTime="3750" id="3">https://t.example.com/q1?cr=101</Event>
      <Event presentationTime="7500" id="4">https://t.example.com/mid?cr=101</Event>
      <Event presentationTime="11250" id="5">https://t.example.com/q3?cr=101</Event>
      <Event presentationTime="15000" id="6">https://t.example.com/complete?cr=101</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" bandwidth="2500000" width="1280" height="720"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/102/</BaseURL>
  <Period id="cr102" duration="PT10S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                 timescale="1000">
      <Event presentationTime="0" id="11">https://t.example.com/imp?cr=102</Event>
      <Event presentationTime="5000" id="12">https://t.example.com/mid?cr=102</Event>
      <Event presentationTime="10000" id="13">https://t.example.com/complete?cr=102</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" bandwidth="2500000" width="1280" height="720"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The ADS chose the quartile schedule of the first ad and a three-beacon
schedule for the second; the APS transcribed both. The Player decides
neither. The beacon identifiers are unique across the two sub-MPDs: once
merged into the List MPD, the streams share one `@id` scope (PLY-81), and
the base ignores an event whose scheme, value and `@id` it has already
processed (*"Whenever an Event with previously processed combination of
values of the @schemeIdUri, @value, and @id attributes is encountered in
course of normal playback, and the Event@status attribute is absent, the
event will be ignored by the DASH client"*, DASH §5.10.2.4).

### A.5 The Player's walk-through

1. Playback starts; the insertion event is active at PRT = 0. The Player
   requests the List MPD.
2. It validates: two candidates, declared durations 15 s and 10 s. Converted
   to the cap's timescale they are 15000 and 10000; the sum, 25000, is under
   the cap of 30000 (PLY-28).
3. It resolves the first `ImportedMPD`, merges the Linked Period (its
   `@duration` stays 15 s, the imported one being equal), and plays it on its
   decoder. Beacons fire at 0, 3.75, 7.5, 11.25 and 15 s of the ad.
4. From 5 s into the first ad it resolves the second `ImportedMPD`, and plays
   it at 15 s.
5. At 25 s the alternative presentation ends; the main presentation resumes
   at RT = PRTA = 0 (insertion) and the episode starts from its first frame.

Had the second sub-MPD's `Period@duration` been PT12S, the Linked Period's
PT10S would have been kept: the base keeps the smaller value.

### A.6 Device classes

| Class | Behaviour |
|---|---|
| D1, D2 | Plays both ads on one decoder; the second decoder may pre-buffer ad 102 during ad 101. |
| D3, D4, D5 | Plays both ads on its single decoder, then the episode on the same decoder: the ads and the programme are sequential. |

Every class sees the same thing: 25 seconds of full-screen ads, then the
episode from its first frame. A legacy Player that implements the base
linear path does the same, removing the `svta` elements of the List MPD.

### A.7 Where this List MPD came from: an illustrative VAST response

The ADS in this deployment answers in VAST. This is one way an APS converts
it; nothing here is required.

```xml
<VAST version="4.2">
  <Ad id="101" sequence="1">
    <InLine>
      <AdSystem>ExampleAds</AdSystem>
      <AdTitle>Spring range, 15 s</AdTitle>
      <Impression><![CDATA[https://t.example.com/imp?cr=101]]></Impression>
      <Creatives>
        <Creative>
          <Linear>
            <Duration>00:00:15</Duration>
            <TrackingEvents>
              <Tracking event="start"><![CDATA[https://t.example.com/start?cr=101]]></Tracking>
              <Tracking event="firstQuartile"><![CDATA[https://t.example.com/q1?cr=101]]></Tracking>
              <Tracking event="midpoint"><![CDATA[https://t.example.com/mid?cr=101]]></Tracking>
              <Tracking event="thirdQuartile"><![CDATA[https://t.example.com/q3?cr=101]]></Tracking>
              <Tracking event="complete"><![CDATA[https://t.example.com/complete?cr=101]]></Tracking>
            </TrackingEvents>
            <VideoClicks>
              <ClickThrough><![CDATA[https://brand-a.example.com/spring]]></ClickThrough>
              <ClickTracking><![CDATA[https://t.example.com/click?cr=101]]></ClickTracking>
            </VideoClicks>
            <MediaFiles>
              <MediaFile delivery="streaming" type="application/dash+xml"
                         width="1920" height="1080">
                <![CDATA[https://ads-cdn.example.com/cr/101/cr101.mpd]]>
              </MediaFile>
            </MediaFiles>
          </Linear>
        </Creative>
      </Creatives>
    </InLine>
  </Ad>
  <Ad id="102" sequence="2">
    <InLine>
      <AdSystem>ExampleAds</AdSystem>
      <AdTitle>Coffee, 10 s</AdTitle>
      <Impression><![CDATA[https://t.example.com/imp?cr=102]]></Impression>
      <Creatives>
        <Creative>
          <Linear>
            <Duration>00:00:10</Duration>
            <TrackingEvents>
              <Tracking event="midpoint"><![CDATA[https://t.example.com/mid?cr=102]]></Tracking>
              <Tracking event="complete"><![CDATA[https://t.example.com/complete?cr=102]]></Tracking>
            </TrackingEvents>
            <MediaFiles>
              <MediaFile delivery="streaming" type="application/dash+xml"
                         width="1920" height="1080">
                <![CDATA[https://ads-cdn.example.com/cr/102/cr102.mpd]]>
              </MediaFile>
            </MediaFiles>
          </Linear>
        </Creative>
      </Creatives>
    </InLine>
  </Ad>
</VAST>
```

| VAST | List MPD |
|---|---|
| each `<Ad>`, in `@sequence` order | one `Period`, in document order |
| `<Duration>` | `Period@duration` of the Linked Period |
| `<MediaFile>` of type `application/dash+xml` | `ImportedMPD` (the sub-MPD already exists) |
| `<Impression>`, `<Tracking>` | callback events in the sub-MPD, at 0 and at the fractions of the duration the event names |
| `<ClickThrough>`, `<ClickTracking>` | `<svta:ClickThrough>` |
| `<AdSystem>`, `<AdTitle>` | §5.7 elements |
| no `@skipoffset` | `svta:dismissAfter="never"` |

Where the ADS returns progressive MP4 files instead, the APS packages or
references a DASH rendition; that step is the APS's.

## Annex B — Mid-roll

### B.1 The scenario

A live sports channel. Ten minutes into the session the broadcast goes to a
30-second break. The Publisher replaces that span of the live timeline with
an ad: the main presentation keeps advancing underneath, and the programme
resumes at the live position after the break. The ADS returns one 30-second
ad.

### B.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="dynamic"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     availabilityStartTime="2026-09-26T18:00:00Z"
     publishTime="2026-09-26T18:09:30Z"
     minimumUpdatePeriod="PT2S"
     timeShiftBufferDepth="PT30M"
     minBufferTime="PT2S">
  <BaseURL>https://live.example.com/sports1/</BaseURL>
  <Period id="live" start="PT0S">
    <!-- Mid-roll: an Alternative MPD Replacement event at 10 minutes. -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
                 timescale="1000">
      <Event id="7" presentationTime="600000" duration="30000">
        <ReplacePresentation uri="https://aps.example.com/linear/break?ch=sports1&amp;b=7"
                             earliestResolutionTimeOffset="20000"
                             maxDuration="30000"
                             returnOffset="30000"
                             clip="true"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" bandwidth="3000000" width="1280" height="720"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The event is a replacement because the MPD is dynamic: an insertion *"shall
not appear if the MPD type is "dynamic""* (DASH §5.16.3). The earliest resolution
time is 600000 − 20000 = 580000 ms.

### B.3 The List MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="list"
     profiles="urn:mpeg:dash:profile:list:2024"
     minBufferTime="PT2S"
     svta:dismissAfter="never">
  <Period id="ad-201" duration="PT30S">
    <ImportedMPD earliestResolutionTimeOffset="20">https://ads-cdn.example.com/cr/201/cr201.mpd</ImportedMPD>
    <svta:AdSystem>ExampleAds</svta:AdSystem>
    <svta:AdTitle>Car launch, 30 s</svta:AdTitle>
  </Period>
</MPD>
```

### B.4 The sub-MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/201/</BaseURL>
  <Period id="cr201" duration="PT30S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                 timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=201</Event>
      <Event presentationTime="7500" id="2">https://t.example.com/q1?cr=201</Event>
      <Event presentationTime="15000" id="3">https://t.example.com/mid?cr=201</Event>
      <Event presentationTime="22500" id="4">https://t.example.com/q3?cr=201</Event>
      <Event presentationTime="30000" id="5">https://t.example.com/complete?cr=201</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" bandwidth="2500000" width="1280" height="720"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### B.5 The Player's walk-through: the break on schedule

1. Between 580 s and 600 s of media time the Player resolves the event, at an
   instant it randomises inside that interval, and receives the List MPD.
2. At PRT = 600 s it executes: the ad replaces the output of the live
   channel, whose media time keeps progressing.
3. The Player fires the beacons at 0, 7.5, 15, 22.5 and 30 s of the ad.
4. At 30 s of ad the presentation ends at PRT + APDmax = 630 s. The main
   presentation resumes at RT = PRT + `@returnOffset` = 630 s, the live
   position.

### B.6 A late start: `@clip` at work

The viewer tunes in at 604 s, while the event is active. The event executes
late, at PRTA = 604 s.

| Quantity | Value | Base definition |
|---|---|---|
| PRT | 600 s | `Event@presentationTime` |
| PRTA | 604 s | the execution time |
| APDmax | 30 s | `@maxDuration` |
| APDadj | max(30 − 604 + 600, 0) = 26 s | `@clip="true"` (Table 57) |
| APDA | min(30 − 0, 26) = 26 s | replacement, `@startWithOffset="false"` so ASO = 0 |
| End of the ad | 604 + 26 = 630 s | *"terminate at the latest at time PRT + APDmax"* |
| RT | PRT + 30 = 630 s | `@returnOffset="30000"` |

The ad starts from its first frame and is cut 26 seconds in; the beacons at
0, 7.5, 15 and 22.5 s fire and the one at 30 s does not (PLY-80). The end of
the break stays where the Publisher scheduled it (PLY-27). With
`@clip="false"` the ad would have run to 634 s.

### B.7 The trick-play variant

On a time-shifted replay the viewer watches at 2x when the event executes.
The ad plays at 2x (PLY-67): its 30 seconds of presentation time occupy
15 seconds of wall clock (PLY-69). The cap and the beacon times are on the
presentation timeline and are unchanged: the midpoint beacon fires at 15 s
of presentation time, 7.5 s of wall clock after the ad starts.

### B.8 Device classes

| Class | Behaviour |
|---|---|
| D1, D2 | Plays the ad on one decoder; may pre-buffer it on the second before 600 s. |
| D3, D4, D5 | Plays the ad on its single decoder, the live channel having stopped being output. |

Every class sees a 30-second full-screen ad, then the live channel at 630 s.

## Annex C — Coexisting overlay, several forms and layouts

### C.1 Scenario

An on-demand film. At five minutes the Publisher allows 30 seconds of
non-linear advertising over the playing film, in four layouts: lower-third,
corner, the upper-left L-shape, and the double box without background. The
ADS returns two 15-second ads. Each carries several options, so that one
decision resolves on every device class: the first ad offers a video, an
HTML and an image lower-third; the second offers a video double box, an image
L-shape and an image corner. The film keeps playing throughout.

### C.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT1H52M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/film9/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="300000" duration="30000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/nl/overlay?title=film9&amp;w=1"
            durationCap="30000"
            earliestResolutionTimeOffset="30000"
            allowedLayouts="overlay-lower-third overlay-corner squeezeback-l-shape-upper-left squeezeback-double-box"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" bandwidth="3000000" width="1280" height="720"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### C.3 The resolution request

The Player resolves from 270 s (300000 − 30000). A D3 Player that declares
nothing sends only the forwarded layouts:

```
GET /nl/overlay?title=film9&w=1&sgai-allowed-layouts=overlay-lower-third%20overlay-corner%20squeezeback-l-shape-upper-left%20squeezeback-double-box HTTP/1.1
Host: aps.example.com
```

### C.4 The resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="PT5S"
                  validFor="PT2M">
  <svta:Ad duration="PT15S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/301/cr301v.mpd"
                          mimeType="application/dash+xml" layout="overlay-lower-third"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/301/banner.html"
                          mimeType="text/html" layout="overlay-lower-third"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/301/banner.png"
                          mimeType="image/png" layout="overlay-lower-third"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=301</Event>
      <Event presentationTime="7500" id="2">https://t.example.com/mid?cr=301</Event>
      <Event presentationTime="15000" id="3">https://t.example.com/complete?cr=301</Event>
    </svta:Tracking>
    <svta:ClickThrough uri="https://brand-b.example.com/tickets"
                       trackingUris="https://t.example.com/click?cr=301"/>
    <svta:AdSystem>ExampleAds</svta:AdSystem>
    <svta:AdTitle>Concert tickets</svta:AdTitle>
  </svta:Ad>
  <svta:Ad duration="PT15S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/302/cr302v.mpd"
                          mimeType="application/dash+xml" layout="squeezeback-double-box"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/302/underlay.jpg"
                          mimeType="image/jpeg" layout="squeezeback-l-shape-upper-left"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/302/corner.png"
                          mimeType="image/png" layout="overlay-corner"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=302</Event>
      <Event presentationTime="15000" id="2">https://t.example.com/complete?cr=302</Event>
    </svta:Tracking>
    <svta:AdSystem>ExampleAds</svta:AdSystem>
    <svta:AdTitle>Streaming bundle</svta:AdTitle>
  </svta:Ad>
</svta:OverlayList>
```

Both candidates use `@id="1"` on their first beacon. They are two beacons,
because the scope is the candidate (PLY-81).

### C.5 The sub-MPDs

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/nl/301/</BaseURL>
  <Period id="cr301v" duration="PT15S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="lt540" bandwidth="1200000" width="960" height="540"/>
    </AdaptationSet>
  </Period>
</MPD>
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/nl/302/</BaseURL>
  <Period id="cr302v" duration="PT15S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="db480" bandwidth="1000000" width="854" height="480"/>
    </AdaptationSet>
  </Period>
</MPD>
```

Neither sub-MPD carries tracking or audio: tracking belongs to the candidate
(§5.4), and a non-linear video over playing content is silent by default in
the IAB guidelines.

### C.6 The walk per device class

| Class | Candidate 1 (lower-third) | Candidate 2 | On screen, 300–315 s | On screen, 315–330 s |
|---|---|---|---|---|
| D1 | video: 2 decoders — renders | video double box — renders | video lower-third | the film shrunk centre-left, the ad video centre-right, black bands |
| D2 | video — renders on the second decoder | video double box — renders | video lower-third | video double box |
| D3 | video fails (one decoder); HTML — renders | video fails; image L-shape — renders | HTML lower-third | the film in the upper-left 60%, the image around it |
| D4 | video fails; HTML fails; image — renders | video fails; image L-shape — renders | image lower-third | image L-shape |
| D5 | all fail | all fail | nothing | nothing |

On D5 both candidates are skipped (PLY-20) and the window presents nothing;
it is not a failed execution, so no other window would be attempted
(PLY-41). The film plays on every class.

### C.7 Timing and cap arithmetic

| Instant (media time) | Event |
|---|---|
| 270 s | earliest resolution; the Player may request from here (PLY-6) |
| before 300 s | document received; usable for 2 minutes (`validFor`) |
| 300 s | window starts; the document is still usable (PLY-9); candidate 1 starts; its beacon `1` fires |
| 305 s | dismissal becomes available (`dismissAfter="PT5S"`) |
| 315 s | candidate 1 ends (15000 ms accrued); candidate 2 starts |
| 330 s | candidate 2 ends; cumulative 30000 ms = the cap, admitted exactly (PLY-28); the span ends |

A viewer who dismisses at 310 s ends the whole slot: candidate 2 is not
presented (PLY-75), beacon `3` of candidate 1 and every beacon of candidate 2
are not fired (PLY-77), and the film is not affected (PLY-76).

### C.8 Where this document came from: an illustrative VAST response

```xml
<VAST version="4.2">
  <Ad id="301" sequence="1">
    <InLine>
      <AdSystem>ExampleAds</AdSystem>
      <AdTitle>Concert tickets</AdTitle>
      <Impression><![CDATA[https://t.example.com/imp?cr=301]]></Impression>
      <Creatives>
        <Creative>
          <NonLinearAds>
            <TrackingEvents>
              <Tracking event="midpoint"><![CDATA[https://t.example.com/mid?cr=301]]></Tracking>
              <Tracking event="complete"><![CDATA[https://t.example.com/complete?cr=301]]></Tracking>
            </TrackingEvents>
            <NonLinear width="1920" height="324" minSuggestedDuration="00:00:15">
              <StaticResource creativeType="application/dash+xml">
                <![CDATA[https://ads-cdn.example.com/nl/301/cr301v.mpd]]>
              </StaticResource>
              <NonLinearClickThrough><![CDATA[https://brand-b.example.com/tickets]]></NonLinearClickThrough>
              <NonLinearClickTracking><![CDATA[https://t.example.com/click?cr=301]]></NonLinearClickTracking>
            </NonLinear>
            <NonLinear width="1920" height="324" minSuggestedDuration="00:00:15">
              <HTMLResource><![CDATA[https://ads-cdn.example.com/nl/301/banner.html]]></HTMLResource>
            </NonLinear>
            <NonLinear width="1920" height="324" minSuggestedDuration="00:00:15">
              <StaticResource creativeType="image/png">
                <![CDATA[https://ads-cdn.example.com/nl/301/banner.png]]>
              </StaticResource>
            </NonLinear>
          </NonLinearAds>
        </Creative>
      </Creatives>
    </InLine>
  </Ad>
  <!-- Ad 302 follows the same pattern with three NonLinear resources. -->
</VAST>
```

| VAST | Resolution document |
|---|---|
| `<Ad>` in `@sequence` order | `<svta:Ad>` in document order |
| `minSuggestedDuration` | `<svta:Ad>@duration` |
| each `<NonLinear>` resource, in the order the ADS gave them | `<svta:RenderableAsset>` in the same order; `@mimeType` from the resource type; `@layout` from the placement the ADS signalled for the creative (here the width and height of a lower-third) |
| `<Impression>`, `<Tracking>` | `<svta:Tracking>`, times relative to the candidate |
| `<NonLinearClickThrough>`, `<NonLinearClickTracking>` | `<svta:ClickThrough>` |

The APS keeps the ADS's order and filters out options outside the forwarded
layouts (APS-9); it does not reorder (APS-5).

## Annex D — Hybrid: a linear break with an overlay composited on top

### D.1 Scenario

An on-demand series. At ten minutes the Publisher inserts a 30-second linear
break and, during it, allows a lower-third overlay on top of the linear ad —
branding for the same campaign or another brand, whatever the ADS returns.
The two portions are selected independently. The overlay window declares
that it is composited **on top** of the linear break; without that
declaration a Player of this specification would play the break and keep the
overlay to the programme around it.

No constraint links the two portions: "no competitor's overlay over this
linear ad" is obtained from the ADS, which owns competitive separation.

### D.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT48M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/series3/ep2/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="1" presentationTime="600000" duration="10000">
        <InsertPresentation uri="https://aps.example.com/linear/mid?s=3&amp;e=2"
                            earliestResolutionTimeOffset="30000"
                            maxDuration="30000"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="600000" duration="30000">
        <svta:OverlayPresentation uri="https://aps.example.com/nl/overlay?s=3&amp;e=2&amp;w=h1"
                                  durationCap="10000"
                                  earliestResolutionTimeOffset="30000"
                                  allowedLayouts="overlay-lower-third"
                                  linearRelation="on-top"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The linear event and the overlay window are of different families and sit in
different `EventStream`s. The window's span, [600 s, 630 s), contains the
event's presentation time, so `on-top` applies to it.

### D.3 The two resolution requests

```
GET /linear/mid?s=3&e=2 HTTP/1.1
Host: aps.example.com

GET /nl/overlay?s=3&e=2&w=h1&sgai-allowed-layouts=overlay-lower-third HTTP/1.1
Host: aps.example.com
```

Both may be issued from 570 s. The linear request carries no forwarded
layouts (DOC-16).

### D.4 The linear resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="list"
     profiles="urn:mpeg:dash:profile:list:2024"
     minBufferTime="PT2S"
     svta:dismissAfter="never">
  <Period id="ad-401" duration="PT30S">
    <ImportedMPD earliestResolutionTimeOffset="30">https://ads-cdn.example.com/cr/401/cr401.mpd</ImportedMPD>
    <svta:AdTitle>Phone launch, 30 s</svta:AdTitle>
  </Period>
</MPD>
```

### D.5 The overlay resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="never">
  <svta:Ad duration="PT10S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/402/cr402v.mpd"
                          mimeType="application/dash+xml" layout="overlay-lower-third"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/402/lt.html"
                          mimeType="text/html" layout="overlay-lower-third"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/402/lt.png"
                          mimeType="image/png" layout="overlay-lower-third"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=402</Event>
      <Event presentationTime="10000" id="2">https://t.example.com/complete?cr=402</Event>
    </svta:Tracking>
  </svta:Ad>
</svta:OverlayList>
```

### D.6 The sub-MPDs

The linear ad:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/401/</BaseURL>
  <Period id="cr401" duration="PT30S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                 timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=401</Event>
      <Event presentationTime="15000" id="2">https://t.example.com/mid?cr=401</Event>
      <Event presentationTime="30000" id="3">https://t.example.com/complete?cr=401</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The overlay video:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/nl/402/</BaseURL>
  <Period id="cr402v" duration="PT10S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="lt540" bandwidth="1200000" width="960" height="540"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### D.7 The budget, and the walk per device class

During the insertion the base outputs one presentation at a time: the linear
ad holds the decoder the programme released (DASH §4.2). An overlay on top needs
exactly what an overlay on the programme needs.

| Class | Linear portion | Overlay portion |
|---|---|---|
| D1 | plays | video lower-third on the second decoder |
| D2 | plays | video lower-third on the second decoder |
| D3 | plays | video fails (one decoder); HTML lower-third renders |
| D4 | plays | video and HTML fail; image lower-third renders |
| D5 | plays | declined: no overlay surface |

### D.8 Timing and cap arithmetic

| Instant | Event |
|---|---|
| 600 s (primary) | The insertion executes; the programme's timeline stops (RT = PRTA). The window's span has started, and `on-top` applies. |
| 0–10 s of the linear ad | The overlay is composited over the linear ad. Its cap accrues on the timeline being output, the linear ad's: 10000 ms at 10 s (§7.6). |
| 10 s of the linear ad | The overlay's candidate ends; the cap is reached. |
| 30 s of the linear ad | The break ends; the programme resumes at 600 s. The window's span still runs to 630 s of programme time, but its cap is spent and its candidates are exhausted, so nothing further appears. |

The same document on a Player of this specification with no `linearRelation`
on the window: the break plays alone, and the window, whose span starts at the
break, presents over the programme after the break for what remains of the
span (PLY-49). A form cannot be on screen when the break begins, since the
span starts there, so none is cut.

## Annex E — Pause-triggered ad

### E.1 Scenario

An on-demand film. For the whole film, a viewer who pauses may see a pause
ad, fullscreen or over the paused frame. The APS returns two candidates for a
pause: a video, HTML or image ad, then an image. If the viewer is still paused
when both have been shown, the Player asks for more; if the APS has nothing
more, the paused frame stays. On resume the ad disappears at once and the film
continues from where it stopped. The Publisher asks the Player to collect the
`PlayList` metric, from which the share of the pause that carried an ad is
derived.

### E.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT1H40M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/film12/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026" timescale="1000">
      <Event id="1" presentationTime="0" duration="6000000">
        <svta:PauseAdPresentation uri="https://aps.example.com/nl/pause?title=film12"
                                  durationCap="60000"
                                  allowedLayouts="pause-fullscreen pause-partial"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
  <Metrics metrics="PlayList">
    <Reporting schemeIdUri="urn:example:reporting:2026" value="collector-1"/>
  </Metrics>
</MPD>
```

`@earliestResolutionTimeOffset` is absent: the Player may resolve from 60
seconds before the window starts, which for a window starting at 0 means from
the start of playback. `@executeOnce` is absent: every qualifying pause may
yield an ad.

### E.3 Resolution request and timing

A D1 Player resolves when playback starts and holds the document:

```
GET /nl/pause?title=film12&sgai-video-decoders=2&sgai-image-over-video=1&sgai-html-over-video=1&sgai-allowed-layouts=pause-fullscreen%20pause-partial HTTP/1.1
Host: aps.example.com
```

The document declares `validFor="PT15M"`. The viewer pauses at 12 min:
the document, received at 0, is still usable and is used without a request.
At a pause at 40 min it has expired; the Player requests a new one and never
presents the expired one (PLY-9). A Player that prefers freshness resolves at
each pause instead (PLY-8).

### E.4 Pause resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="pause"
                  onExhausted="request-again"
                  dismissAfter="PT0S"
                  validFor="PT15M">
  <svta:Ad duration="PT20S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/pz/501/cr501v.mpd"
                          mimeType="application/dash+xml" layout="pause-fullscreen"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/pz/501/panel.html"
                          mimeType="text/html" layout="pause-partial"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/pz/501/panel.png"
                          mimeType="image/png" layout="pause-partial"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=501</Event>
      <Event presentationTime="10000" id="2">https://t.example.com/10s?cr=501</Event>
      <Event presentationTime="20000" id="3">https://t.example.com/20s?cr=501</Event>
    </svta:Tracking>
    <svta:ClickThrough uri="https://brand-c.example.com/qr-offer"/>
  </svta:Ad>
  <svta:Ad duration="PT30S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/pz/502/full.jpg"
                          mimeType="image/jpeg" layout="pause-fullscreen"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=502</Event>
    </svta:Tracking>
  </svta:Ad>
</svta:OverlayList>
```

One pass lasts 20 + 30 = 50 s, under the cap of 60 s. The slot is
dismissible immediately.

### E.5 Sub-MPD of the video creative

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/pz/501/</BaseURL>
  <Period id="cr501v" duration="PT20S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="4000000" width="1920" height="1080"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### E.6 Player walk-through and device classes

| Class | Candidate 1 | Candidate 2 | What the viewer sees while paused |
|---|---|---|---|
| D1 | video fullscreen, second decoder | image fullscreen | a 20 s video, then a fullscreen image |
| D2 | video fullscreen, second decoder over the held frame | image: fails | the video; then candidate 2 is skipped |
| D3 | HTML partial over the paused frame (the conservative choice; it MAY release the decoder for the video, PLY-56) | image fullscreen | the HTML panel, then the image |
| D4 | image partial | image fullscreen | the image panel, then the image |
| D5 | declined | declined | the paused frame (§5.3.7) |

A pause outside every pause window would request nothing (PLY-11); this
window covers the whole film. Any overlay on screen at the pause is suspended
(PLY-52).

### E.7 Exhaustion inside the pause

After one pass (50 s on D1) the viewer is still paused. The document declares
`request-again`, so the Player requests a new document for the same pause.

#### E.7.1 The second request

The APS has nothing to add and returns the empty pause document:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns:svta="urn:svta:dash:sgai:2026"
                  family="pause"
                  onExhausted="stop"
                  dismissAfter="never"/>
```

A document with no candidates under `request-again` is `stop` for the rest of
this pause (PLY-66): the paused frame stays until the viewer resumes. Whether
the second request was a new opportunity or the same one is not this
specification's to fix (§4.5.11). With `onExhausted="repeat"` the Player
would instead have shown the two candidates again, each pass bounded by the
cap.

### E.8 Resume, dismissal and tracking

The viewer resumes 14 s into candidate 1. Within one rendering frame the
video is removed (PLY-57), the beacon at 20 s is never fired (PLY-58), and the
film continues from the paused position (PLY-59). A viewer who dismisses
instead gets the paused frame back without resuming; the beacons scheduled
after the dismissal are not fired either (PLY-77).

### E.9 Measuring delivery

The Player's `PlayList` shows, for this pause: a playback period whose last
trace entry stopped with `stopreason` `UserRequest` at 12:00.0 wall-clock
offset, and the next entry with `starttype` `Resume` at 13:10.0. The paused
interval is 70 s. The pause ad was on screen for 50 s (one pass), then the
paused frame for 20 s: the filled fraction is 50 / 70 ≈ 0.71. A stall that
ends with `stopreason` `Rebuffering` is not a pause and is not counted
(PLY-88).

### E.10 Live variant

On a live channel the same window is declared in a dynamic MPD:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="dynamic"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     availabilityStartTime="2026-09-26T20:00:00Z"
     publishTime="2026-09-26T20:31:00Z"
     minimumUpdatePeriod="PT2S"
     timeShiftBufferDepth="PT1H"
     minBufferTime="PT2S">
  <BaseURL>https://live.example.com/news/</BaseURL>
  <Period id="live" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026" timescale="1000">
      <Event id="1" presentationTime="1800000" duration="1800000">
        <svta:PauseAdPresentation uri="https://aps.example.com/nl/pause?ch=news"
                                  durationCap="60000"
                                  earliestResolutionTimeOffset="0"
                                  allowedLayouts="pause-fullscreen pause-partial"
                                  executeOnce="true"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v720" bandwidth="3000000" width="1280" height="720"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
  <Metrics metrics="PlayList">
    <Reporting schemeIdUri="urn:example:reporting:2026" value="collector-1"/>
  </Metrics>
</MPD>
```

The viewer pauses at 40:00 of media time, inside the window [30:00, 60:00),
and stays paused for 25 minutes. The live edge advances 25 minutes; the
Player's presentation time stays frozen at 40:00, inside the window, and the
pause ad stays admissible for the whole pause (PLY-62). On resume the ad is
removed and playback continues at 40:00; if the Player then jumps to the live
edge, that is a Player action after the resume, outside the window. With
`executeOnce="true"`, a second pause at 50:00 shows nothing, because a pause
ad began rendering during the first (PLY-63, PLY-64); had the first pause
produced no rendered ad, the window would still be available.

## Annex F — Multi-ad break

### F.1 The scenario

An on-demand documentary with a mid-content break capped at 60 seconds. How
many ads fill it is the ADS's decision; it returns four, of 15, 20, 15 and
15 seconds — 65 seconds, more than the cap. The ADS is not required to
respect the cap (ADS-1); the Player enforces it.

### F.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT52M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/doc5/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="1" presentationTime="1200000" duration="10000">
        <InsertPresentation uri="https://aps.example.com/linear/pod?d=5&amp;b=1"
                            earliestResolutionTimeOffset="30000"
                            maxDuration="60000"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### F.3 The List MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="list"
     profiles="urn:mpeg:dash:profile:list:2024"
     minBufferTime="PT2S"
     svta:dismissAfter="never">
  <Period id="ad-601" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="30">https://ads-cdn.example.com/cr/601/cr601.mpd</ImportedMPD>
  </Period>
  <Period id="ad-602" duration="PT20S">
    <ImportedMPD earliestResolutionTimeOffset="15">https://ads-cdn.example.com/cr/602/cr602.mpd</ImportedMPD>
  </Period>
  <Period id="ad-603" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="15">https://ads-cdn.example.com/cr/603/cr603.mpd</ImportedMPD>
  </Period>
  <Period id="ad-604" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="15">https://ads-cdn.example.com/cr/604/cr604.mpd</ImportedMPD>
  </Period>
</MPD>
```

### F.4 The sub-MPDs

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/601/</BaseURL>
  <Period id="cr601" duration="PT15S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1" timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=601</Event>
      <Event presentationTime="15000" id="2">https://t.example.com/complete?cr=601</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/602/</BaseURL>
  <Period id="cr602" duration="PT20S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1" timescale="1000">
      <Event presentationTime="0" id="11">https://t.example.com/imp?cr=602</Event>
      <Event presentationTime="10000" id="12">https://t.example.com/mid?cr=602</Event>
      <Event presentationTime="20000" id="13">https://t.example.com/complete?cr=602</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/603/</BaseURL>
  <Period id="cr603" duration="PT15S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1" timescale="1000">
      <Event presentationTime="0" id="21">https://t.example.com/imp?cr=603</Event>
      <Event presentationTime="15000" id="22">https://t.example.com/complete?cr=603</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/604/</BaseURL>
  <Period id="cr604" duration="PT15S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1" timescale="1000">
      <Event presentationTime="0" id="31">https://t.example.com/imp?cr=604</Event>
      <Event presentationTime="7500" id="32">https://t.example.com/mid?cr=604</Event>
      <Event presentationTime="15000" id="33">https://t.example.com/complete?cr=604</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

All the beacons of the break share one `@id` scope: the base scopes `@id` to
the scheme-and-value pair over the whole presentation, and the four
sub-MPDs' streams are merged into one List MPD (PLY-81). The identifiers are
therefore unique across the break — 1–2, 11–13, 21–22, 31–33. Had every
sub-MPD numbered its beacons from 1, the base would have ignored the later
ones as already processed (DASH §5.10.2.4): an APS that assembles a List MPD
numbers the beacons across it.

### F.5 The arithmetic

Declared durations converted to the cap's timescale: 15000, 20000, 15000,
15000. Running sums: 15000, 35000, 50000, 65000. The cap is 60000.

| Player policy | What plays | Total |
|---|---|---|
| Trim during play only (mandatory) | 601, 602, 603, then 604 for 10 s, cut at the cap | 60 s |
| Drop before play, permitted (PLY-35) | 601, 602, 603; 604 dropped on its declared duration | 50 s |

In both, the order of what plays is the List MPD's (PLY-36). In the first,
the beacons of 604 at 0 and 7.5 s fire, and the one at 15 s does not
(PLY-80).

### F.6 The Player's walk-through

1. From 1170 s the Player resolves the event and receives the List MPD.
2. It validates the four candidates and applies its policy on the fourth.
3. At 1200 s the insertion executes; the programme's timeline stops.
4. It resolves each `ImportedMPD` from 15 s before its PeriodStart and plays
   the candidates back to back.
5. At the cap the alternative presentation terminates; the programme resumes
   at RT = PRTA = 1200 s.

### F.7 Device classes

| Class | Behaviour |
|---|---|
| D1, D2 | Plays the sequence on one decoder, optionally pre-buffering ad N+1 on the second. |
| D3, D4, D5 | Plays the sequence on its single decoder, switching source between ads. |

The viewer sees the same break on every class.

## Annex G — A Player that predates this specification

### G.1 The scenario

A Player that implements the base specification, and not this one, receives
an MPD that uses the constructs of this specification: an overlay window, a
pause window, and extension content in a List MPD. It has no awareness of
their semantics. What it does is skip them and keep playing; what the viewer
then sees depends on what the Publisher authored, and the Publisher's choice
depends on the content.

The content here is on demand, so the Publisher also authors a standard
linear break over the span of the overlay window, using only base
constructs, and declares on the window that it supersedes the break. The
legacy Player plays the break; a Player of this specification presents the
overlay and plays the break only when the overlay presents no ad.

### G.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT50M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/show8/ep1/</BaseURL>
  <Period id="main" start="PT0S">
    <!-- The standard break: base constructs only. -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="1" presentationTime="900000" duration="30000">
        <InsertPresentation uri="https://aps.example.com/linear/mid?show=8&amp;b=1"
                            earliestResolutionTimeOffset="60000"
                            maxDuration="30000"/>
      </Event>
    </EventStream>
    <!-- An overlay window over the same span, superseding the break. -->
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="900000" duration="30000">
        <svta:OverlayPresentation uri="https://aps.example.com/nl/overlay?show=8&amp;w=1"
                                  durationCap="30000"
                                  earliestResolutionTimeOffset="60000"
                                  allowedLayouts="squeezeback-l-shape-upper-left overlay-lower-third"
                                  linearRelation="supersede"/>
      </Event>
    </EventStream>
    <!-- A pause window over the whole episode. -->
    <EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026" timescale="1000">
      <Event id="1" presentationTime="0" duration="3000000">
        <svta:PauseAdPresentation uri="https://aps.example.com/nl/pause?show=8"
                                  durationCap="60000"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
  <Metrics metrics="PlayList">
    <Reporting schemeIdUri="urn:example:reporting:2026" value="collector-1"/>
  </Metrics>
</MPD>
```

### G.3 The same document after removal of the extension namespace

A client that removes every element and attribute outside the DASH namespace,
as DASH §5.2.1 lets it, obtains:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT50M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/show8/ep1/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="1" presentationTime="900000" duration="30000">
        <InsertPresentation uri="https://aps.example.com/linear/mid?show=8&amp;b=1"
                            earliestResolutionTimeOffset="60000"
                            maxDuration="30000"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="900000" duration="30000"/>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026" timescale="1000">
      <Event id="1" presentationTime="0" duration="3000000"/>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
  <Metrics metrics="PlayList">
    <Reporting schemeIdUri="urn:example:reporting:2026" value="collector-1"/>
  </Metrics>
</MPD>
```

It is valid against the base schema and conforms to the base: the two SGAI
streams are ordinary application event streams of schemes the client does not
implement, whose events carry no content, and which it ignores.

### G.4 The List MPD of the standard break

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="list"
     profiles="urn:mpeg:dash:profile:list:2024"
     minBufferTime="PT2S"
     svta:dismissAfter="PT10S">
  <Period id="ad-701" duration="PT30S">
    <ImportedMPD earliestResolutionTimeOffset="60">https://ads-cdn.example.com/cr/701/cr701.mpd</ImportedMPD>
    <svta:ClickThrough uri="https://brand-d.example.com/deal"
                       trackingUris="https://t.example.com/click?cr=701"/>
    <svta:AdSystem>ExampleAds</svta:AdSystem>
  </Period>
</MPD>
```

### G.5 The sub-MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/701/</BaseURL>
  <Period id="cr701" duration="PT30S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                 timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=701</Event>
      <Event presentationTime="30000" id="2">https://t.example.com/complete?cr=701</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### G.6 The walk-through on the older Player

1. It parses the MPD. It meets three event streams and implements one scheme,
   the insertion; it ignores the other two streams (DASH §5.10.1). No error.
2. It plays the episode. A viewer pause is an ordinary pause; nothing is
   requested.
3. From 840 s it resolves the insertion's `@uri` and receives the List MPD.
   It removes `svta:dismissAfter`, `<svta:ClickThrough>` and
   `<svta:AdSystem>` under DASH §5.2.1, and resolves the `ImportedMPD`.
4. At 900 s the insertion executes: a 30-second full-screen ad. Its beacons
   fire. Dismissal follows the base `@skipAfter` default of the event, and
   the ClickThrough is inert.
5. The episode resumes at 900 s.

The Player collects the `PlayList` metric if it implements metrics; that is
base behaviour and harmless.

### G.7 Construct by construct

| Construct | Where the legacy Player meets it | What it does | Test (Annex R) |
|---|---|---|---|
| Overlay window (C1) | `EventStream` of an unknown scheme | ignores the stream; requests nothing | R-BC-1 |
| Pause window (C2) | `EventStream` of an unknown scheme | ignores the stream; its pauses request nothing | R-BC-2 |
| List MPD extension content (C3) | `svta` attribute and elements of the List MPD | removes them; plays the ad | R-BC-3 |
| `<svta:OverlayList>` (C4) | never | — | R-BC-4 |
| Request parameters (C5) | not in this MPD | — | R-BC-5 |

### G.8 The authoring choice: live and on-demand

- **Live content.** A live Publisher would declare the overlay window with
  no standard break: holding a live stream to splice in a break loses real
  content, so the opportunity is an expected loss on legacy Players. The
  viewer of a legacy Player sees the programme uninterrupted.
- **On-demand content, as here.** The standard break costs no content, so the
  Publisher authors it unconditionally — it cannot tell a legacy Player from
  the manifest — and declares `supersede` on the window, which is what keeps
  a Player of this specification from presenting both.

What varies is the content type, not the device: a top-tier device running a
legacy Player behaves exactly as a worst-case one.

### G.9 The same document on a Player of this specification

It resolves the overlay window from 840 s and, per its device (Annex Q),
either renders the overlay over the episode and does not execute the break,
or finds nothing renderable and executes the break. It never presents both
(§7.13). Its pauses resolve the pause window. It reads the List MPD's
ClickThrough and dismissal declaration when the break plays.

### G.10 Device classes

| Class | Legacy Player |
|---|---|
| D1 to D5 | Plays the episode, the standard break at 900 s, and nothing non-linear. No error surfaces. |

## Annex H — An overlay window crossing a pause window

### H.1 Scenario

An on-demand film. An overlay window runs from 5:00 to 5:30. A pause window
covers the whole film. At 5:10 the viewer pauses, with the overlay on screen,
and stays paused 40 seconds. The pause ad takes priority: the overlay is
suspended and the pause ad shown, fullscreen or over the paused frame. On
resume the pause ad goes and the overlay comes back, with the time it had
left.

### H.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT1H35M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/film20/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="300000" duration="30000">
        <svta:OverlayPresentation uri="https://aps.example.com/nl/overlay?t=film20&amp;w=1"
                                  durationCap="30000"
                                  allowedLayouts="overlay-lower-third"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026" timescale="1000">
      <Event id="1" presentationTime="0" duration="5700000">
        <svta:PauseAdPresentation uri="https://aps.example.com/nl/pause?t=film20"
                                  durationCap="60000"
                                  earliestResolutionTimeOffset="0"
                                  allowedLayouts="pause-fullscreen pause-partial"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
  <Metrics metrics="PlayList">
    <Reporting schemeIdUri="urn:example:reporting:2026" value="collector-1"/>
  </Metrics>
</MPD>
```

The two windows are of different families: they are not a fallback chain,
and each has its own stream.

### H.3 Resolution requests

The overlay window is resolved before 5:00 (from 4:00, the default offset).
The pause window declares an offset of zero from its start at 0, so the
Player may resolve it from the start of playback; this Player resolves at the
pause instead, at 5:10:

```
GET /nl/overlay?t=film20&w=1&sgai-allowed-layouts=overlay-lower-third HTTP/1.1
Host: aps.example.com

GET /nl/pause?t=film20&sgai-allowed-layouts=pause-fullscreen%20pause-partial HTTP/1.1
Host: aps.example.com
```

### H.4 Overlay resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="PT3S">
  <svta:Ad duration="PT30S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/801/cr801v.mpd"
                          mimeType="application/dash+xml" layout="overlay-lower-third"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/801/lt.html"
                          mimeType="text/html" layout="overlay-lower-third"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/801/lt.png"
                          mimeType="image/png" layout="overlay-lower-third"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=801</Event>
      <Event presentationTime="15000" id="2">https://t.example.com/mid?cr=801</Event>
      <Event presentationTime="30000" id="3">https://t.example.com/complete?cr=801</Event>
    </svta:Tracking>
  </svta:Ad>
</svta:OverlayList>
```

### H.5 Pause resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="pause"
                  onExhausted="stop"
                  dismissAfter="PT0S">
  <svta:Ad duration="PT30S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/pz/802/cr802v.mpd"
                          mimeType="application/dash+xml" layout="pause-fullscreen"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/pz/802/panel.html"
                          mimeType="text/html" layout="pause-partial"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/pz/802/panel.png"
                          mimeType="image/png" layout="pause-partial"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=802</Event>
      <Event presentationTime="30000" id="2">https://t.example.com/complete?cr=802</Event>
    </svta:Tracking>
  </svta:Ad>
</svta:OverlayList>
```

### H.6 Sub-MPDs of the video creatives

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/nl/801/</BaseURL>
  <Period id="cr801v" duration="PT30S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="lt540" bandwidth="1200000" width="960" height="540"/>
    </AdaptationSet>
  </Period>
</MPD>
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/pz/802/</BaseURL>
  <Period id="cr802v" duration="PT30S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="4000000" width="1920" height="1080"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### H.7 Player walk-through (Branch A: window still open on resume)

| Media time | Wall clock | Event |
|---|---|---|
| 5:00 | 0 s | Overlay candidate starts; beacon `1` of 801 fires. |
| 5:10 | 10 s | The viewer pauses inside the pause window. The Player suspends the overlay, with 10000 ms of its cap accrued (PLY-52), and requests the pause document. |
| 5:10 (frozen) | 10–40 s | The pause ad plays; beacon `1` of 802 at 10 s, `2` at 40 s. The overlay's cap does not accrue: the presentation timeline is not advancing (PLY-31). |
| 5:10 (frozen) | 40–50 s | The pause candidate is exhausted; `onExhausted="stop"` leaves the paused frame (PLY-65). |
| 5:10 | 50 s | The viewer resumes. The pause ad was already gone; the overlay window, [5:00, 5:30), is still active, so the overlay is restored where it was suspended (PLY-53). |
| 5:25 | 65 s | Beacon `2` of 801 (15 s into the candidate). |
| 5:30 | 70 s | The candidate completes, the cap (30000) is reached exactly, and the span ends; beacon `3` fires. |

### H.8 Branch B: the window closed before the resume

The same scenario on a live channel with a 30-second time-shift buffer, the
viewer paused for 10 minutes. The Player's presentation time stays frozen at
5:10 during the pause (PLY-62), but by the time the viewer resumes, 5:10 has
left the buffer; the Player resumes at the oldest available media, as the
base does (§8.8), which is past 5:30. The overlay window is no longer active
there, so the overlay surface stays clear (PLY-54): the overlay is over, and
its remaining beacons are not fired.

### H.9 Device classes

| Class | Overlay before the pause | During the pause | After the resume |
|---|---|---|---|
| D1 | video lower-third | video pause ad, fullscreen | video lower-third restored |
| D2 | video lower-third (second decoder) | video pause ad on the second decoder over the held frame | video lower-third restored |
| D3 | HTML lower-third | HTML partial pause ad | HTML lower-third restored |
| D4 | image lower-third | image partial pause ad | image lower-third restored |
| D5 | none | none | none |

On every class, at most one ad surface is visible at any instant (PLY-45,
PLY-61).

## Annex I — One ad, ordered options, resolved across the device classes

### I.1 The scenario

One non-linear ad for an overlay slot. The ADS returns it with four options,
in order: a double box with a video ad and the advertiser's background image;
an L-shape with an image creative; an image lower-third; and a full-screen
video takeover. The ADS and the APS know nothing about the viewer's device,
and the Publisher declares one device-agnostic set of allowed layouts. The
Player discloses nothing. Each device walks the same list and renders the
first option it can satisfy; five classes land on three layouts, and nobody
upstream authored a per-device variant.

### I.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT58M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/show11/ep4/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="1500000" duration="20000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/nl/overlay?s=11&amp;e=4&amp;w=1"
            durationCap="20000"
            allowedLayouts="squeezeback-double-box-background squeezeback-l-shape-upper-left overlay-lower-third linear"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

`linear` is listed explicitly: an overlay window that declared nothing would
not admit the takeover (§3.4.3).

### I.3 The resolution document

The request carries only the forwarded layouts:

```
GET /nl/overlay?s=11&e=4&w=1&sgai-allowed-layouts=squeezeback-double-box-background%20squeezeback-l-shape-upper-left%20overlay-lower-third%20linear HTTP/1.1
Host: aps.example.com
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="never">
  <svta:Ad duration="PT20S">
    <!-- 1: double box, video ad, advertiser background image -->
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/db-video.mpd"
                          mimeType="application/dash+xml"
                          layout="squeezeback-double-box-background"
                          background="https://ads-cdn.example.com/nl/901/db-bg.jpg"/>
    <!-- 2: L-shape, full-frame image creative -->
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/l-underlay.jpg"
                          mimeType="image/jpeg"
                          layout="squeezeback-l-shape-upper-left"/>
    <!-- 3: image lower-third -->
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/lt.png"
                          mimeType="image/png" layout="overlay-lower-third"/>
    <!-- 4: full-screen takeover, video -->
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/takeover.mpd"
                          mimeType="application/dash+xml" layout="linear"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=901</Event>
      <Event presentationTime="10000" id="2">https://t.example.com/mid?cr=901</Event>
      <Event presentationTime="20000" id="3">https://t.example.com/complete?cr=901</Event>
    </svta:Tracking>
    <svta:ClickThrough uri="https://brand-e.example.com/new"
                       trackingUris="https://t.example.com/click?cr=901"/>
  </svta:Ad>
</svta:OverlayList>
```

The tracking is the candidate's: whichever option renders, the same beacons
fire, from the instant the candidate starts.

### I.4 The sub-MPDs

The double-box ad video:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/nl/901/db/</BaseURL>
  <Period id="db-video" duration="PT20S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="db540" bandwidth="1500000" width="960" height="540"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The full-screen takeover:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/nl/901/to/</BaseURL>
  <Period id="takeover" duration="PT20S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The takeover carries audio: it replaces the programme on screen, as a linear
ad does.

### I.5 Element type and element count

| Option | Elements on screen | Needs |
|---|---|---|
| 1 double box, video ad + background | shrunk programme (video), ad (video), background (image) | 2 decoders + image surface |
| 2 L-shape, image creative | full-frame image, shrunk programme (video) | 1 decoder + image surface |
| 3 image lower-third | programme (video), image | 1 decoder + image surface |
| 4 takeover | the ad alone, programme suspended | 1 decoder, reused |

### I.6 The walk per device class

| Class | 1 | 2 | 3 | 4 | Renders | The viewer sees |
|---|---|---|---|---|---|---|
| D1 | passes | — | — | — | 1 | The programme in one box, the ad video in the other, the advertiser's image in the bands. |
| D2 | fails on the background image, a non-video surface | fails: image creative | fails: image | passes | 4 | A 20 s full-screen video ad; the programme resumes where it was suspended. |
| D3 | fails: needs 2 decoders | passes | — | — | 2 | The programme in the upper-left 60%, the image creative around it. |
| D4 | fails: needs 2 decoders | passes | — | — | 2 | As D3. Had the creative been HTML, D4 would have skipped it and landed on option 3. |
| D5 | fails | fails | fails | passes | 4 | As D2, for another reason: D5 composites nothing over video. |

The takeover on this on-demand programme suspends the programme and resumes it
from the suspended position (§5.3.6).

### I.7 What the scenario shows

The per-device outcome was authored once, as one ordered list emitted to every
viewer, under one device-agnostic allowed-layout set; no actor upstream of the
Player held a device-class matrix. D2 is the instructive case: it owns the two
decoders the double-box video needs and still declines it, because the third
element, the background, is an image it cannot composite. The rule is element
**type** as well as element **count**. D2 and D5 reach the same last option by
different paths. Annex M shows the same ad resolved by an APS that received
the Player's capabilities.

## Annex J — Double box, the three-element layout

### J.1 Scenario

An on-demand cooking show. For 15 seconds at 12:00 the Publisher allows the
double box, with or without an advertiser background:
`squeezeback-double-box` and `squeezeback-double-box-background`. The
programme shrinks into the centre-left box and the ad sits in the
centre-right box. The two boxes leave bands uncovered: with a background the
advertiser's image fills them, without one they are black. The background is
part of the layout's composition, not an alternative the Player chooses; it
is always a still image, and that is what decides which devices can render
the layout.

The ADS offers one ad in four renditions: a video ad with background, an
image ad with background, an HTML ad with background, and an image ad
without background.

### J.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT30M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/cook/ep9/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="720000" duration="15000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/nl/overlay?show=cook&amp;ep=9"
            durationCap="15000"
            allowedLayouts="squeezeback-double-box squeezeback-double-box-background"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### J.3 The resolution request

```
GET /nl/overlay?show=cook&ep=9&sgai-allowed-layouts=squeezeback-double-box%20squeezeback-double-box-background HTTP/1.1
Host: aps.example.com
```

### J.4 The resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="PT5S">
  <svta:Ad duration="PT15S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/1001/ad-video.mpd"
                          mimeType="application/dash+xml"
                          layout="squeezeback-double-box-background"
                          background="https://ads-cdn.example.com/nl/1001/bg.jpg"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/1001/ad.png"
                          mimeType="image/png"
                          layout="squeezeback-double-box-background"
                          background="https://ads-cdn.example.com/nl/1001/bg.jpg"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/1001/ad.html"
                          mimeType="text/html"
                          layout="squeezeback-double-box-background"
                          background="https://ads-cdn.example.com/nl/1001/bg.jpg"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/1001/ad.png"
                          mimeType="image/png"
                          layout="squeezeback-double-box"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=1001</Event>
      <Event presentationTime="15000" id="2">https://t.example.com/complete?cr=1001</Event>
    </svta:Tracking>
  </svta:Ad>
</svta:OverlayList>
```

The background is an attribute of each option whose layout has one; the last
option's layout has none, so it carries none and its bands render black.

### J.5 The sub-MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/nl/1001/v/</BaseURL>
  <Period id="ad-video" duration="PT15S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="db540" bandwidth="1500000" width="960" height="540"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### J.6 The budget, per layout and form

| Option | Decoders | Surfaces over video |
|---|---|---|
| 1 video ad + background | 2 (programme, ad) | image (background) |
| 2 image ad + background | 1 (programme) | image (ad), image (background) |
| 3 HTML ad + background | 1 | HTML (ad), image (background) |
| 4 image ad, no background | 1 | image (ad) |

### J.7 The walk per device class

| Class | 1 | 2 | 3 | 4 | Renders |
|---|---|---|---|---|---|
| D1 | passes | — | — | — | 1: video ad, background image in the bands |
| D2 | fails: the background is an image | fails: image | fails: HTML | fails: image | nothing — the window presents no ad |
| D3 | fails: 2 decoders | passes | — | — | 2: image ad, background |
| D4 | fails: 2 decoders | passes | — | — | 2: image ad, background |
| D5 | fails | fails | fails | fails | nothing |

On D2 the blocker is the element type, not the count: the two decoders are
there for option 1, and the background is not a video. Had the ADS offered a
video ad **without** background (`squeezeback-double-box`), D2 would have
rendered it, with black bands.

### J.8 Timing and cap arithmetic

The candidate starts at 12:00 and ends at 12:15; 15000 ms equals the cap and
the span. The programme returns to full screen when the candidate ends. A
dismissal after 12:05 ends the slot and returns the programme to full screen
at once, without skipping any of it (PLY-76).

## Annex K — ClickThrough

### K.1 Scenario

An on-demand show carries a linear mid-roll and, later, an overlay. Both ads
have a ClickThrough with click-tracking. On a CTV the viewer presses select
on the remote while the ad is on screen; on a phone they tap it. At that
moment the Player opens the destination (or hands it to the device) and fires
every click-tracking URL once. The click has no presentation time and never
fires from the timeline.

### K.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/show15/ep3/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="1" presentationTime="600000" duration="10000">
        <InsertPresentation uri="https://aps.example.com/linear/mid?s=15&amp;e=3"
                            maxDuration="20000"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="1500000" duration="15000">
        <svta:OverlayPresentation uri="https://aps.example.com/nl/overlay?s=15&amp;e=3"
                                  durationCap="15000"
                                  allowedLayouts="overlay-corner"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The Publisher configures nothing about clicks: the ClickThrough travels with
the ad, not with the slot.

### K.3 Linear: the List MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="list"
     profiles="urn:mpeg:dash:profile:list:2024"
     minBufferTime="PT2S"
     svta:dismissAfter="never">
  <Period id="ad-1101" duration="PT20S">
    <ImportedMPD earliestResolutionTimeOffset="60">https://ads-cdn.example.com/cr/1101/cr1101.mpd</ImportedMPD>
    <svta:ClickThrough uri="https://brand-f.example.com/trial"
                       trackingUris="https://t.example.com/click?cr=1101 https://verify.example.net/c?id=1101"/>
  </Period>
</MPD>
```

The sub-MPD of the linear ad:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/1101/</BaseURL>
  <Period id="cr1101" duration="PT20S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                 timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=1101</Event>
      <Event presentationTime="20000" id="2">https://t.example.com/complete?cr=1101</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### K.4 Non-linear: the overlay document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="PT0S">
  <svta:Ad duration="PT15S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/1102/corner.png"
                          mimeType="image/png" layout="overlay-corner"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=1102</Event>
    </svta:Tracking>
    <svta:ClickThrough uri="https://brand-g.example.com/menu"/>
  </svta:Ad>
</svta:OverlayList>
```

This ClickThrough has no click-tracking, which is the advertiser's choice.

### K.5 Player walk-through

1. **Linear, at 10:08.** The viewer presses select 8 seconds into the linear
   ad. The Player reads `<svta:ClickThrough>` from the candidate's Period,
   hands `https://brand-f.example.com/trial` to the device, and issues one
   GET to each of the two tracking URLs, ignoring the responses. The
   impression and complete beacons are unaffected: they are on the timeline.
2. **Overlay, at 25:04.** The viewer presses select on the corner overlay.
   The Player opens `https://brand-g.example.com/menu`; there is nothing to
   fire. What the device does with the programme when it opens a destination
   (pause it, keep it running) is the application's.

### K.6 A Player that does not implement this specification

It plays the linear ad and removes the `svta` elements of the List MPD; a
select does nothing ad-related. It never sees the overlay. The click is
inert, and nothing else changes.

### K.7 Device classes

The outcome depends on the input mechanism, not on decoders or surfaces:
D1 to D5 read the carrier and fire the click identically. The overlay itself
renders on D1, D3 and D4 (image over video) and not on D2 and D5; where it
does not render there is nothing to click.

## Annex L — Overlapping windows of one family, with fallback

### L.1 Scenario

An on-demand film. At 20:00 the Publisher declares two overlapping overlay
windows: a primary one served by one APS and a backup served by another. It
is not two opportunities: it is one opportunity with a declared fallback. The
Player tries the first; only if that attempt produces no ad does it try the
second. Each window carries its own layouts and cap, and binds what it serves
with them.

### L.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT1H48M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/film31/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="1200000" duration="30000">
        <svta:OverlayPresentation uri="https://aps-a.example.com/nl/overlay?f=31"
                                  durationCap="30000"
                                  allowedLayouts="overlay-lower-third"/>
      </Event>
      <Event id="2" presentationTime="1200000" duration="30000">
        <svta:OverlayPresentation uri="https://aps-b.example.net/sgai/ov?f=31"
                                  durationCap="20000"
                                  allowedLayouts="overlay-corner squeezeback-l-shape-upper-left"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

Both windows sit in the one `EventStream` of their family in the Period
(PUB-7).

### L.3 Order of the chain

Both windows start at 1200000. Presentation time does not separate them, so
the Player takes them in the order they appear in the `EventStream`: event 1,
then event 2 (PLY-40). Had event 2 started at 1195000, it would have been
first, whatever its position.

### L.4 The three paths

**Path 1 — the first window answers "nothing sold", the second answers with
an ad.** APS A returns:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="never"/>
```

A well-formed document with no candidates is a failed execution (PLY-39), so
the Player attempts window 2, and APS B's document (§L.5) is presented. At
the Player this path is indistinguishable from one where APS A could not be
reached at all.

**Path 2 — both answer with the empty document.** Both attempts failed; the
chain is exhausted, and the film continues uninterrupted: *"If no event can be
successfully executed, the playback continues uninterrupted"*.

**Path 3 — neither can be reached** (APS A times out, APS B answers `503`).
Both are failed executions; no document was obtained; the film continues.

### L.5 The fallback window's document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="PT5S">
  <svta:Ad duration="PT20S">
    <svta:RenderableAsset src="https://cdn-b.example.net/cr/1201/corner.mpd"
                          mimeType="application/dash+xml" layout="overlay-corner"/>
    <svta:RenderableAsset src="https://cdn-b.example.net/cr/1201/l.jpg"
                          mimeType="image/jpeg" layout="squeezeback-l-shape-upper-left"/>
    <svta:RenderableAsset src="https://cdn-b.example.net/cr/1201/lt.png"
                          mimeType="image/png" layout="overlay-lower-third"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.net/imp?cr=1201</Event>
      <Event presentationTime="20000" id="2">https://t.example.net/complete?cr=1201</Event>
    </svta:Tracking>
  </svta:Ad>
</svta:OverlayList>
```

Its sub-MPD:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://cdn-b.example.net/cr/1201/v/</BaseURL>
  <Period id="corner" duration="PT20S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="c360" bandwidth="600000" width="640" height="360"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The third option, a lower-third, is outside window 2's layouts. It is an APS
error (APS-9), and the Player would never render it on this window — even
though window 1, which this window stands in for, admits exactly that layout
(PLY-43).

### L.6 Which options pass, per window and device class

Window 2 binds its candidate with its own layouts
(`overlay-corner squeezeback-l-shape-upper-left`) and its own cap (20000).

| Class | Option 1 video corner | Option 2 image L-shape | Option 3 image lower-third | Renders |
|---|---|---|---|---|
| D1 | passes | — | — | video corner |
| D2 | passes (second decoder) | — | — | video corner |
| D3 | fails: one decoder | passes | — | L-shape |
| D4 | fails: one decoder | passes | — | L-shape |
| D5 | fails | fails | not admitted | nothing |

Option 3 fails the layout check on every class; on D5 it would fail the device
check too.

### L.7 Candidates that are not renderable end at the primary content

A variant: APS A returns a document carrying one candidate whose only option is
an HTML lower-third, and the device is D4. The document carries candidates, so
it is **not** a failed execution. D4 cannot render HTML, skips the candidate,
has no other, and continues with the film (PLY-20, PLY-41). It does not attempt
window 2. The base's failure condition is about media availability after the
merge, not about what a given device can render, and this specification does not
extend it there.

### L.8 Device classes

Choosing the window is device-agnostic: D1 to D5 walk the chain identically.
The device class affects only what renders inside the chosen window's document
(§L.6).

## Annex M — One ad, Player-declared capabilities, resolved by the APS

### M.1 The scenario

The ad of Annex I, with the same four options at the ADS and the same
device-agnostic allowed layouts. What changes is where the capability check is
resolved. Each Player attaches the capability parameters it chooses to the
resolution request; an APS that uses them removes the options they rule out
and emits the first survivor alone. The Player checks what it receives before
rendering, as always. Every device class ends on the option it ends on in
Annex I.

### M.2 The main MPD

Identical to Annex I.2:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT58M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/show11/ep4/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="1500000" duration="20000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/nl/overlay?s=11&amp;e=4&amp;w=1"
            durationCap="20000"
            allowedLayouts="squeezeback-double-box-background squeezeback-l-shape-upper-left overlay-lower-third linear"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### M.3 The five requests

Every request carries the forwarded layouts, which are not optional
(PLY-15); `L` below stands for
`sgai-allowed-layouts=squeezeback-double-box-background%20squeezeback-l-shape-upper-left%20overlay-lower-third%20linear`.

| Class | Query added to `/nl/overlay?s=11&e=4&w=1` |
|---|---|
| D1 | `&sgai-video-decoders=2&sgai-image-over-video=1&sgai-html-over-video=1&L` |
| D2 | `&sgai-video-decoders=2&sgai-image-over-video=0&sgai-html-over-video=0&L` |
| D3 | `&sgai-video-decoders=1&sgai-image-over-video=1&L` — the HTML axis is omitted: the Player cannot determine it when it issues the request, and sends nothing rather than an empty value (PLY-13). |
| D4 | `&L` — it declares nothing (PLY-12). |
| D5 | `&sgai-video-decoders=1&sgai-image-over-video=0&sgai-html-over-video=0&L` |

### M.4 What the APS derives

This APS rules out an option when a declared value makes it unsatisfiable, and
— its own conservative policy — also when the option depends on an
undetermined axis. Another APS could assume the most capable case for an
undetermined axis and be equally conformant (DOC-14).

| Class | 1 double box + bg (2 dec, image) | 2 L-shape image (1 dec, image) | 3 lower-third image | 4 takeover (1 dec) | Emits |
|---|---|---|---|---|---|
| D1 | survives | — | — | — | option 1 |
| D2 | out: image = 0 | out: image = 0 | out: image = 0 | survives | option 4 |
| D3 | out: decoders = 1 | survives (does not depend on HTML) | — | — | option 2 |
| D4 | nothing declared: cannot narrow | | | | all four, in the ADS's order |
| D5 | out | out | out | survives | option 4 |

The options the APS emits keep the ADS's order (APS-5).

### M.5 The resolution documents

**For D1:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="never">
  <svta:Ad duration="PT20S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/db-video.mpd"
                          mimeType="application/dash+xml"
                          layout="squeezeback-double-box-background"
                          background="https://ads-cdn.example.com/nl/901/db-bg.jpg"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=901</Event>
      <Event presentationTime="10000" id="2">https://t.example.com/mid?cr=901</Event>
      <Event presentationTime="20000" id="3">https://t.example.com/complete?cr=901</Event>
    </svta:Tracking>
    <svta:ClickThrough uri="https://brand-e.example.com/new"
                       trackingUris="https://t.example.com/click?cr=901"/>
  </svta:Ad>
</svta:OverlayList>
```

**For D2 and D5:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="never">
  <svta:Ad duration="PT20S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/takeover.mpd"
                          mimeType="application/dash+xml" layout="linear"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=901</Event>
      <Event presentationTime="10000" id="2">https://t.example.com/mid?cr=901</Event>
      <Event presentationTime="20000" id="3">https://t.example.com/complete?cr=901</Event>
    </svta:Tracking>
    <svta:ClickThrough uri="https://brand-e.example.com/new"
                       trackingUris="https://t.example.com/click?cr=901"/>
  </svta:Ad>
</svta:OverlayList>
```

**For D3:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="never">
  <svta:Ad duration="PT20S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/l-underlay.jpg"
                          mimeType="image/jpeg"
                          layout="squeezeback-l-shape-upper-left"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=901</Event>
      <Event presentationTime="10000" id="2">https://t.example.com/mid?cr=901</Event>
      <Event presentationTime="20000" id="3">https://t.example.com/complete?cr=901</Event>
    </svta:Tracking>
    <svta:ClickThrough uri="https://brand-e.example.com/new"
                       trackingUris="https://t.example.com/click?cr=901"/>
  </svta:Ad>
</svta:OverlayList>
```

**For D4:** the four-option document of Annex I.3, unchanged:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="never">
  <svta:Ad duration="PT20S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/db-video.mpd"
                          mimeType="application/dash+xml"
                          layout="squeezeback-double-box-background"
                          background="https://ads-cdn.example.com/nl/901/db-bg.jpg"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/l-underlay.jpg"
                          mimeType="image/jpeg"
                          layout="squeezeback-l-shape-upper-left"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/lt.png"
                          mimeType="image/png" layout="overlay-lower-third"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/takeover.mpd"
                          mimeType="application/dash+xml" layout="linear"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=901</Event>
      <Event presentationTime="10000" id="2">https://t.example.com/mid?cr=901</Event>
      <Event presentationTime="20000" id="3">https://t.example.com/complete?cr=901</Event>
    </svta:Tracking>
    <svta:ClickThrough uri="https://brand-e.example.com/new"
                       trackingUris="https://t.example.com/click?cr=901"/>
  </svta:Ad>
</svta:OverlayList>
```

### M.6 The sub-MPDs

The double-box ad video (emitted to D1 and D4):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/nl/901/db/</BaseURL>
  <Period id="db-video" duration="PT20S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="db540" bandwidth="1500000" width="960" height="540"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The takeover (emitted to D2, D4 and D5):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/nl/901/to/</BaseURL>
  <Period id="takeover" duration="PT20S">
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### M.7 The Player's check per device class

| Class | Received | Player check (PLY-18, PLY-19) | Renders | Same as Annex I |
|---|---|---|---|---|
| D1 | option 1 | device and layout pass | double box | yes |
| D2 | option 4 | pass | takeover | yes |
| D3 | option 2 | pass | L-shape | yes |
| D4 | all four | walks: 1 fails (2 decoders), 2 passes | L-shape | yes |
| D5 | option 4 | pass | takeover | yes |

Had a D3 device's HTML surface been taken by another application between the
request and the render, nothing would change for option 2; had the APS derived
a wrong option — say, the double box for D3 — the Player's own check would
have failed it, and with no other option the candidate would have been skipped
(PLY-20). Declaring narrows what arrives; it does not make what arrives
authoritative.

### M.8 What the scenario shows

The viewer-visible outcome is identical to Annex I on every class. What moved
is where the check was resolved: in Annex I the APS emits every option and each
Player selects; here each Player declares and the APS selects. The D4 row is not
a special case: a Player that declares nothing leaves the APS unable to narrow,
and the document of Annex I is what this same APS returns to it. A single option
does not require a declaration either: an APS that wants the choice to sit with
it may emit one option on any basis, and the Player renders it or skips the
candidate.

## Annex N — A non-linear ad over a replacement that is not advertising

### N.1 Scenario

A live sports channel loses the rights to a match in one region. The
Publisher replaces that span of the live timeline with a blackout slate —
its own programme, with its own audio — and wants an overlay ad shown during
the slate. The slate is a presentation of its own, with its own MPD, and the
overlay window is declared **there**, over the slate's timeline. The primary
timeline carries no window over the blacked-out span: the primary content
cannot know what the replacement contains.

The base specification does not treat its replacement tool as an ad
mechanism: it serves *"applications such as pre-roll and mid-roll
advertisement, as well as blackouts"* (DASH §5.16.1), and the Advanced Linear
profile names *"server guided advertisement insertion and blackouts"*
(DASH §8.13.1). **This specification does not specify blackouts**; the blackout is
here because it shows that the presentation under a non-linear ad need not be
an ad.

### N.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="dynamic"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     availabilityStartTime="2026-09-26T19:00:00Z"
     publishTime="2026-09-26T19:44:00Z"
     minimumUpdatePeriod="PT2S"
     timeShiftBufferDepth="PT30M"
     minBufferTime="PT2S">
  <BaseURL>https://live.example.com/sports2/</BaseURL>
  <Period id="live" start="PT0S">
    <!-- The blackout: a replacement whose end is not known in advance. -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
                 timescale="1000">
      <Event id="31" presentationTime="2700000" duration="10000">
        <ReplacePresentation uri="https://slate.example.com/sports2/blackout-31.mpd"
                             earliestResolutionTimeOffset="30000"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

No `@maxDuration`: absent, it is infinity, and *"the current presentation
resumes only when the alternative presentation terminates"* (Table 63). No
`@clip` either, which the base forbids without `@maxDuration`. A Player of
this specification executes the event exactly so; requiring a cap here would
make it refuse the blackout and show the programme the Publisher blacked out
(PLY-29 does not apply to inherited events).

### N.3 The two resolutions

1. **The replacement** resolves to the Publisher's slate MPD (§N.4). No ADS,
   no APS and no ad candidate take part.
2. **The slate's overlay window** resolves through the APS:

```
GET /nl/overlay?ch=sports2&ctx=blackout&sgai-allowed-layouts=overlay-lower-third%20overlay-corner HTTP/1.1
Host: aps.example.com
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="PT0S">
  <svta:Ad duration="PT20S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/1401/lt.html"
                          mimeType="text/html" layout="overlay-lower-third"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/1401/lt.png"
                          mimeType="image/png" layout="overlay-lower-third"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=1401</Event>
      <Event presentationTime="20000" id="2">https://t.example.com/complete?cr=1401</Event>
    </svta:Tracking>
    <svta:ClickThrough uri="https://brand-h.example.com/app"/>
  </svta:Ad>
</svta:OverlayList>
```

The ad has image and HTML options only, so no ad sub-MPD is involved.

### N.4 The slate's MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="dynamic"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     availabilityStartTime="2026-09-26T19:44:00Z"
     publishTime="2026-09-26T19:44:30Z"
     minimumUpdatePeriod="PT5S"
     timeShiftBufferDepth="PT5M"
     minBufferTime="PT2S">
  <BaseURL>https://slate.example.com/sports2/blackout-31/</BaseURL>
  <Period id="slate" start="PT0S">
    <!-- The overlay window belongs to the slate's own timeline. -->
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="60000" duration="20000">
        <svta:OverlayPresentation uri="https://aps.example.com/nl/overlay?ch=sports2&amp;ctx=blackout"
                                  durationCap="20000"
                                  allowedLayouts="overlay-lower-third overlay-corner"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="s720" bandwidth="1500000" width="1280" height="720"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="s-a96" bandwidth="96000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The slate is live, so it *"always starts at the live edge"* (DASH §5.16.2.2.6),
and it ends when the Publisher ends it. Its overlay window opens one minute
into the slate. The slate is reached through `@uri`, not through
`ImportedMPD`, so it is not bound to the Single-Period Static profile.

### N.5 What each portion carries

| | Slate | Overlay |
|---|---|---|
| Is an ad | no | yes |
| Declared by | the main MPD's replacement event | the slate MPD's overlay window |
| Resolved through | the Publisher's slate server | the APS |
| Cap | none (infinity) | `durationCap="20000"` |
| Tracking | none | `<svta:Tracking>` |
| ClickThrough | none | `<svta:ClickThrough>` |

What the two share is the screen, not the contract.

### N.6 The budget, and the walk per device class

During the replacement one access engine outputs media (DASH §4.2): the slate holds
the decoder the live channel released, exactly as a linear ad would. The
overlay needs what an overlay over any video needs. The Player processes the
slate's window as the slate's own (PLY-51).

| Class | Overlay over the slate |
|---|---|
| D1 | HTML lower-third composited over the slate |
| D2 | declined: both options are non-video surfaces |
| D3 | HTML lower-third |
| D4 | HTML fails; image lower-third |
| D5 | declined |
| Legacy | plays the slate, ignores the window: the blackout holds and no ad is shown |

### N.7 Timing, and a window on the primary timeline

| Instant | Event |
|---|---|
| 45:00 primary | The replacement executes; the slate starts at its live edge; the channel's media time keeps progressing underneath, not output. |
| slate 1:00 | The slate's overlay window opens; its 20-second candidate starts. |
| slate 1:20 | The candidate ends; cap and span both reached. |
| when the Publisher ends the slate | The replacement terminates; the channel resumes at RT. |

Had the Publisher also declared an overlay window **on the primary timeline**
over the blacked-out span:

- **with no relation**, a Player of this specification presents it only over
  the channel; a form on screen at 45:00 ends there, and the window presents
  nothing over the slate (PLY-49);
- **with `on-top`**, it is composited over the slate, with the budget above
  (PLY-50) — the Publisher's explicit choice to put a primary-timeline ad
  over whatever the replacement contains;
- **with `supersede`**, the Player would present that window over the channel
  and not execute the replacement (PLY-48), showing the programme the
  Publisher blacked out. The Player cannot see that the replacement is a
  blackout; that is why the declaration is the Publisher's, and why this one
  would be an authoring error.

## Annex O — Publisher-restricted layouts forwarded to the APS

### O.1 The scenario

An overlay slot on which the Publisher does not want the programme interrupted
or halved: it admits only `overlay-lower-third` and
`squeezeback-l-shape-upper-left` — no double box, no full-screen takeover. The
Player forwards the set to the APS, so the ads chosen upstream are already
inside it, and still checks what comes back. The ADS has the four options of
Annex I.

### O.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT1H12M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/concert2/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="2400000" duration="20000">
        <svta:OverlayPresentation uri="https://aps.example.com/nl/overlay?c=2&amp;w=1"
                                  durationCap="20000"
                                  allowedLayouts="overlay-lower-third squeezeback-l-shape-upper-left"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.640028" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### O.3 The requests

`A` stands for `sgai-allowed-layouts=overlay-lower-third%20squeezeback-l-shape-upper-left`,
sent unchanged by every class (PLY-15).

| Class | Query added to `/nl/overlay?c=2&w=1` |
|---|---|
| D1 | `&A&sgai-video-decoders=2&sgai-image-over-video=1&sgai-html-over-video=1` |
| D2 | `&A&sgai-video-decoders=2&sgai-image-over-video=0&sgai-html-over-video=0` |
| D3 | `&A&sgai-video-decoders=1&sgai-image-over-video=1&sgai-html-over-video=1` |
| D4 | `&A&sgai-video-decoders=1&sgai-image-over-video=1&sgai-html-over-video=0` |
| D5 | `&A&sgai-video-decoders=1&sgai-image-over-video=0&sgai-html-over-video=0` |

### O.4 What the APS derives

| Option at the ADS | Layout in the set? | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|---|
| 1 double box + bg, video | no — removed (APS-9) | | | | | |
| 2 L-shape, image | yes | keep | out: image = 0 | keep | keep | out |
| 3 lower-third, image | yes | keep | out | keep | keep | out |
| 4 takeover, video | no — removed | | | | | |

### O.5 The resolution documents

**For D1, D3 and D4:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="PT5S">
  <svta:Ad duration="PT20S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/l-underlay.jpg"
                          mimeType="image/jpeg"
                          layout="squeezeback-l-shape-upper-left"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/lt.png"
                          mimeType="image/png" layout="overlay-lower-third"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=901&amp;s=c2</Event>
      <Event presentationTime="20000" id="2">https://t.example.com/complete?cr=901&amp;s=c2</Event>
    </svta:Tracking>
  </svta:Ad>
</svta:OverlayList>
```

**For D2 and D5**, nothing survives, and the APS says so with a document:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="never"/>
```

No option of either document is a video, so no sub-MPD is involved.

### O.6 The walk per device class

| Class | Renders |
|---|---|
| D1 | L-shape image (checked against the set and the device: passes) |
| D2 | nothing: the empty document is a failed execution; no other window; the concert continues. The takeover D2 could play is not offered: the Publisher excluded it. |
| D3 | L-shape image |
| D4 | L-shape image |
| D5 | nothing |

### O.7 A non-conforming APS

An APS that ignored the forwarded set returns, to D2:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="never">
  <svta:Ad duration="PT20S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/takeover.mpd"
                          mimeType="application/dash+xml" layout="linear"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/901/lt.png"
                          mimeType="image/png" layout="overlay-lower-third"/>
  </svta:Ad>
</svta:OverlayList>
```

The Player finds the first option's layout outside the window's
`@allowedLayouts`, does not render it (PLY-19), moves to the second — which D2
cannot composite — and skips the candidate (PLY-20). The concert continues.
Forwarding the set moves the choice upstream; it does not move the check. The
takeover's sub-MPD is never fetched.

## Annex P — A `custom` overlay inside a Publisher region

### P.1 The scenario

The content's own graphics never occupy the upper-right area of the frame, and
the Publisher offers it: an overlay slot admits the optional `custom` layout,
bounded to the region x 60%, y 5%, width 35%, height 30%, and also admits a
lower-third. The APS places the overlay by coordinates inside the region; the
Player checks them before rendering.

### P.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT24M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/kids4/ep12/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="480000" duration="15000">
        <svta:OverlayPresentation uri="https://aps.example.com/nl/overlay?k=4&amp;e=12"
                                  durationCap="15000"
                                  allowedLayouts="custom overlay-lower-third"
                                  customRegion="60 5 35 30"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### P.3 The request

A Player that supports `custom`:

```
GET /nl/overlay?k=4&e=12&sgai-allowed-layouts=custom%20overlay-lower-third&sgai-custom-region=60%205%2035%2030&sgai-custom-layout=1 HTTP/1.1
Host: aps.example.com
```

The allowed layouts and the region are required on the request (PLY-15,
PLY-16); `sgai-custom-layout` is optional, like every capability parameter.

### P.4 The resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="PT3S">
  <svta:Ad duration="PT15S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/1601/badge.png"
                          mimeType="image/png" layout="custom" rect="65 8 25 20"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/1601/lt.png"
                          mimeType="image/png" layout="overlay-lower-third"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=1601</Event>
      <Event presentationTime="15000" id="2">https://t.example.com/complete?cr=1601</Event>
    </svta:Tracking>
  </svta:Ad>
</svta:OverlayList>
```

The APS offers a lower-third after the `custom` option because a Player that
does not support `custom` will skip it. Both options are images; no sub-MPD is
involved.

### P.5 The containment check

Region (60, 5, 35, 30), rectangle (65, 8, 25, 20):

| Test | Values | Result |
|---|---|---|
| x ≥ rx | 65 ≥ 60 | true |
| y ≥ ry | 8 ≥ 5 | true |
| x + w ≤ rx + rw | 90 ≤ 95 | true |
| y + h ≤ ry + rh | 28 ≤ 35 | true |

The rectangle is inside the region and smaller than it, which APS-12 allows.

### P.6 The walk

| Player | Renders |
|---|---|
| Supports `custom`, image over video (D1, D3, D4) | the badge at x 65%, y 8%, 25% × 20% of the video, composited over the playing programme |
| Does not support `custom`, image over video | treats the `custom` option as not renderable (PLY-21); renders the lower-third |
| D2, D5 | neither image option renders; skips |

Both kinds of Player are conformant: `custom` is optional (DOC-21).

### P.7 A rectangle outside the region

An APS returns `rect="50 8 40 20"`. The rectangle reaches x 90%, inside the
region's right edge at 95%, but starts at 50%, left of the region's 60%:
*x ≥ rx* fails. The Player discards the option without rendering it and moves
to the lower-third (PLY-21). A rectangle may be smaller than the region; it may
not extend beyond it.

## Annex Q — A non-linear ad that supersedes a linear break

### Q.1 The scenario

An on-demand drama. At 15:00 the Publisher prefers a non-linear ad, so the
programme keeps playing, and keeps a standard linear break for every case in
which the non-linear ad cannot be shown. It authors both over the same span: an
insertion event carrying a break of at most 30 seconds, and an overlay window
whose span contains the event's presentation time and which declares that it
supersedes the event. One declaration settles, for every Player, which of the
two is shown.

### Q.2 The main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="PT55M"
     minBufferTime="PT2S">
  <BaseURL>https://content.example.com/drama6/ep5/</BaseURL>
  <Period id="main" start="PT0S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="1" presentationTime="900000" duration="30000">
        <InsertPresentation uri="https://aps.example.com/linear/mid?d=6&amp;e=5"
                            earliestResolutionTimeOffset="60000"
                            maxDuration="30000"/>
      </Event>
    </EventStream>
    <EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026" timescale="1000">
      <Event id="1" presentationTime="900000" duration="30000">
        <svta:OverlayPresentation uri="https://aps.example.com/nl/overlay?d=6&amp;e=5"
                                  durationCap="30000"
                                  earliestResolutionTimeOffset="60000"
                                  allowedLayouts="squeezeback-l-shape-upper-left overlay-lower-third"
                                  linearRelation="supersede"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.64001F" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="video/$RepresentationID$/init.mp4"
                       media="video/$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="6000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="4000" startNumber="1"
                       initialization="audio/$RepresentationID$/init.mp4"
                       media="audio/$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The insertion's `Event@duration` covers the window's span, so the break stays
executable, late, for as long as the window might still fail (§7.13). Nothing
is added to the insertion event itself (DOC-26).

### Q.3 The overlay resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011"
                  xmlns:svta="urn:svta:dash:sgai:2026"
                  family="overlay"
                  dismissAfter="PT10S"
                  validFor="PT2M">
  <svta:Ad duration="PT30S">
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/1701/l-underlay.jpg"
                          mimeType="image/jpeg"
                          layout="squeezeback-l-shape-upper-left"/>
    <svta:RenderableAsset src="https://ads-cdn.example.com/nl/1701/lt.html"
                          mimeType="text/html" layout="overlay-lower-third"/>
    <svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1"
                   timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=1701</Event>
      <Event presentationTime="15000" id="2">https://t.example.com/mid?cr=1701</Event>
      <Event presentationTime="30000" id="3">https://t.example.com/complete?cr=1701</Event>
    </svta:Tracking>
    <svta:ClickThrough uri="https://brand-i.example.com/stay"/>
  </svta:Ad>
</svta:OverlayList>
```

### Q.4 The break, when it is executed

The List MPD:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="list"
     profiles="urn:mpeg:dash:profile:list:2024"
     minBufferTime="PT2S"
     svta:dismissAfter="never">
  <Period id="ad-1702" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="60">https://ads-cdn.example.com/cr/1702/cr1702.mpd</ImportedMPD>
  </Period>
  <Period id="ad-1703" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="15">https://ads-cdn.example.com/cr/1703/cr1703.mpd</ImportedMPD>
  </Period>
</MPD>
```

Its sub-MPDs, with beacon identifiers unique across the List MPD:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/1702/</BaseURL>
  <Period id="cr1702" duration="PT15S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1" timescale="1000">
      <Event presentationTime="0" id="1">https://t.example.com/imp?cr=1702</Event>
      <Event presentationTime="15000" id="2">https://t.example.com/complete?cr=1702</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static"
     profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"
     minBufferTime="PT2S">
  <BaseURL>https://ads-cdn.example.com/cr/1703/</BaseURL>
  <Period id="cr1703" duration="PT15S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1" timescale="1000">
      <Event presentationTime="0" id="11">https://t.example.com/imp?cr=1703</Event>
      <Event presentationTime="15000" id="12">https://t.example.com/complete?cr=1703</Event>
    </EventStream>
    <AdaptationSet contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>
    <AdaptationSet contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   lang="en" segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="3000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a128" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

### Q.5 The walk per device class

The Player resolves the window from 14:00 (the offset of 60 s) and knows
before 15:00 whether it will present an ad.

| Class | Window | Break | The viewer sees |
|---|---|---|---|
| D1 | L-shape image renders | not executed | 15:00–15:30: the programme in the upper-left 60%, the image around it; then full screen |
| D2 | neither option renders: no ad | executed at 15:00 | a 30-second full-screen break; the programme resumes at 15:00 |
| D3 | L-shape image (one decoder for the shrunk programme, one image surface) | not executed | as D1 |
| D4 | L-shape image | not executed | as D1 |
| D5 | no overlay surface: no ad | executed | as D2 |
| Legacy | ignores the window | executed | as D2 |

No Player presents both. The superseded event that is not executed is not
counted as executed.

### Q.6 When the window fails to resolve

The APS does not answer, answers `500`, returns a body that does not parse, or
returns the empty document. Every class then executes the break, with the base
semantics.

- If the Player knows before 15:00 — it resolved at 14:00 and the answer
  came back — the break executes on schedule, at 15:00.
- If it only knows at 15:04, say because it resolved the window at the
  moment it opened and the APS took four seconds to fail, the break
  executes late, at PRTA = 15:04 (*"PRT ≤ PRTA ≤ EAP"*, Table 57): an
  insertion plays its full 30 seconds from there, and the programme resumes
  at 15:04.
- Had the failure been known only after 15:30, the event would no longer be
  active and would be ignored, as the base ignores any event no longer
  active; the programme simply continues.

### Q.7 What this demonstrates

One declaration settles which of two ads covering the same span is shown. A
Player of this specification presents the non-linear ad where it can and the
break where it cannot; a legacy Player presents the break. Without the
declaration a Player of this specification would execute the break and
present the overlay only over the programme around it (PLY-49).

## Annex R — Test cases and conformance criteria

### R.1 How to read a test case

Each test names the criteria it checks (chapter 4 identifiers), what is set
up, and what passes. Tests of the Publisher and of the APS read a document;
tests of the Player observe a session — the requests it issues, what it
renders, the beacons it fires — on a given main MPD, resolution document and
viewer action. `DOC` criteria are checked by review of this specification and
are listed in R.2.5. A test "passes on the primary content" when playback of
the primary content continues with no visible artefact and no beacon of the
failed opportunity fires (§8.1).

Test identifiers: `R-PUB-n`, `R-ADS-n`, `R-APS-n`, `R-PLY-n`, `R-SYN-n`, `R-IF-n`,
`R-BEH-n`, `R-E-n`, `R-BC-n`.

### R.2 Chapter 4 — conformance, per actor

#### R.2.1 Publisher (checked against the main MPD)

| Test | Criteria | Check | Pass |
|---|---|---|---|
| R-PUB-1 | PUB-1 | The slot's constraints are in the MPD. | Every cap, layout set, relation, once-per-session and offset the slot relies on is an attribute of the MPD. |
| R-PUB-2 | PUB-2, PUB-3 | Every overlay and pause window carries `@durationCap`; inherited events may omit `@maxDuration`. | No window lacks `@durationCap`; a zero value is read as "does not fire". |
| R-PUB-3 | PUB-4, PUB-5, PUB-6 | `@allowedLayouts` values; `@customRegion` placement. | Every token is in §3.4.2; `custom` only by listing; `@customRegion` only with `custom`. |
| R-PUB-4 | PUB-7, PUB-8 | Event streams per Period. | One `EventStream` per SGAI scheme per Period; none carries `@value`. |
| R-PUB-5 | PUB-9, PUB-10, PUB-11 | Optional declarations. | Offsets are non-negative integers in timescale units; `@executeOnce` only on pause windows; at most one `@linearRelation` per window; on a pause window only `on-top`. |
| R-PUB-6 | PUB-12 | A non-linear ad meant during an alternative presentation. | Declared in that presentation's MPD, or by an `on-top` window of the triggering presentation. |
| R-PUB-7 | PUB-13 | Content with pause windows. | The MPD carries `Metrics` with `PlayList` and at least one `Reporting`. |
| R-PUB-8 | PUB-14, PUB-15, PUB-16 | Placement of every SGAI construct. | Each is at an extension point of §4.7; no base construct changes meaning; no baseline element a legacy Player is expected to process sits inside an `svta` element. |
| R-PUB-9 | PUB-17 | Forms the Publisher declares. | Media types are among the three forms. |

#### R.2.2 ADS

| Test | Criteria | Check | Pass |
|---|---|---|---|
| R-ADS-1 | ADS-1 | A decision whose ads exceed the cap. | Not reported as a non-conformance of the ADS. |
| R-ADS-2 | ADS-2, ADS-3 | The ADS's output. | Not checked against this specification; no device-class matrix is required of it. |

#### R.2.3 APS (checked against the resolution document alone)

| Test | Criteria | Check | Pass |
|---|---|---|---|
| R-APS-1 | APS-1, APS-2 | The document for a linear event, an overlay window, a pause window. | A List MPD (or single-period alternative MPD) for linear; `<svta:OverlayList>` whose `@family` matches the window otherwise. |
| R-APS-2 | APS-3 | Validation per §5.10.2 with the schema of §5.10.1 loaded. | Valid; the validator reports the schemas it loaded. |
| R-APS-3 | APS-4 | A no-fill decision. | The empty resolution of §5.2.3, with a `200`; never an error status or an empty body. |
| R-APS-4 | APS-5, APS-6 | Options per candidate. | At least one; document order is the ADS's order. |
| R-APS-5 | APS-8, APS-9 | Layouts. | Every `@layout` is in §3.4.2 and in the set received (or the family default when none was received). |
| R-APS-6 | APS-10, APS-11 | Forms and asset carriage. | Every `@mimeType` is among the three forms; no image or HTML URL on an `AdaptationSet` or `Representation`. |
| R-APS-7 | APS-12 | `custom` options. | `@rect` present, inside the region received (or the viewport). |
| R-APS-8 | APS-13, APS-14 | Double box and L-shape. | `@background` present exactly on `squeezeback-double-box-background`; an L-shape option carries one creative. |
| R-APS-9 | APS-15 | Requests with no capability parameters, and with each one absent in turn. | A resolution document is returned every time. |
| R-APS-10 | APS-16 | Tracking. | Callback events in the sub-MPD (linear) or in `<svta:Tracking>` (non-linear); `@value="1"`; times relative to the ad; `@id` unique across a List MPD. |
| R-APS-11 | APS-17, APS-18 | ClickThrough and metadata. | The ClickThrough and its tracking only in `<svta:ClickThrough>`; metadata, if any, in §5.7 elements. |
| R-APS-12 | APS-19, APS-20 | Dismissal declaration. | Present on every document; `never` or a non-negative duration. |
| R-APS-13 | APS-21 | Early-resolvable documents. | `@validFor` present, or the default applies. |
| R-APS-14 | APS-22 | Pause documents. | `@onExhausted` present. |

#### R.2.4 Player

| Test | Criteria | Setup | Pass |
|---|---|---|---|
| R-PLY-1 | PLY-1, PLY-4, PLY-18, PLY-19 | A document whose first option's layout is outside the window's set. | The option is not rendered; the next is evaluated. |
| R-PLY-2 | PLY-2 | An APS fed by a non-VAST ADS. | Behaviour identical to the VAST case for the same document. |
| R-PLY-3 | PLY-3 | Each opportunity type on a Player configured as each of D1 to D5. | A defined outcome — render, fall back or skip — every time, as chapter 7 gives it. |
| R-PLY-4 | PLY-5 | A candidate of media type `application/pdf`. | Skipped, or rendered only if renderable; never an error surfaced to the viewer. |
| R-PLY-5 | PLY-6, PLY-7, PLY-8 | Windows with offsets 0, 30000 and absent. | No request before the start minus the offset (60 s when absent); a Player resolving only at the start also passes. |
| R-PLY-6 | PLY-9, PLY-10 | An early document with `@validFor="PT10S"`, the window firing 30 s after receipt; re-resolution returns the empty document. | A new request at firing; nothing from the expired document is shown; the empty re-resolution is treated as E4. |
| R-PLY-7 | PLY-11 | Pauses inside and outside the pause window. | A request only for the pause inside. |
| R-PLY-8 | PLY-12, PLY-13, PLY-14 | Inspect resolution requests. | No reserved parameter with an empty or placeholder value; every non-reserved Player parameter starts with `x-<vendor>-`. |
| R-PLY-9 | PLY-15, PLY-16 | Windows with and without `@allowedLayouts` and `@customRegion`. | `sgai-allowed-layouts` and `sgai-custom-region` carry the declared values unchanged when declared, and are absent otherwise; never on linear requests. |
| R-PLY-10 | PLY-17, PLY-20 | Annex I's document on D1 to D5. | Renders option 1, 4, 2, 2, 4 respectively; a candidate with no satisfiable option is skipped for the next, then the primary content. |
| R-PLY-11 | PLY-21 | Annex P's document; the variant with `rect="50 8 40 20"`; a Player without `custom`. | Renders the contained `custom` option; discards the uncontained one; without support, renders the lower-third. |
| R-PLY-12 | PLY-22, PLY-23 | Annex J's and Annex I's documents on D2 and D3. | D2 declines every option with an image or HTML element; D3 declines every video double box and video L-shape. |
| R-PLY-13 | PLY-24, PLY-26, PLY-37 | A candidate declaring PT10S whose media runs 14 s, cap 12000. | Rendering stops at 12 s of presentation time. |
| R-PLY-14 | PLY-25, PLY-27 | Annex B's late start, with `@clip` true and false. | Ends at 630 s with `true`, at 634 s with `false`. |
| R-PLY-15 | PLY-28 | Cap 15000 with candidates `PT15S`, `PT15.0004S`. | The first is admitted; the second converts to 15001 and is not admitted whole. |
| R-PLY-16 | PLY-29, PLY-30 | An overlay window without `@durationCap`; one with `durationCap="0"`; an insertion without `@maxDuration`. | No request or no ad for the first two; the insertion executes with an unbounded cap. |
| R-PLY-17 | PLY-31, PLY-32 | Annex H's pause during an overlay; a pause slot with `repeat` held for longer than the cap. | The overlay resumes with its remaining cap; the pause slot continues pass after pass. |
| R-PLY-18 | PLY-33 to PLY-36 | Annex F's break. | Order preserved; the fourth ad dropped or trimmed, never moved. |
| R-PLY-19 | PLY-38, PLY-39, PLY-40 | Annex L, each path, and the variant where the second window starts earlier. | The chain order and outcomes of L.3 and L.4. |
| R-PLY-20 | PLY-41 | Annex L.7. | No request to the second window. |
| R-PLY-21 | PLY-42 | A `family="pause"` document returned for an overlay window, with a fallback window. | Nothing from it is shown; the fallback window is requested. |
| R-PLY-22 | PLY-43 | Annex L.5. | The lower-third option is never rendered on window 2; the cap is 20000. |
| R-PLY-23 | PLY-44, PLY-64 | An empty resolution on an `@executeOnce="true"` event and on a once-per-session pause window. | Both remain executable. |
| R-PLY-24 | PLY-45, PLY-46, PLY-47 | Annex C. | One form at a time; candidates in order; the sum within the cap. |
| R-PLY-25 | PLY-48 | Annex Q on D1 and D2, and with each failure shape. | D1: window shown, break not executed. D2 and every failure: break executed, on schedule or late as Q.6 states. |
| R-PLY-26 | PLY-49 | Annex D without `linearRelation`. | No overlay over the linear ad; the break executes. |
| R-PLY-27 | PLY-50 | Annex D. | The overlay is composited over the linear ad on D1 to D4 as D.7 gives it. |
| R-PLY-28 | PLY-51 | Annex N. | The slate's window is presented over the slate. |
| R-PLY-29 | PLY-52, PLY-53, PLY-54 | Annex H, Branches A and B. | As H.7 and H.8. |
| R-PLY-30 | PLY-55 | A pause during a linear ad with an applicable pause window. | Linear ad suspended, pause ad shown, linear ad resumed where it stopped. |
| R-PLY-31 | PLY-56, PLY-59 | A D3 Player releasing its decoder for a video pause ad. | On resume, the primary content continues at the paused position. |
| R-PLY-32 | PLY-57, PLY-58, PLY-60 | Resume during a pause ad. | The ad is gone within one frame; no later beacon fires. |
| R-PLY-33 | PLY-61 | `pause-partial` with an overlay active. | The overlay is suspended; one ad surface. |
| R-PLY-34 | PLY-62 | Annex E.10. | Presentation time frozen at 40:00 for the whole pause. |
| R-PLY-35 | PLY-63 | Annex E.10, second pause. | Nothing shown. |
| R-PLY-36 | PLY-65, PLY-66 | Annex E.7, and variants with `repeat`, `stop` and no `@onExhausted`. | As E.7; `stop` when undeclared. |
| R-PLY-37 | PLY-67 to PLY-70 | Annex B.7; an image overlay at 2x. | Ads at the content's speed; wall-clock length halved; beacons on presentation time. |
| R-PLY-38 | PLY-71, PLY-72, PLY-73 | Annex J and Annex I on D1. | Background in the bands, black without one; the L-shape region as the token names. |
| R-PLY-39 | PLY-74 to PLY-77 | Annex C with dismissal at 3 s and at 10 s. | Not offered at 3 s; at 10 s the whole slot ends, beacons after it do not fire, the film is untouched. |
| R-PLY-40 | PLY-78 | A linear event with explicit `@skipAfter="PT5S"` and a List MPD with `svta:dismissAfter="never"`; the same event without `@skipAfter`. | Dismissible from 5 s in the first; not dismissible in the second. |
| R-PLY-41 | PLY-79, PLY-80 | Annex A, and Annex B.6. | Beacons at their times; none after the trim. |
| R-PLY-42 | PLY-81 | Annex C (same `@id` in two candidates); Annex F. | Both candidates' beacon `1` fire; every beacon of the break fires once. |
| R-PLY-43 | PLY-82 | A candidate that starts 4 s late in its window. | Its beacon at 0 fires when the candidate starts, not at the window start. |
| R-PLY-44 | PLY-83, PLY-85, PLY-87 | Unknown elements inside `<svta:Ad>`; metadata elements; an SGAI stream with `@value`. | Ignored; no effect on rendering. |
| R-PLY-45 | PLY-84 | Annex K. | On activation: the destination opens, each click-tracking URL is requested once; never on the timeline. |
| R-PLY-46 | PLY-86 | An ad segment returning `404` mid-ad. | The ad is abandoned; the primary content continues. |
| R-PLY-47 | PLY-88 | A `PlayList` with a rebuffering stall and a pause. | Only the pause counts as a paused interval. |

#### R.2.5 This document (checked by review)

| Check | Criteria | Where |
|---|---|---|
| Every construct passes the checklist and removal leaves a valid MPD | DOC-1, DOC-2, DOC-42 | §4.7 |
| No base semantics altered; the one departure recorded | DOC-3, DOC-4, DOC-6 | §4.8 |
| Four-actor fit | DOC-5 | §1.2, §1.3 |
| VAST independence and coverage | DOC-7 to DOC-11 | §2, §6.6, Annexes A.7, C.8 |
| Interface and parameters | DOC-12 to DOC-16 | §5.8 |
| Vocabulary, forms, device classes, `custom` | DOC-17 to DOC-21 | §3.4 to §3.6, §5.3.5 |
| Layout delegation | DOC-22 | §1.3, §3.4.2 |
| Composition, priority, fallback, relation | DOC-23 to DOC-27 | §4.5.6 to §4.5.9, §5.1.6 |
| Tracking, ClickThrough, metadata, metric | DOC-28 to DOC-33 | §5.5 to §5.7, §5.9, §5.10.2 |
| Justification, reuse, simplicity, positive obligations, playback | DOC-34 to DOC-38 | §4.8 |
| Names and URIs | DOC-39 to DOC-41 | §2.1, §3.4 |

### R.3 Chapter 5 — syntax

| Test | Check | Pass |
|---|---|---|
| R-SYN-1 | Every MPD of Annexes A to Q, with the schema of §5.10.1 loaded. | Valid against the base schema. |
| R-SYN-2 | Every `<svta:OverlayList>` of the annexes. | Valid against §5.10.1. |
| R-SYN-3 | Co-occurrence: `@rect` with `custom`, `@background` with the background token, `@customRegion` with `custom`, `@onExhausted` on pause documents. | Each holds; each violation is detected. |
| R-SYN-4 | The empty resolutions of §5.2.3. | Valid; recognised as carrying no candidates. |
| R-SYN-5 | `PercentRect` and `LayoutTokenList` values with a comma separator, five numbers, a value above 100, an unknown token. | Rejected. |

### R.4 Chapter 6 — interfaces

| Test | Check | Pass |
|---|---|---|
| R-IF-1 | Each response row of §6.5. | The Player's outcome is the one in the row. |
| R-IF-2 | A resolution request with a Publisher query, a `RequestParam` output and reserved parameters. | All three present; reserved names percent-encoded; no duplicate names. |
| R-IF-3 | A `RequestParam` whose `@includeInRequests` is `urn:svta:dash:sgai-resolution:2026`. | Its parameters appear on window requests and on no base request. |

### R.5 Chapter 7 — expected behaviour, per scenario

| Test | Scenario | Annex | Pass |
|---|---|---|---|
| R-BEH-1 | Pre-roll | A | A.5, A.6 |
| R-BEH-2 | Mid-roll, on time and late | B | B.5, B.6 |
| R-BEH-3 | Coexisting overlay | C | C.6, C.7 |
| R-BEH-4 | Hybrid | D | D.7, D.8 |
| R-BEH-5 | Pause, VOD and live | E | E.6 to E.10 |
| R-BEH-6 | Multi-ad break | F | F.5, F.6 |
| R-BEH-7 | Legacy Player | G | G.6, G.10 |
| R-BEH-8 | Overlay crossing pause | H | H.7 to H.9 |
| R-BEH-9 | Ordered options | I | I.6 |
| R-BEH-10 | Double box | J | J.7 |
| R-BEH-11 | ClickThrough | K | K.5 to K.7 |
| R-BEH-12 | Overlapping windows | L | L.4, L.6, L.7 |
| R-BEH-13 | Declared capabilities | M | M.7 |
| R-BEH-14 | Non-advertising replacement | N | N.6, N.7 |
| R-BEH-15 | Forwarded layouts | O | O.6, O.7 |
| R-BEH-16 | `custom` | P | P.6, P.7 |
| R-BEH-17 | Supersede | Q | Q.5, Q.6 |

### R.6 Error conditions

The conditions of §8.2, restated with the test that exercises each.

| Condition | Restated | Test | Pass |
|---|---|---|---|
| E1 | Transport failure or non-`200` status on the resolution request. | R-E-1 | Next window of the family; primary content when none; on a superseding window, the break. |
| E2 | `200` with an unparsable or invalid body. | R-E-2 | As E1; nothing rendered from the body. |
| E3 | `200` with a document of the wrong family. | R-E-3 | As E1; none of its candidates shown. |
| E4 | `200` with a document carrying no candidates. | R-E-4 | As E1; the opportunity not consumed. |
| E5 | Late or expired document. | R-E-5 | No slot extended; nothing presented from an expired document. |
| E6 | Window without `@durationCap` or `Event@duration`; zero cap. | R-E-6 | No ads; primary content. |
| E7 | No satisfiable option. | R-E-7 | Next candidate; then primary content; never the next window. |
| E8 | Inadmissible layout. | R-E-8 | Option not rendered; next option. |
| E9 | Inadmissible form or carrier. | R-E-9 | Never rendered if the device cannot render it. |
| E10 | Cap reached, declared or actual. | R-E-10 | Stop at the bound, even mid-ad; order kept. |
| E11 | Runtime failure of an accepted ad. | R-E-11 | Ad abandoned; primary content continues. |
| E12 | Unknown construct. | R-E-12 | Ignored with its content; playback continues. |
| E13 | Beacon or click-tracking failure; beacons after trim, resume or dismissal. | R-E-13 | Ad and content unaffected; no beacon after the boundary. |
| E14 | Two forms competing for the screen. | R-E-14 | At most one non-linear form; pause priority; relation honoured. |
| E15 | Pause candidates exhausted; window consumed. | R-E-15 | Declared behaviour, `stop` by default; at most one pause ad per once-per-session window. |

### R.7 Backward compatibility, per construct

Each test uses a representative document containing the construct, a Player
that implements the base specification and not this one, and checks the one
invariant that holds in every case: **the construct is skipped silently and no
tracking beacon fires for it.** What the viewer sees around it is the
Publisher's authoring choice (§7.16) — the primary content for live content,
or the standard break when an on-demand Publisher authored one — and the
standard break is a base construct outside the construct's own test.

| Test | Construct | Representative document | Pass |
|---|---|---|---|
| R-BC-1 | C1 overlay window | Annex C.2; Annex G.2 | No request to the window's `@uri`; no error logged at fatal level; the primary content plays (C.2), or the standard break and then the content (G.2). |
| R-BC-2 | C2 pause window | Annex E.2 | A pause requests nothing and shows nothing; resume continues the content. |
| R-BC-3 | C3 List MPD extension content | Annex A.3; Annex K.3 | The ads play as base ads; the `svta` content is removed without error; the click is inert. |
| R-BC-4 | C4 `<svta:OverlayList>` | Any overlay annex | The document is never requested. |
| R-BC-5 | C5 request-type URN | §5.8.1 example | The URN is dropped from `@includeInRequests`; no base request gains its parameters. |

The same documents after removal of the extension namespace (as in Annex G.3)
are valid against the base schema.

### R.8 What is not tested here

- The APS-to-ADS exchange and the conversion from the ADS's format, which are
  outside this specification.
- The transport of measurements.
- How dismissal is offered to the viewer, and how a ClickThrough destination is
  opened.
- Retry policies (§8.4) and the surfacing of conditions to the application
  (§8.11), which are implementation choices.

# SGAI for Linear and Non-Linear Ads in MPEG-DASH

**Server-Guided Ad Insertion (SGAI) for linear and non-linear
advertising in MPEG-DASH — an extension of the base specification.**

Status: draft for working-group review.
Incubation venue: SVTA Advertisement Working Group.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**,
**SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**
and **OPTIONAL** in this document are to be interpreted as described
in IETF RFC 2119.

Notation: `@attr` denotes an XML attribute and an element name appears
capitalised, following the convention of the base specification.

A reference written **`§N.N`** is to a section of **this document**. A
reference written **`DASH §N.N`** is to a clause of the **base
specification** named in chapter 2, and a table or figure of the base
specification is likewise written `DASH Table N`. The two numbering
spaces overlap — both documents have a §5.2.1 and an §8.1 — so the
prefix is what tells them apart, and every citation of the base
specification carries it.

A claim that could not be verified against a primary source is tagged
`[inferred]`.

---

## 1. Scope

This specification defines Server-Guided Ad Insertion for **both
linear and non-linear advertising** in MPEG-DASH, as a complete
extension of the base specification named in chapter 2.

Under SGAI the ad decision is taken server-side and the Player is
guided to it rather than handed a stitched stream: the manifest
carries an opportunity declaration, and when the opportunity becomes
current the Player resolves a URL and receives a document describing
the ads on offer. The base specification already carries this pattern
for linear ads through its Alternative MPD insertion and replacement
events and its List MPD profile. Those constructs are **absorbed as
the baseline** of this specification, with clarifications and minor
extensions where they are stated below.

The principal new content is **non-linear**: an ad that coexists with
the primary content instead of taking it over — an overlay composited
on the playing video, a squeezeback that shrinks the content to share
the frame, a pause ad shown over the paused frame. The base
specification's ad machinery is substitutive by construction and
carries no construct for any of them, so this specification defines
the opportunity declaration, the resolution document, the presentation
option, the carriers for non-audiovisual creatives, click-through and
creative metadata, and the Player obligations that compose them.

The audience is the four parties the exchange runs between: the
Publisher who authors the manifest, the Ad Decision Server that
decides which ads to serve, the Ad Presentation Server that presents
that decision to the Player, and the Player that validates it and puts
it on screen. Chapter 4 states what each has to do to claim
conformance.

### 1.1 What this specification covers

- Declaring a linear ad opportunity on the primary timeline, and
  declaring a non-linear one — an overlay window or a pause-trigger
  window — alongside it (§5.1).
- The resolution documents an Ad Presentation Server returns: the
  inherited linear `ListMPD`, the Overlay Resolution Document defined
  here, and the shape of a resolution that carries no ads (§5.2).
- The presentation option: a creative-carrier form paired with a
  layout, carried as an ordered list on one ad candidate, with
  document order as the preference order (§5.3).
- The accepted ad types and visual placements, taken by normative
  reference from the IAB catalogue and narrowed to a closed set for
  this edition (§3.2).
- Creative carriage for video through the base specification's
  imported-MPD path, and for still images and HTML documents through
  a carrier that the base specification's media-type constraints
  admit (§5.3.2, §5.4).
- Tracking: timeline-scheduled beacons on the base specification's
  callback event scheme, and a click-through carrier for the one
  event the base specification's timeline cannot express (§5.5,
  §5.6).
- What the Player declares about its device on the resolution
  request, and what the absence of a declaration means (§5.8).
- The composition and arbitration rules — one active non-linear form
  at a time, the slot cap enforced against actual rendered length,
  the pause ad's priority over an overlay and over a linear ad,
  overlapping windows of one family as a fallback chain (§4.6, §7).
- Measurement of pause-ad delivery, derived from the metric the base
  specification already defines (§5.9).
- Backward compatibility: every construct introduced here is
  expressed through an extension point of the base specification
  whose ignore-if-unknown behaviour leaves a Player that predates
  this specification playing the primary content (§4.7).

### 1.2 What this specification leaves out of scope

- **A layout engine.** Spatial arrangement inside a layout is
  delegated to HTML5 and CSS, and the layout vocabulary is the IAB's.
  This specification declares no positioning attribute, no coordinate
  model and no dimensional cap of its own; where an ad sits inside its
  layout follows from the IAB ad type the layout token names (§3.2).
- **The decisioning logic, and the interface that carries it.** Which
  ads exist, which are eligible, how many fill a break and in what
  order are the Ad Decision Server's. The request the Ad Presentation
  Server makes of it, and the format of the decision it returns, are
  agreed between those two parties and are not defined here (§6.7).
- **Ad types outside the closed set of §3.2**, including every ad
  rendered off the video surface: menu, guide and home-screen ads,
  screensaver ads, and companion or multi-screen ads. These are the
  application's ad integration rather than the Player-facing contract
  this specification defines.
- **Creative carriers outside video, still image and HTML** (§3.3).
  A scripted creative is wrapped in an HTML document rather than
  delivered as a script.
- **Interactive ad frameworks.** An ad built on a framework such as
  SIMID is delivered by that framework; no form defined here carries
  such a payload.
- **Single-decoder slice or tile replacement**, in which one decoder
  carries both the primary content and the ad. The technique exists
  and is standardised for one codec family **inside the base
  specification** — its supplementary-video descriptor specifies, for
  VVC, that the descriptor *"enables achieving picture-in-picture
  using a single VVC decoder, where the `@processingInfo` is used to
  signal the possibility of replacing the portions of the main video
  stream with the supplement video stream before sending to a single
  VVC decoder"* (DASH §5.8.5.16.4). It is excluded here as a scope
  decision, not because it is unavailable: the decoder budget this
  specification reasons with (§5.3.7.3) assumes one decoder per
  concurrent form, and a later edition may relax that.
- **Preventing a viewer from seeking past a non-linear opportunity.**
  On an inherited linear break the base specification's `@noJump`
  applies unchanged: the ad occupies the timeline, so forbidding the
  jump forbids skipping the ad. On the non-linear families it is
  excluded, because the region a non-linear window spans is
  programme — the primary content keeps playing underneath the ad — so
  forbidding the jump there would oblige the viewer to watch content
  they chose to skip rather than to watch the ad.
- **Server-side ad insertion and manifest stitching.** This
  specification is client-side rendering under server guidance.
- **Post-roll slots**, and simultaneous presentation of two or more
  non-linear forms. Both are candidates for a later edition.

## 2. Normative references

| Reference | Version pin | Used for |
|---|---|---|
| ISO/IEC 23009-1:2026, *Information technology — Dynamic adaptive streaming over HTTP (DASH) — Part 1: Media presentation description and segment formats*, Sixth edition, 2026-07 | Sixth edition, 2026-07 | The base specification. Every §N.N reference in this document is to this edition. |
| IETF RFC 2119 | BCP 14, March 1997 | The obligation vocabulary of this document. |
| IETF RFC 4337, *MIME Type Registration for MPEG-4* | November 2005 | The media-type registry the base specification binds every Representation's `@mimeType` to (DASH §7.3.1). |
| IETF RFC 6381, *The 'Codecs' and 'Profiles' Parameters for "Bucket" Media Types* | August 2011 | The production every `@codecs` value in this document follows. |
| IETF RFC 6454, *The Web Origin Concept* | December 2011 | Origin comparison, where the base specification's URL-parameterisation mechanism restricts a parameter to its own origin. |
| IETF RFC 8141, *Uniform Resource Names (URNs)* | April 2017 | The production the URNs this specification mints follow, as the base specification requires of profile identifiers (DASH §8.1). |
| IAB Tech Lab, *Ad Format Guidelines for Digital Video and CTV* | Final release, May 2026 — **live reference, not snapshotted** | The ad types, visual placements and their spatial bounds accepted in §3.2. The IAB owns this vocabulary; this specification accepts a subset of it and defines none of it. |
| IAB Tech Lab, *Video Ad Serving Template* (VAST) 4.x | Any 4.x | **Informative only.** Named in illustrative material about what an Ad Decision Server typically emits (§6.7). No construct, obligation or behaviour in chapters 4 to 8 depends on VAST or on any VAST version. |
| CTA-5004, *Common Media Client Data* (CMCD) | — | The key vocabulary the base specification's state substitution can lift a value from (§5.8.1). Referenced through the base specification, not extended here. |

### 2.1 Scheme URIs and namespaces introduced by this edition

| URI | Kind | Introduced by | Meaning |
|---|---|---|---|
| `urn:svta:dash:sgai:2026` | XML namespace | this edition | The namespace every XML element and attribute this specification introduces lives in. Bound to the prefix `svta:` throughout this document. |
| `urn:svta:dash:event:sgai-overlay:2026` | `EventStream@schemeIdUri` | this edition | An event stream of non-linear overlay opportunity windows (§5.1.3). |
| `urn:svta:dash:event:sgai-pause-trigger:2026` | `EventStream@schemeIdUri` | this edition | An event stream of pause-trigger windows (§5.1.4). |
| `urn:svta:dash:profile:sgai-overlay-list:2026` | `MPD@profiles` value | this edition | Identifies an Overlay Resolution Document (§5.2.2). |
| `urn:svta:dash:request:sgai-resolution:2026` | `@includeInRequests` request type | this edition | Names the non-linear resolution request as a request type, for the base specification's URL-parameterisation mechanism (§5.8.1). |

The year suffix is the edition year. A construct whose semantics change
in a later edition takes a new year; one whose semantics are unchanged
keeps its URI. A Player implementing a later edition SHOULD recognise
both that edition's URIs and this edition's.

Reused from the base specification without modification, and listed
here because this specification depends on them:

| URI | Clause | Used for |
|---|---|---|
| `urn:mpeg:dash:event:alternativeMPD:insert:2025` | DASH §5.16.3 | Linear insertion opportunity (§5.1.1). |
| `urn:mpeg:dash:event:alternativeMPD:replace:2025` | DASH §5.16.4 | Linear replacement opportunity (§5.1.2). |
| `urn:mpeg:dash:event:callback:2015` | DASH §4.7, DASH §5.10.4.5 | Every timeline-scheduled tracking beacon (§5.5). |
| `urn:mpeg:dash:profile:list:2024` | DASH §8.14 | The linear `ListMPD` (§5.2.1). |
| `urn:mpeg:dash:profile:sps:2024` | DASH §8.15 | Every sub-MPD reached through `<ImportedMPD>` (§5.4). |
| `urn:mpeg:dash:urlparam:2025` | DASH Annex I.3 | The Publisher's author-declared query template (§5.8.1). |

Vendor-private experimental extensions that are not part of this
specification use a vendor namespace of the implementer's own and are
not listed here.

## 3. Terms, definitions, abbreviations

### 3.1 Core terms

**Server-Guided Ad Insertion (SGAI).** A pattern in which the ad
decision is taken server-side and the manifest carries a reference the
Player resolves to obtain it, rather than the ad being stitched into
the primary content upstream of the Player.

**Publisher.** The party that owns the primary content and the
viewer's screen, authors the manifest, and declares every constraint
that applies to an ad opportunity.

**Ad Decision Server (ADS).** The ad-decisioning authority. It decides
which ads to serve for an opportunity, how many and in what order, and
it owns the tracking schedule. It emits a **decision document** and
performs no conversion into any DASH-native shape.

**Ad Presentation Server (APS).** The Player-facing adapter. It
exposes the endpoint the slot's `@uri` resolves to, obtains the ad
decision, and converts it into the **resolution document** the Player
reads. It is not the decisioning authority and it does not enforce the
Publisher's constraints.

**Player.** The client that reads the manifest, issues the resolution
request, validates each candidate against what the Publisher declared,
selects what to present, and composes it on screen. It is the enforcer
of the Publisher's policy.

**Ad opportunity, slot.** A declaration in the primary manifest that
an ad may be presented — where on the timeline, of which family, under
which constraints. "Slot" and "opportunity window" are used
interchangeably for it.

**Slot family.** The kind of opportunity a window declares. Three
families exist: **linear**, **overlay** and **pause**. A family is not
a layout: it says what kind of opportunity this is, while a layout
token says how one presentation is arranged in the frame.

**Opportunity window.** The interval of the primary timeline over
which an opportunity is valid, given by the declaring `<Event>`'s
`@presentationTime` and `@duration`.

**Resolution request.** The HTTP GET the Player issues against a
slot's `@uri` when the opportunity becomes current.

**Resolution document.** The document the APS returns in answer. For a
linear slot it is a `ListMPD` (§5.2.1); for an overlay or pause slot
it is an Overlay Resolution Document (§5.2.2).

**Ad candidate.** One ad offered in a resolution document, carrying its
presentation options, its declared duration, its tracking and its
click-through.

**Presentation option.** A **form** paired with a **layout**, offered
for a candidate. A candidate carries one or more as an ordered list,
and document order is the preference order.

**Form.** The creative-carrier type of a presentation option: `video`,
`image` or `html` (§3.3).

**Layout.** The spatial arrangement a presentation option takes in the
frame, named by a token from the closed set of §3.2.

**Linear ad.** An ad whose form takes over the primary content surface
for the slot. The timing positions this edition supports are pre-roll,
mid-roll and the multi-ad break.

**Non-linear ad.** An ad that coexists with the primary content rather
than taking it over: composited over the playing video, or sharing the
frame with it, or shown over the paused frame.

**Earliest Resolution Time (ERT).** The earliest instant at which the
Player may issue the resolution request for a slot, obtained by
subtracting the slot's `@earliestResolutionTimeOffset` from the
declaring event's `@presentationTime`.

**Slot cap.** The maximum the Publisher declares on a slot, carried as
`@maxDuration`. What it bounds depends on the family (§4.6.4).

**Sub-MPD.** An MPD reached through `<ImportedMPD>`, bound by the base
specification to the Single-Period Static profile (§5.4).

**Empty resolution.** A well-formed, complete resolution document that
carries no ad candidates (§5.2.3).

**Pause-trigger window.** A non-linear opportunity window whose
trigger is a viewer pause beginning inside it, rather than the playhead
reaching it (§5.1.4).

**Fallback chain.** Two or more windows of one family whose
opportunity windows overlap in time. The first is served; the rest are
attempted only when an attempt produces no ad (§4.6.8).

### 3.2 Accepted ad-type and visual-placement values

Ad types and their visual templates are defined and maintained by the
IAB. This specification references those definitions normatively,
introduces no ad-type category and no visual template of its own, and
accepts an explicit **closed subset** of the IAB catalogue for this
edition. Every accepted entry is rendered on or within the video
surface.

The subset is edition-scoped by design. An IAB ad type or visual
placement that is not in the table below is out of scope for this
edition, and one the IAB publishes later does not enter scope
automatically; widening the set requires a new edition.

| Layout token | IAB ad type | IAB visual placement | Family it is admissible on |
|---|---|---|---|
| `linear` | Linear Ad | Full video viewing pane | Linear slots; and an overlay slot, as the full-screen takeover option of last resort |
| `overlay` | Overlay | — (the base type: a plain image or HTML overlay with no named placement) | Overlay |
| `overlay-corner` | Overlay | Corner Overlay | Overlay |
| `overlay-lower-third` | Overlay | Lower-Third Overlay | Overlay |
| `squeezeback-l-shape` | Squeezeback | L-Shape | Overlay |
| `squeezeback-double-box` | Squeezeback | Double Box Video | Overlay |
| `squeezeback-double-box-with-background` | Squeezeback | Double Box Video + Background | Overlay |
| `pause-fullscreen` | Pause Ad | Fullscreen | Pause |
| `pause-partial` | Pause Ad | Partial Screen | Pause |

Four IAB ad types are therefore accepted — Linear Ad, Overlay,
Squeezeback and Pause Ad — and the tokens above are their accepted
placements.

**The pause type has no bare token.** Every pause ad is one surface or
the other, so a declaration naming neither would leave the surface
choice undetermined; and a Publisher can only admit one surface and
exclude the other if the two are distinguishable in the slot's
`@allowedLayouts`. This is why `pause-fullscreen` and `pause-partial`
are separate tokens and `pause` is not a token at all.

**Each token carries the IAB's spatial bound by reference.** The
Corner Overlay occupies no more than a quarter of the frame; the
L-Shape leaves the primary content at 60 % of the frame; the Double
Box gives content and ad a quarter of the frame each. This
specification inherits those bounds from the IAB guidelines rather than
restating them, and declares no dimensional attribute on the slot or on
a presentation option.

**Out of scope, named explicitly.** Menu ads (home screen, content
menu, guide), screensaver ads, companion and multi-screen ads, and
in-scene composition are all outside the set above: the first three
render off the video surface, in the Player chrome or the application
UI, and the fourth is composited into the programme upstream of the
Player. Because the set above is closed these are already excluded;
they are named so that the off-video-surface category is unambiguous.

### 3.3 Admissible creative carriers

Exactly three creative-carrier forms are admissible:

| Form | Concrete media types | Carriage |
|---|---|---|
| `video` | `video/mp4`, `audio/mp4`, `application/mp4` — the registry the base specification binds a Representation to | Through `<ImportedMPD>` into a sub-MPD (§5.4) |
| `image` | `image/jpeg`, `image/png`, `image/webp` | A URL on the presentation option (§5.3.2) |
| `html` | `text/html` | A URL on the presentation option (§5.3.2) |

An HTML creative MAY contain inline `<script>` per HTML5 semantics; the
script runs under the device's HTML capability contract and is not a
separate carrier. A carrier outside these three — a raw script, a
vector image as payload, a document format, a proprietary binary — is
out of scope, and no annex, example or implementation note in this
document adds one.

### 3.4 Device classes

A device class captures only what bears on this specification: how
many video decoders the device runs concurrently, and which surface
types it composites together with video. Codec support, content
protection and network conditions are orthogonal and are handled
elsewhere in a Player.

| Class | Concurrent video decoders | Image over video | HTML over video |
|---|---|---|---|
| **D1** | 2 or more | yes | yes |
| **D2** | 2 | no | no |
| **D3** | 1 | yes | yes |
| **D4** | 1 | yes | no |
| **D5** | 1 | no | no |

D2 is the class that most often surprises a reader: it has the decoder
budget for a second video and no ability to composite a non-video
surface at all, so it renders a video overlay and declines an image
one. D5 declines every non-linear form and takes the full-screen
takeover.

### 3.5 Abbreviations

| Abbreviation | Expansion |
|---|---|
| ADS | Ad Decision Server |
| APS | Ad Presentation Server |
| ERT | Earliest Resolution Time |
| IAB | Interactive Advertising Bureau (IAB Tech Lab) |
| MPD | Media Presentation Description |
| SGAI | Server-Guided Ad Insertion |
| SPS | Single-Period Static profile (DASH §8.15) |
| SVTA | Streaming Video Technology Alliance |

## 4. Conformance

### 4.1 Conformance scope

An implementation claims conformance **as one actor**. The four actors
are independently conformant: a Player conforms by satisfying §4.6, an
APS by satisfying §4.5, and neither claim depends on the other party
being conformant. This matters at runtime, because the Player is
required to keep the primary content playing whatever the other three
emit.

Two kinds of obligation appear below. A **runtime** obligation is
checked by observing what an actor does; a **document** obligation is
checked by inspecting an artefact the actor produced — a manifest, or a
resolution document.

**What a conformance statement can promise.** The base specification
does not specify Player behaviour: *"as DASH Client operation is not
specified normatively in this document, it is also unspecified how a
DASH Client conforms to a particular profile. Hence, profiles merely
specify restrictions on MPD and Segments rather than DASH Client
behaviour"* (DASH §8.1, NOTE 1), and DASH §5.2.1 contemplates a client that
removes every element outside the base schema and still presents a
conforming Media Presentation. Every obligation this chapter places on
a Player is therefore an obligation on **a Player conformant to this
specification**. No construct defined here, in any namespace and under
any profile, reaches a Player that has never heard of this
specification; what such a Player does is covered by §4.7 instead.

**The governing invariant.** Applying this specification never breaks
primary-content playback. Where an opportunity cannot be honoured, for
any reason at any stage, the outcome is that the primary content
continues uninterrupted and the viewer cannot tell an opportunity
existed. This is not this specification's invention: the base
specification states it for its own execution model — *"If no event can
be successfully executed, the playback continues uninterrupted"*
(DASH §5.16.2.2.5) and *"A failed execution results in smooth continued
playback of the main media presentation"* (DASH §5.16.2.2.6) — and this
specification extends the same guarantee to the constructs it adds.

### 4.2 The four-actor contract

| Decision | Owner |
|---|---|
| When an ad opportunity appears on the timeline | Publisher |
| Which ad types and layouts a slot admits, and the slot cap | Publisher |
| How many ads fill an opportunity, which ads, in what order | ADS |
| Targeting, frequency capping, brand safety, competitive separation | ADS |
| Which tracking beacons exist and at which relative times | ADS |
| Converting the decision into the resolution document | APS |
| Which presentation options a candidate carries, and their order | APS |
| The pause-exhaustion behaviour of a pause resolution document | APS |
| What the Player discloses about its device | Player |
| Validating each candidate against the window that served it | Player |
| Selecting the presentation option to render | Player |
| Compositing and rendering | Player |

Authority over the screen is held jointly by the Publisher, who
declares, and the Player, who enforces. Neither the ADS nor the APS is
normatively bound by the Publisher's slot constraints, and this
specification requires neither of them to validate against them. That
separation is what lets one ADS serve many Publishers through their
APSs without coupling its logic to any Publisher's policy, and lets a
Player guarantee the Publisher's constraints even when the ADS and the
APS are external, unaudited services.

### 4.3 Publisher obligations

The Publisher is an authoring-time actor: every obligation below is a
document obligation, and every unmet one degrades into a Player-side
skip rather than into interrupted playback.

**4.3.1 Declare every constraint in the manifest.** The constraints
that apply to an ad slot — the cap, the admissible layouts, the
resolution-timing bound, any once-per-session bound — are declared in
the MPD by the Publisher. No actor infers them at runtime.

**4.3.2 Declare a maximum duration on every slot.** Every ad slot the
MPD declares, linear or non-linear, carries `@maxDuration`.

This is a **deliberate narrowing** of the base specification, which
treats an absent value as unbounded — *"If absent, the value is assumed
to be infinity, in which case the current presentation resumes only
when the alternative presentation terminates"* (DASH §5.16.5.2). The
narrowing restricts which documents conform and changes no construct's
semantics, which is what a profile-style restriction does (DASH §8.1). It is
recorded here so that a reader who finds the unbounded default in the
base specification knows it was excluded on purpose.

A declared cap of zero means the opportunity does not fire, which is
the base specification's own rule: *"If the value of `@maxDuration` is
zero, the event is not executed"* (DASH §5.16.5.2). A zero cap is not a very
short slot.

**4.3.3 Draw allowed-layout names from the closed set.** Each token in
a slot's `@allowedLayouts` is one of the tokens of §3.2, each of which
maps one-to-one to an IAB-defined ad type or visual placement. For a
pause-trigger window the Publisher names a surface — `pause-fullscreen`,
`pause-partial`, or both.

**4.3.4 Author one event stream per family per Period.** All the
opportunity windows of one family that share a `<Period>` are authored
as `<Event>` entries inside a **single** `<EventStream>`. The base
specification admits at most one event stream per Period for a given
scheme: *"A Period shall contain at most one EventStream element with
the same value of the @schemeIdUri attribute and the value of the
@value attribute, i.e. all Events of one type shall be clustered in one
Event Stream"* (DASH §5.10.2.1).

**4.3.5 Declare a resolution-timing offset that leaves room.** The
Publisher declares `@earliestResolutionTimeOffset` on each slot with a
value wide enough for the APS to answer before the opportunity becomes
current. Declaring it explicitly is what makes the value unambiguous:
the base specification carries the 60-second default in the prose of
DASH Table 63 and not in the XML schema of DASH §5.16.6.

**4.3.6 Declare the fallback chain where continuity matters.** A
Publisher that wants an unfilled or unreachable opportunity retried
declares a second window of the same family overlapping the first. The
overlap itself is the declaration; no attribute names the chain.

**4.3.7 Bind each window with its own declarations.** A window in a
fallback chain carries its own `@allowedLayouts` and its own
`@maxDuration`, and the Player binds the candidates that window serves
with those values (§4.6.9).

**4.3.8 Declare the pause metric where pause windows exist.** Content
carrying pause-trigger windows requests the `PlayList` metric through
the base specification's `Metrics` element (§5.9). Collection is
triggered by the service provider and not by the Player — *"The trigger
mechanism is based on the Metrics element in the MPD"* (DASH §5.9.1) — so
without the declaration there is a derivable quantity that nothing
obliges anyone to collect.

**4.3.9 Author the document so that removal leaves it valid.** Every
construct this specification introduces is removed from the manifest by
a client that does not implement it, and what remains is a valid,
conforming document. This is the base specification's own authoring
obligation: *"the MPD shall be authored such that, after XML attributes
or elements in the other namespaces than the DASH namespace are
removed, the result is a valid XML document formatted according to that
schema and that conforms to this document"* (DASH §5.2.1). A Publisher who
wants a Player that predates this specification to see something in
place of a non-linear opportunity authors that something out of
baseline constructs, as a sibling rather than nested inside an
extension element (§4.7.4).

### 4.4 ADS obligations

The ADS is outside the Player-visible interface: nothing it emits is
checked by this specification, and its output reaches the Player only
through the APS's resolution document. Two obligations are stated
because they are the ones a conformance check might wrongly impose on
it.

**4.4.1 The ADS decides, and emits a decision document.** It selects
which ads serve an opportunity, how many and in what order, and emits
them in its own format. It performs no conversion into a DASH-native
shape.

**4.4.2 The ADS owns the tracking schedule.** Which beacons fire, and
at which points relative to the ad's presentation, are the ADS's
declaration. This specification defines the carrier and the timebase
and prescribes no fraction, granularity or beacon count.

**4.4.3 The slot cap is not the ADS's to respect.** A conformance
check on an ADS passes even when the cumulative duration of the
candidates it returned exceeds the slot cap. The cap is enforced by the
Player (§4.6.4).

**4.4.4 A device-capability view is optional.** Producing candidates
requires no device-class matrix and no per-Player capability view at
the ADS. An implementation that holds one is equally conformant.

**4.4.5 No-fill is a decision.** An opportunity for which the ADS
selects no ads is answered, and the APS expresses that answer as a
document (§4.5.7). It is not a failure of the ADS.

### 4.5 APS obligations

The APS is the only non-Player actor whose output this specification
checks. Every obligation below is checked against the resolution
document alone, which is the one artefact on the path to the Player
that this specification defines.

**4.5.1 Answer the resolution request with a resolution document.**
The APS returns HTTP `200` with a body that parses and validates: a
`ListMPD` for a linear slot (§5.2.1), an Overlay Resolution Document
for an overlay or pause slot (§5.2.2).

**4.5.2 Answer the slot that asked.** The document the APS returns
belongs to the family of the slot that requested it.

**4.5.3 Carry the presentation options as an ordered list.** Each
candidate carries one or more presentation options as an ordered list
whose document order is the preference order. How many a candidate
carries is the APS's decision: no maximum, and no minimum beyond one.

Carrying several is the form this specification asks for, because a
candidate with several resolves on devices neither the ADS nor the APS
knows anything about. Carrying exactly one is equally admissible: the
suitability call then sits with the APS, or with the ADS that returned
a single option to it, and the Player-visible interface is identical
either way.

**4.5.4 Keep the ad-type vocabulary inside the closed set.** Every
presentation option's `@layout` is a token of §3.2, and every creative
carries a media type inside the admissible set of §3.3.

**4.5.5 Carry non-audiovisual creatives on a conformant carrier.** The
URL of an `image` or `html` creative travels on the carrier of §5.3.2.
Video creatives travel through `<ImportedMPD>` into a sub-MPD bound by
the base specification to the Single-Period Static profile.

**4.5.6 Carry the tracking schedule the ADS declared, on the callback
scheme.** Beacons are `<Event>` entries inside an `<EventStream>` of
scheme `urn:mpeg:dash:event:callback:2015`, with presentation times on
the ad's own presentation timeline (§5.5). The APS transcribes the
schedule; it does not invent one.

Whether the transcription is faithful — that no beacon was added,
dropped or reordered — is part of the contract the APS and the ADS
maintain directly. The ADS declares the schedule and receives the
beacons, so it is in a position to enforce that fidelity; the
resolution document is not, because it does not show what was
declared.

**4.5.7 Express an unsold opportunity as a document.** An opportunity
that resolved with no ads is answered with a well-formed, complete
resolution document carrying no candidates (§5.2.3), served with `200`
and a body.

**4.5.8 Carry a ClickThrough in the normative carrier.** When a
candidate carries a ClickThrough, its URL and any click-tracking URLs
accompanying it travel together in the carrier of §5.6. Whether a
ClickThrough has any click-tracking at all is the advertiser's
decision. Whether a ClickThrough the ADS declared reaches the document
at all is, like beacon fidelity, an APS-to-ADS matter.

**4.5.9 Answer without any capability parameter.** The APS produces
candidates for a resolution request that carries none of the reserved
capability parameters of §5.8.2. An APS that required one in order to
answer would make the Player's freedom to omit them unattainable. An
absent parameter means its value is **undetermined**, never that the
device lacks the capability.

**4.5.10 Declare the pause-exhaustion behaviour.** A resolution
document for a pause slot declares which of `repeat`, `request-again`
and `stop` applies when the candidates run out while the viewer is
still paused (§5.2.2.3). Absent the declaration the Player applies
`stop`.

**4.5.11 Reference media that stays reachable.** The ad media a
candidate points at is reachable for the duration of the slot.

### 4.6 Player obligations

The Player is the enforcer. Every obligation below is a runtime
obligation.

**4.6.1 Keep the primary content playing.** Through every condition in
this chapter and in §8.1 the Player keeps primary-content playback
uninterrupted on its own timeline: no freeze, no blank frame and no
error surface unless the application explicitly asked for one. When
resolving or rendering an accepted ad fails at runtime — a decode
error, a malformed candidate, a mid-ad network loss — the Player aborts
that ad and continues the primary content.

**4.6.2 Resolve the slot at or after the Earliest Resolution Time.**
When an opportunity becomes current the Player issues the resolution
request against the slot's `@uri`, at an instant at or after the ERT
and at or before the opportunity's presentation time. For a
pause-trigger window the Player issues the request when a viewer pause
begins inside the window; a pause that begins outside every such window
produces no request.

**4.6.3 Validate every candidate against the window that served it.**
Before rendering anything from a candidate, the Player checks each
presentation option against (a) what its device can satisfy and (b) the
`@allowedLayouts` of the window that served the candidate. Only an
option that satisfies both is rendered.

**4.6.4 Enforce the slot cap.** What the cap bounds differs by family,
because the base specification makes it so:

| Family and operation | What `@maxDuration` bounds |
|---|---|
| Linear replacement | **Until when.** With `@clip` at its default `true` the alternative presentation *"shall terminate at the latest at time PRT + APDmax"* (DASH Table 62) — the end the Publisher scheduled, whatever time the event actually fired, so a late start shortens the ad rather than moving the end. With `@clip="false"` it terminates at `PRTA + APDmax` and the slot ends later than scheduled. |
| Linear insertion | **How long.** Insertion stops the primary timeline and resumes it where it paused, so there is no scheduled end to preserve and `@clip` does not exist on the event. |
| Overlay | **How long**, against the cumulative duration of the forms the slot presents. |
| Pause | **Nothing.** A pause slot's duration is set by the viewer (§4.6.10). `@maxDuration` on a pause-trigger window bounds the display duration of a single pause ad before automatic dismissal. |

The asymmetry is not an exception granted to one construct: replacement
runs against a timeline that keeps moving underneath it and insertion
stops that timeline, so a cap meaning the same thing in both would be
wrong in one.

Where the cap bounds cumulative duration the Player stops rendering
once the cumulative duration would exceed it, **even when the stop
falls mid-ad**, and it enforces against **actual rendered length**
rather than declared length. The Player MAY additionally drop a
candidate before playback when its declared duration alone would push
the cumulative duration past the cap. In short: drop-before-play on
declared duration is permitted, trim-during-play on actual length is
required.

The cap and a candidate's duration are stated in different timebases —
the cap in units of the parent `<EventStream>@timescale`, a candidate's
duration as an ISO 8601 `xs:duration`. The Player converts the
candidate's duration into the cap's timescale before comparing, rounding
the converted value **up** to the next whole unit. A candidate whose
converted duration equals the cap exactly is admitted.

Cap arithmetic runs on the presentation timeline, so an interval during
which that timeline does not advance does not accrue against the cap: a
form suspended while the viewer is paused resumes with the remaining cap
it had when it was suspended.

A slot declaration carrying no `@maxDuration` is not a slot this
specification defines (§4.3.2). The Player presents no ad from such a
slot and continues with the primary content. Reading the absence as the
base specification's unbounded default would make cap enforcement inert
for exactly the slots whose declaration is defective.

> **This position diverges from the base specification and is open.**
> The base specification treats an absent maximum as infinity. What is
> being weighed is which failure is worse: a Publisher who omits the
> attribute sells nothing from that slot and may take a while to notice,
> against an advertisement that can run for as long as it likes. A
> reader should not take this rule as settled.

**4.6.5 Walk the presentation options in document order.** For an
accepted candidate the Player evaluates the options in document order
and renders the **first** whose form and layout it can satisfy on its
device and whose layout the window admits. An option that fails either
check is passed over and the Player moves to the next option in
document order. The Player renders no form its device cannot render.

**4.6.6 Fall through candidate by candidate.** A candidate with no
satisfiable option is skipped and the Player advances to the next
candidate in the resolution document. Only once every candidate is
exhausted does the Player continue with the primary content. A
candidate skipped for want of a satisfiable option does not advance the
Player to the next window: a document carrying candidates is not a
failed execution.

**4.6.7 Honour the document's order, and present one form at a time.**
The Player presents the candidates in the order the resolution document
declares. It MAY drop a candidate that has no satisfiable option or
whose declared duration would overrun the cap; the candidates that
survive are presented in the order the document declared them, without
reordering, deduplication or rearrangement.

At any instant at most **one** non-linear form is active on the screen.
Sequenced forms — one ending, the next beginning — are in scope; two
forms on screen at the same instant are not. The bound exists so that
the device never needs more than the primary content plus one ad form's
decoder concurrently: two concurrent video overlays would demand three
decoders, and many target devices support two.

Within a non-linear slot, candidates are presented one after another in
declared order, each starting when the previous ends, and the cap is
enforced against the cumulative duration of that sequence. Each
candidate contributes the single presentation option the Player selected
for it, so the sequence is a sequence of candidates and the alternatives
inside a candidate are not part of it.

**4.6.8 Treat an attempt that produced no ad as a failed execution.**
When windows of one family overlap in time, the Player selects the
first (§4.6.9) and attempts to resolve it. An attempt **on a window**
that produces no ad is a **failed execution**, and on a failed
execution the Player attempts the next overlapping window of the same
family.

This is the base specification's rule. DASH §5.16.2.2.5, step 2: *"If
execution fails, steps a-c above are repeated for next events in QE,
until: — Execution succeeds, or — PRT of the topmost event in the queue
is in the future (i.e. PRT > PHP), or — The queue is empty."* Each way
an attempt can fail maps to a condition DASH §5.16.2.2.6 lists, and the
Player treats all four alike:

- the APS does not respond, or the request fails at the transport level
  — *"Alternative MPD is unavailable"*;
- the response carries a final HTTP status other than `200` — the same
  condition: nothing was obtained;
- the response carries `200` whose body is not a resolution document
  the Player can parse — *"Alternative MPD is … invalid"*;
- the response carries `200` with a well-formed resolution document
  that **carries no candidates** — *"Alternative MPD is a List MPD, and
  merge process resulted in no available media"*.

When every overlapping window of the family has been attempted and none
produced an ad, the Player continues with the primary content
uninterrupted. Where the Publisher declared no fallback window at all,
that is the outcome after the single attempt.

An empty resolution is therefore **on** the chain and not the end of
it. The reason is behavioural equivalence: the base specification puts
an unreachable APS and an unsold opportunity under one heading, and a
Player implementing this specification and a Player implementing the
base specification should not diverge on the same manifest. For the
linear family the rule is adopted unchanged; for the non-linear
families the base specification's execution model does not reach — it
is built on Alternative MPD events, which overlay and pause-trigger
windows are not — so this specification **extends** the same rule to
them, so that one behaviour governs every family.

An empty resolution does not **consume** the opportunity. The base
specification counts executions rather than attempts: `E.c` is
*"Execution counter (number of times alternative MPD playback
successfully started)"* (DASH §5.16.2.2.2), and NOTE 3 of DASH §5.16.2.2.6 states
that *"The counter E.c has not been incremented due to the failure,
consequently if E.c = 0 the event can still be executed in the future
even if the value of @executeOnce is \"true\"."* A slot that resolved to
no ads leaves the opportunity executable.

A resolution document whose **family does not match** the slot that
requested it is a failure to resolve, and the Player continues down the
chain. It cannot fill this slot whatever it contains, because its
candidates are of a kind this slot does not admit.

**4.6.9 Order overlapping windows by presentation time, oldest first.**
Where two windows carry the same presentation time, the Player takes
them in the order they appear inside the `<EventStream>`.

For the linear family this is the base specification's own rule: the
execution queue is *"a priority queue of references to a subset of
events in table T, ordered by the presentation time PRT"* (DASH §5.16.2.2.2),
processed *"in its priority order (from oldest PRT to the most recent)"*
(DASH §5.16.2.2.5). It is **not** document order: document order governs when
an event is dispatched to the application (DASH §5.10.2.1), an earlier and
separate step. For the non-linear families the base specification's
queue does not reach, and this specification extends the same ordering
to them. The tie-break by document position is this specification's:
the base specification's queue does not resolve equal presentation
times, and document position is what remains once presentation time has
stopped separating them.

Each window in a chain binds the candidates it serves with **its own**
allowed layouts and its own cap. A window does not inherit the
declarations of the window it stands in for.

**4.6.10 Treat a pause window as bounding where, not how long.** A
pause-trigger window declares a region of the primary timeline. A pause
beginning inside it triggers the resolution request; the window
schedules no presentation and predicts none. How long the resulting slot
lasts is set entirely by the viewer and is unknowable when the document
is authored, so the Publisher-declared cap bounds the display duration
of one pause ad and not the slot.

A pause ad exists only while playback is paused. On the pause-to-play
transition the Player removes any rendered pause-ad form from the screen
within one rendering frame and stops firing beacons scheduled for it;
beacons scheduled at relative times after the transition fall outside
the pause ad's active window.

A pause ad MAY be presented **fullscreen**, occupying the whole screen
surface, or as a **partial overlay** composited over the paused primary
frame, according to which layout token the selected option carries.
When it is fullscreen the Player MAY release the resources held by the
primary content and by any pre-existing overlay in order to present a
fullscreen video, image or web page. When it is partial, the paused
primary frame remains visible underneath it.

**4.6.11 Apply the declared behaviour when pause candidates run out.**
Because a pause slot has no declared duration, the candidates may be
exhausted while the viewer is still paused. The Player applies the
behaviour the resolution document declares:

| Declared value | Player behaviour |
|---|---|
| `repeat` | Present the sequence again from the start, for as long as the pause lasts. |
| `request-again` | Request a new resolution document for the same pause. |
| `stop` | Present no further ad; the paused primary frame is shown. |

Absent a declaration the Player applies `stop`, which is what the
viewer would see if the mechanism did not exist and what every Player
can perform. Under `request-again` a resolution document carrying no
candidates is treated as `stop` for the remainder of that pause. The
candidate-level fall-through of §4.6.6 does not apply here, because the
primary content is paused.

When the viewer resumes, the Player returns to the primary content
immediately, whether or not an ad is mid-presentation.

**4.6.12 Honour a once-per-session pause window.** On a pause-trigger
window declared `@executeOnce="true"` the Player presents at most one
pause ad for that window for the duration of the session, and a later
qualifying pause inside the same window leaves the primary content
uninterrupted. The window is consumed when a pause ad **begins
rendering**, not when the pause occurs: a pause that resolves to no
renderable candidate leaves the window available. This is the base
specification's own counter rule with the render event substituted for
the playhead event, and it is the pause family's counterpart of the
single-execution bound the base specification gives a timeline event.

**4.6.13 Give a pause ad priority over an overlay and over a linear
ad.** While the viewer is paused inside a pause-trigger window, the
pause ad is the only ad surface visible:

- An active overlay is **suspended** for the duration of the pause and
  restored on resume if its own window is still open; where the overlay
  window expired during the pause, the Player leaves the overlay
  surface clear on resume.
- A linear ad occupying the screen is **suspended** and resumed from
  where it stopped when the viewer resumes.

The priority holds whatever the pause ad's presentation surface, which
is what keeps the one-active-form bound of §4.6.7 intact: a partial
pause ad does not put two forms on screen. This specification carries no
construct that lets the Publisher, the ADS or the APS invert it.

**4.6.14 Render at the primary content's speed.** Every ad form,
linear or non-linear, is rendered at the speed the primary content is
playing at the moment the ad is presented; the Player does not force an
ad to 1× while the primary content runs at another speed. A form's
declared duration is a value on the **presentation timeline** for every
form, including `image` and `html`, which have no intrinsic media. The
Player derives the wall-clock on-screen length as
`duration / playback_speed` — a 10-second form at 2× is on screen for
five seconds — while cap enforcement (§4.6.4) and beacon scheduling
(§4.6.15) operate on the presentation-timeline duration, which stays the
single canonical value.

**4.6.15 Execute the tracking schedule the document carries.** For an
accepted candidate the Player fires each beacon at its scheduled
relative time, preserving the ADS's authority over the schedule. Where
the cap trims the ad before a scheduled beacon's time, the Player stops
firing the remaining beacons at the trim boundary.

De-duplication is scoped to **the candidate** that carries the beacons:
within a candidate, beacons sharing an `@id`, or carrying the same URL
at the same presentation time, fire once. Two beacons carrying the same
`@id` in two different candidates of one resolution document are two
distinct beacons and the Player fires both. Where the beacon carrier
sits inside a candidate rather than in a `<Period>`, its presentation
times resolve against **that candidate's own presentation**.

A beacon failure — transport error, timeout, non-2xx — leaves the ad
and the primary content unaffected and never reaches the viewer.

**4.6.16 Fire the click and its tracking on activation.** A Player
conformant to this specification reads the ClickThrough URL from the
carrier of §5.6 and, when the viewer activates the ClickThrough, opens
or hands off the destination and fires each accompanying click-tracking
URL once.

**4.6.17 Freeze presentation time for a pause ad in live content.** In
live content, while the viewer is paused inside a pause-trigger window,
the Player keeps its presentation time frozen inside that window for the
duration of the pause, even though the live edge keeps advancing in
wall-clock time: the window is anchored to the Player's frozen
presentation time rather than to the advancing live timeline, so the
pause ad stays admissible until the viewer resumes. A decision to resume
at the live edge is a Player action occurring **after** the resume from
pause, outside the pause-ad window.

> **The base specification bounds this, and the bound applies.** The
> drift a pause accumulates against a live presentation is limited by
> the time-shift buffer: *"In case of live main media presentation, this
> involves clipping RT to the timeshift buffer (i.e. the time interval
> between TSBS and PHPLE)"* (DASH §5.16.2.2.5, step 1a), and DASH Table 62 states
> the consequence for the resumption point — *"if RT is in the past, the
> playback shall start from the oldest available media segment (the edge
> of the timeshift buffer)"* — with NOTE 2 naming the cause as a user
> pausing. Where the pause outlives `MPD@timeShiftBufferDepth`, the
> freeze ends with the buffer: the Player dismisses the pause ad as it
> does on any resume (§4.6.10), and the resumption position is the one
> the base specification prescribes. The obligation above is scoped by
> that bound rather than promising past it.

**4.6.18 Derive the paused interval from the base specification's
metric.** A Player that reports metrics derives the paused interval
from the `PlayList` entries as §5.9 describes, and counts no playback
period that stopped on `Rebuffering` as a pause opportunity.

**4.6.19 Compose the layouts as declared.** For an L-shape the Player
composites the two elements — the full-frame ad creative in the
background and the shrunk primary content on top of it — with the ad
creative covering the whole frame. For a side-by-side / double box it
composites the shrunk primary content and the ad as the two boxes;
where the advertiser supplied a background element it places it in the
uncovered bands, and where none was supplied the uncovered region
renders as black.

**4.6.20 Skip a candidate whose carrier is outside the admissible
set.** A creative whose media type falls outside §3.3 signals a
non-conformant upstream party. The Player MAY skip such a candidate and
fall through as in §4.6.6, and it renders no form its device cannot
render in any case.

**4.6.21 Ignore what it does not implement.** An event scheme URI, an
extension element or a foreign namespace the Player does not implement
is ignored together with its whole subtree, and the primary content
continues uninterrupted.

**4.6.22 Attach capability parameters at its own discretion.** Which of
the reserved parameters of §5.8.2 travel on a resolution request is the
Player's runtime decision. A parameter whose value the Player does not
have, or does not disclose, is **omitted entirely** rather than sent
empty; a parameter the Player attaches that is not one of the reserved
names carries a vendor-specific prefix, so that reserved names added in
a later edition stay free.

### 4.7 Extension points and backward compatibility

A Player that predates this specification is outside its obligations
(§4.1). What §4.7 fixes is that such a Player ignores every construct
introduced here cleanly, without crashing and without a visible
artefact, and keeps playing the primary content.

**4.7.1 The extension points used.** Every construct this
specification introduces is expressed through one of three extension
points of the base specification:

| Extension point | Clause | Used for |
|---|---|---|
| Foreign-namespace open content | DASH §5.2.1 | Every element and attribute in `urn:svta:dash:sgai:2026` |
| Application-level event streams | DASH §5.10 | The opportunity declarations, through a scheme URI of our own on a baseline `<EventStream>` |
| Vendor descriptor schemes | DASH §5.8.4.8, DASH §5.8.4.9 | Weighed for each carrier and not selected; see §5.3.2 |

Foreign-namespace open content is the base specification's normative
extension point for new XML: the schema declares
`<xs:any namespace="##other" processContents="lax"/>` on the containers
this specification places constructs in, and DASH §5.2.1 carries the
authoring obligation that removal leaves a valid document. No new
profile URI is needed for the construction to be conformant.

**4.7.2 The media axis is closed, and that is why non-audiovisual
creatives ride elsewhere.** Two independent facts close it. Any
document reached through `<ImportedMPD>` is bound to the Single-Period
Static profile — *"MPDs referenced in the ImportedMPD element shall be
restricted to the constraints of a single period profile as defined in
8.15"* (DASH §5.3.2.6.1) — which inherits DASH §7.3, where *"The @mimeType
attribute of each Representation shall be provided according to IETF
RFC 4337"* (DASH §7.3.1). And a regular Period inside a `ListMPD` inherits
the List profile, itself *"an extension of the ISO-BMFF CMAF Profile"*
(DASH §8.14), so the same restriction reaches an inline Adaptation Set
there; a per-Adaptation-Set `@profiles` cannot escape it, because it
must be a subset of the MPD-level value. Separately, the base
specification defines the carriage of a still image or an HTML document
as a Representation nowhere at all. There is nothing to relax on the
media axis; there is something absent from it.

A further constraint closes the obvious workaround: at least one
Adaptation Set is required in each Period *"unless the value of the
@duration attribute of the Period is set to zero"* (DASH §5.3.2.2, DASH Table 4),
so a Period that carries only events and no media is not a legal
carrier at non-zero duration.

Wrapping a non-MP4 payload in an `application/mp4` Representation to
satisfy the registry is not admissible under this specification: the
wrapper adds no segment-delivery semantics for the underlying format,
which DASH §8.1 makes an interoperability-point exercise with authoring
rules, conformance criteria and a published URI attached.

**4.7.3 Where a descriptor or an extension element may sit.** The
placement facts this specification's carrier choices rest on, read from
the base schema:

| Host element | `EssentialProperty` | `SupplementalProperty` | Foreign-namespace child elements | Foreign-namespace attributes |
|---|---|---|---|---|
| `MPD` | yes | yes | yes | yes |
| `Period` | — | yes | yes | yes |
| `AdaptationSet`, `Representation`, `SubRepresentation` | yes | yes | yes | yes |
| `EventStream` | yes | yes | yes | — |
| `Event` | yes | yes | yes | yes |
| `InsertPresentation`, `ReplacePresentation` | — | yes | yes | yes |
| `ImportedMPD` | — | — | **no** | yes |

Two consequences matter. First, a descriptor or an extension element
hosted on an `<Event>`, an `<EventStream>` or an alternative-MPD event
element never touches `Representation@mimeType` and therefore inherits
**no** media-type constraint to escape: the descriptor axis is wider
than the media axis, and a carrier choice made as though the two
coincided would be made against a constraint that is not there.
Second, `<ImportedMPD>` is the one placement that is genuinely closed
to an element: its type is declared as simple content extending
`xs:anyURI` with `<xs:anyAttribute namespace="##other"
processContents="lax"/>` and no `xs:any`, so a foreign-namespace
**attribute** may hang off it and a foreign-namespace **child element**
may not.

`<Period>` admits `SupplementalProperty` and not `EssentialProperty`,
which the table records because a reader is likely to assume the two
travel together.

**4.7.4 Which descriptor, when one is used.** The two vendor
descriptor elements differ in exactly the respect that decides what an
extension costs a client that does not recognise the scheme:

> DASH §5.8.4.8, NOTE 1: *"If the scheme or the value for this descriptor is
> not recognized, the DASH Client is expected to ignore **the parent
> element that contains the descriptor**."*
>
> DASH §5.8.4.9, NOTE: *"If the scheme or the value for this descriptor is
> not recognized, the DASH Client is expected to ignore **the
> descriptor**."*

`EssentialProperty` is the correct choice when presenting the parent
without understanding the descriptor would produce an incorrect result:
better for an old client to omit the element than to render it wrongly.
`SupplementalProperty` is the correct choice everywhere else. Neither
is wrong, and classifying a construct as using "a descriptor" without
saying which states nothing auditable.

One consequence follows from this specification's own governing
invariant rather than from the base specification: on anything in the
primary content path, dropping the parent would break primary-content
playback, so `EssentialProperty` is unavailable there.

**4.7.5 A baseline element nested inside an extension element carries
no legacy guarantee.** DASH §5.2.1 defines removal **by namespace** and
states it as an obligation on the author; removing an element removes
what it contains. So a baseline child that a client predating this
specification is expected to process is authored at a baseline
position, as a **sibling** of an extension element; one wrapped
**inside** an extension element is authored for clients that implement
the namespace, and no legacy behaviour may be assumed for it. This
specification uses both placements deliberately, and each construct
below says which.

**4.7.6 Per-construct compatibility audit.** Every construct this
specification introduces is classified here: where it sits, which
extension point governs it, what a client that does not implement this
specification does with it, and whether removing it leaves a document
that parses and plays.

| Construct | Placement | Extension point | Legacy behaviour | Removal leaves a valid document |
|---|---|---|---|---|
| `<svta:OverlayPresentation>` | Child of `<Event>` in an SGAI `<EventStream>` | DASH §5.10 scheme + DASH §5.2.1 | The whole `<EventStream>` is skipped by the per-scheme rule; the element is discarded with its subtree | yes |
| `<svta:PauseAdPresentation>` | Child of `<Event>` in an SGAI `<EventStream>` | DASH §5.10 scheme + DASH §5.2.1 | As above; a viewer pause produces no ad and no side effect | yes |
| `<svta:OverlayList>` | Child of `<Period>` in a resolution document | DASH §5.2.1 | Discarded with its subtree, leaving one zero-duration Period | yes |
| `<svta:Candidate>` | Child of `<svta:OverlayList>` | DASH §5.2.1 | Discarded with the parent subtree | yes |
| `<svta:RenderableAsset>` | Child of `<svta:Candidate>` | DASH §5.2.1 | Discarded with the parent subtree | yes |
| `<svta:BackgroundElement>` | Child of `<svta:RenderableAsset>` | DASH §5.2.1 | Discarded with the parent subtree | yes |
| `<svta:Click>`, `<svta:ClickTracking>` | Child of `<svta:Candidate>`; on a linear slot, of the `ListMPD` `<Period>` | DASH §5.2.1 | Discarded; the ad renders and no click fires | yes |
| `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>`, `<svta:UniversalAdId>` | Children of `<svta:Candidate>` | DASH §5.2.1 | Discarded; nothing in the presentation depends on them | yes |
| `<ImportedMPD>` inside `<svta:RenderableAsset>` | Baseline element inside an extension parent | DASH §5.2.1 with §4.7.5 | Discarded with the parent, which is the intent: a legacy Player has no slot to play the creative in | yes |
| `urn:svta:dash:request:sgai-resolution:2026` in `@includeInRequests` | Token in a baseline attribute | DASH Table I.4 `<URN / tag URI>` row | Dropped as an unknown URI by the base specification's own rule | yes |
| Reserved capability parameters | Query parameters on the resolution request | Not an MPD construct | Never emitted by a Player that does not implement this specification | not applicable |

**4.7.7 What a legacy Player shows instead, and who decides.** The
invariant this audit asserts is that the construct is skipped silently.
What the viewer sees **around** the skipped construct is
content-dependent and is the Publisher's authoring choice. For live
content the primary content continues uninterrupted and the opportunity
is an expected loss on such Players. For on-demand content the
Publisher MAY author a baseline linear break alongside the non-linear
construct, in which case a Player that predates this specification
plays the break (Annex G).

**And the trade-off that choice carries is stated rather than
implied.** A baseline break authored at the same presentation time as
an overlay window is, to a Player that implements this specification,
the hybrid slot of §5.1.5: two independent slots at one presentation
time, both resolved, both composed. This specification carries no
construct that scopes a break to Players that predate it, so the
Publisher's two options are to author the break and accept that a
current Player composes both, or to author no break and accept the loss
on the older Players. Authoring the break at a different presentation
time does not change the arithmetic — it makes two linear slots, and a
current Player serves both.

**4.7.8 A declared profile does not certify these constructs.** For a
profile-conformance check the base specification modifies the MPD
first, and step 4 of that procedure removes *"All elements or
attributes that are either (i) in this document and explicitly excluded
by ProfA, or (ii) in an extension namespace and not explicitly included
by ProfA"* (DASH §8.1). A document that declares a profile URN and carries
SGAI constructs is therefore checked, for that profile, with the SGAI
constructs gone. That does not make the document non-conforming — what
remains is valid, which is the property §4.7.1 rests on — but it does
mean a declared profile cannot be the thing that certifies these
constructs. Only an interoperability point that *"explicitly included"*
them could, and DASH §8.1 puts the authoring rules, the conformance criteria
and the publication on the owner of that URI. This specification's
declared position is the first: a valid base document, plus constructs
that a Player conformant to this specification reads.

## 5. Syntax

This chapter defines the constructs an implementation authors and
reads. Every attribute block is presented as a table. Every new
construct states inline why an existing construct of the base
specification was not reused, and every deliberate decision not to
reuse a construct a reader might expect is recorded with it.

### 5.1 Ad opportunity declarations in the main MPD

A Publisher declares each ad opportunity as an `<Event>` inside an
`<EventStream>` in the main MPD. The `<EventStream>@schemeIdUri`
identifies the slot family; the `<Event>`'s scheme-specific child
element carries the slot's constraints.

| Slot family | `<EventStream>@schemeIdUri` | Child element of `<Event>` | Resolution document |
|---|---|---|---|
| Linear, insert | `urn:mpeg:dash:event:alternativeMPD:insert:2025` | `<InsertPresentation>` | `ListMPD` (§5.2.1) |
| Linear, replace | `urn:mpeg:dash:event:alternativeMPD:replace:2025` | `<ReplacePresentation>` | `ListMPD` (§5.2.1) |
| Overlay | `urn:svta:dash:event:sgai-overlay:2026` | `<svta:OverlayPresentation>` | Overlay Resolution Document (§5.2.2) |
| Pause | `urn:svta:dash:event:sgai-pause-trigger:2026` | `<svta:PauseAdPresentation>` | Overlay Resolution Document (§5.2.2) |

The `<Event>` carrier uses the baseline attributes of DASH §5.10 — `@id`,
`@presentationTime`, `@duration` — with the time base given by
`@timescale` on the parent `<EventStream>`. The scheme-specific child
element is the SGAI attribute carrier.

**Why the event stream, and not a container of our own.**
`<EventStream>` with `<Event>` is the base specification's authoring
vehicle for timeline-anchored signalling, and it is already open to
this specification twice over: `EventType` is declared `mixed="true"`
with `<xs:any namespace="##other" processContents="lax"/>` and
`<xs:anyAttribute namespace="##other" processContents="lax"/>`, and
DASH §5.10.2.1 states that *"the Event element may contain further XML
elements meaningful for a particular event scheme. These may be defined
in this document … or in some external namespace."* The per-scheme skip
rule supplies the other half of what a new construct needs: *"This
enables a DASH Client or the application to subscribe to an Event
Stream of interest and ignore Event Streams that are of no relevance or
interest"* (DASH §5.10.1). A container of our own would have re-derived both
and would have had to argue its own legacy semantics from scratch.

#### 5.1.1 `<InsertPresentation>` — linear insertion, inherited

Reused verbatim from DASH §5.16.3. The Publisher declares an `<Event>`
whose `@presentationTime` marks a point on the primary timeline at
which the alternative presentation is inserted **without consuming any
of the primary timeline**; when it ends, primary content resumes from
where it paused.

The element carries the attributes of `AlternativeMPDEventType`:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | yes | `xs:anyURI` | — | URL the Player resolves at or after the ERT. Resolves to the APS endpoint. |
| `@maxDuration` | optional in the base schema; **required under this specification** | `xs:unsignedLong` | `2251799813685247` in the schema, i.e. unbounded | The slot cap, in parent `<EventStream>@timescale` units. An alternative presentation running past it is terminated at the cap. A Publisher authoring under this specification declares a real value (§4.3.2). |
| `@earliestResolutionTimeOffset` | no | `xs:unsignedLong` | 60 s when absent, per DASH Table 63 | Offset subtracted from the event's `@presentationTime` to obtain the ERT, in `@timescale` units. |
| `@executeOnce` | no | `xs:boolean` | `false` | When `true`, the event executes at most once in the session. |
| `@noJump` | no | `xs:integer` | `0` | Baseline seek-interaction control: when non-zero, the playhead may not move from a point before the event's presentation time to a point past the end of its active period without executing the event. |
| `@skipAfter` | no | `xs:duration` | `PT0S` | Baseline skip control: the offset from the start of the alternative presentation after which the remainder may be skipped in response to a user action. |
| `@serviceDescriptionId` | no | `xs:unsignedInt` | — | The `@id` of a `ServiceDescription` applicable to this event and to the presentation it initiates. |

Children: `<SupplementalProperty>` (zero or more) and
foreign-namespace open content, both inherited from
`AlternativeMPDEventType`.

> **Unit and default note.** The 60-second default of
> `@earliestResolutionTimeOffset` is stated in the prose of DASH Table 63
> and carries no schema default in DASH §5.16.6. An implementation that
> needs the value to be unambiguous declares it explicitly, which
> §4.3.5 asks for in any case.

Constraint inherited unchanged: this event does not appear when
`MPD@type` is `dynamic`. It addresses an operation in which the
playhead can be stopped for an indefinite period, which is an on-demand
or pre-recorded operation. Live content uses `<ReplacePresentation>`.

Legacy behaviour: the baseline per-scheme skip rule of DASH §5.10 (§4.7.6).

#### 5.1.2 `<ReplacePresentation>` — linear replacement, inherited

Reused verbatim from DASH §5.16.4. The `@presentationTime` and `@duration`
of the declaring `<Event>` mark a span of the primary timeline that the
alternative presentation **replaces**. Primary media time keeps
advancing while the ad plays, and on completion the Player resumes at
the position `@returnOffset` determines.

`AlternativeMPDReplaceEventType` extends `AlternativeMPDEventType`, so
every attribute of §5.1.1 applies, plus:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@returnOffset` | no | `xs:unsignedLong` | — | Offset determining the playhead position at which primary content resumes after the alternative presentation. |
| `@clip` | no | `xs:boolean` | `true` | When `true`, the alternative presentation terminates at the latest at the scheduled end of the slot, so a late start shortens the ad rather than moving the end. When `false`, it terminates one cap-length after the actual start. The attribute carries no duration of its own. |
| `@startWithOffset` | no | `xs:boolean` | `false` | When `true`, a delayed alternative presentation skips into its own timeline by the elapsed delay, staying aligned with the wall clock. When `false`, it starts from its first frame. |

Every conditional restriction DASH §5.16.4 and DASH §5.16.5.2 place on these
attributes applies unchanged; the table restates names, types and
defaults only. The three attributes are exclusive to
`<ReplacePresentation>`; `<InsertPresentation>` carries none of them.

Legacy behaviour: as in §5.1.1.

#### 5.1.3 `<svta:OverlayPresentation>` — overlay window, new

Declares a non-linear overlay opportunity. The opportunity window is
the parent `<Event>`'s `@presentationTime` and `@duration`. The Player
resolves the slot's `@uri` at or after the ERT, validates the
candidates against the constraints below, and composites the chosen
form on or alongside the primary content, which keeps playing.

**Why a new construct.** The base specification's ad machinery is
substitutive by definition: *"An alternative Media Presentation is a
presentation that replaces the main Media Presentation at a certain
point on the media timeline for a duration of time"* (DASH §5.16.1), whether
inserted or replacing. Neither composes anything; both swap. Three
constructs elsewhere come close enough to be weighed, and each is
rejected for a stated reason:

- **The supplementary video descriptor**
  (`urn:mpeg:dash:supv:2022`, DASH §5.8.5.16) is the nearest miss, and it
  exists precisely to signal two video surfaces of different sizes in
  one experience: *"Supplementary video services (sometimes referred to
  as picture-in-picture services) offer the ability to include a video
  with a smaller spatial resolution within a video with a bigger
  spatial resolution."* It is rejected on four counts, none of them
  incidental. It is a `SupplementalProperty` at **Preselection** level
  describing two Adaptation Sets of the **same** presentation, authored
  together; a non-linear ad arrives at runtime in a separate document
  and is not a component of the primary presentation. It hands the
  composition back rather than specifying it: *"Potential manipulation
  of the stream and the composition of the main video and the
  supplementary video are out of the scope of the DASH client."* Its
  only payload is `SupVideoInfo@processingInfo`, a codec-level string
  whose *"syntax and sematic … are usually defined by the decoder
  specifications"* — it carries no layout token, no duration cap, no
  tracking, no click and no candidate ordering. And it admits no
  non-video surface at all, while two of the layouts of §3.2 require an
  image or an HTML surface. Rejecting it in writing rather than by
  silence is the point: a reader who finds it in the base specification
  is entitled to know it was considered.
- **The Spatial Relationship Description** (`urn:mpeg:dash:srd:2014`,
  DASH Annex H) positions encoded video tracks in a shared coordinate system
  for tiling and region-of-interest selection, and is confined to two
  elements: *"SRD information shall be contained exclusively in these
  two MPD elements"* (DASH §H.1). Reusing it would both misuse the construct
  and build the parallel layout system this specification declines to
  build (§1.2).
- **The non-linear playback scheme**
  (`urn:mpeg:dash:nonlinearplayback:2020`, DASH Annex L) is, despite the
  name, not about non-linear ads: *"This Annex provides Nonlinear
  Playback capabilities, to serve Interactive Storyline content"*
  (DASH §L.1), modelled as a graph in which the edges are Periods and the
  nodes carry decisions. It defines no overlay, no composition and no
  ad semantics. It is cited below as a **precedent** for a construct's
  shape, not reused as a carrier.

A new opportunity declaration is therefore unavoidable, and it is kept
minimal: an `<Event>` child element carrying attributes, nothing more.

##### 5.1.3.1 Attributes

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | yes | `xs:anyURI` | — | URL the Player resolves at or after the ERT. Resolves to the APS endpoint; the response conforms to §5.2.2. |
| `@maxDuration` | yes | `xs:unsignedLong` | — | The slot cap, in parent `<EventStream>@timescale` units, enforced against the cumulative rendered length of the forms this slot presents. Name, units and termination semantics are those of `@maxDuration` in DASH §5.16.5.2. |
| `@allowedLayouts` | yes | whitespace-separated token list | — | The layout tokens this slot admits, each drawn from §3.2. The Player matches a candidate option's `@layout` against this list by exact token. |
| `@earliestResolutionTimeOffset` | no | `xs:unsignedLong` | 60 s when absent | Offset subtracted from the event's `@presentationTime` to obtain the ERT, in `@timescale` units. Same name, type and semantics as on the linear events. |
| `@executeOnce` | no | `xs:boolean` | `false` | When `true`, the window yields at most one overlay presentation for the session. |
| `@serviceDescriptionId` | no | `xs:unsignedInt` | — | As in §5.1.1. Available on a non-linear slot for the same purpose, without a new construct. |

**Encoding note.** `@allowedLayouts` is a single attribute carrying a
whitespace-separated token list rather than a nested element with one
child per token, matching the encoding the base specification uses for
`@dependencyId` and the other attributes it types as
`StringVectorType`. The two attributes the base specification
comma-separates — `MPD@profiles` and `@codecs` — are both constrained to
IETF RFC 6381 productions, which is why they are not the model here.
The element form is warranted only when each item carries its own
attributes or children, which a layout token does not.

**On concurrency.** This specification declares no maximum-concurrency
attribute on the slot. At most one non-linear form is active at any
instant (§4.6.7), so an attribute whose only admissible value is `1`
would restate a rule the specification already fixes, and a value
disagreeing with it would be unenforceable.

##### 5.1.3.2 Children

None. Every slot constraint is carried as an attribute.

##### 5.1.3.3 Legacy behaviour

A Player that does not implement
`urn:svta:dash:event:sgai-overlay:2026` applies the baseline per-scheme
skip rule: the parent `<EventStream>` is skipped with every `<Event>`
it carries, and the foreign-namespace `<svta:OverlayPresentation>`
element is discarded with its subtree. Primary content continues
uninterrupted. Removing the whole `<EventStream>` leaves a valid MPD
that parses and plays, and no baseline element the legacy Player needs
is nested inside the SGAI element.

#### 5.1.4 `<svta:PauseAdPresentation>` — pause-trigger window, new

Declares a **pause-trigger window**: an interval of the primary
timeline during which a viewer pause permits a pause ad. Outside the
window, a pause permits none. The window is the parent `<Event>`'s
`@presentationTime` and `@duration`.

**Why a new construct, and why this shape.** Every event in the base
specification is scheduled against presentation time — *"Events are
timed, i.e. each event starts at a specific media presentation time and
may have a duration"* (DASH §5.10.1) — and a pause stops presentation time,
and with it the processing: *"Since there is no playhead-triggered
processing during the listen mode, processing always resumes at the
playhead position PHP = RT"* (DASH §5.16.2.2.5, NOTE). The pause is visible
to the base specification in four places and none of them is a trigger:
as client behaviour (*"The client may pause or stop a Media
Presentation. In this case, the client simply stops requesting Media
Segments or parts thereof"*, DASH §A.5), as a playhead condition (DASH §4.2), as
a report in the playout metric (DASH §D.4.6), and informatively as a speed
of zero in the dual-client message of DASH §A.14.2.

The shape follows from that asymmetry. What is declared on the timeline
is the **window of validity**, which a timeline-scheduled `<Event>`
expresses natively; the **trigger** is Player-side and fires on the
pause transition inside that window. The split is not novel in the base
specification: DASH Annex L anchors a window on the timeline — *"the
Event@presentationTime and Event@duration attributes are used to
indicate the start and the duration of the selection window"*
(DASH §L.3.4.2) — while resolving the viewer's decision off it, *"The DASH
Client signals the chosen edge to play after the end of the current by
firing a callback at the @contactURL of the respective Event"*
(DASH §L.3.3).

##### 5.1.4.1 Attributes

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@uri` | yes | `xs:anyURI` | — | URL the Player resolves to obtain the pause-ad resolution document (§5.2.2). |
| `@maxDuration` | yes | `xs:unsignedLong` | — | Maximum display duration of **one** pause ad before automatic dismissal, in parent `<EventStream>@timescale` units. It does not bound the pause slot, whose length the viewer sets (§4.6.10). Name, units and termination semantics are those of `@maxDuration` in DASH §5.16.5.2. |
| `@allowedLayouts` | yes | whitespace-separated token list | — | The pause surfaces this window admits: `pause-fullscreen`, `pause-partial`, or both. |
| `@earliestResolutionTimeOffset` | no | `xs:unsignedLong` | 60 s when absent | Offset subtracted from the event's `@presentationTime` to obtain the ERT. The Player MAY resolve speculatively at that time or lazily at the moment of pause (§8.5). |
| `@executeOnce` | no | `xs:boolean` | `false` | When `true`, the window yields at most one pause ad for the session; a later qualifying pause inside it leaves the primary content uninterrupted. The window is consumed when a pause ad begins rendering (§4.6.12). |

**Why `@executeOnce` carries the baseline name.** The capability is the
pause family's counterpart of the single-execution bound the base
specification gives a timeline event, and the naming rule of this
specification is to reuse a baseline identifier with its name, default
and semantics rather than mint a second one for the same concept. What
changes is only the trigger the counter observes: the base
specification increments when *"the alternative media presentation
triggered by an event successfully starts playing"* (DASH §5.16.2.2.6), and
here the render of a pause ad substitutes for the playhead event. A
reader who knows the baseline construct knows what this one does.

Stating the attribute is what makes the window's behaviour determinate.
Without it the capability is either inert on a pause window or caps it
at one pause ad, and those two readings differ by every pause after the
first.

##### 5.1.4.2 Legacy behaviour

A Player that does not implement
`urn:svta:dash:event:sgai-pause-trigger:2026` skips the `<EventStream>`
and its events, and a viewer pause produces no ad and no side effect.
The window is invisible to it.

#### 5.1.5 Hybrid slots — a linear slot with a concurrent overlay

A hybrid break is authored as **two events at the same
`@presentationTime`**: one carrying `<InsertPresentation>` or
`<ReplacePresentation>` for the take-over portion, and one carrying
`<svta:OverlayPresentation>` for the overlay composited on top of it.
They sit in different event streams, because they are different
schemes.

The two are independent at authoring time and at runtime. The Player
resolves the two `@uri` values separately, validates and selects from
each resolution document independently, and composes the chosen linear
ad with the chosen overlay during the same break. This specification
defines no construct that links the two portions: a Publisher wanting
the overlay restricted during a take-over expresses it through that
event's own `@allowedLayouts`, and a Publisher wanting no overlay
during a take-over declares no overlay event at that position.

#### 5.1.6 Overlapping windows of the same family

Two or more events of one family whose windows overlap in time form a
**fallback chain**: the first is the window to serve, the rest are
backups reached whenever an attempt produces no ad. The Player-side
rule is §4.6.8; no attribute declares the chain, because the overlap
itself is the declaration.

**Considered and not reused.** `BaseURL` alternatives with
`@serviceLocation` (DASH §5.6) offer alternative locations for the **same**
resource, and are the right tool for origin-level robustness on a
sub-MPD or a segment fetch rather than for chaining two different
opportunities. The MPD fallback scheme `urn:mpeg:dash:fallback:2016`
(DASH §5.11.3) chains whole presentations on an error that *"makes it
impossible to continue playback of the current Media Presentation"*;
its ordering rule is the same rule this specification applies — *"If
multiple URLs are provided, the content author expresses the
preferences of using one of those by the order with the first one
having the highest preference"* — and it is cited as the base
specification's own precedent for document-order-as-preference, but its
granularity is a whole presentation rather than an opportunity window.

### 5.2 Resolution documents

#### 5.2.1 Linear `ListMPD`

Reused from DASH §8.14. The APS answers a linear slot's resolution request
with an MPD whose `@type` is `list` and whose `@profiles` includes
`urn:mpeg:dash:profile:list:2024`. Each `<Period>` is one ad in the
break, played back-to-back in declared order: a `ListMPD` is a playlist
of ads the ADS already chose and ordered, not a candidate set the
Player selects from.

Two profile rules bound the document and are inherited unchanged: a
`ListMPD` carries no Alternative MPD events, and no XLink attributes at
any level. Remote resolution inside a `ListMPD` therefore goes through
`<ImportedMPD>` and nowhere else. The first rule has a consequence
worth stating: a resolution document cannot declare a nested ad
opportunity inside itself, so every overlay and pause window is
signalled from the main MPD.

##### 5.2.1.1 Period attributes

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@id` | yes | `xs:string` | — | Period identifier, unique within the document. |
| `@duration` | yes | `xs:duration` | — | Declared duration of this ad as an ISO 8601 duration. The Player uses it for drop-before-play cap evaluation (§4.6.4) without fetching the sub-MPD first. |

##### 5.2.1.2 Period children

A Period carries one `<ImportedMPD>` pointing at the ad's sub-MPD
(§5.4). The base specification also admits inline `<AdaptationSet>` /
`<Representation>` under a `ListMPD`-level Period — *"List MPDs may
contain one or more Linked Periods (see 5.3.2.6), however it may also
contain regular Periods"* (DASH §8.14, rule 4) — and that shape is permitted
here, inheriting the media-type constraint of §4.7.2. The
`<ImportedMPD>` shape is the one this specification uses in its
examples, because it keeps each creative's metadata sharded per ad.

##### 5.2.1.3 `<ImportedMPD>`

Reused verbatim from DASH §5.3.2.6. The imported MPD's URL is the element's
**text content**, not an attribute: its type extends `xs:anyURI`
through simple content.

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@earliestResolutionTimeOffset` | no | `xs:double` | `60.0` | Seconds before this Period's start at which the Player MAY pre-fetch the sub-MPD, smoothing CDN load. |

> **Unit note.** `@earliestResolutionTimeOffset` appears in two
> contexts with different unit bases, both inherited. On a slot event
> (§5.1.1 to §5.1.4) it is `xs:unsignedLong` in the parent
> `<EventStream>@timescale` units. On `<ImportedMPD>` it is
> `xs:double` in **seconds**. A reader determines the base from the
> parent element; authoring tools SHOULD surface the parent element
> alongside the value.

The element's type admits foreign-namespace **attributes** and no
foreign-namespace **child elements** (§4.7.3), so an extension that
needs to travel on an `<ImportedMPD>` travels as an attribute.

A Period carrying an `<ImportedMPD>` is a Linked Period and the
imported document is restricted to the Single-Period Static profile
(§5.4).

#### 5.2.2 Overlay Resolution Document — non-linear, new

The APS answers an overlay or pause slot's resolution request with an
Overlay Resolution Document: an MPD whose `@profiles` includes
`urn:svta:dash:profile:sgai-overlay-list:2026`, carrying the candidates
in a foreign-namespace `<svta:OverlayList>` element.

**Why this shape.** The `ListMPD` structure was the starting point and
most of it is reused: the document is an MPD, the candidate list keeps
declared order as the preference order, and video creatives are still
reached through `<ImportedMPD>` into an SPS sub-MPD. What the `ListMPD`
cannot express is the one construct the non-linear case needs — a
single candidate offering an ordered list of alternative presentation
options — because its Periods are a sequence to play rather than
alternatives to choose among (§5.3). The candidate list is therefore
carried in the extension namespace, inside a document that is otherwise
a conformant MPD.

**On the name.** "Overlay" in *Overlay Resolution Document*, in the
profile URI and in `<svta:OverlayList>` names the **non-linear family
as a whole** — overlay windows and pause-trigger windows alike. It is
not the `overlay` layout token of §3.2, which names one spatial
arrangement. A pause-ad document is an Overlay Resolution Document and
declares that profile URI.

##### 5.2.2.1 Document shape

The document is an `MPD` carrying a single `<Period>` whose `@duration`
is `PT0S` and whose only child is the foreign-namespace
`<svta:OverlayList>`.

The zero duration is load-bearing rather than cosmetic. At least one
`<AdaptationSet>` is required in each `<Period>` *"unless the value of
the @duration attribute of the Period is set to zero"* (DASH §5.3.2.2,
DASH Table 4), and an Overlay Resolution Document carries no Adaptation Set
at all: each candidate's media is reached through its own presentation
options, not through the enclosing Period. Declaring `PT0S` is what
makes the document conformant, and it also states the truth — the
enclosing Period presents nothing; it is the anchor the candidate list
hangs from.

`<Period>` admits foreign-namespace children through the open content
of DASH §5.2.1, so the placement is conformant, and a validator scanning
`<Period>` children for foreign-namespace elements finds the candidate
list under a canonical anchor.

A resolution document is a conforming **MPD used as a carrier** and not
itself a Media Presentation: it describes no media of its own. The
Media-Presentation conformance rule of DASH §8.1 — at least one
Representation in each Period of the profile-specific MPD — is
therefore not the ladder this document is measured against.

Skeleton:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T16:00:00Z">
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

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@profiles` | yes | comma-separated list of `xs:anyURI` | — | Includes `urn:svta:dash:profile:sgai-overlay-list:2026`. DASH §8.1 defines the value as a comma-separated list and forbids a comma inside a profile identifier. |
| `@type` | yes | enum (`static` \| `dynamic` \| `list`) | `static` | `static` on this document. DASH §5.3.1.4 also makes `list` available, conferring the static constraints and the absence of XLink without enrolling the document in the List profile; this specification declares `static` and takes neither, because the value's every other mention in the base specification binds it to Linked Periods and the alternative-MPD flow. |
| `@minBufferTime` | yes | `xs:duration` | — | Baseline MPD attribute. `PT0S` on this document, which buffers nothing itself. |
| `@mediaPresentationDuration` | yes | `xs:duration` | — | `PT0S`, consistent with the single zero-duration Period. The base specification makes this attribute conditional when the last Period declares a `@duration`; this profile declares it unconditionally, which adds a constraint rather than relaxing one. |
| `@publishTime` | yes | `xs:dateTime` | — | The instant the APS produced the document. |

##### 5.2.2.3 `<svta:OverlayList>`

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@onCandidatesExhausted` | no | enum (`repeat` \| `request-again` \| `stop`) | `stop` | What the Player does when the candidates run out while the viewer is still paused (§4.6.11). Inert on an overlay document, where the slot ends with its window. |

| Enum value | Description |
|---|---|
| `repeat` | Present the candidate sequence again from the start, for as long as the pause lasts. |
| `request-again` | Request a new resolution document for the same pause. A document carrying no candidates is then treated as `stop` for the remainder of the pause. |
| `stop` | Present no further ad; the paused primary frame is shown. |

| Child | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:Candidate>` | no | 0..n | The ads offered for the slot, in the order the ADS decided. Zero children is the empty resolution of §5.2.3. |

**Why the declaration belongs to the APS and not to the Publisher.**
The exhaustion behaviour is a property of the answer, not of the
opportunity: it says what to do with *these* candidates when they run
out. A Publisher-declared limit on how many documents may be served
would be answered by APS implementations returning defensively long
candidate lists, since a single response would be their only
opportunity — the constraint would produce the outcome it exists to
prevent. `stop` is the default because it is what the viewer would see
if the mechanism did not exist, and it is the behaviour every Player
can perform.

##### 5.2.2.4 `<svta:Candidate>`

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@id` | yes | `xs:string` | — | Candidate identifier, unique within the document. |
| `@duration` | yes | `xs:duration` | — | The candidate's declared duration on the presentation timeline, as an ISO 8601 duration. The Player uses it for drop-before-play cap evaluation (§4.6.4) and as the basis for the derived wall-clock on-screen length (§4.6.14). |

| Child | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:RenderableAsset>` | yes | 1..n | The candidate's presentation options as an ordered list. Document order is the preference order (§5.3.5). |
| `<EventStream>` of the callback scheme | no | 0..1 | The candidate's tracking schedule (§5.5). |
| `<svta:Click>` | no | 0..1 | The candidate's ClickThrough and its click-tracking (§5.6). |
| `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>`, `<svta:UniversalAdId>` | no | 0..1 each | Application-level metadata (§5.7). |

#### 5.2.3 The empty resolution document

An opportunity that resolved and produced **no ads** is expressed as a
resolution document carrying no candidates, served with HTTP `200` and
a body. It is not an error status, not a `204`, not a `404` and not a
document that fails to parse. The distinction is between *a document
that says nothing was sold* and *no document at all*.

What follows from it at the Player is §4.6.8: the attempt produced no
ad, so it is a failed execution and the next overlapping window of the
family is attempted; where there is none, the primary content
continues. Expressing it as a document rather than as an error is what
lets an unfilled opportunity be reported as unfilled, keeps the
APS-to-Player contract free of a status code that would mean two
different things, and leaves the distinction visible to anyone auditing
the exchange.

**Non-linear.** The document of §5.2.2 with an empty
`<svta:OverlayList>`:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T16:00:00Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList/>
  </Period>
</MPD>
```

**Linear.** A `ListMPD` carrying a single `<Period>` of zero duration
and no `<ImportedMPD>`:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT0S"
     publishTime="2026-09-17T16:00:00Z">
  <Period id="no-fill" duration="PT0S"/>
</MPD>
```

Both shapes are chosen against the same pair of schema constraints.
`<Period>` is declared `<xs:element name="Period" type="PeriodType"
maxOccurs="unbounded"/>` with an omitted `minOccurs`, which defaults to
`1`, so a resolution document carrying zero Periods does not validate;
and at least one Adaptation Set is required in each Period unless the
Period's `@duration` is zero, which is why the degenerate Period
declares `PT0S`. The answer therefore has the same shape for a linear
slot and a non-linear one: one Period of zero duration, carrying
nothing to present. Both are conforming MPDs used as carriers rather
than Media Presentations, so the per-Period Representation rule of DASH §8.1
does not reach them either.

### 5.3 `<svta:RenderableAsset>` — the presentation option

A `<svta:RenderableAsset>` is **one** renderable presentation option on
a candidate: a creative-carrier form paired with a layout. A candidate
carries its options as an ordered list of these elements.

**Why a new construct.** No construct in the base specification lets a
single ad candidate offer an ordered list of alternative presentations
and have the client render the first it can satisfy. Three constructs
express ordered preference and each is scoped elsewhere:

- **`Preselection`** (DASH §5.3.11) *"define user experiences that can be
  selected by the DASH Client"* and each *"encompasses a subset of
  media components such that the media components can be selected and
  combined into a complete experience"* — components combined into one
  jointly rendered experience rather than alternatives to choose
  between. Its `@preselectionComponents` is *"a white space separated
  list in processing order"*, and its `@order` selects conformance
  rules for segment tracks rather than preference.
- **`@selectionPriority`** (DASH §5.3.7.2) *"specifies the selection
  priority for the described data structures … In the absence of other
  information, higher numbers are the preferred selection over lower
  numbers"*, default `1`. It is a numeric hint on
  `RepresentationBaseType`, running in the **opposite** direction from
  document order, and explicitly conditional on there being no other
  information.
- **`urn:mpeg:dash:fallback:2016`** (DASH §5.11.3) states this
  specification's ordering rule almost verbatim, but at the granularity
  of whole MPD URLs on an MPD-level descriptor of which *"Each MPD may
  contain at most one"*, and triggered by an unrecoverable playout
  error rather than by a capability check.

Reusing any of the three would put an ad-level choice on a media-level
construct or invert the ordering convention. The option element is
therefore new, and it is kept minimal: three attributes and, for a
video form, one baseline child. The one thing this specification
**does** take from the base specification here is the convention:
document-order-as-preference is the base specification's own, as the
fallback scheme shows, so declining to introduce a ranking attribute is
consistency with it rather than a departure from it.

#### 5.3.1 Attributes

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@form` | yes | enum (`video` \| `image` \| `html`) | — | The creative-carrier form (§3.3). Value space in §5.3.2. |
| `@layout` | yes | token | — | The layout, drawn from the enumeration of §3.2. The Player matches it against the slot's `@allowedLayouts` by exact token. Value space in §5.3.3. |
| `@assetUrl` | conditional | `xs:anyURI` | — | The creative's URL when `@form` is `image` or `html`. Absent when `@form` is `video`, where the creative is reached through the `<ImportedMPD>` child (§5.3.4). |

This specification declares no priority or ranking attribute on the
option: document order is the preference order (§5.3.5), and a second
declaration of the same fact would be a value that could contradict
the first.

#### 5.3.2 Enum: `@form`

| Enum value | Description |
|---|---|
| `video` | ISO-BMFF video, reached through the `<ImportedMPD>` child of this element (§5.3.4). Representations inside the sub-MPD carry `video/mp4`, `audio/mp4` or `application/mp4`. |
| `image` | Still image at `@assetUrl`. Concrete media types: `image/jpeg`, `image/png`, `image/webp`. |
| `html` | HTML document at `@assetUrl`. Concrete media type: `text/html`. Inline `<script>` MAY appear and runs under the device's HTML capability contract; the script is not a separate carrier. |

**Why the non-audiovisual asset URL rides on this element.** The media
axis is closed to non-MP4 media types along the whole resolution path,
for the two independent reasons §4.7.2 gives. Four DASH-conformant
carriers remain, and this specification uses the first:

| Carrier | Clause | Weighed as |
|---|---|---|
| **(a)** Foreign-namespace open content: the URL as an attribute on a new element | DASH §5.2.1 | **Selected.** |
| (b) An application-level `<Event>` whose text content carries the payload | DASH §5.10 | Rejected: the asset URL is a one-fetch static value with no presentation time of its own, so the carrier's defining property — presentation-time alignment — buys nothing, and it would put the creative's address on a timeline it has no position on. |
| (c1) A `SupplementalProperty` whose `@value` carries the URL | DASH §5.8.4.9 | Rejected: see below. |
| (c2) An `EssentialProperty` whose `@value` carries the URL | DASH §5.8.4.8 | Rejected: see below, and its legacy cost is heavier still — a client that does not recognise the scheme drops the parent element. |

**Why neither descriptor.** The reason is *not* placement. A descriptor
hosted on an `<Event>`, an `<EventStream>` or an alternative-MPD event
element inherits no media-type constraint at all (§4.7.3), so the
descriptor axis is genuinely open here and a rejection resting on the
media-type registry would rest on a constraint that is not present.
The reason is what a descriptor can carry. `DescriptorType` offers one
scheme URI and one `@value` string, and a presentation option is three
inseparable facts — form, layout, and the creative that realises them —
plus, on one layout, a background element with a URL of its own.
Encoding that tuple into a single delimited `@value` would invent a
micro-syntax inside an attribute where an element with named attributes
says the same thing in the schema, and it would put the pieces of one
option in a place where nothing binds them to each other as an option.
The ordered list of §5.3.5 needs the option to be an element for the
same reason: order among elements is the preference order, whereas
order among descriptors on a host element carries no such convention in
the base specification.

Where this specification does place a descriptor is nowhere: no
construct it introduces uses `EssentialProperty` or
`SupplementalProperty` as its carrier, and §4.7.6 records that
uniformly.

#### 5.3.3 Enum: `@layout`

The admissible values are exactly the tokens of §3.2. Which of them are
admissible **on a given slot** is the Publisher's declaration in
`@allowedLayouts`:

| Enum value | Description |
|---|---|
| `linear` | Full-screen takeover. Admissible on an overlay slot as the option of last resort, and inside a linear slot's `ListMPD`, where it is the only form. |
| `overlay` | Plain image or HTML overlay with no named placement. |
| `overlay-corner` | Corner overlay. |
| `overlay-lower-third` | Lower-third overlay. |
| `squeezeback-l-shape` | L-shape: one full-frame ad creative with the shrunk primary content on top (§5.3.7.1). |
| `squeezeback-double-box` | Two boxes; the uncovered bands render as black (§5.3.7.2). |
| `squeezeback-double-box-with-background` | Two boxes plus an advertiser background element filling the uncovered bands (§5.3.7.2). |
| `pause-fullscreen` | Pause ad occupying the whole screen surface. |
| `pause-partial` | Pause ad composited over the paused primary frame, which stays visible underneath. |

An option whose `@layout` is absent from the slot's `@allowedLayouts`
fails the Publisher check, and the Player moves to the next option in
document order (§4.6.5).

#### 5.3.4 `<ImportedMPD>` child, for a video form

When `@form` is `video` the creative is carried through an
`<ImportedMPD>` child, reused verbatim from DASH §5.3.2.6: the sub-MPD's URL
is the element's text content and its single attribute is
`@earliestResolutionTimeOffset` (`xs:double`, default `60.0`, in
seconds).

The child is a **core-namespace** element inside a foreign-namespace
parent. That placement is permitted — the namespace boundary is
lexical, and DASH §5.3.2.6 does not constrain the parent of `<ImportedMPD>`
— and it is deliberate: nesting the baseline element inside the SGAI
element is what makes it opaque to a Player that predates this
specification (§4.7.5), which is the behaviour this construct wants,
since such a Player has no slot to play the creative in. A schema for
`<svta:RenderableAsset>` admits the core-namespace `<ImportedMPD>` as a
first-class child.

#### 5.3.5 Document order is the preference order

The order of the `<svta:RenderableAsset>` children inside a
`<svta:Candidate>` is the preference order. The Player evaluates the
options in that order and renders the first whose form and layout it
can satisfy and whose layout the window admits (§4.6.5).

Carrying several options is the form this specification asks for: a
candidate with several resolves on devices the ADS and the APS know
nothing about, which is what lets one decision serve a heterogeneous
population. Carrying exactly one is equally admissible, and the
Player-visible interface is identical either way — nothing in the
document distinguishes "the APS narrowed the list" from "this is all
there was".

#### 5.3.6 Legacy behaviour and the required-sibling check

`<svta:RenderableAsset>` appears only inside a `<svta:Candidate>`,
inside a `<svta:OverlayList>`, inside a resolution document that a
Player predating this specification never requests — because the slot
that would have triggered the request was skipped at the main-MPD level
(§5.1.3.3, §5.1.4.2). Were the document parsed by such a Player
regardless, it would discard `<svta:OverlayList>` with its whole
subtree and be left with a valid MPD carrying one zero-duration Period.
No baseline element that such a Player needs sits inside an SGAI
element, and removing the SGAI elements changes the semantics of no
baseline attribute on their parents.

#### 5.3.7 Layout composition

##### 5.3.7.1 L-shape / squeezeback

The L-shape has **one** ad creative — a single URL carrying an image, a
video or an HTML creative — and that creative is **always** placed
full-frame in the background. The shrunk primary content is composited
**on top of** it, in one region of the screen; the "L" is the band of
the background creative that stays visible around the shrunk primary
content, commonly the side and the bottom.

The layout therefore puts **two** elements on screen: the full-frame ad
creative and the shrunk primary content over it. There is no separate
third filler element — the ad creative already covers the whole frame,
so the region around the shrunk primary content *is* the ad creative.
This matches the IAB squeezeback model, in which assets are provided in
an underlay format: a full-frame branded creative with a cutout for the
content.

The shrunk primary content is not a creative the ADS or the APS
supplies; it is the main content the Player shrinks. The L-shape is a
presentation option like any other: a candidate lists it among its
ordered options, and the Player renders it when the device can satisfy
it.

##### 5.3.7.2 Side-by-side / double box, and the background element

In a side-by-side / double-box layout the shrunk primary content and
the ad are composed as two on-screen boxes that leave bands uncovered.
A **background element** MAY fill those bands; when none is present
they render as black.

The background element is a still **image** — a branding surface, never
a video and never an HTML surface, so it never consumes a video decoder
— and it is the **advertiser's** creative, mirroring the IAB "Double
Box Video + Background" model. It is a composition attribute of the
layout rather than one of the candidate's alternative presentation
options: the Player does not walk it the way it walks the options, it
composites it as part of rendering the layout once that layout is
chosen.

It is carried as a `<svta:BackgroundElement>` child of the
`<svta:RenderableAsset>` whose `@layout` is
`squeezeback-double-box-with-background`:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@assetUrl` | yes | `xs:anyURI` | — | URL of the advertiser's background image. Concrete media types as for `image` in §5.3.2. |

| Child of `<svta:RenderableAsset>` | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:BackgroundElement>` | yes, when `@layout` is `squeezeback-double-box-with-background` | 1..1 | Exactly one background element on that layout, and none on every other layout. |

A candidate offering the double box **without** a background element
uses the `squeezeback-double-box` token and carries no
`<svta:BackgroundElement>`; the uncovered bands then render as black.

##### 5.3.7.3 Decoder-and-surface budget per layout

The number and type of concurrent elements a layout puts on screen
determine which device classes can composite it. This table is what the
Player evaluates in §4.6.5, and what an APS holding capability
parameters evaluates in §5.8.2.

| Layout | Form of the ad creative | Video decoders | Non-video surfaces | Satisfiable on |
|---|---|---|---|---|
| `overlay`, `overlay-corner`, `overlay-lower-third` | `video` | 2 (primary + ad) | none | D1, D2 |
| `overlay`, `overlay-corner`, `overlay-lower-third` | `image` | 1 (primary) | image over video | D1, D3, D4 |
| `overlay`, `overlay-corner`, `overlay-lower-third` | `html` | 1 (primary) | HTML over video | D1, D3 |
| `squeezeback-l-shape` | `video` | 2 (full-frame creative + shrunk primary) | none | D1, D2 |
| `squeezeback-l-shape` | `image` | 1 (shrunk primary) | image surface for the full-frame creative | D1, D3, D4 |
| `squeezeback-l-shape` | `html` | 1 (shrunk primary) | HTML surface for the full-frame creative | D1, D3 |
| `squeezeback-double-box` | `video` | 2 (primary + ad) | none | D1, D2 |
| `squeezeback-double-box` | `image` | 1 (primary) | image surface for the ad | D1, D3, D4 |
| `squeezeback-double-box` | `html` | 1 (primary) | HTML surface for the ad | D1, D3 |
| `squeezeback-double-box-with-background` | `video` | 2 (primary + ad) | image surface for the background | D1 |
| `squeezeback-double-box-with-background` | `image` | 1 (primary) | image surface for the ad **and** image surface for the background | D1, D3, D4 |
| `squeezeback-double-box-with-background` | `html` | 1 (primary) | HTML surface for the ad **and** image surface for the background | D1, D3 |
| `pause-fullscreen` | `video` | 1, re-tasked from the paused primary content; 2 on a device that cannot re-task it | none | D1, D2; D3, D4 when the device can re-task the decoder holding the paused frame (§8.4) |
| `pause-fullscreen` | `image` | 0 in use for the ad; the paused frame may be released | image surface | D1, D3, D4 |
| `pause-fullscreen` | `html` | 0 in use for the ad; the paused frame may be released | HTML surface | D1, D3 |
| `pause-partial` | `video` | 1 (paused primary holds its frame) + 1 for the ad, unless the device can re-task | none | D1, D2 |
| `pause-partial` | `image` | 1 (paused primary) | image over the paused frame | D1, D3, D4 |
| `pause-partial` | `html` | 1 (paused primary) | HTML over the paused frame | D1, D3 |
| `linear` (full-screen takeover) | `video` | 1, reused sequentially across ad and primary content | none | D1, D2, D3, D4, D5 |

Three readings are worth making explicit, because they are where the
device-class outcome stops being obvious:

- **D2 owns two decoders and still declines the three-element
  side-by-side.** The blocker is the background element, an image
  surface D2 cannot composite. The rule is element **type**, not
  element **count**.
- **The full-screen takeover is the only row satisfiable on every
  class**, because it needs no concurrent composition at all: one
  decoder, reused sequentially. That is what makes it the useful last
  option on a candidate's ordered list.
- **A fullscreen pause ad is the least demanding non-linear form.**
  Nothing of the primary content has to stay on screen, so the Player
  MAY release the resources the primary content and any pre-existing
  overlay hold (§4.6.10). A partial pause ad keeps the paused frame
  visible and therefore keeps its surface.

Whether a given device can re-task the decoder holding a paused frame
is a device property this specification does not decide; the
conservative Player behaviour is described in §8.4. The question is
**open** and it is scoped: D3 and D4 carry the conditional rows because
they can present an ad surface over the paused primary content and the
only thing in doubt is the decoder. D5 presents no ad surface over or
in place of the paused primary content at all, which is what the class
is declared to lack (§3.4), so it declines the pause family and the
re-tasking question does not arise for it. A device that both runs one
decoder and can present a fullscreen surface is a D3 or D4 device on
this axis, whatever else it declines.

### 5.4 Sub-MPD (Single-Period Static profile)

Every `<ImportedMPD>` — from a `ListMPD` Period (§5.2.1.3) or from a
video presentation option (§5.3.4) — points at a sub-MPD bound to the
Single-Period Static profile of DASH §8.15. That binding is structural
rather than a choice: the base specification restricts any document
reached through `<ImportedMPD>` to that profile, and the profile
inherits DASH §7.3, which constrains every Representation's `@mimeType` to
the RFC 4337 registry.

A sub-MPD authored under this specification:

| Property | Value |
|---|---|
| `@profiles` | includes `urn:mpeg:dash:profile:sps:2024` |
| `@type` | `static` |
| `@mediaPresentationDuration` | absent; the Period carries `@duration` instead |
| `@availabilityStartTime` | absent |
| `<Period>` | exactly one, with `@duration` present |
| `<AdaptationSet>` / `<Representation>` | the ad's media, `@mimeType` from the RFC 4337 registry |
| `<EventStream>` of the callback scheme | optional, inside the `<Period>`; carries the ad's tracking schedule (§5.5.2) |

The profile forbids a list of MPD-level elements, and two of them bear
on this specification: `MPD.Metrics` and `MPD.SupplementalProperty`
(DASH §8.15.2). So the `PlayList` metric request lives on the primary MPD
and never travels in a sub-MPD (§5.9), and any descriptor a sub-MPD
carries sits inside the `<Period>`.

`@codecs` values in every MPD this specification defines — main MPD,
`ListMPD`, Overlay Resolution Document, sub-MPD — follow RFC 6381,
which makes the codec identifier case-sensitive and recommends
lowercase hexadecimal: `avc1.4d401f`. The annexes follow that
convention throughout.

#### 5.4.1 Reconciling the declared durations

A candidate's `@duration` in the parent resolution document and the
sub-MPD's `Period@duration` describe the same ad. The parent's value is
the one the Player reads for drop-before-play cap evaluation (§4.6.4),
because it is available without a second fetch. The cap itself is
enforced against **actual rendered length** whatever either document
declared, so a disagreement between the two changes what the Player can
predict, never what it enforces.

### 5.5 Tracking carrier

Timeline-scheduled beacons — impression, start, quartiles, complete —
are carried as `<Event>` entries inside an `<EventStream>` of scheme
`urn:mpeg:dash:event:callback:2015`, defined in DASH §4.7 and DASH §5.10.4.5.
This specification introduces **no** tracking scheme of its own.

**Why the callback scheme is reused as it stands.** It already is a
beacon carrier, named as one: *"DASH Callback events are indications in
the content that it is expected by a DASH Client to issue an HTTP GET
request to a given URL and ignore the HTTP response"*, and *"A content
author may use such an event for tracking play-back of specific content
on a server that is not included in the media path"* (DASH §5.10.4.5.1).
Nothing in it needed extending for ads, and a parallel scheme would
have split tracking across two carriers for no semantic gain.

#### 5.5.1 Carrier shape

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
| `@value` | yes | `xs:string` | — | `1`, the value DASH Table 47 fixes for this scheme. Every tracking carrier authored under this specification declares it. |
| `@timescale` | yes | `xs:unsignedInt` | — | Time base for `<Event>@presentationTime`. `1000`, giving millisecond resolution, is the value used throughout this document. |

Attributes on each `<Event>`:

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@presentationTime` | yes | `xs:unsignedLong` | `0` in the schema | When the Player fires the beacon, in `@timescale` units, measured from the start of **this ad's** presentation. |
| `@id` | yes | `xs:unsignedLong` | — | Identifier of the beacon, used by the Player for de-duplication and by the implementation for logging. The type is the base specification's own; this specification narrows the attribute from optional to required, because de-duplication is keyed on it (§4.6.15). |

The element's **text content** is the absolute HTTP(S) URL the Player
GETs at the scheduled time. It is the element's content and not
`@messageData`, which the base schema declares `use="prohibited"` and
annotates *"Deprecated in favor of carrying the message information in
the value space of the event"*.

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

Where a candidate carries a tracking `<EventStream>` and its video
form's sub-MPD carries one as well, the Player fires the union, with
beacons sharing an `@id`, or carrying the same URL at the same
`@presentationTime`, fired once (§4.6.15).

> **Note for tooling, and an obligation on a validator.** The base
> specification places `<EventStream>` as a child of `<Period>`.
> Carrying it directly inside `<svta:Candidate>` is admissible as
> foreign-namespace open content but is novel relative to that
> canonical placement, so a validator or an analytics pipeline that
> locates callback event streams by scanning only `<Period>` children
> misses the carrier attached to a non-video candidate. A validation
> procedure that reports such a document valid while skipping the
> foreign-namespace subtree **has not checked the tracking carrier at
> all**, which is the outcome a reader is most likely to arrive at by
> default. Tooling implementing this specification scans inside
> `<svta:Candidate>` as well, and a validation report states which of
> the two it did.

#### 5.5.3 The timebase

Every `<Event>@presentationTime` inside a resolution document is
expressed **relative to the start of the ad's own presentation** —
never to the primary timeline and never to wall-clock. A beacon on the
ad's first frame declares `presentationTime="0"`; quartile beacons for
a 10-second ad at `timescale="1000"` sit at 2 500, 5 000 and 7 500. The
Player adds the ad's start position on the primary timeline to each
relative value to obtain the firing point.

An `image` or `html` form has no segment-aligned media to anchor that
origin, so the Player establishes the ad's presentation timeline at the
moment the asset becomes visible: offset 0 is the first rendered frame
of the image or of the HTML document.

Beacon scheduling runs on the presentation timeline, so primary content
playing at a speed other than 1× moves the wall-clock instants at which
beacons fire without changing their scheduled presentation times
(§4.6.14).

### 5.6 ClickThrough carrier

The resolution document carries the ad's ClickThrough URL and its
associated click-tracking URLs in a single normative carrier, so that
every Player conformant to this specification reads them the same way.

**Why a new construct, and why not the callback scheme.** The base
specification defines no carrier for click-through metadata, and — more
fundamentally — no user-triggered event of any kind: every event is
evaluated against the media presentation timeline, and the callback
scheme in particular fires its GET when the playhead reaches the
event's presentation time and discards what comes back. A ClickThrough
activation has no presentation time; it happens when the viewer acts,
or never. The callback scheme is therefore the right carrier for
impressions and quartiles and the wrong one for the click.

The base specification is not silent about user action, and this
specification follows what is there rather than claiming an absolute
absence: `@skipAfter` *"describes an offset in time (in fractional
seconds) from the beginning of the alternative presentation till the
moment the rest of that presentation may be skipped by the application
in response to a user action"* (DASH §5.16.5.2) — a user action with a
normative consequence — and DASH Annex L fires an HTTP request off the
timeline on a viewer selection (DASH §L.3.3). The pattern this carrier
follows is that one: the declaration sits in the document, and the
request is made when the viewer acts.

This carrier is **normative and interoperable**, which is what
separates it from the best-effort metadata of §5.7: the click works
across Players conformant to this specification, rather than being
silently ignored by some of them. The scoping to such Players is not a
weakening but the only obligation available (§4.1).

#### 5.6.1 `<svta:Click>`

| Attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `@clickThroughUrl` | yes | `xs:anyURI` | — | The destination the Player opens, or hands off to the platform, when the viewer activates the click. |

| Child | Required | Cardinality | Description |
|---|---|---|---|
| `<svta:ClickTracking>` | no | 0..n | One click-tracking URL, carried as the element's text content. The Player fires each once, at the moment of activation. |

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

On a non-linear slot the element is a child of `<svta:Candidate>`, so
the ClickThrough travels with the ad rather than with the slot: a
Publisher configures nothing beyond permitting the ad. On a linear slot
the same element is the carrier and travels as foreign-namespace open
content on the `ListMPD` `<Period>` of the ad it belongs to, which a
Player predating this specification discards with its subtree exactly
as it discards the element inside a candidate.

> **Note on profile signalling.** DASH §8.1 removes, for a
> profile-conformance check, every extension-namespace element the
> declared profile does not explicitly include (§4.7.8). A `ListMPD`
> whose `@profiles` names only `urn:mpeg:dash:profile:list:2024`
> therefore has its `<svta:Click>` removed by that procedure, and a
> client bound to the list profile alone is entitled to drop it.

On a Player that predates this specification the click is inert: the
carrier is discarded with its parent subtree, the ad renders, and no
click fires.

### 5.7 Application-level metadata

Generic application-level creative metadata that has no native carrier
in the base specification — the identity of the ad system, the
creative's title, the advertiser, a universal ad identifier — rides on
extension elements in the SVTA Ads WG namespace, as children of
`<svta:Candidate>`.

This carrier is **optional on both ends by design**: nothing obliges an
APS to emit it or a Player to read it, and a Player predating this
specification discards the elements with the parent subtree. What this
specification fixes is that the place exists and is named; nothing in
the ad presentation depends on anyone using it. That is what makes it a
requirement on the specification rather than on an implementation —
what can be checked is that the place exists, not that anyone used it.

| Element and attribute | Required | Type | Default | Description |
|---|---|---|---|---|
| `<svta:AdSystem>@value` | yes, when the element is present | `xs:string` | — | Identifier of the ad system that produced the decision. |
| `<svta:AdTitle>@value` | yes, when the element is present | `xs:string` | — | Human-readable title of the creative. |
| `<svta:Advertiser>@value` | yes, when the element is present | `xs:string` | — | Human-readable identifier of the advertiser. |
| `<svta:UniversalAdId>@idRegistry` | yes, when the element is present | `xs:string` | — | Registry that scopes the identifier, for example `ad-id.org`. |
| `<svta:UniversalAdId>@value` | yes, when the element is present | `xs:string` | — | The registry-scoped identifier of the creative. |

Each of the four elements is an OPTIONAL child of `<svta:Candidate>`,
at most once.

`<svta:UniversalAdId>` is listed here deliberately rather than as a
normative carrier of its own. A universal ad identifier serves ad
tracking and reconciliation on the decisioning side, which the upstream
ad standards already handle; this specification does not replicate that
carrier in the resolution document. An APS that wants to propagate the
identifier anyway has a named place for it, and no Player behaviour
depends on it. This is the deliberate contrast with the ClickThrough of
§5.6, which is mandated because the click has to work across Players.

### 5.8 The resolution request

The Player issues the resolution request as an HTTP GET against the
slot's `@uri`. Two independent sources contribute query parameters to
that URL: the Publisher's author-declared template (§5.8.1) and the
Player's own capability declaration (§5.8.2).

#### 5.8.1 Publisher-declared parameters

The Publisher MAY declare a query template through the base
specification's extended HTTP GET parameterisation. Under the
`urn:mpeg:dash:urlparam:2025` scheme the signalling has two parts, and
they are separate elements:

- **An empty descriptor enabling the scheme.** *"An
  MPD.EssentialProperty element with the attribute @schemeIdUri having
  value of "urn:mpeg:dash:urlparam:2025" shall be present and have no
  content, unless the scheme is explicity allowed in a profile"*
  (DASH §I.3.1). The descriptor is a flag, not a container.
- **A `<RequestParam>` element of type
  `up:ExtendedUrlInfoType`**, carrying the template itself. *"The
  scheme uses a single element, RequestParam of type
  ExtendedUrlInfoType"*, and it *"may be present in elements such as
  but not limited to MPD, Period, AdaptationSet, Representation,
  Preselection, or EventStream"* (DASH §I.3.1). Authoring it inside the
  slot's own `<EventStream>` scopes the template to the slot that owns
  it.

  `<RequestParam>` is **not** in the URL-parameter namespace, which is
  a mistake the `up:` prefix invites: the base specification's NOTE in
  DASH §I.3.1 states that *"As opposed to other elements of type
  ExtendedUrlInfoType, RequestParam is defined in the main DASH
  schema, not in the XML schema defined in this Annex."* Only its
  **type** comes from that namespace. The element is authored
  unprefixed in the DASH default namespace, as the base
  specification's own example authors it.

> **The element is `<RequestParam>`.** The base specification declares
> no element named `UrlParamInfo`, in this clause or anywhere else, and
> a `<RequestParam>` nested **inside** the enabling descriptor would
> contradict DASH §I.3.1's requirement that the descriptor have no content.
> This note is here because the project's own canonical input set
> carries the wrong name and the wrong nesting in its linear-interface
> reference, and a reader arriving from that document needs to know
> which of the two is the base specification's. It is
> `<RequestParam>`, as a sibling of the empty descriptor, at a DASH
> hierarchy element.

The empty descriptor is an `<MPD>` child, and `MPDtype` is an ordered
`xs:sequence` in which `EssentialProperty` follows `Period`, so it is
authored **after** the last `</Period>`.

`@includeInRequests` is what scopes a template to a particular kind of
request. Its value is *"a white spaced concatenated list of keys"*, and
the two keys that matter here are:

| Token | Scope | Defined in |
|---|---|---|
| `altmpd` | *"all requests for MPDs representing the alternative Media Presentation, as defined in subclause 5.16"* | DASH Table I.4 |
| `urn:svta:dash:request:sgai-resolution:2026` | The **non-linear** resolution request of this specification: the GET a Player issues against an overlay or pause slot's `@uri` | §2.1 of this document |

**Why a URN of our own, and why it is not an invention.** `altmpd`
names Alternative MPD requests, which are the linear family's; an
overlay or pause resolution request is not one, so `altmpd` does not
reach it. The value space of `@includeInRequests` is not closed: its
last row is `<URN / tag URI>`, *"a URN or tag URI, where the request
type semantics is understood by the client and specified by the URN /
tag URI owner. The client shall drop unknown URIs from the
@includeInRequests and @includeInHeaders strings prior to processing
them as specified in this Annex"* (DASH Table I.4). Naming the non-linear
resolution request with a URN the SVTA Ads WG owns is therefore the
base specification's own extension hook, and the drop rule gives it
legacy-safe behaviour for free: a client that does not know the URN
removes the token and processes the rest.

A template scoped to the non-linear request declares both tokens only
if it wants both kinds of request parameterised; the tokens are
independent.

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">
  <Period id="1" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="201" presentationTime="600000" duration="30000">
        <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay"
                                  maxDuration="30000"
                                  allowedLayouts="overlay-corner overlay-lower-third"/>
      </Event>
      <RequestParam includeInRequests="urn:svta:dash:request:sgai-resolution:2026"
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
the slot's `@uri`. This specification extends that mechanism in no way
beyond naming one additional request type.

#### 5.8.2 Player-declared capability parameters

This specification reserves a set of **query-parameter names** the
Player MAY attach to the resolution request, stating what its device
can render. Which of them travel is the Player's decision, taken at
runtime; no declaration by the Publisher, the APS or the ADS is
required before a Player sends them.

**Why these are not carried by the author-declared template.** The
mechanism of §5.8.1 is the base specification's upstream channel for
exactly this class of request, and it misses on both axes. Its payload
is session **state**: I.4.1 states the purpose — *"In some cases, such
as dynamic advertisement insertion and content steering, there is a need
to express knowledge of the current state of the player"* — and Table
I.5 is that vocabulary in full: the codecs and bandwidth of what is
playing, the selected language, the protection scheme, CMCD keys, and
per-event execution counters and deltas. What is *playing* and what has
*run*, with no parameter for decoder count, image compositing or HTML
compositing. And the template is authored by the content author in the
MPD — `@queryTemplate` *"provides URL parameters template information.
This string shall contain one or more $<ParamIdentifier>$ template
identifiers"* (DASH §I.2.2.2) — so a Player cannot add an axis to a template
it did not write. The two neighbouring mechanisms miss for their own
reasons: CMCD carries operational delivery state, and
`ServiceDescription` runs the opposite way, letting the service
prescribe consumption targets to the client. The reserved set below is
new by necessity rather than by preference.

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

A fourth axis would have to distinguish two classes these three already
separate, so none is reserved. A boolean is used rather than an
enumerated surface list because a list has no way to say "no surfaces
at all" that is distinguishable from an empty value, and §5.8.3
requires a parameter the Player will not populate to be **omitted**
rather than emptied.

#### 5.8.3 Sending, omitting, and extending

- Sending a reserved parameter is **optional**. A conformant Player
  sends all of them, some of them, or none.
- Where the Player has no value for a reserved parameter, or does not
  disclose its value, it **omits the parameter entirely** rather than
  sending it with an empty or placeholder value.
- A parameter the Player attaches that is not one of the reserved names
  carries a vendor-specific prefix of the form `x-<vendor>-`, so that
  reserved names added in a later edition stay free.
- The reserved names are reserved on the resolution request as a whole.
  A Publisher authoring a `<RequestParam>` query template (§5.8.1)
  draws its parameter names from outside the reserved set, so the two
  sources compose on one URL without collision.

#### 5.8.4 What an absent parameter means

A reserved parameter absent from the resolution request means its value
is **undetermined**: the Player did not determine it, or did not
disclose it. Absence does not assert that the device lacks the
capability.

This specification does not define how an APS resolves an undetermined
value. An APS that resolves it conservatively — emitting no option that
depends on the undetermined axis — and an APS that assumes the most
capable case are both conformant, and they will emit different
documents to the same Player. What does not vary is that the Player
checks whatever arrives before rendering it (§4.6.5).

An APS answers a request carrying none of the reserved parameters by
emitting the candidates' options unnarrowed (§4.5.9). A Player that
declares nothing therefore receives the full ordered list and resolves
the choice itself — which is the same document an APS emits when it
holds no device view at all.

### 5.9 Declaring the pause-delivery metric

A pause slot has no authored duration, so what is worth measuring is
**how much of the paused interval carried an ad**, not how many pause
opportunities occurred. The number of opportunities is set by the
viewer, who decides when and how often to pause: it can be neither
controlled nor incentivised, and a figure that moves for reasons no
party influences reports nothing about how well the slot was served.
The filled fraction can be influenced, by the APS returning candidates
that keep the slot filled for longer.

This specification defines **no metric of its own** for it. The
quantity is derived from the `PlayList` metric of DASH Annex D.4.6, which
defines it as *"A list of playback periods"*, where a playback period is
*"the time interval between a user action and whichever occurs soonest
of the next user action, the end of playback or a failure that stops
playback"*. Two of its fields carry everything a pause slot needs:

- each playback-period entry declares a `starttype`, whose value space
  includes *"Resume - Resume from pause"* — the entry whose `starttype`
  is `Resume` is the one that ends a pause;
- inside a playback period, each continuously rendered stretch declares
  a `stopreason`, whose value space includes *"UserRequest - User
  request"* and *"Rebuffering - Rebuffering"*. That is what separates a
  viewer pause from a stall: a period that stopped on `Rebuffering` is
  not a pause opportunity and no pause-trigger window fired.

**The paused interval is therefore derived rather than measured
separately**: it is the interval between the end of a playback period
whose last rendered stretch stopped on `UserRequest` and the `start` of
the next entry whose `starttype` is `Resume`. Against that interval,
the duration the pause ad actually occupied is the filled fraction.

The Publisher requests the metric on the **primary** MPD:

```xml
<Metrics metrics="PlayList"
         reportingInterval="PT60S">
  <Range starttime="PT0S"/>
</Metrics>
```

`MPD.Metrics` is forbidden in a Single-Period Static MPD (DASH §8.15.2), so
the declaration can never travel in an imported ad MPD; the primary MPD
is the only place it lives.

**How a measurement reaches anyone is out of scope**, and the base
specification takes the same position about its own metrics: *"This
document does not define mechanisms for reporting metrics; however, it
does define a set of metrics and a mechanism that may be used by the
service provider to trigger metric collection and reporting at the
clients, if a reporting mechanism is available"* (DASH §5.9.1). This
specification defines the quantity and inherits that silence about
transport.

## 6. Interfaces

This chapter describes the message flows between the four actors, the
transports they run on and the payloads they carry. Everything at or
below the Player↔APS boundary is Player-visible and normative; the
APS↔ADS leg is described for orientation and is not defined by this
specification (§6.7).

### 6.1 The end-to-end flow

```
                                         primary content (Publisher's CDN)
                                                    ^
                                                    | (3) GET segments
                                                    |
  +-------------+  (1) GET main MPD    +----------+ | (5) GET ad creative
  | Publisher   |<---------------------|          |-+-------------------------> ad CDN
  | (encoder +  |                      |          |
  |  packager + |--(2) MPD with -----> |  Player  |  On the APS response:
  |   CDN)      |      SGAI events     |          |    (6) validate vs the window
  +-------------+                      |          |    (7) enforce the cap
                                       |          |    (8) fire beacons / click
                                       +----+-----+
                                          |    ^
                          (4a) GET        |    |  (4b) 200 OK
                        <slot @uri>?<q>   |    |  resolution document
                                          v    |
                                       +----------+   (4c) ad decision
                                       |   APS    |<----------------------> ADS
                                       | (adapter)|   (not defined here)
                                       +----------+
```

1. The Player fetches the main MPD.
2. The Publisher serves it, carrying one or more SGAI opportunity
   declarations (§5.1).
3. The Player fetches primary segments and plays the main timeline.
4. When an opportunity becomes current — the playhead approaching a
   timeline event, or a viewer pause beginning inside a pause-trigger
   window — the Player issues the resolution request (4a) and receives
   the resolution document (4b). Behind the APS, the ad decision is
   obtained (4c).
5. The Player fetches the creative: ad segments from the ad CDN for a
   `video` form, or the asset at `@assetUrl` for an `image` or `html`
   form.
6. The Player validates each candidate against the window that served
   it (§4.6.3).
7. The Player enforces the cap (§4.6.4).
8. The Player fires the beacons the document carries (§4.6.15), and the
   click on activation (§4.6.16).

For a linear slot the Player then resumes the main timeline per the
event's semantics: insertion resumes where the main timeline was
paused, and replacement resumes at the position `@returnOffset`
determines, because main media time kept advancing while the ad played.
For a non-linear slot the main timeline never stopped.

### 6.2 Publisher → Player: the main MPD

| Property | Value |
|---|---|
| Transport | HTTP/HTTPS, pull |
| Payload | DASH MPD (XML), carrying the opportunity declarations of §5.1 |
| Direction | Request / response |
| Failure | HTTP status codes. A failure here is a primary-content delivery failure and is outside this specification. |

The Publisher is an authoring-time actor: it emits nothing at runtime
beyond serving the manifest and the primary segments.

### 6.3 Player → APS: the resolution request

| Property | Value |
|---|---|
| Transport | HTTPS, pull, synchronous |
| Payload | HTTP GET against the slot's `@uri`, with query parameters from the two sources of §5.8 |
| Trigger | The playhead reaching a timeline slot, at or after the ERT; or a viewer pause beginning inside a pause-trigger window |
| Failure | §8.1, rows E1 to E3 |

One request per slot. Where a pause resolution document declares
`request-again` and its candidates are exhausted inside one pause, the
Player issues a further request for that same pause (§4.6.11).

### 6.4 APS → Player: the resolution document

| Property | Value |
|---|---|
| Transport | HTTPS, response to §6.3 |
| Payload | `ListMPD` (§5.2.1) for a linear slot; Overlay Resolution Document (§5.2.2) for an overlay or pause slot |
| Success | `200` with a document body. A `200` carrying **no candidates** is a well-formed answer that produced no ad, and the Player treats the attempt as a failed execution and continues down the fallback chain (§4.6.8, §5.2.3). |
| Failure | No response, a non-`200` status, a body that does not parse, or a document of the wrong family. All four put the Player on the fallback chain (§8.1). |

### 6.5 Player → ad CDN: fetching the creative

| Property | Value |
|---|---|
| Transport | HTTP/HTTPS, pull |
| Payload | For `video`: the sub-MPD and then its segments. For `image` / `html`: the asset at `@assetUrl`. |
| Failure | Segment-level retry per the usual DASH practice, then §8.1 row E11: the Player aborts that ad and keeps the primary content playing. |

### 6.6 Player → tracking endpoints

| Property | Value |
|---|---|
| Transport | HTTP/HTTPS, fire-and-forget |
| Payload | HTTP GET to the URL carried in a callback `<Event>`; the response is discarded without parsing |
| Click | HTTP GET to each `<svta:ClickTracking>` URL at the moment of activation, plus opening or handing off `@clickThroughUrl` |
| Failure | Non-fatal throughout (§8.1 row E13). Never surfaced to the viewer. |

### 6.7 APS → ADS, and the conversion (non-normative)

This leg is **not defined by this specification**. It is described here
so that a reader knows where the boundary is, and everything in this
section is informative.

In practice the APS requests an ad decision from the ADS and receives a
decision document, typically IAB VAST. It then converts that document
into the resolution document the Player reads. A conversion of the
common shapes:

| Decision-document concept | Resolution-document target |
|---|---|
| One ad in the break | One `<Period>` with one `<ImportedMPD>` in a `ListMPD`; or one `<svta:Candidate>` in an Overlay Resolution Document |
| A wrapper or redirect chain | Resolved inside the APS before the Player sees anything; the Player has no visibility into the hops, which preserves one request per slot on the Player↔APS leg |
| The ad's duration | `Period@duration` in the `ListMPD` and in the sub-MPD; `<svta:Candidate>@duration` in an Overlay Resolution Document |
| A media file per encoding | One `<Representation>` inside an `<AdaptationSet>` of the sub-MPD; several collapse to an ABR ladder |
| A non-audiovisual creative | `@assetUrl` on a presentation option (§5.3.2) |
| Tracking events | `<Event>` entries in a callback `<EventStream>` at the matching relative times (§5.5) |
| An impression | A callback `<Event>` at offset `0` |
| A click-through and its click-tracking | `<svta:Click>` with its `<svta:ClickTracking>` children (§5.6) |
| Ad system, title, advertiser, universal identifier | The optional metadata elements of §5.7 |
| A decision carrying no ads | A resolution document carrying no candidates (§5.2.3) |
| An error signalled by the ADS | Nothing in the document. How the APS reacts belongs to the APS-to-ADS contract; what the Player observes is an opportunity that yielded no candidates, and the fallback chain of §4.6.8 follows. |

Two cases are worth naming because a reader will look for them. A
**decision entry that carries tracking and no media** cannot become a
candidate — there is nothing to render — and what the APS does with it
is APS-internal policy (§8.2). And the **fidelity** of the conversion —
that no beacon was added, dropped or reordered, and that a declared
click-through travelled — is enforceable only between the APS and the
ADS, because the resolution document does not show what was declared
(§4.5.6, §4.5.8).

Nothing in chapters 4, 5 or 7 depends on the decision document being
VAST, on any VAST version, or on VAST existing at all.

### 6.8 Interface contracts summary

| Source | Target | Transport | Payload | Failure semantics |
|---|---|---|---|---|
| Player | Publisher CDN | HTTPS | MPD, then media segments | HTTP status; primary-content concern, outside this specification |
| Player | APS | HTTPS | Query parameters out, resolution document back | `200` with no candidates is an answer that produced no ad; that, a transport failure, a non-`200`, an unparseable body and a wrong-family document all put the Player on the fallback chain |
| Player | Ad CDN | HTTPS | Sub-MPD, ad segments, or a still image / HTML asset | Retry, then abort the ad and keep the primary content |
| Player | Tracking endpoints | HTTPS | Body-less GET | Best-effort; never reaches the viewer |
| APS | ADS | — | — | Not defined by this specification (§6.7) |

All transport runs over HTTPS in production. Authentication, content
protection and token exchange layer on top and are outside this
specification.

## 7. Expected behaviour

Chapter 4 states the obligations. This chapter describes how they
compose in the situations an implementer meets, per actor and then per
scenario. The complete walk-throughs are in the annexes.

### 7.1 Publisher behaviour

The Publisher authors and serves. At authoring time it decides where
opportunities sit, which family each one is, which layouts each one
admits, what each one's cap is, how much head start the APS gets, and
whether a window is bounded to one execution per session. It declares
the `PlayList` metric where pause windows exist.

It decides one more thing, and the decision is invisible in the
manifest: **what a Player predating this specification sees**. On live
content the answer is the primary content, and the opportunity is an
expected loss. On on-demand content the Publisher MAY author a baseline
linear break alongside the non-linear declaration, and then the two
populations diverge by design (Annex G).

### 7.2 ADS behaviour

The ADS decides and emits. It selects the ads, how many and in what
order, and declares the tracking schedule. It observes no
Publisher-declared constraint and holds no device view; both are
somebody else's obligation, and a conformance check on an ADS does not
test either (§4.4).

No-fill is a decision it is entitled to take, and the Player sees it as
a document rather than as an error (§5.2.3).

### 7.3 APS behaviour

The APS converts and answers. Per request it obtains the decision,
produces the resolution document of the family that asked, carries the
options in preference order, transcribes the tracking schedule, carries
the click, and — on a pause document — declares the exhaustion
behaviour.

Its one runtime freedom worth naming is **narrowing**. An APS that
received capability parameters MAY emit fewer options per candidate,
down to one; an APS that received none emits them unnarrowed. Both are
conformant, the Player-visible interface is identical, and the Player
validates whatever arrives (§5.8.4).

### 7.4 Player behaviour: the common loop

Every scenario below is the same loop with different inputs:

1. **Detect.** The playhead approaches a timeline slot, or a viewer
   pause begins inside a pause-trigger window.
2. **Resolve.** Issue the resolution request at or after the ERT, with
   whichever capability parameters the Player discloses.
3. **Parse.** On a failure to obtain a usable document of the right
   family, attempt the next overlapping window of the family; when the
   family is exhausted, continue with the primary content (§4.6.8).
4. **Per candidate, in document order.** Walk the presentation options
   in document order; render the first the device can satisfy and the
   window admits. Where none passes, skip the candidate and take the
   next. Where the candidates are exhausted, continue with the primary
   content — and on a pause slot, apply the declared exhaustion
   behaviour instead (§4.6.11).
5. **Render.** One non-linear form at a time, at the primary content's
   speed, composited per the layout.
6. **Track.** Fire the beacons on the ad's own timeline; fire the click
   on activation.
7. **Bound.** Enforce the cap against actual rendered length, trimming
   mid-ad if necessary and stopping the remaining beacons at the trim
   boundary.
8. **Finish.** Resume or continue the primary content.

### 7.5 Per-scenario behaviour

#### 7.5.1 Linear ad break — pre-roll, mid-roll

The inherited path. The Player resolves the slot, receives a `ListMPD`,
plays the Periods back-to-back in declared order, and enforces the cap
against their cumulative rendered length. Selection already happened
upstream: a `ListMPD` is a playlist and not a candidate set.

Every device class behaves the same, because a linear ad needs one
decoder reused sequentially. The classes differ only in how much
pre-buffering they can afford, which is a Player implementation matter.

#### 7.5.2 Multi-ad break

A `ListMPD` with more Periods. The arithmetic is the whole of the
scenario: the Player sums the declared durations against the cap, MAY
drop a candidate whose declared duration would overrun it, and trims
against actual length if an accepted ad runs long. The candidates that
survive keep the document's order.

#### 7.5.3 Coexisting overlay

The primary content keeps playing. The Player resolves the overlay
slot, walks the candidate's options in order, and composites the first
option the device can satisfy and the window admits. Outcomes by class
follow §5.3.7.3: D1 takes the richest option on offer, D2 takes a video
overlay and declines every non-video surface, D3 takes HTML or image,
D4 takes image, and D5 declines the opportunity and keeps playing the
primary content.

Declining is a defined outcome and not a failure.

#### 7.5.4 Hybrid — a linear ad with a concurrent overlay

Two independent slots at the same presentation time (§5.1.5), resolved
and validated separately. The linear portion takes over the surface and
the overlay composites on top of it. On a single-decoder class the
overlay is satisfiable only as a non-video surface; where it is not
satisfiable at all, the linear ad plays alone.

The linear ad occupies the surface but does not consume a second
decoder: it replaces the primary content on the one decoder rather than
joining it.

#### 7.5.5 Pause-triggered ad

The trigger is the viewer, not the playhead. On a pause beginning
inside a pause-trigger window the Player resolves the slot — at the
moment of pause, or speculatively at the ERT (§8.5) — and presents the
first satisfiable option over the paused frame, fullscreen or partial
according to the layout token.

Any active overlay is suspended for the duration of the pause, and any
linear ad on screen is suspended and resumed from where it stopped
(§4.6.13). On resume the pause ad is dismissed within one rendering
frame and the suspended form is restored if its own window is still
open.

In live content the Player's presentation time stays frozen inside the
window for the pause, bounded by the time-shift buffer (§4.6.17).

Where the candidates run out while the pause continues, the document's
declared behaviour applies: present the sequence again, request a new
document, or show the paused frame (§4.6.11).

#### 7.5.6 Overlapping windows of one family

The first window by presentation time is served; the rest are backups.
An attempt that produces no ad — unreachable APS, non-`200`,
unparseable body, wrong family, or a well-formed document with no
candidates — is a failed execution, and the Player attempts the next
window. A document that *carries* candidates ends the chain whatever
the Player then does with those candidates: a candidate skipped for
want of a satisfiable option leads to the next candidate and,
eventually, to the primary content — never to the next window
(§4.6.6, §4.6.8).

Each window binds what it serves with its own allowed layouts and its
own cap (§4.6.9), so the same candidate can be admissible under one
window of a chain and inadmissible under another.

#### 7.5.7 An overlay window crossing a pause-trigger window

Two windows of **different** families overlapping in time is not a
chain; both are live. The overlay presents while the content plays, and
if the viewer pauses inside the pause window the pause ad takes the
surface and the overlay is suspended. On resume the overlay returns if
its window is still open, and is gone if the window expired during the
pause. At no instant are both on screen (§4.6.7).

#### 7.5.8 A Player that predates this specification

The event stream carrying an unknown scheme is skipped with all its
events; the extension elements are discarded with their subtrees; the
primary content plays. What the viewer sees instead is the Publisher's
authoring choice (§4.7.7).

#### 7.5.9 A non-linear ad over a replacement that is not advertising

The base specification's replacement construct is not an ad construct:
it replaces a span of the primary timeline with an alternative
presentation, whatever that presentation is — a regional blackout
slate, a rights-restricted substitution, a filler card. An overlay
window may overlap such a replacement, and nothing in this
specification makes that case special: the Player resolves the overlay
slot, validates against that window's declarations, and composites the
chosen form over whatever is on the surface. What is underneath the
overlay is not the overlay's concern.

The decoder budget is the one thing that does change, and only in
bookkeeping: the surface is occupied by the replacement rather than by
the primary content, and it is still one decoder (Annex N).

## 8. Implementation notes

This chapter is **non-normative**. It gives guidance on the conditions
an implementation meets in operation, and on the choices this
specification deliberately leaves open. Where a row below states a
"MUST", it restates an obligation chapter 4 already carries.

### 8.1 Error semantics

Every condition on the Player-visible interfaces under which an ad
opportunity can fail to be honoured, with what the Player does and
what the other actors carry for each. The invariant across every row is
§4.6.1: primary-content playback survives all of them.

| ID | Condition | Player (required) | Player (permitted) | Other actors |
|---|---|---|---|---|
| **E1** | The resolution request fails at transport level — DNS, TCP, TLS, timeout before a final status — or returns a final status other than `200`, including an APS that refuses to answer because a capability parameter was absent. | Treat the attempt as a failed execution, attempt the next overlapping window of the family, and continue with the primary content once the family is exhausted (§4.6.8). | Re-attempt inside the interval between the ERT and the slot's presentation time; surface the failure through an implementation-defined API. **Open**: this specification fixes no retry count, backoff or deadline. | Publisher: declare a fallback window where continuity matters, and an `@earliestResolutionTimeOffset` wide enough to leave room (§4.3.5, §4.3.6). APS: answer without any reserved parameter (§4.5.9). |
| **E2** | `200`, but the body is not a resolution document the Player can parse: malformed XML, unknown root, schema-invalid content. | Treat the attempt as a failed execution and continue down the chain as in E1; render nothing from that document. | Log the parse or validation failure. | APS: emit a document valid against the base schema plus the extension points of §4.7.1 — and validated including its foreign-namespace subtree, or the tracking carrier was not checked at all (§5.5.2). |
| **E3** | `200` with a well-formed document whose **family does not match** the slot that requested it. | Treat it as a failure to resolve and continue down the chain (§4.6.8). | Report the family mismatch. | APS: answer the slot that asked (§4.5.2). A misrouted response read as an empty resolution would silence every remaining window. |
| **E4** | `200` with a well-formed, complete document that **carries no candidates**. | Treat the attempt as a failed execution and attempt the next overlapping window, continuing with the primary content once the family is exhausted; do not count the attempt as an execution, so an `@executeOnce="true"` slot stays executable (§4.6.8, §5.2.3). | Report the opportunity as **unfilled** rather than failed. This is the distinction with the most operational value in the table: it separates "the market was asked and did not buy" from "the APS could not be reached", which look identical from the viewer's screen. | APS: express a no-ads decision as a document, never as an error status and never as a bodiless response (§4.5.7). ADS: none — no-fill is a decision. |
| **E5** | The resolution document arrives after the slot window has elapsed. | Keep within what the cap bounds for that family (§4.6.4) and keep the primary content uninterrupted. On a linear replacement slot, honour the clip semantics: a late start shortens the presentation rather than moving the scheduled end. | Discard the document. **Open**: this specification states no deadline after which a pending response is abandoned, and no Player response for a document that lands after the window is over. | Publisher: an `@earliestResolutionTimeOffset` that gives the APS a usable head start. APS: answer inside the window it was asked in; the APS-to-ADS latency budget is bilateral. |
| **E6** | The slot declaration carries no `@maxDuration`, or declares zero. | With none declared, present no ad from that slot and continue with the primary content (§4.6.4). With zero, the opportunity does not fire. | Report the defective declaration. Note that the no-cap rule diverges from the base specification's unbounded default and is **open** (§4.6.4). | Publisher: declare a cap on every slot (§4.3.2). |
| **E7** | No presentation option on a candidate is satisfiable: the device renders none of the forms, or every offered layout needs more decoders or surfaces than the device has (§5.3.7.3). | Skip the candidate and advance to the next in document order; continue with the primary content only once every candidate is exhausted (§4.6.6). Do not attempt the next window — a document carrying candidates is not a failed execution. | Report the skip. | APS: carry the options as an ordered list in preference order (§4.5.3). A candidate carrying a single option places the suitability call upstream. |
| **E8** | An option names a layout the window did not allow, or one outside the closed set of §3.2. | Do not render that option; move to the next in document order, and skip the candidate when none passes both checks (§4.6.5). Check against **the window that served the candidate**, which binds it with its own allowed layouts and its own cap (§4.6.9). | Report the rejected layout name. **Open**: this specification defines no "unrestricted" value for `@allowedLayouts`, so a window admits exactly the tokens it lists; an implementation meeting a token it cannot map to §3.2 treats it as not admitted. | Publisher: draw allowed-layout names only from §3.2, and name a pause **surface** rather than a bare pause type (§4.3.3). APS: emit no form metadata outside that set (§4.5.4). |
| **E9** | A creative's carrier is outside video, image and HTML, or a non-audiovisual asset URL is expressed as a Representation `@mimeType` on a path bound by RFC 4337. | Render no form the device cannot render (§4.6.20). | Skip the candidate as a non-conformant upstream signal and fall through as in E7. **Open**: for a carrier outside the admissible set that the device *can* nevertheless render, this specification states no obligation either way. | APS and Publisher: every creative carries a media type inside §3.3, and non-audiovisual URLs travel on the carrier of §5.3.2, never on an RFC 4337-bound `@mimeType` path (§4.7.2). |
| **E10** | The cap is reached: a candidate's **declared** duration would push the cumulative duration past it, or an accepted candidate's **actual** length exceeds what it declared. | Where the cap bounds cumulative duration, stop rendering once it would be exceeded, even mid-ad, enforcing against actual length; stop the remaining beacons at the trim boundary; convert the candidate's ISO 8601 duration into the cap's timescale, rounding up, before comparing; keep the surviving candidates in document order (§4.6.4, §4.6.7, §4.6.15). | Drop a candidate before playback on declared duration alone. Surface the trim. | Publisher: declare the cap (§4.3.2). ADS: not required to respect it (§4.4.3). Cap arithmetic runs on the presentation timeline, so an interval in which that timeline does not advance does not accrue (§4.6.4), and a pause slot has no authored duration for the cap to bound (§4.6.10). |
| **E11** | Rendering an accepted candidate fails at runtime: an ad segment returns 4xx/5xx, a decode error, the network is lost mid-ad. | Abort that ad and continue playing the primary content uninterrupted (§4.6.1). | Skip to the next candidate in document order, or end the slot — Player policy. Retry the ad segment before aborting. | APS: reference media reachable for the duration of the slot (§4.5.11). |
| **E12** | An event scheme URI, extension element or foreign namespace is unknown to the Player. | Ignore the unknown construct with its whole subtree and keep playing (§4.6.21). | Log it. Ignore the application-level metadata of §5.7 entirely — emitting it and reading it are both optional. | Publisher and APS: express every construct through an extension point of §4.7.1, and alter the semantics of no pre-existing construct. |
| **E13** | A beacon or a click-tracking request fails, or a beacon is scheduled for a moment the ad never reaches — past a trim boundary, or after a pause ad was dismissed on resume. | Leave the ad and the primary content unaffected; a beacon failure never reaches the viewer. Stop the remaining beacons at a trim boundary and from the pause-to-play transition onward. Fire each beacon once **per candidate** that carries it (§4.6.15). | Retry and log; the retry policy is implementation-defined. | APS: beacons as callback events on the ad's own presentation timeline (§4.5.6); the click and its tracking in the normative carrier (§4.5.8). ADS: owns which beacons exist and when. |
| **E14** | The document implies two non-linear forms at the same instant, or a pause begins inside a pause window while an overlay or a linear ad occupies the screen. | Keep at most one non-linear form active (§4.6.7): present sequenced forms one after another in declared order; during a pause suspend the overlay and render the pause ad whatever its surface, suspend a linear ad and resume it where it stopped, and restore the suspended form on resume only if its window is still open (§4.6.13). In live content keep the presentation time frozen for the pause, bounded by the time-shift buffer (§4.6.17). | Release the resources the primary content and a pre-existing overlay hold, to present a fullscreen pause ad. | APS: declare forms as a sequence, never as a concurrent composition. No actor has a construct that inverts the pause-over-overlay priority. |
| **E15** | The pause candidates are exhausted while the viewer is still paused, or the pause window was already consumed. | Apply the declared exhaustion behaviour, defaulting to `stop`; under `request-again`, treat a document with no candidates as `stop` for the rest of that pause; return to the primary content immediately on resume (§4.6.11). On a window declared `@executeOnce="true"`, present at most one pause ad for it and count the window consumed when a pause ad **begins rendering** (§4.6.12). | Report the applied behaviour. | APS: declare the behaviour on every pause document (§4.5.10). Publisher: declare the once-per-session bound where wanted, and the `PlayList` metric where pause windows exist (§4.3.8). |

#### 8.1.1 Two kinds of fall-through, and they are not the same

**Window-level** fall-through (E1 to E4) advances to the next
overlapping window of the family and reaches the primary content only
once the family is exhausted. **Candidate-level** fall-through (E7 to
E9) advances to the next candidate inside the document already
obtained and reaches the primary content once the candidates are
exhausted — never the next window, because a document carrying
candidates is not a failed execution.

Conflating the two is the most consequential mistake available here: it
either spends the Publisher's backup windows on a document that
answered, or strands a slot whose APS was unreachable.

#### 8.1.2 Order of precedence

Where several conditions arise on one exchange, they apply in this
order:

1. **Transport** (E1) — no document, so nothing downstream applies.
2. **Document level** (E2, E3, E4, E5) — unusable, misrouted, empty or
   late. All but E5 put the Player on the fallback chain.
3. **Constraint surfacing** (E6, E8, E9, and E10's drop-before-play) —
   the window's own declarations, validated before anything renders. E6
   precedes every other row, because a slot with no declared cap yields
   no ads at all.
4. **Per-candidate, at resolve time** (E7, E11) — what the device can
   satisfy and what the CDN delivers.
5. **Per-candidate, at playback time** (E10's trim, E14, E15) — the cap
   against actual length, the single-active-form bound, exhaustion
   inside a pause.
6. **Tracking** (E13) — non-fatal throughout.

E12 is orthogonal: an unknown construct is ignored wherever it appears,
at any level, and never advances the Player to the next step.

#### 8.1.3 What "continue with the primary content" means

No visible artefact: no freeze, no blank slate, no error overlay unless
the application explicitly opted in. No beacon fired for the
opportunity that failed. Primary-content playback continuing on its own
timeline. The viewer cannot tell an ad opportunity existed.

One part of that is normative rather than a matter of API shape: an
error overlay is a visible artefact, so rendering one on any row of
§8.1 breaks the guarantee unless the application asked for it.

### 8.2 Decision entries that carry tracking and no media

A decision entry with tracking and no creative cannot become a
candidate: there is nothing to render, and a candidate with no
presentation option is not a conformant candidate (§5.2.2.4). Whether
the APS drops the entry silently or signals the condition upstream is
APS-internal policy, agreed with the ADS (§6.7). The Player-visible
half is covered: if dropping the entry leaves the document with no
candidates, that is the empty resolution of §5.2.3, with the
consequences E4 states.

### 8.3 Late callbacks

A beacon whose scheduled time has already passed when the Player
establishes the ad's timeline — a late-starting replacement, a clock
adjustment — is a judgement call this specification does not make. Two
defensible policies: fire it immediately on the theory that the ad
reached that point, or drop it on the theory that the beacon's meaning
is tied to the instant. What is normative is the boundary: beacons past
a trim boundary are not fired, and beacons scheduled after a pause ad's
dismissal fall outside its active window (§4.6.15, §4.6.10).

### 8.4 Device-class fallbacks

The conservative posture is to treat an unverified capability as
absent. Three cases recur:

- **Re-tasking the decoder holding a paused frame.** A fullscreen pause
  ad can in principle reuse it, which is what makes a video pause ad
  reachable on a single-decoder class (§5.3.7.3). Whether a given
  device can do it, and what happens to the paused frame if it does, is
  a device property. A Player that has not verified the behaviour
  treats a video pause form as unsatisfiable and takes the next option.
- **HTML over video.** The difference between D3 and D4 is exactly
  this, and it is the axis most often mis-declared. A Player that
  cannot confirm it omits `sgaiHtmlOverlay` rather than sending `true`
  (§5.8.3).
- **Two decoders in principle, one in practice.** A device with a
  second decoder reserved by the platform, or unavailable under thermal
  pressure, is a one-decoder device for the duration. Declaring
  `sgaiVideoDecoders=1` under those conditions is more useful than
  declaring a capability the Player cannot deliver on.

The safety net in all three is §4.6.5: the Player checks every option
against its own device before rendering it, whatever it declared.

### 8.5 Resolving a pause slot: speculatively, or lazily

A pause-trigger window carries an `@earliestResolutionTimeOffset` like
any other slot, so the Player MAY resolve it at the ERT, before the
viewer has paused. It MAY equally resolve it at the moment of pause.
The trade-off is plain: resolving early means the ad is ready the
instant the viewer pauses and means requests for pauses that never
happen; resolving late means no wasted request and a visible delay
before the pause ad appears. This specification permits both.

Where the Player resolves early, the freshness question belongs to the
APS: a document produced minutes before the pause may carry a decision
the ADS would no longer make. An APS that cares about that keeps the
window short, or declares `request-again` so it gets a second chance
(§5.2.2.3).

### 8.6 An image form has no intrinsic duration

A `video` form's length is a property of its media. An `image` or
`html` form has none, so its `<svta:Candidate>@duration` is the whole
of what fixes how long it stays on screen, and the Player derives its
wall-clock length from it exactly as for a media-backed form (§4.6.14).
Two consequences follow. A candidate offering both a video option and
an image option declares one duration that applies to whichever the
Player picks. And the presentation timeline of an image or HTML form
starts at the first rendered frame of the asset, which is what the
relative beacon times are measured from (§5.5.3).

### 8.7 Degenerate authoring cases

| Case | What happens |
|---|---|
| A slot whose `@allowedLayouts` is empty | No option can match, so every candidate is skipped and the primary content continues. A validator SHOULD flag it. |
| A candidate whose `@duration` exceeds the slot cap on its own | Permitted; the Player MAY drop it before play, and trims it if it accepts it (§4.6.4). |
| A pause window whose `@allowedLayouts` lists only `pause-partial` on a device with no overlay surface | No option matches; the pause produces no ad and the window is not consumed (§4.6.12). |
| Two overlay windows at the same presentation time in one event stream | A chain of two, ordered by document position (§4.6.9). |
| An overlay window and a pause window at the same presentation time | Not a chain: different families, both live (§7.5.7). |
| A `ListMPD` whose Periods sum to less than the cap | Permitted; the cap is a maximum, not a target. |
| A candidate carrying a `<svta:Click>` and no options | Not conformant: at least one presentation option is required (§5.2.2.4). |

### 8.8 Validators and analytics pipelines

Three placements in this specification are conformant and novel
relative to where a tool would look for them by default, and each is a
place a pipeline silently misses data:

- A callback `<EventStream>` inside a `<svta:Candidate>` rather than
  inside a `<Period>` (§5.5.2).
- `<ImportedMPD>` inside `<svta:RenderableAsset>` rather than inside a
  `<Period>` (§5.3.4).
- `<svta:Click>` on a `ListMPD` `<Period>` for a linear ad (§5.6.1).

A validator that scans only canonical placements reports such a
document valid while having checked none of the three. A validation
report that means anything therefore states which subtrees it walked;
"valid" with the extension namespace skipped is a statement about the
validator, not about the document.

The profile-conformance procedure of DASH §8.1 is a second trap in the same
direction: run against a declared profile it removes the SGAI
constructs first (§4.7.8), so a profile-conformance pass says nothing
at all about them. That is by design and not a defect, but a report
that does not say so will be read as covering more than it does.

### 8.9 What `repeat` does to a candidate's beacons

De-duplication is scoped to the candidate (§4.6.15), so a candidate
presented twice under `@onCandidatesExhausted="repeat"` fires the
beacons that share an `@id` **once** across both presentations. An APS
reading `repeat` as buying a second impression would be surprised, and
the surprise is worth naming here because nothing in the document shape
signals it: `repeat` fills the remainder of a pause with material the
viewer has already seen, and what it buys is dwell time rather than a
second count. An APS that wants a second countable presentation carries
a second candidate, or declares `request-again` and answers with a
different one.

---

# Annexes

The annexes are **informative**. Each one walks a scenario through the
normative chapters and shows the documents the actors exchange; the
obligations themselves are in chapters 4 to 7.

## Annex A — Pre-roll (linear)

*Informative.*

### A.1 Scenario

The viewer starts playback of an on-demand title. The Publisher has
declared an ad opportunity at the very beginning of the session, before
the primary content begins: a linear slot capped at 20 seconds. One ad
takes over the screen, and when it finishes the primary content starts
from its first frame.

The content is on-demand, so the Publisher declares the opportunity
with `<InsertPresentation>` (§5.1.1): the ad consumes none of the
primary timeline, and the main timeline resumes where it was held. The
slot carries no list of admissible layouts, because the family already
fixes the presentation — a linear slot is a full-screen takeover and
the resolution document is a playlist of ads the ad decision server
already chose and ordered, not a candidate set the Player selects from
(§5.2.1). The Player resolves the slot's `@uri` against the ad
presentation server at session start and receives a `ListMPD` carrying
one Period.

### A.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S"
     publishTime="2026-09-17T09:00:00Z"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">

  <Period id="1" start="PT0S">

    <!-- Linear pre-roll: insertion, capped at 20 s -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="101" presentationTime="0" duration="20000">
        <InsertPresentation uri="https://aps.example.com/decision/preroll"
                            maxDuration="20000"
                            earliestResolutionTimeOffset="0"
                            executeOnce="true"/>
      </Event>
      <!-- Query template the Publisher wants on this slot's request -->
      <RequestParam includeInRequests="altmpd"
                    queryTemplate="session_id=$urn:mpeg:dash:state:cmcd#sid$"/>
    </EventStream>

    <!-- Primary content -->
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="video/init.mp4"
                       media="video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
      <Representation id="v2" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="audio/init.mp4"
                       media="audio/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="a1" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>

  <!-- Enables the urlparam:2025 scheme; the descriptor carries no content -->
  <EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025"/>
</MPD>
```

The Earliest Resolution Time is the event's `@presentationTime` minus
`@earliestResolutionTimeOffset`, which is `0 − 0 = 0`. A pre-roll sits
at the origin of the timeline, so there is no room ahead of it to give
the ad presentation server a head start: the Player resolves at session
start, before the first primary frame is rendered.

`@executeOnce="true"` bounds the slot to one execution per session, so
a viewer who restarts the title inside the same session sees the
primary content directly.

### A.3 Resolution request

```
GET https://aps.example.com/decision/preroll?session_id=a1b2c3d4
```

The Publisher's template supplied `session_id` and the Player
substituted the live value for the state variable (§5.8.1). The Player
attaches none of the reserved capability parameters of §5.8.2: every
presentation a linear slot can carry is a full-screen takeover, which
needs one decoder reused sequentially and no compositing surface at
all, so it is satisfiable on every device class (§5.3.7.3). Which
parameters travel is the Player's decision at runtime (§4.6.22), and
the ad presentation server produces candidates for a request carrying
none of them (§4.5.9).

### A.4 Resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xmlns:svta="urn:svta:dash:sgai:2026"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-09-17T09:00:02Z">

  <BaseURL>https://adcdn.example.com/delivery/</BaseURL>

  <Period id="ad_101" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="0">creative_101.mpd</ImportedMPD>
    <svta:Click clickThroughUrl="https://advertiser.example.com/landing?c=101">
      <svta:ClickTracking>https://tracker.example.com/click?ad=101</svta:ClickTracking>
    </svta:Click>
  </Period>

</MPD>
```

The ad declares 15 seconds against a 20-second cap, so the Player
presents it whole. `Period@duration` is declared in this document so
the Player can do the slot arithmetic before fetching the sub-MPD
(§5.2.1.1), and the cap is still enforced against actual rendered
length once the ad plays (§4.6.4).

On a linear slot the click carrier rides on the `ListMPD` `<Period>` of
the ad it belongs to (§5.6.1). A Player conformant to this
specification reads `@clickThroughUrl` there and fires the
click-tracking URL on activation (§4.6.16); a Player that predates this
specification discards the element with its subtree and plays the ad
with no click.

### A.5 Sub-MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S"
     publishTime="2026-09-17T09:00:02Z">

  <Period id="1" duration="PT15S">

    <!-- The tracking schedule the ad decision server declared -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=101</Event>
      <Event presentationTime="0"     id="2">https://tracker.example.com/start?ad=101</Event>
      <Event presentationTime="3750"  id="3">https://tracker.example.com/firstQuartile?ad=101</Event>
      <Event presentationTime="7500"  id="4">https://tracker.example.com/midpoint?ad=101</Event>
      <Event presentationTime="11250" id="5">https://tracker.example.com/thirdQuartile?ad=101</Event>
      <Event presentationTime="15000" id="6">https://tracker.example.com/complete?ad=101</Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2500"
                       initialization="creative_101/video/init.mp4"
                       media="creative_101/video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="2500"
                       initialization="creative_101/audio/init.mp4"
                       media="creative_101/audio/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="a1" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The sub-MPD is bound to the Single-Period Static profile: one Period
carrying `@duration`, no `@mediaPresentationDuration` and no
`@availabilityStartTime` (§5.4). The beacon times are relative to this
ad's own first frame (§5.5.3), so the quartiles of a 15-second ad sit
at 3 750, 7 500 and 11 250 in the carrier's millisecond timescale, and the
Player adds the ad's start position on the primary timeline to each
value to obtain the firing instant.

### A.6 Per-device-class behaviour

The device classes are those of §3.4: what separates them is how many
video decoders they run concurrently and which non-video surfaces they
composite over video.

| Class | What the Player renders | Why |
|---|---|---|
| D1 | The ad on one decoder, full screen, then the primary content. | The slot carries a takeover, so the second decoder and both compositing surfaces stay idle. The spare decoder may pre-buffer the ad while the session starts, which is a Player implementation choice. |
| D2 | Same as D1. | D2's missing capability is compositing a non-video surface over video, and a takeover composites nothing. |
| D3 | The ad on the single decoder, then the same decoder re-tasked for the primary content. | A linear ad and the primary content are sequential rather than concurrent, so one decoder suffices. |
| D4 | Same as D3. | The image-over-video surface D4 has and the HTML surface it lacks are both unexercised here. |
| D5 | Same as D3. | D5 declines every non-linear form, and this slot offers none: the full-screen takeover is the one presentation satisfiable on every class (§5.3.7.3). |

The outcome is uniform, and that is the annex's point. D5 is the class
that declines an overlay and a pause ad, and it takes this ad in full:
the capability a takeover asks for is a decoder it can use once the
primary content has stopped, which every class has. The classes differ
only in how much they can pre-buffer, which changes the transition's
smoothness and not what the viewer is shown.

## Annex B — Mid-roll (linear)

*Informative.*

### B.1 Scenario

The viewer is watching a live channel when the playhead reaches a
Publisher-declared opportunity six minutes into the presentation. The
slot replaces a 30-second span of the primary timeline: the ads take
over the screen, primary media time keeps advancing underneath them,
and when the break ends the Player resumes at the position
`@returnOffset` determines.

The content is live, so the Publisher declares the opportunity with
`<ReplacePresentation>` (§5.1.2): the insertion event addresses an
operation in which the playhead can be held for an indefinite period,
which is an on-demand operation, and it is not available on a
`dynamic` MPD. `@earliestResolutionTimeOffset` is one minute, so the
Player has the whole minute before the break to resolve the slot and
receive its `ListMPD`. The ad decision server filled the break with two
ads of 15 seconds each.

### B.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     type="dynamic"
     availabilityStartTime="2026-09-17T14:00:00Z"
     publishTime="2026-09-17T14:05:00Z"
     minimumUpdatePeriod="PT2S"
     timeShiftBufferDepth="PT1H"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:isoff-live:2011">

  <Period id="1" start="PT0S">

    <!-- Linear mid-roll: replacement of a 30 s span, capped at 30 s -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
                 timescale="1000">
      <Event id="102" presentationTime="360000" duration="30000">
        <ReplacePresentation uri="https://aps.example.com/decision/midroll"
                             maxDuration="30000"
                             earliestResolutionTimeOffset="60000"
                             returnOffset="0"
                             clip="true"
                             startWithOffset="false"/>
      </Event>
    </EventStream>

    <!-- Primary content -->
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000"
                       initialization="video/init.mp4"
                       media="video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
      <Representation id="v2" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true">
      <SegmentTemplate timescale="48000" duration="96000"
                       initialization="audio/init.mp4"
                       media="audio/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="a1" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The Earliest Resolution Time is `360000 − 60000 = 300000` in the event
stream's millisecond timescale — five minutes in. The Player picks an
instant between that and the event's `@presentationTime` and issues the
request then.

`@clip="true"` fixes the end of the break at the instant the Publisher
scheduled it: an execution that starts late is shortened rather than
running past the scheduled end (§4.6.4). `@startWithOffset="false"`
starts a delayed break from the first frame of its first ad instead of
skipping into it. `@returnOffset="0"` resumes the primary content at
the end of the replaced span.

### B.3 Resolution request

```
GET https://aps.example.com/decision/midroll?sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=false
```

This Player runs on a single-decoder device that composites still
images over video and no HTML, and it declares all three reserved
capability parameters on every resolution request it issues, whatever
the family of the slot (§5.8.2). The declaration is a statement about
the device, not a conclusion about which ad experiences are servable,
and deriving the second from the first is the ad presentation server's
work (§5.8.2). Here it changes nothing: a linear slot carries a
full-screen takeover, satisfiable on every device class, so the same
document is the correct answer to a request that declares these values
and to one that declares nothing at all.

A Player with no value for an axis, or that does not disclose it, omits
that parameter rather than sending it empty (§5.8.3), and its absence
means the value is undetermined rather than unsupported (§5.8.4).

### B.4 Resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xmlns:svta="urn:svta:dash:sgai:2026"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-09-17T14:05:12Z">

  <BaseURL>https://adcdn.example.com/delivery/</BaseURL>

  <Period id="ad_201" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="0">creative_201.mpd</ImportedMPD>
    <svta:Click clickThroughUrl="https://advertiser.example.com/landing?c=201">
      <svta:ClickTracking>https://tracker.example.com/click?ad=201</svta:ClickTracking>
    </svta:Click>
  </Period>

  <Period id="ad_202" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="15">creative_202.mpd</ImportedMPD>
    <svta:Click clickThroughUrl="https://advertiser.example.com/landing?c=202"/>
  </Period>

</MPD>
```

The two ads total 30 seconds against a 30-second cap, so both play in
full. Each `<Period>` is one ad, played back-to-back in declared order
(§5.2.1). The second `<ImportedMPD>` declares a 15-second pre-fetch
offset in seconds, so the Player fetches the second sub-MPD while the
first ad is on screen; that attribute is in seconds while the slot's
own offset is in event-stream timescale units, and the parent element
is what tells the two apart (§5.2.1.3).

The second ad carries a click destination and no click-tracking, which
is a complete declaration: the Player opens the destination on
activation and fires nothing (§5.6.1).

### B.5 Sub-MPD

The sub-MPD of the **second** ad, `creative_202.mpd`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S"
     publishTime="2026-09-17T14:05:12Z">

  <Period id="1" duration="PT15S">

    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=202</Event>
      <Event presentationTime="0"     id="2">https://tracker.example.com/start?ad=202</Event>
      <Event presentationTime="3750"  id="3">https://tracker.example.com/firstQuartile?ad=202</Event>
      <Event presentationTime="7500"  id="4">https://tracker.example.com/midpoint?ad=202</Event>
      <Event presentationTime="11250" id="5">https://tracker.example.com/thirdQuartile?ad=202</Event>
      <Event presentationTime="15000" id="6">https://tracker.example.com/complete?ad=202</Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2500"
                       initialization="creative_202/video/init.mp4"
                       media="creative_202/video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
      <Representation id="v2" bandwidth="1200000" width="854" height="480"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="2500"
                       initialization="creative_202/audio/init.mp4"
                       media="creative_202/audio/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="a1" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

This is the second ad of the break and its `complete` beacon sits at
15 000, not at 30 000: every beacon time inside a resolution document is
relative to the start of its own ad's presentation, never to the
primary timeline (§5.5.3). The Player adds the instant at which this
ad starts on the primary timeline to each relative value.

The Single-Period Static profile places the `Metrics` element outside
what an MPD at this level carries, so a Publisher that wants the
pause-delivery metric declares it on the primary MPD, which is the one
place it lives (§5.4, §5.9).

### B.6 Per-device-class behaviour

The device classes are those of §3.4.

| Class | What the Player renders | Why |
|---|---|---|
| D1 | Both ads full screen in declared order, then the live content from the resumption point. May pre-buffer the first ad on the spare decoder while the primary content plays its last frames. | The break is a takeover, so only one decoder is needed for presentation; the second one buys a smoother transition and nothing else. |
| D2 | Same as D1, pre-buffer included. | The slot declarations are device-agnostic, and the non-video compositing D2 lacks is unexercised by a takeover. |
| D3 | Both ads on the single decoder, sequentially with the primary content: the primary content stops, the ads play, the primary content resumes. No pre-buffering on a second decoder. | One decoder is enough because the ad and the primary content never render at the same instant. |
| D4 | Same as D3. | Same as D3; the difference between D3 and D4 is the HTML-over-video surface, which no takeover uses. |
| D5 | Same as D3. | Same as D3. A takeover needs no compositing surface, which is what makes it satisfiable on the class that declines every non-linear form. |

**Trick-play.** A viewer watching at 2× when the break triggers sees
the ads rendered at 2× as well: every ad form is rendered at the speed
the primary content is playing (§4.6.14), so the 30-second break
occupies 15 seconds of wall clock. The cap and the beacon schedule
operate on the presentation timeline and neither moves: the cap still
admits 30 000 units, and the `complete` beacon of each ad still fires at
presentation time 15 000 within that ad's own timeline.

## Annex C — Coexisting overlay (multi-form, multi-layout)

*Informative.*

### C.1 Scenario

The Publisher owns a 42-minute on-demand programme and sells one
non-linear opportunity ten minutes in. The opportunity is **coexisting**:
the primary content keeps playing throughout, and the ad is composited
over it — or alongside it — for a bounded interval, after which the frame
returns to the primary content alone. Nothing about the primary
presentation stops, seeks or resumes; the only thing the slot changes is
what else is on the screen.

The slot is sold into a population of devices whose compositing
capabilities differ, and neither the ADS nor the APS knows which device
will ask. The mechanism that absorbs that is the candidate's **ordered
list of presentation options**: one ad decision carries several
form-and-layout pairings in preference order, and each Player renders the
first pairing its own device satisfies and the window admits (§4.6.5).
This annex walks a single such decision across the five device classes of
§3.4 and shows each class landing on a different option. The APS in this
annex performs no narrowing (§7.3), so all five classes receive the same
document — which is what makes the five walks comparable.

### C.2 Main MPD

The Publisher declares the opportunity as one `<Event>` in an overlay
event stream, alongside the primary content's Adaptation Set. The window
opens at 10:00 on the primary timeline and lasts 30 seconds; the cap is
30 seconds of cumulative rendered non-linear presentation; the admitted
layouts are two corner-class placements, the three-element side-by-side,
and the full-screen takeover as the option of last resort.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT4S"
     publishTime="2026-09-14T08:00:00Z">

  <Period id="main" start="PT0S">

    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="301" presentationTime="600000" duration="30000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/overlay?slot=mid-1"
            maxDuration="30000"
            allowedLayouts="overlay-corner overlay-lower-third squeezeback-double-box-with-background linear"
            earliestResolutionTimeOffset="10000"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="540000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/seg-$Number$.m4s"/>
      <Representation id="v720"  bandwidth="2500000" width="1280" height="720"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>

  </Period>
</MPD>
```

Three values in that declaration carry the whole of the Publisher's
policy. `@maxDuration="30000"` is 30 seconds in the parent event stream's
timescale and bounds the cumulative rendered length of whatever this slot
presents (§4.6.4). `@allowedLayouts` is the closed list of tokens the
Player matches an option's `@layout` against, by exact token (§5.3.3);
`squeezeback-l-shape` is absent from it, so an L-shape option would be
passed over on every device. `@earliestResolutionTimeOffset="10000"`
places the Earliest Resolution Time at 09:50 on the primary timeline,
giving the APS ten seconds of head start before the window becomes
current.

### C.3 Resolution request

At or after the Earliest Resolution Time and at or before the window's
presentation time, the Player issues an HTTP GET against the slot's
`@uri`, appending whichever of the reserved capability parameters of
§5.8.2 it discloses. The request below is the one a D4 device sends — one
video decoder, an image surface over video, no HTML surface over video:

```
GET /decision/overlay?slot=mid-1&sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=false HTTP/1.1
Host: aps.example.com
Accept: application/dash+xml
```

The `slot=mid-1` parameter is part of the `@uri` the Publisher authored;
the three `sgai*` parameters are the Player's own, attached at its
discretion (§4.6.22). The other four classes send the same request with
the three values that identify them per §5.8.2 — and a Player that
discloses nothing sends the first parameter only, receiving the same
unnarrowed document (§5.8.4).

### C.4 Resolution document

The APS answers `200` with an Overlay Resolution Document. It carries two
candidates in the order the ADS decided. The first carries five
presentation options spanning three forms and three layouts; the second
carries two, both non-video.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T10:09:52Z">

  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>

      <svta:Candidate id="c1-brandx" duration="PT20S">

        <!-- option 1 -->
        <svta:RenderableAsset form="video"
                              layout="squeezeback-double-box-with-background">
          <svta:BackgroundElement assetUrl="https://adcdn.example.com/brandx/bands.png"/>
          <ImportedMPD earliestResolutionTimeOffset="8.0">https://adcdn.example.com/brandx/box-video.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <!-- option 2 -->
        <svta:RenderableAsset form="html"
                              layout="overlay-lower-third"
                              assetUrl="https://adcdn.example.com/brandx/lower-third.html"/>

        <!-- option 3 -->
        <svta:RenderableAsset form="video"
                              layout="overlay-corner">
          <ImportedMPD earliestResolutionTimeOffset="8.0">https://adcdn.example.com/brandx/corner-video.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <!-- option 4 -->
        <svta:RenderableAsset form="image"
                              layout="overlay-corner"
                              assetUrl="https://adcdn.example.com/brandx/corner.png"/>

        <!-- option 5 -->
        <svta:RenderableAsset form="video"
                              layout="linear">
          <ImportedMPD earliestResolutionTimeOffset="8.0">https://adcdn.example.com/brandx/takeover.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=brandx</Event>
          <Event presentationTime="5000"  id="2">https://tracker.example.com/firstQuartile?ad=brandx</Event>
          <Event presentationTime="10000" id="3">https://tracker.example.com/midpoint?ad=brandx</Event>
          <Event presentationTime="15000" id="4">https://tracker.example.com/thirdQuartile?ad=brandx</Event>
          <Event presentationTime="20000" id="5">https://tracker.example.com/complete?ad=brandx</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://brandx.example.com/offer">
          <svta:ClickTracking>https://tracker.example.com/click?ad=brandx</svta:ClickTracking>
          <svta:ClickTracking>https://thirdparty.example.net/c?id=brandx</svta:ClickTracking>
        </svta:Click>

        <svta:AdSystem value="example-ads"/>
        <svta:AdTitle value="BrandX — Autumn Range"/>
        <svta:Advertiser value="BrandX"/>
        <svta:UniversalAdId idRegistry="ad-id.org" value="BRX0451000H"/>

      </svta:Candidate>

      <svta:Candidate id="c2-brandy" duration="PT15S">

        <!-- option 1 -->
        <svta:RenderableAsset form="html"
                              layout="overlay-corner"
                              assetUrl="https://adcdn.example.com/brandy/corner.html"/>

        <!-- option 2 -->
        <svta:RenderableAsset form="image"
                              layout="overlay-lower-third"
                              assetUrl="https://adcdn.example.com/brandy/lower-third.jpg"/>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=brandy</Event>
          <Event presentationTime="15000" id="2">https://tracker.example.com/complete?ad=brandy</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://brandy.example.com/landing"/>

      </svta:Candidate>

    </svta:OverlayList>
  </Period>
</MPD>
```

Four properties of the document are worth naming before the walk.

The enclosing `<Period>` declares `duration="PT0S"` and carries no
Adaptation Set, which is what makes an MPD with no media of its own a
conforming carrier (§5.2.2.1). The candidates' order is the ADS's
decision and the Player presents them in it (§4.6.7); the options' order
inside a candidate is the preference order and the Player walks it
(§5.3.5). Each candidate's `@duration` is one value covering whichever
option the Player picks, including the image and HTML options, which have
no intrinsic length of their own (§8.6). And the first candidate's
tracking schedule sits directly inside `<svta:Candidate>` rather than in a
sub-MPD, because four of its five options have no sub-MPD to host it
(§5.5.2) — a validator that locates callback event streams by scanning
`<Period>` children alone does not see it at all (§8.8).

### C.5 Sub-MPD

Option 3 of the first candidate — the corner video overlay — reaches its
creative through `<ImportedMPD>`. The imported document is bound by the
base specification to the Single-Period Static profile (§5.4):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S">

  <Period id="brandx-corner" duration="PT20S">

    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=brandx</Event>
      <Event presentationTime="5000"  id="2">https://tracker.example.com/firstQuartile?ad=brandx</Event>
      <Event presentationTime="10000" id="3">https://tracker.example.com/midpoint?ad=brandx</Event>
      <Event presentationTime="15000" id="4">https://tracker.example.com/thirdQuartile?ad=brandx</Event>
      <Event presentationTime="20000" id="5">https://tracker.example.com/complete?ad=brandx</Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="1"
                       initialization="corner/init.mp4"
                       media="corner/seg-$Number$.m4s"/>
      <Representation id="a360" bandwidth="1200000" width="640" height="360"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The document carries no `@mediaPresentationDuration` and no
`@availabilityStartTime`; the single `<Period>` carries `@duration`
instead (§5.4). Its `@profiles` inherits the RFC 4337 constraint on
`Representation@mimeType`, which is the reason a still image or an HTML
creative travels on `@assetUrl` and never through this path (§4.7.2). The
`@codecs` value follows RFC 6381's lowercase hexadecimal production.

This sub-MPD repeats, verbatim, the schedule the candidate already
carries. The Player fires the **union** of the two carriers, and beacons
sharing an `@id` — or carrying the same URL at the same presentation time
— fire once (§4.6.15), so the viewer's device sends five requests and not
ten. The two placements are equivalent for a video form and an APS
authors either or both (§5.5.2).

### C.6 Per-device-class behaviour

Every class receives the document of §C.4 and walks the first candidate's
five options in document order. The outcome is read off the
decoder-and-surface budget of §5.3.7.3.

| Class | Capability declaration | Options passed over | Option rendered | On screen |
|---|---|---|---|---|
| **D1** | `sgaiVideoDecoders=2`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=true` | none | **1** — `video` / `squeezeback-double-box-with-background` | Primary content shrunk into one box, the ad video in the other, the advertiser's image filling the bands around them |
| **D2** | `sgaiVideoDecoders=2`, `sgaiImageOverlay=false`, `sgaiHtmlOverlay=false` | 1, 2 | **3** — `video` / `overlay-corner` | A second video composited in the corner of the playing primary content |
| **D3** | `sgaiVideoDecoders=1`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=true` | 1 | **2** — `html` / `overlay-lower-third` | An HTML lower-third band over the playing primary content |
| **D4** | `sgaiVideoDecoders=1`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=false` | 1, 2, 3 | **4** — `image` / `overlay-corner` | A static image in the corner of the playing primary content |
| **D5** | `sgaiVideoDecoders=1`, `sgaiImageOverlay=false`, `sgaiHtmlOverlay=false` | 1, 2, 3, 4 | **5** — `video` / `linear` | A full-screen takeover for the length of the candidate, then the primary content alone |

**D1** satisfies every row of §5.3.7.3, so document order alone decides
and the first option wins. The three-element side-by-side with a video ad
is the most demanding row in the table — two decoders plus an image
surface for the background — and D1 is the only class that carries it.

**D2** holds two decoders and still passes over option 1. The blocker is
the background element: it is an image surface, and D2 composites no
non-video surface at all (§5.3.7.3). Option 2 is HTML and fails on the
same axis. Option 3 asks for two decoders and no non-video surface, which
is exactly D2's shape, so the corner video renders on the second decoder
while the primary content holds the first.

**D3** passes over option 1 because a video creative in a side-by-side
needs a second decoder for the ad while the first holds the shrunk
primary content. Option 2 asks for one decoder plus an HTML surface over
video, and that is D3's definition, so the lower-third HTML creative
renders. Note that D3 reaches a **richer** form than D2 does on the same
document while owning half the decoders: the two classes differ on a
surface axis, not on a count.

**D4** differs from D3 in one respect and it decides two options. Option 2
is HTML and D4 composites no HTML over video, so it is passed over;
option 3 is video and D4 has one decoder, already presenting the primary
content. Option 4 asks for one decoder plus an image surface and renders.
The viewer never learns that an HTML rendering of the same ad existed.

**D5** satisfies none of the four non-linear options: no image surface, no
HTML surface, and a single decoder occupied by the primary content. Option
5 is the full-screen takeover, the one row of §5.3.7.3 satisfiable on every
class, because it composites nothing concurrently — one decoder, reused
sequentially across the ad and the primary content. That is what makes it
the useful last entry on an ordered list. Where a candidate's list ends
before offering it, D5 finds nothing satisfiable, the Player skips the
candidate and advances to the next (§4.6.6); declining an opportunity is a
defined outcome and not a failure.

**The second candidate, and the cap.** After the first candidate finishes,
the Player takes the second in declared order. D1 and D3 render its HTML
corner option, D4 its image lower-third option; D2 and D5 satisfy neither
option, skip the candidate, and — with the document's candidates now
exhausted — continue with the primary content alone (§4.6.6). The skip
does not advance any of them to another window: a document carrying
candidates is an answer, not a failed execution (§8.1.1).

The cap binds the classes that do render the second candidate. Twenty
seconds of the first candidate plus fifteen declared for the second is
35 seconds against a 30-second cap, so the Player either drops the second
candidate before playback on its declared duration alone, or accepts it and
stops rendering at the 30-second boundary — ten seconds into a fifteen-second
creative — and stops firing that candidate's remaining beacons at the trim
point (§4.6.4, §4.6.15). Drop-before-play on declared duration is permitted;
trim-during-play against actual rendered length is what the cap requires.

**Playback speed.** The ad renders at whatever speed the primary content is
playing. A 20-second candidate at 2× occupies ten seconds of wall clock,
while its beacons stay at 0, 5 000, 10 000, 15 000 and 20 000 on the ad's own
presentation timeline and the cap keeps counting presentation-timeline units
(§4.6.14).

## Annex D — Hybrid: a linear ad with a concurrent overlay

*Informative.*

### D.1 Scenario

The Publisher sells a mid-content break twenty minutes into a 42-minute
on-demand programme, and sells it twice over. A **linear** ad takes over
the primary content surface for the length of the break, and a
**non-linear** overlay is composited on top of that linear ad for part of
it — campaign branding, a second advertiser, a call to action. The two
portions occupy the same span of the primary timeline and are sold,
decided and resolved separately.

A hybrid break is authored as **two events at the same
`@presentationTime`** in two event streams, because they are two schemes
(§5.1.5). Nothing links them: the Player resolves the two `@uri` values
independently, receives two documents of two different families,
validates and selects from each on its own, and composes the results. A
Publisher restricting what may sit on top of a take-over expresses that
through the overlay event's own `@allowedLayouts`, and a Publisher
wanting no overlay during a take-over declares no overlay event at that
position. The break also stays inside the single-active-form bound of
§4.6.7: the linear ad is not a non-linear form, so one linear ad plus one
overlay is one non-linear form on screen.

### D.2 Main MPD

The linear portion uses replacement rather than insertion, so the primary
presentation timeline keeps advancing while the ad plays and the overlay
window — which is declared on that same timeline — elapses concurrently
with it.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT4S"
     publishTime="2026-09-14T08:00:00Z">

  <Period id="main" start="PT0S">

    <!-- the take-over portion -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
                 timescale="1000">
      <Event id="401" presentationTime="1200000" duration="60000">
        <ReplacePresentation
            uri="https://aps.example.com/decision/linear?slot=hybrid-1"
            maxDuration="60000"
            earliestResolutionTimeOffset="15000"/>
      </Event>
    </EventStream>

    <!-- the concurrent overlay portion -->
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="402" presentationTime="1200000" duration="60000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/overlay?slot=hybrid-1"
            maxDuration="15000"
            allowedLayouts="overlay-lower-third overlay-corner"
            earliestResolutionTimeOffset="15000"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="540000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/seg-$Number$.m4s"/>
      <Representation id="v720"  bandwidth="2500000" width="1280" height="720"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The two caps mean different things, and the difference is the base
specification's rather than this specification's. On the replacement
event `@maxDuration` bounds **until when**: with `@clip` at its default
`true` the alternative presentation terminates at the scheduled end of
the slot, so a late start shortens the linear ad rather than moving the
end of the break. On the overlay event `@maxDuration` bounds **how
long**, against the cumulative rendered length of the forms that slot
presents (§4.6.4). Fifteen seconds of overlay inside a sixty-second
take-over is therefore a deliberate asymmetry: the overlay is bounded
independently of, and more tightly than, the break it sits on.

The overlay's `@allowedLayouts` admits the two corner-class placements
and nothing else. No squeezeback token appears, because a layout that
shrinks the content surface has nothing coherent to shrink while a
take-over owns it; and `linear` does not appear either, since a
full-screen takeover on top of a full-screen takeover is not what the
Publisher is selling.

### D.3 Resolution request

The Player issues **two** GETs, one per slot, each at or after its own
Earliest Resolution Time — here 19:45 on the primary timeline for both.
The requests below are the pair a D3 device sends, one video decoder with
both an image and an HTML surface over video:

```
GET /decision/linear?slot=hybrid-1 HTTP/1.1
Host: aps.example.com
Accept: application/dash+xml
```

```
GET /decision/overlay?slot=hybrid-1&sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=true HTTP/1.1
Host: aps.example.com
Accept: application/dash+xml
```

The capability parameters of §5.8.2 travel on the non-linear request,
where a candidate carries alternatives for the Player to choose among. A
`ListMPD` is a playlist the ADS already selected and ordered, so there is
nothing for the parameters to narrow; a Player MAY attach them to either
request, and this one attaches them where they have an effect (§4.6.22).

### D.4 Resolution documents

The two answers are independent documents of two families, and either one
arriving unusable leaves the other unaffected.

**D.4.1 The linear answer — a `ListMPD`.** Two ads of thirty seconds each,
played back-to-back in declared order, summing to exactly the
sixty-second cap. A candidate whose converted duration equals the cap is
admitted (§4.6.4).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT2S"
     publishTime="2026-09-17T19:45:03Z">

  <Period id="ad-1" duration="PT30S">
    <ImportedMPD earliestResolutionTimeOffset="15.0">https://adcdn.example.com/brandp/spot-30.mpd</ImportedMPD>
    <svta:Click clickThroughUrl="https://brandp.example.com/offer">
      <svta:ClickTracking>https://tracker.example.com/click?ad=brandp</svta:ClickTracking>
    </svta:Click>
  </Period>

  <Period id="ad-2" duration="PT30S">
    <ImportedMPD earliestResolutionTimeOffset="15.0">https://adcdn.example.com/brandq/spot-30.mpd</ImportedMPD>
    <svta:Click clickThroughUrl="https://brandq.example.com/landing"/>
  </Period>

</MPD>
```

Each ad's tracking schedule lives inside its own sub-MPD `<Period>`
(§5.5.2). The ClickThrough travels as foreign-namespace open content on
the `ListMPD` `<Period>` of the ad it belongs to, which is a conformant
and novel placement: a pipeline that looks for click metadata only inside
the extension namespace's candidate element misses it here (§5.6.1,
§8.8). A client bound to the list profile alone is entitled to drop the
element, because a profile-conformance check removes every
extension-namespace element the declared profile does not explicitly
include (§4.7.8).

**D.4.2 The overlay answer — an Overlay Resolution Document.** One
candidate, three options, spanning three forms across the two admitted
layouts.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T19:45:04Z">

  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>

      <svta:Candidate id="c1-brandp-companion" duration="PT15S">

        <!-- option 1 -->
        <svta:RenderableAsset form="html"
                              layout="overlay-lower-third"
                              assetUrl="https://adcdn.example.com/brandp/band.html"/>

        <!-- option 2 -->
        <svta:RenderableAsset form="video"
                              layout="overlay-corner">
          <ImportedMPD earliestResolutionTimeOffset="10.0">https://adcdn.example.com/brandp/corner-15.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <!-- option 3 -->
        <svta:RenderableAsset form="image"
                              layout="overlay-corner"
                              assetUrl="https://adcdn.example.com/brandp/corner.png"/>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=brandp-companion</Event>
          <Event presentationTime="15000" id="2">https://tracker.example.com/complete?ad=brandp-companion</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://brandp.example.com/offer">
          <svta:ClickTracking>https://tracker.example.com/click?ad=brandp-companion</svta:ClickTracking>
        </svta:Click>

        <svta:AdSystem value="example-ads"/>
        <svta:AdTitle value="BrandP — companion band"/>
        <svta:Advertiser value="BrandP"/>

      </svta:Candidate>

    </svta:OverlayList>
  </Period>
</MPD>
```

The overlay's beacons sit on the **overlay's own** presentation timeline,
which starts when the overlay becomes visible — not when the break
started and not when the linear ad's first frame rendered (§5.5.3). The
two portions of the break therefore report independently, which is what
lets two different advertisers be billed for the same sixty seconds.

### D.5 Sub-MPD

Option 2 of the overlay candidate — the corner video — reaches its
creative through `<ImportedMPD>` into a document bound to the
Single-Period Static profile (§5.4):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S">

  <Period id="brandp-corner" duration="PT15S">

    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=brandp-companion</Event>
      <Event presentationTime="15000" id="2">https://tracker.example.com/complete?ad=brandp-companion</Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="1"
                       initialization="corner15/init.mp4"
                       media="corner15/seg-$Number$.m4s"/>
      <Representation id="a360" bandwidth="1000000" width="640" height="360"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The two linear ads' sub-MPDs have the same shape — one static Period with
`@duration`, the ad's Adaptation Set, and the ad's own callback event
stream inside that Period. The beacon identifiers repeated here are the
candidate's own, so the Player fires each once across the two carriers
(§4.6.15).

### D.6 Per-device-class behaviour

The linear portion resolves identically on every class: it takes over the
one decoder the primary content has just stopped using, so it asks for no
concurrency at all. The overlay portion is where the classes diverge, and
the budget it is measured against is the one in §5.3.7.3 — the same
budget as an overlay over primary content, because the take-over
**replaced** the primary content on that decoder rather than joining it
(§7.5.4).

| Class | Capability declaration | Options passed over | Option rendered | On screen |
|---|---|---|---|---|
| **D1** | `sgaiVideoDecoders=2`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=true` | none | **1** — `html` / `overlay-lower-third` | Full-screen linear ad with an HTML band across its lower third |
| **D2** | `sgaiVideoDecoders=2`, `sgaiImageOverlay=false`, `sgaiHtmlOverlay=false` | 1 | **2** — `video` / `overlay-corner` | Full-screen linear ad with a second video in the corner |
| **D3** | `sgaiVideoDecoders=1`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=true` | none | **1** — `html` / `overlay-lower-third` | Full-screen linear ad with an HTML band across its lower third |
| **D4** | `sgaiVideoDecoders=1`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=false` | 1, 2 | **3** — `image` / `overlay-corner` | Full-screen linear ad with a static image in the corner |
| **D5** | `sgaiVideoDecoders=1`, `sgaiImageOverlay=false`, `sgaiHtmlOverlay=false` | 1, 2, 3 | none | Full-screen linear ad alone |

**D1** satisfies every option and takes the first. Both portions render at
full fidelity.

**D2** passes over option 1 because an HTML surface over video is the one
thing its two decoders cannot buy it. Option 2 asks for a second video
decoder and no non-video surface: the linear ad holds one decoder, the
corner overlay takes the other. This is the case the class exists to
describe.

**D3** lands on the same option as D1 with half the decoders, and the
arithmetic is what makes that unsurprising. During the take-over the
device runs one video decoder — the linear ad on the decoder the primary
content released — leaving its HTML surface free. One decoder plus one
HTML surface is D3's definition, so the richest option on the list is
satisfiable. A reader expecting a single-decoder class to decline the
overlay portion of a hybrid break is carrying a budget of two decoders
where the base specification uses one.

**D4** differs from D3 on exactly one axis and that axis decides option 1:
D4 composites no HTML over video. Option 2 asks for a second decoder it
does not have. Option 3 asks for one decoder plus an image surface and
renders. The decline of the HTML option is a real device property and not
a decoder count.

**D5** satisfies none of the three options — no image surface, no HTML
surface, one decoder occupied by the linear ad. With the candidate's
options exhausted the Player skips the candidate, and with the document's
candidates exhausted it continues without an overlay (§4.6.6). The linear
portion is untouched by that outcome: it was resolved from a different
document, against a different window, and the overlay's absence is not a
failure of the break.

**If one portion fails to resolve.** The independence runs both ways. An
overlay request that times out, returns a non-`200`, returns something
that does not parse, or returns a well-formed document with no
candidates, puts the Player on the overlay family's fallback chain and,
with no further overlay window declared, leaves the linear ad playing
alone (§4.6.8). A linear request that fails the same way leaves the
overlay to composite over the primary content, which keeps playing
because the replacement never started. In neither direction does the
viewer see an artefact (§8.1.3).

## Annex E — Pause-triggered ad

*Informative.*

### E.1 Scenario

The Publisher of a 42-minute on-demand title has declared an interval
of the primary timeline during which a viewer pause permits an ad: from
ten minutes to twenty minutes in. A pause inside that interval triggers
a resolution request and, if the answer carries something the device can
render, an ad appears while playback stays paused. A pause outside the
interval permits nothing and produces no request.

The ad is presented either **fullscreen**, occupying the whole screen
surface, or as a **partial overlay** composited over the paused primary
frame, according to which layout token the option the Player selected
carries. The window declares both surfaces as admissible and leaves the
choice to the ordered options the answer carries. How long the pause
lasts is the viewer's, so the Publisher's cap bounds the display
duration of one ad rather than the slot; when the viewer resumes, the ad
leaves the screen within one rendering frame and the primary content
continues from the paused position.

### E.2 Main MPD

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

    <!-- pause-trigger window: 600 s .. 1200 s; one pause ad capped at 30 s -->
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-pause-trigger:2026"
                 timescale="1000">
      <Event id="501" presentationTime="600000" duration="600000">
        <svta:PauseAdPresentation
            uri="https://aps.example.com/decision/pause?slot=501"
            earliestResolutionTimeOffset="30000"
            maxDuration="30000"
            allowedLayouts="pause-fullscreen pause-partial"/>
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

  <!-- pause-delivery measurement is derived from this metric (§5.9) -->
  <Metrics metrics="PlayList" reportingInterval="PT60S">
    <Range starttime="PT0S"/>
  </Metrics>

</MPD>
```

Three parts of this document carry the scenario.

The `<Event>` declares the **window of validity** and nothing else. A
DASH event is dispatched when the playhead reaches its presentation
time, and a pause is the moment the playhead stops moving, so the
trigger sits on the Player side and fires on the pause transition inside
the window (§5.1.4). The window's `@duration` says where a pause
qualifies; it predicts no presentation and schedules none.

`@maxDuration="30000"` is 30 seconds in the parent event stream's
timescale, and on this family it bounds the display duration of **one**
pause ad before automatic dismissal (§4.6.4). The slot itself has no
declared length: the viewer sets it.

The `<Metrics>` element requests the `PlayList` metric on the primary
MPD, which is the obligation that attaches to content carrying pause
windows (§4.3.8). The quantity worth reporting on a pause slot is how
much of the paused interval carried an ad, and that interval is derived
from this metric's own fields — the end of a playback period whose last
rendered stretch stopped on `UserRequest`, up to the `start` of the next
entry whose `starttype` is `Resume` (§5.9). Collection is triggered from
the MPD, so the declaration is what makes the quantity collectable at
all. It lives on the primary MPD because the Single-Period Static
profile that binds every imported ad MPD forbids `MPD.Metrics`.

### E.3 Resolution request

The Player issues one GET against the slot's `@uri` when a pause begins
inside the window, and attaches whichever capability parameters it
discloses (§5.8.2):

```
GET https://aps.example.com/decision/pause?slot=501
      &sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=true
```

That declaration describes one video decoder, an image surface over
video and an HTML surface over video — the D3 class of §3.4. Sending the
parameters is the Player's runtime decision: a Player that discloses
none receives the candidates' options unnarrowed and resolves the choice
itself, which is the same document an APS emits when it holds no device
view (§5.8.4). The device checks every option against itself before
rendering it whatever it declared.

**When the request goes out is open by design.** The window carries
`@earliestResolutionTimeOffset="30000"`, so the ERT is presentation time
570 000 and the Player MAY resolve there — speculatively, before the
viewer has paused — or lazily at the moment of pause, as this walk does.
Resolving early has the ad ready the instant the viewer pauses and
spends requests on pauses that never happen; resolving late spends
nothing and shows a delay before the ad appears. Both are permitted, and
where the Player resolves early the freshness of the decision is the
APS's concern: an APS that cares keeps the window short, or declares
`request-again` so it gets a second chance (§8.5).

### E.4 Resolution document

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
     publishTime="2026-09-17T16:12:00Z">

  <Period id="resolution" duration="PT0S">
    <svta:OverlayList onCandidatesExhausted="repeat">

      <svta:Candidate id="cand-501-a" duration="PT30S">

        <!-- option 1: HTML card, partial overlay over the paused frame -->
        <svta:RenderableAsset form="html"
                              layout="pause-partial"
                              assetUrl="https://adcdn.example.com/501/card.html"/>

        <!-- option 2: still image, fullscreen -->
        <svta:RenderableAsset form="image"
                              layout="pause-fullscreen"
                              assetUrl="https://adcdn.example.com/501/card.png"/>

        <!-- option 3: video, fullscreen -->
        <svta:RenderableAsset form="video" layout="pause-fullscreen">
          <ImportedMPD earliestResolutionTimeOffset="5">https://adcdn.example.com/501/pause30.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=501a</Event>
          <Event presentationTime="15000" id="2">https://tracker.example.com/midpoint?ad=501a</Event>
          <Event presentationTime="30000" id="3">https://tracker.example.com/complete?ad=501a</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://advertiser.example.com/501">
          <svta:ClickTracking>https://tracker.example.com/click?ad=501a</svta:ClickTracking>
        </svta:Click>

        <svta:AdSystem value="example-ads"/>
        <svta:AdTitle value="Autumn campaign, pause card, 30s"/>
      </svta:Candidate>

      <svta:Candidate id="cand-501-b" duration="PT15S">

        <!-- option 1: still image, fullscreen -->
        <svta:RenderableAsset form="image"
                              layout="pause-fullscreen"
                              assetUrl="https://adcdn.example.com/501/house.png"/>

        <!-- option 2: video, partial overlay over the paused frame -->
        <svta:RenderableAsset form="video" layout="pause-partial">
          <ImportedMPD earliestResolutionTimeOffset="5">https://adcdn.example.com/501/house15.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=501b</Event>
          <Event presentationTime="15000" id="2">https://tracker.example.com/complete?ad=501b</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://advertiser.example.com/house"/>
      </svta:Candidate>

    </svta:OverlayList>
  </Period>
</MPD>
```

Four things in this document are worth pointing at.

`@onCandidatesExhausted` is declared explicitly. A pause slot has no
authored length, so the candidates can run out while the viewer is still
paused, and this attribute is what says what happens then: `repeat`
here, meaning the sequence is presented again from the start for as long
as the pause lasts (§4.6.11). The declaration belongs to the APS because
it is a property of this answer — what to do with *these* candidates
when they run out — and where it is absent the Player applies `stop`,
which is what the viewer would see if the mechanism did not exist.

The two candidates span both surfaces, and each carries its options as
an ordered list whose document order is the preference order (§5.3.5).
Between them the document offers an HTML partial overlay, a fullscreen
image, a fullscreen video, a second fullscreen image and a partial video
— five options across two candidates, emitted identically to every
viewer.

`cand-501-a` declares `PT30S`, which converts to exactly the window's
30 000-unit cap. A candidate whose converted duration equals the cap
exactly is admitted (§4.6.4).

The tracking event streams sit directly inside their candidates rather
than inside a sub-MPD, because the image and HTML options have no
sub-MPD to host them. Their presentation times are relative to the start
of the ad's own presentation, which for an image or an HTML form is the
first rendered frame of the asset (§5.5.3). A pipeline that locates
callback event streams by scanning `<Period>` children alone finds
neither of them (§5.5.2).

### E.5 Timeline

The walk below is a D3 device, which renders `cand-501-a`'s first
option. The pause begins at presentation time 742 000 and lasts 70
seconds of wall clock.

| Instant | What happens | Player |
|---|---|---|
| 0 .. 600 000 | Primary content plays; the window is not open | A pause here qualifies nowhere, so no resolution request is issued (§4.6.2) |
| 570 000 | ERT of the window | MAY resolve speculatively from here on; this Player does not (§8.5) |
| 742 000 | Viewer pauses, inside the window | Issues the resolution request, receives the document above |
| 742 000, +0 s | Pause transition | Presentation time stops at 742 000. Walks `cand-501-a`'s options and renders option 1, an HTML card composited over the paused frame, which stays visible around it |
| +0 s to +30 s | `cand-501-a` on screen | Fires the impression at offset 0, the midpoint at 15 s, the complete at 30 s, on the ad's own timeline established at the card's first rendered frame |
| +30 s | Cap reached for that ad | Dismisses `cand-501-a` and begins `cand-501-b`, the next candidate in declared order, whose fullscreen image replaces the paused frame on screen |
| +45 s | Candidates exhausted, viewer still paused | Applies the declared `repeat`: presents the sequence again from `cand-501-a` |
| +70 s | Viewer resumes | Removes the rendered form within one rendering frame, stops the beacons scheduled beyond the transition, and continues the primary content from 742 000 |
| 1 200 000 | Window closes | A later pause qualifies nowhere |

**Before the pause** the screen carries the primary content and nothing
else. **At the transition** exactly one ad form takes the screen, and it
is the first option that satisfies both the device and the window's
`@allowedLayouts`.

**During the pause** the two candidates run one after another in
declared order, each starting when the previous ends, and each bounded
by the 30-second cap on its own (§4.6.7, §4.6.4). At every instant one
form occupies the screen.

**When the candidates run out** the `repeat` declaration presents the
sequence again rather than clearing the surface. One consequence of the
repeat is worth naming: de-duplication is scoped to the candidate that
carries the beacons, so beacons sharing an `@id` inside `cand-501-a`
fire once across both of its presentations (§4.6.15).

**At resume** the ad leaves the screen within one rendering frame. The
second presentation of `cand-501-a` was 25 seconds in, so its complete
beacon at offset 30 000 falls after the pause-to-play transition and is
outside the ad's active window; the Player stops there (§4.6.10). The
primary content continues from 742 000, the position the viewer paused
at, and the viewer sees no artefact of the ad that was on screen.

### E.6 Per-device-class behaviour

Each class walks the same options in the same order and renders the
first that satisfies both its own decoder-and-surface budget (§5.3.7.3)
and the window's `@allowedLayouts`.

| Class | `cand-501-a` opt 1 — HTML, partial | opt 2 — image, fullscreen | opt 3 — video, fullscreen | `cand-501-b` | Renders | What the viewer sees |
|---|---|---|---|---|---|---|
| D1 | HTML surface over the paused frame: **satisfiable** | — | — | — | **A, opt 1** | A rich card over the paused frame, replaced after 30 s by the second ad, dismissed on resume |
| D2 | No non-video surface: fails | No image surface: fails | One decoder re-tasked from the paused frame, or a second decoder: **satisfiable** | — | **A, opt 3** | A fullscreen video ad, dismissed on resume |
| D3 | HTML surface over the paused frame: **satisfiable** | — | — | — | **A, opt 1** | As D1 |
| D4 | No HTML surface: fails | Image surface, paused frame released: **satisfiable** | — | — | **A, opt 2** | A fullscreen still image, dismissed on resume |
| D5 | No non-video surface: fails | No image surface: fails | Outside the class's budget for this form | Both options outside its budget | **nothing** | The paused frame stays on screen until the viewer resumes |

Three rows stop being obvious and are worth the prose.

**D2 owns two decoders and lands on the video option because of the
surfaces, not the decoders.** It composites no non-video content over
video at all, so the HTML card and the still image both fail, and the
fullscreen video is the first option it can satisfy. The rule that
selects here is element **type**, not element count.

**The decoder re-tasking question governs a fullscreen video pause ad on
a single-decoder class, and this walk never reaches it.** A fullscreen
video pause ad needs nothing of the primary content on screen, so in
principle the decoder holding the paused frame can be re-tasked to play
the ad — which is what makes the form reachable on D3 and D4 at all, and
the budget table admits it there conditionally (§5.3.7.3). Whether a
given device can do it, and what becomes of the paused frame if it does,
is a device property this specification leaves to the device. A Player
that has not verified the behaviour treats a video pause form as
unsatisfiable and takes the next option (§8.4). On D3 and D4 above the
HTML and image options win before option 3 is evaluated, so the question
does not arise; on a document offering only the video option it decides
the outcome. The caveat reaches `pause-fullscreen` and stops at
`pause-partial`, where the paused frame stays on screen and the decoder
holding it is in use.

**D5 declines the opportunity, and declining is a defined outcome.** It
composites nothing over video and its single decoder is outside the
budget for every form this document offers, so every option on both
candidates fails, the candidates are exhausted, and the paused frame
stays as the viewer left it. A pause window admits pause surfaces only,
so the full-screen takeover that rescues D5 on an overlay slot has no
token here. The primary content resumes from the paused position
untouched, and the viewer cannot tell an opportunity existed.

### E.7 The live variant

Where the same window is authored on live content, a pause runs against
a timeline that keeps advancing in wall-clock time while the viewer's
presentation time does not. The Player keeps its presentation time
**frozen** inside the window for the duration of the pause, and the
window is anchored to that frozen presentation time rather than to the
advancing live timeline, so the ad stays admissible for as long as the
viewer remains paused (§4.6.17). A decision to resume at the live edge
is a Player action occurring after the resume from pause, outside the
window.

**The freeze has a ceiling, and the base specification sets it.** The
drift a pause accumulates against a live presentation is bounded by the
time-shift buffer: the resumption time is clipped to that buffer, and
where it falls before the buffer's start the playhead is placed at the
oldest available media segment — the buffer's trailing edge. So a pause
that outlives `MPD@timeShiftBufferDepth` ends the freeze with the
buffer. At that boundary the Player dismisses the pause ad as it does on
any resume, stops its remaining beacons, and takes the resumption
position the base specification prescribes (§4.6.17).

The practical consequence for the Publisher is that the pause ad
experience on live content is bounded by a value declared elsewhere in
the manifest. A window of ten minutes on a presentation whose
`MPD@timeShiftBufferDepth` is `PT60S` gives a pause ad at most a minute
of admissibility, whatever the window says: a viewer who stays paused
longer comes back at the buffer edge with the ad already gone. A
Publisher who wants a longer pause ad experience declares a deeper
time-shift buffer. Every per-class outcome of §E.6 applies unchanged
inside that bound.

### E.8 Once-per-session

A Publisher who wants the window to yield one ad per session and no more
declares it on the window:

```xml
<EventStream xmlns="urn:mpeg:dash:schema:mpd:2011"
             xmlns:svta="urn:svta:dash:sgai:2026"
             schemeIdUri="urn:svta:dash:event:sgai-pause-trigger:2026"
             timescale="1000">
  <Event id="502" presentationTime="600000" duration="600000">
    <svta:PauseAdPresentation
        uri="https://aps.example.com/decision/pause?slot=502"
        earliestResolutionTimeOffset="30000"
        maxDuration="30000"
        executeOnce="true"
        allowedLayouts="pause-fullscreen pause-partial"/>
  </Event>
</EventStream>
```

The attribute carries the baseline name, default and semantics; what
changes is the trigger the counter observes. **The window is consumed
when a pause ad begins rendering, not when the pause occurs** (§4.6.12).
That distinction is the whole of the construct's behaviour, and it
separates three pauses that look identical from the viewer's side:

| First pause inside the window | Window after it |
|---|---|
| A pause ad begins rendering | **Consumed.** The window yields no further ad this session |
| The answer carries no candidates | **Available.** An attempt that produced no ad is a failed execution and is not counted as an execution (§4.6.8) |
| The answer carries candidates and the device satisfies no option on any of them | **Available.** Nothing began rendering |

The second row is the base specification's own counter rule: the counter
increments on a successful start rather than on an attempt, so a slot
that resolved to no ads leaves the opportunity executable. The third row
is the same rule read through the render event: a D5 device that declines
every option leaves the window untouched, and a later pause inside it is
served exactly as the first would have been.

**A second pause inside a consumed window.** Take the walk of §E.5 on a
window declared `@executeOnce="true"`. The viewer pauses at 742 000, an
ad renders, the window is consumed, and the viewer resumes at 742 000
with the primary content continuing. At presentation time 905 000 — still
inside the window, which runs to 1 200 000 — the viewer pauses again. The
Player presents no pause ad: the paused primary frame stays as the viewer
left it, the primary content continues uninterrupted on resume, and the
viewer sees the same thing they would see on a title carrying no pause
window at all.

The per-session bound is what separates this from the cap. The cap
bounds how long one ad stays on screen; `@executeOnce` bounds how many
times the window yields one. A window carrying both gives a viewer at
most one pause ad, for at most 30 seconds, however often they pause.

## Annex F — Multi-ad break

*Informative.*

### F.1 Scenario

The viewer is watching an on-demand title when the playhead reaches a
Publisher-declared break fifteen minutes in. The break is filled by
several ads played back-to-back with no primary content between them,
and after the last one the primary content resumes from where it was
held. The Publisher declares the break and its cap of 60 seconds; how
many ads run inside is the ad decision server's call, taken against its
own competitive-separation, frequency-capping and ordering logic, and
the cap is not its to respect (§4.4.3).

This annex exists for the arithmetic, which is where a multi-ad break
differs from a single-ad slot: the ad decision server returned 80.5
seconds of ads for a 60-second break, and the Player is the actor that
brings the sequence inside the cap (§4.6.4). The break is declared with
`<InsertPresentation>`, so it consumes none of the primary timeline.

### F.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S"
     publishTime="2026-09-17T11:00:00Z"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011">

  <Period id="1" start="PT0S">

    <!-- Multi-ad break at 15 min: insertion, capped at 60 s.
         The event stream's timescale is 1, so every value on it
         is in whole seconds. -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1">
      <Event id="601" presentationTime="900" duration="60">
        <InsertPresentation uri="https://aps.example.com/decision/pod"
                            maxDuration="60"
                            earliestResolutionTimeOffset="60"/>
      </Event>
    </EventStream>

    <!-- Primary content -->
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="video/init.mp4"
                       media="video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
      <Representation id="v2" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="audio/init.mp4"
                       media="audio/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="a1" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The Earliest Resolution Time is `900 − 60 = 840`, i.e. fourteen minutes
in: the Player resolves the break at any instant in the minute before
it starts. The cap and the offset are both in the event stream's own
timescale, which is what the candidates' ISO 8601 durations are
converted into before any comparison (§F.7).

### F.3 Resolution request

```
GET https://aps.example.com/decision/pod
```

The Publisher declared no query template on this slot and this Player
attaches no capability parameter: the break is a sequence of full-screen
takeovers, satisfiable on every device class (§5.3.7.3), so no axis of
§5.8.2 changes the answer. An ad presentation server produces candidates
for a request carrying none of the reserved parameters (§4.5.9).

### F.4 Resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xmlns:svta="urn:svta:dash:sgai:2026"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT1S"
     publishTime="2026-09-17T11:14:03Z">

  <BaseURL>https://adcdn.example.com/delivery/</BaseURL>

  <Period id="ad_601" duration="PT30S">
    <ImportedMPD earliestResolutionTimeOffset="0">creative_601.mpd</ImportedMPD>
    <svta:Click clickThroughUrl="https://advertiser.example.com/landing?c=601"/>
  </Period>

  <Period id="ad_602" duration="PT20.5S">
    <ImportedMPD earliestResolutionTimeOffset="30">creative_602.mpd</ImportedMPD>
    <svta:Click clickThroughUrl="https://advertiser.example.com/landing?c=602"/>
  </Period>

  <Period id="ad_603" duration="PT30S">
    <ImportedMPD earliestResolutionTimeOffset="50">creative_603.mpd</ImportedMPD>
    <svta:Click clickThroughUrl="https://advertiser.example.com/landing?c=603"/>
  </Period>

</MPD>
```

Three ads declaring 80.5 seconds for a 60-second break. Each
`<Period>` is one ad and the sequence is the order the ad decision
server chose (§5.2.1); the declared durations are what the Player reads
for the drop-before-play evaluation without fetching a single sub-MPD
first (§5.2.1.1). Each `<ImportedMPD>` carries a pre-fetch offset in
seconds, staggered so each sub-MPD is fetched while the previous ad is
on screen.

### F.5 Sub-MPD

The sub-MPD of the third ad, `creative_603.mpd` — the one the cap
reaches:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="urn:mpeg:dash:schema:mpd:2011 DASH-MPD.xsd"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S"
     publishTime="2026-09-17T11:14:03Z">

  <Period id="1" duration="PT30S">

    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=603</Event>
      <Event presentationTime="0"     id="2">https://tracker.example.com/start?ad=603</Event>
      <Event presentationTime="7500"  id="3">https://tracker.example.com/firstQuartile?ad=603</Event>
      <Event presentationTime="15000" id="4">https://tracker.example.com/midpoint?ad=603</Event>
      <Event presentationTime="22500" id="5">https://tracker.example.com/thirdQuartile?ad=603</Event>
      <Event presentationTime="30000" id="6">https://tracker.example.com/complete?ad=603</Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2500"
                       initialization="creative_603/video/init.mp4"
                       media="creative_603/video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
      <Representation id="v2" bandwidth="1200000" width="854" height="480"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true">
      <SegmentTemplate timescale="1000" duration="2500"
                       initialization="creative_603/audio/init.mp4"
                       media="creative_603/audio/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="a1" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The beacon times are relative to this ad's own first frame (§5.5.3), so
the quartiles of a 30-second creative sit at 7 500, 15 000 and 22 500 in
the carrier's millisecond timescale. Which beacons exist and where they
sit is the ad decision server's declaration, transcribed by the ad
presentation server (§4.5.6); §F.7 walks which of them the trim leaves
on the timeline.

### F.6 Per-device-class behaviour

The device classes are those of §3.4.

| Class | What the Player renders | Why |
|---|---|---|
| D1 | Each surviving ad full screen in declared order, switching the decoder source between them, then the primary content. May pre-buffer ad N+1 on the spare decoder while ad N plays. | A break is a sequence of takeovers, so one decoder carries the presentation; the second one smooths the joins between ads. |
| D2 | Same as D1, pre-buffer included. | The absence of non-video compositing is unexercised: nothing in the break is composited over anything. |
| D3 | The same sequence on the single decoder, re-tasked between each ad and again for the primary content. No pre-buffering on a second decoder. | Ads in a break are sequential rather than concurrent, so the joins are decoder re-tasks and not concurrent decodes. |
| D4 | Same as D3. | Same as D3. |
| D5 | Same as D3. | Same as D3; the full-screen takeover is the presentation satisfiable on every class (§5.3.7.3). |

The cap arithmetic of §F.7 is identical on all five classes: it runs on
declared and rendered durations, which carry no device dependency. What
the class changes is how many joins the Player can hide behind a
pre-buffer, and that is visible as smoothness rather than as a
different set of ads.

### F.7 Cap arithmetic

The cap is 60 units in the event stream's timescale of 1, i.e. 60
seconds. A candidate's duration arrives as an ISO 8601 duration, so the
Player converts each one into the cap's timescale before comparing, and
rounds the converted value **up** to the next whole unit (§4.6.4):

| Ad | Declared | Converted (round up) | Running total | Against the 60-unit cap |
|---|---|---|---|---|
| `ad_601` | `PT30S` | 30 | 30 | fits |
| `ad_602` | `PT20.5S` | 21 | 51 | fits |
| `ad_603` | `PT30S` | 30 | 81 | overruns by 21 |

The middle row is where the conversion earns its keep: 20.5 seconds is
not a whole unit at this timescale, so it is compared as 21. A
candidate whose converted duration lands exactly on the cap is admitted
(§4.6.4).

**Dropping before play.** The third ad's declared duration alone would
push the running total to 81, so the Player may drop it before playback
and present the first two (§4.6.4). The break then runs 50.5 seconds of
the 60 available, and the survivors keep the order the document
declared them in: the Player presents `ad_601` then `ad_602`, and the
room left over stays unused rather than being filled by promoting a
shorter later ad into it (§4.6.7).

**Trimming during play.** The Player may instead accept all three and
enforce the cap against **actual rendered length**, which is what it
does in every case whatever arithmetic it did beforehand. The first two
ads render 30 and 20.5 seconds, so 50.5 of the 60 units are spent when
the third begins; the third is on screen for 9.5 seconds and the Player
stops rendering at the cap, 20.5 seconds short of the creative's end.

The two figures differ on purpose. The prediction built from converted
durations left 9 units of room, and the enforcement against actual
length gives the third ad 9.5 seconds: rounding up makes the prediction
conservative, and the value the Player enforces is the measured one.
The same asymmetry covers a creative that renders longer than it
declared — an ad declaring `PT30S` that renders 32 seconds is trimmed at
the cap on the strength of the 32.

**The beacons at the trim boundary.** The third ad's schedule (§F.5) is
in its own millisecond timescale, so the trim at 9.5 seconds falls
between the `firstQuartile` beacon at 7 500 and the `midpoint` beacon at
15 000. The Player fires `impression` and `start` at offset 0 and
`firstQuartile` at 7 500, and stops firing at the trim boundary, so
`midpoint`, `thirdQuartile` and `complete` stay unfired — the ad never
reached the instants they name (§4.6.15). A beacon left unfired that
way has no effect on the ad or on the primary content, and the viewer
sees nothing of it (§8.1, row E13).

The primary content resumes at the instant the Player stops: the break
was declared as an insertion, so the main timeline was held for the
break's actual length and picks up where it paused, whether the cap was
reached by dropping the third ad or by trimming it.

## Annex G — A Player that predates this specification

*Informative.*

### G.1 Scenario

A Player built before this specification existed receives a manifest
that uses its constructs: a non-linear ad opportunity declared through
an event scheme the Player has never seen, carrying a foreign-namespace
element it has no schema for. The Player has no awareness of the
semantics and no way to acquire it at runtime.

This is the cross-cutting case every other scenario degrades to when the
viewer's Player is old. What the annex establishes is that the
degradation is silent: the construct is skipped, what remains of the
document parses, and primary-content playback continues without a
visible artefact. What the viewer sees *instead* of the ad is a separate
question, and it belongs to the Publisher (§G.5).

### G.2 A main MPD carrying an overlay window

Live content, one overlay opportunity at one hour into the presentation:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="dynamic"
     availabilityStartTime="2026-09-17T12:00:00Z"
     publishTime="2026-09-17T13:00:00Z"
     minimumUpdatePeriod="PT10S"
     timeShiftBufferDepth="PT1H"
     minBufferTime="PT4S">

  <Period id="p1" start="PT0S">

    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="701" presentationTime="3600000" duration="30000">
        <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay?slot=701"
                                  earliestResolutionTimeOffset="20000"
                                  maxDuration="15000"
                                  allowedLayouts="overlay-lower-third overlay-corner"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="video/init.mp4"
                       media="video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="audio/init.mp4"
                       media="audio/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="a1" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

Two constructs of this specification appear in it and nothing else does:
the `<EventStream>@schemeIdUri` that names the overlay family, and the
`<svta:OverlayPresentation>` element that carries the slot's
constraints. Every other element and attribute is baseline.

### G.3 The parser walk

1. **The `MPD` element.** `@profiles`, `@type`, `@availabilityStartTime`,
   `@minimumUpdatePeriod`, `@timeShiftBufferDepth` and `@minBufferTime`
   are all baseline and all recognised. The `xmlns:svta` declaration
   binds a prefix and asserts nothing; there is nothing in it to
   process.

2. **The first `<Period>` child — where the construct is first met.**
   The Player reaches `<EventStream>` and reads its `@schemeIdUri`. The
   value is not one it implements, so it skips the event stream together
   with every `<Event>` inside it. This is the baseline per-scheme rule
   and not a concession made for this specification: an event stream is
   something a client subscribes to by scheme, and one whose scheme is
   of no interest is ignored.

3. **The element inside the event, for a Player that descends anyway.**
   A Player that walks into the `<Event>` regardless finds
   `<svta:OverlayPresentation>` in a namespace it does not implement and
   discards the node with its whole subtree. It does not descend looking
   for children it might recognise, and the attributes on the discarded
   element — `@uri`, `@maxDuration`, `@allowedLayouts` — are never read.
   The outcome is the same by either route.

4. **What remains, and that it still parses.** The Player continues
   through the `<Period>` to the two `<AdaptationSet>` elements, which
   are baseline throughout: the segment templates, the codec strings,
   the bandwidths. It selects a Representation, fetches the
   initialisation segment and starts requesting media segments. The
   document it has in hand is a valid MPD by itself; removing the two
   SGAI constructs from it removes nothing any baseline element depended
   on.

5. **No resolution ever happens.** The Player never recognises that an
   opportunity exists, so it issues no resolution request. The APS is
   not called, the ADS is not consulted, no beacon fires, and no
   ClickThrough is read. The whole exchange this specification defines
   is absent rather than attempted and failed.

6. **Playback continues.** At one hour into the presentation the
   playhead crosses the declared window and nothing happens: no freeze,
   no blank frame, no error surface, no artefact of any kind. From the
   viewer's side the opportunity did not exist.

### G.4 The required-sibling check

The check that establishes the outcome above is mechanical, and a
Publisher can run it on any manifest:

1. Remove every element and every attribute in an extension namespace
   from the document.
2. Confirm the result validates against the base schema.
3. Confirm that every element a Player predating this specification
   needs is still in the result.

On the manifest of §G.2, step 1 removes exactly one element,
`<svta:OverlayPresentation>`. The `<EventStream>` and its `<Event>`
survive, because both are baseline elements — removal is by namespace,
and their namespace is the base one. The `<Event>` is left with no child
element, which the base schema admits: the foreign-namespace slot on
`EventType` is declared
`<xs:any namespace="##other" processContents="lax" minOccurs="0" maxOccurs="unbounded"/>`,
so zero children validate. It costs nothing in any case, since the
legacy Player had already skipped the whole stream on its unknown
scheme. Both Adaptation Sets are untouched. Step 2 passes, and step 3
passes because nothing a legacy Player needs was inside the element that
was removed.

Step 3 is the step that can fail, and it fails for one reason: a
baseline element that the legacy Player is expected to process, authored
**inside** an extension element. Removal by namespace removes an
element together with what it contains, so such a child goes away with
its parent and the legacy Player never sees it (§4.7.5). That is the
constraint the next subsection turns on.

### G.5 What the viewer sees instead, and who decides

The Player's own behaviour is fixed: skip and continue. What the viewer
experiences *around* the skipped construct is not fixed, and it is the
Publisher's authoring decision, taken per content type.

- **Live content.** The primary content continues uninterrupted and the
  opportunity is an expected loss on that Player. Live content cannot be
  held to splice in a baseline break without losing real content, so
  letting the Player keep playing the live edge is the outcome the
  Publisher takes. The manifest of §G.2 is that case: nothing was
  authored for the legacy population, and nothing is what it gets.
- **On-demand content.** The Publisher MAY author a baseline linear
  break alongside the non-linear declaration, using only constructs a
  legacy Player already renders. The legacy Player skips the construct
  it does not understand and plays the break it does, so the opportunity
  is monetised rather than lost. On-demand content is not bound to a
  live edge, so the break costs no real content.

The Publisher cannot read a viewer's Player version out of a manifest
request, which is why the on-demand fallback is authored
unconditionally: it is authored for everyone and consumed by the
population that recognises it.

### G.6 An on-demand manifest carrying both paths

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S"
     publishTime="2026-09-17T13:00:00Z">

  <Period id="p1" start="PT0S">

    <!-- The non-linear path. A Player implementing this specification
         resolves this window; a Player predating it skips the stream. -->
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="711" presentationTime="600000" duration="30000">
        <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay?slot=711"
                                  earliestResolutionTimeOffset="20000"
                                  maxDuration="15000"
                                  allowedLayouts="overlay-lower-third overlay-corner"/>
      </Event>
    </EventStream>

    <!-- The baseline break, authored as a SIBLING of the stream above.
         A Player predating this specification recognises this scheme
         and plays the break. -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025"
                 timescale="1000">
      <Event id="712" presentationTime="600000" duration="15000">
        <InsertPresentation uri="https://aps.example.com/decision/linear?slot=712"
                            earliestResolutionTimeOffset="20000"
                            maxDuration="15000"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="video/init.mp4"
                       media="video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="audio/init.mp4"
                       media="audio/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="a1" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

**The baseline break is a sibling, and the placement is the whole
point.** The `<EventStream>` carrying `<InsertPresentation>` sits next to
the SGAI event stream, at a baseline position inside the `<Period>`, and
`<InsertPresentation>` itself is a baseline element inside a baseline
event. Every element on the legacy path is in the base namespace from
the `<Period>` down.

Nesting the break inside `<svta:OverlayPresentation>` — as a child of the
extension element, to express that it belongs to the same opportunity —
would produce the opposite of what it looks like. A legacy Player
discards a foreign-namespace element with everything it contains, so the
break would be discarded with the element that was supposed to describe
it, and the one population it was authored for would be the one
population that never sees it. The check of §G.4 catches exactly this:
remove the extension namespace and the break disappears, so step 3
fails. Authored as a sibling, the break survives that removal, which is
what makes it visible.

Two consequences of authoring both are worth stating. A Player
implementing this specification recognises **both** schemes, and two
events at one presentation time in two schemes are the hybrid slot of
§5.1.5 — a linear break with a concurrent overlay — rather than a pair
from which one is chosen; this specification carries no construct that
marks a baseline break as legacy-only. A Publisher that wants the two
populations to diverge instead of compose therefore has two options and
not three: author the break and accept the hybrid on current Players, or
author no break and accept the loss on legacy ones.

### G.7 The outcome does not vary by device class

Behaviour is identical on D1 through D5, because what determines it is
the Player's vintage and the content type, not the device's decoder or
surface budget: a legacy Player issues no resolution request on any
hardware, so nothing that distinguishes the classes is ever consulted. A
top-tier device running a legacy Player produces the same screen as a
worst-case device running one.

## Annex H — An overlay window crossing a pause-trigger window

*Informative.*

### H.1 Scenario

An overlay ad is on screen, composited over primary content that keeps
playing, when the viewer pauses — and the pause falls inside a
pause-trigger window the Publisher declared across the same stretch of
the timeline. Two opportunities of two **different** families are valid
at the same instant. Overlapping windows of one family form a fallback
chain, where the later windows are reached only when an attempt produces
no ad; windows of different families are not a chain, and both are live
(§7.5.7).

What the viewer sees is decided by priority rather than by order. While
the viewer is paused inside the pause-trigger window the pause ad is the
only ad surface visible: the overlay is suspended for the duration of
the pause, and on resume the pause ad leaves the screen and the overlay
returns if its own window is still open (§4.6.13). The priority holds
whatever surface the pause ad takes — a partial pause ad keeps the
paused primary frame visible around it and the overlay stays suspended
behind both — so at every instant exactly one non-linear form occupies
the screen (§4.6.7). No construct in this specification lets the
Publisher, the ADS or the APS invert it.

### H.2 Main MPD

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

    <!-- overlay window: 300 s .. 330 s; cap 15 s of rendered length -->
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="801" presentationTime="300000" duration="30000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/overlay?slot=801"
            earliestResolutionTimeOffset="10000"
            maxDuration="15000"
            allowedLayouts="overlay-lower-third overlay-corner"/>
      </Event>
    </EventStream>

    <!-- pause-trigger window: 240 s .. 420 s, spanning the overlay window -->
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-pause-trigger:2026"
                 timescale="1000">
      <Event id="802" presentationTime="240000" duration="180000">
        <svta:PauseAdPresentation
            uri="https://aps.example.com/decision/pause?slot=802"
            earliestResolutionTimeOffset="30000"
            maxDuration="45000"
            allowedLayouts="pause-fullscreen pause-partial"/>
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

  <!-- pause-delivery measurement is derived from this metric (§5.9) -->
  <Metrics metrics="PlayList" reportingInterval="PT60S">
    <Range starttime="PT0S"/>
  </Metrics>

</MPD>
```

The two windows sit in **separate event streams**, because they are
separate schemes and all the windows of one family inside a Period are
clustered in a single stream of that family's scheme (§4.3.4). They
overlap in time on purpose: the pause-trigger window runs from 240 s to
420 s and the overlay window from 300 s to 330 s, so every instant the
overlay is valid is also an instant at which a pause qualifies.

Each window carries its own declarations and binds what it serves with
them (§4.6.9). The overlay window admits two overlay placements and caps
rendered length at 15 seconds inside a 30-second window; the
pause-trigger window admits both pause surfaces and caps one pause ad at
45 seconds. Neither inherits anything from the other.

The `<Metrics>` element requests the `PlayList` metric on the primary
MPD, which is what content carrying pause windows declares (§4.3.8). The
paused interval is derived from its fields, and the fraction of that
interval an ad occupied is the figure a pause slot is worth measuring by
(§5.9).

### H.3 Resolution request

Two slots, two independent requests. The Player resolves each against
its own `@uri` and validates each answer against the window that served
it.

```
GET https://aps.example.com/decision/overlay?slot=801
      &sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=true

GET https://aps.example.com/decision/pause?slot=802
      &sgaiVideoDecoders=1&sgaiImageOverlay=true&sgaiHtmlOverlay=true
```

The capability parameters describe one video decoder, an image surface
over video and an HTML surface over video — the D3 class of §3.4 — and
travel on both requests here because they describe the device rather
than the slot (§5.8.2). Attaching them is the Player's runtime decision:
a Player that discloses none receives every option the ADS returned and
resolves the choice itself (§5.8.4).

The overlay request goes out at or after the overlay window's ERT,
presentation time 290 000, and at or before the window's presentation
time. The pause request has the timing freedom of its family: the
pause-trigger window's ERT is 210 000, so the Player MAY resolve there
speculatively, before the viewer has paused, or lazily at the moment of
pause as this walk does. Resolving early has the ad ready the instant
the viewer pauses and spends requests on pauses that never happen;
resolving late spends nothing and shows a delay before the ad appears
(§8.5).

### H.4 Resolution documents

#### The overlay document

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
     publishTime="2026-09-17T16:04:50Z">

  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>

      <svta:Candidate id="cand-801" duration="PT15S">

        <!-- option 1: HTML lower third -->
        <svta:RenderableAsset form="html"
                              layout="overlay-lower-third"
                              assetUrl="https://adcdn.example.com/801/third.html"/>

        <!-- option 2: image corner overlay -->
        <svta:RenderableAsset form="image"
                              layout="overlay-corner"
                              assetUrl="https://adcdn.example.com/801/corner.png"/>

        <!-- option 3: video lower third -->
        <svta:RenderableAsset form="video" layout="overlay-lower-third">
          <ImportedMPD earliestResolutionTimeOffset="5">https://adcdn.example.com/801/third.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=801</Event>
          <Event presentationTime="7500"  id="2">https://tracker.example.com/midpoint?ad=801</Event>
          <Event presentationTime="15000" id="3">https://tracker.example.com/complete?ad=801</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://advertiser.example.com/801">
          <svta:ClickTracking>https://tracker.example.com/click?ad=801</svta:ClickTracking>
        </svta:Click>
      </svta:Candidate>

    </svta:OverlayList>
  </Period>
</MPD>
```

`<svta:OverlayList>` carries no `@onCandidatesExhausted` here. The
attribute governs what happens when the candidates run out while the
viewer is still paused, and an overlay slot ends with its own window, so
the attribute is inert on an overlay document (§5.2.2.3).

#### The pause document

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
     publishTime="2026-09-17T16:05:12Z">

  <Period id="resolution" duration="PT0S">
    <svta:OverlayList onCandidatesExhausted="stop">

      <svta:Candidate id="cand-802-a" duration="PT20S">

        <!-- option 1: HTML card, partial overlay over the paused frame -->
        <svta:RenderableAsset form="html"
                              layout="pause-partial"
                              assetUrl="https://adcdn.example.com/802/card.html"/>

        <!-- option 2: still image, fullscreen -->
        <svta:RenderableAsset form="image"
                              layout="pause-fullscreen"
                              assetUrl="https://adcdn.example.com/802/card.png"/>

        <!-- option 3: video, fullscreen -->
        <svta:RenderableAsset form="video" layout="pause-fullscreen">
          <ImportedMPD earliestResolutionTimeOffset="5">https://adcdn.example.com/802/pause20.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=802a</Event>
          <Event presentationTime="10000" id="2">https://tracker.example.com/midpoint?ad=802a</Event>
          <Event presentationTime="20000" id="3">https://tracker.example.com/complete?ad=802a</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://advertiser.example.com/802"/>

        <svta:AdSystem value="example-ads"/>
        <svta:AdTitle value="Autumn campaign, pause card, 20s"/>
      </svta:Candidate>

      <svta:Candidate id="cand-802-b" duration="PT10S">

        <!-- option 1: still image, partial overlay over the paused frame -->
        <svta:RenderableAsset form="image"
                              layout="pause-partial"
                              assetUrl="https://adcdn.example.com/802/house.png"/>

        <!-- option 2: video, partial overlay over the paused frame -->
        <svta:RenderableAsset form="video" layout="pause-partial">
          <ImportedMPD earliestResolutionTimeOffset="5">https://adcdn.example.com/802/house10.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=802b</Event>
          <Event presentationTime="10000" id="2">https://tracker.example.com/complete?ad=802b</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://advertiser.example.com/house"/>
      </svta:Candidate>

    </svta:OverlayList>
  </Period>
</MPD>
```

`@onCandidatesExhausted="stop"` is declared explicitly even though it is
the value the Player applies when the attribute is absent. Declaring it
states the choice rather than leaving a reader to resolve a default, and
`stop` is the value every Player can perform: it shows the paused
primary frame, which is what the viewer would see if the mechanism did
not exist (§5.2.2.3).

The two candidates span both pause surfaces — a partial HTML card, a
fullscreen image, a fullscreen video, a partial image, a partial video —
and each carries its options in preference order (§5.3.5).

### H.5 Timeline

The walk below is a D3 device. The overlay renders `cand-801`'s HTML
lower third; the pause ad renders `cand-802-a`'s HTML card. The viewer
pauses at presentation time 312 000 and stays paused for 55 seconds of
wall clock.

| Instant | What happens | Player |
|---|---|---|
| 210 000 | ERT of the pause-trigger window | MAY resolve the pause slot speculatively from here on; this Player does not (§8.5) |
| 290 000 | ERT of the overlay window | Resolves the overlay slot and receives the overlay document |
| 300 000 | Overlay window opens | Walks `cand-801`'s options and renders option 1, the HTML lower third, over primary content that keeps playing. The 15-second cap begins accruing on the presentation timeline |
| 300 000 .. 312 000 | Overlay on screen for 12 s | Fires the overlay's impression at offset 0 and its midpoint at 7 500 |
| 312 000 | Viewer pauses, inside the pause-trigger window | Suspends the overlay, issues the pause resolution request, and renders `cand-802-a`'s option 1 over the paused frame. Presentation time stops at 312 000, so the overlay's cap holds at 12 s consumed and 3 s remaining, and its window holds at 18 s remaining |
| +0 s to +20 s of pause | `cand-802-a` on screen | Fires its beacons on the ad's own timeline, established at the card's first rendered frame |
| +20 s | `cand-802-a` ends | Begins `cand-802-b`, the next candidate in declared order, whose partial image replaces the card |
| +30 s | Candidates exhausted, viewer still paused | Applies the declared `stop`: presents no further ad, and the paused primary frame is shown. The overlay stays suspended — the pause has not ended |
| +55 s | Viewer resumes | Stops the pause ad's beacons from the transition onward, resumes the primary content from 312 000, and restores the overlay: its window runs to 330 000 and is still open, with 3 s of cap remaining |
| 315 000 | Overlay cap reached | Removes the overlay, 15 s of rendered length in total |
| 330 000 | Overlay window closes | Nothing remains to remove |

Four points in that walk carry the composition rules.

**The overlay's clock follows the presentation timeline, and the
presentation timeline does not advance while the viewer is paused.** Cap
arithmetic runs on that timeline, so an interval during which it does
not advance accrues nothing against the cap: a form suspended while the
viewer is paused resumes with the remaining cap it had when it was
suspended (§4.6.4). The overlay consumed 12 of its 15 seconds before the
pause and comes back with 3, however long the pause lasted. The viewer
loses no overlay time to the pause.

**The window and the cap are two different bounds and both survive the
pause.** The overlay's window ends at 330 000 and its cap allows 15
seconds of rendered length; here the cap binds first, at 315 000, so the
overlay leaves the screen 15 seconds of presentation time before its
window closes. A window with a longer cap would have had the window bind
instead.

**Exhausting the pause candidates does not end the pause, and does not
restore the overlay.** At 30 seconds into the pause the document has
nothing left to present and `stop` clears the ad surface, leaving the
paused primary frame. The overlay stays suspended for the remaining 25
seconds: it is suspended for the duration of the pause and restored on
resume (§4.6.13), and the pause is still running.

**At every instant of the pause exactly one ad form occupies the
screen**, and on this device it is a partial one — the paused primary
frame stays visible around the HTML card, and the overlay is suspended
behind both. A partial pause ad does not put two forms on screen, which
is what keeps the priority and the one-active-form bound consistent with
each other (§4.6.13).

#### When the overlay window closed during the pause

The walk above restores the overlay because its window was still open at
the moment of resume. Where the window closed while the viewer was
paused, the Player leaves the overlay surface clear on resume
(§4.6.13).

Reaching that branch takes a mechanism, because on on-demand content the
presentation time a window is measured against does not advance while
the viewer is paused: a pause at 329 000 holds the overlay's remaining
second indefinitely, and the window closes only when presentation time
reaches 330 000, which happens after the resume. The branch is reached
on **live** content, through the bound the base specification puts on
the freeze. The Player keeps its presentation time frozen inside the
pause-trigger window for the duration of the pause (§4.6.17), and that
freeze is limited by the time-shift buffer: where the pause outlives
`MPD@timeShiftBufferDepth` the resumption position is clipped to the
buffer and placed at the oldest available media segment.

So on a live presentation whose `MPD@timeShiftBufferDepth` is `PT60S`, a
viewer who pauses at 329 000 with one second of overlay window left and
stays paused for five minutes resumes at the buffer's trailing edge,
which lies past 330 000. The overlay window closed while the viewer was
paused. The Player dismisses the pause ad as it does on any resume,
stops its remaining beacons, leaves the overlay surface clear, and
continues the primary content from the position the base specification
prescribes. The overlay terminated because its window ended, which is
how an overlay window always ends.

### H.6 Per-device-class behaviour

Both documents are emitted identically to every viewer. Each class walks
the same options in the same order and renders the first that satisfies
both its own decoder-and-surface budget (§5.3.7.3) and the
`@allowedLayouts` of the window that served the candidate.

| Class | During play | On pause | When the pause candidates run out | On resume |
|---|---|---|---|---|
| D1 | HTML lower third — `cand-801` opt 1 | Overlay suspended; HTML card over the paused frame — `cand-802-a` opt 1 | Paused frame shown; overlay stays suspended | Pause ad dismissed, overlay restored for the remainder of its cap and window |
| D2 | Video lower third — `cand-801` opt 3 | Overlay suspended; fullscreen video — `cand-802-a` opt 3 | Paused frame shown; overlay stays suspended | Pause ad dismissed, video overlay restored with its remaining cap |
| D3 | HTML lower third — `cand-801` opt 1 | Overlay suspended; HTML card over the paused frame — `cand-802-a` opt 1 | Paused frame shown; overlay stays suspended | As D1 |
| D4 | Image corner overlay — `cand-801` opt 2 | Overlay suspended; fullscreen image — `cand-802-a` opt 2 | Paused frame shown; overlay stays suspended | Pause ad dismissed, image overlay restored with its remaining cap |
| D5 | Overlay declined | Pause ad declined; paused frame stays as the viewer left it | Nothing to run out of | Primary content continues; nothing to restore |

Four rows need the prose.

**D2 renders both forms and reaches each of them through its decoders
rather than through a surface.** It composites no non-video content over
video, so the HTML lower third and the image corner overlay both fail
and the video lower third is the first overlay option it can satisfy —
two decoders, one for the primary content and one for the ad. On the
pause document the same elimination runs: the partial HTML card and the
fullscreen image need surfaces D2 lacks, and the fullscreen video is
satisfiable. The rule doing the work in both walks is element **type**,
not element count.

**D4 takes a corner overlay during play and a fullscreen image during
the pause, from two different candidates' option lists.** It composites
images over video and not HTML, so the lower third fails on the overlay
document and the HTML card fails on the pause document; the image option
follows in each. The two ads sit on different surfaces because the
options the APS ordered put them there, not because the device treats
the two families differently.

**The decoder re-tasking caveat governs the fullscreen video pause ad,
and no walk above reaches it.** A fullscreen video pause ad needs
nothing of the primary content on screen, so the decoder holding the
paused frame can in principle be re-tasked to play it — which is what
makes the form reachable on a single-decoder class at all, and the
budget table admits it on D3 and D4 conditionally (§5.3.7.3). Whether a
given device can do it is a device property, and a Player that has not
verified the behaviour treats a video pause form as unsatisfiable and
takes the next option (§8.4). On D3 and D4 above the HTML and image
options win first, so the question does not arise. The caveat reaches
`pause-fullscreen` and stops at `pause-partial`: a partial pause ad
keeps the paused frame on screen, so the decoder holding that frame is
in use and `cand-802-b`'s partial video option stays outside a
single-decoder budget.

**On D5 the priority rule is moot, and both opportunities are declined.**
The device composites nothing over video and its single decoder is
outside the budget for every option both documents offer, so the overlay
window yields nothing during play and the pause window yields nothing
during the pause. With no overlay to suspend and no pause ad to give
priority to, the viewer's pause and resume have no ad-related effect:
the primary content plays, the paused frame stays clean, and playback
continues from the paused position. Declining is a defined outcome
rather than a failure, and the viewer cannot tell either opportunity
existed.

## Annex I — One ad, ordered options, resolved across the device classes

*Informative.*

### I.1 Scenario

One non-linear candidate is offered for an overlay slot. It carries
four presentation options as an ordered list, and document order is the
preference order (§5.3.5). The ADS emits the **same** ordered list to
every viewer, and the Publisher declares **one device-agnostic
allowed-layout set**: there is no per-device-class variant anywhere in
the manifest or in the resolution document.

The per-class outcome is therefore not authored upstream. It emerges at
the Player, when each device walks the same four options and renders
the first one it can satisfy on its own hardware and whose layout the
window admits (§4.6.5). This annex is the worked example of that
emergence, and it answers the question of whether the Publisher ought
to declare layouts per device class: the ordered list plus one
device-agnostic allowed-layout set already produces the right layout on
each class, with no actor upstream of the Player holding a device-class
matrix.

In this annex the Player discloses nothing about its device on the
resolution request, so the APS answers unnarrowed (§4.5.9, §5.8.4).
Annex M is the same ad — same options, same order, same creatives and
the same declared duration — with the Player declaring its
capabilities and the APS resolving the choice; every class lands on the
same rendered result.

### I.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S">
  <Period id="1" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="901" presentationTime="480000" duration="20000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/overlay?slot=901"
            maxDuration="15000"
            allowedLayouts="squeezeback-double-box-with-background squeezeback-l-shape overlay-lower-third linear"
            earliestResolutionTimeOffset="15000"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1" par="16:9">
      <SegmentTemplate timescale="90000" duration="360000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/seg-$Number$.m4s"/>
      <Representation id="v-1080" bandwidth="5000000"
                      width="1920" height="1080" sar="1:1"/>
      <Representation id="v-720" bandwidth="2500000"
                      width="1280" height="720" sar="1:1"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true">
      <AudioChannelConfiguration
          schemeIdUri="urn:mpeg:dash:23003:3:audio_channel_configuration:2011"
          value="2"/>
      <SegmentTemplate timescale="48000" duration="192000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/seg-$Number$.m4s"/>
      <Representation id="a-128" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

One window, one allowed-layout set, four admitted tokens. The window
opens 480 s into the programme and stays open for 20 s; the cap admits
15 s of rendered non-linear form inside it, and the ERT sits 15 s
before the window opens, which is the head start the APS gets.

### I.3 Resolution document

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T19:40:12Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-901" duration="PT15S">

        <!-- 1. side-by-side / double box: video ad + advertiser background -->
        <svta:RenderableAsset form="video"
                              layout="squeezeback-double-box-with-background">
          <svta:BackgroundElement
              assetUrl="https://adcdn.example.com/901/box-bg.jpg"/>
          <ImportedMPD>https://adcdn.example.com/901/box.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <!-- 2. L-shape: image full-frame creative -->
        <svta:RenderableAsset form="image"
                              layout="squeezeback-l-shape"
                              assetUrl="https://adcdn.example.com/901/lshape.jpg"/>

        <!-- 3. HTML lower third -->
        <svta:RenderableAsset form="html"
                              layout="overlay-lower-third"
                              assetUrl="https://adcdn.example.com/901/lower-third.html"/>

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

The four options in preference order, and what each one costs the
device (§5.3.7.3):

1. **Side-by-side / double box, video ad plus advertiser background** —
   three on-screen elements: the shrunk primary content, the ad video,
   and the background image filling the bands the two boxes leave
   uncovered. Two concurrent video decoders plus an image surface.
2. **L-shape, image full-frame creative** — two on-screen elements: the
   image creative occupying the whole frame and the shrunk primary
   content composited on top of it. One decoder plus an image surface.
3. **HTML lower third** — an HTML document composited over the bottom
   band of the playing video. One decoder plus an HTML surface.
4. **Full-screen takeover video** — a linear-style ad played
   sequentially: the primary content stops, the ad plays, the primary
   content resumes. One decoder, reused; no concurrent composition of
   any kind.

Three forms and four layout tokens on one candidate, with one declared
duration of `PT15S` that applies to whichever option the Player picks —
an image or HTML form has no intrinsic length, so that value is the
whole of what fixes how long it stays on screen (§8.6). Converted into
the window's timescale it is 15000, which equals the cap exactly and is
admitted (§4.6.4).

### I.4 The per-class walk

Each option is checked on two axes — what the device can composite, and
whether the window admits the layout token (§4.6.3, §4.6.5). Here the
Publisher's set admits all four tokens, so no option fails on the
allowed-layout axis in this annex; what separates the classes is
decoder count and surface type.

**D1** — two or more decoders, image and HTML surfaces. Option 1 needs
two decoders and an image surface for the background element, and D1
has both. The **first** option passes, so the Player renders it and
stops walking.

**D2** — two decoders, no non-video surface. Option 1: the two decoders
are there for the two videos, but the third element is the background,
an **image**, and D2 composites no non-video content — it fails on
surface type, not on decoder count. Option 2: the full-frame creative
is an image and needs an image surface D2 lacks — fails on surface
type. Option 3: needs an HTML surface — fails on surface type. Option
4: one decoder reused sequentially, no concurrent composition at all —
**satisfiable**. The Player renders option 4.

**D3** — one decoder, image and HTML surfaces. Option 1 needs a second
decoder for the ad video — fails on decoder count. Option 2 needs one
decoder for the shrunk primary content plus an image surface for the
full-frame creative, and D3 has both — **satisfiable**. The Player
renders option 2 and never reaches the HTML option behind it.

**D4** — one decoder, image surface, no HTML surface. Option 1 fails on
decoder count. Option 2 needs an image surface, which D4 has —
**satisfiable**, rendered. Had option 2's full-frame creative been HTML
rather than an image, D4 would have failed it on surface type, failed
option 3 on the same axis, and landed on option 4.

**D5** — one decoder, no surface of any kind. Option 1 fails on both
axes at once: the second decoder and the image surface. Option 2 fails
on surface type, option 3 likewise. Option 4 needs no concurrent
composition — **satisfiable**, rendered.

### I.5 Sub-MPD

The video creative of option 1, reached through that option's
`<ImportedMPD>`, in the Single-Period Static profile the base
specification binds every imported MPD to (§5.4). Option 4's sub-MPD
has the same shape.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S">
  <BaseURL>https://adcdn.example.com/901/box/</BaseURL>
  <Period id="ad-901-box" duration="PT15S">
    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=901</Event>
      <Event presentationTime="7500"  id="2">https://tracker.example.com/midpoint?ad=901</Event>
      <Event presentationTime="15000" id="3">https://tracker.example.com/complete?ad=901</Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1" par="16:9">
      <SegmentTemplate timescale="90000" duration="270000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/seg-$Number$.m4s"/>
      <Representation id="v-720" bandwidth="2200000"
                      width="1280" height="720" sar="1:1"/>
      <Representation id="v-360" bandwidth="800000"
                      width="640" height="360" sar="1:1"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true">
      <AudioChannelConfiguration
          schemeIdUri="urn:mpeg:dash:23003:3:audio_channel_configuration:2011"
          value="2"/>
      <SegmentTemplate timescale="48000" duration="144000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/seg-$Number$.m4s"/>
      <Representation id="a-128" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

Two things about the callback stream here. Its presentation times run on
the **ad's own** presentation timeline, so `0` is the ad's first frame
and the Player adds the ad's start position on the primary timeline to
each value (§5.5.3). And this candidate carries a callback stream too,
which is the other admissible position for a video form (§5.5.2): the
Player fires the union of the two, and because the beacons share their
`@id` values it fires three beacons and not six (§4.6.15).

### I.6 Outcome

| Class | Option | What the viewer sees |
|---|---|---|
| D1 | 1 — side-by-side | Primary content shrunk into one box, the ad video in the other, the advertiser's background image filling the bands around them |
| D2 | 4 — full-screen takeover | A full-screen video ad of bounded duration, then the primary content resumes |
| D3 | 2 — L-shape | Primary content shrunk on top of an image creative filling the whole frame; the band of the creative visible around it forms the "L" |
| D4 | 2 — L-shape | The same as D3 |
| D5 | 4 — full-screen takeover | The same as D2, reached by a different route |

Five classes, three layouts, one authored decision.

Two contrasts carry the annex. **D2 is the instructive row**: it owns
the two decoders the side-by-side video needs and still declines option
1, because the third element — the background, an image — is a surface
it cannot composite. The rule is element **type** and not element
**count**. And **D2 and D5 share an outcome for different reasons**: D5
has no compositing capability at all where D2 has it for video only,
and the ordered list reaches the same last option along two different
paths.

The modelling of the two layouts is what separates D3 and D4 from D1.
The side-by-side here is a three-element layout carrying a **video**
ad, needing two decoders plus an image surface, which puts it out of
reach of a single-decoder device. The L-shape is a two-element layout
carrying an **image** full-frame creative, needing one decoder plus one
image surface, which is within reach. The full-screen takeover is the
one row satisfiable on every class, which is what makes it the useful
last option on an ordered list.

## Annex J — Side-by-side / double box, the three-element layout

*Informative.*

### J.1 Scenario

The Publisher sells a non-linear opportunity whose admitted layouts
include the **side-by-side / double box**: the primary content shrinks
into one box, the ad occupies the other, the two sit next to each other
on a 16:9 screen, and the bands the two boxes leave uncovered are filled
by a third element — a **background element**, a still image the
advertiser supplies. The primary content never stops; what changes is
that it gives up part of the frame for a bounded interval.

This layout is the one place in the specification where a single
presentation puts **three** elements on screen at once, and that is why it
is worth a walk of its own. The background element is a still image,
never a video and never an HTML surface, so it consumes no video decoder;
and it is a **composition attribute of the layout** rather than one of the
candidate's alternative presentation options, so the Player does not walk
it the way it walks the options — it composites it as part of rendering
the layout once the layout is chosen (§5.3.7.2). The consequence, developed
in §J.7, is that the class a reader would expect to render this layout is
the one that declines it.

### J.2 Main MPD

The window opens at 15:00 on the primary timeline and lasts 25 seconds.
The cap is 20 seconds of cumulative rendered presentation. The admitted
layouts are the three-element side-by-side, the two-element side-by-side
that carries no background, and the full-screen takeover as the option of
last resort.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT4S"
     publishTime="2026-09-14T08:00:00Z">

  <Period id="main" start="PT0S">

    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="501" presentationTime="900000" duration="25000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/overlay?slot=sbs-1"
            maxDuration="20000"
            allowedLayouts="squeezeback-double-box-with-background squeezeback-double-box linear"
            earliestResolutionTimeOffset="12000"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="540000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/seg-$Number$.m4s"/>
      <Representation id="v720"  bandwidth="2500000" width="1280" height="720"/>
      <Representation id="v1080" bandwidth="5000000" width="1920" height="1080"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The Publisher declares no dimension anywhere. Each layout token carries
the IAB's spatial bound by reference — the double box gives the content
and the ad a quarter of the frame each — and this specification declares
no dimensional attribute on a slot or on a presentation option (§3.2).
Nor does the Publisher supply the background: the two side-by-side tokens
differ precisely in whether the **advertiser** supplied one, and the
Publisher's part is admitting both tokens so that either answer can be
served.

### J.3 Resolution request

```
GET /decision/overlay?slot=sbs-1&sgaiVideoDecoders=2&sgaiImageOverlay=false&sgaiHtmlOverlay=false HTTP/1.1
Host: aps.example.com
Accept: application/dash+xml
```

That is the D2 request — two video decoders, no image surface over video,
no HTML surface over video. An APS that narrows on capability would answer
it with a shorter option list; the APS in this annex narrows nothing, so
all five classes receive the document of §J.4 and the selection happens
entirely at the Player (§7.3, §5.8.4). The other four classes send the
same GET with the three values that identify them per §5.8.2.

### J.4 Resolution document

One candidate, five options. Three of them offer the three-element
side-by-side across three different forms; the fourth offers the same
spatial arrangement without a background element; the fifth is the
full-screen takeover.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T14:59:48Z">

  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>

      <svta:Candidate id="c1-brandz" duration="PT15S">

        <!-- option 1 -->
        <svta:RenderableAsset form="video"
                              layout="squeezeback-double-box-with-background">
          <svta:BackgroundElement assetUrl="https://adcdn.example.com/brandz/bands.png"/>
          <ImportedMPD earliestResolutionTimeOffset="10.0">https://adcdn.example.com/brandz/box-video.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <!-- option 2 -->
        <svta:RenderableAsset form="html"
                              layout="squeezeback-double-box-with-background"
                              assetUrl="https://adcdn.example.com/brandz/box.html">
          <svta:BackgroundElement assetUrl="https://adcdn.example.com/brandz/bands.png"/>
        </svta:RenderableAsset>

        <!-- option 3 -->
        <svta:RenderableAsset form="image"
                              layout="squeezeback-double-box-with-background"
                              assetUrl="https://adcdn.example.com/brandz/box.jpg">
          <svta:BackgroundElement assetUrl="https://adcdn.example.com/brandz/bands.png"/>
        </svta:RenderableAsset>

        <!-- option 4 -->
        <svta:RenderableAsset form="video"
                              layout="squeezeback-double-box">
          <ImportedMPD earliestResolutionTimeOffset="10.0">https://adcdn.example.com/brandz/box-video.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <!-- option 5 -->
        <svta:RenderableAsset form="video"
                              layout="linear">
          <ImportedMPD earliestResolutionTimeOffset="10.0">https://adcdn.example.com/brandz/takeover.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=brandz</Event>
          <Event presentationTime="3750"  id="2">https://tracker.example.com/firstQuartile?ad=brandz</Event>
          <Event presentationTime="7500"  id="3">https://tracker.example.com/midpoint?ad=brandz</Event>
          <Event presentationTime="11250" id="4">https://tracker.example.com/thirdQuartile?ad=brandz</Event>
          <Event presentationTime="15000" id="5">https://tracker.example.com/complete?ad=brandz</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://brandz.example.com/offer">
          <svta:ClickTracking>https://tracker.example.com/click?ad=brandz</svta:ClickTracking>
        </svta:Click>

        <svta:AdSystem value="example-ads"/>
        <svta:AdTitle value="BrandZ — double box"/>
        <svta:Advertiser value="BrandZ"/>
        <svta:UniversalAdId idRegistry="ad-id.org" value="BRZ0088000H"/>

      </svta:Candidate>

    </svta:OverlayList>
  </Period>
</MPD>
```

Four things in that document are the annex's substance.

Options 1 to 3 each carry exactly one `<svta:BackgroundElement>`, which
is what the `squeezeback-double-box-with-background` token requires, and
the three point at the same image: the background is the advertiser's
branding for the campaign, not a per-form asset. Option 4 uses the
`squeezeback-double-box` token and carries no background element, so its
uncovered bands render as black (§5.3.7.2). The background element is an
image on every option, including the option whose ad form is video — it is
a branding surface and never a video, so it never consumes a decoder. And
one candidate duration of fifteen seconds covers whichever option the
Player picks, including the image and HTML options, which have no
intrinsic length (§8.6); the quartile beacons at 3 750, 7 500 and 11 250 are
fractions of that same fifteen seconds, measured from the first rendered
frame of whichever asset was chosen (§5.5.3).

### J.5 Sub-MPD

Option 1 — the video ad inside the three-element side-by-side — reaches
its creative through `<ImportedMPD>` into a document bound to the
Single-Period Static profile (§5.4). Option 4 imports the same document,
since the two options differ in composition and not in creative:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:sps:2024"
     type="static"
     minBufferTime="PT2S">

  <Period id="brandz-box" duration="PT15S">

    <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                 value="1" timescale="1000">
      <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=brandz</Event>
      <Event presentationTime="3750"  id="2">https://tracker.example.com/firstQuartile?ad=brandz</Event>
      <Event presentationTime="7500"  id="3">https://tracker.example.com/midpoint?ad=brandz</Event>
      <Event presentationTime="11250" id="4">https://tracker.example.com/thirdQuartile?ad=brandz</Event>
      <Event presentationTime="15000" id="5">https://tracker.example.com/complete?ad=brandz</Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1">
      <SegmentTemplate timescale="90000" duration="180000" startNumber="1"
                       initialization="box/init.mp4"
                       media="box/seg-$Number$.m4s"/>
      <Representation id="a540" bandwidth="1500000" width="960" height="540"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true">
      <SegmentTemplate timescale="48000" duration="96000" startNumber="1"
                       initialization="box-audio/init.mp4"
                       media="box-audio/seg-$Number$.m4s"/>
      <Representation id="a-aac" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The background element's URL travels on the presentation option in the
resolution document and never inside this sub-MPD, and the reason is
structural rather than stylistic: every Representation in a document
reached through `<ImportedMPD>` carries a media type from the RFC 4337
registry, which admits no still-image type at all (§4.7.2). The
`@codecs` values follow RFC 6381's lowercase hexadecimal production.

### J.6 Per-device-class behaviour

Every class walks the same five options in document order. The outcome is
read off §5.3.7.3, and the five classes land on five different options.

| Class | Capability declaration | Options passed over | Option rendered | On screen |
|---|---|---|---|---|
| **D1** | `sgaiVideoDecoders=2`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=true` | none | **1** — `video` / `squeezeback-double-box-with-background` | Shrunk primary content in one box, ad video in the other, advertiser's image filling the bands |
| **D2** | `sgaiVideoDecoders=2`, `sgaiImageOverlay=false`, `sgaiHtmlOverlay=false` | 1, 2, 3 | **4** — `video` / `squeezeback-double-box` | Shrunk primary content in one box, ad video in the other, bands black |
| **D3** | `sgaiVideoDecoders=1`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=true` | 1 | **2** — `html` / `squeezeback-double-box-with-background` | Shrunk primary content in one box, HTML ad in the other, advertiser's image filling the bands |
| **D4** | `sgaiVideoDecoders=1`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=false` | 1, 2 | **3** — `image` / `squeezeback-double-box-with-background` | Shrunk primary content in one box, still image ad in the other, advertiser's image filling the bands |
| **D5** | `sgaiVideoDecoders=1`, `sgaiImageOverlay=false`, `sgaiHtmlOverlay=false` | 1, 2, 3, 4 | **5** — `video` / `linear` | Full-screen takeover, then the primary content alone |

**D1** is the only class that satisfies the document's first option, which
is the most demanding row of §5.3.7.3: two video decoders for the shrunk
primary content and the ad, plus an image surface for the background.
Document order decides, and the richest option is first.

**D2** passes over the three options that carry a background element and
takes the fourth, which is the same spatial arrangement with the bands
black. Its two decoders are enough for the two videos; what it lacks is
the surface the third element needs. §J.7 develops this.

**D3** passes over option 1 because a video ad in a side-by-side needs a
second decoder while the first holds the shrunk primary content. Option 2
asks for one decoder plus an HTML surface for the ad and an image surface
for the background, and D3 carries both, so the HTML ad renders inside the
full three-element composition — background included. A single-decoder
class therefore reaches a **more complete** composition than the
dual-decoder class above it, which is the clearest statement in this annex
that the decoder count is not the ranking.

**D4** differs from D3 on the HTML axis alone, and that axis decides option
2. Option 3 asks for one decoder plus two image surfaces — one for the ad,
one for the background — and D4 has them, so the three-element side-by-side
renders with a still-image ad.

**D5** composites no non-video surface and holds one decoder, already
presenting the primary content, so none of the four side-by-side options is
satisfiable whatever the ad's form. Option 5 is the full-screen takeover,
the one row of §5.3.7.3 satisfiable on every class, because it composites
nothing concurrently: one decoder, reused sequentially. Where a candidate's
list ends before offering it, D5 finds nothing satisfiable, the Player skips
the candidate, and the primary content continues uninterrupted (§4.6.6).

**The cap.** The candidate declares fifteen seconds against a twenty-second
cap, so it renders in full on every class that accepts it. Were a second
candidate of ten seconds to follow, the Player would either drop it before
playback on its declared duration or accept it and stop rendering at the
twenty-second boundary, stopping that candidate's remaining beacons at the
trim point (§4.6.4, §4.6.15). The cap counts presentation-timeline units, so
an interval during which that timeline does not advance does not accrue
against it.

### J.7 Why D2 declines the three-element layout

D2 owns two video decoders. The three-element side-by-side with a video ad
needs two video decoders. D2 does not render it.

That is not an inconsistency, and reading it as one is the mistake this
section exists to prevent. The budget of §5.3.7.3 has **two** axes, not one:
how many video decoders a layout needs, and which **non-video surfaces** it
needs. A device class is defined on both — D2 is *two decoders and no
non-video compositing at all* — and a layout is satisfiable only when the
device covers both axes.

The three-element composition puts a still image on screen next to playing
video. The background element is that image. It is the cheapest element in
the layout by every measure a reader is likely to reach for — it holds no
decoder, decodes once, and never moves — and it is nevertheless the element
that decides the outcome, because the question is not *how much* the device
has to composite but *what kind of surface* it has to composite. D2 has no
answer to "an image alongside video" at any size.

The rule generalises past this layout and past this class:

- **The blocker is a surface type, not a surface count.** Option 4 removes
  exactly one element from option 1 — the background — and D2 renders it.
  The two options ask for the same two decoders; they differ only in whether
  a non-video surface is in the composition.
- **A higher decoder count does not order the classes.** D3 has one decoder
  and renders option 2, a *three*-element composition. D2 has two decoders
  and renders option 4, a two-element one. Neither class dominates the
  other, so an ordered list of options cannot be a list from "expensive" to
  "cheap": it is a list of pairings, each satisfiable by whichever classes
  cover both of its axes.
- **This is why the ordered list is the mechanism and capability parameters
  are only a hint.** An APS narrowing on `sgaiVideoDecoders=2` alone would
  have sent D2 the video side-by-side with the background and been wrong.
  What makes the outcome correct is the Player checking every option against
  its own device before rendering it (§4.6.5), whatever it declared and
  whatever the APS inferred.
- **The conservative posture follows from the same reading.** A Player that
  cannot confirm a surface capability omits the corresponding parameter
  rather than declaring `true`, because a declared capability the device
  cannot deliver on costs an opportunity that a correct declaration would
  have filled from a lower option (§8.4).

## Annex K — ClickThrough

*Informative.*

### K.1 Scenario

An ad is on screen — linear or non-linear, it makes no difference here.
Its resolution document carries the ad's ClickThrough URL together with
the click-tracking URLs that accompany it. The viewer activates the
click: a select on a CTV remote, a tap on a phone. At that moment the
Player opens, or hands off to the platform, the ClickThrough destination
and fires each accompanying click-tracking URL once.

The Publisher configures nothing beyond permitting the ad. The
ClickThrough travels with the ad and not with the slot, so it arrives in
the resolution document alongside the creative that carries it, and a
slot declaration says nothing about it.

### K.2 The carrier in an Overlay Resolution Document

On a non-linear slot the carrier is a `<svta:Click>` child of the
candidate:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T14:10:02Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>

      <svta:Candidate id="cand-1101" duration="PT15S">
        <svta:RenderableAsset form="image"
                              layout="overlay-lower-third"
                              assetUrl="https://adcdn.example.com/1101/strip.png"/>
        <svta:RenderableAsset form="html"
                              layout="overlay-corner"
                              assetUrl="https://adcdn.example.com/1101/corner.html"/>

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

        <svta:AdSystem value="example-ads"/>
        <svta:AdTitle value="Autumn campaign — lower third"/>
      </svta:Candidate>

    </svta:OverlayList>
  </Period>
</MPD>
```

One `<svta:Click>` per candidate, carrying one `@clickThroughUrl` and as
many `<svta:ClickTracking>` children as the advertiser declared. The
element sits beside the presentation options rather than inside one, so
the click is a property of the ad and survives whichever option the
Player selects: the destination is the same whether the device renders
the lower third or the corner.

### K.3 The carrier on a linear `ListMPD` `<Period>`

On a linear slot the same element is the carrier, travelling as
foreign-namespace open content on the `ListMPD` `<Period>` of the ad it
belongs to:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT0S"
     publishTime="2026-09-17T14:10:02Z">

  <Period id="ad-1" duration="PT15S">
    <ImportedMPD earliestResolutionTimeOffset="10.0">https://adcdn.example.com/1102/ad.mpd</ImportedMPD>
    <svta:Click clickThroughUrl="https://advertiser.example.com/autumn?utm_source=linear">
      <svta:ClickTracking>https://tracker.example.com/click?ad=1102</svta:ClickTracking>
    </svta:Click>
  </Period>

  <Period id="ad-2" duration="PT10S">
    <ImportedMPD earliestResolutionTimeOffset="10.0">https://adcdn.example.com/1103/ad.mpd</ImportedMPD>
    <svta:Click clickThroughUrl="https://advertiser.example.net/offer"/>
  </Period>

</MPD>
```

Each Period is one ad in the break and carries its own click, so the
destination the viewer reaches is the destination of the ad that was on
screen when they acted. The second Period shows the shape of a
ClickThrough with no click-tracking, which §K.6 covers.

> **Note on profile signalling.** A profile-conformance check modifies
> the document before it checks it, and removes every
> extension-namespace element the declared profile does not explicitly
> include (§4.7.8). This `ListMPD` declares only the list profile, so
> that procedure strips both `<svta:Click>` elements and checks what is
> left. What remains is a valid `ListMPD`, which is the property the
> construction rests on — but a client bound to the list profile alone
> is entitled to drop the carrier, and a passing profile-conformance
> report says nothing about the click at all.

### K.4 Two kinds of tracking, and why they need two carriers

| | Timeline beacons | Click-tracking |
|---|---|---|
| Carrier | `<Event>` entries in a callback `<EventStream>` (§5.5) | `<svta:ClickTracking>` inside `<svta:Click>` (§5.6) |
| Trigger | The playhead reaching a scheduled presentation time | The viewer activating the click |
| Timing | `@presentationTime`, relative to the ad's own first frame | None: it fires when the viewer acts, or never |
| Fires when the viewer does nothing | Yes | No |
| Who declares it | The ADS, transcribed by the APS | The advertiser, carried by the APS |

The split follows from what the base specification's event machinery
schedules against. Every event in it is evaluated against the media
presentation timeline, and the callback scheme in particular issues its
HTTP GET when the playhead reaches the event's presentation time. A
ClickThrough activation has no presentation time to reach — it is a
viewer action that may never occur — so the callback scheme can carry
impressions and quartiles and cannot carry the click. A carrier of its
own is what makes the click behave identically on every Player
conformant to this specification, which is the interoperability the
construct exists for.

### K.5 Behaviour on activation

The Player reads `@clickThroughUrl` from the carrier and, when the
viewer activates the click, does two things in the same step: it opens
or hands off the destination — a system browser, a platform hand-off,
whatever the device's convention is — and it fires each
`<svta:ClickTracking>` URL once.

Firing is fire-and-forget, as it is for a timeline beacon: the response
is discarded, and a click-tracking request that fails leaves the ad and
the primary content exactly as they were. The failure stays inside the
implementation and never reaches the viewer.

The timeline beacons of the same candidate keep running on their own
schedule while this happens. An activation neither fires them early nor
suppresses the ones still ahead.

### K.6 A ClickThrough with no click-tracking

Whether a ClickThrough carries any click-tracking is the advertiser's
decision, and a `<svta:Click>` with no `<svta:ClickTracking>` child is a
complete, conformant declaration:

```xml
<svta:Click xmlns:svta="urn:svta:dash:sgai:2026"
            clickThroughUrl="https://advertiser.example.net/offer"/>
```

The Player opens the destination and fires nothing. This is the shape to
expect when the advertiser measures clicks at the landing page rather
than at a tracker, and it is not a degraded or partial form of the
carrier.

### K.7 A Player that predates this specification

The click is inert. Such a Player discards the `<svta:Click>` element
with its parent subtree — inside a candidate it never fetched the
document for, or on a `ListMPD` `<Period>` whose ad it does play — reads
no `@clickThroughUrl`, and has nothing to activate. Nothing else about
the ad changes: on the linear path the creative renders, the timeline
beacons the sub-MPD carries fire on their schedule, and the break
completes normally. What is lost is the click and only the click.

### K.8 Device classes

The outcome does not vary across D1 to D5. What the device needs in
order to activate a click is an input mechanism — a remote select, a
tap — and not a decoder or a compositing surface, so none of the axes
that separate the five classes is consulted. All five read the same
carrier, open the same destination and fire the same click-tracking
URLs.

## Annex L — Overlapping windows of the same family, with fallback

*Informative.*

### L.1 Scenario

Three overlay windows overlap in time in the main MPD. They are windows
of one family, so they are not three concurrent opportunities: they are
a **chain**. The Player serves the first of them and reaches the second
only when the attempt on the first produced no ad; the third stands
behind the second on the same terms.

An attempt produces no ad in four ways, and they are treated alike: the
APS does not answer, the response carries a final status other than
`200`, the body is not a resolution document the Player can parse, or
the body is a well-formed document that carries no candidates. All four
are a failed execution, and a failed execution is what advances the
Player to the next window (§4.6.8). What does **not** advance it is a
document that carries candidates: once candidates arrive, the chain has
been answered, and whatever the Player then does with those candidates
ends at the primary content rather than at the next window.

### L.2 Main MPD

All the windows of one family in one Period are authored as `<Event>`
entries inside a single `<EventStream>` (§4.3.4):

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S"
     publishTime="2026-09-17T15:00:00Z">

  <Period id="p1" start="PT0S">

    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">

      <!-- The window to serve: earliest presentation time. -->
      <Event id="1201" presentationTime="600000" duration="30000">
        <svta:OverlayPresentation uri="https://aps-a.example.com/decision/overlay?slot=1201"
                                  earliestResolutionTimeOffset="20000"
                                  maxDuration="15000"
                                  allowedLayouts="overlay-lower-third overlay-corner"/>
      </Event>

      <!-- First backup: a narrower layout set and a tighter cap. -->
      <Event id="1202" presentationTime="605000" duration="25000">
        <svta:OverlayPresentation uri="https://aps-b.example.com/decision/overlay?slot=1202"
                                  earliestResolutionTimeOffset="20000"
                                  maxDuration="10000"
                                  allowedLayouts="overlay-corner"/>
      </Event>

      <!-- Second backup: admits the full-screen takeover as the
           option of last resort, with the tightest cap. -->
      <Event id="1203" presentationTime="610000" duration="20000">
        <svta:OverlayPresentation uri="https://aps-c.example.com/decision/overlay?slot=1203"
                                  earliestResolutionTimeOffset="20000"
                                  maxDuration="8000"
                                  allowedLayouts="overlay-corner linear"/>
      </Event>

    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="video/init.mp4"
                       media="video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="audio/init.mp4"
                       media="audio/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="a1" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

No attribute declares the chain. The overlap plus the shared family is
the declaration, and the three `@uri` values point at three different
APS endpoints, which is a common reason to declare a chain at all.

The three windows differ in what they admit and in what they cap:
`overlay-lower-third` is admissible only under 1201, `linear` only under
1203, and the caps run 15 000, 10 000 and 8 000 in the event stream's
millisecond timescale. Those differences are not decoration — §L.7
turns on them.

### L.3 The order the Player takes them in

Oldest presentation time first: 1201 at 600 000, then 1202 at 605 000,
then 1203 at 610 000. Document position is consulted only to separate
two windows that declare the same presentation time, which is not the
case here (§4.6.9).

### L.4 Path 1 — the first window answers with no candidates

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
     publishTime="2026-09-17T15:09:38Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList/>
  </Period>
</MPD>
```

The opportunity was offered and nothing was sold. That is a complete,
well-formed answer and it is still an attempt that produced no ad, so it
is a failed execution and the Player moves to window 1202:

```
GET https://aps-b.example.com/decision/overlay?slot=1202
→ 200 OK
```

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T15:09:39Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-b1" duration="PT8S">
        <svta:RenderableAsset form="image"
                              layout="overlay-corner"
                              assetUrl="https://adcdn.example.com/b1/corner.png"/>
        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"    id="1">https://tracker.example.com/impression?ad=b1</Event>
          <Event presentationTime="8000" id="2">https://tracker.example.com/complete?ad=b1</Event>
        </EventStream>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

The Player validates that candidate against **window 1202** — the
`overlay-corner` token is in that window's `@allowedLayouts`, and
`PT8S` converts to 8 000 against its cap of 10 000 — renders it on a
device that composites an image over video, and fires the two beacons on
the ad's own timeline. The fallback was used as declared, and an
implementation that reports opportunities to the application reports
1201 as **unfilled** rather than failed: the market was asked and did
not buy, which is worth distinguishing from an APS that could not be
reached even though the Player's next step is the same.

Window 1201 was not consumed by the attempt. Executions are counted,
not attempts, so a window declared `@executeOnce="true"` that resolved
to no ads stays executable later in the session.

### L.5 Path 2 — the first window's APS is unreachable

```
GET https://aps-a.example.com/decision/overlay?slot=1201
→ connection timed out
GET https://aps-b.example.com/decision/overlay?slot=1202
→ 503 Service Unavailable
GET https://aps-c.example.com/decision/overlay?slot=1203
→ 200 OK
```

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T15:10:11Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-c1" duration="PT8S">
        <svta:RenderableAsset form="image"
                              layout="overlay-corner"
                              assetUrl="https://adcdn.example.com/c1/corner.png"/>
        <svta:RenderableAsset form="video"
                              layout="linear">
          <ImportedMPD earliestResolutionTimeOffset="5.0">https://adcdn.example.com/c1/takeover.mpd</ImportedMPD>
        </svta:RenderableAsset>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

A transport failure and a non-`200` are two different events on the
wire and the same thing to the chain: nothing was obtained either time,
so each is a failed execution and each advances the Player one window.
Window 1203 answers with candidates, and the chain ends there whatever
happens next inside that document.

The candidate offers the corner overlay first and the full-screen
takeover second, and window 1203 is the one window of the three that
admits `linear` — which is what lets the last link in the chain fall
back to an option every device class can render. On a device that
composites an image over video the Player renders the first option; on
one that composites nothing over video it passes over that option and
renders the takeover.

Had 1203 also failed, the family would have been exhausted and the
primary content would have continued uninterrupted. A Publisher who
declares no backup at all gets that outcome after the single attempt.

### L.6 Path 3 — candidates arrive and the device can satisfy none

This is the path that does **not** advance the chain. Window 1201
answers, and it answers with an ad:

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
     publishTime="2026-09-17T15:09:38Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-a1" duration="PT12S">
        <svta:RenderableAsset form="video"
                              layout="overlay-corner">
          <ImportedMPD earliestResolutionTimeOffset="5.0">https://adcdn.example.com/a1/corner.mpd</ImportedMPD>
        </svta:RenderableAsset>
        <svta:RenderableAsset form="html"
                              layout="overlay-lower-third"
                              assetUrl="https://adcdn.example.com/a1/strip.html"/>
      </svta:Candidate>
    </svta:OverlayList>
  </Period>
</MPD>
```

The Player is a D4 device: one video decoder, an image surface over
video, no HTML surface. It walks the options in document order.

| Option | Layout admitted by 1201 | What the device needs | Outcome on D4 |
|---|---|---|---|
| 1 — `video` / `overlay-corner` | yes | a second video decoder | passed over |
| 2 — `html` / `overlay-lower-third` | yes | an HTML surface over video | passed over |

Both options pass the Publisher check and fail the device check, so the
candidate has no satisfiable option and is skipped. It was the only
candidate in the document, so the candidates are exhausted and the
Player continues with the primary content.

Windows 1202 and 1203 are never requested. The attempt on 1201 did not
fail: it obtained a document that carried a candidate, which is an
answer, and the fall-through that followed was inside that document
rather than across windows. Reading this path as a failed execution
would spend the Publisher's two backup windows on an opportunity that
had already been filled by the market and declined by the device —
which is the more consequential of the two mistakes available here,
because it also makes the backups unavailable for the case they were
declared for (§8.1.1).

### L.7 Each window binds what it serves with its own declarations

A window in a chain carries its own `@allowedLayouts` and its own
`@maxDuration`, and the candidates it serves are validated against
those values. A window inherits nothing from the window it stands in
for (§4.6.9).

Take the candidate `cand-b1` of §L.4 — `overlay-corner`, `PT8S` — and a
second candidate offering `overlay-lower-third` at `PT12S`, and check
each against each window:

| Candidate | Under 1201 (`overlay-lower-third overlay-corner`, cap 15 000) | Under 1202 (`overlay-corner`, cap 10 000) | Under 1203 (`overlay-corner linear`, cap 8 000) |
|---|---|---|---|
| `overlay-corner`, `PT8S` | admissible | admissible | admissible |
| `overlay-lower-third`, `PT12S` | admissible | layout not admitted; 12 000 over cap | layout not admitted; 12 000 over cap |

The same document is therefore worth different things depending on which
window obtained it, and an APS answering window 1202 is answering a
narrower question than one answering window 1201. The Player converts
each candidate's ISO 8601 duration into the window's timescale before
comparing, rounding up, and a candidate whose converted duration equals
the cap exactly is admitted (§4.6.4).

### L.8 Why an overlap is a declared chain and not a runtime concurrency case

Two readings of an overlap are available and only one of them can be
implemented without a construct this specification does not have.

Read as concurrency, an overlap would ask the Player to arbitrate at
runtime between two or three simultaneously resolvable opportunities of
one family — and serving more than one of them would put more than one
non-linear form on the screen at the same instant, which is the demand
on the device's decoder and surface budget that the one-form-at-a-time
rule exists to prevent (§4.6.7). Arbitrating would need a priority the
Publisher could declare, and no attribute carries one. Concurrency of
windows is concurrency of presentation, and the specification has no
place to write the tie-break.

Read as a chain, the arbitration disappears. The windows are ordered by
presentation time, which every declaration already carries; exactly one
is served; and the ones behind it are reached only when the one in front
produced nothing. The Publisher gets continuity — an unfilled or
unreachable opportunity retried against a different endpoint — at the
cost of one attribute it does not have to declare, and the Player never
holds two live opportunities of one family at once.

### L.9 Device classes

Which window is served does not vary across D1 to D5: the chain is
decided by presentation times and by what each attempt returned, and
none of the axes that separate the classes is consulted while it is
being walked.

What the device class changes is whether §L.6 arises at all, and that
happens after the chain has already ended — the same document that
strands a D4 device renders on a D1 one, from the same window, with the
same two backups left untouched.

## Annex M — One ad, Player-declared capabilities, resolved by the APS

*Informative.*

### M.1 Scenario

This is the same ad as Annex I: one non-linear candidate for the same
overlay slot, carrying the same four presentation options in the same
order, with the same creative URLs and the same declared duration of
`PT15S`. The Publisher declares the same single device-agnostic
allowed-layout set.

What differs is where the capability check is resolved. Here the Player
attaches the reserved capability parameters it is willing to disclose
to the resolution request (§5.8.2), and the APS resolves the candidate
against them, emitting the options that survive — sometimes exactly one.
The Player then checks what it received before rendering it, as it
always does (§4.6.5).

The two annexes are two divisions of one responsibility rather than two
behaviours to choose between: in Annex I the APS emits every option and
each Player selects among them, here each Player declares and the APS
selects, and every class lands on the same rendered result. The D4 row
below is this same APS behaving exactly as Annex I describes, because
that is what a Player which declares nothing leaves it able to do.

### M.2 Main MPD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-on-demand:2011"
     type="static"
     mediaPresentationDuration="PT42M"
     minBufferTime="PT2S">
  <Period id="1" start="PT0S">
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="901" presentationTime="480000" duration="20000">
        <svta:OverlayPresentation
            uri="https://aps.example.com/decision/overlay?slot=901"
            maxDuration="15000"
            allowedLayouts="squeezeback-double-box-with-background squeezeback-l-shape overlay-lower-third linear"
            earliestResolutionTimeOffset="15000"/>
      </Event>
    </EventStream>
    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f" segmentAlignment="true"
                   startWithSAP="1" par="16:9">
      <SegmentTemplate timescale="90000" duration="360000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/seg-$Number$.m4s"/>
      <Representation id="v-1080" bandwidth="5000000"
                      width="1920" height="1080" sar="1:1"/>
      <Representation id="v-720" bandwidth="2500000"
                      width="1280" height="720" sar="1:1"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en" segmentAlignment="true">
      <AudioChannelConfiguration
          schemeIdUri="urn:mpeg:dash:23003:3:audio_channel_configuration:2011"
          value="2"/>
      <SegmentTemplate timescale="48000" duration="192000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4"
                       media="$RepresentationID$/seg-$Number$.m4s"/>
      <Representation id="a-128" bandwidth="128000"
                      audioSamplingRate="48000"/>
    </AdaptationSet>
  </Period>
</MPD>
```

The manifest is byte-identical to Annex I's, and that is the point:
nothing in it asks for a capability parameter, and nothing has to.
Which reserved parameters travel is the Player's runtime decision
(§4.6.22), taken without any declaration by the Publisher, the ADS or
the APS. The author-declared query template of §5.8.1 is a separate
source of parameters, draws its names from outside the reserved set,
and is not used in this annex.

### M.3 D1 — declares everything

```
GET /decision/overlay?slot=901&sgaiVideoDecoders=2&sgaiImageOverlay=true&sgaiHtmlOverlay=true
Host: aps.example.com
```

Two or more concurrent video decoders, an image surface over video, an
HTML surface over video: the declaration identifies the device as D1
(§5.8.2).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T19:40:12Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-901" duration="PT15S">
        <svta:RenderableAsset form="video"
                              layout="squeezeback-double-box-with-background">
          <svta:BackgroundElement
              assetUrl="https://adcdn.example.com/901/box-bg.jpg"/>
          <ImportedMPD>https://adcdn.example.com/901/box.mpd</ImportedMPD>
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

The APS finds option 1 satisfiable on that declaration — two decoders
for the two videos, an image surface for the background element — and
emits it alone. The Player checks the option against its own device and
against the window's allowed layouts, both pass, and it composites the
side-by-side.

### M.4 D2 — declares two decoders and no non-video surface

```
GET /decision/overlay?slot=901&sgaiVideoDecoders=2&sgaiImageOverlay=false&sgaiHtmlOverlay=false
Host: aps.example.com
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T19:41:38Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-901" duration="PT15S">
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

The two decoders are declared, so option 1 is not ruled out on decoder
count — it is ruled out on its third element, the background image,
which needs a surface the declaration says the device does not have.
Options 2 and 3 fall for the same reason, each needing a non-video
surface. Option 4 survives on one decoder reused sequentially, and the
APS emits it alone. The Player checks it and plays the takeover; the
primary content resumes when the ad ends.

### M.5 D3 — declares an axis it knows and omits one it does not

```
GET /decision/overlay?slot=901&sgaiVideoDecoders=1&sgaiImageOverlay=true
Host: aps.example.com
```

One decoder, an image surface, and no `sgaiHtmlOverlay` at all: the
Player could not determine that axis when it issued the request, so it
omits the parameter entirely rather than sending it empty or with a
placeholder (§5.8.3).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T19:43:02Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-901" duration="PT15S">
        <svta:RenderableAsset form="image"
                              layout="squeezeback-l-shape"
                              assetUrl="https://adcdn.example.com/901/lshape.jpg"/>
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

An absent parameter means the value is **undetermined**, never that the
device lacks the capability (§5.8.4). How an APS resolves an
undetermined axis is its own choice, and this one is conservative: it
emits no option that depends on such an axis. Option 1 is ruled out on
the declared decoder count; option 3 depends on the HTML axis and is
withheld; option 2 needs one decoder plus the declared image surface
and survives, so the APS emits it alone. The Player checks it and
composites the L-shape.

A permissive APS — one that assumes the most capable case for an
undetermined axis — is **equally conformant**. On this candidate it
reaches the same answer, because option 2 stands ahead of the HTML
option in the ADS's order and the order is preserved either way. The
two policies diverge where an option depending on the undetermined axis
sits ahead of the first option that depends on nothing undetermined:
there the conservative APS emits the later option and the permissive
one emits the earlier, and both documents are valid answers to the same
request.

### M.6 D4 — declares nothing

```
GET /decision/overlay?slot=901
Host: aps.example.com
```

Sending a reserved parameter is optional, and this Player sends none
(§5.8.3).

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T19:44:20Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-901" duration="PT15S">

        <!-- 1. side-by-side / double box: video ad + advertiser background -->
        <svta:RenderableAsset form="video"
                              layout="squeezeback-double-box-with-background">
          <svta:BackgroundElement
              assetUrl="https://adcdn.example.com/901/box-bg.jpg"/>
          <ImportedMPD>https://adcdn.example.com/901/box.mpd</ImportedMPD>
        </svta:RenderableAsset>

        <!-- 2. L-shape: image full-frame creative -->
        <svta:RenderableAsset form="image"
                              layout="squeezeback-l-shape"
                              assetUrl="https://adcdn.example.com/901/lshape.jpg"/>

        <!-- 3. HTML lower third -->
        <svta:RenderableAsset form="html"
                              layout="overlay-lower-third"
                              assetUrl="https://adcdn.example.com/901/lower-third.html"/>

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

The APS holds no device information for this request and answers it
anyway, unnarrowed (§4.5.9): it emits all four options in the ADS's
order — the document Annex I shows, differing only in the instant it
was published. The Player walks them in document order — option 1
needs a second decoder it does not have, option 2 needs one decoder
plus an image surface, which it does have — and renders option 2,
stopping there.

This is the row where the relationship between the two annexes stops
being incidental. A Player that declares nothing leaves the APS unable
to narrow, and an APS that cannot narrow emits the full ordered list.
Annex I is not a different design reached by a different route; it is
this one, addressed by a silent Player.

### M.7 D5 — declares one decoder and no surface

```
GET /decision/overlay?slot=901&sgaiVideoDecoders=1&sgaiImageOverlay=false&sgaiHtmlOverlay=false
Host: aps.example.com
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T19:45:51Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>
      <svta:Candidate id="cand-901" duration="PT15S">
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

Every axis is declared and every one of them is negative for concurrent
composition: option 1 needs a second decoder and an image surface,
option 2 an image surface, option 3 an HTML surface. Option 4 needs
neither a second decoder nor a surface, so the APS emits it alone and
the Player plays the takeover. The document the APS produced for D5 and
the one it produced for D2 carry the same single option, reached from
two different declarations.

### M.8 Outcome

| Class | Parameters on the request | Options emitted | Rendered | What the viewer sees |
|---|---|---|---|---|
| D1 | `sgaiVideoDecoders=2`, `sgaiImageOverlay=true`, `sgaiHtmlOverlay=true` | 1 | Option 1 — side-by-side | Primary content shrunk into one box, the ad video in the other, the advertiser's background image filling the bands |
| D2 | `sgaiVideoDecoders=2`, `sgaiImageOverlay=false`, `sgaiHtmlOverlay=false` | 1 | Option 4 — takeover | A full-screen video ad of bounded duration, then the primary content resumes |
| D3 | `sgaiVideoDecoders=1`, `sgaiImageOverlay=true`; HTML axis omitted | 1 | Option 2 — L-shape | Primary content shrunk on top of an image creative filling the whole frame; the visible band forms the "L" |
| D4 | none | 4 | Option 2 — L-shape | The same as D3 |
| D5 | `sgaiVideoDecoders=1`, `sgaiImageOverlay=false`, `sgaiHtmlOverlay=false` | 1 | Option 4 — takeover | The same as D2 |

Every class lands on the rendered result it lands on in Annex I, from
the same ad, the same four options and the same Publisher declaration.
What moved is where the capability check was resolved. The
viewer-visible outcome is identical, which is what makes the two
arrangements two divisions of one responsibility.

### M.9 What declaring does not change

**The Player checks every option it receives.** No presentation option
reaches the screen without passing the Player's own capability check
and the window's allowed-layout check (§4.6.3, §4.6.5), and that holds
for an option the APS computed from the Player's own declaration. Where
the device's state changed between the request and the render — a
second decoder claimed by the platform, thermal pressure, a surface no
longer available — or where the APS derived the wrong option, the
Player passes the option over and falls through candidate by candidate
(§4.6.6), and the primary content keeps playing whatever happens
(§4.6.1). Declaring narrows what arrives; it does not make what
arrives authoritative.

**The Player-visible interface is identical either way.** Nothing in a
resolution document distinguishes "the APS narrowed the list" from
"this is all there was" (§5.3.5, §4.5.3). The D1 document and the D4
document above carry a different number of options and are otherwise
the same answer: same profile, same candidate, same declared duration,
same tracking, same click. A candidate carrying exactly one option is a
complete, conformant candidate whether or not anything was declared —
an APS that wants the suitability call to sit with it sends one, and
the Player renders it or skips the candidate. What a declaration
changes is the basis on which the APS chose, not what the Player does
with what it receives.

## Annex N — A non-linear ad over a replacement that is not advertising

*Informative.*

### N.1 Scenario

The base specification's replacement construct is not an ad construct.
It swaps a bounded span of the primary timeline for an alternative
presentation, and what that presentation contains is the Publisher's
business: an ad break, or a regional blackout slate with its own audio,
or a rights-restricted card. Here it is the second kind — a slate that
carries no advertising at all.

Over that same span the Publisher declares an overlay opportunity, and
the overlay does carry advertising. So for two minutes the screen holds
a non-advertising substitution with an ad composited on top of it, and
the two portions arrive through different paths: the slate from the
Publisher's own endpoint with no ad decision behind it, the overlay from
the APS through the normal resolution exchange.

Nothing in this specification makes the case special, and that is what
the annex demonstrates. A Player cannot observe whether the video it is
decoding is an advertisement, a slate or primary content, so no rule
can be written against the distinction — and this is the case where the
distinction is demonstrably absent while the behaviour is unchanged.
This specification does not specify blackouts: how the Publisher decides
to black out, what the slate contains and how rights are enforced are
outside it.

### N.2 Main MPD

Live content. The replacement window and the overlay window cover the
same span, in two event streams because they are two schemes:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     type="dynamic"
     availabilityStartTime="2026-09-17T10:00:00Z"
     publishTime="2026-09-17T11:58:00Z"
     minimumUpdatePeriod="PT10S"
     timeShiftBufferDepth="PT1H"
     minBufferTime="PT4S">

  <Period id="p1" start="PT0S">

    <!-- The blacked-out span. Resolves to the Publisher's own slate:
         no ADS, no APS, no ad candidate. -->
    <EventStream schemeIdUri="urn:mpeg:dash:event:alternativeMPD:replace:2025"
                 timescale="1000">
      <Event id="1401" presentationTime="7200000" duration="120000">
        <ReplacePresentation uri="https://publisher.example.com/blackout/region-7"
                             earliestResolutionTimeOffset="30000"
                             maxDuration="120000"/>
      </Event>
    </EventStream>

    <!-- The overlay opportunity, covering the same span. -->
    <EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"
                 timescale="1000">
      <Event id="1402" presentationTime="7200000" duration="120000">
        <svta:OverlayPresentation uri="https://aps.example.com/decision/overlay?slot=1402"
                                  earliestResolutionTimeOffset="20000"
                                  maxDuration="20000"
                                  allowedLayouts="overlay-corner overlay-lower-third"/>
      </Event>
    </EventStream>

    <AdaptationSet id="1" contentType="video" mimeType="video/mp4"
                   codecs="avc1.4d401f"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="video/init.mp4"
                       media="video/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="v1" bandwidth="2500000" width="1280" height="720"/>
    </AdaptationSet>

    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4"
                   codecs="mp4a.40.2" lang="en"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000"
                       initialization="audio/init.mp4"
                       media="audio/seg_$Number$.m4s"
                       startNumber="1"/>
      <Representation id="a1" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>

  </Period>
</MPD>
```

The two windows are of different families, so their coincidence is not a
fallback chain: both are live, and each is resolved on its own terms
through its own `@uri`. The overlay window's cap of 20 000 in the event
stream's millisecond timescale bounds the overlay and says nothing about
the two-minute replacement; the replacement's cap of 120 000 bounds the
slate and says nothing about the overlay.

### N.3 The replacement's `ListMPD`

The Publisher's endpoint answers with a `ListMPD` whose single Period
imports the slate:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     profiles="urn:mpeg:dash:profile:list:2024"
     type="list"
     minBufferTime="PT2S"
     publishTime="2026-09-17T11:59:32Z">
  <Period id="slate" duration="PT2M">
    <ImportedMPD earliestResolutionTimeOffset="15.0">https://publisher.example.com/blackout/region-7/slate.mpd</ImportedMPD>
  </Period>
</MPD>
```

It carries no tracking `<EventStream>`, no `<svta:Click>` and no
creative metadata, because there is no ad in it and no ADS or APS took
part in producing it. The document is the base specification's own
construct used for the purpose the base specification names alongside
advertising, and everything in it is baseline.

### N.4 The overlay's resolution document

The APS answers the overlay window with an Overlay Resolution Document
in the ordinary way:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:svta:dash:profile:sgai-overlay-list:2026"
     type="static"
     minBufferTime="PT0S"
     mediaPresentationDuration="PT0S"
     publishTime="2026-09-17T11:59:45Z">
  <Period id="resolution" duration="PT0S">
    <svta:OverlayList>

      <svta:Candidate id="cand-1402" duration="PT20S">
        <svta:RenderableAsset form="video"
                              layout="overlay-corner">
          <ImportedMPD earliestResolutionTimeOffset="5.0">https://adcdn.example.com/1402/corner.mpd</ImportedMPD>
        </svta:RenderableAsset>
        <svta:RenderableAsset form="html"
                              layout="overlay-lower-third"
                              assetUrl="https://adcdn.example.com/1402/strip.html"/>
        <svta:RenderableAsset form="image"
                              layout="overlay-corner"
                              assetUrl="https://adcdn.example.com/1402/corner.png"/>

        <EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"
                     value="1" timescale="1000">
          <Event presentationTime="0"     id="1">https://tracker.example.com/impression?ad=1402</Event>
          <Event presentationTime="10000" id="2">https://tracker.example.com/midpoint?ad=1402</Event>
          <Event presentationTime="20000" id="3">https://tracker.example.com/complete?ad=1402</Event>
        </EventStream>

        <svta:Click clickThroughUrl="https://advertiser.example.com/regional-offer">
          <svta:ClickTracking>https://tracker.example.com/click?ad=1402</svta:ClickTracking>
        </svta:Click>
      </svta:Candidate>

    </svta:OverlayList>
  </Period>
</MPD>
```

Both layout tokens the candidate uses are in the window's
`@allowedLayouts`, and the candidate's `PT20S` converts to 20 000 in the
window's timescale, which equals the cap exactly and is admitted
(§4.6.4). Nothing in the document refers to the replacement, and nothing
needs to: the APS was asked to fill an overlay window and answered that
question.

### N.5 The composition walk

1. **Both windows become current at 7 200 000.** They are of different
   families, so the Player holds two live opportunities rather than a
   primary and a backup.

2. **The replacement is resolved and takes the surface.** The Player
   issues the request against the replacement's `@uri` at or after its
   ERT, receives the `ListMPD` of §N.3, and plays the slate in place of
   the primary content for the declared span. Primary media time keeps
   advancing underneath it, as it does for any replacement, and on
   completion the Player resumes per the event's own semantics.

3. **The overlay is resolved independently.** A separate request against
   the overlay window's `@uri`, a separate document, a separate
   validation. The two resolutions share no state.

4. **The options are validated against the window and the device.** The
   Player walks the three presentation options in document order and
   takes the first whose layout the window admits and whose form and
   layout its device can satisfy. This is the same walk it performs for
   an overlay over primary content; the checks consult the window's
   declarations and the device's capabilities, and neither of those
   mentions what is on the surface.

5. **The chosen form composites over whatever is on the surface.** The
   surface holds the slate, so the overlay composites over the slate.
   The Player does not inspect what is underneath and has no way to: no
   attribute of the window, of the candidate or of the option describes
   it, and the compositing step takes the surface as it finds it. What is
   underneath the overlay is not the overlay's concern.

6. **The ad's own timeline runs on the ad.** Beacon times are relative
   to the overlay's own presentation — offset 0 is its first rendered
   frame — and are independent of the slate's timeline and of the primary
   timeline underneath it. The ClickThrough fires on activation, with no
   presentation time of its own.

7. **The two portions end on their own schedules.** The overlay ends
   when its rendered length reaches the cap, or earlier if the creative
   is shorter; the slate continues to the end of the replaced span and
   the overlay's end changes nothing about it. If the overlay window
   were shorter than the replacement, the slate would simply carry on
   alone.

8. **Where no option is satisfiable, the slate is what remains.**
   The candidate is skipped, the candidates are exhausted, and the
   Player continues with the primary content path — which during this
   span *is* the slate. The viewer sees the slate with no overlay and no
   artefact of any kind.

### N.6 The decoder bookkeeping

The one thing the replacement changes is which presentation occupies the
surface, and the base specification already fixes the consequence: while
an alternative presentation is playing, one access engine outputs media.
The slate therefore occupies the single decoder the primary content
released, exactly as a linear ad in the same window would, and the
overlay's budget is what §5.3.7.3 states for its layout and form:

| | Overlay over the primary content | Overlay over the slate |
|---|---|---|
| What occupies the surface | the primary content | the replacement's slate |
| Video decoders in use before the overlay | 1 | 1 |
| Adding a `video` overlay | 2 | 2 |
| Adding an `image` or `html` overlay | 1, plus one non-video surface | 1, plus one non-video surface |
| Satisfiable on | per §5.3.7.3 | identical |

The accounting is the same because a decoder is a decoder whatever it is
decoding. This is bookkeeping and not a new rule: no row of the
device-class analysis moves, and an implementation that already
composites an overlay over primary content needs nothing further to
composite one over a replacement.

### N.7 Only one of the two portions is an ad

The overlay carries the tracking schedule, the ClickThrough and the slot
cap. The replacement carries none of the three, because it is not an ad:
no ad decision produced it, no beacon belongs to it, and no click leads
away from it. The two portions share the screen and not the contract.

That asymmetry is the reason the case is worth writing down. A reader
who assumes the replacement construct is an advertising construct would
expect the slate to carry an ad's obligations, and would then have to
decide what it means for an ad to carry no tracking. It means nothing,
because the slate is not one.

### N.8 Per device class

The outcomes are those of any coexisting overlay, because the budget is
identical:

| Class | Option selected | What the viewer sees |
|---|---|---|
| **D1** | 1 — `video` / `overlay-corner` | The corner video ad composited over the slate on a second decoder. |
| **D2** | 1 — `video` / `overlay-corner` | The same: two decoders are what this option needs, and no non-video surface is involved. |
| **D3** | 2 — `html` / `overlay-lower-third` | Option 1 is passed over for want of a second decoder; the HTML strip composites over the slate on one decoder plus one surface. |
| **D4** | 3 — `image` / `overlay-corner` | Options 1 and 2 are passed over — no second decoder, no HTML surface — and the still image composites over the slate. |
| **D5** | none | No option is satisfiable, the candidate is skipped, and the slate plays alone for the span. Declining is a defined outcome and not a failure. |

The device class decides which option renders and never decides whether
the surface underneath is advertising: the same five rows hold when the
overlay sits over primary content instead of over a slate.

## Annex O — Test cases and conformance criteria

This annex lists what an implementer can test against, per chapter. It
is informative: the obligations are in chapters 4 to 7, and a test here
is one way of observing one of them, not a new requirement.

Each row names the actor under test, the setup, and the observation that
distinguishes a pass from a fail. A test whose pass condition cannot
fail is not a test, so every row states what the failing case looks
like.

### O.1 Error-condition tests

One test per row of §8.1. The subject is the Player unless the row says
otherwise.

| Test | Condition to create | Pass | Fail looks like |
|---|---|---|---|
| **T-E1** | Point a slot's `@uri` at an unroutable host, with a second overlapping window of the same family declared. | The second window is attempted; with the family exhausted, primary content continues with no visible artefact. | The slot stalls, or the second window is never attempted. |
| **T-E2** | Return `200` with a body of `<not-an-mpd/>`, second window declared. | Treated as a failed execution; the chain advances. | The Player renders something, logs a fatal error, or ends the session. |
| **T-E3** | Ask an overlay slot and answer with a linear `ListMPD` carrying one ad, with a second overlapping window declared. | Treated as a failure to resolve; the chain advances to the second window. | A candidate from the wrong-family document reaches the screen, or the Player stops at the primary content with the second window unattempted. |
| **T-E4** | Answer with the empty Overlay Resolution Document of §5.2.3, second window declared. | The second window is attempted. With `@executeOnce="true"` on the first window, that window remains executable afterwards. | The chain ends at the first window, or the opportunity is marked consumed. |
| **T-E5** | Delay the APS response until after the slot window has elapsed. | The slot does not extend past what the cap bounds for its family; primary content is uninterrupted. On a linear replacement slot with `@clip="true"`, the presentation ends at the scheduled end. | The ad plays past the bound, or the primary timeline is displaced. |
| **T-E6** | Author a slot with no `@maxDuration`; separately, one with `@maxDuration="0"`. | No ad is presented from either slot; primary content continues. | An ad plays from the uncapped slot. |
| **T-E7** | Offer a candidate whose every option needs a surface the device under test lacks, followed by a second candidate the device can satisfy. | The first candidate is skipped and the second renders. No next-window attempt occurs. | The Player advances to the next window, or ends at the primary content with a satisfiable candidate unused. |
| **T-E8** | Offer an option whose `@layout` is outside the window's `@allowedLayouts`, followed by one inside it. | The first option is passed over and the second renders. | The disallowed layout renders. |
| **T-E9** | Offer a candidate whose creative media type is outside §3.3. | No form the device cannot render reaches the screen. | The Player attempts to render an inadmissible carrier. |
| **T-E10** | Cap a slot at 20 s and answer with candidates declaring 15 s and 10 s; then make the second candidate actually run 12 s. | Rendering stops at 20 s cumulative, mid-ad; remaining beacons of the trimmed ad do not fire. | The slot runs 25 s, or beacons past the trim fire. |
| **T-E11** | Return 404 for the second segment of an accepted ad. | The ad aborts and primary content continues uninterrupted. | Playback stalls or the session ends. |
| **T-E12** | Author an `<EventStream>` with an unknown scheme URI, and an unknown foreign-namespace element inside a candidate. | Both are ignored with their subtrees; primary content continues; nothing is rendered from either. | A parse error, or a rendered artefact. |
| **T-E13** | Point a beacon URL at a host returning 500, and separately at an unroutable host. | The ad and the primary content are unaffected; no viewer-visible effect. | The ad aborts, or the failure surfaces to the viewer. |
| **T-E14** | Declare an overlay window and a pause-trigger window overlapping, and pause inside both. | Exactly one non-linear form is on screen at every instant; the overlay is suspended and restored on resume if its window is still open. | Two forms composited at once, or the overlay lost while its window is still open. |
| **T-E15** | Answer a pause slot with two 5 s candidates and `@onCandidatesExhausted="repeat"`, then pause for 30 s. Repeat with `stop`, with `request-again`, and with the attribute absent. | `repeat` re-presents the sequence; `stop` and the absent attribute show the paused frame; `request-again` issues a further request and treats an empty answer as `stop` for the rest of the pause. | Undefined behaviour for any of the four, or a request under `stop`. |

### O.2 Positive-behaviour tests

| Test | Setup | Pass |
|---|---|---|
| **T-P1** | A linear pre-roll slot answered with a two-Period `ListMPD`. | Both ads play back-to-back in declared order; beacons fire at their relative times on each ad's own timeline. |
| **T-P2** | One candidate carrying four options ending in `linear`, run on each of D1..D5. | Each class lands on the first option it can satisfy, and the five outcomes match the budget table of §5.3.7.3. |
| **T-P3** | The same ad, with capability parameters attached and an APS that narrows to one option. | The Player renders that option or skips the candidate; the outcome per class matches T-P2 where the narrowing agreed with the device. |
| **T-P4** | A resolution request from a Player that discloses nothing. | The APS answers with the options unnarrowed; the Player resolves the choice itself. |
| **T-P5** | A `squeezeback-double-box-with-background` option on D1 and on D2. | D1 composites the two boxes plus the background image; D2 passes the option over, on surface type rather than decoder count. |
| **T-P6** | An `image` option and an `html` option on D4. | The image option renders; the HTML option is passed over. |
| **T-P7** | A candidate with a `<svta:Click>` carrying two `<svta:ClickTracking>` children; activate the click. | The destination opens and both tracking URLs fire exactly once. |
| **T-P8** | A candidate with a `<svta:Click>` carrying no `<svta:ClickTracking>`; activate the click. | The destination opens and nothing else fires. |
| **T-P9** | Two beacons sharing an `@id` inside one candidate, and two candidates each carrying a beacon with the same `@id`. | Within the candidate the beacon fires once; across the two candidates both fire. |
| **T-P10** | Primary content at 2×, with a 10 s form. | The form is on screen for 5 s of wall-clock; beacons fire at their scheduled presentation times. |
| **T-P11** | A pause-trigger window with `@executeOnce="true"`; pause twice inside it, with the first pause resolving to a renderable candidate. | The first pause presents a pause ad; the second leaves the primary content uninterrupted. |
| **T-P12** | The same window, with the first pause resolving to no renderable candidate. | The window is not consumed and the second pause presents a pause ad. |
| **T-P13** | A live presentation, paused inside a pause-trigger window for longer than `MPD@timeShiftBufferDepth`. | The pause ad is dismissed on resume and the resumption position is the one the base specification prescribes; primary content continues. |
| **T-P14** | An `image` form with an 8 s candidate duration. | The form is on screen 8 s of presentation time and its beacon origin is the first rendered frame of the asset. |
| **T-P15** | A pause beginning inside a pause window while a linear ad is on screen. | The linear ad is suspended, the pause ad presents, and on resume the linear ad continues from where it stopped. |
| **T-P16** | A hybrid break: a linear event and an overlay event at the same presentation time. | The two slots resolve independently; the overlay composites over the linear ad where the device can satisfy it, and the linear ad plays alone where it cannot. |

### O.3 Document-level tests

These are checked by inspecting an artefact rather than by observing a
session.

| Test | Subject | Pass |
|---|---|---|
| **T-D1** | A main MPD carrying SGAI constructs | Removing every element and attribute outside the DASH namespace leaves a document that validates against the base schema and conforms to the base specification. |
| **T-D2** | An Overlay Resolution Document | Validates against the base schema with the extension subtree present; carries one `<Period>` of `@duration="PT0S"`; every candidate carries at least one presentation option; every `@layout` token is one of §3.2. |
| **T-D3** | The same document | The validator reports **which subtrees it walked**. A report of "valid" that skipped the foreign-namespace subtree has not checked the tracking carrier, the click carrier or the options at all (§8.8). |
| **T-D4** | A sub-MPD | Declares `urn:mpeg:dash:profile:sps:2024`, `@type="static"`, exactly one `<Period>` with `@duration`, and every `@mimeType` from the RFC 4337 registry; carries no `MPD.Metrics` and no `MPD.SupplementalProperty`. |
| **T-D5** | A main MPD with pause-trigger windows | Carries the `<Metrics metrics="PlayList">` declaration (§5.9). |
| **T-D6** | A main MPD | Each family's windows in one `<Period>` sit in a single `<EventStream>`; every slot declares `@maxDuration` and `@allowedLayouts` where its family requires them. |
| **T-D7** | A `<RequestParam>` template for a non-linear slot | Sits as a sibling of an **empty** `EssentialProperty` of scheme `urn:mpeg:dash:urlparam:2025`, at a DASH hierarchy element, and scopes itself with `urn:svta:dash:request:sgai-resolution:2026` rather than `altmpd`. |
| **T-D8** | A profile-conformance check of a document carrying SGAI constructs | The check passes, **and** the report states that the procedure removed the extension-namespace content first, so the check says nothing about those constructs (§4.7.8). |

### O.4 Conformance criteria by chapter

| Chapter | What an implementation is measured against |
|---|---|
| §3 | Every ad-type and layout token it emits or accepts is one of §3.2; every creative carrier is one of §3.3. |
| §4.3 Publisher | Constraints declared in the manifest; a cap on every slot; allowed layouts from the closed set; one event stream per family per Period; a resolution-timing offset; the metric where pause windows exist; a document that stays valid once the extensions are removed. |
| §4.4 ADS | Emits a decision; owns the tracking schedule. Not measured on the cap and not measured on device capability. |
| §4.5 APS | A document that parses and validates, tracking subtree included; of the family that asked; options as an ordered list; creatives on conformant carriers; beacons as callback events; the click in the normative carrier; an unfilled opportunity as a `200` with a body and no candidates; an exhaustion behaviour on every pause document; an answer that depends on no capability parameter. |
| §4.6 Player | Primary content survives every row of §8.1; validation against the window that served the candidate; the cap against actual length; document order honoured, dropping allowed and reordering not; no unsatisfiable form rendered; one non-linear form at a time; a pause ad dismissed on resume; a defined outcome for every class and every family. |
| §4.7 | Each construct classified: placement, extension point, legacy behaviour, and a document that parses and plays once the construct is removed. |
| §5 | The syntax of each construct as its table declares it, including required attributes and enum value spaces. |
| §7 | The per-scenario behaviour, exercised by the tests of §O.2. |

### O.5 What a test harness needs

- **Five device profiles**, one per class of §3.4, distinguished by
  concurrent decoder count and by which surface types composite with
  video. A harness that cannot express "two decoders, no image surface"
  cannot test D2, which is where the type-versus-count distinction
  shows up.
- **A programmable APS** able to return, for one slot: a valid document,
  an empty document, a wrong-family document, an unparseable body, a
  non-`200`, and no response at all. The six are the whole of §8.1's
  document-level rows.
- **A legacy Player**, or a Player build with the SGAI paths compiled
  out, for the tests of §O.3 and Annex G.
- **A beacon sink** that records URL, arrival time and count, so that
  de-duplication and trim-boundary behaviour are observable rather than
  inferred.
- **A validator that reports its own coverage.** Per T-D3, a validator
  that does not say which subtrees it walked cannot be used to
  substantiate a document-level pass.

## Build notes — divergences and open points

This block is **not part of the specification**. It records where this
document departed from the project's own canonical input set, and which
questions it leaves open, so that a reviewer and an automated audit can
see both without diffing two documents.

### Divergences from the canonical input set

Three statements in the project's input documents do not survive the
primary copy of the base specification. This document follows the base
specification and records the divergence here rather than silently
propagating or silently correcting it. The input documents are
human-authored and their correction is not this build's to make.

1. **`UrlParamInfo` does not exist.** The project's linear-interface
   reference writes the URL-parameterisation construct as a
   `<up:UrlParamInfo>` element nested inside an `<EssentialProperty
   schemeIdUri="urn:mpeg:dash:urlparam:2025">`, and cites DASH §I.4 for it.
   The base specification declares no element of that name, in DASH §I.4 or
   anywhere else. The construct is `RequestParam`, of type
   `up:ExtendedUrlInfoType`, specified in DASH §I.3; the enabling
   `EssentialProperty` *"shall be present and have no content"*, so the
   nesting is inadmissible as well as the name; and DASH §I.4 supplies only
   the substitutable state vocabulary, not the element. §5.8.1 of this
   document uses the verified construct and carries the same note for a
   reader arriving from the input document.

2. **The empty resolution falls through, and one rationale in the
   inputs says otherwise.** The input requirement set places a
   well-formed resolution document carrying no candidates on the
   fallback chain, as a failed execution, in both its normative
   criterion and its no-fill requirement — which is what §4.6.8 and
   §5.2.3 of this document implement, and what the project's accepted
   decision record on the question settled. One rationale paragraph in
   the same input document still states the opposite, that such a
   document *"ends the chain"*. That paragraph predates the decision.
   This document follows the normative criterion and the decision
   record. The consequence is viewer-visible and worth naming: a
   Publisher's backup window is now attempted after an unsold
   opportunity, where the previous published build left it untouched.

3. **The descriptor axis is wider than the input rules record.** The
   input extension rules state of the two vendor descriptor carriers
   that *"they sit on AdaptationSet / Representation /
   Sub-Representation, so both inherit DR-5's MIME constraint"*. The
   base schema declares `SupplementalProperty` and `EssentialProperty`
   as children of `MPDtype`, `RepresentationBaseType`,
   `EventStreamType` and `EventType`, `SupplementalProperty` on
   `PeriodType` and on `AlternativeMPDEventType`, and
   `<xs:any namespace="##other" processContents="lax"/>` on all of
   those. A descriptor hosted on an `<Event>`, an `<EventStream>` or an
   alternative-MPD event element therefore never touches
   `Representation@mimeType` and inherits no media-type constraint.
   §4.7.3 of this document records the placements read from the schema,
   including two the input rules do not mention: `<Period>` admits
   `SupplementalProperty` and not `EssentialProperty`, and
   `ImportedMpdType` is simple content with `anyAttribute` and no
   `xs:any`, so a foreign-namespace **attribute** may hang off
   `<ImportedMPD>` and a child **element** may not.

   This changes the argument and not the outcome. §5.3.2 rejects both
   descriptor carriers for the non-audiovisual asset URL on what a
   descriptor can **carry** — one scheme URI and one `@value` string,
   against a presentation option that is three inseparable facts and
   has to be an element to take its place in an ordered list — rather
   than on a media-type constraint that is not present at that
   placement.

   A fourth input rule, on `MPD@type="list"`, rests on a premise the
   primary copy does not support: DASH §5.3.1.4 defines the value in the
   main body of the base specification with its own constraints,
   independently of the List profile of DASH §8.14, and DASH §8.14 rule 1 states
   only that a List MPD must declare it. §5.2.2.2 of this document
   therefore declines the value on a stated design ground — every other
   mention of it binds it to Linked Periods and the alternative-MPD
   flow — and not on the claim that the value is unavailable outside
   the profile.

### Two base-standard constructs weighed rather than passed over

4. **The supplementary video descriptor**
   (`urn:mpeg:dash:supv:2022`, DASH §5.8.5.16) is the base specification's
   own picture-in-picture signal and the nearest miss to the
   composition layouts of this document. It is rejected in writing in
   §5.1.3, on four stated grounds, rather than by silence. Its
   single-decoder VVC path (DASH §5.8.5.16.4) is also the technique this
   document declares out of scope in §1.2, and §1.2 now cites the
   clause: without the citation the exclusion reads as though the
   technique lived outside the base specification.

5. **The `<URN / tag URI>` row of Table I.4** makes the value space of
   `@includeInRequests` open, and the base specification prescribes
   that a client *"shall drop unknown URIs"* from it. That is the hook
   for scoping a Publisher's query template to the non-linear
   resolution request, which `altmpd` does not reach because it names
   Alternative MPD requests only. This document mints
   `urn:svta:dash:request:sgai-resolution:2026` for it (§2.1, §5.8.1).

### Vocabulary change against the previously published build

6. **The pause family has two layout tokens, not one.** The accepted
   set of §3.2 carries `pause-fullscreen` and `pause-partial`, and no
   bare `pause` token. A Publisher can therefore admit one surface and
   exclude the other in `@allowedLayouts`, which a single token made
   impossible. The budget table of §5.3.7.3 is split accordingly.

7. **The pause family's three new capabilities are specified.** The
   exhaustion behaviour when candidates run out inside a pause
   (§5.2.2.3, §4.6.11), the once-per-session bound on a pause window
   (§5.1.4.1, §4.6.12), and the derivation of pause-ad delivery from
   the base specification's `PlayList` metric (§5.9, §4.6.18). The
   second closes a question the previous published build recorded as
   open: `@executeOnce` had no defined meaning on a pause-trigger
   window, and the two available readings differed by every pause
   after the first.

### Open points

Each of these is a question this document does not close, stated where
it arises and repeated here so the list is in one place.

| Open point | Where |
|---|---|
| A slot declaration carrying no cap yields no ads, which diverges from the base specification's unbounded default. Which failure is worse is a working-group call. | §4.6.4, §8.1 E6 |
| No retry count, backoff or deadline is fixed for the resolution request, and no Player response is defined for a document that lands after the window has elapsed. | §8.1 E1, E5 |
| A creative carrier outside the admissible set that the device can nevertheless render carries no obligation either way. | §8.1 E9 |
| `@allowedLayouts` has no "unrestricted" value, so a window admits exactly the tokens it lists. | §8.1 E8 |
| Whether to mint an interoperability-point URI that explicitly includes the extension namespace, so that a profile-conformance check covers these constructs, or to stand on "a valid base document plus constructs a conformant Player reads". This document states the second. | §4.7.8 |
| Whether a second resolution request inside one pause is the same opportunity or a new one. The two readings are identical at the Player and differ only in accounting between the APS and the ADS, which this document does not observe. | §4.6.11 |
| Whether the document should record that an APS narrowed a candidate's options, which it currently cannot — nothing distinguishes a filtered list from a short one. | §5.3.5, Annex M |
| Whether a Publisher needs a way to scope a baseline linear break to Players that predate this specification. There is none today, so a break authored alongside a non-linear window is a hybrid slot to a current Player, and the Publisher chooses between composing both and serving neither population the fallback. | §4.7.7, §5.1.5 |
| Whether a fullscreen video pause ad is reachable on the worst-case device class. The re-tasking question the conditional rows rest on is scoped to the classes that can present an ad surface at all. | §5.3.7.3 |

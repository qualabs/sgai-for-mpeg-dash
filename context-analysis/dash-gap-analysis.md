[GROUNDED_BY=iso-23009-1-2026-pdf]

# DASH 6th edition gap analysis (SGAI for linear + non-linear ads)

This document compares the requirements in
[`../context/03-requirements.md`](../context/03-requirements.md) (R1–R34)
and the use cases in
[`../context/04-use-cases.md`](../context/04-use-cases.md) (UC-01–UC-14)
against what the base specification provides, and identifies what the SGAI
specification must add or extend. It is the bridge between the canonical
context and the spec build.

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY) when stating
requirements.

**Grounding.** Every load-bearing claim about the base specification below was
verified against the primary copy of the edition declared in
[`../context/00-normative-base.md`](../context/00-normative-base.md), by
extracting it to text and searching it. Each claim carries its clause number
**and** a quoted sentence; a clause number alone is not grounding. Negative
claims ("no construct exists for X") were produced by searches whose ability to
find was first demonstrated against terms known to be present in the same
document — the counts are reported inline where the negative is load-bearing.
Claims that could not be verified against the primary copy are tagged
`[inferred]`.

## 1. Scope

In scope:

- Every requirement R1–R34 in `../context/03-requirements.md` against the
  capabilities the base specification provides.
- The use cases UC-01–UC-14 in `../context/04-use-cases.md` as the behavioural
  check on those capabilities across device classes D1–D5.
- The constructs, carriers and conformance rules the spec must add, and the
  existing machinery it must reuse first (R8 / R9).

Out of scope:

- The APS-to-ADS and ADS-side API contracts (R18) — opaque to the spec.
- VAST version pinning (R11) — the spec is VAST-version-agnostic.
- ABR, DRM, transport, low-latency tuning — orthogonal to SGAI.
- The IAB ad-type vocabulary itself (R12) — owned by the IAB and analysed
  separately in [`iab-ad-templates.md`](iab-ad-templates.md).
- The linear SGAI baseline mechanics themselves — inventoried in
  [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
  and absorbed here as the starting point, not re-derived.
- The syntax of the constructs the gaps call for. This document says what is
  missing and which existing machinery constrains the answer; which element or
  attribute carries it is the spec build's decision.

## 2. Coverage matrix — R × DASH 6th capability

Cells: **full** (the base specification covers it normatively and the spec
reuses it as-is), **partial** (covered for the linear case only, or the
machinery exists but is not bound to what the requirement needs), **gap** (no
native construct — the spec must add one), **N/A** (governance or
document-level; the base specification has nothing to say). The grouping
follows the sub-sections of `../context/03-requirements.md`.

### Contract foundations

| R | Theme | Base specification status |
|---|---|---|
| R1 | Extends the base edition; legacy Player ignores and keeps playing | **full** — §5.2.1 carries the authoring obligation: *"the MPD shall be authored such that, after XML attributes or elements in the other namespaces than the DASH namespace are removed, the result is a valid XML document formatted according to that schema and that conforms to this document."* The schema backs it: `EventType` is declared `mixed="true"` with `<xs:any namespace="##other" processContents="lax"/>` and `<xs:anyAttribute namespace="##other"/>` (§5.10.2.3), and §5.10.2.1 states that *"the Event element may contain further XML elements meaningful for a particular event scheme. These may be defined in this document … or in some external namespace."* Per-scheme skip is the other half: *"This enables a DASH Client or the application to subscribe to an Event Stream of interest and ignore Event Streams that are of no relevance or interest"* (§5.10.1). The ignore-if-unknown contract is inherited, not invented. One caveat under R1.2 is in G10. |
| R2 | Four actors, fixed roles | **partial** — §5.16 wires two legs only: the MPD author and the client. The APS is whatever answers `AlternativeMPDEventType@uri` — §5.16.5.2 says of it only that it *"specifies the URI (typically, an HTTP URL) of the MPD describing the alternative Media Presentation"* — and the ADS is invisible. No construct binds an actor to a responsibility, so R2 is carried entirely by spec prose and conformance criteria. |
| R11 | No dependency on VAST | **N/A** — the base specification is VAST-agnostic. It names VAST twice, both times non-normatively: an abbreviation entry, and §5.10.4.5.1 NOTE 1, *"HTTP GET (as opposed to HEAD) is used in alignment with IAB VAST."* Nothing to add or avoid. |
| R18 | Player-visible interface only | **N/A** — governance; the base specification does not constrain server-side APIs. |
| R29 | Player-declared capability parameters on the resolution request | **gap**, confirmed negatively. The edition's upstream channel is Annex I.3 extended HTTP GET parametrization, whose element is `RequestParam` of type `ExtendedUrlInfoType`; `@includeInRequests="altmpd"` scopes parameters to *"all requests for MPDs representing the alternative Media Presentation, as defined in subclause 5.16"* (Table I.4). The state vocabulary it can substitute is Table I.5 in full — `audio`, `video`, `lang#[audio|text]`, `encryption`, `cmcd#[key]`, `execution-delta#[id]`, `expected-duration#[id]`, `execution-count#[id]`, `previous-state` — and it contains no decoder count, no image-rendering axis and no HTML-overlay axis. I.4.1 states what the vocabulary is for: *"there is a need to express knowledge of the current state of the player."* State, not capability. See G6, which also records the one extension hook the mechanism does carry. |

### Opportunity declaration

| R | Theme | Base specification status |
|---|---|---|
| R4 | Publisher-declared max slot duration, Player-enforced | **partial** — the cap, the trim, the zero case and the unbounded default all exist for the linear slot. §5.16.5.2 defines `@maxDuration` as *"maximum duration of the Alternative Presentation, expressed in units of `EventStream@timescale`"*, with *"If the Alternative Presentation initiated by this event has a longer duration than specified in this element, it shall be terminated at the end of this duration"*, *"If the value of `@maxDuration` is zero, the event is not executed"* (R4.7), and *"If absent, the value is assumed to be infinity, in which case the current presentation resumes only when the alternative presentation terminates"* (R4.8). The replacement asymmetry R4.6 rests on is `@clip`, default `true`: *"If the value of this attribute is \"true\", the alternative presentation shall terminate at the latest at time PRT + APDmax. If the value is \"false\", the presentation shall terminate at time PRTA + APDmax"* (Table 62). What is absent: any non-linear slot to cap, the enforcement-against-actual-length rule (R4.5), and the cross-timebase conversion rule (R4.9) — the cap is in `EventStream@timescale` units while a candidate's duration is an `xs:duration`. |
| R31 | Pause window bounds where, not how long | **gap** — no construct in the edition is triggered by a viewer pause (G2), so there is no window to bound and nothing that distinguishes bounding a region from bounding a duration. |
| R12 | Closed IAB ad-type / placement set | **N/A** for the vocabulary (owned by the IAB); **gap** for the carrier. Searches for the placement names return zero across the whole document: `squeezeback` 0, `L-shape` 0, `side-by-side` 0, `banner` 0, and `overlay` 1 — a single occurrence in Annex K.3 listing *"second screen applications, overlays, etc."* as consumers of a service description, not an ad layout. No construct carries an ad-type or visual-placement token, so the Publisher's allowed-layout declaration is net new. |
| R15 | Creative carriers: video, image, HTML | **partial** — video is native, reached via `<ImportedMPD>` and bound by §5.3.2.6.1: *"MPDs referenced in the ImportedMPD element shall be restricted to the constraints of a single period profile as defined in 8.15."* Image and HTML are a **gap**, and doubly so: §7.3.1 states *"The @mimeType attribute of each Representation shall be provided according to IETF RFC 4337"*, and the edition never mentions a non-AV media type at all — `image/` 0 occurrences, `text/html` 0, `thumbnail` 0, against `video/mp4` 79, `audio/mp4` 36 and `application/ttml` 2 in the same search. There is nothing to relax on the media axis; there is something absent from it. |

### Selection and ordering

| R | Theme | Base specification status |
|---|---|---|
| R5 | Candidates carry ordered presentation options; Player renders the first it can satisfy | **gap** — a List MPD is a playlist, not a set of alternatives: §8.14 introduces the profile as *"intended for use in conjunction with the Alternative MPD event (see subclause 5.16)"* and its Periods play in sequence. No construct lets one ad candidate carry an ordered list of (form + layout) options. Three constructs express ordered preference and each is scoped elsewhere — `Preselection` (§5.3.11), `@selectionPriority` (§5.3.7.2) and `urn:mpeg:dash:fallback:2016` (§5.11.3). R8 requires all three to be weighed and the departure recorded; see G3. |
| R7 | Honour the resolution document's order | **partial** — declared-order playback is already the List MPD semantics, and the edition already drops an ad Period that fails to resolve: §5.3.2.6.3 step 2, *"In case the resolution fails, and the Linked Period contains valid content, the ImportedMPD element is removed, and consequently the Linked Period becomes a regular Period and is treated as such."* Missing is the rest of R7's vocabulary: drop-before-play on declared duration, trim-during-play on actual length, and the prohibition on re-ordering or deduplicating what survives. |
| R30 | An unsold opportunity is a document, not an error | **partial** — the **semantics** are the base specification's and are adopted unchanged. §5.16.2.2.6 lists *"Alternative MPD is a List MPD, and merge process resulted in no available media"* among the conditions under which *"Execution fails"*, with the outcome *"A failed execution results in smooth continued playback of the main media presentation"*, and NOTE 3 gives R30.2 directly: *"The counter E.c has not been incremented due to the failure, consequently if E.c = 0 the event can still be executed in the future even if the value of @executeOnce is \"true\"."* What is missing is the document's **shape**: the schema declares `<xs:element name="Period" type="PeriodType" maxOccurs="unbounded"/>` with no `minOccurs`, so a resolution document carrying zero Periods does not validate. See G8. |

### Presentation

| R | Theme | Base specification status |
|---|---|---|
| R3 | Diverse device classes D1–D5 | **N/A** — the edition models codecs and bandwidth, not concurrent decoder budget or overlay-surface capability. Its only device vocabulary is reporting-side: Annex D.4.7 *Device information* logs displayed video resolution, physical screen width and horizontal field of view. `concurrent decoder` and `decoder count` return 0 occurrences. The capability axes R3 separates are what R29's reserved set must express. |
| R16 | Pause-ad lifecycle bound to pause state | **gap** — event processing is driven by presentation time, and a pause stops it. §5.16.2.2.5 NOTE: *"Since there is no playhead-triggered processing during the listen mode, processing always resumes at the playhead position PHP = RT."* The pause is visible to the edition in four places and none is a trigger: trick-mode handling (*"The client may pause or stop a Media Presentation. In this case, the client simply stops requesting Media Segments"*, §A.5), the client model (§4.2), the `PlayList` metric (§D.4.6), and the informative dual-client message `adjust speed(S)` where *"S = 0 is pause"* (§A.14.2). See G2. |
| R32 | Exhausted pause-ad candidates while still paused | **gap** — depends on the pause construct that does not exist. The edition has no repeat / request-again / stop vocabulary for a slot, because no slot of its own outlives its media. |
| R34 | Pause window may be once-per-session | **partial** — the capability exists for timeline events and its counter semantics are exactly what R34.3 needs. §5.16.5.2 defines `@executeOnce` as specifying *"whether the event is executed only once during the media presentation"*; §5.16.2.2.2 defines `E.c` as *"Execution counter (number of times alternative MPD playback successfully started)"*; and §5.16.2.2.6 NOTE 3 makes a failed attempt non-consuming. What does not reach a pause window is the trigger: the counter increments when *"the alternative media presentation triggered by an event successfully starts playing"* (§5.16.2.2.6), which is a playhead event, not a viewer pause. |
| R19 | Ad playback speed follows primary content | **partial** — the rate model exists. `@maxPlayoutRate` (§5.3.7.2) *"specifies the maximum playout rate as a multiple of the regular playout rate … If not present on any level, the value is 1"*; Annex K.3 supplies service-declared `PlaybackRate@min` / `@max`; §D.4.6 defines `playbackspeed` as *"The playback speed relative to normal playback speed (i.e. normal forward playback speed is 1.0)"*; and §A.14.2 already ties two presentations to one speed — *"on reception, the main client will adjust its playhead propagation speed. As a result, media time elapses at the same speed in both clients."* Absent is the binding R19 needs: nothing ties an ad form's on-screen length, or the slot cap, to that rate, and nothing gives a duration to a form with no intrinsic media (R19.4). |
| R21 | Pause-ad fullscreen or partial overlay | **gap** — depends on the pause-ad construct that does not exist (R16), and on the composition facility that does not exist (R26 / R27). |
| R25 | Pause-ad presentation-time freeze in live content | **partial, and in conflict** — the freeze is the edition's own playhead behaviour, but the edition bounds it normatively and R25 as written does not. §5.16.2.2.5 step 1a: *"In case of live main media presentation, this involves clipping RT to the timeshift buffer (i.e. the time interval between TSBS and PHPLE)."* Table 62 states it for the resumption point: *"if RT is in the past, the playback shall start from the oldest available media segment (the edge of the timeshift buffer). Similarly, if RT is in the future, the playback shall start from the most recent available segment (i.e. the live edge)"*, and NOTE 2 names the cause — *"The above can happen in case a user pauses the alternative Media Presentation."* See G9. |
| R26 | Side-by-side / double-box with background element | **gap** — no compositing facility exists. Two constructs come close and neither is one. Annex H.1's Spatial Relationship Description positions encoded video: *"A Spatial Object is represented by either an Adaptation Set or a Sub-Representation … a spatial relationship may express that a video represents a spatial part of another full-frame video (e.g. a region of interest, or a tile)"*, with *"SRD information shall be contained exclusively in these two MPD elements."* §5.8.5.16.1's supplementary video descriptor (`urn:mpeg:dash:supv:2022`) is the nearer one and disclaims the composition: it offers *"the ability to include a video with a smaller spatial resolution within a video with a bigger spatial resolution"*, and *"Potential manipulation of the stream and the composition of the main video and the supplementary video are out of the scope of the DASH client."* Both are video-to-video; neither carries an image background or an ad surface. See G1. |
| R27 | L-shape / squeezeback, one full-frame ad creative | **gap** — same as R26, and the creative may be an image or HTML surface, which R15 already shows has no carrier on the media axis. |

### Interaction and composition rules

| R | Theme | Base specification status |
|---|---|---|
| R14 | Sequential non-linear candidates within a slot | **gap** — there is no non-linear slot to sequence candidates inside. The ordering contract itself is borrowable from the List MPD profile once the slot exists. |
| R17 | Pause-ad priority over overlay, and over linear | **gap** — depends on the R14 / R16 constructs. R17.5's linear leg has a precedent worth citing rather than a carrier: during a replacement the main presentation is suspended in listen mode, where the access engine *"does not output media to the media engine"* (§4.2), which is the edition's own model of one presentation standing down for another. |
| R20 | Overlapping same-family windows: first-window-wins with fallback | **partial** — for the **linear family the rule is the base specification's and is adopted verbatim**. §5.16.2.2.5 step 2: events are processed *"in its priority order (from oldest PRT to the most recent)"*, and *"If execution fails, steps a-c above are repeated for next events in QE, until: — Execution succeeds, or — PRT of the topmost event in the queue is in the future (i.e. PRT > PHP), or — The queue is empty"*, closing with *"If no event can be successfully executed, the playback continues uninterrupted."* The queue is *"a priority queue of references to a subset of events in table T, ordered by the presentation time PRT"* (§5.16.2.2.2), which is R20.3's ordering. R20.2's single-stream rule is §5.10.2.1: *"A Period shall contain at most one EventStream element with the same value of the @schemeIdUri attribute and the value of the @value attribute, i.e. all Events of one type shall be clustered in one Event Stream."* What is **gap**: the queue exists only for Alternative MPD events, so the non-linear families inherit nothing; and R20.3's tie-break by document position, R20.4's family-mismatch rule and R20.5's per-window binding have no base anchor at all. See G7. |
| R22 | At most one active non-linear form | **gap** — the edition has no concurrently presented ad surface to bound. Its own single-alternative model is the same reasoning applied to linear and is the precedent R22 should cite: *"For the duration of the alternative media presentation, the alternative access engine outputs media to the media engine, while the main client will be paused or be in a listen mode"* (§4.2). |

### Tracking

| R | Theme | Base specification status |
|---|---|---|
| R6 | Tracking beacon carrier | **full** — §5.10.4.5.1: *"DASH Callback events are indications in the content that it is expected by a DASH Client to issue an HTTP GET request to a given URL and ignore the HTTP response. These event schemes are identified by the URN \"urn:mpeg:dash:event:callback:2015\""*, and *"A content author may use such an event for tracking play-back of specific content on a server that is not included in the media path."* That is a beacon, named as one. Dispatch is on-start (Table A.3). One authoring correction the spec must carry: `Event@messageData` is declared `use="prohibited"` in the 6th-edition schema, *"Deprecated in favor of carrying the message information in the value space of the event"* (§5.10.2.3), so the beacon URL rides in the `Event` element's content. R6.5's per-candidate de-duplication key and R6.7's validation obligation have no base anchor and are spec-side. |
| R13 | ADS-directed beacon schedule, relative timings | **partial** — the carrier is full (R6) and the relative timebase falls out of the sub-MPD's own Period timeline. The obligations R13 adds — the Player executes the schedule it reads, and stops firing at an R4 trim boundary — are spec-side. R13.4's prohibition on a parallel scheme is satisfied by reuse, not by anything the base specification says. |
| R23 | Application-level ad metadata carrier | **gap** — `AdSystem`, `AdTitle` and `UniversalAdId` each return 0 occurrences in the edition. Conveyance is via a foreign-namespace element under §5.2.1; a legacy client removes it under the same clause's authoring obligation, so nothing in the ad presentation breaks. Low-stakes by construction, since R23 makes emitting and reading both optional. |
| R24 | Non-AV creative asset carrier | **gap**, and the closing facts are narrower than DR-6 records. The RFC 4337 constraint of §7.3.1 binds `Representation@mimeType`, and §5.3.2.2 Table 4 closes the events-only Period: *"At least one Adaptation Set shall be present in each Period unless the value of the @duration attribute of the Period is set to zero."* But the descriptor and open-content axes are **not** confined to the media elements: the schema declares `SupplementalProperty` and `EssentialProperty` children on `MPDtype`, `PeriodType`, `RepresentationBaseType`, `EventStreamType` and `EventType`, and `<xs:any namespace="##other">` on all of those plus `DescriptorType` itself. A carrier hosted on `<Event>` or `<EventStream>` therefore never touches the MIME axis. See G4. |
| R28 | ClickThrough carrier, normative and interoperable | **gap**, and structurally so. `ClickThrough` returns 0 occurrences. The deeper absence is the trigger: every event is evaluated against presentation time, and the callback scheme in particular fires at a scheduled one and *"the client is expected to entirely ignore the response"* (§5.10.4.5.1). A click has no presentation time. The edition does contemplate user action — `@skipAfter` describes *"the moment the rest of that presentation may be skipped by the application in response to a user action"* (§5.16.5.2) — and Annex L does fire an HTTP request off the timeline on a selection, which is the precedent R8 wants. See G5. |
| R33 | Pause-ad delivery measured with the base play-list metric | **full for the metric, partial for its availability.** §D.4.6 Table D.5 defines `PlayList` as *"A list of playback periods. A playback period is the time interval between a user action and whichever occurs soonest of the next user action, the end of playback or a failure that stops playback"*, with `starttype` including *"Resume - Resume from pause"* and `stopreason` including *"UserRequest - User request"* and *"Rebuffering - Rebuffering"* — exactly the two fields R33 derives the paused interval from. §5.9.1 supplies both R33.3 and R33.4: *"This document does not define mechanisms for reporting metrics; however, it does define a set of metrics and a mechanism that may be used by the service provider to trigger metric collection and reporting at the clients, if a reporting mechanism is available. The trigger mechanism is based on the Metrics element in the MPD."* The partial is a placement constraint R33.4 must respect: §8.15.2 forbids `MPD.Metrics` in a Single-Period Static MPD, so the declaration belongs on the primary MPD and can never travel in an imported ad MPD. |

### Governance

| R | Theme | Base specification status |
|---|---|---|
| R8 | Justify any addition or omission | **N/A** — spec-authoring obligation. §4 of this document is its input. |
| R9 | Minimise net new constructs | **N/A** — spec-authoring obligation. |
| R10 | Do not recreate a layout system | **N/A** — the edition carries no layout primitives to recreate, and Annex H SRD is deliberately not one (see R26). |

## 3. Gaps detail

Ten gaps follow from the matrix.

### G1 — No ad-composition construct exists, and the two that come closest are video-to-video (R14, R17, R21, R22, R26, R27; and the carrier for R4 and R12 on non-linear slots)

The edition's ad machinery is substitutive by definition. §5.16.1: *"An
alternative Media Presentation is a presentation that replaces the main Media
Presentation at a certain point on the media timeline for a duration of time.
After the playback of the alternative Media Presentation is complete, the
playback is continued with the main Media Presentation."* The two schemes it
offers are insertion, which *"may be inserted in the media time of the Main
Presentation, i.e. time-shift the part of the Main Presentation which is played
after the alternative Media Presentation"*, and replacement, where *"the main
Media Presentation is not being output, but its media time progresses at the
same speed as the currently playing alternative Media Presentation."* Neither
composes anything; both swap.

Three constructs elsewhere in the edition are close enough that R8 requires each
to be weighed and rejected in writing, and one of them is not named anywhere in
`context/`:

- **§5.8.5.16 supplementary video descriptor (`urn:mpeg:dash:supv:2022`)** is
  the nearest miss and the one the context documents do not mention. It exists
  precisely to signal two video surfaces of different sizes in one experience:
  *"Supplementary video services (sometimes referred to as picture-in-picture
  services) offer the ability to include a video with a smaller spatial
  resolution within a video with a bigger spatial resolution."* The main video's
  Representations sit in the Main Adaptation Set of a `Preselection` and the
  supplementary video's in a Partial Adaptation Set. It is rejected for R26 /
  R27 for a stated reason rather than an assumed one: it carries no ad, no
  layout token and no non-video surface, and it explicitly hands the
  composition back — *"Potential manipulation of the stream and the composition
  of the main video and the supplementary video are out of the scope of the DASH
  client."* Its `SupVideoInfo@processingInfo` is a codec-level string whose
  *"syntax and sematic … are usually defined by the decoder specifications"*.

  It matters beyond the rejection for a second reason. §5.8.5.16.4 specifies
  `@processingInfo` for VVC such that the descriptor *"enables achieving
  picture-in-picture using a single VVC decoder, where the @processingInfo is
  used to signal the possibility of replacing the portions of the main video
  stream with the supplement video stream before sending to a single VVC
  decoder. This way, separate decoding of the main video and the supplementary
  video is avoided."* That is the technique OOS-6 declares out of scope for this
  edition, already standardised in the document this specification extends. The
  OOS-6 exclusion stands as a scope decision, but it should cite this clause:
  the entry currently reads as though the technique lives outside the base
  specification.

- **Annex H SRD** (`urn:mpeg:dash:srd:2014`) positions encoded video tracks in a
  shared coordinate system for tiling and region-of-interest selection, and is
  confined to two elements — *"SRD information shall be contained exclusively in
  these two MPD elements (AdaptationSet and SubRepresentation)"* (§H.1).
  Reusing it would both misuse the construct and build the parallel layout
  system R10 forbids.

- **Annex L `urn:mpeg:dash:nonlinearplayback:2020`** is normative and, despite
  the name, is not about non-linear ads: *"This Annex provides Nonlinear
  Playback capabilities, to serve Interactive Storyline content"* (§L.1), modelled
  as a directed acyclic graph in which *"the graph edges … represent the
  different Periods and the graph nodes (S0, S1 …) contain the available
  decisions"* (§L.2). It defines no overlay, no composition and no ad semantics.
  It is a **precedent**, not a carrier — see G2 and G5.

Verified negatively across the whole edition: `squeezeback` 0 occurrences,
`L-shape` 0, `side-by-side` 0, `banner` 0, `overlay` 1 (Annex K.3, unrelated).
The same search over terms known to be present returned `advertis` 15,
`picture-in-picture` 3 and `VAST` 5, so the zeros are the document's and not the
instrument's.

What the spec must add, under the SVTA Ads WG namespace per
[`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md):

- A non-linear **opportunity declaration** in the primary MPD, carrying the
  Publisher's allowed-layout set (R12), the duration cap (R4) and the
  concurrency cap. §5.10.2.1 already authorises its shape — *"the Event element
  may contain further XML elements meaningful for a particular event scheme.
  These may be defined in this document … or in some external namespace"* — so
  this is an extension of an existing carrier rather than a new one.
- A non-linear **resolution document** carrying the candidates, their
  presentation options (G3) and their tracking (R6 / R13). One base rule closes
  part of the design space before it opens: §8.14 rule 5, *"List MPDs shall not
  contain Alternative MPD events."* A resolution document that reuses the List
  MPD structure cannot declare a nested ad opportunity inside itself, so an
  overlay or pause window is signalled from the primary MPD and nowhere else.
  UC-08's shared candidate has to be expressed Publisher-side.
- The composition rules as Player obligations: one active form at a time (R22),
  candidates sequenced in declared order (R14), the side-by-side with its image
  background (R26), the two-element L-shape (R27), and the cross-family priority
  of R17 including its linear leg (R17.5).

### G2 — No pause-state trigger anywhere in the edition (R16, R21, R31, R32, R34)

Every event in the edition is scheduled against presentation time. §5.10.1:
*"Events are timed, i.e. each event starts at a specific media presentation time
and may have a duration."* A pause stops presentation time, and with it the
processing: §5.16.2.2.5 closes with the NOTE *"Since there is no
playhead-triggered processing during the listen mode, processing always resumes
at the playhead position PHP = RT."*

The pause is visible to the edition in four places, and none of them is a
trigger:

- §A.5, as client behaviour: *"The client may pause or stop a Media
  Presentation. In this case, the client simply stops requesting Media Segments
  or parts thereof."*
- §4.2, as a playhead condition: *"the media time and the corresponding playhead
  can change, for example, if the media engine is instructed with seek or pause
  operations."*
- §D.4.6, as a report: `starttype` value *"Resume - Resume from pause"* and
  `stopreason` value *"UserRequest - User request"*. This is what R33 measures
  with, and it is a record after the fact.
- §A.14.2, informative, as a speed: the alternative client's `adjust speed(S)`
  message, where *"S = 1 is normal playback, S = 1.03 is a 3 % speedup due to
  playback speed modulation, S = 0 is pause, etc."*

The shape the spec must take follows from that asymmetry. What is declared on
the timeline is the **window of validity**, which a timeline-scheduled `<Event>`
expresses natively and which is exactly what R31 says the window bounds — where,
not how long. The **trigger** is Player-side and fires on the pause transition
inside that window. R16's lifecycle, R21's admissible surfaces, R32's
exhaustion behaviour and R34's once-per-session bound are then Player
obligations the spec states; the base specification contributes the window's
placement and nothing else.

Annex L is the precedent R8 wants cited, and the parallel is exact: there too a
timeline-anchored `<Event>` declares a window — *"the Event@presentationTime and
Event@duration attributes are used to indicate the start and the duration of the
selection window"* (§L.3.4.2) — while the decision that resolves it happens off
the timeline, *"The DASH Client signals the chosen edge to play after the end of
the current by firing a callback at the @contactURL of the respective Event"*
(§L.3.3). A window on the timeline whose trigger is not the playhead is
therefore not novel in this edition.

For R34 the counter semantics are already right and only the trigger has to be
restated. §5.16.2.2.6: the counter increments when *"the alternative media
presentation triggered by an event successfully starts playing"*, and NOTE 3
makes a failed attempt non-consuming. R34.3's "consumed when a pause ad begins
rendering, not when the pause occurs" is that rule with the render event
substituted for the playhead event, which is what the spec should say rather
than inventing a bound.

### G3 — No per-candidate ordered presentation options (R5, R7)

A List MPD sequences the ads the ADS already chose. There is no construct in
which a **single** candidate offers an **ordered list of alternative
presentation options** and the client renders the first it can satisfy — the
model that makes UC-09 resolve on D1 through D5 without the ADS or the APS
holding a device matrix (R5.4), and that makes UC-13 indistinguishable from it
at the Player.

The edition does contain ordered preference, three times:

- **`Preselection` (§5.3.11.1)** *"define user experiences that can be selected
  by the DASH Client"* and *"encompasses a subset of media components such that
  the media components can be selected and combined into a complete
  experience"*. It combines components into one jointly rendered experience, not
  alternatives to choose between; `@preselectionComponents` is *"a white space
  separated list in processing order"*, and `@order` selects conformance rules
  for segment tracks (`undefined` / `time-ordered` / `fully-ordered`), not
  preference.
- **`@selectionPriority` (§5.3.7.2)** *"specifies the selection priority for the
  described data structures … In the absence of other information, higher
  numbers are the preferred selection over lower numbers"*, default 1. It is a
  numeric hint on `RepresentationBaseType`, running in the opposite direction
  from document order, and it is explicitly conditional on there being no other
  information.
- **`urn:mpeg:dash:fallback:2016` (§5.11.3)** states R5's rule almost verbatim —
  *"The @value of this descriptor shall be one URL or a whitespace-separated
  list of URLs of the \"chained-to\" MPD. If multiple URLs are provided, the
  content author expresses the preferences of using one of those by the order
  with the first one having the highest preference"* — but at the granularity of
  whole presentations, on an MPD-level descriptor of which *"Each MPD may contain
  at most one"*, and triggered by an error condition that *"makes it impossible
  to continue playback of the current Media Presentation"* rather than by a
  capability check.

R8 requires the spec to record that all three were weighed and why none was
reused. The third is the one to cite affirmatively: document-order-as-preference
is the edition's own convention, so R5.1's prohibition on a ranking attribute is
consistency with the base specification and not a departure from it. The
departure to record is from `@selectionPriority`, whose direction is reversed.

What the spec must add: an option-list child on the candidate, each option
pairing a form (video / image / HTML, R15) with a layout (R12), ordered by XML
document order. The same construct must read correctly when a candidate carries
exactly one option (UC-13): the Player-visible interface is identical, and
nothing in the document distinguishes "the APS filtered" from "this is all there
was". R7's drop / trim vocabulary rides on the same construct and is likewise
spec-side.

### G4 — Non-AV creatives have no home on the media axis, and the descriptor axis is wider than DR-6 records (R15, R24)

Two independent facts close the media axis, and a third narrows where a carrier
may sit.

**The profile chain.** §5.3.2.6.1: *"Linked Periods are Periods which import
their content from an external MPD, referred to as imported MPD … MPDs
referenced in the ImportedMPD element shall be restricted to the constraints of
a single period profile as defined in 8.15."* §8.15.2 requires that *"The rules
for the MPD as defined in subclause 7.3 shall apply"*, and §7.3.1 states *"The
@mimeType attribute of each Representation shall be provided according to IETF
RFC 4337."* §8.14 rule 4 puts regular Periods inside a List MPD under the List
profile, itself *"an extension of the ISO-BMFF CMAF Profile"*, so the same
constraint reaches inline Adaptation Sets there.

**The absence.** The edition never mentions a non-AV media type. Searches over
the full document return `image/` 0 occurrences, `text/html` 0 and `thumbnail`
0, against `video/mp4` 79, `audio/mp4` 36, `application/mp4` 4 and
`application/ttml` 2 from the same search. There is nothing to relax on the
media axis; carriage of a still image or an HTML document as a Representation is
simply not defined in the document this specification extends.

**The Period constraint.** §5.3.2.2 Table 4: *"At least one Adaptation Set shall
be present in each Period unless the value of the @duration attribute of the
Period is set to zero."* An events-only Period of non-zero duration is not a
legal carrier, which is DR-7 and which holds.

**What DR-6 gets wrong, and it changes the answer.** DR-6 records of the two
descriptor carriers that *"they sit on AdaptationSet / Representation /
Sub-Representation, so both inherit DR-5's MIME constraint unless hosted inside
a foreign-namespace parent."* The schema says otherwise. `SupplementalProperty`
and `EssentialProperty` are declared as children of `MPDtype`, `PeriodType`,
`RepresentationBaseType`, `EventStreamType` and `EventType`, and
`AlternativeMPDEventType` carries `SupplementalProperty` directly
(§5.10.2.3, §5.16.6). `<xs:any namespace="##other" processContents="lax"/>`
appears on all of those and on `DescriptorType` itself. A descriptor or a
foreign-namespace element hosted on `<Event>`, `<EventStream>` or on the
alternative-MPD event element therefore never touches the `Representation@mimeType`
axis, and inherits no MIME constraint to escape.

The one placement that is genuinely closed is the one DR-6 does not mention:
`ImportedMpdType` is declared as `xs:simpleContent` extending `xs:anyURI` with
`<xs:anyAttribute namespace="##other" processContents="lax"/>` and no `xs:any`
(§5.3.2.6.2). A foreign-namespace **attribute** may hang off `<ImportedMPD>`; a
foreign-namespace **child element** may not.

What the spec must add: an explicit carrier choice per construct, recorded in
the per-construct classification that Item 8 of
[`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md)
demands, and chosen against the corrected placement facts above. Wrapping a
non-MP4 payload in an `application/mp4` Representation to satisfy the registry
remains an anti-pattern: it adds no segment-delivery semantics for the
underlying format, which §8.1 makes an Interoperability Point exercise.

### G5 — No metadata carrier, and no event fired by a user activation (R23, R28)

`AdSystem`, `AdTitle`, `UniversalAdId` and `ClickThrough` each return 0
occurrences in the edition. For R23 that is a low-stakes gap: the carrier is
optional on both ends by design, and a legacy client removing a
foreign-namespace element under §5.2.1 breaks nothing in the ad presentation.

R28 is the harder half, and the difficulty is the event model rather than the
missing field. Events are timed (§5.10.1), and the callback scheme fires at a
scheduled presentation time and discards what comes back: *"the client is
expected to entirely ignore the response"*, with a response body that *"should
be as small as possible or absent"* (§5.10.4.5.1). A ClickThrough activation has
no presentation time, because it happens when the viewer acts or never. The
callback scheme is therefore the right carrier for impression and quartiles (R6)
and the wrong one for click-tracking.

The edition is not silent about user action, and the spec should use what is
there instead of claiming an absolute absence. `@skipAfter` on the
alternative-MPD event *"describes an offset in time (in fractional seconds) from
the beginning of the alternative presentation till the moment the rest of that
presentation may be skipped by the application in response to a user action"*
(§5.16.5.2) — a user action with a normative consequence. And Annex L fires an
HTTP request off the timeline on a selection (§L.3.3, quoted in G2). What the
edition lacks is an *event scheme* dispatched by a user activation; what it has
is the pattern R28's carrier should follow.

What the spec must add: the ClickThrough URL and any click-tracking URL(s)
accompanying it as a document-level construct the Player reads at render time
and fires on activation — normative and interoperable, unlike R23's best-effort
carrier, because UC-11 requires every Player conformant to this specification to
behave identically. The scoping to conformant Players is not a weakening but the
only obligation available: §8.1 NOTE 1 states that *"as DASH Client operation is
not specified normatively in this document, it is also unspecified how a DASH
Client conforms to a particular profile. Hence, profiles merely specify
restrictions on MPD and Segments rather than DASH Client behaviour"*, and §5.2.1
NOTE 2 contemplates a client that removes every extension element and still
*"can use such a resulting MPD for presentation of a conforming Media
Presentation."* Whether a given ClickThrough carries click-tracking at all is
the advertiser's decision (R28.1); what the carrier guarantees is that when it
does, both travel together and in one place.

### G6 — No channel for the Player to declare device capability, and one extension hook that was missed (R29, R3)

UC-13 needs the Player to tell the APS what its device can render. The edition
carries an upstream channel for exactly this class of request, and it carries
the wrong payload and is authored by the wrong party.

**The construct, named correctly.** It is `RequestParam`, of type
`ExtendedUrlInfoType`, signalled by an `EssentialProperty` or
`SupplementalProperty` descriptor with `@schemeIdUri` equal to
`"urn:mpeg:dash:urlparam:2025"` (§I.3.1), and it *"may be present in elements
such as but not limited to MPD, Period, AdaptationSet, Representation,
Preselection, or EventStream."* `@includeInRequests="altmpd"` scopes parameters
to *"all requests for MPDs representing the alternative Media Presentation, as
defined in subclause 5.16"* (Table I.4). **The edition declares no element named
`UrlParamInfo`** — a search returns 0 occurrences — so the reference in
`../context/05-dash-linear-interfaces.md` step 4a names something that does not
exist in this edition, and the spec and its examples must carry the edition's
name.

**The payload.** §I.4.1 states the vocabulary's purpose: *"In some cases, such
as dynamic advertisement insertion and content steering, there is a need to
express knowledge of the current state of the player."* Table I.5 is that
vocabulary in full — `audio` and `video` (the `@codecs` and `@bandwidth` of what
is playing), `lang#[audio|text]`, `encryption`, `cmcd#[key]`,
`execution-delta#[id]`, `expected-duration#[id]`, `execution-count#[id]` and
`previous-state` (`normal` / `ff` / `rw` / `listen`). What is playing and what
has run; nothing about what the device can render. The template identifiers of
Table I.2 are `$$`, `$querypart$`, `$query:<param>$` and
`$header:<header-name>$`, so a parameter's value can be lifted from the MPD URL
or from a response header, never minted by the Player from its own capability.

**The authoring party.** `@queryTemplate` *"provides URL parameters template
information. This string shall contain one or more $<ParamIdentifier>$ template
identifiers, as listed in Table I.2"* (§I.2.2.2), and it is written by the
content author in the MPD. A Player cannot add an axis to a template it did not
write. That is why R29 places the reserved parameters outside this mechanism.

**The hook the context does not record.** The value space of
`@includeInRequests` (Table I.4) is not closed. Its last row is
`<URN / tag URI>`: *"a URN or tag URI, where the request type semantics is
understood by the client and specified by the URN / tag URI owner. The client
shall drop unknown URIs from the @includeInRequests and @includeInHeaders
strings prior to processing them as specified in this Annex."* An SGAI-defined
request type — the non-linear resolution request, which `altmpd` does not cover
because it is not an Alternative MPD request — can therefore be named by a URN
the SVTA Ads WG owns, and the drop rule gives it legacy-safe behaviour for free.
This does not solve R29 (the payload vocabulary and the authoring party are
still wrong), but it is the base-specification hook for scoping the reserved
parameters to the right request, and R8 requires it to be weighed rather than
left unnamed.

The edition's only device-side vocabulary is reporting-side and is about display
geometry: §D.4.7 *Device information* logs *"information about the displayed
video resolution as well as the physical screen characteristics"* and, *"If
known by the DASH Client, the physical screen width and the horizontal
field-of-view."* Neither decoder count nor overlay-surface capability appears
anywhere — `concurrent decoder` and `decoder count` both return 0.

What the spec must add: a set of reserved query-parameter names on the
resolution request, each optional, each omitted rather than emptied (R29.2 /
R29.3), with absence meaning **undetermined** rather than unsupported (R29.7), a
vendor-prefix rule for non-reserved names (R29.4), and an APS obligation to
answer without any of them (R29.5). The set must separate D1 through D5 (R29.6),
which fixes its axes: concurrent video-decoder count, and which surface types
can be composited with video. The spec must also state how the reserved
parameters coexist on one request with an author-declared `RequestParam`
template, since both land on the same URL.

### G7 — The fallback chain is inherited whole for linear and has no anchor at all for the other two families (R20)

This is the gap where the base specification gives the most and the reading has
to stay narrow. §5.16.2.2.5 step 2 delivers first-window-wins with fallback in
full: events processed *"in its priority order (from oldest PRT to the most
recent)"*; *"If execution fails, steps a-c above are repeated for next events in
QE, until: — Execution succeeds, or — PRT of the topmost event in the queue is
in the future (i.e. PRT > PHP), or — The queue is empty"*; and *"If no event can
be successfully executed, the playback continues uninterrupted."* §5.16.2.2.6
enumerates what counts as a failure, and all four of R20.1's conditions are
there — *"Alternative MPD is unavailable or invalid"* and *"Alternative MPD is a
List MPD, and merge process resulted in no available media"* among them. R20.1
adopts this rather than diverging from it, and the earlier reading in which the
zero-ad case was a conflict does not survive the clause: the edition calls that
case a failed execution, and the fall-through is the consequence.

Three things the base specification does not supply:

- **The other two families.** The queue holds Alternative MPD events. Overlay
  and pause-trigger windows are not those, so they inherit nothing — R20.1 and
  R20.3 extend the rule to them, which R20.1 already says explicitly and which
  R8 requires be recorded as an extension rather than a citation.
- **The tie-break.** The queue is *"ordered by the presentation time PRT"*
  (§5.16.2.2.2) and the edition does not say what happens when two windows carry
  the same one. R20.3's fallback to document position is this specification's.
  The distinction R20.3 draws is real and is worth keeping: document order
  governs dispatch to the application — *"all active events are dispatched
  (according to their dispatch mode) in the order they appear in the EventStream
  element"* (§5.10.2.1) — which is an earlier and separate step from execution
  order.
- **R20.4 and R20.5.** A resolution document of the wrong family, and the
  binding of each window's own declarations to the candidates it serves, have no
  base anchor. R20.6 already says R20.5 must be normative rather than
  illustrative.

R20.2's single-stream rule is the base specification's and is quoted in the
matrix. Two neighbouring mechanisms are worth naming as rejections: `BaseURL`
alternatives retry the *same* resource from another location, and
`urn:mpeg:dash:fallback:2016` chains whole presentations on an unrecoverable
playout error. Neither chains two *opportunity windows*, and R20 should say so
rather than let a reader assume one of them covers it.

### G8 — The empty resolution has its semantics from the base specification and needs its shape from the spec (R30)

R30's semantics are inherited and the matrix quotes them: the zero-ad case is a
failed execution (§5.16.2.2.6), a failed execution continues the main
presentation smoothly, and NOTE 3 leaves the opportunity executable. Nothing
needs adding there.

What needs adding is the document. `Period` cardinality inside `MPDtype` is
1..N — the schema declares `<xs:element name="Period" type="PeriodType"
maxOccurs="unbounded"/>`, and an omitted `minOccurs` defaults to 1 — so a
resolution document carrying zero Periods does not validate against the Annex B
schema. The obvious workaround is closed from the other side: §5.3.2.2 Table 4
requires *"At least one Adaptation Set shall be present in each Period unless
the value of the @duration attribute of the Period is set to zero"*, so a
placeholder Period must either carry media or declare zero duration.

R30 also requires the answer to be the same for a linear slot and for a
non-linear one, and the linear side has a further constraint the non-linear side
does not: a List MPD *"shall have the value of the MPD@type attribute set to
\"list\""* (§8.14 rule 1) and must declare the profile URN (rule 2).

What the spec must add: the normative shape of a resolution document carrying
zero candidates, chosen against that cardinality constraint, stated once for
both families. That shape is also what makes R20's chain well-defined, since
"resolved, and carries nothing" is the case R20.1 and R30 share.

### G9 — The rate model is unbound, and the live-pause freeze has a normative limit R25 does not state (R19, R25)

The pieces R19 needs exist. `@maxPlayoutRate` *"specifies the maximum playout
rate as a multiple of the regular playout rate, which is supported with the same
decoder profile and level requirements as the normal playout rate. If not
present on any level, the value is 1"* (§5.3.7.2); Annex K.3 lets the service
bound the rates it wants used; §D.4.6 defines `playbackspeed` relative to
*"normal forward playback speed … 1.0"*. The edition even ties two presentations
to one speed, informatively, in §A.14.2: *"on reception, the main client will
adjust its playhead propagation speed. As a result, media time elapses at the
same speed in both clients."* What is missing is the binding: nothing ties an ad
form's on-screen length, or the cap it is measured against, to that rate, and
nothing gives a presentation-timeline duration to a form with no intrinsic
media, which is what R19.4 requires for `image` and `html`.

R25 is the same concern at the other end, and here the edition does not merely
omit — it **bounds**. The freeze itself is the edition's model, since a pause
stops media time while wall-clock time advances. But the drift is bounded by the
time-shift buffer and the edition states the consequence normatively twice:
§5.16.2.2.5 step 1a, *"In case of live main media presentation, this involves
clipping RT to the timeshift buffer (i.e. the time interval between TSBS and
PHPLE)"*; and Table 62, *"if RT is in the past, the playback shall start from
the oldest available media segment (the edge of the timeshift buffer). Similarly,
if RT is in the future, the playback shall start from the most recent available
segment (i.e. the live edge)"*, with NOTE 2 naming the cause as *"a user pauses
the alternative Media Presentation."* R25.1 promises the freeze *"for the full
duration of the pause"*, which the edition does not allow past
`MPD@timeShiftBufferDepth`.

What the spec must add: for R19, a statement of which rules operate on which
timebase — cap enforcement (R4) and beacon scheduling (R13) on the presentation
timeline, on-screen behaviour on the derived value — with `duration` kept as the
single canonical value per DP-1.2. For R25, what happens when the pause outlives
the time-shift buffer, because the pause-ad's dismissal and the edition's
mandatory trim then coincide. Leaving R25 unbounded puts the spec in conflict
with the baseline rather than on top of it.

### G10 — A declared profile strips the extension namespace during conformance checking, and `MPD@type="list"` is not the profile (R1.2, and the DR-4 / DR-10 reasoning)

Two facts about profiles bear on how the spec's constructs are declared, and the
second corrects a `context/` rule.

**Profile conformance checking removes extension-namespace content.** §8.1
defines profile conformance by modifying the MPD first, and step 4 of that
procedure removes *"All elements or attributes that are either (i) in this
document and explicitly excluded by ProfA, or (ii) in an extension namespace and
not explicitly included by ProfA."* A document that declares a profile URN and
carries SGAI constructs is therefore checked, for that profile, with the SGAI
constructs gone. This does not make the document non-conforming — §5.2.1
guarantees that what remains is valid, which is the same property R1 relies on —
but it does mean a declared profile cannot be the thing that certifies the SGAI
constructs. Only an Interoperability Point that *"explicitly included"* them
could, and §8.1 states what that costs: *"Such an interoperability points may be
signalled in the @profiles parameter once a URI is defined. The owner of the URI
is responsible to provide sufficient semantics on the restrictions and permission
of this interoperability point."* This is the same cost DR-4 weighs for Annex F,
reaching a construct DR-4 does not cover.

**`MPD@type="list"` is a presentation type defined in the main body, not a
profile.** DR-10 argues that *"that value is not a free choice of presentation
type; it is rule 1 of the ISO Base media file format List profile, and the rules
travel together"*, and the primary copy does not support the inference. §5.3.1.4
*Media Presentations of type "list"* defines the value independently of Annex 8:
*"For Media Presentations with MPD@type set to \"list\" the constraints of a
static Media Presentation shall apply"*, *"MPDs of this type shall not use MPD
assembly as defined in 5.5, i.e. the attributes from namespace @xlink shall not
be present"*, and *"MPDs of @type=\"list\" may contain Linked Periods."* §8.14
rule 1 runs the other way — a document conforming to the List profile **must**
declare `type="list"` — and the edition nowhere states the converse. The two
properties DR-10 says the suggestion was *"reaching for"* — static, no XLink —
are precisely what §5.3.1.4 confers, without the profile URN and without
enrolling anything in a profile built for the linear path.

DR-10's **conclusion** may well stand: whether the non-linear resolution
document should declare `type="list"` is a design decision, and reasons to
decline it exist — the type is bound to Linked Periods and to the alternative-MPD
flow by every other mention of it. But the stated **reason** does not hold
against the clause, and a rule that closes a design option on a false premise is
the kind that gets reopened later at a worse moment. This is recorded as a
finding against `context/08-dash-extension-rules.md` rather than acted on here.

## 4. Reuse opportunities

The spec MUST reuse the constructs below before introducing new ones (R9), and
document each reuse or departure inline (R8).

| Existing construct | Reused for | Notes |
|---|---|---|
| `EventStream` + `<Event>` (§5.10) | Every new SGAI opportunity declaration — non-linear slot, pause window | The authoring vehicle for timeline-anchored signalling, and already open to us: `EventType` is `mixed="true"` with `<xs:any namespace="##other">` and `<xs:anyAttribute namespace="##other">`, and §5.10.2.1 states the Event *"may contain further XML elements … in some external namespace."* A Player that does not implement the `schemeIdUri` ignores the stream (§5.10.1), which is half of R1. |
| Callback event scheme `urn:mpeg:dash:event:callback:2015` (§4.7 / §5.10.4.5) | All timeline-scheduled tracking beacons (R6, R13) | Reused verbatim; R13.4 forbids a parallel scheme. The URL rides in the `Event` element's content, not in `@messageData`, which the 6th-edition schema declares `use="prohibited"` and *"Deprecated in favor of carrying the message information in the value space of the event"*. Dispatch is on-start (Table A.3). Does **not** cover click-tracking, which has no presentation time (G5). |
| List MPD profile `urn:mpeg:dash:profile:list:2024` (§8.14) | The resolution document baseline | Gives declared-order playback, which is R7's baseline. Three rules bound the reuse: *"List MPDs shall not contain XLink attributes defined in subclause 5.5"*, *"List MPDs shall not contain Alternative MPD events"*, and the profile is *"an extension of the ISO-BMFF CMAF Profile."* |
| `MPD@type="list"` (§5.3.1.4) | Declaring the resolution document static and XLink-free | Defined in the main body independently of §8.14, and it confers exactly those two properties: *"the constraints of a static Media Presentation shall apply"* and *"the attributes from namespace @xlink shall not be present."* Whether the non-linear document takes it is open; the reason to decline it is not the one DR-10 gives (G10). |
| `<ImportedMPD>` (§5.3.2.6) | Per-ad sub-MPDs for video creatives | *"Linked Periods are Periods which import their content from an external MPD"*, restricted to §8.15. The URL is the element's text content (`ImportedMpdType` extends `xs:anyURI` via `xs:simpleContent`) and its one attribute is `@earliestResolutionTimeOffset` (`xs:double`, default `60.0`, *"the offset (in seconds) from the PeriodStart"*). It accepts foreign-namespace **attributes** and no foreign-namespace **child elements** — the simpleContent has `anyAttribute` and no `xs:any`. Fine for video; the §8.15 binding is why it is unusable for image / HTML (G4). |
| `@maxDuration`, `@clip` and the trim rule (§5.16.5.2, Table 62) | R4's enforcement baseline, including its two-sided meaning | *"If the Alternative Presentation initiated by this event has a longer duration than specified in this element, it shall be terminated at the end of this duration"*; `@clip` default `true` makes a late replacement *"terminate at the latest at time PRT + APDmax"*. The non-linear cap reuses the name, the units (`EventStream@timescale`) and the zero and absent semantics rather than inventing a second duration vocabulary, per the naming-consistency rule in `../context/06-naming-and-namespaces.md`. |
| `@executeOnce` and the `E.c` counter (§5.16.5.2, §5.16.2.2.2, §5.16.2.2.6 NOTE 3) | R34's once-per-session bound, and R30.2's non-consumption | The capability and the counter semantics are both already right; only the trigger changes from playhead to first render (G2). Reuse the name. |
| `@noJump` (§5.16.5.2) | Preserved on inherited linear breaks; excluded on the non-linear families per OOS-7 | *"If non-zero, the playhead may not move forward from any point for which PHP < PRT to any point where PHP > EAP without executing this event."* OOS-7's exclusion is an exception with a stated reason, which is what R8 asks of an omission. |
| `@skipAfter` (§5.16.5.2) | Publisher-declared skippability, and the precedent for a user action with a normative consequence | *"describes an offset in time … till the moment the rest of that presentation may be skipped by the application in response to a user action."* The spec need not mint a skip control, and G5 should cite this rather than claim the edition ignores user action. |
| `@earliestResolutionTimeOffset` (§5.16.5.2 and Table 5) | The resolution-timing contract on a non-linear slot | Present on the event (in `EventStream@timescale` units, *"The default is 60 seconds in units of timescale"*) and on `ImportedMPD` (seconds, default `60.0`). A non-linear opportunity needs the same "resolve no earlier than" bound and the name exists. Note the two are in different units, which is a trap the spec should call out. |
| `@serviceDescriptionId` (§5.16.5.2) | Binding a slot to a service description | *"specifies the value of the @id attribute of a ServiceDescription element applicable to this Event and to any presentation initiated as a result of executing this Event."* Available on the non-linear slot for the same purpose without a new construct. |
| Alternative-MPD execution model (§5.16.2.2) | R20's chain, R30's failure semantics, and R22's rationale | The priority queue, the four failure conditions, the fall-through, the non-incremented counter and listen mode. Inherited whole for linear and extended to the other families (G7). |
| Listen mode (§4.2) | R22's and R17.5's precedent | *"For the duration of the alternative media presentation, the alternative access engine outputs media to the media engine, while the main client will be paused or be in a listen mode."* The edition's own one-presentation-at-a-time rule, and the model for suspending a linear ad under a pause ad. |
| `adjust speed(S)` dual-client model (§A.14.2, informative) | R19's precedent | Two presentations, one propagation speed, with `S = 0` for pause. R19's "ad follows primary" is this rule stated normatively for ad forms. |
| `PlayList` metric (§D.4.6) and the `Metrics` element (§5.9.1) | R33, adopted unchanged | The `starttype`/`stopreason` value spaces carry everything R33 derives. One placement constraint: §8.15.2 forbids `MPD.Metrics` in a Single-Period Static MPD, so R33.4's declaration lives on the primary MPD only. |
| MPD fallback scheme `urn:mpeg:dash:fallback:2016` (§5.11.3) | **Precedent for R5; rejection for R20** | Document-order-as-preference is the edition's own convention and R5 should cite it affirmatively. Wrong granularity for R20 (whole presentations, error-triggered) — say so rather than let R20 absorb it. |
| `Preselection` (§5.3.11) and `@selectionPriority` (§5.3.7.2) | **Considered and rejected for R5** | `Preselection` combines components into one experience; `@selectionPriority` is a numeric hint running the opposite way from document order. R8 requires both rejections inline (G3). |
| Supplementary video descriptor `urn:mpeg:dash:supv:2022` (§5.8.5.16) | **Considered and rejected for R26 / R27; cited for OOS-6** | The edition's two-video composition signal, which hands the composition itself to the application. Carries no ad, no layout and no non-video surface. Its VVC single-decoder path (§5.8.5.16.4) is the technique OOS-6 excludes, and OOS-6 should cite it (G1). |
| Annex H SRD `urn:mpeg:dash:srd:2014` | **Considered and rejected** | Coordinates between spatial objects for tile / ROI selection, confined to `AdaptationSet` and `SubRepresentation`. Reusing it would misuse the construct and violate R10. |
| Annex L `urn:mpeg:dash:nonlinearplayback:2020` | **Precedent, not carrier** | Not reusable for non-linear ads, but it is the edition's own instance of the split G2 and G5 both need: a timeline-anchored `<Event>` declaring a window, with the decision resolved off the timeline through a callback to `@contactURL`. Normative, which strengthens the citation. |
| Foreign-namespace open content (§5.2.1) | Every new SGAI element and attribute | The single normative extension point, backed by `<xs:any namespace="##other" processContents="lax"/>` on `MPDtype`, `PeriodType`, `RepresentationBaseType`, `EventStreamType`, `EventType`, `AlternativeMPDEventType` and `DescriptorType`. DR-3's authoring rule governs placement. |
| Vendor descriptors (§5.8.4.8 / §5.8.4.9) | Carrier for metadata and for non-AV asset URLs (R23, R24) | The legacy split is the one DR-9 states and the quotations hold. Their placement is wider than DR-6 records: they are declared on `MPD`, `Period`, `RepresentationBaseType`, `EventStream` and `Event`, plus `SupplementalProperty` on the alternative-MPD event, so one hosted on an event inherits no MIME constraint (G4). |
| Annex I `RequestParam` (`urn:mpeg:dash:urlparam:2025`) and the `<URN / tag URI>` row of `@includeInRequests` | **Rejected for the payload; weighed for the scoping** | The vocabulary (Table I.5) carries no capability axis and the template is author-declared, so R29's reserved set is new by necessity. But `@includeInRequests` accepts *"a URN or tag URI, where the request type semantics is understood by the client and specified by the URN / tag URI owner"*, with unknown URIs dropped — the hook for naming the non-linear resolution request, which `altmpd` does not cover (G6). |

## 5. Open questions

1. **Shape of the non-linear resolution document.** Extend the List MPD
   structure (Periods plus `ImportedMPD`) or define a separate document type
   under the SVTA namespace? Reuse maximises R9 but inherits §8.14's rules — no
   Alternative MPD events inside, no XLink — and forces every non-AV creative
   through a non-media carrier. G10 removes one argument previously used to
   close this: `MPD@type="list"` is available from §5.3.1.4 without the profile
   URN, so "static and XLink-free" and "enrolled in the List profile" are
   separable decisions. Needs a WG decision on which.
2. **Encoding of the zero-candidate resolution document (R30).** The semantics
   are settled and inherited; the shape is not. `Period` cardinality is 1..N and
   a Period of non-zero duration needs an Adaptation Set, so the options are a
   zero-duration placeholder Period or a resolution document shape of its own.
   Needs a WG decision.
3. **The reserved capability-parameter set (R29).** Which axes it contains and
   how each is written is left open by R29.1. R29.6 sets the acceptance test:
   the set must tell D1–D5 apart. Needs a decision on the concrete names and
   value spaces, on how the reserved parameters coexist with an author-declared
   `RequestParam` template on one URL, and on whether the non-linear resolution
   request is named by an SVTA-owned URN in `@includeInRequests` (G6).
4. **Single-option versus multi-option candidates (R5, UC-09 vs UC-13).** Both
   are conformant and the Player-visible interface is identical, so the document
   does not show whether the APS filtered. Is that indistinguishability
   acceptable, or should the document record that a filter was applied — for
   diagnostics, or so a Player that cannot satisfy the single option knows it
   was not the only one?
5. **Bound on the R25 freeze.** The edition trims the playhead to the time-shift
   buffer start once the resumption time falls before it, so the freeze cannot
   hold past `MPD@timeShiftBufferDepth`. R25 promises it for the full duration
   of the pause. Decide whether R25 is amended to state the bound or the spec
   declares the pause ad dismissed when the buffer expires — and what happens to
   the pause ad's pending beacons when the resume is a trim to the buffer start
   or a jump to the live edge rather than a resume in place.
6. **Declaring the constructs at all (G10).** §8.1 step 4 strips
   extension-namespace content during profile conformance checking unless the
   profile explicitly includes it. Does the project want an Interoperability
   Point URI that includes the SGAI namespace — with the authoring rules,
   conformance criteria and publication that §8.1 puts on its owner — or is
   "valid base document plus constructs a conformant Player reads" the declared
   position? R28's scoping under DR-8 suggests the second; it has not been
   stated as a decision.
7. **R4.10's treatment of a missing cap.** R4.10 itself records the position as
   provisional and diverging from §5.16.5.2's *"If absent, the value is assumed
   to be infinity"*. The divergence is a profile-style narrowing, which §8.1
   admits, but it changes what a Player does with a document the base
   specification considers valid. Needs the WG call R4.10 says it needs.
8. **Layouts outside the closed R12 set.** ADR 0002 (custom layout with a
   viewport-relative coordinate model) and ADR 0003 (multiview) are both
   `proposed` and scoped to later phases. They sit outside R12's closed
   enumeration, and R10 / OOS-1 forbid a parallel layout engine. Confirm they
   stay out of this edition.
9. **OOS-6 and the single-decoder path that already exists.** §5.8.5.16.4
   standardises single-decoder picture-in-picture for VVC by replacing portions
   of the main stream before decoding. OOS-6 excludes the technique for this
   edition on decoder-budget grounds. The exclusion is a scope call and can
   stand, but it should cite the clause; a reader who finds it in the base
   specification will otherwise conclude the exclusion was made without knowing
   it was there.
10. **Tracking-only decision entries.**
    `../context/05-dash-linear-interfaces.md` flags that the industry convention
    for a tracking-only VAST `<Ad>` with no media — silent skip versus signalled
    error — has no answer in the base specification. This was re-checked: the
    edition has no VAST-side vocabulary at all (`VAST` appears 5 times, all
    non-normative), so there is nothing there to resolve it. Under R18.2 this is
    APS-internal and the spec may decline to bind it; R30 covers the
    Player-visible half.

## 6. Findings against `context/`

Three statements in `context/` do not survive the primary copy. They are
recorded here and not acted on, because `context/` is human-authored and this
document is generated.

1. **`context/08-dash-extension-rules.md`, DR-6** — *"Both share the placement
   constraint: they sit on AdaptationSet / Representation / Sub-Representation,
   so both inherit DR-5's MIME constraint unless hosted inside a
   foreign-namespace parent."* The schema declares `SupplementalProperty` and
   `EssentialProperty` on `MPDtype`, `PeriodType`, `RepresentationBaseType`,
   `EventStreamType` and `EventType`, and `SupplementalProperty` on
   `AlternativeMPDEventType` (§5.10.2.3, §5.16.6). A descriptor on an `<Event>`
   or `<EventStream>` inherits no MIME constraint. This widens the admissible
   carrier set for R24 (G4). The constraint DR-6 omits is that
   `ImportedMpdType` accepts foreign-namespace attributes only, never child
   elements (§5.3.2.6.2).
2. **`context/08-dash-extension-rules.md`, DR-10** — the claim that
   `MPD@type="list"` *"is not a free choice of presentation type; it is rule 1
   of the ISO Base media file format List profile"*. §5.3.1.4 defines the value
   in the main body, with its own constraints, independently of §8.14; §8.14
   rule 1 states only the forward implication. DR-10's conclusion may hold on
   other grounds, but not on this one (G10).
3. **`context/05-dash-linear-interfaces.md`, message-flow step 4a** — *"the
   query parameters declared by the `UrlParamInfo` descriptor on the MPD
   (§I.4)"*. The edition declares no element named `UrlParamInfo` (0
   occurrences). The element is `RequestParam` of type `ExtendedUrlInfoType`,
   signalled under `urn:mpeg:dash:urlparam:2025` and specified in §I.3, with
   §I.4 supplying only the substitutable state vocabulary (G6).

## References

- [`../context/01-intro.md`](../context/01-intro.md) — document index
- [`../context/02-actors.md`](../context/02-actors.md) — Publisher / ADS / APS / Player
- [`../context/03-requirements.md`](../context/03-requirements.md) — R1–R34, DP-1..DP-3, OOS-1..OOS-7
- [`../context/04-use-cases.md`](../context/04-use-cases.md) — UC-01–UC-14, device classes D1–D5
- [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md) — linear SGAI baseline
- [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md) — SVTA Ads WG namespace and versioning
- [`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md) — per-construct R1 audit
- [`../context/08-dash-extension-rules.md`](../context/08-dash-extension-rules.md) — DR-1..DR-10, the closed design space
- [`../context/99-glossary.md`](../context/99-glossary.md) — terminology
- The base specification, in the edition declared in
  [`../context/00-normative-base.md`](../context/00-normative-base.md). Clauses
  cited above: §4.2, §4.7, §5.2.1, §5.3.1.4, §5.3.2.2 (Table 4), §5.3.2.6,
  §5.3.7.2, §5.3.11, §5.8.4.8, §5.8.4.9, §5.8.5.16, §5.9.1, §5.10 (§5.10.1,
  §5.10.2.1, §5.10.2.3, §5.10.4.5), §5.11.3, §5.16 (§5.16.1, §5.16.2.2.2,
  §5.16.2.2.5, §5.16.2.2.6, §5.16.3, §5.16.4, §5.16.5.2, §5.16.6), §7.3.1,
  §8.1, §8.12, §8.14, §8.15, Annex A (§A.5, §A.13.12, §A.14.2), Annex D
  (§D.4.6, §D.4.7), Annex F, Annex H (§H.1), Annex I (§I.2.2.2, §I.3.1, §I.4,
  Tables I.2, I.4, I.5), Annex K (§K.3), Annex L (§L.1, §L.2, §L.3.3,
  §L.3.4.2).

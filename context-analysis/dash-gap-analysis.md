[GROUNDED_BY=iso-23009-1-2026-pdf]

# DASH 6th edition gap analysis (SGAI for linear + non-linear ads)

This document compares the requirements in
[`../context/03-requirements.md`](../context/03-requirements.md) (R1–R39)
and the use cases in
[`../context/04-use-cases.md`](../context/04-use-cases.md) (UC-01–UC-16)
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

- Every requirement R1–R39 in `../context/03-requirements.md` against the
  capabilities the base specification provides.
- The use cases UC-01–UC-16 in `../context/04-use-cases.md` as the behavioural
  check on those capabilities across device classes D1–D5.
- The constructs, carriers and conformance rules the spec must add, and the
  existing machinery it must reuse first (R8 / R9).

Out of scope:

- The APS-to-ADS and ADS-side API contracts (R18) — opaque to the spec.
- VAST itself (R11) — the spec is VAST-version-agnostic; R11.4's coverage
  obligation is checked against the constructs this document identifies, not
  against the VAST schema.
- ABR, DRM, transport, low-latency tuning — orthogonal to SGAI.
- The IAB ad-type vocabulary itself (R12) — owned by the IAB and analysed
  separately in [`iab-ad-templates.md`](iab-ad-templates.md).
- The linear SGAI baseline mechanics themselves — inventoried in
  [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
  and absorbed here as the starting point, not re-derived.
- The items `../context/03-requirements.md` closes as OOS-1..OOS-9. OOS-6 and
  OOS-7 are referenced where the base specification bears on them. OOS-9 (ads
  outside the video surface, and in-scene placement) has nothing to meet in the
  base specification: `companion` 0 occurrences, `screensaver` 0,
  `screen saver` 0, `product placement` 0.

**How conflicts with the base are read.** R1.5 makes the base specification's
answer the default wherever it has one: this specification adopts it and cites
it, defines its own only where the base gives none, and records any departure
as an exception with its reason. Every "default conflict" below is therefore
either resolved by adoption, recorded as an exception in an ADR, or still open —
and the document says which.
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
| R1 | Extends the base edition; legacy Player ignores and keeps playing | **full** — §5.2.1 carries the authoring obligation: *"the MPD shall be authored such that, after XML attributes or elements in the other namespaces than the DASH namespace are removed, the result is a valid XML document formatted according to that schema and that conforms to this document."* The schema backs it: `EventType` is declared `mixed="true"` with `<xs:any namespace="##other" processContents="lax"/>` and `<xs:anyAttribute namespace="##other"/>` (§5.10.2.3), and §5.10.2.1 states that *"The Event element may contain further XML elements meaningful for a particular event scheme."* Per-scheme skip is the other half: *"This enables a DASH Client or the application to subscribe to an Event Stream of interest and ignore Event Streams that are of no relevance or interest"* (§5.10.1). The ignore-if-unknown contract is inherited, not invented. One caveat under R1.2 is in G10. R1.5 is a spec-authoring rule and needs nothing from the base; it governs how every conflict below is settled. |
| R2 | Four actors, fixed roles | **partial** — §5.16 wires two legs only: the MPD author and the client. The APS is whatever answers `AlternativeMPDEventType@uri`, and the ADS is invisible. No construct binds an actor to a responsibility, so R2 is carried entirely by spec prose and conformance criteria. The base specification offers one precedent for the Player-as-enforcer model: it states its own execution model as conditions *"the MPD author may assume"*, while *"the client implementer may provide any functionally equivalent implementation"* (§5.16.2.2.1). |
| R11 | Independent of VAST; covers what VAST expresses | **N/A** — the base specification is VAST-agnostic. `VAST` occurs 5 times, none normative; the one in body text is §5.10.4.5.1 NOTE 1, *"HTTP GET (as opposed to HEAD) is used in alignment with IAB VAST."* R11.4's coverage obligation is a statement about this specification's constructs, and the gaps below are what it is measured against: tracking (R6 / R13), ClickThrough (R28), metadata (R23), skippability (R35 — a field of this specification, weighed against two base constructs, G11). |
| R18 | Player-visible interface only | **N/A** — governance; the base specification does not constrain server-side APIs. |
| R29 | Player-declared capability parameters on the resolution request | **gap** for the payload, with two extension hooks in Annex I that must be weighed. The edition's upstream channel is Annex I.3, whose element is `RequestParam` of type `ExtendedUrlInfoType`; `@includeInRequests="altmpd"` scopes parameters to *"all requests for MPDs representing the alternative Media Presentation, as defined in subclause 5.16"* (Table I.4). The standard state vocabulary (Table I.5) contains no decoder count, no image-rendering axis and no HTML-overlay axis; I.4.1 states what it is for: *"there is a need to express knowledge of the current state of the player."* State, not capability. But the template is **not** closed to third-party variables: *"Scheme-defined signalling (@queryString="a=$urn:XYZ$&b=$urn:ABC$"). In the latter case, the client needs to be aware of the provided schemes, and has to compute appropriate values for them"* (§I.2.3.3). The mechanism is still author-declared, and its unknown-variable rule collides with R29.3. See G6. |

### Opportunity declaration

| R | Theme | Base specification status |
|---|---|---|
| R4 | Publisher-declared max on every slot, Player-enforced | **partial** — the cap, the trim, the zero case and the replacement asymmetry exist for the linear slot. §5.16.5.2 defines `@maxDuration` as specifying *"maximum duration of the Alternative Presentation, expressed in units of EventStream@timescale"*, with *"If the Alternative Presentation initiated by this event has a longer duration than specified in this element, it shall be terminated at the end of this duration"* and *"If the value of @maxDuration is zero, the event is not executed"* (R4.7). The replacement asymmetry R4.6 rests on is `@clip`: *"If the value of this attribute is "true", the alternative presentation shall terminate at the latest at time PRT + APDmax. If the value is "false", the presentation shall terminate at time PRTA + APDmax"* (Table 62). R4.1 / R4.8 / R4.10 narrow the base default — *"If absent, the value is assumed to be infinity, in which case the current presentation resumes only when the alternative presentation terminates"* — and the schema carries that default as a number, `default="2251799813685247"` (§5.16.6). The narrowing restricts which documents conform, which is what §8.1 says a profile does (*"A profile imposes a set of specific restrictions."*); under R1.5 it is a departure from a base default and has to be carried as a recorded exception (ADR 0015; open question 7). Absent: any non-linear slot to cap, the enforcement-against-actual-length rule (R4.5), the cross-timebase rounding rule (R4.9), and R4.11's rule that a non-advancing timeline accrues nothing. |
| R31 | Pause window bounds where, not how long | **gap** — no construct in the edition is triggered by a viewer pause (G2), so there is no window to bound and nothing that distinguishes bounding a region from bounding a duration. |
| R12 | Closed IAB ad-type / placement set (plus `custom`) | **N/A** for the vocabulary (owned by the IAB); **gap** for the carrier. Searches for the placement names return zero across the whole document: `squeezeback` 0, `L-shape` 0, `side-by-side` 0, `banner` 0, and `overlay` 1 — a single occurrence in Annex K.3 listing *"second screen applications, overlays, etc."* as consumers of a service description, not an ad layout. No construct carries an ad-type or visual-placement token, so the Publisher's allowed-layout declaration, and R12.2's closed token list (`linear`, `overlay`, `overlay-corner`, `overlay-lower-third`, the two `squeezeback-l-shape-*`, `squeezeback-double-box`, `squeezeback-double-box-background`, `pause-fullscreen`, `pause-partial`, optional `custom`), are net new. The squeezeback tokens carry their geometry (ADR 0014), which removes any need for a base coordinate construct there; `custom` (R39) is the one layout that does need one (G13). |
| R15 | Creative carriers: video, image, HTML | **partial** — video is native, reached via `<ImportedMPD>` and bound by §5.3.2.6.1: *"MPDs referenced in the ImportedMPD element shall be restricted to the constraints of a single period profile as defined in 8.15."* Image and HTML are a **gap**, and doubly so: §7.3.1 states *"The @mimeType attribute of each Representation shall be provided according to IETF RFC 4337"*, and the edition never mentions a non-AV media type at all — `image/` 0 occurrences, `text/html` 0, `thumbnail` 0, against `video/mp4` 79, `audio/mp4` 36 and `application/ttml` 2 in the same search. There is nothing to relax on the media axis; there is something absent from it. |

### Selection and ordering

| R | Theme | Base specification status |
|---|---|---|
| R5 | Candidates carry ordered presentation options; Player renders the first it can satisfy | **gap** — a List MPD is a playlist, not a set of alternatives: §8.14 introduces the profile as *"intended for use in conjunction with the Alternative MPD event (see subclause 5.16)"*, and §G.29.2 calls List MPDs *"a special simplified type of MPDs needed to represent a playlist of MPDs"*. No construct lets one ad candidate carry an ordered list of (form + layout) options. Three constructs express ordered preference and each is scoped elsewhere — `Preselection` (§5.3.11), `@selectionPriority` (§5.3.7.2) and `urn:mpeg:dash:fallback:2016` (§5.11.3). R8 requires all three to be weighed and the departure recorded; see G3. |
| R7 | Honour the resolution document's order | **partial** — declared-order playback is already the List MPD semantics, and the edition already drops an ad Period that fails to resolve: §5.3.2.6.3 step 2, *"In case the resolution fails, and the Linked Period contains valid content, the ImportedMPD element is removed, and consequently the Linked Period becomes a regular Period and is treated as such."* Missing is the rest of R7's vocabulary: drop-before-play on declared duration, trim-during-play on actual length, and the prohibition on re-ordering or deduplicating what survives. |
| R30 | An unsold opportunity is a document, not an error | **partial** — the **semantics** are the base specification's and are adopted unchanged. §5.16.2.2.6 lists *"Alternative MPD is a List MPD, and merge process resulted in no available media"* among the conditions under which execution fails, with the outcome *"A failed execution results in smooth continued playback of the main media presentation"*, and NOTE 3 gives R30.2 directly: *"The counter E.c has not been incremented due to the failure, consequently if E.c = 0 the event can still be executed in the future even if the value of @executeOnce is "true"."* What is missing is the document's **shape**: the schema declares `<xs:element name="Period" type="PeriodType" maxOccurs="unbounded"/>` with no `minOccurs`, so a resolution document carrying zero Periods does not validate. See G8. |

### Presentation

| R | Theme | Base specification status |
|---|---|---|
| R3 | Diverse device classes D1–D5 | **N/A** — the edition models codecs and bandwidth, not concurrent decoder budget or overlay-surface capability. Its only device vocabulary is reporting-side: Annex D.4.7 logs *"information about the displayed video resolution as well as the physical screen characteristics"*. `concurrent decoder` and `decoder count` return 0 occurrences. The capability axes R3 separates are what R29's reserved set must express. |
| R16 | Pause-ad lifecycle bound to pause state | **gap** — event processing is driven by presentation time, and a pause stops it. §5.16.2.2.5 NOTE: *"Since there is no playhead-triggered processing during the listen mode, processing always resumes at the playhead position PHP = RT."* The pause is visible to the edition in four places and none is a trigger (G2). |
| R32 | Exhausted pause-ad candidates while still paused | **gap** — depends on the pause construct that does not exist. The edition has no repeat / request-again / stop vocabulary for a slot, because no slot of its own outlives its media. |
| R34 | Pause window may be once-per-session | **partial** — the capability exists for timeline events and its counter semantics are exactly what R34.3 needs. §5.16.5.2 defines `@executeOnce` as specifying *"whether the event is executed only once during the media presentation"*; §5.16.2.2.2 defines `E.c` as *"Execution counter (number of times alternative MPD playback successfully started)"*; and §5.16.2.2.6 NOTE 3 makes a failed attempt non-consuming. What does not reach a pause window is the trigger: the queue admits an event only while *"PRT ≤ PHP ≤ EAP"* or *"PHP < PRT"* (§5.16.2.2.3), which is a playhead condition, not a viewer pause. |
| R35 | Viewer may dismiss the slot; the APS says whether and from when | **partial** — the capability exists twice in the base, both times with the opposite default. Annex K defines `ServiceDescription.PlaybackRestrictions@skipAfter`: *"describes an offset in time from the beginning of the scope of this service description till the moment the rest of that presentation may be skipped by the application"*, and *"The default value of 0 implies that skipping is allowed everywhere"* (Table K.9); §G.29.2's List MPD example carries it per ad Period inside the resolution document. The event-level `@skipAfter` (§5.16.5.2) says *"Zero duration implies that skipping is allowed everywhere"* and *"Default value is PT0S"*. R35.1 makes an undeclared slot non-dismissible, so R35's declaration is a field of this specification in the resolution document, a recorded exception to reuse (ADR 0017, `../context/06-naming-and-namespaces.md`). R35.8 keeps the event-level attribute's base meaning on linear slots. **Gap** for the non-linear carrier; two residual conflicts on linear slots (G11). |
| R36 | Early resolution of a non-linear opportunity; the resolution declares how long it keeps | **partial** — early resolution exists; resolution freshness does not. `@earliestResolutionTimeOffset` *"specifies the time interval (in units of EventStream@timescale) prior to the Event@presentationTime during which the MPD described in the @uri attribute may be requested"*, and *"If the value of this attribute is T then the above MPD can be retrieved at any time between PRT – T and PRT"* (§5.16.5.2). R36.1 adopts the base default of 60 seconds for an undeclared window (ADR 0018), so the offset is **full** by reuse. A resolved event is a boolean, `E.isResolved` — *"if true, then the alternative MPD has been successfully fetched and resolved"* (§5.16.2.2.2) — with no lifetime inside one execution, while *"The alternative MPD is resolved at each execution of the Event"* (§5.16.2.2.6) settles re-resolution across executions. The usable lifetime of an early resolution (R36.4–R36.6) is a **gap**. See G12. |
| R37 | A pause is what the viewer experiences, not a mechanism | **N/A** — consistent with the base specification's own stance: *"This document does not prescribe a specific client implementation"* (§5.16.2.2.1), and *"as DASH Client operation is not specified normatively in this document, it is also unspecified how a DASH Client conforms to a particular profile"* (§8.1 NOTE 1). The trick-mode clause says only *"The client may pause or stop a Media Presentation. In this case, the client simply stops requesting Media Segments or parts thereof"* (§A.5), which prescribes no mechanism either. Nothing to add beyond R37's own statement. |
| R38 | Player forwards the slot's allowed layouts to the APS | **gap** — no construct forwards a slot attribute onto the resolution request. The Annex I template can carry a literal the author writes, which would duplicate `@allowedLayouts` in the MPD (DP-1.2), or a scheme-defined variable the client computes (§I.2.3.3), which is author-declared and substitutes `<null>` when unknown. Neither is R38.3's reserved parameter. R38.1's family default — a slot declaring nothing admits only its own family's tokens, never `custom` — has no base anchor, because the base has no layout vocabulary at all (R12). See G6. |
| R39 | Optional `custom` overlay layout, rectangle in percent inside a Publisher region | **gap**, with one coordinate model to weigh. Annex H's Spatial Relationship Description expresses exactly a rectangle in a reference space with a top-left origin — *"the x-axis is oriented from left to right and the y-axis from top to bottom"* (§H.2.2) — and its containment rule is R39.4's (*"the sum of object_x and object_width is smaller or equal to total_width"*, Table H.1). It is confined to media elements: *"SRD information shall be contained exclusively in these two MPD elements (AdaptationSet and SubRepresentation)"* (§H.1). See G13. |
| R19 | Ad playback speed follows primary content | **partial** — the rate model exists. `@maxPlayoutRate` (§5.3.7.2) *"specifies the maximum playout rate as a multiple of the regular playout rate"*; Annex K.3 supplies service-declared playback-rate bounds; §D.4.6 defines `playbackspeed` as *"The playback speed relative to normal playback speed (i.e. normal forward playback speed is 1.0)"*; and §A.14.2 already ties two presentations to one speed — *"on reception, the main client will adjust its playhead propagation speed. As a result, media time elapses at the same speed in both clients."* Absent is the binding R19 needs: nothing ties an ad form's on-screen length, or the slot cap, to that rate, and nothing gives a duration to a form with no intrinsic media (R19.4). |
| R21 | Pause-ad fullscreen or partial overlay | **gap** — depends on the pause-ad construct that does not exist (R16), and on the composition facility that does not exist (R26 / R27). The two surfaces are layout tokens (`pause-fullscreen`, `pause-partial`), so they ride the R12 carrier once it exists. |
| R25 | Pause-ad presentation-time freeze in live content | **partial, and in conflict** — the freeze is the edition's own playhead behaviour, but the edition bounds it normatively and R25 as written does not. §5.16.2.2.5 step 1a: *"In case of live main media presentation, this involves clipping RT to the timeshift buffer (i.e. the time interval between TSBS and PHPLE)."* Table 62 states it for the resumption point: *"If RT is in the past, the playback shall start from the oldest available media segment (the edge of the timeshift buffer)."*, and NOTE 2 names the cause — *"The above can happen in case a user pauses the alternative Media Presentation."* See G9. |
| R26 | Side-by-side / double-box with background element | **gap** — no compositing facility exists. Two constructs come close and neither is one: Annex H SRD positions encoded video (*"a spatial relationship may express that a video represents a spatial part of another full-frame video (e.g. a region of interest, or a tile)"*, §H.1), and §5.8.5.16's supplementary video descriptor (`urn:mpeg:dash:supv:2022`) disclaims the composition: *"Potential manipulation of the stream and the composition of the main video and the supplementary video are out of the scope of the DASH client."* Both are video-to-video; neither carries an image background or an ad surface. See G1. |
| R27 | L-shape / squeezeback, one full-frame ad creative | **gap** — same as R26, and the creative may be an image or HTML surface, which R15 already shows has no carrier on the media axis. |

### Interaction and composition rules

| R | Theme | Base specification status |
|---|---|---|
| R14 | Sequential non-linear candidates within a slot | **gap** — there is no non-linear slot to sequence candidates inside. The ordering contract itself is borrowable from the List MPD profile once the slot exists. |
| R17 | Pause-ad priority over overlay, and over linear | **gap** — depends on the R14 / R16 constructs. R17.5's linear leg has a precedent worth citing rather than a carrier: during an alternative presentation the main client is suspended — *"the alternative access engine outputs media to the media engine, while the main client will be paused or be in a listen mode"* (§4.2) — which is the edition's own model of one presentation standing down for another. |
| R20 | Overlapping same-family windows: first-window-wins with fallback | **partial** — for the **linear family the rule is the base specification's and is adopted verbatim**. §5.16.2.2.5 step 2: *"If execution fails, steps a-c above are repeated for next events in QE, until: — Execution succeeds, or — PRT of the topmost event in the queue is in the future (i.e. PRT > PHP), or — The queue is empty"*, closing with *"If no event can be successfully executed, the playback continues uninterrupted."* The queue is *"a priority queue of references to a subset of events in table T, ordered by the presentation time PRT"* (§5.16.2.2.2), which is R20.3's ordering. R20.2's single-stream rule is §5.10.2.1: *"A Period shall contain at most one EventStream element with the same value of the @schemeIdUri attribute and the value of the @value attribute, i.e. all Events of one type shall be clustered in one Event Stream."* What is **gap**: the queue exists only for Alternative MPD events, so the non-linear families inherit nothing; and R20.3's tie-break by document position and R20.5's per-window binding have no base anchor at all. R20.4 routes a wrong-family document to a failed execution, which is the base's own outcome class (*"Alternative MPD is unavailable or invalid"*, §5.16.2.2.6); the family test that triggers it is this specification's. See G7. |
| R22 | At most one active non-linear form | **gap** — the edition has no concurrently presented ad surface to bound. The bound is fixed at one by R22 and is not a Publisher slot declaration (`../context/02-actors.md`), so no concurrency attribute is needed. Its own single-alternative model is the same reasoning applied to linear and is the precedent R22 should cite (§4.2, quoted under R17). |

### Tracking

| R | Theme | Base specification status |
|---|---|---|
| R6 | Tracking beacon carrier | **full** — §5.10.4.5.1: *"DASH Callback events are indications in the content that it is expected by a DASH Client to issue an HTTP GET request to a given URL and ignore the HTTP response."* and *"A content author may use such an event for tracking play-back of specific content on a server that is not included in the media path."* That is a beacon, named as one. One authoring correction the spec must carry: `Event@messageData` is declared `use="prohibited"` in the 6th-edition schema, *"Deprecated in favor of carrying the message information in the value space of the event"* (§5.10.2.3), so the beacon URL rides in the `Event` element's content. R6.5's per-candidate de-duplication key, R6.6's timebase for a candidate-hosted stream and R6.7's validation obligation have no base anchor and are spec-side. |
| R13 | ADS-directed beacon schedule, relative timings | **partial** — the carrier is full (R6) and the relative timebase falls out of the sub-MPD's own Period timeline. The obligations R13 adds — the Player executes the schedule it reads, and stops firing at an R4 trim boundary — are spec-side. R13.4's prohibition on a parallel scheme is satisfied by reuse, not by anything the base specification says. |
| R23 | Application-level ad metadata carrier | **gap** — `AdSystem`, `AdTitle` and `UniversalAdId` each return 0 occurrences in the edition. Conveyance is via a foreign-namespace element under §5.2.1; a legacy client removes it under the same clause's authoring obligation, so nothing in the ad presentation breaks. Low-stakes by construction, since R23 makes emitting and reading both optional. |
| R24 | Non-AV creative asset carrier | **gap**, and the closing facts are narrower than DR-6 records. The RFC 4337 constraint of §7.3.1 binds `Representation@mimeType`, and §5.3.2.2 Table 4 closes the events-only Period: *"At least one Adaptation Set shall be present in each Period unless the value of the @duration attribute of the Period is set to zero."* But the descriptor and open-content axes are **not** confined to the media elements: the schema declares `SupplementalProperty` and `EssentialProperty` children on `MPDtype`, `PeriodType`, `RepresentationBaseType`, `EventStreamType` and `EventType`, and `<xs:any namespace="##other">` on all of those plus `DescriptorType` itself. A carrier hosted on `<Event>` or `<EventStream>` therefore never touches the MIME axis. See G4. |
| R33 | Pause-ad delivery measured with the base play-list metric | **full for the metric, partial for its availability.** §D.4.6 defines `PlayList` as *"A list of playback periods. A playback period is the time interval between a user action and whichever occurs soonest of the next user action, the end of playback or a failure that stops playback"*, with `starttype` including *"Resume - Resume from pause"* and `stopreason` values `UserRequest` and `Rebuffering` — exactly the two fields R33 derives the paused interval from. §5.9.1 supplies both R33.3 and R33.4: *"This document does not define mechanisms for reporting metrics; however, it does define a set of metrics and a mechanism that may be used by the service provider to trigger metric collection and reporting at the clients, if a reporting mechanism is available. The trigger mechanism is based on the Metrics element in the MPD."* The partial is a placement constraint R33.4 must respect: §8.15.2 lists `MPD.Metrics` among the elements *"The MPD shall not include"* in a Single-Period Static MPD, so the declaration belongs on the primary MPD and can never travel in an imported ad MPD. |
| R28 | ClickThrough carrier, normative and interoperable | **gap**, and structurally so. `ClickThrough` returns 0 occurrences. The deeper absence is the trigger: every event is evaluated against presentation time, and the callback scheme fires at a scheduled one and *"the client is expected to entirely ignore the response"* (§5.10.4.5.1). A click has no presentation time. The edition does contemplate user action — `@skipAfter` (§5.16.5.2, Table K.9) — and Annex L fires an HTTP request off the timeline on a selection, which is the precedent R8 wants. See G5. |

### Governance

| R | Theme | Base specification status |
|---|---|---|
| R8 | Justify any addition or omission | **N/A** — spec-authoring obligation. §4 of this document is its input. |
| R9 | Minimise net new constructs | **N/A** — spec-authoring obligation. |
| R10 | Do not recreate a layout system | **N/A** — the edition carries no overlay layout primitives to recreate. Annex H SRD is a coordinate model for encoded video, not a layout system, and R39's `custom` exception is the one place it becomes relevant (G13). |

## 3. Gaps detail

Thirteen gaps follow from the matrix.

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
  resolution within a video with a bigger spatial resolution."* It is rejected
  for R26 / R27 for a stated reason rather than an assumed one: it carries no
  ad, no layout token and no non-video surface, and it explicitly hands the
  composition back — *"Potential manipulation of the stream and the composition
  of the main video and the supplementary video are out of the scope of the DASH
  client."*

  It matters beyond the rejection. §5.8.5.16.4 specifies `@processingInfo` for
  VVC such that the descriptor *"enables achieving picture-in-picture using a
  single VVC decoder"*, *"This way, separate decoding of the main video and the
  supplementary video is avoided."* That is the technique OOS-6 declares out of
  scope for this edition, already standardised in the document this
  specification extends. The OOS-6 exclusion stands as a scope decision, but it
  should cite this clause (open question 9).

- **Annex H SRD** (`urn:mpeg:dash:srd:2014`) positions encoded video tracks in a
  shared coordinate system for tiling and region-of-interest selection, and is
  confined to two elements — *"SRD information shall be contained exclusively in
  these two MPD elements (AdaptationSet and SubRepresentation)"* (§H.1).
  Reusing it as a composition carrier would both misuse the construct and build
  the parallel layout system R10 forbids. Its value convention is a separate
  question, raised by R39 (G13).

- **Annex L `urn:mpeg:dash:nonlinearplayback:2020`** is normative and, despite
  the name, is not about non-linear ads: *"This Annex provides Nonlinear
  Playback capabilities, to serve Interactive Storyline content"* (§L.1). It
  defines no overlay, no composition and no ad semantics. It is a
  **precedent**, not a carrier — see G2 and G5.

Verified negatively across the whole edition: `squeezeback` 0 occurrences,
`L-shape` 0, `side-by-side` 0, `banner` 0, `overlay` 1 (Annex K.3, unrelated).
The same search over terms known to be present returned `advertis` 15,
`picture-in-picture` 3 and `VAST` 5, so the zeros are the document's and not the
instrument's.

What the spec must add, under the SVTA Ads WG namespace per
[`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md):

- A non-linear **opportunity declaration** in the primary MPD, carrying the
  Publisher's allowed-layout set (R12, R38), the duration cap (R4), the optional
  custom region (R39), the optional early-resolution offset (R36) and the
  optional once-per-session bound (R34). §5.10.2.1 already authorises its shape
  — the Event *"may contain further XML elements meaningful for a particular
  event scheme"* — so this is an extension of an existing carrier rather than a
  new one. The SGAI `EventStream` carries no `@value` per
  `../context/06-naming-and-namespaces.md`; the base specification has the same
  pattern for an attribute a scheme does not use — for `mp4protection`, *"The
  value space of the @robustness attribute is not defined for this scheme and
  therefore the attribute shall not be present"* (§5.8.5.2.2).
- A non-linear **resolution document** carrying the candidates, their
  presentation options (G3), their tracking (R6 / R13), the dismissal
  declaration (R35) and the freshness declaration (R36). One base rule closes
  part of the design space before it opens: §8.14 rule 5, *"List MPDs shall not
  contain Alternative MPD events."* A resolution document that reuses the List
  MPD structure cannot declare a nested ad opportunity inside itself, so an
  overlay or pause window is signalled from the primary MPD and nowhere else.
  UC-08's shared candidate has to be expressed Publisher-side.
- The composition rules as Player obligations: one active form at a time (R22),
  candidates sequenced in declared order (R14), the side-by-side with its image
  background (R26), the two-element L-shape (R27), and the cross-family priority
  of R17 including its linear leg (R17.5).

### G2 — No pause-state trigger anywhere in the edition (R16, R21, R31, R32, R34, R37)

Every event in the edition is scheduled against presentation time. §5.10.1:
*"Events are timed, i.e. each event starts at a specific media presentation time
and may have a duration."* A pause stops presentation time, and with it the
processing: §5.16.2.2.5 closes with the NOTE *"Since there is no
playhead-triggered processing during the listen mode, processing always resumes
at the playhead position PHP = RT."* (`pause` occurs 8 times in the edition;
all are listed or covered below.)

The pause is visible to the edition in four places, and none of them is a
trigger:

- §A.5, as client behaviour: *"The client may pause or stop a Media
  Presentation. In this case, the client simply stops requesting Media Segments
  or parts thereof."*
- §4.2, as a playhead condition: the playhead can change *"if the media engine
  is instructed with seek or pause operations"*.
- §D.4.6, as a report: `starttype` value *"Resume - Resume from pause"*. This is
  what R33 measures with, and it is a record after the fact.
- §A.14.2, informative, as a speed: the alternative client's `adjust speed(S)`
  message, where *"S = 0 is pause"*.

The shape the spec must take follows from that asymmetry. What is declared on
the timeline is the **window of validity**, which a timeline-scheduled `<Event>`
expresses natively and which is exactly what R31 says the window bounds — where,
not how long. The **trigger** is Player-side and fires on the pause transition
inside that window. R16's lifecycle, R21's admissible surfaces, R32's
exhaustion behaviour and R34's once-per-session bound are then Player
obligations the spec states; the base specification contributes the window's
placement and nothing else. R37 needs nothing from the base specification: how a
Player pauses is client operation, which §8.1 NOTE 1 declines to specify.

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
holding a device matrix (R5.4), and that makes UC-13 and UC-15 indistinguishable
from it at the Player.

The edition does contain ordered preference, three times:

- **`Preselection` (§5.3.11.1)** *"define user experiences that can be selected
  by the DASH Client"* and combines components into one jointly rendered
  experience, not alternatives to choose between; `@preselectionComponents` is
  *"a white space separated list in processing order"*.
- **`@selectionPriority` (§5.3.7.2)** — *"In the absence of other information,
  higher numbers are the preferred selection over lower numbers"*. It is a
  numeric hint on `RepresentationBaseType`, running in the opposite direction
  from document order, and it is explicitly conditional on there being no other
  information.
- **`urn:mpeg:dash:fallback:2016` (§5.11.3)** states R5's rule almost verbatim —
  *"If multiple URLs are provided, the content author expresses the preferences
  of using one of those by the order with the first one having the highest
  preference"* — but at the granularity of whole presentations, on an MPD-level
  descriptor of which *"Each MPD may contain at most one"*, and triggered by an
  error condition rather than by a capability check.

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

**The profile chain.** §5.3.2.6.1: *"MPDs referenced in the ImportedMPD element
shall be restricted to the constraints of a single period profile as defined in
8.15."* §8.15.2 requires that *"The rules for the MPD as defined in subclause
7.3 shall apply"*, and §7.3.1 states *"The @mimeType attribute of each
Representation shall be provided according to IETF RFC 4337."* §8.14 rule 4
lets a List MPD contain regular Periods under the List profile, itself *"an
extension of the ISO-BMFF CMAF Profile"*, so the same constraint reaches inline
Adaptation Sets there.

**The absence.** The edition never mentions a non-AV media type. Searches over
the full document return `image/` 0 occurrences, `text/html` 0 and `thumbnail`
0, against `video/mp4` 79, `audio/mp4` 36, `application/mp4` 4 and
`application/ttml` 2 from the same search. Carriage of a still image or an HTML
document as a Representation is simply not defined in the document this
specification extends.

**The Period constraint.** §5.3.2.2 Table 4: *"At least one Adaptation Set shall
be present in each Period unless the value of the @duration attribute of the
Period is set to zero."* An events-only Period of non-zero duration is not a
legal carrier, which is DR-7 and which holds.

**What DR-6 gets wrong, and it changes the answer.** DR-6 records of the two
descriptor carriers that *"they sit on AdaptationSet / Representation /
Sub-Representation, so both inherit DR-5's MIME constraint unless hosted inside
a foreign-namespace parent"*. The schema says otherwise. `SupplementalProperty`
and `EssentialProperty` are declared as children of `MPDtype`, `PeriodType`,
`RepresentationBaseType`, `EventStreamType` and `EventType`, and
`AlternativeMPDEventType` carries `SupplementalProperty` directly
(§5.10.2.3, §5.16.6). `<xs:any namespace="##other" processContents="lax"/>`
appears on all of those and on `DescriptorType` itself. A descriptor or a
foreign-namespace element hosted on `<Event>`, `<EventStream>` or on the
alternative-MPD event element therefore never touches the
`Representation@mimeType` axis, and inherits no MIME constraint to escape.

The one placement that is genuinely closed is the one DR-6 does not mention:
`ImportedMpdType` is declared as `xs:simpleContent` extending `xs:anyURI` with
`<xs:anyAttribute namespace="##other" processContents="lax"/>` and no `xs:any`
(§5.3.2.6.2). A foreign-namespace **attribute** may hang off `<ImportedMPD>`; a
foreign-namespace **child element** may not.

What the spec must add: an explicit carrier choice per construct, recorded in
the per-construct classification that Item 8 of
[`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md)
demands, and chosen against the placement facts above. Wrapping a non-MP4
payload in an `application/mp4` Representation to satisfy the registry remains
an anti-pattern: it adds no segment-delivery semantics for the underlying
format, which §8.1 makes an Interoperability Point exercise.

### G5 — No metadata carrier, and no event fired by a user activation (R23, R28)

`AdSystem`, `AdTitle`, `UniversalAdId` and `ClickThrough` each return 0
occurrences in the edition. For R23 that is a low-stakes gap: the carrier is
optional on both ends by design, and a legacy client removing a
foreign-namespace element under §5.2.1 breaks nothing in the ad presentation.

R28 is the harder half, and the difficulty is the event model rather than the
missing field. Events are timed (§5.10.1), and the callback scheme fires at a
scheduled presentation time and discards what comes back: *"the client is
expected to entirely ignore the response"* (§5.10.4.5.1). A ClickThrough
activation has no presentation time, because it happens when the viewer acts or
never. The callback scheme is therefore the right carrier for impression and
quartiles (R6) and the wrong one for click-tracking.

The edition is not silent about user action, and the spec should use what is
there instead of claiming an absolute absence. `@skipAfter` on the
alternative-MPD event *"describes an offset in time (in fractional seconds) from
the beginning of the alternative presentation till the moment the rest of that
presentation may be skipped by the application in response to a user action"*
(§5.16.5.2) — a user action with a normative consequence, which R35.8 honours on linear
slots (G11). Annex L fires an HTTP request off the timeline on a selection (§L.3.3,
quoted in G2). What the edition lacks is an *event scheme* dispatched by a user
activation; what it has is the pattern R28's carrier should follow.

What the spec must add: the ClickThrough URL and any click-tracking URL(s)
accompanying it as a document-level construct the Player reads at render time
and fires on activation — normative and interoperable, unlike R23's best-effort
carrier, because UC-11 requires every Player conformant to this specification to
behave identically. The scoping to conformant Players is not a weakening but the
only obligation available: §8.1 NOTE 1 states that *"profiles merely specify
restrictions on MPD and Segments rather than DASH Client behaviour"*, and §5.2.1
NOTE 2 contemplates a client that removes every extension element and still
*"can use such a resulting MPD for presentation of a conforming Media
Presentation."*

### G6 — No channel for the Player to declare device capability or forward slot declarations, and two Annex I hooks that must be weighed (R29, R38, R39.3, R3)

UC-13, UC-15 and UC-16 need the Player to put information on the resolution
request: its device capability (R29), the slot's allowed layouts (R38) and the
custom region (R39.3). The edition carries an upstream channel for this class of
request; what it lacks is the payload and the author.

**The construct, named correctly.** It is `RequestParam`, of type
`ExtendedUrlInfoType` (§I.3), which *"is an extension of UrlQueryInfoType
element defined in Table I.1"*. `@includeInRequests="altmpd"` scopes parameters
to *"all requests for MPDs representing the alternative Media Presentation, as
defined in subclause 5.16"* (Table I.4). The edition declares no element named
`UrlParamInfo` — a search returns 0 occurrences, against `UrlQueryInfo` 29 in
the same search — so the reference in
`../context/05-dash-linear-interfaces.md` step 4a names something that does not
exist in this edition (§6, finding 3).

**The standard payload.** §I.4.1 states the vocabulary's purpose: *"In some
cases, such as dynamic advertisement insertion and content steering, there is a
need to express knowledge of the current state of the player."* Table I.5 is
that vocabulary in full — `audio` and `video` (the `@codecs` and `@bandwidth` of
what is playing), `lang#[audio|text]`, `encryption`, `cmcd#[key]`,
`execution-delta#[id]`, `expected-duration#[id]`, `execution-count#[id]` and
`previous-state`. What is playing and what has run; nothing about what the
device can render and nothing about the slot being resolved.

**Hook 1 — scheme-defined variables.** The template vocabulary is not closed to
third parties. §I.2.3.3 admits *"Scheme-defined signalling
(@queryString="a=$urn:XYZ$&b=$urn:ABC$"). In the latter case, the client needs
to be aware of the provided schemes, and has to compute appropriate values for
them"*, and *"Support of these specific schemes is out of the scope of this
document, except for those defined by this document."* An SVTA-owned URN
variable whose value the Player computes — a decoder count, a surface type, the
slot's `@allowedLayouts` — is therefore expressible inside the base mechanism.
It is rejected as R29's carrier for three stated reasons:

- **The author is wrong.** `@queryTemplate` *"provides URL parameters template
  information"* and is written in the MPD by the content author (Table I.1). R29
  requires that *"no declaration by the Publisher, the APS or the ADS is
  required before a Player sends them"*; a variable the Publisher did not write
  into the template is never substituted.
- **The unknown case is wrong.** *"In case of a client unaware of a particular
  scheme the string “<null> ” shall be used as a replacement of the unknown
  scheme"* (§I.2.3.3). A Player that does not implement the variable sends a
  placeholder, which is what R29.3 forbids and what R29.7's "absent means
  undetermined" cannot distinguish.
- **R29 already decided it.** The reserved parameters *"are NOT expressed
  through the MPD-declared URL-parameter template mechanism"*. The hook is
  recorded so R8's justification cites it, not to reopen the decision.

For R38 the same hook has a further cost. Writing the allowed layouts into the
template as a literal duplicates `@allowedLayouts` in the MPD, which DP-1.2
forbids; writing it as a computed variable leaves forwarding to whether the
Publisher authored the template, which R38.2 makes unconditional.

**Hook 2 — the request type.** The value space of `@includeInRequests` is not
closed. Table I.4's last row is `<URN / tag URI>`: *"a URN or tag URI, where the
request type semantics is understood by the client and specified by the URN /
tag URI owner. The client shall drop unknown URIs from the @includeInRequests
and @includeInHeaders strings prior to processing them as specified in this
Annex."* An SGAI-defined request type — the non-linear resolution request, which
`altmpd` does not cover because it is not an Alternative MPD request — can
therefore be named by a URN the SVTA Ads WG owns, with legacy-safe behaviour for
free. This is the base hook for letting an author-declared `RequestParam` reach
the non-linear resolution request alongside the reserved parameters.

The edition's only device-side vocabulary is reporting-side and is about display
geometry: §D.4.7 logs *"information about the displayed video resolution as well
as the physical screen characteristics"*. Neither decoder count nor
overlay-surface capability appears anywhere — `concurrent decoder` and
`decoder count` both return 0.

What the spec must add: a set of reserved query-parameter names on the
resolution request — capability axes, each optional, each omitted rather than
emptied (R29.2 / R29.3), absence meaning **undetermined** (R29.7), a vendor
prefix for non-reserved names (R29.4), an APS obligation to answer without any
of them (R29.5) — plus the two mandatory exceptions of R29.8: the allowed-layout
set (R38.2, sent unchanged, and not sent at all when the slot declares none —
the APS then applies R38.1's family default) and the custom region (R39.3). The capability set
must separate D1 through D5 (R29.6), which fixes its axes: concurrent
video-decoder count, and which surface types can be composited with video. The
spec must also state how the reserved parameters coexist on one request with an
author-declared `RequestParam` template, since both land on the same URL.

### G7 — The fallback chain is inherited whole for linear and has no anchor at all for the other two families (R20)

This is the gap where the base specification gives the most and the reading has
to stay narrow. §5.16.2.2.5 step 2 delivers first-window-wins with fallback in
full (quoted in the matrix), and §5.16.2.2.6 enumerates what counts as a failed
execution — *"Alternative MPD is unavailable or invalid"* and *"Alternative MPD
is a List MPD, and merge process resulted in no available media"* among them.
R20.1 adopts this rather than diverging from it: the edition calls the zero-ad
case a failed execution, and the fall-through is the consequence. The same
clause places *"@executeOnce is set to "true", and E.c > 0"* in the list, which is why R30 reads the heading as "produced no alternative
presentation this time" and not as an error.

Three things the base specification does not supply:

- **The other two families.** The queue holds Alternative MPD events. Overlay
  and pause-trigger windows are not those, so they inherit nothing — R20.1 and
  R20.3 extend the rule to them, which R8 requires be recorded as an extension
  rather than a citation.
- **The tie-break.** The queue is ordered by PRT (§5.16.2.2.2) and the edition
  does not say what happens when two windows carry the same one. R20.3's
  fallback to document position is this specification's. The distinction R20.3
  draws is real: document order governs dispatch to the application — *"all
  active events are dispatched (according to their dispatch mode) in the order
  they appear in the EventStream element"* (§5.10.2.1) — which is an earlier and
  separate step from execution order.
- **R20.5.** The binding of each window's own declarations to the candidates it
  serves has no base anchor. R20.6 already says R20.5 must be normative rather
  than illustrative.

R20.4 sits between the two. Its outcome is the base's: a document that cannot
fill the slot is a failed execution, the class §5.16.2.2.6 opens with *"The
playback of the alternative presentation cannot start"* and whose first listed
reason is *"Alternative MPD is unavailable or invalid."* Its trigger — the
family test — is this specification's, because the base has one family. The
spec should cite the failure class and state the family test as the extension.

Two neighbouring mechanisms are worth naming as rejections: `BaseURL`
alternatives retry the *same* resource from another location, and
`urn:mpeg:dash:fallback:2016` chains whole presentations on an unrecoverable
playout error. Neither chains two *opportunity windows*, and R20 should say so
rather than let a reader assume one of them covers it.

### G8 — The empty resolution has its semantics from the base specification and needs its shape from the spec (R30, R32.2, R36.6)

R30's semantics are inherited and the matrix quotes them: the zero-ad case is a
failed execution (§5.16.2.2.6), a failed execution continues the main
presentation smoothly, and NOTE 3 leaves the opportunity executable. Nothing
needs adding there.

What needs adding is the document. `Period` cardinality inside `MPDtype` is
1..N — the schema declares `<xs:element name="Period" type="PeriodType"
maxOccurs="unbounded"/>`, and an omitted `minOccurs` defaults to 1 — so a
resolution document carrying zero Periods does not validate against the Annex B
schema. The obvious workaround is closed from the other side: §5.3.2.2 Table 4
requires an Adaptation Set in every Period of non-zero duration, so a
placeholder Period must either carry media or declare zero duration.

R30 also requires the answer to be the same for a linear slot and for a
non-linear one, and the linear side has a further constraint the non-linear side
does not: *"List MPDs shall have the value of the MPD@type attribute set to
"list""* (§8.14 rule 1) and must declare the profile URN (rule 2). R32.2 and
R36.6 both route into this same shape — an empty re-resolution within a pause,
and an empty re-resolution after expiry — so it is stated once.

What the spec must add: the normative shape of a resolution document carrying
zero candidates, chosen against that cardinality constraint, stated once for
both families.

### G9 — The rate model is unbound, and the live-pause freeze has a normative limit R25 does not state (R19, R25, R4.11)

The pieces R19 needs exist. `@maxPlayoutRate` *"specifies the maximum playout
rate as a multiple of the regular playout rate"* (§5.3.7.2); Annex K.3 lets the
service bound the rates it wants used; §D.4.6 defines `playbackspeed` relative
to normal forward playback at 1.0. The edition even ties two presentations to
one speed, informatively, in §A.14.2 (quoted in the matrix). What is missing is
the binding: nothing ties an ad form's on-screen length, or the cap it is
measured against, to that rate, and nothing gives a presentation-timeline
duration to a form with no intrinsic media, which is what R19.4 requires for
`image` and `html`. R4.11 belongs here too: that a non-advancing timeline
accrues nothing against the cap is consistent with the edition's model — media
time stops on pause (§4.2) — but no clause states it for a cap.

R25 is the same concern at the other end, and here the edition does not merely
omit — it **bounds**. The freeze itself is the edition's model, since a pause
stops media time while wall-clock time advances. But the drift is bounded by the
time-shift buffer and the edition states the consequence normatively twice:
§5.16.2.2.5 step 1a clips RT *"to the timeshift buffer (i.e. the time interval
between TSBS and PHPLE)"*, and Table 62 has *"If RT is in the past, the
playback shall start from the oldest available media segment (the edge of the
timeshift buffer)."*, with NOTE 2 naming the cause as *"a user pauses the
alternative Media Presentation."* R25.1 promises the freeze *"for the full
duration of the pause"*, which the edition does not allow past
`MPD@timeShiftBufferDepth`.

What the spec must add: for R19 and R4.11, a statement of which rules operate on
which timebase — cap enforcement (R4) and beacon scheduling (R13) on the
presentation timeline, on-screen behaviour on the derived value — with
`duration` kept as the single canonical value per DP-1.2. For R25, what happens
when the pause outlives the time-shift buffer, because the pause-ad's dismissal
and the edition's mandatory trim then coincide. Leaving R25 unbounded puts the
spec in conflict with the baseline rather than on top of it.

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
guarantees that what remains is valid — but a declared profile cannot be the
thing that certifies the SGAI constructs. Only an Interoperability Point that
explicitly included them could, and §8.1 states what that costs: *"The owner of
the URI is responsible to provide sufficient semantics on the restrictions and
permission of this interoperability point."*

**`MPD@type="list"` is a presentation type defined in the main body, not a
profile.** DR-10 argues: *"That value is not a free choice of presentation
type; it is rule 1 of the ISO Base media file format List profile, and the rules
travel together"*, and the primary copy does not support the inference. §5.3.1.4
defines the value independently of clause 8: *"For Media Presentations with
MPD@type set to "list" the constraints of a static Media Presentation shall
apply"*, *"MPDs of this type shall not use MPD assembly as defined in 5.5, i.e.
the attributes from namespace @xlink shall not be present"*, and *"MPDs of
@type="list" may contain Linked Periods."* §8.14 rule 1 runs the other way — a
document conforming to the List profile must declare `type="list"` — and the
edition nowhere states the converse. The two properties DR-10 says the
suggestion was reaching for — static, no XLink — are precisely what §5.3.1.4
confers, without the profile URN.

DR-10's **conclusion** may well stand: reasons to decline `type="list"` for the
non-linear resolution document exist, since the type is bound to Linked Periods
and to the alternative-MPD flow by every other mention of it. But the stated
**reason** does not hold against the clause (§6, finding 2).

### G11 — Viewer dismissal: the base skip control exists twice with the opposite default, and the exception leaves two seams on linear slots (R35)

R35 describes a capability the base specification already has, in two places.

**The two base constructs.**

- **Event-level `@skipAfter`** on `AlternativeMPDEventType` (§5.16.5.2):
  *"describes an offset in time (in fractional seconds) from the beginning of the
  alternative presentation till the moment the rest of that presentation may be
  skipped by the application in response to a user action."* *"Duration equal
  to or exceeding the presentation duration implies that skipping is disallowed
  for its whole duration."* *"Zero duration implies that skipping is allowed
  everywhere."* *"Default value is PT0S."* The schema carries the default:
  `<xs:attribute name="skipAfter" type="xs:duration" default="PT0S"/>`
  (§5.16.6). It is written by the Publisher, in the MPD.
- **`ServiceDescription.PlaybackRestrictions@skipAfter`** (Annex K, Tables K.9
  and K.18): *"describes an offset in time from the beginning of the scope of
  this service description till the moment the rest of that presentation may be
  skipped by the application. The value of Inf implies that skipping is not
  allowed within the scope of this service description."*, and *"The default
  value of 0 implies that skipping is allowed everywhere."* (Table K.9); typed
  `xs:duration`, default `"PT0S"` (Table K.18). §G.29.2's List MPD example —
  the linear resolution document — carries it per ad Period (*"we can skip this
  ad having played its first 5 seconds"*), and marks the Periods without it
  *"no playback restrictions, the user is permitted to skip this ad"*.

**What matches R35.** Seconds from the start of rendering (R35.2), zero meaning
immediately, a value meaning never, and "the rest of that presentation may be
skipped", which ends the whole alternative presentation — R35.4's slot, not one
ad.

**What does not, and how it is settled.** Both constructs default to
skip-allowed; R35.1 makes an undeclared slot non-dismissible (*"the capability
is granted and never assumed"*). Reusing either would bring the default along,
which the naming rule of
[`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)
does not allow. R35's declaration is therefore a field this specification
defines in the resolution document under the extension namespace — the
exception R1.5 permits, recorded in ADR 0017. The new field is **net new** and
is the gap: `dismiss` returns 0 occurrences in the edition (the same search
finds `skipAfter` 7 and `PlaybackRestrictions` 8).

On a non-linear slot the primary content never stopped, so the consequence is
"remove the ad surface" rather than "resume the main presentation", and R35.6's
beacon cut-off is spec-side. Both are Player obligations the spec states
(R35.3–R35.6).

**Two seams on linear slots.** R35.8 keeps the event-level attribute's base
meaning and states the aim: *"a Player of this specification and a base Player
treat the same linear event the same way."*

- **An event that omits `@skipAfter`.** R35.8 applies R35.1's default *"only
  where neither the event nor the resolution document declares anything."* But
  the base gives the omitted attribute a value: `PT0S`, skippable everywhere,
  and the schema writes it into the infoset. For that event a base Player
  permits skipping and a Player applying R35.1 does not, which is the divergence
  R35.8 exists to prevent — and R1.5 says the base answer wins where it has one.
  Whether "carries the base declaration" means "present in the document" or
  "has a value under the base" decides it (open question 11; §6 finding 5).
- **A linear resolution document carrying `PlaybackRestrictions`.** R35.8 names
  only the event's declaration. A List MPD carrying Annex K's restriction per
  ad Period — the base specification's own example — is a second base
  declaration, in the resolution document, at per-ad granularity, which R35
  rejects. `../context/` does not say how a Player of this specification treats
  it, nor which wins when it and this specification's field are both present
  (open question 12).

### G12 — Early resolution is the base mechanism, default included; resolution freshness has no anchor (R36)

**Early resolution is the base mechanism, and the window-start anchor is not a
new computation.** ERT is *"a media time defined by the value of
Event@presentationTime, minus the value of
AlternativeMPDEventType@earliestResolutionTimeOffset, normalized by the value of
@timescale"* (Table 57). An overlay or pause opportunity window declared as an
`<Event>` has an `Event@presentationTime` that **is** the start of its window,
so R36.2's and R36.3's "offset before the start of the window" is ERT computed
the base specification's way, for both families. For a pause there is no
presentation time of the pause itself, but there is one for the window, and the
window is what the offset is computed against (R36.3).

**The default is adopted.** The attribute's semantics give *"The default is 60
seconds in units of timescale"* (§5.16.5.2). R36.1 takes the same default for a
window that declares nothing, and a Publisher who wants resolution at fire time
declares zero (ADR 0018). That is R1.5 applied, and the reuse carries name,
units and default as
[`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)
requires. Two properties of the base attribute the spec has to carry with it
rather than rediscover:

- **The default lives in prose only.** The schema declares
  `<xs:attribute name="earliestResolutionTimeOffset" type="xs:unsignedLong"/>`
  with no `default` (§5.16.6), unlike `@maxDuration` and `@skipAfter` beside it.
  A schema-driven reader sees an absent attribute; the 60 seconds come from the
  semantics table, and are expressed as 60 × `EventStream@timescale` ticks.
- **Two variants, two units.** On the event the offset is in
  `EventStream@timescale` units; on `ImportedMPD` it is
  `type="xs:double" default="60.0"`, in seconds (§5.3.2.6.2). The non-linear
  windows reuse the event variant.

**Freshness has no anchor inside one execution.** Within an execution the base
specification fetches once, anywhere in the interval: *"The alternative MPD is
fetched from the URL specified in AlternativeMPDEventType@uri and is resolved
when the playhead is between the ERT and PRT; the precise timing of the
resolution is not defined in this document"* (§5.16.2.2.1 step 2). `E.isResolved`
is a boolean with no lifetime (§5.16.2.2.2). Across executions the base answer
exists and should be cited: *"The alternative MPD is resolved at each execution
of the Event, and a previous failure to resolve the MPD of the same event does
not impact the current resolution"* (§5.16.2.2.6), and *"a seek backwards
operation may cause a repeated MPD download and resolution"* (§5.16.2.2.1). The
one expiry concept in the edition, MPD validity expiration (§5.10.4.2), signals
that an MPD *"with a specific publish time"* is superseded by an update, which
is an MPD update mechanism and not the lifetime of a resolved alternative MPD.
`freshness` and `stale` both return 0.

What the spec must add: the APS-declared usable lifetime of a resolution
(R36.4) and its default — usable for as long as the window lasts — the Player's
check at fire time (R36.5), and the empty-resolution routing of a failed
re-resolution (R36.6, into G8). R36.7's "resolving early is a permission" matches
the base wording *"may be requested"* and the informative §5.16.2.2.6 NOTE 1,
*"There is no necessity to resolve at time ERT"*, and needs no addition.

### G13 — The `custom` layout's rectangle: a coordinate model exists and is confined to media elements (R39)

R39 introduces the one position this specification defines. The base
specification has one coordinate model, and R8 / R9 require it to be weighed.

**Annex H SRD matches R39's geometry.** The coordinate system has *"an arbitrary
origin (0; 0); the x-axis is oriented from left to right and the y-axis from top
to bottom"* (§H.2.2). A reference space is *"the rectangular region
encompassing the entire source content, whose top-left corner is at the origin
of the coordinate system"*, sized by `total_width` / `total_height` *"expressed
in arbitrary units"*. Objects are placed by `object_x`, `object_y`,
`object_width`, `object_height`, each a *"non-negative integer in decimal
representation"* (Table H.1). With `total_width` and `total_height` both 100,
that is R39.2's percent-of-viewport rectangle with a top-left origin, and the
SRD rule that *"the sum of object_x and object_width is smaller or equal to
total_width"* (Table H.1) is R39.4's containment test applied to the viewport.

**It is not reusable as a carrier.** *"SRD information shall be contained
exclusively in these two MPD elements (AdaptationSet and SubRepresentation)"*
(§H.1), and a Spatial Object *"is represented by either an Adaptation Set or a
Sub-Representation"*. The custom region sits on a slot declaration and the
custom rectangle on a presentation option; neither is either element. Its values
are also integers, which R39 does not state.

**What the spec must decide.** Whether R39's region and rectangle reuse SRD's
parameter names, order and integer domain as a value convention in an SVTA
construct — which is what `../context/06-naming-and-namespaces.md` asks when a
component *"is in essence the same"* as a baseline one — or define their own and
record under R8.2 why SRD was not reused (open question 13). SRD's `@value` is
*"a comma-separated list of values for SRD parameters"* (§H.2.1), where the
project's preferred list delimiter is space; that choice follows whichever way
the reuse question goes. Either way, R39 stays the declared exception to R10.2 /
R10.3 and OOS-3: a coordinate rectangle for one optional overlay layout is not a
layout engine, and SRD is not one either.

The forwarding of the region on the resolution request (R39.3) is G6's
mandatory-parameter exception and is not a separate gap.

## 4. Reuse opportunities

The spec MUST reuse the constructs below before introducing new ones (R9), and
document each reuse or departure inline (R8).

| Existing construct | Reused for | Notes |
|---|---|---|
| `EventStream` + `<Event>` (§5.10) | Every new SGAI opportunity declaration — non-linear slot, pause window | The authoring vehicle for timeline-anchored signalling, and already open to us: `EventType` is `mixed="true"` with `<xs:any namespace="##other">` and `<xs:anyAttribute namespace="##other">`. A Player that does not implement the `schemeIdUri` ignores the stream (§5.10.1), which is half of R1. `EventStream@value` is scheme-owned — *"The value space and semantics is expected to be defined by the owners of the scheme identified in the @schemeIdUri attribute"* (Table 43) — so the SGAI schemes' "no `@value`" rule is within the owner's discretion, with §5.8.5.2.2's `@robustness` as the base precedent. |
| Callback event scheme `urn:mpeg:dash:event:callback:2015` (§4.7 / §5.10.4.5) | All timeline-scheduled tracking beacons (R6, R13) | Reused verbatim; R13.4 forbids a parallel scheme. The URL rides in the `Event` element's content, not in `@messageData`, which the schema declares `use="prohibited"`. Does **not** cover click-tracking, which has no presentation time (G5). |
| List MPD profile `urn:mpeg:dash:profile:list:2024` (§8.14) | The resolution document baseline | Gives declared-order playback, which is R7's baseline. Three rules bound the reuse: *"List MPDs shall not contain XLink attributes defined in subclause 5.5"*, *"List MPDs shall not contain Alternative MPD events"*, and the profile is *"an extension of the ISO-BMFF CMAF Profile"*. |
| `MPD@type="list"` (§5.3.1.4) | Declaring the resolution document static and XLink-free | Defined in the main body independently of §8.14, and it confers exactly those two properties. Whether the non-linear document takes it is open; the reason to decline it is not the one DR-10 gives (G10). |
| `<ImportedMPD>` (§5.3.2.6) | Per-ad sub-MPDs for video creatives | Restricted to §8.15. The URL is the element's text content and its one attribute is `@earliestResolutionTimeOffset` (`xs:double`, default `60.0`, seconds). Accepts foreign-namespace **attributes** and no foreign-namespace **child elements**. Fine for video; the §8.15 binding is why it is unusable for image / HTML (G4). |
| `@maxDuration`, `@clip` and the trim rule (§5.16.5.2, Table 62) | R4's enforcement baseline, including its two-sided meaning | The non-linear cap reuses the name, the units (`EventStream@timescale`) and the zero semantics rather than inventing a second duration vocabulary, per the naming-consistency rule. The absent-means-infinity default is the one characteristic R4.8 / R4.10 deliberately narrow, which R8.2 requires be stated where the construct is reused. |
| `@executeOnce` and the `E.c` counter (§5.16.5.2, §5.16.2.2.2, §5.16.2.2.6 NOTE 3) | R34's once-per-session bound, and R30.2's non-consumption | The capability and the counter semantics are both already right; only the trigger changes from playhead to first render (G2). Reuse the name. |
| `ServiceDescription.PlaybackRestrictions@skipAfter` (Annex K, Tables K.9 / K.18) | **Weighed and not reused for R35** (ADR 0017) | Semantics match R35.2; the default `PT0S` contradicts R35.1. Its presence in linear List MPDs (§G.29.2) still has to be addressed (G11, open question 12). |
| `@earliestResolutionTimeOffset` (§5.16.5.2 and Table 5) | R36's early-resolution offset on overlay and pause windows, default included (ADR 0018) | ERT against the window event's `@presentationTime` is R36.2 / R36.3 unchanged. The 60-second default is stated in the semantics and absent from the schema; the event and `ImportedMPD` variants use different units (G12). |
| `@noJump` (§5.16.5.2) | Preserved on inherited linear breaks; excluded on the non-linear families per OOS-7 | OOS-7's exclusion is an exception with a stated reason, which is what R8 asks of an omission. |
| Event-level `@skipAfter` (§5.16.5.2) | Honoured with its base meaning on linear slots (R35.8, ADR 0019); precedent for a user action with a normative consequence (G5) | Publisher-authored in the MPD, so not R35's carrier. Its schema default `PT0S` is where R35.8's equivalence with a base Player breaks (G11, open question 11). |
| `@serviceDescriptionId` (§5.16.5.2) | Binding a slot to a service description | *"specifies the value of the @id attribute of a ServiceDescription element applicable to this Event and to any presentation initiated as a result of executing this Event."* Available on the non-linear slot for the same purpose without a new construct. |
| Alternative-MPD execution model (§5.16.2.2) | R20's chain, R30's failure semantics, and R22's rationale | The priority queue, the failure conditions, the fall-through, the non-incremented counter and listen mode. Inherited whole for linear and extended to the other families (G7). |
| Listen mode (§4.2) | R22's and R17.5's precedent | The edition's own one-presentation-at-a-time rule, and the model for suspending a linear ad under a pause ad. |
| `adjust speed(S)` dual-client model (§A.14.2, informative) | R19's precedent | Two presentations, one propagation speed, with `S = 0` for pause. |
| `PlayList` metric (§D.4.6) and the `Metrics` element (§5.9.1) | R33, adopted unchanged | One placement constraint: §8.15.2 forbids `MPD.Metrics` in a Single-Period Static MPD, so R33.4's declaration lives on the primary MPD only. |
| MPD fallback scheme `urn:mpeg:dash:fallback:2016` (§5.11.3) | **Precedent for R5; rejection for R20** | Document-order-as-preference is the edition's own convention. Wrong granularity for R20 (whole presentations, error-triggered). |
| `Preselection` (§5.3.11) and `@selectionPriority` (§5.3.7.2) | **Considered and rejected for R5** | `Preselection` combines components into one experience; `@selectionPriority` is a numeric hint running the opposite way from document order (G3). |
| Supplementary video descriptor `urn:mpeg:dash:supv:2022` (§5.8.5.16) | **Considered and rejected for R26 / R27; cited for OOS-6** | Carries no ad, no layout and no non-video surface, and hands the composition to the application. Its VVC single-decoder path (§5.8.5.16.4) is the technique OOS-6 excludes (G1). |
| Annex H SRD `urn:mpeg:dash:srd:2014` | **Rejected as a carrier; weighed as the value convention for R39** | Confined to `AdaptationSet` and `SubRepresentation`. Its parameters, origin and containment rule match R39's rectangle when the reference space is 100 × 100 (G13). |
| Annex L `urn:mpeg:dash:nonlinearplayback:2020` | **Precedent, not carrier** | A timeline-anchored `<Event>` declaring a window, with the decision resolved off the timeline through a callback to `@contactURL` (G2, G5). |
| Foreign-namespace open content (§5.2.1) | Every new SGAI element and attribute | The single normative extension point, backed by `<xs:any namespace="##other" processContents="lax"/>` on `MPDtype`, `PeriodType`, `RepresentationBaseType`, `EventStreamType`, `EventType`, `AlternativeMPDEventType` and `DescriptorType`. DR-3's authoring rule governs placement. |
| Vendor descriptors (§5.8.4.8 / §5.8.4.9) | Carrier for metadata and for non-AV asset URLs (R23, R24) | The legacy split is the one DR-9 states. Their placement is wider than DR-6 records: declared on `MPD`, `Period`, `RepresentationBaseType`, `EventStream` and `Event`, plus `SupplementalProperty` on the alternative-MPD event (G4). |
| Annex I `RequestParam` and its two hooks — scheme-defined `$urn:…$` variables (§I.2.3.3) and the `<URN / tag URI>` request type (Table I.4) | **Rejected for R29 / R38 / R39.3 payloads; weighed for the request scoping** | Author-declared template, standard vocabulary without capability axes, and an unknown-variable rule that sends `<null>` where R29.3 requires omission. The request-type URN is the hook for naming the non-linear resolution request (G6). |

## 5. Open questions

1. **Shape of the non-linear resolution document.** Extend the List MPD
   structure (Periods plus `ImportedMPD`) or define a separate document type
   under the SVTA namespace? Reuse maximises R9 but inherits §8.14's rules — no
   Alternative MPD events inside, no XLink — and forces every non-AV creative
   through a non-media carrier. `MPD@type="list"` is available from §5.3.1.4
   without the profile URN, so "static and XLink-free" and "enrolled in the List
   profile" are separable decisions (G10). The answer also fixes where R35's
   `ServiceDescription` and R36's lifetime sit. Needs a WG decision.
2. **Encoding of the zero-candidate resolution document (R30).** The semantics
   are settled and inherited; the shape is not. `Period` cardinality is 1..N and
   a Period of non-zero duration needs an Adaptation Set, so the options are a
   zero-duration placeholder Period or a resolution document shape of its own.
3. **The reserved parameter set (R29, R38, R39.3).** Which capability axes it
   contains and how each is written is left open by R29.1; R29.6 sets the
   acceptance test (tell D1–D5 apart). Needs the concrete names and value
   spaces, the encoding of the allowed-layout set and of the custom region, how
   the reserved parameters coexist with an author-declared `RequestParam`
   template on one URL, and whether the non-linear resolution request is named
   by an SVTA-owned URN in `@includeInRequests` (G6).
4. **Single-option versus multi-option candidates (R5, UC-09 vs UC-13).** Both
   are conformant and the Player-visible interface is identical, so the document
   does not show whether the APS filtered. Is that indistinguishability
   acceptable, or should the document record that a filter was applied?
5. **Bound on the R25 freeze.** The edition trims the resumption point to the
   time-shift buffer, so the freeze cannot hold past `MPD@timeShiftBufferDepth`.
   R25 promises it for the full duration of the pause. Decide whether R25 is
   amended to state the bound or the spec declares the pause ad dismissed when
   the buffer expires — and what happens to pending beacons when the resume is a
   trim to the buffer start or a jump to the live edge.
6. **Declaring the constructs at all (G10).** §8.1 step 4 strips
   extension-namespace content during profile conformance checking unless the
   profile explicitly includes it. Does the project want an Interoperability
   Point URI that includes the SGAI namespace, or is "valid base document plus
   constructs a conformant Player reads" the declared position? R28's scoping
   under DR-8 suggests the second; it has not been stated as a decision.
7. **Where R4.10's narrowing is written.** R4.10 is decided (ADR 0015), and the
   narrowing is profile-shaped: it changes which documents conform, not what a
   construct means. If the non-linear slot reuses `@maxDuration`, the absent
   case is a characteristic the reuse does not carry, and R8.2 wants that stated
   at the reuse site. On an inherited linear event it is a restriction a legacy
   Player does not apply — that Player plays an uncapped linear break the SGAI
   Player skips. R1.5 lets that stand only as a recorded exception, and R35.8
   resolves the parallel case for `@skipAfter` the other way — base behaviour
   kept on linear slots. Confirm the divergence on inherited linear slots is
   intended and that ADR 0015 is the exception R1.5 asks for.
8. **Layouts outside the closed R12 set.** R39's `custom` is the one declared
   exception. ADR 0003 (multiview) and any other non-IAB layout stay
   outside R12's closed enumeration; confirm no other exception is intended for
   this edition.
9. **OOS-6 and the single-decoder path that already exists.** §5.8.5.16.4
   standardises single-decoder picture-in-picture for VVC. OOS-6 excludes the
   technique on decoder-budget grounds. The exclusion can stand, but it should
   cite the clause; a reader who finds it in the base specification will
   otherwise conclude the exclusion was made without knowing it was there.
10. **Tracking-only decision entries.**
    `../context/05-dash-linear-interfaces.md` flags that the convention for a
    tracking-only VAST `<Ad>` with no media has no answer in the base
    specification. Re-checked: `VAST` appears 5 times, none normative, so there
    is nothing there to resolve it. Under R18.2 this is APS-internal; R30 covers
    the Player-visible half.
11. **R35.8 on a linear event that omits `@skipAfter` (G11).** The base gives
    the omitted attribute the value `PT0S` (skippable everywhere); R35.8 applies
    R35.1's non-dismissible default when the event "declares nothing". Decide
    whether an omitted-but-defaulted `@skipAfter` counts as the event carrying
    the base declaration. Recommendation: it does — that is what R1.5 and
    R35.8's own stated aim (same behaviour as a base Player) both give, and it
    confines R35.1's default to the non-linear families and to linear events a
    base Player would not see as skippable.
12. **Annex K `PlaybackRestrictions` in a linear resolution document (G11).**
    A List MPD may carry `ServiceDescription.PlaybackRestrictions@skipAfter` per
    ad Period, as §G.29.2 does. State how a Player of this specification treats
    it — honoured with its base meaning, as R35.8 does for the event attribute,
    or ignored in favour of this specification's slot-level field — and which
    wins when both are present.
13. **SRD as the value convention for R39 (G13).** Reuse SRD's parameter names,
    origin and integer domain (reference space 100 × 100) inside an SVTA
    construct, or define R39's own and record the departure under R8.2. Needs a
    decision, including whether fractional percentages are admissible, which SRD's
    integer domain would exclude.

## 6. Findings against `context/`

Five statements in `context/` do not survive the primary copy, or do not
survive it whole. They are recorded
here and not acted on, because `context/` is human-authored and this document is
generated.

1. **`context/08-dash-extension-rules.md`, DR-6** — *"Both share the placement
   constraint: they sit on AdaptationSet / Representation / Sub-Representation,
   so both inherit DR-5's MIME constraint unless hosted inside a
   foreign-namespace parent"*. The schema declares `SupplementalProperty` and
   `EssentialProperty` on `MPDtype`, `PeriodType`, `RepresentationBaseType`,
   `EventStreamType` and `EventType`, and `SupplementalProperty` on
   `AlternativeMPDEventType` (§5.10.2.3, §5.16.6). A descriptor on an `<Event>`
   or `<EventStream>` inherits no MIME constraint (G4). The constraint DR-6 omits
   is that `ImportedMpdType` accepts foreign-namespace attributes only, never
   child elements (§5.3.2.6.2).
2. **`context/08-dash-extension-rules.md`, DR-10** — the claim that
   `MPD@type="list"` *"is not a free choice of presentation type; it is rule 1
   of the ISO Base media file format List profile"*. §5.3.1.4 defines the value
   in the main body, with its own constraints, independently of §8.14; §8.14
   rule 1 states only the forward implication (G10).
3. **`context/05-dash-linear-interfaces.md`, message-flow step 4a and the
   reference XML** — *"the query parameters declared by the `UrlParamInfo`
   descriptor on the MPD (§I.4)"*, and the example element
   `<up:UrlParamInfo …>`. The edition declares no element named `UrlParamInfo`
   (0 occurrences). The request-parameter element is `RequestParam` of type
   `ExtendedUrlInfoType` (§I.3), extending `UrlQueryInfoType` (§I.2); §I.4
   supplies only the substitutable state vocabulary (G6).
4. **`context/05-dash-linear-interfaces.md`, message-flow step 4** — *"the
   Player picks a randomised instant between the ERT and the event's
   `presentationTime`"*. The base specification states only the interval:
   *"the precise timing of the resolution is not defined in this document"*
   (§5.16.2.2.1 step 2), and the attribute semantics say the MPD *"can be
   retrieved at any time between PRT – T and PRT"* (§5.16.5.2). Randomising
   is contemplated only informatively: *"If there is an expectation of a large
   number of concurrent clients with identical playhead position, it can be
   useful to randomize the actual resolution time"* (§5.16.2.2.6 NOTE 1). It is
   a server-load practice the base suggests, not what a Player does. The file
   is informative, but R36 builds on the same mechanism, so the distinction
   matters there (G12).
5. **`context/03-requirements.md`, R35.8** — *"R35.1's default applies only
   where neither the event nor the resolution document declares anything. This
   is R1.5 applied: a Player of this specification and a base Player treat the
   same linear event the same way."* The second sentence does not follow from
   the first for an event that omits `@skipAfter`: the base attribute has
   *"Default value is PT0S"* and *"Zero duration implies that skipping is allowed
   everywhere"* (§5.16.5.2), with `default="PT0S"` in the schema (§5.16.6). A
   base Player lets the viewer skip that event; a Player applying R35.1 does
   not (G11, open question 11).

## References

- [`../context/01-intro.md`](../context/01-intro.md) — document index
- [`../context/02-actors.md`](../context/02-actors.md) — Publisher / ADS / APS / Player
- [`../context/03-requirements.md`](../context/03-requirements.md) — R1–R39, DP-1..DP-3, OOS-1..OOS-9
- [`../context/04-use-cases.md`](../context/04-use-cases.md) — UC-01–UC-16, device classes D1–D5
- [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md) — linear SGAI baseline
- [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md) — SVTA Ads WG namespace, versioning, `@value` rule, naming consistency
- [`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md) — per-construct R1 audit
- [`../context/08-dash-extension-rules.md`](../context/08-dash-extension-rules.md) — DR-1..DR-10, the closed design space
- [`../context/99-glossary.md`](../context/99-glossary.md) — terminology
- The base specification, in the edition declared in
  [`../context/00-normative-base.md`](../context/00-normative-base.md). Clauses
  cited above: §4.2, §4.7, §5.2.1, §5.3.1.4, §5.3.2.2 (Table 4), §5.3.2.6,
  §5.3.7.2, §5.3.11, §5.8.4.8, §5.8.4.9, §5.8.5.2.2, §5.8.5.16, §5.9.1, §5.10
  (§5.10.1, §5.10.2.1, §5.10.2.2 Table 43, §5.10.2.3, §5.10.4.2, §5.10.4.5),
  §5.11.3, §5.16 (§5.16.1, §5.16.2.2.1–§5.16.2.2.6, Table 57, §5.16.3, §5.16.4,
  §5.16.5.2, Table 62, §5.16.6), §7.3.1, §8.1, §8.12, §8.14, §8.15, Annex A
  (§A.5, §A.14.2), Annex D (§D.4.6, §D.4.7), Annex F, Annex G (§G.29.2), Annex H
  (§H.1, §H.2, Table H.1), Annex I (§I.2.2.2, §I.2.3.3, §I.3, §I.4, Tables
  I.1, I.2, I.4, I.5), Annex K (§K.3, §K.3.8, §K.4.2.1, §K.4.2.8, §K.4.3.7.3,
  Tables K.9, K.10, K.18), Annex L (§L.1, §L.3.3, §L.3.4.2).

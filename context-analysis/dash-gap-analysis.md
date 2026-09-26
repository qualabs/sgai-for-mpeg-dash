[GROUNDED_BY=iso-23009-1-2026-pdf]

# DASH 6th edition gap analysis (SGAI for linear + non-linear ads)

This document compares the requirements in
[`../context/03-requirements.md`](../context/03-requirements.md) (R1–R40) and
the use cases in [`../context/04-use-cases.md`](../context/04-use-cases.md)
(UC-01–UC-17) against what the base specification provides, and states what the
SGAI specification must add or extend. It is an input to the spec build.

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY) when stating
requirements.

**Grounding.** Every load-bearing claim about the base specification was
verified against the primary copy of the edition declared in
[`../context/00-normative-base.md`](../context/00-normative-base.md), extracted
to text and searched. Each claim carries its clause number **and** a quoted
sentence. Negative claims ("the edition has no construct for X") rest on
searches over the whole extraction whose ability to find was shown on a term
known to be present; the counts are given where the negative is load-bearing
(§2, note on method). Claims not verified against the primary copy are tagged
`[inferred]`.

## 1. Scope

In scope:

- Every requirement R1–R40 against the capabilities of the base specification.
- UC-01–UC-17 as the behavioural check across device classes D1–D5.
- The constructs, carriers and rules the spec must add, and the base machinery
  it must weigh first (R8, R9, R1.5).

Out of scope:

- The APS-to-ADS and ADS-side contracts (R18, OOS-2).
- VAST field coverage beyond what R11.4 needs to be checked against; the
  mapping itself is illustrative (R11.3, R11.5).
- The out-of-scope items OOS-1..OOS-9 of `../context/03-requirements.md`. They
  are not raised as gaps.
- Choosing concrete syntax. Where the base offers more than one carrier, this
  document names the candidates; the build chooses and records why (R8).

## 2. Coverage matrix — R × DASH 6th capability

Cell values: **full** — the base answers the requirement and the spec adopts it
(R1.5); **partial** — the base answers part of it, or answers it for the linear
family only; **gap** — the base has no construct; **N/A** — the requirement
binds the spec's own text or actors the base does not model.

**Note on method (negative claims).** Whole-extraction, case-insensitive
searches: `overlay` 1 hit (Annex K, Table K.2, `MinimumLatency`: *"to
avoid inconsistencies with second screen applications, overlays, etc."*);
`squeeze` 0; `dismiss` 0; `banner` 0; `layout` as a whole word 0 (control:
`playout` as a whole word, 36); `pause` 8 (control for the pause claims — none
is a trigger; see G2). `click` 1, outside the clause text. The base
specification therefore has no vocabulary for non-linear ad forms, layouts,
dismissal or click activation.

### Contract foundations

| Req | DASH 6th capability | Cell | Gap |
|---|---|---|---|
| R1 | §5.2.1 foreign-namespace removal rule; §5.8.4.8 / §5.8.4.9 descriptors; §5.10 application event schemes; §5.16.2.2.6 failed-execution continuity (R1.4) | full | G10 (profile interaction) |
| R2 | The base models a client, not actors: *"DASH Client operation is not specified normatively in this document"* (§8.1 NOTE 1) | N/A | — |
| R11 | The base is VAST-agnostic; its one VAST mention is a note on the callback: *"HTTP GET (as opposed to HEAD) is used in alignment with IAB VAST"* (§5.10.4.5.1 NOTE 1) | N/A | — |
| R18 | Linear: the Player-visible interface is `@uri` (Table 63) and the alternative MPD. Non-linear: no resolution document exists | partial | G1 |
| R29 | Annex I.3 `RequestParam` (author-declared) and the I.4 state vocabulary (currently-playing state, no device capability) | gap | G6 |

### Opportunity declaration

| Req | DASH 6th capability | Cell | Gap |
|---|---|---|---|
| R4 | Linear: `@maxDuration` (Table 63), `@clip` (Table 62), APDmax / APDadj / APDA / RT (Table 57), zero cap not executed, absent cap infinite. Non-linear: none. Timebase conversion (R4.9): not defined | partial | G1, G9 |
| R31 | Events are timeline-scheduled only (§5.10.1); no pause trigger | gap | G2 |
| R12 | No ad-type or layout vocabulary (0 hits, above) | gap | G1 |
| R15 | Video: ISO-BMFF `@mimeType` per RFC 4337 (§7.3.1). Image / HTML: no media-axis carrier | partial | G4 |

### Selection and ordering

| Req | DASH 6th capability | Cell | Gap |
|---|---|---|---|
| R5 | Adaptation Set / Representation selection is client-side and informative (Annex A.2); no ordered form + layout options per candidate | gap | G3 |
| R7 | Linear: Periods of a List MPD play in sequence (§5.3.2.1 PeriodStart rule; §8.14 rule 4). Drop-before-play (R7.3) has no base counterpart: the base trims (APDA = min(APD, APDmax)) | partial | G3 |
| R30 | Linear: *"Alternative MPD is a List MPD, and merge process resulted in no available media"* is a failed execution (§5.16.2.2.6); E.c not incremented (NOTE 3). Non-linear: no document shape | partial | G8 |

### Presentation

| Req | DASH 6th capability | Cell | Gap |
|---|---|---|---|
| R3 | No device-class model; capability selection is informative (Annex A.2) | gap | G3 |
| R16 | No pause-bound lifecycle | gap | G2 |
| R32 | No behaviour on exhaustion during a pause | gap | G2, G8 |
| R34 | `@executeOnce` / E.c for timeline events (Table 63, Table 58); nothing for a pause trigger | partial | G2 |
| R35 | `@skipAfter` (Table 63) and `PlaybackRestrictions@skipAfter` (Table K.18), both default "skippable everywhere" | partial | G11 |
| R36 | `@earliestResolutionTimeOffset`, default 60 s (Table 63); no resolution-freshness declaration | partial | G12 |
| R37 | The base leaves pause mechanism to the client (Annex A.5, informative) | N/A | G9 (live limit) |
| R38 | No slot layout declaration and no forwarding channel | gap | G6 |
| R39 | Annex H SRD coordinate model, confined to Adaptation Set / Sub-Representation | gap | G13 |
| R19 | Replacement couples the main playhead to the alternative's speed (§5.16.4); no rule that the ad follows the primary content | partial | G9 |
| R21 | No pause surface | gap | G1, G2 |
| R25 | Timeshift buffer bounds where a live presentation can resume (Table 62 NOTE 1); no freeze rule | partial | G9 |
| R26 | No composition construct | gap | G1 |
| R27 | No composition construct | gap | G1 |

### Interaction and composition rules

| Req | DASH 6th capability | Cell | Gap |
|---|---|---|---|
| R14 | Linear sequencing only (List MPD Periods) | gap | G1, G3 |
| R17 | A pause of an alternative presentation is contemplated (Table 62 NOTE 2; Annex A.14.2); no cross-family priority | gap | G2, G14 |
| R20 | Linear: execution queue by PRT and fall-through on failure (§5.16.2.2.2, §5.16.2.2.5). Non-linear: none. Tie-break: none | partial | G7 |
| R22 | No concurrency model to conflict with; the bound is the spec's own | gap | G1 |
| R40 | No construct says what an event is or how another relates to it (Tables 59, 61, 62, 63) | gap | G14 |

### Tracking

| Req | DASH 6th capability | Cell | Gap |
|---|---|---|---|
| R6 | Callback scheme `urn:mpeg:dash:event:callback:2015` (§5.10.4.5); `Event@id` scope (Table 44). No time anchor for an `EventStream` outside a Period (R6.6); lax processing of foreign content (R6.7) | partial | G15 |
| R13 | Same callback carrier; timings relative to Period start (Table 44) | partial | G15 |
| R23 | §5.2.1 permits foreign-namespace elements; no metadata elements defined | gap | G5 |
| R24 | The constraint is confirmed (§5.3.2.6, §7.3.1, §8.12.4.3, §8.15.2); the carrier is not provided | partial | G4 |
| R33 | `PlayList` metric (Annex D.4.6, Table D.5); `Metrics` trigger (§5.9.1) | full | — |
| R28 | No click carrier; events are timed (§5.10.1) | gap | G5 |

### Governance

| Req | DASH 6th capability | Cell | Gap |
|---|---|---|---|
| R8 | — | N/A | §4 lists the reuse decisions R8 must record |
| R9 | — | N/A | §4 |
| R10 | The base defines no layout engine; SRD is a spatial-relationship descriptor for media, not placement of overlays | N/A | G13 |

## 3. Gaps detail

### G1 — No non-linear opportunity, resolution document or composition model (R4 on non-linear slots, R12, R14, R18, R21, R22, R26, R27)

**What the base offers.** One ad tool, and it is a switch. *"An alternative
Media Presentation is a presentation that replaces the main Media Presentation
at a certain point on the media timeline for a duration of time"* (§5.16.1).
During it, *"there are two instances of DASH access engine, main and the
alternative"* and *"the alternative access engine outputs media to the media
engine, while the main client will be paused or be in a listen mode"* (§4.2).
Nothing composites two outputs. The ad-form vocabulary is absent (§2, note on
method).

**What must be added.**

- **Opportunity windows for the overlay and pause families.** An event scheme
  per family under `urn:svta:dash:<construct>:<year>`
  (`../context/06-naming-and-namespaces.md`). The base event model gives the
  window span for free: `Event@presentationTime` and `Event@duration`, where
  the duration is *"the presentation duration of the Event"* and *"The
  interpretation of the value of this attribute is defined by the scheme owner"*
  (Table 44). The window's own declarations (URI, cap, allowed layouts, custom
  region, relation of R40, once-per-session of R34, early-resolution offset of
  R36) need a home on the `Event`. The base already models this shape:
  `InsertPresentation` / `ReplacePresentation` are child elements of `Event`,
  and `EventType` admits *"XML content, possibly using elements external to the
  MPD namespace"* (Table 44) through
  `<xs:any namespace="##other" processContents="lax" .../>` and
  `<xs:anyAttribute namespace="##other" processContents="lax"/>` (§5.10.2.3).
- **A non-linear resolution document.** The linear path returns an MPD; the
  non-linear one has no base shape. It must carry candidates, each with ordered
  presentation options (G3), non-AV asset URLs (G4), tracking (G15), metadata
  and ClickThrough (G5), dismissal (G11), freshness (G12), and — for pause —
  the exhaustion behaviour of R32. DR-10 records why it declares no existing
  profile; see G10 and §5.2 on the reason given.
- **The layout vocabulary of R12.2** as a closed token set, with
  `@allowedLayouts` on the window (the space-separated list form of
  `../context/06-naming-and-namespaces.md`). The base has nothing to reuse.
- **Composition rules**: overlay over playing content, squeezeback that
  transforms the primary content (R12's geometry table, R27.2), double-box with
  background (R26), pause surfaces (R21). All are Player obligations of this
  spec; the base's client model has no hook for them, which is consistent with
  DR-8.
- **Sequencing inside a non-linear slot (R14)** and the **single-active-form
  bound (R22)**. The linear analogue is the List MPD's sequential Periods
  (G3); for non-linear candidates the order is the resolution document's
  document order.

**The cap on non-linear slots (R4.1, R4.2, R4.9, R4.10).** The linear cap is
the base's: `@maxDuration` *"specifies maximum duration of the Alternative
Presentation, expressed in units of EventStream@timescale"*, *"If absent, the
value is assumed to be infinity"*, and *"If the value of @maxDuration is zero,
the event is not executed"* (Table 63). For non-linear windows the spec must
carry a required cap of its own (R4.1, R4.10 — the base's "absent means
infinity" is deliberately not adopted there, ADR 0015). R8.1 requires the build
to say why `@maxDuration` itself is not reused on the window; the reason is the
default, which R4.10 cannot inherit. R4.9's conversion is new: the base states
the cap in timescale units and `Period@duration` as `xs:duration`, and defines
no rule converting one to the other or rounding [inferred — searched §5.16 and
Table 4 for a conversion rule; none found].

### G2 — No pause trigger in the edition (R16, R21, R31, R32, R34)

**What the base offers.** Events are timeline-scheduled: *"Events are timed,
i.e. each event starts at a specific media presentation time and may have a
duration"* (§5.10.1). Alternative MPD events execute *"every time the playhead
enters the active interval"* (§5.16.2.2.1). The eight `pause` hits are: the
client model, Table 62 NOTE 2 (*"The above can happen in case a user pauses the
alternative Media Presentation"*), Annex A.5 (*"The client may pause or stop a
Media Presentation"*, informative), Annex A.14.2 (*"S = 0 is pause"*,
informative), and Table D.5 (`Resume` — *"Resume from pause"*). None triggers
anything.

**What must be added.** A pause-trigger window whose span bounds where a pause
begins (R31.1), a resolution requested on the pause and not on the playhead,
dismissal on resume within one frame (R16.1), and the exhaustion declaration of
R32 (`repeat` / `request-again` / `stop`, default `stop`) in the pause
resolution document.

**What can be reused.**

- **R34 (once per session)** is the counterpart of `@executeOnce`: *"If true,
  if some of the media during the active interval of this event is played more
  than once, the event is executed only the first time this media time is
  traversed"* (Table 63). Its counter is the base's: E.c is *"number of times
  alternative MPD playback successfully started"* (Table 58), and *"When the
  alternative media presentation triggered by an event successfully starts
  playing, the corresponding counter E.c is incremented"* (§5.16.2.2.6). R34.3
  ("consumed when a pause ad begins rendering") is that rule restated for the
  pause trigger. The build weighs reusing the attribute name with pause-trigger
  semantics against a new name; `../context/06-naming-and-namespaces.md` asks
  for the base name when the concept is the same, and R34.4 says it is.
- **R33** needs nothing new (see §2, full).

### G3 — No ordered presentation options per candidate (R3, R5, R7, R14)

**What the base offers.** Capability-based selection of media exists only as
informative client behaviour: the client *"selects a collection of Adaptation
Sets suitable for its environment"* and a Representation *"taking into account
client decoding and rendering capabilities"* (Annex A.2). Ordering exists for
linear pods: *"PeriodStart reflects the actual time that should elapse after
playing the media of all prior Periods"* (§5.3.2.1), and *"List MPDs may
contain one or more Linked Periods (see 5.3.2.6), however it may also contain
regular Periods"* (§8.14 rule 4).

**Gap.** There is no construct for a candidate carrying an ordered list of
(form + layout) options whose document order is the preference order, and no
device-class model (R3.1). The spec must define the option list in the
non-linear resolution document (R5.1, R5.5), the Player walk (R5.2, R5.6, R5.7)
and the device-class enumeration D1–D5 with per-UC behaviour (R3.1; already in
`../context/04-use-cases.md`).

**Linear candidates (R5 on linear slots).** A List MPD Period is one ad; the
options of that ad have no base carrier beyond alternative Representations of
the same media type. A video-plus-image fallback inside a linear candidate
(UC-01 "Ad response") cannot ride the media axis (G4). The build decides
whether linear candidates carry options at all, or whether R5 on linear slots
reduces to the base's Representation selection; `../context/04-use-cases.md`
UC-01 / UC-02 describe options, so the choice must be recorded under R8.2.

**R7.3 (drop before play).** The base trims rather than drops:
*"For insertion events, APDA = min(APD, APDmax)"* and the presentation *"shall
be terminated at the end of this duration"* (Tables 57, 63). Dropping a Period
of a List MPD before play is a Player-side choice of this spec, permitted by
R7.3, with no base counterpart.

### G4 — Non-AV creatives have no home on the media axis (R15, R24)

**Confirmed constraint.** *"MPDs referenced in the ImportedMPD element shall be
restricted to the constraints of a single period profile as defined in 8.15"*
(§5.3.2.6.1); SPS requires *"The rules for the MPD as defined in subclause 7.3
shall apply"* (§8.15.2); §7.3.1: *"The @mimeType attribute of each
Representation shall be provided according to IETF RFC 4337."* On the List MPD
itself, the CMAF profile it extends (§8.14) requires *"The @mimeType shall be
set to "<contentType>/mp4""* (§8.12.4.3). DR-1 and DR-5 hold.

**Gap.** Image and HTML creatives need a carrier from DR-6 (R24.1): (a)
foreign-namespace element, (b) event payload, (c1) `SupplementalProperty`, (c2)
`EssentialProperty`. The legacy cost differs as DR-9 states: *"If the scheme or
the value for this descriptor is not recognized, the DASH Client is expected to
ignore the parent element that contains the descriptor"* (§5.8.4.8 NOTE 1)
against *"... is expected to ignore the descriptor"* (§5.8.4.9 NOTE).

**Placement is wider than DR-6 states** (see §5.2). The descriptors are not
confined to AdaptationSet / Representation: `SupplementalProperty` is a child of
`PeriodType`, `EventStreamType`, `EventType` and `AlternativeMPDEventType`, and
`EssentialProperty` of `EventStreamType` and `EventType` (§5.3.2.3, §5.10.2.3,
§5.16.6 XML syntax). A descriptor on an `Event` or `EventStream` does not
inherit DR-5's MIME constraint. The build weighs these placements when it
classifies each carrier under checklist item 8.

### G5 — No metadata carrier and no user-activated event (R23, R28)

**What the base offers.** A place: §5.2.1 lets the MPD carry *"XML attributes
or elements in the other namespaces"*, removable without breaking validity. No
elements for `AdSystem`, `AdTitle`, ClickThrough or click-tracking exist.

**No user-activation trigger.** DASH events are timed (§5.10.1), and the
callback *"is expected by a DASH Client to issue an HTTP GET request to a given
URL and ignore the HTTP response"* when dispatched (§5.10.4.5.1) — on the
timeline. The one user-driven mechanism, Annex L, has the application choose
the next Period: *"The application makes decisions upon which the user selects
which Period to consume after the end of the currently active period"* and
*"The logic upon which the decisions are made is application-specific"*
(Annex L.2). It carries no URL fired on activation.

**What must be added.** The R23 elements in `urn:svta:dash:sgai:<year>`, both
optional to emit and to read (R23.1), and the R28 carrier holding the
ClickThrough URL with its click-tracking URLs, read by every Player of this spec
and fired on activation (R28.2). Neither can reuse the callback scheme (no
presentation time for a click).

### G6 — No channel for Player-declared capability or forwarded slot declarations (R29, R38, R39.3)

**What the base offers.** Annex I.3 lets the author declare parameters for the
alternative MPD request: parameters *"may be selectively embedded in requests
such as but not limited to MPD, MPD Patch, Alternative MPD, XLink and callback
requests"* (I.3.1), selected by `@includeInRequests` with request type `altmpd`
— *"all requests for MPDs representing the alternative Media Presentation"*
(Table I.4). Values come from the I.4 vocabulary, which expresses current
playback state: `video` is *"comma-separated values of Representation@codecs
and Representation@bandwidth attributes of the currently playing video
Representation"*, plus `audio`, `lang`, `encryption`, `cmcd#[key]`,
`execution-delta`, `expected-duration`, `execution-count`, `previous-state`
(Table I.5).

**Gap.**

- **R29.** The I.4 vocabulary has no device-capability axis — decoder count,
  image / HTML surface over video — so it cannot tell D1–D5 apart (R29.6).
  R29 also places the reserved names outside the author-declared template
  mechanism, because which parameters travel is the Player's decision. The
  spec defines the reserved names, the vendor-prefix rule (R29.4) and the
  "absent = undetermined" semantics (R29.7).
- **R38 / R39.3.** No base construct forwards a slot declaration on the
  request. The spec defines how `@allowedLayouts` and the custom region travel
  (R38.3), as reserved parameters.

**Reuse to weigh.** Table I.4 admits a request type the base does not define:
*"a URN or tag URI, where the request type semantics is understood by the
client and specified by the URN / tag URI owner"*. A request type for the
non-linear resolution request would let the Publisher's own `RequestParam`
templates (the slot-constraint query parameters of `../context/02-actors.md`)
reach that request exactly as `altmpd` reaches the linear one. This complements
R29; it does not replace it.

### G7 — The fallback chain is inherited whole for linear and has no anchor for the other two families (R20)

**Linear: full.** *"There is an execution queue QE, which is a priority queue
of references to a subset of events in table T, ordered by the presentation
time PRT"* (§5.16.2.2.2); on failure, *"steps a-c above are repeated for next
events in QE"*, and *"If no event can be successfully executed, the playback
continues uninterrupted"* (§5.16.2.2.5). The four failure shapes of R20.1 map to
§5.16.2.2.6: *"Alternative MPD is unavailable or invalid"* and *"Alternative
MPD is a List MPD, and merge process resulted in no available media"*.

**Non-linear: gap.** The queue is defined for Alternative MPD events only; the
spec extends it to overlay and pause-trigger windows (R20.1, R20.3).

**Tie-break: gap.** The queue orders by PRT only. The base does order events in
a stream — *"Events in Event Streams shall be ordered such that their
presentation time is non-decreasing"* (Table 43) and dispatch is *"in the order
they appear in the EventStream element"* (§5.10.2.1) — so the document-position
tie-break of R20.3 is available and well-defined, but it is the spec's rule for
execution, not the base's.

**R20.2.** *"A Period shall contain at most one EventStream element with the
same value of the @schemeIdUri attribute and the value of the @value
attribute"* (§5.10.2.1). The rule is on the scheme-and-value pair. It gives
R20.2 its force only because SGAI streams carry no `@value`
(`../context/06-naming-and-namespaces.md`); see §5.2.

**R20.4 and R20.5** (wrong family; each window binds its own declarations) are
new Player rules with no base counterpart.

### G8 — The empty resolution has its semantics from the base and needs its shape from the spec (R30, R32.2, R36.6)

**Linear: full.** The base condition and outcome are quoted in G7; *"The counter
E.c has not been incremented due to the failure, consequently if E.c = 0 the
event can still be executed in the future even if the value of @executeOnce is
"true""* (§5.16.2.2.6 NOTE 3) gives R30.2.

**Linear shape, one point to settle.** "No candidates" in a List MPD is a List
MPD whose merge yields no media. A List MPD with zero Periods is a different
document; whether it is schema-valid under Annex B was not checked
[inferred]. The spec must say which shape the APS emits (R30.1: "carries every
element the syntax requires").

**Non-linear: gap.** The spec defines the well-formed, candidate-free
non-linear document, and applies it for `request-again` (R32.2) and failed
re-resolution (R36.6).

### G9 — Speed, timeline accounting and the live-pause limit (R4.11, R17.5, R19, R25, R37)

**Speed (R19).** The base couples the other way round: during a replacement
*"its playhead continues moving at the same speed as the playhead of the
alternative presentation"* (§5.16.4), and Annex A.14.2 (informative) has the
alternative client send `adjust speed(S)` so that *"media time elapses at the
same speed in both clients"*. The base does not require an ad to follow the
primary content's speed; on catch-up after a replacement it states *"this
document does not specify or recommend any particular client behaviour in this
case"* (§5.16.2.2.1, step 5 NOTE). R19 is the spec's rule, and it is consistent
with the base coupling (both playheads move together).

**Which timeline accrues (R4.11).** For insertion, *"RT is defined as PRTA"*
(§5.16.2.2.1, step 5) — the main timeline does not advance; for replacement the
main media time *"progresses at the same speed as the currently playing
alternative Media Presentation"* (§5.16.1). A non-linear window on the primary
timeline declared on top of a linear break (R40.5) therefore sees its span stop
during an insertion and keep moving during a replacement. R4.11 says the cap is
computed "on the presentation timeline" without naming which; see open question
Q3.

**Pause during a linear ad (R17.5).** The base contemplates it (Table 62 NOTE
2, above) and keeps both clients' media time together (A.14.2); suspending and
resuming the linear ad is within that model. Presenting a pause ad over it is
the spec's.

**Live pause limit (R25, R37.2).** A live presentation can only resume inside
the timeshift buffer: *"If RT is in the past, the playback shall start from the
oldest available media segment (the edge of the timeshift buffer)"* (Table 62
NOTE 1), with TSBS *"The smallest (earliest) media time for which Media
Segments are available"* (Table 57). A pause longer than the timeshift buffer
cannot resume at the frozen position, which R37.2 says is then not a pause. The
spec must state what R25's freeze guarantees when the paused position leaves
the buffer (Q4).

### G10 — Profiles and schema placement bear on every construct (R1.2; DR-2, DR-4, DR-10)

**Profile conformance strips the extension namespace.** For profile
conformance the MPD is first reduced, and step 4 removes *"All elements or
attributes that are either (i) in this document and explicitly excluded by
ProfA, or (ii) in an extension namespace and not explicitly included by
ProfA"* (§8.1). A document declaring a profile and carrying SGAI constructs is
checked for that profile with the SGAI constructs removed. A profile cannot
certify them; only an Interoperability Point that includes them could, and
*"The owner of the URI is responsible to provide sufficient semantics on the
restrictions and permission of this interoperability point"* (§8.1). This
supports DR-4's cost argument.

**The Advanced Linear profile restricts events.** The profile announces
*"Support for a restricted set of DASH events"* (§8.13.1), and its Period
constraint reads *"EventStream elements may indicate Alternative MPD (5.16) and
Callback (5.10.4.5) event schemes"* (§8.13.2.2), next to *"Periods and
Representations which do not conform to the constraints in this subclause may
not be presented"* (§8.13.2.1). Whether an `EventStream` with an SGAI scheme in
an Advanced-Linear MPD is non-conforming, and so exposes the Period to "may not
be presented", is not settled by the text: "may indicate" is permissive, and
the scheme URI is a DASH-namespace attribute value, not an extension-namespace
element that step 4 would remove. This matters for R1 because the
`../context/05-dash-linear-interfaces.md` reference MPD declares
`urn:mpeg:dash:profile:advanced-linear:2025`. Q1.

**Schema placement.** The foreign-namespace hooks are not uniform:
`EventType`, `PeriodType`, `DescriptorType` and `AlternativeMPDEventType` admit
both foreign elements and foreign attributes; `EventStreamType` admits foreign
elements (`<xs:any namespace="##other" .../>`) and no `xs:anyAttribute`
(§5.10.2.3); `ImportedMpdType` is simple content with `xs:anyAttribute` only
(§5.3.2.6.2). A foreign attribute on `EventStream` is therefore not
schema-valid, and a foreign child of `ImportedMPD` is not possible. This bears
on R40's carrier (G14) and on DR-2's "every container" (§5.2).

**`MPD@type="list"`.** §5.3.1.4 defines the type independently of the profile:
*"For Media Presentations with MPD@type set to "list" the constraints of a
static Media Presentation shall apply"* and *"MPDs of @type="list" may contain
Linked Periods."* §8.14 rule 1 requires List-profile MPDs to declare the type;
the converse is not stated. DR-10's reason does not hold as written (§5.2); its
conclusion (declare no profile for the non-linear document) is unaffected.

### G11 — Viewer dismissal: the base skip control exists twice, with the opposite default (R35)

**Base.** `@skipAfter` *"describes an offset in time (in fractional seconds)
from the beginning of the alternative presentation till the moment the rest of
that presentation may be skipped by the application in response to a user
action"*, and *"Zero duration implies that skipping is allowed everywhere"*,
default `PT0S` (Table 63). The service description repeats it: *"The default
value of 0 implies that skipping is allowed everywhere"* (Table K.9), carried as
`PlaybackRestrictions@skipAfter` (Table K.18), and an event reaches a service
description through `@serviceDescriptionId`, which *"specifies the value of the
@id attribute of a ServiceDescription element applicable to this Event and to
any presentation initiated as a result of executing this Event"* (Table 63).

**Gap.** R35.1 needs "undeclared = not dismissible", the inverse default.
`../context/06-naming-and-namespaces.md` and ADR 0017 already decide on an SVTA
field in the resolution document; R8.2 is satisfied by that record.

**R35.8 against the base.** The base's `@skipAfter` is a permission to the
application (*"may be skipped"*), not an obligation to offer a skip, so treating
an unwritten `@skipAfter` as non-dismissible stays within base semantics.
R35.8 names "the base specification's own skip declaration" in the singular;
two exist (event attribute and service-description restriction). Q6.

### G12 — Early resolution is the base mechanism; resolution freshness has no in-document anchor (R36)

**Reuse: full.** `@earliestResolutionTimeOffset` *"specifies the time interval
(in units of EventStream@timescale) prior to the Event@presentationTime during
which the MPD described in the @uri attribute may be requested. The default is
60 seconds in units of timescale"* (Table 63). R36.1–R36.3 adopt it (ADR 0018).
Note that `ImportedMPD@earliestResolutionTimeOffset` is a different unit:
*"specifies the offset (in seconds) from the PeriodStart"*, `xs:double`,
default 60 (Table 5, §5.3.2.6.2).

**Freshness: gap.** The base resolves at execution — *"The alternative MPD is
resolved at each execution of the Event"* — and leaves reuse to HTTP: *"The
underlying HTTP client may cache HTTP responses in accordance with IETF RFC
9111"* (§5.16.2.2.6 NOTE 5). R36.4 needs an in-document declaration.

**Reuse to weigh.** The base already rejects a stale imported MPD: *"In case the
MPD is retrieved, is syntactically valid, but the @availabilityEndTime
attribute is present and its value is smaller than the current time NOW, then
the resolution fails"* (§5.3.2.6.3 step 1c). `MPD@availabilityEndTime` is an
absolute `xs:dateTime`, *"the latest Segment availability end time for any
Segment in the Media Presentation"* (Table 3), not a keep-for duration, and its
subject is segment availability rather than decision freshness. The build
weighs it against a new relative field under R8.1.

### G13 — The `custom` rectangle: a coordinate model exists and is confined to media elements (R39)

**Annex H SRD** has R39's geometry: a coordinate system with *"an arbitrary
origin (0; 0); the x-axis is oriented from left to right and the y-axis from top
to bottom"*, a reference space *"whose top-left corner is at the origin of the
coordinate system"*, sized by `total_width` / `total_height` *"expressed in
arbitrary units"* (H.2.2), and the containment rule *"the sum of object_x and
object_width is smaller or equal to total_width"* (Table H.1). With totals of
100 it is R39.2's percent rectangle and R39.4's containment test.

**Not reusable as a carrier.** *"SRD information shall be contained
exclusively in these two MPD elements (AdaptationSet and SubRepresentation)"*
(H.1). The custom region sits on a window and the rectangle on an option.

**Decision for the build.** Reuse SRD's parameter names, order and value
convention in an SVTA construct, or define new ones and record under R8.2 why
SRD was not reused. SRD's `@value` is *"a comma-separated list of values for
SRD parameters"* (H.2.1); the project's list convention is space-separated. The
forwarding of the region (R39.3) is G6.

### G14 — The window's relation to linear events has no base construct and depends on base timing (R40, R17.5, R22 across families)

**No construct to reuse.** The alternative-MPD events carry `@uri`,
`@earliestResolutionTimeOffset`, `@serviceDescriptionId`, `@maxDuration`,
`@executeOnce`, `@noJump`, `@skipAfter` (Table 63) and, for replacement,
`@returnOffset`, `@clip`, `@startWithOffset` (Table 62); `EventStream@value` is
*"currently not required"* (Table 59) and *"currently not used"* (Table 61).
None says what an event is. The base describes the tool as serving *"pre-roll
and mid-roll advertisement, as well as blackouts"* (§5.16.1). This confirms
R40's premise.

**Carrier.** The three alternatives of `../context/06-naming-and-namespaces.md`
meet the schema facts of G10: an attribute on the window is schema-valid if the
window is an `Event` (foreign attributes allowed) or an SVTA element; a
stream-level attribute is not (no `xs:anyAttribute` on `EventStreamType`); the
`@value` route collides with R20.2 as the naming file says.

**Supersede depends on the base's late-execution rules (R40.3).** A superseded
event executed "after all" is a delayed execution. The base allows it only while
the event is active — *"PRT ≤ PRTA ≤ EAP"* (Table 57) and *"If the event is no
longer active, it is ignored"* (§5.16.2.2.1, step 4) — and, for replacement with
`@clip` true, the presentation *"shall terminate at the latest at time PRT +
APDmax"* (Table 62). Resolution after PRT is allowed and discouraged:
*"Attempting resolution at time PRTA is an acceptable practice, however this
can result in a non-smooth transition from main to alternative presentation and
is hence discouraged"* (§5.16.2.2.6 NOTE 2). Consequences the spec must state:
the fallback break exists only if the window's failure is known before the
linear event's EAP; a replacement break executed late is shortened; and the
Player may need to resolve the break's `@uri` speculatively (inside its ERT
window) while the window resolves, or accept a late resolution. Q2.

**On top (R40.5)** composites over an alternative presentation, which the base
outputs through one access engine (§4.2); the composition is the spec's
(G1), and the timeline question is G9 / Q3.

### G15 — Tracking on non-linear candidates has no base time anchor or validation (R6.5–R6.7, R13)

**Linear: full.** Callback events in the ad MPD (§5.10.4.5; Table 47:
`EventStream@value` `1`, the Event value an HTTP-URL). `Event@id` scope:
*"The scope of the @id for each Event is within the same @schemeIdURI and
@value pair over the duration of the current media presentation"* (Table 44) —
R6.5 adopts it for List MPDs. Trimming ends the presentation: *"If the
Alternative Presentation initiated by this event has a longer duration than
specified in this element, it shall be terminated at the end of this duration"*
(Table 63), and *"Events shall terminate at the end of a Period"* (§5.10.2.1),
which carries R13.3 for linear.

**Non-linear: gap.** An MPD event's time is *"relative to the start of the
Period, taking into account the @presentationTimeOffset of the Event Stream"*
(Table 44). A callback `EventStream` hosted inside a candidate (foreign content)
has no Period, so the spec defines its anchor (R6.6: the candidate's own
presentation) and the per-candidate de-duplication scope (R6.5).

**Validation (R6.7).** Foreign content is declared
`processContents="lax"` (§5.10.2.3 and every hook above): a validator without
the SVTA schema skips it. The spec must publish the SVTA schema and state that
validation of a resolution document includes the tracking subtree against the
base `EventStreamType`.

## 4. Reuse opportunities

Per R9 and R1.5, each entry is a base construct the build adopts or must weigh
before minting a new one. "Adopt" means the context already decides it.

| Need | Base construct | Status | Clause |
|---|---|---|---|
| Linear slots, cap, clip, resumption | `InsertPresentation`, `ReplacePresentation`, `@maxDuration`, `@clip`, RT | adopt | §5.16.3–§5.16.5; Tables 57, 62, 63 |
| Linear fallback chain and ordering | QE priority queue, fall-through | adopt | §5.16.2.2.2, §5.16.2.2.5 |
| Empty resolution = failed execution | List MPD merge with no media; E.c not incremented | adopt | §5.16.2.2.6, NOTE 3 |
| Window span | `Event@presentationTime` + `Event@duration` | adopt | Table 44 |
| Window declarations | Child element in the SVTA namespace inside `Event`, as `InsertPresentation` is | weigh | Table 44; §5.10.2.3 |
| Early resolution (R36) | `@earliestResolutionTimeOffset`, default 60 s | adopt (ADR 0018) | Table 63 |
| Resolution freshness (R36.4) | `MPD@availabilityEndTime` stale-import rule | weigh | §5.3.2.6.3 1c; Table 3 |
| Once per session (R34) | `@executeOnce`, E.c | weigh name; adopt counter rule | Tables 58, 63; §5.16.2.2.6 |
| Dismissal (R35) | `@skipAfter` | declined, recorded (ADR 0017) | Table 63; Table K.18 |
| Tracking (R6, R13) | Callback scheme | adopt | §5.10.4.5; Table 47 |
| Pause-ad measurement (R33) | `PlayList` metric, `Metrics` trigger | adopt | Annex D.4.6; §5.9.1 |
| Forwarding Publisher params to the non-linear request | `RequestParam` with a URN request type | weigh | Annex I.3.6, Table I.4 |
| Device capability parameters (R29) | I.4 state vocabulary | not sufficient (no capability axis) | Table I.5 |
| Custom rectangle (R39) | SRD parameters | weigh as value convention | Annex H |
| Non-AV asset carriers (R24) | §5.2.1 content; §5.10 events; §5.8.4.8 / §5.8.4.9 descriptors, including on `Event` / `EventStream` | weigh per carrier (DR-6, DR-9) | §5.3.2, §5.10.2.3 |
| Metadata / ClickThrough (R23, R28) | §5.2.1 foreign namespace | adopt as placement; elements are new | §5.2.1 |

## 5. Open questions

### 5.1 Questions for the working group or the build

- **Q1 — Advanced Linear and SGAI event schemes.** Is an `EventStream` with an
  SGAI scheme in an MPD declaring `urn:mpeg:dash:profile:advanced-linear:2025`
  conforming, given §8.13.1's "restricted set of DASH events" and §8.13.2.1's
  "may not be presented"? If not, the build must place the windows where the
  profile's reduction does not reach, or state that SGAI windows are not
  available under that profile. Needs MPEG-DASH input. (G10)
- **Q2 — Supersede timing.** When may the Player of this spec decide the window
  "presents no ad", relative to the superseded event's PRT and EAP, and does it
  resolve the break speculatively? The base allows execution only up to EAP and
  shortens a clipped replacement. (G14)
- **Q3 — Which timeline an on-top window runs on.** During an insertion the
  primary timeline stops (RT = PRTA); during a replacement it keeps moving.
  Does an on-top window's span and cap (R4.11) accrue on the primary timeline,
  the alternative's, or wall-clock? (G9)
- **Q4 — Live pause beyond the timeshift buffer.** What R25 guarantees when the
  frozen position leaves the buffer, and whether R37.2 then declares the event
  "not a pause". (G9)
- **Q5 — Linear candidates with options.** Do linear candidates carry R5
  presentation options (UC-01 / UC-02 say they may), and if so where, given the
  media axis is closed to image / HTML? (G3, G4)
- **Q6 — Which base skip declaration R35.8 honours.** `@skipAfter` on the
  event, `PlaybackRestrictions@skipAfter` through `@serviceDescriptionId`, or
  both, and which wins if both are written. (G11)
- **Q7 — Empty List MPD shape.** Is a List MPD with zero Periods schema-valid
  and the intended R30.1 shape, or must the APS emit Periods whose merge yields
  no media? (G8)
- **Q8 — Pause windows inside an alternative presentation (R40.6).** R33.4
  requires the `Metrics` element, which sits at MPD level (`MPDtype`, §5.3.1.3
  syntax); SPS forbids `MPD.Metrics` (§8.15.2 g). A pause window declared in an
  SPS-constrained presentation cannot satisfy R33.4 there. Which MPD's
  `Metrics` covers it? [inferred — whether an alternative presentation reached
  by `@uri` is SPS-bound was not established; only `ImportedMPD` targets are.]

### 5.2 Discrepancies between `context/` and the primary copy

Out of this step's scope to fix; recorded so the build does not propagate them.

1. **`05-dash-linear-interfaces.md`, reference main MPD: `InsertPresentation` in
   a dynamic MPD.** The example declares `type="dynamic"` and an insertion
   event; §5.16.3: *"The event shall not appear if the MPD type is
   "dynamic"."* The same file's prose states the restriction correctly.
2. **`05-dash-linear-interfaces.md`, URL parameters.** The example puts
   `<up:UrlParamInfo .../>` inside an `EssentialProperty` with scheme
   `urn:mpeg:dash:urlparam:2025` and attributes it to "§I.4". For that scheme
   *"An MPD.EssentialProperty element with the attribute @schemeIdUri having
   value of "urn:mpeg:dash:urlparam:2025" shall be present and have no
   content"* and *"The scheme uses a single element, RequestParam"* (I.3.1);
   I.4 is the state vocabulary, not the descriptor. Under the Advanced Linear
   profile the example declares, *"It shall be used in case parameters defined
   in I.4. are used"* (§8.13.2.7), referring to `RequestParam`.
3. **`08-dash-extension-rules.md` DR-6: descriptor placement.** "they sit on
   AdaptationSet / Representation / Sub-Representation" is narrower than the
   schema: descriptors are also children of `Period`, `EventStream`, `Event`
   and `AlternativeMPDEventType` (G4).
4. **`08-dash-extension-rules.md` DR-10: reason.** "That value is not a free
   choice of presentation type; it is rule 1 of the ISO Base media file format
   List profile, and the rules travel together" — §5.3.1.4 defines `list`
   independently of §8.14 (G10). The conclusion stands; the reason does not.
5. **`08-dash-extension-rules.md` DR-2: "every container".** `EventStreamType`
   has no `xs:anyAttribute`, and `ImportedMpdType` accepts foreign attributes
   only (G10).
6. **`03-requirements.md` R20.2: scope of the one-stream rule.** "DASH admits at
   most one `EventStream` per `Period` for a given scheme" — §5.10.2.1 states it
   per scheme-and-`@value` pair. Correct for SGAI streams only because they
   carry no `@value` (G7).

## References

- The base specification: the edition and primary copy declared in
  [`../context/00-normative-base.md`](../context/00-normative-base.md).
  Clauses cited: §4.2, §5.2.1, §5.3.1.4, §5.3.2.1, §5.3.2.2 (Table 4),
  §5.3.2.6 (Table 5), §5.8.4.8, §5.8.4.9, §5.9.1, §5.10.1, §5.10.2 (Tables 43,
  44), §5.10.4.5 (Table 47), §5.16 (Tables 57–63), §7.3.1, §8.1, §8.12.4.3,
  §8.13, §8.14, §8.15, Annex A.2 / A.5 / A.14.2 (informative), Annex D.4.6
  (Table D.5), Annex H, Annex I.3 / I.4 (Tables I.3–I.5), Annex K.3.8 (Tables
  K.9, K.18), Annex L.2.
- [`../context/03-requirements.md`](../context/03-requirements.md),
  [`../context/04-use-cases.md`](../context/04-use-cases.md),
  [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md),
  [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md),
  [`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md),
  [`../context/08-dash-extension-rules.md`](../context/08-dash-extension-rules.md).

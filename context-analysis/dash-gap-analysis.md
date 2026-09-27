[GROUNDED_BY=iso-23009-1-2026-pdf]

# DASH 6th edition gap analysis (SGAI for linear + non-linear ads)

This document compares the requirements in
[`../context/03-requirements.md`](../context/03-requirements.md) (R1–R40) against
what the base specification provides, uses the scenarios of
[`../context/04-use-cases.md`](../context/04-use-cases.md) (UC-01–UC-17) as the
behavioural check, and states what the SGAI specification must add or extend. It
is an input to the spec build.

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY) when stating
requirements.

**Grounding.** Claims about the base specification were checked against the
primary copy of the edition declared in
[`../context/00-normative-base.md`](../context/00-normative-base.md), extracted to
text and searched. Each claim carries a clause number and a quoted sentence.
Negative claims ("the edition has no construct for X") rest on a search of the
term over the whole extraction; where the negative is load-bearing the search and
its hit count (occurrences, not lines) are stated, next to a control term known to
be present (`ImportedMPD` as a whole word: 21 occurrences on 17 lines;
`timeShiftBufferDepth`: 31), so a zero reads as the absence of the term and not as
a broken search. Claims not
verified against the primary copy are tagged `[inferred]`.

## 1. Scope

In scope:

- Every requirement R1–R40 against the capabilities of the base specification.
- The design principles DP-1..DP-3 and the extension rules DR-1..DR-10 of
  [`../context/08-dash-extension-rules.md`](../context/08-dash-extension-rules.md),
  where they decide whether a base construct can be reused.
- UC-01–UC-17 across device classes D1–D5, as the check that a gap statement is
  complete.

Out of scope:

- The APS-to-ADS and ADS-side contracts (R18, OOS-2). The VAST mapping is
  illustrative (R11.3, R11.5) and is checked here only as far as R11.4 needs.
- OOS-1..OOS-9. They are exclusions, not gaps, and are not raised below.
- Concrete syntax. Where the base offers more than one carrier, this document
  names the alternatives the build has to weigh (R8, R9, R1.5) and does not pick.

Cell values in §2:

- **full** — the base specification answers the requirement; the SGAI
  specification adopts and cites it (R1.5).
- **partial** — the base answers part of it (typically the linear family) and
  the rest is to be defined.
- **gap** — the base has no construct or rule for it.
- **N/A** — the requirement binds the specification text, the actor model or the
  Player's implementation, and there is no base capability to compare against.

## 2. Coverage matrix — requirement × DASH 6th capability

### Contract foundations

| Req | DASH 6th capability | Cell | Note |
|---|---|---|---|
| R1 | Foreign-namespace open content (§5.2.1), descriptors (§5.8.4.8 / §5.8.4.9), application event schemes (§5.10); failed execution continues playback (§5.16.2.2.6) | full | The extension points exist and are sufficient. R1.4 is the base rule for linear, extended by the spec to non-linear (G1). |
| R2 | Author declares in the MPD, client executes (`@maxDuration`, §5.16.5.2) | partial | No actor model in the base. The declare-in-MPD / enforce-in-client split exists for linear only. R2.2's one APS obligation — stay within the forwarded layouts and region (R38.4, R39.4) — has no base counterpart (G6). |
| R11 | Callback scheme aligned with VAST (§5.10.4.5.1 NOTE 1) | N/A | The base does not depend on VAST. R11.4 coverage is the spec's obligation. |
| R18 | Event `@uri` + returned MPD / List MPD (§5.16.5.2, §8.14) | partial | The Player-visible interface exists for linear; the non-linear resolution document and the request parameters of R29 do not (G1, G6). |
| R29 | `RequestParam` (Annex I.3) with the state vocabulary of Annex I.4 | gap | The base mechanism is author-declared, and its vocabulary has no device-capability axis (G6). |

### Opportunity declaration

| Req | DASH 6th capability | Cell | Note |
|---|---|---|---|
| R4 | `@maxDuration`, `@clip`, zero cap, absent = infinity (§5.16.4 Table 62, §5.16.5.2 Table 63) | partial | Linear fully answered (R4.3, R4.6–R4.8). No cap construct for overlay or pause (G1, G2). |
| R31 | — | gap | Every base event is triggered by the playhead; there is no viewer-triggered window (G2). |
| R12 | — | gap | No ad-type or layout vocabulary (G1). |
| R15 | ISO-BMFF video via Linked Periods / SPS (§5.3.2.6.1, §8.15, §7.3.1) | partial | Video is carried; image and HTML have no home on the media axis (G4). |

### Selection and ordering

| Req | DASH 6th capability | Cell | Note |
|---|---|---|---|
| R5 | — | gap | No ordered form+layout options per candidate (G3). Exhausting the candidates with none rendered hands over to R20.1 (G7). |
| R7 | Periods of a List MPD played in sequence (§8.14, §5.3.1.1) | partial | Order holds for linear. Drop-before-play and the non-linear sequence are the spec's (G3). |
| R30 | "merge process resulted in no available media" is a failed execution; `E.c` not incremented (§5.16.2.2.6, NOTE 3) | partial | Semantics are the base's for linear. The shape of an empty non-linear document is the spec's (G8). |

### Presentation

| Req | DASH 6th capability | Cell | Note |
|---|---|---|---|
| R3 | — | gap | No device-class model (G3, G6). |
| R16 | — | gap | No pause-bound presentation (G2). |
| R32 | — | gap | (G2, G8). |
| R34 | `@executeOnce` + counter `E.c` (§5.16.5.2, §5.16.2.2.2) | partial | The capability exists for timeline events; the pause window needs its counterpart (G2). |
| R35 | `@skipAfter` on alternative-MPD events (Table 63) and `PlaybackRestrictions@skipAfter` (Annex K) | partial | Linear fully answered (R35.8). Overlay and pause need the opposite default, so the base construct cannot be reused (G11). |
| R36 | `@earliestResolutionTimeOffset`, default 60 s (Table 63) | partial | Reused on overlay windows. The pause anchor and the freshness declaration are the spec's (G12). |
| R37 | Client pause described informatively (A.5) | N/A | Player implementation; the base does not constrain it. |
| R38 | `RequestParam` with request-type URNs (Annex I.3, Table I.4) | gap | No channel for a slot declaration toward the resolver of a non-linear window (G6). |
| R39 | SRD coordinates (Annex H) | gap | A coordinate model exists and is confined to media elements in arbitrary units (G13). |
| R19 | Replacement: main media time follows the alternative presentation (§5.16.1) | partial | The base couples timelines in the opposite direction; ad speed following primary is the spec's (G9). |
| R21 | — | gap | (G1, G2). |
| R25 | Time-shift buffer bounds (Table 3 `@timeShiftBufferDepth`; Table 62 NOTE 1) | gap | The freeze is the spec's; the base bounds what can be resumed (G9). |
| R26 | — | gap | (G1). |
| R27 | — | gap | (G1). |

### Interaction & composition rules

| Req | DASH 6th capability | Cell | Note |
|---|---|---|---|
| R14 | Sequential Periods of a List MPD (§8.14) | partial | Linear sequencing exists; the non-linear sequence is the spec's (G1, G3). |
| R17 | Main client paused or in listen mode during an alternative presentation (§4.2) | gap | No cross-family priority. R17.5 applies only to windows R40.5 / R40.6 make applicable, and touches base timing (G9, G14). |
| R20 | Execution queue ordered by PRT; fail-over to the next event; open-ended failure condition *"cannot start"*; one `EventStream` per scheme and value (§5.16.2.2.2, §5.16.2.2.5, §5.16.2.2.6, §5.10.2.1) | partial | Linear adopted unchanged, including a document none of whose candidates the device can render. Non-linear extension is the spec's (G7). |
| R22 | — | gap | No non-linear forms in the base; the single-form bound is the spec's (G1). |
| R40 | Two access engines, main and alternative (§4.2); event attributes of Tables 62–63 | gap | No construct relates a window to a linear event (G14). |

### Tracking

| Req | DASH 6th capability | Cell | Note |
|---|---|---|---|
| R6 | Callback scheme `urn:mpeg:dash:event:callback:2015` (§5.10.4.5); `Event@id` scope (Table 44) | partial | Full for a sub-MPD Period. No time anchor or validation for a candidate-level carrier (G15). |
| R13 | Callback scheme, Period-relative timing (§5.10.4.5, Table 44) | partial | Same as R6 (G15). |
| R23 | Open content place (§5.2.1) | gap | The place exists; the elements are the spec's (G5). |
| R24 | Carriers of DR-6 (§5.2.1, §5.10, §5.8.4.8, §5.8.4.9) | partial | The carriers exist; which one carries the asset is the spec's (G4). |
| R33 | `PlayList` metric, `starttype` / `stopreason` (Annex D.4.6); `Metrics` trigger (§5.9.1) | full | Adopted unchanged. `Metrics` requires a `Reporting` element (open question Q9). |
| R28 | — | gap | No click-through field and no user-triggered event (G5). |

### Governance

| Req | DASH 6th capability | Cell | Note |
|---|---|---|---|
| R8 | — | N/A | Binds the spec text. §4 lists what R8.2 must address. |
| R9 | — | N/A | Binds the spec text. §4 is the reuse inventory. |
| R10 | — | N/A | The base defines no overlay layout system (G1), so R10 constrains only the spec. |

**Note on method.** Negative cells rest on these searches over the whole
extraction (case-insensitive unless stated):

| Term | Occurrences | Where |
|---|---|---|
| `overlay` | 1 | Annex K.3.2, Table K.2, `MinimumLatency`: *"to avoid inconsistencies with second screen applications, overlays, etc."* — not an ad construct |
| `layout` / `layouts` (whole word) | 0 | — |
| `click` | 1 | cover page — not a construct |
| `dismiss` | 0 | — |
| `pause` | 8 | §4.2, A.5, A.14.2, Table 62 NOTE 2, Annex D.4.6 — client state and metrics, no pause-triggered event |
| `non-linear` / `nonlinear` | 2 / 20 | Introduction list item and Annex L (interactive storyline) — Period selection, not a non-linear ad |
| `percent` | 4 | encoding and anchor semantics — no percentage coordinates |

## 3. Gaps detail

### G1 — No non-linear opportunity, resolution document or composition model (R4 on non-linear slots, R12, R14, R21, R22, R26, R27, R1.4)

The base defines two event schemes that switch between presentations:
*"This tool provides the ability to switch between two independent Media
Presentations, for applications such as pre-roll and mid-roll advertisement, as
well as blackouts, during a live streaming session."* (§5.16.1). Both take over
the output: for replacement, *"the main Media Presentation is not being output,
but its media time progresses at the same speed as the currently playing
alternative Media Presentation"* (§5.16.1). Nothing in the base presents content
on top of, or beside, the primary content (§2, note on method: `overlay`,
`layout`).

The closest base construct to a video over video is the supplementary video
service (§5.8.5.16.1), and it delegates exactly what SGAI needs defined:
*"Potential manipulation of the stream and the composition of the main video and
the supplementary video are out of the scope of the DASH client."* It also sits
inside the primary content's `Preselection`, in the primary content's Period, so
the ad would have to be authored into the primary MPD rather than resolved from
an APS.

What must be added:

- **A non-linear opportunity window** — an event scheme under
  `urn:svta:dash:<construct>:<year>` (06), one per family (overlay, pause), whose
  `Event` carries the slot declarations: the cap (R4.1), allowed layouts (R38),
  the custom region (R39.2), the relation to linear events (R40), the early
  resolution offset (R36), once-per-session for pause (R34). Table 44 admits the
  payload: event content is *"XML content, possibly using elements external to
  the MPD namespace"*.
- **A non-linear resolution document** — the document the APS returns for those
  windows, carrying ordered candidates (R14), each with ordered presentation
  options (R5), the slot-level declarations of R32, R35 and R36.4, the R26
  background as an attribute of the layout an option declares (R26.1), tracking
  (R6) and click-through (R28). DR-10 fixes that
  it declares no existing profile: *"The ISO-BMFF List profile is intended for
  use in conjunction with the Alternative MPD event (see subclause 5.16)"*
  (§8.14).
- **The layout vocabulary** of R12.2 as an attribute value space, with the
  geometry the token carries for squeezeback (R12, ADR 0014) and the spatial
  bounds inherited from IAB (R12.4).
- **The composition rules**: single active form (R22), the side-by-side
  three-element composition and its decoder budget (R26.2, R26.3), the L-shape
  underlay and its budget (R27.2, R27.3), pause surfaces (R21).
- **The failure rule for non-linear**: R1.4 restates, for the constructs the
  spec adds, what the base already says for its own execution — *"A failed
  execution results in smooth continued playback of the main media
  presentation."* (§5.16.2.2.6).

On the overlay family the cap bounds cumulative duration (R4.2); a pause slot has
no declared duration for it to bound (R4, R31). The base has no
cumulative-duration model to reuse because its cap bounds one alternative
presentation (Table 63, `@maxDuration`: *"If the Alternative Presentation
initiated by this event has a longer duration than specified in this element, it
shall be terminated at the end of this duration."*). The spec should reuse the
attribute name, units and zero semantics (06, "Naming consistency with baseline
DASH"), and define the non-linear default itself, because R4.10 departs from the
base's *"If absent, the value is assumed to be infinity"* (Table 63). That
departure is an R1.5 exception and must be recorded with its reason (ADR 0015).

### G2 — No pause trigger (R16, R21, R25, R31, R32, R34)

Every base event is dispatched and executed against the playhead. For
alternative-MPD events: *"When the playhead reaches PRT, the Alternative MPD event
is executed."* (§5.16.2.2, step 3), and the whole of §5.16.2.2.5 is
*"Playhead-triggered processing"*. A viewer pause is not an input to any event
model: `pause` occurs only as client state (§4.2), as an informative trick-mode
description (A.5: *"The client may pause or stop a Media Presentation. In this
case, the client simply stops requesting Media Segments or parts thereof."*) and
as a metric value (Annex D.4.6). The execution counter exists
(*"Execution counter (number of times alternative MPD playback successfully
started)."*, Table 58), but its timeline semantics do not reach a trigger that has
no presentation time — which is what R34 states.

What must be added:

- A pause opportunity window whose `Event@presentationTime` / `Event@duration`
  mark a region, not a schedule (R31), with the trigger rule of R31.1.
- The pause-state lifecycle: dismissal within one frame on resume (R16.1), beacon
  stop (R16.2), exhaustion behaviour `repeat` / `request-again` / `stop` with
  `stop` as default (R32.1), and the R34 counter, consumed at first render
  (R34.3). R34 reuses the base's rule that only a successful start counts
  (Table 58), and R34.4 requires the spec to say so.
- The live freeze of R25 (see G9 for its interaction with the time-shift buffer).

### G3 — No ordered presentation options per candidate (R3, R5, R7, R14)

The base has alternatives only inside the media axis: *"An Adaptation Set
contains alternate Representations, i.e. only one Representation within an
Adaptation Set is expected to be presented at a time."* (§5.3.3.1). Those are
perceptually equivalent encodings of one content, not different forms and
layouts of one ad, and the axis is closed to non-MP4 media (G4). A List MPD
orders ads, not options: *"A Media Presentation as described in the MPD consists of
a sequence of one or more Periods"* (§5.3.1.1), and a List MPD's Periods are Linked
or regular Periods (§8.14 rule 4: *"List MPDs may contain one or more Linked Periods
(see 5.3.2.6), however it may also contain regular Periods."*).

What must be added: a candidate containing an ordered list of options, document
order being the preference order (R5.1, R5.5), each option pairing a form (R15)
with a layout (R12); the Player walk of R5.6 / R5.7; the ordering contract of R7
and its non-linear counterpart R14.1; the device-class table required by R3.1.
The walk ends in one of two places (R5.3): if at least one candidate was rendered,
the primary content resumes; if none was, the attempt produced no ad and the
fallback chain of R20.1 takes over (G7).

For linear, R7 is already the base's behaviour for a List MPD, and the spec adds
only the Player's permission to drop before play (R7.3) and the trim-during-play
obligation, which is the base's own cap rule (Table 63, `@maxDuration`).

### G4 — Non-AV creatives have no home on the media axis (R15, R24)

For ads reached through `ImportedMPD`: *"MPDs referenced in the ImportedMPD
element shall be restricted to the constraints of a single period profile as
defined in 8.15."* (§5.3.2.6.1). SPS applies §7.3 (§8.15.2), and §7.3.1 states:
*"The @mimeType attribute of each Representation shall be provided according to
IETF RFC 4337."* A regular Period of a List MPD is under the CMAF-extension
profile (§8.14), whose Adaptation Set constraint is stricter still: *"The
@mimeType shall be set to "<contentType>/mp4"."* (§8.12.4.3). And a Period cannot
hold events alone for a non-zero duration: *"At least one Adaptation Set shall be
present in each Period unless the value of the @duration attribute of the Period
is set to zero."* (§5.3.2.2, Table 4). These are DR-1, DR-5 and DR-7; they close
the media axis for image and HTML.

What must be added: the asset URL of an image or HTML option on one of the DR-6
carriers — open-content element (§5.2.1), event payload (§5.10), or a descriptor,
kept apart as `SupplementalProperty` (§5.8.4.9) versus `EssentialProperty`
(§5.8.4.8) per DR-9 — with the carrier classification of checklist item 8. A
video option on a non-linear candidate can keep the base path (a sub-MPD reached
by URL), and its duration is then the sub-MPD's `Period@duration` and is not
restated (06, DP-1.2).

### G5 — No metadata carrier and no user-activated event (R23, R28)

The base defines no field for click-through or for ad metadata (§2: `click` has
no construct hit). Its events are timeline events: *"Events are timed, i.e. each
event starts at a specific media presentation time and may have a duration."*
(§5.10.1). The callback fires at that time: *"DASH Callback events are
indications in the content that it is expected by a DASH Client to issue an HTTP
GET request to a given URL and ignore the HTTP response."* (§5.10.4.5.1). There
is no event fired by a viewer action.

Annex L is the one base mechanism in which a viewer's choice produces a request:
*"The DASH Client signals the chosen edge to play after the end of the current by
firing a callback at the @contactURL of the respective Event and signalling the
selection as the query parameters."* (L.3.3). It is anchored to a selection window
on the timeline and to Period graph edges; it carries no click-through URL and
cannot be reused for R28. It is the precedent 05 cites for keeping the user
interaction outside the timeline trigger.

What must be added: an R28 element in `urn:svta:dash:sgai:<year>` carrying the
click-through URL with its click-tracking URLs, read and fired on activation by a
Player conformant to the spec (R28.2, scoped per DR-8); and the R23 optional
metadata elements in the same namespace (R23.1).

### G6 — No channel for Player-declared capability or forwarded slot declarations (R29, R38, R39.3)

The base's request parametrisation is declared by the content author. For the
2025 scheme: *"The RequestParam element(s) may be present in elements such as but
not limited to MPD, Period, AdaptationSet, Representation, Preselection, or
EventStream."* (Annex I.3.1). Its state vocabulary is closed and carries no
capability axis of R3: the suffixes are `audio`, `video`, `lang#[audio|text]`,
`encryption`, `cmcd#[key]`, `execution-delta#[id]`, `expected-duration#[id]`,
`execution-count#[id]` and `previous-state` (Annex I.4.2, Table I.5). Nothing in
it states decoder count or overlay surfaces, which are the axes separating D1–D5.

R29 excludes this mechanism by construction — its parameters are Player-decided,
*"NOT expressed through the MPD-declared URL-parameter template mechanism"*
(R29). So the reserved parameter set, its names, its encoding and the
absence-means-undetermined rule (R29.7) are the spec's.

For R38 the data *is* Publisher-declared, so the base mechanism is a real
alternative and the build has to weigh it (R8.2):

- `RequestParam` can target a request type the base does not define: Table I.4
  admits *"a URN or tag URI, where the request type semantics is understood by the
  client and specified by the URN / tag URI owner."* The existing key
  `altmpd`, defined as *"all requests for MPDs representing the alternative
  Media Presentation, as defined in subclause 5.16"*, does not cover a non-linear
  window, which is not a §5.16 event.
- Against it: R38.3 makes the carrier one of R29's reserved parameters, and
  copying `@allowedLayouts` into a `@queryString` would declare the same value
  twice, which DP-1.2 forbids. And outside a profile that allows the scheme, the
  base requires an MPD-level `EssentialProperty` (*"shall be present and have no
  content, unless the scheme is explicity allowed in a profile"*, Annex I.3.1),
  which a legacy Player that does not recognise it would treat as essential
  (§5.8.4.8 NOTE 2: *"the DASH Client is expected to terminate the media
  presentation"*).

The receiving side has no base rule either. Annex I.3 specifies how the client
builds and attaches the parameters (I.3.4, *"Extended parameter generation"*) and
states nothing about what the server that receives them returns: over I.3, `server`
occurs only for Content Steering (*"Content Steering server request"*) and
`respon` only for the header sources of `@headerParamSource` [inferred from that
search]. R2.2 places on the APS exactly one obligation toward Publisher-declared
constraints — return only options inside the layouts and the region it received
(R38.4, R39.4) — and the spec states it without a base construct to lean on; the
Player's own check (R38.5, R39.5) stays, so a non-conforming APS costs options, not
correctness.

What must be added: the reserved parameter set of R29 (at least one parameter
per R3 axis, R29.6), the vendor-prefix rule (R29.4), the forwarding of
`@allowedLayouts` unchanged (R38.2) and of the custom region (R39.3), and the APS
obligations of R38.4 and R39.4.

### G7 — The fallback chain is the base's for linear and has no anchor for the other two families (R20)

For linear, R20 adopts the base unchanged. The queue: *"There is an execution
queue QE, which is a priority queue of references to a subset of events in table
T, ordered by the presentation time PRT."* (§5.16.2.2.2). Fail-over: *"If
execution fails, steps a-c above are repeated for next events in QE, until:"*
execution succeeds, the next PRT is in the future, or the queue is empty
(§5.16.2.2.5, step 2 d). End state: *"If no event can be successfully executed,
the playback continues uninterrupted."* (§5.16.2.2.5). The four failure shapes of
R20.1 map to §5.16.2.2.6: *"Alternative MPD is unavailable or invalid."* and
*"Alternative MPD is a List MPD, and merge process resulted in no available
media."* R20.2 is the base rule: *"A Period shall contain at most one EventStream
element with the same value of the @schemeIdUri attribute and the value of the
@value attribute, i.e. all Events of one type shall be clustered in one Event
Stream."* (§5.10.2.1). R20.3 correctly separates execution order from dispatch
order, which the base defines separately: *"all active events are dispatched
(according to their dispatch mode) in the order they appear in the EventStream
element."* (§5.10.2.1).

A resolution document whose candidates the device can render none of is a failed
execution under R20.1, and for linear that too is the base's. The condition that
heads the list is open-ended: *"The playback of the alternative presentation
cannot start. The reasons for this include (but are not limited to) the following
(at time PRTA):"* (§5.16.2.2.6), and one of the listed reasons is already a
playback condition rather than a resolution one: *"Media playback is impossible
due to missing media or initialization segments."* A device that can render none
of the candidates cannot start the alternative presentation, so the base covers
the case without extension. This is what DP-3's first consequence rests on: an
opportunity is given up only after every declared way of filling it — the next
overlapping window, or the superseded linear events of R40.3 — has been tried.
UC-12 path 4 is the behavioural check across D1–D5.

What must be added: the extension of the queue and fail-over to overlay and
pause windows (R20.1, R20.3), which have no `AlternativeMPDEventType` and are
outside §5.16, including the no-renderable-candidate condition, which for the
non-linear families is the spec's and not the base's; the document-position tie-break the base does not give (R20.3);
the wrong-family rule (R20.4); and per-window binding of declarations stated as
a normative Player obligation (R20.5, R20.6).

### G8 — The empty resolution: semantics from the base, shape from the spec (R30, R32.2, R36.6)

For linear the case and its consequence are the base's: the List-MPD
no-media condition of §5.16.2.2.6 quoted in G7, and *"The counter E.c has not
been incremented due to the failure, consequently if E.c = 0 the event can still
be executed in the future even if the value of @executeOnce is "true"."*
(§5.16.2.2.6 NOTE 3). What a well-formed List MPD with no media looks like is not
spelled out in the base [inferred]: §8.14 does not state a minimum number of
Periods, and a static MPD needs a derivable duration (Table 3,
`@mediaPresentationDuration`: *"This attribute shall be present when neither the
attribute MPD@minimumUpdatePeriod nor the Period@duration of the last Period are
present."*).

What must be added: the well-formed empty non-linear resolution document
(R30.1), how a Player tells it apart from an unparseable one (R20.1), and its
role under `request-again` (R32.2) and after re-resolution (R36.6). For linear,
the spec should state the empty List MPD shape it expects or note that it relies
on the base's merge-failure condition (open question Q4).

### G9 — Speed, timeline accounting and the live pause (R4.11, R17.5, R19, R25, R37)

- **Speed (R19).** The base couples the two timelines in the direction opposite
  to R19: during replacement the main media time follows the alternative
  presentation (§5.16.1, quoted in G1), and the informative dual-client model
  propagates the ad's speed to the main client — *"on reception, the main client
  will adjust its playhead propagation speed. As a result, media time elapses at
  the same speed in both clients."* (A.14.2). No base rule makes an ad follow the
  primary content's speed. For linear this is not a conflict (the primary content
  is not output during the ad), and R19 binds the ad's rendering speed, which the
  base leaves to the client. For non-linear it is new.
- **Timeline accounting (R4.11).** The base accrues an alternative
  presentation's duration on media time (Table 57, `APDA`; §5.16.2.2.5 step 1 a,
  *"PHP ≥ PRTA + APDA"*), so a pause of the ad does not consume its cap. The spec
  extends the same accounting to non-linear forms suspended under R17.
- **Pause over a linear ad (R17.5).** R17.5 applies only to a pause window
  applicable to the presentation being output — one declared in the linear ad's
  own `MPD` (R40.6) or one of the triggering presentation that declares on top
  (R40.5) — so it depends on the relation of G14. The base foresees a viewer pausing the
  alternative presentation and states the consequence for resumption: *"If RT is
  in the past, the playback shall start from the oldest available media segment
  (the edge of the timeshift buffer)."* and *"The above can happen in case a user
  pauses the alternative Media Presentation."* (Table 62, `@returnOffset`,
  NOTES 1–2). A pause ad over a replacement in live content can therefore move
  the resumption point; R17.5's "resume it from where it was suspended" holds for
  the linear ad itself, and the main presentation's return is the base's rule.
- **Live freeze (R25).** Freezing presentation time is Player behaviour and the
  base does not forbid it, but the paused position stays playable only while it
  is inside the time-shift buffer: *"specifies the duration of the smallest time
  shifting buffer for any Representation in the MPD that is guaranteed to be
  available for a Media Presentation with type 'dynamic'."* (Table 3,
  `@timeShiftBufferDepth`). R25 says nothing about a pause that outlasts it
  (open question Q5).
- **Pause mechanism (R37).** A.5 is informative and describes the stop-requesting
  mechanism only; the base does not constrain how a client pauses, so R37 adds a
  definition the base does not contradict.

### G10 — Profiles and schema placement bear on every construct (R1.2; DR-2, DR-4, DR-8, DR-10)

- **Open content is not uniform across types.** `EventStreamType` declares
  `xs:any namespace="##other"` and no `xs:anyAttribute`; `EventType`,
  `PeriodType`, `MPDtype` and `DescriptorType` declare both; `ImportedMpdType`
  declares `xs:anyAttribute` and no child content (Annex B, verified on the type
  definitions). An SGAI attribute on `<EventStream>` is not admissible; a child
  element is. `AlternativeMPDEventType` declares both (§5.16.6), but R40.7 keeps
  SGAI off the inherited linear events.
- **The authoring obligation.** *"In addition, the MPD shall be authored such
  that, after XML attributes or elements in the other namespaces than the DASH
  namespace are removed, the result is a valid XML document formatted according
  to that schema and that conforms to this document."* (§5.2.1). And the DASH
  namespace is closed: *"the addition of XML attributes or elements in the DASH
  namespace, is reserved to ISO/IEC."* (§5.2.1).
- **No hold over a Player.** *"Hence, profiles merely specify restrictions on MPD
  and Segments rather than DASH Client behaviour."* (§8.1 NOTE 1). An
  Interoperability Point URI would declare, not compel: *"It is recommended that
  such external definitions be not referred to as profiles, but as
  Interoperability Points."* (§8.1).
- **The non-linear document and `type="list"`.** *"For Media Presentations with
  MPD@type set to "list" the constraints of a static Media Presentation shall
  apply."* (§5.3.1.4) — available without the List profile, whose URN would claim
  membership in the §5.16 family (DR-10). The build decides whether to declare
  `type="list"`.
- **Merged content keeps SGAI elements.** When a Linked Period is resolved, the
  kept items include *"any elements from a different namespace"*
  (§5.3.2.6.3, step 3 b ix), so SGAI elements on a List-MPD Period survive the
  merge; SGAI elements at MPD level of an imported MPD do not — *"Any attributes
  or elements on MPD level of the imported MPD are ignored except for the
  following ones"* (step 3 a), and foreign elements are not among the exceptions.

### G11 — Viewer dismissal: the base skip control exists twice, with the opposite default (R35)

On alternative-MPD events: `@skipAfter` *"describes an offset in time (in
fractional seconds) from the beginning of the alternative presentation till the
moment the rest of that presentation may be skipped by the application in
response to a user action."*, with *"Zero duration implies that skipping is
allowed everywhere."* and *"Default value is PT0S."* (Table 63). In the service
description: *"The default value of 0 implies that skipping is allowed
everywhere."* (Annex K, Table K.9; element in Table K.18).

For linear, R35.8 adopts it whole, default included — full. For overlay and pause
the base has no declaration, and R35.1 requires an undeclared slot to be
non-dismissible; reusing `@skipAfter` would import the opposite default, which
06 forbids. What must be added: a resolution-document field in the SGAI
namespace carrying *whether* (default: no) and *after how many seconds* (R35.1,
R35.2), and the Player rules R35.3–R35.6. R35's placement in the resolution
document follows from the declaration belonging to the APS; the base's control
sits on the Publisher's event, which is one more reason it does not fit.

### G12 — Early resolution is the base mechanism; resolution freshness has no in-document anchor (R36)

`@earliestResolutionTimeOffset` *"specifies the time interval (in units of
EventStream@timescale) prior to the Event@presentationTime during which the MPD
described in the @uri attribute may be requested. The default is 60 seconds in
units of timescale."* (Table 63). The base leaves the moment of resolution open —
*"the precise timing of the resolution is not defined in this document"*
(§5.16.2.2, step 2) — which R36.7 matches. Reuse on the overlay window is direct
(R36.2). For pause, the offset is anchored to the window start (R36.3), which the
base computes the same way (`ERT` from `Event@presentationTime`, Table 57) —
the difference is only what the window means (G2).

Freshness (R36.4) has no in-document base construct with the right meaning. Two
candidates the build must weigh and justify rejecting or adopting (R8.2):

- `MPD@availabilityEndTime` — *"specifies the latest Segment availability end
  time for any Segment in the Media Presentation."* (Table 3). The base already
  makes an imported MPD fail resolution when it is past (§5.3.2.6.3, step 1 c).
  Its meaning is media availability, not decision validity; using it for R36.4
  would change what it says (R1.3) unless the APS truly withdraws the media.
- HTTP caching — the base leaves it outside: *"The underlying HTTP client may
  cache HTTP responses in accordance with IETF RFC 9111. The HTTP caching
  behaviour is outside the scope of this document."* (§5.16.2.2.6 NOTE 5). R36.4
  asks for a declaration in the resolution document, which transport headers
  are not.

### G13 — The `custom` rectangle: a coordinate model exists and is confined to media elements (R39)

SRD defines positions in a reference space, but only for media: *"SRD information
shall be contained exclusively in these two MPD elements (AdaptationSet and
SubRepresentation)."* (Annex H.1), and its units are relative to an authored space:
*"The total_width and total_height values in a SRD provide the size of this
reference space expressed in arbitrary units."* (H.2.2). A non-linear option is
not an AdaptationSet (G4), and R39.2 fixes percent of the video viewport with a
top-left origin. What must be added: the rectangle on the `custom` option (R39.4),
the region on the slot (R39.2), the containment checks (R39.5), marked optional
(R39.1). R8.2 requires the spec to say why SRD is not reused.

### G14 — The window's relation to linear events has no base construct (R40, R17.5, R22 across families)

Neither alternative-MPD scheme distinguishes an ad from a blackout —
*"This value is currently not required."* (Table 59) and *"This value is
currently not used."* (Table 61) — and the event attributes (`@uri`,
`@earliestResolutionTimeOffset`, `@serviceDescriptionId`, `@maxDuration`,
`@executeOnce`, `@noJump`, `@skipAfter`, Table 63; `@returnOffset`, `@clip`,
`@startWithOffset`, Table 62) say nothing about another construct. The base does
give R40.6 its model: *"In case Alternative Media Presentations are used, there
are two instances of DASH access engine, main and the alternative, both working
as described above."* (§4.2).

What must be added: the relation declared on the non-linear window (default /
supersede / on top, R40.1), the Player rules R40.3–R40.6, and the R1.5 exception
record for supersede (R40.8, ADR 0020). R17.5 inherits its scope from R40.5 and
R40.6, so the pause-over-linear rule cannot be stated before the relation is. 06 names the three carriers to weigh; an
attribute on `<EventStream>` is excluded by schema (G10), and a stream-level
value would bind every window in the stream (06).

R40.3's fallback — execute the superseded linear events when the window
presents no ad — lands after the event's PRT. The base handles delayed execution
(Table 57, `PRTA`: *"media time at which the Event is executed, PRT ≤ PRTA ≤
EAP"*; §5.16.2.2.6, delayed execution with `@clip`), so the supersede fallback
is expressible with base timing, and the replacement shortens under the default
`@clip` (R4.6).

A constraint for R40.6 "in turn": *"List MPDs shall not contain Alternative MPD
events."* (§8.14, rule 5). An alternative presentation delivered as a List MPD
therefore triggers no further alternative presentations (open question Q7).

### G15 — Tracking on non-linear candidates has no base time anchor or validation (R6.5–R6.7, R13)

The callback event is timed against a Period: `Event@presentationTime`
*"specifies the presentation time of the event relative to the start of the
Period, taking into account the @presentationTimeOffset of the Event Stream, if
present."* (Table 44). An `<EventStream>` placed as open content inside a
candidate is not in a Period, so the base gives it no time origin — R6.6 supplies
one. Its `@id` scope in the base is media-presentation-wide: *"The scope of the @id
for each Event is within the same @schemeIdURI and @value pair over the duration
of the current media presentation."* (Table 44), which R6.5 adopts for a List MPD
and narrows per candidate for non-linear. Schema validation does not descend into
foreign content with `processContents="lax"` unless a schema for the namespace is
supplied [inferred from the XML Schema meaning of `lax`], which is why R6.7
requires the spec to state how the carrier is validated. The callback value is
fixed by the base (`EventStream@value` = 1, Table 47), so the "no `@value`" rule of
06 does not apply to it.

## 4. Reuse opportunities

Each row is a base construct the build must weigh before introducing its own
(R9.3), and the outcome must be written inline (R8).

| Base construct | Reuse for | Fit |
|---|---|---|
| `@maxDuration` name, units (`EventStream@timescale`), zero = not executed (Table 63) | R4 cap on non-linear windows | Reuse name and units; the absent default departs (R4.10, recorded exception). |
| `@earliestResolutionTimeOffset`, default 60 s (Table 63) | R36.1–R36.3 | Direct reuse, default included (06, ADR 0018). |
| `@executeOnce` + `E.c` success-counting (Table 63, Table 58, §5.16.2.2.6 NOTE 3) | R34 | Semantics reused; the counter is stated in pause terms (R34.4). |
| `@skipAfter` (Table 63, Annex K) | R35 | Linear only (R35.8). Rejected for overlay/pause because of its default (G11). |
| `@noJump` (Table 63) | seek restriction | Linear unchanged; excluded on non-linear (OOS-7). |
| Execution queue, fail-over, end state (§5.16.2.2.2, §5.16.2.2.5, §5.16.2.2.6) | R20, R30 | Linear adopted; extended to non-linear (G7). |
| One `EventStream` per scheme/value (§5.10.2.1) | R20.2 | Direct. |
| Callback scheme (§5.10.4.5) | R6, R13 | Direct; time anchor and validation added for candidate-level carriers (G15). |
| Linked Period / sub-MPD via `ImportedMPD` (§5.3.2.6) | video options of non-linear candidates; linear baseline | Reuse the sub-MPD for video; duration read from its `Period@duration` (06). |
| `Period@duration` reconciliation (§5.3.2.6.3 step 3 d iii) | DP-1.2 | Base pair, not a duplication. |
| `MPD@type="list"` without the List profile (§5.3.1.4) | non-linear resolution document | Available; build decides (DR-10). |
| `SupplementalProperty` vs `EssentialProperty` (§5.8.4.8 / §5.8.4.9) | descriptor-shaped carriers | Choose per DR-9; `EssentialProperty` never on the primary-content path. |
| `RequestParam` + request-type URN (Annex I.3, Table I.4) | R38 forwarding | Weighed and to be justified against R38.3 / DP-1.2 (G6). |
| Annex I.4 state vocabulary | R29 | Not a fit: no capability axis, author-declared (G6). |
| `PlayList` metric (Annex D.4.6) + `Metrics` (§5.9) | R33 | Direct; `Reporting` requirement open (Q9). |
| Supplementary video / `Preselection` (§5.8.5.16) | video overlay | Not a fit: composition out of scope of the client, sits in the primary Period (G1). Single-decoder VVC subpictures are OOS-6. |
| SRD (Annex H) | R39 | Not a fit: media elements only, arbitrary units (G13). |
| `MPD@availabilityEndTime` (Table 3) | R36.4 | Weigh; meaning differs (G12). |
| Annex L selection callback | R28 | Not a fit: timeline selection window, no click-through (G5). |

R8.2 also requires stating why these are not used where a reader would expect
them: `@skipAfter` on overlay/pause, SRD for `custom`, supplementary video for
video overlays, `RequestParam` for R29/R38, the List profile for the non-linear
document, and `MPD@availabilityEndTime` for freshness.

## 5. Open questions

### 5.1 For the working group or the build

- **Q1 — Carrier of the R40 relation.** Attribute on the window versus
  descriptor on the window (06 leaves it open; `EventStream` attributes are
  excluded by schema, G10).
- **Q2 — Non-linear document type.** Declare `MPD@type="list"` without the List
  profile, or a document of its own (DR-10). The first inherits static
  constraints and XLink exclusion (§5.3.1.4).
- **Q3 — Asset carrier for image/HTML** among DR-6 (a) / (b) / (c1) / (c2),
  per option.
- **Q4 — Shape of an empty linear List MPD.** The base names the condition
  (*"merge process resulted in no available media"*) but not a minimal document;
  whether R30.1 for linear requires a particular shape is not stated [inferred].
- **Q5 — Live pause beyond the time-shift buffer.** R25 freezes presentation
  time; when the frozen position leaves `@timeShiftBufferDepth`, what the Player
  resumes to is not stated. The base's rule for a replacement (resume at the
  buffer edge, Table 62 NOTE 1) is the obvious candidate under R1.5.
- **Q6 — Freshness carrier (R36.4).** New SGAI field versus
  `MPD@availabilityEndTime` (G12).
- **Q7 — R40.6 "in turn" with List MPDs.** §8.14 rule 5 forbids Alternative MPD
  events in a List MPD; R40.6 should state that nested alternative presentations
  arise only from alternative presentations that are not List MPDs.
- **Q8 — Reserved parameter set of R29.** Names, encoding and which axes
  (decoder count, image-over-video, HTML-over-video) are needed to separate
  D1–D5 (R29.6).
- **Q9 — R33.4 versus R33.3.** `Metrics` requires `Reporting` with cardinality
  *"1 ... N"* (§5.9.2, Table 42), and *"No reporting scheme is specified in this
  document."* (§5.9.4); *"It is expected that elements containing unrecognized
  reporting schemes are ignored by the DASH Client."* (§5.9.4). A Publisher
  obliged to request `PlayList` must therefore name a reporting scheme that some
  external specification defines, while R33.3 keeps transport out of scope. R33
  should say which scheme, or that the choice is the Publisher's.
- **Q10 — ADS `<Error>` versus unsold.** 05's interface table lets the APS
  translate ADS errors into HTTP errors *or* an empty List MPD; R30.1 forbids an
  error response only for "resolved with no ads". Whether an ADS error is that
  case is not stated.

### 5.2 Discrepancies between `context/` and the primary copy

- **05, "Resolution document timing baseline"** states that `Event@presentationTime`
  values in the resolution document are *"relative to the start of the ad
  break"*. The base anchors them to the Period (Table 44, quoted in G15).
  In a multi-ad List MPD each ad is its own Period, so the second ad's beacons are
  relative to that ad, not to the break. 05's own sub-MPD example is consistent
  with the base (beacons 0–15000 ms on a 15 s ad), and R13 ("relative to the ad's
  presentation time") is consistent too; only the prose in that section is not.
- **05, VAST mapping, `<AdSystem>` row** attributes to §8.14 that it *"confines
  the spec's tracking footprint to the callback event scheme"*. §8.14 has five
  rules and none concerns events beyond excluding Alternative MPD events (rule 5).
  The callback admission is in the Advanced Linear profile: *"EventStream elements
  may indicate Alternative MPD (5.16) and Callback (5.10.4.5) event schemes."*
  (§8.13.2.2).
- **99-glossary, "Foreign-namespace open content"** says the mechanism works via
  the `xs:any` declaration *"on every container in the MPD schema"*. Annex B does
  not declare both on every type: `EventStreamType` has no `xs:anyAttribute` and
  `ImportedMpdType` has no child content (G10). DR-2 states this correctly.
- **05, linear flow step 4** states that the Player *"picks a randomised instant
  between the ERT and the event's presentationTime"*. The base does not require
  it: *"There is no necessity to resolve at time ERT. If there is an expectation
  of a large number of concurrent clients with identical playhead position, it can
  be useful to randomize the actual resolution time"* (§5.16.2.2.6 NOTE 1).
  05 is informative, so this is a wording issue, not a normative conflict.
- **05, `@clip` bullet** says a late ad *"is trimmed so that it does not exceed
  `@maxDuration`"*. What `@clip` decides is the end anchor — *"the alternative
  presentation shall terminate at the latest at time PRT + APDmax . If the value
  is "false", the presentation shall terminate at time PRTA + APDmax"* (Table
  62) — and neither value lets the ad exceed `@maxDuration`. R4 states it
  correctly.

No discrepancy was found for the base quotations in R4, R20, R30, R33, R34, R35,
R36, R40, DP-1.2, DP-3, DR-1..DR-10 or 06; each was located in the primary copy
with the wording `context/` gives.

### 5.3 Context-internal observations

- `01-intro.md` describes the folder as containing *"the gap analysis that
  compares the status quo of MPEG-DASH 6th edition against those use cases"*.
  `context/` holds no gap analysis; it lives here, in `context-analysis/`, which
  `context/` must not reference. The sentence should be removed or reworded.
- R26.1 places the side-by-side background on *"the layout the presentation
  option declares"*. The R26 prose (*"an attribute of the slot / layout
  composition"*) and UC-09 (*"a composition attribute of the slot / layout"*) still
  admit the slot as its home. R26.1 governs; the build should follow it and not the
  prose.
- R20's rationale paragraph illustrates the fallback only with resolution failures
  (*"the APS is unreachable, the event URL fails"*). R20.1 also makes a document
  with no renderable candidate a failed execution; the paragraph is an
  illustration and does not contradict it, but it should not be read as the list.

## References

- The base specification: the edition and primary copy declared in
  [`../context/00-normative-base.md`](../context/00-normative-base.md).
- [`../context/02-actors.md`](../context/02-actors.md),
  [`../context/03-requirements.md`](../context/03-requirements.md),
  [`../context/04-use-cases.md`](../context/04-use-cases.md),
  [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md),
  [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md),
  [`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md),
  [`../context/08-dash-extension-rules.md`](../context/08-dash-extension-rules.md),
  [`../context/99-glossary.md`](../context/99-glossary.md).

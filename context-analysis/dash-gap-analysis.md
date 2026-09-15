[GROUNDED_BY=notebooklm]

# DASH 6th edition gap analysis (SGAI for linear + non-linear ads)

This document compares the requirements in
[`../context/03-requirements.md`](../context/03-requirements.md) (R1–R30)
and the use cases in
[`../context/04-use-cases.md`](../context/04-use-cases.md) (UC-01–UC-13)
against what MPEG-DASH 6th edition (FDIS ISO/IEC 23009-1:2025) provides,
and identifies what the SGAI specification must add or extend. It is the
bridge between the canonical context and the spec build.

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY) when
stating requirements.

**Grounding.** NotebookLM was queried against the notebook
`Streaming Protocols — DASH, HLS, C2PA, DRM`
(`bb67e20c-9ad1-4a1d-a641-7c7d901f93cb`) for the load-bearing DASH 6th
claims: whether any non-linear ad construct exists; the scope of
`urn:mpeg:dash:nonlinearplayback:2020` (Annex L, illustrated in G.26)
and of the Spatial Relationship Description (Annex H); the timeline-only
nature of DASH events; the alternative-MPD event attributes, the
`@maxDuration` trim rule, the execution queue and its handling of
overlapping events; the List MPD sequencing semantics, its Period
cardinality, and its prohibition on nested alternative-MPD events; the
zero-duration versus failed-execution distinction; the ordered-preference
constructs (`Preselection`, `@selectionPriority`,
`urn:mpeg:dash:fallback:2016`); the Annex I.4 state vocabulary and
whether any client-capability channel exists; playhead behaviour during
a user pause of a live presentation; and the playback-rate model. Quoted
text is verbatim from those sessions. Claims the notebook did not
confirm are tagged `[inferred]`.

## 1. Scope

In scope:

- Every requirement R1–R30 in `../context/03-requirements.md` against the
  capabilities MPEG-DASH 6th edition provides.
- The use cases UC-01–UC-13 in `../context/04-use-cases.md` as the
  behavioural check on those capabilities across device classes D1–D5.
- The constructs, carriers and conformance rules the spec must add, and
  the existing DASH machinery it must reuse first (R8 / R9).

Out of scope:

- The APS-to-ADS and ADS-side API contracts (R18) — opaque to the spec.
- VAST version pinning (R11) — the spec is VAST-version-agnostic.
- ABR, DRM, transport, low-latency tuning — orthogonal to SGAI.
- The IAB ad-type vocabulary itself (R12) — owned by the IAB and
  analysed separately in [`iab-ad-templates.md`](iab-ad-templates.md).
- The linear SGAI baseline mechanics themselves — inventoried in
  [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
  and absorbed here as the starting point, not re-derived.

## 2. Coverage matrix — R × DASH 6th capability

Cells: **full** (DASH 6th covers it normatively and the spec reuses it
as-is), **partial** (covered for the linear case only, or the machinery
exists but is not bound to what the requirement needs), **gap** (no
native construct — the spec must add one), **N/A** (governance or
document-level — DASH has nothing to say). The grouping follows the
sub-sections of `../context/03-requirements.md`.

### Contract foundations

| R | Theme | DASH 6th status |
|---|---|---|
| R1 | Extends DASH 6th; legacy Player ignores and keeps playing | **full** — §5.2.1 foreign-namespace open content, with NOTE 2 mandating that an unimplemented foreign element is discarded together with its whole subtree (DR-2 / DR-3); plus per-scheme `Event` skip (§5.10). The ignore-if-unknown contract is inherited, not invented. |
| R2 | Four actors, fixed roles | **partial** — §5.16 wires only two legs: the MPD author (Publisher) and the client (Player). The APS is nothing more than "whatever answers the event URL", and the ADS is invisible to DASH. No MPD construct binds an actor to a responsibility, so R2 is carried entirely by spec prose and conformance criteria. |
| R11 | No dependency on VAST | **N/A** — DASH is VAST-agnostic by construction; nothing to add or avoid. |
| R18 | Player-visible interface only | **N/A** — governance; DASH does not constrain server-side APIs. |
| R29 | Player-declared capability parameters on the resolution request | **gap**, confirmed negatively: the edition defines no mechanism by which a client declares its device rendering capabilities to a server. The Annex I.4 state vocabulary describes the currently playing Representation and event state (`video`, `audio`, `lang#[…]`, `encryption`, `cmcd#[key]`, `execution-delta#[id]`, `expected-duration#[id]`, `execution-count#[id]`, `previous-state`), not decoder budget or overlay-surface support; CMCD (Annex K.3.7) carries operational delivery state; `ServiceDescription` (Annex K.3) runs the other way, service to client. §I.4's query template is authored in the MPD, so its parameter set is fixed at authoring time — which is why R29 places the reserved parameters outside it. |

### Opportunity declaration

| R | Theme | DASH 6th status |
|---|---|---|
| R4 | Publisher-declared max slot duration, Player-enforced | **partial** — the cap and the trim already exist for the linear slot: *"If the Alternative Presentation initiated by this event has a longer duration than specified in this element, it shall be terminated at the end of this duration"*, and *"If the value of `@maxDuration` is zero, the event is not executed"*. There is no non-linear slot in DASH at all, so no cap construct for an overlay or pause window; and the "enforce against **actual** rendered length" rule (R4.5) has no DASH anchor even for linear. |
| R12 | Closed IAB ad-type / placement set | **N/A** for the vocabulary (owned by the IAB); **gap** for the carrier — no DASH construct carries an ad-type or visual-placement token, so the Publisher's allowed-layout declaration on the slot is a net new construct. |
| R15 | Creative carriers: video, image, HTML | **partial** — video is native (an ISO-BMFF presentation reached via `<ImportedMPD>`, SPS-conformant by construction). Image and HTML are a **gap**, and doubly so: the RFC 4337 chain (DR-1 / DR-5) closes the AdaptationSet axis, and no profile, annex or clause in the base standard defines carriage of a static image or an HTML document as a Representation at all — `Representation` is defined for continuous media streams (video, audio, timed text, timed metadata). |

### Selection and ordering

| R | Theme | DASH 6th status |
|---|---|---|
| R5 | Candidates carry ordered presentation options; Player renders the first it can satisfy | **gap** — a List MPD is a *playlist*: *"A Media Presentation as described in the MPD consists of a sequence of one or more Periods"*, played back-to-back, not offered as alternatives. No construct lets one ad candidate carry an ordered list of (form + layout) options. The two that come closest are scoped elsewhere: `Preselection` (§5.3.11) with `@selectionPriority` (§5.3.7.2) orders preferred experiences *within* a Period across Representations; the MPD fallback scheme `urn:mpeg:dash:fallback:2016` (§5.11.3) orders whole candidate MPD URLs by document order — *"the content author expresses the preferences of using one of those by the order with the first one having the highest preference"* — which is R5's preference rule at the wrong granularity. R8 requires both to be considered and the departure documented. |
| R7 | Honour the resolution document's order | **partial** — declared-order playback is already the List MPD semantics. What is missing is the drop / trim vocabulary R7 adds on top: drop-before-play on declared duration, trim-during-play on actual length, and the prohibition on re-ordering or deduplicating what survives. |
| R30 | Empty resolution distinguishable from failed | **partial** — the edition does define a legitimate zero-ad outcome: *"If at time PRTA the duration APDA is determined to be 0, the event is not executed and the playback of the main Media Presentation continues seamlessly."* It also separates that from an execution failure (alternative MPD unavailable or invalid, a List MPD whose merge yields no media, missing segments), and the separation is observable in exactly one place — a failure *"does not count for the purpose of Event Restrictions"*, so the execute-once counter is not incremented. That is client-internal bookkeeping with no reporting channel, anchored on a zero **duration** rather than on a document that carries no candidates. R30's requirement — an unfilled opportunity identifiable as unfilled — still has to be built, and cannot be built as a zero-Period List MPD (see G8). |

### Presentation

| R | Theme | DASH 6th status |
|---|---|---|
| R3 | Diverse device classes D1–D5 | **N/A** — DASH models codecs and bandwidth, not concurrent decoder budget or overlay-surface capability. The capability axes R3 separates are what R29's reserved set must express. |
| R16 | Pause-ad lifecycle bound to pause state | **gap** — DASH events are strictly scheduled against the media presentation timeline; *"The DASH Client shall dispatch the event to the application at the presentation time of the corresponding media sample"*. A viewer pause is an out-of-band action on the playhead, and the standard defines no event or trigger that activates on a pause state. |
| R19 | Ad playback speed follows primary content | **partial** — the edition already carries the derivation. `@maxPlayoutRate` (§5.3.7.2) and the DASH Metrics `PlayList` (Table D.5) define *"playback speed relative to normal playback speed (i.e. normal forward playback speed is 1.0)"*, with a media interval of duration `DU` rendering in `DU/r` of wall clock at speed `r`; and an event still fires when the playhead reaches its presentation time whatever the rate. What is absent is the binding R19 needs: nothing ties an ad form's on-screen length, or a slot cap, to that derived value. |
| R21 | Pause-ad fullscreen or partial overlay | **gap** — depends on the pause-ad construct that does not exist (R16). |
| R25 | Pause-ad presentation-time freeze in live content | **partial**, and with a bound the requirement does not yet state. The freeze is already DASH's model: the playhead is *"the media time that is presented (i.e., rendered) at specific wall-clock time"*, so on a user pause it stays static at the paused media sample while the live edge advances. But the guarantee is not unbounded — once the pause exceeds `MPD@timeShiftBufferDepth`, the paused position falls out of the timeshift buffer and playback must resume from the oldest available segment or jump to the live edge. R25 promises the freeze holds "for the full duration of the pause"; DASH bounds it. |
| R26 | Side-by-side / double-box with background element | **gap** — DASH carries no layout composition primitives. Annex H's Spatial Relationship Description (`urn:mpeg:dash:srd:2014`) expresses coordinate relationships between spatial objects — tiles, ROIs, panoramas — for viewport-adaptive streaming; it is stream metadata for tile selection, not an overlay composition facility, and it is not the right reuse target (and per R10 the spec must defer to HTML5 / CSS rather than build one). |
| R27 | L-shape / squeezeback, one full-frame ad creative | **gap** — same as R26. Neither the alternative-MPD events nor the List MPD profile supports concurrent side-by-side playout, picture-in-picture, squeezeback layouts, or compositing an ad graphic over the primary video surface. |

### Interaction and composition rules

| R | Theme | DASH 6th status |
|---|---|---|
| R14 | Sequential non-linear forms within a slot | **gap** — there is no non-linear slot to sequence forms inside. The ordering contract itself is borrowable from the List MPD profile once the slot exists. |
| R17 | Pause-ad priority over overlay | **gap** — depends on the R14 / R16 constructs. |
| R20 | Overlapping same-family windows: first-window-wins with fallback | **partial**, and closer than it looks. The execution model already forbids concurrency and already produces first-wins: on-receive dispatching puts every alternative-MPD event into a single execution queue ordered by presentation time; exactly one alternative client exists, so a second event whose presentation time falls inside a running alternative presentation is not executed concurrently; playhead-triggered evaluation on the main timeline is suspended while the alternative plays; and on return the queue is reset, dropping every event whose active window has elapsed. What is absent is the **fallback** half — the drop is unconditional rather than conditional on the first window having succeeded, and nothing licenses falling through when the first fails to resolve. |
| R22 | At most one active non-linear form | **gap** — DASH has no notion of a concurrently presented ad surface to bound. The edition's own single-alternative-client model is the same reasoning applied to linear, and is the precedent R22 should cite. |

### Tracking

| R | Theme | DASH 6th status |
|---|---|---|
| R6 | Tracking beacon carrier | **full** — the callback event scheme `urn:mpeg:dash:event:callback:2015` (§4.7 / §5.10.4.5) is reused verbatim; R13.4 forbids a parallel scheme. |
| R13 | ADS-directed beacon schedule, relative timings | **partial** — the carrier is full (R6). The relative-to-ad-presentation timebase falls out of the sub-MPD's own Period timeline, but the obligations R13 adds — the Player executes the schedule it reads, and stops firing at an R4 trim boundary — are spec-side. |
| R23 | Application-level ad metadata carrier | **gap** — DASH 6th defines no native MPD field for `AdSystem`, `AdTitle`, `Advertiser` or comparable creative metadata. Conveyance is via DR-6(a) SVTA-namespaced elements; legacy clients discard the subtree (DR-3). |
| R24 | Non-AV creative asset carrier | **gap** — DR-1 / DR-5 close the AdaptationSet axis, and `Representation` is not defined for non-continuous assets in the first place. Asset URLs must route through the DR-6 enumeration. |
| R28 | ClickThrough carrier, normative and interoperable | **gap**, and structurally so: DASH defines no native carrier for click-through metadata **and** no user-triggered event of any kind. Every event fires at a scheduled presentation time, so the callback scheme cannot carry a click that has none. The carrier must be a document-level construct the Player reads at render time and acts on at activation. |

### Governance

| R | Theme | DASH 6th status |
|---|---|---|
| R8 | Justify any addition or omission | **N/A** — spec-authoring obligation. |
| R9 | Minimise net new constructs | **N/A** — spec-authoring obligation; §4 of this document is its input. |
| R10 | Do not recreate a layout system | **N/A** — DASH carries no layout primitives to recreate, and Annex H SRD is deliberately not one (see R26). |

## 3. Gaps detail

Nine structural gaps follow from the matrix.

### G1 — DASH 6th has no non-linear ad construct at all (R14, R17, R22, R26, R27; and the carrier for R4 and R12 on non-linear slots)

The ad machinery of the 6th edition is `InsertPresentation` /
`ReplacePresentation` (§5.16) plus the List MPD profile (§8.14). Both
are **substitutive by definition**: they describe what plays *instead
of*, or *spliced into*, the primary timeline, and while the alternative
renders the main playhead either pauses or advances unrendered in
"listen mode". Neither supports concurrent side-by-side playout,
picture-in-picture, squeezeback layouts, or compositing an ad graphic
over the primary video surface.

Nothing elsewhere in the edition fills that role. Annex H's Spatial
Relationship Description is a tile / ROI metadata framework for
viewport-adaptive streaming. Annex L's
`urn:mpeg:dash:nonlinearplayback:2020` — despite the name — is about
non-linear **playback**: branching narratives in which content Periods
are edges of a directed acyclic graph and a `SelectionInfo` payload
offers the viewer story choices resolved through a callback URL. It
defines no overlay rendering, no banner, no squeezeback, no ad
insertion semantics.

What the spec must add, under the SVTA Ads WG namespace per
[`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md):

- A non-linear **opportunity declaration** in the primary MPD — a slot
  that says "compose this on top of the primary content, do not
  interrupt it", carrying the Publisher's allowed-layout set (R12), the
  duration cap (R4) and the concurrency cap.
- A non-linear **resolution document** carrying the candidates, their
  presentation options (G3), and their tracking (R6 / R13). One
  constraint closes part of this design space before it opens: §8.14
  states that *"List MPDs shall not contain Alternative MPD events"*.
  A resolution document that reuses the List MPD structure therefore
  cannot declare a nested ad opportunity inside itself — an overlay or
  pause window is signalled from the primary MPD and nowhere else.
  UC-08's "the overlay candidate doubles as the pause-ad candidate" has
  to be expressed Publisher-side, not resolution-side.
- The composition rules themselves as Player obligations: one active
  form at a time (R22), forms sequenced in declared order (R14), the
  three-element side-by-side (R26) and the two-element L-shape (R27).

### G2 — No pause-state trigger anywhere in DASH (R16, R21)

Every DASH event is scheduled against the continuous media presentation
timeline, and the client dispatches it when the playhead reaches the
presentation time of the corresponding media sample. A viewer pause is
an out-of-band action on the playhead, and the standard defines no event
or trigger that activates on a pause state. UC-05 and UC-08 therefore
have no DASH primitive to hang from.

The shape the spec must take follows from that asymmetry. What is
declared on the timeline is the **window of validity** (start, end)
during which a pause permits an ad — which a timeline-scheduled
construct expresses natively — while the **trigger** is Player-side and
fires on the pause transition inside that window. The pause-ad lifecycle
(R16) and the admissible presentation surfaces (R21) are then Player
obligations the spec states; DASH contributes only the window's
placement on the timeline. The same timeline-anchored-window plus
off-timeline-trigger split is what Annex L already does for viewer
selection, and is the precedent R8 wants cited.

### G3 — No per-candidate ordered presentation options (R5, R7)

A List MPD sequences the ads the ADS already chose: one Period per ad,
played back-to-back. There is no construct anywhere in the edition in
which a **single** ad candidate offers an **ordered list of alternative
presentation options** and the client renders the first it can satisfy.
That model is what makes UC-09 work — one device-agnostic decision
resolving correctly on D1 through D5 without the ADS or the APS holding
a device matrix (R5.4).

The edition does contain the *semantics* R5 needs, twice, at the wrong
granularity. `Preselection` plus `@selectionPriority` orders preferred
experiences inside one Period, across Representations and Adaptation
Sets — media variants of the same content, not alternative presentations
of one ad. The MPD fallback scheme `urn:mpeg:dash:fallback:2016` orders
whole candidate MPD URLs and states R5's preference rule almost
verbatim: document order is preference order, first is highest. Neither
reaches inside an ad candidate. R8 requires the spec to record that both
were considered and why neither was reused.

What the spec must add: an option-list child on the candidate, each
option pairing a **form** (video / image / HTML, R15) with a **layout**
(R12). Order is XML document order — no priority or ranking attribute,
which also keeps it consistent with the fallback scheme's existing
convention (DP-1, R5.1). The same construct must read correctly when a
candidate carries exactly one option, which is the UC-13 case where the
APS resolved the choice upstream from the Player's declared capabilities
(R29): the Player-visible interface is identical, and nothing in the
document distinguishes "the APS filtered" from "this is all there was".

R7's drop / trim vocabulary rides on the same construct and is likewise
spec-side.

### G4 — Non-AV creatives have no home on the media axis (R15, R24)

Two independent facts close this. First, the profile chain: DR-1 binds
every Representation reached via `<ImportedMPD>` to the SPS profile,
which inherits §7.3 and therefore RFC 4337 — `video/mp4`, `audio/mp4`,
`application/mp4`; DR-5 extends the same restriction to inline
AdaptationSets under a List-MPD-level Period, and per-AdaptationSet
`@profiles` must be a subset of the MPD-level value, so no single
AdaptationSet can be promoted out of it. Second, and more basic: no
profile, annex or clause in the base standard defines carriage of a
static image or an HTML document as a Representation at all.
`Representation` is defined for continuous media streams. There is
nothing to relax, only something absent.

What the spec must add: an explicit DR-6 carrier choice per construct,
recorded in the per-construct classification that Item 8 of
[`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md)
already demands. DR-6(a) foreign-namespace open content is the default
for a one-fetch static asset URL; DR-6(b) Event Stream payload is for
presentation-time-aligned payloads. Wrapping a non-MP4 payload in an
`application/mp4` Representation to satisfy the registry remains an
anti-pattern — it adds no segment-delivery semantics for the underlying
format, which would be an Annex F exercise (DR-4).

### G5 — No metadata carrier, and no user-triggered event for the click (R23, R28)

DASH 6th defines no native MPD field for application-level ad metadata
(`AdSystem`, `AdTitle`, `Advertiser`) nor for click-through metadata.
For R23 that is a low-stakes gap: the carrier is optional on both ends
by design, and a legacy client discarding it breaks nothing.

R28 is the harder half, and the difficulty is not the missing field but
the event model. Every DASH event fires at a scheduled presentation
time; a ClickThrough activation has no presentation time, because it
happens when the viewer acts or never. The callback scheme is therefore
the wrong carrier for click-tracking even though it is the right one for
impression and quartiles (R6). The spec must define the ClickThrough URL
and its click-tracking URL(s) as a document-level construct the Player
reads at render time and fires on activation — normative and
interoperable, unlike R23's best-effort carrier, because UC-11 requires
every conformant Player to behave identically. The edition already
splits these two concerns the same way in Annex L, where the
nonlinear-playback event is anchored to the timeline while the viewer's
selection is resolved off it.

### G6 — No channel for the Player to declare device capability (R29, R3)

UC-13 needs the Player to tell the APS what its device can render so the
APS can resolve the presentation option upstream. The edition defines no
such mechanism, and the three places one might expect it all miss for
different reasons.

The Annex I.4 state vocabulary describes what is *playing* and what
events have *run* — the codecs and bandwidth of the active video and
audio Representations, the active language and protection scheme, CMCD
key values, and per-event execution deltas, durations and counts — not
what the device can render. CMCD (Annex K.3.7) carries operational
delivery state: buffer length, measured and requested throughput,
player state. `ServiceDescription` (Annex K.3) runs the opposite way,
letting the service prescribe consumption targets to the client. And
§I.4's query template is authored by the content author in the MPD, so
its parameter set is fixed at authoring time — which is precisely why
R29 places the reserved parameters outside that mechanism.

What the spec must add: a set of reserved query-parameter names on the
resolution request, each optional, each omitted rather than emptied when
the Player has no value or will not disclose it (R29.2 / R29.3), with
absence meaning **undetermined** rather than unsupported (R29.7), a
vendor-prefix rule for non-reserved names (R29.4), and an APS obligation
to answer without any of them (R29.5). The set must be expressive enough
to separate D1 through D5 (R29.6), which fixes its axes: concurrent
video-decoder count, and which surface types can be composited over
video.

### G7 — Overlap is resolved, fallback is not (R20)

The execution model already delivers the first half of R20 for linear.
Alternative-MPD events go into one execution queue ordered by
presentation time; there is exactly one alternative client, so a second
event falling inside a running alternative presentation is not executed
concurrently; playhead-triggered evaluation is suspended while the
alternative plays; and on return the queue is reset and every event
whose active window has elapsed is discarded unexecuted. That is
first-window-wins, resting on the same device-resource reasoning R22
gives: the edition models one alternative client because one is what a
device can be assumed to afford.

What is missing is the second half. The discarded windows are discarded
unconditionally — nothing makes the drop conditional on the first window
having *succeeded*, and nothing licenses falling through to the next one
when the first cannot be resolved. R20 turns the overlap from a
concurrency case into a declared fallback chain, and DASH has no
construct for that chain at the opportunity level. The nearest machinery
sits at other layers: `BaseURL` failover on an `<ImportedMPD>` retries
the *same* document from a secondary origin, and
`urn:mpeg:dash:fallback:2016` chains candidate MPD URLs — neither chains
two *opportunity windows*.

What the spec must add: the R20 rule stated normatively for the three
families (linear, overlay, pause), including the precise failure
condition that licenses the fallback — the Player falls through only
when it cannot **access** the first window's resolution document
(transport failure, or a final HTTP status other than `200`), and a
`200` carrying no candidates is an answer, not a failure (R30) — plus
the UC-12 test case. The spec must also state how its rule composes with
the existing queue behaviour for the linear family, where the edition
already discards the losing windows unconditionally.

### G8 — The empty-versus-failed distinction exists, is unreportable, and cannot reuse the List MPD shape (R30)

The edition defines a legitimate zero-ad outcome and separates it from a
failure. A resolution whose alternative presentation has duration zero
is not executed and the main presentation continues seamlessly; an
execution *failure* — alternative MPD unavailable or invalid, a List MPD
whose merge yields no media, missing segments — is listed separately,
and the two differ in exactly one observable: a failed execution *"does
not count for the purpose of Event Restrictions"*, leaving the
execute-once counter untouched where a successful one increments it.

That is not enough for R30, for two reasons. The distinction is anchored
on a zero **duration** rather than on a resolution that returned no
candidates, and it lives entirely inside the client's own bookkeeping —
no channel lets an unfilled opportunity be *identified* as unfilled by
anyone but the client. For playback the difference is nil either way
(R5.3, DP-3); what it costs is exactly the identification the SVTA WG
asked for.

A third fact constrains the remedy. The obvious encoding — a `list` MPD
carrying zero Periods — is not available: `Period` cardinality under the
MPD root is 1..N, and a List MPD follows the static MPD schema
constraints, so a zero-Period document is schema-invalid. R30's empty
resolution therefore needs either a degenerate Period that carries no
candidate, or a resolution document shape of its own.

What the spec must add: the normative shape of a resolution document
carrying zero candidates — a document, never an error status and never
an empty body (R30.1) — chosen against the cardinality constraint above,
which is also what makes R20's fallback condition well-defined.

### G9 — The wall-clock derivation exists but is not bound to ads (R19, R25)

DASH's timing model is presentation-time, and the edition already
supplies the conversion R19 needs: `@maxPlayoutRate` and the DASH
Metrics `PlayList` define playback speed relative to normal speed, with
a media interval of duration `DU` rendering in `DU/r` of wall clock at
speed `r`, and an event fires when the playhead reaches its presentation
time whatever the rate. What is missing is the binding: nothing ties an
ad form's on-screen length, or the slot cap it is measured against, to
that derived value — which only becomes load-bearing once an ad shares
the screen with primary content running at a non-1x speed.

R25 is the same concern at the other end, and here the edition
constrains the requirement rather than merely omitting it. The freeze is
already DASH's model — the playhead is the media time rendered at a
given wall-clock time, so on pause it stays static while the live edge
advances — but it is not unbounded: once the pause exceeds
`MPD@timeShiftBufferDepth`, the paused position falls out of the
timeshift buffer and playback resumes from the oldest available segment
or jumps to the live edge. R25 as written promises the freeze holds for
the full duration of the pause.

What the spec must add: a Player obligation that `duration` stays the
single canonical value (DP-1.2) while the wall-clock length is derived
from it, and an explicit statement of which rules operate on which
timebase — cap enforcement (R4) and beacon scheduling (R13) on the
presentation timeline, on-screen behaviour on the derived value. For
R25, the spec must state what happens when the pause outlives the
timeshift buffer, because the pause-ad's dismissal and the Player's
resume-at-live-edge jump then coincide.

## 4. Reuse opportunities

The spec MUST reuse the constructs below before introducing new ones
(R9), and document each reuse or departure inline (R8).

| Existing DASH 6th construct | Reused for | Notes |
|---|---|---|
| `EventStream` + `<Event>` (§5.10) | Every new SGAI opportunity declaration — overlay slot, pause window | The standard authoring vehicle for timeline-anchored signalling. A Player that does not implement the `schemeIdUri` skips the event, which is half of R1. |
| Callback event scheme `urn:mpeg:dash:event:callback:2015` (§4.7 / §5.10.4.5) | All timeline-scheduled tracking beacons (R6, R13) | Reused verbatim; R13.4 forbids a parallel scheme. Beacon URLs ride in the `<Event>` `text()`. Does **not** cover click-tracking, which has no presentation time (G5). |
| List MPD profile `urn:mpeg:dash:profile:list:2024` (§8.14) | The resolution document baseline, linear and non-linear | Already gives declared-order playback (R7's baseline). The non-linear document borrows the structure and adds the option list (G3) and the non-AV carriers (G4). Two hard constraints: *"List MPDs shall not contain Alternative MPD events"*, and `Period` cardinality 1..N, so there is no zero-Period document (G8). |
| `<ImportedMPD>` (§5.3.2.6) | Per-ad sub-MPDs for video creatives | Fine for video; DR-1 binds the target to SPS, which is exactly why it is unusable for image / HTML (G4). |
| `BaseURL` failover on `<ImportedMPD>` (§5.3.2.6.2) | Origin-level robustness for a sub-MPD fetch | Retries the same document from a secondary origin. Not R20's fallback, which chains different *opportunities* — the spec should say so rather than let R20 absorb transport retries. |
| MPD fallback scheme `urn:mpeg:dash:fallback:2016` (§5.11.3) | **Precedent for R5 and R20** | Orders candidate MPD URLs by document order with R5's own rule: *"the content author expresses the preferences of using one of those by the order with the first one having the highest preference"*. Wrong granularity for both (whole MPDs, not options inside a candidate nor opportunity windows), but it is the edition's precedent for document-order-as-preference and for a declared fallback chain. R8 requires the decision to be recorded. |
| `Preselection` (§5.3.11) + `@selectionPriority` (§5.3.7.2) | **Considered and rejected for R5** | Orders preferred experiences within a Period across Representations / Adaptation Sets — media variants of one presentation, not alternative presentations of one ad. Reusing it would put ad-level choice on a media-level construct. |
| `InsertPresentation` (§5.16) | Pre-roll and mid-roll on VOD (UC-01, UC-02) | Forbidden on `MPD@type="dynamic"`; the spec carries this as a Publisher authoring rule. |
| `ReplacePresentation` (§5.16) | Pre-roll / mid-roll on live, and the multi-ad break baseline (UC-01, UC-02, UC-06) | Adds three attributes the insert variant lacks — the resumption offset, the late-execution clip flag, and the start-with-offset flag. Exact spellings pending the pin in open question 7. |
| `@maxDuration` and its trim rule | R4's enforcement baseline | *"If the Alternative Presentation … has a longer duration than specified in this element, it shall be terminated at the end of this duration."* The non-linear slot cap reuses the same name and semantics rather than inventing a second duration vocabulary, per the naming-consistency rule in `../context/06-naming-and-namespaces.md`. |
| Alternative-MPD execution model (§5.16.6: one queue, one alternative client) | R20's first-window-wins half, and R22's rationale | The edition already forbids concurrent alternative presentations and already drops overlapping windows on return. The spec inherits the behaviour and adds only the conditional fallback (G7). |
| `@executeOnce` / `@noJump` / `@skipAfter` on the alternative-MPD event | Slot lifecycle controls the spec need not reinvent | `@executeOnce` bounds re-execution; `@noJump` governs what survives a seek (*"If the value is 1, all events are executed. If the value is 2, only the latest such event is executed"*); `@skipAfter` marks when the rest of a presentation may be skipped. A non-linear slot needing equivalent controls reuses these names and semantics. |
| `status="update"` event lifecycle (§5.16.6) | Updating a slot that is already running, on live | Only the attributes affecting playback duration and resumption point apply to a running event; URL and presentation-time changes do not. |
| `@maxPlayoutRate` (§5.3.7.2) and `PlayList.playbackspeed` (Table D.5) | R19's derivation | The `DU/r` conversion is already the edition's; the spec supplies only the binding to ad on-screen length and cap enforcement (G9). |
| `MPD@timeShiftBufferDepth` | R25's bound | The freeze the requirement describes is DASH's default playhead behaviour, and this attribute is what limits it. The spec states the behaviour at the limit rather than re-deriving the freeze. |
| Foreign-namespace open content (§5.2.1) | Every new SGAI element and attribute (DR-2) | The single normative extension point. DR-3's whole-subtree discard is the authoring lever for what a legacy client sees: sibling placement exposes, nesting hides. |
| Vendor descriptors (§5.8.4.8 / §5.8.4.9) | Alternative carrier for metadata (R23) | Admissible per DR-6(c), but placement is constrained to AdaptationSet / Representation, so it inherits DR-5 unless hosted inside a foreign-namespace parent — at which point it collapses into DR-6(a) with worse readability. |
| Annex L `urn:mpeg:dash:nonlinearplayback:2020` | **Precedent, not carrier** | Not reusable for non-linear ads (G1), but it is the edition's own example of the split R28 and G2 both need: the event sits on the timeline while the viewer's interaction is resolved off it. Cite it as the justification for the ClickThrough carrier's shape and the pause trigger's (R8). |
| Annex H SRD `urn:mpeg:dash:srd:2014` | **Considered and rejected** | Expresses coordinates between spatial objects for tile / ROI selection, not composition of an ad surface over video. Reusing it would both misuse the construct and violate R10. R8 requires this rejection documented inline. |
| Annex I.4 state vocabulary, CMCD (Annex K.3.7), `ServiceDescription` (Annex K.3) | **Considered and rejected for R29** | None carries device rendering capability, and §I.4's template is author-declared. The reserved parameter set is new by necessity, not by preference (G6). |

## 5. Open questions

1. **Shape of the non-linear resolution document.** Extend the List MPD
   structure (Periods plus `ImportedMPD`) or define a separate document
   type under the SVTA namespace? Reuse maximises R9 but inherits the
   §8.14 constraints — no nested alternative-MPD events, and no
   zero-Period document — and forces every non-AV creative through a
   DR-6 carrier. Default position: extend the List MPD structure and
   solve the empty case explicitly (open question 2).
2. **Encoding of the zero-candidate resolution document (R30).** Since a
   zero-Period List MPD is schema-invalid, the empty resolution is
   either a document with one Period that declares no candidate, or a
   distinct document type. The first keeps R9; the second is cleaner to
   read and to report on. Needs a WG decision.
3. **The reserved capability-parameter set (R29).** Which axes it
   contains and how each is written is left open by R29.1 and fixed
   "when the syntax is specified". R29.6 sets the acceptance test: the
   set must tell D1–D5 apart. Needs a WG decision on the concrete names
   and value spaces, and on whether an author-declared §I.4 template and
   the reserved parameters can coexist on one request without collision.
4. **Single-option versus multi-option candidates (R5, UC-09 vs UC-13).**
   Both are conformant and the Player-visible interface is identical, so
   the resolution document does not show whether the APS filtered. Is
   that indistinguishability acceptable, or does the WG want the
   document to record that a filter was applied — for diagnostics, or so
   a Player that cannot satisfy the single option knows it was not the
   only one?
5. **Bound on the R25 freeze.** The freeze holds only while the paused
   position stays inside `MPD@timeShiftBufferDepth`. R25 currently
   promises it for the full duration of the pause. Decide whether R25
   is amended to state the bound, or whether the spec declares the
   pause-ad dismissed when the buffer expires — and what the Player
   does with the pause-ad's pending beacons when the resume is a jump
   to the live edge rather than a resume in place.
6. **Carrier for the pause window (G2).** A §5.2.1 element plus a
   timeline-scheduled window is the default position; Annex F (DR-4) is
   rejected on cost per DR-4's own guidance. Confirm with the WG that a
   window whose trigger is Player-side rather than playhead-side is
   acceptable as an event-stream construct.
7. **Attribute names and sub-clause numbering of the alternative-MPD
   event.** The NotebookLM session for this build returns the
   alternative-MPD event type as carrying `@uri`,
   `@earliestResolutionTimeOffset`, `@serviceDescriptionId`,
   `@maxDuration`, `@executeOnce`, `@noJump` and `@skipAfter`, with
   `@returnOffset`, `@clip` and `@startWithOffset` added by the
   replacement variant, and it places `InsertPresentation` at §5.16.2
   and `ReplacePresentation` at §5.16.3.
   `../context/05-dash-linear-interfaces.md` writes `@url` and
   `@clipDuration` and places the two elements at §5.16.3 and §5.16.4.
   Both cannot be right. Pin the spellings and the clause numbers
   against the published FDIS text before any spec chapter quotes them:
   the spec reuses these names verbatim, so a wrong spelling propagates
   into every example.
8. **Layouts outside the closed R12 set.** ADR 0002 (custom layout with
   a viewport-relative pixel coordinate model) and ADR 0003 (multiview)
   are both `proposed` and scoped to later phases. They sit outside
   R12's closed enumeration, and R10 / OOS-1 forbid a parallel layout
   engine in the core. Confirm they stay out of this edition.
9. **Tracking-only decision entries.**
   `../context/05-dash-linear-interfaces.md` flags that the industry
   convention for a tracking-only VAST `<Ad>` with no media — silent
   skip versus signalled error — could not be resolved against the 6th
   edition source. Under R18.2 this is APS-internal and the spec may
   decline to bind it; R30 now covers the Player-visible half (the
   opportunity resolved to no ads).

## References

- [`../context/01-intro.md`](../context/01-intro.md) — document index
- [`../context/02-actors.md`](../context/02-actors.md) — Publisher / ADS / APS / Player
- [`../context/03-requirements.md`](../context/03-requirements.md) — R1–R30, DP-1..DP-3, OOS-1..OOS-6
- [`../context/04-use-cases.md`](../context/04-use-cases.md) — UC-01–UC-13, device classes D1–D5
- [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md) — linear SGAI baseline
- [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md) — SVTA Ads WG namespace and versioning
- [`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md) — per-construct R1 audit
- [`../context/08-dash-extension-rules.md`](../context/08-dash-extension-rules.md) — DR-1..DR-7, the closed design space
- [`../context/99-glossary.md`](../context/99-glossary.md) — terminology
- FDIS ISO/IEC 23009-1:2025(E), MPEG-DASH 6th edition — clauses cited
  above: §4.7, §5.2.1, §5.3.1, §5.3.2.6, §5.3.7.2, §5.3.11, §5.8.4.8 /
  §5.8.4.9, §5.10, §5.11.3, §5.16, §7.3, §8.12, §8.14, §8.15, Annex D
  (Table D.5), Annex F, Annex H, Annex I.4, Annex K.3, Annex L.

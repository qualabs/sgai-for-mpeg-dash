[GROUNDED_BY=notebooklm]

# DASH 6th edition gap analysis (SGAI for linear + non-linear ads)

This document compares the requirements in
[`../context/03-requirements.md`](../context/03-requirements.md) (R1–R30)
and the use cases in
[`../context/04-use-cases.md`](../context/04-use-cases.md) (UC-01–UC-13)
against what MPEG-DASH 6th edition (ISO/IEC 23009-1, sixth edition)
provides, and identifies what the SGAI specification must add or extend.
It is the bridge between the canonical context and the spec build.

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY) when
stating requirements.

**Grounding.** NotebookLM was queried against the notebook `Streaming
Protocols — DASH, HLS, C2PA, DRM`
(`bb67e20c-9ad1-4a1d-a641-7c7d901f93cb`) for every load-bearing DASH 6th
claim below: the alternative-MPD event attribute set and its XML Schema
declaration; the `ImportedMPD` content model, its profile binding and
the List MPD profile requirements; whether any non-linear ad construct
exists and what `urn:mpeg:dash:nonlinearplayback:2020` (Annex L) does;
whether any construct is triggered by a viewer pause; whether Part 1
defines the carriage of an image or an HTML document as a
Representation, and what §7.3 binds `@mimeType` to; the Annex I
request-parameter element and its state vocabulary, and whether any
client-capability channel exists; the ordered-preference constructs
(`Preselection`, `@selectionPriority`, `urn:mpeg:dash:fallback:2016`);
the failure and zero-duration semantics of an alternative-MPD execution
and the event execution queue; the playback-rate model and the
playhead's behaviour across a user pause of a live presentation; the
callback event scheme; and the `Period` / `AdaptationSet` cardinality
rules. Quoted text is verbatim from those sessions. Claims the notebook
did not confirm are tagged `[inferred]`.

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
| R29 | Player-declared capability parameters on the resolution request | **gap**, confirmed negatively. The edition's upstream channel is Annex I's extended HTTP GET parameterisation (`RequestParam`, `urn:mpeg:dash:urlparam:2025`), but the Annex I.4 state vocabulary carries session state — the `@codecs` / `@bandwidth` of the playing video and audio, selected language, trick-play state, per-event execution counters and deltas, throughput, service location — and contains no parameter for decoder count, image rendering or HTML-overlay support. The query template is authored by the content author in the MPD, so its parameter set is fixed at authoring time by someone other than the Player. CMCD carries delivery state; `ServiceDescription` runs service-to-client. |

### Opportunity declaration

| R | Theme | DASH 6th status |
|---|---|---|
| R4 | Publisher-declared max slot duration, Player-enforced | **partial** — the cap and the trim already exist for the linear slot: `@maxDuration` (`xs:unsignedLong`, default `2251799813685247`, i.e. unbounded) with the §5.16.5.2 rule that an alternative presentation longer than it *"shall be terminated at the end of this duration"*, and a zero value meaning the event is not executed. There is no non-linear slot in DASH at all, so no cap construct for an overlay or pause window; and the "enforce against **actual** rendered length" rule (R4.5) has no DASH anchor even for linear. |
| R12 | Closed IAB ad-type / placement set | **N/A** for the vocabulary (owned by the IAB); **gap** for the carrier — no DASH construct carries an ad-type or visual-placement token, so the Publisher's allowed-layout declaration on the slot is a net new construct. |
| R15 | Creative carriers: video, image, HTML | **partial** — video is native (an ISO-BMFF presentation reached via `<ImportedMPD>`, restricted to the Single-Period Static profile by construction). Image and HTML are a **gap**, and doubly so: the RFC 4337 chain (DR-1 / DR-5) closes the AdaptationSet axis along the ListMPD path, and Part 1 defines no carriage of `image/*` or `text/html` as a Representation at all — Image Adaptation Sets come from the DASH-IF Interoperability Points and ISO/IEC 23009-15, not from the document this spec extends. |

### Selection and ordering

| R | Theme | DASH 6th status |
|---|---|---|
| R5 | Candidates carry ordered presentation options; Player renders the first it can satisfy | **gap** — a List MPD is a *playlist*: Periods played back-to-back, not offered as alternatives. No construct lets one ad candidate carry an ordered list of (form + layout) options. Three constructs express ordered preference and all three are scoped elsewhere: `Preselection` (§5.3.11) combines media components into one experience within a Period; `@selectionPriority` (§5.3.7.2) is a non-binding numeric hint on `RepresentationBaseType` where higher wins — the opposite direction from document order; and `urn:mpeg:dash:fallback:2016` (§5.11.3) chains whole MPD URLs on unrecoverable playout error. R8 requires all three to be considered and the departure documented (see G3). |
| R7 | Honour the resolution document's order | **partial** — declared-order playback is already the List MPD semantics, and the edition already drops an ad Period that fails to resolve and moves to the next one in the list. What is missing is the rest of R7's vocabulary: drop-before-play on declared duration, trim-during-play on actual length, and the prohibition on re-ordering or deduplicating what survives. |
| R30 | Empty resolution distinguishable from failed | **partial** — the edition separates the two at the protocol layer: a no-ad response is a valid `200` carrying a valid MPD (the event resolved) whose alternative presentation duration evaluates to zero, while a failed resolution leaves the event unresolved. But the distinction is anchored on a zero **duration** rather than on a document carrying no candidates, it lives in client-internal bookkeeping with no reporting channel, and the zero-duration outcome triggers the queue fall-through that R20.1 forbids (G7). See G8. |

### Presentation

| R | Theme | DASH 6th status |
|---|---|---|
| R3 | Diverse device classes D1–D5 | **N/A** — DASH models codecs and bandwidth, not concurrent decoder budget or overlay-surface capability; the edition expects capability matching to happen client-side at MPD parsing time. The capability axes R3 separates are what R29's reserved set must express. |
| R16 | Pause-ad lifecycle bound to pause state | **gap** — DASH event processing is driven strictly by media presentation time, and a pause halts playhead movement and with it event evaluation. The edition defines no MPD event, XML element or schema construct triggered by a pause; the only place a pause appears is the Metrics playout log. |
| R19 | Ad playback speed follows primary content | **partial** — the edition already carries the rate model: `@maxPlayoutRate` (§5.3.7.2, default `1`), Annex K's `<PlaybackRate>` `@min` / `@max`, and the Metrics definition of `playbackspeed` as the rate relative to normal forward playback. What is absent is the binding R19 needs: nothing ties an ad form's on-screen length, or a slot cap, to that rate. |
| R21 | Pause-ad fullscreen or partial overlay | **gap** — depends on the pause-ad construct that does not exist (R16). |
| R25 | Pause-ad presentation-time freeze in live content | **partial, and in conflict** — the freeze is already DASH's playhead model (pause halts media time while wall-clock advances), but the edition normatively requires trimming the playhead to the time-shift buffer start once the resumption time falls before it. R25 promises the freeze for the full duration of the pause; past `MPD@timeShiftBufferDepth` the edition does not allow it (see G9). |
| R26 | Side-by-side / double-box with background element | **gap** — the edition provides *"no metadata elements, spatial layout attributes, or rendering schemas"* for compositing. Annex H's Spatial Relationship Description (`urn:mpeg:dash:srd:2014`, and the dynamic variant) is a descriptor on an AdaptationSet or Sub-Representation that positions encoded video tracks inside a shared coordinate system for tiling, ROI and mosaic use cases — not a UI compositor and not an overlay layout facility. Per R10 the spec defers to HTML5 / CSS rather than building one. |
| R27 | L-shape / squeezeback, one full-frame ad creative | **gap** — same as R26. Neither the alternative-MPD events nor the List MPD profile supports concurrent side-by-side playout, picture-in-picture, squeezeback layouts, or compositing an ad graphic over the primary video surface. |

### Interaction and composition rules

| R | Theme | DASH 6th status |
|---|---|---|
| R14 | Sequential non-linear forms within a slot | **gap** — there is no non-linear slot to sequence forms inside. The ordering contract itself is borrowable from the List MPD profile once the slot exists. |
| R17 | Pause-ad priority over overlay | **gap** — depends on the R14 / R16 constructs. |
| R20 | Overlapping same-family windows: first-window-wins with fallback | **partial**, and in conflict. The edition's priority queue already gives first-wins plus fall-through: events ordered by presentation time, Listen Mode suspending main-timeline event processing while an alternative plays, and on a failed execution the client *"immediately falls through and evaluates the next event"*. But it falls through on a **zero-duration** resolution as well, which R20.1 forbids, and it exists only for the linear family (see G7). |
| R22 | At most one active non-linear form | **gap** — DASH has no notion of a concurrently presented ad surface to bound. The edition's own single-alternative-client model is the same reasoning applied to linear, and is the precedent R22 should cite. |

### Tracking

| R | Theme | DASH 6th status |
|---|---|---|
| R6 | Tracking beacon carrier | **full** — the callback event scheme `urn:mpeg:dash:event:callback:2015` (§4.7 / §5.10.4.5) is reused verbatim: an `EventStream` at Period level or an inband `emsg`, on-start dispatch, the client firing an HTTP GET at the event's presentation time and discarding the response without parsing it. That is exactly a beacon. R13.4 forbids a parallel scheme. |
| R13 | ADS-directed beacon schedule, relative timings | **partial** — the carrier is full (R6). The relative-to-ad-presentation timebase falls out of the sub-MPD's own Period timeline, but the obligations R13 adds — the Player executes the schedule it reads, and stops firing at an R4 trim boundary — are spec-side. |
| R23 | Application-level ad metadata carrier | **gap** — DASH 6th defines no native MPD field for `AdSystem`, `AdTitle`, `Advertiser` or comparable creative metadata. Conveyance is via DR-6(a) SVTA-namespaced elements; legacy clients discard the subtree (DR-3). |
| R24 | Non-AV creative asset carrier | **gap** — DR-1 / DR-5 close the AdaptationSet axis. Asset URLs must route through the DR-6 enumeration. DR-7's constraint compounds it: `AdaptationSet` is `0...N` in the schema, but *"at least one Adaptation Set shall be present in each Period unless the value of the `@duration` attribute of the Period is set to zero"*, so an events-only Period of non-zero duration is not a legal carrier either. |
| R28 | ClickThrough carrier, normative and interoperable | **gap**, and structurally so: DASH defines no native carrier for click-through metadata **and** no user-triggered event of any kind. Every event fires at a scheduled presentation time, so the callback scheme cannot carry a click that has none. |

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
are **substitutive by definition**: *"strictly linear, Period-based
replacement or insertion mechanisms where an alternative media
presentation completely replaces or precedes/follows content on the
main presentation timeline"*. The edition provides *"no metadata
elements, spatial layout attributes, or rendering schemas for
compositing overlays on top of active video,
side-by-side / double-box views, squeezeback, or L-shape formats"*, and
no construct for a banner or a pause-triggered ad unit.

Nothing elsewhere in the edition fills that role. Annex H's Spatial
Relationship Description (`urn:mpeg:dash:srd:2014`) is a tile / ROI
metadata framework for viewport-adaptive streaming. Annex L's
`urn:mpeg:dash:nonlinearplayback:2020` — despite the name — is
*"Implementation of Nonlinear Playback"*: interactive-storyline content
modelled as a directed acyclic graph in which each `Period` is an edge
and each node is a viewer decision point, carried by an `EventStream` in
`on receive` dispatch mode whose payload is a `SelectionInfo` element of
`Selection` choices, resolved through an HTTP callback to `@contactURL`.
It defines no overlay rendering, no banner, no squeezeback, no ad
insertion semantics. Where the industry does cover non-linear formats
today is outside DASH, in IAB VAST's `<NonLinearAds>` — which is the
upstream side this spec deliberately does not depend on (R11).

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
presentation time of the corresponding media sample. The consequence is
explicit in the edition: when a viewer pauses, *"playhead-triggered
event processing is inactive because media time stops advancing"*, and
the edition defines no MPD or event construct triggered by the pause.
The pause is visible to the edition in exactly one place — DASH Metrics
records a playback stop with `stopreason="UserRequest"` — which is a
reporting record, not a trigger. UC-05 and UC-08 therefore have no DASH
primitive to hang from.

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

The edition does contain ordered preference, three times, and each is
scoped somewhere else:

- **`Preselection` (§5.3.11)** combines media content components across
  Adaptation Sets into one experience intended for joint decoding and
  rendering — NGA track mixing, LCEVC base plus enhancement layer,
  stereoscopic video. It orders media variants of one presentation, not
  alternative presentations of one ad, and the client is explicitly not
  required to take the first in document order.
- **`@selectionPriority` (§5.3.7.2)** is an author hint on
  `RepresentationBaseType`, default `1`, where *"higher integer values
  express a higher preference over lower numbers"* — the opposite
  direction from document order, and non-binding: the client filters by
  capability first and then picks the highest priority among what
  survives.
- **`urn:mpeg:dash:fallback:2016` (§5.11.3)** is an MPD-level
  descriptor whose `@value` is a whitespace-separated list of
  chained-to MPD URLs, and it states R5's rule almost verbatim —
  *"the content author expresses the preferences of using one of those
  by the order with the first one having the highest preference"* — but
  at the granularity of whole presentations, triggered by an
  unrecoverable playout error rather than by a capability check.

R8 requires the spec to record that all three were considered and why
none was reused.

What the spec must add: an option-list child on the candidate, each
option pairing a **form** (video / image / HTML, R15) with a **layout**
(R12). Order is XML document order — no priority or ranking attribute,
which is both DP-1 and the deliberate departure from
`@selectionPriority`'s numeric, opposite-direction convention (R5.1).
The same construct must read correctly when a candidate carries exactly
one option, which is the UC-13 case where the APS resolved the choice
upstream from the Player's declared capabilities (R29): the
Player-visible interface is identical, and nothing in the document
distinguishes "the APS filtered" from "this is all there was".

R7's drop / trim vocabulary rides on the same construct and is likewise
spec-side.

### G4 — Non-AV creatives have no home on the media axis (R15, R24)

Two independent facts close this. First, the profile chain. The binding
starts at the root: a `Period` carrying an `ImportedMPD` is a *"Linked
Period"* which *"imports its media content from an external MPD, which
is restricted to the Single-Period Static Profile
(`urn:mpeg:dash:profile:sps:2024`)"*. SPS inherits §7.3, which binds
`@mimeType` to the IANA media type registry *"according to IETF RFC
4337"* — `video/mp4`, `audio/mp4`, `application/mp4` (DR-1); DR-5
extends the same restriction to inline AdaptationSets under a
List-MPD-level Period, and per-AdaptationSet `@profiles` must be a
subset of the MPD-level value, so no single AdaptationSet can be
promoted out of it. The edition does carry profiles whose `@mimeType` is
not mp4 — the MPEG-2 TS profiles require `video/mp2t`, and XML subtitle
Representations use `application/ttml+xml` or `text/vtt` — but none of
them is reachable from the ListMPD / `ImportedMPD` chain, precisely
because that chain pins the imported document to SPS and a profile may
only add constraints.

Second, and more basic: Part 1 does not define the carriage of a static
image (`image/jpeg`, `image/png`, `image/webp`) or an HTML document
(`text/html`) as a Representation or Adaptation Set at all — it is
designed for segmented, timed media streams. Image Adaptation Sets exist
in the ecosystem, but they originated in the DASH-IF Interoperability
Points and were standardised in ISO/IEC 23009-15, not in Part 1, which
is the document this specification extends. So there is nothing to relax
on the media axis, only something absent from it.

A third fact narrows where a non-AV carrier can sit even after the
carrier type is chosen. `AdaptationSet` is `0...N` in the schema, but
the edition requires that *"at least one Adaptation Set shall be present
in each Period unless the value of the `@duration` attribute of the
Period is set to zero"* — so the "Period that holds only events and no
media" shape (DR-7) is closed for any non-zero duration.

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

DASH 6th defines no XML element or attribute for application-level
advertising metadata — `AdSystem`, `AdTitle`, `Advertiser`,
`ClickThrough`, `ClickTracking`. The edition's ad machinery
(alternative-MPD events, `ImportedMPD`, period splitting) deals
exclusively with manifest resolution, timeline alignment and segment
fetching; the metadata belongs, in the edition's own division of
labour, to the application-layer ad standards. For R23 that is a
low-stakes gap: the carrier is optional on both ends by design, and a
legacy client discarding it breaks nothing.

R28 is the harder half, and the difficulty is not the missing field but
the event model. The edition defines no event or descriptor triggered by
user interaction: every event, event stream and timed metadata track is
evaluated against the media presentation timeline, and the callback
scheme in particular is on-start dispatch — the client fires its HTTP
GET when the playhead reaches the event's presentation time and then
*discards the response without parsing it*. A ClickThrough activation
has no presentation time, because it happens when the viewer acts or
never. The callback scheme is therefore the wrong carrier for
click-tracking even though it is the right one for impression and
quartiles (R6). The spec must define the ClickThrough URL
and any click-tracking URL(s) accompanying it as a document-level
construct the Player reads at render time and fires on activation —
normative and interoperable, unlike R23's best-effort carrier, because
UC-11 requires every conformant Player to behave identically. Whether a
given ClickThrough carries click-tracking at all is the advertiser's
decision (R28.1); what the carrier must guarantee is that when it does,
both travel together and in the same place. The edition already splits
these two concerns the same way in Annex L, where the
nonlinear-playback event is anchored to the timeline while the viewer's
selection is resolved off it through the callback URL.

### G6 — No channel for the Player to declare device capability (R29, R3)

UC-13 needs the Player to tell the APS what its device can render so the
APS can resolve the presentation option upstream. The edition does carry
an upstream channel — Annex I's extended HTTP GET parameterisation —
but it carries the wrong payload and is authored by the wrong party.

The construct, named precisely, is `RequestParam`
(`ExtendedUrlInfoType`), declared in the main MPD namespace and
signalled by an `EssentialProperty` or `SupplementalProperty` descriptor
with `@schemeIdUri="urn:mpeg:dash:urlparam:2025"`. It carries
`@queryTemplate`, `@useMPDUrlQuery`, `@queryString`,
`@includeInRequests` (default `segment`; the value that scopes a
parameter to an alternative-MPD request is `altmpd`),
`@headerParamSource`, `@sameOriginOnly` and `@header`, and it may sit at
MPD, Period, AdaptationSet, Representation, Preselection or EventStream
level. The 6th edition declares no element named `UrlParamInfo`, which
is the name the linear reference in
[`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
uses; the spec and its examples must carry the edition's name.

The payload first. The Annex I.4 state vocabulary is *"strictly
designed to report dynamic session state (active codecs/bitrates,
playhead seek state, event execution metrics, and network throughput)
rather than static hardware capabilities"*, and it contains no parameter
for the number of hardware video decoders, for image rendering, or for
HTML / DOM overlay rendering support. What
Table I.5 does define is `state:video` and `state:audio` (the `@codecs`
and `@bandwidth` of what is playing), `state:lang#[media]`,
`state:previous-state` (the trick-play state: `normal`, `ff`, `rw`,
`listen`), and the per-event counters `execution-count#[id]`,
`execution-delta#[id]` and `expected-duration#[id]`, plus throughput and
service location. That is what is *playing* and what has *run*, not what
the device can render. The two neighbouring mechanisms miss for their own
reasons: CMCD carries operational delivery state (buffer, throughput,
player state), and `ServiceDescription` runs the opposite way, letting
the service prescribe consumption targets to the client.

The authoring party second. The query template is written by the content
author in the MPD — *"the MPD / Content Author defines the URL query
template in the manifest using the `@queryTemplate` attribute"* — so its
parameter set is fixed at authoring time, by someone who is not the
Player. That is precisely why R29 places the reserved parameters outside
that mechanism: a Player cannot add an axis to a template it did not
write, and the capability it would report is not in the vocabulary the
template can substitute.

What the spec must add: a set of reserved query-parameter names on the
resolution request, each optional, each omitted rather than emptied when
the Player has no value or will not disclose it (R29.2 / R29.3), with
absence meaning **undetermined** rather than unsupported (R29.7), a
vendor-prefix rule for non-reserved names (R29.4), and an APS obligation
to answer without any of them (R29.5). The set must be expressive enough
to separate D1 through D5 (R29.6), which fixes its axes: concurrent
video-decoder count, and which surface types can be composited over
video. The spec must also state how the reserved parameters coexist on
one request with an author-declared `RequestParam` template, since both
land on the same URL.

### G7 — The fallback chain exists for linear, and its trigger condition contradicts R20 (R20)

This gap is narrower — and sharper — than "DASH has no fallback". The
execution model of §5.16.2.2 (*Hypothetical Reference Model of
Alternative MPD Event Processing*) already delivers most of R20 for the
linear family. Alternative-MPD events go into a priority queue `QE`
ordered strictly by presentation time, topmost being the soonest. When
the playhead reaches that time the client executes the topmost event; on
success the main presentation enters *Listen Mode* and playhead event
processing on the main timeline is suspended until the alternative
presentation completes, so no second window is served concurrently. And
on failure the client *"immediately falls through and evaluates the next
event in `QE` order … until an event succeeds or the queue is
exhausted"*. That is
first-window-wins **with** a fallback chain, which is what R20 asks for.

The conflict is in what counts as a failure. DASH falls through on two
conditions — a resolution error **and a zero duration**. R20.1 admits
only the first: the Player *"MUST resort to a subsequent overlapping
window ONLY when it cannot access the resolution document of the first
window"*, and *"a `200` response carrying a resolution document with no
candidates per R30 is accessible — the opportunity resolved, and it
resolved to no ads"*. Under the edition's own model that same opportunity
is a zero-duration alternative presentation, the event is not executed,
and the client falls through to the next window. Same input, opposite
outcome.

Two further limits. The queue and its fall-through are defined for
alternative-MPD events, which exist only for the linear family; R20
governs three families (linear, overlay, pause), and the other two have
no queue to inherit because they have no construct at all (G1). And the
machinery that sits nearest at other layers solves neither: `BaseURL`
alternatives retry the *same* resource from another location, and
`urn:mpeg:dash:fallback:2016` chains whole presentations on unrecoverable
playout error — neither chains two *opportunity windows*.

What the spec must add: R20 stated normatively for the three families,
with the failure condition written explicitly against the edition's —
the Player falls through only when it cannot **access** the first
window's resolution document (transport failure, or a final HTTP status
other than `200`), and a `200` carrying no candidates is an answer, not
a failure (R30). Because that narrows the edition's fall-through rather
than extending it, R8 requires the divergence to be stated inline, and
the spec must say what a Player does for the linear family, where the
baseline queue behaviour and the SGAI rule disagree on the zero-ad case.
UC-12 is the test case.

### G8 — The empty-versus-failed distinction exists at the wrong anchor, and is unreportable (R30)

The edition does separate the two outcomes. A no-ad response is a valid
`200` carrying a syntactically valid MPD — the event resolved — whose
alternative presentation duration evaluates to zero; a failed resolution
leaves the event unresolved, with the HTTP error or timeout recorded.
At the playout layer the two are identical by design: the client
continues the main presentation seamlessly either way.

That is not enough for R30, for three reasons. The distinction is
anchored on a zero **duration**, which is a linear notion — a non-linear
opportunity that resolves to no ads has no alternative presentation
whose duration could be zero. It lives entirely inside the client's own
bookkeeping, so nothing lets an unfilled opportunity be *identified* as
unfilled by anyone other than the client, which is precisely what the
SVTA Advertising WG asked for and what ADR 0005 records. And the
edition's handling of the zero-duration case is to fall through to the
next overlapping event (G7), which R20.1 forbids.

ADR 0005 already fixes the transport: the empty resolution is a
**document carrying no candidates**, never an error status and never an
empty body, because a bodiless response has nowhere to carry the
ADS-declared no-ad notification R13 obliges the APS to express in the
resolution document. What remains open is the document's shape, and one
constraint closes the obvious encoding. `Period` cardinality inside the
MPD is 1..N — the schema declares
`<xs:element name="Period" type="PeriodType" maxOccurs="unbounded"/>`,
and an omitted `minOccurs` defaults to 1 — so a `list` MPD carrying zero
Periods does not validate against `DASH-MPD.xsd`. (The edition does
accommodate a Period-less MPD in one narrow normative note, for live
start-up where *"updates to the MPD are expected in order to provide the
start time of the first Period"*; that is a transient live-authoring
state, not a resolution document shape, and adopting it for R30 would
mean shipping a resolution document that fails schema validation.)
R30's empty resolution therefore needs either a degenerate Period that
carries no candidate, or a resolution document shape of its own.

What the spec must add: the normative shape of a resolution document
carrying zero candidates, chosen against that cardinality constraint,
and stated so that it is the same answer for a linear slot and for a
non-linear one. That shape is also what makes R20's fallback condition
well-defined, since "accessible but empty" is the case the two
requirements share.

### G9 — The rate model exists but is not bound to ads, and the live-pause freeze has a normative limit R25 does not state (R19, R25)

DASH's timing model is presentation-time, and the edition already
supplies the pieces R19 needs. `@maxPlayoutRate` (§5.3.7.2, on
`RepresentationBaseType`, default `1` when omitted at every level)
declares the maximum speed decodable at the same profile and level;
Annex K's `<PlaybackRate>` (`@min` / `@max`) lets the service bound the
speeds a client may use for latency management; and the DASH Metrics
playout log defines `playbackspeed` as the rate relative to normal
forward playback (1.0), with the access engine advancing the playhead in
lockstep with wall-clock time unless a seek, a pause, or a non-nominal
speed command says otherwise. What is missing is the binding: nothing
ties an ad form's on-screen length, or the slot cap it is measured
against, to that rate — which only becomes load-bearing once an ad
shares the screen with primary content running at a non-1x speed.

R25 is the same concern at the other end, and here the edition does not
merely omit: it **contradicts**. The freeze itself is DASH's model —
pausing halts media presentation time while wall-clock time keeps
advancing, so the playhead drifts behind the live edge. But the drift is
bounded by the time-shift buffer, and the edition states the consequence
normatively: if the pause is long enough that the resumption time falls
earlier than the time-shift buffer start, the playhead *is required* to
be trimmed to the oldest available segment; and a resumption point set in
the future, or a seek back to live, is trimmed to the live edge. R25 as
written promises the freeze holds *"for the full duration of the pause"*,
which the edition does not allow past `MPD@timeShiftBufferDepth`.

What the spec must add: a Player obligation that `duration` stays the
single canonical value (DP-1.2) while the wall-clock length is derived
from it, and an explicit statement of which rules operate on which
timebase — cap enforcement (R4) and beacon scheduling (R13) on the
presentation timeline, on-screen behaviour on the derived value. For
R25, the spec must state what happens when the pause outlives the
time-shift buffer, because the pause-ad's dismissal and the edition's
mandatory trim to the buffer start or to the live edge then coincide;
leaving R25 as an unbounded promise would put the spec in conflict with
the baseline rather than on top of it.

## 4. Reuse opportunities

The spec MUST reuse the constructs below before introducing new ones
(R9), and document each reuse or departure inline (R8).

| Existing DASH 6th construct | Reused for | Notes |
|---|---|---|
| `EventStream` + `<Event>` (§5.10) | Every new SGAI opportunity declaration — overlay slot, pause window | The standard authoring vehicle for timeline-anchored signalling. A Player that does not implement the `schemeIdUri` skips the event, which is half of R1. |
| Callback event scheme `urn:mpeg:dash:event:callback:2015` (§4.7 / §5.10.4.5) | All timeline-scheduled tracking beacons (R6, R13) | Reused verbatim; R13.4 forbids a parallel scheme. Beacon URLs ride in the `<Event>` `text()`. Does **not** cover click-tracking, which has no presentation time (G5). |
| List MPD profile `urn:mpeg:dash:profile:list:2024` (§8.14) | The resolution document baseline, linear and non-linear | Already gives declared-order playback (R7's baseline). The non-linear document borrows the structure and adds the option list (G3) and the non-AV carriers (G4). Two profile requirements bound the reuse: *"List MPDs shall not contain Alternative MPD events"* and *"List MPDs shall not contain XLink attributes defined in subclause 5.5"* — remote resolution goes through `ImportedMPD` and nowhere else. |
| `<ImportedMPD>` (§5.3.2.6) | Per-ad sub-MPDs for video creatives | A Period carrying it is a *Linked Period* whose imported document is *"restricted to the Single-Period Static Profile"*. The URL is the element's **text content**, not an attribute (`ImportedMpdType` extends `xs:anyURI` via `xs:simpleContent`), and its one attribute is `@earliestResolutionTimeOffset` (`xs:double`, default `60.0`, in seconds from `PeriodStart`). Fine for video; the SPS binding is exactly why it is unusable for image / HTML (G4). |
| `BaseURL` alternatives and `@serviceLocation` (§5.6) | Origin-level robustness for a sub-MPD or segment fetch | Alternative locations for the *same* resource, with document order as a default the client *"may"* follow and is free to override. Not R20's fallback, which chains different *opportunities* — the spec should say so rather than let R20 absorb transport retries. |
| MPD fallback scheme `urn:mpeg:dash:fallback:2016` (§5.11.3) | **Precedent for R5 and R20** | An MPD-level descriptor whose `@value` is a whitespace-separated list of chained-to MPD URLs, triggered on unrecoverable playout error, with R5's own rule: *"the content author expresses the preferences of using one of those by the order with the first one having the highest preference"*. Wrong granularity for both (whole presentations, not options inside a candidate nor opportunity windows), but it is the edition's precedent for document-order-as-preference and for an error-triggered declared fallback chain. R8 requires the decision to be recorded. |
| `Preselection` (§5.3.11) + `@selectionPriority` (§5.3.7.2) | **Considered and rejected for R5** | `Preselection` combines media components into one jointly decoded experience within a Period; `@selectionPriority` is a non-binding numeric hint where higher wins. Reusing either would put ad-level choice on a media-level construct and, for `@selectionPriority`, invert the ordering convention R5 fixes. |
| `InsertPresentation` (§5.16.3) | Pre-roll and mid-roll on VOD (UC-01, UC-02) | Forbidden on `MPD@type="dynamic"`; the spec carries this as a Publisher authoring rule. |
| `ReplacePresentation` (§5.16.4) | Pre-roll / mid-roll on live, and the multi-ad break baseline (UC-01, UC-02, UC-06) | `AlternativeMPDReplaceEventType` extends `AlternativeMPDEventType` with three attributes the insert variant lacks: `@returnOffset` (`xs:unsignedLong`), `@clip` (`xs:boolean`, default `true`) and `@startWithOffset` (`xs:boolean`, default `false`). |
| `@maxDuration` and its trim rule (§5.16.5.2) | R4's enforcement baseline | `xs:unsignedLong`, default `2251799813685247` (unbounded), with the rule that an alternative presentation longer than the declared value *"shall be terminated at the end of this duration"*. The non-linear slot cap reuses the same name and semantics rather than inventing a second duration vocabulary, per the naming-consistency rule in `../context/06-naming-and-namespaces.md`. |
| `@executeOnce` / `@noJump` / `@skipAfter` / `@serviceDescriptionId` on the alternative-MPD event | Slot lifecycle controls the spec need not reinvent | The alternative-MPD event type already carries `@executeOnce` (`xs:boolean`, default `false`), `@noJump` (`xs:integer`, default `0`), `@skipAfter` (`xs:duration`, default `PT0S`) and `@serviceDescriptionId` (`xs:unsignedInt`). A non-linear slot needing equivalent controls reuses these names and semantics instead of minting new ones. |
| `@earliestResolutionTimeOffset` | The resolution-timing contract on a non-linear slot | Present on both the event (`xs:unsignedLong`, in timescale units, semantically defaulting to 60 s) and on `ImportedMPD` (`xs:double`, seconds, default `60.0`). A non-linear opportunity needs the same "resolve no earlier than" bound, and the name already exists. |
| Alternative-MPD execution model (§5.16.2.2: priority queue `QE`, Listen Mode) | R20's first-wins half, R7's skip-on-failure, and R22's rationale | Events queued by presentation time; the topmost executes; Listen Mode suspends main-timeline event processing while an alternative plays, so nothing runs concurrently; a failed execution falls through to the next event in queue order. The spec inherits the shape and narrows the fall-through condition (G7). |
| `@maxPlayoutRate` (§5.3.7.2), Annex K `<PlaybackRate>`, Metrics `playbackspeed` | R19's rate model | Speed relative to normal forward playback is already the edition's vocabulary, with a declared maximum and service-declared bounds; the spec supplies only the binding to ad on-screen length and cap enforcement (G9). |
| `MPD@timeShiftBufferDepth` and the resumption-time trimming rules | R25's bound | The freeze the requirement describes is DASH's default playhead behaviour, and these rules are what limit it: a resumption time earlier than the buffer start is trimmed to the oldest available segment, and a seek back to live is trimmed to the live edge. The spec states the behaviour at the limit rather than re-deriving the freeze (G9). |
| Foreign-namespace open content (§5.2.1) | Every new SGAI element and attribute (DR-2) | The single normative extension point. DR-3's whole-subtree discard is the authoring lever for what a legacy client sees: sibling placement exposes, nesting hides. |
| Vendor descriptors (§5.8.4.8 / §5.8.4.9) | Alternative carrier for metadata (R23) | Admissible per DR-6(c), but placement is constrained to AdaptationSet / Representation, so it inherits DR-5 unless hosted inside a foreign-namespace parent — at which point it collapses into DR-6(a) with worse readability. |
| Annex L `urn:mpeg:dash:nonlinearplayback:2020` | **Precedent, not carrier** | Not reusable for non-linear ads (G1), but it is the edition's own example of the split R28 and G2 both need: the `EventStream` sits on the timeline in `on receive` dispatch mode while the viewer's interaction is resolved off it through an HTTP callback to `@contactURL`. Cite it as the justification for the ClickThrough carrier's shape and the pause trigger's (R8). |
| Annex H SRD `urn:mpeg:dash:srd:2014` | **Considered and rejected** | Expresses coordinates between spatial objects for tile / ROI selection, not composition of an ad surface over video. Reusing it would both misuse the construct and violate R10. R8 requires this rejection documented inline. |
| Annex I `RequestParam` (`urn:mpeg:dash:urlparam:2025`, `@includeInRequests="altmpd"`) and the I.4 state vocabulary; CMCD; `ServiceDescription` | **Considered and rejected for R29** | `RequestParam` is the edition's channel for putting parameters on an alternative-MPD request, and `@includeInRequests="altmpd"` is what scopes them to it. None of the three carries device rendering capability, and the query template is author-declared. The reserved parameter set is new by necessity, not by preference (G6). |

## 5. Open questions

1. **Shape of the non-linear resolution document.** Extend the List MPD
   structure (Periods plus `ImportedMPD`) or define a separate document
   type under the SVTA namespace? Reuse maximises R9 but inherits the
   §8.14 profile requirements — no Alternative MPD events inside, no
   XLink — and forces every non-AV creative through a DR-6 carrier.
   Default position: extend the List MPD structure and solve the empty
   case explicitly (open question 2).
2. **Encoding of the zero-candidate resolution document (R30).** ADR
   0005 settled the transport: an unfilled opportunity is a document,
   never a status code and never an empty body. What is still open is
   the document's shape, since `Period` cardinality is 1..N and a
   zero-Period List MPD does not validate — a degenerate Period that
   carries no candidate, or a resolution document shape of its own.
   Needs a WG decision.
3. **The reserved capability-parameter set (R29).** Which axes it
   contains and how each is written is left open by R29.1 and fixed
   "when the syntax is specified". R29.6 sets the acceptance test: the
   set must tell D1–D5 apart. Needs a WG decision on the concrete names
   and value spaces, and on how the reserved parameters coexist on one
   resolution request with an author-declared Annex I `RequestParam`
   template without collision.
4. **Single-option versus multi-option candidates (R5, UC-09 vs UC-13).**
   Both are conformant and the Player-visible interface is identical, so
   the resolution document does not show whether the APS filtered. Is
   that indistinguishability acceptable, or does the WG want the
   document to record that a filter was applied — for diagnostics, or so
   a Player that cannot satisfy the single option knows it was not the
   only one?
5. **Bound on the R25 freeze.** The edition normatively trims the
   playhead to the time-shift buffer start once the resumption time
   falls before it, so the freeze cannot hold past
   `MPD@timeShiftBufferDepth`. R25 currently promises it for the full
   duration of the pause, which is a conflict with the baseline rather
   than an extension of it. Decide whether R25 is amended to state the
   bound, or whether the spec declares the pause-ad dismissed when the
   buffer expires — and what the Player does with the pause-ad's
   pending beacons when the resume is a trim to the buffer start or a
   jump to the live edge rather than a resume in place.
6. **Carrier for the pause window (G2).** A §5.2.1 element plus a
   timeline-scheduled window is the default position; Annex F (DR-4) is
   rejected on cost per DR-4's own guidance. Confirm with the WG that a
   window whose trigger is Player-side rather than playhead-side is
   acceptable as an event-stream construct.
7. **Divergence from the edition's fall-through condition (G7).** The
   edition's execution queue falls through to the next overlapping event
   when the topmost one fails **or resolves to zero duration**; R20.1
   forbids the second. The spec must state the divergence inline (R8)
   and decide what a conformant Player does for the linear family, where
   the baseline behaviour and the SGAI rule disagree on exactly the
   zero-ad case R30 exists to make visible.
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
   decline to bind it; R30 covers the Player-visible half (the
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
- ISO/IEC 23009-1, MPEG-DASH 6th edition — clauses cited above: §4.7,
  §5.2.1, §5.3.2.2, §5.3.2.6, §5.3.7.2, §5.3.11, §5.6, §5.8.4.8 /
  §5.8.4.9, §5.10, §5.11.3, §5.16 *Alternative Media Presentations*
  (§5.16.2.2 the execution model, §5.16.3 Alternative MPD Insertion
  Event, §5.16.4 Alternative MPD Replacement event, §5.16.5.2 the
  `@maxDuration` termination rule), §7.3, §8.12, §8.14, §8.15, Annex D,
  Annex F, Annex G (G.22), Annex H, Annex I (I.4, Table I.5), Annex K.3,
  Annex L.

# MPEG-DASH 6th Edition — Gap Analysis vs Use Cases

## Frame

Gap analysis for **SGAI (linear + non-linear) vs the MPEG-DASH 6th
edition baseline**. Maps each of the 6 use cases in
[`../spec/04-use-cases.md`](../spec/04-use-cases.md) — covering both
linear ad breaks and non-linear surfaces — against MPEG-DASH 6th
edition (ISO/IEC 23009-1) to identify (a) what the spec can express
today and how, and (b) what is missing or insufficient for each of
the device classes D1–D5. The output supports **R1** (DASH 6th
edition compliance) by making the gap between the status quo (which
already covers linear SGAI) and the proposed extension (principally
non-linear, plus any linear clarifications surfaced here) explicit. Each claim is grounded with
a section reference of the spec where verifiable; references that
could not be verified are tagged `[inferred]`.

## Method

- **Inputs.** [`../spec/04-use-cases.md`](../spec/04-use-cases.md)
  (UC-01..UC-06), [`../spec/02-actors.md`](../spec/02-actors.md),
  [`../spec/03-requirements.md`](../spec/03-requirements.md),
  project-level context in [`../.project/PROJECT.md`](../.project/PROJECT.md)
  (objective, stakeholders, standards),
  [`../proposal-drafts/2026-05-06-v0.md`](../proposal-drafts/2026-05-06-v0.md).
- **Reference source.** ISO/IEC 23009-1 (MPEG-DASH 6th edition),
  consulted via the NotebookLM "Streaming Protocols — DASH, HLS,
  C2PA, DRM" notebook.
- **Question template.** Each UC analysed against three questions:
  1. Which constructs in DASH 6th edition apply to the scenario?
  2. How would a Player implement the case using only DASH 6th
     edition, in each of D1–D5?
  3. What is missing — i.e. what cannot be expressed or enforced
     with current constructs?
- **Tagging.** Claims tagged `[verified]` if grounded in a
  NotebookLM-identified spec section; `[inferred]` if from general
  DASH knowledge but not cross-checked against the spec text.

## Spec primer (constructs referenced below)

Quick reference for the constructs that this analysis cites, so per-UC
sections can stay concise. All claims here `[verified]` against
ISO/IEC 23009-1 unless tagged otherwise.

- **`InsertPresentation`** *(§5.16, Alternative MPD Insertion Event;
  scheme `urn:mpeg:dash:event:alternativeMPD:insert:2025`)*. Inserts
  an alternative presentation into the main timeline; main playhead
  is paused for the duration of the alternative; resumes from the
  same position when the alternative ends. Designed for VOD / on
  demand (the main timeline halts).
- **`ReplacePresentation`** *(§5.16, Alternative MPD Replacement
  Event; scheme `urn:mpeg:dash:event:alternativeMPD:replace:2025`)*.
  Replaces a portion of the main timeline; main media time keeps
  advancing in the background. Designed for live and VOD. Carries
  `@clip` (whether the cap follows the original schedule or shifts
  with delay) and `@startWithOffset` (start the ad at a calculated
  offset).
- **`@maxDuration`** *(inherited from `AlternativeMPDEventType`,
  §5.16)*. Hard cap on total duration of the alternative
  presentation. Spec mandates **trimming**: "If the Alternative
  Presentation initiated by this event has a longer duration than
  specified in this element, it shall be terminated at the end of
  this duration." Applies to the entire alternative presentation,
  whether single ad or List MPD.
- **List MPD** *(§8.14, ISO Base Media File Format List Profile,
  profile URN `urn:mpeg:dash:profile:list:2024`)*. Specialised MPD
  whose `@type` is `list`; it represents a playlist of multiple ad
  MPDs via `ImportedMPD` elements. XLink is prohibited inside a
  List MPD. Used for back-to-back multi-ad pods.
- **Earliest Resolution Time (`@earliestResolutionTimeOffset`)**
  *(§5.16)*. Lets the Player resolve the ADS URL ahead of the
  scheduled `presentationTime`, to randomise / spread ADS load.
- **Supplementary Video Services / Preselection**
  *(§5.8.5.16, scheme `urn:mpeg:dash:supv:2022`)*. Picture-in-
  picture composition of two video bitstreams via a `Preselection`
  element grouping a Main and a Partial Adaptation Set. **Static
  MPD-authoring construct**: cannot be injected via SGAI at runtime,
  and only handles linear video codecs (no images, no HTML).
- **Extended HTTP GET parametrisation** *(§I.4 / Annex I.4)*.
  Mechanism for the Player to append state parameters to ADS URL
  requests, configured via `ExtUrlQueryInfo` / `UrlParamInfo` with
  `@includeInRequests="altmpd"` and a vocabulary scheme
  `urn:mpeg:dash:state:<suffix>`. The vocabulary (per Table I.5)
  is restricted to media-stream descriptors and event-execution
  telemetry: `video` (codec+bandwidth), `audio` (codec+bandwidth),
  `lang#[audio|text]` (BCP-47), `encryption`, `cmcd#[key]` (CMCD
  telemetry keys), `execution-delta#[id]`, `expected-duration#[id]`,
  `execution-count#[id]`, and `previous-state` (normal/ff/rw/listen).
  No key in the vocabulary expresses device-rendering capabilities
  such as decoder count, image-overlay surface, or HTML-overlay
  surface — the dimensions that drive the D1–D5 distinction.
- **Callback Event scheme**
  *(`urn:mpeg:dash:event:callback:2015`)*. Standard in-MPD event
  for firing tracking beacons at presentation-time offsets.
- **Annex L "Implementation of Nonlinear Playback".** Defines
  *interactive storyline branching* (e.g. choose-your-own-adventure
  Period selection). Not a non-linear-ad mechanism in the SGAI
  sense; the name overlaps but the semantics are unrelated.

The spec offers **no construct** for: overlay ads on top of running
primary content, pause-triggered (action-triggered) ads, slot-level
declaration that multiple ad TYPES are acceptable, broadcaster-
declared layout constraints (banner, L-shape, side-by-side, etc.),
or ad candidates carrying multiple alternative renderable forms
(video / image / HTML for the Player to choose from). All of these
are absent from MPEG-DASH 6th edition.

## Per-use-case analysis

### UC-01 — Slot at start of session

**Scenario recap:** Pre-roll ad replaces the first frames of the
session before the primary content begins. Linear-only, bounded
duration.

**What DASH 6th edition can express today (the broadcaster intent
and ADS response side):**
A pre-roll is a textbook linear SGAI case fully covered by §5.16.
The broadcaster places an `InsertPresentation` event at
`presentationTime="PT0S"` on the main MPD, with a `@uri` pointing
at the ADS, and `@maxDuration` set to the slot cap. The Player
resolves the URL, receives back either a single-period MPD (one ad)
or a List MPD (§8.14) for a pod, and plays it before joining the
main presentation. Annex G.23 specifically illustrates this pattern
("Insert Preroll at the beginning of a live content"). *(ISO/IEC
23009-1, §5.16, §8.14, Annex G.23) [verified]*.

**Per-device gap analysis:**

#### D1 — Top-tier
- **Status:** Fully covered.
- **What works:** `InsertPresentation` + `@maxDuration` express the
  broadcaster intent. The Player validates duration against
  `@maxDuration`; the spec's trimming rule (§5.16) covers the
  overrun case automatically.
- **What is missing:** Nothing for this device class on this
  scenario.

#### D2 — Dual-decoder, no overlay
- **Status:** Fully covered. **Same as D1 on this scenario** —
  linear-only ads are sequential, do not need overlay surfaces, and
  the second decoder is irrelevant.

#### D3 — Single-decoder, image and HTML capable
- **Status:** Fully covered. **Same as D1 on this scenario** — a
  single decoder is sufficient because the ad and the primary
  content play sequentially, not concurrently.

#### D4 — Single-decoder, image only
- **Status:** Fully covered. **Same as D1 on this scenario.**

#### D5 — Worst case (single decoder, no overlay)
- **Status:** Fully covered. **Same as D1 on this scenario.** R1
  graceful degradation also holds: a Player that does not understand
  the event ignores it and starts the primary content directly.

**Notes / open questions for the spec design:**
- None — UC-01 is the canonical case the existing 6th edition
  mechanism was designed for.

### UC-02 — Mid-content slot

**Scenario recap:** Linear ad replaces a bounded span of primary
content mid-stream and transitions back at (or near) the slot
position.

**What DASH 6th edition can express today:**
Mid-roll is the second canonical case for §5.16. Live workflows use
`ReplacePresentation` (main media time keeps advancing in the
background, so the timeline lands at the right place when the ad
ends); VOD workflows use `InsertPresentation`. `@maxDuration` caps
the slot. `@returnOffset` (on `ReplacePresentation`) controls where
the main timeline resumes. *(ISO/IEC 23009-1, §5.16) [verified]*.

**Per-device gap analysis:**

#### D1 — Top-tier
- **Status:** Fully covered.
- **What works:** `ReplacePresentation` / `InsertPresentation` +
  `@maxDuration` cover broadcaster intent. The second decoder, if
  used to pre-buffer the ad, is a Player implementation detail and
  not a spec-level concern.
- **What is missing:** Nothing.

#### D2 — Dual-decoder, no overlay
- **Status:** Fully covered. **Same as D1.** Slot is linear-only;
  no overlay needed.

#### D3 — Single-decoder, image and HTML capable
- **Status:** Fully covered. **Same as D1.** Sequential rendering
  on the single decoder is fine.

#### D4 — Single-decoder, image only
- **Status:** Fully covered. **Same as D1.**

#### D5 — Worst case
- **Status:** Fully covered. **Same as D1.** Graceful degradation
  for legacy Players holds (R1).

**Notes / open questions for the spec design:**
- None — UC-02 is the canonical mid-roll case for the existing 6th
  edition mechanism.

### UC-03 — Multi-ad break

**Scenario recap:** Mid-content slot filled by N ads back-to-back,
with no primary content between them; total break duration bounded.

**What DASH 6th edition can express today:**
The List MPD (§8.14) is exactly the construct for this scenario.
The broadcaster declares one `ReplacePresentation` (or
`InsertPresentation`) event with `@uri` pointing at the ADS; the
ADS returns a List MPD whose Periods reference ad MPDs via
`ImportedMPD`. `@maxDuration` on the event applies to the **entire
break sum**, not to a single ad. The spec resolves the open
question raised in UC-03's Notes: per §5.16, when the sum of ad
durations exceeds `@maxDuration`, the Player **terminates playback
at the cap** (trim, not fail-closed). *(ISO/IEC 23009-1, §5.16,
§8.14) [verified]*.

**Per-device gap analysis:**

#### D1 — Top-tier
- **Status:** Fully covered.
- **What works:** List MPD with N `ImportedMPD` entries +
  `@maxDuration` on the parent event express the broadcaster intent
  and the Player behaviour completely. The second decoder may
  pre-buffer ad N+1 while ad N plays — implementation detail, not a
  spec gap.
- **What is missing:** No way to declare a *non-trim* policy
  (fail-closed; trim-and-skip-last-ad) at the broadcaster's
  discretion. The spec hardwires *trim at cap*. UC-03's Notes flag
  this as desirable but are silent on whether the proposal needs to
  take a position. **Tagged as a soft gap** — the spec covers the
  scenario but with one fixed overrun policy.

#### D2 — Dual-decoder, no overlay
- **Status:** Fully covered. **Same as D1 on this scenario.**

#### D3 — Single-decoder, image and HTML capable
- **Status:** Fully covered. **Same as D1.** Sequential rendering
  on one decoder; no pre-buffering of ad N+1.

#### D4 — Single-decoder, image only
- **Status:** Fully covered. **Same as D1.**

#### D5 — Worst case
- **Status:** Fully covered. **Same as D1.**

**Notes / open questions for the spec design:**
- The proposal does not need to redesign multi-ad break handling —
  §8.14 already covers it. If the proposal wants to surface the
  policy choice (trim / fail-closed / play-until-cap-and-cut) as a
  broadcaster knob, it would be a *delta on top of* the existing
  List MPD machinery.

### UC-04 — Coexisting overlay

**Scenario recap:** Ad surface composited over the primary content
without interrupting it. Allowed-layouts list (banner, corner,
L-shape, side-by-side, sidebar, …) declared per-slot; bounded
duration; bounded concurrency.

**What DASH 6th edition can express today (the broadcaster intent
and ADS response side):**
The 6th edition has no construct that fits this scenario. The
Alternative MPD events (§5.16) are designed as sequential timeline
takeovers — once the alternative starts, "the main Media
Presentation shall not be displayed during the playback of the
alternative" — so they cannot represent an overlay that runs
**concurrently** with the primary content. The closest adjacent
mechanism is Supplementary Video Services / Preselection (§5.8.5.16,
`urn:mpeg:dash:supv:2022`), which composes two video bitstreams in
a picture-in-picture arrangement; but Preselection is a **static
MPD-authoring** construct (cannot be dynamically injected via SGAI)
and is restricted to linear video codecs (no images, no HTML).
Annex L's "Nonlinear Playback" is unrelated — it describes
interactive storyline branching, not non-linear ads. *(ISO/IEC
23009-1, §5.16, §5.8.5.16, Annex L) [verified]*.

There is also no construct for the broadcaster to declare an
allowed-layouts list (banner / L-shape / side-by-side / etc.) for a
slot, no construct for a maximum-overlay-duration or
maximum-concurrent-overlays cap, and no construct for an ad
candidate to carry **multiple renderable forms** (video / image /
HTML) so the Player can pick the highest-fidelity form its device
supports. The Spatial Relationship Description scheme
(`urn:mpeg:dash:srd:2014`) expresses 2D regions of interest within a
single video reference space, not advertising-layout constraints.
*(ISO/IEC 23009-1, SRD scheme) [verified]*.

**Per-device gap analysis:**

#### D1 — Top-tier
- **Status:** Not covered.
- **What works:** Nothing in the SGAI side of the spec. A
  broadcaster could statically author a Preselection in the main
  MPD that composes a secondary video over the primary, but that is
  authoring-time, not server-decided, and only handles video — not
  image or HTML overlays.
- **What is missing:** (a) a non-linear / overlay event in §5.16
  alongside Insert/Replace; (b) layout-constraint vocabulary on the
  broadcaster event (banner, L-shape, side-by-side, …); (c) a
  resolution-document schema that carries the overlay's
  spatial+temporal definition (analogous to List MPD but for
  overlays); (d) a multi-form ad candidate so D1 can pick HTML over
  image over video by ADS / client priority hints.

#### D2 — Dual-decoder, no overlay capability
- **Status:** Not covered.
- **What works:** Same as D1 — nothing in SGAI. The picture-in-
  picture Preselection is the *only* native compositing tool, but
  is static and video-only.
- **What is missing:** Same gaps as D1, plus: there is no way for
  the broadcaster to declare *side-by-side* as an allowed (or
  forbidden) fallback layout in the slot, which is the lever D2
  needs per UC-04 to render or skip. The Player has no spec-level
  knob to "promote" a candidate to side-by-side, and even if it
  did, it would have no way to cross-check that the broadcaster
  permits it on this slot (R2 violation).

#### D3 — Single-decoder, image and HTML capable
- **Status:** Not covered.
- **What works:** Same as D1 — nothing in SGAI. Preselection
  doesn't apply (single decoder).
- **What is missing:** Same gaps as D1. UC-04 D3 specifically
  requires the multi-form mechanism (the Player needs to skip the
  video form and pick HTML or image) — which the spec does not
  define.

#### D4 — Single-decoder, image only
- **Status:** Not covered.
- **What works:** Nothing.
- **What is missing:** Same gaps as D1, with the additional
  observation that R6's "skip the candidate, try the next, decline
  the slot if none renderable" walk has no spec-level vocabulary to
  operate over (because there is no slot construct, no candidate
  list, no per-candidate forms list).

#### D5 — Worst case
- **Status:** Not covered.
- **What works:** Nothing.
- **What is missing:** Same gaps as D1. The spec has no notion of
  "decline the slot gracefully" as a legitimate Player outcome at
  the slot level, because there is no slot construct in the first
  place. R1 graceful degradation only covers "Player ignores
  unknown event" — it does not cover "Player understands the slot
  but no candidate is renderable on this device".

**Notes / open questions for the spec design:**
- UC-04 is where the proposal's surface area concentrates. The
  proposal must introduce: a non-linear slot event, a layout-
  constraint vocabulary on that event, a resolution document for
  overlay candidates, and a multi-form candidate model.

### UC-05 — Hybrid linear + concurrent overlay

**Scenario recap:** Single break that combines a linear take-over
ad with a concurrent overlay composited on top of it (e.g. branding
banner during the linear ad). Two independently-selected portions.

**What DASH 6th edition can express today:**
The spec **explicitly forbids** what this scenario requires.
§5.16's `ReplacePresentation` semantics state that during the
alternative presentation the main Media Presentation "shall not be
displayed", and there is no construct that allows two ad
presentations to render concurrently on different surfaces during
the same break. The Alternative MPD mechanism is strictly a
sequential takeover; it has no concept of a secondary concurrent
presentation. Preselection's picture-in-picture (§5.8.5.16) is the
only native multi-stream-on-screen primitive in the spec, and it
operates inside a single MPD — it cannot be assembled at runtime
from two independent ADS responses. *(ISO/IEC 23009-1, §5.16,
§5.8.5.16) [verified]*.

There is also no construct for a broadcaster to declare a slot
where multiple ad **types** (linear AND non-linear together) are
permitted; each event is bound to a specific `schemeIdUri` that
mandates a single processing semantics, and the slot type is fixed
at MPD-authoring time — the Player cannot be given a choice of
types to fulfil. *(ISO/IEC 23009-1, event semantics; §5.10 event
model) [verified]*.

**Per-device gap analysis:**

#### D1 — Top-tier
- **Status:** Not covered.
- **What works:** Nothing for the *combined* hybrid. The linear
  portion alone is `ReplacePresentation` (UC-02). The overlay
  portion in isolation is the UC-04 gap. The *concurrence of the
  two on the same break* is the gap unique to UC-05.
- **What is missing:** A way to declare a single break with two
  concurrent components and have each independently resolved by the
  ADS. Equivalently: a way for a non-linear / overlay event to
  *target the timeline of an ongoing linear ad* rather than the
  primary content.

#### D2 — Dual-decoder, no overlay capability
- **Status:** Not covered (linear-only fallback unspecified at the
  spec level).
- **What works:** The linear portion alone uses
  `ReplacePresentation`.
- **What is missing:** No spec mechanism to declare to the Player
  *"satisfy the linear portion only and decline the overlay
  portion"* as a legitimate degradation path; the broadcaster has
  no slot-level construct that even contemplates the overlay
  portion existing.

#### D3 — Single-decoder, image and HTML capable
- **Status:** Not covered. **Same gap as D2 on this scenario** —
  the device renders only the linear portion. The Player has no
  spec-level construct describing the hybrid break in the first
  place.

#### D4 — Single-decoder, image only
- **Status:** Not covered. **Same gap as D2 on this scenario.**

#### D5 — Worst case
- **Status:** Not covered. **Same gap as D2 on this scenario** —
  linear ad plays, no overlay.

**Notes / open questions for the spec design:**
- The proposal must decide whether hybrid breaks are a first-class
  scenario (separate construct, two components) or modelled as two
  independent slot events with overlapping presentation windows. The
  scenario also surfaces a cross-portion question UC-05 already
  notes (advertiser-X-suppresses-overlay) that has no analogue in
  the existing spec.
- The Player on D3/D4 with HTML/image capability can in principle
  composite an overlay on top of a linear ad video using a single
  decoder; whether the spec should permit this remains open in
  UC-05.

### UC-06 — Pause-triggered ad

**Scenario recap:** Ad opportunity not anchored to the timeline;
fires when the user pauses; ad lives on top of the paused frame;
dismissed when the user resumes.

**What DASH 6th edition can express today:**
The spec has **no construct** for state-triggered or action-
triggered ad opportunities. §5.10.1 explicitly defines events as
*timed*: "each event starts at a specific media presentation time
and may have a duration", and an event becomes active when the
playhead reaches its `presentationTime`. There is no `presentation-
time` value that means "when the user pauses", and no event type
keyed to a player state transition. *(ISO/IEC 23009-1, §5.10.1)
[verified]*.

The overlay-related gaps from UC-04 (no overlay event, no allowed-
layouts vocabulary, no overlay resolution document, no multi-form
candidates) all also apply here, since a pause ad lives on top of
the paused frame and shares the overlay-rendering pipeline.

**Per-device gap analysis:**

#### D1 — Top-tier
- **Status:** Not covered.
- **What works:** Nothing — there is no spec mechanism even to
  declare the pause-triggered slot exists.
- **What is missing:** (a) An event whose activation condition is a
  Player state transition (pause), not a presentation-time match.
  (b) A resolution document schema for the pause overlay candidate
  set. (c) The same multi-form / layout-constraint vocabulary that
  UC-04 needs.

#### D2 — Dual-decoder, no overlay capability
- **Status:** Not covered. **Same primary gap as D1.** UC-06's
  device-specific question (whether D2's overlay-capability gap
  also applies on top of a paused frame) has no spec hook to attach
  to, because there is no pause-ad construct to begin with.

#### D3 — Single-decoder, image and HTML capable
- **Status:** Not covered. **Same primary gap as D1.** UC-06's
  open question on whether the single decoder can be re-tasked to
  play a video form on top of a paused primary frame is downstream
  of the spec's lack of any pause-ad construct.

#### D4 — Single-decoder, image only
- **Status:** Not covered. **Same primary gap as D1.**

#### D5 — Worst case
- **Status:** Not covered. **Same primary gap as D1.** R1 graceful
  degradation does not apply directly, because there is no event in
  the main MPD for a legacy Player to ignore — the trigger is a
  player-state transition, not a manifest event.

**Notes / open questions for the spec design:**
- UC-06 introduces a new kind of trigger (state-transition) that is
  qualitatively different from the timeline-events architecture of
  ISO/IEC 23009-1. The proposal must decide whether to extend §5.10
  with a state-triggered event subtype, or model pause-ads as a
  separate first-class construct outside the EventStream model.
- Pre-fetch vs on-pause-fetch (a UC-06 open question) is downstream
  of that primary structural decision and cannot be resolved
  against current spec text.

## Summary matrix

| UC | Scenario | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|---|
| UC-01 | Slot at start of session | Fully covered | Fully covered | Fully covered | Fully covered | Fully covered |
| UC-02 | Mid-content slot | Fully covered | Fully covered | Fully covered | Fully covered | Fully covered |
| UC-03 | Multi-ad break | Fully covered (soft gap: trim policy hardwired) | Fully covered (soft gap) | Fully covered (soft gap) | Fully covered (soft gap) | Fully covered (soft gap) |
| UC-04 | Coexisting overlay | Not covered (no overlay event, no layout vocab, no multi-form candidates) | Not covered (same gaps + no side-by-side declaration mechanism) | Not covered (same gaps; multi-form needed for image/HTML pick) | Not covered (same gaps; R6 walk has no spec vocabulary) | Not covered (same gaps; "decline-the-slot" outcome has no spec status) |
| UC-05 | Hybrid linear + overlay | Not covered (no concurrent ad presentations in spec) | Not covered (no slot-level "linear-only fallback" expressible) | Not covered (same gap as D2) | Not covered (same gap as D2) | Not covered (same gap as D2) |
| UC-06 | Pause-triggered ad | Not covered (no state-triggered events in spec) | Not covered (same primary gap as D1) | Not covered (same primary gap as D1) | Not covered (same primary gap as D1) | Not covered (same primary gap as D1) |

## Top gaps (consolidated)

These are the gaps that recur across multiple UCs and devices. They
are the surface area the proposal must cover to satisfy R1 (DASH 6th
edition compliance via extension, not breakage) for the non-linear
scenarios.

1. **No overlay / non-linear ad event.** §5.16's
   `InsertPresentation` and `ReplacePresentation` are sequential
   timeline takeovers; the spec mandates that during the alternative
   presentation "the main Media Presentation shall not be displayed"
   *(ISO/IEC 23009-1, §5.16) [verified]*. There is no construct that
   declares an ad surface to be composited *on top of* running
   primary content. Affects UC-04, UC-05, UC-06.
2. **No state-triggered (pause / action) ad opportunity.** §5.10.1
   ties events strictly to `presentationTime` on the media timeline
   *(§5.10.1) [verified]*. A pause-triggered slot has no spec
   surface to land on. Affects UC-06.
3. **No concurrent ad presentations.** Even with the existing
   §5.16 mechanism, a Player cannot be told "play these two MPDs
   simultaneously on different surfaces". Affects UC-05; without
   this, hybrid linear+overlay breaks cannot be expressed at all.
4. **No multi-form ad candidate model.** An Alternative MPD event
   resolves to a single `@uri` returning a single alternative MPD
   *(ISO/IEC 23009-1, §5.16) [verified]*. There is no provision for
   one candidate to expose video / image / HTML alternatives so the
   Player picks the form its device can render. Affects UC-04, UC-05
   (overlay portion), UC-06; this is the lever R6 needs across the
   device classes.
5. **No broadcaster-declared layout-constraint vocabulary on
   slots.** No way for the Broadcaster to declare "this slot
   accepts banner and side-by-side but not L-shape" inside an MPD
   event. SRD (`urn:mpeg:dash:srd:2014`) does not fill this gap —
   it describes regions of interest within a single video reference
   space, not advertising layouts *(SRD scheme) [verified]*. Affects
   UC-04, UC-05, UC-06; without it, R2's "Player validates against
   broadcaster constraints" has no constraints to validate against.
6. **No spec status for "decline the slot" as a Player outcome.**
   R1 graceful degradation today only covers "legacy Player ignores
   unknown event". It does not cover "Player understands the slot
   but no candidate has a renderable form on this device" — the
   D4/D5 outcome on UC-04 and UC-06. The proposal must promote
   "decline" to a first-class outcome that is not an error.

The device-capability hint mechanism in §I.4 (`ExtUrlQueryInfo` /
`UrlParamInfo` with `@includeInRequests="altmpd"`, vocabulary scheme
`urn:mpeg:dash:state:<suffix>`) *(ISO/IEC 23009-1, §I.4) [verified]*
is **not** a substitute for any of the above. The §I.4 vocabulary
(per Table I.5) is restricted to media-stream descriptors and
event-execution telemetry: `video`, `audio`, `lang#`, `encryption`,
`cmcd#[key]`, `execution-delta#[id]`, `expected-duration#[id]`,
`execution-count#[id]`, `previous-state`. None of these express
device-rendering capabilities such as decoder count, image-overlay
surface, or HTML-overlay surface — the dimensions that drive the
D1–D5 distinction. Reviewers who wonder "what about §I.4 / CMCD?"
should find the explicit explanation here.

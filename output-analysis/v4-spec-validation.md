[GROUNDED_BY=spec-only]

# Spec validation — v4 (2026-05-14)

Built against:
- spec: `../output/v4-sgai-spec.md` (2245 lines)
- context/ at git SHA: `81e1215` (working tree includes uncommitted
  edits to `context-analysis/*.md` and the new `output/v4-sgai-spec.md`)
- analysis inputs: `../context-analysis/dash-gap-analysis.md`,
  `../context-analysis/conformance-assertions.md`,
  `../context-analysis/error-semantics.md`,
  `../context-analysis/uc-coverage-matrix.md`,
  `../context-analysis/iab-ad-templates.md`

Mode: independent peer review by a fresh subagent. No NotebookLM
grounding requests issued; validation compares the v4 spec text
against `context/` and `context-analysis/` as the authoritative
source.

Delta against v3 (for reviewer orientation, non-normative): v4
closes v3's G-2 (`<svta:Concurrency @max>` enforcement — now
`maxConcurrent` attribute mandatory =1 plus §4.4.7 serialisation),
G-3 (form-level `@duration` now Required on every
`<svta:RenderableAsset>`; §8.6 defines image-form intrinsic
duration), G-8 (dual-form fallback references removed), and the
SGAI-side leg of v3's G-1 / A-4 (the new `<svta:OverlayPresentation>`
and `<svta:PauseAdPresentation>` declare `@earliestResolutionTimeOffset`
in `<EventStream>@timescale` units with an inline NOTE flagging the
divergence from baseline `<ImportedMPD>`). It also collapses v3's
heavier syntax (`<svta:Concurrency>`, `<svta:Exclusions>`,
`<svta:Pair>`, `<svta:Metadata>`) into attribute-on-event metadata
and a small set of children (`<svta:Click>`, `<svta:UniversalAdId>`).
The issues below are residual or v4-introduced.

---

## Gaps (8)

Things the spec defines but for which `context/` does not provide
enough information for a conformant implementation to ship
deterministically.

### G-1. No normative ADS obligation to author non-linear beacon `presentationTime` in the slot-window time base

- **Spec sections needing it**: §4.3 (A-1..A-7), §4.4.6, §5.5.2,
  §5.5.4, §7.5.
- **What context is missing**: `context/03-requirements.md` R13.2
  is a Player SHOULD: "the Player SHOULD fire quartile beacons
  timed against the Broadcaster-declared overlay window, not
  against the ad's internal duration." But §5.5.2 explicitly
  classifies "Inside the Overlay Resolution Document, as a child
  of `<svta:RenderableAsset>`" as the **preferred** placement and
  ties its timing reference to "the Broadcaster-declared overlay
  window". This obligation falls structurally on whoever authors
  the beacons inside the resolution document — the ADS — yet
  §4.3 A-4 ("Carry ad-tracking beacons inside the resolution
  document … using `urn:mpeg:dash:event:callback:2015`") makes no
  statement about the time base the ADS MUST use. The Player has
  no normative recourse against an ADS that emits beacons keyed
  to the ad's intrinsic duration: §4.4.6 says fire at the
  positions the carrier declares; §7.5 reiterates the slot-window
  expectation but does not give the Player a remap permission.
  Result: a non-remapping ADS silently mis-fires quartile beacons
  and no actor is non-conformant.
- **What an implementer does today**: the ADS either guesses the
  intended time base, or the Player re-implements the remap
  unilaterally and risks contradicting §4.4.6's "fire at the
  positions declared" semantics. v3's G-5 carries forward
  unchanged.

### G-2. Click-through interaction is defined but the trigger event is not

- **Spec sections needing it**: §5.6.1 (`<svta:Click>` `@through`
  / `@trackingUrl`), §4.4 Player obligations, §7 Expected
  behaviour.
- **What context is missing**: §5.6.1 says the Player "opens
  this URL via the host environment's URL-opening mechanism" and
  fires `@trackingUrl` "when the viewer interacts with the ad",
  but no chapter binds "viewer interaction" to a concrete trigger
  surface: which device class can interact, which gesture / button
  / remote event qualifies, whether the interaction is allowed
  during a linear ad take-over, and whether it triggers a fall
  through of the slot. `context/04-use-cases.md` enumerates D1..D5
  rendering capabilities (decoders, image overlay, HTML overlay)
  but no interaction surface. `context-analysis/iab-ad-templates.md`
  notes interactivity is "delegated to SIMID and QR codes per the
  IAB document" and is *non-normative* — but the spec ships
  `<svta:Click>` as a normative metadata carrier and §4.4 has no
  matching obligation.
- **What an implementer does today**: clicks on CTV remotes vs
  mobile gestures vs web pointer events are implementation-defined.
  Two Players on the same device class will diverge on (a) whether
  to surface the click, (b) when to fire `@trackingUrl`, (c)
  whether to abort the ad on click. Per-Player divergence is
  outside the conformance surface.

### G-3. Pause-ad dismissal on viewer resume is informal

- **Spec sections needing it**: §5.1.4 attribute table for
  `<svta:PauseAdPresentation>`, §4.4 Player obligations, §7.4
  compositing rules, Annex E.
- **What context is missing**: `context/04-use-cases.md` UC-05
  prose ("when the user resumes playback, the overlay is
  dismissed") and Annex E.4 ("dismissed on resume") describe the
  intended behaviour, but no normative section of the spec carries
  a "Player MUST dismiss the pause-ad when the viewer resumes
  primary playback" rule. §5.1.4 attribute table defines
  `maxDuration` ("applied from the moment the ad becomes visible
  until automatic dismissal") and `triggerMode` but no dismissal
  trigger besides the cap. §4.4 has no P-N item for resume-driven
  dismissal. §4.4.7 single-form concurrent rendering forbids two
  forms simultaneously but does not say the pause-ad's lifecycle
  is tied to the pause state.
- **What an implementer does today**: dismisses on resume (the
  obvious reading) — but a stricter implementer reading just §5.1.4
  may hold the pause-ad until `maxDuration` expires regardless of
  resume, since the only explicit dismissal trigger is the cap.

### G-4. Pause inside an active `<svta:OverlayPresentation>` is unspecified

- **Spec sections needing it**: §4.4.7 single-form concurrent
  rendering, §4.4.6 tracking, §5.5.4 beacon timing, §7.4 / §7.5.
- **What context is missing**: `context/04-use-cases.md` keeps
  UC-03 (active overlay during primary playback) and UC-05 (pause
  triggers an ad) mutually exclusive and never composes them. If
  the viewer pauses while an overlay form is visible, the overlay's
  slot-window timing (§5.5.4 — referenced to the Broadcaster-
  declared window) collides with the paused primary timeline: does
  the slot-window clock pause with primary or continue against
  wall-clock? Quartile beacons fire on different schedules under
  the two readings. §4.4.7's serialisation rule disables a new
  pause-ad from starting concurrently, but it says nothing about
  the existing overlay's timing. Inherited from v3's EC-3.
- **What an implementer does today**: ad-hoc. A Player that ties
  overlay timing to primary `presentationTime` will pause beacons;
  one that uses wall-clock keeps firing while the user is paused.

### G-5. Tracking-only ad (no `<MediaFile>`) lacks a normative carrier

- **Spec section needing it**: §8.2 (non-normative); referenced by
  §4.3 A-2 ("populate every non-linear candidate with one or more
  renderable forms").
- **What context is missing**: `context/05-dash-linear-interfaces.md`
  flags this as "ADS-internal policy until a normative reference
  emerges from the IAB". §8.2 inherits that posture and recommends
  silent skip — but a tracking-only `<Ad>` is a real industry
  pattern (analytics-only impressions for measurement, server-side
  fallbacks). The Player has no way to surface the dropped
  impression; the ADS has no carrier to emit one in compliance with
  R6.2 / R13.4 (which assume an `<EventStream>` of the callback
  scheme attached to either a sub-MPD `<Period>` or an
  `<svta:RenderableAsset>` — both of which presuppose a renderable
  form). Inherited from v3's G-6.
- **What an implementer does today**: silently drops the impression.
  Production deployments today fire these as bare HTTP GETs through
  a vendor side channel, which is outside the spec.

### G-6. Sub-token admissibility against a parent layout token is unspecified

- **Spec sections needing it**: §3.2 (sub-token enumeration), §4.4.2
  Constraint validation, §5.1.3 attribute table for `allowedLayouts`,
  §5.3.3 admissible `@layout` set per scheme.
- **What context is missing**: §3.2 says sub-tokens (e.g.
  `overlay-corner`, `squeezeback-l-shape`) "MAY refine the
  rendering" of their parent token (`overlay`, `squeezeback`). But
  the matching rule when a Broadcaster declares
  `allowedLayouts="overlay"` and the ADS returns
  `@layout="overlay-corner"` is undefined: (a) exact-token match —
  `overlay-corner` is inadmissible because the Broadcaster did not
  list it; (b) hierarchical match — `overlay-corner` refines
  `overlay` and is admissible. The §5.3.3 admissibility table per
  scheme enumerates every sub-token explicitly, which leans toward
  reading (a); but the §5.1.3 prose "the Broadcaster MAY use one
  token (e.g. `allowedLayouts="overlay-corner"`)" if the Broadcaster
  wants to constrain placement implies a Broadcaster who lists the
  parent intends a broad admissibility. v3's A-5 carries forward
  unchanged.
- **What an implementer does today**: guesses. Reading (a) makes
  ADSs author the fully-refined token they intend to render;
  reading (b) lets Broadcasters write permissively. Pick-one
  divergence between two ADSs talking to the same Broadcaster
  manifest produces silent E7 rejection on one and acceptance on
  the other.

### G-7. `@earliestResolutionTimeOffset` unit on inherited linear events is still unpinned in the spec body

- **Spec sections needing it**: §5.1.1 (`<InsertPresentation>`),
  §5.1.2 (`<ReplacePresentation>`), Annex A.2, Annex B.2, Annex D.2,
  Annex F.2 (all use the attribute on `<ReplacePresentation>` or
  `<InsertPresentation>`).
- **What context is missing**: §5.1.1 / §5.1.2 say attributes are
  "defined verbatim in §5.16.3 / §5.16.4 of the base specification",
  i.e. the unit is whatever MPEG-DASH 6th edition says. The §5.1.3
  NOTE pins the *SGAI-side* attribute on `<svta:OverlayPresentation>`
  to `<EventStream>@timescale` units and explicitly contrasts it
  with `<ImportedMPD>@earliestResolutionTimeOffset` (seconds), but
  it stops short of stating which time base the inherited
  `<InsertPresentation>` / `<ReplacePresentation>` baseline
  attributes use. Every linear annex example carries
  `earliestResolutionTimeOffset="60000"` at `timescale="1000"`,
  which only parses as 60 s if the unit is ticks — not seconds. A
  reader walking the spec front-to-back has no inline citation that
  tells them which reading is canonical for the baseline events.
  v3's G-1 closed for SGAI-side; the linear half is still open.
- **What an implementer does today**: matches the value to the
  surrounding `maxDuration` and infers the timescale. Annex B.2's
  pair `maxDuration="30000"` (=30 s in ms) /
  `earliestResolutionTimeOffset="60000"` (=60 s in ms) makes the
  inference unambiguous but only when both attributes are present
  on the same element.

### G-8. R8 per-construct justification audit table is not consolidated

- **Spec sections needing it**: §5.1.3, §5.1.4, §5.2.2, §5.3, §5.6
  (all new constructs).
- **What context is missing**: `context/03-requirements.md` R8.1
  ("Every new construct introduced by the proposal MUST be
  accompanied by an inline justification stating why an existing
  MPEG-DASH construct could not be reused") and
  `context/07-backward-compat-checklist.md` ask for a per-construct
  audit. v4 carries the carrier-closure list in §4.2 B-4 and
  scattered design rationale in §5.5 ("no new tracking scheme"),
  §5.2.2 ("not a `ListMPD`"), §5.6 ("DASH 6th defines no native
  carrier") — but there is no single audit table that, per
  construct (`<svta:OverlayPresentation>`, `<svta:PauseAdPresentation>`,
  `<svta:OverlayList>`, `<svta:Candidate>`, `<svta:RenderableAsset>`,
  `<svta:Click>`, `<svta:UniversalAdId>`), states "considered reusing
  X, rejected because Y". v3's G-7 carries forward.
- **What an implementer does today**: nothing fails at runtime; the
  gap is governance. But a WG reviewer auditing R8 compliance has to
  reconstruct the justification by reading the gap analysis instead
  of finding it inline.

---

## Edge cases (7)

Boundary conditions not contemplated in `context/04-use-cases.md`
but that deployable Players will encounter.

### EC-1. `allowedLayouts` populated entirely with inadmissible tokens

- **Trigger**: Broadcaster authors `<svta:OverlayPresentation
  allowedLayouts="linear pause-ad"/>` (per §5.1.3 layout-token
  table, both tokens are explicitly inadmissible inside an
  `<svta:OverlayPresentation>`). Or: every token is a typo / future
  edition's value the current Player does not know.
- **Why it matters**: §3.2 says the Player "MUST treat the form as
  if its layout were inadmissible and skip it (§4.4.4)", which is a
  *per-form* rule. The slot-level case — no form on any candidate
  could ever be admissible because the Broadcaster's set is empty
  in effect — collapses to §8.1 E6 (no renderable form on every
  candidate) and then to fall-through. But the spec never
  identifies the malformed `allowedLayouts` as the proximate cause;
  the Player sees an "ordinary" E6 even though the document is
  authoring-broken. v3's EC-1 unchanged.
- **Responsible actor / context silence**: Broadcaster authoring.
  Context is silent on whether a Player should surface a
  diagnostic that distinguishes "no candidate fit" from "no
  candidate could ever fit".

### EC-2. Overlay window exceeds linear window in a hybrid slot

- **Trigger**: `<ReplacePresentation>` declares
  `maxDuration="20000"` and the co-located
  `<svta:OverlayPresentation>` declares `maxDuration="30000"` —
  the linear ad ends 10 s before the overlay's declared window.
- **Why it matters**: §5.1.5 says "the shorter window governs" the
  overlay's display — but only the converse direction (overlay
  shorter than linear) is illustrated in Annex D.3. If the overlay
  is longer, then "the overlay is dismissed when either its own
  `maxDuration` is reached or the underlying linear slot ends,
  whichever comes first" implies overlay is dismissed at 20 s. But
  the primary content has now resumed and an overlay continuing
  past the linear slot end would in principle live on top of
  primary — which is UC-03 semantics, not UC-04. The spec
  short-circuits this with the shorter-window-governs rule, but the
  hybrid contract becomes a single composition window rather than
  two independent slots — which contradicts §5.1.5's "two
  independent events".
- **Responsible actor / context silence**: Player. Annex D scenario
  only walks the overlay-shorter case.

### EC-3. ADS returns `<svta:Candidate>` with zero `<svta:RenderableAsset>` children

- **Trigger**: Schema is `1..N` per §5.2.2; a candidate with zero
  forms is schema-invalid → §8.1 E2 fires. But a candidate with
  *only* forms whose `@mediaType` is non-conformant (e.g. all
  forms declare `@mediaType="video/webm"`) collapses to a
  semantically-empty candidate after §8.1 E8 filtering.
- **Why it matters**: §7.3 step 5 (1)-(2) processes per-candidate
  admissible form sets; an empty set after filtering triggers E6.
  The Player walks to the next candidate. So far so good — but if
  *every* candidate ends up empty after E8 filtering, the slot
  becomes a no-fill and §8.1 E3 / §6.2 (empty document)
  semantics should arguably apply *retroactively*. The spec routes
  this through E6 fall-through, which is correct but unattractive
  for diagnostics: the operator sees "no renderable form" rather
  than "non-conformant ADS".
- **Responsible actor / context silence**: ADS conformance vs
  no-fill telemetry; the spec collapses them.

### EC-4. Pause inside an active overlay window

- **Trigger**: A `<svta:OverlayPresentation>` event window
  [120 s, 140 s] is rendering on D1; the viewer pauses at 125 s.
  Concurrently a `<svta:PauseAdPresentation>` window
  [60 s, 660 s] is active so the pause is "inside" both.
- **Why it matters**: §4.4.7 forbids simultaneous non-linear forms,
  but the spec does not say which form yields. Does the active
  overlay finish before the pause-ad request is issued? Is the
  overlay dismissed to allow the pause-ad? Does the pause-ad
  request fire at all while another non-linear form is rendering?
  Slot-window timing of the running overlay (§5.5.4 — referenced
  to Broadcaster-declared window) collides with paused primary
  (see G-4). v3 EC-3 / EC-4 unchanged.
- **Responsible actor / context silence**: Player. Neither §4.4.7
  nor §7 addresses the resolution rule.

### EC-5. `maxDuration=0` on a slot

- **Trigger**: Broadcaster authors `<svta:OverlayPresentation
  maxDuration="0" .../>` (admissible per `xs:unsignedLong`).
- **Why it matters**: Every candidate's `@duration` would exceed
  the cap by definition → drop-before-play (§4.4.3) drops every
  candidate → fall through. The spec admits this as a degenerate
  but valid case, but does not say so explicitly. A Broadcaster
  could mis-author the manifest and a Player will silently no-op.
- **Responsible actor / context silence**: Broadcaster authoring.
  Context silent.

### EC-6. ADS resolution returns Overlay Resolution Document on a linear slot (or vice versa)

- **Trigger**: ADS responds to a `<ReplacePresentation>` resolution
  request with an Overlay Resolution Document, or to an
  `<svta:OverlayPresentation>` resolution request with a `ListMPD`.
- **Why it matters**: §4.3 A-1 ties the response shape to the
  slot type, so the mismatched response is non-conformant. Player
  detection mechanism: parse the document, find its `@profiles`,
  match against the slot's expected profile. This is implicit in
  §8.1 E2 ("schema-invalid, unsupported profile URI") but the
  cross-type mismatch (well-formed document, wrong profile for the
  slot) is a sub-case worth flagging. §8.1 E2's wording reads as
  if every parseable document maps to a valid resolution; the
  shape-mismatch case is not surfaced.
- **Responsible actor / context silence**: ADS conformance vs
  Player robustness. Context routes through generic E2.

### EC-7. Sub-MPD `<Period>@duration` declared vs `<svta:RenderableAsset @duration>` mismatch (video form)

- **Trigger**: A video form declares `@duration="PT20S"` but its
  child `<ImportedMPD>` resolves to an SPS sub-MPD whose
  `<Period>@duration="PT22S"`. Both attributes exist; both are
  Required.
- **Why it matters**: §5.3.1 `@duration` "drives the Player's
  drop-before-play arithmetic". §5.4 says
  `<Period>@duration` "declares the ad's intrinsic length". For
  cap arithmetic, drop-before-play uses the
  `<svta:RenderableAsset @duration>` (20 s); for trim-during-play
  (§4.4.3), the Player uses *actual* rendered length, which the
  sub-MPD authors as 22 s. The two attributes can disagree, and
  the spec does not say which is canonical. A diligent Broadcaster
  should keep them aligned; the spec gives no rule when they are
  not.
- **Responsible actor / context silence**: ADS authoring vs Player
  resolution. Context silent on the cross-document consistency.

---

## Ambiguities (5)

Places where the spec admits two readings because the context
language permits both.

### A-1. ADS responsibility to remap non-linear `presentationTime` is implied but not codified

- **Context passage**: `context/03-requirements.md` R13.2 — "the
  Player SHOULD fire quartile beacons timed against the
  Broadcaster-declared overlay window, not against the ad's
  internal duration."
- **Reading 1**: Player remaps inbound beacons against the slot
  window — re-computes quartiles, ignoring the ADS-emitted
  `presentationTime` values.
- **Reading 2**: ADS authors `presentationTime` in slot-window
  time so the Player fires the beacons verbatim. This is what
  §5.5.2 ("preferred placement … timing reference: overlay
  window") and §5.5.4 ("quartile beacons at 25 %, 50 %, 75 %,
  100 % of the Broadcaster-declared overlay window") assume — but
  §4.3 A-4 stops at "use the callback scheme" and never demands
  that the time base be slot-window.
- **Spec assumption**: Reading 2 — but without an ADS-side
  normative obligation. See G-1.
- **Tighter context sentence**: split R13.2 into an ADS MUST
  (emit `presentationTime` against the Broadcaster-declared slot
  window for non-linear ads) and a Player SHOULD (fire verbatim).
  v3's A-2 carries forward unresolved.

### A-2. `allowedLayouts` matching: enumeration vs hierarchical

- **Context passage**: §3.2 ("Sub-tokens MAY refine the rendering");
  §5.1.3 (`allowedLayouts="overlay-corner"` is the worked
  one-token example); §5.3.3 enumerates the top-level and
  sub-tokens explicitly per scheme.
- **Reading 1**: Exact-token enumeration. `allowedLayouts="overlay"`
  admits *only* `@layout="overlay"`, not `overlay-corner` or
  `overlay-lower-third`.
- **Reading 2**: Hierarchical. `allowedLayouts="overlay"` admits
  every sub-token under the `overlay` family.
- **Spec assumption**: Reading 1, by the lack of any text in §3.2
  or §4.4.2 describing a hierarchical-match rule. §5.3.3 lists
  every sub-token explicitly *per scheme*, which suggests the
  spec wants the Broadcaster to enumerate the precise admissible
  set.
- **Tighter context sentence**: `context/03-requirements.md` R12
  or §3.2 should state explicitly that `allowedLayouts` is an
  exact-token enumeration and that sub-tokens MUST be listed when
  admissible. v3 A-5 carries forward unresolved.

### A-3. `@mediaType` (svta) vs `@mimeType` (DASH) collision

- **Context passage**: §5.3.1 (`@mediaType` enum
  `{video, image, html}` on `<svta:RenderableAsset>`); §5.3.4
  (`@mimeType` on `<AdaptationSet>` / `<Representation>` reached
  via `<ImportedMPD>`, RFC 4337-bound to
  `video/mp4` / `audio/mp4` / `application/mp4`).
- **Reading 1**: Two distinct attributes with non-overlapping
  domains. `@mediaType` is the spec-side carrier-category enum,
  `@mimeType` is the DASH-baseline IANA MIME type. The spec
  uses both verbatim and the reader is meant to keep them apart.
- **Reading 2**: A reader skimming sees "the same idea — the
  thing's MIME type" and confuses the two, then looks for a
  `@mediaType="video/mp4"` value that does not exist.
- **Spec assumption**: Reading 1.
- **Tighter context sentence**: a one-liner in §3.1 (Core terms)
  that calls out the distinction (`@mediaType` is the spec-side
  enum, `@mimeType` is the inherited IANA value) and a §5.3.1
  cross-link to §5.3.4. Without it, a casual reader can conflate
  them across §5.3.1 ↔ §5.3.4 / §6.4.

### A-4. "Play candidates in declared order" (§4.4.4) vs "stop after one accepted candidate" (§7.3 step 5 e)

- **Context passage**: §4.4.4 — "the Player MUST play the
  candidates in the order declared by the ADS"; §7.3 step 5 e —
  "Stop after one accepted candidate (the slot is filled)" for
  non-linear opportunities.
- **Reading 1**: All admissible candidates play sequentially for
  non-linear opportunities — the natural reading of §4.4.4.
- **Reading 2**: Only the first admissible candidate plays for
  non-linear opportunities; for linear opportunities (`ListMPD`)
  every Period plays in order. §4.4.4 reads as the linear rule
  and §7.3 step 5 e overrides it for non-linear.
- **Spec assumption**: Reading 2 — implied by the §7.3
  algorithm but not stated in §4.4.4. A reader who stops at
  chapter 4 misses the override.
- **Tighter context sentence**: §4.4.4 should split the
  obligation along slot type: for non-linear the Player MUST
  play *at most one* candidate (first admissible); for linear
  every Period plays in declared order subject to drops. Closes
  a v4-introduced ambiguity (was already present in v3 but the
  v3 algorithm was more verbose, masking it).

### A-5. `<svta:RenderableAsset>` carrying an `<EventStream>` reinterprets `presentationTime` semantics

- **Context passage**: §5.5.3 — "the `<EventStream>@timescale`
  governs the unit; the `<Event>@presentationTime` is
  interpreted relative to the moment the form becomes visible
  (i.e. the impression instant)." `urn:mpeg:dash:event:callback:2015`
  is defined by DASH 6th §5.10 with `presentationTime` relative
  to the carrying `<Period>` start.
- **Reading 1**: The spec reuses the callback scheme's syntax but
  redefines its `presentationTime` reference frame when the
  `<EventStream>` is a child of `<svta:RenderableAsset>` instead
  of `<Period>`. Under R1.3 ("MUST NOT alter or override the
  semantics of any pre-existing MPEG-DASH 6th edition construct")
  this is a borderline violation — the carrier is reused but its
  timing semantics are not.
- **Reading 2**: The reference frame shift is intrinsic to placing
  `<EventStream>` outside a `<Period>` parent; there is no
  baseline rule about non-`<Period>`-parent `<EventStream>` so
  the spec is free to define one.
- **Spec assumption**: Reading 2. But the foreign-namespace open
  content rule (§5.2.1) admits *new SVTA elements* under existing
  parents; it does not authorise placing a *baseline DASH
  element* (`<EventStream>`, namespace `urn:mpeg:dash:schema:mpd:2011`)
  under a *new SVTA-namespaced parent* (`<svta:RenderableAsset>`)
  with redefined timing.
- **Tighter context sentence**: `context/08-dash-extension-rules.md`
  or `context/06-naming-and-namespaces.md` should explicitly admit
  the pattern "baseline DASH element placed under an SVTA-namespaced
  parent, timing reinterpreted to the parent's lifecycle". Without
  it, R1.3 carries a small but real residual risk on §5.5.3.

---

## R coverage map

| R   | Status     | Spec sections that satisfy it | Notes |
|-----|------------|-------------------------------|-------|
| R1  | full       | §1, §4.1, §4.4.1, §4.4.8, §4.5, §5.1.3 / §5.1.4 legacy-Player paragraphs, §5.6.4, §7.6 (legacy row), §8.1 E5, Annex G | Ignore-if-unknown discipline complete across scheme URI, foreign-namespace, profile URI; UC-07 walked end-to-end. |
| R2  | full       | §4.1 three-actor model, §4.2 B-1..B-7, §4.3 A-1..A-7, §4.4.1..§4.4.8, §7 algorithm | Each actor's obligations enumerated and the §7.3 algorithm is the operational manifestation. |
| R3  | full       | §3.4 D1..D5 taxonomy, §7.6 per-device matrix, Annexes A.5/B.5/C.5/D.4/E.4/F.5 | Every (class × UC) cell defined; "skip / fall through" is a defined outcome per §7.6 footer. |
| R4  | full       | §4.2 B-2, §4.4.3, §4.4.6 trim-stops-beacons, §5.1.3 / §5.1.4 / §5.2.1 / §5.2.2, §7.3 step 4.c / step 5, §8.1 E9 / E10 | v3's gap on form-level duration is closed: §5.3.1 makes `@duration` Required on every `<svta:RenderableAsset>` and §8.6 defines image-form intrinsic duration as the form's `@duration`. |
| R5  | full       | §4.4.2 / §4.4.5, §5.3, §7.3 step 5 (1)-(4) | Form selection algorithm specified; the three-way intersection (device caps × allowed layouts × admissible carriers) is normative. The tie-break on `@mediaType` (video > html > image) carries an inline `[inferred]` tag — see G-6 / A-2 / A-3. |
| R6  | full       | §4.3 A-4, §5.5 (carrier shape + placement + non-video carrier), §6.5, §7.5 | Tracking carrier reuses the callback scheme; vendor-namespaced extensions for app metadata. R13.2-side gap captured under R13 (partial). |
| R7  | full       | §4.4.4, §7.3 step 4 (linear) / step 5 (non-linear), §8.1 E9 | ADS-declared order honoured; drops permitted only under R7.2 / R7.3 conditions. See A-4 for the non-linear "stop after one" rule that the chapter 4 wording does not surface explicitly. |
| R8  | governance | Inline justifications: §5.1.3 attribute reuse, §5.1.4 scheme distinction, §5.2.2 ("not a `ListMPD`"), §5.5 ("no new tracking scheme"), §5.6 ("DASH 6th defines no native carrier") | Scattered; no consolidated audit table per construct — see G-8. |
| R9  | governance | §5.1.1 / §5.1.2 (linear baseline reused unchanged), §5.4 (sub-MPD inherits SPS), §5.5 (no new tracking scheme), §5.2.2 (uses `<MPD>` envelope and `urn:mpeg:dash:profile:` URI shape), §7.4 (HTML5/CSS for layout) | Heavy reuse demonstrated; no parallel layout / tracking / event-stream surface. |
| R10 | governance | §1.1 OOS, §3.2 IAB-derived layout vocabulary, §7.4 ("Spatial positioning … is delegated entirely to HTML5 / CSS") | Layout system explicitly out of scope and delegated. |
| R11 | full       | §1 scope, §4.3 ADS section ("MAY be derived from VAST"), §6.6 (non-normative), Annex H references | No normative VAST reference; VAST mapping confined to non-normative §6.6 per R11.3. |
| R12 | full       | §3.2 layout vocabulary (IAB sourced live), §4.2 B-3, §4.3 A-5 | 1:1 token mapping; chapter 2 references the live IAB document. |
| R13 | partial    | §4.4.6, §5.5.2 (placement + timing reference table), §5.5.4 | Quartile-against-slot-window stated for the Player; no normative ADS obligation to emit `presentationTime` in the slot-window time base — see G-1 / A-1. v3's G-5 unchanged. |
| R14 | full       | §1.1 OOS, §4.2 B-7 (`maxConcurrent` MUST = 1), §4.4.7 single-form concurrent rendering, §5.1.3 (`maxConcurrent` attribute) | v3's G-2 closed via attribute + serialisation rule. Residual cross-slot composition edge cases under EC-4 / G-4. |
| R15 | full       | §1.1 OOS-4, §3.2 (three carriers enumerated), §3.1 (Tracking carrier), §4.3 A-3, §5.3.2 enum, §5.3.4 RFC 4337 binding for video forms | Three admissible carriers (video, image, HTML); scripted creatives MUST wrap in `text/html`. |

Breakdown: **11 full** (R1, R2, R3, R4, R5, R6, R7, R11, R12, R14,
R15), **1 partial** (R13), **3 governance** (R8, R9, R10) = 15 of
15 enumerated requirements.

---

## Recommended context refinements

Top 5 by leverage, ordered by the number of downstream items each
unblocks.

### 1. Split R13.2 into ADS MUST and Player SHOULD

`context/03-requirements.md` R13.2 places the slot-window timing
obligation on the Player ("the Player SHOULD fire quartile beacons
timed against the Broadcaster-declared overlay window"). Spec
§5.5.2 / §5.5.4 / §7.5 silently shift that obligation to the ADS
because the Player merely fires the `<Event @presentationTime>`
values the ADS authored. Add an ADS-side requirement (e.g. R13.2a
— "for non-linear slots, the ADS MUST emit callback
`<Event @presentationTime>` values measured against the
Broadcaster-declared slot window, not the ad's intrinsic
duration") and keep the current R13.2 as the Player-side
complement ("the Player MUST fire verbatim"). Closes G-1 and A-1;
unblocks R13 → full and tightens §4.3 with a new A-N row.

### 2. Pin `allowedLayouts` matching semantics (enumeration vs hierarchical)

`context/03-requirements.md` R12 or §3.2 in the spec should state
explicitly that `allowedLayouts` is matched as an exact-token
enumeration and that sub-tokens MUST be listed when admissible. A
single sentence in R12.2 ("the matching rule is exact-token; a
parent token does NOT admit its refinements unless the parent itself
is the on-the-wire value") closes G-6 / A-2, makes §5.3.3 audit
table redundant rather than load-bearing, and resolves the
Broadcaster authoring ambiguity that today produces silent E7 on
cross-ADS variability.

### 3. Define the Player obligation to dismiss `<svta:PauseAdPresentation>` on viewer resume

`context/04-use-cases.md` UC-05 prose describes the dismissal but
no requirement captures it. Add a Player MUST rule to R14 or a new
R that fires on the pause-state transition ("when the viewer
resumes primary playback, the Player MUST dismiss any active
pause-ad form and MUST stop firing further beacons"). Closes G-3
and clarifies the pause-ad lifecycle independent of the cap. Touches
§4.4.x (new sub-section) and Annex E.

### 4. Resolve the inherited linear `@earliestResolutionTimeOffset` unit in spec body

`context/05-dash-linear-interfaces.md` § references to §5.16 of
DASH 6th edition assume the unit but do not pin it for the spec's
local readers. Add one sentence — either in
`context/05-dash-linear-interfaces.md` near the worked example or
in `context/06-naming-and-namespaces.md` §"Naming consistency" —
clarifying that on baseline `<InsertPresentation>` /
`<ReplacePresentation>`, `@earliestResolutionTimeOffset` is
expressed in the carrying `<EventStream>@timescale` units (i.e.
matches the SGAI-side convention). The spec body then only needs
to reuse the citation. Closes G-7 and removes a class of off-by-1000
authoring errors in linear annexes.

### 5. Compose UC-03 and UC-05 (pause during active overlay)

`context/04-use-cases.md` keeps UC-03 (active overlay during
primary playback) and UC-05 (pause-trigger) mutually exclusive
even though both ride on the primary timeline. Extend UC-03 with
a "viewer pauses during the overlay window" sub-scenario and pick
a rule for the slot-window clock (pause with primary, or
continue against wall-clock). Closes G-4 / EC-4 and forecloses
divergent Player implementations on a real production trigger
(any CTV remote pause during a non-linear ad).

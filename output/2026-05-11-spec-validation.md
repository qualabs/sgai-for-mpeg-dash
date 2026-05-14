[GROUNDED_BY=notebooklm]

# Spec validation — 2026-05-11

Built against:
- spec: [`./2026-05-11-sgai-spec.md`](./2026-05-11-sgai-spec.md)
- context/ at git SHA: `f7c8ffb`

This document captures gaps, edge cases, and ambiguities surfaced
during the spec build. Findings here feed back into `../context/` —
they are NOT part of the spec itself.

## Gaps (8)

### G-01. Tracking carrier for non-video renderable forms is undefined

- **Spec section affected**: §5.4 (`<sgai:RenderableForms>`), §6.3
  step 7, §8.4.
- **Spec gap**: the spec mandates the callback event scheme
  (§5.10.4.5) as the tracking carrier (R6.2), but this scheme is
  carried inside a sub-MPD's `<EventStream>` — which is natural for
  `video` forms (the sub-MPD describes the ad video) but undefined
  for `image` and `html` forms (no sub-MPD exists for them in this
  spec). The context does not say how non-video forms surface
  impression / start / quartiles / complete tracking.
- **Implementer default today**: silently skip tracking for
  non-video forms, OR ship a vendor-namespaced tracking list inside
  `<sgai:Form>` that some Players read and others ignore. Either
  outcome breaks ad-business interop.

### G-02. VAST 4.x version pin missing

- **Spec section affected**: chapter 2 (Normative references).
- **Spec gap**: [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
  flags this explicitly: the exact 4.x version (4.0 / 4.1 / 4.2 /
  4.3) used by industry practice is unconfirmed. The NotebookLM
  source consulted in this build references VAST v3.0 in the
  bibliography and only mentions 4.2 / 4.3 as placeholder strings
  in the CMCD v2 draft.
- **Implementer default today**: pick 4.2 (most common deployed)
  or 4.3 (newest). Interop matrix is undefined.

### G-03. Pause-trigger event placement vs §5.10.1 timed-event invariant

- **Spec section affected**: §5.3, §6.4.
- **Spec gap**: §5.10.1 says events are *strictly timed* — "Events
  are timed, i.e. each event starts at a specific media
  presentation time and may have a duration". The spec currently
  places the pause-trigger in an `<EventStream>` with a sentinel
  `presentationTime="0"` and pushes the trigger semantics to the
  Player application layer. The spec does not say whether this
  layering is normatively legal or merely tolerated. A WG reviewer
  could plausibly read §5.10.1 as forbidding the sentinel pattern.
- **Implementer default today**: implement the application-layer
  trigger pattern (the path the spec picks) and accept the
  ambiguity — but a strict reviewer's interpretation could force a
  redesign.

### G-04. `<sgai:RenderableForms>` placement when no `<ImportedMPD>` exists

- **Spec section affected**: §5.4, §5.6.
- **Spec gap**: the spec draft assumes `<ImportedMPD>` is the
  primary content carrier and `<sgai:RenderableForms>` augments
  it. But for non-video-only candidates (e.g. an image-only banner
  campaign that has no video sub-MPD at all), there is no
  `<ImportedMPD>` to anchor to. The spec currently says
  `<ImportedMPD>` is REQUIRED on each `<Period>`. What happens to
  candidates with no video form?
- **Implementer default today**: either (a) require the ADS to
  always emit a placeholder `<ImportedMPD>` with a tiny / empty
  sub-MPD (wasteful, fragile), or (b) treat
  `<sgai:RenderableForms>` as the primary carrier on a Period
  with no `<ImportedMPD>` (off-spec). Both are bad.

### G-05. Concurrency cap semantics under hybrid breaks

- **Spec section affected**: §5.2.2 (`@maxConcurrentOverlays`),
  §7.4 (UC-04).
- **Spec gap**: `@maxConcurrentOverlays` counts overlays from the
  same overlay event. UC-04 has a linear `<ReplacePresentation>`
  and a concurrent `<OverlayPresentation>` covering the same span.
  If the OverlayPresentation declares `@maxConcurrentOverlays="2"`
  and an existing overlay (from a different event) is still on
  screen, does that count against the cap?
- **Implementer default today**: count per-event overlays only.
  Off-event overlays are not budgeted. Risk: visual clutter on D1
  devices that have multiple concurrent SGAI events firing.

### G-06. `<sgai:DefaultLayout>` on `<Period>` is introduced in
example 8.2 without a chapter-5 syntactic definition

- **Spec section affected**: §5 (Syntax), §8.2.
- **Spec gap**: the example XML in §8.2 uses
  `<sgai:DefaultLayout value="banner"/>` inside a `<Period>` to
  let the ADS signal the candidate's nominal layout, which the
  Player checks against the parent event's `@allowedLayouts`. But
  chapter 5 never defines `<sgai:DefaultLayout>`. Either the
  syntax chapter omits it, or the example introduces an undefined
  construct. **This is a real authoring bug in the spec draft.**
- **Implementer default today**: parse the example tolerantly;
  ignore the unknown element. The candidate's nominal layout
  remains unsignalled.

### G-07. SPS profile constraint on non-video AdaptationSets is stated
indirectly

- **Spec section affected**: §5 syntax decisions, gap analysis G3.
- **Spec gap**: the gap analysis ([`../analysis/dash-gap-analysis.md`](../analysis/dash-gap-analysis.md)
  G3) and the working position behind §5.4 (carry alternative
  forms at the ListMPD layer, leave SPS untouched) both assume
  §8.15 SPS restricts the sub-MPD to standard audio/video
  AdaptationSets. The NotebookLM verification in this build
  returned: "§8.15 does not explicitly restrict AdaptationSets to
  audio/video only, nor does it forbid formats like image or
  HTML. The normative constraint is solely: 'One and only one
  Period element shall be present. It shall conform to the
  constraints in clause 8.5.3'". The premise of putting
  alternative forms at the ListMPD layer (instead of relaxing
  §8.15) may rest on a misreading of §8.15 itself. A stricter
  reading of §8.5.3 might still forbid non-video AdaptationSets,
  but the chain is unaudited.
- **Implementer default today**: assume the project's working
  position (multi-form at ListMPD layer) and ignore the
  possibility that §8.15 + §8.5.3 already allow image / html
  AdaptationSets inside the sub-MPD. Needs a follow-up
  NotebookLM query specifically on §8.5.3 to resolve.

### G-08. Cross-edition Player URI recognition has no R coverage

- **Spec section affected**: chapter 2, chapter 4.
- **Spec gap**: [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)
  line 27 says "A Player implementing edition N + 1 SHOULD
  recognise both `:N:` and `:N+1:` URIs". This obligation is on
  the *Player*, not on the spec document. No R in
  [`../context/03-requirements.md`](../context/03-requirements.md)
  covers it directly. R1 is about *legacy Players ignoring new
  constructs*; this is the inverse (*new Players recognising old
  constructs*).
- **Implementer default today**: most Players hardcode the URIs
  of their target edition only. Cross-edition deployments
  silently degrade until the Player is upgraded.

## Edge cases (6)

### E-01. ADS returns a `ListMPD` with zero `<Period>` entries

- **Trigger**: no-fill response from the ADS.
- **Why it matters**: per E2 / E4 of the error matrix, Player
  falls through. But the surface error class is ambiguous: empty-
  but-well-formed `ListMPD` is technically schema-valid (the
  schema does not require `<Period>` to be non-empty), so E4
  (schema-invalid) does not apply. Spec is silent on which row
  applies.
- **Responsible actor**: ADS (could be more explicit by emitting
  HTTP 204 or a status header); Player (must handle gracefully).
  Both spec sides silent.

### E-02. Overlay `@maxConcurrentOverlays` is exceeded by the ADS response

- **Trigger**: ADS returns 3 overlay candidates, all renderable,
  `@maxConcurrentOverlays="2"`.
- **Why it matters**: per R2.3 the Player rejects the third.
  Order? The spec draft says nothing; presumed FIFO from
  declared order (per R7.1). But the spec is silent.
- **Responsible actor**: Player. Spec is silent on the rejection
  policy.

### E-03. Layout token in candidate's `<sgai:DefaultLayout>` is not in
the event's `@allowedLayouts`

- **Trigger**: ADS returns a candidate declaring `banner`,
  event allows `l-shape side-by-side` only.
- **Why it matters**: Player rejects per R2.3 (validates against
  Broadcaster constraint). UC-03 notes / R10 imply the Player
  MUST NOT promote a candidate to a different layout. But what
  if `<sgai:DefaultLayout>` is *missing* on the candidate? Spec
  is silent.
- **Responsible actor**: Player (rejection); ADS (should declare
  layout per R5). Spec silent on the missing-default fallback.

### E-04. Pause-ad resume happens before the overlay finishes rendering
its first frame

- **Trigger**: viewer pauses, ADS responds, overlay starts
  rendering, viewer resumes within 100 ms.
- **Why it matters**: dismissal timing. The spec draft says "When
  the user resumes playback, the Player MUST dismiss the overlay
  immediately" but does not address the impression-counting
  consequence. Did the impression fire? Should it?
- **Responsible actor**: Player (dismissal); ADS adapter
  (tracking). Spec is silent.

### E-05. Multi-form candidate where the highest-priority form is
unrenderable and the next form has a longer declared duration that
exceeds the cap

- **Trigger**: ADS returns `video@priority=1 duration=20s` and
  `html@priority=2 duration=30s` for an event with
  `@maxDuration=25s`.
- **Why it matters**: order-of-evaluation interaction between
  R5.3 (skip unrenderable form) and R7.3 (drop-before-play based
  on declared duration). The Player picks the `html` form (R5.2,
  R5.3 promotion), but its declared duration exceeds the cap. Is
  the candidate dropped (R7.3) or trimmed (R7.5)? Both readings
  are defensible.
- **Responsible actor**: Player. Spec is silent on the precedence
  between form-promotion and cap-drop.

### E-06. Tracking beacon firing on D5 (no overlay rendered)

- **Trigger**: D5 receives a multi-form candidate with no
  renderable form. Per R5.3 the Player declines. Per §9.1 ("no
  tracking beacon for the failed exchange"), no tracking fires.
- **Why it matters**: the gap analysis Open question 4 flags this
  as a privacy/bandwidth/ad-business trade-off. The spec currently
  defers (§9.8) but the deferral leaves ad-buyers exposed: a
  campaign budget can leak to D5 viewers because no impression is
  counted. Some ad-business models will object.
- **Responsible actor**: Player (decision); ADS / business
  layer (consequence). Spec defers.

## Ambiguities (5)

### A-01. "Slot window has elapsed" definition for overlay slots (E13)

- **Spec passage**: [`../context/03-requirements.md`](../context/03-requirements.md)
  R7 + [`../analysis/error-semantics.md`](../analysis/error-semantics.md) E13.
- **Readings**:
  - **(a)** "elapsed" = the overlay's `@maxDuration` after the
    event's `presentationTime` has passed.
  - **(b)** "elapsed" = the moment the Player would have started
    rendering the overlay (i.e., `presentationTime`); anything
    later is "late".
- **Spec draft assumed**: (a) — "the overlay's @maxDuration time
  after the event's presentationTime has passed" (§9.6).
  Rationale: gives the ADS the longest legitimate window.
- **Spec fix**: add a normative sentence to R7 or to the error
  matrix E13 row defining the slot window endpoint precisely.

### A-02. "Best form to render" tie-breaking when ADS priorities collide

- **Spec passage**: R5.2 ([`../context/03-requirements.md`](../context/03-requirements.md):139).
- **Readings**:
  - **(a)** "best" = highest-priority renderable form per ADS
    hints; ties broken by document order in
    `<sgai:RenderableForms>`.
  - **(b)** "best" = highest-fidelity renderable form per
    Player's own ranking (e.g., html > image even if ADS gave
    them equal priority).
- **Spec draft assumed**: (a) — §5.4.2 "Lower value = higher
  priority. The Player walks forms in priority order; ties broken
  by document order".
- **Spec fix**: R5.2 conformance criterion should call out the
  tie-breaking rule explicitly. Today the spec is silent.

### A-03. "Drop before play" semantics when the cap is the *running
total* mid-pod

- **Spec passage**: R7.3 ([`../context/03-requirements.md`](../context/03-requirements.md):210).
- **Readings**:
  - **(a)** Drop-before-play is evaluated *before* the pod starts:
    Player walks the declared candidates, drops those whose
    cumulative declared duration would push past the cap, plays
    the survivors.
  - **(b)** Drop-before-play is evaluated *between* candidates:
    after ad N finishes, the Player checks whether ad N+1's
    declared duration would push past, and drops it if yes.
- **Spec draft assumed**: (a) — pre-pod evaluation, matching how
  E11 is phrased.
- **Spec fix**: R7.3 should clarify whether the cap check happens
  once or per-candidate. (a) is simpler and matches ListMPD
  semantics (the pod is fully visible before playback starts);
  (b) is more flexible but harder to reason about.

### A-04. `<sgai:Form>` `@type` enum extensibility

- **Spec passage**: §5.4.2 of the spec draft itself (so this
  ambiguity is self-inflicted, not inherited from spec).
- **Readings**:
  - **(a)** New `@type` values can be added to the canonical enum
    only by amending the spec.
  - **(b)** New `@type` values can be added by vendors via the
    vendor namespace (`urn:qualabs:sgai:2026`).
- **Spec draft assumed**: hybrid — "extensible enum; new values
  MUST be declared in this spec or via vendor namespace". This
  is ambiguous about how a vendor-namespaced `@type` is consumed
  by a non-vendor Player.
- **Spec fix**: pin the policy. Recommended: (a) for canonical
  Players + (b) is informational/ignored by canonical Players.

### A-05. Per-actor binding of R6.4 (vendor-namespaced VAST metadata)

- **Spec passage**: [`../context/03-requirements.md`](../context/03-requirements.md):174.
- **Readings**:
  - **(a)** The Broadcaster authors the vendor-namespaced
    metadata into the main MPD (rare in production).
  - **(b)** The ADS authors it into the ListMPD response (the
    common production case).
- **Spec draft assumed**: (b) — §5.5 places `<qua:VastMetadata>`
  on `<ImportedMPD>` inside the ListMPD.
- **Spec fix**: R6.4's actor binding currently reads
  "ADS / Broadcaster" (joint). Split into two assertions —
  Broadcaster-side authoring is rare and probably orthogonal to
  ADS-side authoring.

## Recommended spec refinements

Top 5 priorities for the next spec iteration, ranked by leverage.

1. **Close G-01 (tracking carrier for non-video forms).** Blocks
   the entire non-linear product if not resolved before
   implementation. Highest leverage. Recommended path: define a
   "carrier sub-MPD" wrapper that carries `<EventStream>` callback
   events tied to the form's display schedule.
2. **Close G-06 (missing `<sgai:DefaultLayout>` definition).**
   Real authoring bug in the spec draft. Cheap to fix; high
   visibility (it is in the chapter 8 example XML).
3. **Resolve A-03 (drop-before-play cap evaluation).** Cap-trim
   semantics are central to R4 / R7; ambiguity here breaks
   interop on multi-ad breaks.
4. **Verify G-07 (§8.15 SPS profile reality).** Single follow-up
   NotebookLM query on §8.5.3 will resolve whether the project's
   working position is correct or rests on a misread. Cheap, high
   information value.
5. **Decide G-08 (cross-edition Player URI recognition R).** Adds
   either an R1.4 sub-requirement or a standalone R. Cheap to
   add to the spec; saves a class of deployment bugs.

Lower-priority but still worth absorbing: G-02 (VAST 4.x pin) is
ecosystem-bound — track the IAB Tech Lab page rather than
forcing a decision today. G-03 (pause-trigger event placement)
needs WG feedback; document the working position and the
alternative side-by-side, defer the strict resolution.

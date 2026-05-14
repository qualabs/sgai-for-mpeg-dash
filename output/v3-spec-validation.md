[GROUNDED_BY=spec-only]

# Spec validation — 2026-05-14

Built against:
- spec: `output/2026-05-14-sgai-spec.md` (2191 lines)
- context/ at git SHA: `b62c7d773b4cd9f2290f10f66ff3781f61dc0b77` (branch `main`)
- analysis inputs: `analysis/dash-gap-analysis.md`, `analysis/conformance-assertions.md`, `analysis/error-semantics.md`, `analysis/uc-coverage-matrix.md`, `analysis/iab-ad-templates.md`

Mode: independent peer review by a fresh subagent. No grounding requests
were issued to NotebookLM; validation is comparison of spec text against
`context/` and `analysis/` as the authoritative source.

---

## Gaps (8)

Things the spec defines but for which `context/` does not provide enough
information to ship a conformant implementation deterministically.

### G-1. Unit of `@earliestResolutionTimeOffset` on inherited linear events is asserted but contradicts the worked example

- **Spec sections needing it**: §5.1.1 (`<InsertPresentation>`), §5.1.2
  (`<ReplacePresentation>`), §5.1.3 (`<svta:OverlayPresentation>`),
  §5.1.4 (`<svta:PauseAdTrigger>`); Annex A.2, B.2, F.2 examples.
- **What context is missing**: `context/05-dash-linear-interfaces.md`
  lines 156–166 carries `earliestResolutionTimeOffset="60000"` and the
  prose at line 196 interprets it as 60000 ms (`= 360000 − 60000 = 300000 ms`).
  Spec §5.1.1 / §5.1.2 attribute tables declare the unit as
  **"in seconds"**. `context/06-naming-and-namespaces.md` lines 138–145
  flags this exact ambiguity (the baseline `<ImportedMPD>`
  `@earliestResolutionTimeOffset` is in seconds per §5.3.2.6.1, but
  inside `<EventStream>` baseline references show `EventStream@timescale`
  units). Context does not authoritatively pin the baseline
  `<InsertPresentation>` / `<ReplacePresentation>` unit, and the
  worked example at `context/05-dash-linear-interfaces.md:165`
  silently uses what reads as ms while context-06 leaves the question
  unresolved.
- **What an implementer does today**: guess. The spec asserts "in
  seconds" four times (§5.1.1, §5.1.2, §5.1.3, §5.1.4) but Annex B.3
  declares `earliestResolutionTimeOffset="60"` on `<ImportedMPD>`
  whereas Annex B.2 declares `earliestResolutionTimeOffset="60000"`
  on `<ReplacePresentation>` for the **same 60 s pre-fetch window**.
  An implementer reading the spec must reconcile two different
  numeric values claimed to encode "60 seconds" with the same unit.

### G-2. `<svta:Concurrency @max>` enforcement is required but the §7.3 algorithm never reads it

- **Spec section needing it**: §7.3 Player validation and selection
  algorithm (lines 1177–1239) and §4.4 P-3 ("validate every
  ADS-returned candidate against the Broadcaster-declared slot
  constraints ... concurrency cap").
- **What context is missing**: `context/03-requirements.md` R2.1 lists
  "maximum number of concurrent overlays" as a Broadcaster-declared
  constraint; `context/04-use-cases.md` UC-03 broadcaster intent line 254
  says "Maximum number of concurrent overlays for this slot is bounded".
  The spec carries `<svta:Concurrency @max>` in §5.1.3.2 but no step
  of the §7.3 algorithm references `@max` — only `<svta:Exclusions>`
  appears in step 3.d.
- **What an implementer does today**: ad-hoc. Without a normative
  algorithm step, two implementations may diverge on whether to
  enforce `@max` at admission time (filter candidates after the cap
  is reached) or at rendering time (stop composing past `@max`
  forms). Both are silent under the current algorithm wording.

### G-3. Cap arithmetic for non-video forms is undefined when `<svta:RenderableAsset @duration>` is absent

- **Spec section needing it**: §7.3 step 3.g (`if CUMULATIVE +
  declared_duration(FORM(C)) > S.@maxDuration ...`); §5.3.1
  `@duration` attribute (OPTIONAL).
- **What context is missing**: `context/03-requirements.md` R4 frames
  cap enforcement against "ad slot duration" and R7.3 ("drop before
  play") cites "declared duration" without disambiguating per-form
  vs per-Period. Context never establishes how the Player computes a
  duration value for an HTML or image form with no `@duration` on
  `<svta:RenderableAsset>`. The §5.2.2 NOTE pins `Period@duration` to
  "the slot's @maxDuration window" for non-linear candidates — i.e.
  every candidate's nominal length equals the cap, which makes
  cumulative cap arithmetic vacuous for an overlay pod of more than
  one candidate.
- **What an implementer does today**: most likely treat `@duration`
  on `<svta:RenderableAsset>` as the slot window when absent, which
  collapses R7.3 (drop before play) to a no-op for non-video pods.
  A divergent implementer may treat absence as zero, accepting all
  candidates unconditionally.

### G-4. Concurrent-slot interaction is unspecified

- **Spec section needing it**: §5.1.3 (overlay) + §5.1.4 (pause
  trigger) + §7.6 (co-located events).
- **What context is missing**: `context/04-use-cases.md` describes
  hybrid linear + overlay (UC-04) but never the case of two
  overlapping `<svta:OverlayPresentation>` events with overlapping
  presentation intervals. The spec §7.6 only addresses two events at
  the **same** `presentationTime`. The cross-slot concurrency cap
  (sum of `@max` across overlapping slots) is undefined.
- **What an implementer does today**: ad-hoc. A platform may
  serialise overlapping overlay slots, render both, or decline the
  second. None of these is normative.

### G-5. No normative ADS obligation to remap non-linear beacon `presentationTime` to slot window

- **Spec section needing it**: §5.5.4, §7.2 step 5, §7.5.
- **What context is missing**: `context/03-requirements.md` R13.2 is
  a Player SHOULD ("the Player SHOULD fire quartile beacons timed
  against the Broadcaster-declared overlay window"). Spec §5.5.4
  pushes the remap responsibility to the ADS as a normative
  obligation ("The non-linear remap is performed at resolution time
  by the ADS") and §7.5 says "The ADS is responsible for placing
  beacon `presentationTime` values such that they fire at the
  intended fractions of the slot window". But §4.3 ADS obligations
  has no A-N item that codifies this; A-3 only requires the callback
  scheme. The Player therefore has no MUST/SHOULD recourse if the
  ADS does not remap.
- **What an implementer does today**: the Player either (a) trusts
  the ADS implicitly (current spec intent) and fires whatever values
  arrive, or (b) re-times beacons itself, which the spec forbids
  ("The Player MUST NOT introduce its own beacon schedule", §7.5).
  Result: a non-remapping ADS produces silently wrong analytics.

### G-6. Tracking-only ad (no `<MediaFile>`) lacks a normative carrier

- **Spec section needing it**: §8.2 (non-normative); referenced by
  §4.3 A-2 (each candidate MUST carry at least one renderable form).
- **What context is missing**: `context/05-dash-linear-interfaces.md`
  lines 401–408 explicitly flags this as "ADS-internal policy until a
  normative reference emerges". Spec §8.2 inherits that posture and
  rejects "empty document with tracking sidecar" as non-conformant
  but offers no normative carrier — silent skip is the only ADS
  option. This drops impressions that production deployments today
  rely on.
- **What an implementer does today**: ADS adapter silently skips the
  VAST `<Ad>`, losing the impression on the Broadcaster's side. There
  is no Player-side surfacing of the loss either.

### G-7. R8 per-construct justification is not systematically present

- **Spec section needing it**: §5.1.3, §5.1.4, §5.2.2, §5.3, §5.6 (all
  new constructs).
- **What context is missing**: `context/03-requirements.md` R8.1
  ("Every new construct ... MUST be accompanied by an inline
  justification stating why an existing MPEG-DASH construct could
  not be reused") demands per-construct inline justification.
  Context `07-backward-compat-checklist.md` requires an aggregated
  audit table per construct (lines 135–144). The spec carries
  scattered NOTEs (§5.1.3 NOTE on attribute reuse; §5.1.4 NOTE on
  distinguishing schemes; §5.2.2 NOTEs on `Period@duration` reuse
  and the AdaptationSet asymmetry) but no consolidated audit table
  and no explicit justification for `<svta:Concurrency>`,
  `<svta:Exclusions>`, `<svta:Pair>`, or `<svta:Metadata>` children
  (`<svta:Click>`, `<svta:AdSystem>`, `<svta:AdTitle>`,
  `<svta:UniversalAdId>`).
- **What an implementer does today**: nothing fails at runtime — the
  gap is governance, not behaviour. But a reviewer auditing R8
  compliance has to reconstruct the justification from the gap
  analysis rather than read it inline.

### G-8. Dual-version authoring pattern for cross-edition compatibility is named but unspecified

- **Spec section needing it**: §4.5 and §8.6 ("a Broadcaster authors
  a slot in dual form for backward compatibility"); Annex G.2
  parenthetical ("if the Broadcaster also declared the same slot via
  a known linear scheme as a dual-form fallback").
- **What context is missing**: `context/06-naming-and-namespaces.md`
  versioning rules cover URI bumping but never define a "dual-form
  fallback" authoring pattern. Context never establishes whether a
  Broadcaster can — or should — declare the same slot via two
  parallel events to maximise legacy reach. The spec invokes the
  idea three times without a constructor for it.
- **What an implementer does today**: a Broadcaster cannot author
  a dual-form slot conformantly because there is no normative rule
  for how the Player de-duplicates two events at the same
  `presentationTime` that resolve to the same slot.

---

## Edge cases (7)

Boundary conditions not contemplated in `context/04-use-cases.md` but
deployable Players will hit them.

### EC-1. `<svta:AllowedLayouts>` populated entirely with invalid tokens

- **Trigger**: Broadcaster authors `<svta:OverlayPresentation>` with
  `<svta:AllowedLayouts>` containing only `linear` and `pause-ad`
  (both invalid inside overlay per §5.1.3.1) — or a typo'd token not
  in §3.2.
- **Why it matters**: §5.1.3.1 says "raise validation error" for
  `linear` and "use `<svta:PauseAdTrigger>` instead" for `pause-ad`,
  but no spec section pins the Player's behaviour when every entry
  is invalid. §8.1 E7 (disallowed layout) operates per-form, not
  per-slot.
- **Responsible actor / context silence**: Player — context is silent.
  Likely outcome: §8.1 E2 (resolution document unparseable) or E6
  (no renderable form) after every candidate is filtered out, but
  neither row references the malformed `<svta:AllowedLayouts>`
  precondition.

### EC-2. Sub-placement refinement (`overlay-corner`) used when only the parent (`overlay`) is allowed

- **Trigger**: `<svta:AllowedLayouts><svta:Layout name="overlay"/></svta:AllowedLayouts>`
  and the ADS returns `<svta:RenderableAsset @layout="overlay-corner">`.
- **Why it matters**: §5.1.3.1 says "the refinement is recognised by
  the Player if and only if it is listed in `<svta:AllowedLayouts>`",
  so `overlay-corner` is NOT recognised when only `overlay` is
  listed. This is counter-intuitive — most readers would expect
  `overlay` to admit its refinements. Production candidates
  routinely carry the more specific layout; ADSs would have all
  refinements rejected against permissive Broadcaster declarations.
- **Responsible actor / context silence**: Broadcaster authoring
  rule. Context is silent on whether allowed-set semantics are
  enumeration-only or hierarchical.

### EC-3. Viewer pauses while a `<svta:OverlayPresentation>` is rendering

- **Trigger**: An overlay event is active (visible) and the user
  triggers pause. The overlay slot timeline is anchored to primary
  `presentationTime` — but primary is now paused.
- **Why it matters**: The overlay's slot window arithmetic (§7.5)
  ties beacon timing to "Broadcaster-declared overlay window".
  During pause, primary `presentationTime` does not advance — does
  the overlay window also pause, or does it continue against
  wall-clock? Quartile beacons fire on different schedules under the
  two readings.
- **Responsible actor / context silence**: Player — context is
  silent. `context/04-use-cases.md` UC-03 and UC-05 are mutually
  exclusive (one is active during primary playback, the other
  during pause) and the spec does not address their composition.

### EC-4. Co-located `<svta:OverlayPresentation>` and `<svta:PauseAdTrigger>`

- **Trigger**: Both event schemes carry an `<Event>` at the same
  Period such that the overlay event's `[presentationTime,
  presentationTime + duration)` interval contains a viewer pause.
- **Why it matters**: §5.1.5 covers co-location of linear + overlay
  but says nothing about non-linear + non-linear. On pause, does the
  Player resolve both endpoints, or treat the pause as an exclusion
  for the overlay? Concurrency cap (§5.1.3.2) is per-slot, so the
  two slots' caps are independent.
- **Responsible actor / context silence**: Player. Neither §7.6 nor
  context addresses this.

### EC-5. Late-arriving ADS response collides with R7 order preservation

- **Trigger**: ADS returns a §5.2.1 ListMPD with three candidates;
  the resolution document arrives before `presentationTime` but the
  Player has already fetched the first candidate's sub-MPD when a
  segment fetch fails (E10). The Player aborts the first candidate
  and falls to the second. The third candidate has now exceeded
  declared duration relative to fresh cap arithmetic.
- **Why it matters**: §8.1 E10 says "Resume the slot at the next
  candidate in declared order and re-apply cap arithmetic against
  rendered-so-far." But "rendered-so-far" for an aborted candidate
  is partial; the spec does not specify whether the aborted
  candidate's partial render counts. This affects R7.3 (drop before
  play) re-evaluation on candidate three.
- **Responsible actor / context silence**: Player. Context is silent
  on the rendered-so-far accounting when E10 fires mid-candidate.

### EC-6. `<svta:Exclusions>` references a layout not in `<svta:AllowedLayouts>`

- **Trigger**: `<svta:Pair @a="overlay-corner" @b="squeezeback-l-shape"/>`
  while `<svta:AllowedLayouts>` lists only `overlay-corner` and
  `overlay-lower-third`.
- **Why it matters**: The `@b` value is unenforceable because the
  Player would never accept `squeezeback-l-shape` anyway. Is the
  Broadcaster's manifest valid? §5.1.3.3 does not require
  `<svta:Pair>` operands to be members of `<svta:AllowedLayouts>`.
- **Responsible actor / context silence**: Broadcaster authoring.
  Context is silent.

### EC-7. Both ListMPD profile URIs declared, document carries no `<svta:RenderableAsset>`

- **Trigger**: ADS returns a document with
  `@profiles="urn:mpeg:dash:profile:list:2024
  urn:svta:dash:profile:sgai-overlay-list:2026"` and every `<Period>`
  has `<ImportedMPD>` only (no overlay-aware constructs).
- **Why it matters**: §5.2.2 says "the ADS MAY include both ... in
  which case the overlay-aware semantics apply". But "overlay-aware
  semantics" on a document with no overlay extensions is
  indistinguishable from linear-baseline semantics. Specifically,
  §5.2.1 ("A linear baseline ListMPD MUST NOT carry a
  `<svta:RenderableAsset>` under a `<Period>`") does NOT apply
  because §5.2.2 has been activated. The Player's validation path
  selection (§7.3 step 1) becomes non-deterministic on a degenerate
  case.
- **Responsible actor / context silence**: Player. Context is
  silent on the dual-profile degenerate case.

---

## Ambiguities (6)

### A-1. `Period@duration` semantics inside §5.2.2

- **Context passage**: spec §5.2.2 Period attributes table (line
  735): "Declared maximum duration of the candidate in this Period.
  For non-linear candidates the value matches the slot's `@maxDuration`
  window; for linear candidates it matches the candidate's intrinsic
  length."
- **Reading 1**: `Period@duration` is always the slot window cap for
  non-linear candidates. The Player should ignore intrinsic length.
- **Reading 2**: `Period@duration` is the maximum allowed by the
  candidate (a min(intrinsic, slot)). The Player uses it as the
  cap-arithmetic input.
- **Spec assumption**: Reading 1 is favoured by the §5.2.2 NOTE
  ("non-linear candidate match the slot's overlay window"). But the
  §7.3 step 3.g algorithm uses `declared_duration(FORM(C))` not
  `Period@duration`, so the two are not interchangeable in practice.
- **Tighter context sentence**: `context/03-requirements.md` should
  define which attribute carries the cap-arithmetic input for
  multi-form candidates, distinct from "slot window declaration".

### A-2. ADS remap normative or guidance

- **Context passage**: `context/03-requirements.md` R13.2 — "The
  Player SHOULD fire quartile beacons timed against the
  Broadcaster-declared overlay window, not against the ad's
  internal duration."
- **Reading 1**: The Player is responsible for the remap (re-times
  inbound beacons). But §7.5 of the spec forbids this ("The Player
  MUST NOT introduce its own beacon schedule").
- **Reading 2**: The ADS is responsible for emitting beacons whose
  `presentationTime` is already in slot-window time. The Player
  fires verbatim. This is what spec §5.5.4 / §7.2 step 5 / §7.5
  jointly assume — but no A-N entry in §4.3 codifies this.
- **Spec assumption**: Reading 2, but without normative force.
- **Tighter context sentence**: R13.2 should be split into two
  requirements: an ADS MUST emit beacons against the slot window
  for non-linear ads; the Player SHOULD fire them verbatim.

### A-3. Definition of "rendered-so-far" after E10

- **Context passage**: `context/05-dash-linear-interfaces.md` "the
  failure of an ad segment skips that ad or aborts the break per
  Player policy" (line 426).
- **Reading 1**: A candidate aborted mid-playback contributes its
  actual-rendered-length to cumulative cap arithmetic.
- **Reading 2**: A candidate aborted before any frame rendered
  contributes zero.
- **Spec assumption**: spec §8.1 E10 says "re-apply cap arithmetic
  against rendered-so-far" but never defines it precisely.
- **Tighter context sentence**: define `rendered-so-far` as "the
  cumulative wall-clock duration of frames actually presented" in
  the requirements vocabulary.

### A-4. `@earliestResolutionTimeOffset` unit

- **Context passage**: `context/06-naming-and-namespaces.md` §139–145
  flags the unit ambiguity but does not resolve it.
- **Reading 1**: Seconds throughout (matches `<ImportedMPD>`
  §5.3.2.6.1).
- **Reading 2**: `EventStream@timescale` units on
  `<InsertPresentation>` / `<ReplacePresentation>`; seconds on
  `<ImportedMPD>`.
- **Spec assumption**: Reading 1 ("in seconds" in §5.1.1/2/3/4 tables).
  But Annex B.2 example value `60000` is inconsistent with that.
- **Tighter context sentence**: pin the unit on each carrier in
  `context/06-naming-and-namespaces.md` §Naming consistency and add
  a sentence in `context/05-dash-linear-interfaces.md` that resolves
  the apparent ms vs seconds disagreement in the line-165 example.

### A-5. `<svta:AllowedLayouts>` enumeration vs hierarchical semantics

- **Context passage**: `context/04-use-cases.md` UC-03 broadcaster
  intent uses informal layout names ("banner, corner, L-shape").
- **Reading 1**: Enumeration — only exact tokens in the set are
  admissible (spec §5.1.3.1 sub-placement note adopts this).
- **Reading 2**: Hierarchical — if `overlay` is in the set, all
  refinements (`overlay-corner`, `overlay-lower-third`) are
  admissible.
- **Spec assumption**: Reading 1.
- **Tighter context sentence**: `context/04-use-cases.md` should
  explicitly state whether `<svta:AllowedLayouts>` is an enumeration
  or a hierarchical filter, and which sub-placement tokens require
  explicit listing.

### A-6. `<svta:Metadata>` as a tracking carrier and the §5.6.5 authoring rule

- **Context passage**: `context/06-naming-and-namespaces.md`:
  baseline children placed as **sibling** of an SGAI extension
  remain visible to legacy; placed inside, opaque.
- **Reading 1**: Tracking `<EventStream>` placed inside
  `<svta:Metadata>` (spec §5.5.3 case (b)) is opaque to legacy
  Players — intentional because tracking is irrelevant when the
  candidate itself is invisible.
- **Reading 2**: This contradicts the §5.6.5 authoring rule ("place
  the baseline element as a **sibling** of the SGAI extension, not
  as a child" when opacity matters), suggesting tracking should
  always be a sibling of `<svta:Metadata>`.
- **Spec assumption**: Reading 1 (case (b) is intentional).
- **Tighter context sentence**: context should state explicitly that
  tracking-inside-`<svta:Metadata>` is a legitimate carrier exception
  to the sibling-placement rule, with the rationale (no legacy
  consumption of non-linear beacons).

---

## R coverage map

| R   | Status   | Spec sections that satisfy it | Notes |
|-----|----------|-------------------------------|-------|
| R1  | full     | §1, §4.1, §4.4 P-1 / P-11, §4.5, §5.6.5, §7.7 (legacy row), §8.1 E5, Annex G | Ignore-if-unknown discipline well-covered across event scheme, foreign-namespace, profile URI; UC-07 walked end-to-end. |
| R2  | full     | §4.1 three-actor model, §4.2 B-1..B-6, §4.3 A-1..A-7, §4.4 P-1..P-12, §7 algorithm | Broadcaster declares, ADS provides, Player enforces — explicit in §4.1 normative load-bearing statement. |
| R3  | full     | §3.4 D1..D5 taxonomy, §7.7 per-device matrix, Annexes A.5/B.5/C.5/D.4/E.4/F.5 | Every (class × UC) cell defined; "decline gracefully" is a defined outcome (§7.7 footer). |
| R4  | partial  | §4.2 B-2, §4.4 P-5 / P-8, §7.3 algorithm steps 3.g / 4.c, §8.1 E8 / E9 | Cap enforcement specified, but cap arithmetic for non-video forms with absent `@duration` is undefined — see G-3. |
| R5  | partial  | §4.4 P-3 / P-6 / P-7, §5.3, §7.3 algorithm steps 3.b–3.f | Form selection algorithm specified, but `<svta:Concurrency @max>` enforcement missing from §7.3 — see G-2. |
| R6  | full     | §4.3 A-3, §5.5 (carrier shape + placement + non-video carrier), §6.5, §7.5 | Tracking carrier reuses callback scheme verbatim per R6.2 / R13.4. |
| R7  | full     | §4.4 P-4 / P-7 / P-8, §7.3 invariants ("order preservation"), §8.1 E8 | ADS-declared order is the algorithm's first invariant. |
| R8  | governance | §5.1.3 NOTE (attribute reuse), §5.1.4 NOTE (scheme distinction), §5.2.2 NOTEs (Period@duration / AdaptationSet asymmetry) | Scattered inline justifications; no consolidated R8 audit table per `context/07-backward-compat-checklist.md` §135 — see G-7. |
| R9  | governance | §5.1.3 (overlay reuses §5.10 EventStream), §5.4 (sub-MPD inherits SPS), §5.5 (no new tracking scheme), §5.2.2 (ListMPD shape reused), §7.4 (HTML5/CSS for layout) | Heavy reuse demonstrated; no parallel layout / tracking / event-stream surface. |
| R10 | governance | §3.2 IAB-derived layout vocabulary, §7.4 ("does NOT define a parallel layout standard"; defers to HTML5/CSS + IAB) | Spatial arrangement delegated; no spec-internal positioning system. |
| R11 | full     | §1 scope, §4.4 P-12, §6.6 (non-normative), Annex H.1 (non-normative) | No normative VAST reference; VAST entries confined to annex / non-normative notes per R11.3. |
| R12 | full     | §3.2 layout vocabulary (IAB), §4.2 B-6, §4.3 A-4 | 1:1 token mapping; spec MUST NOT add new top-level identifiers (§3.2 final paragraph). |
| R13 | partial  | §5.5.4, §7.5 (impression at visible, quartiles vs slot window, stop at trim), §8.1 E9 | Quartile semantics covered, but no normative ADS obligation to remap `presentationTime` to slot window — see G-5. |

Breakdown: **9 full**, **3 partial** (R4, R5, R13), **0 gap**,
**3 governance** (R8 partial-governance, R9 full-governance,
R10 full-governance) = 13 total (with R8 doubled as
partial+governance, counted as governance for the breakdown to sum to
13; in the stdout summary R8 reports as governance).

---

## Recommended context refinements

Top fixes by leverage, ordered by the number of downstream items
each unblocks.

### 1. Resolve the `@earliestResolutionTimeOffset` unit across baseline and SGAI events

Pin the unit on each carrier in
`context/06-naming-and-namespaces.md` §Naming consistency (currently
flagged as open at lines 138–145) and fix the apparent ms/seconds
disagreement in `context/05-dash-linear-interfaces.md` line-165
example. This single fix closes G-1 and A-4, and lets the spec
attribute tables (§5.1.1, §5.1.2, §5.1.3, §5.1.4) carry consistent
unit declarations. Highest leverage: every example currently
shipping a numeric value depends on this resolution.

### 2. Add a per-form `declared_duration` rule for non-video forms

Extend `context/03-requirements.md` R4 with a sentence specifying
the source of duration for cap arithmetic on non-AV forms: either
"the form's intrinsic `@duration` when present, else
`Period@duration`" or "`Period@duration` is authoritative for cap
arithmetic". This closes G-3 and A-1, and makes R7.3 drop-before-play
testable on overlay candidates. Without it, conformance tests on
non-linear pods cannot be written.

### 3. Add a Broadcaster constraint for the `@max` concurrency cap and a normative Player enforcement step

`context/03-requirements.md` R2.1 already lists "max number of
concurrent overlays" as a Broadcaster declaration. Add a Player
conformance criterion (R2.3.x) that the Player MUST NOT render more
than `@max` concurrent overlays during the slot, and reference it
from the §7.3 algorithm. Closes G-2. Without it, the
`<svta:Concurrency>` syntax is decorative.

### 4. Split R13.2 into an ADS MUST and a Player SHOULD

The current R13.2 is Player-side, but spec §5.5.4 / §7.2 / §7.5
place the obligation on the ADS. Add an ADS-side requirement
("R13.2.ADS — for non-linear slots, the ADS MUST emit callback
`<Event @presentationTime>` values measured against the
Broadcaster-declared slot window, not the ad's internal duration")
and keep the current R13.2 as the Player-side complement. Closes
G-5 and A-2. Cascades into §4.3 A-7.x.

### 5. Define the dual-form fallback authoring pattern

`context/06-naming-and-namespaces.md` versioning rules cover URI
bumping but never define how a Broadcaster co-authors a slot via
two event schemes simultaneously (e.g. a linear `<InsertPresentation>`
as a fallback to a new `<svta:OverlayPresentation>` so legacy
Players still see *some* ad). The spec invokes this pattern in
§4.5, §8.6, and Annex G.2 without a constructor. Either define the
pattern explicitly (with deduplication rules at the Player) or
remove the references. Closes G-8.

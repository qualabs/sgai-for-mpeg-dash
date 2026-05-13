[GROUNDED_BY=notebooklm]

# Norm validation — 2026-05-12

Built against:
- norm: `../output/sgai-norm-2026-05-12.md`
- context/ at git SHA: `ca19271`

This document captures gaps, edge cases, ambiguities, and the
R1..R13 coverage map surfaced during the 2026-05-12 norm build.
Findings here feed back into `../context/` — they are NOT part of the
norm itself.

---

## Gaps (8)

### G-01. Layout vocabulary for Pause Ad sub-positions

- **Norm section affected**: Chapter 3 §3.3; annex D §D.2.
- **Spec gap**: `../context/03-requirements.md` R12 mandates that the
  layout vocabulary maps 1:1 to IAB-defined values. The IAB doc lists
  `Fullscreen` and `Partial Screen` as the Pause Ad creative sizes,
  but does not give them canonical lowercase identifier names. The
  norm uses `fullscreen` and `partial-screen` as the kebab-case
  identifiers; the IAB document does not pin these spellings.
- **Implementer default today**: pick a kebab-case spelling and
  document it. Different implementations may drift.
- **Recommended spec refinement**: pin the canonical kebab-case names
  for IAB layouts in a new sub-section of `06-naming-and-namespaces.md`
  or in the glossary, with one row per IAB sub-position.

### G-02. Side-by-side as an allowed layout

- **Norm section affected**: Chapter 7 §7.2 (D2 sub-row mentions
  side-by-side); Chapter 3 §3.3.
- **Spec gap**: UC-03's D2 walk-through says side-by-side is an
  option "if the broadcaster allows it", but no spec file enumerates
  side-by-side as a layout value. The IAB doc has Squeezeback /
  Double-Box-Video patterns that fit this semantically, but the
  mapping from "side-by-side" (used in UC-03) to a specific IAB
  Squeezeback variant is not made explicit anywhere.
- **Implementer default today**: probably `double-box` or
  `frame` from Squeezeback. The norm chapter 7 §7.2 D2 row
  hand-waves with "if `side-by-side` is in `@allowedLayouts`"
  without resolving which IAB identifier this maps to.
- **Recommended spec refinement**: in `04-use-cases.md` UC-03,
  replace "side-by-side" with one of the canonical Squeezeback
  sub-position identifiers (`double-box`, `frame`,
  `double-box-background`) and update Chapter 7 §7.2 / annex B
  consistently.

### G-03. `@maxConcurrency` semantics on overlay slots

- **Norm section affected**: Chapter 5 §5.3, §5.5.
- **Spec gap**: `../context/02-actors.md` mentions "maximum number of
  concurrent overlays" as a Broadcaster-declared constraint, and
  UC-03 references "concurrency cap" in the D1 walk-through, but
  `../context/03-requirements.md` does not state a Player-side
  obligation to enforce it. The norm introduces `@maxConcurrency` on
  `<svta:OverlayPresentation>` but defines no specific Player
  behaviour for the case where two overlay slots overlap in time
  and their combined concurrent ad count would exceed an individual
  slot's cap (or some global cap).
- **Implementer default today**: enforce per-slot only; ignore
  cross-slot concurrency.
- **Recommended spec refinement**: add a conformance criterion under
  R2 or R4 (or a new R if neither fits) stating the Player's
  obligation when overlapping `<OverlayPresentation>` slots'
  concurrency budgets interact.

### G-04. Form `@duration` declared vs actual asset duration

- **Norm section affected**: Chapter 5 §5.6.2 (`<svta:Form>`).
- **Spec gap**: `../context/03-requirements.md` R7.5 (trim-during-play)
  presumes "the actual rendered length of an accepted candidate
  exceeds its declared duration", but does not state the canonical
  field that carries the declared length in a non-linear form. The
  norm uses `<svta:Form>` `@duration` for this, but the spec is
  silent on whether this is the form's intrinsic asset duration
  (which could be longer than the slot window) or the ADS-declared
  rendered duration for the slot (truncated to the cap).
- **Implementer default today**: assume `@duration` is the asset's
  intrinsic length; clamp at the slot cap.
- **Recommended spec refinement**: in `03-requirements.md` R7.5,
  pin the semantics of "declared duration" for non-linear forms:
  the intrinsic asset duration is the right anchor (the cap is
  separately declared on the slot).

### G-05. ADS error responses on non-linear slots

- **Norm section affected**: Chapter 8 §8.1.
- **Spec gap**: `../context/05-dash-linear-interfaces.md` documents the
  linear ADS error contract (empty `ListMPD`, HTTP errors, the
  silent-skip policy for tracking-only VAST `<Ad>` entries). The
  non-linear flow is not covered; specifically, what does an "empty
  non-linear `ListMPD`" look like (zero `<Period>` entries? a
  `<Period>` with an empty `<svta:CandidateForms>`?), and is either
  shape conformant for "no-fill"?
- **Implementer default today**: zero-Period `ListMPD` for no-fill.
- **Recommended spec refinement**: add a non-linear-specific section
  to `05-dash-linear-interfaces.md` (or a new spec file) that pins
  the no-fill shape and the error semantics for non-linear slots.

### G-06. Pre-fetch vs on-demand for pause-triggered slots

- **Norm section affected**: Chapter 6 §6.3 step 3; Chapter 8 §8.3.
- **Spec gap**: UC-05's notes flag the pre-fetch vs on-demand choice
  as an open spec decision; the spec does not pick. The norm leaves
  it as "implementation choice", which is conformance-safe but
  invites deployment drift.
- **Implementer default today**: pre-fetch is the lower-latency
  default; on-demand is the freshest-targeting default. Drift is
  likely.
- **Recommended spec refinement**: leave open OR pin one as the
  default with an opt-out — but the spec should record the WG's
  position. If left open, document it in `03-requirements.md` as a
  "not in conformance" choice so reviewers know it's deliberate.

### G-07. Cross-Broadcaster scheme URI versioning

- **Norm section affected**: Chapter 5 §5.2.
- **Spec gap**: `../context/06-naming-and-namespaces.md` states that a
  Player implementing edition N+1 SHOULD recognise both `:N:` and
  `:N+1:` URIs and treat them per the backward-compatibility rules.
  The spec does not specify what those rules are when both edition
  URIs appear in a single MPD — e.g. one `<EventStream>` carrying
  `urn:svta:dash:sgai-overlay:2026` and another carrying a future
  `urn:svta:dash:sgai-overlay:2027` with semantic changes.
- **Implementer default today**: prefer the newest URI; ignore the
  older one for the same slot. Drift likely if the spec does not
  pin this.
- **Recommended spec refinement**: in `06-naming-and-namespaces.md`,
  pin behaviour for the dual-URI case (newest wins; or both apply
  with documented precedence; etc.).

### G-08. Tracking metadata when no quartile beacons declared

- **Norm section affected**: Chapter 5 §5.8.
- **Spec gap**: R13 says the Player **SHOULD** fire quartile beacons
  against the Broadcaster-declared window. The spec does not
  prescribe what to do if the per-form sub-MPD's tracking
  `<EventStream>` declares an impression but no quartiles — should
  the Player synthesise quartile firing-instants against the window,
  or only fire what the sub-MPD declares?
- **Implementer default today**: only fire what the sub-MPD
  declares; do not synthesise.
- **Recommended spec refinement**: state explicitly in R13 that the
  Player MUST fire only the beacons declared in the sub-MPD; the
  SHOULD on quartiles binds the **ADS adapter / Broadcaster**'s
  obligation to declare them, not the Player's to synthesise them.

---

## Edge cases (5)

### E-01. Multi-ad break with mixed renderable / non-renderable candidates on D4

- **Trigger**: a `<ReplacePresentation>` slot returns a `ListMPD`
  with 3 candidates: candidate A has only an HTML5 interactive form
  (not renderable on D4), candidate B has a video form (renderable),
  candidate C has an HTML5 form (not renderable). Cumulative slot
  cap is 60 s.
- **Why it matters**: P-04 says skip A, render B, skip C — but R7.4
  says the Player MUST NOT re-order. Does "skipping" violate the
  no-reorder rule, or is skipping considered a drop (not a reorder)?
  The norm chapter 4 P-06 implies skipping is a drop, but the wording
  is "drops" plural — does the rule apply when multiple drops are
  non-contiguous?
- **Responsible actor**: Player. Spec is silent on the multi-drop
  edge case.

### E-02. Overlay slot whose `@maxDuration` is shorter than the shortest available form

- **Trigger**: `<OverlayPresentation>` declares
  `@maxDuration="5000"` (5 s), but the ADS returns candidates whose
  forms all have `@duration` ≥ 20 s. Drop-before-play would drop all
  candidates; declining the slot may be the right outcome, but the
  norm does not say whether the Player MUST drop based on declared
  duration or MAY accept and trim.
- **Why it matters**: declared duration exceeding the cap by 4x is a
  signal of misconfiguration; behaviour should be predictable.
- **Responsible actor**: Player. Spec is silent. The norm assumes
  the Player will pick one of the two behaviours per P-06.

### E-03. Pause-triggered slot fires immediately on re-entry to the window

- **Trigger**: user pauses inside the window, ad shown, user resumes,
  user pauses again 1 s later inside the same window. Should the ad
  fire again? Should it fire a different ad? Should it be
  rate-limited?
- **Why it matters**: cosmic-rays of bad UX — the user may
  re-pause repeatedly during natural viewing.
- **Responsible actor**: ADS (frequency capping) + Player (whether
  to issue a second resolution request). Spec is silent.

### E-04. ADS returns a candidate whose form sub-MPD is unreachable

- **Trigger**: the per-form sub-MPD URI in `<ImportedMPD>` returns
  HTTP 500. Other forms on the same candidate are reachable.
- **Why it matters**: should the Player fall through to the next
  form on the candidate (preserving the candidate), or skip the
  candidate entirely?
- **Responsible actor**: Player. The norm Chapter 8 §8.1 says
  "skips form and falls back to next form / candidate" — the form
  fallback is implicit but not pinned.

### E-05. Tracking beacon URL contains macros not resolved by ADS

- **Trigger**: a tracking `<Event>` text body contains
  `[TIMESTAMP]` or `[DEVICE_ID]` macros that the ADS expected the
  Player to resolve before firing.
- **Why it matters**: macro resolution is a VAST concept that the
  norm should explicitly disclaim (R11 — no VAST dependency). The
  Player should fire the URL verbatim, leaving macro resolution as
  an ADS-side responsibility.
- **Responsible actor**: norm document (clarify) + ADS adapter
  (resolve macros server-side).

---

## Ambiguities (4)

### A-01. "Renderable form" on D2 in overlay scenarios

- **Spec passage**: `../context/04-use-cases.md`:285-302 (UC-03 D2
  walk-through).
- **Readings**:
  - (a) D2 can render an overlay only if the candidate has a video
    form AND `side-by-side` is an allowed layout.
  - (b) D2 can render an overlay if the candidate has a video form,
    regardless of layout — the layout constraint is decoupled.
- **Norm draft assumed**: (a) — chapter 7 §7.2 D2 row states the
  video-on-video composition path explicitly and treats side-by-side
  as a fallback only when allowed.
- **Spec fix that would resolve it**: in UC-03 D2, restate the
  conditions on the video form's admissible layout intersected with
  the slot's allowed layout — make the two-step check explicit.

### A-02. "Skip the candidate" vs "skip the slot"

- **Spec passage**: `../context/03-requirements.md`:163-168 (R5.7) and
  `04-use-cases.md` D5 walk-throughs.
- **Readings**:
  - (a) "Skip the candidate" means walk past this candidate but try
    the next one; "skip the slot" means decline the entire slot.
  - (b) The phrases are used interchangeably; both mean abandon.
- **Norm draft assumed**: (a) — the norm chapter 4 P-04 and chapter
  7 use the distinction consistently.
- **Spec fix that would resolve it**: in `03-requirements.md` add a
  short glossary clarification at the top of the R5 / R7 sections.

### A-03. ERT window for `<svta:PauseAdPresentation>`

- **Spec passage**: `../context/04-use-cases.md`:507-525 (UC-05 D1).
- **Readings**:
  - (a) The ERT window for a pause-triggered slot starts at
    `presentationTime − @earliestResolutionTimeOffset` and ends at
    `@windowEnd`. The Player MAY resolve any time in this window.
  - (b) The ERT window is moot for pause-triggered slots; the
    resolution happens at the pause instant unconditionally.
- **Norm draft assumed**: (a) — chapter 6 §6.3 step 3 describes
  pre-fetch at ERT or on-demand at pause as both viable.
- **Spec fix that would resolve it**: pick one and add an explicit
  paragraph in UC-05 notes or in a new section of `03-requirements.md`.

### A-04. "Validation" vs "discard" of a non-conforming candidate

- **Spec passage**: `../context/02-actors.md`:81-84 ("any candidate
  that violates the constraints… is discarded").
- **Readings**:
  - (a) Validation happens once, up-front; non-conforming candidates
    are discarded before form/layout selection.
  - (b) Validation is interleaved with form/layout selection — a
    candidate may pass slot-level validation but fail per-form
    validation (e.g. form's `@admissibleLayouts` is a subset of the
    slot's `@allowedLayouts` but the device cannot render).
- **Norm draft assumed**: (b) — chapter 4 P-02 + P-03 + P-04
  describe a two-stage process where slot validation and per-form
  device-fitness are sequential, and per-candidate selection can
  fail at either stage.
- **Spec fix that would resolve it**: tighten R2.3 to make the
  two-stage validation explicit (slot constraints first, then
  per-form device-fitness during form selection).

---

## R1..R13 coverage map

| Req | Norm chapter(s) / annex(es) | Coverage | Residual |
|-----|------------------------------|----------|----------|
| R1 (ignore-if-unknown) | Chapter 4 §4.1 B-05, §4.3 P-09; Chapter 5 §5.10 (audit table); Chapter 7 §7.5; Annex E (T-E1..T-E3) | full | — |
| R2 (actor roles) | Chapter 4 §4.1, §4.2, §4.3; Chapter 6 §6.1, §6.4; Chapter 7 (per-actor walk-throughs) | full | — |
| R3 (device classes) | Chapter 3 §3.2; Chapter 4 §4.3 P-01; Chapter 7 (per-class behaviour matrix) | full | — |
| R4 (max slot duration) | Chapter 4 §4.1 B-02; Chapter 4 §4.3 P-05; Chapter 5 §5.3 attribute table; Chapter 6 §6.2 / §6.3 | full | — |
| R5 (device-aware selection) | Chapter 4 §4.3 P-03, P-04; Chapter 5 §5.6.2 (CandidateForms / Form schema with intersection of three); Chapter 7 §7.2 / §7.4; Annex B | full | — |
| R6 (tracking carrier) | Chapter 4 §4.4 D-02; Chapter 5 §5.8; Chapter 8 §8.5 (vendor metadata) | full | — |
| R7 (ADS-returned order) | Chapter 4 §4.3 P-06; Chapter 8 §8.1 (precedence) | partial | E-01 (multi-drop edge case ambiguous) |
| R8 (justify additions) | Chapter 5 §5.2 (URI rationale), §5.10 (audit table) | partial | The norm justifies each new construct inline but does not include an explicit "why couldn't existing X be reused?" paragraph per construct. |
| R9 (minimise net new constructs) | Chapter 4 §4.4 D-02 (reuse callback scheme); Chapter 5 §5.6.1 (linear `ListMPD` reused); Chapter 5 §5.7 (SPS reused) | full | — |
| R10 (no layout system) | Chapter 4 §4.4 D-04; Chapter 5 §5.5 (uses HTML/CSS via overlay surface); Chapter 6 §6.3 step 7 | full | — |
| R11 (no VAST dependency) | Chapter 4 §4.2 A-06, §4.3 P-10, §4.4 D-05; Chapter 8 §8.5 (vendor metadata is the VAST-equivalent carrier) | full | — |
| R12 (IAB owns ad types) | Chapter 2 (normative reference to IAB doc); Chapter 3 §3.3 (table sourced from IAB); Chapter 4 §4.1 B-03, §4.4 D-03 | full | G-01 (kebab-case identifiers not pinned by IAB doc — minor) |
| R13 (non-linear tracking) | Chapter 4 §4.3 P-08, §4.4 D-02; Chapter 5 §5.7 (offsets against parent window), §5.8 | partial | G-08 (Player vs ADS responsibility for declaring quartiles) |

---

## Recommended spec refinements

Top 5 priorities for the next spec iteration, ranked by leverage
(unblocks the most other items / reduces the most norm-side
handwaving):

1. **Resolve A-04 / G-04 by pinning the two-stage validation
   semantics in R2.3 and the form `@duration` semantics in R7.5**.
   This single refinement disambiguates how Player conformance is
   measured for non-linear ad selection and unblocks G-04, A-04,
   and partially A-02.

2. **Resolve G-02 by pinning the canonical IAB identifier for
   "side-by-side"** in UC-03's D2 walk-through. The norm chapter 7
   §7.2 currently hand-waves; pinning the IAB sub-position (probably
   `double-box` from Squeezeback) makes the D2 row crisp and
   removes the dangling "if `side-by-side` is in `@allowedLayouts`"
   conditional.

3. **Resolve G-01 by pinning canonical kebab-case identifiers for
   IAB layouts** in `06-naming-and-namespaces.md`. One row per IAB
   sub-position (`corner-overlay`, `lower-third-overlay`, `l-shape`,
   `frame`, `double-box`, `double-box-background`, `fullscreen`,
   `partial-screen`). Without this, every implementation rolls its
   own spelling and `@allowedLayouts` becomes ambiguous.

4. **Resolve G-03 (cross-slot concurrency) by adding a Player
   obligation under R2 or R4**. Right now the norm's chapter 5
   defines `@maxConcurrency` but chapter 4 / chapter 7 do not
   define what the Player does when two overlay slots overlap. A
   one-sentence conformance criterion would close this.

5. **Tighten R13 to clarify the Player's beacon obligation
   (G-08)**. The current "SHOULD fire quartile beacons" wording
   binds the Player to fire what the sub-MPD declares, not to
   synthesise. Pinning this prevents drift where Players invent
   quartile timings the ADS did not intend.

After these five, items E-01 / E-04 / G-05 (multi-drop edge case,
form-failure fallback, non-linear ADS error contract) are the next
tier — they affect Player behaviour in production but are recoverable
by per-implementation policy.

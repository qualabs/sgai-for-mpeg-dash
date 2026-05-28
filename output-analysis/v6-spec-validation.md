[GROUNDED_BY=spec-only]

# Spec validation — v6 (2026-05-28)

Built against:
- spec: `../output/v6-sgai-spec.md`
- context/ at git SHA: `d30c655`

## Scope

This validation is the v6 major-build sidecar. v6 is the first
major iteration after the four-actor split (Publisher / ADS / APS
/ Player) and the addition of R20, R21, R22, R25, R26 to the
context. The spec rewrites §3 / §4 around the four-actor contract
and absorbs the new requirements into §4.6 (Player obligations),
§5.1 (event constructs), §5.3.7 (background fill) and §7.5
(per-scenario behaviour).

The findings below are produced by walking the v6 spec end-to-end
(chapters 1–8 plus Annexes A–K) against `../context/` and
`../context-analysis/`. NotebookLM is not available in this
spec-only validation pass; the per-construct DASH 6th conformance
check is left to the §8 DASH conformance audit.

## Gaps (4)

### G-1. Click-tracking beacon lifecycle after slot trim remains unspecified

**Spec section needing it**: §4.6.10, §8.1 (E12), §8.3.

**Issue**: Carried forward from v5 G-3 / v5.1 G-1. `context/` is
silent on whether a viewer click after a slot trim (§4.6.3 E10)
fires the click-tracking beacon carried by `<svta:Click>`
(§5.6.1) or suppresses it. R13.3 says the Player MUST stop
firing scheduled beacons at the trim boundary — but a click
beacon is event-triggered, not schedule-triggered, and the
spec's §5.6.1 description ("URL the Player fires as a tracking
beacon at the moment of viewer interaction") does not pin the
boundary condition. Both readings are defensible:

- *Fire opportunistically* — consistent with §8.1 E12
  fire-and-forget semantics and the principle that user
  interaction is intent-driven, independent of cap arithmetic.
- *Suppress after trim* — consistent with the spirit of R13.3
  (the Player stopped honouring the candidate's tracking
  schedule at the trim boundary) and §8.1 E7.

**Implementer fallback today**: Player implementers will pick
one, fragmenting the click-tracking ledger across deployments.

### G-2. Default uncovered-region behaviour for `squeezeback-double-box` (no background variant)

**Spec section needing it**: §3.2 (layout enum row),
§5.3.7 (background fill rules).

**Issue**: §3.2 declares the token `squeezeback-double-box`
(without the `-with-background` suffix) and says "the uncovered
region between them is filled with the **Player's default
fallback**". §5.3.7 only describes the three-element rule for
`squeezeback-double-box-with-background` and gives a precedence
ladder (advertiser → Publisher fallback → "Player's default
uncovered-region behaviour"). `context/03-requirements.md` R26
covers the `+Background` case explicitly and is silent on the
plain `double-box` token. Two questions are unresolved:

1. Why does the spec carry two adjacent tokens
   (`squeezeback-double-box` and `squeezeback-double-box-with-background`)
   instead of one with a derived "has background" flag? R26
   speaks of side-by-side / double-box as one IAB layout with a
   `MAY` background fill — not two layouts.
2. The "Player's default fallback" wording is normative in §3.2
   but underspecified in §5.3.7 ("typically a uniform fill"). An
   implementer cannot ship without a concrete decision.

**Implementer fallback today**: ship a black band; an
opt-in-driven uniform colour fill; or quietly conflate the two
tokens.

### G-3. `<svta:RenderableAsset>` exposes layout tokens with no slot construct (`menu-ad`, `screen-saver-ad`, `companion-ad`)

**Spec section needing it**: §3.2 (vocabulary), §5.1
(event constructs), §7.5 (per-scenario behaviour).

**Issue**: §3.2 and §5.3.3 enumerate `menu-ad`,
`screen-saver-ad`, `companion-ad` as admissible `@layout`
values, but the spec defines no slot-bearing event scheme,
constraint, or rendering contract for them. They appear with
slot-family annotations like `(CTV UI)`, `(device-initiated)`,
`(out-of-player)` — none of which corresponds to an
`<EventStream>@schemeIdUri` introduced in §2.1. A Publisher
authoring an MPD has no construct to declare a "menu-ad" slot
through; an APS emitting a candidate with
`@layout="screen-saver-ad"` has no parent event the Player
could trace it back to.

**Implementer fallback today**: implementers either treat
these tokens as dead enum entries (silent skip per §8.1 E8) or
infer a non-normative mapping. The cleanest read of the
context-analysis IAB mirror (`iab-ad-templates.md`) is that
these tokens are reserved for future editions and should not
appear in `@allowedLayouts` or `@layout` in this edition —
that decision is not stated.

### G-4. `<ImportedMPD>` placement inside a foreign-namespace parent

**Spec section needing it**: §5.3.4 (carrier for video forms).

**Issue**: §5.3.4 reuses `<ImportedMPD>` "verbatim from §5.3.2.6
of the base specification" but places it as a child of
`<svta:RenderableAsset>`. Per DR-3
(`context/08-dash-extension-rules.md`), a baseline DASH
element wrapped inside a foreign-namespace parent is invisible
to legacy parsers — which is the intended authoring move. But
DASH 6th's §5.3.2.6 binds `<ImportedMPD>` as a child of a
baseline `<Period>` (the SPS profile carrier). The spec does
not state whether placing `<ImportedMPD>` inside a foreign
parent satisfies the DASH 6th §5.3.2.6 schema contract, nor
whether the SPS-binding inheritance (DR-1) still applies when
the parent path runs through a foreign namespace. Both readings
are defensible from the prose; neither is grounded in
`context/`.

**Implementer fallback today**: implementers either accept the
authoring-by-extension move (legacy-safe per DR-3, treat
DR-1's binding as travelling with the `<ImportedMPD>` element
itself) or flag a schema-validation warning and look for a
different carrier (DR-6(b) Event Stream payload). The two
choices lead to different sub-MPD structures.

## Edge cases (4)

### EC-1. Hybrid slot where the overlay window is **longer** than the linear window

**Trigger**: Carried forward from v5 EC-1 / v5.1 EC-1.
Publisher authors a hybrid (UC-04) where the linear
`@maxDuration` is shorter than the co-located overlay
`@maxDuration`.

**Why it matters**: §5.1.5 says the two events are
"independent at authoring time and at runtime". §7.5.4 walks
the D1..D5 outcomes for the take-over portion plus the
overlay, but does not describe what happens after the linear
ad ends and the overlay window still has time on the clock.
Does the overlay continue composited on top of resumed
primary content? §4.6.8 (R17) only governs the pause-ad /
overlay crossover. The independent-event model would imply
the overlay continues against primary until its own window
expires — but the spec does not say so explicitly.

**Responsible actor**: Publisher declares; Player enforces.
Context-level — UC-04 needs an explicit walk for this
boundary.

### EC-2. Pause-trigger window overlapping a linear ad break

**Trigger**: Publisher declares a
`<svta:PauseAdPresentation>` window whose
`presentationTime`+`duration` straddles a co-scheduled
`<ReplacePresentation>` linear break.

**Why it matters**: When the viewer pauses *during* the
linear ad (inside the pause-trigger window), what does the
Player do? §4.6.7 (R16.1) governs pause-ad lifecycle bound
to pause state; §4.6.11 (R20.1) governs same-family overlap.
But this is a **cross-family** overlap: linear vs
pause-trigger. R17 covers pause-ad over overlay, not
pause-ad over linear. §7.5.5 (pause-triggered ad) assumes
the viewer is in primary content when the pause occurs.

**Responsible actor**: Publisher declares; Player resolves.
The context is silent.

### EC-3. Empty resolution document on the *first* same-family overlapping window

**Trigger**: Two overlapping `<svta:OverlayPresentation>`
windows; the APS for the first responds with HTTP 200 and an
**empty** `<svta:OverlayList>` (§5.2.2.2, §8.1 E2).

**Why it matters**: §4.6.11 (R20.1) says the Player falls
through to a subsequent overlapping window ONLY when it
cannot **access** the resolution document of the first.
§8.1 E2 says an empty resolution document is a successful
fall-through to primary content. Combining the two: an
empty document from the first window is "accessible" — so
the Player must NOT fall through to the second window.
The viewer sees no ad at all even though the second window
could have served one. Is this intentional? `context/`
treats accessibility and content as distinct concerns and
does not state the conjunction.

**Responsible actor**: Player. The Publisher cannot author
around it.

### EC-4. Background fill image fails to load (404 / decode failure) for `squeezeback-double-box-with-background`

**Trigger**: The Player commits to a candidate's
`squeezeback-double-box-with-background` option; the
advertiser-supplied `<svta:BackgroundFill>@assetUrl` or the
Publisher's `@backgroundFallback` URL fetch fails.

**Why it matters**: §5.3.7 enumerates the precedence
(advertiser → Publisher fallback → "Player's default
uncovered-region behaviour") but does not say what the
Player does when the chosen source fails *mid-render*. Is
this an E11 (mid-render asset failure → skip the candidate)
or a graceful degrade to the next source in the precedence
ladder? §8.1 E11 says "cease rendering the candidate" — but
the failure is on the third element, not the ad. The IAB
"Double Box Video + Background" definition is silent on
this.

**Responsible actor**: Player. Both readings produce
defensible outcomes; context picks neither.

## Ambiguities (5)

### A-1. Spec-side ad-type identifiers diverge from the IAB mirror

**Spec passage**: §3.2 (table of accepted layout vocabulary).

**Spec-side IAB-derived identifiers proposed in
`context-analysis/iab-ad-templates.md`** (§"Mapping to spec
chapter 3", live mirror dated 2026-05-28): `pause`, `menu`,
`squeezeback`, `overlay`, `in-scene`, `screensaver`,
`companion`, `linear`.

**Spec v6 §3.2 identifiers**: `linear`, `pause-ad`, `menu-ad`,
`squeezeback`, `overlay`, `in-scene`, `screen-saver-ad`,
`companion-ad`.

**Two readings**:
(i) The `-ad` suffix is a spec-side disambiguation move
("layout token, not ad-type") — the underlying IAB mapping
is 1:1, R12.2 is satisfied because every value still maps
back to an IAB-defined ad type.
(ii) The IAB doc's identifiers ARE the verbatim IAB names;
adding `-ad` is a spec invention that violates R12.2's "names
that map 1:1 to IAB-defined ad-type values".

**Reading assumed by v6**: (i). The §3.2 prose explicitly
calls them "spec-side identifiers that map 1:1 to IAB-defined
names" but does not show the per-row mapping back to the IAB
mirror, so the reader cannot audit it.

**Tighter context sentence**: `context-analysis/iab-ad-templates.md`
SHOULD either adopt the `-ad` suffix in its proposed
identifiers (sync with v6 §3.2) or the spec SHOULD drop the
suffix on the four affected tokens. Either way the mapping
needs to be visible to a reader in one place. R12.2 itself
could be tightened to state whether "1:1" admits a
consistent suffix transformation.

### A-2. `@maxConcurrency` admissible value is fixed at `1` — DP-1.1 tension

**Spec passage**: §5.1.3.1 (`<svta:OverlayPresentation>`
attribute table).

**Two readings**:
(i) The attribute is a positive declaration of the runtime
contract at authoring time; static readers see the
constraint on the slot. The spec defends the choice in the
attribute's description.
(ii) DP-1.1 (`context/03-requirements.md` Design principles)
explicitly forbids constructs whose only admissible value is
fixed by another rule (R22). `@maxConcurrency` with sole
admissible value `1` is precisely the case DP-1.1 declares
out of scope.

**Reading assumed by v6**: (i). The defence is inline.

**Tighter context sentence**: DP-1.1 SHOULD state whether
authoring-time-declarative attributes are an admissible
exception, and on what test. Without that, every reviewer
re-litigates the same DP-1.1 vs "explicit-contract"
trade-off.

The same critique applies to
`<svta:PauseAdPresentation>@allowedLayouts` (§5.1.4.1), which
requires the token `pause-ad` and ignores any other token at
runtime — a single-admissible-value field by another path.

### A-3. Annex C / Annex I use `linear` inside `<svta:OverlayPresentation>@allowedLayouts`, contradicting §5.3.3

**Spec passage**: Annex C.2, Annex I.2 (`@allowedLayouts`
declarations); §5.3.3 (layout enum, "Slot families" column).

**The contradiction**: Annex C declares
`allowedLayouts="squeezeback-double-box-with-background
squeezeback-l-shape overlay-corner linear"` on an
`<svta:OverlayPresentation>` event. §5.3.3 states that the
`linear` token's "Slot families" are "linear insert, linear
replace" — i.e. NOT non-linear overlay. Yet the per-class
walk (§C.5, §I.4) relies on the `linear` token being a
satisfiable last-resort option for D2 and D5.

**Two readings**:
(i) §5.3.3's "Slot families" column documents the primary
slot family for each token, not an exhaustive admissibility
restriction. `linear` can legitimately appear in a non-linear
slot's `@allowedLayouts` as a "takeover" fallback.
(ii) §5.3.3 is normative; admissibility is by exact match;
Annex C is the bug.

**Reading assumed by v6**: (i), but the spec does not state
the takeover-fallback semantics anywhere — the reader has
to infer it from the Annex tables.

**Tighter context sentence**: either §5.3.3's "Slot families"
column SHOULD become advisory (with explicit language) or
the spec SHOULD add a paragraph defining when `linear` is
admissible as an overlay fallback (the "takeover" idiom).
`context/04-use-cases.md` UC-03 / UC-09 already exercise the
takeover-as-fallback pattern; the cross-family-vocabulary
question is the gap.

### A-4. §4.6.11 broadens R20.1's "cannot access" to include late-arrival

**Spec passage**: §4.6.11 (overlapping same-family windows);
`context/03-requirements.md` R20.1.

**Two readings**:
(i) R20.1's "cannot access" already encompasses late arrival
— a resolution document that arrives after the slot has
elapsed is *de facto* inaccessible. §4.6.11's enumeration
("transport failure, malformed response, late arrival") is
just a more explicit restatement.
(ii) R20.1's "cannot access" means transport-level
inaccessibility (E1); late arrival (E13) is a distinct
condition the spec is silently merging. R20.1's example
clause says "the APS does not respond or the event URL
fails", which sounds narrower than what §4.6.11 admits.

**Reading assumed by v6**: (i).

**Tighter context sentence**: R20.1 SHOULD state explicitly
whether late arrival counts as a fallback trigger. The
enumeration in §4.6.11 should match.

### A-5. Tracking carrier may live in two places for video forms (§5.5.2 + §5.4.2 union with de-duplication)

**Spec passage**: §5.5.2 ("MAY live inside the candidate's
video sub-MPD or directly inside the `<svta:Candidate>`");
§5.4.2 ("the union of beacons is fired by the Player;
duplicate beacons ... are de-duplicated").

**Two readings**:
(i) The APS is free to author the carrier in either
location; Player-side de-duplication is the cleanup. The two
locations are "functionally equivalent" (§5.5.2 wording).
(ii) R13.1 says the APS "exercises no discretion over the
schedule — it neither adds, removes, nor reorders beacons".
Two-location authoring with Player-side de-duplication is
the same beacon listed twice; the APS arguably added a
duplicate. R13.1 does not contemplate authoring-location
flexibility.

**Reading assumed by v6**: (i). The Player-side
de-duplication mechanism is concrete but not justified
against R13.1.

**Tighter context sentence**: R13.1 SHOULD state whether the
APS may carry the schedule in more than one location, and
which actor is responsible for resolving duplicates. v5.1
A-1 had a related "single-rooted beacon set" tightening
sentence in §5.5.4 — v6 has replaced that with the union
rule, but the underlying ambiguity is the same.

## R coverage map

| R    | Status     | Spec sections that satisfy it | Notes |
|------|------------|-------------------------------|-------|
| R1.1 | full       | §4.6.1, §5.1.3.4, §5.1.4.2, §7.5.9, §8.8, Annex G | — |
| R1.2 | full       | §2.1, §5.1.3, §5.1.4, §5.2.2, §8.8 (audit table) | — |
| R1.3 | full       | §1, §5.1.1, §5.1.2 (verbatim reuse), §5.4 (SPS reuse) | — |
| R2.1 | full       | §4.3 (Publisher obligations bullet list) | — |
| R2.2 | full       | §4.4 (ADS not constraint-bound), §4.5 (APS not enforcer) | — |
| R2.3 | full       | §4.6.2 (constraint validation) | — |
| R2.4 | full       | §4.2 (four-actor authority table) | — |
| R3.1 | full       | §3.4 (device-class table) + §7.5 per-scenario per-class behaviour | — |
| R3.2 | full       | §4.6, §7.5, §8.1 (E4) | — |
| R3.3 | full       | §4.6.5 (capability check), §8.1 E4 | — |
| R4.1 | full       | §4.3 (`@maxDuration` on every slot), §5.1.1–§5.1.4 | — |
| R4.2 | full       | §4.6.3 ("Player stops rendering at the cap boundary") | — |
| R4.3 | full       | §4.6.3 (positive cap-keeping obligation) | DP-2 inherited from v5. |
| R4.4 | full       | §4.4 (ADS not bound by slot constraints), §8.1 E6 | — |
| R4.5 | full       | §4.6.3 (trim-during-play), §8.1 E7, §5.4.1 | — |
| R5.1 | full       | §4.5 (APS preserves option order), §5.3.5 (document order = preference) | — |
| R5.2 | full       | §4.6.5 (Player walks options in document order) | — |
| R5.3 | full       | §4.6.5 ("skips the candidate"), §8.1 E4 | — |
| R5.4 | full       | §3.4 (Player sole authority), §4.4, §4.5 | — |
| R5.5 | full       | §5.2.2.4, §5.3 (multiple options ordered list) | — |
| R5.6 | full       | §4.6.5 (three-way intersection: media type + layout + surfaces) | — |
| R5.7 | full       | §4.6.5 ("proceeds to the next candidate") | — |
| R6.1 | full       | §5.5 (tracking carrier specified) | — |
| R6.2 | full       | §4.5 (APS transcribes into callback scheme), §5.5.1 | — |
| R6.3 | governance | §5.5 ("No new tracking scheme is introduced") | — |
| R6.4 | full       | §4.6.1 (graceful degradation inherits to tracking carrier), §8.8 | — |
| R7.1 | full       | §4.6.4, §7.4 | — |
| R7.2 | full       | §4.6.5 ("skips the candidate") | — |
| R7.3 | full       | §4.6.3 (drop-before-play) | — |
| R7.4 | full       | §4.6.4 ("remaining candidates' relative order is preserved") | DP-2 inherited. |
| R7.5 | full       | §4.6.3 (trim-during-play) | — |
| R8.1 | partial    | §8.8 (per-construct extension-point table) | v6 drops the inline "considered reuse, chose new" Justification blocks v5.1 carried per construct. §8.8 names the extension point but does not articulate why an existing baseline construct could not be reused per construct. Tracked as refinement gap. |
| R8.2 | full       | §1.2 (out-of-scope), §5.5 (no new tracking scheme rationale) | — |
| R9.1 | full       | §5.1.1, §5.1.2 (verbatim reuse), §5.5 (callback scheme reuse), §5.2.1 (ListMPD reuse), §5.4 (SPS reuse), §5.7 (UrlParamInfo reuse) | — |
| R9.2 | partial    | Same as R8.1 — no inline "extension considered, new construct chosen" prose per new construct (§5.1.3, §5.1.4, §5.2.2). | Tracked as refinement gap. |
| R9.3 | partial    | Same as R9.2. | — |
| R10.1 | governance | §1.2 (HTML5/CSS for spatial), §3.1 (Layout entry), §7.5.2 | — |
| R10.2 | governance | §1.2 (no parallel layout system) | — |
| R10.3 | governance | §1.2 (positioning out of scope) | — |
| R11.1 | governance | §6.6 explicitly non-normative; §3.3 abbrev calls VAST "illustrative only" | — |
| R11.2 | full       | §3.1 (Player def — ADS-agnostic), §4.6 (no VAST mention) | — |
| R11.3 | governance | §6.6 ("non-normative") | — |
| R12.1 | governance | §2 (live IAB ref), §3.2 (IAB-sourced vocabulary) | — |
| R12.2 | full       | §3.2, §4.3 (Publisher uses §3.2 tokens) | Caveat A-1: spec-side identifiers diverge from the IAB mirror's proposed identifiers (`pause-ad` vs `pause`, etc.). |
| R12.3 | full       | §4.5 (APS uses §3.2 tokens), §3.2 | — |
| R13.1 | full       | §4.4 (ADS authority on schedule), §4.5 (APS transcribes verbatim), §5.5 | Caveat A-5: §5.5.2 / §5.4.2 union-with-dedup is a softening relative to R13.1's "APS adds no beacons". |
| R13.2 | full       | §4.6.10 (Player executes schedule) | — |
| R13.3 | full       | §4.6.3 ("Tracking beacons whose scheduled relative time is greater than the trim boundary are not fired"), §8.1 E7 | — |
| R13.4 | governance | §5.5 (no new tracking scheme introduced) | — |
| R14.1 | full       | §4.6.6 (Player presents sequential forms in document order), §7.5.5 | — |
| R14.2 | full       | §4.6.3 + §4.6.6 (cap against cumulative form duration) | — |
| R14.3 | governance | §1.2 (no parallel non-linear ad rendering), §4.6.6 (single active form), §5.3.5 (no priority attribute) | — |
| R15.1 | governance | §3.2 (admissible set table), §5.3.2 (enum), §1.2 (carriers outside set OOS) | — |
| R15.2 | full       | §4.3 (Publisher uses admissible carriers), §4.5 (APS emits `@mediaType` from §3.2), §3.2 | — |
| R15.3 | full       | §4.6.5 (Player skips non-admissible options), §8.1 E8 | — |
| R16.1 | full       | §4.6.7 ("within one rendering frame") | — |
| R16.2 | full       | §4.6.7 ("ceases firing tracking beacons scheduled after the transition") | — |
| R17.1 | full       | §4.6.8 ("renders the pause-ad form and suspends the overlay surface") | — |
| R17.2 | full       | §4.6.8 ("dismisses the pause-ad and restores the overlay surface") | — |
| R17.3 | full       | §4.6.8 ("keeps the overlay surface clear") | — |
| R17.4 | governance | §4.6.8 (positive obligation only — implicit absence of inversion construct) | No explicit "spec carries no construct that lets X invert this priority" statement; relies on implicit absence. Refinement opportunity. |
| R18.1 | governance | §5.1 (MPD event URL pattern), §5.2 (resolution document formats), §6 (Player-visible interfaces) | — |
| R18.2 | governance | §1.2 (out-of-scope), §4.3 (Publisher↔APS contract bilateral), §4.5 (APS↔ADS opaque) | — |
| R19.1 | full       | §4.6.9 (Player renders at primary's playback speed) | — |
| R19.2 | full       | §4.6.9 (no force to 1x — positive obligation form) | The "MUST NOT force" R19.2 wording is implied by the positive "renders at the same speed" statement; DP-2 positive-obligation refactor inherited. |
| R19.3 | full       | §4.6.9 (`duration / playback_speed` derivation), §8.6 (image-form intrinsic duration) | — |
| R20.1 | full       | §4.6.11 (first-window-wins-with-fallback), §7.5.8, §8.1 E1/E13 | Caveat A-4: §4.6.11 enumerates "late arrival" as a fallback trigger; R20.1's "cannot access" wording is narrower. |
| R21.1 | full       | §4.6.7 ("fullscreen, occupying the entire screen surface; MAY release resources") | — |
| R22.1 | full       | §4.6.6 (single active form), §1.2 (OOS for parallel) | — |
| R23.1 | full       | §5.6 (vendor-namespaced extension elements: `<svta:Click>`, `<svta:UniversalAdId>`, `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>`), §4.5 | — |
| R24.1 | full       | §5.3.1 (`@assetUrl` direct on `<svta:RenderableAsset>` for image / html; DR-6(a) carrier), §5.3.4 (video reaches sub-MPD via `<ImportedMPD>` — DR-1) | Caveat G-4: `<ImportedMPD>` placement inside a foreign-namespace parent is an open authoring question. |
| R25.1 | full       | §4.6.7 ("freezes its presentation time inside the window") | — |
| R26.1 | full       | §5.3.7 (background fill as composition attribute; not a presentation option) | — |
| R26.2 | full       | §4.6.12 (Player composites three elements; advertiser → Publisher fallback ladder), §5.3.7 | — |
| R26.3 | full       | §5.3.7 (device class table: element count + type determines admissibility) | — |

**Tallies**: 59 full / 3 partial / 13 governance / 0 gap.

## Recommended next-iteration context refinements

Ordered by leverage — the higher-ranked refinements unblock the
most spec-side ambiguity or close the most R-coverage residuals.

1. **Specify click-tracking beacon lifecycle after slot trim
   (G-1)** in `context/03-requirements.md` R13.3. The current
   wording covers schedule-driven beacons but not the
   user-interaction-driven click beacon. Resolution unlocks the
   §4.6.10 / §8.1 E12 / §8.3 lifecycle question and removes a
   gap that has carried since v5. Suggested addition: an R13.5
   clause stating whether click-tracking beacons fire on viewer
   interaction after the candidate has been trimmed.

2. **Clarify cross-family vocabulary admissibility in §5.3.3
   (A-3)** — either by stating that the "Slot families" column
   is advisory (and naming the `linear`-as-takeover-fallback
   idiom explicitly) or by tightening the column to strict
   admissibility (and pulling `linear` out of the Annex C / I
   `@allowedLayouts` examples). Without this fix, every
   Annex-C-style example carries a contradiction that has to
   be re-explained at every read. Lives best in
   `context/03-requirements.md` R5 / R12 or in a new
   subsection of `04-use-cases.md` UC-09.

3. **Add UC-04 hybrid edge case for overlay-outlasts-linear
   (EC-1)** in `context/04-use-cases.md`. The independent-event
   model of §5.1.5 is silent on what happens after the linear
   ad ends while the overlay window is still live. A one-paragraph
   addition to UC-04's Notes / open questions, or a dedicated
   D1..D5 walkthrough, would close EC-1 (carried from v5.1).

4. **Resolve the `squeezeback-double-box` vs
   `squeezeback-double-box-with-background` token split (G-2)**
   in `context-analysis/iab-ad-templates.md` and reflected in
   §3.2. Either (a) drop the un-suffixed token (IAB's "Double
   Box" already implies the background; the IAB doc treats it
   as one layout), or (b) define the default uncovered-region
   behaviour normatively when no background is supplied. R26
   should pick one.

5. **Tighten R13.1 to cover authoring-location flexibility
   for the tracking carrier (A-5)**. Either (a) state that the
   APS authors the schedule in a single canonical location
   (sub-MPD for video; candidate for non-video), and the Player
   does not need a union-with-dedup rule; or (b) state that
   multiple locations are admissible and define the
   de-duplication contract normatively in `context/`. v6's
   §5.5.2 / §5.4.2 split codifies (b) without grounding it in
   R13.1; v5.1 §5.5.4 codified a flavour of (a). Pick one
   for v7.

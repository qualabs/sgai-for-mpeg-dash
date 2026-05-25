[GROUNDED_BY=spec-only]

# Spec validation — v5 (2026-05-20)

Built against:
- spec: `../output/v5-sgai-spec.md`
- context/ at HEAD (current)

## Scope

This validation is the v5 peer-review sidecar. v5 is a **major
build** (from-scratch rewrite) rather than a minor refinement of
v4.2. It absorbs:
- v4.2's normative surface (chapters 1–8 + annexes).
- v4.2's carried-forward "Refinement gaps" list — the gaps that
  required architectural / requirement-level changes a minor
  refinement could not address.
- The DP-2 positive-obligations refactor required by
  `context/03-requirements.md` Design Principles (no `MUST NOT`
  enumerations in normative obligations).
- The DP-1 / DP-1.1 / DP-1.2 simplification pass (no
  "future-flexibility" attributes whose only admissible value is
  the default; no redundant duplicates).
- Integration of R14 (single concurrent non-linear form), R16
  (pause-ad lifecycle bound to pause state), R17 (pause-ad
  priority over overlay), R18 (ADS API not defined by this spec)
  — all present in `context/03-requirements.md` but not surfaced
  in v4.2.
- Integration of UC-08 (overlay × pause-ad composition) from
  `context/04-use-cases.md` — new in context, absent from v4.2.

## Gaps (3)

### G-1. `<svta:OverlayPresentation>@maxConcurrent` was removed in v5; the underlying R14 obligation needs an explicit anchor

**Spec section needing it**: §4.4.7, §4.4.8 (and `[inferred]`
across §5.1.3 / §5.1.4).

**Issue**: v4.2 carried `@maxConcurrent` as a Broadcaster-
declared attribute with `default="1"` and a normative rule
"the value MUST be exactly `1`". Per DP-1.1, that attribute is
exactly the "construct whose only admissible value matches the
default" pattern the design principle forbids. v5 removes the
attribute and moves the obligation to §4.4.7 ("at any time t the
Player presents at most one non-linear ad form") and §7.6
(serialisation of overlay × pause-ad). The behaviour is captured
correctly, but `context/` does not specify whether a future
relaxation of R14 would re-introduce `@maxConcurrent` as a
Broadcaster lever or use a different mechanism — implementers
auditing for R14 conformance now anchor against §4.4.7, not a
manifest attribute.

**Implementer fallback today**: relies on §4.4.7 Player
obligation; no manifest signal to flag the constraint per slot.

### G-2. Form-tie-break preference order remains `[inferred]`

**Spec section needing it**: §7.3 step 5 (3).

**Issue**: The Player's form-selection algorithm picks the form
with the highest `@priority` among admissible forms, breaking
ties on `@mediaType`. The default order
`video > html > image` is tagged `[inferred]` because
`context/` does not state a normative tie-break vocabulary —
neither R5.2 ("best form it can render") nor R5.6 ("intersecting
device, allowedLayouts, ADS priority") prescribe a tie-break
between two forms with identical `@priority` and admissible
`@layout`. Two conforming Players could pick `video` and `html`
respectively for the same candidate. This is a stable
implementer behaviour question, not a backward-compat issue.

**Implementer fallback today**: Players pick per local policy;
testability of TC-12 across implementers depends on whether the
`@priority` values are distinct.

### G-3. Click-tracking lifecycle vs slot trim is unspecified

**Spec section needing it**: §4.4.9, §8.3.

**Issue**: §4.4.9 introduces a click-tracking beacon on
`<svta:Click>@trackingUrl` that fires on viewer interaction.
§8.3 (late callbacks) addresses quartile beacons after trim
(§4.4.6) but does not state whether a click-tracking beacon
issued by the viewer **after** the slot has been trimmed (§4.4.3,
E10) — i.e. the viewer clicks the ad surface after the Player
has dismissed the ad — fires or is suppressed. The
`<svta:Click>` does not have a `presentationTime`, so the
quartile-stop rule does not apply directly. `context/` is silent
on the click lifecycle's boundary with R4 / R13.3 (the trim rule).

**Implementer fallback today**: Players either fire the click
opportunistically (consistent with E12 fire-and-forget
semantics) or suppress after trim (consistent with the spirit
of R13.3); both are defensible.

## Edge cases (4)

### EC-1. Hybrid slot where the overlay window is **longer** than the linear window

**Trigger**: Broadcaster authors a hybrid (UC-04) where the
linear event's `@maxDuration` is shorter than the overlay
event's `@maxDuration`.

**Why it matters**: §5.1.5 in v5 states "the shorter window
governs the overlay's display: the overlay is dismissed at
whichever of its own `@maxDuration` or the underlying linear
slot's end comes first". The text declares it an authoring error
and the enforcement is clamp-to-linear-end, but `context/04-use-cases.md`
UC-04 does not visit the case; it assumes the overlay ≤ linear.
The decision encoded in v5 (clamp) is sensible but
context-derived.

**Responsible actor**: Broadcaster declares; Player enforces
the clamp.

### EC-2. `<svta:Click>@through` URL is malformed or points at an unreachable host

**Trigger**: Candidate carries `<svta:Click @through="javascript:..."
@trackingUrl="..."/>` or a non-routable host.

**Why it matters**: §4.4.9 says "the Player opens the `@through`
URL via the device's URL-opening mechanism". When the URL is
malformed or unreachable the Player's behaviour on the open
attempt is host-environment dependent. The spec does not
distinguish "open succeeded" from "open failed", and `context/`
does not address it (R6.4 / R6 are about carrier, not click
semantics).

**Responsible actor**: Player (per host platform); ADS / Broadcaster
SHOULD validate the URL out of band.

### EC-3. Pre-roll non-linear: Broadcaster authors `<svta:OverlayPresentation>` at `presentationTime=0` on the first Period

**Trigger**: Conflict with §4.6 ("Pre-roll non-linear scope")
which states the scheme URIs are reserved for non-zero
`presentationTime` in this edition.

**Why it matters**: §4.6 forbids the authoring but does not
specify the Player's behaviour when it encounters it. Two
sensible behaviours: (i) treat as authoring error, fall through
silently per §4.4.1; (ii) process normally because the scheme
URI is recognised. v5 leaves this unspecified.

**Responsible actor**: Player. `context/` does not specify a
behaviour either.

### EC-4. Resolution document arrives with `<Period>@duration` value other than `PT0S`

**Trigger**: ADS authors `<MPD>` envelope of an Overlay Resolution
Document where `<Period>@duration` is set to a non-zero value
(say `PT20S`).

**Why it matters**: §5.2.2 chooses `<Period>@duration="PT0S"` to
satisfy §5.3.2.2 Table 4 ("non-zero-duration Period requires at
least one AdaptationSet") without authoring an AdaptationSet
inside the resolution document. An ADS that emits a non-zero
duration violates the spec implicitly. The Player's behaviour is
unspecified (parse and ignore? reject as schema-invalid?).

**Responsible actor**: ADS; Player MAY treat as E2 (schema-invalid).

## Ambiguities (3)

### A-1. Quartile-beacon timing reference choice on `<svta:RenderableAsset>` carrying both an `<ImportedMPD>` and an inline `<EventStream>`

**Spec passage**: §5.5.2 lists two carrier locations (inside
sub-MPD vs inside `<svta:RenderableAsset>`); §5.5.4 says the
preferred non-linear placement is the latter.

**Two readings**: (i) When both are present, the inline
`<svta:RenderableAsset>`-attached `<EventStream>` wins because
it carries the slot-window timing; (ii) Both fire — the sub-MPD
events fire against the ad's intrinsic timeline and the inline
events against the slot window — yielding double beacons per
quartile.

**Reading assumed by v5**: §5.5.4 prose says "fire quartile
beacons timed against the slot window" implying the inline
`<EventStream>` is the canonical carrier when present, but the
spec does not exclude the sub-MPD events from firing
concurrently.

**Tighter context sentence**: `context/03-requirements.md`
R13.x SHOULD state that the spec's beacon-set per form is
single-rooted (i.e. when both carriers are present on a video
form, the inline `<EventStream>` wins and the sub-MPD events
are suppressed for that rendering instance).

### A-2. `<svta:Candidate>@priority` vs declared candidate order

**Spec passage**: §5.2.2 `<svta:Candidate>@priority` is
described as informational; §4.4.4 says the Player honours
declared candidate order.

**Two readings**: (i) `@priority` is a hint the ADS provides
for diagnostics only; (ii) `@priority` is a tie-break the
Player MAY consult when two adjacent candidates in declared
order have identical pre-filtering admissibility.

**Reading assumed by v5**: (i). §5.2.2 explicitly says "the
Player honours the declared candidate order". This works in
practice (ADS ranks while constructing the document) but the
attribute is then redundant with the declaration order — a
DP-1.2 concern (single source of truth).

**Tighter context sentence**: `context/03-requirements.md` R7
SHOULD state whether `@priority` is purely diagnostic (drop
from the document) or a Player-side tie-break (keep, with
explicit semantics).

### A-3. Speculative pre-fetch for pause ads — staleness threshold

**Spec passage**: §8.5 says the Player MAY pre-fetch the
pause-ad resolution at MPD load time.

**Two readings**: (i) The pre-fetched response is valid for the
duration of the pause-trigger window (potentially hours on
long-form content); (ii) The Player should refresh on a
Player-side staleness threshold.

**Reading assumed by v5**: (i). §8.5 is non-normative; the spec
implicitly accepts whatever the Player chooses.

**Tighter context sentence**: `context/` MAY clarify whether a
pause-ad's pre-fetch has a normative staleness boundary, or
whether it's purely Player-side.

## R coverage map

| R   | Status | Spec sections that satisfy it | Notes |
|-----|--------|-------------------------------|-------|
| R1.1 | full | §4.4.1 (graceful degradation), §G.2 / §G.3 (UC-07 walk-through) | — |
| R1.2 | full | §4.2 B-4 (carrier closure), §5.1.3 / §5.1.4 (DR-2 / DR-6 carriers), §8.8 (audit table) | — |
| R1.3 | full | §5.1.1 / §5.1.2 (linear constructs reused verbatim), §6.1 (no baseline override) | — |
| R2.1 | full | §4.2 B-1, B-2, B-3 (Broadcaster declares in MPD) | — |
| R2.2 | full | §4.3 (ADS not required to enforce constraints) | — |
| R2.3 | full | §4.4.2 (constraint validation), §4.4.5 (form selection) | — |
| R2.4 | full | §4.1 ("Every construct introduced by this specification is expressible within this contract") | — |
| R3.1 | full | §3.4 (device classes table) + §7.7 (per-device-class behaviour) | — |
| R3.2 | full | §4.4.5, §7.3, §7.7 | — |
| R3.3 | full | §4.4.5, §7.3 step 5 (1) | — |
| R4.1 | full | §4.2 B-2 (Broadcaster declares `@maxDuration` on every slot) | — |
| R4.2 | full | §4.4.3 ("stops rendering at the cap boundary, even mid-ad") | — |
| R4.3 | full | §4.4.3 (positive obligation: "keeps the slot bounded by the declared cap") | DP-2 refactor of v4.2's "MUST NOT extend past the cap". |
| R4.4 | full | §4.3 (ADS not required to enforce slot cap) | — |
| R4.5 | full | §4.4.3 (trim during play), §5.4.1 (sub-MPD vs form duration reconciliation) | — |
| R5.1 | full | §4.3 A-2, §5.3 (RenderableAsset with multiple forms per candidate) | — |
| R5.2 | full | §4.4.5, §7.3 step 5 (3) | — |
| R5.3 | full | §4.4.5 ("skips that candidate") | — |
| R5.4 | full | §4.3 ("not required to maintain a device-class matrix") | — |
| R5.5 | full | §5.3 (multiple forms per candidate; multiple `@layout` options across forms) | — |
| R5.6 | full | §4.4.5 (three-way intersection), §7.3 step 5 (1) | — |
| R5.7 | full | §4.4.5 ("falls through to the next candidate"), §7.3 step 5 (2) | — |
| R6.1 | full | §5.5 (tracking carrier) | — |
| R6.2 | full | §4.3 A-4, §5.5.1 (callback scheme reused) | — |
| R6.3 | full | §5.5 (no new tracking scheme introduced) | — |
| R6.4 | full | §5.6.3 (vendor namespace), §4.3 ADS MAY clause | — |
| R6.5 | full | §4.4.10 (unknown-namespace tolerance) | — |
| R6.6 | full | §4.2 B-5 (non-AV asset URLs via carriers, not via `@mimeType` on AdaptationSet axis), §5.3.4 NOTE | — |
| R7.1 | full | §4.4.4, §7.3 step 5 | — |
| R7.2 | full | §4.4.5 ("skips that candidate") | — |
| R7.3 | full | §4.4.3 (drop before play) | — |
| R7.4 | full | §4.4.4 ("preserves the relative order of the remaining candidates") | DP-2 refactor of v4.2's "MUST NOT re-order, deduplicate". |
| R7.5 | full | §4.4.3 (trim during play) | — |
| R8.1 | full | §5.1.3 / §5.1.4 (Justification block per new construct), §8.8 audit table | New in v5: per-construct R8 / R9 justification blocks. |
| R8.2 | full | §1.2 (out-of-scope list), §5.2.2 (ListMPD rejected as non-linear carrier) | — |
| R9.1 | full | §5.1.1 / §5.1.2 (linear constructs reused verbatim), §5.5 (tracking callback scheme reused) | — |
| R9.2 | full | §5.1.3 / §5.1.4 justification blocks | — |
| R9.3 | full | §5.2.2 justification block (ListMPD considered, rejected; Overlay Resolution Document introduced) | — |
| R10.1 | governance | §7.4 (HTML5/CSS for spatial positioning) | — |
| R10.2 | governance | §1.2 ("A parallel spatial-layout system is OOS"), §7.4 | — |
| R10.3 | governance | §1.2, §7.4 | — |
| R11.1 | governance | §6.6 (VAST description is non-normative; cited as illustrative only) | — |
| R11.2 | full | §4.3 (ADS-side protocol not part of this spec's contract) | — |
| R11.3 | governance | §6.6 ("non-normative" prefix; illustrative table only) | — |
| R12.1 | governance | §2 (live IAB link), §3.2 (mapping table 1:1 to IAB names) | — |
| R12.2 | full | §4.2 B-3 (token set drawn from §3.2 vocabulary) | — |
| R12.3 | full | §4.3 A-6 (ADS uses only §3.2 tokens) | — |
| R13.1 | full | §4.4.6 (impression beacon at visible instant) | — |
| R13.2 | full | §4.4.6, §5.5.4 (quartile beacons against slot window) + §4.3 A-5 (ADS authors against slot window) | New in v5: A-5 is the ADS leg complementing the Player leg in v4.2. |
| R13.3 | full | §4.4.6 ("stops firing remaining quartile beacons at the trim boundary") | — |
| R13.4 | full | §5.5 ("No new tracking scheme is introduced") | — |
| R14.1 | full | §4.4.7 (at most one non-linear form at any time t) | New in v5 (v4.2 had `@maxConcurrent` instead). |
| R14.2 | full | §1.2, §4.4.7, §8.1.1 (precedence order ensures serialisation) | — |
| R15.1 | full | §3.2 (admissible set enumerated once), §5.3.2 | — |
| R15.2 | full | §4.3 A-3, §5.3.2 enum | — |
| R15.3 | full | §4.4.5, §8.1 E8 | — |
| R16.1 | full | §4.4.8 ("removes the rendered pause-ad form from the screen within one rendering frame") | New in v5 (R16 missing from v4.2). |
| R16.2 | full | §4.4.8 ("stops firing pause-ad tracking beacons") | New in v5. |
| R17.1 | full | §4.4.8 ("renders the pause-ad form on top and suspends the overlay rendering"), §7.6 | New in v5. |
| R17.2 | full | §4.4.8 ("restores the overlay rendering when the overlay slot window is still active"), §7.6 | New in v5. |
| R17.3 | full | §4.4.8 ("keeps the overlay surface clear") | New in v5. |
| R17.4 | full | §1.2 (pause-ad priority is not Broadcaster-configurable), §4.4.8 | New in v5. |
| R18.1 | full | §1.2, §4.3 (Player-visible interface only; ADS-side protocol opaque) | New in v5 (v4.2 did not formalise R18). |
| R18.2 | full | §4.3 (ADS-Broadcaster bilateral contract out of band) | — |

**Summary**:
- Total R conformance rows: 56
- full: 49
- partial: 0
- gap: 0
- governance: 7 (R10.1/.2/.3, R11.1/.3, R12.1)

## Recommended context refinements

1. **C-1. State the form tie-break vocabulary** in
   `context/03-requirements.md` R5. v5's §7.3 step 5 (3) uses
   `[inferred]` for the `video > html > image` default — resolving
   it in context removes G-2 entirely and removes spec
   ambiguity across implementers.
2. **C-2. State the `<svta:Candidate>@priority` semantics
   explicitly** in `context/03-requirements.md` R7. Either drop
   the attribute (keep declared order as the single source of
   truth per DP-1.2) or specify the tie-break behaviour
   normatively. v5 §5.2.2 keeps it as informational, but it
   currently fails the DP-1.2 test ("the same value or
   relationship appears in multiple places — exactly ONE
   declaration is canonical").
3. **C-3. Resolve the click-lifecycle vs trim question** in
   `context/03-requirements.md` R13 (R13.5 candidate). The
   click-tracking beacon's behaviour after trim (G-3) is
   currently spec-side ambiguous; a one-line addition closes it.
4. **C-4. Re-author UC-04 (`context/04-use-cases.md`)** to
   include the overlay-longer-than-linear sub-case (EC-1). v5
   §5.1.5 encodes the clamp-to-linear-end behaviour but the use
   case does not visit it; readers SHOULD see it in the UC.
5. **C-5. State the pre-roll non-linear Player behaviour
   explicitly** in `context/04-use-cases.md` UC-01 or in
   `context/03-requirements.md`. v5 §4.6 declares the
   prohibition but does not specify the Player's response on
   encountering it (EC-3); a one-line normative behaviour
   closes the edge case.

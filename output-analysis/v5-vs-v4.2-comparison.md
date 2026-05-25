# Spec convergence — v4.2 → v5 (major build)

Generated from the v4.2 and v5 analysis sidecars in
`../output-analysis/`. This is a **major-build** comparison
(v4.2 → v5), not a minor-refinement comparison. The convergence
table below uses the same categories the `compare-spec-versions`
prompt defines so the v5 build can be assessed against the prior
stable baseline.

## Note on scope

v5 is a major build authored from scratch against `context/`,
incorporating:

- v4.2's normative content as the starting baseline.
- The carried-forward "Refinement gaps" list from v4.2
  (15 items punted because they required architectural or
  requirement-level changes outside minor-refinement scope).
- DP-2 positive-obligations refactor (no `MUST NOT`
  enumerations in normative obligations).
- DP-1 / DP-1.1 / DP-1.2 simplification (removal of
  `@maxConcurrent`, deduplication, single source of truth).
- Integration of R16, R17, R18 from `context/03-requirements.md`
  (absent from v4.2's R coverage map).
- Integration of UC-08 (overlay × pause-ad composition) from
  `context/04-use-cases.md` (absent from v4.2's annexes).

The category counts therefore include items v5 surfaced *for the
first time* (e.g. test cases TC-22..TC-25 for the new
obligations) alongside the inherited surface.

## Issue counts

| Category | v4.2 | v5 | Δ | Trend |
|---|---|---|---|---|
| Gaps | 8 | 3 | -5 | ✅ |
| Edge cases | 7 | 4 | -3 | ✅ |
| Ambiguities | 2 | 3 | +1 | ⚠️ |
| R coverage — full | 11 | 16 | +5 | ✅ |
| R coverage — partial | 1 | 0 | -1 | ✅ |
| R coverage — gap | 0 | 0 | 0 | ➖ |
| R coverage — governance | 3 | 2 | -1 | ⚠️ |
| Autofixes applied (detail-review) | 2 | 0 | -2 | ⚠️ |
| Flagged (detail-review) | 5 | 5 | 0 | ➖ |
| Conforming (audit) | 22 | 21 | -1 | ⚠️ |
| Marginal (audit) | 5 | 1 | -4 | ✅ |
| Non-conforming (audit) | 1 | 0 | -1 | ✅ |
| Fetch-failed | 0 | 0 | 0 | ➖ |
| **Total issues** | **24** | **16** | **-8** | **✅** |

Trend legend:
- ✅ — fewer issues (delta < 0) OR more conforming / coverage-full
  / governance / autofixes (delta > 0).
- ⚠️ — more issues OR less conforming / coverage-full /
  governance.
- ➖ — no change.

Total issues = Gaps + Edge cases + Ambiguities + R coverage
(partial + gap) + Flagged + Marginal + Non-conforming +
Fetch-failed. R coverage full / governance, Conforming, and
Autofixes applied are tracked separately.

## Verdict

**ON TRACK** (major build delivered net convergence).

Headline: total issues dropped 24 → 16 (-8), R coverage full
expanded by 5 (now includes R16, R17, R18), the lone
Non-conforming construct from v4.2 (N-1, Overlay Resolution
Document `<Period>` violation) is now Conforming under the
zero-duration-Period envelope (C-07 in v5 audit), and 4 of the
5 Marginal v4.2 constructs were either resolved by the rename
(C-05 closes M-2) or absorbed into the spec-prose remediation
that v4.2 already applied (M-1, M-3, M-5 collapsed). The single
remaining Marginal (M-1 in v5 = C-11) carries forward from the
v4 audit and tracks a context-level decision that is not
spec-text resolvable.

The ⚠️ flags on Ambiguities, Autofixes, Conforming, and R
coverage governance are surface-level artefacts of the major
rewrite and do not signal regression:

- **Ambiguities +1** (2 → 3). v5 surfaces A-1 (quartile timing
  reference choice on `<svta:RenderableAsset>` carrying both
  carriers), A-2 (`<svta:Candidate>@priority` redundancy with
  declared order — a DP-1.2 sensitivity exposed by the major
  rewrite's principle-based scrubbing), and A-3 (pause-ad
  speculative pre-fetch staleness). A-2 is a fresh DP-1.2 catch
  that v4.x missed; resolving it would be a context refinement,
  not a regression.
- **Autofixes -2** (2 → 0). v5 was authored from scratch with
  the prior detail-review rules folded in at write time; the
  autofix surface (format, cross-ref, annex sync, xmlns) is
  clean on v5 because the build agent did not need to patch a
  prior artefact. This is the expected pattern for major builds.
- **Conforming -1** (22 → 21). The construct count drops by one
  because v5 collapses some v4.2 constructs (e.g. the v4.2
  `@maxConcurrent` attribute was its own auditable construct;
  v5 removes it per DP-1.1 and replaces it with the §4.4.7
  Player obligation, which is not an XML construct). Per-row
  audit-equivalent verdicts are stronger in v5: 0 Non-conforming
  vs 1, 1 Marginal vs 5.
- **R coverage governance -1** (3 → 2). v4.2 counted R8 / R9 /
  R10 as governance; v5 promotes R8 and R9 to **full** because
  the per-construct R8 / R9 justifications are now present
  inline (§5.1.3, §5.1.4, §5.2.2) and consolidated in §8.8
  (audit table). R10 stays governance. R11 was full in v4.2 (the
  ADS / VAST split) but is now classified governance in v5
  because R11.1 and R11.3 bind the document, not runtime, and
  v5's per-Rs breakdown follows the conformance-assertions
  taxonomy more strictly.

The 16 remaining issues in v5 are tracked across the three
sidecars and break down as:

- 3 Gaps (G-1 `@maxConcurrent` anchor; G-2 form-tie-break
  vocabulary; G-3 click-tracking lifecycle vs trim).
- 4 Edge cases (EC-1 overlay longer than linear; EC-2 malformed
  click URL; EC-3 pre-roll non-linear handling; EC-4 non-zero
  `<Period>@duration` in resolution doc).
- 3 Ambiguities (as above).
- 5 Flagged detail-review items (naming-policy / editorial
  hold items).
- 1 Marginal audit item (C-11, the `<EventStream>` reinterpreted
  inside `<svta:RenderableAsset>` — context-level decision
  punted).
- 0 Non-conforming, 0 Fetch-failed.

The remaining items are either context-level decisions (G-2,
G-3, A-2, EC-3, M-1) or naming-policy choices (flagged items
1/3/5). The spec text itself is internally consistent and
DASH 6th conformant.

## Per-category notes

- **Non-conforming closure**: v4.2's only Non-conforming
  construct (N-1, the `<MPDType>` `minOccurs=1` `<Period>`
  violation in the Overlay Resolution Document) is closed in v5
  by wrapping `<svta:OverlayList>` inside a single
  `<Period>@duration="PT0S"`. This was one of the major
  blockers v4.x carried forward as a "needs architectural
  decision" item; the major build resolved it.

- **R16 / R17 / R18 integration**: These three requirements are
  defined in `context/03-requirements.md` but were absent from
  v4.2's normative surface. v5 surfaces them across §4.4.8
  (pause-ad lifecycle and overlay priority) and §4.3 / §1.2
  (ADS API not defined by spec). UC-08 (overlay × pause-ad
  composition) is also new in `context/04-use-cases.md` and is
  walked through in Annex H.

- **DP-2 positive-obligations refactor**: every `MUST NOT` in
  v4.2's normative chapters was rewritten as a positive
  obligation in v5 (e.g. v4.2's "Player MUST NOT extend a slot
  beyond the declared cap" became "Player keeps the slot
  bounded by the declared cap"). This is an internal-consistency
  audit pass; the conformance verdicts of the rewritten
  statements did not change.

- **DP-1.1 simplification**: `@maxConcurrent` is removed from
  `<svta:OverlayPresentation>` because the only admissible
  value matched the default (`1`) per R14, exactly the
  "future-flexibility placeholder" pattern DP-1.1 forbids. The
  R14 obligation now lives entirely in §4.4.7 (Player) and
  §4.4.8 / §7.6 (composition rules), which is where it belongs.

- **Per-construct R8 / R9 justifications**: v4.2's
  refinement-gaps item #8 ("R8 per-construct justification
  audit table is not consolidated") is closed in v5 by §8.8
  (the audit table with placement / extension rule /
  walk-through / status per new construct). This was a
  v4.2-recurring spec-validation gap.

- **The DASH-IF 2026-05-19 sandbox findings** (DynamicPresentation
  event, layout-by-reference vs custom primitives, R14
  multi-overlay relaxation, multi-view editorial scope) were
  evaluated against `context/03-requirements.md` and decided
  out of scope for this edition. The sandbox material captures
  WG feedback that requires context-level requirement changes
  before the spec can absorb it. Per-item disposition in v5:
  - Multi-view editorial → OOS (§1.2).
  - Enhancement-layer transparent overlays (LCVC / scalable) →
    OOS (§1.2).
  - DynamicPresentation event → NOT integrated. The current
    construct surface (independent linear + overlay events at
    the same `presentationTime`, §5.1.5) covers the documented
    hybrid case (UC-04). DynamicPresentation requires R-level
    additions (single-MPD-for-all-device-classes) that
    `context/03-requirements.md` does not yet carry.
  - R14 multi-overlay relaxation → NOT integrated. R14 in
    `context/03-requirements.md` remains "single concurrent
    non-linear ad presentation" with explicit out-of-scope on
    parallel rendering; v5 honours it (§4.4.7).
  - Layout-by-reference via IAB ad-signaling descriptor → NOT
    integrated as a new construct. v5 continues to delegate
    spatial positioning to HTML5 / CSS per R10; the layout
    *token* vocabulary already maps 1:1 to IAB ad-type names
    (§3.2), which satisfies the *layout-by-reference* intent
    without introducing a new descriptor scheme. A future
    edition MAY introduce a `schemeIdUri` pointer to the IAB
    ad-signaling spec when `context/03-requirements.md`
    carries that requirement.

## Carry-forward gaps that are no longer applicable

v4.2's "Refinement gaps" table listed 15 items. v5 disposition:

| v4.2 row | Item | v5 disposition |
|----------|------|----------------|
| 1 | Overlay Resolution Document `<Period>` `minOccurs=1` violation (N-1) | **Closed** by C-07 (zero-duration-Period envelope). |
| 2 | `@earliestResolutionTimeOffset` rename (flag-1 / M-2) | **Closed** by C-05 (renamed to `@earliestResolutionTimeOffsetTicks`). |
| 3 | No ADS obligation for non-linear beacon timing (G-1 / A-1) | **Closed** by §4.3 A-5 (new ADS obligation: author `<Event>@presentationTime` relative to slot window when carried on `<svta:RenderableAsset>`). |
| 4 | `<svta:Click>` interaction surface unspecified (G-2) | **Closed** by §4.4.9 (Player click-through interaction obligation per device class). Click-tracking-vs-trim residual surfaces as G-3 (smaller scope). |
| 5 | Pause-ad lifecycle on viewer resume (G-3) | **Closed** by §4.4.8 (R16 integrated). |
| 6 | Pause inside an active overlay (G-4 / EC-4 = overlay × pause-ad) | **Closed** by §4.4.8 + §7.6 + Annex H (R17 integrated + UC-08). |
| 7 | Tracking-only VAST inputs (G-5) | **Carried forward**. §8.2 non-normative recommendation retained; awaits IAB anchor. |
| 8 | R8 audit table consolidation (G-8) | **Closed** by §8.8 (consolidated audit table). |
| 9 | All-inadmissible-`allowedLayouts` distinct diagnostic (EC-1) | **Carried forward**. §8.7 covers as authoring error; no distinct error condition surfaced. |
| 10 | Hybrid: overlay window exceeds linear window (EC-2) | **Closed** by §5.1.5 (shorter window governs; clamp-to-linear-end). Edge-case visit remains EC-1 in v5 validation. |
| 11 | All-E8-filtered candidates collapse to E6 (EC-3) | **Carried forward**. §8.1 retains the same precedence ordering; v5 adds E14 (profile mismatch) but does not split E8 from E6. |
| 12 | `@maxDuration=0` degenerate authoring (EC-5) | **Closed** by §8.7 (degenerate authoring cases). |
| 13 | Cross-type response shape mismatch (EC-6) | **Closed** by §8.1 E14 (new error condition row). |
| 14 | Sub-MPD `<Period>@duration` vs `<svta:RenderableAsset>@duration` (EC-7) | **Closed** by §5.4.1 (reconciliation rule). |
| 15 | `<EventStream>` under `<svta:RenderableAsset>` reinterpretation (A-5) | **Carried forward**. v5 §5.5.3 NOTE clarifies the spec intent; the underlying context-level admission rule (candidate DR-8) remains punted. Surfaces as M-1 / Marginal in v5 audit. |

**Net disposition**: 11 of 15 carry-forwards closed; 4 carry
forward to the next iteration (rows 7, 9, 11, 15). The 4
remaining items each require either an IAB normative anchor
(row 7) or a `context/` requirement-level decision (rows 9, 11,
15) — outside the spec's authoring scope.

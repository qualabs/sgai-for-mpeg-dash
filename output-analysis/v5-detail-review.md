[GROUNDED_BY=spec-only]

# Spec detail review — v5 (2026-05-20)

**Review target**: `../output/v5-sgai-spec.md`.
**Reference**: `../context/` at HEAD.
**Method**: deterministic scan across eight micro-consistency
categories; no autofixes were applied in place (v5 was just
written from scratch and the build agent already incorporated the
detail-level guidance from v4.2 sidecars); items below are
flagged for the next iteration's attention.

## Summary

- Autofixes applied: 0 (v5 is a major build; no in-place edits
  needed beyond the spec author's own editing pass).
- Issues flagged for human decision: 5
- Categories with no issues: format consistency; cross-reference
  consistency; annex vs chapter mismatch; schema-namespace
  pinning; TODO/FIXME/placeholder leftovers.

## Autofixes applied

None. The v5 build was authored against `context/` directly and
applied the per-category rules at write time (the prior detail
reviews against v4.x informed the policy). The detail-review
prompt's autofix surface (format, cross-ref, annex sync, xmlns
declarations) is clean on v5.

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|----------|----------|-------------|-------------|----------------------|----------------|
| 1 | naming reuse with different semantics | §5.1.3 attribute table (`@earliestResolutionTimeOffsetTicks`) | `context/06-naming-and-namespaces.md` "Naming consistency with baseline DASH" (N06.10 / N06.11) | v5 introduces `@earliestResolutionTimeOffsetTicks` on `<svta:OverlayPresentation>` (and references it on `<svta:PauseAdPresentation>` indirectly via §5.1.4 reuse). The rename is correct under N06.11 (unit collision with baseline `@earliestResolutionTimeOffset` which carries seconds on `<ImportedMPD>` per §5.3.2.6.1). The flag is whether the suffix `Ticks` is the right disambiguator (other candidates: `OffsetTimescale`, `TicksOffset`, or full-spell `earliestResolutionTimeOffsetInEventStreamTimescaleUnits`). The current choice is concise and surfaces the unit at the call site, but a future minor refinement MAY prefer a verbose name. | Keep `@earliestResolutionTimeOffsetTicks` for v5; revisit if `06-naming-and-namespaces.md` introduces a normative suffix convention. | Hold. Acceptable for v5; flag for naming policy review. |
| 2 | naming reuse with different semantics | §5.1.4 (`<svta:PauseAdPresentation>` attribute table omits `earliestResolutionTimeOffsetTicks`) | `context/06-naming-and-namespaces.md` N06.10 / N06.11 + ADS resolution pattern | The pause-ad scheme defers ADS resolution to the moment-of-pause (the ERT is the pause itself; see §6.2). Therefore `@earliestResolutionTimeOffsetTicks` is omitted from the attribute table — there is no pre-pause resolution window. However, the spec does not state explicitly that the attribute is **deliberately absent**, only that the table lists three attributes. A reader scanning for symmetric attributes might assume the attribute applies. | Add a one-line note in §5.1.4 stating "Unlike `<svta:OverlayPresentation>`, no `@earliestResolutionTimeOffsetTicks` is declared because the ERT for a pause-trigger slot is the moment of pause (§6.2)." | Add note. Cheap; removes one reader trap. |
| 3 | same-name same-semantics alignment | §5.4.1 `@duration` reconciliation | `context/06-naming-and-namespaces.md` N06.13 (reuse `@duration` because semantics match) | §5.4.1 introduces a reconciliation rule between `<svta:RenderableAsset>@duration` (`xs:duration` seconds) and the sub-MPD's `<Period>@duration` (also `xs:duration` seconds). Both attributes follow the DASH convention and the names match per N06.13. The reconciliation rule is correct, but the spec does not explicitly cite N06.13 to justify the reuse. Reviewers auditing R8 / R9 may want the citation. | Add one sentence in §5.4.1 stating the names reuse the baseline DASH `@duration` per the naming-consistency rule (N06.13 worked example). | Add citation. Improves auditability. |
| 4 | editorial regression | §4.4.8 (pause-ad lifecycle) vs §7.6 (pause-and-overlay composition) | Internal alignment | §4.4.8 and §7.6 cover overlapping content (pause-ad / overlay composition during pause). §4.4.8 is the per-Player obligation; §7.6 is the per-actor behaviour walk-through. The two are consistent but include a couple of redundant phrasings (e.g. "overlay's slot-window clock tracked the primary timeline during the pause" appears in both, slightly rephrased). DP-1 / DP-1.2 prefer a single source of truth. | Move the timeline-anchor detail (slot-window clock anchored to primary timeline) entirely into §7.6, leave §4.4.8 with the obligation statement only and cross-reference §7.6 for the detail. | Refactor in a future minor refinement. Not blocking. |
| 5 | naming reuse with different semantics | §5.5.3 NOTE on `<EventStream>` inside `<svta:RenderableAsset>` | `context/06-naming-and-namespaces.md` N06.10 / N06.11 + `context/08-dash-extension-rules.md` DR-2 / DR-3 | §5.5.3 carries a `<EventStream>` element inside `<svta:RenderableAsset>` with `<Event>@presentationTime` reinterpreted relative to the form-visible instant (not the carrying Period's start, which is the baseline §5.10.2.1 semantics). v5 documents the reinterpretation in an inline NOTE; the carrier-justification (DR-2 / DR-3 strip the entire `<svta:RenderableAsset>` subtree on legacy Players, so no semantic drift occurs) is stated. Per N06.11 (rename when semantics differ), the question is whether the `<EventStream>` element name should be renamed (to e.g. `<svta:Tracking>`). The current path (reuse the baseline name, reinterpret inside foreign-namespace parent) is documented in v4.x as "the §5.2.1 fallback model strips the subtree", but `context/08-dash-extension-rules.md` does not have a normative rule explicitly admitting this pattern. The carry-forward gap A-5 from v4.1 / v4.2 validation tracks it. | Resolve in a future major build by adding a normative rule in `context/08-dash-extension-rules.md` (DR-8 candidate?) admitting "baseline DASH element under SVTA-namespaced parent with reinterpreted timing", or by renaming the element inside SGAI to avoid the reinterpretation. | Hold pending context decision. v5 does not regress vs v4.2 on this. |

## Open questions surfaced

- **`<svta:Candidate>@priority` redundancy with declared order**.
  Tracked as A-2 in `v5-spec-validation.md`. From a detail-review
  lens, the attribute is a clean DP-1.2 candidate for removal,
  but the action is a semantic decision for `context/03-requirements.md`
  R7, not a mechanical detail-review autofix.
- **Form tie-break order `[inferred]` tag in §7.3 step 5 (3)**.
  Tracked as G-2 in `v5-spec-validation.md`. The `[inferred]`
  tag accurately surfaces an unverified claim, but a future
  edition would either remove the tag (when context resolves
  it) or rename the tie-break to a Player-policy local rule.

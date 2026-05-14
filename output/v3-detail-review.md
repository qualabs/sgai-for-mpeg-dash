[GROUNDED_BY=spec-only]

# Spec detail review — 2026-05-14

**Review target**: `../output/2026-05-14-sgai-spec.md`.
**Reference**: `../context/` at git SHA `b62c7d773b4c`.
**Method**: deterministic scan across eight micro-consistency
categories; autofixes applied in place, flags reported here.

## Summary

- Autofixes applied: 1
  - cross-reference consistency: 1
- Issues flagged for human decision: 1
  - naming reuse with different semantics: 1
- Categories with no issues: format consistency (no multi-value
  `@profiles` examples present); same-name same-semantics alignment
  (baseline reuse documented inline at lines 495–500 and 743–760);
  annex vs chapter mismatch (no annex-only construct renames found
  beyond the flagged unit issue); editorial regression (no chapter
  prose / table contradiction found beyond the flagged unit issue);
  schema-namespace pinning (every `svta:`-prefixed element in
  examples carries `xmlns:svta="urn:svta:dash:sgai:2026"` on itself
  or on an ancestor MPD root — lines 581, 638, 769/775, 1703, 1722,
  1892, 1949, 1966); TODO/FIXME/placeholder leftovers (none).

## Autofixes applied

| # | Category | Spec ref | Rule anchor | Before | After |
|---|----------|----------|-------------|--------|-------|
| 1 | cross-reference consistency | `output/2026-05-14-sgai-spec.md:384` | Spec internal — §5.6.2 is "Children of `<svta:Metadata>`" (table of allowed children, no ignore-if-unknown content); §5.6.5 is "Extension rules and legacy compatibility" (the actual ignore-if-unknown rule citing §5.2.1 NOTE 2 of ISO/IEC 23009-1). The §5.6.2 reference under P-11 is a typo for §5.6.5; cross-confirmed by line 1339 ("§5.6.5") and line 1145 ("§5.6.5") which cite the same rule from other call sites. | `MUST safely ignore foreign-namespace elements and attributes it does not implement, treating their absence as the default behaviour (§5.6.2).` | `MUST safely ignore foreign-namespace elements and attributes it does not implement, treating their absence as the default behaviour (§5.6.5).` |

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|----------|----------|-------------|-------------|----------------------|----------------|
| 1 | naming reuse with different semantics / editorial regression | `output/2026-05-14-sgai-spec.md:448, 464, 493, 616` (attribute-table prose) vs `:1636, :1880, :2022` (annex example values) — also referenced by validation sidecar G-1 / A-4 and 2026-05-12 audit M-3 | `context/06-naming-and-namespaces.md:138–145` ("Naming consistency with baseline DASH" — explicitly flags `@earliestResolutionTimeOffset` as the case where SGAI elements in `EventStream@timescale` units MUST NOT reuse the baseline name verbatim because the unit collision is invisible to a reader). | Spec attribute tables declare `@earliestResolutionTimeOffset` as `xs:unsignedInt` "in seconds" on every event element (§5.1.1 `<InsertPresentation>`, §5.1.2 `<ReplacePresentation>`, §5.1.3 `<svta:OverlayPresentation>`, §5.1.4 `<svta:PauseAdTrigger>`). The §5.1.3 NOTE at lines 495–500 reinforces "ERT in seconds" and claims the attribute name is reused verbatim because the semantics match. **But** the annex examples on `<ReplacePresentation>` use `earliestResolutionTimeOffset="60000"` for what surrounding prose treats as a 60-second pre-fetch (`maxDuration="30000"` / `"60000"` / `"90000"` at timescale=1000 = 30/60/90 s respectively). At face value `60000` in seconds is 16+ hours; the value is only sensible as `EventStream@timescale=1000` ticks (ms). Two readings: (a) prose is correct, examples are wrong → autofix the three annex values from `60000` to `60`; (b) examples are correct (ticks), prose is wrong → the SGAI svta attributes collide with baseline `<ImportedMPD>@earliestResolutionTimeOffset` (seconds, §5.3.2.6.1 baseline) and `context/06` §138–145 requires a rename (e.g. `@earliestResolutionTimeOffsetTicks`, or namespace-prefix it as `svta:earliestResolutionTimeOffset` so the unit difference is visible at the call site). | Pick units explicitly. Option (a): patch the three annex values 60000→60 and leave the prose intact. Option (b): change the attribute tables in §5.1.1–§5.1.4 to read "in `EventStream@timescale` units", remove the "ERT in seconds" claim from the §5.1.3 NOTE, and rename the SGAI-side attribute on `<svta:OverlayPresentation>` / `<svta:PauseAdTrigger>` so the unit collision with baseline `<ImportedMPD>` is named explicitly (the baseline `<InsertPresentation>` / `<ReplacePresentation>` attribute is inherited and cannot be renamed; for those a unit-disambiguating NOTE is the only option). | **Flag-only**. Rename / unit-pick is a semantic decision the spec author owns. Option (b) is the stricter reading of `context/06` §138–145 because it makes the unit collision audible at the XML call site; option (a) keeps the inherited baseline name and pushes the discipline onto the spec prose. Either is defensible, but the current state — prose claiming seconds while examples ship 60000 — leaves implementers guessing. |

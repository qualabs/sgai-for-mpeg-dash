[GROUNDED_BY=spec-only]

# Spec detail review — v6 (2026-05-28)

**Review target**: `../output/v6-sgai-spec.md`.
**Reference**: `../context/` at git SHA `d30c655`.
**Method**: deterministic scan across eight micro-consistency
categories; autofixes applied in place, flags reported here.

## Summary

- Autofixes applied: 9
- Issues flagged for human decision: 4
- Categories with no issues: format consistency (category 1), same-name same-semantics alignment (category 4), TODO/FIXME/placeholder leftovers (category 8)

Top categories with autofixes applied: (5) annex vs chapter
mismatch — `<svta:EventStream>` vs baseline `<EventStream>`
realignment across the §5.2.2 skeleton, Annex C.3, and Annex E.3
(6 changes); (7) schema-namespace pinning — `xmlns:svta=`
declarations added to four fragment examples in Annexes I.2,
J.2, and J.3 (4 changes); (2) cross-reference fix — one broken
internal reference repaired in §1.2.

## Autofixes applied

| # | Category | Spec ref | Rule anchor | Before | After |
|---|----------|----------|-------------|--------|-------|
| 1 | (2) cross-reference consistency | §1.2, L:98 | spec internal: §4.6.6 is the single-active-form rendering subsection; §4.4 has no subsection 4.4.7 | `Parallel non-linear ad rendering. At most one non-linear ad form is active on the screen at any given moment (§4.4.7).` | `... at any given moment (§4.6.6).` |
| 2 | (6) editorial regression | §5.2.2.4 children table, L:991 | §5.5 declares the tracking carrier as a baseline DASH `<EventStream>`; the row's own description also says "baseline DASH `<EventStream>`", contradicting the row label | `` `<svta:EventStream>` (callback scheme) `` | `` `<EventStream>` (callback scheme) `` |
| 3 | (5) annex vs chapter mismatch | §5.2.2.1 XML skeleton, L:959 (open tag) | §5.5 + §5.2.2.4 prose both bind the carrier to the baseline `<EventStream>` element name | `<svta:EventStream xmlns:cb="urn:mpeg:dash:event:callback:2015"` | `<EventStream xmlns:cb="urn:mpeg:dash:event:callback:2015"` |
| 4 | (5) annex vs chapter mismatch | §5.2.2.1 XML skeleton, L:966 (close tag) | same anchor as #3 | `</svta:EventStream>` | `</EventStream>` |
| 5 | (5) annex vs chapter mismatch | Annex C.3 XML, L:2207 (open) / L:2216 (close) | same anchor as #3; annex example MUST match chapter declared element name | `<svta:EventStream ...>` ... `</svta:EventStream>` | `<EventStream ...>` ... `</EventStream>` |
| 6 | (5) annex vs chapter mismatch | Annex E.3 XML, L:2403 (open) / L:2408 (close) | same anchor as #3 | `<svta:EventStream ...>` ... `</svta:EventStream>` | `<EventStream ...>` ... `</EventStream>` |
| 7 | (7) schema-namespace pinning | Annex I.2 XML excerpt, L:2636 | `context/06-naming-and-namespaces.md` §"Element / attribute extension namespaces": `urn:svta:dash:sgai:<year>` is the SGAI extension namespace and any example using `svta:` constructs MUST declare it on its root | `<EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"` (root of fragment using `<svta:OverlayPresentation>` child) | `<EventStream xmlns:svta="urn:svta:dash:sgai:2026" schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"` |
| 8 | (7) schema-namespace pinning | Annex J.2 XML excerpt, L:2728 | same anchor as #7 | `<EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"` (root of fragment using `<svta:OverlayPresentation>` child) | `<EventStream xmlns:svta="urn:svta:dash:sgai:2026" schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"` |
| 9 | (7) schema-namespace pinning | Annex J.3 Variants A and B XML excerpts, L:2747 and L:2764 | same anchor as #7; both variants used the `svta:` prefix on the root element itself without declaring the namespace | `<svta:OverlayList>` (twice) | `<svta:OverlayList xmlns:svta="urn:svta:dash:sgai:2026">` (twice) |

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|----------|----------|-------------|-------------|----------------------|----------------|
| 1 | (3) naming reuse with different semantics | §5.1.1 L:759, §5.1.2 L:784, §5.1.3.1 L:807, §5.1.4.1 L:852 vs §5.2.1.3 L:920 and §5.3.4 L:1055 | `context/06-naming-and-namespaces.md` §"Naming consistency with baseline DASH" requires reusing a name with all its characteristics including units | Same attribute name `@earliestResolutionTimeOffset` is declared in two distinct unit conventions: parent `<EventStream>@timescale` units on slot events (`<InsertPresentation>`, `<ReplacePresentation>`, `<svta:OverlayPresentation>`, `<svta:PauseAdPresentation>`) and seconds on `<ImportedMPD>` (both in ListMPD Periods and inside `<svta:RenderableAsset>`). A reader has no syntactic cue to tell the two unit conventions apart | Either (a) rename one of them (e.g. add a `Ticks` suffix on the timescale-units flavour, or a `Seconds` suffix on the seconds flavour); (b) split into two distinct attribute names; or (c) keep one name and document the unit divergence prominently at first introduction in §5.1.1 with a NOTE block visible from every reuse | Rename — unit collision under one identifier is invisible to validators and easy to mis-author. Requires a naming decision out of the deterministic detail-review scope |
| 2 | (6) editorial regression | §5.2.2.4 children table (L:988–996) vs §5.6.3 (L:1257–1267) and §8.8 (L:1890) | spec-internal: §5.2.2.4 is the canonical enumeration of `<svta:Candidate>` children; §5.6.3 introduces `<svta:Advertiser>` as a candidate child and §8.8's audit list also includes it | `<svta:Advertiser>` is declared in §5.6.3 and listed in the §8.8 backward-compat audit but missing from §5.2.2.4's children table (which lists `<svta:RenderableAsset>`, `<svta:EventStream>`, `<svta:Click>`, `<svta:UniversalAdId>`, `<svta:AdSystem>`, `<svta:AdTitle>` only) | Add a row `\| \`<svta:Advertiser>\` \| no \| 0..1 \| The candidate's advertiser identification metadata (§5.6.3). \|` to §5.2.2.4 | Borderline whether the omission was intentional or an editorial slip — the row is mechanical to add but the intent is not unambiguous from `context/`; flag-only |
| 3 | (1) format consistency | Multiple `<AdaptationSet>` examples — main MPD examples use `codecs="avc1.4D401F"` (uppercase hex) at L:1935, L:2050, L:2152, L:2320, L:2376, L:2583; sub-MPD examples use `codecs="avc1.4d401f"` (lowercase hex) at L:1989, L:2237 | RFC 6381 recommends lowercase hexadecimal in codec strings; `context/` does not pin a casing convention | The same AVC codec identifier is rendered in mixed case across examples (main MPDs uppercase, sub-MPDs lowercase) | Normalise to one casing across all examples — RFC 6381 recommends lowercase | Borderline: the inconsistency is cosmetic and codec strings are case-sensitive identifiers but the difference does not affect correctness or example clarity — flag-only |
| 4 | (2) cross-reference consistency | Annex K.1 rows TC-E10 (L:2827) and TC-E11 (L:2828) | spec-internal: §4.6.5 ("skips the candidate and proceeds to the next in document order") is the more precise anchor for "skip the candidate on failure"; §4.6.4 covers ordering preservation when candidates are dropped | Both rows reference §4.6.4 ("Ordering") as the rule anchor; the operative language ("skip the candidate", "advance to the next candidate") is in §4.6.5 ("Presentation-option selection") | Replace `§4.6.4` with `§4.6.5` in the two rows | Borderline — §4.6.4 does mention §4.6.5 implicitly via "Candidates dropped under §4.6.5", so the chain holds; flag-only because the choice is a semantic refinement, not a typo |

## Open questions surfaced

- The skeleton in §5.2.2.1 (L:959) declares `xmlns:cb="urn:mpeg:dash:event:callback:2015"` on the inner `<EventStream>` but never uses the `cb:` prefix in the example. The declaration is harmless but noise — a future minor refinement may want to drop it. Not flagged as an issue because the declaration is syntactically valid and the prompt's category 7 is about pinning declarations of namespaces that ARE used, not pruning unused ones.
- The §3.2 layout table footnote describing `squeezeback-double-box` says the uncovered region "is filled with the Player's default fallback", while §5.3.7 mentions "Player's default uncovered-region behaviour (typically a uniform fill)". The two phrasings are not contradictory but use different vocabulary for the same concept; the validation sidecar's G-2 already tracks the deeper question.

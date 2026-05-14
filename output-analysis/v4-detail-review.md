[GROUNDED_BY=spec-only]

# Spec detail review — v4 (2026-05-14)

**Review target**: `../output/v4-sgai-spec.md`.
**Reference**: `../context/` at git SHA `81e1215`.
**Method**: deterministic scan across eight micro-consistency
categories; autofixes applied in place, flags reported here.

## Summary

- Autofixes applied: 4
  - cross-reference consistency: 3
  - schema-namespace pinning: 1
- Issues flagged for human decision: 5
  - naming reuse with different semantics: 1
  - cross-reference ambiguity: 1
  - placeholder leftover: 1
  - editorial regression: 2
- Categories with no issues: format consistency
  (`allowedLayouts` uses space-separated tokens per
  `context/06-naming-and-namespaces.md` §"Preferred encoding
  patterns" across §5.1.3 attribute description, §4.2 B-3 prose,
  and every annex example — L:655, L:702, L:1797, L:1972, L:2022);
  same-name same-semantics alignment (`@duration`,
  `@maxDuration`, `@priority`, `@url`, `@id` reuse baseline names
  with matching semantics; no shadow-synonyms detected); annex vs
  chapter mismatch (every annex `<svta:OverlayPresentation>` /
  `<svta:PauseAdPresentation>` / `<svta:Candidate>` /
  `<svta:RenderableAsset>` / `<svta:Click>` /
  `<svta:UniversalAdId>` carries the attribute set declared in
  the corresponding §5.x table — checked L:1789-1801, L:1813-1879,
  L:1965-1976, L:2016-2025, L:2037-2057); TODO/FIXME/placeholder
  leftovers (only one bracketed placeholder at L:1230, captured
  in flagged issues; no TODO/FIXME/XXX/TBD markers).

## Autofixes applied

| # | Category | Spec ref | Rule anchor | Before | After |
|---|----------|----------|-------------|--------|-------|
| 1 | cross-reference consistency | `output/v4-sgai-spec.md:268` (chapter 3 §3.2 enumeration footer) | Internal: §4.4.4 is "Ordering and dropping" (candidate-level reordering, not form-skipping). The form-skip-on-unknown-token rule is in §4.4.5 ("Form selection within a candidate") — the parallel cite at L:914 ("MUST skip the form (§4.4.5)") in §5.3.2 mediaType enum uses the same target verbatim. | `MUST treat the form as if its layout were inadmissible and skip it (§4.4.4).` | `MUST treat the form as if its layout were inadmissible and skip it (§4.4.5).` |
| 2 | cross-reference consistency | `output/v4-sgai-spec.md:1017` (§5.5.2 "Where the tracking carrier lives" table) | Internal: §5.5.4 is "Beacon timing" (the *when* of beacons). §5.5.3 "Tracking for non-video forms" is the section that defines the placement "as a child of `<svta:RenderableAsset>`". Row 1 of the same table cites §5.4 for the analogous SPS placement — pattern is "placement → defining section". | `Inside the Overlay Resolution Document, as a child of <svta:RenderableAsset> (§5.5.4)` | `Inside the Overlay Resolution Document, as a child of <svta:RenderableAsset> (§5.5.3)` |
| 3 | cross-reference consistency | `output/v4-sgai-spec.md:1021` (§5.5.2 paragraph following the table) | Same as #2: §5.5.3 defines the form-level carrier; §5.5.4 covers beacon timing only. | `the tracking carrier MUST be attached to the form itself in the Overlay Resolution Document (§5.5.4).` | `the tracking carrier MUST be attached to the form itself in the Overlay Resolution Document (§5.5.3).` |
| 4 | schema-namespace pinning | `output/v4-sgai-spec.md:1033-1043` (§5.5.3 worked example) | Internal: every other `svta:`-prefixed example fragment in the spec carries `xmlns:svta="urn:svta:dash:sgai:2026"` either on itself or on an ancestor `<MPD>` root (L:697, L:743, L:828, L:1792, L:1808, L:1967, L:2018, L:2032). The §5.5.3 example was the only `svta:`-prefixed fragment without an ancestor `<MPD>` and without an inline `xmlns:svta` declaration. | `<svta:RenderableAsset mediaType="image" layout="overlay-corner" duration="PT20S" priority="40" assetUrl=".../banner.png">` | `<svta:RenderableAsset xmlns:svta="urn:svta:dash:sgai:2026" mediaType="image" layout="overlay-corner" duration="PT20S" priority="40" assetUrl=".../banner.png">` |

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|----------|----------|-------------|-------------|----------------------|----------------|
| 1 | naming reuse with different semantics | `output/v4-sgai-spec.md:653` (§5.1.3 `<svta:OverlayPresentation>` attribute table) and L:723-727 (§5.1.4 `<svta:PauseAdPresentation>` attribute table) | `context/06-naming-and-namespaces.md:138-145` ("Naming consistency with baseline DASH" — explicitly names `@earliestResolutionTimeOffset` as the case where SGAI-namespaced elements MUST NOT reuse the baseline name verbatim because the unit collision with `<ImportedMPD>@earliestResolutionTimeOffset` (seconds, §5.3.2.6.1) is invisible to a reader scanning the XML). | v4 keeps `@earliestResolutionTimeOffset` on `<svta:OverlayPresentation>` and `<svta:PauseAdPresentation>` and patches the unit collision with prose ("NOT identical to `@earliestResolutionTimeOffset` on `<ImportedMPD>`…"). This is a deliberate choice but it diverges from the strict reading of `context/06` which mandates a rename. Two readings: (a) accept the divergence — the inline NOTE is enough; or (b) follow context/06 — rename to e.g. `@earliestResolutionTimeOffsetTicks` so the unit is audible at the XML call site. v3 detail review flagged the same conflict; v4 closes the SGAI-side ambiguity with prose but does not satisfy the rename rule. | Rename per context/06, or amend context/06 to admit "rename OR explicit inline NOTE" as the audibility lever. Decision is the spec author's: prose-patch satisfies the *spirit* (collision is documented) but not the *letter* (collision is still invisible to a reader who only scans the XML). | **Flag-only**. Picking between rename and prose-patch is a semantic decision. Recommendation: amend context/06 to explicitly admit the inline-NOTE pattern as a permitted alternative (or rename the SGAI attribute). Leaving the contradiction unresolved keeps the v3 finding open. |
| 2 | cross-reference ambiguity | `output/v4-sgai-spec.md:946` (§5.3.4 sub-MPD MIME constraint) | Internal: the spec's §7.3 is "Player validation and selection"; DASH 6th edition §7.3 is "Single-Period MPD MIME type restrictions" (cited at L:107). The bare `§7.3` at L:946 is in a sentence about RFC 4337 `@mimeType` binding, which is DASH §7.3, not SGAI §7.3. | `the @mimeType on every Representation MUST be video/mp4 / audio/mp4 / application/mp4 per §7.3 / RFC 4337.` | Disambiguate to either "per ISO/IEC 23009-1:2025 §7.3 / RFC 4337" or substitute the more directly-applicable DASH section (§5.3.2.6.1 already governs the `<ImportedMPD>` → SPS chain in this spec — cited at L:101, L:231, L:397). | **Flag-only**. The intended target is unambiguous from context but not from the bare cite; a reader chasing §7.3 lands on the SGAI selection algorithm, which is unrelated. Cheap to fix; flagged rather than autofixed because the right disambiguation form is the author's call. |
| 3 | placeholder leftover | `output/v4-sgai-spec.md:1230` (§6.6 ADS internal: VAST → resolution document, opening paragraph) | Internal: §6.6 is the section itself; the bracketed phrase reads as an unresolved citation. The next sentence asserts implementations MUST be VAST-version-agnostic, and the VAST mapping table that "illustrates the transformation" follows immediately below (L:1238-1248). | `The transformation is illustrated informatively in chapter 6 §6.6 of [the linear baseline adapter mapping carried by the SGAI implementer guide]; conformant implementations MUST be VAST-version-agnostic…` — the bracketed phrase reads as leftover scaffolding from a refactor (the cite points at §6.6 *of an external guide* while we are *in* §6.6 of this spec, and the mapping table is in this same section). | Drop the bracketed phrase: rewrite as "The transformation is illustrated informatively in the table below; conformant implementations MUST be VAST-version-agnostic…" (or replace with a real external citation if one exists). | **Flag-only**. Resolving requires picking between "delete the leftover" and "publish a real citation"; either is defensible. |
| 4 | cross-reference / editorial regression | `output/v4-sgai-spec.md:728` (§5.1.4 `<svta:PauseAdPresentation>` `@triggerMode` attribute description) | Internal: `(see §1.1 OOS)` cross-references the §1.1 "What this specification does not cover" list. §1.1 enumerates seven OOS bullets (SSAI, post-roll, companion / multi-screen beyond CTV end-cards, native ads, parallel-layout system, ADS internal logic, non-admissible creative carriers, parallel non-linear rendering, auth/DRM). None of those bullets covers `device-initiated` triggers / screensaver / inactivity. §5.1.3 layout-token table at L:679 *does* state "Screen-saver-initiated ads are out of scope for this edition" — that is the authoritative anchor for this OOS statement. | The cite should either (a) be amended to point at §5.1.3 ("see §5.1.3 layout-token table, `screen-saver-ad` row") OR (b) §1.1 should be extended to enumerate "device-initiated ad triggers (screensaver / inactivity)" as a discrete OOS bullet matching the §3.2 `screen-saver-ad` token. | **Flag-only**. Choice between repointing the cite vs growing the §1.1 list is editorial. Recommendation: extend §1.1 — keeps the OOS list authoritative and lets §5.1.3 stay as a derived constraint. |
| 5 | editorial regression | `output/v4-sgai-spec.md:2199-2218` (Annex H.1 test case index) cross-referenced with §H.3 (L:2230-2238) and §8.1 E11 (L:1462) | Internal: §H.3 states *"Each error condition has at least one test case that exercises it"*. The 8.1 error table at L:1450-1464 enumerates E1..E13; the TC table covers every row except **E11** ("Ad media-segment or asset fetch fails during playback (HTTP, timeout, decoder, DRM key-exchange on an ad asset)"). No TC in the H.1 table maps to E11. | Add a TC-21 row, e.g.: `TC-21 | §4.4.5 / E11 | E11 | A video form's sub-MPD segment fetch returns 500 mid-playback. | Player aborts current candidate, resumes at next candidate in declared order; re-applies cap arithmetic against rendered-so-far; if no candidates remain, falls through.` | **Flag-only**. Adding a row is mechanical but the wording of the test and its pass criterion need an author's call (especially the cap-arithmetic interaction). The §H.3 invariant fails until the row is added. |

## Open questions surfaced

- The §5.5.3 worked example previously lacked any namespace
  declaration, including for the baseline DASH default
  namespace on the nested `<EventStream>`. Autofix #4 adds the
  `xmlns:svta` declaration only; the baseline DASH namespace on
  the `<EventStream>` element remains implicit on the fragment.
  Other annex examples (e.g. L:1789, L:1965) declare baseline
  DASH on ancestor `<MPD>` roots; the §5.5.3 fragment relies on
  the reader inferring it from context. Worth a one-line
  sentence "this fragment is shown inside the implicit
  `<MPD xmlns="urn:mpeg:dash:schema:mpd:2011">` envelope of an
  Overlay Resolution Document" — not autofixed because adding
  prose around an example is editorial, not deterministic.

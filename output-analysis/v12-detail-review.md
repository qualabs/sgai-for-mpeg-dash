[GROUNDED_BY=spec-only]

# Spec detail review — v12 (2026-09-26)

**Review target**: `../output/v12-sgai-spec.md`.
**Reference**: `../context/` at git SHA `536351fe77f00cff7ef8290de72a89205c0a4a3a`
(HEAD, which is also the last commit touching `context/`;
`git status --porcelain context/` is empty).
**Method**: deterministic scan across eight micro-consistency categories;
autofixes applied in place, flags reported here.

## What this pass could and could not decide

**Grounding is spec-only.** The primary copy of the base standard was not
opened, by instruction. A `DASH §n` citation is checked only for whether it is
written as a base reference, never for whether the base clause says what is
claimed. Categories 3 and 4 are bounded to what the spec and
`context/06-naming-and-namespaces.md` say about each reuse.

**v12 is a major build.** `diff` against v11.1 shows 179 hunks (931 changed
lines). The schema of §5.10.1 changed in two places: `@duration` moved from
`<svta:Ad>` (required) to `<svta:RenderableAsset>` (optional, image and HTML
only), and the global `svta:dismissAfter` for List MPDs was dropped. The whole
document was read, and every scan ran over the whole document; nothing was
carried over from the v11.1 review.

**The validation sidecar routes nothing here.** Its 5.a table has 0 rows. None
of its 5.b items (F-1, F-2, F-4 to F-10) is re-flagged.

## Summary

- **Autofixes applied: 13** (table below). The spec went from 7 313 lines /
  403 609 B (sha256 `2effc315…e1f5`) to 7 313 lines / 403 613 B (sha256
  `a2eb4c4a…af0b`). **The line count did not change and no line moved**, so
  every `L…` anchor in `v12-spec-validation.md` still holds. A `diff` against
  the copy taken before the pass shows exactly the 13 changed lines listed
  below, and nothing else.
- **Issues flagged for human decision: 2.**
- Categories with no issues after the fixes:
  - **cross-reference consistency.**
    - 315 bare `§` refs, 108 `Annex X[.n]` refs and 219 bare `X.n` annex
      sub-section refs resolve against the document's 305 numbered headings.
      The one scanner hit, `I.3.1` at L738, is `DASH Annex I.3.1` wrapped
      across L737-738, a base reference.
    - No `DASH §n` points at a top-level number of this document.
    - Every `§8.13` pointer lands on an item that exists (L1065 → item 12,
      L1787 → item 11, L1981 → item 1, L2301 → item 5, L3550 → item 4).
    - The table of contents matches the 8 chapter and 18 annex headings;
      heading numbers have no gap.
  - **conformance criteria and test identifiers.**
    - `PUB-1..18`, `ADS-1..3`, `APS-1..22`, `PLY-1..88`, `DOC-1..42`: no gap,
      no duplicate, none of the 754 citations undefined, every criterion
      covered in Annex R.
    - 117 test identifiers (`R-PUB-1..10`, `R-ADS-1..2`, `R-APS-1..14`,
      `R-PLY-1..47`, `R-SYN-1..5`, `R-IF-1..2`, `R-BEH-1..17`, `R-E-1..15`,
      `R-BC-1..5`): no gap, no duplicate, none cited undefined. R.1 lists
      every prefix in use.
    - `DR-1..10`, `E1..E15` and `C1..C5` all defined.
  - **schema-namespace pinning.** All 82 non-schema XML blocks parse, which
    means every prefix they use is declared.
  - **annex vs chapter mismatch.** 0 violations of the chapter-5 rules across
    all examples. The rules checked were:
    - `svta` element and attribute names against §5.10.1;
    - `@allowedLayouts` tokens within those the window's family may list
      (§3.4.3), space-separated;
    - `@customRegion` only with `custom`; pause windows `@linearRelation`
      only `on-top`; `@durationCap` on every window;
    - `@duration` iff image or HTML, `@rect` iff `custom`, `@background` iff
      `squeezeback-double-box-background`, `@mimeType` among the three forms
      (inside `<svta:OverlayList>` and on standalone fragments);
    - `@onExhausted` iff `family="pause"`; `@dismissAfter` on every
      `<svta:OverlayList>`; pause layouts only on pause documents;
    - `<svta:Ad>` child order; callback scheme with `@value="1"`;
    - no `@value` on SGAI streams; one stream per scheme per Period;
      non-decreasing presentation times; unique `Event@id`.
    - Profiles: 20 main MPDs `isoff-live:2011` only, 24 sub-MPDs
      `sps:2024,isoff-live:2011`, 8 `list:2024`, as §4.8.5 states.
  - **editorial regression (forwarded declarations).** Every request line
    that forwards `sgai-allowed-layouts` or `sgai-custom-region` matches its
    window (C.3, D.3, E.3, H.3, I.3, J.3, M.3, N.3, O.3, P.3, Q.5, and the
    §5.8.4 line against §5.1.7). Its query is flag 2.
  - **naming reuse / same-name alignment.** No flag. The two schema changes
    introduced no name. Each base name reused on an SGAI construct keeps the
    base's units and default or is excluded with a recorded reason:
    `@earliestResolutionTimeOffset` (units of `EventStream@timescale`, 60 s,
    per `context/06`), `@executeOnce` (the counter rule), `@duration` on an
    option (`xs:duration`, as `Period@duration`, image and HTML only per
    `context/06` "A value the base already carries is not restated"),
    `@durationCap` / `@dismissAfter` / `@validFor` (new names because the
    base default cannot be inherited, §4.8.2), and `@linearRelation` (no base
    construct, the three carriers of `context/06` weighed in §4.8.2). No
    prose site still refers to the dropped `svta:dismissAfter` or to a
    duration on `<svta:Ad>`.
  - **TODO / FIXME / placeholder leftovers.** No marker. The remaining hits
    are the definition of `[inferred]` (L23), prose about a placeholder
    *value* (L926, L2663, L7162), and explanatory XML comments.

## Autofixes applied

Spec refs are line numbers, unchanged by the pass.

| # | Category | Spec ref | Rule anchor | Before | After |
|---|---|---|---|---|---|
| 1 | format consistency (*Required* column) | §5.1.3, `EventStream@timescale`, L2070 | spec §5.0: *Required* is **OD** for "optional with a default". The same table writes `Event@presentationTime`, whose default is also a base literal, as OD (L2071) | `\| O \| … \| \`1\` (base) \|` | `\| OD \|` |
| 2 | as 1 | §5.1.3, `@allowedLayouts`, L2085 | as 1; the sibling `@earliestResolutionTimeOffset` (L2084), whose default is also descriptive, is OD | `\| O \| … \| the family default (§3.4.3) \|` | `\| OD \|` |
| 3 | as 1 | §5.1.3, `@customRegion`, L2086 | as 2 | `\| O \| … \| the whole viewport \|` | `\| OD \|` |
| 4 | as 1 | §5.1.3, `@linearRelation`, L2087 | as 2 | `\| O \| … \| the default relation \|` | `\| OD \|` |
| 5 | as 1 | §5.1.4, `@allowedLayouts`, L2115 | as 2 | `\| O \| … \| the family default (§3.4.3) \|` | `\| OD \|` |
| 6 | as 1 | §5.1.4, `@linearRelation`, L2117 | as 2 | `\| O \| … \| the default relation \|` | `\| OD \|` |
| 7 | as 1 | §5.2.2, `@dismissAfter`, L2209 | as 1; the default is the literal `never` | `\| O \| … \| \`never\` \|` | `\| OD \|` |
| 8 | as 1 | §5.2.2, `@validFor`, L2210 | as 2 | `\| O \| … \| the remainder of the window's span \|` | `\| OD \|` |
| 9 | as 1 | §5.5.2, `@timescale`, L2527 | as 1; the same table writes `@presentationTimeOffset`, default `0`, as OD (L2528) | `\| O \| … \| \`1\` \|` | `\| OD \|` |
| 10 | format consistency (table cell spacing) | Annex R.3, R-SYN-5, L7227 | every other cell of every table in the document opens with a space | `\| R-SYN-5 \|\`PercentRectType\`` | `\| R-SYN-5 \| \`PercentRectType\`` |
| 11 | format consistency (annex sub-section refs) | Annex L.4, L6056 | the document refers to its annex sub-sections as `Annex X.n` or bare `X.n` (for example "as D.7 gives it", "As H.7 and H.8"). These three were the only `§X.n` forms. The target is unchanged | `APS B's document (§L.5)` | `APS B's document (L.5)` |
| 12 | as 11 | Annex L.8, L6147 | as 11 | `(§L.6).` | `(L.6).` |
| 13 | as 11 | Annex N.3, L6486 | as 11 | `slate MPD (§N.4)` | `slate MPD (N.4)` |

**Why fixes 1-9 are fixes and not flags.** After the pass, every attribute row
whose *Default* cell is filled reads OD or CM, and every row whose *Default*
cell is `—` reads M, O, CM or `—`. Before the pass, nine optional rows with a
stated default read O. Two of them sat in tables that already wrote a sibling
with the same kind of default as OD. The rule is §5.0's own definition, and
the change touches the notation only, not what the attribute means. The check
`awk -F'|' '$3==" O " && $5!=" — "'` over the attribute rows returns 9 before
the pass and 0 after.

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|---|---|---|---|---|---|
| 1 | editorial regression (type names: prose and tables vs schema) | §5.0 L2003-2015; Type cells L2087, L2117 (`enum, §5.1.6`), L2208 (`enum`), L2211 (`enum, §5.2.6`), L2573 (`list of xs:anyURI, space-separated`); schema L2764-2820 | spec §5.0 L2003-2004: "Four types are defined here, under the names the schema of §5.10.1 declares" | §5.10.1 declares eleven simple types, not four. Seven are missing from §5.0: `PercentType` and `NeverType`, which are helper types, and `LinearRelationType`, `OnTopOnlyType`, `FamilyType`, `OnExhaustedType` and `URIListType`, which are the types of five attributes. The tables do not name those five types. A reader matching a *Type* cell against the schema finds no name. The cells do follow §5.0's enumeration convention ("names the section that defines it"), so they are not wrong on their own. The problem is §5.0's count and the claim that it covers the schema's names. The v11.1 review raised this as an open question, and it is still present. | (a) Put the five schema names in the Type cells, for example `` `LinearRelationType` (§5.1.6) ``, and change §5.0 to "Nine types … two helper types"; or (b) keep the cells and qualify §5.0: "Four list and union types are defined here; each enumeration is declared in §5.10.1 under the name its table gives". | (a). The schema is what a validator loads, and the other three list or union types already use the schema name in their cells. Flagged, not fixed, because it chooses which text changes and rewrites a §5.0 sentence. |
| 2 | editorial regression (example vs example) | §5.8.4 request, L2671-2672, against §5.1.7 window, L2161-2163 | spec §5.8.1 L2612-2613: "The Player keeps that query unchanged and appends its own parameters to it" | The request line `GET /nl/overlay/1?slot=mid1&sgai-video-decoders=1&…&sgai-allowed-layouts=overlay-lower-third%20squeezeback-l-shape-upper-left` forwards exactly the allowed layouts of §5.1.7's window, whose `@uri` is `https://aps.example.com/nl/overlay/1` with no query. The Publisher query `slot=mid1` is on no window in the document, so the Player in the example has invented a parameter. In v11.1 this request belonged to a §5.8.1 example window with `uri="…/nl/overlay/1?slot=mid1"`. v12 dropped that example, and the request was left pointing at §5.1.7's window. | (a) Add `?slot=mid1` to the `@uri` of §5.1.7; or (b) drop `slot=mid1&` from the §5.8.4 request line. | (a). §5.8.5 ("Two sources on one URL") relies on this line to show a Publisher query next to the reserved parameters, and (b) would remove the only instance of that in chapter 5. Flagged, not fixed, because either fix changes an example that the other one leaves standing. |

## Open questions surfaced

- **The validation sidecar's 5.b count does not match its rows.** The
  heading reads "Flagged for review (10)" and the table holds nine rows
  (F-1, F-2, F-4 to F-10); there is no F-3. This pass does not modify the
  sidecar. Whoever routes its items should not look for a tenth.
- **Some prose lines run to 81-96 characters** (for example L254, L1393,
  L1915, L2036, L3560). Most sit where a `DASH ` prefix lengthens a citation.
  The rendered output is unaffected, and they were not rewrapped, because a
  rewrap would move line numbers that the sidecar and any running audit cite.

## Instrument controls

Each scan was run on the fixed spec and on a copy with one defect of its own
class injected. A scan that reads the same on both cannot fail.

| Scan | Injected defect | Fixed spec | Injected |
|---|---|---|---|
| C1 unresolved bare `§` refs | `(§4.5.4)` → `(§4.5.44)` | 0 | **1** |
| C1 `Annex X[.n]` refs | `Annex L.7.` → `Annex L.17.` | 0 | **1** |
| C1 bare `X.n` refs | `As H.7` → `As H.17` | 1 (L738, base; see Summary) | **2** |
| C1 `DASH §n` on a top-level number | `(DASH §4.2)` → `(DASH §7)` | 0 | **1** |
| C2 undefined criterion cited | `(PLY-43)` → `(PLY-143)` | 0 | **1** |
| C2 test-id gap | `R-PLY-47` → `R-PLY-49` | no gap | **gap 47, 48** |
| C6 heading sequence | `### 7.19` → `### 7.21` | 0 | **2** |
| C7 parse / undeclared prefix | `xmlns:svta` removed from §5.1.7 | 0 | **1** |
| C5 layout tokens | `overlay-lower-third overlay-corner` → comma-separated (N.4) | 0 | **1** |
| C5 `@onExhausted` on pause documents | removed from H.5 | 0 | **1** |
| C5 `@rect` iff `custom` | `rect` removed from the §5.3.5 fragment | 0 | **1** |
| C5 `<svta:Ad>` child order | a `<svta:ClickThrough>` placed before the options (K.4) | 0 | **1** |
| C1 table cell spacing (`\|` + backtick) | fix 10 reverted | 0 | **1** |
| C1 *Required* O with a default | fix 9 reverted | 0 | **1** |
| C1 `§X.n` annex refs | fix 11 reverted | 0 | **1** |
| C8 drafting markers | `TODO` inserted in §8.13 | 0 | **1** |

Two scans were corrected before these results were accepted. The first `X.n`
scan excluded base-table prefixes by prefix match, so `H.17` passed as
`H.1`. The first `@rect` rule checked only options inside
`<svta:OverlayList>`, so the §5.3.5 fragment was not covered. Both were
rewritten, and the counts above are from the corrected versions.

## What was not touched

- Nothing under `../context/` or `../dist/`: `git status --porcelain context/
  dist/` is empty.
- Nothing under `../context-analysis/`. Its five modified files were already
  modified before this pass.
- `../output-analysis/v12-spec-validation.md`, Step 7's artefact.

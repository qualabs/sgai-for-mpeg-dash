[GROUNDED_BY=spec-only]

# Spec detail review — v11 (2026-09-26)

**Review target**: `../output/v11-sgai-spec.md`.
**Reference**: `../context/` at git SHA `a732edf9d94a0ad2509cf440a832bce6cd8a47df`
(`git status --porcelain context/` is empty).
**Method**: deterministic scan across eight micro-consistency categories;
autofixes applied in place, flags reported here.

## What this pass could and could not decide

**Grounding is spec-only.** The primary copy of the base standard was not
opened, by instruction. Categories 3 and 4 are therefore bounded to what the
spec and `context/06-naming-and-namespaces.md` say about each reuse, and a
`DASH §n` citation is checked only for whether it points at this document by
mistake, never for whether the base clause says what is claimed.

**v11 is a major build.** Its schema (§5.10.1) differs from v10.1 in 17
declared names (for example `assetUrl` → `src`, `form` dropped, `Candidate` →
`Ad`, new `durationCap`, `linearRelation`, `validFor`, `onExhausted`), so every
scan ran over the whole document and no v10.1 result was carried over. Every
negative result below comes from an instrument that was first made to fail
(§"Instrument controls").

**The three items the validation sidecar routed here (5.a T1–T3) are applied
as autofixes 1–5.** Its 5.b items f-2 (§1.3 L156, "DASH §4.8.9") and f-3
(§3.4.2 L497, "bottom 30%") are not re-flagged: each needs either the base
text or an IAB source, which this pass does not consult.

## Summary

- **Autofixes applied: 11** (table below). The spec went from 7 126 lines /
  388 337 B (sha256 `d14298e4…6cb7`) to 7 127 lines / 388 442 B (sha256
  `7cd2db0d…0325`). A `diff` against the copy taken before the pass shows 11
  changed hunks, and nothing else.
- **Issues flagged for human decision: 1.**
- Categories with no issues after the fixes:
  - **cross-reference consistency.**
    - 286 bare `§` refs, 102 `Annex X[.n]` refs and 68 bare `X.n` annex
      sub-section refs all resolve against the document's 305 headings. The
      one `Annex X` hit (L19) is the reading convention itself.
    - No `DASH §n` is left pointing at a top-level number of this document.
    - 172 conformance criteria (`PUB-1..17`, `ADS-1..3`, `APS-1..22`,
      `PLY-1..88`, `DOC-1..42`): no gap and no duplicate. None of the 653
      citations is undefined, and every criterion is covered in Annex R.
    - 102 test identifiers, none duplicated or cited undefined; E1–E15 and
      DR-1..10 all defined.
    - Heading numbering has no gaps, and the table of contents matches the
      chapter and annex headings.
  - **schema-namespace pinning.** All 84 XML blocks parse, and every prefix
    they use is declared on the block's root.
  - **annex vs chapter mismatch.** 0 violations of the chapter-5 rules across
    all examples. The rules checked were:
    - element and attribute names against §5.10.1;
    - every `@allowedLayouts` token in §3.4.2;
    - `@rect` iff `custom`, `@background` iff
      `squeezeback-double-box-background`, `@customRegion` only with `custom`;
    - `@onExhausted` iff `family="pause"`;
    - `@linearRelation` on pause windows only `on-top`;
    - `<svta:Ad>` child order;
    - `<svta:Tracking>` scheme and `@value="1"`;
    - no `@value` on SGAI streams;
    - non-decreasing presentation times and unique `Event@id`;
    - `svta:dismissAfter` only on List MPDs.
    - The option layouts outside their window's set appear only where the
      annex itself says they are an APS error (L.5 option 3, O.7).
  - **editorial regression (forwarded declarations).** After autofix 7, all
    11 request lines match the declarations of their window. The only line
    with no window is the linear request of D.3, which correctly carries none
    (DOC-16).
  - **TODO / FIXME / placeholder leftovers.** No marker. The three
    `placeholder` hits (L878, L2559, L6979) are prose about a placeholder
    *value*.
  - **naming reuse with different semantics / same-name alignment.** No new
    flag. Each base name the spec reuses on its own constructs is used with
    the base's units and default, or is excluded with a recorded reason:
    - `@earliestResolutionTimeOffset`: base units and 60 s default, per
      `context/06`;
    - `@executeOnce`: counter rule of Tables 58/63;
    - `@uri`, `@timescale`, `@presentationTimeOffset`: base meaning;
    - `@duration` on `<svta:Ad>`: `xs:duration`, as `Period@duration`;
    - `@durationCap`, `@dismissAfter`, `@validFor`: new names because the base
      default cannot be inherited (§4.8.2, `context/06`).
  - **format consistency (other).**
    - Every token list is space-separated: `@allowedLayouts`,
      `@trackingUris`, `@customRegion`, `@rect`.
    - `@profiles` is comma-separated.
    - List values in queries are `%20`-encoded.
    - The codec strings are uniform (`avc1.64001F` ×39, `avc1.640028` ×5,
      `mp4a.40.2` ×34).

## Autofixes applied

Spec refs are post-fix line numbers. Rows 8 onward sit one line lower than
before the pass, because of fix 7.

| # | Category | Spec ref | Rule anchor | Before | After |
|---|---|---|---|---|---|
| 1 | editorial regression (sidecar T1) | §4.7.3 item 1, L1608 | `context/06` §Scheme URI patterns (`urn:svta:dash:<construct>:<year>`, the two URIs named); spec §2.1 L286, §5.1 L1908, §5.1.3 L1945, and item 6 of the same entry | `@schemeIdUri="urn:mpeg:dash:sgai-overlay:2026"` | `@schemeIdUri="urn:svta:dash:sgai-overlay:2026"` |
| 2 | editorial regression (sidecar T1) | §4.7.4 item 1, L1636 | as 1; spec §2.1 L287, §5.1.4 L1976 | `@schemeIdUri="urn:mpeg:dash:sgai-pause-trigger:2026"` | `@schemeIdUri="urn:svta:dash:sgai-pause-trigger:2026"` |
| 3 | annex vs chapter mismatch (sidecar T2) | Annex R.2.1, R-PUB-5, L6936 | spec §5.1.6 L2017 ("On a pause window, `@linearRelation` takes only the value `on-top`"); schema `OnTopOnlyType`; Annex D.2 declares `on-top` on an overlay window | `at most one @linearRelation per window, on-top only on pause windows` | `at most one @linearRelation per window; on a pause window only on-top` |
| 4 | cross-reference (sidecar T3) | §2.1 table, "Defined in", L285 | spec reading rule L18-20 (a bare `§n` is this document); the namespace is defined in this document's §5.0 and §5.10 | `DASH §5` | `§5` |
| 5 | cross-reference (sidecar T3) | Annex R.2.5, "Where", L7027 | as 4; chapter 2 of this document carries the VAST informative reference (L276-279), and DOC-9 names §6.6, A.7, C.8 of this document | `DASH §2, §6.6, Annexes A.7, C.8` | `§2, §6.6, Annexes A.7, C.8` |
| 6 | editorial regression | Annex R.1, L6923 | the identifiers R.2.2 uses (`R-ADS-1`, `R-ADS-2`); the list names every other prefix in use | `` `R-PUB-n`, `R-APS-n`, `` | `` `R-PUB-n`, `R-ADS-n`, `R-APS-n`, `` |
| 7 | editorial regression (example vs example) | §5.8.1 example, L2501-2503 | PLY-15 (nothing is forwarded for a window that declares no `@allowedLayouts`); §5.8.4 L2567-2568 forwards `overlay-lower-third%20squeezeback-l-shape-upper-left` on a request to this same window (`/nl/overlay/1?slot=mid1&sid=…`); §5.1.7 declares that set on the same window (id 1, 120000/30000, cap 30000) | `durationCap="30000"/>` | `durationCap="30000"` + `allowedLayouts="overlay-lower-third squeezeback-l-shape-upper-left"/>` |
| 8 | format consistency (clause-step citation) | §4.7.8 table, L1727 | the form used at the other eight sites: `(DASH §5.3.2.6.3, step 3 b ix)` L1659, `step 3 d iii` L1348 and L2055, `step 3 c iv` L2379 | `DASH §5.3.2.6.3 3 b ix` | `DASH §5.3.2.6.3, step 3 b ix` |
| 9 | format consistency (clause-step citation) | §4.8.1 table, L1749 | as 8 | `DASH §5.3.2.6.3 3 d iii` | `DASH §5.3.2.6.3, step 3 d iii` |
| 10 | format consistency (clause-step citation) | §4.8.2 table, `@validFor` row, L1777 | as 8 | `(DASH §5.3.2.6.3 1 c)` | `(DASH §5.3.2.6.3, step 1 c)` |
| 11 | format consistency (citation prefix) | §8.2 E9, L3362 | every other RFC citation in the document carries `IETF RFC` | `an RFC 4337-bound` | `an IETF RFC 4337-bound` |

Why fix 7 is in this table and not among the flags: there are two ways to make
the examples agree. One is to drop `sgai-allowed-layouts` from the §5.8.4
request line. That would remove the one list value whose `%20` encoding the
example exists to show (L2556-2557). Adding the attribute to the window
instead changes only an informative example, and it makes that window
identical to §5.1.7's.

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|---|---|---|---|---|---|
| 1 | editorial regression (prose type names vs schema type names) | §5.0 L1887, L1890; tables L1962, L1963, L1990, L2234; R-SYN-5 L7044. Against the schema: L2656, L2667, L2727, L2728, L2741, L2779 | §5.0 L1885 ("Types are those of W3C XML Schema Part 2 unless defined here"), with the schema of §5.10.1 as the definition | The prose and the attribute tables name two types `LayoutTokenList` and `PercentRect`, while the schema declares them as `LayoutTokenListType` and `PercentRectType`. The third type follows neither pattern: it is `DismissAfterType` in both places. The same holds for `@layout`, whose table type is the phrase "layout token" and whose schema type is `LayoutTokenType`. A reader matching a table's *Type* column against §5.10.1 finds no `LayoutTokenList`. The same list in §5.0 also opens with "Two list types are defined here" and then gives `DismissAfterType`, which is not a list type, as an outer-level bullet. | Either rename the 7 prose sites to the schema names (`LayoutTokenListType`, `PercentRectType`, and `LayoutTokenType` for `@layout`), or rename the 6 schema sites to the prose names. | Rename the prose to the schema names. The schema is the artefact a validator loads, and `DismissAfterType` already follows that pattern in both places. Flagged, not fixed: the fix picks which name wins, which is a naming decision. |

## Open questions surfaced

- **The status line carries the build number.** L3 reads "candidate
  specification, build iteration 11". `CLAUDE.md` says the published title
  carries no version and history lives in git and `output/`. In a candidate
  the line is correct. At promotion into `dist/` it has to change, and nothing
  in the pipeline does that.
- **One wrapped line grew past 80 characters.** Fix 6 made L6923 82
  characters long. It does not affect the rendered output. It was not rewrapped,
  so that the fix stays one line.

## Instrument controls

Each scan was run on the spec as found and on a copy with one defect of its
own class injected. A scan that reads the same on both cannot fail. None did.

| Scan | Injected defect | As found | Injected |
|---|---|---|---|
| C1 unresolved bare `§` refs (a `DASH ` prefix, also at the end of the previous line, marks a base ref) | `(§4.5.4)` → `(§4.5.44)` | 0 | **4** |
| C1 bare `X.n` annex sub-section refs | `As H.7` → `As H.17` | 0 | **1** |
| C1 `Annex X[.n]` refs | `Annex L.7.` → `Annex L.17.` | 1 (L19, the convention) | **2** |
| C1 `DASH §n` on a top-level number | `(DASH §7)` added | 2 before the fixes (L285, L7026), 0 after | **3** |
| C2 undefined criterion cited | `(PLY-43)` → `(PLY-143)` | 0 | **1** |
| C2 undefined test id | `R-BC-9` added to R.7 | 0 (R-E-n ids are defined in R.6's third column, see note) | **1** (at 2 sites) |
| C3 XML parse / undeclared prefix | `xmlns:svta` dropped from §5.1.7 | 0 | **1 parse failure + 1** |
| C3 chapter-5 rules | comma in `@allowedLayouts` | 0 | **2** |
| C3 | `image/png` → `application/pdf` | 0 | **1** |
| C3 | `@onExhausted` removed from a pause document | 0 | **1** |
| C3 | `rect` added to a `linear` option | 0 | **1** |
| C3 | Tracking `@value="1"` → `"2"` | 0 | **1** |
| C3 | `linearRelation="supersede"` on a pause window | 0 | **1** |
| C3 | `urn:svta:` → `urn:mpeg:` on an overlay stream | 0 | **1** |
| C3 | `<svta:ClickThrough>` moved before the options | 0 | **1** |
| C3 | `@value` on a pause-trigger stream | 0 | **1** |
| C4 forwarded declarations vs window | (none needed: it found the §5.8.1/§5.8.4 pair, which is its positive control) | 1 + linear D.3 | — |
| C5 drafting markers | a `TODO: settle this.` line | 0 | **1** |
| C6 heading sequence | `### 7.19` → `### 7.21` | 0 | **2** |

C2 initially reported the 15 `R-E-n` ids as undefined, because it looked for
test ids only in the first column. R.6 defines them in its third column, so
that is not a finding. The count under "As found" leaves them out.

## What was not touched

- Nothing under `../context/`: `git status --porcelain context/` is empty.
- Nothing under `../context-analysis/`. The five modified files there
  (`conformance-assertions.md`, `dash-gap-analysis.md`, `error-semantics.md`,
  `iab-ad-templates.md`, `uc-coverage-matrix.md`) were already modified
  before this pass started.
- `../output-analysis/v11-spec-validation.md`, Step 7's artefact.
- Nothing under `../dist/`.

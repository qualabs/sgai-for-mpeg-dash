[GROUNDED_BY=spec-only]

# Spec detail review — v10 (2026-09-25)

**Review target**: `../output/v10-sgai-spec.md`.
**Reference**: `../context/` at git SHA `22ae6f831541ffddbef7c6e96556764eeadf92ae`
(`git status --porcelain context/` is empty).
**Method**: deterministic scan across eight micro-consistency categories;
autofixes applied in place, flags reported here.

## What this pass could and could not decide

**Grounding is spec-only.** The primary copy of the base standard was not
opened, by instruction. Categories 3 and 4 are therefore bounded to what the
spec itself says about its reuses. v10 introduces 11 elements, 5 URIs and the
reserved `sgai*` parameters; the `svta:` element inventory of every example is
exactly the 11 that chapter 5 tables and §5.10 declares, and every attribute on
an `svta:` element in an example is one chapter 5 declares for that element.

**Every negative result below was taken with an instrument that was made to
fail first** (§"Instrument controls"). **Line numbers are post-fix.**

## Summary

- **Autofixes applied: 36 sites, in 5 issue classes.**
- **Issues flagged for human decision: 2.**
- Spec size: 8 759 lines / 457 337 B → **8 761 lines / 457 767 B** (+2 lines,
  +430 B). Every changed line belongs to one of the five classes below; no
  prose was rewritten except the one table cell of row 4.
- Categories with no issues:
  - **TODO / FIXME / placeholder leftovers** — none. The four `placeholder`
    hits (L1343, L1419, L2868, L2911) are prose about a placeholder *value*
    the base URL-parameter scheme sends; none is a drafting marker.
  - **naming reuse with different semantics** — nothing new to flag; see
    §"Open questions surfaced" for the one reuse Step 7 already owns.
  - **same-name same-semantics alignment** — no synonym of a baseline name
    found. Every non-reuse (`@dismissAfter` vs `@skipAfter`, `@assetUrl` vs
    `<ImportedMPD>`, `@customRegion` vs SRD) is argued in §4.8.
  - **annex vs chapter mismatch, on names and values** — every `@layout` is a
    §3.4.2 token admissible for its document's family, every `@form` is one of
    §5.3.2, every `@allowedLayouts` is space-separated with family-admissible
    tokens, `@backgroundUrl` sits exactly on `squeezeback-double-box-background`
    options, `@customRectangle` exactly on `custom` options, every non-linear
    option carries `@duration`, `@onCandidatesExhausted` appears on every pause
    document and on no overlay document, no SGAI-scheme `<EventStream>` carries
    `@value`, every callback stream carries `@value="1"`, every opportunity
    carries `@maxDuration`, and every `<svta:Candidate>` orders its children as
    §5.2.2 tables them.
  - **format consistency (other)** — codec strings all lowercase hex
    (`avc1.4d401f`, `avc1.64001f`, `avc1.640028`, `mp4a.40.2`); speed notation
    `×` throughout; every annex carries the same `*This annex is informative.*`
    line; `---` is used uniformly before every chapter and annex; every
    annex MPD opens with the XML prolog and every chapter-5 example omits it
    (each group internally consistent, as in v9).

## Autofixes applied

| # | Category | Spec ref | Rule anchor | Before | After |
|---|---|---|---|---|---|
| 1 | schema-namespace pinning | 8 fragment roots in 7 blocks: L2411, L2416 (§5.3.5), L2724 (§5.6.1), L2810 (§5.8.1), L7655, L7670, L7682 (M.5), L8522 (P.7) | The prompt's category 7; the spec's own fragments at L1665, L1745, L6042 declare the prefix on the fragment root | `<svta:OverlayList family="overlay">` (prefix used, never declared: `unbound prefix` on parse) | `<svta:OverlayList xmlns:svta="urn:svta:dash:sgai:2026" family="overlay">` |
| 2 | editorial regression | G.2 L5853, G.3 L5914 | §5.9, L2976: *"The base schema requires at least one `<Reporting>` child."*; the other four `<Metrics>` examples (L2972, L5153, L5443, L6147) carry it | `<Metrics metrics="PlayList">` / `<Range starttime="PT0S"/>` / `</Metrics>` | same, plus `<Reporting schemeIdUri="urn:example:publisher:reporting:2026"/>` — the scheme every other example uses |
| 3 | cross-reference consistency | §4.7.6, L1292 | Q.7, L8745: `Q.7.2` is *"Pause scheme and `<svta:PauseAdPresentation>`"* | Row for both event schemes, legacy-test cell `Q.7.1` (the overlay test only) | `Q.7.1, Q.7.2` |
| 4 | editorial regression | Q.5 row B-10, L8700 | J.7, L6875-6877 and the J.7 table: D3 renders option 3 (`html`), D4 option 4 (`image`); §5.3.7 row `squeezeback-double-box-background`/`html` is satisfiable on D1, D3 | `D3, D4 render the image form` | `D3 renders the HTML form, D4 the image form` |
| 5 | format consistency (delimiter) | 24 sites: L4532, L4614, L4628, L4655, L4661 (×2), L4669, L4882, L5037, L5051, L5070, L5724, L5748, L5750, L5986, L6034, L6055, L6062, L6815, L6883, L6908, L7876, L7892, L8027 | Majority form of the document: 89 references write `§X item N` / `§X step N` without a comma (e.g. L5164, L8582-8658 in Annex Q) | `(§4.5.6, item 4)`, `(§4.6, step 4)`, `(§4.7, step 2)` | `(§4.5.6 item 4)`, `(§4.6 step 4)`, `(§4.7 step 2)` |

Scope held deliberately: row 1 adds the declaration only. The §5.3.5 block
(L2410-2419) still does not parse, because it shows two sibling elements
separated by a literal `...`; that is an elision, not a defect of this class.

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|---|---|---|---|---|---|
| 1 | editorial regression (annex vs annex) | M.5, L7597-7646, against I.3, L6492-6543 | M.5 L7597: *"The D4 document, which carries all four options, is the document of Annex I"*; M.1 L7481 | The two documents differ. I.3 carries five beacons (`0`, `3750`, `7500`, `11250`, `15000`, L6525-6529) plus `<svta:AdSystem>` and `<svta:AdTitle>` (L6536-6537); M.5 carries three (`0`, `7500`, `15000`) and no metadata. The four fragment documents of M.5 say their stream and click are *"as in the D4 document"*, so the choice propagates to them. | Either make M.5 byte-identical to I.3 and extend the M.5 elision comment to cover the metadata, or change L7597 to say the options, not the document, are those of Annex I. | Align M.5 to I.3. The prose claim is the more useful one (Annex M exists to compare outcomes against Annex I), and aligning costs one block. Not autofixed because the edit cascades into the elision sentence at L7648-7650 and the four fragments. |
| 2 | editorial regression | §3.6, L574, overlay row, D2 cell | §5.3.7 L2491 and L2494: `squeezeback-double-box`/`video` is satisfiable on D1, D2; `squeezeback-double-box-background`/`video` on D1 only. J.6 bolds exactly this cell pair. | The cell reads *"Video overlay; a double box or L-shape with a video creative; otherwise skip"*. "A double box" covers both double-box tokens under §3.1's definition, so the summary grants D2 the background variant the budget table denies. | Write `squeezeback-double-box` (without background) or name the exclusion. | Rewrite the cell. It is the one summary cell that contradicts the rule it summarises, on the very case §3.6 calls instructive (L583). Flagged rather than fixed because choosing the wording of a normative-chapter summary is not a delimiter, reference, name or namespace edit. |

## Open questions surfaced

- **`@maxDuration` keeps its baseline name with a family-dependent meaning** —
  *until when* on a replacement, cumulative length on insertion and overlay,
  nothing on pause (§4.5.4 table, L859-864), and no default where the base
  default is infinity (§4.8.3). That is category 3's shape, and it is named
  only so that category 3 is not read as empty. It is not flagged here: the
  default departure is Step 7's A-4 in `v10-spec-validation.md`, where the fix
  is in `context/03-requirements.md`, which this pass may not touch.
- **§5.10 schema: `Click` is the only complex type without
  `<xs:anyAttribute namespace="##other" processContents="lax"/>`** (L3131-3139;
  every other complex type carries it). Nothing in chapter 5 says whether
  `<svta:Click>` is meant to be closed to foreign attributes, so this is not
  classifiable as a regression; it is worth one line of intent.

## Instrument controls

Each scan was run on the original v10, on the fixed v10, and on a copy of the
fixed v10 with one defect of the scan's own class injected. A scan whose
fixed and injected counts agree would be a scan that cannot fail; none does.

| Scan | Injected defect | Original | Fixed | Injected |
|---|---|---|---|---|
| C1 unresolved internal `§` refs | `(§4.5.4)` at L1841 rewritten `(§4.5.44)` | 1 | 1 | **2** |
| C2 XML block with an undeclared prefix or parse failure | `xmlns:svta` dropped from the §5.1.3 example | 7 | 1 | **2** |
| C3 chapter-5 rules on every XML example | `allowedLayouts="overlay-lower-third,overlay-corner"` in G.2; separately, `<svta:Click>` moved before the callback stream in K.4 and a `@backgroundUrl` put on an `overlay-corner` option | 0 | 0 | **2** (comma, then unknown token); **2** (child order, `@backgroundUrl` rule) |
| C4 `§X item N` pointing past the section's last item | `(§4.5.1 item 5)` → `(§4.5.1 item 9)` | 0 | 0 | **1** |
| C5 drafting markers | `TODO: settle this.` under §8.13 | 0 | 0 | **1** |
| C6 comma before `item` / `step` | `(§4.4 item 5)` → `(§4.4, item 5)` | 24 | 0 | **1** |
| C7 `<Metrics>` without `<Reporting>` in a document carrying a pause window | the `<Reporting>` of H.2 removed | 2 | 0 | **1** |
| C8 uppercase hex in `@codecs` | one `avc1.640028` → `avc1.64001F` | 0 | 0 | **1** |

Residues after the fixes, both known false positives: **C1 = 1** is L1323,
`(DASH Annex D.4.6, §5.9.1)`, where the `DASH` prefix distributes over both
clauses. **C2 = 1** is the §5.3.5 block at L2410, which now declares its
prefix and fails to parse only on the deliberate `...` elision between two
roots.

## What was not touched

- Nothing under `../context/`: `git status --porcelain context/` is empty.
- Nothing under `../context-analysis/`. The five modified files there were
  modified before this pass started and are unrelated to it.
- `../output-analysis/v10-spec-validation.md`, Step 7's artefact.
- The only file edited is `../output/v10-sgai-spec.md`; every changed line is
  listed in the autofix table (35 changed or inserted lines, 36 sites).

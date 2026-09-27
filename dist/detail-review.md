[GROUNDED_BY=spec-only]

# Spec detail review — v12.6 (2026-09-27)

**Review target**: `../output/v12.6-sgai-spec.md`.
**Reference**: `../context/` at git SHA `924afcbe273267ec3544bddb7858e327fd357a45`
(HEAD; the last commit touching `context/` is `0b82b92`, and
`git status --short context/` is empty).
**Method**: deterministic scan across eight micro-consistency categories;
autofixes applied in place, flags reported here.

## What this pass could and could not decide

**Grounding is spec-only.** The primary copy of the base standard was not
opened, by instruction. A `DASH §n` citation is checked only for whether it is
written as a base reference, never for whether the base clause says what is
claimed.

**v12.6 is two incremental builds over v12.4**, the last candidate with a
detail review (0 flags). v12.5 applied `e4abd85` and `58c1bf7` (DP-3, R5.3,
R5.7, R20.1, R20.4, UC-09); v12.6 applied `0b82b92` (UC-12). `diff` v12.4 →
v12.6 shows 33 hunks: §1.1 L230-238, the *Failed execution* term L404-411,
PUB-level DP-3 prose L653-662, PLY-20 L985-991, PLY-39 L1119-1121, PLY-41
L1143-1152, PLY-86 L1416-1422, §6 L3116-3119 and L3144, §7.12 L3391-3409,
§8.2 L3569-3573, E7/E8/E11 L3588-3592, §8.3 L3605-3607, §8.13 (item 14
removed) L3777-3783, Annex G L4411-4414, Annex L.7 and L.8 L6257-6294,
R-PLY-10 L7311, R-PLY-20 L7321, R.6 E7/E11 L7417 and L7421, and the
Refinement gaps rows 13-18 removed (L7483). Chapter 5 is byte-identical to
v12.4; the XML blocks are v12.4's 83 plus one new, the Annex L.7 document
(L6266-6276):

```
$ diff <(sed -n '/^## 5. Syntax/,/^## 6. Interfaces/p' output/v12.4-sgai-spec.md) \
       <(sed -n '/^## 5. Syntax/,/^## 6. Interfaces/p' output/v12.6-sgai-spec.md) && echo ch5-identical
ch5-identical
$ python3 -c '… findall(```xml …) on v12.4, v12.5, v12.6; sha256 of the concatenation'
12.4 83 09f69bf75151
12.5 83 09f69bf75151
12.6 84 0c7573b77990
```

The scans below ran over the whole document; each hunk was also read by hand
against the other sites that state the same thing.

**What the validation sidecar already carries is not repeated.**
`v12.6-spec-validation.md` routes two items that fall inside this prompt's
categories, both to 5.a with their replacement text:

- **T4 (A-10)**, category 2: PLY-86 L1420 names PLY-20 where PLY-38 is meant.
- **T5 (A-11)**, category 6: the status line L3 still says *"build iteration
  12.4"*, and the Refinement gaps table L7464-7482 says *"from the v12.3
  analyses"*, counts 22 un-moded criteria (now 23) and cites finding ids
  that name other findings in the current sidecars.

Neither is edited here, so that the refine step still finds the text T4 and
T5 quote. Neither is counted below.

## Summary

- **Autofixes applied: 0.** The spec is unchanged: 7 483 lines, sha256
  `197cbd888adccd34…949ba559e88a22`, the hash the validation sidecar records.
- **Issues flagged for human decision: 1** (Annex L.4's heading counts three
  paths in an annex that walks four).
- **The delta is otherwise internally consistent.**
  - PLY-41's new reading (a document none of whose candidates renders is a
    failed execution under PLY-38) is the one every other site now states:
    §1.1 L233-238, the *Failed execution* term L405-411, PLY-20 L989-991,
    §6 L3116-3119 and the `200` row L3144, §7.12 path 4 L3392-3398, §8.2
    L3571-3573, E7 L3588, Annex G L4412-4414, Annex L.7 L6279-6283, L.8,
    R-PLY-10, R-PLY-20, R.6 E7. The phrasings of the old reading are gone:
    `grep -ciE 'four shapes|not a failed execution|never the next window|not
    the next window|end at the primary|ends at the primary'` gives 0 on
    v12.6 and 8 on v12.4.
  - The *Failed execution* term L408-411 says the ways an attempt can fail
    are listed in §4.5.6; §4.5.6 carries all three it names (PLY-39, PLY-42,
    PLY-41). PLY-39 now scopes its *"four ways"* to the resolution itself,
    and its table has four rows.
  - §1.1 L237 points to §4.5.6 and §4.5.8; §4.5.8 is the relation to
    inherited linear events, which carries PLY-48, the supersede fall-back
    PUB-level prose L661 cites.
  - The removal of §8.13 item 14 leaves no dangling reference: `grep 'item
    14'` gives 0; the §8.13 items run 1-13, and the only `§8.13 item N`
    references (items 1, 9, 12, 13, L7474-7481) resolve. The
    `<!-- refine: …#K-36 -->` annotation at L1969 still stands alone for the
    §4.8.3 bullet removed in v12.4.
  - The new Annex L.7 document uses only names chapter 5 declares for
    `<svta:OverlayList>` (§5.2.2: `@family`, `@dismissAfter`),
    `<svta:Ad>` (§5.3.1) and `<svta:RenderableAsset>` (§5.3.2: `@src`,
    `@mimeType`, `@layout`; no `@duration`, as the video form requires). Its
    layout, `overlay-lower-third`, is the one window 1 admits (L.2 L6131).
  - §7.12's *"image overlay"* for window 2 and L.8's *"its L-shape"* name the
    same option: L.6 has D3 and D4 render option 2, the image in
    `squeezeback-l-shape-upper-left`, on an overlay window.
- Categories with no issues:
  - **format consistency.** Every table cell opens and closes with a space.
    `@profiles` is comma-separated in every example; `@allowedLayouts`,
    `@customRegion` and `@rect` are space-separated in every example.
  - **cross-reference consistency** (apart from T4, above).
    - Every bare `§n` and `Annex X[.n]` resolves against the document's
      headings. The scanner's remaining hits are base references whose
      `DASH` sits at the end of the previous line (L364, L755, L1722,
      L3717) and the definition of `Annex X` at L19. Every bare `X.n` ref
      resolves except the base's own Tables K.9 and K.18 (L265, L1895,
      L1926, L2382, L3889).
    - `PUB-1..18`, `ADS-1..3`, `APS-1..22`, `PLY-1..88` and `DOC-1..42`
      have no gap and no duplicate, and none is cited undefined.
    - `R-PUB-1..10`, `R-ADS-1..2`, `R-APS-1..14`, `R-PLY-1..47`,
      `R-SYN-1..5`, `R-IF-1..2`, `R-BEH-1..17`, `R-BC-1..5` have no gap and
      no duplicate.
    - Heading numbers have no gap in the chapters or the annexes; the one
      scanner hit is `5.0 Conventions` (L2058), numbered 0 by design.
  - **naming reuse with different semantics / same-name alignment.** The
    delta introduces no attribute or element name, and chapter 5 is
    byte-identical to v12.4, where these categories were clean.
  - **annex vs chapter mismatch.** The one new XML block is checked above;
    the other 83 and chapter 5 are byte-identical to v12.4, whose review
    found 0 mismatches.
  - **schema-namespace pinning.** All 83 non-schema XML blocks parse, so
    every prefix they use is declared. All 48 `xmlns:svta` are
    `urn:svta:dash:sgai:2026`.
  - **TODO / FIXME / placeholder leftovers.** No marker. The only hits are
    prose about a placeholder *value* (L957, L2762, L7309). The
    `<!-- delta: … -->` comments are the incremental step's audit
    annotations, which `apply-context-delta.prompt` writes by design, as
    `<!-- refine: … -->` are the refine step's.

## Autofixes applied

| # | Category | Spec ref | Rule anchor | Before | After |
|---|----------|----------|-------------|--------|-------|

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|----------|----------|-------------|-------------|----------------------|----------------|
| 1 | editorial regression | L6167 (Annex L.4 heading); L6262 (L.7); L6290 (L.8) | The spec itself: §7.12 L3380-3398 lists four paths, and L.8 L6290 refers to *"path 4 (L.7)"* | `### L.4 The three paths` titles the section that walks paths 1-3, while the annex now walks a fourth, *"**Path 4 — the first window's only candidate is a video overlay.**"*, under L.7. The heading is true of its own section and misleading of the annex: a reader of the table of contents looks for three. Not autofixed because the fix is a choice, not a normalisation. | (a) retitle L.4 `Paths 1 to 3`; (b) move path 4 into L.4, retitle it `The four paths`, and keep L.7 for the device walk | (a): one heading, and L.7's title already names what it adds. It mirrors the validation's P-2 on UC-12 (*"The three paths"* heading over four), which fixes `context/` and does not reach this heading |

## Instrument controls

Each scan was run on the spec and on a copy with one defect of its own class
injected. A scan that gives the same count on both cannot fail.

| Scan | Injected defect | Spec | Injected |
|---|---|---|---|
| C2 unresolved bare `§` refs | §1.1 `(§4.5.6,` → `(§4.5.66,` | 3 (base refs, above) | **4** |
| C2 `Annex X[.n]` refs | R-PLY-20 `Annex L.7` → `Annex L.9` | 2 (L19 definition, L755 base) | **3** |
| C2 bare `X.n` refs | L.7 `checked as L.6` → `L.66` | 9 (base Tables K.9, K.18) | **10** |
| C2 undefined criterion cited | PLY-41 `PLY-38` → `PLY-138` | 0 | **1** |
| C2 heading sequence | `### L.8` → `### L.9` | 1 (`5.0`) | **2** |
| C1 table cell spacing | `\| R-PLY-20 \| ` → `\| R-PLY-20 \|` | 0 | **1** |
| C1 `@profiles` delimiter | first `sps:2024,urn` → `sps:2024 urn` | 0 | **1** |
| C8 drafting markers | `TODO` inserted at the end of L.7 | 3 (prose hits above) | **4** |
| C7 parse / undeclared prefix | L.7 document `xmlns:svta` → `xmlns:svtb` | 0 | **1** (L6267, unbound prefix) |
| C7 namespace value | first `xmlns:svta` URN → `…:2025` | 1 value | **2** values |
| C6 old PLY-41 phrasings | same search on v12.4 | 0 | **8** |

## What was not touched

- `../output/v12.6-sgai-spec.md`: no byte changed.
- Nothing under `../context/`, `../context-analysis/` or `../dist/`.
- `../output-analysis/v12.6-spec-validation.md`, Step 7's artefact.

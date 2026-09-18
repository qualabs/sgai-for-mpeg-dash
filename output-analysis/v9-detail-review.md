[GROUNDED_BY=spec-only]

# Spec detail review — v9 (2026-09-18)

**Review target**: `../output/v9-sgai-spec.md`.
**Reference**: `../context/` at git SHA `25b340fda7650d0cff6b0c3dbda388960534a8a3`
(working tree clean for `context/`: `git status --porcelain context/` returns
nothing).
**Method**: deterministic scan across eight micro-consistency categories;
autofixes applied in place, flags reported here.

## What this pass could and could not decide

**Grounding is spec-only.** The primary copy of ISO/IEC 23009-1:2026 was not
opened, by instruction. That bounds categories 3 and 4 — *naming reuse with
different semantics* and *same-name same-semantics alignment* — to what the spec
itself states about its reuses. v9 introduces no element name, no attribute name
and no URI beyond the twelve elements, the three reserved parameters and the
five URIs chapter 2 and chapter 5 declare; the inventory of `svta:` element
names used in examples is exactly the twelve chapter 5 declares, and the
inventory of attributes carried on them is exactly the set chapter 5 tables.

**Every negative result below was taken with an instrument that was made to
fail first.** Each of the seven scans was re-run against a copy of v9 with one
defect of its own class injected, and each went from its clean count to that
count plus one. The controls are recorded in §"Instrument controls". A zero
from a scan that never fired is not reported as a zero.

**Line numbers are post-fix** unless the row says otherwise, so a reader can
open the file and land on the text.

## Summary

- **Autofixes applied: 73**, in 7 issue classes.
- **Issues flagged for human decision: 4.**
- Spec size: 8 663 lines / 481 846 B → **8 680 lines / 482 767 B**
  (+17 lines, +921 B). Every changed line belongs to one of the seven classes
  below; no prose was rewritten and no example was rebuilt.
- Categories with no issues:
  - **schema-namespace pinning** — all 71 XML blocks declare every prefix they
    use (`svta`, `up`, `xsi`), and all 66 complete documents parse.
  - **annex vs chapter mismatch, on names** — the 12 `svta:` element names and
    the 18 attribute-on-element pairs appearing in examples (plus one
    `xmlns:svta` declaration) are exactly those chapter 5 declares; every `@layout` value in every example is a member of
    §3.2's closed set and every `@form` value a member of §3.3's.
  - **TODO / FIXME / placeholder leftovers** — none. The two `placeholder`
    hits (L3011, L4596) are prose about a placeholder *value* a Player must
    not send and about a placeholder the Player does not draw; neither is a
    drafting marker.
  - **same-name same-semantics alignment** — no new name exists to judge.

## Autofixes applied

| # | Category | Spec ref | Rule anchor | Before | After |
|---|---|---|---|---|---|
| 1 | cross-reference consistency | 22 sites: L3666, L3668, L3671, L3744, L3746, L3782, L3806, L3863, L3877, L6292, L6459, L6847, L7393, L7410, L7476, L7539, L7584, L7589, L7596, L8168, L8172, L8319 | Notation block, L21: *"`DASH §X.Y` refers to a clause of the base specification identified in chapter 2"* | `(§5.16.2.2.5)`, `(§5.10.4.5.1)`, `(§8.13.1)`, … — bare, and unresolvable inside a document whose chapters stop at 8.12 | `(DASH §5.16.2.2.5)`, `(DASH §5.10.4.5.1)`, `(DASH §8.13.1)`, … |
| 2 | cross-reference consistency | L3846 | as row 1 | `a failure that stops playback"* (Annex D.4.6)` | `… (DASH Annex D.4.6)` |
| 3 | cross-reference consistency | L2103, L2351, L2367 | §4.4, L683-692, which is where the RFC 4337 media-type constraint is stated | `the media-type constraint of §4.7.2` / `…along the whole resolution path (§4.7.2)` / `inherits **no** media-type constraint (§4.7.3)` — §4.7.2 is `<svta:PauseAdPresentation>` and §4.7.3 is `<svta:OverlayList>`; neither mentions a media type | `… of §4.4` / `… (§4.4)` / `… (§4.4)` |
| 4 | cross-reference consistency | L1850 | §1.3 *Out of scope*, first bullet: *"**A parallel layout engine.**"* | `build the parallel layout system this specification declines to build (§1.2)` — §1.2 is *The four-actor model* | `… (§1.3)` |
| 5 | format consistency (casing) | 20 sites, spanning L3955 (Annex A) to L8314 (Annex N) | §5.4, L2646: *"`@codecs` values in every MPD this specification defines follow RFC 6381, which makes the codec identifier case-sensitive and recommends lowercase hexadecimal: `avc1.4d401f`."* | `codecs="avc1.4D401F"` | `codecs="avc1.4d401f"` |
| 6 | editorial regression | L3605, L3610, L8502 | §4.5.12 (L1049-1055) and §5.5.3 (L2764) write the multiplier as `1×` / `2×` | `differs from 1x`, `at 2x occupies 5 seconds`, `speed of 2x` | `differs from 1×`, `at 2× occupies 5 seconds`, `speed of 2×` |
| 7 | format consistency (XML prolog) | 21 blocks in Annexes K, L, M, N: L7252, L7289, L7347, L7480, L7606, L7625, L7671, L7691, L7721, L7802, L7852, L7891, L7930, L7974, L8027, L8065, L8086, L8178, L8231, L8249, L8287 | Annexes A..J: 40 of 40 complete-document examples open with the prolog. The annex preamble (L3898) states each annex carries *"the complete documents an implementation would exchange"* | ` ```xml ` then `<MPD xmlns=…` | ` ```xml ` then `<?xml version="1.0" encoding="UTF-8"?>` then `<MPD xmlns=…` |
| 8 | format consistency (delimiters) | 2 sites: before `## Annex D` and before `## Annex E` | 13 of the 15 annex boundaries are a blank line followed by the heading | `…\n\n---\n\n## Annex D — Hybrid…` | `…\n\n## Annex D — Hybrid…` |

Scope held deliberately: the prolog was **not** added to chapter 5's XML
examples. Five of them are fragments (`<EventStream>`, `<svta:Click>`,
`<Metrics>`) where a prolog would be wrong, and the chapter's own examples are
consistently prolog-free, so the chapter is internally consistent and the
annexes are the outlier. The malformed body in §L.4 (attempt 3) sits in a plain
fence rather than an `xml` fence and was left broken, which is what that
example is for.

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|---|---|---|---|---|---|
| 1 | cross-reference consistency (target does not exist) | L2588 and L2609, §5.3.7.3 | internal — chapter 8 | Both send the reader to **§8.4** for the conservative Player behaviour on re-tasking the decoder holding a paused frame. §8.4 is *Tracking-only decision entries*. The string `re-task` appears nowhere in chapter 8 (it appears at L2588, L2609, L5268 and L5304 only), so there is no section to repoint at. Two rows of the decoder budget — D3 and D4 on `pause-fullscreen`/`video` — rest on a conditional whose default is stated nowhere. | Either add the conservative default to §8.7 *Device-class fallbacks* and point both sites there, or state it inline in §5.3.7.3 and drop the pointer. | State it inline in §5.3.7.3. A budget table that defers its own default to another chapter is read by an implementer who never opens that chapter. |
| 2 | format consistency / editorial | Publisher main MPDs: L3925, L4091, L4274, L4681, L5046, L5501, L5736, L8198 (`advanced-linear:2025`); L6006, L6546, L6915 (`isoff-live:2011`); L7255, L7486, L7814 (`isoff-on-demand:2011`) | internal — no chapter states a rule for `MPD@profiles` on the Publisher's main MPD | Three different profile URIs are used for the same artefact. The split does not track content: Annexes C and E carry no alternative-MPD event and still declare `advanced-linear:2025`, while H, I, J and K, L, M carry none either and declare a base profile. Two of them are additionally odd on their own terms — Annexes I (L6546) and J (L6915) declare `isoff-live:2011` on a document whose `@type` is `static` with `@mediaPresentationDuration` set. | Decide the rule and state it once — e.g. `advanced-linear:2025` wherever the annex carries a linear window, a base profile otherwise — then align the 15 examples. | Flag, not autofix: choosing which profile an example's main MPD claims is a conformance judgement about the base standard, which is Step 8's mandate, not this pass's. |
| 3 | format consistency | L3898 (global), L5974, L6517, L6882 (`This annex is informative.`), L7234, L7458, L7790, L8164 (`*Informative.*`) | internal — the annex preamble, L3898: *"The annexes are informative."* | Three treatments of the same fact coexist: eight annexes say nothing, three carry a sentence, four carry an italic fragment — on top of a global statement that already covers all fifteen. | Remove the seven per-annex markers and let L3898 carry it. | Recommend removal, but flagged rather than applied: deleting prose lines is outside this pass's autofix list, which is confined to delimiters, cross-references, names and namespace declarations. |
| 4 | annex vs chapter mismatch (child order) | L7873 and L7998 (Annex M) against L6609 (Annex I) and L6974, L7006 (Annex J) | §5.3.1 children table, L2338-2339, which lists `<ImportedMPD>` then `<svta:BackgroundElement>` | Inside `<svta:RenderableAsset>`, Annexes I and J put `<ImportedMPD>` before `<svta:BackgroundElement>`; Annex M reverses it. The spec declares no content model, so neither order is wrong today — but a schema written from the chapter table would be an `xs:sequence` that rejects Annex M's two documents. | Either fix the order in Annex M to match the chapter table, or state in §5.3.1 that the children are unordered. | Decide the content model first. Reordering the examples without saying whether order is significant fixes the symptom and leaves the schema question open, which is why this is not an autofix. |

## Open questions surfaced

- **`@maxDuration` carries three reference frames under one baseline name** —
  the alternative presentation's bound on a linear slot (§5.1.1), the
  *cumulative rendered length of everything the slot presents* on an overlay
  window (§5.1.3), and the *display of one pause ad* on a pause window
  (§5.1.4, L1939). That is category 3's shape — a baseline name reused with a
  changed reference frame — and it is named here only so that category 3 is
  not read as empty. It is **not** re-flagged: Step 7 owns it as `G-5` and
  `D3` in `v9-spec-validation.md`, where the fix is a criterion in
  `context/03-requirements.md`, which this pass may not touch.

## Instrument controls

Each scan was run twice: once over `../output/v9-sgai-spec.md`, and once over a
copy with one defect of that scan's own class injected. The table records the
clean count and the injected count; a scan whose two counts agree would be a
scan that cannot fail, and none of the seven is.

| Scan | Injected defect | Clean count | With defect |
|---|---|---|---|
| C1 unresolved `§` refs | one resolving `(§4.5.4)` rewritten to `(§4.5.44)` | 24 | **25** |
| C2 uppercase codec hex | one `avc1.4d401e` uppercased | 20 | **21** |
| C3 ASCII-`x` speed notation | one `2×` written `2x` | 3 | **4** |
| C4 annex MPD block without prolog | the prolog stripped from §A.3's `ListMPD` | 21 | **22** |
| C5 stray `---` between annexes | one `---` added before `## Annex F` | 2 | **3** |
| C6 undeclared prefix / parse failure | `xmlns:svta` dropped from the §5.6.1 example; `<Period …/>` opened and not closed in §5.2.3 | 0 | **2** (one `svta` undeclared, one `mismatched tag`) |
| C7 drafting markers | `TODO: settle this.` added under §8.12 | 0 | **1** |

After the autofixes the same scans report **C1 = 2, C2 = 0, C3 = 0, C4 = 0,
C5 = 0, C6 = 0, C7 = 0**. C1's residue is L1444 and L1445, two cells of the
§4.7.13 audit table reading `DASH §5.2.1 + §5.10`, where the prefix distributes
over both clause numbers; those are correct as written and are the scan's only
known false positives.

## What was not touched

- Nothing under `../context/` (`git status --porcelain context/` is empty, and
  `git diff HEAD -- context/` is empty).
- Nothing under `../context-analysis/`. The five modified files there predate
  this pass and are unrelated to it.
- `../output-analysis/v9-spec-validation.md`, Step 7's artefact.
- `../output/v8-sgai-spec.md`, `../output/v8.1-sgai-spec.md` and every `v8` /
  `v8.1` sidecar: mtimes unchanged at 2026-09-17 22:56 through 2026-09-18
  00:45, against `v9-sgai-spec.md` at 2026-09-18 09:44.

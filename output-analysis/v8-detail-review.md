[GROUNDED_BY=spec-only]

# Spec detail review — v8 (2026-09-17)

**Review target**: `../output/v8-sgai-spec.md`.
**Reference**: `../context/` at git SHA `8547827f69e761d934cb0936afaa51e9c232941d`
(working tree clean for `context/`).
**Method**: deterministic scan across eight micro-consistency categories;
autofixes applied in place, flags reported here.

## What this pass could and could not decide

**Grounding is spec-only.** The primary copy of ISO/IEC 23009-1:2026 was not
opened, by instruction. This bounds categories 3 and 4 — *naming reuse with
different semantics* and *same-name same-semantics alignment* — to what the
spec itself states and quotes about baseline names. A finding that a construct
reuses a baseline identifier whose real unit or reference frame differs cannot
be produced without the base document, and none is asserted here on the spec's
own authority. What could be checked is whether the spec's claims about its
reuses are internally consistent with the semantics it then specifies, and
whether they follow `context/06-naming-and-namespaces.md`.

**Every negative result below was taken with an instrument that was made to
fail first.** Each scan was re-run against a deliberately broken copy of the
spec and against a file known to contain the pattern; the controls are recorded
in §"Instrument controls". A zero from a scan that never fired is not reported
as a zero.

**The spec had already been autofixed once** by a previous run of this step that
was killed before writing its log. Every edit below was re-derived against the
state of the file as found, so the table is what *this* run changed and not what
the step would change against the raw Step 6 output.

## Summary

- Autofixes applied: **32** — 32 distinct sites in 6 issue classes.
- Issues flagged for human decision: **2**.
- Spec line count: 7641 → **7657** (+16: 15 inserted blank lines, 1 from one
  rewrap). No text was added or removed — verified by normalising all
  whitespace and digit grouping in both versions and comparing (identical).
- Categories with no issues: **cross-reference consistency** (566 internal
  `§N.N` / `Annex X` references, all resolving; the only unresolved token is the
  literal `§N.N` in the notation note at L17, which is the convention statement
  itself); **schema-namespace pinning** (46 of 54 XML examples use a prefix, all
  declare it on the example root); **naming reuse with different semantics**
  (nothing new beyond what the Step 7 sidecar already holds — see §"Categories
  3 and 4"); **same-name same-semantics alignment** (same); **annex vs chapter
  mismatch** (every attribute and element in every example is declared in
  chapter 5, and every example satisfies the chapter's cardinality rules);
  **editorial regression** (no chapter/example disagreement found);
  **TODO / FIXME / placeholder leftovers** (none).

## Autofixes applied

Line references are **post-fix**, so the table can be audited against the file
as it now stands.

| # | Category | Spec ref | Rule anchor | Before | After |
|---|----------|----------|-------------|--------|-------|
| 1 | format consistency | L1985 | the same column of the same table (§5.3.7.3), which writes every other class list comma-separated, and the prose at L2013 which writes *"D3 and D4"* | `D1, D2; D3–D4 when` | `D1, D2; D3, D4 when` |
| 2 | format consistency | L2156 | the document's own thousands convention: 54 space-grouped occurrences against 15 unseparated ones, both used for the same quantities (`cap 15 000` at L6494 vs `admits 30000 units` at L3550; `midpoint at 7 500` at L5453 vs `beacon at 7500` at L4880) | `sit at 2500, 5000 and 7500.` | `sit at 2 500, 5 000 and 7 500.` |
| 3 | format consistency | L3295 | as #2 | `at 3750, 7500 and 11250 in` | `at 3 750, 7 500 and 11 250 in` |
| 4 | format consistency | L3523 | as #2 | `15000, not at 30000:` | `15 000, not at 30 000:` |
| 5 | format consistency | L3550 | as #2 | `admits 30000 units` | `admits 30 000 units` |
| 6 | format consistency | L3551 | as #2 | `presentation time 15000 within` | `presentation time 15 000 within` |
| 7 | format consistency | L3890 | as #2 | `at 0, 5000, 10000, 15000 and 20000 on` | `at 0, 5 000, 10 000, 15 000 and 20 000 on` |
| 8 | format consistency | L4813 | as #2 | `sit at 7500, 15000 and 22500 in` | `sit at 7 500, 15 000 and 22 500 in` |
| 9 | format consistency | L4880 | as #2 | `beacon at 7500 and` | `beacon at 7 500 and` |
| 10 | format consistency | L4881 | as #2 | `15000. The Player fires` | `15 000. The Player fires` |
| 11 | format consistency | L4882 | as #2 | `` `firstQuartile` at 7500, `` | `` `firstQuartile` at 7 500, `` |
| 12 | format consistency | L6054 | as #2 | `beacons at 3750, 7500 and 11250 are` | `beacons at 3 750, 7 500 and 11 250 are` |
| 13-15 | format consistency | L3555 (Annex C), L3896 (Annex D), L5870 (Annex J) | the other 11 annex status markers, which all read `*Informative.*` | `*(informative)*` | `*Informative.*` |
| 16-30 | format consistency (whitespace) | blank line inserted before the headings now at L3320, L3553, L3894, L4225, L4629, L4893, L5165, L5584, L5868, L6209, L6396, L6742, L7142, L7421, L7525 | every one of the other 220 headings in the document is preceded by a blank line; these 15 (`## Annex B` … `## Annex O`, `## Build notes`) were not | `…left untouched.`<br>`## Annex M — …` | `…left untouched.`<br>`` <blank> ``<br>`## Annex M — …` |
| 31 | format consistency (whitespace) | L7044-7047 (§M.6) | the document wraps prose at ≤ 75 columns (3 948 prose lines, 3 942 of them ≤ 79 columns). This line was 106 columns — an edit made without rewrapping the paragraph | `was published. The Player walks them in document order — option 1 needs a second decoder it does not have,` + 2 lines | the same text rewrapped over 4 lines at ≤ 67 columns |
| 32 | format consistency | L7472 (§O.2, T-P14) | English article agreement; the same row already writes `8 s` twice more | ``An `image` form with a 8 s candidate duration.`` | ``An `image` form with an 8 s candidate duration.`` |

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|----------|----------|-------------|-------------|----------------------|----------------|
| 1 | naming reuse (URI pattern) | L164-168 (§2.1); also L1189-1190, L1364, L1434, L1545 | `context/06-naming-and-namespaces.md` § *Scheme URI patterns* | `context/06` states that new event schemes **MUST** use `urn:svta:dash:<construct>:<year>`, and illustrates it with `urn:svta:dash:sgai-overlay:2026`. The four URIs the spec mints insert a **category segment** the pattern does not show: `urn:svta:dash:event:sgai-overlay:2026`, `urn:svta:dash:event:sgai-pause-trigger:2026`, `urn:svta:dash:profile:sgai-overlay-list:2026`, `urn:svta:dash:request:sgai-resolution:2026`. The spec is entitled to finalise the URI *list* — `context/06` says so explicitly — but not, on its own, the *pattern*. The divergence is not recorded in the spec's own Build-notes divergence list, which covers only three input statements that do not survive the base specification. | Either (a) read `<construct>` as a multi-segment path — which the spec's chosen form does, and which mirrors the baseline's own `urn:mpeg:dash:event:callback:2015` / `urn:mpeg:dash:profile:list:2024` — and say so in one sentence in §2.1; or (b) amend `context/06`'s pattern to `urn:svta:dash:<category>:<construct>:<year>` so the two documents read the same. | (a) **plus** (b). The spec's form is the better of the two and the baseline precedent is on its side, so the spec should not change; what should change is that neither document currently says the extra segment is intended, which leaves a reader auditing §2.1 against `context/06` with an apparent MUST violation. Renaming four published URIs is a decision, not a fix, so nothing was autofixed. |
| 2 | format consistency (example prologues) | 49 full-`<MPD>` examples, e.g. L1595 vs L3124 | internal only — no rule in `context/` or in chapter 5 fixes an example prologue | The XML examples do not share a prologue convention. The `<?xml version="1.0" encoding="UTF-8"?>` declaration appears on 33 of 49 full-MPD examples and is absent from 16 (all of chapter 5's skeletons and all of Annexes G, K, L and N). `xsi:schemaLocation` appears on 14 of 49. `@publishTime` appears on 10 of 15 primary-content manifests, absent from §5.8.1's example and from Annexes E, H, I and M. None of the three is required for the example to be correct — `@publishTime` is conditional in the base schema and this specification mandates it only on an Overlay Resolution Document (§5.2.2.2), where all 20 examples carry it. | Pick one convention and state it once, most plausibly: full annex documents carry the XML declaration, chapter-5 skeletons do not, `xsi:schemaLocation` is dropped everywhere (it is 14/49 today and carries nothing), and `@publishTime` is either on every full manifest or on none. | Normalise on the next build rather than by hand. Which convention wins is an authorial choice, and applying it here would mean touching up to 35 code blocks for no change in meaning — larger than the autofix mandate of this step. Flagged so the choice is visible, not because any example is wrong. |

## Categories 3 and 4 — why nothing new is reported

Four reuses of a baseline identifier were examined, and each is already handled
in the spec or already held by the Step 7 sidecar. No row is added for any of
them, so this section records the reasoning rather than a finding.

- **`@maxDuration` on the two new presentation elements.** §5.1.3.1 and §5.1.4.1
  both state that name, units and termination semantics are the baseline's, and
  §4.6.4 then states, per family, what the value bounds — *until when* for
  linear replacement, *how long* for insertion and overlay, and the display
  duration of one pause ad for the pause family. That asymmetry is declared,
  not silent. The question of whether the requirement set agrees with itself
  about it is `v8-spec-validation.md` A-1 and C1.
- **`@executeOnce` on a pause-trigger window.** §5.1.4.1 carries a subsection
  arguing the reuse and naming what changes: the counter observes a render
  rather than a playhead event. The open semantic questions are
  `v8-spec-validation.md` EC-1, EC-2 and F1, F2.
- **`@earliestResolutionTimeOffset` in two unit bases.** Both bases are
  inherited, and §5.2.1.3 carries an explicit unit note telling a reader to
  determine the base from the parent element.
- **`@duration` on `<svta:Candidate>`.** Typed `xs:duration`, i.e. the
  `Period@duration` shape rather than the timescale-unit shape of
  `<Event>@duration`, and §4.6.4 specifies the conversion and the rounding.

For category 4 — a new name minted where a baseline name with matching
semantics exists — the only new attribute at issue is `@assetUrl`. §5.3.2
weighs four DASH-conformant carriers in a table and states why three are
rejected. Deciding whether some baseline attribute already covers "the URL of
a non-media creative" requires the base document, which this step is instructed
not to open, so no verdict is offered either way.

## Instrument controls

Each scan was shown to fail before its result was believed.

| Scan | Positive evidence it fires | Control that made it fail |
|---|---|---|
| Internal `§` cross-references | 566 references resolved against 280 defined ids | appending `§4.9.9` and `§12.1` to the file: both reported unresolved |
| Namespace pinning in XML examples | 46 of 54 xml blocks use a prefix | deleting one `xmlns:svta=` declaration: the block at L1595 reported missing `svta` |
| Example attribute completeness | 21 `<svta:Candidate>`, 53 `<svta:RenderableAsset>`, 117 tracking `<Event>` elements parsed | removing `duration=` from one candidate and `id=` from one event: both reported |
| Markdown table cell counts | every table row counted, escaped `\|` normalised | adding a cell to one §3.2 row: reported as 5 cells against a 4-cell header |
| Drafting markers (`TODO` / `FIXME` / `XXX` / `TBD`) | the same regex returns 6+ hits on `v8-spec-validation.md` | injecting `TODO` and `TBD` into a copy of the spec: both found |
| Layout tokens against the closed set of §3.2 | 91 token occurrences parsed from `@layout` / `@allowedLayouts` | narrowing the closed set to three tokens: four violations reported |
| Content preservation across the autofixes | — | normalising all whitespace and undoing the digit grouping in both versions and comparing: identical, so the edits changed nothing but the intended bytes |

Checks that returned clean and needed no control, because they are positive
counts rather than negatives: 20 Overlay Resolution Document examples each
carrying the five `MPD` attributes §5.2.2.2 requires and a single `PT0S`
`<Period>`; 7 sub-MPD examples each matching §5.4's property table including
the RFC 4337 media types; all 53 presentation options satisfying §5.3.7.2's
`<svta:BackgroundElement>` rule (present exactly on
`squeezeback-double-box-with-background`, absent everywhere else); all
`@allowedLayouts` values space-delimited per `context/06` § *Preferred encoding
patterns*; all `@profiles` values single-URI, so the comma rule is unexercised;
no numbering gaps in any heading or obligation sequence.

## Open questions surfaced

- **Annex O carries no `*Informative.*` marker** where the other 14 annexes do.
  It is not an omission of meaning — its opening paragraph says *"It is
  informative"* in prose — but a reader scanning for the marker will not find
  one, and adding it to an annex titled *Test cases and conformance criteria*
  is a statement about normative status rather than a formatting fix, so
  nothing was changed.
- **Two cross-annex claims were verified rather than assumed**, and both hold
  exactly: §M.2's *"The manifest is byte-identical to Annex I's"* (the two
  blocks diff clean) and §M.6's *"the document Annex I shows, differing only in
  the instant it was published"* (the two blocks differ in `@publishTime` and
  nowhere else). They are noted because a claim of byte-identity is the kind
  that silently stops being true on the next build, and nothing in `bin/`
  checks it.

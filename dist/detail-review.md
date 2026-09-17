[GROUNDED_BY=spec-only]

# Spec detail review — v7.2 (2026-09-16)

**Review target**: `../output/v7.2-sgai-spec.md` (4803 lines before this
pass, 4802 after; chapters 1–8 + Annexes A–N + a 27-row trailing
`## Refinement gaps` table).
**Reference**: `../context/` at git SHA `38e782f` (working tree clean for
`context/`; repo HEAD `cb10ae1`).
**Method**: deterministic scan across the eight micro-consistency
categories; autofixes applied in place, flags reported here. Findings
already carried by `../output-analysis/v7.2-spec-validation.md` (8 gaps,
6 edge cases, 7 ambiguities, T1–T5, F1–F10, C1–C9) are not repeated —
where a candidate coincided with one of them it was dropped, and the
sidecar id is named in §Not reported.

## Summary

- Autofixes applied: **1**
- Issues flagged for human decision: **5**
- Categories with no issues: **format consistency** (delimiters,
  whitespace, casing and quoting all hold — see the measurements
  below); **naming reuse with different semantics** (category 3);
  **same-name same-semantics alignment** (category 4);
  **annex vs chapter mismatch** (category 5 — every attribute and
  element name used in an example is declared in chapter 5);
  **schema-namespace pinning** (category 7 — 31/31 XML blocks parse
  with every prefix bound inside the block, and the single
  `xmlns:svta` value `urn:svta:dash:sgai:2026` is used in all 20
  blocks that declare it); **TODO / FIXME / placeholder leftovers**
  (category 8 — no `TODO`, `FIXME`, `XXX`, `TBD` or
  `<!-- placeholder -->` in the document).

The 77 inline `<!-- refine: … -->` audit markers were left untouched
(77 before, 77 after).

### Measurements

| Property measured | Instrument | Before | After | Negative control |
|---|---|---|---|---|
| XML blocks well-formed, every prefix bound in the block | `ElementTree.fromstring`, bare `<__wrap__>` fallback for multi-root fragments (declares no prefix, so an unbound prefix still fails) | 31 ok / 0 bad | 31 ok / 0 bad | mutating one `</MPD>` inside a fence → 1 bad; deleting one in-fence `xmlns:svta=` → 1 bad (`unbound prefix`) |
| Drafting markers | `grep -nE '\b(TODO\|FIXME\|XXX\|TBD)\b\|<!-- *placeholder'` | 0 | 0 | same grep on a file containing `hello TODO world` → 1 hit |
| Prose hard-wrap at 72 columns (tables, fences, URLs and refine markers excluded) | line-length scan | 0 over | 0 over | same scan at 68 columns → 554 over |
| One attribute per line on every `<MPD>` root | per-root attribute count | 0 violations | 0 violations | — |
| Section / sub-clause numbering continuity per family (`#`-headings and `**N.N**` bold items) | per-family sequence check | 0 gaps | 0 gaps | renaming `#### 4.6.5` to `#### 4.6.6` → family `4.6` reported `[1,2,3,4,6,6,…]` |
| `§N`, `§X.n`, `Annex X`, `Annex X.n` refs resolve to a heading or bold sub-clause of this document | anchor set + reference scan | 12 residual, all base-specification citations (verified one by one, all qualified in their own sentence, in the §2 clause table, or by §4.7's "Every clause or annex cited in a DR-N label is a clause or annex of the base specification") | 12, same set | the same scan with the bold `**N.N**` anchors omitted reported 53 false positives, so the scan is not returning a vacuous zero |
| `@profiles` delimiter | value extraction | 20 values, each a single profile URI — no multi-value case, so the base specification's comma rule (§5.2.2.2 states it) is not exercised and nothing to normalise | unchanged | — |
| `@allowedLayouts` delimiter | value extraction | 10 values, all space-separated, matching `StringVectorType` per §5.1.3.1's encoding note | unchanged | — |
| `@codecs` | value extraction | 1 distinct value, `avc1.4d401f`, lowercase hex per §5.4 | unchanged | — |
| Abbreviations of §3.5 used at least once outside their definition | per-abbreviation count | 12/12 | 12/12 | — |
| SVTA elements audited in §4.7.3 | element inventory vs table rows | 11 of 12 | 11 of 12 | see flag 1 |

## Autofixes applied

| # | Category | Spec ref | Rule anchor | Before | After |
|---|----------|----------|-------------|--------|-------|
| 1 | editorial regression | §8.8, L2866 | internal — §5.5.2's note is the chapter statement: "The base specification places `<EventStream>` only as a child of `<Period>` (§5.3.2.3 of the base specification)" | `…rather than under a `<Period>` or the `<MPD>` (§5.5.2).` | `…rather than under a `<Period>` (§5.5.2).` |

§8.8 lists the placements that are conformant but novel against the
base specification's canonical shapes, so it has to name the canonical
shape correctly. `<MPD>` is not one: §5.5.2, which §8.8 cites in the
same sentence, states that the only canonical parent is `<Period>`, and
§5.5.2's own table gives the two admissible positions as the sub-MPD's
`<Period>` and `<svta:Candidate>`. Deleting the three words removes the
contradiction and changes no obligation; the chapter is the source of
truth and the implementation note is aligned to it. Edit is within
chapter 8, which the document declares non-normative.

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|----------|----------|-------------|-------------|----------------------|----------------|
| 1 | annex vs chapter mismatch | §4.7.3 audit table, L1055–L1068; construct declared at §5.6.1 L1993 | `context/07-backward-compat-checklist.md` §"Per-construct checklist" ("For each new construct C the spec introduces…") and §"Aggregated audit table"; internally, §4.7.3's own preamble — "Every construct this edition introduces is audited below" | `<svta:ClickTracking>` is the only one of the twelve SVTA-namespace elements the document introduces that has no row in the audit table. The other eleven — including `<svta:BackgroundElement>`, which like `<svta:ClickTracking>` is a leaf child discarded with its parent subtree — each carry one, so the omission is inconsistent with the table's own granularity rather than a deliberate roll-up. T-P15 ("For each construct in §4.7.3, a manifest containing it") derives its scope from the table, so the element also has no legacy test. | Add a row: Construct `<svta:ClickTracking>`; Placement `<svta:Click>` child; Extension rule §5.2.1 of the base specification, foreign namespace (DR-2, DR-3); Legacy Player discarded with the parent subtree; Sibling check n/a — never reached; Carrier class foreign-namespace open content — DR-6(a). Alternatively fold it into the `<svta:Click>` rows explicitly ("`<svta:Click>` and its `<svta:ClickTracking>` children"). | Add the row. Writing six columns of new content is generative rather than mechanical, so it is not autofixed; the separate row is preferable to the roll-up because `<svta:Click>` already occupies two rows for its two placements and a third construct folded into them makes neither row read as one construct. |
| 2 | editorial regression | §5.2.2.2, L1496–L1501 (table); examples at L1456, L1550, L3235, L3462, L3583, L4027, L4437 | internal — §5.2.1 is the parallel chapter statement for the linear document ("an MPD whose `@type` is `list`") | The table titled "`MPD` attributes on an Overlay Resolution Document" declares four attributes, all required, and omits `@type`. All seven Overlay Resolution Document examples in the document declare `type="static"`, and `@mediaPresentationDuration="PT0S"` — which the table does require — is only meaningful on a static MPD. The linear counterpart states its `@type` in §5.2.1's prose, so the non-linear document is the only one of the two whose `@type` is demonstrated everywhere and stated nowhere. | Add a row: `@type` \| yes \| `xs:string` \| `static` \| The document describes no media of its own and is not a live presentation. | Add the row. Not autofixed: fixing the value space of an inherited baseline attribute inside a profile-specific table is a normative statement about the profile, not a transcription. |
| 3 | cross-reference consistency | Annex N.3, L4745 | internal — §7.5 against Annex N.2 | The conformance-criteria row for "§7 Expected behaviour" reads "The per-scenario tests T-P1..T-P15". T-P18 (playback speed — "An ad presented while the primary content runs at 2×") is the test for the closing paragraph of §7.5.1 and for Annex B.5's trick-play variant, and it sits outside the range. T-P16 and T-P17 are correctly outside it: their actor is the APS, not the Player walking a scenario. The row carries a `<!-- refine: v7-detail-review.md#flag-7 -->` marker, so the range was already widened once (from `T-P1..T-P13`) without T-P18 being considered. | Replace the range with `T-P1..T-P15 and T-P18`, or replace it with the explicit list of the tests §7.5's ten scenarios map to. | Widen to `T-P1..T-P15 and T-P18`. Still not autofixed, for the reason the earlier pass gave: the range may be intended as "the annex-walk tests only", and picking between range and list is an editorial decision about what the row means. |
| 4 | cross-reference consistency | §3.2, L379–L381; §3.3, L409–L411 | internal — §5.3.1's own rows, which say "Value space in §5.3.2" for `@form` and "Value space in §5.3.3" for `@layout` | Both sentences attach the phrase "value space" to a pointer at §5.3.1, which is the attribute table and explicitly defers the value space one level down. §3.2: "…the complete admissible value space for `@allowedLayouts` on a slot declaration (§5.1.3, §5.1.4) and for `@layout` on a presentation option (§5.3.1)". §3.3: "They are the value space of `@form` on a presentation option (§5.3.1)." A reader following either pointer for the value space lands on a table that redirects. | §3.2: `(§5.3.3)`. §3.3: `(§5.3.2)`. Or keep §5.3.1 and drop the words "value space" from the sentences, if the pointer is meant to name where the attribute is declared. | Retarget to §5.3.3 and §5.3.2 respectively. Flagged rather than autofixed because the pointer is defensible under the second reading — it names the attribute's declaration site — so the intended target is genuinely ambiguous. Low severity; both targets are one section apart. |
| 5 | editorial regression | §8 preamble L2683 against §8.1 L2692/L2701/L2754 and §8.1.3 L2762 | internal — §4's RFC 2119 preamble, "to be interpreted as described in RFC 2119 and RFC 8174, when, and only when, they appear in all capitals" | Chapter 8 opens "This chapter is **non-normative**" and then emits RFC 2119 vocabulary in all capitals: the §8.1 table's "Player MAY" column header and its two prose references. §8.1.3 partly disclaims it ("Everything in the 'Player MAY' column that reports, logs or exposes a condition is non-normative") but then states the opposite for one item — "One boundary is normative rather than a matter of API shape" — so the chapter both denies and asserts normative force within four lines. The v7 pass lowercased six all-capitals `MAY` occurrences in the informative annexes on exactly this rule; chapter 8 was not in that scope. | (a) Lowercase the column header and the two prose references and delete the "One boundary is normative" sentence, relocating its content to §4.6.2 where the fall-through guarantee already lives; (b) keep the capitals and narrow §8's opening to "This chapter is non-normative except where it states otherwise"; (c) leave both and add one sentence reconciling them. | (a). The error-overlay boundary is a Player obligation and §4.6.2 is where the specification already carries it, so moving it removes the contradiction instead of documenting it. Flagged and not autofixed: relocating a normative sentence is a structural edit, and lowercasing alone would leave §8.1.3's "normative" claim standing in a chapter that denies it. |

## Not reported — checked and dropped

Recorded so a later pass does not re-derive them.

- **§3.2's `pause-ad` row pointing at §7.5.5** — the validation
  sidecar carries it as T3 (DL-1) with the same target, §4.6.9.
- **The `[inferred]` convention in the preamble (L15–L17)** with no
  `[inferred]` tag anywhere in the body — sidecar T4 (DL-2).
- **Annex D.3's "a `ListMPD` exactly as in Annex A.4, carrying one
  30-second ad"** against Annex A.4's `duration="PT15S"` — sidecar
  T2 (A-7).
- **§4.3.5's "on every slot" against the `Required: no` rows of
  §5.1.1 / §5.1.3.1 / §5.1.4.1** — sidecar T1 (A-2).
- **"candidate" meaning a sequence in §4.6.7 / Annex C.7 / T-P7 and
  an alternative in §4.6.6 / §8.1 E6 / T-E6** — sidecar A-1, the
  pass's highest-leverage item.
- **§2.1's `event:` / `profile:` URI segment against `context/06`'s
  `urn:svta:dash:<construct>:<year>` pattern** — sidecar A-6; the
  spec is the correct half.
- **`context/06-naming-and-namespaces.md`'s justification for the
  space delimiter**, which cites `@profiles` and `@codecs` as
  baseline space-separated lists. The spec does not inherit the
  error: §5.1.3.1's encoding note cites `@dependencyId` and
  `StringVectorType`, and §5.2.2.2 states the comma rule for
  `@profiles` correctly. `context/` is read-only here and the defect
  is upstream, so it is named and not filed against the spec.
- **`§5.10` at L1170 cited as "the baseline per-scheme skip rule"
  without the words "of the base specification"** — this document
  has no §5.10, so the citation cannot mis-resolve, and "baseline"
  qualifies it. Below the threshold for an edit.
- **`<svta:Advertiser>` and `<svta:UniversalAdId>` appearing in no
  XML example** — §5.7 declares both and §4.7.3 audits both;
  examples are not required to exhaust the vocabulary.
- **No linear example carrying `<svta:Click>` on a `ListMPD`
  `<Period>`** — adjacent to the sidecar's R28-on-the-linear-path
  finding (gap-table rows 3 and 27), which is where the remedy sits.

## Open questions surfaced

- **§5.1.2, L1196–L1197** — "`@returnOffset`, `@clip` and
  `@startWithOffset` are exclusive to `<ReplacePresentation>`;
  `<InsertPresentation>` carries **neither** of the three."
  *Neither* takes two items; with three the word is *none*. It fits
  none of the eight categories — it is not a format convention, a
  reference or a naming question — so it is surfaced rather than
  autofixed. Suggested: "carries none of the three".

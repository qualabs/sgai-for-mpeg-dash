[GROUNDED_BY=spec-only]

# Spec detail review — v7 (2026-09-16)

**Review target**: `../output/v7-sgai-spec.md`.
**Reference**: `../context/` at git SHA `cb10ae1` (working tree clean for
`context/`).
**Method**: deterministic scan across eight micro-consistency categories;
autofixes applied in place, flags reported here. No external authority was
consulted — conformance against MPEG-DASH 6th edition is Step 8's job. The
findings of `../output-analysis/v7-spec-validation.md` (G-1..G-8, EC-1..EC-5,
A-1..A-7) are excluded from this log and are not restated.

Line numbers in the **Autofixes** table are post-edit; the before-edit line is
given in parentheses so the edit can be located in a diff against the previous
state. Line numbers in the **Flagged** table are post-edit.

## Summary

- Autofixes applied: **8 issues**, **15 content changes** across 17 line ranges.
- Issues flagged for human decision: **11**.
- Categories with no issues: **naming reuse — same-name same-semantics**
  (category 4: no construct invents a name for a concept baseline DASH already
  covers; `@maxDuration`, `@earliestResolutionTimeOffset`, `@executeOnce`,
  `@duration`, `@profiles`, `@id`, `@value` are all reused verbatim);
  **annex vs chapter mismatch** (category 5: every `svta:` element name,
  attribute name, `@layout` token and `@mediaType` value used in an annex
  example is declared in chapter 5 / §3.2 / §3.3); **TODO / FIXME /
  placeholder leftovers** (category 8: none — see the instrument note below).

### Verification of the applied edits

| Property measured | Before | After |
|---|---|---|
| `xml` code blocks that parse as well-formed XML standalone | 21 / 31 | **31 / 31** |
| Over-long prose lines (> 74 cols, excluding headings, tables, code) | 1 | 0 |
| Headings (`^#`) | 211 | 211 |
| Chapters `## 1.`..`## 8.` | 8 | 8 |
| `## Annex A`..`## Annex N` | 14 | 14 |
| Code-fence lines (must be even) | 86 | 86 |
| Markdown table rows (lines beginning with a pipe) | 413 | 413 |
| Lines | 4581 | 4594 |

The XML row is the load-bearing one: the same parser run against the
pre-edit file reports exactly the 10 blocks this review patched as
`unbound prefix`, so the `0 bad` result is a measurement and not a
parser that accepts everything.

Whole-file content check: with all whitespace normalised, a word-level diff
of pre-edit against post-edit yields exactly **15 hunks** — the 5 inserted
`of the base specification` qualifiers and the 10 inserted `xmlns:svta`
declarations — and nothing else. Word count moves 33 953 → 33 983, which is
`5 × 4 + 10 × 1 = 30`. Every other byte that changed is line wrapping.

Instrument note for the category-8 zero: the same `TODO|FIXME|XXX|TBD|
placeholder` scan returns hits on the word `placeholder` where the spec uses
it as prose (§4.6.13, §5.8.3, Annex M.5), so the scan is not silently
returning nothing; there is no drafting marker in the document.

## Autofixes applied

| # | Category | Spec ref | Rule anchor | Before | After |
|---|----------|----------|-------------|--------|-------|
| 1 | schema-namespace pinning | §5.6.1 L1906 (was L1906) | category 7: an example declares every non-default namespace it uses | `<svta:Click clickThroughUrl="…">` | `<svta:Click xmlns:svta="urn:svta:dash:sgai:2026"` + `clickThroughUrl="…">` |
| 2 | schema-namespace pinning | Annex G.4 L3674 (was L3672) | as above | `<Period id="1" start="PT0S">` | `<Period xmlns:svta="urn:svta:dash:sgai:2026"` + `id="1" start="PT0S">` |
| 3 | schema-namespace pinning | Annex H.2 L3740 (was L3737) | as above | `<Period id="1" start="PT0S">` | same insertion |
| 4 | schema-namespace pinning | Annex I.2 L3849 (was L3845) | as above | `<EventStream schemeIdUri="urn:svta:dash:event:sgai-overlay:2026"` | `<EventStream xmlns:svta="urn:svta:dash:sgai:2026"` + `schemeIdUri="…"` |
| 5 | schema-namespace pinning | Annex J.2 L4013 (was L4008) | as above | `<EventStream schemeIdUri="…sgai-overlay:2026"` | same insertion |
| 6 | schema-namespace pinning | Annex J.3 L4036 (was L4030) | as above | `<svta:Candidate id="cand-1001-a" duration="PT15S">` | `<svta:Candidate xmlns:svta="urn:svta:dash:sgai:2026"` + `id="cand-1001-a" duration="PT15S">` |
| 7 | schema-namespace pinning | Annex J.3 L4057 (was L4050) | as above | `<svta:Candidate id="cand-1001-b" …>` | same insertion |
| 8 | schema-namespace pinning | Annex K.2 L4135 (was L4127) | as above | `<svta:Candidate id="cand-1101" …>` | same insertion |
| 9 | schema-namespace pinning | Annex L.2 L4218 (was L4209) | as above | `<Period id="1" start="PT0S">` | same insertion |
| 10 | schema-namespace pinning | Annex M.3 L4381 (was L4369) | as above | `<svta:Candidate id="cand-901" …>` | same insertion |
| 11 | cross-reference consistency | §4.7.2 L977 (was L977) | the spec's own convention — §3.1, §5.1.1, §5.1.6, §5.2.1.3, §5.2.2.1, §5.4 all write "of the base specification" when citing a base clause; the spec's own §7.3 is "APS behaviour" | `…which inherits §7.3 and constrains…` | `…which inherits §7.3 of the base specification and constrains…` |
| 12 | cross-reference consistency | §5.4 L1740 (was L1740) | as above | `…the profile inherits §7.3, which constrains…` | `…the profile inherits §7.3 of the base specification, which constrains…` |
| 13 | cross-reference consistency | §5.3 L1523 (was L1523) | as above; §2's clause table pins `@selectionPriority` to base §5.3.7.2, and the spec's own §5.3.7.2 is "Side-by-side / double-box and the background element" — three subsections below the citation | `` `@selectionPriority` (§5.3.7.2) `` | `` `@selectionPriority` (§5.3.7.2 of the base specification) `` |
| 14 | cross-reference consistency | §5.1.3 L1162 (was L1162) | as above; §2 pins Annex H to the Spatial Relationship Description, and the spec's own Annex H is "An overlay window crossing a pause-ad window" | `The Spatial Relationship Description of Annex H positions…` | `…of Annex H of the base specification positions…` |
| 15 | cross-reference consistency | §5.1.4 L1228 (was L1229) | as above; §2 pins Annex L to `urn:mpeg:dash:nonlinearplayback:2020`, and the spec's own Annex L is "Overlapping windows of the same family" | `…inside that window. Annex L already splits a construct…` | `…inside that window. Annex L of the base specification already splits a construct…` |
| 16 | format consistency | §5.7 L1942 (was L1941) | category 1: the document hard-wraps prose at 72 columns; this was the only body line over that | one 83-column line | wrapped to two lines |
| 17 | format consistency | Annex L.3 L4273-4276 (was L4263) | category 1: every other `<MPD>` root in the document (18 of them) puts one attribute per line | `type="static" minBufferTime="PT0S" mediaPresentationDuration="PT0S"` on one line | three lines, one attribute each |

Edits 11-16 changed the wrapping of the paragraph they sit in, because the
inserted qualifier pushed the following words past column 72. The two "Why a
new construct" paragraphs of §5.1.3 and §5.3 and the first bullet of §4.7.2
were re-wrapped at 72 columns as a consequence; the whole-file word-level
check above proves no word was added, removed or reordered in that re-wrap.

The 10 namespace edits target examples that are **excerpts** — a `<Period>`,
an `<EventStream>`, a `<svta:Candidate>` or a `<svta:Click>` shown without
its enclosing `<MPD>`. The declaration was therefore placed on the excerpt's
own outermost element, which is what makes the excerpt readable in isolation.
Only `xmlns:svta` was added; the default MPD namespace was left undeclared on
the `<Period>` and `<EventStream>` excerpts, because category 7 governs
non-default namespaces and adding a default namespace would change which
elements the example is asserting are in the core namespace.

## Flagged issues

| # | Category | Spec ref | Rule anchor | Description | Suggested resolution | Recommendation |
|---|----------|----------|-------------|-------------|----------------------|----------------|
| 1 | naming reuse with different semantics | §3.1 L330, §5.3.1 L1539 | `context/06` "Naming consistency with baseline DASH" | `@mediaType` on `<svta:RenderableAsset>` carries `video` / `image` / `html` — a creative-carrier form. Baseline DASH spells the adjacent concept `@mimeType` and binds it to the IANA registry via RFC 4337. The two differ in value domain and in what they constrain, but the names are one vowel apart and both read as "the media type". §3.1 defends the split in prose rather than removing the collision | Rename to something that cannot be read as a MIME type — `@form` (the term §3.1 already defines for exactly this dimension), or `@carrier` | Rename to `@form`. §3.1 defines "Form" as "the creative-carrier dimension of a presentation option", so the attribute would carry the name the terminology chapter already gives the concept, and the `@mediaType` / `@mimeType` definition in §3.1 becomes unnecessary |
| 2 | naming reuse with different semantics | §2.1 L206-207 | `context/06` "Scheme URI patterns" | `context/06` mandates `urn:svta:dash:<construct>:<year>` and illustrates it with `urn:svta:dash:sgai-overlay:2026`. The spec publishes `urn:svta:dash:event:sgai-overlay:2026` and `urn:svta:dash:event:sgai-pause-trigger:2026`, inserting an `event:` segment the pattern does not show | Either drop the `event:` segment to match the pattern literally, or amend `context/06` to declare the `<kind>` segment (`event:`, `profile:`) as part of the pattern | Amend `context/06`. The `event:` / `profile:` segment is doing real work — §2.1 also publishes `urn:svta:dash:profile:sgai-overlay-list:2026`, and without the segment the two would be indistinguishable by URI shape. The context file is the thing that is out of date, not the spec. Out of scope for this step (`context/` is read-only here) |
| 3 | naming reuse with different semantics | §2.1 L208, §5.2.2 | `context/06` "Naming consistency with baseline DASH" | The pause-ad family resolves to a document called the **Overlay** Resolution Document, declared by the profile URI `urn:svta:dash:profile:sgai-overlay-list:2026` and carrying a `<svta:OverlayList>`. §5.1 (L1065-1066) routes both the overlay family and the pause-ad family to it. A reader checking a pause-ad document against its declared profile finds "overlay" three times and no mention of pause ads | Rename the document, the profile URI and the list element to a family-neutral term (e.g. "Non-Linear Resolution Document", `urn:svta:dash:profile:sgai-candidate-list:2026`, `<svta:CandidateList>`), or state in §5.2.2 that "overlay" here names the non-linear family and not the `overlay` layout token | Rename. "Overlay" is already a `@layout` token in §3.2 with a narrower meaning, so the same word currently denotes a layout, a slot family and a document class. A note that explains the overload is cheaper to write and more expensive to live with. Editorial decision — this review did not touch it |
| 4 | cross-reference consistency | §4.7.1 L963; §5.1.3 L1167 | the spec's own citation convention (see autofixes 11-15) | Two base-specification annex citations remain unqualified. §4.7.1 writes "An Annex F construction"; §5.1.3 writes "Annex L's `urn:mpeg:dash:nonlinearplayback:2020`". Both collide by label with this spec's own Annex F (Multi-ad break) and Annex L (Overlapping windows). They were **not** autofixed because each already carries its own disambiguator in the same clause — the em-dash apposition ("a new delivery format with a new Interoperability Point URI") and the `urn:mpeg:dash:` URI — so inserting the qualifier would need a re-worded sentence rather than an insertion. The systemic half is larger: this spec's Annexes F, H, I, K and L all collide with base annexes cited in §2, and the spec's own §I.4 collides with the base's I.4 state vocabulary cited at L161 | Add a sentence to §1 or §2 fixing the convention — e.g. "A reference of the form §N or Annex X without qualification is to this document; references to the base specification always name it" — and then qualify the two remaining sites | Add the convention statement. It is one sentence and it retires the whole class, including the five colliding labels in §2's own clause table (§4.7, §5.2.1, §5.3.7.2, §5.6, §7.3, each of which is also a section number of this document). The alternative — re-lettering this spec's annexes to avoid the base's letters — is worse: the base uses A through L, so there is no clean escape |
| 5 | cross-reference consistency | §5.3.7.3 L1693 | internal — §5.8.2 vs §5.8.4 | The decoder-and-surface budget table is introduced as "what an APS that received capability parameters evaluates in §5.8.4". §5.8.4 is titled "What an absent parameter means" and its body is about undetermined values; the section that defines what a *received* parameter says about the device is §5.8.2 | Change the reference to §5.8.2, or to "§5.8" | Change to §5.8.2. Not autofixed because §5.8.4 does also discuss APS behaviour, so the intended target is arguable rather than obvious |
| 6 | editorial regression | §7.5.9 L2500 vs Annex L.3 L4289 | internal — chapter is the source of truth | §7.5.9 enumerates "three paths" for overlapping windows; path 2 is "the first window cannot be accessed and the second answers with a document carrying no candidates … the opportunity still resolved to no ads". Annex L.3's "Path 2" has the second window answer `200 OK, one candidate` and the Player render it. The two describe different outcomes under the same label, and Annex N's T-P13 ("run for each of the three paths") depends on the labels matching | Align the annex to the chapter, or align the chapter to the annex, and keep T-P13's three paths pointing at whichever survives | Align the **chapter** to the annex. The annex's path 2 is the one that exercises the fallback end to end — the chapter's variant tests the fallback request but never the render, which leaves "the fallback was used as declared" unobserved. This is the one case where the chapter-is-source-of-truth default is worth overriding, which is why it is flagged rather than autofixed |
| 7 | cross-reference consistency | Annex N.3 L4575 | internal — §7.5 against Annex N.2 | The conformance-criteria table maps "§7 Expected behaviour" to "The per-scenario tests T-P1..T-P13". §7.5.7 (a Player that predates this specification) maps to T-P15 and §7.5.10 (one ad resolved two ways) maps to T-P14, both outside the range | Widen to `T-P1..T-P15`, or replace the range with the explicit list of the tests §7.5's ten scenarios map to | Widen to `T-P1..T-P15`. Not autofixed because the range could equally be intended as "the annex-walk tests only", which would call for a list instead |
| 8 | cross-reference consistency | Annex N.4 L4588 | internal — §8.1 error table | The harness requirement reads "An APS that can be made to fail deliberately — timeout, non-`200`, truncated body, empty candidate list — for T-E1 to T-E5. The four failures must be independently triggerable." The range names five tests and the list names four modes: T-E4 (document arrives after the window elapsed) has no entry, and it needs a fifth capability — a delayed but successful response | Either add "delayed response" to the list and say "the five failures", or narrow the range to T-E1, T-E2, T-E3 and T-E5 | Add the delayed response and say five. T-E4 is a real test in N.1 and it needs the same deliberately-failing APS; narrowing the range would leave it with no harness requirement |
| 9 | editorial regression | §8.6 L2691-2693 | internal — the paragraph's own argument | The closing sentence reads "An implementation that renders an image form for as long as the slot window lasts, ignoring the candidate's declared duration, is reading a value the document does declare." The paragraph's point is that the declared duration **is** authoritative for a form with no intrinsic length, so the implementation described is *ignoring* a value the document declares, not reading one | Replace "is reading" with "is ignoring", or re-word to "is discarding a value the document does declare" | Replace with "is ignoring". Flagged rather than autofixed because it is a semantic inversion, and a wrong guess here reverses a normative-adjacent statement |
| 10 | format consistency | L2990, L3591, L3596, L3610, L3658, L4002 | §4 preamble L463-467 | §4 states that RFC 2119 key words are to be read as such "when, and only when, they appear in all capitals". Six all-capitals `MAY` occurrences sit inside annexes A, F, G and J, all of which open with "*Informative.*" — so the document is emitting normative permissions from non-normative text | Lowercase the six, or add a line to each annex preamble saying the annexes restate normative permissions and add none | Lowercase the six. Every one of them restates a permission already granted in §4.6 or §5, so nothing is lost, and an informative annex that carries no RFC 2119 vocabulary cannot be misread as adding a requirement |
| 11 | cross-reference consistency | whole document | `context/07-backward-compat-checklist.md` §2 and §8 | `context/07` requires that "The construct's chapter MUST name the applicable DR-N rule from `08-dash-extension-rules.md`" and that the DR-6 carrier classification "MUST be stated explicitly in the construct's chapter". The spec names **no** DR-N rule anywhere: §4.7.1 and the §4.7.3 audit table cite base clauses (§5.2.1, §5.10, §5.8.4.8/9) and spell the carrier class in prose ("Foreign-namespace open content", "Event Stream (§5.10)") instead. The information `context/07` asks for is present; the identifier it asks for is not | Add the DR-N label alongside the base clause in §4.7.1's extension-point table and in the §4.7.3 audit table's "Extension rule" and "Carrier class" columns, or amend `context/07` to accept the base-clause citation as satisfying the item | Add the labels. They are a two-token addition per row and they make the checklist auditable mechanically, which is the whole reason `context/07` names them. Flagged and not applied because it adds content to a normative table rather than correcting it, and because the alternative (amending `context/07`) touches a read-only directory at this step |

## Open questions surfaced

- **`<svta:Candidate id="cand-301-a">` in Annex C.4** is the only candidate in
  its document, but the `-a` suffix reads as one of a pair. Annex J.3 uses
  `-a` / `-b` for a genuine pair. Harmless, but a reader looking for
  `cand-301-b` will not find it.
- **Six of the nineteen complete MPD examples carry `xsi:schemaLocation`**
  (Annex A.2, A.4, A.5, B.2, C.2, C.4); the other thirteen do not. Either
  choice is fine; the mix is not. Left alone because adding or removing a
  schema location is an authoring decision, not a correction.

[GROUNDED_BY=spec-only]

# DASH conformance audit — v5 (2026-05-20)

**Audit target**: `../output/v5-sgai-spec.md`.
**Reference**: MPEG-DASH 6th edition (ISO/IEC 23009-1:2025).
**Method**: inventory built from §5 (Syntax) and the annexes;
verdicts grounded against `context/08-dash-extension-rules.md`
(DR-1..DR-7) and against the per-construct grounding already
performed in `v4-dash-conformance-audit.md` and `v4.1-dash-conformance-audit.md`.
No new NotebookLM queries were issued for this audit: every
construct in v5 either (a) inherits unchanged from v4.x and has
prior grounding, or (b) is a non-substantive rename / rewording
that does not change the DASH 6th surface. The two genuinely new
v5 design choices — `<Period>@duration="PT0S"` in §5.2.2 and
`@earliestResolutionTimeOffsetTicks` in §5.1.3 — are verified
against the DR-1..DR-7 rules in `context/08-dash-extension-rules.md`,
which themselves were grounded against the DASH 6th notebook
during the analysis phase.

## Scope

Inventory of constructs new or modified by v5 relative to the
DASH 6th baseline. Verdicts per construct: **Conforming**
(spec-only or prior-grounded), **Marginal** (ambiguous reading
flagged), **Non-conforming** (cites a violated rule).

## Method summary

- Inventory built from §5 (Syntax), §6.6 (VAST mapping), §8
  (Implementation notes), Annexes A–I.
- Constructs that are byte-identical with v4.2 carry forward
  their verdicts from `v4-dash-conformance-audit.md` /
  `v4.1-dash-conformance-audit.md`.
- v5-only changes audited explicitly below: (1) attribute rename
  `@earliestResolutionTimeOffset` → `@earliestResolutionTimeOffsetTicks`
  on `<svta:OverlayPresentation>`; (2) `<Period>@duration="PT0S"`
  envelope inside the Overlay Resolution Document (§5.2.2);
  (3) removal of `@maxConcurrent` (DP-1.1 simplification);
  (4) new §4.4.8 / §7.6 pause-and-overlay composition rules
  (no new XML construct; behaviour only); (5) new §4.4.9
  click-through interaction rules (no new XML construct; binds
  existing `<svta:Click>` to viewer interaction).

## Inventory + verdicts

| ID | Construct | Type | Placement | Verdict | Rationale |
|----|-----------|------|-----------|---------|-----------|
| C-01 | `<InsertPresentation>` | Reused | `<Event>` child of `<EventStream>` (scheme `urn:mpeg:dash:event:alternativeMPD:insert:2025`) | Conforming | Byte-identical with v4.2. §5.16.3 of the base specification; reused verbatim. The inherited schema-vs-prose split on `@url` / `@uri` is acknowledged in §2 and §5.1.1 NOTE blocks. |
| C-02 | `<ReplacePresentation>` | Reused | `<Event>` child of `<EventStream>` (scheme `urn:mpeg:dash:event:alternativeMPD:replace:2025`) | Conforming | Byte-identical with v4.2. §5.16.4 of the base specification. |
| C-03 | `<svta:OverlayPresentation>` | New | `<Event>` child of `<EventStream>` (scheme `urn:svta:dash:event:sgai-overlay:2026`) | Conforming | Uses §5.2.1 foreign-namespace open content (DR-2). Required-sibling check passes (no baseline sibling depends on it). Year-pinned scheme URI. Walk-through in §5.1.3 and §G.2 / §G.3. R8 / R9 justification block present. |
| C-04 | `<svta:PauseAdPresentation>` | New | `<Event>` child of `<EventStream>` (scheme `urn:svta:dash:event:sgai-pause-trigger:2026`) | Conforming | Same envelope as C-03; year-pinned scheme URI; R8 / R9 justification present. The omission of `@earliestResolutionTimeOffsetTicks` is justified inline (pause = the ERT). Detail-review flag #2 suggests adding an explicit NOTE; not a conformance issue. |
| C-05 | `@earliestResolutionTimeOffsetTicks` on `<svta:OverlayPresentation>` | New (renamed from `@earliestResolutionTimeOffset` in v4.x) | Attribute on `<svta:OverlayPresentation>` (foreign-namespace element) | Conforming | Renamed per `context/06-naming-and-namespaces.md` N06.11 to surface the unit-collision with baseline `@earliestResolutionTimeOffset` on `<ImportedMPD>` (§5.3.2.6.1 of the base specification carries seconds; the SGAI-side attribute carries `<EventStream>@timescale` ticks). The rename closes the v4-detail-review flag #1 / v4.1-spec-validation g-10 issue carried forward in v4.2. Attribute lives on a foreign-namespace element, so DR-2 / DR-3 strip the entire `<svta:OverlayPresentation>` subtree on legacy Players — no schema collision with baseline DASH. |
| C-06 | `<svta:OverlayList>` | New | Child of `<Period>` (in Overlay Resolution Document, foreign-namespace) | Conforming | §5.2.1 foreign-namespace open content (DR-2). The non-zero-duration-Period-requires-AdaptationSet rule from §5.3.2.2 Table 4 is sidestepped by setting `<Period>@duration="PT0S"` — see C-07. |
| C-07 | `<Period>@duration="PT0S"` envelope (Overlay Resolution Document) | New design choice | Single `<Period>` child of `<MPD>` in the resolution document | Conforming | §5.3.2.2 Table 4 requires "at least one AdaptationSet" only for non-zero-duration Periods. With `@duration="PT0S"`, the requirement is waived. This closes the v4.x carry-forward gap #1 ("Overlay Resolution Document carries zero `<Period>` elements") which was non-conforming in v4.2 because v4.2 placed `<svta:OverlayList>` as a direct child of `<MPD>` (violating `MPDType` `minOccurs=1` for `<Period>`). v5 places it inside a zero-duration Period: the `<MPD>` now has the required child, and the zero-duration Period is admissible under §5.3.2.2 Table 4. Grounding source: `context/08-dash-extension-rules.md` DR-7. |
| C-08 | `<svta:Candidate>` | New | Child of `<svta:OverlayList>` | Conforming | Foreign-namespace open content (DR-2). |
| C-09 | `<svta:RenderableAsset>` | New | Child of `<svta:Candidate>` | Conforming | Foreign-namespace open content (DR-2). |
| C-10 | `<svta:RenderableAsset>` child `<ImportedMPD>` | Modified placement | `<ImportedMPD>` reused inside the SGAI form construct | Conforming | The `<ImportedMPD>` XML shape is the baseline §5.3.2.6, but its parent is the SGAI-namespaced `<svta:RenderableAsset>`, not a `ListMPD`-level `<Period>`. The §5.2.1 NOTE 2 ensures that legacy parsers strip the entire `<svta:RenderableAsset>` subtree (including the nested `<ImportedMPD>`), so no §5.3.2.6.1 binding triggers for legacy clients; SGAI-aware Players interpret the `<ImportedMPD>` per §5.3.4 SGAI semantics. Verdict carry-forward from v4 audit M-4 (which was Marginal and resolved by the inline NOTE in §5.3.4); v5 keeps the NOTE. |
| C-11 | `<svta:RenderableAsset>` child `<EventStream>` (tracking carrier) | Modified placement | Baseline `<EventStream>` placed inside SGAI-namespaced parent with reinterpreted `presentationTime` reference frame | Marginal | The `<EventStream>` XML shape is baseline §5.10, but the `presentationTime` reference frame is reinterpreted (relative to form-visible instant, not Period start). DR-2 / DR-3 stripping by legacy clients ensures no semantic drift on the baseline side. The Marginal verdict is carried forward from v4 detail-review flag #2 / v4.1 G-A-5: the pattern "baseline DASH element under SVTA parent with reinterpreted timing" is admissible only because the foreign-namespace parent isolates it from legacy interpretation, but `context/08-dash-extension-rules.md` does not explicitly admit the pattern as a normative rule. v5 adds an inline NOTE in §5.5.3 stating the reinterpretation and citing DR-2 / DR-3 as the protection; the underlying context-level decision (whether to canonise this pattern as DR-8) remains punted. |
| C-12 | `<svta:Click>` | New | Child of `<svta:Candidate>` | Conforming | Foreign-namespace open content (DR-2 / DR-6 carrier (a)). |
| C-13 | `<svta:UniversalAdId>` | New | Child of `<svta:Candidate>` | Conforming | Foreign-namespace open content (DR-2 / DR-6 carrier (a)). |
| C-14 | `urn:svta:dash:profile:sgai-overlay-list:2026` | New | `MPD@profiles` value on the Overlay Resolution Document | Conforming | §8.1 of the base specification admits externally-defined profile URIs in `MPD@profiles`. Year-pinned per N06.5 / N06.7. The profile URI distinguishes the Overlay Resolution Document from a `ListMPD` cleanly. |
| C-15 | `urn:svta:dash:event:sgai-overlay:2026` (scheme URI) | New | `<EventStream>@schemeIdUri` | Conforming | Year-pinned per N06.1 / N06.5. Ignore-if-unknown semantics inherited from §5.10. |
| C-16 | `urn:svta:dash:event:sgai-pause-trigger:2026` (scheme URI) | New | `<EventStream>@schemeIdUri` | Conforming | Same envelope as C-15. |
| C-17 | `urn:svta:dash:sgai:2026` (XML namespace) | New | Namespace declaration on every SGAI element | Conforming | DR-2 foreign-namespace; §5.2.1 NOTE 2 ensures legacy discard. |
| C-18 | Co-located linear + overlay events (hybrid slot) | New design pattern | Two `<EventStream>` siblings at the same `presentationTime` | Conforming | §5.10 of the base specification places no prohibition on multiple `<EventStream>` declarations inside the same `<Period>`. Each stream's events fire independently. The Player's serialisation rule (§4.4.7, §7.6, §7.4) covers the resulting concurrency. |
| C-19 | Linear `ListMPD` (§8.14, reused) | Reused | Resolution document | Conforming | Byte-identical with v4.2. |
| C-20 | Sub-MPD (SPS profile, §8.15, reused) | Reused | Reached via `<ImportedMPD>` from `ListMPD` Period or video-form `<svta:RenderableAsset>` | Conforming | Byte-identical with v4.2. RFC 4337 binding on `@mimeType` per DR-1. |
| C-21 | `<UrlParamInfo>` (§I.4, reused) | Reused | Inside `<MPD>` (and other admissible parents per §I.3.1) | Conforming | Byte-identical with v4.2. The §I.3.1 vs §5.3 schema-vs-prose split on the element name (`<UrlParamInfo>` vs `<RequestParam>`) is documented in §2 NOTE. |
| C-22 | Callback event scheme `urn:mpeg:dash:event:callback:2015` (§5.10.4.5, reused) | Reused | Tracking carrier scheme | Conforming | Byte-identical with v4.2. R13.4 satisfied (no new tracking scheme introduced). |

## NotebookLM findings (highlights)

No new NotebookLM queries were issued in this audit. The
underlying DASH 6th rules consulted are encoded into the
`context/08-dash-extension-rules.md` DR-1..DR-7 ruleset, which
was itself grounded against the "streaming specs" notebook
during the analysis-phase build. The two new v5 design choices
audited above resolve cleanly against that ruleset:

- C-07 (`<Period>@duration="PT0S"` envelope): closes the v4.2
  non-conforming item ("Overlay Resolution Document carries
  zero `<Period>` elements") by satisfying §5.3.2.2 Table 4
  (DR-7) — non-zero-duration Periods require an AdaptationSet;
  zero-duration Periods do not.
- C-05 (`@earliestResolutionTimeOffsetTicks` rename): closes the
  v4.x carried-forward issue (`@earliestResolutionTimeOffset`
  reused on `<svta:OverlayPresentation>` with a different unit
  from `<ImportedMPD>`) by following N06.11 (rename when
  semantics differ).

## Non-conforming items detail

None. The v4.2 non-conforming item N-1 (Overlay Resolution
Document violates `MPDType` `minOccurs=1` for `<Period>`) is
resolved by C-07.

## Marginal items detail

### M-1. `<svta:RenderableAsset>` child `<EventStream>` reinterprets baseline timing semantics (C-11)

**Construct**: A baseline DASH `<EventStream>` is placed inside
the SVTA-namespaced parent `<svta:RenderableAsset>` (§5.5.3).
The `<Event>@presentationTime` is reinterpreted: in the
baseline (§5.10.2.1), `presentationTime` is relative to the
carrying Period's start; the SGAI placement here reinterprets
it relative to the form-visible instant.

**Ambiguity**: The DR-2 / DR-3 fallback semantics (legacy
parsers strip the entire `<svta:RenderableAsset>` subtree)
prevent legacy clients from observing the reinterpretation, so
there is no observable conformance issue on legacy Players.
However, `context/08-dash-extension-rules.md` does not have a
normative rule (no DR-8) that explicitly admits "baseline DASH
element under SVTA parent with reinterpreted timing" as a
canonical pattern. A reviewer might object that the spec
re-uses a baseline element name (`<EventStream>`) with altered
semantics, which N06.11 generally forbids.

**Suggested clarification**: Either rename the SGAI-side
tracking carrier to a new SVTA-namespaced element (e.g.
`<svta:TrackingEvents>`) that owns its own
`presentationTime` semantics, OR canonise the pattern in
`context/08-dash-extension-rules.md` as a new DR-8 "Baseline
DASH child under SGAI-namespaced parent with reinterpreted
reference frame admits new semantics, because DR-2 / DR-3 strip
the parent on legacy parsers". v5 prefers the latter (less
syntactic churn for ADS authors familiar with the callback
scheme) but does not yet have context-side admission.

**Carried-forward from v4 detail-review flag #2 / v4.1 G-A-5**.

## Open questions surfaced

- **Whether `@earliestResolutionTimeOffsetTicks` is the right
  rename**. The current choice is concise and surfaces the unit
  difference at the call site, but a future minor refinement
  MAY prefer a verbose name (e.g. `…InEventStreamTicks`). This
  is a naming-policy decision, not a conformance issue.
- **`<svta:Candidate>@priority` redundancy with declared
  order**. The attribute is informational per v5 §5.2.2, but
  per DP-1.2 "single source of truth", an informational
  attribute that duplicates a structural relationship (the
  document's declaration order) is a soft regression. Tracked
  as ambiguity A-2 in `v5-spec-validation.md`. Not a DASH 6th
  conformance issue.

## Summary

- Total constructs audited: 22
- Conforming: 21
- Marginal: 1 (carry-forward, no v5-introduced regression)
- Non-conforming: 0
- Fetch-failed: 0

Comparison with v4.2: v4.2 had **1 Non-conforming item** (N-1,
Overlay Resolution Document `<Period>` requirement) carried in
its refinement-gap table. v5 closes N-1 via the
zero-duration-Period envelope (C-07). No new conformance
regressions introduced.

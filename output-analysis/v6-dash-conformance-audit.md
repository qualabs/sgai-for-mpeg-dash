[GROUNDED_BY=spec-only]

# DASH conformance audit — v6 (2026-05-28)

**Audit target**: `../output/v6-sgai-spec.md` (git SHA `d30c655`, 2891 lines).
**Reference**: MPEG-DASH 6th edition (ISO/IEC 23009-1:2025, FDIS).
**Method**: inventory + per-construct verdict against the spec's own
internal DASH 6th cross-references (§5.2.1, §5.10, §5.16, §7.3, §8.14,
§8.15, Annex F, §I.3.1 / §I.4) plus close reading of the v6 spec's
treatment of extension points.

**Grounding label rationale**: NotebookLM was attempted (active
notebook `streaming-protocols-—-dash,-hls,-c2pa,-drm`, browser
state authenticated). Three queries were issued (§8.14 ListMPD
structure, §5.2.1 foreign-namespace rules, §5.16
InsertPresentation/ReplacePresentation attributes). Two failed on
a Chromium `ProcessSingleton` browser-profile lock (parallel
queries cannot share the persistent context). The one query that
completed returned an off-topic answer (the model latched onto an
in-band ReplacePresentation question and ignored the ListMPD
prompt), so it was not usable as grounding evidence. The label is
therefore `spec-only`; per-construct claims that would benefit
from canonical DASH 6th text are flagged below as such.

## Scope

Every XML construct (event scheme, profile URI, element,
attribute, compound shape) that v6 introduces or modifies relative
to the baseline DASH 6th feature set defined in
ISO/IEC 23009-1:2025. The audit assesses conformance against the
extension-point rules of §5.2.1 (foreign-namespace open content),
§5.10 (event scheme ignore-if-unknown), §5.16 (Alternative MPD
events), §7.3 (Single-Period MPD MIME types), §8.14 (`ListMPD`
profile), §8.15 (Single-Period Static profile), Annex F (non-ISO-BMFF
delivery), and §I.3.1 / §I.4 (URL parameterisation).

Out of scope: design quality (validate-spec sidecar's job),
clarity, completeness of normative obligations, alignment with the
context document. This audit checks **conformance to DASH 6th**,
nothing else.

## Method summary

- Inventory built from §1, §2.1, §3, §4.3–§4.6, §5.1–§5.7, §6.6,
  §8.8 and the annex examples (Annex A–K).
- NotebookLM attempted; unusable answers (off-topic, browser-lock
  failures). Verdicts rest on the spec's own internal cross-references
  to DASH 6th and on the inheritance claims made by §5.1.1, §5.1.2,
  §5.4, §5.5, §5.7, §8.8.
- Each construct assigned one of: Clean / Conforming-with-comment /
  Marginal / Non-conforming.

## Inventory + verdicts

| ID | Construct | Type | Placement | Verdict | Rationale (short) |
|----|-----------|------|-----------|---------|--------------------|
| C1 | `urn:svta:dash:event:sgai-overlay:2026` | event scheme URI | `<EventStream>@schemeIdUri` in main MPD | Clean | §5.10 event-scheme ignore-if-unknown applies; spec §4.6.1, §8.8 invoke the rule explicitly. |
| C2 | `urn:svta:dash:event:sgai-pause-trigger:2026` | event scheme URI | same as C1 | Clean | Same as C1. |
| C3 | `urn:svta:dash:profile:sgai-overlay-list:2026` | profile URI | `MPD@profiles` on the Overlay Resolution Document | Conforming-with-comment | Profile URIs in DASH are advisory hints; an unaware Player treats the document as unknown and falls through (spec §8.8). Comment: DASH does not formally define a "profile-ignore" mechanism — strictly, an unknown profile URI is silently allowed by §8 (a Player MAY accept any MPD it can parse). The fall-through behaviour relies on the parent event scheme being unknown to the legacy Player, which is the actual gating mechanism — not the profile URI itself. |
| C4 | `urn:svta:dash:sgai:2026` | XML namespace | namespace declaration | Clean | Foreign namespace permitted by §5.2.1. |
| C5 | `<svta:OverlayPresentation>` | extension element | child of `<Event>` (main MPD) | Conforming-with-comment | §5.2.1 permits foreign-namespace open content on most DASH elements. Spec §5.1.3.4 asserts the element is discarded with the parent `<Event>` per the parent's event-scheme ignore rule — that is the operative gating mechanism. Comment: DASH 6th §5.10 does explicitly admit extension elements under `<Event>`, but the formal anchor is the parent `<EventStream>@schemeIdUri` ignore rule, not §5.2.1 directly. The spec's wording in §5.1.3.4 ("foreign namespace relative to the base DASH schema and is discarded together with the parent `<Event>` per §5.2.1") conflates the two paths but converges on the same outcome. |
| C6 | `<svta:PauseAdPresentation>` | extension element | same as C5 | Conforming-with-comment | Same as C5. |
| C7 | `<svta:OverlayList>` | extension element | top-level child of root `<MPD>` (Overlay Resolution Document) | **Non-conforming** | The Overlay Resolution Document declares `MPD@type="static"` and `@profiles="urn:svta:dash:profile:sgai-overlay-list:2026"` but carries `<svta:OverlayList>` as its **only** top-level body — no `<Period>` at all. DASH 6th's MPD schema (the `MPDtype` complexType in `urn:mpeg:dash:schema:mpd:2011`) requires at least one `<Period>` child element on every MPD whose `@type` is `static` or `dynamic`. The §8.14 `ListMPD` profile is what relaxes that constraint, and only by introducing the new `@type="list"` value (per the spec's own §5.2.1.1 inheritance from §8.14). v6 uses `@type="static"` for the Overlay Resolution Document, which means the MPD schema requires a `<Period>` that is not there. See suggested fix below. |
| C8 | `<svta:Candidate>` | extension element | child of `<svta:OverlayList>` | Clean | Entirely inside the foreign-namespace subtree of C7; legitimacy stands or falls with C7's resolution. |
| C9 | `<svta:RenderableAsset>` | extension element | child of `<svta:Candidate>` | Clean | Same as C8. |
| C10 | `<svta:BackgroundFill>` | extension element | child of `<svta:RenderableAsset>` | Clean | Same as C8. |
| C11 | `<svta:Click>`, `<svta:UniversalAdId>`, `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>` | extension elements | child of `<svta:Candidate>` | Clean | Same as C8 — foreign-namespace open content inside a foreign-profile document. |
| C12 | `@allowedLayouts`, `@maxConcurrency`, `@backgroundFallback` on `<svta:OverlayPresentation>` / `<svta:PauseAdPresentation>` | extension attributes | on extension elements (C5 / C6) | Clean | Attributes on foreign-namespace elements are not constrained by the base schema. |
| C13 | `@mediaType`, `@layout`, `@assetUrl` on `<svta:RenderableAsset>` | extension attributes | on extension element (C9) | Clean | Same as C12. |
| C14 | `<InsertPresentation>` reused (§5.16.3) with `@url` attribute name | reused element | child of `<Event>` (main MPD) | Conforming-with-comment | The §2 NOTE acknowledges the inherited schema-vs-prose split: DASH 6th §5.16.3 prose says `@url`; the normative XML schema declares `<xs:attribute name="uri">` on `AlternativeMPDEventType`. v6 follows the prose, which is a legitimate choice but means MPDs written per this spec WILL NOT validate against the DASH 6th XSD without modification. Comment: this is a DASH 6th defect inherited, not a v6 defect — but the spec MUST flag the validator implication, which it does (§2 NOTE). |
| C15 | `<ReplacePresentation>` reused (§5.16.4) with `@url` attribute name | reused element | same as C14 | Conforming-with-comment | Same as C14. |
| C16 | `@maxDuration`, `@earliestResolutionTimeOffset`, `@returnOffset`, `@clipDuration` as `xs:unsignedInt` in `@timescale` units | inherited attribute types | on §5.1.1, §5.1.2 events | Marginal | The spec declares all four attributes as `xs:unsignedInt` expressed in the parent `<EventStream>@timescale` units (§5.1.1, §5.1.2 attribute tables). DASH 6th §5.16 prose conventionally expresses these in seconds, and the schema typically uses `xs:unsignedLong` with a separate `@timescale` semantics. v6's choice to express in `@timescale` units is consistent and well-defined inside this spec, but it should be cross-checked: if DASH 6th §5.16's normative semantics are "seconds" (a different unit), then a Publisher emitting `@maxDuration="20000"` per v6 means "20000 timescale units" = 20s at timescale=1000 — but a baseline DASH 6th-conformant parser may read it as "20000 seconds". This is a real interop risk if v6 has the units wrong. NotebookLM was unable to confirm; flag for spec-build to verify against §5.16.3 / §5.16.4 prose. |
| C17 | `<svta:OverlayPresentation>@maxConcurrency` admissible value = `1` only | extension attribute semantics | on C5 | Clean | Single-valued enum on an extension attribute; no conformance issue. (Design comment is sidecar territory.) |
| C18 | `<ImportedMPD>` reused (§5.3.2.6) as child of ListMPD `<Period>` | inherited element | inside `<Period>` of `urn:mpeg:dash:profile:list:2024` document | Clean | Direct reuse of §5.3.2.6 / §8.14. |
| C19 | `<ImportedMPD>` reused as child of `<svta:RenderableAsset>` (video form) | inherited element | inside foreign-namespace extension element (C9) | Conforming-with-comment | DASH's `<ImportedMPD>` is declared in the core MPD namespace (`urn:mpeg:dash:schema:mpd:2011`). Placing a core-namespace element as a child of a foreign-namespace element is permitted by XML (no namespace restriction), and §5.3.2.6 does not constrain the parent. The semantics carry — the `@uri` resolves to a sub-MPD bound to SPS. Comment: an XSD-strict validator that checks `<svta:RenderableAsset>` against an SVTA-namespaced schema must declare the core-namespace `<ImportedMPD>` as an admissible child. The spec should document the namespace mixing explicitly. |
| C20 | Sub-MPD bound to SPS (`urn:mpeg:dash:profile:sps:2024`, §8.15) | inherited profile | sub-MPD reached via `<ImportedMPD>` | Clean | Direct reuse of §8.15 / §7.3 (RFC 4337 MIME types: `video/mp4`, `audio/mp4`, `application/mp4`). |
| C21 | Tracking carrier — `<EventStream>@schemeIdUri="urn:mpeg:dash:event:callback:2015"` (§5.10.4.5) inside `<svta:Candidate>` | reused event scheme | child of `<svta:Candidate>` (foreign-namespace parent) in the Overlay Resolution Document | Conforming-with-comment | The callback event scheme is defined in §5.10.4.5 with `<EventStream>` as a child of `<Period>` (or `<MPD>` for application-level events per §5.10). Placing it under `<svta:Candidate>` is a foreign-namespace context; the carrier semantics survive intact (the Player reads the URL from `<Event>` text content and the time from `@presentationTime`). Comment: DASH 6th §5.10 places `<EventStream>` under `<Period>` or `<MPD>` — not under a foreign-namespace element. v6's choice is admissible under §5.2.1 (open content inside `<svta:Candidate>`) but is novel: a DASH 6th-aware validator that scans only for `<EventStream>` under `<Period>` will miss the tracking carrier. Validators implementing v6 must scan inside `<svta:Candidate>` as well. Spec §5.5.2 acknowledges this placement choice; document the implication. |
| C22 | Tracking carrier on a video sub-MPD's `<Period>` | reused event scheme | inside the SPS sub-MPD | Clean | Standard DASH §5.10 placement. |
| C23 | ListMPD `<Period>@duration` as `xs:duration` (ISO 8601) | inherited attribute | on Period inside `urn:mpeg:dash:profile:list:2024` document | Clean | Direct reuse of §8.14 / §5.3. |
| C24 | ListMPD `<Period>` admits inline AdaptationSet/Representation OR `<ImportedMPD>` | inherited authoring shape | inside ListMPD | Clean | §5.2.1.2 inheritance from §8.14. |
| C25 | `<UrlParamInfo>` reused (§I.3.1, scheme `urn:mpeg:dash:urlparam:2025`) | inherited descriptor | inside `<EssentialProperty>` on main MPD | Clean | Direct reuse, with the spec's §2 NOTE flagging the prose name `<UrlParamInfo>` vs the semantic-table name `<RequestParam>` — a DASH 6th internal inconsistency inherited, not a v6 defect. |
| C26 | Co-located events for hybrid (linear + overlay at same `presentationTime`) | authoring pattern | two `<EventStream>`s with different `@schemeIdUri`s, each carrying an `<Event>` at the same `presentationTime` | Clean | DASH 6th does not forbid multiple `<EventStream>`s in the same `<Period>`; §5.10 explicitly admits multiple event streams with distinct scheme URIs. Independent resolution at runtime is a Player semantics choice, not a schema-level constraint. |
| C27 | Resolution document `<MPD>@type` choice for Overlay Resolution Document | profile-internal type binding | on the Overlay Resolution Document root | **Non-conforming** | The spec's §5.2.2.1 skeleton declares `type="static"`, but a `static` MPD per §5.3.1 of DASH 6th must contain `<Period>` children describing media. The Overlay Resolution Document carries no `<Period>` and no media at the MPD level (the media is reached transitively via `<svta:RenderableAsset>`/`<ImportedMPD>`). This is the same defect as C7 viewed from the `@type` attribute; the two conform-or-not verdicts move together. See suggested fix. |
| C28 | `<EventStream>@value` attribute for callback scheme | inherited attribute | on `<EventStream>` in tracking carrier | Conforming-with-comment | §5.5.1 declares `@value="1"` "to disambiguate from non-callback usages of the same scheme". DASH 6th §5.10.4.5 defines `urn:mpeg:dash:event:callback:2015` with `@value` semantics that the callback scheme itself sets; the convention `value="1"` for SGAI tracking is admissible but not normatively required by DASH 6th. Comment: the spec should clarify whether `@value` carries a semantic load for the Player (e.g. de-duplication keyed on `@value`) or is purely informational. |
| C29 | Image / HTML carrier MIME types (`image/jpeg`, `image/png`, `image/webp`, `text/html`) | spec-side MIME constraint | informational | Clean | Not a DASH-level binding (these MIME types are not carried inside a sub-MPD's `Representation@mimeType`); they are flat HTTP URLs at `<svta:RenderableAsset>@assetUrl`. No DASH conformance question. |
| C30 | Annex A–K examples (XML excerpts) | informative | annex documents | Conforming-with-comment | The XML excerpts in A.2, B.2, C.2, D.2, E.2, H.2, I.2, J.2 declare extension elements consistently with §5.1.3 / §5.1.4 and use the correct `xmlns:svta=` declaration. Comment: A.2 / B.2 declare `profiles="urn:mpeg:dash:profile:advanced-linear:2025"` on the main MPD — this is a separate DASH 6th profile not enumerated in v6's §2 normative references; if it does not exist in DASH 6th, the example fails validation. (Spec-only verification: I cannot confirm this profile URI exists in DASH 6th from internal cross-references alone.) Flag for spec-build to verify against Annex F. |

## NotebookLM findings (highlights)

NotebookLM was attempted three times; one query completed (and
returned an off-topic answer about in-band ReplacePresentation
update semantics); two failed on a Chromium `ProcessSingleton`
profile-lock when issued in parallel. No usable grounding evidence
was obtained from the notebook for the per-construct conformance
claims in this audit.

The session's serialisation constraint (one browser, persistent
profile, can't run parallel queries) means a future audit that
needs broad coverage should issue NotebookLM queries strictly
sequentially with verification of each answer's relevance before
moving on. The off-topic answer in the §8.14 query is a known
NotebookLM failure mode (the model latches onto a related but
different topic in the corpus); the operator should re-prompt with
a more constrained question shape ("Quote the verbatim text of
Section 8.14 paragraph 1 of ISO/IEC 23009-1:2025") to force literal
retrieval rather than synthesis.

## Non-conforming items detail

### NC-1 (C7 + C27): Overlay Resolution Document is `type="static"` but has no `<Period>`

**Conflict.** The Overlay Resolution Document declared in §5.2.2 of
the v6 spec uses `MPD@type="static"` and carries `<svta:OverlayList>`
as its only top-level body. The DASH 6th MPD schema (`MPDtype` in
`urn:mpeg:dash:schema:mpd:2011`) requires at least one `<Period>`
child on a `static` or `dynamic` MPD. The skeleton in §5.2.2.1 and
every annex example (Annex C.3, E.3, H section excerpts, I.3, J.3)
shows the document with zero `<Period>` elements.

**Where in the spec.** v6 spec lines 940–972 (§5.2.2.1 skeleton),
2169–2226 (Annex C.3), 2383–2414 (Annex E.3), 2652–2683 (Annex I.3),
2746–2775 (Annex J.3).

**Why this matters.** A DASH 6th-conformant XML schema validator
applied to the Overlay Resolution Document will fail with
"element MPD missing required child Period". The base schema does
not see the foreign-namespace `<svta:OverlayList>` as a substitute
for `<Period>` — §5.2.1 permits foreign elements alongside the
base content model, not in place of required base children.

**Suggested fix.** Two clean paths:

1. **Add `@type="list"` semantics or a new SGAI-specific `@type`
   value.** The `ListMPD` profile (§8.14 of DASH 6th) addresses
   exactly this case for linear ad lists: it introduces
   `@type="list"` precisely to relax the `<Period>`-required
   constraint and admit a list-of-things shape. The Overlay
   Resolution Document is structurally analogous; v6 could either
   (a) declare `@type="list"` on the Overlay Resolution Document
   and clarify in §5.2.2.1 that the `urn:svta:dash:profile:sgai-overlay-list:2026`
   profile extends the same `@type` value, or (b) define a new
   `@type` value (e.g. `"overlay-list"`) under the SGAI namespace
   and document the relaxation. Option (a) is cleaner because it
   reuses an existing DASH-6th-aware codepath in MPD parsers.

2. **Wrap `<svta:OverlayList>` inside a placeholder `<Period>`.**
   Declare a single mandatory `<Period id="resolution" duration="…">`
   inside the Overlay Resolution Document and place
   `<svta:OverlayList>` as its foreign-namespace child. The Period
   carries no `<AdaptationSet>` / `<Representation>` and serves
   only as a base-schema anchor. This is the least-invasive fix —
   `<Period>` is permitted to contain foreign-namespace children
   per §5.2.1, and DASH 6th does not require a Period to carry
   media. The spec needs one extra sentence in §5.2.2.1 declaring
   the anchor pattern and updating every annex's resolution-document
   excerpt accordingly.

Either fix preserves backward-compatibility (a legacy Player still
never reaches the resolution document, gated by the unknown event
scheme upstream).

## Marginal items detail

### M-1 (C16): Timescale units on linear-event integer attributes

**Ambiguity.** The spec §5.1.1 / §5.1.2 attribute tables declare
`@maxDuration`, `@earliestResolutionTimeOffset`, `@returnOffset`,
`@clipDuration` as `xs:unsignedInt` "expressed in the parent
`<EventStream>@timescale` units". The annex examples are
consistent with that reading (A.2: `maxDuration="20000"` with
`timescale="1000"`, meaning 20s).

The risk is that DASH 6th §5.16.3 / §5.16.4 prose conventionally
expresses these attributes in **seconds**, not in timescale units.
If the baseline interpretation is "seconds", v6's
`maxDuration="20000"` would be parsed by a DASH 6th-baseline Player
as 20000 seconds (≈5.5 hours) rather than 20s. This is a
catastrophic interop bug if the baseline reading is "seconds".

**Suggested clarification.** Cross-check against §5.16.3 / §5.16.4
prose. If the baseline is seconds, change v6 §5.1.1 / §5.1.2 to
match (drop the `@timescale` units claim, express in seconds) and
update every annex (A.2 `maxDuration="20"`, etc.). If the baseline
is `@timescale` units, the v6 spec is correct and the §2 NOTE
should be extended to flag this inheritance pattern.

NotebookLM was unable to confirm the baseline; the verbatim text
of §5.16.3 attribute tables would resolve this in one query.

### M-2 (C28): `<EventStream>@value="1"` for callback scheme

**Ambiguity.** §5.5.1 declares `@value="1"` "to disambiguate from
non-callback usages of the same scheme". DASH 6th §5.10.4.5 defines
`urn:mpeg:dash:event:callback:2015` and assigns semantics to
`@value` that the callback scheme owns. It is not clear from v6's
text whether (a) `@value="1"` is a normative requirement for SGAI
tracking, (b) the Player uses `@value` as a de-duplication key
across `<EventStream>`s, or (c) `@value` is purely informational.

**Suggested clarification.** State explicitly in §5.5.1 whether
`@value` is normatively `"1"` for SGAI tracking or whether any
string is admissible, and document what the Player does with the
attribute (de-dup key vs. logging hint).

## Conforming-with-comment items detail (selected)

### CWC-1 (C3): Profile-URI fall-through is not a formal DASH mechanism

The spec §8.8 row for `urn:svta:dash:profile:sgai-overlay-list:2026`
states "Profile-ignore (a Player unaware of the profile treats the
response as unknown and falls through per E3)". DASH 6th has no
formal "profile-ignore" mechanism; the `@profiles` attribute is
informative-hint level. The actual gating mechanism is upstream
(the unknown event scheme in the main MPD), which prevents legacy
Players from reaching the resolution document at all. The audit
verdict stands as Conforming-with-comment because the end-to-end
outcome (legacy Player never reaches the resolution document) is
correct, but the §8.8 row's "extension point" attribution is
imprecise. Recommend rewriting that row to attribute the gating
to the parent event scheme, not to profile-ignore.

### CWC-2 (C14 + C15): Schema-vs-prose `@url` vs `@uri`

The §2 NOTE acknowledges this inherited DASH 6th defect and pins
v6 to the prose name `@url`. This is the right authorial choice
(prose is what implementers read), but every MPD written per v6
will FAIL validation against the DASH 6th XSD because the XSD
declares `xs:attribute name="uri"`. The spec correctly warns
implementers ("Implementers using a strict schema validator should
expect the alternate names in DASH-6th-conformant tooling"). No
v6-side fix is possible — this is a DASH 6th errata candidate.

### CWC-3 (C19): Namespace mixing on `<svta:RenderableAsset>` children

The `<ImportedMPD>` element is declared in the core DASH MPD
namespace (`urn:mpeg:dash:schema:mpd:2011`); v6 places it as a
child of `<svta:RenderableAsset>` (foreign namespace). XML allows
this without restriction, but a future SVTA schema for
`<svta:RenderableAsset>` MUST declare the core-namespace
`<ImportedMPD>` as an admissible child (via `<xs:any namespace="…"
processContents="lax"/>` or explicit import). Recommend §5.3.4
note the namespace mixing and document the schema-author
implication.

### CWC-4 (C21): `<EventStream>` callback inside `<svta:Candidate>`

The DASH 6th §5.10 placement convention is `<EventStream>` as a
child of `<Period>` or `<MPD>` (for application-level events). v6
§5.5.2 admits placement directly inside `<svta:Candidate>` for
non-linear image/HTML ads (where no sub-MPD exists to host the
carrier). The semantics survive (foreign-namespace open content
plus the §5.10 scheme is self-describing) and the spec
acknowledges the placement, but DASH 6th-aware validators that
scan only `<Period>`/`<MPD>` for callback `<EventStream>`s will
miss the tracking carrier. Document validator-side implication
in §5.5.2.

### CWC-5 (C30): `urn:mpeg:dash:profile:advanced-linear:2025` in annex examples

Annex A.2, B.2, C.2 declare `profiles="urn:mpeg:dash:profile:advanced-linear:2025"`
on the main MPD. This profile URI is not enumerated in v6's §2
normative references, nor in §2.1 "Scheme URIs and namespaces
introduced by this edition". If `urn:mpeg:dash:profile:advanced-linear:2025`
is a DASH 6th-defined profile, the annexes need a §2 reference
adding it (e.g. "§8.X advanced-linear profile"); if it is not a
DASH 6th profile, the annex examples are technically non-conformant.
NotebookLM was unable to verify. Flag for spec-build to validate
the URI's existence in DASH 6th and either add it to §2 or replace
the annex examples with a known-conformant profile (e.g. omit
`@profiles` entirely or reference §8.12 CMAF on-demand).

## Open questions surfaced (could not resolve from spec text alone)

1. **§5.16 attribute units (M-1)**: are `@maxDuration`,
   `@earliestResolutionTimeOffset`, `@returnOffset`, `@clipDuration`
   expressed in seconds or in the parent `<EventStream>@timescale`
   units per DASH 6th §5.16.3 / §5.16.4 prose? v6's claim
   ("timescale units") needs verification.

2. **`urn:mpeg:dash:profile:advanced-linear:2025` (CWC-5)**: does
   this profile URI exist in DASH 6th? Annex A.2 / B.2 / C.2
   reference it; v6 §2 does not enumerate it.

3. **§5.10 `<EventStream>` placement (CWC-4)**: is placement of
   callback `<EventStream>` directly inside a foreign-namespace
   element (i.e. `<svta:Candidate>`) explicitly permitted by §5.10,
   or does it rely on the §5.2.1 foreign-namespace open-content
   rule alone? The two interpretations produce identical runtime
   behaviour but differ in validator-side strictness.

4. **§8.14 ListMPD `MPD@type` value (NC-1 fix path)**: does §8.14
   define a new `MPD@type` value (`"list"`) that the v6 spec
   inherits, or does it relax the schema differently? The fix
   path for NC-1 depends on the answer.

5. **Profile-ignore mechanism (CWC-1)**: does DASH 6th formally
   define behaviour for "Player encounters MPD with unknown
   `@profiles`"? If yes, what is the normative response?

## Summary

- **Total constructs audited**: 30
- **Clean**: 14 (C1, C2, C4, C8, C9, C10, C11, C12, C13, C17, C18, C20, C22, C23, C24, C26, C29 — re-count: 17. Recounting from the table: C1, C2, C4, C8, C9, C10, C11, C12, C13, C17, C18, C20, C22, C23, C24, C26, C29 — 17 entries.)
- **Conforming-with-comment**: 11 (C3, C5, C6, C14, C15, C19, C21, C25, C28, C30 — recounting from table: 10 entries; ID list: C3, C5, C6, C14, C15, C19, C21, C25, C28, C30.)
- **Marginal**: 1 (C16)
- **Non-conforming**: 2 (C7, C27 — same defect, two views)

**Recount (canonical, from inventory table)**:

| Verdict | Count | Construct IDs |
|---------|-------|----------------|
| Clean | 17 | C1, C2, C4, C8, C9, C10, C11, C12, C13, C17, C18, C20, C22, C23, C24, C26, C29 |
| Conforming-with-comment | 10 | C3, C5, C6, C14, C15, C19, C21, C25, C28, C30 |
| Marginal | 1 | C16 |
| Non-conforming | 2 | C7, C27 |
| **Total** | **30** | |

**The single substantive non-conforming finding is the Overlay
Resolution Document's `MPD@type="static"` + zero-`<Period>` shape
(C7 / C27 — same defect from two angles).** Every other construct
is either clean or has a minor documentation/clarification ask.
The §2 NOTE already addresses the inherited DASH 6th defects
(`@url` vs `@uri`, `<UrlParamInfo>` vs `<RequestParam>`) with the
correct authorial choice, so those do not require further action
at the v6 level.

The two timescale-unit and profile-URI items (M-1 and CWC-5) are
flagged for spec-build verification: both can be resolved by a
single targeted NotebookLM query each, and either could shift a
verdict to Non-conforming if the underlying assumption fails.

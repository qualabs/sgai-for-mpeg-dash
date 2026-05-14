[GROUNDED_BY=notebooklm]

# DASH conformance audit — 2026-05-14

**Audit target**: `../output/2026-05-14-sgai-spec.md` (post-detail-review build).
**Reference**: MPEG-DASH 6th edition (ISO/IEC 23009-1:2025).
**Method**: inventory of every construct introduced or modified by the
spec, four grounded queries against the "Streaming Protocols — DASH,
HLS, C2PA, DRM" notebook in NotebookLM (DASH-6th FDIS loaded), and a
per-construct verdict (Conforming / Marginal / Non-conforming) against
each cited DASH rule. The audit is independent of the spec-build
agent and the validate-spec sidecar (`2026-05-14-spec-validation.md`).

## Scope

In scope: every new scheme URI, new XML element, new attribute on a
new or baseline element, new profile-URI usage, new structural
arrangement of baseline elements, and re-use of inherited baseline
constructs. Annexes A through G are audited as concrete instances
of the chapter 5 constructs.

Out of scope: design-level concerns already raised in the
validate-spec sidecar (use-case coverage, ambiguity, missing rules).
This audit only asks: *given the spec's wording, would a
DASH-6th-conformant parser process the construct as the spec intends,
or would the DASH rules reject it / interpret it differently?*

## Method summary

- Inventory built from §2, §3.2, §5.1.1–5.1.5, §5.2.1, §5.2.2, §5.3,
  §5.4, §5.5, §5.6, §5.7, §7.6, and annexes A through G of
  `2026-05-14-sgai-spec.md`.
- 4 NotebookLM queries against the active notebook covering: (a)
  §5.2.1 / §5.10.1 / §5.10.3.3.1 extension and ignore-if-unknown
  rules; (b) §8.14 ListMPD and §8.15 SPS profile constraints; (c)
  §5.16 Alternative MPD events / §5.3.2.6 ImportedMPD / §5.10.4.5
  callback scheme; (d) §8.14 stricter ListMPD rules, §8.15 SPS
  prohibitions, §I.4 `UrlParamInfo` descriptor (2025), `advanced-linear`
  profile, and `@maxDuration` units. All 4 queries completed; 0
  `[fetch-failed]`.
- Each construct is assessed against the cited rule with a verdict.

## Inventory + verdicts

Legend: V = Conforming (verified against a DASH-6th cite);
M = Marginal (ambiguous, inherits a DASH-6th ambiguity, or needs an
explicit clarification); N = Non-conforming (violates a DASH-6th rule
as written).

| ID | Construct | Type | Placement | Verdict | Rationale |
|----|-----------|------|-----------|---------|-----------|
| C-01 | `urn:svta:dash:sgai:2026` | New XML namespace | Used on every SVTA element | V | §5.2.1 — foreign-namespace open content is the canonical extension point on `MPDType`, `PeriodType`, `EventType`, `AdaptationSetType` (`xs:any namespace="##other" processContents="lax"`). |
| C-02 | `urn:svta:dash:sgai-overlay:2026` | New `EventStream@schemeIdUri` | Main MPD `<EventStream>` | V | §5.10.1 — unknown `EventStream` schemes are subscribed-to-or-ignored. New vendor URI is the canonical extension path. |
| C-03 | `urn:svta:dash:sgai-pause-trigger:2026` | New `EventStream@schemeIdUri` | Main MPD `<EventStream>` | V | Same as C-02. |
| C-04 | `urn:svta:dash:sgai-layout:2026` | New "scheme prefix" URI | Declared in §2 and §3.2 | M | URI declared in §2 normative-references table as "scheme prefix for the IAB-derived layout vocabulary (§3.2)" but is **never used as a `@schemeIdUri` anywhere in the spec body** (layout values appear as bare `@name` tokens on `<svta:Layout>` and as `@layout` on `<svta:RenderableAsset>`). Dead reference; either delete from §2 or document where it should appear. |
| C-05 | `urn:svta:dash:profile:sgai-overlay-list:2026` | New `MPD@profiles` value | Resolution-document `MPD@profiles` | V (semantics) | §8.14 — vendor profile URIs may coexist alongside the ListMPD URI in `@profiles`; §8.1 defines `@profiles` as comma-separated. Spec does not pin a delimiter for the multi-URI case (see M-5). |
| C-06 | `<svta:OverlayPresentation>` | New element | Child of `<Event>` (in svta-scheme `<EventStream>`) | V | §5.2.1 — `EventType` carries `xs:any namespace="##other" processContents="lax"`; foreign-namespace children of `<Event>` are valid extension points. |
| C-07 | `<svta:PauseAdTrigger>` | New element | Child of `<Event>` (in svta-scheme `<EventStream>`) | V | Same as C-06. |
| C-08 | `<svta:AllowedLayouts>` / `<svta:Layout>` | New elements | Children of `<svta:OverlayPresentation>` / `<svta:PauseAdTrigger>` | V | Internal to svta-namespace subtree; opaque to baseline parsers by §5.2.1 NOTE 2 (foreign-namespace discard). |
| C-09 | `<svta:Concurrency>` | New element | Child of `<svta:OverlayPresentation>` / `<svta:PauseAdTrigger>` | V | Same as C-08. |
| C-10 | `<svta:Exclusions>` / `<svta:Pair>` | New elements | Children of `<svta:OverlayPresentation>` / `<svta:PauseAdTrigger>` | V | Same as C-08. |
| C-11 | `<svta:RenderableAsset>` | New element | Child of `<Period>` in §5.2.2 resolution document | V | §5.2.1 — `PeriodType` permits foreign-namespace children directly without nesting (NotebookLM Q4 confirms regular Periods natively accept `##other` children via the `xs:any` wildcard). |
| C-12 | `<svta:Metadata>` (and children `<svta:Click>`, `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:UniversalAdId>`) | New elements | Children of `<Period>` in resolution doc or sub-MPD | V | Same as C-11; `<svta:Metadata>` is the application-level open-content carrier. §5.6.5 of the spec correctly invokes §5.2.1 NOTE 2 for legacy discard semantics. |
| C-13 | `@url`, `@maxDuration`, `@earliestResolutionTimeOffset` on `<svta:OverlayPresentation>` / `<svta:PauseAdTrigger>` | New attributes on new elements | N/A (whole element is svta) | V | Foreign-namespace attributes on a foreign-namespace element are not bound by any baseline schema. Spec restates `@maxDuration` enforcement consistent with §5.16.5 (P-5). Unit choice for `@earliestResolutionTimeOffset` is "seconds" — see M-3. |
| C-14 | `@src`, `@mediaType`, `@layout`, `@priority`, `@width`, `@height`, `@duration` on `<svta:RenderableAsset>` | New attributes on new element | N/A | V | Same as C-13. |
| C-15 | `@name` on `<svta:Layout>`; `@max` on `<svta:Concurrency>`; `@a` / `@b` on `<svta:Pair>`; `@uri` / `@trackingUri` on `<svta:Click>`; `@idRegistry` / `@idValue` on `<svta:UniversalAdId>` | New attributes on new elements | N/A | V | Same as C-13. |
| C-16 | `<InsertPresentation>` re-used from §5.16.3 | Baseline element used as-is | Child of `<Event>` (linear-scheme `<EventStream>`) | M (M-1) | §5.16.3 confirmed. NotebookLM Q3 flagged a DASH-6th internal discrepancy: the SCHEMA registers the URL attribute as `@uri` while the SEMANTIC table (Table 62) names it `@url`. Spec follows the semantic table (`url="…"`) — a strict schema validator would reject. Issue is inherited from DASH-6th, but spec authors should be aware. |
| C-17 | `<ReplacePresentation>` re-used from §5.16.4 | Baseline element used as-is | Child of `<Event>` (linear-scheme `<EventStream>`) | M (M-1) | Same `@url` vs `@uri` schema/semantic split as C-16. Other ReplacePresentation attributes are aligned: spec uses `@clipDuration` (schema name) correctly per NotebookLM Q3 (semantic table calls it `@clip` — schema is `@clipDuration`); `@returnOffset` and `@startWithOffset` match the schema. |
| C-18 | `<ImportedMPD uri="…" earliestResolutionTimeOffset="…">` re-used from §5.3.2.6 | Baseline element used as-is | Direct child of `<Period>` in §5.2.1 / §5.2.2 resolution documents | V | NotebookLM Q3 confirmed `@uri` is the canonical schema name (and the spec uses `uri=` consistently in Annexes A, B, C, E, F). `@earliestResolutionTimeOffset` default is 60 seconds; spec values (0 / 30 / 60) are interpreted as seconds. |
| C-19 | `urn:mpeg:dash:event:callback:2015` re-used for tracking inside sub-MPD `<Period>` (linear case, §5.5.2) | Baseline scheme used as-is | `<EventStream>` child of sub-MPD `<Period>` | V | §5.10.4.5 confirmed by NotebookLM Q3. EventStream-with-callback-scheme placement is Period-level only (no MPD-level, no AdaptationSet-level host); spec respects this. |
| C-20 | `urn:mpeg:dash:event:callback:2015` re-used inside `<svta:Metadata>` (§5.5.3 case (b)) | Baseline scheme nested inside svta subtree | `<EventStream>` inside `<svta:Metadata>` | V | Equivalent on the wire to a Period-level EventStream from an SGAI-aware parser perspective; opaque to legacy parsers per §5.2.1 NOTE 2 discard semantics. Spec correctly flags this opacity in §5.6.5. |
| C-21 | `urn:mpeg:dash:event:callback:2015` re-used as direct child of resolution-doc `<Period>` (§5.5.3 case (a)) | Baseline scheme on a resolution-doc Period | `<EventStream>` child of resolution-doc `<Period>` (no `<ImportedMPD>`, no `<AdaptationSet>`) | N (part of N-2) | EventStream placement itself is conformant (`PeriodType` schema position). BUT the Period's overall shape — non-zero `Period@duration`, no `<ImportedMPD>`, no `<AdaptationSet>` — violates §5.3.2.2 Table 4 (see N-2). |
| C-22 | Callback `Event@presentationTime` measured against the Broadcaster-declared overlay window for non-linear ads (§5.5.4, §7.5) | New tracking-time-base semantics on a baseline scheme | Per-form sub-MPD or `<svta:Metadata>` callback `<Event>` | M (M-2) | NotebookLM Q3 confirmed `Event@presentationTime` is "relative to the start of the Period". Spec §5.5.4 normatively assigns the time-base remap to the ADS — but does **not** explicitly require the sub-MPD's `Period@duration` to equal the slot's `@maxDuration`. If the ADS sets `Period@duration` = asset duration (not slot window), the §5.10.4.5 firing rule mis-aligns. Carry-over from old M-2; partially resolved (ADS now owns the remap) but underlying invariant still implicit. |
| C-23 | `urn:mpeg:dash:profile:list:2024` (ListMPD) re-used for linear baseline (§5.2.1) | Baseline profile, used as-is | Resolution-document `MPD@profiles` | V | §8.14 confirmed. ListMPD profile reused verbatim; `MPD@type="list"` correctly set in Annex A.3 / B.3 / F.3. |
| C-24 | `urn:mpeg:dash:profile:sps:2024` (SPS) re-used for video-only sub-MPDs (§5.4) | Baseline profile, used as-is | Sub-MPD `MPD@profiles` | V | §8.15 confirmed. Spec §5.4 correctly constrains `Representation@mimeType` to the IETF RFC 4337 registry (`video/mp4`, `audio/mp4`, `application/mp4`) and forbids non-MP4 wrappers. Old N-1 / N-2 (HTML / image in SPS sub-MPD) are **resolved** because non-video forms are now carried via `<svta:RenderableAsset>` foreign-namespace open content rather than via `<AdaptationSet mimeType="text/html"\|"image/png">` inside a sub-MPD. |
| C-25 | `MPD@type="list"` + `urn:mpeg:dash:profile:list:2024` on the resolution document | Baseline ListMPD constraints re-applied | Resolution-document root | V | NotebookLM Q4 confirmed `MPD@type="list"` is mandatory for ListMPD, and §8.14 forbids Alternative MPD events / XLink inside the ListMPD's own MPD element. Spec is silent on Alternative MPD events in resolution docs; no annex example violates this. |
| C-26 | `MPD@type="static"` + `urn:mpeg:dash:profile:sps:2024` + exactly one `<Period>` per sub-MPD | Baseline SPS constraints re-applied | Sub-MPD root | V | NotebookLM Q4 confirmed `MPD@type="static"` and "one and only one Period element shall be present" for SPS. Annexes A.4, B.4, C.4 all comply. |
| C-27 | `<EventStream schemeIdUri="urn:svta:dash:sgai-overlay:2026">` and `<…sgai-pause-trigger:2026">` placed in the Broadcaster's primary MPD | Re-use of `<EventStream>` element with a new scheme | Child of primary-MPD `<Period>` | V | §5.10.2.1 confirmed by NotebookLM Q3 — MPD events are placed Period-level only. Primary MPD is not bound by the ListMPD / SPS profile constraints. |
| C-28 | Co-located linear + non-linear events in the same `<Period>` (§5.1.5) | Multiple `<EventStream>` elements in one Period | Children of primary-MPD `<Period>` | V | DASH 6th does not cap the number of `<EventStream>` children of `<Period>`; each is keyed independently by `@schemeIdUri` per §5.10.1. Independent activation per spec §7.6. |
| C-29 | `<up:UrlParamInfo xmlns:up="urn:mpeg:dash:schema:urlparam:2025">` (Annex A.2) | Reuse of §I.4 descriptor with the 2025 scheme | Inside `<EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025">` of primary MPD | N (N-1) | NotebookLM Q4 confirmed: the §I.4 **2025** scheme natively integrates `UrlParamInfo` into the core MPD namespace (`urn:mpeg:dash:schema:mpd:2011`) — unlike the legacy 2014 / 2016 schemes that required an external `up:` namespace. Annex A.2 mixes the new (2025) scheme URI with the OLD (2016) namespacing pattern. See N-1 below. |
| C-30 | `<EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025">` as the descriptor host (Annex A.2) | Reuse of §I.4 descriptor pattern | Primary MPD root | M (M-4) | NotebookLM Q4 confirmed `urn:mpeg:dash:urlparam:2025` is the §I.4 scheme URI. NotebookLM also said in the 2025 scheme `UrlParamInfo` is now a native MPD-namespace element; whether wrapping it in `<EssentialProperty>` is still required or whether direct inclusion under `<MPD>` / `<Period>` / `<AdaptationSet>` / `<Preselection>` / `<EventStream>` is now the canonical pattern is not explicitly resolved by the audit query — spec authors should re-check §I.4 directly. |
| C-31 | `@includeInRequests="altmpd"` (Annex A.2) | Reuse of §I.4 attribute | `<UrlParamInfo>` attribute | V | NotebookLM Q4 confirmed `altmpd` is a defined key in §I.3.6 Table I.4 ("all requests for MPDs representing the alternative Media Presentation, as defined in clause 5.16"). |
| C-32 | `urn:mpeg:dash:profile:advanced-linear:2025` on the primary MPD (Annex A.2) | Reuse of §8.13 baseline profile | `MPD@profiles` of primary MPD | V | NotebookLM Q4 confirmed this URI is a defined DASH-6th profile URI (§8.13, "ISO Base Media File Format Advanced Linear"). Old audit's OQ-1 resolved. |
| C-33 | Resolution-document `<Period>` with `<ImportedMPD>` + zero or more `<svta:RenderableAsset>` + optional `<svta:Metadata>`, no `<AdaptationSet>` (Annex C cand_1, E.3) | Linked Period inside §5.2.2 resolution document | §5.2.2 resolution doc | V | §8.14 NotebookLM Q4 explicitly permits Linked Periods (Periods that use `<ImportedMPD>`) in ListMPD-style documents; an `<AdaptationSet>` is NOT required when `<ImportedMPD>` is present. Foreign-namespace siblings (`<svta:RenderableAsset>`, `<svta:Metadata>`) are permitted by §5.2.1 `xs:any`. |
| C-34 | Resolution-document `<Period>` with only `<svta:RenderableAsset>` (no `<ImportedMPD>`, no `<AdaptationSet>`), non-zero `Period@duration` (Annex C cand_2) | Regular Period inside §5.2.2 resolution document, image-only candidate | §5.2.2 resolution doc | N (N-2) | NotebookLM Q2 confirmed §5.3.2.2 Table 4: "At least one Adaptation Set shall be present in each Period unless the value of the `@duration` attribute of the Period is set to zero." Annex C cand_2 has `Period@duration="PT30S"`, no `<ImportedMPD>`, no `<AdaptationSet>` — direct violation. Spec's §5.5.3 case (a) claims the new profile "relaxes" this requirement, which exceeds the spec's authority (vendor profiles may restrict, not relax, baseline schema constraints). See N-2. |
| C-35 | `Period@duration` reused with extended semantics on non-linear candidates (§5.2.2: "REUSED VERBATIM from baseline DASH") | Reuse of baseline `Period@duration` | §5.2.2 resolution-doc `<Period>` | V | Reuse is conformant in name and type (`xs:duration`). Spec correctly invokes naming-consistency for the inherited identifier. The interplay with §5.3.2.2 Table 4 still binds; see N-2 / C-34. |

## NotebookLM findings (highlights)

- **Q1 (§5.2.1 / §5.10.1 / §5.10.3.3.1 — extension and ignore-if-unknown rules)**: confirmed. `MPDType`, `PeriodType`, `AdaptationSetType`, `EventType` all carry `xs:any namespace="##other" processContents="lax"`. DASH clients subscribe only to known `EventStream` schemes and ignore unknown ones; emsg with unknown scheme MUST be ignored.
- **Q2 (§8.14 ListMPD + §8.15 SPS)**: confirmed. `MPD@profiles` is comma-separated (§8.1); vendor URIs may coexist alongside ListMPD URI. ListMPD may contain Linked Periods (with `<ImportedMPD>`) and regular Periods; regular Periods still bind to §5.3.2.2 Table 4 — **at least one `<AdaptationSet>` shall be present unless `Period@duration` is set to zero**. SPS profile (§8.15) inherits §7.3 → IETF RFC 4337 mimeType restriction (`video/mp4`, `audio/mp4`, `application/mp4`); HTML / image cannot be Representation `@mimeType` values.
- **Q3 (§5.16 / §5.3.2.6 / §5.10.4.5)**: confirmed scheme URIs `urn:mpeg:dash:event:alternativeMPD:insert:2025`, `urn:mpeg:dash:event:alternativeMPD:replace:2025`, `urn:mpeg:dash:event:callback:2015`. **Schema/semantic-table discrepancy**: DASH-6th schema names the AlternativeMPD URL attribute `@uri`; the semantic table (Table 62) names it `@url`. Same divergence on `@clipDuration` (schema) vs `@clip` (semantic). `@maxDuration` is "in units of `EventStream@timescale`"; §5.16.5 mandates termination at the boundary. `<ImportedMPD>` canonical schema name is `@uri`; only other attribute is `@earliestResolutionTimeOffset` (default 60 seconds, schema location: child of `PeriodType` exclusively). Callback `Event@presentationTime` is relative to Period start of the containing `<EventStream>`'s Period.
- **Q4 (§8.14 / §8.15 stricter checks + §I.4 / advanced-linear)**: confirmed. ListMPD `MPD@type` MUST be `"list"`; Alternative MPD events and XLink are forbidden inside the ListMPD's own MPD; foreign-namespace children allowed in a regular Period directly. SPS profile MUST set `MPD@type="static"` and contain exactly one Period; Alternative MPD events not explicitly prohibited inside SPS sub-MPD. **§I.4 (2025) UrlParamInfo descriptor**: scheme URI `urn:mpeg:dash:urlparam:2025`. **Critically, the 2025 scheme natively integrates `UrlParamInfo` into the core MPD namespace (`urn:mpeg:dash:schema:mpd:2011`)** — unlike the legacy 2014 / 2016 schemes which required an external `up:` namespace prefix. `@includeInRequests` keys are whitespace-concatenated; `altmpd` is a defined key. `urn:mpeg:dash:profile:advanced-linear:2025` is a defined DASH-6th profile URI (§8.13).

## Non-conforming items detail

### N-1: `<up:UrlParamInfo xmlns:up="urn:mpeg:dash:schema:urlparam:2025">` in Annex A.2 (C-29)

**Conflict**: §I.4 of DASH 6th edition (per NotebookLM Q4) is explicit
that the **2025** `UrlParamInfo` descriptor scheme integrates the
element natively into the core MPD namespace
(`urn:mpeg:dash:schema:mpd:2011`). The legacy `up:` external namespace
(`urn:mpeg:dash:schema:urlparam:2016`) belongs to the older 2014 /
2016 schemes. Annex A.2 of the spec uses the **new scheme URI**
(`urn:mpeg:dash:urlparam:2025`) together with the **old namespace
pattern** (`xmlns:up="urn:mpeg:dash:schema:urlparam:2025"` and
`<up:UrlParamInfo …/>`). This combination is not what DASH 6th
prescribes. A strict 2025-aware parser would either (a) reject the
`up:UrlParamInfo` element because it sits in a non-MPD namespace that
DASH 6th does not define, or (b) treat it as foreign-namespace open
content and discard it under §5.2.1 NOTE 2 — defeating the purpose
of declaring the descriptor.

Additionally, the spec's §2 normative-references table lists
`urn:mpeg:dash:schema:urlparam:2025` as the "XML namespace for the
§I.4 UrlParamInfo descriptor", which is the inverse of the DASH-6th
2025 rule (no separate namespace; the element lives in the MPD
namespace).

**Suggested fix**: rewrite the Annex A.2 sample so the descriptor is
either (a) emitted as `<UrlParamInfo …/>` in the MPD namespace
directly under `<MPD>`, `<Period>`, `<AdaptationSet>`,
`<Preselection>`, or `<EventStream>` (whichever scope applies),
matching the §I.4 2025 wording, or (b) the spec consults §I.4
directly and pins the exact 2025 pattern verbatim. Update the §2
normative-references table to remove
`urn:mpeg:dash:schema:urlparam:2025` (since DASH 6th does not define
it as an XML namespace under the 2025 scheme).

### N-2: Image-only / non-video-only resolution-document `<Period>` with no `<ImportedMPD>` and no `<AdaptationSet>` (C-21, C-34)

**Conflict**: §5.3.2.2 Table 4 (per NotebookLM Q2): "At least one
Adaptation Set shall be present in each Period unless the value of
the `@duration` attribute of the Period is set to zero." §8.14
ListMPD admits two Period flavours: **Linked Periods** (which carry
`<ImportedMPD>` and therefore do not need an `<AdaptationSet>`) and
**regular Periods** (which still bind to §5.3.2.2 Table 4).

The spec authors a regular Period in two distinct annexed shapes:

- Annex C.3 candidate `cand_2` carries `<Period id="cand_2"
  duration="PT30S">` with **only** `<svta:RenderableAsset
  mediaType="image/jpeg" …/>` and `<svta:Metadata>` as children. No
  `<ImportedMPD>`. No `<AdaptationSet>`. `Period@duration` is
  non-zero. This violates §5.3.2.2 Table 4.
- §5.5.3 case (a) describes a non-video tracking carrier pattern in
  which the Period hosts only a callback `<EventStream>` and one or
  more `<svta:RenderableAsset>` children — again with no
  `<AdaptationSet>` and non-zero `Period@duration`. Spec text
  attempts to license this with: "an `<AdaptationSet>` MUST NOT be
  required by the resolution-document profile because the §5.3.2.2
  Table 4 constraint is bound to baseline-DASH Periods; the
  overlay-aware profile (§5.2.2) relaxes the AdaptationSet
  requirement for this carrier explicitly."

The relaxation claim is non-conformant in principle. A vendor profile
identifier in `MPD@profiles` declares **additional constraints**
beyond the baseline; it cannot lift a baseline schema constraint that
is normatively pinned in `PeriodType` (Table 4). The §5.3.2.2 Table 4
rule applies to every `<Period>` element produced under any DASH
profile unless `Period@duration=0`.

**Suggested fix**: choose one of three remedies, each a real change
to the spec:

1. **Require a minimal `<ImportedMPD>` for every non-video-only
   candidate.** The ADS emits a tiny SPS sub-MPD that wraps the
   callback `<EventStream>` (and an `application/mp4`
   single-sample tracker `<AdaptationSet>` if needed to satisfy
   SPS). The resolution-doc Period is then a Linked Period and the
   AdaptationSet requirement no longer applies. This is the
   sub-MPD-tracking-sidecar pattern §5.5.2 already prescribes for
   linear — generalising it removes N-2 without ceding ground to a
   "profile-relaxes-base-schema" position.
2. **Embed `<AdaptationSet>` with a benign `mimeType` that does not
   imply a Representation MUST stream.** §7.3 / RFC 4337 still
   binds, so the AdaptationSet must carry `application/mp4` (or
   equivalent) — same outcome as remedy 1 with a different
   syntactic shape.
3. **Set `Period@duration="PT0S"`** for non-video-only candidates,
   exploiting the Table 4 exception. The slot-window arithmetic
   then needs a different carrier (e.g., a separate attribute on
   `<svta:RenderableAsset>`), since `Period@duration` is the spec's
   current cap-arithmetic input. Higher cost than remedies 1–2.

Either way, **the §5.5.3 case (a) "relaxes the AdaptationSet
requirement" language must be removed**; the spec cannot license
something the baseline forbids.

## Marginal items detail

### M-1: `@url` vs `@uri` on `<InsertPresentation>` / `<ReplacePresentation>` (C-16, C-17)

**Ambiguity**: NotebookLM Q3 found an internal DASH-6th split:
schema definition for `AlternativeMPDEventType` registers the URL
attribute as `@uri`; the semantic table (Table 62) names it `@url`.
DASH 6th itself is inconsistent. The SGAI spec follows the semantic
table (`url="…"` throughout §5.1.1, §5.1.2, Annexes A.2 / B.2 / D.2 /
F.2). A strict schema validator on a 2025 DASH manifest would reject
`<InsertPresentation url="…"/>` and expect `<InsertPresentation uri="…"/>`.

**Suggested clarification**: either (a) emit both forms — the
schema-named `@uri` plus an editorial note acknowledging the Table 62
prose form — or (b) align with the schema (`@uri`) and add a NOTE in
§5.1.1 / §5.1.2 stating that the Table-62 semantic-table prose names
the attribute `@url` informally. Spec authors should also flag this
DASH-6th inconsistency back to the MPEG-DASH editor (out of scope for
this audit, but a real ecosystem hazard).

### M-2: Callback `Event@presentationTime` time base for non-linear ads (C-22)

**Ambiguity**: §5.10.4.5 (per NotebookLM Q3) measures
`Event@presentationTime` relative to the start of the containing
`<EventStream>`'s `<Period>`. Spec §5.5.4 says non-linear tracking
beacons are "interpreted against the Broadcaster-declared overlay
window" and assigns the time-base remap to the ADS. The remap holds
if and only if the per-form sub-MPD's `Period@duration` equals the
parent slot's `@maxDuration` (the overlay window) — but the spec
does **not** explicitly pin this invariant. If an ADS sets
`Period@duration` = the asset's intrinsic duration (a natural
choice), beacons placed at slot-window quartiles fire at incorrect
internal-clock positions.

**Suggested clarification**: in §5.5.4 (after the existing NOTE),
add: "For non-linear ads, the per-form sub-MPD's `Period@duration`
MUST equal the parent slot's `@maxDuration` (the Broadcaster-declared
overlay window) regardless of the asset's intrinsic duration. The
ADS is the construct's author and is therefore the only actor able
to enforce this invariant."

### M-3: `@earliestResolutionTimeOffset` unit reading (C-13, C-18)

**Ambiguity inherited from DASH-6th**: NotebookLM Q3 surfaced that
the §5.16 semantic table prose says "in units of timescale" while
the schema declares `xs:double` with default `60.0` (interpretable
as seconds). The SGAI spec consistently states "seconds" on both
`<svta:OverlayPresentation>` / `<svta:PauseAdTrigger>` (NEW elements,
§5.1.3 / §5.1.4) and `<ImportedMPD>` (baseline, §5.3.2.6). This is
self-consistent and pragmatically defensible — but it diverges from
the DASH-6th semantic-table prose. Implementers reading DASH-6th
verbatim may default to `EventStream@timescale` units. Old audit's
M-3 (unit collision between the svta element and `<ImportedMPD>`) is
resolved; this is a different, inherited issue.

**Suggested clarification**: add a non-normative NOTE in §5.1.3
flagging the DASH-6th-source ambiguity and stating that this spec
resolves to seconds for both `<svta:OverlayPresentation>` and
`<svta:PauseAdTrigger>` to match the schema default of
`<ImportedMPD @earliestResolutionTimeOffset>`.

### M-4: §I.4 `<UrlParamInfo>` descriptor host (C-30)

**Ambiguity**: NotebookLM Q4 confirmed `<UrlParamInfo>` in the 2025
scheme is a native MPD-namespace element placed directly under
`<MPD>`, `<Period>`, `<AdaptationSet>`, `<Preselection>`, or
`<EventStream>`. Whether the `<EssentialProperty
schemeIdUri="urn:mpeg:dash:urlparam:2025">` host wrapper used in
Annex A.2 is still required, optional, or wrong is not resolved by
the audit's queries — the §I.4 wording may carry transitional
provisions for the descriptor-style host. Coupled with N-1 (wrong
namespace pattern), Annex A.2 is the second source of risk.

**Suggested clarification**: the spec authors should re-read §I.4
of DASH-6th directly and update Annex A.2 to the canonical 2025
pattern (with or without `<EssentialProperty>`), then mirror that
change in §5.7 of the spec.

### M-5: `MPD@profiles` delimiter not pinned for the multi-URI case (C-05)

**Ambiguity**: NotebookLM Q2 confirmed §8.1 defines `@profiles` as
**comma-separated**. Spec §5.2.2 permits `@profiles` to carry both
`urn:mpeg:dash:profile:list:2024` and
`urn:svta:dash:profile:sgai-overlay-list:2026` together, but no
annex exemplifies the multi-URI case and the spec text does not
pin the delimiter. Old audit's M-4 is partially resolved (no
violating example remains), but a future author following spec text
alone could emit space-separated values.

**Suggested clarification**: in §5.2.2, after "The ADS MAY include
both the linear baseline profile URI and the overlay-aware profile
URI in `@profiles`…", add: "Per §8.1 of ISO/IEC 23009-1, the
`@profiles` attribute is a comma-separated list of profile
identifiers. The two URIs MUST be separated by a comma:
`profiles="urn:mpeg:dash:profile:list:2024,urn:svta:dash:profile:sgai-overlay-list:2026"`."

### M-6: `urn:svta:dash:sgai-layout:2026` declared but never used (C-04)

**Ambiguity**: §2 normative-references table lists
`urn:svta:dash:sgai-layout:2026` as "scheme prefix for the
IAB-derived layout vocabulary (§3.2)", but no construct in the spec
body uses this URI as a `@schemeIdUri`, namespace, or in any other
capacity. The §3.2 layout vocabulary is expressed via bare tokens
(`overlay`, `pause-ad`, etc.) on `<svta:Layout @name>` and on
`<svta:RenderableAsset @layout>` — no URI prefixing. This is a dead
reference in §2 and not a conformance violation per se, but readers
following spec text expecting a usage may be confused.

**Suggested clarification**: either (a) delete the URI from §2
unless a future edition introduces a URI-prefixed layout
representation, or (b) document in §3.2 that the IAB layout
vocabulary may also be referenced as
`urn:svta:dash:sgai-layout:2026:<identifier>` in contexts that
require a fully qualified URI (e.g., descriptor `@schemeIdUri` if
such a use materialises).

## Open questions surfaced

- **OQ-1**: §I.4 of DASH 6th edition prescribes the canonical 2025
  pattern for the `UrlParamInfo` descriptor host element
  (`<EssentialProperty>` wrapper vs direct element). The audit
  surfaced the namespace change (N-1) but did not pin the exact
  host-wrapper shape. Spec authors should re-read §I.4 directly
  before publication.
- **OQ-2**: `Period@duration="PT0S"` exception (§5.3.2.2 Table 4) —
  whether a Period with `@duration=0` is admissible inside a ListMPD
  for the purpose of carrying foreign-namespace ad metadata and
  tracking. NotebookLM did not surface explicit ListMPD prohibitions
  on zero-duration Periods, but the spec arithmetic (cap, candidate
  duration accounting) currently assumes non-zero `Period@duration`.
  Worth a follow-up if remedy 3 of N-2 is chosen.
- **OQ-3**: NotebookLM Q3 surfaced that the DASH-6th source itself
  has internal schema-vs-semantic-table inconsistencies (`@uri` vs
  `@url`, `@clipDuration` vs `@clip`). This is not the SGAI spec's
  fault, but the SGAI editors should consider raising these against
  the MPEG-DASH editor's contact path before adopting positions that
  may need revisiting when DASH 6th publishes an erratum.

## Summary

- **Total constructs audited**: 35
- **Conforming (V)**: 27
- **Marginal (M)**: 6 (M-1: AlternativeMPD `@url` vs schema `@uri`;
  M-2: non-linear callback time-base invariant; M-3: inherited DASH
  unit ambiguity; M-4: §I.4 descriptor host shape; M-5: `@profiles`
  delimiter unpinned for multi-URI case; M-6: dead `…sgai-layout…`
  URI reference)
- **Non-conforming (N)**: 2 (N-1: `<up:UrlParamInfo>` namespace
  pattern in Annex A.2; N-2: regular Period in §5.2.2 resolution
  document with no `<ImportedMPD>` and no `<AdaptationSet>` and
  non-zero `Period@duration` — Annex C cand_2 and §5.5.3 case (a))

**Status vs old audit (2026-05-12)**:

- Old N-1 / N-2 (HTML / image as `Representation@mimeType` inside SPS
  sub-MPD): **resolved** — non-video forms now carried via
  `<svta:RenderableAsset>` foreign-namespace, never inside SPS
  sub-MPDs (C-24).
- Old M-1 / M-2 (`<ImportedMPD>` inside `<svta:Form>`,
  non-linear callback timing): **resolved structurally** —
  `<ImportedMPD>` is now a direct child of resolution-doc `<Period>`
  per §5.2.2 (C-33). M-2 carries forward as **new M-2 here**
  (`Period@duration` invariant still implicit).
- Old M-3 (`@earliestResolutionTimeOffset` unit collision between svta
  and `<ImportedMPD>`): **resolved** — SGAI now uses "seconds" on
  both. A new, narrower DASH-inherited ambiguity is captured as
  **new M-3** here.
- Old M-4 (`@profiles` delimiter, space vs comma): **partially
  resolved** — no annex example violates; spec text still doesn't
  pin the comma for the multi-URI case. Captured as **new M-5**.

**Priority for the next spec iteration**: N-1 and N-2 are
high-impact for production deployments — both produce manifests
that strict DASH-6th parsers will reject. N-2 is the more
consequential of the two because it touches the §5.5.3 case (a)
carrier pattern that the spec explicitly invokes for non-video
candidates. Recommended pre-publication: pick a remedy for N-2
(remedy 1 — minimal SPS sub-MPD sidecar — is the cleanest and
preserves the §5.5.2 / §5.5.3 symmetry), rewrite Annex A.2 against
the §I.4 2025 wording (N-1), and add explicit normative pins for
M-1 / M-2 / M-5. M-3, M-4, M-6 are editorial.

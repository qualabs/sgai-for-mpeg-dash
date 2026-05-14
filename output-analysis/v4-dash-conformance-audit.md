[GROUNDED_BY=notebooklm]

# DASH conformance audit — v4 (2026-05-14)

**Audit target**: `../output/v4-sgai-spec.md`.
**Reference**: MPEG-DASH 6th edition (ISO/IEC 23009-1:2025, FDIS).
**Method**: inventory of every construct introduced or modified by
the spec, four grounded queries against the "Streaming Protocols —
DASH, HLS, C2PA, DRM" notebook in NotebookLM (DASH-6th FDIS
loaded), and a per-construct verdict (Conforming / Marginal /
Non-conforming) against each cited DASH rule. The audit is
independent of the spec-build agent and the validate-spec sidecar
(`v4-spec-validation.md`).

## Scope

In scope: every new scheme URI, new XML element, new attribute on a
new or baseline element, new profile-URI usage, new structural
arrangement of baseline elements, and re-use of inherited baseline
constructs. Annexes A through G are audited as concrete instances
of the chapter 5 constructs; Annex H is informative test-case
material and is not audited as a construct.

Out of scope: design-level concerns already raised in the
validate-spec sidecar (use-case coverage, ambiguity, missing rules)
and editorial micro-issues raised in the detail-review log
(`v4-detail-review.md`). This audit only asks: *given the spec's
wording, would a DASH-6th-conformant parser process the construct as
the spec intends, or would the DASH rules reject it / interpret it
differently?*

## Method summary

- Inventory built from §2.1, §5.1.1–5.1.5, §5.2.1, §5.2.2, §5.3.1,
  §5.3.2, §5.3.4, §5.4, §5.5.1–5.5.4, §5.6.1–5.6.4, §5.7 and
  annexes A through F of `v4-sgai-spec.md`.
- 4 NotebookLM queries against the active notebook covering: (Q1)
  the `xs:any namespace="##other"` wildcard on `MPDType` /
  `PeriodType` / `AdaptationSetType`, `<EventStream>` placement
  rules under §5.10.2.1, the ignore-if-unknown rule for unknown
  `EventStream@schemeIdUri` values, and the §I.4 2025 UrlParamInfo
  namespace; (Q2) §8.14 ListMPD constraints (`MPD@type`,
  foreign-namespace children, AlternativeMPD / XLink prohibition),
  §8.15 SPS constraints, the `@url` vs `@uri` schema/prose split on
  `<InsertPresentation>` / `<ReplacePresentation>`, and §8.1
  `MPD@profiles` formatting; (Q3) the parseability of `<EventStream>`
  inside a foreign-namespace subtree, callback-scheme placement
  constraints, and the §I.3 wording for the 2025 `<UrlParamInfo>`
  descriptor host shape; (Q4) `<Period>` cardinality in `MPDType`,
  sole-vendor-URI legality on `MPD@profiles`, `@maxDuration` units
  and termination on §5.16.5, the `@clip` vs `@clipDuration`
  schema/prose split on `<ReplacePresentation>`, and the §8.13
  `advanced-linear:2025` profile URI. All 4 queries completed; 0
  `[fetch-failed]`.
- Each construct is assessed against the cited rule with a verdict.

## Inventory + verdicts

Legend: V = Conforming (verified against a DASH-6th cite);
M = Marginal (ambiguous, inherits a DASH-6th ambiguity, or needs an
explicit clarification); N = Non-conforming (violates a DASH-6th
rule as written).

| ID | Construct | Type | Placement | Verdict | Rationale |
|----|-----------|------|-----------|---------|-----------|
| C-01 | `urn:svta:dash:sgai:2026` | New XML namespace | Used on every SVTA element | V | §5.2.1 / §5.3.1.3 — foreign-namespace open content is the canonical extension point on `MPDType`, `PeriodType`, `AdaptationSetType` (`xs:any namespace="##other" processContents="lax"`). Q1 confirmed wildcard placement at the end of each type's `xs:sequence`. |
| C-02 | `urn:svta:dash:event:sgai-overlay:2026` | New `EventStream@schemeIdUri` | Primary MPD `<Period>`'s `<EventStream>` | V | §5.10.1 / §5.10.2.1 — unknown EventStream schemes are subscribed-to-or-ignored (Q1 / Q3). New vendor URI is the canonical extension path. |
| C-03 | `urn:svta:dash:event:sgai-pause-trigger:2026` | New `EventStream@schemeIdUri` | Primary MPD `<Period>`'s `<EventStream>` | V | Same as C-02. |
| C-04 | `urn:svta:dash:profile:sgai-overlay-list:2026` | New `MPD@profiles` value | Overlay Resolution Document `<MPD>` root | V | Q2 / Q4 — §8.1 / `ListOfProfilesType` permits a single URN with no DASH-baseline-profile companion. Spec's choice to author the overlay resolution document with only the SVTA URI in `@profiles` is schema-legal. |
| C-05 | `urn:svta:dash:sgai-layout:2026` | Declared scheme prefix / "XML namespace" | §2.1 table only | M (M-3) | Declared in §2.1 ("XML namespace / scheme-fragment") and §3.2 anchor language ("The layout-vocabulary anchor for chapter 3 §3.2 enum tokens"), but **never used** as a `@schemeIdUri`, namespace prefix, or scheme-fragment anywhere in the body. Layout tokens in §3.2 are bare strings (`overlay`, `pause-ad`, …), not URI-prefixed. Same as v3 audit M-6; status unchanged. |
| C-06 | `<svta:OverlayPresentation>` | New element | Child of `<Event>` (in svta-scheme `<EventStream>`) | V | §5.2.1 — `EventType` carries `xs:any namespace="##other" processContents="lax"`; foreign-namespace children of `<Event>` are valid extension points. |
| C-07 | `<svta:PauseAdPresentation>` (renamed in v4 from v3's `<svta:PauseAdTrigger>`) | New element | Child of `<Event>` (in svta-pause-trigger `<EventStream>`) | V | Same as C-06. |
| C-08 | `<svta:OverlayList>` | New element | **Direct** child of `<MPD>` in Overlay Resolution Document | V | Q1 confirmed the `MPDType` `xs:any namespace="##other"` wildcard appears at the **end** of `MPDType`'s `xs:sequence` and explicitly permits foreign-namespace children directly under `<MPD>` (not just under `<Period>`). Placement is schema-legal. |
| C-09 | `<svta:Candidate>` | New element | Child of `<svta:OverlayList>` | V | Internal to the SVTA-namespace subtree; opaque to baseline parsers via §5.2.1 fallback discard (Q3). |
| C-10 | `<svta:RenderableAsset>` | New element | Child of `<svta:Candidate>` | V | Same as C-09. |
| C-11 | `<svta:Click>`, `<svta:UniversalAdId>` | New elements | Children of `<svta:Candidate>` | V | Same as C-09. |
| C-12 | New attributes on new SVTA elements (e.g. `@url`, `@maxDuration`, `@earliestResolutionTimeOffset`, `@allowedLayouts`, `@maxConcurrent`, `@triggerMode` on OverlayPresentation / PauseAdPresentation; `@mediaType`, `@layout`, `@duration`, `@priority`, `@assetUrl` on RenderableAsset; `@through`, `@trackingUrl` on Click; `@idRegistry`, `@value` on UniversalAdId; `@version` on OverlayList; `@id`, `@adId`, `@priority` on Candidate) | New attributes on new elements | N/A (whole elements are svta-namespace) | V | Foreign-namespace attributes on a foreign-namespace element are not bound by any baseline schema. `@maxDuration` semantics match §5.16.5 (units = `EventStream@timescale`, Player MUST terminate at boundary — Q4 confirmed). |
| C-13 | `@earliestResolutionTimeOffset` reused as an attribute name on `<svta:OverlayPresentation>` / `<svta:PauseAdPresentation>` with **different units** (`<EventStream>@timescale`) from `<ImportedMPD>@earliestResolutionTimeOffset` (seconds) | Inherited attribute name with rebound unit | OverlayPresentation / PauseAdPresentation vs ImportedMPD | M (M-2) | v4 §5.1.3 patches the unit collision with an inline NOTE ("NOT identical to `@earliestResolutionTimeOffset` on `<ImportedMPD>` … the difference is intentional and aligned with the linear SGAI baseline"). Per Q4, §5.16.5 confirms the linear baseline does measure `@maxDuration` in `EventStream@timescale` units, so the rebinding is internally consistent with §5.16. But the collision remains invisible to a reader who only scans the XML — same finding the v4 detail review (Flagged issue 1) raised against `context/06-naming-and-namespaces.md`. Status: spec author chose prose-patch over rename; not a DASH-rule violation per se. |
| C-14 | `<InsertPresentation>` reused from §5.16.3 | Baseline element used as-is | Child of `<Event>` (insert-scheme `<EventStream>`) | M (M-1) | §5.16.3 confirmed (Q2). Same DASH-6th internal split as v3: the **schema** registers the URL attribute as `@uri` (`<xs:attribute name="uri" type="xs:anyURI" use="required"/>`) while the **semantic table 62** prose names it `@url`. Spec follows the prose (`url="…"` throughout §5.1.1, Annex A.2 L:1615). A strict schema validator would reject `<InsertPresentation url="…"/>`. Issue is inherited from DASH-6th; spec author should flag this back to the MPEG-DASH editor. |
| C-15 | `<ReplacePresentation>` reused from §5.16.4 | Baseline element used as-is | Child of `<Event>` (replace-scheme `<EventStream>`) | N (N-2) + M (M-1) | Two distinct issues compound on this element. (a) **M-1** — same `@url` / `@uri` schema/prose split as C-14 (Q2). (b) **N-2 — schema-vs-spec type collision on `@clipDuration`**: Q4 confirmed that the DASH 6th schema in §5.16.5 (`AlternativeMPDReplaceEventType`) declares `<xs:attribute name="clipDuration" type="xs:boolean" default="true"/>` — i.e. **boolean, default `true`**. The v4 spec's examples (Annex B.2 L:1724, Annex D.2 L:1960, Annex F.2 L:2090) emit `clipDuration="30000"`, a numeric value in `EventStream@timescale` units. `xs:boolean` does not accept `"30000"`; a strict schema validator would reject. The spec's semantic intent (a numeric clip length in timescale units) is the meaning the DASH-6th **prose** (Table 61) assigns to its `@clip` attribute, not to `@clipDuration`. See N-2 below. |
| C-16 | `<ImportedMPD>` as **direct child of `<Period>`** in `<ListMPD>` resolution document | Baseline element used as-is | `<Period>` of `ListMPD` (Annex A.3, B.3, F.3) | V | §5.3.2.6 confirmed. `@uri` is the canonical schema name; spec uses `uri=` consistently. `@earliestResolutionTimeOffset` default is 60 seconds; spec values (`0`, `15`, `20`, `55`) are interpreted as seconds. |
| C-17 | `<ImportedMPD>` as **child of `<svta:RenderableAsset>`** (`mediaType="video"`, §5.3.4) | Baseline element placed inside a foreign-namespace subtree | Inside SVTA subtree, opaque to baseline parsers per §5.2.1 fallback model | M (M-4) | Schema-legal: `<svta:RenderableAsset>` is foreign-namespace open content under `xs:any processContents="lax"`, so its content is not schema-validated against baseline DASH placement constraints (Q1). However, `<ImportedMPD>` is a baseline-DASH element whose schema position (§5.3.2.6) is exclusively under `PeriodType`. Re-using it inside a foreign-namespace parent is **semantically novel**: a legacy DASH parser strips the entire `<svta:RenderableAsset>` subtree (Q3 confirms §5.2.1 fallback removes the parent and all children together), so legacy parsers never reach `<ImportedMPD>` here. This is what graceful degradation requires, but the construct re-uses a Period-bound baseline element outside its native scope. Same finding as v3 audit C-20 (callback inside `<svta:Metadata>`), reformulated for v4's element shape. |
| C-18 | Callback-scheme `<EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015">` inside **SPS sub-MPD** `<Period>` (Annex A.4, B.4, C.4, F.4 — linear ads and non-linear video forms) | Baseline scheme + baseline element in baseline-correct placement | Direct child of sub-MPD `<Period>` | V | Q3 confirmed §5.10.4.5 / §5.10.2.1 — `<EventStream>` schema position is `PeriodType` direct child; SPS profile (§8.15) does not prohibit `<EventStream>` (Q3). Placement is schema-correct and semantically sound. |
| C-19 | Callback-scheme `<EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015">` as **child of `<svta:RenderableAsset>`** for image / HTML forms (§5.5.3) | Baseline DASH-namespaced element in non-baseline placement, inside a foreign-namespace subtree | Inside SVTA subtree of Overlay Resolution Document | M (M-4) | Q3 confirmed the strict reading: `<EventStream>` is schema-defined as a direct child of `<Period>` only, and inside a foreign-namespace subtree it is "opaque" — i.e. a baseline DASH parser following the §5.2.1 fallback model strips the parent `<svta:RenderableAsset>` *together with* its `<EventStream>` child (subtree removal). For graceful degradation this is exactly the intended behaviour (legacy Players never fire SGAI beacons). But the construct re-uses a baseline-DASH-namespaced element outside its native scope, and the spec's intent — "SGAI-aware Players parse this `<EventStream>` and fire its beacons" — relies on a placement the DASH schema does not endorse. Schema-legal (lax wildcard) but semantically novel; readers should not mistake this for a baseline DASH EventStream. |
| C-20 | Overlay Resolution Document envelope: `<MPD>` with `<svta:OverlayList>` as the **only child** (zero `<Period>` elements) — §5.2.2, Annex C.3, Annex E.3 | Baseline `MPDType` element used as document root | Resolution document root | **N (N-1)** | Q4 confirmed: §5.3.1.2 Table 3 and the normative XML schema in §5.3.1.3 define `<Period>` as `<xs:element name="Period" type="PeriodType" maxOccurs="unbounded"/>` — `minOccurs` defaults to 1, so an MPD with zero `<Period>` elements is **schema-invalid**. The Overlay Resolution Document as v4 currently authors it (Annex C.3, E.3) carries no `<Period>` at all. A strict DASH-conformant XML schema validator on the document will reject it. See N-1. |
| C-21 | `MPD@type="list"` + `urn:mpeg:dash:profile:list:2024` on linear resolution doc | Baseline ListMPD constraints applied | Resolution-doc root (Annex A.3, B.3, F.3) | V | Q2 confirmed `MPD@type="list"` is mandatory for ListMPD, that foreign-namespace children of `<MPD>` and `<Period>` are permitted in the ListMPD context, and that Alternative MPD events / XLink are prohibited inside the ListMPD. The spec's linear annexes do not place AlternativeMPD events or XLink in their ListMPDs. |
| C-22 | `MPD@type="static"` + `urn:mpeg:dash:profile:sps:2024` + exactly one `<Period>` per sub-MPD | Baseline SPS constraints applied | Sub-MPD root (Annex A.4, B.4, C.4, F.4) | V | Q2 confirmed `MPD@type="static"` and "one and only one Period element shall be present" for SPS, and RFC 4337 `@mimeType` binding (`video/mp4` / `audio/mp4` / `application/mp4`). All sub-MPD annexes comply. |
| C-23 | `MPD@type="static"` + `urn:svta:dash:profile:sgai-overlay-list:2026` (sole profile URI; no baseline DASH profile alongside) on overlay resolution doc | Baseline `@profiles` attribute with single vendor URN | Overlay resolution doc root | V | Q4 confirmed §8.1 / `ListOfProfilesType` permits a single URN or URL in `@profiles`; no normative requirement that a baseline DASH profile URI must be present. Spec's choice to author the overlay resolution doc with only the SVTA URI is schema-legal. (Practical caveat: ecosystem tooling that assumes a DASH-baseline profile presence may not auto-detect this manifest as a DASH document — pragmatic, not normative.) |
| C-24 | Two co-located `<EventStream>` siblings in the same `<Period>` (one linear-scheme + one overlay-scheme; §5.1.5, Annex D.2) | Multiple `<EventStream>` children of `<Period>` keyed by different `@schemeIdUri` | Primary MPD `<Period>` | V | §5.10.1 / §5.10.2.1 — DASH does not cap the number of `<EventStream>` children of `<Period>`; each is keyed independently by `@schemeIdUri` (Q1). Independent activation per spec §7.6. |
| C-25 | `<EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025">` wrapping `<up:UrlParamInfo xmlns:up="urn:mpeg:dash:schema:urlparam:2025" includeInRequests="altmpd" queryTemplate="…"/>` in Annex A.2 (L:1606-1609) | Reuse of §I.4 descriptor in the legacy 2014 / 2016 wrapper-pattern with non-MPD namespace | Primary MPD root | **N (N-3)** | Q3 quoted §I.3.1 verbatim: *"An MPD.EssentialProperty element with the attribute @schemeIdUri having value of 'urn:mpeg:dash:urlparam:2025' shall be present and **have no content**. The scheme uses a single element, UrlParamInfo… UrlParamInfo element(s) may be present in elements such as but not limited to MPD, Period, AdaptationSet, Preselection, or EventStream."* Q1 / Q3 also confirmed that in the 2025 scheme, `UrlParamInfo` is defined directly in the **core MPD namespace** `urn:mpeg:dash:schema:mpd:2011`, not in any `urlparam` namespace. The Annex A.2 fragment therefore violates §I.3.1 in three ways simultaneously: (i) the EssentialProperty has content (the `<up:UrlParamInfo …/>` nested inside it) when §I.3.1 requires the EssentialProperty to be empty; (ii) `UrlParamInfo` is emitted in a separate namespace (`urn:mpeg:dash:schema:urlparam:2025`) when §I.3.1 places it in the core MPD namespace; (iii) `UrlParamInfo` appears as a child of `EssentialProperty` instead of as a direct child of `<MPD>` / `<Period>` / `<AdaptationSet>` / `<Preselection>` / `<EventStream>`. See N-3. |
| C-26 | `@includeInRequests="altmpd"` on `UrlParamInfo` (Annex A.2) | Reuse of §I.4 attribute | `UrlParamInfo` attribute | V | `altmpd` is a defined key in §I.3 Table I.4 (per v3 audit Q4 verbatim). The attribute name itself is correct; the issue with the host descriptor is N-3 above, not the attribute. |
| C-27 | `urn:mpeg:dash:profile:advanced-linear:2025` on primary MPD (Annex A.2) | Reuse of §8.13 baseline profile | `MPD@profiles` of primary MPD | V | Q4 confirmed §8.13 explicitly defines this profile URI for the "ISO Base Media File Format Advanced Linear" profile. |

## NotebookLM findings (highlights)

- **Q1** (`xs:any` wildcard placement / `<EventStream>` placement /
  ignore-if-unknown / §I.4 2025 namespace): `MPDType` (§5.3.1.3),
  `PeriodType` (§5.3.2.3), and `AdaptationSetType`-via-
  `RepresentationBaseType` (§5.3.7.3) all carry `xs:any
  namespace="##other" processContents="lax"` at the **end** of
  their `xs:sequence`. `MPDType` therefore permits foreign-namespace
  children **directly** under `<MPD>` — not just under `<Period>`.
  Per §5.10.2.1, `<EventStream>` is **strictly Period-level only**:
  "events of the same type are specified by an EventStream element
  in a Period element"; the normative XML schema exclusively
  defines `<EventStream>` as a direct child of `PeriodType`.
  Unknown `EventStream@schemeIdUri` values are subscribed-or-
  ignored. For §I.4 2025: `UrlParamInfo` is defined directly in the
  **core MPD namespace** (`urn:mpeg:dash:schema:mpd:2011`); §I.3.1
  states that it "may be present in elements such as but not
  limited to MPD, Period, AdaptationSet, Preselection, or
  EventStream" with no separate-namespace prefix.
- **Q2** (§8.14 ListMPD + §8.15 SPS + AlternativeMPD schema vs prose
  + §8.1): `MPD@type="list"` mandatory for ListMPD. Foreign-
  namespace children are permitted in the ListMPD's `<MPD>` root
  and in its `<Period>` children. Alternative MPD events and XLink
  are **explicitly prohibited** inside a ListMPD ("List MPDs shall
  not contain Alternative MPD events" and "XLink shall not be used
  in any XML element within the List MPD"). SPS profile requires
  `MPD@type="static"` and exactly one `<Period>`, with RFC 4337
  `@mimeType` binding. **`@url` vs `@uri` schema/prose split
  confirmed**: schema declares `@uri` (`<xs:attribute name="uri"
  type="xs:anyURI" use="required"/>`), Table 62 prose names it
  `@url`. §8.1 confirms `MPD@profiles` is a comma-separated list.
- **Q3** (`<EventStream>` inside foreign-namespace subtree /
  callback scheme placement / §I.3 UrlParamInfo descriptor
  wording): When `<EventStream>` sits inside a foreign-namespace
  element, the §5.2.1 fallback model (*"the MPD shall be authored
  such that, after XML attributes or elements in other namespaces
  than the DASH namespace are removed, the result is a valid XML
  document"*) requires that the foreign parent's removal **also
  removes its entire subtree** — including the nested
  `<EventStream>`. A baseline-DASH-conformant parser sees no
  `<EventStream>` in such a position; for the construct to be
  parseable as an EventStream by a baseline-DASH client, it MUST
  sit as a direct child of `<Period>`. Callback scheme
  `urn:mpeg:dash:event:callback:2015` may be carried either by an
  `<EventStream>` at `<Period>` level or by `<InbandEventStream>`
  at AdaptationSet / Representation level; it is admissible inside
  an SPS sub-MPD's `<Period>` (Q3) and inside the regular Periods
  of a ListMPD. For §I.3 / §I.4 2025: the `<EssentialProperty>`
  acts only as an **empty flag** at MPD level (*"shall be present
  and have no content"*), while the actual `<UrlParamInfo>`
  elements are injected directly as native children of MPD /
  Period / AdaptationSet / Preselection / EventStream — NOT as
  children of `<EssentialProperty>`.
- **Q4** (`<Period>` cardinality / `@profiles` sole-vendor-URI
  legality / `@maxDuration` units / `@clip` vs `@clipDuration`
  schema / §8.13 profile): **`MPDType` requires `minOccurs=1`
  for `<Period>`** — the schema declaration is `<xs:element
  name="Period" type="PeriodType" maxOccurs="unbounded"/>` and the
  default `minOccurs=1` applies. §5.3.1.2 Table 3 lists cardinality
  `1…N`. An MPD with zero `<Period>` elements is schema-invalid;
  the informative §5.4.1 note ("An MPD can contain no Period
  element") does **not** override the normative schema constraint.
  `MPD@profiles` (`ListOfProfilesType`) accepts a single URN or
  URL — no requirement to include a baseline DASH profile URI.
  `@maxDuration` is "expressed in units of `EventStream@timescale`"
  (§5.16.5 Table 62), with termination mandatory at the boundary.
  **`@clip` vs `@clipDuration` schema split**: Table 61 prose calls
  the attribute `@clip`; the §5.16.5 normative schema for
  `AlternativeMPDReplaceEventType` declares it as `<xs:attribute
  name="clipDuration" type="xs:boolean" default="true"/>` — i.e.
  boolean with default `true`, not a numeric duration. §8.13
  confirmed `urn:mpeg:dash:profile:advanced-linear:2025`.

## Non-conforming items detail

### N-1: Overlay Resolution Document has zero `<Period>` elements (C-20)

**Conflict**: Q4 confirmed §5.3.1.3 declares `<xs:element
name="Period" type="PeriodType" maxOccurs="unbounded"/>` with
default `minOccurs=1`, and §5.3.1.2 Table 3 lists `<Period>`
cardinality as `1…N`. The Overlay Resolution Document the v4 spec
defines in §5.2.2 — and instantiates in Annex C.3 (L:1808-1881) and
Annex E.3 (L:2032-2058) — carries **no `<Period>` element**: its
`<MPD>` root has `<svta:OverlayList>` as its only substantive
child. A strict DASH-conformant schema validator on the document
will reject it as schema-invalid. This is a regression from the v3
audit: v3's Overlay Resolution Document used per-candidate
`<Period>` elements (which then triggered v3's N-2 on the
AdaptationSet requirement); v4 dispensed with the per-candidate
Period entirely and accidentally crossed under the MPD-level
`minOccurs=1` floor.

**Why this matters in practice**: an SGAI-aware Player can read the
document by skipping schema validation (or by treating `<svta:*>` as
opaque foreign content); the document parses as XML. But ecosystem
tooling — manifest validators, broadcaster QA pipelines, ad-server
integration tests, DASH-IF conformance tools — almost universally
runs XML schema validation as the first gate. A schema-invalid
manifest fails that gate and surfaces as a hard error before any
SGAI-aware logic even runs.

**Suggested fix**: pick one of three remedies, each a real change
to the spec.

1. **Wrap `<svta:OverlayList>` in a single `<Period>`** (cleanest):
   author the Overlay Resolution Document with exactly one
   `<Period>` whose only child is `<svta:OverlayList>` (and
   optionally `<svta:Metadata>` or similar). The `<Period>`
   inherits §5.3.2.3's `xs:any namespace="##other"` wildcard, so
   placing the SVTA subtree under it is schema-correct. The
   `<Period>` carries no `<AdaptationSet>` — this is admissible if
   `Period@duration` is set to `PT0S` (which satisfies the §5.3.2.2
   Table 4 exception) or if the resolution document is interpreted
   under the SVTA profile alone (since the SVTA profile has no
   declared dependency on the SPS or ListMPD profile and is the
   only `@profiles` value). Pick `Period@duration="PT0S"` to avoid
   re-opening v3's N-2 line of argument.
2. **Move `<svta:OverlayList>` to be a child of a `<Period>` that
   *does* carry an `<AdaptationSet>`** — e.g., a minimal
   placeholder `<AdaptationSet>` with no Representations. Higher
   ceremonial cost than remedy 1.
3. **Author the resolution document as a non-MPD root** — e.g.,
   `<svta:OverlayList>` as a top-level element under
   `urn:svta:dash:sgai:2026` with no `<MPD>` envelope at all. This
   abandons the "DASH-aware tooling can parse the envelope" claim
   in §5.2.2 ("Its root is `<MPD>` … so DASH-aware tooling can
   parse the envelope"). High disruption, but conceptually
   defensible: the document is not a Media Presentation; it is a
   non-linear resolution catalogue, and pretending it is an MPD
   creates the schema impedance N-1 documents.

Remedy 1 is the recommendation: smallest change, preserves the
"DASH-aware tooling parses the envelope" property, satisfies the
schema, and `Period@duration="PT0S"` cleanly closes the §5.3.2.2
Table 4 question.

### N-2: `<ReplacePresentation @clipDuration>` schema/type mismatch (C-15)

**Conflict**: Q4 confirmed the §5.16.5 normative XML schema declares
`<xs:attribute name="clipDuration" type="xs:boolean"
default="true"/>` on `AlternativeMPDReplaceEventType`. The v4 spec
emits `clipDuration="30000"` (a numeric value in
`EventStream@timescale` units) in Annex B.2 (L:1724), Annex D.2
(L:1960), and Annex F.2 (L:2090). `xs:boolean` accepts only the
lexical values `true` / `false` / `1` / `0`; `"30000"` is not a
valid `xs:boolean` literal. A strict XML schema validator will
reject these `<ReplacePresentation>` instances.

There is a second layer of confusion: Table 61 in DASH-6th prose
names the attribute `@clip` (not `@clipDuration`). The semantics
the v4 spec assigns to the attribute — "a numeric clip length in
timescale units" — match neither the schema's `@clipDuration`
(boolean) nor the prose's `@clip` (Table 61 does not, per Q4's
quoted lines, define a numeric clip length attribute either). The
DASH-6th specification itself is internally inconsistent here, but
the **schema is the conformance authority**: the v4 spec's numeric
`clipDuration="30000"` is rejected by every conformant validator.

**Suggested fix**: choose between (a) treating `@clipDuration` as
the schema does — boolean, default `true` — and removing the
numeric value from the v4 annex examples (the slot cap is already
declared on `@maxDuration`, so a separate numeric `@clipDuration`
is redundant); or (b) if the spec genuinely needs a numeric
"how many timescale units to clip" attribute, give it a new SVTA
name (`<svta:clipDuration>` or similar) under the
`urn:svta:dash:sgai:2026` namespace so it carries SGAI-specific
semantics, and remove the conflicting use of the baseline
`@clipDuration` from `<ReplacePresentation>` calls in §5.1.2 and
the annexes. Either way: the spec author should flag the DASH-6th
internal `@clip` vs `@clipDuration` (prose vs schema) split back
to the MPEG-DASH editor as inherited ambiguity (carry-over from
M-1 / v3 OQ-3).

### N-3: `<EssentialProperty>` + `<up:UrlParamInfo>` namespace pattern in Annex A.2 (C-25)

**Conflict**: Q3 quoted §I.3.1 verbatim:
*"An MPD.EssentialProperty element with the attribute @schemeIdUri
having value of 'urn:mpeg:dash:urlparam:2025' shall be present and
**have no content**. The scheme uses a single element,
UrlParamInfo… UrlParamInfo element(s) may be present in elements
such as but not limited to MPD, Period, AdaptationSet, Preselection,
or EventStream."* Q1 / Q3 also confirmed that in the 2025 scheme,
`UrlParamInfo` is defined directly in the **core MPD namespace**
`urn:mpeg:dash:schema:mpd:2011`, not in any separate `urlparam`
namespace.

The Annex A.2 fragment (v4 L:1606-1609):

```xml
<EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025">
  <up:UrlParamInfo includeInRequests="altmpd"
                   queryTemplate="…"/>
</EssentialProperty>
```

violates §I.3.1 in three ways simultaneously:

1. The `<EssentialProperty>` has content (the `<up:UrlParamInfo …/>`
   nested inside it) — §I.3.1 mandates the element "shall be
   present and have no content".
2. `<UrlParamInfo>` is emitted in a separate namespace
   (`xmlns:up="urn:mpeg:dash:schema:urlparam:2025"`) — §I.3.1
   places it in the **core MPD namespace**.
3. `<UrlParamInfo>` appears as a **child of `<EssentialProperty>`**
   — §I.3.1 places it as a direct child of `<MPD>`, `<Period>`,
   `<AdaptationSet>`, `<Preselection>`, or `<EventStream>`. The
   legacy 2014 / 2016 schemes used the wrapper-inside-
   EssentialProperty pattern; the **2025 scheme abandoned it**.

A strict 2025-aware parser will either (a) reject the document
because `<EssentialProperty>` is supposed to be empty and is not,
(b) treat the `up:`-namespaced element as foreign open content and
discard it under §5.2.1 NOTE 2 — defeating the purpose of declaring
the descriptor, or (c) ignore the `<EssentialProperty>` because the
scheme is recognised but the content shape is wrong. In none of
the three cases does the Player apply the intended URL
parameterisation.

This is an expansion of v3 audit's N-1, made worse by Q3's deeper
read of §I.3.1: the original v3 finding flagged only the namespace
mismatch; this audit clarifies that the **wrapper pattern itself
is also wrong** (the EssentialProperty must be empty, not a
container for UrlParamInfo).

Additionally, the spec's §2 normative-references table lists
`urn:mpeg:dash:schema:urlparam:2025` as the "XML namespace for the
§I.4 UrlParamInfo descriptor", which is the inverse of the
DASH-6th 2025 rule (no separate namespace; the element lives in
the MPD namespace).

**Suggested fix**: rewrite the Annex A.2 sample so the descriptor is
emitted in the canonical 2025 pattern:

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" …>
  <EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025"/>
  <UrlParamInfo includeInRequests="altmpd"
                queryTemplate="video_profile=…&amp;session_id=…"/>
  <Period>…</Period>
</MPD>
```

— that is: `<EssentialProperty>` is empty (just declares the scheme
is active), and `<UrlParamInfo>` is a separate, sibling element in
the core MPD namespace, placed directly under `<MPD>` (or under
`<Period>` / `<AdaptationSet>` / etc. as the scope requires). Drop
the `xmlns:up` declaration from the manifest envelope. Update §2
normative-references to remove
`urn:mpeg:dash:schema:urlparam:2025` (since DASH 6th 2025 does not
define it as an XML namespace), and update §5.7 of the spec to
describe the empty-wrapper + direct-child pattern.

## Marginal items detail

### M-1: `@url` vs `@uri` on `<InsertPresentation>` / `<ReplacePresentation>` (C-14, C-15)

**Ambiguity**: Q2 found the DASH-6th internal split: the schema
definition for `AlternativeMPDEventType` registers the URL
attribute as `@uri` (`<xs:attribute name="uri" type="xs:anyURI"
use="required"/>`); the semantic table 62 names it `@url`. DASH 6th
itself is inconsistent. The SGAI spec follows the prose
(`url="…"` throughout §5.1.1, §5.1.2, and every annex example). A
strict schema validator on a 2025 DASH manifest would reject
`<InsertPresentation url="…"/>` and expect
`<InsertPresentation uri="…"/>`. Identical to v3 audit M-1; no
movement in the upstream source.

**Suggested clarification**: either (a) align with the schema
(`@uri`) and add a NOTE in §5.1.1 / §5.1.2 stating that the
Table-62 semantic-table prose names the attribute `@url`
informally; or (b) emit both forms (schema-named `@uri` plus the
prose-named `@url`) so a strict schema validator and a
prose-following implementer both succeed. Spec authors should also
escalate this DASH-6th inconsistency to the MPEG-DASH editor as an
erratum candidate (see OQ-1).

### M-2: `@earliestResolutionTimeOffset` rebound unit on SVTA elements (C-13)

**Ambiguity**: §5.1.3 / §5.1.4 reuse the baseline
`@earliestResolutionTimeOffset` attribute name on
`<svta:OverlayPresentation>` / `<svta:PauseAdPresentation>` but
rebind its unit from "seconds" (the baseline `<ImportedMPD>` unit
per §5.3.2.6.1) to "`<EventStream>@timescale` units" (matching the
§5.16 baseline for `<InsertPresentation>` / `<ReplacePresentation>`,
per Q4). The rebinding is internally consistent with the linear
SGAI baseline, and the spec patches the unit collision with an
inline NOTE in §5.1.3. But the collision remains **invisible to a
reader who only scans the XML** — `context/06-naming-and-
namespaces.md` explicitly forbids this pattern. The v4 detail
review (Flagged issue 1) raised the same concern at the spec/context
boundary. This is not a DASH-rule violation; it is an internal
spec-to-context consistency gap.

**Suggested clarification**: either rename the SVTA attribute
(e.g. `@earliestResolutionTimeOffsetTicks`) so the unit is audible
at the XML call site, or amend `context/06-naming-and-namespaces.md`
to admit "rename OR explicit inline NOTE" as the audibility lever.
Decision is the spec author's; the audit only flags the gap.

### M-3: `urn:svta:dash:sgai-layout:2026` declared but never used (C-05)

**Ambiguity**: §2.1 lists `urn:svta:dash:sgai-layout:2026` as "XML
namespace / scheme-fragment" and §3.2 anchor language calls it the
"layout-vocabulary anchor for chapter 3 §3.2 enum tokens", but no
construct in the spec body uses this URI as a `@schemeIdUri`,
namespace prefix, or scheme-fragment. The §3.2 layout vocabulary
is expressed via bare tokens (`overlay`, `pause-ad`, `squeezeback`,
…) on `<svta:OverlayPresentation>@allowedLayouts` and on
`<svta:RenderableAsset>@layout` — no URI prefixing anywhere. This
is a dead reference. Identical to v3 audit M-6; status unchanged.

**Suggested clarification**: either (a) delete the URI from §2.1
unless a future edition introduces a URI-prefixed layout
representation, or (b) document explicitly in §3.2 that the
layout vocabulary tokens MAY be referenced as
`urn:svta:dash:sgai-layout:2026:<token>` in any context that
requires a fully qualified URI (e.g. `@schemeIdUri` on a future
descriptor), and that bare tokens are the canonical form.

### M-4: Baseline DASH elements re-used inside foreign-namespace subtrees (C-17, C-19)

**Ambiguity**: The v4 spec places two baseline DASH elements
inside SVTA-namespace subtrees:

- `<ImportedMPD>` as a child of `<svta:RenderableAsset>`
  (`mediaType="video"`, §5.3.4).
- `<EventStream>` (callback scheme) as a child of
  `<svta:RenderableAsset>` for image / HTML form tracking
  (§5.5.3).

Both placements are **schema-legal** under the §5.2.1 lax wildcard
on foreign-namespace content (the parent's content model is
`xs:any processContents="lax"`, so anything is allowed inside).
But both elements are **semantically defined for baseline-DASH
placements only**: `<ImportedMPD>` is schema-positioned under
`PeriodType`; `<EventStream>` is, per Q1 / Q3, strictly Period-
level. Q3's §5.2.1 fallback-model quote
(*"after XML attributes or elements in other namespaces than the
DASH namespace are removed, the result is a valid XML document"*)
confirms that legacy parsers strip the foreign-namespace parent
**together with its subtree** — so legacy parsers never see the
nested `<ImportedMPD>` or `<EventStream>`, and the SGAI-aware
Player is the only actor that locates them.

This is acceptable from a graceful-degradation standpoint (legacy
Players fall through cleanly), but the spec re-uses baseline-DASH
names for SGAI-specific semantics. Readers should not mistake
`<EventStream>` inside `<svta:RenderableAsset>` for a baseline
DASH EventStream: it inherits the XML shape but its time-base
semantics (per §5.5.3, "relative to the moment the form becomes
visible") are not the baseline §5.10.2.1 semantics (relative to
the carrying Period's start).

**Suggested clarification**: in §5.3.4 and §5.5.3, add a NOTE
that explicitly says: "Although this element re-uses the baseline
DASH `<ImportedMPD>` / `<EventStream>` XML shape, it is interpreted
under SGAI semantics defined in this spec — not under the
baseline §5.3.2.6 / §5.10.2.1 semantics. A baseline DASH parser
strips the entire `<svta:RenderableAsset>` subtree via the §5.2.1
fallback model and therefore never reaches this element; only
SGAI-aware Players are expected to parse it." Cheap to fix; not a
non-conformance per se because the lax wildcard permits the
placement.

## Open questions surfaced

- **OQ-1**: DASH-6th internal schema-vs-prose split on
  AlternativeMPD attribute names — `@uri` vs `@url` (insert /
  replace) and `@clip` vs `@clipDuration` (replace, with the
  additional type mismatch `xs:boolean default="true"` vs
  numeric duration in spec). This is not the SGAI spec's fault,
  but the SGAI editors should consider raising these against the
  MPEG-DASH editor's contact path as erratum candidates. Direct
  carry-over from v3 audit's OQ-3.
- **OQ-2**: The remedy for N-1 (zero-Period Overlay Resolution
  Document) intersects with the §5.3.2.2 Table 4 question.
  Remedy 1 of N-1 proposes `Period@duration="PT0S"` to satisfy the
  Table-4 exception ("at least one Adaptation Set shall be present
  in each Period unless Period@duration is zero"); the spec's
  arithmetic does not currently use `Period@duration` in the
  resolution doc for cap or candidate accounting, so the
  zero-duration carrier is benign — but this should be verified
  end-to-end before committing.
- **OQ-3**: The Annex A.2 fix for N-3 (empty `<EssentialProperty>`
  + sibling `<UrlParamInfo>` in the core MPD namespace) is the
  audit's best read of §I.3.1; the spec authors should re-read
  §I.4 of DASH-6th directly to confirm the exact element-ordering
  rules (whether `<UrlParamInfo>` MUST precede or follow
  `<Period>`, whether multiple `<UrlParamInfo>` siblings are
  permitted, etc.) before publication. The audit's read is "place
  before `<Period>`" but DASH-6th may permit either order; not
  confirmed.

## Summary

- **Total constructs audited**: 27
- **Conforming (V)**: 20
- **Marginal (M)**: 4 (M-1: AlternativeMPD `@url` vs schema `@uri`;
  M-2: SVTA `@earliestResolutionTimeOffset` invisible unit
  rebinding; M-3: dead `…sgai-layout…` URI reference; M-4:
  baseline DASH elements re-used inside foreign-namespace subtrees
  — `<ImportedMPD>` in §5.3.4, `<EventStream>` in §5.5.3)
- **Non-conforming (N)**: 3 (N-1: Overlay Resolution Document has
  zero `<Period>` elements, violating `MPDType` `minOccurs=1`;
  N-2: `<ReplacePresentation @clipDuration>` numeric value vs DASH
  schema `xs:boolean default="true"`; N-3:
  `<EssentialProperty>` + `<up:UrlParamInfo>` Annex A.2 pattern
  violates §I.3.1 in three ways)

**Status vs v3 audit (2026-05-14, prior build)**:

- v3 N-1 (`<up:UrlParamInfo>` namespace pattern in Annex A.2):
  **carried forward and expanded** as v4 N-3. Q3 surfaced the
  additional §I.3.1 constraints the v3 audit did not catch
  (empty-EssentialProperty rule; UrlParamInfo as a sibling, not a
  child, of EssentialProperty). v4 fix is bigger than v3 fix.
- v3 N-2 (regular Period in resolution doc with no `<ImportedMPD>`
  and no `<AdaptationSet>` and non-zero `Period@duration`):
  **structurally resolved** by v4's architectural choice to drop
  the per-candidate `<Period>` and use a single `<svta:OverlayList>`
  under `<MPD>`. The §5.3.2.2 Table 4 violation no longer applies
  because there are no candidate-bearing Periods. **But the fix
  introduced a new violation**: zero `<Period>` elements crosses
  under the `MPDType` `minOccurs=1` floor (new N-1).
- v3 M-1 (`@url` vs `@uri`): **carried forward unchanged** as v4
  M-1.
- v3 M-2 (callback `Event@presentationTime` time-base for
  non-linear ads): **resolved structurally** — v4 §5.5.3 puts the
  tracking carrier inside `<svta:RenderableAsset>` with a clearly
  declared time base ("relative to the moment the form becomes
  visible"). The new construct introduces M-4 (baseline element
  re-used in foreign placement) but the time-base remap question
  is now self-contained.
- v3 M-3 (inherited DASH unit ambiguity on
  `@earliestResolutionTimeOffset`): **resolved structurally** —
  v4 §5.1.3 explicitly resolves to `EventStream@timescale` units
  on the SVTA elements, with an inline NOTE distinguishing from
  `<ImportedMPD>`. The rename-vs-NOTE question is now an
  internal context/spec issue (new M-2), not a DASH-source
  ambiguity.
- v3 M-4 (`<UrlParamInfo>` descriptor host shape — open
  question): **resolved on the wording side by Q3** (the
  EssentialProperty is empty; UrlParamInfo is a direct child of
  MPD-namespace hosts) and **absorbed into v4 N-3** as the
  fix-direction.
- v3 M-5 (`@profiles` delimiter unpinned for multi-URI case): the
  v4 Overlay Resolution Document carries only the SVTA URI in
  `@profiles` (sole vendor URN), so no multi-URI delimiter
  question is exercised. **Latent**; not a finding for v4.
- v3 M-6 (dead `…sgai-layout…` URI reference): **carried forward
  unchanged** as v4 M-3.

**Priority for the next spec iteration**: N-1 and N-3 are the two
high-impact items. N-1 (zero-`<Period>` Overlay Resolution Document)
fails strict schema validation on every Overlay Resolution Document
the spec produces — every non-linear ad slot in production
deployments hits it. N-3 (Annex A.2 UrlParamInfo pattern) fails
the §I.3.1 wording in three compounded ways; the fix path is clear
from Q3's quoted text. N-2 (`@clipDuration` type mismatch) is
narrower in scope (only `<ReplacePresentation>` instances) but is
strict-validator-rejecting on every mid-roll annex example. M-1
and M-4 are editorial-but-real (spec authors should add explicit
NOTEs); M-2 and M-3 are pure-editorial.

Recommended pre-publication sequence: (1) pick N-1 remedy 1
(`<Period duration="PT0S">` wrapper around `<svta:OverlayList>`);
(2) rewrite Annex A.2 to the canonical 2025 §I.3.1 pattern (N-3);
(3) decide between treating `@clipDuration` as the schema's
boolean or renaming the SGAI-specific numeric attribute (N-2); (4)
add explicit NOTEs for M-1 and M-4; (5) defer M-2 / M-3 to the
context/spec consistency pass.

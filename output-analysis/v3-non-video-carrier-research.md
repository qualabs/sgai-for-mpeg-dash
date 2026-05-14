[GROUNDED_BY=notebooklm]

# Non-video carrier research — SGAI norm v2 follow-up

**Audit target**: `../output/2026-05-12-dash-conformance-audit.md`,
findings **N-1** (HTML form `mimeType="text/html"` inside SPS sub-MPD)
and **N-2** (image form `mimeType="image/png"` inside SPS sub-MPD).
**Reference**: MPEG-DASH 6th edition (ISO/IEC 23009-1:2025).
**Method**: 10 grounded queries against the "Streaming Protocols —
DASH, HLS, C2PA, DRM" notebook in NotebookLM (DASH-6th source loaded).
10 completed, 0 failed. No max-query cap was applied per Nicolas's
direction.

## Problem statement

The DASH conformance audit (2026-05-12) flagged that the spec v2
puts `<AdaptationSet mimeType="text/html">` (Annex B §B.4) and
`<AdaptationSet mimeType="image/png">` (implied by the §B.4 prose
"swapping the AdaptationSet content for image/png") inside per-form
sub-MPDs that the spec also requires to conform to SPS (§5.7 →
§8.15). SPS strictly inherits §7.3, which mandates `@mimeType`
per IETF RFC 4337 — that registry only contains `video/mp4`,
`audio/mp4`, and `application/mp4`. The non-video forms therefore
break SPS conformance as written.

The audit's suggested fix — "wrap HTML/PNG in `application/mp4` as
a single-sample track" — was rejected by Nicolas as over-engineering.
This document re-validates the constraint, enumerates DASH-compliant
alternatives that admit non-video assets *without* ISOBMFF wrapping,
ranks them in a decision matrix, and recommends one option with a
sketch of the Annex B rewrite.

## Re-validation of the §8.15 SPS constraint

The constraint is confirmed and, if anything, **harder** than the
audit stated.

- **§8.15 inherits §7.3 verbatim**: the spec text reads "The rules
  for the MPD as defined in subclause 7.3 shall apply", and §7.3
  reads "The @mimeType attribute of each Representation shall be
  provided according to IETF RFC 4337". RFC 4337 registers
  exclusively `video/mp4`, `audio/mp4`, `application/mp4` for the
  MPEG-4 systems family. Re-validation: SPS is bound by chain
  §8.15 → §7.3 → RFC 4337 with no extension point.
- **The escape hatch is one level up, not inside SPS**: §8.8
  (Extended Live) and §8.9 (Extended On-Demand) include the
  permissive clause "any Representation with a `@mimeType` other
  than `video/mp4`, `audio/mp4`, `application/mp4`, or `text/mp4`
  may be ignored by the client". SPS does **not** include this
  language — non-conforming MIME inside SPS is a hard violation,
  not a "may be ignored" soft drop.
- **Annex F is the only normative path to non-ISO-BMFF**: Annex F
  ("Guidelines for extending DASH with other delivery formats") is
  informative, F.2 mandates that a custom format's authoring rules
  define a MIME type for the Representation when formed as a
  concatenation of Segments. Annex F requires the introduction of
  a new **Interoperability Point URI** in `MPD@profiles` (§8.1).
  No spec-defined image profile, HTML profile, or thumbnail profile
  exists in the 6th edition (verified — `ImageRepresentation` does
  not exist; the only image-related construct is the open
  enumeration `@contentType="image"` from
  `RFC6838ContentTypeType`).
- **Sub-MPDs MUST be SPS, full stop**: §5.3.2.6 reads "MPDs
  referenced in the ImportedMPD element shall be restricted to the
  constraints of a single period profile as defined in clause 8.15".
  A sub-MPD cannot escape SPS by declaring a broader profile (Main,
  Live, On-Demand, Full). A vendor profile URI may be appended to
  the SPS URI in `@profiles`, but the document still has to satisfy
  the SPS intersection — so the vendor profile can only **add**
  constraints, never relax them. SPS conformance is structurally
  inescapable for any document reached via `<ImportedMPD>`.
- **Inline Periods inside the ListMPD itself inherit CMAF**: a
  ListMPD MAY contain "regular Periods" alongside Linked Periods
  (§8.14), but the ListMPD profile is formally an extension of the
  ISO-BMFF CMAF profile (§8.12). Any inline `<AdaptationSet>` /
  `<Representation>` inside a ListMPD-level Period therefore also
  inherits CMAF, which is itself ISO-BMFF — `text/html` and
  `image/png` on a ListMPD-level AdaptationSet would violate the
  same RFC 4337 chain. **The DASH AdaptationSet / Representation
  axis is closed for non-mp4 assets in this design, end to end.**
  The only DASH-conformant carriers for non-AV assets are:
  foreign-namespace open content under §5.2.1, application-level
  Event Streams under §5.10, and `EssentialProperty` /
  `SupplementalProperty` descriptors under §5.8.4.8 / §5.8.4.9.

The implication that drove every option below: **the path to a
DASH-compliant non-video form is not "fix the sub-MPD's mimeType"
but "do not deliver the non-video asset through an `ImportedMPD`
sub-MPD in the first place"**, or, if the sub-MPD path is kept,
"carry the asset URL outside of any AdaptationSet element". Every
option below makes one of those two moves.

## Options identified

The options are presented in order of increasing departure from the
v2 design. A-Wrap is included for completeness as the audit's
original suggestion; the recommendation excludes it.

### Option A — Inline form in `<svta:Form>` (no `<ImportedMPD>` for non-video forms)

- **Construction**: For non-video forms only, the `<svta:Form>`
  element drops its `<ImportedMPD uri="…"/>` child and replaces it
  with two svta-namespaced children:
  - `<svta:RenderableAsset href="creatives/cand-1.html" mimeType="text/html"/>`
    — a direct URL to the renderable asset.
  - `<svta:TrackingEvents>` carrying impression / quartiles /
    complete URLs, scheduled against the Broadcaster-declared
    overlay window. Optionally this MAY be expressed as an
    EventStream of scheme `urn:mpeg:dash:event:callback:2015`
    *inside* the svta foreign-namespace subtree, so SGAI-aware
    Players reuse their existing callback dispatcher.

  Video forms keep `<ImportedMPD uri="creatives/cand-1.mpd"/>` as
  in v2; the SPS sub-MPD remains the carrier for ISO-BMFF assets.

- **DASH baseline ref**: §5.2.1 (`<xs:any namespace="##other"
  processContents="lax"/>` is normative on every container type,
  including `<svta:Form>`'s ancestor `<Period>` and `<svta:Form>`
  itself since it lives in foreign namespace). §5.10.4.5 (callback
  scheme) confirmed in Q4 as carriable via Event element text
  content. §8.14 ListMPD permits Periods that are "regular Periods"
  without `<ImportedMPD>` (Q6).
- **Pros**:
  - DASH-compliant by construction — no AdaptationSet, no MIME
    constraint, no SPS sub-MPD for non-video forms.
  - Backward-compat with legacy Players (R1) is unchanged: the
    whole svta subtree is foreign-namespace and ignored by a
    legacy parser. A legacy Player that doesn't understand svta
    schemes never sees the non-video form, so there is no
    inadvertent rendering.
  - Reuses the existing `<svta:Form>` machinery already shipped in
    v2. The change is local to chapter 5 §5.6.2 (one element
    swapped for non-video forms) and Annex B §B.4 (the per-form
    sub-MPD example is replaced for non-video forms with an inline
    `<svta:RenderableAsset>` block).
  - Tracking semantics unchanged: callback scheme works inside the
    svta subtree as it does inside an SPS sub-MPD, because the
    scheme is application-level, not packaging-level.
  - One-fetch optimisation: the Player resolves the asset URL
    directly from the ListMPD, no second round-trip for a sub-MPD
    that only contains an HTML or PNG reference.
- **Cons**:
  - Asymmetry between video and non-video forms: video keeps
    `<ImportedMPD>`, non-video uses `<svta:RenderableAsset>`. Need
    a clean §5.5 / §5.6.2 statement of which form-class uses which
    carrier.
  - The `@earliestResolutionTimeOffset` semantics on the parent
    `<svta:Form>` already need clarification (M-1 in the audit) —
    this change does not resolve M-1, but it doesn't make it
    worse: M-1 is now scoped exclusively to video forms that still
    use `<ImportedMPD>`.
- **Implementation complexity**: **Low**. One element swap; one
  example revision; one §5.5 sentence pinning carrier-per-form-class.
- **Backward-compat (R1)**: ✓ — entire svta subtree opaque to
  legacy parsers.
- **Fit with current Annex B**: high — Annex B §B.4 already opens
  with "swapping the AdaptationSet content for image/png" as a
  parenthetical; this change replaces that parenthetical with a
  clean "non-video forms use inline carriage; only video forms
  use ImportedMPD".

### Option B — SupplementalProperty descriptor on the form

- **Construction**: Replace `<ImportedMPD>` (for non-video forms)
  with a `<SupplementalProperty schemeIdUri="urn:svta:sgai:renderable-asset:2026"
  value="creatives/cand-1.html|text/html"/>` inside `<svta:Form>`.
  Tracking carried as Option A.
- **DASH baseline ref**: §5.8.4.9 (SupplementalProperty), confirmed
  in Q5 as DASH-defined for vendor extension descriptors with
  ignore-if-unknown semantics.
- **Pros**: uses a spec-blessed descriptor (`SupplementalProperty`)
  instead of a foreign-namespace child element. Legacy ignore
  semantics are explicit in §5.8.4.9. Vendor scheme URI is
  registrable.
- **Cons**: `SupplementalProperty` is defined at
  AdaptationSet / Representation / Sub-Representation level
  (§5.8.4.9), not as a generic top-level descriptor. Hosting it as
  a child of `<svta:Form>` works (foreign-namespace ancestor
  permits any child) but loses the spec's natural placement. Less
  readable than Option A's explicit `<svta:RenderableAsset>`
  element. No gain in conformance — Option A already passes via
  §5.2.1.
- **Implementation complexity**: **Low**.
- **Backward-compat (R1)**: ✓ — SupplementalProperty unknown
  scheme is ignored per §5.8.4.9.
- **Fit with current Annex B**: medium. Adds a generic descriptor
  pattern where v2 already commits to explicit svta-named
  elements (`<svta:Form>`, `<svta:CandidateForms>`,
  `<svta:OverlayPresentation>`). Inconsistent with the existing
  spec voice.

### Option C — Tracking-only SPS sub-MPD; asset URL on the form

- **Construction**: For non-video forms, keep `<ImportedMPD>`
  pointing at a sub-MPD, but make the sub-MPD an **empty-AdaptationSet
  / tracking-only SPS**: one Period with EventStream(callback) but
  zero AdaptationSet elements. The asset URL lives on `<svta:Form>`
  via `<svta:RenderableAsset>` as in Option A.
- **DASH baseline ref**: §5.3.2.2 Table 4 — "At least one Adaptation
  Set shall be present in each Period unless the value of the
  `@duration` attribute of the Period is set to zero." §8.15
  inherits this. Confirmed in Q9.
- **Verdict**: **Non-conforming in the naive form.** A non-zero
  duration SPS Period MUST contain at least one AdaptationSet. The
  only two compliant variants are:
  (i) `Period@duration="PT0S"` — defeats the purpose, since the
  tracking slot is exactly a non-zero duration; the callback
  EventStream's `@presentationTime` is meaningless on a
  zero-duration Period.
  (ii) Add one stub `application/mp4` AdaptationSet — but this is
  Option E lite (still requires ISO-BMFF tooling for a no-op
  track). No gain over Option A.
- **Implementation complexity**: **Medium** (requires the
  application/mp4 stub trick that Nicolas already rejected for the
  full-asset case).
- **Backward-compat (R1)**: ✓.
- **Fit with current Annex B**: medium. Half-step retains the
  sub-MPD round-trip but moves the asset URL.
- **Why eliminated**: §5.3.2.2 Table 4 forbids the naive
  zero-AdaptationSet variant for non-zero-duration Periods. The
  stub-AdaptationSet workaround re-introduces the ISO-BMFF
  packaging cost that the recommendation is trying to avoid.

### Option D — EventStream-only carrier in the primary MPD

- **Construction**: Skip the ListMPD path entirely for non-video
  forms. The Broadcaster declares an additional EventStream in the
  primary MPD with a new vendor scheme (e.g.
  `urn:svta:dash:sgai-overlay-asset:2026`) whose Event children
  carry the asset URL in the Event element text content. The ADS
  is bypassed for non-video forms; the Broadcaster pre-authors
  them.
- **DASH baseline ref**: §5.10.2.3 EventType is `mixed=true` and
  permits an inline URL in Event text content — exactly how the
  callback scheme (§5.10.4.5) is defined. Q4 confirmed.
- **Pros**: zero new structure in ListMPD or sub-MPD. Cleanest
  possible DASH-layer integration.
- **Cons**: **kills the SGAI value proposition** for non-video ads.
  The whole point of SGAI is that the ADS, not the Broadcaster,
  decides which ads run per session. If non-video forms are
  hardcoded into the primary MPD, the multi-form / multi-candidate
  / device-aware selection machinery of v2 chapter 5 disappears.
  Trade-off worse than the SPS conformance bug.
- **Implementation complexity**: **High**. Requires retracting
  chapter 5 §5.5-§5.7 for non-video forms and replacing the
  non-linear flow with a primary-MPD-only path. Inconsistent with
  the project's R1..R13 architecture.
- **Backward-compat (R1)**: ✓.
- **Fit with current Annex B**: very low — replaces it.

### Option E — Wrap HTML/image in `application/mp4` single-sample track (audit suggestion)

- **Construction**: Package each HTML or PNG asset as an ISO-BMFF
  file containing one timed metadata sample (or one
  subtitle-style sample) whose sample data is the HTML or PNG
  bytes. Sub-MPD remains SPS-conformant with
  `mimeType="application/mp4"` and a vendor-namespaced
  `SupplementalProperty` declaring the underlying asset format.
- **DASH baseline ref**: §7.3 + RFC 4337 (application/mp4 is
  registered). §8.15 SPS conformant. Q1 + Q3 background.
- **Pros**: zero changes to chapter 5 carrier model. SPS-conformant
  by direct construction.
- **Cons**: **Listed for completeness only — explicitly rejected by
  Nicolas as over-engineering.** Packaging an HTML file as an
  ISO-BMFF single-sample track introduces ISOBMFF packaging in the
  ADS toolchain for a payload that is a flat HTTP URL in 99% of
  industry deployments. Adds runtime cost (packaging step on the
  ADS), build cost (sample-mapping convention to invent), and
  Player cost (unwrap ISOBMFF to extract bytes before rendering).
  None of these costs buy interoperability that a vendor extension
  doesn't already deliver via Annex F + foreign-namespace
  ignore-if-unknown.
- **Implementation complexity**: **High**. Defines a new
  single-sample-track sample-mapping convention that is itself
  a vendor extension (not standardised), so the
  "DASH-conformant" claim only holds in the trivial sense that
  the outer container is application/mp4.
- **Backward-compat (R1)**: ✓.
- **Fit with current Annex B**: medium — same shape, different
  inner content.

## Decision matrix

| Option | DASH-compliance | Implementation complexity | Backward-compat (R1) | Fit with Annex B |
|--------|-----------------|---------------------------|-----------------------|------------------|
| A — Inline `<svta:RenderableAsset>` | ✓ (§5.2.1 foreign-namespace extension; §8.14 regular Periods; sub-MPDs unaffected) | Low | ✓ (svta subtree opaque to legacy parsers) | High — local change to §5.6.2 and §B.4 |
| B — `SupplementalProperty` carrier | ✓ (§5.8.4.9 ignore-if-unknown) | Low | ✓ | Medium — generic descriptor where v2 prefers explicit svta elements |
| C — Tracking-only SPS sub-MPD | ✗ in naive form (§5.3.2.2 Table 4 forbids zero-AdaptationSet non-zero-duration Period); only ✓ via application/mp4 stub | Medium | ✓ | Medium — keeps `<ImportedMPD>` shape but reduces to Option E lite |
| D — Primary-MPD EventStream | ✓ (§5.10.2.3 + §5.10.4.5 pattern) | High | ✓ | Very low — replaces non-linear chapter 5 |
| E — Wrap in application/mp4 | ✓ (RFC 4337 / §7.3 / §8.15 trivially) | High | ✓ | Medium — same shape, different inner content. **Rejected by Nicolas as over-engineering.** |

## Recommendation

**Option A — Inline `<svta:RenderableAsset>` inside `<svta:Form>`
for non-video forms; `<ImportedMPD>` retained for video forms.**

Reasoning:

- **DASH-compliant by the strongest construction**: foreign-namespace
  open content model is the spec's own normative extension point
  (§5.2.1), invoked the same way the SGAI overlay scheme
  (`urn:svta:dash:sgai:2026`) is already invoked by v2. No
  ImportedMPD → no §5.3.2.6 SPS-coercion → no §7.3 RFC 4337
  collision.
- **Smallest change to the existing spec**: chapter 5 §5.5 / §5.6.2
  already commit the non-linear delivery model to
  svta-namespaced elements. Adding one more svta-namespaced child
  element (`<svta:RenderableAsset>`) is consistent with the
  existing v2 voice; switching to a generic
  `SupplementalProperty` (Option B) is not.
- **One-fetch on non-video forms**: removes a redundant HTTP
  round-trip per non-video form (ListMPD → sub-MPD that only carries
  one URL).
- **Backward-compat preserved**: the entire svta subtree is
  ignore-if-unknown to a legacy DASH client; nothing changes for
  R1 vs v2.
- **Scoping discipline**: Option A leaves the video form path
  (with `<ImportedMPD>` to an SPS sub-MPD) untouched. The fix is
  surgical to the non-video form path only.

The other options were rejected for:

- **Option B**: same DASH-compliance, lower readability fit with
  the v2 voice. No upside over A.
- **Option C**: §5.3.2.2 Table 4 mandates at least one
  AdaptationSet per non-zero-duration Period. The naive
  zero-AdaptationSet variant is non-conformant; the compliant
  variant requires an application/mp4 stub, which is Option E lite
  and re-introduces the rejected ISO-BMFF packaging cost.
- **Option D**: discards SGAI's ADS-driven decisioning for
  non-video forms. Not a tactical fix; a strategic regression.
- **Option E (application/mp4 wrap)**: explicitly rejected by
  Nicolas as over-engineering. Listed for completeness only.

## Sketch of the Annex B rewrite

The HTML form's per-form sub-MPD (current Annex B §B.4) is
**removed**. Annex B §B.3 (non-linear ListMPD) is updated so that
the HTML and image forms carry inline `<svta:RenderableAsset>`
children. The video form (`mediaType="video"`) keeps `<ImportedMPD>`
unchanged.

```xml
<!-- Annex B §B.3, illustrative — non-video forms use inline carriage -->
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     xmlns:svta="urn:svta:dash:sgai:2026"
     profiles="urn:mpeg:dash:profile:list:2024,urn:svta:dash:sgai-list:2026"
     type="list" minBufferTime="PT1S"
     publishTime="2026-05-12T10:00:00Z">
  <BaseURL>https://ads.example.com/delivery/</BaseURL>

  <Period id="cand-1" duration="PT20S">
    <svta:CandidateForms candidateId="cand-1" candidatePriority="80">
      <!-- HTML form: inline carriage, no ImportedMPD -->
      <svta:Form formId="cand-1-html" mediaType="html"
                 admissibleLayouts="corner-overlay,lower-third-overlay"
                 formPriority="100" duration="20000">
        <svta:RenderableAsset href="creatives/cand-1.html"
                              mimeType="text/html"/>
        <svta:TrackingEvents schemeIdUri="urn:mpeg:dash:event:callback:2015"
                             timescale="1000">
          <svta:Event presentationTime="0"     id="impression">
            https://tracker.example.com/impression?cand=1&amp;form=html
          </svta:Event>
          <svta:Event presentationTime="5000"  id="q1">
            https://tracker.example.com/q1?cand=1&amp;form=html
          </svta:Event>
          <!-- q2, q3, complete elided for brevity -->
        </svta:TrackingEvents>
      </svta:Form>

      <!-- Image form: inline carriage, no ImportedMPD -->
      <svta:Form formId="cand-1-image" mediaType="image"
                 admissibleLayouts="corner-overlay,lower-third-overlay,l-shape"
                 formPriority="70" duration="20000">
        <svta:RenderableAsset href="creatives/cand-1.png"
                              mimeType="image/png"/>
        <svta:TrackingEvents schemeIdUri="urn:mpeg:dash:event:callback:2015"
                             timescale="1000">
          <!-- impression + quartiles + complete; same shape -->
        </svta:TrackingEvents>
      </svta:Form>

      <!-- Video form: ImportedMPD as in v2 -->
      <svta:Form formId="cand-1-video" mediaType="video"
                 admissibleLayouts="corner-overlay"
                 formPriority="50" duration="20000">
        <ImportedMPD uri="creatives/cand-1-video.mpd"/>
      </svta:Form>
    </svta:CandidateForms>
  </Period>
</MPD>
```

Companion spec changes (out of scope here, but listed for the next
spec iteration):

- **Chapter 5 §5.5**: state explicitly that non-video forms
  (`mediaType ∈ {html, image}`) MUST use inline carriage via
  `<svta:RenderableAsset>` and MUST NOT use `<ImportedMPD>`. Video
  forms (`mediaType="video"`) MUST use `<ImportedMPD>`.
- **Chapter 5 §5.6.2**: add the `<svta:RenderableAsset>` element
  with `@href` and `@mimeType` attributes; add the
  `<svta:TrackingEvents>` container as the in-svta equivalent of
  the in-sub-MPD callback EventStream.
- **Chapter 5 §5.7**: re-scope the SPS conformance statement to
  apply only when `<ImportedMPD>` is used (i.e. video forms and
  linear ads).
- **Audit finding N-1 / N-2**: resolved.
- **Audit finding M-1** (ImportedMPD nesting inside `<svta:Form>`):
  now scoped to video forms only, but still needs the §5.6.2
  clarification proposed in the audit.

## Open questions

- **OQ-1 (resolved by Q9)**: A §8.15 SPS Period with zero
  AdaptationSet elements is non-conformant unless `Period@duration`
  is zero (§5.3.2.2 Table 4). Option C therefore dies in its naive
  form; the compliant variant collapses to Option E lite.
  Recommendation unaffected.
- **OQ-2 (resolved by Q10)**: `@mimeType` is mandatory (§5.3.7.2
  Table 16) but may be set on either AdaptationSet OR Representation
  (one of them must carry it). `@contentType="image"` is a valid
  enum value per `RFC6838ContentTypeType`, but inside an SPS sub-MPD
  the matching `@mimeType` is still bound to RFC 4337 (i.e. must be
  `application/mp4`-wrapped). Per-AdaptationSet `@profiles` is
  allowed but MUST be a subset of the MPD-level `@profiles`
  (§5.3.7.2 Table 16) — so an SPS-rooted sub-MPD cannot have a
  single AdaptationSet that "pulls in" Full profile to escape RFC
  4337. No back-door. Recommendation unaffected; this just closes
  the last loophole-hunting question.
- **OQ-3 (still open from the audit)**: `MPD@profiles` comma vs
  space delimiter — the audit's M-4. Independent of this research.
- **OQ-4 (still open from the audit)**: `@earliestResolutionTimeOffset`
  semantics on nested `<svta:Form>` (audit's M-1). The
  recommendation narrows the scope of M-1 to video forms only, but
  does not resolve it. The next spec iteration should pin the
  semantics for the video-form case.

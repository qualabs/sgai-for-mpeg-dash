[GROUNDED_BY=notebooklm+spec-audit]

# Errata 1 — Backward compatibility of video form wrapping under Option A

**Target**: `output/2026-05-14-non-video-carrier-research.md`.
**Trigger**: Nicolás Levy (2026-05-14) queried whether wrapping
`<ImportedMPD>` inside `<svta:Form>` for video forms preserves R1
(backward compatibility with legacy DASH players). The intuition was
that legacy parsers, skipping the entire `<svta:Form>`
foreign-namespace subtree, would also skip the inner `<ImportedMPD>`,
breaking R1 for the video case.
**Reference**: MPEG-DASH 6th edition (ISO/IEC 23009-1:2025).
**Method**: spec-v2 audit + targeted NotebookLM query against the
DASH-6th notebook. 5 queries planned; 1 returned a clean grounded
answer (Q3, the critical one); 4 failed due to a stale browser
session and a parallel-launch race. The Q3 answer is sufficient to
settle the question; the remaining queries would have confirmed the
same point from different angles.

## 1. Spec v2 audit

**Conclusion**: Nicolás's intuition about the parser behaviour is
correct, **but it does NOT identify a regression introduced by
Option A**. The v2 spec **already** wraps `<ImportedMPD>` inside
`<svta:Form>` for **every** form — video, image, and HTML.

Evidence from `output/2026-05-12-sgai-spec.md`:

- **§5.6.2 (line 629-631)**: "Each `<svta:Form>` element contains
  exactly one `<ImportedMPD>` child linking to the per-form sub-MPD
  (constrained to SPS per §5.5.1 above)." No carve-out for video.
- **§5.6.2 inline example (lines 638-647)**: HTML and image forms
  shown, both with `<ImportedMPD>` as a child of `<svta:Form>`.
- **Annex B §B.3 (lines 1197-1216)**: The full non-linear ListMPD
  example shows three forms in candidate `cand-1` — HTML, image, and
  **video** — and **all three** carry `<ImportedMPD>` inside
  `<svta:Form>`. Same shape in Annex C (overlay video form, line
  1346-1350) and Annex D (pause-ad video form, line 1416-1420).
- **§7.5 / Annex E.3 (lines 1488-1498)**: The spec **already
  acknowledges and accepts** the legacy-parser consequence. Annex
  E.3 (T-E3) reads verbatim: *"in the non-linear shape there is no
  `<ImportedMPD>` at the `<Period>` level (it lives inside
  `<svta:Form>`), so the Period yields no referenceable ad MPD. The
  Player treats the Period as a no-fill entry and falls through to
  primary content. No tracking beacon is fired."* This applies
  uniformly to all forms, including video.
- **Conformance audit `output/2026-05-12-dash-conformance-audit.md`
  C-08 (line 57)**: explicitly catalogs `<ImportedMPD>` inside
  `<svta:Form>` as Marginal and notes *"Legacy parsers are
  unaffected (whole svta subtree is opaque)."*
- **Conformance audit C-25 (line 74)**: explicitly: *"A non-linear
  Period with neither standard ImportedMPD nor any AdaptationSet is
  technically a 'regular Period that yields nothing' to a legacy
  parser, which then falls through to no-fill (annex E §E.3)."*
- **Conformance audit M-1 (lines 156-176)**: documents the same
  nesting issue at length. Calls it "schema-valid" but flags the
  semantic-equivalence rule SGAI-aware Players need.

The v2 spec design choice is therefore: **legacy clients never
render any non-linear ad** (linear or video), regardless of form
class. R1 is satisfied by graceful no-fill, not by handing legacy
clients a baseline `<ImportedMPD>` they could process. This is the
status quo.

## 2. DASH 6th edition validation (NotebookLM)

**Q3 (one query landed; the critical one)** confirms the legacy
parser behaviour normatively.

The DASH 6th edition §5.2.1 says (quoted verbatim from the notebook
answer):

> *"In addition, the MPD shall be authored such that, after XML
> attributes or elements in the other namespaces than the DASH
> namespace are removed, the result is a valid XML document
> formatted according to that schema and that conforms to this
> document."*

NOTE 2 in the same section confirms parser behaviour:

> *"if DASH Clients remove all XML attributes and elements from the
> MPD in the DASH namespace and in other namespaces that are not in
> the XML schema documented in Annex B, the MPD results in a valid
> XML document which complies with this document. The DASH Client
> can use such a resulting MPD for presentation of a conforming
> Media Presentation."*

The notebook answer is explicit about descent: *"The DASH
specification does not contain any rule or instruction suggesting
that a parser should descend into an unknown foreign-namespace
element to look for known DASH children. ... the entire XML node —
including its subtree of children — is cleanly discarded."*

**Bottom line on Nicolás's question**: when a legacy DASH-6th
parser encounters `<svta:Form>` (a foreign-namespace element under
`<Period>`), it removes that entire element including any baseline
children. The inner `<ImportedMPD>` is **not** processed. This is
true for video, image, and HTML forms equally.

Queries Q1, Q2, Q4, Q5 failed (the browser session is 8 days stale,
and the first parallel launch held the Chromium profile singleton,
killing the others). They are noted as `[fetch-failed]`; Q3 alone is
load-bearing for the conclusion.

## 3. Reconciliation: does Option A as written break R1?

**Outcome (a) — no regression introduced by Option A.**

Reasoning:

- The video-form `<ImportedMPD>` was already nested inside
  `<svta:Form>` in v2 (§5.6.2; Annex B §B.3 video form;
  Annexes C, D).
- A legacy parser, per §5.2.1, removes the entire `<svta:Form>`
  subtree, including the baseline `<ImportedMPD>` it contains.
- This is true of **every** form class in v2 — video included.
- Option A in the 2026-05-14 research report preserves this for
  video forms (it explicitly states *"Video forms keep
  `<ImportedMPD uri="creatives/cand-1.mpd"/>` as in v2"*, line
  113-114) and changes only how non-video forms are carried (inline
  `<svta:RenderableAsset>` instead of nested `<ImportedMPD>`).
- Therefore Option A's video-form path is **byte-identical to v2's
  video-form path** in terms of R1 behaviour: legacy parser
  encounters `<svta:CandidateForms>` under `<Period>`, removes the
  whole subtree, sees a `<Period>` with no baseline children, falls
  through to no-fill. Same outcome as v2.

**What Nicolás's critique correctly identifies, even if it doesn't
target a regression**: the v2 / Option A design **does not deliver
R1 in the strong "legacy players still see the ad" sense**. R1 is
satisfied in v2 only in the weaker "legacy players play primary
content uninterrupted" sense. The spec is internally consistent
about this (§7.5, Annex E.3) but the report's Option A pros section
(line 126-130) overstates the case slightly: it says *"A legacy
Player that doesn't understand svta schemes never sees the non-video
form, so there is no inadvertent rendering"* — that's true, but the
broader fact is that **a legacy Player never sees any non-linear
form, video included**, in both v2 and Option A. The pro is correctly
stated but reads as if non-video is the special case, when in fact
the whole non-linear path is opaque to legacy.

**Strict reading**: Option A introduces zero regression on R1
relative to v2. The critique is well-aimed but does not bind on
Option A specifically — it binds on the v2 design choice from §5.6.2.

## 4. Corrective proposal: not required for Option A; optional v3 follow-up

Because the answer is outcome (a), the research report does **not**
require an "Option A — hybrid" variant to ship. Option A as written
is correct on R1.

That said, **if** the project later decides to deliver R1 in the
strong "legacy plays video forms via baseline DASH" sense, the
construction Nicolás's intuition implies is sound and would be a v3
deliverable, not an Option A errata. Sketched here for the record:

```xml
<!-- v3 hybrid sketch (NOT applied in Option A v1) -->
<Period id="cand-1" duration="PT20S">
  <!-- Baseline DASH path: legacy parsers reach this directly -->
  <ImportedMPD uri="creatives/cand-1-fallback-video.mpd"/>

  <!-- SGAI-aware path: legacy parsers remove this whole subtree
       (§5.2.1) and use the ImportedMPD above; enhancement-aware
       parsers use this and ignore the fallback. -->
  <svta:CandidateForms candidateId="cand-1" candidatePriority="80">
    <svta:Form formId="cand-1-html" mediaType="html" ...>
      <svta:RenderableAsset href="creatives/cand-1.html"
                            mimeType="text/html"/>
    </svta:Form>
    <svta:Form formId="cand-1-image" mediaType="image" ...>
      <svta:RenderableAsset href="creatives/cand-1.png"
                            mimeType="image/png"/>
    </svta:Form>
    <svta:Form formId="cand-1-video" mediaType="video" ...>
      <ImportedMPD uri="creatives/cand-1-video.mpd"/>
    </svta:Form>
  </svta:CandidateForms>
</Period>
```

The sibling `<ImportedMPD>` at Period level is the
"legacy-visible fallback ad" — typically the best video form
(`cand-1-video.mpd`) duplicated. Legacy clients play it as a
linear-style ad in the slot. Enhancement-aware clients ignore the
Period-direct `<ImportedMPD>` in favour of the candidate-set
machinery inside `<svta:CandidateForms>`.

**Trade-offs of the v3 hybrid** (for the record, not endorsing):

- **Pro**: legacy DASH-6th clients get a renderable ad (only for
  candidates whose top video form is suitable as a standalone ad).
- **Con**: requires the ADS to also publish a "best video fallback"
  per candidate, doubling some manifests.
- **Con**: the slot type matters. `<svta:OverlayPresentation>` is
  not a linear-replacement; pointing a Period-direct `<ImportedMPD>`
  at it tells a legacy DASH-6th client to do something the slot was
  not declared as. The Broadcaster's primary MPD declared an
  overlay, not a replace; a legacy client cannot turn an overlay
  into a replace just because the Period contains an `<ImportedMPD>`.
- **Con**: the legacy fallback is not even reached for the
  non-linear path, because a legacy DASH-6th client never resolves
  the ADS URL in the first place (the `<EventStream>` carrying
  `<svta:OverlayPresentation>` uses an unknown scheme URI; per
  §5.10.1 the whole `<EventStream>` is ignored — see audit Q2).
  So **the legacy client never receives the non-linear ListMPD at
  all**, which means any Period-level fallback inside that ListMPD
  is unreachable.

That last point is decisive: the strong-R1 hybrid is **not just
unnecessary, it is unreachable**. A legacy DASH-6th client never
fetches the non-linear ListMPD because it never recognises the
`<svta:OverlayPresentation>` / `<svta:PauseAdPresentation>` event
scheme on the Broadcaster's primary MPD. Whatever the non-linear
ListMPD says about Period-level fallbacks is irrelevant.

**Conclusion on the hybrid**: it is technically buildable, but the
graceful-degradation chain breaks one level higher (at the primary
MPD's unknown event scheme), so the v3 hybrid would not actually
deliver renderable legacy ads. The v2 / Option A design — legacy
plays primary content uninterrupted, no ad — is in fact the only
honest R1 the non-linear path can offer.

## 5. Impact on the research report

**Severity**: errata-level. No re-publish needed.

The research report's Option A is correct on R1; the wording in two
places can be tightened to head off the same misreading next time.

Proposed edits to `output/2026-05-14-non-video-carrier-research.md`
(to be applied by a separate subagent, pending Nicolás's review):

- **Section "Option A — Inline form in `<svta:Form>`", Pros bullet
  about backward-compat (lines 126-130)**: rephrase to make the
  scope explicit. Suggested replacement text:

  > *"Backward-compat with legacy Players (R1) is unchanged from v2:
  > a legacy DASH-6th parser, per §5.2.1, removes the entire
  > `<svta:CandidateForms>` subtree (including any nested
  > `<ImportedMPD>` for video forms), and per §5.10.1 never
  > resolves the non-linear slot's ADS URL in the first place (the
  > `<EventStream>` carrying `<svta:OverlayPresentation>` /
  > `<svta:PauseAdPresentation>` uses an unknown scheme). The legacy
  > Player therefore never reaches the non-linear ListMPD and never
  > sees any form — video, image, or HTML. R1 is satisfied by no-fill
  > graceful degradation, identical to v2 (see §7.5 / Annex E.3 of
  > the v2 spec)."*

- **Section "Sketch of the Annex B rewrite" / video form comment
  (lines 384-389)**: the inline comment `<!-- Video form:
  ImportedMPD as in v2 -->` is correct but does not address the
  obvious reader question "doesn't legacy skip the whole svta
  subtree?". Add a one-line note immediately below the video form
  block:

  > *"Note: legacy DASH-6th clients remove the entire
  > `<svta:CandidateForms>` subtree per §5.2.1, including this
  > nested `<ImportedMPD>`. This is consistent with v2 — see §7.5
  > and Annex E.3. R1 is delivered upstream, on the primary MPD,
  > where the unknown event scheme on the slot's `<EventStream>`
  > causes the legacy Player to never fetch the non-linear ListMPD."*

- **(Optional) "Open questions" section**: add OQ-5 noting that the
  v3 strong-R1 hybrid is unreachable (the legacy client doesn't get
  to the ListMPD), so it should not be pursued unless the
  Broadcaster's primary MPD also moves to a baseline event scheme —
  which is a much larger redesign out of scope here.

These are textual clarifications, not technical corrections. The
Option A recommendation and the Annex B sketch stand as written.

## Open questions surfaced

- **OQ-5 (new)**: If a future iteration wants legacy DASH-6th
  clients to play *some* ad in non-linear slots, the lever is not
  the non-linear ListMPD shape — it is the Broadcaster's primary
  MPD's `<EventStream>` scheme. Replacing
  `urn:svta:dash:sgai-overlay:2026` with a baseline AlternativeMPD
  scheme would route legacy clients through the linear flow and let
  them render a fallback `<ImportedMPD>`-resolved video ad. This is
  a chapter-5-wide redesign and is explicitly out of scope here;
  flagging it for the v3 roadmap.
- **OQ-6 (new)**: NotebookLM Q4/Q5 (preferred-pattern guidance for
  sibling-vs-nested vendor extensions) did not return. If a later
  session refreshes the NotebookLM auth, those queries should be
  re-issued to confirm there is no normative DASH-6th recommendation
  to prefer the sibling pattern. The Q3 answer makes the parser
  behaviour unambiguous regardless of which pattern is used, so
  OQ-6 is informational, not blocking.
- The existing OQs in the v1 report (OQ-1..OQ-4) are unaffected.

[STATUS=proposal-draft]

# Context guidance proposal — extracting DASH 6th edition design-space rules into context/

**Source**: `output/2026-05-14-non-video-carrier-research.md` (commit `63033d7`) plus
`output/2026-05-14-non-video-carrier-research-errata-1.md` (same date).
**Trigger**: Nicolás (2026-05-14) asked what should live in `context/` so a clean spec
re-build converges to the Option A construction without repeating the research.
**Scope**: PROPOSAL only — no `context/` files are modified. Nicolás decides what to apply.

## Why this matters

The research lives in `output/`, but the build pipeline reads `context/`. Without
explicit guidance there, the next clean re-build lacks the §5.3.2.6 / §8.15 / §7.3 /
RFC 4337 chain and may converge to the v2 sub-MPD shape (audit findings N-1/N-2) or to
Option E (the `application/mp4` wrap Nicolás rejected as over-engineering). This proposal
embeds the **design-space-closing rules** the research surfaced into `context/`, phrased
as DASH normative constraints, so the builder picks the foreign-namespace open content
construction on its own.

Phrasing rule (strict): each rule states **what DASH allows or forbids**, not **which
Option to pick**. The builder, reading R1..R13 plus DR-1..DR-7, arrives at Option A
because every other carrier path is closed by an explicit rule. We never write "use
`<svta:RenderableAsset>`" in `context/`.

## Design-space-closing rules to embed in context/

### DR-1 — SPS conformance is structurally inescapable for any document reached via `<ImportedMPD>`

- **Source**: research §"Re-validation of the §8.15 SPS constraint", §5.3.2.6 + §8.15.
- **Phrasing**: "Any MPD reached via `<ImportedMPD>` is normatively bound (§5.3.2.6) to
  the Single Period Stream (SPS) profile (§8.15). SPS inherits §7.3 verbatim, which
  constrains every Representation's `@mimeType` to the IETF RFC 4337 registry —
  `video/mp4`, `audio/mp4`, `application/mp4`. A vendor profile URI MAY be appended in
  `@profiles`, but the document still has to satisfy the SPS intersection: vendor
  profiles can only ADD constraints, never relax them. There is no extension point inside
  SPS for non-MP4 MIME types."
- **Why generic**: closes the design space around sub-MPDs without naming a carrier.

### DR-2 — Foreign-namespace open content is DASH's normative extension point for new XML constructs

- **Source**: research Option A discussion of §5.2.1; errata-1 §2 Q3.
- **Phrasing**: "DASH §5.2.1 is the normative extension point for new XML elements and
  attributes from non-DASH namespaces. The MPD schema declares
  `<xs:any namespace='##other' processContents='lax'/>` on every container, so a
  foreign-namespace element MAY appear as a child of any DASH container (including
  `<Period>`, `<AdaptationSet>`, `<Event>`, and other foreign-namespace elements). The
  MPD MUST be authored such that, after foreign-namespace attributes and elements are
  removed, the result is still a valid DASH document conforming to this specification."
- **Why generic**: states the mechanism, not what to put in it. The builder picks this
  carrier because R1 + R8 + R9 + the alternatives being closed by DR-1/DR-4/DR-6 force it.

### DR-3 — Legacy parsers discard foreign-namespace subtrees entirely (no descent into baseline children inside foreign elements)

- **Source**: errata-1 §2 (§5.2.1 NOTE 2, NotebookLM Q3).
- **Phrasing**: "A DASH client that does not implement the foreign namespace removes the
  **entire** XML node including its subtree of children (§5.2.1, NOTE 2). The spec
  contains no rule suggesting a parser should descend into an unknown foreign-namespace
  element to look for known DASH children. **Consequence**: a baseline DASH element
  wrapped inside a foreign-namespace element is invisible to legacy clients. Authoring
  rule: baseline children that legacy clients are expected to process go at a baseline
  (non-foreign) position; baseline children that should be hidden from legacy go inside
  the foreign-namespace subtree."
- **Why generic**: most load-bearing rule. Tells the builder how to choose between "wrap
  baseline element in foreign namespace" (legacy hides it, no-fill path) vs "place as
  sibling" (legacy sees it, fallback path). Both Option A's video-form behaviour and
  errata-1 §4's v3 hybrid sketch hinge on it.

### DR-4 — Annex F is the only normative DASH path to non-ISO-BMFF delivery formats; requires a new Interoperability Point URI

- **Source**: research §"Re-validation of the §8.15 SPS constraint", §F.2 + §8.1.
- **Phrasing**: "DASH Annex F (informative) describes how to extend DASH with non-
  ISO-BMFF delivery formats. F.2 requires that a custom format's authoring rules define
  a MIME type for the Representation formed as Segment concatenation, and that a new
  **Interoperability Point URI** be declared in `MPD@profiles` (§8.1). No spec-defined
  image profile, HTML profile, or thumbnail profile exists in DASH 6th. Introducing one is
  a full Annex F exercise (new profile URI, new authoring rules, new conformance
  criteria) — heavier than §5.2.1 foreign-namespace for an attribute that is a flat HTTP
  URL to a renderable asset."
- **Why generic**: enumerates Annex F and its cost. Cost is enough to deprioritise it
  against §5.2.1 for static asset URLs — no "do not use Annex F" needed.

### DR-5 — AdaptationSet / Representation axis is closed for non-MP4 MIME types throughout the ListMPD path

- **Source**: research §"Re-validation", §8.14 + §8.12; OQ-2 on §5.3.7.2 Table 16.
- **Phrasing**: "Inline `<AdaptationSet>` / `<Representation>` inside a ListMPD-level
  `<Period>` (§8.14 regular Periods) inherits the ListMPD profile, formally an extension
  of the ISO-BMFF CMAF profile (§8.12). Such inline elements inherit the same RFC 4337
  constraint on `@mimeType`. Per-AdaptationSet `@profiles` MUST be a subset of MPD-level
  `@profiles` (§5.3.7.2 Table 16), so an SPS-rooted document cannot promote a single
  AdaptationSet to a broader profile to escape RFC 4337. **Consequence**: no
  AdaptationSet-shaped carrier exists for non-MP4 assets anywhere in the ListMPD flow."
- **Why generic**: closes the AdaptationSet axis end-to-end when read with DR-1.

### DR-6 — Three DASH-conformant carriers exist for non-AV ad assets

- **Source**: research §"Re-validation", closing summary.
- **Phrasing**: "Given DR-1, DR-4, and DR-5, the only DASH-conformant carriers for
  non-AV (non-MP4) ad assets are: (a) foreign-namespace open content under §5.2.1 — a
  new element in `urn:svta:dash:*` carrying the asset URL as an attribute; (b)
  application-level Event Streams under §5.10 — an `<Event>` whose `text()` carries an
  inline payload (the callback scheme §5.10.4.5 already uses this pattern); (c) vendor
  descriptors under §5.8.4.8 / §5.8.4.9 — a scheme URI with `@value` carrying the asset
  URL string (placement is constrained to AdaptationSet / Representation /
  Sub-Representation, so this carrier inherits DR-5's MIME constraint unless hosted
  inside a foreign-namespace parent, which collapses (c) into (a) with worse
  readability)."
- **Why generic**: enumerates the closed design space. Builder picks (a)/(b)/(c) on fit
  (one-fetch vs round-trip, named element vs descriptor, presentation-time alignment vs
  static attribute).

### DR-7 — Non-zero-duration Periods MUST contain at least one AdaptationSet

- **Source**: research §"Option C", OQ-1; §5.3.2.2 Table 4.
- **Phrasing**: "§5.3.2.2 Table 4 requires at least one AdaptationSet in each Period
  unless `Period@duration` is zero. An SPS Period containing only an `<EventStream>` (no
  AdaptationSet) is non-conformant for any non-zero duration. A slot whose tracking
  requires presentation-time alignment across non-zero duration MUST therefore carry at
  least one AdaptationSet (which inherits DR-1/DR-5) or carry the asset and tracking
  outside any Period the spec defines as non-zero-duration."
- **Why generic**: closes the "empty-Period tracking carrier" variant (Option C naive).

## Proposed edits per file

### NEW — `context/08-dash-extension-rules.md` (~80 lines)

Sits between `06-naming-and-namespaces.md` (URI policy) and
`07-backward-compat-checklist.md` (per-construct verification). `07` already cites "the
DASH extension rule" without naming it; `08` becomes the file `07` cites. Sketch:

```
# DASH 6th edition extension rules

> Normative constraints that bind any new construct the SGAI spec introduces into
> DASH 6th edition (ISO/IEC 23009-1:2025). Design-space layer consumed by
> 07-backward-compat-checklist.md (verification) and the spec's chapter 5 (carrier
> choice).

## DR-1 — SPS conformance is structurally inescapable for sub-MPDs
[body from this proposal]
## DR-2 — Foreign-namespace open content is the normative extension point
[body]
## DR-3 — Legacy parsers discard foreign-namespace subtrees entirely
[body; most load-bearing]
## DR-4 — Annex F path requires a new Interoperability Point URI
[body]
## DR-5 — AdaptationSet / Representation axis is closed for non-MP4
[body]
## DR-6 — Three DASH-conformant carriers for non-AV assets
[body; enumeration with fit notes]
## DR-7 — Non-zero-duration Periods MUST contain at least one AdaptationSet
[body]

## Cross-refs
- 03-requirements.md — R1, R6, R8, R9.
- 07-backward-compat-checklist.md — applies DR-2/DR-3 per construct.
- 06-naming-and-namespaces.md — URI patterns for DR-2 elements.
```

### EDIT — `context/03-requirements.md`

- **R1.2 expansion** (lines 36-42): replace the generic "MUST be expressed using a
  MPEG-DASH 6th edition extension point" with:

  > *"R1.2 (Broadcaster / spec document): Every new SGAI construct MUST be expressed
  > using one of the extension points enumerated in `08-dash-extension-rules.md`:
  > foreign-namespace open content (§5.2.1, DR-2/DR-3), application-level Event Streams
  > (§5.10), or vendor descriptor schemes (§5.8.4.8 / §5.8.4.9). New constructs MUST NOT
  > be introduced by paths that violate the §5.3.2.6 / §8.15 / §7.3 / RFC 4337 chain
  > when reached via `<ImportedMPD>` (DR-1) or by inline AdaptationSet / Representation
  > under a ListMPD-level Period (DR-5). Annex F (DR-4) is admissible only when (a) the
  > construct genuinely requires DASH segment delivery semantics for a non-ISO-BMFF
  > format, and (b) the spec is willing to publish a new Interoperability Point URI."*

- **R6.6 new** (after line 200): "When a non-AV ad form (`mediaType ∈ {html, image, …}`)
  is carried, the asset URL MUST NOT be expressed as `@mimeType` on an AdaptationSet or
  Representation reached through any path bound by RFC 4337 (DR-1, DR-5). It MUST be
  carried via one of the §5.2.1 / §5.10 / §5.8.4.x carriers per R1.2."

### EDIT — `context/05-dash-linear-interfaces.md`

After "Reference XML: main MPD with SGAI events", before VAST → ListMPD. ~6 lines:

> *"The interfaces above are sufficient for **linear** SGAI, where the ad's renderable
> asset is an ISO-BMFF presentation by construction (the `<ImportedMPD>`-reached sub-MPD
> is SPS-conformant under §8.15, bound by RFC 4337). For **non-linear** ads — where the
> form's renderable asset may be HTML, an image, or another non-AV payload — the
> AdaptationSet / Representation axis under `<ImportedMPD>` is closed for non-MP4 MIME
> types (DR-1, DR-5). The non-linear chapters MUST therefore carry non-AV asset URLs
> outside the AdaptationSet axis, via one of the carriers enumerated in DR-6."*

### EDIT — `context/06-naming-and-namespaces.md`

Under "Element / attribute extension namespaces" (lines 64-83). Replace the trailing
"Legacy Players MUST ignore unknown namespaces under DASH's extension rules (per R1)"
with a concrete pointer to DR-2/DR-3:

> *"Elements in the SVTA Ads WG extension namespace operate under DASH §5.2.1
> foreign-namespace open content (DR-2 in `08-dash-extension-rules.md`). Legacy DASH
> clients discard such elements **with their full subtree** (DR-3) — baseline DASH
> children nested inside a foreign-namespace element are not seen by legacy clients.
> Authoring decision applies (see DR-3)."*

### EDIT — `context/07-backward-compat-checklist.md`

- **Item 2** (lines 34-47): replace the loose "typically the open-content model rule"
  with a pointer to DR-2/DR-3/DR-1/DR-4 in `08`. Require each construct chapter to cite
  which DR-N applies.
- **New Item 8 (Carrier classification)**: "Classify the construct's carrier against
  DR-6: (a) foreign-namespace open content, (b) Event Stream payload, or (c) descriptor
  scheme. Constructs not fitting (a)/(b)/(c) MUST justify why Annex F (DR-4) is invoked
  and what new Interoperability Point URI is published."
- **Anti-patterns** (lines 119-133): add "Placing a non-MP4 `@mimeType` on an
  AdaptationSet or Representation reached via `<ImportedMPD>` or inside a ListMPD-level
  Period (violates DR-1 / DR-5)."

### EDIT — `context/99-glossary.md`

Five new entries, one sentence each:

- **SPS (Single Period Stream)**: DASH 6th profile (§8.15) constraining sub-MPDs reached
  via `<ImportedMPD>` to a single Period plus the RFC 4337 `@mimeType` registry on every
  Representation. See DR-1.
- **ImportedMPD**: DASH element importing an external MPD by URI; §5.3.2.6 binds the
  imported document to SPS.
- **Foreign-namespace open content**: DASH §5.2.1 mechanism allowing XML from non-DASH
  namespaces under any DASH container. Legacy clients discard such elements with their
  full subtree (DR-3).
- **Interoperability Point URI** *(DASH Annex F)*: a profile URI in `MPD@profiles`
  advertising conformance to a DASH extension authored under Annex F. Required when a
  custom delivery format is introduced for AdaptationSet / Representation carriage.
- **Sub-MPD**: an MPD reached via `<ImportedMPD>` from a parent ListMPD or primary MPD;
  SPS-conformant (DR-1).

## Generic-not-prescriptive framing — convergence trace

The builder, reading R1 + R6 + R8 + R9 + R1.2 expanded + R6.6 new + DR-1..DR-7, ranks
carriers per construct without us naming one. For the non-video form: DR-1 + DR-5 close
the AdaptationSet axis (kills v2 sub-MPD shape, Option C, inline AdaptationSet in
ListMPD-level Period); DR-4 deprioritises Annex F (heavy for a flat HTTP URL); DR-6
enumerates three valid carriers and DR-2/DR-3 make foreign-namespace the lightest when
the URL is a static attribute; R8/R9 prefer reusing the same extension mechanism the spec
already uses for `urn:svta:dash:sgai:2026`. We never write "use Option A" — the builder
arrives there because every other path is closed.

## Dependencies / risks

- **Errata-1 committed** (`output/2026-05-14-non-video-carrier-research-errata-1.md`).
  Outcome **(a) — no regression introduced by Option A**. DR-3's phrasing explicitly
  supports the dual reading errata-1 surfaced (foreign-namespace subtrees discarded with
  all baseline children inside them — what makes Option A's video-form path opaque to
  legacy, identical to v2). No DR-N changes from errata-1.
- **Edition-binding**: each DR-N is anchored to a specific DASH §. `08` MUST carry an
  explicit "DASH 6th edition" header and the rules MUST be re-validated on edition bump,
  not blindly carried.
- **R1.2 enumeration narrows admissible extension points**: future constructs needing an
  extension point not in the list MUST update R1.2 explicitly. Right governance, not a bug.
- **DR-6's three-carrier enumeration is edition-bound**: a future DASH edition adding a
  fourth normative extension point invalidates DR-6 as written.

## Recommendation (prioritised for Nicolás)

1. **Highest leverage — NEW `context/08-dash-extension-rules.md`**: without this file, R1
   stays generic ("use a DASH extension point") and the builder has no anchor for choosing
   among them. ~80 lines.
2. **Second — EDIT `context/03-requirements.md`** to expand R1.2 (admissible extension
   points) and add R6.6 (non-AV asset URL constraint). These make `08` enforceable from
   the requirements side. ~20 lines added.
3. **Third — EDIT `context/07-backward-compat-checklist.md`** (point Item 2 at `08`, add
   Item 8, add the anti-pattern). ~10 lines added.
4. **Nice-to-have — EDIT `context/05-dash-linear-interfaces.md`** (one paragraph) and
   `context/06-naming-and-namespaces.md` (one paragraph). Small; improve consistency.
5. **Lowest priority — EDIT `context/99-glossary.md`** with five new entries. Readability
   only.

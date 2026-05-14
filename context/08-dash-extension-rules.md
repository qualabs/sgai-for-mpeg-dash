# DASH 6th edition extension rules

This document collects the DASH 6th edition rules that constrain how
SGAI extends the standard. Each rule (DR-N) is normative for the SGAI
design: builders consulting this file should treat the rules as
design-space-closing facts. The rules describe what DASH allows or
forbids; they do not pick a specific construction. The builder,
reading R1 + DR-1..DR-N together, will converge to a DASH-conformant
solution on its own.

Edition binding: every DR-N below is anchored to a specific section
of ISO/IEC 23009-1 6th edition. On any edition bump, this file MUST
be re-validated section by section — rules are not blindly carried
forward.

## DR-1 — SPS conformance is structurally inescapable for any document reached via `<ImportedMPD>`

Any MPD reached via `<ImportedMPD>` is normatively bound (§5.3.2.6)
to the Single-Period Static (SPS) profile (§8.15). SPS inherits §7.3
verbatim, which constrains every Representation's `@mimeType` to the
IETF RFC 4337 registry — `video/mp4`, `audio/mp4`, `application/mp4`.
A vendor profile URI MAY be appended in `@profiles`, but the document
still has to satisfy the SPS intersection: vendor profiles can only
ADD constraints, never relax them. There is no extension point inside
SPS for non-MP4 MIME types.

- **Source**: §5.3.2.6, §8.15, §7.3, IETF RFC 4337.
- **Implication for SGAI**: a sub-MPD referenced from a ListMPD via
  `<ImportedMPD>` cannot carry a non-MP4 ad asset on an AdaptationSet
  or Representation. Non-AV ad assets MUST be carried via one of the
  carriers enumerated in DR-6.

## DR-2 — Foreign-namespace open content is DASH's normative extension point for new XML constructs

DASH §5.2.1 is the normative extension point for new XML elements
and attributes drawn from non-DASH namespaces. The MPD schema
declares `<xs:any namespace='##other' processContents='lax'/>` on
every container, so a foreign-namespace element MAY appear as a
child of any DASH container (including `<Period>`,
`<AdaptationSet>`, `<Event>`, and other foreign-namespace
elements). The MPD MUST be authored such that, after foreign-
namespace attributes and elements are removed, the result is still
a valid DASH document conforming to this specification.

- **Source**: §5.2.1.
- **Implication for SGAI**: new XML constructs introduced by SGAI
  under the SVTA Ads WG namespace (`urn:svta:dash:sgai:<year>`)
  operate within §5.2.1. The construction does not need a new
  profile URI to be DASH-conformant.

## DR-3 — Legacy parsers discard foreign-namespace subtrees entirely (no descent into baseline children inside foreign elements)

A DASH client that does not implement the foreign namespace removes
the **entire** XML node including its subtree of children (§5.2.1,
NOTE 2). The spec contains no rule suggesting a parser should
descend into an unknown foreign-namespace element to look for known
DASH children. Consequence: a baseline DASH element wrapped inside
a foreign-namespace element is invisible to legacy clients.
Authoring rule: baseline children that legacy clients are expected
to process go at a baseline (non-foreign) position; baseline
children that should be hidden from legacy go inside the foreign-
namespace subtree.

- **Source**: §5.2.1 NOTE 2.
- **Implication for SGAI**: chooses the placement of any baseline
  DASH element appearing alongside SGAI extensions. Wrapping a
  baseline element inside a foreign-namespace parent is the
  authoring move that hides it from legacy clients; placing it as
  a sibling is the move that exposes it.

## DR-4 — Annex F is the only normative DASH path to non-ISO-BMFF delivery formats; requires a new Interoperability Point URI

DASH Annex F (informative) describes how to extend DASH with non-
ISO-BMFF delivery formats. F.2 requires that a custom format's
authoring rules define a MIME type for the Representation formed as
Segment concatenation, and that a new **Interoperability Point
URI** be declared in `MPD@profiles` (§8.1). No spec-defined image
profile, HTML profile, or thumbnail profile exists in DASH 6th.
Introducing one is a full Annex F exercise (new profile URI, new
authoring rules, new conformance criteria) — heavier than §5.2.1
foreign-namespace for an attribute that is a flat HTTP URL to a
renderable asset.

- **Source**: Annex F (F.2), §8.1.
- **Implication for SGAI**: admissible only when the construct
  genuinely requires DASH segment-delivery semantics for a non-
  ISO-BMFF format AND the spec is willing to publish a new
  Interoperability Point URI. For flat HTTP URLs to renderable
  assets the cost is not justified.

## DR-5 — AdaptationSet / Representation axis is closed for non-MP4 MIME types throughout the ListMPD path

Inline `<AdaptationSet>` / `<Representation>` inside a ListMPD-
level `<Period>` (§8.14 regular Periods) inherits the ListMPD
profile, formally an extension of the ISO-BMFF CMAF profile
(§8.12). Such inline elements inherit the same RFC 4337 constraint
on `@mimeType`. Per-AdaptationSet `@profiles` MUST be a subset of
MPD-level `@profiles` (§5.3.7.2 Table 16), so an SPS-rooted
document cannot promote a single AdaptationSet to a broader
profile to escape RFC 4337. Consequence: no AdaptationSet-shaped
carrier exists for non-MP4 assets anywhere in the ListMPD flow.

- **Source**: §8.14, §8.12, §5.3.7.2 Table 16.
- **Implication for SGAI**: combined with DR-1, the AdaptationSet
  / Representation axis is closed end-to-end for non-MP4 assets.
  Non-AV ad assets cannot be hosted on that axis whether the
  containing Period is inside the ListMPD root or inside a sub-MPD
  reached via `<ImportedMPD>`.

## DR-6 — Three DASH-conformant carriers exist for non-AV ad assets

Given DR-1, DR-4, and DR-5, the only DASH-conformant carriers for
non-AV (non-MP4) ad assets are:

- **(a) Foreign-namespace open content under §5.2.1** — a new
  element in `urn:svta:dash:*` carrying the asset URL as an
  attribute. One-fetch, static.
- **(b) Application-level Event Streams under §5.10** — an
  `<Event>` whose `text()` carries an inline payload (the callback
  scheme §5.10.4.5 already uses this pattern). Presentation-time
  aligned.
- **(c) Vendor descriptors under §5.8.4.8 / §5.8.4.9** — a scheme
  URI with `@value` carrying the asset URL string. Placement is
  constrained to AdaptationSet / Representation / Sub-Representation,
  so this carrier inherits DR-5's MIME constraint unless hosted
  inside a foreign-namespace parent, which collapses (c) into (a)
  with worse readability.

- **Source**: §5.2.1, §5.10, §5.8.4.8, §5.8.4.9 read against DR-1 /
  DR-4 / DR-5.
- **Implication for SGAI**: the carrier choice for any non-AV
  asset is closed to this enumeration. Builders pick (a) / (b) / (c)
  on fit: one-fetch vs round-trip, named element vs descriptor,
  presentation-time alignment vs static attribute.

## DR-7 — Non-zero-duration Periods MUST contain at least one AdaptationSet

§5.3.2.2 Table 4 requires at least one AdaptationSet in each
Period unless `Period@duration` is zero. An SPS Period containing
only an `<EventStream>` (no AdaptationSet) is non-conformant for
any non-zero duration. A slot whose tracking requires
presentation-time alignment across non-zero duration MUST
therefore carry at least one AdaptationSet (which inherits DR-1 /
DR-5) or carry the asset and tracking outside any Period the spec
defines as non-zero-duration.

- **Source**: §5.3.2.2 Table 4.
- **Implication for SGAI**: an "empty-Period tracking carrier"
  variant — a Period that holds only events and no media — is
  closed. Tracking for non-AV ads that needs presentation-time
  alignment MUST share a Period with at least one AdaptationSet,
  or live outside a non-zero-duration Period.

## Cross-refs

- [`03-requirements.md`](./03-requirements.md) — R1, R6, R8, R9
  (R1.2 enumerates the admissible extension points; R6.6 binds non-
  AV asset URLs to the DR-6 carrier enumeration).
- [`05-dash-linear-interfaces.md`](./05-dash-linear-interfaces.md)
  — references DR-1 / DR-5 when stating the closed AdaptationSet
  axis below the linear reference section.
- [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md)
  — DR-2 / DR-3 govern the legacy-discard semantics of the SVTA
  Ads WG extension namespace.
- [`07-backward-compat-checklist.md`](./07-backward-compat-checklist.md)
  — Item 2 cites DR-2 / DR-3; Item 8 forces a per-construct carrier
  classification against DR-6.

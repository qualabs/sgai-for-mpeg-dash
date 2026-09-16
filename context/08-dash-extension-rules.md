# DASH 6th edition extension rules

This document collects the DASH 6th edition rules that constrain how
SGAI extends the standard. Each rule (DR-N) is normative for the SGAI
design: builders consulting this file should treat the rules as
design-space-closing facts. The rules describe what DASH allows or
forbids; they do not pick a specific construction. The builder,
reading R1 + DR-1..DR-N together, will converge to a DASH-conformant
solution on its own.

Edition binding: every DR-N below is anchored to a specific section
of the edition declared in
[`00-normative-base.md`](./00-normative-base.md). On any edition bump,
this file MUST be re-validated section by section — rules are not
blindly carried forward. `bin/check-normative-base.py` is what makes
that obligation observable: it runs before the build and fails when the
declared edition no longer describes the copy of the standard on disk.

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

## DR-3 — A baseline element nested inside a foreign-namespace parent carries no legacy guarantee

§5.2.1 defines the removal **by namespace**, and states it as an
obligation on the author:

> In addition, the MPD shall be authored such that, after XML
> attributes or elements in the other namespaces than the DASH
> namespace are removed, the result is a valid XML document formatted
> according to that schema and that conforms to this document.

NOTE 2 restates the same operation from the client's side. Neither
addresses a DASH-namespace child nested inside a foreign-namespace
element, and the word *subtree* appears nowhere in the base
specification.

Removing an element removes what it contains: that is ordinary XML,
and it is the reading this specification assumes. What the base
specification supplies is not that reading but the authoring
obligation quoted above — whatever remains after removal has to be a
valid, conformant document, and an author cannot inspect which legacy
client will read it.

Authoring rule: baseline children that legacy clients are expected to
process go at a baseline (non-foreign) position. A baseline child
nested inside a foreign-namespace element is authored for clients
that implement that namespace, and no legacy behaviour may be assumed
for it.

- **Source**: §5.2.1 and its NOTE 2, for the removal-by-namespace
  obligation quoted above. The whole-subtree reading is this
  specification's; the base specification does not state it.
- **Implication for SGAI**: chooses the placement of any baseline
  DASH element appearing alongside SGAI extensions. A baseline
  element placed as a sibling of an SGAI element stays within what a
  legacy client processes; one wrapped inside an SGAI element does
  not — and any construct that nests a baseline element MUST still
  satisfy §5.2.1 once the foreign-namespace parent is removed.

## DR-4 — Annex F is informative; what binds a new delivery format is the Interoperability Point URI of §8.1

DASH Annex F is headed **(informative)**. F.2 says that a
specification for how to use a media container format with DASH
*should* include a definition of the MIME type for the Representation
formed as a concatenation of Segments, and a description of either a
self-initializing Media Segment or the combination of an
Initialization Segment and a Media Segment format. It is guidance and
imposes nothing.

The binding clause is §8.1, which is normative. A profile has an
identifier that is a URI, and the profiles with which an MPD complies
are indicated in the `MPD@profiles` attribute as a comma-separated
list of profile identifiers. §8.1 also names the shape an extension
like this one would take: restrictions defined outside the base
document are recommended to be referred to not as profiles but as
**Interoperability Points**, signalled in `@profiles` once a URI is
defined, with the owner of the URI responsible for providing
sufficient semantics on its restrictions and permissions.

No spec-defined image profile, HTML profile, or thumbnail profile
exists in DASH 6th. Introducing one means authoring rules,
conformance criteria and an Interoperability Point URI to define,
publish and get declared — heavier than §5.2.1 foreign-namespace open
content for an attribute that is a flat HTTP URL to a renderable
asset.

- **Source**: §8.1 for the Interoperability Point URI and
  `MPD@profiles`. Annex F (F.2) is informative and is cited here as
  guidance, not as an obligation.
- **Implication for SGAI**: admissible only when the construct
  genuinely requires DASH segment-delivery semantics for a non-
  ISO-BMFF format AND the spec is willing to define and publish an
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

## DR-6 — Four DASH-conformant carriers exist for non-AV ad assets

Given DR-1, DR-4, and DR-5, the only DASH-conformant carriers for
non-AV (non-MP4) ad assets are:

- **(a) Foreign-namespace open content under §5.2.1** — a new
  element in `urn:svta:dash:*` carrying the asset URL as an
  attribute. One-fetch, static.
- **(b) Application-level Event Streams under §5.10** — an
  `<Event>` whose `text()` carries an inline payload (the callback
  scheme §5.10.4.5 already uses this pattern). Presentation-time
  aligned.
- **(c1) Supplemental descriptors under §5.8.4.9** — a scheme URI
  with `@value` carrying the asset URL string, on a
  `SupplementalProperty`. §5.8.4.9's NOTE: an unrecognised scheme or
  value means the DASH Client *"is expected to ignore the
  descriptor"*, leaving the parent element intact.
- **(c2) Essential descriptors under §5.8.4.8** — the same payload on
  an `EssentialProperty`. §5.8.4.8's NOTE 1: an unrecognised scheme or
  value means the DASH Client *"is expected to ignore the parent
  element that contains the descriptor"*. The parent goes with it.

  The two are **not interchangeable, and neither is wrong**: (c2) is
  what a construct wants when presenting the parent without
  understanding the descriptor would be incorrect, and (c1) is what it
  wants everywhere else. Naming them as one option hides the only
  difference that matters.

  Both share the placement constraint: they sit on AdaptationSet /
  Representation / Sub-Representation, so both inherit DR-5's MIME
  constraint unless hosted inside a foreign-namespace parent, which
  collapses them into (a) with worse readability.

- **Source**: §5.2.1, §5.10, §5.8.4.8, §5.8.4.9 read against DR-1 /
  DR-4 / DR-5.
- **Implication for SGAI**: the carrier choice for any non-AV
  asset is closed to this enumeration. Builders pick
  (a) / (b) / (c1) / (c2) on fit: one-fetch vs round-trip, named
  element vs descriptor, presentation-time alignment vs static
  attribute, and — between (c1) and (c2) — whether a legacy Player
  that cannot read the descriptor should keep the parent element or
  drop it.

## DR-7 — Non-zero-duration Periods MUST contain at least one AdaptationSet

§5.3.2.2 Table 4 requires at least one AdaptationSet in each
Period unless `Period@duration` is zero. An SPS Period containing
only an `<EventStream>` (no AdaptationSet) is non-conformant for
any non-zero duration. A slot whose tracking requires
presentation-time alignment across non-zero duration MUST
therefore carry at least one AdaptationSet (which inherits DR-1 /
DR-5) or carry the asset and tracking outside any Period the spec
defines as non-zero-duration.

- **Source**: §5.3.2.2 Table 4, the `AdaptationSet` row. The
  cardinality column reads `0...N`; the requirement is in the same
  cell, two lines below it: *"At least one Adaptation Set shall be
  present in each Period unless the value of the @duration attribute
  of the Period is set to zero."*
- **Implication for SGAI**: an "empty-Period tracking carrier"
  variant — a Period that holds only events and no media — is
  closed. Tracking for non-AV ads that needs presentation-time
  alignment MUST share a Period with at least one AdaptationSet,
  or live outside a non-zero-duration Period.

## DR-8 — DASH does not govern Player behaviour, so no construct of ours can compel a Player

Placing a construct in a namespace other than DASH's is **the only way
to add anything to an MPD**, and §5.2.1 guarantees the document remains
valid once those constructs are removed. **That is the whole of what the
mechanism provides.**

It obliges no Player. The standard states of itself that *"DASH Client
operation is not specified normatively in this document"* and that
*"profiles merely specify restrictions on MPD and Segments rather than
DASH Client behaviour"*. **DASH specifies no Player behaviour anywhere**
— so no construct defined here, in any namespace and under any profile,
can compel a Player that does not implement this specification.

**Consequence for authoring:** a requirement in this specification
**may** oblige a Player conformant **to this specification**. It **may
not** promise what *"every Player"* will do, nor that a construct will
*"not be silently ignored"*. A profile or interoperability-point URI
would **declare** that a document carries these constructs; it would
**not** make anyone honour them.

- **Source**: §8.1, NOTE 1: *"A profile can also be understood as
  permission for DASH Clients that only implement the features required
  by the profile to process the Media Presentation (MPD document and
  Segments). However, as DASH Client operation is not specified
  normatively in this document, it is also unspecified how a DASH Client
  conforms to a particular profile. Hence, profiles merely specify
  restrictions on MPD and Segments rather than DASH Client behaviour."*
  And §5.2.1, NOTE 2, for the other half — that a client removing
  everything outside the Annex B schema obtains a valid document and
  *"can use such a resulting MPD for presentation of a conforming Media
  Presentation."* Both quotations are located to the line of the primary
  copy in the citation verification register named in
  [`00-normative-base.md`](./00-normative-base.md).
- **Implication for SGAI**: this rule closes a promise, not an
  extension point. The extension namespace remains the way SGAI adds
  everything it adds; what it does not add is any hold over a Player
  that has never heard of SGAI. R28 is the worked case: its
  ClickThrough carrier promised that *"every conformant Player"* would
  read it, which under this rule is unpromiseable, and the guarantee is
  now scoped to Players conformant to this specification across the
  nine sites that stated it. The contrast R28 exists to draw — its
  carrier MUST be read where R23's metadata MAY be ignored — survives
  the scoping untouched, because both obligations were always addressed
  to the same Players.

## DR-9 — The two vendor descriptor elements are not interchangeable: an unrecognised scheme costs the parent on one and only the descriptor on the other

R1.2 admits vendor descriptor schemes (§5.8.4.8 / §5.8.4.9) as an
extension point for **any** new construct, not only for the asset
carriers DR-6 enumerates. The two elements look alike — each carries a
scheme URI and a value — and they differ in the one respect that
decides what an extension costs: what a client does when it does not
recognise the scheme.

> §5.8.4.8, NOTE 1: *"If the scheme or the value for this descriptor is
> not recognized, the DASH Client is expected to ignore **the parent
> element that contains the descriptor**."*
>
> §5.8.4.9, NOTE: *"If the scheme or the value for this descriptor is
> not recognized, the DASH Client is expected to ignore **the
> descriptor**."*

An SGAI scheme carried on an `EssentialProperty` therefore makes a
legacy client drop the `AdaptationSet` or `Representation` that holds
it. Choosing between the two elements is choosing what a client that
does not implement this specification loses.

**Neither is wrong.** `EssentialProperty` is the correct choice when
presenting the parent without understanding the descriptor would
produce an incorrect result — it is better for an old client to omit
the element than to render it wrongly. `SupplementalProperty` is the
correct choice everywhere else.

One consequence follows from DP-3 rather than from the base
specification, and is recorded as a consequence: on anything in the
primary content path, dropping the parent would break primary-content
playback, which DP-3 forbids outright. `EssentialProperty` is
therefore unavailable there — not because DASH says so, but because
this specification has already decided what it will never do.

- **Source**: §5.8.4.8 NOTE 1 and §5.8.4.9's NOTE, quoted verbatim
  above. Both are notes rather than normative clauses, which matches
  the base specification declining to specify Player behaviour
  normatively at all (DR-8); what they describe is the expectation the
  two elements were designed around, and it is the only account the
  standard gives of them.
- **Implication for SGAI**: every construct using either element MUST
  state which one it uses and why, and the backward-compatibility
  checklist classifies them separately for that reason. DR-6 applies
  this rule to the non-AV asset carriers, splitting them into (c1) and
  (c2); this rule is what that split rests on, and it reaches the
  constructs DR-6 does not cover.

## Cross-refs

- [`03-requirements.md`](./03-requirements.md) — R1, R8, R9, R24, R28
  (R1.2 enumerates the admissible extension points; R24.1 binds non-
  AV asset URLs to the DR-6 carrier enumeration; R28 is DR-8's worked
  case, and scopes its guarantee to Players conformant to this
  specification).
- [`05-dash-linear-interfaces.md`](./05-dash-linear-interfaces.md)
  — references DR-1 / DR-5 when stating the closed AdaptationSet
  axis below the linear reference section.
- [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md)
  — DR-2 / DR-3 govern the legacy-discard semantics of the SVTA
  Ads WG extension namespace.
- [`07-backward-compat-checklist.md`](./07-backward-compat-checklist.md)
  — Item 2 cites DR-2 / DR-3; Item 8 forces a per-construct carrier
  classification against DR-6, and keeps (c1) and (c2) apart on the
  grounds DR-9 states.

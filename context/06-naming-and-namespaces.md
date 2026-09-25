# Naming and namespaces

This document captures the naming conventions that any new construct
introduced by the SGAI spec MUST follow. It is the policy layer the
spec consumes when authoring chapters 5 (Syntax) and 8 (Examples),
so the resulting spec document is internally consistent and behaves
cleanly under the R1 ignore-if-unknown contract defined in
[`03-requirements.md`](./03-requirements.md).

## Incubation venue

This specification is incubated at the **SVTA Ads WG**. The SVTA Ads WG is
the working group that owns the namespace of constructs introduced
by the spec during its incubation lifecycle. The choice of `svta`
in the URIs below reflects that ownership: it is the venue
responsible for the spec text, not a vendor tag.

## Scheme URI patterns

### New constructs introduced by this spec

New event schemes introduced by this spec MUST use the year-pinned
pattern under the SVTA Ads WG namespace:

  `urn:svta:dash:<construct>:<year>`

Examples (illustrative — the actual URI list is finalised in the
spec itself):

  - `urn:svta:dash:sgai-overlay:2026`
  - `urn:svta:dash:sgai-pause-trigger:2026`

The `<year>` suffix is the edition year of the spec. Reusing an
existing scheme URI with altered semantics across editions is not
permitted: a fresh URI per edition is what makes the
"ignore-if-unknown" guarantee for legacy Players clean and
auditable. A Player implementing edition N + 1 SHOULD recognise
both `:N:` and `:N+1:` URIs and treat them per the
backward-compatibility rules in that edition's spec.

**`@value` on these schemes.** The base specification asks the owner of
a scheme to define the value space of `EventStream@value` (DASH
§5.10.2.1). The SGAI event schemes define none: an `EventStream`
carrying an SGAI scheme MUST NOT carry `@value`, and a Player MUST
ignore one if present. One family's windows in a Period share a single
`EventStream` (R20.2), so nothing needs to tell two such streams apart.
A later edition that needs to distinguish them defines a value space
then. This does not apply to the tracking callback scheme below, whose
`@value` the base specification fixes.

### Tracking callback event scheme

The spec does **not** introduce a new tracking scheme. Per **R13**
in [`03-requirements.md`](./03-requirements.md), the tracking
callback event scheme is inherited from the MPEG-DASH 6th edition
baseline (the existing scheme URI declared there for the linear
SGAI tracking mechanism). Implementations carrying tracking
beacons for ads introduced by this spec MUST reuse that baseline
scheme; introducing a parallel tracking scheme under
`urn:svta:dash:*` is explicitly out of scope.

### Vendor extensions (Qualabs)

Qualabs-private experimental extensions that are not part of this
specification MUST use the Qualabs vendor namespace:

  `urn:qualabs:<feature>:<year>`

These URIs are not normative and are not part of the SGAI spec.
They are listed here only so that examples and prototypes can
declare them without colliding with the SVTA Ads WG namespace.

## Element / attribute extension namespaces

New XML elements introduced by this spec live under the SVTA Ads
WG extension namespace:

  - **`urn:svta:dash:sgai:<year>`** — proposed extensions to
    MPEG-DASH authored by the SVTA Ads WG as part of this spec.

Every XML element this spec introduces lives under this single SVTA
Ads WG namespace, including the generic application-level metadata
carrier (per R23 in [`03-requirements.md`](./03-requirements.md),
e.g. `AdSystem`, `AdTitle`) and the ClickThrough carrier (per R28).
Both are constructs authored by this spec, so both belong to the
SVTA Ads WG namespace.

Elements in the SVTA Ads WG extension namespace operate under
DASH §5.2.1 foreign-namespace open content (DR-2 in
[`08-dash-extension-rules.md`](./08-dash-extension-rules.md)).
Legacy DASH clients remove such elements, and a baseline DASH child
nested inside one carries **no legacy guarantee** (DR-3). This is the
authoring lever for choosing what legacy clients process: a baseline
element placed as a sibling of an SGAI element stays within their
reach; one wrapped inside an SGAI element does not. Constructs
introduced by this spec MUST honour the authoring rule stated in
DR-3.

## Versioning

When this specification evolves to a new edition:

  - Constructs whose semantics change MUST use a new
    `<year>` suffix on their scheme URI under
    `urn:svta:dash:<construct>:<year>`.
  - Constructs whose semantics are unchanged MAY keep their
    existing URI.
  - The spec's chapter 2 (Normative references) MUST list the
    URIs introduced by the current edition explicitly.
  - The tracking callback event scheme inherited from the
    MPEG-DASH 6th edition baseline is unaffected by this spec's
    versioning; it follows the baseline edition's lifecycle.

## Layout vocabulary

The accepted layout names for overlay templates are defined and
maintained by the IAB, not by this spec. The spec MUST reference
those IAB-defined values without inventing new layout names at
chapter level. To propose a new layout, the editor works with the
IAB directly — this specification does not own the vocabulary.
Per **R12** in [`03-requirements.md`](./03-requirements.md), the
layout vocabulary MUST map 1:1 to IAB-defined ad-type values; no
publisher-private or spec-private layout names are admissible. The one
exception is the optional `custom` overlay layout of **R39**, the only
layout name this spec defines itself.

## A family name and a layout token are different things

The word *overlay* is used for both, and the two must not be read as
one. A **family** is a kind of non-linear ad opportunity; a **layout
token** is one spatial arrangement inside a rendering frame, drawn from
the IAB vocabulary above. `overlay` is a member of both vocabularies,
and they do not mean the same thing.

Every name this specification mints follows from that split:

- Names of documents, elements and profile URIs that serve **the whole
  non-linear family** — the resolution document, its root element, the
  profile URI that identifies it — take the **family** reading. A
  pause-ad document travels under those names because a pause ad is a
  non-linear ad, not because it is laid out as an overlay.
- Names that select a **spatial arrangement** take the layout reading
  and are governed by the IAB vocabulary, which this specification does
  not own.

A reader who meets `overlay` in a name therefore needs to know which of
the two vocabularies the name belongs to, and the rule above is what
tells them. Where a single sentence could be read either way, it states
which reading it takes rather than relying on the context around it.

## Naming consistency with baseline DASH

When this spec needs to express a component that is in essence the
same as one already defined in MPEG-DASH 6th edition (or its
profile annexes), the spec MUST reuse the existing baseline
construct with all its characteristics — name, default values,
permitted value domain, units, semantics. The spec does NOT
introduce a new identifier when an existing one already covers
the concept.

## Preferred encoding patterns

When this spec introduces a list-shaped property whose elements are
single-valued tokens (no per-item nested attributes, no per-item
sub-elements), the preferred encoding is a **single attribute**
carrying a space-separated string of tokens, NOT a nested element
wrapper with per-item child elements.

The delimiter is **space**, matching `@dependencyId`, which baseline
DASH declares as `StringVectorType` — an XML Schema list type, and so
whitespace-delimited.

Baseline DASH does not use one delimiter for every token list.
`MPD@profiles` (§5.3.1.2 Table 3) and `@codecs` (§5.3.7.2 Table 16)
are **comma**-separated: both are constrained to IETF RFC 6381:2011
productions — `pro-simple` / `pro-fancy` for the first, `simp-list` /
`fancy-list` for the second. The space delimiter chosen here follows
`@dependencyId`, not those two.

For example, prefer:

```xml
<svta:OverlayPresentation allowedLayouts="overlay-corner overlay-lower-third"/>
```

over:

```xml
<svta:OverlayPresentation>
  <svta:AllowedLayouts>
    <svta:Layout name="overlay-corner"/>
    <svta:Layout name="overlay-lower-third"/>
  </svta:AllowedLayouts>
</svta:OverlayPresentation>
```

Rationale: the attribute form keeps the MPD compact, matches the
encoding style of existing baseline DASH attributes, and avoids one
level of XML nesting for no semantic gain. The element form is
warranted only when each list item needs to carry its own
attributes or children — at which point the items are no longer
single-valued tokens and this preference no longer applies.

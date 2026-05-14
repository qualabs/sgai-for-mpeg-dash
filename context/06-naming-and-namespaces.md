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

Vendor-private extensions developed by Qualabs that are not part
of this spec — including VAST application-layer metadata that has
no native DASH carrier (per R6 in
[`03-requirements.md`](./03-requirements.md)) — live under the
Qualabs vendor namespace:

  - **`urn:qualabs:sgai:<year>`** — Qualabs vendor-private
    extensions. Not normative; not part of this spec.

Elements in the SVTA Ads WG extension namespace operate under
DASH §5.2.1 foreign-namespace open content (DR-2 in
[`08-dash-extension-rules.md`](./08-dash-extension-rules.md)).
Legacy DASH clients discard such elements **with their full
subtree** (DR-3) — baseline DASH children nested inside a foreign-
namespace element are not seen by legacy clients. This is the
authoring lever for choosing what legacy clients see: a baseline
element placed as a sibling of an SGAI element remains visible to
legacy; a baseline element wrapped inside an SGAI element is
opaque. Constructs introduced by this spec MUST honour the
authoring rule stated in DR-3.

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
broadcaster-private or spec-private layout names are admissible.

## Naming consistency with baseline DASH

When this spec introduces a new element or attribute that represents
**the same semantic concept** as an existing MPEG-DASH 6th edition
construct (same kind of value, same units, same role), the new
identifier MUST reuse the baseline name verbatim. Diverging on the
name when the semantics match is a readability hazard for implementers
and a source of silent mapping bugs across baseline-aware and
SGAI-aware code paths.

Conversely, when this spec introduces a new attribute that **shares a
name** with a baseline DASH attribute but **differs in semantics** (a
different unit, a different reference frame, a different domain of
values), the new identifier MUST be renamed so the difference is
visible at the call site. Same name with different semantics is a
silent-failure pattern; an explicit prefix, suffix, or full rename is
required (for example, `@offsetSeconds` vs `@offsetTicks` when the
unit differs, or namespace-prefixing the custom one as `svta:offset`).

Two specific cases that arose from prior audits:

- `@earliestResolutionTimeOffset` exists in MPEG-DASH §5.3.2.6.1 on
  `<ImportedMPD>` in **seconds**. If SGAI-namespaced elements
  (`<OverlayPresentation>`, `<PauseAdPresentation>`, etc.) need a
  similarly-scoped attribute in `EventStream@timescale` units, the
  SGAI attribute MUST NOT reuse the baseline name verbatim — the
  unit collision otherwise is invisible to a reader scanning the
  XML.
- `Period@duration` of a non-linear sub-MPD is semantically the
  same as the parent slot's overlay window; the spec MUST use
  `@duration` (not invent `@overlayDuration` or similar) because
  the underlying semantics match the DASH baseline meaning.

This applies to elements as well as attributes.

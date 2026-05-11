# Naming and namespaces

This document captures the naming conventions that any new construct
introduced by the SGAI norm MUST follow. It is the policy layer the
norm consumes when authoring chapters 5 (Syntax) and 8 (Examples),
so the resulting norm document is internally consistent and behaves
cleanly under the R1 ignore-if-unknown contract defined in
[`03-requirements.md`](./03-requirements.md).

## Scheme URI patterns

New event schemes introduced by this norm follow the year-pinned
pattern used by the MPEG-DASH 6th edition baseline:

  `urn:mpeg:dash:event:<construct>:<year>`

Examples (illustrative — the actual URI list is finalised in the
norm itself):

  - `urn:mpeg:dash:event:sgai-overlay:2026`
  - `urn:mpeg:dash:event:sgai-pause-trigger:2026`

The `<year>` suffix is the edition year of the norm. Reusing an
existing scheme URI with altered semantics across editions is not
permitted: a fresh URI per edition is what makes the
"ignore-if-unknown" guarantee for legacy Players clean and
auditable. A Player implementing edition N + 1 SHOULD recognise
both `:N:` and `:N+1:` URIs and treat them per the
backward-compatibility rules in that edition's norm.

## Element / attribute extension namespaces

New XML elements introduced by this norm live under one of two
namespaces, picked by content type:

  - **`urn:mpeg:dash:sgai:<year>`** — proposed-MPEG additions
    that are intended to land in a future MPEG-DASH edition (i.e.,
    candidates for normative inclusion).
  - **`urn:qualabs:sgai:<year>`** — vendor-side experimental
    extensions developed by Qualabs that are not (yet) proposed
    for standardisation.

Vendor namespaces are valid carriers for VAST application-layer
metadata that has no native DASH carrier (per R6 in
[`03-requirements.md`](./03-requirements.md)).

Legacy Players MUST ignore unknown namespaces under DASH's
extension rules (per R1).

## Versioning

When this norm evolves to a new edition:

  - Constructs whose semantics change MUST use a new
    `<year>` suffix on their scheme URI.
  - Constructs whose semantics are unchanged MAY keep their
    existing URI.
  - The norm's chapter 2 (Normative references) MUST list the
    URIs introduced by the current edition explicitly.

## Layout vocabulary

The canonical enum of overlay layout templates lives in
[`99-glossary.md`](./99-glossary.md) under "Canonical layout
vocabulary". The norm MUST reference those enum-values without
inventing new layout names at chapter level. To propose a new
layout, an editor adds the entry to the glossary first, then the
norm references it.

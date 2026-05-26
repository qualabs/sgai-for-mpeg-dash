# ADR 0001 — Defer spatial caps to IAB CTV per the `@layout` token

- **Status**: proposed
- **Date**: 2026-05-26
- **Deciders**: Qualabs WG (proposed by AI review of issue #4, pending @emilsas + Nicolás Levy)
- **Supersedes**: —
- **Superseded by**: —

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

Issue [#4](https://github.com/qualabs/sgai-for-mpeg-dash/issues/4)
(raised by @emilsas) asked whether the slot declaration should carry
a **declarative spatial cap**: an overlay size cap (e.g. a corner
overlay never exceeds N% of the viewport) and a squeezeback shrink
cap (e.g. primary content never drops below M% of the viewport).
Today `allowedLayouts` controls *which* layout types are admissible
and `@layout` names the form, but neither carries any *dimensional*
information. The Player therefore has no declarative bound to
enforce against an incoming `RenderableAsset`.

The issue laid out candidate MPD-side shapes:

- **Option A** — flat attributes on `<svta:OverlayPresentation>`
  (`maxOverlayAreaPercent`, `maxShrinkPercent`).
- **Option B** — a child `<svta:OverlayConstraints>` element grouping
  the spatial bounds.
- **Option C** — delegate to the ORD / form metadata and move the
  check into the Player's selection algorithm.

Two of the issue's open questions are decisive for the answer:

- *"Who owns the constraint semantics — the Broadcaster (slot
  declaration) or the IAB (layout template spec)? R12 delegates
  ad-type visual templates to the IAB; does a spatial cap on a slot
  stay within the Broadcaster's domain?"*
- *"Is there a precedent for this pattern in existing VAST 4.x or
  IAB CTV ad template specs that we should align with or defer to?"*

Investigation of the IAB CTV *Ad Format Guidelines for Digital Video
and CTV* (Final Release, May 2026 —
<https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e>)
shows the answer to the second question is **yes**: the spatial caps
are **already defined per layout** by IAB. Each `@layout` token maps
1:1 to an IAB-defined ad type (this 1:1 mapping is already mandated by
R12.2), and each IAB ad type already carries its own dimensional
bound. The cap the issue asks for is not missing from the system — it
is inherited through the layout token by normative reference to IAB,
which is exactly the delegation R12 already establishes for ad-type
definitions and R10 already establishes for spatial arrangement.

### IAB CTV caps, verbatim per layout

Cited verbatim from the IAB CTV *Ad Format Guidelines for Digital
Video and CTV* (Final Release, May 2026). All percentages are of the
1920×1080 frame unless the entry states otherwise.

| `@layout` token (IAB ad type) | IAB spatial cap |
| --- | --- |
| Corner Overlay | 25% of the 1920×1080 frame |
| Lower Third Overlay | 30% of the bottom |
| Squeezeback L-Shape | primary content 60% |
| Squeezeback Frame | primary content 60% |
| Squeezeback Double Box | each box 25% |

The IAB caps are expressed as upper bounds ("no more than X%"),
so a Broadcaster that wants a tighter slot (a corner overlay smaller
than the 25% nominal) is already free to do so within the IAB
envelope — the "less than X%" flexibility lives in the IAB
guidelines, not in a new MPD attribute.

## Decision

Spatial caps on overlay and squeezeback slots are **inherited from
the IAB CTV Ad Format Guidelines per the `@layout` token**; the SGAI
spec does **NOT** introduce an MPD-side dimensional attribute.

Concretely, this means **none** of the following are added to the
spec:

- no `@maxOverlayAreaPercent` / `@maxShrinkPercent` (Option A),
- no `@layoutBoundsXYWH` or any explicit per-slot bounding box,
- no reuse of SRD (Spatial Relationship Description) for this purpose,
- no nested `<svta:OverlayConstraints>` / `<LayoutConstraints>`
  element (Option B).

The Player enforces the per-layout bound by resolving the `@layout`
token to its IAB ad type and applying the IAB-declared cap for that
type. This is a normative-reference relationship, identical in kind
to the one R12 already establishes for ad-type names and R10 already
establishes for spatial arrangement — no new construct, no parallel
layout system, no new MPD surface.

The issue's other open questions are dispositioned as follows:

- *Per-layout-token vs global to the slot* — per-layout-token: the
  cap is a property of the IAB ad type the `@layout` resolves to, not
  of the slot as a whole.
- *Reject vs clip when an asset exceeds the cap* — out of scope for
  this ADR. An asset whose dimensions exceed the IAB cap for its
  declared layout is a malformed form; how the Player handles it
  (reject-and-fall-through like E7, or clip/scale) is a Player error-
  semantics question, not a slot-declaration question, and is left to
  the error-semantics work, not resolved here.

## Consequences

### Positive

- **Zero new MPD construct.** Satisfies R9.2 (a new construct MUST
  NOT be introduced when an existing one suffices), R9.3 (justify
  before introducing), and R10 (do not recreate a layout system).
- **IAB stays authoritative.** Consistent with R12 (ad-type
  definitions, and now their dimensional envelope, are owned by IAB)
  and R10.1/R10.3 (spatial arrangement delegated to the IAB CTV
  layout standard).
- **Broadcaster flexibility is preserved.** A Broadcaster may tighten
  below the nominal IAB cap because the IAB guidelines already
  express the caps as "no more than X%" upper bounds; the smaller-than-
  nominal case needs no new attribute.
- **No downstream selection-algorithm change.** The Player's existing
  `@layout` → IAB resolution already locates the cap; nothing new is
  forwarded from the MPD event.

### Negative / limits

- **Layouts outside the IAB catalogue have no declarative cap.**
  Custom picture-in-picture, custom sidebar, or non-CTV banner
  layouts that are not part of the IAB CTV ad-type set inherit no
  IAB-defined bound. If a future WG requirement needs caps for such
  layouts, the deferral mechanism must be revisited — at which point
  Options A/B/C from issue #4 come back into scope. This ADR does not
  pre-decide that future case.
- **Coupling to an external, evolving document.** The caps live in the
  IAB CTV guidelines (a live link, not snapshotted — same posture as
  R12). If IAB revises a cap, the spec follows automatically by
  reference, which is intended, but it means the authoritative number
  is not pinned inside this repo. The verbatim table above is a
  snapshot for traceability, not the source of truth.

## Links

- Issue #4 — broadcaster-declared spatial constraints:
  <https://github.com/qualabs/sgai-for-mpeg-dash/issues/4>
- IAB CTV *Ad Format Guidelines for Digital Video and CTV*
  (Final Release, May 2026):
  <https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e>
- `../../context/03-requirements.md` — R12 (IAB ownership), R10
  (no parallel layout system), R9.2 / R9.3 (minimise net new
  constructs).

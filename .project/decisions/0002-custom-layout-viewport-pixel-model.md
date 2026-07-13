---
id: 0002
title: Add custom layout as a new layout type with a viewport-relative pixel coordinate model
status: proposed
scope: phase-03
date: 2026-07-13
supersedes: null
superseded_by: null
---

# ADR 0002 — Custom layout: a new layout type with a viewport-relative pixel coordinate model

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

> Status is `proposed`: this ADR records a decision Nicolás has already
> made in substance, written up for review during the phase-03 review.
> It is finalized (flipped to `accepted`) when the phase-03 tasks are
> authorised for execution.

## Context

The core SGAI spec offers a fixed set of layouts for non-linear ads:
overlay, side-by-side / double-box (R26), L-shape / squeezeback (R27),
and full-screen takeover. Spatial arrangement in the core is delegated
to HTML5 / CSS and to the IAB CTV Ad Format Guidelines by normative
reference (R10, R12, ADR 0001). The core spec deliberately owns no
explicit coordinate system: it does not declare pixel or percentage
bounding boxes MPD-side.

A WG request (driven by David Hassoun) asks for a layout in which an ad
opportunity can place an arbitrary number of elements at exact
positions, sizes, and stacking order — a level of spatial control the
IAB catalogue layouts do not express. This is "custom layout".

Two questions must be settled:

1. Is custom layout a generalisation of the base layouts, or a distinct
   additional layout type?
2. What coordinate model does it use — percentages of the viewport, or
   pixels against a reference viewport?

## Decision

**Custom layout is added as a new, additional layout type**, offered
alongside the base layouts (overlay, side-by-side R26, L-shape R27,
takeover). It does NOT subsume, replace, or generalise any base layout;
the base layouts are unchanged. Custom layout is one more entry in the
layout vocabulary a slot may permit.

**Custom layout uses a reference-viewport pixel coordinate model.** A
custom layout declares a **reference viewport** (a width x height in
pixels, e.g. 1920x1080). Every element is positioned (top-left x, y) and
sized (width, height) in **pixels relative to that reference viewport**.
The Player maps the reference viewport onto the actual device screen;
when the reference viewport equals the screen, placement is pixel-exact.

The **element model**: a custom layout carries **N elements**. Exactly
one element is the **primary-content reference**. Every element may be
placed at any position, any size, and any **Z-order**; **overlap is
permitted** and Z-order determines stacking. Each non-primary element
carries a creative under the admissible carrier set (R15).

The **actor contract is preserved (R2)**: the **Publisher enables**
custom layout among the layouts it permits for the slot; the **ADS
decides** the per-element geometry and Z-order and the **APS carries**
it into the resolution document as a presentation option; the **Player
validates and renders** or falls through.

**Degradation reuses existing machinery**: the custom-layout
presentation option participates in the **R5 ordered fallback** (first
satisfiable option wins) and its decoder / surface budget is checked
against the device class per **R3**. No new degradation mechanism is
introduced.

### Why pixels over percentages

Pixels against a known reference viewport give exact, unambiguous
placement. Percentages always carry rounding imprecision when converted
to device pixels, and two implementations can round differently. When
precise, repeatable placement matters — the reason a Publisher would
reach for custom layout at all — a reference-viewport pixel model
delivers it and a percentage model does not.

### Why a new type rather than generalising the base layouts

The base layouts map 1:1 to IAB CTV ad types and inherit their spatial
caps by reference (R12, ADR 0001). Generalising them into a
pixel-coordinate model would pull that IAB deferral into the core and
contradict R10. Keeping custom layout as a separate, opt-in type leaves
the base layouts and their IAB posture untouched.

## Consequences

### Positive

- **Base layouts and their IAB deferral are untouched.** R10, R12, and
  ADR 0001 continue to govern the core layouts unchanged.
- **Exact placement is available** for opportunities that need it,
  without forcing a coordinate model onto the core.
- **No new degradation or actor machinery.** R2 (actor contract), R3
  (decoder budget), and R5 (ordered fallback) absorb custom layout with
  no additions.
- **Opt-in and self-contained.** A conformant implementation ignores
  custom layout and still conforms to the core; a legacy Player that
  does not implement it falls through per R1 / R5.

### Negative / limits

- **The spec owns an explicit coordinate model for this type**, which
  the core deliberately avoids. This is a conscious trade-off: it is
  admissible only because custom layout is an advanced, opt-in extension
  isolated from the core. If custom layout ever became mandatory, the
  R10 posture would have to be revisited.
- **Reference-viewport vs screen aspect-ratio mismatch** (letterbox /
  scale / clip behaviour) is not settled here; it is a design-level
  detail deferred to the design phase.
- **Decoder-budget blow-up risk.** N overlapping video elements can
  exceed any device's decoder budget; the requirement binds custom
  layout to R3 so an over-budget layout is simply not selected rather
  than failing at runtime.

## Links

- `../phases/03-custom-layout/PHASE.md` — phase scope.
- `../phases/03-custom-layout/T-01-PLAN.md` — full design detail.
- `../../context/03-requirements.md` — R2 (actor contract), R3 (device
  capability / decoder budget), R5 (device-aware ordered selection),
  R10 (do not recreate a layout system), R15 (admissible carriers),
  R26 (side-by-side), R27 (L-shape).
- `0001-defer-to-iab-ctv-for-spatial-caps.md` — the IAB spatial-cap
  deferral this ADR consciously steps outside of for the custom-layout
  type only.

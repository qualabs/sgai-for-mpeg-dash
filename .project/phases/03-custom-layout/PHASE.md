---
phase: 03-custom-layout
title: Custom layout — an advanced, opt-in layout type
status: planning
started: 2026-07-13
closed: null
---

# 03-custom-layout

Add a **custom layout** to the SGAI spec: a new, additional layout type
that sits alongside the base layouts already defined (overlay,
side-by-side / double-box per R26, L-shape / squeezeback per R27, and
full-screen takeover). Custom layout lets an ad opportunity place N
elements at arbitrary positions, sizes, and Z-order inside a reference
viewport, expressed in pixels relative to that viewport.

**Custom layout is an ADVANCED, OPTIONAL extension of the spec.**
Implementing it is opt-in: a conformant implementation does NOT need
custom layout to conform to the core spec. The requirement and the
use-cases this phase produces MUST live in their own, self-contained
section explicitly marked as an advanced extension, kept separate from
the core requirements and core use-cases. This is a hard framing
constraint set by Nicolás, not a stylistic preference.

This phase is **independent** of phase `04-multiview`. The two advanced
features are designed separately and do not build on one another.

## Objective

Specify custom layout as a new layout type in `context/`: define the
coordinate model, the element model, who declares what (Publisher
enables it, ADS/APS supplies the positions), and how it degrades on
devices that do not support it. Produce the new requirement(s), the
use-cases, and the ADR that records the architectural decision.

## Design decisions to encode (set by Nicolás)

These are the decisions this phase must faithfully encode. They are the
input to the plan (`T-01-PLAN.md`) and the ADR; they are not open for
re-litigation in this phase.

- **New layout type, not a generalisation of the base layouts.** Custom
  layout is its OWN additional layout type, offered alongside overlay,
  side-by-side (R26), L-shape (R27), and takeover. It does not subsume,
  replace, or generalise any of the base layouts; those remain as they
  are. Custom layout is one more entry in the layout vocabulary.
- **Coordinate model: reference viewport + pixels.** Custom layout
  defines a **reference viewport** (for example 1920x1080). Every
  element is positioned and sized in **pixels relative to that
  reference viewport**. Rationale (Nicolás): pixels against a known
  reference viewport give exact placement when the viewport equals the
  device screen; percentages always carry rounding imprecision. The
  reference viewport is the coordinate space; the Player maps it to the
  actual screen.
- **Element model: N elements, arbitrary geometry and Z-order.** A
  custom layout may carry **N elements**. One element is the
  **reference to the primary content**. Every element can be placed at
  any position, at any size, and at any **Z-order**; overlap between
  elements is permitted (Z-order disambiguates stacking).
- **Who declares what.** The **Publisher ENABLES** the custom layout —
  it is one of the layouts the Publisher permits for ads on the slot.
  The **ADS/APS declares the concrete positions** (the per-element
  geometry and Z-order) in the resolution document. This preserves the
  actor contract (R2): Publisher declares the constraint / permission,
  ADS decides, APS carries, Player renders.
- **Degradation.** Custom layout participates in the **ordered fallback
  (R5)** like any other presentation option and respects the
  **decoder / resource budget (R3)**. If the device cannot satisfy the
  custom layout (geometry, surface types, or decoder count), the Player
  falls through to the next option in the ordered list, exactly as it
  does for the base layouts.

## Scope

- One new **requirement** (or a small self-contained cluster) defining
  custom layout: the reference-viewport pixel coordinate model, the
  N-element model with arbitrary position / size / Z-order and permitted
  overlap, the primary-content reference element, the
  Publisher-enables / ADS-APS-positions split, and the R5 / R3
  degradation behaviour. Written as a **standalone advanced-extension
  section** in `context/03-requirements.md`, not interleaved with the
  core requirements.
- New **use-case(s)** exercising custom layout across the device classes
  (D1–D5), in a **standalone advanced-extension section** of
  `context/04-use-cases.md`.
- One **ADR** in `.project/decisions/` recording the architectural
  decision: a new layout type plus the viewport-relative pixel
  coordinate model, including why pixels-against-a-reference-viewport
  over percentages, and why a new type rather than generalising the base
  layouts.
- Glossary entries in `context/99-glossary.md` for the new terms
  (custom layout, reference viewport, element, Z-order) marked
  *(proposed)*.

## Out of scope

- Multiview (phase `04-multiview`), which is independent.
- The concrete MPD syntax / attribute names for the coordinate model and
  the element list (that is design-level work for a later design phase;
  this phase defines the requirement and the use-cases at the
  spec-requirement level, agnostic of final construct names, consistent
  with the use-case framing in `context/04-use-cases.md`).
- Editing `context/` in this governance-scaffolding step. The phase is
  created in `planning` status for Nicolás to review first; the actual
  writing into `context/` happens when the tasks are executed after
  review.

## Stakeholders

- **Feature driver**: David Hassoun (WG contributor) — drove both this
  feature and multiview.
- **Decision owner**: Nicolás Levy (CTO) — owns the design decisions
  encoded above and approves the ADR.

## Deliverables

1. New advanced-extension requirement(s) for custom layout in
   `context/03-requirements.md`.
2. New advanced-extension use-case(s) in `context/04-use-cases.md`.
3. ADR (custom layout as a new layout type + viewport-pixel coordinate
   model) in `.project/decisions/`.
4. Glossary entries in `context/99-glossary.md`.

## Risks

- **R10 scope (a scoping, not a tension).** R10 (do not recreate a
  layout system) and the IAB deferral (ADR 0001) govern the MANDATORY
  base of the spec: the base version has no layout system of its own, it
  defers spatial arrangement to HTML5 / CSS and the IAB CTV catalogue.
  R10 does NOT govern the advanced, on-top extensions (custom layout,
  multiview, and others): those are opt-in and explicitly outside R10's
  scope. Custom layout owns an explicit pixel-coordinate spatial model,
  and that is admissible precisely because it is an extension, not part
  of the mandatory base. The rewording task (T-07) makes R10's
  base-only scope explicit in `context/`.
- **Decoder-budget interaction.** N elements with permitted overlap can
  imply multiple concurrent video decoders; the requirement must bind
  custom layout to R3 so an over-budget custom layout is simply not
  selected on a constrained device rather than failing at runtime.

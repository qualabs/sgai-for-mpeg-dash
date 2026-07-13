---
id: 0003
title: Multiview — decoder-vs-tiles agnostic, fixed layout collection, alternative-content (non-ad) scope
status: proposed
scope: phase-04
date: 2026-07-13
supersedes: null
superseded_by: null
---

# ADR 0003 — Multiview: implementation-agnostic, fixed layouts, alternative-content scope

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

> Status is `proposed`: this ADR records decisions Nicolás has already
> made in substance, written up for review during the phase-04 review.
> It is finalized (flipped to `accepted`) when the phase-04 tasks are
> authorised for execution.

## Context

The SGAI spec is about server-guided ad insertion — linear and
non-linear ads. A WG request (driven by David Hassoun) asks for
**multiview**: presenting 2 up to 4 videos at once (a second feed, a
different camera angle, a parallel match). Multiview is not an ad
experience; it is alternative content. Three questions must be settled:

1. Does the spec cover non-ad alternative content at all, or does
   multiview fall outside its scope?
2. Are multiview layouts a fixed set or free-form geometry (and how does
   this relate to custom layout, phase 03)?
3. Does the spec prescribe how multiview is delivered — multi-decoder or
   HEVC tiles?

## Decision

### D-1. Alternative-content (non-ad) scope, bounded and opt-in

Multiview presents **alternative content** (another feed, another
angle, another parallel match) and is **NOT** an ad experience. Adding
it **widens the spec's scope beyond ads**. This widening is a conscious
decision: multiview is a bounded, **advanced, opt-in extension**. A
conformant implementation ignores multiview and still conforms to the
core ad spec. The requirement and use-cases live in self-contained
advanced-extension sections, so the core ad spec is unaffected and the
spec does not drift into a general presentation spec by accident.

### D-2. Fixed `multiview-*` layout collection, 2 to 4 videos

Multiview uses a **fixed collection of named layouts**, each prefixed
`multiview-*`, supporting 2 up to a maximum of 4 videos. Each preset is
one named allowed layout. Layouts are **fixed presets**, not free-form
geometry. This makes multiview **independent of custom layout** (phase
03): custom layout is arbitrary geometry, multiview is a closed preset
set. (A multiview could in principle be composed with a custom layout,
but the multiview mode defines its own fixed presets.) The proposed set
is derived from the WOXCON SCU41 multiviewer reference image and
enumerated in `../phases/04-multiview/T-01-PLAN.md`; corner / side /
strip positioning are fixed variants of a preset, not parameters.

### D-3. Implementation-agnostic — multi-decoder or HEVC tiles

The spec stays **agnostic** about how multiview is achieved. The two
known mechanisms are **multi-decoder** (two or more decoders, one per
view) and **HEVC tiles** (a single decoder decoding a tiled stream). The
spec describes the multiview capability and the required device
capabilities (the **what**), not the mechanism (the **how**). A device
satisfies a `multiview-*` layout if it can produce the N simultaneous
views by either mechanism.

**R3 is extended** (in place) to express two-or-more concurrent decoders
as a device capability and to signal the tiles single-decoder path.

### Corollary decisions

- **View content is implementation-defined, but live MUST be possible.**
  The requirement does not fix how the N views are carried, but
  multiview MUST support live content. Whether `<ImportedMPD>` supports
  live — and, if not, what carries the N live views (an independent-video
  source, or tiles) — is an open point deferred to the design phase.
- **Audio defaults to the primary content**, with **audio selection**
  among the contents left open as a future MAY (not foreclosed).

## Consequences

### Positive

- **Core ad spec is untouched.** Multiview is a self-contained,
  opt-in advanced extension; ignoring it still conforms.
- **Implementation freedom.** Vendors can ship multiview with
  multi-decoder or tiles; the spec does not pick a winner and does not
  age out when hardware capabilities shift.
- **Bounded complexity.** A fixed 2–4 video preset set keeps the layout
  space closed and testable, unlike free-form geometry.
- **Independence from custom layout.** The two advanced features can be
  designed, reviewed, and implemented separately.

### Negative / limits

- **Scope beyond ads.** The spec now describes a non-ad presentation
  feature. This is admissible only because multiview is bounded and
  opt-in; the ADR is the record that the widening was deliberate.
- **Open live-carriage question.** The requirement is agnostic, but a
  concrete implementation still needs a live-view source; that is
  unresolved and flagged for the design phase (phase-04 T-06).
- **R3 now carries two capability axes** (decoder count and the tiles
  path). The R3 extension must stay coherent with the D1–D5 model and
  the decoder-budget reasoning in R22 / R26 / R27.

## Links

- `../phases/04-multiview/PHASE.md` — phase scope.
- `../phases/04-multiview/T-01-PLAN.md` — full design detail + the
  proposed `multiview-*` layout set and its reference image.
- `../../context/03-requirements.md` — R3 (device capability, extended
  here), R15 (admissible carriers), R22 (single active non-linear form
  / decoder budget), R26 / R27 (multi-decoder layout precedents).
- WOXCON SCU41 multiviewer layout reference:
  <https://woxcon.com/wp-content/uploads/2019/12/SCU41-MV-Layouts-1-e1576239329889.png>

---
phase: 04-multiview
title: Multiview — an advanced, opt-in fixed-layout feature
status: planning
started: 2026-07-13
closed: null
---

# 04-multiview

Add **multiview** to the SGAI spec: the ability to present 2 up to a
maximum of 4 videos at once in one of a fixed collection of named
layouts (`multiview-*`). Multiview is for **alternative content** (a
second feed, a different camera angle, a parallel match) — it is
**not** an ad experience. This is a conscious widening of the spec's
scope beyond ads, recorded as such in the ADR.

**Multiview is an ADVANCED, OPTIONAL extension of the spec.**
Implementing it is opt-in: a conformant implementation does NOT need
multiview to conform to the core spec. The requirement(s) and the
use-cases this phase produces MUST live in their own, self-contained
section explicitly marked as an advanced extension, kept separate from
the core requirements and core use-cases. This is a hard framing
constraint set by Nicolás.

This phase is **independent** of phase `03-custom-layout`. Multiview
does NOT build on custom layout: multiview uses **fixed** layouts.
(Someone could in principle compose a multiview using a custom layout,
but this multiview mode is its own fixed preset set.)

## Objective

Specify multiview in `context/`: the fixed `multiview-*` layout
collection (2–4 videos), the requirement(s), the use-cases, the
extension of R3 to express two-or-more decoders (and the tiles
single-decoder signal), and the ADR. The spec describes the **what**
(the multiview capability and the required capabilities), not the
**how** (implementation is left agnostic between multi-decoder and
HEVC tiles).

## Design decisions to encode (set by Nicolás)

- **Independent of custom layout; fixed layouts.** Multiview does NOT
  build on the custom-layout feature. Multiview layouts are FIXED. Note
  to leave in the spec: one could build a multiview using a custom
  layout, but the multiview mode defines its own fixed preset set.
- **Fixed layout collection `multiview-*`, 2 to 4 videos.** A collection
  of named fixed layouts, each prefixed `multiview-*`, supporting from
  **2 up to a maximum of 4 videos** in different arrangements. Each
  preset is one named allowed layout. The proposed set is derived from
  the WOXCON SCU41 multiviewer reference image and enumerated in
  `T-01-PLAN.md` for Nicolás to validate against the image
  (https://woxcon.com/wp-content/uploads/2019/12/SCU41-MV-Layouts-1-e1576239329889.png).
- **Implementation-agnostic.** The spec stays agnostic about HOW
  multiview is achieved. The two known ways are (a) **multi-decoder**
  (two or more decoders) and (b) **HEVC tiles** (single decoder). The
  spec describes the multiview and the required capabilities, not the
  mechanism.
- **View content: implementation-defined, but live MUST be possible.**
  How the N views' content is delivered is left to the implementation
  (the requirement does NOT fix how the N views are carried), but
  multiview MUST be possible for **live** content. Open point for the
  design phase: if `ImportedMPD` does not allow live, it may be a source
  for independent videos; tiles are a different mechanism. Left as an
  explicit open point in the plan.
- **Scope: alternative content, NOT ads.** Multiview presents
  alternative content (another feed, another angle, another match in
  parallel). It is NOT an ad experience. The boundary is stated
  explicitly. This widens the spec's scope beyond ads — a conscious
  decision recorded in the ADR.
- **Audio: default = primary content; selection not foreclosed.** By
  default the audio of the **primary content** plays. The spec does NOT
  close the door to implementing **audio selection** among the different
  contents.
- **Capacity: extend R3.** Extend R3 to express **two or more decoders**
  as a device capability, and to signal the **tiles (single-decoder)**
  option.

## Scope

- New **requirement(s)** for multiview: the fixed `multiview-*` layout
  collection (2–4 videos), the implementation-agnostic capability
  statement, the alternative-content (non-ad) scope, the live-content
  possibility, and the default-audio / audio-selection posture. Written
  as a **standalone advanced-extension section** in
  `context/03-requirements.md`.
- **Extension of R3** to express two-or-more concurrent decoders as a
  device capability and to signal the tiles single-decoder path.
- New **use-case(s)** in a **standalone advanced-extension section** of
  `context/04-use-cases.md`, exercised across device classes.
- One **ADR** in `.project/decisions/` recording: the
  decoder-vs-tiles agnosticism, the fixed `multiview-*` layout
  collection, and the alternative-content (non-ad) scope widening.
- Glossary entries in `context/99-glossary.md` (multiview,
  `multiview-*` layout, tiles / HEVC tiles, view) marked *(proposed)*.

## Out of scope

- Custom layout (phase `03-custom-layout`), which is independent.
- Prescribing the multiview delivery mechanism (multi-decoder vs tiles)
  — the spec stays agnostic.
- Fixing how the N views' content is carried in the MPD (left to
  implementation); the live-content carriage question is captured as an
  open point, not resolved in this phase.
- Editing `context/` in this governance-scaffolding step (phase is in
  `planning` for review first).

## Stakeholders

- **Feature driver**: David Hassoun (WG contributor) — drove both
  multiview and custom layout.
- **Decision owner**: Nicolás Levy (CTO) — owns the design decisions
  encoded above, validates the `multiview-*` set against the reference
  image, and approves the ADR.

## Deliverables

1. New advanced-extension requirement(s) for multiview in
   `context/03-requirements.md`, plus the R3 extension.
2. New advanced-extension use-case(s) in `context/04-use-cases.md`.
3. ADR (decoder-vs-tiles agnosticism + fixed `multiview-*` collection +
   non-ad content scope) in `.project/decisions/`.
4. Glossary entries in `context/99-glossary.md`.

## Risks

- **Scope widening beyond ads.** The whole spec is otherwise about ad
  insertion; multiview presents non-ad alternative content. The ADR
  must state this consciously so the spec does not drift into a general
  presentation spec by accident. Multiview stays a bounded, opt-in
  extension.
- **Live-content carriage unknown.** Whether `ImportedMPD` (the baseline
  linear carrier) supports live is unresolved; if it does not, the N
  views need a different source for live. This is an open point that
  must be resolved in the design phase before the requirement can name a
  carrier — but since the requirement is deliberately
  implementation-agnostic, it does not block this phase's requirement
  text.
- **R3 extension coherence.** Extending R3 to two-or-more decoders and a
  tiles path must stay coherent with the existing device-class model
  (D1–D5) and the single-active-form / decoder-budget reasoning that
  already grounds R3, R22, R26, R27.

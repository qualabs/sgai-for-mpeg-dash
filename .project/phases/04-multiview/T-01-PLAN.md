# T-01 Plan — Multiview design

This plan captures the full design of the multiview feature as decided
by Nicolás, and enumerates the proposed fixed `multiview-*` layout set.
It is the source of truth for tasks T-02..T-08. This plan does not edit
`context/`; it specifies what the execution tasks will write.

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY) where it
anticipates normative text.

## Context

Multiview presents 2 up to a maximum of 4 videos at once, in one of a
fixed collection of named layouts. It is for **alternative content** —
a second feed, a different camera angle, a parallel match — and is
**not** an ad experience. David Hassoun drove the request. It is an
**advanced, optional extension**: an implementation conforms to the core
spec without it, and turning it on is opt-in. The requirement(s) and
use-cases must live in their own self-contained sections marked as an
advanced extension.

Multiview is **independent of custom layout** (phase 03): its layouts
are **fixed** presets, not free-form geometry. (A multiview could in
principle be built on a custom layout, but this mode defines its own
fixed preset set — this note stays in the spec.)

## Approach

Define multiview as a bounded, opt-in capability: a fixed collection of
named `multiview-*` layouts (2–4 videos), described at the level of
**what** the Player must be capable of, staying **agnostic** about the
delivery mechanism (multi-decoder vs HEVC tiles). Widen the spec's scope
consciously to cover non-ad alternative content, recorded in the ADR.
Extend R3 to express two-or-more decoders and the tiles single-decoder
signal. Leave the live-view carriage as an explicit open point for the
design phase.

## Design detail — decisions to encode

### D-1. Independent of custom layout; fixed layouts

Multiview does not build on custom layout. Multiview layouts are FIXED
named presets. Spec note to retain: one could compose a multiview with a
custom layout, but the multiview mode defines its own fixed preset set.

### D-2. Fixed `multiview-*` layout collection, 2 to 4 videos

A collection of named fixed layouts, each prefixed `multiview-*`,
supporting 2 up to a maximum of 4 videos. Each preset is one named
allowed layout. **Proposed set below**, derived from the WOXCON SCU41
multiviewer reference image
(https://woxcon.com/wp-content/uploads/2019/12/SCU41-MV-Layouts-1-e1576239329889.png).
Reference-image access: the image was retrieved and read directly (16
presets, up to 4 videos). The set below is the distillation Nicolás
should validate against the image before the use-cases lock the names.

The SCU41 shows 16 hardware presets, many of which are corner / side /
mirror variants of the same arrangement (e.g. four different PiP
corners; left-column vs right-column sidebars; top-strip vs
bottom-strip). Distilled into distinct arrangements:

**2 videos**
- **`multiview-dual`** — two equal boxes side by side (SCU41 Layout 2).
- **`multiview-pip`** — one primary video full-frame with a second video
  as a picture-in-picture inset in a corner (SCU41 Layouts 5–8; the
  corner is a fixed variant of this preset, not free-form).

**3 videos**
- **`multiview-triple-2-over-1`** — two boxes on the top row, one wide
  box on the bottom (SCU41 Layout 3).
- **`multiview-1-plus-2-sidebar`** — one primary large video plus two
  stacked video insets in a side column (SCU41 Layout 11 family).

**4 videos**
- **`multiview-quad`** — 2x2 grid of four equal boxes (SCU41 Layout 4).
- **`multiview-1-plus-3-sidebar`** — one primary large video plus three
  stacked video insets in a side column (SCU41 Layouts 9, 10, 13, 14 —
  left vs right column are fixed variants).
- **`multiview-1-plus-3-strip`** — one primary large video plus three
  video insets across a top or bottom strip (SCU41 Layouts 12, 15, 16 —
  top vs bottom strip are fixed variants).

Notes for validation:
- Corner (PiP), side (left/right column), and strip (top/bottom)
  positioning are **fixed variants of a named preset**, NOT free
  parameters. This fixedness is exactly what separates multiview from
  custom layout (phase 03).
- The count is bounded 2–4. SCU41 Layout 1 (single video) is the plain
  primary-content case, not a multiview preset.
- Naming (`multiview-dual`, `-pip`, `-triple-2-over-1`,
  `-1-plus-2-sidebar`, `-quad`, `-1-plus-3-sidebar`, `-1-plus-3-strip`)
  is proposed; Nicolás may rename before the use-cases land.

### D-3. Implementation-agnostic (decoder vs tiles)

The spec stays agnostic about HOW multiview is achieved. Two known ways:
(a) **multi-decoder** — two or more video decoders, one per view; (b)
**HEVC tiles** — a single decoder decoding a tiled stream. The spec
describes the multiview and the required capabilities (the **what**),
not the mechanism (the **how**). A device satisfies a `multiview-*`
layout if it can produce the N simultaneous views by either mechanism.

### D-4. View content — implementation-defined, live MUST be possible

How the N views' content is delivered is left to the implementation;
the requirement does NOT fix how the N views are carried. **Constraint:
multiview MUST be possible for live content.** Open point (see Risks and
T-06): the baseline linear carrier `<ImportedMPD>` may not allow live;
if so, independent live videos may need a different source, and tiles
are a different mechanism again. The requirement is written
implementation-agnostic so this open point does not block it.

### D-5. Scope — alternative content, NOT ads

Multiview presents **alternative content** (another feed, another angle,
another parallel match). It is **NOT** an ad experience. The requirement
states this boundary explicitly. This **widens the spec's scope beyond
ads** — a conscious decision recorded in the ADR (D-1 of the ADR).

### D-6. Audio — default primary, selection not foreclosed

By default, the audio of the **primary content** plays. The spec does
NOT foreclose implementing **audio selection** among the different
contents; it leaves that door open as a MAY.

### D-7. Capacity — extend R3

Extend **R3** (support a diverse range of device capabilities) to
express **two or more concurrent decoders** as a device capability, and
to signal the **tiles (single-decoder)** path as an alternative way a
device can satisfy a multiview. This keeps the device-capability model
(D1–D5) coherent with the decoder-budget reasoning already in R3, R22,
R26, R27, while admitting the tiles case where one decoder yields N
views.

## Requirement to draft (T-03) + R3 extension (T-04)

Proposed identifier for the new requirement: **R30** (next free stable
number; final number fixed at execution). Written as a **standalone
advanced-extension subsection** of `context/03-requirements.md`,
explicitly marked "advanced / optional extension — not required for core
conformance". States: the fixed `multiview-*` collection (2–4 videos);
implementation-agnostic capability (decoder or tiles, D-3);
alternative-content non-ad scope (D-5); live-content possibility (D-4);
default-audio / audio-selection posture (D-6); conformance sub-criteria
in the house style.

R3 extension (T-04): amend R3 in place (its number does not change) to
express two-or-more decoders as a device capability and to signal the
tiles single-decoder path.

## Use-case(s) to write (T-05)

Next free UC number. A standalone advanced-extension subsection of
`context/04-use-cases.md`, marked advanced / optional. It exercises a
`multiview-*` layout (e.g. `multiview-quad` and a 2-video
`multiview-pip`) with live alternative content, across device classes,
showing: a multi-decoder-capable class rendering N views; a
tiles-capable single-decoder class rendering N views via tiles; a class
that can do neither degrading gracefully; default primary-content audio;
and the non-ad framing (the views are alternative content, not ads).

## ADR to record (T-02)

`.project/decisions/0003-multiview-decoder-tiles-agnostic-fixed-layouts.md`,
drafted `status: proposed`, flipped to `accepted` on approval. Records:
(1) the alternative-content (non-ad) scope widening and why it is
bounded; (2) the fixed `multiview-*` layout collection (2–4 videos) and
why fixed rather than free-form (independence from custom layout); (3)
the decoder-vs-tiles agnosticism and the R3 extension.

## Risks / unknowns

- **Live-view carriage (open point, T-06).** `<ImportedMPD>` may not
  support live; the N live views may need an independent-video source,
  or tiles. Resolve in the design phase; does not block the agnostic
  requirement text.
- **Scope creep beyond ads.** Multiview is non-ad content; the ADR must
  bound it as an opt-in extension so the spec does not silently become a
  general presentation spec.
- **R3 coherence.** The two-or-more-decoder + tiles extension must stay
  consistent with D1–D5 and the R22 / R26 / R27 decoder-budget logic.
- **Layout-set validation.** The `multiview-*` names / set are proposed
  from the reference image and need Nicolás's sign-off (T-08).
- **Numbering.** R30 / the UC number are proposed; confirm next free
  numbers at execution.

## Verification (run before marking each task done)

- **T-02 (ADR):** file exists at
  `.project/decisions/0003-multiview-decoder-tiles-agnostic-fixed-layouts.md`;
  frontmatter `id: 0003`, `scope: phase-04`; body has Context /
  Decision / Consequences; the three decision strands (non-ad scope,
  fixed layouts, decoder-vs-tiles agnosticism) all appear.
- **T-03 (requirement):** new subsection in `03-requirements.md`
  explicitly marked advanced / optional; contiguous, self-contained; names
  the fixed `multiview-*` collection (2–4 videos), the
  implementation-agnostic capability, the non-ad scope, live
  possibility, and the audio posture; conformance sub-criteria present.
- **T-04 (R3 extension):** R3 text now expresses two-or-more decoders
  and the tiles single-decoder path; the D1–D5 model still reads
  coherently; `grep -n "tiles" context/03-requirements.md` returns a hit
  inside R3.
- **T-05 (use-case):** new UC in its own advanced-extension subsection;
  covers a multi-decoder path, a tiles single-decoder path, and a
  graceful-degradation path; default primary-content audio and the
  non-ad framing are explicit; coverage table updated if present.
- **T-06 (open point):** a written finding exists (in the phase folder
  or LOG) on whether `<ImportedMPD>` supports live and what carries the
  N live views; it names a concrete next step for the design phase.
- **T-07 (glossary):** the four terms resolve in `99-glossary.md`, each
  marked *(proposed)*.
- **T-08 (cross-refs + validation):** cited identifiers (R3, R15, R22,
  D1–D5) resolve; no broken internal links; the `multiview-*` set has
  Nicolás's explicit validation against the reference image recorded.

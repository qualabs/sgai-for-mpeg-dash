# T-01 Plan — Custom layout design

This plan captures the full design of the custom-layout feature as
decided by Nicolás. It is the source of truth for tasks T-02..T-06.
This plan does not itself edit `context/`; it specifies what the
execution tasks will write.

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY) where it
anticipates normative text.

## Context

The core SGAI spec defines a fixed set of layouts for non-linear ads:
overlay (the umbrella non-linear surface), side-by-side / double-box
(R26), L-shape / squeezeback (R27), and full-screen takeover. Spatial
arrangement in the core defers to HTML5 / CSS and the IAB CTV Ad Format
Guidelines by normative reference (R10, R12, ADR 0001) — the core spec
deliberately owns no explicit coordinate system.

David Hassoun drove a request for a layout in which an ad opportunity
can place an arbitrary number of elements at exact positions. This is
custom layout. It is an **advanced, optional extension**: an
implementation conforms to the core spec without it, and turning it on
is opt-in. The requirement and the use-cases must therefore live in
their own self-contained sections marked as an advanced extension, not
mixed into the core.

## Approach

Introduce custom layout as **one additional layout type** in the layout
vocabulary, alongside the base layouts, with its own coordinate model
(a reference viewport measured in pixels) and its own element model (N
elements, arbitrary geometry and Z-order, overlap permitted, one element
referencing the primary content). Keep the actor contract intact
(Publisher enables, ADS/APS positions) and bind degradation to the
existing R5 ordered fallback and R3 decoder budget so custom layout adds
no new degradation machinery. Record the architectural decision in an
ADR.

## Design detail — decisions to encode

### D-1. Custom layout is a new, additional layout type

Custom layout is added to the layout vocabulary as its own type. It sits
alongside — and does not subsume, replace, or generalise — overlay,
side-by-side (R26), L-shape (R27), and takeover. The base layouts are
unchanged. A slot's allowed-layouts declaration may list custom layout
as one more admissible layout token.

### D-2. Coordinate model — reference viewport, pixels

- A custom layout declares a **reference viewport**: a width x height in
  pixels (for example 1920x1080). This is the coordinate space of the
  layout.
- Every element's position (x, y of its top-left corner) and size
  (width, height) is expressed in **pixels relative to that reference
  viewport**.
- The Player maps the reference viewport onto the actual device screen.
  When the reference viewport equals the device screen, placement is
  pixel-exact.
- **Why pixels over percentages** (Nicolás): pixels against a known
  reference viewport give exact, unambiguous placement; percentages
  always carry rounding imprecision when converted to device pixels.
  This is the core rationale the ADR records.

### D-3. Element model — N elements, arbitrary geometry and Z-order

- A custom layout carries **N elements**.
- Exactly one element is the **primary-content reference** — the element
  that stands for the primary content surface inside the layout.
- Every element (the primary-content reference included) may be placed
  at **any position**, at **any size**, and at **any Z-order**.
- **Overlap is permitted.** When elements overlap, **Z-order** determines
  stacking (higher Z draws on top).
- Each non-primary element carries an ad creative under the admissible
  carrier set (R15: video, image, HTML).

### D-4. Who declares what (actor contract, R2)

- The **Publisher ENABLES** custom layout by including it among the
  layouts it permits for ads on the slot (the allowed-layouts
  declaration). Enabling is a Publisher constraint declaration, per R2.
- The **ADS decides** to use custom layout and the concrete per-element
  geometry (position, size, Z-order); the **APS carries** that into the
  resolution document as the custom-layout presentation option. This is
  the same ADS-decides / APS-carries contract R5 already defines for
  presentation options.
- The Player validates the custom-layout option against device
  capability and the Publisher's allowed layouts, then renders it or
  falls through (R5).

### D-5. Degradation — R5 ordered fallback + R3 decoder budget

- A custom-layout presentation option is one entry in the candidate's
  **ordered presentation-option list (R5)**. Document order is
  preference order; the Player renders the first satisfiable option.
- A custom layout's decoder / surface budget is the sum of its elements'
  budgets: each video element consumes a video decoder, each image / HTML
  element consumes the corresponding surface. If the total exceeds what
  the device class can composite (R3), the custom-layout option is not
  satisfiable and the Player falls through to the next option — exactly
  like the base layouts. No new degradation mechanism is introduced.

## Requirement to draft (T-03)

Proposed identifier: **R29** (next free stable number; final number
fixed at execution). Written as a **standalone advanced-extension
subsection** of `context/03-requirements.md`, explicitly marked
"advanced / optional extension — not required for core conformance".

The requirement states, at minimum:
- Custom layout is an additional layout type (D-1).
- The reference-viewport pixel coordinate model (D-2).
- The N-element model: arbitrary position / size / Z-order, overlap
  permitted, one primary-content-reference element (D-3).
- Publisher-enables / ADS-decides / APS-carries / Player-validates
  (D-4), tying back to R2.
- Ordered-fallback participation (R5) and decoder-budget compliance
  (R3) for degradation (D-5).
- Conformance criteria in the R-with-sub-criteria style used across
  `03-requirements.md` (e.g. R29.1 Publisher, R29.2 APS, R29.3 Player
  render, R29.4 Player degradation).

Keep the requirement self-contained per the `CLAUDE.md` rule: state
what it mandates, do not compare it to the base layouts except the one
minimal normative distinction that it is a distinct layout type an
implementer could otherwise conflate with overlay.

## Use-case(s) to write (T-04)

Next free UC number (UC-13 at time of writing; final number fixed at
execution). A standalone advanced-extension subsection of
`context/04-use-cases.md`, marked advanced / optional. It exercises a
custom layout with several elements (at least one video, the
primary-content reference, and an overlapping element with explicit
Z-order) across D1–D5, showing:
- D1 rendering the full custom layout,
- constrained classes (single-decoder, no-overlay) failing the
  custom-layout option and falling through to the next ordered option
  or to primary content (R5 / R3),
- the pixel-against-reference-viewport mapping producing exact
  placement when the viewport equals the screen.

## ADR to record (T-02)

`.project/decisions/0002-custom-layout-viewport-pixel-model.md`,
drafted `status: proposed` for review, flipped to `accepted` on
approval. Records: the decision to add a new layout type; the
viewport-relative pixel coordinate model and why pixels over
percentages; why a new type rather than generalising the base layouts;
and the conscious trade-off against R10 / ADR 0001 (custom layout owns
an explicit coordinate model, which the core deliberately does not —
justified because custom layout is opt-in and self-contained).

## Risks / unknowns

- **R10 posture.** The ADR must make the trade-off explicit rather than
  silently contradicting R10. Escape hatch: the advanced-extension
  framing isolates the coordinate model from the core so R10 continues
  to govern the core layouts.
- **Reference-viewport vs device aspect-ratio mismatch.** What the
  Player does when the reference viewport aspect ratio differs from the
  screen (letterbox, scale, clip) is a design-level detail; the plan
  flags it as an open point for the design phase, not resolved in the
  requirement text.
- **Numbering.** R29 / UC-13 are proposed; confirm the next free numbers
  at execution against the then-current `context/`.

## Verification (run before marking each task done)

- **T-02 (ADR):** the file exists at
  `.project/decisions/0002-custom-layout-viewport-pixel-model.md`;
  frontmatter has `id: 0002`, `scope: phase-03`, a valid status; body
  has Context / Decision / Consequences; the pixels-over-percentages
  rationale and the R10 trade-off both appear. `grep -c "R10"` returns
  >= 1.
- **T-03 (requirement):** the new subsection in `03-requirements.md` is
  explicitly marked as an advanced / optional extension; it is a
  contiguous self-contained block (not interleaved with core Rs); it
  names the reference-viewport pixel model, N elements, Z-order +
  overlap, the primary-content reference, the Publisher-enables /
  ADS-APS-positions split, and R5 + R3 degradation; conformance
  sub-criteria are present. Confirm by reading the subsection start to
  end.
- **T-04 (use-case):** the new UC is in its own advanced-extension
  subsection; it specifies behaviour for all of D1–D5; at least one
  device class demonstrates fall-through under R5 / R3; the coverage
  table (if updated) lists the new UC.
- **T-05 (glossary):** the four terms resolve in `99-glossary.md`, each
  marked *(proposed)*.
- **T-06 (cross-refs):** every cross-reference the new text makes (R2,
  R3, R5, R10, R15, ADR 0001) resolves to an existing anchor; no broken
  internal links introduced. Spot-check with a grep for each cited
  identifier.

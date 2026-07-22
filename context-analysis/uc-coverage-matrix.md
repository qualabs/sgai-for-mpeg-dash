[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Inputs: `../context/03-requirements.md` (R1..R28 — non-contiguous,
stable identifiers) and `../context/04-use-cases.md` (UC-01..UC-12).
Total UC count: 12. Total R count in use: 28 distinct stable
identifiers (R1..R28 — `../context/03-requirements.md` is the source of
truth; this matrix enumerates exactly the R-numbers it defines).

## Matrix 1 — UC × R

Rows = UCs, columns = Rs. **A** = the UC exercises the R; **·** =
not applicable / not exercised.

| UC \ R | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15 | R16 | R17 | R18 | R19 | R20 | R21 | R22 | R23 | R24 | R25 | R26 | R27 | R28 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UC-01 | · | A | A | A | A | A | A | · | · | · | · | · | A | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · |
| UC-02 | · | A | A | A | A | A | A | · | · | · | · | · | A | · | A | · | · | · | A | · | · | · | · | · | · | · | · | · |
| UC-03 | · | A | A | A | A | A | A | · | · | A | · | A | A | A | A | · | · | · | A | · | · | A | · | A | · | A | A | · |
| UC-04 | · | A | A | A | A | A | A | · | · | A | · | A | A | A | A | · | · | · | · | · | · | A | · | A | · | · | A | · |
| UC-05 | · | A | A | A | A | A | A | · | · | A | · | A | A | A | A | A | · | · | · | · | A | A | · | A | A | · | · | · |
| UC-06 | · | A | A | A | A | A | A | · | · | · | · | · | A | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · |
| UC-07 | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · |
| UC-08 | · | A | A | A | A | A | A | · | · | A | · | A | A | A | A | A | A | · | · | · | A | A | · | A | A | · | · | · |
| UC-09 | · | A | A | A | A | A | A | · | · | A | · | A | A | A | A | · | · | · | · | · | · | A | · | A | · | A | A | · |
| UC-10 | · | A | A | A | A | A | A | · | · | A | · | A | A | A | A | · | · | · | · | · | · | A | · | A | · | A | · | · |
| UC-11 | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A |
| UC-12 | · | A | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · |

## Matrix 2 — R × UC

Rows = Rs, columns = UCs. Trailing column tags each R as
`(covered)`, `(orphan)`, or `(governance)`.

| R \ UC | UC-01 | UC-02 | UC-03 | UC-04 | UC-05 | UC-06 | UC-07 | UC-08 | UC-09 | UC-10 | UC-11 | UC-12 | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | · | · | · | · | · | · | A | · | · | · | A | · | (covered) |
| R2 | A | A | A | A | A | A | · | A | A | A | A | A | (covered) |
| R3 | A | A | A | A | A | A | · | A | A | A | · | · | (covered) |
| R4 | A | A | A | A | A | A | · | A | A | A | · | · | (covered) |
| R5 | A | A | A | A | A | A | · | A | A | A | · | · | (covered) |
| R6 | A | A | A | A | A | A | · | A | A | A | · | · | (covered) |
| R7 | A | A | A | A | A | A | · | A | A | A | · | · | (covered) |
| R8 | · | · | · | · | · | · | · | · | · | · | · | · | (governance) |
| R9 | · | · | · | · | · | · | · | · | · | · | · | · | (governance) |
| R10 | · | · | A | A | A | · | · | A | A | A | · | · | (covered) |
| R11 | · | · | · | · | · | · | · | · | · | · | · | · | (governance) |
| R12 | · | · | A | A | A | · | · | A | A | A | · | · | (covered) |
| R13 | A | A | A | A | A | A | · | A | A | A | · | · | (covered) |
| R14 | · | · | A | A | A | · | · | A | A | A | · | A | (covered) |
| R15 | A | A | A | A | A | A | · | A | A | A | · | · | (covered) |
| R16 | · | · | · | · | A | · | · | A | · | · | · | · | (covered) |
| R17 | · | · | · | · | · | · | · | A | · | · | · | · | (covered) |
| R18 | · | · | · | · | · | · | · | · | · | · | · | · | (governance) |
| R19 | · | A | A | · | · | · | · | · | · | · | · | · | (covered) |
| R20 | · | · | · | · | · | · | · | · | · | · | · | A | (covered) |
| R21 | · | · | · | · | A | · | · | A | · | · | · | · | (covered) |
| R22 | · | · | A | A | A | · | · | A | A | A | · | · | (covered) |
| R23 | · | · | · | · | · | · | · | · | · | · | · | · | (orphan) |
| R24 | · | · | A | A | A | · | · | A | A | A | · | · | (covered) |
| R25 | · | · | · | · | A | · | · | A | · | · | · | · | (covered) |
| R26 | · | · | A | · | · | · | · | · | A | A | · | · | (covered) |
| R27 | · | · | A | A | · | · | · | · | A | · | · | · | (covered) |
| R28 | · | · | · | · | · | · | · | · | · | · | A | · | (covered) |

## Notes

### Cells added / corrected in this regeneration

The matrix now spans the full R1..R28 / UC-01..UC-12 range. Every `A`
is grounded in explicit spec text; nothing was inferred. The
non-obvious cells and their evidence:

- **R19 (playback speed) — UC-02, UC-03.** UC-02's *"Trick-play
  variant (playback speed != 1x)"* and UC-03's *"Playback speed"*
  paragraph both render an ad at the primary content's speed and cite
  R19 explicitly. R19 is therefore covered, not an orphan.
- **R20 (overlapping same-family windows) — UC-12.** UC-12
  (*"Overlapping same-family windows with fallback"*) exercises R20.1
  directly (first-window-wins, fallback on resolve failure). R20 is
  therefore covered, not an orphan.
- **R27 (L-shape / squeezeback) — UC-03, UC-04, UC-09.** UC-03's ad
  response models the L-shape per R27; UC-04's D3 / D4 sub-sections
  compose it per R27 / R27.3; UC-09's option 2 is the L-box, resolved
  per R27.3 on D3 / D4. UC-10 only *references* R27 in its notes to
  contrast it with the side-by-side (R26) it illustrates, so UC-10 is
  marked `·` for R27.
- **R28 (ClickThrough carrier) — UC-11.** UC-11 is the ClickThrough
  scenario: the APS populates the carrier (R28.1) and the Player reads
  it and fires the click-tracking (R28.2).
- **UC-11 row (R1, R2, R28).** R28 is the scenario's core; R1 is cited
  in UC-11's *"Backward compatibility"* paragraph (a legacy Player
  ignores the unknown carrier); R2 reflects the actor split the
  scenario exercises (the APS produces the carrier, the Player consumes
  it), consistent with how R2 is marked across the rendering UCs. UC-11
  explicitly separates the click-tracking from the timeline beacons of
  R6 / R13, so those stay `·`.
- **UC-12 row (R2, R14, R20).** R20 is the scenario's core; R14 is
  cited explicitly (the forms inside the chosen window are sequenced
  per R14); R2 reflects the APS-per-window resolution the scenario
  exercises. UC-12 states window selection is device-agnostic, so R3 /
  R5 stay `·`.

No cell was left as "por confirmar": every UC-11 / UC-12 / R27 / R28 /
R19 cell was determinable from the spec text above. The two judgment
calls worth a second look are UC-11 / R2 and UC-12 / R2 (the actor-role
reading of a narrow interaction / selection scenario).

### Orphan Rs

Rs with no UC coverage and not classified as governance.

- **R23 — Application-level ad metadata carrier**. No UC exercises a
  creative carrying `AdSystem` / `AdTitle` / `UniversalAdId` metadata
  via the optional SVTA-namespaced carrier. UC-11 covers the
  ClickThrough carrier (R28), which is a distinct, normative carrier,
  not the best-effort metadata carrier of R23. Proposed minimal UC:
  *"Overlay whose creative carries AdSystem / AdTitle metadata that a
  conformant Player MAY drop"* — exercises R23.1.

### Governance Rs (no UC by design)

R8 (justify additions), R9 (minimise net new constructs), R11 (no VAST
dependency), and R18 (ADS / APS API contracts out of scope) are
document-authoring constraints on the spec itself, not runtime
behaviours a use case can exercise. They are correctly uncovered.

### UCs with thin coverage

UCs that map to few Rs. R-count per UC: UC-01 8, UC-02 9, UC-03 16, UC-04 14, UC-05 16, UC-06 8, UC-07 1, UC-08 17, UC-09 15, UC-10 14, UC-11 3, UC-12 3.

- **UC-07 (Legacy Player)** — 1 R (R1 only). Thin by design: the
  cross-cutting backward-compat scenario tests R1 in isolation across
  device classes.
- **UC-11 (ClickThrough)** — 3 Rs (R1, R2, R28) and **UC-12
  (Overlapping windows + fallback)** — 3 Rs (R2, R14, R20). Both are
  intentionally narrow: UC-11 is a device-agnostic interaction
  scenario and UC-12 is a device-agnostic window-selection scenario.
  Neither dips below the 3-R threshold.

The remaining UCs range from 8 Rs (UC-01, UC-06, the simplest linear
scenarios) to 17 Rs (UC-08, the cross-family composition scenario).

### Bidirectional sanity check

The two matrices are generated by transposition from a single coverage
set, so by construction they cannot disagree on the `A` / `·` value for
any cell. Spot check on the newly added cells: UC-11/R28, UC-12/R20,
UC-03/R27, UC-09/R27, UC-02/R19 — all agree across both matrices.

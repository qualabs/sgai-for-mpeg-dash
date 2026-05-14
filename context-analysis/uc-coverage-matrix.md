[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Inputs: `../context/03-requirements.md` (mtime 2026-05-14 14:22:16)
and `../context/04-use-cases.md` (mtime 2026-05-14 14:22:31). 7 UCs
(UC-01..UC-07), 13 Rs (R1..R13; R8/R9/R10/R11/R12 are document-level
governance). Cells: `A` = UC text references the R explicitly or its
scenario directly exercises the R's obligation; `·` = not applicable
(conservative read — when in doubt, marked `·`).

## Matrix 1 — UC × R

| UC                           | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 |
|------------------------------|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|
| UC-01 Pre-roll               | ·  | A  | A  | A  | A  | ·  | A  | ·  | ·  | ·   | ·   | ·   | ·   |
| UC-02 Mid-roll               | ·  | A  | A  | A  | A  | ·  | A  | ·  | ·  | ·   | ·   | ·   | ·   |
| UC-03 Coexisting overlay     | ·  | A  | A  | A  | A  | ·  | A  | ·  | ·  | ·   | ·   | ·   | ·   |
| UC-04 Hybrid linear+overlay  | ·  | A  | A  | A  | A  | ·  | A  | ·  | ·  | ·   | ·   | ·   | ·   |
| UC-05 Pause-triggered ad     | ·  | A  | A  | A  | A  | ·  | A  | ·  | ·  | ·   | ·   | ·   | ·   |
| UC-06 Multi-ad break         | ·  | A  | A  | A  | A  | ·  | A  | ·  | ·  | ·   | ·   | ·   | ·   |
| UC-07 Legacy Player          | A  | ·  | A  | ·  | ·  | ·  | ·  | ·  | ·  | ·   | ·   | ·   | ·   |

## Matrix 2 — R × UC

| R                              | UC-01 | UC-02 | UC-03 | UC-04 | UC-05 | UC-06 | UC-07 | Tag          |
|--------------------------------|-------|-------|-------|-------|-------|-------|-------|--------------|
| R1  DASH 6th / legacy degrade  | ·     | ·     | ·     | ·     | ·     | ·     | A     | (covered)    |
| R2  Actor responsibilities     | A     | A     | A     | A     | A     | A     | ·     | (covered)    |
| R3  Diverse devices            | A     | A     | A     | A     | A     | A     | A     | (covered)    |
| R4  Max slot duration cap      | A     | A     | A     | A     | A     | A     | ·     | (covered)    |
| R5  Device-aware selection     | A     | A     | A     | A     | A     | A     | ·     | (covered)    |
| R6  Tracking carrier           | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (orphan)     |
| R7  Respect ADS order          | A     | A     | A     | A     | A     | A     | ·     | (covered)    |
| R8  Justify add/omission       | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R9  Minimise new constructs    | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R10 No layout system           | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R11 No VAST dependency         | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R12 IAB owns ad types          | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R13 Non-linear ad tracking     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (orphan)     |

## Notes

### Orphan Rs

- **R6 — Ad tracking carrier.** No UC body fires impression, quartile,
  or complete beacons in its scenario, nor mentions the callback
  Event scheme (`urn:mpeg:dash:event:callback:2015`). R6 is the
  runtime carrier mechanism and needs at least one UC that exercises
  beacon emission to be testable. **Proposed minimal close**:
  augment UC-01 and UC-03 with an explicit "Player fires impression
  at ad start; for linear (UC-01) fires quartile + complete beacons
  against the rendered video, for non-linear (UC-03) against the
  Broadcaster-declared overlay window" step in the per-device
  behaviour. Same extension picks up R13 as a side effect.
- **R13 — Non-linear ad tracking semantics.** Overlay UCs (UC-03,
  UC-04 overlay portion, UC-05) describe form selection and cap
  enforcement but say nothing about quartile beacon firing against
  `@maxDuration` or about R4 trim-stopping beacons. **Proposed
  minimal close**: extend UC-03 (then replay into UC-04/UC-05) with
  the R13.1/R13.2/R13.3 behaviour — impression at composition,
  quartiles against the slot window, stop at trim boundary. R6 and
  R13 close together via one UC pair (linear + overlay beacons).

### UCs with thin coverage

- **UC-07 — Legacy Player.** Maps to R1 + R3 (2 Rs, threshold 3).
  Acceptable thinness: UC-07 is the canonical R1 exercise and
  deliberately bypasses the rest of the flow (no ADS reach, no
  candidate validation, no cap enforcement, no form selection, no
  ordering). R3 is marked because the UC's "uniform across D1..D5"
  conclusion is itself a per-device-class defined behaviour
  (R3.2 — every class produces a defined outcome: continue primary
  uninterrupted). Surfacing R5, R7, or R4 here would distort the
  scenario; the spec's conformance chapter should flag UC-07 as
  intentionally narrow-scoped, not under-constrained.

### Bidirectional sanity check

Per-R UC sets agree between Matrix 1 and Matrix 2:

- R1: M1 col = {UC-07}; M2 row = {UC-07}. Match (1).
- R2, R4, R5, R7: M1 col = {UC-01..UC-06}; M2 row identical. Match (6 each).
- R3: M1 col = {UC-01..UC-07}; M2 row identical. Match (7).
- R6, R13: M1 col empty; M2 row empty (orphan tag). Match (0 each).
- R8, R9, R10, R11, R12: M1 col empty; M2 row empty (governance
  tag). Match (0 each).

No inconsistencies. Notes on near-misses kept on the `·` side under
the conservative rule:

- UC-03 prose references R10 explicitly ("using HTML/CSS layout
  primitives (per R10)") and UC-03/UC-04/UC-05 enumerate
  IAB-named layouts (banner, corner, L-shape, side-by-side,
  sidebar) that implicitly satisfy R12.2. Both Rs remain tagged
  governance — R10's conformance criteria (R10.1-R10.3) are all
  spec-document level, and R12's runtime obligations are not
  *tested* by UC text, only consistent with it. If a future
  revision wants to convert these implicit consistencies into
  explicit runtime tests, UC-03 is the right anchor.

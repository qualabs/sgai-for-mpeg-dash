[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Inputs: `../context/03-requirements.md` (mtime 2026-05-27, R1..R26 —
non-contiguous, stable identifiers) and `../context/04-use-cases.md`
(mtime 2026-05-27, UC-01..UC-10). Total UC count: 10. Total R count
in use: 26 distinct stable identifiers (R1..R26 — `../context/03-
requirements.md` is the source of truth; this matrix enumerates
exactly the R-numbers it defines).

## Matrix 1 — UC × R

Rows = UCs, columns = Rs. **A** = the UC exercises the R; **·** =
not applicable / not exercised.

| UC \ R | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15 | R16 | R17 | R18 | R19 | R20 | R21 | R22 | R23 | R24 | R25 | R26 |
|--------|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| UC-01  | ·  | A  | A  | A  | A  | A  | A  | ·  | ·  | ·   | ·   | ·   | A   | ·   | A   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   |
| UC-02  | ·  | A  | A  | A  | A  | A  | A  | ·  | ·  | ·   | ·   | ·   | A   | ·   | A   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   |
| UC-03  | ·  | A  | A  | A  | A  | A  | A  | ·  | ·  | A   | ·   | A   | A   | A   | A   | ·   | ·   | ·   | ·   | ·   | ·   | A   | ·   | A   | ·   | A   |
| UC-04  | ·  | A  | A  | A  | A  | A  | A  | ·  | ·  | A   | ·   | A   | A   | A   | A   | ·   | ·   | ·   | ·   | ·   | ·   | A   | ·   | A   | ·   | ·   |
| UC-05  | ·  | A  | A  | A  | A  | A  | A  | ·  | ·  | A   | ·   | A   | A   | A   | A   | A   | ·   | ·   | ·   | ·   | A   | A   | ·   | A   | A   | ·   |
| UC-06  | ·  | A  | A  | A  | A  | A  | A  | ·  | ·  | ·   | ·   | ·   | A   | ·   | A   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   |
| UC-07  | A  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   | ·   |
| UC-08  | ·  | A  | A  | A  | A  | A  | A  | ·  | ·  | A   | ·   | A   | A   | A   | A   | A   | A   | ·   | ·   | ·   | A   | A   | ·   | A   | A   | ·   |
| UC-09  | ·  | A  | A  | A  | A  | A  | A  | ·  | ·  | A   | ·   | A   | A   | A   | A   | ·   | ·   | ·   | ·   | ·   | ·   | A   | ·   | A   | ·   | A   |
| UC-10  | ·  | A  | A  | A  | A  | A  | A  | ·  | ·  | A   | ·   | A   | A   | A   | A   | ·   | ·   | ·   | ·   | ·   | ·   | A   | ·   | A   | ·   | A   |

## Matrix 2 — R × UC

Rows = Rs, columns = UCs. Trailing column tags each R as
`(covered)`, `(orphan)`, or `(governance)`.

| R \ UC | UC-01 | UC-02 | UC-03 | UC-04 | UC-05 | UC-06 | UC-07 | UC-08 | UC-09 | UC-10 | Tag |
|--------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-------|-----|
| R1     | ·     | ·     | ·     | ·     | ·     | ·     | A     | ·     | ·     | ·     | (covered) |
| R2     | A     | A     | A     | A     | A     | A     | ·     | A     | A     | A     | (covered) |
| R3     | A     | A     | A     | A     | A     | A     | ·     | A     | A     | A     | (covered) |
| R4     | A     | A     | A     | A     | A     | A     | ·     | A     | A     | A     | (covered) |
| R5     | A     | A     | A     | A     | A     | A     | ·     | A     | A     | A     | (covered) |
| R6     | A     | A     | A     | A     | A     | A     | ·     | A     | A     | A     | (covered) |
| R7     | A     | A     | A     | A     | A     | A     | ·     | A     | A     | A     | (covered) |
| R8     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R9     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R10    | ·     | ·     | A     | A     | A     | ·     | ·     | A     | A     | A     | (covered) |
| R11    | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R12    | ·     | ·     | A     | A     | A     | ·     | ·     | A     | A     | A     | (covered) |
| R13    | A     | A     | A     | A     | A     | A     | ·     | A     | A     | A     | (covered) |
| R14    | ·     | ·     | A     | A     | A     | ·     | ·     | A     | A     | A     | (covered) |
| R15    | A     | A     | A     | A     | A     | A     | ·     | A     | A     | A     | (covered) |
| R16    | ·     | ·     | ·     | ·     | A     | ·     | ·     | A     | ·     | ·     | (covered) |
| R17    | ·     | ·     | ·     | ·     | ·     | ·     | ·     | A     | ·     | ·     | (covered) |
| R18    | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R19    | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (orphan) |
| R20    | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (orphan) |
| R21    | ·     | ·     | ·     | ·     | A     | ·     | ·     | A     | ·     | ·     | (covered) |
| R22    | ·     | ·     | A     | A     | A     | ·     | ·     | A     | A     | A     | (covered) |
| R23    | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (orphan) |
| R24    | ·     | ·     | A     | A     | A     | ·     | ·     | A     | A     | A     | (covered) |
| R25    | ·     | ·     | ·     | ·     | A     | ·     | ·     | A     | ·     | ·     | (covered) |
| R26    | ·     | ·     | A     | ·     | ·     | ·     | ·     | ·     | A     | A     | (covered) |

## Notes

### Orphan Rs

Rs with no UC coverage and not classified as governance. These
signal either a missing use case to exercise the R, or conceptual
overlap with an R already covered. Each is listed with the minimal
UC that would close the gap, or the redundancy flag.

- **R19 — Ad playback speed follows primary**. No UC exercises a
  primary playback at a non-1x speed during an ad presentation.
  Proposed minimal UC: *"Mid-content slot triggered while the
  viewer is watching at 1.5x"* — the Player's `duration` is
  unchanged but the wall-clock on-screen duration shrinks to
  `duration / 1.5`. The UC would exercise R19.1, R19.2, R19.3
  jointly. Alternatively R19 can be promoted into an inline
  note inside UC-02 / UC-03 (mid-content scenarios).
- **R20 — First-window-wins fallback for overlapping same-family
  windows**. No UC sequences two overlapping same-family windows
  in the primary MPD. Proposed minimal UC: *"Two overlapping
  overlay windows; the APS for the first fails to respond, the
  Player falls through to the second"* — exercises R20.1
  directly. Could also be exercised by *two overlapping
  pause-ad windows* or *two overlapping linear inserts*.
- **R23 — Application-level ad metadata carrier**. No UC mentions
  a creative carrying `ClickThrough` / `AdSystem` / `AdTitle` /
  `UniversalAdId` (and a viewer interacting with the click-through
  link). Proposed minimal UC: *"Pre-roll with a clickable ad that
  carries ClickThrough"* — exercises R23.1. Click handling itself
  is application-layer (chapter 9 / non-normative); the spec only
  needs to validate the carrier shape.

### UCs with thin coverage

UCs that map to fewer than 3 Rs are under-constrained, or the
spec language could tighten them to invoke more Rs explicitly.

- **UC-07 (Legacy Player encounters new constructs)**: maps to 1 R
  (R1 only). Thinness is expected and **acceptable** — UC-07 is
  the cross-cutting backward-compat scenario; its whole point is
  to test R1 in isolation across device classes. No Rs to
  surface; thin coverage is the design.

No other UC is below the 3-R threshold; the rest range from 9 Rs
(UC-01 / UC-02 / UC-06, the simpler linear scenarios) to 16+ Rs
(UC-05 / UC-08, the action-triggered + cross-family ones).

### Bidirectional sanity check

The two matrices were generated by transposition, so by construction
they cannot disagree on the `A` / `·` value for any cell. Spot check
performed against five representative cells across UC × R and R × UC
(UC-03/R26, UC-08/R17, UC-05/R25, UC-09/R5, UC-04/R10) — all agree.
No mismatches surfaced.

R21 was double-checked: only UC-05 and UC-08 invoke pause-ad
presentation (UC-05 defines it, UC-08 composes it under the
overlay→pause-ad transition), matching the matrix.

R26 was double-checked: UC-03 mentions side-by-side as one of the
allowed-layout family in its overlay scenario; UC-09 walks side-by-
side as option 1 of the ordered options; UC-10 is the worked R26
illustration. UC-04 (hybrid linear + overlay) does NOT exercise
side-by-side (the overlay portion is banner-only by Publisher
intent), so it is correctly marked `·`.

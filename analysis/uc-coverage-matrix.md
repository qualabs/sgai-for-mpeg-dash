[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Inputs: `../context/03-requirements.md` (R1..R13, of which R8/R9/R10 are
document-level governance, plus R11/R12/R13 newly added in this
edition), `../context/04-use-cases.md` (UC-01..UC-07). Total UCs: 7.
Total Rs: 13 (R1..R10 plus R11..R13).

## Matrix 1 — UC × R

Cells: `A` = UC exercises the requirement; `·` = not applicable.

| UC | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 |
|----|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|
| UC-01 (pre-roll, linear) | · | A | A | A | A | A | A | · | · | · | A | · | · |
| UC-02 (mid-roll, linear) | · | A | A | A | A | A | A | · | · | · | A | · | · |
| UC-03 (coexisting overlay) | · | A | A | A | A | A | A | · | · | A | A | A | A |
| UC-04 (hybrid linear + overlay) | · | A | A | A | A | A | A | · | · | A | A | A | A |
| UC-05 (pause-triggered ad) | · | A | A | A | A | A | A | · | · | A | A | A | A |
| UC-06 (multi-ad break) | · | A | A | A | A | A | A | · | · | · | A | · | · |
| UC-07 (legacy Player) | A | · | A | · | · | · | · | · | · | · | · | · | · |

## Matrix 2 — R × UC

| R | UC-01 | UC-02 | UC-03 | UC-04 | UC-05 | UC-06 | UC-07 | Tag |
|---|-------|-------|-------|-------|-------|-------|-------|-----|
| R1  (graceful degradation) | · | · | · | · | · | · | A | (covered) |
| R2  (actor roles) | A | A | A | A | A | A | · | (covered) |
| R3  (device classes) | A | A | A | A | A | A | A | (covered) |
| R4  (max slot duration) | A | A | A | A | A | A | · | (covered) |
| R5  (device-aware selection) | A | A | A | A | A | A | · | (covered) |
| R6  (tracking carrier) | A | A | A | A | A | A | · | (covered) |
| R7  (ADS-returned order) | A | A | A | A | A | A | · | (covered) |
| R8  (justify additions) | · | · | · | · | · | · | · | (governance) |
| R9  (minimise new constructs) | · | · | · | · | · | · | · | (governance) |
| R10 (no layout system) | · | · | A | A | A | · | · | (covered) |
| R11 (no VAST dependency) | A | A | A | A | A | A | · | (covered) |
| R12 (IAB owns ad types) | · | · | A | A | A | · | · | (covered) |
| R13 (non-linear tracking) | · | · | A | A | A | · | · | (covered) |

## Notes

### Orphan Rs

R8 and R9 are document-level governance and are intentionally not
exercised by any UC; they bind the norm document and the proposal
authoring process, not runtime actor behaviour. R10 has both
dimensions: as governance (norm MUST NOT define a parallel layout
standard) and as runtime (Player composes overlays using HTML/CSS
primitives) — surfaced via UC-03/UC-04/UC-05. No non-governance R
is orphan.

R1 is exercised only by UC-07, which is the canonical legacy-Player
scenario. This is by design — UC-07 is the cross-cutting backward-
compat scenario any of UC-01..UC-06 may degrade to.

### UCs with thin coverage

UC-07 maps to only R1 + R3 (2 Rs). Acceptable: UC-07 is a
cross-cutting degradation scenario whose entire purpose is to
exercise R1; the other Rs are bypassed by construction (legacy
Player never reaches the ADS, never validates, never enforces). R3
hits because the UC body explicitly states behaviour is uniform
across D1..D5.

UC-01, UC-02, UC-06 each map to 8 Rs (R2-R7, R11). They skip
R10/R12/R13 because linear ads do not introduce overlay templates,
IAB-defined non-linear ad types, or non-linear tracking — those are
non-linear concerns by construction. Coverage is healthy.

UC-03, UC-04, UC-05 each map to 11 Rs (R2-R7, R10-R13). These are
the non-linear scenarios and the principal new content of the norm.

### Bidirectional sanity check

For every R the count of `A` cells in row R of Matrix 2 equals the
count of `A` cells in column R of Matrix 1.

- R1: column = 1 (UC-07); row = 1. OK.
- R2: column = 6 (UC-01..UC-06); row = 6. OK.
- R3: column = 7 (all UCs); row = 7. OK.
- R4..R7: column = 6 (UC-01..UC-06); row = 6. OK.
- R8..R9: column = 0; row = 0 (governance). OK.
- R10: column = 3 (UC-03, UC-04, UC-05); row = 3. OK.
- R11: column = 6 (UC-01..UC-06); row = 6. OK.
- R12: column = 3 (UC-03, UC-04, UC-05); row = 3. OK.
- R13: column = 3 (UC-03, UC-04, UC-05); row = 3. OK.

No mismatches between the two views.

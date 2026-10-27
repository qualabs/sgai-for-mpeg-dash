[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Inputs: `../context/03-requirements.md` (mtime 2026-10-27 12:35:35 -0300,
last commit `d87fcef`) and `../context/04-use-cases.md` (mtime 2026-10-27
12:34:13 -0300, last commit `e1666a0`). 22 use cases (UC-01..UC-22), 45
requirements (R1..R42, R44, R47, R48; R43, R45 and R46 do not exist).
`A` = the UC cites the R or its scenario directly exercises the R's
obligation; `·` otherwise (conservative).

## Matrix 1 — UC × R

| UC | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15 | R16 | R17 | R18 | R19 | R20 | R21 | R22 | R23 | R24 | R25 | R26 | R27 | R28 | R29 | R30 | R31 | R32 | R33 | R34 | R35 | R36 | R37 | R38 | R39 | R40 | R41 | R42 | R44 | R47 | R48 | #A |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UC-01 | · | · | A | A | A | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 4 |
| UC-02 | · | · | A | A | A | · | A | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 6 |
| UC-03 | A | · | A | A | A | · | A | · | · | A | · | A | A | · | · | · | · | · | A | · | · | A | A | · | · | A | A | · | · | · | · | · | · | · | A | · | · | · | · | · | A | A | A | · | · | 17 |
| UC-04 | · | A | A | A | A | · | A | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | 8 |
| UC-05 | · | · | A | A | A | · | A | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | A | A | · | · | · | · | · | · | · | · | 9 |
| UC-06 | · | A | A | A | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 5 |
| UC-07 | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | 2 |
| UC-08 | · | · | A | A | · | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · | A | A | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 7 |
| UC-09 | · | A | A | A | A | · | · | · | · | · | · | A | A | · | · | · | · | · | · | · | · | · | · | · | · | A | A | · | A | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | 10 |
| UC-10 | · | · | A | A | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 7 |
| UC-11 | A | · | · | · | · | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 4 |
| UC-12 | · | · | A | · | A | · | · | · | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 5 |
| UC-13 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 8 |
| UC-14 | A | · | A | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | 6 |
| UC-15 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | A | A | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | 9 |
| UC-16 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · | · | · | · | 7 |
| UC-17 | A | · | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | A | · | A | · | A | · | · | · | · | · | 11 |
| UC-18 | · | · | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | 6 |
| UC-19 | A | · | A | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 4 |
| UC-20 | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | 2 |
| UC-21 | · | · | A | A | · | · | · | · | · | · | · | · | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | A | · | · | · | A | · | · | · | · | · | 8 |
| UC-22 | · | · | A | A | · | · | · | · | · | · | · | · | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | 5 |

## Matrix 2 — R × UC

Columns are UC numbers (`01` = UC-01). The governance tag takes precedence
over the coverage count. Governance = every conformance criterion binds the
spec document or an arrangement outside it: R8, R9, R10, R23 are
document-level; R18 binds Publisher / APS / ADS out-of-band; R11 binds the
spec's citations, and its one Player criterion, R11.2, has no scenario to
run in.

| R | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | #A | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | · | · | A | · | · | · | A | · | · | · | A | · | · | A | · | · | A | · | A | · | · | · | 6 | (covered) |
| R2 | · | · | · | A | · | A | · | · | A | · | · | · | A | · | A | A | · | · | · | · | · | · | 6 | (covered) |
| R3 | A | A | A | A | A | A | · | A | A | A | · | A | A | A | A | A | A | A | A | A | A | A | 20 | (covered) |
| R4 | A | A | A | A | A | A | · | A | A | A | · | · | A | A | A | A | A | A | · | · | A | A | 17 | (covered) |
| R5 | A | A | A | A | A | · | · | · | A | A | · | A | A | A | A | A | A | A | A | · | · | · | 15 | (covered) |
| R6 | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R7 | A | A | A | A | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 6 | (covered) |
| R8 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R9 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R10 | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (governance) |
| R11 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R12 | · | · | A | A | · | · | · | · | A | A | · | · | A | · | A | A | A | A | · | · | · | · | 9 | (covered) |
| R13 | · | A | A | · | · | A | · | · | A | · | A | · | · | · | · | · | · | · | · | · | A | A | 7 | (covered) |
| R14 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | A | A | 3 | (covered) |
| R15 | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R16 | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 2 | (covered) |
| R17 | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R18 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R19 | · | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 2 | (covered) |
| R20 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | A | · | · | · | · | · | 2 | (covered) |
| R21 | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R22 | · | · | A | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 2 | (covered) |
| R23 | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (governance) |
| R24 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R25 | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R26 | · | · | A | · | · | · | · | · | A | A | · | · | A | · | · | · | · | · | · | · | · | · | 4 | (covered) |
| R27 | · | · | A | A | · | · | · | · | A | A | · | · | A | · | A | · | A | A | · | · | · | · | 8 | (covered) |
| R28 | · | · | · | · | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | 2 | (covered) |
| R29 | · | · | · | · | · | · | · | · | A | · | · | · | A | · | A | · | · | · | A | · | · | · | 4 | (covered) |
| R30 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | A | · | A | · | · | · | · | · | 3 | (covered) |
| R31 | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 2 | (covered) |
| R32 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R33 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R34 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | 1 | (covered) |
| R35 | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | 2 | (covered) |
| R36 | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | A | · | 3 | (covered) |
| R37 | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R38 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | A | · | · | · | · | · | 3 | (covered) |
| R39 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | 1 | (covered) |
| R40 | · | · | · | A | · | · | A | · | · | · | · | · | · | A | · | · | A | · | · | · | A | A | 6 | (covered) |
| R41 | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | 2 | (covered) |
| R42 | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | 2 | (covered) |
| R44 | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R47 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R48 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | 1 | (covered) |

## Notes

### Orphan Rs

| R | Gap | Minimal UC to close it |
|---|---|---|
| R24 | Non-AV asset carrier. Image / HTML forms appear in UC-03, 05, 09, 10, 13–18, 21, 22; none states how the URL travels. | One line in UC-03 (Ad response): the image / HTML option URL rides a DR-6 carrier, not an RFC 4337 `@mimeType` path. |
| R32 | Pause candidates exhausted while the viewer is still paused. | UC-05 variant: viewer stays paused past the last candidate; one outcome per APS-declared value. |
| R33 | Pause-ad measurement via the base `PlayList` metric. | UC-05 variant: paused interval derived from `PlayList`, filled duration measured against it. |
| R47 | Viewability beacons (three outcomes, fired once per impression). | UC-03 variant: the candidate carries the three beacons; a Player that determines viewability fires the matching one, a Player that does not fires the undetermined one. |

None is redundant: each carries an obligation no other R states. R32 and
R33 attach to UC-05; R24 and R47 to UC-03.

### UCs with thin coverage

| UC | #A | Candidate Rs to surface |
|---|---|---|
| UC-07 | 2 | R1, R40 only. R1.4 / R1.5 are the plausible additions; R8 / R9 are the document-level side of the same contract. Thinness is inherent to a cross-cutting legacy scenario. |
| UC-20 | 2 | R48 and R3. The Publisher intent is "a linear break, as in UC-02" but the UC never exercises R4 / R7 on it; naming the cap and the candidate walk would surface them. R6 / R13 are plausible if the icon's display is tracked. |

### Bidirectional sanity check

Both matrices are generated from one UC→R set and parsed back from this
file: 22 × 45 cells, per-R and per-UC counts and tags compared — **no
mismatch**. Mapping decisions worth auditing:

- **UC-03 trailing paragraphs.** Verification (R44.3, R23.2), Degradation
  (R1.6, R42), Dismissal (R35, R42) and Audio (R41.1) each exercise their
  R; marked `A`. R23 stays tagged governance with this one citation, as
  R10 does with UC-03's "per R10".
- **UC-09 resource failure.** The 404 note exercises R5.9 and R42.1 (the
  failure beacon does not fire because an option rendered); the
  per-option impression beacon is R13.6. Marked `A` on R5, R42, R13.
- **UC-06 slot beacons.** Slot-start / slot-end and late join are R13.7;
  marked `A` on R13.
- **UC-19.** Renders UC-09's option 2 by reference; R26 / R27 are not
  exercised by its own text, `·`. R1 (R1.6), R3, R5, R29 (R29.10) are `A`.
- **UC-18.** Dismissal appears only as an end condition of R41.7; R35 `·`.
- **UC-21 and R40.** "B is cut there … (R40)" is the window-end bound that
  R34.8 itself attributes to R40; consistent, marked `A`.
- **UC-22.** A then B is R14 sequencing without naming it; `A`. The
  once-per-session remark is cited to R40.4, not R34; R34 `·`.
- **UC-17 / UC-15 and R30.** A window that presents no ad (UC-17) and
  "the APS emits no candidate for this device" (UC-15 D2) are the R30
  case without naming it; `A`.

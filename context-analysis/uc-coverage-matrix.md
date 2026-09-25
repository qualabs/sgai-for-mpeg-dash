[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Inputs: `../context/03-requirements.md` (mtime 2026-09-25 16:13:52 -0300) and
`../context/04-use-cases.md` (mtime 2026-09-25 16:13:52 -0300). 16 use cases
(UC-01..UC-16), 39 requirements (R1..R39). `A` = the UC cites the R or its
scenario directly exercises the R's obligation; `·` otherwise (conservative).

## Matrix 1 — UC × R

| UC | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15 | R16 | R17 | R18 | R19 | R20 | R21 | R22 | R23 | R24 | R25 | R26 | R27 | R28 | R29 | R30 | R31 | R32 | R33 | R34 | R35 | R36 | R37 | R38 | R39 | #A |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UC-01 | · | · | A | A | A | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 4 |
| UC-02 | · | · | A | A | A | · | A | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 6 |
| UC-03 | · | · | A | A | A | · | A | · | · | A | · | A | A | · | · | · | · | · | A | · | · | · | · | · | · | A | A | · | · | · | · | · | · | · | · | · | · | · | · | 10 |
| UC-04 | · | A | A | A | A | · | A | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | 7 |
| UC-05 | · | · | A | · | A | · | A | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | A | A | · | · | 8 |
| UC-06 | · | · | A | A | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 3 |
| UC-07 | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 1 |
| UC-08 | · | · | A | A | · | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · | A | A | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | 7 |
| UC-09 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | · | A | · | · | · | · | · | · | · | · | · | · | 8 |
| UC-10 | · | · | A | A | A | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · | · | · | · | · | · | · | · | · | · | 6 |
| UC-11 | A | · | · | · | · | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | 4 |
| UC-12 | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | 3 |
| UC-13 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | · | A | · | · | · | · | · | · | · | · | · | · | 8 |
| UC-14 | · | · | A | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | 4 |
| UC-15 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | A | · | 7 |
| UC-16 | · | · | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | 6 |

## Matrix 2 — R × UC

Columns are UC numbers (`01` = UC-01). Governance tag takes precedence over
the coverage count.

| R | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | #A | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | · | · | · | · | · | · | A | · | · | · | A | · | · | · | · | · | 2 | (covered) |
| R2 | · | · | · | A | · | · | · | · | A | · | · | · | A | · | A | · | 4 | (covered) |
| R3 | A | A | A | A | A | A | · | A | A | A | · | · | A | A | A | A | 13 | (covered) |
| R4 | A | A | A | A | · | A | · | A | A | A | · | · | A | A | A | A | 12 | (covered) |
| R5 | A | A | A | A | A | · | · | · | A | A | · | · | A | A | A | A | 11 | (covered) |
| R6 | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | 1 | (covered) |
| R7 | A | A | A | A | A | A | · | · | · | · | · | · | · | · | · | · | 6 | (covered) |
| R8 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R9 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R10 | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (governance) |
| R11 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R12 | · | · | A | A | · | · | · | · | A | · | · | · | A | · | A | A | 6 | (covered) |
| R13 | · | A | A | · | · | · | · | · | · | · | A | · | · | · | · | · | 3 | (covered) |
| R14 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | 1 | (covered) |
| R15 | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | 1 | (covered) |
| R16 | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | 2 | (covered) |
| R17 | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | 1 | (covered) |
| R18 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R19 | · | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | 2 | (covered) |
| R20 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | 1 | (covered) |
| R21 | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | 1 | (covered) |
| R22 | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | 1 | (covered) |
| R23 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R24 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R25 | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R26 | · | · | A | · | · | · | · | · | A | A | · | · | A | · | · | · | 4 | (covered) |
| R27 | · | · | A | A | · | · | · | · | A | A | · | · | A | · | · | · | 5 | (covered) |
| R28 | · | · | · | · | · | · | · | · | · | · | A | · | · | A | · | · | 2 | (covered) |
| R29 | · | · | · | · | · | · | · | · | A | · | · | · | A | · | A | · | 3 | (covered) |
| R30 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | 1 | (covered) |
| R31 | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | 2 | (covered) |
| R32 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R33 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R34 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R35 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R36 | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R37 | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R38 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | 2 | (covered) |
| R39 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | 1 | (covered) |

## Notes

### Orphan Rs

| R | Gap | Minimal UC to close it |
|---|---|---|
| R23 | Application-level metadata carrier; optional both ways, no scenario reads it. | Extend UC-11: candidate carries `AdTitle` / `AdSystem` in the SVTA carrier; a Player that ignores it renders identically. |
| R24 | Non-AV asset carrier; image / HTML forms appear in UC-03, 05, 09, 10, 13–16 but none states how the URL travels. | One line in UC-03 (Ad response): image / HTML option URL rides the R24 carrier, not `@mimeType`. |
| R32 | Pause candidates exhausted while still paused. | UC-05 variant: viewer stays paused past the last candidate; APS declares repeat / request-again / stop, one outcome shown per value. |
| R33 | Pause-ad measurement via `PlayList` metric. | UC-05 variant: paused 40 s, ad shown 25 s; the reported filled duration is derived from `PlayList`. |
| R34 | Once-per-session pause window. | UC-05 variant: second pause inside the same window shows no ad. |
| R35 | Viewer dismissal of a slot. | UC-03 variant: APS allows dismissal after N s; dismiss before N is ignored, after N ends the whole slot. |

None of the six is redundant with another R: each carries an obligation no
other R states. R32, R33 and R34 all attach naturally to UC-05.

### UCs with thin coverage

| UC | #A | Candidate Rs to surface |
|---|---|---|
| UC-07 | 1 | R9 / R8 are the document-level side of the same contract (extension points only); runtime-side, R30 does not apply (no request is issued). Only R1 is genuinely exercised; the thinness is inherent to a cross-cutting scenario, not an under-constraint. |

UC-12 (3) sits at the threshold; R7 (drop, never reorder) is the plausible
addition if the fallback window's document carries several candidates.

### Bidirectional sanity check

Both matrices are rendered from a single UC→R mapping, and the per-R count in
Matrix 2 was re-derived from the Matrix 1 cells: **no mismatch** (39/39 Rs
agree). Coherence issues found in the inputs while building the matrix:

- **UC-03 vs R22.** UC-03 declares "Maximum number of concurrent overlays for
  this slot is bounded" and a "concurrency cap" in D1, while R22 permits at
  most one active non-linear form. R22 is left `·` for UC-03.
- **UC-05 vs R4 / R31.** UC-05 declares "Maximum display duration before
  automatic dismissal is bounded"; R4 states a pause slot has no declared
  duration for a cap to bound, and R31 that its length is set by the viewer.
  R4 is left `·` for UC-05.
- **R10 is tagged governance but has one citation** (UC-03, "per R10"). The
  tag follows the prompt; the citation is real.
- **R11 and R18 are tagged governance**: both constrain what the document
  depends on or defines (no VAST dependency; APS-to-ADS API not defined), not
  a runtime behaviour a UC can exercise.

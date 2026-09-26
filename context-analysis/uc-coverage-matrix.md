[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Inputs: `../context/03-requirements.md` (mtime 2026-09-26 10:47:35 -0300) and
`../context/04-use-cases.md` (mtime 2026-09-26 10:49:06 -0300). 17 use cases
(UC-01..UC-17), 40 requirements (R1..R40). `A` = the UC cites the R or its
scenario directly exercises the R's obligation; `·` otherwise (conservative).

## Matrix 1 — UC × R

| UC | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15 | R16 | R17 | R18 | R19 | R20 | R21 | R22 | R23 | R24 | R25 | R26 | R27 | R28 | R29 | R30 | R31 | R32 | R33 | R34 | R35 | R36 | R37 | R38 | R39 | R40 | #A |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UC-01 | · | · | A | A | A | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 4 |
| UC-02 | · | · | A | A | A | · | A | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 6 |
| UC-03 | · | · | A | A | A | · | A | · | · | A | · | A | A | · | · | · | · | · | A | · | · | A | · | · | · | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | 11 |
| UC-04 | · | A | A | A | A | · | A | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | A | 8 |
| UC-05 | · | · | A | A | A | · | A | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | A | A | · | · | · | 9 |
| UC-06 | · | A | A | A | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 4 |
| UC-07 | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | 2 |
| UC-08 | · | · | A | A | · | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · | A | A | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | 7 |
| UC-09 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | · | A | · | · | · | · | · | · | · | · | · | · | · | 8 |
| UC-10 | · | · | A | A | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | 7 |
| UC-11 | A | · | · | · | · | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | 4 |
| UC-12 | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | 3 |
| UC-13 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | · | A | · | · | · | · | · | · | · | · | · | · | · | 8 |
| UC-14 | A | · | A | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | A | 6 |
| UC-15 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | A | A | · | · | · | · | · | · | · | A | · | · | 9 |
| UC-16 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | · | 7 |
| UC-17 | A | · | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | A | · | · | · | A | 10 |

## Matrix 2 — R × UC

Columns are UC numbers (`01` = UC-01). The governance tag takes precedence
over the coverage count. Governance = every conformance criterion binds the
spec document (R8, R9, R10, R18, R23 are document-level; R11 binds the spec's
citations, and its one Player criterion, R11.2, has no scenario to run in).

| R | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | #A | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | · | · | · | · | · | · | A | · | · | · | A | · | · | A | · | · | A | 4 | (covered) |
| R2 | · | · | · | A | · | A | · | · | A | · | · | · | A | · | A | A | · | 6 | (covered) |
| R3 | A | A | A | A | A | A | · | A | A | A | · | · | A | A | A | A | A | 14 | (covered) |
| R4 | A | A | A | A | A | A | · | A | A | A | · | · | A | A | A | A | A | 14 | (covered) |
| R5 | A | A | A | A | A | · | · | · | A | A | · | · | A | A | A | A | A | 12 | (covered) |
| R6 | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | 1 | (covered) |
| R7 | A | A | A | A | A | A | · | · | · | · | · | · | · | · | · | · | · | 6 | (covered) |
| R8 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R9 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R10 | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (governance) |
| R11 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R12 | · | · | A | A | · | · | · | · | A | A | · | · | A | · | A | A | A | 8 | (covered) |
| R13 | · | A | A | · | · | · | · | · | · | · | A | · | · | · | · | · | · | 3 | (covered) |
| R14 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | 1 | (covered) |
| R15 | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | 1 | (covered) |
| R16 | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | 2 | (covered) |
| R17 | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R18 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R19 | · | A | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 2 | (covered) |
| R20 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | A | 2 | (covered) |
| R21 | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R22 | · | · | A | · | · | · | · | A | · | · | · | · | · | · | · | · | · | 2 | (covered) |
| R23 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R24 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R25 | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R26 | · | · | A | · | · | · | · | · | A | A | · | · | A | · | · | · | · | 4 | (covered) |
| R27 | · | · | A | A | · | · | · | · | A | A | · | · | A | · | A | · | A | 7 | (covered) |
| R28 | · | · | · | · | · | · | · | · | · | · | A | · | · | A | · | · | · | 2 | (covered) |
| R29 | · | · | · | · | · | · | · | · | A | · | · | · | A | · | A | · | · | 3 | (covered) |
| R30 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | A | · | A | 3 | (covered) |
| R31 | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | 2 | (covered) |
| R32 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R33 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R34 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R35 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R36 | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | A | 2 | (covered) |
| R37 | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R38 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | · | 2 | (covered) |
| R39 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | 1 | (covered) |
| R40 | · | · | · | A | · | · | A | · | · | · | · | · | · | A | · | · | A | 4 | (covered) |

## Notes

### Orphan Rs

| R | Gap | Minimal UC to close it |
|---|---|---|
| R24 | Non-AV asset carrier; image / HTML forms appear in UC-03, 05, 09, 10, 13–17, none states how the URL travels. | One line in UC-03 (Ad response): the image / HTML option URL rides a DR-6 carrier, not `@mimeType`. |
| R32 | Pause candidates exhausted while the viewer is still paused. | UC-05 variant: viewer stays paused past the last candidate; one outcome per declared value (repeat / request-again / stop, default stop). |
| R33 | Pause-ad measurement via the `PlayList` metric. | UC-05 variant: paused 40 s, ad shown 25 s; the filled fraction is derived from `PlayList` (`UserRequest` → `Resume`), a `Rebuffering` stop is not a pause. |
| R34 | Once-per-session pause window. | UC-05 variant: a second pause inside the same window shows no ad; a first pause that rendered nothing leaves the window available. |
| R35 | Viewer dismissal of a slot (incl. R35.8, base skip declaration on linear). | UC-03 variant: APS allows dismissal after N s; no control before N, after N dismissal ends the whole slot and later beacons do not fire. A UC-01 line for R35.8. |

None of the five is redundant: each carries an obligation no other R states.
R32, R33 and R34 attach naturally to UC-05. R40 is new and covered by four
UCs: UC-04 (on top, R40.5), UC-07 and UC-17 (supersede, R40.3), UC-14
(default, on top and supersede against a replacement; window inside the
replacement, R40.6).

### UCs with thin coverage

| UC | #A | Candidate Rs to surface |
|---|---|---|
| UC-07 | 2 | R1 and R40 (supersede as the VOD legacy fallback). R1.4 (abort-and-continue) and R1.5 (base answer wins) are the plausible additions; R8 / R9 are the document-level side of the same contract. The thinness is inherent to a cross-cutting legacy scenario, not an under-constraint. |

UC-12 (3) sits at the threshold; R7 (drop, never reorder) is the plausible
addition if the fallback window's document carries several candidates, and
R20.5 (fallback window binds its own declarations) has no scenario naming it.

### Bidirectional sanity check

Both matrices were parsed back from this file and compared cell by cell
(17 × 40 cells) and by per-R / per-UC count: **no mismatch**. Coherence issues
found in the inputs while building the matrix:

- **UC-17 and R38.** UC-17 declares allowed layouts on the overlay window
  but never says the Player forwards them to the APS (R38.2), unlike UC-15;
  marked `·`. Likewise its linear break resolves "as in UC-02" without
  naming R7; marked `·`.
- **UC-17 and R30.** "A resolution document with no candidates" is cited as
  R20.1; the document-not-error obligation is R30.1 / R30.2, marked `A`
  though not named.
- **UC-15 D2 and R30.** "The APS emits no candidate for this device" is the
  R30 case (document with no candidates), marked `A`; the UC ends at R3's skip
  and does not name R30.
- **UC-14 and UC-17, legacy line.** Both now carry a legacy-Player outcome
  pointing to UC-07; marked `A` on R1 (the document-level placement that
  makes the skip hold, R1.1).
- **R10 is tagged governance but has one citation** (UC-03, "per R10"). The
  tag follows the prompt; the citation is real.

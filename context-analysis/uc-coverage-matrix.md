[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Built from [`../context/03-requirements.md`](../context/03-requirements.md)
(mtime 2026-09-15 21:54) and [`../context/04-use-cases.md`](../context/04-use-cases.md)
(mtime 2026-09-15 17:41): **13 use cases** (UC-01..UC-13) × **30 requirements**
(R1..R30), 80 `A` cells. A cell is `A` when the UC names the requirement or its
scenario exercises the requirement's obligation; conservative elsewhere. Two
readings warrant stating, because they set several cells: R12 is marked `A` only
where the Publisher declares an allowed-layout set using the enumerated visual
placements (not merely where an enumerated ad type is used), and R15 only where
the UC selects among the three admissible carrier formats (video / image / HTML).

## Matrix 1 — UC × R

Columns are R1..R30 (the `R` prefix is dropped in the header).

| UC | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 | 27 | 28 | 29 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **UC-01** | · | · | · | A | A | · | A | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · |
| **UC-02** | · | · | · | A | A | · | A | · | · | · | · | · | A | · | A | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · |
| **UC-03** | · | · | A | A | A | · | A | · | · | A | · | A | A | · | A | · | · | · | A | · | · | · | · | · | · | A | A | · | · | · |
| **UC-04** | · | A | A | A | A | · | A | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · |
| **UC-05** | · | · | A | A | A | · | A | · | · | · | · | A | · | · | A | A | · | · | · | · | A | · | · | · | A | · | · | · | · | · |
| **UC-06** | · | A | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · |
| **UC-07** | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · |
| **UC-08** | · | · | A | A | A | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · | A | A | · | · | · | · | · | · | · | · |
| **UC-09** | · | A | A | A | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · |
| **UC-10** | · | · | A | A | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · |
| **UC-11** | A | · | · | · | · | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · |
| **UC-12** | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | A |
| **UC-13** | · | A | A | A | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | A | A | · | A | · |

## Matrix 2 — R × UC

Columns are UC-01..UC-13 (the `UC-` prefix is dropped in the header).

| R | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **R1** | · | · | · | · | · | · | A | · | · | · | A | · | · | `(covered)` |
| **R2** | · | · | · | A | · | A | · | · | A | · | · | · | A | `(covered)` |
| **R3** | · | · | A | A | A | · | · | A | A | A | · | · | A | `(covered)` |
| **R4** | A | A | A | A | A | A | · | A | A | A | · | · | A | `(covered)` |
| **R5** | A | A | A | A | A | · | · | A | A | A | · | · | A | `(covered)` |
| **R6** | · | · | · | · | · | · | · | · | · | · | A | · | · | `(covered)` |
| **R7** | A | A | A | A | A | A | · | · | · | · | · | · | · | `(covered)` |
| **R8** | · | · | · | · | · | · | · | · | · | · | · | · | · | `(governance)` |
| **R9** | · | · | · | · | · | · | · | · | · | · | · | · | · | `(governance)` |
| **R10** | · | · | A | · | · | · | · | · | · | · | · | · | · | `(governance)` |
| **R11** | · | · | · | · | · | · | · | · | · | · | · | · | · | `(governance)` |
| **R12** | · | · | A | A | A | · | · | · | A | A | · | · | A | `(covered)` |
| **R13** | · | A | A | · | · | · | · | · | · | · | A | · | · | `(covered)` |
| **R14** | · | · | · | · | · | · | · | · | · | · | · | A | · | `(covered)` |
| **R15** | A | A | A | A | A | · | · | · | A | A | · | · | A | `(covered)` |
| **R16** | · | · | · | · | A | · | · | A | · | · | · | · | · | `(covered)` |
| **R17** | · | · | · | · | · | · | · | A | · | · | · | · | · | `(covered)` |
| **R18** | · | · | · | · | · | · | · | · | · | · | · | · | · | `(governance)` |
| **R19** | · | A | A | · | · | · | · | · | · | · | · | · | · | `(covered)` |
| **R20** | · | · | · | · | · | · | · | · | · | · | · | A | · | `(covered)` |
| **R21** | · | · | · | · | A | · | · | A | · | · | · | · | · | `(covered)` |
| **R22** | · | · | · | · | · | · | · | A | · | · | · | · | · | `(covered)` |
| **R23** | · | · | · | · | · | · | · | · | · | · | · | · | · | `(governance)` |
| **R24** | · | · | · | · | · | · | · | · | · | · | · | · | · | `(orphan)` |
| **R25** | · | · | · | · | A | · | · | · | · | · | · | · | · | `(covered)` |
| **R26** | · | · | A | · | · | · | · | · | A | A | · | · | A | `(covered)` |
| **R27** | · | · | A | A | · | · | · | · | A | A | · | · | A | `(covered)` |
| **R28** | · | · | · | · | · | · | · | · | · | · | A | · | · | `(covered)` |
| **R29** | · | · | · | · | · | · | · | · | · | · | · | · | A | `(covered)` |
| **R30** | · | · | · | · | · | · | · | · | · | · | · | A | · | `(covered)` |

## Notes

### Orphan Rs

**R24 — non-AV creative asset carrier (RFC 4337 avoidance).** The only
non-governance requirement no use case exercises. Every UC that renders an image
or HTML form (UC-03, UC-05, UC-09, UC-10, UC-13) describes that form at the
capability level — which surface the device needs — and never how the asset URL
reaches the Player, which is exactly what R24 constrains. It is not redundant:
R15 fixes *which* carrier formats are admissible, R6 covers tracking beacons,
and R24 fixes *how* a non-AV asset URL is carried. Minimal UC that closes the
gap: a resolution document carrying one image ad and one HTML ad, where the
Player retrieves both assets and the observable is that each asset URL arrives
through a DR-6 carrier and not as an `@mimeType` on a path bound by RFC 4337.
Appending it to UC-10 (already the image/HTML-heavy worked example) is cheaper
than a new UC.

**Governance Rs with no UC — expected, not gaps.** R8, R9, R11, R18, R23 carry
document-level conformance criteria only, so no playback scenario can exercise
them: R11.2's "the Player operates regardless of whether the ADS uses VAST" is
not observable in a session, R18 states a scope boundary, and R23.1 only
requires the spec to name a place for optional metadata. R10 is tagged
`(governance)` on the same criterion — all three of its conformance items are
spec-document ones — even though UC-03 does cite it when it composes the overlay
through HTML/CSS layout primitives.

### UCs with thin coverage

**UC-07 (1 R: R1)** is the only UC below three. The thinness is structural: the
legacy Player never recognises the SGAI construct, so it never reaches the APS
and every selection, presentation and tracking requirement is out of play by
construction. Two Rs could legitimately surface in the text — **R12**, because
the VOD fallback the Publisher authors is the `linear` ad type of the
enumeration, and **R2**, because authoring that fallback is a Publisher
declaration under R2.1.

Two UCs sit at exactly three and are worth tightening. **UC-06 (R2, R4, R7)**:
its ad response says only that each candidate has its own duration, so **R5**
never surfaces even though a multi-ad break's candidates carry presentation
options like any other slot; **R30** would also fit, for a break that resolves
to no ads. **UC-12 (R14, R20, R30)**: it already sequences the chosen window's
forms per R14, so naming **R7** for the candidate order inside the served
resolution document costs one clause.

### Bidirectional sanity check

**No mismatch.** The two matrices were transcribed independently — one
row-oriented (UC → Rs), one column-oriented (R → UCs) — and then diffed cell by
cell; the symmetric difference is empty at 80 `A` cells. The check was verified
against a seeded discrepancy (an extra cell injected into the row view alone),
which it reported, so an empty result is a measurement and not a silent pass.

A second check ran over the same pair: every literal `RNN` reference inside a UC
body must land on an `A` cell. All 49 explicit references do, with one
deliberate exception — **UC-09 × R29**, where UC-09 names R29 only to point at
UC-13 as the other division of labour and states in the same paragraph that the
Player discloses nothing about its device, so R29's obligation is not exercised
there.

One asymmetry worth recording: **R7 is named by no UC at all**, yet six exercise
it (UC-01..UC-06, through "selects the first renderable candidate following
document order" and "plays each candidate in order"). It is covered in substance
and uncited in text, which is the inverse of the UC-09 × R29 case.

[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Inputs: `../context/03-requirements.md` (mtime 2026-05-14 17:07:53)
and `../context/04-use-cases.md` (mtime 2026-05-14 17:56:44).
7 UCs (UC-01..UC-07), 15 Rs (R1..R15; numbering jumps because the
working doc kept R8/R9/R10 as governance mid-range and appended
R11..R15 later). Cells: `A` = UC text references the R explicitly
or its scenario directly exercises the R's obligation; `·` = not
applicable (conservative read — when in doubt, marked `·`).

## Matrix 1 — UC × R

| UC                           | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15 |
|------------------------------|----|----|----|----|----|----|----|----|----|-----|-----|-----|-----|-----|-----|
| UC-01 Pre-roll               | ·  | A  | A  | A  | A  | ·  | ·  | ·  | ·  | ·   | ·   | ·   | ·   | ·   | A   |
| UC-02 Mid-roll               | ·  | A  | A  | A  | A  | ·  | ·  | ·  | ·  | ·   | ·   | ·   | ·   | ·   | A   |
| UC-03 Coexisting overlay     | ·  | A  | A  | A  | A  | ·  | ·  | ·  | ·  | A   | ·   | A   | ·   | A   | A   |
| UC-04 Hybrid linear+overlay  | ·  | A  | A  | A  | A  | ·  | ·  | ·  | ·  | ·   | ·   | A   | ·   | A   | A   |
| UC-05 Pause-triggered ad     | ·  | A  | A  | A  | A  | ·  | ·  | ·  | ·  | ·   | ·   | ·   | ·   | A   | A   |
| UC-06 Multi-ad break         | ·  | A  | A  | A  | ·  | ·  | A  | ·  | ·  | ·   | ·   | ·   | ·   | ·   | ·   |
| UC-07 Legacy Player          | A  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·   | ·   | ·   | ·   | ·   | ·   |

## Matrix 2 — R × UC

| R                              | UC-01 | UC-02 | UC-03 | UC-04 | UC-05 | UC-06 | UC-07 | Tag          |
|--------------------------------|-------|-------|-------|-------|-------|-------|-------|--------------|
| R1  DASH 6th / legacy degrade  | ·     | ·     | ·     | ·     | ·     | ·     | A     | (covered)    |
| R2  Actor responsibilities     | A     | A     | A     | A     | A     | A     | ·     | (covered)    |
| R3  Diverse devices            | A     | A     | A     | A     | A     | A     | ·     | (covered)    |
| R4  Max slot duration cap      | A     | A     | A     | A     | A     | A     | ·     | (covered)    |
| R5  Device-aware selection     | A     | A     | A     | A     | A     | ·     | ·     | (covered)    |
| R6  Tracking carrier           | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (orphan)     |
| R7  Respect ADS order          | ·     | ·     | ·     | ·     | ·     | A     | ·     | (covered)    |
| R8  Justify add/omission       | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R9  Minimise new constructs    | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R10 No layout system           | ·     | ·     | A     | ·     | ·     | ·     | ·     | (governance) |
| R11 No VAST dependency         | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance) |
| R12 IAB owns ad types          | ·     | ·     | A     | A     | ·     | ·     | ·     | (covered)    |
| R13 Non-linear ad tracking     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (orphan)     |
| R14 Single non-linear at a time| ·     | ·     | A     | A     | A     | ·     | ·     | (covered)    |
| R15 Admissible carriers        | A     | A     | A     | A     | A     | ·     | ·     | (covered)    |

R10 is tagged `(governance)` because R10.1/R10.2/R10.3 are all
spec-document level; UC-03 still cites it explicitly to anchor the
"compose via HTML/CSS" decision, but the runtime test surface is on
the spec, not on the Player.
R11 is tagged `(governance)`: R11.1/R11.3 are spec-document, and
R11.2 is a Player capability claim ("must be able to operate
against a non-VAST ADS") that is not naturally exercised by a
playback scenario.
R12 is tagged `(covered)` because the layout names enumerated by
UC-03 (banner, corner, L-shape, side-by-side, sidebar) and UC-04
("banner only — no L-shape") are exactly the IAB-mapped names R12.2
requires the Broadcaster to use, so the UC text exercises R12.2 at
the broadcaster boundary.

## Notes

### Orphan Rs

- **R6 — Ad tracking carrier.** No UC body fires impression, start,
  quartile, or complete beacons in its scenario, nor mentions the
  callback Event scheme (`urn:mpeg:dash:event:callback:2015`). R6
  has runtime obligations (R6.2 carrier shape; R6.5 Player ignoring
  unknown namespaces on tracking extensions; R6.6 non-AV asset URL
  must not be `@mimeType` on a DR-1/DR-5 path) that need at least
  one UC to be testable. **Proposed minimal close**: a tracking
  sub-step in UC-01 and UC-03 covering (a) impression and quartile
  beacons emitted from an `<EventStream>` of the callback scheme,
  (b) vendor-namespaced `ClickThrough` / `AdSystem` metadata
  travelling alongside without affecting playback, and (c) a legacy
  Player silently ignoring an unknown-namespace tracking element
  (cross-link to UC-07). Same extension picks up R13.
- **R13 — Non-linear ad tracking semantics.** Overlay UCs (UC-03,
  UC-04 overlay portion, UC-05) describe form selection and cap
  enforcement but say nothing about quartile beacon firing against
  the Broadcaster-declared `@maxDuration` window, nor about R4
  trim-stopping beacons (R13.3). **Proposed minimal close**: extend
  UC-03 with the R13.1/R13.2/R13.3 behaviour — impression at
  composition, quartiles timed against the slot window (not the
  ad's intrinsic duration), stop firing at the R4 trim boundary —
  then reference into UC-04 (overlay portion) and UC-05. R6 and
  R13 close together via one tracking-augmented UC pair (linear
  in UC-01, non-linear in UC-03).

### UCs with thin coverage

- **UC-07 — Legacy Player (1 R: R1).** By design — UC-07's whole
  purpose is to exercise R1's graceful-degradation contract on
  legacy Players. The UC deliberately bypasses the rest of the
  flow: ADS is not reached (no R5, no R7, no R15), no cap is
  enforced (no R4), no actor contract is exercised post-detection
  (no R2), and the UC's "uniform across D1..D5" outcome is a
  Player-version axis, not the device-heterogeneity axis R3 covers.
  Accept as-is; the conformance chapter should flag UC-07 as
  intentionally narrow-scoped, not under-constrained.

No other UC falls below the 3-R threshold. UC-06 sits at 4 Rs
(R2, R3, R4, R7) and is borderline: its ADS-response section stays
silent on candidate forms (linear-only break) and on device-class
form selection, which is why R5 and R15 do not surface. If the
spec wants UC-06 to also constrain candidate carriers (e.g. ADS
returning a non-admissible `application/javascript` creative
inside a multi-ad break), explicitly surfacing R15 in UC-06 would
tighten the case.

### Bidirectional sanity check

Per-R UC sets agree between Matrix 1 and Matrix 2:

- R1: M1 col = {UC-07}; M2 row = {UC-07}. Match (1).
- R2: M1 col = {UC-01..UC-06}; M2 row identical. Match (6).
- R3: M1 col = {UC-01..UC-06}; M2 row identical. Match (6).
- R4: M1 col = {UC-01..UC-06}; M2 row identical. Match (6).
- R5: M1 col = {UC-01..UC-05}; M2 row identical. Match (5).
- R6: M1 col empty; M2 row empty (orphan). Match (0).
- R7: M1 col = {UC-06}; M2 row = {UC-06}. Match (1).
- R8: M1 col empty; M2 row empty (governance). Match (0).
- R9: M1 col empty; M2 row empty (governance). Match (0).
- R10: M1 col = {UC-03}; M2 row = {UC-03} (governance). Match (1).
- R11: M1 col empty; M2 row empty (governance). Match (0).
- R12: M1 col = {UC-03, UC-04}; M2 row identical. Match (2).
- R13: M1 col empty; M2 row empty (orphan). Match (0).
- R14: M1 col = {UC-03, UC-04, UC-05}; M2 row identical. Match (3).
- R15: M1 col = {UC-01..UC-05}; M2 row identical. Match (5).

No inconsistencies. Notes on near-misses left on the `·` side under
the conservative rule:

- UC-01/UC-02 ADS-response prose says "one or more candidates" and
  describes Player picking "the highest-ranked renderable"
  candidate via ADS hints. This is candidate *selection* (R5),
  not order-of-playback (R7). R7's runtime obligations bite only
  when the resolution document is a sequence the Player plays in
  order, which is UC-06's scenario. Kept conservative.
- UC-03/UC-04/UC-05 prose enumerates layout names without ever
  citing R10 by number for UC-04/UC-05. Only UC-03 cites "(per
  R10)" explicitly, so R10 = A only for UC-03 in Matrix 1; the
  implicit HTML/CSS dependency in UC-04/UC-05 is left on the
  `·` side. A future revision that adds "(per R10)" parentheticals
  to UC-04 and UC-05 would flip those cells without changing
  Matrix 2's governance tag.

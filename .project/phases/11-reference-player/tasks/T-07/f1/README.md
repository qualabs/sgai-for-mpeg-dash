# T-07 family 1 — layouts

**Conclusion:** every non-beacon field of the family's 11 test files passes
except `geometry` of R12.5-1 and R26.1. That failure is the comparator's
handling of `background` (harness, being decided). Every `beacons` FAIL
belongs to T-08. No change to `reference-player/src/` was needed. In the
mutation campaign 13 of 15 breaks failed; the 2 that stayed green are
listed below.

## How it ran

- The runner came from a HEAD snapshot (`bin/`, `spec-source/`,
  `reference-player/` via `git archive HEAD`) under
  `~/.cache/cto-tmp/t07f1-*/`. It used the live `reference-player/src/`,
  synced with rsync before each run.
- Command: `python3 bin/check-dash-conformance.py --behaviour --only
  R12.5,R19.1,R19.3,R22.1,R26.1,R26.3,R27.1,R27.3 --concurrency 1 --clock
  presentation`.
- **All results are on the presentation clock.**
- Load average was 2.0–2.2.
- While the runs went on, the live `reference-player/src/sgai-reference.js`
  carried another worker's uncommitted edit. The runs include it.

## Results (baseline)

`104 PASS, 10 FAIL`, wall 289.5 s.

| Test | requests | selection | presentation | geometry | beacons |
|---|---|---|---|---|---|
| R12.5-1 D1 | PASS | PASS | PASS | **FAIL** (harness) | PASS (none expected) |
| R12.5-2, R12.5-3, R12.5-4 (all classes) | PASS | PASS | PASS | PASS | PASS |
| R19.1 D1, D2 | PASS | PASS | PASS | — | **FAIL** (T-08) |
| R19.3 D1, D4 | PASS | PASS | PASS | — | **FAIL** (T-08) |
| R22.1 D1, D4 | PASS | PASS | PASS | — | **FAIL** (T-08) |
| R26.1 D1, D3, D4 | PASS | PASS | PASS | **FAIL** (harness) | PASS |
| R26.3, R27.1, R27.3 (all classes) | PASS | PASS | PASS | PASS where present | PASS |

### FAIL classes

- **Harness: `background` in the ad box.** Affects R12.5-1 `geometry[4]`
  and R26.1 `geometry[1]` (D1, D3, D4).
  - Expected ad box: `{0,0,100,100}`.
  - Observed: primary `{0,25,50,50}`, ad `{50,25,50,50}`.
  - This is exactly the comparator's exclusion of `background` that is
    being decided now. The same tests' `presentation` passes with a
    separate `background` element.
- **Reference, owned by T-08: no beacons.** Affects R19.1, R19.3 and R22.1.
  - Every beacon is `observed at never`.
  - `reference-player/src/` has no beacon code: grepping for
    `beacon|tracking` finds only comments.

### Standard list (for v13)

1. **The R12.5 "60%" / "25%" ambiguity.**
   - The context/03 table (lines 842–845) says "the upper-left 60% of the
     frame" and "the centre-left 25% of the frame" without saying whether
     the share is of area or of side.
   - The tests and the reference read it as area. The two readings give
     different geometry:

     | Reading | L-shape box | Double box |
     |---|---|---|
     | Area | 77.46% of each side (77.46² = 60.0% of the area) | 50×50 |
     | Side | 60×60 (36% of the area) | 25×25 |

2. `squeezeback-frame` has no carrier in the spec. It was skipped, as the
   dispatch said.

### Independent check

- The expected values were worked out by hand from the context/03 text,
  read as area:
  - `sqrt(0.60)·100 = 77.4597`, and `100 − 77.4597 = 22.5403`. Both match
    the tests' 77.46 / 22.54 within the ±1 pp tolerance.
  - A box of 25% area with the aspect ratio kept is 50×50. Side by side and
    vertically centred, it sits at y = 25.
- The double-box boxes measured at R12.5-1 `t=20000` were primary
  `{0,25,50,50}` and ad `{50,25,50,50}`. They match the hand computation
  exactly.

## Mutation campaign

Each break was one edit, run only on the tests that cover its rule
(`mutation-campaign.out`). A break counts as **killed** when a FAIL
appears that the baseline does not have. The comparator stops at the first
failing geometry instant, so `geometry[4]`'s baseline FAIL hides nothing
earlier.

| # | Break | Tests | Result |
|---|---|---|---|
| M1 | L-shape upper-left region 50×50 | R12.5 | killed (R12.5-1 `geometry[1]`) |
| M2 | upper-right region placed upper-left | R27.1 | killed (`geometry[0]`, D1 and D3) |
| M3 | double-box ad box at y=0 | R12.5, R26.1 | killed (R12.5-1 `geometry[3]`, R26.1 `geometry[0]`) |
| M4 | black band never appended | R26.1 | **survived**: the test cannot see colour (its header says the schema places rectangles, not colours) |
| M5 | background never made visible | R26.1 | killed (`presentation[2]` with no `background`) |
| M6 | overlay shrinks the content to 90% | R12.5 | killed (R12.5-1 `geometry[0]`) |
| M7 | `pause-fullscreen` not covering | R12.5 | killed (R12.5-2 `presentation`, `geometry`) |
| M8 | `pause-partial` hides the paused frame | R12.5 | killed (R12.5-3 `presentation`, `geometry`: primary None) |
| M9 | takeover hides nothing | R12.5 | killed (R12.5-2, R12.5-4 D1/D5 `presentation`) |
| M10 | the compositor leaves non-top forms visible | R22.1 | **survived** (only T-08's beacon FAILs) |
| M11 | video ad forced to rate 1 | R19.1 | killed (`presentation[4]`, D1 and D2) |
| M12 | slot timeline divided by the rate | R19.3 | killed (`presentation[2]`, D1 and D4) |
| M13 | background without an image surface allowed | R26.3 | killed (D2 `selection`, `presentation`) |
| M14 | HTML surface not required | R27.3 | killed (D4 and D5 `selection`, `presentation`) |
| M15 | previous candidate's surface not removed on advance | R22.1 | killed (D1 and D4 `selection`, `presentation`: A back on screen 10–12 s) |

### Why the two survivors stayed green

- **M4 is an instrument gap.**
  - The scenario schema cannot express the colour of the bands.
  - R26.1 "with no background those bands MUST render as black" therefore
    has no check by code.
- **M10 is not reached by R22.1's vector.**
  - The family removes A's surface before B starts (M15 shows that rule is
    covered).
  - So the compositor never holds two live forms in this test.
  - Its "only the top form is visible" path matters when a pause ad sits
    over an overlay. That is the pause family's tests (R16, R17), which
    were not run here.

## Files changed

- No source files changed.
- New evidence files: this README and `mutation-campaign.out`.

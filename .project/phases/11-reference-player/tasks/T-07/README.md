# T-07 — Non-linear presentation in the reference

## Conclusion

The reference now draws every non-linear layout token that has a carrier, and
it handles how the families coexist. The drawing is a file of its own,
`reference-player/src/sgai-compositor.js`, which replaces T-06's placeholder
rectangles:

- an overlay sits over an untransformed primary;
- an L-shape puts the creative over the whole frame, with the primary shrunk
  on top of it into 77.46% × 77.46% at the named corner;
- a double box puts the primary at 0,25,50,50 and the ad at 50,25,50,50, with
  black bands, or the background image in the bands;
- a `linear` takeover and `pause-fullscreen` show the ad alone, and every
  covered surface is taken off screen;
- `pause-partial` shows the ad over the paused frame, which is not moved.

`sgai-nonlinear.js` decides when each form is on screen:

- the slot timeline runs on media time, so a form at rate r is on screen
  d/r s;
- a pause ad suspends the overlay and restores it on resume;
- a pause over a linear ad suspends the linear ad and resumes it where it was;
- dismissal ends the whole slot, and a dismissed takeover returns to where the
  primary stood;
- the default relation suspends a form during a linear ad and resumes it in
  the same execution, or ends it when the programme comes back outside the
  window;
- an `on-top` form accrues on the linear ad's timeline and ends with it;
- an alternative MPD's own windows are presented over it, on its timeline.

**No remaining FAIL is a reference bug that was found.** Each one is one of:

- the environment (the page plays at 0.17–0.9× real time, and the harness
  makes the viewer's actions on the wall clock);
- one of four test, comparator or harness defects;
- T-08's beacons.

Each decision the module took was checked against the value worked out by
hand from the criteria (below). Two things were checked outside the harness
because the harness cannot measure them: the one-frame removal on resume
(R16.1) and the live pause (R25.1). Both were checked with instruments that
were also seen failing on a deliberate break.

## What was built

| File | Change |
|---|---|
| `reference-player/src/sgai-compositor.js` (new) | the presentation layer. Interface: `ref.compositor.present(el, layout, {kind, rect, background, content})` returns a handle with `suspend()`, `resume()` and `remove()`. `refresh()` recomputes the screen from what is presented: the form on top (a pause ad before an overlay), the content's geometry, the cover, and the viewport's `data-sgai-layout`. It changes only the content `<video>`'s left/top/width/height/z-index (restored exactly), and uses `display:none` for covered surfaces, which no family uses, so it cannot undo a family's own `visibility` |
| `reference-player/src/sgai-nonlinear.js` | placeholder rectangles removed; timelines (the main presentation plus one per alternative presentation, R40.6/PLY-51); a slot timeline accrued per tick (media delta of the declaring presentation; plus the linear ad's delta for `on-top`; the takeover's own playback for `linear`); default relation as suspend/resume (context/03 R40.9 and R40.4, not spec PLY-49); `on-top` over a linear ad, ending with it (R40.5); the takeover holding and releasing the primary (§5.3.6); viewer actions `pause` (with the pause over a linear ad, PLY-55), `resume`, `dismiss` (PLY-74/75, `@dismissAfter` absent = not dismissible) and `seek` (only the viewer's seek starts a new entry of the spans: the seek back to RT after a replacement does not); video ads played, paused and rate-matched with their content (R19.1); a `@background` preloaded and a failed first request makes the option unsatisfiable |
| `reference-player/src/sgai-linear.js` | `onScreen`, `position` and `video` getters; its three layout writes go through the compositor (`layoutChanged`); each alternative's player is offered to the non-linear family before initialisation (`attachAlternative`) |
| `reference-player/src/sgai-reference.js` | `FAMILY_FILES` starts with `sgai-compositor.js`, and the scripts load with `async=false` (deterministic order); `ref.compositor` is constructed before the families; viewer actions go to the families in reverse order, so the non-linear family takes a pause before the linear ad under it (R17.5) |

Not done:

- `squeezeback-frame` has no carrier (T-04 C finding 3);
- a pause **video** option is still unverified (no test);
- a viewer pause during a `linear` takeover is not handled (no test).

## Results

Runs on the live repo, concurrency 1, during another worker's UC battery at
concurrency 6 (load average ≈ 4 on 2 cores). The `ids` are the 21 criteria
of T-04 part C: 28 test files, 57 jobs.

| Run | Fields PASS / FAIL | non-beacon fields PASS |
|---|---|---|
| before (T-06's code), session clock — `baseline-before.out` | 118 / 120 | 92 / 181 |
| before, media clock — `baseline-before-media-clock.out` | 134 / 104 | — |
| **after, session clock** — `after-session.out` | 131 / 107 | 105 / 181 |
| **after, media clock** — `after-media-clock.out` | 142 / 96 | 116 / 181 |
| after, vectors extended 6 s (22 files), media clock — `after-extended-media-clock.out` | 129 / 67 | 109 / 149 |

Every `beacons` FAIL (31 after) is **T-08's**: the family fires no beacon.
Each remaining non-beacon FAIL, by class:

| Class | Tests (fields) | Evidence |
|---|---|---|
| **Env: the page is slower than real time.** On the session clock, boundaries come late. On the media clock, the observation ends before the last expected boundary, even when extended by 6 s at 0.25–0.6× | presentation of R12.5-1, R19.1, R19.3 (session only), R22.1, R26.1, R26.3, R27.1, R27.3, R40.9-2; R12.5-1 selection (candidate 5 never reached); R19.1 selection and requests (the break at programme 20 s never reached in 16 s) | `decisions-after.out`: every show/end at the hand-worked slot time (e.g. R12.5-1 extended: c2 at slotT 4.016, c3 8.011, c4 12.021, the primary at 0.5×). Under a 1.5 s tolerance and +6 s the same tests pass (`mutation-campaign.out` baselines) |
| **Env: the viewer's action is made on the wall clock** | R12.5-2, R12.5-3, R16.1, R17.1, R17.2, R31.2, R35.4-2, R37.2 presentation (`primary from` 3000 expected, the pause found 1.2–2.4 s); R35.4-1 and R35.5 (the dismissal at session 4 s came before the slot started at 4.08 s or 5.19 s: `"nothing on screen takes 'dismiss'"`); R40.9-1 (the pause at session 13 s found the programme before the window's 10 s); R17.5 after-run (the pause at 6 s found programme 2.74 s, before the linear ad at 3 s) | `decisions-after.out`. In every pause test the module paused at the action, showed the pause ad within 1–5 ms, and resumed from the paused position. R17.5 took the path when the pause fell inside the linear ad (`dev`: `pause {"php": 3.037, "overLinear": true}`, linear resumed after) |
| **Env: an ad on its own clock plays slower than real time** (T-05's class) | R12.5-4, R35.5 D5, R40.4-1, R40.4-2, R40.5-1, R40.5-2, R40.9-3 presentation (and R40.9-3 requests at exactly 6000) | a 4 s takeover took 4.29–5.3 s; a 6 s linear ad 6.6–9 s (`decisions-after.out`, `linear:execute` → `terminate`) |
| **Harness: a dynamic MPD cannot be joined at `play_from`** (T-05's finding) | R25.1 requests, selection, presentation | `primary from … observed 5083426353`. On a copy whose `availabilityStartTime` is now − 80 s (`live_now.py`, `r25.1-live-now.out`): paused at 62.967 s, frame frozen for the 10 s pause, resumed from 63.009 s with the live edge at ≈ 103 s. The negative control (resume seeks to the live edge) resumes at 103.332 |
| **Harness: R16.1's 17 ms is not measured by frames** | R16.1 presentation | the runner issued the resume 53 ms late (`startedAt 6053`), and the adapter samples every 25 ms. Measured with the resume issued inside a requestAnimationFrame callback (`r16.1-raf.out`): the pause ad is absent at the next frame (16.6–16.7 ms) in R16.1, R12.5-2, R12.5-3, R37.2, R17.1 (where the overlay is back in the same frame). The break that defers the removal 50 ms leaves it on screen at the next frame |
| **Comparator vs test: the background in the ad box** | R12.5-1 geometry[4], R26.1 geometry[1] (D1, D3, D4) | the tests expect the ad box to include the background (0,0,100,100); `compare_geometry` excludes `background` by its docstring, so it measures the ad 50,25,50,50, which is what R26.1 composes. The same tests' presentation requires a separate `background` element, so no module can pass both as the comparator stands |
| **Comparator: selection is keyed by the viewport's layout** | R40.5-1, R40.5-2 selection | the linear ad under an `on-top` overlay is recorded as (`ad-1`, `overlay-lower-third`) besides (`ad-1`, `linear`), and the test expects the second only. The same tests' presentation expects `overlay-lower-third` while both are on screen |
| **Test: an alternative presentation that is not a List MPD candidate has no element** | R40.6 selection and presentation | the alternative's `<video>` is an `ad` surface of opportunity (main.mpd, 1), which the vector does not list (its own header says so). On the module's clocks: the window of alt.mpd shown from the alternative's 2.004 s to 5.981 s (`decisions-after.out`) |

## Seen failing first (D-11, ADR 0085)

`baseline-before.out` is the 57 jobs on T-06's committed code. Per job,
`d11-seen-failing.txt` shows that 55 of 57 have a non-beacon field that FAILs
without T-07. The two that do not are R26.3 D5 and R27.3 D5, whose outcome is
"declined, nothing happens" (T-06's selection). On the media clock, 16 fields
go from FAIL to PASS between before and after. 8 go from PASS to FAIL:
R22.1 D4, R26.3 D2, R27.1 D1/D3 and R27.3 D2–D4 presentation, plus R17.5
beacons. Each of these 8 was checked: the observation ended before 6 s of
the programme, at 0.57× against 0.88× in the before run. The module's
decisions are the same (e.g. R27.1 D1 shows at php 2.007 and ends at 5.98 in
both).

## Mutation campaign

`mutate.py`: one break per rule. Each break is run on a copy of the project,
on the covering tests only, and judged on both clocks against the unmutated
module run in the same campaign. Because every pause test fails its
presentation on this machine whatever the module does, the campaign runs
copies widened to a 1.5 s tolerance and extended by 6 s (`widen.py`): a break
whose effect is larger than 1.5 s can be seen, and a smaller one cannot.
Results: `mutation-campaign.out` (summary below).

MUTATION-SUMMARY

## Checked by hand

Each value is worked out from the criterion, then compared with the module's
log (`decisions-after.out`, extended run):

- **Geometry (R12.5, R27.1):** sqrt(0.60) × 100 = 77.4597%, which is
  743.6 × 418.3 px of the 960 × 540 viewport. The upper-right box's x is
  100 − 77.46 = 22.54% (216.4 px). The double box's boxes are 50% × 50% =
  480 × 270 px at y = 25% (135 px). Measured by the adapter: L-shape primary
  22.54,0,77.46,77.46 with the ad at 0,0,100,100 (R27.1 geometry PASS, both
  clocks); double box primary 0,25,50,50 and ad 50,25,50,50 (R26.1
  geometry[0] PASS).
- **R19.3 (PLY-69, cap on declared durations):** cap 8000 at timescale
  1000; A is 8 s = 8000 units = the cap, so B gets 0 and is not planned.
  Module: `plan ["c1/o1 … slot 0+8"]`. A is shown from programme 4.011 to
  12.039 at rate 2, which is 8 s of media; on a real-time page that is 4 s
  of wall (here 5.2 s at 0.63×).
- **R40.5-1 (cap on the linear ad's timeline):** the programme stands at 4 s
  during the insertion, so only the linear ad advances the slot. The cap of
  6 s is reached when the linear ad is 6 s in. Module: end at
  `slotT 6.002` with the programme at 4.004.
- **R40.5-2:** slot = 2 s over the programme (2 → 4) + 6 s over the linear
  ad = 8 s of the 15 s image when the linear ad ends. Module: end "the
  alternative presentation it was composited over ended", `slotT 7.986`,
  programme 4.077.
- **R40.4-1 (resume in the same execution):** A is suspended at slotT 3.989
  and resumed at 4.05. It ends at slot 8 (programme 10), then B from 10 to
  18. Module: c2 shown at `php 10.016, slotT 8.008`; end at `php 18.048,
  slotT 16.041`. One resolution request.
- **R40.4-2 (Table 57):** PRT 4, PRTA 4.002, APDmax 6, clip → APDadj =
  6 − 4.002 + 4 = 5.998, APDA = 5.998, RT = PRT + APDA = 9.998 ≥ the
  window's end 8. Module: `linear:terminate RT 9.998`, then `nonlinear:end
  "the span ended", php 9.998`.
- **R40.6:** the window of alt.mpd spans its 2–6 s. Module: shown at alt
  2.004, ended at alt 5.981; alt.mpd's request is the opportunity.
- **R25.1:** frozen 62.967 → resumed 63.009 (the 42 ms is the primary
  playing after the resume; the live edge was ≈ 103 s).
- **R31.2:** 6 s pause ad under a 2 s cap: shown 2.005 → exhausted at
  8.012 (wall clock, onExhausted stop).

## Screenshots

`screenshots/`, real size 960 × 540: the viewport of the harness, clipped. Shot
in a dev copy of the runner (`dev-runner.patch`, never in `bin/`). The patch
serves each image creative as a coloured SVG labelled with its file name and
each HTML creative as a coloured page, instead of the harness's 1 × 1 PNG,
so the composition can be seen:

- `overlay`, `overlay-lower-third`, `overlay-corner`, `custom`;
- `squeezeback-l-shape-upper-left`, `squeezeback-l-shape-upper-right` (also
  with an HTML creative, R27.1);
- `squeezeback-double-box` (black bands), `squeezeback-double-box-background`;
- `linear-takeover` (the takeover's own timecode 00:00:00.200, where the
  programme was at 2 s);
- `pause-fullscreen`, `pause-partial`;
- `on-top-over-linear` (R40.5-1), `pause-fullscreen-over-linear` (R17.5).

## Instruments

- `decisions.py RAW [job]` prints the module's decisions on its own clocks.
- `../T-06/media_clock.py` re-times a record on the primary's media clock.
- `widen.py` (tolerance + extension) and `../T-06/extend.py` (extension
  only).
- `live_now.py` runs R25.1 on a joinable live channel.
- `dev-runner.patch` is the dev copy of `bin/players/behaviour.mjs`. Its
  screenshots and SVG creatives run with `SGAI_SHOTS_DIR`/`SGAI_SHOTS_AT`;
  with `SGAI_RAF_RESUME` it issues each resume inside a rAF callback and
  records the ad surfaces shown at the next frame. Each instrument was seen
  failing on a deliberate break (`r16.1-raf.out`, `r25.1-live-now.out`).

## Findings (out of scope, not fixed)

1. **Comparator vs tests on the background:** `compare_geometry` leaves
   `background` out of the ad box, while R12.5-1 geometry[4] and R26.1
   geometry[1] expect it in. One of the two has to change.
2. **Selection keyed by the viewport's layout:** a linear ad under an
   `on-top` overlay counts as a second presentation (R40.5-1, R40.5-2).
3. **R40.6's vector cannot describe the alternative it is about** (its header
   says so). The alternative's `ad` surface makes the selection fail.
4. **R16.1's one-frame bound needs a frame-based action in the harness.**
   Today the action can be up to ~50 ms late and the sampling is 25 ms.
5. **R25.1 needs a live fixture joinable at `play_from`** (T-05's finding;
   `live_now.py` shows the shape of a fix).
6. **The default relation follows context/03 (R40.9, R40.4), not spec
   PLY-49** (T-04 C finding 2). A Player built to the spec fails R40.4-1;
   T-06's PLY-49 cut is replaced here.
7. **R19.1 for a video overlay is decided by the slot clock only.** The ad
   video's own rate is not observed (see M26).
8. **Load:** these runs shared the 2 cores with another worker's UC battery
   at concurrency 6 (`/home/nicolas/.cache/cto-tmp/t04close-skel-30579`).

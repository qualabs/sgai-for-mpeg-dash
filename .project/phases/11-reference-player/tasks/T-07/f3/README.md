# T-07 family 3 — non-linear windows vs linear events

Criteria: R40.4 (-1, -2), R40.5 (-1, -2), R40.6, R40.9 (-1, -2, -3).
8 vectors × D1, D4 = 16 jobs, 64 fields.

## Conclusion

- **38 PASS, 26 FAIL. No FAIL is the reference's**, so no source file
  changed.
- 14 FAILs are `beacons` (T-08's). 6 are `selection` from known comparator
  classes (1) and (2). 4 are R40.6 (known class 4: the vector cannot describe
  the alternative presentation). 2 are R40.9-3 D4: the ad's first frame comes
  after the vector's window (the test, see below).
- The presentation timing of every rule passes: resume from the suspended
  point (R40.4-1), ended outside the range (R40.4-2), the on-top form over the
  linear ad, its cap on the ad's timeline and its end with it (R40.5), the
  alternative's own window on its timeline (R40.6, timings correct, only the
  labels differ), anchoring and supersede (R40.9).
- Mutation campaign: **9 of 10 breaks killed**. M9 (supersede no longer
  suppresses the inherited event) survived. That is a gap in the test and
  harness, not in the reference.

## How it ran

- The runner came from a HEAD snapshot (`git archive HEAD bin spec-source
  reference-player`) under `~/.cache/cto-tmp/t07f3-*/`, with the live
  `bin/players/node_modules` linked in. The live `reference-player/src/` was
  rsynced in before each run. It included the harness agent's uncommitted
  edit to `sgai-reference.js`, which was left alone.
- Baseline: `python3 bin/check-dash-conformance.py --behaviour --clock
  presentation --only R40.4,R40.5,R40.6,R40.9 --concurrency 1`. Load average
  was 2.8. Wall time was 298 s. The full log is `baseline.log`.
- Mutations: `mutate.py <snapshot>` (in this folder). Its output is
  `mutation-campaign.out`.

## Results (baseline)

| Job | requests | selection | presentation | beacons |
|---|---|---|---|---|
| R40.4-1 D1, D4 | PASS | FAIL (comparator, 1) | PASS | FAIL (T-08) |
| R40.4-2 D1, D4 | PASS | PASS | PASS | FAIL (T-08) |
| R40.5-1 D1, D4 | PASS | FAIL (comparator, 2) | PASS | FAIL (T-08) |
| R40.5-2 D1, D4 | PASS | FAIL (comparator, 2) | PASS | FAIL (T-08) |
| R40.6 D1, D4 | PASS | FAIL (vector, 4) | FAIL (vector, 4) | FAIL (T-08) |
| R40.9-1 D1, D4 | PASS | PASS | PASS | FAIL (T-08) |
| R40.9-2 D1, D4 | PASS | PASS | PASS | FAIL (T-08) |
| R40.9-3 D1 | PASS | PASS | PASS | PASS |
| R40.9-3 D4 | PASS | PASS | **FAIL (test)** | **FAIL (test)** |

### Each FAIL, by class

| FAIL | Class | Evidence |
|---|---|---|
| R40.4-1 selection | **comparator, known (1)** | observed "overlay.xml:#1, overlay.xml:#1" and "1 presentation(s) more: overlay.xml:#2". A's suspension and restore count as two presentations, which pushes B out by one place. The presentation field, which checks A resumed from its 4th second and B after it, PASSes. |
| R40.5-1, R40.5-2 selection | **comparator, known (2)** | "expected linear list.mpd:ad-1; observed overlay-lower-third [ad list.mpd:ad-1]" and, for -1, "1 presentation(s) more: linear [ad list.mpd:ad-1]". The linear ad under the on-top form is labelled with the form's layout, and it is counted again when the form leaves. The presentation PASSes. |
| R40.6 selection, presentation | **vector, known (4)** | "ad presented for an opportunity the vector does not list: (main.mpd, 1) (linear [ad alt.mpd:main] …)". Observed D1: 1996..3993 alt.mpd; 3993..7976 alt.mpd + overlay.xml#1; 7976..12017 alt.mpd; 12017.. primary from 2070. These are the vector's 2/4/8/12 s, with only the label of the alternative differing. |
| R40.9-3 D4 presentation, beacons | **test (vector)** | "observed a change at 6598 from none [primary (paused)] to linear [ad list.mpd:ad-1]". The vector expects 6000 ± 250. See below. |
| 14 × beacons | **T-08, known (3)** | "observed at never" for every non-linear beacon. The linear family's beacons PASS. |

**R40.9-3: why it is the test.** `@earliestResolutionTimeOffset` is 0, so the
List MPD may be fetched only at 6 s. The vector's own `requests` let the ad's
MPD arrive as late as 6250. The ad's first frame cannot come before that MPD,
its init segment and its first media segment. Yet the vector puts that frame
at 6000 ± 250. The reference does nothing between these steps. In the module
log of a D4 rerun: `linear:resolve` at t 8951, `nonlinear:alternative`
(ad.mpd in) at 9058, `linear:execute` at 9139, `linear:started` at 10041
(`gapMs: 903`). That 900 ms is a fresh dash.js player starting. On the session
clock the held primary counts at wall time (scenarios/README.md). Three
reruns of D1+D4 gave late starts of 281, 564, 1013 and 576 ms in turn. Some
reruns passed: D1 passed in the baseline, D1 in rerun 2, and D4 in rerun 3.
So this is not a D4 class effect. The fix belongs to the vector: a
`{from, to}` window, or a per-item `tolerance` on the 6 s boundary that
covers the resolution plus the start-up.

### Standard list (for v13)

- **Known (as dispatched):** context/03 R40.4 and R40.9 resume a suspended
  form after a linear break, while spec §4.5.8 PLY-49 ends it. R40.4-1
  follows context/03 and PASSes, so a Player built to the spec would fail it.
- **New, minor:** neither context/03 nor the vector format says how long a
  Player may hold the content when an event can be resolved only at its own
  PRT (`@earliestResolutionTimeOffset` 0). R40.9-3 needs that to be
  decidable. The vector can absorb it with a tolerance, but a sentence in the
  spec, or in scenarios/README.md, on "resolution at PRT, first frame within
  the start-up" would keep each vector author from reinventing it.

## Mutation campaign

Each break was one edit, made only in the snapshot's copy of
`sgai-nonlinear.js`. Each ran only on its covering tests, on D1 and D4.
A break is **killed** when a FAIL appears that the baseline does not have, or
when a field the baseline already fails shows a different observation.

| # | Rule | Break | Tests | Result |
|---|---|---|---|---|
| M1 | R40.4 resume where suspended | the slot time is reset to 0 at the resume | R40.4-1 | killed: `presentation` A stays from 12032 with no switch to B at 16000 |
| M2 | R40.4 resuming outside the range ends | the span-end check skips suspended forms | R40.4-2 | killed: R comes back at 10 s (`selection` "1 presentation more", D1 `presentation` blank 10138–10746) |
| M3 | R40.5 on-top is composited, not suspended | on-top is also suspended during the break | R40.5-1, -2 | killed: R40.5-1 `selection` "observed nothing" for the overlay; R40.5-2 `presentation` linear alone 4004–10022 |
| M4 | R40.5 cap accrues on the alternative's timeline | the alternative's advance is not added | R40.5-1 | killed: overlay 4000..14020, no change at 10000 |
| M5 | R40.5 form ends with the alternative | the end-with-alternative check is disabled | R40.5-2 | killed: overlay over the primary 10022..11955 |
| M6 | R40.6 alternative's windows on its own timeline | the alternative's windows read the programme's time | R40.6 | killed: overlay 2082..6047 (baseline 3993..7976), so the field fails differently |
| M7 | R40.9 not shown outside the range | the span-end check is removed | R40.9-1 | killed: overlay from 2016 with no change at 6000 |
| M8 | R40.9 pause anchored inside its range | a pause before PT opens the slot | R40.9-1 | killed: pause request at 8017 (expected 11000..13000), pause ad 8035..9068 |
| M9 | R40.9 supersede suppresses the inherited event | the suppressor always returns false | R40.9-2 | **survived** (6 PASS, only `beacons` fail as in the baseline) |
| M10 | R40.9 supersede with no ad releases the events | the release is removed | R40.9-3 | killed: `requests` break and ad.mpd "not observed", no linear ad |

**Why M9 stayed green.** It is a test and harness gap. The rerun's module log
shows the mutant does resolve the insertion at 6 s: `linear:resolve` at php
6.0105. The fetch fails (`linear:failed` "not an MPD") because R40.9-2 lists
no fixture for `/beh/r40-9/break`. The harness then answers that URL 204 and
records it as `kind: other`, and the comparator's `requests` check ignores
`other`. So the vector's own sentence, "its List MPD is never requested",
is not checked, and an insertion that should have been suppressed fails
silently instead of playing. Either of these would make M9 visible: list
`list.mpd`/`ad.mpd` among R40.9-2's fixtures, so the mutant's insertion plays
and `presentation` fails; or have the harness count an unlisted request to a
document host as a document request.

## Independent check (R40.5-1, by hand from the fixtures)

- `main-cap.mpd`: an insertion at `presentationTime="4000"`. The overlay
  window has `presentationTime="4000" duration="10000"`, `durationCap="6000"`
  and `linearRelation="on-top"`. `list.mpd`: Period `ad-1`,
  `duration="PT10S"`. `overlay.xml`: one candidate, `duration="PT15S"`.
- context/03 R40.5: "While composited, the window's cap accrues on that
  presentation's timeline (R4.11), and a form on screen MUST end when that
  presentation ends."
- On the ad's timeline the 6 s cap is spent at 4 + 6 = **10 s**. If the cap
  accrued on the programme's timeline, which stands still during the
  insertion, it would never be reached. The form would then end with the ad
  at 4 + 10 = **14 s**.
- The baseline PASSes the change at 10000 ± 250. Under M4 (programme timeline
  only), the overlay was observed 4000..14020: the 14 s the hand computation
  predicts for the wrong reading.

## Files changed

- Source: none.
- Evidence (this folder): `README.md`, `baseline.log` (14 KB),
  `mutate.py`, `mutation-campaign.out` (25 KB).

## Findings (out of scope, not fixed)

1. **R40.9-2 cannot catch a supersede that leaks** (M9). The causes and the
   two possible fixes are under the M9 explanation above. Owner: the vector
   (`spec-source/behaviour/R40.9-2.yaml`) or the harness's request
   classification.
2. **R40.9-3's 6 s boundary is tighter than physically possible** with
   resolution at PRT. The vector needs a tolerance or window there.

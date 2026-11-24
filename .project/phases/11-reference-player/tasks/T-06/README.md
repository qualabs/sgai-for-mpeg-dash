# T-06 — Resolution and selection in the reference

## Conclusion

`reference-player/src/sgai-nonlinear.js` implements the non-linear family's
resolution and selection: the overlay and pause windows read from the MPD,
the resolution request with the slot parameters the window declares, the
validation of candidates and the choice of one option each by layout and
device class, the cap, the fallback chain, empty resolutions, the usable
lifetime, once-per-session, the pause slot with `@onExhausted`, and
`supersede` through T-05's suppressor. It draws a placeholder surface per
layout (a `custom` option at its `@rect`); the drawing is T-07's, the beacons
and the click T-08's.

**Every decision it takes in media time is the one worked by hand from the
criteria, and no remaining FAIL is a reference bug that was found.** On the
33 overlay and request tests, re-timed on the primary's media clock with the
observation extended by 6 s (below), 191 fields PASS and 45 FAIL; 36 of the
FAILs are beacons, and the 9 others are 8 fields of two harness defects
(R1.4, R5.9 requests; R5.6-1 D3/D4) and 1 environment case (R40.3-1, linear). Every beacon FAIL
is T-08's: the family fires no beacon.

| Class | Tests (fields) | Evidence |
|---|---|---|
| **Needs T-08** (no beacon is fired) | every `beacons` FAIL | the family has no tracking; the beacons that PASS expect none |
| **Environment: the page plays slower than real time** | session-clock `presentation`/`requests` FAILs of nearly every test; `primary from` of the pause tests (R32.x, R34.1, R34.3, R36.5) | `decisions-after.out` (primary media/wall 0.58–0.96 per job) next to each decision's media time; on the media clock with the observation extended, the overlay tests pass (`extended-media-clock.out`). The pause tests are not rescued by the media clock: the harness pauses at a wall-clock session time, which on a slow page is an earlier media time (R34.1 D1: pause at session 9 s found the primary at media 3.63 s, expected 5 s) |
| **Environment, linear** (T-05's class) | R40.3-1, R40.3-2 presentation | the linear ad plays on the wall clock; R40.3-2's window fails when its APS answers at wall 8 s, which was media 7.30 s, so the late insertion runs at PRTA 7.30, not 8 (`decisions-after.out`) |
| **Harness: an `aps` entry on a non-document URL is recorded as a document request** | R1.4 requests (`…/ad/v/4.m4s`), R5.9 requests (`…/missing.png`) | `behaviour.mjs` records every `aps` hit with kind `aps`, and `normalise()` puts kind `aps` among the compared requests; neither vector lists them, so they are "unexpected". The module did what the tests want: R1.4 aborted at session 8.9 s (in 3–10 s) and never requested window 2; R5.9 skipped option 1 and showed option 2 |
| **Harness: an image under a sub-MPD's media prefix is fetched from the content server** | R5.6-1 D3, D4 (selection, presentation) | `banner.html` and `banner.png` sit under `https://ads-cdn.example.com/behaviour/R5.6/`, the BaseURL of `cr561v.mpd`, so the runner maps them to the local content server, which answers 404 (`note: … media errors` in the outputs). The module treats that as a failed first request (R5.9) and declines: `option-skipped … answered 404` in `decisions-after.out` |
| **Comparator: two documents at one URL** (T-05 saw it on R30.2) | R32.1-2, R34.3, R34.6, R36.5-1 selection (and presentation by identity) | the second document (`nth: 2`) is served at the same URL; `Fixtures.of()` maps the ad's `data-sgai-doc` to the first fixture with that URL. The module shows the second document's candidate at the right time (R32.1-2: `pause-show` from `second.xml`'s plan at 5.02 s after the request at 5.01 s) |
| **Comparator: repeated or several selections of one opportunity** | R32.1-1 selection (3 identical passes expected, the comparison deduplicates), R34.3 and R36.5-2 selection (a `declined` and a `presented` entry for the same opportunity: both are compared against everything seen for it) | `compare_selection()` keys by opportunity and keeps distinct surfaces only |
| **Environment: a seek's rebuffer longer than the tolerance** | R36.1-3 D1 presentation (after-run only) | 381 ms with nothing on screen after the seek to 50 s; the module put nothing on screen there, D4 with the same module passed, and the baseline passed it |

## Seen failing first (D-11, ADR 0085)

`baseline-before.out`: the 29 criteria on the reference without this family
(T-05's state, run from a snapshot). 279 FAIL, 85 PASS. Per job,
`d11-seen-failing.txt`: every job but five has a non-beacon field that
fails without the family. The five: R4.7-2 D4, R4.10 D1 and D4 (expected
outcome: nothing happens; mutations M14 and M15 show they can fail), and
R4.7-1, R20.3-2 (linear, T-05's).

## What was built

- `reference-player/src/sgai-nonlinear.js` (new). Its header lists the
  readings it takes where the specification leaves room: a resolution
  request is given up after 10 s (PLY-39 fixes no time; R40.3-2 needs more
  than 6 s, R20.1-1 less than 18 s); the overlay slot runs on the primary's
  media time (PLY-31), the pause slot on the wall clock; options and their
  resources are fetched when the document arrives, so a first-request
  failure moves to the next option before the window starts (R5.9); a video
  option that stalls 1 s while the primary plays, or errors, is aborted and
  ends the execution (PLY-86, R1.4); a held document serves any execution
  while usable and an expired one is replaced only when the opportunity
  fires (PLY-9); a pause video option needs two decoders; nothing is
  composited before the primary's first frame (the linear family's gate).
- `reference-player/src/sgai-reference.js`: one line, `FAMILY_FILES` adds
  `sgai-nonlinear.js`. `sgai-linear.js` is unchanged; the family uses its
  `addSuppressor()` and `active`, and reads `gated`.

## Mutation campaign

`mutate.py`: one break per rule on a copy of the project, run only on the
tests that cover it, judged on the session clock and on the media clock
against the unmutated module run in the same campaign. **32 of 32 CAUGHT**
(`mutation-campaign.out`, `mutation-campaign-rerun.out`). Four were not
caught in the first pass, and each was a defect of the break or of its
reference, not of the tests' power:

- M15 and M20 were wrong breaks (M15 made an absent cap a cap of 0, which
  presents nothing too; M20 consumed the window at the pause but also
  disabled the check). Rewritten: absent cap read as unbounded; consumed at
  the pause with the check kept. Both CAUGHT.
- M27 (late join starts at the window's start) and M30 (the span does not
  end the presentation) act after session 15 s of R34.9, which the slow page
  never reached within `observe_until`. Run on the extended copy of R34.9:
  both CAUGHT.

## Instruments, and what they are worth

- `media_clock.py` re-times a `--save-raw` record on the primary's media
  clock (between two samples with the primary on screen, playing and not
  sought, the time that passes is the media time it advanced; elsewhere wall
  time), then `--replay` judges it. The mapping reads only the primary
  `<video>`'s sampled `currentTime`, never the module. It can fail: every one of the
  32 breaks is caught on it, and 7 only on it (M08–M12, M27, M30).
- `extend.py` copies vectors with `observe_until` and the last segment's end
  moved 6 s later, nothing else; run with `--vector`. Needed because a page
  at 0.6–0.9× never reaches the vector's last media times.
- `decisions.py` prints the module's decisions in media time per job
  (`decisions-after.out`, `decisions-extended.out`).

## Checked by hand against the criteria

- R4.9 (PLY-28): cap 11 at timescale 1; candidate 1 PT10.2S → ⌈10.2⌉ = 11 ≤
  11, admitted whole; cumulative 11 = cap, candidate 2 gets nothing. Module:
  `capUnits 11, ts 1, plan c1 slot 0+10.2 -> media 12.204`; end at media
  12.209.
- R4.2-1 (PLY-24): cap 8000; 5000 + 5000 > 8000, so candidate 2 is shown
  8000 − 5000 = 3000 ms. Module: `c2 slot 5+3 -> media 10.005`, end at
  media 10.005.
- R20.5 (PLY-43): window 2 admits lower-third only and caps 4000; option 2
  (8 s) is cut at 4 s. Module: `c1/o2 slot 0+4 -> media 6.001` after window
  1's 404.
- R39.5-1 (§5.3.5): region 50 50 50 50; option 1 x = 45 < 50, outside;
  option 2 60 ≥ 50, 60 ≥ 50, 100 ≤ 100, 100 ≤ 100, inside. Module: option 1
  skipped "rect 45 60 20 20 outside the region", option 2 shown; geometry
  PASS (60, 60, 40, 40).
- R34.9: join at 15 s in window 10–30 s: candidate A 15–25, B 25–30 cut at
  the end. Module: `c1 slot 0+10 -> 25.018, c2 slot 10+10 -> 35.018`, end
  "the span ended" at media 29.982.
- R36.1-1 (PLY-6, Table 63): offset 3000 on PT 10000 → no request before
  7 s. Module: request at media 7.008.

## Findings out of scope (not fixed)

1. **The harness never passes `sends_capabilities` to the module.**
   `behaviour.py`'s job carries `player_capabilities` only. The family sends
   a capability parameter only when the profile has `sendsCapabilities`
   (none today), which suits every T-06 test (`[]`), but UC-05, UC-13,
   UC-15, UC-16 and UC-19 expect some.
2. The three harness/comparator defects in the table (an `aps` hit on a
   media or creative URL compared as a document request; creatives under a
   sub-MPD's BaseURL routed to the content server; selection keyed by URL
   and by opportunity).
3. The session clock: on this machine the vectors' 250 ms cannot be met for
   anything placed after a few seconds; the presentation-driven clock
   already planned is what T-06's media-clock replay emulates.

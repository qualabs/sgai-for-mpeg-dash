# T-09 — the whole behaviour battery

**Conclusion.** The battery ran complete once: 323 jobs (170 criterion-test
jobs, 153 UC-vector jobs: 22 vectors × their classes and variants), 1 361
results, **1 155 PASS, 132 FAIL, 70 NOT_VERIFIABLE** (plus 4
NOT_APPLICABLE). With concurrency 2 it took **16 614 s (4 h 37 min)** against
a serial estimate of **31 988 s (8 h 53 min)**: speed-up **1.93×**. Every
FAIL was re-run alone twice: 130 repeat, 2 (R40.3-2 D1) do not and are
unstable (environment/load). Of the 132: 37 are the reference's, 93 are the
test's (vectors the format or the harness cannot serve, a vector behind the
comparator, the legacy instrument), 2 unstable. Two findings are the
standard's (below); both reach the battery through a vector or the
reference, so in the table they carry those classes.

## Environment

| | |
|---|---|
| Machine | 2 cores (`nproc`), 15 GiB RAM |
| Load (`uptime`) | start 23:34:35 −03: 1.10, 2.09, 2.48 · end 04:11:52: 0.69, 1.42, 1.68 · other Chrome sessions of the user were running throughout |
| Code | HEAD `fff79a8` at start. `3c3a949` landed during the run (docs and `bin/check-scenarios.py`, neither used by `--behaviour`) |
| Players | reference = dash.js 5.3.0 + `reference-player/src/`; legacy = dash.js 5.3.0 alone (`bin/players/node_modules`, pinned) |
| Browser | Chromium 149.0.7827.55 (Playwright 1.61.1 headless shell, build 1228) |
| Clock | `presentation` (session time from what is presented) |

## Commands

```
# the battery (one combined run: criteria + UC vectors, all classes)
python3 bin/check-dash-conformance.py --behaviour --clock presentation \
    --concurrency 2 --log-dir .project/phases/11-reference-player/tasks/T-09/battery/full-log
# each FAILing job alone, twice (a one-job copy of its vector, the copies built
# by script from the vector with only that class / variant kept)
python3 bin/check-dash-conformance.py --behaviour --clock presentation \
    --concurrency 1 --vector <copy>.yaml --log-dir <tmp>
```

**Why concurrency 2.** Two cores, with an ambient load near 2 from the
user's own browser sessions. A third job would oversubscribe the CPU, and on
the presentation clock what overload costs is not lost time but a FAIL the
environment caused. Each job is paced by playback (one presentation second
takes about one second of wall clock), so the speed-up is bounded by the
concurrency itself; 1.93 of a possible 2 says the two slots stayed full.

The repeat used one-job copies instead of `--only <id> --class <c>` because
`--only` runs every variant of a vector for that class: for UC-05 that is
three 800 s jobs where one failed. The copies change nothing in the vector
but drop the other outcomes; `fixture_file` reads fixtures from the source,
so the copy is served the same documents. The first copy (R40.6 D1) gave the
same two FAILs as the battery.

Files here: `summary.txt` (stdout of the battery), `full-log/behaviour.log`
(190 KB, every result), `repeats/repeats.txt` (one line per repeat run) and
`repeats/<test>--<class>--<variant>-r<1|2>.summary.txt`.

## Totals

| | jobs | PASS | FAIL | NOT_VERIFIABLE | NOT_APPLICABLE |
|---|---|---|---|---|---|
| Criterion tests (`behaviour/R*.yaml`, plus `index.yaml`'s untested criteria) | 170 | 698 | 6 | 17 | 4 |
| UC vectors (`scenarios/UC-*.yaml`) | 153 | 457 | 126 | 53 | 0 |
| **Total** | **323** | **1 155** | **132** | **70** | **4** |

Results are per field (requests, selection, presentation, beacons, audio),
so one job yields up to five. The task names "110 UC results"; the battery
plans 153 UC jobs, because the variants count as jobs of their own.

## Time

| | seconds | |
|---|---|---|
| Measured, concurrency 2 (`wall` of the summary) | 16 614.2 | players 16 609.1, content 0.4 (14 cuts from the cache) |
| Serial estimate: Σ `observe_until` over the 323 jobs | 31 988 | criteria 2 238 · UC vectors 29 750 |
| Speed-up | 1.93× | |

The serial estimate is a floor, not a forecast: a job alone took 1.03–1.06×
its `observe_until` in the repeats (e.g. UC-14 93–95 s for 90 s, UC-07
113–114 s for 110 s), so the battery at concurrency 1 would take about
33 500 s (9 h 18 min). UC-05 (13 jobs × 800 s) and UC-11 (6 jobs × 1 005 s)
are 51 % of the serial time.

## FAILs by class

Every FAIL was re-run alone twice (concurrency 1, 27 842 s for the 62 jobs ×
2, 04:15–11:59 −03). Load at the end of the repeats was 15.9 from work
outside this task; no repeat changed its verdict across r1/r2.

| Class | FAILs | Jobs | Alone ×2 | What |
|---|---|---|---|---|
| **reference** | 37 | 18 | FAIL/FAIL | UC-08 (5 jobs), UC-14 D1–D5 (5), UC-21 (8) |
| test — vector: response routing | 55 | 19 | FAIL/FAIL | UC-05, UC-12, UC-13, UC-15: one URL, several fixtures, and the harness answers the first (`behaviour.mjs`: `job.documents.find`), so a per-class, per-variant or second answer never reaches the Player |
| test — instrument: legacy Player | 18 | 6 | FAIL/FAIL | UC-07, UC-11, UC-14, UC-17, UC-22 `legacy`: dash.js 5.3.0 has no `alternativeMPD` scheme (`grep -rhoi 'alternativeMPD' dist index.d.ts`: 0 hits; the only `urn:mpeg:dash:event:` schemes are `2012` and `callback:2015`) |
| test — vector (cause in the standard) | 10 | 10 | FAIL/FAIL | UC-07 D1–D5: the outcomes are a legacy Player's; the reference requests the SGAI windows |
| test — vector | 9 | 7 | FAIL/FAIL | R40.6 D1/D4 (alternative presentation written as nothing on screen), UC-11 D1–D5 (click tracking now counted) |
| test — vector/format | 1 | 1 | FAIL/FAIL | UC-19 D1: a session capability the format cannot hand the Player |
| unstable (environment/load) | 2 | 1 | PASS/PASS | R40.3-2 D1 |
| **Total** | **132** | **62** | | |

Two FAILs carry a second, timing part that did not repeat alone: UC-05 D4
`beacons` (two beacons at 741 690 for 740 000 in the battery; alone, only the
routing's unexpected beacons) and UC-11 D4 `beacons` (imp at 983 462 for
980 000, its overlay on screen from 980 082; alone, only the click beacons).
Their field still FAILs for the reason in the table; the lateness was load.

### The reference's FAILs

- **UC-08 (D1–D5): the pause window is resolved at its start, not at the
  pause.** Request observed at session 0; the vector, after H.3 ("this Player
  resolves at the pause instead, at 5:10"), puts it at the pause (30 000).
  The window declares `earliestResolutionTimeOffset="0"`. D1–D4 then restore
  the overlay at 60 035, when the pause ad ends and playback is still paused;
  the vector restores it on resume (70 000, H.7 "the overlay is restored
  where it was suspended"). The overlay's `mid` beacon (74 977 for 85 000)
  follows from that.
- **UC-14 (D1–D5): a dynamic alternative MPD is not played.** The module log
  of a `--save-raw` run of D1 says, at the crossing of PRT 2700:
  `linear:failed` "alternative MPD of type dynamic is not played by this
  reference". The slate was fetched (32 955 ms), so the request field of D1
  fails only on the slate's own overlay resolution.
- **UC-21 (D1–D5 and `dismiss-then-rewind` D1/D3/D4): no new resolution for
  the second execution.** After the rewind at 45 000 no request to the overlay
  URL is observed in 45 000..55 000; the document declares no validity, and
  R36.4 says such a document "remains usable for the execution it was obtained
  for (R34.6)". Presentation, selection and beacons pass: the reference
  presents the second pass from the first answer.

## Standard / spec (input for v13)

1. **R36.1, offset zero on a pause window.** Two sentences of the criterion
   give different instants. "On a pause window too the offset is measured
   from the start of the window" makes a zero offset mean *the window's
   start*; "An offset of zero means the window is resolved only when it
   fires" makes it mean *the pause*, since the viewer fires a pause window.
   Annex H.3 reads the second; the reference implements the first. That
   is the first of UC-08's three failures (counted as the reference's above).
2. **Annex G has no overlay resolution document for G.9.** UC-07's vector
   says so: "a Player of this specification on these documents follows G.9
   instead, whose overlay resolution document Annex G does not contain". So
   UC-07 has no written outcome for a Player of this specification on D1–D5,
   and the vector writes a legacy Player's. The reference, which is one,
   requests the overlay and pause windows: 10 FAILs (classified as the
   vector's above).

Not FAILs, but the vectors note them as findings of the annexes, and they
stay open: UC-14's slate timing (N.4 "one minute into the slate" read as
slate time vs elapsed time), and UC-21's carriers (no once-per-session and
no late-start-with-offset declaration on an overlay window).

## NOT_VERIFIABLE (70)

| Reason | Count | Where |
|---|---|---|
| The opportunity is ambiguous: `Event@id` 1 is in EventStreams of several schemes and the vector names none | 29 | UC-07 12, UC-08 5, UC-11 6, UC-17 6 |
| The observation carries no audio state: what is heard is not measured | 24 | UC-03 4, UC-09 2, UC-18 5, UC-19 1, UC-21 9, UC-22 3 |
| The criterion has no test (`behaviour/index.yaml`) | 17 | 7 with no carrier (R41.4–R41.7, R42.3, R47.2, R48.3); 3 permissions (R15.3, R21.1, R37.1); 7 not decidable from outside (R1.6, R3.2, R4.5, R11.2, R29.10, R33.2, R44.3) |

The 4 NOT_APPLICABLE: R28.1-2 D1/D5 and R4.10 D1/D4 `requests` (the
criterion does not bind the requests of that session).

## What I did not verify

- The table's classification rests on the code's output plus one reading of
  the vector and the criterion; I did not debug the reference beyond the one
  `--save-raw` of UC-14 D1.
- Whether the vectors' D1–D5 for UC-07 should be the reference's behaviour
  or a legacy Player's is the vector's design question, not answered here.

## Every FAIL

| # | Test | Class | Variant | Field | Classification | Evidence | Alone ×2 |
|---|---|---|---|---|---|---|---|
| 1 | R40.3-2 | D1 |  | presentation | unstable (environment/load) | ad 415 ms late in the battery (observed 8415 vs 8000); PASS alone twice | PASS/PASS |
| 2 | R40.3-2 | D1 |  | beacons | unstable (environment/load) | ad 415 ms late in the battery (observed 8415 vs 8000); PASS alone twice | PASS/PASS |
| 3 | R40.6 | D1 |  | selection | test (vector) | the alternative MPD is written `shows: []` and not in `selection`; the comparator reports it as `linear [ad alt.mpd]` of the insertion event | FAIL/FAIL |
| 4 | R40.6 | D1 |  | presentation | test (vector) | the alternative MPD is written `shows: []` and not in `selection`; the comparator reports it as `linear [ad alt.mpd]` of the insertion event | FAIL/FAIL |
| 5 | R40.6 | D4 |  | selection | test (vector) | the alternative MPD is written `shows: []` and not in `selection`; the comparator reports it as `linear [ad alt.mpd]` of the insertion event | FAIL/FAIL |
| 6 | R40.6 | D4 |  | presentation | test (vector) | the alternative MPD is written `shows: []` and not in `selection`; the comparator reports it as `linear [ad alt.mpd]` of the insertion event | FAIL/FAIL |
| 7 | UC-05 | D1 |  | requests | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 8 | UC-05 | D1 |  | selection | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 9 | UC-05 | D1 |  | presentation | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 10 | UC-05 | D1 |  | beacons | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 11 | UC-05 | D2 |  | requests | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 12 | UC-05 | D2 |  | selection | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 13 | UC-05 | D2 |  | presentation | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 14 | UC-05 | D2 |  | beacons | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 15 | UC-05 | D3 |  | requests | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 16 | UC-05 | D3 |  | selection | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 17 | UC-05 | D3 |  | presentation | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 18 | UC-05 | D3 |  | beacons | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 19 | UC-05 | D4 |  | requests | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 20 | UC-05 | D4 |  | selection | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 21 | UC-05 | D4 |  | presentation | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 22 | UC-05 | D4 |  | beacons | test (vector: response routing) | E.4-1 and E.7.1-1 share one URL with no `aps`/`nth`; the harness answers the first fixture, so the re-request gets E.4-1 (not the empty E.7.1-1) and the ad plays again | FAIL/FAIL |
| 23 | UC-07 | legacy |  | requests | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme (grep of its dist: 0 hits), so the standard break is never fetched | FAIL/FAIL |
| 24 | UC-07 | legacy |  | presentation | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme (grep of its dist: 0 hits), so the standard break is never fetched | FAIL/FAIL |
| 25 | UC-07 | legacy |  | beacons | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme (grep of its dist: 0 hits), so the standard break is never fetched | FAIL/FAIL |
| 26 | UC-07 | D1 |  | requests | test (vector) — cause in the standard | the vector writes D1..D5 as legacy Players; the reference is an SGAI Player and requests the pause and overlay windows (404 by the vector's own `aps`) | FAIL/FAIL |
| 27 | UC-07 | D2 |  | requests | test (vector) — cause in the standard | the vector writes D1..D5 as legacy Players; the reference is an SGAI Player and requests the pause and overlay windows (404 by the vector's own `aps`) | FAIL/FAIL |
| 28 | UC-07 | D3 |  | requests | test (vector) — cause in the standard | the vector writes D1..D5 as legacy Players; the reference is an SGAI Player and requests the pause and overlay windows (404 by the vector's own `aps`) | FAIL/FAIL |
| 29 | UC-07 | D4 |  | requests | test (vector) — cause in the standard | the vector writes D1..D5 as legacy Players; the reference is an SGAI Player and requests the pause and overlay windows (404 by the vector's own `aps`) | FAIL/FAIL |
| 30 | UC-07 | D5 |  | requests | test (vector) — cause in the standard | the vector writes D1..D5 as legacy Players; the reference is an SGAI Player and requests the pause and overlay windows (404 by the vector's own `aps`) | FAIL/FAIL |
| 31 | UC-07 | legacy | pause-requests-nothing | requests | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme (grep of its dist: 0 hits), so the standard break is never fetched | FAIL/FAIL |
| 32 | UC-07 | legacy | pause-requests-nothing | presentation | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme (grep of its dist: 0 hits), so the standard break is never fetched | FAIL/FAIL |
| 33 | UC-07 | legacy | pause-requests-nothing | beacons | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme (grep of its dist: 0 hits), so the standard break is never fetched | FAIL/FAIL |
| 34 | UC-07 | D1 | pause-requests-nothing | requests | test (vector) — cause in the standard | the vector writes D1..D5 as legacy Players; the reference is an SGAI Player and requests the pause and overlay windows (404 by the vector's own `aps`) | FAIL/FAIL |
| 35 | UC-07 | D2 | pause-requests-nothing | requests | test (vector) — cause in the standard | the vector writes D1..D5 as legacy Players; the reference is an SGAI Player and requests the pause and overlay windows (404 by the vector's own `aps`) | FAIL/FAIL |
| 36 | UC-07 | D3 | pause-requests-nothing | requests | test (vector) — cause in the standard | the vector writes D1..D5 as legacy Players; the reference is an SGAI Player and requests the pause and overlay windows (404 by the vector's own `aps`) | FAIL/FAIL |
| 37 | UC-07 | D4 | pause-requests-nothing | requests | test (vector) — cause in the standard | the vector writes D1..D5 as legacy Players; the reference is an SGAI Player and requests the pause and overlay windows (404 by the vector's own `aps`) | FAIL/FAIL |
| 38 | UC-07 | D5 | pause-requests-nothing | requests | test (vector) — cause in the standard | the vector writes D1..D5 as legacy Players; the reference is an SGAI Player and requests the pause and overlay windows (404 by the vector's own `aps`) | FAIL/FAIL |
| 39 | UC-08 | D1 |  | requests | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 40 | UC-08 | D1 |  | presentation | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 41 | UC-08 | D1 |  | beacons | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 42 | UC-08 | D2 |  | requests | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 43 | UC-08 | D2 |  | presentation | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 44 | UC-08 | D2 |  | beacons | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 45 | UC-08 | D3 |  | requests | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 46 | UC-08 | D3 |  | presentation | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 47 | UC-08 | D3 |  | beacons | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 48 | UC-08 | D4 |  | requests | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 49 | UC-08 | D4 |  | presentation | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 50 | UC-08 | D4 |  | beacons | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 51 | UC-08 | D5 |  | requests | reference | pause resolution requested at session 0 (window start) instead of at the pause (30000, offset 0, H.3); after the pause ad the overlay is restored while still paused (60035) instead of on resume (70000); the `mid` beacon follows | FAIL/FAIL |
| 52 | UC-11 | D1 |  | beacons | test (vector) | the activation's `ClickThrough@trackingUris` fire (68 s) and the comparator now counts id-less beacons; the vector says they cannot be listed | FAIL/FAIL |
| 53 | UC-11 | D2 |  | beacons | test (vector) | the activation's `ClickThrough@trackingUris` fire (68 s) and the comparator now counts id-less beacons; the vector says they cannot be listed | FAIL/FAIL |
| 54 | UC-11 | D3 |  | beacons | test (vector) | the activation's `ClickThrough@trackingUris` fire (68 s) and the comparator now counts id-less beacons; the vector says they cannot be listed | FAIL/FAIL |
| 55 | UC-11 | D4 |  | beacons | test (vector) | the activation's `ClickThrough@trackingUris` fire (68 s) and the comparator now counts id-less beacons; the vector says they cannot be listed | FAIL/FAIL |
| 56 | UC-11 | D5 |  | beacons | test (vector) | the activation's `ClickThrough@trackingUris` fire (68 s) and the comparator now counts id-less beacons; the vector says they cannot be listed | FAIL/FAIL |
| 57 | UC-11 | legacy |  | requests | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the break is never fetched | FAIL/FAIL |
| 58 | UC-11 | legacy |  | presentation | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the break is never fetched | FAIL/FAIL |
| 59 | UC-11 | legacy |  | beacons | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the break is never fetched | FAIL/FAIL |
| 60 | UC-12 | D1 | path-2-both-empty | requests | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 61 | UC-12 | D1 | path-2-both-empty | selection | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 62 | UC-12 | D1 | path-2-both-empty | presentation | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 63 | UC-12 | D1 | path-2-both-empty | beacons | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 64 | UC-12 | D2 | path-2-both-empty | requests | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 65 | UC-12 | D2 | path-2-both-empty | selection | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 66 | UC-12 | D2 | path-2-both-empty | presentation | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 67 | UC-12 | D2 | path-2-both-empty | beacons | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 68 | UC-12 | D3 | path-2-both-empty | requests | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 69 | UC-12 | D3 | path-2-both-empty | selection | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 70 | UC-12 | D3 | path-2-both-empty | presentation | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 71 | UC-12 | D3 | path-2-both-empty | beacons | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 72 | UC-12 | D4 | path-2-both-empty | requests | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 73 | UC-12 | D4 | path-2-both-empty | selection | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 74 | UC-12 | D4 | path-2-both-empty | presentation | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 75 | UC-12 | D4 | path-2-both-empty | beacons | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 76 | UC-12 | D5 | path-2-both-empty | requests | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 77 | UC-12 | D3 | path-4-video-only-first | requests | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 78 | UC-12 | D4 | path-4-video-only-first | requests | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 79 | UC-12 | D5 | path-4-video-only-first | requests | test (vector: response routing) | a variant needs a different APS answer for the same URL; the harness answers the first fixture for it (L.5-1 / L.4-1 instead of the variant's document) | FAIL/FAIL |
| 80 | UC-13 | D2 |  | requests | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 81 | UC-13 | D2 |  | selection | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 82 | UC-13 | D2 |  | presentation | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 83 | UC-13 | D2 |  | beacons | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 84 | UC-13 | D3 |  | requests | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 85 | UC-13 | D3 |  | selection | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 86 | UC-13 | D3 |  | presentation | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 87 | UC-13 | D3 |  | beacons | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 88 | UC-13 | D4 |  | requests | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 89 | UC-13 | D4 |  | selection | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 90 | UC-13 | D4 |  | presentation | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 91 | UC-13 | D4 |  | beacons | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 92 | UC-13 | D5 |  | requests | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 93 | UC-13 | D5 |  | selection | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 94 | UC-13 | D5 |  | presentation | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 95 | UC-13 | D5 |  | beacons | test (vector: response routing) | M.5-1..M.5-4 share one URL; the harness answers every class with M.5-1, so D2..D5 get D1's document | FAIL/FAIL |
| 96 | UC-14 | D1 |  | requests | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 97 | UC-14 | D1 |  | selection | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 98 | UC-14 | D1 |  | presentation | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 99 | UC-14 | D1 |  | beacons | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 100 | UC-14 | D2 |  | requests | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 101 | UC-14 | D2 |  | presentation | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 102 | UC-14 | D3 |  | requests | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 103 | UC-14 | D3 |  | selection | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 104 | UC-14 | D3 |  | presentation | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 105 | UC-14 | D3 |  | beacons | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 106 | UC-14 | D4 |  | requests | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 107 | UC-14 | D4 |  | selection | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 108 | UC-14 | D4 |  | presentation | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 109 | UC-14 | D4 |  | beacons | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 110 | UC-14 | D5 |  | requests | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 111 | UC-14 | D5 |  | presentation | reference | module log: `linear:failed` "alternative MPD of type dynamic is not played by this reference" at the crossing of PRT 2700 | FAIL/FAIL |
| 112 | UC-14 | legacy |  | requests | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the slate is never fetched | FAIL/FAIL |
| 113 | UC-14 | legacy |  | presentation | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the slate is never fetched | FAIL/FAIL |
| 114 | UC-15 | D2 |  | requests | test (vector: response routing) | O.5-1 / O.5-2 / O.7-1 share one URL; the harness answers O.5-1 to D2 and D5 | FAIL/FAIL |
| 115 | UC-15 | D5 |  | requests | test (vector: response routing) | O.5-1 / O.5-2 / O.7-1 share one URL; the harness answers O.5-1 to D2 and D5 | FAIL/FAIL |
| 116 | UC-15 | D2 | non-conforming-aps | requests | test (vector: response routing) | O.5-1 / O.5-2 / O.7-1 share one URL; the harness answers O.5-1 to D2 and D5 | FAIL/FAIL |
| 117 | UC-17 | legacy |  | requests | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the break is never fetched | FAIL/FAIL |
| 118 | UC-17 | legacy |  | presentation | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the break is never fetched | FAIL/FAIL |
| 119 | UC-17 | legacy |  | beacons | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the break is never fetched | FAIL/FAIL |
| 120 | UC-19 | D1 |  | requests | test (vector/format) | the request sends the class row's `sgai-video-decoders=2`; the vector expects the session's 1, which the format cannot give the Player (the vector says so) | FAIL/FAIL |
| 121 | UC-21 | D1 |  | requests | reference | no second resolution request after the rewind (45000..55000); the document declares no validity, so a new execution resolves anew (R36.4, R34.6) | FAIL/FAIL |
| 122 | UC-21 | D3 |  | requests | reference | no second resolution request after the rewind (45000..55000); the document declares no validity, so a new execution resolves anew (R36.4, R34.6) | FAIL/FAIL |
| 123 | UC-21 | D4 |  | requests | reference | no second resolution request after the rewind (45000..55000); the document declares no validity, so a new execution resolves anew (R36.4, R34.6) | FAIL/FAIL |
| 124 | UC-21 | D2 |  | requests | reference | no second resolution request after the rewind (45000..55000); the document declares no validity, so a new execution resolves anew (R36.4, R34.6) | FAIL/FAIL |
| 125 | UC-21 | D5 |  | requests | reference | no second resolution request after the rewind (45000..55000); the document declares no validity, so a new execution resolves anew (R36.4, R34.6) | FAIL/FAIL |
| 126 | UC-21 | D1 | dismiss-then-rewind | requests | reference | no second resolution request after the rewind (45000..55000); the document declares no validity, so a new execution resolves anew (R36.4, R34.6) | FAIL/FAIL |
| 127 | UC-21 | D3 | dismiss-then-rewind | requests | reference | no second resolution request after the rewind (45000..55000); the document declares no validity, so a new execution resolves anew (R36.4, R34.6) | FAIL/FAIL |
| 128 | UC-21 | D4 | dismiss-then-rewind | requests | reference | no second resolution request after the rewind (45000..55000); the document declares no validity, so a new execution resolves anew (R36.4, R34.6) | FAIL/FAIL |
| 129 | UC-22 | legacy |  | requests | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the break is never fetched | FAIL/FAIL |
| 130 | UC-22 | legacy |  | selection | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the break is never fetched | FAIL/FAIL |
| 131 | UC-22 | legacy |  | presentation | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the break is never fetched | FAIL/FAIL |
| 132 | UC-22 | legacy |  | beacons | test (instrument: legacy Player) | dash.js 5.3.0 has no `alternativeMPD` scheme; the break is never fetched | FAIL/FAIL |


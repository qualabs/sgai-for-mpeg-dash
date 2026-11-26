# T-09 final — the failing jobs re-run on the final code

**Conclusion.** Every job that failed in the T-09 battery (62), the criterion
tests added since (R34.6-2, R34.6-3, R17.2-2; R13.3-4 and R6.5-3 were already
in T-09 and are re-run too) and a regression sample (one passing job per UC,
10 criterion tests) ran on the final code: 111 jobs, 464 results, **366 PASS,
62 FAIL, 36 NOT_VERIFIABLE**, 8 573 s with concurrency 2. Updated with these
reruns, the battery stands at **1 249 PASS, 62 FAIL, 70 NOT_VERIFIABLE,
4 NOT_APPLICABLE** over 329 jobs (T-09: 1 155 / 132 / 70 / 4 over 323).
**No FAIL left is the reference's.** 5 are unstable (PASS alone twice), 44 are
the test's (vector, format or legacy instrument), 13 have their cause in the
standard (UC-14). No job of the regression sample regressed.

The harness fix of this task (a seek of a hidden primary is not a boundary)
was first written as "drop the seek"; the regression sample caught that it
broke R34.6 and UC-21 (a viewer seek blanks the primary for ~40 ms, so its
`seeking` sample has nothing on screen). The rule that stands holds the seek
until the primary is shown again. The first run (`run1-round1-rule/`) is kept
as the record of that; every number here is from `run2/`, on the final rule.

## Environment

| | |
|---|---|
| Machine | 2 cores (`nproc`) |
| Code | HEAD `b1d643c` + working tree: `bin/conformance/behaviour_compare.py`, `bin/test_behaviour_compare.py` (this task). `reference-player/src` and `spec-source` untouched |
| Players | reference = dash.js 5.3.0 + `reference-player/src/`; legacy = dash.js 5.3.0 alone |
| Browser | Chromium 149.0.7827.55 (Playwright 1.61.1 headless shell) |
| Clock | `presentation` |
| run2 (`uptime`) | start 2026-11-25 17:00:15, load 3.24 2.74 2.78 · end 19:23:36, load 9.08 10.93 16.93 (peaks near 30 around 18:30–19:00 from work outside this task) |
| repeats r1 | 19:25:12 (load 10.49) → 21:54:27 (1.53) |
| repeats r2 | 21:54:27 (1.53) → 2026-11-26 00:24:31 (3.96); load 39.8 at 23:08 |

## Commands

```
# the copies: the T-09 vectors trimmed to the jobs listed (run2/../run1-round1-rule/build_copies.py)
uv run -q --no-project --with pyyaml==6.0.3 python3 build_copies.py <out> spec-source jobs.txt

# run2: failing jobs + regression sample + criterion tests, raw kept for replay
PYTHONDONTWRITEBYTECODE=1 python3 -B bin/check-dash-conformance.py --behaviour --clock presentation \
    --concurrency 2 --log-dir run2/log --save-raw <raw> --vector <copies> spec-source/behaviour/{R13.3-4,
    R6.5-3,R34.6-2,R34.6-3,R17.2-2,R4.2-1,R5.6-1,R12.5-1,R17.2,R20.1-1,R28.1-1,R32.1-1,R34.6,R36.1-1,R40.4-1}.yaml

# each run2 FAIL job alone, twice (repeats/run-repeats.sh: concurrency 1, r1 then r2)
python3 bin/check-dash-conformance.py --behaviour --clock presentation --concurrency 1 \
    --log-dir repeats/r<n>-log --vector repeats/vectors/*.yaml

# the same run2 record compared by three comparators (replay/)
python3 bin/check-dash-conformance.py --behaviour --replay <raw>
```

Exact command lines: `run2/command.txt`; job lists: `run1-round1-rule/jobs-a.txt`
(the 62 T-09 FAIL jobs), `jobs-sample.txt`, `repeats/jobs.txt`.

## The harness fix

`observed_segments` (`bin/conformance/behaviour_compare.py`): a seek of the
primary while it is not on screen splits nothing where it happens; it is held
and marks the sample where the primary is shown again, whose time is the next
segment's `from`. A seek of a primary on screen still splits.

- Test: `Presentation.test_seek_of_a_hidden_primary_is_not_a_change` — the
  linear-ad shape (seek at 25 000 under the ad: segments 0 / 10 000 / 40 000,
  `from` 40 000), the negative (on screen: splits), the exact tolerance (250:
  no split), a hidden seek as the last sample, one with nothing on screen, and
  R34.6 D1's recorded samples (seek blanks the primary 12 342–12 383: one
  boundary at 12 383, `from` 3000; the same blank without the seek folds).
- Mutations (`mutation-hidden-seek.out`, round 3 with bytecode caching off):
  drop the seek (round-1 rule), split where it happens (HEAD), never split,
  never release, release on any sample — all five red; restored green.
  Rounds 1–2 in that file are superseded: a restore in the same second as a
  same-size mutant imported the mutant's cached `.pyc`.
- Replay of run2's record (`replay/`), same browser data, three comparators:

| Comparator | Result | Jobs that differ from final |
|---|---|---|
| HEAD | 364 PASS, 64 FAIL | UC-02 D1, UC-20 D1 presentation: "a change at 58 177 from linear [ad-201] to linear [ad-201], which the vector does not have" (the hidden seek) |
| round-1 rule | 352 PASS, 76 FAIL | R34.6 D1/D3/D4, R34.6-2 D1/D3/D4, UC-21 ×8 presentation (the viewer's seek lost) |
| final | 366 PASS, 62 FAIL | — (identical to run2's live verdicts) |

- Suite: `bin/test_*.py`, 29 files, all exit 0 (`suite.out`, 239 s).

## Time

| | seconds |
|---|---|
| run2, concurrency 2 (`wall`) | 8 573.2 (2 h 23 min) |
| run2 serial estimate (Σ `observe_until`, 111 jobs) | 16 446 → speed-up 1.92× |
| repeats r1 / r2, concurrency 1, 38 jobs (Σ `observe_until` 8 774) | 8 954.1 / 9 003.3 |
| run1 (round-1 rule, superseded) | 8 484.2 |

## Before (T-09) → after, per job

Full table: `run2/before-after.md` (111 rows). The jobs whose verdict changed:

| Job | T-09 | final | Why |
|---|---|---|---|
| UC-05 D1–D4 | 4 FAIL each | 4 PASS | routing per request (`2ba5835`) |
| UC-12 [path-2-both-empty] D1–D5, [path-4-video-only-first] D3–D5 | FAIL | PASS | routing |
| UC-13 D2, D5 | 4 FAIL | 4 PASS | routing |
| UC-13 D3, D4 | 4 FAIL | 1 FAIL (requests) | routing; the capability FAIL remains |
| UC-15 D2, D2 [non-conforming-aps], D5 | 1 FAIL | PASS | routing |
| UC-08 D1–D4 | 3 FAIL | 1 FAIL (beacons) | pause window resolved at the pause, overlay suspended for the whole pause (`3c8dc1a`) |
| UC-08 D5 | 1 FAIL | PASS | same |
| UC-21 ×8 | 1 FAIL (requests) | PASS | re-resolution after a seek (`3c8dc1a`) |
| UC-14 D1, D3, D4 | 4 FAIL | 3 FAIL | the dynamic slate is played (`f6004fa`); requests now PASS |
| R40.3-2 D1 | 2 FAIL (unstable) | 2 FAIL (unstable) | ad 445 ms late under load; PASS alone twice, as in T-09 |
| R28.1-1 D1 [no-activation] | PASS | 2 FAIL (unstable) | ad 264 ms late under load; PASS alone twice |
| UC-12 D1 | PASS | 1 FAIL (unstable) | `complete` 7 213 ms late under load; PASS alone twice |
| New: R34.6-2 D1/D3/D4, R34.6-3 D1/D4, R17.2-2 D1 | — | all PASS | |

Unchanged FAIL: R40.6 D1/D4, UC-07 (12 jobs), UC-11 (6), UC-14 D2/D5/legacy,
UC-17 legacy, UC-19 D1, UC-22 legacy. The regression sample (UC-01, 02 ×2,
03, 04, 05 [resume-at-734], 06, 09, 10, 12, 13, 15, 16, 17, 18, 20, 21
[seek-to-1015], 22, and R4.2-1, R5.6-1, R12.5-1, R17.2, R20.1-1, R28.1-1,
R32.1-1, R34.6, R36.1-1, R40.4-1): every job as in T-09 except the two
unstable ones above. UC-07, 08, 11, 14 and 19 had no passing job in T-09 to
sample.

## Totals

| | jobs | PASS | FAIL | NOT_VERIFIABLE | NOT_APPLICABLE |
|---|---|---|---|---|---|
| T-09 | 323 | 1 155 | 132 | 70 | 4 |
| − T-09 results of the 105 re-run jobs | | −272 | −132 | −36 | 0 |
| + final results of the 111 jobs (105 + 6 new) | +6 | +366 | +62 | +36 | 0 |
| **Updated** | **329** | **1 249** | **62** | **70** | **4** |

(1 155 − 272 + 366 = 1 249; 132 − 132 + 62 = 62; 70 − 36 + 36 = 70, of which 17
are `index.yaml`'s criteria with no test.) The jobs not re-run keep their T-09
verdict on the T-09 code; the sample above is the evidence that they hold.

## FAILs by class (run2)

Each FAIL job ran alone twice (`repeats/repeats.md`, run2 / r1 / r2 per job).

| Class | FAILs | Jobs | Alone ×2 | Evidence |
|---|---|---|---|---|
| unstable (environment: load) | 5 | 3 | PASS/PASS | R40.3-2 D1 (ad at 8 445 for 8 000), R28.1-1 D1 [no-activation] (imp at 2 264 for 2 000), UC-12 D1 (`complete` at 87 213 for 80 000); load 9–30 during run2 |
| test — instrument: legacy Player | 18 | 6 | FAIL/FAIL | UC-07 legacy ×2, UC-11, UC-14, UC-17, UC-22 `legacy`: dash.js 5.3.0 has no `alternativeMPD` scheme, so the break / slate is never fetched (`requests[0] … not observed`) |
| test — vector (cause in the standard) | 10 | 10 | FAIL/FAIL | UC-07 D1–D5 and [pause-requests-nothing] D1–D5 `requests`: the vector writes legacy outcomes; the reference requests the pause and overlay windows ("unexpected request …/nl/pause?show=8 at 0") |
| test — vector | 4 | 2 | FAIL/FAIL | R40.6 D1/D4 `selection`, `presentation`: the alternative MPD is written `shows: []` and not in `selection`; observed "linear [ad R40.6/alt.mpd]" for event 1 |
| test — vector | 4 | 4 | FAIL/FAIL | UC-08 D1–D4 `beacons`: the vector writes the restored overlay's `mid` at 85 000; the reference sends it at ≈74 990, 5 s after the overlay is restored at 70 000 |
| test — vector | 5 | 5 | FAIL/FAIL | UC-11 D1–D5 `beacons`: the ClickThrough tracking beacons carry no `@id`, the vector does not list them, and the comparator counts them ("unexpected beacon …/click?cr=1101 at 68 032") |
| test — vector/format | 2 | 2 | FAIL/FAIL | UC-13 D3/D4 `requests`: `sends_capabilities` is per vector, so D3/D4 send `sgai-html-over-video=1` where Annex M.3 needs the per-class set |
| test — vector/format | 1 | 1 | FAIL/FAIL | UC-19 D1 `requests`: the vector expects `sgai-video-decoders=1`, the D1 profile sends 2; the session capability cannot be handed to the Player by the format |
| standard | 7 | 5 | FAIL/FAIL | UC-14 D1–D5 `selection` and D2/D5 `presentation`: the blackout slate is presented as a linear ad of event 31 (replace); the vector writes it as nothing (`shows: []`, "the format has no element for the slate") |
| standard | 6 | 3 | FAIL/FAIL | UC-14 D1/D3/D4 `presentation` + `beacons`: overlay over the slate 60 006–73 805 (13.8 s of 20); `complete` never |
| **reference** | **0** | | | |
| **Total** | **62** | **38** | | 5 not reproducible, 57 FAIL/FAIL |

One observation outside the totals: UC-08 D2 `presentation` FAILed in r2 only
(pause ad at 30 449 for 30 000; PASS in run2 and r1), at load 39.8.

## Standard / spec (input for v13)

1. **Annex G has no overlay resolution document for G.9.** UC-07's vector
   says so, so D1–D5 have no written outcome for a Player of this
   specification and carry a legacy Player's. 10 FAILs (UC-07).
2. **A replacement that is not advertising has no place in the model.** The
   blackout slate of UC-14 (an `alternativeMPD:replace` event) is, to the
   reference and the comparator, a linear ad presentation of event 31; the
   vector says it is neither the primary nor an ad and writes it as nothing.
   Neither the specification nor the vector format says how such a
   replacement is presented, selected or reported. 7 FAILs (UC-14).
3. **Live-latency coupling of a dynamic alternative MPD.** The slate starts at
   its live edge (§5.16.2.2.6) while the channel plays its Player's delay
   behind its own. From run2's record of UC-14 D1: at the slate's entry
   (session 60 006) the slate's time is 66 198, not 60 000; the overlay
   window, slate time 60 000–80 000, is already open and closes at slate
   79 722, so it is on screen 13.8 s. Annex N assumes both at the same
   latency (the vector's own header: "their live-edge latencies need not be
   equal"). 6 FAILs (UC-14).
4. From T-09, no FAIL left: R36.1's two readings of offset zero on a pause
   window. The reference now resolves at the pause (Annex H.3's reading) and
   UC-08's requests pass; `context/` did not change since, so the two
   sentences still read differently.

## What I did not verify

- The 218 T-09 jobs not re-run keep their T-09 verdicts; the sample (43 jobs,
  R13.3-4 and R6.5-3 included) is the evidence they hold, not a re-run of each.
- The run2 record (142 MB) was used for the replays and then deleted; the
  replay summaries are in `replay/`.
- The classes "test — vector" and "standard" rest on the code's output plus
  one reading of the vector; I did not change any vector.

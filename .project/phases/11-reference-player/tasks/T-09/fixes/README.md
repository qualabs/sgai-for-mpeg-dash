# T-09 fixes: comparator, R16.1's `from`, R40.9-2 and R40.9-3

Runs: `check-dash-conformance.py --behaviour --clock presentation --only
R16.1,R17.1,R17.2,R17.5,R40.4,R40.9 --concurrency 2 --reference <scratch copy
of HEAD's reference-player/src>`. Full logs here as `*.behaviour.log` (the
paths inside the summaries point to the removed scratch folder).

| Run | File | Result |
|---|---|---|
| before | `before.summary` | 37 PASS, 19 FAIL |
| after | `after.summary` | 44 PASS, 12 FAIL |
| after, again | `after-rerun.summary` (`after2.behaviour.log`) | 44 PASS, 12 FAIL |

## Before / after per field

| Test, field | before | after | after, again |
|---|---|---|---|
| R16.1 D1 presentation | FAIL `from` 3076, expected 3000 ± 17 | PASS | PASS |
| R17.1 D1 selection | FAIL 1 presentation more | PASS | PASS |
| R17.2 D1 selection | FAIL 1 presentation more | PASS | PASS |
| R17.5 D1 selection | FAIL 1 presentation more | PASS | PASS |
| R40.4-1 D1, D4 selection | FAIL | PASS | PASS |
| R40.9-3 D1 presentation | FAIL ad at 6976, expected 6000 ± 250 | PASS | FAIL: blank on return (below) |
| R40.9-3 D1 beacons | FAIL imp 6976, complete 12965 | PASS | PASS |
| R40.9-3 D4 presentation, beacons | PASS | PASS | PASS |

What still fails, by class:

- **10 × beacons** (R17.1, R17.2, R40.4-1 D1/D4, R40.4-2 D1/D4, R40.9-1
  D1/D4, R40.9-2 D1/D4): **reference, T-08's**. Non-linear beacons are not
  fired by HEAD's reference ("observed at never").
- **R40.4-2 presentation** (D4 before; D1 and D4 after; D1 after, again) and
  **R40.9-3 D1 presentation** (after, again; D4 in the M9 run): one signature.
  When the break ends, nothing is on screen for 376–1025 ms before the primary's
  first frame (`none [nothing]` 10054..11079, 13025..13444, 12598..12974).
  The module log of R40.4-2 D1 shows `linear:terminate` and the move to RT,
  with the samples empty until the primary's frame at RT. It comes and goes
  between runs. It has the same signature as UC-02's and R6.5-2's FAILs in
  `harness-r3/`. **Class: standard (gap)**, with the vectors depending on it.
  Base 5.16.2.2.5 says only "Playhead is moved to RT". No text bounds how long
  the return may show no picture, yet the vectors expect the primary within
  250 ms. Not fixed here.

## 1. `presentations()`: suspension and restore

A surface is now one presentation for each (identity, `inst`, `pass`),
however long it was gone. Before, a gap over the tolerance started a new one.

- Unit tests `SuspendedSurface` (four cases: a 3000 ms gap, no gap, a new
  `inst`, a new `pass`). Against HEAD's comparator they fail; after the fix
  they pass (`unit-before-after.out`).
- `bin/test_behaviour_harness.py::test_flicker_shorter_than_the_tolerance_is_the_same`
  asserted the old rule: back after a 300 ms gap counted as a new
  presentation. It is now `test_the_same_element_back_after_any_gap_is_the_same`,
  with gaps of 200, 300 and 3000.
- Raw record (independent check): R16.1's pause ad is `inst` 2 across the
  whole pause. R17.1/R17.5's restored surfaces are the same `inst`/`pass`
  (T-07 f2 README).

## 2. R16.1: a tolerance for `from` alone

The schema now lets a `primary` element carry its own `tolerance`, and it
applies to its `from` only. The segment's `tolerance` still holds the start
boundary (and `from`, when the primary has none). On any other element the
schema refuses the field (`schema-negative.out`). This is in
`scenarios/README.md`. `_silent` leaves the field out of a surface's identity.

R16.1 uses `tolerance: 250` on the primary after the resume. R16.1 bounds when
the ad leaves ("within one rendering frame") and that the content returns
("immediately"). It does not bound the media position to the frame, so the
position goes back to the usual instrument tolerance, the same as every other
`from`. Measured in the raw record: paused at 3027; the first sample after
the resume, 5 ms after the ad left, shows 3076 (+49).

No existing field could do this. A window `from: {3000, 3100}` would still
add the segment's 17 ms on each side. Its bound would also be read off
Chromium, not off the criterion, and the schema describes a `from` window as
something else (a primary that plays across a window boundary).

## 3. R40.9-3 and R40.9-2

**R40.9-3.** The ad's start is the window 6000..7000, written 6001..7000 on
the segment because `check-scenarios` S-TIME requires a segment's end to be
after its start. The bound comes from the base text that R40.9 defers to:
"PRT ≤ PRTA ≤ EAP" (5.16.2.1), and "the execution may happen later, i.e. when
PRTA > PRT and PRTA = PHP. If the event is no longer active, it is ignored"
(5.16.2.2.1). EAP = PRT + Event@duration = 7000. Everything timed from the
start moves with it: the ad MPD request {6000, 7000}, the ad's end and the
return {12000, 13000}, the beacons, and the return's `from`
{6000, 7000} (RT = PRTA, 5.16.2.2.1). A held segment 6000..start covers the
Player that holds the content while the break resolves (5.16.2.2.6 NOTE 2).
It may be empty.

That vector needed one comparator fix. Observed changes are now matched to
written boundaries in order, by DP: the most pairs, then the least distance.
Before, each change took its nearest boundary. A hold beginning at 6056 fell
inside the window, so it took the window, and the ad's real start at 6976 was
left unmatched. Tests: `HeldThenWindow` (the hold then a late ad, no hold, the
window's edge 7250/7251, a hold outside the exact boundary). The 172 recorded
jobs were replayed with the new comparator (`after-crit`, `after-uc` and this
`before`; `replay-diff.out`). No verdict changed except the targeted ones.

The reference's ad start in D1: 6976 (before), 6993 (after, again). That is at
the edge of EAP, from roughly 950 ms between resolving and the ad's first
frame. Inside the bound it is a PASS. Past 7250 it would be a reference FAIL.

**R40.9-2.** I chose to list `list.mpd` and `ad.mpd` as its fixtures. The
other option was to count unlisted requests to a document host as document
requests in the comparator. Listing them is exact: it serves exactly what a
Player that lets the insertion through would get. A host-based rule would
need a heuristic for "document host": `ads-cdn` also serves creatives and
segments, the harness records HTML iframes as `document` resourceType, and
the APS host could also serve beacons. That heuristic is an instrument change
with a risk of false FAILs across the whole battery. The general hole stays
open (see the report: a check-scenarios rule).

**M9** (supersede suppressor always false; `m9.diff`) against the scratch
copy now FAILs R40.9-2 `requests` (break and ad.mpd unexpected), `selection`
(ad for event 2), `presentation` (hold at ~6100, linear at 6611–7031) and
`beacons`, on D1 and D4 (`m9.summary`). Before the change it survived.

## Mutations of the comparator fixes (`unit-mutations.out`)

| Break | Tests | Result |
|---|---|---|
| run key without `pass` | SuspendedSurface | killed (restarted video) |
| run key without `inst` | SuspendedSurface | killed (new element) |
| `tolerance` counted in a surface's identity | PrimaryFromTolerance | killed (silent boundary) |
| primary's `tolerance` ignored | PrimaryFromTolerance | killed (2) |
| nearest-boundary matching instead of in order | HeldThenWindow | killed (2) |

## Suite

`bin/test_*.py`: 29 files, 686 tests, all exit 0 (`suite.out`).
`check-behaviour.py` 0, `check-scenarios.py` 0.

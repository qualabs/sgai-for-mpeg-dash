# T-05 — The 6th edition's linear model in the reference

## Conclusion

`reference-player/src/sgai-linear.js` implements insertion and replacement
(§5.16), the queue by PRT with `@executeOnce`, `@maxDuration` (zero, absent,
cumulative over a List), `@clip`, `@returnOffset`, `@earliestResolutionTimeOffset`,
`@startWithOffset`, the List MPD with its `ImportedMPD`s (§8.14, §5.3.2.6) and
the callback events of the alternative MPDs (§5.10.4.5). Every decision it
takes in media time (PRTA, ASO, APDadj, APDA, RT, which event, which Linked
Period) matches the value worked by hand from Table 57 in every run
(`timing.out`).

**The linear tests do not all pass on the session clock, and no remaining FAIL
is a reference bug that was found.** Each remaining FAIL is one of:

| Class | Tests | Evidence |
|---|---|---|
| **Page too slow for the session clock** (environment): the primary plays at 0.32–0.99× real time and an ad's N s take up to 1.2·N s of wall clock on this 2-core machine, so a transition the vector puts at session T comes T·(1−speed) late | R4.2-2, R4.8, R20.1-7, R6.5-2, UC-01, UC-06, UC-07, E1–E9, E11 (presentation/beacons) | `timing.out` (speed per job); at tolerance 750 ms the same jobs pass every field except where the lateness exceeded 750 (`mutation-campaign-wide.out`, the baselines) |
| **Comparator attribution** (test/harness defect) | R30.2 selection/presentation | the vector serves two documents at one URL (`nth` 1 and 2); `Fixtures.of()` maps the ad's `data-sgai-doc` URL to the first fixture with it, `5.2.3-1.mpd`, so the alternative actually shown (`alt.mpd`, the 2nd answer) is reported as the empty List |
| **Needs the non-linear window family (T-06)** | R40.3-1 requests (no window request), R40.3-2 (insertion runs at its PRT 6 s, not late at 8 s) | the hook is in place: `ref.linear.addSuppressor(fn)` |
| **Needs the pause family (T-07)** | R17.5 (pause ad absent) | the linear part (the ad suspended and resumed where it was) is E11, and M20 shows it can fail |
| **Harness: dynamic MPDs cannot be joined at `play_from`** | UC-02 (both variants), UC-20 | B.2-1's `availabilityStartTime` is 2026-09-26; dash.js starts at the live edge (primary media time 5 083 636 s), 570 s is outside the 30 min time-shift buffer, and the module logs the event `linear:expired` (`uc-run.out`) |

UC-04, UC-11, UC-17, UC-22 mix a linear break with an overlay window and were
not run: their verdicts depend on T-06.

## Seen failing first (D-11)

`baseline-skeleton.out`: the 11 linear jobs on the skeleton, 40 FAIL / 4 PASS.
The 4 PASS are R4.7-1, whose expected outcome is "nothing happens"; mutation
M03 shows it fails when `@maxDuration="0"` is executed.

## What was built

- `reference-player/src/sgai-linear.js` (new): the family. Readings it takes
  where the base leaves room are in its header: no queue reset after a
  termination (A.14.5, the T-01 finding stays open); before an alternative
  plays only its first Linked Period is resolved, the others from
  PeriodStart − `@earliestResolutionTimeOffset` of its own playhead; a due
  event whose document is in flight holds the primary at PRT for at most 3 s.
- `reference-player/src/sgai-reference.js`: loads the family files itself
  (`FAMILY_FILES`), so the harness page needs no change per family; `start()`
  creates the player at once and initialises it when the families are in
  (returns a promise the adapter ignores); exposes `ref.url` (main MPD URL).
  The observation contract is unchanged.
- `vectors/` (11 edge vectors E1–E11, their fixtures and generators, and
  `run-edges.py`): the rules no test of `spec-source/behaviour/` reaches —
  `@executeOnce` after a success, re-execution after a seek, `@clip`
  true/false on a late join, `@startWithOffset`, `@returnOffset`, APDA 0, a
  Linked Period that fails, a join after EAP, a late insertion (RT = PRTA),
  a pause during a linear ad. Each expected value is worked from Table 57 in
  the vector's header. They live here because `spec-source/behaviour/` is
  another worker's; their fixtures are outside `spec-source/`, so
  `run-edges.py` composes a source (links + `t05/`) under `$XDG_RUNTIME_DIR`.
- `mutate.py` (campaign), `timing.py` (media decisions vs page speed).

## Measured behaviour worth knowing

- dash.js 5.3.0 dispatches every MPD event again (on-receive) after a seek.
  §5.16.2.2.4 step 1 says a known event with `@status` absent gets no further
  processing, so the module ignores it; otherwise the reset it triggers put
  an executed replacement back (seen: E5 re-executed at RT).
- dash.js fires an MPD callback at presentation time 0 the moment a preloaded
  player initialises, before anything is shown (seen: R4.8 `start` beacon at
  session 0). The module takes the callback events out of the copy it hands
  dash.js and fires them itself as the alternative's playhead passes them,
  with §5.10.2.4's dedup over one execution (a List is one presentation).
- Without the start gate, a join inside an active interval or a pre-roll
  shows the primary's paused first frame for 0.3–1.2 s before the
  alternative (UC-01, E4, E5); M23 shows the gate is what prevents it.

## Mutation campaign

One break per rule, each against only the tests that cover it; CAUGHT = a
field that passes on the unmutated module fails with the break, both run in
the same campaign. Module sha256 restored and checked after every break.
Because this machine's lateness (hundreds of ms) can both mask and fake a
red at the vectors' 250 ms, the breaks whose effect is seconds ran with every
tolerance widened to 750 ms (`--wide 750`); the two whose effect is under a
second (M18: 0.5 s; M23: a 0.3–0.5 s glimpse) ran at the vectors' own.

| Break | Rule | Tests | Result |
|---|---|---|---|
| M01 | `@executeOnce` ignored | E1 | CAUGHT (request again at 11 s) |
| M02 | a failed execution counts | R30.2 | CAUGHT |
| M03 | `@maxDuration` 0 executed | R4.7 | CAUGHT |
| M04 | QE in document order | R20.3 | CAUGHT |
| M05 | no next event after a failure | R20.1 | CAUGHT |
| M06 | insertion cap ignored | R4.2 | CAUGHT (ad-2 still on at 8–10 s) |
| M07 | absent `@maxDuration` = 5 s | R4.8 | CAUGHT |
| M08 | ERT ignored | R30.2 | CAUGHT (request at 0, not 2 s) |
| M09 | `@clip` ignored | E3 | CAUGHT |
| M10 | RT with `@clip=false` | E4 | CAUGHT |
| M11 | `@startWithOffset` ignored | E5 | CAUGHT |
| M12 | `@returnOffset` ignored | E6 | CAUGHT |
| M13 | APDA 0 executed | E7 | CAUGHT |
| M14 | a failed Linked Period ends the break | E8 | CAUGHT |
| M15 | all Linked Periods resolved up front | R4.2, UC-01 | CAUGHT (ad2/cr102 requested at 0) |
| M16 | callback dedup removed | R6.5 | **NOT CAUGHT by the rule**: the mutant's beacons show `unexpected beacon …/ad2-imp`, which the baseline does not, but the baseline's beacons field already failed on lateness (ad-2 started 1.1 s late), so PASS→FAIL could not fire |
| M17 | callbacks left to dash.js | R4.8 | CAUGHT |
| M18 | insertion RT = PRT | E9 | CAUGHT (`from` 2000, expected 2500) |
| M19 | a seek does not reset QE | R30.2 | CAUGHT |
| M20 | pause not taken by the linear ad | E11 | CAUGHT (ad ends at 10.3 s, expected 12) |
| M21 | QE reset at termination (literal 1a) | E2 | CAUGHT (re-executed at once) |
| M22 | expired events executed | E10 | CAUGHT |
| M23 | no start gate | E4, E5 | CAUGHT (E5: `0..496 none [primary (paused)]`) |

Not covered by any break: the Linked Period's `@duration` taking the smaller
of the two (no fixture has an imported MPD shorter than its Linked Period).

## Independent check (by hand, Table 57)

E3 (join 4, PRT 2, APDmax 6, APD 8, clip true): APDadj = max(6−4+2, 0) = 4,
APDA = min(8, 4) = 4, RT = 2+4 = 6 → module `APDadj 4, APDA 4, RT 6`.
E4 (clip false): APDadj 6, APDA 6, RT = PRTA+APDA = 10 → module `6, 6, 10`.
E5 (startWithOffset): ASO = 2, APDA = min(8−2, 4) = 4, RT 6 → module `ASO 2,
APDA 4, RT 6`. R20.3-2: APDadj = 8−6+2 = 4 → module `4`. R4.2-2: APDA =
min(4+4, 6) = 6, ad-1 on screen 4.024 s, ad-2 2.020 s. E6: RT = 2+9 = 11 →
module `RT 11`. Source: `timing.out`.

## Files

`baseline-skeleton.out`, `linear-run.out` (the 11 linear jobs on the final
module), `edges-run.out`, `uc-run.out` (UC-02, UC-20, UC-07), `timing.out`,
`mutation-campaign-wide.out`, `mutation-campaign-narrow.out`.

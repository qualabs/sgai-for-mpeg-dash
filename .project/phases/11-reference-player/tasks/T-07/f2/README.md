# T-07 family 2 — pause

Criteria: R16.1, R17.1, R17.2, R17.5, R25.1, R31.2, R35.4 (-1, -2), R35.5,
R37.2. 15 jobs, 60 fields.

## Conclusion

- **48 PASS, 12 FAIL. No FAIL is the reference's**, so no source file
  changed.
- 8 FAILs are `beacons` (T-08's), 3 are `selection` (the comparator), and
  1 is R16.1 `presentation` (the harness's one-frame action).
- The mutation campaign killed 10 of 10 breaks. That includes family 1's
  surviving M10 ("only the top form is visible"), which R17.1 kills here.

## How it ran

- The runner came from a HEAD snapshot (`git archive HEAD bin spec-source
  reference-player`) under `~/.cache/cto-tmp/t07f2-*/`, with the live
  `bin/players/node_modules` linked in. The live `reference-player/src/` was
  rsynced in before each run. It included the harness agent's uncommitted
  edit to `sgai-reference.js`, which was left alone.
- Command: `python3 bin/check-dash-conformance.py --behaviour --clock
  presentation --only R16.1,R17.1,R17.2,R17.5,R25.1,R31.2,R35.4,R35.5,R37.2
  --concurrency 1`. Load average was 2.4–2.8.
- The full log is in `baseline.log`. Mutations applied to the snapshot copy
  only are in `mutation-campaign.out`.

## Results (baseline)

| Job | requests | selection | presentation | beacons |
|---|---|---|---|---|
| R16.1 D1 | PASS | PASS | **FAIL (harness)** | PASS |
| R17.1 D1 | PASS | **FAIL (comparator)** | PASS | FAIL (T-08) |
| R17.2 D1 | PASS | **FAIL (comparator)** | PASS | FAIL (T-08) |
| R17.5 D1 | PASS | **FAIL (comparator)** | PASS | PASS |
| R25.1 D1 | PASS | PASS | PASS | PASS |
| R31.2 D1, D4 | PASS | PASS | PASS | FAIL (T-08) |
| R35.4-1 D1, D4 | PASS | PASS | PASS | FAIL (T-08) |
| R35.4-2 D1, D4 | PASS | PASS | PASS | FAIL (T-08) |
| R35.5 D1, D5 | PASS | PASS | PASS | PASS |
| R37.2 D1, D4 | PASS | PASS | PASS | PASS |

### Each FAIL, by class

| FAIL | Class | Evidence |
|---|---|---|
| R16.1 presentation | **harness**: this is the known need for a frame-based (rAF) action | The removal was observed at 6066, against 6000 ± 17. Under M1, which defers the removal by 1 s, it moved to 7041: the module removes at the action, and the action arrives about 40–66 ms late. |
| R17.1, R17.2, R17.5 selection | **test/instrument (comparator)** | `presentations()` in `behaviour_compare.py` counts the same surface as a new presentation when it comes back after a gap longer than the tolerance. A suspension followed by a restore is that gap. Raw record (`--save-raw`): R17.1's overlay is the same surface (`inst` 2) before and after the pause (3978 → 7440 hidden → 10447 back). R17.5's linear ad is `inst` 2, `pass` 0 before and after (3892 → 7085 → 10033), with no restart. The vectors are right: one presentation, resumed. The same live code (with the harness agent's edits) has the same rule. |
| 8 × beacons (R17.1, R17.2, R31.2 ×2, R35.4-1 ×2, R35.4-2 ×2) | **T-08** | `observed at never`: the non-linear family fires no beacon yet. R17.5's beacons come from the linear family and PASS. |

### Standard list (for v13)

None. No FAIL comes from the spec or `context/`.

## Mutation campaign

Each break was one edit, made only in the snapshot's copy. Each ran only on
the tests that cover its rule. A break is **killed** when a FAIL appears
that the baseline does not have.

| # | Rule | Break | Tests | Result |
|---|---|---|---|---|
| M1 | R16.1 | the pause ad's removal on resume is deferred 1 s | R16.1, R37.2 | killed: R37.2 D1/D4 `presentation` (change at 9021/9080, not 8000). R16.1's change moved 6066 → 7041 |
| M2 | R17.1 (family 1's M10) | the compositor leaves non-top forms visible | R17.1, R17.2 | killed: R17.1 `presentation[2]` shows the overlay together with the pause ad from 5015 to 8097 |
| M3 | R17.2 | the suspended-handle resume in `closePause` is replaced by an end | R17.1, R17.2 | **survived**: see the finding below |
| M3b | R17.2 | every overlay is ended at the resume | R17.1, R17.2 | killed: `presentation[3]` 8000..15000, no overlay |
| M4 | R17.5 | the resume over a linear ad resumes the primary, not the ad | R17.5 | killed: `presentation[4]`, and beacons 2–3 never fire |
| M5 | R25.1 | on a dynamic MPD the pause does not pause the primary | R25.1 | killed: `presentation[2]` primary from 70533, expected 64000 |
| M6 | R31.2 | the slot cap bounds the pause slot | R31.2 | killed: D1/D4 `presentation`, the ad leaves at 4083/4006 |
| M7 | R35.4 | a dismissal on a pause slot ends only the current candidate | R35.4 | killed: R35.4-2 D1/D4 `selection` and `presentation` (B appears at 6099/6024); D4 `requests` (request-again at 10026) |
| M8 | R35.5 | a dismissed takeover skips the primary forward 6 s | R35.5 | killed: D1/D5 `presentation`, primary from 8011, expected 2000 |
| M9 | R37.2 | the resume seeks the primary forward 2 s | R37.2 | killed: D1/D4 `presentation`, primary from 5064, expected 3000 |

**Why M3 stayed green.** During a pause, an overlay's handle is not
`suspended`. It is hidden only because the compositor shows the top form,
and the pause ad is that form. The overlay comes back at the resume because
the pause handle is removed, not through `closePause`'s resume loop. So M3
changed a path that the pause case never reaches. That loop serves the case
where the overlay was also suspended for another reason, such as R40.9. M3b
breaks the path that is actually used, and it is killed.

**Not breakable by code here.** R17.1's frozen slot timeline (the overlay's
5 s beacon at 10 s and not at 7 s) is decided only by the `beacons` field.
That field is T-08's, so a break of the freeze shows only once beacons fire.

## Independent check (R31.2, by hand from the fixtures)

- `main.mpd`: the pause window runs 0–60000 (timescale 1000), with
  `durationCap="2000"`, which is 2 s.
- `pause.xml`: one candidate, `duration="PT6S"`, `onExhausted="stop"`.
- context/03 R31.2: "The Publisher-declared slot cap (R4) MUST NOT be
  interpreted as bounding the duration of a pause slot."
- The pause is at 2 s, so the ad should show from 2 s to 8 s. Read as a
  cap, it would show from 2 s to 4 s. The baseline PASSes 2–8 s. Under M6,
  which applies the cap, the ad left at 4083/4006: the 2 s the hand
  computation predicts.

## Files changed

- Source: none.
- Evidence: this README, `baseline.log`, `mutation-campaign.out`.

## Findings (out of scope, not fixed)

1. **Comparator: a suspension and its restore count as two presentations**
   (`bin/conformance/behaviour_compare.py`, `presentations()`). The same
   `inst`/`pass` coming back after a gap longer than the tolerance is
   counted again. A fix would keep the run open across any gap when `inst`
   and `pass` are unchanged, because a new DOM element or a restarted video
   already marks a new pass. This fails R17.1, R17.2 and R17.5 `selection`.
2. **`closePause`'s resume loop is never reached by the pause tests** (M3).
   No test here has an overlay that is both suspended and under a pause.

# T-08 family a — beacons of non-linear candidates

## Conclusion

- The reference now fires each candidate's `<svta:Tracking>` callback events
  on the candidate's own presentation (R13.1), for whichever option is
  presented (R13.6, candidate level), never past the end of that presentation
  (R13.3: cap trim, dismissal, resume from a pause ad), with the `@id` scope one
  presentation of one candidate and de-duplication by `@id` and by URL at one
  time (R6.5), and ignoring foreign-namespace content of the carrier (R6.4).
- **My tests: 36/36 fields PASS** (were 28 PASS, 8 FAIL: every non-linear
  beacon "observed at never"). An exact beacon-set check (below) agrees: 9/9
  jobs fire exactly the expected URLs.
- **T-07 beacon-only FAILs: all non-linear beacons now PASS** (26/28 jobs exact).
  The 2 that remain are R40.4-2 D1/D4: the **linear** ad's `complete`
  callback. That is a fault in the linear family (`sgai-linear.js`, T-05's). I
  did not touch it (see "Findings").
- **Comparator gap (test/harness):** `beacon_urls()` in
  `bin/conformance/behaviour_compare.py` reads only `EventStream` elements. It
  does not read `<svta:Tracking>`. Because of that, an extra non-linear beacon
  whose URL no expected beacon names is not flagged. Every "MUST NOT fire" half
  of R13.3-1/-2/-3, and R6.5-1's `c1-mid-again`, cannot fail in the battery
  today. Mutations M3, M4 and M5 stayed green. I covered this with
  `beacon_set.py` (an exact multiset check over `--save-raw`), which kills all
  three mutations.

## Files changed

- `reference-player/src/sgai-nonlinear.js` (only file). It gets `trackingOf()`
  (parse), `beacons()` (fire), calls from `advance()`/`advancePause()` and at the
  span end, and the slot anchor at PT (`w.seen`, `w.lateBy`).
  `sgai-reference.js` was not touched: it still carries the harness agent's
  uncommitted edit. No new family file was needed.

## What the code does (readings it takes)

- Parse (§5.5.2): the first-level `svta:Tracking` of each `svta:Ad`, with
  scheme `urn:mpeg:dash:event:callback:2015` and `@value` `1`. Only its
  DASH-namespace `Event` children are read (`vnd:Hint` is not).
  `@presentationTimeOffset` is subtracted, as the tracking table says. The
  events are sorted by time, with document order kept between equal times.
- Fire: a beacon fires when its candidate's presentation (`slotT − start`, or
  wall time on a pause slot) reaches its time. Its limit is the candidate's
  shown duration, so a trimmed candidate never fires past the trim. **A beacon
  exactly at the trim boundary fires**, because the spec says "after a trim
  boundary". When the candidate completes, it fires up to its shown duration.
  At the span's end, it fires up to the time the span ended at. On a dismissal,
  a resume or an abort, nothing more fires.
- Dedup (R6.5, §5.10.2.4): the state is per plan entry, which is one
  presentation of one candidate. A new execution or a pause `repeat` is a new
  presentation. The first of two events that share an `@id` wins.
- **Slot anchoring (a fix found by the re-run).** An overlay that fires on
  the tick that crosses PT now starts its slot timeline at `php − PT`, not
  at 0. §3.1 says an overlay's slot timeline is the timeline of the content.
  Without this, the slot lagged the window by one tick (31 ms in R19.1). A
  candidate whose end coincides with the span's end then lost its `complete`
  beacon: R17.1, R17.2, R19.1 and R40.9-2 were "never". Evidence:
  `slotT 7.965` at "the span ended". The offset is applied only on the crossing
  tick and only up to `MAX_STEP`. A late resolution, a seek, or an execution
  that was gated still starts at 0.

## Per test (final run, `final.out`)

| Test | Before (`baseline-seen-failing.log`) | After | Exact set |
|---|---|---|---|
| R6.4 D4 | beacons FAIL (never) | PASS | OK 2/2 |
| R6.5-1 D4 | beacons FAIL (never) | PASS | OK 4/4 |
| R6.5-2 D1 (linear, List MPD scope) | PASS | PASS | OK 2/2 |
| R13.1 D4 | beacons FAIL | PASS | OK 4/4 |
| R13.3-1 D4 | beacons FAIL | PASS | OK 2/2 |
| R13.3-2 D4 | beacons FAIL | PASS | OK 2/2 |
| R13.3-3 D4 | beacons FAIL | PASS | OK 2/2 |
| R13.6 D3, D4 | beacons FAIL | PASS | OK 2/2 each |
| T08-E1 D4 (edge draft) | beacons FAIL (HEAD ref) | PASS | OK 2/2 |
| T08-E2 D4 (edge draft) | — | PASS | OK 3/3 |

`44 PASS`, exit 0. The re-run of the T-07 tests that failed on beacons gives
`100 PASS, 12 FAIL`, and every remaining FAIL is classified below.

R13.1 timing, worked out by hand from the fixture and compared with the
module log. The window is at 4 s. Candidate 1 lasts 3 s, so candidate 2
starts at 7 s, and its beacons at 0, 2 and 4 s fall at 7, 9 and 11 s.
Observed php: 4.002 (c1 imp), 7.001, 9.001, 11.001. In E1, the trim falls at 6 s
(cap 4 s from 2 s). The `@presentationTimeOffset` 1000 maps PT 1000 to 0, and
the beacon at the trim fired at php 6.001. PT 5300 (4.3 s, past the trim) did
not fire.

Independent source, the primary copy §5.10.2.4: "Whenever an Event with
previously processed combination of values of the @schemeIdUri, @value, and
@id attributes is encountered in course of normal playback, and the
Event@status attribute is absent, the event will be ignored by the DASH
client." The `@id` dedup is that rule, applied with the per-candidate scope of
§5.5.2. Table A.3 gives the callback scheme the dispatch mode `on-start`.

## Remaining FAILs and their classes

| FAIL | Class | One line of evidence |
|---|---|---|
| R17.1 D1, R17.2 D1 selection | test/harness, known: suspension and restore counted as two presentations | "1 presentation(s) more than the vector lists: overlay-lower-third [overlay.xml:#1 option #1]" |
| R40.4-1 D1, D4 selection | test/harness, known (same class) | observed "#1 option #1, #1 option #1" |
| R40.5-1, R40.5-2 D1, D4 selection | test/harness, known: on-top over linear counted as a second presentation | "observed overlay-lower-third [ad list.mpd:ad-1 option null]" |
| R40.9-3 D1 presentation + beacons | test, known: R40.9-3 boundary without a window | linear ad at 7051/7073 vs 6000 ± 250; these are the linear family's callbacks |
| R40.4-2 D1, D4 beacons | **reference, the linear family (not mine)** | `linear:execute` "PRTA 4.001697, APDA 5.998303". At terminate, `fireCallbacks(upTo = min(6, 5.998303))` leaves `complete` at 6 s unfired. The 1.7 ms is the tick's lag, subtracted from the APD |

## Mutation campaign (one break per rule; only the covering tests run)

`mutate.py`, `campaign.out`, and the `final.out` top part.

| Break | Rule | Test | Battery | Exact set |
|---|---|---|---|---|
| M1 time against the window, not the candidate | R13.1 | R13.1 | killed (c2-mid at 7014, not 9000) | — |
| M2 candidate beacons only for option 1 | R13.6 | R13.6 | killed (D4 never) | — |
| M3 trim ignored | R13.3 | R13.3-1 | **survived** | killed (extra at-5s, complete) |
| M4 dismissal fires the rest | R13.3 | R13.3-2 | **survived** | killed (extra at-6s, complete) |
| M5 resume fires the rest | R13.3 | R13.3-3 | **survived** | killed (extra at-6s, complete) |
| M6 no dedup | R6.5 | R6.5-1 | killed (only c1-same-url; c1-mid-again not seen) | killed (both) |
| M7 document-wide @id scope | R6.5 | R6.5-1 | killed (c2-imp never) | — |
| M8 drop events with foreign attributes | R6.4 | R6.4 | killed (never) | — |
| M9 slot not anchored at PT | slot anchor | R19.1 | killed (ov-complete never) | — |
| M6 on E2 | R6.5 without @id | T08-E2 | killed (unexpected b at 7008) | — |

The three survivors are the comparator gap from the Conclusion, not the
reference.

## Edge drafts (`edge-drafts/`, not in `spec-source/`)

The dispatch forbids touching `spec-source/`. These drafts therefore ran with
`--vector` from the snapshot. They are kept here as input for whoever owns
`behaviour/`.

- E1: a beacon exactly at the trim fires, one 300 ms past it does not, and
  `@presentationTimeOffset` is subtracted.
- E2: an empty `Tracking` fires nothing. With no `@id`, the same URL at two
  times fires twice, and at one time fires once.

Out of these, E2 exposed a second comparator bug. An expected beacon
**without `id`** (the schema allows that) that is missing crashes the
comparator, at `behaviour_compare.py:556`, with `KeyError: 'id'`.

## "Standard" list (input for v13)

1. **A beacon exactly at a trim boundary.** §5.5.2 says "Beacons scheduled
   after a trim boundary … are not fired" and "one at the candidate's
   duration fires when it completes". At the boundary itself the text does not
   say, and the reference reads "after" strictly, so the beacon fires. The base
   gives no help: whether an `on-start` event at exactly the end of a Period is
   started is not stated either.
2. **R13.6's option-level half has no carrier.** `svta:RenderableAsset`
   admits no `Tracking` (XSD `RenderableAssetType`), so "a beacon attached to
   an option" cannot be written.
3. **`@id` scope across a seek within one presentation.** §5.10.2.4 re-dispatches
   a processed event "due to a time-shift (seek) operation". §5.5.2 scopes
   `@id` to "one presentation" of the candidate, and does not say whether a seek
   inside an overlay makes a new presentation. The reference does not
   re-fire, because the slot timeline ignores seeks. No test covers it.

## How it ran

The runs used a snapshot (`git archive HEAD bin spec-source reference-player`)
under `~/.cache/cto-tmp/t08a-*/`, with the live `bin/players/node_modules`
linked in and the live `reference-player/src` rsynced in before each run. The
mutations were applied to the snapshot copy only. The command was
`python3 bin/check-dash-conformance.py --behaviour --clock presentation --only
<ids> --concurrency 1`. `final.sh` and `campaign.sh` are the exact sequences.

## Regression sample and the full battery

- Other overlay criteria, because the slot anchor touches every overlay:
  `--only R4.2,R4.9,R4.10,R35.5,R20.1,R34.1,R5.6` gave **106 PASS**, exit 0, wall
  321.6 s. `beacon_set.py` gave 27/27 jobs OK.
- **The full battery did not finish.** At `--concurrency 1` it ran past its
  3500 s `timeout` and was killed with no summary, so no result exists for it.
  The other 50 non-linear vectors not listed here and the linear ones did not
  run against this change. That is T-09's run.

# T-01 — Linear insertion with a module on the pinned dash.js

## Conclusion

**The public API of dash.js 5.3.0 (`dist/`, unmodified) is enough** for
6th-edition `InsertPresentation` and `ReplacePresentation`. ADR 0075 stands;
no fork is needed for what was measured. In all ten runs the main
presentation stopped at PRT (or at PRTA on a delayed join) and came back to
the RT that §5.16 Table 57 gives, within the stated tolerance, with no
dash.js error and no request leaving the local origin except the one noted
below.

What dash.js does **not** do, so the module does it itself:

- **The event payload does not carry the `InsertPresentation` /
  `ReplacePresentation` element.** dash.js's `Event` object has
  `presentationTime`, `duration`, `id`, `calculatedPresentationTime` and
  `messageData` (here `undefined`); the child element is dropped. The module
  reads its attributes from `player.getManifest()`, the parsed manifest
  (`Period[i].EventStream[j].Event[k].InsertPresentation.uri` etc.). That
  object is public (`getManifest(): object`) but its shape is not typed or
  documented: it is the softest dependency of the module. Parsing the MPD
  text independently is the fallback if that shape ever moves.
- **dash.js starts an event once.** `triggeredStartEvent` is never reset on
  seek, so `on(..., {mode: onStart})` would not re-execute after a seek back
  as §5.16.2.2.1 requires. The module subscribes on-receive (the dispatch mode
  §5.16.3/§5.16.4 give both schemes), keeps its own table and queue
  (§5.16.2.2.2) and runs the playhead-triggered processing (§5.16.2.2.5)
  itself, polling `currentTime` every 10 ms plus a one-shot timer just before
  PRT. Measured: `insert-seekback` re-executes, `insert-once`
  (`@executeOnce="true"`) does not.
- **Updates of a Replacement event are not re-dispatched (code read, not
  measured).** `EventController.addInlineEvents` triggers on-receive only for
  an `ADDED` event; an `UPDATED` one (same id, `@status="update"`) replaces the
  object silently. A changed `@maxDuration` / `@returnOffset` / `@clip`
  mid-break (§5.16.2.2.4) therefore needs the module to re-read
  `getManifest()` on manifest reload. Still public API; not exercised here.

Narrowest fork, should any of the above stop holding: a patch to
`EventController` (`addInlineEvents`: also dispatch on `UPDATED`) and to
`DashManifestModel.getEventsForPeriod` (copy the event's child element onto
the `Event` object). Neither is needed today.

## Public API the module relies on

`dashjs.MediaPlayer().create()`, `initialize(view, url, autoPlay, startTime)`,
`updateSettings`, `on(schemeIdUri, cb, scope, {mode})` with
`MediaPlayer.events.EVENT_MODE_ON_RECEIVE` (and `EVENT_MODE_ON_START`, only
recorded), `MediaPlayer.events.STREAM_INITIALIZED` and `ERROR`,
`getManifest()`, `duration()`, `play()`, `pause()`, `seek()`,
`seekToPresentationTime()` (static and dynamic RT; clamps a dynamic one to the
live delay), `reset()`, `isDynamic()`, `clearDefaultUTCTimingSources()`. From
the media element: `currentTime`, `pause()`, `ended`, and the `seeking`,
`seeked`, `playing` events. Two `MediaPlayer`s on two `<video>`s; the
alternative is preloaded (`initialize(..., false)`) between ERT and PRT.

## Measured

`python3 reference-player/spike/run.py --out .project/phases/11-reference-player/tasks/T-01`
(full output: `run.txt`; per-case numbers: `results.json`; page logs:
`raw.json`). dash.js 5.3.0, Chromium 149.0.7827.55 (Playwright 1.61.1),
headless. Content: ffmpeg H.264 + AAC, 2 s segments, from
`bin/conformance/players.py`; main 640×360, alternative 320×180, 6 s
(APD = 6). Every event: `presentationTime=10000`, `duration=5000`,
`timescale=1000` (live: `presentationTime=40000`).

| case | MPD | before: main stops at | expected | after: main resumes at | expected RT |
|---|---|---|---|---|---|
| insert | static | 10.001 | PRT 10 | 10.050 | PRTA 10.001 |
| insert-seekback (1st) | static | 10.001 | 10 | 10.050 | 10.000 |
| insert-seekback (2nd, after seek to 8) | static | 10.002 | 10 | 10.050 | 10.002 |
| insert-once (seek to 8, no 2nd run) | static | 10.005 | 10 | 10.050 | 10.005 |
| replace | static | 10.003 | 10 | 16.001 | PRT + APDA = 16.000 |
| replace `@maxDuration=4000` | static | 10.004 | 10 | 13.997 | PRT + APDA = 13.996 |
| replace `@returnOffset=8000` | static | 10.003 | 10 | 18.001 | PRT + RO = 18.000 |
| replace join at 12, `@maxDuration=6000` | static | 12.000 | join 12 | 14.001 | PRT + APDA = 14.000 (APDadj = 4) |
| replace join at 12, `@maxDuration=6000 @clip=false` | static | 12.007 | join 12 | 18.008 | PRTA + APDA = 18.007 |
| replace | dynamic | 40.001 | 40 | 46.001 | PRT + APDA = 46.000 |

Expected RT is computed by `run.py` from the MPD values and the measured PRTA
(Table 57), not read from the module. Tolerances: stop at PRT within
`0 ≤ PRTA − PRT ≤ 0.10 s` (join: ±0.30 s of the start time); resume within
±0.10 s of RT (dynamic ±0.50 s). Every case: one execution (seekback: two),
alternative played for APDA within 0.02 s, main advanced ~0.96 s in the next
wall second. Switch gaps (pause of main → alternative `playing`): 1–9 ms when
preloaded, 139 ms once when it was not yet ready; return gaps 2–24 ms.

**Static and dynamic.** Insertion was tested static only: §5.16.3 forbids it
in a dynamic MPD. Replacement was tested in both; the dynamic one
(`availabilityStartTime` 30 s before the run, `minimumUpdatePeriod=PT10S`,
`timeShiftBufferDepth=PT60S`) played at the live edge, stopped at 40.001 and
returned to 46.001, inside the time-shift buffer, so no trimming applied. The
trimming of RT to the live edge or TSBS was not exercised.

Observed, not explained: after an insertion main reports `currentTime`
≈ PRTA + 0.049 s at its first `playing`, in every run (no seek is made; the
module only calls `play()`). Inside tolerance; a reference that needs it
tighter can seek to PRTA explicitly.

The dynamic run made one request to `https://time.akamai.com/?iso&ms`
(dash.js's default UTC source; the main player clears it, the alternative's
player does not, and which of the two asked was not established); it was aborted like every off-origin request, and dash.js fell
back to the device clock, which is the clock the content server uses.

## §5.16 sentences relied on (ISO/IEC 23009-1, sixth edition)

- §5.16.1: "Alternative MPD Insertion: The alternative Media Presentation may
  be inserted in the media time of the Main Presentation, i.e. time-shift the
  part of the Main Presentation which is played after the alternative Media
  Presentation."
- §5.16.1: "Alternative MPD Replacement: The alternative Media Presentation
  may replace a portion of the main Media Presentation. In this case, the main
  Media Presentation is not being output, but its media time progresses at the
  same speed as the currently playing alternative Media Presentation."
- Table 57, RT: "In case of an insertion event the value is always PRTA. In
  case of a replacement event, the following holds: — If the
  ReplacePresentation@returnOffset attribute is present and has a value of RO,
  then RT = PRT + RO. — Else if ReplacePresentation@clip is “false”, then RT =
  PRTA + APDA — Else RT = PRT + APDA".
- Table 57, APDadj: "If @clip="true" or absent, APDadj = max(APDmax -PRTA +
  PRT, 0), else APDadj = APDmax." APDA: "For replacement events, APDA =
  min(APD-ASO, APDadj). For insertion events, APDA = min(APD, APDmax)."
- §5.16.5 `@maxDuration`: "If the Alternative Presentation initiated by this
  event has a longer duration than specified in this element, it shall be
  terminated at the end of this duration." "If absent, the value is assumed to
  be infinity".
- §5.16.5 `@executeOnce`: "If true, if some of the media during the active
  interval of this event is played more than once, the event is executed only
  the first time this media time is traversed."
- §5.16.2.2.1: "A seek operation within the current media presentation
  results in shifting the playhead position and thus causes re-execution of
  the event if the playhead position is smaller than or equal to EAP."
- §5.16.3: "The dispatch mode of this event scheme is "on-receive"." and "The
  event shall not appear if the MPD type is "dynamic"." §5.16.4: "This event
  can be used with both static and dynamic MPDs."
- §5.16.2.2.5 NOTE: "there is no playhead-triggered processing during the
  listen mode".

## Finding for the project lead (spec of the base, not of this task)

§5.16.2.2.5 step 1a lists, after the alternative terminates, "Playhead is
moved to RT." then "QE is reset". Read literally, the reset puts back any event
with `PRT ≤ PHP ≤ EAP` and `@executeOnce="false"`: an insertion (RT = PRTA,
always inside its active interval) re-executes at once, forever; so does a
replacement whose RT falls before EAP. This is a reading, not a measurement;
a first run of `replace-join-clip` showed the same effect from a queue
refilled while the alternative was playing (a spike defect, since fixed):
RT = 14 ≤ EAP = 15 re-executed with APDadj = 2 and returned to RT = 12. The
pseudocode of A.14.5 does not reset after termination, only pops the executed
event. The spike follows A.14.5.

## Files

- `reference-player/spike/sgai-linear.js` — the module.
- `reference-player/spike/spike-page.js` — page glue (second `<video>`, log).
- `reference-player/spike/run-spike.mjs` — Playwright driver, same launch
  flags and off-origin policy as `bin/players/run.mjs`.
- `reference-player/spike/run.py` — content, server, cases, expected values;
  imports `bin/conformance/players.py` and adds the `/spike/` prefix in its own
  process only (the `--players` path is unchanged). Exit 0 all OK, 1 a case
  failed, 2 cannot run.

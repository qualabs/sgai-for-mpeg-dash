# UC-14: a dynamic alternative MPD in the linear family

The reference refused an alternative MPD of type `dynamic`
(`linear:failed` "alternative MPD of type dynamic is not played by this
reference"). It now plays one in the second MediaPlayer
(`reference-player/src/sgai-linear.js`).

## The rule (ISO/IEC 23009-1:2026)

- §5.16.2.2.6: "When alternative media presentation is a live presentation, it
  always starts at the live edge, and @startWithOffset attribute shall not be
  present."
- §5.16.4, `@startWithOffset`: "This attribute does not apply to a live
  alternative presentation". So ASO = 0.
- §5.16.4, `@returnOffset` NOTE 1: "the most recent available segment (i.e. the
  live edge)". The start is the most recent available segment.
- Table 57: APD is the "media presentation duration of the alternative media
  presentation defined by the MPD". A dynamic MPD with no
  `@mediaPresentationDuration` sets no end, so APD is infinite. For a replacement,
  APDA = min(APD − ASO, APDadj). For an insertion, APDA = min(APD, APDmax).
- §5.16.5, `@maxDuration`: "If absent, the value is assumed to be infinity, in
  which case the current presentation resumes only when the alternative
  presentation terminates."

## What changed

- `type="dynamic"` is accepted as a single Period. APD is infinite when the MPD
  sets no duration.
- A live Part counts its playhead from where it started (`origin`), not from its
  availabilityStartTime. APDA, RT and the callbacks' reach use that count.
- dash.js `liveDelay` is set to one segment (`MPD@maxSegmentDuration`, else
  `SegmentTemplate@duration`). With `liveDelayFragmentCount`, dash.js fell back
  to 4 × `@minBufferTime` (measured: target delay 8).
- While preloaded, a live Part is sought to its live edge again each time a new
  segment becomes available. At execution it is sought only if it is no longer
  in the most recent available segment. Without this, the paused primary stayed
  on screen for 0.3–0.8 s (E15/E17).
- `readyAhead` skips when RT is infinite. `terminate` uses the observed duration
  (APDE) when APDA is infinite.

## Independent check of the start position

From UC-14 D1 (`--save-raw`), using the harness's `time` answers:

- At execution, the harness's now was 19:46:58.261, so PHPLE was 178.26 s on the
  slate's timeline. dash.js's DVR end was 178.17.
- The slate started at 176.18. That is inside segment [176, 178], the most recent
  available segment at that moment.
- Before the delay fix, the start was 8 s behind PHPLE (148.7 at PHPLE 156.7).

## Remaining UC-14 FAILs and how they are classified

- **Overlay timing (requests[1], selection, presentation, beacons): test,
  harness instrument.** `live_utc_at_load` (bin/conformance/behaviour.py) answers
  "now" as AST + `play_from` + the observation span (90 s here) + the wall time
  since load. The vector's times hold only "on a harness whose wall clock follows
  the channel's" (its own header). So at the crossing the slate's live edge is
  about 150–180 s, and the window [60, 80] s is already in its past.
  This rests on the vector's slate-time reading of N.4/N.7 (an open annex
  finding). With a now equal to the channel's playhead, that reading puts the
  window at the slate's start, minus one segment of live delay.
- **The slate reported as `ad`/`linear` while the vector writes `none`/`[]`:
  standard/spec.** Nothing in the documents tells a Player that a replacement is
  not advertising (context/04 UC-14: "the replacement carries none of them"). The
  observation format has no element for a non-ad alternative. The reference
  marks every alternative as `ad`.
- **legacy: test, legacy-Player instrument** (unchanged: dash.js has no
  alternativeMPD scheme).
- **UC-01 D1 and UC-02 D4 beacons (one run): test, environment** (load average
  11–21 from concurrent batteries). They passed on rerun: 24 PASS,
  `--only UC-01,UC-02 --class D1 --class D4`.

## Not covered by a test

The observation records no position of an alternative, so the start position
cannot be checked by a vector. M5b (no live-edge tracking or seek) and M6
(dash.js's default delay) stay green in E15/E17. They show up only in the module
log: M5b started 4.9 s behind the DVR end and M6 started 8 s behind it, against
about 2 s with the fix. The APDE branch of `terminate` (a live alternative that
ends by itself) has no vector.

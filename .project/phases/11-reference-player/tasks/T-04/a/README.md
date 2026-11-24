# T-04 part A — behaviour tests: linear, cap, ordering, fallback, tracking

## Conclusion

30 tests cover 17 of the 21 criteria of this part. `bin/check-behaviour.py`
reports no finding on any of them (`check-behaviour.out`: the only findings
left in the whole population are the 4 `B-COVER` below), and
`bin/check-scenarios.py` exits 0 (`check-scenarios.out`).

Four criteria have no test, and none was put in `index.yaml`:

| Criterion | Why |
|---|---|
| R4.10 | The test needs a window without `@durationCap`, and S-FIXTURE rejects that fixture by construction: the extension XSD requires the attribute, and the level-2 rule R4.1 fails (`r4-10-probe.out`). The missing piece is a fixture marked as deliberately non-conformant, e.g. `fixtures[].expect_red: [E-3, R4.1]` accepted by S-FIXTURE. Also open: R4.10 forbids presenting, not requesting, so `requests` has no single right value; the test needs "requests not compared" for this outcome. |
| R28.1, R28.2 | Firing the click-tracking is observable, but `beacons[]` requires an `Event@id`, and S-REF resolves it against an `Event` of the fixture. `<svta:ClickThrough>@trackingUris` has neither. Missing: a click entry (e.g. `outcomes.*.clicks: [{at, fixture, candidate, url}]`, checked against `@trackingUris`), plus an observation that the destination was made available (`@uri`). Writing the test anyway would make a conforming Player FAIL: its click-tracking request would show up as an unexpected beacon. |
| R4.5 | No conforming document makes the rendered length exceed the declared one. For video, the declared duration is a `Period@duration`, and DASH renders no further than that. A List MPD reconciles the Linked Period's `@duration` with the imported one by taking the smaller. Image and HTML are shown for exactly `@duration`. A stall or a pause does not count, because the cap accrues on the slot timeline (PLY-31). So "actual > declared" cannot be induced from outside. To the coordinator: decide whether this is an `index.yaml` entry ("not decidable black-box") or a spec finding. |

R13.6 is covered only for its candidate-level sentence. The option-level
half has no carrier in `spec-source/`: `RenderableAssetType` admits no
`<svta:Tracking>`. `v12.7-context-delta.md` row 24 says it was placed, but
no v12.7 candidate exists in `output/`. Today the level-2 rule R13.6a should
fail on it.

## The tests

The rule shared by all of them: what a non-implementing Player does
differently is a difference of at least 0.5 s or a whole element, beyond the
`tolerance`. Without that, the test could not fail.

| Test | Loads | Expects | A Player without the criterion |
|---|---|---|---|
| R1.4 | 2 same-span overlay windows (2 is the fallback); w1 has one 12 s video option whose segments 4–6 answer 404 (delay 3 s) | ad 2–~8 s, then the primary content; w2 never requested; `complete` not fired | stalls on the ad, plays it to 14 s, or falls back to w2 |
| R4.2-1 | overlay, cap 8 s, two 5 s images | c1 2–7 s, c2 7–10 s (stopped mid-ad); c2 `complete` not fired | drops c2 (ends at 7 s) or plays it to 12 s |
| R4.2-2 | Insert `@maxDuration` 6000, List MPD of 2 × 4 s | ad 1 2–6 s, ad 2 6–8 s, back to PRTA | ends at 6 s or at 10 s |
| R4.7-1 | Insert `@maxDuration="0"`, ERT offset 0 | no request, the primary content only | requests the break and may play it |
| R4.7-2 | overlay `@durationCap="0"`, ERT offset 0 | no request, the primary content only | same |
| R4.8 | Insert without `@maxDuration`, alternative 8 s | the whole 8 s, back to PRTA | refuses it, or applies a default cap |
| R4.9 | overlay on timescale 1, cap 11, candidates PT10.2S + PT5S | c1 whole (2–12.2 s), nothing for c2 | without rounding up, c2 shows 0.8–1 s |
| R7.1 | 3 candidates: image 4 s, HTML 2 s, the same image 4 s; D1 and D4 | D1: 1, 2, 3 back to back; D4: c2 skipped, c3 at 6 s | reorders, deduplicates c3, or leaves a gap on D4 |
| R20.1-1 | w1 APS never answers; w2 at 20 s | w2's image at 20–25 s | waits forever or does not fall back (assumes the Player gives up before 18 s) |
| R20.1-2 / -3 / -4 | w1: 404 / 200 with an empty body / OverlayList without Ad | w2's image 2–7 s | shows nothing |
| R20.1-5 | D4, w1 with only an HTML candidate | w1 declined, w2 presents | shows nothing |
| R20.1-6 | w1 404, w2 empty | the primary content, nothing else | stalls or shows a placeholder |
| R20.1-7 | 2 inserts at the same PRT, the first answers 500 | the second event's alternative at 2 s (observed up to 5.5 s) | does not try the second one |
| R20.3-1 | 2 overlay windows with the same PT | w1 presented, w2 never requested | takes w2 |
| R20.3-2 | insert (PRT 4, 1st stream) + replace (PRT 2, 2nd stream), join at 6 s | the replacement plays (APDA 4 s), the insert is not requested | follows document order: plays the insert |
| R20.4 | w1 answered with `family="pause"` (image lower-third, renderable) | w1 declined, w2 presents | shows w1's image |
| R20.5 | w1 (corner, cap 10 s) 404; w2 (lower-third, cap 4 s): one candidate [corner 8 s, lower-third 8 s] | option 2, cut at 4 s | option 1 for 8 s |
| R30.2 | Insert `@executeOnce="true"`; 1st answer an empty List MPD (5.2.3-1), 2nd 4 s; seek to 0 at 4 s | 2nd request at 6 s, ad 6–10 s | counts the empty answer as an execution: no ad |
| R40.3-1 | supersede window 404 + Insert at 6 s | the insert at 6 s | keeps it suppressed |
| R40.3-2 | the same, window answered 404 at 8 s (ERT offset 0, delay 6 s) | the insert executed late at PRTA = 8 s | drops the missed event |
| R6.4 | Tracking, Event and ClickThrough with a foreign namespace | the ad and both beacons, normal | rejects the document or drops the beacons |
| R6.5-1 | c1: same URL + time with @id 3 and 4; @id 2 twice; c1 and c2 both use @id 1 | fire once each; c2's @id 1 fires | document-wide scope or no dedup |
| R6.5-2 | List MPD, both sub-MPDs with @id 1 | ad 2's @id 1 ignored (§5.10.2.4) | applies the per-candidate scope: fires it |
| R13.1 | window at 4 s, c2 starts at 7 s with beacons at 0/2/4 s | 7, 9, 11 s | times them against the window or the Period |
| R13.3-1 / -2 / -3 | trim at 4 s / dismiss at 5 s / pause ad 3–7 s | only the beacons before the end | keeps the schedule |
| R13.6 | candidate [HTML, image] with candidate-level tracking; D3 and D4 | the same beacons with either option | ties the beacons to one option |

Every expected value comes from a sentence of the criterion, quoted in the
outcome's `summary`; what the test assumes and why is in the YAML header.
The fixtures are in `spec-source/behaviour/fixtures/<criterion>/`.

## Seen failing (the check's side)

`mutation-campaign.out` covers 30 tests × 4 breaks: a beacon's URL, a
segment boundary, a candidate reference, and the hash. All 106 breaks
applied were CAUGHT; 0 were NOT CAUGHT. The linear tests' beacon-URL break
did not apply (the regex did not match the quoted URL), and the other
three breaks cover them. In `mutation-fixtures.out`, breaking the entry
document of 19 tests was CAUGHT by S-FIXTURE every time. A wrong expected
time that still tiles, or a wrong option that exists, passes the check: only
the executor can catch that (the table above says against what).

## Checked against the primary copy (sixth edition)

These sentences were checked against the primary copy:

- §5.16.5: "If the value of @maxDuration is zero, the event is …" (R4.7).
- Table 57: "For insertion events, APDA = min(APD, APDmax)." (R4.2-2) and
  "APDadj = max(APDmax -PRTA + PRT, 0)". Worked by hand for R20.3-2:
  APDadj = 8 − 6 + 2 = 4, APDA = min(10 − 0, 4) = 4 s, so at 3 s the
  replacement is still playing.
- §5.16.2.2.6 NOTE 3: "The counter E.c has not been incremented due to the
  failure" (R30.2).
- §5.16.2.2.2: "a priority queue … ordered" by PRT, and §5.16.2.2.5: "from
  oldest PRT to the most recent" (R20.3-2).
- Table 44: "The scope of the @id for each Event is within the same
  @schemeIDURI and @value pair over the duration of the current media
  presentation" (R6.5-2).
- §5.10.2.4: "Whenever an Event with previously processed combination of
  values of the @schemeIdUri, @value, and @id attributes is encountered in
  course of normal playback, and the Event@status attribute is absent, the
  event will be ignored by the DASH client." This sentence supports R6.5-2
  and reading the first event as the one that fires in R6.5-1.

## Assumptions T-03 has to honour

1. Non-linear requests carry `query: {sgai-allowed-layouts}`, as UC-03 does
   with `sends_capabilities: []`. Linear requests and sub-MPD requests carry
   none.
2. R1.4 uses `aps` on media segment URLs: the executor has to route any URL
   it names, not only resolution requests.
3. Beacon counting: R6.5-1 expects a URL that appears twice to fire once,
   so the executor has to count fires, not check membership.
4. `presentation[].start/end` cannot be windows. In R1.4 the moment of the
   abort is the Player's, which is why the test has a 2 s tolerance across
   the whole vector. A `when` in the boundaries would fix that.

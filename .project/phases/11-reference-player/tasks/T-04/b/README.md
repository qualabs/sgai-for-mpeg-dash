# T-04, part B — resolution, request and selection, windows

19 criteria: R2.3, R5.3, R5.6, R5.9, R15.3, R29.2, R29.4, R32.1, R32.2,
R34.1, R34.3, R34.6, R34.9, R34.10, R36.1, R36.5, R38.2, R39.3, R39.5.
18 have tests (26 files); R15.3 has none and no index entry (below).

Every expected value is taken from the criterion's text, quoted in the test's
`summary` or header comment. The fixtures are in
`spec-source/behaviour/fixtures/<criterion>/`, written by `gen.py` (kept here
as provenance). Times are session milliseconds. Classes: an outcome only
where the criterion says something; image-overlay tests use D1, D3, D4
(identical outcomes), request tests D1 (custom supported) and D4 (not).

## The tests

| Test | Loads | Expects | A Player that does not implement the criterion |
|---|---|---|---|
| R2.3 | window admits `overlay-corner`; c1 lower-third only, c2 corner | c2 only, 5-10 s; c1's beacon never | renders c1 (lower-third), fires cr=231 |
| R5.3 | c1 HTML only, c2 image only | D3 both; D4 skips c1, c2 from 5 s, then film; D5 declined | D4 stops at c1 (nothing) or renders HTML; D5 renders something |
| R5.6-1 | one candidate: video, HTML, image | D1/D2 video + sub-MPD fetch; D3 HTML; D4 image; D5 declined | renders option 1 regardless, fetches the sub-MPD on a one-decoder class |
| R5.6-2 | window admits corner (forwarded); option 1 lower-third, 2 corner | option 2 | trusts the APS and renders option 1 |
| R5.6-3 | no allowed layouts; option 1 `custom`, 2 corner; Player supports custom | option 2 (family default excludes custom) | renders option 1 because it supports custom |
| R5.9 | option 1 image answers 404 (`aps`), option 2 image | option 2, 5-10 s | stops (nothing) or shows a broken option 1 |
| R29.2 | 3 windows: layouts + region, layouts only, nothing (offset 0) | queries: both / layouts only / none, at 3, 6, 9 s | sends a region or the family default where none is declared, or omits a declared one |
| R29.4 | URI carries the Publisher's `title`, `device` | Player adds only `sgai-allowed-layouts` | adds an unprefixed parameter (`model=…`): an extra parameter |
| R32.1-1 | pause doc `repeat`, 3 s candidate; pause 2-10 s | 3 passes, 3 impressions, 1 request | one pass then the frame |
| R32.1-2 | `request-again` then (nth 2) a `stop` doc | 2nd request at 5 s, 2nd candidate 5-8 s, frame | no 2nd request; frame from 5 s |
| R32.1-3 | `stop`; pause 2-8 s | one pass, frame 5-8 s, 1 request | repeats or requests again |
| R32.2 | `request-again` then an empty doc that also says `request-again` | exactly 2 requests; frame 5-12 s | keeps requesting (3rd request = extra) |
| R34.1 | pause window `executeOnce="true"`; pauses at 2 s and 9 s | ad at pause 1 only; pause 2 frame only, no beacon, no request | ad again at 9 s with its impression |
| R34.3 | same window; nth 1 empty (validFor 5 s), nth 2 a candidate; 3 pauses | pause 1 nothing; pause 2 ad (window still available); pause 3 nothing | consumes at pause 1: nothing at pause 2; or never consumes: ad at pause 3 |
| R34.6 | overlay 5-10 s, offset 0; doc A usable 2 s, nth 2 doc B; seek back at 12 s to 3 s | 2nd request at 14 s, B 14-19 s with its own impression | no 2nd execution (nothing), or A again without a request |
| R34.9 | overlay 10-30 s, A and B of 10 s; join at 15 s | A from its start 0-10 s, B 10-15 s cut at window end | A 5 s into it (0-5 s), B 5-15 s; or nothing |
| R34.10 | overlay 5-10 s, offset 0; APS answers after 7 s | nothing at any time, no beacon | shows A from 12 s |
| R36.1-1 | offset 3000 on a window at 10 s | request in [7, 10] s | requests at load (0 s) |
| R36.1-2 | offset 0 | request at 10 s | requests early |
| R36.1-3 | no offset, window at 65 s; seek at 2 s to 50 s | no request before 2 s; request in [2, 17] s | requests at load, 65 s ahead |
| R36.5-1 | pause window; doc A usable 20 s, nth 2 doc B; pauses at 2 s and 30 s | 2nd request; B at 30 s | shows A again, no request |
| R36.5-2 | as -1, nth 2 empty | frame at 30 s, A not again | falls back on the expired A |
| R38.2 | layouts declared in a non-canonical order; 2nd window none | value byte for byte; 2nd request no parameter | reorders/normalises, or sends the family default |
| R39.3 | layouts with `custom` + region `60 5 35 30` | both parameters, unchanged, on D1 and D4 | omits the region, or sends it only when it supports custom |
| R39.5-1 | region `50 50 50 50`; opt 1 `45 60 20 20` (left edge out), opt 2 `60 60 40 40` (on the edges), opt 3 corner | D1 opt 2, geometry (60,60,40,40); D4 opt 3 | D1 renders opt 1 at (45,60); D4 renders a custom option |
| R39.5-2 | custom, no region; opt 1 `80 0 20 20` | D1 opt 1 at (80,0,20,20) | requires a region and skips it |

R34.1, R34.9, R36.1 (Publisher) and R34.6 (spec document), R32.1 (APS): only
what binds the Player at runtime is tested.

## Not tested, and why

- **R15.3 — no test, no index entry.** It is a MAY (skip or not, both
  conform), and the only consequence still observable needs a creative whose
  mimeType is not admissible: level 2 rejects that document (R15.2a), and a
  test's fixtures must be green. Tried on a copy of `spec-source/`:
  `S-FIXTURE R15.3.yaml behaviour/fixtures/R15.3/overlay-list.xml is not
  green: R15.2a: @mimeType='image/svg+xml' is not video, image or HTML`.
  Proposed index reason: "a permission (MAY skip); the document that would
  exercise it is not admissible (R15.2a), so no green fixture can carry it".
- **The overlay half of R34.1 and R34.3, and the declared half of R34.9.**
  `svta:OverlayPresentation` has neither `@executeOnce` nor
  `@startWithOffset` in `spec-source/syntax/sgai-extension.xsd` (v12.6);
  they were placed by the v12.7 delta that was never built. UC-21 records
  the same as `missing_carrier`.
- **R32.1 "A document that declares none means stop".** A pause document
  without `@onExhausted` is not green (R32.1a; mutation R32.1-2 below).
- **R5.9 timeouts and network errors.** "no response within a time the
  Player chooses": the presentation time depends on that choice, so no
  expected time can be written.
- **R29.2's capability half.** "Sending a capability parameter is
  OPTIONAL": every choice conforms; the vector fixes `sends_capabilities: []`.

## Schema limits (T-03 owns `schema.json`; not edited)

1. **R29.4**: `query` is exact (T-03's comparer: "exactly the parameters
   `query` lists added") and S-REF admits only slot parameters and
   `sends_capabilities`. There is no way to admit a vendor-prefixed
   parameter (`x-<vendor>-…`), which R29.4 allows, so a conformant Player
   that adds one fails this test. Missing: e.g. an `extra_query_pattern`
   (regex the names of any further added parameter must match).
2. **R5.9**: the schema describes `aps` as answering *resolution* requests;
   the test uses it for a creative URL. T-03's `behaviour.mjs` applies `aps`
   to any URL first, so it works there; the schema's description says less.

## Mutations

`mutate.py` copies `spec-source/` to RAM and applies one break per test,
running `check-behaviour.py --source <copy>`: 39 mutations, output in
`mutations.txt`. 31 structural breaks (a hash, a missing reference, a beacon
URL, a gap in the presentation, an invalid fixture) are each caught by the
expected check. 7 behavioural breaks (a wrong but well-formed expectation:
expect the failed option, the non-admitted candidate, a reordered set, an
early request) stay green: the check judges form, the executor judges
behaviour. One behavioural break (R2.3 expecting candidate 1) was caught
anyway, by S-REF on the beacon URL, which ties the expected candidate to its
own impression.

## Checked against an independent source

- ISO/IEC 23009-1 (the copy `context/00-normative-base.md` declares, sha256
  `a7274eb2…` verified), Table 63, `@earliestResolutionTimeOffset`: *"The
  default is 60 seconds in units of timescale. If the value of this
  attribute is T then the above MPD can be retrieved at any time between
  PRT – T and PRT."* R36.1-1 expects [10 000 − 3 000, 10 000] = [7 000,
  10 000]; R36.1-2 (T = 0) 10 000; R36.1-3 nothing before main 65 000 −
  60 000 = 5 000, reached only by the seek at session 2 000.
- The same copy, Table 58: *"E.c Execution counter (number of times
  alternative MPD playback successfully started)"* — R34.3's consumption at
  rendering start, not at the pause.
- R39.5-1 by hand with §5.3.5's rule: option 1, x = 45 < rx = 50, outside;
  option 2, 60 ≥ 50, 60 ≥ 50, 60 + 40 = 100 ≤ 50 + 50, inside.

## Runs

```
$ python3 bin/check-behaviour.py        # exit 1: 5 uncovered, R15.3 the only one of this part
population 76 (from the level-2 catalogue): 56 with a test, 15 NOT_VERIFIABLE in index.yaml, 5 uncovered; 5 findings
B-COVER	R15.3	no test and no entry in index.yaml
$ python3 bin/check-scenarios.py; echo $?
0
```

No finding names a file of this part.

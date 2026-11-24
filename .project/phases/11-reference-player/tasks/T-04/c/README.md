# T-04 part C — non-linear presentation and coexistence of families

21 criteria, 29 test files, all well formed: `bin/check-behaviour.py` names
none of them uncovered and has no finding on any of these files, and
`bin/check-scenarios.py` exits 0 (`check-behaviour.out`,
`check-scenarios.out`). A mutation campaign broke each test once, in a copy
of `spec-source/`, and the check caught all 29 breaks (`mutation-campaign.out`).
No Player has run any test: every one is `NOT_VERIFIABLE — no executor`
until T-03 exists.

Fixtures are new, short (seconds) and written by `gen-fixtures.py`, which
reproduces every file under `spec-source/behaviour/fixtures/R<n>.<m>/` byte
for byte. Every one is green on levels 1 and 2 (S-FIXTURE). Times are on
the session clock, in ms. Image options are used wherever the criterion
does not need video, so D1 (and D4 or D3 where the class matters) is the
class written.

## The tests

"Instead" is what a Player that does not implement the criterion does, and
so what makes the test fail.

| Test | Loads | Expects | A Player without the criterion instead |
|---|---|---|---|
| R12.5-1 | overlay window 2–22 s; 5 image candidates of 4 s: `overlay`, L-shape upper-left, L-shape upper-right, double box, double box + background | geometry mid-candidate: overlay primary 0,0,100,100; L-UL primary 0,0,77.46,77.46, ad 0,0,100,100; L-UR primary 22.54,0,77.46,77.46, ad full; double box primary 0,25,50,50, ad 50,25,50,50; with background ad layer full frame | draws every token as an overlay over an untransformed primary (primary 0,0,100,100 throughout), or shrinks to another region |
| R12.5-2 | pause window; pause 3 s, resume 6 s; 10 s image `pause-fullscreen` | 3–6 s only the ad, ad 0,0,100,100 | shows the ad as a panel over the paused frame |
| R12.5-3 | same, `pause-partial` | 3–6 s paused frame (primary 0,0,100,100) plus ad | covers the frame with the ad, or moves/scales the frame |
| R12.5-4 | overlay window admitting `linear`; 4 s video takeover | 2–6 s only the ad, 0,0,100,100; primary resumes at 2 s | composites the video over the playing primary |
| R16.1 | pause window; pause 3 s, resume 6 s, 3 s into a 20 s image | ad gone within one frame of the resume (tolerance 17 ms), primary from 3 s | keeps the ad up until its 20 s end, or removes it frames later |
| R17.1 | overlay 2–12 s (10 s lower-third), pause window; pause 5 s, resume 8 s; `pause-partial` | 5–8 s paused frame + pause ad, no lower-third; overlay's 5 s beacon at 10 s | lower-third stays over the paused frame next to the pause ad; overlay slot time runs on (beacon at 7 s) |
| R17.2 | same, `pause-fullscreen` | lower-third back at 8 s with its remaining 7 s, to 15 s; completion at 15 s | overlay not restored after the resume (programme alone from 8 s), or restarted from 0 (completion at 18 s) |
| R17.5 | 10 s insertion at 3 s; `on-top` pause window; pause 6 s, resume 9 s | pause ad 6–9 s; linear ad resumed from its 3rd s, 9–16 s; its 5 s beacon at 11 s, completion at 16 s | no pause ad during a linear ad, or the linear ad runs on under the pause (beacon at 8 s, end at 13 s), or restarts (end at 19 s) |
| R19.1 | rate 2 at 0; 8 s video lower-third at 4 s; 8 s insertion at 20 s | each ad on screen 4 s (2–6 s, 10–14 s), beacons 2 s apart | ads at 1x: overlay 2–10 s, linear 10–18 s |
| R19.3 | rate 2 at 0; window 4–24 s, cap 8 s; two 8 s images A, B | A 2–6 s with its 4 s beacon at 4 s; cap spent by A, B never shown | A on screen 8 s; or the cap counted in wall time, so B shown too |
| R22.1 | window 2–14 s; two 4 s images, lower-third then corner | A alone 2–6 s, B alone 6–10 s | A and B on screen together |
| R25.1 | live, pause window 60–90 s; start at 62 s; pause at 2 s for 10 s; `pause-partial` | frame frozen at 64 s for the whole pause; resume from 64 s | primary advances with the live edge; resumes at 74 s |
| R26.1 | window 2–10 s; double box, then double box + background (images); D1, D3, D4 | geometry: boxes 0,25,50,50 and 50,25,50,50; with background the ad layer full frame and a `background` element | no squeeze, or no background in the bands |
| R26.3 | one candidate: video + background, video, image + background | D1 opt 1, D2 opt 2, D3/D4 opt 3 (no sub-MPD request), D5 declined | D2 takes the background option; D3/D4 take a video option |
| R27.1 | window 2–6 s; 4 s HTML L-shape upper-right; D1, D3 | two elements only: creative 0,0,100,100 underneath, primary 22.54,0,77.46,77.46 on top | creative drawn as a band, primary not shrunk, or a third element |
| R27.3 | one candidate: L-shape video, HTML, image | D1/D2 video, D3 HTML, D4 image, D5 declined | D3/D4 pick the video; D4 picks the HTML |
| R31.2 | pause window cap 2 s; 6 s image; pause 2 s, resume 10 s | ad 2–8 s, all three beacons (2, 5, 8 s) | ad cut at 4 s; beacons at 5 and 8 s missing |
| R35.4-1 | overlay window 2–14 s, dismissible at once; A, B 6 s each; dismiss 4 s | A ends at 4 s, B never shown; only A's imp fires | advances to B at 4 s |
| R35.4-2 | pause doc `request-again`, dismissible; A, B 4 s; pause 2 s, dismiss 3 s, resume 10 s | paused frame alone 3–10 s; one request only | shows B, or requests a new document |
| R35.5 | 8 s video takeover at 2 s, dismissible; dismiss 4 s | programme from 2 s at 4 s | programme from 10 s (skips the slot's region) |
| R37.2 | pause window; pause 3 s, resume 8 s; fullscreen image | programme from 3 s at 8 s | resumes elsewhere (restart, or the slot's end) |
| R40.4-1 | window 2–22 s, no relation, A and B 8 s; 6 s insertion at 6 s | A 2–6, break 6–12, A from its 4th s 12–16, B 16–24; one resolution | A ended at the break and nothing after (the spec's PLY-49), or A restarted / re-resolved |
| R40.4-2 | window 2–8 s, no relation, R 6 s; 6 s replacement at 4 s (returns at 10 s) | R not shown after 10 s; its completion never fires | resumes R after the replacement, outside the window |
| R40.5-1 | 10 s insertion at 4 s; `on-top` window 4–14 s, cap 6 s, 15 s image | image over the linear ad 4–10 s (cap reached on the ad's timeline); linear ad alone 10–14 s | image not over the linear ad; or the cap counted on the programme's frozen timeline, image to 14 s |
| R40.5-2 | 6 s insertion at 4 s; `on-top` window 2–6 s, cap 20 s, 15 s image | image 2–10 s, ends with the linear ad; its 9 s beacon (would be 11 s) not fired | image continues over the programme after the break |
| R40.6 | 10 s insertion at 2 s of an alternative MPD declaring a window at its 2–6 s | image over the alternative 4–8 s (its timeline), beacons at 4 and 8 s | ignores the alternative's window, or times it on the programme's timeline |
| R40.9-1 | window 2–6 s, cap 10 s, 10 s image; pause window 10–14 s (ERTO 0); pauses at 8 s and 13 s | image only 2–6 s; no ad and no request at the 8 s pause; pause ad at 13 s | image runs its 10 s past the range; pause ad outside the window |
| R40.9-2 | `supersede` window 2–12 s; insertion at 6 s (ERTO 0) | image 2–12 s, programme never stops, no List MPD request | executes the break too (stops the programme at 6 s) |
| R40.9-3 | same MPD; APS answers the window with 500 | no overlay; the break executes at 6 s, programme back at 6 s at 12 s | skips the break because the window was declared |

## Mutation campaign

`python3 mutate.py <repo> <workdir>` copies `spec-source/` to the workdir,
applies one break per test (a wrong expected value or a broken fixture) and
runs `bin/check-behaviour.py --source <copy>`. Result: **29/29 caught**, one break per test file. The checks that caught them: S-GEOM, S-LAYOUT, S-FIXTURE
(XSD, level 2: R12.3, R19.3a, R27.1a, R32.1a, R33.4, FIX-2), S-TIME, S-REF,
S-CAPS, S-SCHEMA, B-SCHEMA, B-HASH, B-POP. One caught for a reason other
than the intended one: R40.9-2's pause-family document for an overlay
window is caught by R32.1a (no `@onExhausted`), not by a family/scheme
mismatch rule.

**What the check does not catch, shown:** a wrong value that is still well
formed. R12.5-1's L-shape primary changed from 77.46 x 77.46 to 60 x 60 (the
side reading of "60% of the frame") stays green. Whether a test reads its
criterion correctly is for a person and, later, the executor; this is what
the per-test "instead" column is for.

## Checked by hand

- **Geometry**: sqrt(0.60) x 100 = 77.4597 → width/height 77.46,
  x of the upper-right box 100 − 77.46 = 22.54. Double box 50 x 50 = 25.00%
  of the area.
- **R40.4-2's return point**, against ISO/IEC 23009-1 6th ed. Table 57 as
  quoted in `../../T-01/README.md` ("Else RT = PRT + APDA"; "APDadj =
  max(APDmax − PRTA + PRT, 0)"; "APDA = min(APD-ASO, APDadj)"): PRT = PRTA =
  4 s, APD = APDmax = 6 s, ASO = 0, no `@clip` → APDadj = 6, APDA = 6,
  RT = 10 s, after the window's end at 8 s.

## What could not be expressed, or was not written

- **Per-boundary tolerance** (R16.1): `tolerance` is one per file, so the
  17 ms of "one rendering frame" also binds the pause ad's appearance at
  3 s, which R16.1 does not bound. Missing: a tolerance on a presentation
  boundary or on an action.
- **Position inside an ad** (R17.5, R17.2, R40.4-1): only `primary` has
  `from`; where a suspended ad resumes is decided by its beacons and noted.
  Missing: `from` on `element: ad`.
- **Colour of uncovered bands** (R26.1 "with no background those bands MUST
  render as black"): geometry places rectangles, not content. Missing: a
  field for what fills a region, or a `background` rectangle separate from
  the ad layer's bounding box.
- **`squeezeback-frame`** (R12.5, R27.1): not tested. It is an R12.2 token
  in `context/03` but not in the extension schema (`LayoutTokenType` of
  `sgai-extension.xsd`) nor in spec §3.4.2, so no fixture can carry it.
- **R37.2's live clause** (resume "at the earliest available media
  segment" when the position left the time-shift buffer): not written; the
  expected position depends on the live edge and segment grid the harness
  serves, which one file-wide tolerance cannot bound without loosening the
  rest.
- **R40.9's pause window in a linear ad's own MPD** (R17.5's other path,
  R40.6 for pause): not written; R17.5 takes the `on-top` path.

## Findings, not fixed

1. **Geometry of R12.5's table is ambiguous** ("the upper-left 60% of the
   frame", "the centre-left 25%"): area or side. The tests take area, the
   only reading that fixes the double box's placement; a Player taking side
   fails them. `context/03` R12.5 should say which. [inferred reading]
2. **R40.4 / R40.9 "default" disagree with spec §4.5.8 PLY-49**: context
   resumes the suspended form; the spec ends it and presents nothing further
   in the span. R40.4-1 follows context (as `scenarios/UC-22.yaml` does).
3. **`squeezeback-frame` has no carrier** in the extension schema or the
   spec's token table, though `context/03` R12.2, R12.5 and R27.1 name it.

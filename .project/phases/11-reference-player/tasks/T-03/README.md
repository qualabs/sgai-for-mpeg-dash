> Record of this task as of 2026-11-24: what was run and found then, not the current state. The current state is in the project's live documents (`CLAUDE.md`, `spec-source/behaviour/README.md`) and in the checks themselves.

# T-03 — The harness runs a vector on the `sgai` adapter

## Conclusion

`check-dash-conformance.py --behaviour` runs a vector on the reference
(pinned dash.js 5.3.0 + `reference-player/src/`, still with no ad logic) and
says PASS, FAIL or NOT_VERIFIABLE per expected field. UC-01 in D1 runs end to
end in **89.4 s wall clock** (65.9 s on the first run): content generation
(ffmpeg) took 49.9 s and 28.5 s, and the browser 37.2 s and 36.1 s, for 35 s of
observation. It gives four FAILs (requests, selection, presentation, beacons),
which is right: the skeleton plays the episode from 0 and does nothing else.

The comparator can say PASS, and its FAIL names the field:

| run | what | result |
|---|---|---|
| A | UC-01 D1, real Chromium | 4 FAIL, each against what was observed (`uc01-d1-run.txt`) |
| B | UC-01 D1's expected observation injected as the browser record, `--replay` | 4 PASS (`synthetic-replay.txt`) |
| C | the same record against a copy of UC-01 with beacon `@id 3` moved by hand from 3750 to 4750 | beacons FAIL (`expected at 4750; observed at 3750`), the other three PASS |
| D | real Chromium, a copy of UC-01 whose D1 outcome is what the skeleton does | 4 PASS (`skeleton-vectors-run.txt`) |
| D′ | the same with the primary's `from` changed by hand from 0 to 2000 | presentation FAIL (`primary from expected 2000, observed 4`), the other three PASS |

The `aps` routes (200 after a 2 s delay, 404, no response), the viewer's actions
(pause, resume, seek, dismiss), geometry, concurrency 2 and the `legacy` class
were run in real Chromium too (`aps-route-run.txt`, `actions-run.txt`,
`legacy-run.txt`).

## What was built

- `reference-player/src/profiles.js`: R3.1's table, and the profile of a
  class with a vector's `player_capabilities` laid over it. A capability
  outside the class's row is logged as a problem.
- `reference-player/src/sgai-reference.js`: the skeleton. It plays the
  primary, applies the actions and offers a hook for the families. Its header
  is **the observation contract**: the viewport's `data-sgai-layout`, a
  `data-sgai-element` on each surface with its doc, candidate, option and
  opportunity, and *covered surfaces must be hidden* (the harness does not
  compute occlusion).
- `bin/players/adapters/sgai.js`: the adapter, with `mode: 'legacy'` for the
  same dash.js without the module. It samples the DOM every 25 ms and keeps a
  sample on change, on each event of the primary `<video>`, and every 500 ms.
  It has no say in what the module claims beyond the identity attributes.
- `bin/players/behaviour.mjs`: the runner. It serves the fixtures at their
  URLs, applies `aps` (status, document, delay, no response, `nth`), maps the
  external media URLs onto the local content server, answers 204 to anything
  else and records it, drives the actions at session times (`activate` is a
  real click on the ad), and runs jobs concurrently.
- `bin/conformance/behaviour.py`: selection, content, server and replay. It
  reuses players.py with two settings scoped to its own process: CONTENT_S =
  60, so that 3 s segments divide it, and `/reference/`.
- `bin/conformance/behaviour_compare.py`: the comparison. Its docstrings say
  what each field compares.
- `bin/check-dash-conformance.py --behaviour`: the only entry point. It
  accepts `--only UC-NN|R<n>.<m>`, `--class`, `--vector`, `--concurrency`,
  `--out-json`, `--save-raw` and `--replay`, rejects every option of the
  other modes (64), and exits 2 when a job cannot run.
- `bin/test_behaviour_compare.py`: 51 tests on synthetic observations, no
  Chromium.

## Verification

- **Tests**: 51, OK. They cover the edges: exactly at the tolerance and one
  unit past it (request, beacon, boundary, `from`, geometry edge), empty
  expected and empty observed, a harness failure, a missing `.http`, nothing
  ever shown, and a different timescale.
- **Mutation campaign** (`mutate.py`, `mutation-campaign.out`): 40 breaks, one
  per rule, each run only against the tests that cover it. The baseline (44
  covering tests, unmutated) is OK, and **40 of 40 go red**. Two had stayed
  green in a first pass, so two tests were added: an option where a linear
  candidate was expected, and `declined` with a non-empty `presented`. The
  campaign runs with `-B` and deletes the `.pyc` files first, because a
  restored source can be shadowed by a stale bytecode of the same size and
  second.
- **Independent check by hand** (from `uc01-d1.raw.json` with jq): the last
  sample before 25000 is t=24626 at media 23912, so 23912 + 374 = 24286. That
  is the "observed 24286" in run A's presentation detail, and the next sample
  (t=25126 at 24412) agrees with it.
- **Whole bin suite** (`suite.out`): everything OK except
  `test_check_behaviour.py` (9 failures). Its as-it-is tests read the live
  `spec-source/behaviour/`, which the concurrent T-04 workers are filling (it
  counts 3 uncovered criteria and 20 index entries, where the tests expect 61
  and 76). This task did not touch that check or that tree.
  `test_conformance_players.py` (the legacy path, which uses the edited
  `harness.html`) passes: 6 tests OK.
- **ADR 0087**: searching for `--behaviour`, `behaviour.mjs`, an import of
  `conformance.behaviour` and `behaviour.run(`/`behaviour.main(` across
  `*.py`, `*.prompt`, `*.mjs`, `*.js` and `*.sh` (excluding `node_modules` and
  `.project/`) finds only this task's own files and the entry point in
  `check-dash-conformance.py`. Finding that entry point is what shows the
  search works. `test_behaviour_compare.py` imports `conformance.behaviour`
  only for `fixtures_of`, and calls neither `run` nor `drive`.

## Semantics worth knowing (decided here, written in the code)

- The session clock starts at the adapter's `load()`, as the schema puts it
  ("since the Player was told to start playback"). The stretch before the
  first frame is startup: the first segment is taken to start at 0, and the
  startup is reported.
- The main MPD's own requests are not compared: the Player is given that
  document, it does not request it.
- Presentation: every observed change must be a boundary the vector writes,
  within tolerance. A written boundary that nothing observable crosses (same
  surfaces, and a primary playing on at the rate the actions set) is optional.
  A change shorter than the tolerance is a transition and is folded. Across an
  optional boundary, `from` is read from the samples.
- Geometry: the ad's box is the bounding box of the `ad` surfaces, with no
  `background`. A rectangle is the element's box, not the picture inside it
  (`object-fit: contain`). Any state within ±tolerance of `at` may satisfy it.
- Beacons: an observed request is a beacon if some fixture declares its URL,
  or an expected beacon has it.
- `matches` compares the request URL only (host, path and query), not the
  other headers.
- `audio` is NOT_VERIFIABLE: nothing measures what is heard.

## Findings (not fixed)

1. **Startup is longer than UC-01's tolerance.** The time from `load()` to
   the first frame was 227, 565, 398, 431, 425, 471, 423 and 444 ms across
   the runs; UC-01's tolerance is 250. Anything a vector places at session 0
   (UC-01's `imp`/`start` beacons, the requests at 0) will fail on startup
   alone. The scenarios README says "since playback was started" and the
   schema "since the Player was told to start playback": which of the two
   holds is for the project lead. This harness follows the schema.
2. **Content generation dominates a short run** (28–50 s of ffmpeg for one
   vector: 60 s masters at 1280×720 and 1920×1080). T-09 can cache the
   masters across runs; within a run they are already shared across vectors.
3. `test_check_behaviour.py`'s as-it-is tests fail while T-04 is writing
   `spec-source/behaviour/` (see Verification).
4. For T-05..T-08: selection needs the `data-sgai-opportunity-*`
   annotations, and an ad surface without them is a FAIL. A linear ad must
   hide the primary `<video>`. Squeezeback geometry must size the elements
   themselves.
5. Not exercised in real Chromium: an `aps` entry with `nth`, a request
   with an added query, and a beacon actually fired. The skeleton makes none
   of these. The unit tests cover the comparison; the route's `nth` was only
   read, not run.

`spec-source/scenarios/schema.json` was not changed.

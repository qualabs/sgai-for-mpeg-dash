# Live "now": the channel's wall clock follows what is presented

**Defect.** `live_utc_at_load` set a live entry's `now` at load() to
AST + `play_from` + the observation span at the fastest rate (90 s in UC-14),
so a window another live timeline places at a wall time was already past
(UC-14: the slate joined at ≈150 s, its overlay window is 60–80 s).

**Why the span was there** (1924c84, docstring and the scenarios README):
"so that a viewer watching faster than real time stays behind the edge". It
also, silently, gave dash.js the headroom it needs to start at `play_from`:
dash.js starts a dynamic MPD at `min(edge − liveDelay, startTime)`
(`_getInitialStartTimeForDynamicStream`), liveDelay = 4 × segment duration
when the MPD suggests none (`computeAndSetLiveDelay`) — 8 s here. So `now` =
AST + `play_from` alone would start every live vector 8 s early (R25.1's pause
would fall before its window). And the content server does not decide
availability: dash.js requests no segment its own clock says is not available.

**Fix.** `now` at load = AST + `play_from` + the Player's live delay
(`player_live_delay`, dash.js's order: @suggestedPresentationDelay > 0, else 4 ×
the longest segment duration, else 4 × @minBufferTime) + `(rate − 1) ×
observation` (0 at 1x), then a running clock.

## Files

- `mutate.py` / `mutation-campaign.out`: 9 breaks, 9 caught.
- `before.out`, `after.out` (summaries); `before-behaviour.log`,
  `after-behaviour.log` (full logs; the `.out` files point at their temp
  copies, removed).
- `uc02-d1-after.out`, `uc02-d1-after-ready-ahead.txt`: the time host answers
  18:09:38.064 at load + 64 ms (= 18:00 + 570 s + 8 s, by hand), and the
  reference's `linear:ready-ahead` seeks the primary to RT 630 at load + 52 s,
  when the live edge is 630.1 and dash.js clamps it to 622.
- `reference-src-{before,after}.sha256`: the reference was the same in both runs.
- `suite.out`: the whole `bin/test_*.py`, 29 files OK.

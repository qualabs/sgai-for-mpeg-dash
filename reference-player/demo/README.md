# Demo: one session with linear, overlay and pause (ADR 0086)

A page served locally plays, with the reference (dash.js 5.3.0 plus
`reference-player/src/`, class D1), one session with a linear break, an overlay
over it and a pause ad; Playwright records it; then the run asserts, from the
reference's own observation of the page's DOM (never from pixels), that the
three families happened in that order at their times.

```bash
python3 reference-player/demo/demo.py
```

From the project root. It starts the behaviour battery's local content server
(`bin/conformance/players.py`, with `bin/conformance/behaviour.py`'s settings),
opens the battery's harness page in Chromium, makes the viewer's pause and
resume at their session times, records the page to
`.project/phases/11-reference-player/tasks/T-11/demo-session.webm` (640x384,
about 70 s, about 8 MB), and stops the browser and the server it started.

It prints one `PASS` line, or one `FAIL` line per failed check, and where the
recording and the full log (every observed segment) are. Exit `0` PASS, `1`
FAIL, `2` cannot tell, `64` wrong command line.

| Option | |
|---|---|
| `--out FILE` | where the recording goes (the log beside it, `.log`) |
| `--drop ACTION` | removes the viewer actions `ACTION` (`pause`, `resume`) from the session: the way to see the check fail |
| `--headed` | shows the browser while it records |

Needs what the battery needs: `node`, `ffmpeg`, the Chromium of
`bin/players` (`SETUP.md`); PyYAML and lxml are fetched with `uv` when missing.

## The session

`session.yaml`. No UC vector presents all three in one session, so it is
UC-04's (Annex D: the 30 s linear break at 600 s with the video lower-third
over its first 10 s) with a pause window added to its main MPD
(`fixtures/main.mpd`, D.2-1 plus the `PauseAdPresentation` of H.2-1) and
answered by Annex H's pause document (H.5-1, its video sub-MPD H.6-2). The
file says why and what is asserted.

Not part of any battery, build or promotion (ADR 0087).

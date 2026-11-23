---
id: "0051"
title: Legacy-Player tests run pinned dash.js and Shaka behind one adapter per Player
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0051: Legacy-Player tests run pinned dash.js and Shaka behind one adapter per Player

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

Level 3a checks that a Player that does not implement the extension ignores it
and keeps playing (`context/07` §5, UC-07). Measured 2026-11-23: dash.js
v5.3.0 lists "Server Guided Ad Insertion — Not supported" and implements
neither the 6th-edition linear SGAI nor our extension; Shaka v5.3.6 recognises
`urn:mpeg:dash:event:alternativeMPD:insert:2025` and `…:replace:2025` and reads
`InsertPresentation`/`ReplacePresentation`, but not our non-linear extension.
No Player implements the extension today.

## Decision

- Each spec MPD, with its media URLs rewritten to local test content, is loaded
  in unmodified dash.js v5.3.0 and in Shaka v5.3.6, in headless Chromium
  (Playwright). Measured: main content starts, advances a defined stretch, no
  fatal error; events of our schemes are ignored. In Shaka, also that a
  6th-edition `InsertPresentation` is recognised.
- Test content is generated with `ffmpeg` in `isoff-live` profile and served by
  a local server the task starts and stops by PID. No external CDN.
- Player versions are pinned.
- Ad MPDs (List MPD, SPS sub-MPD) are loaded only in their role; a legacy
  Player never requests them, so they are not given as the main manifest.
- The harness has one adapter per Player (load, wait for a state, read events,
  network requests and what is on screen).

## Consequences

- A test that depended on a third party would fail because of the third party;
  a moving Player would give verdicts that do not compare across runs.
- The reference Player of ADR 0052 enters as one more adapter, not a new
  harness.

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-7, and measurement 3.

---
id: "0075"
title: The reference Player is the pinned dash.js, untouched, plus a module of ours
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0075: The reference Player is the pinned dash.js, untouched, plus a module of ours

## Context

Phase 09 (D-8) said the reference is another build of the pinned dash.js plus our code. dash.js 5.3.0 exposes `on(schemeIdUri)` with receive/start modes, request/response interceptors and `extend()`; its npm package ships only `dist/`.

## Decision

The reference is `dist/` of dash.js 5.3.0 as pinned in `bin/players/package.json`, unmodified, plus a module that uses only the public API. Linear insertion runs in a second `MediaPlayer` on a second `<video>`. A fork of the dash.js source enters only for what the public API cannot reach, as shown by T-01. No upstream PR in this phase.

## Consequences

- The legacy Player and the base of the reference are the same file, so a behavioural difference is never a build difference.
- Squeezeback scales the `<video>` by CSS; the switch between two `<video>` elements has a gap of milliseconds, which a behaviour reference does not measure.
- Approved by the project lead on 2026-11-23.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-1.

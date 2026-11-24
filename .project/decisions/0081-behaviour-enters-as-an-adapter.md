---
id: "0081"
title: The reference enters the Player harness as one more adapter, run with `--behaviour`
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0081: The reference enters the Player harness as one more adapter, run with `--behaviour`

## Context

Phase 09 (D-7) wrote the harness with one adapter per Player so the reference would enter as one more.

## Decision

`bin/players/adapters/sgai.js` is the dash.js adapter plus the module; it also reports resolution requests, beacons, presentation segments with session times and the ad layer's geometry. The JS measures and Python compares, as `players.py` does. `check-dash-conformance.py --behaviour` runs the criterion tests and the UC vectors, with exits 0/1/2/64.

## Consequences

- The battery is long (5.35 h serial for the UC vectors alone): concurrency and short content where the vector allows; T-09 measures it.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-7.

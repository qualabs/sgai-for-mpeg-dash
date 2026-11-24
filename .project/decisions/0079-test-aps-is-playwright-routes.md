---
id: "0079"
title: The test APS and the beacons are Playwright routes, not a server
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0079: The test APS and the beacons are Playwright routes, not a server

## Context

`bin/players/run.mjs` already intercepts every request leaving the page.

## Decision

The APS is a `page.route` on the resolution URL that answers what the test's `aps` field declares (document, delay, status, nothing) and records each request with its parameters and session time. Beacons are routes that answer 204 and record URL and time. Media stays on the local server of `bin/conformance/players.py`.

## Consequences

- No new process to start and stop.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-5.

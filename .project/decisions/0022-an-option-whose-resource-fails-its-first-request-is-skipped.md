---
id: "0022"
title: An option whose resource fails its first request is skipped, not its candidate
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0022: An option whose resource fails its first request is skipped, not its candidate

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R5.6 walked a candidate's options against device capability and the slot's
layouts only. A resource that did not load fell under R1.4 — *"the Player MUST
abort that ad"* — and the Player went to the next candidate. A dead asset in
option 1 therefore lost the whole candidate even when option 2 would have
rendered, which DP-3 does not admit: *"an opportunity is given up only after
every way of filling it that the manifest declares has been tried"*.

SVTA2053 v3 (David Hassoun, 2026-10-22/23, ADR 0106 of his demo) states the
fix: *"Only the first request for an asset governs this"*.

## Decision

- **R5.9.** The first request for each resource an option references decides
  whether the option is satisfiable. A failed first request — a final status
  outside 2xx, a network error, or no response within a time the Player chooses
  — makes the option not satisfiable, and the Player moves to the next option,
  as R5.6 does for a failed check. A failure after the option began rendering is
  a runtime failure under R1.4. No timeout value is fixed.
- **R5.7** names R5.9 beside R5.6, and **R1.4** is limited to failures after
  rendering began, plus a malformed candidate.
- **R42.1** gains one occurrence: no option of the candidate renders and at
  least one failed its first request. Only then does the candidate's failure
  beacon fire; when another option renders nothing fires, as R13.6 already
  forbids firing the beacons of an option not rendered.

## Consequences

- A candidate is lost only when none of its options can be shown.
- The ADS learns of a dead creative when it cost an ad, and not when failover
  hid it.
- How a Player learns that a resource loads (`preValidateAssets`, `HEAD`) stays
  its own: R5.9 fixes the outcome, not the method.
- Residual: the Player may wait for the first request before showing an
  option; it can resolve and preload early (R36).

## Links

- `context/03-requirements.md` — R1.4, R5.6, R5.7, R5.9, R42.1.
- `context/04-use-cases.md` — UC-09.
- `output-analysis/2026-10-27-david-v3-vs-context.md`, row 7.

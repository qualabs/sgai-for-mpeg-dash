---
id: "0087"
title: The behaviour battery is opt-in: nothing runs it by default
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0087: The behaviour battery is opt-in: nothing runs it by default

## Context

The project lead, approving the design: "Ok, construyamos pero que por defecto no se use porque es muy caro en tiempo".

## Decision

The battery runs only with an explicit `--behaviour`. `build-all`, the incremental, `promote.py`, the `bin/test_*.py` suite and `check-dash-conformance.py` without the flag do not invoke it. A test in `bin/` fails if any default path calls the battery's executor.

## Consequences

- Tests of the battery's parts (the check, the comparison) run on data, without Chromium.
- ADR 0082 has nothing to gate: promotion does not see the battery.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-13.

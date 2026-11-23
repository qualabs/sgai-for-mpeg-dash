---
id: "0057"
title: Promotion requires the conformance tests green, and the audit stops blocking
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0057: Promotion requires the conformance tests green, and the audit stops blocking

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

The promotion criterion (the project lead, 2026-09-27) was
`check-promotable` exiting `0` and the comparison verdict `BETTER THAN
PUBLISHED`. With the conformance tests, code gives the conformance verdict and
the LLM audit becomes a source of suspicions (ADR 0053). Headless Players may
vary between runs.

## Decision

Decided by the project lead on 2026-11-23:

- A third promotion condition is added: `check-dash-conformance` exits `0` on
  the candidate.
- A code `FAIL` blocks through the pipeline route. A `NOT_VERIFIABLE` does not
  block and is listed with its count.
- The LLM audit rows stop blocking; a suspicion of the audit blocks only when
  it is a rule that fails.
- The Players inform and do not block until their runs are stable.
- T-09 writes this into `CLAUDE.md` and into `check-promotable`.

## Consequences

- What can stop a promotion on conformance grounds is a deterministic check,
  not an LLM's reading.
- Player results are reported but carry no weight on promotion yet.

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-13.

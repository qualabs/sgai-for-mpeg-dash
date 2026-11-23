---
id: "0056"
title: The demo is one command, and a report showing the quote and the place
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0056: The demo is one command, and a report showing the quote and the place

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

The project lead: *"hacer una demo con tests REALES que un código falle y no
sea un LLM diciendo algo está bien o mal es muy distinto"*. The tests have to
be demonstrable: one command that runs everything and exits with a code, and
negative cases that the code rejects with the citation and the location.

## Decision

- `bin/check-dash-conformance.py` with only the candidate as argument runs all
  the code of levels 1 and 2 (E-1 to E-4, the XSD, both rule families, the
  DASH-IF tool; level 3 with `--players`) and exits with its code.
- With `--demo` it also runs the positives and negatives of ADR 0054 and shows
  them side by side: each negative with what was broken, the rule that caught
  it, the quoted sentence and the XPath.

## Consequences

- The same command gives the same result every time, and shows a broken
  document rejected by code with the reason. T-10 runs it twice and checks the
  output is byte-identical.

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-12.

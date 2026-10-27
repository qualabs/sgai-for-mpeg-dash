---
id: "0041"
title: The carrier of time-bound beacons is a MUST
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0041: The carrier of time-bound beacons is a MUST

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R6.2 states the carrier of time-bound beacons as SHOULD and R13.1 as MUST,
and merging R6.2 into R13.1 forces one.

## Decision

MUST, which is what R13.1 and R13.4 (*"mandatory"*) already say. R6.3 remains
the way out for what the callback cannot express. Decided by Nicolás Levy,
2026-10-27.

## Consequences

- It is the only change of strength in the restructure, and the validation
  accepts it only at R13.1 (ADR 0038).

## Links

- DESIGN.md D-14; `context/03-requirements.md` — R6, R13.

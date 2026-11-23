---
id: "0058"
title: The issue to DASH-IF carries the running tool's measurement and needs explicit OK
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0058: The issue to DASH-IF carries the running tool's measurement and needs explicit OK

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

The DASH-IF conformance tool validates against the 5th edition: its XSD
module rejects 8 of ISO's own 41 6th-edition examples (measured 2026-11-23
against the tool's `DASH5th.xsd`). DASH-IF should know. Posting an issue is an
action towards a third party.

## Decision

- DASH-IF is told with an issue in `Dash-Industry-Forum/DASH-IF-Conformance`.
- The evidence is T-08's, with the tool running on ISO's 41 examples, and not
  only its XSD.
- T-08 leaves the draft issue in its evidence. It is not published without the
  explicit OK of the project lead, who decides at that moment who sends it.

## Consequences

- Publishing the issue is outside what the phase does on its own.

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-14, and measurement 2.

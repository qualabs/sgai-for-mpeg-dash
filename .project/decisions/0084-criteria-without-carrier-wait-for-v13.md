---
id: "0084"
title: Criteria whose carrier is not yet in the specification wait for v13
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0084: Criteria whose carrier is not yet in the specification wait for v13

## Context

R41.4–R41.7, R42.3, R47.2 and R48.3 are observable, but `spec-source/` declares no carrier for them (`output-analysis/v12.7-context-delta.md`, Not placed).

## Decision

They are `NOT_VERIFIABLE — no carrier`, with their hash. v13 chooses the carriers and turns them into tests.

## Consequences

- The reference does not decide the HOW of v13.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-10.

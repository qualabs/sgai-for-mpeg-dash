---
id: "0085"
title: Each family's tests are written before its code and seen failing
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0085: Each family's tests are written before its code and seen failing

## Context

The same agent writes the reference and its tests.

## Decision

The tests of a family are written from the criterion's text before the family's code, and each is seen failing against the reference without that family.

## Consequences

- A test that never failed is not known to measure anything.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-11.

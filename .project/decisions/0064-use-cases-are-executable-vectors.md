---
id: "0064"
title: The use cases are executable vectors, run by reference-player
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0064: The use cases are executable vectors, run by reference-player

## Context

`context/04` states each use case's expected behaviour per device class in prose; nothing can execute it.

## Decision

Each UC becomes `spec-source/scenarios/UC-NN.yaml`: its fixtures, the Player capabilities per class, and per class D1–D5 the observable outcome (requests, chosen candidate and option, layout, presentation segments with times, beacons), with the hash of the UC's text. Code checks coverage UC × class, schema, fixtures green, hash current. The executor is reference-player; until then the vectors are `NOT_VERIFIABLE — no executor`.

## Consequences

- reference-player's behaviour tests exist before it does.
- A change to a UC in v13 surfaces as a list of stale vectors.
- Discarded: a Python model of the Player's decisions in this phase (a second implementation beside the dash.js reference).

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-5.

---
id: "0078"
title: The behaviour population is read from the level-2 catalogue, with its hash
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0078: The behaviour population is read from the level-2 catalogue, with its hash

## Context

The level-2 catalogue sends 76 criteria to level 3; 61 are observable from outside, 7 lack a carrier until v13, 8 are not decidable by a black-box test.

## Decision

The population is read by code from `bin/conformance/spec/catalog.py`. Every criterion has at least one test or an entry in `spec-source/behaviour/index.yaml` with `NOT_VERIFIABLE` and its reason. The hashed text is the one `criteria.py` defines, imported, not rewritten. A changed or retired criterion gives exit 2 with the tests to review.

## Consequences

- Levels 2 and 3b cannot read a criterion differently.
- What v13 moves arrives as a list.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-4.

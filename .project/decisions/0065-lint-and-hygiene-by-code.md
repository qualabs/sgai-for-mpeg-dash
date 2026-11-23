---
id: "0065"
title: Editorial lint and dist hygiene are code
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0065: Editorial lint and dist hygiene are code

## Context

`review-spec-details` checked cross-references, namespaces and drafting markers by reading. `dist/` holds 38 `<!-- refine -->` comments, 20 inline comments and a "Refinement gaps" section.

## Decision

`bin/lint-spec.py` checks the assembled document: unprefixed `§n` resolves, ids defined once and referenced only when defined, XML prefixes declared, no TODO/TBD/FIXME/XXX, no HTML comment, no "Refinement gaps". Exits 0/1/2/64.

## Consequences

- It is a promotion condition (ADR 0073).
- Today `dist/` fails on exactly the comments and the gaps section.

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-6.

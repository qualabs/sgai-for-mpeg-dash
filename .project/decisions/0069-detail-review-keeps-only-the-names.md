---
id: "0069"
title: Detail review keeps only the naming judgements, over a list code builds
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0069: Detail review keeps only the naming judgements, over a list code builds

## Context

Six of `review-spec-details`'s eight categories are mechanical (format, cross-references, annex vs chapter, editorial regression, namespaces, drafting markers).

## Decision

Those six are covered by `lint-spec.py`, the fixtures and the generated tables. The two naming categories stay with an LLM, over a list `bin/name-candidates.py` builds: the names of `spec-source/syntax` equal or close to one in the 6th-edition XSD. No in-place autofix; a fix is a patch.

## Consequences

- The review reads a list, not the spec.

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-10.

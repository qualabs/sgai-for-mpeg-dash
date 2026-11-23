---
id: "0067"
title: A major build edits the source; the prose is no longer rewritten from scratch
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0067: A major build edits the source; the prose is no longer rewritten from scratch

## Context

A major regenerated the whole document. `apply-context-delta` alone was 60% of the measured incremental (25.2M of 41.8M input tokens), rereading the whole spec on 88 calls.

## Decision

A major is a delta on `spec-source/` with no changed-fraction cap, allowed to add or retire constructs and sections. The order is always: artefacts (XSD, `syntax.yaml`, fixtures, vectors) in a loop with code until levels 1 and 2 are green; then the prose by section and by patch; then assemble and check. `build-spec.prompt` is retired.

## Consequences

- What a major means changes in the project's `CLAUDE.md`.
- The safeguard against incoherence accumulated by patches is the full-document open search, once per major (ADR 0068).

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-8.

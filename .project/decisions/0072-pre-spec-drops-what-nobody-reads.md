---
id: "0072"
title: The pre-spec drops what nobody reads, and skips by hash
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0072: The pre-spec drops what nobody reads, and skips by hash

## Context

`extract-conformance-assertions` and `build-uc-coverage-matrix` cost 5.5M of the 41.8M input tokens of the measured incremental, and no step reads their output. The other pre-spec steps skip by mtime, so a `touch` reruns them and an mtime-preserving edit does not.

## Decision

Both steps are retired (coverage of the UCs comes from the vectors, ADR 0064; the assertions from levels 1 and 2). The remaining three skip by the hash of their inputs, recorded beside their output.

## Consequences

- `context-analysis/` keeps the two files as a record, no longer regenerated.

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-13.

---
id: "0070"
title: The comparison against what is published is code
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0070: The comparison against what is published is code

## Context

`compare-spec-versions` (an LLM) subtracted 17 requirements from 207 criteria on v12.6 and counted that delta into `BETTER THAN PUBLISHED`.

## Decision

`bin/compare-candidates.py` reads the summaries of the candidate and of `dist/`, writes the table and the verdict, and exits 2 when the populations differ. `BETTER THAN PUBLISHED` means no blocking category rises and no unit `met` in `dist/` falls. The prompt is retired.

## Consequences

- The case that went wrong is the script's negative.

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-11.

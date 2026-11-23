---
id: "0068"
title: Validation rests on a code-checked trace, and an LLM judges per criterion
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0068: Validation rests on a code-checked trace, and an LLM judges per criterion

## Context

`validate-spec` reads the whole spec and writes a coverage map whose quotations nobody else checks: 28 of 364 quoted segments in v12.6's map are not literal.

## Decision

The build writes `output-analysis/v<N>-trace.json`: for each unit of `check-promotable.py --population`, the sections that fulfil it and their quotations, without line numbers. `bin/check-trace.py` checks every unit has a trace, the sections exist and each quotation is literal within its section. The verdict comes from code when a level 1 or 2 rule decides, from the vector for Player behaviour, and otherwise from an LLM reading only the criterion and its sections. The open search (gaps, edge cases, ambiguities) reads the whole spec once per major or incremental and only changed sections in a refine. Each analysis leaves a machine summary (`summary.json`).

## Consequences

- The LLM's context per judgement is small and parallel.
- Scripts read summaries, never prose.

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-9.

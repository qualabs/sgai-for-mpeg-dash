---
id: "0071"
title: The LLM audit leaves the refine loop
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0071: The LLM audit leaves the refine loop

## Context

Since phase 09 the audit only raises suspicions; on `dist/`, 17 of 37 were confirmed by code, 10 partly, 10 had no code evidence, none was contradicted.

## Decision

The audit runs once per major or incremental, over the constructs new or changed, and every confirmed suspicion becomes a code rule. It does not run in a refine round.

## Consequences

- A refine round costs refine, scoped validation and code.

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-12.

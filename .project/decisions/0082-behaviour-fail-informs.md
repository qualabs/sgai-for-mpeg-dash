---
id: "0082"
title: A behaviour FAIL informs and does not block promotion
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0082: A behaviour FAIL informs and does not block promotion

## Context

ADR 0057: Players inform and do not block. A FAIL may be a defect of the reference or a gap of the specification.

## Decision

A FAIL informs. The battery report classifies every FAIL as reference or specification.

## Consequences

- Promotion is not tied to a prototype's quality.
- Approved by the project lead on 2026-11-23.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-8.

---
id: "0077"
title: A behaviour test is a vector with the UC vectors' schema
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0077: A behaviour test is a vector with the UC vectors' schema

## Context

Phase 10 left the use cases as vectors (`spec-source/scenarios/`, ADR 0064) with fixtures and what is observable per device class. The criteria of the Player need tests too, and the UC vectors do not reach edge criteria (R4.9 appears in no UC).

## Decision

Each behaviour test is `spec-source/behaviour/R<n>.<m>[-<k>].yaml`, valid against the scenarios schema extended with optional fields: `criterion` and `criterion_sha256` in place of `uc` / `uc_sha256`, `aps` (how the test APS answers), `actions` (what the viewer does and when) and `geometry` (where the ad layer and the primary content sit).

## Consequences

- One executor, one schema and one check for both kinds of vector.
- Rejected: a Python catalogue like level 2, which would tie data any Player could run to our harness.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-3.

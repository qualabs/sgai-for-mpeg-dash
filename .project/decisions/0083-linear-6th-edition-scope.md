---
id: "0083"
title: Of the 6th edition's linear model, the reference implements what the criteria and vectors use
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0083: Of the 6th edition's linear model, the reference implements what the criteria and vectors use

## Context

dash.js 5.3.0 contains none of `InsertPresentation`, `ReplacePresentation`, `ListMPD`, `ImportedMPD`, `alternativeMPD`; 13 of the 61 testable criteria need them.

## Decision

The reference implements the alternative-MPD insert and replace events (§5.16), the execution queue by PRT with `@executeOnce`, `@maxDuration`, `@clip`, `@earliestResolutionTimeOffset` and `@startWithOffset`, the List MPD (§8.14) with its `ImportedMPD`, and the callback events of the ad MPDs. Each is cited against the primary copy when implemented.

## Consequences

- Out: SCTE-35, MPD chaining, xlink remote Periods.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-9.

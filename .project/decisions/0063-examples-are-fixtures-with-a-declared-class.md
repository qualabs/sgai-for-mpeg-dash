---
id: "0063"
title: Examples are fixtures with a declared class, judged before the prose
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0063: Examples are fixtures with a declared class, judged before the prose

## Context

The conformance tests extract the examples from the finished spec and deduce each block's class from the document. Example G.3 (xml#40), an illustration of what a legacy Player sees, fails Publisher rules because nothing says it is not a Publisher MPD.

## Decision

Each example is a file in `spec-source/examples/` with a declared class (`publisher-mpd`, `list-mpd`, `sps-mpd`, `overlay-list`, `request`, `fragment`, `legacy-view`, `vast`). Levels 1 and 2 run per fixture by class. The deduced class is kept as a check against the declared one. The easy rules phase 09 left open (`Event@id` unique within `svta:Tracking`; type and default of `@earliestResolutionTimeOffset` and `@executeOnce` against `AlternativeMPDEventType`) and the `DASH §n` references against the primary copy's clause index (built at run time, nothing stored) are added.

## Consequences

- Examples are validated as artefacts before any prose is written.
- `legacy-view` closes the G.3 thread.
- The primary copy's text never enters the repository.

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-4.

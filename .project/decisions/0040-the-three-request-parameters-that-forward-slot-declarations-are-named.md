---
id: "0040"
title: The three request parameters that forward what the slot declares are named, and R29.1 enumerates them
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0040: The three request parameters that forward what the slot declares are named, and R29.1 enumerates them

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R29.1 says *"the four below and the audio parameter of R29.9, and no
others"*. But the allowed layouts (R38), the custom region (R39) and the audio
permission (R41.5) are also reserved parameters, R38.3 says so, and they have
no name in `context/`. The contradiction came in with the enumeration of R29
(`94ef488`).

## Decision

R29.1 has two tables: capability (the four of today and `sgai-ad-audio`) and
what the slot declares and the Player forwards: `sgai-allowed-layouts`,
`sgai-custom-region` and `sgai-ad-audio-allowed`. The closed list of R29.1
counts both tables. Decided by Nicolás Levy, 2026-10-27.

## Consequences

- The first two names are those of the published specification.
- R29.2 treats each table differently: capability parameters are optional,
  forwarded ones are required when the slot declares them (R38.2, R39.3,
  R41.5).

## Alternatives considered

**One table with all eight.** Rejected: it mixes what the Player says of
itself with what it forwards from the MPD.

**New names for all three.** Rejected: two are already published.

## Links

- DESIGN.md D-13; `context/03-requirements.md` — R29, R38, R39, R41.

---
id: "0033"
title: The file structure of context/ does not change, and 05 is left as it is
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0033: The file structure of context/ does not change, and 05 is left as it is

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

The rewrite could have redistributed `context/`. 02, 03 and 04 already
follow the order actors, requirements, use cases; 06 is the HOW and cites no
id that goes. 05 describes the base linear interface with the VAST mapping,
and overlaps I-RES for the linear case.

## Decision

The order 00 to 08 and 99 stays. 05 is not changed by this work, other than
citations to ids. Whether it becomes the illustrative annex of R11.5 is
decided separately.

## Consequences

- The overlap of 05 with I-RES for linear ads remains.
- No file is renumbered, so no cross-reference across files moves.

## Links

- ADR 0032; DESIGN.md D-6.

---
id: "0032"
title: Requirements stay the unit of 03, with an index of interfaces at the top
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0032: Requirements stay the unit of 03, with an index of interfaces at the top

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

Writing each meaning once (ADR 0029) needs each interface enumerated, or
"complete" cannot be checked. 03 is organised by requirement, and
`check-promotable` walks that unit.

## Decision

03 keeps its requirements, their order and their ids, with three changes:

- an **"Interfaces"** section at the top, one table per interface, one row per
  element with the id of the criterion that defines it. It is an index: no
  semantics, only pointers;
- inside each requirement, **the document criteria go first** and behaviour
  criteria after;
- the **writing rule** in a section of its own (ADR 0034).

## Consequences

- The diff against the old version stays readable, which the validation of
  the rewrite needs (ADR 0038).
- An element can be checked for having exactly one defining criterion (ADR
  0035).

## Alternatives considered

**One section of 03 per interface.** Rejected: it splits requirements across
sections (R40 has I-MPD and behaviour criteria), breaks the unit
`check-promotable` walks, and moves almost everything, which makes the diff
unreadable.

**One `context/` file per interface.** Rejected: the same, plus renumbering
files and every cross-reference.

**Keep the structure and only remove duplicates.** Rejected: no interface ends
up enumerated, and "complete" cannot be verified.

## Links

- DESIGN.md D-5.

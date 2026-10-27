---
id: "0027"
title: How an APS resolves an undetermined capability stays its own; returning every option is a suggestion
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0027: How an APS resolves an undetermined capability stays its own

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R29.7: *"This specification does not define how an APS resolves an
undetermined value; that is the APS's decision, and two APSs that resolve it
differently are both conformant."* No ADR recorded it. SVTA2053 v3 (ADR 0105 of
David's demo, v3 5.3.3) reverses it: *"When they are not sent, the APS SHOULD
answer with all the layoutOptions of each slot."*

## Decision

R29.7 stands. An informative note is added: an APS that does not know a
capability can return every option the advertiser allowed and leave the choice
to the Player's check (R5.6), which keeps every device that could render one of
them. The note uses *can*, not a modal.

## Consequences

- No conformance obligation moves to the APS; an APS that narrows is still
  conformant (R5.4).
- The reason to return everything is written down where an implementer will
  look, so the WG text raising it again finds the position and its reason.

## Alternatives considered

**David's `SHOULD`.** Rejected: the Player already filters (R5), so the
obligation would add nothing a conformance check could see, and it would bind
an actor this specification deliberately leaves free (R5.4).

## Links

- `context/03-requirements.md` — R5.4, R5.6, R29.7.
- `output-analysis/2026-10-27-david-v3-vs-context.md`, row 5.

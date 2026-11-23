---
id: "0052"
title: The reference Player is built on dash.js, in its own phase before the v13
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0052: The reference Player is built on dash.js, in its own phase before the v13

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

Proving that a Player supporting the extension does what the spec says needs a
Player that supports it, and none exists (ADR 0051). A reference
implementation is needed. The project lead: *"Dash.js tiene que ser la
referencia"*, and *"todos estos cambios tenemos que hacerlos ANTES de v13"*.
Building a Player is a different kind of work from writing checks on
documents, with its own design decisions (where the code lives, how it hooks
into dash.js) not yet taken.

## Decision

- The reference is a separate build of the same pinned dash.js plus our code.
  The legacy Player of ADR 0051 stays unmodified upstream dash.js.
- Behaviour tests come from the Player criteria, one or more per criterion, on
  the same mould: the quoted criterion, what is loaded (a spec MPD and a test
  APS serving its resolution documents), what is observed (network requests
  and their parameters, beacons and their timing, Player events, the geometry
  of what is drawn), and the expected result. What a black-box test cannot
  observe is `NOT_VERIFIABLE` with its reason.
- It goes in its own phase, `reference-player`, ordered
  `conformance-tests` → `reference-player` → `major-build-v13`, written in the
  `depends_on` of both items. About 10 tasks; no day estimate can be backed,
  and its largest part is drawing each layout.
- Each behaviour test stores its criterion id and text hash, like level 2: when
  the v13 changes or retires a criterion, the check exits `2` and lists which
  behaviour tests, level-2 rules and, through them, parts of the reference to
  review.

## Consequences

- The v13 arrives with all three levels running; what it changes appears as a
  list, and adapting the reference to the new carriers (R42, R1.6, R5.9, R47,
  R41) is v13 work measured from that list.
- Discarded: the reference as tasks of this phase.

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-8; `roadmap/major-build-v13`.

---
id: "0050"
title: The criteria of context/03 on documents are code, populated from the Interfaces index
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0050: The criteria of context/03 on documents are code, populated from the Interfaces index

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

Level 2 tests the spec's own rules. `context/03` holds 165 criteria: `spec
document` 61, `Player` 57, `APS` 19, `Publisher` 13, and 15 with two or more
actors (3 of them including the Player). Its "Interfaces" index lists 75
elements: 27 of the MPD (I-MPD), 16 of the request (I-REQ) and 32 of the
resolution document (I-RES), each with the criterion that defines it. The v13
will change `context/03`.

## Decision

- A second catalogue on the same mould as ADR 0049, whose quote is the
  `context/03` criterion. It is written against today's `context/03` and
  adjusted when the v13 arrives.
- The population comes from the "Interfaces" index read by code: each of the 75
  elements has a rule or a `NOT_VERIFIABLE` with its reason. The parser is the
  one in `bin/check-context-interfaces.py`, imported and not rewritten. Criteria
  on a property of the document set (cardinalities, forbidden combinations,
  order) held by `spec document`, `Publisher` or `APS` also enter: up to 108 of
  the 165, the exact number set by the T-05 classification.
- Instances: the spec's MPDs for I-MPD, the resolution documents (List MPD,
  `OverlayList`) for I-RES, and the example request URLs for I-REQ.
- The 57 Player criteria and the Player part of mixed ones are
  `NOT_VERIFIABLE — conducta del Player, nivel 3`, and feed the behaviour tests
  (ADR 0052). So is a criterion that depends on something the document does not
  carry (Player state, the clock, the ADS).
- Each rule stores its criterion id and the hash of its text. If the criterion
  was retired or its text changed, the check exits `2` and names the rules to
  review.

## Consequences

- The check and `check-context-interfaces.py` cannot read the index
  differently.
- Adjusting the catalogue to the v13 is a list, not a re-reading.

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-6, and measurement 5.

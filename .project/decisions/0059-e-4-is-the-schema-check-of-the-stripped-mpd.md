---
id: "0059"
title: E-4 is the schema check of the stripped MPD, without re-running the rules
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0059: E-4 is the schema check of the stripped MPD, without re-running the rules

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

ADR 0048 defines E-4 as §5.2.1 turned into a test: every MPD, with the
elements and attributes of other namespaces removed, is validated against
ISO's `DASH-MPD.xsd` alone **and** run through the base-standard rules of
ADR 0049. The second half was implemented in phase 09 and measured: it never
reported a failure the original document did not already have. The level-1
rules read direct children, and DASH content nested inside a foreign element
is already missing, as a child, from the original. The case built to show
it (the AdaptationSets of a Period moved inside a foreign element) is caught
on the original by DR-7.

## Decision

E-4 is the validation of the stripped MPD against `DASH-MPD.xsd` alone. The
base-standard rules run once, on the document as written. ADR 0048's other
three checks (E-1 to E-3) are unchanged.

## Consequences

- E-4 can fail, and does so together with E-3 (for example on an unknown
  element of the DASH namespace, which removal does not remove); in the
  measured cases it never fails alone. It stays because it is the literal
  statement of §5.2.1, and it would catch a future rule or schema change that
  made the two diverge.
- The negative of E-4 is `core-E4-dash-element-in-event`; the nested
  AdaptationSet case is `core-DR7-adaptationsets-inside-foreign`, expected
  from DR-7.
- Discarded: keeping the re-run for completeness. It cost one pass of every
  rule per MPD and found nothing.

## Links

- ADR 0048 (the four checks), ADR 0049 (the rules).
- `.project/phases/09-conformance-tests/TASKS.md`, T-03, its `post-ejecución` line.

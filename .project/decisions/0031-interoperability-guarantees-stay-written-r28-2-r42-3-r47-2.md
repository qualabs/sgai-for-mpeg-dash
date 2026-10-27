---
id: "0031"
title: Interoperability guarantees stay written: R28.2, R42.3 and R47.2; R20.5 and R20.6 unchanged
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0031: Interoperability guarantees stay written: R28.2, R42.3 and R47.2; R20.5 and R20.6 unchanged

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

ADR 0030 removes Player criteria that follow from the document. Some do follow
and must still be written. R28 exists so that *"every Player conformant to
this specification reads them the same way"*: a promise about Players, not
about the document, which stops being a promise if it is deduced. R42.3 and
R47.2 have the same form and the same reason: they are new carriers that a
legacy Player ignores. R20.6 requires on purpose that R20.5 be a normative
Player obligation, because *"a rule that selects which presentation option
reaches the screen cannot depend on a reader treating an illustration as a
requirement"*.

## Decision

- R28.1, R42.1 and R47.1 receive the semantics. R28.2, R42.3 and R47.2 stay as
  the explicit guarantee that every conformant Player reads that carrier with
  that semantics; their restated semantics becomes a reference.
- R47.2 keeps its privacy note.
- R20.5 and R20.6 do not change: changing them is a content decision, not one
  of wording.

## Consequences

- Two criteria more than a strict application of ADR 0030 would leave.
- The guarantee and the semantics are separate criteria, so the validation can
  check each.

## Links

- ADR 0030, ADR 0026; DESIGN.md D-7.

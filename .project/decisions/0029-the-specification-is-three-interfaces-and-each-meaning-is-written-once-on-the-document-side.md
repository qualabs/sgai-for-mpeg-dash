---
id: "0029"
title: The specification is three interfaces, and the meaning of each element is written once, on the document side
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0029: The specification is three interfaces, and the meaning of each element is written once, on the document side

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

`context/03-requirements.md` writes many facts twice: once as what the
Publisher declares or the APS carries, and again as what the Player does when
it finds it. Of its 199 criteria, 95 have the Player as their only role.

The base specification is written the other way. It says of itself that it
*"primarily specifies formats for the Media Presentation Description and
Segments"* (§1) and *"does not provide a normative specification for such a
client"* (§4.1). It writes semantics as an effect of the document, with no
actor: *"it shall be terminated at the end of this duration"* (Table 63), *"An
event is executed every time the playhead enters the active interval"*
(§5.16.2.2.1). It does not write the same fact twice.

## Decision

- **Three interfaces.** I-MPD, what the Publisher writes in the MPD; I-REQ,
  the request the Player sends the APS; I-RES, the resolution document the APS
  returns. Each element of each is listed, and each must be complete.
- **The meaning of an element is written once**, in one criterion held by the
  party that writes it (Publisher, APS or spec document), including its effect,
  written as the base writes it: *"the audio of an option that declares it MUST
  replace the primary content's audio while the option is presented"*, not
  *"when the option declares its audio, the Player MUST render it"*. Every other
  criterion and use case cites it by id.
- **The meaning keeps the strength of the obligation it absorbs.** A Player
  MUST becomes a MUST with the element as subject.
- **Semantics that lives only in prose rises to a criterion**: R3, R12, R26,
  R27, R28, R29, R31, R32 and R40, which adds R12.5 and R40.9. R33's derivation
  of the pause interval, which belongs to no interface, rises to R33.2 for the
  same reason.
- **A DP-4 privacy note follows the definition it describes**: R29.2's moves to
  R29.1. R47.2's stays, because R47.2 stays (ADR 0031).
- The use cases of 04 show how each actor uses the interfaces; they define no
  semantics.

## Consequences

- `check-promotable` walks criteria and prose modals; semantics in a prose
  table never entered the validation, and now does.
- The criteria go from 199 to 164.
- The inventory of the three interfaces (76 elements) is produced by this work:
  `context/` did not enumerate them.

## Links

- ADR 0030, ADR 0032, ADR 0034; `.project/roadmap/document-first/DESIGN.md` (D-2, D-3, Annex A).

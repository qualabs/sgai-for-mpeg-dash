---
id: "0044"
title: The writing rule names the Player as the party that writes the request
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
generalizes: ["0034"]
generalized_by: null
---

# ADR 0044: The writing rule names the Player as the party that writes the request

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

ADR 0034 fixed the text of the writing rule: the meaning of an element is
written *"in a criterion held by the party that writes the element (the
Publisher, the APS, or the specification document)"*. Of the three interfaces
(ADR 0029), the request (I-REQ) is written by the Player, and R29.3, R29.4 and
R29.10 are Player criteria that define how the request is written. Read
literally, the parenthesis excludes the writer of one interface.

## Decision

The rule reads *"(the Publisher, the APS, or the specification document; for
the request, the Player)"*. The structural check (ADR 0035) takes as the
document side of each interface the party that writes it: Publisher or spec
document for I-MPD, Player or spec document for I-REQ, APS or spec document
for I-RES.

## Consequences

- Nothing in ADR 0034 stops being true: the rule stays in
  `context/03-requirements.md` and the project `CLAUDE.md` points to it. This
  ADR widens the list of writers it names.
- A Player criterion in the I-REQ index is not a finding of the check; one in
  the I-MPD or I-RES index is.

## Links

- ADR 0029, ADR 0034, ADR 0035; `.project/phases/08-document-first/tasks/T-02/notes.md`.

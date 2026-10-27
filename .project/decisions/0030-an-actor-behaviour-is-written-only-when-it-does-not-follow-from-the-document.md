---
id: "0030"
title: An actor's behaviour is written only when it does not follow from the document
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0030: An actor's behaviour is written only when it does not follow from the document

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

With the meaning of each element written on the document side (ADR 0029),
a Player criterion that says *"when the document says X, the Player does what X
means"* restates it. The base writes behaviour only where it is needed, and
then as a guarantee to the author: *"the MPD author may assume that the steps
described in this subclause are taken, while the client implementer may
provide any functionally equivalent implementation"* (§5.16.2.2.1).

## Decision

A criterion on what an actor does stays only when it says something the
document's semantics does not reach. The classes found: an order or what is
tried first; a fallback (R5.9); what to do when a document fails, is missing,
does not conform or arrives late (R34.10); a device limit; a computation
(R4.9); when something happens (R34.3); a chain between actors (R38: the
Publisher declares, the Player forwards, the APS obeys); and a guarantee of
interoperability that has to be stated to hold (ADR 0031). Every other Player
criterion goes, and its content moves to the criterion that defines the
element.

## Consequences

- 83 criteria change: 46 are rewritten, 31 merged into another, 6 withdrawn.
- Whether a Player criterion is deducible is a judgement, not a syntactic
  property: no check enforces it (ADR 0035). The writing rule (ADR 0034) and
  the validation of the rewrite (ADR 0038) carry it.

## Links

- ADR 0029, ADR 0031; DESIGN.md D-4.

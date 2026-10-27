---
id: "0034"
title: The writing rule lives in context/03-requirements.md, and the project CLAUDE.md points to it
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
generalizes: null
generalized_by: "0044"
---

# ADR 0034: The writing rule lives in context/03-requirements.md, and the project CLAUDE.md points to it

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

ADRs 0029 to 0031 are a rule for writing requirements that has to hold for
every future criterion, including multiview's. `context/` must stand on its
own, and both the build prompts and the working group read it.

## Decision

A section "How requirements are written" at the top of 03:

> **How requirements are written.** This specification defines three
> interfaces: what the Publisher writes in the MPD, the request the Player
> sends the APS, and the resolution document the APS returns. The
> "Interfaces" section lists every element of each, and the criterion that
> defines it.
>
> 1. The meaning of an element is written once, in a criterion held by the
>    party that writes the element (the Publisher, the APS, or the
>    specification document), including its effect, with the strength of
>    the obligation it states. Every other criterion, and every use case,
>    cites it by identifier and does not restate it.
> 2. A criterion on what an actor does is written only when it does not
>    follow from the meaning of what the document carries: an order, a
>    fallback, what to do when something fails, is missing, does not
>    conform or arrives late, a device limit, a computation, when something
>    happens, a chain between actors, or a guarantee of interoperability
>    that has to be stated to hold.
> 3. Identifiers are stable. A criterion that is merged into another, or
>    withdrawn, keeps its identifier out of use, and the "Retired
>    identifiers" table says where its content went.

The project `CLAUDE.md`, in its tone section, carries one line: *"Requirements
follow the writing rule at the top of `context/03-requirements.md` ("How
requirements are written"); it is not restated here."*

## Consequences

- One copy of the rule; the `CLAUDE.md` cannot drift from it.
- A reader of `context/` alone has the rule.

## Links

- ADR 0029, ADR 0030, ADR 0036; DESIGN.md D-8.

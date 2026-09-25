---
id: "0019"
title: A base @skipAfter on a linear event is honoured, and the base answer takes precedence by default
status: accepted
scope: core
date: 2026-09-25
supersedes: null
superseded_by: null
---

# ADR 0019: A base `@skipAfter` on a linear event is honoured

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

ADR 0017 moved R35's dismissal declaration into a field of this
specification's own, because the base `@skipAfter` defaults to PT0S,
skippable everywhere, and R35.1 makes an undeclared slot
non-dismissible. It left one case open: a Publisher can still write the
base `@skipAfter` on an inherited linear event (DASH §5.16.5.2), and
R35 applies to the linear family too.

## Decision

**Where a linear event carries the base `@skipAfter`, the Player honours
it with its base meaning, and it governs the slot (R35.8).** R35.1's
default applies only where neither the event nor the resolution document
declares anything.

**The criterion is ADR 0006, now a requirement (R1.5): where the base
specification already answers a question, its answer takes precedence.**
In Nicolás Levy's words: *"lo que hace ya DASH es prioridad para tomar
decisiones"*. ADR 0006 held the principle; R1.5 puts it in `context/`, so
the build applies it without reading the ADRs.

## Consequences

- A Player of this specification and a base Player treat the same
  linear event the same way.
- ADR 0017 stands: the exception is about where R35's declaration
  travels, not about retiring a base attribute.

## Links

- ADR 0006, ADR 0011, ADR 0017, ADR 0018.
- `context/03-requirements.md` — R1.5, R35.8.
- `context/06-naming-and-namespaces.md` — "Viewer dismissal is a
  deliberate exception".

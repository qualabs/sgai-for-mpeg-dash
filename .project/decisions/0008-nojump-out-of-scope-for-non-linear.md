---
id: "0008"
title: The base standard's unskippable-break capability is out of scope for non-linear ad forms
status: accepted
scope: core
date: 2026-09-16
supersedes: null
superseded_by: null
---

# ADR 0008: `@noJump` is out of scope for non-linear forms

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

ADR 0006 settles that this specification adopts the DASH execution
model where the base standard already answers. `@noJump` is such an
answer: it lets a Publisher declare that the playhead may not move
across an event without executing it — an unskippable break.

Applying ADR 0006 mechanically would inherit it for every slot family
this specification defines.

## Decision

**`@noJump` is out of scope for the non-linear families — overlays and
pause ads — and is declared as an exclusion rather than omitted.** For
linear breaks it is inherited unchanged.

## Alternatives considered

**Inherit it for every family.** Rejected on what it would do to the
viewer. A linear break occupies the timeline: the ad plays instead of
the programme, and preventing a skip withholds an ad the viewer has
not yet been shown. A non-linear form is composited **over** the
programme. Preventing a skip across a non-linear window therefore
forces the viewer to watch **a stretch of the programme they chose to
skip**, in order to deliver an ad on top of it. That is not delivering
an advertisement; it is penalising a skip.

**Omit it silently.** Rejected, and this is the half worth recording:
a construct absent from a specification says nothing about whether
anyone considered it. A reader cannot distinguish a deliberate
exclusion from an oversight, and the next revision re-opens the
question with no record of why it closed.

## Consequences

This is the first declared exception to ADR 0006, and it is written as
an exception with its reason rather than as a silent divergence —
which is the form ADR 0006 requires. A criterion with no exceptions
has either been applied to nothing, or applied without looking.

Nothing prevents a Publisher from using `@noJump` on baseline DASH
events. This specification neither builds on it nor requires it for
the families it defines.

---
id: "0007"
title: The APS declares what happens when pause-ad candidates are exhausted, not the Publisher
status: accepted
scope: core
date: 2026-09-16
supersedes: null
superseded_by: null
---

# ADR 0007: The APS declares pause exhaustion behaviour

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

A pause slot has no authored duration (R31): the viewer decides how
long it lasts. The candidates a resolution document carries can
therefore run out while the viewer is still paused, and R5.3's
fall-through to primary content cannot apply, because the primary
content is what is paused.

Three behaviours are useful when that happens: repeat the sequence,
request another resolution document, or stop and show the paused
frame. Someone has to declare which one applies.

## Decision

**The resolution document declares it, which places the choice with
the APS.** `stop` is the default when no declaration is present.

## Alternatives considered

**The Publisher declares it, in the slot.** Rejected on incentives,
not on principle. A Publisher-declared limit on how many documents may
be served gives the APS a single opportunity to fill an interval of
unknown length. The rational response is to return a defensively long
candidate list every time, whether or not the inventory warrants it —
so a rule intended to bound what the APS serves would instead push it
to serve more, every time, for every pause. **The constraint would
produce the outcome it exists to prevent.**

The Publisher does retain what the Publisher should retain: whether a
pause window exists at all, and where on the timeline it applies.
What it does not retain is how the interval it sold gets filled.

**The Player decides.** Rejected: the Player has no view of inventory
and no stake in the outcome. A rule it cannot reason about becomes a
per-implementation default, which is the interoperability failure the
specification exists to avoid.

**Leave it undefined.** Rejected: the state is reachable in ordinary
operation, not at an edge. Leaving it silent means each Player picks,
and a viewer paused for a long time sees behaviour that varies by
device.

## Consequences

`stop` as the default is deliberate: it is what the viewer would see
if this mechanism did not exist, and it is the only one of the three
every Player can perform without additional capability. A default that
requires a network request would make the absent declaration more
expensive than the declared cases.

Under `request-again`, a resolution document carrying no candidates
(R30) is treated as `stop` for the remainder of that pause. The empty
resolution already means "nothing was sold"; it needs no second
meaning here.

Whether a second request within one pause is the same opportunity or a
new one is not settled by this decision, and does not need to be: the
metric that matters is filled duration over paused duration (R33),
which is the same number either way.

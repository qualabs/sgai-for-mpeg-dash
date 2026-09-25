---
id: "0018"
title: Early resolution of overlay and pause windows adopts the base earliestResolutionTimeOffset and its 60-second default
status: accepted
scope: core
date: 2026-09-25
supersedes: null
superseded_by: null
---

# ADR 0018: Early resolution adopts the base offset and its default

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R36 lets a Player resolve an overlay or pause opportunity window ahead of
time, within an offset the Publisher declares. R36.1 said that a window
declaring no offset *"is resolved when it fires"*.

The base specification already has the offset.
ISO/IEC 23009-1:2026 §5.16.5.2, Table 63, `@earliestResolutionTimeOffset`:
*"specifies the time interval (in units of EventStream@timescale) prior to
the Event@presentationTime during which the MPD described in the @uri
attribute may be requested. The default is 60 seconds in units of
timescale."* ERT is *"a media time defined by the value of
Event@presentationTime, minus the value of
AlternativeMPDEventType@earliestResolutionTimeOffset, normalized by the
value of @timescale"* (§5.16.2.1, Table 57). An overlay or pause window
declared as an `<Event>` has a presentation time that is the start of the
window, so R36.2 and R36.3 are ERT computed the base way.

`context/06-naming-and-namespaces.md` requires reusing that construct with
its default. R36.1 contradicted the default, and the incremental build over
v9.1 left the conflict unresolved, keeping the 60 seconds until a human
decided.

## Decision

**The base construct is adopted with its default.** The offset of R36 is
`@earliestResolutionTimeOffset`, in units of the parent
`EventStream@timescale`, and a window that declares nothing may be
resolved up to 60 seconds before it starts. A Publisher who wants
resolution at the moment the window fires declares an offset of zero.

## Why

**Resolving at the moment the window fires wastes the window.** In
Nicolás Levy's words: *"hagamos lo que dice dash!! Si lo hace al momento de
llegar el anuncio no se va a usar toda la ventana por la demora del
proceso."* A resolution request takes time, and every second it takes
after the window opens is a second of the window the ad does not use. A
default of zero makes that loss what a Publisher gets by saying nothing.

**And it is the same criterion as ADR 0011.** A Player implementing this
specification and a Player implementing the base specification should
behave the same on the same manifest. An offset attribute with the base
name and a different default would make the two diverge exactly where a
Publisher wrote nothing.

## Alternatives considered

**Keep R36.1: an undeclared window resolves when it fires.** This needs a
carrier with no default, so either a new attribute next to a base one that
means the same thing, or the base attribute with its default overridden.
The first contradicts the reuse rule, the second contradicts the base
specification's own semantics for the name. Rejected on both counts, and on
the latency argument above.

## Consequences

- R36.1 names the construct, its units and its default; R36.2 and R36.3
  compute against the declared offset or the default; R36.7 no longer says
  that a Publisher who declares nothing gets resolution at fire time.
- The freshness half of R36 is unaffected. How long a resolution keeps
  (R36.4) has no base construct, and a resolution obtained 60 seconds
  early is checked at fire time as before (R36.5).
- `context/06-naming-and-namespaces.md` records the reuse next to the
  rule, so the carrier is named where the build looks for it.
- **The schema carries no default.** The base schema declares the
  attribute as `type="xs:unsignedLong"` with no `default` (§5.16.6), while
  the semantics table gives 60 seconds. This decision follows the
  semantics table, which is where the base specification states the
  behaviour; the schema's omission is the base specification's, not a
  choice of this one.

## Links

- ADR 0006 — adopt the base standard's execution model where it answers.
- ADR 0011 — the behavioural-equivalence criterion this decision applies.
- ADR 0017 — the opposite outcome for R35, where the base default
  contradicts the requirement and the construct is not reused.
- `context/03-requirements.md` — R36.
- `context/06-naming-and-namespaces.md` — "Naming consistency with baseline
  DASH".

---
id: "0005"
title: An unfilled ad opportunity is expressed as an empty resolution document, not as an HTTP status code
status: accepted
scope: core
date: 2026-09-14
supersedes: null
superseded_by: null
---

# ADR 0005: Empty resolution as a document, not a status code

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

An ad opportunity can resolve with no ads at all: the APS asks for a
decision and the decision carries nothing. This is ordinary — the
inventory was not sold, or the decisioning filters left nothing — and it
is not a failure of the system.

The spec already settled what the Player does. The Player-to-APS
interface table in `../../context/05-dash-linear-interfaces.md` states
that an *"empty `ListMPD` or 4xx/5xx"* makes the Player fall through to
the primary content; R5.3 requires the Player to continue with the
primary content once candidates are exhausted; and
`../../context/04-use-cases.md` states that *"'skip the opportunity' is
always a valid outcome and not a failure"*. Playback continuity was
never in question.

What was open is what the APS is asked to do **before** that. The SVTA
Advertising WG raised it on 2026-08-19 without concluding: an unfilled
break today is simply passed forward to the client, which the chair
called wasteful, with the reason that *"those are missed ad breaks.
That's missed revenue, so it's important that they're identified."*

The gap this exposes is narrow and real: as the interface table stands,
an unfilled opportunity and a failed resolution are **indistinguishable**
— both live in the same cell and produce the same Player behaviour. That
is correct for playback and useless for identification.

**`204 No Content` was proposed as the alternative** (by Nicolás Levy,
on reviewing the draft requirement). It is a serious candidate, not a
misunderstanding: a 204 is a 2xx, so it separates "resolved, nothing to
serve" from a 4xx/5xx failure by construction, without a body to parse.
Anyone auditing this decision should expect to reach for it.

## Decision

An opportunity that resolves with no ads is expressed as a **resolution
document carrying no candidates**. It is not expressed as an error
response, and not as a response without a body. This lands as **R30** in
`../../context/03-requirements.md`.

### D-1. The argument that decides it is internal, not precedent

R13 makes the ADS the authority over the tracking schedule and obliges
the APS to express ADS-declared tracking **in the resolution document**:
*"the ADS declares the schedule in its VAST; the APS expresses it in the
resolution document using DASH callback events."*

The no-ad notification is ADS-declared tracking. A bodiless response has
nowhere to carry it, and a `204` with a body is invalid HTTP. So
choosing a status code would leave R13 unsatisfiable in precisely the
case under discussion — the empty one. The candidate does not fail on
taste; it fails against an obligation the spec already carries.

### D-2. The decision format already answers this the same way

VAST prescribes a document, not a status code: *"When the ad server does
not or cannot return an Ad, the VAST response should contain only the
root `<VAST>` element with optional `<Error>` element"*, and that
root-level element *"is primarily used to report a 'No Ad' response"*.
The empty case therefore already travels as a valid document that
carries its own notification. Since the APS converts the decision format
into the resolution document, expressing the empty case as a status code
would break that correspondence exactly at the boundary where the APS
translates.

### D-3. Not choosing the transport was considered and rejected

The requirement could have asserted only that an empty resolution is
distinguishable from a failed one, leaving each implementation to pick
how. That was rejected, and the reason matters more than the others
here, because it is the elegant-looking way back into this decision:
**the two candidates are not equivalent.** One can carry the ADS's no-ad
notification and the other cannot, by definition of the protocol. A
requirement saying "distinguish them however you like" would therefore
assert something false — that the choice does not matter — rather than
something neutral, and it would leave the requirement unverifiable.

Deferring a *spelling* to the syntax stage (as R29.1 does for parameter
names) is a different act from deferring a choice that changes which
obligations can still be met.

## Consequences

### Positive

- **An unfilled opportunity can be identified as such.** That was the
  only thing the WG asked for, and this is the smallest change that
  delivers it.
- **No new mechanism.** Nothing is added to the response shape: the
  requirement constrains which of the already-available forms is used.
  No tracking construct is invented, and no actor is given new work.
- **R13 stays satisfiable in every case**, including the empty one.

### Negative / limits

- **It constrains the APS's HTTP behaviour**, which is otherwise close
  to the boundary that R18 keeps out of scope. The justification is that
  the resolution response is Player-visible, and R18.1 already places
  the resolution document's format inside the spec.
- **The Player-visible behaviour does not change**, so an implementer
  gains nothing at playback time from complying. The benefit accrues to
  whoever counts unfilled opportunities, which is not an actor this spec
  models.
- **`204` remains a reasonable-looking option to anyone who has not read
  this ADR.** That is why the reasoning is recorded here rather than
  inside R30: the requirement states the rule, this document states why
  the obvious alternative loses.

## Links

- `../../context/03-requirements.md`: R30 (this decision), R13
  (ADS-declared tracking expressed in the resolution document), R5.3
  (Player continues when candidates are exhausted), R18 / R18.1 (the
  Player-visible interface is what this spec defines).
- `../../context/05-dash-linear-interfaces.md`: the Player-to-APS
  interface row that today merges the empty and failed cases.
- `../../context/04-use-cases.md`: skipping an opportunity is a valid
  outcome, not a failure.
- `../phases/05-wg-feedback-round-2/svta-wg-2026-08-19-agreements.md`:
  item O7, where the WG left the question open.

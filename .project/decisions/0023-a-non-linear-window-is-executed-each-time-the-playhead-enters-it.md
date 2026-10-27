---
id: "0023"
title: A non-linear window is executed each time the playhead enters it, and each execution resolves
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0023: A non-linear window is executed each time the playhead enters it

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

Nothing in `context/` said what happens when the playhead returns to an overlay
or squeezeback window already presented — a VOD rewound, a seek back, a join
inside it. R3.2 makes undefined behaviour non-conformant, so the silence was a
gap, and SVTA2053 v3 (row 15 of the analysis) answers it.

The base specification answers it for its own events: *"An event is executed
every time the playhead enters the active interval, including the case of join
(tune-in) during the active interval or time-shifted operation moving the
playhead to a position prior to EAP."* (§5.16.2.2.1), and *"The alternative MPD
is resolved at each execution of the Event"* (§5.16.2.2.6). R1.5 makes that
answer ours.

## Decision

- **R34.6.** On an overlay or squeezeback window not declared once-per-session,
  every entry of the playhead into its range is a new **execution**, presented
  as the first was, with its own cap and its own beacons.
- **R34.7.** Each execution resolves the opportunity, so its candidates may
  differ; an earlier resolution is presented again only while still usable
  (R36.5).
- **R36.4.** A resolution that does not declare how long it keeps is usable for
  the execution it was obtained for (it said: *"for as long as its opportunity
  window lasts"*). An APS that wants it reused declares its validity.
- **R13.7.** The slot-start beacon fires once per execution.
- The glossary defines *Execution (of an opportunity window)* with the base
  term, which R20.1 already used.

## Consequences

- Rewinding over a window presents it again and counts it again. A Publisher
  that does not want that declares once-per-session (ADR 0024). UC-21 shows it.
- A viewer's dismissal (R35) does not survive a rewind: a new execution is a new
  presentation of the window. Accepted.
- Coming back to a window after an inherited linear event is not an entry
  (ADR 0025).

## Links

- ADR 0006 (adopt the base execution model where it answers), ADR 0024, ADR
  0025, ADR 0028.
- `context/03-requirements.md` — R13.7, R34.6, R34.7, R36.4.

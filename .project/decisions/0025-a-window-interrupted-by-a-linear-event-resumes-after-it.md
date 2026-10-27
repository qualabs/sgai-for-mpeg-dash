---
id: "0025"
title: A window interrupted by an inherited linear event resumes after it, in the same execution
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0025: A window interrupted by an inherited linear event resumes after it

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R40.4, for a window that declares no relation (ADR 0020): *"A form on screen
when an alternative presentation begins ends there, and the window presents
nothing further."* A mid-roll inside a long overlay window therefore ended the
window for good, though the programme came back inside its range. SVTA2053 v3
(ADR 0114 of David's demo): while the linear runs nothing is drawn or counted,
and if the window is still open when the programme returns, it resumes.

## Decision

- **R40.4.** While an inherited linear event the window overlaps is executed,
  the Player presents nothing of the window and fires none of its beacons; a
  form on screen is suspended. When the presentation that declares the window
  is output again with the playhead still inside its range, the window resumes:
  the suspended form from where it was suspended, then the rest of the sequence,
  until the window ends or its cap is reached. Returning outside the range ends
  the execution.
- **It is the same execution, not a new one.** It does not resolve again, does
  not consume a once-per-session window a second time and does not fire the
  slot-start beacon again. The base distinguishes entering from returning: an
  execution begins when the playhead *enters* the active interval
  (§5.16.2.2.1), and after an insertion the programme resumes at `RT = PRTA`
  (Table 57) — the playhead neither left nor entered. It is the pattern R17.2
  already has for an overlay suspended by a pause ad.
- **R4.11.** The time a form is suspended — during a viewer pause or while an
  inherited linear event is executed — does not accrue against the cap; on a
  replacement the programme timeline advances, so it has to be said.

## Consequences

- What ADR 0020 decided stands: by default the window is never shown over the
  linear event, and no two ads appear at once. Supersede and on top are
  unchanged.
- A viewer seek or rewind is a new execution (ADR 0023); a cut the Player makes
  for a linear event is not. UC-22 exercises the difference, and UC-14 shows
  the blackout case.

## Links

- ADR 0020 (still accepted), ADR 0023.
- `context/03-requirements.md` — R4.11, R17.2, R40.4.
- `context/04-use-cases.md` — UC-14, UC-22.

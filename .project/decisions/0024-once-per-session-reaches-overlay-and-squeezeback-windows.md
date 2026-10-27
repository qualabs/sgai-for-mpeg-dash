---
id: "0024"
title: Once-per-session reaches overlay and squeezeback windows, with the base's counter and carrier
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0024: Once-per-session reaches overlay and squeezeback windows

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R34 let only a pause window be declared once-per-session. With every entry into
an overlay or squeezeback window an execution (ADR 0023), a Publisher needs the
same bound there; SVTA2053 v3 has it as `ONCE`.

The base specification carries it: `@executeOnce` (§5.16.5.2, Table 63,
default `"false"`) — *"If true, if some of the media during the active interval
of this event is played more than once, the event is executed only the first
time this media time is traversed."* Its counter counts executions whose
alternative playback *"successfully started"* (§5.16.2.2.2, Table 58), and a
failed one leaves the event executable (§5.16.2.2.6, NOTE 3).

## Decision

- **R34** covers the overlay, squeezeback and pause families. R34.1 lets the
  Publisher declare any of them once-per-session; R34.5 makes the Player leave
  the content uninterrupted, and fire none of the window's beacons, on every
  later entry into a consumed window.
- **What consumes it is the base counter**: an ad beginning to render (R34.3).
  A crossing with no ad — a seek over it, an empty resolution — leaves it
  available. This differs from David's `ONCE`, which is spent when playback
  enters and leaves the window.
- **The carrier is `@executeOnce`**, with its name and its default, recorded in
  `context/06-naming-and-namespaces.md` (R1.5).

## Consequences

- The same declaration means the same thing on a base event and on a window.
- A once-per-session window that resolved empty can still sell later.

## Links

- ADR 0023; `context/03-requirements.md` — R34; `context/06-naming-and-namespaces.md`.

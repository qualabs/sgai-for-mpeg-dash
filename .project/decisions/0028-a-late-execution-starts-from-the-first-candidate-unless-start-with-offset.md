---
id: "0028"
title: A late execution of a window starts from its first candidate unless the window declares the base's start-with-offset
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0028: A late execution starts from the first candidate unless the window declares start-with-offset

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

With every entry into a window an execution (ADR 0023), an execution can begin
after the window's start — a join or a seek landing inside it. The question is
where in the sequence of candidates it begins. Nicolás Levy asked that the
answer be the one the base specification already gives its own events.

The base calls it delayed execution: *"join and seek operation, as well as
playback of a previous alternative presentation may have caused it to start at
a delay (delayed execution)"* (§5.16.2.2.6). Its default: *"By default, a
static alternative Media Presentation starts from the beginning (i.e. ASO =
0)."* (§5.16.2.2.6). And the event may declare otherwise, with
`ReplacePresentation@startWithOffset` (§5.16.4, Table 62, default `"false"`):
*"specifies whether a static alternative presentation starts at the beginning
("false") or at an offset (from the start of the alternative Media
Presentation) corresponding to the difference Δ between the presentation time
of the event and the current playhead position, i.e. Δ = PRTA – PRT."*

## Decision

- **R34.8.** A late execution presents the sequence from its first candidate,
  unless the window declares that it starts with an offset; then it begins at
  the point of the sequence as far from its start as the execution is from the
  window's start, and candidates ending before that point are not presented.
  Either way the execution ends no later than the window (R40). A time-bound
  beacon whose time falls in a part not presented is not fired (R13.2).
- **R34.9.** The Publisher MAY declare start-with-offset on an overlay or
  squeezeback window; without it, every execution starts from the first
  candidate.
- **The carrier is `@startWithOffset`**, with its name and its default, recorded
  in `context/06-naming-and-namespaces.md` (R1.5).
- **The analogue is the replacement, not the insertion.** The attribute exists
  only on `ReplacePresentation`, because an insertion stops the programme
  timeline; a window runs with that timeline advancing underneath, as a
  replacement does.
- **`@clip` is not brought.** It is `@startWithOffset`'s companion (default
  `"true"`: the alternative terminates *"at the latest at time PRT +
  APDmax"*), and the base forbids `@startWithOffset` with `@clip="false"`. A
  window already ends with its range (R40), which is the base's `"true"`; a
  `"false"` would present outside the window.

## Consequences

- Same default as the base, same declaration to depart from it.
- The time map the offset needs exists: R14.1 plays candidates back to back,
  and a skipped candidate takes no time.
- A Publisher who declares the offset accepts that a candidate begun mid-way
  loses the beacons of its unpresented part, as a replacement with the
  attribute does.
- Pause windows are outside it: their trigger is the viewer, and they have no
  late entry.

## Alternatives considered

**Always from the first candidate**, with no declaration. Rejected: the base
offers the Publisher the choice on its own events, and R1.5 asks for the base
answer where there is one.

**Start at the second of the seek, always** (David's demo). Rejected as a
default for the same reason; it is what the declaration gives.

## Links

- ADR 0023, ADR 0006; `context/03-requirements.md` — R14.1, R34.8, R34.9, R40;
  `context/06-naming-and-namespaces.md`.

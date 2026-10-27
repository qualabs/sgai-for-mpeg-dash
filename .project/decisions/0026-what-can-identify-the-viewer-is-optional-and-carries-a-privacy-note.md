---
id: "0026"
title: What can identify the device or the viewer is optional to send and carries a privacy note
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0026: What can identify the device or the viewer is optional to send

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R29.2 made every capability parameter optional, with no word on why. SVTA2053
v3 adds the reason — capability values *"add to the information that can be
used to fingerprint a device or a viewer"* — and a pair of modals: send them
only where the implementer's policies allow it (SHOULD), and where they allow
it, sending is RECOMMENDED. `context/` had no rule that would make the next
requirement that discloses something about the device ask the same question.

## Decision

- **DP-4**, a design principle: information about the device or the viewer that
  the Player originates and discloses to another actor — a capability, a
  measurement, a determination it makes — MUST be optional for the Player to
  send, and the specification MUST carry a privacy note where it defines it.
- **Beacons are outside it.** Executing an instruction the resolution document
  carries, such as firing a beacon whose URL the APS wrote complete (OOS-10), is
  not information the Player originates. Making beacons optional would break the
  measurement the opportunity is sold on (DP-3), and consent to tracking belongs
  to each market's law and to whoever deploys the Player.
- **Notes** on R29.2 (capabilities), R33 (`PlayList` metrics), R44.3
  (verification resources) and R47.2 (the viewability determination). Each of
  those was already optional; the note says what it discloses.
- **David's `RECOMMENDED` is not brought.** It pushes towards sending, against
  DP-4; R29.7 and R5 work without any capability.

## Consequences

- A future requirement that has the Player disclose something is written
  optional, with its note, or departs from a principle explicitly.
- R13, R42 and the undetermined beacon of R47.2 are unchanged.

## Links

- `context/03-requirements.md` — DP-4, R29.2, R33, R44.3, R47.2.
- `output-analysis/2026-10-27-david-v3-vs-context.md`, row 3.

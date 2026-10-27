---
id: "0043"
title: The ClickThrough destination follows the model of R48.3
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0043: The ClickThrough destination follows the model of R48.3

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

No criterion says what the Player does with the ClickThrough's destination
URL: only that activating it fires the click-tracking.

## Decision

The Player makes the destination available to the viewer by the means its
device has, and how is up to the Player, as R48.3 does for disclosure. It goes
in R28. Decided by Nicolás Levy, 2026-10-27.

## Consequences

- It is new content, and the validation accepts it only at R28 (ADR 0038).
- Devices with no browser or no pointer conform by their own means.

## Links

- DESIGN.md D-16; `context/03-requirements.md` — R28, R48.3.

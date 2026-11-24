---
id: "0080"
title: Device classes D1–D5 are emulated in one Chromium by a device profile
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0080: Device classes D1–D5 are emulated in one Chromium by a device profile

## Context

There is one browser; R3.1 defines the classes by concurrent video decoders, renderable forms, layouts and ad audio.

## Decision

The class is a configuration of the module. The reference chooses what a device of that class would choose; nothing measures real decoders.

## Consequences

- Real devices are out of scope.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-6.

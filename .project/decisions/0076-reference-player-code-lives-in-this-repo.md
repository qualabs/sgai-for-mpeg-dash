---
id: "0076"
title: The reference Player's code lives in this repo, under `reference-player/`
status: accepted
scope: phase-11
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0076: The reference Player's code lives in this repo, under `reference-player/`

## Context

`PROJECT.md` left open whether the prototype lives in this folder or in an external repo. The tests, their fixtures and the criterion hashes live here.

## Decision

The code lives in `reference-player/` at the project root. It moves to its own repo only when it has to be published as a package.

## Consequences

- `CLAUDE.md` adds the folder to its layout.
- A change to `context/03` touches one repo, not two.
- Approved by the project lead on 2026-11-23.

## Links

- Design: `.project/phases/11-reference-player/DESIGN.md`, D-2.

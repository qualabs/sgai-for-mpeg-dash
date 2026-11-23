---
id: "0073"
title: Promotion is a script that requires every gate and copies the full set
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0073: Promotion is a script that requires every gate and copies the full set

## Context

Promotion was carried out by hand against a criterion written in `CLAUDE.md`, and `dist/` ended up without the extension XSD and the conformance-test reports the project's documents promise.

## Decision

`bin/promote.py v<N>` promotes only when the assembled document matches its source, `lint-spec`, `check-trace`, `check-promotable` and `check-dash-conformance` exit 0, and `compare-candidates` says `BETTER THAN PUBLISHED`. It copies spec, XSD, `conformance-tests.md`/`.json`, sidecars and trace, and writes `PROVENANCE.md` and `inputs.sha256` including `spec-source/`. The coordinator runs it and reports, without asking, as before.

## Consequences

- An incomplete `dist/` is no longer possible.
- Nothing is promoted in this phase: v12.6 has 9 FAIL.

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-14.

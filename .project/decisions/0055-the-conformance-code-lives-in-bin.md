---
id: "0055"
title: The conformance code lives in bin/, like the rest of the build's checks
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0055: The conformance code lives in bin/, like the rest of the build's checks

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

The project keeps the executable checks the build invokes in `bin/`, with their
tests as `bin/test_*.py` (for example `test_check_context_interfaces.py`). The
conformance tests add two entry points, two rule catalogues and a Player
harness.

## Decision

- `bin/emit-extension-xsd.py` and `bin/check-dash-conformance.py` are the
  entry points.
- The two catalogues live in a module beside them, `bin/conformance/`, with
  `dash/` for level 1 and `spec/` for level 2.
- Their tests are `bin/test_*.py`.
- The Player harness lives in `bin/players/` with its `package.json`, which
  pins the versions.
- `CLAUDE.md` and `prompts/README.md` are updated with the two steps, the two
  scripts and the new artefact.

## Consequences

- The conformance checks follow the existing `bin/` conventions: they can
  fail with an exit code, which a prompt cannot.

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-11.

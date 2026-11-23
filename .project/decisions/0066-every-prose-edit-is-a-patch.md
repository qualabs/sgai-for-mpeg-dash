---
id: "0066"
title: Every edit of the prose is a patch applied by a script
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0066: Every edit of the prose is a patch applied by a script

## Context

A refine returned a whole document. v9.1 changed 8 sections nobody declared (seven annexes lost `*Informative.*`), and the reading cost is the whole spec on every call.

## Decision

Refines, increments and majors return a patch: `{section, find, replace, reason}` with `find` unique in the section, or `{section, replace_section, reason}`. `bin/apply-spec-patch.py` applies it to `sgai-spec.src.md` and refuses an absent or repeated `find` or an edit of a directive (an example or a table is fixed in its source). Scope is checked as `check-incremental.py scope` does. The patch is the trace, in `output-analysis/`; unresolvable items go to a `refine-gaps` sidecar.

## Consequences

- An undeclared change is impossible by construction.
- No `<!-- refine -->` annotation enters the spec.
- The agent reads only the sections it edits.

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-7.

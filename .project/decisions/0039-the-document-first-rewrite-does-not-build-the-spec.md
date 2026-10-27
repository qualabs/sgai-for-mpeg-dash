---
id: "0039"
title: The document-first rewrite does not build the specification; v13 is a separate item, and the rewrite goes before multiview writes in 03
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0039: The document-first rewrite does not build the specification; v13 is a separate item, and the rewrite goes before multiview writes in 03

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

There is one build, v13. If it ran on today's structure, the following build
would have to validate it all again.

## Decision

The rewrite ends in `context/`, validated (ADR 0038). The build is
`roadmap/major-build-v13`: one major run that gathers what accumulated since
v12.6 (phase 07, the error-semantics fix and the carriers the incremental
could not place), this rewrite and multiview. The multi-asset profile is not
in it.

This rewrite goes before multiview writes its requirement in 03, so multiview
writes it once under the rule and the check. If 03 changes between the design
and the start, the obligation map is redone on the new commit before
rewriting.

## Consequences

- v13's comparison against what is published cannot separate the restructure
  from the rest of the delta. Accepted: the restructure is protected without a
  build (ADR 0038), and the rest is recorded decision by decision in `LOG.md`
  and the ADRs.

## Links

- ADR 0038; DESIGN.md D-1.

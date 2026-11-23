---
id: "0061"
title: One prose source, read by section, not split by chapter
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0061: One prose source, read by section, not split by chapter

## Context

Splitting the spec into one file per chapter was proposed to cut reading cost. Measured over seven refines: the chapters a fix touched were ~42% of the bytes (up to 82%), because §4 and §5 (2,409 lines) fall in almost every fix; the sections touched were ~9% (up to 21%). The spec carries 524 `§n` cross-references.

## Decision

The prose stays in one file. Reading is by section (`bin/spec-section.py`), and edits are by section (ADR 0066). A build that generates chapters in parallel writes them to scratch and concatenates them.

## Consequences

- The reading cost falls to the touched sections without a file layout to maintain.
- Cross-references resolve inside one document and the lint checks them on the assembled spec (ADR 0065).
- Discarded: one source file per chapter.

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-2.

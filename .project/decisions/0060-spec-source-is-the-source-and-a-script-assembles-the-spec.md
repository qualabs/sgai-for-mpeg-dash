---
id: "0060"
title: The spec's source is spec-source/, and a script assembles the document
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0060: The spec's source is spec-source/, and a script assembles the document

## Context

The spec was written and judged as one 7,483-line text. Its examples (31.5% of the lines), the §5 tables and the §5.10.1 schema repeat facts that code can produce and check, and every edit rewrote the document a build had produced.

## Decision

A versioned `spec-source/` sits between `context-analysis/` and `output/`: the prose (`sgai-spec.src.md`) with inclusion directives, `syntax/` (the extension XSD and `syntax.yaml`), `examples/` (fixtures) and `scenarios/` (UC vectors). `bin/assemble-spec.py` replaces each directive and writes `output/v<N>-sgai-spec.md` with a manifest of the source hashes. The dependency arrow becomes `context/` → `context-analysis/` → `spec-source/` → `output/` → `output-analysis/`. The initial source is extracted from v12.6 and MUST assemble to `dist/sgai-spec.md` byte for byte.

## Consequences

- `output/` is still never edited by hand; builds now write `spec-source/` and assemble.
- The byte-for-byte reproduction is the test that the source is the spec.
- Discarded: marking generated regions inside the published document with comments (the published document has to carry none, ADR 0065).

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-1.

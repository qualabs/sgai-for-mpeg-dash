---
id: "0047"
title: The extension XSD is a build artefact, extracted by code from the spec
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0047: The extension XSD is a build artefact, extracted by code from the spec

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

The extension XSD does not exist as a file today: it lives only as the §5.10.1
block inside `dist/sgai-spec.md`, and measuring it against DASH required
pulling it out of the markdown by hand. The extensions are born in the process
that generates the spec, and the XSD is part of the spec's normative text. If
the LLM wrote both, there would be two copies that agree only when the LLM
makes no mistake.

## Decision

- The XSD is a build product with the same rank as the spec: one file per
  candidate, `output/v<N>-sgai-extension.xsd`, and on promotion
  `dist/sgai-extension.xsd`.
- Single source: the §5.10.1 block. `bin/emit-extension-xsd.py` extracts it
  from the freshly generated candidate. It exits `2` if the candidate has no
  `xs:schema` block with `targetNamespace="urn:svta:dash:sgai:2026"` or has
  more than one, and `1` if the block does not compile with the ISO XSD (E-1,
  ADR 0048).
- It runs as Step 6.1, right after every step that writes a candidate: Step 6
  of `build-all`, `apply-context-delta` in the incremental path and
  `refine-spec` in the minor path. A candidate without its XSD does not go on
  to Step 7.
- `check-dash-conformance` compares the file byte for byte with the block of
  the spec next to it, in `output/` and `dist/`, and gives `FAIL` if they
  differ. Promotion copies both together and rewrites `dist/inputs.sha256`.

## Consequences

- The file is identical to the block by construction; the identity check
  catches what happens after the build (a promotion that copied one and not
  the other, a hand edit to either).
- `CLAUDE.md` changes: `output/` holds the candidate and its XSD, and `dist/`
  adds `sgai-extension.xsd` to its unversioned names.
- Discarded: having the LLM write the XSD as a separate output.

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-3, and measurement 4.

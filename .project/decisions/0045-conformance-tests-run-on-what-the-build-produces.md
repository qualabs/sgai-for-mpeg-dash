---
id: "0045"
title: Conformance tests run on what the build produces, not on a separate document
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0045: Conformance tests run on what the build produces, not on a separate document

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

Levels 1 and 2 of the conformance tests need documents to run on. Test
documents written by hand in parallel would be a second copy of what the spec
says, and would fall out of sync at the first build. The published spec holds
84 XML blocks: 52 complete MPDs, 23 `svta:OverlayList`, 1 extension XSD
(§5.10.1), 2 VAST (IAB) and 6 fragments (`Period`, `OverlayPresentation`,
`RenderableAsset`, `Tracking`, `ClickThrough`, `Metrics`).

## Decision

- The subject of levels 1 and 2 is two build products: the extension XSD
  (ADR 0047) and the example documents the spec gives, extracted from its
  markdown (the 84 `xml` blocks, and the example request URLs for I-REQ). No
  hand-written test documents are maintained.
- A construction the spec defines without an example is a coverage finding:
  the report lists each construction with the instances that cover it, and one
  with none is `NOT_VERIFIABLE — sin instancia en la spec`. The fix is for the
  build to add the example, through `context/` or the build prompt.
- The list of constructions comes from code: the elements and attributes the
  extension XSD declares, the `schemeIdUri` values in the blocks, and the 75
  elements of the "Interfaces" index of `context/03`. The audit's inventory
  (K-1…K-37) is used only for comparison in T-11.
- A fragment whose root is a global element of either XSD is validated;
  otherwise it is `NOT_VERIFIABLE — fragmento sin raíz validable`. No wrapping
  document is built by hand. VAST is IAB and is `NOT_APPLICABLE`.

## Consequences

- Tests follow the spec by construction: whatever a build publishes is what
  gets tested.
- Missing examples surface as coverage findings rather than as tests to write.
- Discarded: hand-maintained test documents, and wrapping fragments in a
  hand-built document (that would validate something the spec does not say).

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-1, and measurement 4.

---
id: "0048"
title: DASH conformance of the extensions is proven by four code checks together
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0048: DASH conformance of the extensions is proven by four code checks together

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

"Conforming to DASH" means what §5.2.1 asks: our additions hang only from the
extension points DASH opens, and removing them leaves a valid DASH document.
No single check proves that. The ISO XSD alone does not see errors in our
extensions: its `##other lax` wildcard accepts anything from an unknown
namespace, so a `bogusAttr` on `svta:ClickThrough` inside an MPD passes with
the ISO XSD alone and fails only with the extension XSD loaded too (measured
2026-11-23).

## Decision

Level 1 conformance of the extensions is four code checks:

- **E-1 — The XSD compiles with the ISO 6th-edition XSD.** Proves every
  reference to DASH resolves and there are no particle conflicts with the
  `##other` wildcards. It does not prove placement.
- **E-2 — The XSD does not touch the DASH namespace.** Static check:
  `targetNamespace` other than `urn:mpeg:dash:schema:mpd:2011`, no
  `xs:redefine`, `xs:override` or `xs:include` of DASH, no declarations in its
  namespace.
- **E-3 — It hangs only from extension points.** Each example document
  validates against both XSDs together; an element of ours where DASH does not
  open one is a `FAIL` with its XPath. Wildcards differ by type (for example
  `EventStreamType` admits foreign elements and not attributes,
  `ImportedMpdType` attributes and not elements: DR-2).
- **E-4 — Removing ours leaves valid DASH.** The §5.2.1 sentence as a test:
  *"the MPD shall be authored such that, after XML attributes or elements in
  the other namespaces than the DASH namespace are removed, the result is a
  valid XML document formatted according to that schema and that conforms to
  this document"*. Every foreign element and attribute is stripped and the
  rest is validated against the ISO XSD alone and the rules of ADR 0049.

Each has a negative (ADR 0054): a DASH type referenced by a nonexistent name
(E-1), a declaration in the DASH namespace (E-2), an attribute of ours on an
`EventStream` (E-3), and an `AdaptationSet` placed inside an element of ours
in a `Period` left without one (E-4).

## Consequences

- E-4 is also the document part of the `context/07` §4 and §5 invariant; the
  playback part belongs to level 3 (ADR 0051).
- E-3 covers what the examples exercise; the rest is a coverage finding
  (ADR 0045).

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-4, and measurement 4.

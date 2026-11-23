---
id: "0054"
title: Positives and negatives come from references independent of what is checked
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0054: Positives and negatives come from references independent of what is checked

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

A rule transcribed wrongly can pass what it violates, and a rule too strict can
fail what is valid. The checks need references that do not come from the
checks themselves. ISO's 6th-edition zip carries 41 example MPDs; the four
injections measured 2026-11-23 (an unknown DASH element in `Event`,
`Event@id="one"`, an invented `OverlayList@family` token, `bogusAttr` on
`svta:ClickThrough`) each failed as expected with both XSDs loaded.

## Decision

- **Positives.** For level 1, ISO's 41 examples MUST give `PASS` or
  `NOT_APPLICABLE` in the XSD, in E-4 and in every rule of ADR 0049; a rule
  failing on an example of the standard itself is badly written. Level 2 has no
  equivalent external reference: the positives are the spec's examples, and a
  rule failing on them is a finding investigated both ways (the rule or the
  example).
- **Negatives.** One deliberately broken document per rule and per E of
  ADR 0048, derived with a single change from a spec example or its XSD (ours,
  committable; ISO's are not, ADR 0046), with the expected result written
  beside it: the rule, the clause or criterion, and the XPath where it must
  fail. The test passes only if the `FAIL` comes from that rule at that place;
  a negative that stays green, or fails through another rule, is a finding.
  The four measured injections are the first four.

## Consequences

- The negatives are at once the mutation campaign for the rules and half of
  the demo (ADR 0056).

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-10, and measurement 4.

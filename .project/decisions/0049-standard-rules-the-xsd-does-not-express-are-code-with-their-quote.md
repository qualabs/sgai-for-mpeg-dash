---
id: "0049"
title: The standard's rules the XSD does not express are code with their quoted sentence
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0049: The standard's rules the XSD does not express are code with their quoted sentence

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

Much of what DASH requires of a document is not in its XSD (cardinalities,
combinations, profile constraints). The project has already curated those
rules against the primary copy in `context/08-dash-extension-rules.md`
(DR-1…DR-10) and `context/07-backward-compat-checklist.md`, and the published
audit quotes further sentences. The verdict must come from deterministic code,
never from an LLM.

## Decision

- A rule catalogue in Python, one rule per sentence of the standard, on the
  `tests-de-planos` mould: `id`, clause, the sentence quoted verbatim
  (verified against the primary copy; never pages), what it applies to, and a
  function returning a result per instance with its location.
- Sources, in order: `context/08` rule by rule (what each checks and what
  stays `NOT_VERIFIABLE` is fixed per rule in the design's table; DR-8 checks
  nothing because it is about what the spec text may promise about a Player);
  `context/07` (§1, §2, §4 are E-3/E-4; §5 is E-4 plus level 3; §6 is checked
  against `context/06-naming-and-namespaces.md`; §3 and §7 ask for prose and
  are `NOT_VERIFIABLE`); and the sentences quoted in the published audit rows
  that are document properties (for example K-4, K-14, K-15), taken as a
  source of sentences, not of verdicts.
- A rule whose sentence is not found in the primary copy does not enter the
  catalogue: it goes to the task report as `[fetch-failed]` with what was
  searched.
- An LLM may propose sentences or draft a rule; what enters is reviewed code,
  and what decides is its execution.

## Consequences

- The source is what the project already curated, not a new reading of the
  standard.
- What cannot be judged from a document is reported `NOT_VERIFIABLE` with its
  reason and does not count as passed.

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-5.

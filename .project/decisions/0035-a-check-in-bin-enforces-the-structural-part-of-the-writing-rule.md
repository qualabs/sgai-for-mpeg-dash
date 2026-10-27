---
id: "0035"
title: A check in bin/ enforces the structural part of the writing rule
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0035: A check in bin/ enforces the structural part of the writing rule

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

The writing rule (ADR 0034) has a structural part, which has a syntactic
signature, and a part of meaning, which does not. A prompt can be reasoned
around; a non-zero exit cannot.

## Decision

`bin/check-context-interfaces.py`, Step 0.7 of `build-all`, with the exits of
the other checks (`0`, `1`, `2`, `64`). It detects:

- an index row pointing to a criterion that does not exist;
- an element in two rows, or in two interfaces;
- an index row pointing to a criterion whose role is the Player, rather than
  Publisher, APS or spec document;
- a retired id cited anywhere in `context/` outside the "Retired identifiers"
  table;
- an id missing from 03 that the retired table does not list, compared against
  the commit on which the obligation map was frozen, named as a constant (not
  v12.6: R5.9, R13.8 and R34.5 to R34.10 were born after it, are cited by 04
  and ADRs 0022 to 0028, and three of them retire).

It does not detect, and cannot: two criteria saying the same with other words,
a deducible Player criterion, prose restating semantics, or an element that
exists in the document and nobody put in the index.

## Consequences

- `check-context-coherence` has to know the retired table, or it reads the
  retired ids as references to nothing.
- The check is proven by breaking each of its five conditions on purpose.

## Alternatives considered

**A heuristic warning** ("a Player criterion names an element of the index,
review it"). Rejected: it would flag nearly every legitimate behaviour
criterion, and a list nobody reads is how a check dies.

## Links

- ADR 0034, ADR 0036; DESIGN.md D-9.

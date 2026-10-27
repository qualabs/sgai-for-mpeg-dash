---
id: "0038"
title: A rewrite of context/ is validated at context level, by an agent other than the rewriter, against the obligation map
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0038: A rewrite of context/ is validated at context level, by an agent other than the rewriter, against the obligation map

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

No build protects a rewrite: the degradation comparison of
`check-incremental` skips the units the delta touched, so it would not look at
exactly the criteria that change, and the incremental path on v12.6 already
ended in `MAJOR RECOMMENDED`.

## Decision

The work is four steps: the obligation map (each id, its action and its new
place) frozen on a named commit; the rewrite; the check of ADR 0035; and the
validation, by an agent that did not rewrite, comparing the old version with
the new:

- every modal of every old unit, criterion or prose, is at its new place with
  the same strength; a script lists the pairs and the validator reads them,
  proven by deleting an obligation on purpose. The three changes this design
  decides (ADRs 0040, 0041, 0043) are accepted only at their place;
- 04 and 99 change only ids: their diff, with old ids replaced by their
  destination, is empty, proven by changing one word on purpose;
- the doubles of the v12.6 redundancy review and the three R34 pairs are gone,
  one by one;
- the three interfaces are complete;
- `check-context-coherence`, `check-context-vocabulary` and the new check exit
  `0`.

## Consequences

- `check-incremental degradation` does not apply: v13 is a major.
- The population of `check-promotable` drops from 199 to 164 criteria and
  changes in the 32 prose units; the evidence records old and new and explains
  the difference by the map.
- With the validation green this work ends; build and promotion belong to
  `major-build-v13`.

## Links

- ADR 0039; DESIGN.md D-12.

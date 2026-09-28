---
id: "0021"
title: The questions this edition leaves open are the three another body decides
status: accepted
scope: core
date: 2026-09-28
supersedes: null
superseded_by: null
---

# ADR 0021: The questions left open are the three another body decides

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

The published specification lists thirteen questions in its section
"What this edition leaves open", most of them with a provisional answer.
The "Deliberately open" register of `../../context/03-requirements.md` was
empty, so none of those silences was recorded as chosen, and a reader
could not tell a provisional answer from a settled one.

## Decision

Nicolás Levy, 2026-09-28: a question stays open only when its answer
depends on someone other than this project. Three do:

1. **Whether an SGAI event stream makes a Period non-conforming under the
   Advanced Linear profile.** The base names only its own schemes in the
   profile's restricted set of events (ISO/IEC 23009-1:2026 §8.13.2.2),
   and its own Advanced Linear example carries a scheme that list does
   not name. Only the base specification's editors can say whether the
   list is exhaustive. Decided by MPEG.
2. **Whether the empty resolution document is a conforming Media
   Presentation under the List profile.** The base admits a
   zero-duration Period with no Adaptation Set, and also requires a
   Representation in each Period for profile conformance (§8.1). The
   base is split, and only its editors can reconcile it. Decided by
   MPEG.
3. **The `svta` URN namespace identifier** of the scheme URIs is not a
   registered formal URN namespace; the base asks only for URN or URL
   syntax. Registering the identifier, or moving to a URL under an SVTA
   domain, is SVTA's decision. Decided by SVTA.

The other ten are closed with the answer the specification already
gives, and each answer is written in `context/` as a requirement or as
text.

## Consequences

- The register of `03-requirements.md` carries exactly these three rows,
  each pointing here.
- A row leaves the register when the body named above decides; the
  decision is then written in `context/` and a dated note is added here.

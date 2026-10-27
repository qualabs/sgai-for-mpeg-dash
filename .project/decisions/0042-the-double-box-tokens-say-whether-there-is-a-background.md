---
id: "0042"
title: The two double-box tokens say whether there is a background
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0042: The two double-box tokens say whether there is a background

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R26 says the background is optional, and there are two tokens,
`squeezeback-double-box` and `squeezeback-double-box-background`. Nothing says
whether the first may carry a background, or the second may lack one.

## Decision

The token says the composition: `squeezeback-double-box-background` carries
a background, `squeezeback-double-box` does not. It goes in R12.5 and R26.1.
Decided by Nicolás Levy, 2026-10-27.

## Consequences

- UC-10 already illustrates it (*"the first token is the case with no
  background, the second the case with an advertiser background"*), so 04 does
  not change.

## Links

- DESIGN.md D-15; `context/03-requirements.md` — R12, R26; `context/04-use-cases.md` — UC-10.

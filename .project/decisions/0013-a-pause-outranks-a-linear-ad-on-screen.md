---
id: "0013"
title: A pause ad outranks a linear ad that is on screen, and this decision is weakly grounded
status: accepted
scope: core
date: 2026-09-17
supersedes: null
superseded_by: null
---

# ADR 0013: When a pause lands on a linear ad, the pause ad wins

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R17 settles the cross-family priority between a pause ad and an
overlay: during a pause the pause ad is the only ad surface and the
overlay is suspended. It says nothing about a **linear** ad, because
R22 and the concurrency rules bound the non-linear families only.

The case is reachable and ordinary: a linear break or a hybrid break
overlaps a pause opportunity window, and the viewer pauses while the
linear ad is on screen. Nothing in the specification authorised a
composition, and nothing forbade one either. The outcomes differ by a
whole ad.

## Decision

**The pause ad wins.** The Player presents the pause ad and suspends
the linear ad, resuming it where it was suspended when the viewer
resumes. This is carried as R17.5, which extends R17's cross-family
priority to the linear family.

## The grounding is weak, and it is recorded rather than disguised

There is no strong argument behind it. The reasoning available is
that the pause ad is the form whose trigger the viewer just produced,
and that R17 already gives the pause family priority over the other
family it meets — so giving it priority here is the consistent
extension rather than a new principle. That is a consistency argument,
not a reason drawn from what serves the viewer or the Publisher.

It is written down this way on purpose. A decision that admits it is
weak can be argued with; one that presents a consistency argument as a
justification cannot, because the reader cannot see where to push.

**What would change it**, and each of these is a reason to reopen:

- Evidence that a suspended linear ad is not counted as delivered by
  the measurement the Publisher bills on. Then the decision costs a
  paid impression to serve an unpaid surface, and the cost is concrete
  where the argument above is not.
- A Publisher who wants to protect a linear break explicitly. Today
  nothing in the specification lets them say so, and R17's priority is
  deliberately not Publisher-configurable; that choice was made for the
  overlay case and inherited here without being re-examined.
- A working-group position. This is the kind of question where the
  conventions of the rest of the industry matter more than an
  argument built inside one specification, and there is no reading of
  those conventions in the record yet.

## Alternatives considered

**The linear ad wins and the pause ad is not presented.** Defensible on
the revenue argument: a linear ad is sold against a break and a pause
ad is opportunistic. Not chosen, but the first bullet above is the
evidence that would make it right.

**Compose both.** Rejected on R22's grounds — the decoder budget the
whole non-linear design is built around — and on what it does to the
screen.

## Consequences

R17.5 states the Player behaviour. This ADR is where the weakness
lives, so that a future reader does not reconstruct a rationale that
was never there.

A GitHub issue taking the question to the working group is drafted at
`.project/phases/05-wg-feedback-round-2/github-issue-draft-pause-vs-linear.md`
and has not been published.

---
id: "0016"
title: Linking the two portions of a hybrid break is out of scope, and stays with the ADS
status: accepted
scope: core
date: 2026-09-21
supersedes: null
superseded_by: null
---

# ADR 0016: Cross-portion linkage in a hybrid break is out of scope

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

UC-04 describes a **hybrid break**: a linear ad takes the screen and a
non-linear overlay is composited on top of it during the same break. The
two portions belong to one break and are **selected independently** — the
ADS picks the linear ad and the overlay separately.

The open question was whether the Publisher may declare a constraint that
links them: *"if the linear ad is from advertiser X, suppress the
overlay."*

**The case behind it is commercial and real.** An advertiser who bought
the full screen does not want another advertiser's overlay on top of it,
least of all a competitor's; and a Publisher may want to promise that
exclusivity to whoever paid for the linear portion.

Today nobody can express it. The Publisher declares what may be shown in
the slot but does not know who will fill each portion, because the ADS
decides that afterwards; and the ADS selects each portion without knowing
what it selected for the other. Both answers are consistent with the
four-actor model, which is why UC-04 recorded that the specification had
to pick one.

## Decision

**Out of scope.** This specification does not provide a way to declare a
constraint between the portions of a hybrid break. Exclusivity and
competitive separation stay where they already are: in the commercial
agreement and in the ADS's configuration.

## Why

**It would force the advertiser's identity down to the Player.** For a
Player to enforce "not together with X", it has to know that this ad is
X's. That puts commercial data into the technical contract, and the
Player is precisely the actor that today knows nothing about who bought
what. The specification's Player-facing contract is about what may be
rendered, not about who sold it.

**The ADS already owns this, by name.** R2 assigns targeting, frequency
capping, brand-safety filtering and **competitive separation** to the
ADS. Adding a second place where the same thing is decided creates two
authorities over one outcome, and the day they disagree nothing says
which one wins.

**And the asymmetry favours declining.** Saying no today and adding the
capability later is additive: nothing written against this edition
breaks. Saying yes and removing it later breaks every implementation
that relied on it. When two answers are both defensible and only one is
reversible, the reversible one is the cheaper mistake.

## What this does not decide

It does not say the need is illegitimate — it says the manifest is the
wrong place for it. A Publisher who wants that guarantee gets it from the
ADS, which is the actor that knows about advertisers, competitors and
exclusivity, and which already carries the responsibility.

Nor does it forbid a future edition from revisiting it. What such an
edition would have to solve first is the question this one declines to
answer: how an advertiser's identity reaches the Player without turning
the Player-facing contract into a commercial one.

## Alternatives considered

**Let the Publisher declare the linkage and have the Player enforce it.**
The reading that prompted this decision, rejected on the grounds above.

**Let the Publisher declare it and have the APS enforce it.** Better
placed — the APS already sits between the ADS and the Player — and still
rejected: the APS converts a decision, it does not make one. Giving it
authority to drop a portion the ADS selected makes it a second decider,
which is the same defect one layer down.

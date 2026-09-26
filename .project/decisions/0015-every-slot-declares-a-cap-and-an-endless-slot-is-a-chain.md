---
id: "0015"
title: Every slot declares a cap, and an endless slot is written as a chain of slots
status: accepted
scope: core
date: 2026-09-21
supersedes: null
superseded_by: null
---

# ADR 0015: Every slot declares a maximum duration

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

The base standard treats an absent `@maxDuration` as infinity: *"in which
case the current presentation resumes only when the alternative
presentation terminates"* (§5.16.5). R4.1 narrows that — every ad slot
declares a cap — and R4.8 records the narrowing as deliberate.

R4.10 then answers what a Player does when a slot arrives without one
anyway: it presents no ads from that slot and continues with the primary
content. **That criterion was written as provisional**, open with the
working group rather than settled, and published as issue #9 on the
project repository. This ADR closes it.

The question was never whether the narrowing is legal. It is what a
profile does, and §8.1 permits exactly this: restricting which documents
conform without changing any construct's semantics. The question was
whether an unbounded slot is a capability worth keeping.

## Decision

**Every slot declares a maximum duration. A slot without one is not a
slot this specification defines, and no ad is presented from it.**

A publisher who genuinely wants advertising with no fixed end writes it
as a **chain of bounded slots**: N slots of X seconds each, placed along
the primary content. Nothing in this specification prevents that, and it
requires no new construct.

## Why the capability is not kept

The unbounded slot is a rare edge case that **the chain already covers**,
so keeping it buys no capability. What it costs is not rare: every
requirement written against a cap acquires a second reading for the case
where there is none, and that second reading has to be specified,
implemented and tested by everyone, for a shape that almost nobody
authors.

That trade is the whole argument, and it is worth stating in the form it
was decided in: *"incluir en la norma hoy algo para contemplar slots de
duración infinita implica agregar lógicas y casos borde complejos para
cosas que seguramente no se usen normalmente."*

**The failure mode of this decision is visible and cheap**, which is what
makes it safe. A Publisher who omits the attribute sells nothing from
that slot — they notice, and the fix is one attribute. The failure mode
of the alternative is an advertisement that runs for as long as it likes
in front of a viewer, which is neither visible to the Publisher nor
cheap.

## What this does NOT change: the pause family

**A pause slot has no authored duration, and this decision does not give
it one.** R31 already settles that a pause opportunity window bounds
*where* and not *how long*: the slot lasts exactly as long as the viewer
stays paused, which is unknown when the document is authored. R31.2
states that R4's cap does not bound a pause slot, and that stays true.

The two are compatible because they answer different questions. R4.1
governs what the Publisher **declares**; R31.2 governs what that
declaration **bounds** in one family. A cap on a pause slot is declared
like any other and bounds nothing, because there is no authored duration
for it to bound — the viewer supplies it.

Making the cap bound something in the pause family was considered while
this decision was being taken, on the argument that an attribute which
binds nowhere is decorative. It was rejected: it would reopen R31, whose
reasoning is that the pause duration belongs to the viewer and to no one
else.

## Alternatives considered

**Keep the base standard's unbounded default.** Rejected: it makes R4's
Player-side enforcement inert for exactly the slots whose declaration is
defective, which is the opposite of what an enforcement rule is for.

**Make the cap optional and default it to a fixed value.** Rejected on the
same grounds as the first, plus one of its own: a default nobody authored
is a number the Publisher never chose, and the Publisher is the actor this
specification puts in charge of what may be shown.

**Exempt the pause family from R4.1.** Rejected: it adds a per-family
special case to the one requirement whose value is that it has none, and
the reason for the decision above was to avoid exactly that kind of
branch. Declaring a cap that bounds nothing costs one attribute; a
carve-out costs a reading of R4.1 in every family.

## Note — 2026-09-26

ADR 0020 supersedes the linear part of this record. R4.1 and R4.10 now
bind the overlay and pause families only; an inherited linear event
keeps the base default, under which an absent `@maxDuration` is
unbounded (R4.8). The argument that the failure mode is visible and
cheap holds for an ad slot and not for a blackout, which the base
standard carries on the same events and which R4.10 would have skipped.
The non-linear decision, the chain of bounded slots and the pause family
are unchanged.

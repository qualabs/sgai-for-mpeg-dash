---
id: "0006"
title: Adopt the DASH execution model where it already answers, and declare an extension only where it does not
status: accepted
scope: core
date: 2026-09-16
supersedes: null
superseded_by: null
---

# ADR 0006: Adopt the DASH execution model where it already answers

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

Auditing v7 against the published Sixth edition surfaced several places
where this specification defines runtime behaviour that MPEG-DASH had
already defined, and defined differently. Two examples carried the
discussion:

- Whether an opportunity that resolved with no ads survives and can be
  attempted again. DASH answers it with the `E.c` counter: a failed
  execution does not increment it, so the event remains executable.
- Whether the Publisher-declared cap bounds *how long an ad runs* or
  *when the slot ends*. DASH answers it with `@clip`, whose default
  fixes the end of the slot, so a late start shortens the ad. This
  specification had been written the other way, which is the behaviour
  DASH assigns to the non-default.

These were not isolated. Each one could have been settled on its own
merits, and each settlement would have been an independent judgement
call that the next case would not inherit.

## Decision

**Where MPEG-DASH already answers a runtime question, this
specification adopts its answer and cites it. Where MPEG-DASH does not
answer, this specification defines the behaviour and declares it as an
extension.**

An exception to the first half is admissible, and MUST be written as an
exception with its reason — not as a silent divergence. The first such
exception is recorded in ADR 0008.

## Alternatives considered

**Decide each case on its merits.** Rejected: it produces a
specification whose runtime model is a sequence of local judgements
with no stated relationship to the base standard, and it gives the next
case no guidance. The cost of the criterion is that it sometimes
adopts an answer we would not have chosen; the cost of the alternative
is that nobody can predict what we would choose.

**Define our own model throughout and treat DASH as a transport.**
Rejected: the constructs this specification extends are DASH
constructs, executed by DASH clients. A Player implementing the base
standard will apply the base semantics to the same document. Writing a
parallel model does not replace those semantics; it contradicts them,
and the same bytes then produce two behaviours depending on who reads
them — which is what a specification exists to prevent.

## Consequences

Two adoptions follow directly: the opportunity survives an empty
resolution, and the cap means "until when" wherever DASH defines a
scheduled moment and "how long" elsewhere. The asymmetry in the second
is not an exception: `@clip` exists only for replacement because an
insertion has no original slot end to preserve.

The criterion also bounds where it applies. DASH's execution model is
built on a scheduled presentation time; the overlay and pause-ad
families have none, so most of the model does not reach them. Where
this specification writes behaviour for those families, it is defining
rather than adopting, and says so.

One collision the criterion does **not** resolve is recorded separately:
DASH treats an empty resolution as an execution failure and proceeds to
the next queued event, while R20.1 and UC-12 require the Player not to
fall through. That is a decision of this project against another
decision of this project, and the criterion does not adjudicate it.

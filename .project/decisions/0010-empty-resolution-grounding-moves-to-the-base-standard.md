---
id: "0010"
title: The empty-resolution decision is grounded in the base standard, which already covers the case
status: accepted
scope: core
date: 2026-09-16
supersedes: null
superseded_by: null
---

# ADR 0010: Empty resolution — the grounding moves to the base standard

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

ADR 0005 settled that an unfilled opportunity is expressed as a
resolution document carrying no candidates, not as an HTTP status
code. That decision stands and is not reopened here.

What ADR 0005 could not state, because the project was working against
the FDIS draft at the time, is that **MPEG-DASH already covers the
case**. §5.16.2.2.6 lists "Alternative MPD is a List MPD, and merge
process resulted in no available media" among the conditions under
which an event's execution produces no alternative presentation, and
prescribes the outcome: "A failed execution results in smooth
continued playback of the main media presentation."

The same clause places an event whose `@executeOnce` has already fired
under the same heading — a case that is correct by design. "Execution
fails" in DASH therefore means "this event produced no alternative
presentation this time", not "something went wrong".

## Decision

**The decision of ADR 0005 is unchanged. Its grounding moves**: the
Player behaviour R30 describes is the base standard's own, cited, and
R30 names the case from the APS side rather than defining new Player
behaviour.

Two consequences that ADR 0005 left open are now settled by ADR 0006's
criterion:

- **The opportunity is not consumed.** DASH does not increment the
  execution counter on a failed execution, so the event remains
  executable. This was never stated in `context/`; the assertion that
  it was consumed existed only as an inference from the
  first-window-wins rule.
- **What "carrying no candidates" means** is now stated positively: a
  well-formed, complete document carrying no ad candidate — not an
  empty body, not a `204`, not a `404`, and not a document that fails
  to parse.

## Alternatives considered

**Rewrite ADR 0005.** Rejected: a decision record is a record. The
decision was correct and was taken with the information available; the
information changed. Rewriting it would destroy the only evidence that
the project was working against a draft, which is the fact that
explains several other findings of the same day.

## Consequences

One collision remains open and is explicitly not settled here. DASH
treats an empty resolution as an execution failure and proceeds to the
next queued event; R20.1 and UC-12 require the Player not to fall
through to a subsequent overlapping window. ADR 0006's criterion does
not adjudicate it, because it is a decision of this project against
another decision of this project.

*Closed on 2026-09-17 by ADR 0011, in favour of the base standard's
model. The text above is left as it was written.*

---
id: "0011"
title: An empty resolution is a failed execution and falls through to the next overlapping window
status: accepted
scope: core
date: 2026-09-17
supersedes: null
superseded_by: null
---

# ADR 0011: An empty resolution falls through to the next window

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

ADR 0010 closed by naming a collision it could not adjudicate:

> DASH treats an empty resolution as an execution failure and proceeds
> to the next queued event; R20.1 and UC-12 require the Player not to
> fall through to a subsequent overlapping window. ADR 0006's criterion
> does not adjudicate it, because it is a decision of this project
> against another decision of this project.

The base standard's position is not ambiguous. ISO/IEC 23009-1:2026
§5.16.2.2.6 lists, among the conditions under which execution fails,
*"Alternative MPD is a List MPD, and merge process resulted in no
available media"* — a document that resolved and yielded nothing. And
§5.16.2.2.5 step 2 prescribes what follows a failure: *"If execution
fails, steps a-c above are repeated for next events in QE"*, until
execution succeeds, the next event's presentation time is in the
future, or the queue is empty. Only then: *"If no event can be
successfully executed, the playback continues uninterrupted."*

What R20.1 said until now was the opposite: a well-formed document
carrying no candidates was *accessible*, the opportunity had resolved,
and the Player was forbidden from attempting the fallback window.

## Decision

**The base standard's model is adopted.** A resolution attempt that
produces no ad is a failed execution, whatever shape the failure took,
and the Player attempts the next overlapping window of the same family.
A well-formed resolution document carrying no candidates is one of
those shapes, indistinguishable at the Player from a window that could
not be reached at all.

**The rationale is behavioural equivalence with the base standard, not
a product argument.** In Nicolás Levy's words: *"Adoptemos el modelo
que dice éste. Tomemos el documento vacío como que va a ir a la
próxima, al fallback, si es que lo tiene. Así nos comportamos
exactamente igual."* The reason to prefer fall-through is not that it
fills more inventory; it is that a Player implementing this
specification and a Player implementing the base standard should not
diverge on the same manifest.

**Scope.** For the linear family the rule is adopted unchanged and
cited. For the non-linear families the base standard does not reach —
its execution model is built on Alternative MPD events, which overlay
and pause-trigger windows are not — so this specification extends the
same rule to them and declares the extension, exactly as R20.3 does for
ordering. This is ADR 0006's criterion applied.

## Alternatives considered

**Keep R20.1 as it stood: an empty document ends the chain.** The
argument was real and is recorded here because it lost on a different
axis, not because it was weak: a window that answered with no
candidates did not fail — the market was asked and did not buy — and
walking the Publisher's backup windows after a legitimate answer turns
a decision into a retry. On that reading, fallback windows exist for
*unreachable* APSs, and spending them on *unsold* ones empties the
chain before the case it was declared for arrives.

It was rejected because the criterion in force is behavioural
equivalence with the base standard (ADR 0006), and the base standard
puts both cases under one heading. Keeping the distinction would have
meant a Player conformant to this specification behaving differently
from a Player conformant to DASH on a manifest both accept — the
divergence ADR 0006 exists to avoid. The commercial argument is not
refuted by this decision; it is outranked by the criterion.

**Adopt fall-through for linear only, and keep the old rule for
non-linear.** Rejected: it would leave two behaviours for one authoring
shape, which is the outcome R20.3 rejected for ordering four
paragraphs earlier, and an implementer would have to learn both.

## Consequences

- **R20.1 is rewritten** and now carries the citation inside the
  requirement rather than in a note, per the instruction that a
  requirement aligned to the base standard should say so and say where.
  Each way an attempt can fail is mapped to the §5.16.2.2.6 condition
  it corresponds to.
- **R30 keeps its decision and loses a claim.** Expressing an unsold
  opportunity as a document rather than an error stands, and is what
  R30 is about. What it can no longer say is that the distinction makes
  no difference to playback: where a fallback window exists, it now
  does. Its title changed for the same reason.
- **UC-12's first path is inverted**, and its scenario now demonstrates
  the fallback being used after an empty answer rather than being left
  untouched.
- **The opportunity is still not consumed.** §5.16.2.2.6 NOTE 3 states
  that the execution counter is not incremented on a failed execution,
  so R30.2 is unaffected — and better grounded than before, since the
  empty case is now explicitly one of the failures that clause
  describes.
- **One adjacent case is deliberately not decided.** A resolution
  document that carries candidates, none of which the device can
  render, is governed by R5.3 and R5.7 and ends at the primary content.
  The base standard's condition is media availability after the merge,
  not renderability on a device, and this decision does not extend it
  there.

## Links

- ADR 0005 — an unfilled opportunity is expressed as a document, not an
  HTTP status code. Unchanged: this decision is about what follows from
  that document, not about its shape.
- ADR 0006 — adopt the base standard's execution model where it
  answers. The criterion this decision applies.
- ADR 0010 — the grounding of the empty-resolution case moves to the
  base standard. This decision closes the collision ADR 0010 recorded
  as open.
- `context/03-requirements.md` — R20.1, R20.3, R30.
- `context/04-use-cases.md` — UC-12.

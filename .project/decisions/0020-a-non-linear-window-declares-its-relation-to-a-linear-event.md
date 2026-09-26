---
id: "0020"
title: A non-linear window declares whether it supersedes the linear event it overlaps or sits on top of it, and by default does neither
status: accepted
scope: core
date: 2026-09-26
supersedes: "0012 (in part), 0015 (in part)"
superseded_by: null
---

# ADR 0020: A non-linear window declares its relation to a linear event

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

The base standard carries advertising and blackouts through the same
alternative-presentation events and gives a Player no way to tell them
apart. §5.16.1 describes the tool as *"the ability to switch between two
independent Media Presentations, for applications such as pre-roll and
mid-roll advertisement, as well as blackouts, during a live streaming
session"*. Neither event scheme defines a value space for
`EventStream@value` (*"This value is currently not required"*, Table 59;
*"This value is currently not used"*, Table 61), and no attribute of the
events says what the alternative presentation is (Tables 62 and 63).
ADR 0012 drew the consequence: whether a replacement is an ad is not
observable, and no rule may depend on it.

Two things followed from that, and both were wrong in a way the owner
considers important:

1. **Two ads at the same spot.** A VOD Publisher following UC-07 authored
   a base linear break as the legacy fallback and an SGAI non-linear
   window over the same span. `context/` said the break was *"simply
   ignored by current Players that take the richer SGAI path"*, but no
   requirement made a Player ignore it; R22's informative text said
   stacking a linear and a non-linear ad was permitted and asked
   Publishers to *"be careful"*. A Player of this specification would
   play the break and composite the overlay on top of it.
2. **A blackout that is not honoured.** R4.10 made a Player present
   nothing from a slot declared with no maximum and continue with the
   primary content, and R4.1 required every slot, linear included, to
   declare one. A blackout with no known end is written, in the base
   standard, as a replacement with no `@maxDuration`: *"If absent, the
   value is assumed to be infinity, in which case the current
   presentation resumes only when the alternative presentation
   terminates"* (§5.16.5.2, Table 63). R4.10 made a Player of this
   specification skip it and show the programme the Publisher had
   blacked out. ADR 0015's argument that *"the failure mode of this
   decision is visible and cheap"* holds for an ad slot, which then sells
   nothing; it does not hold for a blackout, whose failure is a rights
   breach nobody sees until it has happened.

## Decision

**The Publisher knows what each event is, and declares, on the
non-linear window, the one fact the Player needs.** The declaration
travels on this specification's own window; which construct carries it
is the build's, weighed against the alternatives listed in
`context/06-naming-and-namespaces.md`. R40 in `context/03-requirements.md`
states it.

**Default — nothing declared.** A non-linear window is presented only
over the content of the presentation whose MPD declares it. It does not
replace an inherited linear event and is not composited over an
alternative presentation. Two ads never happen by accident. This rule
does not reintroduce the objection of ADR 0012: it depends on whether an
alternative presentation is **active**, which a Player of this
specification knows because it executes it, and not on whether that
presentation is an ad, which nobody can observe.

**Case 1 — supersede.** Where a base linear event is an ad and an SGAI
non-linear window covers the same span, the window MAY declare that it
supersedes the event. A Player of this specification presents the
window and does not execute the event; when the window presents no ad —
its resolution fails, returns no candidates, or offers nothing the
device can render — the Player executes the event as the base standard
defines. A legacy Player does not know the window and plays the event as
always, so the break is the legacy fallback. The preference for the
non-linear ad is the point of offering one. In Nicolás Levy's words:
*"si puedo hacer no lineal prefiero no lineal ... y pongo como fallback
el otro, el lineal"*. UC-17 and UC-07 exercise it.

**Case 2 — nested.** The content of a replacement is a presentation of
its own, and an ad shown during it is declared inside that
presentation, by windows in its own MPD, because the primary content
cannot know what the replacement contains. In his words: *"el contenido
reemplazado es el que puede tener o no marcar ads ... es como otro
nivel, anidado"*. A Publisher does not use a primary-timeline window to
put an ad over an alternative presentation unless the window declares
supersede or on top. The base event always executes with its base
semantics, an unbounded replacement included. UC-14 exercises it.

**Case 3 — on top.** A hybrid break, where a linear ad and an overlay
composited over it are intended together, is declared by the window as
on top. UC-04 exercises it.

**R4.1 and R4.10 are scoped to the families this specification
defines.** The cap obligation and the refusal to present from an
uncapped slot bind overlay and pause windows. An inherited linear event
follows the base standard: its `@maxDuration` is optional and, absent,
unbounded (R4.8, R1.5).

**Case 1 is a recorded exception to R1.5**, stated in R40.8: a Player of
this specification does not execute a base event that the base standard
would execute. It is admitted because the Publisher, who authored both
the event and the window, declares it explicitly on a construct this
specification defines, and because a Player that does not implement this
specification sees exactly the base behaviour.

## Consequences

- A manifest that carries a linear break and a non-linear window over the
  same span shows one ad on every Player: the break on a legacy Player,
  and on a Player of this specification whatever the window declares —
  the non-linear ad where it can be rendered and the break otherwise
  (supersede), both on purpose (on top), or the break alone with the
  window kept to the primary content (nothing declared).
- A blackout declared with no maximum duration is honoured by every
  Player.
- Nothing is added to the base `InsertPresentation` / `ReplacePresentation`
  events. The same base event means the same thing to every Player.
- The requirement set gains R40; R4, R4.1, R4.8 and R4.10 are rewritten;
  R22's informative "not forbidden / be careful" paragraph is replaced by
  a pointer to R40; UC-04, UC-07 and UC-14 change and UC-17 is added.
- `output/` is not edited; the next build carries the change.

## Alternatives considered

**Leave it to authoring, with no declaration.** The Publisher avoids the
overlap by not writing it. Rejected: the overlap is exactly what the
UC-07 fallback and the hybrid break need, so the Publisher cannot avoid
writing it, and a Player given two overlapping constructs with no
declaration has to guess which the Publisher meant. The guess is the
two-ads outcome this decision exists to remove.

**Mark the base event** — an attribute or a value on the
`InsertPresentation` / `ReplacePresentation` event saying it is an ad,
or that it may be superseded. Rejected on two grounds. The same bytes
would behave differently on a Player of this specification and on a
Player of the base standard, giving a base construct a second meaning
(R1.3). And the linear events may be written by a packager or an
upstream system that knows nothing of the non-linear offering, so the
declaration would depend on a party that does not own the decision.

**Keep R4.10 for linear events and ask blackouts to declare a large
maximum.** Rejected: a number nobody chose, for an end nobody knows, on
a construct whose content this specification cannot see — the argument
ADR 0015 itself used against defaulting a cap.

## What this supersedes

- **ADR 0012, in part.** It rejected *"this specification does not stack
  two ads"* as a policy, because the Publisher already held the lever and
  a prohibition would take it away. That reasoning stands: nothing here
  prohibits stacking. What changes is the default: stacking now has to be
  declared (on top), and not stacking is obtained from an observable fact
  (an alternative presentation is active) rather than from a distinction
  nobody can observe. ADR 0012's decoder arithmetic and its finding that a
  replacement need not be an ad are unchanged, and are what this decision
  builds on.
- **ADR 0015, in its linear part.** Every overlay and pause slot still
  declares a maximum, an endless non-linear slot is still a chain, and
  the pause family is untouched. An inherited linear event no longer has
  to declare one: the base default stands.

## Links

- ADR 0006 and R1.5 — the base answer takes precedence; R40.8 records the
  exception.
- ADR 0012, ADR 0015, ADR 0016 (cross-portion linkage in a hybrid break,
  unchanged).
- `context/03-requirements.md` — R4, R22, R40.
- `context/04-use-cases.md` — UC-04, UC-07, UC-14, UC-17.
- `context/06-naming-and-namespaces.md` — "The window's relation to a
  linear event travels on the window".

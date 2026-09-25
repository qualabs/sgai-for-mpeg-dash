---
id: "0017"
title: Viewer dismissal is carried by a field of this specification in the resolution document, not by the base skipAfter
status: accepted
scope: core
date: 2026-09-25
supersedes: null
superseded_by: null
---

# ADR 0017: Viewer dismissal has its own carrier, not `@skipAfter`

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R35 lets the viewer dismiss a whole ad slot. The APS declares, per slot,
whether dismissal is allowed and how many seconds must pass first, and
R35.1 fixes the default: *"A resolution document that does not declare it
leaves the slot non-dismissible: the capability is granted and never
assumed."*

`context/06-naming-and-namespaces.md` requires reusing a baseline construct
*"with all its characteristics — name, default values, permitted value
domain, units, semantics"* when one covers the concept. The base
specification has a skip control in two places, and both cover part of the
concept:

- `@skipAfter` on the alternative-MPD events. ISO/IEC 23009-1:2026
  §5.16.5.2, Table 63: *"describes an offset in time (in fractional
  seconds) from the beginning of the alternative presentation till the
  moment the rest of that presentation may be skipped by the application
  in response to a user action"*, and *"Zero duration implies that
  skipping is allowed everywhere … Default value is PT0S."*
- `PlaybackRestrictions@skipAfter` in the service description. Annex K,
  Table K.9: *"The value of Inf implies that skipping is not allowed within
  the scope of this service description"* and *"The default value of 0
  implies that skipping is allowed everywhere."* Table K.18 gives the
  attribute the default `"PT0S"`.

Both defaults are the opposite of R35.1. The incremental build over v9.1
could not place R35 for that reason: reusing either construct brings its
default, and keeping R35.1 contradicts the reuse rule.

## Decision

**The dismissal declaration is a field this specification defines in the
APS's resolution document. Neither base `@skipAfter` carries it.** R35
states this, R35.8 makes it a criterion, and 06 records it as a deliberate
exception to the reuse rule, with its reason.

## Why

**The default is the decision.** R35.1 does not add a detail to the base
control; it inverts what silence means. Under the base construct a
document that says nothing is skippable immediately. Under R35 it is not
dismissible at all. A construct reused with its name and a different
default is a construct a reader will misread, because the name promises
the base behaviour.

**And R35.1 already puts the decision with the APS.** Whether a slot may be
dismissed is a property of what was sold, so it travels with the
candidates. The event-level `@skipAfter` sits in the Publisher's `MPD`, the
wrong document. `PlaybackRestrictions@skipAfter` can sit in the resolution
document, but its default still makes an APS that forgets to declare it
grant dismissal on the advertiser's behalf.

## Alternatives considered

**Reuse `PlaybackRestrictions@skipAfter` and require the APS always to
emit it.** Rejected. It keeps the base vocabulary, but the obligation to
emit the attribute becomes the only thing standing between an omission and
the opposite of R35.1. A Player that meets a document without it applies
the base default, and nothing in the document tells it that this
specification meant otherwise.

**Reuse the construct and change R35.1 to the base default.** Rejected: it
changes the product decision to fit a carrier. The commercial reading of
R35 — dismissal is granted and never assumed — is the requirement.

## Consequences

- R35 names the base constructs and states why neither is reused; R35.8 is
  the criterion.
- `context/06-naming-and-namespaces.md` records the exception next to the
  reuse rule.
- **Not decided here:** what a Player of this specification does with a
  base `@skipAfter` that a Publisher writes on an inherited linear event.
  That attribute belongs to the linear baseline this specification absorbs,
  and this decision is about where R35's declaration travels, not about
  retiring a base attribute.

## Links

- ADR 0006 — adopt the base standard's execution model where it answers.
  This decision is a case where the base construct answers a different
  question.
- ADR 0018 — the opposite outcome for R36's offset, where the base default
  is adopted.
- `context/03-requirements.md` — R35.
- `context/06-naming-and-namespaces.md` — "Naming consistency with baseline
  DASH".

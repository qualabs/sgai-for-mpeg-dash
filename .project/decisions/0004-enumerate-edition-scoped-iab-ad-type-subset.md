---
id: 0004
title: Enumerate the edition-scoped IAB ad-type subset in R12 and exclude ads outside the video surface
status: accepted
scope: core
date: 2026-07-13
supersedes: null
superseded_by: null
---

# ADR 0004: Edition-scoped IAB ad-type enumeration in R12, off-video-surface exclusion

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R12 deferred ad-type definitions to the IAB in the abstract: it stated
that the IAB defines and maintains ad types and their visual templates,
that this spec references those definitions normatively, and that
inventing new categories is out of scope. It never enumerated *which*
IAB ad types and visual placements this edition actually covers. The
complementary boundary, that ads rendered outside the video surface are
not the Player-facing SGAI contract's concern, lived only as a weak line
in `../../context/04-use-cases.md` ("Native ad integrations, ads in the
Player chrome, not in the video, out of scope") plus a separate
companion-ads bullet.

For a working group auditing the spec, that posture is under-specified.
A reader cannot tell, from R12 alone, whether a given IAB format (a menu
ad, a screensaver ad, an in-scene ad) is in or out, and the in / out
line for off-video placements was buried in the use-cases rather than
stated normatively where the ad-type contract lives. An out-of-scope
item (referred to during drafting as OOS-5, the off-video-surface
exclusion) was considered as a standalone entry, which would have split
the boundary across two places.

## Decision

R12 is reframed from an abstract deferral into an explicit,
**edition-scoped enumeration** of the IAB subset this edition supports,
plus an in-requirement exclusion of everything off the video surface.

### D-1. Explicit closed enumeration, mapped 1:1 to IAB

R12 enumerates the supported ad types and visual placements, each mapped
to its IAB ad type (identifier in `code`) and, where applicable, its IAB
visual placement. The supported set, all rendered on or within the video
surface:

- **Linear** (IAB *Linear Ad*, `linear`): pre-roll, mid-roll, and
  multi-ad breaks. Post-roll is out of scope for this edition (a
  candidate for a future phase, per `04-use-cases.md`). Full-screen
  takeover is the `linear` full-viewport rendering used as a fallback
  presentation option, not a separate ad type.
- **Overlay** (IAB *Overlay*, `overlay`): corner / bug (IAB *Corner
  Overlay*) and lower-third (IAB *Lower-Third Overlay*) are the named
  visual placements; a plain image / HTML overlay with no named
  placement is the base `overlay` type.
- **Squeezeback** (IAB *Squeezeback*, `squeezeback`): L-shape (IAB
  *L-Shape*, R27), side-by-side / double-box (IAB *Double Box Video* and
  *Double Box Video + Background*, R26).
- **Pause-ad** (IAB *Pause Ad*, `pause`): fullscreen or partial (R21).

The conformance criteria (R12.1 to R12.3) accept **exactly** the
enumerated values mapped to IAB, not "any IAB value". Publisher-declared
allowed layouts, and the APS's resolution-document form metadata, MUST
draw from this set.

### D-2. Edition-scoped snapshot, closed by design

The enumeration is a per-edition snapshot. An IAB ad type or placement
not listed is out of scope for this edition; a format the IAB publishes
later does NOT enter scope automatically. Widening the set requires a new
edition of the spec. This is deliberate scope control, not a limitation
to work around at runtime.

### D-3. Off-video-surface exclusion, stated in R12

R12 explicitly excludes any ad rendered in the Player chrome or the
application UI rather than on the playing or paused video: menu ads (IAB
*Menu Ad*: home screen, content menu, guide / EPG), home-screen /
launcher ads, screensaver ads (IAB *Screensaver Ad*), and companion /
multi-screen ads (IAB *Companion Ad*). These are application ad-
integration concerns, not the Player-facing SGAI contract. Because the
supported set is closed, anything not enumerated is already out; the
exclusion paragraph makes the off-video-surface category unambiguous.
This **subsumes the standalone OOS-5** that was under consideration; no
separate out-of-scope entry is added.

### D-4. IAB stays the owner of definitions

The principle that the IAB defines and maintains ad types and their
visual templates is preserved. This spec only **selects a subset**; it
does not re-define the formats and does not invent categories.

## Consequences

### Positive

- **Auditable scope.** A WG reader sees the exact supported set and its
  IAB mapping in one place, and the off-video exclusion is normative in
  R12 rather than buried in the use-cases.
- **Unambiguous boundary.** Not-enumerated means out-of-scope by
  definition; the off-video-surface paragraph removes any doubt for the
  chrome / application-UI category.
- **Single source for the boundary.** OOS-5 is folded into R12, so the
  in / out line is stated once.
- **IAB ownership intact.** The spec selects, it does not re-define; the
  deferral to IAB for definitions and (per ADR 0001) spatial caps is
  unchanged.

### Negative / limits

- **Per-edition snapshot.** The supported set is frozen per edition; a
  new IAB format needs a new edition to enter scope. This is accepted on
  purpose as explicit scope control.
- **Consistency debt across `context/`.** The enumeration is now the
  canonical list, so the glossary Overlay entry and the Publisher
  allowed-layouts text in `02-actors.md` were realigned to point at R12,
  and stale illustrative names outside the CTV catalogue (skyscraper,
  sidebar) were dropped from the ad-overlay context. Future ad-format
  edits MUST keep those pointers coherent with R12.
- **Post-roll excluded from this edition.** R12 supports pre-roll,
  mid-roll, and multi-ad breaks under Linear; post-roll is out of scope
  and remains a future-phase candidate in `04-use-cases.md`. The
  glossary's linear-ad definition keeps post-roll as a generic timing
  position but points to R12 for the edition-scoped set, so the
  documents no longer contradict each other.

## Links

- `../../context/03-requirements.md`: R12 (this decision), R21 (pause-ad
  fullscreen / partial), R26 (side-by-side / double-box), R27 (L-shape /
  squeezeback), R15 (admissible carriers).
- `../../context/04-use-cases.md`: UC-09 (full-screen takeover as a
  fallback presentation option); off-video-surface out-of-scope bullet
  aligned to R12.
- `../../context/99-glossary.md`: Overlay entry aligned to R12.
- `../../context/02-actors.md`: Publisher allowed-layouts aligned to R12.
- `0001-defer-to-iab-ctv-for-spatial-caps.md`: spatial caps inherited
  per `@layout` token by reference to IAB (R12.4).
- `../../context-analysis/iab-ad-templates.md`: IAB ad-type catalogue
  and the canonical name-to-identifier mapping the enumeration follows.
- IAB CTV *Ad Format Guidelines for Digital Video and CTV*:
  <https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e>

---
id: "0014"
title: The layout token carries the squeezeback geometry, because nothing else does
status: accepted
scope: core
date: 2026-09-18
supersedes: null
superseded_by: null
---

# ADR 0014: The layout token carries the geometry of a squeezeback

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

In a squeezeback the Player does something it does nowhere else: it
**shrinks and repositions the primary content**. Every other ad form in
this edition leaves the primary content where it is — a linear ad
replaces it, an overlay and a pause ad are composited over it. Only the
squeezeback makes the Player compute a new rectangle for content it was
already playing.

To do that the Player needs the geometry of that rectangle. R27.2 said
the shrunk primary content occupies "its declared region", and nothing
in this specification declares one. That is what made R27.2 a blocking
row rather than a wording fix.

**The obvious answer is that the creative carries it, and it does not
survive contact.** The IAB guidelines say squeezeback assets arrive as
an underlay: "the full screen 1920 x 1080 branded advertisement is
provided with a cutout for the content placement." That is true and it
is not enough. A cutout is a property of the pixels. A Player does not
inspect pixels to decide where to scale a video surface; it needs a
rectangle before it composes anything, and an image with a transparent
hole does not give it one.

**And the IAB does not close the gap either.** Its guidelines describe
each layout in prose with percentages — "the content will take up 60%
of the 1920 x 1080 screen", "the content squeezes to the upper left or
upper right" — and define no field, no coordinate system and no VAST
extension that conveys the region. The guidelines describe the layout;
they do not specify it. So this is a gap in the ecosystem and not only
in this specification, and nothing downstream will fill it for us.

## Decision

**The `@layout` token names the complete composition, and the geometry
of the primary-content region follows from the token.** A token is a
value from a closed enumeration; the region each one denotes is fixed
in R12 from the IAB percentages. The Player derives the rectangle from
the token it read, and no coordinate ever travels in a manifest.

The consequence, and it is the point: **an L-shape whose content sits
upper-left and one whose content sits upper-right are two tokens**, not
one token plus an orientation. They are two compositions, and the
Player has to tell them apart before it can place anything.

## Why this does not break R10

R10 forbids building a parallel layout system, and R10.3 puts position
semantics *inside* a layout out of scope. The distinction that makes
this decision compatible is between **which composition is in play**
and **where something sits within it**:

- *Which composition* — the primary content occupies the upper-left
  region or the upper-right one — determines what the Player must
  compute. It cannot be delegated, because the Player performs the
  transform.
- *Where the ad sits inside its layout* — R10.3's subject — remains out
  of scope and is still rendered with HTML5 / CSS under R10.1.

Applying R10.3 to the first of those was an error made while this
decision was being discussed, and it is recorded here because the two
read alike: both are sentences about left and right.

**The test that keeps this from widening**: a token carries geometry
only where the Player repositions the primary content. That is why an
overlay does not get one per corner even though the IAB names four —
the Player composites an overlay over untouched content, so the corner
is the creative's business and CSS's, exactly as R10.1 says. If a
future form makes the Player transform the primary content, it earns
tokens on the same grounds; if it does not, it does not.

## What this costs, stated rather than hidden

The enumeration grows with the catalogue: every layout the IAB
describes in two orientations becomes two tokens here, and a new
variant published later needs a new edition (R12 already says so).

And **the percentages are copied from a document open for public
comment until January 2026**. If the IAB moves them, this
specification's geometry is wrong until an edition moves too. This is
the cost of specifying what the source only describes; the alternative
was leaving the Player without a rectangle.

## Alternatives considered

**Carry the region as coordinates in the manifest.** Rejected: it is
the parallel layout vocabulary R10.2 forbids, and it was the reason
R10 exists — raised by the chair of MPEG-DASH during review of an
earlier iteration. It also makes every Publisher express geometry no
Publisher wants to own.

**Deliver the creative as HTML/CSS and let the layout come from the
document.** Coherent with R10.1 and rejected on reach: a squeezeback
creative is routinely a video, and binding the form to an HTML carrier
would exclude the common case to solve the uncommon one.

**Leave R27.2 as it is and let implementations agree bilaterally.**
This is what happens today, and it is what a specification exists to
end. Two Players given the same manifest and the same creative compose
different screens, and neither is non-conformant.

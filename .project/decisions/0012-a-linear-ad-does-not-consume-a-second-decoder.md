---
id: "0012"
title: A linear ad does not consume a second decoder, and a replacement need not be an ad
status: accepted
scope: core
date: 2026-09-17
supersedes: null
superseded_by: null
---

# ADR 0012: A linear ad does not consume a second decoder

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

This record exists because the specification stated the opposite, in
`context/` and in the generated document, and the error was durable
enough to be re-derived twice by review. It is written so the confusion
does not return.

**What was written.** A non-linear overlay composited on top of a
linear ad was declined on single-decoder devices that have image and
HTML overlay surfaces (D3 and D4). The justification, in the generated
§8.4, was that the case *"requires the device to composite a second
surface over a surface that is itself an ad"*.

**Why it is wrong, twice.**

The first error is arithmetic. The base standard does not put two
presentations on screen during an alternative presentation; it changes
which access engine outputs media. §4.2 (*DASH Client model*):

> The access engine may be in either the regular or the listen mode.
> The access engine in regular mode outputs media and timing
> information to the media engine for decoding and rendering. Playhead
> moves (and time elapses) at the same speed, and events are processed
> when the access engine is in the listen mode, however **it does not
> output media to the media engine**.

> In case Alternative Media Presentations are used, there are two
> instances of DASH access engine, main and the alternative, both
> working as described above. For the duration of the alternative media
> presentation, **the alternative access engine outputs media to the
> media engine, while the main client will be paused or be in a listen
> mode**.

"Paused" covers insertion and "listen mode" covers replacement; in both
cases one engine is delivering media. §5.16.1 says the same of
replacement directly: *"the main Media Presentation is not being
output, but its media time progresses at the same speed as the
currently playing alternative Media Presentation."* The linear ad
therefore occupies the decoder the primary content has just stopped
using. The budget for an overlay above it is one decoder plus one
surface — the same budget the same use case already declared
satisfiable for the L-shape.

The second error is that the distinguishing fact is not observable. The
justification turns on the underlying surface *being an ad*, and a
device cannot see what the video it is decoding depicts. A conformance
rule written against that distinction cannot be checked by anyone.

And the base standard does not even make the distinction. §5.16.1
describes the tool as *"the ability to switch between two independent
Media Presentations, for applications such as pre-roll and mid-roll
advertisement, **as well as blackouts**, during a live streaming
session"*, and §8.13.1 repeats the pair for the Advanced Linear
profile: *"alternate content use cases, such as server guided
advertisement insertion **and blackouts**"*. The surface underneath may
not be advertising at all.

**Why it survived two reviews: the root was one layer below where
anyone looked.** Review examined §8.4's justification and found it
consistent — and it was, with `context/`'s glossary, which defined
`InsertPresentation` and `ReplacePresentation` as signalling that *an
ad* presentation is inserted or replaces the primary content. From
"the construct is for advertising" to "the surface underneath is an
ad" is one step, and §8.4 took it. Each layer agreed with the layer
below it, so checking any layer against its neighbour returned
consistent, and only checking against the base standard returned
false.

What the glossary had done is visible once the clause is read. §5.16.1
opens by defining the alternative Media Presentation with no content
type at all, and then says: *"**A key use case** for this is
advertisement, where alternative Media Presentation represents the
inserted advertisement content, and main Media Presentation represents
the entertainment content."* A key use case — not the definition. The
element semantics say less still: *"specifies an Alternative MPD
Insertion event"* and *"specifies an Alternative MPD Replace event"*,
with no mention of advertising. **The glossary had turned one use case
into the definition**, and everything built on it inherited the
narrowing.

**The finding is Nicolás Levy's**, not this project's review. Both the
decoder count and the blackout reading came from him; the review had
confirmed the text as a contradiction between two sections without
noticing that one side of it was arithmetically false.

## Decision

**A linear ad does not consume a second decoder.** During an
alternative presentation exactly one access engine outputs media, so
the alternative presentation occupies the decoder the primary content
released. An overlay above it costs one surface, not a decoder.

**A replacement is not necessarily an ad**, and no rule in this
specification may depend on its being one.

D3 therefore composites an image or HTML overlay over a linear ad, and
D4 composites an image one. UC-14 states the same behaviour where the
underlying presentation is demonstrably not advertising.

## Alternatives considered

**Keep the decline and restate it as a policy — "this specification
does not stack two ads."** Rejected. The Publisher already holds the
lever twice over: an overlay above a linear break exists only where the
Publisher authored an overlay window that overlaps the linear one, and
windows are time intervals whose overlap is authored (`@presentationTime`
and `@duration`); and `@allowedLayouts` narrows what an overlapping
window admits. Writing a prohibition would take from the Publisher a
decision `02-actors.md` assigns to it — *"the Publisher declares the
space (slot duration cap, allowed forms, allowed layouts)"* — and would
violate R2.1, which requires slot constraints to be declared by the
Publisher rather than inferred elsewhere. The correct repair removes
text; it does not replace it.

**Keep the decline for HTML overlays only, on the grounds that HTML
composition is heavier.** Rejected: it is the same arithmetic error
with a narrower blast radius. Where a device's HTML capability is the
real constraint — D4 — the decline already stands on that ground and
needs no help.

## Consequences

- **Three declines survive, and each rests on a real device property.**
  D2 declines image and HTML overlays because it composites no
  non-video surface over video. A **video** overlay above a linear ad
  is declined on any single-decoder device, because that case does need
  two decoders. D5 declines everything, having no overlay surface.
  These are not weakened by this decision and should not be "corrected"
  by a later reading of it.
- **No policy rule is added.** See the first rejected alternative.
- **UC-14 is added** rather than a paragraph inside UC-04, so that the
  non-advertising case is visible to a reader who arrives with the
  question rather than only to one who already suspects the answer.
- **The glossary is corrected at the root.** Both entries now give the
  construct as the base specification gives it, and state in a separate
  sentence what this specification uses it for. Keeping the two apart
  is the repair: they were fused, which is what let one be read as the
  other.
- **`output/` is not edited.** The generated §8.4 and Annex D.5 still
  carry the false justification and are corrected by the next build,
  which `context/` now drives correctly.

## Links

- ADR 0006 — adopt the base standard's execution model where it
  answers. The reading of §4.2 applied here is that criterion.
- `context/04-use-cases.md` — UC-04 (D3, D4, coverage row, closed open
  question) and UC-14.
- `context/02-actors.md` and R2.1 — why the Publisher, not this
  specification, holds the lever.

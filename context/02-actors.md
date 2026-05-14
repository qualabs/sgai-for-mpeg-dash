# Actors and Responsibilities

> For the use cases that exercise the model across device classes
> and ad opportunity types, see [`04-use-cases.md`](04-use-cases.md).

The architecture proposed by this project rests on a **three-actor
model**. Each actor has a clearly bounded set of responsibilities, and
the separation is normative: the Broadcaster declares what can be
shown, the ADS provides what is available to show, and the Player is
the entity that actually decides and composes what appears on screen,
always validating against what the Broadcaster declared. This document
is the canonical statement of that model and is mirrored verbatim in
the working doc.

## Broadcaster / Content Owner

The Broadcaster owns the primary content and the viewer's screen.

- Signal ad opportunities in the primary timeline by emitting events
  in the main MPD. Each event marks where in the timeline an ad can
  be inserted and what kind of insertion is permissible.
- Define the type and constraints of each slot. The Broadcaster
  decides whether the slot is a linear replacement, a linear
  insertion, or a non-linear (overlay-style) opportunity. For
  overlay-style slots, the Broadcaster also constrains:
  - which layout templates are allowed (e.g. L-shape, banner,
    skyscraper, sidebar, or unrestricted; additional broadcast-side
    examples include squeezeback, lower-third, and corner-bug as
    defined in [`99-glossary.md`](99-glossary.md)), and
  - other slot-level constraints such as maximum overlay duration,
    maximum number of concurrent overlays, or mutually exclusive
    layouts.
- Encode these constraints within the MPD event so they are
  normative for the slot. Specific positions inside a layout are
  out of scope here — they belong to the per-layout detail covered
  in the Positioning Templates section of the proposal.

## Ad Decision Server (ADS)

The ADS returns ad candidates when the Player resolves the URL
provided by an MPD event.

- Resolve the event URL (the existing `ListMPD` for linear
  opportunities, or the equivalent resolution document for
  non-linear ones) into a list of ad candidates eligible for the
  slot.
- Decide **how many** ads to return for a given opportunity, **which
  ads**, and **in what order**. The number of ads in an opportunity
  is an ADS-only decision — the Broadcaster declares the *space*
  (slot duration cap, allowed forms, allowed layouts) but does not
  prescribe N. The ADS optimises revenue for the slot within the
  Broadcaster-declared envelope.
- Apply ad-decisioning logic over its own pool: targeting,
  frequency capping, brand safety filtering, competitive
  separation, ordering, fill-rate considerations, and any other
  business logic that selects which ads in its catalogue are
  eligible for this viewer in this slot.
- **Tracking schedule authority.** The ADS is the authority over
  what tracking beacons fire and when. The ADS supplies the
  tracking schedule as DASH callback events (or equivalent)
  embedded in its resolution document; the Player executes that
  schedule, but does NOT decide which beacons to fire or at what
  fractions of the ad presentation. The spec defines the carrier
  and the timing space (relative to the ad presentation), not the
  schedule itself.

The ADS is **not** responsible for enforcing the constraints
declared by the Broadcaster in the MPD event. The specification does
not require the ADS to validate its response against those
constraints, and a non-compliant ADS may return ads that violate
them. Validation is the Player's responsibility. This separation
allows a single ADS to serve multiple Broadcasters with heterogeneous
policies without coupling its logic to any specific MPD event
semantics.

## Video Player

The Player is the entity that ties the architecture together. It
reads the MPD, talks to the ADS, validates the response, and composes
the final viewer experience.

- Read the MPD and parse the slot constraints declared by the
  Broadcaster for each event.
- Resolve the ADS URL when the playhead reaches an event and
  receive the list of ad candidates.
- Validate each candidate against the slot constraints declared in
  the MPD. Any candidate that violates the constraints (disallowed
  layout, exceeded duration, more concurrent overlays than allowed,
  etc.) is discarded.
- Select the ad to render from the candidates that passed
  validation. The Player may apply additional client-side criteria
  (ranking, ordering, deduplication, simultaneity caps), but it
  must operate within the validated subset.
- Compose and render the ad over the primary content using the
  workflow that matches the slot type: replace, insert, or overlay.

## Boundary Summary

Authority over the on-screen experience is held jointly by the
Broadcaster (who declares) and the Player (who enforces). The ADS
provides candidates but is not normatively bound by the slot
constraints. This separation lets a single ADS serve multiple
Broadcasters with heterogeneous policies, and lets a Player guarantee
the Broadcaster's constraints even when the ADS is an external,
non-audited service.

The following list summarises which actor owns which decision in the
SGAI flow:

- *When* ad opportunities appear in the timeline — **Broadcaster**.
- *Which types of ads* are allowed per slot (allowed forms,
  layouts, duration cap, concurrency cap) — **Broadcaster**.
- *How many ads* fill a multi-ad opportunity (within the
  Broadcaster's duration cap) — **ADS**.
- *Which ads are available* to serve to the slot for this viewer
  — **ADS**.
- *Targeting, frequency capping, brand safety filtering,
  competitive separation, ordering* of the ad pool — **ADS**.
- *Validating each candidate* against the MPD constraints —
  **Player**.
- *Selecting the ad to render* from validated candidates —
  **Player**.
- *Compositing and rendering* the ad over the primary content —
  **Player**.

# Actors and Responsibilities

> For the use cases that exercise the model across device classes
> and ad opportunity types, see [`04-use-cases.md`](04-use-cases.md).
> The actors are: **Publisher**, **Ad Decision Server (ADS)**,
> **Ad Presentation Server (APS)**, and **Video Player**.

The architecture proposed by this project rests on a **four-actor
model**. Each actor has a clearly bounded set of responsibilities, and
the separation is normative: the Publisher declares what can be
shown, the Ad Decision Server (ADS) decides which ads to serve and
returns them as VAST, the Ad Presentation Server (APS) converts that
VAST into the MPD-native resolution document the Player understands,
and the Player is the entity that actually decides and composes what
appears on screen, always validating against what the Publisher
declared. This document is the canonical statement of that model and
is mirrored verbatim in the working doc.

## Publisher

The Publisher owns the primary content and the viewer's screen.

- Signal ad opportunities in the primary timeline by emitting events
  in the main MPD. Each event marks where in the timeline an ad can
  be inserted and what kind of insertion is permissible.
- Define the type and constraints of each slot. The Publisher
  decides whether the slot is a linear replacement, a linear
  insertion, or a non-linear (overlay-style) opportunity. For
  overlay-style slots, the Publisher also constrains:
  - which layout templates are allowed, drawn from the ad types and
    visual placements enumerated in R12 of
    [`03-requirements.md`](03-requirements.md) (e.g. corner / bug,
    lower-third, L-shape / squeezeback, side-by-side / double-box), or
    unrestricted, and
  - other slot-level constraints such as maximum overlay duration,
    maximum number of concurrent overlays, or mutually exclusive
    layouts.
- Encode these constraints within the MPD event so they are
  normative for the slot. Specific positions inside a layout are
  out of scope here — they belong to the per-layout detail covered
  in the Positioning Templates section of the proposal.

## Ad Decision Server (ADS)

The ADS is the ad-decisioning authority. It receives an ad request,
decides which ads to serve, and responds with a **decision document**
— typically VAST (as defined by the IAB), but the ADS is not bound
to VAST and MAY emit another format. It performs **no** conversion
into the MPD-native / SGAI format the Player consumes — that is the
APS's job. The ADS output is the upstream, format-agnostic ad
decision.

- Receive the ad request and decide **how many** ads to return for a
  given opportunity, **which ads**, and **in what order**. The
  number of ads in an opportunity is an ADS-only decision — the
  Publisher declares the *space* (slot duration cap, allowed forms,
  allowed layouts) but does not prescribe N. The ADS optimises
  revenue for the slot within the Publisher-declared envelope.
- Apply ad-decisioning logic over its own pool: targeting,
  frequency capping, brand safety filtering, competitive
  separation, ordering, fill-rate considerations, and any other
  business logic that selects which ads in its catalogue are
  eligible for this viewer in this slot.
- **Respond with a decision document.** The ADS's output is a
  decision document — typically VAST (IAB), though the ADS is not
  bound to VAST — carrying the selected ads, their media files,
  durations, and tracking events. The ADS does not produce the
  resolution document the Player reads; the APS derives that from
  whatever the ADS emits.
- **Tracking schedule authority.** The ADS is the authority over
  what tracking beacons fire and when. It declares the tracking
  events in its VAST response; the APS translates those into the
  DASH callback events embedded in the resolution document, and the
  Player executes that schedule. The Player does NOT decide which
  beacons to fire or at what fractions of the ad presentation. The
  spec defines the carrier and the timing space (relative to the ad
  presentation), not the schedule itself.

The ADS is **not** responsible for enforcing the constraints
declared by the Publisher in the MPD event, nor for converting its
output into any DASH-native shape. The specification does not require
the ADS to validate its response against those constraints, and a
non-compliant ADS may return ads that violate them. Validation is
the Player's responsibility. This separation allows a single ADS to
serve multiple Publishers (through their APSs) with heterogeneous
policies without coupling its logic to any specific MPD event
semantics. The ADS-side API (request shape, VAST version, decisioning
inputs) is opaque to this spec (R18) and VAST-version-agnostic at
the spec level (R11).

## Ad Presentation Server (APS)

The APS is the adapter between the ADS's decision world and the
MPD-native / SGAI world this spec defines. It sits between the
Player and the ADS: the Player resolves an MPD event's URL against
the APS, the APS calls the ADS, and the APS **converts whatever the
ADS emits — VAST (IAB) or any other decision format — into the
resolution document the Player understands** — the MPD-native / SGAI
document (`ListMPD` or single-period alternative MPD for linear, the
overlay resolution document for non-linear). Translating any ADS
output into the resolution document this spec defines is the APS's
responsibility; the conversion from the ADS's format to the
resolution document is not itself defined by this spec.

> **Note for the reader.** In real-world implementations the APS is
> often a module of the ADS rather than a separately deployed
> service. This document presents it as a distinct actor in order to
> describe its responsibilities clearly, independent of how it is
> ultimately implemented.

- **Player-facing endpoint.** The APS exposes the endpoint that the
  Publisher references in the MPD event `@url`. The
  Publisher can encode slot constraints (for example, a
  slot-duration hint) as query parameters on that URL — this is the
  APS's runtime input. When the playhead reaches the event, the
  Player resolves this URL and receives the resolution document.
- **Convert VAST → MPD-native / SGAI.** On each resolution request,
  the APS obtains the ad decision from the ADS as VAST and
  transforms it into the resolution document: it maps VAST media
  files onto DASH Representations / sub-MPDs, VAST durations onto
  `Period@duration`, and VAST tracking events onto DASH callback
  events. The result is the document the Player reads.
- **Carry the tracking schedule the ADS declared.** The APS does
  not invent the tracking schedule; it translates the ADS-declared
  tracking events into DASH callback events (or equivalent) embedded
  in the resolution document, preserving the ADS's authority over
  which beacons fire and when.
- **Produce candidates with renderable presentation options.**
  Because the Player is device-agnostic on the APS interface, the APS
  emits each ad candidate carrying one or more renderable presentation
  options (form + layout) as an ordered list whose document order is
  the preference order, and the Player renders the first option it can
  satisfy per device capabilities and the Publisher's allowed layouts.

The APS is **not** the ad-decisioning authority — it does not decide
which ads to serve (that is the ADS), and it does not enforce the
Publisher's slot constraints (that is the Player). It is a
translation and presentation layer: VAST in (or similar),
MPD-native / SGAI resolution document out.

## Video Player

The Player is the entity that ties the architecture together. It
reads the MPD, talks to the APS, validates the response, and composes
the final viewer experience.

- Read the MPD and parse the slot constraints declared by the
  Publisher for each event.
- Resolve the APS URL when the playhead reaches an event and
  receive the list of ad candidates as the resolution document.
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
Publisher (who declares) and the Player (who enforces). The ADS
decides which ads to serve and the APS presents them as the
resolution document, but neither is normatively bound by the slot
constraints. This separation lets a single ADS serve multiple
Publishers (through their APSs) with heterogeneous policies, and
lets a Player guarantee the Publisher's constraints even when the
ADS and APS are external, non-audited services.

The following list summarises which actor owns which decision in the
SGAI flow:

- *When* ad opportunities appear in the timeline — **Publisher**.
- *Which types of ads* are allowed per slot (allowed forms,
  layouts, duration cap, concurrency cap) — **Publisher**.
- *How many ads* fill a multi-ad opportunity (within the
  Publisher's duration cap) — **ADS**.
- *Which ads are available* to serve to the slot for this viewer
  — **ADS**.
- *Targeting, frequency capping, brand safety filtering,
  competitive separation, ordering* of the ad pool — **ADS**.
- *The ad decision output as VAST* — **ADS**.
- *Converting the VAST into the MPD-native / SGAI resolution
  document the Player reads* — **APS**.
- *Translating the ADS's tracking events into DASH callback
  events in the resolution document* — **APS**.
- *Validating each candidate* against the MPD constraints —
  **Player**.
- *Selecting the ad to render* from validated candidates —
  **Player**.
- *Compositing and rendering* the ad over the primary content —
  **Player**.

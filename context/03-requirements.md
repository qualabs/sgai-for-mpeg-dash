# Requirements

> R2 anchors on the three-actor model defined in
> [`02-actors.md`](02-actors.md). Use cases that exercise these
> requirements across device classes and ad opportunity types live in
> [`04-use-cases.md`](04-use-cases.md).

The requirements below govern the design of the proposal. They are
grouped into functional, governance / non-functional, and
out-of-scope. Each numbered requirement is referenced later in design
discussions; any design choice that conflicts with one must explicitly
state the conflict and the justification. This section mirrors the
working doc verbatim.

## Design principles

The following principles govern any decision made when authoring the
constructs of this specification. They are intentionally generic;
concrete requirements that follow are constrained by them.

- **DP-1. Keep It Simple — information must not be redundant.**
  Between a simple structure and a more complex one that can
  introduce unnecessary errors, the simpler one is always preferred.
  A construct MUST NOT carry information that is already determined
  by its own context — its element name and namespace, the parent
  construct that contains it, or another attribute on the same
  construct. Redundancy invites contradiction; contradiction invites
  silent bugs.
- **DP-1.1. No "future flexibility" placeholders.** A construct
  MUST NOT be introduced "just in case a future edition relaxes
  it". Constructs whose only admissible value matches the
  construct's default OR is fixed by another rule (e.g. R14)
  MUST NOT exist in the spec. The argument "we might want this
  attribute later" is explicitly rejected — good ideas for the
  future stay in the future, they don't enter the spec "por si
  las dudas". Less is more.
- **DP-1.2. Single source of truth.** When the same value or
  relationship appears in multiple places in the spec or in a
  generated MPD, exactly ONE declaration is canonical and the
  others MUST be derived from it (computed at runtime by the
  implementer, not duplicated in the markup). Duplicating a
  value across attributes invites silent drift when one is
  modified and the other forgotten.
- **DP-2. Obligations are positive.** When the spec states what an
  actor MUST do, it states the positive obligation — the action,
  the construct, the value. The spec does NOT enumerate
  prohibitions. The space of "what is forbidden" is unbounded;
  declaring it exhaustively is impossible and a long list of
  "MUST NOT" items invites confusion and silent gaps. Instead,
  the positive obligation defines the contract; anything outside
  the positive obligation is implicitly out of scope. (For
  example: instead of saying "the Player MUST NOT fire tracking
  beacons after the slot end," say "the Player fires tracking
  beacons within the slot window.")

## Requirements

- **R1. MPEG-DASH 6th edition compliance and graceful degradation.**
  The solution must extend MPEG-DASH 6th edition without breaking
  existing semantics. Backward compatibility is mandatory: a Player
  that does not implement the new mechanisms introduced by this
  proposal MUST skip them and continue playing the primary content
  uninterrupted. Any new construct introduced by the proposal MUST
  be expressed using MPEG-DASH 6th edition extension points whose
  "ignore-if-unknown" semantics already enable this behavior on
  conforming legacy Players. The expected behavior of a legacy
  Player encountering the new constructs is captured as **UC-07**
  in [`04-use-cases.md`](04-use-cases.md).

  **Conformance criteria** (runtime):
  - **R1.1** (Player): Given an `MPD` containing an SGAI construct
    introduced by this proposal that the Player does not implement,
    a conforming legacy Player MUST ignore the unknown construct
    and continue playing the primary content uninterrupted.
  - **R1.2** (Broadcaster / spec document): Every new SGAI construct
    introduced by this proposal MUST be expressed using one of the
    extension points enumerated in
    [`08-dash-extension-rules.md`](./08-dash-extension-rules.md):
    foreign-namespace open content (§5.2.1, DR-2 / DR-3),
    application-level Event Streams (§5.10), or vendor descriptor
    schemes (§5.8.4.8 / §5.8.4.9). New constructs MUST NOT be
    introduced by paths that violate the §5.3.2.6 / §8.15 / §7.3 /
    RFC 4337 chain when reached via `<ImportedMPD>` (DR-1) or by
    inline AdaptationSet / Representation under a ListMPD-level
    Period (DR-5). Annex F (DR-4) is admissible only when (a) the
    construct genuinely requires DASH segment-delivery semantics
    for a non-ISO-BMFF format, and (b) the spec is willing to
    publish a new Interoperability Point URI.
  - **R1.3** (Broadcaster / spec document): The specification MUST NOT alter
    or override the semantics of any pre-existing MPEG-DASH 6th
    edition construct.
- **R2. Honour the actor's responsibilities.** The design must
  enforce the separation defined in the Actors and Responsibilities
  section: the Broadcaster declares constraints, the ADS provides
  candidates, and the Player validates and renders. New mechanisms
  must be expressible within this contract.

  **Conformance criteria** (runtime + document-level):
  - **R2.1** (Broadcaster): Constraints applicable to an ad slot
    (max duration, opt-in policies, layout templates) MUST be
    declared by the Broadcaster in the `MPD`, not inferred at
    runtime by the ADS or the Player.
  - **R2.2** (ADS): The ADS MUST produce ad candidates as a
    resolution document; it MUST NOT be expected to enforce
    Broadcaster-declared constraints (e.g. slot duration cap).
  - **R2.3** (Player): The Player MUST validate ADS-returned
    candidates against Broadcaster-declared constraints and render
    only those that satisfy them.
  - **R2.4** (spec document): Every new mechanism introduced by the
    specification MUST be expressible within the three-actor contract; any
    mechanism that would require an actor to take on a
    responsibility outside its role MUST be rejected or redesigned.
- **R3. Support a diverse range of device capabilities.** The
  solution must work across the heterogeneity of target devices in
  real CTV / streaming deployments — from devices that can render
  multiple concurrent video decoders plus image and HTML overlays on
  top of video, down to devices with a single video decoder and no
  overlay capability at all. The supported device classes and the
  expected behaviour for each combination of device class and ad
  opportunity are enumerated in the **Use Cases** section.

  **Conformance criteria** (runtime + document-level):
  - **R3.1** (spec document): The specification MUST enumerate the supported
    device classes and, for each class, the expected behaviour for
    each ad opportunity type covered by the use cases.
  - **R3.2** (Player): A Player on any supported device class MUST
    produce a defined behaviour (render, fall back, or skip) for
    every ad opportunity type defined in the spec; undefined
    behaviour is non-conforming.
  - **R3.3** (Player): A Player MUST NOT attempt to render an ad
    form (video, image, HTML) that its device class cannot render.
- **R4. Broadcaster-declared max slot duration, Player-enforced.**
  The Broadcaster declares a maximum duration for each ad slot. The
  ADS may return one or more ad candidates to fill that slot, but the
  ADS is **not** responsible for respecting the cap. The Player MUST
  enforce the cap: if the cumulative duration of the candidates the
  Player chose to render exceeds the declared maximum, the Player
  MUST stop at the cap, even if that means cutting an ad in
  mid-playback. This default applies to both linear ad slots
  (start-of-session, mid-content, multi-ad break) and non-linear
  overlay slots (overlay max display duration). Alternative overflow
  policies (e.g. skip the break entirely, trim-clean at the previous
  ad boundary, fail-closed) are explicitly out of scope for the
  default semantics; if needed, they must be expressible by the
  Broadcaster as an opt-in policy on the slot. R4 is a concrete
  instance of R2 — Broadcaster declares the constraint, Player
  enforces it, ADS does not.

  **Conformance criteria** (runtime):
  - **R4.1** (Broadcaster): The Broadcaster MUST declare a maximum
    duration on every ad slot (linear or non-linear) defined in the
    `MPD`.

    > **Note — listen-mode slots (UC-09):** Listen-mode slots are
    > declared WITHOUT `@maxDuration` at activation; R4.1's MUST does
    > not apply to them. The Broadcaster terminates the slot by sending
    > a `status=update` that introduces or revises `@maxDuration` to
    > the desired cut point; the Player enforces that cap per R4.2 when
    > it arrives. `status=update` is a generic lifecycle update — the
    > Player MUST NOT terminate on a `status=update` that does not set
    > or revise `@maxDuration`. Whether to recommend a safety-fallback
    > `@maxDuration` at activation is an open question left to WG
    > resolution (DASH 6th does not mandate it). R4.2 and R4.3 apply
    > whenever `@maxDuration` is present, regardless of whether it was
    > declared at activation or introduced via a subsequent
    > `status=update`. See **UC-09** in
    > [`04-use-cases.md`](04-use-cases.md) and the listen-mode
    > section in
    > [`05-dash-linear-interfaces.md`](05-dash-linear-interfaces.md).

  - **R4.2** (Player): When the cumulative duration of accepted ad
    candidates would exceed the Broadcaster-declared cap, the
    Player MUST stop rendering at the cap boundary, even if the
    stop falls mid-ad.
  - **R4.3** (Player): The Player MUST NOT extend a slot beyond
    the Broadcaster-declared cap regardless of ADS metadata or
    candidate count.
  - **R4.4** (ADS): The ADS is NOT required to respect the cap when
    selecting candidates; a conformance check on the ADS MUST NOT
    fail solely because the cumulative duration of its returned
    candidates exceeds the cap.
  - **R4.5** (Player): When the actual rendered length of an
    accepted candidate exceeds its declared duration, the Player
    MUST enforce the cap against actual length, not declared
    length ("trim during play").
- **R5. Device-aware ad selection.** The Player is the sole
  authority on device capability — the ADS does not need a
  device-class matrix or a per-Player view. Ad candidates returned
  by the ADS carry one or more **renderable forms** (e.g. video,
  image, HTML), optionally ranked by ADS hints. The Player MUST
  choose the best form it can render given its device, and MUST
  skip candidates with no renderable form (falling back to the
  next candidate or to primary content, depending on policy).
  R5 is a concrete instance of R2 — Player owns the responsibility
  the ADS does not have — and a direct contributor to R3.

  The ADS MAY return candidates carrying multiple forms or layouts.
  The Player MUST select per device capabilities, the Broadcaster's
  allowed layouts, and ADS-supplied priority hints. Skipping a
  candidate because none of its forms is renderable on the target
  device is acceptable; the Player then falls through to the next
  candidate or to primary content.

  **Conformance criteria** (runtime):
  - **R5.1** (ADS): Each ad candidate returned by the ADS MUST
    carry one or more renderable forms (e.g. video, image, HTML);
    the ADS MAY rank them via ADS hints.
  - **R5.2** (Player): The Player MUST choose, among the renderable
    forms of an accepted candidate, the best form it can render on
    its device.
  - **R5.3** (Player): The Player MUST skip any candidate that
    carries no form renderable on its device, falling back to the
    next candidate or to primary content per the configured policy.
  - **R5.4** (ADS): The ADS MUST NOT be required to maintain a
    device-class matrix or a per-Player capability view to produce
    candidates.
  - **R5.5** (ADS): An ad candidate MAY carry multiple forms
    and MAY carry multiple admissible layouts; ADS-supplied
    priority hints MAY rank both dimensions independently.
  - **R5.6** (Player): The Player MUST resolve form/layout
    selection by intersecting (a) device capabilities, (b) the
    Broadcaster-declared allowed layouts on the slot, and
    (c) ADS-supplied priority hints. A combination that fails
    any of the three MUST NOT be rendered.
  - **R5.7** (Player): If no form/layout combination on a
    candidate satisfies R5.6, the Player MUST skip that
    candidate and fall through to the next ADS-returned
    candidate (preserving the order required by R7) or, when
    exhausted, to primary content.
- **R6. Ad tracking carrier.** The specification MUST specify how in-band
  ad tracking beacons (impression, start, quartiles, complete, etc.)
  are carried in the resolution document. Implementations SHOULD
  reuse the existing DASH callback event scheme
  (`urn:mpeg:dash:event:callback:2015`, §4.7 / §5.10.4.5) as the
  carrier — embedding tracking `<Event>` entries inside an
  `<EventStream>` of that scheme in the ad MPD or sub-MPD. New
  tracking carriers MAY be introduced only when the callback scheme
  cannot express the required semantics, and only after a
  documented gap analysis per R9. Application-level metadata that
  has no native DASH carrier (e.g. `ClickThrough`, `AdSystem`,
  `AdTitle`, `UniversalAdId`) MAY be conveyed via vendor-namespaced
  extension elements; Players MUST safely ignore unknown namespaces
  per the DASH extension rules invoked by R1.

  **Conformance criteria** (runtime + document-level):
  - **R6.1** (spec document): The specification MUST specify how in-band ad
    tracking beacons are carried in the resolution document.
  - **R6.2** (Broadcaster / ADS): Implementations SHOULD carry
    tracking beacons as `<Event>` entries inside an `<EventStream>`
    of scheme `urn:mpeg:dash:event:callback:2015` in the ad `MPD`
    or sub-`MPD`.
  - **R6.3** (spec document): A new tracking carrier MAY be
    introduced only when the callback scheme cannot express the
    required semantics, and only after a documented gap analysis
    per R9.
  - **R6.4** (ADS / Broadcaster): Application-level metadata with
    no native DASH carrier (`ClickThrough`, `AdSystem`, `AdTitle`,
    `UniversalAdId`, etc.) MAY be conveyed via vendor-namespaced
    extension elements.
  - **R6.5** (Player): A Player MUST safely ignore unknown
    namespaces on tracking-related extension elements, per the DASH
    extension rules invoked by R1.
  - **R6.6** (Broadcaster / ADS / spec document): When a non-AV ad
    form (`mediaType ∈ {html, image, ...}`) is carried, the asset
    URL MUST NOT be expressed as `@mimeType` on an AdaptationSet or
    Representation reached through any path bound by RFC 4337
    (DR-1, DR-5 in
    [`08-dash-extension-rules.md`](./08-dash-extension-rules.md)).
    It MUST be carried via one of the §5.2.1 / §5.10 / §5.8.4.x
    carriers enumerated by DR-6, per R1.2.
- **R7. Respect ADS-returned order.** When the ADS returns a
  resolution document containing more than one ad (e.g. a `ListMPD`
  with multiple `<Period>` entries), the Player MUST play the ads
  in the order declared by the ADS, **as long as this is possible
  given the other Player constraints**. Specifically, the Player
  MAY drop a candidate that violates R3 (no renderable form for the
  device) or that would push the cumulative duration past the slot
  cap (R4), but it MUST NOT re-order, deduplicate, or otherwise
  rearrange the remaining candidates. Ad selection and ordering are
  ADS responsibilities (R2); the Player's role is to honour them
  unless a hard constraint blocks it.

  Order of evaluation when a candidate's declared duration would
  push the cumulative slot duration past the cap (R4 / max slot
  duration): the Player MAY skip that candidate entirely based on
  declared duration ("drop before play"). If the Player accepts a
  candidate and only discovers at playback that its actual rendered
  length exceeds the cap, R4 applies and the Player trims
  mid-rendering ("trim during play"). In summary: drop-before-play
  based on declared duration is permitted; trim-during-play based
  on actual length is mandatory.

  **Conformance criteria** (runtime):
  - **R7.1** (Player): Given an ADS resolution document with more
    than one ad candidate, the Player MUST play the candidates in
    the order declared by the ADS, except for candidates dropped
    under R7.2 or R7.3.
  - **R7.2** (Player): The Player MAY drop a candidate that has no
    form renderable on its device (R3 / R5).
  - **R7.3** (Player): The Player MAY drop a candidate before
    playback ("drop before play") when its declared duration would
    push the cumulative slot duration past the cap (R4).
  - **R7.4** (Player): The Player MUST NOT re-order, deduplicate,
    or otherwise rearrange the remaining candidates after applying
    R7.2 / R7.3.
  - **R7.5** (Player): If a candidate is accepted and its actual
    rendered length exceeds the cap, the Player MUST trim
    mid-rendering ("trim during play") per R4.
- **R11. No dependency on VAST.** The specification MUST NOT depend on any
  specific version of VAST or on VAST as a protocol. Examples that
  show interoperability with a specific VAST version are
  illustrative only — conformant implementations MUST be
  VAST-version-agnostic, and the spec MUST NOT impose VAST as a
  precondition for any actor.

  **Conformance criteria**:
  - **R11.1** (spec document): The normative chapters of the spec
    MUST NOT cite a specific VAST version as required.
  - **R11.2** (Player): A Player MUST be able to operate against
    an ADS that does not use VAST at all (the ADS-side protocol
    is the ADS's internal concern, not the spec's contract).
  - **R11.3** (spec document): Any reference to VAST in the spec
    MUST be in an annex or in a non-normative note explicitly
    flagged as illustrative.
- **R12. Ad type definitions owned by IAB.** Ad types and their
  visual templates are defined and maintained by the IAB. This
  specification references IAB definitions normatively for ad-type names
  and behavioural expectations; introducing new ad-type
  definitions (new template categories beyond what IAB publishes)
  is out of scope.

  Reference (live link, not snapshotted):
  https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e

  **Conformance criteria**:
  - **R12.1** (spec document): The list of accepted ad-type values
    in the spec MUST be sourced from IAB definitions. A reference
    to the IAB source MUST be included.
  - **R12.2** (Broadcaster): Broadcasters declaring allowed
    layouts MUST use names that map 1:1 to IAB-defined ad-type
    values (no broadcaster-private layout names in the
    allowed-layouts declaration on the slot).
  - **R12.3** (ADS): The ADS MUST NOT emit form metadata for ad
    types that are not part of the IAB-defined set used by this
    spec's edition.
- **R13. Non-linear ad tracking — ADS-directed callbacks.**
  The specification MUST define a tracking mechanism that allows
  the ADS to instruct the Player on which tracking beacons to
  fire, and at which points relative to the ad's presentation.
  The mechanism MUST reuse DASH callback events (or an equivalent
  baseline DASH construct); no new tracking event scheme is
  introduced. Beacon timings are **relative to the ad's
  presentation time**, and the **ADS is the authority** over the
  tracking schedule — the spec does NOT prescribe specific
  fractions (no hardcoded quartiles), granularity, or beacon
  count. The Player executes the schedule the ADS supplies.

  **Conformance criteria**:
  - **R13.1** (ADS): The ADS MUST express tracking instructions
    using DASH callback events (or equivalent), with timings
    expressed relative to the ad's presentation timeline.
  - **R13.2** (Player): Given an ad accepted for rendering, the
    Player MUST execute the tracking schedule supplied by the
    ADS — firing each beacon at its specified relative time.
  - **R13.3** (Player): If R4 trims the ad before a scheduled
    beacon's time, the Player MUST stop firing remaining beacons
    at the trim boundary.
  - **R13.4** (spec document): The specification MUST NOT introduce
    a new tracking event scheme; reuse of the DASH baseline
    callback mechanism is mandatory.
- **R14. Single concurrent non-linear ad presentation.**
  At most one non-linear ad form may be active on the screen at any
  given moment. When multiple non-linear ad opportunities overlap in
  time (e.g. a mid-roll l-shape window overlapping with a banner
  window), the Player MUST serialise their presentation — show one,
  finish it, then evaluate the next. Simultaneous presentation of two
  or more non-linear forms is OUT OF SCOPE for this edition; a future
  edition MAY introduce concurrency semantics with explicit conflict
  resolution rules.

  **Conformance criteria**:
  - **R14.1** (Player): At any time t, the Player MUST be presenting
    at most one form from a non-linear opportunity. Other
    simultaneously-active opportunities MUST be deferred or skipped
    per policy.
  - **R14.2** (spec document): The specification MUST NOT introduce
    constructs that imply or require parallel non-linear form
    rendering.
- **R15. Admissible creative carrier formats.**
  The admissible ad-creative carrier formats for this edition are
  exactly three: **video** (carried per the MPEG-DASH 6th edition
  baseline mp4 constraints — see DR-1 in
  [`08-dash-extension-rules.md`](./08-dash-extension-rules.md)),
  **image** (concrete formats defined by IAB ad templates), and
  **HTML** (`text/html`, which MAY contain inline `<script>` per
  HTML5 semantics; the script runs under the device's HTML
  capability contract, not as a separate carrier).

  **Conformance criteria**:
  - **R15.1** (spec document): The specification MUST enumerate
    this exact admissible set wherever creative carrier types are
    discussed; new carrier types MUST NOT be added in annexes,
    examples, or implementation notes.
  - **R15.2** (ADS / Broadcaster): Ad candidates returned by the
    ADS and forms declared by the Broadcaster MUST carry a
    creative whose mimeType falls under one of the three
    admissible categories defined above.
  - **R15.3** (Player): The Player MAY skip a candidate whose
    creative carrier mimeType is not in the admissible set; such
    a candidate signals a non-conformant ADS or Broadcaster.
- **R16. Pause-ad lifecycle bound to pause state.**
  A pause-ad form, by definition, is admissible only while the
  primary content is paused. When the viewer resumes primary
  playback, the Player dismisses any active pause-ad form
  immediately and ceases firing further tracking beacons
  associated with that pause-ad. The pause-ad's lifecycle is
  bounded by the pause-state interval.

  **Conformance criteria** (runtime):
  - **R16.1** (Player): Upon a pause-to-play transition by the
    viewer, the Player MUST remove any rendered pause-ad form
    from the screen within one rendering frame.
  - **R16.2** (Player): Upon the same transition, the Player MUST
    cease firing tracking beacons scheduled for the dismissed
    pause-ad; beacons scheduled at relative times after the
    transition fall outside the pause-ad's active window and are
    therefore out of scope.
- **R17. Pause-ad priority over overlay.**
  When a pause-ad opportunity and an overlay opportunity are
  active at the same instant, the pause-ad is rendered on top of
  the overlay. The Player serializes the two: while the viewer
  is paused inside a pause-ad window, the pause-ad form is the
  only ad surface visible (the overlay is suspended). When the
  viewer resumes primary playback, the pause-ad is dismissed
  (per R16) and the overlay reappears if its slot window is
  still active; the overlay continues until its window expires.
  This priority is not Broadcaster-configurable — pause-ad above
  overlay during pause is the only admissible composition.

  **Conformance criteria** (runtime):
  - **R17.1** (Player): While the viewer is paused inside a
    pause-ad window AND an overlay is active, the Player
    renders the pause-ad form and suspends the overlay
    rendering.
  - **R17.2** (Player): On resume from pause, the Player
    dismisses the pause-ad (per R16) and restores the overlay
    rendering if the overlay slot window is still active.
  - **R17.3** (Player): If the overlay slot window expired
    during the pause, the Player keeps the overlay surface clear
    on resume; the overlay is over.
  - **R17.4** (spec document): The specification carries no
    construct that lets the Broadcaster or ADS invert this
    priority.
- **R18. ADS API contract is not defined by this spec.**
  This specification does NOT define the URL syntax, parameter
  names, request payload, response payload, or any other aspect
  of the ADS-side API. The specification documents the
  Player-visible interface — the MPD event URL referenced by the
  Broadcaster, and the resolution document the ADS returns
  (`ListMPD` or single-period alternative MPD) — and treats the
  ADS internal contract (invocation parameters, decisioning
  inputs, frequency-cap signals) as opaque, agreed bilaterally
  between the Broadcaster and the ADS out-of-band.

  **Conformance criteria** (document-level):
  - **R18.1** (spec document): The specification documents the
    MPD event URL pattern (Player-visible input) and the
    resolution document format (Player-visible output).
  - **R18.2** (Broadcaster / ADS): The bilateral contract for ADS
    invocation parameters is established and maintained by the
    Broadcaster and the ADS directly, outside this specification.

## Governance Requirements

- **R8. Justify any addition or omission.** Whenever the proposal
  introduces a new construct or chooses not to reuse a construct
  that already exists in MPEG-DASH, the document must explicitly
  state why. The default is reuse; departures are documented inline
  with the design decision.

  **Conformance criteria** (document-level):
  - **R8.1** (spec document): Every new construct introduced by the
    proposal MUST be accompanied by an inline justification stating
    why an existing MPEG-DASH construct could not be reused.
  - **R8.2** (spec document): Every deliberate omission of an
    existing MPEG-DASH construct that a reader might expect to see
    reused MUST be documented inline with the design decision.
- **R9. Minimise net new constructs.** The proposal must reuse
  existing MPEG-DASH machinery (events, manifests, presentations,
  schemes) wherever possible. New constructs are introduced only
  when an existing one cannot be made to fit, and only after
  considering whether an extension to the existing construct would
  suffice.

  **Conformance criteria** (document-level):
  - **R9.1** (spec document): The proposal MUST reuse existing
    MPEG-DASH machinery (events, manifests, presentations, schemes)
    wherever possible.
  - **R9.2** (spec document): A new construct MUST NOT be
    introduced unless an existing one cannot be made to fit.
  - **R9.3** (spec document): Before introducing a new construct,
    the proposal MUST consider whether an extension to an existing
    construct would suffice, and document the outcome of that
    consideration.
- **R10. Do not recreate a layout system.** The solution must defer
  to existing layout primitives (HTML5 / CSS) for the spatial
  arrangement of overlays. Maintaining a parallel layout standard is
  out of scope and adds long-term maintenance cost. (This
  requirement was raised by Thomas Stockhammer, chair of MPEG-DASH,
  during the review of earlier iterations of the proposal.)

  **Conformance criteria** (document-level):
  - **R10.1** (spec document): Spatial arrangement of overlays MUST
    be delegated to HTML5 / CSS layout primitives.
  - **R10.2** (spec document): The specification MUST NOT define a parallel
    layout standard for overlay placement.
  - **R10.3** (spec document): Position semantics inside a layout
    (left, right, top, bottom, etc.) are out of scope for the spec
    and MUST be expressed via the Positioning Templates section
    using HTML5 / CSS primitives.

## Out of Scope

- **OOS-1. Building a new layout engine.** Spatial arrangement of
  overlays is delegated to HTML5 and CSS, aligned with the IAB CTV
  Ad Standard. The specification MUST NOT define a parallel layout
  standard.
- **OOS-2. Defining the ADS's internal decisioning logic.** The
  proposal only specifies the contract between the MPD event and
  the ADS response. Targeting, frequency capping, brand safety
  filtering and similar concerns remain implementation-specific.
- **OOS-3. Specific position semantics inside a layout** (left,
  right, top, bottom). Those belong to the per-layout detail
  covered in the Positioning Templates section of the proposal.
- **OOS-4. Creative carrier formats outside R15.** Carriers other
  than the admissible set defined in R15 — for example raw
  JavaScript (`application/javascript`), SVG-as-payload, PDF,
  proprietary binary creatives — are out of scope for this edition.
  Senders that need scripted creatives MUST wrap the script inside
  an HTML document and use `text/html` per R15.

The remainder of the proposal — Positioning Templates, Anatomy of
the Overlay Resolution Document, Ad Tracking, Client Execution Flow,
Example Implementation — should be read against these requirements.
Where a design choice satisfies several Rs in tension, the trade-off
is made explicit in the corresponding section.

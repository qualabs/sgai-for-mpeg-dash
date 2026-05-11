# Requirements

> R2 anchors on the three-actor model defined in
> [`02-actors.md`](02-actors.md). R8 is grounded in
> [`adr-004-device-aware-ad-selection.md`](../decisions/adr-004-device-aware-ad-selection.md).
> Use cases that exercise these requirements across device classes
> and ad opportunity types live in [`04-use-cases.md`](04-use-cases.md).

The requirements below govern the design of the proposal. They are
grouped into functional, governance / non-functional, and
out-of-scope. Each numbered requirement is referenced later in design
discussions; any design choice that conflicts with one must explicitly
state the conflict and the justification. This section mirrors the
working doc verbatim.

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
- **R2. Honour the actor's responsibilities.** The design must
  enforce the separation defined in the Actors and Responsibilities
  section: the Broadcaster declares constraints, the ADS provides
  candidates, and the Player validates and renders. New mechanisms
  must be expressible within this contract.
- **R6. Support a diverse range of device capabilities.** The
  solution must work across the heterogeneity of target devices in
  real CTV / streaming deployments — from devices that can render
  multiple concurrent video decoders plus image and HTML overlays on
  top of video, down to devices with a single video decoder and no
  overlay capability at all. The supported device classes and the
  expected behaviour for each combination of device class and ad
  opportunity are enumerated in the **Use Cases** section.
- **R7. Broadcaster-declared max slot duration, Player-enforced.**
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
  Broadcaster as an opt-in policy on the slot. R7 is a concrete
  instance of R2 — Broadcaster declares the constraint, Player
  enforces it, ADS does not.
- **R8. Device-aware ad selection.** The Player is the sole
  authority on device capability — the ADS does not need a
  device-class matrix or a per-Player view. Ad candidates returned
  by the ADS carry one or more **renderable forms** (e.g. video,
  image, HTML), optionally ranked by ADS hints. The Player MUST
  choose the best form it can render given its device, and MUST
  skip candidates with no renderable form (falling back to the
  next candidate or to primary content, depending on policy).
  Rationale and trade-offs in
  [`adr-004`](../decisions/adr-004-device-aware-ad-selection.md).
  R8 is a concrete instance of R2 — Player owns the responsibility
  the ADS does not have — and a direct contributor to R6.

## Governance Requirements

- **R3. Justify any addition or omission.** Whenever the proposal
  introduces a new construct or chooses not to reuse a construct
  that already exists in MPEG-DASH, the document must explicitly
  state why. The default is reuse; departures are documented inline
  with the design decision.
- **R4. Minimise net new constructs.** The proposal must reuse
  existing MPEG-DASH machinery (events, manifests, presentations,
  schemes) wherever possible. New constructs are introduced only
  when an existing one cannot be made to fit, and only after
  considering whether an extension to the existing construct would
  suffice.
- **R5. Do not recreate a layout system.** The solution must defer
  to existing layout primitives (HTML5 / CSS) for the spatial
  arrangement of overlays. Maintaining a parallel layout standard is
  out of scope and adds long-term maintenance cost. (This
  requirement was raised by Thomas Stockhammer, chair of MPEG-DASH,
  during the review of earlier iterations of the proposal.)

## Out of Scope

- Building a Qualabs-specific or SVTA-specific layout engine. Layout
  is delegated to HTML5 and CSS, aligned with the IAB CTV Ad
  Standard.
- Defining the ADS's internal decisioning logic. The proposal only
  specifies the contract between the MPD event and the ADS response.
  Targeting, frequency capping, brand safety filtering and similar
  concerns remain implementation-specific.
- Specific position semantics inside a layout (left, right, top,
  bottom). Those belong to the per-layout detail covered in the
  Positioning Templates section of the proposal.

The remainder of the proposal — Positioning Templates, Anatomy of
the Overlay Resolution Document, Ad Tracking, Client Execution Flow,
Example Implementation — should be read against these requirements.
Where a design choice satisfies several Rs in tension, the trade-off
is made explicit in the corresponding section.

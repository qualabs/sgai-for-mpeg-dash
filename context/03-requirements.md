# Requirements

> R2 anchors on the four-actor model defined in
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
  construct's default OR is fixed by another rule
  MUST NOT exist in the spec. The argument "we might want this
  attribute later" is explicitly rejected — good ideas for the
  future stay in the future, they do not enter the spec
  speculatively. Less is more.
- **DP-1.2. Single source of truth.** When the same value or
  relationship appears in multiple places in the spec or in a
  generated MPD, exactly ONE declaration is canonical and the
  others MUST be derived from it (computed at runtime by the
  implementer, not duplicated in the markup). Duplicating a
  value across attributes invites silent drift when one is
  modified and the other forgotten. Two declarations the base
  specification itself provides, and reconciles by its own rule, are
  not a duplication under this principle; the base rule is adopted
  (R1.5). A Linked Period's `@duration` and its Imported Period's
  `Period@duration` are such a pair: DASH §5.3.2.6.3 step 3)d)iii keeps
  the smaller of the two.
- **DP-2. Obligations are positive.** When the spec states what an
  actor MUST do, it states the positive obligation — the action,
  the construct, the value. The spec does NOT enumerate
  prohibitions. The space of "what is forbidden" is unbounded;
  declaring it exhaustively is impossible and a long list of
  "MUST NOT" items invites confusion and silent gaps. Instead,
  the positive obligation defines the contract; anything outside
  the positive obligation is implicitly out of scope. What
  changes is which side of the line the obligation sits on, not
  whether there is one: the normative modal stays. (For
  example: instead of saying "the Player MUST NOT fire tracking
  beacons after the slot end," say "the Player MUST fire
  tracking beacons within the slot window.")
- **DP-3. Maximize the ad opportunity, never at the cost of
  playback.** When a design choice affects how fully an ad
  opportunity can be used, prefer the option that uses it most —
  subordinate always to one hard invariant: applying this
  specification MUST NEVER break primary-content playback, so when
  an opportunity cannot be honoured, graceful skip-and-continue is
  mandatory. This invariant is not this specification's invention. The
  base specification states it for its own execution model — *"If no
  event can be successfully executed, the playback continues
  uninterrupted"* (§5.16.2.2.5), and *"A failed execution results in
  smooth continued playback of the main media presentation"*
  (§5.16.2.2.6) — and what this principle does is extend the same
  guarantee to the constructs added here. Which ads fill the
  opportunity, and the revenue they yield, are the ADS's concern, not
  this specification's.

## Requirements

Requirement numbers are **stable identifiers, not positional ones**:
a requirement's number never changes once assigned. The requirements
below are grouped into thematic sub-sections for navigation; within
each sub-section they appear in ascending numeric order, so numbers
are deliberately non-contiguous within a section. Cross-references
throughout the spec are by number ("per R13", "see R20"), never by
position, so a requirement keeps its meaning regardless of where it
sits.

### Core invariants (read first)

The requirements below are grouped into thematic sub-sections, but a
handful are foundational: they depend on nothing else in the set, and
everything else is built on top of them. A reader new to the spec can
start from these, then drop into the full text. Each is defined in full
in the section noted below; the numbers are stable identifiers, not
positions.

| Req | Core invariant (one line) |
|---|---|
| R1 | SGAI extends MPEG-DASH 6th edition without breaking it; a legacy Player ignores the new constructs and keeps playing, and where the base already answers a question its answer wins. |
| R2 | Four actors, fixed roles: the Publisher declares, the ADS decides, the APS converts, the Player validates and renders. |
| R4 | The Publisher declares a maximum on every overlay and pause slot; the Player enforces it even mid-ad, and what it bounds depends on the family. An inherited linear event keeps the base rule: its maximum is optional and unbounded when absent. |
| R5 | Candidates carry one or more renderable options in preference order; the Player renders the first its device can satisfy, and a single-option candidate leaves the choice with the APS. |
| R11 | Independent of VAST, and covers what a VAST-based ADS expresses. |
| R12 | A fixed, closed set of IAB ad types (linear, overlay, squeezeback, pause-ad); nothing else is in scope. |
| R18 | The Player-visible interface is specified, including what the Player sends on the resolution request; the APS-to-ADS and ADS-side APIs are out of scope. |
| R22 | At most one non-linear ad form is active on screen at any instant. |
| R35 | The viewer may dismiss a whole ad slot; the APS declares whether that is allowed and after how many seconds. |
| R36 | An overlay or pause opportunity may be resolved ahead of time, within the offset the Publisher declares or 60 seconds when it declares none, and the APS declares how long that resolution keeps. |
| R37 | A pause is what the viewer experiences; any mechanism that suspends the content and resumes it where it stopped is one. |
| R38 | When a non-linear slot declares its allowed layouts, the Player forwards them to the APS and still checks what comes back; a slot that declares none admits only its own family's layouts. |
| R39 | An optional `custom` overlay layout: the APS places the overlay in a rectangle given in percent of the video, inside a region the Publisher may bound. |
| R40 | A non-linear window is presented only over the presentation that declares it, unless the Publisher declares on it that it supersedes the linear event it overlaps or is composited on top of it. |

### Contract foundations

Requirements that fix what the proposal extends and the contract it
must respect — the MPEG-DASH baseline, the actor responsibilities,
and the boundaries of what this spec does and does not define.

- **R1. MPEG-DASH 6th edition compliance and graceful degradation.**
  *Gist: SGAI extends MPEG-DASH 6th edition without breaking it; a Player that does not implement the new constructs ignores them and keeps playing the primary content, and where the base specification already answers a question, its answer is the one adopted.*

  The solution MUST extend MPEG-DASH 6th edition without breaking
  existing semantics. Backward compatibility is mandatory, and it is a
  property of the document rather than an obligation on a Player this
  specification cannot bind (DR-8, ADR 0009): every new construct
  introduced by this proposal MUST be placed at an MPEG-DASH 6th
  edition extension point whose base semantics let a Player that does
  not implement this specification ignore it and continue playing the
  primary content uninterrupted. The expected behavior of a legacy
  Player encountering the new constructs is captured as **UC-07**
  in [`04-use-cases.md`](04-use-cases.md).

  **Conformance criteria** (runtime + document-level):
  - **R1.1** (spec document): Every SGAI construct introduced by this
    proposal MUST sit at an extension point where removing it, as a
    Player that does not implement this specification does under the
    base rules for unrecognised elements and attributes (§5.2.1),
    leaves a valid MPD whose primary content plays uninterrupted.
  - **R1.2** (Publisher / spec document): Every new SGAI construct
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
  - **R1.3** (Publisher / spec document): The specification MUST NOT alter
    or override the semantics of any pre-existing MPEG-DASH 6th
    edition construct.
  - **R1.4** (Player): When resolving or rendering an accepted ad
    fails at runtime (for example a decode error, a malformed
    candidate, or a mid-ad network loss), the Player MUST abort that
    ad and continue playing the primary content uninterrupted. This
    matches what the base specification already requires of its own
    execution model (§5.16.2.2.6); the criterion states it for the
    constructs added here rather than introducing it.
  - **R1.5** (spec document): Where the base specification already
    defines a behaviour, a default or a construct for a question this
    specification has to answer, the base specification's answer takes
    precedence: this specification adopts it and cites it. It defines
    its own answer only where the base specification gives none, and
    declares that answer as an extension. A decision that departs from
    the base answer anyway is an exception recorded with its reason.
    ADR 0006 records the principle.

- **R2. Honour the actor's responsibilities.**
  *Gist: Four actors with fixed roles: the Publisher declares constraints, the ADS decides which ads to serve, the APS converts that into the resolution document, and the Player validates and renders.*

  The design must
  enforce the separation defined in the Actors and Responsibilities
  section: the Publisher declares constraints, the ADS decides which
  ads to serve and emits its decision document, the APS converts that
  decision into the resolution document the Player reads, and the
  Player validates and renders. New mechanisms must be expressible within this contract.

  **Conformance criteria** (runtime + document-level):
  - **R2.1** (Publisher): Constraints applicable to an ad slot
    (max duration, opt-in policies, layout templates) MUST be
    declared by the Publisher in the `MPD`, not inferred at
    runtime by the ADS, the APS, or the Player.
  - **R2.2** (ADS + APS): The ADS MUST decide which ads to serve and
    output them as its decision document — typically VAST, though the
    ADS is not bound to it. The APS MUST convert that output into the
    resolution document carrying the ad candidates. Enforcing the
    Publisher-declared constraints (e.g. the slot duration cap) is the
    Player's obligation under R2.3, and this specification places no
    such obligation on the ADS or the APS.
  - **R2.3** (Player): The Player MUST validate the candidates in
    the resolution document against Publisher-declared constraints
    and render only those that satisfy them.
  - **R2.4** (spec document): Every new mechanism introduced by the
    specification MUST be expressible within the four-actor contract; any
    mechanism that would require an actor to take on a
    responsibility outside its role MUST be rejected or redesigned.

- **R11. Independent of VAST, compatible with what VAST expresses.**
  *Gist: The spec never depends on VAST or any specific VAST version, and covers the ad behaviours a VAST-based ADS can express; VAST references are illustrative only.*

  The specification MUST NOT depend on any
  specific version of VAST or on VAST as a protocol. Examples that
  show interoperability with a specific VAST version are
  illustrative only — conformant implementations MUST be
  VAST-version-agnostic, and the spec MUST NOT impose VAST as a
  precondition for any actor.

  **Conformance criteria**:
  - **R11.1** (spec document): The normative chapters of the spec
    MUST NOT cite a specific VAST version as required.
  - **R11.2** (Player): A Player MUST be able to operate regardless
    of whether the ADS uses VAST. The Player never talks to the ADS
    directly; it reads only the resolution document the APS produces.
    This spec starts from the resolution document — the conversion
    from the ADS's decision format (VAST or otherwise) into the
    resolution document is performed by the APS and is NOT defined by
    this spec. The ADS-side protocol (VAST or otherwise) is internal
    to the ADS / APS pair, not the spec's Player-facing contract.
  - **R11.3** (spec document): A normative statement MUST NOT require
    VAST, and MUST NOT describe an actor's behaviour in terms that
    only a VAST deployment satisfies. Naming VAST as the typical case
    is permitted where the same sentence states that the actor is not
    bound to it. Everything beyond a named typical case — a field
    mapping, a message example, a version — MUST be in an annex or in
    a non-normative note explicitly flagged as illustrative.
  - **R11.4** (spec document): The spec MUST cover the ad behaviours
    a VAST-based ADS can express, so that an APS fed by VAST can
    build a resolution document for each of them using only the
    semantics this spec defines. Independence from VAST is a
    constraint on what the spec cites, not a licence to leave
    uncovered what the deployed ecosystem already does.
  - **R11.5** (spec document): An annex SHOULD carry a worked
    example of an APS building a resolution document from a VAST
    response, because that is how the resolution document is
    produced in practice. The annex is illustrative: it constrains
    no implementation and defines no semantics.

- **R18. The APS-to-ADS and ADS-side API contracts are not defined by this spec.**
  *Gist: The spec defines only the Player-visible interface; the APS-to-ADS and ADS-side APIs are out of scope and agreed bilaterally.*

  This specification does NOT define the URL syntax, parameter
  names, request payload, response payload, or any other aspect
  of the APS-to-ADS API, nor of the ADS-side API. The specification
  documents only the **Player-visible interface** — the MPD event
  URL referenced by the Publisher (which resolves to the APS), and
  the resolution document the APS returns (`ListMPD` or
  single-period alternative MPD). It does NOT define (a) the
  request/GET used to obtain the ADS's decision document, nor (b)
  the format of that decision document (VAST or otherwise). It
  treats the APS internal contract (how the APS invokes the ADS,
  obtains its decision document, and converts it, the decisioning
  inputs, frequency-cap signals) as opaque, agreed bilaterally
  out-of-band.

  **Conformance criteria** (document-level):
  - **R18.1** (spec document): The specification documents the
    MPD event URL pattern (Player-visible input, served by the APS)
    and the resolution document format (Player-visible output,
    produced by the APS).
  - **R18.2** (Publisher / APS / ADS): The APS-to-ADS contract for ad
    decisioning invocation is established and maintained by those
    parties directly, outside this specification. The Publisher's
    arrangement with the APS for the event URL remains bilateral,
    except for the parameters this specification defines on the
    Player's resolution request (R29).

- **R29. Player-declared capability parameters on the resolution request.**
  *Gist: The Player MAY attach reserved capability parameters — inputs about the device, not conclusions about what can be served — to the resolution request it sends the APS; each is optional except the slot's allowed layouts (R38), and one the Player cannot or will not populate is omitted rather than sent empty.*

  This specification defines a set of **reserved parameter names** that a
  Player MAY attach to the resolution request it issues against the MPD
  event URL. Which of them travel is the Player's decision, taken at
  runtime; no declaration by the Publisher, the APS or the ADS is
  required before a Player sends them.

  These parameters are carried as query parameters on the resolution
  request. They are defined here and are NOT expressed through the
  MPD-declared URL-parameter template mechanism of MPEG-DASH 6th
  edition, whose contents are declared by the content author.

  **Conformance criteria** (runtime + document-level):
  - **R29.1** (spec document): The reserved parameters are **inputs
    about the device** — statements of what the device supports — and
    not conclusions about which ad experiences can be served; deriving
    the second from the first is the APS's. Device capability has more
    than one axis, so what this specification reserves is a set and not
    a single value. Which parameters the set contains, and how each is
    written, is fixed when the syntax is specified.
  - **R29.2** (Player): Sending a reserved parameter is OPTIONAL. A
    Player conformant to this specification MAY send all of them, some
    of them, or none.
  - **R29.3** (Player): When the Player has no value for a reserved
    parameter, or does not disclose its value, the Player MUST omit that
    parameter entirely rather than send it with an empty or placeholder
    value.
  - **R29.4** (Player): A parameter that is not one of the reserved names
    MUST carry a vendor-specific prefix, so that reserved names added in
    a later edition cannot collide with it.
  - **R29.5** (APS): The APS MUST tolerate the absence of any reserved
    parameter and MUST be able to produce ad candidates without receiving
    any of them. An APS that requires a parameter in order to answer
    would make R29.2 unattainable for the Player.
  - **R29.6** (spec document): The reserved set MUST be able to express
    the capability axes that distinguish the device classes this
    specification enumerates (R3.1). A set that cannot tell two
    enumerated device classes apart does not satisfy this requirement.
  - **R29.7** (spec document): A reserved parameter absent from the
    resolution request means its value is **undetermined** — the
    Player did not determine it, or did not disclose it. Absence does
    NOT assert that the device lacks the capability. This
    specification does not define how an APS resolves an undetermined
    value; that is the APS's decision, and two APSs that resolve it
    differently are both conformant.
  - **R29.8** (spec document): R38.2 and R39.3 are the exceptions to
    R29.2: when a non-linear slot declares allowed layouts, or a custom
    region, the Player is required to send them. Every other reserved
    parameter remains optional.

### Opportunity declaration

Requirements that define what the Publisher and the IAB declare about
an ad opportunity before any ad is selected — the slot cap, the
admissible ad-type vocabulary, and the admissible creative carriers.

- **R4. Publisher-declared max slot duration, Player-enforced.**
  *Gist: The Publisher declares a maximum on every overlay and pause slot, and the Player enforces the maximum a slot declares, cutting mid-ad rather than overrunning; what it bounds depends on the family, an inherited linear event keeps the base rule that an absent maximum is unbounded, and the ADS is not responsible for it.*

  The Publisher declares a maximum on each ad slot. On the non-linear
  slots this specification defines the declaration is required; on an
  inherited linear slot (start-of-session, mid-content, multi-ad break)
  it is the base specification's own maximum, which the base
  specification makes optional (R4.8). The ADS may return one or more ad
  candidates to fill that slot, but the ADS is **not** responsible for
  respecting the cap. The Player MUST enforce it, stopping at the
  bound even when the stop falls mid-ad. R4 is a concrete instance of
  R2 — Publisher declares the constraint, Player enforces it, ADS does
  not.

  Overflow policies other than stopping at the bound — skip the break
  entirely, trim clean at the previous ad boundary, fail closed — are
  out of scope for the default semantics and would have to be
  expressible by the Publisher as an opt-in on the slot. One such
  policy already exists and is not ours to invent: `@clip` decides
  what a late start does to a replacement slot, and it is described
  below with the rest of the family behaviour.

  **What the cap bounds is not the same in every family, because the
  base specification makes it so.** On an inherited linear slot the cap
  is `AlternativeMPDEventType@maxDuration`, *"expressed in units of
  `EventStream@timescale`"* (§5.16.5), and what it bounds differs
  between the two linear operations:

  - **Replacement** (`ReplacePresentation`) — the cap bounds **until
    when**. `@clip`, whose default is `"true"`, makes the alternative
    presentation *"terminate at the latest at time PRT + APDmax"*,
    the end the Publisher scheduled, whatever time the event actually
    fired. Starting late therefore shortens the ad instead of moving
    the end. With `@clip="false"` it terminates at `PRTA + APDmax` and
    the slot ends later than scheduled.
  - **Insertion** (`InsertPresentation`) — the cap bounds **how
    long**. `@clip` does not exist on the insertion event, and could
    not: insertion stops the primary timeline and resumes it at
    `RT = PRTA` (§5.16.2.2, Table 57), so there is no scheduled end to
    preserve and starting late displaces nothing.

  The asymmetry is not an exception granted to one construct. It
  follows from the two operations being different: replacement runs
  against a timeline that keeps moving underneath it, and insertion
  stops that timeline. A cap that meant the same thing in both would
  be wrong in one of them.

  On the non-linear families this specification defines there is no
  `PRT` / `PRTA` model to preserve an end against, and the cap bounds
  the cumulative duration of what the slot presents (R4.2, R14.2) —
  with one exception. A **pause** slot has no declared duration for a
  cap to bound: the viewer decides how long it lasts, and R31 states
  what follows from that.

  So "the cap" names one Publisher declaration and two things it can
  bound. The criteria below are written against that: R4.4 and R4.5
  hold in every family, R4.1 in the families this specification
  defines, R4.2 is the cumulative-duration rule, and
  R4.6 is what replaces it where the base specification bounds an end
  instead.

  **Conformance criteria** (runtime):
  - **R4.1** (Publisher): The Publisher MUST declare a maximum
    duration on every overlay and pause slot defined in the `MPD`. On
    an inherited linear event the maximum is the base specification's
    `@maxDuration`, which the Publisher MAY omit (R4.8).
  - **R4.2** (Player): Where the cap bounds cumulative duration — the
    non-linear families, and linear insertion — the Player MUST stop
    rendering once the cumulative duration of the accepted candidates
    would exceed it, even if the stop falls mid-ad.
  - **R4.3** (Player): The Player MUST NOT extend a slot beyond what
    the cap bounds for that slot's family (R4.6), regardless of ADS
    metadata or candidate count. On a replacement slot the bound is
    the scheduled end, so an event declaring `@clip="false"` ends
    later than that end without violating this criterion — it is the
    base specification moving the bound, not the Player exceeding it.
  - **R4.4** (ADS): The ADS is NOT required to respect the cap when
    selecting candidates; a conformance check on the ADS MUST NOT
    fail solely because the cumulative duration of its returned
    candidates exceeds the cap.
  - **R4.5** (Player): When the actual rendered length of an
    accepted candidate exceeds its declared duration, the Player
    MUST enforce the cap against actual length, not declared
    length ("trim during play").
  - **R4.6** (Player): On an inherited linear replacement slot, the
    Player MUST honour the base specification's clip semantics: unless
    the event declares otherwise, the presentation ends at the
    scheduled end of the slot and a late start shortens it rather
    than moving that end. Insertion has no clip semantics to honour
    and falls under R4.2.
  - **R4.7** (Publisher + Player): A declared cap of zero means the
    opportunity does not fire. The base specification states it
    directly — *"If the value of `@maxDuration` is zero, the event is
    not executed"* (§5.16.5) — and this specification adds nothing to
    it: a zero cap is not a very short slot.
  - **R4.8** (spec document): R4.1 requires a cap on the slots this
    specification defines and on no inherited linear event. For those
    the base answer stands (R1.5): an absent `@maxDuration` *"is
    assumed to be infinity, in which case the current presentation
    resumes only when the alternative presentation terminates"*
    (§5.16.5). An alternative presentation need not be an ad — the
    base specification names blackouts beside advertising (§5.16.1)
    and a Player cannot tell the two apart (R40) — and a blackout with
    no known end is written exactly that way. Requiring a cap there
    would make a Player of this specification refuse the blackout and
    show the programme the Publisher had blacked out. On an overlay or
    pause slot every declaration is an advertising opportunity, and a
    missing cap costs a slot that sells nothing, which the Publisher
    sees and fixes with one attribute.
  - **R4.9** (Player): The cap and a candidate's declared duration are
    stated in different timebases — the cap in the units of the parent
    `<EventStream>@timescale`, a candidate's duration as an ISO 8601
    `xs:duration`. The Player MUST convert the candidate's duration
    into the cap's timescale before comparing the two, and MUST round
    the converted value **up** to the next whole unit of that
    timescale. A candidate whose converted duration equals the cap
    exactly is admitted.
  - **R4.10** (Player): An overlay or pause slot declaration carrying
    no maximum duration is not a slot this specification defines
    (R4.1). The Player MUST NOT present ads from such a slot and MUST
    continue with the primary content. Reading the absence as an
    unbounded default is not admissible: it would make R4's
    Player-side enforcement inert for exactly the slots whose
    declaration is defective. An inherited linear event with no maximum
    is outside this criterion: the Player executes it with its base
    semantics (R4.8).

    A Publisher who wants non-linear advertising with no fixed end
    writes it as a chain of bounded slots — N slots of X seconds along
    the primary content — which this specification already allows and
    which needs no new construct. Keeping an unbounded slot would buy no capability
    the chain does not already give, and would cost every
    cap-dependent requirement a second reading for a shape almost
    nobody authors. ADR 0015 records the decision and what it
    deliberately does not change about the pause family (R31); ADR
    0020 records why inherited linear events are outside it.
  - **R4.11** (Player): The Player MUST compute the cap on the
    presentation timeline. An interval during which the presentation
    timeline does not advance MUST NOT accrue against the cap, so a form suspended
    under R17 resumes with the remaining cap it had when it was
    suspended. The only suspension this specification defines happens
    while the viewer is paused (R17.1), and a pause does not advance
    the presentation timeline.

- **R31. A pause opportunity window bounds where, not how long.**
  *Gist: The window marks the region of the primary timeline in which a viewer pause triggers a resolution request; the duration of the resulting slot is set by the viewer and is unknown in advance.*

  A pause opportunity window declares a region of the primary
  timeline. A viewer pause that begins inside that region triggers the
  resolution request; the window does not schedule a presentation and
  does not predict one. How long the resulting slot lasts is
  determined entirely by the viewer and is unbounded and unknowable
  when the document is authored.

  Every other slot family this specification defines has a duration
  the Publisher can declare. A pause slot does not. Requirements
  written on the assumption of a declared duration — the slot cap (R4)
  among them — do not bound a pause slot: the viewer bounds it.

  **Conformance criteria** (runtime):
  - **R31.1** (Player): The Player MUST request a resolution document
    when a viewer pause begins inside a pause opportunity window, and
    MUST NOT request one for a pause that begins outside every such
    window.
  - **R31.2** (Publisher + Player): The Publisher-declared slot cap
    (R4) MUST NOT be interpreted as bounding the duration of a pause
    slot. R4's cap bounds an end on a replacement slot and a
    cumulative duration elsewhere; on a pause slot it bounds neither,
    because there is no authored duration for it to bound.

- **R12. Ad types and formats supported by this edition.**
  *Gist: This edition supports a fixed, closed set of IAB ad types (linear, overlay, squeezeback, pause-ad); anything not listed, or rendered off the video surface, is out of scope.*

  Ad types and
  their visual templates are defined and maintained by the IAB. This
  specification references those definitions normatively; it does not
  introduce new ad-type categories or new visual templates. On top of
  that principle, this edition supports an explicit, closed subset of
  the IAB catalogue. The ad types and visual placements enumerated below
  are the complete set that a conformant Publisher, APS, and Player
  handle under this edition. Each entry names the IAB ad type it maps to
  (identifier in `code`) and, where the IAB type has named visual
  placements, the placement.

  The enumeration is edition-scoped by design. An IAB ad type or visual
  placement that is not listed below is out of scope for this edition,
  and an ad type or placement that the IAB publishes later does NOT
  enter scope automatically; widening the set requires a new edition of
  this specification. This is a deliberate per-edition snapshot, not a
  runtime limitation to work around.

  **Supported ad types and placements** (all rendered on or within the
  video surface):

  - **Linear** (IAB *Linear Ad*, `linear`): a full-viewport ad that
    takes over the primary content surface for the slot. Supported
    timing positions are pre-roll, mid-roll, and multi-ad breaks (two
    or more linear ads presented back-to-back within one slot).
    A full-screen takeover is the `linear` full-viewport
    rendering offered as a fallback presentation option for a candidate
    whose richer non-linear options are not renderable on the device
    (see UC-09 in [`04-use-cases.md`](04-use-cases.md)); it is a
    placement of the `linear` type, not a separate ad type.
  - **Overlay** (IAB *Overlay*, `overlay`): a non-linear surface
    composited on top of the primary content, which keeps playing. Its
    named visual placements are corner / bug (`overlay-corner`, IAB
    *Corner Overlay*) and lower-third (`overlay-lower-third`, IAB
    *Lower-Third Overlay*); a plain image or HTML overlay with no named
    placement is the base `overlay` type. Which corner an
    `overlay-corner` occupies is not a token and not this
    specification's business: the Player composites the creative over
    primary content it does not transform, so the corner follows from
    the creative and is rendered with HTML5 / CSS (R10.1, R10.3).
  - **Squeezeback** (IAB *Squeezeback*, `squeezeback`): a non-linear
    layout in which the primary content is shrunk to share the frame
    with the ad. Supported placements, with the region each one leaves
    for the primary content:

    | Token | Primary content occupies | IAB type |
    |---|---|---|
    | `squeezeback-l-shape-upper-left` | the upper-left 60% of the frame; the ad runs across the bottom and up the right edge | *L-Shape* (see R27) |
    | `squeezeback-l-shape-upper-right` | the upper-right 60% of the frame; the ad runs across the bottom and up the left edge | *L-Shape* (see R27) |
    | `squeezeback-double-box` | the centre-left 25% of the frame; the ad occupies the centre-right 25% | *Double Box Video* (see R26) |
    | `squeezeback-double-box-background` | the centre-left 25% of the frame; the ad occupies the centre-right 25%, over an advertiser-branded background | *Double Box Video + Background* (see R26) |

    **The token carries the geometry because nothing else does.** The
    Player shrinks and repositions the primary content here, which it
    does for no other ad form, so it needs the region before it
    composes. The creative arrives as an underlay whose cutout shows
    the region to a viewer, but a hole in an image is not a rectangle a
    Player can compute with, and the IAB guidelines define no field
    that carries one. Two orientations of an L-shape are therefore two
    tokens and not one token plus an orientation: they are two
    compositions. ADR 0014 records this, including why it does not
    reopen R10.2 — what is enumerated is which composition is in play,
    not where something sits inside it.
  - **Pause-ad** (IAB *Pause Ad*, `pause`): a non-linear surface shown
    over the paused primary frame. Its two visual placements are
    **fullscreen** (`pause-fullscreen`), occupying the entire screen
    surface, and **partial overlay** (`pause-partial`), composited over
    the paused primary frame which remains visible underneath (see
    R21). Unlike `overlay`, the bare `pause` type is **not** an
    admissible layout value: every pause ad is one surface or the
    other, so a declaration naming neither would leave R21's choice
    undetermined. The two placements are separate for the reason
    Overlay's and Squeezeback's are — R21 makes the surface a property
    of the layout the Player selects, and a Publisher can only admit
    one and exclude the other if the two are distinguishable in
    `@allowedLayouts`.

  **Out of scope: ads outside the video surface.** The supported set
  above is closed. Ads the application renders outside the video
  surface are excluded by OOS-9.

  Reference (live link, not snapshotted):
  https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e

  **Conformance criteria**:
  - **R12.1** (spec document): The accepted ad-type and visual-placement
    values are exactly those enumerated in this requirement, each mapped
    to its IAB definition, plus the optional `custom` overlay layout of
    R39, which is the one value with no IAB counterpart. The spec MUST
    NOT accept a value outside the enumeration, and MUST cite the IAB
    source for the values it accepts.
  - **R12.2** (Publisher): Publishers declaring allowed layouts MUST use
    only these tokens, which are the complete list: `linear`, `overlay`,
    `overlay-corner`, `overlay-lower-third`,
    `squeezeback-l-shape-upper-left`, `squeezeback-l-shape-upper-right`,
    `squeezeback-double-box`, `squeezeback-double-box-background`,
    `pause-fullscreen`, `pause-partial`, and the optional `custom` (R39).
    Every token except `custom` names one IAB ad type or visual
    placement; the IAB catalogue holds many more, and none of them is
    admissible. The bare `squeezeback` and `pause` are not tokens,
    because neither says which composition the Player builds.
    Publisher-private layout names MUST NOT appear in the
    allowed-layouts declaration on the slot either.
  - **R12.3** (APS): The ad-type set originates in the ADS's decision.
    The APS MUST NOT emit, in the resolution document, form metadata
    for an ad type or visual placement outside the enumerated set.
    Conformance is checked against the APS's resolution document, not
    against the ADS's internal decision document.
  - **R12.4** (spec document): Each enumerated layout implies the
    spatial bound declared by the IAB CTV Ad Format Guidelines for that
    layout (e.g. Corner Overlay no more than 25% of the frame,
    Squeezeback L-Shape primary content 60% of the frame). The spec
    inherits these bounds by normative reference rather than
    re-declaring them MPD-side; no dimensional attribute is introduced
    on the slot declaration. See
    `../.project/decisions/0001-defer-to-iab-ctv-for-spatial-caps.md`.

- **R15. Admissible creative carrier formats.**
  *Gist: Ad creatives come in exactly three carrier formats: video, image, and HTML.*

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
  - **R15.2** (APS + Publisher): Ad candidates in the resolution
    document the APS produces (carrying the creatives the ADS
    selected) and forms declared by the Publisher MUST carry a
    creative whose mimeType falls under one of the three admissible
    categories defined above. The admissible set originates in the
    ADS's decision; conformance is checked against the APS's
    resolution document and the Publisher's declaration, not against
    the ADS's internal decision document.
  - **R15.3** (Player): The Player MAY skip a candidate whose
    creative carrier mimeType is not in the admissible set; such
    a candidate signals a non-conformant ADS, APS, or Publisher.

### Selection and ordering

Requirements that govern how the Player chooses among candidates and
in what order it presents them: device-aware selection and honouring
the order the resolution document declares.

- **R5. Device-aware ad selection.**
  *Gist: Each candidate carries one or more renderable presentation options in preference order and the Player renders the first one its device can satisfy, skipping candidates with none; an APS that wants the choice to sit with it sends exactly one.*

  The Player is the authority on what its own device can render: no
  presentation option reaches the screen without passing the Player's
  capability check. This specification therefore requires no
  device-class matrix and no per-Player capability view at the ADS or
  the APS, and an implementation whose APS does hold one is equally
  conformant; the Player's check is unchanged. Ad candidates in the
  resolution document the Player reads carry one or more
  **renderable presentation options**, each a **form (video, image,
  HTML) together with its layout**. The options appear as an
  **ordered list — document order IS the preference order; there is
  no separate priority or ranking attribute**. The Player MUST render
  the **first presentation option whose form and layout its device
  can satisfy**, and MUST skip candidates with no satisfiable option,
  falling through to the next candidate and continuing with the primary
  content only once every candidate is exhausted. R5 is a concrete
  instance of R2 — Player owns
  the responsibility the ADS and APS do not have — and a direct
  contributor to R3.

  **Several options is the form this requirement asks for**: a candidate
  that carries more than one resolves on devices the ADS and the APS know
  nothing about, which is what makes a single decision serve a
  heterogeneous population. **Carrying exactly one option is equally
  admissible.** An implementation that does not want the Player choosing
  among options sends a single option, and the Player then renders that
  one or skips the candidate — that is the path to take when the decision
  is meant to sit upstream. When a candidate carries one option, that
  choice was made by the APS, or by the ADS that returned a single option
  to the APS, and the responsibility for its suitability sits there.

  The resolution document MAY carry candidates with multiple
  presentation options. The Player MUST select per device
  capabilities and the Publisher's allowed layouts, taking options
  **in document order and rendering the first that passes**. When none
  of a candidate's options is satisfiable, the Player skips that
  candidate and moves to the next candidate; continuing with the primary
  content is the last resort, reached only once every candidate has been
  exhausted.

  **Conformance criteria** (runtime):
  - **R5.1** (APS): Each ad candidate in the resolution document the
    Player reads MUST carry one or more **renderable presentation
    options (each a form plus its layout) as an ordered list, where
    document order is the preference order**. How many options a
    candidate carries is the APS's decision: this specification sets
    no maximum, and no minimum beyond one. Conformance is checked
    against the APS's resolution document, which is the only artefact
    on the path to the Player that this specification defines.
  - **R5.2** (Player): The Player MUST evaluate the presentation
    options of an accepted candidate **in document order** and render
    the **first option** whose form and layout it can satisfy on its
    device.
  - **R5.3** (Player): The Player MUST skip any candidate that
    carries no form renderable on its device and fall through to the
    next candidate; when the candidates are exhausted, the Player MUST
    continue with the primary content.
  - **R5.4** (ADS + APS): This specification MUST NOT be read as
    obliging the ADS or the APS to maintain a device-class matrix or
    a per-Player capability view in order to produce candidates. An
    implementation that keeps one is conformant; one that does not is
    equally conformant.
  - **R5.5** (APS): An ad candidate MAY carry multiple presentation
    options, each pairing a form with an admissible layout. The
    options form a single ordered list, and their document order is
    the preference order the Player follows.
  - **R5.6** (Player): The Player MUST resolve presentation-option
    selection by walking the options in document order and, for each,
    checking it against (a) device capabilities and (b) the layouts the
    slot admits — the Publisher-declared allowed layouts, or those of
    the slot's own family when it declares none (R38.1). The Player renders
    the first option that satisfies both; an option that fails either
    MUST NOT be rendered and the Player moves to the next option in
    document order.
  - **R5.7** (Player): If no presentation option on a
    candidate satisfies R5.6, the Player MUST skip that
    candidate and fall through to the next candidate in the
    resolution document (preserving the order required by R7) or,
    when exhausted, to primary content.

- **R7. Respect the order of the resolution document.**
  *Gist: The Player plays candidates in the order the resolution document declares, only dropping (never reordering) ones it cannot render or that would exceed the slot cap.*

  When the resolution document
  the APS returns contains more than one ad (e.g. a `ListMPD`
  with multiple `<Period>` entries), the Player MUST play the ads
  in the order the resolution document declares,
  **as long as this is possible given the other Player constraints**.
  Specifically, the Player MAY drop a candidate that violates R3 (no
  renderable form for the device) or that would push the cumulative
  duration past the slot cap (R4), but it MUST NOT re-order,
  deduplicate, or otherwise rearrange the remaining candidates. Ad
  selection and ordering happen upstream of the Player (R2); the
  order the resolution document carries is the one the Player honours,
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
  - **R7.1** (Player): Given a resolution document with more
    than one ad candidate, the Player MUST play the candidates in
    the order the resolution document declares, except
    for candidates dropped under R7.2 or R7.3.
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

- **R30. An unsold opportunity is expressed as a document, not as an error.**
  *Gist: A resolution that returned no ads is a well-formed resolution document carrying no candidates; an error response or an absent one means something else and is non-conforming.*

  When the APS resolves an opportunity and the ad decision carries no
  ads, it returns a resolution document that carries no candidates —
  not an error response and not an absent one. What the Player then
  does with that document is R20.1's: the attempt produced no ad, so it
  is a failed execution and the next overlapping window of the family
  is attempted. Where there is no further window, the primary content
  continues uninterrupted.

  This requirement is about **how the unsold opportunity is expressed**,
  not about what follows from it. Expressing it as a document rather
  than as an error is what lets an unfilled opportunity be reported as
  an unfilled opportunity, keeps the APS-to-Player contract free of
  error codes that mean two different things, and leaves the
  distinction visible to anyone auditing the exchange.

  **What "carrying no candidates" means.** The resolution document is
  **well-formed and complete**: it declares itself a resolution
  document and carries every element the syntax requires. What it does
  not carry is a single ad candidate. It is **not** an empty HTTP
  body, **not** a `204`, **not** a `404`, and **not** a document that
  fails to parse. The distinction is between *a document that says
  "nothing was sold"* and *no document at all*.

  **This case is already covered by MPEG-DASH, and the Player's
  behaviour here is DASH's own.** For a linear slot the resolution
  document is a `ListMPD`, and ISO/IEC 23009-1:2026 §5.16.2.2.6 lists
  *"Alternative MPD is a List MPD, and merge process resulted in no
  available media"* among the conditions under which the event's
  execution does not produce an alternative presentation, with the
  prescribed outcome: *"A failed execution results in smooth continued
  playback of the main media presentation."*

  The same clause places an event whose `@executeOnce` has already
  fired under the same heading — a case that is correct by design. In
  DASH that heading therefore means *"this event produced no
  alternative presentation this time"*, **not** *"something went
  wrong"*. Reading it as an error would be the mistake; reading it as a
  failed execution, which is what the base specification calls it, is
  what makes R20.1's fall-through follow.

  **The opportunity is not consumed.** The base specification counts
  executions, not attempts: `E.c` is *"Execution counter (number of
  times alternative MPD playback successfully started)"* (§5.16.2.2.2),
  and §5.16.2.2.6 NOTE 3 states that *"The counter E.c has not been
  incremented due to the failure, consequently if E.c = 0 the event can
  still be executed in the future even if the value of `@executeOnce`
  is `"true"`."* A slot that resolved to no ads therefore leaves the
  opportunity executable. This specification inherits that rule rather
  than restating it.

  **Conformance criteria** (runtime):
  - **R30.1** (APS): An opportunity that resolved with no ads MUST be
    expressed as a resolution document carrying no candidates, and MUST
    NOT be expressed as an error response or as a response without a
    body.
  - **R30.2** (Player): A resolution carrying no candidates MUST NOT
    count as an execution of the opportunity. Where the opportunity's
    event carries `@executeOnce="true"`, the event remains executable
    afterwards, per §5.16.2.2.2 and §5.16.2.2.6 NOTE 3.

### Presentation

Requirements that govern how ad forms appear on screen: device-class
support, the pause-ad lifecycle, pause-ad presentation surfaces,
playback speed, the live-content presentation-time freeze, and the
squeezeback layouts (side-by-side and L-shape).

- **R3. Support a diverse range of device capabilities.**
  *Gist: The design works across the full spread of target devices, from multi-decoder boxes with image and HTML overlays down to a single decoder with no overlay capability at all.*

  The
  solution must work across the heterogeneity of target devices in
  real CTV / streaming deployments — from devices that can render
  multiple concurrent video decoders plus image and HTML overlays on
  top of video, down to devices with a single video decoder and no
  overlay capability at all. The supported device classes and the
  expected behaviour for each combination of device class and ad
  opportunity are enumerated in the **Use Cases** section. The capability
  axes that separate those classes are what the reserved parameter set
  of R29 must be able to express.

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

- **R16. Pause-ad lifecycle bound to pause state.**
  *Gist: A pause-ad exists only while playback is paused, and the Player dismisses it the instant the viewer resumes.*

  A pause-ad form, by definition, is admissible only while the
  primary content is paused. When the viewer resumes primary
  playback, the Player dismisses any active pause-ad form
  immediately and ceases firing further tracking beacons
  associated with that pause-ad. The pause-ad's lifecycle is
  bounded by the pause-state interval.

  The presentation surface of a pause-ad form — fullscreen or partial
  overlay — is governed separately by R21. The presentation-time freeze
  that keeps a pause-ad admissible in live content is governed
  separately by R25; R16 governs the generic pause-ad lifecycle
  (admissible only in pause, dismissed on resume).

  **Conformance criteria** (runtime):
  - **R16.1** (Player): Upon a pause-to-play transition by the
    viewer, the Player MUST remove any rendered pause-ad form
    from the screen within one rendering frame.
  - **R16.2** (Player): Upon the same transition, the Player MUST
    cease firing tracking beacons scheduled for the dismissed
    pause-ad; beacons scheduled at relative times after the
    transition fall outside the pause-ad's active window and are
    therefore out of scope.

- **R32. Exhausted pause-ad candidates while the viewer is still paused.**
  *Gist: When the pause-ad candidates run out and the pause continues, the APS declares which of three behaviours applies: repeat, request again, or stop.*

  Because a pause slot has no declared duration (R31), the candidates
  a resolution document carries may be exhausted while the viewer is
  still paused. This specification does not leave that state
  undefined, and R5.3's fall-through to primary content does not
  apply: the primary content is paused.

  The resolution document declares which of three behaviours the
  Player applies:

  - **repeat** — the Player presents the sequence again from the
    start, for as long as the pause lasts.
  - **request-again** — the Player requests a new resolution document
    for the same pause.
  - **stop** — the Player presents no further ad; the paused primary
    frame is shown.

  The declaration belongs to the APS and not to the Publisher. A
  Publisher-declared limit on how many documents may be served would
  be answered by APS implementations returning defensively long
  candidate lists, since a single response would be their only
  opportunity — the constraint would produce the outcome it exists to
  prevent.

  `stop` is the default: it is what the viewer would see if this
  mechanism did not exist, and it is the behaviour every Player can
  perform.

  **Conformance criteria** (runtime):
  - **R32.1** (APS): A resolution document for a pause slot MUST
    declare which of the three behaviours applies. Absent the
    declaration, the Player MUST apply `stop`.
  - **R32.2** (Player): Under `request-again`, a resolution document
    carrying no candidates (R30) MUST be treated as `stop` for the
    remainder of that pause.
  - **R32.3** (Player): When the viewer resumes playback, the Player
    MUST return to the primary content immediately, whether or not an
    ad is mid-presentation.
  - **R32.4** (spec document): Whether a second resolution request
    within one pause is the same opportunity or a new one is **out of
    scope**. The two readings are identical at the Player: it requests,
    it renders what arrives, and it stops on resume, in both. What
    differs is accounting between the APS and the ADS, which this
    specification does not observe (R18), so it is in no position to
    fix which reading is correct. What the specification does measure
    is **how much of the paused interval carried an ad** (R33), and
    that figure is the same however the requests are counted.

- **R34. A pause opportunity window may be declared once-per-session.**
  *Gist: The Publisher may declare that a pause opportunity window yields at most one pause ad for the whole session, so a viewer who pauses again inside it is not shown another.*

  The base specification already carries this capability for events on
  the primary timeline: `@executeOnce` bounds an event to a single
  execution in the session. A pause opportunity window is not executed
  by the playhead — its trigger is the viewer's pause (R31) — so the
  attribute's timeline semantics do not reach it on their own. Without
  a statement the capability is either inert on a pause window or caps
  it at one pause ad, and the two readings differ by every pause after
  the first.

  This specification gives the pause family the same capability, and
  states its counter in the terms the trigger actually has. The
  symmetry is the reason: a Publisher who can bound a timeline
  opportunity to one execution can bound a pause opportunity the same
  way, and nothing about a pause makes the wish different.

  **What consumes the window** follows the base specification's own
  rule rather than a new one. The execution counter is not incremented
  when an execution produces no alternative presentation, so an
  opportunity that resolved to nothing stays available. A pause that
  produces no pause ad — no candidate, or none the device can satisfy
  — therefore does not consume the window either.

  This requirement declares a capability, not an attribute name. The
  construct that carries it is named under the rules of
  [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md),
  which is also what keeps it from being minted twice.

  **Conformance criteria** (runtime):
  - **R34.1** (Publisher): The Publisher MAY declare a pause
    opportunity window as once-per-session. The declaration is
    optional, and a window that does not carry it yields a pause ad on
    every qualifying pause.
  - **R34.2** (Player): On a window declared once-per-session, the
    Player MUST present at most one pause ad for that window for the
    duration of the session. A later qualifying pause inside the same
    window MUST leave the primary content uninterrupted.
  - **R34.3** (Player): The Player MUST treat the window as consumed
    when a pause ad **begins rendering**, and not when the pause
    occurs. A pause that resolves to no renderable candidate MUST leave
    the window available.
  - **R34.4** (spec document): The capability is the pause family's
    counterpart of the base specification's single-execution bound,
    and is recorded as such. It is not a new kind of control: a reader
    who knows the base construct knows what this one does.

- **R35. The viewer may dismiss an ad slot, and the APS says whether and from when.**
  *Gist: The APS declares per slot whether the viewer may dismiss it and how many seconds must pass first; dismissing ends the whole slot, never one ad inside it.*

  A viewer who wants their screen back is not the same viewer as one
  escaping an advertisement, and for a non-linear form the second
  motivation is weak — the primary content never stopped. The working
  group agreed on 2026-08-19 that a Player must be able to support a
  viewer-initiated dismissal. Its granularity and its timing are
  settled below.

  **The unit of dismissal is the slot.** A viewer dismisses the whole ad
  slot and never an individual ad inside it. Per-ad dismissal would make
  a viewer who wants their screen back dismiss the same surface several
  times in a row, which is a worse experience than the one it is meant
  to relieve.

  **Whether a slot may be dismissed at all, and how soon, are the APS's
  to declare.** They are properties of the advertising that was sold —
  an advertiser who bought guaranteed exposure and one who did not are
  the same slot to the Publisher — so they travel in the resolution
  document with the candidates, and not in the `MPD`.

  This requirement applies to **every family this edition defines**,
  including the pause family. A pause ad is dismissible on the same
  terms as any other: the viewer is already in control of when it ends
  by resuming (R25), and dismissal gives them the surface back without
  resuming.

  **Dismissal is granted, never assumed.** A slot nobody declared
  dismissible cannot be dismissed (R35.1), so whatever carries the
  declaration has to leave an undeclared slot non-dismissible. The
  carrier is named under the rules of
  [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md), and
  ADR 0017 records the decision.

  **Conformance criteria** (runtime):
  - **R35.1** (APS): The APS MUST declare, for each slot it resolves,
    whether the viewer may dismiss it. A resolution document that does
    not declare it leaves the slot non-dismissible: the capability is
    granted and never assumed.
  - **R35.2** (APS): Where dismissal is allowed, the APS MUST declare
    the number of seconds that MUST elapse, from the moment the slot
    begins rendering, before the viewer may dismiss it. A declared
    delay of zero means the slot is dismissible immediately.
  - **R35.3** (Player): Before that delay has elapsed, the Player MUST
    NOT offer the viewer a way to dismiss the slot. After it has, the
    Player MUST make dismissal available for as long as the slot is on
    screen.
  - **R35.4** (Player): A dismissal ends the **whole slot**. The Player
    MUST stop presenting every ad of that slot and MUST NOT advance to
    another ad or another form within it.
  - **R35.5** (Player): A dismissed slot does not shorten the primary
    content. Where the slot bounded a region of the primary timeline,
    the Player MUST continue from where the primary content stands, and
    MUST NOT compress or skip any part of it.
  - **R35.6** (Player): The Player MUST fire the tracking events the
    resolution document scheduled up to the moment of the dismissal,
    and MUST NOT fire those scheduled after it. A dismissal is an
    outcome of the presentation, not a failure of it.
  - **R35.7** (spec document): How the dismissal is offered — a
    control, a gesture, a remote button — is out of scope. This
    specification states when it must be available and what it ends,
    and the market decides how it is presented.
  - **R35.8** (Player): On a linear slot whose event carries the base
    specification's own skip declaration, written explicitly by the
    Publisher, the Player MUST honour that declaration as the base
    specification defines it, and it governs the slot. The base default
    that applies when the event writes nothing is not a declaration:
    where neither the event nor the resolution document declares
    anything, R35.1's default applies and the slot is non-dismissible. This is R1.5
    applied: a Player of this specification and a base Player treat the
    same linear event the same way.

- **R36. A non-linear opportunity may be resolved ahead of time, and the resolution declares how long it keeps.**
  *Gist: The Publisher may declare how early a Player may resolve an overlay or pause opportunity, 60 seconds when it declares nothing, and the APS declares how long that resolution stays good; a stale one is resolved again.*

  The base specification already lets a Player resolve early on the
  primary timeline: an alternative-MPD event carries an earliest
  resolution time, computed from the event's presentation time minus a
  declared offset (§5.16.5), and the Player may fetch from that instant
  onward. Without the same capability for the non-linear families, the
  Player can only resolve at the moment the opportunity fires, and the
  viewer waits for the APS with the ad surface already due — and a
  window that opens only once its resolution has arrived loses, to
  that delay, part of the time the Publisher gave it.

  **The offset behaves as the base specification's, default included.**
  A window that declares no offset may be resolved up to 60 seconds
  ahead, exactly as a base event that declares none. The reason is the
  one ADR 0011 applies: a Player implementing this specification and a
  Player implementing the base specification behave the same on the
  same manifest. ADR 0018 records the decision.

  **For an overlay the mechanism carries over unchanged**, because an
  overlay window occupies a region of the primary timeline: the
  earliest resolution time is computed against the start of the window,
  exactly as the base specification computes it against an event's
  presentation time.

  **For a pause it cannot**, and the reason is not an oversight of this
  specification. A pause opportunity window bounds where and not when
  (R31): the trigger is the viewer, so there is no presentation time to
  subtract an offset from. Here the offset is computed against **the
  start of the opportunity window** — the moment the playhead enters
  the region in which a pause would produce an ad — which is a point on
  the timeline the Publisher does author.

  **Resolving early buys latency and spends freshness**, and that trade
  is not the same for every deployment. A resolution obtained when the
  playhead entered a half-hour window is half an hour old if the viewer
  pauses at its end: the targeting is stale and the advertiser's budget
  may be spent. So the resolution says how long it keeps, and the APS
  declares it because the APS is the only actor that knows how long its
  own decision stays good.

  That single mechanism covers the whole range rather than picking a
  point in it: a resolution declared to keep indefinitely is resolved
  once per window, and one declared to keep for no time at all is
  resolved at the moment of the pause. Both are positions a deployment
  may hold, and neither has to reopen this requirement.

  The constructs that carry the offset and how long a resolution keeps
  are named under the rules of
  [`06-naming-and-namespaces.md`](./06-naming-and-namespaces.md).

  **Conformance criteria** (runtime):
  - **R36.1** (Publisher): The Publisher MAY declare, on an overlay or
    pause opportunity window, how far ahead of it a Player may resolve.
    A window that declares nothing may be resolved up to 60 seconds
    ahead, the base specification's default for early resolution. A
    Publisher who wants a window resolved only when it fires declares
    an offset of zero.
  - **R36.2** (Player): On an overlay window, the Player MUST NOT
    resolve earlier than the offset — declared, or the default of
    R36.1 — before the start of the window.
  - **R36.3** (Player): On a pause opportunity window, the Player MUST
    NOT resolve earlier than the offset — declared, or the default of
    R36.1 — before the start of the window. The offset is computed
    against the start of the window and never against the pause, which
    has no authored time (R31).
  - **R36.4** (APS): Where a resolution may have been obtained ahead of
    the opportunity, the APS MUST declare how long that resolution
    remains usable. A resolution document that does not declare it
    remains usable for as long as its opportunity window lasts.
  - **R36.5** (Player): When the opportunity fires, the Player MUST
    check whether the resolution it holds is still usable. If it is
    not, the Player MUST request a new one and MUST NOT present
    candidates from the expired resolution.
  - **R36.6** (Player): When a re-resolution yields no usable
    candidate, the Player MUST treat it as an empty resolution (R30)
    and MUST NOT fall back on the expired one.
  - **R36.7** (spec document): Resolving early is a permission and
    never an obligation. A Player that resolves only when the
    opportunity fires is conformant, whatever offset the window
    carries.

- **R37. A pause is what the viewer experiences, not how the Player achieves it.**
  *Gist: Any mechanism that leaves the primary content suspended and resumes it where it was suspended is a pause; the specification does not prescribe how a Player implements one.*

  A device with a single video decoder cannot hold the paused frame and
  play an ad video at the same time. A Player on such a device may
  therefore leave the primary content — releasing its decoder, or
  tearing down its pipeline — present the ad, and afterwards restore
  the primary content at the position it was suspended at. Whether that
  counts as a pause decides whether a whole class of devices can
  present a video pause ad at all.

  **It counts.** A pause is a property of what the viewer perceives: the
  content stopped where they stopped it and continued from there. A
  Player that leaves the content and reloads it at the same position
  has produced exactly that experience, and this specification
  recognises it as a conformant way to pause.

  The reason for saying so rather than leaving it to implementers is
  that the alternative reading is available and costly. Read as a
  statement about mechanism, "pause" would exclude the devices that
  need the mechanism most, and it would do so silently — a Player would
  simply decline the video form and nobody would know why.

  **Conformance criteria** (runtime):
  - **R37.1** (Player): A Player MAY implement a pause by any mechanism
    that suspends the primary content and later resumes it from the
    position at which it was suspended, including one that releases the
    primary content's decoding resources for the duration of the pause.
  - **R37.2** (Player): On resume, the Player MUST continue the primary
    content from the position at which it was suspended. A mechanism
    that cannot restore that position is not a pause under this
    specification, whatever it is called.
  - **R37.3** (spec document): This specification states no requirement
    about how a Player implements a pause, and a criterion elsewhere
    that appears to assume one mechanism is to be read as this
    requirement defines it.

- **R38. The Player forwards the slot's allowed layouts to the APS.**
  *Gist: When a non-linear slot declares the layouts the Publisher allows, the Player sends that set to the APS on the resolution request, and checks the options it gets back against it before rendering; a slot that declares none admits only its own family's layouts.*

  A Publisher MAY declare, on a non-linear slot, the layouts it allows
  (`@allowedLayouts`, R12.2). When it does, the set travels to the APS,
  so the ads chosen upstream are already among those the Publisher
  allows. The case is **UC-15** in
  [`04-use-cases.md`](04-use-cases.md).

  **Conformance criteria** (runtime):
  - **R38.1** (Publisher): Declaring the allowed layouts on a non-linear
    slot is OPTIONAL. A slot that declares none admits only the layout
    tokens R12 enumerates for its own family: on an overlay slot those
    of the Overlay and Squeezeback entries, on a pause slot those of the
    Pause-ad entry. It admits no token of another family — an overlay slot
    that declares nothing does not admit the `linear` full-screen
    takeover — and it does not admit `custom`, which a slot admits only
    by listing it (R39.2).
  - **R38.2** (Player): When the slot declares allowed layouts, the Player
    MUST send the declared set, unchanged, on the resolution request to
    the APS. When the slot declares none, nothing is sent, and the set
    that binds the APS and the Player is the one R38.1 admits.
  - **R38.3** (spec document): The way the set is carried is normative
    and defined by this specification, as one of the reserved parameters
    of R29 — for example, a query parameter on the resolution request.
  - **R38.4** (APS): The APS MUST NOT return an option whose layout is
    outside the set it received or, when it received none, outside the
    set R38.1 admits for the slot's family.
  - **R38.5** (Player): Before rendering, the Player MUST check that the
    option it selects uses one of the layouts the slot admits — the
    declared set, or the one R38.1 admits when none is declared — and
    MUST NOT render it otherwise (R5.6). Forwarding the set does not
    remove this check.
  - **R38.6** (spec document): Linear slots (`InsertPresentation`,
    `ReplacePresentation`) are outside this requirement.

- **R39. The `custom` overlay layout (optional).**
  *Gist: An optional layout, `custom`, lets the APS place an overlay in a rectangle given in percent of the video viewport, inside a region the Publisher may bound; it is the only layout with no IAB counterpart.*

  `custom` is an **optional mode**: an implementation that does not
  support it is conformant to this specification. It is the one
  declared exception to the IAB mapping of R12 and to R10.2 / R10.3,
  and it applies to the overlay family only. The case is **UC-16** in
  [`04-use-cases.md`](04-use-cases.md).

  **Conformance criteria** (runtime):
  - **R39.1** (spec document): Supporting `custom` is OPTIONAL for every
    actor. The layout carries no IAB ad type; it is the only exception
    to R12.1's mapping, and the only layout for which this
    specification defines a position (an exception to R10.2 and
    R10.3). It applies only to non-linear overlay slots.
  - **R39.2** (Publisher): A Publisher that admits `custom` on a slot
    lists it in `@allowedLayouts`. It MAY also declare a **custom
    region** on the slot: a rectangle — x, y, width, height, in percent
    of the video viewport, origin top-left — within which a `custom`
    overlay must lie. With no region declared, the region is the whole
    viewport.
  - **R39.3** (Player): When the slot declares a custom region, the
    Player MUST send it on the resolution request together with the
    allowed layouts (R38.2), carried the way R38.3 defines.
  - **R39.4** (APS): An option with layout `custom` MUST carry the
    overlay's rectangle in the same units, and that rectangle MUST lie
    entirely inside the region it received. It MAY be smaller than the
    region; it MUST NOT extend beyond it.
  - **R39.5** (Player): Before rendering a `custom` option, the Player
    MUST check that its rectangle lies inside the slot's region (or the
    viewport when no region is declared), and MUST NOT render it
    otherwise; the option is then not renderable and the Player moves
    to the next one (R5.6). A Player that does not support `custom`
    treats every `custom` option as not renderable.

- **R19. Ad playback speed follows primary content.**
  *Gist: Ads play at the primary content's speed, so a 10 s ad at 2x is on screen for 5 s of wall-clock; the cap and beacon schedule still use the presentation timeline.*

  All ad content, linear or non-linear, MUST be rendered at the same
  playback speed as the primary content. A presentation window
  (presentation time + duration) does NOT define the wall-clock time
  the ad stays on screen: the effective on-screen duration is given by
  `duration / playback_speed`, governed by the primary content's
  playback speed at the time the ad is presented. For example, an ad
  with presentation time = 0 and duration = 10s, played while the
  primary content runs at 2x, is shown on screen for 5 seconds of
  wall-clock time. `duration` remains expressed on the presentation
  timeline (the single source of truth per DP-1.2); the wall-clock
  on-screen length is derived from it, never duplicated.

  **Conformance criteria** (runtime):
  - **R19.1** (Player): The Player MUST render every ad form (linear
    or non-linear) at the same playback speed as the primary content
    at the moment the ad is presented.
  - **R19.2** (Player): The Player MUST NOT force an ad to 1x
    playback speed when the primary content is playing at a different
    speed; the ad follows the primary content's speed.
  - **R19.3** (Player): The Player MUST compute an ad form's
    effective on-screen (wall-clock) duration as
    `duration / playback_speed`, not as the raw `duration` value;
    cap enforcement (R4) and beacon scheduling (R13) operate on the
    presentation-timeline `duration`, while wall-clock on-screen
    behaviour follows the derived value.
  - **R19.4** (Player): A form's declared duration is a value on the
    presentation timeline for **every** form, including those with no
    intrinsic media — `image` and `html`. The Player MUST derive the
    wall-clock length of such a form as `duration / playback_speed`,
    exactly as for a media-backed form.

- **R21. Pause-ad forms MAY be fullscreen or a partial overlay.**
  *Gist: A pause-ad may be presented fullscreen or as a partial overlay over the paused frame.*

  A pause-ad form MAY be presented fullscreen, occupying the entire
  screen surface, OR as a partial overlay composited over the paused
  primary frame. Both presentation surfaces are admissible; which one
  applies is a property of the pause-ad form / layout the Player
  selects (R5), not a fixed constraint of this requirement. The two
  surfaces are separate layout placements — `pause-fullscreen` and
  `pause-partial` (R12) — so a Publisher that wants only one of them
  can say so in the slot's `@allowedLayouts`, which is what makes this
  delegation something a Publisher can actually exercise. When the
  pause-ad is fullscreen, because it replaces the whole visual surface
  for the duration of the pause, the Player MAY release all resources
  held by the primary content and by any pre-existing overlay in order
  to present a fullscreen video, image, or web page. When the pause-ad
  is a partial overlay, the paused primary frame remains visible
  underneath it.

  R17 governs pause-ad priority over a coexisting overlay independently
  of the pause-ad's presentation surface: while the viewer is paused
  inside a pause-ad window, the pause-ad is the only ad surface visible
  and any coexisting overlay (R17) is suspended, whether the pause-ad
  is fullscreen or partial. This preserves R22's single-active-form
  bound — at most one non-linear ad form is active at any instant — so a
  partial pause-ad does not introduce simultaneous presentation of two
  forms. R16 governs the pause-ad lifecycle (bound to the pause state);
  the live-content presentation-time freeze is governed by R25; this
  requirement (R21) is about the admissible pause-ad presentation
  surfaces.

  **Conformance criteria** (runtime):
  - **R21.1** (Player): The Player MAY present a pause-ad form
    fullscreen, occupying the entire screen surface, or as a partial
    overlay composited over the paused primary frame. When the pause-ad
    is fullscreen, the Player MAY release the resources held by the
    primary content and by any pre-existing overlay to present a
    fullscreen video, image, or web page. When the pause-ad is a
    partial overlay, the Player MUST keep at most one non-linear ad form
    active during the pause (R22): any coexisting overlay is suspended
    while the pause-ad is shown (R17).

- **R25. Pause-ad presentation-time freeze in live content.**
  *Gist: In live content, pausing inside a pause-ad window freezes the Player's presentation time so the pause-ad stays admissible until the viewer resumes.*

  In live content, when the viewer pauses inside the pause-ad's
  temporal window, the Player's presentation time MUST freeze inside
  that window for as long as the viewer remains paused — even though
  the live edge keeps advancing in wall-clock time. The pause-ad
  window is anchored to the Player's (frozen) presentation time, not
  to the still-advancing live timeline, so the pause-ad stays
  admissible until the viewer resumes. If the Player subsequently
  decides to resume at the live edge of the event, that jump is a
  Player action that occurs AFTER the resume from pause — it is not
  part of the pause-ad window. The guarantee is: once paused, the
  Player's presentation time stays frozen inside the pause-ad window
  regardless of the live content continuing to be produced.

  R16 governs the generic pause-ad lifecycle (admissible only in pause,
  dismissed on resume); this requirement (R25) governs the specific
  presentation-time freeze guarantee in live content.

  **Conformance criteria** (runtime):
  - **R25.1** (Player): In live content, while the viewer is paused
    inside a pause-ad window, the Player MUST keep its presentation
    time frozen inside that window for the full duration of the
    pause, regardless of the live edge advancing in wall-clock time.
    Any decision to resume at the live edge MUST be treated as a
    Player action occurring after the resume from pause, outside the
    pause-ad window.

- **R26. Side-by-side / double-box background element.**
  *Gist: In a side-by-side / double-box layout an optional advertiser background image (never video or HTML) fills the bands the two boxes leave uncovered.*

  In a
  **side-by-side / double-box** layout the shrunk primary content and the
  ad are composed as two on-screen boxes that leave bands uncovered. A
  **background element** MAY fill those bands; when none is present they
  render as black. The background element is a still **image** (a branding
  surface, never a video or web/HTML surface, so it never adds a video
  decoder). It is the **advertiser's creative**, mirroring the IAB
  **"Double Box Video + Background"** model, owned by the advertiser and
  not the Publisher or platform. It is an attribute of the slot / layout
  composition, NOT one of the candidate's alternative presentation
  options (R5).

  Reference: IAB Tech Lab, "Ad Format Guidelines for Digital Video
  and CTV" (public comment, Dec 2025). "Double Box Video + Background",
  pp.12-13.
  https://iabtechlab.com/standards/ctv-ad-portfolio/

  **Conformance criteria** (runtime + document-level):
  - **R26.1** (APS + Publisher): The background element of a side-by-side
    / double-box layout MUST be carried as a composition attribute of the
    slot / layout, not as a separate presentation option (R5).
  - **R26.2** (Player): The Player MUST composite the primary content
    and the ad as the two boxes of a side-by-side / double-box layout.
    When the advertiser supplies a background element, the Player MUST
    place it in the uncovered bands. When the advertiser supplies no
    background element, the uncovered region renders as black.
  - **R26.3** (Player): The number and type of concurrent elements
    determine the device classes that can composite the side-by-side
    layout. The background element is always a still **image**, never a
    video and never a web/HTML surface, so it never consumes a video
    decoder. The primary content consumes one video decoder; the ad
    consumes a second video decoder only when the ad itself is a video,
    otherwise consuming an image / HTML surface. A side-by-side whose ad
    is **video** therefore requires **two** concurrent video decoders (the
    primary content plus the ad video) plus an image surface for the
    background, and MUST NOT be selected on a single-decoder device
    (R3 / R5). A side-by-side whose ad is an **image** or **HTML** surface
    needs **one** decoder (the primary content) plus an image / HTML
    surface for the ad and an image surface for the background, and a
    single-decoder image/HTML-capable device can render it. A non-video
    element (the ad when it is an image / HTML surface, or the image
    background) MUST NOT be selected on a device that cannot composite
    that surface type on top of video (e.g. an image background is not
    satisfiable on a video-only-overlay device such as D2, R3 / R5).

- **R27. L-shape / squeezeback (the "L-box") — a full-frame ad creative
  with the primary content shrunk on top.**
  *Gist: The L-shape / squeezeback has one full-frame ad creative in the background with the shrunk primary content on top; there is no separate third fill element.*

  The L-shape / squeezeback
  is a layout that has **one** ad creative — a single URL the ADS
  supplies, carrying an **image, a video, or a web/HTML** creative — and
  that creative is **always** placed **full-frame in the background**.
  The shrunk primary content is composited **on top of** the full-frame
  creative, in one region of the screen; the "L" is the band of the
  background creative that stays visible around the shrunk primary
  content (commonly the side and / or bottom). The L-shape therefore
  puts **two elements** on screen: the full-frame ad creative in the
  background and the shrunk primary content on top of it. There is **no
  separate third filler element**: the ad creative itself already covers
  the whole frame, so the region around the shrunk primary content is
  the ad creative, not a distinct background fill. This matches the IAB
  squeezeback model, in which the assets are provided in an underlay
  format (a full-frame branded creative with a cutout for the content).

  The L-shape is a **layout / presentation option** offered under R5
  (an ad candidate MAY list it among its ordered presentation options),
  not a slot-composition attribute.

  Reference: IAB Tech Lab — "Ad Format Guidelines for Digital Video
  and CTV" (public comment, Dec 2025). "Squeezeback", p.12.
  https://iabtechlab.com/standards/ctv-ad-portfolio/

  **Conformance criteria** (runtime + document-level):
  - **R27.1** (APS + Publisher): An L-shape / squeezeback presentation
    option MUST carry exactly one ad creative — the full-frame
    background creative — as an image, a video, or a web/HTML surface
    (R15). The shrunk primary content is not a creative the ADS / APS
    supplies; it is the main content the Player shrinks.
  - **R27.2** (Player): The Player MUST composite the two elements of an
    L-shape — the full-frame ad creative in the background and the
    shrunk primary content on top of it — with the ad creative covering
    the whole frame and the shrunk primary content scaled into the region
    its `@layout` token denotes (R12).
  - **R27.3** (Player): The decoder-and-surface budget of an L-shape is
    driven by the media type of the full-frame ad creative. The shrunk
    primary content always consumes **one** video decoder. If the
    full-frame ad creative is a **video**, it consumes a **second** video
    decoder (two videos: the background creative and the shrunk primary
    content), so the L-shape is NOT satisfiable on a single-decoder
    device (R3 / R5). If the full-frame ad creative is an **image or
    HTML**, it consumes an image / HTML surface for the background and the
    L-shape needs only **one** decoder (the shrunk primary content) plus
    that surface; a single-decoder device that can composite that surface
    type underneath / around video can render it. An image / HTML
    full-frame creative MUST NOT be selected on a device that cannot
    composite that surface type together with video (R3 / R5).

### Interaction & composition rules

Requirements that govern how ad forms and opportunity windows compose
and interact when more than one is in play: sequencing several
non-linear forms within a slot, layering a pause-ad over a coexisting
overlay, arbitrating overlapping same-family windows, and bounding the
screen to a single active non-linear form at any instant.

- **R14. Sequential non-linear ad candidates within a slot.**
  *Gist: A non-linear slot may carry several ad candidates, played one after another in declared order, the same way a linear break plays its ads.*

  A non-linear ad slot MAY be filled by more than one ad candidate
  played in **sequence**, exactly as a linear ad break plays its
  candidate ads one after another (R7). When the resolution document
  the APS produces declares several non-linear candidates for one
  slot, the Player presents them **one after another, in the order the
  candidates appear in the resolution document** — the same ordering
  contract R7 imposes on linear candidates. Each candidate contributes
  the one presentation option the Player selected for it under R5, so
  the sequence is a sequence of candidates and the alternatives inside
  a candidate are not part of it. For example, a 30 s overlay slot
  whose resolution document declares Overlay A (10 s), then Overlay B
  (10 s), then Overlay C (10 s) is presented as A, then B, then C, each
  starting when the previous one ends. The cumulative duration of the
  candidates is expected to match the opportunity window the Publisher
  declared for the slot (here, 30 s), and the Player enforces the slot
  cap against that cumulative duration per R4. That the forms play one
  at a time rather than concurrently — and the rationale for it — is
  governed separately by R22.

  This in-slot sequencing rule (candidates played in declared order) is
  distinct from how the Player handles **multiple overlapping
  opportunity windows of the same family in the primary `MPD`**, which
  is governed separately by R20. The two levels are independent: R20
  selects which opportunity window is served; this requirement (R14)
  governs the sequence of candidates inside the selected window's
  resolution document.

  **Conformance criteria**:
  - **R14.1** (Player): When the resolution document for a non-linear
    slot declares more than one ad candidate, the Player MUST present
    the candidates in sequence, in the order they appear in the
    resolution document (the same ordering contract R7 applies to
    linear candidates), each starting when the previous one ends.
  - **R14.2** (Player): The Player MUST enforce the Publisher-declared
    slot cap (R4) against the cumulative duration of the sequence of
    non-linear candidates it presents, trimming or dropping per R4 / R7
    when the cumulative duration would exceed the slot's opportunity
    window.
  - **R14.3** (spec document): The specification MUST NOT introduce a
    construct that implies or requires the parallel (simultaneous)
    rendering of two or more non-linear ad forms. Sequencing of forms
    within a slot is governed by the resolution document's declared
    candidate order (R14.1) and carries no separate "render-then"
    primitive beyond that order. The single-active-form runtime
    constraint itself lives in R22.

- **R17. Pause-ad priority over overlay.**
  *Gist: During a pause, a pause-ad takes priority over any coexisting overlay, which is suspended and then restored on resume.*

  This priority mechanism applies BETWEEN different ad families (a
  pause-ad over an overlay); it is distinct from the single-family
  overlap handling of R20. Suspending the overlay during a pause and
  restoring it on resume is a cross-family layering rule, not an
  in-slot sequencing of two forms within one family (R14). This
  priority holds regardless of the pause-ad's presentation surface
  (R21): whether the pause-ad is fullscreen or a partial overlay, while
  the viewer is paused inside the pause-ad window the pause-ad is the
  only ad surface visible and any active overlay is suspended, so there
  is no simultaneous composition of a pause-ad and an overlay during the
  pause (R22).

  When a pause-ad opportunity and an overlay opportunity are
  active at the same instant, the pause-ad is rendered on top of
  the overlay. The Player layers the two by priority: while the viewer
  is paused inside a pause-ad window, the pause-ad form is the
  only ad surface visible (the overlay is suspended). When the
  viewer resumes primary playback, the pause-ad is dismissed
  (per R16) and the overlay reappears if its slot window is
  still active; the overlay continues until its window expires.
  This priority is not Publisher-configurable — pause-ad above
  overlay during pause is the only admissible composition.

  **Conformance criteria** (runtime):
  - **R17.1** (Player): While the viewer is paused inside a
    pause-ad window AND an overlay is active, the Player
    MUST render the pause-ad form and MUST suspend the overlay
    rendering.
  - **R17.2** (Player): On resume from pause, the Player
    MUST dismiss the pause-ad (per R16) and MUST restore the overlay
    rendering if the overlay slot window is still active.
  - **R17.3** (Player): If the overlay slot window expired
    during the pause, the Player MUST keep the overlay surface clear
    on resume; the overlay is over.
  - **R17.4** (spec document): The specification carries no
    construct that lets the Publisher, the ADS, or the APS invert
    this priority.
  - **R17.5** (Player): When a viewer pause begins inside a pause
    opportunity window while a linear ad occupies the screen, the
    Player MUST present the pause ad and MUST suspend the linear ad,
    and MUST resume it from where it was suspended when the viewer
    resumes. The pause
    ad is dismissed on resume (R16). The cross-family priority of this
    requirement therefore holds against the linear family as well as
    against an overlay.

- **R20. Overlapping same-family opportunity windows: first-window-wins with fallback.**
  *Gist: When same-family opportunity windows overlap, the Player serves the first and treats the rest as fallback, used only if the first fails to resolve.*

  How the Player handles **multiple overlapping opportunity windows of
  the same family in the primary `MPD`** (the families are linear,
  overlays, and pause ads — each family is a category of ad). When two
  or more windows of the same family overlap in time in the primary
  `MPD`, the Player takes the first overlapping window — which R20.3
  identifies — and resolves its resolution document; that one
  resolution document may itself carry a sequence of candidates
  governed by the in-slot rule of R14. The remaining overlapping
  windows are FALLBACK: the Player resorts to them only when it cannot
  obtain the first window's resolution document at all, and R20.1
  enumerates exactly when that is. The two levels are independent:
  this requirement (R20) selects which window is served; R14 governs
  the sequence of candidates inside the selected window's resolution
  document.

  The rationale for resolving overlapping same-family windows as
  first-window-wins-with-fallback — rather than serving them
  concurrently — parallels the device-resource rationale behind the
  single-active-form constraint (R22.1). If two opportunity windows of
  the same family were allowed to be active at the same instant, the
  Player would have to decide which of two simultaneously resolvable ad
  presentations to render, and rendering both would mean two concurrent
  non-linear presentations — the same pressure on the device's decoder
  and resource budget that the one-form-at-a-time rule exists to avoid.
  Concurrency of windows is concurrency of presentation. By selecting
  the first window and treating the rest as fallback, the form we define
  never asks the device to present more than one ad at a time, and it
  never asks the Player to resolve a runtime conflict between two equally
  valid windows. Instead, the overlap is reinterpreted: it is not two
  things to play at once (which would complicate resource selection on
  the device), but a Publisher-declared chain of one primary window plus
  robust backups. When the first window fails to resolve its resolution
  document (the APS is unreachable, the event URL fails), the Player
  falls through to the next overlapping window as a backup. Overlap
  therefore stops being a concurrency case to arbitrate at runtime and
  becomes a simple, declared fallback chain.

  **Conformance criteria** (runtime):
  - **R20.1** (Player): When ad opportunity windows of the same family
    overlap in time within the primary `MPD`, the Player MUST select
    the first overlapping window (R20.3) and attempt to resolve it. An
    attempt **on a window** that does not produce an ad is a **failed
    execution**, and on a failed execution the Player MUST attempt the
    next overlapping window of the same family. This is the base specification's rule,
    stated in ISO/IEC 23009-1:2026 **§5.16.2.2.5** (*Playhead-triggered
    processing*), step 2: *"If execution fails, steps a-c above are
    repeated for next events in QE, until: — Execution succeeds, or —
    PRT of the topmost event in the queue is in the future (i.e.
    PRT > PHP), or — The queue is empty."*

    Each way an attempt can fail maps to a condition **§5.16.2.2.6**
    (*Execution*) lists, and the Player MUST treat all four alike:

    - the APS does not respond, or the request fails at the transport
      level — *"Alternative MPD is unavailable"*;
    - the response carries a final HTTP status other than `200` — the
      same condition: nothing was obtained;
    - the response carries a `200` whose body is not a resolution
      document the Player can parse — *"Alternative MPD is …
      invalid"*;
    - the response carries a well-formed resolution document that
      **carries no candidates** (R30) — *"Alternative MPD is a List
      MPD, and merge process resulted in no available media"*.

    When every overlapping window of the family has been attempted and
    none produced an ad, the Player MUST continue with the primary
    content uninterrupted: *"If no event can be successfully executed,
    the playback continues uninterrupted"* (§5.16.2.2.5). Where the
    Publisher declared no fallback window at all, that is the behaviour
    after the single attempt, which is what it has always been.

    For the **linear family this is adopted unchanged** from the base
    specification. For the **non-linear families the base specification
    does not reach** — its execution model is built on Alternative MPD
    events, and overlay and pause-trigger windows are not those — so
    this specification **extends the same rule to them**, for the
    reason R20.3 gives: one behaviour across every family, so that an
    implementer does not have to learn two.

    **A resolution document that carries candidates is not a failed
    execution**, whatever the Player then does with them. A candidate
    skipped because the device can satisfy none of its presentation
    options is governed by R5.3 and R5.7, which end at the primary
    content and not at the next window. The base specification's
    condition is media availability after the merge, not renderability
    on a device; this specification does not extend it there.
  - **R20.2** (Publisher): All opportunity windows of one family that
    share a `Period` MUST be authored as `<Event>` entries inside a
    **single** `<EventStream>`. DASH admits at most one `EventStream`
    per `Period` for a given scheme — §5.10.2.1: *"all Events of one
    type shall be clustered in one Event Stream"* — so two sibling
    streams carrying the same SGAI scheme in one `Period` is not a
    conformant document.
  - **R20.3** (Player): The Player MUST order overlapping windows of
    one family by **presentation time, oldest first**. Where two
    windows carry the same presentation time, the Player MUST take them
    in the order in which they appear inside the `EventStream`.

    For the linear family this is the base standard's own rule: the
    execution queue is *"a priority queue ... ordered by the
    presentation time PRT"* (§5.16.2.2.2), processed *"from oldest PRT
    to the most recent"* (§5.16.2.2.5). **It is not document order** —
    document order governs when an event is handed to the application
    (§5.10.2.1), which is an earlier and separate step.

    For the non-linear families the base standard does not reach: its
    execution model is built on a scheduled presentation time that
    overlays and pause-ads do not have. **This specification therefore
    extends the same rule to them**, so that one ordering governs
    every family and an implementer does not have to learn two. The
    tie-break by document position is likewise ours: the base
    standard's queue does not resolve equal presentation times, and
    document position is what remains once presentation time has
    stopped separating them.
  - **R20.4** (Player): A resolution document whose family does not
    match the slot that requested it is not a resolution of that slot.
    The Player MUST treat it as a failed execution, MUST NOT present any
    of its candidates in the slot, and MUST continue down the chain of
    R20.1 to the next overlapping window of the slot's family.

    It ends the way a resolution carrying no candidates ends, and for
    the reason ADR 0011 gives for that case: the attempt produced no ad
    for this slot. A document of the wrong family cannot fill the slot
    whatever it contains, because its candidates are of a kind the slot
    does not admit. It is stated separately because it does carry
    candidates, and R20.1 holds that a resolution document carrying
    candidates is not a failed execution; this criterion is the
    exception, since none of those candidates belongs to the slot.
  - **R20.5** (Player): The Player MUST bind the candidates each window
    in a fallback chain serves with **that window's own** declarations:
    its allowed layouts and its maximum duration. The Player MUST NOT
    apply the declarations of the window it stands in for. This follows from
    R20's ownership model — a declaration belongs to the window that
    carries it — and the alternative, binding the chain to the first
    window's declarations, contradicts it.
  - **R20.6** (spec document): R20.5 MUST be carried as a normative
    Player obligation. Stating it only in informative material does not
    bind a Player, and a rule that selects which presentation option
    reaches the screen cannot depend on a reader treating an
    illustration as a requirement. This is a **change of status** for a
    rule the specification already contained: it was answered where it
    could be read and not where it had to be obeyed.

- **R22. Single active non-linear form; no concurrent presentation.**
  *Gist: At most one non-linear ad form is active on screen at any instant; no two non-linear forms are shown simultaneously.*

  Although a slot MAY carry a sequence of non-linear ad candidates
  (R14),
  what this edition does **not** permit is the **simultaneous**
  presentation of two or more non-linear ad forms: at any instant `t`,
  at most ONE non-linear ad form is active on the screen. Sequential
  forms (one ending, the next beginning) are in scope; overlapping two
  forms on screen at the same time is not.

  The rationale for the single-active-form constraint is **device
  resource simplicity**, specifically concurrent video-decoder budget.
  If two non-linear forms were both video overlays and were required to
  be shown at the same instant, the device would need to decode main
  content (1 video decoder) plus overlay A (1 decoder) plus overlay B
  (1 decoder) — three concurrent video decoders. Many target devices
  support only a small number of concurrent decoders (sometimes only
  two). By bounding the slot to one active non-linear form at a time,
  the device never needs more than main content plus one ad form — a
  budget that is always feasible across the device classes in R3.
  Hence the expectation of a single non-linear ad form on screen at a
  time.

  R14 permits the sequence of candidates within a slot; this
  requirement imposes that the sequence is played one form at a time,
  never overlapping.

  Simultaneous presentation of two or more non-linear forms is OUT OF
  SCOPE for this edition; a future edition MAY relax the single-active-
  form constraint and introduce concurrency semantics with explicit
  conflict-resolution and decoder-budget rules.

  **Conformance criteria** (runtime):
  - **R22.1** (Player): At any instant `t`, the Player MUST keep at
    most ONE non-linear ad form active on the screen. The Player MUST
    NOT present two or more non-linear ad forms simultaneously. This
    bound exists so the device never needs more than main content plus
    one ad form's video decoder concurrently (R3).

  **Across families.** R22 bounds non-linear forms only. Whether a
  non-linear form is composited over a linear presentation
  (`InsertPresentation`, `ReplacePresentation`) is governed by R40: by
  default it is not, and it is when the window declares that it is
  composited on top (UC-04). A non-linear ad shown during a replacement
  that is not advertising, such as a blackout, is declared inside the
  replacement's own presentation (UC-14).

- **R40. A non-linear window declares how it relates to the linear events it overlaps.**
  *Gist: A non-linear window is presented only over the content of the presentation that declares it; it neither replaces an inherited linear event nor is composited over an alternative presentation, unless the Publisher declares on the window that it supersedes the linear event it overlaps or that it is composited on top of it.*

  The base specification carries advertising and blackouts through the
  same alternative-presentation events. §5.16.1 describes the tool as
  *"the ability to switch between two independent Media Presentations,
  for applications such as pre-roll and mid-roll advertisement, as well
  as blackouts"*, and neither event scheme gives `EventStream@value` a
  value space that could tell them apart (*"This value is currently not
  required"*, Table 59; *"This value is currently not used"*, Table
  61). Whether an alternative presentation is an ad is therefore not
  observable by a Player (ADR 0012), and no rule here depends on it.
  Whether one is **active** is observable: a Player of this
  specification executes it.

  The Publisher knows what each of its events is. This requirement lets
  it declare, on the non-linear window, the one fact the Player needs,
  in one of three relations:

  - **Default (nothing declared).** The window is presented only over
    the content of the presentation whose `MPD` declares it. It does not
    replace an inherited linear event, and it is not composited over an
    alternative presentation. Two ads on screen at once never come from
    an overlap nobody declared.
  - **Supersede.** The window stands in for the inherited linear events
    whose presentation time falls within its span. A Player of this
    specification presents the window and does not execute those
    events, and executes them after all when the window presents no ad.
    A Player that does not implement this specification ignores the
    window and plays the linear events, so the linear break is the
    legacy fallback of a non-linear offering (UC-07, UC-17).
  - **On top.** The window is presented also while an alternative
    presentation that starts within its span is active, composited over
    it: a hybrid break (UC-04).

  **The content of an alternative presentation is a presentation of its
  own.** The primary content cannot know what a replacement contains, so
  a non-linear ad shown during it is declared by a window in the
  replacement's own `MPD`, over the replacement's content. The base
  specification already runs the alternative presentation as a second
  instance of the same client: *"there are two instances of DASH access
  engine, main and the alternative, both working as described above"*
  (§4.2). A blackout is the case (UC-14).

  **Conformance criteria** (runtime + document-level):
  - **R40.1** (Publisher): Declaring a relation on a non-linear window
    is OPTIONAL. A window declares at most one relation, supersede or
    on top; a window that declares neither has the default relation.
  - **R40.2** (Publisher): A Publisher that wants a non-linear ad
    presented during an alternative presentation MUST declare it either
    by a window in that alternative presentation's own `MPD`, or by a
    window of the triggering presentation that declares on top.
  - **R40.3** (Player): When a window declares supersede, the Player
    MUST present the window and MUST NOT execute the inherited linear
    events whose presentation time falls within its span. When the
    window presents no ad — every attempt to resolve it is a failed
    execution under R20.1, or the device can render none of its
    candidates (R5) — the Player MUST execute those events as the base
    specification defines, including its rules for an execution that
    starts after an event's presentation time.
  - **R40.4** (Player): When a window declares no relation, the Player
    MUST present its forms only while the content of the presentation
    whose `MPD` declares the window is being output, and MUST execute
    every inherited linear event it overlaps with its base semantics. A
    form on screen when an alternative presentation begins ends there,
    and the window presents nothing further.
  - **R40.5** (Player): When a window declares on top, the Player MUST
    present it also while an alternative presentation that starts
    within its span is active, composited over that presentation,
    within the device's capability (R3, R5) and R22. The inherited
    linear event executes with its base semantics.
  - **R40.6** (Player): The Player MUST process the non-linear windows
    declared in an alternative presentation's `MPD` as that
    presentation's own: they are presented over its content, and
    R40.3–R40.5 apply to them against the alternative presentations it
    triggers in turn.
  - **R40.7** (spec document): The relation is declared on the
    non-linear window this specification defines. The specification
    MUST NOT add anything to the inherited linear events to carry it:
    the same base event means the same thing to every Player. How the
    declaration is carried is decided under the conventions of
    [`06-naming-and-namespaces.md`](06-naming-and-namespaces.md).
  - **R40.8** (spec document): R40.3 is a recorded exception to R1.5:
    a Player of this specification does not execute a base event that
    the base specification would execute. The reason is that the
    departure is declared explicitly by the Publisher, who authored
    both the event and the window, on a construct this specification
    defines; and that a Player that does not implement this
    specification, which does not recognise the window, executes the
    base event exactly as the base specification defines. ADR 0020
    records the decision.

### Tracking

Requirements governing what is reported back and through which carrier
— the tracking-beacon scheme, ADS-directed beacon schedules, and the
carriers for creative metadata and non-AV assets.

- **R6. Ad tracking beacon carrier.**
  *Gist: In-band tracking beacons ride the existing DASH callback event scheme rather than a newly invented carrier.*

  The specification MUST specify how in-band
  ad tracking beacons (impression, start, quartiles, complete, etc.)
  are carried in the resolution document. Implementations SHOULD
  reuse the existing DASH callback event scheme
  (`urn:mpeg:dash:event:callback:2015`, §4.7 / §5.10.4.5) as the
  carrier — embedding tracking `<Event>` entries inside an
  `<EventStream>` of that scheme in the ad MPD or sub-MPD. New
  tracking carriers MAY be introduced only when the callback scheme
  cannot express the required semantics, and only after a
  documented gap analysis per R9. Players MUST safely ignore unknown
  namespaces on tracking-related extension elements per the DASH
  extension rules invoked by R1.

  Application-level creative metadata that has no native DASH carrier
  is governed separately by R23, and the carrier for non-AV creative
  assets is governed separately by R24; both are distinct from this
  requirement (R6 covers tracking beacons, not creative metadata or
  asset URLs). The timeline-scheduled ad beacons reuse this callback
  carrier.

  **Conformance criteria** (runtime + document-level):
  - **R6.1** (spec document): The specification MUST specify how in-band ad
    tracking beacons are carried in the resolution document.
  - **R6.2** (APS): Implementations SHOULD carry tracking beacons
    as `<Event>` entries inside an `<EventStream>` of scheme
    `urn:mpeg:dash:event:callback:2015` in the ad `MPD` or sub-`MPD`.
    The APS produces these entries by translating the tracking events
    the ADS declared in its decision document.
  - **R6.3** (spec document): A new tracking carrier MAY be
    introduced only when the callback scheme cannot express the
    required semantics, and only after a documented gap analysis
    per R9.
  - **R6.4** (Player): A Player MUST safely ignore unknown
    namespaces on tracking-related extension elements, per the DASH
    extension rules invoked by R1.
  - **R6.5** (Player + APS): The de-duplication key for in-band
    beacons is scoped to **the candidate** that carries them. Within a
    candidate, beacons sharing an `@id`, or the same URL at the same
    presentation time, fire once. Two beacons carrying the same `@id`
    in two different candidates of one resolution document are two
    distinct beacons and the Player MUST fire both. On a `ListMPD` the
    base scope applies unchanged (R1.5): `Event@id` is scoped to its
    `@schemeIdUri` / `@value` pair over the whole media presentation
    (DASH Table 44), so the ads of one `ListMPD`, streams merged from
    their sub-MPDs included, share one scope. The per-candidate scope
    above governs the candidates of a non-linear resolution document.
  - **R6.6** (Player): When the beacon carrier is an `<EventStream>`
    hosted as foreign-namespace open content inside a candidate, the
    Player MUST resolve its presentation times against **that
    candidate's own presentation**, not against a `<Period>` the
    element does not sit in.
  - **R6.7** (spec document): The specification MUST state how a
    resolution document carrying the candidate-level beacon carrier is
    validated. A validation procedure that reports such a document
    valid while skipping the foreign-namespace subtree has not checked
    the tracking carrier at all, which is the outcome a reader is most
    likely to arrive at by default.

- **R13. Non-linear ad tracking — ADS-directed callbacks.**
  *Gist: The ADS owns the beacon schedule (which beacons, at which relative times); the Player just executes what the resolution document carries.*

  The specification MUST define a tracking mechanism that allows
  the ADS to instruct the Player on which tracking beacons to
  fire, and at which points relative to the ad's presentation. The
  ADS declares the schedule in its decision document; the APS
  expresses it in the resolution document using DASH callback events (or an equivalent
  baseline DASH construct); no new tracking event scheme is
  introduced. Beacon timings are **relative to the ad's
  presentation time**, and the **ADS is the authority** over the
  tracking schedule — the spec does NOT prescribe specific
  fractions (no hardcoded quartiles), granularity, or beacon
  count. The Player executes the schedule it reads from the
  resolution document.

  **Conformance criteria**:
  - **R13.1** (APS): When the resolution document carries tracking
    instructions, the APS MUST express them using DASH callback
    events (or an equivalent baseline DASH construct), with timings
    relative to the ad's presentation timeline. Conformance is
    checked against the resolution document alone: it fixes the form
    the instructions take and the timebase they use, and it does not
    reveal how many beacons the ADS declared.
  - **R13.2** (Player): Given an ad accepted for rendering, the
    Player MUST execute the tracking schedule it reads from the
    resolution document — firing each beacon at its specified
    relative time, preserving the ADS's authority over the
    schedule.
  - **R13.3** (Player): If R4 trims the ad before a scheduled
    beacon's time, the Player MUST stop firing remaining beacons
    at the trim boundary.
  - **R13.4** (spec document): The specification MUST NOT introduce
    a new tracking event scheme; reuse of the DASH baseline
    callback mechanism is mandatory.
  - **R13.5** (APS + ADS): The fidelity of the transcription — that
    the APS neither adds, removes, nor reorders the beacons the ADS
    declared — is part of the APS-to-ADS contract those parties
    maintain directly, outside this specification (R18). The ADS
    declares the schedule and receives the beacons, so it is in a
    position to enforce that fidelity; the resolution document is
    not, because it does not show what was declared.

- **R23. Application-level ad metadata carrier.**
  *Gist: The specification defines an SVTA-namespaced place for creative metadata with no native DASH carrier; emitting it and reading it are both optional.*

  Generic application-level metadata that has no native DASH carrier
  (e.g. `AdSystem`, `AdTitle`, etc.) has a defined place to ride:
  extension elements in the SVTA Ads WG namespace. This carrier is
  **optional and non-interoperable by design** — nothing obliges an APS
  to emit it or a Player to read it, and a legacy Player discards the
  extension elements as an unknown namespace per the DASH extension
  rules invoked by R1, so nothing in the ad presentation breaks either
  way. That is what makes this a requirement on the specification
  rather than on an implementation: what can be checked is that the
  place exists and is named, not that anyone used it. This requirement
  governs generic creative metadata, distinct from the tracking beacon
  carrier of R6 (both are "carriers", but R6 carries tracking beacons
  while R23 carries creative metadata).

  **Conformance criteria** (document-level):
  - **R23.1** (spec document): The specification MUST define, in the
    SVTA Ads WG namespace, the extension elements that carry generic
    application-level metadata with no native DASH carrier
    (`AdSystem`, `AdTitle`, etc.), and MUST state that emitting them
    and reading them are both optional.

- **R24. Non-AV creative asset carrier (RFC 4337 avoidance).**
  *Gist: URLs for non-AV creatives (image, HTML) must use a DASH-conformant carrier, never an @mimeType path bound by RFC 4337.*

  When a
  non-AV ad form (`mediaType ∈ {html, image, ...}`) is carried in the
  resolution document, the asset URL MUST NOT be expressed as
  `@mimeType` on an AdaptationSet or Representation reached through any
  path bound by RFC 4337. It MUST be carried via one of the DASH-
  conformant carriers enumerated by DR-6. This requirement governs the
  carrier for non-AV creative assets, distinct from the tracking beacon
  carrier of R6.

  **Conformance criteria** (runtime + document-level):
  - **R24.1** (APS / spec document): When a non-AV ad
    form (`mediaType ∈ {html, image, ...}`) is carried in the
    resolution document, the asset URL MUST NOT be expressed as
    `@mimeType` on an AdaptationSet or Representation reached through
    any path bound by RFC 4337 (DR-1, DR-5 in
    [`08-dash-extension-rules.md`](./08-dash-extension-rules.md)).
    It MUST be carried via one of the §5.2.1 / §5.10 / §5.8.4.x
    carriers enumerated by DR-6, per R1.2.

- **R33. Pause-ad delivery is measured with the base specification's play-list metric.**
  *Gist: The paused interval is derived from the `PlayList` metric DASH already defines; this specification adds no metric of its own, and measures filled duration rather than opportunity count.*

  A pause slot has no authored duration (R31), so what is worth
  measuring is how much of the paused interval carried an ad, not how
  many pause opportunities occurred. **The number of opportunities is
  set by the viewer**, who decides when and how often to pause: it can
  be neither controlled nor incentivised, and a figure that moves for
  reasons no party influences reports nothing about how well the slot
  was served. **The filled fraction can be influenced**, by the APS
  returning candidates that keep the slot filled for longer.

  The measurement is already defined by the base specification and is
  adopted unchanged. Annex D.4.6 defines the `PlayList` metric as *"a
  list of playback periods"*, where a playback period is *"the time
  interval between a user action and whichever occurs soonest of the
  next user action, the end of playback or a failure that stops
  playback"*. Two of its fields carry everything a pause slot needs:

  - Each playback-period entry declares a `starttype`, whose value
    space includes **`Resume` — "Resume from pause"**. The entry whose
    `starttype` is `Resume` is the one that ends a pause.
  - Inside a playback period, each continuously rendered stretch
    declares a `stopreason`, whose value space includes
    **`UserRequest`** and **`Rebuffering`**. That is what separates a
    viewer pause from a stall: a period that stopped on `Rebuffering`
    is not a pause opportunity, and R31's window never triggered.

  **The paused interval is therefore derived, not measured
  separately**: it is the interval between the end of a playback
  period whose last rendered stretch stopped on `UserRequest`, and the
  `start` of the next entry whose `starttype` is `Resume`. Against
  that interval, the duration the pause ad actually occupied is the
  filled fraction.

  **How the measurement reaches anyone is out of scope**, and the base
  specification takes the same position about its own metrics: *"This
  document does not define mechanisms for reporting metrics; however,
  it does define a set of metrics and a mechanism that may be used by
  the service provider to trigger metric collection and reporting at
  the clients, if a reporting mechanism is available"* (§5.9.1). This
  specification defines the quantity and inherits that silence about
  transport.

  **Conformance criteria** (runtime + document-level):
  - **R33.1** (spec document): This specification MUST NOT define a
    metric of its own for pause-ad delivery. The quantity is derived
    from the `PlayList` metric of Annex D.4.6; defining a parallel
    metric for something the base specification already measures is
    the duplication R9 exists to prevent.
  - **R33.2** (Player): A Player that reports metrics MUST derive the
    paused interval from the `PlayList` entries as described above,
    and MUST NOT count a playback period that stopped on
    `Rebuffering` as a pause opportunity.
  - **R33.3** (spec document): The transport by which any measurement
    reaches the Publisher, the APS or the ADS is out of scope, as it
    is for the base specification's own metrics (§5.9.1).
  - **R33.4** (Publisher): Content carrying pause opportunity windows
    MUST request the `PlayList` metric through the base
    specification's `Metrics` element. Collection is triggered by the
    service provider and not by the Player — *"The trigger mechanism
    is based on the `Metrics` element in the MPD"* (§5.9.1) — so
    without this declaration R33.2 defines how to derive a quantity
    that nothing obliges anyone to collect.

- **R28. ClickThrough carrier — normative and interoperable.**
  *Gist: The resolution document carries the ClickThrough URL and its click-tracking URLs in an explicit, normative, interoperable carrier.*

  The
  resolution document MUST carry the ad's ClickThrough URL and its
  associated click-tracking URL(s) in a normative carrier that the
  specification defines explicitly, so that every Player conformant to
  this specification reads them the same way.

  The guarantee is scoped to Players that implement this
  specification, and it can only be scoped that way. DASH does not
  specify Player behaviour normatively — §8.1 states that "profiles
  merely specify restrictions on MPD and Segments rather than DASH
  Client behaviour" — and §5.2.1 contemplates a client removing every
  element outside the Annex B schema and still presenting a conforming
  Media Presentation. An obligation on a Player that does not
  implement this specification is therefore not available to be made,
  here or in any other extension of DASH.

  **Conformance criteria** (runtime + document-level):
  - **R28.1** (APS): When an ad candidate in the resolution document
    carries a ClickThrough, the ClickThrough URL and any click-tracking
    URL(s) accompanying it MUST be carried in the normative carrier this
    specification defines, and not elsewhere. Whether a ClickThrough has
    any associated click-tracking URL is the advertiser's decision and
    is not constrained here. Conformance is checked against the
    resolution document alone: a ClickThrough or a click-tracking URL
    carried outside the normative carrier is a violation the document
    shows.
  - **R28.2** (Player): a Player conformant to this specification MUST
    read the ClickThrough URL and fire its associated click-tracking
    when the viewer activates the ClickThrough.
  - **R28.3** (APS + ADS): Whether a ClickThrough the ADS declared
    reaches the resolution document at all is part of the APS-to-ADS
    contract those parties maintain directly, outside this
    specification (R18). The ADS declares the ClickThrough and receives
    the click-tracking, so it is in a position to enforce that it
    travels; the resolution document is not, because it does not show
    what was declared.

### Governance

Requirements that constrain how the proposal itself is authored —
justifying every addition or omission, minimising net new constructs,
and deferring layout to existing primitives.

- **R8. Justify any addition or omission.**
  *Gist: Every new construct, and every deliberate choice not to reuse an existing one, is justified inline in the document.*

  Whenever the proposal
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

- **R9. Minimise net new constructs.**
  *Gist: Reuse existing MPEG-DASH machinery wherever possible; add a new construct only when nothing existing can be made to fit.*

  The proposal must reuse
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

- **R10. Do not recreate a layout system.**
  *Gist: Spatial layout of overlays is delegated to HTML5 / CSS; the spec does not build a parallel layout engine.*

  The solution must defer
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
    (left, right, top, bottom, etc.) are out of scope for the spec.
    Where an ad sits inside its layout follows from the IAB CTV ad
    type that the `@layout` token names (R12.2, R12.4) and is
    rendered with HTML5 / CSS primitives (R10.1). This specification
    declares no positioning vocabulary of its own, which is what
    R10.2 forbids. The one exception is the optional `custom` overlay
    layout (R39), whose rectangle is a position by definition.

## Out of Scope

- **OOS-1. Building a new layout engine.** Spatial arrangement of
  overlays is delegated to HTML5 and CSS, aligned with the IAB CTV
  Ad Standard. The specification MUST NOT define a parallel layout
  standard.
- **OOS-2. Defining the ADS's internal decisioning logic.** The
  proposal only specifies the contract between the MPD event, the
  Player's resolution request, and the resolution document the APS
  returns. Targeting, frequency capping, brand safety filtering and
  similar ADS concerns — and the APS-to-ADS exchange that conveys
  them — remain implementation-specific.
- **OOS-3. Specific position semantics inside a layout** (left,
  right, top, bottom). They follow from the IAB CTV ad type that the
  `@layout` token names (R12.2, R12.4), and are rendered with
  HTML5 / CSS primitives.
- **OOS-4. Creative carrier formats outside R15.** Carriers other
  than the admissible set defined in R15 — for example raw
  JavaScript (`application/javascript`), SVG-as-payload, PDF,
  proprietary binary creatives — are out of scope for this edition.
  Senders that need scripted creatives MUST wrap the script inside
  an HTML document and use `text/html` per R15.
- **OOS-5. Interactive ad frameworks.** An ad built on an interactive
  framework such as SIMID is delivered by that framework, not by this
  specification: SIMID is not among the ad types R12 enumerates, and
  this edition defines no non-linear form that carries a SIMID
  payload.
- **OOS-6. Single-decoder slice or tile replacement.** Replacing a
  slice or a tile so that one decoder carries both the primary content
  and the ad is out of scope for this edition. The technique exists —
  it is most practical in HEVC and AV1 — and a future edition may
  cover it; this edition's decoder-budget reasoning (R3, R22) assumes
  one decoder per concurrent form.

- **OOS-7. Preventing a viewer from seeking past a non-linear
  opportunity window.** The base specification provides `@noJump`,
  which forbids the playhead moving from a point before an event's
  presentation time to a point past the end of its active period
  without executing the event (§5.16.5). On an **inherited linear
  break the mechanism is preserved unchanged**: the ad occupies the
  timeline, so forbidding the jump forbids skipping the ad, which is
  what it exists for.

  On the **non-linear families this specification defines it is out of
  scope**, and the reason is what the window actually spans. A
  non-linear ad is presented over the primary content, which keeps
  playing underneath it, so the region the window covers is programme.
  Forbidding the jump there would not oblige the viewer to watch the
  ad — it would oblige them to watch a stretch of the programme they
  chose to skip. The mechanism would be doing something other than
  what it was built to do.

  This is an **exception and not an omission**, and the difference is
  the point of writing it down: `@noJump` exists, it is understood,
  and it is excluded on one family for a stated reason. A construct
  absent from a specification says nothing about whether anyone
  considered it.

- **OOS-8. Linking the two portions of a hybrid break.** In a hybrid
  break a linear ad takes the screen and an overlay is composited on
  top of it, and the two are selected independently. This
  specification provides no way for the Publisher to declare a
  constraint between them — *"if the linear ad is from advertiser X,
  suppress the overlay"* — and a Player is never asked to enforce one.

  The need is real and commercial: an advertiser who bought the full
  screen does not want a competitor's overlay on top of it. It is
  excluded because enforcing it in the Player would require the
  advertiser's identity to reach the Player, putting commercial data
  into a contract that is about what may be rendered; and because
  competitive separation is already the ADS's, by name, in R2.
  Declaring it here would create a second authority over one outcome.

  Exclusivity between portions is obtained from the ADS, which knows
  about advertisers and competitors and already carries the
  responsibility. ADR 0016 records the decision, including why the
  APS is not the answer either.

- **OOS-9. Ads outside the video surface.** This specification covers
  only ads the video Player renders on the playing or paused video,
  because the contract it defines is between a manifest and the Player
  that plays it. An ad the application renders in its own interface is
  outside that contract and outside this specification, whatever IAB
  calls it: menu ads (IAB *Menu Ad*: home screen, content menu, guide /
  EPG), home-screen and launcher ads, screen saver ads (IAB *Screen
  Saver Ad*), and companion or multi-screen ads (IAB *Companion Ad*).
  In-scene ads are excluded for the same reason from the other side:
  a product or sign placed inside the scene itself (virtual product
  placement) is part of the video frames, not something the Player
  renders over them. They are not candidates for a later phase and are not raised as gaps
  in the specification: no requirement, use case or layout value
  covers them, and none is to be added.

## Deliberately open

A question this specification has decided **not** to answer yet is
recorded here, against the unit it concerns. An entry says the silence
was chosen; the absence of an entry says nothing was chosen, and those
are the two states a reader must be able to tell apart. A construct
absent from a specification says nothing about whether anyone
considered it — which is why an OOS item above states its exclusion,
and why an open question states its openness instead of being left to
look like an oversight.

The difference from Out of Scope is what happens next. An OOS item is
closed: the specification will not address it. An entry here is open:
the specification will address it, and has not yet.

| Unit | Why it is open | Recorded in |
|------|----------------|-------------|

The table is empty, and that is a statement: **no silence in this
specification has been declared deliberate yet.** Adding a row is a
decision about one question, taken by the owner of the specification,
and the row carries where that decision is written down — an ADR under
`.project/decisions/`, or the working-group record that took it.

The remainder of the proposal — Anatomy of the Overlay Resolution
Document, Ad Tracking, Client Execution Flow, Example
Implementation — should be read against these requirements.
Where a design choice satisfies several Rs in tension, the trade-off
is made explicit in the corresponding section.

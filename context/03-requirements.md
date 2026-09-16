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
| R1 | SGAI extends MPEG-DASH 6th edition without breaking it; a legacy Player ignores the new constructs and keeps playing. |
| R2 | Four actors, fixed roles: the Publisher declares, the ADS decides, the APS converts, the Player validates and renders. |
| R4 | The Publisher declares the maximum slot duration; the Player enforces the cap, even mid-ad. |
| R5 | Candidates carry one or more renderable options in preference order; the Player renders the first its device can satisfy, and a single-option candidate leaves the choice with the APS. |
| R11 | No dependency on VAST or any specific VAST version. |
| R12 | A fixed, closed set of IAB ad types (linear, overlay, squeezeback, pause-ad); nothing else is in scope. |
| R18 | The Player-visible interface is specified, including what the Player sends on the resolution request; the APS-to-ADS and ADS-side APIs are out of scope. |
| R22 | At most one non-linear ad form is active on screen at any instant. |

### Contract foundations

Requirements that fix what the proposal extends and the contract it
must respect — the MPEG-DASH baseline, the actor responsibilities,
and the boundaries of what this spec does and does not define.

- **R1. MPEG-DASH 6th edition compliance and graceful degradation.**
  *Gist: SGAI extends MPEG-DASH 6th edition without breaking it; a Player that does not implement the new constructs ignores them and keeps playing the primary content.*

  The solution MUST extend MPEG-DASH 6th edition without breaking
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

- **R2. Honour the actor's responsibilities.**
  *Gist: Four actors with fixed roles: the Publisher declares constraints, the ADS decides which ads to serve, the APS converts that into the resolution document, and the Player validates and renders.*

  The design must
  enforce the separation defined in the Actors and Responsibilities
  section: the Publisher declares constraints, the ADS decides which
  ads to serve (output as VAST), the APS converts that VAST into the
  resolution document the Player reads, and the Player validates and
  renders. New mechanisms must be expressible within this contract.

  **Conformance criteria** (runtime + document-level):
  - **R2.1** (Publisher): Constraints applicable to an ad slot
    (max duration, opt-in policies, layout templates) MUST be
    declared by the Publisher in the `MPD`, not inferred at
    runtime by the ADS, the APS, or the Player.
  - **R2.2** (ADS + APS): The ADS MUST decide which ads to serve and
    output them as its decision document (typically VAST); the APS
    MUST convert that output into the resolution document carrying
    the ad candidates. Neither MUST be expected to enforce
    Publisher-declared constraints (e.g. slot duration cap).
  - **R2.3** (Player): The Player MUST validate the candidates in
    the resolution document against Publisher-declared constraints
    and render only those that satisfy them.
  - **R2.4** (spec document): Every new mechanism introduced by the
    specification MUST be expressible within the four-actor contract; any
    mechanism that would require an actor to take on a
    responsibility outside its role MUST be rejected or redesigned.

- **R11. No dependency on VAST.**
  *Gist: The spec never depends on VAST or any specific VAST version; VAST references are illustrative only.*

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
  - **R11.3** (spec document): Any reference to VAST in the spec
    MUST be in an annex or in a non-normative note explicitly
    flagged as illustrative.

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
  *Gist: The Player MAY attach reserved capability parameters — inputs about the device, not conclusions about what can be served — to the resolution request it sends the APS; each is optional, and one the Player cannot or will not populate is omitted rather than sent empty.*

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

### Opportunity declaration

Requirements that define what the Publisher and the IAB declare about
an ad opportunity before any ad is selected — the slot cap, the
admissible ad-type vocabulary, and the admissible creative carriers.

- **R4. Publisher-declared max slot duration, Player-enforced.**
  *Gist: The Publisher declares a maximum slot duration and the Player enforces it, cutting mid-ad if the candidates would overflow; the ADS is not responsible for the cap.*

  The Publisher declares a maximum duration for each ad slot. The
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
  Publisher as an opt-in policy on the slot. R4 is a concrete
  instance of R2 — Publisher declares the constraint, Player
  enforces it, ADS does not.

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
  cumulative duration (R4.2, R14.2).

  **Conformance criteria** (runtime):
  - **R4.1** (Publisher): The Publisher MUST declare a maximum
    duration on every ad slot (linear or non-linear) defined in the
    `MPD`.
  - **R4.2** (Player): When the cumulative duration of accepted ad
    candidates would exceed the Publisher-declared cap, the
    Player MUST stop rendering at the cap boundary, even if the
    stop falls mid-ad.
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
    scheduled end of the slot and a late start shortens it. On an
    insertion slot the cap bounds the presentation's own duration.
  - **R4.7** (Publisher + Player): A declared cap of zero means the
    opportunity does not fire. The base specification states it
    directly — *"If the value of `@maxDuration` is zero, the event is
    not executed"* (§5.16.5) — and this specification adds nothing to
    it: a zero cap is not a very short slot.
  - **R4.8** (spec document): R4.1's requirement that every slot
    declare a cap is a **deliberate narrowing** of the base
    specification, which treats an absent `@maxDuration` as infinity,
    *"in which case the current presentation resumes only when the
    alternative presentation terminates"* (§5.16.5). The narrowing
    restricts which documents conform and changes no construct's
    semantics, which is what a profile does (§8.1). It is recorded
    here so that a reader who finds the unbounded default in the base
    specification knows it was excluded on purpose.

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
    named visual placements are corner / bug (IAB *Corner Overlay*) and
    lower-third (IAB *Lower-Third Overlay*); a plain image or HTML
    overlay with no named placement is the base `overlay` type.
  - **Squeezeback** (IAB *Squeezeback*, `squeezeback`): a non-linear
    layout in which the primary content is shrunk to share the frame
    with the ad. Supported placements are L-shape / squeezeback (IAB
    *L-Shape*; see R27) and side-by-side / double-box (IAB *Double Box
    Video* and *Double Box Video + Background*; see R26).
  - **Pause-ad** (IAB *Pause Ad*, `pause`): a non-linear surface shown
    over the paused primary frame, fullscreen or partial (see R21).

  **Out of scope: ads outside the video surface.** Any ad rendered in
  the Player chrome or the application UI rather than on the playing or
  paused video is out of scope for this specification. This includes
  menu ads (IAB *Menu Ad*: home screen, content menu, guide / EPG),
  home-screen / launcher ads, screensaver ads (IAB *Screensaver Ad*),
  and companion / multi-screen ads (IAB *Companion Ad*). These are
  concerns of the application's ad integration, not of the
  Player-facing SGAI contract this specification defines. Because the
  supported set above is closed, anything not enumerated there is
  already out of scope; this paragraph makes the off-video-surface
  category unambiguous.

  Reference (live link, not snapshotted):
  https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e

  **Conformance criteria**:
  - **R12.1** (spec document): The accepted ad-type and visual-placement
    values are exactly those enumerated in this requirement, each mapped
    to its IAB definition. The spec MUST NOT accept a value outside the
    enumeration, and MUST cite the IAB source for the values it accepts.
  - **R12.2** (Publisher): Publishers declaring allowed layouts MUST use
    names drawn from the enumerated set, each of which maps 1:1 to an
    IAB-defined ad type or visual placement. Publisher-private layout
    names, and IAB values outside the enumerated set, MUST NOT appear in
    the allowed-layouts declaration on the slot.
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
  - **R5.4** (ADS + APS): Neither the ADS nor the APS MUST be
    required to maintain a device-class matrix or a per-Player
    capability view to produce candidates.
  - **R5.5** (APS): An ad candidate MAY carry multiple presentation
    options, each pairing a form with an admissible layout. The
    options form a single ordered list, and their document order is
    the preference order the Player follows.
  - **R5.6** (Player): The Player MUST resolve presentation-option
    selection by walking the options in document order and, for each,
    checking it against (a) device capabilities and (b) the
    Publisher-declared allowed layouts on the slot. The Player renders
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

- **R30. An empty resolution is distinguishable from a failed one.**
  *Gist: A resolution that legitimately returned no ads is expressed as a resolution document carrying no candidates, not as an error.*

  When the APS resolves an opportunity and the ad decision carries no
  ads, it returns a resolution document that carries no candidates. The
  Player's behaviour is unchanged — it continues with the primary
  content, as it does whenever the candidates are exhausted (R5.3). The
  distinction is not a difference in playback; it is what lets an
  unfilled opportunity be reported as an unfilled opportunity rather
  than as a failure to resolve.

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
  wrong"*. R30 names the case from the APS side; it does not change
  playback.

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

- **R21. Pause-ad forms MAY be fullscreen or a partial overlay.**
  *Gist: A pause-ad may be presented fullscreen or as a partial overlay over the paused frame.*

  A pause-ad form MAY be presented fullscreen, occupying the entire
  screen surface, OR as a partial overlay composited over the paused
  primary frame. Both presentation surfaces are admissible; which one
  applies is a property of the pause-ad form / layout the Player
  selects (R5), not a fixed constraint of this requirement. When the
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
    the whole frame and the shrunk primary content occupying its
    declared region.
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
    renders the pause-ad form and suspends the overlay
    rendering.
  - **R17.2** (Player): On resume from pause, the Player
    dismisses the pause-ad (per R16) and restores the overlay
    rendering if the overlay slot window is still active.
  - **R17.3** (Player): If the overlay slot window expired
    during the pause, the Player keeps the overlay surface clear
    on resume; the overlay is over.
  - **R17.4** (spec document): The specification carries no
    construct that lets the Publisher, the ADS, or the APS invert
    this priority.

- **R20. Overlapping same-family opportunity windows: first-window-wins with fallback.**
  *Gist: When same-family opportunity windows overlap, the Player serves the first and treats the rest as fallback, used only if the first fails to resolve.*

  How the Player handles **multiple overlapping opportunity windows of
  the same family in the primary `MPD`** (the families are linear,
  overlays, and pause ads — each family is a category of ad). When two
  or more windows of the same family overlap in time in the primary
  `MPD`, the Player takes the FIRST overlapping window it encounters and
  resolves its resolution document; that one resolution document may
  itself carry a sequence of candidates governed by the in-slot rule
  of R14. The remaining overlapping windows (the second and any
  subsequent ones) are FALLBACK: the Player resorts to them only when it cannot access
  the resolution document of the first window — for example the APS does
  not respond, or the event URL that resolves to the APS fails. The two
  levels are independent: this requirement (R20) selects which window is
  served; R14 governs the sequence of candidates inside the selected
  window's
  resolution document.

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
    the first overlapping window it encounters and attempt to resolve
    its resolution document. The remaining overlapping windows of the
    same family are fallback only: the Player MUST resort to a
    subsequent overlapping window ONLY when it cannot access the
    resolution document of the first window: the APS does not respond,
    the request fails at the transport level, the response carries a
    final HTTP status other than `200`, or the response carries a
    `200` whose body is not a resolution document the Player can parse.
    When the first window's resolution document is accessible, the
    Player MUST NOT fall through to the others. A `200` carrying a
    resolution document with no candidates per R30 **is** accessible —
    the opportunity resolved, and it resolved to no ads. A `200`
    carrying a body that does not parse is **not**: nothing was
    obtained to resolve the opportunity with, which is the same
    outcome as no response at all.
  - **R20.2** (Publisher): All opportunity windows of one family that
    share a `Period` MUST be authored as `<Event>` entries inside a
    **single** `<EventStream>`. DASH §5.10.2.1 admits at most one
    `EventStream` per `Period` for a given (`@schemeIdUri`, `@value`)
    pair — "all Events of one type shall be clustered in one Event
    Stream" — so two sibling streams carrying the same SGAI scheme in
    one `Period` is not a conformant document. Clustering is also what
    gives R20.1's "first overlapping window it encounters" a defined
    referent: §5.10.2.1 dispatches active events "in the order they
    appear in the EventStream element", so the primary window and its
    fallbacks are read off document order inside that one stream.

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
    the ADS declared in its VAST.
  - **R6.3** (spec document): A new tracking carrier MAY be
    introduced only when the callback scheme cannot express the
    required semantics, and only after a documented gap analysis
    per R9.
  - **R6.4** (Player): A Player MUST safely ignore unknown
    namespaces on tracking-related extension elements, per the DASH
    extension rules invoked by R1.

- **R13. Non-linear ad tracking — ADS-directed callbacks.**
  *Gist: The ADS owns the beacon schedule (which beacons, at which relative times); the Player just executes what the resolution document carries.*

  The specification MUST define a tracking mechanism that allows
  the ADS to instruct the Player on which tracking beacons to
  fire, and at which points relative to the ad's presentation. The
  ADS declares the schedule in its VAST; the APS expresses it in the
  resolution document using DASH callback events (or an equivalent
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
    R10.2 forbids.

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

The remainder of the proposal — Anatomy of the Overlay Resolution
Document, Ad Tracking, Client Execution Flow, Example
Implementation — should be read against these requirements.
Where a design choice satisfies several Rs in tension, the trade-off
is made explicit in the corresponding section.

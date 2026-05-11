# Glossary

Defines the technical terminology used across this body of documents.
Terms appear in the order they're first introduced in `01-intro.md`
through `05-dash-linear-interfaces.md` (plus
[`../analysis/dash-gap-analysis.md`](../analysis/dash-gap-analysis.md)).
Entries marked *(proposed)* are constructs that this project is
putting on the table; they are not standardised yet.

- **SGAI (Server-Guided Ad Insertion)**: pattern where the ad decision
  is made server-side (by an Ad Decision Server) rather than by the
  client. The MPD carries event references; when the playhead reaches
  one, the Player resolves a URL that returns a document describing
  the ad(s) to render. Reduces client-side stitching fragmentation and
  centralises inventory control.
- **Linear ad**: ad that *replaces* the primary content for the
  duration of a break (pre-roll, mid-roll, post-roll). The Player
  switches its source from the main timeline to the ad timeline and
  back.
- **Non-linear ad**: ad that *coexists* with the primary content; it
  does not interrupt playback. Rendered as an overlay or as a
  side-by-side composition.
- **Overlay**: umbrella term for any non-linear ad surface. Concrete
  sub-types used in this project (mapped to `layoutMode` enums in the
  proposal):
  - **L-shape (left / right)**: primary content is shrunk and anchored
    to one corner; ad fills the remaining "L" along the other two
    edges.
  - **Banner**: primary content keeps full scale; ad rendered as an
    overlay strip, typically at the bottom.
  - **Skyscraper**: tall, narrow vertical ad on one side (this label
    appears in the broadcaster's allowed-layouts list; not an
    explicit `layoutMode` enum in the current proposal).
  - **Sidebar**: similar idea to skyscraper, declared by the
    broadcaster as an allowed layout.
  - **Side-by-side**: primary content scaled and placed on one side;
    ad takes the other side; no visual overlap.
  - **Squeezeback**: synonym frequently used in broadcast for the
    "primary content shrunk to make room for ad real estate" effect
    (it is what L-shape and side-by-side do under the hood).
  - **Pause-ad**: ad rendered as an overlay only when the user pauses
    playback. State-triggered, not timeline-triggered.
  - **Lower-third**: traditional broadcast ad format anchored to the
    lower third of the screen; can be expressed via the banner or
    custom layout.
  - **Corner-bug**: small ad anchored to a corner; supports IAB Tile
    flexible aspect ratios.
- **MPEG-DASH 6th edition**: revision of ISO/IEC 23009-1 that
  introduced the `InsertPresentation` and `ReplacePresentation`
  constructs for linear SGAI.
- **MPD (Media Presentation Description) / Manifest**: the XML
  document a DASH player consumes to play media. It describes
  Periods, AdaptationSets, Representations and (with 6th edition)
  ad-related events.
- **ListMPD**: the resolution document returned by the ADS in the
  6th edition linear SGAI flow. The `InsertPresentation` /
  `ReplacePresentation` event in the main MPD points to a URL; that
  URL returns a `ListMPD` describing the ad presentation.
- **ListOverlay** *(proposed)*: the non-linear analogue of `ListMPD`.
  The `OverlayPresentation` (or `DynamicPresentation`) event in the
  main MPD points to a URL; that URL returns a `ListOverlay`
  document with `<svta:Overlay>` elements that describe the
  non-linear surfaces to render.
- **InsertPresentation** *(DASH 6th ed)*: signals that an ad
  presentation is to be **inserted into** the timeline alongside the
  main content. Used for splice-style insertion.
- **ReplacePresentation** *(DASH 6th ed)*: signals that an ad
  presentation **replaces** the primary content for the duration of
  the event. Used for traditional break-style ads.
- **OverlayPresentation** *(proposed, original name)*: the new event
  proposed by this project to signal a non-linear ad slot. Resolves
  to a `ListOverlay` document.
- **DynamicPresentation** *(proposed, current name)*: rename of
  `OverlayPresentation` adopted by the WG on 2026-04-29. The intent
  is to express *one* top-level MPD event whose semantics — replace,
  insert, or overlay — are decided dynamically based on the
  resolution document and the Player's capabilities. Whether the
  discriminator lives in a `content_type` attribute or in sub-types
  (`DynamicReplacePresentation`, `DynamicInsertPresentation`) is an
  open design decision (ADR pending).
- **ADS (Ad Decision Server)**: external server that returns the ad
  candidates eligible for a given slot. Owns targeting, frequency
  capping, brand safety filtering, fill-rate logic, and any
  business-side decisioning. Not responsible for enforcing the
  broadcaster's MPD-level constraints.
- **Player (Video Player)**: client-side component that reads the
  MPD, queries the ADS, validates the response against the MPD
  constraints, selects the ad, and composes it on screen. It is the
  enforcer of the broadcaster's policy.
- **Broadcaster / Content Owner**: the entity that owns the primary
  content and the viewer's screen. Declares ad opportunities in the
  MPD (where in the timeline, what kind of slot, what layouts are
  allowed, what duration / concurrency constraints apply).
- **IAB CTV Ad Standard**: the IAB's spec for ad units in connected
  TV environments; describes flexible-ratio formats (e.g. 8:1, 6:1,
  1:4) that this proposal defers to instead of redefining its own
  layout system. R5 of this proposal explicitly aligns with it.
- **SCTE-35**: ANSI/SCTE digital program insertion cueing standard;
  the markers that signal where ad opportunities exist in a stream.
  The current prototype consumes SCTE-35 markers (via Morpheus) and
  turns them into DASH dynamic events.
- **SVTA (Streaming Video Technology Alliance)**: industry consortium
  that hosts working groups on video tech topics. The Advertisement
  WG is the venue where this proposal is being incubated outside of
  Comcast and MPEG.
- **DASH-IF (DASH Industry Forum)**: industry body responsible for
  guidelines and interop on top of the MPEG-DASH base spec. Adjacent
  to the SVTA Ads WG for our purposes.
- **MPEG WG (more precisely the MPEG Systems WG that hosts DASH)**:
  the formal standards body where MPEG-DASH itself is maintained.
  Chair: Thomas Stockhammer.
- **Brand safety**: the requirement that the actual creative shown to
  a viewer satisfies the broadcaster's policy on prohibited content.
  In the AI-generated-ads pipeline that the prototype experiments
  with, brand safety becomes an explicit pipeline stage (prompt-level
  guardrails plus post-generation content classification) rather than
  a property of a curated ad pool.

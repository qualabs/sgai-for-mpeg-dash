# Glossary

Defines the technical terminology used across this body of documents.
Terms appear in the order they're first introduced in `01-intro.md`
through `05-dash-linear-interfaces.md` (plus
[`../analysis/dash-gap-analysis.md`](../analysis/dash-gap-analysis.md)).

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
- **Overlay**: umbrella term for any non-linear ad surface. The
  concrete sub-types (banner, l-shape, skyscraper, side-by-side,
  pause-ad, etc.) are defined and maintained by the IAB; this spec
  references the IAB definitions normatively and does NOT introduce
  new sub-types. See the IAB CTV Ad Format Guidelines live document:
  https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e
  — the accepted values are extracted into
  [`../analysis/iab-ad-templates.md`](../analysis/iab-ad-templates.md)
  by `prompts/analyze-iab-ad-templates.prompt` and refreshed on every
  build. Examples of sub-types encountered in practice include
  l-shape, banner, skyscraper, sidebar, side-by-side, squeezeback,
  pause-ad, lower-third, and corner-bug; these names are illustrative
  and the authoritative list is the IAB document, not this glossary.
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
- **InsertPresentation** *(DASH 6th ed)*: signals that an ad
  presentation is to be **inserted into** the timeline alongside the
  main content. Used for splice-style insertion.
- **ReplacePresentation** *(DASH 6th ed)*: signals that an ad
  presentation **replaces** the primary content for the duration of
  the event. Used for traditional break-style ads.
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
  layout system. R10 of this proposal explicitly aligns with it.
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

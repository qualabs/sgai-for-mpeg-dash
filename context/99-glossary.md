# Glossary

Defines the technical terminology used across this body of documents.
Terms appear in the order they're first introduced in `01-intro.md`
through `08-dash-extension-rules.md`.

- **SGAI (Server-Guided Ad Insertion)**: pattern where the ad decision
  is made server-side (by an Ad Decision Server) rather than by the
  client. The MPD carries event references; when the playhead reaches
  one, the Player resolves a URL (served by the Ad Presentation
  Server) that returns a document describing the ad(s) to render.
  Reduces client-side stitching fragmentation and centralises
  inventory control.
- **Linear ad**: ad whose form takes over the primary content
  surface during a slot (pre-roll, mid-roll, post-roll). The Player
  switches its rendering source from the main timeline to the ad
  timeline and back.
- **Non-linear ad**: ad that *coexists* with the primary content; it
  does not interrupt playback. Rendered as an overlay or as a
  side-by-side composition.
- **Overlay**: umbrella term for any non-linear ad surface. The
  concrete sub-types (banner, l-shape, skyscraper, side-by-side,
  pause-ad, etc.) are defined and maintained by the IAB; this spec
  references the IAB definitions normatively and does NOT introduce
  new sub-types. See the IAB CTV Ad Format Guidelines live document:
  https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e
  for the authoritative list. Examples of sub-types encountered in
  practice include
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
- **ListMPD**: the resolution document returned by the APS in the
  6th edition linear SGAI flow. The `InsertPresentation` /
  `ReplacePresentation` event in the main MPD points to a URL; that
  URL (served by the APS) returns a `ListMPD` describing the ad
  presentation. The APS derives the `ListMPD` from the VAST the ADS
  produced. The presentation options an ad offers appear in the
  ListMPD as an ordered list; document order is the Player's
  preference order (R5).
- **Presentation option**: a (form + layout) pairing offered for an
  ad candidate. The resolution document lists the options in an
  ordered list; document order is the preference order the Player
  follows (R5).
- **InsertPresentation** *(DASH 6th ed)*: signals that an ad
  presentation is to be **inserted into** the timeline alongside the
  main content. Used for splice-style insertion.
- **ReplacePresentation** *(DASH 6th ed)*: signals that an ad
  presentation **replaces** the primary content for the duration of
  the event. Used for traditional break-style ads.
- **ADS (Ad Decision Server)**: external server that decides which
  ads to serve for a given slot and responds with a **decision
  document** — typically VAST (IAB), though the ADS is not bound to
  VAST and MAY emit another format. Owns targeting, frequency
  capping, brand safety filtering, fill-rate logic, ordering, and any
  business-side decisioning, plus authority over the tracking
  schedule. Does NOT convert its output into the MPD-native / SGAI
  resolution document (that is the APS), and is not responsible for
  enforcing the Publisher's MPD-level constraints.
- **APS (Ad Presentation Server)**: external server that sits between
  the Player and the ADS. Exposes the endpoint the Player resolves
  (referenced by the Publisher in the MPD event `@url`), calls the
  ADS, and **converts whatever the ADS emits — VAST (IAB) or any
  other decision format — into the MPD-native / SGAI resolution
  document** the Player understands (`ListMPD` or single-period
  alternative MPD for linear, the overlay resolution document for
  non-linear). Translating any ADS output into the resolution
  document this spec defines is the APS's responsibility; the
  conversion itself is not defined by this spec. Translates the
  ADS-declared tracking events into DASH callback events. Not the
  ad-decisioning authority and not the constraint enforcer — a
  translation / presentation layer (decision document in, resolution
  document out).
- **Player (Video Player)**: client-side component that reads the
  MPD, queries the APS, validates the response against the MPD
  constraints, selects the ad, and composes it on screen. It is the
  enforcer of the Publisher's policy.
- **Publisher**: the entity that owns the primary content and the
  viewer's screen. Declares ad opportunities in the MPD (where in
  the timeline, what kind of slot, what layouts are allowed, what
  duration / concurrency constraints apply). (Previously named
  "Broadcaster / Content Owner".)
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
  a viewer satisfies the Publisher's policy on prohibited content.
  In the AI-generated-ads pipeline that the prototype experiments
  with, brand safety becomes an explicit pipeline stage (prompt-level
  guardrails plus post-generation content classification) rather than
  a property of a curated ad pool.
- **Foreign-namespace open content** *(DASH §5.2.1)*: DASH's normative
  extension mechanism allowing XML elements and attributes from non-
  DASH namespaces under any DASH container, via the
  `<xs:any namespace='##other' processContents='lax'/>` declaration on
  every container in the MPD schema. Legacy clients discard such
  elements together with their full subtree (DR-3 in
  [`08-dash-extension-rules.md`](./08-dash-extension-rules.md)).
- **ImportedMPD** *(DASH 6th ed)*: DASH element that imports an
  external MPD by URI from a parent (typically a ListMPD-level
  `<Period>`). §5.3.2.6 binds the imported document to the SPS
  profile (DR-1 in
  [`08-dash-extension-rules.md`](./08-dash-extension-rules.md)).
- **Interoperability Point URI** *(DASH Annex F)*: a profile URI
  declared in `MPD@profiles` advertising conformance to a DASH
  extension authored under Annex F. Required when a custom delivery
  format is introduced for AdaptationSet / Representation carriage
  (DR-4 in
  [`08-dash-extension-rules.md`](./08-dash-extension-rules.md)).
- **Single-Period Static (SPS) profile** *(DASH 6th ed, §8.15)*: DASH
  profile constraining the document to a single Period and inheriting
  §7.3 verbatim, which limits every Representation's `@mimeType` to
  the IETF RFC 4337 registry (`video/mp4`, `audio/mp4`,
  `application/mp4`). All MPDs reached via `<ImportedMPD>` are bound
  to SPS (DR-1 in
  [`08-dash-extension-rules.md`](./08-dash-extension-rules.md)).
- **Sub-MPD**: an MPD reached via `<ImportedMPD>` from a parent
  ListMPD or primary MPD. SPS-conformant by construction (DR-1 in
  [`08-dash-extension-rules.md`](./08-dash-extension-rules.md)).

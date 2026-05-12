# MPEG-DASH 6th Edition — Gap Analysis vs SGAI Requirements

`[GROUNDED_BY=notebooklm]` — authoritative claims verified against
ISO/IEC 23009-1 (MPEG-DASH 6th edition, FDIS) via the "Streaming
Protocols — DASH, HLS, C2PA, DRM" NotebookLM notebook. Claims that
could not be cross-checked against the source are tagged `[inferred]`.

> Companion to [`../spec/05-dash-linear-interfaces.md`](../spec/05-dash-linear-interfaces.md).
> That document inventories the **linear baseline** that DASH 6th
> edition already provides. This document maps **the requirements R1..R10
> in [`../spec/03-requirements.md`](../spec/03-requirements.md) against
> that baseline** and identifies what the proposed SGAI extension must
> add. Use cases referenced below live in
> [`../spec/04-use-cases.md`](../spec/04-use-cases.md).

## 1. Scope

**In scope.** Each functional and governance requirement in
[`../spec/03-requirements.md`](../spec/03-requirements.md) (R1..R10)
mapped against what MPEG-DASH 6th edition provides natively, with a
verdict (full / partial / gap / N/A), a justification, and — for gaps
and partials — the construct or extension point the proposal must
introduce or extend.

**Out of scope.** Detailed XML schema for the proposed extension
(belongs in the norm draft, not in the gap analysis). VAST 4.x
internals beyond the linear adapter mapping already covered in
[`../spec/05-dash-linear-interfaces.md`](../spec/05-dash-linear-interfaces.md).
SSAI / server-side stitching. Post-roll, companion ads, native
in-chrome ads (all out of scope per [`../spec/04-use-cases.md`](../spec/04-use-cases.md)).
DRM, auth, low-latency, ABR — orthogonal to SGAI.

## 2. Coverage matrix

Verdicts: **full** (DASH 6th covers it as-is) / **partial** (DASH 6th
covers a subset; the proposal extends it) / **gap** (no native DASH
6th construct covers it; the proposal introduces a new one or extends
an existing one substantively) / **N/A** (the requirement is a
governance / process constraint that DASH 6th cannot satisfy or fail
by itself).

| #   | Requirement                                                  | Verdict | DASH 6th capability used / missing |
|-----|--------------------------------------------------------------|---------|------------------------------------|
| R1  | DASH 6th compliance and graceful degradation                 | full    | EventStream "ignore-if-unknown" semantics (§5.10.1); year-pinned scheme URIs (§5.16 `:2025`); ERT randomisation via `@earliestResolutionTimeOffset` (§5.16). MPD-level unknown attribute / element survival rule mandated by §5.2.1. The extension contract is exactly what DASH 6th already mandates. UC-07 (legacy Player encounters new constructs) is the cross-cutting scenario whose graceful-degradation outcome R1 directly produces. |
| R2  | Honour the three-actor model                                 | partial | Linear flow uses `InsertPresentation` (§5.16.2) / `ReplacePresentation` (§5.16.3) and `ListMPD` (§8.14) cleanly. Non-linear flow has no native event; new event types are needed for overlay / pause-triggered slots (see G1, G2). |
| R3  | Device-capability diversity (D1..D5)                         | gap     | `ImportedMPD` is restricted to Single-Period Static Profile (§8.15, `urn:mpeg:dash:profile:sps:2024`) — only standard audio/video AdaptationSets. No "multi-form" candidate (video + image + HTML) where the Player picks the renderable form. DASH 6th's only multi-stream composition primitive is the Supplementary Video Descriptor (§5.8.5.16, `urn:mpeg:dash:supv:2022`) which targets picture-in-picture, not multi-form ad selection (see G3). |
| R4  | Broadcaster-declared max slot duration, Player-enforced      | full    | `@maxDuration` on `InsertPresentation` / `ReplacePresentation` (§5.16); cap-trim semantics mandated in §5.16.5 — verbatim: "If the Alternative Presentation initiated by this event has a longer duration than specified in this element, it shall be terminated at the end of this duration". The non-linear extension reuses the same attribute on the new overlay / pause events. |
| R5  | Device-aware ad selection (multi-form ads, Player picks form)| gap     | Same root cause as R3: ImportedMPD restricted to SPS (§8.15), no carrier in the ListMPD or sub-MPD for alternate renderable forms (image, HTML) tied to one ad candidate. State vocabulary in §I.4 (Table I.5) has no device-capability keys either (see G3, G5). |
| R6  | Ad tracking carrier                                          | full    | Callback event scheme `urn:mpeg:dash:event:callback:2015` (§5.10.4.5) carries impression, start, quartiles, complete as `<Event>` entries in an `<EventStream>` of that scheme inside the ad sub-MPD. Application-level metadata (ClickThrough, AdSystem, AdTitle, UniversalAdId) has no native DASH carrier — vendor-namespaced extension elements per R1's ignore-if-unknown contract (see G6). |
| R7  | Respect ADS-returned order                                   | full    | `ListMPD` `<Period>` order is normative in §8.14 (a ListMPD is a playlist of MPDs; selection happened upstream inside the ADS). The Player plays Periods in declared order; the only legal deviations are R3 (drop unrenderable candidates) and R4 (cap-trim). No DASH 6th construct forces re-ordering — full coverage as-is. |
| R8  | Justify any addition or omission                             | N/A     | Governance requirement — a constraint on the proposal's authoring process, not on DASH itself. |
| R9  | Minimise net new constructs                                  | N/A     | Governance requirement — a constraint on the proposal's design choices, not on DASH itself. Drives the "Reuse opportunities" section below. |
| R10 | Do not recreate a layout system                              | gap     | DASH 6th has no spatial layout vocabulary at all (verified — §5.16 events have no layout fields). Reuse path is HTML5 / CSS, not a DASH construct (see G4). |

## 3. Gaps detail

### G1 — No native non-linear ad construct (R2 partial, foundational gap)

**Status quo.** DASH 6th edition's SGAI primitives are exclusively
linear. §5.16.1 defines an *Alternative Media Presentation* as "a
presentation that replaces the main Media Presentation at a certain
point on the media timeline for a duration of time". `InsertPresentation`
(§5.16.2) pauses the main timeline and resumes it where it left off;
`ReplacePresentation` (§5.16.3) replaces a span of the main timeline
while the main media clock continues to advance. Neither construct
allows the alternative presentation to **coexist** with primary
content.

**What is missing.** A new event type — call it `OverlayPresentation`
or equivalent — that signals an ad opportunity which **does not stop
or replace** the primary content. Required attributes on this event
(beyond the linear baseline reused per R9):
- *Allowed layouts*: a closed enumeration of overlay layouts the
  broadcaster permits for this slot (banner, L-shape, side-by-side,
  corner, …). Maps to the broadcaster intent expressed in UC-03 / UC-04.
- *Concurrency cap*: maximum number of overlays the broadcaster
  allows on screen simultaneously during this slot.
- *Overlay duration cap*: maximum on-screen time per overlay (the
  non-linear analogue of `@maxDuration`, reusing the same attribute).

The event MUST follow R1's "ignore-if-unknown" contract: a legacy
Player encountering the new scheme URI silently skips it (UC-07). The
year-pinned scheme convention (`...:overlay:<year>`) is mandated by
R1's sub-requirement on scheme URIs.

**Affects.** UC-03 (coexisting overlay), UC-04 (hybrid linear +
overlay), UC-05 (pause-triggered ad) directly. UC-06 (multi-ad break)
indirectly when one of the pod's slots is non-linear.

### G2 — No action-triggered events (R2 partial, supports UC-05)

**Status quo.** §5.10.1 defines events as strictly timed: "Events are
timed, i.e. each event starts at a specific media presentation time
and may have a duration". User actions interact with events only by
moving the playhead — a seek causes the client to re-evaluate which
events are active at the new position. There is no construct that
fires an event in response to a state change such as *pause*, *resume*,
*enter-fullscreen*, or *mute*.

**What is missing.** UC-05 (pause-triggered ad) requires an ad
opportunity bound to a Player state rather than a timeline position.
The proposal must specify how the action-trigger semantics are layered
on top of (or alongside) the existing `EventStream` machinery without
violating §5.10.1's timed-event invariant. Two candidate paths exist —
either is compatible with R1:

1. **Application-layer trigger, DASH carrier for the resolution
   contract**: the broadcaster declares a pause-ad opportunity in the
   MPD via a new action-triggered scheme URI; `presentationTime` on
   the event is a sentinel (or the event lives on a different
   `EventStream` profile). The Player application logic decides
   *when* to dispatch the ADS request based on local pause state. The
   ADS resolution document and tracking carriers reuse the linear
   constructs (`ListMPD`, callback events). Minimises net new DASH
   constructs (R9-aligned) at the cost of moving "when to fire" into
   the Player application layer.
2. **New event semantics in DASH**: extend §5.10 with an explicit
   action-triggered event class. Larger spec surface; requires WG
   acceptance of a new event model. R9 disfavours this unless option 1
   proves insufficient.

The proposal should default to option 1 unless WG feedback says
otherwise.

**Affects.** UC-05 only.

### G3 — No carrier for multi-form ad candidates (R3, R5)

**Status quo.** The `ListMPD` profile (§8.14) lists ad candidates as
`<Period>` entries that delegate to per-ad sub-MPDs via `<ImportedMPD>`.
The sub-MPD is restricted to the **Single-Period Static Profile**
(§8.15, `urn:mpeg:dash:profile:sps:2024`), which carries a single-Period MPD with standard DASH
AdaptationSets (audio, video). There is no provision for the same ad
candidate to expose *alternative renderable forms* — for example, the
same creative as a video stream, a static image, and an interactive
HTML payload — for the Player to pick from depending on device
capability. The Supplementary Video Descriptor (§5.8.5.16,
`urn:mpeg:dash:supv:2022`) is the only multi-stream composition
construct in the spec; it targets picture-in-picture video composition,
not multi-form ad selection.

**What is missing.** A way to attach, to each ad candidate, **a set of
renderable forms** with optional ADS-supplied priority hints. The
Player walks the forms in priority order and renders the
highest-fidelity form it can support on the device (R3 device walk-down;
R5 device-aware selection). Two extension points exist within DASH 6th:

1. **Extend the ListMPD per-Period record** with a vendor-namespaced
   `<RenderableForms>` element (or equivalent) listing image / HTML /
   video forms with URIs, MIME types, and intrinsic durations. Legacy
   Players ignore the unknown namespace per R1; new Players consume
   it. Compatible with the SPS restriction because the alternative
   forms live in the ListMPD layer, not inside the imported sub-MPD.
2. **Relax §8.15** (Single-Period Static Profile) to allow non-video
   AdaptationSets (image, HTML) inside the imported sub-MPD. Bigger
   spec footprint; touches a profile that is intentionally minimal.

The proposal should default to option 1: ListMPD-level multi-form
declaration. It is the smaller surface, fully consistent with R9
(extend rather than introduce), and the SPS profile remains untouched.

**Affects.** UC-03, UC-04 (overlay portion), UC-05 across D1..D5
where the Player must skip forms the device cannot render.

### G4 — No carrier for layout / concurrency constraints (R10, R2)

**Status quo.** §5.16's `AlternativeMPDEventType` complex type carries
only timeline / execution attributes: `@url` (also `@uri` in the XML
schema), `@earliestResolutionTimeOffset`, `@serviceDescriptionId`,
`@maxDuration`, `@executeOnce`, `@noJump`, `@skipAfter`, plus the
`ReplacePresentation`-only `@returnOffset`, `@clip`
(`@clipDuration` in the XML schema), `@startWithOffset`. None of
these touch spatial layout, overlay surfacing, or concurrency. There
is no mechanism in §5.16 or anywhere else in DASH 6th to declare
"this slot allows banner and L-shape only" or "max 2 overlays
concurrently".

**What is missing.** Layout vocabulary on the new non-linear event
(G1). The proposal explicitly does not introduce a parallel layout
standard (R10); it defers spatial detail to HTML/CSS. What the event
must carry is:
- *Closed layout enumeration*: `banner | l-shape | side-by-side |
  skyscraper | sidebar | squeezeback | pause-ad | lower-third |
  corner-bug`, plus an extensibility hook for future entries. Each
  enum value is a *contract token*; the actual rendering is HTML/CSS
  in the Player. The canonical vocabulary lives in
  [`../spec/99-glossary.md`](../spec/99-glossary.md).
- *Allowed-set semantics*: the broadcaster declares which layout
  tokens are permitted for the slot. The Player MUST reject (per R2)
  any candidate whose layout falls outside the allowed set.
- *Concurrency cap*: integer `maxConcurrentOverlays`.

The IAB CTV Ad Standard provides the canonical flexible-ratio formats
that should anchor the layout enum (R10 alignment with IAB CTV is
explicit in [`../spec/03-requirements.md`](../spec/03-requirements.md)).

**Affects.** UC-03 (layout enum), UC-04 (subset of layouts allowed
during a linear take-over), UC-05 (full-screen-pause as a distinct
token).

### G5 — Device capability signalling has no native vocabulary (R3, R5)

**Status quo.** The `urn:mpeg:dash:state:<suffix>` vocabulary in
Annex §I.4 (Table I.5) is restricted to playback / telemetry state:
codec / bandwidth (`audio`, `video`), language (`lang#…`), encryption
scheme (`encryption`), CMCD (`cmcd#…`), Alternative MPD callback
metrics (`execution-delta#id`, `expected-duration#id`,
`execution-count#id`), and previous-state hints. None of these convey
rendering capability — whether the Player has an overlay surface,
HTML rendering, dual video decoders, etc.

**What is missing.** Whether the proposal even needs Player → ADS
capability signalling depends on the design choice for R5. The
multi-form ad approach (G3) keeps the ADS device-agnostic: the ADS
returns the same multi-form candidates to every viewer, and the
Player picks locally. With multi-form ads, **no capability signalling
is required** and §I.4 needs no extension. This is the R9-clean
solution and the proposal's working position. Capability signalling
remains a fallback if multi-form turns out to be insufficient — to be
revisited if WG feedback or implementation experience forces it.

**Affects.** R3, R5, UC-03..UC-05 indirectly. Resolved by G3, not by
extending §I.4.

### G6 — Application-layer ad metadata has no native carrier (R6 partial)

**Status quo.** R6 is full for the **tracking** path: the callback
event scheme (§5.10.4.5) cleanly carries impression / start /
quartiles / complete as `<Event>` entries in an `<EventStream>` inside
the ad sub-MPD. But VAST application-level metadata —
`<ClickThrough>`, `<AdSystem>`, `<AdTitle>`, `<UniversalAdId>` — has
**no normative DASH 6th carrier** (verified against the 6th edition
source, see [`../spec/05-dash-linear-interfaces.md`](../spec/05-dash-linear-interfaces.md)).

**What is missing.** A documented convention for carrying these
fields via vendor-namespaced extension elements on `ImportedMPD` or
on a sidecar payload returned alongside the `ListMPD`. R6 already
mandates this approach in principle: "Application-level metadata that
has no native DASH carrier (…) MAY be conveyed via vendor-namespaced
extension elements". The gap is documenting the **specific** field
names, namespaces, and serialisation the proposal recommends so
implementations interop. This is a thin spec-side gap (not a
DASH-side gap), but it must be closed for production deployments.

**Affects.** Production ADS adapters integrating VAST upstream.

## 4. Reuse opportunities (R9)

Listed in priority order — the proposal MUST reuse these constructs
before introducing alternatives. Each opportunity already passes a
"would extension suffice?" check; departures from reuse must be
justified per R8.

1. **`InsertPresentation` / `ReplacePresentation` (§5.16) for linear
   portions.** The non-linear extension does not touch linear
   semantics. UC-01, UC-02, UC-06 are satisfied by the linear baseline
   as-is. UC-04's take-over portion reuses `InsertPresentation` /
   `ReplacePresentation` verbatim.
2. **`ListMPD` profile (§8.14, `urn:mpeg:dash:profile:list:2024`) as the resolution document for
   non-linear slots.** The same construct that today answers a
   linear ADS request answers the non-linear request: a playlist of
   `<Period>` entries, ADS-determined order, Player honours order
   modulo R3 / R4. The G3 extension lives at the per-Period record
   layer (renderable forms), not in a new resolution document.
3. **Callback event scheme `urn:mpeg:dash:event:callback:2015`
   (§5.10.4.5) for tracking.** Already mandated by R6. Covers
   impression, start, quartiles, complete, plus arbitrary VAST
   tracking events translated by the ADS adapter into callback
   events. No new tracking carrier needed.
4. **`@maxDuration` (§5.16.5) for slot duration cap.** The same
   attribute carries the cap for linear slots (R4) and for the new
   non-linear slots (per overlay, per pause-ad). Reuse is verbatim;
   semantics extend naturally — the §5.16.5 cap-trim rule
   ("terminated at the end of this duration") applies to any
   Alternative Presentation, linear or non-linear, by symmetry.
5. **§I.4 `UrlParamInfo` state vocabulary for ADS request
   parametrisation.** Reused unchanged — playback state, CMCD,
   language, encryption hints flow from Player to ADS via the
   existing mechanism. G5 deliberately does not extend this
   vocabulary (multi-form ads make device-capability signalling
   unnecessary).
6. **EventStream "ignore-if-unknown" extension contract (§5.10.1) and
   the MPD-level survival rule (§5.2.1).** The cornerstone of R1 /
   UC-07. §5.10.1 lets a Player subscribe to an Event Stream of
   interest and ignore others; §5.2.1 mandates that "if a DASH client
   removes XML attributes or elements [...] not in the standard XML
   schema [...] or from other namespaces, the remaining result is
   still a valid XML document that can be used for presentation".
   Every new construct introduced by the proposal MUST be expressible
   via one of these extension points. This is reuse of a *contract*,
   not of a construct, but it is the most important one — it is
   what makes the whole proposal backward compatible at deployment
   time.
7. **Year-pinned scheme URI convention (§5.16, §8.14).** New scheme
   URIs (e.g. `urn:mpeg:dash:event:overlay:<year>`) follow the
   established `:<year>` suffix pattern. This makes the
   "ignore-if-unknown" guarantee for legacy Players clean and
   auditable per edition.
8. **Single-Period Static Profile (§8.15, `urn:mpeg:dash:profile:sps:2024`) for the per-ad sub-MPD.**
   Sub-MPDs imported by ListMPD keep the SPS restriction unchanged.
   The G3 multi-form extension lives at the ListMPD layer (above the
   sub-MPD), so SPS is untouched.

## 5. Open questions

Items requiring WG input, prototype validation, or further research
before the norm draft locks them in.

1. **Action-trigger placement for UC-05 (G2).** Application-layer
   trigger with DASH carrying only the resolution contract (preferred,
   R9-clean) vs new event semantics in §5.10 (larger spec surface).
   Decision blocks the UC-05 portion of the draft.
2. **Multi-form ad carrier schema (G3).** Vendor-namespaced
   `<RenderableForms>` element on the ListMPD per-Period record vs
   relaxing §8.15 (SPS) to allow non-video AdaptationSets. Working
   position: per-Period extension. Validate with one or two ADS
   vendors before locking.
3. **Layout vocabulary baseline (G4).** Anchor the closed enum on the
   IAB CTV Ad Standard's flexible-ratio formats (8:1, 6:1, 1:4, …) or
   on a smaller broadcast-aligned token set (banner, L-shape,
   side-by-side, corner)? The two are reconcilable but the proposal
   needs to name a starting point. The canonical enum lives in
   [`../spec/99-glossary.md`](../spec/99-glossary.md).
4. **D5 ADS request policy.** Whether the Player issues the ADS
   request on devices that cannot render any form of the candidates
   (D5, and any D3 / D4 case where every candidate's forms are
   unrenderable) to support impression accounting and frequency
   capping. Privacy / bandwidth trade-off; raised as an open question
   in UC-03 already.
5. **Hybrid break composition on single-decoder devices (UC-04, D3
   / D4).** Whether the broadcaster can express "overlay on top of
   linear ad is allowed on devices with HTML / image surfaces only"
   and whether such a layout token belongs in the G4 enum or is
   declared via a separate slot attribute. Raised in UC-04 already.
6. **VAST 4.x version pin.** [`../spec/05-dash-linear-interfaces.md`](../spec/05-dash-linear-interfaces.md)
   flags this — the exact 4.x version (4.0 / 4.1 / 4.2 / 4.3) used by
   industry practice needs to be pinned against the IAB Tech Lab page
   on the next revision. Out of DASH WG scope but inside SVTA Ads WG
   scope.
7. **Application-level metadata namespace (G6).** What namespace and
   field names the proposal recommends for `<ClickThrough>`,
   `<AdSystem>`, `<AdTitle>`, `<UniversalAdId>` on `ImportedMPD`. A
   thin spec gap with high interop value.
8. **Backward-compat checklist application per construct.** The
   spec now ships [`../spec/07-backward-compat-checklist.md`](../spec/07-backward-compat-checklist.md)
   — the norm MUST apply that checklist (placement, extension rule,
   walk-through, sibling check, UC-07 test, namespace, doc
   cross-reference) to **each** new construct G1..G4 introduces.
   Audit table belongs in the norm's chapter 4 (Conformance).

## References

- ISO/IEC 23009-1 (FDIS, MPEG-DASH 6th edition):
  §5.2.1 MPD-level survival rule for unknown XML attributes / elements;
  §5.8.5.16 Supplementary Video Descriptor (`urn:mpeg:dash:supv:2022`);
  §5.10 EventStream and callback event semantics
  (§5.10.1 EventStream and ignore-if-unknown, §5.10.4.5 callback event
  scheme `urn:mpeg:dash:event:callback:2015`);
  §5.16 Alternative MPD Insertion / Replacement Events
  (§5.16.1 framework, §5.16.2 `InsertPresentation`,
  §5.16.3 `ReplacePresentation`, §5.16.5 cap-trim rule);
  §8.14 List MPD profile (`urn:mpeg:dash:profile:list:2024`);
  §8.15 Single-Period Static Profile (`urn:mpeg:dash:profile:sps:2024`);
  Annex I.4 (Table I.5) state vocabulary for `UrlParamInfo`.
- [`../spec/02-actors.md`](../spec/02-actors.md) — three-actor model.
- [`../spec/03-requirements.md`](../spec/03-requirements.md) — R1..R10.
- [`../spec/04-use-cases.md`](../spec/04-use-cases.md) — UC-01..UC-07,
  device classes D1..D5.
- [`../spec/05-dash-linear-interfaces.md`](../spec/05-dash-linear-interfaces.md)
  — linear SGAI baseline (the constructs reused by this analysis).
- [`../spec/06-naming-and-namespaces.md`](../spec/06-naming-and-namespaces.md)
  — namespace policy for the new constructs G1..G4 propose.
- [`../spec/07-backward-compat-checklist.md`](../spec/07-backward-compat-checklist.md)
  — per-construct verification checklist the norm MUST satisfy.
- [`../spec/99-glossary.md`](../spec/99-glossary.md) — terminology
  and canonical layout vocabulary.
- IAB CTV Ad Standard — anchor for the layout vocabulary baseline
  (G4 / open question 3). Exact version pin pending.
- IAB Tech Lab, VAST 4.x — upstream ad-decisioning protocol; exact
  4.x version pin pending per [`../spec/05-dash-linear-interfaces.md`](../spec/05-dash-linear-interfaces.md).

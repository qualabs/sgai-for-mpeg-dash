# DASH 6th Edition Gap Analysis

> Grounded against ISO/IEC 23009-1:2025 (MPEG-DASH 6th edition, FDIS)
> via NotebookLM (notebook *Streaming Protocols — DASH, HLS, C2PA, DRM*).
> Requirements terminology follows RFC 2119 (MUST / SHOULD / MAY). The
> requirements R1..R15, the use cases UC-01..UC-07, and the
> extension-rule closure DR-1..DR-7 referenced below live in
> [`../context/`](../context/) — this document compares those against
> the baseline DASH 6th edition surface; it does not restate them.

## 1. Scope

**Compared.** The functional, non-functional and governance
requirements stated in [`../context/03-requirements.md`](../context/03-requirements.md)
(R1..R15) and the use cases in
[`../context/04-use-cases.md`](../context/04-use-cases.md)
(UC-01..UC-07) against the normative surface of MPEG-DASH 6th edition
(ISO/IEC 23009-1:2025), with particular attention to §5.16
(Alternative MPD Insertion / Replacement Events), §8.14 (List MPD
profile), §5.10 (Event Streams and the callback event scheme), §5.2.1
(foreign-namespace open content), §5.3.2.6 / §8.15 / §7.3 / RFC 4337
(SPS conformance under `<ImportedMPD>`), §5.8.4.8 / §5.8.4.9 (vendor
descriptors), §5.8.5.16 (supplementary video services), Annex F
(non-ISO-BMFF delivery) and Annex L (Implementation of Nonlinear
Playback — name-only collision; see §3.A).

**Out of scope.** SSAI / server-side stitching; the ADS's internal
decisioning protocol (R11 + OOS-2); DRM, authentication and
token-exchange flows; Player implementation details (ABR, buffer
policy, decoder re-tasking) — all orthogonal to the gap surface.
Comprehensive VAST → ListMPD coverage is also out of scope (see
[`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
for the linear baseline adapter mapping).

**Methodology.** Each requirement is classified as **full**,
**partial**, **gap** or **N/A** against the baseline. *Full* means
DASH 6th already provides a carrier or rule that satisfies the
requirement with no spec-side addition. *Partial* means a carrier
exists for the linear sub-case but not for the non-linear extension,
or a carrier exists but the slot-level semantics required by the
requirement (e.g. overlay window, concurrency cap) are absent.
*Gap* means no DASH 6th carrier exists and the spec MUST introduce
one within the DR-1..DR-7 closure. *N/A* applies to governance
requirements that bind the spec document itself, not DASH 6th.

## 2. Coverage Matrix

| Req | Topic | DASH 6th capability | Coverage |
|---|---|---|---|
| R1 | Backward compat / graceful degradation | §5.2.1 foreign-namespace open content (DR-2 / DR-3); Event `schemeIdUri` ignore-if-unknown; vendor descriptors §5.8.4.8 / §5.8.4.9 | **full** |
| R1.2 | Admissible extension points enumeration | §5.2.1, §5.10, §5.8.4.8 / §5.8.4.9, Annex F (closed by DR-1..DR-7) | **full** |
| R1.3 | No semantic override of pre-existing constructs | Foreign-namespace siblings (DR-2) do not alter baseline semantics; year-pinned scheme URIs prevent override | **full** |
| R2 | Three-actor model (Broadcaster / ADS / Player) | Three-actor decomposition exists for linear (§5.16 events emit `@url`; ADS returns `ListMPD` §8.14; Player enforces) | **partial** — pattern exists but only for linear |
| R2.1 | Broadcaster declares slot constraints in MPD | §5.16: `@maxDuration`, `@earliestResolutionTimeOffset` on `InsertPresentation` / `ReplacePresentation`; `@returnOffset`, `@clipDuration`, `@startWithOffset` on `ReplacePresentation` | **partial** — only linear-slot constraints; no allowed-layouts, no overlay-duration, no concurrency-cap attribute exists in DASH 6th |
| R2.2 | ADS not bound to enforce Broadcaster constraints | DASH 6th is silent on ADS responsibilities (the ADS is described only as the resolver of `@url`); R2.2 is satisfied by absence of obligation | **full** |
| R2.3 | Player validates ADS response against MPD constraints | §5.16.5 mandates trim against `@maxDuration` for linear; broader validation is implicit | **partial** — no normative validation step for non-linear (no non-linear constraints exist to validate against) |
| R2.4 | Every new mechanism expressible within three-actor contract | Spec-document requirement; DASH 6th carriers (DR-2 / R1.2) are agnostic | **N/A** (binds the SGAI spec, not DASH 6th) |
| R3 | Device-class diversity | DASH 6th has no device-class signalling abstraction; codec / DRM signalling exists on AdaptationSet / Representation but is orthogonal | **partial** — D1..D5 differentiation is entirely a Player-side concern; no DASH 6th construct distinguishes overlay-capable from overlay-incapable Players |
| R3.1 | Spec enumerates device classes × ad opportunities | Spec-document requirement | **N/A** |
| R3.2 / R3.3 | Player produces defined behaviour per device class; never renders an unrenderable form | Player-side; DASH 6th provides codec / mime signalling on Representations but no overlay-form signalling | **partial** (see R5) |
| R4 | Broadcaster-declared max slot duration, Player-enforced | `@maxDuration` on §5.16 events; §5.16.5 mandates trim at the cap | **partial** — defined for linear slots; no construct caps a non-linear overlay window |
| R4.1 | Broadcaster declares cap on every slot (linear + non-linear) | Linear-only carrier exists | **partial** |
| R4.2 / R4.3 / R4.5 | Player stops at cap, never extends, trims actual length | §5.16.5 trim rule for linear; no equivalent for non-linear (because non-linear slots do not exist in DASH 6th) | **partial** |
| R5 | Device-aware ad selection (candidate with multiple renderable forms) | `ListMPD` §8.14 is a *playlist of MPDs*, not a *candidate set*; each `Period` has exactly one resolved sub-MPD; sub-MPD is SPS-bound (DR-1) → ISO-BMFF only on the AdaptationSet axis | **gap** — no DASH 6th construct expresses "candidate carrying N renderable forms (video / image / HTML), ADS-ranked" |
| R5.1 / R5.5 | ADS returns candidates with one-or-more forms, optionally multi-layout | No multi-form / multi-layout candidate carrier in DASH 6th | **gap** |
| R5.2 / R5.3 / R5.6 / R5.7 | Player walks forms, applies (device ∩ allowed-layouts ∩ ADS-hints), skips on no-fit | No DASH 6th surface to walk; Player has no Broadcaster-declared "allowed-layouts" to intersect against | **gap** |
| R5.4 | ADS does not need device-class matrix | DASH 6th makes no demand on ADS internals; satisfied by absence | **full** |
| R6 | In-band tracking carrier | Callback event scheme `urn:mpeg:dash:event:callback:2015` (§4.7, §5.10.4.5) — `<Event>` text() is the URL to GET | **full** for AV-form linear ads inside SPS sub-MPDs |
| R6.2 | Tracking beacons carried as callback events | Carrier exists | **full** |
| R6.4 | App-level VAST metadata (`ClickThrough` / `AdSystem` / `AdTitle` / `UniversalAdId`) | DASH 6th defines NO native carrier for these — confirmed against §8.14 source; ADS adapters use vendor-namespaced extension elements or sidecar payloads | **gap** — covered by vendor namespace (§5.2.1) per R1.2 / DR-2 |
| R6.5 | Player ignores unknown namespaces on tracking-related extensions | §5.2.1 + DR-3 | **full** |
| R6.6 | Non-AV asset URL MUST NOT live on `@mimeType` of an AdaptationSet / Representation reached via `<ImportedMPD>` or inline under a ListMPD-level Period | DR-1 (§5.3.2.6 → §8.15 → §7.3 → RFC 4337) and DR-5 (§8.14 inline inherits CMAF profile §8.12) close that axis; only DR-6 carriers admissible | **gap** for the *carrier choice*, **full** for the *prohibition* (it is structurally enforced) |
| R7 | Respect ADS-returned order | `ListMPD` §8.14: `Period` elements played in document order | **full** for ordering itself |
| R7.2 / R7.3 / R7.4 | Player MAY drop a candidate (unrenderable / over-cap), MUST NOT reorder | DASH 6th has no "candidate skip" semantics on `ListMPD` because every Period resolves to a single sub-MPD that the Player will play; the drop semantics needed for R5 / R4 enforcement are not in §8.14 | **partial** — order semantics exist, drop semantics do not |
| R7.5 | Trim during play | §5.16.5 mandates trim for `ReplacePresentation`; applies to `ListMPD` per §8.14 | **full** for linear |
| R8 | Justify any addition or omission | Spec-document requirement | **N/A** |
| R9 | Minimise net new constructs | Spec-document requirement | **N/A** |
| R10 | Defer overlay layout to HTML5 / CSS | DASH 6th defines no parallel layout system to displace; §5.8.5.16 supplementary video defines a codec-level subpicture mechanism (VVC) but explicitly states "composition of the main video and the supplementary video is out of the scope of the DASH client" — not a layout system | **full** — DASH 6th does not stand in the way |
| R11 | No dependency on VAST | DASH 6th itself imposes no VAST dependency; the Player ↔ ADS interface is `@url` + `ListMPD`, format-agnostic on the Player side | **full** |
| R12 | Ad-type / layout vocabulary owned by IAB | DASH 6th defines no ad-type or layout vocabulary | **N/A** (orthogonal) |
| R13 | Reuse linear tracking mechanism for non-linear | Callback scheme `urn:mpeg:dash:event:callback:2015` is a scheduled HTTP GET keyed by `presentationTime`; mechanism is reusable | **partial** — carrier reusable, but quartile alignment to a Broadcaster-declared overlay window (not the ad's intrinsic duration) requires the spec to define the timing reference; no DASH 6th rule covers this |
| R14 | Single concurrent non-linear ad | DASH 6th has no concurrency model for ads (there are no non-linear ads to be concurrent) | **gap** — spec-side serialisation rule, with no DASH 6th carrier needed beyond the slot constraint declared per R2.1 |
| R15 | Admissible carriers limited to video, image, HTML | DASH 6th admits ISO-BMFF (`video/mp4`, `audio/mp4`, `application/mp4`) on the AdaptationSet axis (DR-1, RFC 4337); image and HTML are not carriable on that axis | **gap** for image / HTML — DR-6 carriers required; **full** for video (DR-1 already requires `video/mp4`) |

## 3. Gaps Detail

### A. Structural: DASH 6th defines no non-linear ad construct

NotebookLM, queried against ISO/IEC 23009-1:2025, confirms:

> "In the MPEG-DASH 6th edition, non-linear ad mechanisms — such as
> overlays, side-by-side videos, pause-ads, banners, or L-shapes
> where the primary content keeps playing while an ad is composited
> on top — are explicitly not defined."

§5.16 (`InsertPresentation` / `ReplacePresentation`) is **strictly
linear**: §5.16.1 frames an alternative Media Presentation as one
that "replaces the main Media Presentation at a certain point on the
media timeline for a duration of time". §5.16.3 mandates that the
Insert event "stops the playback of the current Media Presentation
till the end of the Alternative Media Presentation". §5.16.4 mandates
that the Replace event "stops the playback of the current (main)
Media Presentation till the end of the Alternative Media
Presentation" (the main playhead continues advancing under the
cover, but the main is not rendered).

Two adjacent §-anchored features need to be **explicitly excluded**
in the spec text to avoid reader confusion:

- **Annex L "Implementation of Nonlinear Playback"** is a *name-only*
  collision. Annex L describes an *Interactive Storyline* branching
  narrative use case (directed acyclic graph of Periods, user
  selects the next Period). It is not a non-linear advertising
  construct. The SGAI spec MUST clarify this in chapter 2
  (Normative references) or in the introduction to chapter 5 to
  prevent misreading.
- **§5.8.5.16 Supplementary Video Services** is a codec-tight
  picture-in-picture mechanism (e.g. VVC subpictures) for tightly
  synchronised compositions of a main and a supplementary video
  into a single decoder. The spec explicitly notes that
  "composition of the main video and the supplementary video are
  out of the scope of the DASH client". §5.8.5.16 is therefore NOT
  a carrier for non-linear ads (no advertising semantics, no
  event-driven resolution, no Broadcaster-declared constraints,
  no IAB layout vocabulary). Its existence MUST be acknowledged
  and discarded as a candidate in R8 / R9 justification text.

**Implication:** the entire surface for non-linear opportunities
(UC-03 coexisting overlay, UC-04 hybrid linear + overlay, UC-05
pause-triggered ad) is a net new construct relative to DASH 6th.
The new constructs MUST live within the DR-1..DR-7 closure (§5.2.1
foreign-namespace open content under `urn:svta:dash:sgai:<year>`,
§5.10 application-level Event Streams under year-pinned scheme URIs
`urn:svta:dash:<construct>:<year>`, or vendor descriptors
§5.8.4.8 / §5.8.4.9) per R1.2.

### B. Slot-level non-linear constraints (R2.1, R4.1, R5.6)

The Broadcaster MUST declare, on a non-linear slot: **allowed
layouts** (a token list mapped 1:1 to IAB ad-type values, per R12),
**maximum overlay duration** (R4 / R13's window reference),
**maximum concurrent overlays** (R14), and — for UC-05 — the
**pause-trigger window** (`startTime`, `endTime`). None of these
attributes exist on any DASH 6th element. The carrier choice is
constrained by R1.2 to:

- A new SVTA-namespaced element under §5.2.1 attached as a child
  of the SGAI event (DR-2 / DR-3), carrying the constraints as
  attributes. This is the path consistent with
  [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)
  §"Preferred encoding patterns" (single attribute with
  space-separated tokens for `allowedLayouts`).
- §5.10 application-level Event Stream with a year-pinned
  `schemeIdUri` and the constraints encoded as the `<Event>`'s
  `text()` payload or attributes. Suitable when the constraint
  set is presentation-time-aligned and tied to a specific event
  window (UC-05 pause-trigger window is the prime fit).

R8 / R9 require the spec to pick one carrier per construct and
justify the choice inline.

### C. Multi-form, multi-layout candidate (R5.1, R5.5)

`ListMPD` §8.14 represents a *sequence of ads to play*, not a *set
of candidates to choose from*. Each `Period` resolves (via
`<ImportedMPD>` or inline) to one sub-MPD, and `<ImportedMPD>`
binding to SPS (DR-1, §5.3.2.6 → §8.15 → §7.3 → RFC 4337) closes
the ISO-BMFF assumption on the resolved AdaptationSet axis.

For non-linear ads the spec needs a construct that:

1. carries N candidates per slot (the Player picks one) — distinct
   from §8.14's "play all in order" semantics; AND
2. carries M renderable forms per candidate (video, image, HTML)
   with optional ADS-supplied priority hints — distinct from a
   single sub-MPD per Period; AND
3. is admissible under DR-6 for non-AV forms (no `@mimeType` on an
   AdaptationSet / Representation reached via `<ImportedMPD>`).

Three design directions remain in scope under DR-1..DR-7:

- **(i)** A new SVTA-namespaced resolution document (foreign-
  namespace siblings of `Period` or a new top-level element under
  `urn:svta:dash:sgai:<year>`), carrying candidate / form metadata
  as attributes and asset URLs as `text()` or attribute values.
  The Player resolves the slot's `@url` (provided by the new SGAI
  event in the main MPD) and parses this document as a non-linear
  analogue of `ListMPD`. Open content under §5.2.1 makes this
  DASH-conformant without a new profile URI.
- **(ii)** Reuse `ListMPD` as the response container but layer the
  multi-form / multi-candidate semantics on top via foreign-
  namespace children of `Period` and `<ImportedMPD>` (DR-2). For
  AV-form candidates the sub-MPD path remains SPS-conformant; for
  non-AV forms the asset URLs live on SVTA-namespaced siblings of
  the AdaptationSet (DR-6 (a)) or on application-level Event
  Streams (DR-6 (b)). Maximises reuse per R9 but couples
  non-linear semantics to §8.14's playlist semantics.
- **(iii)** Annex F (DR-4) — defining new Interoperability Point
  URI(s) for image / HTML profiles so the AdaptationSet axis
  could carry non-AV `@mimeType` values. Heavier per DR-4
  ("requires new authoring rules, new conformance criteria");
  justified only when a construct genuinely requires DASH
  segment-delivery semantics for a non-ISO-BMFF format. Flat HTTP
  URLs to renderable assets — the SGAI use case — do not require
  Annex F. Should be rejected with an explicit R8 / R9 entry.

R8 / R9 require the spec to pick (i) or (ii) and justify.

### D. Non-AV asset URL carrier (R6.6, R15)

R15 admits exactly three carriers: video (ISO-BMFF per DR-1),
image (IAB-defined formats), HTML (`text/html`). The image and
HTML carriers fall under DR-6 because:

- DR-1 closes the SPS sub-MPD AdaptationSet to `video/mp4` /
  `audio/mp4` / `application/mp4`.
- DR-5 closes the inline `<AdaptationSet>` inside a ListMPD-level
  Period to the same RFC 4337 set.
- DR-7 closes the "empty Period with only an `<EventStream>`"
  variant for any non-zero duration.

So non-AV asset URLs MUST be carried as DR-6 (a) foreign-namespace
attributes / elements under `urn:svta:dash:sgai:<year>`, DR-6 (b)
Event payloads under a year-pinned scheme URI, or DR-6 (c) vendor
descriptors. R8 / R9 require per-construct justification of which
of (a) / (b) / (c) is chosen.

The structural prohibition itself ("non-AV `@mimeType` MUST NOT
live on an AdaptationSet reached via `<ImportedMPD>` or inline
under a ListMPD-level Period") is *enforced by the baseline* — a
non-conforming document fails the SPS / CMAF profile intersection.
The spec therefore needs to state the prohibition explicitly (so
reviewers can audit chapter 5 against it) but does not need a new
DASH 6th rule to back it up. The
[`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md)
checklist item 8 (carrier classification) is the audit hook.

### E. Application-level VAST metadata (R6.4)

DASH 6th defines no native field for `ClickThrough`,
`ClickTracking`, `AdSystem`, `AdTitle`, `Advertiser`,
`UniversalAdId`. Confirmed against §8.14 source. R6.4 admits
vendor-namespaced extension elements (DR-6 (a)); per R6.5 Players
ignore unknown namespaces (DR-3). The spec MUST commit to a
namespace policy —
[`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)
covers `urn:qualabs:sgai:<year>` for vendor-private metadata; the
SGAI spec itself does not normatively define carriers for
application-level VAST metadata, deferring that to vendor namespace
per R1 / R11.

### F. Drop-before-play semantics on a candidate sequence (R7.2, R7.3)

In DASH 6th, `ListMPD` Periods are played in document order with
no defined "skip this Period" hook. R7 mandates that the Player
MAY drop a candidate that has no renderable form (R7.2) or that
would push the cumulative slot duration past the cap (R7.3). For
linear SGAI this is harmless — every sub-MPD is by construction
SPS-conformant and ISO-BMFF, so "no renderable form" is rare in
practice (codec mismatch only). For the non-linear extension, the
candidate construct introduced under §3.C carries multiple forms,
of which the Player picks at most one — the drop semantics live
on that construct (skip a *candidate*, not a *Period*), and must
be defined inline in the non-linear chapter. No DASH 6th rule is
required to back this up; it is a semantic addition on top of the
new construct.

### G. Quartile alignment for non-linear tracking (R13.2, R13.3)

The callback event scheme `urn:mpeg:dash:event:callback:2015` is a
generic *scheduled HTTP GET* keyed by `<Event>@presentationTime`
within an `<EventStream>` `@timescale`. R13.2 mandates that
non-linear quartile beacons SHOULD be timed against the
**Broadcaster-declared overlay window** (R4 `@maxDuration` on the
slot), not against the ad's intrinsic duration. DASH 6th does not
distinguish these two timing references — the callback events fire
at `presentationTime` relative to the containing Period. The spec
MUST therefore define which Period the tracking events are scoped
to:

- If non-linear tracking lives inside the candidate's sub-MPD
  Period (mirroring linear), `presentationTime` is relative to
  the ad's own timeline → quartiles align to the ad, not to the
  overlay window. R13.2 violated.
- If non-linear tracking lives inside the Broadcaster's main MPD
  (on an SGAI-namespaced event), `presentationTime` aligns to
  the overlay window → R13.2 satisfied; ADS no longer owns the
  beacons' authoring.
- If non-linear tracking lives on a new SVTA-namespaced
  `<EventStream>` whose `presentationTime` references the slot's
  declared `maxDuration` window (a new timing semantic, attached
  to the resolution document under §3.C), the carrier is the
  baseline callback scheme but the *reference frame* is novel —
  this needs explicit text per R8 / R9.

R13.3 (stop firing on trim) is purely Player-side and does not
need a DASH 6th carrier.

### H. Pause-trigger window (UC-05)

The pause-trigger window is a (`startTime`, `endTime`,
`maxDisplayDuration`) tuple on the Broadcaster's main MPD that
gates *whether* a pause produces an ad opportunity. No DASH 6th
construct represents this. Candidate carriers under DR-1..DR-7:

- §5.10 application-level Event Stream with a year-pinned
  `schemeIdUri = urn:svta:dash:sgai-pause-trigger:<year>`,
  `<Event>@presentationTime = startTime`,
  `<Event>@duration = endTime − startTime`. The `<Event>`'s
  `text()` or a child element under `urn:svta:dash:sgai:<year>`
  carries the ADS resolution URL and the max display cap.
- A §5.2.1 foreign-namespace element under `<Period>` in the
  main MPD, carrying the window as attributes. Equivalent
  expressive power; the Event Stream form has the advantage of
  presentation-time alignment that mirrors §5.16 events.

R8 / R9 require the spec to pick one and justify.

## 4. Reuse Opportunities

Per R9 the default is to reuse existing DASH 6th machinery and
introduce new constructs only when no extension suffices. The
inventory below lists the reuse paths the spec SHOULD exercise
before considering net new constructs.

- **§5.10 Event Stream as the opportunity carrier.** The
  Broadcaster-side signal for *both* linear and non-linear
  opportunities is already an `<EventStream>` of a scheme URI
  the Player recognises. Linear SGAI uses
  `urn:mpeg:dash:event:alternativeMPD:insert:2025` and
  `urn:mpeg:dash:event:alternativeMPD:replace:2025`; the
  non-linear extension extends the pattern with year-pinned
  `urn:svta:dash:sgai-overlay:<year>`,
  `urn:svta:dash:sgai-pause-trigger:<year>`, and (if needed)
  `urn:svta:dash:sgai-hybrid:<year>` schemes. Reuses §5.10
  machinery wholesale; satisfies R1 backward compatibility
  unmodified (DR-2 / DR-3).
- **§5.16-shaped three-actor decomposition.** Broadcaster
  declares opportunity in main MPD → Player resolves `@url` at
  the Earliest Resolution Time → ADS returns resolution
  document → Player validates and renders. The non-linear
  extension reuses the same flow; only the event's child
  element and the resolution document's shape differ. R2 is
  satisfied by reuse, not invention.
- **`@maxDuration` semantics.** The attribute name and the
  Player-enforced cap semantics (§5.16.5) reuse cleanly for the
  overlay window in non-linear slots —
  [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)
  §"Naming consistency with baseline DASH" mandates the reuse
  precisely because the semantics match (Broadcaster-declared
  upper bound on slot duration, Player-enforced at the
  boundary). However, the `@earliestResolutionTimeOffset` unit
  collision (seconds on `<ImportedMPD>` §5.3.2.6.1 vs
  `EventStream@timescale` units on `<Event>`) is a worked
  example in the same chapter — non-linear attributes that mean
  a different thing in a different unit MUST be renamed.
- **`urn:mpeg:dash:event:callback:2015` for tracking (R13).**
  No new tracking scheme is admissible (R13.4). The non-linear
  spec embeds tracking `<Event>` entries inside `<EventStream>`
  of the baseline callback scheme exactly as linear SGAI does.
  The non-trivial point is *where* the `<EventStream>` lives —
  see §3.G.
- **`ListMPD` profile (§8.14) as a basis for the non-linear
  resolution document.** Option (ii) in §3.C reuses §8.14
  plumbing (Periods, `<ImportedMPD>` for AV-form sub-MPDs,
  `Period@duration` for slot arithmetic). The candidate / form
  semantics layer on top via foreign-namespace open content
  (§5.2.1). This is the maximum-reuse path per R9; the
  trade-off vs option (i) is whether the playlist-of-MPDs
  reading of `ListMPD` is a clean fit for a candidate-pool
  semantic (the Player picks *one*, not plays *all*).
- **§5.2.1 foreign-namespace open content for slot-level
  constraints.** `allowedLayouts`, `maxConcurrentOverlays`,
  `pauseTriggerStart` / `End` are attributes on SVTA-namespaced
  children of the SGAI event. Reuses §5.2.1 wholesale; no new
  profile URI required (DR-2). Encoding follows
  [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)
  §"Preferred encoding patterns" — single attribute,
  space-separated tokens.
- **§I.4 `UrlParamInfo` descriptor for ADS request
  parameterisation.** Reused as-is for non-linear ADS calls
  [inferred] — `@includeInRequests="altmpd"` appears general
  enough to cover both linear and non-linear ADS resolutions,
  pending the spec's confirmation that the descriptor's
  vocabulary substitution semantics apply to non-linear
  resolution URLs.

## 5. Open Questions

These items require either WG input or a deliberate R8 / R9
decision in the spec before chapter 5 (Syntax) can be authored.

- **Q1.** Is the non-linear resolution document a `ListMPD`
  variant (extending §8.14 with foreign-namespace candidate /
  form metadata, option (ii) in §3.C) or a new top-level XML
  document type under `urn:svta:dash:sgai:<year>` (option (i))?
  Trade-off: §8.14 reuse maximises R9 compliance, at the cost
  of semantic stretching (`ListMPD` is a *playlist*, not a
  *candidate pool*). A new top-level document is cleaner but
  invents more.
- **Q2.** UC-04 hybrid break: one resolution document
  containing both linear (`ListMPD`-style) and non-linear
  (candidate-pool-style) portions, or two independent ADS calls
  each typed to its portion? The use-case notes flag a related
  question (Broadcaster-level cross-portion linkage). The
  schema decision here shapes the whole UC-04 chapter.
- **Q3.** Whether the Player issues an ADS request on devices
  that will certainly skip the opportunity (e.g. D5 on UC-03 /
  UC-05). UC-03 notes call this out — privacy / bandwidth vs
  impression-accounting trade-off. Independent of carrier
  choice, but the spec must take a position to avoid
  implementer drift.
- **Q4.** Pre-roll non-linear opportunities. UC-01 currently
  declares the pre-roll slot as linear-only. The spec must
  decide whether to disallow the pre-roll-non-linear
  combination *by construct* (no SGAI overlay event admissible
  before `presentationTime > 0`) or *by Broadcaster convention*
  (the Broadcaster simply does not author one). By-construct
  is cleaner for conformance testing; by-convention is more
  permissive.
- **Q5.** Tracking `<EventStream>` placement (§3.G). Three
  candidate locations, three different timing reference
  frames. The spec MUST pick one explicitly to satisfy R13.2.
- **Q6.** Whether the ADS resolution call for a non-linear
  slot returns the *candidate pool* directly, or returns a
  *handle* (e.g. a URL) that the Player resolves a second time
  once it has picked a candidate. Two-step adds latency but
  separates the candidate-set concerns from the per-creative
  concerns. Single-step is simpler and matches linear SGAI's
  pattern.
- **Q7.** The exact VAST 4.x pin (4.0 / 4.1 / 4.2 / 4.3) for
  the illustrative VAST → resolution-document adapter. R11
  forbids citing a specific version as required, so this is
  annex-only text; the question is which 4.x version the
  examples demonstrate. Open in
  [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
  References section.
- **Q8.** Whether `<EventStream>@timescale` on the new SGAI
  overlay scheme defaults to `1000` (milliseconds, matching
  the baseline §5.16 examples in
  [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md))
  or carries no default. Defaulting to milliseconds matches
  reader expectations but adds a constraint not present in
  baseline §5.10.
- **Q9.** Image-form intrinsic duration. R4 / R13 are expressed
  in time, but a static image has no native duration. Implicit
  assumption: the Broadcaster-declared overlay `@maxDuration` is
  the *image display duration*, applied by the Player. The spec
  MUST state this explicitly — otherwise the R7.3 drop-before-
  play and R4.5 trim-during-play rules become ill-defined for
  image candidates.

## References

- [`../context/02-actors.md`](../context/02-actors.md) — three-actor
  model.
- [`../context/03-requirements.md`](../context/03-requirements.md) —
  R1..R15 and Out of Scope.
- [`../context/04-use-cases.md`](../context/04-use-cases.md) —
  UC-01..UC-07 and device classes D1..D5.
- [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
  — DASH 6th linear SGAI interfaces and reference XML.
- [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)
  — SVTA Ads WG namespace policy and naming-consistency rules.
- [`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md)
  — per-construct R1 verification checklist.
- [`../context/08-dash-extension-rules.md`](../context/08-dash-extension-rules.md)
  — DR-1..DR-7 closing the design space.
- ISO/IEC 23009-1:2025 (FDIS) — MPEG-DASH 6th edition: §5.2.1,
  §5.3.2.6, §5.8.4.8 / §5.8.4.9, §5.8.5.16, §5.10, §5.16, §7.3,
  §8.12, §8.14, §8.15, Annex F, Annex L; IETF RFC 4337. Citations
  grounded against NotebookLM notebook *Streaming Protocols —
  DASH, HLS, C2PA, DRM*.

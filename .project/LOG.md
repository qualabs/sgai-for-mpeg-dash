# Project log

## 2026-07-10 — New use cases and extensions (Nicolás): UC-11 ClickThrough (R28), UC-12 overlapping same-family windows + fallback (R20), UC-05 live variant (R25), UC-02/UC-03 playback-speed extensions (R19)

Added new use cases and extended existing ones in
`context/04-use-cases.md` to exercise requirements that had no use-case
coverage yet. Working tree only, not committed.

- **UC-11 — ClickThrough (R28)** — new. An ad's resolution document
  carries the ClickThrough URL plus its click-tracking URL(s); the
  viewer activates the click (remote select / tap) and the Player opens
  the ClickThrough and fires the click-tracking at the moment of
  activation, not by the timeline. Exercises R28.1 (APS populates both
  URLs) and R28.2 (Player reads and fires on activation). Brief contrast
  with the timeline beacons of R13 / R6 (the click has no presentation
  time). Device classes collapsed to one sentence (D1–D5 read and fire
  identically; input-driven, not decoder-driven). One-line backward-compat
  note connecting to UC-07 (a legacy Player renders the ad but the click
  is inert per R1). Per Nicolás, R23 (AdSystem/AdTitle) contrast was
  explicitly dropped — nothing to show.
- **UC-12 — Overlapping same-family windows with fallback (R20)** — new.
  Two same-family overlay windows overlap in the primary `MPD`; the
  Player serves the first and falls back to the second only when it
  cannot access the first window's resolution document (APS/event URL
  failure). Never concurrent. Exercises R20.1. One sentence on the axis
  vs R14 (R20 selects which window is served; R14 sequences the forms
  inside it). Device classes collapsed to one sentence (window selection,
  not rendering — largely device-agnostic).
- **UC-05 — live-content variant (R25)** — extension. Added a
  "Live-content variant (presentation-time freeze)" sub-scene: the
  viewer pauses inside the pause-ad window in live content; presentation
  time freezes inside the window while the live edge advances in
  wall-clock; the pause-ad stays admissible until resume; a later jump to
  the live edge is a post-resume Player action outside the window.
  Exercises R25.1. Integrated into UC-05, not a separate UC.
- **UC-02 — trick-play variant (R19)** — extension. Added a sub-scene:
  the viewer watches at 1.5x/2x when the mid-content slot triggers; the
  ad renders at the primary's speed, wall-clock on-screen time is
  `duration / playback_speed`; the cap (R4) and beacon schedule (R13)
  operate on the presentation timeline. Exercises R19.
- **UC-03 — playback-speed mirror note (R19)** — one-line note mirroring
  the UC-02 variant for overlays.
- **Indexes** — Coverage table updated with UC-11 (category "Interaction")
  and UC-12 (category "Selection") rows; Terminology table gains a
  "Click-through → UC-11" row. Existing UCs use no "Requirements
  exercised:" closing line, so none was added (pattern not invented).
- **Matrix** — `context-analysis/uc-coverage-matrix.md` is now stale and
  left for regeneration by the build step (not edited by hand).

## 2026-07-10 — Namespace correction (Nicolás): R23 metadata carrier realigned to the canonical SVTA Ads WG namespace; invented `urn:qualabs:sgai:<year>` removed

The round-2e edit had wrongly assigned the R23 generic-metadata carrier
to a Qualabs vendor namespace (`urn:qualabs:sgai:<year>`), framing it as
"not part of this spec", while keeping R28's ClickThrough carrier under
the SVTA Ads WG namespace as "the exception". This contradicted the
canonical namespace policy: every XML element the spec introduces lives
under the single SVTA Ads WG extension namespace
`urn:svta:dash:sgai:<year>` (06-naming-and-namespaces.md, corroborated by
08-dash-extension-rules.md §, 07-backward-compat-checklist.md, and every
conformance audit, which use `urn:svta:dash:sgai:2026` on every SVTA
element and never `urn:qualabs`). The Qualabs namespace is reserved for
experimental extensions that are NOT part of the spec; R23 is a numbered
requirement of the spec, so its carrier belongs to SVTA. The invented
`urn:qualabs:sgai:<year>` was replaced by the canonical SVTA namespace.
The R23-vs-R28 distinction is normative interoperability (best-effort vs
mandatory-read), not namespace: both carriers are SVTA. Working tree
only, not committed.

- **`context/06-naming-and-namespaces.md`** — "Element / attribute
  extension namespaces" section rewritten. Removed the paragraph and the
  `urn:qualabs:sgai:<year>` bullet that placed the R23 carrier in the
  Qualabs vendor namespace, and the "ClickThrough is the exception"
  paragraph. Now states that every XML element the spec introduces
  (including both the R23 metadata carrier and the R28 ClickThrough
  carrier) lives under the single SVTA Ads WG namespace, and that the
  R23/R28 difference is normative interoperability, not namespace. The
  general "Vendor extensions (Qualabs)" section (`urn:qualabs:<feature>:<year>`
  for genuine non-spec experiments) was left intact.
- **`context/03-requirements.md` R23 / R23.1** — "vendor-namespaced
  extension elements" / "does not recognise the vendor namespace"
  reworded to "extension elements in the SVTA Ads WG namespace" and the
  best-effort/ignorable property re-grounded on foreign-namespace
  handling (conformant Player MAY drop; legacy Player discards unknown
  namespace) rather than on a vendor namespace.
- **`context/05-dash-linear-interfaces.md`** — the VAST↔DASH mapping
  rows for `<AdSystem>`/`<AdTitle>`/`<Advertiser>`, `<UniversalAdId>`,
  the `<ClickThrough>` contrast line, and the UniversalAdId prose all
  changed from "vendor-namespaced" / "best-effort vendor namespace" to
  "best-effort SVTA-namespaced carrier" (R23), keeping the best-effort
  vs normative (R28) contrast intact.
- **Consistency check** — grep over `context/` confirms no remaining
  `urn:qualabs:sgai` and no remaining "vendor-namespaced" reference tied
  to R23; the only surviving `urn:qualabs:*` is the general
  `urn:qualabs:<feature>:<year>` pattern for non-spec experiments.

## 2026-07-10 — Refinement sub-round (Nicolás, round 2g): R28 shortened and made concise; long grounding kept in 05, not in the requirement; R23 no longer references R28

R28 had grown too long and verbose across the 2e / 2f rounds. Nicolás
asked to make it much shorter and more concrete. The requirement now
carries only the essential idea (a normative, mandatory carrier for the
ClickThrough URL plus its click-tracking URL(s), and that the click is
fired on user activation, not by the callback timeline) with a single
grounding anchor (§5.10.1). The long grounding detail — that the
callback fires its HTTP GET at the presentation time (§5.10.4.5.2 /
Table 47) and the `urn:mpeg:dash:nonlinearplayback:2020` precedent where
the event is anchored to the timeline while the user interaction stays
outside the trigger — now lives only in `05-dash-linear-interfaces.md`,
where the ClickThrough / callback mapping already carried it. Working
tree only, not committed.

- **`context/03-requirements.md` R28 body** — cut from ~28 lines to two
  sentences. Removed the timeline-beacon recap (impression / quartiles),
  the §5.10.4.5.2 / Table 47 citation, and the nonlinearplayback:2020
  precedent paragraph. Only §5.10.1 remains as grounding in the
  requirement. The essentials are preserved: mandatory normative carrier
  for the ClickThrough URL + click-tracking, not relegated to a
  vendor-namespaced extension, and the click-tracking fired on user
  activation rather than through the callback presentation-time trigger.
- **`context/03-requirements.md` R28.1 / R28.2** — shortened to one
  sentence each while keeping the same normative content (APS populates
  both URLs in the normative carrier; Player reads the ClickThrough and
  fires click-tracking on user activation, not via the callback trigger).
- **`context/03-requirements.md` R23** — removed the sentence in the R23
  body that distinguished R23 from R28 ("It is also distinct from R28:
  …") and the trailing R28 reference in R23.1. R23 keeps its own idea
  (generic best-effort carrier for AdSystem / AdTitle, safely ignorable)
  and its distinction from R6, but no longer references R28.
- **`context/05-dash-linear-interfaces.md`** — checked; the long
  grounding (§5.10.4.5.2 / Table 47 + nonlinearplayback:2020, with the
  timeline-anchored-event / outside-timeline-interaction split) is
  already present in the `<ClickThrough>` / `<ClickTracking>` mapping
  row. No change needed — the detail now lives here and not in the
  requirement.
- **Consistency check** — grep over `03-requirements.md` confirms R23
  no longer mentions R28, and R28 no longer asserts the click-tracking
  uses the callback event scheme.

## 2026-07-10 — Refinement sub-round (Nicolás, round 2f): R28 click-tracking corrected — it no longer reuses the DASH callback event scheme

Correction to the R28 introduced in round 2e. Verification against
DASH 6th edition (confirmed via NotebookLM with verbatim citations)
showed the callback event scheme is timeline-triggered and cannot
represent a user-triggered event such as a click: DASH events are
timeline-scheduled and the callback fires its HTTP GET at the scheduled
presentation time (ISO/IEC 23009-1 §5.10.1; §5.10.4.5.2 / Table 47).
The 2e text erroneously said the click-tracking MUST reuse the callback
event scheme of R6 / R13.4. Corrected: the timeline-scheduled ad
beacons still reuse the callback scheme (that is right), but the
ClickThrough URL and its click-tracking are now co-located in the
normative ClickThrough carrier and the Player fires the click-tracking
when the viewer activates the ClickThrough (on click), not via the
presentation-time trigger. Precedent cited: DASH's interactive
nonlinear-playback scheme (`urn:mpeg:dash:nonlinearplayback:2020`),
where the event is anchored to the timeline while the user interaction
is handled outside the timeline trigger. Working tree only, not
committed.

- **`context/03-requirements.md` R28 body** — the click-tracking
  clause was rewritten. Removed the assertion that the click-tracking
  MUST reuse the R6 beacon carrier / callback event scheme. New text:
  timeline-scheduled beacons reuse the callback scheme per R6 / R13.4;
  a ClickThrough activation has no presentation time and DASH defines
  no user-triggered event (§5.10.1; §5.10.4.5.2 / Table 47), so the
  resolution document MUST carry the ClickThrough URL together with its
  click-tracking URL(s) in the normative carrier and a conformant
  Player MUST fire the click-tracking on user activation, not via the
  callback presentation-time trigger; nonlinearplayback:2020 cited as
  precedent for the timeline-anchored-event / outside-timeline-
  interaction split.
- **`context/03-requirements.md` R28.1 / R28.2** — R28.1 (APS) now
  requires populating BOTH the ClickThrough URL AND its click-tracking
  URL(s) in the normative carrier. R28.2 (Player) now requires reading
  the ClickThrough URL from the normative carrier AND firing its
  click-tracking on user click, NOT via the presentation-time trigger
  of the callback event scheme. The prior "read the ClickThrough and
  fire click-tracking via the R6 callback carrier" wording was removed.
- **`context/03-requirements.md` R6 note** — the line stating that the
  R28 click-tracking reuses R6's beacon carrier was corrected: the
  timeline-scheduled beacons reuse the callback carrier, but the R28
  click-tracking is not timeline-scheduled, is not carried by the
  callback event scheme, and is fired on user activation. R6 / R13.4
  themselves (timeline beacons) are unchanged.
- **`context/05-dash-linear-interfaces.md` VAST↔DASH mapping** — the
  `<ClickThrough>` / `<ClickTracking>` row now states the ClickThrough
  URL and its click-tracking URL(s) are carried together in the
  normative carrier and the click-tracking fires on user click, not via
  the callback timeline. Existing grounding preserved (DASH 6th defines
  no native carrier for Click-through URLs). Added §5.10.1 and
  nonlinearplayback:2020 as backing that DASH has no user-triggered
  event.
- **`context/06-naming-and-namespaces.md`** — checked; already
  consistent (both the ClickThrough URL and its click-tracking are
  carried by the R28 normative carrier under the SVTA Ads WG namespace,
  not an EventStream callback). No change needed.
- **Consistency check** — grep over `context/` for `R28` and for
  `click` near `callback` confirms no remaining assertion that the
  click-tracking uses the callback event scheme.

## 2026-07-10 — Refinement sub-round (Nicolás, round 2e): R23 narrowed to best-effort generic metadata; new R28 elevates ClickThrough to a normative carrier; UniversalAdId declared out of DASH scope

Nicolás split the application-level metadata carrier into two distinct
requirements: a generic best-effort carrier (R23, unchanged in spirit)
and a normative, interoperable carrier specifically for ClickThrough
(new R28). The rationale: the click MUST work across every conformant
Player, so it cannot ride the ignorable vendor-namespaced carrier that
generic metadata uses. UniversalAdId is dropped from the DASH carrier
scope entirely because its tracking / reconciliation role is handled by
VAST on the ADS side. Working tree only, not committed.

- **`context/03-requirements.md` R23** — narrowed to *generic*
  application-level metadata with no native DASH carrier. Examples
  trimmed to `AdSystem`, `AdTitle`, "etc."; `ClickThrough` and
  `UniversalAdId` removed from both the R23 body and R23.1. The
  optional / best-effort / ignorable nature is now stated explicitly
  (a Player that does not recognise the vendor namespace drops the
  metadata and nothing breaks), and R23 cross-refs R28 to make the
  boundary explicit: ClickThrough is NOT covered by the best-effort
  carrier.
- **`context/03-requirements.md` R28 (new)** — added at the end of the
  Tracking sub-section (ascending numeric order after R24). The
  resolution document MUST carry the ClickThrough URL and its
  click-tracking through a normative, interoperable carrier the spec
  defines explicitly, so every conformant Player reads it the same way
  and the click works cross-Player. Contrasted explicitly with R23
  (optional / ignorable). The click-tracking MUST reuse the existing
  R6 beacon carrier (DASH callback event scheme, per R13.4); no new
  tracking scheme. Conformance criteria: R28.1 (APS MUST populate the
  normative carrier) and R28.2 (Player MUST read the ClickThrough and
  fire its click-tracking via the R6 carrier). R6's cross-ref note
  updated to mention R28 reuses its beacon carrier.
- **`context/05-dash-linear-interfaces.md` VAST↔DASH mapping** — the
  `<ClickThrough>` / `<ClickTracking>` row now reflects the R28
  normative carrier (click-tracking via the callback scheme), instead
  of "no native carrier — sidecar or vendor namespace". The
  `<AdSystem>` / `<AdTitle>` row was re-anchored on R23 directly (it
  previously said "same conclusion as `<ClickThrough>`", which no
  longer holds). The `<UniversalAdId>` row and the "lost in
  translation" bullet were reframed: no hole left behind, but the id is
  declared intentionally out of the DASH carrier scope and left on the
  VAST / ADS side (with the reason recorded — tracking handled by VAST).
- **`context/06-naming-and-namespaces.md`** — the vendor-namespace
  paragraph now distinguishes the generic best-effort carrier (R23,
  Qualabs vendor namespace) from the ClickThrough normative carrier
  (R28), which lives under the SVTA Ads WG extension namespace, not the
  vendor-private one.
- **Coherence check** — no conflict with R11 (the spec defines its OWN
  ClickThrough carrier, it does not depend on VAST; the URL originates
  in VAST but is transcribed into a DASH-native carrier, same pattern
  as R6 / R13) nor with R18 (defining the resolution-document format is
  in scope; R28 constrains the document, not the ADS / APS API
  contract). No commit.

## 2026-07-10 — Refinement sub-round (Nicolás, round 2d): side-by-side background further restricted to IMAGE ONLY (no web/HTML)

Follow-up to 2c. Nicolás tightened the constraint further: the
side-by-side / double-box background is now **image only**, dropping the
web/HTML option left in 2c. The background is a still image, never a
video and never a web/HTML surface. Working tree only, not committed.

- **`context/03-requirements.md` R26** — body carrier sentence, the
  device-budget "worked cases" paragraph, and R26.3 all changed from
  "image or web/HTML surface" to "a still **image**, never a video and
  never a web/HTML surface". Surface arithmetic updated: a video ad
  needs two decoders (primary + ad video) plus an **image** surface for
  the background; an image / HTML ad needs one decoder (primary) plus an
  image / HTML surface for the ad and an **image** surface for the
  background. The ad still admits the full R15 carrier set (video /
  image / HTML); only the background is restricted.
- **`context/04-use-cases.md`** — UC-04 layout taxonomy bullet, UC-10
  scenario intro, and the D1 / D3 device analyses updated so the
  background surface is image only (ad may still be image / HTML). UC-09
  and the D4 / D5 analyses already described an image background, so no
  change there. The UC-10 table row (background element generic, ad
  types listed) needed no change.
- **Scope check** — grep over `context/` confirms no side-by-side
  background is described as web/HTML or video anywhere. R27 (L-shape /
  squeezeback) left untouched: there the full-frame creative IS the ad
  and may still be image / video / web/HTML, since it is the ad itself,
  not a separate background fill.
- **IAB alignment** — unchanged. IAB describes the background only as
  advertiser branding of the region between the two boxes; restricting
  it to a still image is strictly more restrictive and does not
  contradict IAB. No commit.

## 2026-07-10 — Refinement sub-round (Nicolás, round 2c): R26.3 decoder arithmetic fixed; side-by-side background restricted to image/HTML (never video), IAB-checked

Two fixes to the side-by-side / double-box device budget in
`context/03-requirements.md` R26, propagated to the use-cases. Working
tree only, not committed.

- **Arithmetic error fixed.** The prior R26 text claimed a side-by-side
  whose ad and/or background is video "requires two decoders". With
  three video elements (primary content + video ad + video background)
  that is three concurrent decoders, not two. The error is now moot
  because of the restriction below, but it drove the rewrite.
- **IAB check on the background type.** Re-read IAB Tech Lab, "Ad Format
  Guidelines for Digital Video and CTV" (public comment, Dec 2025),
  Squeezeback section, p.12. The "Double Box Video + Background" entry
  describes the background only as: *"The advertiser also brands/takes
  over the background between the double boxes of video."* IAB does not
  state or require the background to be a video element; it is described
  as advertiser branding of the region between the two video boxes. IAB
  is effectively silent on the background being a decoder-bearing video.
- **Decision (simplification, Nicolás's preferred path).** The
  side-by-side background element is now **always an image or a web/HTML
  surface, never a video**. It never consumes a video decoder. The
  decoder budget is therefore at most **two** concurrent video decoders:
  the primary content plus a video ad. The three-video / three-decoder
  case is removed entirely. This does not contradict IAB (IAB does not
  require a video background) and matches the "Background = branding
  surface" reading.
- **Applied.** `context/03-requirements.md`: R26 body carrier sentence
  (background = image or web/HTML, never video), the device-budget
  "worked cases" paragraph (two cases now: video ad → two decoders +
  image/HTML surface; image/HTML ad → one decoder + surfaces), and R26.3
  conformance criterion (same two-branch arithmetic; the two-video-max
  bound made explicit). `context/04-use-cases.md`: UC-04 layout taxonomy
  bullet and UC-10 scenario intro updated to list the background as
  image/web-HTML only (never video). UC-09 already used the correct
  two-decoder arithmetic (its background is an image), so no change there.
- **R27 unchanged.** The L-shape / squeezeback ad creative (which IS the
  full-frame background) may still be image, video, or web/HTML per R27,
  since there the creative is the ad itself, not a separate branding
  fill. No commit.

## 2026-07-10 — Refinement sub-round (Nicolás, round 2b): publisher fallback background removed entirely; background is advertiser-only, black if none

Follow-up to the sub-round below. Nicolás simplified further: the
uncovered-region background is **only** the advertiser's creative (IAB
"Double Box Video + Background"). There is **no** publisher / platform
fallback. If the advertiser supplies no background, the uncovered bands
render as **black**. All mention of a publisher-declared fallback
background was removed across `context/`. Applied to the working tree
(not committed).

- **`context/02-actors.md`** — removed the Publisher bullet about
  optionally declaring a fallback background. The Publisher no longer
  declares anything about the side-by-side background; the background is
  the advertiser's. The Publisher bullet list now runs layout templates
  → other slot-level constraints.
- **`context/03-requirements.md` R26** — advertiser-default paragraph
  rewritten: the background element, when present, is the advertiser's
  creative; it is owned by the advertiser, not the Publisher or the
  platform; when the advertiser supplies none, the uncovered region
  renders as black. Deleted the "specification MAY define a platform /
  publisher fallback background" sentences. R26.2 rewritten to two
  branches only: advertiser supplies a background (Player places it) or
  advertiser supplies none (black). R26 stays MAY (the advertiser may or
  may not bring a background).
- **`context/04-use-cases.md` UC-10** — removed the publisher-fallback
  mentions in the scenario intro, Publisher intent, Ad response ("No
  advertiser background → black", no fallback), and D1 "what the user
  sees" (advertiser's background image only). Also swept the two
  residual negative-framing sentences ("the L-box is a different layout,
  not an R26 case") in the scenario intro and closing Note, leaving R27
  to define the L-box positively.
- **Verification** — grep over `context/` confirms no remaining
  publisher / platform fallback-background mention and no "not a(n) R26
  case" negative framing. Remaining "fallback" hits are unrelated
  (legacy standard-break fallback, R20 first-window-wins fallback
  chain). IAB alignment unchanged (advertiser owns the background per
  the Dec 2025 guidelines, verified prior). No commit.

## 2026-07-10 — Refinement sub-round (Nicolás, round 2): R26 background simplified to advertiser-default / publisher-fallback-MAY, IAB-aligned; negative "not R26" framing dropped

Nicolás's refinement feedback on the uncovered-region background model,
applied to the working tree (not committed). Four points, all reconciled
against the authoritative IAB source.

- **IAB verification (the crux).** Confirmed against IAB Tech Lab, *"Ad
  Format Guidelines for Digital Video and CTV"* (public comment, Dec 2025),
  Squeezeback section, p.12. IAB text, verbatim: *"Double Box Video +
  Background: Each box (content and the ad) will take up 25% of the 1920 x
  1080 screen. The content squeezes back to the center left, and the ad
  squeezes to the center right. The advertiser also brands/takes over the
  background between the double boxes of video."* Also, Squeezeback creative
  note: *"the squeezeback assets are provided in an underlay format... the
  full screen 1920 x 1080 branded advertisement is provided with a cutout
  for the content placement."* Conclusion: in IAB the background is the
  **advertiser's** creative, not the publisher's. IAB is silent on any
  fallback when the advertiser supplies none.
- **R26 → MAY (Punto 2).** `context/03-requirements.md` R26 title and body
  changed from "layouts carry a background element" to "**MAY** carry a
  background element". The background is optional: when none is present the
  uncovered bands render as black. R26.2 rewritten so the Player MUST
  composite primary content + ad, and MUST place a background element only
  when one is present (advertiser default, publisher fallback when the
  advertiser supplies none), black otherwise.
- **Advertiser default, publisher fallback opt-in (Punto 4).** The
  advertiser-default paragraph (mirroring IAB "Double Box Video +
  Background") is retained as the normative default; the platform /
  publisher fallback stays an opt-in MAY that applies only when the
  advertiser supplies no background. This was already largely present in the
  working tree; verified against IAB and kept.
- **Dropped the negative "not R26" framing (Punto 3).** Removed the R26
  paragraph that defined the L-shape by what it is NOT ("a different layout,
  not a case of R26..."). R27 already defines the L-shape / squeezeback
  positively (one full-frame ad creative in the background + shrunk primary
  content on top, no separate third fill element); added a one-line anchor
  to the IAB underlay model. R27's closing contrast sentence against R26 was
  removed in favour of the positive definition.
- **02-actors.md (Punto 1).** The Publisher bullet was simplified: dropped
  the long parenthetical and the L-shape negative clause. It now states the
  Publisher optionally declares a platform / publisher fallback background
  for the side-by-side, with the default background being the advertiser's
  own creative (IAB model), fallback used only when the advertiser supplies
  none so the region does not render black.
- **Consistency.** `context/04-use-cases.md` UC-10 already frames the
  background as advertiser-supplied with an optional publisher fallback
  (R26.2), consistent with the MAY model; no contradiction introduced, left
  as-is per "adjust the minimum necessary". No commit (Nicolás refining).

## 2026-05-29 — WG feedback round 2 (David Hassoun, Slack thread #wg-comcast): L-box modelled as its own layout (R27, not R26) + UC-07 content-dependent fallback + R21 relaxed

A second round of David Hassoun's feedback arrived as a **Slack thread**
(`#wg-comcast`, 2026-05-29), distinct from the file-based round 1 cross-referenced
on 2026-05-27. Three `context/` changes applied + one point closed; A4 still
pending. Changes applied to the working tree for Nicolás to validate before commit.

- **L-box model (U2 / U4).** David objected to an earlier model that
  treated the L-box as a full-frame ad with a cutout and **no background**: *"I'm
  not sure I totally agree with the L-Box. Yes it can be done with a cutout image
  (with transparency), but it could also be a background image - no transparency.
  It could reasonably be bg image, content on top, ad video or static on side and
  or bottom."* **Nicolás closed the debate:** *"Lets agree on this: Lbox is ALWAYS
  a background image/video/web"* + *"so lets not call it background image, is just
  'the image/web/video for the LBOX'"* (David reacted 👍). The agreed model: the
  L-box (L-shape / squeezeback) is a layout with **one** ad creative — an image,
  video, or web/HTML, a single URL the ADS supplies — that is **always** placed
  **full-frame in the background**, with the shrunk primary content composited on
  top of it. Two on-screen elements (the full-frame ad creative + the shrunk
  primary content); the "L" is the band of the ad creative that stays visible
  around the shrunk content. There is **no separate third filler element** — the
  ad creative is itself the background. The L-box is therefore **its own layout,
  NOT a case of R26**: R26 is specifically the side-by-side / double-box, where
  two boxes leave an uncovered region that a distinct third background element
  fills. The L-box has no such uncovered region. Applied:
  - `context/03-requirements.md` **R26** scoped back to **side-by-side /
    double-box only** — the three-element case (primary content + ad + a third
    background element of variable media filling the uncovered bands). R26.1/.2/.3
    describe the side-by-side. The L-box is **not** an R26 case.
  - `context/03-requirements.md` **new R27** — L-shape / squeezeback as its own
    layout: one full-frame ad creative (image/video/web) + the shrunk primary
    content on top, a presentation option under R5. R27.1/.2/.3 cover the
    two-element composition and the decoder budget (video creative → 2 decoders;
    image/HTML creative → 1 decoder + a surface). Next free number, no
    renumbering of existing requirements.
  - `context/04-use-cases.md` — UC-03 layout taxonomy, UC-04 D3/D4, UC-09 (option
    2 + D2/D3/D4/D5 analysis + "what this demonstrates"), UC-10 (scenario intro +
    final Note: the L-box is a different layout, not the "other R26 case"), and the
    coverage table reconciled to the two-element L-shape model under R27.
  - `context/02-actors.md` — the Publisher sub-bullet now scopes the background
    element to the side-by-side (R26) and notes the L-shape's full-frame ad
    creative is its own background (R27).
  - **UC-09 option 2 modeling:** an **L-shape with an image full-frame ad
    creative** (one decoder for the shrunk primary content + an image surface for
    the full-frame background creative), which preserves the worked-example
    per-class outcomes (D1 → side-by-side, D3 / D4 → L-shape, D2 / D5 → takeover).
    A video full-frame creative would push D3 / D4 off the L-shape.

- **UC-07 content-dependent legacy fallback (U5).** David: *"It should skip OR use
  standard break depending on content options. If live and real content then skip
  otherwise use will lose content."* UC-07 now documents the legacy-player
  fallback as **content-dependent**: the legacy Player always skips the unknown
  SGAI construct (R1), but what the Publisher authors around it differs — for
  **live** content, skip-and-continue (cannot pause live to splice without losing
  real content); for **non-live / VOD**, the Publisher MAY / SHOULD author a
  **standard linear break** using baseline constructs a legacy Player renders, so
  the legacy Player plays the standard break instead of losing the opportunity.
  Applied to `context/04-use-cases.md` UC-07 (Player decision + What the user sees
  + Notes) and `context/07-backward-compat-checklist.md` §5 (the UC-07 test now
  asserts only the silent skip of the new construct; the surrounding viewer
  experience is the Publisher's content-dependent authoring choice). RFC 2119
  MUST / SHOULD / MAY used.

- **R21 pause-ad partial overlay (U6).** David: *"i think thats an oversight in
  spec... I have seen partial screen pause ad overlays."* R21 relaxed from
  "Pause-ad forms are fullscreen" (MUST fullscreen, partial not supported) to
  **"Pause-ad forms MAY be fullscreen or a partial overlay"**. R21.1 rewritten to
  permit both surfaces; the R17 priority (pause-ad suspends a coexisting overlay)
  and the R22 single-active-form bound were made the load-bearing guarantee
  instead of the old "fullscreen necessarily covers the overlay" reasoning. R16
  and R17 cross-refs to R21 updated to drop the fullscreen assumption; UC-08
  scenario intro + D1 "What the user sees" note that the pause-ad may be
  fullscreen or partial. No renumbering.

- **UC-02 vs UC-06 closed (U1).** David reacted "sounds good" to keeping the two
  use cases separate; the round-1 conflict is resolved in favour of the v1
  decision (keep them discrete for the test-generation workflow). No spec change.

- **A4 still pending.** David did not confirm the ADS + APS split in this thread;
  the lightweight confirmation remains outstanding.

These are `context/` changes → next major build is **v6** (the orchestrator
regenerates the spec + analyses when the operator runs `build-all`). **NOT yet
committed** — pending Nicolás's diff review (especially the UC-09 option-2
modeling decision above). Phase governance updated in
`.project/phases/02-wg-feedback-round-1/TASKS.md` (round-2 note).

## 2026-05-27 — use cases: UC-09 (ordered fallback across device classes) + UC-10 (side-by-side three-element R26)

Added two use cases to `context/04-use-cases.md` to make the expected
behaviour explicit for the WG, built on the corrected positional-ordering
(R5/R5.x) + R26 side-by-side model confirmed earlier today.

- **UC-09 — One ad, ordered presentation options, resolved across device
  classes.** A worked example: ONE candidate offering four ordered
  presentation options (document order = preference per R5) — (1) side-by-side
  with a video ad + advertiser background (R26, three elements: two decoders +
  image surface), (2) L-shape / squeezeback with a full-frame image ad (one
  decoder + image surface, ad covers the screen, no background — a layout, not
  R26), (3) image banner overlay, (4) full-screen takeover video as last
  resort. The same ordered list is emitted identically to every viewer and the
  Publisher declares ONE device-agnostic allowed-layout set; the per-class
  layout emerges Player-side (R5.2/R5.6/R5.7). Per-class outcomes: D1 → option 1
  (side-by-side); D2 → option 4 (takeover — owns two decoders but the
  background/image surfaces are non-video, R26.3); D3 → option 2 (L-shape image
  ad); D4 → option 2 (L-shape image ad); D5 → option 4 (takeover — no overlay
  surface). Directly answers Hassoun A3 ("shouldn't the Publisher declare
  layouts per device class?") by showing the ordered fallback already produces
  the correct per-class layout with no device-class matrix held upstream (R5.4).

- **UC-10 — Side-by-side / double-box (three-element layout, R26
  illustration).** The worked illustration of R26 itself: primary content + ad
  + background as three on-screen elements, the advertiser-supplied background
  (R26 default) and the no-advertiser-background fallback (platform MAY,
  R26.2), and the device-class reasoning (video ad → two decoders + image
  surface; image/HTML ad → one decoder + image/HTML surfaces; the background is
  a composition attribute of the layout per R26.1, not a presentation option).
  D2 declines the side-by-side even with two decoders because the background
  image is a non-video surface (R26.3) — the element-type distinction.

Coverage table updated with rows for UC-09 and UC-10. This is a `context/`
change → next major build is **v6** (implied; `build-all` regenerates the spec
and analyses when the operator runs it). Validated by Nicolás and **committed
+ pushed** to `main` (2026-05-27). Addresses Hassoun A3 + U2 /
U4 by illustrating the per-device-class layout outcome and the L-shape vs
side-by-side distinction concretely.

## 2026-05-27 — decisions: positional ordered fallback (normative) + advertiser-owned background fill (Option A)

Two design decisions confirmed by Nicolás. Both are recorded here as a
decision trace. The `context/` implementation has now been **applied** to the
normative spec (R5 + R5.1/R5.2/R5.5/R5.6/R5.7, new R26 + R26.1-3, UC-01..05
vocabulary alignment, UC-04 D2/D3 + UC-03 L-box rewrites, the `02-actors.md`
APS/Publisher edits, and the `99-glossary.md` ListMPD line + new "Presentation
option" entry) following Nicolás's wording review (R5.5 trimmed; R26 in
English; R26 placed in the Presentation section; platform fallback kept as an
opt-in MAY with no normative default). R14 was deliberately left unchanged
(intra-slot sequence axis, distinct from R5's ordered fallback). The changes
were validated by Nicolás and **committed + pushed** to `main` (2026-05-27).

**Decision 1 — Ordered fallback is normative and positional.** The
presentation options an ad offers (a form plus its layout) are modelled as an
**ordered list in the resolution document, where document order IS the
preference order** — there is no separate priority / ranking attribute. The
Player evaluates the options in document order, intersects each with device
capability and the Publisher's allowed layouts (per R5.6), and renders the
**first option that passes** (R5.7 still governs skipping to the next
candidate when nothing renders). This makes the ordered-fallback behaviour a
normative MUST rather than emergent behaviour driven by optional hints.

Rationale: today the spec models preference as OPTIONAL "ADS-supplied priority
hints" ("optionally ranked", R5.1 / R5.2 / R5.5) and R5.6 treats allowed
layouts as a SET to intersect. Nicolás's decision (verbatim, translated):
*"make the order NOT optional. The order the Player follows is the order of
appearance in the ad resolution document. It is not an attribute or anything —
it is the specific order of the options."* This also resolves the
two-dimensions subtlety in R5.5 (form AND layout "ranked independently"): a
single linear order cannot rank two independent axes, so the model becomes a
single ordered list of discrete **(form + layout) presentation options**. The
"priority hints" / "optionally ranked" / independent-ranking language is
retired in favour of positional order. UC-03 / UC-04 wording aligns
("priority order" → "document order").

**Decision 2 — Background fill is the advertiser's (Option A), mirroring
IAB.** When a non-linear ad layout leaves empty screen area (L-shape /
squeezeback, side-by-side, banner with margins), the background fill is part
of the **advertiser's creative**, NOT neutral publisher filler. This mirrors
the IAB model normatively because our spec delegates the layout vocabulary to
IAB (R10, R12, OOS-1). A new requirement is proposed: for any layout whose
on-device composition leaves regions with no content, a **background image MAY
be defined**; by default it is part of the advertiser's creative (the IAB
underlay model), and the spec MAY specify a platform / publisher fallback only
for the case where the advertiser supplies none. The background is modelled as
an attribute of the slot / layout composition, NOT as one of the alternative
forms. A full-frame HTML form composes its own background and needs no
separate fill.

IAB evidence (the layout vocabulary this spec defers to, cited so the trace is
auditable):
- Document: **IAB Tech Lab — "Ad Format Guidelines for Digital Video and
  CTV"**, version released for public comment Dec 2025. The public-comment
  period closed 2026-01-31; a signaling addendum remains in public comment
  until 2026-06-05.
- URLs:
  - https://iabtechlab.com/standards/ctv-ad-portfolio/
  - https://iabtechlab.com/wp-content/uploads/2025/12/TV-Ad-Format-Guidelines-For-Public-Comment-Dec-2025.pdf
- Quote (p.12, squeezeback): *"the squeezeback assets are provided in an
  underlay format. This means that the full screen 1920 x 1080 branded
  advertisement is provided with a cutout for the content placement."*
- Quote (pp.12-13, "Double Box Video + Background"): *"The advertiser also
  brands/takes over the background between the double boxes of video."*
- Model: the creative is a full-frame (1920x1080) underlay with a cutout where
  the content is composited. Full-frame composition is the creative's
  responsibility, not the player's. IAB defines no notion of neutral publisher
  filler.
- Honest gap: the base variant (no "+ Background") does NOT specify who fills
  the gap when the advertiser does not brand it — IAB is silent there. So our
  spec MAY define a platform / publisher fallback for the "no advertiser
  background" case WITHOUT contradicting IAB.

Open for owner review (carried into the proposal): whether retiring the
"priority hints" language loses any intended capability (the form/layout
independence it allowed); the exact number / placement of the new background
requirement (proposed near R3 / R17 in Presentation, or near R5 in Selection);
and any cross-ref that goes stale (R7, R14, R20 reference "order" / "priority
hints"; R5.5 / R5.6 are the most affected). The 🔧 background-image-below-video
L-box and the UC-04 D2 "CONFUSING" items in phase `02-wg-feedback-round-1`
(see `phases/02-wg-feedback-round-1/hassoun-feedback-crossref.md`, U2 / U3 /
U4) are addressed by Decision 2 and the UC-04 wording fixes in the same
proposal.

## 2026-05-27 — phase opened: 02-wg-feedback-round-1

Opened phase `02-wg-feedback-round-1` to formally process working-group
feedback round 1 on the SGAI spec, starting with David Hassoun's review.
David returned 3 `context/` files (`02-actors.md`, `04-use-cases.md`,
`03-requirements.md`) marked with inline `//ISSUE` / `//` comments during
the 2026-05-20 Comcast WG session — 10 feedback pieces total (plus 2 text
renames in `02-actors`).

The phase's primary work product is the cross-reference report
(`phases/02-wg-feedback-round-1/hassoun-feedback-crossref.md`, English),
which maps David's feedback — captured against the spec state he received
(commit `c983ff7`, three-actor model) — against the current spec state
(post `fb30314`, four-actor Publisher / ADS / APS / Player). Classification:
4 ✅ already addressed, 3 🔧 change-needed (background-image-below-video
L-box, UC-08 partial pause-ad overlay, UC-04 D2 wording), 3 ❓ open for
discussion (UC-07 legacy-player fallback objection, UC-02 vs UC-06 conflict,
layout-per-device-class).

T-01 (the cross-reference) is `done`; T-02..T-08 (the 3 ❓ decisions, the
3 🔧 edits, and the 1 ✅ follow-up with David) are `pending` and require
Nicolas's input. No change was applied to `context/` — this phase holds the
analysis and audit trail; spec edits land as separate iterations.

Scope: round 1 = David Hassoun only. Other reviewers / future passes become
follow-on phases.

## 2026-05-26 — decision: defer spatial caps to IAB CTV per @layout token

ADR 0001 closes the spatial-caps question raised by issue #4
(emilsas): rather than introduce a new MPD-side dimensional
attribute, the spec defers broadcaster-declared spatial
constraints to the per-layout caps already defined by the IAB
CTV Ad Format Guidelines, inherited by normative reference via
the `@layout` token. `R12.4` lifts this into a normative
requirement in `context/03-requirements.md`. This avoids a new
MPD construct (per R9.2 / R9.3 / R10) and keeps the layout
system anchored on the external IAB spec instead of redefining
caps locally. Captured as ADR
`.project/decisions/0001-defer-to-iab-ctv-for-spatial-caps.md`
and shipped in PR #6 (resolves issue #4). The
"alignment with IAB CTV Ad Standard" open thread in
`PROJECT.md` is closed by this decision.

## 2026-05-16 — refactor: separate ADS responsibility from R18 (API scope)

The bullet about the ADS URL in context/02-actors.md was mixing
two distinct concerns:

- Behavioural responsibility (what the ADS, Broadcaster, and
  Player do at runtime around the URL).
- Spec-scope decision (which parts of the ADS API the
  specification documents and which it leaves opaque).

The responsibility part stays in actors as a shorter bullet
("ADS endpoint as a URL"), and the spec-scope part moves to
context/03-requirements.md as a new R18 "ADS API contract is
not defined by this spec". R18 uses explicit "does NOT define"
wording because it is a scope statement, not an actor obligation
— DP-2 (positive obligations) governs obligations to actors, not
decisions of what the spec itself documents.

R18.1 and R18.2 are positive: they describe what the spec
documents (the Player-visible interface) and who maintains the
bilateral contract outside the spec (the Broadcaster and the ADS
directly).

## 2026-05-16 — R17 pause-ad priority + UC-08 scenario refinement

Nicolas approved the proposed pause-ad priority rule:

- R17 added: pause-ad always renders on top of the overlay during
  the pause window. Not Broadcaster-configurable. Player suspends
  overlay rendering during pause, restores it on resume if the
  overlay slot window is still active, and lets the overlay
  terminate naturally when its declared window expires per R4.
  All R17 conformance criteria are written in positive obligation
  style per DP-2.
- UC-08 scenario and per-device behaviour rewritten to align with
  R17 — the overlay continues after resume until its window
  expires, not because the pause-ad ended.

## 2026-05-15 — UC-03/UC-05 restructure: UC-08 nuevo para overlap

Removed the wrongly-placed `#### UC-03.x — Viewer pauses during
overlay` subsection from inside UC-03 (it mixed heading levels —
`####` was already used for device classes — and contained
out-of-scope notes/open questions).

The pause-during-overlay scenario is now formalised as UC-08, a
top-level Use Case dedicated to the overlap between UC-03
(coexisting overlay, no pause involved) and UC-05 (pause-ad
window). UC-08 follows the canonical UC template: Scenario,
Broadcaster intent, ADS response, Per-device behaviour D1..D5.

Coverage table updated with a new row for UC-08.

This keeps UC-03 strictly about overlays without pause involvement,
UC-05 strictly about pause-ads without overlay context, and UC-08
about the composition rule that R14 + R16 enforce when both
opportunities apply at the same instant.

## 2026-05-15 — feedback round: 5 edits to context + build prompt

Five changes from a single feedback round, all touching context/
and the spec build prompt (no output regenerated yet):

1. `context/06-naming-and-namespaces.md` — "Naming consistency
   with baseline DASH" collapsed from two directional rules + two
   worked cases into a single rule: if a component is in essence
   the same as one already in MPEG-DASH 6th edition, reuse the
   baseline construct with all its characteristics (name, default
   values, permitted value domain, units, semantics).
2. `context/02-actors.md` — added "ADS URL is opaque to the spec"
   responsibility on the ADS: the URL syntax, parameter names,
   and ADS-side API contract are not defined here; the Broadcaster
   may encode slot constraints as query parameters, but
   `@maxDuration` on the MPD event remains the Player's
   enforcement target.
3. `context/05-dash-linear-interfaces.md` — added "Resolution
   document timing baseline" subsection making explicit that all
   `<Event @presentationTime>` values in the ADS resolution
   document are relative to slot start, not to wall-clock or to
   the primary content timeline.
4. `context/03-requirements.md` — new R16 "Pause-ad lifecycle
   bound to pause state" (R16.1 dismissal within one rendering
   frame on resume; R16.2 cessation of beacon firing after
   dismissal); and new DP-2 "Obligations are positive" (state the
   positive obligation, do not enumerate prohibitions).
5. `context/04-use-cases.md` — extended UC-03 with a sub-scenario
   "viewer pauses during overlay": overlay suppresses, pause-ad
   fires per UC-05, resume dismisses pause-ad and restores the
   overlay; slot window clock follows the primary content
   timeline.
6. `prompts/build-spec.prompt` — added a style rule mirroring
   DP-2: the spec generated by this prompt MUST state positive
   obligations only; existing "MUST NOT" / "forbidden" lists in
   prior chapters are refactored into positive statements on the
   next build.

The current spec output (v4.2) is unchanged; the next major build
(v5) will pick up these context changes.

## 2026-05-14 — actors layering fix: no forward-references to requirements

`context/02-actors.md` had 2 forward-references to
`context/03-requirements.md` (one in the file's preamble, one in
the new "Tracking schedule authority" bullet for the ADS). Per
the layering principle that requirements ground on actors (R2
anchors on the three-actor model — the dependency arrow points
from requirements to actors, not the reverse), actors must be
self-contained.

Both references were reformulated to express the same content
without naming R-N identifiers or linking to the requirements
file. The substantive content (the ADS's tracking-schedule
authority, the preamble's contextual framing) is preserved.

## 2026-05-11 — Initial iteration of spec and repo

Set up the repo scaffold, drafted the initial spec, and prepared
the build pipeline. Subsequent iterations of the spec / analysis /
norm output will append entries here as work progresses.

## 2026-05-14 — DP-1 expand (DP-1.1 + DP-1.2) + R13 rewrite

Feedback de Nicolás:

- DP-1 needed sub-rules. Two new bullets added:
  - DP-1.1 "No future-flexibility placeholders" — closes the bug
    that introduced @maxConcurrent in v4 with a fixed value of 1.
  - DP-1.2 "Single source of truth" — closes the bug of duration
    being declared in svta:RenderableAsset@duration AND in the
    last Event's @presentationTime.
- R13 rewritten — moved from "spec prescribes quartiles" to
  "ADS supplies the tracking schedule, Player executes". Removes
  the hardcoded 25/50/75/100, makes the ADS the authority over
  beacon timing, keeps the DASH baseline callback mechanism as
  the carrier.

## 2026-05-14 — R13.5 removed, ADS tracking authority moved to actors

After back-and-forth feedback on whether R13.5 (the prohibition on
hardcoded tracking fractions) should remain as a specific
requirement or be generalised:

- **R13.5 removed** from context/03-requirements.md. The specific
  prohibition was too narrow for the requirements layer.
- **The generalisation lives in context/02-actors.md** instead, as
  a new responsibility bullet for the ADS: "Tracking schedule
  authority". The actor model already separates mechanism from
  policy by design — codifying that the ADS owns the tracking
  schedule there is the right home, not as a forbidden-fraction
  rule in R13.
- DP-2 ("Mechanism over policy") proposed earlier in the
  conversation is NOT introduced — actors already covers it.

R13 itself remains as rewritten in fda6b5f (ADS-directed
callbacks; no hardcoded quartiles in the spec text). Only R13.5
is removed.

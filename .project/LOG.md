# Project log

## 2026-07-13 — phase closed: 02-wg-feedback-round-1

Closed the working-group feedback round-1 phase. All of David Hassoun's
10 feedback items (round 1 file-based review 2026-05-20 + round-2 Slack
thread 2026-05-29) are resolved and incorporated into `context/`. The
last open task, **T-08** (confirm the ADS+APS split matches David's
ADS→APS rename intent), is marked `done`: the four-actor split
(Publisher / ADS / APS / Player) is in the committed spec
(`context/02-actors.md`, R2/R2.2), and the explicit confirmation with
David is treated as an external, non-blocking follow-up (to raise in the
next `#wg-comcast` exchange), not a phase blocker.

Closure report written to
`phases/02-wg-feedback-round-1/REPORT.md`. PHASE.md set to `closed`
(`closed: 2026-07-13`). PROJECT.md phase pointer and `last_update`
updated; no phase is currently active.

Context for the close: a later spec-refinement iteration (commit
`97e6f71`, 2026-07-13) landed changes that are this project's own scope,
distinct from David's review — R28 (ClickThrough carrier as a normative
requirement), R23 narrowed to a generic best-effort carrier, R26 scoped
to image-only fill, new use-cases UC-11 (R28) / UC-12 (R20), SVTA
namespace alignment, and the `CLAUDE.md` rule that requirements must be
self-contained and concise. Recorded here as part of everything worked
up to the close; not attributed to tasks T-01..T-07.

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

## 2026-07-13 — Phases 03-custom-layout and 04-multiview opened (planning, scaffold only)

Two new phases opened in `planning` to scaffold two **advanced,
optional** extensions of the spec, both driven by David Hassoun. Only
the governance scaffold was created — no `context/` edits, nothing
committed. Both phases await Nicolás's review before execution.

Transversal framing set by Nicolás and encoded in both phases: custom
layout and multiview are **opt-in advanced extensions**, not required
for core conformance; each feature's requirement(s) and use-cases must
live in their own self-contained advanced-extension section, separate
from the core. The two phases are **independent** of each other.

- **`03-custom-layout`** — a new, additional layout type (alongside
  overlay / side-by-side R26 / L-shape R27 / takeover). Reference-viewport
  pixel coordinate model (pixels over percentages, for exact placement);
  N elements with arbitrary position / size / Z-order and permitted
  overlap; one primary-content reference element. Publisher enables the
  layout, ADS/APS declares the positions (R2); degrades via R5 ordered
  fallback + R3 decoder budget. Scaffolded `PHASE.md`, `TASKS.md`,
  `T-01-PLAN.md`, and proposed ADR 0002
  (`0002-custom-layout-viewport-pixel-model.md`). Proposed requirement
  number R29, next free UC number — fixed at execution.

- **`04-multiview`** — 2 up to 4 videos at once in a **fixed** named
  `multiview-*` layout collection, for **alternative content** (another
  feed / angle / match), explicitly **not** an ad experience (conscious
  scope widening beyond ads). Implementation-agnostic between
  multi-decoder and HEVC tiles; R3 extended to express two-or-more
  decoders and the tiles single-decoder path. Default audio = primary
  content, audio selection left open. Live content MUST be possible
  (open point flagged: `<ImportedMPD>` live carriage — T-06). Scaffolded
  `PHASE.md`, `TASKS.md`, `T-01-PLAN.md`, and proposed ADR 0003
  (`0003-multiview-decoder-tiles-agnostic-fixed-layouts.md`). The
  proposed `multiview-*` set (`multiview-dual`, `-pip`,
  `-triple-2-over-1`, `-1-plus-2-sidebar`, `-quad`, `-1-plus-3-sidebar`,
  `-1-plus-3-strip`) was distilled from the WOXCON SCU41 reference image
  (retrieved and viewed directly: 16 hardware presets, up to 4 videos;
  corner / side / strip variants collapsed into named presets), pending
  Nicolás's validation against the image. Proposed requirement number
  R30, next free UC number — fixed at execution.

PROJECT.md phases index updated with both phases. ADRs 0002 and 0003
recorded in `status: proposed` (they capture decisions Nicolás already
made; they flip to `accepted` when execution is authorised).

## 2026-08-19 — phase opened: 05-wg-feedback-round-2 (SVTA Ads WG call of 2026-08-19)

Opened phase `05-wg-feedback-round-2` to process the feedback from the
**SVTA Advertising WG call of 2026-08-19**. Round 2 is a different shape
from round 1: a live discussion among six participants (David Hassoun
chairing, Frédéric Plissonneau / InterDigital, Martin Gold / YouView,
Nicolás Levy / Qualabs, Rob Walch / Apple, Yasser Syed / Comcast;
Olivier Cortambert absent), not one reviewer's marked-up files. David
walked the group through a document he had assembled collecting every
concern raised so far about the non-linear work.

The number reserved in PROJECT.md for this was `03-wg-feedback-round-2`;
03 and 04 were taken by `custom-layout` and `multiview` on 2026-07-13, so
it opened as `05`.

**Source.** The Tactiq transcript, Google Doc
`1E_B_53VRaBm8TwJYKTouFxZvSq2MabkO-1l0NIiIdPA` — the only record, no
separate notes, no recording. The 2026-07-22 call
(`1ENK8wExWLduxv45rw08OfIoAd0KwF2w1pCVp1K4dVys`, where this project was
presented to the WG) was read as background so nothing carried over from
it would be reported as new.

**Phase material**: `phases/05-wg-feedback-round-2/svta-wg-2026-08-19-agreements.md`
(English, matching the rest of `.project/`). It splits the call three
ways — **15 agreements** (A1–A15), **7 open proposals** (O1–O7), and
items mentioned without conclusion — attributes every item to its
proposer, notes who argued against it, timestamps each against the
transcript, and carries a fourth section of **eleven readings the
transcript does not support with confidence**, quoted verbatim and left
unresolved rather than guessed at. The extract is phase material, not
task evidence: it is the *input* to T-01, whose *output* is the tasks.

**The two structural items**, both pointing the opposite way from the
committed spec:

- **A2** — device capability travels **up** the chain: the Player tells
  the APS what it can render, the APS makes a specific ad request, and
  the ADS returns a single presentation that is expected to be rendered.
  David's position. Yasser argued for the alternative — the ADS offers
  options and the APS, knowing the device, selects — and the counter to
  it was about ad-delivery practice rather than mechanics: several
  options delivered and only one used breaks tracking and upstream
  expectations. Nicolás's written comment was cited around the point, and
  which of the questions on the table it was cited on is not recoverable
  from the transcript (see the entry below). The external
  constraint behind it is **A3**: the IAB pushed back hard on carrying
  alternative ad experiences inside a single VAST response. This
  contradicts R5 (ADS/APS need no device view, R5.4; a candidate MAY carry
  several ordered presentation options, R5.5; the Player renders the first
  it can satisfy, R5.2), the APS's presentation-options responsibility in
  `02-actors.md`, the
  ordered-fallback decision logged on 2026-05-27, and the whole of
  **UC-09**, which exists solely to demonstrate that model. It also
  reaches phases 03 and 04, both of which lean on the R5 ordered
  fallback.
- **A7** — pausing during an ad break does not raise a pause ad; the
  running ad owns that time until completed or abandoned (David, as
  current practice, with the IAB defining it; Nicolás agreed as an
  instance of the one-experience-at-a-time rule and asked that it be
  confirmed with Zach Kava). This points against **R17**'s pause-ad
  priority over a running overlay, and touches R16, R21, R25, UC-05 and
  UC-08.

**Other agreements of consequence**: capability detection lives in the
application, not the Player, and is passed through to the manifest / APS
request (A1, closed on silence as acceptance); the ADS
decides the layout (A4); slice/tile single-decoder replacement is
deferred to a future edition but recorded as a breadcrumb, at Yasser's
request (A5); **one ad experience at a time** as a general rule spanning
families — broader than R22, which bounds simultaneity only within the
non-linear family (A6); viewer-initiated skip of a non-linear form must
be supported, possibly timer-gated, with dismissal read as an
engagement signal per Rob — a construct absent from the spec, where
"dismiss" only ever means the Player dismissing on resume (A8); SSAI is
not mixed with SGAI in one break (A11); SIMID stays out (A12); and on
the HLS side a non-linear interstitial class in an SVTA-owned namespace,
`com.svta.*` and not `com.apple.*` at Rob's request (A13).

**The principal open proposal is O1**: a placement-type declaration in
the MPD — `replace` / `insert` / `concurrent` / `concurrent-static` — as
a declarable permitted set, with the break **skipped, with tracking**,
when a device satisfies none of the declared types (**O2**). The
combinations carry the intent: `concurrent` only for content that must
not be interrupted; `concurrent` or `insert` so VOD never loses content;
`concurrent` or `replace` so an incapable device gets a standard linear
break; `concurrent` or `concurrent-static` for an L-box with an image
when two video decoders are unavailable. **O3** is agreed as a real
requirement but unresolved in mechanism: mixed ad types inside one break
(concurrent, concurrent, linear, concurrent — Nicolás confirmed he saw
it in the FIFA World Cup water break), where nobody could yet say how
the linear member is known to be a replace or an insert; three candidate
answers were floated and none chosen. **O4** (what the APS must receive
from the Player) collides with R18, which declares the ADS/APS APIs out
of scope. **O5** is the one item where this project has something to
contribute rather than absorb: pause ads have no manifest-level
definition on the SVTA side yet, while our spec already models a
Publisher-declared pause window.

**Tasks**: `T-01` compares the three `context/` source-of-truth files
against the extract and **emits one task per proposed change** — it is a
task that generates tasks, written that way deliberately so the changes
can be iterated one at a time between Nicolás and the agent, each with
its own status and its own close. `T-02` settles the eleven open
readings with David, the deadline first (§4.1, "buy the RENS meeting" —
probably the Rennes MPEG meeting, but the date is what matters).
`T-03` onward do not exist by design: they are T-01's output.
**19 candidate change items** were identified across A1–A15 and O1–O7;
T-01 fixes the final count, since some will merge (A3 and A4 into A2)
and some may split.

Neither task has run. `context/` is untouched — the phase plans the spec
change, it does not make it. PROJECT.md phases index updated.

## 2026-08-19 — phase 05: T-03 added to verify the four claimed spec contradictions

Nicolás questioned the most consequential claim in the agreements
extract — that A2 contradicts R5 — and asked for a task to establish it
rather than assume it, not being convinced the contradiction was real.
Added `T-03` to phase `05-wg-feedback-round-2`.

**Why the doubt is well founded.** The claim travelled through two
layers of interpretation: the automatic transcript, then a reading of
it. And the extract itself leaves **eleven readings unresolved**, of
which **three land directly on A2's mechanics** — §4.8 (whether the
placement-type list is ordered and whether order expresses preference),
§4.9 (where in the MPD the declaration lives, a sentence David breaks
off mid-way), and §4.7 (whether `concurrent-static` is a presentation
element or only a placement-type token). If order expresses preference,
the distance between A2 and R5 narrows sharply. The doubt is not generic
scepticism: identified ambiguities fall exactly on the point in question.

**How T-03 is written.** The verification runs against the **primary
sources**, not against the extract — the extract is the artifact under
test, so re-reading it proves nothing. Required inputs: the transcript
itself (Google Doc `1E_B_53VRaBm8TwJYKTouFxZvSq2MabkO-1l0NIiIdPA`, with
the export command, since it is not in the repo), with every supporting
quote read **in its surrounding turns** rather than isolated; the literal
text of R5 + R5.1–R5.7, R17 + R17.1–R17.4, R22 + R22.1, R16 / R21 / R25,
and DP-1..DP-3; the Ad Presentation Server section and Boundary Summary
of `02-actors.md`; UC-09, plus UC-05 and UC-08; and the ordered-fallback
decision record — which is a **`LOG.md` entry dated 2026-05-27, not an
ADR**, read for its rationale (the spec previously modelled preference as
*optional* priority hints, and the decision made document order
normative) and not only its outcome.

**Three verdicts per pair, all valid**: `contradiction`, `compatible`,
`indeterminate`. The task is explicitly forbidden from forcing one — if
the honest answer is that David has to say what he meant, that is the
result, and it produces a concrete question for the WG instead of a
change to the spec. `indeterminate` is expected on several pairs; that is
what the eleven open readings imply.

Four pairs, with candidate hypotheses named as hypotheses rather than
findings:

- **A2 vs R5** — the *layer* question (R5 governs the resolution
  document APS→Player, A2 the ad request Player→APS→ADS: different legs
  may both hold), the *cardinality* question (R5.5 says a candidate
  **MAY** carry multiple options — is a single-option candidate already
  conformant?), and the *R5.4* question (whether "neither ADS nor APS
  MUST be required to maintain a device-class matrix" **forbids** the APS
  from knowing the device or merely declines to mandate it — the two
  readings give opposite verdicts).
- **A6 vs R22** — contradiction or *gap*: R22 bounds simultaneity within
  the non-linear family, A6 across families, and silence is not
  contradiction. R17 already legislates one cross-family case, so the
  spec is not wholly silent on the axis.
- **A7 vs R17** — whether "an overlay is active" and "an ad break is
  running" denote the same state in this model. If not, the two rules
  may never meet.
- **A8 vs the Player-dismiss vocabulary** — absence rather than
  conflict: a viewer-initiated skip looks unaddressed, not forbidden,
  which makes it an addition and not a contradiction.

**The dependency is written into both tasks.** T-03 questions the
premise T-01 rests on: if A2 does not contradict R5, a large part of the
19 candidate items changes shape or disappears. T-01 may not emit any
task deriving from A2, A6, A7 or A8 before T-03 has ruled on that pair,
and its definition of done now checks that. **Execution order is not
numbering order** — T-03 takes the next free id per the repo convention
(no renumbering of what exists) but runs first; that is stated in the
TASKS.md preamble and in both blocks. `T-04` onward remain T-01's output.

T-03 also has to **write any correction back into the extract**,
including the "Consequence for our spec" note on an affected item:
leaving a disproved claim in the phase material would corrupt the audit
trail for everything downstream.

Not executed. `context/` untouched. PHASE.md context and risks updated
(new risk: the extract's own conflict claims being wrong, mitigated by
T-03); PROJECT.md phase entry updated.

## 2026-08-19 — phase 05: Nicolás's WG-doc comment lands as evidence; A2 claim corrected; T-04 opened

Nicolás supplied the comment of his that was cited during the call, from
the WG document itself. It changed two things and produced one new
task.

**The extract's A2 carried a misreading of the comment, now corrected.**
The extract had summarised the comment as agreeing that the device should
not choose and that the request should send only one option. The comment
says close to the opposite:

> "In my opinion at spec level we should should let devices to choose ->
> main reason: it's the most flexible design because if you don't want
> devices to choose, the APS should send only one option (this is just an
> implementation decision). In my point of view: - spec must be the most
> flexible - the URL to the APS is not under this spec (you could send a
> queryparam with capabilities in your implementation if you like) -
> implementations may send only 1 options if they don't want the device
> to choose"

It defends letting the device choose **at spec level**, and calls "the
APS sends one option" an **implementation** decision. The error was in
this extract: the conditional ("if you don't want devices to choose…")
and the "this is just an implementation decision" qualifier were
compressed away, which inverted the sense. A2's body now reproduces the
comment verbatim, points at the stretch of the call where it was cited
[10:08, 10:49] — where the transcript breaks down at exactly the
conditionals that carry the sense — and flags the point as **contested**.
Two questions sit next to each other there: where capability *detection*
happens, which is **A1** and which Nicolás did agree to, and who
*chooses* the presentation, which is A2. So the passage can be read as
bearing on either. Establishing which of the two the room was on is
handed to T-03.

The same section of the doc also documents what sits behind **A1**: the
"Capabilities detection" question, its device-level and APS-lookup
branches, and the doc's own privacy objection to the latter. Its comment
thread of 2026-08-17 asks for help verifying whether the
decoder-detection APIs exist, and names the supplemental material
referenced in the call — a tab titled *"Concurrent Media Decode
Capability Detection for SGAI Non-Linear Ad Experiences"*. A1 now records
that the material is offered for verification rather than as settled.
Both facts are in the extract.

**The intent behind R5 is settled by its author, so T-03 narrows.**
Nicolás confirmed R5 was written as a **superset**: the APS may send
ordered options; the device may send capabilities **if it has them, and
that is optional**; an implementation may send a single option, in which
case control sits with the APS, and if it sends them all, control sits
with the device: the spec is flexible, the implementation may vary. Under
that reading the A2 shape is **an implementation R5 already permits**,
not a contradiction of it. T-03 no longer has to reconstruct
what R5 means — that is given — only **whether the text says it**, since
a WG reader has nothing but the words. Its expected outcome for A2 is now
the fourth verdict, `spec-does-not-express-its-intent`, and every verdict
must be labelled **design** or **drafting**.

**T-04 opened: make R5's flexibility explicit in `context/`.** A
**drafting** task, explicitly not a design one — it changes what the spec
says, not what it allows, and is constrained so that nothing conformant
becomes non-conformant or vice versa. It must also decide two judgement
calls rather than assume them:

- **R18.** The comment's *"the URL to the APS is not under this spec"*
  overlaps R18, which already declares the ADS / APS API contracts out of
  scope. The task decides whether R18 already carries this adequately and
  only needs to be findable from R5, or whether R5 must state it too.
- **UC-09.** It demonstrates **only one of the two permitted
  implementations** — the APS returning everything and the device
  choosing, worked across D1..D5. A reader who studies the use cases sees
  one path and concludes it is *the* path, which is a plausible
  explanation of how the text came to be read as prescriptive. The task
  evaluates whether a companion use case, or a variant inside UC-09,
  should show the single-option / APS-decides route reaching the same
  screen outcome — weighed against its cost (UC numbering, coverage
  matrix, derived `context-analysis/` artefacts). It records the decision
  either way; clarified wording alone may suffice.

T-04 is **deliberately independent of T-03**: the intent is already
confirmed, so the clarification is justified whatever verdict T-03
reaches. The dependency runs the other way — if T-04 lands, **several of
T-01's 19 candidate items stop being design changes and collapse into
this one drafting problem**, and T-01 must check T-04's outcome and
report which candidates it absorbed. T-01's classification now carries a
**design vs drafting** axis for the same reason. `T-05` onward remain
T-01's output.

New risk recorded in PHASE.md: a drafting task on a normative
requirement is exactly where a "clarification" can quietly become a
semantic change; T-04 is instructed to stop and report if that happens,
because it would mean the intent and the current design genuinely differ.

Nothing executed. `context/` still byte-identical — T-04 will be the
first task to touch it, and only its wording.

## 2026-08-19 — phase 05: T-05 opened (state that an APS may return one option); T-04 scoped back

Nicolás asked for a task to put the permission into `context/` in so many
words, and in doing so answered the question T-04 had left open:

> Add a task for a requirement, a clarification, or something in
> `context/` that says an APS may return one option. Perhaps a use case
> explaining that the APS wants to offer only one option.

**T-05 opened**, and **T-04 scoped back** so the two do not overlap. The
split is written into both blocks and into the TASKS.md preamble:

- **T-04 fixes what is there.** It audits R5 and the APS section of
  `02-actors.md` and clarifies the existing wording where it fails to
  convey the permissiveness. It is subtractive of ambiguity and **adds no
  artefact** — no new requirement, no new use case. Its definition of done
  now says so explicitly, and an audit finding that something is
  *missing* rather than *unclear* is handed to T-05 instead of growing
  T-04's scope. The UC-09 observation moved out of T-04 entirely.
- **T-05 adds what is missing.** An explicit statement that an APS may
  return exactly one presentation option, with the choice then sitting at
  the APS, and/or the use case that demonstrates it.

**The form is T-05's to decide, with an argument**: a clarification inside
R5, a new requirement, or a use case — not mutually exclusive. The
criterion recorded for it: **a requirement says what is permitted, a use
case shows why someone would want it**, and Nicolás's framing — an APS
that *wants* to offer only one option — is a **motivation**, not a rule.
His message
**leans toward the use case**, and that is registered as the **preference
of the spec's owner** — the leading option, not one of two equals. It
remains a preference and not an instruction: if the analysis lands
elsewhere the task must raise it with him rather than deciding silently.

**The pair, and the failure mode it carries.** If the use case lands, it
pairs with **UC-09** — UC-09 shows the device choosing from an ordered
list, the new one shows the APS deciding and sending one. Together they
teach that the spec is a **superset** far better than an adjective in a
requirement could, which is what justifies the cost. But two use cases
can be read as **two modes of the spec** rather than two implementations
of one rule, and that would deepen the misunderstanding instead of
undoing it, since there is no mode to declare. T-05 must therefore edit
**both** cases (UC-09 included, in scope) to state that they exercise
**R5 differently**, that the difference lives in the implementation and
not in the spec, and that **neither is canonical** — and is forbidden
from introducing any name, label, flag or attribute that could be read as
selecting between them, per DP-1.1.

**Two costs written into scope rather than left to be discovered:**

- **The derived artefacts.** A new use case touches the *"Total UC
  count"* line and both matrices in `context-analysis/uc-coverage-matrix.md`
  (which enumerate UC-01..UC-12 explicitly),
  `context-analysis/dash-gap-analysis.md`, and the UC cross-references in
  `context/03-requirements.md`, `05-dash-linear-interfaces.md` and
  `07-backward-compat-checklist.md`. The matrix is regenerable via
  `prompts/1-pre-spec/build-uc-coverage-matrix.prompt`, so regenerate
  rather than hand-patch.
- **A live numbering collision.** The highest landed requirement is
  **R28**, but phase `03-custom-layout` has proposed **R29** and
  `04-multiview` **R30**, and both also claim "next free UC number" —
  neither having executed. T-05 must read both phases before taking a
  number and **raise a collision rather than quietly taking it**.

Same hard limit as T-04: this clarifies and exemplifies, it does **not**
change what the spec permits, and if writing it surfaces that a semantic
change is needed the task **stops and reports**. Also independent of T-03
for the same reason — the intent is already confirmed by R5's author.
The relation to T-01 again runs the other way: T-05 is a **second route**
by which several of the 19 candidates stop being design changes, and T-01
must check its outcome and report which candidates it absorbed.

`T-06` onward remain T-01's output; the phase backlog is five. Two new
risks recorded in PHASE.md: the two-modes misreading, and the numbering
collision. Nothing executed; `context/` still byte-identical.

## 2026-09-15 — phase 05: where the thread stands after two work streams

Written so the next person does not reconstruct this from commits. The
previous entry ends with *"Nothing executed; `context/` still
byte-identical"* — that stopped being true on 2026-09-14 and is
stale; this entry supersedes it as the statement of current state.

### What landed, in two streams

**Stream 1 — the WG feedback round (2026-08-19 call).** Nine commits on
2026-09-14 closed T-06..T-13 (listed with their commits in the phase's
`TASKS.md`): the numbering rule, R29 and its binding to R3, R5 read as
the superset it always was, the APS's permission to omit options,
OOS-5 / OOS-6, R30 with ADR 0005, and the `<Error>` row. On 2026-09-15
the phase's `context-change-recommendations.md` stopped claiming
nothing had been applied (`ed862e4`), and the empty-vs-failed
frontier was closed: `200` strict, an empty resolution is an answer
and not a server failure (`5de5c4d`).

**Stream 2 — the use-case review Nicolás asked for.** The question was
whether the requirements are exercised by the use cases, because that
is what makes the spec testable. Six findings came out; four are
closed and two dissolved on inspection.

- **UC-13** — one ad, Player-declared capabilities, the APS resolving
  to a single option, paired with UC-09 so neither reads as canonical
  (`507c214`). Its D4 row is the structural part: a Player that
  declares nothing leaves the APS unable to narrow, so the same APS
  emits UC-09's document.
- **The APS's document is the reference point** (`242590b`): R5.1,
  R5.5, R7 (title, gist, prose, R7.1) and the section intro stopped
  obliging anyone against the ADS's decision document, which R18
  declares out of scope. Plus R29.7 (an absent parameter means
  *undetermined*, and what an APS does with that is its own business
  decision), UC-12's three paths, and the two sites in
  `05-dash-linear-interfaces.md` that presented an empty response and
  an HTTP error as interchangeable.
- **R23** became a document requirement (`f7d19dd`) instead of a pair
  of permissions no implementation could fail.
- **R13** (`b997663`) and **R28** (applied, pending commit at the time
  of writing) split the same way: the checkable obligation is written
  against the resolution document, and the fidelity of what the APS
  did with the ADS's material is declared part of the bilateral
  contract R18 already puts out of scope, with the ADS named as the
  party in a position to enforce it.

**Result: zero obligations in `context/` that cannot be audited from
the Player-visible interface.** The number comes from two sweeps with
working controls — one over each conformance criterion, one over each
sentence including requirement prose — not from an expectation. A
line-based sweep is not sufficient here and produced a wrong count
twice: these files wrap at ~72 columns, so a subject and its `MUST`
routinely sit on different lines.

**Two findings dissolved rather than closing.** An extension of UC-01
for R30 would have documented a distinction it cannot show, because in
a single-window scenario an empty resolution and a failed one produce
the same playback; the distinction is observable only where a fallback
window exists, which is UC-12. And the reporting of an unfilled
opportunity needs no tracking carrier: R6 and R13 are both anchored to
an ad that exists, and the distinction R30 promises is carried by the
shape of the response.

### What waits on third parties — not blocked on us

- **David Hassoun**: A6 (does "one ad experience at a time"
  contemplate a Publisher-declared hybrid break?), plus the four
  structural questions handed over for the sync before the 21st.
  A6 decides UC-04's fate and R22's wording.
- **Zach Kava, via David**: A7 (does the "running ad owns the pause"
  practice hold?). Decides R17's inversion and UC-08.
- **The Working Group**: A8's slot question — does a viewer dismissal
  end the slot or fall through to the next form under R14 — sent as
  issue 7 on the public repo. The A8 requirement does not land until
  it is answered, and no number is held for it.

**UC-04 and UC-08 are not to be edited** while A6 and A7 are open.

### Pending, depending on nobody

**Regenerating the spec.** `output/v6.1-sgai-spec.md` is from
2026-05-28 and `context/` has moved a great deal since. It is a
**major (v7)**: `context/` changed, which the decision table in
`CLAUDE.md` sends to `build-all`, not to `refine-spec`. Measured, not
estimated:

- **Every one of the nine steps runs; nothing skips.** All generated
  artefacts predate the newest `context/` mtime, the v7 sidecars do
  not exist, and Step 5 (`analyze-iab-ad-templates`) never skips by
  contract.
- **~30–40 minutes of compute**, calibrated on the v5 run of
  2026-05-20, which is the only clean sample — the v6 run has a
  3½-hour idle gap inside it. Roughly 420k input tokens and 70k
  output across the nine steps.
- **Auto-refine: leave it on with `MAX_REFINEMENTS=1`.** The six
  comparison artefacts on disk show the first refinement of a major
  moving four to seven issue categories and the third and fourth
  moving one cosmetic flag each, while the verdict stayed `ON TRACK`
  throughout — so the `STALLED` break never fires on the tail and the
  cap is the only real stop. The default of 5 buys one iteration's
  value for four iterations' cost.
- **`v6.1` has no `comparison.md`** and is the only minor in the
  project without one. It does not need to be produced: it answers
  whether to keep refining or escalate to a major, and `context/`
  having changed already forces the major.

This was deliberately deferred: the use cases had to close first, so
that the regenerated spec would not contain parts nothing can test.

### Recorded, and not work

- **`context/05-dash-linear-interfaces.md` carries no explicit
  informative flag.** This is **not** a defect. R11.3 already requires
  VAST references to sit in an annex or a non-normative note flagged
  as illustrative, and the build already executes that: v6.1 §6.6 is
  titled *"APS internal: decision document → resolution document
  (non-normative)"* and states the conversion *"is not bound by this
  specification"*. The three findings previously open against that
  file — the `<Ad>` wrapper row, the "central responsibility of the
  APS" heading, and the absence of an informative marking — were
  artefacts of reading `context/` as if it were the generated spec,
  and all three dissolve in the output. **They are closed.** A single
  sentence in the file's opening would remove the inference for a
  human reading the source; it changes nothing about the build, and
  the round-1 WG review touched `02`, `03`, `04` and `07` but not
  `05`.
- **A method rule is in force**, approved on 2026-09-15 and living in
  `knowledge/reglas-para-workers.md` in the parent repo: a zero is not
  a result until the same search has been shown to find something
  known to be present. It earned its place repeatedly in this session.
  Its companion — that an idea is swept for across every file rather
  than by the phrase in the file that was edited — is recorded in
  `context-change-recommendations.md` and was **not** approved as a
  rule.
- **The phase-shape proposal is NOT in force.** The suggestion that a
  list of tasks buys nothing when the decider is present, recorded at
  the end of `context-change-recommendations.md`, remains a proposal
  Nicolás has not adopted. It is marked as such there.

### Where the texts are

The two proposal documents in this phase folder carry the reasoning
behind the edits, including what was deliberately not done:
`uc-13-proposal.md` and `aps-truth-and-undetermined-proposal.md`.

## 2026-09-15 — v7 build attempt: halted before Step 6, and what it exposed

The first attempt to regenerate the spec since 2026-05-28. It did not
produce a spec, and the reason is worth more than the spec would have
been.

### What ran

`build-all` was invoked at 19:24 with the defaults Nicolás asked for
(`BUILD_ALL_AUTO_REFINE=true`, `MAX_REFINEMENTS=5`). Stage 1 completed
in 16m 37s — all five artefacts regenerated, none skipped, each
grounding line correct (`notebooklm` for the gap analysis,
`iab-live-link` for the IAB catalogue, `spec-only` for the other
three). They are committed, and the commit records which `context/`
state they were built against.

### Why it stopped

The orchestrator halted **before** Step 6 rather than generating a spec
it knew would be wrong. Its report is preserved verbatim at
[`phases/05-wg-feedback-round-2/v7-build-halt-report-2026-09-15.md`](phases/05-wg-feedback-round-2/v7-build-halt-report-2026-09-15.md).

The finding: **MPEG-DASH 6th spells the same attributes two ways in two
clauses.** The prose (§5.16.4 / §5.16.5) says `@url` and `@clip`; the
normative XML schema (§5.16.6) says `uri` and `clipDuration`. An
instance document validates against the schema, so every XML example in
`context/05-dash-linear-interfaces.md` would be schema-invalid. And
`clipDuration` is `xs:boolean` — our example writes `clipDuration="30000"`,
which is invalid under either spelling.

Halting was the right call: baking invalid XML into a ~160 KB spec and
then refining on it up to five times does not self-correct, because the
refine loop cannot reach back into `context/`.

**What was verified locally, independent of any retrieval**: the file
contradicts itself — `url=` on lines 195 and 205, `uri=` on 289 and 294;
the ten `@url` prose references; and `earliestResolutionTimeOffset`
carrying three incompatible unit conventions (`0`, `15`, `60000`).
These stand whichever spelling turns out to be correct.

**What was NOT verified**: that the schema says `uri` and that
`clipDuration` is boolean. That rests on this build's NotebookLM
retrieval, and this project already records that retrievals have
disagreed with each other about this very document's clause numbering.
**The blocking question is therefore whether the ISO PDF is available**
— it is the only thing that settles spelling and type.

### The pattern the build exposed

Three prompts were found describing a repo that no longer exists:
stale requirement ranges (`R1..R7`, `R1..R10`, `R1..R13` against a set
that reaches R30), the retired **Broadcaster** actor, and — in
`build-spec.prompt`, the generator itself — **no mention of the APS at
all**, the actor that owns most of the obligations landed this week.

In every case the output came out correct anyway, because the worker
reading the prompt noticed and compensated. That is the finding: a
prompt whose output is correct because its reader corrects it is not
working, it is getting lucky, and the next reader has no obligation to
notice. Four commits fixed them, by replacing hard-coded literals with
references to the source of truth — a literal goes stale silently, a
reference does not.

One instance of the same family is **left open deliberately**:
`build-spec.prompt` asks each use-case annex for "the full ListMPD",
but `ListMPD` is only one of the forms a resolution document takes
(R18.1: "`ListMPD` or single-period alternative MPD"), and the glossary
scopes it to the **linear** flow. Counting the v6.1 annexes shows the
worker compensated correctly — linear annexes carry `ListMPD`,
non-linear ones carry `OverlayList`, and nothing wrong was published.
Naming an artefact that takes two shapes is a design decision, not a
correction, so it waits for the batch.

### Where this leaves the work

Blocked on decisions, in the order they block:

1. **The ISO PDF of DASH 6th** — settles spelling and type. Blocks the
   build.
2. **R28.1** — corrected text approved, applied after the batch closes.
3. **How `build-spec` should name the resolution document.**
4. **The IAB citations** at `03-requirements.md:745, 802, 374` —
   a December 2025 draft cited where the Final Release of May 2026
   applies, and a private Google Doc where R12.1 wants the public URL.
5. **Two load-bearing obligations that live outside the R-set** — the
   strip-foreign-namespace validation rule and the backward-compat
   checklist. Recorded as a design question, not a fix.

Nothing was pushed. `context/` was frozen throughout the attempt and is
unchanged: the fixes above are all in `prompts/`, so Stage 1 stays fresh
and the next build starts at Step 6.

### A note on instruments

Four separate measuring instruments returned confident, readable, wrong
answers during this session: a `zsh` glob that aborted the whole command
because one pattern matched nothing; `fuser -m`, which answers for the
mount point rather than the directory asked about; `pgrep -f`, which
matched the very shell running the query; and line-based `grep` for
obligations, in files that wrap at 72 columns, which cannot see a
subject and its `MUST` on different lines. That last one produced a
wrong count twice in one evening.

None of the four failed loudly. Each returned a number that could be
read and believed. The only thing that caught all four was asking the
instrument something whose answer was already known, and disbelieving it
until it got that right.

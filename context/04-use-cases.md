# Use Cases

> See [`02-actors.md`](02-actors.md) for the four-actor model
> (Publisher / ADS / APS / Player) and [`03-requirements.md`](03-requirements.md)
> for R1–R10 that ground these scenarios.

## Frame

Each use case describes a **scenario** (what happens in the playback
session) and the **expected behavior on each device class D1–D5**.
The Publisher's intent (rules) and the ad response (decided by the
ADS, presented to the Player by the APS as the resolution document)
are declared once per scenario; the per-device sub-sections describe
how the Player decides and what the user sees on each device class.
This structure mirrors how Publishers actually validate compliance:
they don't pick one device — they need a single scenario to be
deterministic across the heterogeneity of their viewer population.

The cases below are intentionally **agnostic to the specific MPD
constructs that will implement them**. Cases must remain valid
against multiple design alternatives. If a future design changes the
names of events, resolution documents or attributes, these cases
should still hold without rewriting. New use cases can be appended
as they surface; existing ones are not deleted, only marked
superseded if the design renders them obsolete.

## Terminology

For external readers familiar with industry vocabulary:

| Industry term | Term in this doc |
|---|---|
| Pre-roll | UC-01 — Slot at start of session |
| Mid-roll | UC-02 — Mid-content slot |
| Post-roll | (out of scope — see "Out of scope") |
| Linear ad | An ad whose form takes over the primary content surface during a slot |
| Non-linear ad | An ad whose form is composited on top of the primary content during a slot |
| Ad pod / ad break | UC-06 — Multi-ad break |
| Click-through | UC-11 — ClickThrough activation |

## Device classes

The device class captures only the rendering capabilities relevant
to this spec: how many simultaneous video decoders the device can
run, and what kinds of surfaces it can composite on top of video. It
does not address codec support, DRM, or network conditions — those
are orthogonal and handled elsewhere in the player.

- **D1 — Top-tier**: 2 or more video decoders; can render images on
  top of video; can render HTML on top of video.
- **D2**: 2 video decoders; cannot composite **non-video** content
  (images, HTML) on top of video — but **can composite a second video
  on top of primary** using its dual decoders.
- **D3**: 1 video decoder; can render images on top of video; can
  render HTML on top of video.
- **D4**: 1 video decoder; can render images on top of video;
  cannot render HTML on top of video.
- **D5 — Worst case**: 1 video decoder; no overlay capability of
  any kind (no images, no HTML on top of video).

## Coverage

Each scenario is specified against all five device classes. The
table below summarises, at a glance, the dominant Player behavior
each class exhibits in each scenario. It is a navigational aid, not
a substitute for the per-device sub-sections inside each UC.

| Scenario | Category | D1 | D2 | D3 | D4 | D5 |
|---|---|---|---|---|---|---|
| UC-01 Slot at start of session (pre-roll) | Linear | full-fidelity linear | linear (same) | linear on single decoder | linear on single decoder | linear on single decoder |
| UC-02 Mid-content slot (mid-roll) | Linear | full-fidelity linear | linear with optional pre-buffer | linear on single decoder | linear on single decoder | linear on single decoder |
| UC-06 Multi-ad break | Verification | full sequence | full sequence | full sequence on single decoder | full sequence on single decoder | full sequence on single decoder |
| UC-07 Legacy Player encounters new constructs | Cross-cutting | primary continues (legacy) | primary continues (legacy) | primary continues (legacy) | primary continues (legacy) | primary continues (legacy) |
| UC-11 ClickThrough | Interaction | reads carrier, fires click on activation | same | same | same | same |
| UC-12 Overlapping same-family windows + fallback | Selection | first-window-wins, fallback on resolve failure | same | same | same | same |
| UC-03 Coexisting overlay | Non-linear | highest-fidelity overlay | video overlay or side-by-side (if allowed) or skip | HTML or image overlay | image overlay | skip (graceful) |
| UC-05 Pause-triggered ad | Action-triggered | rich pause overlay | video pause overlay (if video form available) or skip | HTML or image pause overlay | image pause overlay | skip (graceful) |
| UC-04 Hybrid linear + overlay | Mixed | linear + overlay | linear + video overlay (if video form available) or linear only | linear only (overlay skipped) | linear only (overlay skipped) | linear only (overlay skipped) |
| UC-10 Side-by-side / double-box (three-element R26) | Composition | three-element side-by-side (video or image/HTML ad + background element) | side-by-side declined (background element is a non-video surface) | side-by-side for image/HTML ad; declined for video ad | side-by-side for image ad; declined for video/HTML ad | side-by-side declined (no overlay surface) |
| UC-08 Overlay window crosses a pause-ad window | Composition | overlay swaps to pause-ad on pause, restores on resume | overlay swaps to video pause-ad if available, else pause-ad declined; overlay restores on resume | overlay swaps to HTML or image pause-ad, restores on resume | overlay swaps to image pause-ad, restores on resume | both opportunities declined gracefully |
| UC-09 One ad, ordered options across device classes | Worked example | side-by-side (video ad + background) — option 1 | full-screen takeover video — option 4 (image ad/background surfaces unrenderable) | L-shape image full-frame ad creative — option 2 (no second decoder for side-by-side) | L-shape image full-frame ad creative — option 2 (no HTML, no second decoder) | full-screen takeover video — option 4 (no overlay surface) |

Per R3, "skip the opportunity" is always a valid outcome and not a
failure: when no candidate has a renderable form on the target
device, the Player declines the slot and continues with the primary
content uninterrupted. The same continuity guarantee holds at
runtime: if an accepted ad fails while being resolved or rendered — a
decode error, a malformed candidate, a mid-ad network loss — the
Player aborts that ad and continues the primary content uninterrupted
(per R1.4).

## Scenarios

### Out of scope

The following scenarios are deliberately not covered by this document:

- **Server-side ad insertion / stitching (SSAI / SSR)** — the
  foundation phase covers client-side ad rendering only.
- **Post-roll slots** — candidate for a future phase.
- **Ads rendered outside the video surface** (menu / guide / EPG ads,
  home-screen / launcher ads, screensaver ads, and companion /
  multi-screen ads) live in the Player chrome or the application UI,
  not on the playing or paused video, so they are out of scope for the
  SGAI contract. See R12 in
  [`03-requirements.md`](03-requirements.md) for the supported ad-type
  enumeration and this exclusion.

### UC-01 — Slot at start of session (pre-roll)

**Scenario:** The user starts playback of a piece of content. The
Publisher has declared an ad opportunity at the beginning of the
playback session, before the primary content begins. A linear ad is
presented; when it completes, the primary content starts playing.
The underlying DASH mechanism — `InsertPresentation` or
`ReplacePresentation` — is a Publisher decision per content type
(VOD vs live) captured in
[`05-dash-linear-interfaces.md`](05-dash-linear-interfaces.md). Each
use case below references the industry-standard term where applicable
(pre-roll, mid-roll, etc.) so external readers find their bearings.

**Publisher intent:**
- Linear forms allowed (the ad takes over the screen).
- Non-linear forms not allowed for this slot — the Publisher
  wants a clean handoff from ad to primary content.
- Maximum slot duration is bounded.

**Ad response:**
- One or more candidates eligible for this slot.
- Each candidate carries one or more renderable presentation options
  — typically a video form, optionally with an image or HTML form as
  a fallback for devices that cannot render video — as an ordered
  list, where document order is the preference order. Each form has
  its own intrinsic duration declared by the ADS; the actual rendered
  stream length governs R4 enforcement.
- The candidates appear in document order across the slot, and the
  presentation options within a candidate appear in document order.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** reads the Publisher's slot rules
  (linear-only, bounded duration). Selects the first
  renderable candidate following document order, and renders its
  first satisfiable option (video form) on one of the decoders. R4 is
  enforced at playback (the Player stops at the slot cap if the
  rendered stream length reaches it). The extra decoder and overlay
  surfaces are not exercised here because the slot is linear-only.
- **What the user sees:** the session starts. Before the primary
  content begins, the user sees a full-screen ad of bounded
  duration. When the ad completes, the primary content starts from
  its first frame.

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** same as D1. The absence of non-video overlay
  capability does not change behavior here because the slot is
  linear-only.
- **What the user sees:** same as D1.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** selects the first renderable
  candidate following document order. Plays the candidate's video
  form on the single decoder, then reuses the same decoder for the
  primary content. This is feasible because a linear ad and the
  primary content do not need to play concurrently — they are
  sequential. R4 is enforced at playback.
- **What the user sees:** same as D1 and D2 — a full-screen ad
  before the primary content starts.

#### D4 — Single-decoder, image only

- **Player decision:** same as D3.
- **What the user sees:** same as D3.

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** same as D3. Linear ads are sequential, not
  concurrent; they do not need overlay capability or a second
  decoder.
- **What the user sees:** same as D3.

### UC-02 — Mid-content slot (mid-roll)

**Scenario:** While the user is watching the primary content, the
Publisher has declared an ad opportunity at a chosen point inside
the primary timeline. A linear ad is presented at the slot position;
on completion, primary content resumes. Whether the slot consumes a
bounded span of the primary timeline (`ReplacePresentation`) or
leaves it intact and resumes at the same point
(`InsertPresentation`) is a Publisher decision captured in
[`05-dash-linear-interfaces.md`](05-dash-linear-interfaces.md).

**Publisher intent:**
- Linear forms allowed: the ad takes over the screen, replacing a
  bounded span of primary content.
- Non-linear forms not allowed for this slot.
- Maximum slot duration is bounded.

**Ad response:**
- One or more candidates eligible for this slot.
- Each candidate carries one or more renderable presentation options
  — typically a video form, optionally with an image or HTML form as
  a fallback for devices that cannot render video — as an ordered
  list, where document order is the preference order. Each form has
  its own intrinsic duration declared by the ADS; the actual rendered
  stream length governs R4 enforcement.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** reads the Publisher's slot rules at the
  slot position. Selects the first renderable candidate
  following document order, and renders its video form on one of the
  decoders. Transitions playback from primary to ad and back. The
  second decoder may be used to pre-buffer the ad while the first
  finishes the last frames of primary, but this is a Player
  implementation detail with no impact on the Publisher's rules.
  R4 is enforced at playback.
- **What the user sees:** while watching the primary content,
  playback transitions to a full-screen ad of bounded duration,
  then transitions back to the primary content at (or near) the
  slot position.

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** same as D1. Slot rules are device-agnostic;
  the Publisher does not declare different rules for D2 than for
  D1. The second decoder may be used to pre-buffer the ad, same as
  on D1.
- **What the user sees:** same as D1 — a clean mid-content slot.
  No overlay is shown; this device cannot composite non-video
  content on top of video, but linear ads do not need that
  capability.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** selects the first renderable
  candidate following document order. Plays the candidate's video
  form on the single decoder, sequentially with the primary content
  (primary stops, ad plays, primary resumes). R4 is enforced at
  playback.
- **What the user sees:** same as D1 and D2.

#### D4 — Single-decoder, image only

- **Player decision:** same as D3.
- **What the user sees:** same as D3.

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** same as D3.
- **What the user sees:** same as D3.

**Trick-play variant (playback speed != 1x):** the viewer is watching
at 1.5x or 2x when the mid-content slot triggers. The ad renders at the
same speed as the primary content (per R19), so its wall-clock time on
screen is `duration / playback_speed` — a 10 s ad played at 2x occupies
5 s of wall-clock. The slot cap (R4) and the beacon schedule (R13)
operate on the presentation timeline, not on wall-clock, so neither
changes with the playback speed.

### UC-03 — Coexisting overlay

**Scenario:** The Publisher has declared an ad opportunity that
runs *on top of* the primary content without interrupting it. The
primary continues to play; an overlay is composited over it for a
bounded duration, then disappears. This is the central scenario for
non-linear ads and the one where the heterogeneity of devices
matters most: per R3, the Player walks the candidate's presentation
options in document order and renders the first option (form +
layout) it can satisfy.

**Publisher intent:**
- Non-linear forms allowed.
- Allowed layouts for this slot are restricted to a subset
  declared by the Publisher (e.g. banner, corner, L-shape,
  side-by-side, sidebar). Side-by-side may or may not be in the
  allowed set; this matters for the D2 sub-section.
- Maximum overlay duration is bounded.
- Maximum number of concurrent overlays for this slot is bounded.

**Ad response:**
- One or more candidates eligible for this slot.
- Each candidate carries multiple renderable presentation options —
  typically a video form, an image form, and an HTML form — as an
  ordered list, where document order is the preference order.
- The ADS is unaware of the device class; it returns the same
  multi-option candidates for every viewer.
- A candidate's presentation option MAY be a partial-screen layout.
  Two distinct partial-screen layouts can appear, and they are modelled
  differently:
  - **L-shape / squeezeback (the "L-box")**: a layout with **two
    on-screen elements** — a single full-frame ad creative in the
    background and the shrunk primary content composited on top of it
    (the "L" is the band of the full-frame creative that stays visible
    around the shrunk primary content, commonly the side and / or
    bottom). The ad creative is one URL the ADS supplies (image, video,
    or web/HTML) and **always** occupies the whole frame; there is no
    separate third filler element, because the ad creative is itself the
    background (per R27). The media type of the full-frame ad creative
    determines which device class can composite the layout: a **video**
    creative needs two concurrent decoders (the background creative plus
    the shrunk primary content); an **image / HTML** creative needs one
    decoder (the shrunk primary content) plus an image / HTML surface for
    the background.
  - **Side-by-side / double-box**: a layout with **three on-screen
    elements**: the shrunk primary content and the ad sit next to each
    other in two separate boxes, and the two together leave bands /
    margins uncovered, so a third **background element** (a still image,
    never a video and never a web/HTML surface) fills the uncovered
    region (per R26). The media type of the ad determines which device
    class can composite it: a video ad needs two decoders (the primary
    content plus the ad video) plus an image surface for the background;
    an image / HTML ad needs one decoder (the primary content) plus an
    image / HTML surface for the ad and an image surface for the
    background.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** reads Publisher slot rules (allowed
  layouts, duration cap, concurrency cap). Selects a candidate whose
  presentation options conform to the allowed layouts and concurrency
  cap and are renderable on this device, following document order.
  For the selected candidate, per R3, walks the presentation options
  in document order and renders the first option (form + layout) it
  can satisfy. On D1 every form is renderable, so the choice follows
  document order. Composes the chosen form on top of the primary content
  using HTML/CSS layout primitives (per R10). R4 (the duration cap)
  is enforced at playback: the overlay is removed when the rendered
  display reaches the cap.
- **What the user sees:** the primary content keeps playing
  uninterrupted. At the configured position, an overlay appears on
  top of the primary content for the declared duration, then
  disappears. The user sees the highest-fidelity form available
  (typically the HTML or video rendering).

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** selects a candidate whose presentation
  options conform to the allowed layouts and are renderable on this
  device, following document order. For the selected candidate, walks
  the presentation options in document order. The video form
  can be composited on top of the primary using the second decoder
  — this *is* possible on D2 (the device cannot composite non-video
  content on top of video, but it can composite video on video).
  If the candidate's highest-priority form is video, the Player
  picks it and renders it as an overlay on top of the primary using
  the second decoder. If the candidate offers only HTML or image
  forms, those are not renderable (D2 cannot composite non-video
  surfaces on top of video); side-by-side remains an option if the
  Publisher allows it (the video form placed in a non-overlapping
  screen region). Per R3, "decline the opportunity" is a valid
  graceful fallback if nothing renders.
- **What the user sees:** the typical case is a video overlay
  composited on top of the primary content for the declared
  duration. Alternative outcomes: side-by-side (primary shrinks
  to one side, ad video plays in the other) if the first satisfiable
  presentation option is a video form in a side-by-side layout;
  nothing, if neither overlay-video nor side-by-side is
  satisfiable for any candidate. The primary content keeps playing
  in all cases.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** selects a candidate following document order.
  For the selected candidate, walks the presentation options in
  document order and (per R3) skips the video form because rendering
  it concurrently with the primary would require a second decoder
  this device lacks. Picks the HTML form (or the image form, if HTML
  is unavailable for that candidate). Renders the chosen form via the
  HTML/CSS layer on top of the primary content.
- **What the user sees:** the primary content plays without
  interruption. At the configured position, an overlay appears on
  top of the primary content, rendered via HTML or as a static
  image, for the declared duration, then disappears.

#### D4 — Single-decoder, image only

- **Player decision:** selects a candidate following document order.
  For the selected candidate, walks the presentation options in
  document order: skips the HTML form
  (this device cannot render HTML on top of video), skips the
  video form (this device has only one decoder), picks the image
  form (which it can render via the image overlay surface). If the
  only renderable form on the selected candidate is HTML or video,
  per R3 the candidate is skipped and the Player tries the next
  one; if no candidate has a renderable form, the Player declines
  the opportunity entirely.
- **What the user sees:** the primary content plays uninterrupted.
  At the configured position, a static image banner appears on top
  of the primary content for the declared duration, then
  disappears. The user does not see the HTML version even though
  the ADS returned one — that is invisible to the user and to the
  Publisher's rules.

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** reads slot rules. For each candidate, walks
  the presentation options and finds none renderable: HTML needs an HTML overlay
  surface, image needs an image overlay surface, video needs a
  second decoder for concurrent rendering — the device has none of
  these. Side-by-side is also unavailable on D5 because it
  requires a second decoder. Per R3, the Player declines the
  opportunity entirely and continues with the primary content
  uninterrupted.
- **What the user sees:** nothing. The primary content keeps
  playing without interruption. No overlay is rendered.

**Playback speed:** if the primary content plays at a speed other than
1x when the overlay triggers, the overlay renders at that same speed and
its wall-clock on-screen time is `duration / playback_speed` (per R19);
the duration cap (R4) and the beacon schedule (R13) stay on the
presentation timeline.

### UC-04 — Hybrid linear + concurrent overlay

**Scenario:** The Publisher has declared a mid-content slot
where the ad experience is hybrid: a linear ad takes over the
screen *and* a non-linear overlay is composited on top of it
during the same break. The two portions belong to the same break
but are independently selected.

**Publisher intent:**
- Linear forms allowed for the take-over portion.
- Non-linear forms allowed concurrently with the linear ad, with
  a restricted layout set (e.g. banner only — no L-shape on top
  of a linear ad).
- Maximum break duration is bounded.

**Ad response:**
- A linear candidate (or several, in document order) for the take-over
  portion of the break.
- A non-linear candidate (or several, in document order) for the
  overlay portion. Non-linear candidates carry multiple
  renderable presentation options.
- The two responses are independent: the ADS does not
  cross-reference one against the other.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** reads slot rules — linear allowed,
  concurrent overlay allowed with a restricted layout set.
  Validates linear candidates against the linear rules and overlay
  candidates against the overlay rules independently. Selects one
  of each. Plays the linear ad while compositing the overlay on
  top — using a second decoder for the overlay video form, or an
  HTML surface for the HTML form, both available on D1.
- **What the user sees:** a linear ad plays full-screen, and
  during the linear ad a banner overlay is rendered on top of it
  (e.g. branding tied to the same campaign or a different brand
  entirely, depending on what the ADS returns for each portion).

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** the linear portion is satisfied normally
  (one decoder for the linear ad). The overlay portion: if the
  overlay candidate has a video form, the Player can composite it
  on top of the linear ad using the second decoder — this is
  exactly the video-on-video case D2 supports. If the overlay
  candidate only offers HTML or image forms, those cannot be
  composited (D2 does not support non-video overlays on top of
  video), and the overlay portion is declined per R3 while the
  linear ad still plays. Side-by-side does not apply during a
  linear ad take-over.
- **What the user sees:**
  - Overlay candidate has video form: a linear ad plays full-screen
    with a smaller video overlay composited on top of it (e.g.
    branding tied to the campaign) for the declared duration.
  - Overlay candidate has only HTML/image forms: D2 cannot composite
    non-video surfaces on top of video, so the overlay portion is
    declined per R5/R3 while the linear ad still plays. The user sees
    a full-screen linear ad of bounded duration with no overlay on
    top; on completion, primary content resumes.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** for an L-shape / squeezeback option, the layout
  composes two elements — the full-frame ad creative in the background
  and the shrunk primary content on top of it — per R27 (a layout /
  presentation option per R5). The device can satisfy it only when it
  can composite both under the decoder-and-surface budget of R27.3. When
  the full-frame ad creative is an image or HTML surface, this is one
  decoder for the shrunk primary content plus an image / HTML surface for
  the background creative, which a single-decoder image/HTML-capable
  device (D3) can satisfy; if the full-frame ad creative is **video** the
  layout needs two concurrent decoders and is not satisfiable on D3. A
  separate HTML/image overlay *on top of* the linear ad's video still
  requires concurrent composition the single decoder cannot guarantee,
  and is declined per R5/R3.
- **What the user sees:** either the L-shape (the shrunk primary content
  composited on top of a full-frame image / HTML ad creative that fills
  the rest of the frame) if that option is offered and satisfiable, or —
  if only a top-of-video overlay option exists — a full-screen linear ad
  with no overlay on top.

#### D4 — Single-decoder, image only

- **Player decision:** same reasoning as D3, except this device
  cannot render HTML. An L-shape / squeezeback option (two elements
  per R27, a layout / presentation option per R5) is satisfiable when
  the full-frame ad creative is an **image** (one decoder for the shrunk
  primary content plus an image surface for the background creative); an
  HTML full-frame creative is not (D4 cannot render HTML), and a video
  full-frame creative is not (it would need two decoders). A separate
  HTML/image overlay *on top of* the linear ad's video is declined per
  R5/R3.
- **What the user sees:** either the L-shape (the shrunk primary content
  composited on top of a full-frame image ad creative that fills the
  rest of the frame) if that option is offered and satisfiable, or — if
  only a top-of-video overlay option exists — a full-screen linear ad
  with no overlay on top.

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** the linear portion plays normally. The
  overlay portion is declined (no overlay capability of any kind).
- **What the user sees:** a linear ad full-screen, no overlay on
  top.

**Notes / open questions:**
- Whether the Publisher can express constraints linking the two
  portions of the break (e.g. "if the linear ad is from advertiser
  X, suppress the overlay") or whether such cross-portion linkage
  is out of scope. Either answer is compatible with the
  four-actor model; the spec must pick one.
- Whether D3 / D4 must always decline the overlay portion of a
  hybrid break, or whether the Player is allowed to composite an
  HTML / image overlay on top of a linear ad video on
  single-decoder devices that have HTML/image overlay surfaces.
  The R2-clean answer depends on whether the Publisher considers
  "overlay on top of linear ad" a renderable layout the Player can
  satisfy with a single decoder; the spec must declare it
  explicitly.

### UC-05 — Pause-triggered ad

**Scenario:** A window is defined during which, if the user pauses,
an overlay ad is allowed. The window starts at a specified time and
ends at a specified time. Outside the window, pause does not trigger
any overlay. While the window is active and the user is paused, the
overlay is composited on top of the paused primary frame; when the
user resumes playback, the overlay is dismissed and the primary
content continues from the paused position.

**Publisher intent:**
- Define a window of validity (start time, end time) during which
  a pause by the user permits an overlay ad. Outside the window,
  pause permits no overlay.
- The overlay, when permitted, appears on top of the paused
  primary frame.
- Allowed layouts typically include full-screen image, HTML, and
  possibly video over the paused frame.
- Maximum display duration before automatic dismissal is bounded.

**Ad response:**
- Candidates with one or more renderable presentation options (image,
  HTML; optionally video), as an ordered list whose document order is
  the preference order, for the pause-triggered slot.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** if the user pauses inside the
  Publisher-declared window of validity, the Player applies the
  slot rules and selects a renderable candidate following document
  order. For the selected candidate, per R3,
  walks the presentation options in document order. Because the primary is paused
  (no concurrent decoding needed for the primary), even
  single-decoder devices can render a video form here — but on D1
  the second decoder is also available. Renders the chosen form on
  top of the paused primary frame. When the user resumes playback,
  dismisses the overlay. If the user pauses outside the window of
  validity, no overlay is shown.
- **What the user sees:** the user pauses playback. The paused
  frame remains on screen, and an overlay ad appears on top of it
  (typically the highest-fidelity form available — HTML, image, or
  video over the paused frame). When the user resumes playback,
  the overlay is dismissed and playback continues from the paused
  position.

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** the primary is paused, which leaves the
  primary decoder holding the paused frame. The second decoder is
  free to render an ad video on top of the paused frame — this is
  the video-on-video case D2 supports. If the pause-ad candidate
  has a video form, the Player picks it and renders it as an
  overlay. If the candidate only offers HTML or image forms, those
  cannot be composited (D2 does not support non-video overlays);
  per R3, the Player declines the pause-ad opportunity.
- **What the user sees:**
  - Candidate has video form → an ad video plays on top of the
    paused frame for the declared duration, dismissed on resume.
  - Candidate has only HTML/image forms → nothing; the paused
    frame stays on screen until the user resumes.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** selects a candidate following document order.
  Walks the presentation options in document order. The video form would need a decoder, and the
  primary's decoder is currently holding the paused frame; the
  Player has to decide whether it can re-task the decoder to play
  an ad video while preserving the paused position. The image and
  HTML forms are unambiguously renderable on top of the paused
  frame via the HTML/CSS layer. The Player picks the highest
  renderable form: HTML (or image, if HTML is not available for
  the selected candidate).
- **What the user sees:** an HTML or image overlay on top of the
  paused frame, dismissed on resume.

#### D4 — Single-decoder, image only

- **Player decision:** same logic as D3, but HTML is not
  renderable on this device. Walks the presentation options in document order and picks the image form.
  If the only renderable form is HTML or video, per R3 the
  candidate is skipped and the Player tries the next one; if no
  candidate has a renderable form, the Player declines the
  pause-ad opportunity.
- **What the user sees:** a static image overlay on top of the
  paused frame, dismissed on resume.

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** no overlay capability of any kind. Per R3,
  declines the pause-ad opportunity entirely.
- **What the user sees:** nothing. The paused frame stays on
  screen until the user resumes; no ad is rendered.

**Live-content variant (presentation-time freeze):** the content is
live and the viewer pauses inside the pause-ad window. The Player's
presentation time freezes inside the window while the live edge keeps
advancing in wall-clock time; the window is anchored to the frozen
presentation time, so the pause-ad stays admissible for as long as the
viewer remains paused (per R25.1). On resume the pause-ad is dismissed
(per R16). If the Player then jumps to the live edge, that jump is a
Player action after the resume, outside the pause-ad window. This
variant applies across device classes on top of each class's D1–D5
rendering behavior above.

**Notes / open questions:**
- Whether the Player is allowed to pre-fetch pause-triggered
  candidates speculatively when the manifest loads, or must defer
  the APS resolution call to the moment of pause, is an open design
  decision with latency vs targeting-freshness trade-offs. Both
  options are compatible with the four-actor model.
- Whether single-decoder devices (D3, D4) can re-task the decoder
  to play a video form on top of a paused primary frame — and the
  precise semantics of "pause" while doing so — is an open device
  capability question. The conservative default is to skip the
  video form on single-decoder devices in this scenario; the spec
  may revisit this.
- Resolved: D2 has video-on-video composition capability (see
  Device classes), so on D2 the pause-ad's video form is the
  renderable option; non-video forms (HTML/image) remain
  non-renderable on D2 in this scenario.

### UC-06 — Multi-ad break

**Scenario:** The Publisher has declared a mid-content slot that
is filled by several ads played back-to-back, with no primary
content between them. After the last ad in the sequence, the
primary content resumes.

**Publisher intent:**
- Linear forms allowed.
- Maximum total break duration is bounded; the Publisher does
  not prescribe how many ads fit inside, only that the sum cannot
  exceed the cap.

**Ad response:**
- The Publisher declares the break with a duration cap. How many
  ads run inside is an ADS-only decision — the Publisher does not
  express a preference on N. The ADS optimises for revenue across
  the slot by applying its competitive separation, frequency
  capping, and ordering logic.
- An ordered sequence of N candidates that together fill the break.
- Each candidate has its own duration.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** reads slot rules. Plays each candidate in
  order, switching the decoder source between ads. The second
  decoder may be used to pre-buffer ad N+1 while ad N is playing,
  but this is a Player implementation detail. R4 is enforced at
  playback: when the cumulative sequence duration reaches the break
  cap, the Player stops, even if the in-progress ad has not
  finished.
- **What the user sees:** a break plays as a sequence of N ads
  back-to-back, with no primary content between them. After the
  last ad, the primary content resumes.

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** same as D1. The break is linear-only, so
  the absence of non-video overlay capability does not change
  behavior.
- **What the user sees:** same as D1.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** same logic as D1, but the single decoder is
  reused sequentially across the ads and the primary content. No
  pre-buffering of ad N+1 while ad N plays — the device does not
  have a second decoder for that.
- **What the user sees:** same as D1.

#### D4 — Single-decoder, image only

- **Player decision:** same as D3.
- **What the user sees:** same as D3.

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** same as D3.
- **What the user sees:** same as D3.

**Notes:**
- The Player's behaviour when the sequence's total duration exceeds
  the Publisher's declared cap is governed by **R4** in
  [`03-requirements.md`](03-requirements.md): the cap is Publisher-declared
  and the Player enforces it by cutting at the cap, even mid-ad. This
  default applies to UC-06's multi-ad break the same way it applies
  to single-ad slots. Alternative overflow policies (skip the break
  entirely, trim-clean to the previous ad boundary, fail-closed) are
  not the default and would have to be opt-in policies declared by
  the Publisher on the slot — out of scope for the foundation
  phase.

### UC-07 — Legacy Player encounters new constructs

**Scenario:** A Player implementation that predates this proposal
receives a manifest that uses the new SGAI mechanisms — for example,
a non-linear ad opportunity declared via a new event type, or a
modified presentation construct. The legacy Player has no awareness
of the new semantics. This is the cross-cutting backward-
compatibility scenario that any of UC-01..UC-06 may degrade to when
the viewer's Player predates the proposal.

**Publisher intent:** the Publisher has declared an ad
opportunity (any of UC-01..UC-06) intending it to be honored where
possible. The legacy Player cannot honor it.

**Ad response:** not exercised in this scenario. The legacy Player
never reaches the APS resolution step (and the ADS is never
consulted) because it does not recognize the construct that would
trigger the request.

**Expected behavior (uniform across device classes D1..D5):**

- **Player decision:** the Player encounters an unrecognized event
  type or construct in the manifest. Per **R1**, the legacy Player
  MUST skip the unknown construct and continue playing the primary
  content as if the construct were not present. The new proposal
  achieves this by expressing all new mechanisms via MPEG-DASH 6th
  edition extension points whose normative semantics already let a
  non-conforming Player ignore them silently. The legacy Player's
  own behaviour is therefore always skip-and-continue; it has no
  knowledge of the SGAI construct and cannot do anything else.

  What the legacy Player skips depends on what the **Publisher**
  authored for the opportunity, and the Publisher's choice is
  **content-dependent**:

  - **Live / real-time content** → the opportunity falls through as
    skip-and-continue and the ad is an expected loss on the legacy
    Player. Live content cannot be paused or held to splice in a
    standard linear break without losing real content, so per **R1**
    the only safe outcome is to let the legacy Player ignore the SGAI
    construct and keep playing the live edge. The Publisher SHOULD
    treat the opportunity as a loss on legacy Players (see Notes).
  - **Non-live / VOD content** → the Publisher MAY (and SHOULD, where
    monetising the opportunity matters) author a **standard linear
    break** alongside the SGAI construct, using only baseline
    MPEG-DASH 6th edition constructs that a legacy Player already
    renders. The legacy Player skips the SGAI construct it does not
    understand and plays the standard break it does understand, so the
    opportunity is still monetised instead of lost. A current Player
    recognises the SGAI construct and uses it; the standard break is
    the legacy fallback only. Because VOD is not bound to a live edge,
    inserting a standard break costs no real content.

  The Publisher cannot detect a viewer's Player version from the
  manifest (see Notes), so the standard-break fallback is authored
  unconditionally for VOD and is simply ignored by current Players
  that take the richer SGAI path.
- **What the user sees:**
  - Live content, or VOD with no standard-break fallback authored →
    the primary content plays uninterrupted, no ad is rendered, and no
    error surfaces.
  - VOD with a standard-break fallback authored → the legacy Player
    plays the standard linear break (the fallback the Publisher
    authored), then resumes the primary content; no error surfaces.

Behavior does not vary across device classes because the
graceful-degradation outcome depends on Player version and on the
content type (live vs VOD), not on device hardware capabilities. A
device with rich rendering caps running a legacy Player produces the
same outcome as a worst-case device running a legacy Player. What
differs is the content type, not the device: for live content the
legacy Player skips and the opportunity is lost; for VOD the legacy
Player plays whatever standard linear break the Publisher authored as
the fallback.

**Notes:**
- This scenario is the cornerstone of the proposal's extensibility
  contract. Any new construct that the proposal introduces MUST be
  expressible via extension points that produce this outcome on
  legacy Players. New mechanisms that would require a fork of
  MPEG-DASH semantics, or that would error on legacy Players, are
  out of scope (R1).
- The Publisher cannot detect from the manifest whether a viewer's
  Player is legacy or current. For **live** content the Publisher
  must therefore treat ad opportunities that fall through to UC-07 as
  expected losses, not as errors. For **VOD** the Publisher MAY avoid
  the loss by authoring a standard linear break as the legacy
  fallback (using baseline constructs a legacy Player renders): a
  current Player takes the SGAI path and a legacy Player plays the
  standard break, so the opportunity is monetised in both cases.

### UC-08 — Overlay window crosses a pause-ad window

**Scenario:** An overlay (per UC-03) is being shown to the viewer
when the viewer pauses primary playback, and the pause occurs
inside a Publisher-declared pause-ad window (per UC-05). The
pause-ad takes priority over the overlay (per R17): while the
viewer is paused, the pause-ad form is rendered and the overlay
is suspended. The pause-ad form MAY be fullscreen or a partial
overlay over the paused primary frame (per R21); either way it is
the only ad surface visible during the pause and the coexisting
overlay is suspended (R17 / R22). On resume, the pause-ad is
dismissed (per R16) and the overlay continues if its slot window is
still active; the overlay terminates naturally when its window
expires (per R4).

**Publisher intent:**
- An overlay slot (per UC-03) is active at some moment.
- A pause-ad window (per UC-05) overlaps in time with the overlay
  slot.
- The viewer pauses primary playback while the overlay is on
  screen, inside the pause-ad window.

**Ad response:**
- The overlay candidate was already supplied (the ADS decided it
  and the APS presented it) per the UC-03 flow.
- On pause-ad trigger, the Player resolves the APS again for the
  pause-ad slot (which consults the ADS) per the UC-05 flow, unless
  the Publisher's MPD signals that the overlay candidate doubles as
  the pause-ad candidate. The resolution contract is the same as
  UC-05.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** the overlay is currently rendered (per
  UC-03 / D1). When the viewer pauses inside the pause-ad window,
  the Player suspends the overlay rendering (per R17.1) and
  resolves the pause-ad opportunity per UC-05 / D1. The pause-ad
  form is composed on top of the paused primary frame, taking
  priority over the overlay surface. On resume the Player
  dismisses the pause-ad (per R16) and restores the overlay if
  its slot window is still active (per R17.2). The overlay
  continues from where it was suspended — its slot window clock
  followed the primary timeline and froze during the pause. The
  overlay terminates when its declared window expires (per R4),
  not because of the pause.
- **What the user sees:** the overlay is visible while playback
  advances. The viewer pauses; the overlay disappears and a
  pause-ad form (typically the highest-fidelity available: HTML,
  image, or video over the paused frame) takes its place. The
  pause-ad may fill the whole screen or appear as a partial overlay
  over the paused frame (per R21); in the partial case the paused
  frame stays visible around it, but the original overlay is still
  suspended. On resume, the pause-ad disappears and, if the overlay
  slot window is still active, the original overlay reappears and
  continues until its declared window expires.

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** identical to D1 in the pause/resume
  sequencing per R17. The pause-ad rendering follows UC-05 / D2
  rules: if the pause-ad candidate offers a video form, the
  second decoder composites it on top of the paused frame; if the
  candidate offers only HTML or image forms, per R3 the Player
  declines the pause-ad gracefully and the paused frame stays on
  screen until resume. In either case the overlay is suspended
  during the pause (per R17.1). On resume the Player dismisses
  the pause-ad (per R16) and restores the overlay if its slot
  window is still active (per R17.2). The overlay continues from
  where it was suspended — its slot window clock followed the
  primary timeline and froze during the pause. The overlay
  terminates when its declared window expires (per R4), not
  because of the pause.
- **What the user sees:** overlay (video, side-by-side, or other
  D2-renderable form) is visible during play. The viewer pauses;
  if a video pause-ad is available, it replaces the overlay on
  the paused frame; otherwise the paused frame stays clean until
  resume. On resume, if the overlay slot window is still active,
  the overlay reappears and continues until its declared window
  expires.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** the overlay is rendered via the HTML/CSS
  layer (per UC-03 / D3). On pause, the Player suspends the
  overlay rendering (per R17.1) and resolves the pause-ad per
  UC-05 / D3: HTML or image form, composited on top of the
  paused frame. The pause-ad takes priority over the overlay
  surface. On resume the Player dismisses the pause-ad (per R16)
  and restores the overlay if its slot window is still active
  (per R17.2). The overlay re-renders on the HTML/CSS layer from
  where it was suspended — its slot window clock followed the
  primary timeline and froze during the pause. The overlay
  terminates when its declared window expires (per R4), not
  because of the pause.
- **What the user sees:** overlay (HTML or image) is visible
  during play. The viewer pauses; the pause-ad takes its place.
  On resume, if the overlay slot window is still active, the
  original overlay reappears and continues until its declared
  window expires.

#### D4 — Single-decoder, image only

- **Player decision:** the overlay was an image (per UC-03 / D4).
  On pause, the Player suspends the image overlay (per R17.1) and
  resolves the pause-ad per UC-05 / D4: only image forms are
  renderable. The image pause-ad takes priority over the overlay
  surface. On resume the Player dismisses the pause-ad (per R16)
  and restores the image overlay if its slot window is still
  active (per R17.2). The overlay continues from where it was
  suspended — its slot window clock followed the primary timeline
  and froze during the pause. The overlay terminates when its
  declared window expires (per R4), not because of the pause.
- **What the user sees:** image overlay is visible during play.
  On pause, the pause-ad image takes its place. On resume, if the
  overlay slot window is still active, the original image overlay
  reappears and continues until its declared window expires.

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** the overlay was declined per UC-03 / D5
  (the device has no overlay surface, no second decoder). The
  pause-ad is also declined per UC-05 / D5 for the same reasons.
  Since neither surface renders, the R17 priority is moot: there
  is no overlay to suspend and no pause-ad to take priority. The
  viewer's pause and resume have no ad-related effect. Per R3,
  both opportunities are declined gracefully.
- **What the user sees:** primary content plays uninterrupted; on
  pause, the paused frame stays clean; on resume, primary
  continues. No ad is rendered at any point.

### UC-09 — One ad, ordered presentation options, resolved across device classes

**Scenario:** A single non-linear ad candidate is presented for an
overlay slot. The candidate carries several presentation options as
an **ordered list** in the resolution document; per R5, document
order IS the preference order. The ADS emits the **same** ordered
list to every viewer, and the Publisher declares **one
device-agnostic allowed-layout set** for the slot. There is no
per-device-class variant anywhere in the manifest or the resolution
document. The per-device-class outcome is not authored upstream — it
**emerges Player-side** when each device walks the ordered options
(R5.2 / R5.6) and renders the first one it can satisfy against its
own capability and the Publisher's allowed layouts, skipping to the
next when an option fails (R5.7). This use case is the worked
example of that emergence.

**Publisher intent:**
- Non-linear forms allowed.
- One **device-agnostic** allowed-layout set for the slot, including
  side-by-side, L-shape / squeezeback, banner overlay, and
  full-screen takeover. The Publisher does NOT declare a different
  layout set per device class — device capability is the Player's
  sole authority (R5 / R5.4).
- For the side-by-side layout, an advertiser-supplied background element
  fills the uncovered bands (R26). For the L-shape / squeezeback, the
  single ad creative is itself the full-frame background (R27).
- Maximum slot / overlay duration is bounded (R4).

**Ad response:**
- One candidate, carrying four presentation options as an **ordered
  list** (document order is the preference order, R5.1 / R5.5). In
  document order:
  1. **Side-by-side / double-box with a video ad + advertiser
     background** — three on-screen elements: the shrunk primary
     content, the ad video, and an advertiser-supplied background
     element (an image here) filling the bands the two boxes leave
     uncovered (R26). Compositing it needs **two concurrent video
     decoders** (primary content + ad video) **plus an image surface**
     for the background (R26.3).
  2. **L-shape / squeezeback (L-box) with an image full-frame ad
     creative** — two on-screen elements: a single image ad creative
     occupying the full frame in the background, and the shrunk primary
     content composited on top of it (the "L" is the band of the image
     creative that stays visible around the shrunk primary content)
     (R27). The full-frame ad creative is an image, so compositing it
     needs **one video decoder** (the shrunk primary content) **plus an
     image surface** for the full-frame background creative.
  3. **Image banner overlay** — a static image composited on top of
     the primary content. Needs **one video decoder** (the primary
     content) **plus an image overlay surface**.
  4. **Full-screen takeover video** — a linear-style video ad that
     replaces the primary content for the slot, played sequentially
     (primary stops, ad plays, primary resumes). Needs only **one
     video decoder**, reused across ad and primary content; no overlay
     surface and no second decoder.
- The ADS is unaware of the device class; it returns this same
  ordered list for every viewer.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** walks the options in document order (R5.2 /
  R5.6). Option 1 (side-by-side video + background) requires two
  decoders plus an image surface for the background — D1 has both, and
  side-by-side is in the Publisher's allowed set, so the **first**
  option already satisfies form + layout. The Player renders it and
  stops walking.
- **What the user sees:** the primary content shrinks into one box,
  the ad video plays in the other, and the advertiser's background
  image fills the bands around them.

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** walks the options in document order. Option 1
  (side-by-side video + **image** background) — D2 has the two
  decoders for the two videos, but the **background is an image
  element**, and D2 **cannot composite non-video content** on top of
  / alongside video (R26.3): the option fails on its third element.
  Option 2 (L-box with an **image** full-frame ad creative) — needs an
  image surface D2 lacks (the full-frame background creative is
  non-video, R27.3): fails. Option 3 (image banner
  overlay) — needs an image surface: fails. Option 4 (full-screen
  takeover video) — a single decoder reused sequentially, no overlay
  surface, no concurrent composition: **satisfiable**. The Player
  renders option 4.
- **What the user sees:** a full-screen video ad of bounded duration
  replaces the primary content; on completion the primary content
  resumes. Note this is the instructive case: D2 has two decoders yet
  still lands on the takeover, because every earlier option needs a
  non-video surface (the background or the image ad) that D2 cannot
  composite.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** walks the options in document order. Option 1
  (side-by-side video + background) — needs **two** decoders (primary
  + ad video); D3 has one: fails (R26.3). Option 2 (L-box with an
  image full-frame ad creative) — needs **one** decoder for the shrunk
  primary content plus an image surface for the full-frame background
  creative; D3 has both: **satisfiable** (R27.3). The Player renders
  option 2.
- **What the user sees:** the primary content shrinks into one region
  composited on top of the image ad creative that fills the whole frame
  (the L-shape / squeezeback); the band of the ad creative visible
  around the shrunk primary content forms the "L". Both elements are
  present per R27.

#### D4 — Single-decoder, image only

- **Player decision:** walks the options in document order. Option 1
  — two decoders: fails. Option 2 (L-box with an **image** full-frame
  ad creative) — one decoder for the shrunk primary content plus an
  image surface for the full-frame background creative; D4 can render
  images together with video, so: **satisfiable** (R27.3). The Player
  renders option 2. (Had option 2's full-frame ad creative been HTML,
  D4 — which cannot render HTML — would have skipped it and fallen to
  option 4.)
- **What the user sees:** same as D3 — the primary content shrinks into
  one region composited on top of the image ad creative that fills the
  whole frame (the L-shape / squeezeback).

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** walks the options in document order. Option 1
  — two decoders plus an image surface: fails on both counts. Option 2
  — an image surface for the full-frame ad creative: fails (no
  compositing capability of any kind). Option 3 — image overlay surface:
  fails. Option 4
  (full-screen takeover video) — a single decoder reused
  sequentially, no overlay surface required: **satisfiable**. The
  Player renders option 4.
- **What the user sees:** a full-screen video ad of bounded duration
  replaces the primary content; on completion the primary content
  resumes. Same outcome as D2, reached for a different reason (D5 has
  no overlay capability at all; D2 has it for video only).

**What this demonstrates:** the per-device-class outcome was authored
**once**, as a single ordered list emitted identically to every
viewer, with the Publisher declaring **one device-agnostic
allowed-layout set**. No actor upstream of the Player declared a
per-device-class layout. The five classes land on three different
layouts (D1 → side-by-side, D3 / D4 → L-shape, D2 / D5 → full-screen
takeover) purely because each Player walked the same ordered options
and rendered the first one its hardware could satisfy. This directly
answers David Hassoun's question (cross-ref A3) — *"shouldn't the
Publisher declare layouts per device class?"* — by showing that the
positional ordered fallback (R5) plus the Publisher's single
device-agnostic allowed-layout set already produce the correct
per-class layout, without the Publisher (or the ADS or the APS)
holding a device-class matrix (R5.4). The element-count / element-type
reasoning is what makes D2 (two decoders, video-only surfaces) land
differently from D1 (two decoders plus image/HTML surfaces), and what
makes D3 / D4 (one decoder plus image surfaces) land on the L-shape
rather than the side-by-side. The two layouts are modelled
differently: the side-by-side here is a **three-element** layout
(primary content + ad + background element, R26) carrying a **video**
ad, which needs two decoders plus an image surface for the background —
out of reach for D3 / D4; the L-shape is a **two-element** layout
(a full-frame ad creative + the shrunk primary content on top, R27)
carrying an **image** full-frame creative, which needs one decoder plus
one image surface — within reach for D3 / D4.

**Notes:**
- The instructive contrast is D2: it owns the two decoders the
  side-by-side video needs, yet declines option 1 because the **third
  element** — the background element, an image here — is a non-video
  surface D2 cannot composite (R26.3). This shows the rule is
  element-**type**, not just element-**count**.
- D5 and D2 share the outcome (full-screen takeover) but for different
  reasons; the ordered fallback reaches the same last-resort option by
  two different paths.

### UC-10 — Side-by-side / double-box (three-element layout, R26 illustration)

**Scenario:** The Publisher has declared an overlay slot whose allowed
layouts include **side-by-side / double-box**. A candidate is
presented whose chosen presentation option is the side-by-side: the
shrunk primary content sits next to the ad on a 16:9 screen, and the
two boxes together leave bands / margins uncovered. Per R26 a third
element, a **background element** (a still image, never a video and
never a web/HTML surface), MAY fill the uncovered region; in this worked
example the advertiser supplies an image background. This use case is the worked
illustration of R26 itself: a layout that puts **three on-screen
elements** in play (primary content, ad, background) and the
device-class reasoning that follows from the element count and type.

**Publisher intent:**
- Non-linear forms allowed; the allowed-layout set includes
  side-by-side / double-box.
- An advertiser-supplied background element MAY brand the uncovered
  region (R26); the Publisher does not supply a background. When the
  advertiser supplies none, the uncovered region renders as black
  (R26.2).
- Maximum overlay duration is bounded (R4).

**Ad response:**
- A candidate whose selected presentation option is the side-by-side
  layout. The option pairs the ad **form** (video, image, or HTML per
  R15) with the side-by-side **layout**.
- The background fill is carried as a **composition attribute of the
  slot / layout**, NOT as one of the candidate's alternative
  presentation options (R26.1). Two background cases are exercised:
  - **Advertiser background supplied** — the advertiser's creative
    brands / takes over the region between the two boxes (the IAB
    "Double Box Video + Background" model). The Player composites it as
    the third element (R26.2).
  - **No advertiser background** — the uncovered region renders as
    black (R26.2).

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** the side-by-side is in the allowed set and the
  device can composite three elements. If the ad form is **video**, D1
  uses two decoders (primary + ad video) plus an image surface for the
  background (R26.3). If the ad form is an **image or HTML** surface,
  D1 uses one decoder for the primary content plus an image / HTML
  surface for the ad and an image surface for the background. Either way
  the side-by-side renders with the third-element background.
- **What the user sees:** the primary content shrinks into one box,
  the ad plays / displays in the other, and the advertiser's background
  image fills the bands around the two boxes.

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** D2 can composite **video on video** but cannot
  composite **non-video** surfaces alongside / on top of video. The
  side-by-side's third element — the background image — is a non-video
  surface (R26.3). Even when the ad form is video (the two decoders are
  available for the two videos), the background-image element cannot be
  composited on D2, so the side-by-side option is **not satisfiable**
  on D2. Per R5.7 the Player skips it and falls through to the next
  presentation option (or declines per R3).
- **What the user sees:** the side-by-side is not rendered on D2;
  whatever the next satisfiable option is takes its place (or nothing,
  if none renders). The three-element background is the blocker, not
  the decoder count.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** if the ad form is **image or HTML**, the
  side-by-side needs **one** decoder (the primary content) plus an image
  / HTML surface for the ad and an image surface for the background; D3
  has both, so it is **satisfiable** (R26.3). If the ad form is **video**, the
  side-by-side needs **two** decoders (primary + ad video), which D3
  lacks: not satisfiable, the Player skips to the next option per R5.7.
- **What the user sees:** for an image / HTML ad, the primary content
  shrinks into one box, the image / HTML ad displays in the other, and
  the background image fills the bands around them. For a video ad on
  D3, the side-by-side is skipped.

#### D4 — Single-decoder, image only

- **Player decision:** same reasoning as D3 restricted to the image
  case — D4 cannot render HTML. An **image** ad in the side-by-side
  needs one decoder (the primary content) plus image surfaces for the
  ad and the background; D4 has them, so it is **satisfiable** (R26.3).
  A **video** ad (two decoders) or an **HTML** ad (no HTML surface) is
  not satisfiable; the Player skips to the next option per R5.7.
- **What the user sees:** for an image ad, the primary content shrinks
  into one box, the image ad displays in the other, and the background
  image fills the bands around them. For a video or HTML ad, the
  side-by-side is skipped.

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** D5 has no overlay capability of any kind — no
  image surface, no HTML surface, and only one decoder. The
  side-by-side needs at minimum one decoder plus an image surface for
  the ad and for the background; D5 cannot composite any non-video
  surface, so the side-by-side is **not satisfiable** regardless of the
  ad form. Per R5.7 / R3 the Player skips it and falls through (or
  declines the opportunity).
- **What the user sees:** the side-by-side is not rendered on D5; the
  next satisfiable option takes its place, or nothing if none renders.

**Notes:**
- The background element is a **composition attribute of the layout**
  (R26.1), not a fourth presentation option. The Player does not "walk"
  it the way it walks the ordered presentation options; it composites
  it as part of rendering the side-by-side once that layout is chosen.
- The element **type** matters as much as the count (R26.3): D2 owns
  the decoders a side-by-side video needs but still cannot render it,
  because the background element (an image here) is a non-video surface
  D2 cannot composite. The L-shape / squeezeback (the L-box, UC-09
  option 2) is defined in R27 as its own layout: two elements (a
  full-frame ad creative with the shrunk primary content on top), with
  its own decoder-and-surface budget (R27.3).

### UC-11 — ClickThrough

**Scenario:** An ad (linear or non-linear) is presented in a slot. Its
resolution document carries the ad's ClickThrough URL together with one
or more associated click-tracking URLs. The viewer activates the click
— a select on a CTV remote, a tap on mobile. At the moment of
activation the Player opens (or hands off) the ClickThrough destination
and fires the associated click-tracking (per R28.2). The activation is
a user-input event: the click carries no presentation time and fires
only when the viewer acts, never on the timeline.

**Publisher intent:**
- The slot permits an ad whose creative may carry a ClickThrough. No
  Publisher-side configuration beyond permitting the ad — the
  ClickThrough travels with the ad, not with the slot.

**Ad response:**
- A candidate whose resolution document declares the ClickThrough URL
  and its associated click-tracking URL(s) in the normative carrier
  (per R28.1).

**Expected behavior:**
- On activation the Player opens the ClickThrough destination and fires
  every associated click-tracking URL once. This is the interoperability
  point of the use case: because the carrier is normative, every
  conformant Player reads the same two fields and fires the click
  identically (R28.2).
- The click-tracking fires on activation. This is separate from the
  timeline tracking beacons (impression, quartiles) of R13 / R6, which
  the Player schedules by presentation time through the callback scheme;
  the click has no presentation time.

**Device classes:** the outcome depends on the device's input mechanism
(remote select, tap), not on its decoder or overlay budget. D1–D5 read
the ClickThrough carrier and fire the click-tracking identically;
device class does not change the behavior.

**Backward compatibility:** a legacy Player predating SGAI renders the
ad but does not activate the click, because it ignores the unknown
carrier (per R1) — the click is simply inert, connecting to UC-07.

### UC-12 — Overlapping same-family windows with fallback

**Scenario:** Two overlay windows of the same family overlap in time in
the primary `MPD`. The Player takes the first overlapping window it
encounters and resolves its resolution document. If it cannot access
that resolution document — the APS does not respond, or the event URL
that resolves to the APS fails — it falls through to the second window
as a backup. If the first window resolves successfully, the second is
ignored; the two are never served concurrently (per R20.1).

**Publisher intent:**
- Two overlapping opportunity windows of the same family are declared in
  the primary `MPD`, forming a primary-plus-fallback chain, not two
  concurrent opportunities.

**Ad response:**
- Each window resolves independently to its own resolution document via
  its own event URL / APS. The fallback window's resolution document is
  fetched only if the first window fails to resolve.

**Expected behavior:**
- The Player selects the first overlapping window and attempts to
  resolve it. On success it serves that window and does not touch the
  second. On failure to access the first window's resolution document,
  it resorts to the second (per R20.1). Whichever window is served, the
  forms inside its resolution document are then sequenced per R14: R20
  selects which window is served; R14 sequences the forms within the
  chosen window.

**Device classes:** this is window selection, not rendering, so it is
largely device-agnostic. D1–D5 select and fall back identically; the
device class affects only how the forms inside the chosen window render
(per UC-03), not which window is chosen.

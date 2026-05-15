# Use Cases

> See [`02-actors.md`](02-actors.md) for the three-actor model
> (Broadcaster / ADS / Player) and [`03-requirements.md`](03-requirements.md)
> for R1–R10 that ground these scenarios.

## Frame

Each use case describes a **scenario** (what happens in the playback
session) and the **expected behavior on each device class D1–D5**.
The broadcaster's intent (rules) and the ADS response are declared
once per scenario; the per-device sub-sections describe how the
Player decides and what the user sees on each device class. This
structure mirrors how broadcasters actually validate compliance:
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
| UC-03 Coexisting overlay | Non-linear | highest-fidelity overlay | video overlay or side-by-side (if allowed) or skip | HTML or image overlay | image overlay | skip (graceful) |
| UC-04 Hybrid linear + overlay | Mixed | linear + overlay | linear + video overlay (if video form available) or linear only | linear only (overlay skipped) | linear only (overlay skipped) | linear only (overlay skipped) |
| UC-05 Pause-triggered ad | Action-triggered | rich pause overlay | video pause overlay (if video form available) or skip | HTML or image pause overlay | image pause overlay | skip (graceful) |
| UC-06 Multi-ad break | Verification | full sequence | full sequence | full sequence on single decoder | full sequence on single decoder | full sequence on single decoder |
| UC-07 Legacy Player encounters new constructs | Cross-cutting | primary continues (legacy) | primary continues (legacy) | primary continues (legacy) | primary continues (legacy) | primary continues (legacy) |

Per R3, "skip the opportunity" is always a valid outcome and not a
failure: when no candidate has a renderable form on the target
device, the Player declines the slot and continues with the primary
content uninterrupted.

## Scenarios

### Out of scope

The following scenarios are deliberately not covered by this document:

- **Server-side ad insertion / stitching (SSAI / SSR)** — the
  foundation phase covers client-side ad rendering only.
- **Post-roll slots** — candidate for a future phase.
- **Companion ads / multi-screen** — out of scope.
- **Native ad integrations** (ads in the Player chrome, not in the
  video) — out of scope.

### UC-01 — Slot at start of session (pre-roll)

**Scenario:** The user starts playback of a piece of content. The
broadcaster has declared an ad opportunity at the beginning of the
playback session, before the primary content begins. A linear ad is
presented; when it completes, the primary content starts playing.
The underlying DASH mechanism — `InsertPresentation` or
`ReplacePresentation` — is a Broadcaster decision per content type
(VOD vs live) captured in
[`05-dash-linear-interfaces.md`](05-dash-linear-interfaces.md). Each
use case below references the industry-standard term where applicable
(pre-roll, mid-roll, etc.) so external readers find their bearings.

**Broadcaster intent:**
- Linear forms allowed (the ad takes over the screen).
- Non-linear forms not allowed for this slot — the broadcaster
  wants a clean handoff from ad to primary content.
- Maximum slot duration is bounded.

**ADS response:**
- One or more candidates eligible for this slot.
- Each candidate carries one or more renderable forms — typically a
  video form, optionally with an image or HTML form as a fallback
  for devices that cannot render video. Each form has its own
  intrinsic duration declared by the ADS; the actual rendered
  stream length governs R4 enforcement.
- Optional ADS-supplied ranking hints across candidates and across
  forms within a candidate.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** reads the broadcaster's slot rules
  (linear-only, bounded duration). Selects the highest-ranked
  renderable candidate using ADS ranking hints and any client-side
  ranking, and renders its video form on one of the decoders. R4 is
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

- **Player decision:** selects the highest-ranked renderable
  candidate using ADS ranking hints. Plays the candidate's video
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
broadcaster has declared an ad opportunity at a chosen point inside
the primary timeline. A linear ad is presented at the slot position;
on completion, primary content resumes. Whether the slot consumes a
bounded span of the primary timeline (`ReplacePresentation`) or
leaves it intact and resumes at the same point
(`InsertPresentation`) is a Broadcaster decision captured in
[`05-dash-linear-interfaces.md`](05-dash-linear-interfaces.md).

**Broadcaster intent:**
- Linear forms allowed: the ad takes over the screen, replacing a
  bounded span of primary content.
- Non-linear forms not allowed for this slot.
- Maximum slot duration is bounded.

**ADS response:**
- One or more candidates eligible for this slot.
- Each candidate carries one or more renderable forms — typically a
  video form, optionally with an image or HTML form as a fallback
  for devices that cannot render video. Each form has its own
  intrinsic duration declared by the ADS; the actual rendered
  stream length governs R4 enforcement.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** reads the broadcaster's slot rules at the
  slot position. Selects the highest-ranked renderable candidate
  using ADS ranking hints, and renders its video form on one of the
  decoders. Transitions playback from primary to ad and back. The
  second decoder may be used to pre-buffer the ad while the first
  finishes the last frames of primary, but this is a Player
  implementation detail with no impact on the broadcaster's rules.
  R4 is enforced at playback.
- **What the user sees:** while watching the primary content,
  playback transitions to a full-screen ad of bounded duration,
  then transitions back to the primary content at (or near) the
  slot position.

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** same as D1. Slot rules are device-agnostic;
  the broadcaster does not declare different rules for D2 than for
  D1. The second decoder may be used to pre-buffer the ad, same as
  on D1.
- **What the user sees:** same as D1 — a clean mid-content slot.
  No overlay is shown; this device cannot composite non-video
  content on top of video, but linear ads do not need that
  capability.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** selects the highest-ranked renderable
  candidate using ADS ranking hints. Plays the candidate's video
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

### UC-03 — Coexisting overlay

**Scenario:** The broadcaster has declared an ad opportunity that
runs *on top of* the primary content without interrupting it. The
primary continues to play; an overlay is composited over it for a
bounded duration, then disappears. This is the central scenario for
non-linear ads and the one where the heterogeneity of devices
matters most: per R3, the Player walks the candidate's renderable
forms in priority order and picks the highest-fidelity form it can
render.

**Broadcaster intent:**
- Non-linear forms allowed.
- Allowed layouts for this slot are restricted to a subset
  declared by the broadcaster (e.g. banner, corner, L-shape,
  side-by-side, sidebar). Side-by-side may or may not be in the
  allowed set; this matters for the D2 sub-section.
- Maximum overlay duration is bounded.
- Maximum number of concurrent overlays for this slot is bounded.

**ADS response:**
- One or more candidates eligible for this slot.
- Each candidate carries multiple renderable forms — typically a
  video form, an image form, and an HTML form — with optional
  ADS-supplied priority hints across forms.
- The ADS is unaware of the device class; it returns the same
  multi-form candidates for every viewer.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** reads broadcaster slot rules (allowed
  layouts, duration cap, concurrency cap). Selects the highest-
  ranked candidate whose form-and-layout combinations conform to
  the allowed layouts and concurrency cap and are renderable on
  this device, using ADS ranking hints and any client-side ranking.
  For the selected candidate, per R3, walks the forms in priority
  order and picks the highest-fidelity form it can render. On D1
  every form is renderable, so the choice follows ADS priority
  hints. Composes the chosen form on top of the primary content
  using HTML/CSS layout primitives (per R10). R4 (the duration cap)
  is enforced at playback: the overlay is removed when the rendered
  display reaches the cap.
- **What the user sees:** the primary content keeps playing
  uninterrupted. At the configured position, an overlay appears on
  top of the primary content for the declared duration, then
  disappears. The user sees the highest-fidelity form available
  (typically the HTML or video rendering).

#### D2 — Dual-decoder, video-on-video only

- **Player decision:** selects the highest-ranked candidate whose
  form-and-layout combinations conform to the allowed layouts and
  are renderable on this device, using ADS ranking hints. For the
  selected candidate, walks forms in priority order. The video form
  can be composited on top of the primary using the second decoder
  — this *is* possible on D2 (the device cannot composite non-video
  content on top of video, but it can composite video on video).
  If the candidate's highest-priority form is video, the Player
  picks it and renders it as an overlay on top of the primary using
  the second decoder. If the candidate offers only HTML or image
  forms, those are not renderable (D2 cannot composite non-video
  surfaces on top of video); side-by-side remains an option if the
  broadcaster allows it (the video form placed in a non-overlapping
  screen region). Per R3, "decline the opportunity" is a valid
  graceful fallback if nothing renders.
- **What the user sees:** the typical case is a video overlay
  composited on top of the primary content for the declared
  duration. Alternative outcomes: side-by-side (primary shrinks
  to one side, ad video plays in the other) if the candidate's
  highest-renderable form is video and the layout is preferred or
  forced; nothing, if neither overlay-video nor side-by-side is
  satisfiable for any candidate. The primary content keeps playing
  in all cases.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** selects the highest-ranked candidate. For the selected
  candidate, walks forms in priority order and (per R3) skips the
  video form because rendering it concurrently with the primary
  would require a second decoder this device lacks. Picks the HTML
  form (or the image form, if HTML is unavailable for that
  candidate). Renders the chosen form via the HTML/CSS layer on
  top of the primary content.
- **What the user sees:** the primary content plays without
  interruption. At the configured position, an overlay appears on
  top of the primary content, rendered via HTML or as a static
  image, for the declared duration, then disappears.

#### D4 — Single-decoder, image only

- **Player decision:** selects the highest-ranked candidate. For the selected
  candidate, walks forms in priority order: skips the HTML form
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
  broadcaster's rules.

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** reads slot rules. For each candidate, walks
  the forms and finds none renderable: HTML needs an HTML overlay
  surface, image needs an image overlay surface, video needs a
  second decoder for concurrent rendering — the device has none of
  these. Side-by-side is also unavailable on D5 because it
  requires a second decoder. Per R3, the Player declines the
  opportunity entirely and continues with the primary content
  uninterrupted.
- **What the user sees:** nothing. The primary content keeps
  playing without interruption. No overlay is rendered.

**Notes / open questions:**
- How the ADS expresses form-level priority (ranked list vs single
  priority field per form) is an open spec decision; it should be
  expressible without coupling the cases to a specific schema.
- Whether the Player can pick a layout different from the
  candidate's nominal layout (e.g. promote a "banner" candidate to
  "side-by-side" because the device cannot do banner) or whether
  the broadcaster must declare side-by-side as an allowed layout
  for the swap to be legal. The R2-clean answer is the latter: the
  Player never violates the broadcaster's declared rules.
- Whether the Player still issues the ADS request on D5 (and any
  other device that will inevitably skip the opportunity) to
  support impression accounting and frequency-capping signals, or
  whether it can skip the request entirely, is a privacy and
  bandwidth trade-off the spec must resolve. The question is
  independent of the schema chosen.
- Resolved: "No overlay shown" is an explicit, valid outcome per
  **R3** in [`03-requirements.md`](03-requirements.md) — the Player may
  decline the opportunity gracefully without raising an error.

### UC-04 — Hybrid linear + concurrent overlay

**Scenario:** The broadcaster has declared a mid-content slot
where the ad experience is hybrid: a linear ad takes over the
screen *and* a non-linear overlay is composited on top of it
during the same break. The two portions belong to the same break
but are independently selected.

**Broadcaster intent:**
- Linear forms allowed for the take-over portion.
- Non-linear forms allowed concurrently with the linear ad, with
  a restricted layout set (e.g. banner only — no L-shape on top
  of a linear ad).
- Maximum break duration is bounded.

**ADS response:**
- A linear candidate (or several, with ranking) for the take-over
  portion of the break.
- A non-linear candidate (or several, with ranking) for the
  overlay portion. Non-linear candidates carry multiple
  renderable forms.
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
  - Overlay candidate has only HTML/image forms: a linear ad plays
    full-screen with no overlay on top. From the user's
    perspective, the experience collapses to UC-02.

#### D3 — Single-decoder, image and HTML capable

- **Player decision:** the linear portion uses the single decoder.
  The overlay portion would need to render concurrently with the
  linear ad's video, but the device has only one decoder for
  video. The HTML and image forms could in principle be composited
  via the HTML/CSS layer, but the Player has to decide whether
  rendering an overlay on top of a linear ad is supported in this
  scenario at all. The conservative interpretation, consistent
  with R2 and R3, is to decline the overlay portion when the
  primary "video underneath" is itself an ad and the device cannot
  handle the linear+overlay composition cleanly.
- **What the user sees:** a linear ad plays full-screen, with no
  overlay on top. (See open question below — this behavior is not
  fully resolved.)

#### D4 — Single-decoder, image only

- **Player decision:** same reasoning as D3. The overlay portion
  is declined.
- **What the user sees:** same as D3 — a linear ad full-screen,
  no overlay on top.

#### D5 — Single-decoder, no overlay (worst case)

- **Player decision:** the linear portion plays normally. The
  overlay portion is declined (no overlay capability of any kind).
- **What the user sees:** a linear ad full-screen, no overlay on
  top.

**Notes / open questions:**
- Whether the broadcaster can express constraints linking the two
  portions of the break (e.g. "if the linear ad is from advertiser
  X, suppress the overlay") or whether such cross-portion linkage
  is out of scope. Either answer is compatible with the
  three-actor model; the spec must pick one.
- Whether D3 / D4 must always decline the overlay portion of a
  hybrid break, or whether the Player is allowed to composite an
  HTML / image overlay on top of a linear ad video on
  single-decoder devices that have HTML/image overlay surfaces.
  The R2-clean answer depends on whether the broadcaster considers
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

**Broadcaster intent:**
- Define a window of validity (start time, end time) during which
  a pause by the user permits an overlay ad. Outside the window,
  pause permits no overlay.
- The overlay, when permitted, appears on top of the paused
  primary frame.
- Allowed layouts typically include full-screen image, HTML, and
  possibly video over the paused frame.
- Maximum display duration before automatic dismissal is bounded.

**ADS response:**
- Candidates with one or more renderable forms (image, HTML;
  optionally video) for the pause-triggered slot.

**Expected behavior per device class:**

#### D1 — Top-tier (2+ video decoders, image and HTML overlays)

- **Player decision:** if the user pauses inside the
  Broadcaster-declared window of validity, the Player applies the
  slot rules and selects the highest-ranked renderable candidate
  using ADS ranking hints. For the selected candidate, per R3,
  walks the forms in priority order. Because the primary is paused
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

- **Player decision:** selects the highest-ranked candidate. Walks the forms in
  priority order. The video form would need a decoder, and the
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
  renderable on this device. Walks forms and picks the image form.
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

**Notes / open questions:**
- Whether the Player is allowed to pre-fetch pause-triggered
  candidates speculatively when the manifest loads, or must defer
  the ADS call to the moment of pause, is an open design decision
  with latency vs targeting-freshness trade-offs. Both options are
  compatible with the three-actor model.
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

**Scenario:** The broadcaster has declared a mid-content slot that
is filled by several ads played back-to-back, with no primary
content between them. After the last ad in the sequence, the
primary content resumes.

**Broadcaster intent:**
- Linear forms allowed.
- Maximum total break duration is bounded; the broadcaster does
  not prescribe how many ads fit inside, only that the sum cannot
  exceed the cap.

**ADS response:**
- The broadcaster declares the break with a duration cap. How many
  ads run inside is an ADS-only decision — the broadcaster does not
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
  the broadcaster's declared cap is governed by **R4** in
  [`03-requirements.md`](03-requirements.md): the cap is broadcaster-declared
  and the Player enforces it by cutting at the cap, even mid-ad. This
  default applies to UC-06's multi-ad break the same way it applies
  to single-ad slots. Alternative overflow policies (skip the break
  entirely, trim-clean to the previous ad boundary, fail-closed) are
  not the default and would have to be opt-in policies declared by
  the broadcaster on the slot — out of scope for the foundation
  phase.

### UC-07 — Legacy Player encounters new constructs

**Scenario:** A Player implementation that predates this proposal
receives a manifest that uses the new SGAI mechanisms — for example,
a non-linear ad opportunity declared via a new event type, or a
modified presentation construct. The legacy Player has no awareness
of the new semantics. This is the cross-cutting backward-
compatibility scenario that any of UC-01..UC-06 may degrade to when
the viewer's Player predates the proposal.

**Broadcaster intent:** the broadcaster has declared an ad
opportunity (any of UC-01..UC-06) intending it to be honored where
possible. The legacy Player cannot honor it.

**ADS response:** not exercised in this scenario. The legacy Player
never reaches the ADS resolution step because it does not recognize
the construct that would trigger the request.

**Expected behavior (uniform across device classes D1..D5):**

- **Player decision:** the Player encounters an unrecognized event
  type or construct in the manifest. Per **R1**, the Player MUST
  skip the unknown construct and continue playing the primary
  content as if the construct were not present. The new proposal
  achieves this by expressing all new mechanisms via MPEG-DASH 6th
  edition extension points whose normative semantics already let a
  non-conforming Player ignore them silently.
- **What the user sees:** the primary content plays uninterrupted.
  No ad is rendered. No error surfaces.

Behavior does not vary across device classes because the
graceful-degradation outcome depends on Player version, not on
device hardware capabilities. A device with rich rendering caps
running a legacy Player produces the same outcome as a worst-case
device running a legacy Player: the primary content continues
unmodified.

**Notes:**
- This scenario is the cornerstone of the proposal's extensibility
  contract. Any new construct that the proposal introduces MUST be
  expressible via extension points that produce this outcome on
  legacy Players. New mechanisms that would require a fork of
  MPEG-DASH semantics, or that would error on legacy Players, are
  out of scope (R1).
- The Broadcaster cannot detect from the manifest whether a viewer's
  Player is legacy or current. Thus the Broadcaster must treat ad
  opportunities that fall through to UC-07 as expected losses, not
  as errors.

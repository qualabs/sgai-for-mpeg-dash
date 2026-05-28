# Project log

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

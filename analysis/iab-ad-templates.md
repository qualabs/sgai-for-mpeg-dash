[GROUNDED_BY=iab-live-link]

# IAB ad templates — live mirror

**Source**: <https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e>
(IAB Tech Lab — "Ad Format Guidelines for Digital Video and CTV",
Final Release May 2026)

**Fetched**: 2026-05-14T18:31:27Z

**Status**: Live mirror — snapshot in time. This file is regenerated
on every `build-all` invocation; it MAY diverge from the source
between runs. Authoritative content remains in the IAB document.

**Grounding**: `[GROUNDED_BY=iab-live-link]` — fetch from the source
link succeeded via
`mcp__claude_ai_Google_Drive__read_file_content`; the table below
reflects the live IAB content.

## Accepted ad-type values

| Name | Category | Visual placement | Typical duration / interaction | Source paragraph / heading |
|------|----------|------------------|-------------------------------|----------------------------|
| Linear Ad | Linear / in-stream | Full video pane (16:9 preferred; 21:9 admissible). Interactive portion MAY extend beyond the pane if the publisher allows. | Pre-roll, mid-roll, post-roll. Standard durations 6 s, 15 s, 20 s, 30 s; short-form "bumper" 3–10 s; 60 s spots sparingly; "info-mercial" 1–5 min or longer. Interactive ads: 15–30 s compulsory portion, MAY extend on interaction. Engagement via player controls (CTV: remote / game controller; mobile: gesture). | "Linear Ad Format Guidelines" |
| Pause Ad | Non-linear / viewer-initiated overlay | Full screen (1920 × 1080, 16:9) **or** partial screen (600 × 600, 1:1) shown while content is paused. | Persists for the duration of the pause experience. Ends on viewer dismiss / resume / power-off / app exit, or device-initiated screensaver / shutdown. Display/static OR video/animated; videos MAY autoplay; ad MAY refresh — refresh rate / autoplay behaviour signalled in the bid request. Optional QR / remote-control interactivity. | "Pause Ad" |
| Menu Ad | Non-linear / UI-embedded | Inside the smart-TV or streaming app UI. Two placements: **Headline Banner** (full horizontal row, top of navigation or between tile rows; aspect ratios 2:3, 6:5, 16:9) and **In Menu Tile** (anywhere in the navigational UI; aspect ratio 16:9 or 3:9). Size is variable — IAB defines aspect ratios for scalability rather than fixed pixel sizes. | Display/static or video/animated. Duration depends on viewer or device behaviour (navigate-away / power-off / app-exit / screensaver / device shutdown). MAY be part of navigable slides; MAY have fixed duration and/or refresh rate; videos MAY autoplay or require explicit engagement — behaviour signalled in the bid request. Optional QR / remote-control interactivity. | "Menu Ad" |
| Squeezeback | Non-linear / content-adjacent (content resized, not covered) | Content is squeezed to ~60 % of 1920 × 1080 (or 25 % for the Double Box variants); the ad occupies the freed-up area. Four sub-placements: **L-Shape** (content upper-left or upper-right; ad across the bottom and right vertical bar); **Frame** (content centred; ad surrounds it); **Double Box Video** (content centre-left, ad centre-right, each ~25 % of screen); **Double Box Video + Background** (same as Double Box plus advertiser-branded background between the two boxes). Aspect ratio 16:9. Content reduction transition 1–2 s. | Display/static or video/animated; assets provided as a full-screen 1920 × 1080 underlay with a cut-out for the resized content. Variable length; minimum 10 s; duration signalled in the bid request. Default execution requires no audio, but the publisher MAY require audio (e.g. during a sports content lull). Optional QR / remote-control interactivity. | "Squeezeback" |
| Overlay | Non-linear / over-content (content NOT resized) | Ad creative placed on top of programming. Two sub-placements: **Corner Overlay** (~25 % of 1920 × 1080, generally in one of the four corners; MAY appear smaller / non-square if formatted for transparency) and **Lower Third Overlay** (~30 % of the screen, along the bottom; MAY appear smaller / non-square if formatted for transparency). Aspect ratio 16:9. | Display/static or video/animated. Variable length; minimum 10 s; duration signalled in the bid request. Default execution requires no audio. Optional QR / remote-control interactivity. | "Overlay" |
| In Scene Ads | Non-linear / in-content composite | Branded element composited into the programming itself (typically a virtual out-of-home billboard inside the scene — e.g. a billboard along a road in the content). Content is **not** resized or covered; the asset appears as part of the scene. Asset sizes: 9:16 (1080 × 1920), 4:3 (1280 × 960), 16:9 (1920 × 1080), Poster (840 × 400), Bulletin (1400 × 400). | Static image (JPG / PNG / GIF). 3D / CGI assets supported by some partners but require out-of-band coordination. No audio. **No interactivity** — the format is intentionally non-interactive, closer to a brand placement. Variable length; minimum 3 s "brand exposure duration". | "In Scene Ads" |
| Screen Saver Ad | Non-linear / device-initiated overlay | Full screen, 1920 × 1080, 16:9. Begins after a defined period of inactivity on the smart TV (OS / app-initiated, not viewer-initiated — this is the distinguishing factor from Pause Ad). | Display/static or video/animated. Persists for the screensaver duration. Ends on viewer dismiss / resume / power-off / app exit, or device shutdown. MAY refresh; videos MAY autoplay — refresh rate / autoplay behaviour signalled in the bid request. Default execution requires no audio. Optional QR / remote-control interactivity. | "Screen Saver Ad" |
| Companion Ad | Companion / wrap-around (master ad required) | Outside the video player (around or adjacent to it). Common dimensions: 300 × 250, 468 × 60, 300 × 100, 728 × 90, 300 × 60. | Display only — text, static image, rich media, or skin around the player. **No video, no audio.** Visible for the duration of the master ad and intended to leave residual visibility after the master completes. File size ≤ 200 kB (subject to IAB Creative Display Guidelines). Not available on CTV except as end cards. | "Video Companion Ad Guidelines" |

## Mapping to spec chapter 3

The spec's chapter 3 accepted layout vocabulary maps 1:1 to the
IAB-defined ad-type values per **R12** in
[`../context/03-requirements.md`](../context/03-requirements.md).
The spec-side identifier is a kebab-cased token derived from the
IAB canonical name and namespaced under
`urn:svta:dash:sgai-layout:2026` when used as a scheme URI fragment.

| IAB name | Spec-side identifier | Rationale |
|----------|----------------------|-----------|
| Linear Ad | `linear` | Baseline in-stream ad slot; already covered by MPEG-DASH 6th edition SGAI (`InsertPresentation` / `ReplacePresentation` / `ListMPD`). Spec uses `linear` to refer to the baseline path. |
| Pause Ad | `pause-ad` | Viewer-initiated overlay outside the ad break; requires non-linear extension. Identifier matches the IAB heading. |
| Menu Ad | `menu-ad` | UI-embedded placement; sub-placements (`menu-headline-banner`, `menu-in-tile`) MAY be enumerated as refinements when chapter 3 needs to distinguish them, but the top-level identifier is `menu-ad`. |
| Squeezeback | `squeezeback` | Content-resize-adjacent placement. Sub-placements (`squeezeback-l-shape`, `squeezeback-frame`, `squeezeback-double-box`, `squeezeback-double-box-with-background`) MAY be enumerated as refinements; top-level identifier is `squeezeback`. |
| Overlay | `overlay` | Over-content non-linear placement; the principal target of the non-linear extension this spec introduces. Sub-placements (`overlay-corner`, `overlay-lower-third`) MAY be enumerated as refinements. |
| In Scene Ads | `in-scene` | Composited-into-content placement. The IAB explicitly defines this format as non-interactive; the spec MUST honour that (no interaction-event carrier permitted for `in-scene`). |
| Screen Saver Ad | `screen-saver-ad` | OS/app-initiated overlay. Semantically close to `pause-ad` but with a different initiation actor; the spec keeps them distinct because the trigger surface and lifecycle differ. |
| Companion Ad | `companion-ad` | Wrap-around display ad accompanying a master ad. Not generally available on CTV (only as end card per IAB); chapter 3 carries it for completeness but flags the CTV restriction inline. |

### Notes for chapter 3 authors

- The IAB document explicitly removed the legacy "Instream" submission
  guidelines in the May 2026 release and redirects implementers to
  OpenRTB / AdCOM for placement-type semantics. Chapter 3 SHOULD cite
  the IAB redirect rather than restating Instream subtypes.
- The IAB document uses **OpenRTB `plcmt`** (defined in AdCOM) as the
  authoritative enumeration for digital-video placement types. The
  spec's chapter 3 layout vocabulary is **orthogonal** to `plcmt`:
  `plcmt` describes the inventory category sent in the bid request,
  whereas the layout vocabulary describes the on-screen rendering the
  Broadcaster permits. Both axes coexist in the final delivery
  pipeline.
- **Interactivity** in the IAB document is delegated to **SIMID**
  (Secure Interactive Media Interface Definition) for rich
  interactions and to **QR codes** (burned-in or dynamically composited)
  for simple call-to-action. Chapter 3 SHOULD NOT define a new
  interactivity envelope; per **R11** (no VAST dependency) and
  **R10** (no parallel layout standard), references to SIMID and QR
  codes belong in non-normative notes or annexes.
- **Companion Ad** is listed for completeness but the IAB document
  states companion ads are not available on CTV except as end cards.
  Chapter 3 MAY scope `companion-ad` to web / mobile placements only
  and explicitly note the CTV restriction.
- Sub-placements (e.g. `overlay-corner` vs `overlay-lower-third`) are
  proposed here as refinements the spec MAY adopt if a Broadcaster
  needs to constrain the rendering surface further than the top-level
  identifier allows. If chapter 3 opts for a flat enumeration, the
  sub-placements collapse into hints carried by ADS-supplied priority
  metadata (per **R5.5** / **R5.6**) rather than spec-level layout
  names.

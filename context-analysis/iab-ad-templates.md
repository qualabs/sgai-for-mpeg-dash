[GROUNDED_BY=iab-live-link]

# IAB ad-template catalogue — live mirror

**Source**: IAB Tech Lab — *Ad Format Guidelines for Digital Video and CTV*,
Final Release May 2026.
Google Doc:
https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e

**Fetch timestamp (UTC)**: 2026-09-25T19:26:09Z

**Fetch method**: `mcp__claude_ai_Google_Drive__read_file_content` against the
document ID above (authenticated Google Drive connector).

This file is a **live mirror** — a snapshot in time of the source document,
regenerated on every `build-all` invocation. The source updates independently
of this project, so this file MAY be stale between builds. It is consumed by
the spec build (chapter 3, ad-type vocabulary). Do not edit by hand; regenerate
by re-running `prompts/1-pre-spec/analyze-iab-ad-templates.prompt`.

---

## Accepted ad-type values

The source enumerates a **CTV Ad Portfolio** of seven entries — the Linear Ad
baseline plus six formats introduced by the 2025/2026 update (Pause, Menu,
Squeezeback, Overlay, In Scene, Screen Saver). Companion Ad is not part of the
CTV Ad Portfolio list but is normatively specified in its own section
(*Video Companion Ad Guidelines*) and is therefore carried as a row; the source
states companion ads that are not end cards are not available on CTV.

Named sub-variants inside Squeezeback (L-Shape, Frame, Double Box Video, Double
Box Video + Background) and Overlay (Corner, Lower-Third) are **visual
placements of one ad type**, not separate ad types — the source defines them
inside the single format's Creative Size / Placement rows. They appear in the
"Visual placement" column.

| Name | Category | Visual placement | Typical duration / interaction | Source paragraph / heading |
|------|----------|------------------|-------------------------------|----------------------------|
| Linear Ad | Linear, in-stream | Full video viewing pane during pre-roll / mid-roll / post-roll. Preferred aspect ratio 16:9; ultra-wide 21:9 less common. Viewer-initiated portion may fill the video viewing pane or extend beyond it if the publisher allows. | 6 / 15 / 20 / 30 s; "bumper" short-form 3–10 s; 60 s spots used sparingly; "info-mercial" 1–5 min or longer. Interactive ads 15–30 s compulsory portion, may continue indefinitely on viewer interaction. Skip and player controls negotiated with the publisher; viewer-initiated portion must provide a close control, plus a collapse button if the extended portion has expandable media. | "Linear Ad Format Guidelines" |
| Pause Ad | Non-linear, viewer-initiated (content paused) | Fullscreen 1920×1080 (16:9) or Partial Screen 600×600 (1:1) in the pause experience. | Persists for the pause experience. Ends on viewer dismiss / resume / power off / app exit, or device-initiated screen saver / timeout. Some refresh; videos may autoplay (refresh rate and autoplay behaviour signalled in the bid request). Default execution requires no audio. Optional QR code and TV-remote interactivity. | "Pause Ad" |
| Menu Ad | Non-linear, out-of-playback (platform UI) | Inside the TV / streaming platform UI — home screen or content navigation menu. Headline Banner (2:3, 6:5, 16:9) featured across an entire horizontal row, often the top of the navigation, sometimes between rows of tiles; In Menu Tile (16:9 or 3:9) anywhere in the navigational UI. Size variable, aspect ratios given for scalability. | Loads when the TV is turned on or when the user navigates to the hosting menu. Duration depends on viewer or device behaviour. Ends on navigate-away / power off / app exit, or device screen saver / timeout. Some are navigable slides; some have fixed duration and/or refresh rates; videos may autoplay or require engagement (described by the seller in the bid request). Default execution requires no audio. Optional QR code and TV-remote interactivity. | "Menu Ad" |
| Squeezeback | Non-linear, concurrent with content (content resized, not covered) | Content resized to share the frame; no content is covered — the stated distinction from Overlay. **L-Shape**: content 60% of 1920×1080, squeezed upper-left or upper-right, ad across the bottom and the vertical right bar. **Frame**: content 60%, squeezed to centre, ad surrounds it. **Double Box Video**: content and ad each 25%, content centre-left, ad centre-right. **Double Box Video + Background**: Double Box plus advertiser-branded background between the two boxes. Aspect ratio 16:9. Assets assumed provided in underlay format (full-screen 1920×1080 branded ad with a cutout for the content placement). | Not user initiated. Content reduction takes 1–2 s. Minimum duration 10 s; variable, signalled in the bid request. Content returns to full screen when the ad ends. Default execution requires no audio, but the publisher may signal that audio is required (e.g. a lull in sports content where the squeezeback becomes the focus). Optional QR code and TV-remote interactivity. | "Squeezeback" |
| Overlay | Non-linear, concurrent with content (content covered, not resized) | Over the playing content; content size is not reduced. **Corner Overlay**: 25% of a 1920×1080 screen, generally in one of the four corners; may appear to cover less and not adhere to a square shape if formatted for transparency. **Lower Third Overlay**: 30% of the bottom of a 1920×1080 screen, same transparency caveat. Aspect ratio 16:9. Often a banner or picture-in-picture execution. | Not user initiated. Minimum duration 10 s; variable, signalled in the bid request. Creative is no longer visible when the ad ends. Default execution requires no audio. Optional QR code and TV-remote interactivity via the remote control. | "Overlay" |
| In Scene Ads | Non-linear, composited into the content | Composited within the programming so it appears naturally in the scene; content is neither resized nor covered. Typically product placements or virtual out-of-home insertions — standardisation currently focuses on the out-of-home insertions (e.g. a billboard in the scene filled with branded content). Sizes: 9:16 1080×1920, 4:3 1280×960, 16:9 1920×1080, Poster 840×400, Bulletin 1400×400. Creative is static image (jpg, png, gif); 3D / CGI supported by some partners via direct arrangement. | Not user initiated. Minimum 3 s Brand Exposure Duration; variable. No sound. **No interactivity** — the format is closer to a brand placement and is meant not to read as an ad. | "In Scene Ads" |
| Screen Saver Ad | Non-linear, OS / app-initiated | Full screen 1920×1080, 16:9. | Begins after a defined period of inactivity on the smart TV. Ends on viewer dismiss / resume / power off / app exit, or device timeout / shutdown. Some refresh; videos may autoplay (signalled in the bid request). Default execution requires no audio. Optional QR code and TV-remote interactivity. | "Screen Saver Ad" |
| Companion Ad | Companion, outside the player | Display ad wrapping the video experience — text, static image, rich media, or skin alongside or surrounding the player. Dimensions should fit the publisher's display placement; common sizes 300×250, 468×60, 300×100, 728×90, 300×60. File size 200 kB for most ads. | Sustained visibility throughout the streaming video experience, leaving a reminder after the linear or nonlinear component completes. Always served with a master (linear or nonlinear) ad. **No video or audio allowed** in the companion unit. Companion ads that are not served as end cards are not available on CTV. | "Video Companion Ad Guidelines" (definition also in "Linear, Nonlinear & Companion Ads") |

### Notes on the catalogue

- The source lists the portfolio entry as "Screen Ssaver Ad" (typo in the CTV
  Ad Portfolio bullet list); the section heading spells it "Screen Saver Ad".
  The heading spelling is used as the canonical name in the table.
- The source states the portfolio "is not comprehensive of all CTV
  experiences" and explicitly does not further define executions inside a
  linear pod slot.
- Interactivity is orthogonal to the ad type. The source describes it in
  separate sections (*Interactivity*, *QR Codes*) and recommends SIMID
  (VAST 4.2+) over the VPAID standard it replaces; QR codes may be burned
  into the creative, generated sell-side, or made dynamic under SIMID.
  Interactivity flavours are not ad types and are not enumerated as such.
- Digital Video Placement Types are deferred by the source to the OpenRTB
  `plcmt` attribute and the AdCOM enumeration; they are a buying-side
  taxonomy, not an ad-type taxonomy, and do not produce rows here.

## Mapping to spec chapter 3

Spec chapter 3 does **not** accept the whole IAB catalogue. Per **R12** in
[`../context/03-requirements.md`](../context/03-requirements.md), this edition
supports an explicit, **closed** subset of four IAB ad types, all rendered on or
within the video surface; anything rendered in the player chrome or the
application UI is out of scope. The enumeration is edition-scoped by design — an
IAB type published later does not enter scope automatically.

The spec-side identifiers are the layout tokens R12 enumerates, each mapped 1:1
to an IAB ad type or IAB visual placement (R12.2). The one value with no IAB
counterpart is the optional `custom` overlay layout of **R39**; it is not an
IAB ad type and therefore has no row below.

| IAB ad-type (verbatim) | Spec chapter 3 value(s) | Rationale |
|------------------------|-------------------------|-----------|
| Linear Ad | `linear` | Accepted. Full-viewport takeover of the primary content surface for the slot. Pre-roll, mid-roll and multi-ad breaks are timing positions of the one type; the full-screen takeover fallback (UC-09) is a placement of `linear`, not a separate type. |
| Overlay | `overlay`, `overlay-corner`, `overlay-lower-third` | Accepted. `overlay-corner` maps IAB *Corner Overlay*, `overlay-lower-third` maps IAB *Lower Third Overlay*; a plain overlay with no named placement is the base `overlay`. Which corner is not a token (R10.1, R10.3). |
| Squeezeback | `squeezeback-l-shape-upper-left`, `squeezeback-l-shape-upper-right`, `squeezeback-double-box`, `squeezeback-double-box-background` | Accepted. The two L-shape tokens map IAB *L-Shape* in its two orientations (upper left / upper right, R27); the double-box tokens map IAB *Double Box Video* and *Double Box Video + Background* (R26). The token carries the primary-content region because the IAB defines no field that does (ADR 0014). IAB *Frame* is not among the enumerated placements. |
| Pause Ad | `pause-fullscreen`, `pause-partial` | Accepted as the `pause` type, but bare `pause` is not an admissible layout value: R12 splits it into the IAB *Fullscreen* and *Partial Screen* placements so a Publisher can admit one and exclude the other in `@allowedLayouts`, and so R21's surface choice is determined. |
| Menu Ad | — (out of scope) | Rendered in the platform UI (home screen, content menu), not on the playing or paused video. Named explicitly as out of scope in R12. |
| Screen Saver Ad | — (out of scope) | OS / app-initiated after inactivity, off the video surface. Named explicitly as out of scope in R12. |
| Companion Ad | — (out of scope) | Rendered outside the player. Named explicitly as out of scope in R12 (companion / multi-screen ads). |
| In Scene Ads | — (out of scope) | Not in R12's closed supported set. The creative is composited into the content upstream of the Player rather than presented as a Player-side ad surface, and the format carries no interactivity. Because the set is closed, it is out of scope without a separate exclusion clause. |

R12.4 binds each accepted layout to the spatial bound the IAB declares for it
(e.g. Corner Overlay no more than 25% of the frame, Squeezeback L-Shape primary
content 60% of the frame), by normative reference rather than by re-declaring
dimensions MPD-side — see
[`../.project/decisions/0001-defer-to-iab-ctv-for-spatial-caps.md`](../.project/decisions/0001-defer-to-iab-ctv-for-spatial-caps.md).
Those bounds are traceable to the "Visual placement" column above.

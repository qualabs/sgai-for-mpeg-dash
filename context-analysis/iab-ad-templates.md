[GROUNDED_BY=iab-live-link]

# IAB ad-template catalogue — live mirror

**Source**: IAB Tech Lab — *Ad Format Guidelines for Digital Video and CTV*
(Final Release May 2026).
Google Doc:
https://docs.google.com/document/d/17JXFhHWWX1SVD3s2vMTMO-bvvj9XXK5e

**Fetch timestamp (UTC)**: 2026-05-28T02:20:00Z

**License**: Creative Commons Attribution 3.0 (per IAB doc footer).

This file is a **live mirror** — a snapshot in time of the source document,
regenerated on every `build-all` invocation. It is consumed verbatim by
the spec build (chapter 3, Terms & ad-type vocabulary). Do not edit by
hand; instead regenerate by re-running
`prompts/1-pre-spec/analyze-iab-ad-templates.prompt`.

---

## Accepted ad-type values

The IAB *Ad Format Guidelines for Digital Video and CTV* enumerates one
linear baseline plus six non-linear CTV ad portfolio formats. The
"Squeezeback" and "Overlay" entries each enumerate sub-variants of
visual placement that are normatively listed in their source tables; we
keep the canonical IAB names as separate rows because the visual
placement and creative size differ materially. "Companion ad" is
explicitly excluded from CTV per the IAB doc ("Companion ads, that are
not served as end cards, are not available on CTV.") but is included as
a row because it is a normative ad-form in the broader Digital Video
catalogue.

| Name | Category | Visual placement | Typical duration / interaction | Source paragraph / heading |
|------|----------|------------------|--------------------------------|----------------------------|
| Linear Ad | in-stream | Full viewport during pre-roll / mid-roll / post-roll (16:9 preferred, 21:9 accepted) | 6 / 15 / 20 / 30 s; "bumpers" 3–10 s; up to 60 s; "infomercial" 1–5 min. Interactive variants 15–30 s mandatory + indefinite on engagement. Skip & controls publisher-negotiated. | "Linear Ad Format Guidelines" |
| Pause Ad | non-linear, out-stream | Fullscreen 1920×1080 or partial 600×600 overlay shown while content is paused | Persistent for the duration of the pause; ends on resume / dismiss / app exit / screensaver. Optional QR / remote interactivity. Audio off by default. | "Pause Ad" |
| Menu Ad | non-linear, out-stream | Inside TV/streaming UI (home screen, content menu). Headline Banner (2:3, 6:5, 16:9) or In-Menu Tile (16:9 or 3:9) | Variable; tied to menu navigation. May autoplay video. Optional QR / remote interactivity. Audio off by default. | "Menu Ad" |
| Squeezeback | non-linear, in-content (concurrent, content resized) | Content squeezed to share screen with the ad. Variants: L-Shape (content 60%, ad spans bottom + vertical right bar), Frame (content centred, ad surrounds), Double Box Video (content + ad each 25%, left/right), Double Box Video + Background (Double Box plus advertiser-branded background) | Minimum 10 s; variable. Content reduction takes 1–2 s. Audio off by default; publisher may request it. Optional QR / remote interactivity. | "Squeezeback" |
| Overlay | non-linear, in-content (concurrent, content not resized) | Over content. Variants: Corner Overlay (25% of 1920×1080, one of four corners) and Lower-Third Overlay (30% of bottom strip). 16:9. | Minimum 10 s; variable. Audio off by default. Optional QR / remote interactivity. | "Overlay" |
| In Scene Ads | non-linear, in-content (composited) | Composited into the scene as a virtual out-of-home insertion (billboard, poster, bulletin). Resolutions 9:16 1080×1920, 4:3 1280×960, 16:9 1920×1080, Poster 840×400, Bulletin 1400×400 | Minimum 3 s brand exposure; variable. No audio. No user interactivity (closer to product placement). | "In Scene Ads" |
| Screensaver Ad | non-linear, OS/app-initiated | Fullscreen 1920×1080 after device inactivity | Persistent until viewer / device dismiss. Optional QR / remote interactivity. Audio off by default. May refresh; video may autoplay. | "Screen Saver Ad" |
| Companion Ad | non-linear, out-of-player | Display/static/rich-media bands wrapping the player (300×250, 468×60, 300×100, 728×90, 300×60) | Sustained visibility throughout the video session. No audio / video allowed inside the companion. Not available on CTV except as end-cards. | "Video Companion Ad Guidelines" |

### Notes on the catalogue

- The IAB doc identifies the six non-linear CTV formats (Pause, Menu,
  Squeezeback, Overlay, In Scene, Screensaver) as the *standardisation
  scope* of the 2026 release. The Linear Ad row is the baseline that
  every player already supports; it is included so that the spec
  chapter 3 can normatively reference one ad-type identifier for the
  linear case as well.
- Interactivity (SIMID, QR codes, remote-control gestures) is
  orthogonal to the ad-type and is described in a separate IAB section
  (*Interactivity* and *QR Codes*); the spec chapter 3 does not enumerate
  interactivity flavours as ad-types — they are layered on top of any
  of the rows above.
- Variants inside Squeezeback and Overlay (L-Shape, Frame, Double Box,
  Corner, Lower-Third) are *visual placements* of the same ad-type, not
  separate ad-types. They are listed in the "Visual placement" column.

## Mapping to spec chapter 3

The spec chapter 3 ("Terms, definitions, abbreviations") MUST include a
normative section that enumerates the accepted ad-type values consumed
by chapter 5 (Syntax) — specifically by the `@adType` (or equivalent)
attribute on non-linear ad descriptors. The spec MUST NOT invent new
identifiers; it MUST adopt the IAB names verbatim, kebab-cased for XML
attribute hygiene.

| IAB ad-type (verbatim) | Spec-side identifier (`@adType` value) | Rationale |
|------------------------|----------------------------------------|-----------|
| Linear Ad | `linear` | Baseline; one identifier suffices for the linear case since the variations (pre-roll / mid-roll / post-roll, bumper, infomercial) are timing & duration metadata, not ad-type distinctions. |
| Pause Ad | `pause` | One-to-one mapping. The fullscreen vs partial-screen sub-variant is a visual-placement attribute carried separately. |
| Menu Ad | `menu` | One-to-one mapping. Headline Banner vs In-Menu Tile is a visual-placement attribute. |
| Squeezeback | `squeezeback` | One-to-one mapping. L-Shape / Frame / Double Box / Double Box + Background are visual-placement attributes (the Player picks the rendering layout based on the candidate's declared placement and the local device class). |
| Overlay | `overlay` | One-to-one mapping. Corner Overlay vs Lower-Third Overlay is a visual-placement attribute. |
| In Scene Ads | `in-scene` | One-to-one mapping. Composited / out-of-home virtual signage is a single ad-type; resolution & aspect-ratio variants are carried as separate media-fragment attributes. |
| Screensaver Ad | `screensaver` | One-to-one mapping. OS/app-initiated trigger is normative for the ad-type. |
| Companion Ad | `companion` | One-to-one mapping. CTV restriction (end-card only) is a conformance constraint enforced in chapter 4, not a separate ad-type. |

Spec chapter 3 MUST cite this file (live mirror) as the authoritative
source for accepted ad-type values, and MUST state that any ad-type
identifier not in this table is non-conformant with this spec.

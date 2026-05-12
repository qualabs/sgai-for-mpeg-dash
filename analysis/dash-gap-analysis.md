[GROUNDED_BY=notebooklm]

# MPEG-DASH 6th Edition — Gap Analysis vs SGAI Requirements

Authoritative claims verified against ISO/IEC 23009-1 (MPEG-DASH 6th
edition, FDIS) via the "Streaming Protocols — DASH, HLS, C2PA, DRM"
NotebookLM notebook. Claims tagged `[inferred]` could not be verified
against the notebook in this pass and rely on the model's prior
knowledge of DASH 6th edition; reviewers SHOULD double-check those
against the canonical text before publication.

## 1. Scope

This document compares the SGAI requirements R1..R13 in
`../spec/03-requirements.md` against the capabilities of MPEG-DASH
6th edition (ISO/IEC 23009-1:2025) and identifies the gaps the norm
must close.

**In scope**:

- The SGAI primitives introduced in DASH 6th: `InsertPresentation`,
  `ReplacePresentation` (§5.16.3), the ListMPD profile (§8.14), the
  Single-Period Static Profile (§8.15), the callback event scheme
  `urn:mpeg:dash:event:callback:2015` (§4.7 / §5.10.4.5), the
  `UrlParamInfo` descriptor (§I.4).
- The extension rules that govern ignore-if-unknown for new
  constructs (R1).
- The non-linear ad scenarios (UC-03, UC-04, UC-05) that DASH 6th
  does not address natively.

**Out of scope**:

- DRM, encryption, segment-level retry, DASH-IF interop profiles
  outside the SGAI primitives.
- Internal DSP/SSP behaviour upstream of the ADS.
- IAB ad-format catalogue content (mirrored separately in
  `../analysis/iab-ad-templates.md`).

## 2. Coverage matrix

Cell legend: **full** = DASH 6th already satisfies the R end-to-end;
**partial** = DASH 6th partially satisfies it but the SGAI norm has
to fill the rest; **gap** = DASH 6th does not address the R at all
and the SGAI norm has to add it; **N/A** = the R is governance and
the comparison is not meaningful.

| Req | DASH 6th capability | Coverage | What's missing |
|-----|---------------------|----------|----------------|
| R1 — ignore-if-unknown, legacy degradation | DASH 6th defines extension points (open content model on `Period`, `AdaptationSet`, `EventStream`, etc.) and the `Event@schemeIdUri` ignore-if-unknown rule for unrecognised event schemes. | full (for linear baseline) / partial (for new non-linear constructs) | The norm has to demonstrate per construct that each new element/attribute/scheme sits at a DASH extension point whose ignore-if-unknown behaviour is already defined. The `07-backward-compat-checklist.md` is the auditing tool. |
| R2 — actor roles | DASH 6th cleanly separates Player (consumes MPD, talks to ADS, validates and renders) from Broadcaster (publishes MPD) from ADS (returns resolution document). `InsertPresentation` / `ReplacePresentation` express the Broadcaster's intent; the Player enforces; the ADS is unconstrained by `@maxDuration` semantics. | full | None. The actor separation pre-exists in 6th edition; the SGAI norm inherits it. |
| R3 — device classes (D1..D5) | DASH 6th is device-class-agnostic — there is no `<DeviceProfile>` or capability descriptor in the manifest. The Player is implicitly the device-capability authority. | partial | The norm has to enumerate D1..D5 explicitly and define per-class expected behaviour for each non-linear ad type. Pure DASH machinery does not surface device classes. |
| R4 — Broadcaster-declared max slot, Player-enforced | `InsertPresentation` and `ReplacePresentation` both carry `@maxDuration` (§5.16). For ListMPD, §5.16.5 mandates the Player terminates at the cap if the cumulative Period duration would exceed it. The ADS is not bound by the cap. | full (linear) / gap (non-linear overlay duration cap) | DASH 6th has no construct that expresses "overlay max display duration" on a non-linear slot. The norm has to introduce one (probably an attribute on the new non-linear SGAI event), with R4-style enforcement semantics restated for overlay windows. |
| R5 — device-aware ad selection | DASH 6th `ListMPD` does not carry per-candidate form metadata (it is a playlist of MPDs, not a candidate set). Selection happens **upstream** inside the ADS. | gap | The norm has to introduce a new resolution document for non-linear slots that carries (a) multiple renderable forms per candidate, (b) admissible layouts per form, (c) optional ADS priority hints. The intersection-of-three (device caps × `@allowedLayouts` × hints) selection logic is new. |
| R6 — tracking carrier | The callback event scheme `urn:mpeg:dash:event:callback:2015` (§4.7 / §5.10.4.5) is the established carrier for tracking beacons in linear sub-MPDs. Application-level VAST metadata (ClickThrough, AdSystem, AdTitle, UniversalAdId) has no native field in DASH 6th and is conveyed via vendor namespaces or sidecar — confirmed against the 6th edition source. | full (in-band beacons) / partial (application-level metadata) | The norm has to (a) require reuse of the callback scheme for non-linear tracking under R13, (b) declare a vendor-namespace convention for app-level metadata, (c) define quartile semantics anchored to the Broadcaster-declared overlay window rather than the candidate's intrinsic duration. |
| R7 — ADS-returned order | DASH 6th `ListMPD` declares an ordered sequence of Periods; the Player plays them back-to-back in declared order. The drop-before-play / trim-during-play semantics are not normatively spelled out — they emerge from §5.16.5 trimming behaviour. | partial | The norm has to formalise drop-before-play (R7.3) and the no-reorder/no-dedup obligation (R7.4) — these are inferred from DASH 6th's trim rule but not stated as Player obligations there. |
| R8 — justify additions | N/A (governance). | N/A | The norm authoring process MUST enforce this, not DASH. |
| R9 — minimise net new constructs | N/A (governance). | N/A | Same. |
| R10 — no parallel layout system | DASH 6th has no layout system. The norm's R10 is an architectural choice (defer to HTML5/CSS), not a gap. | N/A (architectural) | The norm has to state R10 prescriptively in chapter 5 (Syntax) when defining overlay placement attributes — they reference HTML/CSS classes, not pixel positions. |
| R11 — no VAST dependency | DASH 6th does not depend on VAST. The Player ↔ ADS interface is `ListMPD`, an XML document with no VAST semantics. VAST appears only on the ADS-internal upstream side (DSPs etc.). | full | None for the runtime contract. The norm must keep VAST out of normative chapters (informative annex only — `R11.3`). |
| R12 — IAB owns ad types | DASH 6th does not define ad types at all (it carries presentations, not ad-type taxonomy). | gap (by design) | Chapter 3 of the norm MUST source ad-type values from the IAB live document (mirrored in `../analysis/iab-ad-templates.md`). The norm itself MUST NOT invent ad-type names. |
| R13 — non-linear tracking semantics | DASH 6th's callback event scheme is the linear-baseline tracking mechanism. Non-linear quartile semantics anchored to a Broadcaster-declared overlay window are not addressed (linear quartiles anchor to the candidate's duration). | gap | The norm has to specify (a) impression beacon at overlay-visible instant, (b) quartiles timed against the overlay window not the ad's internal duration, (c) tracking stops at trim boundary if R4 trims early, (d) no new tracking scheme — reuse callback. |

## 3. Gaps detail

### Gap G-R3 — device-class enumeration

DASH 6th does not enumerate device classes. The norm has to define
D1..D5 (1-or-2 decoders × image/HTML/no overlay capability) and, for
each combination of device class and non-linear ad type, the expected
Player behaviour. This lives in chapter 7 of the norm (Expected
behaviour per scenario) and is sourced verbatim from
`../spec/04-use-cases.md`.

### Gap G-R4 — overlay max display duration

`InsertPresentation` / `ReplacePresentation` carry `@maxDuration` for
linear slots. For non-linear (overlay) slots, the norm has to
introduce an analogous attribute on the new non-linear SGAI event,
with the same Broadcaster-declares / Player-enforces semantics. The
Player MUST stop rendering the overlay at the cap even if the ad's
internal duration is longer.

### Gap G-R5 — multi-form / multi-layout candidate carrier

The DASH 6th `ListMPD` profile does not express "candidates with
multiple renderable forms". `ListMPD` is a *playlist of MPDs* —
selection has already happened upstream inside the ADS. For
non-linear ad slots the norm needs a different resolution document
shape: a *candidate set*, where each candidate carries one or more
renderable forms (video / image / HTML), one or more admissible
layouts (from the IAB-defined vocabulary), and optional ADS-supplied
priority hints across both dimensions.

The norm has to decide between (a) extending `ListMPD` to make Period
entries carry alternative-form metadata, (b) introducing a parallel
*OverlayList* resolution document with the same top-level structure
but a different per-Period shape, or (c) reusing `ListMPD` as a thin
wrapper and pushing the candidate-set semantics into the sub-MPDs.
The candidate-comparison is a chapter-5 (Syntax) decision; the
default reuse posture (R9) favours (a) or (c) over (b).

### Gap G-R6.app — application-level metadata carriers

VAST application-layer metadata (`ClickThrough`, `AdSystem`, `AdTitle`,
`UniversalAdId`) has no native DASH 6th carrier. Production ADS
adapters carry it via vendor-namespaced attributes or sidecar JSON.
The norm has to declare a normative convention: at minimum, require
that vendor-namespaced metadata sits under the Qualabs (or future
SVTA) namespace per `06-naming-and-namespaces.md`, and that legacy
Players safely ignore unknown namespaces (R6.5).

### Gap G-R13 — non-linear quartile anchor

Linear tracking quartiles anchor to the candidate's intrinsic
duration. For non-linear, the anchor MUST be the Broadcaster-declared
overlay window (`@maxDuration` on the non-linear slot). If R4 trims
the overlay before all quartiles fire, R13.3 mandates the Player
stops firing beacons at the trim boundary. This re-targeting of
quartile semantics is new and the norm has to spell it out alongside
the carrier (which is unchanged — same callback scheme as linear).

### Gap G-R5.UC-04 — hybrid linear+overlay decision

UC-04 has two candidates returned independently (linear + overlay).
The Player on device classes D3/D4 has to decide whether the overlay
portion is renderable on top of a linear ad's video on a single-
decoder device. UC-04 itself flags this as an open question; the
norm has to resolve it (the conservative default per R2 is "decline
the overlay portion if the device can't cleanly composite over a
linear ad").

### Gap G-R5.UC-05 — pause-ad video form on single-decoder

UC-05 raises whether single-decoder devices (D3/D4) can re-task the
decoder to play a video form on top of a paused primary frame. The
spec's conservative default is "skip the video form on single-decoder
devices in this scenario"; the norm should keep this default and
flag it for the WG.

## 4. Reuse opportunities (R9)

DASH 6th's machinery covers more of SGAI than naive reading suggests.
The norm SHOULD reuse rather than introduce, in these places:

- **Tracking carrier**: reuse `urn:mpeg:dash:event:callback:2015`
  end-to-end. R13.4 makes this normative for non-linear; the linear
  baseline already uses it. No parallel tracking scheme.
- **ListMPD top-level structure**: keep `MPD@type="list"` and
  `urn:mpeg:dash:profile:list:2024` as the carrier even for non-linear
  resolution documents. The candidate-set semantics can be expressed
  inside Periods via extension elements rather than via a new top-
  level profile URI.
- **`ImportedMPD` linkage**: reuse `ImportedMPD@uri` and
  `@earliestResolutionTimeOffset` to point at per-form sub-MPDs. The
  Single-Period Static Profile (§8.15) already constrains imported
  MPDs to a single Period, which matches the candidate-form model
  cleanly.
- **Callback event scheme on sub-MPDs**: reuse for impression / start
  / quartile / complete on non-linear ads.
- **`UrlParamInfo` descriptor (§I.4)**: reuse for ADS request
  parameterisation on non-linear slots too — the state vocabulary
  (e.g. `$urn:mpeg:dash:state:video$`) does not need to be extended
  for the baseline.
- **MPEG-DASH event scheme URN convention**: use the same year-pinned
  URN pattern, but under the SVTA namespace per
  `06-naming-and-namespaces.md` — `urn:svta:dash:<construct>:<year>`.
- **R7 ordering semantics**: inherit from `ListMPD`'s declared
  Period order. The drop-before-play / trim-during-play obligations
  are codified on top of this baseline.

## 5. Open questions

The following items need WG input or further research before the norm
publishes a final spec:

1. **Schema choice for candidate-set (G-R5)**: extend `ListMPD`
   Period entries vs introduce a parallel `OverlayList` resolution
   document. Default reuse posture (R9) and the SVTA WG's likely
   preference need a decision. Pin a candidate construct in chapter 5
   and validate against `07-backward-compat-checklist.md`.
2. **Form-priority schema (G-R5)**: how the ADS expresses form-level
   priority — ranked list, per-form `@priority` attribute, both?
   UC-03 flags this explicitly.
3. **Layout swap on the Player (G-R5)**: whether the Player can
   promote a candidate's nominal layout (e.g. banner → side-by-side
   because the device can't do banner) without the Broadcaster
   declaring side-by-side in `@allowedLayouts`. UC-03 flags this; the
   R2-clean answer is no.
4. **Pre-fetch on pause-ad (G-R5.UC-05)**: whether the Player MAY
   pre-fetch pause-ad candidates speculatively at manifest-load
   versus deferring the ADS call to the moment of pause. Latency vs
   targeting-freshness trade-off.
5. **Hybrid overlay on single-decoder (G-R5.UC-04)**: whether D3/D4
   MUST always decline the overlay portion of a hybrid break, or
   whether the Player MAY composite an HTML/image overlay on top of a
   linear ad's video on a device with HTML/image overlay surfaces.
6. **D5 ADS call (R3 / privacy / impression accounting)**: whether
   the Player still issues the ADS request on D5 / other devices that
   will inevitably skip the opportunity, to support impression
   accounting and frequency-capping signals. UC-03 flags this.
7. **Tracking-only VAST `<Ad>` (I05.4)**: the silent-skip default
   that the linear interfaces doc currently follows could not be
   confirmed against the 6th edition source. Pin via WG decision and
   document in chapter 8 (Implementation notes).
8. **VAST 4.x version pin** [inferred]: the exact 4.x version the
   norm cites in its informative annex (4.0 / 4.1 / 4.2 / 4.3) needs
   pinning against IAB Tech Lab's spec page. The 6th edition source
   does not pin VAST versions definitively.

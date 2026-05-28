[GROUNDED_BY=notebooklm]

# DASH 6th edition gap analysis (SGAI for linear + non-linear ads)

This document compares the requirements in `../context/03-requirements.md`
against what MPEG-DASH 6th edition (FDIS ISO/IEC 23009-1:2025) provides,
and identifies the constructs the new SGAI specification must add or
extend. It is the bridge between the canonical context and the spec
build.

Grounding mode: NotebookLM was queried against the
`streaming-protocols-—-dash,-hls,-c2pa,-drm` notebook (notebook URL
ID `bb67e20c-9ad1-4a1d-a641-7c7d901f93cb`) for the load-bearing
DASH 6th claims about the §5.16 / §8.14 / §5.10 mechanics. Where the
notebook could not (or did not) confirm a specific section in the
sessions consulted for this build, the claim is tagged `[inferred]`
and grounded against the prior NotebookLM validation that
`../context/05-dash-linear-interfaces.md` already absorbed verbatim
(quoted there: *"The MPEG-DASH 6th edition standard does not define
any carrier fields within the MPD for application-level VAST metadata
such as Click-through URLs."*).

## 1. Scope

In scope:

- Compare the SGAI-relevant capabilities of MPEG-DASH 6th edition
  against the requirements R1..R26 in `../context/03-requirements.md`
  and the use cases UC-01..UC-10 in `../context/04-use-cases.md`.
- Identify the gaps the new spec must close (constructs, attributes,
  carriers, conformance rules).
- Surface reuse opportunities (existing DASH machinery the spec MUST
  extend before introducing new constructs, per R8 / R9).

Out of scope:

- Internal ADS or APS protocol design (R18 — opaque to the spec).
- VAST version pinning (R11 — VAST-version-agnostic).
- ABR, DRM, transport, low-latency CMAF tuning — orthogonal to SGAI.
- IAB ad-template enumeration — analysed separately in
  `iab-ad-templates.md`.

## 2. Coverage matrix — R × DASH 6th capability

Cells: **full** (DASH 6th covers it normatively), **partial** (covered
for linear / partially), **gap** (no native carrier — spec must add),
**N/A** (governance / document-level — orthogonal to DASH).

| R     | Theme                                                              | DASH 6th status |
|-------|--------------------------------------------------------------------|-----------------|
| R1    | DASH 6th compliance + ignore-if-unknown for legacy Players         | full (§5.2.1 foreign-namespace + per-scheme `Event` skip — DR-2 / DR-3) |
| R2    | Honour Publisher / ADS / APS / Player actor split                  | partial (§5.16 has Publisher/Player legs; APS and ADS are external; no actor enforcement at MPD level — R2 lives in spec text) |
| R3    | Diverse device classes                                             | N/A (governance — DASH does not model device capabilities) |
| R4    | Publisher-declared max slot duration, Player-enforced              | partial (`@maxDuration` on `InsertPresentation` / `ReplacePresentation`, trim mandated by §5.16.5; non-linear slot cap has no native equivalent) |
| R5    | Device-aware ad selection — ordered presentation options           | gap (no native construct for "ad candidate carrying multiple form+layout options"; ListMPD is a sequence of ads, not an ordered-options-per-ad set) |
| R6    | In-band tracking beacon carrier                                    | full (callback scheme `urn:mpeg:dash:event:callback:2015`, §4.7 / §5.10.4.5 — reusable verbatim) |
| R7    | Respect ADS-declared order                                         | partial (ListMPD Periods play in declared order, §8.14; drop-before-play / trim-during-play semantics for the cap need extension) |
| R8    | Justify additions / omissions                                      | N/A (governance — applies to spec authoring, not DASH) |
| R9    | Minimise net new constructs                                        | N/A (governance — applies to spec authoring, not DASH) |
| R10   | Defer layout to HTML5 / CSS                                        | N/A (governance — DASH carries no layout primitives) |
| R11   | No dependency on VAST                                              | N/A (DASH is VAST-agnostic by construction) |
| R12   | IAB-owned ad-type vocabulary                                       | N/A (governance — vocabulary lives in IAB) |
| R13   | ADS-directed tracking schedule (non-linear, relative times)        | partial (callback scheme covers the carrier; presentation-time-relative semantics need the spec to confirm relative-to-ad-presentation anchoring) |
| R14   | Sequential non-linear forms within a slot                          | gap (DASH 6th has no non-linear ad slot at all; no construct for sequencing forms within an overlay window) |
| R15   | Admissible creative carriers (video / image / HTML)                | gap for non-AV (DR-1 binds sub-MPD Representations to RFC 4337 mp4 set; image/HTML need a separate carrier via DR-6) |
| R16   | Pause-ad lifecycle bound to pause state                            | gap (no pause-ad construct) |
| R17   | Pause-ad priority over overlay                                     | gap (depends on R14 / R16 constructs) |
| R18   | ADS / APS API contracts not defined by spec                        | N/A (governance — DASH does not constrain external APIs) |
| R19   | Ad playback speed follows primary                                  | gap (DASH 6th `Period@duration` is presentation-time; no normative anchor that an ad's wall-clock follows primary playback speed for non-linear) |
| R20   | Overlapping same-family windows: first-window-wins fallback        | gap (DASH 6th defines no policy for overlapping non-linear opportunity windows; for linear, `InsertPresentation` / `ReplacePresentation` events are scheduled without an overlap-resolution rule) |
| R21   | Pause-ad forms are fullscreen                                      | gap (depends on R16 construct) |
| R22   | Single active non-linear form; no concurrent presentation          | gap (depends on R14 construct) |
| R23   | Application-level ad metadata carrier (ClickThrough, AdSystem, ...) | gap (the 6th edition validated via NotebookLM in `05-dash-linear-interfaces.md` defines no native field; conveyance is via vendor-namespaced extensions per DR-2 / DR-6(a)) |
| R24   | Non-AV creative asset carrier (RFC 4337 avoidance)                 | gap (DR-1 / DR-5 close the AdaptationSet axis; spec must route non-AV asset URLs through DR-6) |
| R25   | Pause-ad presentation-time freeze in live content                  | gap (depends on R16 construct; presentation-time freeze on pause is a Player-state concern DASH does not normatively bind) |
| R26   | Three-element layouts with background fill (side-by-side)          | gap (depends on R14 / R5 constructs; DASH carries no layout composition primitives) |

## 3. Gaps detail

The matrix surfaces seven structural gaps that the SGAI spec must close.
Each is described below with the missing capability and the minimal
extension footprint.

### G1 — No native non-linear ad construct (R14 / R16 / R20 / R21 / R22 / R25 / R26)

DASH 6th edition's ad-related machinery is `InsertPresentation` and
`ReplacePresentation` (§5.16) plus the List MPD profile (§8.14). Both
are **linear-only**: they describe what plays *instead of* or
*inserted into* the primary timeline. The spec carries no construct
for an ad that coexists with primary content — overlay, banner,
L-shape, side-by-side, pause-ad. The notebook session that grounded
this build returned no §5.16 / §8.14 / elsewhere construct that
addresses non-linear; the standard's `Alternative MPD Insertion /
Replacement` framing is substitutive by definition
[partial-inferred from the §5.16 grounding session].

What the spec must add (in new constructs under the SVTA Ads WG
namespace, per `../context/06-naming-and-namespaces.md`):

- An MPD-level event family analogous to `InsertPresentation` /
  `ReplacePresentation` but with the semantics "overlay this on top
  of, do not interrupt the primary" (governs R14, R20, R26).
- A pause-trigger window event family — declares a temporal window
  during which a viewer pause permits a pause-ad (governs R16, R17,
  R21, R25).
- An overlay / pause-ad **resolution document** analogous to ListMPD,
  carrying ordered presentation options per candidate (governs R5,
  R14, R22).

### G2 — No ordered-presentation-options carrier per ad candidate (R5)

DASH 6th edition's ListMPD (§8.14) sequences ads, one Period per
selected ad. There is no construct that lets a single ad candidate
carry multiple **renderable presentation options** (form + layout) as
an ordered list with document order = preference order — the model
R5 codifies. The Player needs this carrier so it can walk the options
top-down (R5.6) and render the first satisfiable one without the ADS
or APS holding a per-device matrix (R5.4).

What the spec must add: an option-list child on the per-candidate
construct (whether linear or non-linear), where each `Option` pairs
`form` and `layout` (R5.1). The order is XML document order, no
priority attribute (DP-1).

### G3 — Non-AV creative carrier (R15 / R24 — DR-1 / DR-5 chain)

DR-1 binds every Representation reached via `<ImportedMPD>` to the
SPS profile, which inherits §7.3 RFC 4337 — `video/mp4`, `audio/mp4`,
`application/mp4`. DR-5 extends the same restriction to inline
AdaptationSets under ListMPD-level Periods. The AdaptationSet /
Representation axis is therefore closed for HTML and image
creatives end-to-end. Non-AV ad asset URLs must be carried via one
of the DR-6 carriers (foreign-namespace open content, Event Stream
payload, or vendor descriptor), not as `@mimeType` on an
AdaptationSet.

What the spec must add: explicit DR-6 carrier selection per
construct in the per-construct backward-compat checklist (Item 8 of
`../context/07-backward-compat-checklist.md` already requires this).
The default carrier for one-fetch static assets is DR-6(a)
foreign-namespace open content; presentation-time-aligned payloads
go to DR-6(b) Event Stream.

### G4 — Application-level VAST metadata carrier (R23)

The MPEG-DASH 6th edition specification confirms (validated via
NotebookLM as already absorbed in `../context/05-dash-linear-interfaces.md`,
which quotes verbatim: *"The MPEG-DASH 6th edition standard does not
define any carrier fields within the MPD for application-level VAST
metadata such as Click-through URLs"*) that there is no native MPD
field for `ClickThrough`, `ClickTracking`, `AdSystem`, `AdTitle`,
`Advertiser`, or `UniversalAdId`.

What the spec must add: route these through DR-6(a) — vendor /
SVTA-namespaced extension elements under `urn:svta:dash:sgai:<year>`
(R23.1). Legacy clients discard the foreign-namespace subtree per
DR-3 — no impact on baseline parsing.

### G5 — Overlap-resolution policy for same-family opportunity windows (R20)

DASH 6th edition schedules `InsertPresentation` / `ReplacePresentation`
events by `presentationTime`, with §5.16.6 "On Receive Processing"
rules governing event updates (validated by the §5.16 NotebookLM
session for this build). The standard contains no normative rule
for what a Player does when two **same-family** ad opportunity
windows overlap in time — both linear and non-linear cases are
silent. R20 fills the gap with first-window-wins-with-fallback.

What the spec must add: a chapter that states the R20 rule
normatively for the three families (linear, overlay, pause) and a
test case in chapter 10 modelled on UC-07.

### G6 — Wall-clock vs presentation-time semantics for non-linear ads (R19 / R25)

DASH 6th's timing model is presentation-time; `Period@duration`
expresses presentation-time duration. For non-linear ads that share
the screen with primary content played at a non-1x speed, the
**wall-clock** on-screen duration is `presentation_time_duration /
playback_speed`. DASH has no normative anchor that this derived
value is what the Player uses for cap enforcement against the slot's
declared display window. R25's pause-ad presentation-time freeze
guarantee in live content is a similar concern — the Player must
freeze its presentation time inside the pause-ad window even while
the live edge advances [inferred from `context/03-requirements.md`
R25 — no §5.x rule in DASH 6th binds Player presentation-time during
pause].

What the spec must add: a Player obligation paragraph in the
non-linear chapter, plus an explicit cross-reference to DASH's
presentation-time vs wall-clock model. The derivation is computed by
the Player; `duration` stays canonical (DP-1.2 single-source-of-truth).

### G7 — Layout composition for three-element layouts (R26)

R26's side-by-side / double-box layout puts three on-screen elements
(primary, ad, background fill). DASH 6th has no layout composition
primitives (and per R10, the spec must defer to HTML5 / CSS rather
than create them). The gap is not a DASH gap to close inside the
spec — it is a spec-text obligation: declare that the third element
is a **composition attribute of the slot / layout**, not an
alternative presentation option (R26.1), and that the Player
composites it via HTML5 / CSS (R10.1).

What the spec must add: an explicit attribute (likely on the overlay
slot's allowed-layout declaration in `urn:svta:dash:sgai:<year>`)
expressing the background-fill source — advertiser creative or
Publisher fallback — together with the device-class composition
rules from R26.3.

## 4. Reuse opportunities

The spec MUST reuse the constructs below before introducing new ones
(R9), and document the reuse decision per R8.

| Existing DASH 6th construct                                       | Reused for                                            | Notes |
|-------------------------------------------------------------------|-------------------------------------------------------|-------|
| `EventStream` + `<Event>` (§5.10)                                 | All new SGAI events (overlay slot, pause window)      | Standard authoring vehicle; legacy Players skip events whose `schemeIdUri` they don't recognise. |
| Callback event scheme `urn:mpeg:dash:event:callback:2015` (§4.7 / §5.10.4.5) | All ad tracking beacons (R6, R13)                     | No new tracking scheme per R13.4. Beacon URLs go in the `<Event>` `text()`. |
| `ListMPD` profile `urn:mpeg:dash:profile:list:2024` (§8.14)       | The linear resolution document baseline               | Already covers `<InsertPresentation>` / `<ReplacePresentation>` resolution. Non-linear borrows the "playlist of MPDs" structure but with overlay semantics. |
| `<ImportedMPD>` (§5.3.2.6)                                        | Per-ad sub-MPDs for video creatives                   | DR-1 binds sub-MPD to SPS — fine for video ads, blocked for non-AV. |
| `UrlParamInfo` descriptor (§I.4)                                  | APS resolution-request query parametrisation          | Player-side substitution of state-vocabulary variables; already in linear flow. |
| Foreign-namespace open content (§5.2.1)                           | All new SGAI-namespaced elements / attributes (DR-2)  | The single normative extension point. New constructs MUST live here. Legacy discards subtree (DR-3) — pick wrapping to control what legacy sees. |
| Vendor descriptors (§5.8.4.8 / §5.8.4.9)                          | Application-level ad metadata (R23) — alternative carrier | Choice between DR-6(a) and DR-6(c) is per-construct; descriptor-based has weaker readability vs SVTA-named element. |
| `InsertPresentation` (§5.16.3) — VOD-only                         | UC-01 (pre-roll on VOD) and UC-02 (mid-roll on VOD)   | Per §5.16.3, `InsertPresentation` "shall not appear if the MPD type is dynamic"; live content must use `ReplacePresentation`. The spec carries this constraint as a Publisher authoring rule. |
| `ReplacePresentation` (§5.16.4) — VOD and live                    | UC-01, UC-02 on live; UC-06 multi-ad break baseline   | `@returnOffset`, `@clipDuration`, `@startWithOffset` are exclusive to `ReplacePresentation` (§5.16.5). |
| `@maxDuration` trimming rule (§5.16.5)                            | R4 enforcement baseline for linear slots              | Validated via NotebookLM: *"If absent, the value is assumed to be infinity, in which case the current presentation resumes only when the alternative presentation terminates."* Non-linear slot cap reuses the same name and semantics. |
| `status="update"` lifecycle on Events (§5.16.4 / §5.16.6.2.4)     | Dynamic update of a running slot — useful for live ad-decision updates | NotebookLM grounded the verbatim rule: only `@maxDuration`, `@returnOffset`, `@clip` updates apply to a running event; `@url`, `@PRT` updates are ignored on already-running events. |

## 5. Open questions

The items below need WG input, further NotebookLM verification, or a
deliberate design decision before the spec text stabilises.

1. **Pause-trigger window vs `ReplacePresentation`** — UC-05's
   pause-ad is conceptually a window during which the Player MAY
   render an ad triggered by viewer action, not a timeline event the
   Player *reaches*. Can `EventStream` + a new `schemeIdUri`
   `urn:svta:dash:sgai-pause-trigger:<year>` (DR-2) carry this, or
   does the action-triggered nature require an Annex F-style profile
   extension (DR-4)? Default position: §5.2.1 carries it; DR-4 is
   rejected per DR-4's "cost not justified" guidance.
2. **Live presentation-time freeze (R25)** — DASH 6th does not
   normatively bind Player presentation-time behaviour during user
   pause in dynamic MPDs (the spec assumes timing follows wall
   clock). R25 introduces a Player obligation that freezes
   presentation-time inside the pause-ad window. Confirm with
   NotebookLM that no §5.x / §I.x rule conflicts with that
   obligation before the spec text goes out.
3. **Overlay resolution document shape** — should the overlay
   resolution document be a ListMPD variant (Periods + ImportedMPD,
   reusing §8.14) or a fully separate document type under the SVTA
   namespace? ListMPD reuse maximises R9 compliance but forces the
   non-AV creative cases through DR-6 carriers (and out of the
   AdaptationSet axis per DR-5). A separate document type
   pessimises R9. Default position: extend ListMPD; carry non-AV
   asset URLs via SVTA-namespaced child elements per DR-6(a).
4. **`UniversalAdId` carrier choice** — both DR-6(a) foreign-
   namespace and DR-6(c) vendor descriptor are admissible (R23). The
   choice is between a named element (`<svta:UniversalAdId
   idRegistry="..." value="..."/>`) and a descriptor
   (`<EssentialProperty schemeIdUri="urn:svta:dash:ad-id:<year>"
   value="..."/>`). Default position: named element under DR-6(a)
   for readability.
5. **`InsertPresentation` on dynamic MPDs** — UC-02 mid-roll on live
   content must use `ReplacePresentation`, not `InsertPresentation`
   (§5.16.3 forbids `InsertPresentation` for `MPD@type="dynamic"`).
   `context/05-dash-linear-interfaces.md` already documents this; the
   spec MUST surface it as a Publisher authoring rule in the chapter
   on slot mechanism choice.
6. **Empty / no-fill ListMPD policy** — `context/05-dash-linear-
   interfaces.md` flags that the industry-convention question for
   tracking-only VAST `<Ad>` (no `<MediaFile>`) — *silent skip vs
   VAST Error code 403* — could not be resolved against the 6th
   edition source. The non-linear spec MUST decide silently-skip vs
   surface-an-error and state it in the per-construct chapter. The
   ListMPD response is APS-internal policy under R18.2 — the spec
   may decline to normatively bind it.

## References

- `../context/01-intro.md` — document index
- `../context/02-actors.md` — Publisher / ADS / APS / Player
- `../context/03-requirements.md` — R1..R26
- `../context/04-use-cases.md` — UC-01..UC-10 (D1..D5 device classes)
- `../context/05-dash-linear-interfaces.md` — linear SGAI baseline
- `../context/06-naming-and-namespaces.md` — SVTA Ads WG namespace
- `../context/07-backward-compat-checklist.md` — per-construct R1 audit
- `../context/08-dash-extension-rules.md` — DR-1..DR-7 closed design space
- `../context/99-glossary.md` — terminology

### NotebookLM sessions consulted for this build

- Notebook: `Streaming Protocols — DASH, HLS, C2PA, DRM` (UUID
  `bb67e20c-9ad1-4a1d-a641-7c7d901f93cb`). Sessions: 2026-05-27.
- Verbatim quotes from those sessions used above:
  - §5.16.5: *"If absent, the value is assumed to be infinity, in
    which case the current presentation resumes only when the
    alternative presentation terminates."*
  - §5.16.6.2.4 (On Receive Processing): *"changes to attributes
    such as URL or PRT will not be applied to the running event,
    however any changes affecting changes to its playback duration
    and resumption point (i.e., @maxDuration, @returnOffset, @clip)
    will be applied and acted upon."*
- The application-level metadata absence claim is grounded against
  the prior NotebookLM validation captured verbatim inside
  `../context/05-dash-linear-interfaces.md` (the VAST → ListMPD
  conversion table): *"The MPEG-DASH 6th edition standard does not
  define any carrier fields within the MPD for application-level
  VAST metadata such as Click-through URLs."*

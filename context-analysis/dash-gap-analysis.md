# DASH 6th edition — Gap analysis vs SGAI requirements

> Grounding mode: `[GROUNDED_BY=spec-only]`. NotebookLM was reachable
> in the local library but the headless session timed out on page load
> across two attempts; this analysis fell back to the `context/` files
> as the authoritative source. The `context/` documents themselves
> cite DASH 6th sections that were previously validated against the
> ISO source via NotebookLM (see notes inside
> `../context/05-dash-linear-interfaces.md` and
> `../context/08-dash-extension-rules.md`), so the section anchors
> below are reliable. Claims that could not be re-verified live on
> this pass are tagged `[inferred]`.
>
> Vocabulary in this document follows RFC 2119 for normative terms
> (MUST / SHOULD / MAY).

This document compares each requirement in
[`../context/03-requirements.md`](../context/03-requirements.md)
against what **MPEG-DASH 6th edition (ISO/IEC 23009-1:2025, FDIS)**
provides natively. The goal is to identify, per requirement, whether
the baseline already satisfies it, partially satisfies it, leaves a
gap that the new spec MUST fill, or is out of scope for the baseline.
The output feeds the spec-build step: every `gap` and `partial`
becomes a candidate construct in `output/<date>-sgai-spec.md`, and
every `reuse` opportunity is a constraint on how those constructs
are introduced (per R9).

## 1. Scope

**In scope**

- Native DASH 6th edition mechanisms for ad insertion: §5.16
  Alternative MPD Insertion / Replacement Events (the linear SGAI
  baseline), §8.14 ListMPD profile (the resolution-document carrier),
  §5.10 Event Streams (incl. the §5.10.4.5 callback scheme), §5.2.1
  foreign-namespace open content (the extension surface), §5.8.4.8 /
  §5.8.4.9 vendor descriptor schemes, §5.3.2.6 / §8.15 / §7.3 chain
  binding `<ImportedMPD>` to SPS / RFC 4337, Annex F (non-ISO-BMFF
  delivery extension), §I.4 extended URL parameterisation.
- The three-actor model (Broadcaster / ADS / Player) per
  [`../context/02-actors.md`](../context/02-actors.md).
- The thirteen requirements R1..R13 in
  [`../context/03-requirements.md`](../context/03-requirements.md).
  R1..R10 are the original functional + governance set; R11..R13 are
  the later requirements (VAST-independence, IAB-owned ad-type
  definitions, non-linear tracking reuse) and are covered here for
  completeness — the build prompt's nominal `R1..R10` framing is
  understood as "every requirement currently in the requirements
  chapter".
- The seven use cases UC-01..UC-07 in
  [`../context/04-use-cases.md`](../context/04-use-cases.md), to the
  extent they discriminate between linear and non-linear behaviour.

**Out of scope**

- Server-side ad insertion / stitching (SSAI) — both the spec and
  this analysis are client-side.
- Post-roll slots, companion ads, multi-screen, native ads in the
  Player chrome — out of scope per the spec.
- VAST 4.x internal semantics beyond the linear `ListMPD` adapter
  mapping already described in
  [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md).
- DRM / authentication / token exchange — orthogonal layers handled
  by DASH-IF guidance.
- Internal ADS decisioning logic (targeting, frequency capping,
  brand safety, etc.).

## 2. Coverage matrix

Status legend:

- **full** — DASH 6th edition provides the capability directly; the
  SGAI spec just inherits and cites it.
- **partial** — DASH 6th provides part of the capability (typically:
  the linear half) but the requirement extends beyond what the
  baseline covers; the spec MUST add the missing half via an
  extension point per DR-1..DR-7 in
  [`../context/08-dash-extension-rules.md`](../context/08-dash-extension-rules.md).
- **gap** — DASH 6th has no native carrier for the capability; the
  spec MUST introduce one via DR-2 / DR-6 carriers.
- **N/A** — the requirement is a document-discipline obligation on
  the spec author (e.g. justify additions, do not recreate a layout
  system); DASH 6th has nothing to say about it. The matrix records
  these as N/A and treats them in the Gaps section only when DASH 6th
  shapes the obligation (e.g. R9 reuse opportunities exist).

| Req  | Sub-clauses                  | Capability                                                                                  | DASH 6th carrier / mechanism                                                                                                                                                      | Status   |
|------|------------------------------|---------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| R1   | R1.1                         | Legacy Player ignores unknown SGAI constructs and keeps playing primary content             | §5.2.1 foreign-namespace open content + §5.10 unknown-`schemeIdUri` skip + standard ignore-unknown-attribute rule                                                                  | full     |
| R1   | R1.2                         | Admissible extension points enumerated and bounded                                          | §5.2.1, §5.10, §5.8.4.8 / §5.8.4.9, Annex F (DR-2 / DR-4 / DR-6). §5.3.2.6 / §8.15 / §7.3 / RFC 4337 / §8.14 close off the `<ImportedMPD>` and ListMPD-Period paths (DR-1 / DR-5). | full     |
| R1   | R1.3                         | Spec MUST NOT alter pre-existing DASH 6th semantics                                         | DASH 6th allows additive extension only; no relaxation path                                                                                                                       | full     |
| R2   | R2.1                         | Broadcaster declares **linear** slot constraints (`@maxDuration`, etc.) in MPD              | §5.16.3 `<InsertPresentation>` / §5.16.4 `<ReplacePresentation>` attributes                                                                                                       | full     |
| R2   | R2.1                         | Broadcaster declares **non-linear** slot constraints (allowed layouts, concurrency cap)     | Not present in DASH 6th — overlay / pause-trigger semantics do not exist in §5.16                                                                                                 | gap      |
| R2   | R2.2                         | ADS produces a resolution document                                                          | §8.14 ListMPD (linear). No equivalent resolution document shape defined for non-linear opportunities.                                                                             | partial  |
| R2   | R2.3                         | Player validates ADS candidates against MPD constraints                                     | §5.16.5 mandates trim-at-cap for `@maxDuration`; broader validation conformance is not normatively specified `[inferred]`                                                         | partial  |
| R2   | R2.4                         | Every new mechanism expressible inside the three-actor contract                             | DASH 6th has no concept of the three-actor contract; satisfaction is on the spec author                                                                                           | N/A      |
| R3   | R3.1 / R3.2 / R3.3           | Spec enumerates device classes; Player produces a defined behaviour per (class × UC)        | DASH 6th has no device-class taxonomy for ad rendering; ABR addresses bandwidth/codec only                                                                                        | gap      |
| R4   | R4.1 / R4.2 / R4.3 / R4.5    | Broadcaster-declared max **linear** slot duration; Player trims at cap                      | §5.16 `@maxDuration` on `<InsertPresentation>` / `<ReplacePresentation>`; §5.16.5 mandates trimming                                                                                | full     |
| R4   | R4.1 / R4.2                  | Broadcaster-declared max **non-linear / overlay** display duration; Player trims at cap     | No native overlay duration attribute in DASH 6th                                                                                                                                  | gap      |
| R4   | R4.4                         | ADS MUST NOT be conformance-tested against the cap                                          | DASH 6th does not define an ADS conformance test; satisfied by silence                                                                                                            | full     |
| R5   | R5.1 / R5.5                  | ADS candidate carries one or more renderable forms (video / image / HTML) and rank hints    | ListMPD `<Period>` → `<ImportedMPD>` → SPS sub-MPD is RFC 4337-bound (DR-1); no native multi-form-per-candidate carrier                                                            | gap      |
| R5   | R5.2 / R5.3 / R5.6 / R5.7    | Player chooses best renderable form / skips candidates with no renderable form              | DASH 6th has no concept of form selection at the Player; behaviour must be specified by SGAI on the new constructs                                                                | gap      |
| R5   | R5.4                         | ADS not required to maintain a device-class matrix                                          | DASH 6th imposes no such requirement (silence is satisfaction)                                                                                                                    | full     |
| R6   | R6.1 / R6.2 / R6.3           | Carrier for in-band ad tracking beacons (impression / quartiles / complete)                 | §4.7 + §5.10.4.5 callback event scheme `urn:mpeg:dash:event:callback:2015`                                                                                                        | full     |
| R6   | R6.4                         | Carrier for application-level VAST metadata (`ClickThrough`, `AdSystem`, `AdTitle`, `UniversalAdId`) | No native DASH 6th field — confirmed in [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md) §VAST→ListMPD; vendor-namespaced extension required          | gap      |
| R6   | R6.5                         | Player safely ignores unknown namespaces on tracking-related extension elements             | §5.2.1 + DR-2 / DR-3 already provide this                                                                                                                                         | full     |
| R6   | R6.6                         | Non-AV ad asset URL MUST NOT be carried via `@mimeType` on AS/Rep reached through SPS chain | DR-1 / DR-5 close that path; DR-6 enumerates the three admissible carriers                                                                                                        | full     |
| R7   | R7.1 / R7.4                  | Player MUST play candidates in ADS-returned order                                           | §8.14 ListMPD `<Period>` sequencing is normative (a ListMPD is a playlist of MPDs)                                                                                                | full     |
| R7   | R7.2 / R7.3 / R7.5           | Player MAY drop candidates per R3 / R4; trim mid-rendering when actual length exceeds cap   | §5.16.5 covers trim-on-cap; "drop before play" semantics for unrenderable candidates is not in DASH 6th and must be specified by SGAI                                             | partial  |
| R8   | R8.1 / R8.2                  | Inline justification for each new construct / each deliberate omission                      | Author-discipline obligation on the spec                                                                                                                                          | N/A      |
| R9   | R9.1 / R9.2 / R9.3           | Reuse existing DASH machinery before introducing new constructs                             | DASH 6th provides §5.10 events, §5.2.1 foreign-namespace, §8.14 ListMPD, callback scheme — broad reuse surface                                                                    | N/A (high reuse potential — see §4) |
| R10  | R10.1 / R10.2 / R10.3        | Layout primitives deferred to HTML5 / CSS; no parallel layout standard                      | DASH 6th has no layout system; satisfied by reference to IAB / HTML5 / CSS                                                                                                        | N/A      |
| R11  | R11.1 / R11.2 / R11.3        | No dependency on VAST                                                                       | DASH 6th's Player-facing interface is `ListMPD`, not VAST; VAST is an ADS-internal concern                                                                                        | full     |
| R12  | R12.1 / R12.2 / R12.3        | Ad-type definitions sourced from IAB; no broadcaster-private layout names                   | DASH 6th does not enumerate ad types; satisfied by silence + reference                                                                                                            | N/A      |
| R13  | R13.1 / R13.2 / R13.3 / R13.4 | Non-linear tracking reuses linear baseline scheme; quartile beacons timed against overlay window | §4.7 + §5.10.4.5 callback scheme is the inherited carrier. Mapping quartiles to a Broadcaster-declared overlay window is new semantics layered on top.                            | partial  |

## 3. Gaps detail

The numbered gaps below are the points at which the spec MUST add
something the baseline does not provide. Each gap states the missing
capability, points to the admissible carrier from
[`../context/08-dash-extension-rules.md`](../context/08-dash-extension-rules.md),
and identifies the requirements it satisfies. Where the carrier
choice is open inside DR-6 (a / b / c), the gap notes both options;
the build prompt downstream picks one and records the rationale per
R8.

### G1. Non-linear ad opportunity signalling (R2.1, R3, R5)

**Missing**: A way for the Broadcaster to declare an ad opportunity
whose semantics are "ad runs **on top of** the primary content, the
primary keeps playing, the overlay disappears at a declared time".
DASH 6th §5.16 only defines `<InsertPresentation>` (splice-style,
pauses the primary) and `<ReplacePresentation>` (replace-style, the
primary's media time advances under the ad). Neither has overlay
semantics; both consume the screen.

**Carrier (admissible)**: A new event scheme URI of the form
`urn:svta:dash:sgai-overlay:<year>` (per
[`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)),
carried as a child element inside `<Event>` on an `<EventStream>` —
shape parallel to `<InsertPresentation>` and `<ReplacePresentation>`,
under the SVTA Ads WG namespace `urn:svta:dash:sgai:<year>` (DR-2,
§5.2.1 foreign-namespace open content). Legacy clients ignore the
event because the `schemeIdUri` is unknown; UC-07 is satisfied
verbatim.

**What the new construct MUST carry** (attribute set determined by
the requirements, not by DASH 6th):

- The ADS URL to resolve (mirrors §5.16 `@url`).
- A maximum overlay display duration `@maxDuration` (R4.1). The
  attribute name is reused verbatim from the linear baseline per the
  naming-consistency rule in
  [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)
  §Naming consistency.
- An `@earliestResolutionTimeOffset` (mirrors §5.16). Whether the
  unit is seconds (matching `<ImportedMPD>` §5.3.2.6.1) or
  `EventStream@timescale` units is open (see Q3 below) — the
  attribute name MUST be chosen so the unit is unambiguous at the
  call site (`06-naming-and-namespaces.md` §Naming consistency).
- The allowed-layouts set, the concurrency cap, and the
  IAB-vocabulary anchor (see G2).

**Why not extend `<InsertPresentation>` / `<ReplacePresentation>`**:
both have screen-take-over semantics baked into §5.16.3 / §5.16.4 —
the Player suspends the primary timeline. Overlay semantics keep the
primary running, so the event behaviour is incompatible. Per the
naming-consistency rule, reusing a name with different semantics is
explicitly forbidden — a new event name is required.

### G2. Broadcaster-declared overlay constraints — allowed layouts, concurrency cap (R2.1, R10, R12)

**Missing**: A way for the Broadcaster to declare, per overlay
opportunity:

- The set of allowed layout templates (banner, L-shape, side-by-side,
  sidebar, corner, etc., from the IAB CTV vocabulary referenced by
  R12).
- The maximum number of concurrent overlays during the slot.
- (Optional) Mutually-exclusive layout pairings.

DASH 6th has no native carrier for any of these — overlay layout is
not a DASH concept.

**Carrier (admissible)**: Child elements / attributes in the SVTA Ads
WG namespace placed inside the new overlay event element from G1
(§5.2.1 foreign-namespace, DR-2). Per R10 the **layout vocabulary**
itself is IAB-owned and referenced normatively — the SGAI spec
does not invent layout names; it only declares which IAB-named
layouts are permitted on this slot. Per R12.2, broadcaster
declarations MUST use names that map 1:1 to IAB ad-type values.

**Why not §5.8.4.x vendor descriptor**: descriptors (Role, Rating,
EssentialProperty, SupplementalProperty) are bound to
AdaptationSet / Representation / Sub-Representation placement and
inherit DR-5's RFC 4337 constraint. They are also single-`@value`
strings, which is awkward for a structured allowed-set + concurrency
cap + optional exclusions payload. Foreign-namespace child elements
under the event (DR-6 carrier (a)) are the natural fit.

### G3. Non-linear resolution document — overlay-friendly ListMPD shape (R2.2, R5.5)

**Missing**: A resolution-document shape that lets the ADS return,
for a non-linear opportunity, one or more ad candidates where each
candidate carries **multiple renderable forms** (video, image, HTML)
with optional priority hints — and where the Player picks one form
per device. The DASH 6th ListMPD profile (§8.14) does not provide
this shape: each `<Period>` references a single `<ImportedMPD>`
which is SPS-bound (DR-1), and the inline AS/Rep axis is RFC 4337-
bound (DR-5). There is no native multi-form-per-Period carrier.

**Carrier (admissible)**: Two non-mutually-exclusive options live
inside the DR-6 enumeration; the spec must pick one and justify per
R8:

- **(a) ListMPD-plus-extensions**: keep §8.14 ListMPD as the
  resolution document, but add a foreign-namespace child to each
  `<Period>` (DR-6 (a), DR-2) that declares the candidate's
  renderable forms (image URL, HTML URL, alongside the existing
  `<ImportedMPD>` reference for the video form). The Player walks
  the foreign child to pick the form. AV-only candidates degrade
  to the standard linear pattern. This keeps the §8.14 profile
  intact and inherits ListMPD `<Period>` ordering for R7.
- **(b) New non-linear resolution document**: a separate document
  shape under the SVTA Ads WG namespace, distinct from §8.14
  ListMPD. Bypasses §8.14 constraints but requires a new profile
  URI and a separate Player code path.

Option (a) is the lighter touch and aligns with R9. Open Q1 below
captures the trade-off.

Either way: an AV form on the candidate MUST be carried via
`<ImportedMPD>` to an SPS sub-MPD (DR-1) — that path is the only
native DASH carrier for AV ad payloads in a resolution document.
Non-AV forms (image, HTML) MUST be carried via DR-6 (a / b / c) per
R6.6 — never via `@mimeType` on an AS / Rep in the SPS / CMAF
chain.

### G4. Per-candidate priority hints across forms and across candidates (R5.5)

**Missing**: A way for the ADS to rank (i) candidates against each
other and (ii) forms within a candidate. DASH 6th has no
prioritisation field on `<ImportedMPD>` or anywhere else relevant in
the SPS / ListMPD profiles. The §I.4 `UrlParamInfo` descriptor does
not cover this; `<Role>` is qualitative (`main`, `alternate`), not a
numeric priority.

**Carrier (admissible)**: Attributes (`@priority`, or
`@rank` — naming open) on the foreign-namespace form-descriptor
element introduced in G3, under the SVTA Ads WG namespace
(§5.2.1 / DR-2). Carrying priority as an XML attribute on the
extension element keeps the carrier (a) under DR-6 and avoids a new
descriptor scheme.

The semantics — totally-ordered numeric rank vs ordered list vs
weighted — is an open spec design question (Q4 below). DASH 6th
does not constrain the choice.

### G5. Pause-triggered overlay event with a window of validity (R2.1, R3, UC-05)

**Missing**: A signalling shape that means "if the user pauses
between t1 and t2, an overlay ad is permitted". DASH 6th `<Event>`
fires at `presentationTime`. Pause is a Player-side input, not a
timeline marker; there is no native carrier for "Player input
condition + time window".

**Carrier (admissible)**: A new event scheme URI under
`urn:svta:dash:sgai-pause-trigger:<year>` (DR-2 / §5.10 / §5.2.1
combination). The event itself sits at a `presentationTime` with a
declared `duration` covering the window; the Player consults the
event set at pause time. The carrier reuses the §5.10 `<Event>` /
`<EventStream>` pair; the new scheme URI is the only addition.

The new construct's attribute set parallels G1's overlay event,
with the additional Player-side trigger semantics in the chapter
prose.

### G6. Hybrid linear + concurrent overlay break (UC-04)

**Missing**: A way for the Broadcaster to declare a slot where a
linear ad and an overlay ad coexist during the same break. DASH 6th
allows multiple `<EventStream>` elements at the same Period level,
so two events at the same `presentationTime` (one `<ReplacePresentation>`,
one new overlay event from G1) can in principle co-exist. The gap is
**not** in the carrier — it's in the semantics of cross-event
linkage and the conformance behaviour expected of the Player.

**Resolution path**: Spec chapter MUST define the conformance
behaviour for `<ReplacePresentation>` + overlay-event collocation:
either as two independent events at the Player (low-coupling
default; aligns with the three-actor R2) or with an explicit
linkage attribute on one event referencing the other (high-coupling
variant; covered in Q2). The carrier is §5.10; no new construct is
needed for the linkage if the low-coupling default is chosen.

### G7. Application-level ad metadata — `ClickThrough`, `AdSystem`, `AdTitle`, `UniversalAdId` (R6.4)

**Missing**: A way to carry VAST application-level metadata that has
no native DASH 6th field — confirmed in
[`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
§VAST → ListMPD conversion: "The MPEG-DASH 6th edition standard does
not define any carrier fields within the MPD for application-level
VAST metadata such as Click-through URLs."

**Carrier (admissible)**: Vendor-namespaced extension element /
attribute on the relevant target (sub-MPD root, `<ImportedMPD>`,
or the candidate descriptor introduced by G3) — DR-6 carrier (a).
Per R6.4 / R6.5 / R1.1 a Player that does not understand the
namespace MUST safely ignore it.

The SGAI spec MUST decide whether to mint a normative element
shape for these (e.g.
`<svta:Click>`, `<svta:AdSystem>`, ... under `urn:svta:dash:sgai:<year>`)
or to leave them as undefined "vendor namespace area" per
[`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md).
Q6 below.

### G8. Device-class taxonomy and per-(class × UC) expected behaviour (R3)

**Missing**: An enumeration of device rendering classes
(D1..D5 in [`../context/04-use-cases.md`](../context/04-use-cases.md))
and the corresponding Player behaviour for each ad opportunity
type. DASH 6th says nothing about device classes for ad rendering
— ABR / codec / DRM negotiation lives in a different chapter and
does not address "how many concurrent video decoders" or "image
overlay surface".

**Carrier (admissible)**: This is a **spec-document obligation**,
not a carrier choice. The SGAI spec MUST include a chapter that
enumerates D1..D5 (or whatever final taxonomy) and writes the
Player-side conformance behaviour per (class × UC) combination.
The behaviour itself is exercised via the constructs from G1, G3,
G5 — but the spec text is what makes R3.1 satisfiable.

### G9. Player-side validation conformance for SGAI constructs (R2.3, R7.2/R7.3)

**Missing**: A normative algorithm for Player-side validation: how
the Player checks candidates against MPD-declared constraints (G2's
allowed layouts, concurrency cap, the new overlay `@maxDuration`)
before rendering. §5.16.5 covers the cumulative-cap trim for
linear, but the multi-dimensional intersection of (device caps × MPD
constraints × ADS hints) introduced by R5.6 is new. `[inferred]`:
DASH 6th has no comparable validation algorithm to inherit.

**Carrier (admissible)**: Spec-document obligation. The SGAI spec
MUST add a Player conformance chapter that specifies:

1. The validation order (R5.6 intersection: device caps → allowed
   layouts → ADS hints).
2. The drop-before-play behaviour (R7.3) vs trim-during-play
   behaviour (R4.5).
3. The fall-through on candidate exhaustion (R5.7).

This chapter is what closes the "Player MUST validate" requirement
into something testable.

### G10. Non-linear tracking semantics — quartile beacons timed against the overlay window (R13.2)

**Missing**: The §5.10.4.5 callback scheme provides the carrier for
beacons, but its `presentationTime`-anchored semantics are tied to
the media-internal timeline of the ad MPD (15s ad → quartiles at
3750/7500/11250/15000 ms — see the example in
[`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)).
R13.2 requires that for non-linear ads, quartile beacons fire
against the **Broadcaster-declared overlay window** (the slot's
`@maxDuration`), not against the ad's internal duration. There is
no native DASH 6th hook for "re-time the callback events against
an external clock".

**Carrier (admissible)**: Two paths, both inside the DR-6
enumeration:

- **(i) ADS re-times the events**: the ADS, when building the ad
  sub-MPD for an overlay candidate, places the callback `<Event>`
  entries at quartiles of the slot's `@maxDuration` rather than of
  the ad's internal duration. No new construct; entirely a
  resolution-time behaviour. Cleanest under R9 / R13.4.
- **(ii) Spec-level normative remap**: the SGAI spec adds a chapter
  stating that for overlay events, Player MUST interpret callback
  event `presentationTime` values relative to the slot window, not
  the ad media. This re-purposes a baseline construct's semantics,
  which collides with R1.3 (do not alter pre-existing DASH 6th
  semantics) — not admissible.

Option (i) is the path. The SGAI spec MUST state this explicitly
in the Player conformance chapter, even though no new construct is
introduced. R13.3 (stop firing at trim boundary) is a Player rule
that lives in the same chapter and inherits the callback scheme
carrier unchanged.

### G11. "Drop before play" semantics for unrenderable candidates (R7.3, R5.7)

**Missing**: DASH 6th §5.16.5 covers trim-at-cap (trim during play).
It does not define "drop the candidate before fetching its sub-MPD
because its declared duration would exceed the remaining cap" or
"drop the candidate because none of its forms is renderable on this
device" — those are new behaviours specific to multi-form and
device-aware selection.

**Carrier (admissible)**: Spec-document obligation in the Player
conformance chapter (G9). The carrier for the input signals
(declared duration on the sub-MPD `<Period>`; renderable forms on
the candidate from G3) is already present.

---

The following requirement areas appear in the matrix as **full** /
**N/A** but warrant a short note:

- **R1.2 fully covered**: DR-1..DR-7 in
  [`../context/08-dash-extension-rules.md`](../context/08-dash-extension-rules.md)
  is the complete enumeration; the SGAI spec just has to apply it
  per construct via the backward-compat checklist in
  [`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md).
  Conformance to R1.2 is a per-construct audit, not a missing
  carrier.
- **R8 / R9 / R10 are N/A on the matrix** but R9 has high reuse
  potential — captured in §4 below.

## 4. Reuse opportunities (R9)

The points at which existing DASH 6th machinery can be extended
rather than replaced. Each opportunity reduces the net-new-construct
surface and contributes directly to R9.1 / R9.2 / R9.3.

1. **Reuse `<EventStream>` + new `schemeIdUri` for overlay
   opportunities (G1)**. The §5.10 carrier covers the new event
   without modification; only the scheme URI is new. Legacy clients
   skip unknown schemes (R1.1).

2. **Reuse `urn:mpeg:dash:event:callback:2015` for ALL tracking,
   linear and non-linear (R6, R13)**. No new tracking scheme. The
   only delta is *how the ADS sets `presentationTime`* on non-linear
   beacons (G10) — that is an ADS adapter behaviour, not a new
   construct. R13.4 mandates this reuse.

3. **Reuse `<ImportedMPD>` for the AV form of any candidate,
   including non-linear (G3)**. The SPS sub-MPD pattern carries the
   video form of an overlay candidate the same way it carries a
   linear ad. Non-AV forms (image, HTML) live alongside the
   `<ImportedMPD>` in a foreign-namespace child element (DR-6 (a)).

4. **Reuse `@maxDuration` as the attribute name on the new overlay
   event (G1)**. Per the naming-consistency rule in
   [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md),
   identical semantics (broadcaster-declared cap, Player enforces) MUST
   share the baseline name verbatim. Diverging would create silent
   mapping bugs across linear-aware and overlay-aware code paths.

5. **Reuse the §5.2.1 foreign-namespace open content extension
   point as the single carrier surface for almost every new
   construct (G1, G2, G3, G4, G5, G7)**. Choosing DR-6 (a)
   consistently means one extension surface to audit per
   `07-backward-compat-checklist.md`, instead of a mix of (a) / (b)
   / (c). Per
   [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md),
   the namespace `urn:svta:dash:sgai:<year>` carries all of them.

6. **Reuse `UrlParamInfo` (§I.4) for ADS requests on non-linear
   opportunities**. Per
   [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md),
   `@includeInRequests="altmpd"` already scopes the descriptor to
   ADS requests. The spec MAY define a new value
   (`@includeInRequests="overlay"` or similar) `[inferred]`, but the
   descriptor framework is reused as-is.

7. **Reuse `<Period>` ordering inside `ListMPD` (§8.14) for the
   multi-candidate non-linear case (R7)**. If G3 picks option (a)
   (ListMPD-plus-extensions), R7's order-preservation is inherited
   verbatim from §8.14 — the Player honours the ADS-declared order
   the same way it does for a linear pod.

8. **Reuse the §I.4 / §8.14 / §5.10 trio for hybrid linear + overlay
   (UC-04, G6)**. Two `<EventStream>` elements at the same Period —
   one `<ReplacePresentation>`, one new overlay event — co-exist
   without conflict; the linkage is implicit in the shared
   `presentationTime`. No new linkage construct is needed in the
   low-coupling default.

9. **Reuse the `Period@duration` semantics of the sub-MPD as the
   slot's overlay window** (per
   [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)
   §Naming consistency). The semantic match means the spec does not
   invent `@overlayDuration` or similar — same name, same meaning
   keeps reader cognitive load low.

10. **Reuse the §8.14 ListMPD `<Period>` shape for the overlay
    resolution document under option (a)** of G3. Same XML shape;
    extension children declare the non-AV forms; the AV form
    continues to live on `<ImportedMPD>`. Reuses the existing parser
    code path in DASH 6th-aware Players.

## 5. Open questions

These are decisions the spec MUST make but which the gap analysis
does not pre-decide. Each one is admissible under DASH 6th
constraints; the choice is for the spec author (informed by the
SVTA Ads WG and the working doc).

1. **Q1. Should the non-linear resolution document reuse §8.14
   ListMPD (G3 option a) or introduce a separate document shape
   (G3 option b)?** Reusing ListMPD keeps the §8.14 profile intact
   and is lighter on the spec — but constrains the design space.
   Picking a separate shape requires a new profile URI and a Player
   code path. The R9 default leans (a); the decision impacts G3 /
   G4 / G6 / reuse #7 / reuse #10.

2. **Q2. For UC-04 (hybrid linear + overlay), is the cross-event
   linkage explicit or implicit?** Two independent events at the
   same `presentationTime` (low-coupling default, three-actor clean)
   vs an explicit linkage attribute (high-coupling, harder to
   degrade gracefully on legacy Players). Trade-off is between
   richer Broadcaster expressivity and the R1 ignore-if-unknown
   discipline.

3. **Q3. Unit choice for the overlay event's `@earliestResolutionTimeOffset`
   — seconds (matching `<ImportedMPD>` §5.3.2.6.1) or
   `EventStream@timescale` units?** The naming-consistency rule
   forbids reusing the baseline name if the unit differs; the
   choice affects whether the attribute name has to be renamed
   (e.g. `@earliestResolutionTimeOffsetTicks` or
   `svta:earliestResolutionTimeOffset`) or can keep the
   baseline name unchanged. See
   [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md)
   §Naming consistency, second specific case.

4. **Q4. Priority hints schema for multi-form candidates (G4)** —
   numeric `@priority` per form, ordered-list semantics on a
   `<Forms>` container, or a weighted distribution `[inferred]`.
   DASH 6th does not pre-decide; pick the simplest pattern that
   captures both within-candidate form ranking and across-candidate
   ranking (R5.5).

5. **Q5. Pause-event placement**: should the pause-trigger
   `<Event>` (G5) sit at `presentationTime = window_start` with
   `duration = window_end − window_start`, or sit at
   `presentationTime = window_end` with the start derived from a
   separate attribute? The §5.10 carrier supports either; the
   choice has UX implications when the Broadcaster's window starts
   before stream load.

6. **Q6. Whether the spec normatively defines the
   application-level metadata elements (G7) under
   `urn:svta:dash:sgai:<year>`** (`<svta:Click>`, `<svta:AdSystem>`,
   `<svta:AdTitle>`, `<svta:UniversalAdId>`), or leaves them as
   "vendor namespace area" deferred to per-deployment policy. The
   first option is uniform and auditable; the second is closer to
   the current production reality (per
   [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
   §VAST → ListMPD).

7. **Q7. Should the SGAI spec define a normative form-selection
   algorithm for the Player (G9 — the (device caps × allowed
   layouts × ADS hints) intersection), or leave it as conformance
   guidance with a few worked examples?** DASH 6th conformance
   chapters lean toward normative algorithms; cf. §5.16.5 for the
   trim rule. R5.6 reads as if a normative algorithm is intended.
   The trade-off is between spec complexity and implementer
   determinism.

8. **Q8. ADS request on D5 / always-skip devices** — fire the
   request for impression / frequency-capping signals, or skip
   it entirely? Independent of DASH 6th, surfaces in UC-03's notes
   and affects privacy / bandwidth trade-offs.

9. **Q9. Whether single-decoder devices (D3 / D4) can re-task the
   decoder during a pause-ad scenario (UC-05) to play a video form
   on top of a paused primary frame, and what "pause" means under
   that re-tasking.** A device-capability question, not a DASH 6th
   question; the spec MUST pick a default (skip video-form on
   single-decoder D3 / D4 in pause-ad scenarios is the conservative
   choice already noted in UC-05).

10. **Q10. Tracking-only `<Ad>` (no `<MediaFile>`) in VAST input** —
    skip silently or emit VAST Error 403? Could not be resolved
    against the 6th edition source consulted via NotebookLM in a
    prior pass — see the note in
    [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
    §Edge cases. ADS-internal policy until normative guidance
    appears, but the spec SHOULD state it.

11. **Q11. Pin VAST 4.x version** for the illustrative VAST →
    ListMPD adapter mapping. Per
    [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
    §References, the exact 4.x version pin was not confirmed
    against the NotebookLM source in the prior pass — needs
    pinning against the IAB Tech Lab page on the next revision.
    Adapter mapping is illustrative per R11.3 (annex / non-
    normative note), so this is a documentation pin, not a
    normative decision.

## References

- [`../context/02-actors.md`](../context/02-actors.md) — three-actor model.
- [`../context/03-requirements.md`](../context/03-requirements.md) — R1..R13 referenced throughout.
- [`../context/04-use-cases.md`](../context/04-use-cases.md) — UC-01..UC-07 and device classes D1..D5.
- [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md) — DASH 6th linear SGAI baseline, VAST → ListMPD mapping, section anchors.
- [`../context/06-naming-and-namespaces.md`](../context/06-naming-and-namespaces.md) — naming consistency rule, SVTA Ads WG namespace, year-pinning.
- [`../context/07-backward-compat-checklist.md`](../context/07-backward-compat-checklist.md) — per-construct UC-07 audit.
- [`../context/08-dash-extension-rules.md`](../context/08-dash-extension-rules.md) — DR-1..DR-7, the closed extension-point enumeration.
- **FDIS ISO/IEC 23009-1:2025(E), MPEG-DASH 6th edition**, sections cited inline: §4.7, §5.2.1, §5.3.2.2 Table 4, §5.3.2.6, §5.3.2.6.1, §5.3.7.2 Table 16, §5.8.4.8, §5.8.4.9, §5.10, §5.10.4.5, §5.16, §5.16.3, §5.16.4, §5.16.5, §7.3, §8.1, §8.12, §8.14, §8.15, §I.4, Annex F (F.2). IETF RFC 4337 for the MIME-type registry. Anchors above are previously validated in `../context/`; this pass did not re-verify against NotebookLM (grounding mode fallback).

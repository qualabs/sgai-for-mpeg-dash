[GROUNDED_BY=spec-only]

# Spec validation — v7.2 (2026-09-16)

Built against:

- spec: `../output/v7.2-sgai-spec.md` (4803 lines, chapters 1–8 +
  Annexes A–N + a trailing `## Refinement gaps` table)
- `../context/` at git SHA: `38e782f` (working tree clean for
  `context/`; repo HEAD `cb10ae1`)
- `../context-analysis/`: `conformance-assertions.md`,
  `dash-gap-analysis.md`, `error-semantics.md`,
  `uc-coverage-matrix.md`, `iab-ad-templates.md`

The trailing `## Refinement gaps` table (27 rows) is treated as part of
the document under validation. Every item below was re-derived from the
spec body and from `context/`; where a finding coincides with a gap-table
row, the row id is named so the two can be reconciled, but no item was
accepted or dismissed on the strength of its presence in that table.

## Summary

Canonical integer counts. Where a count here and a table below disagree,
the table is canonical.

| Category | Count |
|---|---|
| Gaps (§1) | 8 |
| Edge cases (§2) | 6 |
| Ambiguities (§3) | 7 |
| **Findings carried in §1–§3** | **21** |
| Detail-level findings surfaced in §5.a only (DL-1, DL-2) | 2 |
| Findings surfaced in the R coverage map only (R1.3 vs §4.6.8; R28 on the linear path) | 2 |
| **Findings routed in §5** | **25** |

| R coverage status | Count | Requirements |
|---|---|---|
| `full` | 17 | R2, R5, R6, R11, R13, R15, R16, R17, R18, R20, R22, R23, R24, R25, R27, R29, R30 |
| `partial` | 10 | R1, R3, R4, R7, R12, R14, R19, R21, R26, R28 |
| `gap` | 0 | — |
| `governance` | 3 | R8, R9, R10 |
| **Total** | **30** | R1..R30 |

| Disposition bucket | Rows |
|---|---|
| §5.a Actionable TODOs | 5 |
| §5.b Flagged for review | 10 |
| §5.c Deferred to `context/` | 9 |
| **Total rows** | **24** |

The 24 rows carry the 25 findings above: row C4 carries G-1 and G-2
together, because a single R4 edit closes both. Every finding is routed
to exactly one bucket.

Top three by leverage:

1. **A-1** — several `<svta:Candidate>` in one non-linear resolution
   document are a *sequence* in §4.6.7 / Annex C.7 / T-P7 and a set of
   *alternatives* in §3.1 / §4.6.6 / §8.1 E6 / T-E6. The two readings
   produce opposite viewer outcomes for the same document, and neither
   is a wording slip: `context/` R14 sequences **forms**, and the spec
   carries no construct for a sequence of forms inside one candidate.
2. **R1.3 vs §4.6.8** — the declared narrowing of the base
   specification's §5.16.2.2 fall-through applies to the *inherited*
   linear schemes, so two Players reading
   `urn:mpeg:dash:event:alternativeMPD:insert:2025` behave differently.
   R1.3 is an unconditional document-level MUST NOT.
3. **R28 on the linear path** — §5.6.1's own note records that the
   §8.1 profile-conformance procedure removes `<svta:Click>` from a
   `ListMPD` declaring only `urn:mpeg:dash:profile:list:2024`, so the
   "normative carrier every conformant Player reads the same way" does
   not hold for linear ads.

## Gaps (8)

### G-1 — No timebase or rounding rule for cap arithmetic

- **Spec sections**: §4.6.4, §5.1.1/§5.1.3.1/§5.1.4.1
  (`@maxDuration`), §5.2.1.1 and §5.2.2.4 (`@duration`).
- **What `context/` is missing**: the cap is `xs:unsignedLong` in the
  parent `<EventStream>@timescale` units; a candidate's declared
  duration is `xs:duration` (ISO 8601). R4 states the comparison
  ("cumulative duration … exceeds the declared maximum") and fixes no
  timebase, no conversion and no rounding direction. Nothing in
  `context/` supplies one either.
- **What an implementer does today**: guesses. Two Players converting
  `PT15S` against `maxDuration="15000"` with different rounding
  disagree on whether a candidate exactly at the cap is admitted, which
  is a drop-before-play decision (§4.6.4) with a viewer-visible
  outcome.

### G-2 — No Player behaviour when a slot carries no `@maxDuration`

- **Spec sections**: §4.3.2, §5.1.1 attribute table, §8.1 row E9.
- **What `context/` is missing**: R4.1 makes the Publisher declare a
  cap on every slot but defines no Player behaviour when the Publisher
  did not. The spec inherits the problem: §5.1.1 marks `@maxDuration`
  "no in the base schema; **yes under this specification**" while
  keeping the base default `2251799813685247` (unbounded) in the same
  row, so a manifest omitting it is schema-valid and cap-less. §8.1's
  E9 row names the dependency in the "Other actors" column and states
  no Player response.
- **What an implementer does today**: applies the unbounded default,
  which makes R4's Player-side enforcement inert for that slot.

### G-3 — `@allowedLayouts` is not bound to the slot family

- **Spec sections**: §3.2, §5.1.3.1, §5.1.4.1, §4.6.5.
- **What `context/` is missing**: R12's enumeration maps each token to
  an IAB ad type but declares no token-to-family relation, and R2.1
  gives the Publisher the constraint without bounding the value space
  per family. The spec's §3.2 "Where it appears" column is prose, not a
  constraint: the Player's stated check is exact-token matching against
  `@allowedLayouts` (§4.6.5), so `pause-ad` listed on an overlay slot
  passes every check the spec defines, and so does `overlay-corner` on
  a pause-trigger window.
- **What an implementer does today**: accepts it, or adds a
  proprietary family check that another Player does not have.
- *Gap-table row 1 (F-1) covers the same defect; it is live in the
  body.*

### G-4 — `<Event>@id` uniqueness is scoped nowhere

- **Spec sections**: §5.5.1 (`@id` "narrowed from optional to
  required"), §5.5.2 (de-duplication rule).
- **What `context/` is missing**: R6 and R13 fix the carrier and the
  timebase and say nothing about identifier scope. §5.5.2 makes the
  Player fire "the union, with beacons that share an `@id`, or the same
  URL at the same `presentationTime`, fired once" — a de-duplication
  key whose scope the spec never states. Every worked example numbers a
  candidate's beacons from `id="1"` (lines 1885, 2999, 3276, 3482,
  3613, 4064, 4212, 4230, 4311, 4560), and §5.2.2.3 admits `0..n`
  candidates per document. No example in the spec puts two candidates
  in one document, so the collision is licensed rather than
  demonstrated; but a document that follows both the cardinality and
  the numbering convention suppresses the second candidate's impression
  beacon.
- **What an implementer does today**: scopes the key per candidate and
  hopes the APS agrees, or ignores de-duplication and double-fires.
- *Gap-table row 8 (F-8).*

### G-5 — The Positioning Templates section R10.3 requires does not exist

- **Spec sections**: §1.2, §3.1 ("Positioning inside a layout is
  delegated to HTML5 / CSS and is out of scope here"), §2 (W3C CSS
  layout modules).
- **What `context/` is missing**: R10.3 is a positive document-level
  obligation — position semantics "MUST be expressed via the
  Positioning Templates section using HTML5 / CSS primitives". The spec
  satisfies R10.1 and R10.2 (delegate, define no parallel standard) by
  declaring positions out of scope, which is the opposite of expressing
  them somewhere. A grep of the spec for "Positioning Template" returns
  only the gap table (line 4793); the same grep finds the CSS
  delegation prose at lines 101, 205 and 279, so the instrument is not
  the null result.
- **What an implementer does today**: has nowhere in this
  specification to read how a corner overlay is positioned, and takes
  it from the IAB document by inference.

### G-6 — The Publisher query template has no request type on a non-linear slot

- **Spec sections**: §5.8.1, §6.2, §6.3, Annex A.2.
- **What `context/` is missing**: R18.2 leaves the Publisher↔APS
  arrangement bilateral and R29 reserves only the Player's parameters,
  so no requirement covers this. The spec declares
  `@includeInRequests="altmpd"` as "the value that names an
  alternative-MPD resolution request" and then presents the mechanism
  as available on "the resolution request" for any slot (§5.8.1 intro,
  §6.2's "Carries" row, §6.3's "Payload" row). The overlay and
  pause-trigger schemes of §2.1 are not alternative-MPD events, so
  `altmpd` does not name their resolution request.
- **What an implementer does today**: invents a request-type value, or
  authors the template on a linear slot only and discovers the
  restriction empirically.
- *See Actionable TODO T5. Gap-table row 26 (M3) states the durable
  remedy — a new request-type URI registered in §2.1 — which stays
  outside a minor refinement.*

### G-7 — The candidate-level callback `<EventStream>` has no validation contract

- **Spec sections**: §5.5.2, §8.8.
- **What `context/` is missing**: R6.2 places the beacons "in the ad
  `MPD` or sub-`MPD`" and DR-6(b) admits an application-level Event
  Stream, but neither reaches a `<EventStream>` hosted as
  foreign-namespace open content inside `<svta:Candidate>`. §5.5.2's
  own note concedes the placement is "novel relative to that canonical
  placement"; §8.8 tells tooling to scan for it. Neither states how a
  document carrying it is validated, nor which scope the callback
  scheme's presentation times are resolved in once the element is
  outside a `<Period>`.
- **What an implementer does today**: validates the resolution
  document with the foreign-namespace subtree stripped, which removes
  the tracking carrier from the check entirely.
- *Gap-table row 24 (M1).*

### G-8 — Two §4.7.3 rows cannot name a DR-N rule, and the table is two columns short of the checklist

- **Spec sections**: §4.7, §4.7.3.
- **What `context/` is missing**: `context/07-backward-compat-checklist.md`
  item 2 requires every construct's chapter to name the applicable
  DR-N rule, and its "Aggregated audit table" prescribes eight columns
  (Construct, Placement, Extension rule, Walk-through, Sibling check,
  UC-07 test, Namespace, Status). `context/08-dash-extension-rules.md`
  enumerates DR-1..DR-7, none of which is the §5.10 per-scheme skip the
  two opportunity-declaration `<EventStream>` rows rely on. The spec's
  table carries six columns — Construct, Placement, Extension rule,
  Legacy Player, Sibling check, Carrier class — substituting the
  checklist's item-8 classification for the UC-07-test, Namespace and
  Status columns.
- **What an implementer does today**: reads the extension rule as a
  bare clause citation and cannot audit the table rule by rule, which
  is the property §4.7's own DR-N paragraph claims for it.
- *Gap-table row 21 (flag-1) records the DR-6 half; the missing
  columns are additional.*

## Edge cases (6)

### EC-1 — Does the slot cap accrue while a non-linear form is suspended?

- **Trigger**: an overlay is rendering and the viewer pauses inside a
  pause-ad window (§4.6.9), or the primary content is paused with a
  partial pause-ad on screen.
- **Why it matters**: §4.6.4 enforces the cap against "actual rendered
  length" and §4.6.12 puts cap arithmetic on the presentation
  timeline. Annex H freezes the overlay's *window* clock with
  presentation time and says nothing about its *cap* clock. A
  suspended overlay that keeps accruing cap returns with less time than
  its window shows; one that does not can outlive its declared cap in
  wall clock.
- **Actor**: Player. `context/` (R4, R17, UC-08) is silent; UC-08
  describes suspend-and-restore without a cap statement.
- *Gap-table row 5 (F-5).*

### EC-2 — A pause inside a pause-trigger window while a linear ad occupies the screen

- **Trigger**: a hybrid break (§5.1.5) or a plain linear slot whose
  span overlaps a pause-trigger window (§5.1.4), and the viewer pauses.
- **Why it matters**: R22 and §4.6.7 bound *non-linear* forms only, so
  a pause-ad composited over a paused linear ad breaks no stated rule
  and is authorised by none either. The viewer-visible outcomes differ
  by a whole ad.
- **Actor**: Player. `context/` is silent — UC-04 and UC-05 never
  cross.
- *Gap-table row 7 (F-7).*

### EC-3 — A `200` resolution document of the wrong family for the slot

- **Trigger**: an overlay slot's `@uri` answers `200` with a `ListMPD`,
  or a linear slot's answers with an Overlay Resolution Document.
- **Why it matters**: §8.1's E3 row covers a body that is "not
  well-formed XML, carries an unknown root element, or fails schema
  validation" — a well-formed `ListMPD` is none of the three. E5 covers
  a document carrying no candidates, and a `ListMPD` carries no
  `<svta:Candidate>` by construction, so the wrong-family document
  reads as an empty resolution and terminates the fallback chain
  (§4.6.8), which is the opposite of what happened.
- **Actor**: Player. `context/` is silent; R20.1's access test is
  transport-level.
- *Gap-table row 6 (F-6).*

### EC-4 — A fullscreen pause ad on a device with no overlay capability

- **Trigger**: a `pause-ad` option whose surface is fullscreen, on D5
  (one decoder, no image or HTML surface) — or on D3/D4 when neither
  non-video option is offered.
- **Why it matters**: §4.6.9 states that when the pause ad is
  fullscreen "the Player MAY release the resources held by the primary
  content and by any pre-existing overlay in order to present a
  fullscreen video, image or web page". That is the same
  one-decoder-reused-sequentially budget §5.3.7.3 gives the `linear`
  full-screen takeover, which the table marks satisfiable on **all
  five** classes. Yet §5.3.7.3's `pause-ad` rows never split by
  surface: the `video` row lists "D1, D2; D3–D4 when the device can
  re-task the decoder", and the `image` / `html` rows require surfaces
  D5 lacks — so Annex E.4 has D5 decline an opportunity a fullscreen
  option makes renderable.
- **Actor**: Player, and the spec document for §5.3.7.3. `context/` is
  the origin: UC-05 models the pause ad exclusively as "composited on
  top of the paused primary frame" and its open question names only
  "single-decoder devices (D3, D4)", so the fullscreen surface R21
  admits is in no use case.

### EC-5 — Whose `@allowedLayouts` binds the candidates served from a fallback window

- **Trigger**: the first window of a same-family chain is inaccessible
  and the second answers (§4.6.8, path 2).
- **Why it matters**: the two windows are separate `<Event>`s with
  separate `@allowedLayouts` and separate `@maxDuration`. Binding the
  chain to the first window's declaration and binding each window to
  its own are both defensible and select different options.
- **Actor**: Player. The answer appears only in Annex L.3 ("validates
  its candidates against window 1202's own constraints"), which is
  marked *Informative*; §4.6.8 is silent.
- *Gap-table row 11 (F-11).*

### EC-6 — `@executeOnce` on a pause-trigger window

- **Trigger**: a `<svta:PauseAdPresentation>` with
  `@executeOnce="true"` and two viewer pauses inside the window.
- **Why it matters**: §5.1.4.1 defines the attribute as "As in
  §5.1.1", where it means "the event executes at most once in the
  session". A pause-trigger window is not executed by the playhead —
  §5.1.4's own rationale is that the trigger is the pause, off the
  timeline. One reading makes the attribute inert on this element; the
  other caps the window at one pause ad per session. The two differ by
  every pause after the first.
- **Actor**: Player. `context/` is silent — no requirement mentions
  `@executeOnce`.
- *Gap-table row 10 (F-10).*

## Ambiguities (7)

### A-1 — Several candidates in one non-linear document: a sequence, or alternatives?

- **Context passage**: `context/03-requirements.md` R14 body
  ("A non-linear ad slot MAY be filled by more than one ad **form**
  played in **sequence**") and R14.1 ("when the resolution document …
  declares more than one ad form, the Player MUST present the forms in
  sequence"), against R5.3 / R7.1, where candidates are walked and
  dropped. `context-analysis/conformance-assertions.md` records the
  same word in P03.2: "The resolution document MAY declare more than
  one ad **form** for it, played in sequence."
- **Reading 1 — sequence**: §4.6.7 ("when the resolution document
  declares more than one **candidate** for one slot, the Player
  presents them one after another"), Annex C.7 ("three candidates of
  10 seconds each is presented as the first, then the second, then the
  third"), §N.2 T-P7 ("three 10 s candidates … render one after
  another").
- **Reading 2 — alternatives**: §3.1 ("the selection sense of
  'candidate' applies to the non-linear document"), §4.6.6 ("When no
  option on a candidate is satisfiable, the Player advances to the
  **next candidate**"), §8.1 E6, §N.1 T-E6 ("The first candidate is
  skipped and the **second renders**. Falling through to primary
  content instead is a fail").
- **Which the draft assumed**: both, in different chapters. The two
  are not reconcilable at runtime: under reading 1 a document with
  three satisfiable candidates renders three ads; under reading 2 it
  renders one. T-P7 and T-E6 are the same setup with opposite pass
  observables.
- **Tighter `context/` sentence**: R14 needs to name the construct
  that carries the sequence. The spec has no per-candidate form
  sequence — `<svta:RenderableAsset>` children are alternatives by
  §5.3.5 — so R14 either binds the sequence to candidates (and R5.3 /
  R7 need a non-linear carve-out) or requires a new construct.
- *Gap-table row 15 (D-1) names this the highest-leverage open item.
  This pass agrees, independently.*

### A-2 — `@earliestResolutionTimeOffset`: a Publisher obligation, or an optional attribute?

- **Context passage**: R2.1 enumerates the constraints the Publisher
  declares — "max duration, opt-in policies, layout templates" — and
  does not include the resolution offset. R4.1 makes only
  `@maxDuration` mandatory on every slot. No requirement makes the
  offset mandatory.
- **Reading 1 — mandatory**: §4.3.5, "Declares
  `@earliestResolutionTimeOffset` on every slot with a value that
  leaves the APS a usable head start" (line 563), stated in the same
  imperative voice as §4.3.2 and §4.3.4.
- **Reading 2 — optional**: every attribute table marks it
  `Required: no` with "60 s when absent" (§5.1.1, §5.1.3.1, §5.1.4.1),
  and §5.1.1's note tells an implementation that "needs the value to be
  unambiguous" to declare it — advice that only makes sense if not
  declaring it is conformant.
- **Which the draft assumed**: reading 2 in chapter 5, reading 1 in
  chapter 4. A conformance checker built from §4.3 and one built from
  §5.1 disagree on a manifest that omits it.
- **Tighter `context/` sentence**: none needed — `context/` already
  says only `@maxDuration` is mandatory. The spec site to align is
  §4.3.5.
- *Routed to Actionable TODO T1. Not in the gap table; the same defect
  shape as row 4 (F-4) on a different attribute.*

### A-3 — What quantity `@maxDuration` bounds on a pause-trigger window

- **Context passage**: R4 ("the cumulative duration of the candidates
  the Player chose to render") and R4's own mention of "overlay max
  display duration".
- **Reading 1 — one ad's display time**: §5.1.4.1, "Maximum display
  duration of the pause ad before automatic dismissal".
- **Reading 2 — cumulative**: §5.1.3.1 for the overlay slot
  ("enforced against the cumulative rendered length of the forms
  presented in this slot") and §4.6.4's fourth bullet, which applies
  the cumulative rule to every non-linear slot.
- **Which the draft assumed**: both. With one pause ad the two
  coincide, which is why every annex example hides it; with a document
  carrying several candidates they diverge, and which one applies
  depends on A-1.
- **Tighter `context/` sentence**: R4 stating the quantity once, in
  the same terms for every slot family.
- *Gap-table row 22 (flag-4).*

### A-4 — "Overlay" names a family, a document class, a profile URI and a layout token

- **Context passage**: `context/03-requirements.md` R12 uses
  `overlay` as one IAB ad type; `context/04-use-cases.md` UC-03 uses
  "overlay" as the non-linear family.
- **Readings**: in the spec, "Overlay" is the non-linear family as a
  whole (§5.2.2.2's note), the resolution-document class
  (§5.2.2), the profile URI
  `urn:svta:dash:profile:sgai-overlay-list:2026` (§2.1), the element
  `<svta:OverlayList>` (§5.2.2.3) — and separately the `overlay`
  `@layout` token of §3.2, which names one spatial arrangement.
- **Which the draft assumed**: the family reading for the document and
  profile names, the layout reading for the token, with §5.2.2.2's note
  as the disambiguator.
- **Tighter `context/` sentence**: `context/06` fixing a family name
  distinct from a layout token. The note resolves it for a reader; the
  wire format still carries a pause-ad document under a profile URI
  that says "overlay".
- *Gap-table row 12 (F-12).*

### A-5 — A still image's declared duration under non-1× playback

- **Context passage**: R19's body and R19.3 ("`duration /
  playback_speed`"), written for an ad whose media has an intrinsic
  length; R19 never separates media-backed from non-media forms.
- **Readings**: (1) `@duration` is a presentation-timeline value for
  every form, so a 10-second image at 2× is on screen for 5 seconds of
  wall clock — which §4.6.12 states unconditionally and §5.5.3 supports
  by anchoring an image's presentation origin at first render;
  (2) a form with no intrinsic media has no presentation timeline to
  scale, so its `@duration` is wall clock.
- **Which the draft assumed**: reading 1, by omission — §8.6 says "For
  those forms the candidate's declared `@duration` is the length" and
  never names the speed.
- **Tighter `context/` sentence**: R19 stating that `@duration` is a
  presentation-timeline value for `image` and `html` forms too, and
  that the derived wall-clock length applies to them.
- *Gap-table row 14 (F-14).*

### A-6 — §2.1's URIs carry a segment `context/06`'s pattern does not admit

- **Context passage**: `context/06-naming-and-namespaces.md`,
  "New event schemes introduced by this spec MUST use the year-pinned
  pattern … `urn:svta:dash:<construct>:<year>`", with the illustrative
  examples `urn:svta:dash:sgai-overlay:2026` and
  `urn:svta:dash:sgai-pause-trigger:2026`.
- **Readings**: (1) `<construct>` is a single opaque segment, so the
  spec's `urn:svta:dash:event:sgai-overlay:2026` and
  `urn:svta:dash:profile:sgai-overlay-list:2026` violate the pattern;
  (2) `<construct>` may itself be dotted or segmented, and the
  `event:` / `profile:` classifier is part of it.
- **Which the draft assumed**: reading 2, silently — §2.1 introduces
  the classifier without citing or amending the policy.
- **Tighter `context/` sentence**: `context/06` admitting a
  kind-classifier segment, `urn:svta:dash:<kind>:<construct>:<year>`.
  The classifier does real work — it separates a scheme URI from a
  profile URI in one glance — so the spec is the half that is right.
- *Gap-table row 19 (D-5).*

### A-7 — Annex D.3's linear portion is 15 seconds and 30 seconds

- **Context passage**: none — this is internal to the spec. UC-04
  bounds the break and names no duration.
- **Readings**: (1) the linear portion is the 15-second ad Annex A.4
  declares (`<Period id="ad_01" duration="PT15S">`, "The ad is 15
  seconds against a 20-second cap"); (2) it is 30 seconds, per D.3's
  own sentence and D.2's `maxDuration="30000"`.
- **Which the draft assumed**: reading 2 for the scenario, reading 1
  for the document it points at, in one sentence: "resolves to a
  `ListMPD` exactly as in Annex A.4, carrying one 30-second ad"
  (line 3453).
- **Tighter `context/` sentence**: none — this is a spec-internal
  cross-reference defect.
- *Routed to Actionable TODO T2.*

## R coverage map

Every requirement in `../context/03-requirements.md`. Status values:
`full`, `partial`, `gap`, `governance` (R8, R9, R10). Section
references are to `../output/v7.2-sgai-spec.md`.

| R | Status | Spec sections that satisfy it | Notes |
|---|---|---|---|
| R1 | partial | §1, §4.1, §4.6.2, §4.6.3, §4.7.1, §4.7.3, §5.1.3.3, §5.1.4.2, §5.3.6, Annex G, T-P15 | R1.1, R1.2, R1.4 met. **R1.3 unmet**: §4.6.8 declares a narrowing of the base specification's §5.16.2.2 fall-through that applies to the inherited linear schemes; §1 and §4.1 declare the exception rather than avoid it, and R1.3 admits none. Gap-table rows 16 (D-2) and 23 (NC1). |
| R2 | full | §4.2, §4.3, §4.4, §4.5, §4.6, §6.7, §7.1–§7.3 | The decision table of §4.2 maps 1:1 onto R2.1–R2.4; §4.1's three document-level obligations carry R2.4. |
| R3 | partial | §3.4, §4.6.5, §5.3.7.3, §5.8.2, Annexes A–M per-class tables, §8.4 | R3.1 and R3.3 met. **R3.2 partial**: the hybrid opportunity type on a single-decoder device has two opposite answers — §7.5.4 and Annex D.5 decline the overlay portion; §8.4 says the specification decides neither. Gap-table rows 2 (F-2) and 20 (D-6). See also EC-4 for the pause-ad type on D5. |
| R4 | partial | §4.3.2, §4.6.4, §5.1.1, §5.1.3.1, §5.1.4.1, §5.4.1, §8.1 E9/E10, Annex F.4, T-E9, T-E10 | R4.2–R4.5 met. **R4.1 residual**: G-1 (no timebase or rounding for the comparison), G-2 (no Player behaviour when no cap is declared, and §5.1.1 keeps the unbounded base default), EC-1 (accrual while suspended), A-3 (which quantity on a pause window). Gap-table rows 4 (F-4), 5 (F-5), 18 (D-4). |
| R5 | full | §4.5.3, §4.6.5, §5.3, §5.3.5, §5.8.4, Annexes C, I, M, T-P3, T-P4 | R5.1–R5.7 all carried. §4.6.5's "no presentation option reaches the screen without passing this check" carries R5.2/R5.6 against the APS-narrowed case of §5.8. |
| R6 | full | §4.5.6, §5.5, §5.5.1, §5.5.2, §4.6.3 | R6.1–R6.4 met; no new tracking scheme (§2.1). The placement question is G-7, which is a validation contract rather than an R6 obligation. |
| R7 | partial | §4.6.6, §5.3.5, §8.1 E6/E9, Annex F.4, T-E6, T-E9 | R7.1–R7.5 met for the linear family. **Residual**: on the non-linear family, "the order the resolution document declares" means a play order in §4.6.7 and a walk order in §4.6.6 (A-1). |
| R8 | governance | §5.1, §5.1.3, §5.1.4, §5.1.6, §5.2.2, §5.3, §5.5, §5.6, §5.7, §4.1 | Every new construct carries a "Why a new construct" block and a "Considered and not reused" note (R8.1, R8.2). |
| R9 | governance | §4.7.1, §5.1.1, §5.1.2, §5.2.1, §5.3, §5.5, §5.1.6 | Reuse is the default throughout; the three ordered-preference constructs and the two fallback constructs are each considered and rejected with a stated reason (R9.3). |
| R10 | governance | §1.2, §2 (W3C CSS layout modules), §3.1 | R10.1 and R10.2 met. **R10.3 unmet** — see G-5. Status stays `governance` per the prescribed value set; the residual is the note. Gap-table row 17 (D-3). |
| R11 | full | §1.2, §3.5, §4.4.6, §6.7 (marked non-normative), §5.7 | R11.1–R11.3 met; every VAST mention is in §6.7 or an abbreviation gloss. |
| R12 | partial | §3.2, §4.3.3, §4.5.4, §5.3.3, §2 (IAB reference), §8.1 E7 | R12.1–R12.4 met at the value level. **Residuals**: G-3 (no family binding on the token space) and the `pause-ad` token collapsing the IAB "Fullscreen or Partial Screen" placements into one row while Squeezeback splits by placement, which also drives EC-4. Gap-table rows 1 (F-1) and 9 (F-9). |
| R13 | full | §4.4.2, §4.5.6, §4.6.10, §5.5.1, §5.5.3, §8.3, §8.1 E14 | R13.1–R13.5 met; §5.5.1 states explicitly that the quartile names in the example are the ADS's and not prescribed. |
| R14 | partial | §4.6.7, §7.5.3, Annex C.7, T-P7 | The sequencing rule exists but is expressed over **candidates**, while R14 and R14.1 express it over **forms** and the spec's forms (`<svta:RenderableAsset>`) are alternatives by §5.3.5. R14.3 met (no parallel-render primitive). See A-1; gap-table row 15 (D-1). |
| R15 | full | §3.3, §4.5.4, §5.3.2, §8.1 E8, T-P16 | R15.1–R15.3 met; §3.3 is the single enumeration and §1.2 restates the exclusions. |
| R16 | full | §4.6.9, §7.5.5, Annex E, T-P8, T-E14 | R16.1 (one rendering frame) and R16.2 (beacons cease) both carried verbatim. |
| R17 | full | §4.6.9, §7.5.6, Annex H, T-P10, §8.1 E15 | R17.1–R17.4 met, including "this specification carries no construct that lets the Publisher, the ADS or the APS invert it". |
| R18 | full | §1.2, §4.1, §4.5 preamble, §6.7, §6.8 | R18.1 and R18.2 met; the two fidelity properties are explicitly placed outside the specification in §4.5 and §6.7. |
| R19 | partial | §4.6.12, §5.5.3, §7.5.1, Annex B.5 trick-play variant, T-P18 | R19.1–R19.3 met for media-backed forms. **Residual**: A-5 — a still image's declared duration under non-1× speed is never stated, and §8.6 states the length without the speed. Gap-table row 14 (F-14). |
| R20 | full | §4.6.8, §5.1.6, §7.5.9, Annex L, T-P13 | R20.1 met including the `200`-with-no-candidates carve-out. EC-5 (whose `@allowedLayouts` binds the fallback) is adjacent and not an R20 obligation; it is normative only in Annex L.3, which is *Informative*. |
| R21 | partial | §4.6.9, §3.2, §5.3.3, §7.5.5, Annex E | R21.1's two surfaces are stated. **Residual**: the surface never reaches the decoder-and-surface budget — §5.3.7.3's `pause-ad` rows do not split fullscreen from partial, so the fullscreen case §4.6.9 authorises is unreachable on D5 and conditional on D3/D4. See EC-4. |
| R22 | full | §4.6.7, §1.2, §5.1.3.1 ("On concurrency"), §8.1 E15, T-E15 | R22.1 met; §5.1.3.1 declines a maximum-concurrency attribute on DP-1.1 grounds, which is the right reading. |
| R23 | full | §5.7, §4.7.3 | R23.1 met: the four elements are named, in the SVTA namespace, and both ends are declared optional. |
| R24 | full | §4.5.5, §4.7.2, §5.3.1, §5.3.2, §8.1 E8, T-P16 | R24.1 met: the asset URL rides on `@assetUrl` under DR-6(a) and §4.7.2 closes the `@mimeType` axis with both independent reasons. |
| R25 | full | §4.6.9, §7.5.5, Annex E.5, T-P9 | R25.1 met, plus the `MPD@timeShiftBufferDepth` ceiling, which is a constraint the base specification imposes and the spec surfaces rather than invents. |
| R26 | partial | §5.3.7.2, §5.3.7.3, §4.3.10, Annex J, §3.2 | R26.2 and R26.3 met. **R26.1 residual**: the background is a child of the option element rather than of the slot, and splitting the double box into two tokens makes an advertiser-supplied background gated by the Publisher's `@allowedLayouts`, an outcome R26.2 does not contemplate. Gap-table row 13 (F-13). |
| R27 | full | §5.3.7.1, §5.3.7.3, §3.2, Annex I, Annex J.5 | R27.1–R27.3 met, including the "no separate third filler element" statement and the per-form decoder budget. |
| R28 | partial | §5.6, §5.6.1, §4.5.8, §4.6.11, §6.7, Annex K, T-P12 | R28.2 and R28.3 met, and R28.1 met on the non-linear path. **R28.1 unmet on the linear path**: §5.6.1's own note records that the §8.1 profile-conformance procedure of the base specification removes `<svta:Click>` from a `ListMPD` declaring only `urn:mpeg:dash:profile:list:2024`, and §2.1 mints no linear-family profile URI. Gap-table rows 3 (F-3) and 27 (M4). |
| R29 | full | §4.6.13, §5.8.2, §5.8.3, §5.8.4, §4.5.9, §4.5.10, Annex M, T-P14 | R29.1–R29.7 all carried. R29.6's acceptance test is met: the three parameters separate D1..D5 (§5.8.2's mapping table), and the spec states why no fourth axis is reserved. |
| R30 | full | §4.5.7, §5.2.3, §4.6.8, §6.4, §8.1 E5, T-E5, T-P17 | R30.1 met for both families, with the `200`-plus-body shape stated and both degenerate documents given. |

## Disposition of findings

### 5.a Actionable TODOs (5)

Two rows below — DL-1 and DL-2 — are detail-level items that do not
belong in §1/§2/§3: they are not gaps, boundary conditions or readings,
but single-site defects. They are named here so the refine step can
apply them and so the count in §Summary reconciles.

| # | Finding ref | Criterion | Spec section | Concrete edit | Citation |
|---|---|---|---|---|---|
| T1 | A-2 | 3 — internal contradiction, one reading matches `context/` | §4.3.5 (line 563) | Replace "Declares `@earliestResolutionTimeOffset` on every slot with a value that leaves the APS a usable head start before the slot's `presentationTime`." with "Declares `@earliestResolutionTimeOffset` on a slot whose APS needs more head start than the base specification's 60-second default gives it; when the attribute is absent that default applies (§5.1.1)." | R2.1 enumerates the constraints the Publisher declares — max duration, opt-in policies, layout templates — and does not include the resolution offset; R4.1 makes only `@maxDuration` mandatory on every slot. The optional-with-default reading in §5.1.1 / §5.1.3.1 / §5.1.4.1 is the context-grounded one. |
| T2 | A-7 | 4 — cross-reference inconsistency | §D.3 (line 3453) | Replace "resolves to a `ListMPD` exactly as in Annex A.4, carrying one 30-second ad" with "resolves to a `ListMPD` of the same shape as Annex A.4, whose single `<Period>` declares `duration=\"PT30S\"`". | DP-1.2 (single source of truth): the linear portion's duration is stated in two places — Annex A.4's `duration="PT15S"` and D.3's prose — with different values, and D.2's `maxDuration="30000"` fixes which one the scenario means. |
| T3 | DL-1 | 4 — cross-reference pointing at the informative half of a normative claim | §3.2, `pause-ad` row (line 377) | Replace "(§7.5.5)" with "(§4.6.9)". | R21.1 is a runtime Player obligation; §4.6.9 is where the spec carries it. §7.5.5 is inside chapter 7, which restates behaviour per scenario, and Annex E is marked *Informative*. |
| T4 | DL-2 | 2 — self-flagged marker the spec does not use | Preamble, line 15–17 | Replace "Grounding: the MPEG-DASH 6th edition claims in this document were checked against the authoritative source. Claims that could not be verified against it are tagged `[inferred]`." with "Grounding: every MPEG-DASH 6th edition claim in this document was checked against the authoritative source; none remained unverified." | DP-1.1: a convention introduced for a case that does not occur is a future-flexibility placeholder. `grep -n "\[inferred\]"` returns one hit, the convention sentence itself; the same grep for `inferred` returns three hits (lines 17, 550, 2394), so the null result is the document and not the instrument. |
| T5 | G-6 | 1 — the spec asserts a base-specification semantic the base specification does not carry | §5.8.1 (after the `@includeInRequests` sentence), and §6.2 "Carries" / §6.3 "Payload" rows | Append to §5.8.1: "The `altmpd` request type is defined by the base specification for an alternative-MPD resolution request, so a Publisher-declared query template travels on a **linear** slot's resolution request. This edition defines no request-type value for the overlay and pause-trigger schemes of §2.1, so a non-linear slot carries no author-declared query template." Qualify §6.2's "plus optionally a `<RequestParam>` query template (§5.8.1)" and §6.3's "the Publisher-declared template (§5.8.1)" with "on a linear slot". | R1.3 — the specification MUST NOT alter or override the semantics of a pre-existing base specification construct, and `@includeInRequests="altmpd"` with its Annex I.4 binding is one. The edit states the existing limitation and mints nothing; the durable remedy (a new request-type URI in §2.1) is a new construct and stays out of a minor refinement (gap-table row 26, M3). |

### 5.b Flagged for review (10)

| # | Finding ref | Spec section | Why uncertain | Resolutions considered |
|---|---|---|---|---|
| F1 | G-3 | §3.2, §5.1.3.1, §5.1.4.1, §4.6.5 | Binding a token to a family is vocabulary design, not wording: it adds a column to §3.2 and a Publisher obligation to §4.3.3, and it changes what an existing `@allowedLayouts` declaration means. | (a) family column in §3.2 plus an exact-token-within-family check in §4.6.5; (b) a per-family token prefix, which renames the wire format; (c) leave it and state that a cross-family token is inert. |
| F2 | G-4 | §5.5.1, §5.5.2 | Scoping `<Event>@id` and scoping the de-duplication key are two different fixes, and the second is a runtime Player obligation rather than an authoring rule. | (a) require `@id` unique per resolution document; (b) scope the de-duplication key to (candidate, `@id`); (c) drop `@id` from the key and de-duplicate on URL plus `presentationTime` alone. |
| F3 | EC-1 | §4.6.4, §4.6.9, Annex H.3 | Both readings are defensible, and the choice also settles A-3 and constrains EC-2. | (a) the cap accrues only while the form is actually on screen; (b) the cap follows presentation time and therefore freezes with it; (c) the cap follows the slot window and accrues regardless. |
| F4 | EC-2 | §4.6.7, §4.6.9, §5.1.5 | Allowing or forbidding a pause ad over a linear ad changes what the viewer sees during a break, and R22's bound does not reach a linear form. | (a) forbid, on the grounds that a linear ad is itself the whole surface; (b) allow, with the pause-ad priority of §4.6.9 applied unchanged; (c) declare it Publisher-controlled through the pause window's placement. |
| F5 | EC-3 | §8.1 E3, E5, §4.6.8 | Deciding it without deciding E3's deliberately open case splits two conditions the Player cannot tell apart before parsing. | (a) treat a wrong-family document as E3 (unusable body); (b) treat it as an access failure and try the fallback; (c) require the APS to answer with the family the slot declared and leave the Player's response unconstrained. |
| F6 | EC-5 | §4.6.8, Annex L.3 | Promoting Annex L.3's sentence into §4.6.8 adds a normative obligation, and binding the whole chain to the first window's declaration is equally defensible. | (a) each window binds its own candidates (Annex L.3's current answer); (b) the first window's declaration binds the chain; (c) the intersection of the chain's declarations binds. |
| F7 | EC-6 | §5.1.4.1 | One reading makes the attribute inert on this element, the other caps the window at one pause ad per session — opposite viewer-visible outcomes. | (a) define `@executeOnce` on a pause-trigger window as one pause ad per session; (b) declare it inadmissible on the element and drop the row; (c) leave the base semantics and state that a pause-trigger window is never "executed". |
| F8 | A-3 | §5.1.3.1, §5.1.4.1, §4.6.4 | Aligning the quantity decides EC-1 and EC-6 in passing, and which quantity is right depends on A-1. | (a) cumulative for every family, matching §4.6.4; (b) per-ad display time for the pause family, matching §5.1.4.1; (c) two attributes, which DP-1 rejects. |
| F9 | A-4 | §2.1, §5.2.2, §5.2.2.3, §3.2 | A rename is a wire-format change across a profile URI and an element name; §5.2.2.2's note already removes the reader-facing ambiguity. | (a) rename the document class and the profile URI to a family-neutral term; (b) rename the `overlay` layout token; (c) keep both and keep the note. |
| F10 | A-5 | §4.6.12, §8.6, §5.5.3 | The alternative — wall clock for non-media forms — breaks DP-1.2's single canonical value, so the fix is not free either way. | (a) state that `@duration` is a presentation-timeline value for `image` and `html` too, so the derived wall-clock length applies; (b) declare non-media forms wall-clock-timed, with the DP-1.2 cost; (c) leave the case open and say so. |

### 5.c Deferred to `context/` (8)

Ordered by leverage.

| # | Finding ref | `context/` file to edit | Suggested edit | Leverage rationale |
|---|---|---|---|---|
| C1 | A-1 | `context/03-requirements.md` (R14, R7, R5) | Name the construct that carries R14's sequence. Either bind the sequence to candidates and give R5.3 / R7.1 a non-linear carve-out, or state that the sequence lives inside one candidate and requires a construct the spec does not yet have. | Highest leverage in this pass. §4.6.7, §4.6.6, §8.1 E6, Annex C.7, §N.1 T-E6 and §N.2 T-P7 all resolve from it, and T-E6 and T-P7 are today the same setup with opposite pass observables. Nothing downstream can be fixed while both readings stand. |
| C2 | R1.3 vs §4.6.8 (see the R coverage map) | `context/03-requirements.md` (R1.3, R20.1, R30) | Let R1.3 admit a declared, enumerated narrowing, or scope R20's first-window-wins rule to the SGAI schemes so the inherited linear schemes keep base semantics. | Two requirements cannot both hold: R1.3 is unconditional and R20.1 with R30 forces the narrowing. Today the spec declares the exception in §1 and §4.1, which is honest and still non-conformant against its own requirement set. Gap-table rows 16 (D-2) and 23 (NC1). |
| C3 | R28 on the linear path (see the R coverage map) | `context/03-requirements.md` (R28) and `context/06-naming-and-namespaces.md` | Decide whether the linear family gets its own profile URI — which §2.1 would then mint — or whether R28.1's "normative carrier" is scoped to the non-linear document. | R28.1 is unmet on the linear path today and the spec says so itself in §5.6.1's note. Every remedy either mints a URI or moves the carrier, and both are requirement-level. Gap-table rows 3 (F-3) and 27 (M4). |
| C4 | G-1 and G-2 | `context/03-requirements.md` (R4) | Add two criteria: the timebase and rounding direction for comparing a candidate's `xs:duration` against a cap expressed in `@timescale` units; and the Player's behaviour on a slot that carries no cap. | R4 is exercised by ten of the thirteen use cases (`uc-coverage-matrix.md`), so both gaps reach every linear and non-linear scenario. Gap-table row 18 (D-4). |
| C5 | EC-4 | `context/04-use-cases.md` (UC-05) and `context/03-requirements.md` (R21) | Extend UC-05 with the **fullscreen** pause-ad surface R21 admits, including its per-class rows: a fullscreen pause ad needs no concurrent composition, so its budget is the `linear` takeover's and reaches D5. | UC-05 today models the pause ad exclusively as an overlay on the paused frame and its open question names only D3/D4, so §5.3.7.3 and Annex E.4 inherit an exclusion the requirement set does not intend. Closing it makes R3.2 checkable for the pause-ad opportunity type on every class. Not in the gap table. |
| C6 | G-8 | `context/08-dash-extension-rules.md` and `context/07-backward-compat-checklist.md` | Add a DR-N for the §5.10 per-scheme event-skip rule, so the two opportunity-declaration `<EventStream>` rows of §4.7.3 can name one; and reconcile the audit table's column set with the checklist's eight. | `context/07` item 2 makes naming the DR-N rule mandatory and `context/08` supplies no rule that covers an event scheme, so the spec cannot comply as the two files stand. Gap-table row 21 (flag-1). |
| C7 | G-7 | `context/03-requirements.md` (R6) and `context/08-dash-extension-rules.md` (DR-6) | State where a tracking carrier may sit when the ad has no sub-MPD: either widen DR-6(b) to admit an `<EventStream>` hosted as foreign-namespace open content, with the scope its presentation times resolve in, or require an SVTA-namespace carrier mirroring the callback shape. | R6.2 places the beacons "in the ad `MPD` or sub-`MPD`", which does not reach an `image` or `html` candidate — the case §5.5.2 invents a placement for. Until the context says where, the carrier cannot be schema-validated and §8.8's tooling note is the only thing standing between it and silent loss. Gap-table row 24 (M1). |
| C8 | G-5 | `context/03-requirements.md` (R10.3) | Either drop R10.3's Positioning Templates obligation — R10.1 and R10.2 already deliver the delegation R10 exists for — or state what the section must contain for an `image` form, which carries no HTML/CSS surface on which a position could be expressed. | An unmet document-level MUST that the spec cannot satisfy without building the thing R10.2 forbids. Gap-table row 17 (D-3). |
| C9 | A-6 | `context/06-naming-and-namespaces.md` | Admit a kind-classifier segment in the pattern: `urn:svta:dash:<kind>:<construct>:<year>`, with `event` and `profile` as the kinds this edition uses. | The classifier does real work — it separates a scheme URI from a profile URI at a glance — so the policy is the half that is behind, not the spec. Cheap, and it removes a standing non-conformance against a normative context file. Gap-table row 19 (D-5). |

### 5.d Routing notes

Four items were re-examined against `context/` and **not** routed as
defects, because the spec matches what `context/` says:

- **§5.3.7.3's `pause-ad` / `video` row naming only D3–D4 for the
  decoder re-task.** `context/04-use-cases.md` UC-05's open question
  names "single-decoder devices (D3, D4)" and its D5 row declines the
  opportunity. The spec is faithful; the gap is upstream and is filed
  as EC-4 / C5.
- **`<svta:BackgroundElement>` carried on the option rather than on the
  slot.** R26.1 says "composition attribute of the slot / layout"; the
  layout half is satisfied, and attaching it to the slot would make an
  advertiser creative a Publisher declaration. Recorded as an R26
  residual, not a defect.
- **§4.7.1's vendor-descriptor row marked "not used by this
  edition".** R1.2 enumerates all three admissible extension points, so
  listing an unused one is required by the requirement and is not a
  DP-1.1 placeholder.
- **The `<svta:Click>` note in §5.6.1 stating that a list-profile
  client may drop the element.** The note is accurate and the defect it
  records is R28's, filed as C3; the note itself should stay.

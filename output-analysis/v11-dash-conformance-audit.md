[GROUNDED_BY=iso-23009-1-2026-pdf]

# DASH conformance audit — v11 (2026-09-26)

**Audit target**: `../output/v11-sgai-spec.md`.
**Reference**: the edition declared in
`../context/00-normative-base.md` (ISO/IEC 23009-1:2026, Sixth edition).
The primary copy on disk matches the declared `sha256`
(`a7274eb2…be100`). Schema: `DASH-MPD.xsd` and `DASH-MPD-UP.xsd` from the
edition's own schema package (`DASHSchema-6th-Ed.zip`, published at the URL
the base gives in Annex B).
**Method**: inventory + clause searches against the primary copy + schema
validation of every example + rule checks on every complete document +
per-construct verdict.

## Scope

Whether each construct v11 introduces or reuses is valid under the base
specification: its schema, its extension-point rules, its event rules, the
profile restrictions (§8.1, §8.4, §8.13, §8.14, §8.15) and the semantics of
the base attributes the spec inherits. Design quality is out of scope.

## Method summary

- **Inventory** built from §1.3, §2.1, §3.3–§3.5, §4.2–§4.8, §5.0–§5.10,
  §6.2–§6.5, §7.13–§7.16, §8.13 and the complete documents of Annexes A–Q.
- **Quotation check.** The document has 93 italic quotations from the base.
  All were searched in a whitespace-flattened extraction of the primary copy.
  91 matched as written. The other 2 were confirmed by reading the source: the
  Table 63 `@skipAfter` row is split across table columns, and *"a key use
  case"* (§5.16.1) differs only in the capital letter of the source. Controls:
  a sentence known to be present (*"At least one Adaptation Set shall be
  present in each Period"*) was found; the same sentence with one word changed
  was not.
- **Clause-number check.** Each quotation was located in the extraction and
  its enclosing clause compared with the clause cited next to it. No citation
  points at a clause about a different subject. Where the first match landed
  elsewhere, the phrase was generic (*"may not be presented"*, *"The rules for
  the MPD as defined in subclause 7.3"*, *"infinity"*), and the cited clause
  was read and does contain it.
- **Existence check of every citation.** 70 distinct `DASH §n`, `DASH Annex
  X.n` and `Table n` references were checked against the headings of the
  extraction. 68 exist. One is the placeholder `DASH Annex X` of the
  reference convention (line 18). **One does not exist: `DASH §4.8.9`** (E1).
- **About 40 targeted clause reads**: §4.2, §5.2.1, §5.2.3.2, §5.2.3.6,
  §5.3.1.4, §5.3.2.2 Table 4, §5.3.2.6.1–3, §5.8.4.8, §5.8.4.9, §5.9.1,
  §5.9.4, §5.10.1, §5.10.2.1–4 (Tables 43, 44), §5.10.4.5 (Tables 46, 47),
  §5.16.1, §5.16.2.2.1–6, §5.16.3 (Table 59), §5.16.4 (Tables 61, 62),
  §5.16.5.2 (Table 63), §7.3.1, §8.1, §8.3.2, §8.4.2, §8.12.4.3, §8.12.4.4,
  §8.13 (all subclauses), §8.14, §8.15, Annex D.4.6 (Table D.5), §H.1–§H.2.3,
  Annex I.3.1, I.3.6 (Table I.4), K.3.8, K.6.4, L.2, and the base example
  files G29-1, G29-2, K6.4.
- **Schema validation.** The §5.10.1 schema compiles against the base schema.
  **81 of 81** XML fragments (every `xml` block except the schema itself and
  the two illustrative VAST responses; five partial fragments wrapped in a
  minimal parent) validate against the base schema plus the extension schema.
  The validator was shown to reject: a layout token outside the enumeration,
  an `svta:Ad` with no option, an unknown `@family`, a 3-value and an
  out-of-range `@rect`, an `svta:Tracking` without `@schemeIdUri`, an `Event`
  with `@messageData`, `svta:Tracking` after `svta:ClickThrough`, a bad
  `@dismissAfter` on both documents, a window without `@durationCap`,
  `linearRelation="supersede"` on a pause window, an `svta:` child placed
  before `ImportedMPD`, and a foreign attribute on `EventStream`. It accepts
  the base's own G29-1 and G29-2. With the base schema **alone**, a window
  without `@durationCap` validates, which reproduces the lax-skip that §5.10.2
  describes.
- **Rule checks on 75 complete documents**: 21 main MPDs, 8 List MPDs, 24
  Single-Period Static (SPS) MPDs, 22 `svta:OverlayList`. Checked: one
  `EventStream` per scheme and value per Period; non-decreasing `Event` times;
  unique `Event@id` per stream; SGAI streams without `@value`, each window
  with `@id`, `@duration` and exactly one `svta` child of its family;
  `@allowedLayouts` within the family; `@customRegion` only with `custom`;
  `InsertPresentation` only in static MPDs; alternative-MPD events carrying
  `@id` and no `@status` on insertion; `@clip` only with `@maxDuration`;
  `RequestParam` accompanied by the MPD-level `EssentialProperty`
  `urn:mpeg:dash:urlparam:2025`; List rules 1, 2, 3 and 5 of §8.14; the SPS
  rules of §8.15.2 and §8.15.3; callback streams with `@value="1"` and no
  `@messageData`; `PlayList` metrics wherever pause windows appear; on the
  non-linear documents `@onExhausted` by family, `@rect` if and only if
  `custom`, `@background` if and only if the background double box,
  `@mimeType` among the three forms, and tracking order and id uniqueness;
  and **callback `@id` uniqueness across each List MPD together with its
  sub-MPDs** (7 annexes). The checker was run on documents broken on purpose:
  a duplicated callback id across two sub-MPDs, `Metrics` in an SPS, two
  streams with the same scheme and value, and a callback stream with
  `@value="2"`. It reported each one. No defect was found in the spec's
  documents. G.3 is correctly flagged as holding windows with no `svta` child,
  because that is what the document looks like after removal.
- **Removal check (§5.2.1).** Every `svta` element and attribute was removed
  from all 53 MPDs, and each result validates against the base schema alone.
  G.3 as authored validates against the base schema alone and carries no
  `svta` content.

## Inventory + verdicts

| ID | Construct | Type | Placement | Verdict | Rationale |
|----|-----------|------|-----------|---------|-----------|
| C1 | `urn:svta:dash:sgai-overlay:2026` | event scheme | `Period/EventStream@schemeIdUri` | Conforming | Table 43: *"The string may use URN or URL syntax"*; `@value` space *"expected to be defined by the owners of the scheme"*. §5.10.1: a client may *"ignore Event Streams that are of no relevance or interest"*. |
| C2 | `urn:svta:dash:sgai-pause-trigger:2026` | event scheme | as C1 | Conforming | As C1. |
| C3 | One stream per family per Period, no `@value`; Player ignores `@value` (PUB-7, PUB-8, PLY-87) | authoring rule | `Period` | Conforming | §5.10.2.1: *"A Period shall contain at most one EventStream element with the same value of the @schemeIdUri attribute and the value of the @value attribute"*. `@value` is `O` in Table 43. Checked on 21 main MPDs. |
| C4 | `<svta:OverlayPresentation>` | element | child of `Event` | Conforming | Table 44: Event content may be *"XML content, possibly using elements external to the MPD namespace"*. §5.10.2.1: further elements *"may be defined in this document … or in some external namespace"*. `EventType` has an `xs:any ##other lax` after the base choice. Validated. |
| C5 | `<svta:PauseAdPresentation>` | element | child of `Event` | Conforming | As C4. |
| C6 | `Event@id`, `@duration` required on windows; `@presentationTime` Period-relative | narrowing of base attributes | `Event` | Conforming | All are `O`/`OD` in Table 44 and in `EventType`; requiring them narrows the base without contradicting it. Types match the schema (`xs:unsignedLong`), and `@status` defaults to `repeat`. |
| C7 | `@earliestResolutionTimeOffset` on windows: same name, units, 60 s default | reused attribute | SGAI elements | Conforming | Table 63: *"specifies the time interval (in units of EventStream@timescale) prior to the Event@presentationTime … The default is 60 seconds in units of timescale"*. The base schema declares no default on this attribute either, which is consistent with the extension schema. |
| C8 | `@executeOnce` on a pause window, consumed when rendering starts | attribute | `svta:PauseAdPresentation` | Conforming | The attribute is in the spec's own namespace. The counter rule matches §5.16.2.2.6: *"When the alternative media presentation triggered by an event successfully starts playing, the corresponding counter E.c is incremented"*. |
| C9 | `@durationCap` (required) instead of `@maxDuration` | new attribute | SGAI elements | Conforming | Own attribute. The base `@maxDuration` default is infinity (Table 63; schema `default="2251799813685247"`), so a new name avoids redefining a base construct. |
| C10 | `@maxDuration` on inherited events keeps the base meaning (absent means infinity; zero means not executed) | reuse | `InsertPresentation`/`ReplacePresentation` | Conforming | Both quotes verified in Table 63. The v10.1 departure (absence meant no ad) is gone; N.2 omits the attribute and is played with base semantics. |
| C11 | `InsertPresentation` only in static MPDs | reuse | main MPD | Conforming | §5.16.3: *"The event shall not appear if the MPD type is "dynamic""*. 9 inherited events across the annexes: every insertion sits in a static MPD. All carry `Event@id` (*"Required"*, Tables 59/61) and no `@status` on insertion (*"This attribute shall not be used"*, Table 59). |
| C12 | `ReplacePresentation` `@clip`, `@returnOffset`, `@startWithOffset` | reuse | main MPD | Conforming | Types and defaults match `AlternativeMPDReplaceEventType`. `@clip` *"shall not be present if the @maxDuration attribute is absent"* (Table 62): N.2 has neither attribute; B.2 has both. |
| C13 | `@noJump` kept on the linear events, not carried on the windows | reuse / non-reuse | alternative-MPD events | Conforming | Table 63 semantics verified. **Citation defect**: §1.3 justifies it with `(DASH §4.8.9)`, and that clause does not exist (E1). |
| C14 | Explicit `@skipAfter` and `PlaybackRestrictions@skipAfter` with their base meaning; spec-defined precedence between them | reuse | alternative-MPD event; `ServiceDescription` | Conforming | Table 63 and Table K.9 quotes verified. The claim that the base gives no precedence was checked: all 7 lines of the extraction that contain `skipAfter` were read (Table 63 row, schema, G.29 example, K.3.8 row, Table K.18, schema), and none orders the two controls. |
| C15 | `@linearRelation` on windows; only `on-top` on pause windows | new attribute | SGAI elements | Conforming | Own attribute; nothing is added to the base events or their streams (DOC-26). The schema enforces `OnTopOnlyType`, and a rejected sample confirmed it. |
| C16 | `supersede`: a Player of this spec does not execute a base event that the base would execute | Player departure on a base construct | Player | Marginal | Declared in §4.8.3 and opted into by the Publisher; a legacy Player is unaffected. But §5.16.2.2.1 presents its steps as *"a set of normative conditions which hold for any sequence of Alternative MPD events"*, on which *"the MPD author may assume that the steps described in this subclause are taken"*. See detail. |
| C17 | Fallback chain; PRT order; tie-break by stream position | extension of §5.16.2.2 | Player | Conforming | §5.16.2.2.5 step 2 d quoted verbatim; *"ordered by the presentation time PRT"* (§5.16.2.2.2). The base leaves ties unordered, so the tie-break is correctly labelled as the spec's own. |
| C18 | Four failure shapes mapped to §5.16.2.2.6; E.c not incremented | reuse | Player | Conforming | Conditions and NOTE 3 quoted verbatim. |
| C19 | A List MPD with candidates is not a failed execution even when the device can render none of them (PLY-41) | behaviour on the inherited linear family | Player | Marginal | The base list is open: *"The playback of the alternative presentation cannot start. The reasons for this include (but are not limited to)…"*, and it includes *"Media playback is impossible due to missing media or initialization segments"*. See detail. |
| C20 | Dropping List MPD Periods before play (PLY-34, PLY-35) | Player departure on a base construct | Player | Marginal | §4.5.5 itself says *"dropping a List MPD Period before play is this specification's permission"*, but §4.8.3 says only *"One decision departs"*. See detail. |
| C21 | List MPD as the linear resolution document | reuse | resolution document | Conforming | §8.14 rules 1, 2, 3 and 5 hold on all 8 List MPDs; rule 4 permits the regular Period of the empty resolution. |
| C22 | `svta:` children of a List Period, after the DASH children | extension content | `Period` | Conforming | `PeriodType` ends with `xs:any ##other lax` (validated; a misordered sample was rejected). §5.3.2.6.3 step 3 b ix keeps *"any elements from a different namespace"*. |
| C23 | `@svta:dismissAfter` on the List `MPD` element | foreign attribute | `MPD` | Conforming | `MPDtype` has `xs:anyAttribute ##other lax`. The merge acts on the Linked Period and on the imported MPD's MPD level, not on the List MPD element. A bad value was rejected. |
| C24 | Linear tracking only in the sub-MPD Period | reuse | sub-MPD | Conforming | §5.3.2.6.3 step 3 c: Imported Period elements *"replace (i.e. override)"* Linked Period ones, and for `EventStream` equivalence is *"EventStream@schemeIdUri and EventStream@value"*. No List MPD in the document carries an `EventStream`. This resolves v10.1 C21. |
| C25 | Callback `Event@id` unique across a List MPD and all its sub-MPDs (PLY-81, §5.5.1) | id scope on the inherited construct | List MPD + sub-MPDs | Conforming | Table 44: *"The scope of the @id for each Event is within the same @schemeIdURI and @value pair over the duration of the current media presentation"*. §5.10.2.4: an event with a previously processed scheme, value and id is *"ignored by the DASH client"* when `@status` is absent (both quotes verified). The check found no duplicate in the 7 annexes; an injected duplicate was detected. This resolves v10.1 C22. |
| C26 | Empty linear resolution: a List MPD with one regular `PT0S` Period and no media | reuse | List MPD | Marginal | Table 4 allows an Adaptation-Set-less Period only at zero duration, and §8.14 rule 4 allows regular Periods. But the List profile *"is an extension of the ISO-BMFF CMAF Profile"*, and §8.1 conditions profile conformance of a presentation on *"at least one Representation in each Period"*. The spec now tags the reading `[inferred]` (§8.13 item 9). See detail. |
| C27 | `<svta:OverlayList>` as a standalone document with no profile | new document | resolution document | Conforming | Not an MPD, so it carries no `@profiles` obligation (`use="required"` in `MPDtype`). It reaches a Player only through C1/C2. It is validated by the extension schema, which imports the base. |
| C28 | `<svta:Ad>`, `<svta:RenderableAsset>`; image and HTML never as Representations | carrier | `svta:OverlayList` | Conforming | §7.3.1: *"The @mimeType attribute of each Representation shall be provided according to IETF RFC 4337"*, applied to SPS by §8.15.2 and to List Adaptation Sets through §8.12.4.3 (*"The @mimeType shall be set to "<contentType>/mp4""*). |
| C29 | Video option as an SPS sub-MPD referenced by `@src` | reuse | option | Conforming | §8.15.1: SPS MPDs *"are usable on their own"*. All 24 SPS MPDs pass the §8.15.2/§8.15.3 checks, and their mimeTypes are within RFC 4337. |
| C30 | No `ImportedMPD` inside a non-linear option | non-reuse | — | Conforming | `ImportedMPD` exists only as a child of `Period` in the schema, and the merge is a Period process (§5.3.2.6.3). |
| C31 | `<svta:Tracking>` of type `dash:EventStreamType`, with DASH-namespace `Event` children | base type reused in a foreign element | `svta:Ad` | Conforming | The base declares `EventStream` only locally (no global declaration in `DASH-MPD.xsd`), which confirms the §4.8.2 rationale. With the extension schema loaded, the tracking carrier is validated strictly (missing `@schemeIdUri` and `@messageData` were both rejected). This resolves v10.1 C29. |
| C32 | Tracking timebase anchored at the candidate's start | redefinition for extension content | `svta:Tracking` | Conforming | Table 44 anchors `@presentationTime` to *"the start of the Period"*. `svta:Tracking` sits in no Period, and the spec states its own anchor and keeps the `@presentationTimeOffset` subtraction (Table 43). |
| C33 | Callback carrier: `@value="1"`, URL as event content, no `@messageData` | reuse | every tracking stream | Conforming | Table 47 (`EventStream@value` 1). Table 44: *"Including the message within the Event element … is the recommended approach"*; the schema has `messageData use="prohibited"`. |
| C34 | `<svta:ClickThrough>` in both documents | element | `svta:Ad`; List Period | Conforming | Extension content at extension points; validated. |
| C35 | `<svta:AdSystem>`, `AdTitle`, `Advertiser` | elements | `svta:Ad`; List Period | Conforming | As C34. |
| C36 | `@allowedLayouts` (space-separated list); `@customRegion`/`@rect` in SRD notation, 100 × 100 | attributes | SGAI elements | Conforming | `StringVectorType` is `xs:list` (*"Whitespace-separated list of strings"*). §H.2.2 axes and the Table H.1 containment sentence verified. §H.1 confines the SRD **descriptor** to `AdaptationSet`/`SubRepresentation`, not the notation. |
| C37 | `@family`, `@dismissAfter`, `@validFor`, `@onExhausted`, `@background` | attributes | `svta:OverlayList`, option | Conforming | Own attributes; no base construct is touched. The co-occurrence rules hold on all 22 documents. |
| C38 | `RequestParam` in a window's `EventStream`, with request type `urn:svta:dash:sgai-resolution:2026` | reuse | `EventStream` | Conforming | `EventStreamType` admits `RequestParam`. Table I.4 admits *"a URN or tag URI, where the request type semantics is understood by the client and specified by the URN / tag URI owner. The client shall drop unknown URIs…"*. |
| C39 | The MPD-level `EssentialProperty` `urn:mpeg:dash:urlparam:2025` that C38 brings, and its legacy consequence | base descriptor required by Annex I.3 | `MPD` | Marginal | §5.8.4.8 NOTE 1: *"If the scheme or the value for this descriptor is not recognized, the DASH Client is expected to ignore the parent element that contains the descriptor"*; at MPD level the parent is the whole MPD. The C5 walk-through (§4.7.7) covers only a legacy Player *"that implements DASH Annex I.3"*. See detail. |
| C40 | Reserved `sgai-` query parameters, `x-<vendor>-` prefix | request convention | resolution request | Conforming | Not an MPD construct. It shares the URL with the `RequestParam` output, as Annex I.3.5.2 permits. |
| C41 | `<Metrics metrics="PlayList">` at MPD level; paused interval derived from `starttype`/`stopreason` | reuse | `MPD` | Conforming | Table D.5 values `Resume` (*"Resume from pause"*), `UserRequest` and `Rebuffering` verified. `MetricsType` requires `Reporting` (1..N). §5.9.4: *"No reporting scheme is specified in this document"*. |
| C42 | Annex main MPDs declare `isoff-live:2011` | Publisher choice in the examples | `MPD@profiles` | Marginal | §8.4.2: *"The elements and attributes listed in subclause 5.2.3.2 may be ignored"*; §5.2.3.2 lists `Period.EventStream` and `MPD.EssentialProperty`; §8.1 profile step 5 removes what *"may be ignored"*. Carried over from v10.1 (C44). See detail. |
| C43 | SGAI event streams in an Advanced Linear MPD | profile interaction | `MPD@profiles` | Marginal | §8.13.2.2 *"EventStream elements may indicate Alternative MPD (5.16) and Callback (5.10.4.5) event schemes"* is permissive, and the base's own Advanced Linear example (K.6.4) carries a Period `EventStream` of `urn:mpeg:dash:event:service-description:2024`, a scheme that list does not name. The spec leaves the question open (§4.8.5, §8.13 item 1). See detail. |
| C44 | Removal-by-namespace guarantee | authoring rule | every SGAI construct | Conforming | §5.2.1 quote verified. All 53 MPDs validate against the base schema alone after removal, and G.3 as authored does too. |
| C45 | Namespace `urn:svta:dash:sgai:2026`, SVTA URNs, per-edition versioning | identifiers | — | Conforming | No base rule constrains foreign namespaces or application scheme URNs. Whether `svta` is a registered URN namespace identifier is not a DASH question and was not checked `[inferred]`. |
| C46 | No profile or Interoperability Point minted | non-construct | — | Conforming | §8.1 quotes verified: *"The owner of the URI is responsible…"* and profile step 4 (*"in an extension namespace and not explicitly included by ProfA"*). |
| C47 | `linear` takeover option of a non-linear candidate: insertion-like on static, replacement-like on dynamic | spec composition rule | Player | Conforming | This is the spec's own composition; no base event is emitted. The justification (§5.16.3 forbids insertion in dynamic MPDs) is quoted correctly. |

## Base-standard findings (highlights)

- **Linked-Period merge and event identity.** The merge keeps foreign-namespace
  children and overrides a same-scheme, same-value `EventStream` (§5.3.2.6.3
  step 3 b ix, 3 c iv). `@id` is scoped per scheme and value across the media
  presentation (Table 44), and a repeat with an absent `@status` is ignored
  (§5.10.2.4). v11 now authors tracking in one position and numbers beacons
  across the List MPD, so the two v10.1 non-conformities are gone (C24, C25).
- **Profiles.** `isoff-live` and `isoff-on-demand` both mark `Period.EventStream`
  as ignorable (C42). Advanced Linear lists Alternative MPD and Callback
  streams with *"may"*, and the base's own AL example carries a third scheme
  (C43). The List profile inherits the CMAF Period model, and §8.1 requires a
  Representation per Period for a conforming presentation (C26).
- **Descriptors.** An MPD-level `EssentialProperty` that a client does not
  recognise makes it ignore the MPD (§5.8.4.8 NOTE 1), which is the legacy cost
  of using `RequestParam` for SGAI requests (C39). Also, `PeriodType` and
  `AlternativeMPDEventType` admit only `SupplementalProperty`, not
  `EssentialProperty` (E2).
- **Alternative presentations are not SPS-bound.** §5.16.2.2.6: *"When
  alternative media presentation is a live presentation, it always starts at
  the live edge"*. Only `ImportedMPD` targets are SPS (§5.3.2.6.1). This
  answers the `[inferred]` of §8.13 item 6 (E5).

## Non-conforming items detail

None. No construct of v11 violates an explicit rule of the base
specification.

## Marginal items detail

### C16 — Supersede against the base processing model

§4.8.3 declares that a Player of this spec does not execute a superseded
event, and DOC-3 names it as the one exception. The base frames §5.16.2.2 as
*"a set of normative conditions which hold for any sequence of Alternative MPD
events"*, adding that *"the MPD author may assume that the steps described in
this subclause are taken"*. The document stays valid DASH, and the author who
relies on the assumption is the same Publisher who opts out of it. What is
ambiguous is the scope of DOC-3's *"MUST NOT alter or override the semantics
of any construct of the base specification"* next to a declared override.
**Clarify**: in §4.8.3, cite the §5.16.2.2.1 sentence as the rule being
departed from, and state that the departure is scoped to MPDs whose author
declared `supersede`.

### C19 — Unrenderable linear candidates

PLY-41 says a resolution document with candidates *"is not a failed
execution, whatever the Player then does with them"*, and that an
unrenderable candidate ends at the primary content. This rule covers List
MPDs too. The base failure list is open (*"include (but are not limited
to)"*) and names *"Media playback is impossible due to missing media or
initialization segments"*. A linear ad the device cannot start is therefore a
failed execution under the base, and the base then moves to the next queued
event (§5.16.2.2.5 step 2 d). §4.8.3 does not record this. **Clarify**:
either restrict PLY-41 to the non-linear families, or record it in §4.8.3 as
a departure for the linear family.

### C20 — Dropping List MPD Periods

PLY-34 and PLY-35 let a Player drop List MPD Periods (no renderable form; a
declared duration past the cap). The base plays the merged alternative
presentation and trims it: *"For insertion events, APDA = min(APD,
APDmax)"* (Table 57). §4.5.5 calls dropping *"this specification's
permission"*, but §4.8.3 opens with *"One decision departs"* and lists only
supersede. DOC-4 requires every departure to be recorded there.
**Clarify**: record the permission in §4.8.3, or confine PLY-34/35 to
`svta:OverlayList` candidates.

### C26 — The empty List MPD under the List profile

Table 4 permits a Period with no Adaptation Set when *"the value of the
@duration attribute of the Period is set to zero"*, and §5.16.2.2.6
anticipates *"merge process resulted in no available media"*. Against this,
§8.14 makes the List profile *"an extension of the ISO-BMFF CMAF Profile"*;
§8.12.4.4 says *"If the Subset element is not present, the Period contains
exactly one CMAF Presentation"*; and §8.1 makes a Media Presentation
conforming to a profile only if *"There is at least one Representation in
each Period in the profile-specific MPD"*. The empty List MPD can be a
conforming **MPD** and still not a conforming **Media Presentation** under the
List profile. **Clarify**: add the §8.1 sentence to §8.13 item 9, and state
that the spec relies on MPD conformance only, which is what the base's own
failure condition presupposes.

### C39 — Legacy cost of the `urlparam:2025` descriptor

§5.8.1 correctly requires the MPD-level `EssentialProperty` whenever
`RequestParam` is used. Under §5.8.4.8 NOTE 1, a client that does not
recognise that scheme *"is expected to ignore the parent element that
contains the descriptor"*, which at MPD level is the whole MPD, so the primary
content does not play. The C5 entry of §4.7.7 walks only the legacy Player
that implements Annex I.3. This is a base obligation that the Publisher opts
into (MAY), not an SGAI construct. But it bears on DOC-1 and DOC-38. The
sentence the spec paraphrases also continues *"unless the scheme is explicity
allowed in a profile (e.g. ISO-BMFF Advanced Linear Profile defined in
8.13)"*. **Clarify**: add to §4.7.7 the case of a legacy Player without Annex
I.3 support, and quote the full §I.3.1 sentence.

### C42 — The annex profile lets a client ignore every window

All 21 annex main MPDs declare `urn:mpeg:dash:profile:isoff-live:2011`.
§8.4.2 makes the §5.2.3.2 list ignorable, and that list includes
`Period.EventStream`. A client conforming to that profile may therefore drop
every SGAI window and every inherited linear event. No rule is broken.
**Clarify**: say so in §4.8.5. Also correct §4.8.5's statement that the
annexes use `isoff-live` *"or"* `isoff-on-demand`: none uses on-demand
(E3), and on-demand carries the same ignorable list (§8.3.2).

### C43 — SGAI streams under Advanced Linear

§4.8.5 and §8.13 item 1 quote §8.13.1 (*"Support for a restricted set of DASH
events"*), §8.13.2.2 and §8.13.2.1 (*"Periods and Representations which do not
conform to the constraints in this subclause may not be presented"*)
correctly. The constraints are permissive: nothing in §8.13 says *"shall
only"*. The base's own Advanced Linear example in K.6.4 carries a Period
`EventStream` of `urn:mpeg:dash:event:service-description:2024`, which
§8.13.2.2 does not name. The base therefore reads §8.13.2.2 as
non-exhaustive, at least for base schemes. For SGAI streams, two points
remain open: whether an **application** scheme counts as a conforming Period
element, and whether an SGAI `RequestParam` fits §8.13.2.4/§8.13.2.7, whose
lists of `@includeInRequests` values (*"may appear"*) contain no URN.
**Clarify**: add the K.6.4 evidence to §8.13 item 1, and keep the question
open for the application-scheme case.

## Text defects against the base (not counted as constructs)

- **E1 — `DASH §4.8.9` does not exist** (§1.3, line 156). Clause 4 of the base
  ends at 4.7 (*Schemes*), and Clause 5 follows. Search: no heading `4.8` in
  the extraction; the string `4.8.9` occurs 0 times; `4.8.` occurs only
  inside `5.8.4.8` (2 hits, which shows the search does find the substring).
  The reason the sentence refers to is this document's own §4.8.4 (*"`@noJump`
  on the non-linear windows. Excluded, for the reason in §1.3"*), which would
  make the reference circular. **Fix**: drop the parenthesis, or cite the
  base's `@noJump` semantics (Table 63).
- **E2 — DR-6 overstates where descriptors sit.** *"Descriptors sit on
  `Period`, `EventStream`, `Event` and `AlternativeMPDEventType`"*: `PeriodType`
  and `AlternativeMPDEventType` admit `SupplementalProperty` only (schema;
  Table 4 lists only `SupplementalProperty` on Period). `EventStream` and
  `Event` admit both. No construct depends on it.
- **E3 — §4.8.5 profile list.** All 21 annex main MPDs use `isoff-live:2011`;
  none uses `isoff-on-demand:2011`.
- **E4 — Minor.** The containment sentence cited as *"DASH Annex H.2.2, Table
  H.1"* sits in Table H.1, which belongs to §H.2.3. The axes are in §H.2.2.
- **E5 — §8.13 item 6 `[inferred]` can be resolved.** Only `ImportedMPD` targets
  are SPS-bound (§5.3.2.6.1). §5.16.2.2.6 contemplates a live alternative
  presentation, and a live presentation cannot be SPS, which requires `static`.
  An alternative MPD reached through `@uri` may therefore carry `Metrics`.

## Open questions surfaced

- **C43** — whether an application-scheme `EventStream` (and its URN
  `RequestParam`) belongs in an Advanced Linear Period. Searched §8.13.1–§8.13.4
  and Annex I.3.1; no *"shall only"* rule was found. The only evidence is the
  base's K.6.4 example, which uses a base scheme.
- **C26** — whether the List profile's CMAF Period constraints and §8.1's
  Representation-per-Period condition bind a zero-duration, media-less Period.
  Searched §8.12.4.4, §8.12.4.5, §8.14 and §8.1. The only zero-duration rule in
  the extraction is Table 4's exception, and the instrument found that
  sentence.
- **C45** — registration of the `svta` URN namespace identifier is outside the
  base standard and was not checked `[inferred]`.

No `[fetch-failed]` item: every construct's governing clause was located.

## Summary

- Total constructs audited: 47
- Conforming: 40
- Marginal: 7 (C16, C19, C20, C26, C39, C42, C43)
- Non-conforming: 0
- Text defects against the base: 5 (E1–E5), E1 being the non-existent
  `DASH §4.8.9`

[GROUNDED_BY=iso-23009-1-2026-pdf]

# DASH conformance audit — v10 (2026-09-25)

**Audit target**: `../output/v10-sgai-spec.md`.
**Reference**: the edition declared in
`../context/00-normative-base.md` (ISO/IEC 23009-1:2026, Sixth edition,
2026-07); `bin/check-normative-base.py` returned `OK` before the audit.
**Method**: inventory + clause searches against the primary copy +
schema validation of every XML example + per-construct verdict.

## Scope

Conformance of every construct v10 introduces or reuses to the base
specification's schema, extension-point rules, event placement rules,
profile restrictions and inherited attribute semantics. Design choices
are not assessed (that is the validation sidecar's job).

## Method summary

- Inventory built from §1.4, §2.1, §4.6, §4.7, §4.8, §5.1–§5.10 and the
  XML examples of Annexes A–Q.
- About 90 phrase searches against a whitespace-flattened extraction of
  the primary copy (line breaks removed before matching). Every quoted
  sentence below was found literally; the clause number was confirmed by
  locating the nearest preceding clause heading, not taken from the
  spec's citation.
- The primary copy does not contain the full MPD schema: *"The schema of
  the MPD for this document is provided at:
  https://standards.iso.org/iso-iec/23009/-1/ed-6/en (DASH-MPD.xsd)"*
  (Annex B). That published schema (`DASHSchema-6th-Ed.zip`) was
  downloaded to a temporary directory and used for validation; it is not
  in this repository.
- Schema validation (lxml / libxml2):
  - **Positive control**: the 41 official `example_*.mpd` files shipped
    with the schema validate against `DASH-MPD.xsd` (41/41).
  - **Examples of v10**: 87 `xml` blocks parsed; 72 complete `<MPD>`
    documents and 7 standalone `svta:` fragments validated against
    `DASH-MPD.xsd` + the §5.10 schema combined (lax wildcards of the
    base schema therefore reach into `svta:` content). Result: 57 MPDs
    valid, **15 invalid, all for the same cause** (item C24). With that
    one wildcard switched to `lax`, 72/72 and 7/7 valid.
  - **Negative control**: an appended MPD with `family="banner"` and a
    `RenderableAsset` without `@assetUrl` were both rejected, so the
    combined validation does check `svta:` content inside an MPD.
  - **Removal check (DASH §5.2.1)**: every non-DASH-namespace element and
    attribute removed from the 72 MPDs (164 removals); 72/72 still valid
    against `DASH-MPD.xsd`.
- Structural checks (scripted, over all examples): child order of `MPD`,
  `Period`, `EventStream`, `Event` and `svta:Candidate` (78 Periods, 25
  Candidates, 61 EventStreams: 0 violations; the checker flagged all 3
  violations injected into a control copy); List MPD rules (9
  documents), Single-Period Static rules (24 documents), non-linear
  document shape (21), `InsertPresentation` in a dynamic MPD, duplicate
  scheme/value streams in one Period, non-decreasing `presentationTime`
  (61/61), callback `@value`, `@messageData`, missing `@maxDuration`.
  The only hit (two lines at the G.3 example) is the deliberate
  post-removal document, where the SGAI `<Event>` elements are empty by
  construction.

## Inventory + verdicts

| ID | Construct | Type | Placement | Verdict | Rationale |
|----|-----------|------|-----------|---------|-----------|
| C01 | `urn:svta:dash:sgai:2026` | XML namespace | all `svta:` elements | Conforming | DASH §5.2.1: *"the MPD shall be authored such that, after XML attributes or elements in the other namespaces than the DASH namespace are removed, the result is a valid XML document formatted according to that schema and that conforms to this document"*. Removal check 72/72. No `svta:` attribute is placed on a base element (0 occurrences). |
| C02 | `urn:svta:dash:sgai-overlay:2026` | event scheme | `EventStream@schemeIdUri`, main MPD Period | Conforming | Table 43: *"@schemeIdUri M identifies the message scheme. The string may use URN or URL syntax."* DASH §5.10.1: clients *"subscribe to an Event Stream of interest and ignore Event Streams that are of no relevance or interest"*. |
| C03 | `urn:svta:dash:sgai-pause-trigger:2026` | event scheme | as C02 | Conforming | As C02. |
| C04 | No `@value` on the two SGAI streams | scheme rule | `EventStream` | Conforming | Table 43: *"@value O ... The value space and semantics is expected to be defined by the owners of the scheme"*. |
| C05 | One stream per family per Period | placement rule | Period | Conforming | DASH §5.10.2.1: *"A Period shall contain at most one EventStream element with the same value of the @schemeIdUri attribute and the value of the @value attribute"*. No duplicate found in the examples. |
| C06 | Overlap order: presentation time, then position | ordering rule | Events of one stream | Conforming | Table 43: *"Events in Event Streams shall be ordered such that their presentation time is non-decreasing"*, so position among equal times is well defined; DASH §5.16.2.2.2 queue *"ordered by the presentation time PRT"*. 61/61 streams non-decreasing. |
| C07 | `<svta:OverlayPresentation>` | new element | child of `<Event>` | Conforming | `EventType` (§5.10.2.3) ends its sequence with `<xs:any namespace="##other" processContents="lax" .../>`; DASH §5.10.2.1: *"The Event element may contain further XML elements meaningful for a particular event scheme. These may be defined in this document ... or in some external namespace"*. |
| C08 | `<svta:PauseAdPresentation>` | new element | child of `<Event>` | Conforming | As C07. |
| C09 | `Event@id`, `@presentationTime`, `@duration` required on SGAI windows | attribute use | `<Event>` | Conforming | Tightening optional base attributes. Table 44: `@duration` *"The interpretation of the value of this attribute is defined by the scheme owner"*; `@id`: *"Each EventStream element shall not contain two Event elements with the same value of Event@id"* (no duplicate in examples). |
| C10 | `@maxDuration`, `@earliestResolutionTimeOffset`, `@executeOnce` on the `svta:` window elements | reused names on new elements | `svta:` attributes | Conforming | Types match `AlternativeMPDEventType` (`xs:unsignedLong`, `xs:unsignedLong`, `xs:boolean`). The spec's claim that the 60 s default lives in semantics, not the schema, is correct: the base schema declares `earliestResolutionTimeOffset` with no default, and §5.16.5.2 says *"The default is 60 seconds in units of timescale"*. The render-based trigger of `@executeOnce` is a semantic of an extension-namespace attribute, not a change to the base attribute. |
| C11 | `<InsertPresentation>` reused | inherited | `<Event>` | Conforming | DASH §5.16.3: *"The event shall not appear if the MPD type is "dynamic""*; no example places it in a dynamic MPD. |
| C12 | `<ReplacePresentation>` reused (`@returnOffset`, `@clip`, `@startWithOffset`) | inherited | `<Event>` | Conforming | Table 62: *"If the value of this attribute is "true", the alternative presentation shall terminate at the latest at time PRT + APDmax"*; also *"This attribute shall not be present if the @maxDuration attribute is absent"*, which the mandatory cap never triggers. |
| C13 | `@maxDuration` mandatory on every slot, including inherited linear events; absent means no ad | narrowing of a base attribute | `InsertPresentation`, `ReplacePresentation` | **Marginal** | See detail. The base schema carries a numeric default, `default="2251799813685247"`, so "absent" is not observable to a schema-defaulting parser. |
| C14 | `@skipAfter` and `PlaybackRestrictions@skipAfter` with base meaning | inherited | event; List MPD Period `ServiceDescription` | Conforming | §5.16.5.2: *"Zero duration implies that skipping is allowed everywhere ... Default value is PT0S"*; schema `default="PT0S"` on both (§5.16.6, K.4); Table K.18 exists as cited. Base example G.29.2 carries the per-ad restriction on a List MPD Period. |
| C15 | `@noJump` kept on linear, not declared on non-linear | inherited / exclusion | event | Conforming | §5.16.5.2 quote verified (*"... to any point where PHP > EAP without executing this event"*). The `svta:` elements do not declare it, so nothing is redefined. |
| C16 | List MPD as the linear resolution document | profile reuse | resolution document | Conforming | DASH §8.14 rules 1–5 verified verbatim (type `list`, URN in `@profiles`, no XLink, Linked or regular Periods, *"List MPDs shall not contain Alternative MPD events"*). 9 List MPDs in the examples pass all five. |
| C17 | Empty linear resolution: List MPD with one `PT0S` Period and no content | document shape | resolution document | Conforming | Table 4: *"At least one Adaptation Set shall be present in each Period unless the value of the @duration attribute of the Period is set to zero"*. §5.16.2.2.6 lists *"Alternative MPD is a List MPD, and merge process resulted in no available media"* as a failed execution, and *"A failed execution results in smooth continued playback of the main media presentation"*. |
| C18 | `svta:RenderableAsset`, `svta:Click`, metadata on a List MPD Period | extension content | after the DASH children of `<Period>` | Conforming | `PeriodType` closes with `<xs:any namespace="##other" processContents="lax" .../>`; order check 0 violations. `ImportedMPD` stays first, where `PeriodType` places it. |
| C19 | `<ImportedMPD>` and sub-MPDs on the Single-Period Static profile | inherited | List MPD Period | Conforming | DASH §5.3.2.6.1: *"MPDs referenced in the ImportedMPD element shall be restricted to the constraints of a single period profile as defined in 8.15"*. §8.15.2/§8.15.3 constraints checked on 24 sub-MPDs (type static, one Period with `@duration`, no `@mediaPresentationDuration`, none of the excluded MPD-level elements, no `ImportedMPD`). `ImportedMpdType@earliestResolutionTimeOffset` is `xs:double`, default `60.0`, as the spec states. |
| C20 | Sub-MPD reached by `@assetUrl` from a non-linear option | binding by statement | `svta:RenderableAsset` | Conforming | Keeps Table 4's *"This element shall not appear if the value of MPD@type is not "list""* by not nesting `<ImportedMPD>`; the SPS binding is imposed by this specification, which the base does not forbid. |
| C21 | Non-linear resolution document: static MPD, Full profile, one `PT0S` Period whose only child is `svta:OverlayList` | new document shape on base MPD | resolution document | Conforming | `MPDtype` requires only `@profiles`, `@minBufferTime` and one `Period`; Table 4 zero-duration rule as C17; DASH §8.2.1: *"The full profile includes all features and Segment Types defined in this document"*. 21 documents validate. |
| C22 | Claim: the document conforms as an MPD, not as a Media Presentation | profile-conformance reading | — | Conforming | DASH §8.1 separates the two tests: the profile-specific MPD removes elements *"in an extension namespace and not explicitly included by ProfA"*; a Media Presentation additionally needs *"at least one Representation in each Period in the profile-specific MPD"*. The spec claims only the first. |
| C23 | `svta:OverlayList` with `@family`, `@dismissAfter`, `@usableFor`, `@onCandidatesExhausted` | new element + attributes | Period of the non-linear document | Conforming | Extension content under `PeriodType`'s `##other` wildcard; validated by the §5.10 schema; negative control rejected a bad `@family`. |
| C24 | `svta:Candidate` content model: `<xs:any namespace="urn:mpeg:dash:schema:mpd:2011" processContents="strict" minOccurs="0"/>` for the callback `EventStream` | schema of the extension namespace | §5.10 | **Non-conforming** | See detail. `EventStream` has no global declaration in the base schema, so a strict wildcard rejects it; 15 of the spec's own example MPDs fail validation. |
| C25 | Callback `<EventStream>` directly inside `svta:Candidate`, times relative to the ad's own presentation | base element outside any base placement | `svta:Candidate` | **Marginal** | See detail. Table 44 defines `@presentationTime` *"relative to the start of the Period"*; this placement has no Period and the spec redefines the anchor. Legacy-safe (removed with its parent) and disclosed (§5.5.2), but the semantics of a base-namespace attribute are redefined. |
| C26 | Callback scheme reused for timeline beacons | inherited scheme | sub-MPD Period, List MPD Period, Candidate | Conforming | §5.10.4.5.1: *"A content author may use such an event for tracking play-back of specific content on a server that is not included in the media path"*. Table 47: `EventStream@value` `1`, `Event@messageData(deprecated)` / *"HTTP-URL Event value"*; `EventType` declares `messageData` `use="prohibited"` and `mixed="true"`. All callback streams in the examples carry `value="1"` and no `@messageData`. |
| C27 | `svta:RenderableAsset` | new element | `svta:Candidate`; List MPD Period | Conforming | Extension content; §5.10 schema validates it (negative control caught a missing `@assetUrl`). |
| C28 | Image and HTML creatives kept off `Representation` | exclusion | — | Conforming | DASH §7.3.1: *"The @mimeType attribute of each Representation shall be provided according to IETF RFC 4337"*, applied to SPS by §8.15.2 (*"The rules for the MPD as defined in subclause 7.3 shall apply"*); the List profile extends the CMAF profile, whose §8.12.4 sets *"The @mimeType shall be set to "<contentType>/mp4""*. |
| C29 | `svta:Click` / `svta:ClickTracking` | new element | `svta:Candidate`; List MPD Period | Conforming | Extension content, after DASH children. |
| C30 | `svta:AdSystem`, `AdTitle`, `Advertiser`, `UniversalAdId` | new elements | as C29 | Conforming | Extension content. |
| C31 | `custom` rectangle using the SRD coordinate convention | notation reuse, no SRD carrier | `svta:` attributes | Conforming | §H.2.2: *"the x-axis is oriented from left to right and the y-axis from top to bottom"*; §H.2.1: *"a comma-separated list of values"*; §H.1: *"SRD information shall be contained exclusively in these two MPD elements (AdaptationSet and SubRepresentation)"* — respected, since no SRD descriptor is emitted. |
| C32 | `RequestParam` inside the window's `EventStream`, after the `Event` entries | reused base mechanism | `EventStream` | Conforming | `EventStreamType` sequence is `Event`, `BaseURL`, `RequestParam`, …; Table 43: `RequestParam` *"specifies parameter(s) to be passed in a URL of an HTTP request issued by the client as a result of dispatching an event in this Event Stream"*. `$urn:mpeg:dash:state:cmcd#sid$` is valid: Table I.5 defines the suffix `cmcd#[key]`. `@includeInRequests` is *"a white spaced concatenated list of keys"*, default `"segment"`. |
| C33 | `urn:svta:dash:sgai-resolution:2026` request type | URN in `@includeInRequests` | `RequestParam` | Conforming | Table I.4: *"a URN or tag URI, where the request type semantics is understood by the client and specified by the URN / tag URI owner. The client shall drop unknown URIs from the @includeInRequests and @includeInHeaders strings prior to processing them as specified in this Annex."* |
| C34 | Legacy walk-through of Publisher-declared parameters (§4.7.5) | backward-compatibility statement | main MPD | **Marginal** | See detail. Using the mechanism obliges an `MPD.EssentialProperty` of scheme `urn:mpeg:dash:urlparam:2025`, whose non-recognition makes a client ignore the whole MPD (§5.8.4.8). §4.7.5 does not say so. |
| C35 | Reserved `sgai*` query parameters and `x-<vendor>-` prefix | request-URL convention | resolution request | Conforming | Not an MPD construct. The spec does not route them through the template mechanism, so the §I.2.3.3 placeholder rule (*"the string "<null> " shall be used as a replacement of the unknown scheme"*) is not engaged. |
| C36 | Pause measurement via the `PlayList` metric and `<Metrics>` on the main MPD | reused metric | main MPD | Conforming | Table D.5 key `PlayList`: *"A playback period is the time interval between a user action and whichever occurs soonest of the next user action, the end of playback or a failure that stops playback"*; `starttype` includes *"Resume - Resume from pause"*, `stopreason` includes `Rebuffering` and `UserRequest`. `MetricsType` requires `Reporting` (no `minOccurs`, so 1..N); `Metrics` follows `Period` in `MPDtype`, as in the examples. §8.15.2 excludes *"MPD.Metrics"* from SPS, as the spec says. |
| C37 | Decoder budget relying on listen mode during a linear ad | reading of the client model | — | Conforming | DASH §4.2: *"the alternative access engine outputs media to the media engine, while the main client will be paused or be in a listen mode"* and a listening engine *"does not output media to the media engine"*. |
| C38 | Rest of the §5.10 schema: simple types, lists, `svta:` elements, `xs:import` of the base schema | schema of the extension namespace | §5.10 | Conforming | Compiles against the official `DASH-MPD.xsd`; the `LayoutListType` `xs:list` matches the base's whitespace list typing (`StringVectorType`, *"Whitespace-separated list of strings"*). Minor: the prose says the schema imports the base *"for `EventStreamType`"*, but no declaration references that type (see C24). |
| C39 | No profile and no Interoperability Point minted | profile policy | — | Conforming | DASH §8.1: *"The owner of the URI is responsible to provide sufficient semantics on the restrictions and permission of this interoperability point"* — quoted accurately; the Full profile is declared instead. |
| C40 | `urn:svta:` URN prefix for the scheme and request-type URIs | URI choice | §2.1 | Conforming | The base only requires URN or URL syntax (Table 43). Whether `svta` is a registered URN namespace identifier is not a DASH question; see Open questions. |

## Base-standard findings (highlights)

- The extension points the spec relies on are the ones the base schema
  actually opens: `##other` lax wildcards at the end of `EventType`,
  `EventStreamType`, `PeriodType` and `MPDtype`, and the §5.2.1 removal
  obligation. The official schema confirms all placements (72/72 valid
  after removal).
- The base schema declares exactly one global element in the MPD
  namespace, `MPD` (the only top-level `xs:element` of `DASH-MPD.xsd`).
  Every other base element, `EventStream` included, is local to its
  parent type. That single fact makes C24 fail.
- `AlternativeMPDEventType` carries schema defaults for `maxDuration`
  (`2251799813685247`), `executeOnce`, `noJump` and `skipAfter`, and
  none for `earliestResolutionTimeOffset`. The spec relies on the
  `skipAfter` schema default (§5.2.4) but not on the `maxDuration` one
  (C13).
- Every other quotation the spec attributes to the base (§5.16.x, §8.1,
  §8.14, §8.15, Table I.4, §5.10.4.5, Annex D/H/K/L, §5.8.5.16, §5.11.3,
  §5.3.7.2, §5.3.11.1) was found literally under the cited clause.

## Non-conforming items detail

### C24 — strict wildcard for the base `EventStream` in `svta:Candidate`

- **Rule.** The base schema defines `EventStream` only as a local element
  (`<xs:element name="EventStream" type="EventStreamType" .../>` inside
  `PeriodType`, §5.3.2.3); `DASH-MPD.xsd` has no top-level declaration
  for it. Under W3C XML Schema, a `strict` wildcard requires a global
  declaration for the matched element (or an `xsi:type`).
- **Conflict.** §5.10 declares
  `<xs:any namespace="urn:mpeg:dash:schema:mpd:2011" processContents="strict" minOccurs="0"/>`.
  Every document carrying a callback stream inside a candidate fails
  validation. Measured: 15 of the 72 example MPDs fail, each with
  *"Element '{urn:mpeg:dash:schema:mpd:2011}EventStream': No matching
  global element declaration available, but demanded by the strict
  wildcard."* A control element with a global declaration (`MPD`) passes
  the same wildcard. §4.6 step 2 (*"validates strictly as the base
  `EventStreamType`"*) cannot be met with the schema as written.
- **Suggested fix** (HOW; no requirement changes). Options:
  1. `processContents="lax"`, with the `EventStreamType` check done by
     §4.6 step 3 (or by the validator binding the element to
     `dash:EventStreamType` explicitly). Smallest change; keeps the base
     element and its namespace. Under `lax` without a global declaration
     the element is **not** checked by the schema, so §4.6 has to say so.
  2. Require `xsi:type="dash:EventStreamType"` on that element in
     instances. Schema-checkable, but unusual for authors.
  3. An `svta:` element of type `dash:EventStreamType`. Schema-checkable,
     but the element leaves the base namespace, which contradicts the
     spec's "the callback scheme is reused, in its base element"
     position (§5.5, §4.7) and needs that position re-argued.
  Whichever is chosen, the §5.10 prose about importing the base schema
  "for `EventStreamType`" should match what the schema does.

## Marginal items detail

### C13 — `@maxDuration` "absent" versus the base schema default

- **Ambiguity.** The base schema declares
  `<xs:attribute name="maxDuration" type="xs:unsignedLong" default="2251799813685247"/>`,
  and §5.16.5.2 says *"If absent, the value is assumed to be infinity"*
  / *"Default: Infinity"*. A parser that applies schema defaults hands the
  Player `2251799813685247`, not "absent", so the rule "a slot without a
  cap presents no ad" (§4.8.3, §5.1.1) cannot be applied to what that
  Player sees. The §5.1.1 table says "none under this specification (the
  base default is infinity)", which omits that the base default is
  carried in the schema. The spec also treats the two schema defaults of
  the same element differently: it honours the `skipAfter` default
  (§5.2.4, *"every linear event has a skip value under the base
  schema"*) and overrides the `maxDuration` one.
- **Suggested clarification.** State that the requirement applies to the
  authored document (the attribute is lexically present), and say what a
  Player of this specification does when it can only see the defaulted
  value. For example, treat `2251799813685247` as "not declared", or
  require the Player to read the attribute before defaults are applied.
  One sentence in §5.1.1 / §4.8.3.

### C25 — callback `EventStream` outside any Period

- **Ambiguity.** Table 44: `@presentationTime` *"specifies the
  presentation time of the event relative to the start of the Period,
  taking into account the @presentationTimeOffset of the Event Stream"*.
  Inside `svta:Candidate` there is no Period; §5.5.3 re-anchors the time
  to the start of the selected option. The base does not forbid this,
  because the element sits under extension content and a base client
  removes it. It is still a base-namespace element whose attribute
  semantics are redefined by placement, and `EventStream@presentationTimeOffset`
  (*"aligns with the start of the Period"*) has no stated meaning there.
- **Suggested clarification.** In §5.5.3, state what
  `@presentationTimeOffset` means on a candidate-level stream: forbidden,
  or subtracted from the option-relative time. Say explicitly that
  Table 44's Period anchor is replaced, not extended.

### C34 — the MPD-level `EssentialProperty` that Annex I requires

- **Ambiguity.** DASH §I.3.1: *"An MPD.EssentialProperty element with
  the attribute @schemeIdUri having value of "urn:mpeg:dash:urlparam:2025"
  shall be present and have no content"*. DASH §5.8.4.8: *"If the scheme
  or the value for this descriptor is not recognized, the DASH Client is
  expected to ignore the parent element that contains the descriptor"*.
  The parent is the MPD. §5.8.1 quotes the first sentence and Annex B
  shows the descriptor. But §4.7 says no SGAI construct uses carrier class
  (c2), and §4.7.5's walk-through does not mention that a Publisher using
  `<RequestParam>` to reach the non-linear request brings a (c2)
  descriptor at MPD level. A client that does not know the URL-parameter
  scheme drops the whole main MPD. This is a base consequence, not an
  SGAI one.
- **Suggested clarification.** One line in §4.7.5 (or the §4.7.6 row):
  the request-type URN is safe per Table I.4's drop rule, and the
  mechanism it rides on carries an MPD-level `EssentialProperty` whose
  legacy cost is the base specification's (§5.8.4.8).

## Open questions surfaced

- **`urn:svta` as a URN namespace identifier.** Searched the primary copy
  for rules on URN registration for scheme URIs: Table 43 says only
  *"The string may use URN or URL syntax"* and recommends a dated form
  for URLs. It sets no registration requirement. Whether `svta` is a
  registered URN NID (RFC 8141) was not checked `[inferred]`. This is
  outside DASH conformance, but an unregistered NID is a question a WG
  reviewer may raise.
- No `[fetch-failed]` items. Every clause the spec cites was located.
  The full MPD schema is outside the primary copy by the standard's own
  design (Annex B points to the published `DASH-MPD.xsd`), and that
  published file was used.

## Summary

- Total constructs audited: 40
- Conforming: 36
- Marginal: 3 (C13, C25, C34)
- Non-conforming: 1 (C24)

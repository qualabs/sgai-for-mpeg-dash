[GROUNDED_BY=notebooklm]

# DASH conformance audit — v7 (2026-09-16)

**Audit target**: `../output/v7-sgai-spec.md`.
**Reference**: MPEG-DASH 6th edition — ISO/IEC 23009-1:2026(en), Sixth
edition, 2026-07.
**Method**: inventory + grounded queries against the DASH 6th notebook
+ per-construct verdict.

## Scope

Every construct the spec introduces or re-uses in a new position is
checked against the 6th edition: MPD schema validity, the §5.2.1
extension rules, event placement inside `EventStream`, profile
restrictions (§8.14 List MPD, §8.15 Single-Period Static), and
attribute semantics inherited from baseline DASH. Design quality,
requirement coverage and internal consistency are out of scope except
where an internal claim about the base specification is itself false.

## Method summary

- Inventory built from §2.1, §4.7.3, §5.1 to §5.8, and every XML
  listing in Annexes A to M (`grep '<Event '`, `<EventStream`,
  `<MPD`, `<Period`, `<ImportedMPD>`, `svta:*`).
- 9 NotebookLM queries answered against the DASH 6th notebook
  (`NOTEBOOK_ID=bb67e20c-9ad1-4a1d-a641-7c7d901f93cb`): `PeriodType` +
  `ImportedMPD` + the AdaptationSet-per-Period rule; `EventStreamType`
  + `EventType`; the callback scheme; §8.14; §8.15 + §7.3; the §5.16
  attribute tables; §5.16.2.2 + §5.16.5.2; `MPDtype` order and
  mandatory attributes; Annex I + §5.8.4.8.
- Every grounded claim was then re-checked against the primary copy of
  ISO/IEC 23009-1:2026. The two sources agreed on every point. Where a
  verdict rests on schema or clause text, that text is quoted verbatim
  below, so the reader can audit the verdict without opening either
  source.
- Each construct assessed Conforming / Marginal / Non-conforming.

## Inventory + verdicts

| ID | Construct | Type | Placement | Verdict | Rationale |
|----|-----------|------|-----------|---------|-----------|
| C1 | `urn:svta:dash:sgai:2026` | XML namespace | all SVTA elements | Conforming | §5.2.1 requires only that removing all non-DASH-namespace elements leaves a schema-valid MPD. Verified on every listing in Annexes A–M. |
| C2 | `urn:svta:dash:event:sgai-overlay:2026` | `EventStream@schemeIdUri` | `Period` child, main MPD | Conforming | `PeriodType` declares `EventStream` 0..N; `@schemeIdUri` is the only required attribute (5.10.2.3). Unknown scheme ⇒ per-scheme skip. |
| C3 | `urn:svta:dash:event:sgai-pause-trigger:2026` | `EventStream@schemeIdUri` | `Period` child, main MPD | Conforming | Same as C2. |
| C4 | `<svta:OverlayPresentation>` | element + attributes | `Event` child | Conforming | `EventType` sequence ends with `<xs:any namespace="##other" processContents="lax" .../>` (5.10.2.3). The listings carry no `SupplementalProperty`/`EssentialProperty` sibling, so sequence order holds. |
| C5 | `<svta:PauseAdPresentation>` | element + attributes | `Event` child | Conforming | Same as C4. |
| C6 | `<svta:OverlayList>` | element | `Period` child, resolution doc | Conforming | `PeriodType` sequence ends with `<xs:any namespace="##other" .../>`; it is the Period's only child in every listing, so it sits last. |
| C7 | `<svta:Candidate>`, `<svta:RenderableAsset>`, `<svta:BackgroundElement>`, `<svta:Click>`, `<svta:ClickTracking>`, `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>`, `<svta:UniversalAdId>` | elements + attributes | inside the SVTA subtree | Conforming | Validated `lax` under the `##other` wildcard; removal leaves a valid MPD. |
| C8 | Zero-duration `Period` carrying no `AdaptationSet` (§5.2.2.1) | compound | resolution doc | Conforming | Table 4, `AdaptationSet` row, verbatim: *"At least one Adaptation Set shall be present in each Period unless the value of the @duration attribute of the Period is set to zero."* |
| C9 | Empty resolution document, non-linear (§5.2.3) | compound | resolution doc | Conforming | Schema-valid by C8; `Period` `minOccurs` defaults to 1 so the single Period is required. |
| C10 | Empty resolution document, linear `ListMPD` (§5.2.3) | compound | resolution doc | Conforming *as a document* | Schema-valid by C8. Its **runtime** treatment is NC5. |
| C11 | `MPD@type="list"` + `urn:mpeg:dash:profile:list:2024` in `@profiles` | MPD attributes | `ListMPD` | Conforming | §8.14(1)(2): *"List MPDs shall have the value of the MPD@type attribute set to \"list\"."* §5.3.1.4 defines the value. |
| C12 | `ListMPD` carries no XLink and no Alternative MPD events | profile constraint | `ListMPD` | Conforming | §8.14(3)(5), quoted by the spec without distortion. |
| C13 | `<ImportedMPD>` in a `ListMPD` Period; URL as text content; `@earliestResolutionTimeOffset` `xs:double` default `60.0` | baseline reuse | `Period` first child | Conforming | `ImportedMpdType` is `xs:simpleContent` extending `xs:anyURI` with that single attribute and default. Matches §5.2.1.3 exactly, including the unit note (seconds here, `@timescale` units on the slot events). |
| C14 | Sub-MPD bound to `urn:mpeg:dash:profile:sps:2024`, `@type="static"`, exactly one `Period` with `@duration` | baseline reuse | sub-MPD | Conforming | §8.15.2: *"The value of MPD@type shall be \"static\""*, *"One and only one Period element shall be present"*, *"The MPD@mediaPresentationDuration attribute shall not be present, but the Period element shall include the @duration attribute"*. The spec's sub-MPD table matches; no listing declares `@mediaPresentationDuration`. |
| C15 | RFC 4337 restriction on the `@mimeType` axis (§4.7.2) | inherited constraint | sub-MPD, `ListMPD` inline AS | Conforming | §8.15.2 → §7.3; §7.3.1: *"The @mimeType attribute of each Representation shall be provided according to IETF RFC 4337."* The CMAF chain the spec invokes for inline `AdaptationSet`s also holds: §8.12.4 requires *"The @mimeType shall be set to \"&lt;contentType&gt;/mp4\""*. |
| C16 | `<InsertPresentation>` attribute block (§5.1.1) | baseline reuse | `Event` child | Conforming | Matches `AlternativeMPDEventType` attribute-for-attribute: `@uri` required, `@earliestResolutionTimeOffset` `xs:unsignedLong`, `@serviceDescriptionId` `xs:unsignedInt`, `@maxDuration` `xs:unsignedLong` default `2251799813685247`, `@executeOnce` `xs:boolean` default `false`, `@noJump` `xs:integer` default `0`, `@skipAfter` `xs:duration` default `PT0S`. |
| C17 | `<ReplacePresentation>` delta attributes (§5.1.2) | baseline reuse | `Event` child | Conforming | `AlternativeMPDReplaceEventType` extends the above with `@returnOffset` `xs:unsignedLong`, `@clip` `xs:boolean` default `true`, `@startWithOffset` `xs:boolean` default `false`. |
| C18 | Insert event absent when `MPD@type="dynamic"` (§5.1.1) | inherited constraint | main MPD | Conforming | §5.16.3: *"The event shall not appear if the MPD type is \"dynamic\"."* |
| C19 | `@maxDuration` units and termination (§5.16.5.2 reuse) | inherited semantics | slot events | Conforming | Table 63: *"specifies maximum duration of the Alternative Presentation, expressed in units of EventStream@timescale"*, and *"If the value of @maxDuration is zero, the event is not executed."* |
| C20 | Callback scheme reused as the tracking carrier; URL in the `Event` element's content | baseline reuse | sub-MPD `Period` | Conforming | Table 47 (§5.10.4.5.3) puts the HTTP-URL in the Event value space; `@messageData` is `use="prohibited"` in the schema and annotated *"Deprecated in favor of carrying the message information in the value space of the event"*. |
| C21 | Callback `EventStream` inside the sub-MPD `Period` (§5.5.2, linear row) | baseline reuse | `Period` child | Conforming | Canonical: the 6th edition's own List MPD example (G.29.2) carries exactly this shape. |
| C22 | Two `EventStream`s of different schemes in one `Period` (Annex G.4 dual path) | authoring pattern | main MPD | Conforming | `PeriodType` declares `EventStream` `maxOccurs="unbounded"`. |
| C23 | `@includeInRequests="altmpd"` token exists | baseline reuse | `RequestParam` | Conforming *as a token* | Table I.4 lists `altmpd`. Its **scope** for non-linear slots is M5. |
| C24 | `$urn:mpeg:dash:state:video$`, `$urn:mpeg:dash:state:cmcd#sid$` | state vocabulary | `@queryTemplate` | Conforming | Both suffixes are in Table I.5; `@queryTemplate` is an `UrlQueryInfoType` attribute (Table I.1). |
| C25 | No Annex F Interoperability Point introduced (§4.7.1) | non-construct | — | Conforming | Nothing in the spec adds a delivery format or IOP URI; the claim holds against the document. |
| C26 | Reserved capability query parameters (§5.8.2) | HTTP query string | resolution request | Conforming | Not an MPD construct; `x-<vendor>-` prefixing keeps future reserved names free. No DASH rule governs them. |
| NC1 | Tracking `<Event>@id` typed `xs:string`, authored as `b1`…`b6` | baseline attribute | callback `EventStream` | **Non-conforming** | Schema declares `<xs:attribute name="id" type="xs:unsignedLong"/>`. |
| NC2 | `<RequestParam>` nested inside `<EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025">` | baseline reuse | MPD level | **Non-conforming** | Annex I.3.1 requires the descriptor to be **empty** and `RequestParam` to be a sibling-level element. |
| NC3 | MPD-level `<EssentialProperty>` authored **before** `<Period>` (Annex A.2) | document order | main MPD | **Non-conforming** | `MPDtype` is an `xs:sequence` in which `EssentialProperty` follows `Period`. |
| NC4 | `MPD@profiles` described as a "whitespace-separated list" (§5.2.2.2, §5.1.3.1) | baseline attribute | resolution doc | **Non-conforming** | §8.1 defines `@profiles` as a **comma-separated** list. |
| NC5 | §4.6.8 narrows the §5.16.2.2 fall-through for the linear family | runtime semantics | Player | **Non-conforming** | §5.16.2.2.6 makes a zero-duration / no-media alternative an execution **failure**, and §5.16.2.2.5 requires the client to try the next event in the queue. |
| M1 | Callback `<EventStream>` directly inside `<svta:Candidate>` | baseline element, novel parent | resolution doc | Marginal | No global element declaration ⇒ unvalidatable; the scheme's timing anchor is defined against a `Period` that is not there. |
| M2 | Core-namespace `<ImportedMPD>` inside `<svta:RenderableAsset>` | baseline element, novel parent | resolution doc | Marginal | Same declaration problem, plus the Linked-Period resolution model (§5.3.2.6.3) does not apply in this parent. |
| M3 | `EventStream@value` declared optional and "informational" for the callback scheme (§5.5.1) | baseline attribute | resolution doc | Marginal | Table 47 fixes `EventStream@value` = 1 for this scheme. |
| M4 | A `ListMPD` carrying `<svta:Click>` (Annex K.3) declares only the MPEG list profile | profile signalling | `ListMPD` | Marginal | §8.1 step 4 removes extension-namespace content *not explicitly included by* the declared profile. |
| M5 | `altmpd` used to scope a query template to an overlay / pause-ad resolution request | token scope | main MPD | Marginal | Table I.4 binds `altmpd` to §5.16 alternative-MPD requests; the SGAI non-linear request is not one. |
| M6 | MPD-level `EssentialProperty` vs the legacy-playback guarantee | descriptor semantics | main MPD | Marginal | §5.8.4.8 NOTE 1/NOTE 2: an unrecognised MPD-level `EssentialProperty` leads a client to ignore the parent element, and to terminate the presentation when none can be processed. |
| M7 | `Period@start="PT0S"` in the sub-MPDs of Annexes A.5 and C.5 | profile guidance | sub-MPD | Marginal | §8.15.3: *"Period@start attribute should not be present. If present, its value shall be 0."* SHOULD-level only. |
| M8 | `@earliestResolutionTimeOffset` default tagged `[inferred]` (§5.1.1) | provenance | spec text | Marginal | The value is normative in Table 63, not merely prose: *"The default is 60 seconds in units of timescale."* |
| M9 | Normative reference given as "ISO/IEC 23009-1:2025 … FDIS stage" (§2) | citation | spec text | Marginal | The published 6th edition is ISO/IEC 23009-1:**2026**, dated 2026-07. |

## NotebookLM findings (highlights)

- **`EventType` / `EventStreamType` (5.10.2.3)** — the notebook returned
  the schema verbatim: `Event@id` is `xs:unsignedLong`;
  `@contentEncoding` and `@messageData` are `use="prohibited"`; the
  content model is `mixed="true"` with a leading choice of
  `SelectionInfo` / `ServiceDescription` / `InsertPresentation` /
  `ReplacePresentation`, then descriptors, then
  `<xs:any namespace="##other" processContents="lax"/>`. It also stated
  that at MPD level `EventStream` *"appears exclusively inside the
  `<Period>` element (PeriodType, subclause 5.3.2.3)"*.
- **`PeriodType` and `ImportedMPD` (5.3.2.3, 5.3.2.6.2)** — the
  foreign-namespace wildcard is the **last** particle of the Period
  sequence, so an SVTA child must follow every DASH child present.
  `ImportedMPD` is *"declared locally within the `<xs:sequence>` of
  PeriodType … not declared as a global top-level element"*; its type
  `ImportedMpdType` extends `xs:anyURI` by simple content with
  `@earliestResolutionTimeOffset` `xs:double` default `60.0`.
- **AdaptationSet-per-Period (Table 4)** — quoted verbatim and matching
  the spec's use of `PT0S` as the licence for a Period with no
  `AdaptationSet`.
- **Callback scheme (5.10.4.5)** — URL in the element value space,
  `EventStream@value` = 1 per Table 47, permitted both as an MPD event
  under a `Period` and inband, and `Event@presentationTime` is
  *"relative to the start of the Period, taking into account the
  @presentationTimeOffset of the Event Stream"*.
- **§8.14 List MPD** — `MPD@type="list"` is mandatory for the profile
  and `list` is a first-class value of `MPD@type` (§5.3.1.4); XLink and
  Alternative MPD events are forbidden; Linked and regular Periods are
  both admissible.
- **§8.15 / §7.3** — the Single-Period Static profile inherits the §7.3
  MPD rules, which pin `Representation@mimeType` to RFC 4337.

- **`MPDtype` (5.3.1.3)** — the notebook returned the root sequence and
  stated that *"EssentialProperty (item 13) and SupplementalProperty
  (item 14) sit after `<Period>` (item 11) and after `<Metrics>`
  (item 12)"*, and that `PresentationType` admits `static`, `dynamic`
  and `list`.
- **Annex I.3.1 and §5.8.4.8** — *"The RequestParam element itself is
  carried directly as a child element of DASH hierarchy elements — not
  nested inside EssentialProperty or SupplementalProperty
  descriptors"*, with the root-level descriptor *"with no content"*;
  `altmpd` is *"all requests for MPDs representing the alternative
  Media Presentation, as defined in subclause 5.16"*; and an
  unrecognised `EssentialProperty` obliges the client to ignore the
  parent element, terminating the presentation when the descriptor is
  at MPD level.

Every one of these was re-checked against the primary copy of
ISO/IEC 23009-1:2026; no divergence was found between the two sources.

## Non-conforming items detail

### NC1 — Tracking `Event@id` is a string

**Where**: §5.5.1 attribute table (`@id` | yes | `xs:string`), the
skeleton in §5.2.2.1, and every callback `<Event>` in Annexes A, C, D,
E, I, J, K and M (`id="b1"` … `id="b6"`).

**Rule**: ISO/IEC 23009-1:2026, 5.10.2.3:

```xml
<xs:attribute name="id" type="xs:unsignedLong"/>
```

Table 44 adds that `@id` is Optional, that events with equivalent
content share the value, and that no `EventStream` carries two `Event`
elements with the same `@id`.

**Conflict**: `b1` is not a lexical value of `xs:unsignedLong`, so every
resolution document and every sub-MPD in the spec fails schema
validation at Annex B. This is not cosmetic: T-P17 in Annex N asks an
implementer to validate the spec's own documents against the base
schema, and those documents fail on this attribute.

**Suggested fix**: retype `@id` as `xs:unsignedLong` in §5.5.1 and
renumber every example (`b1`→`1`, …). Keeping the "required" strength is
fine — it narrows an optional baseline attribute, which a profile may
do. If a human-readable beacon label is wanted, carry it as
`<svta:*>` metadata on the candidate, not on `Event@id`.

### NC2 — `RequestParam` nested inside the `urlparam:2025` descriptor

**Where**: §5.8.1 listing and Annex A.2.

**Rule**: Annex I.3.1, `urn:mpeg:dash:urlparam:2025` signalling:

> — An `MPD.EssentialProperty` element with the attribute
> `@schemeIdUri` having value of `"urn:mpeg:dash:urlparam:2025"`
> **shall be present and have no content**, unless the scheme is
> explicity allowed in a profile …
> — The `RequestParam` element(s) may be present in elements such as
> but not limited to `MPD`, `Period`, `AdaptationSet`,
> `Representation`, `Preselection`, or `EventStream`.

with the NOTE that *"As opposed to other elements of type
ExtendedUrlInfoType, RequestParam is defined in the main DASH schema"*.

**Conflict**: two independent violations. The descriptor is authored
with content, which the clause forbids; and `DescriptorType` admits only
`<xs:any namespace="##other">`, so a `RequestParam` in the DASH
namespace is not a legal child of it under Annex B either.

**Suggested fix**: adopt the 6th edition's own shape, example G.29.1:

```xml
<MPD …>
  <Period id="1">
    <EventStream timescale="1000"
                 schemeIdUri="urn:mpeg:dash:event:alternativeMPD:insert:2025">
      <Event id="101" presentationTime="0" duration="20000">
        <InsertPresentation uri="…" maxDuration="20000"/>
      </Event>
      <RequestParam includeInRequests="altmpd"
                    queryTemplate="session_id=$urn:mpeg:dash:state:cmcd#sid$"/>
    </EventStream>
    …
  </Period>
  <EssentialProperty schemeIdUri="urn:mpeg:dash:urlparam:2025"/>
</MPD>
```

Placing `RequestParam` inside the slot's own `EventStream` also removes
the need for §5.8.3's collision rule to be stated as broadly as it is:
the template is then scoped to the slot that owns it.

### NC3 — MPD-level descriptor authored before `Period`

**Where**: Annex A.2, where `<EssentialProperty>` precedes
`<Period id="1">`.

**Rule**: `MPDtype` is an `xs:sequence` whose order is
`ProgramInformation`, `BaseURL`, `Location`, `PatchLocation`,
`RequestParam`, `ServiceDescription`, `InitializationSet`,
`InitializationGroup`, `InitializationPresentation`,
`ContentProtection`, **`Period`**, `Metrics`, **`EssentialProperty`**,
`SupplementalProperty`, `UTCTiming`, `LeapSecondInformation`,
`ContentSteering`, `xs:any`.

**Conflict**: XML Schema sequences are ordered, so the Annex A.2 MPD
does not validate. The 6th edition's own example G.29.1 puts the same
descriptor after `</Period>`.

**Suggested fix**: move the element after the last `</Period>` in
Annex A.2, and add a sentence to §5.8.1 stating the position, since a
reader copying the listing will otherwise reproduce the error.

### NC4 — `MPD@profiles` is comma-separated, not whitespace-separated

**Where**: §5.2.2.2 (`@profiles` | yes | *whitespace-separated list of
`xs:anyURI`*) and, as a supporting argument, §5.1.3.1's encoding note,
which justifies `@allowedLayouts` by claiming it matches *"the encoding
the base specification already uses for `@profiles`, `@codecs` and
`@dependencyId`"*.

**Rule**: §8.1: *"The identifier of a profile shall not contain any
comma. The profiles with which an MPD complies are indicated in the
MPD@profiles attribute as a comma-separated list of profile
identifiers."*

**Conflict**: an APS that follows §5.2.2.2 literally and emits two
profile URIs separated by a space produces a `@profiles` value that the
base specification reads as a single, non-existent profile identifier.
No listing in the document trips it, because every one declares exactly
one profile URI — the defect is in the normative table, and it fires the
first time a second URI is added (which M4 asks for).
The mis-citation also weakens §5.1.3.1: of the three attributes named,
`@profiles` is comma-separated and `@codecs` is comma-separated (RFC
6381 `simp-list`); only `@dependencyId` is whitespace-separated.

**Suggested fix**: change the §5.2.2.2 type to "comma-separated list of
`xs:anyURI`". In §5.1.3.1, cite `@dependencyId` (and any other
`StringVectorType` attribute) as the precedent and drop `@profiles` and
`@codecs`. `@allowedLayouts` itself is an SVTA attribute and may stay
whitespace-separated; only its justification is wrong.

### NC5 — The fall-through narrowing is a change to baseline Player semantics

**Where**: §4.6.8 and its inline divergence blockquote; §5.2.3
("Linear"); §8.1 rows E3 and E5; test T-E5.

**Rule**: §5.16.2.2.6:

> Execution fails if at least one of the conditions below is true at
> PRTA:
> — APDA is determined to be 0.
> — `@executeOnce` is set to "true", and E.c > 0 …
> — The playback of the alternative presentation cannot start. The
> reasons for this include (but are not limited to) …: Alternative MPD
> is unavailable or invalid. Alternative MPD is a List MPD, and merge
> process resulted in no available media. …

and §5.16.2.2.5, step 2:

> b) If the event is active, it will be executed. This event will be
> removed from the queue irrespective of the success of its execution.
> c) If execution succeeds, processing stops here.
> d) If execution fails, steps a-c above are repeated for next events in
> QE, until: Execution succeeds, or PRT of the topmost event in the
> queue is in the future, or The queue is empty.

**Conflict**: for a linear slot, the spec's no-fill document is a
`ListMPD` with one `PT0S` Period and no `ImportedMPD` — exactly
"APDA is 0" and "merge process resulted in no available media". The base
model therefore classifies it as an execution failure and requires the
client to attempt the next queued event; §4.6.8 requires the opposite
("the Player serves that answer … and leaves the remaining windows
untouched"), and T-E5 makes the un-requested fallback the pass
observable. A Player built to T-E5 fails a base-specification
conformance check on §5.16.2.2.5; a Player built to §5.16.2.2.5 fails
T-E5. The same tension applies to E3: the base spec explicitly names an
invalid alternative MPD as an execution failure, while E3 leaves the
choice open.

This also contradicts the spec's own document-level obligation in §4.1
that "no pre-existing base specification semantics are altered", and the
§1 claim that the specification "alters no baseline semantics". The
divergence blockquote in §4.6.8 acknowledges the change but does not
reconcile it with those two statements.

**Suggested fix**, in order of decreasing cost to the design:

1. Scope the narrowing to the families the base model does not govern.
   Overlay and pause-ad windows are not Alternative MPD events, so
   §4.6.8 can stand for them unchanged; for the linear family, state
   that §5.16.2.2.5 applies as written and that the "resolved to no
   ads" signal is not available there. §4.1's no-alteration claim then
   holds.
2. Keep one rule across families but stop expressing linear no-fill as
   a zero-duration presentation — e.g. a `ListMPD` carrying one Period
   with an SVTA no-fill marker and a non-zero `@duration` is not an
   APDA-0 case, though it then has to satisfy Table 4 by carrying an
   `AdaptationSet`.
3. Keep the text as it is and delete the no-alteration claims from §1
   and §4.1, replacing them with an explicit statement that a Player
   conforming to this specification does not conform to §5.16.2.2.5.
   This is the honest minimum; it is also the option that makes the
   spec's backward-compatibility story weaker than it currently reads.

## Marginal items detail

### M1 — Callback `EventStream` inside `<svta:Candidate>`

§5.5.2 makes the candidate-level position equivalent to the sub-MPD
position, and §8.8 already flags it as novel. Three consequences the
spec does not state:

- `EventStream` is declared **only** locally inside `PeriodType`. There
  is no global element declaration, so under `processContents="lax"` a
  validator does not check it at all: the construct is unvalidatable
  rather than valid.
- Table 44 defines `Event@presentationTime` as *"relative to the start
  of the Period"*. Inside a candidate there is no Period, so §5.5.3 has
  to redefine the origin. That redefinition of a baseline scheme's
  timebase is a semantic extension of `urn:mpeg:dash:event:callback:2015`,
  which §5.5 elsewhere claims to reuse "as-is".
- §5.2.1 reserves extension of the DASH namespace to ISO/IEC. Reusing an
  existing DASH element in an undeclared parent is not literally adding
  to the namespace, but it lands in the same grey area and gets no
  ignore-if-unknown guarantee from the base specification.

**Suggested clarification**: carry the beacons in the SVTA namespace
when they are not inside a Period — e.g. `<svta:TrackingEvents>` with
`<svta:Beacon presentationTime="…" id="…">URL</svta:Beacon>` children,
declared in the SGAI schema with the same timebase §5.5.3 already
defines. The sub-MPD position stays on the baseline carrier, where it is
canonical (C21). This also dissolves M3 and NC1 for the non-linear case.

### M2 — `<ImportedMPD>` inside `<svta:RenderableAsset>`

Same declaration problem as M1: the element is local to `PeriodType`,
and its processing model (§5.3.2.6.3) is a **merge into the enclosing
Period** — attributes of the Linked Period take precedence, the
imported Period's elements override, the `ImportedMPD` element is
removed, and the Linked Period becomes a regular Period. None of that is
meaningful inside a `RenderableAsset`, where the spec wants only "fetch
this sub-MPD and render it". §5.3.4's argument that "§5.3.2.6 does not
constrain the parent of `<ImportedMPD>`" is true of the prose and false
of the schema, where the parent is the only place the element exists.

**Suggested clarification**: use `<svta:ImportedMPD>` (or an `@mpdUrl`
attribute on the option) and state that the referenced document is
bound to the Single-Period Static profile, which is the only part of
§5.3.2.6 the construct actually needs. Keep `<ImportedMPD>` where a
real Linked Period exists — i.e. inside the `ListMPD` (C13).

### M3 — `EventStream@value` for the callback scheme

§5.5.1 marks `@value` "Required: no" and calls it *"informational at the
Player level"*. Table 47 lists `EventStream@value` = 1 as the parameter
value for this scheme; the base specification's own List MPD example
carries `value="1"`. A Player keyed on Table 47 will not recognise a
callback `EventStream` emitted without it.

**Suggested clarification**: make `@value` required with fixed value
`1`, matching Table 47, and drop the "informational" characterisation.

### M4 — SVTA elements in a `ListMPD` that does not declare the SGAI profile

Annex K.3 states that a linear `ListMPD` Period may carry
`<svta:Click>` as foreign-namespace open content. §8.1's profile
conformance procedure, step 4, removes *"All elements or attributes that
are … in an extension namespace and not explicitly included by ProfA"*.
A `ListMPD` whose `@profiles` names only `urn:mpeg:dash:profile:list:2024`
therefore has its `<svta:Click>` removed for conformance checking, and a
list-profile client is entitled to drop it. The construct is also
unmentioned by §5.6, which says the element is a child of
`<svta:Candidate>`.

The same rule reaches the **main MPD**, where it is benign but
unremarked: every main-MPD listing declares exactly one baseline
profile URI — `urn:mpeg:dash:profile:isoff-on-demand:2011`, or
`urn:mpeg:dash:profile:isoff-live:2011` in Annex B — and nothing
else, so the SGAI `EventStream`s are extension content not explicitly
included by the declared profile. That is exactly the ignore-if-unknown
outcome §4.7 wants for a legacy Player, but it also means a current
Player has no profile signal telling it the document carries SGAI
constructs.

**Suggested clarification**: require any `ListMPD` carrying SVTA
elements to include `urn:svta:dash:profile:sgai-overlay-list:2026` (or a
sibling linear profile URI) in `MPD@profiles`, move the rule out of
Annex K into §5.6 where the carrier is defined, and decide explicitly
whether a main MPD carrying SGAI slots declares an SGAI profile URI —
§2.1 currently mints a profile URI for resolution documents only.

### M5 — `altmpd` on a non-linear resolution request

Table I.4 defines `altmpd` as *"all requests for MPDs representing the
alternative Media Presentation, as defined in subclause 5.16"*. An
overlay or pause-ad resolution request is triggered by an SVTA event
scheme, is answered by a document that is not an alternative Media
Presentation, and never enters the §5.16 execution model. §5.8.1
nevertheless presents `altmpd` as "the value that names a slot's
resolution request" without qualification. Table I.4 anticipates this
case: it admits a URN or tag URI whose semantics are defined by its
owner, and requires clients to drop unknown ones.

**Suggested clarification**: keep `altmpd` for the linear slots and mint
`urn:svta:dash:request:sgai-resolution:2026` for the non-linear ones,
registering it in §2.1 alongside the other URIs this edition introduces.

### M6 — The MPD-level `EssentialProperty` and the legacy guarantee

§5.8.4.8 NOTE 1: *"If the scheme or the value for this descriptor is not
recognized, the DASH Client is expected to ignore the parent element
that contains the descriptor."* NOTE 2, for MPD-level descriptors: *"In
the case when none of the EssentialProperty elements sharing the same
@id can be successfully processed, the DASH Client is expected to
terminate the media presentation."* `urn:mpeg:dash:urlparam:2025` is new
in the 6th edition, so a Player predating it meets an unrecognised
MPD-level `EssentialProperty` in the main MPD of Annex A.2 and may stop
playing.

That is the one construct in the spec whose legacy behaviour is not
"skip and continue", and it is absent from the §4.7.3 per-construct
audit table — which §4.1 makes a document-level conformance obligation,
since that table is where the specification discharges its
backward-compatibility claim construct by construct. The §4.7.1 row on
descriptor schemes does not cover it: that row is about *vendor*
descriptor schemes as a carrier for SGAI payload, and this is an
MPEG-defined descriptor used for its own purpose. Annex I gives no
escape either — for the 2025 scheme the `EssentialProperty` form is
mandatory, and `SupplementalProperty` signalling belongs to the legacy
2016 / 2014 schemes.

**Suggested clarification**: add the row to §4.7.3 with its real legacy
outcome, reconcile §4.7.1, and state that a Publisher who needs the
§4.3.7 legacy-fallback guarantee authors no `RequestParam` template —
or accepts that the guarantee holds only for Players implementing the
6th edition.

### M7 — `Period@start` in the sub-MPDs

§8.15.3: *"Period@start attribute should not be present. If present, its
value shall be 0."* `start="PT0S"` satisfies the second sentence and
contradicts the first. SHOULD-level, and it affects both sub-MPD
listings in the document — A.5 and C.5, the only two.
**Fix**: drop the attribute from both.

### M8 — An `[inferred]` tag on a verifiable value

§5.1.1 tags the 60-second default of `@earliestResolutionTimeOffset` as
`[inferred]` and explains it as a value "carried in the clause's prose".
Table 63 of §5.16.5.2 states it normatively: *"The default is 60 seconds
in units of timescale."* The footnote's narrower claim — that the XML
Schema declares no default — is correct and worth keeping. **Fix**:
remove the `[inferred]` tag and cite Table 63; keep the schema-versus-
semantics note.

### M9 — The dated normative reference

§2 cites *ISO/IEC 23009-1:2025(E) … (MPEG-DASH 6th edition, FDIS
stage)*. The published document is ISO/IEC 23009-1:2026(en), Sixth
edition, dated 2026-07. Every clause number the spec cites resolves
correctly in the published text — the audit checked each one — so this
is a citation defect rather than a content defect, but §2 declares that
"for dated references, only the cited edition applies", which points at
a document that no longer exists. **Fix**: update the year, drop "FDIS
stage", and keep the canonical URL.

## Open questions surfaced

- **`ListOfProfilesType` is not reproduced in the body of the standard**
  — the complete schema lives in Annex B, which the PDF references
  rather than inlines. NC4 therefore rests on the §8.1 prose ("comma-
  separated list"), which is unambiguous, rather than on the simple
  type's own definition.
- **Media-Presentation-level conformance of the resolution documents.**
  §8.1 says a Media Presentation conforms to a profile only if "there is
  at least one Representation in each Period in the profile-specific
  MPD". Neither the Overlay Resolution Document nor the empty `ListMPD`
  satisfies that. Both are MPDs that are never presented as Media
  Presentations, and §8.14 states a List MPD is "not expected to be an
  entry point to a service", so the clause arguably does not bind them —
  but the specification does not say so, and a conformance tool applying
  §8.1 mechanically will flag both documents. Worth one sentence in
  §5.2.2.1.
- **`EventType` sequence order with descriptors.** If a Publisher ever
  authors a `SupplementalProperty` inside a slot `<Event>` alongside the
  SVTA child, the SVTA element must come **after** it. No listing does
  this today, so nothing is wrong; the ordering constraint is simply
  unstated in §5.1.3.2 ("Children: None").

## Summary

- Total constructs audited: 40
- Conforming: 26
- Marginal: 9
- Non-conforming: 5

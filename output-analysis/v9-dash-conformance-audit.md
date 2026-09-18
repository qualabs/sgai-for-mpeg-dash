[GROUNDED_BY=iso-23009-1-2026-pdf]

# DASH conformance audit — v9 (2026-09-18)

**Audit target**: `../output/v9-sgai-spec.md`.
**Reference**: the edition declared in `../context/00-normative-base.md` —
ISO/IEC 23009-1:2026 (Sixth edition, 2026-07). The copy consulted matched the
`sha256` recorded there.
**Method**: inventory + clause searches against the primary copy +
per-construct verdict.

## Scope

Conformance of every construct the specification introduces, modifies or
reuses against the rules of the base standard: the Annex B MPD schema as
reproduced in the clause-level XML-syntax subclauses, the extension rule of
§5.2.1, the event placement and clustering rules of §5.10, the profile
definitions of §8.1 and §8.3–§8.15, and the request-parametrisation rules of
Annex I. Design quality is out of scope — that is the validation sidecar's.

Annex examples are inside scope. They are the only place where the constructs
appear composed into whole documents, so they are where a schema-order or
profile-declaration defect becomes visible at all.

## Method summary

- Inventory built from Chapter 5 (Syntax) in full, §4.7 (Backward
  compatibility, per construct), §4.8, and every XML listing in Annexes A–O.
- The primary copy was extracted once with `pdftotext -layout`, the
  per-page licence header stripped before reading, and searched in two
  forms: line-oriented and paragraph-flattened, so a sentence broken across
  the extraction's line wraps still matches. Over fifty searches were run;
  every sentence quoted below was matched in the primary copy verbatim, and
  every reported absence was preceded by the same search against a string
  known to be present.
- Each construct assessed Conforming / Marginal / Non-conforming.

## Inventory + verdicts

| ID | Construct | Type | Placement | Verdict | Rationale |
|----|-----------|------|-----------|---------|-----------|
| C01 | `urn:svta:dash:sgai:2026` | Extension namespace | Elements and attributes throughout | Conforming | §5.2.1: *"the MPD shall be authored such that, after XML attributes or elements in the other namespaces than the DASH namespace are removed, the result is a valid XML document formatted according to that schema and that conforms to this document."* Every SGAI element sits in a container whose `xs:sequence` ends in `<xs:any namespace="##other" processContents="lax"/>`. |
| C02 | `<svta:OverlayPresentation>` | New element | Child of `<Event>` | Conforming | `EventType` (§5.10.2.3) ends its sequence with `<xs:any namespace="##other" processContents="lax" minOccurs="0" maxOccurs="unbounded"/>`, and §5.10.2.1 states the intent: *"The Event element may contain further XML elements meaningful for a particular event scheme. These may be defined in this document … or in some external namespace."* It is the only child, so the wildcard's terminal position is satisfied. |
| C03 | `<svta:PauseAdPresentation>` | New element | Child of `<Event>` | Conforming | As C02. |
| C04 | `urn:svta:dash:event:sgai-overlay:2026` | New scheme URI | `EventStream@schemeIdUri` | Conforming | `@schemeIdUri` is `xs:anyURI use="required"` with no enumeration, and §5.10.2.1 states *"This document does not provide any specific information on how to use Event Streams. It is up to the application that employs DASH formats to instantiate the description elements with appropriate scheme information."* |
| C05 | `urn:svta:dash:event:sgai-pause-trigger:2026` | New scheme URI | `EventStream@schemeIdUri` | Conforming | As C04. |
| C06 | One family, one `<EventStream>` (§5.1.6) | Authoring rule | `<Period>` | Conforming | §5.10.2.1: *"Events of the same type are clustered in Event Streams by the same scheme/value pair … all Events of one type shall be clustered in one Event Stream."* The specification restates the base rule and adds nothing. |
| C07 | Tie-break by position in the stream (§5.1.6) | Authoring rule | `<EventStream>` | Conforming | §5.10.2.1: active events are dispatched *"in the order they appear in the EventStream element."* The base standard does not order equal presentation times; the specification fills that gap in the direction the clause already points. |
| C08 | `<InsertPresentation>` reuse, `@maxDuration` made required | Modified reuse | `<Event>` | Conforming | Table 63 (§5.16.5.2) types `@maxDuration` `OD`, so requiring it narrows rather than relaxes. §5.16.3's *"The event shall not appear if the MPD type is \"dynamic\""* is respected: the element appears in Annexes A, F and G only, all `type="static"`. |
| C09 | `<ReplacePresentation>` reuse, `@clip` / `@startWithOffset` | Reuse | `<Event>` | **Marginal** | See M1. Two `shall` restrictions of Table 62 (§5.16.4) are not reproduced. |
| C10 | Linear `ListMPD` | Reuse | Resolution document for a linear slot | Conforming | §8.14 rules 1, 2, 3 and 5 are quoted accurately and the annex documents satisfy them: `type="list"`, `urn:mpeg:dash:profile:list:2024` in `@profiles`, no XLink, no Alternative MPD events. |
| C11 | `<ImportedMPD>` in a `ListMPD` `<Period>` | Reuse | First child of `<Period>` | Conforming | `PeriodType` declares `ImportedMPD` as the **first** particle of its sequence, and every annex `ListMPD` authors it first. §8.14 rule 4 admits Linked Periods. |
| C12 | Sub-MPD bound to `urn:mpeg:dash:profile:sps:2024` | Reuse | Target of every `<ImportedMPD>` | Conforming | §5.3.2.6.1: *"MPDs referenced in the ImportedMPD element shall be restricted to the constraints of a single period profile as defined in 8.15."* The annex sub-MPDs satisfy §8.15.2 on every checkable point: `type="static"`, no `@availabilityStartTime`, no `@mediaPresentationDuration`, exactly one `<Period>` carrying `@duration`, no MPD-level `Metrics` or `SupplementalProperty`. |
| C13 | Overlay Resolution Document envelope | New document shape | APS response | **Marginal** | See M2. MPD-level profile conformance holds; Media-Presentation-level conformance under §8.1 does not, and the specification does not distinguish the two. |
| C14 | `urn:svta:dash:profile:sgai-overlay-list:2026` | New URI | `MPD@profiles` | **Marginal** | See M3. §8.1 admits the declaration but classifies such a URI differently from how §2.1 and §4.7.10 describe it. |
| C15 | `<svta:OverlayList>` | New element | Only child of the resolution `<Period>` | Conforming | `PeriodType` ends in `<xs:any namespace="##other" processContents="lax"/>`, and being the only child places it last trivially. The zero-duration Period is admitted by Table 4 (§5.3.2.2): *"At least one Adaptation Set shall be present in each Period unless the value of the @duration attribute of the Period is set to zero."* |
| C16 | `<svta:Candidate>` | New element | Child of `<svta:OverlayList>` | Conforming | Inside an extension parent; no base schema reaches it. |
| C17 | `<svta:RenderableAsset>` | New element | Child of `<svta:Candidate>` | Conforming | As C16. |
| C18 | `<ImportedMPD>` nested inside `<svta:RenderableAsset>` | Reuse at a new position | Inside an extension element | Conforming | The DASH schema declares exactly one **global** element, `MPD`; `ImportedMPD` is declared locally inside `PeriodType`. Under `processContents="lax"` a processor validates only what it can find a declaration for, so a locally-declared name appearing outside its parent type is skipped rather than rejected. `ImportedMpdType` carries `<xs:anyAttribute namespace="##other"/>` and **no** `<xs:any>`, confirming §5.3.4's statement that the element admits foreign attributes and no foreign child elements — that claim no longer needs its `[inferred]` tag. |
| C19 | `<svta:BackgroundElement>`, and its order against `<ImportedMPD>` | New element | Child of `<svta:RenderableAsset>` | **Marginal** | See M4 (routed item). Both orders are conformant; nothing in the base standard decides between them, and the specification declares no content model that would. |
| C20 | `<svta:Click>` + `<svta:ClickTracking>` | New elements | Child of `<svta:Candidate>` | Conforming | Inside an extension parent. |
| C21 | `<svta:Click>` on a `ListMPD` `<Period>` | New element at a base position | Foreign-namespace child of `<Period>` | **Marginal** | See M5. Admissible only when authored after every DASH-namespace child of that `<Period>`, which the specification never says and no annex demonstrates. |
| C22 | `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>`, `<svta:UniversalAdId>` | New elements | Children of `<svta:Candidate>` | Conforming | Inside an extension parent; optional to emit and to read. |
| C23 | Callback `<EventStream>` inside a sub-MPD `<Period>` | Reuse | `<Period>` of the sub-MPD | Conforming | Table 47 (§5.10.4.5.3) fixes exactly the shape used: `EventStream@schemeIdUri` = `"urn:mpeg:dash:event:callback:2015"`, `EventStream@value` = `1`, the URL as the `Event` value. The `@value="1"` claim no longer needs its `[inferred]` tag. §8.15.3 places no restriction on `EventStream` inside the Period, and `PeriodType` orders `EventStream` before `AdaptationSet`, which every annex sub-MPD follows. |
| C24 | Callback `<EventStream>` inside `<svta:Candidate>` | Reuse at a non-schema position | Inside an extension element | **Marginal** | See M6. |
| C25 | `<Event>@id` required, URL as element value, `@messageData` unused | Modified reuse | Tracking `<Event>` | Conforming | `EventType` declares `@id` as `xs:unsignedLong` optional, so requiring it narrows. `@messageData` is `use="prohibited"` in the 6th-edition schema, annotated *"Deprecated in favor of carrying the message information in the value space of the event"* — the specification's §5.10.2.3 citation is exact and the `[inferred]` tag can be dropped. |
| C26 | Empty resolution documents, both families | New document shape | APS response | **Marginal** | Folded into M2: the same §8.1 Media-Presentation test is not met, and the empty `ListMPD` case is the sharper one because `urn:mpeg:dash:profile:list:2024` is a profile of the base standard rather than of this specification. |
| C27 | `<RequestParam>` carrying the Publisher query template | Reuse | `MPD`, `<EventStream>` | **Non-conforming** | See N1. Annexes A.2, B.2, F.2, G.2 and G.3 author it as `<up:RequestParam>` in `urn:mpeg:dash:urlparam:2025`. |
| C28 | `urn:svta:dash:request:sgai-resolution:2026` in `@includeInRequests` | New request-type URN | `<RequestParam>` | **Marginal** | See M7. Table I.4 admits it in general; §8.13.2.7 enumerates the values admitted under the profile Annex G declares, and the URN is not among them. |
| C29 | Reserved capability query parameters | Non-MPD construct | Resolution-request query string | Conforming | Nothing in the base standard governs a query string a client composes itself. §I.4.1's vocabulary is author-declared session state and holds no decoder-count or compositing axis, which §5.8.2 states and the primary copy confirms: Table I.5's suffixes are `audio`, `video`, `lang#…`, `encryption`, `cmcd#[key]`, `execution-delta#[id]`, `expected-duration#[id]`, `execution-count#[id]`, `previous-state`. |
| C30 | `<Metrics metrics="PlayList">` on the main MPD | Reuse | `MPD` | Conforming | §8.15.2 lists `MPD.Metrics` among the elements a Single-Period Static MPD *"shall not include"*, so placing the request on the main MPD is forced rather than chosen — the `[inferred]` tag on that claim can be dropped. Annex D.4.6's `PlayList` definition, `starttype` and `stopreason` are quoted accurately. |
| C31 | Main-MPD `MPD@profiles` across the annexes | Profile declaration | `MPD@profiles` | **Non-conforming** | See N2 (routed item). Three different URIs are declared with no stated rule; `isoff-live:2011` on a `static` document is explicitly fine, but `isoff-on-demand:2011` in Annexes K, L and M is declared over media the profile forbids. |
| C32 | `@allowedLayouts` as a whitespace-separated token list | New attribute | SGAI window elements | **Marginal** | The justification rests on `StringVectorType` being an XML Schema list type. That type is *used* throughout the primary copy but never *defined* in it — Annex B is by reference (see O1). The attribute itself is on an extension element and is therefore conformant regardless; only the stated reason is unverifiable here. |
| C33 | `@serviceDescriptionId` on the SGAI window elements | Reused attribute name | `<svta:OverlayPresentation>`, `<svta:PauseAdPresentation>` | **Marginal** | See M8. |
| C34 | Grounding of the `<Event>`-carrier claim in §5.1 | Citation | §5.1 | **Marginal** | See M9. The quoted sentence is not the one §5.10.1 carries. |

## Base-standard findings (highlights)

- **`RequestParam` lives in the DASH namespace, not in the Annex I namespace.**
  §I.3.1 says so in as many words: *"NOTE As opposed to other elements of type
  ExtendedUrlInfoType, RequestParam is defined in the main DASH schema, not in
  the XML schema defined in this Annex."* The schema reproduced under §5.3.1.2
  confirms it — `MPDtype` declares `<xs:element name="RequestParam"
  type="up:ExtendedUrlInfoType" …/>` as one of its own particles — and the
  standard's own Advanced-Linear example authors it unprefixed. This is what
  N1 turns on.
- **The On-Demand profile and segment templates are incompatible.** §8.3.3:
  *"Each Representation shall have one Segment that complies with the
  Self-Initializing Media Segment as defined in subclause 6.3.5.2."* §8.3.2
  adds that an `AdaptationSet` carrying `SegmentTemplate`, and a
  `Representation` with no `BaseURL`, *"may be ignored"*. This is what N2
  turns on.
- **The Live profile explicitly admits a static document**, which settles half
  of the first routed item: *"Although the profile is optimized for live
  services, the MPD@type attribute may be set to 'static' to distribute
  non-live content, for example in case a live Media Presentation is
  terminated but kept available as On-Demand service"* (§8.4.1).
- **§8.1 runs two conformance tests, not one.** An MPD conforms to a profile
  when the profile-specific MPD validates and satisfies the profile's
  restrictions; a *Media Presentation* conforms when additionally *"There is
  at least one Representation in each Period in the profile-specific MPD for
  ProfA."* Every zero-duration Period this specification defines passes the
  first and fails the second.
- **An externally defined `@profiles` URI is an Interoperability Point.**
  §8.1: *"External organizations or individuals may define restrictions,
  permissions and extensions by using this profile mechanism. It is
  recommended that such external definitions be not referred to as profiles,
  but as Interoperability Points. … The owner of the URI is responsible to
  provide sufficient semantics on the restrictions and permission of this
  interoperability point."* The second sentence is already cited in §5.2.2 and
  no longer needs its `[inferred]` tag; the first is not cited anywhere and
  contradicts §4.7.10's wording.
- **Table I.4 names a request type for sub-MPD fetches that the specification
  never mentions**: `mpdlink` — *"all requests for MPDs referenced from linked
  Periods"*. Every `<ImportedMPD>` resolution is one. §5.8.1 discusses only
  `altmpd` and the SGAI URN.

## Non-conforming items detail

### N1 — `RequestParam` is authored in the wrong namespace and at a position the MPD schema does not admit

**Locations**: `../output/v9-sgai-spec.md` §A.2, §B.2, §F.2, §G.2, §G.3 — each
binds `xmlns:up="urn:mpeg:dash:urlparam:2025"` and authors
`<up:RequestParam includeInRequests="…" queryTemplate="…"/>` as the first child
of `<MPD>`, before `<Period>`.

**Conflict**, on two independent axes:

1. **Namespace.** `RequestParam` is a particle of `MPDtype` in the main DASH
   schema, so its qualified name is
   `{urn:mpeg:dash:schema:mpd:2011}RequestParam`. §I.3.1's NOTE states this
   explicitly and the standard's own example in §G.30 authors it unprefixed
   under the default DASH namespace. Placed in
   `urn:mpeg:dash:urlparam:2025`, the element is not the one the mechanism
   defines, and the extended HTTP GET parametrisation is therefore not
   signalled at all.
2. **Sequence position.** Having a foreign namespace, the element can only
   match `MPDtype`'s trailing `<xs:any namespace="##other"
   processContents="lax"/>`, which is the **last** particle of the sequence —
   after `Period`, `Metrics`, `EssentialProperty`, `SupplementalProperty`,
   `UTCTiming`, `LeapSecondInformation` and `ContentSteering`. Authored before
   `<Period>`, it fails schema validation even as an extension element.

The second axis is what makes this more than a prefix slip: correcting only
the namespace fixes both, but correcting only the position fixes neither.

**Contrast within the document**: §5.8.1's own example gets it right —
unprefixed `<RequestParam>` inside `<EventStream>`, after the `<Event>`, which
is exactly where `EventStreamType` places the particle. The body and the
annexes disagree.

**Suggested fix**: in all five annex listings, drop the `up` prefix and the
`xmlns:up` binding, and author `<RequestParam …/>` in the default DASH
namespace at MPD level, before `<Period>` (where `MPDtype` declares it) or
inside the `<EventStream>` the template scopes to. Note that the `up` prefix
is still needed nowhere else: no other element of this specification comes
from that namespace.

### N2 — Annexes K, L and M declare the On-Demand profile over media that profile forbids

**Locations**: §K.2, §L.2, §M.2 — `profiles="urn:mpeg:dash:profile:isoff-on-demand:2011"`
on a main MPD whose primary Adaptation Set is

```xml
<AdaptationSet id="1" contentType="video" mimeType="video/mp4"
               codecs="avc1.4d401f" segmentAlignment="true"
               startWithSAP="1" par="16:9">
  <SegmentTemplate timescale="90000" duration="360000" startNumber="1"
                   initialization="$RepresentationID$/init.mp4"
                   media="$RepresentationID$/seg-$Number$.m4s"/>
  <Representation id="v-720" bandwidth="2500000" width="1280" height="720" sar="1:1"/>
</AdaptationSet>
```

**Conflict**. §8.3.3 states a `shall`: *"Each Representation shall have one
Segment that complies with the Self-Initializing Media Segment as defined in
subclause 6.3.5.2."* A separate Initialization Segment plus `$Number$`-indexed
Media Segments is the opposite arrangement. §8.3.2 adds three independent
grounds on which a conformance check discards this Adaptation Set: *"if either
the AdaptationSet.SegmentList or the AdaptationSet.SegmentTemplate element is
present in an AdaptationSet element then this AdaptationSet element may be
ignored"*; *"if the Representation element does not contain a BaseURL element
then this Representation element may be ignored"*; and *"AdaptationSet elements
with AdaptationSet@subsegmentAlignment not present or set to 'false' may be
ignored"* — the listing declares `@segmentAlignment`, which is the Live
profile's attribute, not `@subsegmentAlignment`.

Applying §8.1's profile-specific-MPD construction, step 5 removes everything
that *"may be ignored"*, leaving a Period with no Representation at all, which
then fails the Media-Presentation test of §8.1.

**Same defect class, one more location**: §5.8.1's example MPD declares the
same profile and carries a `<Representation>` with neither a `BaseURL` nor any
segment information. It is a skeleton rather than a full listing, but it
declares the same profile and meets it no better.

**Contrast**: the three annexes that declare `urn:mpeg:dash:profile:isoff-live:2011`
(§H.2, §I.2, §J.2) do satisfy it — `SegmentTemplate` present, `@segmentAlignment="true"`,
`@startWithSAP="1"` — including on the two documents whose `MPD@type` is
`static`, which §8.4.1 permits outright.

**Suggested fix**: one of two, and the choice is the specification's, not the
audit's.

- Change the declaration in §K.2, §L.2, §M.2 and the §5.8.1 example to
  `urn:mpeg:dash:profile:isoff-live:2011`, which the media as written already
  satisfies and which §8.4.1 allows on a `static` document. This is the
  smaller edit and touches no media.
- Or change the media to the On-Demand shape: drop `SegmentTemplate`, give
  each `<Representation>` a `<BaseURL>` and a `<SegmentBase indexRange="…"/>`,
  and replace `@segmentAlignment` with `@subsegmentAlignment` — the shape the
  sub-MPDs in §A.3 and §C.4 already use.

**And the rule that is missing is the reason this happened.** Nothing in
`context/` or in the specification says which profile a Publisher's main MPD
declares, or that the declaration constrains the media authored under it. The
three URIs in the annexes are a consequence of that silence, not the cause of
it. A one-line statement in §5.1 — the main MPD declares whatever profile its
own media satisfies, and this specification constrains none of them — would
make the annexes auditable against something.

## Marginal items detail

### M1 — `@clip` and `@startWithOffset` are reproduced without two inherited `shall` restrictions

§5.1.2 presents the three replacement-only attributes as independent. Table 62
(§5.16.4) attaches two restrictions the specification does not carry over:
`@clip` *"shall not be present if the @maxDuration attribute is absent"*, and
`@startWithOffset` *"does not apply to a live alternative presentation and
shall not be used if the @clip attribute value is \"false\""*.

The first is harmless here — §5.1.2 makes `@maxDuration` required — but the
second is not: §5.1.2's own prose describes `@clip="false"` and
`@startWithOffset="true"` as two independent choices, and a reader authoring
from §5.1.2 alone would produce the combination the base standard forbids.

**Suggested clarification**: state both restrictions in the §5.1.2 table rows,
quoted from Table 62. Reuse "verbatim" has to include the constraints, or the
word is doing less work than it looks like it is.

### M2 — Zero-duration Periods pass the MPD conformance test and fail the Media Presentation one

§5.2.2 says an Overlay Resolution Document is *"a document that is otherwise a
conformant MPD"*, and §4.7.3 rests the legacy argument on the same claim. Both
are true of §8.1's MPD-level test. §8.1 then defines a second test the
documents do not pass: *"A Media Presentation is conforming to profile ProfA
when it satisfies the following: 1) The MPD of the Media Presentation is
conforming to profile ProfA as specified above. 2) There is at least one
Representation in each Period in the profile-specific MPD for ProfA."*

This reaches three shapes: the Overlay Resolution Document (§5.2.2), the empty
non-linear document and the empty `ListMPD` (§5.2.3). The last is the sharpest,
because it declares `urn:mpeg:dash:profile:list:2024` — a profile of the base
standard, whose conformance a third-party validator already knows how to test.

**Suggested clarification**: say which of the two tests the specification
claims. The honest claim is the first, and it is enough for the purpose:
these documents are answers to a resolution request, not presentations to
play. Saying so also removes the temptation to add a Representation nobody
would render.

### M3 — The profile URI is described in terms §8.1 assigns differently

§2.1 names `urn:svta:dash:profile:sgai-overlay-list:2026` *"the profile
identifier of the non-linear resolution document"*, and §4.7.10 states that
*"The identifier carries no Interoperability Point"*. §8.1 says the opposite
about both: an external definition signalled in `@profiles` **is** an
Interoperability Point, it *"is recommended that such external definitions be
not referred to as profiles"*, and its owner carries a stated obligation.
§5.2.2 already cites the obligation half; the classification half is not cited
anywhere and is contradicted.

Nothing invalid follows — `@profiles` is a list of URIs and the token is
well-formed under RFC 8141 — but the document describes its own construct in
vocabulary the base standard reserves for something else.

**Suggested clarification**: keep the URI (renaming it would break every
document already authored) and correct §4.7.10 to say what is true: the
identifier **is** an Interoperability Point in the base standard's sense, this
specification is its owner, and the semantics §8.1 makes the owner responsible
for are the ones this document states. That is a stronger position than
disclaiming it.

### M4 — Routed item: `<svta:BackgroundElement>` and `<ImportedMPD>` child order

**Verdict: no DASH rule bites, in either order.**
`<svta:RenderableAsset>` is an element of an extension namespace matched by
`<xs:any namespace="##other" processContents="lax"/>`. Lax processing
validates only what a declaration can be found for, and this specification
publishes no XSD, so nothing constrains the order of its children. The
`<ImportedMPD>` nested inside it is a locally-declared name of the DASH
schema (C18), which lax processing also skips. Annexes I.3 and J.3
(`<ImportedMPD>` then `<svta:BackgroundElement>`) and Annex M.3
(`<svta:BackgroundElement>` then `<ImportedMPD>`) are therefore equally
conformant to the base standard.

What is missing is this specification's own content model. §5.3.1 lists the two
children in a table with cardinalities and no order, so the annexes are not
inconsistent with a rule — there is no rule to be inconsistent with, and a
validator written from §5.3.1 has nothing to check.

**Suggested clarification**: state the order in §5.3.1, or state that order is
not significant. Either closes it; leaving it open means every implementer
picks, and the annexes already show two picks.

### M5 — `<svta:Click>` on a `ListMPD` `<Period>` is admissible only in one position

§5.6.1 places `<svta:Click>` as *"foreign-namespace open content on the
`ListMPD` `<Period>`"*. `PeriodType`'s sequence begins with `ImportedMPD` and
ends with `<xs:any namespace="##other" processContents="lax"/>`, so the
element is schema-valid only when authored **after** `<ImportedMPD>` and after
every other DASH-namespace child present. Authored first — the position a
reader might choose, since the click belongs to the ad the `<ImportedMPD>`
names — the document does not validate.

No annex shows the composition, so nothing in the specification demonstrates
the correct shape. This is the same class of defect as M4 and the opposite
resolution: here the base schema **does** decide, and the specification is
silent about a decision that has already been made for it.

**Suggested clarification**: add the ordering sentence to §5.6.1 and a
three-line listing showing a `ListMPD` `<Period>` carrying `<ImportedMPD>`
followed by `<svta:Click>`.

### M6 — The candidate-level tracking `<EventStream>` sits outside every rule that governs it

§5.5.2 places a callback `<EventStream>` directly inside `<svta:Candidate>`,
and the specification already states the two consequences it saw: no schema
validation at that position, and tooling that scans `<Period>` children misses
it. A third follows from §5.10.2.1 and is not stated. The clustering rule —
*"all Events of one type shall be clustered in one Event Stream"* — is scoped
to Event Streams the base schema knows about. A resolution document carrying
four candidates carries four streams of the identical scheme/value pair
(`urn:mpeg:dash:event:callback:2015` / `1`), which inside a `<Period>` would be
a violation and here is not, because after the §5.2.1 removal none of them
exists.

The verdict is conformant. It is Marginal because the conformance rests on the
streams being invisible to the base standard, which is also what removes every
guarantee the carrier normally comes with — and §5.5.4's per-candidate
de-duplication scope is doing the work the clustering rule would otherwise do.

**Suggested clarification**: say in §5.5.2 that the clustering rule of
§5.10.2.1 does not reach this position, and that §5.5.4 is what replaces it.

### M7 — The request-type URN against the Advanced Linear profile's enumeration

§G.2 and §G.3 declare `profiles="urn:mpeg:dash:profile:advanced-linear:2025"`
and author `includeInRequests="altmpd urn:svta:dash:request:sgai-resolution:2026"`.

Table I.4 admits the token in general — its last row is *"a URN or tag URI,
where the request type semantics is understood by the client and specified by
the URN / tag URI owner"*, with the drop rule §4.7.11 relies on. §8.13.2.7,
the Advanced Linear profile's own constraints on request parametrisation,
then says: *"The following values may appear in the @includeInRequests
attribute: — mpd and mpdpatch — segment and init — steering — callback,
altmpd and mpdlink."* The SGAI URN is not among them.

Whether that enumeration is exhaustive is genuinely undecidable from the text.
It is phrased permissively (*"may appear"*), which reads as non-exclusive; it
sits in a profile's constraints subclause, where an enumeration of what may
appear conventionally closes the set. The specification cites Table I.4 and
never mentions §8.13.2.7.

**Suggested clarification**: decide it explicitly rather than by omission.
Either cite §8.13.2.7 in §5.8.1 and state that Table I.4's URN row governs
because a profile's list of admitted values cannot narrow a value space the
mechanism defines generically; or change the Annex G declaration to a profile
that carries no such enumeration. The first is the better answer and costs one
paragraph — but it is a reading, and a reading that is written down can be
corrected by the working group, while one that is implicit cannot.

### M8 — `@serviceDescriptionId` reused on an element the base semantics do not reach

§5.1.3 and §5.1.4 carry `@serviceDescriptionId` onto the two SGAI window
elements with the base definition: *"specifies the value of the @id attribute
of a ServiceDescription element applicable to this Event and to any
presentation initiated as a result of executing this Event"* (Table 63).
In the base standard the presentation initiated by such an event is an
alternative Media Presentation, which §5.16.1 defines as one that *"replaces
the main Media Presentation"*. An overlay does not replace it, and a pause ad
is not on the timeline at all.

Nothing is violated — the attribute is on an extension element and this
specification defines what it means there — but the row quotes a definition
whose own scope does not cover the case.

**Suggested clarification**: state in §5.1.3 and §5.1.4 what a
`ServiceDescription` governs for a composited or a pause presentation, rather
than importing a sentence written about a substitutive one.

### M9 — A citation points at a clause that says something different

§5.1 quotes, attributed to DASH §5.10.1: *"Events are timed, i.e. each event
starts at a specific media presentation time and typically has a duration."*

§5.10.1 reads: *"Events are timed, i.e. each event starts at a specific media
presentation time and **may** have a duration."* The sentence with *"typically
has a duration"* is in §4.3 (DASH data model overview).

The point the specification is making survives either wording. The citation
does not, and this is the third occurrence in this project of a clause number
attached to a sentence from elsewhere.

**Suggested clarification**: quote §5.10.1's own sentence and keep the §5.10.1
citation, which is the clause the surrounding argument actually needs.

## Open questions surfaced

### O1 — `StringVectorType` cannot be verified against the primary copy — `[fetch-failed]`

§5.1.3's encoding note justifies the whitespace-separated `@allowedLayouts`
by *"matching the encoding the base specification uses for the attributes it
types as `StringVectorType`, an XML Schema list type and therefore
whitespace-delimited."*

**Searched for**: `StringVectorType` (7 hits, all
`<xs:attribute … type="StringVectorType"/>` uses on `@dependencyId`,
`@associationId`, `@mediaStreamStructureId`, `@contentComponent`,
`@preselectionComponents`, `@serviceLocations`); `name="StringVectorType"`
(0 hits); `xs:list` (0 hits anywhere in the document);
`ListOfProfilesType` (2 hits, both uses, no definition).

**Why the zero is real and not an instrument failure**: the same search finds
simple-type definitions that *are* printed — `name="EventStatusType"`,
`name="RatioType"`, `name="FrameRateType"`, `name="PreselectionOrderType"` all
resolve. The definitions of `StringVectorType` and `ListOfProfilesType` are
absent because Annex B is by reference: *"The schema of the MPD for this
document is provided at: https://standards.iso.org/iso-iec/23009/-1/ed-6/en
(DASH-MPD.xsd)."* The clause-level XML-syntax subclauses reproduce the complex
types and not the shared simple types.

The construct is conformant regardless — `@allowedLayouts` is an attribute of
an extension element, and no base type governs it. What cannot be verified
from the primary copy is the **reason given**. Either fetch DASH-MPD.xsd and
cite it as a second normative source alongside the PDF, or tag the sentence
`[inferred]`. Leaving it as an unqualified assertion is the one option that
misrepresents what was checked.

### O2 — `mpdlink` is never named, and sub-MPD requests are exactly what it covers

Not a conformance defect, but a reuse gap the audit surfaces because it sits
in the clause §5.8.1 already covers. Table I.4 defines `mpdlink` as *"all
requests for MPDs referenced from linked Periods"*. Every `<ImportedMPD>`
resolution this specification performs — from a `ListMPD` Period and from a
video presentation option alike — is one, and §8.13.2.7 lists `mpdlink` among
the values the Advanced Linear profile admits. A Publisher wanting to
parameterise sub-MPD requests has the mechanism and no mention of it here.

## Summary

- Total constructs audited: 34
- Conforming: 21
- Marginal: 11
- Non-conforming: 2

**The two Non-conforming items are both in the annexes and neither touches a
construct.** N1 is a namespace and a sequence position on a reused base
element; N2 is a profile declaration that does not match the media declared
under it. Every construct this specification introduces — the two window
elements, the two event scheme URIs, the candidate list and its subtree, the
click carrier, the metadata elements, the profile URI and the request-type
URN — is conformant to the base standard as written.

**What the Marginal items have in common is worth naming**, because it is one
thing and not eleven: the specification is precise about what it introduces
and loose about what it inherits. M1, M8 and M9 are inherited definitions
reproduced incompletely or inexactly; M3 and M2 are inherited classifications
described in the specification's own vocabulary rather than the base
standard's; M5 and M7 are inherited constraints the specification does not
mention. M4 and M6 are the mirror image — positions where nothing is
inherited and the specification has not yet said what governs instead.

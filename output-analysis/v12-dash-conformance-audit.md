[GROUNDED_BY=iso-23009-1-2026-pdf]

# DASH conformance audit — v12 (2026-09-26)

**Audit target**: `../output/v12-sgai-spec.md`.
**Reference**: the edition declared in
`../context/00-normative-base.md` (ISO/IEC 23009-1:2026, sixth edition).
**Method**: inventory + clause searches against the primary copy +
per-construct verdict.

The key words MUST, SHOULD and MAY in suggested fixes are used as in
IETF RFC 2119.

## Scope

Every construct v12 introduces or modifies in a DASH document, plus the
inherited base constructs whose semantics v12 restates or constrains:
the two window schemes and their child elements and attributes, the
List MPD additions, the empty linear resolution, the sub-MPDs, the
tracking carriers, the standalone `<svta:OverlayList>` document and its
schema, the request-parameter rules, the profile declarations, the
pause-delivery `Metrics` request, and the Player rules that restate the
base Alternative-MPD processing model. Design quality is out of scope.

## Method summary

- Inventory built from §1.4, §2.1, §4.2, §4.5.2–§4.5.8, §4.7, §4.8,
  chapter 5 (including the §5.10.1 schema) and §8.13, and from all 83
  `xml` blocks of the spec (Annexes A–R included).
- Primary copy: the PDF whose SHA-256 matches `primary_copy.sha256` of
  `00-normative-base.md` (`a7274eb2…be100`, verified before extraction).
  Extracted once with `pdftotext -layout`; the licence header/footer
  lines were stripped before any search; whitespace flattened so
  phrases spanning line breaks match.
- About 45 verbatim phrase searches against the flattened text, plus
  direct reads of the governing clauses and schema fragments
  (`MPDtype`, `PeriodType`, `EventStreamType`, `EventType`,
  `AlternativeMPDEventType`, `ImportedMpdType`, `MetricsType`,
  `ServiceDescriptionType`, `PlaybackRestrictionsType`; §5.2.1,
  §5.3.1.4, §5.3.2.2, §5.3.2.6, §5.10.1–§5.10.2.4, §5.10.4.5,
  §5.16.1–§5.16.6, §8.1, §8.4.2, §8.12.4, §8.13, §8.14, §8.15, Annexes
  D.4.6, H, I.3, K.3.8/K.4, L.2). Every search that returned a hit is a
  positive control for the method; the zero-hit searches are listed in
  *Open questions*.
- A structural checker was run over all 83 XML blocks: well-formedness;
  child order of `MPD`, `Period`, `EventStream` and `<svta:Tracking>`
  against the sixth-edition sequences; foreign attributes on
  `EventStream`; non-decreasing `@presentationTime`; duplicate
  `Event@id`; Insertion events in dynamic MPDs; `@status` on Insertion
  events; `@clip` without `@maxDuration`; SPS constraints of §8.15.2/3
  on every sub-MPD; List MPD Periods without `ImportedMPD`; the
  chapter-5 co-occurrence rules on `<svta:RenderableAsset>` and
  `<svta:OverlayList>`; child order inside `<svta:Ad>`. Before it was
  trusted, it was run against a synthetic MPD carrying eight seeded
  violations and reported all eight. On the spec it reported only the
  expected items: the empty List MPD of §5.2.3 (a Period without
  `ImportedMPD`, by design) and the Events left empty in Annex G.3
  after the extension namespace is removed (valid: `EventType` is
  `mixed` and its children are optional).
- Each construct assessed Conforming / Marginal / Non-conforming.

## Inventory + verdicts

| ID | Construct | Type | Placement | Verdict | Rationale |
|----|-----------|------|-----------|---------|-----------|
| K-01 | Namespace `urn:svta:dash:sgai:2026` | Extension namespace | Elements and attributes in MPDs, List MPDs, standalone document | Conforming | §5.2.1: *"the MPD shall be authored such that, after XML attributes or elements in the other namespaces than the DASH namespace are removed, the result is a valid XML document formatted according to that schema and that conforms to this document."* Every MPD example stays valid after removal (Annex G.3 shows it). |
| K-02 | Scheme `urn:svta:dash:sgai-overlay:2026` | Event scheme | `Period/EventStream@schemeIdUri` | Conforming | Application scheme. §5.10.1: a client can *"subscribe to an Event Stream of interest and ignore Event Streams that are of no relevance or interest."* See K-35 for the URN form. |
| K-03 | Scheme `urn:svta:dash:sgai-pause-trigger:2026` | Event scheme | `Period/EventStream@schemeIdUri` | Conforming | As K-02. A span-shaped trigger is scheme semantics: *"The semantics of the element are specific to the scheme employed"* (§5.10.2.1). |
| K-04 | Usage of `EventStream`/`Event` for windows (§5.1.3) | Base element usage | `Period` | Conforming | One stream per family and no `@value` (PUB-7/8) fits *"A Period shall contain at most one EventStream element with the same value of the @schemeIdUri attribute and the value of the @value attribute"* (§5.10.2.1). Making `Event@id` mandatory and unique matches *"Each EventStream element shall not contain two Event elements with the same value of Event@id"* (Table 44). Making `Event@duration` mandatory is allowed because *"The interpretation of the value of this attribute is defined by the scheme owner"* (Table 44). The `@status` default `repeat` matches the schema (`default="repeat"`). A span ending at the end of its Period matches *"Events shall terminate at the end of a Period"* (§5.10.2.1). `EventStreamType` has no `xs:anyAttribute`, and no example puts a foreign attribute on it (checker). |
| K-05 | `<svta:OverlayPresentation>` | Foreign element | Child of `Event` | Conforming | `EventType` ends in `<xs:any namespace="##other" processContents="lax" …/>`. Table 44: *"The Event element may contain further XML elements meaningful for a particular event scheme. These may be defined in this document … or in some external namespace."* |
| K-06 | `<svta:PauseAdPresentation>` | Foreign element | Child of `Event` | Conforming | As K-05. |
| K-07 | `@durationCap` | Attribute (own name) | On K-05/K-06 | Conforming | New name, so the base `@maxDuration` default (*"If absent, the value is assumed to be infinity"*, Table 63) is not inherited. The units (`EventStream@timescale`) match the base. |
| K-08 | `@earliestResolutionTimeOffset` on windows | Attribute (reused name) | On K-05/K-06 | Conforming | Name, units and default match Table 63: *"specifies the time interval (in units of EventStream@timescale) prior to the Event@presentationTime during which the MPD described in the @uri attribute may be requested. The default is 60 seconds in units of timescale."* |
| K-09 | `@executeOnce` on the pause window | Attribute (reused name) | On K-06 | Conforming | It reuses the E.c rule: *"When the alternative media presentation triggered by an event successfully starts playing, the corresponding counter E.c is incremented"* (§5.16.2.2.6). The base wording is *"executed only once during the media presentation"* (Table 63); the spec says "for the whole session". The two are equivalent for one presentation. |
| K-10 | `@allowedLayouts`, `@customRegion` | Attributes (own) | On K-05 (K-06 for `@allowedLayouts`) | Conforming | Extension-namespace element, own list types. The base describes its list attributes as *"whitespace-separated list"* (e.g. `@dependencyId`). |
| K-11 | `@linearRelation` (`supersede`, `on-top`) | Attribute (own) | On K-05/K-06 | Conforming | The attribute itself sits on a foreign element. `supersede` (PLY-48) departs from *"a set of normative conditions which hold for any sequence of Alternative MPD events … the MPD author may assume that the steps described in this subclause are taken"* (§5.16.2.2.1). The departure is declared in §4.8.3 and is opted into by the same author the base addresses. A legacy Player executes the base event unchanged. |
| K-12 | Dispatch mode of the two window schemes | Scheme definition | §5.1.3/§5.1.4 | **Marginal** | See detail. |
| K-13 | Inherited `InsertPresentation` (§5.1.1) | Base event | `Event` of `…:insert:2025` | Conforming | The attribute types in §5.1.1 match `AlternativeMPDEventType`. *"The event shall not appear if the MPD type is "dynamic""* (§5.16.3): no Insertion event appears in a dynamic MPD (checker). Table 59: `Event@status` *"shall not be used"*; `Event@id` *"Required"*. Both hold in every example. |
| K-14 | Inherited `ReplacePresentation` (§5.1.2) | Base event | `Event` of `…:replace:2025` | Conforming | `@returnOffset`, `@clip` and `@startWithOffset` are as in `AlternativeMPDReplaceEventType`. *"This attribute shall not be present if the @maxDuration attribute is absent"* (Table 62) holds in every example: Annex N omits both, and says why. |
| K-15 | List MPD shape (§5.2.1, Annexes A/B/D/F/G/K) | Base document | `MPD@type="list"` | Conforming | §8.14 rules 1–5 hold (`type="list"`, the URN in `@profiles`, no XLink, Linked Periods, no Alternative MPD events). `ImportedMPD` comes first in the `PeriodType` sequence and the examples respect that. `ServiceDescription` inside the candidate Period survives the merge: *"iv) ServiceDescription"* (§5.3.2.6.3, step 3 b). The duration reconciliation quotes step 3 d iii exactly. |
| K-16 | `<svta:ClickThrough>`, `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>` in a List MPD | Foreign elements | Children of a candidate `Period`, after `ServiceDescription` | Conforming | `PeriodType` ends in `xs:any ##other`. The merge keeps them: *"ix) any elements from a different namespace"* (§5.3.2.6.3, step 3 b). |
| K-17 | Empty linear resolution (§5.2.3) | Base document shape | List MPD, one `Period duration="PT0S"`, no children | **Marginal** | See detail. |
| K-18 | SPS sub-MPD (§5.4) | Base document | Target of `ImportedMPD` / `@src` | Conforming | *"MPDs referenced in the ImportedMPD element shall be restricted to the constraints of a single period profile as defined in 8.15"* (§5.3.2.6.1). All sub-MPD examples satisfy §8.15.2/§8.15.3 (checker: static, one Period with `@duration`, no `@mediaPresentationDuration`/`@availabilityStartTime`, none of the excluded MPD-level elements, `…/mp4` mimeTypes). |
| K-19 | Sub-MPD `@profiles` = SPS **and** `isoff-live:2011` (Annex examples) | Profile declaration | Sub-MPD root | **Marginal** | See detail. |
| K-20 | Callback tracking in the sub-MPD (§5.5.1) | Base scheme reuse | `Period/EventStream` of the sub-MPD | Conforming | Table 47: `EventStream@value` `1`, the HTTP URL in the Event value. Placement is justified by *"In case equivalent above elements are present in both Linked Period and Imported Period, the elements from the Imported Period replace (i.e. override) the elements from the Linked Period"* (step 3 c, iv). Numbering beacons uniquely across the List MPD fits *"The scope of the @id for each Event is within the same @schemeIdURI and @value pair over the duration of the current media presentation"* (Table 44). |
| K-21 | `<svta:Tracking>` of type `dash:EventStreamType` (§5.5.2) | Foreign element reusing a base type | Child of `<svta:Ad>` | **Marginal** | See detail. |
| K-22 | `<svta:OverlayList>` standalone document (§5.2.2) | New document type | HTTP response to a window `@uri` | Conforming | It is not an MPD, and no document a legacy Player reads refers to it. Choosing not to be an MPD avoids `MPDtype`'s *`profiles … use="required"`* and the §8.14 List-profile binding (*"intended for use in conjunction with the Alternative MPD event"*). Whether a standalone document counts as an extension point is a project reading (§8.13 item 11), not a base rule. |
| K-23 | `<svta:Ad>`, `<svta:RenderableAsset>` (non-AV carrier) | Foreign elements | In K-22 | Conforming | No image or HTML asset reaches an `AdaptationSet`/`Representation`. That respects §7.3.1 *"The @mimeType attribute of each Representation shall be provided according to IETF RFC 4337"* and §8.12.4.3 *"The @mimeType shall be set to "<contentType>/mp4""*. |
| K-24 | Video option referencing an SPS MPD by `@src` | Reference to a base document | `<svta:RenderableAsset>` | Conforming | The referenced document is an ordinary §8.15 MPD. `ImportedMPD` is not used outside a Period. |
| K-25 | `@family`, `@dismissAfter`, `@validFor`, `@onExhausted` | Attributes (own) | On K-22 | Conforming | Extension-namespace document. `@dismissAfter` does not reuse `@skipAfter`, whose default is *"Default value is PT0S"* (Table 63). |
| K-26 | Reserved query parameters `sgai-*` (§5.8) | Request parameters | Query of a window `@uri` | Conforming | Not an MPD construct. The Annex I.3 mechanism is not used for windows. The URN request-type option (*"a URN or tag URI, where the request type semantics is understood by the client"*, Table I.4) was weighed and rejected in §4.8.4, and the base text supports that reasoning. |
| K-27 | `RequestParam` on inherited linear events (PUB-18) | Base mechanism usage | `EventStream`/MPD of the main MPD | **Marginal** | See detail. |
| K-28 | Main MPDs under `isoff-live:2011` (§4.8.5) | Profile declaration | Main MPD root | Conforming | §8.4.2: *"The elements and attributes listed in subclause 5.2.3.2 may be ignored."* The §5.2.3.2 list contains `Period.EventStream`. The spec states the consequence in §4.8.5, and no rule is broken. |
| K-29 | SGAI event streams in an Advanced Linear MPD | Profile interaction | Main MPD | **Marginal** | See detail. Already recorded in §8.13 item 1. |
| K-30 | `Metrics metrics="PlayList"` + `Reporting` (§5.9, PUB-13) | Base element usage | MPD level, after `Period` | Conforming | In `MPDtype`, `Metrics` follows `Period`, and the examples respect that order (checker). `MetricsType` requires ≥1 `Reporting`. *"No reporting scheme is specified in this document"* (§5.9.4). `starttype` `Resume` (*"Resume - Resume from pause"*) and `stopreason` `UserRequest`/`Rebuffering` exist in Table D.5. `Metrics` is kept out of sub-MPDs (§8.15.2 g). |
| K-31 | Schema of §5.10.1 | XML Schema | Extension namespace | Conforming | It imports `DASH-MPD.xsd`. The simple types are valid XSD 1.0 (a list restricted by `xs:length`, a union with an enumerated token, an enumeration restricted to a subset). The wildcards are `##other` with no Unique Particle Attribution conflict against the declared `svta` particles. Because the base schema is `elementFormDefault="qualified"`, the `Event` children of `<svta:Tracking>` are DASH-namespace, and every example declares the DASH default namespace wherever such children appear (checker: no unqualified `Event`). |
| K-32 | `PercentRectType` / SRD notation | Notation reuse | `@customRegion`, `@rect` | Conforming | Only the notation is reused, not the descriptor: *"the x-axis is oriented from left to right and the y-axis from top to bottom"* (H.2.2); *"the sum of object_x and object_width is smaller or equal to total_width"* (H.2.3). SRD placement (*"SRD information shall be contained exclusively in these two MPD elements (AdaptationSet and SubRepresentation)"*, H.1) is not touched. |
| K-33 | Fallback, failed execution, E.c (PLY-38, -39, -40, -44) | Player restatement of the base model | §4.5.6 | Conforming | These quote §5.16.2.2.5 step 2 d and §5.16.2.2.6 NOTE 3 verbatim. The base queue is *"ordered by the presentation time PRT"* (§5.16.2.2.2) and says nothing about ties, so a document-order tie-break is an addition, not a conflict. |
| K-34 | Drop-before-play of a List MPD Period (PLY-35) | Player rule on an inherited event | §4.5.5 | **Marginal** | See detail. |
| K-35 | URN form `urn:svta:…` of the three URIs of §2.1 | URI syntax | Scheme and namespace identifiers | **Marginal** | See detail. Already recorded in §8.13 item 13. |
| K-36 | PLY-41 applied to a linear resolution document | Player rule on an inherited event | §4.5.6 | **Non-conforming** | See detail. |

## Base-standard findings (highlights)

- Extension points: `MPD`, `Period`, `Event`, `EventStream` and
  `AlternativeMPDEventType` admit `xs:any ##other`. `MPD`, `Period`,
  `Event` and `AlternativeMPDEventType` admit `xs:anyAttribute ##other`;
  `EventStreamType` does not. `ImportedMpdType` is simple content with
  `anyAttribute` only. DR-2 in §4.7.1 matches the schema text exactly.
- List profile: an extension of the CMAF profile with five overriding
  rules. SPS: the §8.15.2 exclusion list (`Metrics` and
  `SupplementalProperty` among them) and `Period.ImportedMPD shall not
  be present`. Merge step 3 b keeps foreign elements, `ServiceDescription`
  and `EventStream`; step 3 c lets the imported `EventStream` override the
  Linked Period's. Every one of these is quoted correctly in v12.
- Events: `@id` is scoped *"within the same @schemeIdURI and @value
  pair over the duration of the current media presentation"*, and must
  be unique inside one `EventStream` (Table 44). Each base DASH scheme
  declares its dispatch mode (*"The dispatch mode of this event scheme
  is "on-receive""*, §5.16.3/§5.16.4). Application schemes get the
  dispatch-mode model only in informative Annex A.13.7.
- Alternative MPD execution: *"Execution fails if … The playback of the
  alternative presentation cannot start"* (§5.16.2.2.6). On a failure the
  next queued event is tried (§5.16.2.2.5 step 2 d). For insertion,
  *"APDA = min(APD, APDmax)"* (Table 57).
- Every clause number cited in v12 that was checked exists and is about
  the subject v12 cites it for (§4.2, §5.2.1, §5.3.1.4, §5.3.2.2,
  §5.3.2.6.x, §5.8.4.8/9, §5.9.1, §5.9.4, §5.10.1–§5.10.2.4, §5.10.4.5,
  §5.16.x, §7.3.1, §8.1, §8.4.2, §8.12.4.3, §8.13.x, §8.14, §8.15, D.4.6,
  H.1, H.2.2, H.2.3, I.3.1, K.3.8, K.6.4, L.2).

## Non-conforming items detail

### K-36 — PLY-41 turns a base failed execution into a non-failure on the linear family

**Rule.** §5.16.2.2.6: *"Execution fails if at least one of the
conditions below is true at PRTA: … The playback of the alternative
presentation cannot start. The reasons for this include (but are not
limited to) the following … Media playback is impossible due to missing
media or initialization segments."* §5.16.2.2.5 step 2 d: *"If execution
fails, steps a-c above are repeated for next events in QE"*. The base
presents both as *"normative conditions which hold for any sequence of
Alternative MPD events"* on which *"the MPD author may assume"*
(§5.16.2.2.1).

**Conflict.** PLY-41 says *"A resolution document carrying candidates
is **not** a failed execution, whatever the Player then does with them.
A candidate skipped because the device can satisfy none of its options
ends at the primary content (PLY-20), not at the next window."* The rule
is not limited to the non-linear families. For a List MPD whose
candidates the device cannot play, the base says playback cannot start:
the execution fails and the next queued Alternative MPD event is tried.
A Player conformant to v12 stops at the primary content instead. That is
a Player of this specification not executing a base event the base would
execute, which is the kind of departure §4.8.3 requires to be declared.
It is not declared there. §8.13 item 12 says so itself: *"This edition
states both as its own rules and has not recorded either as a
departure."* It also conflicts with the spec's own §1.4 rule 1 and
PUB-15.

**Suggested fix.** Scope PLY-41 to `<svta:OverlayList>` documents. For a
List MPD, state that a Player unable to start any candidate treats the
execution as failed under §5.16.2.2.6 and continues down the chain
(PLY-38), as the base does. If the project wants the current behaviour
on the linear family anyway, list it in §4.8.3 with its scope and
reason, as PLY-48 is listed.

## Marginal items detail

### K-12 — No dispatch mode declared for the window schemes

**Ambiguity.** Each base DASH scheme states its dispatch mode, and the
meaning of `Event@duration` depends on that mode: *"In the case of
on-start, duration defines the duration starting from ST in which DASH
Client is expected to dispatch the Event exactly once … In the case of
on-receive, duration is a property of event instance and is defined by
the scheme_id owner"* (A.13.7, NOTE; informative). v12 defines early
resolution (`@earliestResolutionTimeOffset`), which works only if the
window reaches the application before its start. That means on-receive,
but v12 never says so. A search of the spec for "dispatch" returns one
hit, in the `<svta:ClickThrough>` rationale of §4.8.2. As a positive
control, the same search for `earliestResolutionTimeOffset` returns 39.

**Suggested clarification.** State in §5.1.3/§5.1.4 that both schemes
are dispatched on-receive, as the base Alternative MPD schemes are, and
that `Event@duration` is the window span defined by this specification.

### K-17 — Empty linear resolution vs the List profile's CMAF base and the failure condition it cites

**Ambiguity.** The document is schema-valid, and Table 4 admits it:
*"At least one Adaptation Set shall be present in each Period unless the
value of the @duration attribute of the Period is set to zero."* Two
points remain open, though.

1. The List profile *"is an extension of the ISO-BMFF CMAF Profile"*
   (§8.14). The CMAF Period constraints say *"If the Subset element is
   not present, the Period contains exactly one CMAF Presentation"*
   (§8.12.4.4), and a Media Presentation conforms to a profile only if
   *"There is at least one Representation in each Period in the
   profile-specific MPD"* (§8.1).
2. v12 maps this document to *"Alternative MPD is a List MPD, and merge
   process resulted in no available media"* (§5.16.2.2.6). But the
   document has no `ImportedMPD`, so no merge takes place.

The outcome still holds either way: the playback of the alternative
presentation cannot start, so the execution fails and E.c is not
incremented. §8.13 item 10 records point 1 but not point 2.

**Suggested clarification.** In §5.2.3 and PLY-39, cite the broader
condition (*"The playback of the alternative presentation cannot
start"*) as the governing one, with the merge sentence only as the
closest analogue. Keep §8.13 item 10.

### K-19 — Sub-MPDs declaring `isoff-live:2011` make the callback stream ignorable

**Ambiguity.** The annex sub-MPDs declare
`profiles="urn:mpeg:dash:profile:sps:2024,urn:mpeg:dash:profile:isoff-live:2011"`.
Under the live profile, *"The elements and attributes listed in
subclause 5.2.3.2 may be ignored"* (§8.4.2), and that list contains
`Period.EventStream`. That element is the carrier of every List MPD
beacon (§5.5.1). The merge copies the profile into the List MPD
(*"The information in the @profiles parameters is merged into the
MPD@profiles attribute"*, step 3 a i). §4.8.5 analyses this effect for
main MPDs only.

**Suggested clarification.** Either drop `isoff-live:2011` from the
sub-MPD examples (SPS already applies the §7.3 rules), or extend §4.8.5
to sub-MPDs and state that a client processing them under the live
profile may ignore the tracking stream.

### K-21 — `<svta:Tracking>` reuses `EventStreamType` whole but re-anchors three of its semantics

**Ambiguity.** v12 says the element *"takes the attributes and children
of an `EventStream` (DASH §5.10.2.3)"* and that the reuse is "whole".
Three base semantics of that type are then redefined without being
listed as redefinitions:

1. **Timebase.** Base `@presentationTime` is *"relative to the start of
   the Period"* (Table 44). In v12 it is relative to the moment the
   candidate begins rendering (§5.5.2).
2. **`@id` scope.** Base: *"within the same @schemeIdURI and @value pair
   over the duration of the current media presentation"* (Table 44). v12:
   *"The same `@id` in two candidates of one document names two beacons"*
   (PLY-81). Annex E.4 uses `id="1"` in two candidates, and §5.2.5 re-fires
   the same beacons on every reuse of a document. A Player that routes
   these through its DASH event pipeline would treat the repeats as
   already processed.
3. **Duplicate `@id` in one stream.** §5.5.2 says *"Within one
   `<svta:Ad>`, beacons sharing an `@id` … fire once"*, which presupposes
   duplicates. The base forbids them in any `EventStream`: *"Each
   EventStream element shall not contain two Event elements with the same
   value of Event@id"* (Table 44).

Table 47 also scopes the callback parameters to *"a Callback event
signalled in the MPD"*, and `<svta:OverlayList>` is not an MPD. The
schema reuse is valid (K-31). The semantic reuse is only partial.

**Suggested clarification.** In §5.5.2, list the three redefinitions
explicitly as this specification's semantics for the non-MPD carrier:
the candidate-relative timebase, `@id` scoped to one `<svta:Ad>` and one
presentation of it, and `@id` unique within one `<svta:Tracking>` (an
APS obligation), with the Player de-duplication kept as robustness.
Alternatively, add a sentence saying the Table 44 scope rules apply to
MPD event streams only.

### K-27 — PUB-18 mandates a contentless `SupplementalProperty` for `urn:mpeg:dash:urlparam:2025`

**Ambiguity.** Annex I.3.1 says in general that *"This extended scheme
is signalled through the use of EssentialProperty or
SupplementalProperty descriptors"*. For the 2025 scheme, however, the
only signalling it specifies is *"An MPD.EssentialProperty element with
the attribute @schemeIdUri having value of "urn:mpeg:dash:urlparam:2025"
shall be present and have no content, unless the scheme is explicity
allowed in a profile"*. Under an allowing profile (Advanced Linear:
*"Extended HTTP GET request parametrization (I.3) may be used"*,
§8.13.2.1) no descriptor is required at all. The contentless
`SupplementalProperty` PUB-18 requires is therefore permitted by the
general sentence, but for this scheme it has no semantics the base
defines. PUB-18 also routes Publishers into Advanced Linear, where K-29
is open.

**Suggested clarification.** State that under an allowing profile the
descriptor is optional, or keep the `SupplementalProperty` and cite the
general I.3.1 sentence as its basis. Cross-reference K-29 / §8.13 item 1
from PUB-18.

### K-29 — SGAI event streams under Advanced Linear

**Ambiguity.** §8.13.1 announces *"Support for a restricted set of DASH
events"*. §8.13.2.2 says *"EventStream elements may indicate Alternative
MPD (5.16) and Callback (5.10.4.5) event schemes"*, and §8.13.2.1 says
*"Periods and Representations which do not conform to the constraints in
this subclause may not be presented."* The base's own Advanced Linear
example (K.6.4) carries an `EventStream` of
`urn:mpeg:dash:event:service-description:2024`, a scheme §8.13.2.2 does
not name. That supports reading the list as non-exhaustive, but it does
not settle the question for application schemes. §8.13 item 1 already
records this.

**Suggested clarification.** Keep it open and route it to the base
editors, as §8.13 item 1 proposes.

### K-34 — Drop-before-play of a List MPD Period (PLY-35)

**Ambiguity.** For insertion the base bounds the alternative
presentation by trimming: *"For insertion events, APDA = min(APD,
APDmax)"* (Table 57). It has no rule that drops a Period of a
successfully merged List MPD because of its declared duration. PLY-35
permits exactly that (MAY). This is a Player permission on an inherited
construct, and §4.5.5 and §8.13 item 12 acknowledge it without
recording it in §4.8.3. It is Marginal, not Non-conforming, because the
base states no explicit obligation to play every Period (a Period can
already be removed during the merge, step 2). The effect is still that
what plays differs from what the base model produces.

**Suggested clarification.** Either restrict PLY-35 to the non-linear
families, or record it in §4.8.3 as a declared departure with its scope
(List MPD, insertion and replacement).

### K-35 — `urn:svta:` is not a registered URN namespace

**Ambiguity.** Table 43 asks only that *"The string may use URN or URL
syntax"*. A URN with an unregistered NID has URN syntax but is not a
formal URN, and the base recommends date-stamping only for URLs.
Nothing in the base is violated. The spec records this as §8.13 item 13.

**Suggested clarification.** None beyond §8.13 item 13. Registering the
NID, or moving to a URL under an SVTA-owned domain with a date, would
remove it.

## Open questions surfaced

- **`StringVectorType` as an XML Schema list** (§5.0, §4.8.2, cited as
  the model for `LayoutTokenListType`). Searched the extracted text for
  `simpleType name="StringVectorType"` and for `StringVectorType` (6
  hits, all attribute declarations, no type definition). The definition
  sits in the separately published `DASH-MPD.xsd`, not in the PDF body.
  The prose that was found (*"whitespace-separated list"* for the
  `@dependencyId` semantics) supports the claim. `[fetch-failed]` for the
  type definition only.
- **Exact wording of the EssentialProperty NOTE.** A first search for
  *"The DASH Client is expected to ignore the parent element that
  contains the descriptor"* returned 0 hits because the base text reads
  *"the DASH Client is expected to ignore the parent element that
  contains the descriptor"* after *"If the scheme or the value for this
  descriptor is not recognized,"*. Re-searched with *"ignore the parent
  element"*: 1 hit (§5.8.4.8, NOTE 1). DR-9 is quoted correctly.

## Summary

- Total constructs audited: 36
- Conforming: 27
- Marginal: 8 (K-12, K-17, K-19, K-21, K-27, K-29, K-34, K-35)
- Non-conforming: 1 (K-36)

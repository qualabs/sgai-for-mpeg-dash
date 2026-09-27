[GROUNDED_BY=iso-23009-1-2026-pdf]

# DASH conformance audit — v12.6 (2026-09-27)

**Audit target**: `../output/v12.6-sgai-spec.md`.
**Reference**: the edition declared in
`../context/00-normative-base.md` (ISO/IEC 23009-1:2026, sixth edition).
**Method**: inventory + clause searches against the primary copy +
per-construct verdict.

The key words MUST, SHOULD and MAY in suggested fixes are used as in
IETF RFC 2119.

## Scope

This audit covers every construct v12.6 introduces or modifies in a DASH
document, and the inherited base constructs whose semantics v12.6 restates
or constrains: the two window schemes and their child elements and
attributes, the List MPD additions, the empty linear resolution, the
sub-MPDs, both tracking carriers, the standalone `<svta:OverlayList>` and its
schema, the request-parameter rules, the profile declarations, the
pause-delivery `Metrics` request, and the Player rules that restate the base
Alternative-MPD processing model. Design quality is out of scope.

No audit was produced for v12.5, so this one covers the two incremental
steps since v12.4 together. v12.5 reverses PLY-41: a resolution document
whose candidates the device can render none of is now a failed execution in
every family, grounded for the linear family on §5.16.2.2.6 (§3.1, §4.5.6,
§6.3, §6.5, §7.12, §8.1, §8.2, C.6, L.7, R.2.4, R.6); §8.13 item 14 is
removed. v12.5 also rewrites PLY-20 and PLY-86 so that an attempt which ends
with no candidate rendered returns to the fallback chain (DP-3; §1.4, §4.1,
§4.5.3, §4.5.17, §8.2 E7/E8/E11, §8.3). v12.6 reshapes §7.12 path 4, Annex
L.7 and L.8 to UC-12 and adds one `<svta:OverlayList>` example in L.7. No
DASH construct is added or removed. K-1 to K-36 keep their constructs; K-37
is the PLY-86 rule as rewritten in v12.5.

## Method summary

- **Inventory.** Carried from the v12.4 audit and re-checked against the
  full `diff` of v12.4 and v12.6 (243 lines), read line by line, together
  with `v12.5-context-delta.md` and `v12.6-context-delta.md`. The §8.13 item
  numbers the verdicts cite (1, 9, 10, 11, 12) are unchanged; item 14 is gone.
- **Primary copy.** The PDF whose SHA-256 equals `primary_copy.sha256`
  (`a7274eb2…be100`); `bin/check-normative-base.py` exited 0. Extracted once
  with `pdftotext -layout` into a private RAM directory. The licence header
  and footer lines were stripped before any search; a grep for them
  afterwards returned 0 (the same grep on the unstripped extraction returned
  1152). Whitespace was flattened so that phrases spanning line breaks match.
- **Quotations.** A script extracted the 99 distinct italic quotations of
  v12.6, split them at ellipses, and looked each fragment up in the
  flattened text with case, quotes and dashes normalised. A known-present
  phrase (*"The queue is empty"*) matched and an invented one did not. 98
  matched. The other is the `@skipAfter` sentence of Table 63, split in the
  extraction by the table's *Default* column, as in v12.4. Against v12.4 one
  quotation is added and one removed: PLY-41 now quotes *"The reasons for
  this include (but are not limited to)"*, the longer form of the fragment
  §8.13 item 14 quoted.
- **Clause searches for the changed rules.** Six, each quoted below:
  the §5.16.2.2.6 failure conditions and their open list of reasons; the
  §5.16.2.2.5 step 2 b to d queue processing; the E.c definition (Table 58);
  the NOTE 2 sentence PLY-86 quotes; the §5.16.2.2.7 playhead reset; and a
  search for any base rule on a failure after alternative playback has
  started (`execution succeed`, `successful execution`, `successfully
  executed`, `(error|fail) during playback of the alternative`), which
  found the step 2 c and dual-client sentences and no such rule.
- **Structural checks.** v12.6 has 84 `xml` blocks: the 83 of v12.4
  byte-identical, plus the new L.7 document. All 84 parse as well-formed; a
  malformed control document was rejected. The new document was checked by
  hand against the §5.10.1 schema: `family` (required, `FamilyType`
  `overlay`), `dismissAfter`, one `Ad` with one `RenderableAsset` carrying the
  three required attributes, `layout` a `LayoutTokenType` value.
- Each construct is assessed Conforming / Marginal / Non-conforming.

## Inventory + verdicts

| ID | Construct | Type | Placement | Verdict | Rationale |
|----|-----------|------|-----------|---------|-----------|
| K-1 | Namespace `urn:svta:dash:sgai:2026` | Extension namespace | Elements and attributes in MPDs, List MPDs, standalone document | Conforming | §5.2.1: *"the MPD shall be authored such that, after XML attributes or elements in the other namespaces than the DASH namespace are removed, the result is a valid XML document formatted according to that schema and that conforms to this document."* Every MPD example stays valid after removal (Annex G.3 shows it). |
| K-2 | Scheme `urn:svta:dash:sgai-overlay:2026` | Event scheme | `Period/EventStream@schemeIdUri` | Conforming | An application scheme. §5.10.1 lets a client *"subscribe to an Event Stream of interest and ignore Event Streams that are of no relevance or interest."* See K-35 for the URN form. |
| K-3 | Scheme `urn:svta:dash:sgai-pause-trigger:2026` | Event scheme | `Period/EventStream@schemeIdUri` | Conforming | As K-2. A trigger shaped as a span is scheme semantics: Table 44 says of `@duration` that *"The interpretation of the value of this attribute is defined by the scheme owner"*. |
| K-4 | `EventStream`/`Event` used for windows (§5.1.3) | Base element usage | `Period` | Conforming | One stream per family and no `@value` fits *"A Period shall contain at most one EventStream element with the same value of the @schemeIdUri attribute and the value of the @value attribute"* (§5.10.2.1). A unique `Event@id` fits *"Each EventStream element shall not contain two Event elements with the same value of Event@id"* (Table 44). The §5.1.3 types match `EventType`. `EventStreamType` has no `xs:anyAttribute`, and no example puts a foreign attribute on it. |
| K-5 | `<svta:OverlayPresentation>` | Foreign element | Child of `Event` | Conforming | `EventType` ends its sequence with `<xs:any namespace="##other" processContents="lax" …/>`. Table 44: *"XML content, possibly using elements external to the MPD namespace"*. |
| K-6 | `<svta:PauseAdPresentation>` | Foreign element | Child of `Event` | Conforming | As K-5. |
| K-7 | `@durationCap` | Attribute (own name) | On K-5/K-6 | Conforming | A new name, so the base `@maxDuration` default (*"If absent, the value is assumed to be infinity"*, Table 63) is not inherited. The attribute is required on a pause window and bounds nothing there (§4.5.4, PLY-24, PLY-32, the §5.1.4 attribute table, and in v12.4 also §7 and Annex E.7). An own attribute with no semantics on one family breaks no base rule. |
| K-8 | `@earliestResolutionTimeOffset` on windows | Attribute (reused name) | On K-5/K-6 | Conforming | Name, units, type (`xs:unsignedLong`, as in `AlternativeMPDEventType`) and default match Table 63: *"The default is 60 seconds in units of timescale"*. |
| K-9 | `@executeOnce` on the pause window | Attribute (reused name) | On K-6 | Conforming | It reuses the E.c rule (*"Execution counter (number of times alternative MPD playback successfully started)"*, §5.16.2.2.2; §5.16.2.2.6 NOTE 3), with the base type and default. |
| K-10 | `@allowedLayouts`, `@customRegion` | Attributes (own) | On K-5 (K-6 for `@allowedLayouts`) | Conforming | Attributes of an extension-namespace element, with their own list types. The base describes its list attributes as *"whitespace-separated list"* (`@dependencyId`). |
| K-11 | `@linearRelation` (`supersede`, `on-top`) | Attribute (own) | On K-5/K-6 | Conforming | The departure `supersede` makes (PLY-48) from *"a set of normative conditions which hold for any sequence of Alternative MPD events"* (§5.16.2.2.1) is declared in §4.8.3, and the MPD author opts into it. A legacy Player executes the base event unchanged. |
| K-12 | Dispatch mode of the two window schemes | Scheme definition | §5.1.3/§5.1.4 | Conforming | Both declared on-receive, as the base schemes: *"The dispatch mode of this event scheme is "on-receive""* (§5.16.3, §5.16.4). A.13.7 (informative) gives the on-receive reading of `@duration`. |
| K-13 | Inherited `InsertPresentation` (§5.1.1) | Base event | `Event` of `…:insert:2025` | Conforming | Attribute types match `AlternativeMPDEventType`. *"The event shall not appear if the MPD type is "dynamic""* (§5.16.3), and `Event@status` is not used; both hold in every example. |
| K-14 | Inherited `ReplacePresentation` (§5.1.2) | Base event | `Event` of `…:replace:2025` | Conforming | *"This attribute shall not be present if the @maxDuration attribute is absent"* (Table 62, `@clip`) holds in every example. |
| K-15 | List MPD shape (§5.2.1, Annexes A/B/D/F/G/K) | Base document | `MPD@type="list"` | Conforming | The §8.14 rules hold. `ImportedMPD` is first in `PeriodType` and `ServiceDescription` follows `EventStream`. `ImportedMpdType` has `earliestResolutionTimeOffset` `xs:double`, default 60.0. `ServiceDescription` survives the merge (§5.3.2.6.3 step 3 b iv). |
| K-16 | `<svta:ClickThrough>`, `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>` in a List MPD | Foreign elements | Children of a candidate `Period` | Conforming | `PeriodType` ends in `xs:any ##other`, and the merge keeps them: *"ix) any elements from a different namespace"* (§5.3.2.6.3, step 3 b). |
| K-17 | Empty linear resolution (§5.2.3) | Base document shape | List MPD, one `Period duration="PT0S"`, no children | **Marginal** | See detail. §8.13 item 9 cites the governing condition; the List-profile question remains. |
| K-18 | SPS sub-MPD (§5.4) | Base document | Target of `ImportedMPD` / `@src` | Conforming | *"MPDs referenced in the ImportedMPD element shall be restricted to the constraints of a single period profile as defined in 8.15"* (§5.3.2.6.1). Every sub-MPD example satisfies §8.15.2. |
| K-19 | Sub-MPD `@profiles` = SPS **and** `isoff-live:2011` | Profile declaration | Sub-MPD root | Conforming | §4.8.5 states the consequence: *"The information in the @profiles parameters is merged into the MPD@profiles attribute"* (§5.3.2.6.3 step 3 a i), and under that profile *"The elements and attributes listed in subclause 5.2.3.2 may be ignored"* (§8.4.2), a list that contains `Period.EventStream`. |
| K-20 | Callback tracking in the sub-MPD (§5.5.1) | Base scheme reuse | `Period/EventStream` of the sub-MPD | Conforming | Table 47 gives `EventStream@value` `1`. The imported stream overrides the Linked Period's (step 3 c iv, *"EventStream@schemeIdUri and EventStream@value"*). Unique beacon numbering fits the Table 44 `@id` scope. |
| K-21 | `<svta:Tracking>` of type `dash:EventStreamType` (§5.5.2) | Foreign element reusing a base type | Child of `<svta:Ad>` | Conforming | The schema reuse is valid (K-31). §5.5.2 re-anchors the timebase, the `@id` scope and the no-duplicate-`@id` rule as this specification's own. The sentence that the one candidate-level carrier reuses the callback scheme and `EventStreamType` whole is consistent with it. |
| K-22 | `<svta:OverlayList>` standalone document (§5.2.2) | New document type | HTTP response to a window `@uri` | Conforming | Not an MPD, and no document a legacy Player reads refers to it, so neither `MPDtype`'s required `profiles` nor the List-profile binding applies. Whether it counts as an extension point is a project reading (§8.13 item 10), not a base rule. |
| K-23 | `<svta:Ad>`, `<svta:RenderableAsset>` (non-AV carrier) | Foreign elements | In K-22 | Conforming | No image or HTML asset reaches an `AdaptationSet`/`Representation`, so §7.3.1 and §8.12.4.3 (*"The @mimeType shall be set to "<contentType>/mp4""*) are respected. The v12.4 rule that a scripted creative is wrapped in an HTML document and carried as `text/html` (§3.5, §5.2.2) keeps it on this side. |
| K-24 | Video option referencing an SPS MPD by `@src` | Reference to a base document | `<svta:RenderableAsset>` | Conforming | An ordinary §8.15 MPD. `ImportedMPD` is not used outside a Period. |
| K-25 | `@family`, `@dismissAfter`, `@validFor`, `@onExhausted` | Attributes (own) | On K-22 | Conforming | Extension-namespace document. `@dismissAfter` does not reuse `@skipAfter`, whose default is PT0S (Table 63). |
| K-26 | Reserved query parameters `sgai-*` (§5.8) | Request parameters | Query of a window `@uri` | Conforming | Not an MPD construct; Annex I.3 is not used for windows. §8.13.2.7 names *"callback, altmpd and mpdlink"* for `@includeInRequests`. |
| K-27 | `RequestParam` on inherited linear events (PUB-18) | Base mechanism usage | `EventStream`/MPD of the main MPD | Conforming | *"This extended scheme is signalled through the use of EssentialProperty or SupplementalProperty descriptors"* (I.3.1). §8.13.2.4 permits `RequestParam` with `altmpd` in an `EventStream` of Alternative MPD events. |
| K-28 | Main MPDs under `isoff-live:2011` (§4.8.5) | Profile declaration | Main MPD root | Conforming | §8.4.2: *"The elements and attributes listed in subclause 5.2.3.2 may be ignored."* The spec states the consequence. |
| K-29 | SGAI event streams in an Advanced Linear MPD | Profile interaction | Main MPD | **Marginal** | See detail. Recorded in §8.13 item 1. |
| K-30 | `Metrics metrics="PlayList"` + `Reporting` (§5.9, PUB-13) | Base element usage | MPD level, after `Period` | Conforming | `Metrics` follows `Period` in `MPDtype`; *"No reporting scheme is specified in this document"* (§5.9.4); kept out of sub-MPDs (§8.15.2). |
| K-31 | Schema of §5.10.1 | XML Schema | Extension namespace | Conforming | Imports `DASH-MPD.xsd`; valid XSD 1.0 simple types; `##other` wildcards with no Unique Particle Attribution conflict; `Event` children of `<svta:Tracking>` are DASH-namespace (`elementFormDefault="qualified"`), and every example declares it. Unchanged since v12.2. |
| K-32 | `PercentRectType` / SRD notation | Notation reuse | `@customRegion`, `@rect` | Conforming | Only the notation is reused (*"the x-axis is oriented from left to right"*, H.2.2). SRD placement (H.1) is untouched. |
| K-33 | Fallback, failed execution, E.c (PLY-38, -39, -40, -44) | Player restatement of the base model | §4.5.6 | Conforming | These quote §5.16.2.2.5 step 2 d, §5.16.2.2.6 and NOTE 3 verbatim, and the PLY-39 table maps each of the four ways the resolution itself can fail to a §5.16.2.2.6 condition (reworded in v12.5, same mapping). The tie-break by document order is an addition to a queue *"ordered by the presentation time PRT"* (§5.16.2.2.2). |
| K-34 | Drop-before-play of a List MPD Period (PLY-35) | Player rule on an inherited event | §4.5.5 | **Marginal** | See detail. §8.13 item 11; refinement gap 2 (validation F-2). |
| K-35 | URN form `urn:svta:…` of the three URIs of §2.1 | URI syntax | Scheme and namespace identifiers | **Marginal** | See detail. §8.13 item 12. |
| K-36 | PLY-41 applied to a linear resolution document (§4.5.6) | Player rule on an inherited event | §4.5.6 | Conforming | v12.5 makes a document with no candidate the device can render a failed execution under PLY-38 in every family. On the linear family that is the base: *"The playback of the alternative presentation cannot start. The reasons for this include (but are not limited to) the following"*, among them *"Alternative MPD is a List MPD, and merge process resulted in no available media"* (§5.16.2.2.6), followed by *"If execution fails, steps a-c above are repeated for next events in QE"* (§5.16.2.2.5 step 2 d). §6.5, §7.12 path 4, §8.2 E7, C.6, L.7 and R-PLY-20 follow it. DOC-3 and §4.8.3 (one departure, PLY-48) are consistent with it again. |
| K-37 | PLY-86 / E11: a runtime failure that leaves "no candidate rendered" returns to the fallback chain (§4.5.17, §8.2, §8.3) | Player rule on an inherited event | §4.5.17 | **Marginal** | See detail. Conforming on the linear family only if "rendered" means that playback of the candidate started. |

## Base-standard findings (highlights)

- **Failed execution.** *"Execution fails if at least one of the conditions
  below is true at PRTA"*; one is *"The playback of the alternative
  presentation cannot start"*, whose reasons *"include (but are not limited
  to)"* *"Media playback is impossible due to missing media or
  initialization segments"* (§5.16.2.2.6). The conditions are evaluated at
  PRTA.
- **After a successful start.** *"If execution succeeds, processing stops
  here"* (§5.16.2.2.5 step 2 c), and E.c counts *"number of times
  alternative MPD playback successfully started"* (Table 58). No clause
  found returns the Player to QE because an alternative presentation that
  started then failed.
- **Extension points and profiles.** Unchanged from v12.4: `EventType`,
  `PeriodType` and `EventStreamType` admit `xs:any ##other`; the List profile
  *"is an extension of the ISO-BMFF CMAF Profile"* (§8.14); §8.13.2.2 names
  Alternative MPD and Callback schemes for Advanced Linear `EventStream`s.

## Non-conforming items detail

None. K-36, Non-conforming in v12.4, is Conforming in v12.6 (see its row).

## Marginal items detail

### K-17 — Empty linear resolution vs the List profile's CMAF base

§8.13 item 9 names *"The playback of the alternative presentation cannot
start"* as the condition the empty shape falls under, with the merge
condition as its closest analogue; §5.2.3 and PLY-39 say the same. The
document is schema-valid, and Table 4 admits it (*"At least one Adaptation
Set shall be present in each Period unless the value of the @duration
attribute of the Period is set to zero."*). But the List profile *"is an
extension of the ISO-BMFF CMAF Profile"* (§8.14), and a Media Presentation
conforms to a profile only if *"There is at least one Representation in each
Period in the profile-specific MPD"* (§8.1). §8.13 item 9 records this, so
it is an open question and not a conflict.

**Suggested clarification.** None beyond §8.13 item 9.

### K-29 — SGAI event streams under Advanced Linear

§8.13.1 announces *"Support for a restricted set of DASH events"*.
§8.13.2.2 says *"EventStream elements may indicate Alternative MPD (5.16)
and Callback (5.10.4.5) event schemes"*. §8.13.2.1 says *"Periods and
Representations which do not conform to the constraints in this subclause
may not be presented."* The base's own K.6.4 example carries a scheme
§8.13.2.2 does not name, which suggests the list is not exhaustive; that
does not settle it for application schemes.

**Suggested clarification.** Keep it open and route it to the base editors
(§8.13 item 1).

### K-34 — Drop-before-play of a List MPD Period (PLY-35)

For insertion the base trims: *"For insertion events, APDA = min(APD,
APDmax)"* (Table 57). It has no rule that drops a Period of a successfully
merged List MPD because of its declared duration, and PLY-35 permits that
(MAY). This is Marginal and not Non-conforming because the base states no
explicit obligation to play every Period: step 2 of the merge already
removes invalid Periods. §4.5.5 and §8.13 item 11 acknowledge it without
recording it in §4.8.3.

**Suggested clarification.** Either restrict PLY-35 (R7.3) to the non-linear
families, or record it in §4.8.3 as a departure scoped to List MPDs.

### K-35 — `urn:svta:` is not a registered URN namespace

Table 43 asks only that *"The string may use URN or URL syntax"*. A URN with
an unregistered NID has URN syntax but is not a formal URN. No base rule is
violated, and §8.13 item 12 records it.

**Suggested clarification.** None beyond §8.13 item 12.

### K-37 — PLY-86 and a linear ad that fails after it started

**What the spec says.** PLY-86 covers resolving *or rendering* an accepted
ad failing at runtime, "for example a decode error, a malformed candidate,
or a mid-ad network loss": the Player aborts the ad, and "When the attempt
ends with no candidate rendered, it produced no ad and PLY-20 governs what
follows", which through PLY-20 and PLY-38 is the next overlapping window.
E11 in §8.2 and step 4 of §8.3 say the same, and E11 names "an ad segment
returns an error" among its triggers. PLY-86 applies to every family.

**Why it is Marginal.** On the linear family the base evaluates failure
*"at PRTA"*, and *"Media playback is impossible due to missing media or
initialization segments"* is one of its reasons, so a linear ad that cannot
start is a failed execution and the next event in QE is tried: PLY-86 agrees
with that. But once playback has started, the base counts the execution as
successful (*"If execution succeeds, processing stops here"*, §5.16.2.2.5
step 2 c; E.c counts playback that *"successfully started"*, Table 58), and
no clause found sends the Player back to QE when that presentation later
fails. The spec does not define "rendered". If a candidate aborted by a
mid-ad network loss counts as not rendered, a Player of this specification
executes the next queued linear event where the base would continue with the
main presentation, a second departure that §4.8.3 and DOC-3 do not record.
If "rendered" means "its playback started", PLY-86 conforms. The spec
already uses the base's "successfully started" for the pause window's
counter (PLY-64, §4.5.10), so the conforming reading is
available but not stated.

**Suggested clarification.** In PLY-20 and PLY-86 (R5.3 and the DP-3
consequence in `context/`), state that a candidate counts as rendered once
its presentation started, and that for the linear family this is E.c's
*"successfully started"*; a failure after that point continues with the
primary content. Alternatively, scope the return to the fallback chain after
a runtime failure to the non-linear families.

## Open questions surfaced

- **`StringVectorType` as an XML Schema list** (§5.0, §4.8.2). The type
  definition is not in the PDF body: a search for
  `simpleType name="StringVectorType"` returns 0, while `simpleType name="`
  alone finds other base types. The type sits in the separately published
  `DASH-MPD.xsd`. The prose (*"whitespace-separated list"* for
  `@dependencyId`) supports the claim, and it bears on no verdict.
- **A base rule for failure after an alternative presentation started**
  (K-37). Searched for `execution succeed`, `successful execution`,
  `successfully executed` and `(error|fail) during/while playback of the
  alternative`; the hits were §5.16.2.2.5 step 2 c and the dual-client NOTE,
  neither of which addresses it. The absence is what K-37 rests on.

## Summary

- Total constructs audited: 37
- Conforming: 32
- Marginal: 5 (K-17, K-29, K-34, K-35, K-37)
- Non-conforming: 0

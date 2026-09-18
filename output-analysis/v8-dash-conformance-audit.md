[GROUNDED_BY=iso-23009-1-2026-pdf]

# DASH conformance audit — v8 (2026-09-17)

**Audit target**: `../output/v8-sgai-spec.md` (7657 lines).
**Reference**: the edition declared in `../context/00-normative-base.md` —
ISO/IEC 23009-1:2026, Sixth edition. The primary copy was opened for this
audit; its SHA-256 matched `primary_copy.sha256` byte for byte, and the
extraction's Foreword confirms *"This sixth edition cancels and replaces the
fifth edition (ISO/IEC 23009-1:2022)"*.
**Method**: inventory + clause searches against the primary copy +
per-construct verdict.

RFC 2119 vocabulary in quoted passages is the base specification's own.

## Scope

Conformance only: whether each construct the specification introduces or
modifies is admissible under the base specification's schema, extension-point
rules, event-placement rules, profile restrictions and inherited attribute
semantics. Design quality, requirement coverage and internal coherence are
the validation and detail-review sidecars' subject and are not assessed here.

## Method summary

- Inventory built from §2.1 (scheme URIs and namespaces), §4.7 (extension
  points and the per-construct compatibility audit), §5.1–§5.9 (syntax), and
  the Build-notes block at the end of the document.
- 48 clause searches against the primary copy, each grounded by quoting the
  sentence and not only its number. Verified verbatim: DASH §5.2.1 (three
  extension paragraphs), §5.3.1.3 (`MPDtype` XML syntax), §5.3.1.4,
  §5.3.2.2 Table 4, §5.3.2.3 (`PeriodType` XML syntax), §5.3.2.6.1,
  §5.3.2.6.2, §5.3.2.6.3, §5.3.7.2 (`@selectionPriority`), §5.3.11.1,
  Table 29 (`@preselectionComponents`), §5.6.2 Table 35, §5.8.4.8 NOTE 1,
  §5.8.4.9 NOTE, §5.8.5.16.1, §5.8.5.16.4, §5.9.1, §5.10.1, §5.10.2.1,
  §5.10.2.3 (`EventStreamType` and `EventType` XML syntax), §5.10.4.5.1,
  Table 47, §5.11.3, §5.16.1, §5.16.2.2.5 NOTE, §5.16.2.2.6, §5.16.3,
  Table 59, §5.16.4 Table 62, §5.16.5.2 Table 63, §5.16.6
  (`AlternativeMPDEventType` XML syntax), §7.3.1, §8.1, §8.12.1, §8.12.4.4,
  §8.14, §8.15.1, §8.15.2, §8.15.3, §H.1, §I.2.2.2 Table I.1, §I.3.1,
  Table I.4, §I.4.1, §A.5, §A.14.2, §4.2, Annex D.4.6 Table D.5.
- Two search habits applied. Whitespace was flattened before matching, and
  two reported zeroes turned out to be extraction artefacts rather than
  absences: in the two-column `Use / Default` tables the middle column
  interleaves into the prose, so `@skipAfter` reads
  `... (in fractional seconds) default: from the beginning ... till "PT0S" the
  moment ...` and a long phrase match fails. Both were re-run by clause
  location and found. Every negative below was controlled against a phrase
  known to be present in the same region.
- Each construct assessed Conforming / Marginal / Non-conforming.

**One limit on every schema claim here.** Annex B is not in the primary copy:
*"The schema of the MPD for this document is provided at:
https://standards.iso.org/iso-iec/23009/-1/ed-6/en (DASH-MPD.xsd)."* Schema
facts below are verified against the per-clause `XML syntax` snippets printed
in the body, which §5.2.2 subordinates to Annex B — *"In case of
inconsistencies, the schema in Annex B takes precedence both over the XML
syntax snippets provided in this clause and all prose text in this
document."* No inconsistency was observed, but the printed snippets are what
was read.

## Inventory + verdicts

| ID | Construct | Type | Placement | Verdict | Rationale |
|----|-----------|------|-----------|---------|-----------|
| C01 | `urn:svta:dash:sgai:2026` | XML namespace | n/a | Conforming | Foreign-namespace open content is the base specification's own extension point: `MPDtype`, `PeriodType`, `EventStreamType`, `EventType`, `RepresentationBaseType` and `AlternativeMPDEventType` each carry `<xs:any namespace="##other" processContents="lax"/>`, read from the printed snippets of DASH §5.3.1.3, §5.3.2.3, §5.10.2.3, §5.16.6 and the `RepresentationBaseType` snippet. |
| C02 | `urn:svta:dash:event:sgai-overlay:2026` | `EventStream@schemeIdUri` | `<EventStream>` in main MPD | Conforming | DASH §5.10.1: *"Events include DASH specific signalling or application-specific events. DASH events are identified by scheme identifiers defined in this document. For application specific events, a scheme identifier identifies the application such that the DASH Client can forward the event to the proper application."* `EventStream@schemeIdUri` is `xs:anyURI use="required"` with no enumeration. |
| C03 | `urn:svta:dash:event:sgai-pause-trigger:2026` | `EventStream@schemeIdUri` | `<EventStream>` in main MPD | Conforming | As C02. The window-on-the-timeline / trigger-off-it split has a base precedent the specification cites correctly: DASH §L.3.4.2, *"the Event@presentationTime and Event@duration attributes are used to indicate the start and the duration of the selection window"*, with the decision resolved off-timeline in DASH §L.3.3. |
| C04 | `urn:svta:dash:profile:sgai-overlay-list:2026` | `MPD@profiles` value | Overlay Resolution Document | **Marginal** | Detail M1. Admissible as an externally defined identifier, but the obligation the specification cites for it is scoped to the base document's own identifiers, and DASH §8.1 recommends against calling an external definition a profile. |
| C05 | `urn:svta:dash:request:sgai-resolution:2026` | `@includeInRequests` token | `<RequestParam>` | Conforming | DASH Table I.4 last row: *"a URN or tag URI, where the request type semantics is understood by the client and specified by the URN / tag URI owner. The client shall drop unknown URIs from the @includeInRequests and @includeInHeaders strings prior to processing them as specified in this Annex."* §I.3.6 adds *"In addition to the list of request types specified below a URN or a tag URI can be used to specify requests or other operations not described in this document."* |
| C06 | `<svta:OverlayPresentation>` | New element | Child of `<Event>` | Conforming | `EventType` is `mixed="true"` with `<xs:any namespace="##other" processContents="lax"/>` last in its sequence and `<xs:anyAttribute namespace="##other" processContents="lax"/>`. DASH §5.10.2.1: *"The Event element may contain further XML elements meaningful for a particular event scheme. These may be defined in this document … or in some external namespace."* Document order in the §5.8.1 example respects the sequence. |
| C07 | `<svta:PauseAdPresentation>` | New element | Child of `<Event>` | Conforming | As C06. |
| C08 | `<svta:OverlayList>` | New element | Child of `<Period>` | Conforming | `PeriodType`'s sequence ends in `<xs:any namespace="##other" processContents="lax" minOccurs="0" maxOccurs="unbounded"/>`, and the element is the Period's only child, so the sequence order holds. |
| C09 | `<svta:Candidate>` | New element | Child of `<svta:OverlayList>` | Conforming | Inside a subtree the DASH schema does not govern; removal by namespace (DASH §5.2.1) takes it with its parent. |
| C10 | `<svta:RenderableAsset>` | New element | Child of `<svta:Candidate>` | Conforming | As C09. |
| C11 | `<svta:BackgroundElement>` | New element | Child of `<svta:RenderableAsset>` | Conforming | As C09. |
| C12 | `<svta:Click>` / `<svta:ClickTracking>` | New elements | Child of `<svta:Candidate>`; on a linear slot, of the `ListMPD` `<Period>` | Conforming | Period placement covered by `PeriodType`'s `xs:any ##other`. The specification's own note on DASH §8.1 step 4 is correct and verified verbatim: *"All elements or attributes that are either (i) in this document and explicitly excluded by ProfA, or (ii) in an extension namespace and not explicitly included by ProfA, are removed from the profile-specific MPD."* |
| C13 | `<svta:AdSystem>`, `<svta:AdTitle>`, `<svta:Advertiser>`, `<svta:UniversalAdId>` | New elements | Children of `<svta:Candidate>` | Conforming | As C09. |
| C14 | `<ImportedMPD>` inside `<svta:RenderableAsset>` | Baseline DASH-namespace element at a placement the schema does not declare | Child of an SGAI element | **Marginal** | Detail M2. |
| C15 | Callback `<EventStream>` inside `<svta:Candidate>` | Baseline DASH-namespace element at a placement the schema does not declare | Child of an SGAI element | **Marginal** | Detail M3. The construct survives the same removal test as C14, but §5.5.2 grounds it on a premise that is false: `<EventStream>` is in the DASH namespace, and the `##other` wildcards exclude it by definition. |
| C16 | `<InsertPresentation>`, reused | Baseline element | Child of `<Event>` | Conforming | Every attribute, type and default in §5.1.1's table matches the printed `AlternativeMPDEventType`: `@uri` `xs:anyURI use="required"`, `@earliestResolutionTimeOffset` `xs:unsignedLong` with no schema default, `@serviceDescriptionId` `xs:unsignedInt`, `@maxDuration` `xs:unsignedLong default="2251799813685247"`, `@executeOnce` `xs:boolean default="false"`, `@noJump` `xs:integer default="0"`, `@skipAfter` `xs:duration default="PT0S"`. Children are `xs:any ##other` plus `SupplementalProperty`, as stated. The dynamic restriction is verbatim: *"The event shall not appear if the MPD type is \"dynamic\"."* (DASH §5.16.3). |
| C17 | `<ReplacePresentation>`, reused | Baseline element | Child of `<Event>` | Conforming | `AlternativeMPDReplaceEventType` extends `AlternativeMPDEventType` with `@returnOffset` `xs:unsignedLong`, `@clip` `xs:boolean default="true"`, `@startWithOffset` `xs:boolean default="false"` — exactly the three §5.1.2 lists, and it defers the conditional restrictions to DASH §5.16.4 / §5.16.5.2 rather than restating them, which is the correct move: one of them (*"When alternative media presentation is a live presentation, it always starts at the live edge, and @startWithOffset attribute shall not be present."*) would otherwise have needed reproducing. |
| C18 | `@maxDuration` narrowed from optional to required on the linear insert slot | Attribute-use narrowing | `<InsertPresentation>` | Conforming | Narrowing an optional baseline attribute to required adds a constraint. The specification records both the schema default and Table 63's prose default (*"Default: Infinity."*) rather than picking one, and Table 63's *"If the value of @maxDuration is zero, the event is not executed."* is not contradicted. |
| C19 | `@maxDuration` on the two new non-linear slots | Baseline name reused on a foreign-namespace element | `<svta:OverlayPresentation>`, `<svta:PauseAdPresentation>` | Conforming | Unprefixed attributes on an SGAI element are in no namespace and are that element type's own; no DASH rule reaches them. Table 63's units (*"expressed in units of EventStream@timescale"*) and termination rule (*"it shall be terminated at the end of this duration"*) are the ones the specification claims to inherit. |
| C20 | `@executeOnce` reused on a pause-trigger window | Baseline name, new trigger | `<svta:PauseAdPresentation>` | Conforming | The substitution the specification declares is exactly the one DASH §5.16.2.2.6 states for the baseline counter: *"When the alternative media presentation triggered by an event successfully starts playing, the corresponding counter E.c is incremented …"*. The asymmetry it argues from is also verbatim: *"Since there is no playhead-triggered processing during the listen mode, processing always resumes at the playhead position PHP = RT."* (DASH §5.16.2.2.5 NOTE). |
| C21 | `@allowedLayouts` as a whitespace-separated token list | New attribute | Two SGAI slot elements | Conforming | The encoding precedent the specification cites checks out: `@dependencyId` is `type="StringVectorType"`, and `Preselection@preselectionComponents` is `type="StringVectorType" use="required"`, described as *"the ids of the contained Adaptation Sets or Content Components … as white space separated list in processing order"*. DASH §8.1 confirms the contrast: *"The identifier of a profile shall not contain any comma."* |
| C22 | Linear `ListMPD` resolution document | Baseline profile reuse | APS response to a linear slot | **Marginal** | Detail M4. The two rules §5.2.1 states are verbatim (§8.14 rules 3 and 5), and rule 4 is quoted correctly, but the profile's inherited constraint set is not uniquely identified by the base specification. |
| C23 | Overlay Resolution Document — one `<Period duration="PT0S">` carrying no Adaptation Set | New document shape | APS response to a non-linear slot | Conforming | The load-bearing rule is verbatim in DASH §5.3.2.2 Table 4: *"At least one Adaptation Set shall be present in each Period unless the value of the @duration attribute of the Period is set to zero."* `MPD@profiles` and `MPD@minBufferTime` are `use="required"` in `MPDtype`, and the document declares both; the other attributes it declares unconditionally are optional in the schema, which narrows. |
| C24 | The empty resolution document, both shapes | Degenerate document shape | APS response | **Marginal** | Detail M5. `<xs:element name="Period" type="PeriodType" maxOccurs="unbounded"/>` with `minOccurs` omitted is verified verbatim, so the zero-Period alternative is correctly excluded; what is not settled is the linear shape against the constraints §8.14 inherits. |
| C25 | Sub-MPD bound to the Single-Period Static profile | Baseline profile reuse | Target of every `<ImportedMPD>` | Conforming | Every row of §5.4's table is verbatim in DASH §8.15.2: `@type` *"shall be \"static\""*, *"The MPD@availabilityStartTime shall not be present"*, *"The MPD@mediaPresentationDuration attribute shall not be present, but the Period element shall include the @duration attribute"*, *"One and only one Period element shall be present"*, and `MPD.Metrics` / `MPD.SupplementalProperty` among the forbidden MPD-level items. The binding itself is verbatim in DASH §5.3.2.6.1: *"MPDs referenced in the ImportedMPD element shall be restricted to the constraints of a single period profile as defined in 8.15."* |
| C26 | Callback event scheme reused for every timeline beacon | Baseline scheme reuse | `<EventStream>` in a sub-MPD `<Period>` or in `<svta:Candidate>` | Conforming | DASH §5.10.4.5.1 verbatim as quoted. Table 47 fixes `EventStream@value` at `1`, which the specification declares; `@value` is optional in `EventStreamType` and narrowing it to required adds a constraint. The URL-as-text-content choice is correct: `EventType` is `mixed="true"` and `@messageData` is `use="prohibited"` with the annotation *"Deprecated in favor of carrying the message information in the value space of the event"*, quoted exactly. |
| C27 | `Event@id` narrowed from optional to required on tracking carriers | Attribute-use narrowing | `<Event>` of the callback scheme | Conforming | `EventType` declares `<xs:attribute name="id" type="xs:unsignedLong"/>` with no `use`, i.e. optional. Narrowing adds a constraint, and the type the specification states is the schema's. |
| C28 | `<RequestParam>` authored inside the slot's `<EventStream>`, with the empty MPD-level enabling descriptor | Baseline mechanism reuse | `<EventStream>`; `<MPD>` | Conforming | Explicitly permitted: *"The RequestParam element(s) may be present in elements such as but not limited to MPD, Period, AdaptationSet, Representation, Preselection, or EventStream."* (DASH §I.3.1). The enabling descriptor requirement is verbatim, including its typo: *"An MPD.EssentialProperty element with the attribute @schemeIdUri having value of \"urn:mpeg:dash:urlparam:2025\" shall be present and have no content, unless the scheme is explicity allowed in a profile"*. The NOTE the specification leans on is verbatim too. Authoring the descriptor after the last `</Period>` is required by `MPDtype`'s sequence, where `EssentialProperty` follows `Period`. `UrlParamInfo` appears zero times in the primary copy, against six occurrences of `ExtUrlQueryInfo` as a control — the Build-notes divergence 1 is confirmed. |
| C29 | `PlayList` metric request on the primary MPD | Baseline metric reuse | `<Metrics>` on the main MPD | Conforming | Annex D.4.6 Table D.5 verbatim: *"A list of playback periods. A playback period is the time interval between a user action and whichever occurs soonest of the next user action, the end of playback or a failure that stops playback."* `starttype` carries *"Resume - Resume from pause"*; `stopreason` carries *"Rebuffering - Rebuffering"* and *"UserRequest - User request"*. The reason it cannot travel in a sub-MPD is the `MPD.Metrics` prohibition of DASH §8.15.2, correctly cited. The inherited silence on transport is verbatim from DASH §5.9.1. |
| C30 | Hybrid slot — two events at one `@presentationTime`, in two event streams | Authoring pattern, no new construct | Main MPD | Conforming | `PeriodType` admits `EventStream` `maxOccurs="unbounded"`, and DASH §5.10.1 clusters events by scheme/value pair, so two streams of different schemes are independent by construction. |
| C31 | Overlapping windows of one family as a fallback chain | Authoring pattern, no new construct | Main MPD | Conforming | No base rule constrains the temporal relation of two `<Event>` elements in one stream. The precedent the specification cites for document-order-as-preference is verbatim in DASH §5.11.3, including *"Each MPD may contain at most one Fallback Presentation descriptor"* and *"If multiple URLs are provided, the content author expresses the preferences of using one of those by the order with the first one having the highest preference."* |
| C32 | Player-declared capability query parameters | Not an MPD construct | Resolution request URL | Conforming | Nothing in the base specification governs query parameters a client adds to a request it originates. The specification's ground for not routing them through DASH §I.3 is verbatim: `@queryTemplate` *"provides URL parameters template information. This string shall contain one or more $<ParamIdentifier>$ template identifiers"* (DASH §I.2.2.2), authored by the content author, and §I.4.1's payload is player **state** — *"In some cases, such as dynamic advertisement insertion and content steering, there is a need to express knowledge of the current state of the player."* |
| C33 | §4.7.3's placement table (7 rows) | Fact table the carrier choices rest on | n/a | Conforming | All seven rows verified against the printed snippets. `PeriodType` carries `SupplementalProperty` and **no** `EssentialProperty` — correct, and correctly flagged as counter-intuitive. `EventStreamType` carries both descriptors and `xs:any ##other` but **no** `xs:anyAttribute` — correct. `EventType` carries both plus `xs:anyAttribute` — correct. `AlternativeMPDEventType` carries `SupplementalProperty` only, plus `xs:anyAttribute` — correct. `MPDtype` and `RepresentationBaseType` carry both, `xs:any` and `xs:anyAttribute` — correct. `ImportedMpdType` is `<xs:simpleContent><xs:extension base="xs:anyURI">` with `<xs:anyAttribute namespace="##other" processContents="lax"/>` and no `xs:any` — correct, quoted below. |
| C34 | §5.3.2's rejection of both vendor descriptors as the non-audiovisual carrier | Carrier decision | n/a | Conforming | The asymmetry it turns on is verbatim. DASH §5.8.4.8 NOTE 1: *"If the scheme or the value for this descriptor is not recognized, the DASH Client is expected to ignore the parent element that contains the descriptor."* DASH §5.8.4.9 NOTE: *"… is expected to ignore the descriptor."* |
| C35 | §5.1.3's rejection of the supplementary video descriptor | Carrier decision | n/a | Conforming | All four grounds check out. DASH §5.8.5.16.1 verbatim as quoted; the composition hand-back verbatim — *"Potential manipulation of the stream and the composition of the main video and the supplementary video are out of the scope of the DASH client."*; Preselection-level placement confirmed (*"When a supplementary video descriptor is present in a Preselection element …"*); and the single-VVC-decoder path §1.2 cites is verbatim in DASH §5.8.5.16.4. |
| C36 | §5.1.3's and §5.3's rejections of SRD, nonlinear playback, Preselection and `@selectionPriority` | Carrier decisions | n/a | Conforming | DASH §H.1: *"SRD information shall be contained exclusively in these two MPD elements (AdaptationSet and SubRepresentation)."* DASH §L.1: *"This Annex provides Nonlinear Playback capabilities, to serve Interactive Storyline content with MPEG-DASH."* DASH §5.3.11.1: *"Preselections define user experiences that can be selected by the DASH Client."* DASH §5.3.7.2: `@selectionPriority` *"specifies the selection priority for the described data structures, i.e. the one described by the containing element. In the absence of other information, higher numbers are the preferred selection over lower numbers."*, `default=1` — so the "opposite direction from document order" claim holds. |
| C37 | §4.7.2's closure of the media axis | Constraint argument | n/a | Conforming | Both legs verbatim: DASH §5.3.2.6.1's SPS binding, and DASH §7.3.1's *"The @mimeType attribute of each Representation shall be provided according to IETF RFC 4337."* The workaround-closing leg (Table 4) is verbatim too. See the third base-standard finding for one carrier the argument does not name and why the conclusion survives it anyway. |
| C38 | §4.7.8's position that a declared profile does not certify the constructs | Conformance posture | n/a | Conforming | DASH §8.1 step 4 verbatim, and the ownership rule it defers to is verbatim as well: *"The owner of the URI is responsible to provide sufficient semantics on the restrictions and permission of this interoperability point."* |
| C39 | §5.2.2.2's decision to declare `@type="static"` rather than `"list"` | Attribute choice | Overlay Resolution Document | Conforming | The premise is correct. DASH §5.3.1.4 defines the value in the body, independently of the List profile: *"For Media Presentations with MPD@type set to \"list\" the constraints of a static Media Presentation shall apply."* plus the XLink prohibition and *"MPDs of @type=\"list\" may contain Linked Periods."* DASH §8.14 rule 1 states only that a List MPD shall declare it. Build-notes divergence 3's fourth paragraph is therefore correct. |
| C40 | The "conforming MPD used as a carrier, not a Media Presentation" reading | Conformance posture | Both resolution documents | Conforming | DASH §8.1 separates the two ladders explicitly. The Representation rule the specification sets aside sits under *"A Media Presentation is conforming to profile ProfA when it satisfies the following: … 2) There is at least one Representation in each Period in the profile-specific MPD for ProfA."*, not under MPD conformance. The reading is textually supported; the base specification defines no term for "MPD used as a carrier", so it is a reading and not a quotation. |

## Base-standard findings (highlights)

**The base specification's own scheme registry misnumbers the fallback
descriptor, and the specification cites the right clause anyway.** Table 2
routes `urn:mpeg:dash:fallback:2016` to 5.11.2, which is *Regular Chaining*;
the descriptor is defined in 5.11.3, *Fallback Chaining*, and §5.11.1 agrees
(*"error conditions as defined in subclause 5.11.3 and serves as a
fallback"*). §5.1.6 and §5.3.2 cite DASH §5.11.3. No action.

**`EmptyAdaptationSet` is the workaround §4.7.2 does not name, and it is
closed for a reason the document does not give.** Table 4 lists it separately
from `AdaptationSet` — *"specifies an Adaptation Set that does not contain
any Representation element"* — so a reader could take it as a way to satisfy
the at-least-one-Adaptation-Set rule while carrying no media at non-zero
duration. It is not: *"This element shall only be present, if an Essential
Descriptor is present with @schemeIDURI set to
\"urn:mpeg:dash:mpd-as-linking:2015\"."* §4.7.2's conclusion holds; its
argument is one sentence short of covering the case a reader is likeliest to
raise.

**Table I.4 carries two request-type tokens the specification does not
weigh.** `mpdlink` — *"all requests for MPDs referenced from linked
Periods"* — and `callback` — *"all requests triggered by DASH callback
events, as defined in 5.10.4.5"*. Both touch traffic this specification
generates: sub-MPD fetches and tracking beacons. Neither is a conformance
problem; the second raises the open question below.

**The base specification's model for a non-DASH scheme identifier is
forwarding, and this specification's Player processes the event itself.**
DASH §5.10.1: *"For application specific events, a scheme identifier
identifies the application such that the DASH Client can forward the event
to the proper application."* Nothing normative follows from the difference —
DASH §8.1 NOTE 1 states *"as DASH Client operation is not specified
normatively in this document, it is also unspecified how a DASH Client
conforms to a particular profile"* — so C02 and C03 stand as Conforming, but
the base text does not describe the division of labour this specification
adopts.

## Non-conforming items detail

None. No construct was found to violate an explicit rule of the base
specification.

## Marginal items detail

### M1 — `urn:svta:dash:profile:sgai-overlay-list:2026` (C04)

**Ambiguity.** Two things about the profile URI are stated on grounds the
primary copy does not support.

First, the normative-references table in chapter 2 gives RFC 8141 as *"The
production the URNs this specification mints follow, as the base
specification requires of profile identifiers (DASH §8.1)."* DASH §8.1 scopes
that requirement to the base document's own identifiers and says the opposite
about external ones: *"Profile identifiers defined in this document are URNs
and shall conform to IETF RFC 8141. Externally defined profiles may use
profile identifiers that are URNs or URLs."* Following RFC 8141 is sound, but
the base specification does not oblige it here, and an implementer reading
the row will believe it does.

Second, DASH §8.1 recommends against the word: *"External organizations or
individuals may define restrictions, permissions and extensions by using this
profile mechanism. It is recommended that such external definitions be not
referred to as profiles, but as Interoperability Points."* The URI contains
the token `profile`, §5.2.2 calls the value a profile URI, and §4.7.8 —
which does raise the interoperability-point question — raises a different
one: whether to mint a URI that *explicitly includes* the extension
namespace, not whether the URI already minted is named against a
recommendation.

**Suggested fix.** Reword the RFC 8141 row to state that the specification
elects RFC 8141 for its own identifiers, citing §8.1's permission rather than
a requirement. In §4.7.8 or §2.1, note in one sentence that §8.1 recommends
the term Interoperability Point for an externally defined identifier, and
state whether the existing URI is kept for compatibility or renamed. Renaming
is a breaking change and the recommendation is a `should`-strength one, so
recording the choice is enough.

### M2 — `<ImportedMPD>` inside `<svta:RenderableAsset>` (C14)

**Ambiguity.** The element is admissible, but not for the reason §5.3.4
gives, and the reason it is admissible has a second reading under which it is
not.

`ImportedMPD` is declared **once** in the whole primary copy, locally inside
`PeriodType`: `<xs:element name="ImportedMPD" type="ImportedMpdType"
minOccurs="0" maxOccurs="1"/>`. There is no global declaration for it. A
control search confirms the instrument finds local declarations — 124
`<xs:element name=` occurrences overall — so the single hit is a fact about
the document and not about the search. Consequently a
`{urn:mpeg:dash:schema:mpd:2011}ImportedMPD` element anywhere other than as
a `Period` child is an element in the DASH namespace for which the schema
provides no declaration at that position. `[inferred]` — XSD lax-wildcard
semantics, which the primary copy does not state — a validator descending
into the SGAI subtree finds no global declaration and skips the element
rather than failing, so schema validation does not reject the document.

§5.3.4's ground is *"the namespace boundary is lexical, and DASH §5.3.2.6 does
not constrain the parent of `<ImportedMPD>`"*. That argues from the absence
of a prose constraint and does not reach either of the two clauses that
actually govern. DASH §5.2.1 contains both readings:

> *"The extension of the DASH XML schema (as provided in Annex B), in
> particular the addition of XML attributes or elements in the DASH
> namespace, is reserved to ISO/IEC."*

> *"The MPD shall be authored such that, after XML attributes or elements in
> the DASH namespace but not in the XML schema documented in Annex B are
> removed, the result is a valid XML document formatted according to that
> schema and that conforms to this document."*

The first sentence read strictly forbids putting an element in the DASH
namespace that the schema does not declare — which is what this placement
produces. The second sentence anticipates that such elements exist and
prescribes a removal test for them instead of forbidding them, and this
construct passes that test: removing it leaves the SGAI subtree intact and
valid, and removing the SGAI subtree by the next paragraph's rule takes it
along. The second reading is the more natural one and is the one that admits
the construct. The specification relies on neither.

The semantic half is also unaddressed. DASH §5.3.2.6.1 says *"Linked Periods
are indicated by the ImportedMPD element in a Period element"*, and the whole
processing model for the element (DASH §5.3.2.6.3) is written as combining the
imported MPD's content **into the Linked Period** — step 3 merges MPD-level
`@profiles` into `MPD@profiles` and moves MPD-level `SupplementalProperty`
elements to Period level. Outside a Period there is no Period to merge into,
so the specification is reusing the element's name, type and URL-in-text-
content convention while supplying its own processing. That is a legitimate
choice; it is not the one §5.3.4 describes.

**Suggested fix.** Replace §5.3.4's justification with the two DASH §5.2.1
removal paragraphs, state that `ImportedMPD` is declared only within
`PeriodType` and therefore carries no schema declaration at this position,
and state that the reference processing model of DASH §5.3.2.6.3 does not apply
because there is no Linked Period — this specification supplies the
resolution behaviour itself, in §4.6. Also drop or correct the sentence *"A
schema for `<svta:RenderableAsset>` admits the core-namespace `<ImportedMPD>`
as a first-class child."* `[inferred]` — a schema whose target namespace is
`urn:svta:dash:sgai:2026` cannot declare an element in the DASH namespace at
all; it can only admit one through a namespace wildcard, and under `lax` that
child is never validated against `ImportedMpdType`. "First-class child" is
not achievable, and an implementer building the SGAI schema will discover it.

### M3 — the callback `<EventStream>` inside `<svta:Candidate>` (C15)

**Ambiguity.** Same structure as M2, with one flat factual error on top.
`EventStream` is likewise declared once only, locally inside `PeriodType`:
`<xs:element name="EventStream" type="EventStreamType" minOccurs="0"
maxOccurs="unbounded"/>`. The placement is admissible under the removal-test
reading of DASH §5.2.1 and questionable under the reserved-to-ISO/IEC reading,
exactly as in M2.

The error is in §5.5.2's note, which states that *"Carrying it directly
inside `<svta:Candidate>` is admissible as foreign-namespace open content"*.
It is not foreign-namespace content. `<EventStream>` is in
`urn:mpeg:dash:schema:mpd:2011`, and every wildcard the specification relies
on is `namespace="##other"`, which excludes the target namespace by
definition. The note's operative half — that a validator scanning only
`<Period>` children misses this carrier — is correct and valuable; its stated
legal basis is wrong.

There is a second consequence the note does not draw. Because the element is
outside the schema at that position, `@schemeIdUri`'s `use="required"`, the
`xs:unsignedLong` typing of `Event@presentationTime` and `Event@id`, and the
`use="prohibited"` on `@messageData` are **not enforced by schema
validation** there, while the identical carrier inside a sub-MPD `<Period>`
is fully validated. §5.5.2 says the two positions *"are equivalent"*; for
presentation they are, for validation they are not.

**Suggested fix.** In §5.5.2, replace "foreign-namespace open content" with
the removal-test grounding of DASH §5.2.1, and add one sentence: the carrier
inside a `<Period>` is schema-validated and the one inside
`<svta:Candidate>` is not, so a Player validates the callback attributes
itself in the second position. Then the note's obligation on tooling has a
stated reason rather than only an instruction.

### M4 — the linear `ListMPD` (C22)

**Ambiguity.** DASH §8.14 defines the List profile as *"an extension of the
ISO-BMFF CMAF Profile (see subclause 8.12), with the following requirements
overriding the requirements of the latter subclause"*, and then lists five
rules. But §8.12 does not define one profile. It defines two: *"The DASH core
profile for CMAF Content is defined in subclause 8.12.5"* and *"The DASH
extended profile for CMAF Content is defined in subclause 8.12.6. This
profile is more permissive on timeline mapping and addresses cases for which
splicing of content from different sources need to happen."* Which of the two
a `ListMPD` extends is therefore not determined by the base text, and with it
the constraint set a `ListMPD` inherits beyond §8.14's five rules is not
determined either. This is a defect in the base specification, not in this
document; the consequence for this document is that §5.2.1 inherits an
unidentified constraint set and says nothing about it.

The observation is not academic for ad insertion: the extended profile is
described as the one addressing splicing from different sources, which is
what a break of third-party creatives is.

**Suggested fix.** In §5.2.1, state that §8.14 inherits from §8.12 without
naming which of its two profiles, name the extended profile of §8.12.6 as the
reading this specification assumes and why, and tag the assumption. One
sentence. It also belongs on the Open points list and is a good candidate for
a working-group question, since the base specification is the only place it
can be settled.

### M5 — the empty linear resolution document (C24)

**Ambiguity.** The zero-Period alternative is correctly excluded and the
quotation supporting it is exact. What is not established is the remaining
shape against the profile constraints the document declares. The empty
`ListMPD` is `<MPD profiles="urn:mpeg:dash:profile:list:2024" type="list"
…><Period id="no-fill" duration="PT0S"/></MPD>`, and §5.2.3 grounds it on
DASH §5.3.2.2 Table 4 — a general rule — while the document also declares a
profile whose inherited Period constraints reach it through M4's chain. DASH
§8.12.4.4 includes *"If the Subset element is not present, the Period
contains exactly one CMAF Presentation"*, which a Period carrying nothing
does not obviously satisfy. The constraints are conditional rather than
`shall`-strength prohibitions on emptiness, so this is an unresolved reading
and not a violation — and it cannot be resolved while M4 is open, since the
inherited set is unidentified.

The non-linear empty document is not affected: it declares only this
specification's own profile URI, whose constraint set this specification
defines, and §5.2.2.1's grounding on Table 4 is sufficient for it.

**Suggested fix.** Once M4 is settled, add one sentence to §5.2.3 stating
that the degenerate `ListMPD` Period is assessed against Table 4 and that the
inherited profile constraints of §8.12.4.4 are conditional on Adaptation Sets
being present, so an empty Period does not trip them. If M4 resolves the
other way, the alternative is for the empty linear resolution to reuse the
non-linear document shape, which declares only a profile this specification
governs.

## Open questions surfaced

**Whether `svta` is a URN namespace identifier registered under RFC 8141.**
Every URI this specification mints uses it. The primary copy states the
production a base-defined profile identifier follows but carries no registry;
the IANA URN-namespace registry is external and was not consulted for this
audit. `[inferred]` — nothing was verified either way. Searched: `RFC 8141`,
`URN`, `namespace identifier`, `IANA` in the primary copy; §8.1 and the
normative-references clause are the only places the production appears, and
neither registers anything.

**Which Table I.4 request type, if any, names a sub-MPD fetch issued from a
`<svta:RenderableAsset>`.** `mpdlink` is *"all requests for MPDs referenced
from linked Periods"*, and a video presentation option's `<ImportedMPD>` is
not in a Linked Period (M2). No other row reaches it, so a Publisher wanting
to parameterise those fetches has no token and this specification does not
say so. Searched the whole of Table I.4 and §I.3.6; the rows are
`segment`, `init`, `xlink`, `mpd`, `callback`, `chaining`, `fallback`, `sbd`,
`steering`, `mpdpatch`, `altmpd`, `mpdlink`, `<URN / tag URI>`, `*`.

**Whether Annex B's normative XSD agrees with the printed per-clause
snippets.** Annex B is a URL, not text: *"The schema of the MPD for this
document is provided at: https://standards.iso.org/iso-iec/23009/-1/ed-6/en
(DASH-MPD.xsd)."* §5.2.2 gives it precedence over the snippets. The two
findings that turn on a schema fact — M2 and M3, both resting on
`ImportedMPD` and `EventStream` having no global declaration — would change
if the XSD declared those elements globally. Fetching the XSD was not part of
this step and the file is not on disk.

## Summary

- Total constructs audited: 40
- Conforming: 35
- Marginal: 5
- Non-conforming: 0

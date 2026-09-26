[GROUNDED_BY=spec-only]

# Conformance assertions

Every RFC 2119 obligation in `context/`, normalised to one row per
testable assertion, for absorption into chapter 10 (Test cases). The
keywords MUST, MUST NOT, SHOULD, SHOULD NOT, MAY and OPTIONAL are used as
defined in RFC 2119.

**IDs.** Criteria of `context/03-requirements.md` reuse their `R<N>.<n>`
ID. A criterion imposing obligations that differ in actor, condition or
obligation is split into rows suffixed `a` / `b` / `c` (`R20.1a`…); the
suffix indexes one criterion and is not a new criterion. Obligations in
the same file outside a criteria block carry `DP03` (design principles)
or `P03` (requirement prose, Out of Scope). Other files: `IN01`
(`01-intro.md`), `A2` (`02-actors.md`), `UC04` (`04-use-cases.md`),
`I05` (`05-dash-linear-interfaces.md`), `N06`
(`06-naming-and-namespaces.md`), `B07`
(`07-backward-compat-checklist.md`), `D08`
(`08-dash-extension-rules.md`), `G99` (`99-glossary.md`).
`00-normative-base.md` carries no RFC 2119 keyword. IDs are stable
across rebuilds: `UC04.3` and `N06.13` are unused, because the sentences
they carried no longer hold a keyword or no longer exist.

**Actors.** Publisher, ADS, APS, Player (`../context/02-actors.md`),
`spec document` for document-level obligations, and `all` for an
assertion binding more than one runtime actor, with the actors named in
parentheses when the source names them.

**Coverage.** All 164 conformance criteria declared in
`context/03-requirements.md` are carried; they yield 245 rows. 51 rows
come from a criterion or sentence stated without an RFC 2119 keyword
and are tagged `[no RFC 2119 keyword]`: the source declares them as
conformance, so they stay testable, but no keyword is invented for them.

**Folded** (a sentence restating an obligation already carried by a row
of the same file): `03-requirements.md` requirement prose at `:124`,
`:128` (R1.1), `:207`, `:211` (R11.1, R11.3a), `:277` (R29.2), `:340`
(R4.2, R4.3), `:669`, `:671`, `:689`, `:690` (R5.2, R5.3a, R5.5,
R5.6a), `:743`, `:746`, `:748`, `:756` (R7.1–R7.3), `:1196` (R38.1a),
`:1267` (R19.1), `:1301`, `:1311` (R21.1a, R21.1b), `:1344` (R25.1a),
`:1871`, `:1873`, `:1878`, `:1880` (R6.1–R6.4), `:2001`, `:2003`
(R24.1a, R24.1b), `:2087` (R28.1); `:1725` restates P03.5; OOS-1 at
`:2195` restates R10.2. The R40 prose (`:1771`–`:1812`) and the R22
"Across families" paragraph restate R40.1–R40.6 without a keyword.
`04-use-cases.md:863` restates UC04.5; `:1204` restates UC04.9.
`05-dash-linear-interfaces.md:443` restates I05.4; `:476` restates
I05.5. `08-dash-extension-rules.md:209` restates D08.9.

**Excluded**: `03-requirements.md:50`, `:54`, `:59`, `:60` (DP-2 quoting
MUST / MUST NOT to illustrate a style, imposing nothing); `:1751` (a
permission to a future edition, binding nothing in this one); `:274`,
`:1298` (the R29 gist and the R21 heading, restated by R29.2 and
R21.1a).

| Assertion ID | Source | Actor | Condition | Obligation |
|--------------|--------|-------|-----------|------------|
| DP03.1 | context/03-requirements.md:24 | spec document | Given a construct being authored | MUST NOT carry information already determined by its own context — its element name and namespace, its parent construct, or another attribute on the same construct. |
| DP03.2 | context/03-requirements.md:30 | spec document | Given a construct justified only by a possible future relaxation | MUST NOT be introduced. |
| DP03.3 | context/03-requirements.md:33 | spec document | Given a construct whose only admissible value matches its default or is fixed by another rule | MUST NOT exist in the spec. |
| DP03.4 | context/03-requirements.md:40 | spec document | Given the same value or relationship appearing in several places in the spec or in a generated MPD | Exactly one declaration is canonical and the others MUST be derived from it at runtime, not duplicated in the markup; two declarations the base specification itself provides and reconciles by its own rule (e.g. a Linked Period's `@duration` and its Imported Period's `Period@duration`, §5.3.2.6.3 step 3)d)iii) are not a duplication, and the base rule is adopted (R1.5). |
| DP03.5 | context/03-requirements.md:66 | all | (unconditional) | Applying this specification MUST NEVER break primary-content playback; when an opportunity cannot be honoured, skip-and-continue is mandatory. |
| R1.1 | context/03-requirements.md:137 | spec document | Given any SGAI construct introduced by this proposal | MUST sit at an extension point where removing it, as a Player not implementing this spec does under the base rules for unrecognised elements and attributes (§5.2.1), leaves a valid `MPD` whose primary content plays uninterrupted. |
| R1.2a | context/03-requirements.md:142 | spec document | Given a new SGAI construct | MUST be expressed using an extension point enumerated in `08-dash-extension-rules.md`: foreign-namespace open content (§5.2.1, DR-2/DR-3), application-level Event Streams (§5.10), or vendor descriptor schemes (§5.8.4.8 / §5.8.4.9). |
| R1.2b | context/03-requirements.md:147 | spec document | Given a new SGAI construct | MUST NOT be introduced via `<ImportedMPD>` paths bound by the §5.3.2.6 / §8.15 / §7.3 / RFC 4337 chain (DR-1) or via inline AdaptationSet / Representation under a ListMPD-level Period (DR-5). |
| R1.2c | context/03-requirements.md:151 | spec document | Given a construct invoking Annex F (DR-4) | Admissible only when it requires DASH segment-delivery semantics for a non-ISO-BMFF format AND a new Interoperability Point URI is published. `[no RFC 2119 keyword]` |
| R1.3 | context/03-requirements.md:155 | spec document | (unconditional) | MUST NOT alter or override the semantics of any pre-existing MPEG-DASH 6th edition construct. |
| R1.4 | context/03-requirements.md:160 | Player | Given resolving or rendering an accepted ad fails at runtime (decode error, malformed candidate, mid-ad network loss) | MUST abort that ad and continue playing the primary content uninterrupted. |
| R1.5a | context/03-requirements.md:165 | spec document | Given a question for which the base specification already defines a behaviour, a default or a construct | The base answer takes precedence: the spec adopts it and cites it. `[no RFC 2119 keyword]` |
| R1.5b | context/03-requirements.md:169 | spec document | Given a question the base specification does not answer | The spec defines its own answer and declares it as an extension. `[no RFC 2119 keyword]` |
| R1.5c | context/03-requirements.md:170 | spec document | Given a decision that departs from the base answer | It is recorded as an exception with its reason. `[no RFC 2119 keyword]` |
| R2.1 | context/03-requirements.md:186 | Publisher | Given constraints applicable to an ad slot (max duration, opt-in policies, layout templates) | MUST declare them in the `MPD`; they are not inferred at runtime by the ADS, the APS or the Player. |
| R2.2a | context/03-requirements.md:189 | ADS | Given an ad request | MUST decide which ads to serve and output them as its decision document (typically VAST; not bound to it). |
| R2.2b | context/03-requirements.md:191 | APS | Given the ADS's decision document | MUST convert it into the resolution document carrying the ad candidates. |
| R2.2c | context/03-requirements.md:192 | all (ADS, APS) | Given a Publisher-declared constraint (e.g. slot cap) | No enforcement obligation is placed on them; enforcement is the Player's under R2.3. `[no RFC 2119 keyword]` |
| R2.3 | context/03-requirements.md:196 | Player | Given candidates in the resolution document | MUST validate them against the Publisher-declared constraints and render only those that satisfy them. |
| R2.4a | context/03-requirements.md:200 | spec document | Given a new mechanism | MUST be expressible within the four-actor contract. |
| R2.4b | context/03-requirements.md:202 | spec document | Given a mechanism that would require an actor to take on a responsibility outside its role | MUST be rejected or redesigned. |
| R11.1 | context/03-requirements.md:216 | spec document | Given the normative chapters | MUST NOT cite a specific VAST version as required. |
| R11.2 | context/03-requirements.md:217 | Player | (unconditional) | MUST be able to operate regardless of whether the ADS uses VAST; it reads only the APS's resolution document. |
| R11.3a | context/03-requirements.md:225 | spec document | Given a normative statement | MUST NOT require VAST. |
| R11.3b | context/03-requirements.md:226 | spec document | Given a normative statement describing an actor's behaviour | MUST NOT use terms that only a VAST deployment satisfies. |
| R11.3c | context/03-requirements.md:227 | spec document | Given a normative sentence naming VAST as the typical case | Permitted only where the same sentence states the actor is not bound to it. `[no RFC 2119 keyword]` |
| R11.3d | context/03-requirements.md:230 | spec document | Given VAST material beyond a named typical case (field mapping, message example, version) | MUST be in an annex or in a non-normative note explicitly flagged as illustrative. |
| R11.4 | context/03-requirements.md:232 | spec document | (unconditional) | MUST cover the ad behaviours a VAST-based ADS can express, so an APS fed by VAST can build a resolution document for each using only this spec's semantics. |
| R11.5 | context/03-requirements.md:238 | spec document | (unconditional) | An annex SHOULD carry an illustrative worked example of an APS building a resolution document from a VAST response. |
| R18.1 | context/03-requirements.md:262 | spec document | (unconditional) | Documents the MPD event URL pattern (Player-visible input, served by the APS) and the resolution document format (Player-visible output). `[no RFC 2119 keyword]` |
| R18.2a | context/03-requirements.md:266 | all (APS, ADS) | Given ad decisioning invocation between APS and ADS | The contract is established and maintained by those parties outside this specification. `[no RFC 2119 keyword]` |
| R18.2b | context/03-requirements.md:269 | all (Publisher, APS) | Given the event URL arrangement | Remains bilateral, except for the resolution-request parameters this spec defines (R29). `[no RFC 2119 keyword]` |
| R29.1 | context/03-requirements.md:288 | spec document | Given the reserved capability parameters | They are a set of inputs about the device, not conclusions about servable experiences; membership and syntax are fixed when the syntax is specified. `[no RFC 2119 keyword]` |
| R29.2 | context/03-requirements.md:295 | Player | Given the reserved parameters | Sending is OPTIONAL; the Player MAY send all, some, or none. |
| R29.3 | context/03-requirements.md:299 | Player | Given the Player has no value for a reserved parameter, or does not disclose it | MUST omit the parameter entirely rather than send it empty or with a placeholder. |
| R29.4 | context/03-requirements.md:303 | Player | Given a resolution-request parameter that is not a reserved name | MUST carry a vendor-specific prefix. |
| R29.5a | context/03-requirements.md:305 | APS | Given a resolution request lacking any reserved parameter | MUST tolerate the absence. |
| R29.5b | context/03-requirements.md:306 | APS | Given a resolution request carrying no reserved parameter at all | MUST be able to produce ad candidates. |
| R29.6 | context/03-requirements.md:309 | spec document | Given the device classes enumerated under R3.1 | The reserved set MUST be able to express the capability axes that distinguish them. |
| R29.7 | context/03-requirements.md:313 | spec document | Given a reserved parameter absent from the request | Its value is undetermined, not an assertion that the capability is lacking; how the APS resolves it is the APS's decision. `[no RFC 2119 keyword]` |
| R29.8 | context/03-requirements.md:320 | spec document | (unconditional) | R38.2 and R39.3 are the only exceptions to R29.2; every other reserved parameter remains optional. `[no RFC 2119 keyword]` |
| R4.1a | context/03-requirements.md:393 | Publisher | Given any overlay or pause slot defined in the `MPD` | MUST declare a maximum duration on it. |
| R4.1b | context/03-requirements.md:396 | Publisher | Given an inherited linear event | Its maximum is the base specification's `@maxDuration`, which the Publisher MAY omit (R4.8). |
| R4.2 | context/03-requirements.md:398 | Player | Given a slot whose cap bounds cumulative duration (non-linear families, linear insertion) | MUST stop rendering once the cumulative duration of accepted candidates would exceed the cap, even mid-ad. |
| R4.3 | context/03-requirements.md:401 | Player | Given any slot | MUST NOT extend it beyond what the cap bounds for its family (R4.6), regardless of ADS metadata or candidate count; an `@clip="false"` late end is not a violation. |
| R4.4 | context/03-requirements.md:408 | ADS | Given returned candidates whose cumulative duration exceeds the cap | A conformance check on the ADS MUST NOT fail solely on that ground. |
| R4.5 | context/03-requirements.md:413 | Player | Given an accepted candidate whose actual rendered length exceeds its declared duration | MUST enforce the cap against actual length ("trim during play"). |
| R4.6 | context/03-requirements.md:416 | Player | Given an inherited linear replacement slot | MUST honour clip semantics: unless the event declares otherwise, the presentation ends at the scheduled slot end and a late start shortens it. |
| R4.7 | context/03-requirements.md:421 | all (Publisher, Player) | Given a declared cap of zero | The opportunity does not fire (§5.16.5); it is not a very short slot. `[no RFC 2119 keyword]` |
| R4.8 | context/03-requirements.md:426 | spec document | Given an inherited linear event with no `@maxDuration` | R4.1 requires no cap on it; the base answer stands (R1.5): the absent maximum is infinity and the current presentation resumes only when the alternative presentation terminates (§5.16.5). `[no RFC 2119 keyword]` |
| R4.9a | context/03-requirements.md:443 | Player | Given a candidate duration (`xs:duration`) to compare against the cap (`EventStream@timescale` units) | MUST convert the candidate duration into the cap's timescale before comparing. |
| R4.9b | context/03-requirements.md:444 | Player | Given the converted candidate duration | MUST round it up to the next whole unit of the timescale. |
| R4.9c | context/03-requirements.md:446 | Player | Given a converted duration exactly equal to the cap | The candidate is admitted. `[no RFC 2119 keyword]` |
| R4.10a | context/03-requirements.md:450 | Player | Given an overlay or pause slot declaration carrying no maximum duration | MUST NOT present ads from that slot. |
| R4.10b | context/03-requirements.md:450 | Player | Given an overlay or pause slot declaration carrying no maximum duration | MUST continue with the primary content. |
| R4.10c | context/03-requirements.md:454 | Player | Given an inherited linear event carrying no maximum duration | Outside R4.10; the Player executes it with its base semantics (R4.8). `[no RFC 2119 keyword]` |
| R4.11a | context/03-requirements.md:467 | Player | Given any slot cap | MUST compute the cap on the presentation timeline. |
| R4.11b | context/03-requirements.md:469 | Player | Given an interval in which the presentation timeline does not advance (e.g. a form suspended under R17 during a pause) | MUST NOT accrue it against the cap; the form resumes with its remaining cap. |
| R31.1a | context/03-requirements.md:491 | Player | Given a viewer pause beginning inside a pause opportunity window | MUST request a resolution document. |
| R31.1b | context/03-requirements.md:493 | Player | Given a viewer pause beginning outside every pause opportunity window | MUST NOT request a resolution document. |
| R31.2 | context/03-requirements.md:496 | all (Publisher, Player) | Given a pause slot | The Publisher-declared cap MUST NOT be interpreted as bounding its duration. |
| R12.1a | context/03-requirements.md:592 | spec document | Given an ad-type or visual-placement value | MUST NOT accept a value outside the R12 enumeration (plus `custom`, R39). |
| R12.1b | context/03-requirements.md:593 | spec document | Given the accepted ad-type and placement values | MUST cite the IAB source for each. |
| R12.2a | context/03-requirements.md:595 | Publisher | Given a slot declaring allowed layouts | MUST use only `linear`, `overlay`, `overlay-corner`, `overlay-lower-third`, `squeezeback-l-shape-upper-left`, `squeezeback-l-shape-upper-right`, `squeezeback-double-box`, `squeezeback-double-box-background`, `pause-fullscreen`, `pause-partial` and the optional `custom` (R39); any other IAB value, and the bare `squeezeback` or `pause`, is not a token. |
| R12.2b | context/03-requirements.md:605 | Publisher | Given a slot declaring allowed layouts | Publisher-private layout names MUST NOT appear in the declaration. |
| R12.3 | context/03-requirements.md:608 | APS | Given a resolution document | MUST NOT emit form metadata for an ad type or placement outside the enumerated set. |
| R12.4 | context/03-requirements.md:612 | spec document | Given an enumerated layout | It implies the IAB CTV spatial bound for that layout by normative reference; no dimensional attribute is introduced on the slot. `[no RFC 2119 keyword]` |
| R15.1a | context/03-requirements.md:634 | spec document | Given any place where creative carrier types are discussed | MUST enumerate exactly the admissible set (video, image, HTML). |
| R15.1b | context/03-requirements.md:636 | spec document | Given annexes, examples or implementation notes | MUST NOT add new carrier types. |
| R15.2a | context/03-requirements.md:640 | APS | Given an ad candidate in the resolution document | MUST carry a creative whose mimeType falls under video, image or HTML. |
| R15.2b | context/03-requirements.md:640 | Publisher | Given a form declared by the Publisher | MUST carry a creative whose mimeType falls under video, image or HTML. |
| R15.3 | context/03-requirements.md:646 | Player | Given a candidate whose creative mimeType is outside the admissible set | MAY skip the candidate. |
| R5.1 | context/03-requirements.md:700 | APS | Given an ad candidate in the resolution document | MUST carry one or more renderable presentation options (form + layout) as an ordered list whose document order is the preference order. |
| R5.2 | context/03-requirements.md:707 | Player | Given an accepted candidate | MUST evaluate its options in document order and render the first whose form and layout the device can satisfy. |
| R5.3a | context/03-requirements.md:711 | Player | Given a candidate with no form renderable on the device | MUST skip it and fall through to the next candidate. |
| R5.3b | context/03-requirements.md:713 | Player | Given all candidates exhausted | MUST continue with the primary content. |
| R5.4 | context/03-requirements.md:715 | all (ADS, APS) | Given candidate production | This spec MUST NOT be read as obliging them to maintain a device-class matrix or per-Player capability view. |
| R5.5 | context/03-requirements.md:720 | APS | Given an ad candidate | MAY carry multiple presentation options, each pairing a form with an admissible layout, as a single ordered list. |
| R5.6a | context/03-requirements.md:724 | Player | Given presentation-option selection | MUST walk the options in document order checking each against device capabilities and the layouts the slot admits — the Publisher-declared allowed layouts, or its own family's when it declares none (R38.1) — and render the first satisfying both. |
| R5.6b | context/03-requirements.md:730 | Player | Given an option failing either check | MUST NOT render it; moves to the next option. |
| R5.7 | context/03-requirements.md:733 | Player | Given no option on a candidate satisfies R5.6 | MUST skip the candidate and fall through to the next (preserving R7 order) or, when exhausted, to primary content. |
| R7.1 | context/03-requirements.md:766 | Player | Given a resolution document with more than one candidate | MUST play the candidates in declared order, except those dropped under R7.2 / R7.3. |
| R7.2 | context/03-requirements.md:769 | Player | Given a candidate with no form renderable on the device | MAY drop it. |
| R7.3 | context/03-requirements.md:771 | Player | Given a candidate whose declared duration would push the cumulative slot duration past the cap | MAY drop it before playback. |
| R7.4 | context/03-requirements.md:774 | Player | Given the candidates remaining after R7.2 / R7.3 | MUST NOT re-order, deduplicate or otherwise rearrange them. |
| R7.5 | context/03-requirements.md:778 | Player | Given an accepted candidate whose actual rendered length exceeds the cap | MUST trim mid-rendering per R4. |
| R30.1 | context/03-requirements.md:835 | APS | Given an opportunity that resolved with no ads | MUST express it as a well-formed resolution document carrying no candidates, never as an error response or a bodyless response. |
| R30.2 | context/03-requirements.md:839 | Player | Given a resolution carrying no candidates | MUST NOT count it as an execution; an event with `@executeOnce="true"` remains executable. |
| R3.1 | context/03-requirements.md:866 | spec document | (unconditional) | MUST enumerate the supported device classes and, per class, the expected behaviour for each opportunity type covered by the use cases. |
| R3.2 | context/03-requirements.md:869 | Player | Given any supported device class and any opportunity type defined in the spec | MUST produce a defined behaviour (render, fall back, or skip). |
| R3.3 | context/03-requirements.md:873 | Player | Given an ad form (video, image, HTML) the device class cannot render | MUST NOT attempt to render it. |
| R16.1 | context/03-requirements.md:894 | Player | Given a viewer pause-to-play transition with a pause-ad rendered | MUST remove the pause-ad form within one rendering frame. |
| R16.2 | context/03-requirements.md:896 | Player | Given the same transition | MUST cease firing tracking beacons scheduled for the dismissed pause-ad. |
| R32.1a | context/03-requirements.md:933 | APS | Given a resolution document for a pause slot | MUST declare which of repeat, request-again or stop applies on exhaustion. |
| R32.1b | context/03-requirements.md:935 | Player | Given a pause-slot resolution document with no exhaustion declaration | MUST apply `stop`. |
| R32.2 | context/03-requirements.md:937 | Player | Given `request-again` and a re-request returning no candidates (R30) | MUST treat it as `stop` for the remainder of that pause. |
| R32.3 | context/03-requirements.md:940 | Player | Given the viewer resumes playback | MUST return to the primary content immediately, whether or not an ad is mid-presentation. |
| R32.4 | context/03-requirements.md:942 | spec document | Given a second resolution request within one pause | Whether it is the same or a new opportunity is out of scope. `[no RFC 2119 keyword]` |
| R34.1 | context/03-requirements.md:983 | Publisher | Given a pause opportunity window | MAY declare it once-per-session; without the declaration, every qualifying pause yields a pause ad. |
| R34.2a | context/03-requirements.md:988 | Player | Given a window declared once-per-session | MUST present at most one pause ad for that window for the session. |
| R34.2b | context/03-requirements.md:990 | Player | Given a later qualifying pause inside an already-consumed once-per-session window | MUST leave the primary content uninterrupted. |
| R34.3a | context/03-requirements.md:991 | Player | Given a once-per-session window | MUST treat it as consumed when a pause ad begins rendering, not when the pause occurs. |
| R34.3b | context/03-requirements.md:993 | Player | Given a pause that resolves to no renderable candidate | MUST leave the window available. |
| R34.4 | context/03-requirements.md:995 | spec document | (unconditional) | The capability is recorded as the pause-family counterpart of the base single-execution bound. `[no RFC 2119 keyword]` |
| R35.1a | context/03-requirements.md:1036 | APS | Given each slot it resolves | MUST declare whether the viewer may dismiss it. |
| R35.1b | context/03-requirements.md:1037 | Player | Given a resolution document with no dismissal declaration | The slot is non-dismissible. `[no RFC 2119 keyword]` |
| R35.2a | context/03-requirements.md:1040 | APS | Given dismissal is allowed | MUST declare the seconds that MUST elapse, from the moment the slot begins rendering, before the viewer may dismiss. |
| R35.2b | context/03-requirements.md:1042 | Player | Given a declared dismissal delay of zero | The slot is dismissible immediately. `[no RFC 2119 keyword]` |
| R35.3a | context/03-requirements.md:1044 | Player | Given the declared delay has not elapsed | MUST NOT offer the viewer a way to dismiss the slot. |
| R35.3b | context/03-requirements.md:1046 | Player | Given the declared delay has elapsed | MUST make dismissal available for as long as the slot is on screen. |
| R35.4a | context/03-requirements.md:1049 | Player | Given a viewer dismissal | MUST stop presenting every ad of that slot. |
| R35.4b | context/03-requirements.md:1049 | Player | Given a viewer dismissal | MUST NOT advance to another ad or another form within the slot. |
| R35.5 | context/03-requirements.md:1053 | Player | Given a dismissed slot that bounded a region of the primary timeline | MUST continue from where the primary content stands, without compressing or skipping any part. |
| R35.6a | context/03-requirements.md:1055 | Player | Given a dismissal | MUST fire the tracking events scheduled up to the moment of dismissal. |
| R35.6b | context/03-requirements.md:1057 | Player | Given tracking events scheduled after the dismissal | MUST NOT fire them. |
| R35.7 | context/03-requirements.md:1059 | spec document | (unconditional) | How dismissal is offered (control, gesture, remote button) is out of scope. `[no RFC 2119 keyword]` |
| R35.8a | context/03-requirements.md:1065 | Player | Given a linear slot whose event carries the base specification's own skip declaration | MUST honour that declaration as the base specification defines it; it governs the slot. |
| R35.8b | context/03-requirements.md:1066 | Player | Given a linear slot where neither the event nor the resolution document declares dismissal | R35.1's default (non-dismissible) applies, and only then. `[no RFC 2119 keyword]` |
| R36.1a | context/03-requirements.md:1126 | Publisher | Given an overlay or pause opportunity window | MAY declare how far ahead of it a Player may resolve. |
| R36.1b | context/03-requirements.md:1126 | Player | Given an overlay or pause window that declares no offset | It may be resolved up to 60 seconds ahead of the window start, the base specification's default. `[no RFC 2119 keyword]` |
| R36.1c | context/03-requirements.md:1128 | Publisher | Given a window the Publisher wants resolved only when it fires | It declares an offset of zero. `[no RFC 2119 keyword]` |
| R36.2 | context/03-requirements.md:1132 | Player | Given an overlay window | MUST NOT resolve earlier than the offset — declared, or the 60-second default of R36.1 — before the window start. |
| R36.3 | context/03-requirements.md:1135 | Player | Given a pause opportunity window | MUST NOT resolve earlier than the offset — declared, or the 60-second default of R36.1 — before the window start; the offset is computed against the window start, never the pause. |
| R36.4a | context/03-requirements.md:1141 | APS | Given a resolution that may have been obtained ahead of the opportunity | MUST declare how long it remains usable. |
| R36.4b | context/03-requirements.md:1140 | Player | Given a resolution document with no usability declaration | It remains usable for as long as its window lasts. `[no RFC 2119 keyword]` |
| R36.5a | context/03-requirements.md:1144 | Player | Given the opportunity fires with a held resolution | MUST check whether that resolution is still usable. |
| R36.5b | context/03-requirements.md:1144 | Player | Given the held resolution is no longer usable | MUST request a new one. |
| R36.5c | context/03-requirements.md:1144 | Player | Given an expired resolution | MUST NOT present candidates from it. |
| R36.6a | context/03-requirements.md:1149 | Player | Given a re-resolution yielding no usable candidate | MUST treat it as an empty resolution (R30). |
| R36.6b | context/03-requirements.md:1149 | Player | Given a re-resolution yielding no usable candidate | MUST NOT fall back on the expired resolution. |
| R36.7 | context/03-requirements.md:1151 | spec document | (unconditional) | Resolving early is a permission, never an obligation; a Player resolving only on firing is conformant whatever offset the window carries. `[no RFC 2119 keyword]` |
| R37.1 | context/03-requirements.md:1180 | Player | Given a pause | MAY implement it by any mechanism that suspends the primary content and resumes it from the suspended position, including releasing its decoding resources. |
| R37.2 | context/03-requirements.md:1184 | Player | Given resume from a pause | MUST continue the primary content from the position at which it was suspended. |
| R37.3 | context/03-requirements.md:1188 | spec document | (unconditional) | No requirement is stated on how a Player implements a pause; criteria appearing to assume one are read per R37. `[no RFC 2119 keyword]` |
| R38.1a | context/03-requirements.md:1204 | Publisher | Given a non-linear slot | Declaring allowed layouts is OPTIONAL. |
| R38.1b | context/03-requirements.md:1203 | all (APS, Player) | Given a non-linear slot declaring no allowed layouts | It admits only the R12 tokens of its own family — overlay slot: the Overlay and Squeezeback entries; pause slot: the Pause-ad entry — no token of another family (an overlay slot does not admit `linear`), and not `custom`, which is admitted only by listing it (R39.2). `[no RFC 2119 keyword]` |
| R38.2a | context/03-requirements.md:1212 | Player | Given a slot declaring allowed layouts | MUST send the declared set, unchanged, on the resolution request to the APS. |
| R38.2b | context/03-requirements.md:1211 | Player | Given a slot declaring no allowed layouts | Nothing is sent; the set binding the APS and the Player is the one R38.1b admits. `[no RFC 2119 keyword]` |
| R38.3 | context/03-requirements.md:1215 | spec document | (unconditional) | The carriage of the set is normative and defined by this spec as a reserved R29 parameter. `[no RFC 2119 keyword]` |
| R38.4 | context/03-requirements.md:1218 | APS | Given a resolution request for a non-linear slot | MUST NOT return an option whose layout is outside the set it received or, when it received none, outside the set R38.1b admits for the slot's family. |
| R38.5a | context/03-requirements.md:1221 | Player | Given a selected option, before rendering | MUST check that it uses a layout the slot admits — the declared set, or the one R38.1b admits when none is declared. |
| R38.5b | context/03-requirements.md:1224 | Player | Given a selected option whose layout the slot does not admit | MUST NOT render it, even though the set was forwarded. |
| R38.6 | context/03-requirements.md:1226 | spec document | Given linear slots (`InsertPresentation`, `ReplacePresentation`) | Outside R38. `[no RFC 2119 keyword]` |
| R39.1 | context/03-requirements.md:1239 | spec document | (unconditional) | Supporting `custom` is OPTIONAL for every actor; it applies only to non-linear overlay slots and is the sole exception to R12.1, R10.2 and R10.3. |
| R39.2a | context/03-requirements.md:1244 | Publisher | Given a slot admitting `custom` | Lists `custom` in `@allowedLayouts`. `[no RFC 2119 keyword]` |
| R39.2b | context/03-requirements.md:1245 | Publisher | Given a slot admitting `custom` | MAY declare a custom region (x, y, width, height in percent of the video viewport, origin top-left); absent, the region is the whole viewport. |
| R39.3 | context/03-requirements.md:1251 | Player | Given a slot declaring a custom region | MUST send it on the resolution request together with the allowed layouts, carried as R38.3 defines. |
| R39.4a | context/03-requirements.md:1253 | APS | Given an option with layout `custom` | MUST carry the overlay's rectangle in the same percent units. |
| R39.4b | context/03-requirements.md:1254 | APS | Given a `custom` option's rectangle | MUST lie entirely inside the region received; MUST NOT extend beyond it. |
| R39.4c | context/03-requirements.md:1253 | APS | Given a `custom` option's rectangle | MAY be smaller than the region. |
| R39.5a | context/03-requirements.md:1258 | Player | Given a `custom` option, before rendering | MUST check its rectangle lies inside the slot's region (or the viewport when none is declared). |
| R39.5b | context/03-requirements.md:1258 | Player | Given a `custom` rectangle outside the region | MUST NOT render it; the option is not renderable and the Player moves to the next (R5.6). |
| R39.5c | context/03-requirements.md:1259 | Player | Given a Player that does not support `custom` | Treats every `custom` option as not renderable. `[no RFC 2119 keyword]` |
| R19.1 | context/03-requirements.md:1280 | Player | Given any ad form, linear or non-linear | MUST render it at the primary content's playback speed at the moment it is presented. |
| R19.2 | context/03-requirements.md:1283 | Player | Given primary content playing at a speed other than 1x | MUST NOT force the ad to 1x. |
| R19.3a | context/03-requirements.md:1286 | Player | Given an ad form's declared duration | MUST compute its wall-clock on-screen duration as `duration / playback_speed`. |
| R19.3b | context/03-requirements.md:1287 | Player | Given cap enforcement (R4) and beacon scheduling (R13) | Operate on the presentation-timeline `duration`, not the wall-clock value. `[no RFC 2119 keyword]` |
| R19.4 | context/03-requirements.md:1294 | Player | Given a form with no intrinsic media (`image`, `html`) | MUST derive its wall-clock length as `duration / playback_speed`. |
| R21.1a | context/03-requirements.md:1330 | Player | Given a pause-ad form | MAY present it fullscreen or as a partial overlay over the paused frame. |
| R21.1b | context/03-requirements.md:1333 | Player | Given a fullscreen pause-ad | MAY release resources held by the primary content and any pre-existing overlay. |
| R21.1c | context/03-requirements.md:1336 | Player | Given a partial-overlay pause-ad | MUST keep at most one non-linear ad form active during the pause; any coexisting overlay is suspended (R17). |
| R25.1a | context/03-requirements.md:1362 | Player | Given live content and the viewer paused inside a pause-ad window | MUST keep presentation time frozen inside that window for the whole pause, regardless of the live edge. |
| R25.1b | context/03-requirements.md:1365 | Player | Given a decision to resume at the live edge | MUST treat it as a Player action after the resume, outside the pause-ad window. |
| R26.1 | context/03-requirements.md:1391 | all (APS, Publisher) | Given a side-by-side / double-box background element | MUST be carried as a composition attribute of the slot / layout, not as a presentation option. |
| R26.2a | context/03-requirements.md:1393 | Player | Given a side-by-side / double-box layout | MUST composite the primary content and the ad as its two boxes. |
| R26.2b | context/03-requirements.md:1393 | Player | Given an advertiser-supplied background element | MUST place it in the uncovered bands. |
| R26.2c | context/03-requirements.md:1394 | Player | Given no background element supplied | The uncovered region renders as black. `[no RFC 2119 keyword]` |
| R26.3a | context/03-requirements.md:1407 | Player | Given a side-by-side whose ad is video | MUST NOT select it on a single-decoder device. |
| R26.3b | context/03-requirements.md:1413 | Player | Given a non-video element (image/HTML ad, or image background) | MUST NOT select it on a device that cannot composite that surface type on top of video. |
| R27.1 | context/03-requirements.md:1447 | all (APS, Publisher) | Given an L-shape / squeezeback presentation option | MUST carry exactly one ad creative — the full-frame background — as image, video or HTML. |
| R27.2 | context/03-requirements.md:1451 | Player | Given an L-shape option | MUST composite the creative full-frame in the background and the shrunk primary content on top, scaled into the region its `@layout` token denotes. |
| R27.3a | context/03-requirements.md:1459 | Player | Given an L-shape whose full-frame creative is video | Not satisfiable on a single-decoder device. `[no RFC 2119 keyword]` |
| R27.3b | context/03-requirements.md:1467 | Player | Given an L-shape whose full-frame creative is image or HTML | MUST NOT select it on a device that cannot composite that surface type together with video. |
| R14.1 | context/03-requirements.md:1510 | Player | Given a non-linear slot's resolution document declaring more than one candidate | MUST present them in sequence in document order, each starting when the previous ends. |
| R14.2 | context/03-requirements.md:1514 | Player | Given a sequence of non-linear candidates | MUST enforce the slot cap against their cumulative duration, trimming or dropping per R4 / R7. |
| R14.3 | context/03-requirements.md:1519 | spec document | (unconditional) | MUST NOT introduce a construct implying or requiring parallel rendering of two or more non-linear forms; no "render-then" primitive beyond candidate order. |
| R17.1a | context/03-requirements.md:1556 | Player | Given the viewer paused inside a pause-ad window AND an overlay active | MUST render the pause-ad form. |
| R17.1b | context/03-requirements.md:1556 | Player | Given the viewer paused inside a pause-ad window AND an overlay active | MUST suspend the overlay rendering. |
| R17.2a | context/03-requirements.md:1559 | Player | Given resume from pause | MUST dismiss the pause-ad (R16). |
| R17.2b | context/03-requirements.md:1559 | Player | Given resume from pause with the overlay slot window still active | MUST restore the overlay rendering. |
| R17.3 | context/03-requirements.md:1562 | Player | Given the overlay slot window expired during the pause | MUST keep the overlay surface clear on resume. |
| R17.4 | context/03-requirements.md:1564 | spec document | (unconditional) | Carries no construct letting the Publisher, the ADS or the APS invert the pause-over-overlay priority. `[no RFC 2119 keyword]` |
| R17.5a | context/03-requirements.md:1569 | Player | Given a viewer pause beginning inside a pause window while a linear ad occupies the screen | MUST present the pause ad. |
| R17.5b | context/03-requirements.md:1569 | Player | Given the same situation | MUST suspend the linear ad. |
| R17.5c | context/03-requirements.md:1570 | Player | Given the viewer resumes after R17.5b | MUST resume the linear ad from where it was suspended. |
| R20.1a | context/03-requirements.md:1618 | Player | Given same-family windows overlapping in time within the primary `MPD` | MUST select the first overlapping window (R20.3) and attempt to resolve it. |
| R20.1b | context/03-requirements.md:1621 | Player | Given an attempt on a window that produced no ad (failed execution) | MUST attempt the next overlapping window of the same family (§5.16.2.2.5 step 2). |
| R20.1c | context/03-requirements.md:1630 | Player | Given no response or transport failure, a final HTTP status other than `200`, a `200` body that is not a parseable resolution document, or a well-formed resolution document carrying no candidates | MUST treat all four alike as a failed execution. |
| R20.1d | context/03-requirements.md:1644 | Player | Given every overlapping window of the family attempted with none producing an ad | MUST continue with the primary content uninterrupted. |
| R20.1e | context/03-requirements.md:1656 | Player | Given a resolution document that carries candidates, none renderable on the device | Not a failed execution; handled by R5.3 / R5.7, ending at primary content, not at the next window. `[no RFC 2119 keyword]` |
| R20.2 | context/03-requirements.md:1666 | Publisher | Given windows of one family sharing a `Period` | MUST author them as `<Event>` entries inside a single `<EventStream>`. |
| R20.3a | context/03-requirements.md:1672 | Player | Given overlapping windows of one family | MUST order them by presentation time, oldest first. |
| R20.3b | context/03-requirements.md:1672 | Player | Given two overlapping windows with the same presentation time | MUST take them in their order inside the `EventStream`. |
| R20.4a | context/03-requirements.md:1695 | Player | Given a resolution document whose family does not match the requesting slot | MUST treat it as a failed execution and continue down the R20.1 chain to the next overlapping window of the slot's family. |
| R20.4b | context/03-requirements.md:1695 | Player | Given a resolution document whose family does not match the requesting slot | MUST NOT present any of its candidates in the slot. |
| R20.5 | context/03-requirements.md:1707 | Player | Given a window in a fallback chain serving candidates | MUST bind them with that window's own allowed layouts and maximum duration, not those of the window it stands in for. |
| R20.6 | context/03-requirements.md:1714 | spec document | (unconditional) | R20.5 MUST be carried as a normative Player obligation, not only in informative material. |
| R22.1 | context/03-requirements.md:1756 | Player | At any instant `t` | MUST keep at most one non-linear ad form active on screen; MUST NOT present two or more simultaneously. |
| R40.1a | context/03-requirements.md:1816 | Publisher | Given a non-linear window | Declaring a relation (supersede or on top) on it is OPTIONAL. |
| R40.1b | context/03-requirements.md:1816 | Publisher | Given a non-linear window declaring a relation | It declares at most one relation, supersede or on top. `[no RFC 2119 keyword]` |
| R40.1c | context/03-requirements.md:1817 | all (Publisher, Player) | Given a non-linear window declaring neither relation | It has the default relation (R40.4). `[no RFC 2119 keyword]` |
| R40.2 | context/03-requirements.md:1819 | Publisher | Given the Publisher wants a non-linear ad presented during an alternative presentation | MUST declare it either by a window in that alternative presentation's own `MPD`, or by a window of the triggering presentation that declares on top. |
| R40.3a | context/03-requirements.md:1823 | Player | Given a window declaring supersede | MUST present the window. |
| R40.3b | context/03-requirements.md:1823 | Player | Given a window declaring supersede | MUST NOT execute the inherited linear events whose presentation time falls within its span. |
| R40.3c | context/03-requirements.md:1827 | Player | Given a window declaring supersede that presents no ad (every resolution attempt a failed execution under R20.1, or no candidate renderable on the device, R5) | MUST execute those inherited linear events as the base specification defines, including its rules for an execution starting after an event's presentation time. |
| R40.4a | context/03-requirements.md:1831 | Player | Given a window declaring no relation | MUST present its forms only while the content of the presentation whose `MPD` declares the window is being output. |
| R40.4b | context/03-requirements.md:1832 | Player | Given a window declaring no relation | MUST execute every inherited linear event it overlaps with its base semantics. |
| R40.4c | context/03-requirements.md:1834 | Player | Given a window declaring no relation with a form on screen when an alternative presentation begins | The form ends there and the window presents nothing further. `[no RFC 2119 keyword]` |
| R40.5a | context/03-requirements.md:1836 | Player | Given a window declaring on top and an alternative presentation that starts within its span is active | MUST present the window also during it, composited over that presentation, within the device's capability (R3, R5) and R22. |
| R40.5b | context/03-requirements.md:1839 | Player | Given a window declaring on top | The inherited linear event it overlaps executes with its base semantics. `[no RFC 2119 keyword]` |
| R40.6 | context/03-requirements.md:1841 | Player | Given non-linear windows declared in an alternative presentation's `MPD` | MUST process them as that presentation's own: presented over its content, with R40.3–R40.5 applied against the alternative presentations it triggers in turn. |
| R40.7a | context/03-requirements.md:1846 | spec document | Given the R40 relation | It is declared on the non-linear window this spec defines; its carrier is decided under `06-naming-and-namespaces.md`. `[no RFC 2119 keyword]` |
| R40.7b | context/03-requirements.md:1848 | spec document | Given the R40 relation | MUST NOT add anything to the inherited linear events (or their `EventStream`s) to carry it. |
| R40.8 | context/03-requirements.md:1852 | spec document | (unconditional) | R40.3 is recorded as an exception to R1.5, with its reason (Publisher-declared departure on an SGAI construct; a non-implementing Player executes the base event unchanged). `[no RFC 2119 keyword]` |
| R6.1 | context/03-requirements.md:1892 | spec document | (unconditional) | MUST specify how in-band ad tracking beacons are carried in the resolution document. |
| R6.2 | context/03-requirements.md:1894 | APS | Given tracking beacons in the resolution document | SHOULD carry them as `<Event>` entries in an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015` in the ad `MPD` or sub-`MPD`. |
| R6.3 | context/03-requirements.md:1899 | spec document | Given the callback scheme cannot express the required semantics | A new tracking carrier MAY be introduced only after a documented gap analysis per R9. |
| R6.4 | context/03-requirements.md:1903 | Player | Given unknown namespaces on tracking-related extension elements | MUST safely ignore them. |
| R6.5a | context/03-requirements.md:1906 | all (APS, Player) | Given beacons within one candidate sharing an `@id`, or the same URL at the same presentation time | They fire once; the de-duplication key is scoped to the candidate. `[no RFC 2119 keyword]` |
| R6.5b | context/03-requirements.md:1911 | Player | Given two beacons with the same `@id` in two different candidates of one resolution document | MUST fire both. |
| R6.5c | context/03-requirements.md:1911 | Player | Given beacons carried as `Event`s of a `ListMPD`, including streams merged from its sub-MPDs | The base scope applies (R1.5): `Event@id` is scoped to its `@schemeIdUri` / `@value` pair over the whole media presentation (Table 44), so the ads of one `ListMPD` share one de-duplication scope. `[no RFC 2119 keyword]` |
| R6.6 | context/03-requirements.md:1919 | Player | Given a beacon `<EventStream>` hosted as foreign-namespace open content inside a candidate | MUST resolve its presentation times against that candidate's own presentation. |
| R6.7 | context/03-requirements.md:1922 | spec document | (unconditional) | MUST state how a resolution document carrying the candidate-level beacon carrier is validated. |
| R13.1 | context/03-requirements.md:1947 | APS | Given a resolution document carrying tracking instructions | MUST express them with DASH callback events (or an equivalent baseline construct), timed relative to the ad's presentation timeline. |
| R13.2 | context/03-requirements.md:1954 | Player | Given an ad accepted for rendering | MUST execute the tracking schedule read from the resolution document, firing each beacon at its relative time. |
| R13.3 | context/03-requirements.md:1959 | Player | Given R4 trims the ad before a scheduled beacon time | MUST stop firing remaining beacons at the trim boundary. |
| R13.4 | context/03-requirements.md:1961 | spec document | (unconditional) | MUST NOT introduce a new tracking event scheme; reuse of the baseline callback mechanism is mandatory. |
| R13.5 | context/03-requirements.md:1964 | all (APS, ADS) | Given the ADS-declared beacon schedule | Transcription fidelity is part of the APS-to-ADS contract, outside this spec. `[no RFC 2119 keyword]` |
| R23.1a | context/03-requirements.md:1990 | spec document | (unconditional) | MUST define, in the SVTA Ads WG namespace, extension elements carrying generic metadata with no native DASH carrier (`AdSystem`, `AdTitle`, etc.). |
| R23.1b | context/03-requirements.md:1993 | spec document | (unconditional) | MUST state that emitting and reading those elements are both optional. |
| R24.1a | context/03-requirements.md:2011 | APS | Given a non-AV ad form (`html`, `image`, …) in the resolution document | The asset URL MUST NOT be expressed as `@mimeType` on an AdaptationSet or Representation reached through any RFC 4337-bound path. |
| R24.1b | context/03-requirements.md:2015 | APS | Given a non-AV ad form in the resolution document | The asset URL MUST be carried via one of the DR-6 carriers (§5.2.1 / §5.10 / §5.8.4.x). |
| R33.1 | context/03-requirements.md:2063 | spec document | (unconditional) | MUST NOT define a metric of its own for pause-ad delivery. |
| R33.2a | context/03-requirements.md:2068 | Player | Given a Player that reports metrics | MUST derive the paused interval from the `PlayList` metric entries (Annex D.4.6). |
| R33.2b | context/03-requirements.md:2068 | Player | Given a playback period that stopped on `Rebuffering` | MUST NOT count it as a pause opportunity. |
| R33.3 | context/03-requirements.md:2072 | spec document | (unconditional) | Measurement transport to Publisher, APS or ADS is out of scope (§5.9.1). `[no RFC 2119 keyword]` |
| R33.4 | context/03-requirements.md:2076 | Publisher | Given content carrying pause opportunity windows | MUST request the `PlayList` metric through the `Metrics` element. |
| R28.1 | context/03-requirements.md:2105 | APS | Given an ad candidate carrying a ClickThrough | The ClickThrough URL and any accompanying click-tracking URLs MUST be carried in this spec's normative carrier and not elsewhere. |
| R28.2a | context/03-requirements.md:2112 | Player | Given the viewer activates the ClickThrough | MUST read the ClickThrough URL from the normative carrier. |
| R28.2b | context/03-requirements.md:2112 | Player | Given the viewer activates the ClickThrough | MUST fire the associated click-tracking. |
| R28.3 | context/03-requirements.md:2115 | all (APS, ADS) | Given an ADS-declared ClickThrough | Whether it reaches the resolution document is part of the APS-to-ADS contract, outside this spec. `[no RFC 2119 keyword]` |
| R8.1 | context/03-requirements.md:2140 | spec document | Given a new construct | MUST be accompanied by an inline justification of why no existing MPEG-DASH construct could be reused. |
| R8.2 | context/03-requirements.md:2144 | spec document | Given a deliberate omission of an existing construct a reader might expect reused | MUST be documented inline with the design decision. |
| R9.1 | context/03-requirements.md:2157 | spec document | (unconditional) | MUST reuse existing MPEG-DASH machinery (events, manifests, presentations, schemes) wherever possible. |
| R9.2 | context/03-requirements.md:2160 | spec document | Given a candidate new construct | MUST NOT be introduced unless an existing one cannot be made to fit. |
| R9.3a | context/03-requirements.md:2163 | spec document | Before introducing a new construct | MUST consider whether an extension to an existing construct would suffice. |
| R9.3b | context/03-requirements.md:2164 | spec document | Before introducing a new construct | MUST document the outcome of that consideration. |
| R10.1 | context/03-requirements.md:2178 | spec document | (unconditional) | MUST delegate the spatial arrangement of overlays to HTML5 / CSS layout primitives. |
| R10.2 | context/03-requirements.md:2180 | spec document | (unconditional) | MUST NOT define a parallel layout standard for overlay placement. |
| R10.3 | context/03-requirements.md:2182 | spec document | (unconditional) | Position semantics inside a layout are out of scope, except the `custom` rectangle (R39). `[no RFC 2119 keyword]` |
| P03.1 | context/03-requirements.md:210 | all | (unconditional) | Conformant implementations MUST be VAST-version-agnostic. |
| P03.2 | context/03-requirements.md:629 | APS | Given an HTML creative carried as `text/html` | MAY contain inline `<script>`, which runs under the device's HTML capability contract and is not a separate carrier. |
| P03.3 | context/03-requirements.md:1375 | APS | Given a side-by-side / double-box layout | An advertiser background element MAY fill the uncovered bands. |
| P03.4 | context/03-requirements.md:1438 | APS | Given an ad candidate | MAY list the L-shape among its ordered presentation options. |
| P03.5 | context/03-requirements.md:1481 | APS | Given a non-linear ad slot | MAY be filled by more than one candidate played in sequence. |
| P03.6 | context/03-requirements.md:1932 | spec document | (unconditional) | MUST define a tracking mechanism that lets the ADS instruct the Player which beacons to fire and at which points relative to the ad's presentation. |
| P03.7 | context/03-requirements.md:2211 | APS | Given a sender needing a scripted creative | MUST wrap the script in an HTML document and use `text/html`. |
| IN01.1 | context/01-intro.md:51 | spec document | Given each new construct the spec introduces | MUST apply the verification checklist of `07-backward-compat-checklist.md`. |
| A2.1 | context/02-actors.md:55 | ADS | Given its decision document | MAY emit a format other than VAST. |
| UC04.1 | context/04-use-cases.md:305 | APS | Given a candidate's presentation option | MAY be a partial-screen layout (L-shape / squeezeback or side-by-side / double-box). |
| UC04.2 | context/04-use-cases.md:642 | Player | Given a video pause-ad option while the single decoder holds the paused frame | MAY re-task the decoder by releasing the primary content and restoring it at the suspended position. |
| UC04.4 | context/04-use-cases.md:814 | Publisher | Given live content with an SGAI opportunity | SHOULD treat the opportunity as a loss on legacy Players. |
| UC04.5 | context/04-use-cases.md:816 | Publisher | Given non-live / VOD content with an SGAI opportunity | MAY author a standard linear break of baseline constructs over the same span as the SGAI window, declaring on the window that it supersedes the break (R40). |
| UC04.6 | context/04-use-cases.md:816 | Publisher | Given non-live / VOD content where monetising the opportunity matters | SHOULD author that standard linear break, with the supersede declaration. |
| UC04.7 | context/04-use-cases.md:855 | spec document | Given any new construct | MUST be expressible via extension points that make legacy Players skip it (UC-07 outcome). |
| UC04.8 | context/04-use-cases.md:877 | Player | Given a pause-ad form during a pause with a coexisting overlay | MAY present it fullscreen or as a partial overlay; either way it is the only ad surface visible. |
| UC04.9 | context/04-use-cases.md:1193 | APS | Given a side-by-side / double-box layout | An advertiser background element (still image only) MAY fill the uncovered region. |
| I05.1 | context/05-dash-linear-interfaces.md:43 | APS | Given an APS with a view of the device | MAY send a single form, the choice then sitting with it. |
| I05.2 | context/05-dash-linear-interfaces.md:392 | spec document | Given non-AV asset URLs (HTML, image, other) in the non-linear chapters | MUST carry them outside the AdaptationSet axis, via a DR-6 carrier. |
| I05.3 | context/05-dash-linear-interfaces.md:442 | Player | Given a Player conformant to this spec and a ClickThrough carrier | MUST read the ClickThrough carrier. |
| I05.4 | context/05-dash-linear-interfaces.md:442 | Player | Given R23 metadata (`AdSystem`, `AdTitle`, `Advertiser`) | MAY ignore it. |
| I05.5 | context/05-dash-linear-interfaces.md:444 | APS | Given a VAST `<UniversalAdId>` | MAY propagate it on a best-effort SVTA-namespaced attribute / element (R23); no carrier is mandated. |
| N06.1 | context/06-naming-and-namespaces.md:4 | spec document | Given any new construct | MUST follow the naming conventions of `06-naming-and-namespaces.md`. |
| N06.2 | context/06-naming-and-namespaces.md:22 | spec document | Given a new event scheme | MUST use the year-pinned pattern `urn:svta:dash:<construct>:<year>`. |
| N06.3 | context/06-naming-and-namespaces.md:37 | Player | Given a Player implementing edition N + 1 | SHOULD recognise both `:N:` and `:N+1:` URIs and treat them per that edition's backward-compatibility rules. |
| N06.4 | context/06-naming-and-namespaces.md:44 | Publisher | Given an `EventStream` carrying an SGAI scheme | MUST NOT carry `@value`. |
| N06.5 | context/06-naming-and-namespaces.md:44 | Player | Given an SGAI-scheme `EventStream` carrying `@value` | MUST ignore it. |
| N06.6 | context/06-naming-and-namespaces.md:58 | APS | Given tracking beacons for ads introduced by this spec | MUST reuse the baseline callback event scheme; no parallel `urn:svta:dash:*` tracking scheme. |
| N06.7 | context/06-naming-and-namespaces.md:65 | all | Given a Qualabs-private experimental extension outside this spec | MUST use the vendor namespace `urn:qualabs:<feature>:<year>`. |
| N06.8 | context/06-naming-and-namespaces.md:96 | spec document | Given a construct introduced by this spec | MUST honour the DR-3 authoring rule (baseline sibling vs wrapped). |
| N06.9 | context/06-naming-and-namespaces.md:103 | spec document | Given a new edition in which a construct's semantics change | MUST use a new `<year>` suffix on its scheme URI. |
| N06.10 | context/06-naming-and-namespaces.md:106 | spec document | Given a new edition in which a construct's semantics are unchanged | MAY keep its existing URI. |
| N06.11 | context/06-naming-and-namespaces.md:108 | spec document | Given the spec's chapter 2 (Normative references) | MUST list the URIs introduced by the current edition explicitly. |
| N06.12 | context/06-naming-and-namespaces.md:117 | spec document | Given overlay layout names | MUST reference the IAB-defined values without inventing new layout names. |
| N06.14 | context/06-naming-and-namespaces.md:157 | spec document | Given a component in essence the same as one in MPEG-DASH 6th edition | MUST reuse the baseline construct with all its characteristics (name, defaults, value domain, units, semantics). |
| B07.1 | context/07-backward-compat-checklist.md:5 | spec document | Given every new construct | MUST follow the per-construct backward-compatibility checklist. |
| B07.2 | context/07-backward-compat-checklist.md:13 | spec document | Given chapter 4 (Conformance) and chapter 10 (Test cases) | MUST apply the checklist's verification procedure. |
| B07.3 | context/07-backward-compat-checklist.md:17 | spec document | Given each new construct C | MUST answer the checklist questions explicitly in C's specification chapter. |
| B07.4 | context/07-backward-compat-checklist.md:19 | spec document | Given an unanswered checklist item | SHOULD block publication. |
| B07.5 | context/07-backward-compat-checklist.md:37 | spec document | Given a construct chapter | MUST name the applicable DR-N rule. |
| B07.6 | context/07-backward-compat-checklist.md:48 | spec document | Given a construct introducing a new namespace | MUST be in an extension namespace per `06-naming-and-namespaces.md`. |
| B07.7 | context/07-backward-compat-checklist.md:53 | spec document | Given a construct invoking Annex F (DR-4) | Its chapter MUST state the new Interoperability Point URI published in `MPD@profiles` and justify why DR-6 carriers are insufficient. |
| B07.8 | context/07-backward-compat-checklist.md:67 | spec document | Given a construct chapter | The legacy-Player walk-through MUST be present as an explicit prose paragraph. |
| B07.9 | context/07-backward-compat-checklist.md:79 | spec document | Given a document containing construct C | Removing C MUST leave a document that parses and plays. |
| B07.10 | context/07-backward-compat-checklist.md:84 | spec document | Given each new construct | MUST have a chapter-10 test case modelled on UC-07. |
| B07.11 | context/07-backward-compat-checklist.md:91 | Player | Given a legacy Player and construct C | MUST ignore C in every case. |
| B07.12 | context/07-backward-compat-checklist.md:99 | Publisher | Given non-live / VOD content containing C | MAY author a standard linear break of baseline constructs over the same span as C, declaring on C that it supersedes the break (R40). |
| B07.13 | context/07-backward-compat-checklist.md:129 | spec document | Given a construct chapter | MUST link to the checklist and confirm each item is satisfied. |
| B07.14 | context/07-backward-compat-checklist.md:130 | spec document | Given a construct chapter omitting the checklist confirmation | Reviewers SHOULD reject it. |
| B07.15 | context/07-backward-compat-checklist.md:156 | spec document | Given carrier classes (c1) and (c2) | MUST NOT be classified together. |
| B07.16 | context/07-backward-compat-checklist.md:162 | spec document | Given a construct fitting none of (a) / (b) / (c1) / (c2) | MUST justify invoking Annex F (DR-4) and name the Interoperability Point URI published. |
| B07.17 | context/07-backward-compat-checklist.md:164 | spec document | Given a construct chapter | MUST state the carrier classification explicitly. |
| B07.18 | context/07-backward-compat-checklist.md:169 | spec document | (unconditional) | SHOULD ship an audit table summarising checklist status for every new construct. |
| B07.19 | context/07-backward-compat-checklist.md:181 | spec document | Given the listed anti-patterns | Reviewers MUST flag them. |
| B07.20 | context/07-backward-compat-checklist.md:196 | APS | Given non-AV ad assets | MUST be carried via one of the DR-6 carriers. |
| D08.1 | context/08-dash-extension-rules.md:14 | spec document | Given an edition bump | `08-dash-extension-rules.md` MUST be re-validated section by section. |
| D08.2 | context/08-dash-extension-rules.md:25 | all (Publisher, APS) | Given a sub-MPD rooted in the SPS profile | MAY append a vendor profile URI in `@profiles`, still satisfying the SPS intersection. |
| D08.3 | context/08-dash-extension-rules.md:33 | APS | Given non-AV ad assets in a sub-MPD referenced via `<ImportedMPD>` | MUST be carried via one of the DR-6 carriers. |
| D08.4 | context/08-dash-extension-rules.md:41 | all (Publisher, APS) | Given any DASH container | A foreign-namespace element MAY appear as its child. |
| D08.5 | context/08-dash-extension-rules.md:44 | all (Publisher, APS) | Given an MPD carrying foreign-namespace content | MUST be authored so that, with foreign attributes and elements removed, it is still a valid DASH document. |
| D08.6 | context/08-dash-extension-rules.md:89 | spec document | Given a construct nesting a baseline element inside an SGAI element | MUST still satisfy §5.2.1 once the foreign-namespace parent is removed. |
| D08.7 | context/08-dash-extension-rules.md:134 | all (Publisher, APS) | Given an AdaptationSet `@profiles` | MUST be a subset of MPD-level `@profiles` (§5.3.7.2). |
| D08.8 | context/08-dash-extension-rules.md:190 | all (Publisher, APS) | Given a Period with non-zero duration | MUST contain at least one AdaptationSet (§5.3.2.2). |
| D08.9 | context/08-dash-extension-rules.md:196 | APS | Given a slot whose tracking needs presentation-time alignment across non-zero duration | MUST carry at least one AdaptationSet in that Period, or carry asset and tracking outside any non-zero-duration Period. |
| D08.10 | context/08-dash-extension-rules.md:254 | Player | Given the R28 ClickThrough carrier | MUST read it. |
| D08.11 | context/08-dash-extension-rules.md:254 | Player | Given R23 metadata | MAY ignore it. |
| D08.12 | context/08-dash-extension-rules.md:299 | spec document | Given a construct using either vendor descriptor element (§5.8.4.8 / §5.8.4.9) | MUST state which one it uses and why. |
| G99.1 | context/99-glossary.md:54 | Player | Given a reserved capability parameter | MAY attach it to the resolution request. |
| G99.2 | context/99-glossary.md:89 | ADS | Given its decision document | MAY emit a format other than VAST. |

## 1. Assertions per R

- R1: 9
- R2: 7
- R3: 3
- R4: 17
- R5: 9
- R6: 9
- R7: 5
- R8: 2
- R9: 4
- R10: 3
- R11: 8
- R12: 6
- R13: 5
- R14: 3
- R15: 5
- R16: 2
- R17: 9
- R18: 3
- R19: 5
- R20: 12
- R21: 3
- R22: 1
- R23: 2
- R24: 2
- R25: 2
- R26: 6
- R27: 4
- R28: 4
- R29: 9
- R30: 2
- R31: 3
- R32: 5
- R33: 5
- R34: 6
- R35: 14
- R36: 13
- R37: 3
- R38: 9
- R39: 10
- R40: 16

Total in R blocks: 245. Outside R blocks: DP03 5, P03 7, other files 62. Grand total: 319.

## 2. Assertions per actor

- Publisher: 22
- ADS: 4
- APS: 34
- Player: 142
- spec document: 96
- all: 21

## 3. Assertions per source doc

- `context/00-normative-base.md`: 0
- `context/01-intro.md`: 1
- `context/02-actors.md`: 1
- `context/03-requirements.md`: 257
- `context/04-use-cases.md`: 8
- `context/05-dash-linear-interfaces.md`: 5
- `context/06-naming-and-namespaces.md`: 13
- `context/07-backward-compat-checklist.md`: 20
- `context/08-dash-extension-rules.md`: 12
- `context/99-glossary.md`: 2

## 4. Orphan assertions

Assertions outside `context/03-requirements.md` with no requirement that
absorbs them cleanly.

| Assertion ID | Source | Summary | Absorb into |
|--------------|--------|---------|-------------|
| UC04.4 | context/04-use-cases.md:814 | On live content, the Publisher SHOULD treat an SGAI opportunity as a loss on legacy Players. | No R binds the Publisher on the legacy path; R1 would need a Publisher criterion for it. |
| UC04.5 | context/04-use-cases.md:816 | On VOD, the Publisher MAY author a baseline linear break over the SGAI window's span, declaring supersede on the window. | R40.1 / R40.3 carry the supersede declaration and its runtime effect, but no criterion states the Publisher's permission to author the fallback break itself; R40 would absorb it as a Publisher criterion. |
| UC04.6 | context/04-use-cases.md:816 | On VOD, where monetising matters, the Publisher SHOULD author that break. | Same R40 Publisher criterion as UC04.5. |
| B07.12 | context/07-backward-compat-checklist.md:99 | Restates UC04.5 for any construct C. | Same R40 Publisher criterion as UC04.5. |
| B07.11 | context/07-backward-compat-checklist.md:91 | The legacy Player MUST ignore C in every case. | R1.1 is now a property of the document (DR-8, ADR 0009) and binds no legacy Player; this sentence still puts the MUST on the Player. It is the observation of R1.1's test, and would be reworded as such rather than absorbed. |
| N06.1 | context/06-naming-and-namespaces.md:4 | New constructs MUST follow the naming conventions of `06`. | No R imposes the naming policy (R34, R35, R36, R40 only delegate to it); a governance R, or R9, would need to absorb it. |
| N06.2 | context/06-naming-and-namespaces.md:22 | New event schemes MUST use `urn:svta:dash:<construct>:<year>`. | Same governance gap as N06.1. |
| N06.3 | context/06-naming-and-namespaces.md:37 | An edition-N+1 Player SHOULD recognise both `:N:` and `:N+1:` URIs. | A runtime Player obligation with no R and no UC; implies a new cross-edition criterion, arguably under R1. |
| N06.4 | context/06-naming-and-namespaces.md:44 | An SGAI-scheme `EventStream` MUST NOT carry `@value`. | No R; closest is R20.2 (one `EventStream` per family per Period). |
| N06.5 | context/06-naming-and-namespaces.md:44 | A Player MUST ignore `@value` on an SGAI-scheme `EventStream`. | No R; same as N06.4. |
| N06.6 | context/06-naming-and-namespaces.md:58 | Tracking beacons MUST reuse the baseline callback scheme. | Maps to R13.4 by content, but the keyword conflicts with R6.2, which only says SHOULD for the same carrier. |
| N06.7 | context/06-naming-and-namespaces.md:65 | Qualabs-private extensions MUST use `urn:qualabs:<feature>:<year>`. | Binds extensions that are outside the spec; no R, and arguably outside the conformance set. |
| N06.9 | context/06-naming-and-namespaces.md:103 | Changed semantics in a new edition MUST get a new `<year>` URI. | Same governance gap as N06.1. |
| N06.10 | context/06-naming-and-namespaces.md:106 | Unchanged semantics MAY keep the URI. | Same governance gap as N06.1. |
| N06.11 | context/06-naming-and-namespaces.md:108 | Chapter 2 MUST list the edition's URIs. | Same governance gap as N06.1. |
| IN01.1 | context/01-intro.md:51 | The spec MUST apply the `07` checklist to each new construct. | No R requires the checklist; R1 (or R8) needs a documentation criterion. |
| B07.1 | context/07-backward-compat-checklist.md:5 | The spec MUST follow the checklist for every new construct. | Same as IN01.1. |
| B07.2 | context/07-backward-compat-checklist.md:13 | Chapters 4 and 10 MUST apply the checklist procedure. | Same as IN01.1. |
| B07.3 | context/07-backward-compat-checklist.md:17 | Each construct chapter MUST answer the checklist questions. | Same as IN01.1. |
| B07.5 | context/07-backward-compat-checklist.md:37 | Each construct chapter MUST name its DR-N rule. | Same as IN01.1; closest is R1.2a. |
| B07.7 | context/07-backward-compat-checklist.md:53 | An Annex F construct chapter MUST name its IOP URI and justify it. | Documentation half of R1.2c; R1.2c states admissibility, not what the chapter says. |
| B07.8 | context/07-backward-compat-checklist.md:67 | The legacy walk-through MUST be explicit prose. | Same as IN01.1. |
| B07.10 | context/07-backward-compat-checklist.md:84 | Each construct MUST have a UC-07-style test in chapter 10. | Same as IN01.1. |
| B07.13 | context/07-backward-compat-checklist.md:129 | Each construct chapter MUST link to the checklist and confirm each item. | Same as IN01.1. |
| B07.16 | context/07-backward-compat-checklist.md:162 | A construct outside (a)/(b)/(c1)/(c2) MUST justify Annex F. | Same as B07.7. |
| B07.4 | context/07-backward-compat-checklist.md:19 | Unanswered checklist items SHOULD block publication. | Binds a review process no R establishes; a governance R (extension of R8), or explicitly outside the conformance set. |
| B07.14 | context/07-backward-compat-checklist.md:130 | Reviewers SHOULD reject chapters missing the confirmation. | Same as B07.4. |
| B07.18 | context/07-backward-compat-checklist.md:169 | The spec SHOULD ship an aggregated audit table. | Same as B07.4. |
| B07.19 | context/07-backward-compat-checklist.md:181 | Reviewers MUST flag the listed anti-patterns. | Same as B07.4. |
| B07.15 | context/07-backward-compat-checklist.md:156 | (c1) and (c2) carriers MUST NOT be classified together. | R1.2a admits both vendor descriptor elements without distinguishing them; R1.2 needs a criterion requiring the distinction. |
| B07.17 | context/07-backward-compat-checklist.md:164 | The carrier classification MUST be explicit in the chapter. | Same as B07.15. |
| D08.12 | context/08-dash-extension-rules.md:299 | A construct using a vendor descriptor MUST state which element and why. | Same as B07.15. |
| D08.1 | context/08-dash-extension-rules.md:14 | `08` MUST be re-validated on an edition bump. | Governs maintenance of `context/`, not the spec; no R, and arguably outside the conformance set (enforced by `bin/check-normative-base.py`). |
| D08.8 | context/08-dash-extension-rules.md:190 | A non-zero-duration Period MUST contain an AdaptationSet. | No R cites DR-7 (R1.2b cites only DR-1 and DR-5); R1.2b or R6 should absorb it. |
| D08.9 | context/08-dash-extension-rules.md:196 | Tracking needing presentation-time alignment MUST share a Period with an AdaptationSet or sit outside non-zero-duration Periods. | Same as D08.8; constrains the R6 carrier for non-AV ads. |

These non-R assertions map cleanly and are not orphans: A2.1 → R2.2a;
UC04.1 → R5.5 / R27; UC04.2 → R37.1; UC04.7 → R1.1 / R1.2a;
UC04.8 → R21.1a / R17.1; UC04.9 → R26.2b; I05.1 → R5.1; I05.2 → R24.1b;
I05.3 → R28.2a; I05.4 → R23.1b; I05.5 → R23.1a; N06.8 → R1.2a; N06.12 →
R12.1a; N06.14 → R1.5a; B07.6 → R1.2a; B07.9 → R1.1; B07.20 → R24.1b;
D08.2 → R1.2b; D08.3 → R24.1b; D08.4 → R1.2a; D08.5 → R1.1 / R1.2a;
D08.6 → R1.2a; D08.7 → R1.2b / R24.1a; D08.10 → R28.2a; D08.11 →
R23.1b; G99.1 → R29.2; G99.2 → R2.2a.

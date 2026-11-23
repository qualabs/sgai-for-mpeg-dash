# T-05 — Classification of the 165 criteria of context/03

Generated from the catalogue (`bin/conformance/spec/catalog.py`) and `context/03-requirements.md`; the verdicts are the code's, this table only lists them. One row per rule; a criterion split into several rules has several rows. *Code* = a check that runs on the documents named; *NV* = NOT_VERIFIABLE with the reason the runner prints.

165 criteria, 196 rules: 48 with a check (on 34 criteria), 148 NOT_VERIFIABLE.

| holder | criteria | rules with a check | NOT_VERIFIABLE rules |
|---|---|---|---|
| spec document | 61 | 20 | 55 |
| Player | 57 | 1 | 56 |
| APS | 19 | 11 | 13 |
| Publisher | 13 | 11 | 7 |
| APS + Publisher | 3 | 4 | 3 |
| Publisher / spec document | 2 | 0 | 2 |
| ADS + APS | 2 | 0 | 2 |
| Publisher + Player | 2 | 0 | 4 |
| APS + ADS | 2 | 0 | 2 |
| Publisher / APS / ADS | 1 | 0 | 1 |
| ADS | 1 | 0 | 1 |
| Player + APS | 1 | 0 | 2 |
| APS / spec document | 1 | 1 | 0 |

| criterion | holder | rule | Code / NV | applies to | reason or what the check measures | Interfaces index |
|---|---|---|---|---|---|---|
| R1.1 | spec document | R1.1 | NV | spec | the document property (removing every extension leaves a valid MPD) is level 1, E-4; that the primary content keeps playing is level 3a |  |
| R1.2 | Publisher / spec document | R1.2 | NV | spec | that every construct hangs from an enumerated extension point is level 1 (E-3 and the DR rules of ADR 0049) |  |
| R1.3 | Publisher / spec document | R1.3 | NV | spec | whether a base construct's semantics were altered is a reading of the specification's prose against the base; a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R1.5 | spec document | R1.5 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R1.4 | Player | R1.4 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R1.6 | Player | R1.6 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R2.1 | Publisher | R2.1 | NV | spec | forbids inference at runtime by other actors; the declarations it requires on a document are checked by R4.1 and R12.2 |  |
| R2.2 | ADS + APS | R2.2 | NV | spec | what the ADS decides and how the APS converts it are processes, and the ADS's output is not a document this specification defines |  |
| R2.4 | spec document | R2.4 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R2.3 | Player | R2.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R11.1 | spec document | R11.1 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R11.3 | spec document | R11.3 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R11.4 | spec document | R11.4 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R11.5 | spec document | R11.5 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R11.2 | Player | R11.2 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R18.1 | spec document | R18.1 | NV | spec | the event URL is the window's @uri (typed by the schema, level 1); whether a request is sent to it is Player behaviour, and an example request is tied to its window only by prose, not by data the check can follow | I-REQ: Event URL the request is sent to |
| R18.2 | Publisher / APS / ADS | R18.2 | NV | spec | an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it |  |
| R29.1 | spec document | R29.1a | Code | request | R29.1: the reserved parameters are those of the two tables, and no others. (a `sgai-` name outside the two tables is not reserved, the set being closed) | I-REQ: Transport: query parameters, not the MPD URL-parameter template; I-REQ: `sgai-video-decoders`; I-REQ: `sgai-image-over-video`; I-REQ: `sgai-html-over-video`; I-REQ: `sgai-custom-layout`; I-REQ: `sgai-ad-audio`; I-REQ: `sgai-allowed-layouts`; I-REQ: `sgai-custom-region`; I-REQ: `sgai-ad-audio-allowed` |
| R29.1 | spec document | R29.1b | Code | request | (sgai-video-decoders takes 1, 2 or 3) | I-REQ: Transport: query parameters, not the MPD URL-parameter template; I-REQ: `sgai-video-decoders`; I-REQ: `sgai-image-over-video`; I-REQ: `sgai-html-over-video`; I-REQ: `sgai-custom-layout`; I-REQ: `sgai-ad-audio`; I-REQ: `sgai-allowed-layouts`; I-REQ: `sgai-custom-region`; I-REQ: `sgai-ad-audio-allowed` |
| R29.1 | spec document | R29.1c | Code | request | (sgai-image-over-video takes 1 or 0) | I-REQ: Transport: query parameters, not the MPD URL-parameter template; I-REQ: `sgai-video-decoders`; I-REQ: `sgai-image-over-video`; I-REQ: `sgai-html-over-video`; I-REQ: `sgai-custom-layout`; I-REQ: `sgai-ad-audio`; I-REQ: `sgai-allowed-layouts`; I-REQ: `sgai-custom-region`; I-REQ: `sgai-ad-audio-allowed` |
| R29.1 | spec document | R29.1d | Code | request | (sgai-html-over-video takes 1 or 0) | I-REQ: Transport: query parameters, not the MPD URL-parameter template; I-REQ: `sgai-video-decoders`; I-REQ: `sgai-image-over-video`; I-REQ: `sgai-html-over-video`; I-REQ: `sgai-custom-layout`; I-REQ: `sgai-ad-audio`; I-REQ: `sgai-allowed-layouts`; I-REQ: `sgai-custom-region`; I-REQ: `sgai-ad-audio-allowed` |
| R29.1 | spec document | R29.1e | Code | request | (sgai-custom-layout takes 1 or 0) | I-REQ: Transport: query parameters, not the MPD URL-parameter template; I-REQ: `sgai-video-decoders`; I-REQ: `sgai-image-over-video`; I-REQ: `sgai-html-over-video`; I-REQ: `sgai-custom-layout`; I-REQ: `sgai-ad-audio`; I-REQ: `sgai-allowed-layouts`; I-REQ: `sgai-custom-region`; I-REQ: `sgai-ad-audio-allowed` |
| R29.1 | spec document | R29.1f | Code | request | (sgai-ad-audio takes 1 or 0) | I-REQ: Transport: query parameters, not the MPD URL-parameter template; I-REQ: `sgai-video-decoders`; I-REQ: `sgai-image-over-video`; I-REQ: `sgai-html-over-video`; I-REQ: `sgai-custom-layout`; I-REQ: `sgai-ad-audio`; I-REQ: `sgai-allowed-layouts`; I-REQ: `sgai-custom-region`; I-REQ: `sgai-ad-audio-allowed` |
| R29.1 | spec document | R29.1g | Code | request | (sgai-allowed-layouts is a non-empty list of R12.2 tokens) | I-REQ: Transport: query parameters, not the MPD URL-parameter template; I-REQ: `sgai-video-decoders`; I-REQ: `sgai-image-over-video`; I-REQ: `sgai-html-over-video`; I-REQ: `sgai-custom-layout`; I-REQ: `sgai-ad-audio`; I-REQ: `sgai-allowed-layouts`; I-REQ: `sgai-custom-region`; I-REQ: `sgai-ad-audio-allowed` |
| R29.1 | spec document | R29.1h | Code | request | (sgai-custom-region is four percentages) | I-REQ: Transport: query parameters, not the MPD URL-parameter template; I-REQ: `sgai-video-decoders`; I-REQ: `sgai-image-over-video`; I-REQ: `sgai-html-over-video`; I-REQ: `sgai-custom-layout`; I-REQ: `sgai-ad-audio`; I-REQ: `sgai-allowed-layouts`; I-REQ: `sgai-custom-region`; I-REQ: `sgai-ad-audio-allowed` |
| R29.1 | spec document | R29.1i | Code | request | (sgai-ad-audio-allowed takes only 1) | I-REQ: Transport: query parameters, not the MPD URL-parameter template; I-REQ: `sgai-video-decoders`; I-REQ: `sgai-image-over-video`; I-REQ: `sgai-html-over-video`; I-REQ: `sgai-custom-layout`; I-REQ: `sgai-ad-audio`; I-REQ: `sgai-allowed-layouts`; I-REQ: `sgai-custom-region`; I-REQ: `sgai-ad-audio-allowed` |
| R29.1 | spec document | R29.1j | Code | mpd, sps-mpd, list-mpd | R29.1: the reserved parameters are not expressed through the MPD's URL-parameter template mechanism. (the transport: query parameters, never the MPD's URL-parameter template (DASH Annex I)) | I-REQ: Transport: query parameters, not the MPD URL-parameter template; I-REQ: `sgai-video-decoders`; I-REQ: `sgai-image-over-video`; I-REQ: `sgai-html-over-video`; I-REQ: `sgai-custom-layout`; I-REQ: `sgai-ad-audio`; I-REQ: `sgai-allowed-layouts`; I-REQ: `sgai-custom-region`; I-REQ: `sgai-ad-audio-allowed` |
| R29.2 | Player | R29.2 | NV | spec | Player behaviour: level 3 (reference-player). Whether a capability parameter is sent is the Player's choice, and a slot parameter is due only when the slot declares it, which needs the window the request was built from | I-REQ: Which parameters are optional |
| R29.3 | Player | R29.3 | Code | request | R29.3: a reserved parameter with no value is omitted, never sent empty. (held by the Player, but it states a property of the request, the document the Player writes (I-REQ)) | I-REQ: A parameter with no value is omitted |
| R29.4 | Player | R29.4 | NV | spec | Player behaviour: level 3 (reference-player). A request does not show which parameters the Player added and which came with the Publisher's event URL (R18.2), and only the first need the vendor prefix | I-REQ: Vendor prefix on a non-reserved parameter |
| R29.5 | APS | R29.5 | NV | spec | how an APS behaves on receiving a request without a parameter; no document records it |  |
| R29.7 | spec document | R29.7 | NV | spec | an absent capability parameter is legal; its meaning (undetermined) binds the APS's resolution, which no document records | I-REQ: An absent capability parameter |
| R29.10 | Player | R29.10 | NV | spec | Player behaviour: level 3 (reference-player). Whether a declared value is the device's real capability is a property of the device, not of the request | I-REQ: A capability value is the device's real capability in the session |
| R4.1 | Publisher | R4.1 | Code | mpd, sps-mpd | R4.1: every overlay and pause window declares its maximum duration. | I-MPD: Maximum duration of an overlay or pause slot |
| R4.4 | ADS | R4.4 | NV | spec | an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it; it limits what a conformance check on the ADS may fail |  |
| R4.6 | spec document | R4.6 | Code | mpd, sps-mpd | R4.6: `@clip` belongs to the inherited replacement; insertion has none, and neither does a window. (the document part: @clip exists only on the replacement; what the cap bounds at runtime is level 3) | I-MPD: `@clip` of an inherited linear replacement |
| R4.7 | Publisher + Player | R4.7a | NV | spec | a zero cap is a legal declaration (typed by the schema); what it means, not executing, binds the Player | I-MPD: A maximum duration of zero |
| R4.7 | Publisher + Player | R4.7b | NV | spec | Player behaviour: level 3 (reference-player) | I-MPD: A maximum duration of zero |
| R4.8 | spec document | R4.8 | NV | spec | @maxDuration on an inherited linear event is optional and typed by the base schema; no document can violate R4.8, which fixes how absence is read (level 3) | I-MPD: `@maxDuration` of an inherited linear event |
| R4.11 | spec document | R4.11 | NV | spec | the timeline the cap accrues on is a Player computation; the document carries only the cap and its timescale | I-MPD: Timeline the cap is measured on |
| R4.2 | Player | R4.2 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R4.5 | Player | R4.5 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R4.9 | Player | R4.9 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R4.10 | Player | R4.10 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R31.1 | spec document | R31.1 | Code | mpd, sps-mpd | (the window is a declared range of the primary timeline; the trigger itself is level 3) | I-MPD: Range of a pause window |
| R31.2 | Publisher + Player | R31.2a | NV | spec | the Publisher part forbids an interpretation, not a value: any declared cap on a pause window is legal | I-MPD: The cap on a pause slot |
| R31.2 | Publisher + Player | R31.2b | NV | spec | Player behaviour: level 3 (reference-player) | I-MPD: The cap on a pause slot |
| R12.1 | spec document | R12.1a | Code | spec | R12.1: the accepted values are exactly the enumerated ones. (the extension schema's layout-token enumeration against R12.2) |  |
| R12.1 | spec document | R12.1b | NV | spec | citing the IAB source for each accepted value is a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R12.2 | Publisher | R12.2 | Code | mpd, sps-mpd | R12.2: a window's allowed layouts are tokens of the closed list. | I-MPD: Layout token vocabulary |
| R12.3 | APS | R12.3 | Code | overlay-list | R12.3: no form metadata for a layout outside the enumerated set. | I-RES: An option's `@layout` and ad-type metadata |
| R12.4 | spec document | R12.4 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec; the bounds are the IAB's, inherited by reference |  |
| R12.5 | spec document | R12.5 | NV | spec | the composition a token denotes is what the Player builds on screen (level 3); the document carries only the token, checked by R12.2 and R12.3 | I-MPD: Composition each layout token denotes |
| R15.1 | spec document | R15.1 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R15.2 | APS + Publisher | R15.2a | Code | overlay-list | R15.2: a creative's mimeType falls under video, image or HTML. (video (video/*, application/dash+xml), image/* except SVG (OOS-4), text/html) | I-RES: Creative form and `mimeType` |
| R15.2 | APS + Publisher | R15.2b | NV | spec | the Publisher part: an MPD declares windows, not creatives, so no Publisher document carries a form's mimeType | I-RES: Creative form and `mimeType` |
| R15.3 | Player | R15.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R5.1 | APS | R5.1 | Code | overlay-list | R5.1: each candidate carries one or more presentation options. | I-RES: Presentation options of a candidate, and their order |
| R5.4 | ADS + APS | R5.4 | NV | spec | an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it; it fixes what the specification may not be read as requiring |  |
| R5.8 | spec document | R5.8 | NV | spec | what the options represent (the formats the advertiser allowed) is not visible in the document | I-RES: What the options represent |
| R5.3 | Player | R5.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R5.6 | Player | R5.6 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R5.9 | Player | R5.9 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R7.1 | spec document | R7.1 | NV | spec | any order of candidates is legal; it binds presentation, which is level 3 | I-RES: Order of the candidates |
| R30.1 | APS | R30.1 | NV | spec | that the empty resolution is a complete, well-formed document is the schema's (level 1); that it is not an error status or an empty body is a property of the HTTP response, which no example carries | I-RES: A document with no candidates |
| R30.2 | Player | R30.2 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R3.1 | spec document | R3.1 | NV | spec | the class is derived and never sent: a reserved-looking name for it fails R29.1a, and a vendor-named one cannot be recognised by code; giving each class its behaviour is a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec | I-REQ: Device class (derived from the parameters; does not travel) |
| R3.2 | Player | R3.2 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R16.1 | Player | R16.1 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R32.1 | APS | R32.1a | Code | overlay-list | (a pause document declares which behaviour applies) | I-RES: Behaviour when pause candidates are exhausted: declaration and default; I-RES: What `repeat`, `request-again` and `stop` mean |
| R32.1 | APS | R32.1b | NV | spec | what repeat, request-again and stop mean, and the default, bind the Player (level 3) | I-RES: Behaviour when pause candidates are exhausted: declaration and default; I-RES: What `repeat`, `request-again` and `stop` mean |
| R32.4 | spec document | R32.4 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R32.2 | Player | R32.2 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R34.1 | Publisher | R34.1a | Code | spec | (the spec lets both window families carry the declaration (carrier named by context/06)) | I-MPD: Once-per-session declaration |
| R34.1 | Publisher | R34.1b | NV | spec | the declaration is optional and boolean (schema, level 1); what it means binds the Player (level 3) | I-MPD: Once-per-session declaration |
| R34.4 | spec document | R34.4 | NV | spec | when a window is consumed is the base's execution counter at runtime; no document records it | I-MPD: When a once-per-session window is consumed; I-MPD: `@executeOnce` and an execution that produces no ad |
| R34.6 | spec document | R34.6 | NV | spec | what an execution is and how it resolves are runtime events (level 3) | I-MPD: Executions of an overlay or squeezeback window |
| R34.9 | Publisher | R34.9a | Code | spec | (the spec lets an overlay window declare the offset (carrier named by context/06)) | I-MPD: Late execution: default and start-with-offset |
| R34.9 | Publisher | R34.9b | NV | spec | the declaration is optional; where a late execution starts binds the Player (level 3) | I-MPD: Late execution: default and start-with-offset |
| R34.3 | Player | R34.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R34.10 | Player | R34.10 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R35.1 | APS | R35.1 | Code | overlay-list | (every non-linear resolution document declares dismissibility) | I-RES: Whether the slot is dismissible |
| R35.2 | APS | R35.2 | Code | overlay-list | (the delay is a number of seconds that must elapse: never negative) | I-RES: Delay before the slot is dismissible |
| R35.7 | spec document | R35.7 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R35.8 | spec document | R35.8 | Code | mpd, sps-mpd, list-mpd | R35.8: a linear slot is governed by the base skip declaration; nothing of R35.1's carries dismissal on it. (the document part: the base skip control governs, so the overlay/pause dismissal carrier appears on no linear slot) | I-MPD: `@skipAfter` of an inherited linear event |
| R35.4 | Player | R35.4 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R35.5 | Player | R35.5 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R36.1 | Publisher | R36.1a | Code | spec | (the spec lets both window families carry the offset (carrier named by context/06)) | I-MPD: Earliest-resolution offset: value, anchor and default |
| R36.1 | Publisher | R36.1b | NV | spec | the offset is optional with the base default, typed by the schema (level 1); when a Player requests is level 3 | I-MPD: Earliest-resolution offset: value, anchor and default |
| R36.4 | APS | R36.4 | Code | overlay-list | (a usable lifetime is never negative; absence is legal) | I-RES: How long the resolution remains usable |
| R36.7 | spec document | R36.7 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R36.5 | Player | R36.5 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R37.3 | spec document | R37.3 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R37.1 | Player | R37.1 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R37.2 | Player | R37.2 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R38.1 | Publisher | R38.1 | NV | spec | any declared set of R12.2 tokens is legal (the tokens are R12.2's rule) and absence is legal; what the set, or the family default, admits binds the APS (R38.4) and the Player (R5.6) | I-MPD: `@allowedLayouts`, declared; I-MPD: `@allowedLayouts`, absent |
| R38.4 | APS | R38.4 | NV | spec | needs the set the APS received, which the resolution document does not carry; the examples pair a document with its request only in prose |  |
| R38.6 | spec document | R38.6 | NV | spec | a scope statement; the document property it implies, nothing of ours on a linear event, is checked by R40.7 |  |
| R38.2 | Player | R38.2 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R39.1 | spec document | R39.1 | Code | mpd, sps-mpd, overlay-list | R39.1: `custom` applies only to overlay slots. (`custom` on no pause window and in no pause document) |  |
| R39.2 | Publisher | R39.2a | Code | mpd, sps-mpd | R39.2: a custom region is declared by a Publisher that admits `custom`, which it does by listing it. (a region is declared by a Publisher that admits `custom`, which it does by listing it) | I-MPD: Custom region |
| R39.2 | Publisher | R39.2b | Code | mpd, sps-mpd | R39.2: the region is a rectangle of the viewport (x, y, width, height in percent). (x, y, width, height in percent of the viewport, origin top-left) | I-MPD: Custom region |
| R39.4 | APS | R39.4a | Code | overlay-list | (a `custom` option carries its rectangle) | I-RES: Rectangle of a `custom` option |
| R39.4 | APS | R39.4b | Code | overlay-list | R39.4: the rectangle lies inside the region, which lies inside the viewport. (the region received is not in the document, but every region lies inside the viewport) | I-RES: Rectangle of a `custom` option |
| R39.3 | Player | R39.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R39.5 | Player | R39.5 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R19.3 | spec document | R19.3a | Code | overlay-list | R19.3: an image or HTML form has no intrinsic media, so its duration on the presentation timeline is declared, and is not negative. | I-RES: Declared duration of a form |
| R19.3 | spec document | R19.3b | NV | spec | the wall-clock length and the timeline the cap and beacons run on are Player computations (level 3) | I-RES: Declared duration of a form |
| R19.1 | Player | R19.1 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R21.1 | Player | R21.1 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R25.1 | Player | R25.1 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R26.1 | APS + Publisher | R26.1a | Code | overlay-list | (a squeezeback-double-box-background option carries a background) | I-RES: Background of a double-box |
| R26.1 | APS + Publisher | R26.1b | Code | overlay-list | (a squeezeback-double-box option carries none) | I-RES: Background of a double-box |
| R26.1 | APS + Publisher | R26.1c | NV | spec | that the background is a still image and how the boxes and bands are composed is what the Player renders (level 3) | I-RES: Background of a double-box |
| R26.3 | Player | R26.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R27.1 | APS + Publisher | R27.1a | Code | overlay-list | (an L-shape or frame option carries no background: one creative, no third element) | I-RES: Creative of an L-shape and of the frame |
| R27.1 | APS + Publisher | R27.1b | NV | spec | that the creative covers the frame under the shrunk primary content is what the Player renders (level 3) | I-RES: Creative of an L-shape and of the frame |
| R27.3 | Player | R27.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R41.2 | Publisher | R41.2 | NV | spec | ad-audio allowance: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py. A window that declares nothing does not allow audio, so no document violates R41.2 today | I-MPD: Ad-audio allowance |
| R41.3 | APS | R41.3 | NV | spec | audio declared on an option: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py | I-RES: Audio declared on an option |
| R41.4 | Player | R41.4 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R41.5 | Player + APS | R41.5a | NV | spec | the APS part needs the request (did it carry the allowance?) and an option-audio carrier; no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py |  |
| R41.5 | Player + APS | R41.5b | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R41.6 | Player | R41.6 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R41.7 | Player | R41.7 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R14.3 | spec document | R14.3 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R17.4 | spec document | R17.4 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R17.1 | Player | R17.1 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R17.2 | Player | R17.2 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R17.5 | Player | R17.5 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R20.2 | Publisher | R20.2a | Code | mpd, sps-mpd | R20.2: one EventStream per SGAI scheme in a Period. | I-MPD: One `EventStream` per family and Period |
| R20.2 | Publisher | R20.2b | Code | mpd, sps-mpd | R20.2: an EventStream carrying an SGAI scheme carries no @value. | I-MPD: One `EventStream` per family and Period |
| R20.4 | spec document | R20.4 | NV | spec | whether the document's family matches the requesting slot needs the slot, which the document does not carry; that it declares a family is the schema's (level 1); what follows is level 3 | I-RES: Family of the document against the slot's |
| R20.6 | spec document | R20.6 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R20.1 | Player | R20.1 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R20.3 | Player | R20.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R20.5 | Player | R20.5 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R22.1 | Player | R22.1 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R40.1 | Publisher | R40.1 | Code | mpd, sps-mpd | R40.1: a pause window declares only on top. (optional and at most one are given by a single optional attribute (schema)) | I-MPD: Relation to the inherited linear events: optional, at most one, pause only on top |
| R40.2 | Publisher | R40.2 | NV | spec | says where a Publisher declares a window it wants during an alternative presentation; a document cannot show the want | I-MPD: Windows declared in an alternative presentation's `MPD` |
| R40.9 | spec document | R40.9a | Code | mpd, sps-mpd | R40.9: a window's family is the family its event scheme names, and an Event of an SGAI scheme carries exactly one window of that family. (a window's family is the one its event scheme names) | I-MPD: Family of a non-linear window; I-MPD: Media-time range of an overlay or squeezeback window; I-MPD: Relation to the inherited linear events: what each relation means |
| R40.9 | spec document | R40.9b | Code | mpd, sps-mpd | (an overlay window declares the media-time range it is anchored to) | I-MPD: Family of a non-linear window; I-MPD: Media-time range of an overlay or squeezeback window; I-MPD: Relation to the inherited linear events: what each relation means |
| R40.9 | spec document | R40.9c | NV | spec | what the anchoring and each relation mean (presented, suspended, resumed, executed) is level 3 | I-MPD: Family of a non-linear window; I-MPD: Media-time range of an overlay or squeezeback window; I-MPD: Relation to the inherited linear events: what each relation means |
| R40.7 | spec document | R40.7 | Code | mpd, sps-mpd | R40.7: nothing of this specification is added to an inherited linear event, its Event or its EventStream. |  |
| R40.8 | spec document | R40.8 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R40.3 | Player | R40.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R40.4 | Player | R40.4 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R40.5 | Player | R40.5 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R40.6 | Player | R40.6 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R6.1 | spec document | R6.1 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R6.3 | spec document | R6.3 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R6.5 | spec document | R6.5 | NV | spec | any assignment of @id is legal; its scope decides which beacons fire once, which is level 3 | I-RES: Scope of a beacon's `@id` |
| R6.7 | spec document | R6.7 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R6.4 | Player | R6.4 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R13.1 | APS | R13.1a | Code | overlay-list | R13.1: time-bound beacons are DASH callback events. | I-RES: Carrier of time-bound beacons; I-RES: Time anchor and firing of time-bound beacons |
| R13.1 | APS | R13.1b | NV | spec | that times are relative to the hosting candidate and that each beacon fires then is level 3 | I-RES: Carrier of time-bound beacons; I-RES: Time anchor and firing of time-bound beacons |
| R13.4 | spec document | R13.4 | NV | spec | the document property, beacons bound to a time travel as callback events, is checked by R13.1a; that the specification introduces no scheme is a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R13.5 | APS + ADS | R13.5 | NV | spec | an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it |  |
| R13.6 | APS | R13.6a | Code | spec | (the option can carry the tracking carrier (named by context/06)) | I-RES: Beacons attached to an option or to the candidate |
| R13.6 | APS | R13.6b | NV | spec | that an option's beacon fires only when that option is presented is level 3 | I-RES: Beacons attached to an option or to the candidate |
| R13.7 | APS | R13.7 | NV | spec | slot-start and slot-end beacons: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py | I-RES: Slot-start and slot-end beacons |
| R13.8 | spec document | R13.8 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R13.3 | Player | R13.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R23.1 | spec document | R23.1a | Code | spec | R23.1: the extension namespace defines AdSystem and AdTitle. | I-RES: Application metadata (`AdSystem`, `AdTitle`) |
| R23.1 | spec document | R23.1b | NV | spec | stating that emitting and reading the metadata are optional is a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec | I-RES: Application metadata (`AdSystem`, `AdTitle`) |
| R23.2 | spec document | R23.2 | NV | spec | creative identifiers: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py (context/06 names AssetIdentifier only for a sub-MPD Period) | I-RES: Creative identifiers |
| R24.1 | APS / spec document | R24.1 | Code | list-mpd, sps-mpd | R24.1: a non-AV asset is not an AdaptationSet or Representation @mimeType. (image/* and HTML media types as AdaptationSet or Representation @mimeType on the resolution path) | I-RES: URL of a non-AV asset |
| R33.1 | spec document | R33.1 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R33.3 | spec document | R33.3 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R33.4 | Publisher | R33.4 | Code | mpd, sps-mpd | R33.4: an MPD carrying pause windows requests PlayList through Metrics. | I-MPD: `PlayList` metric request (`Metrics`) |
| R33.2 | Player | R33.2 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R28.1 | APS | R28.1a | Code | overlay-list, list-mpd | R28.1: the ClickThrough of a candidate is carried in the carrier the specification defines: one per candidate, on the candidate. | I-RES: ClickThrough carrier and its click-tracking; I-RES: Click-tracking fired when the ClickThrough is activated; I-RES: The ClickThrough destination, on activation |
| R28.1 | APS | R28.1b | NV | spec | firing the click-tracking and offering the destination on activation is level 3 | I-RES: ClickThrough carrier and its click-tracking; I-RES: Click-tracking fired when the ClickThrough is activated; I-RES: The ClickThrough destination, on activation |
| R28.3 | APS + ADS | R28.3 | NV | spec | an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it |  |
| R28.2 | Player | R28.2 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R42.1 | spec document | R42.1 | NV | spec | occurrence beacons: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py | I-RES: Occurrence beacons |
| R42.2 | APS | R42.2 | NV | spec | needs the occurrence carrier and what the ADS declared; no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py |  |
| R42.4 | spec document | R42.4 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R42.3 | Player | R42.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R44.1 | spec document | R44.1 | NV | spec | verification resources: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py | I-RES: Verification resources |
| R44.2 | APS | R44.2 | NV | spec | an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it; and no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py |  |
| R44.3 | Player | R44.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R47.1 | APS | R47.1 | NV | spec | viewability beacons ride the occurrence carrier of R42.1: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py | I-RES: Viewability beacons |
| R47.3 | spec document | R47.3 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R47.2 | Player | R47.2 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R48.1 | spec document | R48.1 | NV | spec | regulatory disclosure: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py | I-RES: Regulatory disclosure |
| R48.2 | APS | R48.2 | NV | spec | an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it; and no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py |  |
| R48.3 | Player | R48.3 | NV | spec | Player behaviour: level 3 (reference-player) |  |
| R8.1 | spec document | R8.1 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R8.2 | spec document | R8.2 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R9.1 | spec document | R9.1 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R9.2 | spec document | R9.2 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R9.3 | spec document | R9.3 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R10.1 | spec document | R10.1 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R10.2 | spec document | R10.2 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |
| R10.3 | spec document | R10.3 | NV | spec | a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec |  |

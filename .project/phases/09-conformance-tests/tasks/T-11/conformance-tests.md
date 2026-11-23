# Conformance tests

Specification: `dist/sgai-spec.md`. Every verdict below was computed by code (XSD validation and rules as code); none is an LLM's judgement.

**Exit 1** — PASS 1155, FAIL 8, NOT_VERIFIABLE 273, NOT_APPLICABLE 1531.

## FAIL

- **R12.1a** on specification, `/schema/complexType[5]/attribute[4]`: RenderableAsset@layout: missing squeezeback-frame
  - context/03 R12.1: *"- **R12.1** (spec document): The accepted ad-type and visual-placement values are exactly those enumerated in this requirement, each mapped to its IAB definition, plus the optional `custom` overlay layout of R39, which is the one value with no IAB counterpart. The spec MUST NOT accept a value outside the enumeration, and MUST cite the IAB source for the values it accepts."*
- **R12.1a** on specification, `/schema/complexType[1]/attribute[4]`: OverlayPresentation@allowedLayouts: missing squeezeback-frame
  - context/03 R12.1: *"- **R12.1** (spec document): The accepted ad-type and visual-placement values are exactly those enumerated in this requirement, each mapped to its IAB definition, plus the optional `custom` overlay layout of R39, which is the one value with no IAB counterpart. The spec MUST NOT accept a value outside the enumeration, and MUST cite the IAB source for the values it accepts."*
- **R12.1a** on specification, `/schema/complexType[2]/attribute[4]`: PauseAdPresentation@allowedLayouts: missing squeezeback-frame
  - context/03 R12.1: *"- **R12.1** (spec document): The accepted ad-type and visual-placement values are exactly those enumerated in this requirement, each mapped to its IAB definition, plus the optional `custom` overlay layout of R39, which is the one value with no IAB counterpart. The spec MUST NOT accept a value outside the enumeration, and MUST cite the IAB source for the values it accepts."*
- **R34.1a** on specification, `/schema/complexType[1]`: <OverlayPresentation> cannot carry executeOnce: context/06 carries the once-per-session declaration as @executeOnce on overlay and pause windows
  - context/03 R34.1: *"- **R34.1** (Publisher): The Publisher MAY declare an overlay, squeezeback or pause opportunity window as once-per-session. The declaration is optional; a window that does not carry it is executed each time the playhead enters it (R34.6), and a pause window that does not carry it yields a pause ad on every qualifying pause. The declaration means: - on an overlay or squeezeback window, once the window is consumed (R34.3), every later entry of the playhead into the window's range MUST leave the primary content uninterrupted and MUST fire none of the window's beacons; - on a pause window, at most one pause ad MUST be presented for that window for the duration of the session, and a later qualifying pause inside the same window MUST leave the primary content uninterrupted."*
- **R34.9a** on specification, `/schema/complexType[1]`: <OverlayPresentation> cannot carry startWithOffset: context/06 carries the late-execution offset as @startWithOffset on overlay windows
  - context/03 R34.9: *"- **R34.9** (Publisher): The Publisher MAY declare, on an overlay or squeezeback window, that a late execution starts with an offset. An execution that begins after the window's start MUST present the sequence of candidates (R7.1) from its first candidate when the window does not declare it; when it does, the execution MUST begin at the point of the sequence that lies as far from its start as the execution lies from the window's start, and the candidates that end before that point are not presented. In both cases the execution ends no later than the window does (R40)."*
- **R40.9a** on xml#40 (line 5251), `/MPD/Period[1]/EventStream[2]/Event[1]`: 0 window elements in one Event of urn:svta:dash:sgai-overlay:2026; exactly one is needed
  - context/03 R40.9: *"- **R40.9** (spec document): A non-linear window is anchored as follows. An overlay or squeezeback window is anchored to the media-time range it declares: its ad is shown while the presentation that declares it plays through that range, and MUST NOT be shown outside it. A pause window is anchored to the viewer's pause inside its range (R31), and its ad lasts as long as the pause does (R16). The relation a window declares to the inherited linear events it overlaps (R40.1) means: - **default** (nothing declared): the window's forms MUST be presented only while the content of the presentation whose `MPD` declares the window is being output, and every inherited linear event it overlaps MUST be executed with its base semantics. While such an event is being executed, the window MUST NOT be presented and none of its beacons fired; a form on screen when the alternative presentation begins is suspended. When the presentation that declares the window is output again and the playhead is still inside the window's range, the window MUST be resumed in the same execution (R34.6): it is not a new entry, it does not resolve again, and it does not consume a once-per-session window a second time or fire the slot-start beacon again. ADR 0025 records the decision; - **supersede**: the window MUST be presented, and the inherited linear events whose presentation time falls within its span MUST NOT be executed. When the window presents no ad — every attempt to resolve it is a failed execution under R20.1, or the device can render none of its candidates (R5) — those events MUST be executed as the base specification defines; - **on top**: the window MUST be presented also while an alternative presentation that starts within its span is active, composited over that presentation; the inherited linear event executes with its base semantics."*
- **R40.9a** on xml#40 (line 5251), `/MPD/Period[1]/EventStream[3]/Event[1]`: 0 window elements in one Event of urn:svta:dash:sgai-pause-trigger:2026; exactly one is needed
  - context/03 R40.9: *"- **R40.9** (spec document): A non-linear window is anchored as follows. An overlay or squeezeback window is anchored to the media-time range it declares: its ad is shown while the presentation that declares it plays through that range, and MUST NOT be shown outside it. A pause window is anchored to the viewer's pause inside its range (R31), and its ad lasts as long as the pause does (R16). The relation a window declares to the inherited linear events it overlaps (R40.1) means: - **default** (nothing declared): the window's forms MUST be presented only while the content of the presentation whose `MPD` declares the window is being output, and every inherited linear event it overlaps MUST be executed with its base semantics. While such an event is being executed, the window MUST NOT be presented and none of its beacons fired; a form on screen when the alternative presentation begins is suspended. When the presentation that declares the window is output again and the playhead is still inside the window's range, the window MUST be resumed in the same execution (R34.6): it is not a new entry, it does not resolve again, and it does not consume a once-per-session window a second time or fire the slot-start beacon again. ADR 0025 records the decision; - **supersede**: the window MUST be presented, and the inherited linear events whose presentation time falls within its span MUST NOT be executed. When the window presents no ad — every attempt to resolve it is a failed execution under R20.1, or the device can render none of its candidates (R5) — those events MUST be executed as the base specification defines; - **on top**: the window MUST be presented also while an alternative presentation that starts within its span is active, composited over that presentation; the inherited linear event executes with its base semantics."*
- **R13.6a** on specification, `/schema/complexType[5]`: <RenderableAsset> cannot carry Tracking: context/06 attaches a beacon to one option by placing the candidate's tracking carrier on the option
  - context/03 R13.6: *"- **R13.6** (APS): Beacons MAY be attached to a single presentation option instead of to the candidate. A beacon attached to an option reports that option: it MUST fire only when that option is presented, and MUST NOT fire for an option that was not. A beacon attached to the candidate fires whichever option is presented. This is what lets the ADS learn which of the formats the advertiser allowed (R5.8) was shown."*

## Per rule

| rule | level | source | PASS | FAIL | NOT_VERIFIABLE | NOT_APPLICABLE |
|---|---|---|---|---|---|---|
| C07-3 | 1 | context/07 §3 | 0 | 0 | 1 | 0 |
| C07-6a | 1 | context/07 §6, against context/06 "Scheme URI patterns" | 17 | 0 | 0 | 64 |
| C07-6b | 1 | context/07 §6, against context/06 "Element / attribute extension namespaces" | 48 | 0 | 0 | 33 |
| C07-6c | 1 | context/07 §6, against context/06 "Vendor extensions (Qualabs)" | 0 | 0 | 0 | 81 |
| C07-7 | 1 | context/07 §7 | 0 | 0 | 1 | 0 |
| DR-1 | 1 | ISO/IEC 23009-1:2026 §5.3.2.6.1; context/08 DR-1 | 0 | 0 | 8 | 0 |
| DR-1a | 1 | ISO/IEC 23009-1:2026 §7.3.1, applied by §8.15.2 ("The rules for the MPD as defined in subclause 7.3 shall apply."); context/08 DR-1 | 24 | 0 | 0 | 0 |
| DR-1b | 1 | ISO/IEC 23009-1:2026 §8.15.2; context/08 DR-1 | 24 | 0 | 0 | 0 |
| DR-1c | 1 | ISO/IEC 23009-1:2026 §8.15.2; context/08 DR-1 | 24 | 0 | 0 | 0 |
| DR-1d | 1 | ISO/IEC 23009-1:2026 §8.15.2; context/08 DR-1 | 24 | 0 | 0 | 0 |
| DR-1e | 1 | ISO/IEC 23009-1:2026 §8.15.2; context/08 DR-1 | 24 | 0 | 0 | 0 |
| DR-1f | 1 | ISO/IEC 23009-1:2026 §8.15.2; context/08 DR-1 | 24 | 0 | 0 | 0 |
| DR-1g | 1 | ISO/IEC 23009-1:2026 §8.15.2; context/08 DR-1 | 24 | 0 | 0 | 0 |
| DR-1h | 1 | ISO/IEC 23009-1:2026 §8.15.3; context/08 DR-1 | 24 | 0 | 0 | 0 |
| DR-1i | 1 | ISO/IEC 23009-1:2026 §8.15.3; context/08 DR-1 | 24 | 0 | 0 | 0 |
| DR-3 | 1 | ISO/IEC 23009-1:2026 §5.2.1 NOTE 2; context/08 DR-3 | 0 | 0 | 1 | 0 |
| DR-3a | 1 | ISO/IEC 23009-1:2026 §5.2.1 NOTE 2; context/08 DR-3 | 58 | 0 | 45 | 0 |
| DR-4 | 1 | ISO/IEC 23009-1:2026 §8.1; context/08 DR-4 | 0 | 0 | 1 | 0 |
| DR-4a | 1 | ISO/IEC 23009-1:2026 §8.1; context/08 DR-4 | 52 | 0 | 0 | 0 |
| DR-5a | 1 | ISO/IEC 23009-1:2026 §5.3.7.2 Table 16, @profiles; context/08 DR-5 | 0 | 0 | 0 | 52 |
| DR-5b | 1 | ISO/IEC 23009-1:2026 §8.12.4.3, applied to List MPDs by §8.14 (an extension of the CMAF profile); context/08 DR-5 | 0 | 0 | 0 | 52 |
| DR-6 | 1 | ISO/IEC 23009-1:2026 §5.2.1; context/08 DR-6 | 0 | 0 | 1 | 0 |
| DR-7 | 1 | ISO/IEC 23009-1:2026 §5.3.2.2 Table 4, AdaptationSet; context/08 DR-7 | 45 | 0 | 0 | 12 |
| DR-8 | 1 | ISO/IEC 23009-1:2026 §8.1 NOTE 1; context/08 DR-8 | 0 | 0 | 1 | 0 |
| DR-9 | 1 | ISO/IEC 23009-1:2026 §5.8.4.8 NOTE 1; context/08 DR-9 | 0 | 0 | 1 | 0 |
| DR-9a | 1 | ISO/IEC 23009-1:2026 §5.8.4.8 NOTE 1; context/08 DR-9 (consequence of DP-3) | 0 | 0 | 0 | 20 |
| DR-10a | 1 | ISO/IEC 23009-1:2026 §8.14 rules 1 and 2; context/08 DR-10 | 8 | 0 | 0 | 44 |
| DR-10b | 1 | ISO/IEC 23009-1:2026 §5.3.1.4; context/08 DR-10 | 8 | 0 | 0 | 0 |
| DR-10c | 1 | ISO/IEC 23009-1:2026 §8.14; context/08 DR-10 | 0 | 0 | 1 | 0 |
| DR-10d | 1 | ISO/IEC 23009-1:2026 §5.3.1.4; context/08 DR-10 | 0 | 0 | 8 | 0 |
| E-1 | 1 | ISO/IEC 23009-1:2026 Annex B; ADR 0048 | 1 | 0 | 0 | 0 |
| E-2 | 1 | ISO/IEC 23009-1:2026 §5.2.1; ADR 0048 | 1 | 0 | 0 | 0 |
| E-3 | 1 | ISO/IEC 23009-1:2026 Annex B (xs:any / xs:anyAttribute namespace="##other"); ADR 0048 | 77 | 0 | 4 | 2 |
| E-4 | 1 | ISO/IEC 23009-1:2026 §5.2.1 | 52 | 0 | 0 | 0 |
| K-4a | 1 | ISO/IEC 23009-1:2026 §5.10.2.1 | 33 | 0 | 0 | 25 |
| K-4b | 1 | ISO/IEC 23009-1:2026 §5.10.2.2 Table 44, Event@id | 33 | 0 | 0 | 25 |
| K-13a | 1 | ISO/IEC 23009-1:2026 §5.16.3 | 7 | 0 | 0 | 45 |
| K-13b | 1 | ISO/IEC 23009-1:2026 §5.16.3 Table 59, Event@status row | 7 | 0 | 0 | 51 |
| K-14 | 1 | ISO/IEC 23009-1:2026 §5.16.4 Table 62, @clip | 1 | 0 | 0 | 57 |
| K-15a | 1 | ISO/IEC 23009-1:2026 §8.14 rule 3 | 8 | 0 | 0 | 44 |
| K-15b | 1 | ISO/IEC 23009-1:2026 §8.14 rule 5 | 8 | 0 | 0 | 44 |
| K-17 | 1 | ISO/IEC 23009-1:2026 §8.1 (conformance of a Media Presentation to a profile, condition 2) | 0 | 0 | 52 | 0 |
| K-20 | 1 | ISO/IEC 23009-1:2026 §5.10.4.5.3 Table 47 | 12 | 0 | 0 | 46 |
| P-INSERT-shaka | 3 | ADR 0051 | 7 | 0 | 0 | 0 |
| P-LEGACY-dashjs | 3 | context/07 §5 (UC-07) | 20 | 0 | 0 | 0 |
| P-LEGACY-shaka | 3 | context/07 §5 (UC-07) | 20 | 0 | 0 | 0 |
| R1.1 | 2 | context/03 R1.1 | 0 | 0 | 1 | 0 |
| R1.2 | 2 | context/03 R1.2 | 0 | 0 | 1 | 0 |
| R1.3 | 2 | context/03 R1.3 | 0 | 0 | 1 | 0 |
| R1.4 | 2 | context/03 R1.4 | 0 | 0 | 1 | 0 |
| R1.5 | 2 | context/03 R1.5 | 0 | 0 | 1 | 0 |
| R1.6 | 2 | context/03 R1.6 | 0 | 0 | 1 | 0 |
| R2.1 | 2 | context/03 R2.1 | 0 | 0 | 1 | 0 |
| R2.2 | 2 | context/03 R2.2 | 0 | 0 | 1 | 0 |
| R2.3 | 2 | context/03 R2.3 | 0 | 0 | 1 | 0 |
| R2.4 | 2 | context/03 R2.4 | 0 | 0 | 1 | 0 |
| R3.1 | 2 | context/03 R3.1 | 0 | 0 | 1 | 0 |
| R3.2 | 2 | context/03 R3.2 | 0 | 0 | 1 | 0 |
| R4.1 | 2 | context/03 R4.1 | 15 | 0 | 0 | 29 |
| R4.2 | 2 | context/03 R4.2 | 0 | 0 | 1 | 0 |
| R4.4 | 2 | context/03 R4.4 | 0 | 0 | 1 | 0 |
| R4.5 | 2 | context/03 R4.5 | 0 | 0 | 1 | 0 |
| R4.6 | 2 | context/03 R4.6 | 18 | 0 | 0 | 26 |
| R4.7a | 2 | context/03 R4.7 | 0 | 0 | 1 | 0 |
| R4.7b | 2 | context/03 R4.7 | 0 | 0 | 1 | 0 |
| R4.8 | 2 | context/03 R4.8 | 0 | 0 | 1 | 0 |
| R4.9 | 2 | context/03 R4.9 | 0 | 0 | 1 | 0 |
| R4.10 | 2 | context/03 R4.10 | 0 | 0 | 1 | 0 |
| R4.11 | 2 | context/03 R4.11 | 0 | 0 | 1 | 0 |
| R5.1 | 2 | context/03 R5.1 | 20 | 0 | 0 | 3 |
| R5.3 | 2 | context/03 R5.3 | 0 | 0 | 1 | 0 |
| R5.4 | 2 | context/03 R5.4 | 0 | 0 | 1 | 0 |
| R5.6 | 2 | context/03 R5.6 | 0 | 0 | 1 | 0 |
| R5.8 | 2 | context/03 R5.8 | 0 | 0 | 1 | 0 |
| R5.9 | 2 | context/03 R5.9 | 0 | 0 | 1 | 0 |
| R6.1 | 2 | context/03 R6.1 | 0 | 0 | 1 | 0 |
| R6.3 | 2 | context/03 R6.3 | 0 | 0 | 1 | 0 |
| R6.4 | 2 | context/03 R6.4 | 0 | 0 | 1 | 0 |
| R6.5 | 2 | context/03 R6.5 | 0 | 0 | 1 | 0 |
| R6.7 | 2 | context/03 R6.7 | 0 | 0 | 1 | 0 |
| R7.1 | 2 | context/03 R7.1 | 0 | 0 | 1 | 0 |
| R8.1 | 2 | context/03 R8.1 | 0 | 0 | 1 | 0 |
| R8.2 | 2 | context/03 R8.2 | 0 | 0 | 1 | 0 |
| R9.1 | 2 | context/03 R9.1 | 0 | 0 | 1 | 0 |
| R9.2 | 2 | context/03 R9.2 | 0 | 0 | 1 | 0 |
| R9.3 | 2 | context/03 R9.3 | 0 | 0 | 1 | 0 |
| R10.1 | 2 | context/03 R10.1 | 0 | 0 | 1 | 0 |
| R10.2 | 2 | context/03 R10.2 | 0 | 0 | 1 | 0 |
| R10.3 | 2 | context/03 R10.3 | 0 | 0 | 1 | 0 |
| R11.1 | 2 | context/03 R11.1 | 0 | 0 | 1 | 0 |
| R11.2 | 2 | context/03 R11.2 | 0 | 0 | 1 | 0 |
| R11.3 | 2 | context/03 R11.3 | 0 | 0 | 1 | 0 |
| R11.4 | 2 | context/03 R11.4 | 0 | 0 | 1 | 0 |
| R11.5 | 2 | context/03 R11.5 | 0 | 0 | 1 | 0 |
| R12.1a | 2 | context/03 R12.1 | 0 | 3 | 0 | 0 |
| R12.1b | 2 | context/03 R12.1 | 0 | 0 | 1 | 0 |
| R12.2 | 2 | context/03 R12.2 | 15 | 0 | 0 | 29 |
| R12.3 | 2 | context/03 R12.3 | 20 | 0 | 0 | 3 |
| R12.4 | 2 | context/03 R12.4 | 0 | 0 | 1 | 0 |
| R12.5 | 2 | context/03 R12.5 | 0 | 0 | 1 | 0 |
| R13.1a | 2 | context/03 R13.1 | 17 | 0 | 0 | 6 |
| R13.1b | 2 | context/03 R13.1 | 0 | 0 | 1 | 0 |
| R13.3 | 2 | context/03 R13.3 | 0 | 0 | 1 | 0 |
| R13.4 | 2 | context/03 R13.4 | 0 | 0 | 1 | 0 |
| R13.5 | 2 | context/03 R13.5 | 0 | 0 | 1 | 0 |
| R13.6a | 2 | context/03 R13.6 | 0 | 1 | 0 | 0 |
| R13.6b | 2 | context/03 R13.6 | 0 | 0 | 1 | 0 |
| R13.7 | 2 | context/03 R13.7 | 0 | 0 | 1 | 0 |
| R13.8 | 2 | context/03 R13.8 | 0 | 0 | 1 | 0 |
| R14.3 | 2 | context/03 R14.3 | 0 | 0 | 1 | 0 |
| R15.1 | 2 | context/03 R15.1 | 0 | 0 | 1 | 0 |
| R15.2a | 2 | context/03 R15.2 | 20 | 0 | 0 | 3 |
| R15.2b | 2 | context/03 R15.2 | 0 | 0 | 1 | 0 |
| R15.3 | 2 | context/03 R15.3 | 0 | 0 | 1 | 0 |
| R16.1 | 2 | context/03 R16.1 | 0 | 0 | 1 | 0 |
| R17.1 | 2 | context/03 R17.1 | 0 | 0 | 1 | 0 |
| R17.2 | 2 | context/03 R17.2 | 0 | 0 | 1 | 0 |
| R17.4 | 2 | context/03 R17.4 | 0 | 0 | 1 | 0 |
| R17.5 | 2 | context/03 R17.5 | 0 | 0 | 1 | 0 |
| R18.1 | 2 | context/03 R18.1 | 0 | 0 | 1 | 0 |
| R18.2 | 2 | context/03 R18.2 | 0 | 0 | 1 | 0 |
| R19.1 | 2 | context/03 R19.1 | 0 | 0 | 1 | 0 |
| R19.3a | 2 | context/03 R19.3 | 17 | 0 | 0 | 6 |
| R19.3b | 2 | context/03 R19.3 | 0 | 0 | 1 | 0 |
| R20.1 | 2 | context/03 R20.1 | 0 | 0 | 1 | 0 |
| R20.2a | 2 | context/03 R20.2 | 16 | 0 | 0 | 28 |
| R20.2b | 2 | context/03 R20.2 | 16 | 0 | 0 | 28 |
| R20.3 | 2 | context/03 R20.3 | 0 | 0 | 1 | 0 |
| R20.4 | 2 | context/03 R20.4 | 0 | 0 | 1 | 0 |
| R20.5 | 2 | context/03 R20.5 | 0 | 0 | 1 | 0 |
| R20.6 | 2 | context/03 R20.6 | 0 | 0 | 1 | 0 |
| R21.1 | 2 | context/03 R21.1 | 0 | 0 | 1 | 0 |
| R22.1 | 2 | context/03 R22.1 | 0 | 0 | 1 | 0 |
| R23.1a | 2 | context/03 R23.1 | 1 | 0 | 0 | 0 |
| R23.1b | 2 | context/03 R23.1 | 0 | 0 | 1 | 0 |
| R23.2 | 2 | context/03 R23.2 | 0 | 0 | 1 | 0 |
| R24.1 | 2 | context/03 R24.1 | 24 | 0 | 0 | 8 |
| R25.1 | 2 | context/03 R25.1 | 0 | 0 | 1 | 0 |
| R26.1a | 2 | context/03 R26.1 | 4 | 0 | 0 | 19 |
| R26.1b | 2 | context/03 R26.1 | 2 | 0 | 0 | 21 |
| R26.1c | 2 | context/03 R26.1 | 0 | 0 | 1 | 0 |
| R26.3 | 2 | context/03 R26.3 | 0 | 0 | 1 | 0 |
| R27.1a | 2 | context/03 R27.1 | 7 | 0 | 0 | 16 |
| R27.1b | 2 | context/03 R27.1 | 0 | 0 | 1 | 0 |
| R27.3 | 2 | context/03 R27.3 | 0 | 0 | 1 | 0 |
| R28.1a | 2 | context/03 R28.1 | 13 | 0 | 0 | 18 |
| R28.1b | 2 | context/03 R28.1 | 0 | 0 | 1 | 0 |
| R28.2 | 2 | context/03 R28.2 | 0 | 0 | 1 | 0 |
| R28.3 | 2 | context/03 R28.3 | 0 | 0 | 1 | 0 |
| R29.1a | 2 | context/03 R29.1 | 12 | 0 | 0 | 0 |
| R29.1b | 2 | context/03 R29.1 | 2 | 0 | 0 | 10 |
| R29.1c | 2 | context/03 R29.1 | 2 | 0 | 0 | 10 |
| R29.1d | 2 | context/03 R29.1 | 1 | 0 | 0 | 11 |
| R29.1e | 2 | context/03 R29.1 | 1 | 0 | 0 | 11 |
| R29.1f | 2 | context/03 R29.1 | 0 | 0 | 0 | 12 |
| R29.1g | 2 | context/03 R29.1 | 11 | 0 | 0 | 1 |
| R29.1h | 2 | context/03 R29.1 | 1 | 0 | 0 | 11 |
| R29.1i | 2 | context/03 R29.1 | 0 | 0 | 0 | 12 |
| R29.1j | 2 | context/03 R29.1 | 0 | 0 | 0 | 52 |
| R29.2 | 2 | context/03 R29.2 | 0 | 0 | 1 | 0 |
| R29.3 | 2 | context/03 R29.3 | 11 | 0 | 0 | 1 |
| R29.4 | 2 | context/03 R29.4 | 0 | 0 | 1 | 0 |
| R29.5 | 2 | context/03 R29.5 | 0 | 0 | 1 | 0 |
| R29.7 | 2 | context/03 R29.7 | 0 | 0 | 1 | 0 |
| R29.10 | 2 | context/03 R29.10 | 0 | 0 | 1 | 0 |
| R30.1 | 2 | context/03 R30.1 | 0 | 0 | 1 | 0 |
| R30.2 | 2 | context/03 R30.2 | 0 | 0 | 1 | 0 |
| R31.1 | 2 | context/03 R31.1 | 4 | 0 | 0 | 40 |
| R31.2a | 2 | context/03 R31.2 | 0 | 0 | 1 | 0 |
| R31.2b | 2 | context/03 R31.2 | 0 | 0 | 1 | 0 |
| R32.1a | 2 | context/03 R32.1 | 3 | 0 | 0 | 20 |
| R32.1b | 2 | context/03 R32.1 | 0 | 0 | 1 | 0 |
| R32.2 | 2 | context/03 R32.2 | 0 | 0 | 1 | 0 |
| R32.4 | 2 | context/03 R32.4 | 0 | 0 | 1 | 0 |
| R33.1 | 2 | context/03 R33.1 | 0 | 0 | 1 | 0 |
| R33.2 | 2 | context/03 R33.2 | 0 | 0 | 1 | 0 |
| R33.3 | 2 | context/03 R33.3 | 0 | 0 | 1 | 0 |
| R33.4 | 2 | context/03 R33.4 | 4 | 0 | 0 | 40 |
| R34.1a | 2 | context/03 R34.1 | 0 | 1 | 0 | 0 |
| R34.1b | 2 | context/03 R34.1 | 0 | 0 | 1 | 0 |
| R34.3 | 2 | context/03 R34.3 | 0 | 0 | 1 | 0 |
| R34.4 | 2 | context/03 R34.4 | 0 | 0 | 1 | 0 |
| R34.6 | 2 | context/03 R34.6 | 0 | 0 | 1 | 0 |
| R34.9a | 2 | context/03 R34.9 | 0 | 1 | 0 | 0 |
| R34.9b | 2 | context/03 R34.9 | 0 | 0 | 1 | 0 |
| R34.10 | 2 | context/03 R34.10 | 0 | 0 | 1 | 0 |
| R35.1 | 2 | context/03 R35.1 | 23 | 0 | 0 | 0 |
| R35.2 | 2 | context/03 R35.2 | 23 | 0 | 0 | 0 |
| R35.4 | 2 | context/03 R35.4 | 0 | 0 | 1 | 0 |
| R35.5 | 2 | context/03 R35.5 | 0 | 0 | 1 | 0 |
| R35.7 | 2 | context/03 R35.7 | 0 | 0 | 1 | 0 |
| R35.8 | 2 | context/03 R35.8 | 17 | 0 | 0 | 35 |
| R36.1a | 2 | context/03 R36.1 | 1 | 0 | 0 | 0 |
| R36.1b | 2 | context/03 R36.1 | 0 | 0 | 1 | 0 |
| R36.4 | 2 | context/03 R36.4 | 23 | 0 | 0 | 0 |
| R36.5 | 2 | context/03 R36.5 | 0 | 0 | 1 | 0 |
| R36.7 | 2 | context/03 R36.7 | 0 | 0 | 1 | 0 |
| R37.1 | 2 | context/03 R37.1 | 0 | 0 | 1 | 0 |
| R37.2 | 2 | context/03 R37.2 | 0 | 0 | 1 | 0 |
| R37.3 | 2 | context/03 R37.3 | 0 | 0 | 1 | 0 |
| R38.1 | 2 | context/03 R38.1 | 0 | 0 | 1 | 0 |
| R38.2 | 2 | context/03 R38.2 | 0 | 0 | 1 | 0 |
| R38.4 | 2 | context/03 R38.4 | 0 | 0 | 1 | 0 |
| R38.6 | 2 | context/03 R38.6 | 0 | 0 | 1 | 0 |
| R39.1 | 2 | context/03 R39.1 | 6 | 0 | 0 | 61 |
| R39.2a | 2 | context/03 R39.2 | 1 | 0 | 0 | 43 |
| R39.2b | 2 | context/03 R39.2 | 1 | 0 | 0 | 43 |
| R39.3 | 2 | context/03 R39.3 | 0 | 0 | 1 | 0 |
| R39.4a | 2 | context/03 R39.4 | 1 | 0 | 0 | 22 |
| R39.4b | 2 | context/03 R39.4 | 1 | 0 | 0 | 22 |
| R39.5 | 2 | context/03 R39.5 | 0 | 0 | 1 | 0 |
| R40.1 | 2 | context/03 R40.1 | 4 | 0 | 0 | 40 |
| R40.2 | 2 | context/03 R40.2 | 0 | 0 | 1 | 0 |
| R40.3 | 2 | context/03 R40.3 | 0 | 0 | 1 | 0 |
| R40.4 | 2 | context/03 R40.4 | 0 | 0 | 1 | 0 |
| R40.5 | 2 | context/03 R40.5 | 0 | 0 | 1 | 0 |
| R40.6 | 2 | context/03 R40.6 | 0 | 0 | 1 | 0 |
| R40.7 | 2 | context/03 R40.7 | 9 | 0 | 0 | 35 |
| R40.8 | 2 | context/03 R40.8 | 0 | 0 | 1 | 0 |
| R40.9a | 2 | context/03 R40.9 | 15 | 2 | 0 | 28 |
| R40.9b | 2 | context/03 R40.9 | 13 | 0 | 0 | 31 |
| R40.9c | 2 | context/03 R40.9 | 0 | 0 | 1 | 0 |
| R41.2 | 2 | context/03 R41.2 | 0 | 0 | 1 | 0 |
| R41.3 | 2 | context/03 R41.3 | 0 | 0 | 1 | 0 |
| R41.4 | 2 | context/03 R41.4 | 0 | 0 | 1 | 0 |
| R41.5a | 2 | context/03 R41.5 | 0 | 0 | 1 | 0 |
| R41.5b | 2 | context/03 R41.5 | 0 | 0 | 1 | 0 |
| R41.6 | 2 | context/03 R41.6 | 0 | 0 | 1 | 0 |
| R41.7 | 2 | context/03 R41.7 | 0 | 0 | 1 | 0 |
| R42.1 | 2 | context/03 R42.1 | 0 | 0 | 1 | 0 |
| R42.2 | 2 | context/03 R42.2 | 0 | 0 | 1 | 0 |
| R42.3 | 2 | context/03 R42.3 | 0 | 0 | 1 | 0 |
| R42.4 | 2 | context/03 R42.4 | 0 | 0 | 1 | 0 |
| R44.1 | 2 | context/03 R44.1 | 0 | 0 | 1 | 0 |
| R44.2 | 2 | context/03 R44.2 | 0 | 0 | 1 | 0 |
| R44.3 | 2 | context/03 R44.3 | 0 | 0 | 1 | 0 |
| R47.1 | 2 | context/03 R47.1 | 0 | 0 | 1 | 0 |
| R47.2 | 2 | context/03 R47.2 | 0 | 0 | 1 | 0 |
| R47.3 | 2 | context/03 R47.3 | 0 | 0 | 1 | 0 |
| R48.1 | 2 | context/03 R48.1 | 0 | 0 | 1 | 0 |
| R48.2 | 2 | context/03 R48.2 | 0 | 0 | 1 | 0 |
| R48.3 | 2 | context/03 R48.3 | 0 | 0 | 1 | 0 |
| XSD-ID | 1 | ADR 0047 | 1 | 0 | 0 | 0 |

## NOT_VERIFIABLE, and why

- **C07-3** (1): asks for prose in the construct's chapter; level 2 and review read the prose
- **C07-7** (1): asks for a link and a confirmation in the construct's chapter, which is prose
- **DR-1** (8): the referenced MPD is fetched at resolution time and is not in the referring document; the specification's sub-MPDs that declare the SPS profile are checked against §8.15 by DR-1a..DR-1i
- **DR-3** (1): what legacy behaviour the specification's text assumes for a baseline element nested inside a foreign one is a property of the prose, not of a document; the document half (valid after removal by namespace) is E-4
- **DR-3a** (45): DASH element Event inside Tracking: it is removed with its foreign parent, so no legacy behaviour may be assumed for it; whether the author assumed one is not in the document
- **DR-4** (1): whether an Interoperability Point URI is defined, published and given sufficient semantics is a fact about the specification's text and its publication, not about a document
- **DR-6** (1): which of the four carriers a construct uses, and why, is the classification its chapter states (context/07 §8); the document side (no non-MP4 @mimeType on the AdaptationSet axis, nothing new in the DASH namespace) is DR-1a, DR-5b and E-3
- **DR-8** (1): DR-8 limits what the specification's text may promise about a Player; no document property follows from it
- **DR-9** (1): which descriptor element a construct uses, and the reason, is stated in its chapter; both elements are valid in a document, so no document property separates the right choice from the wrong one
- **DR-10c** (1): how a document is reached (by an Alternative MPD event or otherwise) is not in the document
- **DR-10d** (8): the base gives no closed list of 'the constraints of a static Media Presentation': each lives in its own attribute row, and none is transcribed here
- **E-3** (1): fragment whose root {urn:mpeg:dash:schema:mpd:2011}Period is not a global element of either schema
- **E-3** (1): fragment whose root {urn:svta:dash:sgai:2026}RenderableAsset is not a global element of either schema
- **E-3** (1): fragment whose root {urn:svta:dash:sgai:2026}Tracking is not a global element of either schema
- **E-3** (1): fragment whose root Metrics is not a global element of either schema
- **K-17** (52): a condition on the Media Presentation (the MPD with its Segments, and for a List MPD the merged result of its Linked Periods), which §8.1 lists apart from the conditions on the MPD; an MPD example may elide its Representations (ISO's own K.6.4 does), so the document alone does not decide it
- **R1.1** (1): the document property (removing every extension leaves a valid MPD) is level 1, E-4; that the primary content keeps playing is level 3a
- **R1.2** (1): that every construct hangs from an enumerated extension point is level 1 (E-3 and the DR rules of ADR 0049)
- **R1.3** (1): whether a base construct's semantics were altered is a reading of the specification's prose against the base; a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R1.4** (1): Player behaviour: level 3 (reference-player)
- **R1.5** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R1.6** (1): Player behaviour: level 3 (reference-player)
- **R2.1** (1): forbids inference at runtime by other actors; the declarations it requires on a document are checked by R4.1 and R12.2
- **R2.2** (1): what the ADS decides and how the APS converts it are processes, and the ADS's output is not a document this specification defines
- **R2.3** (1): Player behaviour: level 3 (reference-player)
- **R2.4** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R3.1** (1): the class is derived and never sent: a reserved-looking name for it fails R29.1a, and a vendor-named one cannot be recognised by code; giving each class its behaviour is a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R3.2** (1): Player behaviour: level 3 (reference-player)
- **R4.2** (1): Player behaviour: level 3 (reference-player)
- **R4.4** (1): an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it; it limits what a conformance check on the ADS may fail
- **R4.5** (1): Player behaviour: level 3 (reference-player)
- **R4.7a** (1): a zero cap is a legal declaration (typed by the schema); what it means, not executing, binds the Player
- **R4.7b** (1): Player behaviour: level 3 (reference-player)
- **R4.8** (1): @maxDuration on an inherited linear event is optional and typed by the base schema; no document can violate R4.8, which fixes how absence is read (level 3)
- **R4.9** (1): Player behaviour: level 3 (reference-player)
- **R4.10** (1): Player behaviour: level 3 (reference-player)
- **R4.11** (1): the timeline the cap accrues on is a Player computation; the document carries only the cap and its timescale
- **R5.3** (1): Player behaviour: level 3 (reference-player)
- **R5.4** (1): an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it; it fixes what the specification may not be read as requiring
- **R5.6** (1): Player behaviour: level 3 (reference-player)
- **R5.8** (1): what the options represent (the formats the advertiser allowed) is not visible in the document
- **R5.9** (1): Player behaviour: level 3 (reference-player)
- **R6.1** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R6.3** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R6.4** (1): Player behaviour: level 3 (reference-player)
- **R6.5** (1): any assignment of @id is legal; its scope decides which beacons fire once, which is level 3
- **R6.7** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R7.1** (1): any order of candidates is legal; it binds presentation, which is level 3
- **R8.1** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R8.2** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R9.1** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R9.2** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R9.3** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R10.1** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R10.2** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R10.3** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R11.1** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R11.2** (1): Player behaviour: level 3 (reference-player)
- **R11.3** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R11.4** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R11.5** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R12.1b** (1): citing the IAB source for each accepted value is a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R12.4** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec; the bounds are the IAB's, inherited by reference
- **R12.5** (1): the composition a token denotes is what the Player builds on screen (level 3); the document carries only the token, checked by R12.2 and R12.3
- **R13.1b** (1): that times are relative to the hosting candidate and that each beacon fires then is level 3
- **R13.3** (1): Player behaviour: level 3 (reference-player)
- **R13.4** (1): the document property, beacons bound to a time travel as callback events, is checked by R13.1a; that the specification introduces no scheme is a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R13.5** (1): an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it
- **R13.6b** (1): that an option's beacon fires only when that option is presented is level 3
- **R13.7** (1): slot-start and slot-end beacons: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py
- **R13.8** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R14.3** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R15.1** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R15.2b** (1): the Publisher part: an MPD declares windows, not creatives, so no Publisher document carries a form's mimeType
- **R15.3** (1): Player behaviour: level 3 (reference-player)
- **R16.1** (1): Player behaviour: level 3 (reference-player)
- **R17.1** (1): Player behaviour: level 3 (reference-player)
- **R17.2** (1): Player behaviour: level 3 (reference-player)
- **R17.4** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R17.5** (1): Player behaviour: level 3 (reference-player)
- **R18.1** (1): the event URL is the window's @uri (typed by the schema, level 1); whether a request is sent to it is Player behaviour, and an example request is tied to its window only by prose, not by data the check can follow
- **R18.2** (1): an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it
- **R19.1** (1): Player behaviour: level 3 (reference-player)
- **R19.3b** (1): the wall-clock length and the timeline the cap and beacons run on are Player computations (level 3)
- **R20.1** (1): Player behaviour: level 3 (reference-player)
- **R20.3** (1): Player behaviour: level 3 (reference-player)
- **R20.4** (1): whether the document's family matches the requesting slot needs the slot, which the document does not carry; that it declares a family is the schema's (level 1); what follows is level 3
- **R20.5** (1): Player behaviour: level 3 (reference-player)
- **R20.6** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R21.1** (1): Player behaviour: level 3 (reference-player)
- **R22.1** (1): Player behaviour: level 3 (reference-player)
- **R23.1b** (1): stating that emitting and reading the metadata are optional is a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R23.2** (1): creative identifiers: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py (context/06 names AssetIdentifier only for a sub-MPD Period)
- **R25.1** (1): Player behaviour: level 3 (reference-player)
- **R26.1c** (1): that the background is a still image and how the boxes and bands are composed is what the Player renders (level 3)
- **R26.3** (1): Player behaviour: level 3 (reference-player)
- **R27.1b** (1): that the creative covers the frame under the shrunk primary content is what the Player renders (level 3)
- **R27.3** (1): Player behaviour: level 3 (reference-player)
- **R28.1b** (1): firing the click-tracking and offering the destination on activation is level 3
- **R28.2** (1): Player behaviour: level 3 (reference-player)
- **R28.3** (1): an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it
- **R29.2** (1): Player behaviour: level 3 (reference-player). Whether a capability parameter is sent is the Player's choice, and a slot parameter is due only when the slot declares it, which needs the window the request was built from
- **R29.4** (1): Player behaviour: level 3 (reference-player). A request does not show which parameters the Player added and which came with the Publisher's event URL (R18.2), and only the first need the vendor prefix
- **R29.5** (1): how an APS behaves on receiving a request without a parameter; no document records it
- **R29.7** (1): an absent capability parameter is legal; its meaning (undetermined) binds the APS's resolution, which no document records
- **R29.10** (1): Player behaviour: level 3 (reference-player). Whether a declared value is the device's real capability is a property of the device, not of the request
- **R30.1** (1): that the empty resolution is a complete, well-formed document is the schema's (level 1); that it is not an error status or an empty body is a property of the HTTP response, which no example carries
- **R30.2** (1): Player behaviour: level 3 (reference-player)
- **R31.2a** (1): the Publisher part forbids an interpretation, not a value: any declared cap on a pause window is legal
- **R31.2b** (1): Player behaviour: level 3 (reference-player)
- **R32.1b** (1): what repeat, request-again and stop mean, and the default, bind the Player (level 3)
- **R32.2** (1): Player behaviour: level 3 (reference-player)
- **R32.4** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R33.1** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R33.2** (1): Player behaviour: level 3 (reference-player)
- **R33.3** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R34.1b** (1): the declaration is optional and boolean (schema, level 1); what it means binds the Player (level 3)
- **R34.3** (1): Player behaviour: level 3 (reference-player)
- **R34.4** (1): when a window is consumed is the base's execution counter at runtime; no document records it
- **R34.6** (1): what an execution is and how it resolves are runtime events (level 3)
- **R34.9b** (1): the declaration is optional; where a late execution starts binds the Player (level 3)
- **R34.10** (1): Player behaviour: level 3 (reference-player)
- **R35.4** (1): Player behaviour: level 3 (reference-player)
- **R35.5** (1): Player behaviour: level 3 (reference-player)
- **R35.7** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R36.1b** (1): the offset is optional with the base default, typed by the schema (level 1); when a Player requests is level 3
- **R36.5** (1): Player behaviour: level 3 (reference-player)
- **R36.7** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R37.1** (1): Player behaviour: level 3 (reference-player)
- **R37.2** (1): Player behaviour: level 3 (reference-player)
- **R37.3** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R38.1** (1): any declared set of R12.2 tokens is legal (the tokens are R12.2's rule) and absence is legal; what the set, or the family default, admits binds the APS (R38.4) and the Player (R5.6)
- **R38.2** (1): Player behaviour: level 3 (reference-player)
- **R38.4** (1): needs the set the APS received, which the resolution document does not carry; the examples pair a document with its request only in prose
- **R38.6** (1): a scope statement; the document property it implies, nothing of ours on a linear event, is checked by R40.7
- **R39.3** (1): Player behaviour: level 3 (reference-player)
- **R39.5** (1): Player behaviour: level 3 (reference-player)
- **R40.2** (1): says where a Publisher declares a window it wants during an alternative presentation; a document cannot show the want
- **R40.3** (1): Player behaviour: level 3 (reference-player)
- **R40.4** (1): Player behaviour: level 3 (reference-player)
- **R40.5** (1): Player behaviour: level 3 (reference-player)
- **R40.6** (1): Player behaviour: level 3 (reference-player)
- **R40.8** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R40.9c** (1): what the anchoring and each relation mean (presented, suspended, resumed, executed) is level 3
- **R41.2** (1): ad-audio allowance: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py. A window that declares nothing does not allow audio, so no document violates R41.2 today
- **R41.3** (1): audio declared on an option: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py
- **R41.4** (1): Player behaviour: level 3 (reference-player)
- **R41.5a** (1): the APS part needs the request (did it carry the allowance?) and an option-audio carrier; no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py
- **R41.5b** (1): Player behaviour: level 3 (reference-player)
- **R41.6** (1): Player behaviour: level 3 (reference-player)
- **R41.7** (1): Player behaviour: level 3 (reference-player)
- **R42.1** (1): occurrence beacons: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py
- **R42.2** (1): needs the occurrence carrier and what the ADS declared; no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py
- **R42.3** (1): Player behaviour: level 3 (reference-player)
- **R42.4** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R44.1** (1): verification resources: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py
- **R44.2** (1): an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it; and no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py
- **R44.3** (1): Player behaviour: level 3 (reference-player)
- **R47.1** (1): viewability beacons ride the occurrence carrier of R42.1: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py
- **R47.2** (1): Player behaviour: level 3 (reference-player)
- **R47.3** (1): a property of the specification's prose (what it states, cites or justifies), not of a document instance; judged by validate-spec
- **R48.1** (1): regulatory disclosure: no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py
- **R48.2** (1): an obligation between parties outside the documents (the APS-to-ADS contract, R18): no document shows it; and no carrier is bound for it: context/06 leaves the name to the build and the specification under test declares none the catalogue recognises; undecidable until one is named and bound in vocab.py
- **R48.3** (1): Player behaviour: level 3 (reference-player)

[GROUNDED_BY=spec-only]

# Error semantics matrix

Inputs consumed (all mtime 2026-09-15): `../context/02-actors.md`,
`../context/03-requirements.md` (R1..R30, DP-1..DP-3) and
`../context/05-dash-linear-interfaces.md`. Total rows: 15 — every
condition on the Player-visible interfaces under which an ad
opportunity can fail to be honoured, with the obligations the other
three actors carry for each.

## Scope

In scope:

- Errors on the Player ↔ APS interface — the resolution request and
  the document it returns — including Player-side validation of that
  document against Publisher-declared constraints (R2.3).
- Errors surfaced while rendering an accepted candidate: duration
  overrun, decode failure, mid-render loss, composition conflicts.
- Errors on the Player ↔ tracking-endpoint interface.

Out of scope:

- The APS ↔ ADS interface, opaque to this specification (R18, OOS-2);
  a failure there reaches the Player only as E1, E2 or E5.
- Primary-content delivery errors (Publisher CDN, ABR, segment retry)
  and auth / DRM / token exchange — DASH baseline, orthogonal to SGAI.
- Requirements with no runtime failure mode: the governance set (R8,
  R9, R10) and VAST independence (R11). Violating one is
  non-conformance of the spec document, not a condition to which a
  Player response can be assigned.

Rows marked **UNDEFINED** flag a condition on which `../context/`
states no Player response. They are gaps to close in the spec, not
behaviour this analysis invents.

## Error matrix

| ID | Error condition | Player response (MUST) | Player response (MAY) | Non-Player actor obligation |
|---|---|---|---|---|
| E1 | Resolution request fails at transport level: DNS unresolvable, TCP refused, TLS handshake failure, or timeout before any final status. | Treat the window as unresolvable and fall through to the next overlapping same-family window when the Publisher declared one; when none is declared, fall through to primary content uninterrupted (R20.1, R1.1). | Re-attempt within the interval between the Earliest Resolution Time and the event's `presentationTime`; surface the failure through an implementation-defined API. **UNDEFINED**: `context/` fixes no retry count, backoff or deadline for the resolution request. | Publisher: declare a fallback window where continuity matters, and an `@earliestResolutionTimeOffset` wide enough to leave room before the slot (R20.1). APS: serve the event `@uri` for the whole window the Publisher declared. |
| E2 | Resolution request returns a final HTTP status other than `200` (4xx / 5xx), including an APS that refuses to answer because a reserved capability parameter was absent. | Same as E1 — fallback window if declared, else primary content uninterrupted (R20.1). | Re-attempt before the event's `presentationTime`; log. | APS: MUST tolerate the absence of every reserved capability parameter and produce candidates without any of them (R29.5); an absent parameter means undetermined, never unsupported (R29.7). |
| E3 | Response is `200` but the resolution document is not well-formed XML, carries an unknown root element, or fails schema validation. | Render nothing from that document and continue playing the primary content uninterrupted (R1.4, DP-3). | Log the parse or validation failure. **UNDEFINED**: R20.1 enumerates transport failure, no response, and a non-`200` status as the triggers for the fallback window. A `200` carrying an unusable body matches none of them and is not the accessible-but-empty case of R30 either, so whether the fallback window is tried is not decided by `context/`. | APS: emit a document valid against the DASH 6th edition schema plus the extension points R1.2 admits. |
| E4 | Resolution document arrives after the slot window has elapsed. | Not extend the slot past the Publisher-declared cap in order to play it (R4.3); keep primary content uninterrupted (DP-3). | Discard the document; reuse it for a later still-unresolved window of the same family. **UNDEFINED**: `context/` defines late *execution* of an event (`@clip` trims to `@maxDuration`, `@startWithOffset` decides whether a delayed ad starts at its first frame — §5.16.4 via `../context/05-dash-linear-interfaces.md`) but states no Player response for a resolution document that lands after the window is over. | Publisher: declare an `@earliestResolutionTimeOffset` that gives the APS a usable head start. APS: answer inside the window it was asked in; the APS-to-ADS latency budget is bilateral and outside this spec (R18). |
| E5 | Response is `200` and the document carries no candidates — the opportunity resolved to no ads. | Continue with the primary content uninterrupted, exactly as when candidates are exhausted (R30, R5.3), and NOT fall through to a fallback window: the opportunity resolved (R20.1). | Report the opportunity as unfilled rather than failed, through an implementation-defined API. | APS: express a no-ads decision as a document carrying no candidates, never as an error response and never as a response without a body (R30.1). ADS: none — no-fill is a legitimate decision, not a failure. |
| E6 | No presentation option on a candidate is satisfiable: the device renders none of the offered forms, or every offered layout needs more decoders or surfaces than the device has (R26.3, R27.3). | Skip that candidate and fall through to the next one in document order; continue with primary content only once every candidate is exhausted (R3.3, R5.3, R5.7, R7.2). | Report the skip through an implementation-defined API. | APS: carry the presentation options as an ordered list whose document order is the preference order (R5.1, R5.5). Neither ADS nor APS is required to hold a device-class matrix (R5.4); a candidate carrying a single option places the suitability call upstream, with the APS or with the ADS that returned one option to it. |
| E7 | A presentation option names a layout the Publisher did not allow on the slot, or one outside the ad-type / visual-placement set R12 enumerates (the vocabulary `../context/99-glossary.md` defers to). | Not render that option; move to the next option in document order and skip the candidate when none passes both the device check and the allowed-layouts check (R5.6, R5.7). | Report the rejected layout name. **UNDEFINED**: when the Publisher declared the slot's layouts unrestricted (`../context/02-actors.md`), a name outside the R12 enumeration passes the allowed-layouts check, and `context/` gives the Player no verdict on a layout it cannot map to an enumerated placement. | Publisher: draw allowed-layout names only from the enumerated set; Publisher-private names and IAB values outside it MUST NOT appear (R12.2). APS: emit no form metadata for an ad type or placement outside that set (R12.3). |
| E8 | A candidate's creative carrier is outside the admissible set — not video, image or HTML — or a non-AV asset URL is expressed as `@mimeType` on a path bound by RFC 4337. | Not render a form the device cannot render (R3.3). | Skip the candidate as a non-conformant upstream signal (R15.3) and fall through as in E6. **UNDEFINED**: R15.3 is permissive only. For a carrier outside the admissible set that the device *can* nevertheless render, `context/` states no obligation, so rendering it and skipping it are both unconstrained. | APS + Publisher: every creative carries a mimeType inside the admissible set (R15.2), and non-AV asset URLs travel on one of the DASH-conformant carriers of DR-6, never on an RFC 4337-bound `@mimeType` path (R24.1). |
| E9 | A candidate's **declared** duration would push the cumulative slot duration past the Publisher-declared cap. | Not extend the slot past the cap, whatever the ADS metadata or the candidate count say (R4.3); keep the surviving candidates in document order, without re-ordering or deduplicating (R7.4). | Drop that candidate before playback on declared duration alone — "drop before play" (R7.3); accepting it instead defers the case to E10. | Publisher: declare a maximum duration on every slot, linear or non-linear (R4.1). **UNDEFINED**: `context/` states no Player response for a slot on which the Publisher declared no cap. ADS: not required to respect the cap when selecting candidates; a conformance check MUST NOT fail solely on cumulative overflow (R4.4). |
| E10 | An accepted candidate's **actual** rendered length exceeds its declared duration, or the sequence reaches the cap mid-ad. | Stop rendering at the cap boundary even mid-ad, enforcing against actual and not declared length — "trim during play" (R4.2, R4.5, R7.5, R14.2) — and stop firing the remaining beacons at the trim boundary (R13.3). | Surface the trim through an implementation-defined API. | ADS + APS: declared durations that match the creatives reduce trims but are not a conformance condition on the cap (R4.4). Cap arithmetic runs on the presentation timeline; wall-clock on-screen length is derived from it and never duplicated (R19.3, DP-1.2). |
| E11 | Rendering an accepted candidate fails at runtime: an ad segment returns 4xx / 5xx, a decode error occurs, or the network is lost mid-ad. | Abort that ad and continue playing the primary content uninterrupted (R1.4, DP-3). | Skip to the next candidate in document order or end the break — Player policy, per the interface contracts in `../context/05-dash-linear-interfaces.md`; retry the ad segment per DASH-IF guidance before aborting. | APS: reference ad media reachable for the duration of the slot. |
| E12 | An event scheme URI, extension element or namespace in the primary MPD or in the resolution document is unknown to the Player. | Ignore the unknown construct together with its whole subtree and keep playing the primary content uninterrupted (R1.1, R6.4, R23.1). | Log the unknown scheme or namespace. | Publisher + APS: express every new construct through one of the extension points R1.2 enumerates, whose ignore-if-unknown semantics produce this behaviour on a conforming legacy Player, and never alter pre-existing DASH semantics (R1.3). |
| E13 | A tracking beacon or a click-tracking request fails: transport error, timeout, or non-2xx response. | Keep the ad and the primary content unaffected — a beacon failure is non-fatal and never reaches the viewer (`../context/05-dash-linear-interfaces.md`, interface contracts). | Retry the beacon and log the failure; the retry policy is implementation-defined. | APS: carry beacons as `<Event>` entries in an `EventStream` of scheme `urn:mpeg:dash:event:callback:2015`, timed on the ad's presentation timeline (R6.2, R13.1). ADS: owns which beacons exist and at which relative times (R13); transcription fidelity is an APS-to-ADS matter outside this spec (R13.5). |
| E14 | A beacon is scheduled for a moment the ad never reaches: past a trim boundary (E10), or after a pause-ad was dismissed on resume. | Stop firing the remaining beacons at the trim boundary (R13.3), and cease the pause-ad's beacons from the pause-to-play transition onward — beacons scheduled after it fall outside the pause-ad's active window (R16.1, R16.2). | Report the unfired beacons through an implementation-defined API. | ADS + APS: schedules are expressed relative to the ad's presentation timeline (R13.1), so a schedule overrunning the slot is trimmed by the Player rather than rejected upstream. |
| E15 | The resolution document implies two non-linear forms on screen at the same instant, or a pause-ad window opens while an overlay is rendering. | Keep at most one non-linear form active at any instant (R22.1): present sequenced forms one after another in the order the document declares (R14.1), and during a pause suspend the overlay and render the pause-ad, restoring the overlay on resume only if its window is still open (R17.1, R17.2, R17.3). | Report the suspended form through an implementation-defined API. | APS: declare forms as a sequence, never as a concurrent composition (R14.3). Publisher, ADS and APS have no construct that inverts the pause-ad-over-overlay priority (R17.4). Overlapping windows of the same family are a declared fallback chain, not a concurrency case (R20.1). |

## Notes

### Fall-through definition

"Fall through to primary content uninterrupted" means: no visible
artefact — no freeze, no blank slate, no error overlay unless the
application explicitly opted in; no tracking beacon fired for the
opportunity that failed; and primary-content playback continuing on
its own timeline. The viewer cannot tell that an ad opportunity
existed. This is the floor DP-3 sets: an opportunity that cannot be
honoured degrades into graceful skip-and-continue, and applying this
specification never breaks primary-content playback.

Falling through at the *candidate* level (E6, E7, E8) is a different
move: the Player advances to the next candidate in document order and
reaches primary content only once every candidate is exhausted (R5.3).

### Order of precedence

When several conditions arise on the same exchange, the Player applies
them in this order:

1. **Transport** (E1, E2) — no document, so nothing downstream applies.
2. **Resolution-document level** (E3, E4, E5) — the document is
   unusable, late, or legitimately empty. E5 is terminal for the
   opportunity: it resolved, so no fallback window is tried.
3. **Constraint surfacing** (E7, E8, E9) — Publisher-declared
   constraints validated against each candidate before anything is
   rendered.
4. **Per-candidate decode-time** (E6, E11) — what the device can
   actually satisfy and what the ad CDN actually delivers.
5. **Per-candidate playback-time** (E10, E15) — the cap enforced
   against actual length, and the single-active-form bound.
6. **Tracking failures** (E13, E14) — non-fatal throughout; they never
   abort an ad and never reach the viewer.

E12 is orthogonal: an unknown construct is ignored wherever it appears,
at any level, and never advances the Player to the next step.

### Guarantees by actor

**Publisher.** Declares in the MPD, not by runtime inference (R2.1): a
maximum duration on every slot (R4.1), allowed layouts drawn from the
enumerated set (R12.2), and the opportunity windows including any
fallback chain (R20.1). An authoring-time actor — it guarantees nothing
at runtime, and every unmet Publisher obligation above degrades into a
Player-side skip, never into interrupted playback.

**ADS.** Decides which ads, how many and in what order, and owns the
tracking schedule (R13). Guarantees neither the slot cap (R4.4) nor a
device-capability view (R5.4); no-fill is a legitimate outcome, not a
failure (R30). Nothing it emits is checked by this matrix — its output
reaches the Player only through the APS.

**APS.** The only non-Player actor whose output this specification
checks at runtime. Guarantees: a document that parses and validates
(E3); a `200` with no candidates for an unfilled opportunity rather
than an error (R30.1); presentation options as an ordered list in
preference order (R5.1); creatives inside the admissible carrier set on
DASH-conformant carriers (R15.2, R24.1); form metadata only for the
enumerated ad types (R12.3); beacons as callback events on the ad's
presentation timeline (R6.2, R13.1); the ClickThrough with any
click-tracking URLs accompanying it in the normative carrier (R28.1);
and an answer that depends on no reserved capability parameter (R29.5).

**Player.** The enforcer. Guarantees that primary-content playback
survives every row of this matrix (R1.1, R1.4); that Publisher-declared
constraints are validated before anything is rendered (R2.3); that the
cap holds against actual length even mid-ad (R4.2, R4.5); that document
order is honoured, dropping allowed and re-ordering not (R7.1, R7.4);
that no form its device cannot render reaches the screen (R3.3); that
at most one non-linear form is active at any instant (R22.1); and that
a defined behaviour — render, fall back, or skip — exists for every
device class and opportunity type (R3.2).

### Surfacing errors to the application layer

Everything in the "Player response (MAY)" column that reports, logs or
exposes a condition is non-normative: this specification defines
neither event names, nor payloads, nor delivery mechanism, and a Player
that exposes nothing is conformant. Chapter 9 SHOULD give guidance on
what is worth surfacing — the unfilled opportunity (E5) versus failed
resolution (E1, E2, E3) distinction carries the most operational value
— while leaving the API shape to implementers.

One boundary is normative rather than a matter of API shape: an error
overlay is a visible artefact, so a Player that renders one on any row
of this matrix has broken the fall-through guarantee unless the
application explicitly opted in.

## References

- [`../context/02-actors.md`](../context/02-actors.md) — actor
  definitions and the boundary summary behind the obligations column.
- [`../context/03-requirements.md`](../context/03-requirements.md) —
  R1..R30 and the design principles DP-1 through DP-3.
- [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
  — interface contracts table, linear message flow, VAST → ListMPD
  edge cases.
- [`../context/99-glossary.md`](../context/99-glossary.md) —
  terminology; the edition-scoped ad-type and placement vocabulary is
  R12 of `03-requirements.md`, to which the glossary defers.

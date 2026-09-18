[GROUNDED_BY=spec-only]

# Error semantics matrix

Inputs consumed: `../context/03-requirements.md` (mtime
2026-09-17T15:46, R1..R34 and DP-1..DP-3),
`../context/05-dash-linear-interfaces.md` (2026-09-17T13:16),
`../context/02-actors.md` (2026-09-16T14:21) and
`../context/99-glossary.md` (2026-09-17T14:35). Total rows: 15 — every
condition on the Player-visible interfaces under which an ad
opportunity can fail to be honoured, with the obligations the other
three actors carry for each.

## Scope

In scope:

- Errors on the Player ↔ APS interface — the resolution request and the
  document it returns — including Player-side validation of that
  document against Publisher-declared constraints (R2.3).
- Errors surfaced while rendering an accepted candidate: duration
  overrun, decode failure, mid-render loss, composition conflicts,
  candidate exhaustion inside a pause.
- Errors on the Player ↔ tracking-endpoint interface.

Out of scope:

- The APS ↔ ADS interface, opaque to this specification (R18, OOS-2); a
  failure there reaches the Player only as E1, E2 or E4.
- Primary-content delivery errors (Publisher CDN, ABR, segment retry)
  and auth / DRM / token exchange — DASH baseline, orthogonal to SGAI.
- Requirements with no runtime failure mode: the governance set (R8, R9,
  R10) and VAST independence (R11). Violating one is non-conformance of
  the spec document, not a condition to which a Player response can be
  assigned.

Rows marked **UNDEFINED** flag a condition on which `context/` states
no Player response; the row marked **CONFLICT** flags two statements in
`context/` that prescribe opposite outcomes. Both are gaps to close in
the spec, not behaviour this analysis invents.

## Error matrix

| ID | Error condition | Player response (MUST) | Player response (MAY) | Non-Player actor obligation |
|---|---|---|---|---|
| E1 | The resolution request fails at transport level — DNS unresolvable, TCP refused, TLS handshake failure, timeout before any final status — or returns a final HTTP status other than `200` (4xx / 5xx), including an APS that refuses to answer because a reserved capability parameter was absent. | Treat the attempt as a failed execution and attempt the next overlapping window of the same family; when every window of the family has been attempted, continue with the primary content uninterrupted (R20.1, R1.1, DP-3). | Re-attempt within the interval between the Earliest Resolution Time and the event's `presentationTime`; surface the failure through an implementation-defined API. **UNDEFINED**: `context/` fixes no retry count, backoff or deadline for the resolution request. | Publisher: declare a fallback window where continuity matters, and an `@earliestResolutionTimeOffset` wide enough to leave room before the slot (R20.1); author every window of one family in a single `EventStream` per `Period` (R20.2). APS: tolerate the absence of every reserved capability parameter and produce candidates without any of them (R29.5) — an absent parameter means undetermined, never unsupported (R29.7). |
| E2 | The response is `200` but the body is not a resolution document the Player can parse: malformed XML, unknown root element, or schema-invalid content. | Treat the attempt as a failed execution and continue down the fallback chain as in E1 (R20.1); render nothing from that document and keep the primary content uninterrupted (R1.4, DP-3). | Log the parse or validation failure. | APS: emit a document valid against the DASH 6th edition schema plus the extension points R1.2 admits. A validation procedure that reports such a document valid while skipping its foreign-namespace subtree has not checked the tracking carrier at all (R6.7). |
| E3 | The response is `200` and carries a well-formed resolution document whose **family does not match** the slot that requested it. | Treat it as a failure to resolve and continue down the fallback chain of R20.1; not treat it as a resolution carrying no candidates (R20.4). | Report the family mismatch through an implementation-defined API. | APS: answer the slot that was requested — a document of the wrong family cannot fill the slot whatever it contains, and reading it as an empty resolution would let one misrouted response silence every remaining window (R20.4). |
| E4 | The response is `200` and the document is well-formed and complete but **carries no candidates** — the opportunity resolved to no ads. | Treat the attempt as a failed execution and attempt the next overlapping window of the same family, continuing with the primary content once the family is exhausted (R30, R20.1); not count the attempt as an execution, so an `@executeOnce="true"` event stays executable (R30.2). | Report the opportunity as unfilled rather than failed, through an implementation-defined API. **CONFLICT**: R30 and R20.1 place the empty document on the fallback chain; R20.4's rationale states that a resolution carrying no candidates *"ends the chain"*. The two prescribe opposite outcomes for this row, and the MUST column follows R20.1, which is where the normative criterion sits. | APS: express a no-ads decision as a document carrying no candidates, never as an error response and never as a response without a body (R30.1). ADS: none — no-fill is a legitimate decision, not a failure. |
| E5 | The resolution document arrives after the slot window has elapsed (late ADS decision, late APS conversion). | Not extend the slot past what the cap bounds for that family (R4.3); keep the primary content uninterrupted (DP-3). On an inherited linear replacement slot, honour the base specification's clip semantics — a late start shortens the presentation rather than moving the scheduled end (R4.6). | Discard the document. **UNDEFINED**: `context/` defines late *execution* of an event (`@clip`, `@startWithOffset` — §5.16.4 via `../context/05-dash-linear-interfaces.md`) but states no Player response for a resolution document that lands after the window is over, and no deadline after which a pending response is abandoned. | Publisher: declare an `@earliestResolutionTimeOffset` that gives the APS a usable head start. APS: answer inside the window it was asked in; the APS-to-ADS latency budget is bilateral and outside this specification (R18). |
| E6 | The slot declaration carries no maximum duration, or declares a maximum of zero. | With no maximum declared, present no ads from that slot and continue with the primary content — the absence MUST NOT be read as the base specification's unbounded default (R4.10). With a maximum of zero, the opportunity does not fire (R4.7). | Report the defective declaration through an implementation-defined API. Note: R4.10 is **provisional** in `context/` — it diverges from the base specification's unbounded default (R4.8) and is open with the working group, so a Player author should not read it as settled. | Publisher: declare a maximum duration on every ad slot, linear or non-linear (R4.1). This is a deliberate narrowing of the base specification, which treats an absent maximum as infinity (R4.8). |
| E7 | No presentation option on a candidate is satisfiable: the device renders none of the offered forms, or every offered layout needs more concurrent decoders or compositing surfaces than the device has (R26.3, R27.3). | Skip that candidate and fall through to the next one in document order; continue with the primary content only once every candidate is exhausted (R3.3, R5.3, R5.7, R7.2). Not attempt the next window — a document carrying candidates is not a failed execution (R20.1). | Report the skip through an implementation-defined API. | APS: carry the presentation options as an ordered list whose document order is the preference order (R5.1, R5.5). Neither ADS nor APS is required to hold a device-class matrix (R5.4); a candidate carrying a single option places the suitability call upstream, with the APS or with the ADS that returned one option to it. |
| E8 | A presentation option names a layout the window did not allow, or one outside the ad-type / visual-placement set R12 enumerates (the vocabulary `../context/99-glossary.md` defers to). | Not render that option; move to the next option in document order and skip the candidate when none passes both the device check and the allowed-layouts check (R5.6, R5.7). Check against **the window that served the candidate**, which binds it with its own allowed layouts and its own maximum duration and inherits neither from the window it stands in for (R20.5, R20.6). | Report the rejected layout name. **UNDEFINED**: where the window declared its layouts unrestricted (`../context/02-actors.md`), a name outside the R12 enumeration passes the allowed-layouts check, and `context/` gives the Player no verdict on a layout it cannot map to an enumerated placement. | Publisher: draw allowed-layout names only from the enumerated set — Publisher-private names and IAB values outside it MUST NOT appear (R12.2); for a pause window, name a surface, since the bare `pause` type is not an admissible layout value (R12). APS: emit no form metadata for an ad type or placement outside that set (R12.3). |
| E9 | A candidate's creative carrier is outside the admissible set — not video, image or HTML — or a non-AV asset URL is expressed as `@mimeType` on a path bound by RFC 4337. | Not render a form the device cannot render (R3.3). | Skip the candidate as a non-conformant upstream signal (R15.3) and fall through as in E7. **UNDEFINED**: R15.3 is permissive only. For a carrier outside the admissible set that the device *can* nevertheless render, `context/` states no obligation, so rendering it and skipping it are both unconstrained. | APS + Publisher: every creative carries a mimeType inside the admissible set (R15.2), and non-AV asset URLs travel on one of the DASH-conformant carriers of DR-6, never on an RFC 4337-bound `@mimeType` path (R24.1). |
| E10 | The slot's cap is reached: a candidate's **declared** duration would push the cumulative duration past it, or an accepted candidate's **actual** rendered length exceeds its declared duration. | Where the cap bounds cumulative duration — the non-linear families and linear insertion — stop rendering once the cumulative duration would exceed it, even mid-ad (R4.2, R14.2), enforcing against actual and not declared length ("trim during play", R4.5, R7.5); stop firing the remaining beacons at the trim boundary (R13.3); not extend the slot past what the cap bounds, whatever the ADS metadata or candidate count say (R4.3); convert a candidate's ISO 8601 duration into the cap's timescale, rounding **up**, before comparing, admitting a candidate whose converted duration equals the cap exactly (R4.9); keep the surviving candidates in document order, without re-ordering or deduplicating (R7.4). | Drop a candidate before playback on declared duration alone — "drop before play" (R7.3); accepting it instead defers the case to the trim rule above. Surface the trim through an implementation-defined API. | Publisher: declare the cap on every slot (R4.1). ADS: not required to respect the cap when selecting candidates; a conformance check MUST NOT fail solely on cumulative overflow (R4.4). Cap arithmetic runs on the presentation timeline — an interval in which that timeline does not advance does not accrue, so a form suspended during a pause resumes with the cap it had (R4.11) — and the wall-clock on-screen length is derived from it, never duplicated (R19.3, DP-1.2). A pause slot has no authored duration for the cap to bound (R31.2). |
| E11 | Rendering an accepted candidate fails at runtime: an ad segment returns 4xx / 5xx, a decode error occurs, or the network is lost mid-ad. | Abort that ad and continue playing the primary content uninterrupted (R1.4, DP-3). | Skip to the next candidate in document order or end the break — Player policy, per the interface contracts in `../context/05-dash-linear-interfaces.md`; retry the ad segment per DASH-IF guidance before aborting. | APS: reference ad media reachable for the duration of the slot. |
| E12 | An event scheme URI, extension element or foreign namespace in the primary MPD or in the resolution document is unknown to the Player. | Ignore the unknown construct together with its whole subtree and keep playing the primary content uninterrupted (R1.1, R6.4). | Log the unknown scheme or namespace; ignore the R23 application-level metadata carrier entirely — emitting it and reading it are both optional (R23.1). | Publisher + APS: express every new construct through one of the extension points R1.2 enumerates, whose ignore-if-unknown semantics produce this behaviour on a conforming legacy Player, and never alter pre-existing DASH semantics (R1.3). |
| E13 | A tracking beacon or a click-tracking request fails (transport error, timeout, non-2xx), or a beacon is scheduled for a moment the ad never reaches — past a trim boundary, or after a pause-ad was dismissed on resume. | Keep the ad and the primary content unaffected — a beacon failure is non-fatal and never reaches the viewer (`../context/05-dash-linear-interfaces.md`, interface contracts). Stop firing the remaining beacons at the trim boundary (R13.3) and from the pause-to-play transition onward for a dismissed pause-ad (R16.1, R16.2). Fire each beacon once per candidate that carries it: beacons sharing an `@id`, or the same URL at the same presentation time, fire once **within a candidate**, while the same `@id` in two candidates of one document is two distinct beacons and both fire (R6.5). | Retry the beacon and log the failure; the retry policy is implementation-defined. Report the unfired beacons through an implementation-defined API. | APS: carry beacons as `<Event>` entries in an `EventStream` of scheme `urn:mpeg:dash:event:callback:2015`, timed on the ad's presentation timeline and, for a candidate-level carrier, resolved against that candidate's own presentation (R6.2, R6.6, R13.1); carry the ClickThrough with any click-tracking URLs in the normative carrier (R28.1). ADS: owns which beacons exist and at which relative times (R13); transcription fidelity, and whether a declared ClickThrough travels at all, are APS-to-ADS matters outside this specification (R13.5, R28.3). |
| E14 | The resolution document implies two non-linear forms on screen at the same instant, or a pause begins inside a pause window while an overlay or a linear ad occupies the screen. | Keep at most one non-linear form active at any instant (R22.1): present sequenced forms one after another in the order the document declares (R14.1); during a pause, suspend the overlay and render the pause-ad whatever its presentation surface (R17.1, R21.1), suspend a linear ad and resume it from where it stopped (R17.5), and restore the suspended form on resume only if its window is still open (R17.2, R17.3). In live content, keep the presentation time frozen inside the pause window for the whole pause (R25.1). | Release the resources held by the primary content and by a pre-existing overlay to present a fullscreen pause-ad (R21.1). Report the suspended form through an implementation-defined API. | APS: declare forms as a sequence, never as a concurrent composition (R14.3). Publisher, ADS and APS have no construct that inverts the pause-ad-over-overlay priority (R17.4). Overlapping windows of one family are a declared fallback chain, not a concurrency case (R20.1). |
| E15 | The pause-ad candidates are exhausted while the viewer is still paused, or the pause window was already consumed. | Apply the behaviour the resolution document declares — repeat the sequence, request a new document, or stop — and apply `stop` when the document declares nothing (R32.1); under `request-again`, treat a document carrying no candidates as `stop` for the remainder of that pause (R32.2); return to the primary content immediately on resume, even mid-presentation (R32.3). On a window declared once-per-session, present at most one pause ad for it and leave a later qualifying pause uninterrupted (R34.2), counting the window consumed when a pause ad **begins rendering** and not when the pause occurs (R34.3). R5.3's fall-through to primary content does not apply here: the primary content is paused. | Report the applied behaviour through an implementation-defined API. | APS: declare which of the three behaviours applies on every pause resolution document — the declaration is the APS's and not the Publisher's (R32.1). Publisher: declare the once-per-session bound where wanted, optionally (R34.1); request the `PlayList` metric through the `Metrics` element on content carrying pause windows, or nothing obliges anyone to collect what R33.2 derives (R33.4). |

## Notes

### Fall-through definition

"Fall through to primary content uninterrupted" means: no visible
artefact — no freeze, no blank slate, no error overlay unless the
application explicitly opted in; no tracking beacon fired for the
opportunity that failed; and primary-content playback continuing on its
own timeline. The viewer cannot tell that an ad opportunity existed.
This is the floor DP-3 sets, and it is the base specification's own rule
for its execution model: *"A failed execution results in smooth
continued playback of the main media presentation"* (§5.16.2.2.6, via
R30).

Two other moves are distinct from it. **Window-level** fall-through (E1,
E2, E3, E4) advances to the next overlapping window of the same family
and reaches the primary content only once the family is exhausted
(R20.1). **Candidate-level** fall-through (E7, E8, E9) advances to the
next candidate inside the document already obtained and reaches the
primary content only once the candidates are exhausted (R5.3) — never
the next window, because a document carrying candidates is not a failed
execution.

### Order of precedence

When several conditions arise on the same exchange, the Player applies
them in this order:

1. **Transport** (E1) — no document, so nothing downstream applies.
2. **Resolution-document level** (E2, E3, E4, E5) — the document is
   unusable, misrouted, empty, or late. All but E5 put the Player on the
   fallback chain of R20.1.
3. **Constraint surfacing** (E6, E8, E9, and E10's drop-before-play) —
   the window's own declarations validated before anything is rendered;
   E6 precedes every other row, because a slot with no declared cap
   yields no ads at all.
4. **Per-candidate decode-time** (E7, E11) — what the device can
   actually satisfy and what the ad CDN actually delivers.
5. **Per-candidate playback-time** (E10's trim-during-play, E14, E15) —
   the cap enforced against actual length, the single-active-form bound,
   and exhaustion inside a pause.
6. **Tracking failures** (E13) — non-fatal throughout; they never abort
   an ad and never reach the viewer.

E12 is orthogonal: an unknown construct is ignored wherever it appears,
at any level, and never advances the Player to the next step.

### Guarantees by actor

**Publisher.** Declares in the MPD, not by runtime inference (R2.1): a
maximum duration on every slot (R4.1), allowed layouts drawn from the
enumerated set (R12.2), the opportunity windows including any fallback
chain — one `EventStream` per family per `Period` (R20.2) — any
once-per-session bound on a pause window (R34.1), and the `PlayList`
metric request where pause windows exist (R33.4). An authoring-time
actor: every unmet Publisher obligation above degrades into a
Player-side skip, never into interrupted playback.

**ADS.** Decides which ads, how many and in what order, and owns the
tracking schedule (R13). Guarantees neither the slot cap (R4.4) nor a
device-capability view (R5.4); no-fill is a legitimate outcome, not a
failure (R30). Nothing it emits is checked by this matrix — its output
reaches the Player only through the APS.

**APS.** The only non-Player actor whose output this specification
checks at runtime. Guarantees: a document that parses and validates,
tracking subtree included (E2, R6.7); a document of the family the slot
asked for (R20.4); a document carrying no candidates for an unfilled
opportunity rather than an error (R30.1); presentation options as an
ordered list in preference order (R5.1); creatives inside the admissible
carrier set on DASH-conformant carriers (R15.2, R24.1); form metadata
only for the enumerated ad types (R12.3); beacons as callback events on
the ad's presentation timeline (R6.2, R13.1); the ClickThrough with any
click-tracking URLs in the normative carrier (R28.1); an exhaustion
behaviour declared on every pause document (R32.1); and an answer that
depends on no reserved capability parameter (R29.5).

**Player.** The enforcer. Guarantees that primary-content playback
survives every row of this matrix (R1.1, R1.4, DP-3); that the
declarations of the window that served a candidate are validated before
anything is rendered (R2.3, R20.5); that the cap holds against actual
length even mid-ad (R4.2, R4.5); that document order is honoured,
dropping allowed and re-ordering not (R7.1, R7.4); that no form its
device cannot render reaches the screen (R3.3); that at most one
non-linear form is active at any instant (R22.1); that a pause-ad is
dismissed the instant the viewer resumes (R16.1, R32.3); and that a
defined behaviour exists for every device class and opportunity type
(R3.2).

### Surfacing errors to the application layer

Everything in the "Player response (MAY)" column that reports, logs or
exposes a condition is non-normative: this specification defines neither
event names, nor payloads, nor delivery mechanism, and a Player that
exposes nothing is conformant. Chapter 9 SHOULD give guidance on what is
worth surfacing — the unfilled opportunity (E4) versus failed resolution
(E1, E2, E3) distinction carries the most operational value, and the
misrouted document (E3) is the one an operator cannot diagnose from the
viewer's screen — while leaving the API shape to implementers.

One boundary is normative rather than a matter of API shape: an error
overlay is a visible artefact, so rendering one on any row of this
matrix breaks the fall-through guarantee unless the application
explicitly opted in.

## References

- [`../context/02-actors.md`](../context/02-actors.md) — actor
  definitions and the boundary summary behind the obligations column.
- [`../context/03-requirements.md`](../context/03-requirements.md) —
  R1..R34 and the design principles DP-1 through DP-3.
- [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
  — interface contracts table, linear message flow, VAST → ListMPD edge
  cases.
- [`../context/99-glossary.md`](../context/99-glossary.md) —
  terminology; the edition-scoped ad-type and placement vocabulary is
  R12 of `03-requirements.md`, to which the glossary defers.

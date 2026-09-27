[GROUNDED_BY=spec-only]

# Error semantics matrix

Inputs consumed: `../context/03-requirements.md` (mtime 2026-09-26T21:52,
R1..R40 and DP-1..DP-3), `../context/05-dash-linear-interfaces.md`
(2026-09-26T15:44), `../context/02-actors.md` (2026-09-26T21:48) and
`../context/99-glossary.md` (2026-09-26T10:49). Total rows: 15 — every
condition on the Player-visible interfaces under which an ad opportunity
can fail to be honoured, with the obligations the other three actors carry
for each. Clause numbers of the base standard appear only as `context/`
quotes them.

## Scope

In scope:

- Errors on the Player ↔ APS interface — the resolution request and the
  document it returns — including Player-side validation of that document
  against Publisher-declared constraints (R2.3, R38.5).
- Errors surfaced while rendering an accepted candidate: duration overrun,
  decode failure, mid-render loss, composition conflicts with other forms
  and with alternative presentations, candidate exhaustion inside a pause.
- Errors on the Player ↔ tracking-endpoint interface.

Out of scope:

- The APS ↔ ADS interface, opaque to this specification (R18). An ADS error
  reaches the Player only as an HTTP error or a document with no candidates
  (E1, E4), per the `<Error>` row of the VAST mapping in
  `../context/05-dash-linear-interfaces.md`.
- Primary-content delivery errors (Publisher CDN, ABR, segment retry) and
  auth / DRM / token exchange — DASH baseline, orthogonal to SGAI.
- Requirements with no runtime failure mode: backward compatibility as a
  property of the document (R1.1–R1.3), governance (R8, R9, R10), VAST
  independence (R11), base-first precedence (R1.5) and the carrier of the
  R40 relation (R40.7, R40.8). Violating one is non-conformance of the spec
  document, not a condition a Player response can be assigned to.
- Viewer dismissal of a slot (R35): an outcome of the presentation, not a
  failure of it (R35.6). On overlay and pause it is granted by the APS
  (R35.1); on a linear slot the base specification's skip declaration and
  its default govern (R35.8). It appears here only where it bounds beacon
  firing (E13).

Rows marked **UNDEFINED** flag a condition on which `context/` states no
Player response. They are gaps to close in the spec, not behaviour this
analysis invents.

## Error matrix

| ID | Error condition | Player response (MUST) | Player response (MAY) | Non-Player actor obligation |
|---|---|---|---|---|
| E1 | The resolution request fails at transport level — DNS unresolvable, TCP refused, TLS handshake failure, timeout before any final status — or returns a final HTTP status other than `200` (4xx / 5xx), including an APS that refuses to answer because a reserved capability parameter was absent. | Treat the attempt as a failed execution and attempt the next overlapping window of the same family (R20.1, R20.3); once every window of the family has been attempted, continue with the primary content uninterrupted (R20.1, DP-3). On a window declaring supersede that presents no ad, execute the inherited linear events it stands in for with their base semantics, late-execution rules included (R40.3). | Re-attempt within the interval between the earliest resolution time and the opportunity; surface the failure through an implementation-defined API. **UNDEFINED**: `context/` fixes no retry count, backoff or deadline for the resolution request. | Publisher: declare a fallback window where continuity matters (R20.1); author every window of one family in a single `EventStream` per `Period` (R20.2). APS: tolerate the absence of every reserved capability parameter and produce candidates without any (R29.5) — absence means undetermined, never unsupported (R29.7). |
| E2 | The response is `200` but the body is not a resolution document the Player can parse: malformed XML, unknown root element, or schema-invalid content. | Treat the attempt as a failed execution and continue down the fallback chain as in E1, supersede case included (R20.1, R40.3); render nothing from that document and keep the primary content uninterrupted (R1.4, DP-3). | Log the parse or validation failure. | APS: emit a document valid against the DASH 6th edition schema plus the extension points R1.2 admits. A validation that reports such a document valid while skipping its foreign-namespace subtree has not checked the tracking carrier (R6.7). |
| E3 | The response is `200` and carries a well-formed resolution document whose **family does not match** the slot that requested it. | Treat it as a failed execution, present none of its candidates in the slot, and continue down the R20.1 chain to the next overlapping window of the slot's family (R20.4), even when its candidates are renderable on the device. | Report the family mismatch through an implementation-defined API. | APS: answer the slot that was requested; a document of the wrong family cannot fill it whatever it contains (R20.4). |
| E4 | The response is `200` and the document is well-formed and complete but **carries no candidates** — the opportunity resolved to no ads. | Treat the attempt as a failed execution and attempt the next overlapping window of the family, ending on the primary content — or, on a supersede window, on the linear events it stands in for (R40.3) — once the family is exhausted (R30, R20.1). Not count the attempt as an execution: an `@executeOnce="true"` event stays executable (R30.2) and a once-per-session pause window stays available (R34.3). | Report the opportunity as unfilled rather than failed. | APS: express a no-ads decision as a document carrying no candidates, never as an error response nor a response without a body (R30.1). ADS: none — no-fill is a legitimate decision. |
| E5 | The resolution arrives late — after the slot window has elapsed — or a resolution obtained ahead of time has expired when the opportunity fires. | Not extend the slot past what the cap bounds for its family (R4.3); on an inherited linear replacement slot, a late start shortens the presentation rather than moving the scheduled end unless the event declares otherwise (R4.6). For an early resolution: check at firing whether it is still usable; if not, request a new one and present nothing from the expired one (R36.5); a re-resolution with no usable candidate is an empty resolution (R30) and never falls back on the expired one (R36.6). | Resolve early within the offset — declared, or 60 s by default — as a permission, never an obligation (R36.1, R36.7). Discard a document that lands after the window. **UNDEFINED**: `context/` states no Player response for a non-linear resolution document that lands after its window is over, and no deadline after which a pending request is abandoned. | Publisher: optionally declare how far ahead an overlay or pause window may be resolved, zero meaning only at firing (R36.1); the Player MUST NOT resolve earlier (R36.2, R36.3). APS: declare how long an early resolution remains usable, defaulting to the window's length (R36.4). The APS-to-ADS latency budget is bilateral (R18). |
| E6 | An overlay or pause slot declaration carries no maximum duration, or any slot declares a maximum of zero. | With no maximum on an overlay or pause slot, present no ads from it and continue with the primary content; the absence MUST NOT be read as unbounded (R4.10). With a maximum of zero, the opportunity does not fire (R4.7). An inherited linear event with no maximum is **not** this condition: execute it with its base semantics, an absent `@maxDuration` being infinity (R4.8, R4.10). | Report the defective declaration through an implementation-defined API. | Publisher: declare a maximum on every overlay and pause slot; on an inherited linear event the base `@maxDuration` MAY be omitted (R4.1, R4.8). Non-linear advertising with no fixed end is a chain of bounded slots (R4.10). |
| E7 | No presentation option on a candidate is satisfiable on the device: none of the offered forms renders, or every offered layout needs more concurrent decoders or compositing surfaces than the device has (R26.3, R27.3). | Skip that candidate and fall through to the next in document order (R3.3, R5.3, R5.7); the drop is not a rearrangement (R7.2). When the candidates are exhausted: if at least one was rendered, continue with the primary content (R5.3); if none was, the attempt produced no ad and is a failed execution — attempt the next overlapping window of the family, ending on the primary content once the family is exhausted (R20.1, DP-3), or on a supersede window execute the inherited linear events it stands in for (R40.3). A pause that yields no renderable candidate leaves a once-per-session window available (R34.3). | Report the skip through an implementation-defined API. | APS: carry the options as an ordered list whose document order is the preference order (R5.1, R5.5). Neither ADS nor APS is required to hold a device-class matrix (R5.4); a single-option candidate places the suitability call upstream (R5). |
| E8 | A presentation option names an **unknown or inadmissible layout**: a token outside the closed list of R12.2, a Publisher-private name, bare `squeezeback` or `pause`, a token the serving window did not allow, a token of another family on a window that declares none, or a `custom` layout the Player does not support or whose rectangle extends beyond the slot's region. | Not render that option; move to the next option in document order, and skip the candidate when none passes both the device and admitted-layouts checks, exhaustion then following E7 (R5.6, R5.7, R38.5) — forwarding the set to the APS does not remove the check. A window declaring no allowed layouts admits only its own family's R12 tokens and never `custom` (R38.1). Treat a `custom` option as not renderable when unsupported or outside the region, or the viewport when none is declared (R39.5). Check against **the window that served the candidate**, not the one it stands in for (R20.5, R20.6). | Report the rejected layout name. | Publisher: allowed-layout names only from the closed token list, `custom` only by listing it (R12.2, R39.2). APS: no option outside the set received or, with none received, outside the family's set (R38.4), nor outside the enumeration (R12.3); a `custom` rectangle inside the received region (R39.4) — the only Publisher-declared constraints R2.2 binds the APS to. |
| E9 | A candidate's creative carrier is outside the admissible set — not video, image or HTML — or a non-AV asset URL is expressed as `@mimeType` on a path bound by RFC 4337. | Not render a form the device cannot render (R3.3). | Skip the candidate as a non-conformant upstream signal (R15.3) and fall through as in E7. **UNDEFINED**: R15.3 is permissive only; for an inadmissible carrier the device *can* render, rendering and skipping are both unconstrained. | APS + Publisher: every creative carries a mimeType inside the admissible set (R15.2); non-AV asset URLs travel on a DR-6 carrier, never on an RFC 4337-bound `@mimeType` path (R24.1). |
| E10 | The slot's cap is reached: a candidate's **declared** duration would push the cumulative duration past it, or an accepted candidate's **actual** rendered length exceeds its declared duration. | Where the cap bounds cumulative duration — the overlay family and linear insertion — stop rendering once it would be exceeded, even mid-ad (R4.2, R14.2), against actual length (R4.5, R7.5); stop the remaining beacons at the trim boundary (R13.3); not extend the slot whatever the ADS metadata say (R4.3); convert the ISO 8601 duration to the cap's timescale rounding **up**, admitting an exact match (R4.9); accrue nothing while the presentation timeline does not advance (R4.11); keep the survivors in document order (R7.4). | Drop a candidate before playback on declared duration alone (R7.3). Surface the trim through an implementation-defined API. | Publisher: declare the cap on every overlay and pause slot (R4.1); an inherited linear event without one has no cap to reach (R4.8). ADS + APS: not required to respect the cap, which R2.2 leaves to the Player (R2.3); a conformance check MUST NOT fail solely on cumulative overflow (R4.4). A pause slot has no authored duration for the cap to bound (R31.2). Wall-clock length is derived, never duplicated (R19.3, DP-1.2). |
| E11 | Rendering an accepted candidate fails at runtime: an ad segment returns 4xx / 5xx, a decode error occurs, or the network is lost mid-ad. | Abort that ad; primary-content playback is never broken (R1.4, DP-3). If the window has thereby produced no ad, the attempt is a failed execution and the R20.1 chain applies as in E7, supersede case included (R20.1, R40.3); on the linear family the base condition is *"The playback of the alternative presentation cannot start"* (§5.16.2.2.6, as R20.1 quotes it). | Skip to the next candidate or end the break, per Player policy (interface contracts, `../context/05-dash-linear-interfaces.md`); retry the ad segment before aborting. **UNDEFINED**: `context/` does not say whether a candidate that began rendering and then failed counts as an ad produced, which decides between continuing with the primary content and attempting the next window. | APS: reference ad media reachable for the duration of the slot. |
| E12 | An event scheme URI, extension element or foreign namespace in the primary MPD or in the resolution document is unknown to the Player. | Ignore the unknown construct with its whole subtree and keep playing the primary content uninterrupted, under the base rules for unrecognised elements and attributes (§5.2.1, on which R1.1 relies); on tracking-related extension elements, safely ignore unknown namespaces (R6.4). | Log it; ignore the R23 metadata carrier entirely — emitting and reading it are both optional (R23.1). | Publisher + APS: every new construct at an extension point R1.2 enumerates, whose removal leaves a valid MPD that plays uninterrupted (R1.1), never altering pre-existing DASH semantics (R1.3). |
| E13 | A tracking beacon or click-tracking request fails (transport error, timeout, non-2xx), or a beacon is scheduled for a moment the ad never reaches — past a trim boundary, after a pause-ad was dismissed on resume, or after the viewer dismissed the slot. | Keep the ad and the primary content unaffected: a beacon failure is non-fatal and never reaches the viewer (interface contracts, `../context/05-dash-linear-interfaces.md`). Stop firing at the trim boundary (R13.3), from the pause-to-play transition for a dismissed pause-ad (R16.2), and at a viewer dismissal, firing those scheduled before it (R35.6). Fire each beacon once **within a candidate** of a non-linear document, the same `@id` in two candidates being two beacons; on a `ListMPD`, once per `@id` within its `@schemeIdUri` / `@value` over the whole presentation, merged sub-MPD streams included (R6.5). | Retry and log; the retry policy is implementation-defined. | APS: beacons as callback events on the ad's presentation timeline, resolved against the candidate's own presentation (R6.2, R6.6, R13.1); ClickThrough with its click-tracking in the normative carrier (R28.1). ADS: owns the schedule (R13); transcription fidelity is an APS-to-ADS matter (R13.5, R28.3). |
| E14 | Two forms would share the screen: the resolution document implies two non-linear forms at once; a pause begins inside a pause window while an overlay or a linear ad occupies the screen; or an alternative presentation begins while a non-linear window is presenting. | Keep at most one non-linear form active (R22.1), sequenced forms in document order (R14.1). During a pause: suspend the overlay and render the pause-ad whatever its surface (R17.1, R21.1); suspend a linear ad and resume it where it stopped, when the pause window applies to the presentation being output — declared in the linear ad's own `MPD` or on top in the triggering one (R17.5, R40.5, R40.6); restore the overlay on resume only if its window is still open (R17.2, R17.3); in live content keep presentation time frozen inside the pause window (R25.1); resume the primary content from the suspended position (R37.2). On an alternative presentation: with no relation declared, end the form there and present nothing further from the window, executing the linear event with its base semantics (R40.4); on top, keep presenting composited over it within R3, R5 and R22 (R40.5); windows in the alternative presentation's own `MPD` are that presentation's (R40.6). | Release the primary content's and a pre-existing overlay's resources for a fullscreen pause-ad (R21.1), by any pause mechanism that restores position (R37.1). | APS: forms as a sequence, never a concurrent composition (R14.3). No actor has a construct that inverts pause-ad-over-overlay priority (R17.4). Publisher: at most one relation per window (R40.1); a non-linear ad during an alternative presentation is declared in that presentation's `MPD` or by an on-top window (R40.2). Overlapping same-family windows are a fallback chain, not concurrency (R20.1). |
| E15 | The pause-ad candidates are exhausted while the viewer is still paused, or the pause window was already consumed. | Apply the declared behaviour — repeat, request again, or stop — and `stop` when none is declared (R32.1); under `request-again`, a document with no candidates is `stop` for the rest of that pause (R32.2); return to the primary content immediately on resume (R32.3). On a once-per-session window, present at most one pause ad and leave later pauses uninterrupted (R34.2), the window consumed when a pause ad **begins rendering**, and left available by a pause that resolves to no renderable candidate (R34.3). R5.3's fall-through does not apply: the primary content is paused (R32). | Report the applied behaviour through an implementation-defined API. | APS: declare the behaviour on every pause document (R32.1). Publisher: optionally declare once-per-session (R34.1); request the `PlayList` metric through `Metrics` where pause windows exist (R33.4). |

## Notes

### Fall-through definition

"Fall through to primary content uninterrupted" means: no visible artefact
— no freeze, no blank slate, no error overlay unless the application
explicitly opted in; no tracking beacon fired for the opportunity that
failed; primary-content playback continuing on its own timeline. This is
the floor DP-3 sets, which extends the base specification's own rule as
`context/` quotes it: *"A failed execution results in smooth continued
playback of the main media presentation"* (§5.16.2.2.6).

Three moves are distinct from it. **Window-level** fall-through (E1–E4)
advances to the next overlapping window of the same family and reaches the
primary content only once the family is exhausted (R20.1).
**Candidate-level** fall-through (E7, E8, E9) advances to the next
candidate in the document already obtained. Its exhaustion ends on the
primary content only if at least one candidate was rendered; if none was,
the window produced no ad and window-level fall-through takes over
(R5.3, R20.1). DP-3 states the principle: an opportunity is given up
only after every way of filling it that the manifest declares has been
tried.
**Supersede fall-back** applies when a window declaring supersede presents
no ad by either route: what continues is the inherited linear events it
stood in for, with their base semantics (R40.3).

### Order of precedence

1. **Transport** (E1) — no document, so nothing downstream applies.
2. **Resolution-document level** (E2, E3, E4, E5) — unusable, misrouted,
   empty, late or expired. E2–E4 put the Player on the R20.1 chain; so
   do E7 and E11 when the window ends with no ad rendered.
3. **Constraint surfacing** (E6, E8, E9, E10 drop-before-play) — the
   serving window's declarations validated before rendering; E6 first,
   because an overlay or pause slot with no cap yields no ads at all.
4. **Per-candidate decode-time** (E7, E11).
5. **Per-candidate playback-time** (E10 trim-during-play, E14, E15).
6. **Tracking failures** (E13) — non-fatal; never abort an ad.

E12 is orthogonal: an unknown construct is ignored wherever it appears.
The supersede fall-back (R40.3) runs after steps 1–4 have left the window
with no ad.

### Guarantees by actor

**Publisher.** Declares in the MPD, never left to runtime inference
(R2.1): a cap on every overlay and pause slot (R4.1), allowed layouts from
the closed token list and any custom region (R12.2, R39.2), the windows
including any fallback chain (R20.2), any relation to overlapped linear
events (R40.1, R40.2), any early-resolution offset (R36.1), any
once-per-session bound (R34.1), and the `PlayList` metric request (R33.4).
Every unmet Publisher obligation degrades into a Player-side skip, never
into interrupted playback.

**ADS.** Decides which ads, how many and in what order, and owns the
tracking schedule (R13). Bound to enforce no Publisher-declared constraint (R2.2):
guarantees neither the cap (R4.4) nor a device view (R5.4); no-fill is legitimate (R30). Its output reaches the Player
only through the APS.

**APS.** The only non-Player actor whose output is checked at runtime: a
parseable, valid document, tracking subtree included (R6.7); the requested
family (R20.4); no candidates for no-fill (R30.1); ordered options (R5.1);
admissible carriers (R15.2, R24.1); layouts within the enumeration and the
admitted set (R12.3, R38.4), `custom` rectangles within the region
(R39.4) — the only Publisher-declared constraints it is bound to (R2.2),
and the Player checks them again (R38.5, R39.5); callback-event beacons (R6.2, R13.1); the ClickThrough carrier
(R28.1); a pause exhaustion behaviour (R32.1); a dismissal declaration on
every overlay and pause slot (R35.1); a usability period for early
resolutions (R36.4); and no dependence on capability parameters (R29.5).

**Player.** The enforcer: primary content survives every row (R1.4,
DP-3); the serving window's declarations are validated before rendering
(R2.3, R20.5, R38.5); the cap holds against actual length (R4.2, R4.5);
document order is honoured, never re-ordered or deduplicated
(R7.1, R7.4); no unrenderable form reaches the
screen (R3.3); at most one non-linear form is active (R22.1); a non-linear
form never overlaps an alternative presentation undeclared (R40.4); a
window that yields no ad hands over to the next window of its family (R20.1), and a
superseded linear break still runs when the window yields no ad (R40.3); a
pause-ad goes the instant the viewer resumes (R16.1, R32.3); an expired
resolution is never presented (R36.5); a linear slot's skippability is the
base specification's (R35.8); and every device class and opportunity type
has a defined behaviour (R3.2).

### Surfacing errors to the application layer

Everything in the MAY column that reports, logs or exposes a condition is
non-normative: no event names, payloads or delivery mechanism are defined,
and a Player that exposes nothing is conformant. Chapter 9 SHOULD give
guidance — the unfilled (E4) versus failed (E1, E2, E3) distinction
carries the most operational value, and the misrouted document (E3) is
the one an operator cannot diagnose from the screen — while leaving the
API shape to implementers. One boundary is normative: an error overlay is
a visible artefact, so rendering one breaks the fall-through guarantee
unless the application explicitly opted in.

## References

- [`../context/02-actors.md`](../context/02-actors.md) — actor definitions
  and boundary summary.
- [`../context/03-requirements.md`](../context/03-requirements.md) —
  R1..R40 and DP-1..DP-3.
- [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
  — interface contracts, linear message flow, VAST → ListMPD edge cases.
- [`../context/99-glossary.md`](../context/99-glossary.md) — terminology;
  the ad-type and placement vocabulary is R12, to which the glossary
  defers.

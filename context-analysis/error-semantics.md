[GROUNDED_BY=spec-only]

# Error semantics matrix

Inputs consumed: `../context/03-requirements.md` (mtime
2026-09-26T10:47, R1..R40 and DP-1..DP-3),
`../context/05-dash-linear-interfaces.md` (2026-09-18T16:15),
`../context/02-actors.md` (2026-09-25T19:49) and
`../context/99-glossary.md` (2026-09-26T10:49). Total rows: 15 — every
condition on the Player-visible interfaces under which an ad
opportunity can fail to be honoured, with the obligations the other
three actors carry for each.

## Scope

In scope:

- Errors on the Player ↔ APS interface — the resolution request and the
  document it returns — including Player-side validation of that
  document against Publisher-declared constraints (R2.3, R38.5).
- Errors surfaced while rendering an accepted candidate: duration
  overrun, decode failure, mid-render loss, composition conflicts with
  other forms and with alternative presentations, candidate exhaustion
  inside a pause.
- Errors on the Player ↔ tracking-endpoint interface.

Out of scope:

- The APS ↔ ADS interface, opaque to this specification (R18); a
  failure there reaches the Player only as E1, E2 or E4.
- Primary-content delivery errors (Publisher CDN, ABR, segment retry)
  and auth / DRM / token exchange — DASH baseline, orthogonal to SGAI.
- Requirements with no runtime failure mode: backward compatibility as
  a property of the document (R1.1–R1.3), the governance set (R8, R9,
  R10), VAST independence (R11), base-first precedence (R1.5) and the
  carrier of the R40 relation (R40.7, R40.8). Violating one is
  non-conformance of the spec document, not a condition to which a
  Player response can be assigned.
- Viewer dismissal of a slot (R35), including the base specification's
  own skip declaration on a linear event (R35.8): an outcome of the
  presentation, not a failure of it (R35.6). It appears here only where
  it bounds beacon firing (E13).

Rows marked **UNDEFINED** flag a condition on which `context/` states
no Player response. They are gaps to close in the spec, not behaviour
this analysis invents.

## Error matrix

| ID | Error condition | Player response (MUST) | Player response (MAY) | Non-Player actor obligation |
|---|---|---|---|---|
| E1 | The resolution request fails at transport level — DNS unresolvable, TCP refused, TLS handshake failure, timeout before any final status — or returns a final HTTP status other than `200` (4xx / 5xx), including an APS that refuses to answer because a reserved capability parameter was absent. | Treat the attempt as a failed execution and attempt the next overlapping window of the same family; when every window of the family has been attempted, continue with the primary content uninterrupted (R20.1, DP-3). When the window declares supersede and presents no ad, execute the inherited linear events it stands in for with their base semantics, including the base rules for a late execution (R40.3). | Re-attempt within the interval between the earliest resolution time and the opportunity; surface the failure through an implementation-defined API. **UNDEFINED**: `context/` fixes no retry count, backoff or deadline for the resolution request. | Publisher: declare a fallback window where continuity matters (R20.1); author every window of one family in a single `EventStream` per `Period` (R20.2). APS: tolerate the absence of every reserved capability parameter and produce candidates without any of them (R29.5) — an absent parameter means undetermined, never unsupported (R29.7). |
| E2 | The response is `200` but the body is not a resolution document the Player can parse: malformed XML, unknown root element, or schema-invalid content. | Treat the attempt as a failed execution and continue down the fallback chain as in E1, including the supersede case (R20.1, R40.3); render nothing from that document and keep the primary content uninterrupted (R1.4, DP-3). | Log the parse or validation failure. | APS: emit a document valid against the DASH 6th edition schema plus the extension points R1.2 admits. A validation procedure that reports such a document valid while skipping its foreign-namespace subtree has not checked the tracking carrier at all (R6.7). |
| E3 | The response is `200` and carries a well-formed resolution document whose **family does not match** the slot that requested it. | Treat it as a failed execution, present none of its candidates in the slot, and continue down the chain of R20.1 to the next overlapping window of the slot's family (R20.4) — the exception to "a document carrying candidates is not a failed execution". | Report the family mismatch through an implementation-defined API. | APS: answer the slot that was requested — a document of the wrong family cannot fill the slot whatever it contains (R20.4). |
| E4 | The response is `200` and the document is well-formed and complete but **carries no candidates** — the opportunity resolved to no ads. | Treat the attempt as a failed execution and attempt the next overlapping window of the same family, continuing with the primary content — or, on a supersede window, with the linear events it stands in for (R40.3) — once the family is exhausted (R30, R20.1); not count the attempt as an execution, so an `@executeOnce="true"` event stays executable (R30.2) and a once-per-session pause window stays available (R34.3). | Report the opportunity as unfilled rather than failed. | APS: express a no-ads decision as a document carrying no candidates, never as an error response and never as a response without a body (R30.1). ADS: none — no-fill is a legitimate decision, not a failure. |
| E5 | The resolution arrives late — after the slot window has elapsed — or a resolution obtained ahead of time has expired when the opportunity fires. | Not extend the slot past what the cap bounds for that family (R4.3); on an inherited linear replacement slot, a late start shortens the presentation rather than moving the scheduled end unless the event declares otherwise (R4.6). For an early resolution: check at firing whether it is still usable; if not, request a new one and present nothing from the expired one (R36.5); a re-resolution with no usable candidate is an empty resolution (R30) and never falls back on the expired one (R36.6). | Resolve early within the offset — declared, or 60 s by default — as a permission, never an obligation (R36.1, R36.7). Discard a document that lands after the window. **UNDEFINED**: `context/` states no Player response for a non-linear resolution document that lands after its window is over, and no deadline after which a pending request is abandoned. | Publisher: optionally declare how far ahead an overlay or pause window may be resolved, zero meaning only at firing (R36.1); the Player MUST NOT resolve earlier (R36.2, R36.3). APS: declare how long an early resolution remains usable, defaulting to the window's length (R36.4); the APS-to-ADS latency budget is bilateral (R18). |
| E6 | An overlay or pause slot declaration carries no maximum duration, or any slot declares a maximum of zero. | With no maximum on an overlay or pause slot, present no ads from that slot and continue with the primary content — the absence MUST NOT be read as an unbounded default (R4.10). With a maximum of zero, the opportunity does not fire (R4.7). An inherited linear event with no maximum is **not** this condition: execute it with its base semantics, an absent `@maxDuration` being infinity (R4.8, R4.10). | Report the defective declaration through an implementation-defined API. | Publisher: declare a maximum duration on every overlay and pause slot; on an inherited linear event the base `@maxDuration` MAY be omitted (R4.1, R4.8). Non-linear advertising with no fixed end is a chain of bounded slots (R4.10). |
| E7 | No presentation option on a candidate is satisfiable on the device: none of the offered forms renders, or every offered layout needs more concurrent decoders or compositing surfaces than the device has (R26.3, R27.3). | Skip that candidate and fall through to the next one in document order; continue with the primary content only once every candidate is exhausted (R3.3, R5.3, R5.7, R7.2). Not attempt the next window — a document carrying candidates is not a failed execution (R20.1). On a supersede window whose candidates the device can render none of, execute the inherited linear events it stands in for (R40.3). | Report the skip through an implementation-defined API. | APS: carry the presentation options as an ordered list whose document order is the preference order (R5.1, R5.5). Neither ADS nor APS is required to hold a device-class matrix (R5.4); a single-option candidate places the suitability call upstream. |
| E8 | A presentation option names an **unknown or inadmissible layout**: a token outside the closed list of R12.2, a Publisher-private name, bare `squeezeback` or `pause`, a token the serving window did not allow, a token of another family on a window that declares none, or a `custom` layout the Player does not support or whose rectangle extends beyond the slot's region. | Not render that option; move to the next option in document order and skip the candidate when none passes both the device and admitted-layouts checks (R5.6, R5.7, R38.5) — forwarding the set to the APS does not remove the check. A window that declares no allowed layouts admits only its own family's R12 tokens and never `custom` (R38.1). Treat a `custom` option as not renderable when unsupported or outside the region, or the viewport when none is declared (R39.5). Check against **the window that served the candidate**, not the window it stands in for (R20.5, R20.6). | Report the rejected layout name. | Publisher: draw allowed-layout names only from the closed token list, `custom` included only by listing it (R12.2, R39.2). APS: no option outside the set received or, with none received, outside the family's set (R38.4), nor outside the enumeration (R12.3); a `custom` rectangle inside the received region (R39.4). |
| E9 | A candidate's creative carrier is outside the admissible set — not video, image or HTML — or a non-AV asset URL is expressed as `@mimeType` on a path bound by RFC 4337. | Not render a form the device cannot render (R3.3). | Skip the candidate as a non-conformant upstream signal (R15.3) and fall through as in E7. **UNDEFINED**: R15.3 is permissive only; for an inadmissible carrier the device *can* render, rendering and skipping are both unconstrained. | APS + Publisher: every creative carries a mimeType inside the admissible set (R15.2); non-AV asset URLs travel on a DR-6 carrier, never on an RFC 4337-bound `@mimeType` path (R24.1). |
| E10 | The slot's cap is reached: a candidate's **declared** duration would push the cumulative duration past it, or an accepted candidate's **actual** rendered length exceeds its declared duration. | Where the cap bounds cumulative duration — non-linear families and linear insertion — stop rendering once it would be exceeded, even mid-ad (R4.2, R14.2), against actual length (R4.5, R7.5); stop the remaining beacons at the trim boundary (R13.3); not extend the slot whatever the ADS metadata say (R4.3); convert the ISO 8601 duration to the cap's timescale rounding **up**, admitting an exact match (R4.9); accrue nothing while the presentation timeline does not advance (R4.11); keep the survivors in document order (R7.4). | Drop a candidate before playback on declared duration alone (R7.3). Surface the trim through an implementation-defined API. | Publisher: declare the cap on every overlay and pause slot (R4.1); an inherited linear event without one has no cap to reach (R4.8). ADS: not required to respect the cap; a conformance check MUST NOT fail solely on cumulative overflow (R4.4). The wall-clock length is derived from the presentation-timeline duration, never duplicated (R19.3, DP-1.2). A pause slot has no authored duration for the cap to bound (R31.2). |
| E11 | Rendering an accepted candidate fails at runtime: an ad segment returns 4xx / 5xx, a decode error occurs, or the network is lost mid-ad. | Abort that ad and continue playing the primary content uninterrupted (R1.4, DP-3). | Skip to the next candidate or end the break — Player policy per the interface contracts in `../context/05-dash-linear-interfaces.md`; retry the ad segment before aborting. | APS: reference ad media reachable for the duration of the slot. |
| E12 | An event scheme URI, extension element or foreign namespace in the primary MPD or in the resolution document is unknown to the Player. | Ignore the unknown construct with its whole subtree and keep playing the primary content uninterrupted, under the base rules for unrecognised elements and attributes (§5.2.1, on which R1.1 relies); on tracking-related extension elements, safely ignore unknown namespaces (R6.4). | Log it; ignore the R23 metadata carrier entirely — emitting and reading it are both optional (R23.1). | Publisher + APS: every new construct placed at an extension point R1.2 enumerates, whose removal leaves a valid MPD that plays uninterrupted (R1.1), and never altering pre-existing DASH semantics (R1.3). |
| E13 | A tracking beacon or click-tracking request fails (transport error, timeout, non-2xx), or a beacon is scheduled for a moment the ad never reaches — past a trim boundary, after a pause-ad was dismissed on resume, or after the viewer dismissed the slot. | Keep the ad and the primary content unaffected — a beacon failure is non-fatal and never reaches the viewer (`../context/05-dash-linear-interfaces.md`, interface contracts). Stop firing at the trim boundary (R13.3), from the pause-to-play transition for a dismissed pause-ad (R16.2), and at a viewer dismissal, firing those scheduled before it (R35.6). Fire each beacon once **within a candidate** of a non-linear document, the same `@id` in two candidates being two beacons; on a `ListMPD`, once per `@id` within its `@schemeIdUri` / `@value` over the whole presentation, merged sub-MPD streams included (R6.5). | Retry and log; the retry policy is implementation-defined. | APS: beacons as callback events on the ad's presentation timeline, resolved against the candidate's own presentation (R6.2, R6.6, R13.1); ClickThrough with its click-tracking in the normative carrier (R28.1). ADS: owns the schedule (R13); transcription fidelity is an APS-to-ADS matter (R13.5, R28.3). |
| E14 | Two forms would share the screen: the resolution document implies two non-linear forms at once; a pause begins inside a pause window while an overlay or a linear ad occupies the screen; or an alternative presentation begins while a non-linear window is presenting. | Keep at most one non-linear form active (R22.1), presenting sequenced forms in document order (R14.1). During a pause: suspend the overlay and render the pause-ad whatever its surface (R17.1, R21.1), suspend a linear ad and resume it where it stopped (R17.5), restore the overlay on resume only if its window is still open (R17.2, R17.3); in live content keep the presentation time frozen inside the pause window (R25.1); resume the primary content from the suspended position (R37.2). On an alternative presentation: with no relation declared, end the form there, present nothing further from the window and execute the linear event with its base semantics (R40.4); on top, keep presenting composited over it within R3, R5 and R22 (R40.5); treat windows in the alternative presentation's own `MPD` as that presentation's (R40.6). | Release the primary content's and a pre-existing overlay's resources for a fullscreen pause-ad (R21.1), by any pause mechanism that restores position (R37.1). | APS: declare forms as a sequence, never a concurrent composition (R14.3). No actor has a construct that inverts pause-ad-over-overlay priority (R17.4). Publisher: declare at most one relation per window (R40.1); a non-linear ad during an alternative presentation is declared in that presentation's `MPD` or by an on-top window (R40.2). Overlapping same-family windows are a fallback chain, not concurrency (R20.1). |
| E15 | The pause-ad candidates are exhausted while the viewer is still paused, or the pause window was already consumed. | Apply the declared behaviour — repeat, request again, or stop — and `stop` when none is declared (R32.1); under `request-again`, a document with no candidates is `stop` for the rest of that pause (R32.2); return to the primary content immediately on resume (R32.3). On a once-per-session window, present at most one pause ad and leave later pauses uninterrupted (R34.2), counting the window consumed when a pause ad **begins rendering** (R34.3). R5.3's fall-through does not apply: the primary content is paused. | Report the applied behaviour through an implementation-defined API. | APS: declare the behaviour on every pause document (R32.1). Publisher: optionally declare once-per-session (R34.1); request the `PlayList` metric through `Metrics` where pause windows exist (R33.4). |

## Notes

### Fall-through definition

"Fall through to primary content uninterrupted" means: no visible
artefact — no freeze, no blank slate, no error overlay unless the
application explicitly opted in; no tracking beacon fired for the
opportunity that failed; and primary-content playback continuing on its
own timeline. This is the floor DP-3 sets, and the base specification's
own rule: *"A failed execution results in smooth continued playback of
the main media presentation"* (§5.16.2.2.6, via DP-3).

Three moves are distinct from it. **Window-level** fall-through (E1,
E2, E3, E4) advances to the next overlapping window of the same family
and reaches the primary content only once the family is exhausted
(R20.1). **Candidate-level** fall-through (E7, E8, E9) advances to the
next candidate in the document already obtained and reaches the primary
content only once the candidates are exhausted (R5.3) — never the next
window, because a document carrying candidates of the slot's family is
not a failed execution. **Supersede fall-back** applies when a window
that declares supersede presents no ad by either route: what continues
is not the bare primary content but the inherited linear events the
window stood in for, executed with their base semantics (R40.3).

### Order of precedence

1. **Transport** (E1) — no document, so nothing downstream applies.
2. **Resolution-document level** (E2, E3, E4, E5) — unusable, misrouted,
   empty, late or expired. E2–E4 put the Player on the R20.1 chain.
3. **Constraint surfacing** (E6, E8, E9, E10's drop-before-play) — the
   serving window's declarations validated before rendering; E6 first,
   because an overlay or pause slot with no declared cap yields no ads
   at all.
4. **Per-candidate decode-time** (E7, E11).
5. **Per-candidate playback-time** (E10's trim-during-play, E14, E15).
6. **Tracking failures** (E13) — non-fatal; never abort an ad.

E12 is orthogonal: an unknown construct is ignored wherever it appears.
The supersede fall-back (R40.3) runs after steps 1–4 have left the
window with no ad.

### Guarantees by actor

**Publisher.** Declares in the MPD, not by runtime inference (R2.1): a
cap on every overlay and pause slot (R4.1), allowed layouts from the
closed token list and any custom region (R12.2, R39.2), the windows
including any fallback chain (R20.2), any window relation to the linear
events it overlaps (R40.1, R40.2), any early-resolution offset (R36.1),
any once-per-session bound (R34.1), and the `PlayList` metric request
(R33.4). Every unmet Publisher obligation degrades into a Player-side
skip, never into interrupted playback.

**ADS.** Decides which ads, how many and in what order, and owns the
tracking schedule (R13). Guarantees neither the cap (R4.4) nor a
device view (R5.4); no-fill is legitimate (R30). Its output reaches the
Player only through the APS.

**APS.** The only non-Player actor whose output is checked at runtime:
a parseable, valid document, tracking subtree included (R6.7); the
requested family (R20.4); no-candidates for no-fill (R30.1); ordered
options (R5.1); admissible carriers (R15.2, R24.1); layouts within the
enumeration and the admitted set (R12.3, R38.4), `custom` rectangles
within the region (R39.4); callback-event beacons (R6.2, R13.1); the
ClickThrough carrier (R28.1); a pause exhaustion behaviour (R32.1); a
dismissal declaration (R35.1); a usability period for early resolutions
(R36.4); and no dependence on capability parameters (R29.5).

**Player.** The enforcer: primary content survives every row (R1.4,
DP-3); the serving window's declarations are validated before rendering
(R2.3, R20.5, R38.5); the cap holds against actual length (R4.2, R4.5);
document order is honoured (R7.1, R7.4); no unrenderable form reaches
the screen (R3.3); at most one non-linear form is active (R22.1); a
non-linear form never overlaps an alternative presentation undeclared
(R40.4); a superseded linear break still runs when the window yields no
ad (R40.3); a pause-ad goes the instant the viewer resumes (R16.1,
R32.3); an expired resolution is never presented (R36.5); and every
device class and opportunity type has a defined behaviour (R3.2).

### Surfacing errors to the application layer

Everything in the MAY column that reports, logs or exposes a condition
is non-normative: no event names, payloads or delivery mechanism are
defined, and a Player that exposes nothing is conformant. Chapter 9
SHOULD give guidance — the unfilled (E4) versus failed (E1, E2, E3)
distinction carries the most operational value, and the misrouted
document (E3) is the one an operator cannot diagnose from the screen —
while leaving the API shape to implementers. One boundary is normative:
an error overlay is a visible artefact, so rendering one breaks the
fall-through guarantee unless the application explicitly opted in.

## References

- [`../context/02-actors.md`](../context/02-actors.md) — actor
  definitions and boundary summary.
- [`../context/03-requirements.md`](../context/03-requirements.md) —
  R1..R40 and DP-1..DP-3.
- [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
  — interface contracts, linear message flow, VAST → ListMPD edge cases.
- [`../context/99-glossary.md`](../context/99-glossary.md) —
  terminology; the ad-type and placement vocabulary is R12, to which the
  glossary defers.

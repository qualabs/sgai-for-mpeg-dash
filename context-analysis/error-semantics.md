[GROUNDED_BY=spec-only]

# Error semantics matrix

Inputs consumed: `../context/03-requirements.md` (R1..R30, mtime
2026-09-15) and `../context/05-dash-linear-interfaces.md` (interface
contracts table and VAST → ListMPD edge cases, mtime 2026-09-15).
Total rows: 16, covering every condition on the Player-visible
interfaces under which an ad opportunity can fail to be honoured.

## Scope

In scope:

- Errors on the Player ↔ APS interface (the resolution request and
  the resolution document it returns).
- Errors surfaced by Player-side validation of the resolution
  document against Publisher-declared constraints (R2.3).
- Errors surfaced while rendering an accepted candidate
  (declared-vs-actual duration, decode failure, mid-render loss).
- Errors on the Player ↔ tracking endpoint interface (beacons and
  click-tracking).

Out of scope:

- The APS ↔ ADS interface, opaque to this specification (R18, OOS-2).
  A failure there is observable to the Player only as E2 or E5.
- Primary content delivery errors (Publisher CDN, ABR, segment
  retry) — DASH 6th edition baseline, orthogonal to SGAI.
- Requirements that carry no runtime failure mode of their own: the
  governance set (R8, R9, R10), VAST independence (R11), and the
  presentation guarantees for playback speed (R19), pause-ad surface
  (R21) and live presentation-time freeze (R25). Violating one of
  these is non-conformance, not a condition this matrix assigns a
  Player response to.
- Auth / DRM / token exchange, out of scope of the interfaces
  document.

## Error matrix

| ID | Error condition | Player response (MUST) | Player response (MAY) | Publisher / APS / ADS obligation |
|---|---|---|---|---|
| E1 | Resolution request unreachable at transport level: DNS failure, TCP refused, TLS handshake failure, or timeout before a final status. | Treat the window as unresolvable; fall through to the next overlapping same-family window if the Publisher declared one, else fall through to primary content uninterrupted (R20.1, R1.1). | Retry within the interval between the earliest resolution time and the slot's presentation time; log the failure through an implementation-defined API. | Publisher: declare a fallback window where continuity matters (R20.1). APS: serve the event `@url` for the whole window the Publisher declared. |
| E2 | Resolution request returns a final HTTP status other than `200` (4xx / 5xx), including an APS that rejects the request because a reserved capability parameter was omitted. | Same as E1: fallback window if declared, else primary content uninterrupted (R20.1). | Retry before the slot's presentation time; log. | APS: MUST answer without any reserved capability parameter, since every one of them is optional for the Player (R29.2, R29.5); an absent parameter means undetermined, never unsupported (R29.7). |
| E3 | Resolution document is not well-formed XML, has an unknown root element, or fails schema validation. | Discard the whole document and fall through to primary content uninterrupted (R1.1, R1.4). | Fall through to a declared fallback window, since the first window's document was retrieved but is unusable; log the parse failure. | APS: emit a resolution document valid against the DASH 6th edition schema plus the extension points of R1.2. |
| E4 | Resolution document arrives after the slot window has elapsed (late response). | Discard the document and continue primary content uninterrupted; fire no beacon from it (R4.3 — a slot is never extended past its cap). | Reuse the late document for a subsequent window of the same family only if that window is still unresolved. | Publisher: declare an earliest-resolution offset that gives the APS a usable head start. APS: answer within the window it was asked in. |
| E5 | Resolution document returns `200` and carries no candidates (unfilled opportunity, not a failure). | Continue with the primary content uninterrupted, exactly as when candidates are exhausted (R30, R5.3), and MUST NOT fall through to a fallback window — the opportunity resolved (R20.1). | Report the opportunity as unfilled rather than failed through an implementation-defined API. | APS: express a no-ads decision as a document with no candidates, never as an error response or an empty body (R30.1). ADS: no obligation — no-fill is a legitimate decision. |
| E6 | No presentation option on a candidate is satisfiable: the device cannot render any offered form, or the decoder / surface budget of every offered layout exceeds what the device has (R26.3, R27.3). | Skip that candidate, preserving document order, and move to the next; when candidates are exhausted, continue with primary content (R5.3, R5.7, R7.2). | Report the skip through an implementation-defined API. | APS: candidates carry presentation options as an ordered list, document order being preference order (R5.1, R5.5). Neither ADS nor APS is required to hold a device-capability matrix (R5.4); a candidate carrying a single option places the suitability call upstream. |
| E7 | A presentation option names a layout outside the enumerated ad-type / visual-placement set, or a layout the Publisher did not allow on this slot. | Not render that option; move to the next option in document order, and skip the candidate if none passes (R5.6, R5.7). | Report the rejected layout name through an implementation-defined API. | Publisher: declare allowed layouts only with names from the enumerated set (R12.2). APS: emit no form metadata for an ad type or placement outside that set (R12.3). |
| E8 | A candidate's creative carrier is outside the admissible set (not video, image or HTML), or a non-AV asset URL is carried on a path bound by RFC 4337. | Not render that option; fall through as in E7 — an inadmissible carrier is never rendered (R3.3, R15.2). | Skip the candidate outright rather than evaluating its remaining options; log it as a non-conformant upstream signal (R15.3). | APS + Publisher: every creative carries a mimeType inside the admissible set (R15.2); non-AV asset URLs use a DASH-conformant carrier, never an RFC 4337-bound `@mimeType` path (R24.1). |
| E9 | A candidate's declared duration would push the cumulative slot duration past the Publisher-declared cap. | Not extend the slot past the cap under any circumstances (R4.3); keep the remaining candidates in document order without re-ordering or deduplicating (R7.4). | Drop the candidate before playback on declared duration alone ("drop before play", R7.3). | Publisher: declare a maximum duration on every slot, linear or non-linear (R4.1). ADS: not required to respect the cap when selecting candidates; conformance MUST NOT fail on cumulative overflow alone (R4.4). |
| E10 | An accepted candidate's actual rendered length exceeds its declared duration, or the sequence reaches the cap mid-ad. | Stop rendering at the cap boundary even mid-ad, enforcing against actual and not declared length ("trim during play", R4.2, R4.5, R7.5, R14.2), and stop firing beacons at the trim boundary (R13.3). | Surface the trim through an implementation-defined API. | ADS + APS: declared durations that match the creatives reduce trims but are not a conformance condition on the cap (R4.4). |
| E11 | Rendering an accepted candidate fails at runtime: ad segment fetch returns 4xx / 5xx, a decode error occurs, or the network is lost mid-ad. | Abort that ad and continue playing the primary content uninterrupted (R1.4). | Skip to the next candidate in document order instead of ending the slot, or end the break, per Player policy; retry the ad segment per DASH-IF guidance before aborting. | APS: reference ad media that is reachable for the duration of the slot. |
| E12 | An event scheme URI, extension element, or namespace in the primary MPD or the resolution document is unknown to the Player. | Ignore the unknown construct together with its subtree and continue playing the primary content uninterrupted (R1.1, R6.4, R23.1). | Log the unknown scheme or namespace. | Publisher + APS: express every new construct through an extension point whose ignore-if-unknown semantics produce this behaviour on a legacy Player (R1.2), and never alter pre-existing DASH semantics (R1.3). |
| E13 | A tracking beacon or a click-tracking request fails: transport error, timeout, or non-2xx response. | Continue rendering the ad and the primary content unaffected — a beacon failure is non-fatal and never visible to the viewer. | Retry the beacon, and log the failure; the retry policy is implementation-defined. | APS: carry beacons as callback events on the ad presentation timeline (R6.2, R13.1). ADS: owns which beacons exist and at what relative times (R13); beacon-delivery fidelity is an ADS-side concern, not a Player conformance condition. |
| E14 | A beacon is scheduled for a moment the ad never reaches: after a trim boundary (E10), or after a pause-ad was dismissed on resume. | Stop firing the remaining beacons at the trim boundary (R13.3) and cease beacons for a dismissed pause-ad from the pause-to-play transition onward (R16.2). | Report the unfired beacons through an implementation-defined API. | ADS + APS: schedules are expressed relative to the ad's presentation timeline (R13.1), so a schedule that overruns the slot is trimmed by the Player rather than rejected upstream. |
| E15 | A candidate carries a ClickThrough with no associated click-tracking URL(s). | Still honour the ClickThrough on viewer activation; the absent click-tracking is fired by nothing (R28.2). | Report the incomplete carrier as a non-conformant resolution document. | APS: a ClickThrough is carried together with its click-tracking URL(s) in the normative carrier — a ClickThrough without them is a violation the resolution document itself shows (R28.1). Whether a ClickThrough travels at all is an ADS-to-APS matter outside this specification (R28.3). |
| E16 | The resolution document implies two non-linear forms active at the same instant, or a pause-ad window opens while an overlay is rendering. | Keep at most one non-linear form active at any instant (R22.1): present sequenced forms one after another in document order (R14.1), and during a pause suspend the overlay and render the pause-ad (R17.1), restoring the overlay on resume only if its window is still open (R17.2, R17.3). | Report the suppressed form through an implementation-defined API. | APS: declare forms as a sequence, never as a concurrent composition (R14.3). Publisher, ADS and APS have no construct that inverts the pause-ad-over-overlay priority (R17.4). |

## Notes

### Fall-through definition

"Fall through to primary content uninterrupted" means: no visible
artefact — no freeze, no blank slate, no error overlay unless the
application explicitly opted in; no tracking beacon fired for the
opportunity that failed; and playback of the primary content
continues on its own timeline. The viewer cannot tell that an ad
opportunity existed. This is the floor that DP-3 sets: an opportunity
that cannot be honoured degrades into graceful skip-and-continue, and
applying this specification never breaks primary-content playback.

Falling through at the candidate level (E6, E7, E8) is different: the
Player moves to the next candidate in document order and only reaches
primary content once every candidate is exhausted (R5.3).

### Order of precedence

When several conditions arise on the same exchange, the Player
applies them in this order:

1. **Transport** (E1, E2) — no document, nothing downstream applies.
2. **Resolution-document level** (E3, E4, E5) — the document is
   unusable, late, or legitimately empty. E5 is terminal for the
   opportunity: it resolved, so no fallback window is tried.
3. **Constraint surfacing** (E7, E8, E9) — Publisher-declared
   constraints validated against each candidate before any is
   rendered.
4. **Per-candidate decode-time** (E6, E11) — what the device can
   actually satisfy and what the ad CDN actually delivers.
5. **Per-candidate playback-time** (E10, E16) — the cap enforced
   against actual length, and the single-active-form bound.
6. **Tracking failures** (E13, E14) and incomplete click carriers
   (E15) — non-fatal throughout; they never abort an ad and never
   reach the viewer.

E12 is orthogonal: an unknown construct is ignored wherever it
appears, at any level, and never advances the Player to the next
step in this order.

### Guarantees by actor

**Publisher.** Declares a maximum duration on every slot (R4.1), the
allowed layouts drawn from the enumerated set (R12.2), and the
opportunity windows including any fallback chain (R20.1). Declares
constraints in the MPD rather than leaving them to runtime inference
(R2.1). Guarantees nothing at runtime — it is an authoring-time
actor.

**ADS.** Decides which ads to serve and owns the tracking schedule
(R13). Guarantees neither the slot cap (R4.4) nor a device-capability
view (R5.4). No-fill is a legitimate outcome, not a failure.

**APS.** The only actor whose output this specification checks at
runtime. Guarantees: a resolution document that parses and validates
(E3); a `200` with no candidates for an unfilled opportunity rather
than an error (R30.1); candidates whose presentation options form an
ordered list in preference order (R5.1); creatives inside the
admissible carrier set on DASH-conformant carriers (R15.2, R24.1);
form metadata only for the enumerated ad types (R12.3); beacons as
callback events on the ad's presentation timeline (R6.2, R13.1); a
ClickThrough carried with its click-tracking (R28.1); an answer that
does not depend on any reserved capability parameter (R29.5).

**Player.** The enforcer. Guarantees that primary-content playback
survives every row of this matrix (R1.1, R1.4); that
Publisher-declared constraints are validated before anything is
rendered (R2.3); that the cap holds against actual length even mid-ad
(R4.2, R4.5); that document order is honoured, with dropping allowed
and re-ordering not (R7.1, R7.4); that no form its device cannot
render reaches the screen (R3.3); that at most one non-linear form is
active at any instant (R22.1); and that a defined behaviour — render,
fall back, or skip — exists for every device class and opportunity
type, undefined behaviour being non-conforming (R3.2).

### Surfacing errors to the application layer

Everything in the "Player response (MAY)" column that reports, logs
or exposes a condition is non-normative: this specification defines
neither event names, nor payloads, nor delivery mechanism, and a
Player that exposes nothing is conformant. The implementation-notes
chapter SHOULD give guidance on what is worth surfacing — unfilled
versus failed resolution (E5 versus E1 / E2 / E3) being the
distinction with the most operational value — while leaving the API
shape to implementers.

One boundary is normative rather than a matter of API shape: an error
overlay is a visible artefact, so a Player that renders one on any
row of this matrix has broken the fall-through guarantee unless the
application explicitly opted in.

## References

- [`../context/02-actors.md`](../context/02-actors.md) — actor
  definitions and the boundary summary.
- [`../context/03-requirements.md`](../context/03-requirements.md) —
  R1..R30 and the design principles DP-1 through DP-3.
- [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md)
  — interface contracts table, message flow, VAST → ListMPD edge
  cases.
- [`../context/99-glossary.md`](../context/99-glossary.md) —
  terminology; the edition-scoped ad-type and placement vocabulary is
  R12 of `03-requirements.md`, to which the glossary defers.

[GROUNDED_BY=spec-only]

# Error semantics matrix

Inputs consumed: `../context/03-requirements.md` (R1..R7, R12, R13, R15)
and `../context/05-dash-linear-interfaces.md` (Linear SGAI message flow
and Interface contracts). 13 error rows covering the eight categories
required by `prompts/1-pre-spec/build-error-semantics.prompt`. Vocabulary is
deliberately slot-agnostic ("resolution document", "candidate",
"form", "slot") so the matrix applies to both linear and non-linear
SGAI without re-stating the rows per chapter.

## Scope

In scope:

- Error conditions on the Player ↔ Broadcaster, Player ↔ ADS, and
  Player ↔ tracking endpoint interfaces.
- Errors surfaced at resolution time, at decode time, and at
  playback time.
- Player MUST and MAY behaviours, and ADS / Broadcaster obligations
  that prevent or recover from each condition.

Out of scope:

- Errors on the ADS ↔ upstream-decisioning leg (e.g. VAST
  `<Error>` from a DSP). Those are an ADS-internal concern and are
  flattened by the ADS adapter into one of the Player-facing rows
  below (typically E1 or E3).
- Application-layer error surfacing API shape (non-normative,
  implementation-defined; see Notes §4).
- Authentication, DRM, and token-exchange failures — out of scope
  per `05-dash-linear-interfaces.md` §"Out of scope".

## Error matrix

| ID  | Error condition | Player response (MUST) | Player response (MAY) | ADS / Broadcaster obligation |
|-----|-----------------|------------------------|-----------------------|------------------------------|
| E1  | Transport failure on the resolution request to the ADS (HTTP timeout, 4xx, 5xx, DNS unreachable, TCP refused, TLS handshake failure). | Fall through to primary content uninterrupted (R1). MUST NOT block primary playback waiting for the ADS. | Apply a bounded retry inside the window between the Earliest Resolution Time and the slot's `presentationTime`; abandon retries once the window closes (E4). | ADS SHOULD bound its response latency to the slot's resolution window; Broadcaster SHOULD set `@earliestResolutionTimeOffset` large enough to leave room for one retry. |
| E2  | Resolution document received but unparseable or schema-invalid (malformed XML, unknown root element, unsupported profile URI, missing required attributes). | Treat as if no resolution document was returned; fall through to primary content (R1). MUST NOT attempt partial recovery on a non-conforming document. | Log the failure for diagnostics (non-normative). | ADS MUST emit a resolution document that validates against the profile it declares; Broadcaster MUST NOT advertise a profile URI that the spec does not define. |
| E3  | Resolution document is well-formed but empty (no candidates / zero `<Period>` entries). | Fall through to primary content uninterrupted (R1). No tracking beacons MUST be fired. | Surface a non-normative "no-fill" event to the application layer (Notes §4). | ADS MAY return an empty resolution document deliberately as a no-fill signal; this is conforming behaviour, not an error on the ADS side. |
| E4  | Resolution document arrives after the slot window has elapsed (response received past the slot's `presentationTime` for linear, or past the overlay window for non-linear). | Discard the late response; fall through to primary content for the slot that just elapsed. MUST NOT delay primary playback to render a late ad. | Reuse the late response for a subsequent slot only if its `@earliestResolutionTimeOffset` / scheme allows it; otherwise discard entirely. | ADS MUST honour the slot's resolution window; if it cannot meet the deadline it SHOULD return early with an empty resolution document (E3) rather than late with content. |
| E5  | Player does not implement the SGAI event scheme URI declared on the `<EventStream>` (legacy Player encountering a construct introduced by this proposal). | Ignore the unknown event and continue playing primary content uninterrupted (R1.1). | None. | Broadcaster MUST express every new SGAI construct via an extension point with `ignore-if-unknown` semantics (R1.2); the Broadcaster MUST NOT redefine pre-existing constructs (R1.3). |
| E6  | An ADS-returned candidate carries no form renderable on the device (no admissible form / layout / device-capability intersection per R5.6). | Skip the candidate; fall through to the next candidate in declared order (R5.7, R7.1). If exhausted, fall through to primary content. | Surface a non-normative "candidate-skipped" event for diagnostics. | ADS SHOULD return at least one candidate with a broadly renderable form (e.g. video) so that R5.7 fall-through to primary content is the worst case, not the default case. ADS MUST NOT require a device-class matrix (R5.4). |
| E7  | A candidate declares a form whose layout name is not in the Broadcaster's allowed-layouts set, or is not part of the IAB-defined set used by the spec edition. | Reject the form (R5.6); evaluate other forms on the same candidate. If no admissible form remains, treat as E6 and fall through. | Log the layout name and the reason for rejection. | Broadcaster MUST declare allowed layouts using names that map 1:1 to IAB-defined values (R12.2). ADS MUST NOT emit form metadata for layout names outside the IAB-defined set (R12.3). |
| E8  | A candidate declares a creative carrier mimeType outside the admissible set defined by R15 (i.e. anything other than the baseline mp4 video carrier, an IAB-defined image format, or `text/html`). | Reject the form. If no admissible form remains on the candidate, treat as E6 and fall through. | Skip the candidate entirely per R15.3 even if other forms on the same candidate are admissible; flag the resolution document as non-conformant for diagnostics. | ADS / Broadcaster MUST restrict every returned form's mimeType to the R15 admissible set (R15.2). Scripted creatives MUST be wrapped inside `text/html` (OOS-4); raw JavaScript, SVG-as-payload, PDF and proprietary binary carriers MUST NOT be emitted. |
| E9  | Cumulative declared duration of accepted candidates would exceed the Broadcaster-declared slot cap if the next candidate is added ("drop before play", R7.3). | Apply R7.3 / R7.4: MUST NOT re-order, deduplicate, or rearrange the remaining candidates after dropping. | Drop the offending candidate based on declared duration; choose between dropping only the offending candidate or dropping all subsequent candidates — both are conforming under R7.3. | Broadcaster MUST declare `@maxDuration` on every slot (R4.1). ADS is NOT required to respect the cap (R4.4); the cap is enforced Player-side. |
| E10 | Actual rendered length of an accepted candidate exceeds its declared duration, pushing cumulative slot duration past the cap ("trim during play", R4.5 / R7.5). | Stop rendering the candidate exactly at the cap boundary, even mid-ad (R4.2, R4.5). MUST NOT extend past the cap (R4.3). MUST stop firing tracking beacons at the trim boundary (R13.3). | Surface a non-normative "slot-trimmed" event to the application layer. | ADS / Broadcaster MUST NOT rely on declared duration matching actual length for cap arithmetic; the Player is the authoritative enforcer (R2.3 / R4). |
| E11 | Ad media segment fetch fails during playback (HTTP 4xx/5xx, timeout, decoder error, DRM key-exchange failure on an ad asset). | Abort the current candidate. Resume the slot at the next candidate in declared order (R7.1) and re-apply R4 cap arithmetic against rendered-so-far. If no candidates remain, fall through to primary content. | Surface a non-normative "candidate-failed" event. May tear down the entire slot per Player policy (`05-dash-linear-interfaces.md` §Interface contracts). | ADS SHOULD point at CDNs with availability comparable to the Broadcaster CDN; the spec does not require parity but the Player's recourse on failure is to drop the candidate, not to retry indefinitely. |
| E12 | Tracking beacon delivery fails (HTTP error, timeout, DNS failure on a callback URL emitted under scheme `urn:mpeg:dash:event:callback:2015`). | Continue playback uninterrupted. Beacon failures are non-fatal and MUST NOT abort the candidate or the slot. | Retry the beacon with bounded backoff; log the failure for diagnostics. Surface beacon failures via an implementation-defined API (Notes §4). | ADS MUST embed tracking beacons under the callback scheme reused from linear SGAI (R6.2, R13.4); the ADS / Broadcaster MUST NOT depend on beacon delivery for state correctness. |
| E13 | Unknown vendor namespace or unrecognised extension element on the resolution document or its sub-MPDs (e.g. vendor-specific click-through / `AdSystem` / `UniversalAdId` carriers, or unknown attributes on a tracking carrier). | Safely ignore the unknown namespace / element (R1.1, R6.5). MUST NOT abort the candidate or the slot. | Pass the ignored data verbatim to the application layer for opportunistic consumption (non-normative). | ADS / Broadcaster MAY use vendor-namespaced extensions to convey application metadata that has no native DASH carrier (R6.4); when they do, they MUST NOT rely on Players consuming them (R1.1). |

## Notes

### Fall-through definition

"Fall through to primary content uninterrupted" means: no visible
artefact (no freeze, no blank slate, no error overlay unless the
application has explicitly opted in via an implementation-defined
API); no tracking beacon fired for the failed slot; primary
playback continues from the position it would have held had the
SGAI event not existed. For `ReplacePresentation` slots specifically,
"uninterrupted" means the playhead continues advancing on the main
timeline at wall-clock pace; the Player does not pause main media
time waiting for an ADS response that ultimately failed.

### Order of precedence

When more than one error condition is applicable to the same
candidate or exchange, the Player MUST apply them in this order
(short-circuit at the first match):

1. **Transport** — E1 (resolution-request transport) before E11
   (ad-segment transport).
2. **Resolution-document level** — E2 (parse / schema), E3 (empty)
   and E4 (late) before any per-candidate evaluation.
3. **Constraint surfacing** — E5 (unknown event scheme), E7
   (unknown / disallowed layout) and E8 (inadmissible creative
   carrier mimeType, R15) before per-candidate device evaluation.
4. **Per-candidate decode-time** — E6 (no renderable form) before
   any duration evaluation.
5. **Per-candidate playback-time** — E9 (drop before play) before
   E10 (trim during play); E11 (ad-segment failure) preempts E10
   on the affected candidate.
6. **Tracking failures (non-fatal)** — E12 and E13 are evaluated
   independently and MUST NOT influence the slot outcome.

### Guarantees by actor

- **Broadcaster guarantees**: declares `@maxDuration` on every slot
  (R4.1); declares allowed layouts using IAB-defined names (R12.2);
  expresses every new SGAI construct via an `ignore-if-unknown`
  extension point (R1.2 / R1.3). Together these guarantees make
  E5 / E7 / E9 / E10 decidable Player-side.
- **ADS guarantees**: emits a resolution document that validates
  against its declared profile (E2); honours the slot's resolution
  window or returns early with an empty document (E3 / E4); embeds
  tracking beacons under the callback scheme (R6.2 / R13.4);
  populates each candidate with at least one renderable form
  (R5.1) whose creative carrier mimeType is in the R15 admissible
  set (R15.2). The ADS makes no guarantee on the duration cap
  (R4.4) and is not required to maintain a device-class matrix
  (R5.4).
- **Player guarantees**: enforces the cap on actual rendered length
  (R4.2 / R4.5); honours ADS-declared candidate order (R7.1 / R7.4)
  except for drops permitted by R7.2 / R7.3; selects per device
  capabilities × Broadcaster-allowed layouts × ADS hints (R5.6);
  falls through to primary content as the worst-case behaviour on
  every error row (R1).

### Surfacing errors to the application layer

The Player MAY expose any of the error events in the matrix above
to the embedding application via an implementation-defined API
(e.g. a JavaScript event on a web Player, a delegate callback on a
native SDK). The API shape is non-normative and out of the spec's
scope; spec chapter 9 (Implementation notes) SHOULD include
guidance on the categories that benefit from application surfacing
(at minimum: E3 no-fill, E8 inadmissible carrier, E10 trim, E11
candidate failure) but MUST NOT mandate a wire format or method
signature.

## References

- [`../context/02-actors.md`](../context/02-actors.md) — three-actor
  responsibility model invoked by every Guarantees-by-actor row.
- [`../context/03-requirements.md`](../context/03-requirements.md) —
  R1, R2, R4, R5, R6, R7, R12, R13, R15 cited inline.
- [`../context/05-dash-linear-interfaces.md`](../context/05-dash-linear-interfaces.md) —
  linear SGAI message flow and Interface contracts table; the rows
  in this matrix are the abstract / slot-agnostic generalisation of
  the linear "Error semantics" column in that table.
- [`../context/99-glossary.md`](../context/99-glossary.md) —
  canonical vocabulary for "resolution document", "candidate",
  "form", "slot", "fall through".

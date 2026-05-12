[GROUNDED_BY=spec-only]

# Error semantics matrix

This document captures the exhaustive matrix of error conditions
that can arise during an SGAI exchange (Broadcaster → Player ↔
ADS) and the obligations each actor has in response. The matrix is
the source-of-truth for the norm's chapter 9 (Implementation
notes) and chapter 10 (Test cases) — it makes "what does the
Player do when X breaks" auditable, not narrative.

This is a generated analysis derived from R1..R10 in
[`../spec/03-requirements.md`](../spec/03-requirements.md) and the
interface contracts in
[`../spec/05-dash-linear-interfaces.md`](../spec/05-dash-linear-interfaces.md).
The norm output (the published spec document) will instantiate
these with concrete construct names and codes.

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY) for
normative statements.

## Scope

This document covers:

- Failures of the Player ↔ ADS exchange.
- Malformed or non-conformant resolution documents (`ListMPD` or
  successor).
- Constraint violations surfaced at the Player at decode or
  playback time.
- Recovery and fall-through obligations.

Out of scope:

- Failures of the Broadcaster → Player MPD fetch — a DASH baseline
  concern, not SGAI-specific.
- Failures of ADS-internal upstream calls (e.g. ADS ↔ VAST
  upstream) — those are ADS-internal per R2 and
  [`../spec/02-actors.md`](../spec/02-actors.md). From the Player's perspective
  any such failure surfaces as one of E1..E4 or E12.
- Broadcaster authoring errors at MPD level (e.g. malformed primary
  `MPD`) — also a DASH baseline concern.

## Error matrix

| ID | Error condition | Player response (MUST) | Player response (MAY) | ADS / Broadcaster obligation |
|----|-----------------|------------------------|-----------------------|------------------------------|
| E1 | HTTP timeout on the ADS request (no response within the configured window). | Fall through to primary content uninterrupted (R1, R2.3). | Retry once against a different ADS endpoint if the Broadcaster declared a fallback URL. | ADS: respond within the window or do not respond at all — partial responses MUST NOT be sent. |
| E2 | HTTP 4xx / 5xx from the ADS, with empty or non-resolution body. | Fall through to primary content uninterrupted. | Log the status code for telemetry; surface a debug event to the application layer. | None. |
| E3 | HTTP 200 from the ADS but body is malformed (XML / JSON parse error). | Fall through to primary content uninterrupted. | Surface a debug event to the application layer. | ADS: a 200 status code MUST imply a parseable body. |
| E4 | HTTP 200 with a schema-invalid resolution document (e.g. `ListMPD` with no candidate Periods, unknown root element, missing required attributes). | Fall through to primary content uninterrupted. | Surface a debug event with the schema violation. | ADS: MUST emit schema-conformant resolution documents only (R2.2). |
| E5 | The resolution document is well-formed but no candidate carries a form renderable on this device (R3, R5.3). | Skip every non-renderable candidate; if all are skipped, fall through to primary content. | Log a per-candidate skip reason. | ADS: MAY return candidates that are not all renderable on every device — this is expected (R5.4); the Player picks. |
| E6 | A candidate's declared duration would push cumulative slot duration past the Broadcaster-declared cap (R4.1, R4.2). | Drop the candidate before playback ("drop before play", R7.3) while preserving the order of remaining candidates (R7.4). | None. | ADS: MAY return candidates whose cumulative declared duration exceeds the cap (R4.4); Broadcaster: MUST declare the cap on each slot (R4.1). |
| E7 | A candidate's actual rendered length at playback exceeds its declared duration or pushes cumulative duration past the cap (R4.5, R7.5). | Trim the rendering at the cap boundary ("trim during play"), even mid-ad. | None. | ADS: SHOULD declare accurate durations; Broadcaster: MUST declare the cap on each slot. |
| E8 | A candidate's form references a layout / vocabulary name not present in the canonical layout vocabulary referenced from [`../spec/99-glossary.md`](../spec/99-glossary.md). | Treat the form as non-renderable; if the candidate has no renderable form left, skip it (R5.3). | Log the unknown layout name. | ADS: MUST only emit candidates whose forms use canonical-vocabulary names (R2.2). |
| E9 | The resolution document references a scheme URI or extension whose version the Player does not implement. | Apply R1 ignore-if-unknown: skip the unknown construct and continue. If the unknown construct was load-bearing (e.g. the wrapper of the candidate itself), skip that candidate; if it was the whole event, fall through to primary content. | None. | ADS / Broadcaster: MAY send newer schemes to older Players (R1.2); the burden of degrading is on the Player. |
| E10 | A tracking beacon HTTP request fails (timeout, 4xx, 5xx, network error). | Continue ad playback uninterrupted — tracking failures MUST NOT abort rendering or fall through. | Retry the beacon up to an implementation-defined number of times with back-off. | None. R6 specifies the carrier; delivery reliability is implementation-defined. |
| E11 | The resolution document contains more candidates than the slot can hold at the cap. | Apply R7.3 drop-before-play in declared order until cumulative declared duration ≤ cap; play the accepted subset in the original ADS-declared order (R7.1, R7.4). | None. | ADS: MAY return more candidates than fit — the Player selects (R4.4). |
| E12 | ADS endpoint unreachable: DNS failure, TCP refused, TLS handshake failure. | Treat equivalently to E1: fall through to primary content uninterrupted. | Mark the endpoint as failing for an implementation-defined back-off window. | None. |
| E13 | Resolution document received after the slot window has already elapsed at the Player (late response). | Discard the response; fall through (or continue) with primary content uninterrupted. The Player MUST NOT play the late ads outside their slot. | Surface a debug event. | ADS: SHOULD respect the slot window declared by the Broadcaster. |

## Notes

### Fall-through definition

"Fall through to primary content uninterrupted" means the Player:

- Continues rendering the Broadcaster's primary stream without
  interrupting playback.
- Shows no visible artefact of the failed SGAI exchange (no
  freeze, no blank slate, no error overlay unless the application
  explicitly opted in via the surfacing API below).
- Fires no tracking beacon for the failed exchange — per R6,
  tracking is fired only against successfully rendered ads.

### Order of precedence

When more than one error arises simultaneously on the same
exchange, the Player applies them in this order:

1. **Transport / parse errors** (E1, E2, E3, E12) — fall through
   to primary content immediately. No per-candidate processing.
2. **Resolution-document-level errors** (E4, E13) — fall through.
3. **Document-level constraint surfacing** (E5, E11) — process
   per-candidate, then fall through only if the surviving set is
   empty.
4. **Per-candidate violations** (E6, E8, E9) — handled per
   candidate at decode time; do not affect siblings beyond R7.4
   (order preservation).
5. **Playback-time violations** (E7) — handled during rendering;
   do not affect already-rendered ads.
6. **Tracking failures** (E10) — non-fatal; never affect playback.

### Surfacing errors to the application layer

The Player MAY expose error conditions via implementation-defined
APIs to the embedding application (e.g. SDK callbacks, event
listeners). This surface is non-normative; the norm chapter 9
SHOULD include guidance but implementations are free to choose the
shape of the API. What is normative is the playback behaviour
above — the application-facing surface is purely additive.

### Guarantees by actor

Derived from the matrix above:

- **Broadcaster** guarantees: declares a cap on every slot
  (R4.1); declares any fallback ADS endpoint if expected to be
  used; uses MPEG-DASH 6th edition extension points for any new
  construct so legacy Players ignore them gracefully (R1.2).
- **ADS** guarantees: HTTP 200 implies a parseable,
  schema-conformant body (E3, E4); only emits canonical-vocabulary
  layout names (E8); is NOT obliged to respect the cap (R4.4) or
  to know device capability (R5.4).
- **Player** guarantees: enforces the cap (R4); validates every
  candidate against device capability (R5) and against Broadcaster
  constraints (R2.3); preserves ADS-declared order modulo R7.2 /
  R7.3 drops; never aborts primary content because of an SGAI
  failure (R1).

## References

- [`../spec/02-actors.md`](../spec/02-actors.md) — actor
  responsibilities and the three-actor contract every error
  condition is read against.
- [`../spec/03-requirements.md`](../spec/03-requirements.md) — R1,
  R2, R4, R5, R6, R7 (the obligations the matrix derives from),
  with their conformance criteria.
- [`../spec/05-dash-linear-interfaces.md`](../spec/05-dash-linear-interfaces.md)
  — the concrete interface contracts that surface most of these
  errors (Player → ADS HTTP exchange, `ListMPD` schema, tracking
  carrier).
- [`../spec/99-glossary.md`](../spec/99-glossary.md) — canonical
  layout vocabulary referenced in E8.

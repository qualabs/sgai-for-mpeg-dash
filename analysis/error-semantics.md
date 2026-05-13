[GROUNDED_BY=spec-only]

# Error semantics matrix

Inputs consumed: `../context/03-requirements.md` (R1..R7, with extension
to R11..R13) and `../context/05-dash-linear-interfaces.md` (interface
contracts and message flow). 13 rows total. Scope: runtime error
behaviour on the Player ↔ Broadcaster, Player ↔ ADS, and Player ↔
tracking-endpoint interfaces.

## Scope

- In scope: transport / parse / semantic / behavioural failures that
  the Player encounters during an SGAI exchange and the actors'
  obligations in each case.
- Out of scope: ADS-internal failures upstream of the Player (DSP /
  SSP / ad-server timeouts); these are absorbed by the ADS adapter
  and surface as ADS HTTP errors or empty resolution documents.
- Out of scope: DRM, CDN authentication, codec mismatch — these are
  orthogonal Player concerns governed by DASH-IF guidelines.

## Error matrix

| ID | Error condition | Player response (MUST) | Player response (MAY) | ADS / Broadcaster obligation |
|----|-----------------|------------------------|-----------------------|------------------------------|
| E1 | HTTP timeout on ADS resolution request. | Treat the slot as no-fill; fall through to primary content. | Retry once within the slot window if time permits; log the failure for telemetry. | ADS SHOULD respond within a tighter-than-slot deadline so the Player has time to react. |
| E2 | HTTP 4xx (e.g. 403, 404) on ADS resolution. | Treat the slot as no-fill; fall through to primary content. | Log the status; suppress retries for the same slot. | ADS MUST NOT emit 4xx as a soft-no-fill signal — empty resolution document is the canonical no-fill. |
| E3 | HTTP 5xx on ADS resolution. | Treat the slot as no-fill; fall through to primary content. | Retry once with exponential backoff inside the slot window. | ADS MUST eventually emit an empty resolution document for sustained outages instead of 5xx storms. |
| E4 | DNS / TCP / TLS failure reaching the ADS (DNS NXDOMAIN, connection refused, TLS handshake error). | Treat the slot as no-fill; fall through to primary content. | Log the network class of failure. | ADS endpoint MUST be reachable for the lifetime of the campaign. |
| E5 | Resolution document is malformed XML (unparsable). | Treat the slot as no-fill; fall through to primary content. | Log the parse error. | ADS MUST serve XML that conforms to the resolution document schema. |
| E6 | Resolution document is schema-invalid (e.g. missing required field, illegal attribute value). | Treat the slot as no-fill; fall through to primary content. | Log schema violations per candidate; partial recovery (drop offending candidate, keep the others) is permitted if the document is structurally salvageable. | ADS MUST validate the resolution document against the spec's schema before emitting. |
| E7 | Resolution document root is an unknown element / unknown profile URI. | Skip the slot per R1 "ignore-if-unknown"; fall through to primary content. | Log the unknown element / scheme; emit a single warning, not per-segment. | Broadcaster MUST NOT inject manifest constructs whose root element falls outside the SGAI-known set. |
| E8 | No candidate carries a form renderable on the Player's device (R5.3 / R5.7 — every form/layout combination violates one of device caps, allowed layouts, or hints). | Skip the candidate; if no candidate remains, decline the slot and fall through to primary content uninterrupted. | Log the no-renderable-form fall-through. | ADS SHOULD include at least one widely-renderable form (image as a long-tail fallback for non-linear; video for linear) to maximise fill. |
| E9 | Unknown event scheme URI on a Broadcaster MPD event. | Per R1: ignore the event; continue primary content uninterrupted. | Log the unknown scheme once. | Broadcaster MUST use the year-pinned `urn:svta:dash:<construct>:<year>` URIs for SGAI constructs introduced by this spec (and reuse the DASH baseline scheme for tracking). |
| E10 | Declared cumulative duration of accepted candidates would exceed the Broadcaster-declared cap (R4.2 / R7.3 — drop-before-play). | MAY drop the offending candidate before playback if its declared duration would push the total past the cap. | Continue with the remaining candidates in ADS-declared order (R7.4 — no reorder, no dedup). | ADS is not required to pre-respect the cap (R4.4); cap enforcement is the Player's responsibility. |
| E11 | Actual rendered length of an accepted candidate exceeds its declared duration; cumulative actual length crosses the cap mid-rendering (R4.5 / R7.5 — trim-during-play). | Stop rendering at the cap boundary, even mid-ad; transition to next candidate or back to primary content. | Stop firing tracking beacons at the trim boundary (R13.3). | Broadcaster MUST declare a cap on every slot (R4.1). |
| E12 | Tracking beacon HTTP failure (timeout, 4xx, 5xx) on an ad-tracking endpoint (impression, quartile, complete, etc.). | Continue playback uninterrupted — tracking is fire-and-forget. | Log the beacon failure; surface to application layer via an implementation-defined API (non-normative). | Tracking endpoints SHOULD be highly available; ADS MAY rotate dead endpoints between resolution requests. |
| E13 | ADS resolution response arrives after the slot has elapsed (late callback). | Treat as no-fill — the slot has already been resolved as primary content; the Player MUST NOT inject the late ad post-hoc. | Drop the late response silently; log latency for telemetry. | ADS SHOULD respect the time budget implied by `@earliestResolutionTimeOffset` and the slot's `@presentationTime`. |

## Notes

### Fall-through definition

"Fall through to primary content uninterrupted" means: no visible
artefact (no freeze, no blank slate, no error overlay unless the
application has explicitly opted in to one via an implementation-
defined API); no tracking beacon fired for the failed ad slot;
playback of the primary content continues seamlessly from the
position the playhead occupied when the failure was detected. This
is the runtime equivalent of R1's "ignore-if-unknown" guarantee.

### Order of precedence

When multiple errors arise on the same exchange, the Player applies
them in this order (top wins):

1. **Transport** — HTTP / DNS / TCP / TLS failures (E1..E4) short-
   circuit the exchange before any document content is consumed.
2. **Resolution-document level** — XML parse failures (E5) and
   schema-invalid documents (E6) short-circuit before per-candidate
   evaluation. Unknown root element (E7) is in the same tier — ignore
   per R1.
3. **Constraint surfacing** — Broadcaster-declared cap or layout
   policy violations are detected at this tier; the Player either
   discards offending candidates (E10) or declines the slot.
4. **Per-candidate decode-time** — no-renderable-form fall-through
   (E8) is detected here and triggers the next-candidate walk per
   R5.7.
5. **Per-candidate playback-time** — trim-during-play (E11) is the
   only error in this tier.
6. **Tracking failures** — beacon errors (E12) are non-fatal and never
   alter playback; they are the lowest tier.

Late callbacks (E13) cross-cut — by the time the Player observes
them, the slot has already fallen through to primary at a higher
tier.

### Guarantees by actor

- **Broadcaster** guarantees: every SGAI slot has a `@maxDuration`
  declared (R4.1); event scheme URIs are year-pinned per
  `06-naming-and-namespaces.md`; constructs sit in DASH extension
  points whose ignore-if-unknown semantics are already defined
  (R1.2).
- **ADS** guarantees: the response is either a well-formed,
  schema-valid resolution document, an empty resolution document
  (canonical no-fill), or an HTTP error. ADS does NOT guarantee that
  the cumulative duration of returned candidates respects the cap
  (R4.4) — that is the Player's job.
- **Player** guarantees: every error in this matrix produces a
  defined behaviour. Undefined behaviour is non-conforming (R3.2).
  Specifically, no error in this matrix can cause the primary
  content to freeze, blank, or surface an error overlay to the
  user unless an opt-in API has been exercised.

### Surfacing errors to the application layer

The Player MAY expose error events via implementation-defined APIs;
this surfacing is non-normative. The spec's implementation-notes
chapter SHOULD include guidance (e.g. emit `adslot-error` with the
matrix-row ID, allow the application to register listeners), but
implementations are free to choose the API shape. Conformance does
not require any specific API.

## References

- `../context/02-actors.md` — actor responsibilities.
- `../context/03-requirements.md` — R1 (ignore-if-unknown), R4 (cap
  enforcement), R5 (device-aware selection), R6 (tracking carrier),
  R7 (ADS-returned order), R13 (non-linear tracking semantics).
- `../context/05-dash-linear-interfaces.md` — interface contracts and
  message flow.
- `../context/06-naming-and-namespaces.md` — scheme URI patterns
  (E7 / E9 reference these).
- `../context/99-glossary.md` — definitions of resolution document,
  candidate, form, slot.

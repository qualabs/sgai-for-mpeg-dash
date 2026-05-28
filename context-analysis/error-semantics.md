[GROUNDED_BY=spec-only]

# Error semantics matrix

Inputs consumed: `../context/03-requirements.md` (R1..R7, R12, R13,
R15 — mtime 2026-05-27) and `../context/05-dash-linear-interfaces.md`
(interface contracts table — mtime 2026-05-27). Total rows: 13. Scope
covers transport, parse, fall-through, declared-vs-actual duration,
unknown-vocabulary, late response, and tracking failure conditions
that surface on the actors' interfaces. Solution-specific construct
names are deliberately avoided per prompt instructions; abstract
terms ("resolution document", "candidate", "form", "layout") are used
throughout.

## Scope

In scope:

- Errors that surface on the Player ↔ APS interface (resolution
  document exchange) and on the Player ↔ tracking endpoint interface.
- Errors that surface during Player-side validation of the
  resolution document against Publisher-declared constraints.
- Errors that surface during candidate playback (declared-vs-actual
  duration, decode failure).

Out of scope:

- Errors on the APS ↔ ADS interface — opaque to the spec (R18).
- Primary content delivery errors (Publisher CDN, ABR, segment
  retries) — orthogonal to SGAI and handled by DASH 6th baseline.
- Authentication / DRM / token-exchange errors — handled by the
  layers below SGAI per DASH-IF guidance.
- Application-layer error surfacing (chapter 9 implementation
  notes) — non-normative API shape.

## Error matrix

| ID  | Error condition | Player response (MUST) | Player response (MAY) | ADS / Publisher / APS obligation |
|-----|-----------------|------------------------|-----------------------|----------------------------------|
| E1  | Transport-level failure on APS resolution request (HTTP timeout, 4xx, 5xx, DNS unreachable, TCP refused, TLS handshake failure) | Fall through to primary content uninterrupted (R1); apply R20 fallback if a subsequent same-family overlapping window exists (R20.1) | Surface the failure to the application layer via an implementation-defined event (non-normative); retry once with exponential backoff per Player policy | APS SHOULD respond within a Player-policy timeout; APS MUST NOT block the Player on slow ADS calls (R18.2) |
| E2  | Empty resolution document (`ListMPD` with zero Periods, no candidates) | Fall through to primary content uninterrupted (R1); apply R20 fallback if applicable | Surface to application layer (non-normative) | APS MAY return an empty resolution document on ADS no-fill (industry convention — per `05-dash-linear-interfaces.md` open question; the spec MAY decline to bind) |
| E3  | Parse failure on resolution document (malformed XML, schema-invalid, unknown root element) | Fall through to primary content uninterrupted (R1); discard the entire document | Surface to application layer (non-normative) | APS MUST emit a syntactically valid resolution document; if it cannot, MUST return an HTTP error (collapsing into E1) |
| E4  | No candidate carries a presentation option satisfiable on the device (R5.7 fall-through exhausted) | Skip the entire slot and continue primary content uninterrupted (R3) | Surface to application layer (non-normative); record the slot as a "graceful decline" | APS / ADS NOT required to maintain a device-class matrix (R5.4); the Player is the sole authority on device capability |
| E5  | Candidate violates a Publisher-declared slot constraint (disallowed layout, exceeds duration cap on declared duration, exceeds concurrency cap) | Discard the candidate and continue evaluating the next candidate in document order (R2.3, R7.4) | Surface to application layer (non-normative); log the constraint that triggered the discard | Publisher declares constraints in the primary MPD (R2.1); ADS / APS NOT obligated to enforce (R2.2). The APS MAY emit candidates that violate constraints — the Player is the enforcer (R2.3) |
| E6  | Declared candidate duration vs cap mismatch — declared duration would push cumulative slot duration past the cap (R4 drop-before-play) | Skip the candidate before playback (R7.3), continue with the next candidate in document order | None — drop-before-play is the only conformant response | ADS NOT required to respect the cap (R4.4); cap enforcement is Player-side only |
| E7  | Actual rendered length exceeds declared duration ("trim during play" — R4.5, R7.5) | Stop rendering at the cap boundary, even mid-frame (R4.2); fire only the tracking beacons whose scheduled relative time is ≤ the trim boundary (R13.3) | Surface "ad trimmed" event to the application layer (non-normative) | ADS / APS MUST declare each candidate's duration as accurately as possible in the resolution document; the Player MUST NOT extend the slot beyond the cap regardless of metadata (R4.3) |
| E8  | Unknown layout name in the Publisher's allowed-layouts declaration (name does not map to an IAB-defined ad-type value, R12.2) | Discard the candidate whose presentation option references the unknown layout (treat as a non-renderable option per R5.7); continue evaluating the next option | Surface to application layer (non-normative); log the unknown layout name | Publisher MUST declare allowed-layouts using names that map 1:1 to IAB-defined values (R12.2); APS MUST NOT emit form metadata for ad types outside the IAB-defined set used by this spec's edition (R12.3) |
| E9  | Unknown event scheme URI on a `<EventStream>` carrying an SGAI construct the Player does not implement (R1 ignore-if-unknown) | Skip the unknown event and continue playing primary content uninterrupted (R1.1) | Surface to application layer if the Player exposes that hook (non-normative) | Publisher MUST express new constructs via the extension points enumerated in R1.2 (DR-2 / DR-3, §5.10, §5.8.4.x) — paths that violate the DR-1 / DR-5 chain are non-conformant |
| E10 | Per-candidate decode-time failure (segment fetch failed, decoder rejected the bitstream, codec not supported) | Treat as if the candidate had no renderable form on this device (R5.3); skip to the next candidate in document order (R7); fire no further tracking beacons for the failed candidate | Surface "decode failed" event to the application layer (non-normative); attempt a single retry on transport failure per Player policy | ADS MUST select creatives whose codecs are within the Publisher's declared codec set (out-of-band agreement); APS transcribes verbatim |
| E11 | Per-candidate playback-time failure mid-render (decoder stall, network drop on segment N+1, asset URL 404 for non-AV creatives) | Cease rendering the candidate; fire only the tracking beacons whose scheduled relative time has already elapsed; advance to the next candidate or to primary content per R7 / R3 | Surface "ad failed mid-render" event to the application layer (non-normative) | APS MUST emit asset URLs that resolve (R24.1); transient CDN-level errors are best-effort handled |
| E12 | Tracking beacon HTTP failure (4xx, 5xx, timeout on the HTTP GET to a tracking endpoint, R6) | Continue rendering the ad uninterrupted; tracking failure MUST NOT affect ad playback or primary content | Best-effort log the failure (non-normative); MAY retry once per Player policy | The tracking endpoint is operated by the ADS (or its tracking-provider proxy); the spec does NOT bind tracking endpoint availability |
| E13 | Late APS response (resolution document arrives after the slot's playback window has elapsed) | Discard the late response and continue primary content uninterrupted (R1); apply R20 fallback if applicable | Surface "ad arrived too late" to the application layer (non-normative) | Player computes the Earliest Resolution Time (ERT) from `@earliestResolutionTimeOffset` (§5.16 baseline) and issues the request between ERT and the slot's `presentationTime`; APS SHOULD respond before the slot starts |

## Notes

### Fall-through definition

"Fall through to primary content uninterrupted" means:

- **No visible artefact** — no freeze, no blank slate, no error
  overlay (unless the application explicitly opted in to surface
  errors via the non-normative chapter 9 API).
- **No tracking beacon fired** — neither for the failed candidate
  nor for any candidate that would have followed it.
- **Playback continues** — the primary timeline keeps advancing
  exactly as if the slot had never been declared.

Fall-through is the **default** for every transport-level, parse, and
no-renderable-form error (E1, E2, E3, E4, E13). It is the
manifestation of R1 graceful degradation at runtime.

### Order of precedence

When multiple errors arise on the same slot exchange, the Player
applies them in this order:

1. **Transport** (E1, E13) — if the resolution document cannot be
   fetched in time, no later error can be evaluated. Fall through.
2. **Resolution-document level** (E2, E3) — if the document is
   absent or unparseable, no candidate can be evaluated. Fall
   through.
3. **Constraint surfacing** (E5, E6, E8) — for each candidate,
   validate against Publisher-declared constraints and the IAB
   vocabulary. Discarded candidates do not advance to playback.
4. **Per-candidate decode-time** (E10) — at the moment the Player
   commits to a candidate, decoder readiness is checked. Failure at
   this stage falls back to the next candidate.
5. **Per-candidate playback-time** (E11, E7 trim) — during the
   candidate's render, mid-stream failures and cap-trim apply.
6. **Tracking failures** (E12) — non-fatal, never affect playback.

The precedence is strict: a transport failure pre-empts every later
check; a decode-time failure on candidate N does not block the
evaluation of candidate N+1.

### Guarantees by actor

- **Publisher** — guarantees that ad opportunities are declared in
  the primary MPD with explicit slot constraints (allowed forms,
  allowed layouts mapped to IAB-defined names, max duration,
  concurrency caps). Guarantees that new constructs are introduced
  via the extension points enumerated in R1.2.
- **ADS** — guarantees that selected ads are returned in an
  ordered decision document (the ADS's authority over selection and
  order, R7). Does NOT guarantee constraint compliance (R2.2,
  R4.4, R5.4) — the Player enforces.
- **APS** — guarantees the resolution document is syntactically
  valid, that it transcribes the ADS decision verbatim (no
  reordering, no addition or removal of beacons — R5.1, R13.1),
  and that asset URLs resolve. Does NOT guarantee constraint
  compliance — the Player enforces.
- **Player** — guarantees that constraint validation happens for
  every candidate (R2.3), that the slot duration cap is enforced
  at actual rendered length (R4.5), that tracking beacons fire on
  schedule for accepted candidates (R13.2), and that any error
  produces a defined behaviour — render, fall back, or skip — per
  R3.2; undefined behaviour is non-conforming.

### Surfacing errors to the application layer

The Player MAY expose error events via implementation-defined APIs
(e.g. an `onAdError(slotId, candidateId, reason)` callback exposed
to embedding application code). The shape of this API is
**non-normative**; implementations are free to choose it. The spec's
chapter 9 (Implementation notes) SHOULD include guidance — for
example, an enumerated `reason` value set aligned with the
`E1..E13` matrix above — but does not bind a specific signature.
Application-layer error surfacing MUST NOT cause the Player to
deviate from the runtime obligations in the MUST column.

## References

- `../context/02-actors.md` — Publisher / ADS / APS / Player and
  their boundaries
- `../context/03-requirements.md` — R1..R7, R12, R13, R15 cited
  above; R20 cited for fallback semantics
- `../context/05-dash-linear-interfaces.md` — interface contracts
  table (HTTP / transport / format / direction / error semantics
  per actor pair)
- `../context/99-glossary.md` — terminology for "resolution
  document", "candidate", "form", "layout"
- `../context/08-dash-extension-rules.md` — DR-1..DR-7 (carrier
  rules cited indirectly through R1.2, R24.1)

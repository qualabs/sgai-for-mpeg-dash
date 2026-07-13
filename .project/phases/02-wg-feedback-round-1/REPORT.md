# Phase 02 — Working-group feedback round 1 — Closure report

**Phase:** `02-wg-feedback-round-1`
**Status:** closed (2026-07-13)
**Reviewer processed:** David Hassoun (WG contributor)

## 1. Summary

This phase processed the first round of working-group feedback on the SGAI
spec, centred on David Hassoun's review. The work started by cross-referencing
the 3 files he edited (round 1, 2026-05-20 session) against the current state of
`context/`, classifying each of his 10 items as already-addressed,
change-needed, or open-for-discussion. That report
(`hassoun-feedback-crossref.md`) was the phase's work product and the source of
truth for tasks T-01..T-08.

On that basis the three open decisions were resolved, the three documentation
edits were applied to `context/`, and the follow-up was closed. A second round
of David's feedback (Slack thread in `#wg-comcast`, 2026-05-29) closed the three
previously-open points plus a fourth (U1), consolidating the L-box model, the
content-dependent fallback for UC-07, and the pause-ad as a partial overlay. At
closure, all 10 of David's items are resolved and incorporated into `context/`.

## 2. Decisions made

- **Layout is not declared per device class** (T-04). The Publisher does not emit
  layouts per device class. The same outcome is achieved via a positional ordered
  fallback on the Player side (R5/R5.1/R5.2/R5.5/R5.6/R5.7) and, for uncovered
  regions, via an advertiser-supplied background. This preserves "device
  capability is the Player's sole authority" (R5/R5.4) and DP-1. Illustrated by
  UC-09.
- **L-box model** (T-04 / T-05, round 2). The L-box (L-shape / squeezeback) has a
  single ad creative (image, video, or web) always placed full-frame in the
  background, with the shrunk primary content composited on top. It is its own
  layout, modelled by the new R27; the side-by-side / double-box stays in R26.
- **Content-dependent fallback for legacy players** (T-02 / UC-07). For live
  content, skip-and-continue; for non-live / VOD, the Publisher may author a
  standard linear break as the fallback so the opportunity is monetised.
- **Pause-ad as a partial overlay** (T-06 / R21). R21 was relaxed from "the
  pause-ad MUST be fullscreen" to "the pause-ad MAY be fullscreen OR a partial
  overlay".
- **UC-02 and UC-06 stay separate** (T-03 / U1). The round-1 conflict is resolved
  in favour of the v1 decision: they remain discrete.

These decisions are recorded in `TASKS.md` and `.project/LOG.md`. No new formal
ADRs were created in this phase. The global ADR `0001` (defer spatial caps to IAB
CTV) is related context but predates the phase.

## 3. Tasks

All phase tasks are `done`:

- **T-01** — Cross-reference David's feedback against the current spec.
- **T-02** — UC-07: content-dependent fallback for legacy players.
- **T-03** — UC-02 vs UC-06: kept separate (David: "sounds good").
- **T-04** — Device-agnostic layout + Player-side intersection (UC-09).
- **T-05** — Background / L-box documented (R26 side-by-side, R27 L-shape).
- **T-06** — Pause-ad as a partial overlay (R21 relaxed).
- **T-07** — Rewrote the "CONFUSING" wording in UC-04 D2.
- **T-08** — ADS+APS split: incorporated and committed in the spec. The explicit
  confirmation with David remains an external, non-blocking follow-up.

No task was abandoned.

## 4. Open threads

- **Confirmation with David of the ADS+APS split** — external, non-blocking
  follow-up. The split is in the committed spec; what remains is David's explicit
  sign-off that it matches his intent behind the ADS to APS rename. To be raised
  in the next `#wg-comcast` exchange.
- **Other reviewers' feedback** — Alex Giladi, Thasso, SVTA Ads WG. Out of scope
  for this phase; they trigger a round-2 phase when that work arrives.
- **PR #6** — the spatial-caps conflict (issue #4 / ADR 0001) ran its course
  outside this phase; the phase did not manage it.

## 5. Risks that materialised

None material. David's feedback arrived outside the expected channel (he could
not edit the shared Doc, so he returned files with inline comments over Slack),
which added a manual cross-reference step but did not block or derail the phase.
The design points David pushed opposite to the v1 decision (UC-02 vs UC-06) were
closed by agreement without friction.

## 6. Recommendations for the next phase

- The project's long-term progression stays foundation -> design -> prototype ->
  closeout. PROJECT.md suggests a spec-iteration phase for foundation work; since
  the feedback phase is already numbered 02, the next iteration/feedback phase
  should open as `03-...`.
- If the next work is another round of WG feedback (more reviewers or a second
  pass), open `03-wg-feedback-round-2`. If instead the focus shifts to closing the
  foundational ADRs and adding the non-functional requirements document, open
  `03-spec-iteration`.
- Raise the David confirmation follow-up as the first external touchpoint of the
  next phase, to close the last round-1 thread.
- Do not open the next phase until Nicolas decides explicitly.

# Tasks — phase 02-wg-feedback-round-1

| id   | brief                                                                                   | status      | plan | evidence                                          |
| ---- | --------------------------------------------------------------------------------------- | ----------- | ---- | ------------------------------------------------- |
| T-01 | Cross-reference David Hassoun's feedback (3 files) against the current spec, classify    | done        | —    | `.project/phases/02-wg-feedback-round-1/hassoun-feedback-crossref.md` |
| T-02 | ❓ Resolve UC-07 legacy-player objection (skip-and-continue vs fallback to old ad exp)    | done        | —    | round 2 (2026-05-29) note below; `context/04-use-cases.md` UC-07 (content-dependent fallback); `context/07-backward-compat-checklist.md` §5 |
| T-03 | ❓ Resolve UC-02 vs UC-06 conflict (keep separate, with rationale, or combine)            | done        | —    | round 2 (2026-05-29): David "sounds good" — closed, keep separate (U1) |
| T-04 | ❓ Decide layout-per-device-class (device-agnostic + Player intersection vs per-class)    | done        | —    | `.project/LOG.md` 2026-05-27 entries; `context/03-requirements.md` R5/R5.1/R5.2/R5.5/R5.6/R5.7 + R26; **`context/04-use-cases.md` UC-09** (worked example proving per-class layout emerges from one ordered list) |
| T-05 | 🔧 Document background-image below the video in L-box layout (UC-03 + UC-04 D3)           | done        | —    | `context/03-requirements.md` R26 (+R26.1-3); `context/04-use-cases.md` UC-03 ad-response (L-box presentation option) + UC-04 D3/D4 + **UC-09 option 2** (L-shape) + **UC-10** (side-by-side three-element R26); `context/02-actors.md` Publisher background-fill sub-bullet |
| T-06 | 🔧 Allow pause-ad as a partial overlay (UC-08 / R17)                                      | done        | —    | round 2 (2026-05-29) note below; `context/03-requirements.md` R21 (relaxed) + R16/R17 refs; `context/04-use-cases.md` UC-08 |
| T-07 | 🔧 Clarify the "CONFUSING" wording in UC-04 D2                                            | done        | —    | `context/04-use-cases.md` UC-04 D2 (rewrote the "collapses to UC-02" sub-bullet to an explicit outcome) |
| T-08 | ✅ Confirm with David that the ADS+APS split matches his ADS→APS intent (A4)              | done        | —    | Split incorporated in the committed spec: `context/02-actors.md` (four-actor Publisher / ADS / APS / Player) + R2/R2.2. David confirmation is an external, non-blocking follow-up (see note below). |

T-01 produced the cross-reference report (the phase resource). T-02..T-08
are the actions the report surfaces: the 3 ❓ require Nicolas's decision,
the 3 🔧 are documentation / wording edits to `context/`, and T-08 is the
single ✅ follow-up. Resolutions that touch the spec are applied as
separate iterations on `context/`, not in this phase's governance folder.

## Decision / action notes (2026-05-27)

- **T-04 — DECIDED (done) + ILLUSTRATED.** Resolved together with the
  ordered-fallback question. Decision: the Publisher does **not** declare
  layouts per device class. The same outcome is achieved (a) Player-side via a
  **positional ordered fallback** — the resolution document lists presentation
  options (form + layout) in document order and the Player renders the first
  option it can satisfy (R5/R5.1/R5.2/R5.5/R5.6/R5.7), and (b) for empty
  regions, via an **advertiser-supplied background** (R26, underlay model),
  mirroring the IAB CTV vocabulary the spec defers to. Keeping per-device-class
  out of the Publisher preserves "device capability is the Player's sole
  authority" (R5/R5.4) and DP-1. Full rationale + IAB citation in
  `.project/LOG.md`. **New (2026-05-27):** the decision is now also *illustrated*
  by **UC-09** — a worked example where one ordered list, emitted identically to
  every viewer with one device-agnostic allowed-layout set, lands D1..D5 on three
  different layouts purely Player-side. Directly answers Hassoun A3.

- **T-05 — done + ILLUSTRATED.** Background-image-below-video (L-box) is now a
  documented case: new requirement **R26** (advertiser creative as a full-frame
  underlay with a cutout; platform fallback is an opt-in MAY with no normative
  default), plus the L-box presentation option in UC-03 and the rewritten UC-04
  D3/D4. **New (2026-05-27):** the L-shape vs side-by-side distinction is now
  illustrated concretely in **UC-09** (L-shape as option 2, no background) and
  **UC-10** (side-by-side as the three-element R26 case with the background
  fill). Closes Hassoun U2/U4.

- **T-07 — done.** The UC-04 D2 sub-bullet no longer says the experience
  "collapses to UC-02"; it now states the outcome explicitly (full-screen
  linear ad of bounded duration, no overlay, primary content resumes on
  completion). Closes Hassoun U3.

- **T-03 — parked by owner.** UC-02 vs UC-06 stays unchanged for now
  ("por ahora no hacer nada con esto", Nicolás 2026-05-27). The cross-ref
  conflict with David's combine-suggestion is acknowledged but deferred;
  the spec keeps them separate per the v1 decision.

- **T-02, T-06, T-08 — still pending.** T-02 (UC-07 legacy-player objection)
  and T-08 (confirm the ADS+APS split with David) await action. T-06 (pause-ad
  as a partial overlay) was **not** addressed by the 2026-05-27 edits — it
  remains open and conflicts with R21 (pause-ad fullscreen), which needs a
  separate resolution.

## Round 2 — David Hassoun feedback (Slack thread #wg-comcast, 2026-05-29)

A second round of feedback arrived as a Slack thread (distinct from the
file-based round 1). It resolves three of the previously-open / documentation
points and closes a fourth; A4 stays open.

- **U2 / U4 — L-box MODEL SETTLED (T-04 / T-05 revisited, done).** David objected
  to an earlier model that treated the L-box as a full-frame ad with a cutout
  and **no background**: *"I'm not sure I totally agree with the L-Box. Yes it
  can be done with a cutout image (with transparency), but it could also be a
  background image - no transparency. It could reasonably be bg image, content
  on top, ad video or static on side and or bottom."* Nicolás closed the debate:
  *"Lets agree on this: Lbox is ALWAYS a background image/video/web"* and *"so
  lets not call it background image, is just 'the image/web/video for the
  LBOX'"* — David reacted 👍. **Agreed model:** the L-box (L-shape / squeezeback)
  has **one** ad creative — image, video, or web/HTML, a single URL the ADS gives
  — that is **always** placed **full-frame in the background**, with the shrunk
  primary content composited on top of it. Two on-screen elements (full-frame ad
  creative + shrunk primary content); no separate third filler element — the ad
  creative is itself the background. The L-box is **its own layout, NOT a case of
  R26** (R26 is the side-by-side / double-box, whose two boxes leave an uncovered
  region a distinct third element must fill — the L-box has no such region).
  Applied to `context/`: **R26 scoped back to side-by-side only**; **new R27**
  models the L-shape / squeezeback (full-frame ad creative + shrunk primary
  content, presentation option under R5, own R27.1/.2/.3 decoder budget; next free
  number, no renumbering); UC-03 layout taxonomy, UC-04 D3/D4, UC-09 option 2 +
  per-class analysis, and UC-10 reconciled to the two-element L-shape model.
  UC-09 option 2 is an **L-shape with an image full-frame ad creative** (one
  decoder for the shrunk primary content + an image surface for the background
  creative), which preserves the worked-example outcomes (D3/D4 → L-shape,
  D1 → side-by-side, D2/D5 → takeover).

- **U5 / UC-07 — content-dependent fallback (T-02, done).** David: *"It should
  skip OR use standard break depending on content options. If live and real
  content then skip otherwise use will lose content."* The legacy-player
  behaviour is now documented as **content-dependent**: for **live** content,
  skip-and-continue (cannot pause live to splice without losing content, R1
  applies); for **non-live / VOD**, the Publisher MAY / SHOULD author a standard
  linear break (baseline constructs a legacy Player renders) as the fallback,
  so the opportunity is monetised instead of lost. Applied to UC-07 +
  `07-backward-compat-checklist.md` §5.

- **U6 / R21 — pause-ad partial overlay (T-06, done).** David confirmed the
  fullscreen-only rule is a spec oversight: *"i think thats an oversight in
  spec... I have seen partial screen pause ad overlays."* R21 relaxed from
  "pause-ad MUST be fullscreen" to "pause-ad MAY be fullscreen OR a partial
  overlay"; R21.1, R16 / R17 cross-refs, and UC-08 adjusted; R22 single-active-
  form coherence preserved.

- **U1 / UC-02 vs UC-06 — CLOSED (T-03, done).** David reacted "sounds good" to
  keeping the two use cases separate; the round-1 conflict is resolved in favour
  of the v1 decision (keep them discrete for the test-generation workflow). No
  spec change.

- **A4 — RESOLVED IN SPEC, confirmation is external follow-up (T-08, done).**
  The ADS + APS split (four-actor Publisher / ADS / APS / Player model) is
  incorporated and committed in `context/02-actors.md` and R2/R2.2. The point is
  considered resolved on the spec side. The lightweight confirmation with David
  that the split matches his ADS→APS rename intent is treated as an **external,
  non-blocking follow-up** — it does not gate the phase close and carries over as
  an external touchpoint (to raise in the next `#wg-comcast` exchange with David).

## Phase close (2026-07-13)

All of David Hassoun's round-1 feedback (10 items) is resolved and incorporated
into `context/`. Round 2 of his feedback (Slack thread, 2026-05-29) closed the
three previously-open / documentation points and the fourth (U1). T-08, the one
remaining follow-up, is given `done`: the ADS+APS split is in the committed spec;
David's explicit confirmation is an external, non-blocking follow-up.

Separately from David's feedback, a **later spec-refinement iteration** (commit
`97e6f71`, 2026-07-13) landed changes that are **this project's own scope**, not
part of David's review: R28 (ClickThrough carrier as a normative requirement),
R23 narrowed to a generic best-effort carrier, R26 scoped to image-only fill,
new use-cases UC-11 (R28) and UC-12 (R20), SVTA namespace alignment, and the
`CLAUDE.md` rule that requirements must be self-contained and concise. This is
recorded as context for the close (it is part of everything worked up to the
close) and is intentionally **not** attributed to tasks T-01..T-07, which are
David's feedback resolutions.

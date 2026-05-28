# Tasks — phase 02-wg-feedback-round-1

| id   | brief                                                                                   | status      | plan | evidence                                          |
| ---- | --------------------------------------------------------------------------------------- | ----------- | ---- | ------------------------------------------------- |
| T-01 | Cross-reference David Hassoun's feedback (3 files) against the current spec, classify    | done        | —    | `.project/phases/02-wg-feedback-round-1/hassoun-feedback-crossref.md` |
| T-02 | ❓ Resolve UC-07 legacy-player objection (skip-and-continue vs fallback to old ad exp)    | pending     | —    | —                                                 |
| T-03 | ❓ Resolve UC-02 vs UC-06 conflict (keep separate, with rationale, or combine)            | pending     | —    | —                                                 |
| T-04 | ❓ Decide layout-per-device-class (device-agnostic + Player intersection vs per-class)    | done        | —    | `.project/LOG.md` 2026-05-27 entries; `context/03-requirements.md` R5/R5.1/R5.2/R5.5/R5.6/R5.7 + R26; **`context/04-use-cases.md` UC-09** (worked example proving per-class layout emerges from one ordered list) |
| T-05 | 🔧 Document background-image below the video in L-box layout (UC-03 + UC-04 D3)           | done        | —    | `context/03-requirements.md` R26 (+R26.1-3); `context/04-use-cases.md` UC-03 ad-response (L-box presentation option) + UC-04 D3/D4 + **UC-09 option 2** (L-shape) + **UC-10** (side-by-side three-element R26); `context/02-actors.md` Publisher background-fill sub-bullet |
| T-06 | 🔧 Allow pause-ad as a partial overlay (UC-08 / R17)                                      | pending     | —    | —                                                 |
| T-07 | 🔧 Clarify the "CONFUSING" wording in UC-04 D2                                            | done        | —    | `context/04-use-cases.md` UC-04 D2 (rewrote the "collapses to UC-02" sub-bullet to an explicit outcome) |
| T-08 | ✅ Confirm with David that the ADS+APS split matches his ADS→APS intent (A4)              | pending     | —    | —                                                 |

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

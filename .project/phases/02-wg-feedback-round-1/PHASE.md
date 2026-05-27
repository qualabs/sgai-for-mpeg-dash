---
phase: 02-wg-feedback-round-1
title: Working-group feedback — round 1
status: in-progress
started: 2026-05-27
closed: null
---

# 02-wg-feedback-round-1

Process working-group feedback **round 1** on the SGAI spec — starting
with **David Hassoun's** review (the 3 spec files he edited and
commented during the 2026-05-20 WG session). Each piece of feedback is
classified as **already-addressed (✅)**, **change-needed (🔧)**, or
**open-for-discussion (❓)**, and the resolutions are driven from there.

The cross-reference report is the work product of this phase: it maps
David's 10 feedback items against the current state of `context/`
(post commit `fb30314`, the four-actor Publisher / ADS / APS / Player
revision) and projects the next actions. See the phase resource
[`hassoun-feedback-crossref.md`](hassoun-feedback-crossref.md).

## Objective

Process working-group feedback round 1 on the SGAI spec — starting with
David Hassoun's review (his 3 edited files from the WG) — classifying
each point as already-addressed / change-needed / open-for-discussion,
and driving the resolutions.

## Context

- **WG review of 2026-05-20**: David Hassoun reviewed the SGAI spec and
  returned feedback during the Comcast WG session. He could not edit
  the shared doc directly, so he downloaded 3 `context/` files, marked
  them with inline `//ISSUE` / `//` comments (plus 2 text renames in
  `02-actors.md`), and posted them to `#wg-comcast`.
- **David's files** (the 3 he returned):
  - `02-actors.md` — 2 text edits + 4 inline `//ISSUE` comments.
  - `04-use-cases.md` — 6 inline comments (no text edits).
  - `03-requirements.md` — untouched (no feedback at all).
- **The cross-reference vs the current spec**: David's feedback was
  captured against the spec state he received (commit `c983ff7`, the
  three-actor Broadcaster / ADS / Player model, before R19–R25). The
  report crosses it against the **current** spec state, post commit
  `fb30314` (four-actor Publisher / ADS / APS / Player, +R19–R25) — so
  some of David's points are already addressed by changes that landed
  after his review.

## Scope

- **Round 1 = David Hassoun.** This phase processes only David's review
  from 2026-05-20: cross-reference his feedback against the current
  spec, classify each point, and drive the resolutions.
- Future feedback rounds, or reviews from other reviewers (e.g. Alex
  Giladi, Thasso, SVTA Ads WG), are **out of scope for this phase** —
  they become follow-on phases (`03-wg-feedback-round-2`, …) or
  sub-sections, depending on volume.

## Out of scope

- Modifying the spec (`context/`) in this phase's governance work. The
  resolutions identified here drive spec edits as separate tasks /
  iterations; the phase folder holds the analysis and the audit trail,
  not the spec changes themselves.
- Resolving the open PR #6 conflict (separate task, pending Nicolas's
  validation).
- Other reviewers' feedback (future rounds).

## The 10 feedback items (summary)

From the cross-reference report, David left 10 feedback pieces:

- **✅ Already addressed (4):** Publisher rename (`02#L15`), ADS→APS /
  naming conflict resolved via the actor split (`02#L9`+`L38`), ADS
  acronym expanded on first reference (`02#L9`), Player "select" issue
  (`02#L98`) covered by the atomised R5/R7 chain.
- **🔧 Change-needed (3):** background-image below the video in an L-box
  layout (`02#L26` + `04` UC-03 `#L242` + UC-04 D3 `#L423`); UC-08
  "pause-ad can be a partial overlay" (`04#L702`); UC-04 D2 "CONFUSING"
  wording (`04#L419`).
- **❓ Open for discussion (3):** UC-02 "why limit to 1 vs combine with
  UC-06?" (`04#L170`) — David pushes the **opposite** way to Nicolas's
  decision to keep them separate; UC-07 "this is bad — should use old
  ad experience" (`04#L653`) — David objects to the legacy-player
  behaviour; layout-per-device as an open question (`02#L26`).

## Stakeholders

- **Reviewer**: David Hassoun (WG contributor).
- **Decision owner**: Nicolás Levy (CTO) — owns the 3 ❓ design
  decisions and approves the 3 🔧 documentation edits.
- **Venue**: Comcast WG (`#wg-comcast`).

## Resource

- [`hassoun-feedback-crossref.md`](hassoun-feedback-crossref.md) — the
  cross-reference report (English). Maps each of David's 10 feedback
  items against the current spec, with classification (✅ / 🔧 / ❓),
  provenance (file + line numbers from David's returned files), and a
  prioritised next-steps list. This is the phase's primary work
  product and the source of truth for the tasks in `TASKS.md`.

## Recommendation for next phase

Once round-1 resolutions are driven to closure (the 3 ❓ decisions
made, the 3 🔧 edits applied to `context/`, and the 1 ✅ follow-up —
confirming with David that the ADS+APS split matches his intent — sent),
the natural follow-up is **round 2**: collect the next batch of WG
feedback (additional reviewers or a second pass from David), and open
`03-wg-feedback-round-2`. Open it explicitly when that work starts.

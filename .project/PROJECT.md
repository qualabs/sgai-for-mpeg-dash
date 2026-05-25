---
name: SGAI for MPEG-DASH
slug: sgai-for-mpeg-dash
description: >
  Design a complete Server-Guided Ad Insertion (SGAI) specification for
  MPEG-DASH covering **linear and non-linear ads**, extending
  MPEG-DASH 6th edition. Linear SGAI already exists in 6th edition
  (InsertPresentation / ReplacePresentation / ListMPD) and is
  absorbed as the baseline; the principal design delta is the
  non-linear extension (overlays, pause ads, L-shapes, banners,
  side-by-side, fullscreen interactive layers) coexisting with the
  linear flow under the same architecture. Dual output: spec
  (working doc shared with the industry) + working prototype.
  Collaboration with SVTA Ads WG and MPEG-DASH contributors
  (Alex Giladi from Netflix, Thasso from Castlabs, Thomas
  Stockhammer chair of MPEG-DASH).
status: ongoing
type: research
owner: nicolas-levy
started: 2026-05-06
last_update: 2026-05-11
tags: [dash, sgai, non-linear-ads, mpeg, comcast, svta, overlays, dynamic-presentation, prototype, spec, server-guided-ads]
related_processes: [preparacion-working-group]
related_wgs: [comcast-sgai, svta-ads]
---

# SGAI for MPEG-DASH

Project hub. Substantive content lives in files referenced from
here — this `PROJECT.md` is only navigation + phases.

## Objective and motivation

Design a **complete Server-Guided Ad Insertion (SGAI) specification for
MPEG-DASH** covering **linear and non-linear ads** as a single
coherent extension of **MPEG-DASH 6th edition**.

- **Linear** already exists in 6th edition (`InsertPresentation` /
  `ReplacePresentation` resolving a `ListMPD` returned by an
  external Ad Decision Server). The spec absorbs that mechanism as
  the **baseline**, clarifies it, and may add minor extensions
  where the gap analysis justifies them.
- **Non-linear** is the **principal design delta**: cover non-linear
  surfaces (overlays, side-by-side, pause ads, L-shapes, banners,
  corner bugs, fullscreen interactive layers) reusing the same
  pattern — *MPD event → resolution document → Player composes the
  result* — without fragmenting the architecture.

The final output is a single SGAI spec that an implementer can
follow to cover both cases.

## Expected output

Two deliverables:

1. **Complete technical spec** of SGAI for MPEG-DASH (linear +
   non-linear), written collaboratively in a Google Doc shared
   with the industry. Destination: land in the **MPEG-DASH WG** as
   the starting point for a formal extension of the standard.
2. **Working prototype** demonstrating the proposal end-to-end on
   a real DASH player, with coexistence of linear and non-linear
   ad slots in the same playback session.

## Stakeholders

At the level of organizations and public roles (no internal
personal info — see `knowledge/output-policy.md`):

- **Qualabs Working Group** (internal) — weekly WG that advances
  spec and prototype. Relevant public roles: Chief Solution
  Architect (technical lead + representation in SVTA Ads WG), CTO
  Nicolás Levy (customer relationship + strategic positioning in
  MPEG / SVTA). The formal technical actor model lives in
  `context/02-actors.md`.
- **Comcast** — sponsor and primary customer of the WG that
  produced the linear SGAI in DASH 6th edition. Funds and
  prioritizes the non-linear extension.
- **SVTA Advertisement WG** — socialization venue outside Comcast.
  Cadence and slot to be arranged.
- **DASH Industry Forum (DASH-IF)** — interop and guidelines on
  top of the base spec.
- **MPEG-DASH WG** (MPEG Systems WG that hosts DASH) — formal
  standards body. Chair: **Thomas Stockhammer**.
- **Identified external contributors**: Alex Giladi (Netflix,
  likely reviewer at stable v0.x), Thasso (Castlabs,
  prototype-side validation), Olivier Cortambert (detailed
  comments on the split of timeline-triggered overlays vs
  action-triggered pause ads).

## Relevant standards

- **MPEG-DASH 6th edition** (ISO/IEC 23009-1) — base on which this
  proposal extends. `InsertPresentation`, `ReplacePresentation`,
  `ListMPD`.
- **IAB CTV Ad Standard** — flexible-ratio formats (8:1, 6:1, 1:4,
  etc.) that this proposal references instead of redefining its
  own layout system. R10 aligns explicitly with it.
- **SCTE-35** (ANSI/SCTE digital program insertion cueing) —
  markers consumed by the prototype via Morpheus, converted into
  DASH dynamic events.

## How the project is organized

| File / folder | Contents |
| --- | --- |
| `README.md` | User-facing entry doc: what the project does, layout, how to regenerate artefacts. |
| `CLAUDE.md` | Conventions for subagents touching this project. |
| `context/01-intro.md` | Objective of the docs body and index of the canonical set. Technical entry point. |
| `context/02-actors.md` | Self-contained three-actor model: Broadcaster, ADS, Player. Boundary summary and per-actor responsibilities. |
| `context/03-requirements.md` | Requirements R1–R10 (functional + governance), out of scope, and design characteristics satisfying the Rs. |
| `context/04-use-cases.md` | Device classes D1–D5 and the 7 scenarios (UC-01..UC-07), each with expected behavior per device class. Scenario-first structure: the broadcaster validates a scenario against its full device fauna, not isolated cases. |
| `context/05-dash-linear-interfaces.md` | Reference of how SGAI is implemented today for linear ads in DASH 6th edition: inventory of the interfaces between the three actors, end-to-end message flow with concrete MPDs and ListMPDs, VAST → ListMPD mapping. Foundation on which the non-linear proposal extends. |
| `context/99-glossary.md` | Glossary of the technical terminology used across the docs set. Entries marked *(proposed)* are constructs that this proposal puts on the table. |
| `analysis/dash-gap-analysis.md` | Generated artefact: mapping of each UC against MPEG-DASH 6th edition (ISO/IEC 23009-1) — what construct exists today, how it covers the case per device class, what is missing. Regenerable via `prompts/1-pre-spec/analyze-dash-gap.prompt`. |
| `prompts/` | Build scripts in `.prompt` format with Inputs / Output / Skip if header, grouped by pipeline stage: `1-pre-spec/` (gap, UC coverage, error semantics, conformance assertions, IAB ad templates), `2-build/` (build-spec), `3-post-spec/` (validate-spec, review-spec-details, audit-dash-conformance), `4-auto-refine/` (refine-spec, compare-spec-versions). The `build-all` orchestrator lives at the root of `prompts/`. See `prompts/README.md` for the full layout and a "when to use which prompt" table. |
| `output/` | Final builds of the spec document, with dated filename (`YYYY-MM-DD-sgai-spec.md`). Not overwritten — the build history is preserved. |
| `proposal-drafts/` | Historical iterations of the spec in Google Doc form, one per file, with date and version (`YYYY-MM-DD-vN.md`). Internal drafts that do NOT live in the shared Doc. Kept as historical reference. |
| `.project/decisions/` | Numbered ADRs (Architecture Decision Records). One material decision per file. Immutable — if a decision is superseded, another ADR is created marking it as replaced. |
| `.project/LOG.md` | Chronological logbook of the project. One entry per work session or material action. Append-only. |
| `.project/phases/` | Phase folders with `PHASE.md` and `TASKS.md`. |

Folders created when their first file appears (not created
preemptively): `.project/meeting-notes/`, `references/`,
`external-collab/`, `prototype/`.

## Shared working doc in Drive

- URL: https://docs.google.com/document/d/1CWm1BP65h45iJ5RwCAQkUAZ6lz7f-w3qJRGMdH8DDdQ/edit
- Current title: *"Proposal for Non-Linear SGAI Ad Insertion"*.
- Audience: WG Qualabs, Comcast, SVTA Ads WG, MPEG-DASH
  contributors.
- Edit the Doc using rule 7.0.1 in `CLAUDE.md` (Docs API
  `documents.batchUpdate` surgical, NEVER `gws drive files update
  --upload`).
- The repo does NOT automatically reflect changes from the Doc.
  When the Doc changes (comments, edits by others), the repo
  keeps its version and we reconcile manually. If you want a
  fresh snapshot of the Doc in the repo, generate a new file in
  `proposal-drafts/` with the snapshot date.

## Phases

Phase folders live under `.project/phases/`. Only the phase that is
actively scoped has a folder — future phases are described here in
the long-range plan and get a folder when they open.

### Current state

- **`01-setup` — `closed`** (2026-05-11). Bootstrap of the project:
  repo layout, build pipeline (3 prompts), governance scaffolding
  under `.project/`, a first iteration of the spec set in `context/`
  (6 files), first generated artefact
  (`analysis/dash-gap-analysis.md`), operational config (`SETUP.md`,
  `.env.agent.example`, `.gitignore`), and `git init` with an
  initial commit. See `phases/01-setup/` for PHASE.md and TASKS.md
  (the close report is embedded in PHASE.md).

### Long-range plan

The narrative of the project — once setup is done — remains a
foundation → design → prototype → closeout progression. Each phase
opens explicitly when its predecessor closes (or when Nicolas
decides to pivot).

**Foundation / spec iteration** — validate the foundation set
(actors, use cases, functional + non-functional requirements) with
the internal Qualabs WG (weekly) and Comcast (monthly). Capture
feedback as iterations on the existing `context/` files. Close
foundational ADRs (actor model, rename, layout deferral, pause-ads
split, IAB CTV alignment) and add the non-functional requirements
doc. Suggested slug for the folder: `02-spec-iteration`.

**Design** — produce one or more concrete design candidates (MPD
event structure, schema, syntax, concrete examples). Iterate via
`proposal-drafts/<date>-v<n>.md`. Close design-level ADRs.
Decision matrix comparing candidates vs UCs and requirements.

**Prototype** — implement one or more designs end-to-end as a working
prototype. Tentative stack (to confirm at phase open): dash.js or
Shaka as base player, Morpheus for SCTE-35, Gemini for
overlay-template generation. Prototype code (in this folder or in an
external repo), run instructions, recorded demo.

**Closeout** — final proposal packaging, learnings recap, publication-
ready artifacts. Final doc in shareable format, learnings summary,
pull request or equivalent to the MPEG-DASH repo if applicable.

### External touchpoints — transversal

Engagements with **SVTA Ads WG**, **Alex Giladi (Netflix)**, **Thasso
(Castlabs)**, and **Thomas Stockhammer (MPEG-DASH chair)** are
transversal — they fire when the artifacts are mature enough to
share, not as a dedicated phase. Each touchpoint is logged in
`LOG.md` and feedback may inform iterations within the active phase.

## Cadence and artefacts

- **Internal Qualabs WG**: weekly cadence. Minutes are processed
  by the `cto-minutes` process and indexed with tags `Comcast` /
  `SGAI`. For prep use the `preparacion-working-group` process.
- **Sessions with Comcast customer**: monthly. Spec decisions
  affecting the customer are discussed there.
- **Recap posted to `#wg-comcast`**: after each internal session,
  recap applying `knowledge/output-policy.md` and disclaimer
  "generated by AI" if applicable.

## How to send me tasks (for Nicolas)

When you send me a task for this project, you can reference it
with the prefix "tarea SGAI:". I assume this project as context
and work inside its folder.

Typical patterns:
- "tarea SGAI: armá el ADR del rename DynamicPresentation"
- "tarea SGAI: revisá la sección de schema del working doc y dame
  3 alternativas para el atributo content_type"
- "tarea SGAI: prep para el WG del jueves"
- "tarea SGAI: redactá el mensaje al SVTA Ads WG presentando la
  propuesta"
- "tarea SGAI: investigá X y proponé un draft, lo revisamos juntos"

When I receive a research / spec generation task:
- If the decision is new and material → new ADR in `decisions/`.
- If it touches proposal content → new iteration in
  `proposal-drafts/` (I do not edit prior ones; they remain
  immutable).
- If it changes anything in the immutable context → update of
  `PROJECT.md` (objective, motivation, stakeholders, standards
  sections).
- Always → new entry in `LOG.md`.
- I only merge into the shared Doc when you explicitly say "this
  version ships".

## Risks / blockers

- **DASH 6th edition support in real players**: the prototype
  needs a player that understands Insert/ReplacePresentation.
  Validate against at least 2 players (dash.js + Shaka or
  Castlabs) before closing the spec.
- **Coordination with MPEG WG** (roughly quarterly cadence): if
  the proposal does not reach a WG slot, a quarter is lost. Keep
  sync with Alex Giladi and Thasso to avoid clashing with their
  deliverables.
- **"Build first" vs "spec first" tension**: the Comcast WG
  decision of 2026-04-29 was "build first, spec later". Hold
  that stance when pressure appears to amend the spec before
  validating with the prototype.
- **Brand safety guardrails** (model serving + prompt engineering
  + content filtering): significant AI work, do not underestimate.

## Open threads (snapshot at close of 2026-05-06)

- [ ] **Spec — DynamicPresentation syntax**: `content_type`
  attribute vs `DynamicReplacePresentation` /
  `DynamicInsertPresentation` sub-types. Owner: Nico + David.
- [ ] **Spec — player workflow**: how the player decides which
  workflow to use before fetching the dynamic MPD.
- [ ] **Spec — split pause-ads from the timeline flow**: separate
  pause-ads as a distinct type (action-triggered) from
  OverlayPresentation (timeline-triggered). Surfaces from
  Olivier's thread.
- [ ] **Spec — alignment with IAB CTV Ad Standard**: the
  Positioning Templates section must reference the IAB spec.
  Pending official publication from IAB.
- [ ] **Prototype — dynamic user parameters** (wire from the
  client to the manifest).
- [ ] **Prototype — brand safety guardrails**.
- [ ] **External — SVTA Ads WG**: confirm regular slot.
- [ ] **External — Alex Giladi**: opportunity when the proposal
  reaches v0.3 or v0.4.
- [ ] **External — Thasso (Castlabs)**: contact to be identified;
  ask him for an intro to JP.
- [ ] **Working doc — title rename** (still says
  "OverlayPresentation"; pending until the rename decision is
  fully closed).

For details on each thread, see the corresponding ADR or the
relevant entry in `LOG.md`.

---
phase: 01-setup
title: Project setup
status: closed
started: 2026-05-11
closed: 2026-05-11
---

# 01-setup

Bootstrap the project: stand up the repo layout, the build pipeline,
the governance scaffolding, and a first iteration of the spec inputs
so the project can be used and iterated on by humans and LLM agents.

This phase is closed in-place — the work was done during the session
of 2026-05-11. The deliverables of this phase are the conditions
that enable any subsequent phase (spec iteration, design, prototype).

## Scope

- **Repo layout**: top-level folders (`spec/`, `prompts/`, `analysis/`,
  `output/`, `proposal-drafts/`, `.project/`), with README and CLAUDE
  documenting conventions for human readers and subagents.
- **Build pipeline**: three `.prompt` files (`analyze-dash-gap`,
  `build-norm`, `build-all` orchestrator) that any LLM-driven agent
  can invoke from the project root. Skip-if-fresh logic on each
  prompt so re-runs are cheap.
- **Governance scaffolding**: `.project/PROJECT.md` (project hub),
  `.project/LOG.md` (append-only bitácora), `.project/decisions/`
  (ADRs), `.project/phases/` (this folder).
- **Initial spec set**: 6 files in `spec/` covering intro, actors,
  requirements, use cases, DASH linear interfaces, glossary.
- **Operational config**: `SETUP.md` explaining setup paths,
  `.env.agent` + `.env.agent.example` for optional per-user config
  (NotebookLM grounding), `.gitignore` excluding user-specific files.
- **Versioning**: `git init` in the project folder so the spec set
  evolves with auditable history. The repo is local-only — no
  remote is configured at the end of this phase.

## Out of scope

- Spec iteration based on WG feedback (validating actors, use cases,
  requirements with internal Qualabs WG and Comcast). That is the
  next phase.
- Concrete design candidates (MPD event structure, schema syntax).
  Future phase.
- Prototype implementation. Future phase.

## Outputs

- `README.md`, `CLAUDE.md`, `SETUP.md` at the project root.
- `.env.agent.example` (tracked) + `.env.agent` (gitignored).
- `.gitignore` at the project root.
- `prompts/analyze-dash-gap.prompt`, `prompts/build-norm.prompt`,
  `prompts/build-all.prompt`.
- `spec/01-intro.md`, `spec/02-actors.md`, `spec/03-requirements.md`,
  `spec/04-use-cases.md`, `spec/05-dash-linear-interfaces.md`,
  `spec/99-glossary.md`.
- `analysis/dash-gap-analysis.md` (first generated artefact).
- `.project/PROJECT.md`, `.project/LOG.md`, `.project/decisions/`,
  `.project/phases/01-setup/`.
- A local git repository (`.git/`) with an initial commit capturing
  the state at phase close.

## Recommendation for next phase

The natural follow-up is a **spec iteration** phase: validate the
foundation set (actors, use cases, requirements) with the internal
Qualabs WG and Comcast, capture feedback as iterations on the
existing `spec/` files, and close foundational ADRs as decisions
emerge. Suggested slug: `02-spec-iteration`. Not opened by this
phase — open it explicitly when starting that work.

See the closing summary below.

---

## Close report

**Phase**: `01-setup` · **Status**: closed · **Dates**: 2026-05-11
(opened and closed in-place).

### Summary

Stood up the project end-to-end: repo layout, three-prompt build
pipeline (analyze-dash-gap, build-norm, build-all), governance
scaffolding under `.project/`, a first iteration of the spec set in
`spec/` (6 files), the first generated artefact
(`analysis/dash-gap-analysis.md`), operational config
(`SETUP.md`, `.env.agent` + `.env.agent.example`, `.gitignore`), and
local versioning via `git init` with an initial commit.

NotebookLM grounding was made **optional**: the three prompts now
work with or without the `notebooklm` skill installed. With the skill
and a populated `.env.agent`, prompts ground their output against the
configured notebook (recommended for fidelity against MPEG-DASH 6th
edition). Without it, prompts proceed using only the contents of
`spec/`; outputs are less authoritative but the build completes.

### Decisions

- **One setup phase** instead of the previous 4-phase model
  (foundation / design / prototype / closeout) baked into
  `.project/phases/`. Rationale: the 4-phase model was projecting
  too far ahead while the setup was still in flux. We collapsed the
  initial scaffolding work into a single `01-setup` and will open
  follow-on phases (`02-spec-iteration`, design, prototype, closeout)
  explicitly as the work demands. The 4-phase narrative remains
  documented in `PROJECT.md` as the long-range plan.
- **Local-only git** (no remote configured). Reversibility comes from
  filesystem + local history. A remote can be added later without
  rewriting history.
- **NotebookLM optional, audit-logged**: each prompt emits
  `[GROUNDED_BY=notebooklm]` or `[GROUNDED_BY=spec-only]` so any
  consumer of the output can tell which grounding was used.

### Tasks (recap)

- **T-01 — Repo + workflow**: done. README, CLAUDE, SETUP,
  `.env.agent.example`, `.gitignore`, three prompts, governance
  files, initial git commit.
- **T-02 — Specs iniciales**: done. Six files in `spec/` covering
  intro, actors, requirements, use cases, DASH linear interfaces,
  glossary.

See `TASKS.md` for the full evidence list per task.

# Setup

This project can be run with zero external dependencies — clone, read,
and invoke the prompts in `prompts/` from any LLM-driven agent. For
**better grounding against the MPEG-DASH 6th edition specification**,
install the optional NotebookLM skill.

## Quick start

1. Read `context/01-intro.md` for an overview.
2. Read `README.md` for the project layout.
3. To regenerate the gap analysis: invoke
   `prompts/1-pre-spec/analyze-dash-gap.prompt`.
4. To build the spec: invoke `prompts/2-build/build-spec.prompt`.
5. To run the full pipeline with skip-if-fresh logic (orchestrator
   over `1-pre-spec/`, `2-build/`, `3-post-spec/`, and the
   `4-auto-refine/` convergence loop): invoke
   `prompts/build-all.prompt`. See `prompts/README.md` for the
   folder layout and a per-prompt usage guide.

Without NotebookLM, the prompts ground the analysis on `context/`
content alone. Outputs are less authoritative but the build
completes successfully.

## Optional: NotebookLM grounding

For higher-fidelity validation against the MPEG-DASH 6th edition spec
(ISO/IEC 23009-1:2025) and other authoritative sources, install the
NotebookLM skill:

  - Skill repo: https://github.com/PleasePrompto/notebooklm-skill
  - Follow the install instructions in that repo.
  - Set up a NotebookLM notebook containing the MPEG-DASH 6th edition
    spec (and optionally VAST 4.x docs, IAB CTV guidelines).

### Configure `.env.agent`

Once the skill is installed, copy the env example and point it at
your notebook:

    cp .env.agent.example .env.agent
    # Edit .env.agent and set NOTEBOOK_ID to the UUID of your
    # NotebookLM notebook. Get the UUID from the URL of your
    # notebook in notebooklm.google.com — it is the last path
    # segment, e.g. for
    # https://notebooklm.google.com/notebook/bb67e20c-9ad1-4a1d-a641-7c7d901f93cb
    # the UUID is `bb67e20c-9ad1-4a1d-a641-7c7d901f93cb`.

The prompts read `NOTEBOOK_ID` from `.env.agent` and resolve it via
the skill at runtime. Using the UUID (instead of the notebook's
display name) gives an exact, robust match that does not break when
the notebook is renamed. `.env.agent` is gitignored so your personal
notebook UUID does not leak into the repo.

## Why this matters

Without NotebookLM, the prompts rely on the model's training data
for any reference to MPEG-DASH or VAST internals. That works for
common patterns but the model may hallucinate attribute names,
section references, or version numbers. With NotebookLM grounded
to the actual spec, the analysis and spec cite the canonical source.

See `prompts/*.prompt` headers — each prompt logs
`[GROUNDED_BY=notebooklm]` or `[GROUNDED_BY=spec-only]` per run so
the audit trail is clear.

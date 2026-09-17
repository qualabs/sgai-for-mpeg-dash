# Setup

This project is written against a specific edition of MPEG-DASH, and
the build will not start without a copy of it. That copy is a licensed
document, so it is not in this repository and you supply your own —
see **The base standard** below. Everything else — clone, read, invoke
the prompts in `prompts/` from any LLM-driven agent — needs nothing
installed.

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

`bin/check-normative-base.py` runs before anything is generated and
stops the build if the declared edition does not describe the file you
supplied. `bin/check-context-coherence.py` runs next and stops it if
`context/` does not hold together.

## The base standard

Every step that makes a claim about MPEG-DASH grounds it against the
**primary copy**: the PDF of the edition declared in
`context/00-normative-base.md`. That file names the edition, the
filename and the `sha256` that identifies it, and links the ISO
catalogue page it comes from. It is a licensed single-user document:
it is not redistributable, it is not in this repository, and where it
sits on disk is a property of your checkout rather than of the project.

### Configure `.env.agent`

    cp .env.agent.example .env.agent
    # Edit .env.agent and set NORMATIVE_PDF_PATH to the absolute path
    # of your copy of the standard.

`.env.agent` is gitignored, so the path does not leave your machine.
For a single run the path can be overridden with the
`SGAI_NORMATIVE_PDF` environment variable; the check announces the
override every time it takes effect, so a stale variable cannot
quietly redirect a build.

### Check it before you need it

    bin/check-normative-base.py

It compares the declared edition against the **cover of the document
you supplied** and against its `sha256`. It fails when the file is
missing, when it is a different document than the one declared, and
when it cannot be read — that last case deliberately, because a check
that passes when it could not look is worse than no check.

## Why this matters

The steps that reason about MPEG-DASH cite clause numbers and quote
sentences from it. Without the document they would be citing from
memory, and this project has twice recorded a citation that named a
real clause about a different subject — which is why quoting the
sentence, and not only naming the clause, is what the prompts require.

Each prompt logs `[GROUNDED_BY=iso-23009-1-2026-pdf]` or
`[GROUNDED_BY=spec-only]` per run, so the audit trail says which
claims were checked against the standard and which were not.

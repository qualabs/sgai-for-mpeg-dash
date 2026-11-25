# Setup

This project is written against a specific edition of MPEG-DASH, and
the build will not start without a copy of it. That copy is a licensed
document, so it is not in this repository and you supply your own —
see **The base standard** below. Everything else needs Python 3 and
`uv` (see **Dependencies**), plus an LLM-driven agent to run the
prompts in `prompts/`.

## Quick start

1. Read `context/01-intro.md` for an overview.
2. Read `README.md` for the project layout.
3. To build: invoke `prompts/build-incremental.prompt` (a bounded
   `context/` delta) or `prompts/build-all.prompt` (a major), as
   `CLAUDE.md` → "How to invoke a build" says. Both edit
   `spec-source/` and assemble the candidate from it. See
   `prompts/README.md` for the folder layout and a per-prompt usage
   guide.

`bin/check-normative-base.py` runs before anything is generated and
stops the build if the declared edition does not describe the file you
supplied. `bin/check-context-coherence.py`, `bin/check-context-vocabulary.py`
and `bin/check-context-interfaces.py` run next and stop it if `context/`
does not hold together: its identifiers, its vocabulary, and the index of
interfaces of `context/03-requirements.md`.

## Dependencies

Most of `bin/` needs only the standard library. The exceptions:

- `check-dash-conformance.py`, `emit-extension-xsd.py` and
  `check-trace.py` need `lxml`, and `check-scenarios.py` needs `lxml`,
  PyYAML and `jsonschema`. When one is not importable they re-run
  themselves under `uv run --with` the pinned versions, so `uv` is
  enough.
- `gen-syntax-tables.py` and `strip-legacy-annotations.py` need PyYAML
  and do not re-run themselves: install it, or run them under
  `uv run --no-project --with pyyaml==6.0.3 python3 bin/<script>.py`.

The whole test suite, one `unittest` file per script:

    for t in bin/test_*.py; do
      uv run -q --no-project --with lxml==6.1.3 --with pyyaml==6.0.3 \
        --with jsonschema==4.25.1 python3 "$t" || echo "FAIL $t"
    done

## Conformance tests

The first run of `bin/check-dash-conformance.py` downloads
ISO's 6th-edition schema zip from `standards.iso.org` into
`~/.cache/sgai-conformance/` (`SGAI_CONFORMANCE_CACHE` moves it) and
checks its `sha256`; later runs work offline
(`SGAI_CONFORMANCE_OFFLINE=1` forbids the download).

`--players` needs `node`, `ffmpeg`, and the pinned Players:

    (cd bin/players && npm ci)

It uses the Chromium Playwright already has in `~/.cache/ms-playwright`.

`--behaviour` (the reference Player's battery, opt-in), and
`reference-player/test/edges/run-edges.py` and
`reference-player/demo/demo.py` on top of it, need the same: `node`,
`ffmpeg`, `npm ci` in `bin/players`, and the Chromium of the pinned
Playwright; a `--behaviour` run that lacks one says which and exits `2`. The test
content ffmpeg generates is kept across runs in
`~/.cache/cto-tmp/sgai-behaviour-content/` and regenerated when what it
is generated from changes (`--clear-content-cache` empties it;
`SGAI_BEHAVIOUR_CONTENT_CACHE=0` generates it per run instead).

`--dashif` needs Docker and the pinned DASH-IF tool image, built once:

    bin/dashif/build.sh

Its first run measures the tool's baseline on ISO's examples (about six
minutes) and caches it.

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

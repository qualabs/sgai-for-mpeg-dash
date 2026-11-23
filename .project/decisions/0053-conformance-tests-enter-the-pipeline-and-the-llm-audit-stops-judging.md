---
id: "0053"
title: Conformance tests enter the pipeline, and the LLM audit stops being the judge
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0053: Conformance tests enter the pipeline, and the LLM audit stops being the judge

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

Today Step 8 of `build-all` (`audit-dash-conformance.prompt`) has an LLM
decide conformance; its verdict cannot be re-run deterministically. The
project lead: *"Los tests dan confianza PQ es deterministico, un LLM JUZGANDO
NO"*. The DASH-IF conformance tool (`v3.1.0`) validates its XSD module against
the 5th edition: it rejects 8 of ISO's 41 6th-edition examples and 17 of the
52 spec MPDs, all for 6th-edition constructs (measured 2026-11-23).

## Decision

- **Step 6.1** emits the extension XSD (ADR 0047) after every step that writes
  a candidate.
- **Step 8.0**, before the audit, runs
  `bin/check-dash-conformance.py output/v<N>-sgai-spec.md`: levels 1 and 2,
  writing `output-analysis/v<N>-conformance-tests.md` and a `.json`. Exits as
  the rest of `bin/`: `0` nothing fails, `1` something fails, `2` cannot tell
  (missing or mismatched ISO XSD, missing candidate XSD, a stale level-2 rule),
  `64` bad command line. Level 3 runs with `--players`, same contract.
- Both steps go in `build-all`, `build-incremental` and the minor path.
- The LLM audit still runs after the tests, but stops issuing `Conforming` /
  `Non-conforming` verdicts and reports suspicions that no test covers. A
  suspicion blocks only once someone turns it into a rule and that rule fails.
  The audit report says so in its first line.
- The DASH-IF tool is a second auditor: its schematron (Global Module) and IOP
  modules run; its XSD module result is discarded. It is first run on ISO's 41
  examples and what it flags there is subtracted as its false-positive
  baseline. The existing build in
  `qualabs-video-replacement/tools/dash-conformance/` is reused, moved to
  `v3.1.0`.

## Consequences

- Removing the audit altogether would lose the only reader looking for what
  nobody thought to test; keeping it as judge contradicts the guiding
  criterion. Both were discarded.
- `check-promotable` stops reading audit rows as verdicts (ADR 0057).

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-9, and measurement 2.

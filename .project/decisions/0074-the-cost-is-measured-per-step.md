---
id: "0074"
title: The cost of a run is measured per step, before and after
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0074: The cost of a run is measured per step, before and after

## Context

The only surviving pipeline transcript (the 2026-10-27 incremental) gives 90M input tokens when its lines are summed and 41.8M when counted once per API call; the transcript repeats usage per content block. Transcripts are deleted after 30 days.

## Decision

`bin/measure-run.py <session>` sums usage once per API call, per step (the prompt each subagent received), separating fresh input, cache write, cache read and output. It runs after every run and its numbers are saved as evidence. The phase goal is at least 70% fewer processed input tokens per incremental and per refine round, measured A/B.

## Consequences

- Line-summing is the meter's negative test.
- The baseline includes one paid refine round with the old pipeline, approved by the project lead.

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-15.

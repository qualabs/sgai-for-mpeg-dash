---
id: ADR-01
title: Listen-mode slots — safety-fallback @maxDuration policy
status: ACCEPTED
date: 2026-05-20
---

## Context

UC-09 introduces open-ended linear slots declared without `@maxDuration` at
activation time. The question: should the spec require, recommend (SHOULD),
discourage (SHOULD NOT), or merely permit (MAY) a safety-fallback
`@maxDuration` declared at the time the slot activates?

DASH 6th edition §5.16.4 does not mandate a cap for listen-mode slots.

## Decision

The Broadcaster MAY declare `@maxDuration` at activation as a local safety
fallback. The spec neither recommends nor discourages it.

Rationale:
- SHOULD would require WG consensus on what constitutes a "wide enough"
  value, which is deployment-dependent and premature to prescribe here.
- SHOULD NOT would be too restrictive for Broadcasters with conservative
  failure-mode policies.
- MAY is the permissive neutral position that lets each Broadcaster decide
  based on their operational requirements, without pre-empting a WG
  decision.

## Consequences

When `@maxDuration` is present at activation, R4.2 and R4.3 apply without
change. When absent, R4.1's MUST does not apply; the slot terminates solely
via a terminating `status=update`.

This decision applies to the linear UC-09 scope only. The non-linear
analog is deferred (see follow-up PR thread in `.project/PROJECT.md`).

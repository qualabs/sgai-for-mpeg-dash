---
id: "0036"
title: Requirement ids are stable, and retired ids have their table
status: accepted
scope: project
date: 2026-10-27
supersedes: null
superseded_by: null
---

# ADR 0036: Requirement ids are stable, and retired ids have their table

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

Merging and withdrawing criteria (ADR 0030) removes 37 ids. The working
group, the ADRs and the issues cite old ids, and without a record those
citations point to nothing.

## Decision

A merged criterion keeps the id of the one that absorbs it. An absorbed or
withdrawn id is never reused. At the end of 03, a "Retired identifiers" table
has one row per id and where its content went.

## Consequences

- It is a register of identifiers, not a trace of iteration.
- Accepted ADRs need no edit to stay readable (ADR 0037).

## Links

- ADR 0034, ADR 0035, ADR 0037; DESIGN.md D-10.

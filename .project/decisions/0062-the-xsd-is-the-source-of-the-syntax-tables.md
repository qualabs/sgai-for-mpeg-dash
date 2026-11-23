---
id: "0062"
title: The XSD is the source of the syntax, and the §5 tables are generated
status: accepted
scope: phase-10
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0062: The XSD is the source of the syntax, and the §5 tables are generated

## Context

The §5 tables restate, row by row, the type, presence and default that the extension XSD already states, and nothing checked that the two agree.

## Decision

`spec-source/syntax/sgai-extension.xsd` plus `syntax.yaml` (description, semantic default, the base attributes each scheme uses) generate the §5 tables and the §5.10.1 block. Code cross-checks: `OD` implies `use="optional"`, an XSD default equals the table's, and base-attribute rows match ISO 6th-edition types and defaults (`AlternativeMPDEventType` and neighbours).

## Consequences

- XSD and tables cannot diverge.
- Rows where v12.6's tables disagree with its XSD are listed as findings for v13, not fixed in this phase.
- Discarded: YAML as the single source of both (a third format for what the XSD expresses) and descriptions inside `xs:documentation` (turns the §5.10.1 block into prose).

## Links

- Design: `.project/phases/10-code-first-pipeline/DESIGN.md`, D-3.

---
id: "0009"
title: A conformance promise in this specification binds Players that implement this specification, and no others
status: accepted
scope: core
date: 2026-09-16
supersedes: null
superseded_by: null
---

# ADR 0009: Conformance promises are scoped to this specification

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

R28 required that a ClickThrough carried in the normative carrier be
read "the same way by every conformant Player", and stated that the
click "MUST work cross-Player, not be silently ignored". That promise
was what distinguished R28 from R23, where a Player MAY ignore the
metadata.

Auditing against the published edition showed the promise cannot be
kept. ISO/IEC 23009-1:2026 §8.1 NOTE 1 states that "DASH Client
operation is not specified normatively in this document" and that
"profiles merely specify restrictions on MPD and Segments rather than
DASH Client behaviour". §5.2.1 requires the author to keep the MPD
valid once foreign-namespace constructs are removed, and its NOTE 2
observes that a Client removing them is still presenting a conforming
Media Presentation.

DASH does not permit a Player to discard an extension. It says nothing
about Player behaviour at all, anywhere — so no construct defined in
any namespace, under any profile, can compel a Player that does not
implement this specification.

## Decision

**A conformance promise in this specification binds a Player
conformant to this specification.** Where the text said "every
conformant Player", it now says conformant to what. Nine sites carried
the unqualified form.

## Alternatives considered

**Mint a profile or interoperability-point URI and require Players to
declare it.** Rejected: it would declare that a document carries these
constructs, which is useful, but it would not make anyone honour them.
§8.1 NOTE 1 forecloses this directly — a profile restricts documents,
not clients.

**Keep the unqualified promise.** Rejected: it is not merely
optimistic, it is unkeepable, and an implementer who relies on it
builds against a guarantee nobody provides.

## Consequences

R28 is not weakened. Its contrast with R23 — a Player MAY ignore the
R23 metadata, a Player MUST read the R28 carrier and fire the click —
survives unchanged, because both sentences were always about Players
implementing SGAI. What is lost is a promise about Players that do
not, and that promise was false.

The general rule is recorded as DR-8 in
`context/08-dash-extension-rules.md`, with the two citations. R28 is
its worked case: the rule was written after the correction, not before
it, so it arrives with an instance a reader can go and inspect.

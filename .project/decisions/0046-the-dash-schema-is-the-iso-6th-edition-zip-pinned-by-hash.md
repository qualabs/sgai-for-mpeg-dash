---
id: "0046"
title: The DASH schema is the ISO 6th-edition zip, pinned by content hash
status: accepted
scope: phase-09
date: 2026-11-23
supersedes: null
superseded_by: null
generalizes: null
generalized_by: null
---

# ADR 0046: The DASH schema is the ISO 6th-edition zip, pinned by content hash

This document uses RFC 2119 vocabulary (MUST / SHOULD / MAY).

## Context

The primary copy names where the schema lives: *"The schema of the MPD for
this document is provided at: https://standards.iso.org/iso-iec/23009/-1/ed-6/en
(DASH-MPD.xsd)"* (Annex B). That page lists one file,
`DASHSchema-6th-Ed.zip`, with `DASH-MPD.xsd`, `DASH-MPD-UP.xsd`,
`DASH-MPD-PATCH.xsd` and 41 example MPDs. Two other sources differ from it,
measured 2026-11-23: the generic
`standards.iso.org/ittf/PubliclyAvailableStandards/MPEG-DASH_schema_files/DASH-MPD.xsd`
is not the 6th (`grep -c InsertPresentation` gives `0`), and the `6th-Ed`
branch of `github.com/MPEGGroup/DASHSchema` differs from the ISO zip in 4
lines.

## Decision

- The schema is `DASHSchema-6th-Ed.zip` from
  `standards.iso.org/iso-iec/23009/-1/ed-6/en/`, identified by its sha256 like
  the primary copy (`context/00-normative-base.md`). The check exits `2` if the
  hash does not match, as `check-normative-base.py` does.
- It is not committed: the zip's LICENSE refers to the ISO/IEC Directives and
  does not say it may be redistributed. It is downloaded to a cache outside the
  repo, like the primary copy.
- The XSD's two network dependencies (`xlink.xsd`, and the `xml.xsd` it
  imports) resolve against local copies, also pinned by hash.

## Consequences

- A moved or changed zip stops the check with `2` and says why, instead of
  validating against something else.
- ISO's examples cannot be used as committed negatives (ADR 0054).
- Discarded: the generic URL and the GitHub branch, both of which differ from
  what the standard names.

## Links

- `.project/roadmap/conformance-tests/DESIGN.md` D-2, and measurement 1.

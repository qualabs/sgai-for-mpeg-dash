---
edition: "ISO/IEC 23009-1:2026 (Sixth edition, 2026-07)"
cover_tokens:
  - "ISO/IEC 23009-1"
  - "Sixth edition"
  - "2026-07"
primary_copy:
  filename: "ISO_IEC_23009-1_2026(en).pdf"
  sha256: "a7274eb244d916285f76c3a08c806ec07481968e1e771820eba58370b64be100"
  source: "https://www.iso.org/standard/89962.html"
  locate_with: "NORMATIVE_PDF_PATH in .env.agent; SGAI_NORMATIVE_PDF overrides it for one run"
last_revalidation: "2026-09-16"
revalidation_max_age_days: 90
verification_register: ".project/phases/05-wg-feedback-round-2/citation-verification-register.md"
---

# The normative base this specification is written against

This is the only place that names the edition. Every other document in
`context/` refers to "the base specification" and takes the identity
from here, so there is one thing to change when the base moves and no
second copy to fall out of step with it.

## The edition

The front matter above binds this specification to the edition named in
`edition`. `cover_tokens` are the strings that appear on the cover of
the document itself, and they are what a check compares against — not
another sentence written by us. Comparing our declaration to our own
prose would be two copies of the same claim agreeing with each other.

They are **three independent tokens rather than one phrase** on purpose.
A phrase only matches if the extractor lays the cover out the way we
expected; tokens survive a change of extractor, of column layout, or of
the whitespace between them.

## The primary copy

`primary_copy` identifies the document used for verification. It
**lives outside this repository and is not committed to it**.

**It is identified by content, not by location.** The `sha256` is what
makes the identification hold: a new edition arriving under the same
filename is exactly the event this declaration exists to catch, and a
filename alone would not notice it. Where the file sits is a property
of whoever checked it out, not of this specification — a declaration
that named one machine's directory would only be true on that machine.
`locate_with` names how the check finds it; the check fails, loudly,
when it cannot.

## What binding to an edition claims, and what it does not

This specification binds to the edition named above. That binding states
what the specification is written against and what has been verified
against it — **not** that every sentence has been re-read. The
per-clause state, including which citations carry direct evidence and
which carry only a prior verdict, is the citation verification register
named in `verification_register`.

**The counts belong there and not here, and the reason is not
tidiness.** `context/` is a build input: a number here that changes
every time a citation is verified would invalidate the build on every
verification pass, so auditing the specification would trigger
rebuilding it. This file carries what is stable; the register carries
what moves.

The next reader will want to put the counts here, because a file that
states its own coverage feels more honest than one that points
elsewhere. It is worse, for the reason above.

## Why this file may point into `.project/`

`context/` must not reference `context-analysis/`, `output/` or
`output-analysis/`. The reason is that those are what the build
**produces**: an input that cites its own output is a cycle, and the
document would end up resting on something it generated.

`.project/` is governance, not build output. It sits outside that cycle,
which is why a requirement may cite an architecture decision record and
why this file may cite the verification register. The rule is *do not
depend on what you produce*, not *do not cross directories*.

## Revalidation

`last_revalidation` is the date of the last pass over this
specification's claims against the primary copy. `revalidation_max_age_days`
is the age past which that pass is stale enough to be worth saying so.

Neither field can detect that a newer edition exists — that happens
outside this repository and nothing here can observe it. What they do
detect is **how long it has been since anyone looked**, which is the
part that was missing when a published edition sat on disk for thirteen
days while this specification still declared a draft.

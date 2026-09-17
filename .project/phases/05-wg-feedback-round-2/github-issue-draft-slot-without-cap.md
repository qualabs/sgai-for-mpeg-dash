# Published as issue #9

https://github.com/qualabs/sgai-for-mpeg-dash/issues/9 — *A slot that declares no maximum duration*.
Posted 2026-09-17 on `qualabs/sgai-for-mpeg-dash`, public, under the
`[DISCUSSION]` series. No labels, by that series' convention: labels on
these threads are applied by the triage pipeline, and putting them on a
thread written by hand makes it read as machine-processed.

The body below is what was published. It is kept as the record of what
was asked; the live thread is where the answers are, and this file is
not updated to follow it.

**The body carries `<!-- sgai-issues: ours -->` at the end**, which is
what keeps Stage 5 from triaging and answering our own question in
front of the group. `detect-issues.prompt` drops any issue carrying it.
An issue in this series published without the marker is one the
pipeline will pick up on the next `--live` run.

---

**Title**: [DISCUSSION] A slot that declares no maximum duration: does it fire, or does it run unbounded?

**Body**:

## Context

The draft requires the Publisher to declare a maximum duration on every
ad slot, linear or non-linear, and requires the Player to enforce it.
That requirement is a deliberate narrowing of the base specification,
which treats an absent maximum as infinity — *"in which case the
current presentation resumes only when the alternative presentation
terminates"*.

The narrowing says which manifests conform. It does not say what a
Player does when it meets one that does not, and a manifest missing the
attribute is schema-valid: the base specification's default fills in
silently.

So the case arrives by omission rather than by intent, which is what
makes it worth asking about instead of assuming.

## The question we cannot answer on our own

**When a slot declaration carries no maximum duration, does the slot
yield no advertisement, or does it run under the base specification's
unbounded default?**

## Why this needs a deliberate answer

The two readings are not a matter of strictness. They place the cost of
one missing attribute on two different parties, and neither party is
told.

They also differ in what they do to the rest of the draft. One of them
keeps the Player-side enforcement meaningful everywhere; the other
makes it inert in exactly the case where the declaration is defective,
which is the case it exists for.

## The two answers, and what each costs

**A. The slot does not fire.**
A slot with no declared maximum is not a slot this specification
defines, so the Player presents nothing from it and continues with the
primary content.

The cost lands on the Publisher, quietly. A Publisher who forgets the
attribute on one slot sells nothing there, and nothing in the playback
path tells them: the content plays normally, and the absence shows up
as revenue that never arrived. How long that takes to notice depends on
their own monitoring, not on anything the specification provides.

**B. The base specification's default applies.**
The slot is unbounded and the Player enforces no cap on it, exactly as
it would outside this specification.

The cost lands on the viewer and on the Publisher's own screen time. An
advertisement in that slot runs for as long as its creative lasts, and
the requirement to declare a maximum stays on the page while being
unenforceable in the one case where it would have mattered.

## Where our draft stands today

We have taken **A**, and we are treating it as provisional rather than
settled — the criterion itself says so in the draft.

Two things make us uncomfortable with it, and we would rather say them
than have them found:

- It is a divergence from the base specification. The base treats the
  absence as infinity, and we turn the same manifest into one that
  yields nothing. The narrowing that requires the attribute was already
  recorded; this is that narrowing acquiring a consequence at playback.
- A failure that is silent to the party that caused it is a failure
  that repeats. A Publisher who could be told would fix it once.

## What we would like from the group

1. Is there an established convention for a missing duration bound in
   ad insertion that we should follow rather than choose?
2. If A, should the specification say anything about surfacing the
   condition to the Publisher, or is that outside what a manifest
   format can carry?
3. Is there a third answer we have not considered — a Player-side
   default that is bounded rather than infinite, for instance?

Being told this should simply follow the base specification is a useful
answer, and we would record it as one.

<!-- sgai-issues: ours -->

# Published as issue #8

https://github.com/qualabs/sgai-for-mpeg-dash/issues/8 — *A viewer pauses while a linear ad is on screen*.
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

**Title**: [DISCUSSION] A viewer pauses while a linear ad is on screen: which ad holds the screen?

**Body**:

## Context

The draft gives the pause-ad family priority over an overlay: while the
viewer is paused inside a pause opportunity window, the pause ad is the
only ad surface and any active overlay is suspended and restored on
resume. That rule is scoped to the non-linear families, and so is the
single-active-form constraint that sits next to it.

A linear ad is outside both. So when a linear break — or the linear
portion of a hybrid break — overlaps a pause opportunity window and the
viewer pauses while the linear ad is on screen, the draft has a rule
for every pair of ads except this one.

The case is reached by ordinary scheduling rather than by an unusual
manifest: the two windows are declared independently, by different
parts of the same Publisher's workflow.

## The question we cannot answer on our own

**When a viewer pauses while a linear ad occupies the screen inside a
pause opportunity window, is the pause ad presented, or does the linear
ad hold the screen?**

## Why this needs a deliberate answer

Unlike the dismissal case raised earlier in this series, the draft does
not answer this one by accident — it does not answer it at all. Nothing
authorises composing the two, and nothing forbids it. An implementer
reading the text end to end finds the priority rule, sees that its
scope names the non-linear families, and is left to decide whether that
scope was deliberate.

The outcomes differ by a whole advertisement, and they differ in who is
affected: one of them interrupts a break that was sold, the other drops
an opportunity that was triggered by the viewer.

## The two answers, and what each costs

**A. The pause ad is presented, and the linear ad is suspended.**
The viewer produced the pause, and the pause family already outranks
the other family it meets. The cost is that a linear ad that was sold
against a break is interrupted, and if the measurement a Publisher
bills on does not count a suspended linear ad as delivered, the cost is
a paid impression spent to serve an unpaid surface.

**B. The linear ad holds the screen, and the pause opportunity does not
fire for that pause.**
The break is protected and the sold inventory is delivered intact. The
cost is that the viewer's own action produces nothing, and a pause
opportunity the Publisher declared is silently skipped in exactly the
region where it overlaps inventory.

## Where our draft stands today

We have taken **A**, so that the draft states something rather than
leaving implementers to guess, and we have recorded that the grounding
is weak.

The argument we have is consistency: the pause family already outranks
the other family it meets, and the pause is the event the viewer just
produced. That is an argument from the shape of our own document, not
from what serves the viewer or from what the break was sold as, and we
would rather say so than present it as a finding.

We would change it on any of:

- evidence that a suspended linear ad is not counted as delivered by
  the measurement a Publisher bills on;
- a way for a Publisher to protect a linear break explicitly — the
  priority rule is deliberately not Publisher-configurable today, a
  choice made for the overlay case and inherited here without being
  re-examined;
- a position from this group, which for a question of this kind counts
  for more than an argument built inside one document.

## What we would like from the group

1. Is there an established convention for this in linear ad insertion
   that we should be following rather than deciding?
2. Should the priority be Publisher-declared, or fixed by the
   specification as it is today for the overlay case?
3. Does the measurement question above have a known answer — is a
   suspended-and-resumed linear ad delivered?

Being told the case is out of scope is also an answer, and we would
record it as one.

<!-- sgai-issues: ours -->

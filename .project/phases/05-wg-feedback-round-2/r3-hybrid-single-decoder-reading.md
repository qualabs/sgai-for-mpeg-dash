# R3 and the hybrid break on a single-decoder device — what the three sections actually say

**Status: READING ONLY. Nothing applied, nothing committed.** No file
under `context/`, `output/` or `.project/decisions/` was edited.

## Conclusion first

**The reported contradiction does not exist.** §7.5.4, Annex D.5 and
§8.4 say the same thing, under the same condition, and D.5 cites §8.4
as its authority rather than disagreeing with it. The validator read
§8.4's opening sentence as scoping the whole subclause; it scopes only
the sentence it opens.

**But there is a real defect, upstream and different.**
`context/04-use-cases.md` UC-04 **answers the question in its own body
and its own coverage row, and then lists it as an open question** in
its Notes. That is `context/` contradicting itself, and it is what made
the generated spec look inconsistent to a reader coming from the use
case.

**And there is a second, smaller one**: `context/` answers it
unconditionally and the generated spec answers it conditionally. Those
are different obligations, and the difference is not recorded anywhere.

---

## 1. What each section says

### §7.5.4 — `output/v7.2-sgai-spec.md`, line 2540

> Whether the overlay portion reaches the screen depends on what the
> device can composite **while the linear ad occupies the video
> surface**. A device with a second decoder composites a video overlay
> on top of the linear ad. A device with overlay surfaces but a single
> decoder presents the linear portion alone **when the overlay option
> needs to be composited on top of the linear ad's video**, and MAY
> present a squeezeback option whose budget it can satisfy. A device
> with no overlay capability presents the linear portion alone. In
> every case the linear portion plays and the break completes.

It does **not** decline flatly. It declines on a stated condition, and
in the same sentence permits a squeezeback option the device can
satisfy.

### Annex D.5, row D3 — line 3504 (table), row at 3509

> D3 | Plays on the single decoder | The video option needs a second
> decoder and fails. The image option would need a surface composited
> over the linear ad's video, **which this device cannot guarantee
> concurrently**, so the overlay portion is declined **(§8.4)** | A
> full-screen linear ad, no overlay on top

Note the parenthesis: D.5 **cites §8.4 as the authority for
declining**. It is applying §8.4, not contradicting it.

### §8.4 — line 2788

Opening sentence:

> Two device questions recur and **this specification decides neither**,
> because both are properties of the device rather than of the
> contract.

Second bullet, in full:

> **An overlay on top of a linear ad on a single-decoder device.** In a
> hybrid break the linear ad occupies the video surface, so an overlay
> composited on top of it requires the device to composite a second
> surface over a surface that is itself an ad. **Where the device
> cannot guarantee that concurrently**, the Player presents the linear
> portion alone and the overlay portion is declined — which leaves the
> break complete and the viewer with a full-screen linear ad.

## 2. Is it a contradiction? No

The three sentences share an antecedent and a consequent:

| | Condition | Behaviour |
|---|---|---|
| §7.5.4 | the overlay option needs compositing on the linear ad's video | linear alone |
| D.5 D3 | the device cannot guarantee that concurrently | declined, per §8.4 |
| §8.4 | where the device cannot guarantee that concurrently | linear alone, overlay declined |

**What §8.4 declines to decide is the device-capability question** —
*can this device composite a second surface over an ad video?* — which
it calls a property of the device. **What it does decide is the
behavioural question**: what the Player does when the device cannot.
Those are two different questions in one subclause, and the opening
sentence answers only the first.

The validator's finding, and the gap table rows that repeat it
(row 2 / F-2, row 20 / D-6), took the opening sentence as scoping the
bullet. This is the same misreading pattern already recorded twice in
this phase: a verdict taken from a heading or an opening rather than
from the unit it introduces.

**R3.2 is therefore satisfiable on this evidence.** It requires a
defined behaviour — render, fall back or skip — for every opportunity
type on every supported device class. The hybrid type on D3/D4/D5 has
one: the linear portion plays, the overlay portion is declined.

## 3. The real defect, which is in `context/`

`context/04-use-cases.md`, UC-04 answers the question three times and
then declares it open.

**Answered — the coverage table, line 78:**

> UC-04 Hybrid linear + overlay | … | linear only (overlay skipped) |
> linear only (overlay skipped) | linear only (overlay skipped)

for D3, D4 and D5.

**Answered — UC-04's D3 body:**

> A separate HTML/image overlay *on top of* the linear ad's video still
> **is declined per R5/R3**.

**Declared open — UC-04's `Notes / open questions`:**

> Whether D3 / D4 must always decline the overlay portion of a hybrid
> break, or whether the Player is allowed to composite an HTML / image
> overlay on top of a linear ad video on single-decoder devices that
> have HTML/image overlay surfaces. … **the spec must declare it
> explicitly**.

The body and the table decide it; the Notes say it is undecided and
instruct the spec to decide it. **The generated spec did what the Notes
asked, and the result reads as an inconsistency only because the
question it answers is marked unanswered in its own input.**

### What is lost each way, concretely

The choice the Notes pose is real even though the body already made it:

**If D3/D4 must always decline** — a device that genuinely can
composite an image over a decoded ad video is forbidden from showing
an overlay it could show. Lost: inventory on a class of device that is
common, and the Publisher has no way to permit it.

**If the Player may composite when it can** — an implementer cannot
verify conformance from the document: two conformant Players on the
same hardware may differ, because the deciding fact is a platform
capability the specification does not define and cannot test. Lost:
the checkability R3.2 exists to provide.

## 4. What MPEG-DASH says

**It does not model this, and where it comes closest it excludes it
explicitly.**

- `concurrent decoder` → **0 occurrences**. `decoder budget` → **0**.
- `overlay` → **1**, and it is unrelated (a `QualityType` note about
  second-screen applications, PDF 22392).
- `composit*` → **7**, and the relevant one is §5.8.5.16, *Supplementary
  video services and the supplementary video descriptor* — DASH's
  picture-in-picture concept, the nearest analogue to a second video
  presented over a main one. PDF 9092:

  > spatial manipulation of the stream and **the composition of the
  > main video and the supplementary video are out of the scope of the
  > DASH client**.

**Control**: the same instrument returns `Alternative MPD` 89 times and
`EventStream` 106 times, so the zeros are measurements and not a broken
search.

**What this means under ADR 0006.** The criterion is to adopt the base
model where it answers and declare an extension where it does not.
Here the base standard answers, and its answer is that composition is
not the client's business — so there is no execution-model rule to
inherit, and this is legitimately extension territory. §8.4's refusal
to decide the device-capability half is **aligned with the base
standard's own posture**, not a gap in ours.

## 5. Recommendation

**Do not "resolve the contradiction" — there is none to resolve in the
generated spec.** Three actions, in order of value:

1. **Close UC-04's open question in `context/`**, because it is the
   only thing actually undecided. The body and the coverage table
   already answer it; the Notes bullet should either be deleted as
   already-answered or the body changed to match a different answer.
   Leaving both is what produced this report.

2. **Reconcile the strength.** `context/` says D3/D4/D5 skip the
   overlay, full stop. The generated spec says they decline *where the
   device cannot guarantee concurrency*, which leaves room for a device
   that can. **These are different obligations.** The generated one is
   the more defensible — it matches the base standard's placement of
   composition outside the client — but it is not what `context/`
   says, and `context/` is the input.

3. **Record why the strength is conditional**, wherever it lands: DASH
   puts composition outside the DASH client (§5.8.5.16), so a
   specification that hard-declined on a device capability it cannot
   test would be asserting more than it can check. That is the argument
   for the conditional form, and it is not written anywhere today.

**On the second open question in UC-04's Notes** — whether the
Publisher can link the two portions of a break — this reading found
nothing about it in the generated spec either way, and it is out of
scope of what was asked. Flagged, not investigated.

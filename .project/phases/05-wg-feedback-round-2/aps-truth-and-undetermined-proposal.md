# Proposed: the APS's document is the reference point, and an absent parameter is undetermined

**Status: PROPOSED — not applied.** `context/` is untouched by this
document.

Two decisions of 2026-09-15, turned into text in one pass:

- **A.** An obligation is written only against what the Player can see.
  The APS-to-ADS interface is out of scope, so the resolution document
  the APS returns is the reference point for order.
- **B.** A reserved parameter absent from the resolution request means
  **undetermined**. What an APS does with an undetermined value is a
  business decision this specification deliberately leaves open.

---

## The discriminator for decision A

Six sites in `context/03-requirements.md` name the ADS as the origin of
something. They are **not one family**, and the split decides which get
edited:

| | Reference point of the obligation | Reached? |
|---|---|---|
| **R5.1**, **R5.5**, **R7** (title, gist, prose, R7.1), section intro | The order **in the ADS's decision document** | **Yes** — only the ADS holds it |
| **R12.3** (ad-type set), **R15.2** (mimeType set) | The **enumerated set defined in this specification** | **No** — already checkable |
| **R13.1** (tracking schedule transcribed verbatim) | The **schedule in the ADS's VAST** | **Same shape — not touched, see below** |

**The test is not whether the ADS is named. It is whether the thing the
APS's output is compared against lives inside the Player-visible
interface.** R12.3 says the APS must not emit an ad type outside *the
enumerated set* — that set is in the spec, so an auditor holding only
the resolution document can check it. R12.3 and R15.2 already close
with *"conformance is checked against the APS's resolution document,
not against the ADS's internal decision document"*. They comply with
decision A as written; naming the ADS as provenance costs nothing
because no obligation rests on it.

R5.1 is the opposite: *"MUST carry the options it does emit **in the
order the ADS gave them**"* can only be checked by holding the ADS's
document, which R18 declares out of scope.

---

## A1 — R5.1

**Current:**

> - **R5.1** (APS): Each ad candidate in the resolution document the
>   Player reads MUST carry one or more **renderable presentation
>   options (each a form plus its layout) as an ordered list, where
>   document order is the preference order**. The options and their
>   order originate in the ADS's decision (which media files / forms
>   exist, and their order). The APS MAY omit options from what the ADS
>   returned; it MUST carry the options it does emit in the order the
>   ADS gave them, **preserving document order**, **without
>   reordering**. The normative carry obligation is the APS's: the
>   APS produces the resolution document the Player reads, so
>   conformance is checked against the APS's resolution document,
>   not against the ADS's internal decision document.

**Proposed:**

> - **R5.1** (APS): Each ad candidate in the resolution document the
>   Player reads MUST carry one or more **renderable presentation
>   options (each a form plus its layout) as an ordered list, where
>   document order is the preference order**. How many options a
>   candidate carries is the APS's decision: this specification sets
>   no maximum, and no minimum beyond one. Conformance is checked
>   against the APS's resolution document, which is the only artefact
>   on the path to the Player that this specification defines.

**On `without reordering`, which was the question:** it does not
survive in reduced form, it has to go with the clause that carried it.
Its referent was the ADS's order; with that gone there is nothing left
to not-reorder, because the APS's document *is* the order. Keeping the
words without the referent would leave a MUST that cannot be failed.

**On the permission to omit (T-10, `ff528d7`):** it is not dropped, it
is restated without an upstream referent. *"MAY omit options from what
the ADS returned"* answered the WG's question by pointing at a document
the auditor cannot open; *"how many options a candidate carries is the
APS's decision"* answers the same question from the side the auditor
can see. Nothing the APS could do before is forbidden now.

## A2 — R5.5

**Current:**

> - **R5.5** (ADS): An ad candidate MAY carry multiple presentation
>   options, each pairing a form with an admissible layout. The
>   options form a single ordered list; their document order
>   expresses the ADS's preference.

**Proposed:**

> - **R5.5** (APS): An ad candidate MAY carry multiple presentation
>   options, each pairing a form with an admissible layout. The
>   options form a single ordered list, and their document order is
>   the preference order the Player follows.

The actor tag changes from `(ADS)` to `(APS)`. A conformance criterion
addressed to an actor whose interface this specification does not
define was the defect in miniature: there was no document against
which to check it.

## A3 — R7, four sites

**Title.** `R7. Respect ADS-declared order.` →
`R7. Respect the order of the resolution document.`

**Gist.** *"The Player plays candidates in the order the ADS
declared…"* → *"The Player plays candidates in the order the
resolution document declares, only dropping (never reordering) ones it
cannot render or that would exceed the slot cap."*

**Prose, two sentences.**

> …the Player MUST play the ads **in the order declared by the ADS and
> preserved by the APS**, as long as this is possible…

→

> …the Player MUST play the ads **in the order the resolution document
> declares**, as long as this is possible…

> Ad selection and ordering are ADS responsibilities (R2); the APS MUST
> preserve that order when building the resolution document, and the
> Player's role is to honour it unless a hard constraint blocks it.

→

> Ad selection and ordering happen upstream of the Player (R2); the
> order the resolution document carries is the one the Player honours,
> unless a hard constraint blocks it.

**R7.1.**

> - **R7.1** (Player): …the Player MUST play the candidates in
>   the order declared by the ADS (and preserved by the APS), except
>   for candidates dropped under R7.2 or R7.3.

→

> - **R7.1** (Player): …the Player MUST play the candidates in
>   the order the resolution document declares, except for candidates
>   dropped under R7.2 or R7.3.

**R7.4 is not edited.** *"MUST NOT re-order, deduplicate, or otherwise
rearrange"* is an obligation on the Player against the document in its
hands; once R7.1 names that document as the referent, R7.4 reads
correctly and gains the referent R5.1 lost.

**Why R7 is in this pass and not a later one.** Decision A is about
order, and R7 *is* the order requirement — its title names the ADS.
Editing R5.1 and leaving R7 would produce two adjacent requirements
disagreeing on what the Player honours.

## A4 — the section introduction

`context/03-requirements.md`, the paragraph opening the selection and
ordering group:

> …device-aware selection and honouring the **ADS-declared order**.

→

> …device-aware selection and honouring the **order the resolution
> document declares**.

## A5 — R13.1: same shape, NOT proposed for edit

> - **R13.1** (ADS + APS): The ADS MUST declare the tracking
>   schedule … as the sole authority; the APS MUST **transcribe those
>   instructions verbatim** into the resolution document …
>   The APS exercises no discretion over the schedule — it neither
>   adds, removes, nor reorders beacons.

This is R5.1's defect exactly: *"transcribe verbatim"* and *"neither
adds, removes, nor reorders"* can be checked only against the ADS's
VAST. Decision A's principle reaches it.

It is **not** in this proposal because the decision as stated was about
order, and R13 is about the tracking schedule. Extending it is a
separate call — and unlike R5.1 / R7, the fix is not obvious: R13's
whole point is that the ADS owns the schedule, so removing the ADS
referent may require rethinking what the requirement asks for rather
than rewording it.

---

## B1 — R29.7, new conformance criterion

Appended to R29's conformance criteria, after R29.6:

> - **R29.7** (spec document): A reserved parameter absent from the
>   resolution request means its value is **undetermined** — the
>   Player did not determine it, or did not disclose it. Absence does
>   NOT assert that the device lacks the capability. This
>   specification does not define how an APS resolves an undetermined
>   value; that is the APS's decision, and two APSs that resolve it
>   differently are both conformant.

The criterion carries two statements because they are two different
things and only the first is a rule: the spec fixes what absence
*means*, and declines to fix what an APS *does* about it.

## B2 — UC-13, the D3 row

**It does need reformulating, and the use-case frame does not save
it.** The row currently reads as a derivation:

> The APS treats the omitted axis as undetermined — neither present nor
> absent — and **therefore** emits no option that depends on it.

That *therefore* presents the conservative policy as the consequence of
the rule. Under R29.7 it is one admissible policy, and an APS that
resolves the same absence optimistically is equally conformant. The
frame at the top of the file establishes that a case describes a
scenario, but it does not neutralise a sentence whose own grammar
claims a derivation.

**Proposed, replacing that clause:**

> The APS treats the omitted axis as undetermined (R29.7), and this
> implementation resolves an undetermined axis conservatively: it emits
> no option that depends on it. Option 1 needs a second decoder and is
> ruled out; option 2 needs one decoder plus one image surface, depends
> on no undetermined axis, and survives.

**And a fourth entry under `Notes:`**

> - **The policy for an undetermined axis is the APS's, not this
>   specification's.** The APS in this scenario resolves an
>   undetermined axis conservatively. One that assumed the most
>   capable case would emit a different option on D3 and would be
>   equally conformant (R29.7). What does not vary is that the Player
>   checks whatever arrives before rendering it.

**One consequence to be aware of.** With the policy declared as this
implementation's, D3's *"same rendered result as UC-09"* becomes a
property of the scenario as specified rather than of every conformant
APS — a different policy is a different input, and a different input
may land elsewhere. The demonstration is unaffected: it compares two
divisions of labour over the same inputs, and the other four classes
depend on no undetermined axis at all.

---

## What this proposal does not do

- **It does not touch R12.3 or R15.2.** Their obligations are checked
  against sets this specification enumerates, and both already state
  that conformance is checked against the APS's resolution document.
- **It does not touch R13.1**, which shares the shape but not the
  subject; see A5.
- **It does not narrow what any APS may do.** Every behaviour
  conformant before these edits is conformant after them; what is
  removed is an obligation no auditor could have checked.

---

## C1 — UC-12, the three paths made explicit (added 2026-09-15, second pass)

Case 3 — every overlapping window fails and no fallback is left — is
**already specified**, by DP-3, and needs no new requirement. It has no
scenario, and UC-12 is where it belongs, because all three paths run on
the scenario UC-12 already sets up.

**Added as a second bullet under UC-12's `**Expected behavior:**`,
after the existing one:**

> - **The three paths this scenario admits**, all ending with the
>   primary content playing uninterrupted:
>   1. The first window answers with a resolution document carrying no
>      candidates. The opportunity resolved, and it resolved to no ads;
>      the second window is not touched (R20.1, R30) and the Player
>      continues with the primary content.
>   2. The first window cannot be accessed and the second answers with
>      a document carrying no candidates. The fallback is used as
>      declared, and the opportunity still resolves to no ads.
>   3. Neither window can be accessed and no further fallback is
>      declared. The chain is exhausted with no resolution document
>      obtained, so no candidate was ever accepted. The Player skips
>      the opportunity and continues with the primary content:
>      applying this specification never breaks primary-content
>      playback, and an opportunity that cannot be honoured is skipped
>      (DP-3).

**The Coverage table row for UC-12 is not edited.** It reads
*"first-window-wins, fallback on resolve failure"* across D1–D5, which
stays accurate: all three paths are window selection, and all five
device classes behave identically.

**Why this is one case and not two.** All three paths need the same
scenario: two overlapping same-family windows, each with an APS behind
it. Only what each APS returns varies. A second use case would rebuild
that setup to show a different ending, which is what UC-09's five
device classes already show is unnecessary — a case carries several
paths.

**What is right in the two-case instinct** is the content, not the
structure: a chain ends for two different reasons — someone answered
(empty), or nobody could (exhausted) — and UC-12 showed only the first.
Path 3 is that missing half.

**A side effect worth knowing.** Path 3 is the only place in
`04-use-cases.md` where DP-3's runtime invariant is exercised by a
scenario. See the note on DP-3's standing in the channel report.

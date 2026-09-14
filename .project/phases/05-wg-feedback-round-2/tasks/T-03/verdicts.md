# T-03 — the four claimed contradictions, verified against the primary sources

Verified 2026-09-14 against: the Tactiq transcript of the 2026-08-19
Advertising WG call (Google Doc
`1E_B_53VRaBm8TwJYKTouFxZvSq2MabkO-1l0NIiIdPA`, exported to Markdown and read
in full around each cited turn); the literal text of `context/03-requirements.md`,
`context/02-actors.md`, `context/04-use-cases.md` and
`context/05-dash-linear-interfaces.md`; the `LOG.md` entry of 2026-05-27 and
phase 02's T-04 / T-05 notes. The agreements extract was used only as an index.

`context/` is byte-identical to how this task found it.

| Pair | Verdict | Work it implies |
|---|---|---|
| A2 vs R5 | `spec-does-not-express-its-intent` — `contradiction` is ruled out | **drafting** (T-04 / T-05) |
| A6 vs R22 | `contradiction` — but with **UC-04**, not with R22 | **design** |
| A7 vs R17 | `contradiction` | **design** |
| A8 vs the Player-dismiss vocabulary | `compatible` — absence, an addition | **design** (an addition) |

---

## A2 vs R5 — verdict: `spec-does-not-express-its-intent`

`contradiction` is ruled out. Every normative clause of R5 permits the
arrangement A2 describes; what fails is the prose around those clauses, which
reads as an obligation to offer the device a choice.

### What the extract asserts

> Taken at face value, A2 runs against `context/03-requirements.md` R5, where
> the ADS/APS need no device view (R5.4), a candidate MAY carry several ordered
> presentation options (R5.5), and the Player renders the first it can satisfy
> (R5.2); UC-09 in `context/04-use-cases.md` exists to demonstrate that model.

### The transcript, read in its surrounding turns

The two quotes the extract rests A2 on are both about legs the spec does not
govern, and the second is David glossing a comment the transcript mangles.

At **[10:49]**, in one unbroken turn, David reads Nicolás's written comment
aloud and then draws his own conclusion from it:

> "Um, I believe that's what he said. Uh, let's see, so, in your opinion, at
> the Speclo, she would let the devices Um, choose, maybe you're using the
> device, most flexible design, because you don't have, uh, don't want devices
> to choose. The image should send only one option. This is just an
> implementation, so the APS should, yeah. So when the APS is speaking to the
> ADS, you should just be requesting what you want and know can be rendered for
> that. Uh, individual user."

The first three sentences are the comment being read out. Set against the
comment's actual text —

> "In my opinion at spec level we should should let devices to choose -> main
> reason: it's the most flexible design because **if** you don't want devices to
> choose, the APS should send only one option (this is just an implementation
> decision)."

— the transcript has dropped the **`if`** and turned **`APS`** into `the image`.
The conditional is the load-bearing word in the sentence: with it, the comment
says single-option is a *permitted implementation*; without it, the sentence
reads as an assertion that one option is what gets sent. The record cannot show
which of the two the room heard.

The sentence that follows — *"when the APS is speaking to the ADS…"* — is the
**APS→ADS ad request**. At **[14:30]** the same arrangement is restated across
both request legs:

> "the player is gonna talk to the, um… the APS, and say, hey, this is what I'm
> able to support, and then the APS can also have additional logic for the
> event, For user accounts, and so forth (…) and then they can make specific ad
> requests to get content that matches what they want to render at that time."

Neither sentence is about the resolution document.

### The literal spec text

`context/03-requirements.md` **R18**, lines 195–202:

> This specification does NOT define the URL syntax, parameter names, request
> payload, response payload, or any other aspect of the **APS-to-ADS API**, nor
> of the ADS-side API. The specification documents only the **Player-visible
> interface** — the MPD event URL referenced by the Publisher (which resolves to
> the APS), and the resolution document the APS returns

**The R18 scope question, answered.** The two legs are not in the same
position, and the extract's hypothesis is right on one and only approximately
right on the other:

- **APS→ADS** — the leg the [10:49] quote and half of [14:30] describe. Out of
  scope, explicitly, by R18 and R18.2. R5 never governed it. For this half of
  A2 the finding is that the two requirements were never in the same territory.
- **Player→APS** — the leg the other half of [14:30] describes. *Not* fully out
  of scope: `context/05-dash-linear-interfaces.md` line 114 documents the
  resolution request as `GET <event @url>` augmented with query parameters
  declared by an MPD-level `UrlParamInfo` descriptor (§I.4, lines 168, 250–256),
  and R18.1 names the event URL pattern as Player-visible. But the spec
  enumerates no capability parameter and forbids none, and DP-2 (lines 43–53)
  settles what silence means: *"the positive obligation defines the contract;
  anything outside the positive obligation is implicitly out of scope."* So
  Nicolás's *"the URL to the APS is not under this spec"* is right in effect and
  loose in letter: the carrier is specified, its contents are bilateral.

**The cardinality question, answered — a single-option candidate is already
conformant.** R5.1, lines 417–419:

> Each ad candidate in the resolution document the Player reads MUST carry
> **one or more** renderable presentation options

R5.5, lines 440–443:

> An ad candidate **MAY** carry multiple presentation options

R5.2, lines 429–432, is a rule for *resolving* a choice, not an obligation to
*offer* one:

> The Player MUST evaluate the presentation options of an accepted candidate
> **in document order** and render the **first option** whose form and layout it
> can satisfy on its device.

With one option the walk terminates on the first step. Nothing in R5 requires
a second.

**The R5.4 question, answered — it declines to mandate, it does not forbid.**
Lines 437–439:

> Neither the ADS nor the APS MUST be required to maintain a device-class
> matrix or a per-Player capability view to produce candidates.

"MUST be required" is a statement about what the spec imposes, not a
prohibition on the actor. DP-2 confirms the reading directionally: the spec
does not enumerate prohibitions. An APS that *chooses* to hold a device view is
outside the positive obligation, not against it.

### Where the drafting actually fails

Four passages say, in ordinary reading, that the device chooses — and a WG
reader has only the words.

1. **R5 gist, line 389** — *"Each candidate carries renderable presentation
   options in preference order, and the Player renders the first one its device
   can satisfy."* Plural throughout; the gist is the line a reader skims.
2. **The core-invariant table, line 89** — *"Candidates list renderable options
   in preference order; the Player renders the first its device can satisfy."*
   Same shape, in the eight lines the spec itself tells a new reader to start
   from.
3. **R5 prose, lines 391–392** — *"The Player is the **sole authority** on
   device capability."* Read alone this excludes the APS from knowing anything
   about the device, which is precisely what A2 has it doing. The em-dash clause
   that follows narrows it to "neither needs a matrix", but the headline phrase
   is what carries.
4. **`context/02-actors.md`, line 129 — the sharpest instance.** *"Because the
   Player is **device-agnostic on the APS interface**, the APS emits each ad
   candidate carrying one or more renderable presentation options…"* This is not
   a permission that happens to be phrased tightly; it is a **stated premise
   about the interface** that A2's Player→APS capability signal denies outright.
   A reader cannot reconcile it with *"you could send a queryparam with
   capabilities in your implementation if you like"* without being told that the
   premise describes one implementation rather than the interface.

Nothing normative has to change. The permission is already there; it is
invisible.

### What the call concluded on A2, and on what support — the answer

**A2 never received an assent round of its own.** This is a finding, not an
`indeterminate`: the transcript is clear about where the assent attaches.

The only assent in that stretch is at [17:15] and [17:22], and it answers the
question David put at [16:01] and [16:28] — whether decoder detection belongs
in the Player or in the application, which is **A1**:

> David [16:28]: "my general feel is that doesn't really belong in the player,
> let it reside in the application (…) And do note that I take silence as
> acceptance."
> Nicolás [17:15]: "Yep." [17:22]: "Or not strong Pushbacks"

Between the comment being read [10:49] and that question [16:01], Yasser put
the opposite arrangement on the table [13:18], David answered it with an
ad-delivery objection [14:03], and Yasser replied "Uh-huh, okay" [14:28],
"Okay" [15:03], "Okay" [15:57]. Acknowledgement of an answer is not adoption of
a position, and no one was asked for one.

**Consequence: A2's standing is weaker than the extract's §1 placement
credits.** Its two sources of support are a gloss on a sentence the transcript
mangled at exactly its conditional, and an assent that belongs to A1. It should
be read as proposed rather than agreed.

### Scope — the dependency set, verified

The set `TASKS.md` enumerates for A2 is **larger than what the verdict
touches**. Item by item, against the verdict above:

| Enumerated dependency | Actually alcanzado? |
|---|---|
| R5, R5.1–R5.7 | **No normative change.** R5.1 and R5.5 already permit one option; R5.4 declines to mandate rather than forbidding. Drafting only: the gist (line 389) and the "sole authority" prose (lines 391–392). |
| The APS's *"produce candidates with renderable presentation options"* responsibility, `02-actors.md` | **Yes — and this is the sharpest item, not a secondary one.** Line 129's *"the Player is device-agnostic on the APS interface"* states as a premise what A2 denies. Drafting. |
| The ordered-fallback decision, `LOG.md` 2026-05-27 | **No.** Reading its rationale: the decision replaced *optional ADS-supplied priority hints* with *normative document order* — it is about **how preference is expressed**, not about **who chooses**. A one-option list is positionally ordered trivially. Phase 02's T-04 note confirms what it was protecting: *"the Publisher does not declare layouts per device class."* A2 says nothing about the Publisher. **Drop this from the dependency set.** |
| UC-09, entire | **No.** UC-09 is a worked example whose own premise is *"The ADS is unaware of the device class; it returns this same ordered list for every viewer"* (line 1048). It illustrates one implementation R5 permits; it never claims to be the only one. It survives intact. Its value is the opposite of what the risk register assumed: it is the existing half of the pair T-05 wants to complete. |
| Phase `03-custom-layout` | **Yes.** Its `T-01-PLAN.md` §D-5 is *"Degradation — R5 ordered fallback + R3 decoder budget"*, and T-06 binds the new requirement to R5. But since the verdict is drafting-only, the phase is unblocked. |
| Phase `04-multiview` | **No.** `grep` over both its files returns **zero** references to R5 or to ordered fallback. It leans on **R3** (§D-7, "extend R3") and on **R22**. The claim that it leans on R5 is wrong. **It is reached by A6, not by A2.** |

**Both open phases are unblocked by this verdict.** Nothing normative in R5
changes, so nothing either phase builds on R5 moves.

**Work: drafting.** T-04 owns the R5 text and the `02-actors.md` line 129
premise; T-05 owns the explicit permission and the paired use case.

### Open question for the WG (David)

> In the 19 Aug call, when my comment on "Capabilities detection" was read out
> around [10:49], the conditional dropped: the comment says the APS sends a
> single option **if** an implementation does not want the device to choose,
> which makes it an implementation choice rather than a spec rule. Did the group
> take the position that the spec should *mandate* the ADS returning one
> presentation, or only that it should *permit* it? Our spec permits both today;
> we want to state that explicitly, and we need to know whether the group reads
> it as a rule.

---

## A6 vs R22 — verdict: `contradiction`, and its locus is **UC-04**, not R22

The extract's framing is right about R22 and misses the thing that actually
breaks.

### What the extract asserts

> R22 in `context/03-requirements.md` bounds simultaneity **within** the
> non-linear family only. The WG rule is broader: it spans families (linear vs
> non-linear, pause-ad vs overlay).

### The transcript, read in context

The rule is an answer to a specific question. Yasser [36:31, 36:39]:

> "Hey David, one thing. Can you have a nonlinear ad being played? (…) And then
> when a regular linear ad is occurring?"

David [36:46, 36:51]:

> "Please don't do that. (…) God, no, let's not ever do that. Um, and we should
> not consider that supported."

Nicolás [37:23] generalises and David [37:29] confirms:

> "you can only do one type of ad experience at a time, meaning linear,
> non-linear, Um, at a most basic level, but even deeper than that. Like, you
> can't mix (…) at least not trying to support that now."

There is no ambiguity about which case was asked: a non-linear ad presenting
while a linear ad plays.

### The literal spec text

**R22 is not contradicted.** Line 899 and R22.1, lines 932–936:

> At any instant `t`, at most ONE **non-linear** ad form is active on the
> screen.

R22 is narrower than A6 and consistent with it. Silence across families would
be a gap.

**But the spec is not silent — it models the case A6 forbids, as a first-class
use case.** `context/04-use-cases.md` line 421, **UC-04 — Hybrid linear +
concurrent overlay**:

> **Scenario:** The Publisher has declared a mid-content slot where the ad
> experience is hybrid: a linear ad takes over the screen *and* a non-linear
> overlay is composited on top of it during the same break.

> **Publisher intent:** (…) Non-linear forms allowed **concurrently with the
> linear ad**, with a restricted layout set (e.g. banner only — no L-shape on
> top of a linear ad).

UC-04 is specified against all five device classes and carries its own row in
the coverage table at line 78, category **Mixed**:

> | UC-04 Hybrid linear + overlay | Mixed | linear + overlay | linear + video overlay (if video form available) or linear only | linear only (overlay skipped) | … |

The D1 expected behaviour, line ~455, is exactly Yasser's question answered the
other way:

> "a linear ad plays full-screen, and during the linear ad a banner overlay is
> rendered on top of it"

Note the spec is internally consistent: UC-04 needs one decoder for the linear
ad plus one for the overlay, and only *one* of the two forms is non-linear, so
R22's decoder-budget bound is respected. It is A6 that breaks UC-04, not R22.

### Scope

- **UC-04, entire** — the use case A6 removes. This is the whole cost of A6 and
  the extract does not mention it.
- **The coverage table**, `04-use-cases.md` line 78, and the "Mixed" category.
- **R22** — not contradicted, but **widened**: if A6 is adopted, the bound
  becomes one *ad experience* rather than one *non-linear form*, which changes
  R22's title, its rationale (today it is decoder-budget-based) and R22.1.
- **Phase `04-multiview`** — leans on R22's decoder-budget reasoning
  (`T-01-PLAN.md` §D-7 cites R3, R22, R26, R27). If R22 is rewidened, that phase
  reads against a moved requirement. **This is the phase A2 was wrongly said to
  reach; A6 is what actually reaches it.**
- **R17** — already legislates one cross-family case in a way consistent with
  A6 (it suspends the overlay so only one surface shows). Not contradicted by A6.

### The §4.10 bound does not rescue UC-04

§4.10 records Nicolás at [42:42]: *"or not not to add experiences inside the
player, let's say, controlled by this mechanism"*, read as bounding A6 to what
this spec controls. Verified against UC-04: both the linear portion and the
overlay portion are Publisher-declared in the MPD and resolved through the APS,
i.e. squarely inside the mechanism. Whatever §4.10 exempts, it does not exempt
UC-04.

This is a `T-02` item for the *edges* of A6 (an application-drawn banner), not
for its core. Do not resolve it by inference.

**Work: design.** Adopting A6 deletes a use case.

---

## A7 vs R17 — verdict: `contradiction`

### What the extract asserts

> R17 in `context/03-requirements.md` gives the pause-ad priority **over** a
> running overlay and suspends the overlay. The WG's rule points the other way
> for the case where the pause happens while an ad is already presenting.

Confirmed, and the collision is sharper than the extract states, because the
spec has a use case dedicated to the exact state.

### The transcript, read in context

The condition Nicolás posed at [40:41] is explicitly the non-linear one:

> "what happens if I was in the middle of an ad, dual side, replacement,
> whatever, and I pause Should the… it's like which wins (…) It's like post ad
> [pause ad] is something you can sell (…) But what happened if you also have an
> again, an L bar something"

David's answer, [41:27]:

> "I think today the standard is if you pause during an ad break, You do not…
> you're not going to show your PAWS [pause] ad state as well. The ad is paused
> until they resume. (…) I think IAB even defines, uh, this stuff, because,
> like, once you've started a… an actual ad, right, within an ad break, they own
> that time until it's completed or abandoned."

**Two claims are tangled here and they do not have the same verdict.**

Nicolás's restatement at [41:55] is about **simultaneity**:

> "even if it is a post add [pause ad], a concurrent presentation or whatever,
> it's just one at a time You cannot define a window where a post ad [pause ad]
> plus L shape goes together."

That half is **already the spec's position** — R17 exists precisely to prevent
simultaneous composition. R17, lines 817–820:

> while the viewer is paused inside the pause-ad window the pause-ad is the
> only ad surface visible and any active overlay is suspended, so there is no
> simultaneous composition of a pause-ad and an overlay during the pause (R22).

What contradicts is David's half: **which of the two wins.**

### The literal spec text

R17.1, lines 833–836:

> While the viewer is paused inside a pause-ad window AND an overlay is active,
> the Player renders the pause-ad form and suspends the overlay rendering.

R17.4, lines 843–846 — the spec has hard-coded the direction A7 reverses:

> The specification carries no construct that lets the Publisher, the ADS, or
> the APS invert this priority.

### "Are these the same state?" — answered: yes

The hypothesis was that R17's "an overlay is active" and A7's "an ad break is
running" might denote different conditions and never meet. They meet, and the
spec names the meeting point itself. `context/04-use-cases.md` line 831,
**UC-08 — Overlay window crosses a pause-ad window**:

> **Scenario:** An overlay (per UC-03) is being shown to the viewer when the
> viewer pauses primary playback, and the pause occurs inside a
> Publisher-declared pause-ad window (per UC-05). The pause-ad takes priority
> over the overlay (per R17): while the viewer is paused, the pause-ad form is
> rendered and the overlay is suspended.

That is Nicolás's [40:41] question, word for word, resolved in the direction
David says the industry resolves it the other way.

### Scope — the enumeration, verified

The extract lists "R17, R21, R25, UC-05 and UC-08"; `TASKS.md` adds R16. Sorted
by what is actually contradicted:

| Construct | Status |
|---|---|
| **R17** (prose, R17.1, R17.2, R17.3, R17.4) | **Contradicted.** R17.4 in particular: the spec declares the priority non-invertible, and A7 inverts it. |
| **UC-08**, entire, all five device classes | **Contradicted.** Under A7 there is nothing to arbitrate: the overlay keeps running and no pause-ad is raised. The use case either disappears or is rewritten to the opposite outcome. |
| **R21** | **Touched, not contradicted.** Lines 604–609 cite R17 to explain why a partial pause-ad does not create simultaneity. Re-reference only. |
| **R16**, **R25**, **UC-05** | **Not contradicted.** They govern the pause-ad's lifecycle, its live-content time freeze and the plain pause-with-no-overlay case. A7 adds a *gating condition* upstream of them ("no pause-ad is raised while an ad is presenting"); it changes nothing about how a pause-ad behaves once raised. **The extract over-states these three.** |

**Work: design.** Adopting A7 inverts a normative priority and removes or
reverses UC-08.

### Caveat that belongs on the task, not on the verdict

A7's own status in the room was *"agreed in substance, with a confirmation with
Zach Kava pending"* — Nicolás asked for it at [41:55] and David accepted at
[40:28]. The contradiction is real as stated; whether the WG's statement itself
holds is what the Zach Kava confirmation is for.

---

## A8 vs the Player-dismiss vocabulary — verdict: `compatible`

It is an absence, and an absence is an addition.

### What the extract asserts

> "Dismiss" in `context/03-requirements.md` (R16, R21) always means *the Player
> dismisses on resume*. A **viewer-initiated** skip or dismissal of a non-linear
> form is absent from the spec.

Verified on both halves.

### The literal spec text

Every occurrence of "dismiss" in `context/03-requirements.md` — lines 531, 535,
544, 551, 640, 826, 838 — is the Player acting on a state transition. The
canonical one, R16 lines 534–537:

> When the viewer resumes primary playback, the Player dismisses any active
> pause-ad form immediately and ceases firing further tracking beacons
> associated with that pause-ad.

Every occurrence of "skip" in the same file is the Player skipping an
unrenderable candidate (R5.3, R5.7, R7.2, DP-3). A grep across all of
`context/` for a viewer-initiated skip, close, or dismissal —
`viewer.*skip`, `skip.*viewer`, `skippable`, `skip button`, `user.*close` —
returns nothing in any normative file.

**And nothing forbids it.** DP-2, lines 43–53, makes silence permissive rather
than prohibitive. The spec also already models viewer interaction elsewhere:
R28's ClickThrough carrier fires on the viewer's click
(`05-dash-linear-interfaces.md` line 431, *"a conformant Player therefore fires
the click-tracking when the viewer activates the ClickThrough"*), so
viewer-initiated events are not foreign to the model — they are simply not
defined for skip.

### The transcript adds one constraint the extract under-reports

David [34:42, 34:46] does not treat support as optional:

> "my point is, we need to support it, whether or not… how it gets used and when
> it gets used, this will determine, you know, within the market."

So the addition is a **MUST-support capability with market-determined use**, not
a MAY. Rob's engagement-signal observation [34:11] and Yasser's window-size
point [34:34] went undisputed and bear on tracking, not on the requirement's
strength.

### Scope

Nothing existing is contradicted, so nothing has to give. The addition reaches:

- **A new requirement** — viewer-initiated dismissal of a non-linear form, its
  effect on the slot (does the slot end, or does the Player fall through to the
  next form under R14?), and its tracking event.
- **R16 / R21 vocabulary** — the word "dismiss" would then carry two agents.
  Either the new construct uses a different verb or "dismiss" is qualified at
  each site.
- **Tracking** — the dismissal is a reportable event; which carrier holds it is
  the open part.
- **`99-glossary.md`** — a term for the new interaction.

**Work: design** (an addition).

---

## What could not be determined, and what would close it

Two items, both for `T-02` / the WG. Neither blocks a verdict above.

1. **Whether the WG means A2 as a spec rule or as a permitted implementation.**
   Cannot be settled from the record: the transcript drops the conditional in
   the sentence the whole reading turns on, and no assent round was taken on A2.
   *Closes with:* the question drafted in the A2 section, put to David — or,
   more cheaply, David re-reading the comment as written on the doc.
   *Consequence if unanswered:* none for the verdict, which is drafting either
   way. It matters for how T-05's addition is worded to the WG.

2. **The outer boundary of A6 (§4.10).** Whether "one ad experience at a time"
   binds only what this spec controls. Verified as **not** affecting UC-04,
   which is inside the mechanism on both portions; it affects only the edges
   (an application-drawn banner outside the SGAI flow).
   *Closes with:* §4.10's existing question to David.
   *Consequence if unanswered:* the A6 task can be written and decided; only the
   scoping sentence of a future R22 rewording waits on it.

Three §4 readings were named as landing on A2's mechanics — §4.7
(`concurrent-static` as presentation vs placement token), §4.8 (whether the
placement-type list is ordered and whether order expresses preference) and §4.9
(where the declaration lives). **None of them changes the A2 verdict**, because
the verdict does not depend on the placement-type list at all: it turns on the
scope split of R18 and on the cardinality wording of R5.1 / R5.5, neither of
which the placement list touches. The prediction that "if order expresses
preference, the distance between A2 and R5 narrows sharply" is moot — the
distance is already zero on the normative text. §4.7–§4.9 remain live for the
O1 placement-type work, not for this pair.

---

## Corrections written back into the extract

Per the T-03 constraint that a disproved claim must not be left standing in the
phase material, the "Consequence for our spec" notes of A2, A6, A7 and A8 in
`svta-wg-2026-08-19-agreements.md` were updated to carry this task's verdict.
Nothing else in the extract was touched: the §1 / §2 / §3 classification, the
quotes and the §4 list are unchanged. In particular **A2 was left in §1** even
though this task finds its assent basis belongs to A1 — reclassifying it is a
decision, not a correction, and it is flagged here and in the note instead.

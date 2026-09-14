# SVTA Advertising WG call — 2026-08-19: what was agreed about the spec

Source: the Tactiq transcript of the call, Google Doc
`1E_B_53VRaBm8TwJYKTouFxZvSq2MabkO-1l0NIiIdPA` ("Advertising WG Call",
19 Aug 2026). That transcript is the **only** record — there are no
separate notes and no recording. The previous call
(`1ENK8wExWLduxv45rw08OfIoAd0KwF2w1pCVp1K4dVys`, 22 Jul 2026, the
presentation of this project to the WG) was read as background so that
nothing carried over from it is reported here as new.

Attendees: David Hassoun (chair), Frédéric Plissonneau (InterDigital),
Martin Gold (YouView), Nicolás Levy (Qualabs), Rob Walch (Apple),
Yasser Syed (Comcast). Olivier Cortambert (Yospace) was absent.

This is **not** a minute of the call. It extracts only what bears on the
spec, split three ways, because the three have different consequences:

- **§1 Agreed** — a decision was reached. Acts on the spec.
- **§2 Proposed, still open** — on the table, needs a decision.
- **§3 Mentioned, no conclusion** — context. No action.

**§4 lists what the transcript does not let us read with confidence.**
Those points are quoted verbatim and left unresolved rather than
guessed at.

Timestamps in brackets are the transcript's own, for provenance.

**How the quotes are handled.** Filler ("um", "uh", "you know",
false starts) is dropped without marking it; nothing else is. Where the
transcript clearly mistranscribed a word, the correction is in square
brackets and the transcript's own text is kept, so any quote here can be
found in the source by searching for it. Where a reading is uncertain
rather than clearly wrong, it is not corrected — it goes to §4 instead.

The call was driven by a document David had prepared collecting the
concerns and cases raised so far about the non-linear work — largely
feedback from the DASH side, though he stated most of it pertains to
both DASH and HLS [05:28]. His stated goal: have all of it in the spec
document, with a tentative thumbs-up from the DASH group and a plan for
the HLS side, then seek broader approval and submit [02:32, 02:44].

---

## 1. Agreed

### A1 — Decoder-capability detection belongs to the application, not the Player

**Proposed by David.** Detecting how many video decoders (and which
overlay surfaces) a device has is the **application's** job. The value
is passed through the Player and onto the manifest request, and from
there flows into the APS — or onto direct calls to the APS.

> "my general feel is that doesn't really belong in the player, let it
> reside in the application, it can be passed along through the player,
> and onto the requests for the manifests, which is probably what would
> happen. So that it then flows into the APS, or on the direct calls to
> the APS." [16:28]

David asked for objections, got none, and closed the point explicitly:
*"do note that I take silence as acceptance"* [16:28]. Nicolás
confirmed with *"Yep"* and *"or not strong pushbacks"* [17:15, 17:22].

David has supplemental research on how to detect multiple decode
engines across platforms and which detection methods are trustworthy;
it is attached to his document [16:28, 53:01] as a tab titled
*"Concurrent Media Decode Capability Detection for SGAI Non-Linear Ad
Experiences"*. Its comment thread (2026-08-17) asks for help verifying
it: *"we need to determine if there is actually API's to determine this
and what limitations and platforms will be a concern for this. Any help
or verification would be awesome."* The research is therefore offered
for verification rather than as a settled result, and the detection APIs
it relies on are still to be checked.

A1 is also what the WG document itself already proposes, independently
of the call: under "Capabilities detection" it asks *"How does the
Device/Application/Player know if it has support for concurrent
multi-video surface rendering? Handled at device or APS?"* and the
device branch is annotated *"Determined at the application level. Passed
to APS via manifest params or direct injection to APS calls"*. The APS
branch — *"would have to do a lookup based on passed along device
identification details"* — carries the doc's own objection, which David
repeated in the call: *"This could be a privacy concern and potentially
more limited support in certain regions pending evolving restrictions"*.

### A2 — Device capability travels **up** the chain; the ADS returns one presentation that fits

**Proposed by David. Yasser put the opposite arrangement on the table
and it was not taken further in this call. How firmly the call settled
between the two is not something the transcript establishes — see the
note at the end of this item.**

The Player tells the APS what it can render. The APS adds its own
logic (the event, the user account, the moment in the game) and makes
a **specific** ad request. The ADS answers with what it wants
rendered, and the expectation is that it gets rendered.

> "when the APS is speaking to the ADS, you should just be requesting
> what you want and know can be rendered for that individual user."
> [10:49]

> "the player is gonna talk to the APS, and say, hey, this is what I'm
> able to support, and then the APS can also have additional logic for
> the event, for user accounts, and so forth (…) and then they can make
> specific ad requests to get content that matches what they want to
> render at that time." [14:30]

**Yasser argued the opposite**: let the ADS offer what is available and
have the APS — which knows more about the device — pick.

> "should it be the ADS making that decision or should the ADS say,
> here's what's offered at that time for an overlay, and then have the
> APS decide that. In which case, it might have more knowledge of the
> device." [13:18]

**The counter-argument was about ad-delivery practice rather than about
the mechanics**: delivering several options and using only one breaks
tracking and upstream expectations.

> "with ADS systems, like a decision system, once you pass along a hey,
> here, play this ad — if you were to give multiple options and some
> weren't used, that starts creating also, I think, some tracking
> issues, and other stuff that goes upstream. Once they deliver
> something, they're expecting you to render it. That's a general
> norm." [14:03]

**What the call settled between the two arrangements is not recoverable
from the transcript, so treat the point as open rather than closed.**
Nicolás's written comment on the WG doc was referred to during this
stretch of the discussion [10:08, 10:49], and the transcript there is too
broken to show which of the questions on the table it was being cited on.
The comment — posted on the WG doc under "Capabilities detection" the
day before the call, and reproduced here in full so that any reading of
it can be checked against the source — says:

> "In my opinion at spec level we should should let devices to choose ->
> main reason: it's the most flexible design because if you don't want
> devices to choose, the APS should send only one option (this is just
> an implementation decision).
>
> In my point of view:
> - spec must be the most flexible
> - the URL to the APS is not under this spec (you could send a
>   queryparam with capabilities in your implementation if you like)
> - implementations may send only 1 options if they don't want the
>   device to choose"

Read as written, the comment argues **for** letting the device choose at
spec level, and treats "the APS sends only one option" as a **permitted
implementation**, explicitly not a spec rule — which is the R5 position,
not A2. So the arrangement recorded as A2 and the comment cited around it
point different ways, and the record does not resolve the difference. Two
questions are tangled together there, and separating them is the open
work:

- **Two different questions sit next to each other.** Whether capability
  *detection* happens at the device / application is **A1**, and Nicolás
  agreed to it. Who *chooses* the presentation is **A2**, and the comment
  argues for the device. A stretch of discussion that moves between the
  two can be read as bearing on either.
- **The transcript breaks down** exactly where the comment's conditionals
  are, so it cannot show which of the two questions the room took the
  comment to answer.

**Separating them belongs to T-03**, and if the transcript cannot settle
it, the output is a question to put to the WG rather than an edit to the
spec.

> **Consequence for our spec — verified: there is no contradiction; the
> spec does not express its own flexibility.** Every normative clause of
> R5 permits the arrangement A2 describes. The APS→ADS leg the [10:49]
> quote is about is out of scope by R18 and R18.2, so R5 never governed
> it. A single-option candidate is already conformant: R5.1 requires
> "one or more" options and R5.5 makes multiple a MAY, while R5.2's
> "render the first option whose form and layout its device can satisfy"
> is a rule for resolving a choice, not an obligation to offer one.
> R5.4 declines to *mandate* a device-class matrix; it does not forbid
> one, and DP-2 settles that silence is permissive.
>
> What fails is the drafting. Four passages read as prescribing
> client-side selection: R5's gist line, the core-invariant table line
> for R5, R5's "the Player is the **sole authority** on device
> capability", and — the sharpest — `context/02-actors.md`'s "Because
> the Player is **device-agnostic on the APS interface**", which states
> as a premise about the interface exactly what A2 denies. **T-04 owns
> the R5 and `02-actors.md` wording; T-05 owns the explicit
> single-option permission and its use case.** UC-09 survives intact —
> its own premise is that the ADS is unaware of the device class, so it
> illustrates one implementation R5 permits rather than the only one.
> The 2026-05-27 ordered-fallback decision is **not** reached: it was
> about how preference is expressed (document order rather than priority
> hints), not about who chooses.
>
> On the WG's own position, the transcript does not settle it, and the
> support the extract credited A2 with belongs elsewhere: the only
> assent in that stretch ([17:15], [17:22]) answers the Player-vs-app
> detection question of A1, and the sentence of the comment the room
> heard at [10:49] had lost its conditional ("**if** you don't want
> devices to choose"). A2 is better read as proposed than as agreed.
> The question for David is in T-03's output.
>
> Full verification, with both sides quoted, in
> [`tasks/T-03/verdicts.md`](tasks/T-03/verdicts.md).

### A3 — The IAB will not allow alternative ad experiences inside one VAST response

**Reported by David** as IAB's answer to the multi-layout-fallback
idea. This is the external constraint that forces A2.

> "IAB pushed really hard back, I believe, on that, and said they don't
> want to have alternative ad experiences within a single VAST response
> right now. (…) the biggest gist was, like, no — you should request
> what you want, and you'll get that, and not have multiple things
> within there." [30:33]

David will keep following up with the IAB, and noted that if that ever
changed, the selection could move back to the client:

> "If we ultimately didn't have to worry about that, and we were able
> to get multiple, then we could do this kind of selection at the later
> point, as to which one we wanted. (…) that's in part why we kind of
> focused up ahead, to make sure that we are requesting and have the
> right details from the player." [31:06]

### A4 — The ADS decides the layout

**Stated by David**, in answer to Yasser asking whether the layout is
chosen programmatically or specified by the buyer.

> "the ADS will determine which layout you get. And that's gonna be
> based off of whether it could be programmatic or other forms of
> their decisioning and inventory. What we're trying to make sure we
> handle is, like, hey, don't give me an overlay ad that's a video if I
> can't support two video decoders. Or if I'm doing an L box — I can do
> an L box with a static image, but I can't do an L box with an
> additional video in there." [12:20]

### A5 — Slice/tile single-decoder replacement is out of scope for this edition, but recorded as a breadcrumb

**Raised and deferred by David; Yasser asked for the note.** Replacing
a slice or tile lets a single decoder carry both the content and the
ad, works at the edge without a full transcode, and exists in H.264
but more so in HEVC and AV1. Some platforms already have solutions
built around it. It is deferred to keep this edition finishable.

> "I don't think we're looking to tackle this for now, this could be in
> the next version. (…) booting it for now is the idea from the spec
> perspective, because we want to be able to actually get this stuff
> done at some point." [08:51, 09:19]

> Yasser: "just to leave it in the notes, you should say that you can
> use a single decoder on that and just leave it as a breadcrumb for
> later." [09:32]

> David: "that'll be the indication — hey, there are options for this,
> this is not covered in this spec at this time, although we will
> hopefully look to provide solutions in the future." [09:40]

### A6 — One ad experience at a time. This is a general rule

**Stated by David, generalised by Nicolás, both agreeing.** No two ad
experiences may be presented at the same time — not two non-linear
forms, and not a non-linear form on top of a linear ad.

Yasser asked whether a non-linear ad could run while a linear ad plays.
David's answer was an unqualified no [36:46]:

> "you can only do one type of ad experience at a time, meaning linear,
> non-linear, at a most basic level, but even deeper than that. Like,
> you can't mix (…) at least not trying to support that now. If demand
> really came up (…) there's all sorts of brand conflicts. That's what
> companion ads are for today. So there's already the option to do
> things like that. We're not going there." [37:29]

Nicolás: *"So we can say that all the different options, layouts,
stuff — one at a time"* [37:23] and *"I agree. Keep it simple for
now."* [38:08]

Later, discussing pause ads, David restated it as the general rule and
Nicolás agreed:

> David: "this is, like, a general rule. You cannot have two ad
> experiences at the same time." [42:30] — Nicolás: "Yes." [42:35]

> **Consequence for our spec — verified: a contradiction, and it lands
> on UC-04, not on R22.** R22 in `context/03-requirements.md` bounds
> simultaneity **within** the non-linear family only, so it is narrower
> than the WG rule but not incompatible with it. The spec is not silent
> across families, though: **UC-04 — Hybrid linear + concurrent
> overlay** in `context/04-use-cases.md` models precisely the case A6
> forbids ("a linear ad takes over the screen *and* a non-linear overlay
> is composited on top of it during the same break"), specified against
> all five device classes and carrying its own row in the coverage
> table. Adopting A6 deletes that use case and widens R22 from "one
> non-linear form" to "one ad experience", which also moves the
> decoder-budget rationale phase `04-multiview` leans on. The §4.10
> scope caveat does not rescue UC-04: both of its portions are
> Publisher-declared and APS-resolved, i.e. inside the mechanism.
> Detail in [`tasks/T-03/verdicts.md`](tasks/T-03/verdicts.md).

### A7 — Pausing during an ad break does not trigger a pause ad; the running ad owns that time

**Stated by David as current industry practice; Nicolás agreed and
asked that it be confirmed with Zach Kava.**

> "I think today the standard is if you pause during an ad break, you
> do not — you're not going to show your pause ad state as well. The ad
> is paused until they resume. (…) I think IAB even defines this stuff,
> because once you've started an actual ad within an ad break, they own
> that time until it's completed or abandoned." [41:27]

Nicolás had raised the case (pause in the middle of an L-bar or a
side-by-side: which wins?) [40:41], and accepted the answer as an
instance of A6:

> "even if it is a post add [pause ad], a concurrent presentation or
> whatever, it's just one at a time. You cannot define a window where a
> post ad [pause ad] plus L shape goes together. I think that I'm okay
> with that, but it will be nice to check with Zach expectations. I
> think that expectation sounds reasonable. (…) And simple, and
> simplifies a lot of stuff." [41:55, 42:27]

So: agreed in substance, with a confirmation with Zach Kava pending.

> **Consequence for our spec — verified: a contradiction.** R17 in
> `context/03-requirements.md` gives the pause-ad priority **over** a
> running overlay and suspends the overlay, and R17.4 declares that
> priority non-invertible. The WG's rule reverses it for the case where
> the pause happens while an ad is already presenting — the case
> Nicolás put at [40:41] in those words. **UC-08 — Overlay window
> crosses a pause-ad window** in `context/04-use-cases.md` is that exact
> state resolved the other way, across all five device classes, and is
> contradicted whole.
>
> Two claims are tangled in A7 and they do not have the same verdict.
> Nicolás's restatement at [41:55] — no pause-ad *plus* L-shape at the
> same time — is **already** the spec's position (R17 suspends the
> overlay so nothing composes simultaneously, per R22). What
> contradicts is David's half: which of the two wins. R21 is only
> re-referenced; R16, R25 and UC-05 are **not** contradicted — A7 adds a
> gating condition upstream of them and changes nothing about how a
> pause-ad behaves once raised. Detail in
> [`tasks/T-03/verdicts.md`](tasks/T-03/verdicts.md).

### A8 — Viewer-initiated skip of a non-linear ad: existing mechanics carry over, support is required, the market decides its use

**David's position, with contributions from Nicolás, Rob and Yasser.**
Nothing new is needed in the schema:

> "existing logic and capabilities for schema should work for
> concurrent, as they do for linear (…) I don't see how anything really
> changes. (…) I don't think anything changes from what is out there
> today." [31:06, 31:39]

The **need** for skip should be lower, because the point of the format
is that the viewer does not lose content. But the capability must
exist:

> "my point is, we need to support it, whether or not… how it gets used
> and when it gets used, this will determine (…) within the market."
> [34:42]

Variants named, all as options rather than requirements: a premium
tier that always offers it, and a timer-gated eligibility —

> "it always can be on a timer, like, hey, as long as you've seen this
> for 5 seconds — especially if it's a static L-box: I saw it, I'm
> done, let me out of this." [32:32]

Nicolás pushed on the live case (*"if we go to live, like, the skip, it
sounds weird"* [32:25]) and named a second reason a viewer would
dismiss: to get the content back at full size.

> "maybe if you are doing, for some reason, dual box something and put
> in an ad, maybe I want to put again my content in full resolution."
> [32:57]

Two observations were added and neither was disputed:

- **Rob**: dismissing a non-linear ad is an engagement signal, not a
  negative one — the person was present enough to dismiss it. From the
  QOE meeting the week before [34:11].
- **Yasser**: the video window size changes between the skip and
  non-skip states, which may itself make skip preferable [34:34].

> **Consequence for our spec — verified: an absence, not a conflict.**
> "Dismiss" in `context/03-requirements.md` (R16, R21) always means
> *the Player dismisses on resume*, at every one of its seven
> occurrences, and every "skip" in that file is the Player skipping an
> unrenderable candidate. A **viewer-initiated** skip or dismissal of a
> non-linear form appears nowhere in `context/` — and nothing forbids
> it: DP-2 makes silence permissive, and R28's ClickThrough already
> fires on a viewer action, so viewer-initiated events are not foreign
> to the model. So this is an addition, not a change. One nuance the
> item under-reports: David's *"we need to support it"* [34:42] makes
> the capability a MUST-support with market-determined use, not a MAY.
> The addition reaches a new requirement (its effect on the slot and
> its tracking event), the two-agent ambiguity it creates for the verb
> "dismiss" in R16 / R21, and a `99-glossary.md` term. Detail in
> [`tasks/T-03/verdicts.md`](tasks/T-03/verdicts.md).

### A9 — Joining a live stream mid-break with a pre-roll pending: nothing changes

**David.** The hard cases are real (a 3-minute mid-roll joined one
minute in, with a 30-second pre-roll: prioritise the pre-roll and then
drop into a break with a minute and a half of slate; or try to resume
mid-way into the mid-roll and absorb a 3-to-5-second drift) and premium
platforms do handle them. But they are not created by this work.

> "There's already, I think, generally logic in both HLS and DASH for
> these situations. Nothing should really change in that. (…) anything
> we're doing here, none of that changes. This isn't anything specific
> to that. And you should keep it as such." [34:55, 36:07]

### A10 — An empty ad break is not a non-linear problem; noted, not prioritised

**David**, with one sub-question he left open (see O7).

> "if the ad break gets empty, the APS can fire tracking and so forth,
> client-side can fire tracking if necessary; would need to add signals
> to the response from the interstitial — needed to define what this
> would look like. Once again, though, this isn't anything specific to
> non-linear, and I'm not too worried about that. These things do
> happen today. Those are missed ad breaks. That's missed revenue, so
> it's important that they're identified." [38:09]

### A11 — SSAI and SGAI are not mixed inside one ad break

**David.** Technically the layout-control machinery could be applied to
SSAI, but it is not where this belongs.

> "I don't see you doing, like, hey, we're gonna use SGAI per the
> concurrent, and SSAI for the linear in a single ad break. That would
> be… not wise, I don't think. (…) Everything in this document is
> geared towards SGA [SGAI]. (…) With what we're doing for some of the
> layout control and other stuff, that could be applied to SSAI, but I
> don't think it really makes sense." [50:49, 51:06]

### A12 — SIMID stays out

**David.**

> "if you're using SIMID, you should be — it should just be use SIMID.
> (…) SIMID as a non-linear element in a concurrent also probably goes
> against the IAB spec as well. So if you want to do SIMID, use SIMID.
> If you want to do your own stuff and non-linear, then this is what
> this is about." [51:50]

### A13 — On the HLS side: a new non-linear interstitial class in an SVTA-owned namespace

**David, with Rob agreeing.** The HLS mapping keeps today's
interstitial flow and adds a non-linear class that the SVTA can define.

> David: "right now, when you're doing the interstitial, you're putting
> in the interstitial class into the manifest. My thought is you would
> now have a non-linear class that SVTA or whatnot can make, and that
> would help handle the experience, but we get to follow the same flow
> of what you guys are doing today." [54:29]

> Rob: "don't make it come.apple.hls [com.apple.hls], I guess, if it's
> not coming from Apple." — David: "No. Exactly. We do something like
> com.svta." [55:24, 55:28]

A point of fact was settled with Rob along the way: HLS interstitials
are themselves always VOD, but they can be placed inside **live**
primary content, which is all this work needs [28:34–29:12].

### A14 — The "alternative experiences" agenda item is dropped

**David**, on an item in his own document: its original intent was no
longer clear, so it was dropped rather than interpreted [29:36].

### A15 — Next step: mock samples in both HLS and DASH, authored by David with Nicolás

**David.** Concrete syntax examples come before more prose.

> "my next step is, I can actually start putting together some mock
> samples showing how I would think that this would be represented, I
> can then share that with you down the road." [29:36]

> "I think the next step is I'm gonna try to take this next up, and
> Nico, probably see if you're game to still continue to help me work
> through some of this. Start creating some samples, both with HLS and
> DASH, showing how this stuff would bubble in, and how this stuff
> would flow. I generally think those work the best to have this
> hopefully make some sense. And with adjoining documentation."
> [53:37]

David will then run the HLS half past Rob [54:04], and take it to
prospective adopters [55:54]. Rob's advice: seeing it work at the app
layer first, with a demo, would help the case [55:47].

WG cadence: nominally every two weeks, in practice every other one
[04:19].

---

## 2. Proposed, still open

### O1 — A placement-type declaration in the MPD: `replace` / `insert` / `concurrent` / `concurrent-static`

**David's proposal, and the core structural addition of the call.** The
manifest declares which insertion modes are permissible for a break.
The Player, knowing what it can render, either satisfies one of them or
skips the break.

> "Placement should indicate what type of placement is supported. So
> now we're talking about in the manifest — essentially, with a
> playlist. These are some DASH terms, of course, right now, but
> ultimately, today we have things like replace and insert. Those have
> different use cases, obviously, especially when we're talking about
> VOD: are we replacing content? Are we inserting content? Same with
> live — live we're generally just replacing content. There is not
> usually an insert that pushes you further back from your live point.
> Now we have also the ability to have concurrent, is the theory."
> [17:41, 18:23]

The combinations David walked through, each with a different intent:

| Declared | Meaning |
| --- | --- |
| `concurrent` only | The content must not be interrupted. A single-decoder device skips the break. |
| `concurrent` or `insert` | Never replace, so a VOD stream never loses content. |
| `concurrent` or `replace` | A device that cannot do concurrent gets a standard linear break instead. |
| `concurrent` or `concurrent-static` | An L-box with an image is acceptable when two video decoders are not available. |

> "if it's not skippable, then you would only say you can do a
> concurrent ad here and nothing else. And if you can support a
> concurrent, do it. If not, skip the ad. But if it's either one, you
> could say concurrent or replace, meaning that I could handle either."
> [23:53, 24:08]

`concurrent-static` means an image rather than a video, confirmed in an
exchange with Nicolás:

> Nicolás: "is like image, it's just an image" — David: "yeah, for
> static." — Nicolás: "and so concurrent, you mean concurrent, you will
> need two decoders (…) concurrent image is just image rendering
> capabilities" — David: "yeah, it means we have image capabilities and
> or video." [24:33–24:49]

**What is open**: whether `concurrent-static` needs its own
*presentation* element or is only a *placement type* (David's own read
is the latter — see §4.7), and exactly where in the MPD the
declaration lives. David's placement of it is tentative:

> "this is not in the MPD list, this is in the top level MPD in this
> regard?" [19:57]

Yasser's summary of what this achieves, unchallenged: *"that sounds
like options from the ADS to say which way it wants it to behave"*
[24:55].

### O2 — Skipping the break when no declared placement type is supported, with tracking

**David.** The consequence of O1, and the case that motivates it.

> "if a placement is limited to types that are not supported on that
> device, the ad break would be skipped with an appropriate event
> tracking to indicate such." [18:23]

The reasoning is content loss, and it is sharpest in live:

> "if you have live and you did a concurrent only, because you don't
> have a good breakpoint (…) you would either lose content or push
> people back from your live point. That's a really bad thing. In which
> case, we need to skip it." [19:16]

And the break stays in the manifest for everybody — it resolves
per-device:

> "we need to have the option to skip it, but it's still gonna be in
> that manifest. So for some users, they're gonna be able to act on it.
> Some users are not. All depending on their devices." [20:47]

Yasser's squeezeback example was accepted as the canonical shape of
this: a capable device keeps the game on screen with the ad alongside;
a device that cannot must have the ad interrupt instead [22:37–23:18].
David then added the constraint that decides which of the two is
allowed: what the content is doing at that moment. If the break falls
over commentary, the viewer missing it is acceptable; if it falls over
live action, an interrupting linear break costs them the play itself,
and that is not [23:26].

Yasser drew the conclusion that the composition author must express
this, and David confirmed it is exactly what the declaration is for:

> Yasser: "you have to define — someone who's creating the composition
> would say, yeah, it's fine to be skippable versus…" — David:
> "Exactly, so that's what we're defining with this." [23:45, 23:53]

**What is open**: which tracking signal fires on a skipped break, and
whether the skip is reported to the APS.

### O3 — Mixed ad types inside one break, and how the linear member is signalled

**Raised by David, confirmed as real by Nicolás; the mechanism is
unresolved.** A break of concurrent, concurrent, linear, concurrent,
then back to content.

> "we have content, and then we go to a concurrent ad. Another
> concurrent ad. What about mixing in a linear ad in the middle of
> that, and then another concurrent ad? And then back to content. Is
> this something that we would ever do?" [42:59]

Nicolás: *"I already saw this in the World Cup (…) in the refreshment
water [break]"* [43:46]. Yasser: it could equally be overlays first
that then go into an ad [43:32]. David: *"I agree, I think this
definitely can happen, and will happen"* [43:56] and *"the idea is this
can and should be able to be supported. We know that it is"* [49:47].

**The unresolved part** is how the linear ad in the middle is known to
be a replace or an insert:

> "the tricky thing, though, that I don't have an immediate answer of
> how we would handle is, how do you know to do replace or insert on
> the linear one in the middle." [43:56, 44:20]

Three candidate answers were floated and none was chosen:

1. **Extend the placement-type declaration of O1** so its linear member
   carries insert-vs-replace. David: *"we would say concurrent, or —
   and then we would then specify — well, it wouldn't just be linear.
   We'd have to go beyond that, so that might be the key thing"*
   [45:46].
2. **Let the APS decide it at resolution time** and write it into the
   `ListMPD` or the HLS interstitial. David: *"Or does it? I'm trying
   to think, maybe we don't. (…) it could be controlled by the APS,
   then. And the APS could define that there (…) when writing it into
   the MPD list, or the HLS interstitial, it would then be able to
   define it as replace or insert at that time"* [46:39]. Nicolás
   agreed with this one: *"I agree that it should be the APS telling
   you what it's going to be the experience like"* [47:05] and *"we are
   expecting the APS to tell you what the experience will look
   like"* [47:55].
3. **A separate structure**, rather than reusing the existing MPD-level
   insert/replace. Nicolás: *"maybe to create these use cases, we need
   to create another structure for this and not attach to what already
   exists"* [47:05].

David's closing framing of the item:

> "we just need to work through where and how are we going to define
> this and make sure the data can flow, and that it [isn't] excessively
> burdening on users to be able to implement it." [49:53]

A supporting point of fact was settled in passing: replace and insert
are **not** VOD-only. VOD can use either (replace on a recorded sports
match, unless the breaks were collapsed, in which case insert), and
live generally only uses replace — insert is technically supported but
pushes the viewer back from the live edge [44:33–45:20].

### O4 — The list of what the APS needs to receive from the Player

They started drafting it live and did not finish it [48:21–49:08].
What made the list:

- The layout / ad types wanted. Nicolás: *"layout slash replacement
  types or ad types you want"* [48:54, 48:58].
- Insert, replace, linear, concurrent. David: *"it also needs to know
  insert, or replace, or linear, concurrent"* [49:08].
- *"what else?"* — left unanswered.

> **Consequence for our spec.** R18 in `context/03-requirements.md`
> declares the ADS and APS APIs out of scope and specifies only the
> Player-visible interface. This list is a specification of what the
> Player sends to the APS, which R18 currently excludes.

### O5 — Pause ads have no manifest definition yet, on either side

**David**, who owns the follow-up. This is the item where this project
has material to contribute rather than to absorb.

> "I don't think we've actually gotten good definition on how these get
> defined and [in] manifest from a spec perspective, at least on the
> SVTIA [SVTA] side at all yet. (…) I don't know how we want to better
> handle these, and how we best need to define these." [39:15]

> "We need to go do some research and figure out what people are doing
> today. Does that actually get defined into the manifest playlist, or
> is it just at the application, or player level? And is there a way
> that we can better unify any of this?" [39:52]

He asked the room for insight into current practice; none was offered in
the call. Follow-up: check with Zach Kava and others, and cross-check the
V3 document, which may already carry some of it [40:28].

### O6 — Naming: the decisioning server, and "canvas"

**David** confirmed APS = Ad Presentation Server, the name he coined
for the interstitial service, prompted by Nicolás supplying the missing
word [05:56–06:40]. He then asked for opinions on what to call the
decisioning server, aiming for something that works for both HLS and
DASH: *"if anyone else has strong feels on what we should start calling
that, great"* [06:40]. Nobody offered one.

**Yasser proposed "canvas"** for the viewable area, with the video
display area occupying all or part of it [06:56–08:00]. David resisted
the term while agreeing on the concept: *"I think it was a little bit
of danger of using the term canvas, because it's also an HTML5 term"*
[08:01]. He named the underlying problem rather than solving it:

> "one of the challenges that I think a lot of these groups run into is
> that you start using different kinds of vernacular across different
> groups. And then you always have to decipher it as you're going
> across systems." [08:13]

No term was adopted.

### O7 — Should the APS act on an empty break, or pass it to the client?

Left open inside A10. David finds passing it forward wasteful but
described it as how things work today:

> "I do think this is an interesting thing to think about — what should
> potentially be happening more so now at an interstitial service, APS,
> that if it sees one, what it should do about it? Or does it just pass
> it forward, and then it falls into the client? To me, I feel that's
> kind of wasteful. But, you know, that's how things kind of work more
> today." [38:09, 38:53]

---

## 3. Mentioned, no conclusion

- **Viewers switching to a device that skips the ads.** Yasser raised
  it as a possible perverse incentive; David acknowledged it and parked
  it: *"I don't think that's a big one to worry about yet (…) we don't
  know if that would really have any type of impact"* [21:38, 22:03].
- **Frame accuracy and stream conditioning.** Yasser asked whether
  concurrent breaks need frame-accurate, conditioned splice points.
  David: inserts and outs should be frame accurate, but *"that's all
  nothing new or specific"*; SSAI needs conditioning, SGAI has more
  slack [27:27–28:19].
- **Under-filled breaks and slate.** A 2-minute break filled with 1:45
  of ads leaves 15 seconds of slate; avoided with programmatic and
  other factors; David called it *"a theoretical solution"*
  [26:57–27:25].
- **Quartile beaconing still has to fire** during the ad (Yasser)
  [42:46], which David agreed is part of why the mixed-break case gets
  complicated [42:54].
- **MoQ and ad signalling.** Steve Rydell (Paramount, Pluto side) is
  adding a MoQ version of the ad spec 2.0 as an IETF draft, and has a
  MoQ stitcher with SCTE-35 and beacon timing. David shared the link
  and asked for feedback; he wants to kick this off in the OpenMoQ
  group [03:54, 52:29]. See §4.3 on the names.
- **Other WG threads with no update**: Common Ad Interface (Casey — no
  update; meetings lined up, plus VideoJS 10 work), contextual ads (no
  update, owner not in the call), the skippable-ads document (authored by
  David Glasson; no update in this call, and it may be published as it
  stands), and David's intent to add
  non-linear material to the SVTA university course once this is locked
  down [03:11, 04:19, 04:55].
- **An earlier HLS non-linear proposal** that Rob referenced was, in
  David's recollection, too specific to its authors' own system and
  server-side processing; he wants something broader and adoptable
  [54:45–55:24]. See §4.6 on the name.

---

## 4. What the transcript does not let us read with confidence

This is an automatic transcript. The following are unresolved rather
than guessed, with the verbatim text alongside so they can be settled
at a glance.

1. **The deadline David is working to.** *"my goal, personal goal, is
   buy the RENS meeting. I want to have this all updated in the spec
   document"* [02:32]. Most likely "by the Rennes meeting", an MPEG
   meeting, but the date it implies is the thing that matters and the
   transcript does not give it.
2. **"Christian Hillsbury"** [03:11] — a name Casey is meeting about
   the Common Ad Interface. Probably mangled.
3. **The MoQ item's names.** *"Steven Rydell"* [03:54] and *"Steve
   Rydell from Paramount, I believe Pluto side"* [52:29]; *"adding a
   mock version to the ad spec, 2.0 as an IUT. ITF draft"* [52:29].
   Read as: a **MoQ** version of the ad spec 2.0 as an **IETF** draft.
   "mock" is MoQ throughout the transcript, and "open mock group" is
   OpenMoQ.
4. **"Zach Kava"** [40:28] — the pause-ads contact, also referenced for
   adoption [55:54]. Note that "PAWS ads" throughout the transcript is
   "pause ads".
5. **"Sarge"** [03:11] — the contextual-ads owner, who did not join.
   Also, "Olivia" in the opening [01:30] is Olivier (Cortambert,
   Yospace).
6. **The earlier HLS non-linear proposal.** *"like what Mikel presented
   from Mikhail Vermatemi presented last year, right? HLS interest,
   something like that"* — Rob [54:45]. Two garbled names for what is
   probably one person and one company.
7. **Whether `concurrent-static` is a presentation or only a placement
   type.** David's sentence answers itself mid-way and is worth
   confirming: *"The one thing I wasn't sure, and that I had added on
   at this time was the concurrent static. Before, we just had kind of
   this concurrent presentation. Is that still good enough, or do we
   need to break out a secondary one for the static. I don't think we —
   I think the presentation's fine. This was just now adding in a
   placement type."* [19:57]. Read as: no new presentation element,
   only a new placement-type token.
8. **The grammar of the placement-type list.** David gives examples of
   permitted combinations [24:08–25:40] but never says whether the list
   is ordered, whether order expresses preference, or whether it is an
   unordered set the Player intersects with its capabilities. Our own
   R5 makes document order the preference order; whether the placement
   list inherits that convention is not addressed.
9. **Where exactly the declaration goes.** *"you think about it in the
   top low in the — the primary playlist, right, in this case, like the
   MPD, you know, you're specifying, essentially — was it, like, a
   period? You need to spend—"* [46:16]. David appears to be asking
   whether it is declared on a Period, and the sentence breaks off.
10. **The scope of the one-at-a-time rule.** Nicolás: *"or not not to
    add experiences inside the player, let's say, controlled by this
    mechanism"* [42:42]. Reads as "not two ad experiences inside the
    player, controlled by this mechanism" — i.e. the rule binds what
    this spec controls, and an application-drawn banner outside the
    mechanism is not in scope. Worth confirming, because it materially
    bounds A6.
11. **The name of the agenda item behind A3.** *"Multi-layout fallback,
    so limited codes, multiple layout fallback, memorization"* [30:03].
    "limited codes" is limited decoders; "memorization" is probably
    "memoization". The item's real title is not recoverable.

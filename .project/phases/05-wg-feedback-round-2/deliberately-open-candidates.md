# The sixteen silences: which of them are deliberate?

`context/03-requirements.md` now carries a **Deliberately open** table,
and it is empty. The mechanism is built; what goes in it is a judgement
per question, and this document is the proposal — one line of reasoning
each, for the owner of the specification to accept, reject or redirect.

Nothing here has been written into `context/`.

## What has been decided since

The owner of the specification answered on 2026-09-17. The proposal
below is left as it was made; this section records what came back and
where it went, because the table further down is no longer the state of
play on five of its rows.

| Finding | Decision | Where it went |
|---|---|---|
| `EC-6` | Give the pause family the same once-per-session capability the base standard gives timeline events. The reason is symmetry. | **R34**, new. It is no longer a candidate for the open table. |
| `EC-2` | The pause ad wins over a linear ad on screen. Taken as a weak decision, with the weakness declared. | **R17.5**, plus ADR 0013, plus a working-group issue drafted and not published. |
| `A-5` | Always presentation time. | **R19.4**. A clarification of R19, which already carried the formula for media-backed forms; no new requirement was needed. |
| `EC-1` | Answered by the one above: with cap arithmetic on the presentation timeline, a suspended form accrues nothing. | **R4.11**. |
| `EC-4` | A pause document should be able to carry ordered fallback options. | **Nothing written** — R5 already requires exactly that, for every family. See below. |

**The residue on `EC-1` does not exist.** The question was whether a
form suspended for a reason other than a pause would accrue cap. Every
suspension this specification defines is R17's, and R17's precondition
is that the viewer is paused inside a pause-ad window. R22 does not
suspend anything: it prevents a second non-linear form from starting
rather than pausing the first, and its forms are sequential by
construction. So there is no suspension while the presentation timeline
advances, and R4.11 covers the whole of the case.

**`EC-4` was already answered by R5**, which is why nothing was
written. R5 requires each candidate to carry its presentation options
as an ordered list in preference order and the Player to render the
first one its device can satisfy — video first, image after it, exactly
as proposed — and R5 is scoped to "the resolution document the Player
reads", with no family restriction. UC-09 already walks the case across
five device classes.

One distinction is worth a separate answer, because the proposal can be
read either way. R5's check is a **capability** check made before
anything is rendered: can this device satisfy this form and layout. It
is not a **runtime-failure** fallback: a video that passed the check,
started, and then failed to play. `context/` states nothing about that
case for any family, and it would be a new capability rather than a
clarification. It is not written here, and it is flagged rather than
assumed.

### One status change, recorded where it can be named

`EC-5`'s answer already existed in the generated spec, in **Annex L.3**
— *"validates its candidates against window 1202's own constraints"* —
and that annex is marked *Informative*, while §4.6.8 says nothing. So
the rule was answered where it could be read and not where it had to be
obeyed.

R20.5 and R20.6 move it to normative. The requirement itself cannot say
"Annex L.3" — a `context/` file that points at the generated spec
inverts the dependency arrow — so R20.6 states the change of status in
terms of what must hold, and the annex is named here, which is the only
place that can name it. A reader who later finds the same sentence in an
informative annex should know it was promoted on purpose and not
duplicated by accident.

## Why the table is not simply filled with all sixteen

`v7.2-findings-classified.md` groups sixteen findings as *"the spec is
silent where it cannot be — may stay open"*. That grouping answered a
different question: **why the pipeline stalls**. It is not a list of
deliberate silences, because nothing about those sixteen was decided —
they are the places where nobody wrote anything yet.

Declaring all sixteen open would make the promotion gate say what its
author wanted to hear. A register that absorbs unfinished work stops
being a record of decisions and becomes the place blockers go to
disappear, which is the exact failure the gate exists to prevent.

So the proposal sorts them three ways, and **only the first is a
candidate for the table**:

| | Meaning | What happens next |
|---|---|---|
| **open** | A real question this specification is not ready to answer, usually because the answer depends on something outside it | a row in the table, with its reason |
| **decide** | The answer is a choice with a cost either way, and leaving it unmade makes two conformant Players behave differently | Nicolás decides, then `context/` and a major build |
| **write** | There is a correct answer and no trade-off; it is missing text | the pipeline, on a refinement pass |

## The sixteen

| Finding | The silence | Proposal | Why |
|---|---|---|---|
| `G-1` | no timebase or rounding rule for cap arithmetic | **write** | The comparison is an `xs:unsignedLong` in timescale units against an `xs:duration`, and the base standard already fixes the units. Rounding has one defensible direction — down, so a cap is never overrun — and stating it costs nothing. |
| `G-2` | no Player behaviour when a slot carries no `@maxDuration` | **write** | §5.1.1 already keeps the base standard's unbounded default. The silence is that the spec never says so out loud. |
| `G-3` | `@allowedLayouts` is not bound to the slot family | **decide** | Binding the token space to a family narrows what a Publisher can declare. It travels with R12 / R21 and `EC-4`; deciding those decides this. |
| `G-4` | `<Event>@id` uniqueness is scoped nowhere | **write** | The base standard scopes `@id` within its Event Stream. The spec has to cite that rather than invent a scope. |
| `G-6` / `M3` | no request-type key covers a non-linear resolution request | **open** | The key space is not ours: it belongs to the request-type registry the linear path already uses. Answering it unilaterally mints a value someone else governs. This is a genuine "not ready", and it is what a row in the table is for. |
| `G-7` / `M1` | the candidate-level callback `<EventStream>` has no validation clause | **write** | Every other carrier in the spec states what makes it valid. This one was missed, not deferred. |
| `M5` | the SGAI event schemes define no `@value` value space | **open** | Leaving `@value` unconstrained is a defensible position — it keeps the scheme extensible — and constraining it later is a breaking change. Whichever way it goes, it should be a stated position and not an omission. |
| `EC-1` | does the slot cap accrue while a non-linear form is suspended? | **decide** | Both answers are implementable and they produce different ad durations. Left unmade, two conformant Players bill differently. |
| `EC-2` | a pause inside a pause-trigger window while a linear ad occupies the screen | **decide** | The question is whether the pause ad competes with a linear ad for the screen. It is a product call about what the viewer sees. |
| `EC-3` | a `200` resolution document of the wrong family for the slot | **write** | R20.1 and R30 already define what an unusable resolution produces. This case falls under them and needs to be said. |
| `EC-4` | a fullscreen pause ad on a device with no overlay capability | **decide** | It is the R21 contradiction seen from the device side, and it is already blocking for another reason. Deciding R21 decides it. |
| `EC-5` | whose `@allowedLayouts` binds the candidates served from a fallback window | **write** | One of the two readings is consistent with R20's ownership model and the other is not. |
| `EC-6` | `@executeOnce` on a pause-trigger window | **open** | A pause trigger is not consumed the way a timeline event is, and the base standard's counter semantics were written for the timeline case. Until ADR 0011's model is exercised against a trigger, a stated "not answered" is more honest than either answer. |
| `A-4` | "overlay" names a family, a document class, a profile URI and a layout token | **write** | Four meanings on one word is a terminology defect with a mechanical fix. |
| `A-5` | a still image's declared duration under non-1× playback | **decide** | Whether a declared duration is wall-clock or presentation time changes what the viewer sees at 2×. Both are defensible; it needs a choice. |
| `A-7` | Annex D.3's linear portion is 15 seconds and 30 seconds | **write** | An internal inconsistency in one annex. |

## The count

```
open    3   — G-6/M3 · M5 · EC-6
decide  5   — G-3 · EC-1 · EC-2 · EC-4 · A-5
write   8   — G-1 · G-2 · G-4 · G-7/M1 · EC-3 · EC-5 · A-4 · A-7
```

**Three of sixteen.** The other thirteen are not silences the project
chose; eight are text nobody has written and five are decisions nobody
has taken. Recording those as deliberately open would clear the gate
without changing the specification, and the specification is the thing
the gate exists to protect.

## What this means for the promotion gate today

Only the three in the first group would be added to
`context/03-requirements.md`, each with the reason above and a pointer
to where the decision is recorded. The five in the second group are the
kind of item the gate is designed to surface: they stop the loop and
reach a person, which is what they need.

The eight in the third group should stop blocking by being fixed.

## The same frontier, one level up

The seventeen criteria that state an obligation with no modal are the
same shape of question: the mechanism for recording them exists, the
judgement about each one does not belong to a script or to whoever runs
it. They are not proposed here, and they are named so that their absence
from this list is not read as their having been handled.

---
phase: 05-wg-feedback-round-2
title: Working-group feedback — round 2 (SVTA Advertising WG, 2026-08-19)
status: planning
started: 2026-08-19
closed: null
---

# 05-wg-feedback-round-2

Process the feedback from the **SVTA Advertising WG call of
2026-08-19** — the first round of WG feedback that arrives as a
**group discussion** rather than as one reviewer's marked-up files.
David Hassoun walked the group through a document collecting every
concern raised so far about the non-linear work; the call produced 15
agreements, 7 open proposals, and a set of items that were mentioned
without conclusion.

The phase's material is the agreements extract,
[`svta-wg-2026-08-19-agreements.md`](svta-wg-2026-08-19-agreements.md).
The phase's **work product** is a task per proposed change, so each one
can be decided on its own — preceded by a verification of the four
places where the extract claims the WG's position breaks against the
committed spec, because those claims are a reading of an automatic
transcript and the reading is what the rest of the phase is built on.

## Objective

Turn the 2026-08-19 SVTA Ads WG call into a decidable backlog: compare
what the WG agreed and proposed against `context/02-actors.md`,
`context/03-requirements.md` and `context/04-use-cases.md`, and emit
**one task per proposed change or addition** — each self-contained
enough to be discussed and resolved on its own, one at a time, between
Nicolás and the agent.

Before that, establish whether the four conflicts the extract asserts
(A2 vs R5, A6 vs R22, A7 vs R17, A8 vs the Player-dismiss vocabulary)
are real, by checking them against the transcript and the literal spec
text rather than against the extract. `compatible` and `indeterminate`
are as valid as `contradiction`; where the transcript cannot settle it,
the output is a question for the WG, not a change to the spec.

Independently of that, make R5's **designed flexibility** explicit in
`context/`. Its author has confirmed that R5 was written as a superset —
the APS may send ordered options, the device may send capabilities
optionally, and an implementation may send a single option with the APS
holding control — and that the text does not currently make this legible.
That is a drafting problem, not a design one, and it is worth fixing
whatever T-03 concludes.

And state outright what the text never says: **that an APS may return
exactly one presentation option**, with the choice then sitting at the
APS. Nicolás asked for this explicitly and leans toward a **use case**
that carries the motivation — an APS that wants to offer only one
option. If it lands as a use case it forms a **pair with UC-09**, which
shows the device choosing: together they teach the superset better than any
adjective in a requirement can.

## Context

- **Round 1 (phase `02-wg-feedback-round-1`) was one reviewer's files.**
  David Hassoun marked up three `context/` files offline and returned
  them; the phase cross-referenced his 10 items against the spec and
  drove them to closure. Round 2 is a different shape: a live
  discussion among six participants, where agreements, proposals and
  asides are interleaved in the same sentences.
- **The transcript is the only record.** There are no separate notes
  and no recording. The extract in this phase quotes it verbatim
  wherever a reading is load-bearing, and marks what the transcript
  does not support with confidence instead of resolving it.
- **The previous call (2026-07-22)** — where this project was presented
  to the WG — was read as background, so that nothing carried over from
  it is reported here as new.
- **Four items are *reported* as breaking against the committed spec —
  and that reading is itself under verification.** A2 (device capability
  travels up to the ADS, which returns a single presentation) is
  reported as contradicting R5's device-agnostic ADS/APS with ordered
  presentation options, on which UC-09 is built; A7 (pausing during an
  ad break does not raise a pause ad) as pointing against R17; A6 as
  broader than R22; A8 as absent from the spec. Each claim passed
  through an automatic transcript and then through a reading of it, and
  **three of the eleven unresolved readings in §4 land directly on A2's
  mechanics** — if the placement-type list turns out to be ordered with
  order expressing preference, the distance to R5 narrows sharply.
  **T-03 tests all four against the primary sources before T-01 emits
  anything that depends on them.** None of the four is an edit to apply;
  the first question is whether there is anything to decide at all.
- **On A2 the intent is now settled, and it points at our own drafting.**
  Nicolás's written comment on the WG doc — the one cited around A2 in
  the call — argues the **opposite** of A2: it defends letting the device
  choose at spec level and calls "the APS sends one option" an
  *implementation* decision. He has since confirmed that R5 was written
  as a **superset** permitting both, and that the comment is the faithful
  statement of what `context/` should say. So the open question is no
  longer what R5 means but **whether its text says it** — a WG reader has
  only the words, and those words read as prescriptive; this project's own
  extract read them that way too. **T-04** owns making the
  permissiveness legible; it does not wait for T-03. The comment is
  reproduced verbatim in §A2 of the extract.
- **The remedy splits in two, and the split is deliberate.** **T-04**
  clarifies what is already written and adds no artefact; **T-05** adds
  what is missing — the explicit permission, and/or the use case that
  demonstrates it. Both blocks carry the boundary, so an audit finding
  that something is *missing* rather than *unclear* moves to T-05 instead
  of growing T-04.
- **On one item this project has something to contribute**: O5 — pause
  ads have no manifest-level definition on the SVTA side yet, while our
  spec already models a Publisher-declared pause window (UC-05, R16,
  R21, R25). That item is an opportunity to contribute rather than a
  change to absorb.

## Scope

- **Round 2 = the SVTA Advertising WG call of 2026-08-19.** Extract
  what was agreed and proposed about the spec, compare it against
  `context/`, and emit one task per proposed change or addition.
- Each generated task carries the minimum needed to be discussed on its
  own: what is proposed, who proposed it, which `context/` file it
  touches, and what has to be decided.
- Deciding and applying those changes happens **task by task**, after
  this phase's T-01 produces them.

## Out of scope

- **Editing `context/`.** This phase plans the spec change; it does not
  make it. Every `context/` edit lands as its own task, after its own
  decision.
- **Executing T-01.** The comparison runs when Nicolás says so.
- **The HLS half of the work** (A13). It is David's to author; this
  project tracks the DASH side and the naming constraint the HLS side
  imposes.
- **Items the WG explicitly deferred or excluded**: slice/tile
  single-decoder replacement (A5, next edition), SIMID (A12), SSAI
  inside an SGAI break (A11). These become out-of-scope statements in
  the spec, not features.
- **Non-spec WG threads**: MoQ ad signalling, the Common Ad Interface,
  contextual ads, the skippable-ads document, the university course.

## Stakeholders

- **Chair and principal proposer**: David Hassoun (SVTA Ads WG).
  Authored the document the call walked through; owns the mock samples
  and the HLS mapping.
- **Decision owner**: Nicolás Levy (Qualabs) — decides each proposed
  change against the committed spec, and owns the two conflicts (A2 vs
  R5, A7 vs R17).
- **Contributors in the call**: Yasser Syed (proposed the
  APS-selects-the-layout alternative, asked for the tile breadcrumb,
  raised the mixed-break and frame-accuracy questions), Rob Walch
  (Apple — HLS constraints and namespace, the dismissal-as-engagement
  observation), Frédéric Plissonneau (InterDigital), Martin Gold
  (YouView).
- **External follow-ups named in the call**: Zach Kava (pause-ad
  practice, and the A7 confirmation), the IAB (the single-VAST
  constraint behind A3).
- **Venue**: SVTA Advertising WG, nominally every two weeks, in
  practice every other meeting.

## Risks and mitigations

- **Reading agreement into the transcript where there was none.** An
  automatic transcript of a six-person call mangles names and technical
  terms, and several points are closed on silence rather than on an
  explicit round of assent — a rule the chair stated openly at the time.
  *Mitigation*: the extract splits agreed / open / mentioned, attributes
  every item, quotes verbatim where the reading matters, and carries a
  dedicated section (§4) of eleven readings it does **not** resolve.
  T-01 is required to preserve that classification rather than flatten
  it.
- **The extract's own conflict claims being wrong.** The four
  break-against-spec claims are a *reading*, two interpretation layers
  removed from the room, and the extract is the phase's foundation —
  a wrong claim here propagates into every task T-01 emits.
  *Mitigation*: **T-03**, which verifies each pair against the
  transcript and the literal spec text rather than against the extract,
  may return `compatible` or `indeterminate` as readily as
  `contradiction`, and writes any correction back into the extract. It
  gates T-01 on the affected items.
- **A2 silently demolishing R5 and UC-09.** A2 is not a local edit: R5,
  R5.1–R5.7, the APS's "produce candidates with renderable presentation
  options" responsibility in `02-actors.md`, and the whole of UC-09
  rest on the model it contradicts. Applying it piecemeal would leave
  the spec self-contradictory. *Mitigation*: **T-03 establishes
  first whether the contradiction is real** — the layer question (R5
  governs the resolution document, A2 the ad request) may dissolve it
  entirely; if it survives, its task must enumerate every dependent
  construct before any edit, and no dependent task may be executed
  before it is decided.
- **Task explosion diluting the decisions that matter.** Nineteen
  candidate items, of which two are structural and several are
  one-line out-of-scope statements. *Mitigation*: T-01 marks each
  generated task with its weight, and the trivial ones are grouped for
  a single pass rather than iterated individually.
- **The deadline is unknown** (§4.1: "buy the RENS meeting"). If it is
  the next MPEG meeting, the window may be short. *Mitigation*: it is
  the first thing to confirm with David; T-02 carries it, and T-03 hands
  it any further questions its `indeterminate` verdicts raise.
- **Fixing the wording of R5 while silently changing what it permits.**
  T-04 is a drafting task operating on a normative requirement, which is
  exactly where a "clarification" can quietly become a semantic change.
  *Mitigation*: T-04 is constrained to leave conformance unchanged in
  both directions, and instructed to **stop and report** if the work
  turns out to need a semantic change — which would mean the intent and
  the current design genuinely differ, a finding rather than an edit.
- **A second use case reading as a second *mode* of the spec.** If T-05
  adds the APS-decides example, UC-09 and the new case could be read as
  two modes to choose between rather than two implementations of one
  rule — which would deepen the misunderstanding this phase is trying to
  undo, since there is no mode to declare. *Mitigation*: T-05 must edit
  **both** cases to say they exercise R5 differently with neither being
  canonical, and is forbidden from introducing any name, label or
  attribute that could be read as selecting between them (DP-1.1).
- **Requirement / use-case numbering collision.** Phases
  `03-custom-layout` and `04-multiview` have proposed **R29** and **R30**
  and both claim "next free UC number", neither having executed, while
  the highest landed requirement is R28. *Mitigation*: T-05 must read
  both phases before taking a number and raise a collision rather than
  quietly taking it.
- *Accepted*: the WG's terminology ("concurrent") diverging from ours
  ("overlay" / "non-linear") costs some translation friction until O6
  is settled. Not blocking.

## Resource

- **Nicolás's comment of 2026-08-18 on the WG document**, under its
  "Capabilities detection" section — the authoritative statement of R5's
  intended flexibility, and the source that has to be read against what
  the call was reported to have concluded from it. It is reproduced
  verbatim in §A2 of the extract, along with the surrounding doc body:
  the two branches for capability detection (device-level versus an APS
  lookup), the privacy objection to the second, and the request to verify
  the decoder-detection APIs.
- [`svta-wg-2026-08-19-agreements.md`](svta-wg-2026-08-19-agreements.md)
  — the agreements extract (English, matching the rest of `.project/`
  and the WG-facing material). What was agreed (A1–A15), what was
  proposed and left open (O1–O7), what was mentioned without conclusion,
  and what the transcript does not support with confidence (§4). Every
  item is attributed and timestamped against the transcript.

  This is **phase material, not task evidence**: it is the *input* to
  T-01, not its output. T-01's output is the generated tasks
  themselves. Phase 02 put its cross-reference report at the phase root
  as the phase resource for the same reason — it is the document the
  phase's tasks are derived from — and this follows that precedent.

## Recommendation for next phase

This phase closes when every task T-01 generates has been decided and,
where a decision requires it, applied to `context/`. The likely
successor is not another feedback round but the **mock-samples**
work — A15, David's next step, where the placement-type declaration
(O1), the skip semantics (O2) and the mixed-break signalling (O3) stop
being prose and become concrete MPDs and HLS playlists. That is also
where the spec meets a second implementation, so it is the natural
place to discover which of the decisions taken here do not survive
contact with syntax.

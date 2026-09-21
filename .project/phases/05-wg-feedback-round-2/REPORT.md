# Phase 05 — Working-group feedback round 2 — Closure report

**Phase:** `05-wg-feedback-round-2`
**Status:** closed (2026-09-21)
**Source processed:** SVTA Advertising WG call of 2026-08-19

## 1. Summary

This phase turned a group discussion into decided text. Unlike round 1,
where one reviewer marked up files, the input here was a call in which
David Hassoun walked the group through every concern collected about the
non-linear work: 15 agreements, 7 open proposals, and a set of items
mentioned without conclusion.

The phase did not run the way it was specified, and the reason is worth
recording rather than hiding. T-01 was written to emit one task per
proposed change **so that the changes could then be decided one at a
time**. Nicolás was available throughout, so each item was put to him,
decided, and applied in the same pass. Writing the list first and
executing it afterwards would have been a step that bought nothing — the
list exists to let work proceed without him, and he was there. T-06 to
T-13 are therefore recorded after the fact, each against the commit that
landed it.

Twelve of the thirteen tasks are done. The thirteenth is closed
unresolved, deliberately, and section 4 says what that costs.

## 2. What the phase established before changing anything

T-03 verified the four places where the agreements extract claimed the
WG's position broke against the committed spec. The extract is a reading
of an automatic transcript, and the rest of the phase was built on it, so
the claims were checked against the transcript and the literal spec text
rather than against the extract:

| Claim | Verdict |
| --- | --- |
| A2 vs R5 | `spec-does-not-express-its-intent` — a drafting problem, not a conflict |
| A6 vs R22 | `contradiction`, but it lands on UC-04 and not on R22 |
| A7 vs R17 | `contradiction` |
| A8 vs the Player-dismiss vocabulary | `compatible` — it is an addition |

Two of the four claims were wrong as stated, and one pointed at the wrong
requirement. Corrections were written back into the extract. This is the
reason the verification gated the rest: three of the eight changes that
followed would have been made against a misreading.

## 3. What landed in `context/`

- **R5 reads as what it always meant** — several presentation options are
  the form, exactly one admissible is tolerated (T-04, T-08).
- **An APS may return exactly one option**, stated explicitly, with UC-13
  as the paired use case (T-05).
- **R29** — the Player declares its capabilities in the resolution
  request. Rewritten mid-phase to state a property instead of enumerating
  a list, and bound to the device classes of R3 (T-07, T-09).
- **The APS may omit options** from what the ADS returned, preserving
  order (T-10).
- **R30 + ADR 0005** — an unfilled opportunity is a resolution document
  with no candidates, which is not an error (T-12).
- **Two out-of-scope declarations**: interactive ad frameworks, and
  single-decoder slice/tile replacement (T-11).
- **The `<Error>` mapping row** stops describing what the APS does
  internally (T-13).
- **Numbering across phases**: a number is taken at execution and never
  held by a proposal (T-06). This came out of a collision — phases 03 and
  04, unexecuted, had reserved R29 and R30, which T-05 and T-07 then
  needed.

## 4. What closes unresolved, and what it costs

**T-02 — the eleven ambiguous transcript readings — closes without being
settled.** Four of the eleven were handed over for the sync with David
before the 21st; the call of 2026-09-21 happened and covered the Apple
demo, not the specification. The readings were not discussed.

Closed on Nicolás's instruction of 2026-09-21: *"ya que lo que queda sólo
depende de David, dalo por cerrado"*. The phase had been waiting on an
external party since August, and a phase that stays open waiting is a
phase that stops being read.

**What this costs, stated plainly:** five of the eleven readings change
what was built. They are not resolved by closing this phase — they are
released from it. Three items are the concrete residue:

1. Whether the APIs for detecting concurrent decode capability actually
   exist. David asked for help verifying this; it is recorded as
   unverified.
2. The deadline. The transcript says "the RENS meeting", probably the
   MPEG meeting in Rennes, and the date was never obtained.
3. The eleven readings themselves, each with its verbatim citation, in
   the agreements extract.

Whoever reopens any of these starts from
[`svta-wg-2026-08-19-agreements.md`](svta-wg-2026-08-19-agreements.md) §4,
which holds the citations. Nothing in `context/` depends on an unverified
reading: the three that would have are the ones T-03 checked first.

## 5. One decision of this phase that outlived it

The dismissal of a non-linear ad by the viewer was agreed at the
2026-08-19 call and, at the close of this phase, still exists nowhere in
`context/` — not as a requirement and not as an open question. It was
found on 2026-09-18 while auditing the open-questions register, by
searching for the term rather than by reading the phase.

Nicolás settled its shape on 2026-09-21: **the dismissal is of the whole
ad slot and never of an individual ad inside it**, because dismissing ads
one at a time is a bad experience. Writing it is carried outside this
phase, with the rest of the open-questions work.

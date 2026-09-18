[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Consumed `context/03-requirements.md` (mtime 2026-09-17 15:46) and `context/04-use-cases.md` (mtime 2026-09-17 11:49).
14 use cases (UC-01..UC-14) × 34 requirements (R1..R34). A cell is `A` only where the UC references the requirement explicitly or its scenario directly exercises the requirement's obligation; everything else is `·`.
Coverage: 25 of 34 Rs covered by at least one UC, 5 governance (R8, R9, R11, R18, R23), 4 orphan (R24, R32, R33, R34).

## Matrix 1 — UC × R

| UC | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15 | R16 | R17 | R18 | R19 | R20 | R21 | R22 | R23 | R24 | R25 | R26 | R27 | R28 | R29 | R30 | R31 | R32 | R33 | R34 | Σ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UC-01 | · | A | A | A | A | · | A | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 7 |
| UC-02 | · | A | A | A | A | · | A | · | · | · | · | A | A | · | A | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 9 |
| UC-03 | · | A | A | A | A | · | A | · | · | A | · | A | A | · | A | · | · | · | A | · | · | · | · | · | · | A | A | · | · | · | · | · | · | · | 12 |
| UC-04 | · | A | A | A | A | · | A | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | · | 8 |
| UC-05 | · | A | A | A | A | · | A | · | · | · | · | A | · | · | A | A | · | · | · | · | A | · | · | · | A | · | · | · | · | · | A | · | · | · | 11 |
| UC-06 | · | A | A | A | · | · | A | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 5 |
| UC-07 | A | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 2 |
| UC-08 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | A | A | A | · | · | · | A | A | · | · | · | · | · | · | · | · | A | · | · | · | 11 |
| UC-09 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | A | A | · | A | · | · | · | · | · | 9 |
| UC-10 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · | · | · | · | · | 8 |
| UC-11 | A | A | A | · | · | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | 6 |
| UC-12 | · | A | A | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | A | · | · | · | · | 5 |
| UC-13 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | A | A | · | A | · | · | · | · | · | 9 |
| UC-14 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | · | 7 |

## Matrix 2 — R × UC

| R | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 | 11 | 12 | 13 | 14 | Σ | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | · | · | · | · | · | · | A | · | · | · | A | · | · | · | 2 | (covered) |
| R2 | A | A | A | A | A | A | · | A | A | A | A | A | A | A | 13 | (covered) |
| R3 | A | A | A | A | A | A | A | A | A | A | A | A | A | A | 14 | (covered) |
| R4 | A | A | A | A | A | A | · | A | A | A | · | · | A | A | 11 | (covered) |
| R5 | A | A | A | A | A | · | · | A | A | A | · | · | A | A | 10 | (covered) |
| R6 | · | · | · | · | · | · | · | · | · | · | A | · | · | · | 1 | (covered) |
| R7 | A | A | A | A | A | A | · | · | · | · | · | · | · | · | 6 | (covered) |
| R8 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R9 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R10 | · | · | A | · | · | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R11 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R12 | A | A | A | A | A | A | · | A | A | A | · | · | A | A | 11 | (covered) |
| R13 | · | A | A | · | · | · | · | · | · | · | A | · | · | · | 3 | (covered) |
| R14 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | 1 | (covered) |
| R15 | A | A | A | A | A | · | · | A | A | A | · | · | A | A | 10 | (covered) |
| R16 | · | · | · | · | A | · | · | A | · | · | · | · | · | · | 2 | (covered) |
| R17 | · | · | · | · | · | · | · | A | · | · | · | · | · | · | 1 | (covered) |
| R18 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R19 | · | A | A | · | · | · | · | · | · | · | · | · | · | · | 2 | (covered) |
| R20 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | 1 | (covered) |
| R21 | · | · | · | · | A | · | · | A | · | · | · | · | · | · | 2 | (covered) |
| R22 | · | · | · | · | · | · | · | A | · | · | · | · | · | · | 1 | (covered) |
| R23 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (governance) |
| R24 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R25 | · | · | · | · | A | · | · | · | · | · | · | · | · | · | 1 | (covered) |
| R26 | · | · | A | · | · | · | · | · | A | A | · | · | A | · | 4 | (covered) |
| R27 | · | · | A | A | · | · | · | · | A | A | · | · | A | · | 5 | (covered) |
| R28 | · | · | · | · | · | · | · | · | · | · | A | · | · | A | 2 | (covered) |
| R29 | · | · | · | · | · | · | · | · | A | · | · | · | A | · | 2 | (covered) |
| R30 | · | · | · | · | · | · | · | · | · | · | · | A | · | · | 1 | (covered) |
| R31 | · | · | · | · | A | · | · | A | · | · | · | · | · | · | 2 | (covered) |
| R32 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R33 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |
| R34 | · | · | · | · | · | · | · | · | · | · | · | · | · | · | 0 | (orphan) |

## Notes

### Orphan Rs

Four requirements have no UC coverage and are not governance: **R24, R32,
R33, R34**. They do not share a disposition.

- **R32 — Exhausted pause-ad candidates while the viewer is still paused.**
  A real gap. UC-05 covers the window, the option walk and the dismissal on
  resume, and stops there; the three declared behaviours (repeat /
  request-again / stop) are exercised by nothing. Minimal UC: *"Pause
  outlasts the pause-ad candidates"* — candidates are consumed while the
  pause continues, and the UC states the Player's action under each of the
  three APS-declared behaviours, the constraint on a second resolution
  document under `request-again` (R32.2), and the behaviour on resume
  (R32.3). The policy does not vary by rendering capability, so D1–D5
  collapse to one row.

- **R34 — A pause opportunity window may be declared once-per-session.**
  A real gap, and the cheapest to close. Minimal UC: the viewer pauses
  **twice** inside the same window — the first pause yields an ad, the
  second yields none (R34.2) — plus the case that distinguishes R34.3: a
  first pause that resolved to no ad leaves the window unconsumed
  (device-agnostic).
- **R24 — Non-AV creative asset carrier (RFC 4337 avoidance).** Probably
  not a UC gap: R24.1 binds the APS and the spec document to a carrier
  choice, and a Player cannot observe which carrier delivered a URL it
  resolved successfully. Recommended disposition: **reclassify as
  governance**. A UC naming the admissible carrier would also push a HOW
  decision into `context/`.
- **R33 — Pause-ad delivery measured with the base play-list metric.**
  Split. R33.1 / R33.3 are document-level and belong with governance. R33.4
  is a **Publisher authoring obligation** (content carrying pause windows
  MUST request the `PlayList` metric via `Metrics`) — the same kind as R31,
  and UC-expressible: add it to the Publisher intent of the pause UCs
  (UC-05 and the new R32 UC).

**Near-orphan worth the same attention: R14.** Its only coverage is UC-12,
and there it is a pointer — *"R20 selects which window is served; R14
sequences the forms within the chosen window"*. No UC plays two non-linear
candidates back to back, which is R14's obligation; the linear break R14
names as the model is UC-06, which is linear-only and does not exercise it
either. Minimal fix: two non-linear candidates in document order in UC-03's
ad response, the first ending before the second begins, bounded by R4 and
held to one active form by R22.

### UCs with thin coverage

**UC-07 (2 Rs: R1, R3)** is the only UC below three, and part of that is
correct by construction: the scenario withdraws the ADS and the APS (*"Ad
response: not exercised in this scenario"*), so the selection and
presentation set (R5, R7, R15, R26, R27) genuinely does not apply.

Three Rs are exercised by the existing prose without being invoked in it:
- **R2** — the UC's central move is that the Publisher's declaration stands
  while the ADS/APS chain is never entered. Stating that against R2.1 /
  R2.2 makes the actor boundary explicit instead of implied by an absence.
- **R12** — the VOD fallback is *"a standard linear break"*, an ad type
  from R12's closed set expressed with baseline constructs.
- **R28** — UC-11 carries the pointer one way (*"a legacy Player renders
  the ad but does not activate the click … connecting to UC-07"*); UC-07
  carries no reverse pointer, so the inert-click outcome is stated only on
  the other side.

Nothing else is thin: the next lowest are UC-06 and UC-12 at 5 Rs, both
narrow by design (a linear sequence; window selection without rendering).

### Bidirectional sanity check

**No mismatches** — a property of how the views were produced, not evidence
about the cells: Matrix 1 is the single source of truth and Matrix 2 is its
computed transpose, so divergence is structurally impossible. Calling it
agreement between two independent views would be false.

What was verified is the transpose. The generator rebuilds each Matrix 1
row from Matrix 2's columns and compares it against the source, run once
with a deliberately dropped cell (`R4 × UC-06`) and once on the real data:

```
$ CHECKONLY=1 INJECT_MISMATCH=1 python3 gen.py
MISMATCHES: [('UC-06', [4])]   exit=1
$ CHECKONLY=1 python3 gen.py
MISMATCHES: none               exit=0
```

The check goes red when the data is broken, so its green means the
transpose is faithful. It says nothing about whether any individual `A` is
the right call — that judgement is the per-UC reading above, and is what a
reviewer should audit.

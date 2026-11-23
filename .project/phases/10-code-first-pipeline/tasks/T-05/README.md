# T-05: the use cases as executable vectors (part A)

ADR 0064. Part A: the format (`spec-source/scenarios/schema.json`), the
check (`bin/check-scenarios.py`, tests `bin/test_check_scenarios.py`), two
vectors (`UC-01.yaml` on Annex A, `UC-03.yaml` on Annex C) and the brief for
part B (`spec-source/scenarios/README.md`).

## State

`check-scenarios.py` exits 1: the 20 UCs without a vector (UC-02, UC-04 to
UC-22), and nothing else. UC-01 and UC-03 have no finding; every class of
both is `NOT_VERIFIABLE — no executor`. With context/04 cut down to UC-01 and
UC-03 the check exits 0 (test `test_two_vectors_alone_exit_0`).

## Choices part B inherits

- **Times on the session clock**, not the presentation timeline the task
  named: a linear insertion and a pause both stop the main presentation's
  timeline while the screen changes, so it cannot order what is observed.
  Each `primary` element carries `from`, its main presentation time, so that
  timeline is still recoverable.
- **The classes a UC states** are its `#### Dk` headings plus the non-"—"
  cells of its Coverage row: 12 UCs have no `#### Dk` headings at all
  (UC-07, UC-11, UC-12, UC-14 to UC-22). That gives UC-19 only D1 and UC-20
  D1, D3, D4, D5. `legacy` is required on UC-14, UC-17, UC-22 (a
  `**Legacy Player**` entry).
- **R3.1 and R12.2 are read from context/03** at run time, not copied into
  the check: a capability or layout that context/03 stops admitting fails the
  vector.
- **Fixture green** means no FAIL in the levels 1 and 2 run whose subject is
  that file. The 6 FAILs of the source run today are on the subject
  `specification` (the v13 carriers), not on a fixture.

## Disagreements recorded, not resolved

- UC-01: context/04 D1 "the extra decoder … not exercised" against A.6 "the
  second decoder may pre-buffer ad 102". Not observable in the outcome.
- UC-03: context/04's double box has a still-image background element and
  needs an image surface for it (D2 has none); C.1 offers "the double box
  without background" and C.6 renders it on D2. The outcomes follow the annex.

## Findings out of scope

- `bin/spec-section.py` cannot split `context/04-use-cases.md` (exit 2:
  "section keys repeated: D1, D2, D3, D4, D5"), so `--file
  context/04-use-cases.md` does not work. `check-scenarios.py section UC-NN`
  prints one UC and its hash instead.

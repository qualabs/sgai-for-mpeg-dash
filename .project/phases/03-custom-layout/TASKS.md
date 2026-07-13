# Tasks — phase 03-custom-layout

All tasks are `pending` — the phase is in `planning` for Nicolás to
review before execution. No task touches `context/` until the phase is
reviewed and execution is authorised. The full design that these tasks
implement lives in [`T-01-PLAN.md`](T-01-PLAN.md).

| id   | brief                                                                                          | status  | plan          | evidence |
| ---- | ---------------------------------------------------------------------------------------------- | ------- | ------------- | -------- |
| T-01 | Write the phase design plan capturing all of Nicolás's custom-layout decisions                 | done    | T-01-PLAN.md  | T-01-PLAN.md |
| T-02 | Finalize + accept ADR 0002 (new custom-layout type + viewport-relative pixel coordinate model) | pending | —             | —        |
| T-03 | Draft the custom-layout requirement(s) as a standalone advanced-extension section in `context/03-requirements.md` (coordinate model, N-element model, primary-content reference, Z-order + overlap, Publisher-enables / ADS-APS-positions split, R5 / R3 degradation) | pending | —             | —        |
| T-04 | Write the custom-layout use-case(s) as a standalone advanced-extension section in `context/04-use-cases.md`, exercised across D1–D5 (next free UC number) | pending | —             | —        |
| T-05 | Add glossary entries to `context/99-glossary.md` (custom layout, reference viewport, element, Z-order) marked *(proposed)* | pending | —             | —        |
| T-06 | Cross-reference pass: ensure the new requirement binds to R2 (actor contract), R3 (decoder budget), R5 (ordered fallback), and states the R10 / ADR-0001 trade-off; verify the advanced-extension framing is explicit and self-contained | pending | —             | —        |
| T-07 | Reword R10 in `context/03-requirements.md` (and align ADR 0001 / ADR 0002) so R10's scope is explicitly the MANDATORY base spec: the base version of the spec has no layout system of its own (it defers spatial arrangement to HTML5 / CSS and the IAB CTV catalogue), and advanced on-top extensions (custom layout, multiview, and others) are explicitly OUT of R10's scope, not governed by it | pending | —             | —        |

## Notes

- **T-02** — ADR 0002 is drafted in `.project/decisions/` in
  `status: proposed` so Nicolás can review the decision as recorded.
  Accepting it (flip to `accepted`) is part of executing this task,
  after review.
- **T-03 / T-04** — the requirement and the use-cases MUST be
  self-contained advanced-extension sections, explicitly marked as
  opt-in / advanced, and kept separate from the core requirements and
  core use-cases. This is the transversal framing constraint for the
  phase.
- Requirement / use-case numbers are assigned at execution time from the
  next free stable identifiers (per the numbering convention in
  `context/03-requirements.md`). The plan proposes R29 for the
  custom-layout requirement and the next free UC number for the
  use-case, but the final numbers are fixed when the text lands.

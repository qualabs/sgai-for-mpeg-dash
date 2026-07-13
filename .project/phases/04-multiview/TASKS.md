# Tasks — phase 04-multiview

All tasks are `pending` — the phase is in `planning` for Nicolás to
review before execution. No task touches `context/` until the phase is
reviewed and execution is authorised. The full design (including the
proposed `multiview-*` layout set) lives in [`T-01-PLAN.md`](T-01-PLAN.md).

| id   | brief                                                                                          | status  | plan          | evidence |
| ---- | ---------------------------------------------------------------------------------------------- | ------- | ------------- | -------- |
| T-01 | Write the phase design plan capturing all of Nicolás's multiview decisions + enumerate the `multiview-*` fixed layout set from the WOXCON SCU41 reference image | done    | T-01-PLAN.md  | T-01-PLAN.md |
| T-02 | Finalize + accept ADR 0003 (decoder-vs-tiles agnosticism + fixed `multiview-*` collection + alternative-content non-ad scope) | pending | —             | —        |
| T-03 | Draft the multiview requirement(s) as a standalone advanced-extension section in `context/03-requirements.md` (fixed `multiview-*` collection 2–4 videos, implementation-agnostic capability, alternative-content non-ad scope, live-content possibility, default-audio / audio-selection posture) | pending | —             | —        |
| T-04 | Extend R3 to express two-or-more concurrent decoders as a device capability and to signal the tiles single-decoder path | pending | —             | —        |
| T-05 | Write the multiview use-case(s) as a standalone advanced-extension section in `context/04-use-cases.md`, exercised across device classes (next free UC number) | pending | —             | —        |
| T-06 | Investigate the open point: does `ImportedMPD` allow live content, and if not what carries the N live views (independent-video source vs HEVC tiles)? Record the finding to inform the design phase | pending | —             | —        |
| T-07 | Add glossary entries to `context/99-glossary.md` (multiview, `multiview-*` layout, tiles / HEVC tiles, view) marked *(proposed)* | pending | —             | —        |
| T-08 | Cross-reference + coherence pass: R3 extension coherent with D1–D5 and R22 / R26 / R27 decoder reasoning; verify the advanced-extension framing is explicit and self-contained; validate the `multiview-*` set with Nicolás against the reference image | pending | —             | —        |

## Notes

- **T-02** — ADR 0003 is drafted in `.project/decisions/` in
  `status: proposed` so Nicolás can review the decision as recorded.
  Accepting it (flip to `accepted`) is part of executing this task,
  after review.
- **T-03 / T-05** — requirement and use-cases MUST be self-contained
  advanced-extension sections, explicitly marked opt-in / advanced, kept
  separate from the core requirements and core use-cases.
- **T-06** — open research point flagged by Nicolás. It informs the
  design phase but does NOT block the requirement text, which is
  deliberately implementation-agnostic (it describes the multiview
  capability, not the carrier).
- **T-08** — the `multiview-*` layout set in `T-01-PLAN.md` is proposed
  from the WOXCON SCU41 reference image and needs Nicolás's validation
  against that image before the use-cases lock the named presets.
- Requirement / use-case numbers are assigned at execution time from the
  next free stable identifiers. The plan proposes R30 for the multiview
  requirement and the next free UC number; final numbers fixed when the
  text lands. R3 is extended in place (its number does not change).

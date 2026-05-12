[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Generated from [`../spec/03-requirements.md`](../spec/03-requirements.md)
(R1..R10) and [`../spec/04-use-cases.md`](../spec/04-use-cases.md)
(UC-01..UC-07, device classes D1..D5).
Inputs consumed: 03-requirements.md (2026-05-11 19:58),
04-use-cases.md (2026-05-11 19:43). 7 UCs × 10 Rs.

## Matrix 1 — UC × R

Cell legend: **A** — the UC exercises the R (its prose, scenario, or
expected behaviour invokes the R explicitly or directly tests its
obligation). **·** — not applicable / not exercised in this UC.

| UC    | Scenario                              | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 |
|-------|---------------------------------------|----|----|----|----|----|----|----|----|----|-----|
| UC-01 | Slot at start of session (pre-roll)   | A  | A  | A  | A  | A  | ·  | ·  | ·  | ·  | ·   |
| UC-02 | Mid-content slot (mid-roll)           | A  | A  | A  | A  | A  | ·  | ·  | ·  | ·  | ·   |
| UC-03 | Coexisting overlay                    | A  | A  | A  | A  | A  | ·  | A  | ·  | ·  | A   |
| UC-04 | Hybrid linear + concurrent overlay    | A  | A  | A  | A  | A  | ·  | A  | ·  | ·  | A   |
| UC-05 | Pause-triggered ad                    | A  | A  | A  | A  | A  | ·  | ·  | ·  | ·  | A   |
| UC-06 | Multi-ad break                        | A  | A  | A  | A  | A  | ·  | A  | ·  | ·  | ·   |
| UC-07 | Legacy Player encounters new construct| A  | A  | ·  | ·  | ·  | ·  | ·  | ·  | ·  | ·   |

## Matrix 2 — R × UC

Cell legend: **A** — the UC in this column exercises the R in this
row. **·** — not exercised. Tag column: **(covered)** if at least one
UC exercises the R; **(orphan)** if no UC exercises the R and the R
is a runtime obligation; **(governance)** if the R is document-level
and not runtime-testable via UCs.

| R    | Topic                                                | UC-01 | UC-02 | UC-03 | UC-04 | UC-05 | UC-06 | UC-07 | Tag           |
|------|------------------------------------------------------|-------|-------|-------|-------|-------|-------|-------|---------------|
| R1   | DASH 6th compliance and graceful degradation         | A     | A     | A     | A     | A     | A     | A     | (covered)     |
| R2   | Honour the three-actor model                         | A     | A     | A     | A     | A     | A     | A     | (covered)     |
| R3   | Device-capability diversity (D1..D5)                 | A     | A     | A     | A     | A     | A     | ·     | (covered)     |
| R4   | Broadcaster-declared max slot duration, Player-enforced | A | A     | A     | A     | A     | A     | ·     | (covered)     |
| R5   | Device-aware ad selection (multi-form, Player picks) | A     | A     | A     | A     | A     | A     | ·     | (covered)     |
| R6   | Ad tracking carrier                                  | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (orphan)      |
| R7   | Respect ADS-returned order                           | ·     | ·     | A     | A     | ·     | A     | ·     | (covered)     |
| R8   | Justify any addition or omission                     | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance)  |
| R9   | Minimise net new constructs                          | ·     | ·     | ·     | ·     | ·     | ·     | ·     | (governance)  |
| R10  | Do not recreate a layout system                      | ·     | ·     | A     | A     | A     | ·     | ·     | (covered)     |

## Notes

### Orphan Rs

Runtime Rs (R1..R7) with no UC coverage at all. Each is a signal that
either (a) the UC list is incomplete, or (b) the R can be tested
exclusively via test cases derived from an analysis sidecar rather
than a UC.

- **R6 — Ad tracking carrier.** No UC in
  [`../spec/04-use-cases.md`](../spec/04-use-cases.md) describes
  tracking-beacon behaviour (impression, quartiles, complete, failure
  modes). The UCs focus on rendering and slot logic, leaving R6 to
  [`../spec/05-dash-linear-interfaces.md`](../spec/05-dash-linear-interfaces.md)
  (which shows the `urn:mpeg:dash:event:callback:2015` carrier in the
  reference ListMPD) and to
  [`../analysis/error-semantics.md`](error-semantics.md) (E10
  tracking-beacon failure). Proposed close: add **UC-08 — Tracking
  beacon delivery and failure** that walks an impression → start →
  quartiles → complete sequence across one happy path and one beacon
  HTTP failure, per device class (where overlay vs linear ads change
  which beacons fire). Alternative: leave R6 covered solely by the
  interface reference + error matrix and update R6's prose to declare
  that it is intentionally tested at the interface layer rather than
  at the UC layer.

### UCs with thin coverage

UCs that map to fewer than 3 Rs. Each is a candidate for tightening
the UC text so it invokes more Rs explicitly.

- **UC-01 (Slot at start of session) — 5 Rs.** Not thin. R1, R2, R3,
  R4, R5 are all exercised. The R7 ordering case does not apply
  because UC-01 is a single-ad slot; the multi-ad-ordering check
  surfaces in UC-06. R10 layout vocabulary does not apply because
  UC-01 is linear-only. Coverage adequate.
- **UC-02 (Mid-content slot) — 5 Rs.** Same as UC-01. Adequate.
- **UC-07 (Legacy Player encounters new constructs) — 2 Rs.** Thin
  by design: UC-07's whole point is graceful skip via R1 +
  three-actor non-violation (R2). Adding R3..R5 to UC-07 would
  conflate "legacy Player ignores construct" with "Player picks the
  best renderable form" — different obligations on different code
  paths. Suggest leaving UC-07 at R1+R2 and accepting it as
  intentionally narrow. Reviewers SHOULD flag if a future UC-07
  variant blurs this.

### Bidirectional sanity check

A mismatch occurs if an R is marked covered by N UCs in Matrix 2 but
the cells in Matrix 1 show `A` in M ≠ N different UCs for that same
R.

Walk-through:

| R    | Matrix 2 UC set (where `A`)              | Matrix 1 UC set (where `A` in this R column) | Match |
|------|-------------------------------------------|----------------------------------------------|-------|
| R1   | UC-01, UC-02, UC-03, UC-04, UC-05, UC-06, UC-07 | UC-01, UC-02, UC-03, UC-04, UC-05, UC-06, UC-07 | yes |
| R2   | UC-01, UC-02, UC-03, UC-04, UC-05, UC-06, UC-07 | UC-01, UC-02, UC-03, UC-04, UC-05, UC-06, UC-07 | yes |
| R3   | UC-01, UC-02, UC-03, UC-04, UC-05, UC-06 | UC-01, UC-02, UC-03, UC-04, UC-05, UC-06     | yes   |
| R4   | UC-01, UC-02, UC-03, UC-04, UC-05, UC-06 | UC-01, UC-02, UC-03, UC-04, UC-05, UC-06     | yes   |
| R5   | UC-01, UC-02, UC-03, UC-04, UC-05, UC-06 | UC-01, UC-02, UC-03, UC-04, UC-05, UC-06     | yes   |
| R6   | (none)                                    | (none)                                       | yes   |
| R7   | UC-03, UC-04, UC-06                       | UC-03, UC-04, UC-06                          | yes   |
| R8   | (governance — no UC cells)                | (none)                                       | yes   |
| R9   | (governance — no UC cells)                | (none)                                       | yes   |
| R10  | UC-03, UC-04, UC-05                       | UC-03, UC-04, UC-05                          | yes   |

No mismatches.

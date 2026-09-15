[GROUNDED_BY=spec-only]

# UC × R coverage matrix

Consumed `../context/03-requirements.md` (mtime 2026-09-15 19:16:04 -03) and
`../context/04-use-cases.md` (mtime 2026-09-15 17:41:41 -03). **13 use cases**
(UC-01..UC-13) × **30 requirements** (R1..R30; numbering is non-contiguous by
section but the set is complete).

A cell is `A` when the UC text names the requirement (or one of its `RN.M`
criteria) **or** its scenario / expected behaviour performs the obligation the
requirement states; `·` otherwise. Naming a requirement is not required for `A`
— R7 is never cited by number yet six UCs walk candidates "in document order",
which is R7.1 verbatim.

## Matrix 1 — UC × R

| UC | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 | R9 | R10 | R11 | R12 | R13 | R14 | R15 | R16 | R17 | R18 | R19 | R20 | R21 | R22 | R23 | R24 | R25 | R26 | R27 | R28 | R29 | R30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UC-01 | · | · | A | A | A | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · |
| UC-02 | · | · | A | A | A | · | A | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · |
| UC-03 | · | · | A | A | A | · | A | · | · | A | · | A | A | · | A | · | · | · | A | · | · | · | · | · | · | A | A | · | · | · |
| UC-04 | · | A | A | A | A | · | A | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · | · |
| UC-05 | · | A | A | A | A | · | A | · | · | A | · | · | · | · | A | A | · | · | · | · | A | · | · | · | A | · | · | · | · | · |
| UC-06 | · | A | A | A | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · |
| UC-07 | A | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · | · |
| UC-08 | · | · | A | A | A | · | · | · | · | A | · | · | · | · | · | A | A | · | · | · | A | A | · | · | · | · | · | · | · | · |
| UC-09 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | · | A | · |
| UC-10 | · | · | A | A | A | · | · | · | · | · | · | A | · | · | A | · | · | · | · | · | · | · | · | · | · | A | A | · | · | · |
| UC-11 | A | · | A | · | · | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | · | A | · | · |
| UC-12 | · | · | A | · | · | · | · | · | · | · | · | · | · | A | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | A |
| UC-13 | · | A | A | A | A | · | · | · | · | · | · | A | · | · | · | · | · | · | · | · | · | · | · | · | · | A | A | · | A | · |

## Matrix 2 — R × UC

| R | UC-01 | UC-02 | UC-03 | UC-04 | UC-05 | UC-06 | UC-07 | UC-08 | UC-09 | UC-10 | UC-11 | UC-12 | UC-13 | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | · | · | · | · | · | · | A | · | · | · | A | · | · | (covered) |
| R2 | · | · | · | A | A | A | · | · | A | · | · | · | A | (covered) |
| R3 | A | A | A | A | A | A | A | A | A | A | A | A | A | (covered) |
| R4 | A | A | A | A | A | A | · | A | A | A | · | · | A | (covered) |
| R5 | A | A | A | A | A | · | · | A | A | A | · | · | A | (covered) |
| R6 | · | · | · | · | · | · | · | · | · | · | A | · | · | (covered) |
| R7 | A | A | A | A | A | A | · | · | · | · | · | · | · | (covered) |
| R8 | · | · | · | · | · | · | · | · | · | · | · | · | · | (governance) |
| R9 | · | · | · | · | · | · | · | · | · | · | · | · | · | (governance) |
| R10 | · | · | A | · | A | · | · | A | · | · | · | · | · | (covered) |
| R11 | · | · | · | · | · | · | · | · | · | · | · | · | · | (orphan) |
| R12 | · | · | A | A | · | · | · | · | A | A | · | · | A | (covered) |
| R13 | · | A | A | · | · | · | · | · | · | · | A | · | · | (covered) |
| R14 | · | · | · | · | · | · | · | · | · | · | · | A | · | (covered) |
| R15 | · | · | A | · | A | · | · | · | · | A | · | · | · | (covered) |
| R16 | · | · | · | · | A | · | · | A | · | · | · | · | · | (covered) |
| R17 | · | · | · | · | · | · | · | A | · | · | · | · | · | (covered) |
| R18 | · | · | · | · | · | · | · | · | · | · | · | · | · | (governance) |
| R19 | · | A | A | · | · | · | · | · | · | · | · | · | · | (covered) |
| R20 | · | · | · | · | · | · | · | · | · | · | · | A | · | (covered) |
| R21 | · | · | · | · | A | · | · | A | · | · | · | · | · | (covered) |
| R22 | · | · | · | · | · | · | · | A | · | · | · | · | · | (covered) |
| R23 | · | · | · | · | · | · | · | · | · | · | · | · | · | (governance) |
| R24 | · | · | · | · | · | · | · | · | · | · | · | · | · | (orphan) |
| R25 | · | · | · | · | A | · | · | · | · | · | · | · | · | (covered) |
| R26 | · | · | A | · | · | · | · | · | A | A | · | · | A | (covered) |
| R27 | · | · | A | A | · | · | · | · | A | A | · | · | A | (covered) |
| R28 | · | · | · | · | · | · | · | · | · | · | A | · | · | (covered) |
| R29 | · | · | · | · | · | · | · | · | A | · | · | · | A | (covered) |
| R30 | · | · | · | · | · | · | · | · | · | · | · | A | · | (covered) |

## Notes

### Orphan Rs

Two requirements carry a runtime actor obligation and no UC exercises it.
Neither is redundant with another R; both are gaps.

- **R11 — No dependency on VAST.** `VAST` appears zero times in
  `04-use-cases.md`; the ad response of every UC is described as "the ADS
  decided it and the APS presented it", never as a VAST document. That silence
  is consistent with R11 but does not exercise R11.2 ("a Player MUST be able to
  operate regardless of whether the ADS uses VAST"), because no scenario makes
  the ADS's decision format visible. **Minimal UC to close it**: a variant note
  on UC-01 or UC-03 stating that the same resolution document is produced from a
  non-VAST ADS decision and the Player's behaviour is bit-identical — the
  Player-facing contract starts at the resolution document. One paragraph, no
  new device-class table.
- **R24 — Non-AV creative asset carrier (RFC 4337 avoidance).** `mimeType`
  appears zero times in `04-use-cases.md`. UC-03, UC-05, UC-09, UC-10 and UC-13
  all render image and HTML creatives, so the situation R24 constrains occurs
  repeatedly, but no UC says how the asset URL travels. R24.1 binds the APS
  (a runtime actor emitting the resolution document), so it is not a
  document-only rule. **Minimal UC to close it**: extend UC-10's "Ad response"
  block by one bullet — the image ad and the image background element carry
  their URLs through a DR-6 carrier, not as `@mimeType` on an AdaptationSet —
  and the same statement covers the image / HTML options of UC-09 and UC-13 by
  reference.

Tagged `(governance)` instead, because every conformance criterion is
spec-document or bilateral-contract and a UC cannot exercise it: **R8**
(justify additions), **R9** (minimise new constructs), **R18** (APS-to-ADS API
out of scope), **R23** (application-level metadata carrier — the requirement
explicitly says what is checkable is "that the place exists and is named, not
that anyone used it").

**R10 is document-level but not orphaned**: UC-03/D1 cites it directly
("using HTML/CSS layout primitives (per R10)"), and UC-05/D3 and UC-08/D3
render through "the HTML/CSS layer". Tagged `(covered)`.

### UCs with thin coverage

| UC | Rs | Candidates to surface in the UC text |
|---|---|---|
| UC-07 — Legacy Player | 2 (R1, R3) | **R2.1** — the UC already has the Publisher authoring a standard linear break as the VOD fallback; naming it as a Publisher declaration ties the scenario to the actor contract. **R1.2** — the UC asserts new mechanisms are expressed "via MPEG-DASH 6th edition extension points"; R1.2 is the criterion that enumerates which ones, so the citation is free. **R12** — what the legacy Player ignores is one of the enumerated ad types. |

No other UC falls below three. The next lowest are UC-01, UC-06 and UC-12 at
four each, and in all three the narrow count is the scenario's actual shape
(a single linear slot; a linear pod; window selection with no rendering), not
under-specification.

Two requirements are covered by exactly one UC each and are worth watching even
though they are not orphans:

- **R14** (sequential non-linear forms in a slot) is reached only through
  UC-12's forward pointer ("the forms inside its resolution document are then
  sequenced per R14"). No UC shows the scenario R14 describes — a non-linear
  slot whose resolution document declares Overlay A → B → C played in order.
- **R22** (single active non-linear form) is exercised only by UC-08, and there
  only as a by-product of R17 suspending the overlay during a pause. No UC puts
  two non-linear forms in contention on their own.

### Bidirectional sanity check

The two matrices were rendered from one `R → {UC}` table and then re-parsed
independently from the rendered markdown above; for every R, the UC set read
back from Matrix 1's columns was compared against the UC set read back from
Matrix 2's rows. **0 mismatches across all 30 requirements.** The comparator
was validated by flipping a single cell in Matrix 1 (R5 / UC-04, `A` → `·`),
which made it report the mismatch and exit non-zero; the check can fail.

Totals agree from both directions: 84 `A` cells read row-wise out of Matrix 1
and 84 read row-wise out of Matrix 2, over 30 requirements × 13 use cases.

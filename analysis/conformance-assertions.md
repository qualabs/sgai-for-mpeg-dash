[GROUNDED_BY=spec-only]

# Conformance assertions extracted from spec/

Normalised RFC 2119 MUST / SHOULD / MAY sentences across every file
in [`../spec/`](../spec/). Assertions inside `Conformance criteria`
blocks of [`../spec/03-requirements.md`](../spec/03-requirements.md)
reuse their `R<N>.<n>` IDs verbatim. Sentences elsewhere in the spec
are given a file-prefixed sequential ID. Each row is actionable as a
chapter-10 test case.

## Assertion table

| Assertion ID | Source | Actor | Condition | Obligation |
|--------------|--------|-------|-----------|------------|
| R1.1  | spec/03-requirements.md:32  | Player          | Given an MPD containing an SGAI construct the Player does not implement | The Player MUST ignore the unknown construct and continue playing the primary content uninterrupted. |
| R1.2  | spec/03-requirements.md:36  | norm document   | Given a new SGAI construct introduced by this proposal | The construct MUST be expressed using a MPEG-DASH 6th edition extension point with defined ignore-if-unknown semantics. |
| R1.3  | spec/03-requirements.md:40  | norm document   | (unconditional) | The norm MUST NOT alter or override the semantics of any pre-existing MPEG-DASH 6th edition construct. |
| R2.1  | spec/03-requirements.md:50  | Broadcaster     | Given an ad slot (linear or non-linear) | Constraints applicable to that slot (max duration, opt-in policies, layout templates) MUST be declared by the Broadcaster in the MPD, not inferred at runtime. |
| R2.2  | spec/03-requirements.md:54  | ADS             | (unconditional) | The ADS MUST produce ad candidates as a resolution document; it MUST NOT be expected to enforce Broadcaster-declared constraints. |
| R2.3  | spec/03-requirements.md:57  | Player          | Given ADS-returned candidates | The Player MUST validate each candidate against Broadcaster-declared constraints and render only those that satisfy them. |
| R2.4  | spec/03-requirements.md:60  | norm document   | Given a new mechanism introduced by the norm | The mechanism MUST be expressible within the three-actor contract; any mechanism requiring an actor to take a responsibility outside its role MUST be rejected or redesigned. |
| R3.1  | spec/03-requirements.md:74  | norm document   | (unconditional) | The norm MUST enumerate supported device classes and, per class, the expected behaviour for each ad opportunity type covered by the use cases. |
| R3.2  | spec/03-requirements.md:77  | Player          | Given a supported device class and any ad opportunity type defined in the norm | The Player MUST produce a defined behaviour (render, fall back, or skip); undefined behaviour is non-conforming. |
| R3.3  | spec/03-requirements.md:81  | Player          | Given an ad form the device class cannot render | The Player MUST NOT attempt to render that form. |
| R4.1  | spec/03-requirements.md:101 | Broadcaster     | Given any ad slot (linear or non-linear) in the MPD | The Broadcaster MUST declare a maximum duration on that slot. |
| R4.2  | spec/03-requirements.md:105 | Player          | Given the cumulative duration of accepted ad candidates would exceed the cap | The Player MUST stop rendering at the cap boundary, even if the stop falls mid-ad. |
| R4.3  | spec/03-requirements.md:108 | Player          | (unconditional) | The Player MUST NOT extend a slot beyond the Broadcaster-declared cap regardless of ADS metadata or candidate count. |
| R4.4  | spec/03-requirements.md:111 | ADS             | (unconditional) | The ADS is NOT required to respect the cap when selecting candidates; a conformance check MUST NOT fail the ADS solely because cumulative candidate duration exceeds the cap. |
| R4.5  | spec/03-requirements.md:115 | Player          | Given a candidate's actual rendered length exceeds its declared duration | The Player MUST enforce the cap against actual length, not declared length ("trim during play"). |
| R5.1  | spec/03-requirements.md:136 | ADS             | (unconditional) | Each ad candidate returned by the ADS MUST carry one or more renderable forms; the ADS MAY rank them via ADS hints. |
| R5.2  | spec/03-requirements.md:139 | Player          | Given an accepted candidate with multiple renderable forms | The Player MUST choose the best form it can render on its device. |
| R5.3  | spec/03-requirements.md:142 | Player          | Given a candidate with no form renderable on the device | The Player MUST skip it, falling back to the next candidate or to primary content per the configured policy. |
| R5.4  | spec/03-requirements.md:145 | ADS             | (unconditional) | The ADS MUST NOT be required to maintain a device-class matrix or a per-Player capability view to produce candidates. |
| R6.1  | spec/03-requirements.md:164 | norm document   | (unconditional) | The norm MUST specify how in-band ad tracking beacons are carried in the resolution document. |
| R6.2  | spec/03-requirements.md:166 | Broadcaster / ADS | Given an ad MPD or sub-MPD | Implementations SHOULD carry tracking beacons as `<Event>` entries inside an `<EventStream>` of scheme `urn:mpeg:dash:event:callback:2015`. |
| R6.3  | spec/03-requirements.md:170 | norm document   | Given the callback scheme cannot express the required semantics | A new tracking carrier MAY be introduced, and only after a documented gap analysis per R9. |
| R6.4  | spec/03-requirements.md:174 | ADS / Broadcaster | Given application-level metadata with no native DASH carrier | The metadata MAY be conveyed via vendor-namespaced extension elements. |
| R6.5  | spec/03-requirements.md:178 | Player          | Given an unknown namespace on a tracking-related extension element | The Player MUST safely ignore that namespace, per the DASH extension rules invoked by R1. |
| R7.1  | spec/03-requirements.md:204 | Player          | Given an ADS resolution document with more than one candidate | The Player MUST play candidates in the order declared by the ADS, except for candidates dropped under R7.2 / R7.3. |
| R7.2  | spec/03-requirements.md:208 | Player          | Given a candidate with no form renderable on the device | The Player MAY drop the candidate. |
| R7.3  | spec/03-requirements.md:210 | Player          | Given a candidate whose declared duration would push cumulative slot duration past the cap | The Player MAY drop it before playback ("drop before play"). |
| R7.4  | spec/03-requirements.md:213 | Player          | After applying R7.2 / R7.3 to the candidate list | The Player MUST NOT re-order, deduplicate, or otherwise rearrange remaining candidates. |
| R7.5  | spec/03-requirements.md:216 | Player          | Given an accepted candidate whose actual rendered length exceeds the cap | The Player MUST trim mid-rendering ("trim during play") per R4. |
| R8.1  | spec/03-requirements.md:229 | norm document   | Given a new construct introduced by the proposal | Inline justification MUST accompany it stating why an existing MPEG-DASH construct could not be reused. |
| R8.2  | spec/03-requirements.md:233 | norm document   | Given a deliberate omission of an existing MPEG-DASH construct a reader might expect to see reused | The omission MUST be documented inline with the design decision. |
| R9.1  | spec/03-requirements.md:243 | norm document   | (unconditional) | The proposal MUST reuse existing MPEG-DASH machinery (events, manifests, presentations, schemes) wherever possible. |
| R9.2  | spec/03-requirements.md:246 | norm document   | (unconditional) | A new construct MUST NOT be introduced unless an existing one cannot be made to fit. |
| R9.3  | spec/03-requirements.md:248 | norm document   | Before introducing a new construct | The proposal MUST consider whether an extension to an existing construct would suffice, and document the outcome. |
| R10.1 | spec/03-requirements.md:260 | norm document   | (unconditional) | Spatial arrangement of overlays MUST be delegated to HTML5 / CSS layout primitives. |
| R10.2 | spec/03-requirements.md:262 | norm document   | (unconditional) | The norm MUST NOT define a parallel layout standard for overlay placement. |
| R10.3 | spec/03-requirements.md:264 | norm document   | (unconditional) | Position semantics inside a layout (left, right, top, bottom, etc.) are out of scope for the norm and MUST be expressed via the Positioning Templates section using HTML5 / CSS primitives. |
| UC04.1 | spec/04-use-cases.md:687 | Player | Given an unrecognized event type or construct in the manifest | The Player MUST skip the unknown construct and continue playing primary content as if the construct were not present (UC-07; redundant with R1.1, kept for cross-reference). |
| UC04.2 | spec/04-use-cases.md:705 | norm document | Given a new construct the proposal introduces | It MUST be expressible via extension points that produce the UC-07 outcome on legacy Players. |
| N06.1  | spec/06-naming-and-namespaces.md:27 | Player          | Given a Player implementing edition N+1 | The Player SHOULD recognise both `:N:` and `:N+1:` scheme URIs and treat them per the backward-compatibility rules in that edition's norm. |
| N06.2  | spec/06-naming-and-namespaces.md:47 | Player          | Given an unknown namespace under DASH's extension rules | The legacy Player MUST ignore that namespace. |
| N06.3  | spec/06-naming-and-namespaces.md:54 | norm document   | Given a construct whose semantics change across editions | It MUST use a new `<year>` suffix on its scheme URI. |
| N06.4  | spec/06-naming-and-namespaces.md:56 | norm document   | Given a construct whose semantics are unchanged across editions | It MAY keep its existing scheme URI. |
| N06.5  | spec/06-naming-and-namespaces.md:58 | norm document   | (unconditional) | Chapter 2 (Normative references) MUST list the URIs introduced by the current edition explicitly. |
| N06.6  | spec/06-naming-and-namespaces.md:65 | norm document   | Given a layout to reference at chapter level | The norm MUST reference enum-values from the canonical layout vocabulary in `99-glossary.md` without inventing new layout names at chapter level. |
| BC07.1 | spec/07-backward-compat-checklist.md:5  | norm document | (unconditional) | The norm MUST apply the per-construct backward-compatibility checklist for every new construct it introduces. |
| BC07.2 | spec/07-backward-compat-checklist.md:13 | norm document | Given chapters 4 (Conformance) and 10 (Test cases) | They MUST apply the verification procedure defined in this checklist. |
| BC07.3 | spec/07-backward-compat-checklist.md:17 | norm document | For each new construct C the norm introduces | The norm MUST answer the seven checklist questions (placement, extension rule, walk-through, sibling check, UC-07 test, namespace, doc cross-reference) in the construct's specification chapter. |
| BC07.4 | spec/07-backward-compat-checklist.md:19 | norm document | Given an unanswered checklist item | Publication of the construct chapter SHOULD be blocked. |
| BC07.5 | spec/07-backward-compat-checklist.md:43 | norm document | Given a new construct introduced by the norm | The construct MUST be in one of the extension namespaces declared in `06-naming-and-namespaces.md`. |
| BC07.6 | spec/07-backward-compat-checklist.md:58 | norm document | Given a construct's specification chapter | The legacy-Player walk-through MUST be present as an explicit prose paragraph, not implicit. |
| BC07.7 | spec/07-backward-compat-checklist.md:70 | norm document | Given a construct C is removed from a conforming document | The remaining document MUST still parse and play. |
| BC07.8 | spec/07-backward-compat-checklist.md:75 | norm document | Given a new construct C introduced by the norm | The norm MUST ship a corresponding test case in chapter 10 modelled on UC-07 (representative MPD, legacy-Player harness, silent-skip expectation, FATAL-free log). |
| BC07.9 | spec/07-backward-compat-checklist.md:99 | norm document | Given a construct's specification chapter | The chapter MUST link to the backward-compat checklist and confirm each item is satisfied. |
| BC07.10 | spec/07-backward-compat-checklist.md:100 | reviewer (norm process) | Given a construct chapter that omits checklist confirmation | Reviewers SHOULD reject the chapter. |
| BC07.11 | spec/07-backward-compat-checklist.md:105 | norm document | (unconditional) | The norm SHOULD ship an audit table summarising the checklist status for every new construct it introduces. |
| BC07.12 | spec/07-backward-compat-checklist.md:117 | reviewer (norm process) | Given any of the documented anti-patterns | Reviewers MUST flag them (mandatory element in non-extension position, reused name with new semantics, hidden sibling dependency, scheme URI without year suffix). |
| G99.1  | spec/99-glossary.md:49 | norm document | (unconditional) | The norm MUST reference canonical layout enum-values from `99-glossary.md` without inventing new names. |
| G99.2  | spec/99-glossary.md:50 | norm document | Given a new layout token | It MUST be added to the canonical layout vocabulary in `99-glossary.md` first, then referenced by the norm. |
| A01.1  | spec/01-intro.md:48 | norm document | Given a new construct introduced by the norm | The norm MUST apply the per-construct verification checklist in `07-backward-compat-checklist.md` so legacy Player compatibility is auditable per construct (redundant with BC07.1 / R1.2, kept for cross-reference). |

Total assertions: 56.

## Assertions per R

- R1: 3
- R2: 4
- R3: 3
- R4: 5
- R5: 4
- R6: 5
- R7: 5
- R8: 2
- R9: 3
- R10: 3
- (unmapped / cross-cutting orphan assertions): 19

## Assertions per actor

- Broadcaster: 2
- Broadcaster / ADS (joint): 1
- ADS: 4
- ADS / Broadcaster (joint): 1
- Player: 19
- norm document: 26
- reviewer (norm process): 2
- all: 0
- (cross-counted: assertions listed under joint actors counted once in each joint cell above; per-actor totals here count *primary* obligation owner)

## Assertions per source doc

- spec/03-requirements.md: 37
- spec/04-use-cases.md: 2
- spec/06-naming-and-namespaces.md: 6
- spec/07-backward-compat-checklist.md: 12
- spec/99-glossary.md: 2
- spec/01-intro.md: 1
- spec/02-actors.md: 0
- spec/05-dash-linear-interfaces.md: 0

The zero counts on `02-actors.md` and `05-dash-linear-interfaces.md`
are intentional: those documents are descriptive (define roles,
describe interfaces) rather than normative. Their obligations are
absorbed by the R-block conformance criteria.

## Orphan assertions

MUST / SHOULD / MAY sentences found outside the R-blocks that do not
map cleanly to one of R1..R10. For each, the proposed absorption
target (existing R it should fold into) or the gap signal it raises.

### UC04.1 — Legacy Player skips unknown construct

- Source: spec/04-use-cases.md:687.
- Summary: Player MUST skip an unknown event/construct and continue
  primary playback.
- Absorption: redundant with **R1.1**. UC-07 prose pre-dates the
  R1.1 split-out; not a new obligation, kept as cross-reference.

### UC04.2 — Extension-point expressibility for new constructs

- Source: spec/04-use-cases.md:705.
- Summary: norm document MUST express every new construct via
  extension points that produce the UC-07 outcome.
- Absorption: redundant with **R1.2** + **R9.1**. Cross-reference
  only.

### N06.1 — Cross-edition URI recognition

- Source: spec/06-naming-and-namespaces.md:27.
- Summary: a Player implementing edition N+1 SHOULD recognise both
  `:N:` and `:N+1:` scheme URIs.
- Absorption: signals a missing R. **No existing R covers cross-edition
  Player behaviour explicitly.** Candidate new R or sub-R of R1.

### N06.5 — Normative URI listing in chapter 2

- Source: spec/06-naming-and-namespaces.md:58.
- Summary: chapter 2 MUST list URIs introduced in the current
  edition.
- Absorption: norm-authoring guideline. Folds into the norm's own
  chapter-2 structure (not into an R). Acceptable as a
  norm-document-level governance assertion.

### N06.6 / G99.1 / G99.2 — Canonical layout vocabulary discipline

- Source: spec/06-naming-and-namespaces.md:65, spec/99-glossary.md:49,
  spec/99-glossary.md:50.
- Summary: layouts MUST be referenced from the canonical glossary
  vocabulary; new layouts MUST be added there first.
- Absorption: refines **R10** ("do not recreate a layout system"
  + the canonical-vocabulary discipline). Could split out as an
  R10.4. Working position: keep as ancillary discipline since the
  R10 conformance criteria already mandate use of the glossary
  enum, indirectly.

### BC07.1..BC07.12 — Per-construct backward-compat checklist

- Source: spec/07-backward-compat-checklist.md:5..117.
- Summary: norm MUST apply the seven-question checklist + audit
  table to every new construct, with anti-pattern enforcement.
- Absorption: refines **R1.2** ("new constructs MUST use DASH
  extension points") into an auditable procedure. Could fold into
  R1 conformance criteria as R1.4..R1.6, or remain as a separate
  process document. Working position: keep separate. The checklist
  is a verification procedure (process), the R-block is the
  obligation; conflating the two would bloat R1.

### A01.1 — Intro-doc reference to the checklist

- Source: spec/01-intro.md:48.
- Summary: norm MUST apply the per-construct checklist.
- Absorption: redundant with **BC07.1**. The intro file is a TOC
  cross-reference, not a new obligation.

## Notes

- The total of 56 is inside the prompt's 40-80 target range.
- The largest concentration of orphans is the BC07 set (12 of 19).
  These deserve their own home in the norm (chapter 4 Conformance or
  a separate annex) rather than being absorbed into the R-block.
- No assertion was found in `spec/02-actors.md` or
  `spec/05-dash-linear-interfaces.md`. These are descriptive
  documents; their content surfaces normatively through the R-blocks
  in `spec/03-requirements.md`.
- Assertion **N06.1** (cross-edition URI recognition) is the only
  one that arguably signals a *missing* R. Candidate for a new R or
  R1.4 in the next spec iteration.

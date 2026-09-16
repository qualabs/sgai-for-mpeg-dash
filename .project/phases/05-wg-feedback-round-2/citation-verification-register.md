# Citation verification register — `context/` against ISO/IEC 23009-1:2026

Every claim this project makes about the published MPEG-DASH 6th edition,
with the line of the standard that settles it. Source of truth: the
purchased PDF, `ISO_IEC_23009-1_2026(en)`, extracted to text; `PDF n` is
a line number in that extraction and is reproducible from it.

This file exists because the first sweep was reported in conversation and
never written down. A verdict that lives in a message cannot be audited
later, and three weeks from now "we checked the citations" is not a fact,
it is a memory.

## How to read the evidence columns

Two different things are recorded, and the register does not merge them:

| Grade | Meaning |
|---|---|
| **directa** | Verified in this register's own pass, with the PDF line printed here. Reproducible by anyone holding the PDF. |
| **agregada** | Carried from the sweep of 2026-09-15, which reported a closed verdict over the whole set but itemised only its findings. The verdict is on record; the per-site evidence is not. |

An **agregada** row is not a verified row. It is a row that says someone
looked and reported no problem, without leaving the proof.

**No row carries `agregada` today.** The grade stays defined because the
distinction is the point of this file, and the next batch of citations
will arrive carrying it again.

`Verificado` is a date because `context/` changes. A citation checked
against a sentence we later rewrite is unverified again, and without the
date nothing detects that.

## How the count moved: 23 → 25 → 30

The sweep counted **102 citations over 23 distinct clauses**. Re-deriving
the inventory today gives different numbers, for two separate reasons,
and only one of them is accounted for:

- **Against the pre-sweep tree (`cb10ae1`): 110 citations, 25 distinct.**
  The sweep's extractor cannot be reproduced, so the gap of two is
  unexplained. It is resolved by scope, not by argument: this register
  verifies everything present today, which is a superset of both.
- **Against the tree today: 123 citations, 30 distinct.** Five references
  are new, added by this phase's own commits — `§5.10.2.1` (R20.2),
  `§5.16.2.2.6` (R30), `§5.3.1.2` + `Table 3` (the separator), `Annex B`
  and `§5.10.4.5.3` (R28 and the callback fix). Fixing a citation adds
  citations.

## The 30 references

Title and line verified directly in this pass, today, for all 30.
Correspondence — whether our sentence says what the clause says — is
graded per row.

| Reference | What the standard titles it | PDF | Correspondence | Grade | Verificado |
|---|---|---|---|---|---|
| §4.7 | Schemes | 1376 / 1472 | ok — §4.7 *"specifies several schemes as listed in Table 2"*, and Table 2 maps the callback URN to §5.10.4.5. The paired citation is exact | directa | 2026-09-16 |
| §5.2.1 | General (MPD) | 1583 | ok — the removal-by-namespace obligation is quoted verbatim in DR-3 | directa | 2026-09-16 |
| §5.3.1.2 | Semantics — Table 3, Semantics of MPD element | 1979 | ok — `MPD@profiles` is comma-separated | directa | 2026-09-16 |
| §5.3.2.2 | Semantics — Table 4, Semantics of Period element | 2384 | ok — DR-7's exception is quoted verbatim from the same cell | directa | 2026-09-16 |
| §5.3.2.6 | Linked Periods | 2701 | ok — `ImportedMPD` "in a Period element" | directa | 2026-09-16 |
| §5.3.7.2 | Semantics — Table 16, Common AdaptationSet / Representation / Sub-Representation | 4355 | ok — cites the subset rule, which Table 16 states | directa | 2026-09-16 |
| §5.8.4 | Specific descriptors | 7857 | ok — heading confirmed; see the finding on its two children | directa | 2026-09-16 |
| §5.8.4.8 | Essential Property Descriptor | 8179 / 8187 | **incomplete** — an unrecognised EssentialProperty makes the client ignore **the parent element**; our text does not say so | directa | 2026-09-16 |
| §5.8.4.9 | Supplemental Property Descriptor | 8216 | **incomplete** — an unrecognised SupplementalProperty makes the client ignore **only the descriptor**; our text treats it as interchangeable with §5.8.4.8 | directa | 2026-09-16 |
| §5.10 | Events | 9332 | ok — events carry application-specific payloads and are the extension point DR-6(b) names | directa | 2026-09-16 |
| §5.10.1 | Overview | 9332 | ok — *"Events are timed, i.e. each event starts at a specific media presentation time"*, which is the timeline-scheduled claim of `05:432` | directa | 2026-09-16 |
| §5.10.2.1 | Overview (Event Stream) | 9371 | ok — the one-stream-per-(scheme,value) rule, quoted in R20.2 | directa | 2026-09-16 |
| §5.10.4.5 | DASH call back event | 10113 | ok — the callback scheme, reached from Table 2; its MPD case is §5.10.4.5.3 | directa | 2026-09-16 |
| §5.10.4.5.3 | MPD event — Table 47 | 10151 | ok — this is the fix; `.2` is the inband case | directa | 2026-09-15 |
| §5.16 | Alternative Media Presentations | 11115 | ok | directa | 2026-09-16 |
| §5.16.2.2.6 | Execution | 11578 | ok — the failure list and the smooth-continuation outcome, quoted in R30 | directa | 2026-09-16 |
| §5.16.3 | Alternative MPD Insertion Event | 11707 | ok — *"The event shall not appear if the MPD type is 'dynamic'"*, quoted verbatim in `05:45`, which is what makes InsertPresentation VOD-only | directa | 2026-09-16 |
| §5.16.4 | Alternative MPD Replacement Event | 1478 | ok — `@clip` / `@startWithOffset` / `@returnOffset` live here | directa | 2026-09-16 |
| §5.16.5 | Common Alternative Media Presentation Properties | 11955 | ok — `@maxDuration`, `@executeOnce` and `@noJump` are declared here | directa | 2026-09-16 |
| §7.3 | Media Presentation based on the ISO base media file format | 13058 | ok — *"of each Representation shall be provided according to IETF RFC 4337"*, the chain DR-1 and DR-5 rest on | directa | 2026-09-16 |
| §8.1 | Definition (Profiles) | 13322 | ok — profile identifier, `@profiles`, Interoperability Points, and the five profile-checking steps | directa | 2026-09-16 |
| §8.12 | DASH profile for CMAF content | 14272 | ok — the CMAF profile §8.14 declares itself an extension of | directa | 2026-09-16 |
| §8.14 | ISO Base Media File Format List Profile | 15350 | ok — the List profile; `type="list"` and the `list:2024` URN are its rules 1 and 2 | directa | 2026-09-16 |
| §8.15 | Single-Period Static Profile | 15371 | ok — SPS, the profile DR-1 binds to | directa | 2026-09-16 |
| Annex B | (normative) MPD schema | 16957 | ok | directa | 2026-09-16 |
| Annex F | (informative) Guidelines for extending DASH with other delivery formats | 145 / 17868 | **corrected** — DR-4 called it normative; it is informative | directa | 2026-09-16 |
| Table 3 | Semantics of MPD element | 1981 | ok | directa | 2026-09-16 |
| Table 4 | Semantics of Period element | 2386 | ok | directa | 2026-09-16 |
| Table 16 | Common AdaptationSet / Representation / Sub-Representation attributes | 4357 | **was a defect** — cited for `MPD@profiles`; fixed in `9caa460` | directa | 2026-09-15 |
| Table 47 | Relevant parameters for a Callback event signalled in the MPD | 10155 | **was a defect** — cited under §5.10.4.5.2; fixed in `6d5de1a` | directa | 2026-09-15 |

**Clauses that do not exist: zero.** Every reference resolves in the
published standard.

## Claims verified that are not clause-number checks

These were established in conversation and lived nowhere else. They are
the load-bearing ones.

### The execution and duration model (§5.16.2.2.5 / §5.16.4)

```
PDF 11235  APDmax = AlternativeMPDEventType@maxDuration, infinity if absent
PDF 11252  APDadj = max(APDmax - PRTA + PRT, 0)   if @clip="true" or absent
                  = APDmax                         if @clip="false"
PDF 11260  APDA  = min(APD - ASO, APDadj)   replacement
                 = min(APD, APDmax)          insertion
PDF 11271  RT    = PRT + RO  (if @returnOffset) | PRTA + APDA (if @clip="false")
                 | PRT + APDA (otherwise)
PDF 11870  @clip, default "true": if "true" the alternative presentation
           "shall terminate at the latest at time PRT + APDmax"; if "false",
           "shall terminate at time PRTA + APDmax". Shall not be present if
           @maxDuration is absent.
PDF 11942  @maxDuration "expressed in units of EventStream@timescale"
PDF 11955  @maxDuration absent -> infinity; if zero, the event is not executed
PDF 11973  @executeOnce, default "false"; the execution counter is E.c
```

`@executeOnce` is declared on the base type and so reaches both insertion
and replacement; `@clip` exists only on `ReplacePresentation`. Control:
`InsertPresentation@clip` returns zero, `ReplacePresentation@clip` returns
one. The structural reason is that insertion resumes at `RT = PRTA`, so
there is no original slot end for `@clip` to preserve.

### §5.16.2.2.6's failure list, in its real structure

```
PDF 11587  Execution fails if at least one of the conditions below is true at PRTA:
           — APDA is determined to be 0.
PDF 11598  — @executeOnce is set to "true", and E.c > 0 ...
PDF 11604  — The playback of the alternative presentation cannot start. The
             reasons for this include (but are not limited to) ...
PDF 11609    — Alternative MPD is a List MPD, and merge process resulted in
               no available media.
PDF 11616  A failed execution results in smooth continued playback of the
           main media presentation.
```

The `@executeOnce`-already-fired case is a sibling item of the ListMPD
case under the same "Execution fails" heading, and it is correct by
design. That is what establishes that the heading means "produced no
alternative presentation this time", not "something went wrong".

### DASH does not specify Player behaviour (the clause that dissolved M4)

```
PDF 13335  8.1 NOTE 1: "as DASH Client operation is not specified normatively
           in this document, it is also unspecified how a DASH Client conforms
           to a particular profile. Hence, profiles merely specify restrictions
           on MPD and Segments rather than DASH Client behaviour."
PDF 13365  "the MPD is modified into a profile-specific MPD for profile
           conformance checking using the following ordered steps"
PDF 13376  step 4: elements in an extension namespace not explicitly included
           by ProfA "are removed from the profile-specific MPD"
PDF 1611   5.2.1 NOTE 2: a client removing everything outside the Annex B
           schema obtains a valid document and "can use such a resulting MPD
           for presentation of a conforming Media Presentation"
```

Consequence: no cross-Player guarantee can rest on DASH conformance, by
anyone, for anything. The profile-specific MPD is a conformance-checking
construct and licenses no runtime behaviour. This is why R28 is scoped to
Players conformant to *this* specification (`a275422`).

### The zero that carries a conclusion, with its controls

**`subtree` appears zero times in the standard** — this is what makes
DR-3's old wording ours rather than a quotation.

Controls, without which the zero is an assertion and not a measurement:
the same instrument returns §5.2.1's sentence (PDF 1606), its NOTE 2
(PDF 1611) and `Spatial Relationship Description` ten times.

**`rounding` appears zero times** — this is what makes `G-1` an inherited
gap rather than one of ours, since `@maxDuration` is in timescale units
while the alternative presentation's duration is an `xs:duration`, and
the standard fixes no conversion.

Control: the stem `round` returns five hits, all of them *around* or
*background*. The instrument finds the stem; the standard has no rule.

## Method — two controls that failed, and how

Both failures produced a **false zero**, and both were caught only
because a positive control was run alongside.

1. **Line-based search over a wrapped source.** The PDF extraction wraps
   at roughly 100 columns and `context/` at 72, so a needle spanning a
   line break never matches. Fix: the search runs over a flattened copy
   with the line map retained, so a hit still reports its PDF line.
2. **Typography.** `the value of MPD@type is not 'list'` returned zero
   with straight quotes; the standard uses curly ones. It exists, at
   PDF 2539. Fix: the search normalises quotes and dashes before
   matching.

The rule both produce: **a zero is not a result until the instrument has
been shown to find something.** And its companion, bought on DR-7: read
the whole unit of the source — the cell, not the column. DR-7 looked
unfounded because the column said `0...N`; the exception was two lines
below inside the same cell.

## What this pass found that was already right

**DR-6(b) uses the recommended carrier, for a reason nobody had
written down.** It carries an inline payload inside the `<Event>`
element. The 6th edition deprecated the alternative:

```
PDF 9573  @messageData ... "Deprecated as of the 6th edition"
PDF 9578  NOTE  "Including the message within the Event element, either
          as a value or as an XML element, is the recommended approach."
```

Nothing changes. What is recorded is **why** it should not change,
which is the part that keeps someone from simplifying it next year into
the attribute the standard has retired.

## The defect this pass found — DR-6(c) merges two opposite behaviours

Promoting the twelve carried rows turned up one place where our claim is
not wrong but **incomplete in a way that matters**, which is why that
row could not simply be signed off.

`08-dash-extension-rules.md` DR-6 and `07-backward-compat-checklist.md`
both offer **"(c) vendor descriptors under §5.8.4.8 / §5.8.4.9"** as a
single carrier option, "a scheme URI with `@value` carrying the payload
string". The two clauses are named together, as alternatives of one
thing.

They fail in opposite directions:

```
PDF 8187   5.8.4.8 EssentialProperty, NOTE 1: "If the scheme or the value
           for this descriptor is not recognized, the DASH Client is
           expected to ignore THE PARENT ELEMENT that contains the
           descriptor."
PDF 8216   5.8.4.9 SupplementalProperty, NOTE: "If the scheme or the
           value for this descriptor is not recognized, the DASH Client
           is expected to ignore THE DESCRIPTOR."
```

An SGAI scheme carried on an `EssentialProperty` therefore makes a
legacy Player **drop the AdaptationSet or Representation that holds
it** — the opposite of the graceful degradation the whole extension
strategy rests on, and a direct hazard to DP-3's invariant that
applying this specification never breaks primary-content playback.
Carried on a `SupplementalProperty`, the same scheme costs nothing.

**Where this bites hardest is the backward-compatibility checklist**,
whose entire purpose is to make legacy behaviour auditable per
construct — and which currently offers the dangerous half and the safe
half as one choice, with no way to tell them apart.

This is a correction with no trade-off rather than a decision: which of
the two is admissible follows from what dropping the parent would cost,
and DP-3 already answers that for anything on the primary content path.
It is recorded here rather than applied because it changes what DR-6
offers, which is more than a wording fix.

## What this register does NOT establish

- **Every row now carries direct evidence.** The twelve that were
  carried from the 2026-09-15 sweep were re-verified against the
  primary copy on 2026-09-16, each against what its sentence asserts
  rather than against its clause number.
- **It does not re-verify anything against `context/` as of a later
  edit.** Each row is true as of its `Verificado` date and no later.
- **It records no claim about the FDIS draft.** Everything here is
  against the published 2026 edition.

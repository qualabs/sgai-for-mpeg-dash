# T-04: the examples as fixtures with a declared class

`spec-source/examples/index.yaml` declares the class of each of the 93
fixtures; `bin/check-dash-conformance.py --source spec-source` runs levels 1
and 2 on them by that class, with `spec-source/syntax/sgai-extension.xsd`
(ADR 0063). Code: `bin/conformance/source.py`, `bin/conformance/clauses.py`;
tests: `bin/test_conformance_source.py`.

## The classes

| Class | Fixtures |
|---|---|
| publisher-mpd | 19 |
| legacy-view | 1 |
| list-mpd | 8 |
| sps-mpd | 24 |
| overlay-list | 23 |
| request | 10 files (12 requests) |
| fragment | 6 |
| vast | 2 |

Every MPD the prose introduces was read in its place in
`spec-source/sgai-spec.src.md`. One is a legacy view:

- `annex-g/G.3-1.mpd`, under "G.3 The same document after removal of the
  extension namespace": *"A client that removes every element and attribute
  outside the DASH namespace, as DASH §5.2.1 lets it, obtains:"*. It is the
  main MPD of G.2 as a Player that predates this specification sees it, and
  no party of this specification writes it.

The other 19 MPDs are introduced as a main MPD (`### X.2 The main MPD`,
E.10's live variant "the same window is declared in a dynamic MPD") or, in
N.4, as the slate's MPD, which carries its own overlay window: all are
written by a Publisher.

FIX-2 checks each declaration against the class `extract.py` deduces from the
document (a legacy view is deduced as an MPD): 93 PASS.

## Source run against the dist run

Compared: `--source spec-source` against the document run on a copy of
`dist/sgai-spec.md` with the XSD emitted beside it (so the dist run has 8
FAIL, not the 9 of a dist without `sgai-extension.xsd`). Each dist subject is
mapped to its fixture by the order of the directives in the prose.

| | PASS | FAIL | NOT_VERIFIABLE | NOT_APPLICABLE |
|---|---|---|---|---|
| dist (XSD beside it) | 1108 | 8 | 273 | 1531 |
| source | 1201 | 6 | 273 | 1537 |

Every difference, and nothing else (the test
`TestAgainstDocumentRun` asserts it result by result):

1. **The legacy view (G.3).** In the dist run the 16 level-2 rules that read
   an MPD judged xml#40 as a Publisher MPD: 2 FAIL (R40.9a on the overlay and
   pause-trigger events, which lost their window elements with the
   namespace), 5 PASS (R4.6, R20.2a, R20.2b, R35.8, R40.7) and 10
   NOT_APPLICABLE for lack of the construct. In the
   source run each of those 16 rules gives one NOT_APPLICABLE with the
   reason: *the criteria of context/03 do not bind a document no party of
   this specification writes*. Level 1 (E-1..E-4, the base-standard rules)
   judges G.3 as before. FAIL 8 → 6, PASS −5 + 98 new, NOT_APPLICABLE −10 + 16; and the remaining 6 are the carriers
   the v13 adds (3× R12.1a, R34.1a, R34.9a, R13.6a).
2. **Rules only the source has** (all PASS on the source):
   - FIX-1 (1): every file has one entry of a known class, every entry a
     file, and the prose holds no example of its own.
   - FIX-2 (93): declared class = deduced class.
   - C06-1a (2): `@earliestResolutionTimeOffset` on `OverlayPresentationType`
     and `PauseAdPresentationType` is `xs:unsignedLong` with no default, as
     in ISO's `AlternativeMPDEventType`.
   - C06-1b (1): `@executeOnce` on `PauseAdPresentationType` is `xs:boolean`
     default `false`, as ISO's. (Its absence from the overlay window is
     R34.1a's FAIL, which both runs report.)
   - DASH-REF (1): the 185 `DASH §n` of the prose name 47 distinct clauses,
     all in the primary copy's clause index (474 clauses).
3. **XSD-ID** asks a different question in each mode. On a document: the
   file is byte-identical to the spec's block. On the source: the prose has
   exactly one `{{xsd}}` directive and no inline schema block, so the
   assembled block is the file. PASS in both.

## The rules added, and their negatives

| Rule | Negative (`bin/conformance/fixtures/negative/source/`) | Caught |
|---|---|---|
| C06-1a | `source-C06-1a-earliest-offset-unsignedint`: the overlay window's attribute typed `xs:unsignedInt` | yes |
| C06-1b | `source-C06-1b-execute-once-default-true`: the pause window's default `true` | yes |
| DASH-REF | `source-DASH-REF-nonexistent-clause`: cites `DASH §5.10.4.9` (§5.10.4 has seven subclauses) beside a real §5.16.3 | yes, only the 5.10.4.9 line, with the real index and with a stand-in |
| FIX-1, FIX-2 | built in the tests on a copy of `spec-source/` (unknown class, file without entry, entry without file, an example written in the prose, a contradicted class) | yes |

The negatives live in a subdirectory so that `--demo`, which runs only the
document mode's rules, does not count them as missed (still 84/84).

**Not added: `Event@id` unique within one `svta:Tracking`.** No criterion of
`context/03` states it, and R6.5 states the opposite: *"Within a candidate,
beacons sharing an `@id`, or the same URL at the same presentation time, are
one beacon and fire once."* The spec's §5.5.2 says the same ("The base rule
that an `EventStream` holds no two `Event` elements with the same `@id` does
not apply"). Searched: `grep -n -i -E "Event@id|@id" context/03-requirements.md`
(R6.5 is the only criterion on a beacon's `@id`) and
`grep -rn -i "unique" context/*.md` (nothing on events or tracking). A rule
would contradict the requirement, so ADR 0063's line was not followed.

## The clause index

`bin/conformance/clauses.py` locates the copy as `check-normative-base.py`
does (`SGAI_NORMATIVE_PDF`, else `NORMATIVE_PDF_PATH` in `.env.agent`),
refuses a file whose sha256 is not the one `context/00` declares, and reads
`pdftotext -layout` through a pipe: no text is written anywhere, not even to
a temporary file. It keeps body lines of the form `<number> <Capitalised
title>`, skips table-of-contents lines, keeps a number only when its parent
is kept, and refuses an index lacking any of clauses 1..8. Without the copy
DASH-REF is NOT_VERIFIABLE, never PASS.

Checked against the copy's own table of contents (an independent part of the
document, read the same way): the 57 TOC entries (two levels deep) are all in
the index; no parent has a gap in its children's numbering (1..k for all
474); `5.10.4.9` and clause `9` are absent, `5.16.5.2` and `5.16.2.2.6` present.

## What a green does not say

That the clause cited says what the prose cites it for; anything about the
prose beyond its `DASH §n` references; whether a `legacy-view` is really what
a legacy Player sees (only that it is an MPD the base standard accepts).

# T-04 evidence — level 1 catalog (2026-11-23)

Files: `bin/conformance/dash/rules.py`, `bin/conformance/dash/__init__.py`,
`bin/test_conformance_dash.py`, 25 pairs `bin/conformance/fixtures/negative/dash-*`.

## Quotes against the primary copy

Extraction `pdftotext -layout` of the copy at `NORMATIVE_PDF_PATH`, in a private
temp dir (deleted), whitespace flattened, curly quotes folded. Count of each
catalog quote in the flattened text, with a known-present control and a
known-absent control on the same search:

```
DR-1 1 | DR-1a 1 | DR-1b 1 | DR-1c 1 | DR-1d 1 | DR-1e 1 | DR-1f 1 | DR-1g 1 | DR-1h 1 | DR-1i 1
DR-3 1 | DR-4 1 | DR-5a 1 | DR-5b 1 | DR-6 1 | DR-7 1 | DR-8 1 | DR-9 1
DR-10a 1 | DR-10b 1 | DR-10c 1 | DR-10d 1
K-4a 1 | K-4b 1 | K-13a 1 | K-13b 1 | K-14 1 | K-15a 1 | K-15b 1 | K-17 1 | K-20 1
CONTROL-known ("List MPDs shall not contain Alternative MPD events.") 1
CONTROL-bogus ("List MPDs shall contain Alternative MPD events.") 0
C07-3 1 | C07-6a 1 | C07-6b 1 | C07-6c 1 | C07-7 1   (in context/06 + context/07)
```

`[fetch-failed]`: none. The K-4a sentence first searched without its tail
(ending at "@value attribute.") gave 0; the sentence continues
("…, i.e. all Events of one type shall be clustered in one Event Stream."),
and the full sentence gives 1.

RFC 4337's registered types (DR-1a) read from rfc-editor.org: video/mp4,
audio/mp4, application/mp4, application/mpeg4-iod, application/mpeg4-iod-xmt.

Leak scan of the new files for the extraction's header/footer strings: 0 files;
the same pattern counts 384 lines in the extraction.

## Tests

```
$ uv run -q --no-project --with lxml==6.1.3 python -I bin/test_conformance_dash.py -v
test_every_coded_rule_has_one_negative (__main__.Catalog.test_every_coded_rule_has_one_negative) ... ok
test_shape (__main__.Catalog.test_shape) ... ok
test_every_rule_pass_or_not_applicable (__main__.IsoPositives.test_every_rule_pass_or_not_applicable) ... ok
test_forty_one_examples (__main__.IsoPositives.test_forty_one_examples) ... ok
test_dash_negatives (__main__.Negatives.test_dash_negatives) ... ok

Ran 5 tests in 1.907s
OK
```

`python -I -m unittest bin/test_conformance_dash.py` cannot import the file:
`-I` drops the working directory from `sys.path`, and unittest turns the path
into the module `bin.test_conformance_dash`. The file runs as a script, as
`test_conformance_core.py` does.

ISO positives: no ISO example is an SPS MPD, so DR-1a..DR-1i have no external
positive (kept explicit in `NO_ISO_INSTANCE`). DR-5a and DR-5b have ISO
instances but every one is NOT_APPLICABLE (no `@profiles` below MPD level, no
inline AdaptationSet in a List MPD), in ISO and in the spec alike.

K-17 was written as code first and failed ISO's K.6.4, whose AdaptationSet
elides its Representations (`<!-- ... -->`); §8.1 states it as a condition on
the Media Presentation, so it entered as NOT_VERIFIABLE.

## Mutation campaign

One mutation per rule in `rules.py`, `Negatives` and `IsoPositives` run,
file restored (sha256 identical after the campaign).

| rule | broken how | red | own negative red | ISO positives red |
|---|---|---|---|---|
| DR-1a | RFC 4337 test disabled | yes | yes | — |
| DR-1b | value comparison disabled | yes | yes | — |
| DR-1c | scope narrowed to type=list | yes | yes | — |
| DR-1d | allows two Periods | yes | yes | — |
| DR-1e | presence test replaced | yes | yes | — |
| DR-1f | mediaPresentationDuration test disabled | yes | yes | — |
| DR-1g | Location dropped from the list | yes | yes | — |
| DR-1h | element name misspelt | yes | yes | — |
| DR-1i | condition inverted | yes | yes | — |
| DR-5a | subset test inverted | yes | yes | — |
| DR-5b | always ok | yes | yes | — |
| DR-7 | condition inverted | yes | yes | DR-7 |
| DR-10a | condition inverted | yes | yes | DR-10a |
| DR-10b | scope test inverted | yes | yes | — |
| C07-6a | pattern accepts anything | yes | yes | — |
| C07-6b | pattern accepts anything | yes | yes | — |
| C07-6c | pattern accepts anything | yes | yes | — |
| K-4a | duplicate test disabled | yes | yes | — |
| K-4b | duplicate test disabled | yes | yes | — |
| K-13a | wrong type compared | yes | yes | — |
| K-13b | condition inverted | yes | yes | — |
| K-14 | condition inverted | yes | yes | K-14 |
| K-15a | scope test inverted | yes | yes | K-15a |
| K-15b | scheme test inverted | yes | yes | K-15b |
| K-20 | condition inverted | yes | yes | K-20 |

## The published spec

```
$ python3 bin/check-dash-conformance.py dist/sgai-spec.md --out-md $XDG_RUNTIME_DIR/cto/t04.md
exit 1: PASS 997  FAIL 9  NOT_VERIFIABLE 228  NOT_APPLICABLE 1511
```

No rule of this catalog FAILs on `dist/sgai-spec.md`. The 9 FAILs are XSD-ID
(`dist/sgai-extension.xsd` does not exist) and 8 of level 2 (R12.1a ×3,
R34.1a, R34.9a, R40.9a ×2, R13.6a), outside T-04.

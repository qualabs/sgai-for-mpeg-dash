# Behaviour tests

One or more files per criterion of `context/03` that the level-2 catalogue
sends to level 3: `R<n>.<m>.yaml`, or `R<n>.<m>-<k>.yaml` when a criterion
needs several. Each is a vector with the schema of the UC vectors,
`../scenarios/schema.json` (ADR 0077), and is read like one: everything in
`../scenarios/README.md` ("Where each value comes from" for documents and
times, "The fields") holds here. This file says only what differs.

```bash
python3 bin/check-behaviour.py                  # the whole check (exit 0/1/2/64, --json)
python3 bin/check-behaviour.py uncovered        # the criteria with neither a test nor an entry
python3 bin/check-behaviour.py criterion R4.9   # its criterion_sha256 on line 1, then the text it is taken over
```

The population is not written anywhere: the check reads it from the
catalogue every run (`--help` gives the rule). A criterion of it has tests,
or an entry in `index.yaml` with its `NOT_VERIFIABLE` reason, never both.

## What differs from a UC vector

- **`criterion`, `criterion_sha256`** in place of `uc`, `uc_sha256`; the hash
  from `check-behaviour.py criterion`, never by hand. No `missing_carrier`
  and no `disagreements`: a criterion whose carrier is missing goes to
  `index.yaml` (ADR 0084), and a gap in the specification is a finding, not
  a test.
- **Written from the criterion's text**, not from a UC: what is loaded, what
  the viewer does and what is expected all serve to decide that criterion.
  Say in `summary` which sentence of it the outcome decides. Outcomes only
  for the classes where the criterion says something; any class may appear.
- **Fixtures**: those of `../examples/` when one fits, else new ones in
  `fixtures/R<n>.<m>/`, each with its `class` (the classes of
  `../examples/index.yaml`), green on levels 1 and 2 like any fixture.
- **`aps`**: how the test APS answers. One entry per URL (and `nth` to pick
  one request of several): `status` with an optional `document` (absent: an
  empty body) and `delay`, or `no_response: true`. A URL no entry names is
  answered at once with `200` and the request's `answered_by`; a request
  answered without a document has no `answered_by`.
- **`actions`**: as in a UC vector (`pause`, `resume`, `seek` with `to`,
  `rate` with `rate`, `dismiss`, `activate` for a click on the ad), at
  session times.
- **`geometry`** (per outcome): at an instant `at`, the expected `primary`
  and `ad` rectangles, `{x, y, width, height}` in percent of the Player's
  viewport, origin top-left, with a `tolerance` in percentage points per
  edge. At that instant the outcome's `presentation` must show what the
  rectangle places.

## Checking it

`check-behaviour.py` exits 1 while criteria are uncovered; the findings that
name your test must be none, and a stale hash (exit 2) means re-reading the
criterion before copying its new hash. Run `python3 bin/test_check_behaviour.py`
if you touch the check. No Player runs a test here: every one is
`NOT_VERIFIABLE — no executor` until the behaviour executor exists.

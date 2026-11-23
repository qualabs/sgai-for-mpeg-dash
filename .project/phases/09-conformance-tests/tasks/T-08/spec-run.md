# T-08 — DASH-IF Conformance tool over the MPDs of `dist/sgai-spec.md`

Measured 2026-11-23, same tool, image and modules as [`baseline.md`](baseline.md),
over the 52 MPD-kind blocks of `dist/sgai-spec.md` (20 `mpd`, 24 `sps-mpd`,
8 `list-mpd`, as classified by `bin/conformance/extract.py`; the other 32 XML
blocks are not MPDs and are skipped). This auditor informs; it decides nothing.

## Result

| Bucket | Documents |
|---|---|
| **Ours** (a finding the tool raises on none of ISO's 41 examples) | **0** |
| Baseline only (every finding also raised on an ISO example) | 32 (all 24 `sps-mpd`, all 8 `list-mpd`) |
| No schematron/IOP finding at all | 20 (all 20 `mpd`) |
| DASH 5th XSD rejects (discarded) | 17 |
| Tool aborts | 0 |

The 17 DASH 5th rejections are all 6th-edition constructs, the same family the
tool rejects on ISO's examples: `MPD@type="list"` + `ImportedMPD` (the 8
`list-mpd`), `InsertPresentation` (7 `mpd`), `ReplacePresentation` (2 `mpd`).
That matches the 17 of 52 measured before this task.

The baseline findings on our documents are four schematron assertions:

| Short | Assertion | Ours | Matched on ISO |
|---|---|---|---|
| PROFILE | At least one unknown profile string found. Known list in schematron file. | 32 | 9 examples |
| MPD-DUR | If mediaPresentationDuration is not defined for the MPD minimumUpdatePeriod shall be defined or vice versa. | 32 | G29-2 |
| BASEURL | At least one BaseURL, SegmentTemplate or SegmentList shall be defined in Period, AdaptationSet or Representation. | 8 | G8, G29-2 |
| SRD | When every Adaptation Set in a MPD has a SRD descriptor, at least one of this descriptor shall be a SupplementalProperty. | 8 | G29-2 |

## What the subtraction hides, read before trusting the zero

The baseline is matched by rule, not by cause. Two of the matches deserve a
person's look, not because they look wrong but because the ISO match is thin:

- **PROFILE on the 24 `sps-mpd`.** On ISO the rule fires for
  `advanced-linear:2025` and `list:2024`; `urn:mpeg:dash:profile:sps:2024`
  appears in none of ISO's examples, so no ISO example shows the tool rejecting
  *that* string. Same cause (a profile list older than the 6th edition), not the
  same evidence.
- **MPD-DUR on the 24 `sps-mpd`.** Its only ISO match is G29-2, a `list` MPD.
  Our SPS MPDs are `static`, with no `@mediaPresentationDuration` and the
  duration on `Period@duration` (e.g. xml#12, line 3898: `<Period id="cr101"
  duration="PT15S">`). The assertion ignores `Period@duration`; whether the
  6th edition requires `@mediaPresentationDuration` here was not checked
  against the primary copy [inferred: the tool's rule is stricter than the
  standard].

## Per document

The "DASH 5th XSD" column lists the element (or `element@attribute`) that XSD rejects.

| Block | Kind | Line | Baseline findings (rule) | DASH 5th XSD (discarded) | Ours |
|---|---|---|---|---|---|
| xml#3 | list-mpd | 2338 | MPD-DUR, PROFILE, BASEURL, SRD | MPD@type | — |
| xml#10 | mpd | 3809 | — | InsertPresentation | — |
| xml#11 | list-mpd | 3855 | MPD-DUR, PROFILE, BASEURL, SRD | MPD@type, ImportedMPD | — |
| xml#12 | sps-mpd | 3898 | MPD-DUR, PROFILE | — | — |
| xml#13 | sps-mpd | 3934 | MPD-DUR, PROFILE | — | — |
| xml#15 | mpd | 4095 | — | ReplacePresentation | — |
| xml#16 | list-mpd | 4143 | MPD-DUR, PROFILE, BASEURL, SRD | MPD@type, ImportedMPD | — |
| xml#17 | sps-mpd | 4165 | MPD-DUR, PROFILE | — | — |
| xml#18 | mpd | 4262 | — | — | — |
| xml#20 | sps-mpd | 4360 | MPD-DUR, PROFILE | — | — |
| xml#21 | sps-mpd | 4379 | MPD-DUR, PROFILE | — | — |
| xml#23 | mpd | 4500 | — | InsertPresentation | — |
| xml#24 | list-mpd | 4564 | MPD-DUR, PROFILE, BASEURL, SRD | MPD@type, ImportedMPD | — |
| xml#26 | sps-mpd | 4606 | MPD-DUR, PROFILE | — | — |
| xml#27 | sps-mpd | 4640 | MPD-DUR, PROFILE | — | — |
| xml#28 | mpd | 4704 | — | — | — |
| xml#30 | sps-mpd | 4804 | MPD-DUR, PROFILE | — | — |
| xml#32 | mpd | 4887 | — | — | — |
| xml#33 | mpd | 4951 | — | InsertPresentation | — |
| xml#34 | list-mpd | 4988 | MPD-DUR, PROFILE, BASEURL, SRD | MPD@type, ImportedMPD | — |
| xml#35 | sps-mpd | 5011 | MPD-DUR, PROFILE | — | — |
| xml#36 | sps-mpd | 5040 | MPD-DUR, PROFILE | — | — |
| xml#37 | sps-mpd | 5070 | MPD-DUR, PROFILE | — | — |
| xml#38 | sps-mpd | 5099 | MPD-DUR, PROFILE | — | — |
| xml#39 | mpd | 5189 | — | InsertPresentation | — |
| xml#40 | mpd | 5251 | — | InsertPresentation | — |
| xml#41 | list-mpd | 5301 | MPD-DUR, PROFILE, BASEURL, SRD | MPD@type, ImportedMPD | — |
| xml#42 | sps-mpd | 5322 | MPD-DUR, PROFILE | — | — |
| xml#43 | mpd | 5423 | — | — | — |
| xml#46 | sps-mpd | 5539 | MPD-DUR, PROFILE | — | — |
| xml#47 | sps-mpd | 5558 | MPD-DUR, PROFILE | — | — |
| xml#48 | mpd | 5627 | — | — | — |
| xml#50 | sps-mpd | 5716 | MPD-DUR, PROFILE | — | — |
| xml#51 | sps-mpd | 5737 | MPD-DUR, PROFILE | — | — |
| xml#52 | mpd | 5819 | — | — | — |
| xml#54 | sps-mpd | 5900 | MPD-DUR, PROFILE | — | — |
| xml#55 | mpd | 5963 | — | InsertPresentation | — |
| xml#56 | list-mpd | 6010 | MPD-DUR, PROFILE, BASEURL, SRD | MPD@type, ImportedMPD | — |
| xml#57 | sps-mpd | 6027 | MPD-DUR, PROFILE | — | — |
| xml#59 | mpd | 6118 | — | — | — |
| xml#62 | sps-mpd | 6218 | MPD-DUR, PROFILE | — | — |
| xml#64 | mpd | 6313 | — | — | — |
| xml#69 | sps-mpd | 6490 | MPD-DUR, PROFILE | — | — |
| xml#70 | sps-mpd | 6511 | MPD-DUR, PROFILE | — | — |
| xml#71 | mpd | 6587 | — | ReplacePresentation | — |
| xml#73 | mpd | 6668 | — | — | — |
| xml#74 | mpd | 6778 | — | — | — |
| xml#78 | mpd | 6918 | — | — | — |
| xml#80 | mpd | 7037 | — | InsertPresentation | — |
| xml#82 | list-mpd | 7116 | MPD-DUR, PROFILE, BASEURL, SRD | MPD@type, ImportedMPD | — |
| xml#83 | sps-mpd | 7133 | MPD-DUR, PROFILE | — | — |
| xml#84 | sps-mpd | 7162 | MPD-DUR, PROFILE | — | — |

## How to reproduce

```bash
cd bin && uv run -q --no-project --with lxml==6.1.3 python -I -c '
import sys, json; sys.path.insert(0, ".")
from conformance import iso, dashif, extract
r = dashif.run(extract.blocks(open("../dist/sgai-spec.md").read()), iso.materialise())
print(json.dumps(r["summary"], indent=1))'
```

Output of that run:

```
{
 "documents": 52,
 "with_ours": 0,
 "with_baseline_only": 32,
 "xsd5_rejected": 17,
 "ours_keys": []
}
```

## The instrument can find, and documents do not leak into each other

A zero in "ours" is only a result if the same path can produce a non-zero.
ISO's G1 with one Role value changed to `bogus`, run before an unmodified G1 in
the same batch:

```
a-neg-role-bogus {'xsd': [], 'baseline': [], 'ours': ['Global - Schematron | The value of Role (role) shall be caption, subtitle, main, alternate, supplementary, commentary or dub.']}
b-clean-G1 {'xsd': [], 'baseline': [], 'ours': []}
```

ISO's G19 submitted as one of ours lands in `baseline`, not `ours`:

```
{'xsd': [], 'baseline': ['Global - Schematron | The id of each AdaptationSet within a Period shall be unique.'], 'ours': []}
```

With an image that does not exist:

```
{'ran': False, 'reason': 'image sgai-nope:x not available; run bin/dashif/build.sh', ...}
```

Not detected by this tool (seen while choosing the negative): a duplicated
`Representation@id` in G1 produced no finding.

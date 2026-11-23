# T-08 — DASH-IF Conformance tool: false-positive baseline on ISO's 41 examples

Measured 2026-11-23 with DASH-IF-Conformance `v3.1.0`
(commit `bdf0c27a8f198da7a4bf81634bb01faf7c7c3c06`, verified by
`bin/dashif/build.sh` before building), image `sgai-dashif-conformance:v3.1.0`
(`sha256:eaca4907bdd7…`), modules `Global Module` + `IOP MPD`, no network, over
ISO's 41 example MPDs of the 6th-edition schema zip (sha256 `43b62f3d80a2…`,
`bin/conformance/iso.py`). Segment-level modules not run (no GPAC).

All 41 examples validate against ISO's own 6th-edition `DASH-MPD.xsd` (lxml
6.1.3, 0 invalid), so everything below that rejects one of them is the tool's,
not the example's.

## Summary

| What the tool reports | Examples |
|---|---|
| Nothing (no FAIL/WARN) | 13: G1–G7, G9, G13-1, G15, G21_patch_base, G28-3, G28-4 |
| Only legacy DVB XSD failures (discarded) | 5: G16, G17, G20, G25, G30-2 |
| DASH 5th XSD rejects (discarded) | **8**: G23, G26-1, G26-2, G27, G28-5, G29-1, G29-2, K6.4 (G23 has nothing else) |
| Schematron assertion fails (baseline) | 16 examples, 13 distinct assertions |
| Schematron cannot run (`XPTY0004` in the tool's `val_schema.xsl`) | 3: G10, H1, H2 |
| Tool aborts, no report (PHP exception) | 3: G11, G12, G13-2 |
| IOP MPD FAIL/WARN | 0 (only G6 signals an IOP identifier, `dash264`) |

The baseline that `bin/conformance/dashif.py` subtracts is the set of
`(module, test)` keys of the schematron and abort rows: 17 keys (13 assertions, the "Schematron shall be able to run" check, 3 abort locations). The XSD rows
(DASH 5th and the two legacy DVB XSDs) are never compared: they are discarded.

Two things in the tool shape this baseline, and both are the tool's:

- **`At least one unknown profile string found`** fires on 9 examples: the
  schematron's profile list does not know `urn:mpeg:dash:profile:advanced-linear:2025`
  or `urn:mpeg:dash:profile:list:2024`.
- The **DASH 5th XSD** rejects every 6th-edition construct it meets:
  `ReplacePresentation` (G23, G29-1), `SegmentSequenceProperties` (G26-1, G26-2),
  `SegmentTimeline/Pattern` (G27), `RequestParam` (G28-5, G29-1),
  `MPD@type="list"` and `ImportedMPD` (G29-2), and `ClientDataReporting` inside
  `ServiceDescription` (K6.4). The tool's line numbers refer to its re-serialised
  copy of the document, not the file; validating the files directly against the
  tool's `DASH5th.xsd` gives the same 8 examples (and, for G28-5, a
  `ContentSteering` error the tool did not list).

## Per example

Module of each finding: schematron rows are `Global - Schematron`; the XSD
columns are `Global - XSD` (DASH 5th) and `LEGACY - XSD` (DVB 2018 / 2019).

| Example | Schematron / IOP / tool error (baseline) | DASH 5th XSD (discarded) | Legacy XSDs (discarded) |
|---|---|---|---|
| G1 | — | — | — |
| G2 | — | — | — |
| G3 | — | — | — |
| G4 | — | — | — |
| G5 | — | — | — |
| G6 | — | — | — |
| G7 | — | — | — |
| G8 | At least one BaseURL, SegmentTemplate or SegmentList shall be defined in Period, AdaptationSet or Representation. | — | — |
| G9 | — | — | — |
| G10 | Schematron shall be able to run | — | DASH 2nd (DVB 2018) |
| G11 | abort: In XLink.php line 28 — file_get_contents(example_G11_remote.period.xml): Failed to open stream: No such file or directory | — | — |
| G12 | abort: In UriString.php line 572 — The uri `%20http://example.com/1/` contains an invalid scheme | — | — |
| G13-1 | — | — | — |
| G13-2 | abort: In Uri.php line 791 — The path mimetype `/video/mp4` is invalid. | — | — |
| G14 | For ISO BMFF extended live profile, MPD@type shall be static. | — | — |
| G15 | — | — | — |
| G16 | — | — | DASH 2nd (DVB 2018) |
| G17 | — | — | DASH 2nd (DVB 2018) |
| G18 | For ISO BMFF extended live profile, MPD@type shall be static. | — | DASH 2nd (DVB 2018) |
| G19 | The id of each AdaptationSet within a Period shall be unique. | — | — |
| G20 | — | — | DASH 2nd (DVB 2018) |
| G21_patch_base | — | — | — |
| G22 | Common attributes for AdaptationSet and Representation shall either be in one of the elements but not in both.<br>If more than one Media Segment is present the duration attribute or SegmentTimeline element shall be present. | — | DASH 2nd (DVB 2018) |
| G23 | — | ReplacePresentation | DASH 2nd (DVB 2018)<br>DASH 4th-amd1 (DVB 2019) |
| G25 | — | — | DASH 2nd (DVB 2018) |
| G26-1 | At least one unknown profile string found. Known list in schematron file.<br>Only identifiers such as $Bandwidth$, $Time$, $RepresentationID$, or $Number$ shall be used. | SegmentSequenceProperties | DASH 2nd (DVB 2018)<br>DASH 4th-amd1 (DVB 2019) |
| G26-2 | At least one unknown profile string found. Known list in schematron file.<br>Only identifiers such as $Bandwidth$, $Time$, $RepresentationID$, or $Number$ shall be used. | SegmentSequenceProperties | DASH 2nd (DVB 2018)<br>DASH 4th-amd1 (DVB 2019) |
| G27 | At least one unknown profile string found. Known list in schematron file. | Pattern | DASH 2nd (DVB 2018)<br>DASH 4th-amd1 (DVB 2019) |
| G28-1 | At least one unknown profile string found. Known list in schematron file. | — | — |
| G28-2 | At least one unknown profile string found. Known list in schematron file. | — | DASH 2nd (DVB 2018) |
| G28-3 | — | — | — |
| G28-4 | — | — | — |
| G28-5 | At least one unknown profile string found. Known list in schematron file. | RequestParam | DASH 2nd (DVB 2018)<br>DASH 4th-amd1 (DVB 2019) |
| G29-1 | At least one unknown profile string found. Known list in schematron file. | ReplacePresentation<br>RequestParam | DASH 2nd (DVB 2018)<br>DASH 4th-amd1 (DVB 2019) |
| G29-2 | If mediaPresentationDuration is not defined for the MPD minimumUpdatePeriod shall be defined or vice versa.<br>At least one unknown profile string found. Known list in schematron file.<br>At least one BaseURL, SegmentTemplate or SegmentList shall be defined in Period, AdaptationSet or Representation.<br>When every Adaptation Set in a MPD has a SRD descriptor, at least one of this descriptor shall be a SupplementalProperty. | MPD@type<br>ImportedMPD | DASH 2nd (DVB 2018)<br>DASH 4th-amd1 (DVB 2019) |
| G30-1 | For live profile, the SegmentTemplate element shall be present on at least one of the three levels, the Period level containing the Representation, the Adaptation Set containing the Representation, or on Representation level itself. | — | DASH 2nd (DVB 2018) |
| G30-2 | — | — | DASH 2nd (DVB 2018) |
| H1 | Schematron shall be able to run | — | — |
| H2 | Schematron shall be able to run | — | — |
| H3 | Either the Representation or the containing AdaptationSet shall have the mimeType attribute. | — | DASH 2nd (DVB 2018) |
| K6.4 | If MPD is of type "dynamic" publishTime shall be defined.<br>At least one unknown profile string found. Known list in schematron file.<br>An AdaptationSet shall have at least one Representation element. | ServiceDescription | DASH 2nd (DVB 2018)<br>DASH 4th-amd1 (DVB 2019) |


## How to reproduce

```bash
bin/dashif/build.sh          # once
cd bin && uv run -q --no-project --with lxml==6.1.3 python -I -c '
import sys; sys.path.insert(0, ".")
from conformance import iso, dashif
r = dashif.run([], iso.materialise())
print(r["baseline"]["xsd5_rejected"]); print(list(r["baseline"]["keys"]))'
```

The per-example result is cached at
`~/.cache/sgai-conformance/dashif-baseline-<image-id>-<zip>.json`; delete it to
re-measure.

<!--
DRAFT — NOT PUBLISHED. Do not post without the project lead's explicit OK
(ADR 0058). Target: https://github.com/Dash-Industry-Forum/DASH-IF-Conformance/issues
Checked 2026-11-23: `gh search issues --repo Dash-Industry-Forum/DASH-IF-Conformance "6th edition"`
and `... "XSD"` returned no open issue on this; #563 ("Schema validation is out of date",
closed 2026-01-29) is about the old Java validator and says the .xsd files can now be replaced.
Everything below the line is the issue body.
-->

**Title:** MPD XSD validation uses the 5th-edition schema and rejects valid ISO/IEC 23009-1 6th-edition MPDs (8 of ISO's 41 schema examples)

---

### Summary

In `v3.1.0`, the Global Module validates the MPD against `resources/xsd/DASH5th.xsd`
(`app/Modules/Common/MPD/XSDValidation.php`, test "DASH 5th / MPD SHALL be valid").
MPDs that use constructs introduced in ISO/IEC 23009-1 6th edition therefore FAIL that
test even when they are valid against the 6th-edition schema.

Measured on the example MPDs ISO publishes with the 6th-edition schema
(`https://standards.iso.org/iso-iec/23009/-1/ed-6/en/DASHSchema-6th-Ed.zip`, 41 `.mpd`
files): all 41 validate against the zip's own `DASH-MPD.xsd`; the tool's DASH 5th test
rejects 8 of them.

### Version

- DASH-IF-Conformance `v3.1.0` (commit `bdf0c27a8f198da7a4bf81634bb01faf7c7c3c06`), built
  from source, run with the CLI:
  `php artisan app:analyze-manifest <file> "Global Module" "IOP MPD"`
- ISO schema zip: sha256 `43b62f3d80a2cfca99d7530e8c092d032bf65736eb1ce176ae6bc8454feb1d28`

### The 8 examples rejected

| ISO example | 6th-edition construct | Tool message (DASH 5th, "MPD SHALL be valid") |
|---|---|---|
| `example_G23.mpd` | `ReplacePresentation` | `Element '{urn:mpeg:dash:schema:mpd:2011}ReplacePresentation': This element is not expected. Expected is ( ##other{urn:mpeg:dash:schema:mpd:2011}* ).` |
| `example_G26-1.mpd` | `SegmentSequenceProperties` | `Element '{urn:mpeg:dash:schema:mpd:2011}SegmentSequenceProperties': This element is not expected. Expected is one of ( {urn:mpeg:dash:schema:mpd:2011}SupplementalProperty, {urn:mpeg:dash:schema:mpd:2011}InbandEventStream, {urn:mpeg:dash:schema:mpd:2011}Switching, ...` |
| `example_G26-2.mpd` | `SegmentSequenceProperties` | `Element '{urn:mpeg:dash:schema:mpd:2011}SegmentSequenceProperties': This element is not expected. Expected is one of ( {urn:mpeg:dash:schema:mpd:2011}ProducerReferenceTime, {urn:mpeg:dash:schema:mpd:2011}ContentPopularityRate, {urn:mpeg:dash:schema:mpd:2011}Resync, ...` |
| `example_G27.mpd` | `SegmentTimeline/Pattern` | `Element '{urn:mpeg:dash:schema:mpd:2011}Pattern': This element is not expected. Expected is one of ( {urn:mpeg:dash:schema:mpd:2011}S, ##other{urn:mpeg:dash:schema:mpd:2011}* ).` |
| `example_G28-5.mpd` | `RequestParam` (also `ContentSteering`, see note) | `Element '{urn:mpeg:dash:schema:mpd:2011}RequestParam': This element is not expected. Expected is one of ( {urn:mpeg:dash:schema:mpd:2011}Role, {urn:mpeg:dash:schema:mpd:2011}Rating, {urn:mpeg:dash:schema:mpd:2011}Viewpoint, ...` |
| `example_G29-1.mpd` | `ReplacePresentation`, `RequestParam` | `Element '{urn:mpeg:dash:schema:mpd:2011}ReplacePresentation': This element is not expected. Expected is ( ##other{urn:mpeg:dash:schema:mpd:2011}* ).` / `Element '{urn:mpeg:dash:schema:mpd:2011}RequestParam': This element is not expected. Expected is one of ( {urn:mpeg:dash:schema:mpd:2011}Event, ##other{urn:mpeg:dash:schema:mpd:2011}* ).` |
| `example_G29-2.mpd` | `MPD@type="list"`, `ImportedMPD` | `Element '{urn:mpeg:dash:schema:mpd:2011}MPD', attribute 'type': [facet 'enumeration'] The value 'list' is not an element of the set {'static', 'dynamic'}.` / `Element '{urn:mpeg:dash:schema:mpd:2011}ImportedMPD': This element is not expected. Expected is one of ( {urn:mpeg:dash:schema:mpd:2011}BaseURL, ...` |
| `example_K6.4.mpd` | `ClientDataReporting` in `ServiceDescription` | `Element '{urn:mpeg:dash:schema:mpd:2011}ServiceDescription': This element is not expected. Expected is ( ##other{urn:mpeg:dash:schema:mpd:2011}* ).` |

Note: the line numbers the tool prints refer to its re-serialised copy of the MPD, not to
the input file, and the tool lists fewer errors than a direct validation. Validating the
same files directly against the tool's `DASH5th.xsd` (lxml) gives the same 8 files, plus
`ContentSteering` in G28-5 and `ClientDataReporting` (lines 9 and 17) in K6.4.

### Expected

A 6th-edition MPD that is valid against the ISO 6th-edition schema passes the tool's
schema test, i.e. the test validates against the 6th-edition `DASH-MPD.xsd` (or the
edition the MPD is written for). Per #563, the XSD validation now runs in PHP/libxml
and the `.xsd` files can be replaced.

### Related observations on the same 41 files (can be split out if preferred)

- **Profile list:** the schematron assertion "At least one unknown profile string found.
  Known list in schematron file." fails on 9 examples, for
  `urn:mpeg:dash:profile:advanced-linear:2025` (G26-1, G26-2, G27, G28-1, G28-2, G28-5,
  G29-1, K6.4) and `urn:mpeg:dash:profile:list:2024` (G29-2).
- **Schematron does not run** on G10, H1 and H2 ("Unable to run schematron"):
  `Type error at char 579 in expression in xsl:when/@test on line 1823 column 808 of val_schema.xsl: XPTY0004 A seq...`
- **The CLI aborts with no report** on three examples:
  G11 (`In XLink.php line 28: file_get_contents(example_G11_remote.period.xml): Failed to open stream`, a relative xlink),
  G12 (`In UriString.php line 572: The uri '%20http://example.com/1/' contains an invalid scheme`),
  G13-2 (`In Uri.php line 791: The path mimetype '/video/mp4' is invalid.`).

### How to reproduce

```bash
curl -LO https://standards.iso.org/iso-iec/23009/-1/ed-6/en/DASHSchema-6th-Ed.zip
unzip DASHSchema-6th-Ed.zip
# for each example_*.mpd:
php artisan app:analyze-manifest /path/to/example_G23.mpd "Global Module"
# -> MPD / Global - XSD / DASH 5th / "MPD SHALL be valid": FAIL
```

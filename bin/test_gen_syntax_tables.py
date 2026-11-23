#!/usr/bin/env python3
"""gen-syntax-tables: the §5 tables are generated from the schemas and
syntax.yaml, each cross-check can fail, and each way the source can be wrong
is caught with its own exit.

Unit tests feed each cross-check a cell that agrees and one that does not.
End-to-end negatives copy spec-source/ (and, for base rows, ISO's schema) into
a private temporary directory, break one thing, and run --check.
Run: python3 bin/test_gen_syntax_tables.py
"""
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
SRC = os.path.join(ROOT, "spec-source")
DIST = os.path.join(ROOT, "dist", "sgai-spec.md")
SCRIPT = os.path.join(BIN, "gen-syntax-tables.py")

_spec = importlib.util.spec_from_file_location("gst", SCRIPT)
g = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g)

try:
    sys.path.insert(0, BIN)
    from conformance import iso as _iso
    ISO = str(_iso.materialise())
except Exception as e:  # noqa: BLE001 — any reason means: cannot run base-row tests
    ISO = None
    ISO_WHY = str(e)


def run(*args):
    p = subprocess.run([sys.executable, "-I", SCRIPT, *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def attr(required=False, default=None, type_="xs:string"):
    return {"required": required, "default": default, "type": type_, "prohibited": False}


class Presence(unittest.TestCase):
    def test_m_needs_required(self):
        self.assertEqual(g.check_presence("M", attr(required=True)), [])
        self.assertTrue(g.check_presence("M", attr()))

    def test_od_needs_optional(self):
        self.assertEqual(g.check_presence("OD", attr(default="0")), [])
        self.assertEqual(g.check_presence("OD", attr()), [])      # semantic default
        self.assertTrue(g.check_presence("OD", attr(required=True)))

    def test_o_needs_optional_without_default(self):
        self.assertEqual(g.check_presence("O", attr()), [])
        self.assertTrue(g.check_presence("O", attr(required=True)))
        self.assertTrue(g.check_presence("O", attr(default="x")))

    def test_cm_and_dash_need_optional(self):
        for code in ("CM", "—"):
            self.assertEqual(g.check_presence(code, attr()), [])
            self.assertTrue(g.check_presence(code, attr(required=True)), code)

    def test_unknown_code(self):
        self.assertTrue(g.check_presence("R", attr()))


class Cells(unittest.TestCase):
    def test_type(self):
        self.assertEqual(g.check_type("`LinearRelationType` (§5.1.6) <!-- c -->", "LinearRelationType"), [])
        self.assertTrue(g.check_type("`OnTopOnlyType`", "LinearRelationType"))
        self.assertTrue(g.check_type("a prose type", "xs:string"))

    def test_default_schema_declares(self):
        self.assertEqual(g.check_default("`0` (base)", "0"), [])
        self.assertTrue(g.check_default("`1`", "0"))
        self.assertTrue(g.check_default("infinity", "2251799813685247"))
        self.assertTrue(g.check_default("—", "0"))

    def test_default_schema_silent(self):
        self.assertEqual(g.check_default("the family default (§3.4.3)", None), [])
        self.assertEqual(g.check_default("—", None), [])
        self.assertTrue(g.check_default("`never`", None))

    def test_cardinality(self):
        self.assertEqual(g.check_cardinality("0 … N", {"min": "0", "max": "unbounded"}), [])
        self.assertEqual(g.check_cardinality("0 … 1 each", {"min": "0", "max": "1"}), [])
        self.assertTrue(g.check_cardinality("1 … N", {"min": "0", "max": "unbounded"}))
        self.assertTrue(g.check_cardinality("0 … 1", {"min": "0", "max": "unbounded"}))
        self.assertTrue(g.check_cardinality("0..1", {"min": "0", "max": "1"}))

    def test_enum(self):
        self.assertEqual(g.check_enum(["*(absent)*", "`supersede`", "`on-top`"], ["supersede", "on-top"]), [])
        self.assertTrue(g.check_enum(["`supersede`"], ["supersede", "on-top"]))            # missing
        self.assertTrue(g.check_enum(["`a`", "`b`", "`c`"], ["a", "b"]))                    # extra

    def test_union_flattened(self):
        s = g.Schema(b"""<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:t="urn:t">
          <xs:simpleType name="N"><xs:restriction base="xs:token"><xs:enumeration value="never"/></xs:restriction></xs:simpleType>
          <xs:simpleType name="U"><xs:union memberTypes="xs:duration t:N"/></xs:simpleType></xs:schema>""", "t.xsd")
        self.assertEqual(s.enumeration("U"), ["xs:duration", "never"])

    def test_extension_inherits(self):
        s = g.Schema.load(os.path.join(SRC, "syntax", "sgai-extension.xsd"))
        self.assertIn("uri", s.attributes("OverlayPresentationType"))
        self.assertEqual(s.children("AdType")["RenderableAsset"], {"min": "1", "max": "unbounded",
                                                                  "type": "RenderableAssetType"})
        self.assertEqual(s.children("AdType")["AdTitle"]["type"], "xs:string")   # via ref=


@unittest.skipIf(ISO is None, "ISO schema unavailable: cannot tell")
class EndToEnd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = os.path.join(self.tmp.name, "src")
        shutil.copytree(SRC, self.src)
        self.iso = os.path.join(self.tmp.name, "iso")
        shutil.copytree(ISO, self.iso)
        self.findings = os.path.join(self.tmp.name, "findings.md")
        shutil.copy(g.FINDINGS, self.findings)

    def tearDown(self):
        self.tmp.cleanup()

    def check(self):
        return run("--source", self.src, "--iso", self.iso, "--findings", self.findings, "--check")

    def edit(self, rel, old, new, root=None):
        p = os.path.join(root or self.src, rel)
        with open(p, encoding="utf-8", newline="") as fh:
            body = fh.read()
        self.assertEqual(body.count(old), 1, old)
        with open(p, "w", encoding="utf-8", newline="") as fh:
            fh.write(body.replace(old, new))

    def assert_new_disagreement(self, row_fragment):
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("findings.md: not what the generator produces", out)
        code, out = run("--source", self.src, "--iso", self.iso, "--findings", self.findings, "--write")
        self.assertEqual(code, 0, out)
        with open(self.findings, encoding="utf-8") as fh:
            self.assertIn(row_fragment, fh.read())

    # ---- the real tree

    def test_repo_is_green(self):
        code, out = run("--check")
        self.assertEqual(code, 0, out)
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "assemble-spec.py"), "--check", DIST],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout)

    def test_copy_is_green(self):
        code, out = self.check()
        self.assertEqual(code, 0, out)

    # ---- each cross-check, end to end: the schema changes, the table does not

    def test_m_against_optional(self):
        self.edit("syntax/sgai-extension.xsd",
                  '<xs:attribute name="mimeType" type="xs:string" use="required"/>',
                  '<xs:attribute name="mimeType" type="xs:string"/>')
        code, out = self.check()       # derived presence is now O: the fragment differs
        self.assertEqual(code, 1, out)
        self.assertIn("renderable-asset: the fragment on disk", out)
        self.edit("syntax/syntax.yaml", "  - name: mimeType\n", "  - name: mimeType\n    override:\n      required: M\n")
        self.assert_new_disagreement("| renderable-asset | `@mimeType` | presence M | optional |")

    def test_od_against_required(self):
        self.edit("syntax/sgai-extension.xsd",
                  '<xs:attribute name="customRegion" type="svta:PercentRectType"/>',
                  '<xs:attribute name="customRegion" type="svta:PercentRectType" use="required"/>')
        # the derived presence becomes M, the published text no longer matches the fragment
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("overlay-presentation", out)

    def test_od_override_against_required(self):
        # an OD the table insists on (override) against a required attribute
        self.edit("syntax/syntax.yaml", "  - name: customRegion\n",
                  "  - name: customRegion\n    override:\n      required: OD\n")
        self.edit("syntax/sgai-extension.xsd",
                  '<xs:attribute name="customRegion" type="svta:PercentRectType"/>',
                  '<xs:attribute name="customRegion" type="svta:PercentRectType" use="required"/>')
        self.assert_new_disagreement('| overlay-presentation | `@customRegion` | presence OD | use="required" |')

    def test_default_differs(self):
        self.edit("syntax/sgai-extension.xsd",
                  '<xs:attribute name="executeOnce" type="xs:boolean" default="false"/>',
                  '<xs:attribute name="executeOnce" type="xs:boolean" default="true"/>')
        code, out = self.check()       # derived default moves: the fragment differs
        self.assertEqual(code, 1, out)
        self.assertIn("pause-ad-presentation: the fragment on disk", out)
        self.edit("syntax/syntax.yaml",
                  "  - name: executeOnce\n    description: 'When `true`",
                  "  - name: executeOnce\n    override:\n      default: '`false`'\n    description: 'When `true`")
        self.assert_new_disagreement("| pause-ad-presentation | `@executeOnce` | default 'false' | default 'true' |")

    def test_type_differs(self):
        self.edit("syntax/sgai-extension.xsd",
                  '<xs:attribute name="trackingUris" type="svta:URIListType"/>',
                  '<xs:attribute name="trackingUris" type="xs:string"/>')
        self.assert_new_disagreement("| click-through | `@trackingUris` | type 'URIListType' | type 'xs:string' |")

    def test_cardinality_differs(self):
        self.edit("syntax/syntax.yaml", "  - names:\n    - Tracking\n",
                  "  - names:\n    - Tracking\n    override:\n      cardinality: 0 … 1\n")
        # identical to the derived text: refused
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("equals the derived text", out)
        self.edit("syntax/sgai-extension.xsd",
                  '<xs:element name="Tracking" type="dash:EventStreamType" minOccurs="0"/>',
                  '<xs:element name="Tracking" type="dash:EventStreamType" minOccurs="0" maxOccurs="unbounded"/>')
        self.assert_new_disagreement("| ad-children | `Tracking` | cardinality '0 … 1' | cardinality '0 … N' |")

    def test_element_type_differs(self):
        for n in ("AdSystem", "AdTitle", "Advertiser"):   # all three: ad-children groups them
            self.edit("syntax/sgai-extension.xsd", f'<xs:element name="{n}" type="xs:string"/>',
                      f'<xs:element name="{n}" type="xs:token"/>')
            self.edit("syntax/syntax.yaml", f"  - names:\n    - {n}\n    description",
                      f"  - names:\n    - {n}\n    override:\n      type: '`xs:string`'\n    description")
        self.assert_new_disagreement("| metadata-elements | `AdTitle` | type 'xs:string' | type 'xs:token' |")

    def test_enum_value_added(self):
        self.edit("syntax/sgai-extension.xsd", '<xs:enumeration value="request-again"/>',
                  '<xs:enumeration value="request-again"/>\n      <xs:enumeration value="loop"/>')
        self.assert_new_disagreement("| on-exhausted-values | `(value column)` | no row | value 'loop' enumerated |")

    def test_enum_value_removed(self):
        self.edit("syntax/sgai-extension.xsd",
                  '      <xs:enumeration value="pause"/>\n    </xs:restriction>\n  </xs:simpleType>\n\n  <xs:simpleType name="OnExhaustedType">',
                  '    </xs:restriction>\n  </xs:simpleType>\n\n  <xs:simpleType name="OnExhaustedType">')
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("does not enumerate 'pause'", out)

    def test_union_member_removed(self):
        self.edit("syntax/sgai-extension.xsd", '<xs:union memberTypes="xs:duration svta:NeverType"/>',
                  '<xs:union memberTypes="svta:NeverType"/>')
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("does not enumerate 'xs:duration'", out)

    def test_completeness(self):
        self.edit("syntax/sgai-extension.xsd",
                  '<xs:attribute name="background" type="xs:anyURI"/>',
                  '<xs:attribute name="background" type="xs:anyURI"/>\n    <xs:attribute name="zOrder" type="xs:int"/>')
        self.assert_new_disagreement("| renderable-asset | attribute @zOrder of RenderableAssetType |")

    # ---- base rows against ISO

    def test_base_default_differs(self):
        self.edit("DASH-MPD.xsd", '<xs:attribute name="noJump" type="xs:integer" default="0"/>',
                  '<xs:attribute name="noJump" type="xs:integer" default="1"/>', root=self.iso)
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("insert-presentation: the fragment on disk", out)
        self.edit("syntax/syntax.yaml", "  - name: noJump\n",
                  "  - name: noJump\n    override:\n      default: '`0`'\n")
        self.assert_new_disagreement("| insert-presentation | `@noJump` | default '0' | default '1' |")

    def test_base_type_differs(self):
        self.edit("DASH-MPD.xsd", '<xs:attribute name="status" type="EventStatusType" default="repeat"/>',
                  '<xs:attribute name="status" type="xs:string" default="repeat"/>', root=self.iso)
        self.edit("syntax/syntax.yaml", "  - name: status\n",
                  "  - name: status\n    override:\n      type: '`EventStatusType`'\n")
        self.assert_new_disagreement("| overlay-window-event-usage | `Event@status` | type 'EventStatusType' | type 'xs:string' |")

    def test_base_required_differs(self):
        self.edit("DASH-MPD.xsd", '<xs:attribute name="duration" type="xs:unsignedLong"/>\n    <xs:attribute name="id"',
                  '<xs:attribute name="duration" type="xs:unsignedLong" use="required"/>\n    <xs:attribute name="id"',
                  root=self.iso)
        code, out = self.check()
        self.assertEqual(code, 1, out)   # the M override now equals the derived text
        self.assertIn("equals the derived text", out)

    # ---- source errors

    def test_fragment_edited(self):
        self.edit("syntax/tables/overlay-list.md", "| `@family` | M |", "| `@family` | O |")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("overlay-list: the fragment on disk", out)

    def test_fragment_missing_and_stale(self):
        os.rename(os.path.join(self.src, "syntax/tables/tracking.md"),
                  os.path.join(self.src, "syntax/tables/tracking-old.md"))
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("tracking: no fragment on disk", out)
        self.assertIn("tracking-old: a fragment on disk that syntax.yaml does not declare", out)

    def test_directive_missing_or_doubled(self):
        self.edit("sgai-spec.src.md", "{{include:syntax/tables/family-values.md}}\n", "")
        self.edit("sgai-spec.src.md", "{{include:syntax/tables/tracking.md}}\n",
                  "{{include:syntax/tables/tracking.md}}\n{{include:syntax/tables/tracking.md}}\n")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("family-values: the prose includes it 0 times", out)
        self.assertIn("tracking: the prose includes it 2 times", out)

    def test_unknown_attribute(self):
        p = os.path.join(self.src, "syntax/syntax.yaml")
        with open(p, encoding="utf-8") as fh:
            body = fh.read()
        with open(p, "w", encoding="utf-8") as fh:
            fh.write(body.replace("  - name: durationCap\n", "  - name: durationKap\n"))
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("has no attribute durationKap", out)

    def test_yaml_cannot_declare_m(self):
        self.edit("syntax/syntax.yaml", "  - name: rect\n    required: CM\n", "  - name: rect\n    required: M\n")
        code, out = self.check()
        self.assertEqual(code, 1, out)
        self.assertIn("may only declare CM or —", out)

    def test_findings_missing(self):
        os.remove(self.findings)
        code, out = self.check()
        self.assertEqual(code, 1, out)

    def test_yaml_missing(self):
        os.remove(os.path.join(self.src, "syntax/syntax.yaml"))
        code, out = self.check()
        self.assertEqual(code, 2, out)

    def test_iso_missing(self):
        os.remove(os.path.join(self.iso, "DASH-MPD.xsd"))
        code, out = self.check()
        self.assertEqual(code, 2, out)

    def test_command_line(self):
        self.assertEqual(run()[0], 64)
        self.assertEqual(run("--check", "--write")[0], 64)
        self.assertEqual(run("--bogus")[0], 64)
        self.assertEqual(run("--source")[0], 64)


if __name__ == "__main__":
    if ISO is None:
        print(f"ISO schema unavailable ({ISO_WHY}): end-to-end tests skipped", file=sys.stderr)
    unittest.main()

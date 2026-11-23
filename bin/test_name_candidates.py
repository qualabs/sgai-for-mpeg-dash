#!/usr/bin/env python3
"""name-candidates: each match rule fires on its side of the threshold and not
on the other, declarations carry their line and context, sections are found
by the mention forms --help names, the exits 2 and 64 mean what --help says,
and on the real schemas the entries checked by hand against ISO's XSD are
there.

Run: python3 bin/test_name_candidates.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
SCRIPT = os.path.join(BIN, "name-candidates.py")

_spec = importlib.util.spec_from_file_location("name_candidates", SCRIPT)
nc = importlib.util.module_from_spec(_spec)
sys.modules["name_candidates"] = nc
_spec.loader.exec_module(nc)

HEAD = ('<?xml version="1.0"?>\n'
        '<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">\n')

BASE = HEAD + """  <xs:complexType name="EventType">
    <xs:attribute name="duration" type="xs:unsignedLong"/>
    <xs:attribute name="maxDuration" type="xs:unsignedLong"/>
    <xs:attribute ref="href"/>
  </xs:complexType>
  <xs:element name="Wrapper">
    <xs:complexType>
      <xs:attribute name="Region" type="xs:string"/>
    </xs:complexType>
  </xs:element>
  <xs:simpleType name="StatusType">
    <xs:restriction base="xs:string">
      <xs:enumeration value="repeat"/>
      <xs:enumeration value="update"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:attribute name="Representation" type="xs:string"/>
</xs:schema>
"""

OURS = HEAD + """  <xs:complexType name="OurType">
    <xs:attribute name="duration" type="xs:duration"/>
    <xs:attribute name="region" type="xs:string"/>
    <xs:attribute name="href" type="xs:anyURI"/>
  </xs:complexType>
  <xs:simpleType name="ModeType">
    <xs:restriction base="xs:token">
      <xs:enumeration value="repeat"/>
      <xs:enumeration value="duration"/>
    </xs:restriction>
  </xs:simpleType>
  <xs:element name="Lonely" type="xs:string"/>
</xs:schema>
"""

SPEC = """# Spec

## 1. Scope

The `@duration` and the `<svta:Lonely>` element.

## 2. Other

Mode `"repeat"` and @durationCap; Lonely as a word; OurType here.

## 3. Third

`Lonely` and svta:Lonely and duration without at, repeat unquoted.
"""


def write(d, name, text):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


def run(*args):
    r = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


class Match(unittest.TestCase):
    def test_exact_and_case(self):
        self.assertEqual(nc.match("duration", "duration"), "exact")
        self.assertEqual(nc.match("region", "Region"), "case")

    def test_suffix_needs_a_word_boundary(self):
        self.assertEqual(nc.match("AdType", "Ad"), "suffix")
        self.assertEqual(nc.match("OverlayPresentationType", "OverlayPresentation"), "suffix")
        self.assertEqual(nc.match("OverlayPresentation", "Overlay"), "suffix")
        self.assertEqual(nc.match("URLType", "URL"), "suffix")
        self.assertEqual(nc.words("overlay-corner"), ["overlay", "corner"])
        # `presentation` inside one word is not a suffix: no stem `re`
        self.assertEqual(nc.stem("Representation"), "representation")
        self.assertIsNone(nc.match("Re", "Representation"))

    def test_edit_distance_threshold(self):
        self.assertEqual(nc.levenshtein("abcdef", "abcdxy"), 2)
        self.assertEqual(nc.match("abcdef", "abcdxy"), "edit")      # 6 chars, distance 2
        self.assertIsNone(nc.match("abcdef", "abcxyz"))             # distance 3
        self.assertIsNone(nc.match("abcde", "abcdx"))               # 5 chars, distance 1
        self.assertEqual(nc.match("abcdefType", "abcdxyType"), "edit")  # on stems
        self.assertIsNone(nc.match("AdType", "SAPType"))            # shared Type does not count
        self.assertEqual(nc.match("abcdefPresentationType", "abcdxy"), "edit")  # names far, stems close

    def test_affix_threshold(self):
        self.assertEqual(nc.match("durationCap", "duration"), "affix")
        self.assertEqual(nc.match("AdTitle", "Title"), "affix")     # shorter stem 5 chars
        self.assertIsNone(nc.match("AdName", "Name"))               # shorter stem 4 chars
        self.assertIsNone(nc.match("myDurationCap", "duration"))    # two extra words
        self.assertIsNone(nc.match("capDurationMax", "durationMin"))

    def test_strongest_wins(self):
        self.assertEqual(nc.match("durationType", "duration"), "suffix")


class Candidates(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.tmp.name
        self.base = write(d, "base.xsd", BASE)
        self.ours = write(d, "ours.xsd", OURS)
        self.spec = write(d, "spec.md", SPEC)

    def tearDown(self):
        self.tmp.cleanup()

    def out(self):
        code, stdout, err = run("--ours", self.ours, "--iso", self.base, "--spec", self.spec, "--json")
        self.assertEqual(code, 0, err)
        return json.loads(stdout)

    def by(self, data):
        return {(c["kind"], c["name"]): c for c in data["candidates"]}

    def test_list(self):
        c = self.by(self.out())
        self.assertEqual(set(c), {("attribute", "duration"), ("attribute", "region"),
                                  ("enumeration", "repeat")})

    def test_a_reference_declares_nothing(self):
        # base has <xs:attribute ref="href"/>, ours declares href
        self.assertNotIn(("attribute", "href"), self.by(self.out()))

    def test_pools_do_not_mix(self):
        # the enumeration value "duration" matches no attribute `duration`
        self.assertNotIn(("enumeration", "duration"), self.by(self.out()))

    def test_declaration_line_context_type(self):
        c = self.by(self.out())[("attribute", "duration")]
        self.assertEqual(c["declared"], [{"context": "OurType", "type": "xs:duration", "line": 4}])
        m = {x["iso_name"]: x for x in c["matches"]}
        self.assertEqual(m["duration"]["match"], "exact")
        self.assertEqual(m["duration"]["declarations"],
                         [{"kind": "attribute", "type": "xs:unsignedLong",
                           "context": "EventType", "line": 4}])
        self.assertEqual(m["maxDuration"]["match"], "affix")
        self.assertEqual(c["strongest"], "exact")
        self.assertEqual([x["iso_name"] for x in c["matches"]], ["duration", "maxDuration"])

    def test_anonymous_type_context_is_its_element(self):
        c = self.by(self.out())[("attribute", "region")]
        self.assertEqual(c["matches"][0]["declarations"][0]["context"], "Wrapper")
        self.assertEqual(c["matches"][0]["match"], "case")

    def test_enumeration_type_is_its_simple_type(self):
        c = self.by(self.out())[("enumeration", "repeat")]
        self.assertEqual(c["declared"][0]["type"], "ModeType")
        self.assertEqual(c["matches"][0]["declarations"][0]["line"], 15)

    def test_sections_by_mention_form(self):
        c = self.by(self.out())
        self.assertEqual(c[("attribute", "duration")]["sections"], ["1"])   # not @durationCap, not bare
        self.assertEqual(c[("enumeration", "repeat")]["sections"], ["2"])
        secs = nc.spec_sections.split(SPEC)
        self.assertEqual(nc.sections_of("Lonely", "element", secs), ["1", "3"])  # not the bare word
        self.assertEqual(nc.sections_of("OurType", "type", secs), ["2"])
        self.assertEqual(nc.sections_of("absent", "attribute", secs), [])

    def test_empty_list_is_exit_0(self):
        empty = write(self.tmp.name, "empty.xsd", HEAD + "</xs:schema>\n")
        code, stdout, _ = run("--ours", empty, "--iso", self.base, "--spec", self.spec, "--json")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout)["count"], 0)

    def test_text_output(self):
        code, stdout, _ = run("--ours", self.ours, "--iso", self.base, "--spec", self.spec)
        self.assertEqual(code, 0)
        self.assertIn("3 of", stdout)
        self.assertIn("exact  duration: attribute in EventType: xs:unsignedLong (line 4)", stdout)


class Exits(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = self.tmp.name
        self.base = write(d, "base.xsd", BASE)
        self.ours = write(d, "ours.xsd", OURS)
        self.spec = write(d, "spec.md", SPEC)

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_ours_is_2(self):
        code, _, err = run("--ours", os.path.join(self.tmp.name, "nope.xsd"),
                           "--iso", self.base, "--spec", self.spec)
        self.assertEqual(code, 2)
        self.assertIn("cannot tell", err)

    def test_malformed_iso_is_2(self):
        bad = write(self.tmp.name, "bad.xsd", HEAD + "<xs:element")
        self.assertEqual(run("--ours", self.ours, "--iso", bad, "--spec", self.spec)[0], 2)

    def test_missing_spec_is_2(self):
        self.assertEqual(run("--ours", self.ours, "--iso", self.base,
                             "--spec", os.path.join(self.tmp.name, "x.md"))[0], 2)

    def test_unsplittable_spec_is_2(self):
        dup = write(self.tmp.name, "dup.md", "## 1. A\n\n## 1. B\n")
        self.assertEqual(run("--ours", self.ours, "--iso", self.base, "--spec", dup)[0], 2)

    def test_iso_unavailable_is_2(self):
        env = dict(os.environ, SGAI_CONFORMANCE_CACHE=os.path.join(self.tmp.name, "cache"),
                   SGAI_CONFORMANCE_OFFLINE="1")
        r = subprocess.run([sys.executable, SCRIPT, "--ours", self.ours, "--spec", self.spec],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("ISO's schema", r.stderr)

    def test_usage_is_64(self):
        self.assertEqual(run("--bogus")[0], 64)
        self.assertEqual(run("--iso")[0], 64)

    def test_help_is_0(self):
        code, stdout, _ = run("--help")
        self.assertEqual(code, 0)
        self.assertIn("Exit codes", stdout)


def iso_available():
    sys.path.insert(0, BIN)
    from conformance import iso
    try:
        iso.materialise()
        return True
    except iso.Unavailable:
        return False


@unittest.skipUnless(iso_available(), "ISO's schema not cached")
class RealSchemas(unittest.TestCase):
    """Entries checked by hand against DASH-MPD.xsd (grep -n of the name)."""

    def test_hand_checked_entries(self):
        code, stdout, err = run("--json")
        self.assertEqual(code, 0, err)
        c = {(x["kind"], x["name"]): x for x in json.loads(stdout)["candidates"]}
        dur = {m["iso_name"]: m for m in c[("attribute", "duration")]["matches"]}
        self.assertEqual(sorted(d["line"] for d in dur["duration"]["declarations"]),
                         [187, 237, 863, 1080])
        self.assertEqual(dur["maxDuration"]["declarations"][0]["line"], 1197)
        title = c[("element", "AdTitle")]["matches"][0]
        self.assertEqual((title["iso_name"], title["match"]), ("Title", "affix"))
        self.assertEqual(title["declarations"][0]["context"], "ProgramInformationType")
        self.assertEqual(title["declarations"][0]["line"], 1041)


if __name__ == "__main__":
    unittest.main()

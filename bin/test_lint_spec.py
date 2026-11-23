#!/usr/bin/env python3
"""lint-spec: a clean synthetic spec exits 0, each rule catches its own
negative, the exits 2 and 64 mean what --help says, and on dist/ the
findings are exactly the ones measured by hand.

Run: python3 bin/test_lint_spec.py
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
DIST = os.path.join(ROOT, "dist", "sgai-spec.md")

CLEAN = """# A spec

**References.** `DASH §n` is the base; a bare `§n` is this document.

## 1. Scope

### 1.1 Covers

See §2 and §1.1, and §A.1. The base says so (DASH
§5.10.2.1), and DASH §5.16.3–DASH §5.16.5 too; RFC 8216 §4.3.1 and
ISO/IEC 23009-1 §3.1 as well. A wrapped span `Event@presentationTime,
<!-- not a comment --> §9.9` is code. Lowercase todo is prose.

## 2. Conformance

- **PUB-1.** The Publisher MUST declare a cap.
- **PLY-2.** The Player MUST honour PUB-1.

Under PLY-2 nothing else.

```xml
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" xmlns:svta="urn:svta:sgai"
     xml:lang="en">
  <!-- an XML comment: <bad:Thing> is not a name here -->
  <svta:Ad svta:id="1"/>
</MPD>
```

```xml
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="Ad" type="xs:string"/>
</xs:schema>
```

```
GET /resolve?x=1 HTTP/1.1
```

# Annexes

## Annex A — Pre-roll

### A.1 The scenario

Nothing more.
"""


def run(*args):
    p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "lint-spec.py"), *args],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class Lint(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def doc(self, text, name="spec.md", raw=None):
        path = os.path.join(self.tmp.name, name)
        with open(path, "wb") as fh:
            fh.write(raw if raw is not None else text.encode("utf-8"))
        return path

    def findings(self, text):
        code, out = run(self.doc(text), "--json")
        return code, json.loads(out)

    def assertOnly(self, text, rule, n=1):
        code, data = self.findings(text)
        self.assertEqual(code, 1, data)
        rules = [f["rule"] for f in data["findings"]]
        self.assertEqual(rules, [rule] * n, data)
        return data["findings"]

    # --- the clean document -------------------------------------------
    def test_clean_exits_0(self):
        code, out = run(self.doc(CLEAN))
        self.assertEqual(code, 0, out)
        self.assertIn("CLEAN", out)

    # --- L-REF ---------------------------------------------------------
    def test_ref_unresolved(self):
        f = self.assertOnly(CLEAN.replace("See §2 and", "See §7 and"), "L-REF")
        self.assertEqual(f[0]["line"], 9)
        self.assertIn("§7", f[0]["text"])

    def test_ref_annex_unresolved(self):
        self.assertOnly(CLEAN.replace("and §A.1.", "and §A.2."), "L-REF")

    def test_ref_deeper_than_any_heading_does_not_resolve(self):
        self.assertOnly(CLEAN.replace("and §1.1,", "and §1.1.1,"), "L-REF")

    def test_ref_previous_line_prefix_honoured_and_needed(self):
        # The wrapped "(DASH\n§5.10.2.1)" is clean; without the prefix it is not.
        self.assertOnly(CLEAN.replace("(DASH\n§5.10.2.1)", "(see\n§5.10.2.1)"), "L-REF")

    def test_ref_range_second_end_needs_prefix(self):
        self.assertOnly(CLEAN.replace("§5.16.3–DASH §5.16.5", "§5.16.3–§5.16.5"), "L-REF")

    def test_ref_standard_number_prefix_needed(self):
        self.assertOnly(CLEAN.replace("RFC 8216 §4.3.1", "RFC 8216, §4.3.1"), "L-REF")

    def test_ref_in_list_after_prefixed_is_bare(self):
        # The document's own convention: a bare § is this document's.
        self.assertOnly(CLEAN.replace("(DASH\n§5.10.2.1)", "(DASH\n§5.10.2.1, §5.10.2.2)"), "L-REF")

    # --- L-ID ----------------------------------------------------------
    def test_id_duplicate(self):
        f = self.assertOnly(CLEAN.replace("- **PLY-2.**", "- **PUB-1.**").replace("PLY-2 nothing", "PUB-1 nothing"), "L-ID")
        self.assertIn("defined again", f[0]["text"])

    def test_id_dangling(self):
        f = self.assertOnly(CLEAN.replace("honour PUB-1.", "honour PUB-9."), "L-ID")
        self.assertIn("PUB-9", f[0]["text"])

    def test_id_dangling_inside_code(self):
        self.assertOnly(CLEAN.replace("GET /resolve?x=1", "GET /resolve?x=APS-3"), "L-ID")

    def test_id_each_family(self):
        for fam in ("PUB", "PLY", "APS", "DOC", "ADS"):
            self.assertOnly(CLEAN.replace("Nothing more.", f"Nothing more than {fam}-77."), "L-ID")

    # --- L-NS ----------------------------------------------------------
    def test_ns_element_prefix_undeclared(self):
        f = self.assertOnly(CLEAN.replace('  <svta:Ad svta:id="1"/>', '  <svta:Ad svta:id="1"/>\n  <scte:Signal/>'), "L-NS")
        self.assertIn("'scte'", f[0]["text"])

    def test_ns_attribute_prefix_undeclared(self):
        self.assertOnly(CLEAN.replace('<svta:Ad svta:id="1"/>', '<svta:Ad foo:id="1"/>'), "L-NS")

    def test_ns_declaration_is_per_block(self):
        self.assertOnly(CLEAN.replace(' xmlns:svta="urn:svta:sgai"', ""), "L-NS")

    def test_ns_xs_not_exempt(self):
        self.assertOnly(CLEAN.replace('<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">', "<xs:schema>"), "L-NS")

    # --- L-DRAFT -------------------------------------------------------
    def test_draft_in_prose(self):
        for word in ("TODO", "TBD", "FIXME", "XXX"):
            self.assertOnly(CLEAN.replace("Nothing more.", f"Nothing more {word}."), "L-DRAFT")

    def test_draft_in_code(self):
        self.assertOnly(CLEAN.replace("GET /resolve?x=1", "GET /resolve?x=TODO"), "L-DRAFT")

    # --- L-COMMENT -----------------------------------------------------
    def test_comment_own_line(self):
        f = self.assertOnly(CLEAN.replace("Nothing more.", "<!-- refine: X-1 -->\nNothing more."), "L-COMMENT")
        self.assertIn("refine: X-1", f[0]["text"])

    def test_comment_inline_and_multiline(self):
        f = self.assertOnly(CLEAN.replace("Nothing more.", "Nothing <!-- delta:\n abc --> more."), "L-COMMENT")
        self.assertEqual(f[0]["text"], "<!-- delta: abc -->")

    def test_comment_unterminated(self):
        f = self.assertOnly(CLEAN.replace("Nothing more.", "Nothing <!-- more."), "L-COMMENT")
        self.assertIn("unterminated", f[0]["text"])

    # --- L-GAPS --------------------------------------------------------
    def test_gaps_heading(self):
        f = self.assertOnly(CLEAN + "\n## Refinement gaps\n\nNone.\n", "L-GAPS")
        self.assertEqual(f[0]["text"], "## Refinement gaps")

    # --- exits 2 and 64 ------------------------------------------------
    def test_missing_file_is_2(self):
        self.assertEqual(run(os.path.join(self.tmp.name, "absent.md"))[0], 2)

    def test_empty_is_2(self):
        self.assertEqual(run(self.doc(""))[0], 2)

    def test_not_a_spec_is_2(self):
        self.assertEqual(run(self.doc(CLEAN.replace("## 1. Scope", "## Scope")))[0], 2)

    def test_heading_one_inside_code_is_not_a_spec(self):
        text = CLEAN.replace("## 1. Scope", "```\n## 1. Scope\n```")
        self.assertEqual(run(self.doc(text))[0], 2)

    def test_open_fence_is_2(self):
        self.assertEqual(run(self.doc(CLEAN + "\n```xml\n<a/>\n"))[0], 2)

    def test_not_utf8_is_2(self):
        self.assertEqual(run(self.doc(None, raw=b"## 1. Scope\n\xff\xfe\n"))[0], 2)

    def test_cannot_tell_json(self):
        code, out = run(self.doc("hello"), "--json")
        self.assertEqual((code, json.loads(out)["verdict"]), (2, "CANNOT TELL"))

    def test_command_line_64(self):
        self.assertEqual(run()[0], 64)
        self.assertEqual(run("a.md", "b.md")[0], 64)
        self.assertEqual(run("--bogus")[0], 64)

    def test_help_states_coverage(self):
        code, out = run("--help")
        self.assertEqual(code, 0)
        self.assertIn("does NOT cover", out)

    # --- the real document ---------------------------------------------
    @unittest.skipUnless(os.path.isfile(DIST), "dist/sgai-spec.md absent")
    def test_dist_exact_findings(self):
        code, out = run(DIST, "--json")
        data = json.loads(out)
        self.assertEqual(code, 1)
        self.assertEqual(data["counts"], {"L-COMMENT": 72, "L-GAPS": 1, "L-REF": 1})
        comments = [f["text"] for f in data["findings"] if f["rule"] == "L-COMMENT"]
        self.assertEqual(sum(c.startswith("<!-- refine") for c in comments), 38)
        self.assertEqual(sum(c.startswith("<!-- delta") for c in comments), 34)
        by = {(f["rule"], f["line"]) for f in data["findings"]}
        self.assertIn(("L-GAPS", 7462), by)
        self.assertIn(("L-REF", 2156), by)
        self.assertEqual(data["stats"]["ids_defined"], 173)
        self.assertEqual(data["stats"]["xml_blocks"], 84)


if __name__ == "__main__":
    unittest.main()

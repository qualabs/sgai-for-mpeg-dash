#!/usr/bin/env python3
"""apply-spec-patch and spec-section: a patch changes exactly what it
declares, and each thing a patch may not do is refused with nothing written.

Every case works on a private copy of spec-source/sgai-spec.src.md.
Run: python3 bin/test_apply_spec_patch.py
"""
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
SRC = os.path.join(ROOT, "spec-source", "sgai-spec.src.md")
sys.path.insert(0, BIN)
import spec_sections as ss  # noqa: E402

spec = importlib.util.spec_from_file_location("asp", os.path.join(BIN, "apply-spec-patch.py"))
asp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(asp)


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


class Patch(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = os.path.join(self.tmp.name, "src.md")
        shutil.copy(SRC, self.src)
        with open(self.src) as fh:
            self.text = fh.read()
        self.secs = ss.by_key(ss.split(self.text))

    def tearDown(self):
        self.tmp.cleanup()

    def run_patch(self, ops, *extra):
        p = os.path.join(self.tmp.name, "p.json")
        with open(p, "w") as fh:
            json.dump({"ops": ops}, fh)
        before = sha(self.src)
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = asp.main([p, "--source", self.src, *extra])
        return code, buf.getvalue(), before != sha(self.src)

    def changed(self):
        with open(self.src) as fh:
            new = fh.read()
        return asp.changed_keys(self.text, new)[0]

    # --- what is allowed -------------------------------------------------
    def test_find_replace_changes_only_its_section(self):
        code, out, wrote = self.run_patch([{"section": "5.1.3", "find": "What the span means.",
                                            "replace": "What the span denotes.", "reason": "t"}])
        self.assertEqual(code, 0, out)
        self.assertTrue(wrote)
        self.assertEqual(self.changed(), ["5.1.3"])

    def test_insert_and_delete(self):
        code, out, _ = self.run_patch([
            {"insert_after": "5.1.7", "section_text": "#### 5.1.8 New\n\nText.\n\n", "reason": "t"},
            {"delete_section": "1.3", "reason": "t"}])
        self.assertEqual(code, 0, out)
        self.assertEqual(self.changed(), ["1.3", "5.1.8"])

    def test_replace_section_keeps_key(self):
        code, out, _ = self.run_patch([{"section": "1.3", "replace_section": "### 1.3 Same key\n\nNew body.\n\n",
                                        "reason": "t"}])
        self.assertEqual(code, 0, out)
        self.assertEqual(self.changed(), ["1.3"])

    def test_new_directive_line_is_allowed(self):
        code, out, _ = self.run_patch([{"section": "1.3", "find": self.secs["1.3"].lines[1] if self.secs["1.3"].lines[1].strip() else self.secs["1.3"].lines[2],
                                        "replace": "{{example:annex-a/A.2-1.mpd}}\n", "reason": "t"}], "--dry-run")
        self.assertEqual(code, 0, out)

    def test_dry_run_and_record(self):
        code, out, wrote = self.run_patch([{"section": "5.1.3", "find": "What the span means.",
                                            "replace": "X.", "reason": "t"}], "--dry-run")
        self.assertEqual((code, wrote), (0, False), out)
        rec = os.path.join(self.tmp.name, "rec.json")
        code, out, wrote = self.run_patch([{"section": "5.1.3", "find": "What the span means.",
                                            "replace": "X.", "reason": "t"}], "--record", rec)
        with open(rec) as fh:
            r = json.load(fh)
        self.assertEqual(r["sections_changed"], ["5.1.3"])
        self.assertEqual(r["source_sha256_after"], sha(self.src))

    # --- what is refused, with nothing written ---------------------------
    def refused(self, ops, *extra, word=""):
        code, out, wrote = self.run_patch(ops, *extra)
        self.assertEqual(code, 1, out)
        self.assertFalse(wrote)
        self.assertIn(word, out)

    def test_find_absent(self):
        self.refused([{"section": "5.1.3", "find": "no such text", "replace": "x", "reason": "t"}], word="0 times")

    def test_find_twice(self):
        self.refused([{"section": "5.1.3", "find": "the", "replace": "x", "reason": "t"}], word="times")

    def test_find_on_directive(self):
        line = [l for l in self.secs["5.1.7"].lines if l.startswith("{{")][0]
        self.refused([{"section": "5.1.7", "find": line, "replace": "x\n", "reason": "t"}], word="directive")

    def test_replace_adds_heading(self):
        self.refused([{"section": "5.1.3", "find": "What the span means.",
                       "replace": "x\n\n#### 5.1.3a Sneaky\n", "reason": "t"}], word="heading")

    def test_replace_section_other_key(self):
        self.refused([{"section": "1.3", "replace_section": "### 1.4 Other\n\nx\n", "reason": "t"}])

    def test_replace_section_drops_directive(self):
        self.refused([{"section": "5.1.7", "replace_section": "#### 5.1.7 A window, in short\n\nNo example.\n",
                       "reason": "t"}], word="directive")

    def test_insert_existing_key(self):
        self.refused([{"insert_after": "1.3", "section_text": "### 1.4 Dup\n\nx\n", "reason": "t"}], word="exists")

    def test_delete_section_with_directive(self):
        self.refused([{"delete_section": "5.1.7", "reason": "t"}], word="directive")

    def test_no_reason(self):
        self.refused([{"section": "5.1.3", "find": "What the span means.", "replace": "x"}], word="reason")

    def test_max_fraction(self):
        self.refused([{"section": "5.1.3", "find": "What the span means.", "replace": "x", "reason": "t"}],
                     "--max-fraction", "0.0001", word="MAJOR")

    def test_undeclared_change_is_caught(self):
        real = asp.apply

        def leaky(text, ops):
            new, declared = real(text, ops)
            return new.replace("## 2. Normative references", "## 2. Normative refs", 1), declared
        asp.apply = leaky
        try:
            self.refused([{"section": "5.1.3", "find": "What the span means.", "replace": "x", "reason": "t"}],
                         word="changed without being declared")
        finally:
            asp.apply = real

    def test_unreadable_and_cli(self):
        bad = os.path.join(self.tmp.name, "bad.json")
        open(bad, "w").write("{")
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "apply-spec-patch.py"), bad, "--source", self.src],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "apply-spec-patch.py")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 64)


class FileOps(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = os.path.join(self.tmp.name, "spec-source")
        shutil.copytree(os.path.join(ROOT, "spec-source"), self.dir)
        os.makedirs(os.path.join(self.dir, "syntax", "tables"), exist_ok=True)
        open(os.path.join(self.dir, "syntax", "tables", "t.md"), "w").write("| a |\n")
        self.src = os.path.join(self.dir, "sgai-spec.src.md")
        self.fx = os.path.join(self.dir, "examples", "annex-c", "C.2-1.mpd")

    def tearDown(self):
        self.tmp.cleanup()

    def run_patch(self, ops):
        p = os.path.join(self.tmp.name, "p.json")
        with open(p, "w") as fh:
            json.dump({"ops": ops}, fh)
        before = (sha(self.src), sha(self.fx))
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = asp.main([p, "--source", self.src])
        return code, buf.getvalue(), before != (sha(self.src), sha(self.fx))

    def test_fixture_edit(self):
        code, out, wrote = self.run_patch([{"file": "examples/annex-c/C.2-1.mpd",
                                            "find": 'xmlns="urn:mpeg:dash:schema:mpd:2011"',
                                            "replace": 'xmlns="urn:mpeg:dash:schema:mpd:2011" ', "reason": "t"}])
        self.assertEqual(code, 0, out)
        self.assertTrue(wrote)
        self.assertIn("examples/annex-c/C.2-1.mpd", out)

    def refused(self, op, word):
        code, out, wrote = self.run_patch([dict(op, reason="t")])
        self.assertEqual(code, 1, out)
        self.assertFalse(wrote)
        self.assertIn(word, out)

    def test_generated_refused(self):
        self.refused({"file": "syntax/tables/t.md", "find": "a", "replace": "b"}, "generated")

    def test_prose_as_file_refused(self):
        self.refused({"file": "sgai-spec.src.md", "find": "## 5. Syntax", "replace": "x"}, "by section")

    def test_outside_refused(self):
        self.refused({"file": "../dist/sgai-spec.md", "find": "a", "replace": "b"}, "not a file of spec-source")

    def test_file_find_twice(self):
        self.refused({"file": "examples/annex-c/C.2-1.mpd", "find": "<", "replace": "<"}, "times")

    def test_file_noop_refused(self):
        self.refused({"file": "examples/annex-c/C.2-1.mpd", "find": "<MPD", "replace": "<MPD"}, "unchanged")


class Sections(unittest.TestCase):
    def test_split_is_lossless_and_keys_unique(self):
        with open(SRC) as fh:
            t = fh.read()
        secs = ss.split(t)
        self.assertEqual(ss.join(secs), t)
        self.assertIn("A.5", ss.by_key(secs))

    def test_repeated_key_cannot_tell(self):
        with self.assertRaises(ss.SectionError):
            ss.split("## 1. A\n\nx\n\n## 1. B\n")

    def test_heading_inside_fence_is_not_a_section(self):
        self.assertEqual([s.key for s in ss.split("## 1. A\n```\n## 2. not\n```\n")], ["1"])

    def test_get_cli(self):
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "spec-section.py"), "get", "1.3"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertTrue(p.stdout.startswith("### 1.3"))
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "spec-section.py"), "get", "99.9"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)


if __name__ == "__main__":
    unittest.main()

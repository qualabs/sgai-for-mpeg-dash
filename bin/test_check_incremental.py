#!/usr/bin/env python3
"""check-incremental: the parts the new pipeline reads (ADR 0066, 0067).

scope: a `## Sections changed` row may name its section by key; every
section a patch record lists must be declared; `cleanup` and `version` rows
must have changed and do not count toward the fraction. anchor: a major
built on spec-source/ records its own `Context head`.

Each case writes two small specs and a trace into private directories and
points the module at them.
Run: python3 bin/test_check_incremental.py
"""
import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
spec = importlib.util.spec_from_file_location("ci", os.path.join(BIN, "check-incremental.py"))
ci = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ci)

def put(path, text):
    with open(path, "w") as fh:
        fh.write(text)


def read(path):
    with open(path) as fh:
        return fh.read()


BODY = "".join("line %d\n" % i for i in range(20))
BASE = ("# Title\n\n**Status:** build iteration 1.\n\n"
        "## 1. Scope\n\n" + BODY +
        "## 2. Terms\n\nshort\n\n"
        "## Annex A Use case\n\nwalk\n")


def head_from(base, **edits):
    t = base
    for a, b in edits.values():
        t = t.replace(a, b, 1)
    return t


def trace(rows, not_placed=()):
    t = ("# v1.1 — context delta applied to v1\n\n- Context head: `abc1234`\n\n"
         "## Not placed\n\n| # | Commit | Context unit | Change | Class | Why |\n|---|---|---|---|---|---|\n")
    t += "".join("| %d | c | u | added | %s | w |\n" % (i, c) for i, c in enumerate(not_placed, 1))
    t += "\n## Sections changed\n\n| Section | Change | Rows |\n|---------|--------|------|\n"
    t += "".join("| %s | %s | 1 |\n" % r for r in rows)
    return t


class Scope(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = os.path.join(self.tmp.name, "output")
        self.an = os.path.join(self.tmp.name, "output-analysis")
        os.makedirs(self.out)
        os.makedirs(self.an)
        self.saved = (ci.OUTPUT, ci.ANALYSIS)
        ci.OUTPUT, ci.ANALYSIS = self.out, self.an

    def tearDown(self):
        ci.OUTPUT, ci.ANALYSIS = self.saved
        self.tmp.cleanup()

    def write(self, head, rows, not_placed=(), records=()):
        put(os.path.join(self.out, "v1-sgai-spec.md"), BASE)
        put(os.path.join(self.out, "v1.1-sgai-spec.md"), head)
        put(os.path.join(self.an, "v1.1-context-delta.md"), trace(rows, not_placed))
        for k, rec in enumerate(records):
            with open(os.path.join(self.an, "v1.1-delta-patch-%d.json" % k), "w") as fh:
                fh.write(rec if isinstance(rec, str) else json.dumps(rec))

    def scope(self, frac=0.30):
        buf = io.StringIO()
        with redirect_stdout(buf):
            try:
                code = ci.scope("v1", "v1.1", frac)
            except ci.CannotTell:
                code = 2
        return code, buf.getvalue()

    def test_rows_by_key(self):
        self.write(BASE.replace("short", "shorter"), [("2", "modified")])
        code, out = self.scope()
        self.assertEqual(code, 0, out)
        self.assertIn("RESULT=IN_SCOPE", out)

    def test_rows_by_heading_text_still_work(self):
        self.write(BASE.replace("short", "shorter"), [("2. Terms", "modified")])
        self.assertEqual(self.scope()[0], 0)

    def test_key_of_unnumbered_and_annex(self):
        self.write(BASE.replace("walk", "walks").replace("**Status:** build iteration 1.", "**Status:** x"),
                   [("Annex A", "modified"), ("Title", "version")])
        self.assertEqual(self.scope()[0], 0)

    def test_undeclared_and_phantom(self):
        self.write(BASE.replace("short", "shorter"), [("Annex A", "modified")])
        code, out = self.scope()
        self.assertEqual(code, 1)
        self.assertIn("CAMBIO SIN DECLARAR: 2. Terms", out)
        self.assertIn("DECLARADA Y SIN CAMBIO: Annex A", out)
        self.assertIn("RESULT=REJECT", out)

    def test_recorded_section_must_be_declared(self):
        head = BASE.replace("short", "shorter")
        self.write(head, [("2", "modified")], records=[{"sections_changed": ["2", "1"]}])
        code, out = self.scope()
        self.assertEqual(code, 1, out)
        self.assertIn("REGISTRADA EN UN PARCHE Y SIN DECLARAR: 1", out)
        self.write(head, [("2", "modified")], records=[{"sections_changed": ["2"]}])
        self.assertEqual(self.scope()[0], 0)

    def test_unreadable_record_cannot_tell(self):
        self.write(BASE.replace("short", "shorter"), [("2", "modified")], records=["{"])
        self.assertEqual(self.scope()[0], 2)

    def test_cleanup_does_not_count_toward_the_fraction(self):
        head = BASE.replace("line 3\n", "line three\n").replace("short", "shorter")
        # Section 1 is most of the document: counted, it is far above 30 %.
        self.write(head, [("1", "modified"), ("2", "modified")])
        code, out = self.scope()
        self.assertEqual(code, 1, out)
        self.assertIn("RESULT=MAJOR", out)
        self.write(head, [("1", "cleanup"), ("2", "modified")])
        code, out = self.scope()
        self.assertEqual(code, 0, out)
        self.assertIn("1 secciones de cleanup/version no cuentan", out)

    def test_a_section_both_cleaned_and_edited_counts(self):
        head = BASE.replace("line 3\n", "line three\n")
        self.write(head, [("1", "cleanup"), ("1. Scope", "modified")])
        self.assertEqual(self.scope()[0], 1)

    def test_cleanup_row_that_did_not_change_is_phantom(self):
        self.write(BASE.replace("short", "shorter"), [("2", "modified"), ("1", "cleanup")])
        code, out = self.scope()
        self.assertEqual(code, 1)
        self.assertIn("DECLARADA Y SIN CAMBIO: 1", out)

    def test_needs_structure_and_no_cap(self):
        head = BASE.replace("line 3\n", "line three\n")
        self.write(head, [("1", "modified")], not_placed=["needs-structure"])
        self.assertIn("RESULT=MAJOR", self.scope(float("inf"))[1])
        self.write(head, [("1", "modified")], not_placed=["ambiguous-source"])
        self.assertEqual(self.scope(float("inf"))[0], 0)

    def test_deleting_the_last_section_leaves_the_one_before_unchanged(self):
        self.write(BASE.replace("## Annex A Use case\n\nwalk\n", ""), [("Annex A", "removed")])
        code, out = self.scope()
        self.assertEqual(code, 0, out)
        self.assertNotIn("2. Terms", out)

    def test_cli_max_fraction_inf(self):
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "check-incremental.py"), "scope",
                            "v1", "v1.1", "--max-fraction", "inf"], capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 64, p.stderr)


class Anchor(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.out = os.path.join(self.tmp.name, "output")
        self.an = os.path.join(self.tmp.name, "output-analysis")
        os.makedirs(self.out)
        os.makedirs(self.an)
        self.saved = (ci.OUTPUT, ci.ANALYSIS)
        ci.OUTPUT, ci.ANALYSIS = self.out, self.an
        put(os.path.join(self.out, "v13-sgai-spec.md"), BASE)
        self.head = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"],
                                   capture_output=True, text=True).stdout.strip()

    def tearDown(self):
        ci.OUTPUT, ci.ANALYSIS = self.saved
        self.tmp.cleanup()

    def test_major_trace_is_its_anchor(self):
        put(os.path.join(self.an, "v13-context-delta.md"), 
            "- Context head: `%s`\n" % self.head)
        self.assertEqual(ci.anchor("v13")[0], self.head)
        self.assertEqual(ci.anchor("v13.2")[0], self.head)

    def test_incremental_trace_wins_over_the_major(self):
        put(os.path.join(self.an, "v13-context-delta.md"), "- Context head: `0000000`\n")
        put(os.path.join(self.an, "v13.1-context-delta.md"), "- Context head: `%s`\n" % self.head)
        self.assertEqual(ci.anchor("v13.3")[0], self.head)

    def test_without_trace_falls_back_to_git(self):
        # output/v13-sgai-spec.md of this private directory is in no commit.
        with self.assertRaises(ci.CannotTell):
            ci.anchor("v13")


if __name__ == "__main__":
    unittest.main()

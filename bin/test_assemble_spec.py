#!/usr/bin/env python3
"""assemble-spec: the source assembles to the published spec byte for byte,
and each way the source can be wrong is caught with its own exit.

Each negative copies spec-source/ into a private temporary directory, breaks
one thing, and runs --check against dist/sgai-spec.md.
Run: python3 bin/test_assemble_spec.py
"""
import hashlib
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


def run(*args):
    p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "assemble-spec.py"), *args],
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class Assemble(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = os.path.join(self.tmp.name, "src")
        shutil.copytree(SRC, self.src)

    def tearDown(self):
        self.tmp.cleanup()

    def test_reproduces_dist(self):
        code, out = run("--check", DIST)
        self.assertEqual(code, 0, out)
        target = os.path.join(self.tmp.name, "a.md")
        man = os.path.join(self.tmp.name, "m.sha256")
        code, out = run("--out", target, "--manifest", man)
        self.assertEqual(code, 0, out)
        with open(target, "rb") as a, open(DIST, "rb") as b:
            self.assertEqual(hashlib.sha256(a.read()).hexdigest(), hashlib.sha256(b.read()).hexdigest())
        with open(man) as fh:
            rows = [l for l in fh if not l.startswith("#")]
        self.assertEqual(rows[0].split()[1], "spec-source/sgai-spec.src.md")

    def test_changed_fixture_is_named(self):
        f = os.path.join(self.src, "examples", "annex-c", "C.2-1.mpd")
        with open(f) as fh:
            body = fh.read()
        with open(f, "w") as fh:
            fh.write(body.replace('xmlns="', 'xmlns ="', 1))
        code, out = run("--source", self.src, "--check", DIST)
        self.assertEqual(code, 1, out)
        self.assertIn("C.2-1.mpd", out)

    def test_changed_prose_is_named(self):
        f = os.path.join(self.src, "sgai-spec.src.md")
        with open(f) as fh:
            body = fh.read()
        with open(f, "w") as fh:
            fh.write(body.replace("## 5. Syntax", "## 5. Syntaxe", 1))
        code, out = run("--source", self.src, "--check", DIST)
        self.assertEqual(code, 1, out)
        self.assertIn("(prose)", out)

    def test_missing_file(self):
        os.remove(os.path.join(self.src, "examples", "annex-a", "A.2-1.mpd"))
        code, out = run("--source", self.src, "--check", DIST)
        self.assertEqual(code, 2, out)
        self.assertIn("does not exist", out)

    def test_no_final_newline(self):
        f = os.path.join(self.src, "syntax", "sgai-extension.xsd")
        with open(f) as fh:
            body = fh.read()
        with open(f, "w") as fh:
            fh.write(body.rstrip("\n"))
        code, out = run("--source", self.src, "--check", DIST)
        self.assertEqual(code, 2, out)

    def test_bad_command_line(self):
        self.assertEqual(run()[0], 64)
        self.assertEqual(run("--out", "x", "--check", "y")[0], 64)


class Version(unittest.TestCase):
    """{{version}}: the status line carries the build iteration, filled by
    the assembler, and --check still holds on dist/ (version read from it)."""

    STATUS = "**Status:** candidate specification, build iteration 12.4."

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = os.path.join(self.tmp.name, "src")
        shutil.copytree(SRC, self.src)
        self.prose = os.path.join(self.src, "sgai-spec.src.md")
        with open(self.prose) as fh:
            body = fh.read()
        self.assertIn(self.STATUS, body)
        with open(self.prose, "w") as fh:
            fh.write(body.replace(self.STATUS, self.STATUS.replace("12.4", "{{version}}"), 1))
        with open(DIST) as fh:
            self.dist = fh.read()

    def tearDown(self):
        self.tmp.cleanup()

    def path(self, name, text=None):
        p = os.path.join(self.tmp.name, name)
        if text is not None:
            with open(p, "w") as fh:
                fh.write(text)
        return p

    def test_version_fills_the_token_without_its_v(self):
        out = self.path("a.md")
        code, msg = run("--source", self.src, "--version", "v12.4", "--out", out)
        self.assertEqual(code, 0, msg)
        with open(out) as fh:
            self.assertEqual(fh.read(), self.dist)
        code, msg = run("--source", self.src, "--version", "13.2", "--out", out)
        self.assertEqual(code, 0, msg)
        with open(out) as fh:
            self.assertIn("build iteration 13.2.", fh.read())

    def test_version_from_the_out_name(self):
        out = self.path("v13.2-sgai-spec.md")
        code, msg = run("--source", self.src, "--out", out)
        self.assertEqual(code, 0, msg)
        with open(out) as fh:
            self.assertIn("build iteration 13.2.\n", fh.read())

    def test_no_version_anywhere_is_refused_on_out(self):
        code, msg = run("--source", self.src, "--out", self.path("a.md"))
        self.assertEqual(code, 2, msg)
        self.assertIn("{{version}}", msg)

    def test_check_takes_the_version_from_the_name(self):
        good = self.path("v12.4-sgai-spec.md", self.dist)
        self.assertEqual(run("--source", self.src, "--check", good)[0], 0)
        wrong = self.path("v12.5-sgai-spec.md", self.dist)
        code, msg = run("--source", self.src, "--check", wrong)
        self.assertEqual(code, 1, msg)
        self.assertIn("line 3", msg)

    def test_check_reads_the_version_from_an_unversioned_document(self):
        code, msg = run("--source", self.src, "--check", DIST)
        self.assertEqual(code, 0, msg)
        self.assertIn("version 12.4, read from the document", msg)
        other = self.path("sgai-spec.md", self.dist.replace("build iteration 12.4.", "build iteration 13.", 1))
        self.assertEqual(run("--source", self.src, "--check", other)[0], 0)
        not_a_version = self.path("sgai-spec.md", self.dist.replace("build iteration 12.4.", "build iteration x.", 1))
        self.assertEqual(run("--source", self.src, "--check", not_a_version)[0], 1)

    def test_two_places_must_carry_the_same_version(self):
        with open(self.prose) as fh:
            body = fh.read()
        with open(self.prose, "w") as fh:
            fh.write(body.replace("## 5. Syntax", "## 5. Syntax {{version}}", 1))
        same = self.path("sgai-spec.md", self.dist.replace("## 5. Syntax", "## 5. Syntax 12.4", 1))
        self.assertEqual(run("--source", self.src, "--check", same)[0], 0)
        differ = self.path("sgai-spec.md", self.dist.replace("## 5. Syntax", "## 5. Syntax 12.5", 1))
        self.assertEqual(run("--source", self.src, "--check", differ)[0], 1)

    def test_explicit_version_wins_over_the_document(self):
        code, msg = run("--source", self.src, "--version", "v12.5", "--check", DIST)
        self.assertEqual(code, 1, msg)

    def test_token_in_an_included_file_is_not_replaced(self):
        f = os.path.join(self.src, "examples", "annex-c", "C.2-1.mpd")
        with open(f, "a") as fh:
            fh.write("{{version}}\n")
        out = self.path("a.md")
        self.assertEqual(run("--source", self.src, "--version", "13", "--out", out)[0], 0)
        with open(out) as fh:
            self.assertIn("{{version}}", fh.read())

    def test_bad_version_is_a_command_line_error(self):
        self.assertEqual(run("--source", self.src, "--version", "13.x", "--out", self.path("a.md"))[0], 64)
        self.assertEqual(run("--source", self.src, "--version", "", "--out", self.path("a.md"))[0], 64)


if __name__ == "__main__":
    unittest.main()

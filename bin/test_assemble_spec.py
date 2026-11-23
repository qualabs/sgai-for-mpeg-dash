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


if __name__ == "__main__":
    unittest.main()

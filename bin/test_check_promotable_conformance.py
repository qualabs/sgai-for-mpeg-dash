#!/usr/bin/env python3
"""check-promotable after ADR 0057: a FAIL in conformance-tests.json blocks,
a Non-conforming row of the LLM audit does not, a missing tests sidecar makes
the run uncertain, and a Player FAIL informs without blocking.

Each case copies dist/'s sidecars into a private temporary directory, adds or
edits one thing, and compares against the same run without it.
Run: python3 bin/test_check_promotable_conformance.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(os.path.dirname(BIN), "dist")
SIDE = ("spec-validation.md", "detail-review.md", "dash-conformance-audit.md")


def run(d):
    p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "check-promotable.py"), "--from", d],
                       capture_output=True, text=True)
    last = [l for l in p.stdout.splitlines() if l.startswith("PROMOTABLE=")][-1]
    return p.returncode, dict(re.findall(r"(\w+)=(\w+)", last)), p.stdout


def tests_json(results, cannot=()):
    return json.dumps({"results": results, "cannot": list(cannot), "exit": 0})


class Conformance(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(dir=os.environ.get("XDG_RUNTIME_DIR"))
        for n in SIDE:
            shutil.copy(os.path.join(DIST, n), self.d)
        self.write([{"rule": "E-3", "outcome": "PASS", "subject": "xml#10"}])

    def tearDown(self):
        shutil.rmtree(self.d)

    def write(self, results, cannot=()):
        with open(os.path.join(self.d, "conformance-tests.json"), "w") as fh:
            fh.write(tests_json(results, cannot))

    def test_code_fail_blocks(self):
        _, base, _ = run(self.d)
        self.write([{"rule": "DR-7", "outcome": "FAIL", "subject": "xml#10"}])
        _, after, out = run(self.d)
        self.assertEqual(int(after["BLOCKERS"]), int(base["BLOCKERS"]) + 1)
        self.assertIn("conformance FAIL", out)

    def test_player_fail_does_not_block(self):
        _, base, _ = run(self.d)
        self.write([{"rule": "P-LEGACY-dashjs", "outcome": "FAIL", "subject": "xml#10"}])
        _, after, _ = run(self.d)
        self.assertEqual(after["BLOCKERS"], base["BLOCKERS"])
        self.assertEqual(int(after["OPEN"]), int(base["OPEN"]) + 1)

    def test_audit_non_conforming_does_not_block(self):
        _, base, _ = run(self.d)
        path = os.path.join(self.d, "dash-conformance-audit.md")
        text = open(path).read()
        new = text.replace("| K-1 | Namespace `urn:svta:dash:sgai:2026` | Extension namespace | Elements and attributes in MPDs, List MPDs, standalone document | Conforming |",
                           "| K-1 | Namespace `urn:svta:dash:sgai:2026` | Extension namespace | Elements and attributes in MPDs, List MPDs, standalone document | Non-conforming |", 1)
        self.assertNotEqual(new, text, "the audit row to edit was not found")
        open(path, "w").write(new)
        _, after, _ = run(self.d)
        self.assertEqual(after["BLOCKERS"], base["BLOCKERS"])
        self.assertEqual(int(after["OPEN"]), int(base["OPEN"]) + 1)

    def test_missing_tests_is_uncertain_missing_audit_is_not(self):
        _, base, _ = run(self.d)
        os.remove(os.path.join(self.d, "dash-conformance-audit.md"))
        _, no_audit, _ = run(self.d)
        self.assertEqual(no_audit["UNCERTAIN"], base["UNCERTAIN"])
        os.remove(os.path.join(self.d, "conformance-tests.json"))
        code, no_tests, out = run(self.d)
        self.assertEqual(code, 2)
        self.assertEqual(int(no_tests["UNCERTAIN"]), int(base["UNCERTAIN"]) + 1)
        self.assertIn("conformance-tests.json", out)

    def test_cannot_tell_is_uncertain(self):
        _, base, _ = run(self.d)
        self.write([], cannot=["ISO schema unavailable"])
        _, after, _ = run(self.d)
        self.assertEqual(int(after["UNCERTAIN"]), int(base["UNCERTAIN"]) + 1)


if __name__ == "__main__":
    unittest.main()

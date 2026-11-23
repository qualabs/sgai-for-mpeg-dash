#!/usr/bin/env python3
"""promote: copies the full published set only when every gate holds; one gate
failing copies nothing (exit 1), one gate unable to tell copies nothing
(exit 2). The gates' scripts are replaced by stubs; the candidate's files live
in a scratch root and the dist is a scratch directory.
Run: python3 bin/test_promote.py
"""
import importlib.util
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

BIN = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("promote", os.path.join(BIN, "promote.py"))
pr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pr)

GATES = ("assemble-spec.py", "lint-spec.py", "check-trace.py", "check-promotable.py",
         "compare-candidates.py", "check-dash-conformance.py")


class Promote(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = os.path.join(self.tmp.name, "root")
        self.dist = os.path.join(self.tmp.name, "dist")
        for pat in pr.PUBLISHED.values():
            p = os.path.join(self.root, pat.format(v="v9.9"))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w").write(pat + "\n")
        self.real_root, self.real_run = pr.ROOT, pr.run
        pr.ROOT = self.root
        self.result = {g: (0, "ok") for g in GATES}
        self.result["compare-candidates.py"] = (0, "BETTER THAN PUBLISHED (0 worse, 1 better)")
        pr.run = lambda script, *a: self.result[os.path.basename(script)]

    def tearDown(self):
        pr.ROOT, pr.run = self.real_root, self.real_run
        self.tmp.cleanup()

    def promote(self, *extra):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = pr.main(["v9.9", "--dist", self.dist, *extra])
        return code, buf.getvalue()

    def copied(self):
        return sorted(os.listdir(self.dist)) if os.path.isdir(self.dist) else []

    def test_all_hold_copies_the_full_set(self):
        code, out = self.promote()
        self.assertEqual(code, 0, out)
        self.assertEqual(self.copied(), sorted(list(pr.PUBLISHED) + ["PROVENANCE.md", "inputs.sha256"]))
        with open(os.path.join(self.dist, "sgai-extension.xsd")) as fh:
            self.assertEqual(fh.read(), "output/{v}-sgai-extension.xsd\n")
        with open(os.path.join(self.dist, "inputs.sha256")) as fh:
            self.assertIn("spec-source/sgai-spec.src.md", fh.read())

    def test_dry_run_copies_nothing(self):
        code, out = self.promote("--dry-run")
        self.assertEqual((code, self.copied()), (0, []), out)

    def test_each_gate_failing_blocks(self):
        for g in GATES:
            with self.subTest(gate=g):
                self.result[g] = (1, "broken")
                code, out = self.promote()
                self.assertEqual((code, self.copied()), (1, []), out)
                self.result[g] = (0, "ok") if g != "compare-candidates.py" else (0, "BETTER THAN PUBLISHED")

    def test_compare_not_better_blocks(self):
        for verdict in ("NO BETTER THAN PUBLISHED", "WORSE THAN PUBLISHED"):
            self.result["compare-candidates.py"] = (0, verdict)
            code, out = self.promote()
            self.assertEqual((code, self.copied()), (1, []), out)

    def test_cannot_tell_is_2(self):
        self.result["check-trace.py"] = (2, "no trace")
        code, out = self.promote()
        self.assertEqual((code, self.copied()), (2, []), out)

    def test_missing_file_blocks(self):
        os.remove(os.path.join(self.root, "output-analysis", "v9.9-conformance-tests.json"))
        code, out = self.promote()
        self.assertEqual((code, self.copied()), (1, []), out)
        self.assertIn("conformance-tests.json", out)


if __name__ == "__main__":
    unittest.main()

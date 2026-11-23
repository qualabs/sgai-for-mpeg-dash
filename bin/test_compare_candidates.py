#!/usr/bin/env python3
"""compare-candidates: unit by unit, a written verdict, and no verdict when the
two sides do not count the same kind of unit (the v12.6 vs v7.2 case).

Each case builds a candidate and a published side in a private temporary
directory from the v12.6 sidecars (published in dist/), changes one thing,
and compares.
Run: python3 bin/test_compare_candidates.py
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
ROOT = os.path.dirname(BIN)
DIST = os.path.join(ROOT, "dist")
NAMES = ("spec-validation.md", "detail-review.md", "dash-conformance-audit.md")


def git_show(rev, path):
    return subprocess.run(["git", "-C", ROOT, "show", f"{rev}:{path}"], capture_output=True, text=True).stdout


class Compare(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.an = os.path.join(self.tmp.name, "an")
        self.dist = os.path.join(self.tmp.name, "dist")
        os.makedirs(self.an)
        os.makedirs(self.dist)
        for n in NAMES:
            shutil.copy(os.path.join(DIST, n), os.path.join(self.an, "v9.9-" + n))
            shutil.copy(os.path.join(DIST, n), os.path.join(self.dist, n))
        self.tests = {"counts": {"PASS": 100, "FAIL": 3, "NOT_VERIFIABLE": 10}}
        for p in (os.path.join(self.an, "v9.9-conformance-tests.json"), os.path.join(self.dist, "conformance-tests.json")):
            with open(p, "w") as fh:
                json.dump(self.tests, fh)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cmp(self, *extra):
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "compare-candidates.py"), "v9.9",
                            "--analysis", self.an, "--dist", self.dist, *extra], capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr

    def edit_validation(self, unit, new_status):
        p = os.path.join(self.an, "v9.9-spec-validation.md")
        with open(p) as fh:
            lines = fh.read().split("\n")
        for i, l in enumerate(lines):
            if l.startswith(f"| {unit} |"):
                cells = l.split(" | ")
                cells[2] = new_status
                lines[i] = " | ".join(cells)
                break
        else:
            self.fail(f"no row {unit}")
        with open(p, "w") as fh:
            fh.write("\n".join(lines))

    def test_same_is_no_better(self):
        code, out = self.run_cmp()
        self.assertEqual(code, 0, out)
        self.assertTrue(out.startswith("NO BETTER THAN PUBLISHED"), out)
        self.assertIn("211 shared units", out)

    def test_met_to_contradicted_is_worse(self):
        self.edit_validation("R1.1", "contradicted")
        code, out = self.run_cmp()
        self.assertEqual(code, 0, out)
        self.assertTrue(out.startswith("WORSE THAN PUBLISHED"), out)

    def test_met_to_partial_is_not_worse(self):
        self.edit_validation("R1.1", "partial")
        self.assertTrue(self.run_cmp()[1].startswith("NO BETTER"))

    def test_partial_to_met_is_better(self):
        with open(os.path.join(self.dist, "spec-validation.md")) as fh:
            partial = [m.group(1) for m in re.finditer(r"^\| (\S+) \| \w+ \| partial \|", fh.read(), re.M)]
        self.assertTrue(partial)
        self.edit_validation(partial[0], "met")
        self.assertTrue(self.run_cmp()[1].startswith("BETTER THAN PUBLISHED"))

    def test_more_fail_is_worse_fewer_is_better(self):
        self.tests["counts"]["FAIL"] = 4
        with open(os.path.join(self.an, "v9.9-conformance-tests.json"), "w") as fh:
            json.dump(self.tests, fh)
        self.assertTrue(self.run_cmp()[1].startswith("WORSE THAN PUBLISHED"))
        self.tests["counts"]["FAIL"] = 2
        with open(os.path.join(self.an, "v9.9-conformance-tests.json"), "w") as fh:
            json.dump(self.tests, fh)
        self.assertTrue(self.run_cmp()[1].startswith("BETTER THAN PUBLISHED"))

    def test_dist_without_tests_is_outside_the_rule(self):
        os.remove(os.path.join(self.dist, "conformance-tests.json"))
        self.tests["counts"]["FAIL"] = 50
        with open(os.path.join(self.an, "v9.9-conformance-tests.json"), "w") as fh:
            json.dump(self.tests, fh)
        code, out = self.run_cmp()
        self.assertTrue(out.startswith("NO BETTER"), out)
        with open(os.path.join(self.an, "v9.9-comparison.md")) as fh:
            self.assertIn("outside the rule", fh.read())

    def test_v72_population_cannot_tell(self):
        # The comparison the LLM made on v12.6: 30 requirements against 211 criteria.
        for n in NAMES:
            body = git_show("225dacf", "dist/" + n)
            self.assertTrue(body, "git history of dist/ before the v12.6 promotion is needed")
            with open(os.path.join(self.dist, n), "w") as fh:
                fh.write(body)
        code, out = self.run_cmp()
        self.assertEqual(code, 2, out)
        self.assertIn("not comparable", out)

    def test_candidate_without_tests_cannot_tell(self):
        os.remove(os.path.join(self.an, "v9.9-conformance-tests.json"))
        self.assertEqual(self.run_cmp()[0], 2)

    def test_command_line(self):
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "compare-candidates.py"), "nine"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 64)


if __name__ == "__main__":
    unittest.main()

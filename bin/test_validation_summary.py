#!/usr/bin/env python3
"""validation-summary: the summary carries what check-promotable reads, with
the counts each heading declares checked against its entries; and
check-promotable, given the summary, reads it (and refuses a stale one)
without changing its verdict on the real v12.6 sidecars.

Run: python3 bin/test_validation_summary.py
"""
import importlib.util
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
spec = importlib.util.spec_from_file_location("vs", os.path.join(BIN, "validation-summary.py"))
vs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vs)

POP = [("R1.1", "criterion"), ("R1.2", "criterion"), ("UC-01", "use-case")]

SIDECAR = """# Spec validation — v9 (2026-11-23)

## Gaps (1)

### G-1 — one

## Edge cases (0)

## Ambiguities (2)

### A-1 — one

### A-2 — two

## Obligation coverage map

| Unit | Kind | Verdict | Disposition | Evidence | Notes |
|------|------|---------|-------------|----------|-------|
| R1.1 | runtime | met | — | §1: *"x"* | |
| R1.2 | runtime | contradicted | 5.a | §1: *"y"* | |
| R9.9 | runtime | met | — | §1: *"z"* | |

## Disposition of findings

### 5.a Actionable TODOs (1)

| # | Finding ref | Criterion | Spec section | Concrete edit | Citation |
|---|-------------|-----------|--------------|---------------|----------|
| T1 | R1.2 | 6 | §1 | edit | R1.2 |

#### 5.a Overflow (next pass)

| # | Finding ref | Criterion | Spec section | Concrete edit | Citation |
|---|-------------|-----------|--------------|---------------|----------|
| T2 | A-2 | 3 | §1 | edit | R1.1 |

### 5.b Flagged for review (1)

| # | Finding ref | Spec section | Why | Resolutions | Recommended | Searched |
|---|-------------|--------------|-----|-------------|-------------|----------|
| F-1 | G-1 | §1 | w | r | r | s |

### 5.c Deferred to context/ (0)

### 5.d context/ change, predictable (1)

| # | Finding ref | passage | Replacement | Source |
|---|-------------|---------|-------------|--------|
| P-1 | A-1 | p | r | ADR 0001 |
"""


class Summarise(unittest.TestCase):
    def s(self, text=SIDECAR):
        return vs.summarise(text, POP, "x.md")

    def test_counts(self):
        s = self.s()
        self.assertEqual((s["gaps"], s["edge_cases"], s["ambiguities"]), (1, 0, 2))
        self.assertEqual(s["findings"], {"5.a": 2, "5.b": 1, "5.c": 0, "5.d": 1})
        self.assertEqual(s["inconsistent"], [])

    def test_population_arithmetic(self):
        s = self.s()
        self.assertEqual((s["population"], s["walked"], s["missing"], s["extra"]),
                         (3, 3, ["UC-01"], ["R9.9"]))
        self.assertEqual(s["verdicts"], {"met": 2, "contradicted": 1})

    def test_units_carry_their_disposition(self):
        u = self.s()["units"]
        self.assertEqual(u["R1.2"], {"verdict": "contradicted", "disposition": "5.a"})
        self.assertEqual(u["R1.1"], {"verdict": "met", "disposition": None})

    def test_heading_count_disagrees(self):
        s = self.s(SIDECAR.replace("## Ambiguities (2)", "## Ambiguities (3)"))
        self.assertTrue(any("Ambiguities" in m for m in s["inconsistent"]))
        s = self.s(SIDECAR.replace("### 5.b Flagged for review (1)", "### 5.b Flagged for review (2)"))
        self.assertTrue(any(m.startswith("5.b") for m in s["inconsistent"]))

    def test_overflow_is_not_counted_against_the_heading(self):
        self.assertEqual(self.s()["inconsistent"], [])
        s = self.s(SIDECAR.replace("### 5.a Actionable TODOs (1)", "### 5.a Actionable TODOs (2)"))
        self.assertTrue(any(m.startswith("5.a") for m in s["inconsistent"]))

    def test_no_map_cannot_tell(self):
        with self.assertRaises(vs.CannotTell):
            self.s(SIDECAR.replace("## Obligation coverage map", "## Something else"))

    def test_no_findings_heading_cannot_tell(self):
        with self.assertRaises(vs.CannotTell):
            self.s(SIDECAR.replace("## Edge cases (0)", "## Edge cases"))


class Cli(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(dir=os.environ.get("XDG_RUNTIME_DIR"))
        self.p = lambda n: os.path.join(self.d, n)
        with open(self.p("pop.tsv"), "w") as fh:
            fh.write("".join(f"{u}\t{k}\n" for u, k in POP))

    def tearDown(self):
        shutil.rmtree(self.d)

    def run_vs(self, text, *extra):
        with open(self.p("v.md"), "w") as fh:
            fh.write(text)
        return subprocess.run([sys.executable, os.path.join(BIN, "validation-summary.py"), self.p("v.md"),
                               "--population", self.p("pop.tsv"), "--out", self.p("s.json"), *extra],
                              capture_output=True, text=True)

    def test_exits(self):
        self.assertEqual(self.run_vs(SIDECAR).returncode, 0)
        self.assertEqual(self.run_vs(SIDECAR.replace("## Gaps (1)", "## Gaps (5)")).returncode, 1)
        self.assertEqual(self.run_vs("# nothing\n").returncode, 2)
        self.assertEqual(self.run_vs(SIDECAR, "--outt").returncode, 64)


V126 = os.path.join(ROOT, "output-analysis", "v12.6-spec-validation.md")


def promotable(d):
    p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "check-promotable.py"), "--from", d],
                       capture_output=True, text=True)
    return p.returncode, p.stdout


@unittest.skipUnless(os.path.isfile(V126), "no v12.6 sidecar")
class PromotableReadsTheSummary(unittest.TestCase):
    """The v12.6 sidecars in a private directory, with and without the summary."""

    def setUp(self):
        self.d = tempfile.mkdtemp(dir=os.environ.get("XDG_RUNTIME_DIR"))
        oa = os.path.join(ROOT, "output-analysis")
        for n in ("spec-validation.md", "detail-review.md", "dash-conformance-audit.md"):
            shutil.copy(os.path.join(oa, "v12.6-" + n), os.path.join(self.d, n))
        with open(os.path.join(self.d, "conformance-tests.json"), "w") as fh:
            json.dump({"results": [], "cannot": []}, fh)
        with open(os.path.join(self.d, "spec-validation.md")) as fh:
            self.text = fh.read()
        self.summary = vs.summarise(self.text, vs.cp.population(), "spec-validation.md")

    def tearDown(self):
        shutil.rmtree(self.d)

    def write(self, summ):
        with open(os.path.join(self.d, "spec-validation.summary.json"), "w") as fh:
            json.dump(summ, fh)

    def test_real_counts(self):
        s = self.summary
        self.assertEqual((s["walked"], s["shape"]), (211, "per-criterion"))
        self.assertEqual(s["findings"], {"5.a": 4, "5.b": 6, "5.c": 6, "5.d": 2})
        self.assertEqual((s["gaps"], s["edge_cases"], s["ambiguities"]), (2, 1, 12))
        self.assertEqual(s["verdicts"], {"met": 207, "partial": 4})
        self.assertEqual(s["inconsistent"], [])

    def test_same_verdict_with_and_without(self):
        without = promotable(self.d)
        self.write(self.summary)
        self.assertEqual(promotable(self.d), without)

    def test_the_summary_is_what_is_read(self):
        before = promotable(self.d)
        s = json.loads(json.dumps(self.summary))
        s["rows"] = [[u, "contradicted" if u == "R2.3" else v] for u, v in s["rows"]]
        self.write(s)
        code, out = promotable(self.d)
        self.assertNotEqual((code, out), before)
        self.assertIn("R2.3", out)

    def test_stale_summary_cannot_tell(self):
        s = dict(self.summary, sidecar_sha256="0" * 64)
        self.write(s)
        code, out = promotable(self.d)
        self.assertEqual(code, 2)
        self.assertIn("no es de este sidecar", out)

    def test_unreadable_summary_cannot_tell(self):
        with open(os.path.join(self.d, "spec-validation.summary.json"), "w") as fh:
            fh.write("{}")
        code, out = promotable(self.d)
        self.assertEqual(code, 2)
        self.assertIn("summary.json no se puede leer", out)


if __name__ == "__main__":
    unittest.main()

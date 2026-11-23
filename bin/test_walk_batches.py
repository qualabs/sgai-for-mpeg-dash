#!/usr/bin/env python3
"""walk-batches: every walker answer is validated by code; what fails, or asks
for sections, goes back once; what still fails is written not-verifiable and
never met. The model is replaced by a stub that returns scripted answers.
Run: python3 bin/test_walk_batches.py
"""
import importlib.util
import json
import os
import tempfile
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("wb", os.path.join(BIN, "walk-batches.py"))
wb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wb)

SECTIONS = {"5.1.3": "#### 5.1.3 The overlay window\n\nThe Player **MUST** present the window\nonly inside its span.\n",
            "7.2": "### 7.2 Other\n\nNothing about windows.\n"}
GOOD = {"unit": "R1.1", "kind": "runtime", "verdict": "met",
        "sections": [{"key": "5.1.3", "quotes": ["The Player MUST present the window only inside its span."]}],
        "notes": "ok"}


class Walk(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.W = self.tmp.name
        with open(os.path.join(self.W, "batch-1.txt"), "w") as fh:
            fh.write("===== UNIT R1.1 (criterion) =====\ntext\n")
        self.replies = []
        self.prompts = []
        self.real = wb.call_model

        def stub(prompt, model=None):
            self.prompts.append(prompt)
            return self.replies.pop(0), {"input_tokens": 1, "output_tokens": 1}
        wb.call_model = stub

    def tearDown(self):
        wb.call_model = self.real
        self.tmp.cleanup()

    def run_with(self, *replies):
        self.replies = [json.dumps(r) if isinstance(r, dict) else r for r in replies]
        _, out, calls = wb.walk(1, self.W, SECTIONS, None)
        return out[0], len(calls)

    def test_valid_in_one_call(self):
        o, n = self.run_with(GOOD)
        self.assertEqual((o["verdict"], n), ("met", 1))

    def test_each_defect_goes_back_and_ends_not_verifiable(self):
        bad = {
            "kind": dict(GOOD, kind="behaviour"),
            "verdict": dict(GOOD, verdict="fine"),
            "section": dict(GOOD, sections=[{"key": "9.9", "quotes": ["x"]}]),
            "quote": dict(GOOD, sections=[{"key": "5.1.3", "quotes": ["The Player MAY present"]}]),
            "uncited": dict(GOOD, sections=[]),
            "other section": dict(GOOD, sections=[{"key": "7.2", "quotes": ["only inside its span"]}]),
        }
        for name, b in bad.items():
            with self.subTest(defect=name):
                o, n = self.run_with(b, b)
                self.assertEqual((o["verdict"], n), ("not-verifiable", 2), o)

    def test_second_round_can_fix(self):
        o, n = self.run_with(dict(GOOD, sections=[]), GOOD)
        self.assertEqual((o["verdict"], n), ("met", 2))
        self.assertIn("carries no quotation", self.prompts[1])

    def test_need_sections_are_sent(self):
        o, n = self.run_with({"unit": "R1.1", "verdict": None, "need_sections": ["7.2"]}, dict(GOOD, verdict="gap", sections=[]))
        self.assertEqual(o["verdict"], "gap")
        self.assertIn("Nothing about windows.", self.prompts[1])

    def test_no_answer_and_garbage(self):
        o, n = self.run_with("I think it is met.", "still prose")
        self.assertEqual(o["verdict"], "not-verifiable")

    def test_gap_needs_no_quote_and_emphasis_is_normalised(self):
        o, _ = self.run_with(dict(GOOD, verdict="gap", sections=[]))
        self.assertEqual(o["verdict"], "gap")
        o, _ = self.run_with(dict(GOOD, sections=[{"key": "5.1.3", "quotes": ["The Player **MUST** present the window\nonly"]}]))
        self.assertEqual(o["verdict"], "met")

    def test_answer_file_and_exit(self):
        self.replies = [json.dumps(dict(GOOD, kind="x")), json.dumps(dict(GOOD, kind="x"))]
        wb.walk(1, self.W, SECTIONS, None)
        with open(os.path.join(self.W, "answer-1.jsonl")) as fh:
            self.assertEqual(json.loads(fh.readline())["verdict"], "not-verifiable")


if __name__ == "__main__":
    unittest.main()

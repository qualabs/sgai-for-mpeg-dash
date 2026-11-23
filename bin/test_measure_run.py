#!/usr/bin/env python3
"""measure-run counts once per API call, attributes subagents to their step,
and the line-per-block count it replaces gives a different (larger) number.

A synthetic transcript reproduces the shape Claude Code writes: each call
appears on several lines (one per content block) repeating its usage, with
the output count growing to its final value on the last line.
Run: python3 bin/test_measure_run.py
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("measure_run", os.path.join(BIN, "measure-run.py"))
mr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mr)

REAL = os.path.expanduser(
    "~/.claude/projects/-home-nicolas-Develop-ai-workspace-cto-assistant-projects-"
    "sgai-for-mpeg-dash/5ad312df-caca-482f-b848-255221700f7e.jsonl")


def call_lines(mid, cr, cw, fresh, outs):
    return [{"type": "assistant", "message": {"id": mid, "usage": {
        "input_tokens": fresh, "cache_creation_input_tokens": cw,
        "cache_read_input_tokens": cr, "output_tokens": o}}} for o in outs]


class MeasureRun(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = os.path.join(self.tmp.name, "sess")
        os.makedirs(os.path.join(base, "subagents"))
        main = [{"type": "user", "message": {"content": "orchestrate"}}]
        main += call_lines("m1", 1000, 100, 1, [5, 50])
        sub = [{"type": "user", "message": {"content": [{"type": "text", "text":
                "Task: follow the instructions in `prompts/3-post-spec/validate-spec.prompt`"}]}}]
        sub += call_lines("s1", 200000, 0, 2, [1, 2, 300])
        sub += call_lines("s2", 210000, 5000, 3, [400])
        for path, rows in ((base + ".jsonl", main),
                           (os.path.join(base, "subagents", "agent-x.jsonl"), sub)):
            with open(path, "w") as fh:
                fh.write("\n".join(json.dumps(r) for r in rows) + "\n")
        self.session = base + ".jsonl"

    def tearDown(self):
        self.tmp.cleanup()

    def test_once_per_call_with_final_output(self):
        rows, total = mr.measure(self.session)
        sub = [r for r in rows if r["step"] == "prompts/3-post-spec/validate-spec.prompt"][0]
        self.assertEqual(sub["calls"], 2)
        self.assertEqual(sub["cache_read"], 410000)
        self.assertEqual(sub["output"], 700)          # final 300 + 400, not 1+2+300+400
        self.assertEqual(sub["max_context"], 215003)
        self.assertEqual(total["input_processed"], 1101 + 200002 + 215003)
        self.assertEqual(total["calls"], 3)

    def test_line_count_differs(self):
        # The negative: counting lines inflates the input of a call by its block count.
        _, good = mr.measure(self.session)
        _, bad = mr.measure(self.session, count_lines=True)
        self.assertEqual(bad["calls"], 6)
        self.assertGreater(bad["input_processed"], good["input_processed"])

    def test_cli_exits(self):
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "measure-run.py"), self.session],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "measure-run.py"), "no-such-id",
                            "--root", self.tmp.name], capture_output=True, text=True)
        self.assertEqual(p.returncode, 2)
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "measure-run.py"), "--nope", "x"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 64)

    @unittest.skipUnless(os.path.exists(REAL), "the 2026-10-27 transcript is gone (30-day cleanup)")
    def test_baseline_incremental(self):
        _, total = mr.measure(REAL)
        self.assertEqual(round(total["input_processed"] / 1e6, 1), 41.8)
        _, bad = mr.measure(REAL, count_lines=True)
        self.assertGreater(bad["input_processed"], 80e6)


if __name__ == "__main__":
    unittest.main()

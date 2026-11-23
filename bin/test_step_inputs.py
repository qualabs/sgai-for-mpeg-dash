#!/usr/bin/env python3
"""step-inputs: a pre-spec step is stale exactly when the content of a declared
input moved; a touch leaves it fresh. Runs on a private copy of the inputs.
Run: python3 bin/test_step_inputs.py
"""
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
spec = importlib.util.spec_from_file_location("step_inputs", os.path.join(BIN, "step-inputs.py"))
si = importlib.util.module_from_spec(spec)
spec.loader.exec_module(si)


def call(root, *argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = si.main(list(argv), root)
    return code, buf.getvalue()


class StepInputs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        r = self.root = self.tmp.name
        shutil.copytree(os.path.join(ROOT, "context"), os.path.join(r, "context"))
        os.makedirs(os.path.join(r, "prompts", "1-pre-spec"))
        os.makedirs(os.path.join(r, "context-analysis"))
        for p in ("analyze-dash-gap.prompt", "build-error-semantics.prompt"):
            shutil.copy(os.path.join(ROOT, "prompts", "1-pre-spec", p), os.path.join(r, "prompts", "1-pre-spec", p))
        for o in ("dash-gap-analysis.md", "error-semantics.md"):
            open(os.path.join(r, "context-analysis", o), "w").write("built\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_no_manifest_cannot_tell(self):
        self.assertEqual(call(self.root, "check", "analyze-dash-gap")[0], 2)

    def test_record_then_fresh_and_touch_stays_fresh(self):
        self.assertEqual(call(self.root, "record", "analyze-dash-gap")[0], 0)
        self.assertEqual(call(self.root, "check", "analyze-dash-gap")[0], 0)
        f = os.path.join(self.root, "context", "03-requirements.md")
        later = time.time() + 3600
        os.utime(f, (later, later))
        self.assertEqual(call(self.root, "check", "analyze-dash-gap")[0], 0)

    def test_byte_change_is_stale_and_named(self):
        call(self.root, "record", "build-error-semantics")
        f = os.path.join(self.root, "context", "05-dash-linear-interfaces.md")
        st = os.stat(f)
        with open(f, "a") as fh:
            fh.write(" ")
        os.utime(f, (st.st_atime, st.st_mtime))  # same mtime, different bytes
        code, out = call(self.root, "check", "build-error-semantics")
        self.assertEqual(code, 1)
        self.assertIn("changed: context/05-dash-linear-interfaces.md", out)

    def test_undeclared_input_does_not_count(self):
        call(self.root, "record", "build-error-semantics")
        with open(os.path.join(self.root, "context", "04-use-cases.md"), "a") as fh:
            fh.write("x")
        self.assertEqual(call(self.root, "check", "build-error-semantics")[0], 0)

    def test_added_context_file_is_stale(self):
        call(self.root, "record", "analyze-dash-gap")
        open(os.path.join(self.root, "context", "50-new.md"), "w").write("new\n")
        code, out = call(self.root, "check", "analyze-dash-gap")
        self.assertEqual(code, 1)
        self.assertIn("added: context/50-new.md", out)

    def test_prompt_change_is_stale(self):
        call(self.root, "record", "analyze-dash-gap")
        with open(os.path.join(self.root, "prompts", "1-pre-spec", "analyze-dash-gap.prompt"), "a") as fh:
            fh.write("\n")
        self.assertEqual(call(self.root, "check", "analyze-dash-gap")[0], 1)

    def test_bad_command_line(self):
        p = subprocess.run([sys.executable, "-I", os.path.join(BIN, "step-inputs.py"), "check", "nope"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 64)


if __name__ == "__main__":
    unittest.main()

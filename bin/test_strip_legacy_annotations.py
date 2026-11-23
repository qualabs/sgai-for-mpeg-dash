#!/usr/bin/env python3
"""strip-legacy-annotations: the patch removes the old pipeline's four marks
and nothing else, and on a clean source finds nothing.

Unit cases work on small documents; the end-to-end case applies the patch to
a private copy of spec-source/ and asks lint-spec, an independent script,
whether the marks are gone. The syntax.yaml cases need PyYAML and ISO's
schema (the generator is the oracle): run with
  uv run --with lxml==6.1.3 --with pyyaml==6.0.3 python3 bin/test_strip_legacy_annotations.py
"""
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
sys.path.insert(0, BIN)

def put(path, text):
    with open(path, "w") as fh:
        fh.write(text)


def read(path):
    with open(path) as fh:
        return fh.read()



def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sla = load("sla", "strip-legacy-annotations.py")
asp = load("asp", "apply-spec-patch.py")

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False


def run(*args):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = sla.main(list(args))
    return code, buf.getvalue()


DOC = """# Title

**Status:** candidate specification, build iteration 12.4.

## 1. Scope

<!-- delta: abc1234 R1.1 -->
A sentence. <!-- refine: v1-x.md#T1 --> The next sentence.

| a | b <!-- refine: v1-x.md#T2 --> |
| c | d <!-- delta: e R2 --> <!-- delta: f R3 --> |

  <!-- refine: v1.md#K-1 -->
Code `<!-- refine: inline code -->` stays, and <!-- note: other --> stays.

```xml
<!-- refine: inside a fence stays -->
```

<!-- refine: v1.md#K-2 --> Starts the line.

## Refinement gaps

| # | x |

## 2. Next

Clean.
"""

EXPECTED = """# Title

**Status:** candidate specification, build iteration {{version}}.

## 1. Scope

A sentence. The next sentence.

| a | b |
| c | d |

Code `<!-- refine: inline code -->` stays, and <!-- note: other --> stays.

```xml
<!-- refine: inside a fence stays -->
```

Starts the line.

## 2. Next

Clean.
"""


class Unit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = os.path.join(self.tmp.name, "s.md")
        self.out = os.path.join(self.tmp.name, "p.json")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, text):
        with open(self.src, "w") as fh:
            fh.write(text)

    def apply(self):
        with redirect_stdout(io.StringIO()):
            code = asp.main([self.out, "--source", self.src])
        self.assertEqual(code, 0)
        with open(self.src) as fh:
            return fh.read()

    def test_each_mark_and_only_marks(self):
        self.write(DOC)
        code, msg = run("--source", self.src, "--out", self.out)
        self.assertEqual(code, 1, msg)
        self.assertIn("7 comment(s), 1 gaps section(s), 1 status line(s)", msg)
        self.assertEqual(self.apply(), EXPECTED)

    def test_idempotent(self):
        self.write(EXPECTED)
        code, msg = run("--source", self.src, "--out", self.out)
        self.assertEqual(code, 0, msg)
        self.assertFalse(os.path.exists(self.out))

    def test_status_with_token_is_left(self):
        self.write("# T\n\n**Status:** candidate, build iteration {{version}}.\n")
        self.assertEqual(run("--source", self.src, "--out", self.out)[0], 0)

    def test_status_with_v_prefix(self):
        self.write("# T\n\n**Status:** candidate, build iteration v13.2.\n")
        self.assertEqual(run("--source", self.src, "--out", self.out)[0], 1)
        self.assertEqual(self.apply(), "# T\n\n**Status:** candidate, build iteration {{version}}.\n")

    def test_comment_only_after_a_space_or_before_one(self):
        self.assertEqual(sla.strip_line("x <!-- refine: a --> y\n"), ("x y\n", 1))
        self.assertEqual(sla.strip_line("x <!-- refine: a -->\n"), ("x\n", 1))
        self.assertEqual(sla.strip_line("<!-- refine: a --> y\n"), ("y\n", 1))
        self.assertEqual(sla.strip_line("x<!-- delta: a -->y\n"), ("xy\n", 1))
        self.assertEqual(sla.strip_line("   <!-- delta: a -->\n"), (None, 1))
        self.assertEqual(sla.strip_line("x <!-- refined thing -->\n"), ("x <!-- refined thing -->\n", 0))

    def test_gaps_with_directive_cannot_tell(self):
        self.write("# T\n\n## Refinement gaps\n\n{{example:a/b.mpd}}\n")
        self.assertEqual(run("--source", self.src, "--out", self.out)[0], 2)

    def test_command_line(self):
        self.write(DOC)
        for args in ([], ["--source", self.src], ["--out"], ["--bogus", "x"]):
            with self.assertRaises(SystemExit) as cm, redirect_stdout(io.StringIO()):
                import contextlib
                with contextlib.redirect_stderr(io.StringIO()):
                    sla.main(args)
            self.assertEqual(cm.exception.code, 64)
        self.assertEqual(run("--source", os.path.join(self.tmp.name, "none.md"), "--out", self.out)[0], 2)


@unittest.skipUnless(HAVE_YAML, "needs PyYAML (the generator is the oracle)")
class OnTheSource(unittest.TestCase):
    """The real source: after the patch and the regeneration, lint finds no
    L-COMMENT and no L-GAPS; a second run finds nothing."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = os.path.join(self.tmp.name, "spec-source")
        shutil.copytree(os.path.join(ROOT, "spec-source"), self.dir)
        self.src = os.path.join(self.dir, "sgai-spec.src.md")
        self.out = os.path.join(self.tmp.name, "p.json")

    def tearDown(self):
        self.tmp.cleanup()

    def py(self, *args):
        p = subprocess.run([sys.executable, *args], capture_output=True, text=True, cwd=ROOT)
        return p.returncode, p.stdout + p.stderr

    def test_lint_is_clean_of_marks_and_second_run_is_clean(self):
        code, msg = run("--source", self.src, "--out", self.out)
        self.assertEqual(code, 1, msg)
        ops = json.loads(read(self.out))["ops"]
        self.assertTrue(any("file" in o for o in ops))
        self.assertTrue(any(o.get("delete_section") == "Refinement gaps" for o in ops))
        self.assertEqual(self.py(os.path.join(BIN, "apply-spec-patch.py"), self.out, "--source", self.src)[0], 0)
        code, msg = self.py(os.path.join(BIN, "gen-syntax-tables.py"), "--source", self.dir,
                            "--findings", os.path.join(self.tmp.name, "f.md"), "--write")
        self.assertEqual(code, 0, msg)
        doc = os.path.join(self.tmp.name, "v13-sgai-spec.md")
        self.assertEqual(self.py(os.path.join(BIN, "assemble-spec.py"), "--source", self.dir, "--out", doc)[0], 0)
        code, msg = self.py(os.path.join(BIN, "lint-spec.py"), doc)
        self.assertNotIn("L-COMMENT", msg)
        self.assertNotIn("L-GAPS", msg)
        self.assertIn("build iteration 13.\n", read(doc))
        os.remove(self.out)
        self.assertEqual(run("--source", self.src, "--out", self.out)[0], 0)

    def test_redundant_override_is_dropped_not_stripped(self):
        code, _ = run("--source", self.src, "--out", self.out)
        ops = [o for o in json.loads(read(self.out))["ops"] if "file" in o]
        dropped = [o for o in ops if o["replace"] == "" and o["find"].lstrip().startswith("override:")]
        self.assertEqual(len(dropped), 2, [o["find"] for o in dropped])
        kept = [o for o in ops if "LinearRelationType" in o["find"]]
        self.assertEqual(kept[0]["replace"].strip(), "type: '`LinearRelationType` (§5.1.6)'")


if __name__ == "__main__":
    unittest.main()

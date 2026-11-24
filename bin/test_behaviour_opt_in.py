#!/usr/bin/env python3
"""ADR 0087: the behaviour battery runs only with an explicit `--behaviour`.

Fails if a default path can reach the battery's executor:
`conformance.behaviour.run` / `drive` / `main`, or `bin/players/behaviour.mjs`.

Measured, not only grepped:

- check-dash-conformance.py is run in process, in every mode that is not
  `--behaviour` (document, --source, --demo, --players, --dashif, the error
  paths), with the executor replaced by traps that raise a BaseException and
  with subprocess.Popen refusing any command that carries `--behaviour` or
  `behaviour.mjs`. A run that touches a trap is red. The Players' and the
  DASH-IF tool's runs are stubbed (they need Chromium and docker); what they
  run is covered by the static scan below.
- promote.py runs its whole gate sequence (dry run and real, into a scratch
  dist) with its command runner replaced by a recorder: no recorded command
  may carry the flag or the runner, and every recorded
  check-dash-conformance.py command is then run in process as above.
- The prompts (prompts/**, .github-ai/prompts/**) are read by what they
  invoke: every check-dash-conformance.py command in a fenced block is run in
  process as above, and no prompt mentions `--behaviour`, `behaviour.mjs` or
  `conformance.behaviour` at all.
- bin/ is scanned: the Python files by their syntax tree (an import of the
  executor by name, an attribute or getattr of run/drive/main on the module,
  a string carrying the flag or the runner; docstrings are prose and are not
  read; importing the module for a helper such as fixtures_of is allowed),
  the other text files by text. The files that are the battery are exempt:
  check-dash-conformance.py (its --behaviour branch is what the runtime
  part above holds), conformance/behaviour.py, conformance/behaviour_compare.py,
  players/behaviour.mjs, players/adapters/sgai.js, and this file.

Each scan has its positive control: it finds the entry in
check-dash-conformance.py and the runner in behaviour.py; each trap has
one: `--behaviour` reaches it.

What a green does NOT say: that the Players' level 3a (stubbed here) does
not pick the `sgai` adapter by name; that a path invoking the executor in a
way none of the above reads (a shell script outside bin/ and prompts/, an
eval) does not exist.

Run: python3 bin/test_behaviour_opt_in.py   (re-runs itself under uv for lxml
and PyYAML; no Chromium, a few seconds)
"""
import ast
import contextlib
import importlib.util
import io
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

BIN = Path(__file__).resolve().parent
ROOT = BIN.parent
sys.path.insert(0, str(BIN))

if __name__ == "__main__":
    from conformance.deps import ensure_yaml
    ensure_yaml(os.path.abspath(__file__), sys.argv[1:])

EXECUTOR = ("run", "drive", "main")
FLAG = re.compile(r"(?<![\w-])--behaviour\b")
RUNNER = "behaviour.mjs"
EDGES = "run-edges.py"   # reference-player/test/edges/: the battery on the edge vectors
SCRATCH = os.environ.get("XDG_RUNTIME_DIR") or None  # RAM and private when there is one
# The battery itself, relative to bin/.
EXEMPT = {"check-dash-conformance.py", "conformance/behaviour.py", "conformance/behaviour_compare.py",
          "players/behaviour.mjs", "players/adapters/sgai.js", Path(__file__).name}
PROMPT_TEXT = [(FLAG, "the --behaviour flag"), (re.compile(re.escape(RUNNER)), "the runner behaviour.mjs"),
               (re.compile(re.escape(EDGES)), "the edge vectors' runner run-edges.py"),
               (re.compile(r"conformance[./]behaviour\b(?!_)"), "the module conformance.behaviour")]


class ExecutorCalled(BaseException):
    """BaseException so that no `except Exception` on the way can swallow it."""


# ---------------------------------------------------------------- runtime

def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _carries(args) -> str | None:
    flat = args if isinstance(args, str) else " ".join(map(str, args))
    if RUNNER in flat or FLAG.search(flat):
        return flat
    return None


@contextlib.contextmanager
def executor_trapped(calls: list, stubs: list):
    """The executor's entry points and any process carrying the flag or the
    runner raise ExecutorCalled and are recorded in `calls`. The Players'
    and the DASH-IF tool's runs are stubbed and recorded in `stubs`."""
    from conformance import behaviour, dashif, players

    def trap(name):
        def f(*a, **k):
            calls.append(f"conformance.behaviour.{name}")
            raise ExecutorCalled(name)
        return f

    real = subprocess.Popen

    class Guarded(real):
        def __init__(self, args, *a, **k):
            hit = _carries(args)
            if hit:
                calls.append(f"process: {hit}")
                raise ExecutorCalled(hit)
            super().__init__(args, *a, **k)

    def players_stub(docs, report, raw=None):
        stubs.append("players.run_documents")
        return []

    def dashif_stub(blocks, isodir):
        stubs.append("dashif.run")
        return {"ran": False, "reason": "stubbed by test_behaviour_opt_in"}

    with mock.patch.multiple(behaviour, **{n: trap(n) for n in EXECUTOR}), \
            mock.patch.object(subprocess, "Popen", Guarded), \
            mock.patch.object(players, "run_documents", players_stub), \
            mock.patch.object(dashif, "run", dashif_stub):
        yield


_RUNS = {}


def run_conformance(argv: list) -> tuple:
    """check-dash-conformance.py's main(argv) in process, from the project
    root, the executor trapped. -> (exit or None when a trap fired, calls,
    stubs, output). The same command line runs once per process — output
    paths aside, paths taken from the root, options in any order (main's
    parser does not read their order): the run is deterministic and the
    --source one costs seconds."""
    key, args = set(), list(argv)
    while args:
        a = args.pop(0)
        if a in ("--out-md", "--out-json", "--save-raw") and args:
            key.add((a, "OUT"))
            args.pop(0)
        elif a in ("--source", "--context", "--xsd") and args:
            key.add((a, os.path.relpath(os.path.join(ROOT, args.pop(0)), ROOT)))
        else:
            key.add((a,))
    key = frozenset(key)
    if key not in _RUNS:
        _RUNS[key] = _run_conformance(argv)
    return _RUNS[key]


def _run_conformance(argv: list) -> tuple:
    calls, stubs, out = [], [], io.StringIO()
    cwd = os.getcwd()
    try:
        os.chdir(ROOT)
        with executor_trapped(calls, stubs), contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            mod = _load(BIN / "check-dash-conformance.py", "check_dash_conformance_opt_in")
            try:
                code = mod.main(list(argv))
            except ExecutorCalled:
                code = None
            except SystemExit as e:
                code = e.code
    finally:
        os.chdir(cwd)
    return code, calls, stubs, out.getvalue()


def _outputs_to(argv: list, tmp: str) -> list:
    """--out-md / --out-json values go to scratch, whatever placeholder the
    prompt wrote."""
    argv = list(argv)
    for i, a in enumerate(argv[:-1]):
        if a in ("--out-md", "--out-json", "--save-raw"):
            argv[i + 1] = os.path.join(tmp, f"{i}-{a.strip('-')}")
    return argv


# ---------------------------------------------------------------- prompts

def prompt_files() -> list:
    return sorted(p for d in (ROOT / "prompts", ROOT / ".github-ai" / "prompts") if d.is_dir()
                  for p in d.rglob("*.prompt"))


def fenced_commands(text: str, script: str) -> list:
    """argv after `script` for every command in a fenced block that invokes
    it; backslash continuations joined, cut at the first shell operator."""
    out, inside, buf = [], False, ""
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            inside, buf = not inside, ""
            continue
        if not inside:
            continue
        buf += line.rstrip()
        if buf.endswith("\\"):
            buf = buf[:-1] + " "
            continue
        cmd, buf = buf, ""
        k = cmd.find(script)
        if k < 0:
            continue
        try:
            toks = shlex.split(cmd[k + len(script):], comments=True)
        except ValueError:
            toks = cmd[k + len(script):].split()
        args = []
        for t in toks:
            if t in ("|", "||", "&&", ";", "&") or t.startswith((">", "2>")):
                break
            args.append(t)
        out.append(args)
    return out


def text_findings(text: str, rules=PROMPT_TEXT) -> list:
    return [f"{n}: {what}" for n, line in enumerate(text.splitlines(), 1)
            for rx, what in rules if rx.search(line)]


# ---------------------------------------------------------------- bin/ by syntax

def _docstrings(tree) -> set:
    ids = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) \
                    and isinstance(first.value.value, str):
                ids.add(id(first.value))
    return ids


def _dotted(node) -> str:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def py_findings(src: str) -> list:
    """Every way a Python source reaches the executor: by name import, by
    attribute or getattr on the module, or by a string carrying the flag or
    the runner (docstrings excluded)."""
    tree = ast.parse(src)
    docs = _docstrings(tree)
    alias, found = set(), []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[-1] == "behaviour":
                    alias.add(a.asname or a.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod.split(".")[-1] == "behaviour":
                for a in node.names:
                    if a.name in EXECUTOR or a.name == "*":
                        found.append(f"{node.lineno}: imports {a.name} from {'.' * node.level}{mod}")
            else:
                for a in node.names:
                    if a.name == "behaviour":
                        alias.add(a.asname or "behaviour")
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in EXECUTOR:
            base = _dotted(node.value)
            if base in alias or base.split(".")[-1] == "behaviour":
                found.append(f"{node.lineno}: {base}.{node.attr}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "getattr" \
                and len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) \
                and node.args[1].value in EXECUTOR and _dotted(node.args[0]).split(".")[-1] in alias | {"behaviour"}:
            found.append(f"{node.lineno}: getattr(..., {node.args[1].value!r})")
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in docs:
            if FLAG.search(node.value):
                found.append(f"{node.lineno}: string carries --behaviour")
            for name in (RUNNER, EDGES):
                if name in node.value:
                    found.append(f"{node.lineno}: string carries {name}")
    return sorted(set(found))


def bin_files():
    for p in sorted(BIN.rglob("*")):
        rel = p.relative_to(BIN).as_posix()
        if not p.is_file() or "node_modules" in p.parts or "__pycache__" in p.parts:
            continue
        if rel.startswith("conformance/fixtures/") or rel in EXEMPT:
            continue
        yield rel, p


def bin_findings(select) -> dict:
    out = {}
    for rel, p in bin_files():
        if not select(rel):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        f = py_findings(text) if p.suffix == ".py" else text_findings(text, PROMPT_TEXT[:2])
        if f:
            out[rel] = f
    return out


def _is_test(rel):
    return re.fullmatch(r"test_[^/]*\.py", rel) is not None


# ---------------------------------------------------------------- tests

class Traps(unittest.TestCase):
    """The traps themselves: --behaviour reaches them, so a green elsewhere
    is not a trap that never fires."""

    def test_flag_reaches_the_trap(self):
        code, calls, _, _ = run_conformance(["--behaviour", "--replay", "/nonexistent.json"])
        self.assertIsNone(code)
        self.assertEqual(calls, ["conformance.behaviour.main"])

    def test_process_trap(self):
        calls = []
        with executor_trapped(calls, []):
            with self.assertRaises(ExecutorCalled):
                subprocess.run(["node", "behaviour.mjs"])
            with self.assertRaises(ExecutorCalled):
                subprocess.run(["python3", "x.py", "--behaviour"])
            subprocess.run(["true", "--behaviours-not"], check=True)  # not the flag
        self.assertEqual(len(calls), 2)


class DefaultModes(unittest.TestCase):
    """check-dash-conformance.py without --behaviour never reaches the executor."""

    MODES = [
        [], ["--help"], ["--bogus"], ["--source", "/nonexistent-dir"], ["no-such-spec.md"],
        ["--source", "spec-source", "--out-md", os.devnull],
        ["dist/sgai-spec.md", "--out-md", os.devnull],
        ["dist/sgai-spec.md", "--players", "--dashif", "--out-md", os.devnull],
        ["--demo"],
    ]

    def test_every_default_mode(self):
        for argv in self.MODES:
            with self.subTest(argv=argv):
                code, calls, stubs, out = run_conformance(argv)
                self.assertEqual(calls, [], f"{argv} reached the executor:\n{out[-2000:]}")
                self.assertIn(code, (0, 1, 2, 64), f"{argv} exit {code}:\n{out[-2000:]}")
                if "--players" in argv:  # the mode did go down its branch
                    self.assertEqual(stubs, ["players.run_documents", "dashif.run"])


class Promote(unittest.TestCase):
    """promote.py's gates, real and dry, record their commands; none carries
    the flag or the runner, and its conformance gate run in process does not
    reach the executor."""

    def _commands(self, dry: bool) -> list:
        pr = _load(BIN / "promote.py", "promote_opt_in")
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            root, dist = os.path.join(tmp, "root"), os.path.join(tmp, "dist")
            for pat in pr.PUBLISHED.values():
                p = os.path.join(root, pat.format(v="v0"))
                os.makedirs(os.path.dirname(p), exist_ok=True)
                Path(p).write_text("stub\n", encoding="utf-8")
            recorded = []

            def record(*args):
                recorded.append([a.replace(root, str(ROOT)) for a in args])
                line = "BETTER THAN PUBLISHED (stub)" if "compare-candidates" in args[0] else "stub"
                return 0, line

            calls, out = [], io.StringIO()
            with mock.patch.object(pr, "ROOT", root), mock.patch.object(pr, "run", record), \
                    executor_trapped(calls, []), contextlib.redirect_stdout(out):
                try:
                    code = pr.main(["v0", "--dist", dist] + (["--dry-run"] if dry else []))
                except ExecutorCalled:
                    code = None
            self.assertEqual(calls, [], out.getvalue())
            self.assertEqual(code, 0, out.getvalue())  # every gate ran
        return recorded

    def test_gates(self):
        for dry in (True, False):
            recorded = self._commands(dry)
            self.assertTrue(recorded)
            conf = []
            for args in recorded:
                with self.subTest(dry=dry, command=args):
                    self.assertIsNone(_carries(args))
                if os.path.basename(args[0]) == "check-dash-conformance.py":
                    conf.append(args[1:])
            for argv in conf:
                with self.subTest(dry=dry, conformance=argv):
                    code, calls, _, out = run_conformance(argv)
                    self.assertEqual(calls, [], out[-2000:])
                    self.assertIn(code, (0, 1, 2, 64))


class Prompts(unittest.TestCase):
    """build-all, the incremental and every prompt they dispatch."""

    def test_no_prompt_mentions_the_battery(self):
        found = {str(p.relative_to(ROOT)): f for p in prompt_files()
                 if (f := text_findings(p.read_text(encoding="utf-8")))}
        self.assertEqual(found, {})

    def test_conformance_commands_of_the_prompts(self):
        cmds = {}
        for p in prompt_files():
            for argv in fenced_commands(p.read_text(encoding="utf-8"), "check-dash-conformance.py"):
                cmds.setdefault(str(p.relative_to(ROOT)), []).append(argv)
        self.assertIn("prompts/build-all.prompt", cmds)  # the reader finds Step 8.0
        with tempfile.TemporaryDirectory(dir=SCRATCH) as tmp:
            seen = set()
            for f, lst in cmds.items():
                for argv in lst:
                    argv = _outputs_to(argv, tmp)
                    if tuple(argv) in seen:
                        continue
                    seen.add(tuple(argv))
                    with self.subTest(prompt=f, argv=argv):
                        self.assertIsNone(_carries(argv))
                        code, calls, _, out = run_conformance(argv)
                        self.assertEqual(calls, [], out[-2000:])
                        self.assertIn(code, (0, 1, 2, 64))

    def test_reader(self):
        text = ("prose `bin/check-dash-conformance.py --behaviour` outside a block\n"
                "```bash\npython3 bin/check-dash-conformance.py --source spec-source \\\n"
                "  --out-md W/a.md > log 2>&1\n```\n")
        self.assertEqual(fenced_commands(text, "check-dash-conformance.py"),
                         [["--source", "spec-source", "--out-md", "W/a.md"]])
        self.assertEqual(len(text_findings(text)), 1)
        self.assertEqual(text_findings("--behaviours and behaviour_compare and a behaviour"), [])


class Bin(unittest.TestCase):
    """bin/: no script and no test of the suite reaches the executor."""

    def test_scripts(self):
        self.assertEqual(bin_findings(lambda rel: not _is_test(rel)), {})

    def test_suite(self):
        self.assertEqual(bin_findings(_is_test), {})

    def test_positive_controls(self):
        entry = py_findings((BIN / "check-dash-conformance.py").read_text(encoding="utf-8"))
        self.assertTrue(any("--behaviour" in f for f in entry), entry)
        self.assertTrue(any("behaviour.main" in f for f in entry), entry)
        runner = py_findings((BIN / "conformance" / "behaviour.py").read_text(encoding="utf-8"))
        self.assertTrue(any(RUNNER in f for f in runner), runner)

    def test_rules(self):
        cases = {
            "from conformance import behaviour\nbehaviour.run(1)": 1,
            "from conformance import behaviour as b\nb.drive()": 1,
            "import conformance.behaviour\nconformance.behaviour.main([])": 1,
            "from conformance.behaviour import main": 1,
            "from .behaviour import *": 1,
            "from conformance import behaviour\ngetattr(behaviour, 'run')()": 1,
            "x = ['node', 'behaviour.mjs']": 1,
            "argv = ['--behaviour']": 1,
            "subprocess.run(['python3', 'reference-player/test/edges/run-edges.py'])": 1,
            '"""Docstring naming behaviour.mjs and --behaviour."""': 0,
            "from conformance import behaviour\nbehaviour.fixtures_of(v, s)": 0,
            "from conformance.behaviour_compare import compare\ncompare()": 0,
            "players.run(ctx, report)\nrunner.main()": 0,
            "": 0,
        }
        for src, n in cases.items():
            with self.subTest(src=src):
                self.assertEqual(len(py_findings(src)), n, py_findings(src))


if __name__ == "__main__":
    unittest.main()

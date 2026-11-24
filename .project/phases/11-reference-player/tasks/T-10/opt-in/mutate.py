"""Mutation campaign for bin/test_behaviour_opt_in.py, on a scratch copy.
One break per path; each run only the opt-in test; restore after each."""
import shutil, subprocess, sys
from pathlib import Path
P = Path(sys.argv[1])
UV = ["uv", "run", "-q", "--no-project", "--with", "lxml==6.1.3", "--with", "pyyaml==6.0.3", "python3", "-B"]

def edit(rel, old, new):
    p = P / rel
    s = p.read_text()
    if old == "":
        p.write_text(s + new)
        return
    assert s.count(old) == 1, (rel, old)
    p.write_text(s.replace(old, new))

M = [
 ("M1 build-all.prompt: --behaviour on Step 8.0's conformance command", "prompts/build-all.prompt",
  "python3 bin/check-dash-conformance.py --source spec-source \\\n",
  "python3 bin/check-dash-conformance.py --source spec-source --behaviour \\\n"),
 ("M2 apply-context-delta.prompt (dispatched by the incremental): runs behaviour.mjs", "prompts/2-build/apply-context-delta.prompt",
  "python3 bin/check-dash-conformance.py --source spec-source --out-json W/conf-base.json --out-md W/conf-base.md\n",
  "python3 bin/check-dash-conformance.py --source spec-source --out-json W/conf-base.json --out-md W/conf-base.md\n(cd bin/players && node behaviour.mjs < jobs.json)\n"),
 ("M3 promote.py: a gate that shells out to check-dash-conformance.py --behaviour", "bin/promote.py",
  "    return res\n\n\ndef write_provenance",
  "    res.append((\"behaviour\",) + run(os.path.join(BIN, \"check-dash-conformance.py\"), \"--behaviour\"))\n    return res\n\n\ndef write_provenance"),
 ("M4 promote.py: calls conformance.behaviour.run in process", "bin/promote.py",
  "    return res\n\n\ndef write_provenance",
  "    sys.path.insert(0, BIN)\n    from conformance import behaviour\n    behaviour.run(None, [], [], 1, None)\n    return res\n\n\ndef write_provenance"),
 ("M5 check-dash-conformance.py: document mode calls behaviour.run", "bin/check-dash-conformance.py",
  "    report = Report()\n    ctx = runner.load(spec, context_dir, report)\n",
  "    report = Report()\n    from conformance import behaviour\n    behaviour.run(Path(HERE).parent / 'spec-source', [], [], 2, report)\n    ctx = runner.load(spec, context_dir, report)\n"),
 ("M6 check-dash-conformance.py: --source mode calls behaviour.main", "bin/check-dash-conformance.py",
  "    report, _ = src.run(source, context_dir)\n",
  "    report, _ = src.run(source, context_dir)\n    from conformance import behaviour\n    behaviour.main([], source)\n"),
 ("M7 conformance/runner.py (a helper of the default path): calls behaviour.drive", "bin/conformance/runner.py",
  "", "\nfrom . import behaviour as _b\n_b_go = lambda: _b.drive('', [], 1)\n"),
 ("M8 test_behaviour_compare.py (the suite): a test calls the executor", "bin/test_behaviour_compare.py",
  "from conformance.model import Outcome  # noqa: E402\n",
  "from conformance.model import Outcome  # noqa: E402\n\n\ndef _never_called():\n    behaviour.run(None, [], [], 1, None)\n"),
 ("M9 players/run.mjs (level 3a): spawns behaviour.mjs", "bin/players/run.mjs",
  "", "\nimport { spawn as _sp } from 'node:child_process'; const _go = () => _sp('node', ['behaviour.mjs']);\n"),
]

def run():
    r = subprocess.run(UV + [str(P / "bin/test_behaviour_opt_in.py")], capture_output=True, text=True, cwd=P)
    return r.returncode, r.stdout + r.stderr

code, out = run()
print(f"BASELINE (copy, unmutated): exit {code}  {out.strip().splitlines()[-1]}")
for name, rel, old, new in M:
    keep = (P / rel).read_text()
    edit(rel, old, new)
    try:
        code, out = run()
    finally:
        (P / rel).write_text(keep)
    fails = [l for l in out.splitlines() if l.startswith(("FAIL:", "ERROR:"))]
    print(f"\n{name}\n  exit {code} -> {'RED' if code else 'GREEN (finding)'}")
    for l in fails:
        print("  " + l)
    for l in out.splitlines():
        if l.startswith("AssertionError") or "reached the executor" in l:
            print("    " + l[:300])
code, out = run()
print(f"\nAFTER RESTORE: exit {code}  {out.strip().splitlines()[-1]}")

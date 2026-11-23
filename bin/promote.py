#!/usr/bin/env python3
"""Promote a candidate into dist/, only when every gate holds (ADR 0073).

The gates, in order; every one runs and every failure is named:
  1. assemble   output/v<N>-sgai-spec.md is the assembly of spec-source/
                (bin/assemble-spec.py --check)
  2. lint       bin/lint-spec.py on the candidate exits 0
  3. trace      bin/check-trace.py on output-analysis/v<N>-trace.json exits 0
  4. promotable bin/check-promotable.py on the candidate's sidecars exits 0
  5. compare    bin/compare-candidates.py v<N> says BETTER THAN PUBLISHED
  6. conformance bin/check-dash-conformance.py on the candidate exits 0
     (with its extension XSD, output/v<N>-sgai-extension.xsd)
  7. files      every file of the published set exists for the candidate

When all hold, it copies the published set into the dist directory under
unversioned names — sgai-spec.md, sgai-extension.xsd, spec-validation.md,
detail-review.md, conformance-tests.md, conformance-tests.json,
dash-conformance-audit.md, comparison.md, trace.json — writes
PROVENANCE.md, and records inputs.sha256 (context/, context-analysis/,
prompts/ and spec-source/, as bin/check-dist-freshness.py reads them).

Usage:
  bin/promote.py v<N> [--dist DIR] [--dry-run]

--dist defaults to dist/; tests point it at a scratch directory. --dry-run
runs the gates and copies nothing.

Exit codes: 0 promoted (or, with --dry-run, would be) · 1 a gate failed,
nothing copied · 2 a gate could not tell, nothing copied · 64 wrong command
line.
"""
from __future__ import annotations

import datetime
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
PY = sys.executable

PUBLISHED = {  # name in dist/ : path pattern for the candidate
    "sgai-spec.md": "output/{v}-sgai-spec.md",
    "sgai-extension.xsd": "output/{v}-sgai-extension.xsd",
    "spec-validation.md": "output-analysis/{v}-spec-validation.md",
    "detail-review.md": "output-analysis/{v}-detail-review.md",
    "conformance-tests.md": "output-analysis/{v}-conformance-tests.md",
    "conformance-tests.json": "output-analysis/{v}-conformance-tests.json",
    "dash-conformance-audit.md": "output-analysis/{v}-dash-conformance-audit.md",
    "comparison.md": "output-analysis/{v}-comparison.md",
    "trace.json": "output-analysis/{v}-trace.json",
}


def usage(msg):
    sys.stderr.write(msg + "\n\n" + __doc__)
    sys.exit(64)


def run(*args):
    p = subprocess.run([PY, "-I", *args], capture_output=True, text=True, cwd=ROOT)
    out = (p.stdout + p.stderr).strip().splitlines()
    return p.returncode, (out[-1] if out else "")


def gates(v, dist):
    """[(name, exit, line)] — exit 0 holds, 1 fails, 2 cannot tell."""
    path = {k: os.path.join(ROOT, pat.format(v=v)) for k, pat in PUBLISHED.items()}
    res = []
    missing = [os.path.relpath(p, ROOT) for p in path.values() if not os.path.isfile(p)]
    res.append(("files", 1 if missing else 0, "missing: " + ", ".join(missing) if missing else "all present"))
    spec = path["sgai-spec.md"]
    if not os.path.isfile(spec):
        return res
    res.append(("assemble",) + run(os.path.join(BIN, "assemble-spec.py"), "--check", spec))
    res.append(("lint",) + run(os.path.join(BIN, "lint-spec.py"), spec))
    if os.path.isfile(path["trace.json"]):
        res.append(("trace",) + run(os.path.join(BIN, "check-trace.py"), path["trace.json"], "--spec", spec))
    else:
        res.append(("trace", 2, "no trace"))
    with tempfile.TemporaryDirectory() as tmp:
        for name in ("spec-validation.md", "detail-review.md", "conformance-tests.json", "dash-conformance-audit.md"):
            if os.path.isfile(path[name]):
                shutil.copy(path[name], os.path.join(tmp, name))
        res.append(("promotable",) + run(os.path.join(BIN, "check-promotable.py"), "--from", tmp))
    code, line = run(os.path.join(BIN, "compare-candidates.py"), v, "--dist", dist, "--out", path["comparison.md"])
    if code == 0 and not line.startswith("BETTER THAN PUBLISHED"):
        code = 1
    res.append(("compare", code, line))
    if os.path.isfile(path["sgai-extension.xsd"]):
        res.append(("conformance",) + run(os.path.join(BIN, "check-dash-conformance.py"), spec,
                                          "--xsd", path["sgai-extension.xsd"]))
    else:
        res.append(("conformance", 2, "no extension XSD"))
    return res


def write_provenance(dist, v, res):
    today = datetime.date.today().isoformat()
    lines = ["# What is published here, and where it came from", "",
             "| | |", "|---|---|",
             f"| **Candidate promoted** | `{v}` |",
             f"| **Promoted on** | {today} |",
             "| **Promoted by** | `bin/promote.py`, every gate in its `--help` holding |", "",
             f"The files here are `output/{v}-*` and `output-analysis/{v}-*` under names without",
             "the version. `inputs.sha256` records the inputs the candidate was built from",
             "(`context/`, `context-analysis/`, `prompts/`, `spec-source/`); "
             "`bin/check-dist-freshness.py` compares against it.", "",
             "## The gates", "", "| Gate | Result |", "|---|---|"]
    lines += [f"| {n} | {line.replace('|', '/')} |" for n, _, line in res]
    with open(os.path.join(dist, "PROVENANCE.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def main(argv):
    v = None
    dist = os.path.join(ROOT, "dist")
    dry = False
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--dist":
            if i + 1 >= len(argv):
                usage("--dist needs a directory")
            dist = os.path.abspath(argv[i + 1])
            i += 2
            continue
        if a == "--dry-run":
            dry = True
        elif re.match(r"^v\d+(\.\d+)?$", a) and v is None:
            v = a
        else:
            usage(f"unknown argument {a}")
        i += 1
    if v is None:
        usage("a candidate version v<N> or v<N.M> is required")
    res = gates(v, dist)
    for name, code, line in res:
        mark = {0: "holds", 1: "FAILS", 2: "CANNOT TELL"}.get(code, f"exit {code}")
        print(f"{name:12} {mark:12} {line}")
    worst = max((c if c in (0, 1, 2) else 2) for _, c, _ in res)
    if worst == 2:
        print(f"NOT PROMOTED: {v} — a gate could not tell")
        return 2
    if worst == 1:
        print(f"NOT PROMOTED: {v} — " + ", ".join(n for n, c, _ in res if c == 1) + " fail")
        return 1
    if dry:
        print(f"WOULD PROMOTE: {v}")
        return 0
    os.makedirs(dist, exist_ok=True)
    for name, pat in PUBLISHED.items():
        shutil.copy(os.path.join(ROOT, pat.format(v=v)), os.path.join(dist, name))
    write_provenance(dist, v, res)
    spec = importlib.util.spec_from_file_location("freshness", os.path.join(BIN, "check-dist-freshness.py"))
    fr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fr)
    rows = fr.manifest_now()
    with open(os.path.join(dist, "inputs.sha256"), "w", encoding="utf-8") as fh:
        fh.write(f"# Inputs of the build currently published in {os.path.basename(dist)}/ ({v}).\n"
                 "# Recorded by bin/promote.py. Compared by content, never by date.\n")
        for rel in sorted(rows):
            fh.write(f"{rows[rel]}  {rel}\n")
    print(f"PROMOTED: {v} → {dist}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

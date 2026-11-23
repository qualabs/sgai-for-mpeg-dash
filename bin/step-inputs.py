#!/usr/bin/env python3
"""Does a pre-spec step have to run again? Answered by the content of its
inputs, never by date (ADR 0072).

Each step declares its inputs below. After a step builds its output, the
orchestrator records the sha256 of every input beside it
(`<output>.inputs.sha256`); before running the step again it asks whether
those hashes still hold. A `touch` changes nothing; an edit that keeps the
mtime changes everything.

Usage:
  bin/step-inputs.py check  <step>   exit 0 fresh (skip), 1 stale (run),
                                     naming every input that moved
  bin/step-inputs.py record <step>   write the manifest after building
  bin/step-inputs.py list            the steps and their inputs

Steps: analyze-dash-gap, build-error-semantics. `analyze-iab-ad-templates`
is not here on purpose: its source is a live external document, so it
always runs.

What a green says: the declared inputs and the step's own prompt are byte
for byte what they were when the output was built. What it does not say:
that the declared list is complete — a step reading a file not declared
here is not tracked.

Exit codes: 0 fresh · 1 stale · 2 no output or no manifest (cannot tell:
run the step) · 64 wrong command line.
"""
from __future__ import annotations

import glob
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STEPS = {
    "analyze-dash-gap": {
        "output": "context-analysis/dash-gap-analysis.md",
        "inputs": ["context/*.md", "prompts/1-pre-spec/analyze-dash-gap.prompt"],
    },
    "build-error-semantics": {
        "output": "context-analysis/error-semantics.md",
        "inputs": ["context/03-requirements.md", "context/05-dash-linear-interfaces.md",
                   "prompts/1-pre-spec/build-error-semantics.prompt"],
    },
}


def usage(msg):
    sys.stderr.write(msg + "\n\n" + __doc__)
    sys.exit(64)


def inputs_of(step, root=ROOT):
    files = []
    for pat in STEPS[step]["inputs"]:
        files += sorted(glob.glob(os.path.join(root, pat)))
    return files


def hashes(step, root=ROOT):
    out = {}
    for f in inputs_of(step, root):
        with open(f, "rb") as fh:
            out[os.path.relpath(f, root)] = hashlib.sha256(fh.read()).hexdigest()
    return out


def manifest_path(step, root=ROOT):
    return os.path.join(root, STEPS[step]["output"] + ".inputs.sha256")


def read_manifest(path):
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                digest, _, rel = line.partition("  ")
                rows[rel] = digest
    return rows


def main(argv, root=ROOT):
    if not argv:
        usage("a command is required")
    cmd = argv[0]
    if cmd == "list" and len(argv) == 1:
        for s, d in STEPS.items():
            print(f"{s} -> {d['output']}: " + ", ".join(d["inputs"]))
        return 0
    if cmd not in ("check", "record") or len(argv) != 2 or argv[1] not in STEPS:
        usage(f"usage: check|record <step>, step one of {', '.join(STEPS)}")
    step = argv[1]
    now = hashes(step, root)
    man = manifest_path(step, root)
    if cmd == "record":
        if not os.path.isfile(os.path.join(root, STEPS[step]["output"])):
            print(f"exit 2: {STEPS[step]['output']} does not exist; build it before recording")
            return 2
        with open(man, "w", encoding="utf-8") as fh:
            fh.write(f"# inputs of {step} when {STEPS[step]['output']} was built\n")
            for rel, d in sorted(now.items()):
                fh.write(f"{d}  {rel}\n")
        print(f"recorded {len(now)} inputs in {os.path.relpath(man, root)}")
        return 0
    if not os.path.isfile(os.path.join(root, STEPS[step]["output"])) or not os.path.isfile(man):
        print(f"exit 2: no output or no manifest for {step}: cannot tell, run it")
        return 2
    old = read_manifest(man)
    moved = sorted(set(old) ^ set(now) | {k for k in now if k in old and old[k] != now[k]})
    if moved:
        print(f"stale: {step} — {len(moved)} input(s) moved:")
        for m in moved:
            state = "added" if m not in old else "removed" if m not in now else "changed"
            print(f"  {state}: {m}")
        return 1
    print(f"fresh: {step} — {len(now)} inputs as recorded; skip")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""The reference's own regression tests of the 6th edition's linear model: the
edge vectors E1-E13 beside this file, run on the reference in headless
Chromium through the behaviour battery. They test the base standard's rules
(Table 57, the queue, @clip, @startWithOffset, @returnOffset, a List MPD's
Linked Periods, a pause in a linear ad), not criteria of context/03, which is
why they are here and not in spec-source/behaviour/. Opt-in like the battery
(ADR 0087): nothing runs them by default.

    python3 reference-player/test/edges/run-edges.py [E3 E5 ...] [battery options]

Positional names pick vectors (E3 E5 ...; all when none); any other argument
goes to `check-dash-conformance.py --behaviour` as it is (--concurrency,
--clock, --out-json, --save-raw, --reference ...). Every vector runs in D1.
Exit: the battery's (0 nothing fails, 1 a FAIL, 2 cannot tell, 64 wrong
command line)."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def edge_files(names=()):
    files = sorted(HERE.glob("E*.yaml"), key=lambda f: int(f.name[1:].split("-")[0]))
    if names:
        files = [f for f in files if f.name.split("-")[0] in names]
    return files


def main(argv):
    if any(a in ("-h", "--help") for a in argv):
        print(__doc__)
        return 0
    names = [a for a in argv if a[:1] == "E" and a[1:].isdigit()]
    rest = [a for a in argv if a not in names]
    files = edge_files(names)
    if names and len(files) != len(set(names)):
        sys.stderr.write(f"no edge vector for some of {' '.join(names)}\n")
        return 64
    cmd = [sys.executable, str(ROOT / "bin" / "check-dash-conformance.py"), "--behaviour", "--class", "D1"]
    cmd += [a for f in files for a in ("--vector", str(f))] + rest
    return subprocess.run(cmd, cwd=ROOT).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

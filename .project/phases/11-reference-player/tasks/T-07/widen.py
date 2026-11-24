"""Copies of behaviour vectors for the mutation campaign on this machine:
the file-wide `tolerance` set to TOL ms and, with EXTRA > 0, `observe_until`
and the last presentation segment's end moved EXTRA ms later (as
../T-06/extend.py). Nothing else changes: a per-segment tolerance (R16.1's
17 ms), geometry tolerances (percentage points) and every expected value stay.

Why: on this 2-core machine the page plays at 0.3-0.9x and the harness makes
the viewer's actions on the wall clock, so a pause at session 3 s finds the
programme 0.5-2 s short of 3 s. Every pause test then FAILs its presentation
on either clock, with the module right or wrong, and a break cannot turn a
PASS into a FAIL there. With the tolerance at TOL, a break whose effect is
larger than TOL can still be seen; one whose effect is smaller cannot.

Usage: widen.py OUT_DIR TOL EXTRA VECTOR.yaml ..."""
import pathlib
import sys

import yaml

out, tol, extra = pathlib.Path(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
for f in sys.argv[4:]:
    v = yaml.safe_load(open(f))
    v["tolerance"] = tol
    if extra:
        old = v["observe_until"]
        v["observe_until"] = old + extra * v["timescale"] // 1000
        for o in v["outcomes"].values():
            pres = o["presentation"]
            if pres and pres[-1]["end"] == old:
                pres[-1] = dict(pres[-1])
                pres[-1]["end"] = v["observe_until"]
    (out / pathlib.Path(f).name).write_text(yaml.safe_dump(v, sort_keys=False))

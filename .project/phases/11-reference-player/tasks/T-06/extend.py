"""Copies of behaviour vectors with observe_until extended by EXTRA ms and
the last presentation segment's end with it; nothing else changes."""
import sys, yaml, pathlib
out = pathlib.Path(sys.argv[1]); extra = int(sys.argv[2])
for f in sys.argv[3:]:
    v = yaml.safe_load(open(f))
    old = v["observe_until"]; v["observe_until"] = old + extra * v["timescale"] // 1000
    for o in v["outcomes"].values():
        pres = o["presentation"]
        if pres and pres[-1]["end"] == old:
            pres[-1] = dict(pres[-1]); pres[-1]["end"] = v["observe_until"]
    (out / pathlib.Path(f).name).write_text(yaml.safe_dump(v, sort_keys=False))

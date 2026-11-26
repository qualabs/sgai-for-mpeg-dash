"""Trimmed copies of the vectors: keep only the (class, variant) jobs listed.
Usage: build_copies.py OUTDIR SPEC_SOURCE JOBS_FILE  (lines: name|class|variant)"""
import sys, yaml, copy
from pathlib import Path
out, src, jobs_file = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
want = {}
for line in open(jobs_file):
    line = line.strip()
    if not line:
        continue
    name, cls, var = line.split("|")
    want.setdefault(name, set()).add((cls, var))
out.mkdir(parents=True, exist_ok=True)
total = 0
for name, keep in sorted(want.items()):
    f = src / ("scenarios" if name.startswith("UC-") else "behaviour") / f"{name}.yaml"
    v = yaml.safe_load(f.read_text(encoding="utf-8"))
    c = copy.deepcopy(v)
    c["outcomes"] = {k: o for k, o in (v.get("outcomes") or {}).items() if (k, "") in keep}
    vs = []
    for var in v.get("variants") or []:
        oc = {k: o for k, o in (var.get("outcomes") or {}).items() if (k, var["id"]) in keep}
        if oc:
            vs.append(dict(var, outcomes=oc))
    if "variants" in v:
        c["variants"] = vs
    n = len(c["outcomes"]) + sum(len(x["outcomes"]) for x in vs)
    assert n == len(keep), (name, n, keep)
    total += n
    (out / f"{name}.yaml").write_text(yaml.safe_dump(c, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"{name}: {n} job(s), observe_until {v['observe_until']}")
print("total jobs", total)

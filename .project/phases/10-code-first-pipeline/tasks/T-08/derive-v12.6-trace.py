#!/usr/bin/env python3
"""One-off (T-08): derive output-analysis/v12.6-trace.json from the coverage
map of output-analysis/v12.6-spec-validation.md.

  python3 .project/phases/10-code-first-pipeline/tasks/T-08/derive-v12.6-trace.py CONFORMANCE.json

CONFORMANCE.json: `bin/check-dash-conformance.py dist/sgai-spec.md --out-json`
(dist/sgai-spec.md is byte-identical to output/v12.6-sgai-spec.md).

Each `*"quote"*` of the evidence column is attached to the line range
written right after it as `(Lnnn[-mmm])`, else to the nearest range before
it. The range becomes the sections of v12.6 whose lines overlap it
(spec_sections.split gives each section's start); the quote is filed under
the first of those sections where it is literal (check-trace's
normalisation), else under the first of them, where check-trace reports
it. The quote text is kept verbatim: nothing is repaired (`/` for a table
pipe, an inner ellipsis). Every range of the cell, quoted or not, adds its
sections. Units are the map's 211 rows, retired ones included: the trace
records what v12.6's validation walked, not today's population.
"""
import importlib.util
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
BIN = os.path.join(ROOT, "bin")
sys.path.insert(0, BIN)
import spec_sections  # noqa: E402


def load(name, f):
    s = importlib.util.spec_from_file_location(name, os.path.join(BIN, f))
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


cp = load("cp", "check-promotable.py")
ct = load("ct", "check-trace.py")

SPEC = "output/v12.6-sgai-spec.md"
SIDECAR = "output-analysis/v12.6-spec-validation.md"
Q = re.compile(r'\*"(.+?)"\*(?!\*)')
L = re.compile(r"\bL(\d+)(?:-(\d+))?\b")
AFTER = re.compile(r'^\s*\(L(\d+)(?:-(\d+))?\)')


def kind_of(u):
    return "prose" if "#p" in u else "use-case" if u.startswith("UC-") else "criterion"


def main(conf_path):
    with open(os.path.join(ROOT, SPEC), encoding="utf-8", newline="") as fh:
        secs = spec_sections.split(fh.read())
    spans = [(s.key, s.start + 1, s.start + len(s.lines)) for s in secs]
    order = {s.key: i for i, s in enumerate(secs)}
    norm = {s.key: ct.normalise(s.text) for s in secs}
    with open(os.path.join(ROOT, SIDECAR), encoding="utf-8") as fh:
        v = fh.read()
    for heading, header, rows in cp.tables(v):
        if "coverage" in heading.lower() and cp.column(header, "verdict") is not None:
            break
    ev, vc = cp.column(header, "evidence"), cp.column(header, "verdict")
    ids = [cp.strip_marks(r[0]) for r in rows]
    with open(conf_path, encoding="utf-8") as fh:
        conf = json.load(fh)
    src = ct.sources(conf, [(u, kind_of(u)) for u in ids])

    def covering(a, b):
        return [k for k, s, e in spans if s <= b and e >= a]

    units = {}
    for r, u in zip(rows, ids):
        cell = r[ev]
        keys = {}
        for m in L.finditer(cell):
            for k in covering(int(m.group(1)), int(m.group(2) or m.group(1))):
                keys.setdefault(k, [])
        for m in Q.finditer(cell):
            a = AFTER.match(cell[m.end():])
            rng = (a.group(1), a.group(2)) if a else L.findall(cell[:m.start()])[-1]
            lo = int(rng[0])
            hi = int(rng[1] or rng[0])
            cand = covering(lo, hi)
            nq = ct.normalise(m.group(1))
            home = next((k for k in cand if nq in norm[k]), cand[0])
            keys.setdefault(home, []).append(m.group(1))
        s = src[u]
        e = {"kind": kind_of(u), "source": s["source"], "verdict": cp.verdict_of(r[vc]),
             "sections": [{"key": k, "quotes": keys[k]} for k in sorted(keys, key=order.get)]}
        if s["rules"]:
            e["rules"] = s["rules"]
        if s["residual"]:
            e["residual"] = s["residual"]
        if s["source"] == "code" and s["verdict"] != e["verdict"]:
            e["code_verdict"] = s["verdict"]
        units[u] = e
    trace = {"format": "sgai-trace/1", "spec": SPEC,
             "derived_from": SIDECAR + " (coverage map; line ranges mapped to sections by code)",
             "units": units}
    out = os.path.join(ROOT, "output-analysis", "v12.6-trace.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(trace, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(f"wrote {out}: {len(units)} units")


if __name__ == "__main__":
    main(sys.argv[1])

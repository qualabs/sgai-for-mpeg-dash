#!/usr/bin/env python3
"""A candidate against what is published, by a written rule (ADR 0070).

Reads the candidate's sidecars in output-analysis/ (v<N>-spec-validation.md,
v<N>-detail-review.md, v<N>-conformance-tests.json, v<N>-dash-conformance-
audit.md) and the published ones in dist/, with the same parsers
`check-promotable.py` uses, and writes the table and the verdict.

**Unit by unit, never count against count.** The obligation coverage is
compared on the units both sides walked (by id). If the two populations
share less than MIN_OVERLAP of the smaller one, they are not the same kind
of unit (30 requirements against 211 criteria, as the LLM comparison of
v12.6 did) and there is no verdict: exit 2.

The verdict:
  WORSE THAN PUBLISHED    a shared unit that was clear (met/full/governance)
                          in dist/ is blocking (contradicted/gap/force-lost)
                          in the candidate, or the conformance tests have
                          more FAIL, or more findings are routed as
                          blocking (§5.a–5.d of the validation).
  BETTER THAN PUBLISHED   not worse, and at least one of: fewer conformance
                          FAIL, fewer blocking routed findings, a shared
                          unit moved from blocking/partial to clear, fewer
                          detail-review flags.
  NO BETTER THAN PUBLISHED otherwise.
A category dist/ does not have (a sidecar published before it existed) is
shown as n/a and enters neither side of the rule; that is said in the
report.

Usage:
  bin/compare-candidates.py v<N> [--out FILE] [--dist DIR] [--analysis DIR]

--out defaults to output-analysis/v<N>-comparison.md. Prints the verdict line.

What it does not do: read the spec, or promote (bin/promote.py does).

Exit codes: 0 verdict written · 2 cannot tell (a required sidecar of the
candidate missing or unparseable, or the populations not comparable) ·
64 wrong command line.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys

BIN = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BIN)
_spec = importlib.util.spec_from_file_location("promotable", os.path.join(BIN, "check-promotable.py"))
cp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cp)

MIN_OVERLAP = 0.9
CLEAR = cp.COVERAGE_CLEAR
BLOCK = cp.COVERAGE_BLOCKS
BLOCKING_BUCKETS = ("5.a", "5.b", "5.c", "5.d")


class CannotTell(Exception):
    pass


def usage(msg):
    sys.stderr.write(msg + "\n\n" + __doc__)
    sys.exit(64)


def heading_count(text, word):
    m = re.search(r"^## " + word + r"\s*\((\d+)\)", text, re.M | re.I)
    return int(m.group(1)) if m else None


def side(paths, required):
    """Parse one side. `paths` maps validation/detail/tests/audit to a file."""
    out = {}
    v = paths["validation"]
    if not os.path.isfile(v):
        raise CannotTell(f"no validation sidecar at {v}")
    text = cp.read(v)
    rows, shape = cp.coverage_rows(text)
    if rows is None:
        raise CannotTell(f"{v}: no coverage map")
    out["units"] = {u: s for u, s in rows}
    out["shape"] = shape
    disp = cp.dispositions(text)
    out["routed"] = {b: sum(1 for x in disp.values() if x == b) for b in BLOCKING_BUCKETS}
    for w in ("Gaps", "Edge cases", "Ambiguities"):
        out[w] = heading_count(text, w)
    d = paths["detail"]
    if os.path.isfile(d):
        fl = cp.flagged_rows(cp.read(d))
        out["flags"] = len(fl) if fl is not None else None
    else:
        out["flags"] = None
    t = paths["tests"]
    if os.path.isfile(t):
        with open(t, encoding="utf-8") as fh:
            out["tests"] = json.load(fh).get("counts", {})
    elif "tests" in required:
        raise CannotTell(f"no conformance-tests.json at {t}")
    else:
        out["tests"] = None
    a = paths["audit"]
    sus = cp.suspicion_rows(cp.read(a)) if os.path.isfile(a) else None
    out["suspicions"] = len(sus) if sus is not None else None
    return out


def judge(dist, cand):
    du, cu = dist["units"], cand["units"]
    shared = set(du) & set(cu)
    small = min(len(du), len(cu)) or 1
    if len(shared) / small < MIN_OVERLAP:
        raise CannotTell(f"populations not comparable: {len(shared)} shared units of "
                         f"{len(du)} published and {len(cu)} candidate "
                         f"({dist['shape']} against {cand['shape']})")
    worse, better = [], []
    for u in sorted(shared):
        a, b = du[u], cu[u]
        if a in CLEAR and b in BLOCK:
            worse.append(f"{u}: {a} → {b}")
        elif a not in CLEAR and b in CLEAR:
            better.append(f"{u}: {a} → {b}")
    if dist["tests"] is not None and cand["tests"] is not None:
        df, cf = dist["tests"].get("FAIL", 0), cand["tests"].get("FAIL", 0)
        if cf > df:
            worse.append(f"conformance FAIL {df} → {cf}")
        elif cf < df:
            better.append(f"conformance FAIL {df} → {cf}")
    dr, cr = sum(dist["routed"].values()), sum(cand["routed"].values())
    if cr > dr:
        worse.append(f"blocking routed findings {dr} → {cr}")
    elif cr < dr:
        better.append(f"blocking routed findings {dr} → {cr}")
    if dist["flags"] is not None and cand["flags"] is not None and cand["flags"] < dist["flags"]:
        better.append(f"detail-review flags {dist['flags']} → {cand['flags']}")
    if worse:
        return "WORSE THAN PUBLISHED", worse, better, shared
    if better:
        return "BETTER THAN PUBLISHED", worse, better, shared
    return "NO BETTER THAN PUBLISHED", worse, better, shared


def cell(x):
    return "n/a" if x is None else str(x)


def report(version, dist, cand, verdict, worse, better, shared):
    def stat(units, s):
        return sum(1 for u in shared if units[u] == s)
    rows = []
    for s in ("met", "full", "governance", "partial", "contradicted", "gap", "force-lost"):
        a, b = stat(dist["units"], s), stat(cand["units"], s)
        if a or b:
            rows.append((f"coverage on shared units — {s}", a, b))
    for b in BLOCKING_BUCKETS:
        rows.append((f"routed {b}", dist["routed"][b], cand["routed"][b]))
    for w in ("Gaps", "Edge cases", "Ambiguities"):
        rows.append((w.lower(), dist[w], cand[w]))
    rows.append(("detail-review flags", dist["flags"], cand["flags"]))
    for k in ("PASS", "FAIL", "NOT_VERIFIABLE"):
        rows.append((f"conformance {k}", (dist["tests"] or {}).get(k) if dist["tests"] is not None else None,
                     (cand["tests"] or {}).get(k)))
    rows.append(("audit suspicions (inform only)", dist["suspicions"], cand["suspicions"]))
    added = sorted(set(cand["units"]) - set(dist["units"]))
    removed = sorted(set(dist["units"]) - set(cand["units"]))
    lines = [f"# Candidate {version} against the published build", "",
             "Generated by `bin/compare-candidates.py` (ADR 0070). Coverage is compared unit by unit "
             f"on the {len(shared)} units both walked.", "",
             "| Category | dist (published) | candidate | ",
             "|---|---|---|"]
    lines += [f"| {n} | {cell(a)} | {cell(b)} |" for n, a, b in rows]
    lines += ["", f"Units only in the candidate ({len(added)}): {', '.join(added) or '—'}.",
              f"Units only in dist ({len(removed)}): {', '.join(removed) or '—'}.", "",
              "## Verdict", "", f"**{verdict}**", ""]
    if worse:
        lines += ["Worse:", *[f"- {w}" for w in worse], ""]
    if better:
        lines += ["Better:", *[f"- {b}" for b in better], ""]
    na = [n for n, a, b in rows if a is None and b is not None]
    if na:
        lines += ["Categories dist/ does not have, outside the rule: " + ", ".join(na) + ".", ""]
    lines += ["This verdict promotes nothing; `bin/promote.py` decides with every gate."]
    return "\n".join(lines) + "\n"


def main(argv):
    pos, opts = [], {"--out": None, "--dist": os.path.join(ROOT, "dist"),
                     "--analysis": os.path.join(ROOT, "output-analysis")}
    i = 0
    while i < len(argv):
        if argv[i] in opts:
            if i + 1 >= len(argv):
                usage(f"{argv[i]} needs a value")
            opts[argv[i]] = argv[i + 1]
            i += 2
        elif argv[i].startswith("--"):
            usage(f"unknown flag {argv[i]}")
        else:
            pos.append(argv[i])
            i += 1
    if len(pos) != 1 or not re.match(r"^v\d+(\.\d+)?$", pos[0]):
        usage("one candidate version v<N> or v<N.M> is required")
    v, an, dd = pos[0], opts["--analysis"], opts["--dist"]
    cand_paths = {"validation": f"{an}/{v}-spec-validation.md", "detail": f"{an}/{v}-detail-review.md",
                  "tests": f"{an}/{v}-conformance-tests.json", "audit": f"{an}/{v}-dash-conformance-audit.md"}
    dist_paths = {"validation": f"{dd}/spec-validation.md", "detail": f"{dd}/detail-review.md",
                  "tests": f"{dd}/conformance-tests.json", "audit": f"{dd}/dash-conformance-audit.md"}
    try:
        cand = side(cand_paths, required=("tests",))
        dist = side(dist_paths, required=())
        verdict, worse, better, shared = judge(dist, cand)
    except CannotTell as e:
        print(f"exit 2: {e}")
        return 2
    out = opts["--out"] or f"{an}/{v}-comparison.md"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(report(v, dist, cand, verdict, worse, better, shared))
    print(f"{verdict} ({len(worse)} worse, {len(better)} better, {len(shared)} shared units) → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

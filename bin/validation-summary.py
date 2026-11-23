#!/usr/bin/env python3
"""The machine summary of a validation sidecar (ADR 0068: scripts read
summaries, never prose).

Usage:
  bin/validation-summary.py SIDECAR.md [--out FILE] [--population FILE]

Writes `output-analysis/v<N>-spec-validation.summary.json` (or FILE, or
stdout without --out) from `output-analysis/v<N>-spec-validation.md`:

  {"format": "sgai-validation-summary/1",
   "sidecar": "<path as given>", "sidecar_sha256": "<hex>",
   "shape": "per-criterion" | "per-requirement",
   "population": <units of the population>, "walked": <rows of the map>,
   "missing": [units of the population with no row],
   "extra": [rows that are not units of the population],
   "rows": [[unit, verdict], ...],          # the map, in order
   "verdicts": {verdict: count},
   "units": {unit: {"verdict": v, "disposition": "5.x" | null}},
   "dispositions": {finding or unit id: "5.a" | "5.b" | "5.c" | "5.d"},
   "findings": {"5.a": rows, "5.b": rows, "5.c": rows, "5.d": rows},
   "gaps": n, "edge_cases": n, "ambiguities": n}

Everything is parsed with bin/check-promotable.py's own functions
(coverage_rows, dispositions, tables), so the summary and the script that
reads it cannot disagree about the sidecar. The 5.a-5.d counts are the rows
of each bucket's table (an overflow table of 5.a counts in 5.a). The gaps,
edge cases and ambiguities are the `### G-`, `### EC-`, `### A-` entries
under their `## Gaps (n)`, `## Edge cases (n)`, `## Ambiguities (n)`
headings.

--population FILE reads `<id><TAB><kind>` lines instead of today's
`check-promotable.py --population` (to summarise an old sidecar against the
population it was walked on).

What a green says: the sidecar parses, and every count a heading declares
equals the entries under it. It does NOT say the verdicts are right, nor
that the map covers the population (`missing` says that, and
check-promotable judges it).

Exit codes: 0 written · 1 written, but a heading's `(n)` disagrees with
its entries (listed in "inconsistent") · 2 cannot tell: no sidecar, or no
coverage map, or a findings heading missing · 64 wrong command line.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import sys

BIN = os.path.dirname(os.path.abspath(__file__))


def _load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BIN, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cp = _load("check_promotable", "check-promotable.py")

FINDINGS = (("gaps", "Gaps", "G"), ("edge_cases", "Edge cases", "EC"), ("ambiguities", "Ambiguities", "A"))


class CannotTell(Exception):
    pass


def chapter(text, title):
    """(declared n, body) of the `## <title> (n)` chapter, or None."""
    m = re.search(r"^## %s \((\d+)\)\s*$" % re.escape(title), text, re.M)
    if not m:
        return None
    nxt = re.search(r"^## ", text[m.end():], re.M)
    return int(m.group(1)), text[m.end(): m.end() + nxt.start() if nxt else len(text)]


def summarise(text, pop, sidecar_name):
    rows, shape = cp.coverage_rows(text)
    if rows is None:
        raise CannotTell("no obligation coverage map")
    disp = cp.dispositions(text)
    inconsistent = []
    out = {"format": "sgai-validation-summary/1", "sidecar": sidecar_name,
           "sidecar_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
           "shape": shape}
    ids = [u for u, _ in pop]
    seen = [u for u, _ in rows]
    out["population"] = len(ids)
    out["walked"] = len(rows)
    out["missing"] = [u for u in ids if u not in set(seen)]
    out["extra"] = [u for u in seen if u not in set(ids)]
    out["rows"] = [[u, v] for u, v in rows]
    verdicts = {}
    for _, v in rows:
        verdicts[v] = verdicts.get(v, 0) + 1
    out["verdicts"] = verdicts
    out["units"] = {u: {"verdict": v, "disposition": disp.get(u)} for u, v in rows}
    out["dispositions"] = disp

    counts = {"5.a": 0, "5.b": 0, "5.c": 0, "5.d": 0}
    declared = {}
    for m in re.finditer(r"^### (5\.[abcd])\b.*\((\d+)\)\s*$", text, re.M):
        declared[m.group(1)] = int(m.group(2))
    for heading, header, trows in cp.tables(text):
        m = re.search(r"5\.([abcd])\b", heading)
        if m:
            counts["5." + m.group(1)] += len(trows)
    out["findings"] = counts
    for b, n in declared.items():
        # An overflow table of 5.a adds rows its heading's (n) does not count.
        over = sum(len(r) for h, _, r in cp.tables(text) if b == "5.a" and "overflow" in h.lower())
        if counts[b] - over != n:
            inconsistent.append(f"{b}: heading says {n}, its table has {counts[b] - over} row(s)")
    for key, title, prefix in FINDINGS:
        ch = chapter(text, title)
        if ch is None:
            raise CannotTell(f"no `## {title} (n)` heading")
        n, body = ch
        found = len(re.findall(r"^### %s-\d+\b" % prefix, body, re.M))
        out[key] = n
        if found != n:
            inconsistent.append(f"{title}: heading says {n}, {found} `### {prefix}-<n>` entr(y/ies)")
    out["inconsistent"] = inconsistent
    return out


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        sys.stdout.write(__doc__)
        return 0 if argv else 64
    pos, o, i = [], {}, 0
    while i < len(argv):
        a = argv[i]
        if a in ("--out", "--population"):
            if i + 1 >= len(argv):
                sys.stderr.write(f"{a} needs a value\n")
                return 64
            o[a] = argv[i + 1]
            i += 1
        elif a.startswith("--"):
            sys.stderr.write(f"unknown option {a}\n\n{__doc__}")
            return 64
        else:
            pos.append(a)
        i += 1
    if len(pos) != 1:
        sys.stderr.write(f"one sidecar is needed\n\n{__doc__}")
        return 64
    try:
        try:
            with open(pos[0], encoding="utf-8") as fh:
                text = fh.read()
        except OSError as e:
            raise CannotTell(str(e))
        if "--population" in o:
            try:
                with open(o["--population"], encoding="utf-8") as fh:
                    pop = [tuple(ln.rstrip("\n").split("\t")) for ln in fh if ln.strip()]
            except OSError as e:
                raise CannotTell(str(e))
        else:
            pop = cp.population()
        summ = summarise(text, pop, pos[0])
    except CannotTell as e:
        print(f"CANNOT TELL: {e}")
        return 2
    data = json.dumps(summ, indent=1, ensure_ascii=False) + "\n"
    if "--out" in o:
        with open(o["--out"], "w", encoding="utf-8") as fh:
            fh.write(data)
        print(f"wrote {o['--out']}: {summ['walked']} rows, population {summ['population']}, "
              f"findings {summ['findings']}, gaps {summ['gaps']}, edge cases {summ['edge_cases']}, "
              f"ambiguities {summ['ambiguities']}")
    else:
        sys.stdout.write(data)
    for msg in summ["inconsistent"]:
        print(f"INCONSISTENT: {msg}")
    return 1 if summ["inconsistent"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

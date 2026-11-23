#!/usr/bin/env python3
"""T-12 dry run only: stand in for the validation's trace handling, with no LLM.

  carry-trace.py base  TRACE SPEC POPULATION OUT
      v12.6's trace (derived from its prose sidecar, T-08) made literal: units
      outside POPULATION dropped, units missing added with no section, and the
      quotations bin/check-trace.py finds not literal in SPEC dropped.
  carry-trace.py carry TRACE NEW_SPEC STALE.json OUT
      the trace carried to the next candidate, as validate-spec §B.2 carries
      every unit check-trace `stale` does not list. Prints the units whose
      quotations broke and FAILS (exit 1) if one of them is not a stale unit:
      a patch may only break what it declares. Then, standing in for the
      walkers, it drops the broken quotations of the stale units.
"""
import importlib.util, json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), *[".."] * 5))
spec = importlib.util.spec_from_file_location("ct", os.path.join(ROOT, "bin", "check-trace.py"))
ct = importlib.util.module_from_spec(spec); spec.loader.exec_module(ct)


def broken(trace, spec_path):
    secs = ct.spec_index(spec_path)
    out = {}
    for u, e in trace["units"].items():
        for s in e.get("sections") or []:
            if s["key"] not in secs:
                out.setdefault(u, []).append((s["key"], None))
                continue
            body = ct.normalise(secs[s["key"]].text)
            for q in s.get("quotes") or []:
                if ct.normalise(q) not in body:
                    out.setdefault(u, []).append((s["key"], q))
    return out


def drop(trace, units_quotes):
    for u, bad in units_quotes.items():
        e = trace["units"][u]
        keep = []
        for s in e.get("sections") or []:
            gone = [q for k, q in bad if k == s["key"]]
            if (s["key"], None) in bad:
                continue
            s["quotes"] = [q for q in s.get("quotes") or [] if q not in gone]
            keep.append(s)
        e["sections"] = keep


def main(a):
    if a[0] == "base":
        trace, spec_path, pop_path, out = json.load(open(a[1])), a[2], a[3], a[4]
        pop = ct.population(pop_path)
        ids = dict(pop)
        extra = [u for u in trace["units"] if u not in ids]
        for u in extra:
            del trace["units"][u]
        missing = [u for u in ids if u not in trace["units"]]
        for u in missing:
            trace["units"][u] = {"kind": ids[u], "source": "llm", "sections": []}
        b = broken(trace, spec_path)
        drop(trace, b)
        print(f"base: dropped {len(extra)} extra unit(s), added {len(missing)} missing, "
              f"dropped {sum(len(v) for v in b.values())} non-literal quotation(s) of {len(b)} unit(s)")
    else:
        trace, spec_path, stale, out = json.load(open(a[1])), a[2], json.load(open(a[3])), a[4]
        b = broken(trace, spec_path)
        outside = sorted(set(b) - set(stale["units"]))
        print(f"carry: {len(stale['units'])} stale unit(s); quotations broken in {len(b)} unit(s): {sorted(b)}; "
              f"outside the stale units: {outside}")
        if outside:
            return 1
        drop(trace, b)
    trace["spec"] = os.path.relpath(os.path.abspath(spec_path), os.getcwd())
    with open(out, "w") as fh:
        json.dump(trace, fh, indent=1, ensure_ascii=False)
    return 0


sys.exit(main(sys.argv[1:]))

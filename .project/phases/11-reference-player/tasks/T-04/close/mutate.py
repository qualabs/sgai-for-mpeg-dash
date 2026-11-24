#!/usr/bin/env python3
"""Mutation campaign for T-04's closing changes: one deliberate break per rule,
each run only against the tests that cover it. Works on a copy of bin/,
spec-source/ and context/ in RAM; the repository is never edited.

    python3 mutate.py <project root>
"""
import os
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
CMP = "bin/conformance/behaviour_compare.py"
CS = "bin/check-scenarios.py"
SCHEMA = "spec-source/scenarios/schema.json"
TBC = "bin/test_behaviour_compare.py"
TCB = "bin/test_check_behaviour.py"

# (name, file, old, new, test file, test ids)
MUTATIONS = [
    ("origin: samples not moved to the first frame", CMP,
     'ss = {"t": max(0.0, (s["t"] - ff) * k)', 'ss = {"t": max(0.0, (s["t"]) * k)',
     TBC, ["Origin"]),
    ("origin: requests not moved", CMP,
     "    t0 = raw[\"t0\"] + ff\n", "    t0 = raw[\"t0\"]\n", TBC, ["Origin"]),
    ("origin: no clamp to 0", CMP,
     'at = max(0.0, (r["wall"] - t0) * k)', 'at = (r["wall"] - t0) * k', TBC, ["Origin"]),
    ("origin: runner's startupMs ignored", CMP,
     '    ff = raw.get("startupMs")\n', '    ff = None\n', TBC, ["Origin"]),
    ("origin: first frame counts a background", CMP,
     'in ("primary", "ad") for e in s.get', 'in ("primary", "ad", "background") for e in s.get', TBC, ["Origin"]),
    ("tolerance: request ignores its own", CMP,
     'within(o["at"], e["at"], tol_of(e, tol))\n                  and o.get',
     'within(o["at"], e["at"], tol)\n                  and o.get', TBC, ["ItemTolerance"]),
    ("tolerance: beacon ignores its own", CMP,
     'hit = next((j for j, o in same if within(o["at"], e["at"], tol_of(e, tol))), None)\n        if hit is not None:\n            used.add(hit)\n            continue\n        seen = ", ".join(str(_r(o["at"])) for _, o in same) or "never"\n        problems.append(f"beacons',
     'hit = next((j for j, o in same if within(o["at"], e["at"], tol)), None)\n        if hit is not None:\n            used.add(hit)\n            continue\n        seen = ", ".join(str(_r(o["at"])) for _, o in same) or "never"\n        problems.append(f"beacons',
     TBC, ["ItemTolerance"]),
    ("tolerance: segment boundary ignores its own", CMP,
     "           tol_of(expected[i], tol)) for i in range", "           tol) for i in range", TBC, ["ItemTolerance"]),
    ("tolerance: segment from ignores its own", CMP,
     'not within(got, pe["from"], tol_of(e, tol))', 'not within(got, pe["from"], tol)', TBC, ["ItemTolerance"]),
    ("extra query: match instead of fullmatch", CMP,
     "re.fullmatch(extra, k)", "re.search(extra, k)", TBC, ["ExtraQuery"]),
    ("extra query: pattern ignored (exact)", CMP,
     "return all(extra is not None and re.fullmatch(extra, k) for k in rest)", "return not rest", TBC, ["ExtraQuery"]),
    ("window: boundary matched on its from only", CMP,
     "and dist(t, bt) <= bt_tol]", "and abs(t - lo(bt)) <= bt_tol]", TBC, ["Windows"]),
    ("window: a windowed boundary may be silent", CMP,
     ' or isinstance(nxt["start"], dict) or isinstance(prev["start"], dict):', ":", TBC, ["Windows"]),
    ("requests_not_compared ignored", CMP,
     'if f == "requests" and outcome.get("requests_not_compared"):', 'if False:', TBC, ["NotCompared"]),
    ("clicks: url not checked against trackingUris", CMP,
     ' or e["url"] not in (ct.get("trackingUris") or "").split():', ':', TBC, ["Clicks"]),
    ("clicks: an unexpected click passes", CMP,
     'problems.append(f"unexpected click-tracking', 'unverifiable.append(f"unexpected click-tracking',
     TBC, ["Clicks"]),
    ("clicks: time not compared", CMP,
     'hit = next((j for j, o in same if within(o["at"], e["at"], tol_of(e, tol))), None)\n        if hit is not None:\n            used.add(hit)\n            continue\n        seen = ", ".join(str(_r(o["at"])) for _, o in same) or "never"\n        problems.append(f"clicks',
     'hit = next((j for j, o in same), None)\n        if hit is not None:\n            used.add(hit)\n            continue\n        seen = ", ".join(str(_r(o["at"])) for _, o in same) or "never"\n        problems.append(f"clicks',
     TBC, ["Clicks"]),
    ("destinations: shown on screen not read", CMP,
     ' + \\\n           [("shown", d["at"], d["uri"]) for d in obs.destinations]', "", TBC, ["Clicks"]),
    ("destinations: an unexpected one passes", CMP,
     'problems.append(f"unexpected destination', 'unverifiable.append(f"unexpected destination', TBC, ["Clicks"]),
    ("destinations: time not compared", CMP,
     "hit = next((j for j, x in same if within(x[1], e[\"at\"], tol_of(e, tol))), None)",
     "hit = next((j for j, x in same), None)", TBC, ["Clicks"]),
    ("beacons: click-tracking not handed to clicks", CMP,
     "        known -= click_urls(fx)[0]\n", "        pass\n", TBC, ["Clicks"]),
    ("beacons: OverlayList candidate scope lost", CMP,
     'return [e for e in root if _local(e) in ("Period", "Ad")]', 'return [e for e in root if _local(e) in ("Period",)]',
     TBC, ["Clicks.test_overlay_candidate_scope_of_a_beacon"]),
    ("check: expect_red extra rule passes", CS,
     'finder(key)("S-FIXTURE", f"{p}: expect_red lists {r}, which does not fail on it")', "pass",
     TCB, ["TestExtensions.test_expect_red_extra_rule", "TestExtensions.test_expect_red_on_a_green_fixture"]),
    ("check: expect_red missing rule passes", CS,
     'finder(key)("S-FIXTURE", f"{p} fails a rule expect_red does not list: {d}")', "pass",
     TCB, ["TestExtensions.test_expect_red_missing_a_rule"]),
    ("check: expect_red ignored (fixture judged green)", CS,
     '            ctx.setdefault("expect_red", {})[(key, p)] = set(f["expect_red"])', "            pass",
     TCB, ["TestExtensions.test_expect_red_exact"]),
    ("check: click url not checked", CS,
     'elif f == "clicks" and c["url"] not in', 'elif False and c["url"] not in',
     TCB, ["TestExtensions.test_click_url_not_in_tracking_uris"]),
    ("check: ClickThrough count not checked", CS,
     "            if len(cts) != 1:", "            if False:", TCB, ["TestExtensions.test_candidate_without_clickthrough"]),
    ("check: clicks times not bounded", CS,
     '    for f in ("clicks", "destinations"):\n        for i, c in enumerate(o.get(f, [])):\n            yield',
     '    for f in ():\n        for i, c in enumerate(o.get(f, [])):\n            yield',
     TCB, ["TestExtensions.test_click_after_observe_until"]),
    ("check: extra_query_pattern not compiled", CS,
     '                re.compile(r["extra_query_pattern"])', "                pass",
     TCB, ["TestExtensions.test_extra_query_pattern"]),
    ("check: window end <= start not found", CS,
     ' or _hi(s["end"]) <= _hi(s["start"]):', ":", TCB, ["TestExtensions.test_window_boundary"]),
    ("schema: clicks without destinations", SCHEMA,
     '"dependentRequired": {"clicks": ["destinations"], "destinations": ["clicks"]},', "",
     TCB, ["TestExtensions.test_schema"]),
    ("schema: requests_not_compared with requests", SCHEMA,
     '"then": {"properties": {"requests": {"maxItems": 0}}},', '"then": {},',
     TCB, ["TestExtensions.test_requests_not_compared"]),
    ("schema: expect_red empty allowed", SCHEMA,
     '"expect_red": {"type": "array", "minItems": 1,', '"expect_red": {"type": "array",',
     TCB, ["TestExtensions.test_schema"]),
    ("schema: negative item tolerance allowed", SCHEMA,
     '"tolerance": {"type": "integer", "minimum": 0,\n                  "description": "this item',
     '"tolerance": {"type": "integer",\n                  "description": "this item',
     TCB, ["TestExtensions.test_per_item_tolerance_schema"]),
    ("background: candidate required when absent", CMP,
     'if "candidate" in exp and not cand_matches(exp["candidate"], el, fx)',
     'if not cand_matches(exp.get("candidate", {"fixture": None}), el, fx)',
     TBC, ["Presentation.test_background_without_candidate_matches_any_background"]),
    ("background: candidate ignored when written", CMP,
     'if "candidate" in exp and not cand_matches(exp["candidate"], el, fx)',
     'if False',
     TBC, ["Presentation.test_background_with_candidate_is_compared"]),
    ("background: option null required when absent", CMP,
     'return "option" not in exp or opt_matches(exp["option"], el)',
     'return opt_matches(exp.get("option"), el)',
     TBC, ["Presentation.test_background_without_candidate_matches_any_background"]),
    ("background: describe_exp without candidate", CMP,
     '        elif "candidate" not in e:\n            parts.append(e["element"])\n',
     '',
     TBC, ["Presentation.test_background_without_candidate_never_shown"]),
]


def run_tests(work, test, ids):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-B", test, *ids], cwd=work, capture_output=True, text=True, env=env)
    return p.returncode, (p.stdout + p.stderr).strip().splitlines()[-1:]


def main():
    base = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "cto" / f"t04close-mut-{secrets.token_hex(3)}"
    base.mkdir(parents=True)
    try:
        for d in ("bin", "spec-source", "context"):
            shutil.copytree(ROOT / d, base / d, ignore=shutil.ignore_patterns("node_modules", "__pycache__"))
        caught = 0
        ids_all = {}
        for _, _, _, _, test, ids in MUTATIONS:
            ids_all.setdefault(test, set()).update(ids)
        for test, ids in ids_all.items():
            rc, tail = run_tests(base, test, sorted(ids))
            print(f"BASELINE {test} {' '.join(sorted(ids))}: {'OK' if rc == 0 else 'RED'} {tail}")
            if rc != 0:
                raise SystemExit("baseline is red")
        for name, rel, old, new, test, ids in MUTATIONS:
            f = base / rel
            orig = f.read_text()
            if orig.count(old) != 1:
                print(f"NOT APPLIED  {name}: the text to break occurs {orig.count(old)} times")
                continue
            f.write_text(orig.replace(old, new))
            try:
                rc, tail = run_tests(base, test, ids)
            finally:
                f.write_text(orig)
            ok = rc != 0
            caught += ok
            print(f"{'CAUGHT     ' if ok else 'NOT CAUGHT '} {name}  [{test} {' '.join(ids)}] {tail}")
        print(f"{caught} of {len(MUTATIONS)} caught")
    finally:
        shutil.rmtree(base)


main()

"""Scoped mutation campaign for behaviour_compare.py: one break per rule, only the tests that cover it."""
import subprocess, sys
from pathlib import Path
ROOT = Path(sys.argv[1]); F = ROOT / "bin/conformance/behaviour_compare.py"
M = [
 ("exact time threshold", 'return abs(t - when) <= tol', 'return abs(t - when) < tol', "Requests.test_exact_time_threshold"),
 ("window widened by tolerance", 'when["from"] - tol <= t <= when["to"] + tol', 'when["from"] <= t <= when["to"]', "Requests.test_window_edges_with_tolerance"),
 ("query the Player adds", 'ok = (q == want_q and', 'ok = (True and', "Requests.test_query_the_player_adds"),
 ("answered_by", 'and o.get("fixture") == e.get("answered_by")', 'and True', "Requests.test_answered_by"),
 ("entry not compared", 'if entry is not None and fx.of(o["url"]) == entry:', 'if False:', "Requests.test_entry_is_not_compared"),
 ("unexpected request", 'problems.append(f"unexpected request', 'print(f"unexpected request', "Requests.test_unexpected_request"),
 ("matches .http", 'and (http is None or same_url(http, o["url"])))', ')', "Requests.test_matches_http"),
 ("declared params must be present", '        if kv not in rest:\n            return None\n        rest.remove(kv)', '        if kv in rest:\n            rest.remove(kv)', "Requests.test_declared_parameter_missing_is_another_url"),
 ("unexpected beacon", 'problems.append(f"unexpected beacon', 'print(f"unexpected beacon', "Beacons.test_fired_twice_is_unexpected Beacons.test_a_declared_beacon_not_expected"),
 ("beacon time", 'hit = next((j for j, o in same if within(o["at"], e["at"], tol)), None)', 'hit = next((j for j, o in same), None)', "Beacons.test_time_threshold"),
 ("beacon query order", 'return _split(a) == _split(b)', 'return a == b', "Beacons.test_query_order_does_not_matter"),
 ("candidate scope", '        if "id" in cand:\n            scopes = [p for p in periods if p.get("id") == cand["id"]]', '        if "id" in cand:\n            scopes = periods', "Beacons.test_candidate_scope"),
 ("beacon URL from fixture", '    if exp.get("url"):\n        return exp["url"]\n    text', '    if exp.get("url"):\n        return exp["url"]\n    return None\n    text', "Beacons.test_url_read_from_the_fixture"),
 ("extra observed change", 'which the vector does not have")', 'which the vector does not have") if False else None', "Presentation.test_extra_change"),
 ("silent boundary rule", 'return pb["from"] == pa["from"] + (prev["end"] - prev["start"]) * rate', 'return True', "Presentation.test_pause_is_a_segment Presentation.test_silent_boundary_needs_no_change"),
 ("rate in silent rule", 'rate = _rate_at(prev["start"], actions, timescale)', 'rate = 1.0', "Presentation.test_silent_boundary_needs_no_change"),
 ("missing written change", '        if not silent and i not in matched:', '        if False:', "Presentation.test_missing_change"),
 ("primary from", '            if got is None or abs(got - pe["from"]) > tol:', '            if False:', "Presentation.test_from_threshold"),
 ("boundary tolerance", 'if i not in matched and abs(bt - t) <= tol]', 'if i not in matched and abs(bt - t) < 1]', "Presentation.test_boundary_threshold"),
 ("transition folding", '        if sg.end - sg.start < tol and len(segs) > 1:', '        if False:', "Presentation.test_short_glitch_is_folded"),
 ("pause is a boundary", 'if not segs or ident != segs[-1].ident or paused != segs[-1].paused or seek:', 'if not segs or ident != segs[-1].ident or seek:', "Presentation.test_pause_is_a_segment"),
 ("seek beyond tolerance", 'abs(s["seek"]["to"] - s["seek"]["from"]) > tol', 'abs(s["seek"]["to"] - s["seek"]["from"]) > 0', "Presentation.test_seek_is_a_change"),
 ("startup absorbed", '    segs[0].start = 0\n', '', "Presentation.test_startup_is_not_a_change"),
 ("exactly its surfaces", '    return not left', '    return True', "Presentation.test_extra_surface"),
 ("option identity", '        return "optionId" not in el and "optionIndex" not in el', '        return True', "Presentation.test_wrong_option"),
 ("candidate identity", '        return el.get("candidateId") == exp["id"]', '        return True', "Presentation.test_wrong_candidate"),
 ("selection order", '            for (el, lay), w in zip(got, want))', '            for (el, lay), w in zip(got, sorted(want, key=lambda w: w["candidate"].get("id", ""))))', "Selection.test_order_of_first_appearance"),
 ("unlisted opportunity", '            problems.append(f"ad presented for an opportunity', '            print(f"ad presented for an opportunity', "Selection.test_unattributed_ad"),
 ("selection layout", '            lay == w["layout"] and cand_matches', '            cand_matches', "Selection.test_wrong_layout"),
 ("declined expects nothing", 'want = sel["presented"] if sel["result"] == "presented" else []', 'want = sel["presented"]', "Selection.test_declined_expects_nothing"),
 ("geometry edge tolerance", 'return all(abs(a - b) <= tol + 1e-9 for a, b in zip(we, ge))', 'return all(abs(a - b) <= 1e-9 for a, b in zip(we, ge))', "Geometry.test_edge_threshold"),
 ("ad union", '    ad = _union([e["rect"] for e in sample["elements"] if e.get("element") == "ad"])', '    ad = ([e["rect"] for e in sample["elements"] if e.get("element") == "ad"] or [None])[-1]', "Geometry.test_union_of_ad_surfaces"),
 ("background not the ad", 'if e.get("element") == "ad"])', 'if e.get("element") in ("ad", "background")])', "Geometry.test_background_is_not_the_ad"),
 ("geometry time window", '        lo, hi = g["at"] - tol_t, g["at"] + tol_t', '        lo, hi = g["at"], g["at"]', "Geometry.test_window_around_a_transition"),
 ("primary rect", '            if ("primary" not in g or _edges_ok(g["primary"], prim, g["tolerance"])) and', '            if True and', "Geometry.test_primary_squeezed"),
 ("units", '    k = timescale / 1000.0\n    t0', '    k = 1.0\n    t0', "Normalise.test_units Baseline.test_timescale_is_converted"),
 ("audio NV", '            o, d = Outcome.NOT_VERIFIABLE, "the observation', '            o, d = Outcome.PASS, "the observation', "Baseline.test_audio_is_not_verifiable"),
 ("harness failure NV", '    if not raw or not raw.get("ok") or raw.get("t0") is None:', '    if not raw:', "Baseline.test_harness_failure_is_not_verifiable_everywhere"),
 ("primary time read from samples", 'got = sg.from_ if at_start else _primary_time_at(obs.samples, e["start"])', 'got = sg.from_ if at_start else sg.from_ + (e["start"] - sg.start) * (0 if sg.paused else sg.rate)', "Presentation.test_from_across_a_silent_boundary_reads_the_samples Presentation.test_pause_is_a_segment"),
 ("nothing shown", '        return Outcome.FAIL, "presentation: nothing was ever shown on screen"', '        return Outcome.PASS, "presentation: nothing was ever shown on screen"', "Presentation.test_nothing_ever_shown"),
]
import os
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
for c in (ROOT / "bin/conformance/__pycache__").glob("behaviour_compare*.pyc"):
    c.unlink()
def run(ids):
    return subprocess.run(["uv", "run", "-q", "--no-project", "--with", "pyyaml==6.0.3", "python3", "-B", "-m", "unittest", *ids],
                          cwd=ROOT / "bin", capture_output=True, text=True, env=ENV)
orig = F.read_text()
base = run([f"test_behaviour_compare.{t}" for _, _, _, ts in M for t in ts.split()])
print("baseline (unmutated, every covering test):", [l for l in base.stderr.splitlines() if l.startswith(("FAILED", "OK", "Ran"))])
assert base.returncode == 0
green = []
try:
    for name, old, new, tests in M:
        n = orig.count(old)
        if n != 1:
            print(f"SKIP  {name}: pattern found {n} times"); green.append(name); continue
        F.write_text(orig.replace(old, new))
        ids = [f"test_behaviour_compare.{t}" for t in tests.split()]
        p = run(ids)
        tail = [l for l in p.stderr.splitlines() if l.startswith(("FAILED", "OK", "Ran"))]
        verdict = "RED  " if p.returncode != 0 else "GREEN"
        if p.returncode == 0: green.append(name)
        print(f"{verdict} {name:32} {tests}  -> {' '.join(tail)}")
finally:
    F.write_text(orig)
print(f"\n{len(M)} mutations, {len(M) - len(green)} red, {len(green)} green/skipped: {green}")

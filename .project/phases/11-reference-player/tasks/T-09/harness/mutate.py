"""T-09 harness: one deliberate break per rule, each run only against the
tests that cover it, on a scratch copy of bin/ (never the repo's: a battery
run may be reading it). Baseline first (the covering tests, unmutated, must be
OK); a break whose tests stay green is NOT CAUGHT. Python runs with -B and the
copy's .pyc are removed before each run.

Usage: python3 mutate.py   (prints the campaign; exit 1 if any break is not caught)"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[6]
SCRATCH = Path(os.environ.get("XDG_RUNTIME_DIR") or "/tmp") / "cto" / f"t09-mutate-{os.getpid()}"

H = "test_behaviour_harness"
C = "test_behaviour_compare"
CLOCK = "players/adapters/sgai-clock.js"
CMP = "conformance/behaviour_compare.py"
BEH = "conformance/behaviour.py"
PLY = "conformance/players.py"

# (id, rule, file, find, replace, tests)
BREAKS = [
    ("M01", "a viewer pause runs on wall time", CLOCK,
     "    if (state.viewerPaused) return { kind: 'wall', why: 'viewer-paused' };\n", "",
     [f"{H}.Clock.test_viewer_pause_is_wall", f"{H}.Clock.test_viewer_pause_with_a_playing_video_is_wall"]),
    ("M02", "a linear ad's media time drives while the primary is hidden", CLOCK,
     "    if (!primary || !primary.shown) {", "    if (false) {",
     [f"{H}.Clock.test_linear_ad_drives_while_primary_hidden"]),
    ("M03", "the primary's media time drives while it plays", CLOCK,
     "    if (primary && primary.shown && !primary.paused) return", "    if (false) return",
     [f"{H}.Clock.test_primary_at_half_speed", f"{H}.Clock.test_stall_stands_still"]),
    ("M04", "media time is divided by the rate", CLOCK,
     "/ (v.rate || 1);", "/ 1;", [f"{H}.Clock.test_rate"]),
    ("M05", "a jump larger than the wall time allows counts nothing", CLOCK,
     "if (dm >= 0 && dm <= dt * JUMP_FACTOR + JUMP_SLACK_MS) step = dm;", "step = dm;",
     [f"{H}.Clock.test_jump_counts_nothing", f"{H}.Clock.test_jump_threshold"]),
    ("M06", "a seek counts nothing", CLOCK,
     "if (prev && v && prev.seeks === (v.seeks || 0)) {", "if (prev && v) {",
     [f"{H}.Clock.test_small_seek_counts_nothing"]),
    ("M07", "an overlay <video> over a playing primary does not drive", CLOCK,
     "    if (!primary || !primary.shown) {", "    if (true) {",
     [f"{H}.Clock.test_overlay_video_does_not_drive"]),
    ("M08", "the wall clock mode is wall time", CLOCK,
     "    this.mode = mode === 'wall' ? 'wall' : 'presentation';", "    this.mode = 'presentation';",
     [f"{H}.Clock.test_primary_at_half_speed"]),
    ("M09", "the mapping interpolates between clock points", CMP,
     "        return sa + (sb - sa) * ((t - a) / (b - a) if b > a else 0.0)", "        return sa",
     [f"{H}.Mapping.test_points"]),
    ("M10", "the mapping puts what precedes the first point at 0", CMP,
     "        if t <= pts[0][0]:\n            return 0.0", "        if t < 0:\n            return 0.0",
     [f"{H}.Mapping.test_points"]),
    ("M11", "normalise maps through the adapter's clock", CMP,
     "    smap = session_map((obs_raw.get(\"clock\") or {}).get(\"points\"), ff)",
     "    smap = session_map(None, ff)", [f"{H}.Mapping.test_normalise_maps_requests_and_samples"]),
    ("M12", "an aps-media answer is not a document request", CMP,
     "        if r.get(\"kind\") in (\"aps\", \"document\"):", "        if r.get(\"kind\") in (\"aps\", \"document\", \"aps-media\"):",
     [f"{H}.Mapping.test_normalise_maps_requests_and_samples"]),
    ("M13", "a URL served twice stands for the latest document served", CMP,
     "            hit = r[\"fixture\"]", "            hit = hit or r[\"fixture\"]",
     [f"{H}.Attribution.test_second_document_at_one_url"]),
    ("M14", "a surface keeps the document it appeared with", CMP,
     "            if key in prev:", "            if False:",
     [f"{H}.Attribution.test_surface_keeps_the_document_it_appeared_with"]),
    ("M15", "a new DOM element is a new presentation", CMP,
     "            run = (ident, e.get(\"inst\"), e.get(\"pass\"))", "            run = (ident, None, e.get(\"pass\"))",
     [f"{H}.Sequence.test_three_passes_by_element"]),
    ("M16", "a video started again is a new presentation", CMP,
     "            run = (ident, e.get(\"inst\"), e.get(\"pass\"))", "            run = (ident, e.get(\"inst\"), None)",
     [f"{H}.Sequence.test_passes_by_video_restart"]),
    ("M17", "a gap shorter than the tolerance is a flicker", CMP,
     "(run in ended and s[\"t\"] - ended[run] < tol)", "False",
     [f"{H}.Sequence.test_flicker_shorter_than_the_tolerance_is_the_same"]),
    ("M18", "a presentation left over is a FAIL", CMP,
     "        elif len(lst) > pos[key]:", "        elif False:",
     [f"{H}.Sequence.test_three_passes_by_element", f"{H}.Sequence.test_declined_then_presented"]),
    ("M19", "each entry takes the next presentations, not the first", CMP,
     "        got = seen.get(key, [])[p:p + len(want)]", "        got = seen.get(key, [])[:len(want)]",
     [f"{H}.Attribution.test_second_document_at_one_url", f"{H}.Sequence", f"{C}.Selection"]),
    ("M20", "an aps answer on a creative is media", BEH,
     "            any(same_url(a[\"url\"], c) for c in creatives)", "            False",
     [f"{H}.Jobs.test_aps_on_a_segment_or_a_creative_is_not_a_document"]),
    ("M21", "an aps answer on a segment is media", BEH,
     "            or (media is not None and media.is_segment(a[\"url\"], media_map)))", "            or False)",
     [f"{H}.Jobs.test_aps_on_a_segment_or_a_creative_is_not_a_document"]),
    ("M22", "an aps answer with a document is a document", BEH,
     "        is_media = not a.get(\"document\") and (", "        is_media = (",
     [f"{H}.Jobs.test_aps_with_a_document_is_a_document"]),
    ("M23", "only a declared segment goes to the content server", BEH,
     "            if any(re.match(x, local) for x in self.segments(m[\"key\"])):", "            if True:",
     [f"{H}.Jobs.test_segments_and_not_creatives_go_to_the_content_server"]),
    ("M24", "segment patterns are anchored", BEH,
     "        return [\"^\" + re.escape(p) + \"$\" for p in plan[\"inits\"]] + [rx.pattern for rx, _ in plan[\"medias\"]]",
     "        return [re.escape(p).replace('init', '') for p in plan[\"inits\"]] + [rx.pattern for rx, _ in plan[\"medias\"]]",
     [f"{H}.Jobs.test_segments_and_not_creatives_go_to_the_content_server", f"{H}.Jobs.test_segment_patterns_as_javascript"]),
    ("M25", "sends_capabilities reaches the job", BEH,
     "        \"sendsCapabilities\": list(v.get(\"sends_capabilities\") or []) if cls != \"legacy\" else [],",
     "        \"sendsCapabilities\": [],", [f"{H}.Jobs.test_sends_capabilities"]),
    ("M26", "a live entry is joined at AST + play_from + the span", BEH,
     "    return ast.timestamp() * 1000 + (play_from_s + span_s) * 1000", "    return ast.timestamp() * 1000",
     [f"{H}.Jobs.test_live_now"]),
    ("M27", "the live span is at the fastest rate", BEH,
     "    rate = max([1.0] + [float(a.get(\"rate\") or 1) for a in actions if a.get(\"do\") == \"rate\"])",
     "    rate = 1.0", [f"{H}.Jobs.test_live_now"]),
    ("M28", "a fixture is read beside its vector when not in the source", BEH,
     "    if base is not None and not p.exists() and (base / path).exists():", "    if False:",
     [f"{H}.FixtureBesideTheVector.test_entry_outside_the_source"]),
    ("M29", "a dropped connection prints nothing", PLY,
     "        if isinstance(sys.exc_info()[1], (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)):\n            return\n",
     "", [f"{H}.DroppedConnection.test_reset_prints_nothing"]),
    ("M30", "any other handler exception still prints", PLY,
     "        if isinstance(sys.exc_info()[1], (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)):",
     "        if True:", [f"{H}.DroppedConnection.test_a_handler_exception_still_prints"]),
    ("M32", "the same URL serving a second document is a change on screen", CMP,
     "(_ident_el(e) + ((\"docFixture\", str(e.get(\"docFixture\"))),)", "(_ident_el(e)",
     [f"{H}.PresentationByDocument"]),
    ("M31", "the presentation clock gives a job 4x its observation in wall time", BEH,
     "WALL_FACTOR = {\"presentation\": 4, \"wall\": 1}", "WALL_FACTOR = {\"presentation\": 1, \"wall\": 1}",
     [f"{H}.Jobs.test_clock_and_wall_limit"]),
]


def run_tests(binc: Path, tests: list) -> tuple[bool, str]:
    for pyc in binc.rglob("__pycache__"):
        shutil.rmtree(pyc, ignore_errors=True)
    p = subprocess.run([sys.executable, "-B", "-m", "unittest", *tests], cwd=binc, capture_output=True, text=True,
                       timeout=600)
    last = [ln for ln in p.stderr.splitlines() if ln.startswith(("FAIL:", "ERROR:"))]
    return p.returncode == 0, "; ".join(last)[:300] or p.stderr.strip().splitlines()[-1]


def main():
    SCRATCH.mkdir(parents=True, mode=0o700)
    try:
        binc = SCRATCH / "bin"
        shutil.copytree(PROJECT / "bin", binc, symlinks=True,
                        ignore=shutil.ignore_patterns("node_modules", "__pycache__", "dashif"))
        (binc / "players" / "node_modules").symlink_to(PROJECT / "bin" / "players" / "node_modules")
        # the tests read spec-source/ beside bin/
        (SCRATCH / "spec-source").symlink_to(PROJECT / "spec-source")
        missed = 0
        for mid, rule, f, find, repl, tests in BREAKS:
            path = binc / f
            orig = path.read_text(encoding="utf-8")
            ok, why = run_tests(binc, tests)
            if not ok:
                print(f"{mid} BASELINE RED ({rule}): {why}")
                missed += 1
                continue
            if orig.count(find) != 1:
                print(f"{mid} BREAK NOT APPLIED ({rule}): found {orig.count(find)} times")
                missed += 1
                continue
            path.write_text(orig.replace(find, repl), encoding="utf-8")
            try:
                ok, why = run_tests(binc, tests)
            finally:
                path.write_text(orig, encoding="utf-8")
            if ok:
                missed += 1
                print(f"{mid} NOT CAUGHT  {rule}  [{', '.join(t.split('.', 1)[1] for t in tests)}]")
            else:
                print(f"{mid} CAUGHT      {rule}  -> {why}")
        print(f"{len(BREAKS) - missed} of {len(BREAKS)} caught")
        return 1 if missed else 0
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())

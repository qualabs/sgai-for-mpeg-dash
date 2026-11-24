"""T-09 harness, round 3 (no job selected, geometry background, linear layout, action timing, edges runner): one deliberate break per rule, each run only against the
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
SCRATCH = Path(os.environ.get("XDG_RUNTIME_DIR") or "/tmp") / "cto" / f"t09-mutate-r3-{os.getpid()}"

H = "test_behaviour_harness"
C = "test_behaviour_compare"
CLOCK = "players/adapters/sgai-clock.js"
CMP = "conformance/behaviour_compare.py"
BEH = "conformance/behaviour.py"
PLY = "conformance/players.py"

# (id, rule, file, find, replace, tests)
O = "test_behaviour_opt_in"
BREAKS = [
    ("N01", "a selection with no job cannot tell", BEH,
     "    if not plans:\n        report.cannot.append(", "    if False:\n        report.cannot.append(",
     [f"{H}.NoJobSelected"]),
    ("N02", "the ad box includes the background", CMP,
     'e.get("element") in ("ad", "background")', 'e.get("element") == "ad"',
     [f"{C}.Geometry"]),
    ("N03", "a linear candidate's presentation has layout linear", CMP,
     '(e, "linear" if linear else s["layout"])', '(e, s["layout"])',
     [f"{H}.Sequence"]),
    ("N04", "a viewport layout change is not a new presentation", CMP,
     'run = (_ident_el(e), e.get("inst"), e.get("pass"))', 'run = ((_ident_el(e), s["layout"]), e.get("inst"), e.get("pass"))',
     [f"{H}.Sequence"]),
    ("N05", "a boundary at an action is measured from when it was made", CMP,
     'and a["startedAt"] * k > bt:', 'and False:',
     [f"{H}.ActionTiming"]),
    ("N06", "an action record never moves a boundary earlier", CMP,
     'and a["startedAt"] * k > bt:', 'and True:',
     [f"{H}.ActionTiming"]),
    ("N07", "a bin/ string naming the edges runner is a finding", "test_behaviour_opt_in.py",
     "            for name in (RUNNER, EDGES):", "            for name in (RUNNER,):",
     [f"{O}.Bin.test_rules"]),
    ("N08", "a new DOM element is a new presentation (M15 on the reworded line)", CMP,
     '            run = (_ident_el(e), e.get("inst"), e.get("pass"))', '            run = (_ident_el(e), None, e.get("pass"))',
     [f"{H}.Sequence.test_three_passes_by_element"]),
    ("N09", "a video started again is a new presentation (M16 on the reworded line)", CMP,
     '            run = (_ident_el(e), e.get("inst"), e.get("pass"))', '            run = (_ident_el(e), e.get("inst"), None)',
     [f"{H}.Sequence.test_passes_by_video_restart"]),
    ("N10", "right after a change of driver, media counts at most wall time", CLOCK,
     "? Math.min(dm, dt) : dm;", "? dm : dm;",
     [f"{H}.Clock.test_resume_jump_is_not_presentation", f"{H}.Clock.test_settle_window_edge"]),
    ("N11", "the settle window is SETTLE_MS inclusive", CLOCK,
     "wall - this.switchedAt <= SETTLE_MS", "wall - this.switchedAt < SETTLE_MS",
     [f"{H}.Clock.test_settle_window_edge"]),
    ("N12", "the settle window starts at a change of driver, not at start()", CLOCK,
     "if (d.why !== (this.why || '').split(':')[0]) this.switchedAt = wall;", "this.switchedAt = wall;",
     [f"{H}.Clock"]),
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

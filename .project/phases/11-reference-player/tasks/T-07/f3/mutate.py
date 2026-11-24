"""T-07 family 3 scoped mutation campaign: one deliberate break per rule of
R40.4, R40.5, R40.6, R40.9, each run only on the tests that cover it.

Run from a snapshot (git archive HEAD bin spec-source reference-player) whose
reference-player/src holds the module under test: mutate.py SNAPSHOT [M-ids].
Each break edits the snapshot's copy, runs the covering tests, prints the
summary lines and restores the file. A break whose `find` does not occur
exactly once is NOT APPLIED. Killed = a FAIL (job, field) the baseline does
not have, or, on a field the baseline already fails, a different observation
(judged from the printed lines)."""
import subprocess
import sys
from pathlib import Path

NL = "reference-player/src/sgai-nonlinear.js"
M = [
    ("M1", "R40.4 resume from where it was suspended", NL,
     "if (x.h && x.h.suspended && !this.pauseShown()) { x.h.resume();",
     "if (x.h && x.h.suspended && !this.pauseShown()) { x.slotT = 0; x.h.resume();", "R40.4-1"),
    ("M2", "R40.4 resuming outside the range ends the execution", NL,
     "if (php >= w.end - EPS) { this.endExec(x, 'the span ended'); return; }",
     "if (php >= w.end - EPS && !(x.h && x.h.suspended)) { this.endExec(x, 'the span ended'); return; }", "R40.4-2"),
    ("M3", "R40.5 on-top is composited over the alternative, not suspended", NL,
     "      if (over && w.linearRelation !== 'on-top') {\n        if (x.h && !x.h.suspended)",
     "      if (over) {\n        if (x.h && !x.h.suspended)", "R40.5-1,R40.5-2"),
    ("M4", "R40.5 the cap accrues on the alternative's timeline", NL,
     "if (a !== null && x.lastAlt !== null) d += step(a - x.lastAlt);", "", "R40.5-1"),
    ("M5", "R40.5 the form ends with the alternative presentation", NL,
     "if (x.overAlt && (!lin || lin.alt !== x.overAlt)) {", "if (false) {", "R40.5-2"),
    ("M6", "R40.6 an alternative's windows run on its own timeline", NL,
     "        const php = tl.time();\n        const over = tl.main",
     "        const php = tl.main ? tl.time() : this.mainTl.time();\n        const over = tl.main", "R40.6"),
    ("M7", "R40.9 not shown outside the window's range", NL,
     "if (php >= w.end - EPS) { this.endExec(x, 'the span ended'); return; }", "", "R40.9-1"),
    ("M8", "R40.9 a pause window is anchored to a pause inside its range", NL,
     "if (php >= w.PT && php < w.end) ws.push(w);", "if (php < w.end) ws.push(w);", "R40.9-1"),
    ("M9", "R40.9 supersede: linear events in the span are not executed", NL,
     "(E) => !w.released && E.PRT >= w.PT - 1e-6", "(E) => false && E.PRT >= w.PT - 1e-6", "R40.9-2"),
    ("M10", "R40.9 supersede with no ad: the events execute", NL,
     "if (w.release) w.release();", "", "R40.9-3"),
]


def run(snap, only):
    args = ["python3", "bin/check-dash-conformance.py", "--behaviour", "--clock", "presentation", "--concurrency", "1"]
    for t in only.split(","):
        args += ["--vector", f"spec-source/behaviour/{t}.yaml"]
    p = subprocess.run(args, cwd=snap, capture_output=True, text=True)
    return [l for l in p.stdout.splitlines() if l.startswith(("FAIL ", "exit ")) or "PASS," in l]


def main():
    snap = Path(sys.argv[1])
    want = set(sys.argv[2:])
    for mid, rule, f, find, repl, only in M:
        if want and mid not in want:
            continue
        path = snap / f
        orig = path.read_text()
        print(f"=== {mid} {rule} [{only}]", flush=True)
        if orig.count(find) != 1:
            print(f"NOT APPLIED: find occurs {orig.count(find)} times")
            continue
        path.write_text(orig.replace(find, repl))
        try:
            for l in run(snap, only):
                print(l[:600], flush=True)
        finally:
            path.write_text(orig)


if __name__ == "__main__":
    main()

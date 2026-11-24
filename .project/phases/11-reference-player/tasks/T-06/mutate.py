"""T-06 scoped mutation campaign: one deliberate break per rule of
reference-player/src/sgai-nonlinear.js, each run only against the tests that
cover that rule.

Each break is applied to a copy of the project under ~/.cache/cto-tmp (the
live tree is never edited), the covering jobs run in headless Chromium with
`--save-raw`, and the record is judged twice: as recorded (session clock) and
re-timed on the primary's media clock (media_clock.py). A break is CAUGHT when
a field that PASSES on the unmutated module (the baseline, run the same way in
the same campaign) FAILS with the break, on either clock; NOT CAUGHT
otherwise. A break whose `find` does not occur exactly once is NOT APPLIED.

Usage: mutate.py [M-ids ...]    (default: all)"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[4]
SRC = "reference-player/src/sgai-nonlinear.js"

# (id, rule, find, replace, --only, --class list)
M = [
    ("M01", "PLY-18/19 allowed layouts checked", "if (!w.admitted.includes(layout)) return", "if (false) return", "R5.6", ["D1"]),
    ("M02", "§3.4.3 family default excludes custom", "    pause: ['pause-fullscreen', 'pause-partial'],\n  };\n  // Placeholder", "    pause: ['pause-fullscreen', 'pause-partial'],\n  };\n  DEFAULT.overlay.push('custom');\n  // Placeholder", "R5.6", ["D1"]),
    ("M03", "§5.3.7 video over video needs two decoders", "layout !== 'linear' && decoders < 2", "layout !== 'linear' && decoders < 1", "R5.6", ["D3"]),
    ("M04", "PLY-4 HTML surface capability", "if (f === 'html' && !html)", "if (f === 'html' && false)", "R5.3", ["D4"]),
    ("M05", "R5.9 first-request failure moves to the next option", "img.onerror = () => r(false)", "img.onerror = () => r(true)", "R5.9", ["D1"]),
    ("M06", "PLY-21 custom containment", "if (!(r[0] >= rx - e &&", "if (false && !(r[0] >= rx - e &&", "R39.5", ["D1"]),
    ("M07", "PLY-21 custom unsupported is not renderable", "if (Number(c['sgai-custom-layout'] || 0) !== 1) return", "if (false) return", "R39.5", ["D4"]),
    ("M08", "PLY-15 allowed layouts sent", "if (w.allowedRaw !== null) params.push(['sgai-allowed-layouts', w.allowedRaw]);", "", "R38.2", ["D1"]),
    ("M09", "PLY-16 custom region sent", "if (w.customRegionRaw !== null) params.push(['sgai-custom-region', w.customRegionRaw]);", "", "R39.3", ["D1"]),
    ("M10", "PLY-15 nothing sent when none declared", "if (w.allowedRaw !== null) params.push(['sgai-allowed-layouts', w.allowedRaw]);", "params.push(['sgai-allowed-layouts', w.allowedRaw !== null ? w.allowedRaw : DEFAULT.overlay.join(' ')]);", "R38.2", ["D1"]),
    ("M11", "PLY-14 only prefixed own parameters", "const sends = this.ref.profile.sendsCapabilities || [];", "params.push(['model', 'reference']); const sends = this.ref.profile.sendsCapabilities || [];", "R29.4", ["D1"]),
    ("M12", "PLY-24 cumulative cap stops mid-ad", "if (cumUnits + units > w.capUnits) shown", "if (false) shown", "R4.2", ["D4"]),
    ("M13", "PLY-28 duration rounded up to the cap's timescale", "Math.ceil(c.duration * w.ts - 1e-9)", "(c.duration * w.ts)", "R4.9", ["D4"]),
    ("M14", "PLY-30 a cap of zero does not fire", ": this.capUnits === 0 ? '@durationCap is zero (PLY-30)' : null;", ": null;", "R4.7", None),
    ("M15", "PLY-29 no cap is not a window (read as unbounded)", "? null : Number(a('durationCap'));", "? Infinity : Number(a('durationCap'));", "R4.10", ["D1"]),
    ("M16", "PLY-38 fallback to the next window", "const w = chain.windows.find((x) => !x.failed);", "const w = chain.windows.find((x) => !x.failed); if (w !== chain.windows[0]) return;", "R20.1", None),
    ("M17", "PLY-42 a document of another family fails", "if (family !== w.family) return", "if (false) return", "R20.4", None),
    ("M18", "PLY-43 each window binds with its own declarations", "if (!w.admitted.includes(layout)) return", "if (!w.chain.windows[0].admitted.includes(layout)) return", "R20.5", None),
    ("M19", "PLY-40 order by PT then document order", "(a.PT - b.PT) || (a.order - b.order)", "(a.PT - b.PT) || (b.order - a.order)", "R20.3", None),
    ("M20", "PLY-64 consumed when rendering begins, not at the pause", "if (w.consumed) { this.log('nonlinear:pause-consumed'", "const was = w.consumed; if (w.executeOnce) w.consumed = true; if (was) { this.log('nonlinear:pause-consumed'", "R34.3", ["D1"]),
    ("M21", "PLY-63 once per session", "if (w.consumed) { this.log('nonlinear:pause-consumed'", "if (false) { this.log('nonlinear:pause-consumed'", "R34.1", ["D1"]),
    ("M22", "§5.2.6 repeat", "if (how === 'repeat') {", "if (false) {", "R32.1", ["D1"]),
    ("M23", "PLY-66 request-again + empty = stop", "if (r.failed || !r.plan.length) { slot.stopped = true;", "if (r.failed) { slot.stopped = true;", "R32.2", ["D1"]),
    ("M24", "PLY-9 / §5.2.5 usable lifetime", "if (d.validFor !== null) return now() < d.receivedAt + d.validFor * 1000;", "", "R36.5", ["D1"]),
    ("M25", "PLY-6 not earlier than the offset", "if (!w.doc && php >= w.PT - w.ERT - 1e-6) {", "if (!w.doc) {", "R36.1", ["D1"]),
    ("M26", "R34.10 a document after the window's end is dropped", "if (php >= w.end - EPS) {\n        // The span passed", "if (false) {\n        // The span passed", "R34.10", ["D1"]),
    ("M27", "R34.9 a late execution starts the sequence from its first candidate", "const x = { w, d, PRTA: php,", "const x = { w, d, PRTA: Math.min(php, w.PT),", "$T06_EXT/R34.9.yaml", ["D1"]),
    ("M28", "PLY-48 a superseding window that presents no ad releases the linear events", "if (w.release) w.release();", "", "R40.3", None),
    ("M29", "PLY-86 / R1.4 an aborted ad counts as rendered", "this.endExec(x, 'aborted (PLY-86)');", "this.endExec(x, 'aborted (PLY-86)'); x.w.executed = false; this.fail(x.w, 'mutant');", "R1.4", None),
    ("M30", "§5.1.3 the span ends the presentation", "if (php >= w.end - EPS) { this.endExec(x, 'the span ended'); return; }", "", "$T06_EXT/R34.9.yaml", ["D1"]),
    ("M31", "PLY-33/36 document order of candidates", "for (const c of d.plan) {\n        if (cumUnits >= w.capUnits) break;", "for (const c of d.plan.slice().reverse()) {\n        if (cumUnits >= w.capUnits) break;", "R7.1", ["D1"]),
    ("M32", "PLY-34 a dropped candidate takes no time", "if (sel) out.plan.push(", "if (!sel) out.plan.push({ index: i + 1, doc: url, option: { index: 0 }, layout: 'overlay-lower-third', duration: 2, make: () => document.createElement('div') }); if (sel) out.plan.push(", "R7.1", ["D4"]),
]


def run(cmd, cwd):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def verdicts(text):
    out = {}
    for ln in text.splitlines():
        m = re.match(r"^(PASS|FAIL|NOT_VERIFIABLE|NOT_APPLICABLE)\s+(\S+(?: \S+)*?)\s{2,}(\S+)\s", ln)
        if m:
            out[(m.group(2).strip(), m.group(3))] = m.group(1)
    return out


def judge(copy, only, classes, tag, work):
    raw = work / f"{tag}.raw.json"
    sel = ["--vector", os.path.expandvars(only)] if only.startswith(("/", "$")) else ["--only", only]
    cmd = ["python3", "bin/check-dash-conformance.py", "--behaviour", *sel, "--concurrency", "1", "--save-raw", str(raw)]
    for c in classes or []:
        cmd += ["--class", c]
    _, a = run(cmd, copy)
    mc = work / f"{tag}.mc.json"
    subprocess.run(["python3", str(HERE / "media_clock.py"), str(raw), str(mc)], check=True)
    _, b = run(["python3", "bin/check-dash-conformance.py", "--behaviour", "--replay", str(mc)], copy)
    return verdicts(a), verdicts(b), a, b


def snapshot(work, name):
    d = work / name
    shutil.copytree(PROJ, d, symlinks=True, ignore=shutil.ignore_patterns(
        ".git", "output", "output-analysis", "dist", "node_modules", ".github-ai", ".project"))
    os.symlink(PROJ / "bin/players/node_modules", d / "bin/players/node_modules")
    return d


def main():
    want = set(sys.argv[1:])
    base = Path.home() / ".cache" / "cto-tmp"
    base.mkdir(mode=0o700, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="t06-mut-", dir=base))
    try:
        orig = (PROJ / SRC).read_text()
        baselines = {}
        for mid, rule, find, repl, only, classes in M:
            if want and mid not in want:
                continue
            n = orig.count(find)
            if n != 1:
                print(f"{mid} NOT APPLIED ({rule}): find occurs {n} times", flush=True)
                continue
            key = (only, tuple(classes or []))
            if key not in baselines:
                copy = snapshot(work, "base")
                baselines[key] = judge(copy, only, classes, f"base-{Path(only).name}-{'-'.join(classes or [])}", work)
                shutil.rmtree(copy)
                bs, bm, _, _ = baselines[key]
                print(f"baseline {only} {classes or 'all'}: session {sum(v == 'PASS' for v in bs.values())}/{len(bs)} PASS, "
                      f"media {sum(v == 'PASS' for v in bm.values())}/{len(bm)} PASS", flush=True)
            bs, bm, _, _ = baselines[key]
            copy = snapshot(work, mid)
            (copy / SRC).write_text(orig.replace(find, repl))
            ms, mm, ta, tb = judge(copy, only, classes, mid, work)
            shutil.rmtree(copy)
            caught = [f"{k[0]} {k[1]} ({clock})" for clock, b, m in (("session", bs, ms), ("media", bm, mm))
                      for k, v in b.items() if v == "PASS" and m.get(k) == "FAIL"]
            print(f"{mid} {'CAUGHT' if caught else 'NOT CAUGHT'} — {rule} [{only} {classes or 'all'}]"
                  + (f": {'; '.join(sorted(set(caught))[:6])}" if caught else ""), flush=True)
            if caught:
                first = next((ln for ln in tb.splitlines() if ln.startswith("FAIL")), "") or \
                    next((ln for ln in ta.splitlines() if ln.startswith("FAIL")), "")
                print("    " + first[:400], flush=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

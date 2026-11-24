"""T-07 scoped mutation campaign: one deliberate break per rule of the
presentation (reference-player/src/sgai-compositor.js and what T-07 changed
in sgai-nonlinear.js, sgai-linear.js and sgai-reference.js), each run only
against the tests that cover that rule.

Each break is applied to a copy of the project under ~/.cache/cto-tmp (the
live tree is never edited), the covering jobs run in headless Chromium with
`--save-raw`, and the record is judged twice: as recorded (session clock) and
re-timed on the primary's media clock (../T-06/media_clock.py). A break is
CAUGHT when a field that PASSES on the unmutated module (the baseline, run the
same way in the same campaign) FAILS with the break, on either clock; NOT
CAUGHT otherwise. A field that FAILs in the baseline already can still catch a
break by a numbered item (geometry[0], presentation[2]) that only the mutant
fails; that is reported as "new item". A break whose `find` does not occur
exactly once is NOT APPLIED. A test given as a path runs that vector file (an extended copy,
extend.py) with `--vector`.

Usage: mutate.py [M-ids ...]    (default: all)"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJ = HERE.parents[4]
T06 = HERE.parent / "T-06"
SRC = "reference-player/src/"
EXT = os.environ.get("T07_EXT", "")    # the folder of extended vector copies

C, N, L, R = "sgai-compositor.js", "sgai-nonlinear.js", "sgai-linear.js", "sgai-reference.js"

# (id, rule, file, find, replace, test, classes); a break of several edits
# gives a list of (file, find, replace) in place of `file` and None for the
# two others.
M = [
    ("M01", "R12.5/R27.1 an L-shape shrinks the content",
     C, "        this.squeeze(content, REGION[L]);\n      } else if (DOUBLE_BOX", "      } else if (DOUBLE_BOX", "R27.1", ["D1"]),
    ("M02", "R12.5 the L-shape region is 60% of the AREA (side 77.46%)",
     C, "const L_SIDE = Math.sqrt(0.60) * 100;", "const L_SIDE = 60;", "R27.1", ["D1"]),
    ("M03", "R27.1 the L-shape creative covers the whole frame",
     C, "        place(el, FULL, Z.creative);", "        place(el, [0, 77.46, 100, 22.54], Z.creative);", "R27.1", ["D1"]),
    ("M04", "R26.1 double box: content centre-left, ad centre-right",
     C, "    'squeezeback-double-box': [50, 25, 50, 50],\n    'squeezeback-double-box-background': [50, 25, 50, 50],\n  };",
     "    'squeezeback-double-box': [25, 25, 50, 50],\n    'squeezeback-double-box-background': [25, 25, 50, 50],\n  };", "R26.1", ["D1"]),
    ("M05", "R26.1 the background image fills the bands",
     C, "          h.background.style.visibility = 'visible';", "          h.background.style.visibility = 'hidden';", "R26.1", ["D1"]),
    ("M06", "R12.5 pause-fullscreen: the ad alone",
     C, "const COVERING = new Set(['linear', 'pause-fullscreen']);", "const COVERING = new Set(['linear']);", "R12.5-2", ["D1"]),
    ("M07", "R12.5 pause-partial: the paused frame stays",
     C, "const COVERING = new Set(['linear', 'pause-fullscreen']);", "const COVERING = new Set(['linear', 'pause-fullscreen', 'pause-partial']);", "R12.5-3", ["D1"]),
    ("M08", "§5.3.6 a takeover suspends the primary (static)",
     N, "        this.player.pause();\n        x.heldMain = true;", "        x.heldMain = false;", "R12.5-4", ["D1"]),
    ("M09", "R17.1 PLY-52 a pause ad suspends the overlay (only the top form is shown)",
     C, "        if (x === h) continue;", "        if (x === h || x.kind === 'overlay') continue;", "R17.1", ["D1"]),
    ("M10", "R17.2 PLY-53 the overlay is restored on resume",
     N, "      if (x.h && x.h.suspended && !this.pauseShown()) { x.h.resume();", "      if (x.h && x.h.suspended && false) { x.h.resume();", "R17.2", ["D1"]),
    ("M11", "R17.5 PLY-55 a pause ad over a linear ad (the act order)",
     R, "      for (const f of this.families.slice().reverse()) {", "      for (const f of this.families) {", "R17.5", ["D1"]),
    ("M12", "R19.3 PLY-69 the slot runs on media time (d/r on screen)",
     N, "        if (tl.seeks === x.seeks) d += step(t - x.lastT);", "        if (tl.seeks === x.seeks) d += step((t - x.lastT) / (tl.video.playbackRate || 1));", "R19.3", ["D1"]),
    ("M13", "R22.1 at most one form on screen (both guards: the previous candidate removed, and only the top form shown)",
     [(N, "    showCandidate(x, k) {\n      this.removeSurface(x);", "    showCandidate(x, k) {\n      x.el = null; x.h = null;"),
      (C, "        if (x === h) continue;", "        if (x === h || x.kind === 'overlay') continue;")], None, None, "R22.1", ["D1"]),
    ("M14", "R31.2 PLY-32 the cap does not bound a pause slot",
     N, "      for (const c of d.plan) { slot.plan.push({ c, start: t, shown: c.duration }); t += c.duration; }",
     "      for (const c of d.plan) { slot.plan.push({ c, start: t, shown: Math.min(c.duration, w.capUnits / w.ts) }); t += c.duration; }", "R31.2", ["D1"]),
    ("M15", "R35.4 PLY-75 a dismissal ends the whole overlay slot",
     N, "      this.endExec(x, 'dismissed by the viewer (R35.4)');", "      x.slotT = x.plan[x.k].start + x.plan[x.k].shown;", "R35.4-1", ["D1"]),
    ("M16", "R35.4 PLY-75 no request-again after a pause dismissal",
     N, "        slot.stopped = true;   // no repeat, no request-again (PLY-75)", "        slot.stopped = false; slot.plan = [{ c: slot.plan[slot.k].c, start: 0, shown: 0 }];", "R35.4-2", ["D1"]),
    ("M17", "R35.5 PLY-76 a dismissed takeover does not skip the primary",
     N, "      this.endExec(x, 'dismissed by the viewer (R35.4)');", "      const left = x.plan.reduce((s, p) => s + p.shown, 0) - x.slotT; this.endExec(x, 'dismissed'); this.player.seek(this.main.currentTime + left);", "R35.5", ["D1"]),
    ("M18", "R37.2 PLY-59 resume from the suspended position",
     N, "          this.player.play();\n          return { done: 'pause ad removed, primary resumed' };", "          this.player.seek(this.main.currentTime + 2); this.player.play();\n          return { done: 'pause ad removed, primary resumed' };", "R37.2", ["D1"]),
    ("M19", "R40.4 the default relation suspends and resumes the form (not PLY-49's end)",
     N, "        if (x.h && !x.h.suspended) { x.h.suspend();", "        if (x.h && !x.h.suspended) { this.endExec(x, 'PLY-49'); return; } if (x.h && !x.h.suspended) { x.h.suspend();", "R40.4-1", ["D1"]),
    ("M20", "R40.4 a resumption outside the range ends the execution",
     N, "      if (php >= w.end - EPS) { this.endExec(x, 'the span ended'); return; }", "      if (php >= w.end - EPS && !x.h) { this.endExec(x, 'the span ended'); return; }", "R40.4-2", ["D1"]),
    ("M21", "R40.5 the cap accrues on the alternative's timeline",
     N, "      if (a !== null && x.lastAlt !== null) d += step(a - x.lastAlt);", "      if (a !== null && x.lastAlt !== null) d += 0;", "R40.5-1", ["D1"]),
    ("M22", "R40.5 a form ends with the presentation it is over",
     N, "      if (x.overAlt && (!lin || lin.alt !== x.overAlt)) {", "      if (false) {", "R40.5-2", ["D1"]),
    ("M23", "R40.6 PLY-51 the windows of an alternative's MPD",
     L, "      if (f.ref.nonlinear && f.ref.nonlinear.attachAlternative) {", "      if (false) {", "R40.6", ["D1"]),
    ("M24", "R40.9 a default window presents nothing during a linear ad",
     N, "      if (over && w.linearRelation !== 'on-top') {\n        if (x.h && !x.h.suspended)", "      if (false) {\n        if (x.h && !x.h.suspended)", "R40.4-1", ["D1"]),
    ("M25", "R16.1 PLY-57 the pause ad is removed in the resume's task",
     N, "      this.pauseSlot = null;\n      this.clearPauseSurface(slot);", "      this.pauseSlot = null;\n      setTimeout(() => this.clearPauseSurface(slot), 50);", "R16.1", ["D1"]),
    ("M26", "R19.1 a video form plays at the content's rate",
     N, "      if (v.playbackRate !== rate) v.sgaiPlayer.setPlaybackRate(rate);", "      if (v.playbackRate !== 1) v.sgaiPlayer.setPlaybackRate(1);", "R19.1", ["D1"]),
    ("M27", "R26.3 the background needs an image surface",
     N, "      if (layout === 'squeezeback-double-box-background' && !image) return", "      if (false) return", "R26.3", ["D2"]),
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


def selector(copy, test):
    """An extended copy when there is one; one file for a test named with its
    suffix (R12.5-2); every test of a criterion otherwise (R27.1)."""
    if EXT and (Path(EXT) / f"{test}.yaml").exists():
        return ["--vector", str(Path(EXT) / f"{test}.yaml")]
    if re.match(r"^R\d+\.\d+-\d+$", test):
        return ["--vector", str(copy / "spec-source/behaviour" / f"{test}.yaml")]
    return ["--only", test]


def items(text):
    """Per (job, field): the numbered items a FAIL names (geometry[0],
    presentation[2], ...). A field that FAILs in the baseline already (a
    timing FAIL, or a known defect on another item) can still show a break
    through an item that only the mutant fails."""
    out = {}
    for ln in text.splitlines():
        m = re.match(r"^FAIL\s+(\S+(?: \S+)*?)\s{2,}(\S+)\s+(.*)$", ln)
        if m:
            out[(m.group(1).strip(), m.group(2))] = set(re.findall(r"\b(?:geometry|presentation|selection|requests)\[\d+\]", m.group(3)))
    return out


def judge(copy, test, classes, tag, work):
    raw = work / f"{tag}.raw.json"
    sel = selector(copy, test)
    cmd = ["python3", "bin/check-dash-conformance.py", "--behaviour", *sel, "--concurrency", "1", "--save-raw", str(raw)]
    for c in classes or []:
        cmd += ["--class", c]
    _, a = run(cmd, copy)
    mc = work / f"{tag}.mc.json"
    subprocess.run(["python3", str(T06 / "media_clock.py"), str(raw), str(mc)], check=True)
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
    work = Path(tempfile.mkdtemp(prefix="t07-mut-", dir=base))
    try:
        origs = {f: (PROJ / SRC / f).read_text() for f in (C, N, L, R)}
        baselines = {}
        for mid, rule, f, find, repl, test, classes in M:
            if want and mid not in want:
                continue
            edits = f if isinstance(f, list) else [(f, find, repl)]
            bad = [(ef, origs[ef].count(efind)) for ef, efind, _ in edits if origs[ef].count(efind) != 1]
            if bad:
                print(f"{mid} NOT APPLIED ({rule}): find occurs {bad}", flush=True)
                continue
            key = (test, tuple(classes or []))
            if key not in baselines:
                copy = snapshot(work, "base")
                baselines[key] = judge(copy, test, classes, f"base-{test}-{'-'.join(classes or [])}", work)
                shutil.rmtree(copy)
                bs, bm, _, _ = baselines[key]
                print(f"baseline {test} {classes or 'all'}: session {sum(v == 'PASS' for v in bs.values())}/{len(bs)} PASS, "
                      f"media {sum(v == 'PASS' for v in bm.values())}/{len(bm)} PASS", flush=True)
            bs, bm, _, _ = baselines[key]
            copy = snapshot(work, mid)
            texts = dict(origs)
            for ef, efind, erepl in edits:
                texts[ef] = texts[ef].replace(efind, erepl)
            for ef in {e[0] for e in edits}:
                (copy / SRC / ef).write_text(texts[ef])
            ms, mm, ta, tb = judge(copy, test, classes, mid, work)
            shutil.rmtree(copy)
            caught = [f"{k[0]} {k[1]} ({clock})" for clock, b, m in (("session", bs, ms), ("media", bm, mm))
                      for k, v in b.items() if v == "PASS" and m.get(k) == "FAIL"]
            if not caught:
                _, _, ba, bb = baselines[key]
                for clock, b, m in (("session", items(ba), items(ta)), ("media", items(bb), items(tb))):
                    for k, its in m.items():
                        extra = its - b.get(k, set()) if k in b else set()
                        if extra:
                            caught.append(f"{k[0]} {k[1]} new item {','.join(sorted(extra))} ({clock})")
            print(f"{mid} {'CAUGHT' if caught else 'NOT CAUGHT'} — {rule} [{test} {classes or 'all'}]"
                  + (f": {'; '.join(sorted(set(caught))[:6])}" if caught else ""), flush=True)
            if caught:
                first = next((ln for ln in tb.splitlines() if ln.startswith("FAIL")), "") or \
                    next((ln for ln in ta.splitlines() if ln.startswith("FAIL")), "")
                print("    " + first[:400], flush=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()

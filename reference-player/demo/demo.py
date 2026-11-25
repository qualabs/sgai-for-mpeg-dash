#!/usr/bin/env python3
"""The demo (ADR 0086): one session of the reference with a linear break, an
overlay and a pause ad, played on a page served locally, recorded, and then
checked from the reference's own observation.

    python3 reference-player/demo/demo.py [--out FILE] [--drop ACTION] [--headed]

1. Builds the job of session.yaml (class D1) with bin/conformance/behaviour.py:
   the same local content server, test content and job format as the
   behaviour battery, unchanged.
2. Plays it with record.mjs on the battery's harness page, the pause and the
   resume made at their session times, and records the page with Playwright
   (640x384 WebM) to --out (default:
   .project/phases/11-reference-player/tasks/T-11/demo-session.webm).
3. Asserts, from the adapter's samples of the page's DOM (never from pixels),
   each phase of session.yaml's `presentation` in order: its layout token, its
   start and end on the session clock within the tolerance, the surfaces
   shown, an ad's rectangle (`fills` / `within`), the primary's position when
   it resumes, the primary playing after the resume, and that the pause ad is
   on screen between the pause and the resume.

Output: one PASS line, or one FAIL line per failed check; the full detail
(every observed segment) goes to a log file named on the last line.
--drop ACTION removes the viewer actions named ACTION (`pause`, `resume`) from
the session: the way to see the check fail.

Exit: 0 PASS, 1 FAIL, 2 cannot tell (no frame, harness error, prerequisites
missing), 64 wrong command line. Not part of any battery, build or promotion
(ADR 0087).
"""
from __future__ import annotations

import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "bin"))

from conformance.deps import ensure_yaml  # noqa: E402

ensure_yaml(str(Path(__file__).resolve()), sys.argv[1:])

import yaml  # noqa: E402

from conformance import behaviour, players  # noqa: E402
from conformance.behaviour_compare import attribute, normalise, observed_segments, shows_match  # noqa: E402
from conformance.model import Report  # noqa: E402

VECTOR = HERE / "session.yaml"
SOURCE = ROOT / "spec-source"
DEFAULT_OUT = ROOT / ".project" / "phases" / "11-reference-player" / "tasks" / "T-11" / "demo-session.webm"
CLASS = "D1"
BOX_TOL = 1.0   # percentage points


def tmpdir() -> Path:
    base = os.environ.get("XDG_RUNTIME_DIR") or os.environ.get("TMPDIR") or "/tmp"
    d = Path(base) / "cto" / f"sgai-demo-{time.strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3)}"
    d.mkdir(parents=True, mode=0o700)
    return d


def record(origin: str, job: dict, video_dir: Path, headed: bool) -> dict:
    """record.mjs in its own process group, stopped by the id kept here if it
    overruns."""
    timeout = 120 + job["wallLimitMs"] / 1000
    proc = subprocess.Popen(["node", str(HERE / "record.mjs")], cwd=HERE, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True)
    try:
        out, err = proc.communicate(json.dumps({"origin": origin, "job": job, "videoDir": str(video_dir),
                                                "headed": headed}), timeout=timeout)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.communicate()
        raise RuntimeError(f"record.mjs did not finish in {timeout:.0f} s")
    if proc.returncode != 0:
        raise RuntimeError(f"record.mjs exited {proc.returncode}: {err.strip()[-800:]}")
    return json.loads(out)


def play(drop: list, out: Path, headed: bool, tmp: Path) -> tuple:
    """(vector, fixtures, actions, raw record)."""
    report = Report()
    plans = behaviour.plan_jobs(SOURCE, [VECTOR], [CLASS], report)
    if report.cannot or len(plans) != 1:
        raise RuntimeError("; ".join(report.cannot) or f"{len(plans)} jobs planned, not 1")
    jid, path, v, fx, variant, cls, actions, outcome = plans[0]
    actions = [a for a in actions if a["do"] not in drop]
    missing = players.missing_prerequisites()
    if missing:
        raise RuntimeError("; ".join(missing))
    server = None
    try:
        with behaviour.serving():
            croot, cached = behaviour.content_root(tmp, False)
            content = behaviour.CachedContent(croot) if cached else players.Content(croot)
            server = players._Server(content)
            threading.Thread(target=server.serve_forever, daemon=True).start()
            origin = f"http://127.0.0.1:{server.server_address[1]}"
            media = behaviour.Media(server, origin)
            media_map = []
            for p, u in fx.urls.items():
                if behaviour._is_media_mpd(fx.texts[p]):
                    media_map += media.add(fx.texts[p], u)
            job = behaviour.build_job(jid, v, fx, media_map, cls, actions, SOURCE, media, "presentation", HERE)
            raw = record(origin, job, tmp / "video", headed)
    finally:
        if server is not None:
            server.shutdown()
            server.server_close()
    if raw.get("video"):
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(raw["video"], out)
        raw["video"] = str(out)
    return v, fx, actions, raw


def _rect(el: dict) -> list:
    r = el.get("rect") or {}
    return [r.get("x"), r.get("y"), r.get("width"), r.get("height")]


def _fmt(r) -> str:
    return "[" + ", ".join(f"{x:g}" if isinstance(x, (int, float)) else str(x) for x in r) + "]"


def check(v: dict, fx, actions: list, raw: dict) -> tuple[list, list, list]:
    """(fails, the PASS phrases, the log lines). A fail is
    (phase, field, expected, observed)."""
    ts, tol = v["timescale"], v["tolerance"]
    expected = v["outcomes"][CLASS]["presentation"]
    end = v["observe_until"]
    obs = normalise(raw, ts)
    attribute(obs, fx)
    segs, startup = observed_segments(obs.samples, end, tol)
    log = [f"startup {startup} ms; {len(obs.samples)} samples; actions {raw.get('actions')}",
           f"page errors {raw.get('pageErrors')}; media errors {raw.get('mediaErrors')}"]
    for s in segs:
        log.append(f"segment {s.start:.0f}-{s.end:.0f} layout {s.layout} paused {s.paused} from {s.from_} "
                   f"elements {[{k: e.get(k) for k in ('element', 'docFixture', 'candidateId', 'candidateIndex', 'optionIndex', 'rect', 'time', 'paused')} for e in s.elements]}")
    fails, passes = [], []
    i = 0
    for n, ph in enumerate(expected, 1):
        name = f"{n} {ph['family']}"
        mid = (ph["start"] + ph["end"]) / 2
        hit = next((k for k in range(i, len(segs)) if segs[k].start <= mid < segs[k].end), None)
        if hit is None:
            seen = next((s for s in segs if s.start <= mid < s.end), None)
            fails.append((name, "phase", f"{ph['layout']} at {mid:.0f} ms, after the previous phase",
                          f"{seen.layout} {seen.start:.0f}-{seen.end:.0f}" if seen else "nothing"))
            continue
        i = hit + 1
        s = segs[hit]
        bad = len(fails)
        if s.layout != ph["layout"]:
            fails.append((name, "layout", ph["layout"], s.layout))
        for f in ("start", "end"):
            if abs(getattr(s, f) - ph[f]) > tol:
                fails.append((name, f, f"{ph[f]} ms ±{tol}", f"{getattr(s, f):.0f} ms"))
        shown = [e for e in s.elements]
        if not shows_match(ph["shows"], shown, fx):
            fails.append((name, "shows", json.dumps(ph["shows"])[:200],
                          json.dumps([{k: e.get(k) for k in ("element", "docFixture", "candidateId",
                                                              "candidateIndex", "optionIndex")} for e in shown])[:200]))
        boxes = []
        for want in ph["shows"]:
            if "from" in want:
                p = next((e for e in shown if e.get("element") == "primary"), None)
                if p is None or s.from_ is None or abs(s.from_ - want["from"]) > tol:
                    fails.append((name, "primary from", f"{want['from']} ms ±{tol}",
                                  f"{s.from_:.0f} ms" if s.from_ is not None else "no primary"))
            if "fills" in want or "within" in want:
                el = next((e for e in shown if e.get("element") == "ad" and shows_match([
                    {k: x for k, x in want.items() if k in ("element", "candidate", "option")}], [e], fx)), None)
                r = _rect(el) if el else None
                if "fills" in want:
                    ok = r is not None and all(abs(a - b) <= BOX_TOL for a, b in zip(r, want["fills"]))
                    if not ok:
                        fails.append((name, "ad rect", f"{_fmt(want['fills'])} ±{BOX_TOL:g}", _fmt(r) if r else "no ad"))
                else:
                    x, y, w, h = want["within"]
                    ok = (r is not None and r[2] > 0 and r[3] > 0 and r[0] >= x - BOX_TOL and r[1] >= y - BOX_TOL
                          and r[0] + r[2] <= x + w + BOX_TOL and r[1] + r[3] <= y + h + BOX_TOL)
                    if not ok:
                        fails.append((name, "ad rect", f"inside {_fmt(want['within'])}", _fmt(r) if r else "no ad"))
                    else:
                        boxes.append(f"box {_fmt(r)}")
        if len(fails) == bad:
            passes.append(f"{ph['family']} {s.start / 1000:.1f}-{s.end / 1000:.1f} s" + (f" {boxes[0]}" if boxes else ""))
    # The pause ad is on screen between the pause and the resume, and the
    # primary plays after the resume.
    made = {a["do"]: a for a in raw.get("actions", [])}
    pause = next((p for p in expected if p["family"] == "pause"), None)
    if pause:
        for do, at in (("pause", pause["start"]), ("resume", pause["end"])):
            a = made.get(do)
            got = a.get("startedAt") if a else None
            if got is None or abs(got - at) > tol:
                fails.append((f"viewer {do}", "made at", f"{at} ms ±{tol}", f"{got} ms" if got is not None else "not made"))
            else:
                passes.append(f"viewer {do} at {got / 1000:.1f} s")
    last = expected[-1]
    tail = [x for x in obs.samples if last["start"] + tol <= x["t"] <= end]
    times = [e["time"] for x in tail for e in x["elements"] if e.get("element") == "primary" and not e.get("paused")]
    advance = (max(times) - min(times)) if times else 0
    want_adv = (end - last["start"]) - 2 * tol
    if advance < want_adv - tol:
        fails.append((f"{len(expected)} {last['family']}", "primary playing", f"advances >= {want_adv - tol:.0f} ms",
                      f"{advance:.0f} ms"))
    log.append(f"primary advanced {advance:.0f} ms over {last['start'] + tol}-{end} ms")
    return fails, passes, log


def main(argv: list) -> int:
    out, drop, headed = DEFAULT_OUT, [], False
    args = list(argv)
    while args:
        a = args.pop(0)
        if a == "--headed":
            headed = True
        elif a in ("--out", "--drop") and args:
            val = args.pop(0)
            if a == "--out":
                out = Path(val).resolve()
            else:
                drop.append(val)
        else:
            sys.stderr.write(__doc__)
            return 64
    tmp = tmpdir()
    log_file = out.with_suffix(".log")
    try:
        try:
            v, fx, actions, raw = play(drop, out, headed, tmp)
        except RuntimeError as e:
            print(f"cannot tell: {e}")
            return 2
        size = out.stat().st_size if out.exists() else None
        rec = f"recording {out} ({size / 1e6:.2f} MB)" if size else "no recording"
        if not raw.get("ok") or raw.get("startupMs") is None:
            print(f"cannot tell: {raw.get('harnessError') or 'no frame was shown'}; {rec}")
            return 2
        fails, passes, log = check(v, fx, actions, raw)
        log_file.write_text("\n".join(log + [f"FAIL {f}" for f in fails] + [f"PASS {p}" for p in passes]) + "\n")
        dropped = f" (dropped: {', '.join(drop)})" if drop else ""
        if not fails:
            print(f"PASS demo session{dropped}: " + "; ".join(passes))
        for ph, fld, exp, got in fails:
            print(f"FAIL {ph} | {fld} | expected: {exp} | observed: {got} | log: {log_file}")
        print(f"{rec}; full log: {log_file}")
        return 1 if fails else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

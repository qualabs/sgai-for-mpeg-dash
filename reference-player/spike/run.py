"""T-01 spike: does a module on the public API of the pinned dash.js 5.3.0
execute 6th-edition InsertPresentation and ReplacePresentation?

    python3 reference-player/spike/run.py [--out DIR]

Reuses bin/conformance/players.py (ffmpeg test content, the local server that
serves bin/players/harness.html and the pinned dash.js) and Playwright from
bin/players. The only addition to the server, in this process only, is the
/spike/ prefix for this directory. Prints a table of measured vs expected
main-presentation positions; with --out, writes raw.json and results.json.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import shutil
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "bin"))
from conformance import players  # noqa: E402

INSERT = players.INSERT_SCHEME
REPLACE = players.REPLACE_SCHEME
AD_S = 6.0          # duration of the alternative presentation
TOL_EXEC = 0.10     # PRTA - PRT allowed at a scheduled execution (s)
TOL_RETURN = 0.10   # |main position at resume - RT| allowed, static main (s)
TOL_RETURN_LIVE = 0.50

AV = """    <AdaptationSet id="1" contentType="video" mimeType="video/mp4" codecs="avc1.64001F"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4" media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="v" bandwidth="800000" width="{w}" height="{h}"/>
    </AdaptationSet>
    <AdaptationSet id="2" contentType="audio" mimeType="audio/mp4" codecs="mp4a.40.2"
                   segmentAlignment="true" startWithSAP="1">
      <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
                       initialization="$RepresentationID$/init.mp4" media="$RepresentationID$/$Number$.m4s"/>
      <Representation id="a" bandwidth="128000" audioSamplingRate="48000"/>
    </AdaptationSet>"""


def static_mpd(dur: str, events: str = "", w=640, h=360) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static" profiles="urn:mpeg:dash:profile:isoff-live:2011"
     mediaPresentationDuration="{dur}" minBufferTime="PT2S">
  <Period id="p0" start="PT0S">
{events}
{AV.format(w=w, h=h)}
  </Period>
</MPD>
"""


def live_mpd(ast: datetime, events: str) -> str:
    iso = ast.strftime("%Y-%m-%dT%H:%M:%SZ")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="dynamic" profiles="urn:mpeg:dash:profile:isoff-live:2011"
     availabilityStartTime="{iso}" publishTime="{iso}" minimumUpdatePeriod="PT10S"
     timeShiftBufferDepth="PT60S" minBufferTime="PT2S">
  <Period id="p0" start="PT0S">
{events}
{AV.format(w=640, h=360)}
  </Period>
</MPD>
"""


def stream(scheme: str, element: str, attrs: str, prt=10000, dur=5000) -> str:
    return f"""    <EventStream schemeIdUri="{scheme}" timescale="1000">
      <Event id="1" presentationTime="{prt}" duration="{dur}">
        <{element} uri="{{ad}}" {attrs}/>
      </Event>
    </EventStream>"""


# id -> (MPD text, page opts, run until main position, expected-return rule)
def cases(now: datetime) -> dict:
    ins = lambda a="": stream(INSERT, "InsertPresentation", a)          # noqa: E731
    rep = lambda a="", **k: stream(REPLACE, "ReplacePresentation", a, **k)  # noqa: E731
    return {
        "insert": (static_mpd("PT30S", ins()), {}, 13.0),
        "insert-seekback": (static_mpd("PT30S", ins()), {"seekAfterResume": {"1": 8}}, 13.0),
        "insert-once": (static_mpd("PT30S", ins('executeOnce="true"')), {"seekAfterResume": {"1": 8}}, 13.0),
        "replace": (static_mpd("PT40S", rep()), {}, 19.0),
        "replace-maxduration": (static_mpd("PT40S", rep('maxDuration="4000"')), {}, 17.0),
        "replace-returnoffset": (static_mpd("PT40S", rep('returnOffset="8000"')), {}, 21.0),
        "replace-join-clip": (static_mpd("PT40S", rep('maxDuration="6000"')), {"startTime": 12}, 17.0),
        "replace-join-noclip": (static_mpd("PT40S", rep('maxDuration="6000" clip="false"')),
                                {"startTime": 12}, 21.0),
        "replace-live": (live_mpd(now - timedelta(seconds=30), rep(prt=40000)), {}, 49.0),
    }


def expected_rt(case: str, E: dict) -> tuple[float, str]:
    """RT from §5.16 Table 57, computed here from the MPD values and the
    measured PRTA, not read from the module."""
    PRT, PRTA = E["PRT"], E["PRTA"]
    if case.startswith("insert"):
        return PRTA, "insertion: RT = PRTA"
    APD = AD_S
    APDmax = {"replace-maxduration": 4.0, "replace-join-clip": 6.0,
              "replace-join-noclip": 6.0}.get(case, float("inf"))
    clip = case != "replace-join-noclip"
    APDadj = max(APDmax - PRTA + PRT, 0) if clip else APDmax
    APDA = min(APD - 0, APDadj)  # ASO = 0: @startWithOffset absent
    if case == "replace-returnoffset":
        return PRT + 8.0, "RT = PRT + RO"
    if not clip:
        return PRTA + APDA, f"@clip=false: RT = PRTA + APDA (APDA={APDA:.3f})"
    return PRT + APDA, f"RT = PRT + APDA (APDA={APDA:.3f})"


def register(server, origin: str, key: str, text: str) -> None:
    text = text.replace("{ad}", f"{origin}/m/ad6.mpd")
    new, _ = players.rewrite(text, f"{origin}/c/{key}/")
    server.mpds[key] = (new, players.plan(new, f"{origin}/c/{key}/"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, help="directory to write raw.json and results.json")
    ap.add_argument("--only", nargs="*", help="case ids to run")
    a = ap.parse_args()
    missing = players.missing_prerequisites()
    if missing:
        print("cannot run:", *missing, sep="\n  ", file=sys.stderr)
        return 2

    base = os.environ.get("XDG_RUNTIME_DIR") or os.environ.get("TMPDIR") or "/tmp"
    tmp = Path(base) / "cto" / f"t01-spike-{time.strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3)}"
    tmp.mkdir(parents=True, mode=0o700)
    players.PREFIXES["/spike/"] = HERE  # this process only
    server = players._Server(players.Content(tmp))
    raw = {"results": []}
    try:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f"http://127.0.0.1:{server.server_address[1]}"
        register(server, origin, "ad6", static_mpd("PT6S", w=320, h=180))
        names = [k for k in cases(datetime.now(timezone.utc)) if not a.only or k in a.only]
        for k in names:
            # Built right before its run: a live MPD's availabilityStartTime is
            # relative to now.
            text, opts, until = cases(datetime.now(timezone.utc))[k]
            register(server, origin, k, text)
            job = {"id": k, "mpd": f"{origin}/m/{k}.mpd", "opts": opts,
                   "untilMainTime": until, "timeoutMs": 90000}
            proc = subprocess.Popen(["node", str(HERE / "run-spike.mjs")], stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                    start_new_session=True)
            try:
                out, err = proc.communicate(json.dumps({"origin": origin, "cases": [job]}), timeout=180)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.communicate()
                print(f"run-spike.mjs timed out on {k}", file=sys.stderr)
                return 2
            if proc.returncode != 0:
                print(f"run-spike.mjs exited {proc.returncode} on {k}: {err[-800:]}", file=sys.stderr)
                return 2
            got = json.loads(out)
            raw["browser"] = got["browser"]
            raw["results"] += got["results"]
    finally:
        server.shutdown()
        server.server_close()
        shutil.rmtree(tmp, ignore_errors=True)

    results = []
    for r in raw["results"]:
        log = (r.get("state") or {}).get("log", [])
        execs = [e for e in log if e["type"] == "module:execute"]
        terms = [e for e in log if e["type"] == "module:terminate"]
        resumes = [e for e in log if e["type"] == "main:resumed"]
        after1 = [e for e in log if e["type"] == "main:after1s"]
        alts = [e for e in log if e["type"] == "alt:playing"]
        onstart = [e for e in log if e["type"] == "dashjs:onStart"]
        recv = [e for e in log if e["type"] == "dashjs:onReceive"]
        row = {"id": r["id"], "executions": len(execs), "errors": (r.get("state") or {}).get("errors"),
               "pageErrors": r.get("pageErrors"), "external": r.get("external"),
               "timedOut": r.get("timedOut", False), "harnessError": r.get("harnessError"),
               "received": recv[0]["data"] if recv else None,
               "dashjsOnStartAt": [e["data"]["php"] for e in onstart],
               "isDynamic": (r.get("state") or {}).get("isDynamic")}
        row["runs"] = []
        for i, ex in enumerate(execs):
            E = {"PRT": ex["data"]["PRT"], "PRTA": ex["data"]["PRTA"]}
            rt, rule = expected_rt(r["id"], E)
            t = terms[i]["data"] if i < len(terms) else {}
            res = resumes[i]["data"] if i < len(resumes) else {}
            tol = TOL_RETURN_LIVE if r["id"].endswith("live") else TOL_RETURN
            join = r["id"].startswith("replace-join")
            before_ok = (abs(ex["data"]["pauseAt"] - 12.0) <= 0.3) if join else \
                (0 <= ex["data"]["pauseAt"] - E["PRT"] <= TOL_EXEC)
            after = res.get("php")
            row["runs"].append({
                "PRT": E["PRT"], "PRTA": round(E["PRTA"], 3), "mainBefore": round(ex["data"]["pauseAt"], 3),
                "beforeOk": before_ok,
                "altGapMs": alts[i]["data"]["gapMs"] if i < len(alts) else None,
                "APDA": t.get("APDA"), "altPlayed": round(t["altPlayed"], 3) if "altPlayed" in t else None,
                "expectedRT": round(rt, 3), "rule": rule,
                "mainAfter": round(after, 3) if after is not None else None,
                "afterOk": after is not None and abs(after - rt) <= tol, "tolerance": tol,
                "returnGapMs": res.get("gapMs"),
                "mainAfter1s": round(after1[i]["data"]["php"], 3) if i < len(after1) else None,
            })
        results.append(row)

    exp_execs = {"insert-seekback": 2}
    print(f"dash.js {raw['results'][0].get('dashjs')}  {raw['browser']}")
    print(f"{'case':22} {'n':>2} {'PRT':>6} {'before':>7} {'alt':>6} {'RTexp':>7} {'after':>7} "
          f"{'+1s':>7}  verdict")
    ok_all = True
    for row in results:
        want = exp_execs.get(row["id"], 1)
        n_ok = row["executions"] == want and not row["timedOut"] and not row["errors"]
        if not row["runs"]:
            print(f"{row['id']:22} {row['executions']:>2}  -- no execution "
                  f"{row['harnessError'] or row['errors'] or ''}")
            ok_all = False
            continue
        for run in row["runs"]:
            ok = n_ok and run["beforeOk"] and run["afterOk"]
            ok_all &= ok
            print(f"{row['id']:22} {row['executions']:>2} {run['PRT']:>6.2f} {run['mainBefore']:>7.3f} "
                  f"{(run['altPlayed'] or 0):>6.2f} {run['expectedRT']:>7.3f} {run['mainAfter'] or -1:>7.3f} "
                  f"{run['mainAfter1s'] or -1:>7.3f}  {'OK' if ok else 'NO'}  ({run['rule']})")
    if a.out:
        a.out.mkdir(parents=True, exist_ok=True)
        (a.out / "raw.json").write_text(json.dumps(raw, indent=1))
        (a.out / "results.json").write_text(json.dumps(results, indent=1))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())

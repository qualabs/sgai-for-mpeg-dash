"""Separates what the module decided from how fast the page played, for each
job of a `--save-raw` record of the behaviour battery:
  - the module's decisions in media time (moduleLog: PRT, PRTA, APDA, RT);
  - the primary's speed: media seconds per wall second from the first frame
    to the first ad sample (1.00 = real time);
  - each ad span on screen in wall seconds against the APDA it played.
A transition the vector places at session T is late by the primary's
deficit (T x (1 - speed)) plus the switch gap; this is what the report's
timing classification rests on.  Usage: timing.py RAW.json [substring]"""
import json, sys

d = json.load(open(sys.argv[1]))
pick = sys.argv[2] if len(sys.argv) > 2 else ""
for j in d["jobs"]:
    name = f"{j['vector'].split('/')[-1][:-5]} {j['variant'] or ''}".strip()
    if pick not in name:
        continue
    r = j["raw"]; obs = r["observation"]; ff = r.get("startupMs") or obs.get("firstFrame") or 0
    ss = obs["samples"]
    prim = [(s["t"], e["time"]) for s in ss for e in s["elements"] if e["element"] == "primary" and not e.get("paused")]
    first_ad = next((s["t"] for s in ss if any(e["element"] == "ad" for e in s["elements"])), None)
    pre = [p for p in prim if first_ad is None or p[0] < first_ad]
    speed = (pre[-1][1] - pre[0][1]) / (pre[-1][0] - pre[0][0]) if len(pre) > 1 and pre[-1][0] > pre[0][0] else None
    print(f"{name}: startup {ff} ms; primary speed before the ad {speed and round(speed, 3)}")
    for m in obs["moduleLog"]:
        if m["type"] in ("linear:execute", "linear:terminate", "linear:failed", "linear:not-executed"):
            dd = m["data"]
            keep = {k: (round(v, 3) if isinstance(v, float) else v) for k, v in dd.items() if k in ("key", "PRT", "PRTA", "ASO", "APDadj", "APDA", "RT", "reason")}
            keep["key"] = str(keep.get("key", "")).split(":")[-1]
            print(f"    session {m['t'] - ff:>6} ms  {m['type']:<20} {keep}")
    # ad spans on screen
    span = None
    last_t = ss[-1]["t"] if ss else 0
    for s in ss + [{"t": last_t, "elements": [], "end": True}]:
        ad = next((e.get("candidateId") for e in s["elements"] if e["element"] == "ad"), None)
        if ad and (span is None or span[0] != ad):
            if span: print(f"    ad {span[0]} on screen {span[1] - ff}..{s['t'] - ff} ms = {(s['t'] - span[1]) / 1000:.3f} s")
            span = (ad, s["t"])
        elif not ad and span:
            end = s["t"]
            more = " (still on screen when observation ended)" if s.get("end") else ""
            print(f"    ad {span[0]} on screen {span[1] - ff}..{end - ff} ms = {(end - span[1]) / 1000:.3f} s{more}")
            span = None

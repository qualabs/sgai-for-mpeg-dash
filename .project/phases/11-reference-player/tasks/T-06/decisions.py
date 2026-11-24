"""The non-linear family's own decisions per job of a `--save-raw` record, in
media time (the primary's currentTime when the module took them), next to the
page's speed: what was requested (URL, playhead), skipped and why, the plan an
execution computed (each candidate's slot start and shown duration, the cap),
what was shown and when it ended, and the pause slot's steps on its own
clock. The expected values are worked by hand from the criteria in the
README; this script only prints what the module decided.
Usage: decisions.py RAW.json [substring]"""
import json
import sys

d = json.load(open(sys.argv[1]))
pick = sys.argv[2] if len(sys.argv) > 2 else ""
SKIP = {"nonlinear:receive"}
for j in d["jobs"]:
    name = f"{j['vector'].split('/')[-1][:-5]} {j['class']}"
    if pick not in name:
        continue
    r = j["raw"]
    if not r or not r.get("ok"):
        print(f"{name}: no record")
        continue
    obs = r["observation"]
    ff = r.get("startupMs") or obs.get("firstFrame") or 0
    prim = [(s["t"], e["time"]) for s in obs["samples"] for e in s["elements"] if e["element"] == "primary" and not e.get("paused")]
    speed = (prim[-1][1] - prim[0][1]) / (prim[-1][0] - prim[0][0]) if len(prim) > 1 and prim[-1][0] > prim[0][0] else None
    print(f"{name}: startup {ff} ms; primary media/wall over the run {speed and round(speed, 3)}")
    for m in obs["moduleLog"]:
        t = m["type"]
        if not t.startswith("nonlinear") or t in SKIP:
            continue
        x = dict(m["data"] or {})
        x.pop("key", None)
        for k in ("php", "PRTA", "slotT"):
            if isinstance(x.get(k), float):
                x[k] = round(x[k], 3)
        if t == "nonlinear:execute":
            x["plan"] = [f"c{p['candidate']}/o{p['option']} {p['layout']} slot {round(p['start'], 3)}+{round(p['shown'], 3)} -> media {round(p['until'], 3)}" for p in x["plan"]]
        print(f"    session {m['t'] - ff:>6}  {t[10:]:<18} {json.dumps(x)[:300]}")

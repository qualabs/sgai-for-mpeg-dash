"""The reference's own decisions per job of a `--save-raw` record, on the
clocks the module keeps: for each non-linear execution the slot time
(`slotT`) and the playhead of the presentation that declares the window
(`php`) when a form was shown, suspended, resumed and ended, the pause slot's
steps, and the linear family's execute/terminate. Next to it, the page's
speed (the primary's media time over wall time). This prints what the module
decided; the expected values are worked by hand from the criteria in
README.md. Usage: decisions.py RAW.json [substring]"""
import json
import sys

d = json.load(open(sys.argv[1]))
pick = sys.argv[2] if len(sys.argv) > 2 else ""
KEEP = ("nonlinear:execute", "nonlinear:show", "nonlinear:end", "nonlinear:suspend", "nonlinear:resume",
        "nonlinear:pause", "nonlinear:pause-show", "nonlinear:pause-close", "nonlinear:pause-exhausted",
        "nonlinear:dismissed", "nonlinear:failed", "nonlinear:request", "nonlinear:alternative",
        "nonlinear:alternative-gone", "linear:execute", "linear:started", "linear:terminate")
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
    prim = [(s["t"], e["time"]) for s in obs["samples"] for e in s["elements"]
            if e["element"] == "primary" and not e.get("paused")]
    speed = (prim[-1][1] - prim[0][1]) / (prim[-1][0] - prim[0][0]) if len(prim) > 1 and prim[-1][0] > prim[0][0] else None
    print(f"{name}: startup {ff} ms; primary media/wall over the run {speed and round(speed, 3)}")
    for a in r.get("actions", []):
        print(f"    session {a.get('startedAt'):>6}  action {a['do']:<11} {json.dumps(a.get('result'))[:160]}")
    for m in obs["moduleLog"]:
        t = m["type"]
        if t not in KEEP:
            continue
        x = dict(m["data"] or {})
        x.pop("key", None)
        for k, v in list(x.items()):
            if isinstance(v, float):
                x[k] = round(v, 3)
        if t == "nonlinear:execute":
            x["plan"] = [f"c{p['candidate']}/o{p['option']} {p['layout']} slot {round(p['start'], 3)}+{round(p['shown'], 3)}"
                         for p in x["plan"]]
        print(f"    session {m['t'] - ff:>6}  {t:<26} {json.dumps(x)[:260]}")

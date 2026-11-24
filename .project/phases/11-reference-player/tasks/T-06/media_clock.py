"""Re-times a `--save-raw` record of the behaviour battery on the primary's
media clock, so that `check-dash-conformance.py --behaviour --replay` judges
what the module decided rather than how fast this machine played the page.

Between two consecutive samples where the primary is on screen, playing,
and not sought, the time that passes is the media time the primary advanced
divided by its rate; anywhere else (startup, a pause, a seek, the primary
hidden behind a linear ad) it is the wall time that passed. Every wall time of
the record (samples, requests, the first frame, the module's log) is mapped
through that piecewise-linear function. Nothing the module reports enters
the mapping: it is read off the primary <video>'s sampled currentTime only,
so a module that shows an ad at the wrong media time still fails the replay.

Usage: media_clock.py IN.raw.json OUT.raw.json"""
import json
import sys


def mapping(samples):
    pts = []          # (wall t, media-clock t)
    prev = None
    T = 0.0
    for s in sorted(samples, key=lambda s: s["t"]):
        if prev is None:
            T = float(s["t"])
        else:
            dt = s["t"] - prev["t"]
            pa = next((e for e in prev["elements"] if e.get("element") == "primary"), None)
            pb = next((e for e in s["elements"] if e.get("element") == "primary"), None)
            step = dt
            if pa and pb and not pa.get("paused") and not s.get("seek") and pa.get("time") is not None and pb.get("time") is not None:
                r = pa.get("rate") or 1.0
                dm = (pb["time"] - pa["time"]) / r
                if 0 <= dm <= dt * 3 + 100:
                    step = dm
            T += step
        pts.append((s["t"], T))
        prev = s
    return pts


def f(pts, t):
    if not pts or t <= pts[0][0]:
        return t if not pts else pts[0][1] - (pts[0][0] - t)
    for (a, A), (b, B) in zip(pts, pts[1:]):
        if a <= t <= b:
            return A + (B - A) * ((t - a) / (b - a) if b > a else 0)
    return pts[-1][1] + (t - pts[-1][0])


def retime(raw):
    obs = raw.get("observation") or {}
    pts = mapping(obs.get("samples", []))
    m = lambda t: int(round(f(pts, t)))  # noqa: E731
    t0 = raw["t0"]
    for s in obs.get("samples", []):
        s["t"] = m(s["t"])
    for k in ("firstFrame",):
        if obs.get(k) is not None:
            obs[k] = m(obs[k])
    if raw.get("startupMs") is not None:
        raw["startupMs"] = m(raw["startupMs"])
        raw["origin"] = t0 + raw["startupMs"]
    for r in raw.get("requests", []):
        r["wall"] = t0 + m(r["wall"] - t0)
    for x in obs.get("moduleLog", []):
        if x.get("t") is not None:
            x["t"] = m(x["t"])
    for d in obs.get("destinations", []):
        d["t"] = m(d["t"])


def main():
    d = json.load(open(sys.argv[1]))
    for j in d["jobs"]:
        if j.get("raw") and j["raw"].get("ok"):
            retime(j["raw"])
    json.dump(d, open(sys.argv[2], "w"))


if __name__ == "__main__":
    main()

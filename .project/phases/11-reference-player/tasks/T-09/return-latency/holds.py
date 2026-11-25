import json,sys
raw=json.load(open(sys.argv[1]))
for j in raw["jobs"]:
    r=j["raw"] or {}
    o=r.get("observation") or {}
    holds=(o.get("clock") or {}).get("holds") or []
    lh=max(holds,key=lambda h:(h[3],h[2])) if holds else None
    ev=[]
    for e in o.get("moduleLog",[]):
        t=e["type"]; d=e.get("data") or {}
        if t=="linear:started": ev.append(f"started gap {d.get('gapMs')}")
        elif t=="linear:execute": ev.append(f"exec PRT {d.get('PRT')} PRTA {round(d.get('PRTA',0),3)}")
        elif t=="linear:ready-ahead": ev.append(f"ready@{e['t'] and round(e['t'])} RT {d.get('RT')} from {round(d.get('from',0),3)} alt {round(d.get('alt',0),2)}")
        elif t=="linear:terminate": ev.append(f"term@{e['t'] and round(e['t'])} RT {d.get('RT')} ra {d.get('readyAhead')} rs {d.get('readyState')}")
    name=j["vector"].split("/")[-1]
    print(name, j["class"], j["variant"], "| longest hold", [round(x) for x in lh] if lh else None, "| n", len(holds), "|", "; ".join(ev))

"""Evidence helpers for T-03: synthetic raw for UC-01 D1, and hand-made vector copies."""
import copy, json, sys
from pathlib import Path
import yaml
ROOT = Path(sys.argv[1]); W = Path(sys.argv[2])
sys.path.insert(0, str(ROOT / "bin"))
from test_behaviour_compare import synthetic_raw
from conformance import behaviour
src = ROOT / "spec-source"
uc = src / "scenarios" / "UC-01.yaml"
v = yaml.safe_load(uc.read_text())
fx = behaviour.fixtures_of(v, src)
raw = synthetic_raw(v, v["outcomes"]["D1"], fx)
# (B) the expected observation, injected as if the browser had recorded it
(W / "uc01-d1.synthetic.raw.json").write_text(json.dumps(
    {"source": str(src), "jobs": [{"vector": str(uc), "variant": None, "class": "D1", "raw": raw}]}, indent=1))
# (C) a copy of UC-01 with one expected value changed by hand: q1 beacon 3750 -> 4750
text = uc.read_text()
old = '{at: 3750, fixture: examples/annex-a/A.4-1.mpd, id: "3"'
assert text.count(old) == 1
(W / "UC-01-q1-moved.yaml").write_text(text.replace(old, '{at: 4750, fixture: examples/annex-a/A.4-1.mpd, id: "3"'))
(W / "uc01-d1.synthetic-vs-copy.raw.json").write_text(json.dumps(
    {"source": str(src), "jobs": [{"vector": str(W / "UC-01-q1-moved.yaml"), "variant": None, "class": "D1", "raw": raw}]}, indent=1))
# (D) a copy of UC-01 whose D1 outcome is what the skeleton does (no ad logic), and one value changed in it
sk = copy.deepcopy(v)
sk["outcomes"] = {"D1": {
    "summary": "What the skeleton does: the event is not acted on; the episode plays from 0.",
    "requests": [],
    "selection": [{"opportunity": {"fixture": "examples/annex-a/A.2-1.mpd", "event_id": "1"},
                   "result": "ignored", "presented": []}],
    "presentation": [{"start": 0, "end": 35000, "layout": "none", "shows": [{"element": "primary", "from": 0}]}],
    "beacons": []}}
(W / "UC-01-skeleton.yaml").write_text(yaml.safe_dump(sk, sort_keys=False))
sk["outcomes"]["D1"]["presentation"][0]["shows"][0]["from"] = 2000
(W / "UC-01-skeleton-from-2000.yaml").write_text(yaml.safe_dump(sk, sort_keys=False))
print("written:", *sorted(p.name for p in W.iterdir()), sep="\n  ")

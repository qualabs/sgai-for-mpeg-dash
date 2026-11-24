"""Mutation campaign for T-04 part C: one deliberate break per test, applied
to a copy of spec-source/, then bin/check-behaviour.py --source <copy>.
Each break must produce a finding naming its test file."""
import os, re, shutil, subprocess, sys

REPO = sys.argv[1]
WORK = sys.argv[2]
SRC = os.path.join(WORK, "spec-source")
if os.path.exists(SRC):
    shutil.rmtree(SRC)
shutil.copytree(os.path.join(REPO, "spec-source"), SRC)
B = os.path.join(SRC, "behaviour")

# (test file, file to edit relative to behaviour/, old, new, expected check, what it breaks)
M = [
    ("R12.5-1.yaml", "R12.5-1.yaml", "primary: {x: 22.54, y: 0, width: 77.46", "primary: {x: 32.54, y: 0, width: 77.46",
     "S-GEOM", "L-shape upper-right primary shifted 10 points right (out of the viewport)"),
    ("R12.5-2.yaml", "R12.5-2.yaml", "layout: pause-fullscreen, shows", "layout: pause-full, shows",
     "S-LAYOUT", "a token that is not R12.2's"),
    ("R12.5-3.yaml", "fixtures/R12.5/pause-partial.xml", 'layout="pause-partial"', 'layout="pause-half"',
     "S-FIXTURE", "the fixture's layout token not in the schema"),
    ("R12.5-4.yaml", "R12.5-4.yaml", "{at: 4000, tolerance: 1, ad:", "{at: 7000, tolerance: 1, ad:",
     "S-GEOM", "an ad rectangle at an instant the presentation shows no ad"),
    ("R16.1.yaml", "R16.1.yaml", "{start: 3000, end: 6000, layout: pause-fullscreen", "{start: 3000, end: 5900, layout: pause-fullscreen",
     "S-TIME", "a gap in the presentation (pause ad ends 100 ms early)"),
    ("R17.1.yaml", "R17.1.yaml", "&p {fixture: behaviour/fixtures/R17.1/pause.xml, index: 1}", "&p {fixture: behaviour/fixtures/R17.1/pause.xml, index: 2}",
     "S-REF", "a pause candidate the document does not have"),
    ("R17.2.yaml", "R17.2.yaml", '"https://t.example.com/r17-2/ov-mid"', '"https://t.example.com/r17-2/ov-quartile"',
     "S-REF", "a beacon URL that is not the event's text"),
    ("R17.5.yaml", "R17.5.yaml", "R17.5/list.mpd, id: ad-1}", "R17.5/list.mpd, id: ad-9}",
     "S-REF", "a linear candidate id the List MPD does not have"),
    ("R19.1.yaml", "R19.1.yaml", "D2: {sgai-video-decoders: 2,", "D2: {sgai-video-decoders: 1,",
     "S-CAPS", "D2 declared with one decoder"),
    ("R19.3.yaml", "R19.3.yaml", 'candidate: *a, id: "2"', 'candidate: *a, id: "9"',
     "S-REF", "a beacon @id the candidate does not schedule"),
    ("R22.1.yaml", "fixtures/R22.1/overlay.xml", 'mimeType="image/png" \n', None,
     "S-FIXTURE", "an image option without @duration (DOC-6)"),
    ("R25.1.yaml", "fixtures/R25.1/live.mpd", '<Metrics metrics="PlayList">', '<Metrics metrics="HttpList">',
     "S-FIXTURE", "a pause window with no PlayList metrics (R33.4)"),
    ("R26.1.yaml", "R26.1.yaml", "{at: 8000, tolerance: 1, primary: {x: 0, y: 25,", "{at: 8000, tolerance: 1, primary: {x: 60, y: 25,",
     "S-GEOM", "a double-box primary box that leaves the viewport"),
    ("R26.3.yaml", "R26.3.yaml", "{candidate: *c, option: {index: 2}, layout: squeezeback-double-box}", "{candidate: *c, option: {index: 4}, layout: squeezeback-double-box}",
     "S-REF", "an option the candidate does not have"),
    ("R27.1.yaml", "fixtures/R27.1/overlay.xml", 'layout="squeezeback-l-shape-upper-right"', 'layout="squeezeback-l-shape-upper-right"\n                              background="https://ads-cdn.example.com/beh/r27-1/bg.png"',
     "S-FIXTURE", "a background on an L-shape option"),
    ("R27.3.yaml", "fixtures/R27.3/l-shape-ad.mpd", None, None,
     "S-FIXTURE", "the video creative's sub-MPD deleted"),
    ("R31.2.yaml", "R31.2.yaml", "criterion_sha256: e3765bd5", "criterion_sha256: f3765bd5",
     "B-HASH", "a hash that is not the criterion's"),
    ("R35.4-1.yaml", "R35.4-1.yaml", "{at: 4000, do: dismiss}", "{at: 4000, do: skip}",
     "B-SCHEMA", "an action the schema does not know"),
    ("R35.4-2.yaml", "R35.4-2.yaml", "answered_by: behaviour/fixtures/R35.4/pause.xml", "answered_by: behaviour/fixtures/R35.4/overlay.xml",
     "S-FIXTURE", "answered by a fixture the test does not list"),
    ("R35.5.yaml", "R35.5.yaml", "observe_until: 8000", "observe_until: 9000",
     "S-TIME", "a presentation that stops short of observe_until"),
    ("R37.2.yaml", "R37.2.yaml", "criterion: R37.2\n", "criterion: R37.9\n",
     "B-", "a criterion that is not its file's"),
    ("R40.4-1.yaml", "R40.4-1.yaml", 'R40.4/main.mpd, event_id: "2"', 'R40.4/main.mpd, event_id: "7"',
     "S-REF", "an opportunity the main MPD does not declare"),
    ("R40.4-2.yaml", "R40.4-2.yaml", "        answered_by: behaviour/fixtures/R40.4/overlay-r.xml\n", "",
     "S-SCHEMA", "a request with no answered_by and no aps entry"),
    ("R40.5-1.yaml", "fixtures/R40.5/main-cap.mpd", 'linearRelation="on-top"', 'linearRelation="ontop"',
     "S-FIXTURE", "a relation value the schema does not have"),
    ("R40.5-2.yaml", "R40.5-2.yaml", "{start: 4000, end: 10000, layout: overlay-lower-third", "{start: 3900, end: 10000, layout: overlay-lower-third",
     "S-TIME", "two overlapping presentation segments"),
    ("R40.6.yaml", "R40.6.yaml", "url: https://aps.example.com/beh/r40-6/alt\n    class: publisher-mpd", "url: https://aps.example.com/beh/r40-6/alt\n    class: overlay-list",
     "S-FIXTURE", "the alternative MPD declared as a non-linear document"),
    ("R40.9-1.yaml", "R40.9-1.yaml", "layout: pause-fullscreen, shows", "layout: pause, shows",
     "S-LAYOUT", "the bare `pause`, which is not a token"),
    ("R40.9-2.yaml", "fixtures/R40.9/overlay-s.xml", 'family="overlay"', 'family="pause"',
     "S-FIXTURE", "an overlay window resolved by a pause-family document"),
    ("R40.9-3.yaml", "R40.9-3.yaml", "status: 500}", "status: 700}",
     "B-SCHEMA", "an HTTP status out of range"),
]

for test, path, old, new, check, what in M:
    p = os.path.join(B, path)
    if old is None and new is None:
        os.remove(p)
        continue
    text = open(p).read()
    if path.endswith("overlay.xml") and test == "R22.1.yaml":
        # drop @duration from the first option
        n = re.sub(r'\n\s*duration="PT4S"', "", text, count=1)
        assert n != text, test
        open(p, "w").write(n)
        continue
    assert text.count(old) >= 1, (test, old)
    open(p, "w").write(text.replace(old, new, 1))

r = subprocess.run([sys.executable, os.path.join(REPO, "bin/check-behaviour.py"), "--source", SRC],
                   capture_output=True, text=True, cwd=REPO)
out = r.stdout + r.stderr
open(os.path.join(WORK, "mutation.out"), "w").write(out)
print(f"exit {r.returncode}")
caught = 0
for test, path, old, new, check, what in M:
    lines = [l for l in out.splitlines() if "\t" in l and l.split("\t")[1] == test and not l.split("\t")[1:2] == []
             and "NOT_VERIFIABLE" not in l]
    hit = [l for l in lines if l.startswith(check)]
    ok = bool(hit)
    caught += ok
    print(f"{'CAUGHT' if ok else 'MISSED'}  {test:14} expect {check:9} ({what})")
    for l in (hit or lines)[:2]:
        print(f"        {l[:220]}")
print(f"{caught}/{len(M)} caught")

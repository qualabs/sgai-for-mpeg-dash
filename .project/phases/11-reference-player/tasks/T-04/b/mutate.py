"""Mutation campaign for T-04 part B: one deliberate break per test, run
check-behaviour.py on a copy of spec-source, report whether a finding names
the broken file. Usage: python3 mutate.py <project root> <work dir>"""
import shutil
import subprocess
import sys
from pathlib import Path

root, work = Path(sys.argv[1]), Path(sys.argv[2])
ss = work / "ss"
if ss.exists():
    shutil.rmtree(ss)
shutil.copytree(root / "spec-source", ss)

B = "behaviour/"
F = "behaviour/fixtures/"
# (test it belongs to, file, old, new, what the break is, expectation: a check name or GREEN)
M = [
    ("R2.3", B + "R2.3.yaml", "index: 2}, option: {index: 1}, layout: overlay-corner", "index: 3}, option: {index: 1}, layout: overlay-corner", "expected candidate 3, which the document lacks", "S-REF"),
    ("R2.3", F + "R2.3/overlay-list.xml", 'layout="overlay-corner"', 'layout="overlay-corners"', "fixture: a layout outside the token enumeration", "S-FIXTURE"),
    ("R2.3", B + "R2.3.yaml", "index: 2}, option: {index: 1}, layout: overlay-corner", "index: 1}, option: {index: 1}, layout: overlay-corner", "BEHAVIOURAL: expects the non-admitted candidate 1", "GREEN"),
    ("R5.3", B + "R5.3.yaml", "imp?cr=532\"}\n  D5", "imp?cr=533\"}\n  D5", "beacon URL not the event's text", "S-REF"),
    ("R5.3", B + "R5.3.yaml", "{start: 10000, end: 17000, layout: none, shows: [{element: primary, from: 10000}]}", "{start: 11000, end: 17000, layout: none, shows: [{element: primary, from: 10000}]}", "D4 presentation leaves a gap", "S-TIME"),
    ("R5.6-1", B + "R5.6-1.yaml", "option: {index: 3}, layout", "option: {index: 4}, layout", "D4 expects option 4, which does not exist", "S-REF"),
    ("R5.6-1", F + "R5.6/cr561v.mpd", 'duration="PT5S"', 'duration="PT5X"', "fixture: sub-MPD duration not an xs:duration", "S-FIXTURE"),
    ("R5.6-1", B + "R5.6-1.yaml", "option: {index: 3}, layout", "option: {index: 1}, layout", "BEHAVIOURAL: D4 expected to render the video option", "GREEN"),
    ("R5.6-2", B + "R5.6-2.yaml", "query: {sgai-allowed-layouts: overlay-corner}", "query: {sgai-allowed-layout: overlay-corner}", "query names a parameter that is no slot parameter", "S-REF"),
    ("R5.6-3", B + "R5.6-3.yaml", "option: {index: 2}, layout: overlay-corner", "option: {index: 2}, layout: corner", "layout not an R12.2 token", "S-LAYOUT"),
    ("R5.9", B + "R5.9.yaml", "status: 404}", "status: 99}", "aps status below 100", "B-SCHEMA"),
    ("R5.9", B + "R5.9.yaml", "option: {index: 2}, layout", "option: {index: 1}, layout", "BEHAVIOURAL: expects the failed option 1", "GREEN"),
    ("R29.2", B + "R29.2.yaml", "query: {sgai-allowed-layouts: overlay-corner}", "query: {sgai-allowed-layouts: overlay-corner, sgai-video-decoders: \"2\"}", "a capability parameter not in sends_capabilities", "S-REF"),
    ("R29.2", B + "R29.2.yaml", "query: {sgai-allowed-layouts: overlay-corner}", "query: {sgai-allowed-layouts: overlay-corner, sgai-custom-region: 0 0 10 10}", "BEHAVIOURAL: window 2 expected to send a region it does not declare", "GREEN"),
    ("R29.4", B + "R29.4.yaml", "query: {sgai-allowed-layouts: overlay-corner}", "query: {sgai-allowed-layouts: overlay-corner, model: tv1}", "query expects an unprefixed Player parameter", "S-REF"),
    ("R32.1-1", F + "R32.1/repeat.xml", 'onExhausted="repeat"', 'onExhausted="again"', "fixture: onExhausted outside its enumeration", "S-FIXTURE"),
    ("R32.1-2", F + "R32.1/second.xml", '\n                  onExhausted="stop"', "", "fixture: pause document without onExhausted (the 'declares none' case)", "S-FIXTURE"),
    ("R32.1-3", B + "R32.1-3.yaml", "{start: 5000, end: 8000, layout: none", "{start: 5000, end: 7000, layout: none", "presentation leaves a gap", "S-TIME"),
    ("R32.2", B + "R32.2.yaml", "nth: 2,", "nth: 0,", "aps nth below 1", "B-SCHEMA"),
    ("R32.2", B + "R32.2.yaml", "{start: 5000, end: 12000, layout: none", "{start: 5000, end: 8000, layout: pause-fullscreen, shows: [{element: ad, candidate: *c, option: {index: 1}}]}\n      - {start: 8000, end: 12000, layout: none", "BEHAVIOURAL: the empty document read as request-again, candidate shown again", "GREEN"),
    ("R34.1", F + "R34.1/main.mpd", 'executeOnce="true"', 'executeOnce="yes"', "fixture: executeOnce not an xs:boolean", "S-FIXTURE"),
    ("R34.3", B + "R34.3.yaml", "criterion_sha256: 778da27c", "criterion_sha256: 000da27c", "stale criterion hash", "B-HASH"),
    ("R34.6", B + "R34.6.yaml", "do: seek, to: 3000}", "do: seek}", "seek without `to`", "B-SCHEMA"),
    ("R34.9", B + "R34.9.yaml", "{at: 10000, fixture: behaviour/fixtures/R34.9", "{at: 20000, fixture: behaviour/fixtures/R34.9", "beacon after observe_until", "S-TIME"),
    ("R34.9", B + "R34.9.yaml", "{start: 0, end: 10000, layout: overlay-lower-third", "{start: 0, end: 5000, layout: overlay-lower-third", "BEHAVIOURAL (partial): A cut to 5 s leaves a gap", "S-TIME"),
    ("R34.10", B + "R34.10.yaml", "delay: 7000}", "delay: -1}", "negative aps delay", "B-SCHEMA"),
    ("R36.1-1", B + "R36.1-1.yaml", "{at: {from: 7000, to: 10000}", "{at: {from: 11000, to: 10000}", "request window from > to", "S-TIME"),
    ("R36.1-1", B + "R36.1-1.yaml", "{at: {from: 7000, to: 10000}", "{at: {from: 0, to: 10000}", "BEHAVIOURAL: request allowed before the offset", "GREEN"),
    ("R36.1-2", F + "R36.1/main-zero.mpd", 'earliestResolutionTimeOffset="0"', 'earliestResolutionTimeOffset="-1"', "fixture: negative offset", "S-FIXTURE"),
    ("R36.1-3", B + "R36.1-3.yaml", "actions: [{at: 2000, do: seek", "actions: [{at: 20000, do: seek", "action after observe_until", "S-TIME"),
    ("R36.5-1", F + "R36.5/second.xml", 'validFor="PT10M"', 'validFor="ten minutes"', "fixture: validFor not an xs:duration", "S-FIXTURE"),
    ("R36.5-2", B + "R36.5-2.yaml", 'event_id: "1"}', 'event_id: "2"}', "opportunity names an Event the MPD lacks", "S-REF"),
    ("R38.2", B + "R38.2.yaml", "status: 200, document: behaviour/fixtures/R38.2/empty.xml}", "status: 200, document: behaviour/fixtures/R38.2/none.xml}", "aps serves a document that is not a fixture", "S-FIXTURE"),
    ("R38.2", B + "R38.2.yaml", "sgai-allowed-layouts: overlay-corner squeezeback-double-box overlay-lower-third}", "sgai-allowed-layouts: overlay-corner overlay-lower-third squeezeback-double-box}", "BEHAVIOURAL: expects the set reordered", "GREEN"),
    ("R39.3", F + "R39.3/main.mpd", 'customRegion="60 5 35 30"', 'customRegion="60 5 35"', "fixture: region with three numbers", "S-FIXTURE"),
    ("R39.5-1", B + "R39.5-1.yaml", "ad: {x: 60, y: 60, width: 40, height: 40}", "ad: {x: 70, y: 60, width: 40, height: 40}", "geometry past the viewport", "S-GEOM"),
    ("R39.5-1", F + "R39.5/region.xml", 'rect="45 60 20 20"', 'rect="45 60 60 20"', "fixture: rectangle past the viewport (R39.4b)", "S-FIXTURE"),
    ("R39.5-1", B + "R39.5-1.yaml", "ad: {x: 60, y: 60, width: 40, height: 40}", "ad: {x: 45, y: 60, width: 20, height: 20}", "BEHAVIOURAL: expects option 1's rectangle", "GREEN"),
    ("R39.5-2", B + "R39.5-2.yaml", "{at: 7500, ad:", "{at: 11000, ad:", "geometry at an instant with no ad on screen", "S-GEOM"),
]

cmd = [sys.executable, str(root / "bin/check-behaviour.py"), "--source", str(ss), "--context", str(root / "context")]
base = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
mine = {Path(m[1]).name for m in M if m[1].startswith(B) and "/fixtures/" not in m[1]}
base_find = [l for l in base.stdout.splitlines() if "\t" in l and any(n in l.split("\t")[1] for n in mine) and "NOT_VERIFIABLE" not in l]
print(f"baseline exit {base.returncode}; findings naming the tests broken below: {len(base_find)}")
bad = 0
for test, rel, old, new, what, want in M:
    p = ss / rel
    orig = p.read_text(encoding="utf-8")
    if old not in orig:
        print(f"!! {test}: pattern not found in {rel}")
        bad += 1
        continue
    p.write_text(orig.replace(old, new, 1), encoding="utf-8")
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=root)
    p.write_text(orig, encoding="utf-8")
    name = f"{test}.yaml"
    hits = [l for l in r.stdout.splitlines() if "\t" in l and l.split("\t")[1] == name and "NOT_VERIFIABLE" not in l]
    got = sorted({h.split("\t")[0] for h in hits}) or ["GREEN"]
    ok = want in got
    bad += not ok
    print(f"{'ok ' if ok else 'XX '} {test:8} exit={r.returncode} want={want:9} got={','.join(got):20} {what}")
    for h in hits[:2]:
        print(f"      {h[:200]}")
print(f"{len(M)} mutations, {bad} not as expected")

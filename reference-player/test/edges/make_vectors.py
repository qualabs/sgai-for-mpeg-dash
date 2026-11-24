"""Writes T-05's edge vectors (E*.yaml): the linear rules no test of
spec-source/behaviour/ reaches on its own. Each expected value is computed
here from Table 57 of ISO/IEC 23009-1 6th ed., by hand in the comment, not by
the reference. Their own documents are in fixtures/ beside them (the harness
reads a fixture path from spec-source/, else from the vector's directory);
the ones they borrow are spec-source/'s. Run them with run-edges.py.

    python3 make_vectors.py      # rewrites E*.yaml here"""
from pathlib import Path
import yaml

HERE = Path(__file__).parent
F = "fixtures/"   # this folder's fixtures/, read beside the vector
R48 = "behaviour/fixtures/R4.8/"
CAPS = {"D1": {"sgai-video-decoders": 2, "sgai-image-over-video": 1, "sgai-html-over-video": 1,
               "sgai-custom-layout": 0, "sgai-ad-audio": 0}}


def prim(start, end, frm, note=None):
    s = {"start": start, "end": end, "layout": "none", "shows": [{"element": "primary", "from": frm}]}
    if note:
        s["note"] = note
    return s


def ad(start, end, fixture, cid):
    return {"start": start, "end": end, "layout": "linear",
            "shows": [{"element": "ad", "candidate": {"fixture": fixture, "id": cid}, "option": None}]}


def sel(main, cands):
    return [{"opportunity": {"fixture": main, "event_id": "1"}, "result": "presented",
             "presented": [{"candidate": {"fixture": f, "id": c}, "option": None, "layout": "linear"} for f, c in cands]}]


def vector(name, doc, *, entry, fixtures, play_from, observe, summary, requests, selection, presentation,
           beacons, actions=(), aps=None, not_compared=None):
    v = {"format": "sgai-scenario/1", "timescale": 1000, "tolerance": 250, "play_from": play_from,
         "observe_until": observe, "entry": entry, "fixtures": fixtures, "player_capabilities": CAPS,
         "sends_capabilities": [], "actions": list(actions)}
    if aps:
        v["aps"] = aps
    out = {"summary": summary, "requests": requests, "selection": selection,
           "presentation": presentation, "beacons": beacons}
    if not_compared:
        out["requests_not_compared"] = not_compared
    v["outcomes"] = {"D1": out}
    (HERE / f"{name}.yaml").write_text("# " + doc.strip().replace("\n", "\n# ") + "\n"
                                       + yaml.safe_dump(v, sort_keys=False, width=120), encoding="utf-8")


REP = F + "rep.mpd"
REP_URL = "https://aps.example.com/t05/rep"


def rep_fix(main):
    return [{"path": F + main}, {"path": REP, "url": REP_URL}]


def b(at, i, label, fixture=REP, name="rep"):
    return {"at": at, "fixture": fixture, "id": str(i), "url": f"https://t.example.com/t05/{name}/{label}"}


vector("E1-execute-once-after-success", """
@executeOnce="true" after a successful execution (§5.16.5: "the event is executed only the
first time this media time is traversed"). R4.8's documents; the viewer seeks back to 0 at
11 s, so PRT (2 s) is traversed again at 13 s and the event must not run again.""",
       entry=R48 + "main.mpd", fixtures=[{"path": R48 + "main.mpd"}, {"path": R48 + "alt.mpd", "url": "https://aps.example.com/b/r4-8/break"}],
       play_from=0, observe=15000, actions=[{"at": 11000, "do": "seek", "to": 0}],
       summary="the 8 s alternative once; after the seek back the programme plays through PRT",
       requests=[{"at": {"from": 0, "to": 2000}, "url": "https://aps.example.com/b/r4-8/break", "answered_by": R48 + "alt.mpd"}],
       selection=sel(R48 + "main.mpd", [(R48 + "alt.mpd", "alt")]),
       presentation=[prim(0, 2000, 0), ad(2000, 10000, R48 + "alt.mpd", "alt"), prim(10000, 11000, 2000),
                     prim(11000, 15000, 0, "after the seek back to 0")],
       beacons=[{"at": 2000, "fixture": R48 + "alt.mpd", "id": "1", "url": "https://t.example.com/r4-8/start"},
                {"at": 10000, "fixture": R48 + "alt.mpd", "id": "2", "url": "https://t.example.com/r4-8/end"}])

INS = F + "ins.mpd"
vector("E2-insert-reexecuted-after-seek", """
An insertion without @executeOnce (default "false") is executed again when a seek moves the
playhead before EAP (§5.16.2.2.1), and is not executed again at its own return, RT = PRTA
(A.14.5 pops it and does not reset QE; the T-01 reading). PRT 2 s, EAP 3 s, a 4 s
alternative; seek to 0 at 8 s.""",
       entry=F + "ins-many-main.mpd", fixtures=[{"path": F + "ins-many-main.mpd"}, {"path": INS, "url": "https://aps.example.com/t05/ins-many"}],
       play_from=0, observe=15000, actions=[{"at": 8000, "do": "seek", "to": 0}],
       summary="the alternative at 2 s, the programme from 2 s, the seek, the alternative again at 10 s",
       requests=[{"at": {"from": 0, "to": 2000}, "url": "https://aps.example.com/t05/ins-many", "answered_by": INS},
                 {"at": {"from": 8000, "to": 10000}, "url": "https://aps.example.com/t05/ins-many", "answered_by": INS}],
       # two executions of one opportunity: two entries, one presentation each
       selection=sel(F + "ins-many-main.mpd", [(INS, "ins")]) + sel(F + "ins-many-main.mpd", [(INS, "ins")]),
       presentation=[prim(0, 2000, 0), ad(2000, 6000, INS, "ins"), prim(6000, 8000, 2000),
                     prim(8000, 10000, 0, "after the seek back to 0"), ad(10000, 14000, INS, "ins"), prim(14000, 15000, 2000)],
       beacons=[b(2000, 1, "imp", INS, "ins"), b(10000, 1, "imp", INS, "ins")])

vector("E3-replace-late-clip", """
Delayed replacement with @clip absent (true). Join at 4 s; PRT 2 s, APDmax 6 s, APD 8 s.
Table 57: APDadj = max(6 - 4 + 2, 0) = 4; ASO = 0; APDA = min(8 - 0, 4) = 4; RT = PRT + APDA = 6.""",
       entry=F + "rep-clip-main.mpd", fixtures=rep_fix("rep-clip-main.mpd"), play_from=4000, observe=7000,
       summary="the alternative for 4 s from its start, then the programme from 6 s",
       requests=[{"at": 0, "url": REP_URL, "answered_by": REP}],
       selection=sel(F + "rep-clip-main.mpd", [(REP, "rep")]),
       presentation=[ad(0, 4000, REP, "rep"), prim(4000, 7000, 6000)],
       beacons=[b(0, 1, "b0"), b(2000, 2, "b2")])

vector("E4-replace-late-noclip", """
Delayed replacement with @clip="false". Join at 4 s; PRT 2 s, APDmax 6 s, APD 8 s.
Table 57: APDadj = APDmax = 6; APDA = min(8, 6) = 6; RT = PRTA + APDA = 4 + 6 = 10.""",
       entry=F + "rep-noclip-main.mpd", fixtures=rep_fix("rep-noclip-main.mpd"), play_from=4000, observe=8000,
       summary="the alternative for 6 s, then the programme from 10 s",
       requests=[{"at": 0, "url": REP_URL, "answered_by": REP}],
       selection=sel(F + "rep-noclip-main.mpd", [(REP, "rep")]),
       presentation=[ad(0, 6000, REP, "rep"), prim(6000, 8000, 10000)],
       beacons=[b(0, 1, "b0"), b(2000, 2, "b2"), b(5000, 3, "b5")])

vector("E5-replace-start-with-offset", """
Delayed replacement with @startWithOffset="true". Join at 4 s; PRT 2 s, APDmax 6 s, APD 8 s.
Table 57: ASO = PRTA - PRT = 2; APDadj = max(6 - 4 + 2, 0) = 4; APDA = min(8 - 2, 4) = 4;
RT = PRT + APDA = 6. The alternative starts at its 2 s: its callback at 0 is not played,
the one at 2 s fires at once and the one at 5 s after 3 s.""",
       entry=F + "rep-swo-main.mpd", fixtures=rep_fix("rep-swo-main.mpd"), play_from=4000, observe=6000,
       summary="the alternative from its 2nd second for 4 s, then the programme from 6 s",
       requests=[{"at": 0, "url": REP_URL, "answered_by": REP}],
       selection=sel(F + "rep-swo-main.mpd", [(REP, "rep")]),
       presentation=[ad(0, 4000, REP, "rep"), prim(4000, 6000, 6000)],
       beacons=[b(0, 2, "b2"), b(3000, 3, "b5")])

vector("E6-replace-return-offset", """
Replacement with @returnOffset 9 s, APDmax 4 s, executed at PRT 2 s. Table 57: APDA =
min(8, 4) = 4; RT = PRT + RO = 11.""",
       entry=F + "rep-ro-main.mpd", fixtures=rep_fix("rep-ro-main.mpd"), play_from=0, observe=8000,
       summary="the programme, the alternative 2-6 s, then the programme from 11 s",
       requests=[{"at": {"from": 0, "to": 2000}, "url": REP_URL, "answered_by": REP}],
       selection=sel(F + "rep-ro-main.mpd", [(REP, "rep")]),
       presentation=[prim(0, 2000, 0), ad(2000, 6000, REP, "rep"), prim(6000, 8000, 11000)],
       beacons=[b(2000, 1, "b0"), b(4000, 2, "b2")])

vector("E7-replace-apda-zero", """
A replacement whose clip-adjusted duration is zero is not executed (§5.16.2.2.1 step 3, "If at
time PRTA the duration APDA is determined to be 0, the event is not executed"). Join at 6 s;
PRT 2 s, APDmax 3 s: APDadj = max(3 - 6 + 2, 0) = 0.""",
       entry=F + "rep-zero-main.mpd", fixtures=rep_fix("rep-zero-main.mpd"), play_from=6000, observe=4000,
       summary="the programme from 6 s, nothing else",
       requests=[], not_compared="A.14.5 resolves the event before it checks APDA; the base does not bind whether a zero APDA is found before the request",
       selection=[], presentation=[prim(0, 4000, 6000)], beacons=[])

LIST = F + "list-hole.mpd"
vector("E8-list-linked-period-fails", """
A List MPD whose second Linked Period does not resolve (404). §5.3.2.6.3 step 2: the Linked
Period has no content of its own, so it is removed, and the third follows the first. Lazy
resolution: lb from PeriodStart 4 - 2 = 2 s of the alternative (session 4 s); after lb is
removed lc's PeriodStart is 4, so it is eligible at once (4 - 4 = 0).""",
       entry=F + "list-hole-main.mpd",
       fixtures=[{"path": F + "list-hole-main.mpd"}, {"path": LIST, "url": "https://aps.example.com/t05/list-hole"},
                 {"path": F + "la.mpd", "url": "https://ads-cdn.example.com/t05/la.mpd"},
                 {"path": F + "lc.mpd", "url": "https://ads-cdn.example.com/t05/lc.mpd"}],
       aps=[{"url": "https://ads-cdn.example.com/t05/lb.mpd", "status": 404}],
       play_from=0, observe=11000,
       summary="la 2-6 s, lc 6-10 s, then the programme from 2 s",
       requests=[{"at": {"from": 0, "to": 2000}, "url": "https://aps.example.com/t05/list-hole", "answered_by": LIST},
                 {"at": {"from": 0, "to": 2000}, "url": "https://ads-cdn.example.com/t05/la.mpd", "answered_by": F + "la.mpd"},
                 {"at": 4000, "url": "https://ads-cdn.example.com/t05/lb.mpd"},
                 {"at": {"from": 4000, "to": 6000}, "url": "https://ads-cdn.example.com/t05/lc.mpd", "answered_by": F + "lc.mpd"}],
       selection=sel(F + "list-hole-main.mpd", [(LIST, "la"), (LIST, "lc")]),
       presentation=[prim(0, 2000, 0), ad(2000, 6000, LIST, "la"), ad(6000, 10000, LIST, "lc"), prim(10000, 11000, 2000)],
       beacons=[b(2000, 1, "imp", F + "la.mpd", "la"), b(6000, 2, "imp", F + "lc.mpd", "lc")])

vector("E9-insert-late-join", """
Delayed insertion: join at 2.5 s inside the active interval [2, 3] s of R4.8's event. PRTA =
2.5; Table 57, RT of an insertion "is always PRTA" = 2.5 (not PRT).""",
       entry=R48 + "main.mpd", fixtures=[{"path": R48 + "main.mpd"}, {"path": R48 + "alt.mpd", "url": "https://aps.example.com/b/r4-8/break"}],
       play_from=2500, observe=10000,
       summary="the 8 s alternative from the start, then the programme from 2.5 s",
       requests=[{"at": 0, "url": "https://aps.example.com/b/r4-8/break", "answered_by": R48 + "alt.mpd"}],
       selection=sel(R48 + "main.mpd", [(R48 + "alt.mpd", "alt")]),
       presentation=[ad(0, 8000, R48 + "alt.mpd", "alt"), prim(8000, 10000, 2500)],
       beacons=[{"at": 0, "fixture": R48 + "alt.mpd", "id": "1", "url": "https://t.example.com/r4-8/start"},
                {"at": 8000, "fixture": R48 + "alt.mpd", "id": "2", "url": "https://t.example.com/r4-8/end"}])

vector("E10-join-after-eap", """
A join after the end of the active interval: R4.8's event is active over [2, 3] s; playback
starts at 4 s. §5.16.2.2.3: only events with PRT ≤ PHP ≤ EAP or PHP < PRT enter QE, so it
is never resolved nor executed.""",
       entry=R48 + "main.mpd", fixtures=[{"path": R48 + "main.mpd"}, {"path": R48 + "alt.mpd", "url": "https://aps.example.com/b/r4-8/break"}],
       play_from=4000, observe=4000,
       summary="the programme from 4 s, nothing else",
       requests=[], selection=[], presentation=[prim(0, 4000, 4000)], beacons=[])

REP_END = F + "rep-end.mpd"
vector("E12-replace-end-callback-on-time", """
A replacement executed on time, whose callback sits at the alternative's own end. PRT 2 s,
APDmax 6 s = APD 6 s, @clip absent (true). A Player executes at the first instant it sees
PHP >= PRT, so PRTA = PRT + d with d a fraction of a frame; Table 57 then gives APDadj =
6 - d, APDA = min(6 - 0, 6 - d) = 6 - d, RT = PRT + APDA = 8 - d. A cut no longer than
the lag of an execution on time is the alternative's end, so its callback at 6 s (session
8 s) fires; d is below the vector's tolerance everywhere else.""",
       entry=F + "rep-end-main.mpd",
       fixtures=[{"path": F + "rep-end-main.mpd"}, {"path": REP_END, "url": "https://aps.example.com/t05/rep-end"}],
       play_from=0, observe=10000,
       summary="the programme, the 6 s alternative 2-8 s with both its callbacks, then the programme from 8 s",
       requests=[{"at": {"from": 0, "to": 2000}, "url": "https://aps.example.com/t05/rep-end", "answered_by": REP_END}],
       selection=sel(F + "rep-end-main.mpd", [(REP_END, "rep-end")]),
       presentation=[prim(0, 2000, 0), ad(2000, 8000, REP_END, "rep-end"), prim(8000, 10000, 8000)],
       beacons=[b(2000, 1, "start", REP_END, "rep-end"), b(8000, 2, "complete", REP_END, "rep-end")])

vector("E13-replace-late-join-no-end-callback", """
E12's documents joined late: playback starts at 4 s, inside the active interval [2, 12] s.
Table 57: PRTA = 4, APDadj = max(6 - 4 + 2, 0) = 4, APDA = min(6 - 0, 4) = 4, RT = PRT + APDA
= 6. The cut (2 s) equals PRTA - PRT, but nothing played the primary up to PRT: the
alternative was shown for 4 s of its 6, and its callback at 6 s is not reached.""",
       entry=F + "rep-end-main.mpd",
       fixtures=[{"path": F + "rep-end-main.mpd"}, {"path": REP_END, "url": "https://aps.example.com/t05/rep-end"}],
       play_from=4000, observe=7000,
       summary="the alternative for 4 s from its start, without its end callback, then the programme from 6 s",
       requests=[{"at": 0, "url": "https://aps.example.com/t05/rep-end", "answered_by": REP_END}],
       selection=sel(F + "rep-end-main.mpd", [(REP_END, "rep-end")]),
       presentation=[ad(0, 4000, REP_END, "rep-end"), prim(4000, 7000, 6000)],
       beacons=[b(0, 1, "start", REP_END, "rep-end")])

vector("E11-pause-during-linear-ad", """
The viewer pauses during a linear alternative and resumes 2 s later, with no pause window:
the linear ad is suspended and resumed where it was (the linear part of R17.5; the primary
is already stopped by the insertion). R4.8's 8 s alternative from 2 s, paused 4-6 s: it
ends at 12 s, and its end callback (at 8 s of its own timeline) fires then.""",
       entry=R48 + "main.mpd", fixtures=[{"path": R48 + "main.mpd"}, {"path": R48 + "alt.mpd", "url": "https://aps.example.com/b/r4-8/break"}],
       play_from=0, observe=14000, actions=[{"at": 4000, "do": "pause"}, {"at": 6000, "do": "resume"}],
       summary="the alternative 2-12 s, paused 4-6 s, then the programme from 2 s",
       requests=[{"at": {"from": 0, "to": 2000}, "url": "https://aps.example.com/b/r4-8/break", "answered_by": R48 + "alt.mpd"}],
       selection=sel(R48 + "main.mpd", [(R48 + "alt.mpd", "alt")]),
       presentation=[prim(0, 2000, 0), ad(2000, 12000, R48 + "alt.mpd", "alt"), prim(12000, 14000, 2000)],
       beacons=[{"at": 2000, "fixture": R48 + "alt.mpd", "id": "1", "url": "https://t.example.com/r4-8/start"},
                {"at": 12000, "fixture": R48 + "alt.mpd", "id": "2", "url": "https://t.example.com/r4-8/end"}])

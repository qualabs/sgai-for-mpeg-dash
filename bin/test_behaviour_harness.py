#!/usr/bin/env python3
"""Tests for the behaviour battery's harness (phase 11, T-09), without
Chromium: the session clock (bin/players/adapters/sgai-clock.js, run under
node), its mapping in the comparison, the attribution of a document served
twice at one URL, the selection as ordered sequences, which `aps` answers are
document requests, which URLs the runner fetches from the content server, a
fixture kept beside its vector, the UTC time a live entry is joined at, the
capabilities a job discloses, and the content server's silence when a Player
drops a connection.

None of them runs the battery (ADR 0087): no `run`, `drive` or `main` of
conformance.behaviour, no runner. The clock tests need node (skipped, saying
so, without it).

Run: python3 bin/test_behaviour_harness.py   (re-runs itself under uv for
PyYAML; a few seconds)
"""
import contextlib
import copy
import io
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parent
ROOT = BIN.parent
sys.path.insert(0, str(BIN))

if __name__ == "__main__":
    from conformance.deps import ensure_yaml
    ensure_yaml(os.path.abspath(__file__), sys.argv[1:])

from conformance import behaviour, players  # noqa: E402
from conformance.behaviour_compare import (Fixtures, Observed, attribute, compare_presentation,  # noqa: E402
                                           compare_selection, normalise, session_map)
from conformance.model import Outcome  # noqa: E402

CLOCK_JS = BIN / "players" / "adapters" / "sgai-clock.js"
SOURCE = ROOT / "spec-source"
T0 = 1_700_000_000_000


# --------------------------------------------------------------------------- the clock, in node

def run_clock(mode: str, ticks: list) -> list:
    """Feeds `ticks` ([wall ms, state]) to a SessionClock started at the
    first; returns the session time after each."""
    # run as the page runs it: a classic script that sets SGAI_CLOCK on the global
    script = (f"require('vm').runInThisContext(require('fs').readFileSync({json.dumps(str(CLOCK_JS))}, 'utf8'));"
              "const C = globalThis.SGAI_CLOCK;"
              "const inp = JSON.parse(require('fs').readFileSync(0, 'utf8'));"
              "const c = new C.SessionClock(inp.mode);"
              "c.start(inp.ticks[0][0], inp.ticks[0][1]);"
              "const out = [0];"
              "for (const [w, s] of inp.ticks.slice(1)) out.push(c.tick(w, s));"
              "process.stdout.write(JSON.stringify(out));")
    p = subprocess.run(["node", "-e", script], input=json.dumps({"mode": mode, "ticks": ticks}),
                       capture_output=True, text=True, timeout=30)
    if p.returncode != 0:
        raise AssertionError(p.stderr)
    return [round(x, 6) for x in json.loads(p.stdout)]


def vid(role, t, shown=True, paused=False, rate=1, id_=None, seeks=0):
    return {"id": id_ or (1 if role == "primary" else 2), "role": role, "shown": shown, "paused": paused,
            "time": t, "rate": rate, "seeks": seeks}


@unittest.skipUnless(shutil.which("node"), "node is not installed")
class Clock(unittest.TestCase):
    def test_primary_at_half_speed(self):
        # 1 s of wall per 0.5 s of media: the clock follows the media.
        ticks = [[1000 + i * 1000, {"viewerPaused": False, "videos": [vid("primary", i * 0.5)]}] for i in range(5)]
        self.assertEqual(run_clock("presentation", ticks), [0, 500, 1000, 1500, 2000])
        self.assertEqual(run_clock("wall", ticks), [0, 1000, 2000, 3000, 4000])

    def test_stall_stands_still(self):
        ticks = [[0, {"videos": [vid("primary", 3.0)]}], [400, {"videos": [vid("primary", 3.0)]}]]
        self.assertEqual(run_clock("presentation", ticks), [0, 0])

    def test_viewer_pause_is_wall(self):
        # a pause: the primary is paused and stands still; the clock runs on wall
        ticks = [[0, {"viewerPaused": False, "videos": [vid("primary", 2.0)]}],
                 [100, {"viewerPaused": True, "videos": [vid("primary", 2.05, paused=True)]}],
                 [3100, {"viewerPaused": True, "videos": [vid("primary", 2.05, paused=True)]}],
                 [3600, {"viewerPaused": False, "videos": [vid("primary", 2.30)]}]]
        self.assertEqual(run_clock("presentation", ticks), [0, 100, 3100, 3350])

    def test_viewer_pause_with_a_playing_video_is_wall(self):
        # a pause ad that is a video, playing at half speed over the hidden
        # primary: the viewer has paused, so wall time, not the ad's media time
        state = lambda t: {"viewerPaused": True, "videos": [vid("primary", 2, shown=False, paused=True),  # noqa: E731
                                                            vid("ad", t)]}
        ticks = [[0, state(0)], [1000, state(0.5)], [2000, state(1.0)]]
        self.assertEqual(run_clock("presentation", ticks), [0, 1000, 2000])

    def test_linear_ad_drives_while_primary_hidden(self):
        # the primary hidden (and still advancing underneath, as a replacement
        # may): the ad's media time drives, not the primary's
        ticks = [[0, {"videos": [vid("primary", 10, shown=False), vid("ad", 0)]}],
                 [1000, {"videos": [vid("primary", 11, shown=False), vid("ad", 0.4)]}],
                 [2000, {"videos": [vid("primary", 12, shown=False), vid("ad", 0.9)]}]]
        self.assertEqual(run_clock("presentation", ticks), [0, 400, 900])

    def test_overlay_video_does_not_drive(self):
        # an overlay <video> over a playing primary: the primary drives
        ticks = [[0, {"videos": [vid("primary", 5), vid("ad", 0)]}],
                 [1000, {"videos": [vid("primary", 5.5), vid("ad", 0.9)]}]]
        self.assertEqual(run_clock("presentation", ticks), [0, 500])

    def test_image_takeover_is_wall(self):
        ticks = [[0, {"videos": [vid("primary", 5, shown=False)]}],
                 [700, {"videos": [vid("primary", 5, shown=False)]}]]
        self.assertEqual(run_clock("presentation", ticks), [0, 700])

    def test_jump_counts_nothing(self):
        # a seek forward (counted by `seeks`) and one that is not counted but
        # is larger than the wall time allows: neither is presentation
        ticks = [[0, {"videos": [vid("primary", 2)]}],
                 [100, {"videos": [vid("primary", 40, seeks=1)]}],
                 [200, {"videos": [vid("primary", 40.1, seeks=1)]}],
                 [300, {"videos": [vid("primary", 90, seeks=1)]}],
                 [400, {"videos": [vid("primary", 89.0, seeks=1)]}]]
        self.assertEqual(run_clock("presentation", ticks), [0, 0, 100, 100, 100])

    def test_small_seek_counts_nothing(self):
        # a seek of 250 ms in 100 ms is within the bound: only the seek
        # counter tells it from playback
        ticks = [[0, {"videos": [vid("primary", 2)]}], [100, {"videos": [vid("primary", 2.25, seeks=1)]}]]
        self.assertEqual(run_clock("presentation", ticks), [0, 0])
        ticks[1][1]["videos"][0]["seeks"] = 0
        self.assertEqual(run_clock("presentation", ticks), [0, 250])

    def test_jump_threshold(self):
        # exactly at the bound (1.5 x 100 + 200 = 350 ms) counts; past it, not
        at = [[0, {"videos": [vid("primary", 0)]}], [100, {"videos": [vid("primary", 0.35)]}]]
        past = [[0, {"videos": [vid("primary", 0)]}], [100, {"videos": [vid("primary", 0.3501)]}]]
        self.assertEqual(run_clock("presentation", at)[1], 350)
        self.assertEqual(run_clock("presentation", past)[1], 0)

    def test_resume_jump_is_not_presentation(self):
        # Chromium after play(): currentTime 60 ms ahead 2 ms after the
        # resume (T-09 runs: 40-70 ms in 2-6 ms, at almost every resume)
        p = lambda t, paused=False: {"viewerPaused": paused, "videos": [vid("primary", t, paused=paused)]}  # noqa: E731
        ticks = [[0, p(3.0)], [100, p(3.0, True)], [3100, p(3.0, True)], [3102, p(3.0)], [3104, p(3.060)],
                 [3204, p(3.160)], [3304, p(3.260)]]
        # the resume tick reads the old time (0); the 60 ms jump counts the 2 ms of wall
        self.assertEqual(run_clock("presentation", ticks), [0, 100, 3100, 3100, 3102, 3202, 3302])

    def test_settle_window_edge(self):
        # within SETTLE_MS (100) of the switch the cap holds, past it media counts
        p = lambda t, paused=False: {"viewerPaused": paused, "videos": [vid("primary", t, paused=paused)]}  # noqa: E731
        ticks = [[0, p(1.0, True)], [10, p(1.0)], [110, p(1.150)], [111, p(1.170)]]
        self.assertEqual(run_clock("presentation", ticks), [0, 0, 100, 120])

    def test_rate(self):
        ticks = [[0, {"videos": [vid("primary", 0, rate=2)]}], [1000, {"videos": [vid("primary", 2, rate=2)]}]]
        self.assertEqual(run_clock("presentation", ticks), [0, 1000])

    def test_no_videos(self):
        self.assertEqual(run_clock("presentation", [[0, {}], [250, {}]]), [0, 250])


# --------------------------------------------------------------------------- the mapping

class Mapping(unittest.TestCase):
    def test_points(self):
        f = session_map([[100, 0, "primary"], [1100, 500, "primary"], [2100, 500, "primary"]], 100)
        self.assertEqual([f(t) for t in (0, 100, 600, 1100, 1600, 2100, 2600)],
                         [0, 0, 250, 500, 500, 500, 1000])

    def test_no_points_is_the_wall_clock(self):
        f = session_map(None, 300)
        self.assertEqual([f(0), f(300), f(1300)], [0, 0, 1000])

    def test_normalise_maps_requests_and_samples(self):
        raw = {"t0": T0, "startupMs": 100, "origin": T0 + 100,
               "requests": [{"wall": T0 + 1100, "url": "https://a.example/x", "kind": "aps", "fixture": "x"},
                            {"wall": T0 + 1100, "url": "https://a.example/v/1.m4s", "kind": "aps-media"},
                            {"wall": T0 + 1100, "url": "https://time.akamai.com/?iso&ms", "kind": "time"}],
               "observation": {"samples": [{"t": 1600, "layout": "none", "elements": []}],
                               "clock": {"mode": "presentation",
                                         "points": [[100, 0, "p"], [1100, 500, "p"], [2100, 1000, "p"]]}}}
        obs = normalise(raw, 1000)
        self.assertEqual([r["at"] for r in obs.requests], [500])
        self.assertEqual(obs.others, [])          # neither aps-media nor time is a beacon
        self.assertEqual(obs.samples[0]["t"], 750)


# --------------------------------------------------------------------------- attribution and selection

def ad(doc, cid="c1", inst=1, pass_=None, opp_doc="https://e.invalid/main.mpd"):
    e = {"element": "ad", "doc": doc, "candidateIndex": "1" if cid is None else None, "optionIndex": "1",
         "opportunityDoc": opp_doc, "opportunityEvent": "1", "inst": inst}
    if cid is not None:
        e["candidateId"] = cid
        del e["candidateIndex"]
    if pass_ is not None:
        e["pass"] = pass_
    return e


URL = "https://aps.example.com/p?w=1"
FX = Fixtures({"main.mpd": "https://e.invalid/main.mpd", "first.xml": URL}, {})


def sel(*cands, result="presented"):
    return {"opportunity": {"fixture": "main.mpd", "event_id": "1"}, "result": result,
            "presented": [{"candidate": {"fixture": f, "id": c}, "option": {"index": 1}, "layout": "pause-fullscreen"}
                          for f, c in cands]}


def samples(*spans):
    """spans: (from, to, element) shown in pause-fullscreen; sampled every 100."""
    end = max(s[1] for s in spans) + 200
    out = []
    for t in range(0, end, 100):
        els = [copy.deepcopy(e) for a, b, e in spans if a <= t < b]
        out.append({"t": t, "layout": "pause-fullscreen" if els else "none", "elements": els})
    return out


class Attribution(unittest.TestCase):
    def obs(self, reqs, smp):
        o = Observed(requests=[{"at": a, "url": URL, "fixture": f, "kind": "aps"} for a, f in reqs], samples=smp)
        attribute(o, FX)
        return o

    def test_second_document_at_one_url(self):
        o = self.obs([(0, "first.xml"), (5000, "second.xml")],
                     samples((2000, 5000, ad(URL, inst=1)), (5000, 8000, ad(URL, inst=2))))
        out, d = compare_selection([sel(("first.xml", "c1"), ("second.xml", "c1"))], o, FX, 250)
        self.assertEqual(out, Outcome.PASS, d)

    def test_without_the_request_record_it_is_the_first_fixture(self):
        # the defect: by URL alone, the second document is the first fixture
        o = self.obs([], samples((2000, 5000, ad(URL, inst=1)), (5000, 8000, ad(URL, inst=2))))
        out, d = compare_selection([sel(("first.xml", "c1"), ("second.xml", "c1"))], o, FX, 250)
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("first.xml:c1", d.split("observed")[1])

    def test_surface_keeps_the_document_it_appeared_with(self):
        # a re-request while the first document's surface is still on screen
        # does not re-attribute it
        o = self.obs([(0, "first.xml"), (3000, "second.xml")], samples((2000, 6000, ad(URL, inst=1))))
        out, d = compare_selection([sel(("first.xml", "c1"))], o, FX, 250)
        self.assertEqual(out, Outcome.PASS, d)
        later = [e for x in o.samples if x["t"] >= 4000 for e in x["elements"]]
        self.assertTrue(later and all(e["docFixture"] == "first.xml" for e in later))


class PresentationByDocument(unittest.TestCase):
    """R32.1-2's shape: the second document's candidate replaces the first's
    with the same URL, index and option, after a gap shorter than the
    tolerance: the change is the document's, and it must be observed."""

    def run_(self, reqs):
        o = Observed(requests=[{"at": a, "url": URL, "fixture": f, "kind": "aps"} for a, f in reqs],
                     samples=samples((2000, 5000, ad(URL, inst=1)), (5100, 8000, ad(URL, inst=2))))
        for x in o.samples:
            if not x["elements"]:
                x["elements"] = [{"element": "primary", "time": 0, "paused": False, "rate": 1, "inst": 9}]
        attribute(o, FX)
        cand = lambda f: {"element": "ad", "candidate": {"fixture": f, "id": "c1"}, "option": {"index": 1}}  # noqa: E731
        exp = [{"start": 0, "end": 2000, "layout": "none", "shows": [{"element": "primary", "from": 0}]},
               {"start": 2000, "end": 5000, "layout": "pause-fullscreen", "shows": [cand("first.xml")]},
               {"start": 5000, "end": 8000, "layout": "pause-fullscreen", "shows": [cand("second.xml")]},
               {"start": 8000, "end": 8800, "layout": "none", "shows": [{"element": "primary", "from": 0}]}]
        return compare_presentation(exp, o, 8800, 250, FX, [], 1000)

    def test_document_change_is_a_change(self):
        out, d = self.run_([(0, "first.xml"), (5000, "second.xml")])
        self.assertEqual(out, Outcome.PASS, d)

    def test_same_document_throughout_fails(self):
        out, d = self.run_([(0, "first.xml")])
        self.assertEqual(out, Outcome.FAIL)


class Sequence(unittest.TestCase):
    def check(self, expected, smp, tol=250):
        o = Observed(samples=smp)
        attribute(o, FX)
        return compare_selection(expected, o, FX, tol)

    def test_three_passes_by_element(self):
        smp = samples((2000, 5000, ad(URL, inst=1)), (5000, 8000, ad(URL, inst=2)), (8000, 10000, ad(URL, inst=3)))
        self.assertEqual(self.check([sel(*[("first.xml", "c1")] * 3)], smp)[0], Outcome.PASS)
        out, d = self.check([sel(*[("first.xml", "c1")] * 2)], smp)
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("1 presentation(s) more", d)
        self.assertEqual(self.check([sel(*[("first.xml", "c1")] * 4)], smp)[0], Outcome.FAIL)

    def test_passes_by_video_restart(self):
        smp = samples((2000, 5000, ad(URL, pass_=0)), (5000, 8000, ad(URL, pass_=1)))
        self.assertEqual(self.check([sel(*[("first.xml", "c1")] * 2)], smp)[0], Outcome.PASS)

    def test_one_surface_throughout_is_one_pass(self):
        smp = samples((2000, 8000, ad(URL)))
        self.assertEqual(self.check([sel(("first.xml", "c1"))], smp)[0], Outcome.PASS)
        self.assertEqual(self.check([sel(*[("first.xml", "c1")] * 2)], smp)[0], Outcome.FAIL)

    def test_flicker_shorter_than_the_tolerance_is_the_same(self):
        smp = samples((2000, 4000, ad(URL)), (4200, 8000, ad(URL)))      # a 200 gap, tolerance 250
        self.assertEqual(self.check([sel(("first.xml", "c1"))], smp)[0], Outcome.PASS)
        smp = samples((2000, 4000, ad(URL)), (4300, 8000, ad(URL)))      # 300: back after a gap
        self.assertEqual(self.check([sel(("first.xml", "c1"))], smp)[0], Outcome.FAIL)

    def test_declined_then_presented(self):
        smp = samples((10000, 13000, ad(URL)))
        exp = [sel(result="declined"), sel(("first.xml", "c1"))]
        self.assertEqual(self.check(exp, smp)[0], Outcome.PASS)
        exp = [sel(("first.xml", "c1")), sel(result="declined")]
        self.assertEqual(self.check(exp, smp)[0], Outcome.PASS)    # order cannot tell which pause
        self.assertEqual(self.check([sel(result="declined"), sel(result="declined")], smp)[0], Outcome.FAIL)

    def test_two_presented_entries_take_the_presentations_in_turn(self):
        # R36.5-1's shape: one opportunity, a first pause and a second, each
        # with the document served for it
        o = Observed(requests=[{"at": 0, "url": URL, "fixture": "first.xml", "kind": "aps"},
                               {"at": 20000, "url": URL, "fixture": "second.xml", "kind": "aps"}],
                     samples=samples((2000, 4000, ad(URL, inst=1)), (30000, 32000, ad(URL, inst=2))))
        attribute(o, FX)
        exp = [sel(("first.xml", "c1")), sel(("second.xml", "c1"))]
        self.assertEqual(compare_selection(exp, o, FX, 250)[0], Outcome.PASS)
        exp.reverse()
        self.assertEqual(compare_selection(exp, o, FX, 250)[0], Outcome.FAIL)

    def test_linear_ad_under_an_on_top_overlay_is_one_presentation(self):
        # R40.5-1's shape: a linear ad (no option) 4..14 s; an on-top overlay
        # over it 6..10 s turns the viewport's layout to the overlay's. The
        # linear ad stays one presentation, with layout `linear`.
        fx = Fixtures({"main.mpd": "https://e.invalid/main.mpd", "list.mpd": "https://aps.example.com/l",
                       "overlay.xml": URL}, {})
        lin = {"element": "ad", "doc": "https://aps.example.com/l", "candidateId": "ad-1",
               "opportunityDoc": "https://e.invalid/main.mpd", "opportunityEvent": "1", "inst": 1}
        ov = dict(ad(URL, cid=None), opportunityEvent="2", inst=2)
        smp = []
        for t in range(0, 16000, 100):
            els = ([copy.deepcopy(lin)] if 4000 <= t < 14000 else []) + ([copy.deepcopy(ov)] if 6000 <= t < 10000 else [])
            lay = "overlay-lower-third" if 6000 <= t < 10000 else "linear" if els else "none"
            smp.append({"t": t, "layout": lay, "elements": els})
        o = Observed(samples=smp)
        attribute(o, fx)
        exp = [{"opportunity": {"fixture": "main.mpd", "event_id": "1"}, "result": "presented",
                "presented": [{"candidate": {"fixture": "list.mpd", "id": "ad-1"}, "option": None, "layout": "linear"}]},
               {"opportunity": {"fixture": "main.mpd", "event_id": "2"}, "result": "presented",
                "presented": [{"candidate": {"fixture": "overlay.xml", "index": 1}, "option": {"index": 1},
                               "layout": "overlay-lower-third"}]}]
        out, d = compare_selection(exp, o, fx, 250)
        self.assertEqual(out, Outcome.PASS, d)
        # a non-linear surface keeps the layout it appeared with: the same
        # overlay listed as `overlay` is a FAIL
        exp[1]["presented"][0]["layout"] = "overlay"
        self.assertEqual(compare_selection(exp, o, fx, 250)[0], Outcome.FAIL)
        exp[1]["presented"][0]["layout"] = "overlay-lower-third"
        # both appear in one sample (R40.5-1: the insertion and the window at
        # 4 s): the viewport shows the overlay's layout, the linear ad is
        # still `linear`
        for s in smp:
            if 4000 <= s["t"] < 6000:
                s["elements"].append(copy.deepcopy(ov))
                s["layout"] = "overlay-lower-third"
        o = Observed(samples=smp)
        attribute(o, fx)
        out, d = compare_selection(exp, o, fx, 250)
        self.assertEqual(out, Outcome.PASS, d)

    def test_empty_both(self):
        self.assertEqual(self.check([sel(result="declined")], samples((0, 1, {"element": "primary"})))[0],
                         Outcome.PASS)
        self.assertEqual(self.check([], [])[0], Outcome.PASS)


# --------------------------------------------------------------------------- jobs: aps, media, entry, live, capabilities

class _FakeServer:
    def __init__(self):
        self.mpds = {}

        class C:
            def prepare(self, track, segdur):
                return None
        self.content = C()


SUB_MPD = """<?xml version="1.0"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="static" mediaPresentationDuration="PT12S">
  <BaseURL>https://ads-cdn.example.com/b/ad/</BaseURL>
  <Period id="ad" duration="PT12S"><AdaptationSet contentType="video" mimeType="video/mp4">
    <SegmentTemplate timescale="1000" duration="2000" startNumber="1"
       initialization="$RepresentationID$/init.mp4" media="$RepresentationID$/$Number$.m4s"/>
    <Representation id="v" bandwidth="1" width="960" height="540"/></AdaptationSet></Period></MPD>"""
LIST = """<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011" xmlns:svta="urn:svta:dash:sgai:2026">
  <svta:Ad><svta:RenderableAsset src="https://ads-cdn.example.com/b/ad/banner.png" mimeType="image/png"/>
  </svta:Ad></svta:OverlayList>"""


def job_for(aps, sends=None, entry_text=SUB_MPD, actions=(), cls="D1"):
    server = _FakeServer()
    media = behaviour.Media(server, "http://127.0.0.1:1")
    fx = Fixtures({"main.mpd": "https://sgai-entry.invalid/main.mpd", "ad.mpd": "https://ads-cdn.example.com/b/ad/ad.mpd",
                   "list.xml": "https://aps.example.com/list"},
                  {"main.mpd": entry_text, "ad.mpd": SUB_MPD, "list.xml": LIST})
    mm = media.add(SUB_MPD, fx.urls["ad.mpd"])
    v = {"timescale": 1000, "play_from": 2000, "observe_until": 10000, "entry": "main.mpd",
         "player_capabilities": {"D1": {}}, "sends_capabilities": sends if sends is not None else [], "aps": aps}
    return behaviour.build_job("j1", v, fx, mm, cls, list(actions), SOURCE, media), media, mm


class Jobs(unittest.TestCase):
    def test_aps_on_a_segment_or_a_creative_is_not_a_document(self):
        job, _, _ = job_for([{"url": "https://ads-cdn.example.com/b/ad/v/4.m4s", "status": 404},
                             {"url": "https://ads-cdn.example.com/b/ad/banner.png", "status": 404},
                             {"url": "https://aps.example.com/list", "status": 404},
                             {"url": "https://ads-cdn.example.com/b/ad/v/notasegment.xml", "status": 404}])
        self.assertEqual([a["media"] for a in job["aps"]], [True, True, False, False])

    def test_aps_with_a_document_is_a_document(self):
        job, _, _ = job_for([{"url": "https://ads-cdn.example.com/b/ad/v/4.m4s", "status": 200,
                              "document": "behaviour/fixtures/R32.1/second.xml"}])
        self.assertFalse(job["aps"][0]["media"])

    def test_segments_and_not_creatives_go_to_the_content_server(self):
        job, media, mm = job_for([])
        self.assertTrue(media.is_segment("https://ads-cdn.example.com/b/ad/v/init.mp4", mm))
        self.assertTrue(media.is_segment("https://ads-cdn.example.com/b/ad/v/12.m4s?x=1", mm))
        self.assertFalse(media.is_segment("https://ads-cdn.example.com/b/ad/banner.png", mm))
        self.assertFalse(media.is_segment("https://ads-cdn.example.com/b/ad/v/x.m4s", mm))
        # what the runner receives: the same answer, as regular expressions
        # over the local path (a node check, below, runs them as JS)
        self.assertTrue(job["media"] and all(m["segments"] for m in job["media"]))

    @unittest.skipUnless(shutil.which("node"), "node is not installed")
    def test_segment_patterns_as_javascript(self):
        job, _, _ = job_for([])
        m = job["media"][0]
        script = ("const m = JSON.parse(require('fs').readFileSync(0, 'utf8'));"
                  "const rx = m.segments.map((x) => new RegExp(x));"
                  "const t = (u) => rx.some((r) => r.test(new URL(m.local + u.slice(m.prefix.length).split('?')[0]).pathname));"
                  "process.stdout.write(JSON.stringify(['v/init.mp4', 'v/3.m4s', 'banner.png', 'banner.html']"
                  ".map((x) => t(m.prefix + x))));")
        p = subprocess.run(["node", "-e", script], input=json.dumps(m), capture_output=True, text=True, timeout=30)
        self.assertEqual(json.loads(p.stdout), [True, True, False, False], p.stderr)

    def test_sends_capabilities(self):
        job, _, _ = job_for([], sends=["sgai-video-decoders", "sgai-image-over-video"])
        self.assertEqual(job["sendsCapabilities"], ["sgai-video-decoders", "sgai-image-over-video"])
        self.assertEqual(job_for([])[0]["sendsCapabilities"], [])
        self.assertEqual(job_for([], sends=["sgai-video-decoders"], cls="legacy")[0]["sendsCapabilities"], [])

    def test_live_now(self):
        live = SUB_MPD.replace('type="static"', 'type="dynamic" availabilityStartTime="2026-09-26T18:00:00Z"')
        job, _, _ = job_for([], entry_text=live)
        ast = 1790445600000   # 2026-09-26T18:00:00Z
        self.assertEqual(job["utcAtLoad"], ast + 2000 + 10000)       # play_from + observation at 1x
        job, _, _ = job_for([], entry_text=live, actions=[{"at": 0, "do": "rate", "rate": 2}])
        self.assertEqual(job["utcAtLoad"], ast + 2000 + 20000)       # at 2x the observation spans 20 s of it
        self.assertIsNone(job_for([])[0]["utcAtLoad"])               # static: the machine's time

    def test_clock_and_wall_limit(self):
        job, _, _ = job_for([])
        self.assertEqual(job["clock"], "presentation")
        self.assertEqual(job["wallLimitMs"], 10000 * 4 + behaviour.JOB_MARGIN_MS)


class FixtureBesideTheVector(unittest.TestCase):
    def test_entry_outside_the_source(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("XDG_RUNTIME_DIR")) as d:
            d = Path(d)
            (d / "fixtures").mkdir()
            (d / "fixtures" / "main.mpd").write_text(SUB_MPD)
            v = {"entry": "fixtures/main.mpd", "fixtures": [{"path": "fixtures/main.mpd"},
                                                             {"path": "behaviour/fixtures/R32.1/second.xml"}],
                 "outcomes": {}}
            with self.assertRaises(FileNotFoundError):     # the defect: only the source is read
                behaviour.fixtures_of(v, SOURCE)
            fx = behaviour.fixtures_of(v, SOURCE, d)
            self.assertEqual(fx.urls["fixtures/main.mpd"], behaviour.ENTRY_HOST + "fixtures/main.mpd")
            self.assertEqual(fx.of(behaviour.ENTRY_HOST + "fixtures/main.mpd"), "fixtures/main.mpd")
            self.assertIn("Second document", fx.texts["behaviour/fixtures/R32.1/second.xml"])


class ActionTiming(unittest.TestCase):
    """R16.1's shape: a boundary an action causes is measured from the frame
    the action was made in (its `startedAt`), not from its written time: the
    Player cannot answer a viewer before the viewer acts."""
    PAUSE_AD = {"element": "ad", "doc": URL, "candidateIndex": "1", "optionIndex": "1",
                "opportunityDoc": "https://e.invalid/main.mpd", "opportunityEvent": "1", "inst": 1}
    EXPECTED = [
        {"start": 0, "end": 3000, "layout": "none", "shows": [{"element": "primary", "from": 0}]},
        {"start": 3000, "end": 6000, "layout": "pause-fullscreen",
         "shows": [{"element": "ad", "candidate": {"fixture": "first.xml", "index": 1}, "option": {"index": 1}}]},
        {"start": 6000, "end": 8000, "tolerance": 17, "layout": "none",
         "shows": [{"element": "primary", "from": 3000}]},
    ]

    def obs(self, gone_at, started_at):
        smp = []
        for t in list(range(0, 8000, 25)) + [gone_at]:
            if t < 3000:
                els = [{"element": "primary", "time": t, "paused": False, "rate": 1}]
                lay = "none"
            elif t < gone_at:
                els, lay = [dict(self.PAUSE_AD)], "pause-fullscreen"
            else:
                els = [{"element": "primary", "time": 3000 + (t - gone_at), "paused": False, "rate": 1}]
                lay = "none"
            smp.append({"t": t, "layout": lay, "elements": els})
        smp.sort(key=lambda s: s["t"])
        o = Observed(samples=smp, startup=0)
        o.actions = [{"at": 3000, "do": "pause", "startedAt": 3000},
                     {"at": 6000, "do": "resume", "startedAt": started_at, "timing": "frame"}]
        attribute(o, FX)
        return o

    def check(self, gone_at, started_at):
        return compare_presentation(self.EXPECTED, self.obs(gone_at, started_at), 8000, 250, FX,
                                    [{"at": 3000, "do": "pause"}, {"at": 6000, "do": "resume"}], 1000)

    def test_gone_at_the_next_frame_after_a_late_action(self):
        out, d = self.check(6031, 6014)             # the action 14 ms late, the ad gone 17 ms after it
        self.assertEqual(out, Outcome.PASS, d)

    def test_gone_two_frames_after_the_action(self):
        self.assertEqual(self.check(6048, 6014)[0], Outcome.FAIL)   # 34 ms after the action

    def test_an_action_on_time_is_not_moved(self):
        self.assertEqual(self.check(6016, 6000)[0], Outcome.PASS)
        self.assertEqual(self.check(6018, 6000)[0], Outcome.FAIL)

    def test_an_early_record_does_not_move_the_boundary_back(self):
        self.assertEqual(self.check(6010, 5980)[0], Outcome.PASS)    # judged from 6000, not from 5980


class NoJobSelected(unittest.TestCase):
    """A selection that matches no job cannot tell: exit 2 with a line that
    says so, never "0 PASS" and exit 0."""

    def test_zero_jobs_cannot_tell(self):
        report = behaviour.Report()
        plans = behaviour.plan_jobs(SOURCE, [SOURCE / "behaviour" / "R1.4.yaml"], ["D5", "legacy"], report)
        self.assertEqual(plans, [])
        self.assertEqual(report.exit_code(), 2)
        lines = behaviour.summary_lines(report, 0.0, None)
        self.assertTrue(any(x.startswith("cannot tell: no job selected") for x in lines), lines)
        self.assertTrue(lines[-1].startswith("exit 2"), lines)

    def test_no_file_cannot_tell(self):
        report = behaviour.Report()
        self.assertEqual(behaviour.plan_jobs(SOURCE, [], [], report), [])
        self.assertEqual(report.exit_code(), 2)

    def test_one_job_is_not_flagged(self):
        report = behaviour.Report()
        plans = behaviour.plan_jobs(SOURCE, [SOURCE / "behaviour" / "R1.4.yaml"], [], report)
        self.assertGreaterEqual(len(plans), 1)
        self.assertEqual(report.cannot, [])


# --------------------------------------------------------------------------- the content server

class DroppedConnection(unittest.TestCase):
    """A Player that closes a connection mid-answer is not an error of the
    harness; an exception of the handler still is."""

    def serve(self):
        server = players._Server(players.Content(Path(tempfile.mkdtemp(dir=os.environ.get("XDG_RUNTIME_DIR")))))
        th = threading.Thread(target=server.serve_forever, daemon=True)
        th.start()
        return server

    def stop(self, server):
        server.shutdown()
        server.server_close()
        shutil.rmtree(server.content.root, ignore_errors=True)

    def drop(self, port):
        s = socket.create_connection(("127.0.0.1", port))
        s.sendall(b"GET /lib/dashjs/dash.all.min.js HTTP/1.1\r\nHost: x\r\n\r\n")
        s.recv(64)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
        s.close()                         # an RST while the server is still writing

    @unittest.skipUnless((players.PLAYERS_DIR / "node_modules" / "dashjs").is_dir(), "no dash.js in bin/players")
    def test_reset_prints_nothing(self):
        err = io.StringIO()
        server = self.serve()
        try:
            with contextlib.redirect_stderr(err):
                for _ in range(5):
                    self.drop(server.server_address[1])
                time.sleep(0.5)
        finally:
            self.stop(server)
        self.assertNotIn("Traceback", err.getvalue())

    def test_a_handler_exception_still_prints(self):
        err = io.StringIO()
        server = self.serve()
        orig = players._Handler.do_GET
        players._Handler.do_GET = lambda self: (_ for _ in ()).throw(ValueError("a harness defect"))
        try:
            with contextlib.redirect_stderr(err):
                s = socket.create_connection(("127.0.0.1", server.server_address[1]))
                s.sendall(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n")
                s.settimeout(2)
                with contextlib.suppress(OSError):
                    s.recv(64)
                s.close()
                time.sleep(0.3)
        finally:
            players._Handler.do_GET = orig
            self.stop(server)
        self.assertIn("a harness defect", err.getvalue())


if __name__ == "__main__":
    unittest.main()

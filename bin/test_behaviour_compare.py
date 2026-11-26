#!/usr/bin/env python3
"""Tests for the behaviour battery's comparison (bin/conformance/behaviour_compare.py).

On synthetic observations only: no browser, no server, no Player (ADR 0087:
the bin/ suite never runs the battery). `synthetic_raw` builds, from an
outcome, the record bin/players/behaviour.mjs would write for a Player that
did exactly what the outcome says; each test then breaks one thing in it or in
the vector and checks the verdict of the field it belongs to, and of that
field only.

Run:  python3 bin/test_behaviour_compare.py   (needs PyYAML for the UC-01 cases)
"""
import copy
import os
import sys
import unittest

BIN = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BIN)

from conformance import behaviour  # noqa: E402
from conformance.behaviour_compare import (Fixtures, Observed, added_query, attribute, compare,  # noqa: E402
                                           compare_selection, normalise, observed_segments)
from conformance.model import Outcome  # noqa: E402

SOURCE = os.path.join(os.path.dirname(BIN), "spec-source")
T0 = 1_700_000_000_000
FULL = {"x": 0, "y": 0, "width": 100, "height": 100}


def _ms(t, ts):
    return t * 1000.0 / ts


def _mid(when):
    return (when["from"] + when["to"]) / 2 if isinstance(when, dict) else when


def synthetic_raw(v, outcome, fx, startup_ms=200, shift_ms=0):
    """The raw record of a Player that did exactly what `outcome` says, every
    time moved by `shift_ms`, the first frame `startup_ms` after load."""
    ts = v["timescale"]
    reqs = [{"wall": T0 + 40, "url": fx.urls[v["entry"]], "kind": "document", "fixture": v["entry"]}]
    for r in outcome["requests"]:
        q = "&".join(f"{k}={val}" for k, val in (r.get("query") or {}).items())
        url = r["url"] + (("&" if "?" in r["url"] else "?") + q if q else "")
        reqs.append({"wall": T0 + _ms(_mid(r["at"]), ts) + shift_ms, "url": url, "kind": "document",
                     "fixture": r.get("answered_by")})
    for b in outcome["beacons"]:
        from conformance.behaviour_compare import beacon_url_of
        reqs.append({"wall": T0 + _ms(_mid(b["at"]), ts) + shift_ms, "url": beacon_url_of(b, fx),
                     "kind": "other", "resourceType": "fetch"})
    opp = {}
    for sel in outcome["selection"]:
        for p in sel["presented"]:
            c = p["candidate"]
            opp[(c["fixture"], c.get("id"), c.get("index"))] = sel["opportunity"]
    samples = [{"t": 30, "layout": "none", "elements": []}]
    segs = outcome["presentation"]
    for i, seg in enumerate(segs):
        els = []
        for e in seg["shows"]:
            if e["element"] == "primary":
                nxt = segs[i + 1] if i + 1 < len(segs) else None
                pn = next((x for x in nxt["shows"] if x["element"] == "primary"), None) if nxt else None
                paused = pn is not None and pn["from"] == e["from"] and seg["end"] > seg["start"]
                els.append({"element": "primary", "rect": dict(FULL), "time": _ms(e["from"], ts),
                            "paused": paused, "rate": 1})
            else:
                c = e["candidate"]
                el = {"element": e["element"], "rect": dict(FULL), "doc": fx.urls.get(c["fixture"], c["fixture"])}
                if "id" in c:
                    el["candidateId"] = c["id"]
                else:
                    el["candidateIndex"] = str(c["index"])
                o = e.get("option")
                if o is not None:
                    el["optionId" if "id" in o else "optionIndex"] = o.get("id") or str(o.get("index"))
                op = opp.get((c["fixture"], c.get("id"), c.get("index")))
                if op:
                    el["opportunityDoc"] = fx.urls.get(op["fixture"], op["fixture"])
                    el["opportunityEvent"] = str(op["event_id"])
                els.append(el)
        t = startup_ms if i == 0 else _ms(seg["start"], ts) + shift_ms
        samples.append({"t": t, "layout": seg["layout"], "elements": els})
    for g in outcome.get("geometry") or []:
        at = _ms(g["at"], ts)
        cur = [s for s in samples if s["t"] <= at][-1]
        s = copy.deepcopy(cur)
        s["t"] = at
        for e in s["elements"]:
            if e["element"] == "primary" and "primary" in g:
                e["rect"] = dict(g["primary"])
            if e["element"] == "ad" and "ad" in g:
                e["rect"] = dict(g["ad"])
        samples.append(s)
        samples.sort(key=lambda x: x["t"])
    # Already on the session clock: the origin is load() (startupMs 0), and
    # the first frame `startup_ms` after it folds into the first segment.
    # The Origin tests below build records whose origin is the first frame.
    return {"id": "j1", "ok": True, "t0": T0, "startupMs": 0, "origin": T0, "requests": reqs, "actions": [],
            "observation": {"t0": T0, "samples": samples}}


def verdicts(results):
    return {r.rule: r.outcome for r in results}


def details(results):
    return {r.rule: r.detail for r in results}


# --------------------------------------------------------------------------- a small vector

def small_vector():
    """An overlay at 10..20 s over a playing primary, with geometry, a request
    with an added parameter, and two beacons."""
    ad = {"fixture": "behaviour/fixtures/X/list.mpd", "id": "c1"}
    v = {
        "timescale": 1000, "tolerance": 250, "play_from": 0, "observe_until": 30000,
        "entry": "behaviour/fixtures/X/main.mpd",
        "outcomes": {"D1": {
            "summary": "s",
            "requests": [{"at": {"from": 5000, "to": 9000}, "url": "https://aps.example.com/ov?a=1",
                          "query": {"sgai-video-decoders": "2"},
                          "answered_by": "behaviour/fixtures/X/list.mpd"}],
            "selection": [{"opportunity": {"fixture": "behaviour/fixtures/X/main.mpd", "event_id": "5"},
                           "result": "presented",
                           "presented": [{"candidate": ad, "option": {"index": 1},
                                          "layout": "overlay-lower-third"}]}],
            "presentation": [
                {"start": 0, "end": 10000, "layout": "none", "shows": [{"element": "primary", "from": 0}]},
                {"start": 10000, "end": 20000, "layout": "overlay-lower-third",
                 "shows": [{"element": "primary", "from": 10000},
                           {"element": "ad", "candidate": ad, "option": {"index": 1}}]},
                {"start": 20000, "end": 30000, "layout": "none", "shows": [{"element": "primary", "from": 20000}]},
            ],
            "beacons": [{"at": 10000, "fixture": "behaviour/fixtures/X/list.mpd", "id": "1",
                         "url": "https://t.example.com/imp?c=1"},
                        {"at": 20000, "fixture": "behaviour/fixtures/X/list.mpd", "id": "2"}],
            "geometry": [{"at": 15000, "tolerance": 1,
                          "primary": {"x": 0, "y": 0, "width": 100, "height": 100},
                          "ad": {"x": 10, "y": 75, "width": 80, "height": 20}}],
        }},
    }
    list_mpd = """<MPD xmlns="urn:mpeg:dash:schema:mpd:2011" type="list"><Period id="c1">
<EventStream schemeIdUri="urn:mpeg:dash:event:callback:2015"><Event id="1">https://t.example.com/imp?c=1</Event>
<Event id="2">https://t.example.com/end?c=1</Event><Event id="9">https://t.example.com/never?c=1</Event>
</EventStream></Period></MPD>"""
    fx = Fixtures({"behaviour/fixtures/X/main.mpd": "https://sgai-entry.invalid/main.mpd",
                   "behaviour/fixtures/X/list.mpd": "https://aps.example.com/ov?a=1"},
                  {"behaviour/fixtures/X/main.mpd": "<MPD xmlns='urn:mpeg:dash:schema:mpd:2011'/>",
                   "behaviour/fixtures/X/list.mpd": list_mpd})
    return v, v["outcomes"]["D1"], fx


def run(v, outcome, fx, raw, actions=()):
    return compare(v, outcome, raw, fx, "T D1", [dict(a) for a in actions])


class Baseline(unittest.TestCase):
    def test_exact_observation_passes_every_field(self):
        v, o, fx = small_vector()
        got = verdicts(run(v, o, fx, synthetic_raw(v, o, fx)))
        self.assertEqual(got, {f: Outcome.PASS for f in
                               ("requests", "selection", "presentation", "beacons", "geometry")})

    def test_harness_failure_is_not_verifiable_everywhere(self):
        v, o, fx = small_vector()
        for raw in (None, {"ok": False, "harnessError": "boom"}):
            rs = run(v, o, fx, raw)
            self.assertTrue(all(r.outcome is Outcome.NOT_VERIFIABLE for r in rs), rs)
            self.assertEqual(len(rs), 5)

    def test_audio_is_not_verifiable(self):
        v, o, fx = small_vector()
        o["presentation"][0]["audio"] = "primary"
        got = verdicts(run(v, o, fx, synthetic_raw(v, o, fx)))
        self.assertEqual(got["audio"], Outcome.NOT_VERIFIABLE)
        self.assertEqual(got["presentation"], Outcome.PASS)

    def test_timescale_is_converted(self):
        v, o, fx = small_vector()
        raw = synthetic_raw(v, o, fx)
        v2, o2 = copy.deepcopy(v), copy.deepcopy(o)
        k = 90
        v2["timescale"], v2["tolerance"], v2["observe_until"] = 90000, 250 * k, 30000 * k

        def scale(x):
            return {"from": x["from"] * k, "to": x["to"] * k} if isinstance(x, dict) else x * k
        for r in o2["requests"] + o2["beacons"]:
            r["at"] = scale(r["at"])
        for s in o2["presentation"]:
            s["start"], s["end"] = s["start"] * k, s["end"] * k
            for e in s["shows"]:
                if "from" in e:
                    e["from"] *= k
        for g in o2["geometry"]:
            g["at"] *= k
        self.assertTrue(all(r.outcome is Outcome.PASS for r in run(v2, o2, fx, raw)))


class Requests(unittest.TestCase):
    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        self.raw = synthetic_raw(self.v, self.o, self.fx)
        self.req = self.raw["requests"][1]

    def field(self):
        rs = run(self.v, self.o, self.fx, self.raw)
        return verdicts(rs)["requests"], details(rs)["requests"]

    def test_window_edges_with_tolerance(self):
        for at, want in ((4750, Outcome.PASS), (4749, Outcome.FAIL), (9250, Outcome.PASS), (9251, Outcome.FAIL)):
            self.req["wall"] = T0 + at
            self.assertEqual(self.field()[0], want, at)

    def test_exact_time_threshold(self):
        self.o["requests"][0]["at"] = 7000
        for at, want in ((7250, Outcome.PASS), (6750, Outcome.PASS), (7251, Outcome.FAIL), (6749, Outcome.FAIL)):
            self.req["wall"] = T0 + at
            self.assertEqual(self.field()[0], want, at)

    def test_missing_request(self):
        del self.raw["requests"][1]
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("not observed", d)

    def test_unexpected_request(self):
        self.raw["requests"].append(dict(self.req, wall=T0 + 25000))
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("unexpected request", d)

    def test_entry_is_not_compared(self):
        self.raw["requests"].append(dict(self.raw["requests"][0], wall=T0 + 20000))
        self.assertEqual(self.field()[0], Outcome.PASS)
        # also when an `aps` entry answers it without a document
        self.raw["requests"].append(dict(self.raw["requests"][0], wall=T0 + 21000, kind="aps", fixture=None))
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_query_the_player_adds(self):
        self.req["url"] = "https://aps.example.com/ov?a=1&sgai-video-decoders=1"
        self.assertEqual(self.field()[0], Outcome.FAIL)
        self.req["url"] = "https://aps.example.com/ov?a=1"
        self.assertEqual(self.field()[0], Outcome.FAIL)
        self.req["url"] = "https://aps.example.com/ov?sgai-video-decoders=2&a=1"
        self.assertEqual(self.field()[0], Outcome.PASS)
        self.req["url"] = "https://aps.example.com/ov?a=1&sgai-video-decoders=2&x=y"
        self.assertEqual(self.field()[0], Outcome.FAIL)

    def test_declared_parameter_missing_is_another_url(self):
        self.req["url"] = "https://aps.example.com/ov?sgai-video-decoders=2"
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("not observed", d)

    def test_answered_by(self):
        self.req["fixture"] = None
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("answered_by None", d)

    def test_matches_http(self):
        self.o["requests"][0]["matches"] = "x.http"
        self.fx.texts["x.http"] = "GET /ov?a=1&sgai-video-decoders=2 HTTP/1.1\nHost: aps.example.com\n"
        self.assertEqual(self.field()[0], Outcome.PASS)
        self.fx.texts["x.http"] = "GET /ov?a=1&sgai-video-decoders=3 HTTP/1.1\nHost: aps.example.com\n"
        self.assertEqual(self.field()[0], Outcome.FAIL)
        del self.fx.texts["x.http"]
        self.assertEqual(self.field()[0], Outcome.NOT_VERIFIABLE)

    def test_none_expected_none_observed(self):
        self.o["requests"] = []
        del self.raw["requests"][1]
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_added_query(self):
        self.assertEqual(added_query("https://a/x?k=1", "http://a/x?k=1&b=2"), {"b": "2"})
        self.assertIsNone(added_query("https://a/x?k=1", "https://a/y?k=1"))
        self.assertIsNone(added_query("https://a/x?k=1", "https://a/x?k=2"))
        self.assertEqual(added_query("https://a/x", "https://a/x?l=a%20b"), {"l": "a b"})


class Beacons(unittest.TestCase):
    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        self.raw = synthetic_raw(self.v, self.o, self.fx)

    def field(self):
        rs = run(self.v, self.o, self.fx, self.raw)
        return verdicts(rs)["beacons"], details(rs)["beacons"]

    def beacon(self, url):
        return next(r for r in self.raw["requests"] if r["url"] == url)

    def test_url_read_from_the_fixture(self):
        self.assertTrue(any(r["url"] == "https://t.example.com/end?c=1" for r in self.raw["requests"]))
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_time_threshold(self):
        b = self.beacon("https://t.example.com/imp?c=1")
        for at, want in ((10250, Outcome.PASS), (10251, Outcome.FAIL), (9750, Outcome.PASS), (9749, Outcome.FAIL)):
            b["wall"] = T0 + at
            self.assertEqual(self.field()[0], want, at)

    def test_missing(self):
        self.raw["requests"].remove(self.beacon("https://t.example.com/end?c=1"))
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("observed at never", d)

    def test_fired_twice_is_unexpected(self):
        self.raw["requests"].append(dict(self.beacon("https://t.example.com/imp?c=1"), wall=T0 + 12000))
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("unexpected beacon https://t.example.com/imp?c=1", d)

    def test_a_declared_beacon_not_expected(self):
        self.raw["requests"].append({"wall": T0 + 5000, "url": "https://t.example.com/never?c=1", "kind": "other"})
        self.assertEqual(self.field()[0], Outcome.FAIL)

    def test_other_requests_are_not_beacons(self):
        self.raw["requests"].append({"wall": T0 + 5000, "url": "https://img.example.com/a.png", "kind": "other"})
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_query_order_does_not_matter(self):
        self.o["beacons"][0]["url"] = "https://t.example.com/imp?c=1&d=2"
        self.beacon("https://t.example.com/imp?c=1")["url"] = "https://t.example.com/imp?d=2&c=1"
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_no_url_and_no_event(self):
        self.o["beacons"][1]["id"] = "77"
        self.assertEqual(self.field()[0], Outcome.NOT_VERIFIABLE)

    def test_missing_beacon_without_id(self):
        # the schema does not require `id` on an expected beacon with a `url`
        del self.o["beacons"][0]["id"]
        self.raw["requests"].remove(self.beacon("https://t.example.com/imp?c=1"))
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("beacons[0] https://t.example.com/imp?c=1 expected at 10000; observed at never", d)

    def test_present_beacon_without_id(self):
        del self.o["beacons"][0]["id"]
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_no_url_no_id_is_not_verifiable(self):
        del self.o["beacons"][1]["id"]
        self.assertEqual(self.field()[0], Outcome.NOT_VERIFIABLE)

    def test_candidate_scope(self):
        self.o["beacons"][1]["candidate"] = {"fixture": "behaviour/fixtures/X/list.mpd", "id": "c1"}
        self.assertEqual(self.field()[0], Outcome.PASS)
        self.o["beacons"][1]["candidate"] = {"fixture": "behaviour/fixtures/X/list.mpd", "id": "c2"}
        self.assertEqual(self.field()[0], Outcome.NOT_VERIFIABLE)


class Presentation(unittest.TestCase):
    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        self.raw = synthetic_raw(self.v, self.o, self.fx)
        self.samples = self.raw["observation"]["samples"]

    def field(self, actions=()):
        rs = run(self.v, self.o, self.fx, self.raw, actions)
        return verdicts(rs)["presentation"], details(rs)["presentation"]

    def sample_at(self, t):
        return next(s for s in self.samples if s["t"] == t)

    def test_boundary_threshold(self):
        s = self.sample_at(10000)
        for t, want in ((10250, Outcome.PASS), (10251, Outcome.FAIL), (9750, Outcome.PASS)):
            s["t"] = t
            s["elements"][0]["time"] = t
            self.samples.sort(key=lambda x: x["t"])
            self.assertEqual(self.field()[0], want, t)

    def test_missing_change(self):
        self.samples.remove(self.sample_at(20000))
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("expected a change at 20000", d)

    def test_extra_change(self):
        s = copy.deepcopy(self.sample_at(0 + 200))
        s["t"], s["layout"] = 5000, "overlay-corner"
        s2 = copy.deepcopy(self.sample_at(200))
        s2["t"] = 6000
        self.samples += [s, s2]
        self.samples.sort(key=lambda x: x["t"])
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("which the vector does not have", d)

    def test_wrong_candidate(self):
        self.sample_at(10000)["elements"][1]["candidateId"] = "c9"
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("presentation[1]", d)

    def test_extra_surface(self):
        s = self.sample_at(200)
        s["elements"].append(dict(self.sample_at(10000)["elements"][1]))
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("presentation[0]", d)

    def test_wrong_option(self):
        del self.sample_at(10000)["elements"][1]["optionIndex"]
        self.assertEqual(self.field()[0], Outcome.FAIL)
        # and the other way: a linear candidate (option null) shown as an option
        for seg in self.o["presentation"]:
            for e in seg["shows"]:
                if e["element"] == "ad":
                    e["option"] = None
        ads = [e for s in self.samples for e in s["elements"] if e["element"] == "ad"]
        for e in ads:
            e.pop("optionIndex", None)
        self.assertEqual(self.field()[0], Outcome.PASS)
        for e in ads:
            e["optionIndex"] = "1"
        self.assertEqual(self.field()[0], Outcome.FAIL)

    def test_from_threshold(self):
        p = self.sample_at(20000)["elements"][0]
        for t, want in ((20250, Outcome.PASS), (20251, Outcome.FAIL)):
            p["time"] = t
            self.assertEqual(self.field()[0], want, t)

    def test_nothing_ever_shown(self):
        self.raw["observation"]["samples"] = [{"t": 0, "layout": "none", "elements": []}]
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("nothing was ever shown", d)

    def test_startup_is_not_a_change(self):
        self.samples[1]["t"] = 900
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_short_glitch_is_folded(self):
        blank = {"t": 20000, "layout": "none", "elements": []}
        self.sample_at(20000)["t"] = 20100
        self.samples.append(blank)
        self.samples.sort(key=lambda x: x["t"])
        self.assertEqual(self.field()[0], Outcome.PASS)
        self.sample_at(20100)["t"] = 20400   # a blank of 400 ms is a change
        self.assertEqual(self.field()[0], Outcome.FAIL)

    def test_pause_is_a_segment(self):
        # UC-07's shape: 0..5000 playing, 5000..8000 paused, then playing again.
        self.o["presentation"] = [
            {"start": 0, "end": 5000, "layout": "none", "shows": [{"element": "primary", "from": 830000}]},
            {"start": 5000, "end": 8000, "layout": "none", "shows": [{"element": "primary", "from": 835000}]},
            {"start": 8000, "end": 30000, "layout": "none", "shows": [{"element": "primary", "from": 835000}]},
        ]
        p = lambda t, mt, paused: {"t": t, "layout": "none", "elements": [  # noqa: E731
            {"element": "primary", "rect": FULL, "time": mt, "paused": paused, "rate": 1}]}
        self.raw["observation"]["samples"] = [p(200, 830000, False), p(5050, 835050, True),
                                              p(8100, 835050, False)]
        self.assertEqual(self.field()[0], Outcome.PASS)
        # never paused: the split at 5000 is silent (835000 = 830000 + 5000),
        # the one at 8000 is not, and the primary at 8000 is at 838000
        self.raw["observation"]["samples"] = [p(200, 830000, False)]
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("expected a change at 8000", d)
        self.assertIn("primary from expected 835000, observed 837800", d)   # first frame at 200

    def test_silent_boundary_needs_no_change(self):
        # A written split with nothing observable across it.
        self.o["presentation"] = [
            {"start": 0, "end": 4000, "layout": "none", "shows": [{"element": "primary", "from": 0}]},
            {"start": 4000, "end": 30000, "layout": "none", "shows": [{"element": "primary", "from": 4000}]},
        ]
        self.raw["observation"]["samples"] = [{"t": 0, "layout": "none", "elements": [
            {"element": "primary", "rect": FULL, "time": 0, "paused": False, "rate": 1}]}]
        self.assertEqual(self.field()[0], Outcome.PASS)
        # at rate 2 the same split is silent only if `from` doubles
        self.raw["observation"]["samples"][0]["elements"][0]["rate"] = 2
        self.o["presentation"][1]["from"] = 8000
        self.o["presentation"][1]["shows"][0]["from"] = 8000
        self.assertEqual(self.field([{"at": 0, "do": "rate", "rate": 2}])[0], Outcome.PASS)
        self.assertEqual(self.field([])[0], Outcome.FAIL)

    def test_from_across_a_silent_boundary_reads_the_samples(self):
        # A written split with nothing to observe: the primary's time at 4000
        # is read from the samples, so a stall shows, and is judged with the
        # tolerance (a clock run on from the segment's start would not see it).
        self.o["presentation"] = [
            {"start": 0, "end": 4000, "layout": "none", "shows": [{"element": "primary", "from": 0}]},
            {"start": 4000, "end": 30000, "layout": "none", "shows": [{"element": "primary", "from": 4000}]},
        ]
        p = lambda t, mt: {"t": t, "layout": "none", "elements": [  # noqa: E731
            {"element": "primary", "rect": FULL, "time": mt, "paused": False, "rate": 1}]}
        for stall, want in ((250, Outcome.PASS), (251, Outcome.FAIL)):
            self.raw["observation"]["samples"] = [p(0, 0), p(3800, 3800 - stall)]
            out, d = self.field()
            self.assertEqual(out, want, stall)
        self.assertIn("primary from expected 4000, observed 3749", d)

    def test_seek_is_a_change(self):
        self.o["presentation"] = [
            {"start": 0, "end": 5000, "layout": "none", "shows": [{"element": "primary", "from": 0}]},
            {"start": 5000, "end": 30000, "layout": "none", "shows": [{"element": "primary", "from": 615000}]},
        ]
        p = lambda t, mt, seek=None: dict({"t": t, "layout": "none", "elements": [  # noqa: E731
            {"element": "primary", "rect": FULL, "time": mt, "paused": False, "rate": 1}]},
            **({"seek": seek} if seek else {}))
        self.raw["observation"]["samples"] = [p(200, 0), p(5040, 615000, {"from": 4840, "to": 615000})]
        self.assertEqual(self.field()[0], Outcome.PASS)
        # a seek within tolerance (a Player's own nudge) is not a change
        segs, _ = observed_segments([dict(p(200, 0)), dict(p(3000, 2900, {"from": 2800, "to": 2900}))],
                                    30000, 250)
        self.assertEqual(len(segs), 1)

    def test_seek_of_a_hidden_primary_is_not_a_change(self):
        # Under a linear ad the primary is not on screen (not in `elements`);
        # the reference moves it to RT ahead of the ad's end. That seek is no
        # boundary: the ad segment runs on, and the next segment's `from` is
        # the primary's time when it is shown again.
        ad = {"element": "ad", "rect": FULL, "doc": "ad.mpd", "candidateId": "a", "time": 0}
        p = lambda t, mt: {"t": t, "layout": "none", "elements": [  # noqa: E731
            {"element": "primary", "rect": FULL, "time": mt, "paused": False, "rate": 1}]}
        lin = lambda t, seek=None: dict({"t": t, "layout": "linear", "elements": [dict(ad)]},  # noqa: E731
                                        **({"seek": seek} if seek else {}))
        samples = [p(0, 0), lin(10000), lin(25000, {"from": 10000, "to": 40000}), p(40000, 40000)]
        segs, _ = observed_segments(samples, 60000, 250)
        self.assertEqual([(s.start, s.layout) for s in segs], [(0, "none"), (10000, "linear"), (40000, "none")])
        self.assertEqual(segs[2].from_, 40000)
        self.assertEqual([s.seek for s in segs], [False, False, True])
        # the seek at the exact tolerance is no change either way; one past it,
        # with the primary on screen, still splits
        shown = [p(0, 0), dict(p(25000, 40000), seek={"from": 25000, "to": 40000})]
        self.assertEqual(len(observed_segments(shown, 60000, 250)[0]), 2)
        at_tol = [p(0, 0), dict(p(25000, 25250), seek={"from": 25000, "to": 25250})]
        self.assertEqual(len(observed_segments(at_tol, 60000, 250)[0]), 1)
        # a hidden seek as the last sample, and with no elements at all
        segs, _ = observed_segments([p(0, 0), lin(10000), lin(25000, {"from": 10000, "to": 40000})], 30000, 250)
        self.assertEqual(len(segs), 2)
        empty = [p(0, 0), {"t": 10000, "layout": "none", "elements": []},
                 {"t": 12000, "layout": "none", "elements": [], "seek": {"from": 10000, "to": 40000}},
                 p(14000, 40000)]
        self.assertEqual([s.start for s in observed_segments(empty, 30000, 250)[0]], [0, 10000, 14000])
        # a viewer's seek that blanks the primary for less than the tolerance
        # (R34.6 D1 as recorded: 'seeking' with nothing on screen at 12342,
        # the primary back at 3000 at 12383) is held, and splits where the
        # primary is shown again: the blank folds, the seek does not
        blink = [p(0, 0), p(12339, 12022), {"t": 12342, "layout": "none", "elements": [],
                                            "seek": {"from": 12022, "to": 3000}},
                 {"t": 12356, "layout": "none", "elements": []}, p(12383, 3000), p(12902, 3477)]
        segs, _ = observed_segments(blink, 21000, 250)
        self.assertEqual([(s.start, s.from_, s.seek) for s in segs], [(0, 0, False), (12383, 3000, True)])
        # the same blank with no seek folds into one segment
        blank = [x for x in blink if "seek" not in x]
        self.assertEqual(len(observed_segments(blank, 21000, 250)[0]), 1)

    def background_vector(self, with_candidate):
        """The overlay segment of the small vector with a `background` added,
        written as R12.5-1 writes it (no candidate) or as UC-09 does."""
        seg = self.o["presentation"][1]
        bg = {"element": "background"}
        if with_candidate:
            bg.update(candidate=seg["shows"][1]["candidate"], option={"index": 1})
        seg["shows"].append(bg)
        self.bg_el = dict(self.sample_at(10000)["elements"][1], element="background")

    def show_background(self, *els):
        """Put `els` on screen wherever the overlay is (its samples at 10000
        and at 15000, the geometry's)."""
        for s in self.samples:
            if any(e["element"] == "ad" for e in s["elements"]):
                s["elements"].extend(els)

    def test_background_without_candidate_never_shown(self):
        # The D-11 crash: a written boundary into a segment whose background
        # has no candidate, not observed, made describe_exp raise KeyError.
        self.background_vector(with_candidate=False)
        self.samples[:] = [s for s in self.samples if s["t"] < 10000]
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("expected a change at 10000 to overlay-lower-third [primary from 10000, "
                      "ad behaviour/fixtures/X/list.mpd:c1 option #1, background]", d)

    def test_background_without_candidate_matches_any_background(self):
        self.background_vector(with_candidate=False)
        self.assertEqual(self.field()[0], Outcome.FAIL)            # no background on screen
        self.show_background(self.bg_el)
        self.assertEqual(self.field()[0], Outcome.PASS)
        self.bg_el["candidateId"] = "c9"                           # its candidate is not compared
        self.assertEqual(self.field()[0], Outcome.PASS)
        self.show_background(dict(self.bg_el))                     # but it is counted
        self.assertEqual(self.field()[0], Outcome.FAIL)

    def test_background_with_candidate_is_compared(self):
        self.background_vector(with_candidate=True)
        self.show_background(self.bg_el)
        self.assertEqual(self.field()[0], Outcome.PASS)
        self.bg_el["candidateId"] = "c9"
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("background behaviour/fixtures/X/list.mpd:c1 option #1]", d)


class Selection(unittest.TestCase):
    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        self.raw = synthetic_raw(self.v, self.o, self.fx)
        self.ad = next(e for s in self.raw["observation"]["samples"] for e in s["elements"]
                       if e["element"] == "ad")

    def field(self):
        rs = run(self.v, self.o, self.fx, self.raw)
        return verdicts(rs)["selection"], details(rs)["selection"]

    def test_unattributed_ad(self):
        del self.ad["opportunityEvent"]
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("does not list", d)

    def test_wrong_layout(self):
        self.o["selection"][0]["presented"][0]["layout"] = "overlay-corner"
        self.assertEqual(self.field()[0], Outcome.FAIL)

    def test_declined_expects_nothing(self):
        # whatever `presented` holds, `declined` expects nothing on screen
        self.o["selection"][0]["result"] = "declined"
        self.assertEqual(self.field()[0], Outcome.FAIL)
        for s in self.raw["observation"]["samples"]:
            s["elements"] = [e for e in s["elements"] if e["element"] != "ad"]
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_order_of_first_appearance(self):
        second = dict(self.ad, candidateId="c2")
        self.o["selection"][0]["presented"].insert(0, {"candidate": {"fixture": "behaviour/fixtures/X/list.mpd",
                                                                     "id": "c2"}, "option": {"index": 1},
                                                       "layout": "overlay-lower-third"})
        s = next(s for s in self.raw["observation"]["samples"] if self.ad in s["elements"])
        late = copy.deepcopy(s)
        late["t"] += 3000
        # c2 joins c1 on screen (c1 stays: the record shows c1 again at the
        # geometry sample, and an ad back after a gap is a new presentation)
        late["elements"] = late["elements"] + [second]
        self.raw["observation"]["samples"].append(late)
        self.raw["observation"]["samples"].sort(key=lambda x: x["t"])
        self.assertEqual(self.field()[0], Outcome.FAIL)   # c1 came first
        self.o["selection"][0]["presented"].reverse()
        self.assertEqual(self.field()[0], Outcome.PASS)


class Geometry(unittest.TestCase):
    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        self.raw = synthetic_raw(self.v, self.o, self.fx)
        self.s = next(s for s in self.raw["observation"]["samples"] if s["t"] == 15000)

    def field(self):
        rs = run(self.v, self.o, self.fx, self.raw)
        return verdicts(rs)["geometry"], details(rs)["geometry"]

    def test_edge_threshold(self):
        ad = next(e for e in self.s["elements"] if e["element"] == "ad")
        for x, want in ((11, Outcome.PASS), (9, Outcome.PASS), (11.01, Outcome.FAIL)):
            ad["rect"]["x"] = x
            ad["rect"]["width"] = 90 - x   # right edge stays at 90
            self.assertEqual(self.field()[0], want, x)

    def test_union_of_ad_surfaces(self):
        ad = next(e for e in self.s["elements"] if e["element"] == "ad")
        ad["rect"] = {"x": 10, "y": 75, "width": 40, "height": 20}
        self.assertEqual(self.field()[0], Outcome.FAIL)
        self.s["elements"].append(dict(ad, rect={"x": 50, "y": 80, "width": 40, "height": 15}))
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_background_is_part_of_the_ad_layer(self):
        # schema.json, geometry.ad: "the bounding box of the ad layer, every
        # element of the ad included"; the background is the advertiser's
        # creative (R26), so a full-frame background makes the box the frame.
        ad = next(e for e in self.s["elements"] if e["element"] == "ad")
        self.s["elements"].append(dict(ad, element="background", rect=dict(FULL)))
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("ad {'x': 0", d)
        self.o["geometry"][0]["ad"] = dict(FULL)
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_no_ad_on_screen(self):
        self.s["elements"] = [e for e in self.s["elements"] if e["element"] != "ad"]
        for s in self.raw["observation"]["samples"]:
            s["elements"] = [e for e in s["elements"] if e["element"] != "ad"]
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("ad None", d)

    def test_primary_squeezed(self):
        self.o["geometry"][0]["primary"] = {"x": 0, "y": 0, "width": 75, "height": 75}
        self.assertEqual(self.field()[0], Outcome.FAIL)

    def test_window_around_a_transition(self):
        # the ad appears 200 ms after the instant: within tolerance
        self.o["geometry"][0]["at"] = 9800
        self.assertEqual(self.field()[0], Outcome.FAIL)   # the moved geometry sample is still at 15000
        self.s["t"] = 10000
        self.raw["observation"]["samples"].sort(key=lambda x: x["t"])
        self.assertEqual(self.field()[0], Outcome.PASS)
        self.o["geometry"][0]["at"] = 9749
        self.assertEqual(self.field()[0], Outcome.FAIL)


class UC01(unittest.TestCase):
    """The worked example of spec-source/scenarios/, read from disk."""

    @classmethod
    def setUpClass(cls):
        try:
            import yaml
        except ImportError:
            raise unittest.SkipTest("PyYAML not importable")
        from pathlib import Path
        cls.v = yaml.safe_load(Path(SOURCE, "scenarios", "UC-01.yaml").read_text(encoding="utf-8"))
        cls.fx = behaviour.fixtures_of(cls.v, Path(SOURCE))

    def test_synthetic_passes_and_each_change_fails_only_its_field(self):
        o = self.v["outcomes"]["D1"]
        raw = synthetic_raw(self.v, o, self.fx)
        self.assertEqual(set(verdicts(run(self.v, o, self.fx, raw)).values()), {Outcome.PASS})
        cases = {
            "requests": lambda o: o["requests"][2].update(answered_by="examples/annex-a/A.4-1.mpd"),
            "selection": lambda o: o["selection"][0]["presented"].reverse(),
            "presentation": lambda o: o["presentation"][2]["shows"][0].update({"from": 1000}),
            "beacons": lambda o: o["beacons"][2].update(at=4750),
        }
        for name, change in cases.items():
            o2 = copy.deepcopy(o)
            change(o2)
            got = verdicts(run(self.v, o2, self.fx, raw))
            self.assertEqual(got[name], Outcome.FAIL, name)
            self.assertEqual({k for k, x in got.items() if x is not Outcome.PASS}, {name}, name)

    def test_skeleton_observation_fails_every_field(self):
        o = self.v["outcomes"]["D1"]
        p = {"element": "primary", "rect": FULL, "time": 0, "paused": False, "rate": 1}
        raw = {"ok": True, "t0": T0, "requests": [], "observation": {"samples": [
            {"t": 50, "layout": "none", "elements": []}, {"t": 230, "layout": "none", "elements": [p]}]}}
        got = verdicts(run(self.v, o, self.fx, raw))
        self.assertEqual(set(got.values()), {Outcome.FAIL})


class ItemTolerance(unittest.TestCase):
    """A request's, a beacon's or a segment's own `tolerance` replaces the
    vector's for that item only."""

    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        self.raw = synthetic_raw(self.v, self.o, self.fx)

    def verdict(self, f):
        return verdicts(run(self.v, self.o, self.fx, self.raw))[f]

    def test_request(self):
        self.o["requests"][0]["at"] = 7000
        self.o["requests"][0]["tolerance"] = 10
        req = self.raw["requests"][1]
        for at, want in ((7010, Outcome.PASS), (7011, Outcome.FAIL), (6990, Outcome.PASS), (6989, Outcome.FAIL)):
            req["wall"] = T0 + at
            self.assertEqual(self.verdict("requests"), want, at)

    def test_beacon(self):
        self.o["beacons"][0]["tolerance"] = 0
        b = next(r for r in self.raw["requests"] if r["url"] == "https://t.example.com/imp?c=1")
        b["wall"] = T0 + 10000
        self.assertEqual(self.verdict("beacons"), Outcome.PASS)
        b["wall"] = T0 + 10001
        self.assertEqual(self.verdict("beacons"), Outcome.FAIL)
        # the other beacon keeps the vector's 250
        e = next(r for r in self.raw["requests"] if r["url"] == "https://t.example.com/end?c=1")
        e["wall"] = T0 + 20250
        b["wall"] = T0 + 10000
        self.assertEqual(self.verdict("beacons"), Outcome.PASS)

    def test_segment_boundary_and_its_from(self):
        # R16.1's shape: 17 on one boundary, the vector's 250 elsewhere
        self.o["presentation"][2]["tolerance"] = 17
        s20 = next(s for s in self.raw["observation"]["samples"] if s["t"] == 20000)
        s10 = next(s for s in self.raw["observation"]["samples"] if s["t"] == 10000)
        s10["t"], s10["elements"][0]["time"] = 10200, 10200       # 200 late: within 250
        for t, want in ((20017, Outcome.PASS), (20018, Outcome.FAIL)):
            s20["t"], s20["elements"][0]["time"] = t, 20000
            self.raw["observation"]["samples"].sort(key=lambda x: x["t"])
            self.assertEqual(self.verdict("presentation"), want, t)
        s20["t"] = 20000
        for mt, want in ((20017, Outcome.PASS), (20018, Outcome.FAIL)):     # its `from` too
            s20["elements"][0]["time"] = mt
            self.assertEqual(self.verdict("presentation"), want, mt)


class Windows(unittest.TestCase):
    """A presentation boundary written {from, to}: the Player's instant."""

    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        del self.o["geometry"]          # its sample at 15000 would be a change of its own
        self.raw = synthetic_raw(self.v, self.o, self.fx)
        w = {"from": 15000, "to": 18000}
        self.o["presentation"][1]["end"] = w
        self.o["presentation"][2]["start"] = w
        self.o["presentation"][2]["shows"][0]["from"] = dict(w)
        self.s20 = next(s for s in self.raw["observation"]["samples"] if s["t"] == 20000)

    def at(self, t):
        self.s20["t"] = t
        self.s20["elements"][0]["time"] = t
        self.raw["observation"]["samples"].sort(key=lambda x: x["t"])
        return verdicts(run(self.v, self.o, self.fx, self.raw))["presentation"]

    def test_edges(self):
        for t, want in ((15000, Outcome.PASS), (16500, Outcome.PASS), (18000, Outcome.PASS),
                        (14750, Outcome.PASS), (18250, Outcome.PASS),
                        (14749, Outcome.FAIL), (18251, Outcome.FAIL)):
            self.assertEqual(self.at(t), want, t)

    def test_from_window(self):
        self.at(16000)
        self.s20["elements"][0]["time"] = 10000        # the primary jumped back: outside the window
        self.assertEqual(verdicts(run(self.v, self.o, self.fx, self.raw))["presentation"], Outcome.FAIL)

    def test_same_surfaces_across_a_window_are_not_silent(self):
        # primary alone on both sides: a split written as a window must still
        # be observed (an exact split there would be silent)
        w = {"from": 15000, "to": 18000}
        self.o["presentation"] = [
            {"start": 0, "end": w, "layout": "none", "shows": [{"element": "primary", "from": 0}]},
            {"start": w, "end": 30000, "layout": "none", "shows": [{"element": "primary", "from": 15000}]}]
        self.raw["observation"]["samples"] = [{"t": 0, "layout": "none", "elements": [
            {"element": "primary", "rect": FULL, "time": 0, "paused": False, "rate": 1}]}]
        self.assertEqual(verdicts(run(self.v, self.o, self.fx, self.raw))["presentation"], Outcome.FAIL)

    def test_a_window_is_never_silent(self):
        # the change must be observed: without it, a FAIL even though the
        # surfaces either side could look alike
        self.raw["observation"]["samples"].remove(self.s20)
        self.assertEqual(verdicts(run(self.v, self.o, self.fx, self.raw))["presentation"], Outcome.FAIL)


class ExtraQuery(unittest.TestCase):
    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        self.raw = synthetic_raw(self.v, self.o, self.fx)
        self.req = self.raw["requests"][1]
        self.o["requests"][0]["extra_query_pattern"] = "x-[a-z0-9]+-.+"

    def verdict(self, url):
        self.req["url"] = url
        return verdicts(run(self.v, self.o, self.fx, self.raw))["requests"]

    def test_pattern(self):
        base = "https://aps.example.com/ov?a=1&sgai-video-decoders=2"
        self.assertEqual(self.verdict(base), Outcome.PASS)
        self.assertEqual(self.verdict(base + "&x-acme-model=tv1"), Outcome.PASS)
        self.assertEqual(self.verdict(base + "&x-acme-model=tv1&x-b-c=2"), Outcome.PASS)
        self.assertEqual(self.verdict(base + "&model=tv1"), Outcome.FAIL)          # unprefixed
        self.assertEqual(self.verdict(base + "&x-acme=tv1"), Outcome.FAIL)         # no name after the prefix
        self.assertEqual(self.verdict(base + "&ax-acme-model=tv1"), Outcome.FAIL)   # the whole name
        self.assertEqual(self.verdict("https://aps.example.com/ov?a=1&x-acme-model=1"), Outcome.FAIL)  # query missing

    def test_without_pattern_exact(self):
        del self.o["requests"][0]["extra_query_pattern"]
        self.assertEqual(self.verdict("https://aps.example.com/ov?a=1&sgai-video-decoders=2&x-acme-model=1"),
                         Outcome.FAIL)


class NotCompared(unittest.TestCase):
    def test_requests_not_compared(self):
        v, o, fx = small_vector()
        raw = synthetic_raw(v, o, fx)
        o["requests"] = []
        o["requests_not_compared"] = "R4.10 forbids presenting, not requesting"
        rs = run(v, o, fx, raw)
        self.assertEqual(verdicts(rs)["requests"], Outcome.NOT_APPLICABLE)
        self.assertIn("R4.10 forbids", details(rs)["requests"])
        del o["requests_not_compared"]
        self.assertEqual(verdicts(run(v, o, fx, raw))["requests"], Outcome.FAIL)   # the request is unexpected


LIST = """<svta:OverlayList xmlns="urn:mpeg:dash:schema:mpd:2011" xmlns:svta="urn:svta:dash:sgai:2026" family="overlay">
<svta:Ad><svta:RenderableAsset src="https://cdn/a.png" mimeType="image/png" duration="PT4S" layout="overlay-corner"/>
<svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1" timescale="1000">
<Event presentationTime="0" id="1">https://t.example.com/imp?c=1</Event></svta:Tracking>
<svta:ClickThrough uri="https://brand.example.com/c1"/></svta:Ad>
<svta:Ad><svta:RenderableAsset src="https://cdn/b.png" mimeType="image/png" duration="PT4S" layout="overlay-corner"/>
<svta:Tracking schemeIdUri="urn:mpeg:dash:event:callback:2015" value="1" timescale="1000">
<Event presentationTime="0" id="1">https://t.example.com/imp?c=2</Event></svta:Tracking>
<svta:ClickThrough uri="https://brand.example.com/c2" trackingUris="https://t.example.com/clk?c=2 https://t2.example.com/clk"/>
</svta:Ad></svta:OverlayList>"""


class Clicks(unittest.TestCase):
    """R28.1's carrier: click-tracking fired and the destination made
    available, at the activation; neither otherwise."""

    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        self.fx.texts["behaviour/fixtures/X/ol.xml"] = LIST
        self.fx.urls["behaviour/fixtures/X/ol.xml"] = "https://aps.example.com/ol"
        c1 = {"fixture": "behaviour/fixtures/X/ol.xml", "index": 1}
        c2 = {"fixture": "behaviour/fixtures/X/ol.xml", "index": 2}
        self.o["clicks"] = [{"at": 7000, "fixture": c2["fixture"], "candidate": c2, "url": "https://t.example.com/clk?c=2"},
                            {"at": 7000, "fixture": c2["fixture"], "candidate": c2, "url": "https://t2.example.com/clk"}]
        self.o["destinations"] = [{"at": 3000, "fixture": c1["fixture"], "candidate": c1},
                                  {"at": 7000, "fixture": c2["fixture"], "candidate": c2}]
        self.raw = synthetic_raw(self.v, self.o, self.fx)
        self.add("https://t.example.com/clk?c=2", 7050)
        self.add("https://t2.example.com/clk", 7060)
        self.add("https://brand.example.com/c1", 3100)
        self.raw["observation"]["destinations"] = [{"t": 7020, "uri": "https://brand.example.com/c2"}]

    def add(self, url, at):
        self.raw["requests"].append({"wall": T0 + at, "url": url, "kind": "other", "resourceType": "document"})

    def got(self):
        return verdicts(run(self.v, self.o, self.fx, self.raw))

    def test_as_expected(self):
        g = self.got()
        self.assertEqual((g["clicks"], g["destinations"], g["beacons"]), (Outcome.PASS,) * 3)

    def test_fields_only_with_clicks(self):
        del self.o["clicks"], self.o["destinations"]
        g = self.got()
        self.assertNotIn("clicks", g)
        # without `clicks`, a fired click-tracking URL is an unexpected beacon
        self.assertEqual(g["beacons"], Outcome.FAIL)

    def test_one_url_of_the_list_missing(self):
        self.raw["requests"] = [r for r in self.raw["requests"] if r["url"] != "https://t2.example.com/clk"]
        self.assertEqual(self.got()["clicks"], Outcome.FAIL)

    def test_click_threshold(self):
        r = next(r for r in self.raw["requests"] if r["url"] == "https://t2.example.com/clk")
        for at, want in ((7250, Outcome.PASS), (7251, Outcome.FAIL), (6750, Outcome.PASS), (6749, Outcome.FAIL)):
            r["wall"] = T0 + at
            self.assertEqual(self.got()["clicks"], want, at)

    def test_fired_twice_or_without_activation(self):
        self.add("https://t.example.com/clk?c=2", 7100)
        self.assertEqual(self.got()["clicks"], Outcome.FAIL)
        self.raw["requests"].pop()
        self.o["clicks"], self.o["destinations"] = [], []
        g = self.got()
        self.assertEqual((g["clicks"], g["destinations"]), (Outcome.FAIL, Outcome.FAIL))

    def test_none_expected_none_observed(self):
        self.o["clicks"], self.o["destinations"] = [], []
        self.raw["requests"] = [r for r in self.raw["requests"] if "clk" not in r["url"] and "brand" not in r["url"]]
        self.raw["observation"]["destinations"] = []
        g = self.got()
        self.assertEqual((g["clicks"], g["destinations"]), (Outcome.PASS, Outcome.PASS))

    def test_destination_opened_or_shown(self):
        # c2's destination shown on screen; also opened at the same time is no extra
        self.add("https://brand.example.com/c2", 7030)
        self.assertEqual(self.got()["destinations"], Outcome.PASS)
        # c1's destination never made available
        self.raw["requests"] = [r for r in self.raw["requests"] if r["url"] != "https://brand.example.com/c1"]
        self.assertEqual(self.got()["destinations"], Outcome.FAIL)

    def test_click_url_must_be_a_tracking_uri(self):
        # an expected click on the destination URL is not a click-tracking URL
        self.o["clicks"][1]["url"] = "https://brand.example.com/c2"
        r = next(r for r in self.raw["requests"] if r["url"] == "https://t2.example.com/clk")
        r["url"] = "https://brand.example.com/c2"
        self.assertEqual(self.got()["clicks"], Outcome.NOT_VERIFIABLE)

    def test_destination_swapped_for_tracking(self):
        # a Player that opens the tracking URL and pings the destination
        self.raw["observation"]["destinations"] = [{"t": 7020, "uri": "https://t.example.com/clk?c=2"}]
        g = self.got()
        self.assertEqual(g["destinations"], Outcome.FAIL)

    def test_destination_too_late(self):
        self.raw["observation"]["destinations"] = [{"t": 7251, "uri": "https://brand.example.com/c2"}]
        self.assertEqual(self.got()["destinations"], Outcome.FAIL)


class ClicksFromTheAction(Clicks):
    """A click and its destination written at an `activate`'s time are
    measured from when the executor made it (the action's `startedAt`: when
    the click reached the page), when later; never from earlier, and only for
    the action at that written time."""

    def setUp(self):
        super().setUp()
        self.raw["actions"] = [{"at": 3000, "do": "activate", "startedAt": 3000},
                               {"at": 7000, "do": "activate", "startedAt": 7000}]

    def late(self, made):
        self.raw["actions"][1]["startedAt"] = made
        for url, at in (("https://t.example.com/clk?c=2", made + 25), ("https://t2.example.com/clk", made + 25)):
            next(r for r in self.raw["requests"] if r["url"] == url)["wall"] = T0 + at
        self.raw["observation"]["destinations"] = [{"t": made + 20, "uri": "https://brand.example.com/c2"}]

    def test_a_late_click_is_measured_from_when_it_was_made(self):
        # R28.1-1 D1 under load: the click reached the page 230 ms late
        self.late(7230)
        g = self.got()
        self.assertEqual((g["clicks"], g["destinations"]), (Outcome.PASS, Outcome.PASS))

    def test_without_startedAt_the_written_time_holds(self):
        self.late(7240)        # click at 7265, destination at 7260: past 7000 + 250
        del self.raw["actions"][1]["startedAt"]
        g = self.got()
        self.assertEqual((g["clicks"], g["destinations"]), (Outcome.FAIL, Outcome.FAIL))

    def test_threshold_from_when_made(self):
        self.late(7230)
        r = next(r for r in self.raw["requests"] if r["url"] == "https://t2.example.com/clk")
        for at, want in ((7480, Outcome.PASS), (7481, Outcome.FAIL), (6980, Outcome.PASS), (6979, Outcome.FAIL)):
            r["wall"] = T0 + at
            self.assertEqual(self.got()["clicks"], want, at)
        for at, want in ((7480, Outcome.PASS), (7481, Outcome.FAIL)):
            self.raw["observation"]["destinations"] = [{"t": at, "uri": "https://brand.example.com/c2"}]
            self.assertEqual(self.got()["destinations"], want, at)

    def test_never_earlier(self):
        # an action recorded as made before its time does not pull the window in
        self.raw["actions"][1]["startedAt"] = 6900
        r = next(r for r in self.raw["requests"] if r["url"] == "https://t2.example.com/clk")
        for at, want in ((6749, Outcome.FAIL), (6750, Outcome.PASS), (7250, Outcome.PASS)):
            r["wall"] = T0 + at
            self.assertEqual(self.got()["clicks"], want, at)

    def test_only_the_action_at_that_time(self):
        self.late(7230)
        self.raw["actions"][1]["at"] = 6000      # no action at the written 7000
        self.assertEqual(self.got()["clicks"], Outcome.FAIL)

    def test_failure_says_when_made(self):
        self.late(7230)
        next(r for r in self.raw["requests"] if r["url"] == "https://t2.example.com/clk")["wall"] = T0 + 7600
        d = details(run(self.v, self.o, self.fx, self.raw))["clicks"]
        self.assertIn("expected at 7000 (the action made at 7230); observed at 7600", d)

    def test_tracking_beacon_not_expected(self):
        # a non-linear candidate's beacon lives in <svta:Tracking>, not in an
        # EventStream: fired and not expected, it is an unexpected beacon
        self.add("https://t.example.com/imp?c=2", 9000)
        g = self.got()
        self.assertEqual(g["beacons"], Outcome.FAIL)
        self.assertIn("unexpected beacon https://t.example.com/imp?c=2",
                      details(run(self.v, self.o, self.fx, self.raw))["beacons"])

    def test_tracking_beacon_with_click_tracking_judged_by_clicks(self):
        # the Tracking URLs stay beacons when clicks are judged; only the
        # ClickThrough's trackingUris move to the clicks field
        self.assertEqual(self.got()["beacons"], Outcome.PASS)
        self.add("https://t.example.com/imp?c=1", 9500)
        self.assertEqual(self.got()["beacons"], Outcome.FAIL)

    def test_overlay_candidate_scope_of_a_beacon(self):
        # a beacon named by candidate and @id in an OverlayList, with no url
        self.o["beacons"].append({"at": 9000, "fixture": "behaviour/fixtures/X/ol.xml",
                                  "candidate": {"fixture": "behaviour/fixtures/X/ol.xml", "index": 2}, "id": "1"})
        self.add("https://t.example.com/imp?c=2", 9000)
        self.assertEqual(self.got()["beacons"], Outcome.PASS)


class BeaconsFromTheirAd(unittest.TestCase):
    """R32.1-1's shape: a pause at 2000 shows the candidate three times in a
    row (2-5, 5-8, 8-10 s), its impression at each pass. A beacon's written
    time is on its ad's own timeline: when the pause is made late and the ad
    observed late within its boundary's tolerance, the beacons of that ad
    move with it; a beacon late relative to its own ad still fails."""

    AD = {"fixture": "behaviour/fixtures/X/list.mpd", "id": "c1"}
    IMP = "https://t.example.com/imp?c=1"

    def setUp(self):
        self.v, _, self.fx = small_vector()
        ad = {"element": "ad", "candidate": self.AD, "option": {"index": 1}}
        self.v["observe_until"] = 12000
        self.v["actions"] = [{"at": 2000, "do": "pause"}, {"at": 10000, "do": "resume"}]
        self.o = self.v["outcomes"]["D1"] = {
            "summary": "s",
            "requests": [{"at": {"from": 0, "to": 2000}, "url": "https://aps.example.com/ov?a=1",
                          "answered_by": "behaviour/fixtures/X/list.mpd"}],
            "selection": [{"opportunity": {"fixture": "behaviour/fixtures/X/main.mpd", "event_id": "1"},
                           "result": "presented",
                           "presented": [{"candidate": self.AD, "option": {"index": 1},
                                          "layout": "pause-fullscreen"}] * 3}],
            "presentation": [
                {"start": 0, "end": 2000, "layout": "none", "shows": [{"element": "primary", "from": 0}]},
                {"start": 2000, "end": 5000, "layout": "pause-fullscreen", "shows": [ad]},
                {"start": 5000, "end": 8000, "layout": "pause-fullscreen", "shows": [ad]},
                {"start": 8000, "end": 10000, "layout": "pause-fullscreen", "shows": [ad]},
                {"start": 10000, "end": 12000, "layout": "none", "shows": [{"element": "primary", "from": 2000}]},
            ],
            "beacons": [{"at": t, "fixture": "behaviour/fixtures/X/list.mpd", "candidate": self.AD, "id": "1",
                         "url": self.IMP} for t in (2000, 5000, 8000)],
        }
        self.raw = synthetic_raw(self.v, self.o, self.fx)
        self.raw["actions"] = [{"at": 2000, "do": "pause", "startedAt": 2000},
                               {"at": 10000, "do": "resume", "startedAt": 10000}]

    def observe(self, made, ad_at, fired=(0, 3000, 6000)):
        """The pause made at `made`, the ad on screen from `ad_at`, the
        impressions at `ad_at` + each of `fired`."""
        self.raw["actions"][0]["startedAt"] = made
        for s in self.raw["observation"]["samples"]:
            if s["layout"] == "pause-fullscreen":
                s["t"] = ad_at + (s["t"] - 2000) if s["t"] == 2000 else s["t"]
        imps = [r for r in self.raw["requests"] if r["url"] == self.IMP]
        for r, off in zip(imps, fired):
            r["wall"] = T0 + ad_at + off

    def got(self):
        rs = run(self.v, self.o, self.fx, self.raw, self.v["actions"])
        return verdicts(rs), details(rs)

    def test_as_written(self):
        g, _ = self.got()
        self.assertEqual((g["presentation"], g["beacons"]), (Outcome.PASS, Outcome.PASS))

    def test_r32_1_1_pause_made_late(self):
        # D1 under load: the pause made at 2074, the ad and its impression at 2255
        self.observe(2074, 2255)
        g, _ = self.got()
        self.assertEqual((g["presentation"], g["beacons"]), (Outcome.PASS, Outcome.PASS))

    def test_late_relative_to_its_own_ad_fails(self):
        # the impressions 400 ms after the ad they belong to
        self.observe(2074, 2255, (400, 3400, 6400))
        g, d = self.got()
        self.assertEqual((g["presentation"], g["beacons"]), (Outcome.PASS, Outcome.FAIL))
        self.assertIn("expected at 2000 (its ad observed from 2255, written 2000); observed at 2655", d["beacons"])

    def test_threshold_from_its_ad(self):
        self.observe(2074, 2255)
        r = next(r for r in self.raw["requests"] if r["url"] == self.IMP)
        for at, want in ((2505, Outcome.PASS), (2506, Outcome.FAIL), (2005, Outcome.PASS), (2004, Outcome.FAIL)):
            r["wall"] = T0 + at
            self.assertEqual(self.got()[0]["beacons"], want, at)

    def test_a_later_pass_is_on_the_same_timeline(self):
        # passes 2 and 3 follow the first: a second pass begun 300 ms late fails
        self.observe(2074, 2255, (0, 3300, 6000))
        g, d = self.got()
        self.assertEqual(g["beacons"], Outcome.FAIL)
        self.assertIn("beacons[1]", d["beacons"])

    def test_ad_later_than_its_boundary_tolerance_moves_nothing(self):
        # the ad 300 ms after the pause was made: unpaired, the beacons keep
        # their written times (from when the pause was made) and fail
        self.observe(2074, 2374)
        g, d = self.got()
        self.assertEqual((g["presentation"], g["beacons"]), (Outcome.FAIL, Outcome.FAIL))
        self.assertIn("expected at 2000 (the action made at 2074); observed at 2374", d["beacons"])

    def test_never_earlier(self):
        # the ad shown 200 ms early does not pull its beacons in
        self.observe(2000, 1800, (440, 3200, 6200))
        self.assertEqual(self.got()[0]["beacons"], Outcome.PASS)     # 2240 vs 2000 +- 250
        self.observe(2000, 1800, (451, 3200, 6200))
        self.assertEqual(self.got()[0]["beacons"], Outcome.FAIL)     # 2251

    def test_a_different_ad_on_screen_moves_nothing(self):
        # the boundary paired with a change that shows another candidate
        self.observe(2074, 2255)
        for s in self.raw["observation"]["samples"]:
            for e in s["elements"]:
                if e["element"] == "ad":
                    e["candidateId"] = "c2"
        g, _ = self.got()
        self.assertEqual((g["presentation"], g["beacons"]), (Outcome.FAIL, Outcome.FAIL))

    def test_a_beacon_outside_its_ad_is_not_moved(self):
        # a beacon written in the primary-only segment keeps its time
        self.o["beacons"].append({"at": 11000, "fixture": "behaviour/fixtures/X/list.mpd", "id": "2"})
        self.raw["requests"].append({"wall": T0 + 11000, "url": "https://t.example.com/end?c=1", "kind": "other"})
        self.observe(2074, 2255)
        self.assertEqual(self.got()[0]["beacons"], Outcome.PASS)
        self.raw["requests"][-1]["wall"] = T0 + 11251
        self.assertEqual(self.got()[0]["beacons"], Outcome.FAIL)

    def test_a_beacon_of_another_candidate_is_not_moved(self):
        # the ad 240 ms late, its impression 60 ms after it: moved, it passes
        self.observe(2000, 2240, (60, 0, 0))
        self.assertEqual(self.got()[0]["beacons"], Outcome.FAIL)      # passes 2, 3 at 2240: not theirs
        self.observe(2000, 2240, (60, 3000, 6000))
        self.assertEqual(self.got()[0]["beacons"], Outcome.PASS)
        # named for a candidate that ad is not, it keeps its written 2000
        self.o["beacons"][0]["candidate"] = {"fixture": "behaviour/fixtures/X/list.mpd", "id": "c2"}
        self.assertEqual(self.got()[0]["beacons"], Outcome.FAIL)      # 2300 vs 2000 +- 250


class Normalise(unittest.TestCase):
    def test_units(self):
        obs = normalise({"t0": 1000, "startupMs": 0,
                         "requests": [{"wall": 3000, "url": "u", "kind": "document"},
                                      {"wall": 2000, "url": "b", "kind": "other"}],
                         "observation": {"samples": [{"t": 500, "layout": "none", "elements": [
                             {"element": "primary", "time": 1000}], "seek": {"from": 0, "to": 1000}}]}},
                        90000)
        self.assertEqual(obs.requests[0]["at"], 180000)
        self.assertEqual(obs.others[0]["at"], 90000)
        self.assertEqual(obs.samples[0]["t"], 45000)
        self.assertEqual(obs.samples[0]["elements"][0]["time"], 90000)
        self.assertEqual(obs.samples[0]["seek"]["to"], 90000)


class Origin(unittest.TestCase):
    """The session clock starts at the first frame presented, not at load()
    (spec-source/scenarios/README.md): what happened before it is at 0."""

    def raw(self, startup, **extra):
        p = {"element": "primary", "rect": FULL, "time": 0, "paused": False, "rate": 1}
        return dict({"t0": T0, "requests": [
            {"wall": T0 + 100, "url": "https://x/early", "kind": "other"},
            {"wall": T0 + startup + 2000, "url": "https://x/late", "kind": "other"}],
            "observation": {"samples": [{"t": 50, "layout": "none", "elements": []},
                                        {"t": startup, "layout": "none", "elements": [p]},
                                        {"t": startup + 1000, "layout": "none", "elements": [dict(p, time=1000)]}],
                            "destinations": [{"t": startup + 3000, "uri": "https://brand/x"}]}}, **extra)

    def test_origin_from_each_source(self):
        # the runner's origin, the adapter's firstFrame, or the first sample
        # that shows something: the same instant, 565 ms after load()
        for raw in (self.raw(565, startupMs=565, origin=T0 + 565),
                    self.raw(565, origin=T0 + 565),
                    dict(self.raw(565), observation=dict(self.raw(565)["observation"], firstFrame=565)),
                    self.raw(565)):
            obs = normalise(raw, 1000)
            self.assertEqual(obs.startup, 565)
            self.assertEqual([o["at"] for o in obs.others], [0, 2000])     # the early one at 0
            self.assertEqual([s["t"] for s in obs.samples], [0, 0, 1000])
            self.assertEqual(obs.destinations, [{"at": 3000, "uri": "https://brand/x"}])

    def test_a_background_is_not_the_first_frame(self):
        raw = self.raw(565)
        raw["observation"]["samples"].insert(1, {"t": 300, "layout": "none", "elements": [
            {"element": "background", "rect": FULL}]})
        self.assertEqual(normalise(raw, 1000).startup, 565)

    def test_no_frame_keeps_load(self):
        raw = self.raw(565)
        raw["observation"]["samples"] = [{"t": 50, "layout": "none", "elements": []}]
        obs = normalise(raw, 1000)
        self.assertIsNone(obs.startup)
        self.assertEqual([o["at"] for o in obs.others], [100, 2565])

    def test_instant_zero_survives_a_long_startup(self):
        # T-03's finding: 227-565 ms from load() to the first frame against a
        # 250 ms tolerance. A beacon fired with the first frame is at 0.
        v, o, fx = small_vector()
        o["beacons"][0]["at"] = 0
        o["requests"] = []
        raw = synthetic_raw(v, o, fx)
        del raw["requests"][1:]
        raw["requests"].append({"wall": T0 + 565, "url": "https://t.example.com/imp?c=1", "kind": "other"})
        raw["requests"].append({"wall": T0 + 565 + 20000, "url": "https://t.example.com/end?c=1", "kind": "other"})
        for s in raw["observation"]["samples"]:
            s["t"] = s["t"] + 565 if s["t"] > 30 else s["t"]
        raw["observation"]["samples"][1]["t"] = 565
        del raw["startupMs"], raw["origin"]
        got = verdicts(run(v, o, fx, raw))
        self.assertEqual(got["beacons"], Outcome.PASS)
        self.assertEqual(got["presentation"], Outcome.PASS)
        # the same record on the load() clock: the beacon is 565 ms late
        raw["startupMs"] = 0
        self.assertEqual(verdicts(run(v, o, fx, raw))["beacons"], Outcome.FAIL)


class SuspendedSurface(unittest.TestCase):
    """A surface hidden and shown again (a suspension and its restore, R40.4,
    R17) is one presentation when it is the same DOM element (`inst`) and, for
    a <video>, the same pass; a new element or a restarted video is another."""

    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        del self.o["geometry"]
        self.raw = synthetic_raw(self.v, self.o, self.fx)
        samples = self.raw["observation"]["samples"]
        s10 = next(s for s in samples if s["t"] == 10000)
        self.ad = next(e for e in s10["elements"] if e["element"] == "ad")
        self.ad["inst"], self.ad["pass"] = 2, 0
        gone = {"t": 12000, "layout": "none", "elements": [
            {"element": "primary", "rect": FULL, "time": 12000, "paused": False, "rate": 1}]}
        self.back = copy.deepcopy(s10)
        self.back["t"] = 15000
        self.back["elements"][0]["time"] = 15000
        samples += [gone, self.back]
        samples.sort(key=lambda x: x["t"])
        self.back_ad = next(e for e in self.back["elements"] if e["element"] == "ad")

    def field(self):
        rs = run(self.v, self.o, self.fx, self.raw)
        return verdicts(rs)["selection"], details(rs)["selection"]

    def test_restore_after_a_long_gap_is_one_presentation(self):
        # 3000 ms hidden, far over the 250 tolerance
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_restore_with_no_gap_is_one_presentation(self):
        self.back["t"] = 12000.5
        self.raw["observation"]["samples"].sort(key=lambda x: x["t"])
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_a_new_element_is_a_new_presentation(self):
        self.back_ad["inst"] = 3
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("1 presentation(s) more", d)

    def test_a_restarted_video_is_a_new_presentation(self):
        self.back_ad["pass"] = 1
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("1 presentation(s) more", d)


class PresentationSerial(SuspendedSurface):
    """The serial a Player stamps on each presentation (`presentation`, its
    `data-sgai-presentation`) is part of a presentation's identity: a new
    serial on the same element (a still image shown again, R32.1's repeat) is
    a new presentation, the same serial after a gap (a suspension and its
    restore) is the same one, and no serial at all leaves the identity as
    the element and pass say."""

    def setUp(self):
        super().setUp()
        for e in (self.ad, self.back_ad):
            e.pop("pass")                 # a still image has no pass
            e["presentation"] = "1"

    def test_same_serial_after_a_gap_is_one_presentation(self):
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_new_serial_on_the_same_element_is_a_new_presentation(self):
        self.back_ad["presentation"] = "2"
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("1 presentation(s) more", d)

    def test_new_serial_with_no_gap_is_a_new_presentation(self):
        # the repeat's case: cleared and shown again in one task, so no
        # sample without the surface lies between the two
        self.back_ad["presentation"] = "2"
        self.back["t"] = 12000.5
        self.raw["observation"]["samples"] = [s for s in self.raw["observation"]["samples"] if s["t"] != 12000]
        self.raw["observation"]["samples"].sort(key=lambda x: x["t"])
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("1 presentation(s) more", d)

    def test_serial_absent_on_the_restore_is_another_identity(self):
        # a Player that stamps a serial stamps it on every sample: one that
        # disappears is not the same presentation read twice
        del self.back_ad["presentation"]
        self.assertEqual(self.field()[0], Outcome.FAIL)

    def test_serial_absent_on_both_is_the_element_alone(self):
        for e in (self.ad, self.back_ad):
            del e["presentation"]
        self.assertEqual(self.field()[0], Outcome.PASS)

    def test_three_serials_are_three_presentations(self):
        obs_samples = self.raw["observation"]["samples"]
        third = copy.deepcopy(self.back)
        third["t"] = 17000
        third["elements"][0]["time"] = 17000
        next(e for e in third["elements"] if e["element"] == "ad")["presentation"] = "3"
        self.back_ad["presentation"] = "2"
        obs_samples.append(third)
        obs_samples.sort(key=lambda x: x["t"])
        out, d = self.field()
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("2 presentation(s) more", d)


class PrimaryFromTolerance(unittest.TestCase):
    """A `primary` element's own `tolerance` holds its `from` and nothing
    else: the segment's (R16.1's one frame) keeps holding the boundary."""

    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        del self.o["geometry"]
        self.raw = synthetic_raw(self.v, self.o, self.fx)
        self.o["presentation"][2]["tolerance"] = 17
        self.o["presentation"][2]["shows"][0]["tolerance"] = 250
        self.s20 = next(s for s in self.raw["observation"]["samples"] if s["t"] == 20000)

    def verdict(self):
        self.raw["observation"]["samples"].sort(key=lambda x: x["t"])
        return verdicts(run(self.v, self.o, self.fx, self.raw))["presentation"]

    def test_from_takes_the_element_tolerance(self):
        for mt, want in ((20250, Outcome.PASS), (19750, Outcome.PASS), (20251, Outcome.FAIL),
                         (19749, Outcome.FAIL)):
            self.s20["elements"][0]["time"] = mt
            self.assertEqual(self.verdict(), want, mt)

    def test_boundary_keeps_the_segment_tolerance(self):
        for t, want in ((20017, Outcome.PASS), (20018, Outcome.FAIL)):
            self.s20["t"], self.s20["elements"][0]["time"] = t, 20000
            self.assertEqual(self.verdict(), want, t)

    def test_zero(self):
        self.o["presentation"][2]["shows"][0]["tolerance"] = 0
        self.s20["elements"][0]["time"] = 20000
        self.assertEqual(self.verdict(), Outcome.PASS)
        self.s20["elements"][0]["time"] = 20001
        self.assertEqual(self.verdict(), Outcome.FAIL)

    def test_absent_falls_back_to_the_segment(self):
        del self.o["presentation"][2]["shows"][0]["tolerance"]
        self.s20["elements"][0]["time"] = 20018
        self.assertEqual(self.verdict(), Outcome.FAIL)

    def test_element_tolerance_does_not_break_a_silent_boundary(self):
        # the same primary on both sides, one carrying its own tolerance: the
        # split stays silent (no change needs observing)
        self.o["presentation"] = [
            {"start": 0, "end": 5000, "layout": "none", "shows": [{"element": "primary", "from": 0}]},
            {"start": 5000, "end": 30000, "layout": "none",
             "shows": [{"element": "primary", "from": 5000, "tolerance": 100}]}]
        self.o["selection"], self.o["beacons"], self.o["requests"] = [], [], []
        self.raw["observation"]["samples"] = [{"t": 0, "layout": "none", "elements": [
            {"element": "primary", "rect": FULL, "time": 0, "paused": False, "rate": 1}]}]
        self.assertEqual(self.verdict(), Outcome.PASS)


class HeldThenWindow(unittest.TestCase):
    """R40.9-3's shape: the content held at an exact boundary while the break
    resolves, then the ad from a window. The hold is optional (shorter than
    the tolerance it folds away), so two observed changes must match the two
    written boundaries in order, not each its nearest."""

    def setUp(self):
        self.v, self.o, self.fx = small_vector()
        del self.o["geometry"]
        self.raw = synthetic_raw(self.v, self.o, self.fx)     # replaced by record()
        ad = self.o["presentation"][1]["shows"][1]
        w, back = {"from": 6000, "to": 7000}, {"from": 12000, "to": 13000}
        self.o["presentation"] = [
            {"start": 0, "end": 6000, "layout": "none", "shows": [{"element": "primary", "from": 0}]},
            {"start": 6000, "end": w, "layout": "none", "shows": [{"element": "primary", "from": 6000}]},
            {"start": w, "end": back, "layout": "overlay-lower-third", "shows": [ad]},
            {"start": back, "end": 30000, "layout": "none",
             "shows": [{"element": "primary", "from": dict(w)}]}]
        self.ad = next(e for s in self.raw["observation"]["samples"] for e in s["elements"] if e["element"] == "ad")

    def record(self, hold, ad_at, ad_len=6000):
        p = lambda t, mt, paused: {"t": t, "layout": "none", "elements": [  # noqa: E731
            {"element": "primary", "rect": FULL, "time": mt, "paused": paused, "rate": 1}]}
        s = [p(0, 0, False)]
        if hold is not None:
            s.append(p(hold, hold, True))
        s.append({"t": ad_at, "layout": "overlay-lower-third", "elements": [dict(self.ad)]})
        mt = hold if hold is not None else ad_at
        s.append(p(ad_at + ad_len, mt, False))
        self.raw["observation"]["samples"] = s
        return verdicts(run(self.v, self.o, self.fx, self.raw))["presentation"], \
            details(run(self.v, self.o, self.fx, self.raw))["presentation"]

    def test_held_then_ad_late_in_the_window(self):
        out, d = self.record(6050, 6976)
        self.assertEqual(out, Outcome.PASS, d)

    def test_no_hold(self):
        self.assertEqual(self.record(None, 6100)[0], Outcome.PASS)

    def test_window_edges(self):
        for at, want in ((7250, Outcome.PASS), (7251, Outcome.FAIL)):
            self.assertEqual(self.record(6050, at)[0], want, at)

    def test_hold_not_at_the_exact_boundary(self):
        # a hold that begins outside the exact boundary's tolerance is a change
        # the vector does not have
        self.assertEqual(self.record(6300, 6976)[0], Outcome.FAIL)


class OpportunityIdentity(unittest.TestCase):
    """An opportunity is (document, @schemeIdUri, @value, Event@id), as
    ISO/IEC 23009-1 5.10.2.4 identifies an Event: UC-04's shape, a linear
    break and an overlay window of one MPD, both Event@id 1 in EventStreams of
    different schemes, are two opportunities."""
    INS = "urn:mpeg:dash:event:alternativeMPD:insert:2025"
    OVL = "urn:svta:dash:sgai-overlay:2026"
    MAIN = "examples/annex-d/D.2-1.mpd"
    LIN = {"fixture": "examples/annex-d/D.4-1.mpd", "id": "ad-401"}
    OV = {"fixture": "examples/annex-d/D.5-1.xml", "index": 1}

    def setUp(self):
        with open(os.path.join(SOURCE, self.MAIN), encoding="utf-8") as f:
            main = f.read()
        self.fx = Fixtures({self.MAIN: "https://sgai-entry.invalid/D.2-1.mpd",
                            self.LIN["fixture"]: "https://aps.example.com/lin",
                            self.OV["fixture"]: "https://aps.example.com/ov"},
                           {self.MAIN: main})
        self.expected = [
            {"opportunity": {"fixture": self.MAIN, "event_id": "1", "scheme": self.INS}, "result": "presented",
             "presented": [{"candidate": self.LIN, "option": None, "layout": "linear"}]},
            {"opportunity": {"fixture": self.MAIN, "event_id": "1", "scheme": self.OVL}, "result": "presented",
             "presented": [{"candidate": self.OV, "option": {"index": 1}, "layout": "overlay-lower-third"}]},
        ]

    def surface(self, cand, option, scheme=None, value=None, doc=None, inst=1):
        el = {"element": "ad", "rect": dict(FULL), "inst": inst, "doc": self.fx.urls[cand["fixture"]],
              "opportunityDoc": self.fx.urls[doc or self.MAIN], "opportunityEvent": "1"}
        el["candidateId" if "id" in cand else "candidateIndex"] = cand.get("id") or str(cand["index"])
        if option is not None:
            el["optionIndex"] = str(option)
        if scheme is not None:
            el["opportunityScheme"] = scheme
        if value is not None:
            el["opportunityValue"] = value
        return el

    def select(self, expected, *timeline):
        """timeline: (t, layout, [surfaces])."""
        o = Observed(requests=[], samples=[{"t": t, "layout": lay, "elements": els} for t, lay, els in timeline])
        attribute(o, self.fx)
        return compare_selection(expected, o, self.fx, 250)

    def uc04(self, lin_scheme, ov_scheme):
        # the overlay appears first, the linear ad under it a sample later: the
        # order the conflated key compared against the vector's order
        ov = self.surface(self.OV, 1, ov_scheme, inst=2)
        lin = self.surface(self.LIN, None, lin_scheme, inst=1)
        return self.select(self.expected, (0, "none", []), (100, "overlay-lower-third", [ov]),
                           (200, "overlay-lower-third", [ov, lin]))

    def test_same_id_different_schemes_are_two_opportunities(self):
        out, d = self.uc04(self.INS, self.OVL)
        self.assertEqual(out, Outcome.PASS, d)
        self.assertIn("2 opportunit", d)

    def test_presentation_under_the_other_scheme_fails(self):
        out, d = self.uc04(self.OVL, self.INS)
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn(self.INS, d)

    def test_player_without_scheme_is_not_verifiable(self):
        # the @id names two EventStreams of D.2-1: no scheme, no opportunity
        out, d = self.uc04(None, None)
        self.assertEqual(out, Outcome.NOT_VERIFIABLE, d)
        self.assertIn("data-sgai-opportunity-scheme", d)

    def test_vector_without_scheme_is_not_verifiable(self):
        for sel in self.expected:
            del sel["opportunity"]["scheme"]
        out, d = self.uc04(self.INS, self.OVL)
        self.assertEqual(out, Outcome.NOT_VERIFIABLE, d)
        self.assertIn("the vector names none", d)

    def test_unknown_scheme_is_a_third_opportunity(self):
        out, d = self.uc04(self.INS, "urn:example:other")
        self.assertEqual(out, Outcome.FAIL)
        self.assertIn("does not list", d)

    def test_unique_id_needs_no_scheme(self):
        # an @id one EventStream carries: neither side has to name the scheme
        main = """<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"><Period>
<EventStream schemeIdUri="urn:a" value="v"><Event id="1"/></EventStream>
<EventStream schemeIdUri="urn:b"><Event id="2"/></EventStream></Period></MPD>"""
        self.fx.texts[self.MAIN] = main
        exp = [{"opportunity": {"fixture": self.MAIN, "event_id": "1"}, "result": "presented",
                "presented": [{"candidate": self.LIN, "option": None, "layout": "linear"}]}]
        for scheme, value in ((None, None), ("urn:a", None), ("urn:a", "v")):
            lin = self.surface(self.LIN, None, scheme, value)
            out, d = self.select(exp, (100, "linear", [lin]))
            self.assertEqual(out, Outcome.PASS, f"{scheme} {value}: {d}")

    def test_same_scheme_value_and_id_is_one_opportunity(self):
        # negative: the same combination in two Periods is one opportunity, so
        # its two presentations are one entry's, in order
        main = """<MPD xmlns="urn:mpeg:dash:schema:mpd:2011">
<Period><EventStream schemeIdUri="urn:a" value="v"><Event id="1"/></EventStream></Period>
<Period><EventStream schemeIdUri="urn:a" value="v"><Event id="1"/></EventStream></Period></MPD>"""
        self.fx.texts[self.MAIN] = main
        exp = [{"opportunity": {"fixture": self.MAIN, "event_id": "1"}, "result": "presented",
                "presented": [{"candidate": self.LIN, "option": None, "layout": "linear"},
                              {"candidate": self.OV, "option": {"index": 1}, "layout": "overlay-lower-third"}]}]
        lin = self.surface(self.LIN, None, "urn:a", "v", inst=1)
        ov = self.surface(self.OV, 1, None, inst=2)
        timeline = ((100, "linear", [lin]), (200, "none", []), (300, "overlay-lower-third", [ov]))
        out, d = self.select(exp, *timeline)
        self.assertEqual(out, Outcome.PASS, d)
        # and listed as two entries of one opportunity they are consumed in order
        two = [dict(exp[0], presented=[p]) for p in exp[0]["presented"]]
        self.assertEqual(self.select(two, *timeline)[0], Outcome.PASS)
        self.assertEqual(self.select(two[::-1], *timeline)[0], Outcome.FAIL)

    def test_same_scheme_and_id_different_value_are_two_opportunities(self):
        main = """<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"><Period>
<EventStream schemeIdUri="urn:a" value="x"><Event id="1"/></EventStream>
<EventStream schemeIdUri="urn:a" value="y"><Event id="1"/></EventStream></Period></MPD>"""
        self.fx.texts[self.MAIN] = main
        exp = [{"opportunity": {"fixture": self.MAIN, "event_id": "1", "scheme": "urn:a", "value": v},
                "result": "presented", "presented": [p]}
               for v, p in (("x", {"candidate": self.LIN, "option": None, "layout": "linear"}),
                            ("y", {"candidate": self.OV, "option": {"index": 1}, "layout": "overlay-lower-third"}))]
        ov = self.surface(self.OV, 1, "urn:a", "y", inst=2)
        lin = self.surface(self.LIN, None, "urn:a", "x", inst=1)
        out, d = self.select(exp, (100, "overlay-lower-third", [ov]), (200, "overlay-lower-third", [ov, lin]))
        self.assertEqual(out, Outcome.PASS, d)
        # the scheme alone does not tell them apart
        lin.pop("opportunityValue")
        ov.pop("opportunityValue")
        self.assertEqual(self.select(exp, (100, "overlay-lower-third", [ov]),
                                     (200, "overlay-lower-third", [ov, lin]))[0], Outcome.NOT_VERIFIABLE)


if __name__ == "__main__":
    unittest.main()
